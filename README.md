<div align="center">

# 🎬 漫剧老李 AIGC 全流程 Skill

## **V6.8 轻量版 (Lite)** · Short-Drama Director Suite

> ⚡ 抖音 & 红果爆款短剧/漫剧的 **工业化编剧与视听导演超级系统**
> 供 AI 助手 / LLM 直接调用的完整生产管线

![Version](https://img.shields.io/badge/版本-V6.8--轻量版-6a5acd)
![Modules](https://img.shields.io/badge/规则库-38%20模块-00b4d8)
![Files](https://img.shields.io/badge/文件-45-2ec4b6)
![Platform](https://img.shields.io/badge/平台-OpenClaw%20%7C%20Coze%20%7C%20Dify%20%7C%20WorkBuddy-ff6b6b)
![License](https://img.shields.io/badge/License-MIT-ffca3a)
![Stars](https://img.shields.io/github/stars/lixiaoxiao9888-create/manju-laoli-skill?style=social)

---

### 🎥 生产管线

```
📋 立项锁定 → ✍️ 门控编剧 → 🎙️ 台词诊断 → 🖼️ 资产锁定 → 🎬 文武分镜 → 🚀 提示词渲染 → ✅ 独立质检 → 🖥️ 离线看板
```

</div>

---

## 🔥 核心亮点

| 领域 | 能力 | 说明 |
|:---:|:---|:---|
| 🏗️ **管线** | Asset-First 六阶段 | P0~P5 唯一生产顺序，**资产图先于分镜**；资产依赖 A0~A3 分级按需触发 |
| 🖥️ **平台** | 多 Agent 适配 | OpenClaw / WorkBuddy / 豆包Coze / Dify + 豆包 JSON 分块 |
| 📐 **画幅** | 三选一强制锁 + 路由 | 16:9 / 9:16 / 21:9 与模型版本同规格前置锁定，全流程裁决，禁止默认 |
| ✍️ **编剧** | 五阶门控引擎 | Premise→Structure→Beat→Entity→Page，拒绝无大纲直奔台词 |
| 🎙️ **台词** | 七维诊断 + 语速自检 | 杜绝播音腔；三档语速/五步流程/拆镜 |
| 🖼️ **资产** | 4 View 资产板 + 台账 | 角色 4 View 资产板（五官 10 项 + 服装材质 6 项）+ A/B/C 分级锁 + CHR/AUD/PRP/SCN/Uxx 台账 + 亲缘遗传推导 |
| 😀 **表演** | FACS 微表情引擎 | 情绪 AU 化：四区拆解 + 强度三档 + 真假笑铁律 + 情绪→AU 配方库（增强模块·按需触发） |
| 📈 **情绪** | 12 节拍曲线 | 全片情绪张力量化 + 可视化绘图 |
| 🎬 **分镜** | 文武双模 | 文戏微表情递进 + 武戏 15s 完播率评分（R1/R2/R3 三档） |
| ⚔️ **武打** | 全流派武学库 | 23 门武学 + 9 套剑法 + 兵器 + 轻功 + 11 环杀招 |
| 🔮 **玄幻** | 法术战斗 R3 | 法宝/五行术法/术法攻防/能量具象/对军清场 |
| 🚀 **渲染** | Seedance 2.5 / 2.0 强制分流 | 七段式主格式；2.5 走官方声音字符 + Hit-Stop + **任务模式二选一**（全能参考 / 首尾帧） |
| 🎥 **空间** | 2x2 顶视图 + 站位分级 | CAM1~4 + 一行式【站位声明】；空间站位 S0~S4 分级按需加载 |
| 🖥️ **看板** | 轻量离线分镜看板 | md 唯一真相 → 单文件 HTML（双击即开，P2.5 出图词与 P4 投喂词必同板） |
| ✅ **质检** | 三级门禁 + 必查清单 | P0/P1/P2 独立门禁 + P4 投喂前六步执行序列 + 改动后三步复验 |
| 🛡️ **合规** | 安全转译词典 | 降低平台风险，不承诺 100% 通过 |

---

## ⚙️ 快速开始

```bash
# 安装到 OpenClaw
openclaw skills install ./short-drama-director --as short-drama-director

# 自检包完整性（38 模块静态 + 语义回归检查）
python3 short-drama-director/scripts/check_package.py

# 项目 md → 单文件离线看板
python3 short-drama-director/scripts/build_board_lite.py <项目.md>
```

完整规则与指令见 [`short-drama-director/SKILL.md`](short-drama-director/SKILL.md)

---

## 📦 项目结构

```
lixiaoxiao9888-create/manju-laoli-skill/
└── short-drama-director/              # V6.8 轻量版主包（45 文件）
    ├── SKILL.md                       # 路由 + 工作方法 + 模块索引
    ├── references/                    # 38 部专业规则库
    │   ├── asset-first-pipeline.md    #   Asset-First 六阶段（权威）
    │   ├── model-adapters.md          #   七段式主格式唯一权威定义
    │   ├── seedance-render-engine.md  #   时长预算 + 三层解耦
    │   ├── ★ facs-micro-expression.md #   FACS 微表情引擎（表情域权威）
    │   ├── storyboard-board-lite.md   #   轻量离线分镜看板规范
    │   ├── ★ prompt-feeding-checklist.md  # P4 投喂必查清单
    │   └── ... 共 38 模块
    ├── scripts/
    │   ├── check_package.py           # 静态 + 语义回归自检
    │   ├── build_board_lite.py        # 分镜看板编译器（md → 单文件 HTML）
    │   └── generate_emotion_curve.py  # 情绪曲线绘图
    └── README.md / LICENSE / CHANGELOG.md
```

---

## 📜 更新历史

- **V6.8 轻量版**（2026-09-15）— 去可灵正式支持（降级 LEGACY）/ 角色资产统一 **4 View** / 「七段式」命名统一 / 空间 S0~S4·资产 A0~A3·FACS **三级按需触发** / 提示词**末尾参数行废止** / 2.5 新增**任务模式二选一**（全能参考 · 首尾帧）
- **V6.7 轻量版**（2026-09-14）— 双锁同规格（模型版本 + 画幅三选一强制锁）/ 按官方文档校准 Seedance 2.5 / 吸收 FACS 微表情引擎三件套 / 吸收轻量离线分镜看板
- **V6.5 Multi-Agent**（2026-09-01）— Asset-First 六阶段 + 多 Agent 平台适配 + Seedance 2.5 深度适配 + 静止段禁用铁律（AI 视频无静止表演能力，情绪蓄力必须在运动中完成）
- **V6.0**（2026-08-28）— 23 references 模块重组 + 瘦身 + 审计修复
- **V5.0.2**（2026-08-27）— 武学招式库补全 + 打斗专项优先声明
- 旧版归档：[**manju-laoli-skill-legacy**](https://github.com/lixiaoxiao9888-create/manju-laoli-skill-legacy)

---

<div align="center">

---

# 🇬🇧 English Overview

## **V6.8 Lite** · Short-Drama Director Suite

**An industrial-grade screenwriting & audiovisual-directing system for viral short dramas / animated short dramas (Douyin & Hongguo), built for AI agents/LLMs to call directly.**

![Pipeline](https://img.shields.io/badge/Pipeline-Asset--First-6a5acd)
![Platforms](https://img.shields.io/badge/Platforms-OpenClaw%20%7C%20Coze%20%7C%20Dify%20%7C%20WorkBuddy-00b4d8)
![Seedance](https://img.shields.io/badge/Rendering-Seedance%202.5%20%2F%202.0-2ec4b6)
![QC](https://img.shields.io/badge/QC-P0%2FP1%2FP2-ff6b6b)

### 🎥 Production Pipeline

```
📋 Project Lock-in → ✍️ Gated Screenwriting → 🎙️ Dialogue Diagnosis → 🖼️ Asset Locking → 🎬 Dual-mode Storyboard → 🚀 Prompt Rendering → ✅ Independent QC → 🖥️ Offline Board
```

</div>

---

## 🔥 Feature Highlights

| Domain | Capability | Description |
|:---:|:---|:---|
| 🏗️ **Pipeline** | Asset-First 6-stage | P0–P5 single authoritative production order; **asset images precede storyboards**; A0–A3 dependency grading |
| 🖥️ **Platforms** | Multi-agent adapters | OpenClaw / WorkBuddy / Doubao Coze / Dify + Doubao JSON chunking |
| 📐 **Aspect Ratio** | Mandatory 3-way lock + routing | 16:9 / 9:16 / 21:9 locked alongside model version; no defaults allowed |
| ✍️ **Screenwriting** | 5-stage gated engine | Premise→Structure→Beat→Entity→Page; no dialogue without structure |
| 🎙️ **Dialogue** | 7-dimension diagnosis + speed check | No broadcast tone; 3 speed tiers / 5-step flow / shot splitting |
| 🖼️ **Assets** | 4-View sheets + ledger | Character 4-View sheets (10 facial + 6 material items) + A/B/C grading + CHR/AUD/PRP/SCN/Uxx ledger + lineage derivation |
| 😀 **Performance** | FACS micro-expression engine | Emotions as Action Units: 4-zone breakdown, 3 intensity tiers, real-vs-fake smile rule, emotion→AU recipes (on-demand module) |
| 📈 **Emotion** | 12-beat curve | Full-episode emotional intensity quantified + visual chart |
| 🎬 **Storyboard** | Dual-mode | Micro-expression progression (drama) + 15s action completion scoring (R1/R2/R3) |
| ⚔️ **Action** | Full martial-arts library | 23 schools + 9 sword forms + weapons + lightness skills + 11 finisher links |
| 🔮 **Fantasy** | Magic combat R3 | Artifacts / five-element spells / spell attack-defense / energy materialization / army-clearing |
| 🚀 **Rendering** | Seedance 2.5 / 2.0 forced split | 7-section main format; 2.5 uses official sound chars + Hit-Stop + **task-mode choice** (all-reference / first-last frame) |
| 🎥 **Space** | 2×2 top-view + stance grading | CAM1–4 + one-line stance declaration; S0–S4 space grading loaded on demand |
| 🖥️ **Board** | Lightweight offline storyboard board | md as single source → single-file HTML (double-click to open) |
| ✅ **QC** | 3-tier gates + checklist | P0/P1/P2 independent gates + P4 pre-feed 6-step sequence + 3-step post-edit re-verification |
| 🛡️ **Compliance** | Safety dictionary | Platform-risk reduction; no 100% pass guarantee |

---

## ⚙️ Quick Start

```bash
# Install into OpenClaw
openclaw skills install ./short-drama-director --as short-drama-director

# Lint package integrity (38-module static + semantic regression check)
python3 short-drama-director/scripts/check_package.py

# Project md → single-file offline board
python3 short-drama-director/scripts/build_board_lite.py <project.md>
```

Full rules & commands: [`short-drama-director/SKILL.md`](short-drama-director/SKILL.md)

---

## 📦 Structure

```
lixiaoxiao9888-create/manju-laoli-skill/
└── short-drama-director/              # V6.8 Lite main package (45 files)
    ├── SKILL.md                       # Router + working method + module index
    ├── references/                    # 38 professional rulebooks
    │   ├── asset-first-pipeline.md    #   Asset-First 6-stage (authoritative)
    │   ├── model-adapters.md          #   7-section format — single authority
    │   ├── seedance-render-engine.md  #   Duration budget + 3-layer decoupling
    │   ├── ★ facs-micro-expression.md #   FACS engine (expression authority)
    │   ├── storyboard-board-lite.md   #   Offline board spec
    │   ├── ★ prompt-feeding-checklist.md  # P4 pre-feed mandatory checklist
    │   └── ... 38 modules total
    ├── scripts/
    │   ├── check_package.py           # Static + semantic regression lint
    │   ├── build_board_lite.py        # Board compiler (md → single-file HTML)
    │   └── generate_emotion_curve.py  # Emotion curve chart
    └── README.md / LICENSE / CHANGELOG.md
```

---

## 📜 Changelog

- **V6.8 Lite** (2026-09-15) — Kling officially dropped (demoted to LEGACY) / character assets unified to **4 Views** / "7-section" naming unified / space S0–S4 · asset A0–A3 · FACS **three-level on-demand triggering** / end-of-prompt parameter line **abolished** / 2.5 gains **task-mode choice** (all-reference · first-last frame)
- **V6.7 Lite** (2026-09-14) — dual locks at equal weight (model version + 3-way aspect ratio) / Seedance 2.5 calibrated against official docs / FACS micro-expression engine absorbed / lightweight offline storyboard board absorbed
- **V6.5 Multi-Agent** (2026-09-01) — Asset-First 6-stage + multi-agent platform adapters + Seedance 2.5 deep adaptation + no-static-scene iron rule (AI video models cannot "act" while standing still; all emotion/charging must happen in motion)
- **V6.0** (2026-08-28) — 23-module reorganization + slimming + audit fixes
- **V5.0.2** (2026-08-27) — martial-arts library completion + combat-priority declaration
- Legacy archive: [**manju-laoli-skill-legacy**](https://github.com/lixiaoxiao9888-create/manju-laoli-skill-legacy)

---

<div align="center">

## 📄 License

**MIT** · For creative & learning use; comply with platform content policies

**Made with ❤️ for AI Content Creators**

</div>
