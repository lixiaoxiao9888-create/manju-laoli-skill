# -*- coding: utf-8 -*-
"""人声定位（2026-10-11）：用基音（80~450Hz 周期性）检测找出片段里"有人声"的区间，给字幕对时、检查剪点有没有切在笑声中间。
风声、爆炸、冰裂这类音效没有稳定音高，不会被算成人声；说话、笑、吼都会被算进来。
用法：python 人声定位.py <视频或音频> [--起 秒 --止 秒]
输出：每个人声区间（秒，原片时间）和时长；区间之间停顿 < 0.25s 的会合并。"""
import argparse
import subprocess
import sys

import numpy as np

SR = 16000


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-af", "highpass=f=70,lowpass=f=3000", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def voiced(x, hop=0.01, win=0.04):
    h, w = int(SR * hop), int(SR * win)
    lo, hi = int(SR / 450), int(SR / 80)
    n = max(0, (len(x) - w) // h)
    v = np.zeros(n, bool)
    e = np.zeros(n)
    for i in range(n):
        f = x[i * h:i * h + w]
        f = f - f.mean()
        en = float(np.sqrt(np.mean(f * f)))
        e[i] = en
        if en < 1e-3:
            continue
        ac = np.correlate(f, f, "full")[w - 1:]
        if ac[0] <= 0:
            continue
        ac = ac / ac[0]
        v[i] = ac[lo:hi].max() > 0.55
    floor = np.percentile(e, 20)
    v &= e > floor * 2.0
    return v


def segments(v, hop=0.01, gap=0.25, min_len=0.15):
    segs, s = [], None
    for i, a in enumerate(v):
        if a and s is None:
            s = i
        if not a and s is not None:
            segs.append([s * hop, i * hop]); s = None
    if s is not None:
        segs.append([s * hop, len(v) * hop])
    out = []
    for a, b in segs:
        if out and a - out[-1][1] < gap:
            out[-1][1] = b
        else:
            out.append([a, b])
    return [(a, b) for a, b in out if b - a >= min_len]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("--起", type=float, default=0); ap.add_argument("--止", type=float, default=None)
    a = ap.parse_args()
    x = load(a.src)
    x = x[int(a.起 * SR):int(a.止 * SR) if a.止 else None]
    for s, e in segments(voiced(x)):
        print(f"{s + a.起:6.2f} – {e + a.起:6.2f}  ({e - s:.2f}s)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
