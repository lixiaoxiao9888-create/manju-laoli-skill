# 五席圆桌审核制与叙事连续性

> 精编自《灵境AI剧本改编 skill》（6阶段编剧链）

本文件覆盖阶段⑥五席圆桌审核制的全部规范（五席角色与协议、评分等级与门禁、市场基准、交付模板），以及三个配套契约：叙事连续性与反碎片化、单集独立开场与相邻集过桥契约、全上下文深读与权威顺序（供精修阶段执行）。

# 第一部分 · 五席圆桌审核制

## 1.1 核心结果

把「大家觉得好不好看」变成可追溯的批次质量门。每批必须先取得五份互相独立的审读意见，再讨论分歧和计算综合结论；不能让五个席位重复同一个答案，也不能用平均分掩盖来源跑偏、故事断裂或合规风险。

圆桌只判断剧本层竞争力。`S` 表示具备强爆款剧本潜力，不表示已经成为爆款；实际表现仍取决于演员、导演、制作、宣发、分发、档期和观众数据。

所有最终报告必须写入边界常量：`SCRIPT_LEVEL_POTENTIAL_NOT_PERFORMANCE_PREDICTION`。

## 1.2 门禁与输入

只消费已经完成阶段⑤基础校验的连续批次：

- 本批所有干净 `EP###_SCRIPT.md`
- `SCRIPT_SET_MANIFEST.json`
- `SERIES_SCRIPT_STRATEGY.md`
- `SOURCE_ADAPTATION_MAP.md`
- `SOURCE_DIALOGUE_LEDGER.md`
- `CONTINUITY_LEDGER.json`
- 对应的IP、故事圣经与分集版本
- 上一批末集和下一集分集卡

若剧本文件缺失、版本不一致、阶段⑤失败标记非空或本批不是连续集数，输出 `BLOCKED_REPORT`，不先打分。

`STEPWISE` 与 `FULL_SCRIPT_PIPELINE` 都在每批评审结束后停止。`S/A/B/NOT_READY` 只决定推荐动作，不自动继续，也不自动返修。所有等级统一写 `decision: AWAITING_USER_DECISION`，等待用户明确选择：

1. `PROCEED_CURRENT`：接受当前版本，进入下一批或下一阶段。
2. `REFINE_OR_REWRITE`：交给独立精修/重写阶段，只生成一个新正式版本后再开下一轮评审。

`B/NOT_READY` 选择继续时必须另外记录质量风险接受；不得因此把等级改成 `A/S`。

## 1.3 固定五席

五席不得合并，全部属于 `AI_ROLE_SIMULATION`，必须显式标注。没有真实用户样本时，不得写「真实观众一致认为」。

### EDITOR-01 故事主编（权重 25%）

优先回答：

- 小说事实、人物动机、关系责任和关键台词功能是否保真。
- 批次能否用「因为—但是—于是—结果」连续复述。
- 每集是否有目标、反制、换策、代价和局部结果。
- 人物弧、关系弧、知识边界、时间和钩子是否累积而非复位。
- 删除或重排是否损伤后续因果。

不得因为「更刺激」宽恕来源跑偏。

### EDITOR-02 商业主编（权重 25%）

优先回答：

- 前10秒是否有可见爆点、人物处境、行动问题和紧迫性。
- 冲突是否升级，主角是否主动，反派或环境是否有效反制。
- 爽点、笑点、甜点、虐点、燃点或悬念是否完成建立、延迟、见证和兑现。
- 集尾是否在局部支付后留下具体下一动作。
- 同一冲突公式、羞辱方式和钩子类型是否过度重复。
- 卖点是否能用一句具体故事表达，而不是题材标签。

不得把吵闹、打脸次数或反转数量直接当作节奏。

### VIEWER-01 题材核心观众（权重 17%）

按项目目标受众和题材替换具体画像，但职责固定：判断类型期待、角色喜爱、情绪回报、名场面潜力和追更欲。必须说明「期待被满足/被破坏」的具体位置。

### VIEWER-02 信息流新观众（权重 17%）

假设没有看简介和上一集。重点记录：前10秒能否知道谁遇到什么麻烦；人名、关系、时空和规则是否一次可懂；哪一处必须倒回去看；哪一处会划走；单集结束能否复述主要事件和所得。

### VIEWER-03 连刷挑剔观众（权重 16%）

假设已经连续看过上一批。重点记录：上集结尾是否由本集第一动作支付；信息、关系、伤势、道具和情绪是否复位；连续三至五集是否重复同一套路；钩子是否按期兑现，是否不断拖答案；本批结束后是否仍信任编剧会支付承诺。

主编的 `continue_intent` 使用 `NOT_APPLICABLE`，另写个人判定 `PASS/REVISE/REWRITE`。

## 1.4 独立评审协议

### 为什么先独立再讨论

圆桌一开始就共享观点，会产生从众、权威压制和重复措辞。五席必须先冻结个人意见，再进入讨论。每份个人表都记录输入快照版本；看到他人意见后形成的新判断只能写入圆桌讨论，不能反改个人原始分。

### 个人表最低证据

每席必须提供：

- 一句话复述本批故事。
- 最强三点与最弱三点。
- 至少三条集号、场号和正文短语证据。
- 最想继续看的位置、最可能弃剧的位置和原因。
- 十维分数、个人总分、继续观看意愿。
- 可直接改写的三项建议。

证据使用短语或动作概述，不长篇复制剧本：

```yaml
evidence:
  - episode_id: EP006
    scene_id: EP006-SC02
    quote_or_action: "角色把唯一证据交给对手"
    finding: "该动作支付了前两集建立的信任成本"
```

批评与优点都必须定位；仅写「总体流畅」「节奏偏慢」不计入有效意见。

### 独立性检查

出现以下情况应重做个人审读：五份报告段落结构和结论完全同序；三名观众使用主编术语而没有观看体验；所有人选择同一最强点、最弱点，却没有各自证据；个人分数在圆桌后被统一修改；观众声称代表真实用户群体或引用不存在的数据。

### 讨论规则

圆桌主持只做四件事：1. 合并重复发现；2. 要求无证据判断补证；3. 并列冲突意见并寻找适用条件；4. 根据固定公式计算结论。

主持人不能新增第六个评分席位，也不能用「综合考虑」随意改分。最终报告保留少数意见和未解决分歧。

## 1.5 每批八步评审

### 1. 冻结输入快照

记录剧本版本、批次、集数、文件哈希、上游版本、市场基准日期和评审轮次。返修后必须产生新快照和新轮次，不得覆盖旧意见。

### 2. 独立审读

五席分别只读干净剧本，再按需核对审稿层。任何席位在提交个人表前不得读取其他席位的分数、结论或建议。

### 3. 硬门检查

先检查来源权威、故事完整、相邻连续、单集理解、钩子兑现、价值与合规六项硬门。任一失败，综合等级只能是 `NOT_READY`，不得靠高爽点分拉回。

### 4. 证据合并

把相同问题合并，把相反意见并列。每个结论必须回答「哪一集、哪一场、哪段动作或台词导致这个判断」。「节奏不够」「不够爽」「人物不讨喜」没有证据时无效。

### 5. 圆桌讨论

依次讨论：

1. 普通观众能否连续复述。
2. 每集是否先支付结果再落钩子。
3. 爽点、笑点、情感或悬念是否有建立、对抗、见证和后果。
4. IP选择和台词是否可辨识。
5. 相邻集与整批是否重复、疲劳或断裂。
6. 相比当前同题材内容，差异化卖点是否来自故事与人物，而非噱头堆砌。

保留少数意见，不强行伪造全票共识。

### 6. 计算综合分与等级

使用固定十维权重和席位权重。综合分只能由个人已冻结分数计算。先判硬门，再判分数和席位下限。输出等级与推荐：

- `S`：强爆款剧本潜力，`PROCEED_RECOMMENDED`。
- `A`：具备平台竞争力，`PROCEED_RECOMMENDED`。
- `B`：基础故事成立但未达到爆款目标，`REFINE_RECOMMENDED`。
- `NOT_READY`：存在阻断问题，`REWRITE_RECOMMENDED`。

推荐不能替代用户选择。任何结果均输出同一组可选动作和回复案例。

### 7. 形成返修任务

按 `P0/P1/P2` 排序：`P0` 来源跑偏、因果断裂、人物失真、时间冲突、钩子失约、合规风险；`P1` 节奏、爽点、主角主动性、台词、开场与集尾不足；`P2` 措辞、表演空间、局部趣味和制作成本优化。

每项写明受影响集数、正文证据、修改目标、不可改变的上游事实和验收方法。圆桌不直接改写剧本。

### 8. 更新批次与全剧评审账本

登记本轮等级、分数、推荐、主要优缺点、用户决策状态和下一次评审入口。审核完成后保持 `AWAITING_USER_DECISION`。只有用户接受当前版本，该批才可锁定；`B/NOT_READY` 还需登记风险接受。用户选择修改时，本轮保持只读，等待新剧本版本开启下一轮独立评审。

## 1.6 评分、等级与返修门禁

### 十维统一评分

每席对十个维度打 `0—10` 分，使用同一权重，便于比较。维度权重合计 100：

| 维度 | 权重 | 核心问题 |
|---|---:|---|
| `source_fidelity` | 12 | 改编是否保留原作事实、动机、关系、规则与关键功能 |
| `story_clarity_completeness` | 13 | 本批与各集是否完整、流畅、能连续复述 |
| `conflict_strategy_progression` | 10 | 目标、反制、换策与代价是否真实推进 |
| `pacing_information_density` | 10 | 是否紧凑但不切碎，信息释放是否恰当 |
| `payoff_satisfaction` | 10 | 爽点/情绪点是否有建立、见证、结果和后果 |
| `hook_next_click` | 12 | 集尾是否具体、可支付、令人必须点下一集 |
| `character_ip_appeal` | 10 | 角色是否鲜活、可爱、可辨识并持续做选择 |
| `dialogue_performance` | 8 | 台词是否像人物争取结果、可演、有潜台词 |
| `standalone_and_continuity` | 8 | 单集可懂与上下集承接是否同时成立 |
| `novelty_market_fit` | 7 | 同题材中是否有来自人物与机制的差异化 |

个人总分：`Σ(维度分 × 维度权重) ÷ 10`。不得先写个人总分再倒推维度分。

### 席位权重与综合分

| 席位 | 权重 |
|---|---:|
| EDITOR-01 | 25% |
| EDITOR-02 | 25% |
| VIEWER-01 | 17% |
| VIEWER-02 | 17% |
| VIEWER-03 | 16% |

综合分：`Σ(个人总分 × 席位权重) ÷ 100`。主编合计 50%，观众合计 50%，避免只顾专业结构或只顾即时刺激。

### 六项硬门

必须分别为 `PASS`：

1. `source_authority`：没有无授权核心改写。
2. `narrative_completeness`：没有碎片化、因果断裂或无局部结果。
3. `adjacent_continuity`：上下集与跨批状态连续。
4. `episode_comprehension`：首看观众能理解人物、困境、目标和结果。
5. `hook_payoff_integrity`：钩子有来源、有支付位置且本批没有失约。
6. `value_and_compliance`：价值表达与内容风险没有阻断性问题。

任一为 `FAIL`，等级直接为 `NOT_READY`。整改后重新开启新一轮评审，不保留原分直接升档。

### 等级定义

**S：强爆款剧本潜力**——同时满足：综合分 90—100；两名主编均不低于 88；五席无人低于 80；至少两名观众为 `MUST_CONTINUE`，第三名不低于 `WILL_CONTINUE`；六项硬门全过；本批没有 P0 问题。推荐 `PROCEED_RECOMMENDED`，仍须等待用户选择。

**A：具备平台竞争力**——同时满足：综合分 80—89.99；两名主编均不低于 78；五席无人低于 70；至少两名观众为 `MUST_CONTINUE` 或 `WILL_CONTINUE`；六项硬门全过。推荐 `PROCEED_RECOMMENDED`。P1/P2 可以由用户选择继续优化；不得自动进入下一批。

**B：基础成立但未达到爆款目标**——综合分 70—79.99，或虽高于 80 但不满足 A 的席位下限/观看意愿；六项硬门全过。推荐 `REFINE_RECOMMENDED`。用户可以选择进行一次精修/重写，也可以明确接受当前质量风险后进入下一步。

**NOT_READY：未达 B 级**——综合分低于 70；或任一硬门失败；或存在来源跑偏、核心因果断裂、严重人物失真、时间不可能、钩子失约或阻断性合规风险。推荐 `REWRITE_RECOMMENDED`。用户仍需明确选择；若接受当前版本继续，必须记录硬伤和风险接受，不得改写等级。

### 统一用户决策门

每次审核无论等级都写：

```yaml
decision: AWAITING_USER_DECISION
allowed_user_actions:
  - PROCEED_CURRENT
  - REFINE_OR_REWRITE
selected_action: NONE
```

固定提示：1. 接受当前版本，进入下一批或下一阶段。回复：`1`。2. 进行一次精修或重写。回复：`2`。

用户未选择前不得路由。`B/NOT_READY` 的 `risk_acceptance_required` 为 `true`，只有用户明确选择 1 并确认风险后才可登记 `USER_APPROVED`。

### 红果同赛道剧本层潜力

只允许：`STRONG_SCRIPT_POTENTIAL`（通常对应 S）、`COMPETITIVE_SCRIPT_POTENTIAL`（通常对应 A）、`BORDERLINE_SCRIPT_POTENTIAL`（对应 B）、`NOT_READY_FOR_PLATFORM_COMPARISON`（对应 NOT_READY）。

必须同时写：`SCRIPT_LEVEL_POTENTIAL_NOT_PERFORMANCE_PREDICTION`。不得写预计播放量、充值率、完播率、平台采购价或「必爆」。这些数据需要真实上线样本或平台内部数据。

### 返修优先级条目

每个任务必须包含：

```yaml
priority: P0
episode_ids: ["EP011", "EP012"]
evidence: "EP011-SC03的证据失窃没有触发EP012第一动作"
problem: "相邻集钩子未支付"
revision_target: "让EP012第一动作直接处理证据失窃，并建立新的行动目标"
protected_facts: "不得改变锁定的失窃者和证据内容"
acceptance_test: "LAST_FRAME_FIRST_ACTION_TEST通过"
```

不得只写「加强节奏」「增加爽点」「台词更生动」。

## 1.7 市场基准

- `benchmark_id`：`HG-SCRIPT-2026-07-23`
- `as_of_date`：`2026-07-23`
- `basis_type`：`PUBLIC_SOURCE_SYNTHESIS`
- `official_internal_scorecard`：`false`
- `prediction_scope`：`SCRIPT_LEVEL_ONLY`

本基准用于评估「红果同赛道剧本层竞争力」，不是红果官方内部评分表。公开资料没有披露统一的 S/A/B 算法、采购阈值、完播率门槛或爆款公式；不得自行编造。

**公开来源**：

1. 湖南省广播电视局与红果短剧真人微短剧项目通知（2026-06-08）：投稿剧本需完成不少于 40 集；真人项目限定竖屏，并按阶段组织专家评估；鼓励「画风优良、创新探索、立意向上」，用短剧节奏讲积极且有主题表达的故事。
2. 国家广播电视总局《微短剧发展管理办法（征求意见稿）》（2026-06-24）：对微短剧的公开定义强调主题主线明确、故事情节连续完整、人物角色突出；强调原创、版权、价值导向和内容规范。
3. 国家广播电视总局「微短剧精品创作传播计划」（2026-05-26）：强调内容为本、品质为魂、守正创新；追求思想与艺术交融、网感与美感兼备、通俗质朴、贴近现实；平台承担创作者孵化、原创IP和系列化IP培育、精品审核与传播责任。
4. 2026「星耀影都」全国微短剧创投季（红果短剧参与承办）：剧本与AI漫剧均设置专项赛道；评价方向包括多元题材创新、城市文化IP表达、主题鲜明、制作精良和创意突出。

**转化为剧本评审维度**——公开基准只能支持以下判断：主线是否明确，故事是否连续完整；角色是否突出且具备系列化IP潜力；是否具有短剧节奏、网感、情绪回报和持续追看机制；创意是否来自人物、题材机制或真实生活，而非低俗猎奇和套路堆砌；是否兼顾通俗表达、主题表达、正向价值与合规；40 集以上项目是否具备长线稳定性，而不是前几集强、后续注水。

**不允许推断**——没有真实平台数据时，不判断：一定会被红果采购或签约；一定成为爆款；具体播放量、完播率、付费率、拉新率和分账；红果内部编辑的真实分数或算法推荐结论。

最终措辞必须是：「基于截至2026-07-23的公开资料和本批剧本证据，该项目在剧本层呈现某等级潜力；这不是平台官方结论或实际上线表现预测。」

**更新规则**——以下任一发生时重新检索并更新：距 `as_of_date` 超过 90 天；红果、抖音集团或广电主管部门发布新征集/审核/精品计划；用户要求比较某一具体年度、赛道或平台活动；项目从AI漫剧切换为真人竖屏、横屏精品或其他发行形态。

## 1.8 双层交付

每批写入 `04_roundtable/BATCH-###/`：

```text
04_roundtable/
├── SERIES_REVIEW_LEDGER.json
└── BATCH-001/
    ├── PANEL_INPUT_SNAPSHOT.json
    ├── EDITOR_01_REVIEW.md
    ├── EDITOR_02_REVIEW.md
    ├── VIEWER_01_REVIEW.md
    ├── VIEWER_02_REVIEW.md
    ├── VIEWER_03_REVIEW.md
    ├── ROUND_TABLE_DISCUSSION.md
    ├── BATCH_REVIEW_REPORT.md
    ├── REVISION_BRIEF.md
    ├── BATCH_REVIEW_MANIFEST.json
    ├── USER_DECISION_PROMPT.md
    └── HANDOFF_CARD.md
```

全剧共用 `04_roundtable/SERIES_REVIEW_LEDGER.json`。个人审读、圆桌过程与最终判定不能只存在聊天中。

### 个人评审条目

```yaml
PANEL_MEMBER_REVIEW:
  member_id: VIEWER-02
  panel_type: AI_ROLE_SIMULATION
  batch_id: BATCH-001
  input_snapshot_version: SNAPSHOT-B001-R1
  one_sentence_recall: "普通观众对本批故事的复述"
  strongest_points: []
  weakest_points: []
  evidence: []
  most_want_to_continue_at: "集号、场号、原因"
  likely_drop_point: "集号、场号、原因；没有则写NONE_WITH_REASON"
  continue_intent: MUST_CONTINUE
  scores: {}
  weighted_total: 88.4
  recommendations: []
  independent_submission: true
```

### 圆桌讨论

`ROUND_TABLE_DISCUSSION.md` 至少包含：五席独立结论摘要；已达成共识的优点；已达成共识的问题；分歧议题、双方证据和主持结论；单集独立观看讨论；相邻集与整批连刷讨论；爽点/看点建立—见证—兑现讨论；红果同赛道剧本层比较与边界；少数意见。

不写虚构的寒暄、鼓掌或人物表演。圆桌是专业评审记录，不是综艺对白。

### BATCH_REVIEW_MANIFEST 合同

清单至少记录：输入剧本版本、批次、连续集数和评审轮次；`panel_type: AI_ROLE_SIMULATION`；五个固定席位及各自权重、十维分数、个人总分、继续观看意愿和证据；六项硬门结果；固定市场基准ID、基准日期、公开来源和剧本层预测边界；综合分、等级、推荐动作、统一用户决策门和红果同赛道剧本层潜力；分歧、阻断问题、优先返修项、失败标记和文件路径。

```json
{
  "schema_version": "1.0",
  "version": "ROUND-TABLE-B001-R1",
  "review_stage": "04R_SCRIPT_ROUNDTABLE",
  "panel_type": "AI_ROLE_SIMULATION",
  "script_manifest_version": "SCRIPT-SET-V1",
  "batch_id": "BATCH-001",
  "review_round": 1,
  "episode_ids": ["EP001", "EP002", "EP003", "EP004", "EP005"],
  "input_snapshot_version": "SNAPSHOT-B001-R1",
  "panel_members": [],
  "dimension_weights": {
    "source_fidelity": 12,
    "story_clarity_completeness": 13,
    "conflict_strategy_progression": 10,
    "pacing_information_density": 10,
    "payoff_satisfaction": 10,
    "hook_next_click": 12,
    "character_ip_appeal": 10,
    "dialogue_performance": 8,
    "standalone_and_continuity": 8,
    "novelty_market_fit": 7
  },
  "hard_gate_results": {
    "source_authority": "PASS",
    "narrative_completeness": "PASS",
    "adjacent_continuity": "PASS",
    "episode_comprehension": "PASS",
    "hook_payoff_integrity": "PASS",
    "value_and_compliance": "PASS"
  },
  "market_benchmark": {
    "benchmark_id": "HG-SCRIPT-2026-07-23",
    "as_of_date": "2026-07-23",
    "basis_type": "PUBLIC_SOURCE_SYNTHESIS",
    "official_internal_scorecard": false,
    "prediction_scope": "SCRIPT_LEVEL_ONLY"
  },
  "composite_score": 0,
  "grade": "NOT_READY",
  "decision": "AWAITING_USER_DECISION",
  "recommended_action": "REWRITE_RECOMMENDED",
  "user_decision": {
    "status": "AWAITING_USER_DECISION",
    "allowed_actions": ["PROCEED_CURRENT", "REFINE_OR_REWRITE"],
    "selected_action": "NONE",
    "risk_acceptance_required": true,
    "risk_acceptance_recorded": false
  },
  "hongguo_script_potential": "NOT_READY_FOR_PLATFORM_COMPARISON",
  "claim_boundary": "SCRIPT_LEVEL_POTENTIAL_NOT_PERFORMANCE_PREDICTION",
  "panel_disagreements": [],
  "blocking_findings": [],
  "priority_revisions": [],
  "failure_flags": [],
  "open_items": []
}
```

`panel_members` 条目记录：`member_id`、`role_type`、`specialty`、`panel_weight_percent`、`review_path`、`independent_submission`、十维 `scores`、`weighted_total`、`continue_intent`（主编为 `NOT_APPLICABLE` 并另写 `personal_verdict`）、`evidence`、`strengths`、`must_fix`。

### 最终报告与用户决策提示

`BATCH_REVIEW_REPORT.md` 先写结论：综合分与等级；五席个人总分与继续观看意愿；是否具备红果同赛道剧本层潜力；三个最强证据；三个最危险问题；是否进入下一批。最后必须重复预测边界，避免把剧本评审写成平台承诺。

`USER_DECISION_PROMPT.md` 先展示等级、推荐动作、主要风险，再固定显示：1. 接受当前版本，进入下一批或下一阶段。2. 进行一次精修或重写。回复案例：`回复：1`、`回复：2`、`接受当前版本`、`进行修改`。

评审文件只保存待选择状态。用户选择另存 `USER_QUALITY_DECISION.json` 并更新项目状态，不覆盖原始评审。

### HANDOFF_CARD

交接卡记录批次等级、综合分、五席继续观看意愿、已通过硬门、推荐动作、用户可选动作和风险。用户未选择前，不写允许进入的下一批，也不调用精修流程。

## 1.9 阶段自检

- 五席数量、角色、权重和个人文件完整。
- 每席独立意见不是换名复述，且至少三条正文证据。
- 十维分数、个人总分和综合分可重新计算。
- 六项硬门全部有证据；失败时没有被平均分覆盖。
- `S/A/B/NOT_READY` 与分数、席位下限和观看意愿一致。
- 「红果爆款」只写为剧本层潜力，不声称实际播放结果。
- `B/NOT_READY` 有可执行返修任务，所有等级都有用户决策提示。
- 评审完成后是 `AWAITING_USER_DECISION`，没有自动路由字段。
- 返修后创建新评审轮次，保留旧记录。

## 1.10 圆桌禁止越界

不假扮真实人类观众，不编造红果内部指标、官方 S/A/B 标准、播放量或转化率；不因题材热门就判爆款；不以平均分掩盖硬伤；不直接修改小说事实、分集承诺或剧本正文；不读取或执行精修流程；不替用户选择继续或修改；不创建资产、分镜、灯光、剪辑或视频提示词。

## 1.11 防捧杀硬规则与「会诊一致度过高」警报

> 融合自 script-writing-studio 02 模块。**核心目的：防止 AI 会诊变成集体说好话。**

### 1.11.1 六条硬规则

| # | 规则 |
|---|---|
| 1 | **真实反馈，不捧杀**：每位评委必须给出**至少 1 个真实弱点**；剧本真好时给**未来风险点**。 |
| 2 | **每条意见必须有证据**：必须引用**至少 1 段剧本原文、大纲条目或明确剧情事实**，不允许空泛判断。 |
| 3 | **必须有优先级**：问题要区分**高/中/低**优先级，告诉用户**先改什么**。 |
| 4 | **必须有立场冲突**：如果所有评委意见都很温和 → 主治医生归纳前**触发"会诊一致度过高"警报**，检查是否召集偏差。 |
| 5 | **禁止角色 OOC**：评委发言要符合该评委身份和关注点，**不要全部说同一种话**。 |
| 6 | **重要分歧立即追问**：碰到与项目档案、大纲或用户目标冲突的地方，**停下问**，不假装理解后硬评。 |

### 1.11.2 禁用泛话清单

以下泛话**禁止出现在五席意见中**：

```
❌ 整体不错
❌ 节奏可以
❌ 人物还可以
❌ 这个地方可以再加强一下
❌ 建议再丰富一点
❌ 立意很好
❌ 有潜力
```

**必须改写成**：`【问题定位】+【具体证据（引用原文）】+【影响】+【优先改法】`

### 1.11.3 「会诊一致度过高」警报机制

**触发条件**：所有席位的意见**都很温和**（无高优先级问题、无非议、无立场冲突）。

**触发后动作**：

```
① 主治医生在归纳前暂停，输出警报：
   ⚠️ 会诊一致度过高，可能存在召集偏差
② 检查两件事：
   · 是否召集偏差？（五席是否都偏向了同一立场）
   · 是否评价失真？（是否因题材偏好/作者滤镜而普遍宽松）
③ 处理：
   · 若确认召集偏差 → 重新配置席位视角或补充对立视角
   · 若确认评价失真 → 强制要求每席补充"最坏情况推演"
④ 在 BATCH_REVIEW_REPORT 中显式记录本次警报及其处理
```

**反捧杀强度三档**（随用户明确要求切换）：

| 档位 | 措辞 | 适用 |
|---|---|---|
| 常规档 | 保持，措辞温和 | 默认 |
| 严苛档 | 评委更辛辣，所有"对作者的善意"被抑制 | 用户要求"往死里批" |
| 经典档 | 保持，但允许对经典作品有真夸奖（不强行挑刺） | 改编名作 |

### 1.11.4 阶段自检追加项

- 五席中每一席是否都给出了至少 1 个真实弱点？
- 每条意见是否都引用了具体证据（非空泛判断）？
- 是否出现了"会诊一致度过高"警报？若有，是否已记录处理？

## 1.12 台词七维诊断框架

> 融合自 script-writing-studio 03 模块。**与 `short-drama-director/references/dialogue-doctor-7d.md`（总控）双向互链**：那份管"台词七宗罪的症状清单"，本框架管"**逐句过七维**的量化诊断"。

### 1.12.1 七维定义（每条台词都过）

| 维度 | 核心拷问 | 红线 |
|---|---|---|
| **① 角色辨识度** | 遮住角色名，能不能认出谁在说？ | A 角色台词换给 B 说也毫无违和 = 严重不及格 |
| **② 潜台词层级** | 字面说的是不是真意？有几层？ | 所有台词都是 0 层（想什么说什么）= 像 AI 写的而非戏 |
| **③ 冲突推进力** | 这一句让张力前进了，还是原地踏步？ | 连续 3 句以上没推进任何东西 = 该删 |
| **④ 类型语感** | 这句话在这个类型里成立吗？ | 单句混入跨类型违和词 = 立即标红 |
| **⑤ 信息效率** | 用最少的字传递最多的东西吗？ | 连续两句设定灌输 = 重写 |
| **⑥ 节奏与音乐性** | 读出来好听吗？长短句搭配吗？ | 通篇齐整长句 / 通篇短促独词 = 单调 |
| **⑦ 金句潜力** | 能不能截图发抖音 / 引用 / 复用？ | **加分项非底线**；一集 1-3 句即可，满篇金句 = 没有金句 |

### 1.12.2 各维检查项速查

```
① 角色辨识度：词汇库 / 句长偏好 / 句式习惯 / 口头禅语气词 / 文化层
② 潜台词层级：字面意vs真实意图（0层直白/1层反话/2层错位/3层折射）/ 观众解码难度 / 双方不知情时的双关
③ 冲突推进力：信息量/立场/关系/情绪温度/下一步动作 至少一项变化 / 回合感 / 拒绝反驳加码
④ 类型语感：古装忌现代词 / 都市忌文言密度 / 悬疑信息控制 / 喜剧反转错位 / 年代术语匹配
⑤ 信息效率：反exposition / 一句多用（≥2项=优秀）/ 删字测试 / 替换测试
⑥ 节奏音乐性：长短交错 / 停顿点 / 语气词颗粒度 / 压韵排比（高级项）/ 可朗读性
⑦ 金句潜力：可独立成句 / 修辞钩子 / 真理+反差 / 角色烙印
```

### 1.12.3 输出硬契约（★ 关键）

**诊断台词时，必须按「原台词 → 改写建议 → 为什么这么改」结构输出，且"为什么这么改"必须给出 ≥3 条维度依据。**

```
【原台词】"你根本不懂我！"
【改写建议】"（把烟按灭）……你以为你懂了？"
【为什么这么改】
  ① 角色辨识度：加"把烟按灭"的动作绑定，区别于其他角色
  ② 潜台词层级：从 0 层直白情绪 → 1 层反诘（表面质问，实则逃避）
  ③ 信息效率：删掉"根本"这类无效加强词，用动作替代形容词
```

⚠️ **凡"改写建议"未附 ≥3 条维度依据的，视为不合格产出，必须重做。**

### 1.12.4 与其他模块的边界

- **本框架不改台词**：只做诊断 + 改写建议；实际改写由剧本阶段执行。
- **不改剧本结构**：结构问题回 `six-stage-pipeline.md`。
- **不涉分镜**：台词分配节拍属分镜引擎职责。

# 第二部分 · 叙事连续性与反碎片化

本规则判断剧本正文是否真的是完整、流畅的故事，而不是字段齐全的剧情片段。锁稿前必须执行，不得用分镜、音乐、剪辑或元数据掩盖剧本问题。

## 2.1 完整故事单元

每集不要求解决全剧主线，但必须完成一个可复述的 `STORY_UNIT`：

```yaml
STORY_UNIT:
  entry_pressure: "开场已经作用于人物的压力，不是背景介绍"
  active_goal: "主角本集要完成、阻止、取得或确认什么"
  first_strategy: "主角首先采取的可见行动"
  counteraction: "对手、规则、环境或关系对象如何主动反制"
  strategy_change: "原办法失效后，主角换了什么做法"
  visible_cost: "本集画面中实际支付或确认的代价"
  local_result: "本集完成、失败或部分完成的明确结果"
  new_pressure_or_closure: "交给下一集的新行动压力，或本弧闭合结论"
```

这些字段必须能在正文中指向具体动作、台词和结果。不能把「承担风险」「关系改变」只写在审稿元数据中，正文却没有人失去、拒绝、暴露、负责或改变行动。

## 2.2 CONTINUOUS_SCENE_SPLIT 连续场景拆集

同一地点、同一时间、同一目标的一场戏，默认作为一个完整场次或一集处理。只有同时满足以下条件才允许跨集：

1. 前一集已经完成一次局部兑现，不是把一句话或一个动作拦腰截断。
2. 集尾发生不可逆状态变化，例如证据出现、行动启动、身份暴露、选择落地或关系破裂。
3. 下一集开场立即支付钩子，并建立新的行动目标或策略，不只是继续上一轮解释。
4. 两集分别具有独立的 `STORY_UNIT`，删去集号后不是一场普通谈判被机械切成两半。

若不满足，标记 `CONTINUOUS_SCENE_SPLIT` 并退回分集合并或重排。

## 2.3 单集独立开场与相邻集过桥

每集是独立发布的视频，也是连续剧的一环。首场前 10 秒必须用正在发生的危险、冲突、证据、行动或反常状态，同时建立行动主体、直接困境、本集目标和 `WHY_NOW`；不能要求观众先看上一集简介才能理解。

相邻集按「上一集最后变化 → 本集第一动作 → 本集新目标/新策略」连读。允许用 1–3 秒动作、声音或短句重叠帮助独立观看，但不能完整复播上一集，也不能先解释几十秒才兑现上集钩子。

每集执行：`STANDALONE_EPISODE_TEST`、`LAST_FRAME_FIRST_ACTION_TEST`、`FLASHBACK_ANCHOR_TEST`（完整定义见第三部分）。

## 2.4 冲突、代价与关系转变

**方案必须经历抵抗**：人物提出方案后，至少出现一次针对该方案的质疑、阻止、失败、条件交换或现实检验。仅在纸上列步骤、说清道理、对方立即同意，标记 `CHECKLIST_SOLUTION`。

**关系转变必须有证据**：从敌对到合作、怀疑到信任、疏离到亲近，都要有触发行动：保护、拒绝利益、公开站队、交出控制权、承担责任或付出资源。只有一句漂亮台词或一次眼神就达成共识，标记 `SUDDEN_CONSENSUS`。

**可见代价必须发生**：代价可以是失去时间、资源、机会、身份安全、关系信任或道德退路。必须在本集发生、被确认或触发后果；只写「可能被问责」「承担风险」但无人采取导致风险的行动，标记 `UNPAID_COST`。

**赌注先建立再调用**：资格、生命、婚姻、项目、秘密或亲人等赌注，在人物拿它施压前必须被观众建立。突然说「你连资格也不要了」，而前文没有资格线，标记 `UNESTABLISHED_STAKE`。

**情感必须改变行动**：创伤、亲情和爱情不能只用摸道具、闪回或一句宣言代表。情感证据必须影响人物选择、迟疑、隐瞒、牺牲或策略；否则标记 `EMOTION_BY_LABEL`。

## 2.5 反碎片化标记总表

出现任一未解决标记时，剧本不得 `LOCKED`：

- `CONTINUOUS_SCENE_SPLIT`：同一场戏因时长机械拆集。
- `CHECKLIST_SOLUTION`：方案靠列清单或解释直接解决，没有抵抗与检验。
- `SUDDEN_CONSENSUS`：关系转变缺少触发行为和代价。
- `UNPAID_COST`：宣称有代价，正文没有支付或后果。
- `UNESTABLISHED_STAKE`：重要赌注第一次出现就被拿来施压。
- `EMOTION_BY_LABEL`：元数据说情绪重要，正文没有改变行动。
- `PROP_ONLY_PROGRESS`：主要进展只靠连续摸、看、放置道具，没有人物策略。
- `EXPOSITION_CHAIN`：连续对白只解释信息，没人改变对话目的或行动。
- `EXPECTED_HOOK_ONLY`：结尾只确认观众已经预料的结果，没有改变下一步行动。
- `UNSOURCED_CORE_PAYOFF`：为让本批显得完整，新增来源未提供的身份、签名、证据、机关、暗号、能力、胜负或谜底。
- `IMPOSSIBLE_TIME_BRIDGE`：相邻集的日期、时段、倒计时或「连续」标记互相冲突，所需经过的时间没有被建立。
- `ALTERED_SOURCE_STAKE`：把原作的期限、触发条件、惩罚强度、资格状态或风险可能性擅自改早、改重、改轻或写成既成事实。
- `SEMANTICALLY_BROKEN_LINE`：台词有气势但主语、对象、条件或并列关系不成立，观众无法准确复述意思。
- `UNESTABLISHED_ACTION_STATE`：用于转折的重要界面、标题、文件、审批或道具状态没有被此前动作建立，突然作为既成事实出现。
- `KEY_LINE_OVERUSE`：来源金句或主题句在相邻集被完整重复，却没有关系位置、行动功能或含义升级。
- `SUMMARY_NOT_SCRIPT`：正文仍是故事概述、场次说明或编剧意图，没有可表演的行动和对白。
- `BEAT_LIST_FRAGMENTATION`：靠节拍标题和短句拼贴代替连续故事。
- `SCENE_CAUSAL_GAP`：上一场结果没有导致下一场，关键过程被场间跳过。
- `PASSIVE_PROTAGONIST`：主角只接收信息和反应，没有主动目标、策略或选择。
- `GENERIC_IP_PERFORMANCE`：角色动作、台词和关系信号可任意换给其他人。
- `VOICE_HOMOGENIZATION`：主要人物句式、攻防方式和语气趋同。
- `DIALOGUE_AS_EXPOSITION`：对白主要承担资料说明，没有争取行动结果。
- `SOURCE_KEY_LINE_LOSS`：关键台词缺失、错置人物或丢失原有行动功能。
- `LOCAL_PAYOFF_MISSING`：只留下下一集钩子，没有支付本集承诺。
- `HOOK_DEBT_BROKEN`：主钩子没有按账本兑现，或下一集没有从承接动作开始支付。
- `MECHANICAL_FAST_PACING`：通过删除动机、反制、反应和代价制造表面快节奏。
- `MAINLINE_DRIFT`：本集主要讲述内容偏离锁定主事件。
- `UNAUTHORIZED_PLOT_INVENTION`：新增来源和上游未授权的重要故事事实。
- `DELETION_CAUSAL_BREAK`：删减导致因果、动机、伏笔或后续理解断裂。
- `SOURCE_MOTIVATION_DRIFT`：人物行动理由偏离原作。
- `TROPE_REPLACEMENT`：用流行套路替换原作冲突机制或人物选择。
- `CONNECTIVE_MATERIAL_OVERREACH`：连接材料实际改变了事实、责任、关系、规则或答案。
- `CROSS_BATCH_STATE_DRIFT`：上一批出口状态与下一批入口状态不一致。
- `BATCH_CONTEXT_GAP`：本批依赖的关键状态未在上游、剧本或连续性账本中建立。
- `STANDALONE_CONTEXT_GAP`：单独观看本集时，前 10 秒无法识别行动主体、直接困境、当前目标或 `WHY_NOW`。
- `EPISODE_OPENING_DEPENDENCY`：本集开场只有看过上一集或读取简介才能理解。
- `ADJACENT_EPISODE_BRIDGE_BREAK`：上一集最后变化没有触发本集第一动作，或人物状态被重置。
- `FLASHBACK_TIME_ANCHOR_MISSING`：闪回、时间经过或返回主时间线缺少正文中的可见时间锚点。

标记必须通过改写正文消除，不能在报告中把标记改为空数组而保留原问题。

## 2.6 SOURCE_BOUNDED_CLOSURE 来源受限的闭合

完整故事单元必须闭合行动问题，不必闭合全剧事实谜团。原文只给出「某物可能与失踪亲人有关」时，可以闭合「人物决定封存、公开验证或与谁合作」，不能新增文件、签名、机关或检测结果证明关联成立。

`INFERENCE 不是` 把新谜底写入正式剧本的授权。允许推定的内容仅限不改变主线事实的表情、移动、职业流程和连接动作；一旦新增内容改变观众对身份、责任、世界规则、关键道具或结局的判断，就属于核心事实。未提供的谜底必须保留为 `OPEN_ITEM`，并用人物行动结果产生追看，而不是用编造答案制造闭合。

锁稿时从每个 `local_result` 和钩子反查来源。无法引用 `EVT` 或明确允许的连接推定时，标记 `UNSOURCED_CORE_PAYOFF` 并退回故事圣经或分集阶段。

## 2.7 SOURCE_PRESSURE_CONTRACT 原作压力保真

来源中的压力不只是一句「有危险」，还包含生效时间、触发条件、对象和后果强度。例如「**三天后的开放日必须展出，否则撤项**」不能改成「**今天停展就立即撤项**」；「资格可能受影响」不能写成「已经取消资格」。为了制造强冲突而缩短期限、升级处分或把风险写成事实，属于篡改主线因果，不属于连接推定。

每集在 `SCRIPT_SET_MANIFEST.json` 记录：

```yaml
pressure_contract:
  source_pressure: "来源原意"
  script_pressure: "剧本实际使用的压力"
  onset_and_condition: "何时、在什么条件下触发什么后果"
  source_trace: "SRC-###:范围"
  change_status: "UNCHANGED 或 USER_AUTHORIZED"
```

默认只能写 `UNCHANGED`。只有用户明确授权改变该压力时才能写 `USER_AUTHORIZED`，并在项目 `USER_OVERRIDE` 中留痕。发现剧本把「以后/可能/条件成立才发生」改成「现在/一定/已经发生」，标记 `ALTERED_SOURCE_STAKE`，`source_pressure_fidelity` 不得写 `PASS`。

## 2.8 EPISODE_TRANSITION_CONTRACT 时间线与跨集过桥

相邻两集必须先核对绝对时间、相对时间和倒计时。上一集若明确「开放日在三天后」，下一集不得写成「时间连续」并直接进入开放日；必须用场头、屏显、环境变化、人物状态或一个有效动作建立「三天后」。相反，上一集若以正在下落的杯子作钩子，下一集不得无说明跳到次日。

每集在 `SCRIPT_SET_MANIFEST.json` 记录：

```yaml
timeline:
  entry_time: "本集开场所处的明确时间状态"
  exit_time: "本集结束所处的时间状态"
  elapsed_time: "本集正文实际经过多久"
  transition_from_previous: "承接动作，或明确的时间跳转建立"
  transition_to_next: "连续承接，或下集必须建立的时间跳转"
```

检查所有屏显时间、人物说出的期限、日夜、服装伤势和流程耗时。可以省略无戏剧价值的过程，不能省略会让因果看似瞬移的时间证据。发现矛盾时标记 `IMPOSSIBLE_TIME_BRIDGE`；修复正文和跨集桥后，`timeline_continuity` 才能写 `PASS`。

## 2.9 METADATA_STRIPPED_READ 去元数据通读

锁稿前临时隐藏集头字段、`BEAT` 标题、功能标签、审稿结论和解释性项目符号，只朗读场头、动作、台词、声音与场尾。逐集以及相邻两集连读，回答：

1. 不看说明，能否知道人物此刻要什么、为什么现在必须做？
2. 每个动作是否由上一动作、信息或选择触发，而非作者把新材料摆上桌？
3. 对手是否根据主角行动改变策略？
4. 关系变化能否指出触发行为，而非靠审稿表宣称？
5. 本集结束时是否有实际结果，不只是「准备开始下一步」？
6. 同场跨集是否形成两个完整单元，而不是一个场次的上下半段？
7. 台词是否像人物在争取结果，而非编剧总结主题？
8. 相邻集连读时，日期、倒计时和「连续/稍后/次日」等标记是否真的相容？
9. 剧本使用的期限、惩罚和资格风险，是否与来源的生效条件同样准确？
10. 关键台词能否用直白句准确复述；参与转折的界面、文件和道具状态是否有建立动作？
11. 单独抽出本集时，首场前 10 秒能否识别行动主体、直接困境、本集目标和 `WHY_NOW`？
12. 上一集最后变化是否由本集第一动作直接承接；闪回和时间跳转是否有正文锚点？

任一核心答案为否，`metadata_stripped_read` 不能写 `PASS`。

## 2.10 跨批连续性

长剧分批输出时，批次边界不是叙事边界。每一批都维护人物位置、身体与情绪状态、目标、知识和秘密，关系位置，道具归属，时间与倒计时，伏笔状态和钩子债务。

新批次开始前必须读取全剧策略、全部分集卡、上一批末集完整正文和 `CONTINUITY_LEDGER.json`。只读上一批摘要会遗漏台词承诺、动作位置和情绪余波。逐项验证：

1. 上一批出口人物状态等于本批入口状态。
2. 上一批集尾动作由本批第一动作直接支付，或明确建立合法时间跳转。
3. 已公开与未公开信息没有复位或越权泄露。
4. 伤势、服装、道具、地点和流程耗时连续。
5. 关系变化累积，不因换批恢复到早期位置。
6. 关键台词 `PRIMARY_USE`、伏笔和钩子账本跨批唯一。

不一致时分别标记 `CROSS_BATCH_STATE_DRIFT` 或 `BATCH_CONTEXT_GAP`。每批完成后连读「上一批末集 + 本批全部集 + 下一批分集卡首集」；全部批次完成后执行全剧去元数据通读。

## 2.11 锁稿质量合同

`SCRIPT_SET_MANIFEST.json` 中每个锁定集必须记录完整 `story_unit`、`pressure_contract`、`timeline`、空的 `fragmentation_flags`，以及以下 `quality_gates` 全部为 `PASS`：

```yaml
quality_gates:
  source_event_fidelity: PASS
  deletion_safety: PASS
  episode_plan_fidelity: PASS
  source_bounded_closure: PASS
  source_pressure_fidelity: PASS
  timeline_continuity: PASS
  narrative_continuity: PASS
  episode_completeness: PASS
  scene_causality: PASS
  active_opposition: PASS
  visible_cost_or_consequence: PASS
  relationship_turn_evidence: PASS
  key_dialogue_fidelity: PASS
  dialogue_naturalness: PASS
  ip_dramatization: PASS
  visual_story_progression: PASS
  audience_comprehension: PASS
  local_payoff_and_hook: PASS
  first_10_seconds_hook: PASS
  standalone_episode_comprehension: PASS
  adjacent_episode_bridge: PASS
  flashback_time_anchor: PASS
  metadata_stripped_read: PASS
  duration_table_read: PASS
  cross_batch_continuity: PASS
fragmentation_flags: []
failure_flags: []
```

若本集不包含关系转变，`relationship_turn_evidence: PASS` 表示正文没有伪造关系变化；不能使用 `N/A` 绕过检查。若本集没有闪回，`flashback_time_anchor: PASS` 表示没有伪造或遗漏时间跳转，同样不使用 `N/A` 绕过检查。

## 2.12 合成对照

弱版本：角色写出三条方案，对方听完立即同意，两人宣布共同承担风险；为增强结尾，又从道具里弹出一份原文不存在的身份证明。它同时触发 `CHECKLIST_SOLUTION`、`SUDDEN_CONSENSUS`、`UNPAID_COST` 和 `UNSOURCED_CORE_PAYOFF`。

有效版本：角色先封存证据，对方因必须提交材料而准备发送旧方案；角色提出替代方案但被主管拒绝；对方主动删除能保住自己的噱头标题并签名承担延期责任，才换来一次限时验证。关系变化由行动触发，代价已经进入现实流程。

# 第三部分 · 单集独立开场与相邻集过桥契约

本规则解决两个必须同时成立的观看入口：

1. 连续观看：上一集最后的状态、钩子或动作自然触发下一集第一动作。
2. 单集观看：观众没有看上一集，也能在本集前 10 秒内知道谁正处在什么困境、本集要解决什么、为什么必须现在行动。

不能用「上集回顾」替代戏剧开场，也不能为了单集可懂重复解释整段前情。最小补课信息必须嵌在正在发生的冲突、选择、证据或危险中。

## 3.1 前 10 秒双入口

首场前 10 秒至少同时提供：

- 一个可见爆点：危险、行动、证据、反常、冲突、身份落差、不可逆选择或关系突变。
- 最小人物处境：行动主体是谁，他正在承受什么直接压力。
- 本集行动问题：他现在要完成、阻止、确认或夺回什么。
- `WHY_NOW`：为什么不能晚一点再做。

爆点不是无来源闪回、喊口号、突然打人或单独展示奇观。它必须来自本集主事件、上集钩子、已授权重排或来源允许的连接动作，并在本集得到推进或结算。

不要在开头塞入世界观、人物小传和全剧前情。若删除某条背景后，观众仍能理解本集行动，就不应放入前 10 秒。

## 3.2 STANDALONE_EPISODE_TEST

把本集干净剧本单独交给一名不知道上集内容的观众，只阅读首场前 10 秒和本集正文。观众必须能回答：

1. 谁是当前行动主体？
2. 他眼前遇到什么具体麻烦？
3. 本集当前要解决或确认什么？
4. 为什么必须现在处理？
5. 本集结束时实际得到什么？
6. 为什么愿意继续看下一集？

前四题任一无法回答，标记 `STANDALONE_CONTEXT_GAP`；只能依赖集名、简介、审稿字段或上一集才能回答，标记 `EPISODE_OPENING_DEPENDENCY`。

单集可懂不等于单集封闭。观众可以不知道全剧谜底，但不能不知道当前行动因果。

## 3.3 LAST_FRAME_FIRST_ACTION_TEST

逐对连读相邻两集，先只看：上一集局部兑现；上一集最后不可逆变化或主钩子；上游锁定的 `next_episode_first_action`；下一集第一场的首个有效动作。

必须形成：

`上一集最后变化 → 下一集第一动作 → 下一集新目标或新策略`

下一集不能重置人物位置、身体、情绪、知识、关系、道具或危险，也不能先解释几十秒再支付上集钩子。若第一动作不是由上一集产生，标记 `ADJACENT_EPISODE_BRIDGE_BREAK`。

允许用 1–3 秒动作、声音或关键短句重叠帮助单集观众进入，但不得完整复播上一集结尾；重复内容必须同时承担新一集的目标建立或策略变化。

## 3.4 时间跳转与闪回

相邻集或首场发生时间跳转时，观众必须在正文看见或听见时间证据，不能只在清单里写「闪回」：

- `CONTINUOUS`：连续动作、同一声音、未完成动作或明确「连续」状态。
- `FLASHBACK`：可见「数小时前/三日前」等进入锚点；回到主时间线时再给返回锚点。
- `ELAPSED`：用屏显、环境、服装、伤势、流程结果或台词建立经过时间。
- `PARALLEL`：用「与此同时」、共同声源、同一事件反馈或同步时点建立为何此刻切入。
- `SERIES_OPENING`：第一集开篇，不消费上集状态。

把「三日前」写成「当日稍早」、把「数日后」写成「连续」、闪回结束后直接切回现在而无提示，标记 `FLASHBACK_TIME_ANCHOR_MISSING` 或 `IMPOSSIBLE_TIME_BRIDGE`。

## 3.5 结构化合同

每集在 `SCRIPT_SET_MANIFEST.json` 写入：

```yaml
opening_contract:
  hook_type: DANGER
  visual_or_conflict_hook: "花轿突然侧倾，主角撞向轿壁"
  protagonist_and_situation: "苏棠正在被迫送往陌生婚局"
  immediate_conflict: "轿夫故意加重颠簸"
  active_goal_or_question: "她必须先稳住身体并逼停颠轿"
  why_now: "继续颠簸会令体弱身体失去行动能力"
  first_10_seconds_evidence_text: "轿身猛地向一侧倾斜"
  standalone_test_summary: "盲看可识别主角、颠轿危险、即时目标与时限"
  status: PASS

transition_contract:
  previous_episode_id: EP003
  previous_local_payoff: "上集锁定的局部兑现原文"
  previous_hook_id: HK-EP003
  planned_first_action: "上集锁定的 next_episode_first_action 原文"
  first_action_evidence_text: "轿身再次猛地侧倾"
  causal_bridge: "上一集第一次侧倾未解决，下一集继续升级并迫使苏棠反制"
  opening_time_relation: CONTINUOUS
  source_time_basis: "SRC-001:L95，花轿驶出信王府所在长街后"
  time_consistency_summary: "与上集出口均为替嫁当日送嫁途中，没有提前或重置"
  opening_time_anchor_evidence_text: "连续"
  return_to_main_timeline_evidence_text: NOT_APPLICABLE
  no_reset_proof: "人物仍在轿内，针囊在袖中，危险和身体状态连续"
  status: PASS
```

第一集使用：

```yaml
previous_episode_id: SERIES_OPENING
previous_local_payoff: NOT_APPLICABLE
previous_hook_id: NOT_APPLICABLE
planned_first_action: NOT_APPLICABLE
opening_time_relation: SERIES_OPENING
source_time_basis: "来源开篇时间事实"
time_consistency_summary: "系列开篇，没有上集时间状态"
opening_time_anchor_evidence_text: NOT_APPLICABLE
return_to_main_timeline_evidence_text: NOT_APPLICABLE
```

非第一集的 `previous_local_payoff`、`previous_hook_id` 和 `planned_first_action` 必须逐字绑定上一集锁定分集卡，禁止剧本层同义改写。`source_time_basis` 必须引用小说或事件账本的时间事实，`time_consistency_summary` 必须说明来源、分集与正文是否同日、连续、经过时间、闪回或平行；不能把「三日前」改成「当日稍早」。`first_10_seconds_evidence_text`、`first_action_evidence_text` 和适用的时间锚点必须能在干净剧本正文中找到。

## 3.6 锁稿门

以下质量门全部为 `PASS` 才能锁稿：`first_10_seconds_hook`、`standalone_episode_comprehension`、`adjacent_episode_bridge`、`flashback_time_anchor`。

# 第四部分 · 全上下文深读与权威顺序

> 本契约供授权后的精修/重写执行（流程见 [six-stage-pipeline.md](six-stage-pipeline.md) 第八节）。

## 4.1 固定阅读顺序

1. 读取 `SOURCE_MANIFEST` 和用户提供的全部原小说范围。
2. 读取锁定 IP 版本、角色小传、行为锚点、声音规则和关系签名。
3. 读取故事圣经、世界观价值观、事件账本、人物弧、信息边界和改编蓝图。
4. 读取分集规划、本批前后集卡、钩子兑现账本和批次入口出口。
5. 读取当前干净剧本、来源改编地图、关键台词账本和连续性账本。
6. 最后读取五席意见、圆桌报告和返修清单。

不得先看评分再带着结论找证据。

`REFINEMENT_MANIFEST.verified_inputs.read_order` 必须按上述顺序留下机器可检验记录；输入核验还应核对来源文件哈希和五个版本绑定。任何输入缺失或仍为测试/临时未锁定状态，都必须先返回对应上游，不得进入正式精修。

## 4.2 理解简报最低内容

`UPSTREAM_COMPREHENSION_BRIEF.md` 必须回答：

- 当前来源是完整小说还是节选，哪些结论仍是 `OPEN_ITEM`。
- 本批覆盖哪些来源事件，哪些后续因果依赖本批。
- 主角、对手和关键关系各自想要什么，为什么现在行动。
- 锁定 IP 的稳定内核、灵魂选择、缺陷、行为锚点和声音禁区。
- 本批在全剧弧线中的入口、变化、出口和下一批第一动作。
- 每集的命题、局部兑现、主钩子与支付集。
- 人物、道具、伤势、知识、关系和时间的进入与退出状态。
- 不得删除、改序或改义的来源事实与关键台词。

只复述圆桌问题、不复述原作和上游，判定 `CONTEXT_NOT_UNDERSTOOD`。

## 4.3 评审意见的权威边界

评审意见只有三种合法用途：

- 指出正文证据支持的观看或结构问题。
- 提出不改变上游事实的修改目标。
- 暴露需要返回上游的真实冲突。

出现以下情况拒绝意见：

- 要求新增来源没有的核心反转、身份、证据或救援。
- 要求人物违反锁定 IP 换取即时爽感。
- 要求取消分集已锁定的局部兑现或钩子。
- 把平台猜测、个人偏好或分数目标写成故事事实。

拒绝时写明冲突的上游版本、事实和替代处理，不得静默忽略。

## 4.4 长篇来源

长篇可以分段读取，但必须先建立全源索引，再完整读取：本批直接来源段；本批前因；本批后果和未来支付段；角色身份、关系、能力和秘密的全局证据。

不得只读当前三集对应段而误改后续伏笔。

## ★ 全稿纯口播连读测试（初稿完稿及任何删改移动后的强制终检）

初稿写完或任何相邻场次挪动/删改后，**临时剥离章节标题、场景说明与 `△` 动作提示，仅将全部对白与旁白从头到尾连续朗读一遍**，专抓四类结构隐疾：
1. **主语悬空与指代不清**（“他/那个/下一批”在当前语境存在两个以上指向）；
2. **信息重复与二次上课**（前面已讲明的结果或数字，后文换人再复述一遍）；
3. **时间突跳与因果断桥**（删掉章节标题后上下两场接不上）；
4. **高潮后结尾拖沓**（核心反转已成立，结尾仍在复述前面细节而非收刀升维）。
