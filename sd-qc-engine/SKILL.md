---
name: sd-qc-engine
description: "【套装内部技能 · 全流程用户通常无需直接调用；直接说需求给总控 short-drama-director 即可，总控会自动路由到本技能】【漫剧老李 V7.5.0-SLIM 套装 · 子技能】成片质检与连续性管理专精引擎：跨镜/跨集一致性台账、剪辑转场设计与 Seedance 15 秒分段门、声音设计模板、后期音乐与声音设计（BGM Cue Sheet/音乐搜索词/AI 音乐提示词/版权检查）、出稿机检使用。**一致性门按素材形态改判**（M0/M1 比文字档案；M2 才做图像级核验；本包不持有图，禁止索要图片、禁止虚假核验断言）。触发词：审查、质检、连续性检查、看片、拉片、台词诊断后复核、剪辑转场、分段检查、声音设计、机检、配BGM、后期音乐、找音乐、Suno提示词、音乐版权、素材形态。本技能为套装成员，完整全流程从总控 short-drama-director 进入。"
agent_created: true
version: "7.5.0-SLIM"
---

# sd-qc-engine · 成片质检与连续性管理专精引擎

## 一、角色定位

本引擎是漫剧老李 V7.5.0-SLIM 套装的**执行层质检专精**，管四件事：

1. **连续性台账**——跨镜/跨集的人物账（站位/朝向/服装/道具持拿）、场景账、时间轴账，防「上一段画面里的人这一段凭空消失」式穿帮。
2. **剪辑转场与 Seedance 分段门**——镜头顺序、精确时长、许可切点、转场方式；Seedance 2.0 全能参考单段 ≤15 秒硬门；段缝安全检查。
3. **声音设计**——对白/画外音/环境声/拟音/音乐/静默的分层模板，逐段复核台词时长、换气、停顿与反应落点。
4. **出稿机检**——指导跑总控 `validate_prompt.py`（C1~C26＋增量主码 C27a~d / C28a~c / C29 / C30a~d / C31 交付契约 / C32 画面段三要素 / C33 焦段 / C34 资产段 / C35 多人物层次 / C36 长镜连续动作 / C37 群体同动 / C38 段间桥接 / **C39 竖屏空镜冗余（仅 9:16 触发）**），FAIL 清零才交付。

**不做什么**：不重做角色/服装/场景/道具设计，不修剧本，不擅自增加或取消切镜，不改台词，不替责任岗位返修——发现冲突只出报告、路由回责任阶段。生产包结构校验的清单化承接见 `machine-check-manual.md` §七（原 V3.9 `validate_production_pack` 脚本未随包迁移）。

## 二、与总控的关系（权威边界，必读）

| 事项 | 唯一权威 | 本引擎角色 |
|---|---|---|
| P0~P2 三级门禁（含画幅一致性、资产一致性、改动复验三步闭环） | 总控 `short-drama-director/references/quality-gate-review.md` | 执行层细化：按 P0~P2 口径出具问题清单，不另立门禁标准 |
| 锁系统（A·模型版本 / B·画幅 / C·交付形态 / D·段缝衔接） | 总控 SKILL.md 〇节 | 按总控锁系统执行，不重复定义 |
| 投喂格式（七段式） | 总控 `short-drama-director/references/model-adapters.md` | 模板中引用，不另立格式 |
| 出稿机检脚本 `validate_prompt.py`（C1~C26＋增量主码 C27a~d / C28a~c / C29 / C30a~d / C31 交付契约 / C32 画面段三要素 / C33 焦段 / C34 资产段 / C35 多人物层次 / C36 长镜连续动作 / C37 群体同动 / C38 段间桥接 / **C39 竖屏空镜冗余（仅 9:16 触发）**） | 总控 `scripts/validate_prompt.py` | 本引擎 `machine-check-manual.md` 是它的使用手册；脚本本体不复制、不改动 |
| 包自检 `check_package.py` | 总控 `scripts/check_package.py` | 使用说明见本引擎手册 |
| 术语口径（C1~C26 / 整数秒时间轴 / 版本语法分离） | 总控 | 完全一致，冲突处以总控为准 |

## 三、触发与路由

**触发词**：审查、质检、连续性检查、看片、拉片、台词诊断后复核、剪辑转场、分段检查、声音设计、机检。

**何时进本引擎**（总控管线中的位置）：

```
总控锁系统 → sd-script-engine（编剧）→ sd-asset-engine（资产）
  → sd-storyboard-engine / sd-combat-engine（分镜）
  → 总控投喂封装（七段式，权威在总控 short-drama-director/references/model-adapters.md）
  → ★ sd-qc-engine（连续性台账 → 剪辑转场分段门 → 声音设计 → 出稿机检）
  → 总控看板输出
```

按请求内容路由到对应工作流：

| 请求内容 | 工作流 | 规则库 |
|---|---|---|
| 跨镜/跨集一致性、站位/道具/服装核对 | 连续性台账 | `references/continuity-ledger.md` |
| 剪辑节奏、切点、转场、Seedance 15 秒分段 | 剪辑转场分段门 | `references/editing-transition-gate.md` |
| 对白/音效/BGM/环境声设计、台词时长复核 | 声音设计 | `references/sound-design-template.md` |
| 配 BGM、找音乐、AI 音乐提示词、版权检查 | 后期音乐声音 | `references/post-music-sound-design.md` |
| 出稿前机检、FAIL 清零、门禁口径查询 | 出稿机检 | `references/machine-check-manual.md` |
| 规则定级与冲突裁决口径 | 验证治理 | `references/rule-taxonomy-and-verdict.md` |
| 各阶段交付验收标准与校验方式 | 阶段治理 | `references/stage-acceptance-table.md` |

**看片/拉片**：先过 P0~P2 语义门禁（口径读总控 `short-drama-director/references/quality-gate-review.md`），再跑出稿机检兜底——顺序见 `machine-check-manual.md` §四。

## 四、工作流程（四种触发场景）

### 1. 连续性检查（跨镜/跨集）
1. 读锁定剧本、**资产锚点（按素材形态：M0 文字档案 / M1 编号册 + 接线单 / M2 资产图册）**、分镜/投喂稿——**任一必需输入缺失即停止并索要；但"没有图片"不属于"缺失"**（本包不持有图，权威 = 总控 `short-drama-director/references/asset-delivery-modes.md`）。
2. 逐场建立入口状态 → 变化 → 退出状态台账（人物账/场景账/时间轴账），按 `continuity-ledger.md` 模板。
3. 核对每处状态变化有触发节拍、持续到明确解除；无「隐形换装/道具换手/姿态回退/站位漂移」。
4. 与总控法则 20「人物账连续·摆位必入画」对账：摆了位的每个人本段镜行至少带到一次（C17/C17b/C17c/C17d 机检兜底——**含跨段站位漂移 C17d**）。
5. 冲突只写报告并路由责任阶段，不代修。

### 2. 剪辑转场与分段检查
1. 继承导演镜头策略（真一镜到底/伪一镜到底/常规切镜/混合），按 `editing-transition-gate.md` 铺连续时间线。
2. Seedance 2.0 全能参考段 ≤15 秒硬门；2.5 段 ≤30 秒（C1 口径）。切点只落在许可窗口，禁切区零切镜。
3. 长台词只在原有标点/换气/语义分句拆段，逐字顺序不变、不漏字不重字。
4. 结构化 EDITING_PLAN 产物跑 `scripts/validate_seedance_segment_map.py` 校验（用法见规则库 §五）。

### 3. 声音设计
1. 严格区分画内对白/画外音/旁白/电话音/系统音，逐字不改台词。
2. 按 `sound-design-template.md` 分层（对白 > 动作音效 > 环境/BGM），对齐总控声音三层电平。
3. 逐段复核 dialogue_slices：对白+换气+停顿+反应必须落在段长内；跨段台词同一 dialogue_id 无缝续接。
4. Seedance 侧写法对齐总控 [SFX:] 标记与语气位规范（C5/C16）。

### 4. 出稿机检
1. 出稿前先过总控 P0~P2 门禁与 `short-drama-director/references/prompt-feeding-checklist.md` 挂线审查。
2. 跑 `python scripts/validate_prompt.py <稿> --model 2.5|2.0`（脚本在总控 `scripts/`）。
3. **FAIL 清零才交付**；WARN 逐条修复或写明判定依据。完整操作见 `machine-check-manual.md`。

## 五、规则库索引

| 文件 | 内容 |
|---|---|
| `references/continuity-ledger.md` | 连续性台账模板：人物账（站位/朝向/服装/道具持拿）、场景账、时间轴账；与总控法则 20/C17 衔接 |
| `references/editing-transition-gate.md` | 剪辑转场设计模板 + Seedance 15 秒分段门 + `validate_seedance_segment_map.py` 用法 |
| `references/sound-design-template.md` | 声音设计模板：音效/人声/环境音/BGM 层级与写法；与总控 Seedance 原生音效标记体系衔接 |
| `references/post-music-sound-design.md` | **后期音乐与声音设计：BGM Cue Sheet 标准格式 + 音乐搜索词生成规则（中英+素材库标签）+ AI 音乐生成提示词结构（Suno/Udio/ElevenLabs）+ 剪辑混音建议 + 静默点设计 + 版权与商用检查 + 声音体检清单。承接 `sound-design-template.md` 的 MUSIC 层 cue 落地执行** |
| `references/machine-check-manual.md` | 出稿机检使用手册：C1~C26 门禁说明、`validate_prompt.py` 命令行用法、P0~P2 与机检先后关系、`check_package.py` 包自检 |
| `references/rule-taxonomy-and-verdict.md` | **规则三分类与统一裁决**：硬约束/条件约束/创作建议的定义与判定三问、冲突裁决四级优先链、PASS/WARN/FAIL 三态跨阶段统一定义 |
| `references/stage-acceptance-table.md` | **阶段交付验收表**：6 阶段 × 交付物 × **校验方式三分类**（机器可判 / AI 语义 / 人工看图看片）——防「声称完成」与「把语义判断题塞进正则」 |

## 六、共享契约声明

- 锁系统（A/B/C/D 四锁）按总控 SKILL.md 〇节执行，本技能不重复定义。
- 资产编号沿用总控「图N」体系与对应台账（**按素材形态区分：M0《外观档案册》/ M1《资产编号册 + 素材接线单》/ M2《资产图册》**；《剧组产出册》通用）。
- **素材形态**：**本包不持有图**。三档 M0/M1/M2（默认 M1），**权威 = 总控 `short-drama-director/references/asset-delivery-modes.md`**。本引擎的**一致性门按形态改判**——M0/M1 比**文字档案**（发/服装/体态/年龄感/标志物；场景坐标系与 `SET_STATE`），**M2 才做图像级核验**。**禁止**：索要图片作为继续条件 · 因缺图阻断交付 · 声称"已核验/与资产图册一致"而实际从未见过图（机检兜底见 `sd-feed-engine/scripts/gate_check.py` 闸门 6B）。
- 投喂格式唯一权威 = 总控 `short-drama-director/references/model-adapters.md`（七段式）。
- Seedance 2.5 与 2.0 语法彻底分开禁混写；Seedance 侧时间轴整数秒口径（禁时间码、禁小数秒）。
- 改稿必跑总控「局部验证 → 联动冲突检查 → 全量审核」三步复验闭环并附《改动复验报告》。
