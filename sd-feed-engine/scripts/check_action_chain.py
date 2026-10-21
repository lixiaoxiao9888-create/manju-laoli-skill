#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_action_chain.py — 动作链时长门（C-act）· 投喂提示词结构自检补丁

背景（2026-10-21 ·《汴京谜卷》EP01 实拍复盘）：
  现行三层审核（分镜自检 / 六道闸门 / validate_prompt.py 全部机检码）只检查
  「台词时长」（语速 6 字/秒），没有任何一层检查「动作量与镜长的物理匹配」。
  无台词镜（纯动作镜）是机检盲区——9 个动作拍塞 4 秒照样放行，成片动作被模型
  大幅砍删（表演缩水的直接成因之一）。本脚本把动作的物理速度约束规则化。

物理口径（动作的「6 字/秒」）：
  表情/微动作            0.3s/拍（瞳/眉/睫/目光 变化）
  单一肢体动作           0.6s/拍（手/臂/头 施动动词）
  复合位移动作           1.2s/拍（走/冲/退/跨/扑/掠 + 位移）
  转场遮挡               1.5s/拍（遮住/掠过/移开/合拢）
  光线/环境展示          0.5s/项（照亮/浮出/层次；每镜封顶 2 项）
  台词时间 = 字数/5.5 + 标点停顿补偿（与闸门2 同口径）

判定：
  比率 = (动作链时间 + 台词时间) / 镜长
  > 1.5  → FAIL（严重超载：必然砍动作或砍停顿）
  > 1.1  → WARN（超载：复核加时或删动作拍）
  全景/远景/大远景镜阈值放宽 15%（多主体并行动作）

用法：
  python check_action_chain.py <投喂稿.md> [--strict] [--json]
    --strict   WARN 也计入退出码（交付门禁用）
    --json     结构化输出

退出码：0 = 通过；1 = 存在 FAIL；2 = 仅存在 WARN（--strict 时）。
独立补丁脚本，不依赖技能库内任何模块；技能库官方收录本门后可退休。
"""

import io
import json
import re
import sys

# ── 动作动词表（子串匹配） ─────────────────────────────────────────
# 复合位移（1.2s）：发生空间移动的动作
DISPLACE = [
    "回身", "转身", "起身", "翻身", "回头", "回头", "弯腰", "俯冲",
    "走", "跑", "冲", "退", "跨", "扑", "掠", "追", "撞翻", "撞",
    "进入", "进棚", "入画", "进屋", "离场", "离画", "走近", "逼近",
    "欺进", "翻出", "掠出", "跨出", "走出", "退出", "跳", "爬", "登",
]
# 转场遮挡（1.5s）
TRANSITION = ["遮住", "掠过", "移开", "合拢", "没入", "吞进", "掩没", "浮沉", "挡在身前", "横挡"]
# 表情/微动作（0.3s）：依托眼面部词的细小变化
MICRO = ["瞳孔", "眉梢", "眉峰", "眉间", "睫毛", "眼睫", "眼皮", "眼缝", "眼底", "眼神",
         "目光", "视线", "眨", "眯眼", "垂眼", "抬眼", "扫一眼", "扫视", "盯", "望向",
         "望向", "看向", "瞅", "打量", "眼皮不抬", "锁定", "钉住", "锁视"]
# 环境展示（0.5s/项，每镜封顶 2）：静景描述动词
AMBIENT = ["照亮", "灯花", "火星", "浮尘", "钉满", "挂着", "摆着", "沉在", "映着", "浮着",
           "渗入", "漏下", "透进", "透过", "占满", "贴着", "层次", "腾起", "糊了", "发亮",
           "波动", "轻晃", "颤", "掀起", "掠过影", "拖出影子", "投在", "反光", "发光"]
# 一般肢体动作（0.6s）：其余施动动词
ACT = [
    "插", "推到底", "推", "落死", "落笔", "落", "按", "点燃油灯", "点燃", "点着",
    "掀", "翻", "拧", "泼", "砸", "矮身", "劈", "削", "挡", "滚落", "滚动",
    "抄", "卷进", "卷起", "卷", "扑上", "抓", "刮出", "喊出", "喊", "撕", "缠紧", "缠",
    "打结", "晃亮", "扫过", "扫", "捻", "凑近", "凑到", "凑", "睁开", "闭了一次眼", "闭眼",
    "顿住", "顿", "抬起", "抬手", "抬", "撇", "甩", "转", "掩好", "掩", "抹平", "抹",
    "压回", "压", "铺平", "铺", "铺开", "补完", "补", "夹出", "夹回", "夹", "掐住", "掐",
    "掰开", "掰", "探入", "探", "丢", "咳", "瘫", "垂", "挑", "撞", "挤字", "挤",
    "拢", "搁", "摊开", "摊", "展开", "抽出", "抽", "携", "接钱", "接", "递",
    "捡", "拾", "扔", "抛", "掷", "攥", "捏", "拽", "拖", "拉", "撑膝", "撑",
    "吞", "咽", "咳出", "吐出", "吐", "咬", "嚼", "舔", "抿", "张到极限", "张",
    "灌进", "灌", "泼流", "流", "淌", "洒", "泻", "溅", "洇", "沁", "滴",
    "爆", "塌", "坠", "伏", "挣扎", "熄", "灭", "燃", "烧", "坠入",
    "拔", "插进", "塞", "绑", "系", "解", "开", "关", "递给", "送",
    "举", "伸", "缩回", "缩", "抖", "默写", "写", "画", "描", "点出一", "颤了颤", "颤", "叩", "磕", "敲",
    "摩挲", "拍打", "拍", "摸", "拎", "端详", "打量自身", "比划", "虚拍",
]
ALL_ACT = DISPLACE + TRANSITION + MICRO + ACT

# 环境子句豁免：子句仅由环境词+名词构成、无施动主语时按环境计
AMBIENT_MARKERS = AMBIENT

PUNC_SHORT = 0.2   # 逗号/顿号停顿
PUNC_END = 0.4     # 句号/问/叹
PUNC_ELL = 0.8     # 省略号
PUNC_DASH = 0.4    # 破折号
CHARS_PER_SEC = 5.5  # 最快档语速（与闸门2 同口径）

UNIT_RE = re.compile(r"^##\s*【投喂单元\s*(\d+/\d+)\s*·\s*段(\d+)】", re.M)
SHOT_RE = re.compile(
    r"^(\d\d:\d\d)-(\d\d:\d\d)\s*\[镜头(\d+)\]\s*([^。]*?)。\s*"
    r"(?:画面主体|空镜|开场即[^：：]*)[:：]\s*(.*?)(?=。?\s*声音：|$)",
    re.M,
)
DIAL_RE = re.compile(r"台词：(【[^】]*】|.*)$")


def t2s(ts: str) -> int:
    m, s = ts.split(":")
    return int(m) * 60 + int(s)


def split_clauses(text: str):
    text = text.replace("——", "；").replace("——", "；")
    parts = re.split(r"[。；；,，、\n]", text)
    return [p.strip() for p in parts if p.strip()]


def clause_time(clause: str):
    """返回 (seconds, kind)：kind ∈ act/displace/transition/micro/ambient/none"""
    has_disp = any(w in clause for w in DISPLACE)
    has_tran = any(w in clause for w in TRANSITION)
    has_micro = any(w in clause for w in MICRO)
    has_amb = any(w in clause for w in AMBIENT_MARKERS)
    has_act = any(w in clause for w in ACT)

    # 转场遮挡优先
    if has_tran:
        return 1.5, "transition"
    # 位移
    if has_disp:
        return 1.2, "displace"
    # 纯表情子句（含眼面部词，且不含强肢体动词）
    if has_micro and not has_act:
        return 0.3, "micro"
    # 环境展示（环境词存在且无明确肢体施动）
    if has_amb and not has_act:
        return 0.5, "ambient"
    # 一般肢体
    if has_act:
        return 0.6, "act"
    return 0.0, "none"


def dialogue_time(dial: str):
    """台词时间（秒）：字数/5.5 + 标点补偿。dial 含【角色（语气）："…"】整体。"""
    inner = re.findall(r'"([^"]*)"', dial)
    body = "".join(inner) if inner else re.sub(r"^台词：", "", dial)
    body_core = body.strip().strip("。！？.!? ")
    if not body_core or body_core == "无":
        return 0.0
    chars = len(re.sub(r"[^\w]", "", body, flags=re.U))
    if chars <= 1:  # 「无」类单字兜底
        return 0.0
    t = chars / CHARS_PER_SEC
    t += body.count("，") * PUNC_SHORT + body.count("、") * PUNC_SHORT * 0.5
    t += (body.count("。") + body.count("？") + body.count("！")) * PUNC_END
    t += body.count("……") * PUNC_ELL + body.count("—") * PUNC_DASH * 0.5
    return t


def parse(md: str):
    units = []
    cur = None
    for line in md.splitlines():
        mu = UNIT_RE.match(line)
        if mu:
            cur = {"title": line.strip(), "no": mu.group(1), "seg": mu.group(2), "shots": []}
            units.append(cur)
            continue
        if cur is None:
            continue
        ms = SHOT_RE.match(line)
        if not ms:
            continue
        t0, t1, no, head, body = ms.groups()
        dur = t2s(t1) - t2s(t0)
        mdial = DIAL_RE.search(line)
        dial = mdial.group(1) if mdial else ""
        dt = dialogue_time(dial)

        ambient_count = 0
        transition_count = 0
        combat = ("手持" in head) or ("晃动" in head)  # 打戏快节奏：拍时降权
        act_t = 0.0
        details = []
        for c in split_clauses(body):
            sec, kind = clause_time(c)
            if sec <= 0:
                continue
            if kind == "ambient":
                if ambient_count >= 2:
                    continue
                ambient_count += 1
            if kind == "transition":
                if transition_count >= 1:
                    continue
                transition_count += 1
            if combat:
                sec *= 0.7  # 快刃节奏动作更快
            act_t += sec
            details.append((c[:18], kind, round(sec, 2)))

        wide = any(k in head for k in ("全景", "远景"))
        slack = 1.0
        if wide:
            slack *= 1.15
        if combat:
            slack *= 1.3
        # 并行模型：说话时手上动作同步进行，非串行相加
        est = max(act_t, dt) + 0.35 * min(act_t, dt)
        ratio = est / dur if dur else 99
        thr_warn, thr_fail = 1.1 * slack, 1.5 * slack
        verdict = "PASS"
        if ratio > thr_fail:
            verdict = "FAIL"
        elif ratio > thr_warn:
            verdict = "WARN"
        cur["shots"].append({
            "no": int(no), "head": head.strip(), "dur": dur,
            "act": round(act_t, 2), "dial": round(dt, 2), "est": round(est, 2),
            "ratio": round(ratio, 2), "verdict": verdict,
            "details": details, "wide": wide,
        })
    return units


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    as_json = "--json" in args
    path = next((a for a in args if not a.startswith("--")), None)
    if not path:
        print(__doc__)
        sys.exit(3)
    with io.open(path, encoding="utf-8") as f:
        md = f.read()
    units = parse(md)

    n_fail = n_warn = 0
    report = []
    for u in units:
        for s in u["shots"]:
            line = (f"[段{u['seg']}] 镜{s['no']} {s['head'][:26]} | 镜长{s['dur']}s "
                    f"动作{s['act']}s+台词{s['dial']}s={round(s['act']+s['dial'],2)}s "
                    f"比率{s['ratio']} → {s['verdict']}")
            report.append(line)
            if s["verdict"] == "FAIL":
                n_fail += 1
            elif s["verdict"] == "WARN":
                n_warn += 1
    summary = (f"动作链时长门（C-act）：镜 {sum(len(u['shots']) for u in units)} | "
               f"FAIL {n_fail} | WARN {n_warn}")
    if as_json:
        print(json.dumps({"fail": n_fail, "warn": n_warn, "shots": report},
                         ensure_ascii=False, indent=1))
    else:
        print("\n".join(report))
        print(summary)
        if n_fail:
            print("★ 超载镜的「画面主体」需加时或删动作拍——动作没演完就是这类镜（见 ACTION_CHAIN_RULE.md）")
    code = 1 if n_fail else (2 if (strict and n_warn) else 0)
    sys.exit(code)


if __name__ == "__main__":
    main()
