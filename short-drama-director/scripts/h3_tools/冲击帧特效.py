# -*- coding: utf-8 -*-
"""冲击帧特效（2026-10-11）：给一段视频的命中瞬间加短剧常见的"击杀冲击帧"，不改时长、不错音画。

用法：
  python 冲击帧特效.py <输入.mp4> <输出.mp4> <命中时间秒>[,<命中时间秒>...] [--起 秒] [--止 秒] [--强度 1.0] [--图 a.png,b.png,...] [--停 2]
  --图：每个命中点一张 AI 转绘的"红底线稿冲击图"（与命中点一一对应，不用的写 -；第一项是 - 时必须写成 --图=-,图.png，否则会被当成选项）。有图时改用"AI 漫画冲击帧"：
     第 0~1 帧 整张漫画图 → 第 2~3 帧 漫画图以"颜色加深"58% 叠在原画面上 → 第 4~9 帧 原画面推近 + 提亮爆闪 + 速度线/色散/震屏衰减

每个命中点（帧数按 24fps）：
  第 0~1 帧   漫画反色帧：黑白高反差 + 墨线描边，第 0 帧反色、第 1 帧正色（日漫/国漫"冲击帧"）
  第 2~9 帧   回到原画：放射速度线（由强到弱）+ 红闪 + RGB 色散 + 推近回弹 + 震屏，全部随时间衰减
只替换画面，不插帧，所以原声和字幕时间不变；命中音效请在剪辑方案里另加。
--起/--止 只截取这一段输出（做试剪用）；不写就处理整条。
"""
import argparse
import math
import os
import subprocess
import sys
import tempfile

import cv2
import numpy as np

FPS_OUT = 24


def speed_lines(w, h, seed):
    """放射速度线遮罩（0~1），越靠边越密越亮，中心留空。"""
    rng = np.random.default_rng(seed)
    m = np.zeros((h, w), np.float32)
    cx, cy = w / 2, h / 2
    R = math.hypot(w, h) / 2
    for _ in range(170):
        ang = rng.uniform(0, 2 * math.pi)
        r0 = R * rng.uniform(0.38, 0.75)
        width = rng.uniform(1.5, 7.0)
        p0 = (cx + math.cos(ang) * r0, cy + math.sin(ang) * r0)
        p1 = (cx + math.cos(ang) * R * 1.1, cy + math.sin(ang) * R * 1.1)
        d = np.array([-math.sin(ang), math.cos(ang)]) * width
        poly = np.array([[p0[0], p0[1]], [p1[0] + d[0] * 3, p1[1] + d[1] * 3], [p1[0] - d[0] * 3, p1[1] - d[1] * 3]], np.int32)
        cv2.fillConvexPoly(m, poly, float(rng.uniform(0.5, 1.0)))
    return cv2.GaussianBlur(m, (0, 0), 1.2)


def manga(frame, invert):
    """黑白高反差 + 墨线：冲击帧的漫画定格。"""
    g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    g = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(g)
    tone = np.where(g > 150, 255, np.where(g > 80, 130, 0)).astype(np.uint8)   # 三阶色调
    edges = cv2.dilate(cv2.Canny(cv2.GaussianBlur(g, (5, 5), 0), 60, 140), np.ones((3, 3), np.uint8))
    out = tone.copy()
    out[edges > 0] = 0
    if invert:
        out = 255 - out
    return cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)


def cover(img, w, h):
    """等比铺满 w×h（居中裁切）。"""
    ih, iw = img.shape[:2]
    sc = max(w / iw, h / ih)
    r = cv2.resize(img, (int(iw * sc + 0.5), int(ih * sc + 0.5)), interpolation=cv2.INTER_AREA)
    y0, x0 = (r.shape[0] - h) // 2, (r.shape[1] - w) // 2
    return r[y0:y0 + h, x0:x0 + w]


def color_burn(base, top, opacity):
    """剪映"颜色加深"混合：1 - (1 - base) / top，再按不透明度和原画混合。"""
    b = base.astype(np.float32) / 255.0
    t = np.clip(top.astype(np.float32) / 255.0, 1e-3, 1)
    burn = np.clip(1 - (1 - b) / t, 0, 1)
    return np.clip((b * (1 - opacity) + burn * opacity) * 255, 0, 255).astype(np.uint8)


def flash(frame, a):
    """爆闪：提亮度/对比/高光（a 0~1）。"""
    f = frame.astype(np.float32)
    f = (f - 128) * (1 + 0.6 * a) + 128 + 70 * a
    return np.clip(f, 0, 255).astype(np.uint8)


def punch(frame, k, sl, strength, shake_seed, tint=(30, 30, 255)):
    """第 k 帧（2~9）的衰减特效。"""
    h, w = frame.shape[:2]
    a = max(0.0, 1.0 - (k - 2) / 8.0) * strength          # 1 → 0
    # 推近回弹 + 震屏
    z = 1.0 + 0.12 * a
    rng = np.random.default_rng(shake_seed + k)
    dx, dy = rng.uniform(-1, 1, 2) * 22 * a
    M = cv2.getRotationMatrix2D((w / 2, h / 2), rng.uniform(-1, 1) * 1.2 * a, z)
    M[:, 2] += (dx, dy)
    f = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)
    # RGB 色散
    s = int(round(14 * a))
    if s:
        b, g, r = cv2.split(f)
        b = np.roll(b, -s, axis=1)
        r = np.roll(r, s, axis=1)
        f = cv2.merge([b, g, r])
    f = f.astype(np.float32)
    # 红闪
    f = f * (1 - 0.35 * a) + np.array(tint, np.float32) * 0.35 * a
    # 速度线（白）
    m = (sl * 0.9 * a)[..., None]
    f = f * (1 - m) + 255 * m
    return np.clip(f, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst"); ap.add_argument("hits")
    ap.add_argument("--起", type=float, default=None); ap.add_argument("--止", type=float, default=None)
    ap.add_argument("--强度", type=float, default=1.0)
    ap.add_argument("--图", default="")
    ap.add_argument("--停", type=int, default=2)   # AI 漫画图停留帧数（2=教学原版；4 更猛）
    a = ap.parse_args()
    hits = [float(x) for x in a.hits.split(",")]
    cap = cv2.VideoCapture(a.src)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    w, h = int(cap.get(3)), int(cap.get(4))
    t0 = a.起 or 0.0
    t1 = a.止 if a.止 is not None else cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    tmp = os.path.join(tempfile.gettempdir(), f"impact_{os.getpid()}.mp4")
    vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    sl = {i: speed_lines(w, h, 100 + i) for i in range(4)}
    hit_frames = [round(t * fps) for t in hits]
    pics = [x.strip() for x in a.图.split(",")] if a.图 else []
    art, tints = {}, {}
    for hf, pth in zip(hit_frames, pics):
        if pth and pth != "-":
            im = cv2.imdecode(np.fromfile(pth, np.uint8), cv2.IMREAD_COLOR)
            if im is None:
                raise SystemExit(f"读不了冲击图：{pth}")
            art[hf] = cover(im, w, h)
            m = art[hf].reshape(-1, 3).mean(0)                # 闪色取冲击图主色（冰蓝图闪冰蓝，红图闪红）
            tints[hf] = tuple(float(x) for x in np.clip((m - m.min()) / max(1.0, m.max() - m.min()) * 255, 30, 255))
    cap.set(cv2.CAP_PROP_POS_FRAMES, round(t0 * fps))
    n = round(t0 * fps)
    while n < round(t1 * fps):
        ok, fr = cap.read()
        if not ok:
            break
        for hf in hit_frames:
            k = n - hf
            if hf in art:                                    # AI 漫画冲击帧
                H = a.停
                if 0 <= k < H:                                       # 漫画图停 H 帧：缓慢推近 + 轻微抖动，停住但不死
                    z = 1.0 + 0.05 * k / max(1, H - 1)
                    jit = (k % 2) * 6 - 3 if H > 2 else 0
                    M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, z)
                    M[:, 2] += (jit, -jit)
                    fr = cv2.warpAffine(art[hf], M, (w, h), borderMode=cv2.BORDER_REFLECT)
                elif H <= k < H + 2:
                    if fr.mean() < 70:                              # 原画面太暗：颜色加深会压成黑帧，改为提亮爆闪
                        fr = flash(fr, 0.9)
                    else:
                        fr = flash(color_burn(fr, art[hf], 0.5), 0.35)
                elif H + 2 <= k < H + 8:
                    kk = k - H + 2                                   # 2~7，沿用衰减曲线
                    fr = punch(flash(fr, max(0.0, 1 - (kk - 2) / 5)), kk, sl[kk % 4], a.强度 * 0.8, hf, tints[hf])
            elif k in (0, 1):
                fr = manga(fr, invert=(k == 0))
            elif 2 <= k <= 9:
                fr = punch(fr, k, sl[k % 4], a.强度, hf)
        vw.write(fr)
        n += 1
    vw.release()
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", tmp, "-ss", f"{t0:.3f}", "-to", f"{t1:.3f}", "-i", a.src,
           "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
           "-shortest", a.dst]
    subprocess.run(cmd, check=True)
    os.remove(tmp)
    print(f"已输出 {a.dst}：{t1 - t0:.2f}s，命中点 {', '.join(f'{t:.2f}s' for t in hits)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
