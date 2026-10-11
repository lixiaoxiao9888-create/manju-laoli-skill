# MiniMax H3 格式支线（格式转换层 · ★权威）

> **定位（2026-09-19 用户裁定）**：H3 **不是又一个模型，而是一条格式转换支线**——A 锁在 Seedance 2.5 / 2.0 之下并列 **MiniMax H3**；选定后只做一件事：**把本包最终出的七段式投喂稿，转成 MiniMax H3 原生格式**。
>
> **支线边界**
> - **不动的部分**：P0~P3 全流程、资产链（4 View 资产板/场景/道具）、台词七维与语速、**对白语气位（法则 19）**、**人物账·摆位必入画（法则 20）**、**首镜锚定·景别一致·姿态延续·视线指派（法则 21）**、**禁令失效三改法（法则 22）**、**首镜单主体锚定与具象化（法则 23）**、**示范句验证纪律（法则 24）**、FACS、12 节拍、段缝 D 锁、看板、C1~C20 机检（Seedance 侧）——**一律不改**。
> - **动的部分**：只有 P4 投喂封装的**输出壳**：七段式 → H3 三字段 / 六段式，**且正文整体转译为英文**（2026-10-02 官方复核，见下方修订块）。
> - **一句话**：上游（剧作/分镜/资产/时长/语气/人物账/首镜/禁令/语言）全由本包供给，下游只换壳。
>
> 官方背书：H3 的 `H3-Context-IR` 就是把多模态上下文转成结构化提示词的模块，官方明言 *"对最终输出质量至关重要，我们强烈建议将其纳入你的生成流水线，或按照提示词指导构建自己的上下文处理系统"*——**本包适配层就是那个"自建上下文处理系统"**。

> ## ⚠️ 2026-10-02 官方复核修订（对照 MiniMax-AI/MiniMax-H3 官方仓库 live 文件逐字重验）
> ① **正文语言（根因级修正）**：官方指南 base-en/ref-en 明文 "**Write all six rewrite sections in English**"——六段正文一律英文，只有 `<d>` 内台词/歌词与双引号内画内文字保留原语言（中文台词写 `<d>[Chinese] …</d>`）。本文件旧口径"跟随内容主语言（中文项目写中文）"即日起废止。实测佐证：中文正文属模型重写格式的域外输入，切点/说话人/字幕执行率全线劣化。
> ② **切镜动词官方绑定短语**：`the camera cuts to` / `the shot cuts to` / `the shot transitions to` / `the shot changes to` / `the shot switches to`；**cross-dissolve / fade / wipe 仅在用户明确要求时使用**；"若只是距离或角度微变，优先用运镜不切镜"（base-en §4.2）。实测：中文"镜头切至"不被绑定，模型自由发挥成叠化+过渡融脸。
> ③ **画外声官方公式**（base-en §4.4）：`<Subject N> (Sx) says in an off-screen voiceover: <d>[Language] …</d> while his/her lips remain completely closed.`——固定短语 + (Sx) + 闭口证据紧跟 `</d>` 之后。实测：中文自创措辞 + 无 (Sx) 压不住口型（画面角色照样张嘴）。
> ④ **多说话人已知缺陷**（官方 issue #17，open 未修复）：多说话人声音身份互串，**同性别多说话人必崩**（付费闭源版同样复现）；模型按粗声学特征（音高/共振峰）分人而非按提示词绑定。缓解：说话人首次出现给足 age/gender/on-screen/**pitch/timbre/rate/accent** 且同场景声学画像拉满对比、一段一开口者、清理非对白人声词（轻笑/抽气/窃语类，有实测因一句未格式化的 chuckle 打乱全段路由）、声音只前进不回头（A→B→A 恢复旧声必翻车）。
> ⑤ 机检同步：`validate_prompt.py` H4 新增"正文出现中文（`<d>` 与双引号内除外）→ WARN"、H9 新增"缺官方固定短语 → WARN"、H11 声学提示词表补英文词。


> ## ⚠️ 2026-10-05 V7.0 实战修订：H3 支线 = 格式转换 + 生产实战
> 《实测玄幻漫剧》EP01 约 40 条实测证明：**只换格式会卡成 PPT**。H3 支线从 V7.0 起必须同时遵守 **`h3-production-playbook.md`（★生产实战权威）**，后期见 `post-production-jianying.md`。要点：
> ① **分镜图只能弱参考**：官方两种用法——硬锁（首帧/关键帧/尾帧，`the shot begins from <Picture N>`）与软参考（`storyboard reference for [Shot 1]…, defining viewpoint, subject placement, and shot order`）；分镜 retention 一律 `weak_reference` 并写明"不是关键帧、角色不摆姿势"（partially_preserved 会让每镜锁成分镜定格）。
> ①b **官方分镜规范（2026-10-06 复核 MiniMax-AI/MiniMax-H3 `skills/3d-animation-short-generator/references/storyboard-guidelines.md` + `model-selection.md`）**：官方默认**文字分镜**（逐秒四要素：姿态+表情 / 镜头 / 音频+站位锚 / 表演备注）直接作为 H3 提示词主体；**分镜图是可选的人看预览、渲染时不喂给模型**（"pencil images are human-review-only"，"do not let it override the text storyboard"）；若画分镜图：**纯黑白铅笔线稿，无颜色、无成品光影、无精修渲染**（"not final art"），**一镜一图**、格数＝该镜秒数（3s→1×3、6s→2×3）。本项目做法（彩色精修 CG、一张九格跨 7 切、作为 Ref2VA 参考图喂入）与官方差距三处：成品感、跨镜一图、喂给了模型——E02-2 00197 分镜 v6（精修近景、时间码对齐切镜）被逐格当关键帧（均值 1.6）即此病。
> ② **分镜画九格"动作过程"**：3×3、每格时间码、相邻格是同一动作起势→到位、每格画动作中途（运动模糊）；静态造型格 = 视频在此定姿。
> ③ **动态按运动量≈10 写**：高能量词、三层运动、首末帧在动、跟着动作切；**禁静止蓄力与慢镜**（AI 无静止表演能力，打击感只用 1~2 帧 hit-stop，正向写）；长台词每镜 ≤3 秒。
> ④ **打戏规则同样适用**：`action-previs-15grid.md` 的开局冲击、五要素+30~60° 斜角、闪避大幅化、动力链、高潮收尾——H3 支线不再只换壳（v1.3→v1.4 动作均值 +1.7~2.1）。
> ⑤ **画外声**：官方公式写全仍不够，脸在画内仍可能张嘴（E01-2 实测）→ 独白落在看不到脸的镜头。
> ⑥ **生成 15s、剪辑保留 10~13s**：H3 每镜与段尾必"落定"，靠 `scripts/h3_tools/动作剪辑.py` 压掉；换分辨率=重新抽卡，低清挑卡后超分。
> ⑦ 机检升至 **H1~H16**（新增 H13 分镜锁帧 / H14 低能量词 / H15 静止与慢镜 / H16 单镜台词时长）。

---

## 一、模式路由（H3 只有两个 checkpoint，别按"五模型"理解）

| H3 checkpoint | 输入形态 | 对应本包状态 | 输出字段集 |
|---|---|---|---|
| `H3-Base-FL2VA` | 零图 | 文生音视频（T2VA）：无资产图 / 纯文本段 | 三字段 |
| `H3-Base-FL2VA` | 一图 | 首帧（I2VA）：有分镜首帧图；**D 锁①的段缝分镜参考图按首帧投** | 首帧指令行 + 三字段 |
| `H3-Base-FL2VA` | 一图 | 尾帧（L2VA）：只有收势定格图 | 尾帧指令行 + 三字段 |
| `H3-Base-FL2VA` | 两图 | 首尾帧（FL2VA）：本包「参考模式②首尾帧」 | 首尾帧指令行 + 三字段 |
| `H3-Base-Ref2VA` | 多模态参考 | 本包「参考模式①全能参考」（角色 4 View + 场景 + 道具 + 可选视频/音频） | **六段式** |

- **三字段**：`integrated_multimodal_description` / `overall_soundscape` / `non_diegetic_music`
- **六段式**：`subject_definitions` / `summary` / `retention_analysis` / `detailed_description` / `overall_soundscape` / `non_diegetic_music`（顺序固定，不可调换）

### 1.1 指令行（仅 I2VA / FL2VA / L2VA 需要）

必须作为正文**第一行**，其后跟一个空行：

```text
I2VA:  For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

FL2VA: How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.

L2VA:  How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.
```

- `N` = 实际末镜编号；`S.SS` = 有效时长，两位小数。
- **Ref2VA 没有指令行**（官方实例亦无），不要凭手感加。
- 指令行是官方固定英文模板，**保持英文原文不译写**（2026-10-02 修正：旧"可整行译写"口径废止——六段正文一律英文）。

---

## 二、七段式 → H3 字段映射（核心表）

| 本包七段式稿源 | H3 目标 | 转换动作（硬要求） |
|---|---|---|
| 【画幅风格】行（含 `model=`） | 请求参数 `ratio` + 正文开场句 | 画幅**不进正文**，走载荷；风格转成开场 1~2 句具体描述（Ref2VA 在 `[Shot 1]` **之前**；T2VA 在 `[Shot 1]` 之后）；**"电影感/唯美"这类空词换成可见要素**（镜头质感/色温/光位/景深） |
| 【场景资产】`@SCN-xxx` | 六段式：`<Subject N>`（环境类） | 场景**图**当环境参考 → Subject；只有图本身要当具体帧（首/尾/构图锚）时才另立 `<Picture N>` 独立条目 |
| 【核心人物】`@CHR-xxx` × N（含 `（在场）` 标记） | 六段式：`<Subject N>`（人物类） | 外观特征写进定义行（发式/肤色/服装/兵器）；`@` 锚点**全删**；音色锁（2.5 可选）转写成主体描述里的音色短语；**`（在场）` 两级标记在 H3 侧不保留标记词**，只体现在该角色是否被镜头带到 |
| 【站位声明】（四要素 + 轴线 + 位移） | **无对应栏** | **必须转写成画面语言句**并入对应 `[Shot N]`（"三步外停住""身子半侧向庭院""两人之间"）；禁坐标表、禁 ASCII 布局、禁 `@` 锚点。⚠️ **摆位必入画（法则 20）在 H3 侧照旧成立**：站位里摆了位的每个人，转换后**必须在至少一个 `[Shot N]` 出现**（正拍/焦外身影/全景群像/反应镜头均算），否则写明"已出画/已退场·去向"——H3 没有站位栏可查，这条只能由转换者守住（机检 H5 兜底：定义了却全文未引用 → 告警） |
| 【时间轴分镜】镜行 | `[Shot 1]`（无时间戳）/ `[Shot N] At MM:SS.mmm,` + 切点 | 首镜**不带时间戳**；后续镜以 `At 00:04.000,` **严格递增**且 ≤ 段时长（英文正文用官方格式，中文"在…处"仅旧稿兼容）。**切镜动词用官方绑定短语**：`the camera cuts to` / `the shot cuts to` / `the shot transitions to` / `the shot changes to` / `the shot switches to`；**cross-dissolve/fade/wipe 仅用户明确要求时用**；景别/角度微变优先用运镜不切镜（base-en §4.2）。⚠️ **首镜锚定（法则 21）照旧成立**：`[Shot 1]` 必须带**一个具名主体**（`<Subject N>` 或注明归属的部位，如 "her right hand"）；空镜开场须在镜行首写明「空镜：…」且每段至多 1 镜（机检 H12a） |
| 镜行 `声音：…` | 拆三层 | 环境音/物理音/非语言人声 → `overall_soundscape`；BGM → `non_diegetic_music`；对白/歌唱 → 留在正文 `<d>` |
| **镜行 `台词：【角色（语气）："…"】`（法则 19）** | `(Sx)` + 说话人身份短语写在 `<d>` **外面** + `<d>[Chinese] 原文</d>` |**语气位必须继承，且用英文合成说话人短语**（官方 base-en §4.4：首次出现要给足 character type / age / gender / on-screen 与否 / **pitch / timbre / speaking rate / accent**）——`The young woman with a low, flat, cool voice (S1) says at an even pace: <d>[Chinese] …</d>`；`<d>` 内**只放语言标签 + 台词原文**，逐字不改（含标点）；**语气词禁写进画面段**（同 C16a）。⚠️ **同性别多说话人高危**（官方 issue #17，open 未修复）：声音身份会互串、同性别必崩——同场景说话人声学画像**拉满对比**（音高/音质反着写）、优先"一段一开口者"、非对白人声词（轻笑/窃语/抽气类）清理成群杂环境音、声音只前进不回头（A→B→A 恢复旧声必翻车） |
| `（OS·音色）/（VO·音色）` 画外声（`vo-os-weaving.md`） | `<Subject N> (Sx) says in an off-screen voiceover: <d>[Chinese] …</d> while his/her lips remain completely closed.` | **官方固定公式**（base-en §4.4）：短语 `says in an off-screen voiceover` + 画外声源自具体人物时**必须给 (Sx)** + 闭口证据 `while … lips remain completely closed` **紧跟 `</d>` 之后**。⚠️ 2026-10-02 实测（本包两轮抽卡）：中文自创措辞 + 无 (Sx) 时该通道压不住口型（画面角色照样张嘴）——按官方公式英文书写，或摘出正文走后期贴声；`{}` 锁口型通道**不得**用于画外声；⚠️ **2026-10-04 实测：公式写全、脸在画面里仍可能张嘴露齿**（E01-2 近景）→ 独白一律放在看不到脸的镜头（背影/远景/物件/过肩），见 `h3-production-playbook.md` §三.7 |
| 画内文字 / 字幕【】 | 双引号内保原文 | `木牌写着"静心"`；用**英文直角双引号**，不用中文引号/书名号 |
| FACS 微表情（AU 配方） | 可见肌肉语言 | `眼周皮肤绷紧、眉心一蹙、下唇内抿`；**AU 编号/强度档/kernel 不进正文**（同 C12 口径） |
| **抽象形态形容（法则 23）** | **具象可见形态** | 成线/成串/如注/轻蜷/微蜷 这类抽象副词一律换掉——"雨滴砸在手背上溅开"（机检 H12 同族；与 C20c 同口径） |
| **首镜单主体（法则 23）** | 一个具名主体统摄 | **禁「X 与 Y 同框」并列主体句式**（`同框/同在画面/一同入画`）；部位以"她的/其 + 部位"从属出现；**禁悬空指示代词**（这只手/那张脸 → 她的那只手）（机检 H12b/H12c；C20a/C20b 同口径） |
| **禁令改法（法则 22）** | **正文只写"有什么"** | 否定式（不要出现/没有 X/禁止出现）**一律不进 H3 正文**——模型对否定不敏感、对词根敏感，被禁概念的词根留在稿子里就会被渲染；改成正向表述（机检 H8 否定式告警；C19 同口径） |
| **反光道具（法则 23 · C20d）** | 材质本色 | 玉佩/银镯等反光道具**零光效描写**（不写 光斑/受光/照射/亮起），只写材质本色（青玉原色/哑光金属本色），动作上不靠近光源 |
| Hit-Stop / 顿挫 / 蓄力 / 打击感 | 可见物理描述 | "接触的一拍里短暂凝住 + 反作用力"；**"顿挫/阻尼/弹开/压缩蓄力"禁进正文** |
| 【接续状态】 | **无对应栏** | 末帧画面信息写进该段**末镜句尾**（谁+在哪+姿态+道具状态，可画出一帧），供下一段 I2VA 首帧或段缝参考图使用 |
| 【音效】【强制禁止项】 | **不进正文** | H3 正文只写"有什么"；禁止项由执行者侧管理（栏目纪律见法则 22） |
| 段时长 | ≤15s | 本包每组 ≤15s 天然合规；**Seedance 2.5 的 15~30s 长段必须再拆一刀** |

---

## 三、H3 硬约束（写死 · 机检兜底）

1. **时长 4–15 秒**（官方规格表逐字）：与请求时长严格对齐；不支持超过 15s 的单段。
2. **参考素材上限（Ref2VA）**：图像 **≤9 张**；视频 ≤3 段（每段 2–15s、总 ≤15s）；音频 ≤3 段（**必须与图像或视频同时使用，不能作为唯一输入**，每段 2–15s、总 ≤15s）；**混合输入文件总数 ≤12 个**。超限走 §四 取材策略。
3. **画幅六档**：`21:9 / 16:9 / 4:3 / 1:1 / 3:4 / 9:16`（比 B 锁多 **4:3 / 3:4**）；参考类模式用 `auto` / `adaptive`（等同本包参考模式②的自适应）。
4. **输出规格**：24 FPS、32 kHz 立体声、默认短边 768；2K 走 `H3-Regenerate-2K` 重生成（可选）。
5. **语言（2026-10-02 按官方指南修正）**：**六段正文一律英文**——官方 base-en/ref-en 明文 "Write all six rewrite sections in English"；**只有 `<d>` 内台词/歌词与双引号内画内文字保留原语言**（中文台词写 `<d>[Chinese] …</d>`；中文是其稳定支持的 11 种对话语言之一，台词无障碍）。固定英文的还有：字段名、保留度标记、标签、`(Sx)`、时间码 `MM:SS.mmm`、切镜动词、`says in an off-screen voiceover` 等官方绑定短语。机检 H4 对 `<d>` 外中文字符告警。
6. **正文只写"有什么"**：禁否定式指导（"不要出现 X"）、禁 `@` 锚点、禁七段式栏名（【画幅风格】【站位声明】【接续状态】【强制禁止项】等）、禁工作流规则词（末态继承/拼接节点/换机位）、禁坐标/ASCII 布局。
7. **保留度标记是固定英文值**：画面 `fully_preserved` / `partially_preserved` / `attribute_transfer` / `weak_reference`；音频 `fully_copy` / `partially_copy` / `reference` / `weak_reference`。**`retention_analysis` 里不写 `(Sx)`。**
8. **说话人编号**：按**本段实际发声顺序**从 `(S1)` 起编，未发声角色**不给 ID**；同段内一致。一集拆多段分别生成时，每段独立重编即可（H3 每段零记忆）。
9. **任务类型前缀**（`summary` 段首）：`keyframe completion` / `reference generation` / `video editing` / `video continuation` / `audio reuse` / `audio reference`，多类型用 ` + ` 连接。可由本包状态直接推导：模式②首尾帧→`keyframe completion`；模式①全能参考→`reference generation`；段缝续写原片→`video continuation`；音频复用→`audio reuse`/`audio reference`。
10. **体量**：`detailed_description` 官方英文口径 350–500 词（15s 段按此写满）；中文按同信息量折算，**宁细勿简**，但不得靠注水凑字（呼应法则 17 禁拉伸）。
11. **语气位必须继承（对应法则 19）**：H3 没有台词语气位字段，但**官方同样要求把 delivery 写在 `<d>` 外**——转换时**不得丢掉语气信息**（机检 H11 告警）。说话人首次出现按官方要求给足**声学身份**（age / gender / on-screen / pitch / timbre / rate / accent，英文写入 `<d>` 外）；同性别多说话人按官方 issue #17 拉满声学对比，或拆成"一段一开口者"。
12. **摆位必入画必须继承（对应法则 20）**：H3 没有【站位声明】栏，但**人在画面里凭空消失同样是 H3 的穿帮**——每段至少给每个摆了位的人一个镜头，或写明出画/退场（机检 H5 兜底）。
13. **首镜锚定与单主体必须继承（对应法则 21 / 23）**：`[Shot 1]` 必须有**一个具名主体**（禁空镜无标注）；锚定句**只由单一主体统摄**，禁「X 与 Y 同框」并列句式（会把同一主体的手与脸渲染成两张脸），禁悬空指示代词（机检 H12a/b/c）。
14. **抽象形容必须具象化（对应法则 23）**：成线/成串/如注/轻蜷 这类抽象形态副词，模型只渲染可命名的具象形态——一律改写为可见形态（机检 H12 同族；与 C20c 同口径）。
15. **禁令只走正向（对应法则 22）**：否定式不进正文；被禁概念的词根（空镜里的"空镜"、不发光里的"发光"）哪怕挂着"不/禁"也照旧被渲染（机检 H8 否定式告警）。
16. **多说话人风险（官方 issue #17 · open 未修复 · 2026-10-02 收录）**：多说话人声音身份互串为官方已知缺陷，**同性别多说话人必崩**（社区已在付费闭源版复现）；模型按粗声学特征（音高/共振峰）分人而非按提示词绑定。缓解四条：① 说话人声学画像拉满对比（音高/音质/语速反着写）；② 同段尽量只留一个开口者（拆段）；③ 非对白人声词（轻笑/抽气/窃语类）清理为群杂环境音或删除——有实测因一句未格式化的 chuckle 打乱全段路由；④ 声音只前进不回头（A→B→A 恢复旧声必翻车，社区 workaround = 给回归说话人换新音频槽位）。

---

## 四、9 张取材策略（Ref2VA 必备）

角色资产全量投喂会**瞬间超限**（4 View × N 人 + 场景 + 道具 ≫ 9）。取值优先级：

| 优先级 | 取材 | 说明 |
|---|---|---|
| ① | **具体帧锚图** | 首帧 / 尾帧 / 构图锚（`<Picture N>` 独立条目）——锁定动作起止态，最高优先 |
| ② | **主要角色** | 每个角色的 **4 View 资产板算 1 张图**（板内四格）；主角优先，配角次之 |
| ③ | **核心场景** | 场景**拼接图**优先于母版（信息密度高：左 2/3 鸟瞰 + 右 1/3 四向） |
| ④ | 对手 / 次要角色 | 同 ②，1 张/人 |
| ⑤ | 道具 | 多件**拼一板**算 1 张 |
| ⑥ | 动作 / 运镜参考视频 | ≤3 段，每段 2–15s |
| ⑦ | 音色 / BGM 音频 | ≤3 段，**必须挂一张图或一段视频**才能投（音色锁只服务 2.5，H3 侧作 `reference_audio` 投） |

- 计数口径：**图 ≤9、视频 ≤3、音频 ≤3、总数 ≤12**。
- 超限处置：保 ①②③，其余降级为**文字描述**写进对应 `<Subject N>` 定义行（不丢信息，只丢"图锁定"强度）。
- 素材用途必须在定义行写清（锁形象 / 锁动作 / 锁音色 / 锁节奏），呼应本包"参考素材必须标注用途"铁律。
- ⚠️ **别把额度浪费在"定义了却不引用"的素材上**：给了图却在正文一次没提到的 Subject，等于白占 9 张里的一个位（机检 H5 告警）。

---

## 五、投喂路径与载荷（P4 封装）

**路径 B（本包主线）· 本地/自建 H3-Base**——结构化稿直接进 `prompt`：

```json
POST http://<host>:30011/v1/videos
{
  "task": "ref2va",
  "prompt": "<本包转出的六段式全文>",
  "conditions": [ { "type": "image|video|audio", "uri": "…", "role": "reference" } ],
  "target": { "short_edge": 768, "aspect_ratio": "auto", "duration_seconds": 12 },
  "seed": 0
}
```

**路径 A（可选）· 官方托管 H3-Context-IR**——只给自然语言 + 素材，官方自己出结构化稿：

```json
POST {MINIMAX_API_BASE}/v2/h3_context_ir
{ "model": "MiniMax-H3",
  "content": [ { "type": "text", "text": "<自然语言指令>" },
               { "type": "video_url", "video_url": { "url": "…" }, "role": "reference_video" },
               { "type": "audio_url", "audio_url": { "url": "…" }, "role": "reference_audio" } ],
  "duration": 5, "ratio": "adaptive" }
```

> 走路径 A 时剧作质量由官方 Context-IR 决定（**这就是用户判断"官方提示词不如本包"的那一环**）；本包价值集中在**路径 B 的 `prompt`**。

---

## 六、机检（H1~H16 · `scripts/validate_prompt.py --model h3`）

选 H3 支线后，出稿改用 H 系列门（C1~C20 是 Seedance 侧，不套用）：

| 门 | 检查 |
|---|---|
| H1 | 字段集完整：T2VA/I2VA/FL2VA/L2VA → 三字段；Ref2VA → 六段式且**顺序正确** |
| H2 | `[Shot 1]` 无时间戳；后续切点 `[Shot N] At MM:SS.mmm,` 严格递增且 ≤ 段时长；切镜动词用官方绑定短语（the camera/shot cuts to…） |
| H3 | 时长落在 **4–15s**，且与载荷 `duration_seconds` 一致 |
| H4 | **正文应为英文**（官方 base-en/ref-en；`<d>` 与双引号画内文字之外出现中文 → WARN）；`<d>` 必须有语言标签、台词保原语言未被翻译 |
| H5 | 标签先定义后引用（Ref2VA）；无未定义标签；`summary` 不引入新标签；**定义项 >9 告警**；**定义了却在正文一次未引用 → 告警**（别白占 9 张额度 / 人物凭空消失） |
| H6 | 保留度标记取值为合法英文固定值；`retention_analysis` 不含 `(Sx)` |
| H7 | `(Sx)` 按首现顺序编号；未发声角色无 ID |
| H8 | 泄漏检查：七段式栏名【】/`@` 锚点 → FAIL；工作流规则词/内部术语/**否定式** → WARN（否定式对应法则 22/C19） |
| H9 | 画外声含闭口证据（"lips remain completely closed" 紧跟 `</d>`）；官方固定短语 `says in an off-screen voiceover` 缺失 → WARN；禁用 `{}` 锁口型 |
| H10 | 声音分层：`overall_soundscape` 不含台词；BGM 只出现在 `non_diegetic_music`；BGM 段不复述台词 |
| H11 | **语气位继承（WARN）**：发言人首次出场处缺语气/音色/语速描述 → 告警（对应法则 19） |
| H12 | **首镜锚定与单主体（WARN）**：a) `[Shot 1]` 无具名主体；b) 并列主体/同框句式；c) 悬空指示代词（对应 C18a / C20a / C20b，即法则 21/23） |
| H13 | （V7.0）分镜/规划图 retention 用 fully/partially_preserved，或正文对分镜写 begins from / keyframe corresponds to / ends on → WARN |
| H14 | （V7.0）正文低能量词（gliding/steady/smooth/drifting/unhurried/gentle/slow speed）≥2 处 → WARN（文戏段可忽略） |
| H15 | （V7.0）slow motion / held beat / freeze / pause 等静止词（含否定句）→ WARN |
| H16 | （V7.0）单个 [Shot] 台词按 4.2 字/秒 > 3 秒 → WARN（长台词拆镜） |

---

## 七、核对来源（2026-09-19 逐条核对，非推测）

- 官方仓库 `MiniMax-AI/MiniMax-H3`：`README.zh-CN.md` 的 **case-T2VA / case-I2VA / case-Ref2VA** 三段 **H3-Context-IR 真实输出 JSON**（`task.content.prompt`）→ 字段名、段序、标签、保留度标记、`(S1)`、`<d>[Language]`、镜号切点、任务类型前缀全部逐字对上。
- `skills/h3-prompt-writing/SKILL.md` + `references/base-en.txt` + `references/ref-en.txt`（基础模式指南 / 全参考六段式指南）。
- 官方规格表：输出时长 **4–15 秒**、宽高比含 `21:9/16:9/4:3/1:1/3:4/9:16`、24 FPS、32 kHz 立体声、短边 768 默认、2K 走 `H3-Regenerate-2K`、稳定支持 11 种对话语言（含中文）。
- 模型变体与输入规格（FL2VA / Ref2VA 两 checkpoint，图像 ≤9 张等上限）。
- `scripts/readme/*.sh` 真实请求体（路径 A / 路径 B 两套载荷）。
- ⚠️ **真人脸红线：H3 官方没有这条**（官方只有通用内容审核：违法/色情/侵权拦截）。**不得把 Seedance 的真人脸素材红线照搬到 H3 支线。**

> **2026-10-02 官方复核增补**：重拉官方仓库 live 文件逐字比对（`skills/h3-prompt-writing/references/base-en.txt` / `ref-en.txt` / `README.zh-CN.md`，与 HuggingFace `docs/VIDEO_PROMPT_WRITING_GUIDE_*.md` diff 逐字一致），修正正文语言口径——旧"跟随内容主语言（中文项目写中文）"与官方 "**Write all six rewrite sections in English**" 冲突，以官方为准；新增官方 issue #17（多说话人声音身份互串，open，同性别必崩）、切镜动词官方绑定短语表、`says in an off-screen voiceover` 画外声公式。
> 参考样片（本包配套示例，非规则；⚠️ 旧中文正文格式，正文语言与切镜动词以 2026-10-02 修订为准）：`projects/H3-样片/H3-文戏样片.md`、`H3-打戏样片.md`。
