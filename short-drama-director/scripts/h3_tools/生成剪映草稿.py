# -*- coding: utf-8 -*-
"""生成剪映草稿：把"动作剪辑"的分段方案写成剪映时间线，打开剪映即可精修（加音效、曲线变速、导出）。

用法：
  python 生成剪映草稿.py <草稿名> <输入.mp4> 段1 段2 ...
段的写法与 动作剪辑.py 相同：起点-终点@倍速[+推][+震]，例如
  0.3-6@1.2  6-7.5@1.8  7.5-8.9@1+推  8.9-10.8@1+震  10.8-13.9@1.15+震
  +推：片段内关键帧放大 1.0→1.25（由慢到快）
  +震：片段开头叠 0.2s "闪白" + 0.35s "色散冲击"，整段叠"震动"特效（放在独立特效轨，剪映里可直接调强度或删掉）
可选参数（写在分段后面，时间都是"成片时间线"上的秒数）：
  音效:时间=文件[*音量]   在该时间点放一个音效，文件可写 P4任务/音效库 里的文件名，音量默认 1.0
                          例：音效:6.98=重低音冲击.wav*1.2
  静:起-止[*音量]         把原片声音在这段压低（默认压到 0.12），做"先静再炸"
                          例：静:5.6-6.5
草稿生成到剪映实际使用的草稿目录（自动从剪映配置里识别），画布 1080x1920、24fps。生成前请关闭剪映，生成后重新打开剪映即可在草稿列表看到。
"""
import os
import re
import sys

import pyJianYingDraft as draft
from pyJianYingDraft import (AudioMaterial, AudioSegment, KeyframeProperty, TrackSpec, TrackType,
                             VideoMaterial, VideoSceneEffectType, VideoSegment, trange)

SFX_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "音效库")

DEFAULT_ROOT = os.path.join(os.environ["LOCALAPPDATA"], "JianyingPro", "User Data", "Projects", "com.lveditor.draft")
PUSH_MAX = 1.25


def find_draft_root():
    """剪映可在设置里改草稿位置；从 root_meta_info.json 里已有草稿的路径推断实际草稿目录。"""
    import collections
    import json
    meta = os.path.join(DEFAULT_ROOT, "root_meta_info.json")
    try:
        with open(meta, encoding="utf-8") as f:
            store = json.load(f).get("all_draft_store", [])
        parents = collections.Counter(os.path.dirname(x.get("draft_fold_path", "")) for x in store if x.get("draft_fold_path"))
        if parents:
            root = os.path.normpath(parents.most_common(1)[0][0])
            if os.path.isdir(root):
                return root
    except (OSError, ValueError):
        pass
    return DEFAULT_ROOT


DRAFT_ROOT = find_draft_root()


def free_name(folder, name):
    """同名草稿已存在时不覆盖（可能正被剪映打开或已被手动修改），改用 名字_v2、_v3…"""
    if not folder.has_draft(name):
        return name
    k = 2
    while folder.has_draft(f"{name}_v{k}"):
        k += 1
    return f"{name}_v{k}"


RAMP = (0.75, 1.0, 1.4, 2.0)   # +冲：曲线加速四段的相对倍速（与 动作剪辑.py 一致）


def parse_full(spec):
    """解析 起点-终点@倍速[+推][+震][+冲][+闪]，返回 dict。"""
    m = re.fullmatch(r"([\d.]+)-([\d.]+)@([\d.]+)((?:\+推|\+震|\+冲|\+闪)*)", spec)
    if not m:
        raise SystemExit(f"段格式不对：{spec}（应为 起点-终点@倍速[+推][+震][+冲][+闪]）")
    a, b, sp, flags = float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4)
    if b <= a or sp <= 0:
        raise SystemExit(f"段数值不对：{spec}")
    seg = dict(a=a, b=b, sp=sp, push="+推" in flags, shake="+震" in flags,
               ramp="+冲" in flags, flash="+闪" in flags)
    if seg["ramp"] and seg["push"]:
        raise SystemExit(f"{spec}：+冲 不与 +推 同用")
    return seg


def expand(seg):
    """曲线加速段展开成四个小片（倍速依次 0.75/1.0/1.4/2.0 × 段倍速），其余段原样；first 标记段首。"""
    if not seg["ramp"]:
        return [dict(seg, first=True)]
    step = (seg["b"] - seg["a"]) / len(RAMP)
    return [dict(seg, a=seg["a"] + k * step, b=seg["a"] + (k + 1) * step, sp=seg["sp"] * r, first=(k == 0))
            for k, r in enumerate(RAMP)]


def seg_entry(entry):
    """分段条目：字符串，或 {"段": spec, "放大": 1.4, "焦点": [x, y]}。返回 (spec, zoom, (fx, fy))。"""
    if isinstance(entry, str):
        return entry, 1.0, (0.5, 0.5)
    zoom = float(entry.get("放大", 1.0))
    if zoom < 1.0:
        raise SystemExit(f"放大不能小于 1：{entry}")
    fx, fy = entry.get("焦点", [0.5, 0.5])
    return entry["段"], zoom, (float(fx), float(fy))


def focus_transform(zoom, fill, focus):
    """把原画面里的焦点 (fx, fy) 移到画布中心所需的剪映位移（单位：半个画布；y 向上为正），并夹在不露边的范围内。"""
    s = zoom * fill
    lim = max(0.0, s - 1.0)
    tx = max(-lim, min(lim, (0.5 - focus[0]) * 2 * s))
    ty = max(-lim, min(lim, (focus[1] - 0.5) * 2 * s))
    return tx, ty


def parse(spec):
    """旧接口：返回 (a, b, sp, push, shake)，不含 +冲/+闪。"""
    seg = parse_full(spec)
    return seg["a"], seg["b"], seg["sp"], seg["push"], seg["shake"]


def us(sec):
    return int(round(sec * 1_000_000))


def parse_extras(extras):
    sfx, dips = [], []
    for x in extras:
        if x.startswith("音效:"):
            m = re.fullmatch(r"音效:([\d.]+)=(.+?)(?:\*([\d.]+))?", x)
            if not m:
                raise SystemExit(f"音效格式不对：{x}（应为 音效:时间=文件[*音量]）")
            path = m.group(2)
            if not os.path.isfile(path):
                path = os.path.join(SFX_DIR, path)
            if not os.path.isfile(path):
                raise SystemExit(f"找不到音效文件：{m.group(2)}")
            sfx.append((float(m.group(1)), os.path.abspath(path), float(m.group(3) or 1.0)))
        elif x.startswith("静:"):
            m = re.fullmatch(r"静:([\d.]+)-([\d.]+)(?:\*([\d.]+))?", x)
            if not m:
                raise SystemExit(f"静音段格式不对：{x}（应为 静:起-止[*音量]）")
            dips.append((float(m.group(1)), float(m.group(2)), float(m.group(3) or 0.12)))
        else:
            raise SystemExit(f"看不懂的参数：{x}")
    return sfx, dips


def add_dips(seg, seg_start, seg_len, dips):
    """在视频片段上用音量关键帧把原声压低（时间换算成片段内偏移）。"""
    points = []
    for a, b, v in dips:
        lo, hi = max(a, seg_start), min(b, seg_start + seg_len)
        if lo >= hi:
            continue
        rel_lo, rel_hi = lo - seg_start, hi - seg_start
        if rel_lo > 0.06:
            points.append((rel_lo - 0.06, 1.0))
        points += [(rel_lo, v), (rel_hi, v)]
        if rel_hi + 0.12 < seg_len:
            points.append((rel_hi + 0.12, 1.0))
    for t, v in sorted(points):
        seg.add_keyframe(KeyframeProperty.volume, us(t), v)


def build(name, video_path, specs, extras=()):
    sfx, dips = parse_extras(extras)
    video_path = os.path.abspath(video_path)
    folder = draft.DraftFolder(DRAFT_ROOT)
    name = free_name(folder, name)
    script = folder.create_draft(name, 1080, 1920, fps=24)
    script.append_track(TrackSpec(TrackType.video, "主画面"))
    script.append_track(TrackSpec(TrackType.effect, "冲击特效"))
    material = VideoMaterial(video_path)

    cursor = 0.0
    for a, b, sp, push, shake in (parse(s) for s in specs):
        out_len = (b - a) / sp
        seg = VideoSegment(material, trange(us(cursor), us(out_len)),
                           source_timerange=trange(us(a), us(b - a)), speed=sp)
        if push:
            seg.add_keyframe(KeyframeProperty.uniform_scale, 0, 1.0)
            seg.add_keyframe(KeyframeProperty.uniform_scale, us(out_len * 0.6), 1.06)
            seg.add_keyframe(KeyframeProperty.uniform_scale, us(out_len), PUSH_MAX)
        if dips:
            add_dips(seg, cursor, out_len, dips)
        script.add_segment(seg, "主画面")
        if shake:
            script.add_effect(VideoSceneEffectType.闪白, trange(us(cursor), us(min(0.2, out_len))), "冲击特效")
            script.add_effect(VideoSceneEffectType.色散冲击, trange(us(cursor + 0.2), us(min(0.35, max(0.05, out_len - 0.2)))), "冲击特效")
            script.add_effect(VideoSceneEffectType.震动, trange(us(cursor + 0.55), us(max(0.1, out_len - 0.55))), "冲击特效")
        cursor += out_len

    track_ends = []
    for t, path, vol in sorted(sfx):
        mat = AudioMaterial(path)
        dur = min(mat.duration / 1_000_000, max(0.1, cursor - t))
        idx = next((i for i, end in enumerate(track_ends) if end <= t), None)
        if idx is None:
            idx = len(track_ends)
            track_ends.append(0.0)
            script.append_track(TrackSpec(TrackType.audio, f"音效{idx + 1}"))
        track_ends[idx] = t + dur
        aseg = AudioSegment(mat, trange(us(t), us(dur)), volume=vol)
        script.add_segment(aseg, f"音效{idx + 1}")
    script.save()
    print(f"已生成剪映草稿「{name}」，时长约 {cursor:.1f} 秒")
    print(f"位置：{os.path.join(DRAFT_ROOT, name)}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    rest = sys.argv[3:]
    specs = [x for x in rest if not (x.startswith("音效:") or x.startswith("静:"))]
    extras = [x for x in rest if x.startswith("音效:") or x.startswith("静:")]
    build(sys.argv[1], sys.argv[2], specs, extras)
