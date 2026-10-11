# -*- coding: utf-8 -*-
"""封面排版（2026-10-11）：AI 生成的无字底图 → 抖音竖封面 3:4（1080×1440）+ 横封面 4:3（1440×1080），加书法标题。
用法：python 封面排版.py <底图.png> <输出目录> --剧名 实测项目 --副标题 实测项目 --集 第八集 --集名 各自的命运 [--角标 季终]
      [--竖裁 y0] [--横裁 x0,y0,w]   （裁切位置按底图像素；不写就自动：竖封面取顶部到人物、横封面取人物半身）
标题：剧名华文行楷金色大字（深色描边 + 金色辉光），副标题楷体，集数/集名白字，角标朱红印章；底部渐暗压字。"""
import argparse
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

F_TITLE = r"C:\Windows\Fonts\STXINGKA.TTF"
F_SUB = r"C:\Windows\Fonts\STKAITI.TTF"
F_EP = r"C:\Windows\Fonts\msyhbd.ttc"
F_SEAL = r"C:\Windows\Fonts\SIMLI.TTF"
GOLD = (236, 200, 120)


def text_img(size, draw_fn):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(im))
    return im


def glow_text(canvas, xy, text, font, fill, stroke=6, stroke_fill=(30, 18, 6), glow=(236, 200, 120), glow_r=18, anchor="mm", spacing=0):
    W, H = canvas.size
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text(xy, text, font=font, fill=glow + (255,), anchor=anchor, stroke_width=stroke + 4, stroke_fill=glow + (255,))
    g = lay.filter(ImageFilter.GaussianBlur(glow_r))
    a = np.asarray(g).astype(np.float32)
    a[..., 3] *= 0.55
    canvas.alpha_composite(Image.fromarray(a.astype(np.uint8), "RGBA"))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0] + 5, xy[1] + 7), text, font=font, fill=(0, 0, 0, 180), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 180))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(canvas).text(xy, text, font=font, fill=fill + (255,), anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill + (255,))


def gold_gradient_text(canvas, xy, text, font, anchor="mm"):
    """金色渐变字：上亮下暗。"""
    W, H = canvas.size
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).text(xy, text, font=font, fill=255, anchor=anchor)
    bbox = mask.getbbox()
    if not bbox:
        return
    grad = np.zeros((H, W, 3), np.float32)
    y0, y1 = bbox[1], bbox[3]
    t = np.clip((np.arange(H) - y0) / max(1, y1 - y0), 0, 1)[:, None]
    top, mid, bot = np.array([255, 240, 200]), np.array([236, 196, 110]), np.array([170, 110, 40])
    col = np.where(t < 0.5, top + (mid - top) * (t / 0.5), mid + (bot - mid) * ((t - 0.5) / 0.5))
    grad[:] = col[:, None, :] if col.ndim == 2 else col
    lay = Image.fromarray(grad.astype(np.uint8), "RGB").convert("RGBA")
    lay.putalpha(mask)
    canvas.alpha_composite(lay)


def seal(canvas, cx, cy, text, s):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((2, 2, s - 3, s - 3), radius=int(s * 0.1), fill=(186, 30, 26, 240))
    f = ImageFont.truetype(F_SEAL, int(s * (0.6 if len(text) == 1 else 0.38)))
    if len(text) <= 1:
        d.text((s / 2, s / 2), text, font=f, fill=(252, 240, 222), anchor="mm")
    else:
        for i, ch in enumerate(text[:2]):
            d.text((s / 2, s * (0.29 + 0.42 * i)), ch, font=f, fill=(252, 240, 222), anchor="mm")
    canvas.alpha_composite(im, (int(cx - s / 2), int(cy - s / 2)))


def bottom_shade(img, start, strength=0.82):
    W, H = img.size
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    t = np.clip((np.arange(H) - start) / max(1, H - start), 0, 1) ** 1.3
    a *= (1 - strength * t)[:, None, None]
    return Image.fromarray(a.astype(np.uint8)).convert("RGBA")


def side_shade(img, x_end, strength=0.8):
    W, H = img.size
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    t = np.clip((x_end - np.arange(W)) / max(1, x_end), 0, 1) ** 1.2
    a *= (1 - strength * t)[None, :, None]
    return Image.fromarray(a.astype(np.uint8)).convert("RGBA")


def fit(src, x0, y0, w, h, W, H):
    crop = src[y0:y0 + h, x0:x0 + w]
    r = cv2.resize(crop, (W, H), interpolation=cv2.INTER_LANCZOS4)
    blur = cv2.GaussianBlur(r, (0, 0), 1.2)
    r = cv2.addWeighted(r, 1.35, blur, -0.35, 0)          # 放大后轻度锐化
    return Image.fromarray(cv2.cvtColor(r, cv2.COLOR_BGR2RGB)).convert("RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--剧名", required=True); ap.add_argument("--副标题", default="")
    ap.add_argument("--集", default=""); ap.add_argument("--集名", default=""); ap.add_argument("--角标", default="")
    ap.add_argument("--竖裁", type=int, default=None); ap.add_argument("--横裁", default="")
    a = ap.parse_args()
    src = cv2.imdecode(np.fromfile(a.src, np.uint8), cv2.IMREAD_COLOR)
    h0, w0 = src.shape[:2]
    os.makedirs(a.out, exist_ok=True)
    ep = "  ·  ".join(x for x in (a.集, a.集名) if x)

    # 竖封面 3:4
    ch = int(w0 * 4 / 3)
    y0 = a.竖裁 if a.竖裁 is not None else max(0, min(h0 - ch, int(h0 * 0.03)))
    V = fit(src, 0, y0, w0, ch, 1080, 1440)
    V = bottom_shade(V, 860)
    gold_gradient_text(V, (540, 1150), a.剧名, ImageFont.truetype(F_TITLE, 210))
    glow_text(V, (540, 1150), a.剧名, ImageFont.truetype(F_TITLE, 210), fill=(0, 0, 0), stroke=5, stroke_fill=(40, 22, 6), glow_r=22)
    gold_gradient_text(V, (540, 1150), a.剧名, ImageFont.truetype(F_TITLE, 210))
    if a.副标题:
        glow_text(V, (540, 1278), a.副标题, ImageFont.truetype(F_SUB, 64), fill=GOLD, stroke=3, stroke_fill=(20, 12, 4), glow_r=10)
    if ep:
        glow_text(V, (540, 1365), ep, ImageFont.truetype(F_EP, 50), fill=(255, 255, 255), stroke=4, stroke_fill=(0, 0, 0), glow=(255, 255, 255), glow_r=8)
    if a.角标:
        seal(V, 940, 120, a.角标, 120)
    V.convert("RGB").save(os.path.join(a.out, "竖封面_3x4_1080x1440.png"))

    # 横封面 4:3：人物半身铺满，左侧压暗放标题
    if a.横裁:
        x0, y0h, cw = map(int, a.横裁.split(","))
    else:
        cw = w0
        x0, y0h = 0, int(h0 * 0.12)
    chh = int(cw * 3 / 4)
    Hh = fit(src, x0, y0h, cw, chh, 1440, 1080)
    Hh = bottom_shade(Hh, 640, 0.75)
    gold_gradient_text(Hh, (720, 820), a.剧名, ImageFont.truetype(F_TITLE, 200))
    glow_text(Hh, (720, 820), a.剧名, ImageFont.truetype(F_TITLE, 200), fill=(0, 0, 0), stroke=5, stroke_fill=(40, 22, 6), glow_r=22)
    gold_gradient_text(Hh, (720, 820), a.剧名, ImageFont.truetype(F_TITLE, 200))
    line2 = "  ·  ".join(x for x in (a.副标题, (a.集 + " " + a.集名).strip()) if x)
    if line2:
        glow_text(Hh, (720, 960), line2, ImageFont.truetype(F_SUB, 56), fill=GOLD, stroke=3, stroke_fill=(20, 12, 4), glow_r=10)
    if a.角标:
        seal(Hh, 1330, 110, a.角标, 120)
    Hh.convert("RGB").save(os.path.join(a.out, "横封面_4x3_1440x1080.png"))
    print("已输出", a.out)


if __name__ == "__main__":
    main()
