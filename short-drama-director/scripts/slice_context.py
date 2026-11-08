#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
slice_context.py · 动态原文切片器（Phase Context Slicer · 非手写摘要！）
设计动机：
  全包 140 份 Markdown 合计 2.46MB。若一次性塞进上下文，大模型必然发生「中间注意力坍塌（Lost in the Middle）」。
  而此前删除「运行态微核 agent-system-core.md」是因为手写摘要不随原文同步。
  本脚本直接从**权威原文**按「当前阶段 P0~P5 + 打戏档 R1~R3 + 模型版本 2.5/2.0 + 素材形态 M0~M2」
  动态解析必读文件，以完整章节分页输出原文与 coverage/未加载范围；不预填已读回执。
用法：
  python3 scripts/slice_context.py --stage P3 --combat R1 --model 2.5 --mode M1
  python3 scripts/slice_context.py --self-test
"""
import argparse
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
SUITE_DIR = os.path.dirname(BASE_DIR)

STAGE_FILES = {
    "P0": [
        "short-drama-director/references/asset-first-pipeline.md",
        "short-drama-director/references/asset-delivery-modes.md",
        "short-drama-director/references/aspect-ratio-adaptation.md",
        "sd-decision-engine/SKILL.md",
        "sd-decision-engine/references/context-mapping.md",
        "sd-decision-engine/references/emotion-anchor-table.md",
        "sd-decision-engine/references/forbidden-zone-whitelist.md",
    ],
    "P1": [
        "sd-script-engine/SKILL.md",
        "sd-script-engine/references/six-stage-pipeline.md",
        "sd-script-engine/references/dialogue-naturalization.md",
        "short-drama-director/references/dialogue-doctor-7d.md",
        "sd-script-engine/references/story-bible-and-ip.md",
        "sd-script-engine/references/episode-planning.md",
    ],
    "P2": [
        "sd-asset-engine/SKILL.md",
        "sd-asset-engine/references/three-list-extraction.md",
        "sd-asset-engine/references/scene-grid-template.md",
        "sd-asset-engine/references/character-portrait-templates.md",
        "sd-asset-engine/references/prop-template.md",
        "short-drama-director/references/asset-spatial-ledger.md",
        "short-drama-director/references/asset-delivery-modes.md",
    ],
    "P3": [
        "short-drama-director/references/acting-direction.md",
        "short-drama-director/references/blocking-direction.md",
        "sd-storyboard-engine/SKILL.md",
        "sd-storyboard-engine/references/short-drama-camera-system.md",
        "sd-storyboard-engine/references/shot-economy-and-acting.md",
        "sd-storyboard-engine/references/storyboard-sheet-template.md",
        "sd-storyboard-engine/references/plot-deduction-grid.md",
    ],
    "P4": [
        "sd-feed-engine/SKILL.md",
        "sd-feed-engine/references/feed-mode-and-gates.md",
        "sd-feed-engine/references/asset-mapping-and-rules.md",
        "short-drama-director/references/model-adapters.md",
        "short-drama-director/references/segment-splicing.md",
        "short-drama-director/references/prompt-feeding-checklist.md",
    ],
    "P5": [
        "sd-qc-engine/SKILL.md",
        "sd-qc-engine/references/machine-check-manual.md",
        "sd-qc-engine/references/continuity-ledger.md",
        "short-drama-director/references/quality-gate-review.md",
        "short-drama-director/references/storyboard-board-lite.md",
    ],
}

COMBAT_FILES = {
    "R1": [
        "sd-real-engine/SKILL.md",
        "sd-real-engine/references/r1-combat-core.md",
        "sd-real-engine/references/kinetic-chain-11.md",
        "sd-real-engine/references/defense-evasion-rules.md",
        "sd-real-engine/references/impact-physics.md",
        "sd-real-engine/references/camera-action-specs.md",
        "sd-real-engine/references/render-adapters.md",
    ],
    "R2": [
        "sd-combat-engine/SKILL.md",
        "sd-combat-engine/references/combat-iron-laws.md",
        "sd-combat-engine/references/combat-construction.md",
        "sd-combat-engine/references/eight-sentence-masters.md",
        "sd-combat-engine/references/combat-intensity-guardrails.md",
        "sd-combat-engine/references/combat-rhythm-and-load-guardrails.md",
        "sd-combat-engine/references/tier-and-finisher-system.md",
    ],
    "R3": [
        "sd-xuanhuan-engine/SKILL.md",
        "sd-xuanhuan-engine/references/core-combat-laws.md",
        "sd-xuanhuan-engine/references/xuanhuan-elements-vfx.md",
        "sd-xuanhuan-engine/references/grand-scale-domains.md",
        "sd-xuanhuan-engine/references/camera-specs-15modes.md",
        "sd-combat-engine/references/combat-intensity-guardrails.md",
        "sd-combat-engine/references/combat-rhythm-and-load-guardrails.md",
    ],
}


def resolve_files(stage, combat="none", model="2.5", source="1", previs=False):
    files = list(STAGE_FILES.get(stage.upper(), STAGE_FILES["P3"]))
    if source in ("3", "4") and stage.upper() in ("P0", "P1"):
        files.extend([
            "sd-recon-engine/SKILL.md",
            "sd-recon-engine/references/source-ladder.md",
            "sd-recon-engine/references/recon-evidence.md",
            "sd-recon-engine/references/intel-card.md",
        ])
    if stage.upper() in ("P3", "P4") and combat.upper() in COMBAT_FILES:
        files.extend(COMBAT_FILES[combat.upper()])
    if previs:
        files.append("sd-storyboard-engine/references/p45-previs-storyboard.md")
    # 去重保序
    seen = set()
    out = []
    for f in files:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def chapter_pages(raw_lines, line_budget=40):
    """按最外层正文标题分章；预算是软限，不拆章节、代码围栏或表格。"""
    if line_budget < 1:
        raise ValueError("--lines 必须为正整数")
    headings = []
    fence = None
    frontmatter = bool(raw_lines and raw_lines[0] == "---")
    for i, line in enumerate(raw_lines):
        if frontmatter:
            if i and line == "---":
                frontmatter = False
            continue
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            token, suffix = marker.groups()
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not suffix.strip():
                fence = None
            continue
        if fence is None:
            heading = re.match(r"^(#{1,6})\s+", line)
            if heading:
                headings.append((i, len(heading[1])))
    # 单一文档标题归入前言；多个一级标题则各自成章。
    if headings and headings[0][1] == 1 and sum(level == 1 for _, level in headings) == 1:
        headings = headings[1:]
    level = min((level for _, level in headings), default=0)
    starts = sorted({0, *(i for i, depth in headings if depth == level)})
    boundaries = starts + [len(raw_lines)]
    pages = []
    for start, end in zip(boundaries, boundaries[1:]):
        if start == end:
            continue
        if pages and end - pages[-1][0] <= line_budget:
            pages[-1] = (pages[-1][0], end)
        else:
            pages.append((start, end))
    return pages


def build_slice(stage, combat="none", model="2.5", mode="M1", max_lines_per_file=45,
                source="1", previs=False, page=1):
    if page < 1 or max_lines_per_file < 1:
        raise ValueError("--page 与 --lines 必须为正整数")
    files = resolve_files(stage, combat, model, source, previs)
    records = []
    for rel in files:
        full_p = os.path.join(SUITE_DIR, rel)
        if not os.path.isfile(full_p):
            records.append((rel, None, []))
            continue
        with open(full_p, encoding="utf-8") as handle:
            raw = handle.read().splitlines()
        records.append((rel, raw, chapter_pages(raw, max_lines_per_file)))
    page_count = max((len(pages) for _, _, pages in records), default=0)
    if page > max(1, page_count):
        raise ValueError(f"页码越界：本次路由共 {page_count} 页")
    lines = [
        f"# {stage.upper()} 阶段完整章节原文分页 · 第 {page}/{max(1, page_count)} 页",
        f"> 素材形态：{mode}；来源：{source}；预演：{'启用' if previs else '未启用'}",
        "> coverage 仅表示本次实际输出范围，不代表已读或已执行。未加载内容须续页读取。",
        "> 不记录历史阅读状态；前页也不自动算已读。回执须由执行者实际阅读后填写，不能直接粘贴为已读证明。",
        "",
        "## coverage / 未加载清单",
    ]
    bodies = []
    for rel, raw, pages in records:
        if raw is None:
            lines.append(f"- `{rel}`：coverage=0；缺失；未加载=全文（无法确定行数）")
            continue
        selected = pages[page - 1] if page <= len(pages) else None
        start, end = selected or (0, 0)
        unread = []
        if start:
            unread.append(f"L1-L{start}")
        if end < len(raw):
            unread.append(f"L{end + 1}-L{len(raw)}")
        span = f"L{start + 1}-L{end}" if selected else "无"
        lines.append(f"- `{rel}`：coverage={end - start}/{len(raw)} 行；本页范围={span}；"
                     f"文件页数={len(pages)}；未加载={'、'.join(unread) or '无'}")
        if selected:
            bodies.extend([f"\n## 原文 `{rel}` · {span}", *raw[start:end]])
    command = (f"python scripts/slice_context.py --stage {stage.upper()}"
               f" --combat {combat} --model {model} --mode {mode} --source {source}"
               f" --lines {max_lines_per_file}" + (" --previs" if previs else ""))
    lines.append(f"\n续页：`{command} --page {page + 1}`" if page < page_count
                 else "\n已到最后一页；这不代表此前页已读，按 --page N 回读未加载范围。")
    return "\n".join(lines + bodies)


# 各阶段「每集」经验产出字数（报账默认值 · 用户可用 --chars-per-episode 覆盖）
STAGE_OUTPUT_CHARS = {
    "P0": 2000,   # 立项基准表
    "P1": 4500,   # 一集剧本正文
    "P2": 6000,   # 一集所需资产提示词（角色/场景/道具）
    "P3": 12000,  # 一集分镜（镜数 × 每镜字段）
    "P4": 11000,  # 一集投喂稿（分组 + 七段式）
    "P5": 3000,   # 一集质检卡
}
BATCH_TOKEN_LIMIT = 8000  # 预算铁律第 3 条：单批输出上限


def estimate_tokens(text):
    """保守估算 token 数（不追求精确，只用于报账）：CJK ≈ 1.05 token/字，其余 ≈ 3.6 字符/token。"""
    cjk = 0
    for ch in text:
        o = ord(ch)
        if 0x4E00 <= o <= 0x9FFF or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF:
            cjk += 1
    return int(cjk * 1.05 + (len(text) - cjk) / 3.6)


def build_estimate(stage, combat="none", model="2.5", mode="M1",
                   lines=40, episodes=1, chars_per_episode=0, source="1", previs=False, page=1):
    """预算报账：输入侧真实占用 + 输出侧应切几批（预算铁律第 1 条）。"""
    files = resolve_files(stage, combat, model, source, previs)
    slice_tok = estimate_tokens(build_slice(stage, combat, model, mode, lines, source, previs, page))
    full_tok = 0
    for rel in files:
        fp = os.path.join(SUITE_DIR, rel)
        if os.path.isfile(fp):
            with open(fp, encoding="utf-8") as handle:
                full_tok += estimate_tokens(handle.read())

    stg = stage.upper()
    per_ep_chars = chars_per_episode or STAGE_OUTPUT_CHARS.get(stg, 6000)
    per_ep_tok = int(per_ep_chars * 1.05)
    per_ep_batches = max(1, -(-per_ep_tok // BATCH_TOKEN_LIMIT))
    total_tok = per_ep_tok * episodes
    total_batches = per_ep_batches * episodes
    hard_cut = max(1, -(-total_tok // BATCH_TOKEN_LIMIT))

    out = [
        "=" * 58,
        f"💰 预算报账 · {stg} 阶段（预算铁律第 1 条 · 禁止心算）",
        "=" * 58,
        f"必读权威文件      : {len(files)} 份（已按打戏档/模型/素材形态解析）",
        f"切片后输入        : ≈ {slice_tok:,} token   ← 当前页输出估算，不是全文已读证明",
        f"若通读本阶段全文  : ≈ {full_tok:,} token   ← 可分章节续页通读，仅作预算对照（{full_tok // max(slice_tok,1)}× 倍）",
        "",
        f"预计产出          : {episodes} 集 × {per_ep_chars:,} 字 = {episodes * per_ep_chars:,} 字"
        f" ≈ {total_tok:,} token",
        f"单批上限          : {BATCH_TOKEN_LIMIT:,} token（≈ {int(BATCH_TOKEN_LIMIT / 1.05):,} 汉字）",
        f"按 token 硬切      : {hard_cut} 批 ← ⛔ 仅参考，硬切会劈开整场戏",
        f"按结构切（推荐）   : 每集 ≈ {per_ep_tok:,} token → 每集拆 {per_ep_batches} 批"
        f" → 共 {total_batches} 批（集/场边界切）",
        "",
        "确认策略          : ① 自动续跑（默认，仅 P1/P2/P3/P4 阶段门停）",
        "                    ② 逐批确认（长剧集精修时选）",
        "                    强制停：超预算 1.5 倍 / 机检 FAIL / 需拍板岔路",
        "=" * 58,
    ]
    return "\n".join(out)


def self_test():
    for stg in ("P0", "P1", "P2", "P3", "P4", "P5"):
        out = build_slice(stg, combat="R1" if stg == "P3" else "none", max_lines_per_file=10)
        assert "coverage / 未加载清单" in out and "；缺失；" not in out, f"{stg} slice failed"
        assert "> 已读子库：" not in out, f"{stg} 虚假已读"
    est = build_estimate("P3", combat="R1", episodes=10)
    assert "预算报账" in est and "按结构切" in est, "estimate failed"
    print("[+] slice_context self-test PASSED（slice 6/6 + estimate 1/1）")
    return 0


def main():
    ap = argparse.ArgumentParser(description="漫剧老李 V7.5.0-SLIM 动态原文切片器")
    ap.add_argument("--stage", default="P3", choices=["P0", "P1", "P2", "P3", "P4", "P5", "p0", "p1", "p2", "p3", "p4", "p5"])
    ap.add_argument("--combat", default="none", choices=["none", "R1", "R2", "R3", "r1", "r2", "r3"])
    ap.add_argument("--model", default="2.5", choices=["2.5", "2.0"])
    ap.add_argument("--mode", default="M1", choices=["M0", "M1", "M2"])
    ap.add_argument("--lines", type=int, default=40, help="每文件每页软行数预算；完整章节可超限，不截断")
    ap.add_argument("--page", type=int, default=1, help="读取第 N 页；不自动累计已读状态")
    ap.add_argument("--source", default="1", choices=["1", "2", "3", "4"], help="素材来源锁")
    ap.add_argument("--previs", action="store_true", help="加载 P4.5 预演故事板权威原文")
    ap.add_argument("--estimate", action="store_true", help="预算报账模式：算输入占用与应切批数（预算铁律第 1 条）")
    ap.add_argument("--episodes", type=int, default=1, help="预计集数（配合 --estimate）")
    ap.add_argument("--chars-per-episode", type=int, default=0, help="每集预计产出字数（0=用阶段经验值）")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(self_test())
    if args.lines < 1 or args.page < 1 or args.episodes < 1 or args.chars_per_episode < 0:
        ap.error("lines/page/episodes 必须为正整数，chars-per-episode 不得为负")
    try:
        if args.estimate:
            print(build_estimate(args.stage, args.combat, args.model, args.mode,
                                 args.lines, args.episodes, args.chars_per_episode,
                                 args.source, args.previs, args.page))
        else:
            print(build_slice(args.stage, args.combat, args.model, args.mode,
                              args.lines, args.source, args.previs, args.page))
    except ValueError as exc:
        ap.error(str(exc))


if __name__ == "__main__":
    main()
