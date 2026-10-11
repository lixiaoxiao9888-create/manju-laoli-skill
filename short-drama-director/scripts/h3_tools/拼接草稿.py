# -*- coding: utf-8 -*-
"""拼接草稿：按一份 JSON 剪辑方案，把多段视频依次排进同一个剪映草稿（每段可有自己的变速/推镜/震屏/音效/压低原声）。

用法：
  python 拼接草稿.py <剪辑方案.json>

方案格式（时间单位秒；音效与"静"的时间是该段剪完后的段内时间）：
{
  "草稿名": "EP01_前四段",
  "画面填充": 1.02,
  "段落": [
    {"名称": "E01-1", "素材": "E01-1_H3v6/素材_00145.mp4",
     "分段": ["0-3@1.1", "4.4-6@1+震"],
     "音效": ["0.0=水花炸裂.wav*0.9"],
     "静": ["3.0-3.85"]}
  ],
  "背景音乐": {"文件": "配乐/配乐_EP01_前四段_临时版.wav", "音量": 0.45}
}
分段也可写成 {"段": "2.0-3.9@1.8+震", "放大": 1.5, "焦点": [0.6, 0.3]}：该段局部放大并把原画面里 (x, y)（0~1，左上为 0,0）
这个点移到画面中心（遮穿帮、半身化全身镜头）。素材路径相对于方案文件所在目录（P4任务）。背景音乐从 0 秒开始铺到整集结尾（可选）。生成前关闭剪映，生成后重开。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib

jy = importlib.import_module("生成剪映草稿")

import pyJianYingDraft as draft
from pyJianYingDraft import (AudioMaterial, AudioSegment, ClipSettings, KeyframeProperty, TrackSpec,
                             TrackType, VideoMaterial, VideoSceneEffectType, VideoSegment, trange, TextSegment, TextStyle, TextBorder, TextShadow)

us = jy.us


def build(plan_path):
    base = os.path.dirname(os.path.abspath(plan_path))
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)
    fill = float(plan.get("画面填充", 1.0))
    folder = draft.DraftFolder(jy.DRAFT_ROOT)
    name = jy.free_name(folder, plan["草稿名"])
    script = folder.create_draft(name, 1080, 1920, fps=24)
    script.append_track(TrackSpec(TrackType.video, "主画面"))
    script.append_track(TrackSpec(TrackType.effect, "冲击特效"))

    cursor_us = 0
    sfx_all, report, subs_all, plates_all = [], [], [], []
    for part in plan["段落"]:
        path = os.path.join(base, part["素材"])
        if not os.path.isfile(path):
            raise SystemExit(f"找不到素材：{path}")
        material = VideoMaterial(os.path.abspath(path))
        sfx, dips = jy.parse_extras([f"音效:{x}" for x in part.get("音效", [])] +
                                    [f"静:{x}" for x in part.get("静", [])])
        part_start = cursor_us / 1_000_000
        for entry in part["分段"]:
            spec, zoom, focus = jy.seg_entry(entry)
            full = jy.parse_full(spec)
            base_scale = fill * zoom
            tx, ty = jy.focus_transform(zoom, fill, focus)
            seg_start = cursor_us / 1_000_000
            for p in jy.expand(full):   # +冲 展开成四个由慢到快的小片（剪映里就是四段连续变速）
                a, b, sp = p["a"], p["b"], p["sp"]
                # 全程用整数微秒累加，避免浮点取整让相邻片段重叠
                src_us = us(b - a)
                tgt_us = round(src_us / sp)
                out_len = tgt_us / 1_000_000
                cursor = cursor_us / 1_000_000
                seg = VideoSegment(material, trange(cursor_us, tgt_us),
                                   source_timerange=trange(us(a), src_us), speed=sp,
                                   clip_settings=ClipSettings(scale_x=base_scale, scale_y=base_scale,
                                                             transform_x=tx, transform_y=ty))
                if p["push"]:
                    seg.add_keyframe(KeyframeProperty.uniform_scale, 0, base_scale)
                    seg.add_keyframe(KeyframeProperty.uniform_scale, us(out_len * 0.6), base_scale * 1.06)
                    seg.add_keyframe(KeyframeProperty.uniform_scale, us(out_len), base_scale * jy.PUSH_MAX)
                if dips:
                    jy.add_dips(seg, cursor - part_start, out_len, dips)
                script.add_segment(seg, "主画面")
                # 以库实际写入的片段时长推进游标（库内部对时长取整的方式可能和这里不同）
                cursor_us = seg.target_timerange.start + seg.target_timerange.duration
            seg_len = cursor_us / 1_000_000 - seg_start
            if full["shake"]:
                script.add_effect(VideoSceneEffectType.闪白, trange(us(seg_start), us(min(0.2, seg_len))), "冲击特效")
                script.add_effect(VideoSceneEffectType.色散冲击,
                                  trange(us(seg_start + 0.2), us(min(0.35, max(0.05, seg_len - 0.2)))), "冲击特效")
                script.add_effect(VideoSceneEffectType.震动,
                                  trange(us(seg_start + 0.55), us(max(0.1, seg_len - 0.55))), "冲击特效")
            elif full["flash"]:
                script.add_effect(VideoSceneEffectType.闪白, trange(us(seg_start), us(min(0.12, seg_len))), "冲击特效")
        cursor = cursor_us / 1_000_000
        for x in part.get("人名条", []):
            plates_all.append((part_start + float(x["起"]), x))
        for x in part.get("字幕", []):
            subs_all.append((part_start + float(x["起"]), part_start + float(x["止"]), x["文"], x.get("类型", "")))
        for t, p, vol in sfx:
            sfx_all.append((part_start + t, p, vol, cursor))
        report.append(f"{part['名称']}: {part_start:.2f}s – {cursor:.2f}s（{cursor - part_start:.1f}s）")

    track_ends = []
    for t, p, vol, part_end in sorted(sfx_all):
        mat = AudioMaterial(p)
        dur = min(mat.duration / 1_000_000, max(0.1, cursor - t))
        idx = next((i for i, end in enumerate(track_ends) if end <= t), None)
        if idx is None:
            idx = len(track_ends)
            track_ends.append(0.0)
            script.append_track(TrackSpec(TrackType.audio, f"音效{idx + 1}"))
        track_ends[idx] = t + dur
        script.add_segment(AudioSegment(mat, trange(us(t), us(dur)), volume=vol), f"音效{idx + 1}")

    if subs_all:   # 字幕轨：白字黑描边、下三分之一；OS（心声/画外）淡蓝斜体。剪映里可整体改字体/位置
        script.append_track(TrackSpec(TrackType.text, "字幕"))
        for a, b, text, kind in subs_all:
            os_ = kind == "OS"
            if kind == "标题":   # 居中大字（片尾/章节卡）
                script.add_segment(TextSegment(text, trange(us(a), us(b - a)),
                                               style=TextStyle(size=16.0, align=1, color=(0.91, 0.77, 0.47)),
                                               shadow=TextShadow(alpha=0.5, distance=3.0),
                                               clip_settings=ClipSettings(transform_y=0.0)), "字幕")
                continue
            script.add_segment(TextSegment(text, trange(us(a), us(b - a)),
                                           style=TextStyle(size=9.0, bold=True, italic=os_, align=1, auto_wrapping=True, max_line_width=0.8,
                                                           color=(0.75, 0.9, 1.0) if os_ else (1.0, 1.0, 1.0)),
                                           border=TextBorder(color=(0.0, 0.0, 0.0), width=45.0),
                                           shadow=TextShadow(alpha=0.6, distance=4.0),
                                           clip_settings=ClipSettings(transform_y=-0.42)), "字幕")
        report.append(f"字幕 {len(subs_all)} 条")

    if plates_all:   # 人名条：竖排行楷名字 + 楷体身份（预览成片里是带动画的版本，见 人名条.py）
        script.append_track(TrackSpec(TrackType.text, "人名条"))
        script.append_track(TrackSpec(TrackType.text, "人名条小字"))
        for t0, x in plates_all:
            d = float(x.get("时长", 2.0))
            left = x.get("侧", "左") == "左"
            script.add_segment(TextSegment(x["名"], trange(us(t0), us(d)),
                                           style=TextStyle(size=22.0, vertical=True, color=(1.0, 0.98, 0.94)),
                                           border=TextBorder(color=(0.0, 0.0, 0.0), width=25.0),
                                           shadow=TextShadow(alpha=0.7, distance=5.0),
                                           clip_settings=ClipSettings(transform_x=-0.72 if left else 0.72, transform_y=0.45)), "人名条")
            if x.get("身份"):
                script.add_segment(TextSegment(x["身份"], trange(us(t0 + 0.4), us(max(0.3, d - 0.4))),
                                               style=TextStyle(size=6.0, vertical=True, color=(0.91, 0.77, 0.47)),
                                               border=TextBorder(color=(0.0, 0.0, 0.0), width=20.0),
                                               clip_settings=ClipSettings(transform_x=-0.55 if left else 0.55, transform_y=0.42)), "人名条小字")
        report.append(f"人名条 {len(plates_all)} 个")

    bgm = plan.get("背景音乐")
    if bgm:
        bgm_path = os.path.abspath(os.path.join(base, bgm["文件"]))
        if not os.path.isfile(bgm_path):
            raise SystemExit(f"找不到背景音乐：{bgm_path}")
        mat = AudioMaterial(bgm_path)
        dur = min(mat.duration, cursor_us)
        script.append_track(TrackSpec(TrackType.audio, "背景音乐"))
        bseg = AudioSegment(mat, trange(0, dur), volume=float(bgm.get("音量", 0.5)))
        bseg.add_fade("0.3s", "0.8s")
        script.add_segment(bseg, "背景音乐")
        report.append(f"背景音乐：{bgm['文件']}（音量 {bgm.get('音量', 0.5)}）")

    script.save()
    print(f"已生成剪映草稿「{name}」，总长约 {cursor:.1f} 秒，音效 {len(sfx_all)} 个")
    print("\n".join(report))
    print(f"位置：{os.path.join(jy.DRAFT_ROOT, name)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    build(sys.argv[1])
