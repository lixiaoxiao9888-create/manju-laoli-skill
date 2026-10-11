# -*- coding: utf-8 -*-
"""裸眼3D（2026-10-11）：抖音常见的"白框出屏"效果——画面上加两条白色边框，把主体逐帧抠出来叠到白框前面，
主体（爪子、脸、飞出来的东西）越过白框时就像冲出屏幕。

用法：
  python 裸眼3D.py <输入.mp4> <输出.mp4> --起 秒 --止 秒 [--方向 竖|横] [--位置 0.13] [--线宽 16] [--颜色 白|黑] [--样式 竖线|宽银幕] [--黑边 0.17] [--入场 0.35]

抠像模型：rembg 的 isnet-general-use（U2NET_HOME 指定的目录（默认 ~/.u2net），CPU 跑，约 1~2 秒一帧）。
遮罩做了时间平滑（减少闪边）和 1 像素羽化。输出带原片同段声音。
适合的镜头：主体朝镜头扑来、伸手/伸爪、物体飞出画面；主体和背景颜色差越大，抠得越干净。
"""
import argparse
import os
import subprocess
import sys
import tempfile

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--起", type=float, required=True); ap.add_argument("--止", type=float, required=True)
    ap.add_argument("--方向", default="竖"); ap.add_argument("--位置", type=float, default=0.13)
    ap.add_argument("--线宽", type=int, default=16)
    ap.add_argument("--颜色", default="白")   # 背景亮（白云、雪地）用 黑
    ap.add_argument("--样式", default="竖线")   # 竖线 | 宽银幕（上下黑边破框，推荐）
    ap.add_argument("--黑边", type=float, default=0.17)   # 宽银幕：上下黑边各占画高的比例
    ap.add_argument("--入场", type=float, default=0.35)
    ap.add_argument("--冲击", default="")   # 命中时间（相对片段起点，秒，逗号分隔）：冲击帧只作用在画面里，黑边保持纯黑不动   # 边框入场动画秒数（宽银幕黑边从画外滑入；竖线从上往下画出）
    a = ap.parse_args()
    sess = new_session("isnet-general-use")
    cap = cv2.VideoCapture(a.src)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    w, h = int(cap.get(3)), int(cap.get(4))
    bars = np.zeros((h, w), bool)
    lw = a.线宽
    if a.方向 == "竖":
        for x in (int(w * a.位置), int(w * (1 - a.位置))):
            bars[:, x - lw // 2:x + lw // 2] = True
    else:
        for y in (int(h * a.位置), int(h * (1 - a.位置))):
            bars[y - lw // 2:y + lw // 2, :] = True
    bars0 = bars
    hits = [round(float(x) * fps) for x in a.冲击.split(",") if x.strip()]
    if hits:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import importlib
        fx = importlib.import_module("冲击帧特效")
        sls = {k: fx.speed_lines(w, h, 100 + k) for k in range(4)}
    tmp = os.path.join(tempfile.gettempdir(), f"pop3d_{os.getpid()}.mp4")
    vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    cap.set(cv2.CAP_PROP_POS_FRAMES, round(a.起 * fps))
    prev = None
    n_total = round((a.止 - a.起) * fps)
    for i in range(n_total):
        ok, fr = cap.read()
        if not ok:
            break
        rgb = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
        m = np.asarray(remove(rgb, session=sess, only_mask=True), np.float32) / 255.0
        m = prev * 0.35 + m * 0.65 if prev is not None else m      # 时间平滑，减少边缘闪烁
        prev = m
        m = np.clip((m - 0.35) / 0.3, 0, 1)                        # 边缘做硬，免得边框半透明地印在主体上
        # 只保留主体：最大的连通块（及面积 ≥ 其 30% 的块），碎屑、远山、飞石都丢掉，免得它们"破框"
        nlab, lab, stats, _ = cv2.connectedComponentsWithStats((m > 0.5).astype(np.uint8), 8)
        if nlab > 1:
            areas = stats[1:, cv2.CC_STAT_AREA]
            keep = [k + 1 for k, ar in enumerate(areas) if ar >= max(areas) * 0.3 and ar >= h * w * 0.02]
            m = m * np.isin(lab, keep).astype(np.float32)
        m = cv2.GaussianBlur(m, (0, 0), 1.0)
        cover = float(m.mean())
        p = min(1.0, (i + 1) / max(1, a.入场 * fps))
        p = 1 - (1 - p) ** 3                                        # 入场缓出
        if a.样式 == "宽银幕":
            bh = int(h * a.黑边 * p)
            bars = np.zeros((h, w), bool)
            bars[:bh, :] = True
            bars[h - bh:, :] = True
            fade = 1.0                                              # 宽银幕黑边始终在（淡出会露出半截黑块）
            col = 0.0
        else:
            if p < 1:                                               # 竖线从上往下画出来
                bars = bars0 & (np.arange(h)[:, None] < h * p)
            else:
                bars = bars0
            fade = float(np.clip((0.55 - cover) / 0.15, 0, 1))     # 主体占满画面（>55%）时边框淡出，抠像这时也不可靠
            col = 0.0 if a.颜色 == "黑" else 255.0
        bar_a = np.where(bars, fade, 0.0).astype(np.float32)
        for hf in hits:                                             # 冲击帧：画面做特效，抠像仍用原画面
            k = i - hf
            if k in (0, 1):
                fr = fx.manga(fr, invert=(k == 0))
            elif 2 <= k <= 9:
                fr = fx.punch(fr, k, sls[k % 4], 1.0, hf)
            if 0 <= k <= 9:
                m = m * (~bars)                                     # 冲击帧画面被推近/震动，和抠像对不上 → 这几帧不破框
        f = fr.astype(np.float32)
        withbar = f * (1 - bar_a[..., None]) + col * bar_a[..., None]
        mm = m[..., None]
        out = (f * mm + withbar * (1 - mm)).astype(np.uint8)       # 主体叠在边框前面
        vw.write(out)
        if i % 12 == 0:
            print(f"  {i}/{n_total}", flush=True)
    vw.release()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-ss", f"{a.起:.3f}", "-to", f"{a.止:.3f}", "-i", a.src,
                    "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "256k", "-shortest", a.dst], check=True)
    os.remove(tmp)
    print(f"已输出 {a.dst}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
