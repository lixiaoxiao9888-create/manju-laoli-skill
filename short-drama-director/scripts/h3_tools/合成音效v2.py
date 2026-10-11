# -*- coding: utf-8 -*-
"""合成音效 v2：分层设计 + 洞穴混响，比 v1 的单层合成更接近影视音效（仍是占位级，正式版建议换专业音效库）。

用法：
  python 合成音效v2.py <输出目录>

生成（48kHz 立体声 wav）：
  声浪轰鸣   低频下潜 + 青铜钟泛音 + 气压"呼"声 + 洞穴尾音（声浪环炸出 / 掠过）
  岩壁龟裂   连串脆裂 + 低频闷击 + 碎屑崩落（撞山壁、撞岩顶）
  碎石滚落   密集碎石颗粒 + 低频隆隆（落石、山壁崩落的持续层）
  风啸上冲   湍流噪声经共振滤波上扫 + 声像横移（镜头急冲、上冲、甩镜）
  巨物砸水   低频砸击 + 水体轰响 + 气泡咕噜 + 水雾嘶声（蟒头砸水、人砸湖面）
  压迫低鸣   拍频低音 + 缓慢上扬的紧张泛音（推近特写前的压迫感）
  心跳       一次"咚-咚"（低频双击 + 体腔闷响），重复放置做心跳卡点
依赖：numpy、scipy。
"""
import os
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
rng = np.random.default_rng(7)


def t_axis(sec):
    return np.arange(int(SR * sec)) / SR


def noise(sec):
    return rng.standard_normal(int(SR * sec))


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def sweep_bp(x, f_start, f_end, q=4.0, curve=1.0):
    """时变共振带通（状态变量滤波器，逐样本），f 从 f_start 指数滑到 f_end。"""
    n = len(x)
    pos = (np.arange(n) / max(1, n - 1)) ** curve
    f = f_start * (f_end / f_start) ** pos
    g = np.tan(np.pi * np.minimum(f, SR * 0.45) / SR)
    k = 1.0 / q
    a1 = 1.0 / (1.0 + g * (g + k))
    out = np.empty(n)
    ic1 = ic2 = 0.0
    for i in range(n):
        v3 = x[i] - ic2
        v1 = a1[i] * ic1 + g[i] * a1[i] * v3
        v2 = ic2 + g[i] * v1
        ic1 = 2 * v1 - ic1
        ic2 = 2 * v2 - ic2
        out[i] = v1
    return out


def env_ad(sec, attack, decay_tau, hold=0.0):
    t = t_axis(sec)
    e = np.where(t < attack, t / max(attack, 1e-4), np.exp(-(np.maximum(t - attack - hold, 0)) / decay_tau))
    return e


def turbulence(sec, rate=18.0, depth=0.6):
    """湍流幅度调制：低通随机信号，让噪声不那么"电子"。"""
    m = lp(noise(sec), rate, 2)
    m /= np.abs(m).max() + 1e-9
    return 1.0 - depth + depth * (0.5 + 0.5 * m)


def cave_ir(sec=2.6, damp=2500.0):
    t = t_axis(sec)
    ir = noise(sec) * np.exp(-t / (sec / 6.0))
    ir = lp(ir, damp, 2)
    # 早期反射
    for d, a in ((0.019, 0.7), (0.033, 0.5), (0.051, 0.45), (0.077, 0.3)):
        ir[int(d * SR)] += a * 3
    return ir / np.abs(ir).max()


IR = cave_ir()


def reverb(x, wet=0.3):
    y = fftconvolve(x, IR)[: len(x) + int(1.5 * SR)]
    y /= np.abs(y).max() + 1e-9
    dry = np.concatenate([x, np.zeros(len(y) - len(x))])
    dry /= np.abs(dry).max() + 1e-9
    return (1 - wet) * dry + wet * y


def grains(sec, density_curve, lo=700, hi=4500, glen=(0.004, 0.025)):
    """碎屑颗粒：随机位置、随机长度的带通噪声短脉冲。density_curve(t)→每秒颗粒数。"""
    n = int(SR * sec)
    out = np.zeros(n)
    t = 0.0
    while t < sec:
        rate = max(density_curve(t), 1e-3)
        t += rng.exponential(1.0 / rate)
        if t >= sec:
            break
        L = rng.uniform(*glen)
        m = int(L * SR)
        s = int(t * SR)
        if s + m >= n:
            break
        fc = rng.uniform(lo, hi)
        g = bp(rng.standard_normal(m), fc * 0.7, min(fc * 1.4, SR * 0.45))
        g *= np.exp(-np.arange(m) / (m / 4)) * rng.uniform(0.2, 1.0)
        out[s:s + m] += g
    return out


def norm(x, peak=0.89):
    return x / (np.abs(x).max() + 1e-9) * peak


def stereo(x, width=0.25, pan_from=0.0, pan_to=0.0):
    """轻微去相关 + 声像移动。"""
    d = int(0.011 * SR)
    side = np.concatenate([np.zeros(d), x[:-d]]) if len(x) > d else x
    pan = np.linspace(pan_from, pan_to, len(x))
    l = x * (1 - pan) * 0.5 + side * width * 0.5
    r = x * (1 + pan) * 0.5 - side * width * 0.5
    st = np.stack([l, r], 1)
    return st / (np.abs(st).max() + 1e-9) * 0.89


def save(dirpath, name, st):
    wavfile.write(os.path.join(dirpath, name), SR, (st * 32767).astype(np.int16))
    print(f"  {name}  {len(st) / SR:.2f}s")


# ---------------- 各音效 ----------------

def shock_boom():
    sec = 2.2
    t = t_axis(sec)
    f = 35 + 60 * np.exp(-t / 0.18)                       # 95Hz → 35Hz 下潜
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(sec, 0.004, 0.6)
    bell = np.zeros_like(t)
    for ratio, amp, tau in ((0.5, 0.5, 1.2), (1.0, 0.6, 0.9), (1.19, 0.35, 0.7), (1.5, 0.3, 0.6),
                            (2.0, 0.25, 0.5), (2.67, 0.18, 0.35), (3.4, 0.12, 0.25)):
        bell += amp * np.sin(2 * np.pi * 98 * ratio * t + rng.uniform(0, 6)) * np.exp(-t / tau)
    bell *= env_ad(sec, 0.003, 10)
    air = noise(sec) * turbulence(sec, 25, 0.5)
    air = sweep_bp(air, 2600, 180, q=0.9, curve=0.5) * env_ad(sec, 0.012, 0.35)
    x = 1.0 * sub + 0.35 * bell + 0.8 * air
    x = np.tanh(1.8 * norm(x)) # 轻度饱和，压出"厚"
    return stereo(reverb(x, 0.32), 0.3)


def rock_crack():
    sec = 2.4
    n = int(SR * sec)
    x = np.zeros(n)
    for k in range(7):                                      # 连串脆裂
        s = int((0.0 + k * rng.uniform(0.012, 0.03)) * SR)
        m = int(rng.uniform(0.003, 0.009) * SR)
        c = hp(rng.standard_normal(m), 1800) * np.exp(-np.arange(m) / (m / 3)) * rng.uniform(0.5, 1.0)
        x[s:s + m] += c
    t = t_axis(sec)
    thump = np.sin(2 * np.pi * (48 + 40 * np.exp(-t / 0.05)) * t) * env_ad(sec, 0.002, 0.18)
    crumble = grains(sec, lambda tt: 900 * np.exp(-tt / 0.5) + 40, 500, 3800)
    rumble = lp(noise(sec), 120, 2) * env_ad(sec, 0.02, 0.6)
    x = 1.2 * x + 0.9 * thump + 0.55 * norm(crumble) + 0.5 * norm(rumble)
    return stereo(reverb(norm(x), 0.3), 0.35)


def debris_rain():
    sec = 2.8
    crumbs = grains(sec, lambda tt: 260 * (1 - tt / 2.8) + 60, 400, 3200, (0.006, 0.04))
    small = grains(sec, lambda tt: 500 * (1 - tt / 2.8) + 50, 2500, 7000, (0.002, 0.008))
    rumble = lp(noise(sec), 90, 2) * turbulence(sec, 6, 0.7)
    t = t_axis(sec)
    fade = np.minimum(1, t / 0.05) * np.minimum(1, (sec - t) / 0.6)
    x = (0.9 * norm(crumbs) + 0.4 * norm(small) + 0.6 * norm(rumble)) * fade
    return stereo(reverb(norm(x), 0.25), 0.5)


def wind_rush():
    sec = 1.5
    t = t_axis(sec)
    src = noise(sec) * turbulence(sec, 30, 0.6)
    a = sweep_bp(src, 260, 2400, q=2.5, curve=1.6)
    b = sweep_bp(src, 520, 4200, q=4.0, curve=1.8)
    swell = (t / sec) ** 2.2 * np.minimum(1, (sec - t) / 0.08)   # 由弱渐强，末尾利落收
    body = lp(noise(sec), 160, 2) * swell
    x = (norm(a) + 0.5 * norm(b) + 0.4 * norm(body)) * swell
    return stereo(reverb(norm(x), 0.15), 0.3, -0.7, 0.7)


def heavy_splash():
    sec = 2.6
    t = t_axis(sec)
    thump = np.sin(2 * np.pi * (40 + 70 * np.exp(-t / 0.04)) * t) * env_ad(sec, 0.002, 0.25)
    body = bp(noise(sec), 200, 2600) * turbulence(sec, 40, 0.8) * env_ad(sec, 0.006, 0.35)
    spray = hp(noise(sec), 4500) * turbulence(sec, 60, 0.7) * env_ad(sec, 0.03, 0.7)
    bub = np.zeros_like(t)
    for _ in range(45):                                   # 气泡：快速上滑的短正弦
        s = rng.uniform(0.05, 1.6)
        L = rng.uniform(0.02, 0.07)
        f0 = rng.uniform(250, 900)
        m = int(L * SR)
        i0 = int(s * SR)
        tt = np.arange(m) / SR
        bub[i0:i0 + m] += np.sin(2 * np.pi * f0 * (1 + 4 * tt / L) * tt) * np.exp(-tt / (L / 3)) * rng.uniform(0.2, 1)
    drip = grains(sec, lambda tt: 300 * np.exp(-tt / 0.8) + 10, 1500, 6000, (0.003, 0.012))
    x = 0.9 * thump + 1.0 * norm(body) + 0.45 * norm(spray) + 0.3 * norm(bub) + 0.3 * norm(drip)
    return stereo(reverb(norm(x), 0.22), 0.45)


def pressure_drone():
    sec = 3.0
    t = t_axis(sec)
    rise = (t / sec) ** 1.5
    lo = np.sin(2 * np.pi * 42 * t) + 0.8 * np.sin(2 * np.pi * 43.3 * t)          # 拍频
    mid = np.sin(2 * np.pi * np.cumsum(110 + 25 * rise) / SR) * 0.35
    hiss = bp(noise(sec), 900, 3000) * turbulence(sec, 8, 0.8) * 0.15
    x = (lo * 0.9 + mid + norm(hiss) * 0.3) * (0.15 + 0.85 * rise) * np.minimum(1, (sec - t) / 0.05)
    return stereo(reverb(np.tanh(1.4 * norm(x)), 0.25), 0.3)


def heartbeat():
    sec = 0.9
    t = t_axis(sec)
    x = np.zeros_like(t)
    for start, amp in ((0.0, 1.0), (0.24, 0.7)):
        tt = np.maximum(t - start, 0)
        on = t >= start
        f = 38 + 30 * np.exp(-tt / 0.03)
        x += on * amp * np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.09)
    x += 0.25 * lp(noise(sec), 200, 2) * env_ad(sec, 0.003, 0.12)
    return stereo(reverb(np.tanh(1.5 * norm(x)), 0.18), 0.1)


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    print(f"输出到 {out_dir}")
    save(out_dir, "声浪轰鸣.wav", shock_boom())
    save(out_dir, "岩壁龟裂.wav", rock_crack())
    save(out_dir, "碎石滚落.wav", debris_rain())
    save(out_dir, "风啸上冲.wav", wind_rush())
    save(out_dir, "巨物砸水.wav", heavy_splash())
    save(out_dir, "压迫低鸣.wav", pressure_drone())
    save(out_dir, "心跳.wav", heartbeat())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
