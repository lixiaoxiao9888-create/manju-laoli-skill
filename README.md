<div align="center">

# 🎬 漫剧老李 AIGC 创作全流程 Skill

## **V7.5.0-SLIM 精简套装版** · Short-Drama Director Suite

> **版本**：V7.5.0-SLIM 精简套装版（Suite）· 在全量版基础上**删去海外剧剧本（sd-overseas-engine）与解说叙事（sd-jieshuo-engine）两条赛道及〇·0 赛道分流锁**，其余判据一条未改。改动与验收记录见 [`short-drama-director/CHANGELOG.md`](short-drama-director/CHANGELOG.md)。

> 🎨 面向 **AIGC 视听创作** 的工业级全流程技能包（**1 总控 + 10 子技能 · 四层纵深**）
> 从创意立项、剧本、资产、分镜到视频模型投喂提示词与独立质检 —— 给 AI 助手 / LLM 直接调用

![Version](https://img.shields.io/badge/版本-V7.5.0--SLIM-6a5acd)
![Structure](https://img.shields.io/badge/结构-1%20总控%20%7C%2010%20子技能-8e44ad)
![Rulebooks](https://img.shields.io/badge/规则库-48%20份-00b4d8)
![Files](https://img.shields.io/badge/文件-155-2ec4b6)
![Models](https://img.shields.io/badge/模型-Seedance%202.5%20%7C%202.0-9d4edd)
![QC](https://img.shields.io/badge/机检-C1~C41-ff6b6b)
![Platform](https://img.shields.io/badge/平台-OpenClaw%20%7C%20Coze%20%7C%20Dify%20%7C%20WorkBuddy-ff9f43)
![License](https://img.shields.io/badge/License-MIT-ffca3a)
![Stars](https://img.shields.io/github/stars/lixiaoxiao9888-create/manju-laoli-skill?style=social)

---

### 🎥 生产管线

```
📋 立项锁定 → ✍️ 五阶门控剧本 → 🖼️ 资产锁定 → 🎬 文武双模分镜 → 🚀 提示词封装 → ✅ 独立质检 → 🖥️ 离线看板
```

</div>

---

## 🏆 赞助商

感谢以下赞助商对本项目的支持：

| LOGO | 类型 | 赞助商名称 | 说明 | 网站 |
| --- | --- | --- | --- | --- |
| <img src="assets/omniboard.jpg" alt="OmniBoard" width="160"> | 企业 | OmniBoard | 字字动画旗下专业漫剧创作画布工具，从剧本到发行变现全链路一站式，新手可用 H3 模型五分钱一秒 | [omniboard.tv/register?ref=GITHUBADD7DZ](https://omniboard.tv/register?ref=GITHUBADD7DZ) |
| <img src="assets/himadrama.png" alt="浮瑞万相AI" width="160"> | 企业 | 浮瑞万相AI | 浮瑞万相AI旗下喜马抓马 AI 视听全链路综合服务平台，HimaStudio 多模态 AI 视听创作平台及线上 OPC 社区 · 深度适配漫剧老李 Skill | [himadrama.com](https://www.himadrama.com) |
| <img src="assets/dianzhong.png" alt="点众" width="160"> | 企业 | 点众 | 开放全 IP 库，超创与公司自制权限相同，可看到典藏版、爆款剧、精品剧的 IP | [点众开放 IP 库](https://vcnti1p0lovd.feishu.cn/wiki/VDIowZgiOiymKCkc1vnc7MjTnYe) |
| *（LOGO 占位）* | — | 虚位以待 | 赞助位开放中——让你的产品出现在众多 AI 短剧创作者面前 | [联系我们](mailto:lixiaoxiao9888@gmail.com) |

> 💡 **招商说明**：赞助位对模型渠道、算力平台、API 服务商及创作团队开放。
> 合作请联系：邮箱 `lixiaoxiao9888@gmail.com` · 微信 `lisenlin998`

### 🎬 分镜引擎专项赞助用户

感谢以下用户赞助分镜引擎的开发（开放中）：

*你的头像将出现在这里。*

| 赞助用户 | 联系方式 |
| --- | --- |
| 汤圆（用老李 skills 出剧 · 包算力 · 包发行） | 微信：fush989 |

---

## 🧭 这是什么

一套 **给 AI 助手执行的 AIGC 全流程创作规则库**（OpenClaw Skill / Agent 技能包）。**自多技能套装版起升级为「多技能套装」**：**1 个总控**（`short-drama-director`）+ **10 个子技能**（`sd-*-engine`），**四层纵深架构**——不是单一 `SKILL.md`，而是一套可路由、可挂载、可机检的导演系统。

> **核心理念**：「**用户看到的是 5 个步骤，AI 内部跑的是 100 条规则**」——用户层只做「① 做什么 ② 从哪来 ③ 模型 ④ 画幅 ⑤ 要什么结果」，**锁 / 路由 / 子技能挂载 / 机检全部由总控内部完成**，用户**不需要手动调用任何子技能**（直接说需求，总控自动路由；但五道锁必须弹出让用户勾选）。

它把「AIGC 视听创作」拆成一条可复用的工业化管线，核心解决三件事：

1. **不漂移** —— 角色 / 场景 / 道具**先锁定再进分镜**（Asset-First），跨镜跨集一致性有据可依；
2. **不返工** —— **五道前置锁 + 投喂必查清单** + P0~P2 独立门禁 + 稿件级机检**，把错误拦在生成之前；
3. **能直接投喂** —— 输出 **七段式**结构化提示词，整组复制即可喂给视频模型。

> 🔑 **本包不持有图**：交付的是「**提示词 + 接线说明书**」——图由用户在外部平台（即梦 / Seedance / 豆包等）自行生成并持有。素材按**存在形态**分三档：**M0 纯提示词 / M1 编号占位（默认）/ M2 已入库**，**每次交付首行声明形态**。

## 🎯 适用场景

管线与题材解耦，凡「**剧本 → 分镜 → 视频模型投喂**」的 AIGC 创作都可套用：

- **AI 短剧 / 漫剧 / 短视频剧集**（本包最典型的高密度场景）
- **AI 广告片 / 品牌宣传片 / 概念片**
- **分镜预演（PREVIS）与动态分镜** · **武打 / 动作场面设计**（现代格斗、武侠、仙侠、二次元、科幻）
- **情绪戏 / 微表情专项**（FACS 表情工程）
- 任何需要**跨镜头角色一致性**的 AI 视频生产

## 🧩 四层纵深架构（1 总控 + 10 子技能）

| 层 | 技能 | 职责 |
|:---:|:---|:---|
| **L0 总控** | `short-drama-director` | 素材来源 · **素材形态 M0/M1/M2** · 锁系统 · **48 份规则库**（含 style-bible 画风锁知识库 8 份）· 七段式 · 机检 **C1~C26**（另设增量主码 C27~C41）· P0~P2 门禁 · ★场面调度 · ★素材形态与接线单 |
| **L1 决策** | `sd-decision-engine` | 情境映射 E01~E15 + 80/15/5 权重 + 情绪锚点表 + 构图雷区 A/B 双态白名单——回答「这场戏该用什么镜头」 |
| **L2 生产** | `sd-recon-engine` | 素材采风与对标情报（只交付《对标情报卡》，不做打分 / 聚簇 / 台账 / 定时抓取） |
| | `sd-script-engine` | 剧本创作与小说改编（六阶段编剧链 + 五席圆桌审核 + 台词七维诊断 + 拟人化引擎 + 外来剧本润色层） |
| | `sd-asset-engine` | 资产锁定（三清单 · 场景连续性 · 道具单实例锁 · 人群调度 · 按素材形态产出 + 接线单） |
| | `sd-storyboard-engine` | 文戏/日常戏分镜（★故事板图·面板链 · 剧情分镜格 · 段内衔接 5 维 / 运镜 5 模式） |
| | `sd-combat-engine` | 通用打戏分镜（摄影机行为锁 · 战场群战速查） |
| | `sd-xuanhuan-engine` | 玄幻仙侠打戏（黄金颗粒度 · 双向攻防 · 收束闭环 · 法武合一招式库） |
| | `sd-real-engine` | 真人写实打戏（R1 克制档 · 11 环动力链 · 真实格斗招式库 · 多人战斗调度） |
| **L3 交付** | `sd-feed-engine` | A/B/C 输出模式 + **投喂层闸门**（闸门 6 = 编号一致性 + 素材形态一致性）+ 素材映射 / 人物锚定 + 《素材接线单》+ 多段衔接 + 工程语言清洗 |
| | `sd-qc-engine` | 成片质检与连续性管理（一致性台账 · 剪辑转场 · 声音设计 · 后期音乐与 BGM Cue Sheet · 出稿机检） |

## 🔒 五道前置锁 + I 画风锁（动手前全部弹出让用户勾选）

| 锁 | 选项 | 说明 |
|:---:|:---|:---|
| **〇·1 素材来源** | ① 原创 ② 改编 ③ 对标爆款 ④ 热点速成 | 第 1 道锁，先于一切创作；③④ 挂 `sd-recon-engine`，先出《对标情报卡》 |
| **A 模型版本** | Seedance 2.5 / 2.0 | **二选一**，锁定后语法契约彻底分流 |
| **B 画幅** | 16:9 / 9:16 / 21:9 | 与模型版本同规格前置锁定，未指定不动笔 |
| **C 交付形态** | ① 离线看板 ② md ③ 两者都交付 | ★ 强制锁，未指定 = 停下询问 |
| **D 段缝衔接方式** | ① 末帧定格承接 ② 换机位硬切 ③ 空镜过渡 ④ 技巧型转场 | 多段任务四选一，四项独立弹出 |
| **I 画风锁** | 候选卡内勾选（含「按你的推荐走」） | 导演风格卡锁定，选定即冻结 |

> ⚠️ 任何一道未指定，**必须停下询问并把选项摆出来让用户勾**——禁止默认跳过、禁止替用户推断（硬门，不是建议）。另含**动作强度三档定档**：`R1 写实克制` / `R2 商业高燃（默认）` / `R3 玄幻大招`。

## 🔥 核心能力

| 阶段 | 能力 | 说明 |
|:---:|:---|:---|
| 📥 **采风** | 对标情报（★〇·1） | 信源分级（T1 平台官方 / T1.5 数据指数站 / T2 媒体与讨论，含外网独立指数）· 采风四步 · 《对标情报卡》十三项字段 · 六条证据纪律 |
| ✍️ **剧本** | 六阶段编剧链 | 来源登记 → IP 与角色开发 → 开发圣经 → 分集规划 → 正式剧本 → 五席圆桌审核；含反捧杀 / 台词七维诊断 / 台词拟人化引擎 / 平台节奏矩阵 |
| 📈 **情绪** | 12 节拍曲线 | 全片张力 0~10 量化 + 折线图脚本；波峰/波谷与第 9 节拍反杀峰值校验 |
| 🎙️ **台词** | 七维诊断 + 语速自检 + 语气位 | 三维语速档、超长句拆镜、金句发酵气口；对白统一 `台词：【角色（语气）："…"】`，2.0/2.5 同规格必写 |
| 🖼️ **资产** | Asset-First 资产包 | 角色资产板 / 场景空间图三件套 / 道具图；CHR/AUD/PRP/SCN/Uxx 台账；A/B/C 分级、A0~A3 按需触发 |
| 🎥 **空间** | 一行式站位 + 分级 | 【站位声明】四要素 + 轴线锁 + 位移链；空间 S0~S4；180° 轴线；**人物账连续·摆位必入画** |
| 🎬 **分镜** | 文武双模 + 故事板图 | 文戏微表情六阶段 / 武戏 PREVIS 完播评分；★故事板图（面板链，动作相位七态拆格）· ★剧情分镜格（推演宫格）· 段内衔接 5 维 / 运镜 5 模式 |
| ⚔️ **打戏** | 三大打戏引擎 | 通用打戏（`sd-combat`）· 玄幻仙侠（`sd-xuanhuan`）· 真人写实（`sd-real`）——分域专精，总控不持有打戏规则 |
| 🚀 **提示词** | 七段式 | 【画幅风格】→【场景资产】→【核心人物】→【站位声明】→【时间轴分镜】→【音效】→【强制禁止项】 |
| 🚫 **禁令** | 禁令失效三改法 | 模型对否定不敏感、对词根敏感——高关联概念换词 / 主体优先句式 / 触发器移除；【强制禁止项】只装负面清单 |
| ✅ **质检** | P0~P2 门禁 + 稿件级机检 | `validate_prompt.py` **C1~C26**（子检查码共 104 条，另设增量主码 C27~C41）；投喂层另加**投喂层闸门**（`gate_check.py`） |
| 🖥️ **看板** | 离线分镜看板 | 项目 md（唯一真相）→ 单文件 HTML，双击即开；可导出 SRT 字幕 / 剪辑时间线 CSV / API 载荷 JSON |
| 🎵 **声音** | 后期音乐与声音设计 | BGM Cue Sheet / 音乐搜索词 / AI 音乐提示词 / 版权检查（`sd-qc-engine`） |
| 🛡️ **合规** | 安全转译词典 | 把血腥/断肢类动作转译为「气浪震散 / 火花消散 / 重创定格」，降低平台风险（不承诺 100% 通过） |

## 🖥️ 适用平台与模型

| | 支持 |
|---|---|
| **Agent 平台** | OpenClaw · WorkBuddy · 豆包智能体 / 扣子(Coze) · Dify 及通用 LLM（支持豆包 JSON 分块，防上下文截断） |
| **视频模型** | **Seedance 2.5 / 2.0**（强制二选一，语法契约彻底分流；**包内唯一模型线**） |
| **输出** | 七段式投喂提示词组 · Canvas / API 结构化载荷 · 单文件离线分镜看板 · 情绪曲线图 |

---

## ⚙️ 快速开始

> 📦 **部署（Multi-Agent 套装）**：本仓根目录**并列** 1 个总控（`short-drama-director/`）+ 10 个子技能（`sd-*-engine/`）。**支持多技能目录的平台（如 OpenClaw）把 13 个技能目录整体同级部署即可，主入口 = `short-drama-director`**；要求「zip 根即 `SKILL.md`」的单技能平台，请以 `short-drama-director/SKILL.md` 为主入口并把子技能**同级**补齐。

```bash
# 安装到 OpenClaw（总控 + 10 子技能整体同级部署）
openclaw skills install ./short-drama-director --as short-drama-director

# 包级自检（48 份规则库静态 + 语义回归）
python3 short-drama-director/scripts/check_package.py

# 出稿质检（★一次跑完：投喂层闸门 + C 系机检，FAIL 清零才交付）
python3 sd-feed-engine/scripts/gate_check.py <稿>.md --model 2.5 --aspect 16:9

# 契约核销（查"该交的东西交没交"，与语法判据不重叠）
python3 short-drama-director/scripts/audit_contract.py <稿>.md

# 项目 md → 单文件离线看板
python3 short-drama-director/scripts/build_board_lite.py <项目.md>
```

**给 AI 助手的最小执行序列**：读 `SKILL.md` → 完成**五道前置锁 + 画风锁**（〇·1 素材来源 / A 模型 / B 画幅 / C 交付形态 / D 段缝）→ 定**动作强度档**（R1/R2/R3）→ 有对白先过语速自检 + 语气位 → 资产锁定 → 分镜 → 按 `★ prompt-feeding-checklist.md` 生成投喂词 → 跑 `validate_prompt.py` 机检 → 过 `quality-gate-review`。

### 🧮 常用指令

`/写剧本` · `/台词诊断` · `/数字资产包` · `/素材形态` · `/接线单` · `/做分镜` · `/语速自检` · `/生成视频提示词` · `/导出工作流参数` · `/情绪曲线` · `/看板` · `/微表情` · `/审查` · `跳过确认，直接出整集`

完整指令路由见 [`short-drama-director/SKILL.md`](short-drama-director/SKILL.md)

---

## 📦 项目结构

```
lixiaoxiao9888-create/manju-laoli-skill/        # V7.5.0-SLIM 精简套装（155 文件）
├── README.md                                   # 本落地页（中文 + English）
├── LICENSE / .gitignore
├── short-drama-director/                       # L0 总控（68 文件 · 48 份规则库 · 机检脚本）
│   ├── SKILL.md                                #   总控路由 + 工作法 + 模块索引
│   ├── references/                             #   48 份专业规则库（含 style-bible 画风锁知识库 8 份）
│   ├── scripts/                                #   check_package / validate_prompt / gate 等机检全家桶
│   └── README.md / LICENSE / CHANGELOG.md
├── sd-decision-engine/                         # L1 决策层（情境映射 E01~E15）
├── sd-recon-engine/                            # L2 生产层 · 素材采风
├── sd-script-engine/                           # L2 · 剧本（国内剧 + 外来剧本润色）
├── sd-asset-engine/                            # L2 · 资产锁定
├── sd-storyboard-engine/                       # L2 · 文戏分镜 + 故事板图
├── sd-combat-engine/                           # L2 · 通用打戏
├── sd-xuanhuan-engine/                         # L2 · 玄幻仙侠打戏
├── sd-real-engine/                             # L2 · 真人写实打戏
├── sd-feed-engine/                             # L3 交付层 · 投喂（投喂层闸门）
└── sd-qc-engine/                               # L3 · 质检 / 连续性 / 声音设计
```

---

## 📜 更新历史

- **V7.5.0-SLIM 精简版**（本轮）— **瘦身**：删去海外剧剧本（`sd-overseas-engine`）与解说叙事（`sd-jieshuo-engine`）两个子技能、赛道分流唯一权威文件（原 `references/` 下，已删）、〇·0 赛道分流锁，子技能 **12 → 10**、六道锁 → **五道锁**；判据体系一条未改（详见 `CHANGELOG.md` 沿革）。
- **历史补丁 V7.4.26 P14**（2026-11-03，`CHANGELOG.md` 存档）— **案例示例整体剔除 + 判据级去重 + 文档瘦身**：删除全部成稿示例（4 份示例文件 + 30 余处正文示范段 + 填写示例），只留规则、公式与反例约束；`gate_check.py` 与 `validate_prompt.py` 的重复判据合并为单一实现（同一语气位/镜长/七段缺栏不再查两遍），出稿质检从三跑变一跑；README / CHANGELOG / 补丁说明全部精简。
- **V7.4.26 补丁 P13 及更早** — 见 [`short-drama-director/CHANGELOG.md`](short-drama-director/CHANGELOG.md)（V7.4.26 系列全文保留，更早版本压成一行摘要表）。
- 旧版归档：[**manju-laoli-skill-legacy**](https://github.com/lixiaoxiao9888-create/manju-laoli-skill-legacy)

---

<div align="center">

---

# 🇬🇧 English Overview

## **V7.5.0-SLIM Slim Suite** · Short-Drama Director Suite

**An industrial, full-pipeline creation skill package for AIGC audiovisual works — from concept lock-in to video-model feed prompts — built for AI agents / LLMs to call directly. One router + 12 sub-skills across a four-layer architecture.**

![Pipeline](https://img.shields.io/badge/Pipeline-Asset--First-6a5acd)
![Structure](https://img.shields.io/badge/Structure-1%20router%20%7C%2010%20sub--skills-8e44ad)
![Models](https://img.shields.io/badge/Models-Seedance%202.5%20%7C%202.0-9d4edd)
![QC](https://img.shields.io/badge/QC-C1~C41-ff6b6b)
![Platforms](https://img.shields.io/badge/Platforms-OpenClaw%20%7C%20Coze%20%7C%20Dify%20%7C%20WorkBuddy-00b4d8)

### 🎥 Production Pipeline

```
📋 Lock-in → ✍️ Gated Screenwriting → 🖼️ Asset Locking → 🎬 Dual-mode Storyboard → 🚀 Prompt Packaging → ✅ QC → 🖥️ Offline Board
```

</div>

---

## 🧭 What This Is

An **AIGC creation rulebase for AI agents** (OpenClaw Skill / Agent skill package). **It is a multi-skill suite — 1 router** (`short-drama-director`) **+ 10 sub-skills** (`sd-*-engine`) **across four layers.**

> **Core idea:** "**The user sees 5 steps; the AI runs 100 rules.**" The user only decides ① what to make ② where it comes from ③ model ④ aspect ratio ⑤ desired output — locks, routing, sub-skill mounting, and linting are all handled internally. Sub-skills are never called by hand.

It turns AIGC audiovisual creation into a reusable industrial pipeline, solving three things:

1. **No drift** — characters / scenes / props are **locked first, then storyboarded** (Asset-First);
2. **No rework** — **five front-end locks + a pre-feed checklist + independent P0–P2 gates + shot-level lint** stop errors before generation;
3. **Feed-ready** — outputs a structured **7-section** prompt you can copy straight into the video model.

> 🔑 **The package holds no images**: it delivers "**prompts + a wiring sheet**". Images are generated and held by the user on external platforms. Assets are graded by **existence form** — **M0 prompt-only / M1 numbered slots (default) / M2 registered** — declared on the first line of every delivery.

## 🎯 Use Cases

Genre-agnostic: anything that goes **script → storyboard → video-model feed** fits.

- **AI short dramas / animated shorts / short-form series** (the densest use case)
- **AI commercials / brand films / concept films**
- **Storyboard previsualization (PREVIS)** · **action & fight choreography design**
- **Emotional & micro-expression work** (FACS expression engineering)
- Any AI video production needing **cross-shot character consistency**

## 🧩 Four-Layer Architecture (1 router + 10 sub-skills)

| Layer | Skill | Role |
|:---:|:---|:---|
| **L0 Router** | `short-drama-director` | Material sourcing · **asset existence form M0/M1/M2** · lock system · **48 rulebooks** (incl. 8 in `style-bible/`) · 7-section format · lint **C1~C26** (+ incremental C27–C41) · P0–P2 gates · ★blocking direction · ★asset-delivery modes |
| **L1 Decision** | `sd-decision-engine` | Situation mapping E01–E15 + 80/15/5 weight + emotional anchors + composition minefield whitelist — answers "what shot should this scene use?" |
| **L2 Production** | `sd-recon-engine` | Reference sourcing & benchmark intel (delivers only a 《Benchmark Card》) |
| | `sd-script-engine` | Screenwriting & novel adaptation (6-stage chain + 5-seat roundtable review + 7-dimension dialogue diagnosis + humanizing engine + external-script polish layer) |
| | `sd-asset-engine` | Asset locking (3 checklists · scene continuity · prop single-instance lock · crowd direction) |
| | `sd-storyboard-engine` | Drama/日常 storyboarding (★storyboard sheet · plot-deduction grid · in-segment linking) |
| | `sd-combat-engine` | General fight storyboarding |
| | `sd-xuanhuan-engine` | Xianxia/fantasy fight (golden granularity · bidirectional offense · closed-loop endings) |
| | `sd-real-engine` | Live-action fight (R1 restrained tier · 11-link power chain · real combat techniques) |
| **L3 Delivery** | `sd-feed-engine` | Output modes A/B/C + **feed-layer gates** (gate 6 = numbering + asset-form consistency) + material mapping + 《wiring sheet》 + multi-segment joining |
| | `sd-qc-engine` | Final QC & continuity (consistency ledger · editing/transitions · sound design · music & BGM cue sheet · lint) |

## 🔒 Five Front-End Locks + Style Lock (all must be offered for the user to choose)

| Lock | Options | Note |
|:---:|:---|:---|
| **〇·1 Sourcing** | ① original ② adaptation ③ benchmark ④ trend | First lock, before any creation; ③④ mount `sd-recon-engine` |
| **A Model** | Seedance 2.5 / 2.0 | Choose one; syntax contracts split fully |
| **B Aspect ratio** | 16:9 / 9:16 / 21:9 | Locked together with the model version |
| **C Delivery form** | ① offline board ② md ③ both | ★ Mandatory; unspecified = stop and ask |
| **D Seam joining** | ① held end-frame ② camera swap ③ empty shot ④ creative transition | Four-way choice for multi-segment work |
| **I Style** | pick from a candidate card (incl. "go with your recommendation") | Style card frozen once chosen |

> ⚠️ If any lock is unspecified, the system **must stop and offer the options** — no skipping, no inferring. Action-intensity tiers: `R1 restrained` / `R2 commercial (default)` / `R3 fantasy`.

## 🔥 Capabilities

| Stage | Capability | Description |
|:---:|:---|:---|
| 📥 **Recon** | Benchmark intel | Tiered sources · 4-step recon · 13-field 《Benchmark Card》 · six evidence disciplines |
| ✍️ **Script** | 6-stage chain | Sourcing → IP & characters → dev bible → episode planning → script → 5-seat review |
| 📈 **Emotion** | 12-beat curve | Tension 0–10 + chart script |
| 🎙️ **Dialogue** | 7-dim + speed + tone | Structured `台词：【角色（语气）："…"】` for both 2.0 and 2.5 |
| 🖼️ **Assets** | Asset-First pack | Character/scene/prop assets · CHR/AUD/PRP/SCN/Uxx ledger · A0–A3 triggering |
| 🎥 **Space** | Stance line + grading | 4-element stance declaration + axis lock + movement chains; S0–S4 |
| 🎬 **Storyboard** | Dual-mode + sheets | Dialogue micro-expression / action PREVIS; ★storyboard sheet · deduction grid |
| ⚔️ **Fight** | Three engines | General / xianxia / live-action — domain-specialized |
| 🚀 **Prompts** | 7-section | 【Style】→…→【Hard Negatives】 |
| 🚫 **Negatives** | Three rewrites | Models are insensitive to negation, sensitive to word roots |
| ✅ **QC** | Gates + lint | `validate_prompt.py` **C1~C26** (104 sub-codes; incremental C27–C41); feed-layer **gates** |
| 🖥️ **Board** | Offline storyboard | Project md → single-file HTML; export SRT / timeline CSV / API JSON |
| 🎵 **Sound** | Music & sound design | BGM cue sheet / search terms / AI music prompts / copyright check |
| 🛡️ **Compliance** | Safety dictionary | Rewrites gore into shockwave / spark / freeze-frame language |

## 🖥️ Platforms & Models

| | Support |
|---|---|
| **Agent platforms** | OpenClaw · WorkBuddy · Doubao Agent / Coze · Dify, plus generic LLMs |
| **Video models** | **Seedance 2.5 / 2.0** (mandatory choice); Jimeng = secondary / legacy |
| **Outputs** | 7-section feed prompts · Canvas / API payloads · offline board · emotion curve |

---

## ⚙️ Quick Start

> 📦 **Deploy (multi-agent suite):** the repo root holds 1 router (`short-drama-director/`) + 10 sub-skills (`sd-*-engine/`) side by side. On multi-skill platforms (e.g. OpenClaw) deploy all 13 directories at the same level; the main entry is `short-drama-director`.

```bash
# Install into OpenClaw
openclaw skills install ./short-drama-director --as short-drama-director

# Package lint (51 rulebooks, static + semantic regression)
python3 short-drama-director/scripts/check_package.py

# Ship check — ONE run covers feed-layer gates + all C-series lint (zero FAIL to ship)
python3 sd-feed-engine/scripts/gate_check.py <script>.md --model 2.5 --aspect 16:9

# Contract reconciliation (what must be delivered vs what was delivered)
python3 short-drama-director/scripts/audit_contract.py <script>.md

# Project md → single-file offline board
python3 short-drama-director/scripts/build_board_lite.py <project.md>
```

**Minimal agent sequence**: read `SKILL.md` → complete the **six front-end locks + style lock** → pick action tier (R1/R2/R3) → dialogue speed check + tone slot → lock assets → storyboard → generate feed prompts → pass `validate_prompt.py` → pass `quality-gate-review`.

## 📦 Structure

```
lixiaoxiao9888-create/manju-laoli-skill/        # V7.5.0-SLIM slim suite (155 files)
├── README.md                                   # landing (Chinese + English)
├── LICENSE / .gitignore
├── short-drama-director/                       # L0 router (68 files · 48 rulebooks · lint scripts)
├── sd-decision-engine/                         # L1 decision (E01–E15)
├── sd-recon-engine/                            # L2 · sourcing
├── sd-script-engine/                           # L2 · scriptwriting
├── sd-asset-engine/                            # L2 · asset locking
├── sd-storyboard-engine/                       # L2 · storyboard + storyboard sheets
├── sd-combat-engine/                           # L2 · general fight
├── sd-xuanhuan-engine/                         # L2 · xianxia fight
├── sd-real-engine/                             # L2 · live-action fight
├── sd-feed-engine/                             # L3 delivery · feed (feed-layer gates)
└── sd-qc-engine/                               # L3 · QC / continuity / sound
```

---

## 📜 Changelog

- **V7.5.0-SLIM** — **slim build**: overseas-drama and explainer-narration tracks **removed** (2 engines + track-routing authority + 〇·0 routing lock), leaving 1 router + 10 sub-skills; all criteria unchanged. Details (历史沿革) in `CHANGELOG.md`.
- **历史 patch V7.4.26 P14** (2026-11-03, archived in `CHANGELOG.md`) — **all worked examples removed + criteria de-duplicated + docs slimmed**: every full-length sample script, inline demo block and fill-in example is gone (rules, formulas and counter-examples stay); duplicated checks in `gate_check.py` vs `validate_prompt.py` merged into a single implementation, so shipping a script now needs one check run instead of three; README / CHANGELOG / patch notes compacted.
- **V7.4.26 patch P13 and earlier** — see [`short-drama-director/CHANGELOG.md`](short-drama-director/CHANGELOG.md).
- Legacy archive: [**manju-laoli-skill-legacy**](https://github.com/lixiaoxiao9888-create/manju-laoli-skill-legacy)

---

<div align="center">

## 📄 License

**MIT** · For creative & learning use; comply with platform content policies

**Made with ❤️ for AIGC Creators**

</div>

---

## 🙌 贡献者与团队

感谢参与产品设计、开发、测试、内容与社区建设的成员：

<table>
<tr>
<td width="50%" valign="top">
  <img src="https://github.com/lixiaoxiao9888-create.png?size=64" alt="老李" width="56" align="left">
  <strong>老李<br><sub>项目发起者 · 总编导 · 微信：lisenlin998</sub></strong><br>
  <a href="mailto:lixiaoxiao9888@gmail.com">lixiaoxiao9888@gmail.com</a><br>
  <em>用作品说话。</em>
  <br clear="left">
</td>
<td width="50%" valign="top">
  <img src="https://github.com/coco38622.png?size=64" alt="evo" width="56" align="left">
  <strong>evo<br><sub>格式支线贡献者 · GitHub：coco38622</sub></strong><br>
  <a href="https://github.com/coco38622">@coco38622</a><br>
  <em>让格式支线与官方文档逐字对齐。</em>
  <br clear="left">
</td>
</tr>
<tr>
<td width="50%" valign="top">
  <strong>JY<br><sub>子技能规范贡献者</sub></strong><br>
  <em>好故事，不分国界。</em>
  <br clear="left">
</td>
<td width="50%" valign="top">
  <em>虚位以待 —— 期待你加入。</em>
</td>
</tr>
</table>


## V7.5.0-SLIM 稳定性能力与边界

新增完整章节分页、JSON/text 统一门禁、多对白累计及 JSON 单源导出。使用单源项目时必读 `short-drama-director/references/project-bundle-contract.md`。导出仅含资产提示词与 P3CLEAN_GRID 计划；不是已生成图片，也不是已经过 P4 模型适配的投喂稿。旧示例回归和未解决项见包外交付说明，不以机检 PASS 代替语义与实拍验收。
