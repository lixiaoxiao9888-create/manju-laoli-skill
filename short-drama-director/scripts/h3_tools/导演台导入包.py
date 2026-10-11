# -*- coding: utf-8 -*-
"""导演台导入包：把若干段（H3提示词 + 参考图 + 时长 + 段间锁）打成 MiniMaxH3Director 的 .mmxpack.zip（r2v）。

格式取自用户导出的 MiniMaxH3Director-r2v-20261010-045122.mmxpack.zip：
  pack.json      生成参数（采样/尺寸/段间锁默认），照抄模板
  timeline.json  segments[]（顶层）与 batchWorkspaces.r2v.segments[]（工作区）两份段落列表
  extra/*.png    参考图；refs[i].index = <Picture i+1>，imageFile = "extra/<文件名>"
帧数：15s = 362 帧，10s = 243 帧（与导演台导出一致）。

用法：
  python 导演台导入包.py <清单.json> <输出.mmxpack.zip>
清单格式：
  {"段": [{"名称": "E06-1a", "目录": "E06-1a_v2_H3", "提示词": "H3提示词v1.txt", "时长": 15, "段间锁": false,
           "参考图": ["参考图1_分镜稿v1_E06-1a.png", "参考图2_山寨广场.png", ...],
           "参考音频": ["../音色库/主角A/参考音频_主角A.wav"]}, ...],      # 可选，最多 3 条，按顺序 = Audio 1..3
   "种子": 666}
目录相对 P4任务；参考图、参考音频的路径相对该段目录。参考图按列表顺序 = Picture 1..N，参考音频 = Audio 1..3
（音频条目格式取自导演台源码 director/pack.py：{"index", "audioFile", "fileName", "type": "input", "subfolder"}）。缺任何一张图都会报错退出，不会生成残缺包。
"""
import copy
import json
import os
import random
import re
import string
import sys
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "导演台导入包模板")
FRAMES = {15: 362, 10: 243}


def new_id():
    return "mv" + "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(11))


def build(manifest_path, out_path):
    man = json.load(open(manifest_path, encoding="utf-8"))
    pack = json.load(open(os.path.join(TPL, "pack.json"), encoding="utf-8"))
    tl = json.load(open(os.path.join(TPL, "timeline.json"), encoding="utf-8"))
    if "种子" in man:
        pack["widgets"]["seed"] = man["种子"]
    seg_tpl = tl["segments"][0]
    ws_tpl = tl["batchWorkspaces"]["r2v"]["segments"][0]

    files, top, ws, start, missing = [], [], [], 0, []
    for k, s in enumerate(man["段"]):
        d = os.path.join(BASE, s["目录"])
        prompt = open(os.path.join(d, s["提示词"]), encoding="utf-8").read()
        frames = FRAMES[s["时长"]]
        refs = []
        for i, name in enumerate(s["参考图"]):
            src = os.path.join(d, name)
            if not os.path.exists(src):
                missing.append(src)
                continue
            arc = re.sub(r"[^a-z0-9_]", "_", s["名称"].lower()) + f"_p{i + 1}.png"   # 导演台要求包内路径只含 a-z0-9_（连字符会报 Pack paths must be ASCII）
            files.append((src, "extra/" + arc))
            refs.append({"index": i, "imageFile": "extra/" + arc, "fileName": arc, "type": "input", "subfolder": "extra", "imageB64": ""})
        auds = []
        assert len(s.get("参考音频", [])) <= 3, s["名称"] + " 参考音频超过 3 条"
        for i, name in enumerate(s.get("参考音频", [])):
            src = os.path.normpath(os.path.join(d, name))
            if not os.path.exists(src):
                missing.append(src)
                continue
            arc = re.sub(r"[^a-z0-9_]", "_", s["名称"].lower()) + f"_a{i + 1}" + os.path.splitext(src)[1].lower()
            files.append((src, "extra/" + arc))
            auds.append({"index": i, "audioFile": "extra/" + arc, "fileName": arc, "type": "input", "subfolder": "extra"})
        vids = []
        assert len(s.get("参考视频", [])) <= 3, s["名称"] + " 参考视频超过 3 条"
        for i, name in enumerate(s.get("参考视频", [])):   # 可选，= <Video 1..3>；格式同导演台源码 director/pack.py（videoFile）
            src = os.path.normpath(os.path.join(d, name))
            if not os.path.exists(src):
                missing.append(src)
                continue
            arc = re.sub(r"[^a-z0-9_]", "_", s["名称"].lower()) + f"_v{i + 1}" + os.path.splitext(src)[1].lower()
            files.append((src, "extra/" + arc))
            vids.append({"index": i, "videoFile": "extra/" + arc, "fileName": arc, "type": "input", "subfolder": "extra"})
        sid = new_id()
        a = copy.deepcopy(seg_tpl)
        a.update({"id": sid, "start": start, "length": frames, "frameCount": frames, "durationSec": s["时长"], "prompt": prompt,
                  "negativePrompt": "", "taskType": "", "refs": refs, "refAudios": auds, "refVideos": vids,
                  "genImage": {"imageFile": "", "fileName": ""}, "startImage": None, "endImage": None,
                  "continuityFromPrev": bool(s["段间锁"]) and k > 0, "refImageSize": "match", "loras": []})
        w = copy.deepcopy(ws_tpl)
        w.update({"id": sid, "start": start, "length": frames, "frameCount": frames, "durationSec": s["时长"], "prompt": prompt,
                  "negativePrompt": "", "taskType": "", "refs": copy.deepcopy(refs), "refAudios": copy.deepcopy(auds), "refVideos": copy.deepcopy(vids),
                  "genImage": {"imageFile": "", "fileName": ""}, "continuityFromPrev": bool(s["段间锁"]) and k > 0,
                  "refImageSize": "match", "loras": [], "_videoFrameCount": frames, "previewFps": 24,
                  "referenceVideo": {"videoFile": "", "fileName": "", "type": "input", "subfolder": ""}})
        top.append(a)
        ws.append(w)
        start += frames
    if missing:
        raise SystemExit("缺参考图，未生成导入包：\n  " + "\n  ".join(missing))

    tl["segments"] = top
    any_lock = any(x["continuityFromPrev"] for x in top)
    for o in (tl["output"], pack["output"]):   # 全局"段间引导"总开关；不开的话每段 continuityFromPrev 不生效（用户 2026-10-10 实测）
        o["continuityEnabled"] = any_lock
    tl["batchWorkspaces"]["r2v"]["segments"] = ws
    tl["batchWorkspaces"]["r2v"]["selectedIndex"] = 0
    tl["batchWorkspaces"]["r2v"]["runSelection"] = list(range(len(top)))
    tl["runSelection"] = list(range(len(top)))
    tl["totalFrames"] = start
    tl["durationSec"] = round(start / 24)
    tl["global"]["refs"] = []
    tl["global"]["prompt"] = "\n"

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("timeline.json", json.dumps(tl, ensure_ascii=False, indent=2))
        z.writestr("pack.json", json.dumps(pack, ensure_ascii=False, indent=2))
        for src, arc in files:
            z.write(src, arc)
    # 自检：能完整读回，refs 指向的文件都在包里
    with zipfile.ZipFile(out_path) as z:
        names = set(z.namelist())
        bad = [n for n in names if not re.fullmatch(r"[A-Za-z0-9_./]+", n)]
        assert not bad, bad
        t = json.loads(z.read("timeline.json"))
        for seg in t["segments"] + t["batchWorkspaces"]["r2v"]["segments"]:
            for r in seg["refs"]:
                assert r["imageFile"] in names, r["imageFile"]
            for r in seg["refAudios"]:
                assert r["audioFile"] in names, r["audioFile"]
            for r in seg["refVideos"]:
                assert r["videoFile"] in names, r["videoFile"]
    print(f"已生成 {out_path}：{len(top)} 段，{start} 帧（约 {start / 24:.0f} 秒），参考图 {len(files)} 张")
    for k, s in enumerate(man["段"]):
        print(f"  {k + 1:2d}. {s['名称']}  {s['时长']}s  段间锁={'开' if top[k]['continuityFromPrev'] else '关'}  参考图 {len(top[k]['refs'])} 张  参考音频 {len(top[k]['refAudios'])} 条  参考视频 {len(top[k]['refVideos'])} 条")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    build(sys.argv[1], sys.argv[2])
