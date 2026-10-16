#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_contract.py — 漫剧老李 Short-Drama Director Suite 全流程交付契约与权威源核销器 (V7.4.20)

专治外部 Agent 三大通病（2026-10-14 实测根因封堵）：
  1. 「拿 validate_prompt.py 机检全绿当任务完成」——只写 P4 投喂稿，漏掉 P0B 情绪锚点表、P1 表演档案/世界锚/人物锚、P3 场面调度/故事板图、P5 连续性台账/素材接线单；
  2. 「按当下最小口径糊弄过关，不按权威源落字」——P2/P2.5 资产提示词写成几行简笔摘要（未回角色四字段模板 / 场景母版+九宫格 8 字段 / 道具模板），I 锁美学短语凭常识手搓（未回 style-bible 取 72 卡正主短语与 11 槽位）；
  3. 「你抓一次我修一次，挤牙膏式被动返工」——开工前不建契约清单，交付前不逐项核销。

修复记录（2026-10-14 · 实测《北境隐王》回归发现）：
  • P1：auto 模式误判——满配档案含 P2.5 即被降级 board-lite，静默跳过 CT1/CT4/CT6-LED 六项；改为先探满配阶段标记，无标记才降级。
  • P2：指纹匹配空白归一化——「3×3 九宫格」「45° 侧视图」「Voice Description」等空格/大小写变体不再误杀；CT6-WIR 放宽「只控制什么」为「控制什么+不控制什么」等价变体。

用法：
  1. 开工前生成《交付契约核销表》（含每阶段硬产出 + 权威源文件路径 + 必现结构指纹 + 指定导演卡正主短语）：
     python3 short-drama-director/scripts/audit_contract.py --init [--mode full|board-lite] [--director 07|路阳|33|朴赞郁]
  2. 交付前对稿件执行全流程契约与权威源指纹审计（未通过严禁宣布「任务完成」）：
     python3 short-drama-director/scripts/audit_contract.py <稿件.md> [--mode auto|full|board-lite] [--director 07|路阳]
  3. 自测：
     python3 short-drama-director/scripts/audit_contract.py --self-test
"""

import argparse
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
SUITE_DIR = os.path.dirname(BASE_DIR)

# 10 张满配主力导演卡正主短语与关键指纹（与 style-bible/director-param-library.md & style-prefix-blocks.md 同源）
CANONICAL_DIRECTOR_CARDS = {
    "01": {"name": "张艺谋", "keywords": ("浓烈色块", "高饱和", "仪式对称", "大远景", "1:8", "冷暖对冲")},
    "03": {"name": "王家卫", "keywords": ("霓虹", "抽帧", "前景遮挡", "浅景深", "1:6", "暗绿", "暖黄")},
    "04": {"name": "徐克", "keywords": ("广角", "斜角", "高速", "急推", "1:8", "冷青", "16mm", "18mm")},
    "06": {"name": "乌尔善", "keywords": ("神话", "重工业", "金青", "火光", "1:8", "图腾", "厚重")},
    "07": {"name": "路阳", "keywords": ("冷青", "暖橙", "烛火", "火折", "浅景深", "1:8", "1:10", "硬切", "冷峻")},
    "12": {"name": "袁和平", "keywords": ("硬桥硬马", "中景", "全景", "拳脚", "力道", "竹林", "青灰")},
    "33": {"name": "朴赞郁", "keywords": ("幽绿", "暗红", "对称", "俯拍", "折磨", "冷冽", "1:8", "1:10", "高反差")},
    "39": {"name": "大卫·芬奇", "keywords": ("冷黄绿", "青灰", "阴郁", "机械", "定焦", "1:6", "1:8", "精准")},
    "52": {"name": "罗杰·狄金斯", "keywords": ("单源", "实用光", "剪影", "冷青灰", "阴影侧", "1:6", "1:8", "35~85mm")},
    "64": {"name": "MAPPA", "keywords": ("高对比", "粗黑边", "速度线", "冲击帧", "广角透视", "粒子")},
    "65": {"name": "国漫3D仙侠", "keywords": ("国漫3D", "半写实", "PBR", "丝绸", "丁达尔", "流光剑气")},
    "66": {"name": "暗黑神话游戏CG", "keywords": ("虚幻5", "游戏CG", "PBR", "甲胄", "暗黑", "丁达尔")},
    "71": {"name": "国漫3D进阶水墨", "keywords": ("三渲二", "水墨", "枯笔", "飞白", "墨韵", "朱砂")},
    "72": {"name": "东方神话3D奇幻", "keywords": ("东方神话", "3D", "次表面散射", "青绿", "赤金", "法相")},
}

CONTRACT_ITEMS_FULL = [
    ("CT1-P0A", "P0A 前置六道锁基准表", "short-drama-director/SKILL.md §〇",
     "含 〇·0 赛道 / 〇·1 素材来源 / A 模型 / B 画幅 / C 交付 / D 段缝 / I 画风锁 / M 素材形态"),
    ("CT1-P0B", "P0B 导演决策《情绪锚点表》", "sd-decision-engine/references/emotion-anchor-table.md + forbidden-zone-whitelist.md",
     "含 情境 ID (E01~E15) + 80/15/5 机位组合锁 + 构图雷区 A 类解锁 / B 类规避"),
    ("CT1-P1A", "P1 《世界锚卡》与《人物锚卡》", "sd-script-engine/references/story-bible-and-ip.md §1.11",
     "世界锚卡含年代/地域/禁用与必现元素；人物锚卡含年龄锚 + 体型锚(身高/头身比) + 身份外观三件套 + 反漂移清单"),
    ("CT1-P1B", "P1 《因果与关系表》与《称呼账本》", "sd-script-engine/references/dialogue-naturalization.md",
     "因果表每场必写明确「溃败方」（公理7）；称呼账本含前态/后态/禁称"),
    ("CT1-P1C", "P1/P3 《角色表演主档案》", "short-drama-director/references/acting-direction.md",
     "每位主要角色一份：含内在驱动引擎 + Voice Lock 英文声线标签 + 习惯动作账本 + 眼神生命 + 「然而，当…」破功句"),
    ("CT2-P2L", "P2 资产三清单与状态汇总表", "sd-asset-engine/references/three-list-extraction.md",
     "文档A 角色清单 / 文档B 道具清单 / 文档C 场景清单 + Step 3.5 素材清单状态汇总表"),
    ("CT2-CHR", "P2 角色独立建档与四字段提示词（防简笔糊弄）", "short-drama-director/references/character-extraction.md + asset-spatial-ledger.md",
     "角色身份与出场证据可追溯；角色提示词采用画幅/排版结构/服装与身体材质/面部特写四字段；五官10项与服装6项写入描述；不要求亲缘推导、声纹图或音色标签"),
    ("CT2-SCN", "P2 场景母版 + 3×3 九宫格 8 字段提示词（防简笔糊弄）", "sd-asset-engine/references/scene-grid-template.md + asset-spatial-ledger.md §四",
     "必含：场景空间事实五件事(坐标系/SET_STATE/空气介质/尺度/年代锚) + ① 16:9 无人场景母版 + ② 3×3 九宫格完整 8 字段(含摄影机矩阵与标注降级条款)"),
    ("CT2-PRP", "P2 道具四格设定图提示词（防简笔糊弄）", "sd-asset-engine/references/prop-template.md",
     "每个核心道具必含：全图共 4 格(①正面/②45°侧视/③顶部俯视/④细节特写) + 禁止出现手/人物剪影 + negative prompt"),
    ("CT3-STY", "I 锁画风正主出处核验（防常识手搓假短语）", "short-drama-director/references/style-bible/director-param-library.md + style-prefix-blocks.md",
     "选定导演卡时必须原样提取 style-bible 对应卡号的正主美学短语与 11 槽位段8/段9，严禁凭印象手搓近似词"),
    ("CT4-BLK", "P3 场面调度层（坐标系·权力几何·道具台账）", "short-drama-director/references/blocking-direction.md",
     "含全场唯一空间坐标系文字平面图 + 各段初始位与位移增量 + 权力几何演进表 + 关键道具持有/手位/落点台账"),
    ("CT4-SBD", "P3 九字段分镜与故事板图 CLEAN_GRID + 图形化交付清单", "sd-storyboard-engine/SKILL.md §五 + storyboard-sheet-template.md",
     "逐镜九字段标准分镜 + 每段一张故事板图 CLEAN_GRID(文戏2×2四宫格/打戏2×3六宫格，面板1~4/6) + P3 图形化交付清单"),
    ("CT5-P4F", "P4 相邻段边界推荐表 + 七段式投喂词 + 外挂回执头", "short-drama-director/references/segment-splicing.md + model-adapters.md §5",
     "顶部三行【外挂激活回执头】+ 相邻段边界推荐表(含段缝景别差) + N 组完整七段式投喂词"),
    ("CT6-P5Q", "P5 《素材接线单》+ 机检报告 + 《跨镜连续性台账》", "short-drama-director/references/asset-delivery-modes.md + sd-qc-engine/references/continuity-ledger.md",
     "M1 必附《素材接线单》(含只控制什么/不控制什么) + 双门机检结果 + 逐段《跨镜连续性台账》(SET_STATE/CHAR_STATE/出口帧)"),
]


def print_init_checklist(mode="full", director=None):
    print("# 📋 Short-Drama Director 全流程交付契约核销表（开工必建 · 交付必核）")
    print("")
    print("> **铁律**：`validate_prompt.py` 报 `PASSED` 只代表「P4 投喂块语法合格」，**绝不代表全流程交付完成**！")
    print("> 开工前必须先建本表；每写完一节必须回对照「权威源文件路径」与「必现结构指纹」打 `[x]`；")
    print("> 交付前必须跑 `python3 short-drama-director/scripts/audit_contract.py <稿件.md>` 全绿放行。")
    print("")
    print("| 状态 | 契约码 | 阶段交付物 | 唯一权威源文件（必须回读，禁凭印象手搓） | 必现结构指纹（机检核销项） |")
    print("| :--- | :--- | :--- | :--- | :--- |")
    for code, title, ref_path, fp in CONTRACT_ITEMS_FULL:
        if mode == "board-lite" and code in ("CT1-P0B", "CT1-P1B", "CT4-BLK"):
            continue
        print(f"| `[ ]` | `{code}` | **{title}** | `{ref_path}` | {fp} |")
    if director:
        print("\n## 🎨 指定导演卡正主参数提取指引（严禁凭常识手搓）")
        d_key = str(director).strip().zfill(2) if str(director).strip().isdigit() else str(director).strip()
        matched = None
        for k, v in CANONICAL_DIRECTOR_CARDS.items():
            if d_key == k or d_key in v["name"] or v["name"] in d_key:
                matched = (k, v)
                break
        if matched:
            k, v = matched
            print(f"- **锁定卡号**：`{k} {v['name']}`")
            print(f"- **权威源位置**：`short-drama-director/references/style-bible/director-param-library.md` + `style-prefix-blocks.md`")
            print(f"- **必现正主指纹词**：`{' / '.join(v['keywords'])}`")
            print(f"- **自动提取命令**：`python3 short-drama-director/scripts/style-lock-ladder.py --card {k}`")
        else:
            print(f"- 请运行 `python3 short-drama-director/scripts/style-lock-recommend.py` 或查阅 `director-style-catalog-74.md` 提取 `{director}` 的正主槽位。")


def audit_markdown(text, mode="auto", director=None):
    issues = []
    warns = []
    passed = []

    if mode == "auto":
        # Detect whether this is a board-lite single-file doc or a full production archive
        # 2026-10-14 修复（P1 级 · 实测《北境隐王》回归发现）：满配生产档案同样含 P2.5——
        # 旧逻辑「见 P2.5 即 board-lite」会静默跳过 CT1-P0B/P1A/P1B/P1C、CT4-BLK/SBD、CT6-LED 六项，
        # 恰好放走「漏 P1/P3/P5」这类最典型的漏项。改为：检出任一满配阶段标记即按 full 审计，
        # 仅当全文缺失所有满配标记且含 P2.5/看板标记时才降级 board-lite（宁可多查，不可静默漏查）。
        _full_markers = (
            "世界锚卡", "人物锚卡", "表演主档案", "故事板图",
            "连续性台账", "场面调度", "空间坐标系", "场景坐标系",
        )
        _has_full_marker = any(m in text for m in _full_markers) or bool(
            re.search(r"^##\s*P[135]\b", text, re.M) or re.search(r"^###\s*P3-", text, re.M)
        )
        if not _has_full_marker and ("P2.5" in text or ("导演参考块" in text and "【时间轴分镜】" in text)):
            mode = "board-lite"
        else:
            mode = "full"

    # 1. CT1: P0 & P1 anchors and acting profiles
    if mode == "full":
        if "情绪锚点表" in text and re.search(r"E0[1-9]|E1[0-5]", text) and "80%" in text:
            passed.append("CT1-P0B P0B《情绪锚点表》（含情境ID与80/15/5机位锁）在位")
        else:
            issues.append("CT1-P0B 缺失 P0B《情绪锚点表》（须含情境 ID E01~E15 与 80/15/5 机位锁，权威见 sd-decision-engine）")

        if "世界锚卡" in text and "人物锚卡" in text and "身份外观三件套" in text:
            passed.append("CT1-P1A P1《世界锚卡》与《人物锚卡》（含身份外观三件套）在位")
        else:
            issues.append("CT1-P1A 缺失 P1《世界锚卡》或《人物锚卡》（须含年龄锚/体型锚/身份外观三件套，权威见 story-bible-and-ip.md §1.11）")

        if ("角色表演" in text or "表演主档案" in text or "表演档案" in text) and "然而，当" in text:
            passed.append("CT1-P1C 《角色表演主档案》（含 Voice 声线锁与「然而，当…」破功句）在位")
        else:
            issues.append("CT1-P1C 缺失《角色表演主档案》或漏写「然而，当…」破功句（权威见 acting-direction.md）")

    # 2. CT2: P2 / P2.5 Asset Prompts — strictly block sketchy 1-line summaries!
    # 2026-10-14 修复（P2 级）：指纹匹配统一做空白归一化（_tn=去全半角空白 / _tnl=再转小写），
    # 「全图共 4 格 / 3×3 九宫格 / 45° 侧视图 / Voice Description」等空格与大小写变体不再误杀，
    # 与 CHR 检查原有的双变体口径对齐（SCN/PRP 此前只认单一带空格写法，口径不一）。
    _tn = re.sub(r"[\s\u3000]+", "", text)
    _tnl = _tn.lower()
    has_chr_template = all(x in _tn for x in ("画幅", "排版结构", "服装与身体材质", "面部特写")) and "五官10项" in _tn
    if has_chr_template:
        passed.append("CT2-CHR 角色提示词采用四字段模板（含五官10项描述）")
    else:
        issues.append(
            "CT2-CHR 角色资产提示词未按当前四字段模板展开——须包含「画幅、排版结构、服装与身体材质、面部特写」，并将五官10项写入描述；"
            "不得把亲缘推导、四格板、声纹图或音色标签列为必需项。权威见 asset-spatial-ledger.md 与 character-extraction.md"
        )

    has_scn_template = (
        ("场景母版" in _tn or "无人空镜基准图" in _tn)
        and ("九宫格摄影机矩阵" in _tn or ("3×3九宫格" in _tn and "参考场景锁定模式" in _tn))
        and ("标注降级条款" in _tn or "画面纯净要求" in _tn)
    )
    if has_scn_template:
        passed.append("CT2-SCN 场景母版 + 3×3 九宫格 8 字段提示词已按权威模板展开")
    else:
        issues.append(
            "CT2-SCN 场景资产提示词未按权威模板展开（疑似简笔糊弄版！）——必须回读 "
            "`sd-asset-engine/references/scene-grid-template.md` 与 `asset-spatial-ledger.md §四`，"
            "同时产出「① 16:9 无人场景母版」与「② 3×3 九宫格完整 8 字段（含【九宫格摄影机矩阵】、【参考场景锁定模式】、标注降级条款）」"
        )

    has_prp_template = (
        ("道具设定图" in _tn or "道具提示词" in _tn)
        and ("正面视图" in _tn and "45°侧视图" in _tn and "俯视图" in _tn)
        and ("禁止手持" in _tn or "不出现人物、人手" in _tn)
    )
    if has_prp_template:
        passed.append("CT2-PRP 道具四格设定图提示词已按权威模板展开")
    else:
        issues.append(
            "CT2-PRP 道具资产提示词未按权威模板展开（疑似简笔糊弄版或缺失！）——必须回读 "
            "`sd-asset-engine/references/prop-template.md`，写出「全图共 4 格（①正面视图/②45°侧视图/③顶部俯视图/④关键细节特写）+ 禁止手持展示 + negative prompt」"
        )

    # 3. CT3: Style-Bible canonical verification
    detected_card = director
    if not detected_card:
        m_card = re.search(r"(?:导演卡|风格卡|I\s*锁)[^\n]{0,30}?\b(0[13467]|12|33|39|52|64)\b", text)
        if m_card:
            detected_card = m_card.group(1)
        else:
            for k, v in CANONICAL_DIRECTOR_CARDS.items():
                if v["name"] in text:
                    detected_card = k
                    break
    if detected_card:
        d_key = str(detected_card).strip().zfill(2) if str(detected_card).strip().isdigit() else str(detected_card).strip()
        for k, v in CANONICAL_DIRECTOR_CARDS.items():
            if d_key == k or d_key in v["name"] or v["name"] in d_key:
                hits = [kw for kw in v["keywords"] if kw in text]
                if len(hits) >= 2:
                    passed.append(f"CT3-STY I 锁画风已对齐 style-bible [{k} {v['name']}] 正主槽位词 {hits[:4]}")
                else:
                    issues.append(
                        f"CT3-STY I 锁画风疑似手搓近似词：检测到导演卡 [{k} {v['name']}]，但正文未命中 style-bible 正主槽位指纹词 "
                        f"{v['keywords']}（仅命中 {hits}）——严禁凭常识手搓风格词，必须从 `director-param-library.md` / `style-prefix-blocks.md` 取正主！"
                    )
                break

    # 4. CT4: P3 Blocking, Storyboard Sheet CLEAN_GRID & Graphical Delivery Checklist
    if mode == "full":
        if ("场景坐标系" in text or "空间坐标系" in text) and "权力几何" in text:
            passed.append("CT4-BLK P3 场面调度层（空间坐标系 + 权力几何）在位")
        else:
            issues.append("CT4-BLK 缺失 P3 场面调度层（须含空间坐标系文字平面图与权力几何演进表，权威见 blocking-direction.md）")

        if "故事板图" in text and "面板 1" in text and "图形化交付清单" in text:
            passed.append("CT4-SBD P3 故事板图 CLEAN_GRID 与《P3 图形化交付清单》在位")
        else:
            issues.append(
                "CT4-SBD 缺失 P3《故事板图 CLEAN_GRID》（每段一张，含面板 1~4/6 相位拆解）或《P3 图形化交付清单》"
                "（权威见 sd-storyboard-engine/references/storyboard-sheet-template.md）"
            )

    # 5. CT5: P4 Feed blocks & segment boundary table
    if "【时间轴分镜】" in text and "【站位声明】" in text:
        passed.append("CT5-P4F P4 七段式投喂提示词主体在位")
    else:
        issues.append("CT5-P4F 缺失 P4 七段式投喂提示词主体")

    # 6. CT6: P5 M1 Wiring Table & Continuity Ledger
    # 2026-10-14 修复（P2 级）：「只控制什么」放宽为「控制什么+不控制什么」等价变体
    # （「只控制什么」是「控制什么」的超集串，权威正主写法仍优先命中，不再因少一个「只」字误杀）。
    if "素材接线单" in text and "控制什么" in text and "不控制什么" in text:
        passed.append("CT6-WIR M1《素材接线单》（含只控制什么/不控制什么）在位")
    elif "M0" not in text[:400]:
        issues.append("CT6-WIR 缺失 M1《素材接线单》（须含图号、引用段落、只控制什么、不控制什么，权威见 asset-delivery-modes.md）")

    if mode == "full":
        if ("连续性台账" in text or "Continuity Ledger" in text) and "SET_STATE" in text:
            passed.append("CT6-LED P5《跨镜连续性台账（Continuity Ledger）》在位")
        else:
            issues.append("CT6-LED 缺失 P5《跨镜连续性台账（Continuity Ledger）》（须逐段登记 SET_STATE / CHAR_STATE / 道具落点 / 出口帧，权威见 continuity-ledger.md）")

    return issues, warns, passed


def _self_test():
    # 1. Verify init checklist generation works
    from io import StringIO
    old_stdout = sys.stdout
    buf = StringIO()
    sys.stdout = buf
    try:
        print_init_checklist("full", "33")
    finally:
        sys.stdout = old_stdout
    out = buf.getvalue()
    assert "CT2-CHR" in out and "朴赞郁" in out, "init checklist self-test failed"

    # 2. Verify full compliant sample passes 0 issues
    compliant_sample = (
        "素材形态：M1\n情绪锚点表 E04 80%\n世界锚卡 人物锚卡 身份外观三件套\n"
        "角色表演主档案 然而，当\n"
        "画幅 排版结构 服装与身体材质 面部特写 五官10项 服装6项\n"
        "场景母版 九宫格摄影机矩阵 3×3 九宫格 参考场景锁定模式 标注降级条款\n"
        "道具设定图 正面视图 45° 侧视图 俯视图 禁止手持\n"
        "场景坐标系 权力几何 故事板图 面板 1 图形化交付清单\n"
        "【站位声明】 【时间轴分镜】\n"
        "素材接线单 只控制什么 不控制什么 连续性台账 SET_STATE\n"
    )
    iss, _, pas = audit_markdown(compliant_sample, mode="full")
    assert not iss and len(pas) >= 8, f"compliant sample should pass, got {iss}"

    # 3. Verify sketchy / incomplete sample is caught on CT1, CT2, CT3, CT4, CT6
    sketchy_sample = (
        "# 某剧分镜看板\n"
        "导演卡：33 朴赞郁（高对比冷蓝深红）\n"
        "## P2.5 资产提示词\n- 霍擎：50岁，穿绯袍。\n"
        "【站位声明】@霍擎（画面左）\n【时间轴分镜】\n"
    )
    iss2, _, _ = audit_markdown(sketchy_sample, mode="full", director="33")
    codes = " ".join(iss2)
    for req_code in ("CT1-P0B", "CT2-CHR", "CT2-SCN", "CT2-PRP", "CT3-STY", "CT4-SBD", "CT6-WIR", "CT6-LED"):
        assert req_code in codes, f"sketchy sample should trigger {req_code}, got {iss2}"

    print("[+] audit_contract.py self-test PASSED")
    return 0


def main():
    ap = argparse.ArgumentParser(description="全流程交付契约与权威源核销器")
    ap.add_argument("file", nargs="?", help="待核销的 Markdown 稿件路径")
    ap.add_argument("--init", action="store_true", help="开工前输出《全流程交付契约核销表》")
    ap.add_argument("--mode", default="auto", choices=["auto", "full", "board-lite"], help="交付模式")
    ap.add_argument("--director", default=None, help="锁定的导演卡编号或姓名（如 07 / 路阳 / 33 / 朴赞郁）")
    ap.add_argument("--self-test", action="store_true", help="运行内置自测")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(_self_test())

    if args.init or not args.file:
        print_init_checklist(mode="full" if args.mode == "auto" else args.mode, director=args.director)
        sys.exit(0)

    if not os.path.isfile(args.file):
        print(f"[-] 文件不存在: {args.file}", file=sys.stderr)
        sys.exit(2)

    with open(args.file, "r", encoding="utf-8") as f:
        txt = f.read()

    issues, warns, passed = audit_markdown(txt, mode=args.mode, director=args.director)
    print(f"=== 📋 全流程交付契约核销报告 ({os.path.basename(args.file)} | mode={args.mode}) ===")
    for p in passed:
        print(f"  [PASS] {p}")
    for w in warns:
        print(f"  [WARN] {w}")
    for i in issues:
        print(f"  [FAIL] {i}")
    if issues:
        print(f"\n[-] 交付契约未通过：共 {len(issues)} 项契约/权威源缺失！严禁把 validate_prompt 格式全绿当成任务完成！")
        sys.exit(1)
    print(f"\n[+] 交付契约全项核销通过（共 {len(passed)} 项硬产出与权威模板指纹全部在位）")
    sys.exit(0)


if __name__ == "__main__":
    main()
