# -*- coding: utf-8 -*-
"""专业精剪方案生成器 · 示例（V7.2）。复制到项目 P4任务/工具/ 后按本集改 SEGS 即可。
所有时间都写**原片时间**（每段 H3 出片里的秒数），脚本自动换算成整集成片时间，输出：
  P4任务/EPxx_整集_剪辑方案.json   → 渲染整集.py（预览成片）/ 拼接草稿.py（剪映草稿）
  配乐/EPxx_整集_配乐提示表.json   → 合成配乐.py
内置检查：有人声（台词/笑/吼，人声定位.py 检出）的区间落进变速分段 → 直接报错（加速会让笑声和尾音发怪）。
分段写法：起-止@倍速[+冲][+闪][+震][+推]；字幕类型 ""=台词 / "OS"=心声 / "标题"=居中大字；
人名条：(段内原片秒, 名, 身份, 印章字, 左|右, 时长)，放在人物本集第一次露脸、脸的对侧。"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
vd = importlib.import_module("人声定位")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # P4任务
EP = "EP01"
P = "专业/"   # 音效库/专业/ 下的文件

SEGS = [
    dict(名称="开头钩子", 素材="E01-4_H3/素材_00004.mp4", 分段=["2.9-5.6@1+推"],
         字幕=[(2.95, 5.2, "（本集最炸的一句台词）", "")], 音效=[], 配乐=dict(让位=[(2.9, 5.6)])),
    dict(名称="E01-1 开场打斗", 素材="E01-1_H3/素材_00001_冲击.mp4",   # 冲击帧特效.py 预渲染的版本
         分段=["0-0.4@1+闪", "0.4-2.4@1+震", "2.4-4.4@1.25", "4.4-6.8@1", "6.8-13.4@1", "13.4-15.0@1.25"],
         字幕=[(7.0, 8.3, "（台词前半句，", ""), (8.9, 10.6, "按停顿拆开）", "")],
         人名条=[(6.9, "主角A", "某门派·身份", "魔", "左", 2.0)],
         音效=[(0.4, P + "冲击_拳击肉体.wav", 0.40), (2.6, P + "嗖_风冲.wav", 0.20)],
         配乐=dict(段落=[(0, 6.8, "脉冲", 0.55), (6.8, 15.0, "暗底", 0.40)], 鼓点=[0.4], 让位=[(6.8, 13.4)])),
    dict(名称="E01-2 对话", 素材="E01-2_H3/素材_00002.mp4",
         分段=["0.3-2.0@1.1", "2.0-15.0@1"],
         字幕=[(2.0, 4.2, "（台词）", ""), (5.0, 7.6, "（心声）", "OS")],
         音效=[], 配乐=dict(段落=[(0.3, 15.0, "清冷", 0.40)], 让位=[(2.0, 7.8)])),
]
ENDING = {"文": "下集预告 · （集名）", "秒": 3.0}   # 片尾黑场 + 居中标题；不要就设为 None


def pieces(spec):
    rng, rest = spec.split("@")
    a, b = map(float, rng.split("-"))
    sp = float(rest.split("+")[0])
    if "+冲" in rest:   # 与 生成剪映草稿.expand 一致：四小段 0.75/1.0/1.4/2.0 倍
        q = (b - a) / 4
        return [(a + i * q, a + (i + 1) * q, sp * r) for i, r in enumerate((0.75, 1.0, 1.4, 2.0))]
    return [(a, b, sp)]


def seg_map(segs):
    out, cur = [], 0.0
    for s in segs:
        for a, b, sp in pieces(s):
            out.append((a, b, sp, cur))
            cur += max(1, round((b - a) / sp * 24)) / 24   # 与 渲染整集.py 的帧取整一致
    return out, cur


def to_out(m, t):
    for a, b, sp, o in m:
        if a - 1e-6 <= t <= b + 1e-6:
            return round(o + (t - a) / sp, 3)
    later = [(a, o) for a, b, sp, o in m if a >= t]
    return round(min(later)[1], 3) if later else round(m[-1][3] + (m[-1][1] - m[-1][0]) / m[-1][2], 3)


def main():
    parts, cue = [], {"段落": [], "鼓点": [], "轰鸣": [], "蓄力": [], "静默": [], "让位": []}
    offset = 0.0
    for s in SEGS:
        m, total = seg_map(s["分段"])
        f = lambda t: to_out(m, t)
        src = os.path.join(BASE, s["素材"].replace("_冲击.mp4", ".mp4"))
        voice = vd.segments(vd.voiced(vd.load(src)), gap=0.08, min_len=0.08)
        for spec in s["分段"]:
            for a, b, sp in pieces(spec):
                hit = [(va, vb) for va, vb in voice if va < b - 0.05 and vb > a + 0.05]
                if abs(sp - 1) > 1e-6 and hit:
                    raise SystemExit(f"{s['名称']} 分段 {spec} 是 {sp} 倍速，但里面有人声 {hit}——改成原速或挪剪点")
        parts.append({"名称": s["名称"], "素材": s["素材"], "分段": s["分段"],
                      "字幕": [{"起": f(a), "止": f(b), "文": t, "类型": k} for a, b, t, k in s["字幕"]],
                      "音效": [f"{f(t):.3f}={p}*{v}" for t, p, v in s["音效"]],
                      "人名条": [{"起": f(t), "名": n, "身份": i, "印": y, "侧": c, "时长": d} for t, n, i, y, c, d in s.get("人名条", [])]})
        c = s["配乐"]
        for a, b, kind, strength in c.get("段落", []):
            cue["段落"].append({"起": round(offset + f(a), 3), "止": round(offset + f(b), 3), "类型": kind, "强度": strength})
        for key in ("鼓点", "轰鸣"):
            cue[key] += [round(offset + f(t), 3) for t in c.get(key, [])]
        for key in ("蓄力", "静默", "让位"):
            cue[key] += [[round(offset + f(a), 3), round(offset + f(b), 3)] for a, b in c.get(key, [])]
        offset += total
    if ENDING:
        n = int(ENDING["秒"])
        parts.append({"名称": "片尾黑场", "素材": "工具/黑场1s_高清.mp4", "分段": ["0-1@1"] * n,
                      "字幕": [{"起": 0.5, "止": n - 0.1, "文": ENDING["文"], "类型": "标题"}], "音效": []})
        cue["段落"].append({"起": round(offset, 3), "止": round(offset + n, 3), "类型": "清冷", "强度": 0.35})
        offset += n
    cue["总长"] = round(offset, 3)
    cue["调性根音Hz"] = 73.42
    plan = {"草稿名": f"{EP}_专业精剪", "画面填充": 1.02, "段落": parts,
            "背景音乐": {"文件": f"配乐/配乐_{EP}_整集.wav", "音量": 0.45}}
    json.dump(plan, open(os.path.join(BASE, f"{EP}_整集_剪辑方案.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(cue, open(os.path.join(BASE, "配乐", f"{EP}_整集_配乐提示表.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"方案已写出：总长约 {offset:.1f}s，{len(parts)} 段落")


if __name__ == "__main__":
    main()
