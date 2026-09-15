<div align="center">

# 🎬 漫剧老李 AIGC 创作全流程 Skill

## **V6.8 轻量版** · Short-Drama Director Suite

> 🎨 面向 **AIGC 视听创作** 的工业化全流程技能包
> 从创意立项到视频模型投喂提示词 —— 给 AI 助手 / LLM 直接调用

![Version](https://img.shields.io/badge/版本-V6.8--轻量版-6a5acd)
![Modules](https://img.shields.io/badge/规则库-38%20模块-00b4d8)
![Files](https://img.shields.io/badge/文件-45-2ec4b6)
![Models](https://img.shields.io/badge/模型-Seedance%202.5%20%7C%202.0-9d4edd)
![Platform](https://img.shields.io/badge/平台-OpenClaw%20%7C%20Coze%20%7C%20Dify%20%7C%20WorkBuddy-ff6b6b)
![License](https://img.shields.io/badge/License-MIT-ffca3a)
![Stars](https://img.shields.io/github/stars/lixiaoxiao9888-create/manju-laoli-skill?style=social)

---

### 🎥 生产管线

```
📋 立项锁定 → ✍️ 门控编剧 → 🎙️ 台词诊断 → 🖼️ 资产锁定 → 🎬 文武双模分镜 → 🚀 提示词封装 → ✅ 独立质检 → 🖥️ 离线看板
```

</div>

---

## 🧭 这是什么

一套 **给 AI 助手执行的 AIGC 创作规则库**（OpenClaw Skill / Agent 技能包），不是面向消费者的成品剧本——把 `SKILL.md` 与 `references/` 放进 Agent 技能目录即可调用。

它把「AIGC 视听创作」拆成一条可复用的工业化管线，核心解决三件事：

1. **不漂移** —— 角色 / 场景 / 道具**先出图锁定**，再进分镜（Asset-First：**资产图先于分镜**），跨镜跨集一致性有据可依；
2. **不返工** —— 前置强制锁定（模型版本 / 画幅）+ 投喂前必查清单 + P0~P2 独立门禁，把错误拦在生成之前；
3. **能直接投喂** —— 输出**七段式**结构化提示词，整组复制即可喂给视频模型，不需要二次翻译。

## 🎯 适用场景

管线与题材解耦，凡「**剧本 → 分镜 → 视频模型投喂**」的 AIGC 创作都可套用：

- **AI 短剧 / 漫剧 / 短视频剧集**（本包最典型的高密度场景）
- **AI 广告片 / 品牌宣传片 / 概念片**
- **分镜预演（PREVIS）与动态分镜**
- **武打 / 动作场面设计**（现代格斗、武侠、仙侠、二次元、科幻）
- **情绪戏 / 微表情专项**（FACS 表情工程）
- 任何需要**跨镜头角色一致性**的 AI 视频生产

> 题材覆盖：现代都市 / 古装武侠 / 玄幻仙侠 / 悬疑 / 科幻 / 赛博 / 水墨国漫 —— 含六大电影级视听美学预设（诗意 / 纪实 / 港派 / 赛博 / 水墨 / 国漫）。

## 🔥 核心能力

| 阶段 | 能力 | 说明 |
|:---:|:---|:---|
| 📋 **立项** | 前置强制锁定 | 模型版本（Seedance 2.5 / 2.0 **强制二选一**）+ 画幅（16:9 / 9:16 / 21:9 **三选一**）——未指定不动笔，禁止默认 |
| ✍️ **剧本** | 五阶门控引擎 | Premise → Structure → Beat → Entity → Page；含三幕结构、因果节拍表与专业剧本页排版 |
| 📈 **情绪** | 12 节拍曲线 | 全片张力 0~10 量化 + 折线图脚本；波峰/波谷与第 9 节拍反杀峰值校验 |
| 🎙️ **台词** | 七维诊断 + 语速自检 | 三维语速档（3.5~5 字/秒基准）、超长句拆镜、金句发酵气口、三段式重构 |
| 🖼️ **资产** | Asset-First 数字资产包 | 角色 **4 View 资产板**（五官 10 项 + 服装材质 6 项）/ 场景空间图 / 道具图；《资产图册》CHR/AUD/PRP/SCN/Uxx 台账；A/B/C 分级、依赖 A0~A3 按需触发 |
| 🎥 **空间** | 一行式站位 + 分级 | 【站位声明】四要素（位置/依托物/朝向/姿态）+ 轴线锁 + 位移链；空间 S0~S4 分级；180° 轴线 |
| 🎬 **分镜** | 文武双模 | 文戏微表情六阶段递进 / 武戏 15 秒 PREVIS 完播评分（R1 写实 · R2 商业高燃 · R3 玄幻）；镜头规格 15 铁律 + 三手法六式衔接 |
| 😀 **表演** | FACS 微表情引擎 | 情绪 AU 化：四区拆解 + 强度三档 + 真假笑铁律 + 情绪→AU 配方库与 AU 字典（增强模块 · 按需触发） |
| ⚔️ **资料库** | 武学 / 玄幻 | 23 门武学 + 9 套剑法 + 兵器 + 轻功 + 11 环杀招；玄幻法术 R3（法宝 / 五行术法 / 能量具象 / 对军清场） |
| 🚀 **提示词** | 七段式主格式 | 【画幅风格】→【场景资产】→【核心人物】→【站位声明】→【时间轴分镜】→【音效】→【强制禁止项】；2.5 走官方声音字符（`<>` `{}` `()` `【】`）+ Hit-Stop 顿挫 + **任务模式二选一**（全能参考 / 首尾帧） |
| ✅ **质检** | P0~P2 独立门禁 | 时长 / 台词 / 跳轴 / 画幅 / 资产锚点一致性 + 声音三层相对电平 + **改动后三步复验铁律** |
| 🖥️ **看板** | 离线分镜看板 | 项目 md（唯一真相）→ 单文件 HTML，双击即开；P2.5 出图词与 P4 投喂词必同板 |
| 🛡️ **合规** | 安全转译词典 | 把血腥/断肢类动作转译为「气浪震散 / 火花消散 / 重创定格」，降低平台风险（不承诺 100% 通过） |

## 🖥️ 适用平台与模型

| | 支持 |
|---|---|
| **Agent 平台** | OpenClaw · WorkBuddy · 豆包智能体 / 扣子(Coze) · Dify 及通用 LLM（支持豆包 JSON 分块，防上下文截断） |
| **视频模型** | **Seedance 2.5 / 2.0**（强制二选一，语法契约彻底分流）；即梦为次选 / 历史兼容；可灵自 V6.8 起移出正式支持（LEGACY） |
| **输出** | 七段式投喂提示词组 · Canvas / API 结构化载荷 · 单文件离线分镜看板 · 情绪曲线图 |

---

## ⚙️ 快速开始

```bash
# 安装到 OpenClaw
openclaw skills install ./short-drama-director --as short-drama-director

# 自检包完整性（38 模块静态 + 语义回归检查）
python3 short-drama-director/scripts/check_package.py

# 项目 md → 单文件离线看板
python3 short-drama-director/scripts/build_board_lite.py <项目.md>

# 12 节拍情绪曲线
python3 short-drama-director/scripts/generate_emotion_curve.py
```

**给 AI 助手的最小执行序列**：读 `SKILL.md` → 完成 A/B 双锁 → 定动作强度档（R1/R2/R3）→ 有对白先过语速自检 → 资产出图锁定 → 分镜 → 按 `★ prompt-feeding-checklist.md` 生成投喂词 → 过 `quality-gate-review`

### 🧮 常用指令

`/写剧本` · `/拆资产` · `/资产图册` · `/角色资产板` · `/顶视图` · `/做分镜` · `/台词诊断` · `/语速自检` · `/微表情` · `/情绪曲线` · `/生成视频提示词` · `/导出工作流参数` · `/看板` · `/审查` · `跳过确认，直接出整集`

完整规则与指令路由见 [`short-drama-director/SKILL.md`](short-drama-director/SKILL.md)

---

## 📦 项目结构

```
lixiaoxiao9888-create/manju-laoli-skill/
└── short-drama-director/              # V6.8 轻量版主包（45 文件 · 38 规则库）
    ├── SKILL.md                       # 总控路由 + 工作法 + 模块索引
    ├── references/                    # 38 部专业规则库
    │   ├── asset-first-pipeline.md    #   Asset-First 六阶段（★流程权威）
    │   ├── model-adapters.md          #   七段式主格式唯一权威定义
    │   ├── aspect-ratio-adaptation.md #   画幅三选一锁定与全流程路由（★权威）
    │   ├── seedance-render-engine.md  #   时长预算 + 三层解耦
    │   ├── ★ facs-micro-expression.md #   FACS 微表情引擎（★表情域权威）
    │   ├── storyboard-board-lite.md   #   轻量离线分镜看板规范
    │   ├── ★ prompt-feeding-checklist.md  # P4 投喂必查清单（★执行序列权威）
    │   └── ... 共 38 模块
    ├── scripts/
    │   ├── check_package.py           # 静态 + 语义回归自检
    │   ├── build_board_lite.py        # 分镜看板编译器（md → 单文件 HTML）
    │   └── generate_emotion_curve.py  # 12 节拍情绪曲线绘图
    └── README.md / LICENSE / CHANGELOG.md
```

---

## 📜 更新历史

- **V6.8 轻量版**（2026-09-15）— 可灵移出正式支持（降级 LEGACY）/ 角色资产统一 **4 View** / 「七段式」命名统一、末尾参数行废止 / 空间 S0~S4 · 资产 A0~A3 · FACS **三级按需触发** / 2.5 新增**任务模式二选一**（全能参考 · 首尾帧）
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

**An industrial, full-pipeline creation skill package for AIGC audiovisual works — from concept lock-in to video-model feed prompts — built for AI agents / LLMs to call directly.**

![Pipeline](https://img.shields.io/badge/Pipeline-Asset--First-6a5acd)
![Models](https://img.shields.io/badge/Models-Seedance%202.5%20%7C%202.0-9d4edd)
![Platforms](https://img.shields.io/badge/Platforms-OpenClaw%20%7C%20Coze%20%7C%20Dify%20%7C%20WorkBuddy-00b4d8)
![QC](https://img.shields.io/badge/QC-P0%2FP1%2FP2-ff6b6b)

### 🎥 Production Pipeline

```
📋 Lock-in → ✍️ Gated Screenwriting → 🎙️ Dialogue → 🖼️ Asset Locking → 🎬 Dual-mode Storyboard → 🚀 Prompt Packaging → ✅ QC → 🖥️ Offline Board
```

</div>

---

## 🧭 What This Is

An **AIGC creation rulebase for AI agents** (OpenClaw Skill / Agent skill package) — not a finished screenplay. Drop `SKILL.md` plus `references/` into your agent's skill directory.

It turns AIGC audiovisual creation into a reusable industrial pipeline, solving three things:

1. **No drift** — characters / scenes / props are **generated and locked as reference images first**, before any storyboard (**Asset-First**: asset images precede storyboards);
2. **No rework** — mandatory front-end locks (model version / aspect ratio) + a pre-feed checklist + independent P0–P2 gates stop errors before generation;
3. **Feed-ready** — outputs a structured **7-section** prompt you can copy straight into the video model.

## 🎯 Use Cases

The pipeline is genre-agnostic: anything that goes **script → storyboard → video-model feed** fits.

- **AI short dramas / animated shorts / short-form series** (the densest use case)
- **AI commercials / brand films / concept films**
- **Storyboard previsualization (PREVIS)**
- **Action & fight choreography design** (modern combat, wuxia, xianxia, anime, sci-fi)
- **Emotional & micro-expression work** (FACS expression engineering)
- Any AI video production needing **cross-shot character consistency**

> Genres: modern urban / period wuxia / fantasy xianxia / mystery / sci-fi / cyberpunk / ink-wash guoman — including six cinematic audiovisual aesthetic presets.

## 🔥 Capabilities

| Stage | Capability | Description |
|:---:|:---|:---|
| 📋 **Lock-in** | Mandatory front-end locks | Model version (Seedance 2.5 / 2.0, **choose one**) + aspect ratio (16:9 / 9:16 / 21:9, **choose one**) — no work starts without them |
| ✍️ **Script** | 5-stage gated engine | Premise → Structure → Beat → Entity → Page; three-act structure, causal beat sheet, professional script page |
| 📈 **Emotion** | 12-beat curve | Full-episode tension on a 0–10 scale + chart script; peak/valley and 9th-beat reversal validation |
| 🎙️ **Dialogue** | 7-dimension diagnosis + speed check | Three speed tiers (3.5–5 chars/s baseline), long-line shot splitting, punchline breathing room |
| 🖼️ **Assets** | Asset-First digital asset pack | Character **4-View sheets** (10 facial + 6 material items) / scene maps / prop sheets; 《Asset Ledger》 CHR/AUD/PRP/SCN/Uxx; A/B/C grading, A0–A3 dependency triggering |
| 🎥 **Space** | One-line stance + grading | Stance declaration (position / anchor / facing / pose) + axis lock + movement chains; S0–S4 grading; 180° rule |
| 🎬 **Storyboard** | Dual-mode | Drama: 6-stage micro-expression progression / Action: 15s PREVIS completion scoring (R1 realistic · R2 commercial · R3 fantasy) + 15 camera rules + 3-technique / 6-form transitions |
| 😀 **Performance** | FACS micro-expression engine | Emotions as Action Units: 4-zone breakdown + 3 intensity tiers + real-vs-fake smile rule + emotion→AU recipes & AU dictionary (on-demand module) |
| ⚔️ **Libraries** | Martial arts / fantasy | 23 schools + 9 sword forms + weapons + lightness skills + 11 finisher links; fantasy spell combat R3 |
| 🚀 **Prompts** | 7-section main format | 【Style】→【Scene Asset】→【Characters】→【Stance】→【Timeline Storyboard】→【SFX】→【Hard Negatives】; 2.5 uses official sound chars + Hit-Stop + **task-mode choice** (all-reference / first-last frame) |
| ✅ **QC** | Independent P0–P2 gates | Duration / dialogue / axis / aspect / anchor consistency + 3-layer audio levels + mandatory 3-step re-verification after edits |
| 🖥️ **Board** | Offline storyboard board | Project md (single source of truth) → single-file HTML, double-click to open |
| 🛡️ **Compliance** | Safety translation dictionary | Rewrites gore/amputation into shockwave / spark / freeze-frame language to lower platform risk (no 100% guarantee) |

## 🖥️ Platforms & Models

| | Support |
|---|---|
| **Agent platforms** | OpenClaw · WorkBuddy · Doubao Agent / Coze · Dify, plus generic LLMs (Doubao JSON chunking supported) |
| **Video models** | **Seedance 2.5 / 2.0** (mandatory choice, fully split syntax contracts); Jimeng = secondary / legacy; Kling dropped to LEGACY as of V6.8 |
| **Outputs** | 7-section feed prompt sets · Canvas / API payloads · single-file offline storyboard board · emotion curve chart |

---

## ⚙️ Quick Start

```bash
# Install into OpenClaw
openclaw skills install ./short-drama-director --as short-drama-director

# Lint package integrity (38-module static + semantic regression check)
python3 short-drama-director/scripts/check_package.py

# Project md → single-file offline board
python3 short-drama-director/scripts/build_board_lite.py <project.md>

# 12-beat emotion curve
python3 short-drama-director/scripts/generate_emotion_curve.py
```

**Minimal agent sequence**: read `SKILL.md` → complete both locks → pick action tier (R1/R2/R3) → run the dialogue speed check if there is dialogue → lock assets → storyboard → generate feed prompts via `★ prompt-feeding-checklist.md` → pass `quality-gate-review`

### 🧮 Commands

`/写剧本` · `/拆资产` · `/资产图册` · `/角色资产板` · `/顶视图` · `/做分镜` · `/台词诊断` · `/语速自检` · `/微表情` · `/情绪曲线` · `/生成视频提示词` · `/导出工作流参数` · `/看板` · `/审查` · `跳过确认，直接出整集`

Full rules & routing: [`short-drama-director/SKILL.md`](short-drama-director/SKILL.md)

---

## 📦 Structure

```
lixiaoxiao9888-create/manju-laoli-skill/
└── short-drama-director/              # V6.8 Lite main package (45 files · 38 rulebooks)
    ├── SKILL.md                       # Router + working method + module index
    ├── references/                    # 38 professional rulebooks
    │   ├── asset-first-pipeline.md    #   Asset-First 6 stages (★flow authority)
    │   ├── model-adapters.md          #   7-section format — single authority
    │   ├── aspect-ratio-adaptation.md #   Aspect-ratio locking & routing (★)
    │   ├── seedance-render-engine.md  #   Duration budget + 3-layer decoupling
    │   ├── ★ facs-micro-expression.md #   FACS engine (★expression authority)
    │   ├── storyboard-board-lite.md   #   Offline board spec
    │   ├── ★ prompt-feeding-checklist.md  # P4 pre-feed checklist (★sequence authority)
    │   └── ... 38 modules total
    ├── scripts/
    │   ├── check_package.py           # Static + semantic regression lint
    │   ├── build_board_lite.py        # Board compiler (md → single-file HTML)
    │   └── generate_emotion_curve.py  # 12-beat emotion curve chart
    └── README.md / LICENSE / CHANGELOG.md
```

---

## 📜 Changelog

- **V6.8 Lite** (2026-09-15) — Kling demoted to LEGACY / character assets unified to **4 Views** / "7-section" naming unified, end-of-prompt parameter line abolished / space S0–S4 · asset A0–A3 · FACS **three-level on-demand triggering** / 2.5 gains **task-mode choice** (all-reference · first-last frame)
- **V6.7 Lite** (2026-09-14) — dual locks at equal weight (model version + 3-way aspect ratio) / Seedance 2.5 calibrated against official docs / FACS micro-expression engine absorbed / lightweight offline storyboard board absorbed
- **V6.5 Multi-Agent** (2026-09-01) — Asset-First 6 stages + multi-agent platform adapters + Seedance 2.5 deep adaptation + no-static-scene iron rule (AI video models cannot "act" while standing still; all emotion/charging must happen in motion)
- **V6.0** (2026-08-28) — 23-module reorganization + slimming + audit fixes
- **V5.0.2** (2026-08-27) — martial-arts library completion + combat-priority declaration
- Legacy archive: [**manju-laoli-skill-legacy**](https://github.com/lixiaoxiao9888-create/manju-laoli-skill-legacy)

---

<div align="center">

## 📄 License

**MIT** · For creative & learning use; comply with platform content policies

**Made with ❤️ for AIGC Creators**

</div>
