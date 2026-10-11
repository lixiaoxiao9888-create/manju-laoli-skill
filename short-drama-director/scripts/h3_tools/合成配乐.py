# -*- coding: utf-8 -*-
"""合成配乐：按一份"配乐提示表"(JSON) 合成与剪辑点对齐的预告片式临时配乐（低音铺底 + 太鼓 + 铜管轰鸣 + 蓄力 + 弦乐震音 + 清冷长音）。
不是旋律音乐，定位是 temp track：先把情绪和卡点对上，正式版可换成 AI 作曲或曲库音乐。

用法：
  python 合成配乐.py <配乐提示表.json> <输出.wav>

提示表字段（时间单位秒，都是整集时间线上的时间）：
  总长                    float
  调性根音Hz              float，默认 73.42（D2）
  段落: [{"起","止","类型","强度"}]   类型：暗底(低音铺底) / 清冷(高音长音) / 脉冲(低音十六分脉冲) / 震音(弦乐震音)
  鼓点: [时间, ...]        太鼓重击
  轰鸣: [时间, ...]        铜管 braam（大冲击点）
  蓄力: [[起, 止], ...]    上扬蓄力，止点即落点
  静默: [[起, 止], ...]    整体压到几乎无声（先静再炸）
  让位: [[起, 止], ...]    台词/独白区间，配乐自动压低到 35%
"""
import json
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
RNG = np.random.default_rng(7)


def lp(x, f):
    return sosfilt(butter(4, f, "low", fs=SR, output="sos"), x)


def hp(x, f):
    return sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)


def saw(freq, n, detune=0.0):
    t = np.arange(n) / SR
    ph = (freq * (1 + detune)) * t
    return 2 * (ph - np.floor(ph + 0.5))


def env_ar(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def place(buf, sig, t):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def taiko():
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (70 * np.exp(-t * 6) + 45) * t) * np.exp(-t * 4.5)
    skin = lp(RNG.standard_normal(n), 900) * np.exp(-t * 28) * 0.6
    return np.tanh(1.8 * (body + skin)) * 0.9


def braam(root):
    n = int(3.2 * SR)
    t = np.arange(n) / SR
    x = sum(saw(root * m, n, d) for m in (1, 2) for d in (-0.006, 0.0, 0.007)) / 6
    cut = 300 + 1800 * np.exp(-t * 1.4)            # 滤波随时间收拢，模拟铜管"轰"
    y = np.zeros(n)
    step = int(0.05 * SR)
    for k in range(0, n, step):
        seg = x[k:k + step]
        y[k:k + len(seg)] = lp(seg, float(cut[k]))
    y += np.sin(2 * np.pi * root / 2 * t) * 0.6      # 次低音
    return np.tanh(1.6 * y) * env_ar(n, 0.02, 1.6) * 0.8


def riser(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sweep = np.sin(2 * np.pi * (180 * t + 700 * t * t / dur))
    noise = hp(RNG.standard_normal(n), 1500) * 0.35
    return (sweep * 0.4 + noise) * (t / dur) ** 2.2 * 0.7


def section(kind, n, root, strength):
    t = np.arange(n) / SR
    if kind == "暗底":
        x = (saw(root, n, -0.004) + saw(root, n, 0.005) + 0.5 * saw(root * 1.5, n)) / 2.5
        x = lp(x, 260) + 0.5 * np.sin(2 * np.pi * root / 2 * t)
        x *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.25 * t)
    elif kind == "清冷":
        x = sum(np.sin(2 * np.pi * root * m * t) * a for m, a in ((8, 0.4), (12, 0.3), (16, 0.2), (24, 0.1)))
        x *= 0.7 + 0.3 * np.sin(2 * np.pi * 0.5 * t)
        x += 0.25 * lp(saw(root * 2, n), 400)
    elif kind == "脉冲":
        step = int(SR * 60 / 140 / 4)                 # 140BPM 十六分
        gate = ((np.arange(n) % step) < step * 0.45).astype(float)
        x = lp(saw(root, n) + saw(root * 2, n, 0.003), 500) * gate
        x += 0.4 * np.sin(2 * np.pi * root / 2 * t)
    elif kind == "震音":
        x = sum(lp(saw(root * m, n, d), 2200) for m, d in ((4, 0.0), (4.76, 0.004), (6, -0.003))) / 3
        x *= 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 12 * t))   # 弦乐震音
        x *= np.linspace(0.4, 1.0, n)                             # 越拉越紧
    else:
        raise SystemExit(f"未知段落类型：{kind}")
    return x * strength * env_ar(n, 0.4, 0.4)


def gain_curve(n, ranges, level, ramp=0.08):
    g = np.ones(n)
    r = int(ramp * SR)
    for a, b in ranges:
        i, j = int(a * SR), min(n, int(b * SR))
        g[i:j] = np.minimum(g[i:j], level)
        if i - r > 0:
            g[i - r:i] = np.minimum(g[i - r:i], np.linspace(1, level, r))
        if j + r < n:
            g[j:j + r] = np.minimum(g[j:j + r], np.linspace(level, 1, r))
    return g


def build(cue_path, out_path):
    with open(cue_path, encoding="utf-8") as f:
        cue = json.load(f)
    n = int(cue["总长"] * SR) + SR
    root = float(cue.get("调性根音Hz", 73.42))
    bed, hits = np.zeros(n), np.zeros(n)
    for s in cue.get("段落", []):
        m = int((s["止"] - s["起"]) * SR)
        place(bed, section(s["类型"], m, root, float(s.get("强度", 0.5))), s["起"])
    for t in cue.get("鼓点", []):
        place(hits, taiko(), t)
    for t in cue.get("轰鸣", []):
        place(hits, braam(root), t)
        place(hits, taiko(), t)
    for a, b in cue.get("蓄力", []):
        place(hits, riser(b - a), a)
    mix = bed * gain_curve(n, cue.get("静默", []), 0.04) + hits * gain_curve(n, cue.get("静默", []), 0.04, 0.02)
    mix *= gain_curve(n, cue.get("让位", []), 0.35, 0.25)
    mix = mix[: int(cue["总长"] * SR)]
    mix *= env_ar(len(mix), 0.05, 0.6)
    mix = np.tanh(mix * 1.2)
    mix /= max(1e-6, np.max(np.abs(mix))) / 0.89
    stereo = np.stack([mix, np.roll(mix, int(0.012 * SR))], axis=1)   # 轻微拉宽
    wavfile.write(out_path, SR, (stereo * 32767).astype(np.int16))
    print(f"已输出 {out_path}，{len(mix) / SR:.1f} 秒")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    build(sys.argv[1], sys.argv[2])
