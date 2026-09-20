<div align="center">

# 🎬 漫剧老李 AIGC 创作全流程 Skill

## **V6.9.8 轻量版** · Short-Drama Director Suite

> 🎨 面向 **AIGC 视听创作** 的工业化全流程技能包
> 从创意立项到视频模型投喂提示词 —— 给 AI 助手 / LLM 直接调用

![Version](https://img.shields.io/badge/版本-V6.9.8--轻量版-6a5acd)
![Modules](https://img.shields.io/badge/规则库-41%20模块-00b4d8)
![Files](https://img.shields.io/badge/文件-49-2ec4b6)
![Models](https://img.shields.io/badge/模型-Seedance%202.5%20%7C%202.0%20%7C%20MiniMax%20H3-9d4edd)
![QC](https://img.shields.io/badge/机检-C1~C20%20%7C%20H1~H12-ff6b6b)
![Platform](https://img.shields.io/badge/平台-OpenClaw%20%7C%20Coze%20%7C%20Dify%20%7C%20WorkBuddy-ff9f43)
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
2. **不返工** —— 前置强制锁定（模型版本 / 画幅）+ 投喂前必查清单 + P0~P2 独立门禁 + **稿件级机检**，把错误拦在生成之前；
3. **能直接投喂** —— 输出**七段式**结构化提示词，整组复制即可喂给视频模型，不需要二次翻译；走 **MiniMax H3** 时自动转成 H3 原生六段式。

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
| 📋 **立项** | 前置强制锁定 | 模型版本（**三选一**：Seedance 2.5 / Seedance 2.0 / **MiniMax H3 格式支线**）+ 画幅（16:9 / 9:16 / 21:9 **三选一**）+ 段缝衔接方式（多段任务）——未指定不动笔，禁止默认 |
| ✍️ **剧本** | 五阶门控引擎 | Premise → Structure → Beat → Entity → Page；含三幕结构、因果节拍表与专业剧本页排版 |
| 📈 **情绪** | 12 节拍曲线 | 全片张力 0~10 量化 + 折线图脚本；波峰/波谷与第 9 节拍反杀峰值校验 |
| 🎙️ **台词** | 七维诊断 + 语速自检 + **语气位** | 三维语速档（3.5~5 字/秒基准）、超长句拆镜、金句发酵气口；**对白三要素之三（HOW THEY SOUND）**——台词统一 `台词：【角色（语气）："…"】`，2.0/2.5 同规格必写 |
| 🖼️ **资产** | Asset-First 数字资产包 | 角色 **4 View 资产板**（五官 10 项 + 服装材质 6 项）/ 场景空间图三件套 / 道具图；《资产图册》CHR/AUD/PRP/SCN/Uxx 台账；A/B/C 分级、依赖 A0~A3 按需触发 |
| 🎥 **空间** | 一行式站位 + 分级 | 【站位声明】四要素（位置/依托物/朝向/姿态）+ 轴线锁 + 位移链；空间 S0~S4 分级；180° 轴线；**人物账连续·摆位必入画**（摆了位的人本段必须被镜头带到，否则写明离画/退场） |
| 🎬 **分镜** | 文武双模 + 首镜锚定 | 文戏微表情六阶段递进 / 武戏 15 秒 PREVIS 完播评分（R1 写实 · R2 商业高燃 · R3 玄幻）；镜头规格 15 铁律 + 三手法六式衔接；**首镜锚定·景别一致·姿态延续·视线指派**（首镜必带具名主体）+ **首镜单主体**（禁「X 与 Y 同框」并列句式） |
| 😀 **表演** | FACS 微表情引擎 | 情绪 AU 化：四区拆解 + 强度三档 + 真假笑铁律 + 情绪→AU 配方库与 AU 字典（增强模块 · 按需触发） |
| ⚔️ **资料库** | 武学 / 玄幻 | 23 门武学 + 9 套剑法 + 兵器 + 轻功 + 11 环杀招；玄幻法术 R3（法宝 / 五行术法 / 能量具象 / 对军清场） |
| 🚀 **提示词** | 七段式主格式 + **H3 格式支线** | 【画幅风格】→【场景资产】→【核心人物】→【站位声明】→【时间轴分镜】→【音效】→【强制禁止项】；2.5 走官方声音字符（`<>` `{}` `()` `【】`）+ Hit-Stop 顿挫 + 任务模式二选一（全能参考 / 首尾帧）；**选 H3 时自动转 Ref2VA 六段式**（subject_definitions / summary / retention_analysis / detailed_description / overall_soundscape / non_diegetic_music） |
| 🚫 **禁令** | 禁令失效三改法 | 视频模型对否定不敏感、对词根敏感——被禁概念的词根哪怕挂着"不/禁"也会被渲染；禁止项栏目纪律（只装负面清单，禁混正向执行指令） |
| ✅ **质检** | P0~P2 门禁 + 稿件级机检 | 时长 / 台词 / 跳轴 / 画幅 / 资产锚点一致性 + 声音三层相对电平 + **改动后三步复验铁律**；`validate_prompt.py` 出稿机检 **C1~C20**（Seedance 侧）/ **H1~H12**（H3 侧，`--model h3`） |
| 🖥️ **看板** | 离线分镜看板 | 项目 md（唯一真相）→ 单文件 HTML，双击即开；P2.5 出图词与 P4 投喂词必同板 |
| 🛡️ **合规** | 安全转译词典 | 把血腥/断肢类动作转译为「气浪震散 / 火花消散 / 重创定格」，降低平台风险（不承诺 100% 通过） |

## 🖥️ 适用平台与模型

| | 支持 |
|---|---|
| **Agent 平台** | OpenClaw · WorkBuddy · 豆包智能体 / 扣子(Coze) · Dify 及通用 LLM（支持豆包 JSON 分块，防上下文截断） |
| **视频模型** | **Seedance 2.5 / 2.0**（强制二选一，语法契约彻底分流）+ **MiniMax H3**（格式支线：只做七段式→H3 原生格式转换，单段 4–15s）；即梦为次选 / 历史兼容；可灵自 V6.8 起移出正式支持（LEGACY） |
| **输出** | 七段式投喂提示词组（Seedance）· **H3 Ref2VA 六段式稿** · Canvas / API 结构化载荷 · 单文件离线分镜看板 · 情绪曲线图 |

---

## ⚙️ 快速开始

```bash
# 安装到 OpenClaw
openclaw skills install ./short-drama-director --as short-drama-director

# 自检包完整性（41 模块静态 + 语义回归检查 ①~⑱ 组）
python3 short-drama-director/scripts/check_package.py

# 出稿机检（FAIL 清零才交付）
python3 short-drama-director/scripts/validate_prompt.py <稿>.md --model 2.5|2.0|h3

# 项目 md → 单文件离线看板
python3 short-drama-director/scripts/build_board_lite.py <项目.md>

# 12 节拍情绪曲线
python3 short-drama-director/scripts/generate_emotion_curve.py
```

**给 AI 助手的最小执行序列**：读 `SKILL.md` → 完成 A/B（+多段任务 D）锁 → 定动作强度档（R1/R2/R3）→ 有对白先过语速自检 + 语气位 → 资产出图锁定 → 分镜 → 按 `★ prompt-feeding-checklist.md` 生成投喂词 → 跑 `validate_prompt.py` 机检 → 过 `quality-gate-review`

### 🧮 常用指令

`/写剧本` · `/拆资产` · `/资产图册` · `/角色资产板` · `/顶视图` · `/做分镜` · `/台词诊断` · `/语速自检` · `/微表情` · `/情绪曲线` · `/生成视频提示词` · **`/H3提示词`** · `/导出工作流参数` · `/看板` · `/审查` · `跳过确认，直接出整集`

完整规则与指令路由见 [`short-drama-director/SKILL.md`](short-drama-director/SKILL.md)

---

## 📦 项目结构

```
lixiaoxiao9888-create/manju-laoli-skill/
└── short-drama-director/              # V6.9.8 轻量版主包（49 文件 · 41 规则库）
    ├── SKILL.md                       # 总控路由 + 工作法 + 模块索引（法则 0~25）
    ├── references/                    # 41 部专业规则库
    │   ├── asset-first-pipeline.md    #   Asset-First 六阶段（★流程权威）
    │   ├── model-adapters.md          #   七段式主格式唯一权威定义 + 语气位/摆位/首镜锚定
    │   ├── ★ h3-adapter.md            #   MiniMax H3 格式支线（★：两 checkpoint 路由/字段映射/9 张取材策略/H1~H12）
    │   ├── aspect-ratio-adaptation.md #   画幅三选一锁定与全流程路由（★权威）
    │   ├── segment-splicing.md        #   段缝衔接（D 锁：末态双保险/换机位/空镜）
    │   ├── vo-os-weaving.md           #   旁白与独白视听编织（OS 声画分离红线）
    │   ├── seedance-render-engine.md  #   时长预算 + 三层解耦
    │   ├── ★ facs-micro-expression.md #   FACS 微表情引擎（★表情域权威）
    │   ├── storyboard-board-lite.md   #   轻量离线分镜看板规范
    │   ├── ★ prompt-feeding-checklist.md  # P4 投喂必查清单（★执行序列权威）
    │   └── ... 共 41 模块
    ├── scripts/
    │   ├── check_package.py           # 静态 + 语义回归自检（①~⑱ 组）
    │   ├── validate_prompt.py         # 稿件级投喂机检（C1~C20 / --model h3 → H1~H12）
    │   ├── build_board_lite.py        # 分镜看板编译器（md → 单文件 HTML）
    │   └── generate_emotion_curve.py  # 12 节拍情绪曲线绘图
    └── README.md / LICENSE / CHANGELOG.md
```

---

## 📜 更新历史

- **V6.9.8 轻量版**（2026-09-20）— 新增 **MiniMax H3 格式支线**：A 锁并列第三选项，只做「七段式 → H3 原生格式」转换（`h3-adapter.md`：两 checkpoint 路由 / 六段式映射 / 素材上限 9 图·3 视频·3 音频·总 12 / 9 张取材策略 / 两套投喂载荷）；出稿机检新增 **H1~H12**（`--model h3`）
- **V6.9.3 ~ V6.9.7 轻量版**（2026-09-19）— 五轮实拍复盘驱动的定向修订：**对白语气位**（C16）· **人物账连续·摆位必入画**（C17）· **首镜锚定·景别一致·姿态延续·视线指派**（C18）· **禁令失效三改法 + 栏目纪律**（C19 / C19e）· **首镜单主体锚定与具象化**（C20）· **示范句验证纪律**（⑰ 规则自洽门）；机检升至 C1~C20
- **V6.9 轻量版**（2026-09-18）— 新增 **〇节 D·段缝衔接方式三选一锁**（末态双保险 / 换机位硬切 / 空镜过渡，治"段落间衔接生硬"）/ **旁白·独白视听编织规程**（篇幅卡口 · OS 声画分离红线 · VO 冷漠审视）/ **时长守恒·禁拉伸凑满**（法则 17 修订 + C15 门）
- **V6.8 轻量版**（2026-09-15）— 可灵移出正式支持（降级 LEGACY）/ 角色资产统一 **4 View** / 「七段式」命名统一、末尾参数行废止 / 空间 S0~S4 · 资产 A0~A3 · FACS **三级按需触发** / 2.5 新增**任务模式二选一**（全能参考 · 首尾帧）
- **V6.7 轻量版**（2026-09-14）— 双锁同规格（模型版本 + 画幅三选一强制锁）/ 按官方文档校准 Seedance 2.5 / 吸收 FACS 微表情引擎三件套 / 吸收轻量离线分镜看板
- **V6.5 Multi-Agent**（2026-09-01）— Asset-First 六阶段 + 多 Agent 平台适配 + Seedance 2.5 深度适配 + 静止段禁用铁律（AI 视频无静止表演能力，情绪蓄力必须在运动中完成）
- 旧版归档：[**manju-laoli-skill-legacy**](https://github.com/lixiaoxiao9888-create/manju-laoli-skill-legacy)

---

<div align="center">

---

# 🇬🇧 English Overview

## **V6.9.8 Lite** · Short-Drama Director Suite

**An industrial, full-pipeline creation skill package for AIGC audiovisual works — from concept lock-in to video-model feed prompts — built for AI agents / LLMs to call directly.**

![Pipeline](https://img.shields.io/badge/Pipeline-Asset--First-6a5acd)
![Models](https://img.shields.io/badge/Models-Seedance%202.5%20%7C%202.0%20%7C%20MiniMax%20H3-9d4edd)
![QC](https://img.shields.io/badge/QC-C1~C20%20%7C%20H1~H12-ff6b6b)
![Platforms](https://img.shields.io/badge/Platforms-OpenClaw%20%7C%20Coze%20%7C%20Dify%20%7C%20WorkBuddy-00b4d8)

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
2. **No rework** — mandatory front-end locks (model version / aspect ratio) + a pre-feed checklist + independent P0–P2 gates + **shot-level machine QC** stop errors before generation;
3. **Feed-ready** — outputs a structured **7-section** prompt you can copy straight into the video model; when **MiniMax H3** is selected, it converts automatically into H3's native 6-section format.

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
| 📋 **Lock-in** | Mandatory front-end locks | Model version (**choose one**: Seedance 2.5 / Seedance 2.0 / **MiniMax H3 format branch**) + aspect ratio (16:9 / 9:16 / 21:9) + seam-joining mode for multi-segment work — no work starts without them |
| ✍️ **Script** | 5-stage gated engine | Premise → Structure → Beat → Entity → Page; three-act structure, causal beat sheet, professional script page |
| 📈 **Emotion** | 12-beat curve | Full-episode tension on a 0–10 scale + chart script; peak/valley and 9th-beat reversal validation |
| 🎙️ **Dialogue** | 7-dimension diagnosis + speed check + **tone slot** | Three speed tiers (3.5–5 chars/s baseline), long-line shot splitting, punchline breathing room; **the third element of dialogue (HOW THEY SOUND)** — every line is written as `台词：【角色（语气）："…"】`, mandatory for both 2.0 and 2.5 |
| 🖼️ **Assets** | Asset-First digital asset pack | Character **4-View sheets** (10 facial + 6 material items) / 3-piece scene maps / prop sheets; 《Asset Ledger》 CHR/AUD/PRP/SCN/Uxx; A/B/C grading, A0–A3 dependency triggering |
| 🎥 **Space** | One-line stance + grading | Stance declaration (position / anchor / facing / pose) + axis lock + movement chains; S0–S4 grading; 180° rule; **placement must appear on screen** (anyone placed in the stance block must be covered by at least one shot, else marked as exiting) |
| 🎬 **Storyboard** | Dual-mode + first-shot anchoring | Drama: 6-stage micro-expression progression / Action: 15s PREVIS completion scoring (R1 realistic · R2 commercial · R3 fantasy) + 15 camera rules + 3-technique / 6-form transitions; **first-shot anchoring / consistent shot size / pose carry-over / gaze assignment**, plus **single-subject anchoring** (no "X and Y in the same frame" phrasing) |
| 😀 **Performance** | FACS micro-expression engine | Emotions as Action Units: 4-zone breakdown + 3 intensity tiers + real-vs-fake smile rule + emotion→AU recipes & AU dictionary (on-demand module) |
| ⚔️ **Libraries** | Martial arts / fantasy | 23 schools + 9 sword forms + weapons + lightness skills + 11 finisher links; fantasy spell combat R3 |
| 🚀 **Prompts** | 7-section main format + **H3 branch** | 【Style】→【Scene Asset】→【Characters】→【Stance】→【Timeline Storyboard】→【SFX】→【Hard Negatives】; 2.5 uses official sound chars + Hit-Stop + task-mode choice; **selecting H3 converts it into Ref2VA's six sections** |
| 🚫 **Negatives** | Three rewrites for failed bans | Video models are insensitive to negation but sensitive to word roots — a banned concept's root still renders even with "no/never" attached; the negatives block holds only negative lists, never positive execution instructions |
| ✅ **QC** | P0–P2 gates + shot-level lint | Duration / dialogue / axis / aspect / anchor consistency + 3-layer audio levels + mandatory 3-step re-verification after edits; `validate_prompt.py` runs **C1–C20** (Seedance) / **H1–H12** (H3, `--model h3`) |
| 🖥️ **Board** | Offline storyboard board | Project md (single source of truth) → single-file HTML, double-click to open |
| 🛡️ **Compliance** | Safety translation dictionary | Rewrites gore/amputation into shockwave / spark / freeze-frame language to lower platform risk (no 100% guarantee) |

## 🖥️ Platforms & Models

| | Support |
|---|---|
| **Agent platforms** | OpenClaw · WorkBuddy · Doubao Agent / Coze · Dify, plus generic LLMs (Doubao JSON chunking supported) |
| **Video models** | **Seedance 2.5 / 2.0** (mandatory choice, fully split syntax contracts) + **MiniMax H3** (format branch: 7-section → H3 native format, 4–15s per segment); Jimeng = secondary / legacy; Kling dropped to LEGACY as of V6.8 |
| **Outputs** | 7-section feed prompt sets (Seedance) · **H3 Ref2VA six-section scripts** · Canvas / API payloads · single-file offline storyboard board · emotion curve chart |

---

## ⚙️ Quick Start

```bash
# Install into OpenClaw
openclaw skills install ./short-drama-director --as short-drama-director

# Lint package integrity (41-module static + semantic regression, groups ①~⑱)
python3 short-drama-director/scripts/check_package.py

# Shot-level feed lint (zero FAIL to ship)
python3 short-drama-director/scripts/validate_prompt.py <script>.md --model 2.5|2.0|h3

# Project md → single-file offline board
python3 short-drama-director/scripts/build_board_lite.py <project.md>

# 12-beat emotion curve
python3 short-drama-director/scripts/generate_emotion_curve.py
```

**Minimal agent sequence**: read `SKILL.md` → complete A/B (and D for multi-segment) locks → pick action tier (R1/R2/R3) → run the dialogue speed check + tone slot if there is dialogue → lock assets → storyboard → generate feed prompts via `★ prompt-feeding-checklist.md` → pass `validate_prompt.py` → pass `quality-gate-review`

### 🧮 Commands

`/写剧本` · `/拆资产` · `/资产图册` · `/角色资产板` · `/顶视图` · `/做分镜` · `/台词诊断` · `/语速自检` · `/微表情` · `/情绪曲线` · `/生成视频提示词` · **`/H3提示词`** · `/导出工作流参数` · `/看板` · `/审查` · `跳过确认，直接出整集`

Full rules & routing: [`short-drama-director/SKILL.md`](short-drama-director/SKILL.md)

---

## 📦 Structure

```
lixiaoxiao9888-create/manju-laoli-skill/
└── short-drama-director/              # V6.9.8 Lite main package (49 files · 41 rulebooks)
    ├── SKILL.md                       # Router + working method + module index (laws 0–25)
    ├── references/                    # 41 professional rulebooks
    │   ├── asset-first-pipeline.md    #   Asset-First 6 stages (★flow authority)
    │   ├── model-adapters.md          #   7-section format authority + tone/placement/first-shot anchoring
    │   ├── ★ h3-adapter.md            #   MiniMax H3 format branch (★: 2-checkpoint routing / field mapping / 9-image sourcing / H1–H12)
    │   ├── aspect-ratio-adaptation.md #   Aspect-ratio locking & routing (★)
    │   ├── segment-splicing.md        #   Segment-seam joining (D-lock: end-state twin insurance / camera swap / empty shot)
    │   ├── vo-os-weaving.md           #   Narration & inner-monologue weaving (OS audio-visual split rule)
    │   ├── seedance-render-engine.md  #   Duration budget + 3-layer decoupling
    │   ├── ★ facs-micro-expression.md #   FACS engine (★expression authority)
    │   ├── storyboard-board-lite.md   #   Offline board spec
    │   ├── ★ prompt-feeding-checklist.md  # P4 pre-feed checklist (★sequence authority)
    │   └── ... 41 modules total
    ├── scripts/
    │   ├── check_package.py           # Static + semantic regression lint (groups ①~⑱)
    │   ├── validate_prompt.py         # Shot-level feed lint (C1–C20 / --model h3 → H1–H12)
    │   ├── build_board_lite.py        # Board compiler (md → single-file HTML)
    │   └── generate_emotion_curve.py  # 12-beat emotion curve chart
    └── README.md / LICENSE / CHANGELOG.md
```

---

## 📜 Changelog

- **V6.9.8 Lite** (2026-09-20) — adds the **MiniMax H3 format branch**: a third option at the A-lock that only converts the 7-section script into H3's native format (`h3-adapter.md`: 2-checkpoint routing / six-section mapping / material caps of 9 images · 3 videos · 3 audios · 12 files total / 9-image sourcing strategy / two feed payloads); shot-level lint gains **H1–H12** (`--model h3`)
- **V6.9.3 – V6.9.7 Lite** (2026-09-19) — five rounds of revisions driven by real shoot retros: **dialogue tone slot** (C16) · **placement must appear on screen** (C17) · **first-shot anchoring / shot-size consistency / pose carry-over / gaze assignment** (C18) · **three rewrites for failed bans + negatives-block discipline** (C19 / C19e) · **first-shot single-subject anchoring and concreteness** (C20) · **exemplar validation discipline** (⑰ self-consistency gate); lint raised to C1–C20
- **V6.9 Lite** (2026-09-18) — adds the **D-lock: three ways to join segments** (end-state twin insurance / camera swap / empty shot), the **narration & inner-monologue weaving spec** (length quota · OS audio-visual split · detached VO gaze) and **duration conservation / no stretching to fill** (law 17 revised + gate C15)
- **V6.8 Lite** (2026-09-15) — Kling demoted to LEGACY / character assets unified to **4 Views** / "7-section" naming unified, end-of-prompt parameter line abolished / space S0–S4 · asset A0–A3 · FACS **three-level on-demand triggering** / 2.5 gains **task-mode choice**
- **V6.7 Lite** (2026-09-14) — dual locks at equal weight / Seedance 2.5 calibrated against official docs / FACS engine absorbed / lightweight offline board absorbed
- **V6.5 Multi-Agent** (2026-09-01) — Asset-First 6 stages + multi-agent platform adapters + Seedance 2.5 deep adaptation + no-static-scene iron rule
- Legacy archive: [**manju-laoli-skill-legacy**](https://github.com/lixiaoxiao9888-create/manju-laoli-skill-legacy)

---

<div align="center">

## 📄 License

**MIT** · For creative & learning use; comply with platform content policies

**Made with ❤️ for AIGC Creators**

</div>
