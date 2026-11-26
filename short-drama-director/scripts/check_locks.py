#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""锁凭证机检 (check_locks.py) · V8.2.0-SLIM-rev2

为什么存在这个脚本（2026-11-25 用户追责事故）：
    包规第 61/112/248 行写明「五道前置锁 + I 画风锁全部必须弹出让用户选」，
    但全套机检里没有任何一条断言「锁值来自用户」。
    audit_contract.py 的 CT1-P0A 只在契约表里声明、未写实现（幽灵项），
    于是「执行者自己写一张锁表 → 自己宣布 PASS」的自我认证路径完全畅通，
    连续三次出现「按默认值代填锁、把门停的『继续』当锁确认」。

本脚本的存在意义：把「锁必须由用户勾选」变成机器可判定的断言。
没有 src=user 的凭证行 = FAIL，代填在物理上过不了门。

用法：
    python check_locks.py <项目文件.md> [--multi-segment] [--self-test]
    python check_locks.py <项目文件.md> --format   # 打印台账模板

台账格式（写在 00_立项包.md 或 05_项目主档.md 内）：

    <!-- LOCK-LEDGER:BEGIN -->
    [LOCK] name=A | value=2.5 | src=user | ev=卡片勾选「① Seedance 2.5」 | ts=2026-11-25T14:20
    <!-- LOCK-LEDGER:END -->

必需项：〇·1 素材来源 / A 模型 / B 画幅 / C 交付 / 板式 / I 画风
    D 段缝：多段任务（--multi-segment）必填；单段任务可省

判定项：
    L1 台账块在位（含 BEGIN/END 标记）
    L2 六项必需锁齐全（多段任务加 D 共七项）
    L3 每项 src=user —— 出现 default/agent/infer/preset 即 FAIL（这就是「代填」）
    L4 ev 为用户凭证（含「」/""/勾选/用户回 之一），且不含 默认/代填/推断/假设/推测
    L5 ts 为 YYYY-MM-DD 或 ISO 时间
    L6 值域合法（A ∈ 2.5/2.0；B ∈ 16:9/9:16/21:9；板式 四格/八格 二选一）
    L7 无重复锁项（同一锁写两行 = 后写覆盖前写，属静默改锁）
"""
import os
import re
import sys
import tempfile

REQUIRED = [
    ("〇·1", ("〇·1", "〇1", "素材来源")),
    ("A", ("A", "A 模型", "模型版本")),
    ("B", ("B", "B 画幅", "画幅")),
    ("C", ("C", "C 交付", "交付形态")),
    ("板式", ("板式", "角色资产板式")),
    ("场景方案", ("场景方案", "场景站位方案", "场景站位", "场景")),
    ("I", ("I", "I 画风", "画风锁")),
]
REQUIRED_MULTI = ("D", ("D", "D 段缝", "段缝衔接"))

BAD_SRC = ("default", "agent", "infer", "inferred", "preset", "auto", "assume")
# 只禁「以默认/推断充当凭证」的强信号词。不能把「默认」「代填」二字一律禁掉：
#   · 包规 Step4 的合法选项原文就叫「不叠加（默认）」；
#   · 弹卡 label 历史上写过「（当前代填值）」，照抄勾选项属合法凭证。
# 真正的判据是「有没有用户证据」= EVIDENCE_MARKS，两者同时满足才算过。
FORBIDDEN_EV = ("按默认走", "默认值走", "按默认执行", "自行判定", "未问用户", "未弹卡", "推断得出", "假设", "推测")
EVIDENCE_MARKS = ("「", "」", "\"", "勾选", "用户回", "用户原话", "用户指定", "用户确认")

BEGIN_MARK = "<!-- LOCK-LEDGER:BEGIN -->"
END_MARK = "<!-- LOCK-LEDGER:END -->"

TEMPLATE = """<!-- LOCK-LEDGER:BEGIN -->
[LOCK] name=〇·1 | value=③对标爆款 | src=user | ev=用户原话「（原句照抄）」 | ts=YYYY-MM-DDTHH:MM
[LOCK] name=A | value=2.5 | src=user | ev=卡片勾选「① Seedance 2.5」 | ts=YYYY-MM-DDTHH:MM
[LOCK] name=B | value=16:9 | src=user | ev=卡片勾选「① 16:9 横屏」 | ts=YYYY-MM-DDTHH:MM
[LOCK] name=C | value=①离线看板 | src=user | ev=卡片勾选「① 离线看板」 | ts=YYYY-MM-DDTHH:MM
[LOCK] name=D | value=②换机位硬切 | src=user | ev=卡片勾选「② 换机位硬切」 | ts=YYYY-MM-DDTHH:MM
[LOCK] name=板式 | value=①16:9 四格纯图板 | src=user | ev=卡片勾选「① 16:9 四格纯图板」 | ts=YYYY-MM-DDTHH:MM
[LOCK] name=场景方案 | value=①双图方案C+（模板图+白模图） | src=user | ev=卡片勾选「① 双图方案 C+」 | ts=YYYY-MM-DDTHH:MM
[LOCK] name=I | value=真人实拍+诺兰向·T7 | src=user | ev=卡片勾选「C 诺兰向」+Step4「不叠加」 | ts=YYYY-MM-DDTHH:MM
<!-- LOCK-LEDGER:END -->"""


def _parse_rows(block):
    """解析台账块内的 [LOCK] 行 → [{name, value, src, ev, ts}, ...]"""
    rows = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("[LOCK]"):
            continue
        body = line[len("[LOCK]"):]
        row = {}
        for part in body.split("|"):
            part = part.strip()
            if "=" not in part:
                continue
            k, v = part.split("=", 1)
            row[k.strip().lower()] = v.strip()
        if row:
            rows.append(row)
    return rows


def _match_name(row_name, aliases):
    n = (row_name or "").strip()
    for a in aliases:
        if n == a:
            return True
    for a in aliases:
        if a and a in n and len(a) >= 2:
            return True
    # A / B / C / D / I 这类单字母锁：只允许完全相等，避免子串误命中
    return False


def audit_text(text, multi_segment=False):
    """返回 (passed:list[str], fails:list[str], warns:list[str])"""
    passed, fails, warns = [], [], []

    # L1 台账块
    if BEGIN_MARK not in text or END_MARK not in text:
        fails.append(
            "L1 缺失锁台账块（须在 00_立项包 / 05_项目主档 内写 %s … %s）——" % (BEGIN_MARK, END_MARK)
            + "无台账 = 无法证明锁值来自用户 = 视为代填"
        )
        return passed, fails, warns
    start = text.index(BEGIN_MARK) + len(BEGIN_MARK)
    end = text.index(END_MARK)
    block = text[start:end]
    rows = _parse_rows(block)
    if not rows:
        fails.append("L1 台账块为空（BEGIN/END 之间没有任何 [LOCK] 行）")
        return passed, fails, warns

    # L7 重复锁项
    seen = {}
    for r in rows:
        nm = (r.get("name") or "").strip()
        if nm in seen:
            fails.append("L7 锁项重复：`%s` 出现两次以上（后写覆盖前写 = 静默改锁）" % nm)
        seen[nm] = seen.get(nm, 0) + 1

    need = list(REQUIRED) + ([REQUIRED_MULTI] if multi_segment else [])
    for canonical, aliases in need:
        hit = None
        for r in rows:
            if _match_name(r.get("name"), aliases):
                hit = r
                break
        if hit is None:
            tip = "（多段任务必填）" if canonical == "D" else ""
            fails.append("L2 缺失锁项 `%s`%s：台账里没有这一行" % (canonical, tip))
            continue

        src = (hit.get("src") or "").strip().lower()
        ev = (hit.get("ev") or "").strip()
        ts = (hit.get("ts") or "").strip()
        val = (hit.get("value") or "").strip()

        # L3 来源
        if src != "user":
            if any(b in src for b in BAD_SRC) or src == "":
                fails.append(
                    "L3 `%s` 来源不是用户（src=%s）——这就是「代填」。"
                    "锁值只能来自用户勾选或用户原话，禁止 default/agent/infer/preset" % (canonical, src or "空")
                )
            else:
                fails.append("L3 `%s` 来源非法（src=%s），唯一合法值 = user" % (canonical, src))
        else:
            passed.append("L3 `%s` src=user" % canonical)

        # L4 凭证
        if not ev:
            fails.append("L4 `%s` 缺用户凭证 ev（须照抄用户勾选/原话）" % canonical)
        else:
            bad = [t for t in FORBIDDEN_EV if t in ev]
            if bad:
                fails.append("L4 `%s` 凭证含代填词 %s（ev=%s）——凭证必须是用户原话或勾选项原文" % (canonical, bad, ev))
            elif not any(m in ev for m in EVIDENCE_MARKS):
                fails.append("L4 `%s` 凭证不像用户证据（ev=%s）：须含「」/\"\"/勾选/用户回 之一" % (canonical, ev))
            else:
                passed.append("L4 `%s` 凭证在位" % canonical)

        # L5 时间戳
        if not re.search(r"\d{4}-\d{2}-\d{2}", ts):
            fails.append("L5 `%s` 缺时间戳 ts（YYYY-MM-DD 或 ISO）" % canonical)

        # L6 值域（A/B 兼容带选项前缀或型号全名写法，但严禁同时出现两个值）
        if canonical == "A":
            a_hits = re.findall(r"(?<!\d)(2\.5|2\.0)(?!\d)", val)
            if len(set(a_hits)) != 1:
                fails.append("L6 `A` 值非法（value=%s）：只允许唯一指定 2.5 或 2.0" % val)
        elif canonical == "B":
            b_hits = re.findall(r"(16:9|9:16|21:9)", val)
            if len(set(b_hits)) != 1:
                fails.append("L6 `B` 值非法（value=%s）：只允许唯一指定 16:9 / 9:16 / 21:9" % val)
        elif canonical == "板式":
            quad = "四格" in val
            octa = "八格" in val
            if quad == octa:
                fails.append("L6 `板式` 值非法（value=%s）：四格/八格必须二选一（互斥铁律）" % val)
        elif canonical == "场景方案":
            has_c2 = any(k in val for k in ("二合一", "C++", "c++", "单张实景"))
            has_c1 = any(k in val for k in ("双图", "C+", "c+", "模板图", "白模", "五视图")) and not any(k in val for k in ("C++", "c++"))
            both = has_c2 and any(k in val for k in ("双图", "模板图"))
            if both or (not has_c1 and not has_c2):
                fails.append("L6 `场景方案` 值非法（value=%s）：①双图方案C+ / ②二合一方案C++ 必须二选一（互斥铁律）" % val)
        elif canonical == "C":
            if not any(k in val for k in ("看板", "md", "MD", "两者")):
                fails.append("L6 `C` 值非法（value=%s）：须含 看板/md/两者" % val)
        elif canonical == "D":
            if not re.search(r"[①②③④]", val) and not any(k in val for k in ("定格", "硬切", "空镜", "转场")):
                fails.append("L6 `D` 值非法（value=%s）：须为四选项之一" % val)
        elif canonical == "I":
            if not val:
                fails.append("L6 `I` 值为空：须写 影像基底 + 导演卡")
            elif not re.search(r"真人|3D|2D", val):
                warns.append("L6 `I` 未写影像基底（真人/3D/2D）——I 锁 Step1 必确认，建议补全")

    if not fails:
        passed.append("锁台账机检通过（%d 项锁 · 全部 src=user）" % len(need))
    return passed, fails, warns


def _self_test():
    filled = TEMPLATE.replace("YYYY-MM-DDTHH:MM", "2026-11-25T14:20")
    ok_text = "前文\n" + filled + "\n后文"
    bad_text = "前文\n" + filled.replace("src=user", "src=default", 1) + "\n后文"
    no_block = "# 立项包\n| 锁 | 值 |\n|---|---|\n| A 模型 | Seedance 2.5（默认） |"

    p1, f1, _ = audit_text(ok_text, multi_segment=True)
    p2, f2, _ = audit_text(bad_text, multi_segment=True)
    p3, f3, _ = audit_text(no_block, multi_segment=True)

    checks = [
        ("正常台账应 PASS", not f1),
        ("src=default 应 FAIL", bool(f2) and any("L3" in x for x in f2)),
        ("无台账块应 FAIL", bool(f3) and any("L1" in x for x in f3)),
    ]
    bad = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(("[+] " if ok else "[-] ") + name)
    if f2:
        print("    └ 捕获：" + f2[0][:110])
    return 0 if not bad else 1


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if "--format" in flags:
        print(TEMPLATE)
        return 0
    if "--self-test" in flags:
        return _self_test()
    if not args:
        print("[!] 用法：python check_locks.py <项目文件.md> [--multi-segment] [--self-test]")
        return 2

    path = args[0]
    if not os.path.exists(path):
        print("[!] 文件不存在：%s" % path)
        return 2
    text = open(path, encoding="utf-8").read()
    passed, fails, warns = audit_text(text, multi_segment="--multi-segment" in flags)

    for p in passed:
        print("[+] " + p)
    for w in warns:
        print("[~] " + w)
    for f in fails:
        print("[-] " + f)

    print("\n=== 锁凭证机检：%s ===" % os.path.basename(path))
    print("PASS %d · WARN %d · FAIL %d" % (len(passed), len(warns), len(fails)))
    if fails:
        print("[-] FAILED —— 锁未取得用户凭证，禁止进入 P1（写剧本）及之后任何阶段")
        return 1
    print("[+] PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
