# 漫剧老李 AIGC 全流程 Skill · V6.8 轻量版（Short-Drama Director Suite）

面向竖屏短剧、AI 漫剧、短视频剧集全生命周期的工业级导演总控技能包，供 AI 助手 / LLM 调用。
覆盖：**Asset-First 六阶段管线**（立项锁定 → 五阶门控剧本 → 数字资产包 → 分镜 → 视频提示词渲染 → 独立质检）。

> 🔑 **核心理念：资产图先于分镜。** 角色/场景/道具在 P2 数字资产包阶段完成**出图并锁定**（非文字描述），成为《资产图册》唯一权威事实来源，分镜/投喂一律引用已锁定 @资产图。

> **品牌**：漫剧老李 AIGC 全流程 Skill
> **版本**：V6.8 轻量版（Lite）Multi-Agent（V6.7 基座 + 2026-09-15 定向修订：移除可灵正式支持 / 角色 4 View 统一 / 格式命名统一 / 空间 S0~S4·资产 A0~A3·FACS 分级按需触发 / LEGACY 清理，38 份规则库）
> **技术标识**：`short-drama-director`（OpenClaw 命令路由用，保持不变）

> ⚠️ 本包是 **给 AI 助手执行的规则库**（OpenClaw Skill / Agent 技能包），不是面向消费者的成品剧本。
> 把 `SKILL.md` 与 `references/` 一起放入你的 Agent 技能目录即可使用。

---

## ✨ 能力总览

| 阶段 | 模块 | 功能 |
|---|---|---|
| 管线 | `asset-first-pipeline` | **Asset-First 六阶段（★权威）**：P0~P5 唯一生产顺序，资产图先于分镜（A0~A3 按任务复杂度分级触发） |
| 画幅 | `aspect-ratio-adaptation` | **画幅自适应路由（★权威）**：横/竖屏全流程裁决，用户指令优先 |
| 平台 | `agent-platform-adapters` | 多 Agent 平台适配（OpenClaw/WorkBuddy/豆包Coze/Dify）+ 豆包 JSON 分块 |
| 剧本 | `screenplay-gate-engine` | 五阶门控（前提/结构/节拍/世界观/专业排版） |
| 台词 | `dialogue-doctor-7d` | 台词七维诊断与三段式重构 |
| 台词 | `dialogue-speed-check` | **强制语速自检**（三档语速/五步流程/拆镜） |
| 资产 | `asset-spatial-ledger` | A/B/C 分级资产锁 + **分批出图执行规范（角色 4 View 资产板/场景/道具）** + 3D 空间快照 + 空间站位 S0~S4 分级 |
| 资产 | `character-lineage-and-sheets` | 角色资产板 + T1→T2→T3 亲缘推导**直接出图** |
| 台账 | `production-ledger-handbook` | 《剧组资产图册》CHR/AUD/PRP/SCN/Uxx + **资产参考图** 工业化台账 |
| 情绪 | `emotion-beat-curve` | 12 节拍全片情绪张力量化 + 可视化曲线 |
| 空间 | `spatial-topview-camera` | 2x2 顶视图机位调度（CAM1~4）+ 180° 轴线 |
| 分镜 | `action-previs-15grid` | 15 秒打戏完播潜力评分 + R1/R2/R3 三档 + 11 环动力链 |
| 分镜 | `xuanhuan-magic-combat` | **玄幻法术战斗（R3专用）**：法宝/五行术法/术法攻防/能量具象/对军清场 |
| 分镜 | `combat-direction-engine` / `combat-rhythm-defense3state` / `camera-specs-15rules` | 武打导演引擎 / 机枪节奏防守三态 / 镜头规格 15 铁律 |
| 分镜 | `wenxi-micro-expression` | 文戏情绪六阶段 + 对白保护 |
| 表演 | `★ facs-micro-expression` / `facs-au-dictionary` / `facs-emotion-recipes` | **FACS 微表情引擎**：表情 AU 化（四区拆解/强度三档/真假笑铁律）+ AU 完整字典 + 情绪→AU 配方库（增强模块·按需触发）（增强模块·按需触发） |
| 武学 | `martial-arts-combat-library` / `martial-arts-arsenal` / `authentic-martial-taxonomy` | 23 门武学 + 9 套剑法 + 兵器 + 轻功 + 11 环杀招 |
| 衔接 | `camera-transitions-6types` | 三手法六式镜头衔接 |
| 渲染 | `seedance-render-engine` | 三层解耦提示词模板（16:9 / 9:16，Seedance 2.5 / Seedance 2.0 强制二选一） |
| 适配 | `model-adapters` / `comfyui-canvas-automation` | 闭源模型参数适配 + Canvas/API 工作流对接 |
| 合规 | `platform-safety-compliance-guide` | 安全风控转译词典（降低风险，不承诺 100% 通过） |
| 质检 | `quality-gate-review` | P0/P1/P2 独立门禁 + 声音相对电平 + **改动后复验铁律（三步闭环 + 改动复验报告）** |
| 看板 | `storyboard-board-lite` | **轻量离线分镜看板**（md → 单文件 HTML，双击即开；P2.5 出图提示词与 P4 投喂提示词必同板） |
| 空间 | `spatial-reference-system-V3` | 空间参考系统 V3 原文（**备查**：默认不用一行式站位声明，仅超复杂群像时取法） |

完整模块清单与权威文件路由见 `SKILL.md`。

---

## 🚀 快速开始（给 AI 助手）

1. 读取 `SKILL.md`，按“六步工作法”执行——**先完成 A 锁（模型版本 Seedance 2.5/2.0 强制二选一）与 B 锁（画幅 16:9/9:16/21:9）才动笔，未指定不动笔**；
2. 先定**动作强度档**：`R1 写实克制` / `R2 商业高燃（默认）` / `R3 玄幻大招`；
3. 有对白 → 先过 `dialogue-speed-check` 语速自检；
4. 查 `model-adapters` 当前平台能力；
5. 直投公开平台 → 走 `platform-safety-compliance-guide` 安全默认档转译；
6. 交付前过 `quality-gate-review`。

## 🧮 常用指令（SKILL 内注册）

`/写剧本` · `/台词诊断` · `/拆资产` · `/做分镜` · `/语速自检` · `/生成视频提示词` · `/看板` · `/微表情` · `/审查` · `跳过确认，直接出整集`

---

## 📦 安装

```bash
# OpenClaw
openclaw skills install ./short-drama-director --as short-drama-director
```

其他 Agent 框架：把整个目录放入技能目录，并在系统提示中引用 `SKILL.md`。

## 🧹 质量自检

仓库内置 `scripts/check_package.py`：

```bash
python3 scripts/check_package.py
```

检查：SKILL frontmatter 完整性、references 清单、语义回归（可灵残留 / 4 View 口径 / Prompt 格式命名 / LEGACY 标记 / README-SKILL 版本一致）。

---

## 🧱 结构

```
short-drama-director/
├── SKILL.md                     # 总控路由 + 工作法 + 模块清单
├── references/                  # 38 个专业规则库
├── scripts/
│   ├── check_package.py         # 静态自检脚本
│   ├── build_board_lite.py      # 轻量离线分镜看板编译器（md → 单文件 HTML）
│   └── generate_emotion_curve.py# 12 节拍情绪曲线绘制脚本
├── README.md
├── LICENSE
└── CHANGELOG.md
```

## 📄 License

见 [LICENSE](./LICENSE)。

## 🙏 致谢与使用约定

- 本包整理自 AI 短剧/漫剧工业化生产实践，供创作学习使用；
- 涉及真实武术流派、历史地点仅作创作参考；
- 输出内容需自行遵守所在平台的内容规范与版权要求。
