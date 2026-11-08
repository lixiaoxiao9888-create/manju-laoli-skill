# 可选 JSON 项目包契约

## 边界

本工具是一条**新生产链的可选入口**，不替换现有 Markdown 工作流，不修改旧编译器或门禁，也不自动挂载到现有技能流程。**旧 md 不会自动迁移**；需要人工整理成 JSON 并复核后再使用。JSON 是本链唯一事实源，导出的 Markdown 是只读衍生物；改镜头请改 JSON 后导出到新目录，不在两份 md 中分别改稿。

仅使用 Python 标准库，无第三方依赖。**包内不随附示例工程文件**（P14 起案例示例整体剔除）：合规输入由 `scripts/test_project_bundle.py` 内联的测试夹具在运行期生成到系统临时目录，只服务于回归测试，不作为可参照的样例交付物。

## JSON 字段

所有列出的字段必填，除 `segments[].transition` 外无可选字段。未知字段报 ERROR，避免拼写错误被静默忽略。文本字段必须为非空字符串；数组字段允许空数组，但 segments 和每段 shots 必须非空。文件采用 UTF-8（可带 BOM）。拒绝重复 JSON 键、NaN、Infinity。

| 对象 | 字段与类型 |
|---|---|
| 根对象 | project 对象、characters 数组、assets 数组、segments 数组 |
| project | model 非空字符串；video_aspect 画幅字符串；asset_aspect 固定 `16:9`；total_duration 有限正数，秒 |
| characters[] | id 稳定字符串；visual_age 非负整数（不接受 `28.0`、字符串或 bool）；description 非空字符串 |
| assets[] | id 稳定字符串；type 非空分类字符串；aspect 固定 `16:9`；prompt 非空字符串；refs 为角色或资产 ID 字符串数组 |
| segments[] | id 稳定字符串；duration 有限正数，秒；entry_state、exit_state 非空状态字符串；shots 数组；可选 transition 非空字符串 |
| shots[] | id 全局稳定字符串；start、end 段内有限非负秒数；action、camera 非空字符串；dialogues 数组；asset_refs 资产 ID 数组 |
| dialogues[] | character_id 角色 ID；text 非空字符串 |

ID 在角色、资产、段落及全部镜头之间全局唯一，格式为 `[A-Za-z0-9_][A-Za-z0-9_.-]*`。镜号由作者维护，不按数组索引重新编号；调整时间或排序不应修改既有镜头身份。工具能检查单份项目内的唯一性，不能证明跨版本身份未漂移。

video_aspect 支持 `16:9 / 9:16 / 21:9 / 1:1 / 4:3 / 3:4`。视频竖屏不改变资产横屏约束。model 和资产 type 只登记非空标签，不声称对应模型的能力、单段上限或官方投喂语法已核验。

refs 只是登记关系，不递归展开，也不代表已上传图片。asset_refs 仅接受资产 ID；对白 character_id 仅接受角色 ID。action、camera、状态和 prompt 内的自由文字不做实体识别，文字内的人名或资产描述需要人工复核。

## 机械校验

- `DUPLICATE_ID`：全局 ID 重复，ERROR。
- `DANGLING_REF`：显式引用不存在或指向错误类型，ERROR。
- `VISUAL_AGE`：视觉年龄不是非负整数，ERROR。
- `ASSET_ASPECT`：项目或任一资产不是 16:9，ERROR。
- `TOTAL_DURATION`：总时长不等于全部段长之和，ERROR。
- `SHOT_COVERAGE`：shots 按输入数组顺序从 0 到 duration 连续覆盖；禁止间隙、重叠、倒序、零长、越界或尾部缺失，ERROR。不自动排序修复。秒数支持小数，比较绝对误差容许 `1e-6` 秒。
- `STATE_TRANSITION`：前段 exit_state 与后段 entry_state 字符串不完全相等时，后段必须有非空 transition，ERROR。相等只是字符串一致；有 transition 只是声明齐备，并不证明衔接合理。转场发生在既有段与 shots 时间轴内，不自动增加时长或镜头。
- `DIALOGUE_BUDGET`：同镜全部对白**累计**预算超过镜长时报 WARN。每句估算为 `字母数字字符数 / 6 + 0.3 秒停顿`；不计标点和空白，同镜按顺序发声，不假设多人同时说话。英语等语言的估算可能偏差很大；这不是声音合成实测，也不是动作与对白共用预算的自动证明。
- `SCHEMA`：缺字段、未知字段、形状或类型不符、非有限数等，ERROR。遇到首个结构类型错误停止深入检查；已发现的问题保留，修正后重新运行。

结果 JSON 分开返回 `structural_status: valid|error`、`semantic_status: needs_review` 和 issues（level/code/path/message）。WARN 不阻止导出，但保留在两份 Markdown 中；退出码 0 只表示无机械 ERROR。

**所有语义一律 needs_review**，不输出语义自动通过结论。包括空间/轴线/遮挡、人物外观年龄是否可视、状态转场因果、对白可演性、动作物理、镜头充分性、资产图像一致性、模型适配等。工具不看图、不出图，也不能阻止用户在自由文本中自己写入不实结论；这些仍需人工审查。

## 同源导出与阶段

`export` 从同一份 `segments[].shots[]` 顺序生成两份文件：

1. `assets-prompts.md`：角色档案、资产提示词与引用关系，以及逐镜画面、摄影、时码、对白、资产引用。
2. `P3CLEAN_GRID.md`：**P3 图形化环 CLEAN_GRID** 故事板生图计划，不是 P4.5，不是最终模型七段式投喂稿，也不是已生成图片。

两份逐镜内容共用同一个渲染片段，保留稳定镜号和对白原文。每段一张网格，最小映射一镜一格；列数为格数平方根向上取整，行数向上补齐，余槽留白（四镜工程即 2×2）。不凭空增加动作、镜头或剪辑点。复杂动作的相位拆分、默认格数与正式 P3 模板是否充分，仍须人工复核，本工具不宣称完整 P3 已完成。

CLEAN_GRID 的图面要求无文字、序号、对白框、箭头、技术标签或水印，纯画面加留白分隔。Markdown 里的镜号、时码和对白是**图外追溯信息**，不是让生图模型绘制的图中文字。人物与资产依据由同包档案、资产提示词和显式引用提供；素材形态声明为 M0，没有虚构图片槽位。

## CLI 与失败行为

从 `short-drama-director` 目录运行（`python` 换成实际解释器路径）：

```bash
PYTHONDONTWRITEBYTECODE=1 python scripts/project_bundle.py validate <你的工程.json>
PYTHONDONTWRITEBYTECODE=1 python scripts/project_bundle.py export <你的工程.json> --output /existing-parent/new-bundle
PYTHONDONTWRITEBYTECODE=1 python scripts/test_project_bundle.py
```

本次指定 Windows Git Bash 解释器用法：

```bash
PYTHONDONTWRITEBYTECODE=1 "C:/Users/李/.workbuddy/binaries/python/versions/3.13.12/python.exe" scripts/test_project_bundle.py
```

- validate 仅读取并向 stdout 输出 JSON，不写文件。
- export 在完整校验、内存渲染成功前不创建目录或文件；有 ERROR 时不写任何输出。
- 输出必须是**不存在的新目录**，其父目录必须已存在。已有目录或文件一律拒绝，不覆盖已有工作，也不能覆盖输入 JSON。
- 两份文件先写同父目录下的临时区，再整体重命名发布；普通写入/发布异常会清理临时区，不留下半份输出。进程被强制终止、断电等不承诺事务恢复；同一目标不支持并发导出。
- JSON/输入 IO/输出 IO 失败退出 1，报告 semantic_status 仍为 needs_review。机械校验有 ERROR 退出 1；无 ERROR（含 WARN）退出 0；CLI 参数用法错误由 argparse 退出 2。
- 不修改输入 JSON、不自动修复、不创建缓存或迁移旧 md。测试设置 PYTHONDONTWRITEBYTECODE=1，临时 JSON/导出件仅在系统临时目录中生成并自动清理。
