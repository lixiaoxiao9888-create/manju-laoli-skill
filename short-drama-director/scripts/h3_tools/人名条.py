# -*- coding: utf-8 -*-
"""人名条（人物出场字幕 / 角色介绍花字，2026-10-11）：人物第一次出镜时，画面一侧竖排书法大字写名字 + 小字身份 + 朱红印章。

动画（24fps）：
  0.00–0.25s  一道细金线从上往下划出
  0.15–0.80s  名字逐字"刷"出（每个字由上往下笔刷擦出，带金色辉光与墨色投影）
  0.70–1.00s  身份小字淡入、印章"盖"下（由大到小一顿）
  …保持…
  最后 0.35s   整体上飘淡出
用法：
  python 人名条.py --名 主角A --身份 "山寨·三转修士" [--印 魔] [--侧 左|右] [--时长 2.6] --输出 主角A.mov
  python 人名条.py ... --输出 主角A.mov --叠加到 视频.mp4 --起 1.2 --成片 出.mp4      # 顺手叠到一段视频上看效果
输出 .mov 为带透明通道的 PNG 编码（剪映可直接当画中画素材拖进去）；渲染整集.py 的方案里写 "人名条" 字段会自动叠加。
字体：名字用华文行楷（STXINGKA），身份用华文楷体（STKAITI），印章用隶书（SIMLI），都在 C:/Windows/Fonts。
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 24
F_NAME = r"C:\Windows\Fonts\STXINGKA.TTF"
F_SUB = r"C:\Windows\Fonts\STKAITI.TTF"
F_SEAL = r"C:\Windows\Fonts\SIMLI.TTF"
GOLD = (232, 196, 120)


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def text_layer(chars, font, size, step, color, x, y0):
    """竖排：每个字居中放在 (x, y0 + i*step)，返回 RGBA 图与每字的 y 范围。"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(font, size)
    spans = []
    for i, ch in enumerate(chars):
        cy = y0 + i * step
        d.text((x, cy), ch, font=f, fill=color + (255,), anchor="mm")
        spans.append((cy - size // 2 - 6, cy + size // 2 + 6))
    return np.asarray(img).astype(np.float32) / 255.0, spans


def glow(rgba, radius, color, strength):
    a = cv2.GaussianBlur(rgba[..., 3], (0, 0), radius) * strength
    g = np.zeros_like(rgba)
    g[..., :3] = np.array(color, np.float32) / 255.0
    g[..., 3] = np.clip(a, 0, 1)
    return g


def over(dst, src):
    a = src[..., 3:4]
    out = dst.copy()
    out[..., :3] = src[..., :3] * a + dst[..., :3] * (1 - a)
    out[..., 3:4] = a + dst[..., 3:4] * (1 - a)
    return out


def seal_layer(text, cx, cy, size):
    """朱红方印：红底白字（阳刻风），边缘略不规则。"""
    s = int(size)
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((2, 2, s - 3, s - 3), radius=int(s * 0.08), fill=(178, 32, 28, 235))
    f = ImageFont.truetype(F_SEAL, int(s * (0.72 if len(text) == 1 else 0.42)))
    if len(text) == 1:
        d.text((s / 2, s / 2), text, font=f, fill=(250, 238, 220, 255), anchor="mm")
    else:   # 两字竖排
        for i, ch in enumerate(text[:2]):
            d.text((s / 2, s * (0.3 + 0.4 * i)), ch, font=f, fill=(250, 238, 220, 255), anchor="mm")
    arr = np.asarray(img).astype(np.float32) / 255.0
    rng = np.random.default_rng(7)
    noise = cv2.GaussianBlur(rng.random((s, s)).astype(np.float32), (0, 0), 1.2)
    arr[..., 3] *= np.clip(0.75 + noise * 0.5, 0, 1)   # 印泥斑驳
    return arr


def render(name, title, seal, side, dur, out_dir):
    n = round(dur * FPS)
    size = 168 if len(name) <= 3 else 140
    step = int(size * 1.02)
    x_name = int(W * (0.14 if side == "左" else 0.86))
    x_sub = x_name + (int(size * 0.78) if side == "左" else -int(size * 0.78))
    y0 = int(H * 0.20)
    name_l, spans = text_layer(list(name), F_NAME, size, step, (255, 250, 240), x_name, y0)
    shadow = name_l.copy()
    shadow[..., :3] = 0
    shadow[..., 3] = cv2.GaussianBlur(name_l[..., 3], (0, 0), 6) * 0.85
    shadow = np.roll(shadow, (6, 6), axis=(0, 1))
    name_glow = glow(name_l, 14, GOLD, 0.9)
    sub_chars = [c for c in title if c.strip()]
    sub_size = 44
    sub_l, _ = text_layer(sub_chars, F_SUB, sub_size, int(sub_size * 1.12), GOLD, x_sub, y0 - size // 2 + sub_size)
    sub_glow = glow(sub_l, 4, (0, 0, 0), 1.0)
    line_x = x_name + (-int(size * 0.62) if side == "左" else int(size * 0.62))
    line_top, line_bot = y0 - size // 2 - 30, y0 + (len(name) - 1) * step + size // 2 + 30
    seal_img = seal_layer(seal, 0, 0, 74) if seal else None
    seal_c = (x_name + (int(size * 0.05)), line_bot + 70)
    ys = np.arange(H)[:, None]
    # 文字后面一层很淡的墨色晕染，亮背景上也读得清（不是硬底框）
    back = np.zeros((H, W, 4), np.float32)
    bx0, bx1 = sorted((line_x, x_sub + (sub_size if side == "左" else -sub_size)))
    cv2.rectangle(back, (bx0 - 40, line_top - 40), (bx1 + 40, line_bot + 120), (0, 0, 0, 0.42), -1)
    back[..., 3] = cv2.GaussianBlur(back[..., 3], (0, 0), 45)
    for i in range(n):
        t = i / FPS
        frame = np.zeros((H, W, 4), np.float32)
        out_k = 1.0 - ease_out((t - (dur - 0.35)) / 0.35)          # 退场淡出
        drift = int(-40 * (1 - out_k))
        bp = ease_out(t / 0.3)
        if bp > 0:
            b2 = back.copy()
            b2[..., 3] *= bp
            frame = over(frame, b2)
        # 1 金线
        p = ease_out(t / 0.25)
        if p > 0:
            yb = int(line_top + (line_bot - line_top) * p)
            cv2.line(frame, (line_x, line_top), (line_x, yb), (GOLD[0] / 255, GOLD[1] / 255, GOLD[2] / 255, 0.9), 3, cv2.LINE_AA)
        # 2 名字逐字刷出
        mask = np.zeros((H, 1), np.float32)
        for k, (a, b) in enumerate(spans):
            q = ease_out((t - 0.15 - k * 0.14) / 0.22)
            if q <= 0:
                continue
            edge = a + (b - a) * q
            mask += ((ys >= a) & (ys <= b)) * np.clip((edge - ys) / 18.0, 0, 1)
        mask = np.clip(mask, 0, 1)
        for lay in (shadow, name_glow, name_l):
            l2 = lay.copy()
            l2[..., 3] *= mask
            frame = over(frame, l2)
        # 3 身份小字
        sp = ease_out((t - 0.7) / 0.3)
        if sp > 0:
            for lay in (sub_glow, sub_l):
                l2 = lay.copy()
                l2[..., 3] *= sp
                frame = over(frame, l2)
        # 4 印章
        if seal_img is not None:
            st = (t - 0.85) / 0.18
            if st > 0:
                sc = 1.0 + 0.6 * (1 - ease_out(st))
                s = int(seal_img.shape[0] * sc)
                im = cv2.resize(seal_img, (s, s), interpolation=cv2.INTER_LINEAR)
                im[..., 3] *= min(1.0, st * 1.5)
                x0, y0s = seal_c[0] - s // 2, seal_c[1] - s // 2
                layer = np.zeros_like(frame)
                layer[max(0, y0s):y0s + s, max(0, x0):x0 + s] = im[max(0, -y0s):, max(0, -x0):][:H - max(0, y0s), :W - max(0, x0)]
                frame = over(frame, layer)
        frame[..., 3] *= out_k
        if drift:
            frame = np.roll(frame, drift, axis=0)
        Image.fromarray((np.clip(frame, 0, 1) * 255).astype(np.uint8), "RGBA").save(os.path.join(out_dir, f"{i:04d}.png"))
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--名", required=True); ap.add_argument("--身份", default="")
    ap.add_argument("--印", default=""); ap.add_argument("--侧", default="左")
    ap.add_argument("--时长", type=float, default=2.6); ap.add_argument("--输出", required=True)
    ap.add_argument("--叠加到"); ap.add_argument("--起", type=float, default=0.0); ap.add_argument("--成片")
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="nameplate_")
    render(a.名, a.身份, a.印, a.侧, a.时长, tmp)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(tmp, "%04d.png"),
                    "-c:v", "png", "-pix_fmt", "rgba", a.输出], check=True)
    shutil.rmtree(tmp)
    print(f"已输出 {a.输出}（{a.时长}s，带透明通道）")
    if a.叠加到 and a.成片:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.叠加到, "-itsoffset", f"{a.起:.3f}", "-i", a.输出,
                        "-filter_complex", f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[b];"
                                           f"[b][1:v]overlay=0:0:eof_action=pass[v]",
                        "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "copy", a.成片], check=True)
        print(f"已叠加到 {a.成片}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
