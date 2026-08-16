# HELL GRIND 开源 95 分钟电影提示词 · 分类方法论

> 来源：Higgsfield 开源 AI 电影《HELL GRIND》（95:06，全提示词/资产/画布开源）。
> 本文件将该项目的全部提示词内容按**可复用方法论**分类提炼，供漫剧/AI 短剧生产直接套用。
> ⚠️ V4.1.3（2026-08-16）：原始逐段全文（252KB 全集）已应要求移除，本方法论文件为唯一保留件。

---

## 一、提示词骨架（PROMPT FRAMEWORK）——每段提示词的顶层结构

HELL GRIND 所有长提示词共用同一套骨架，按此顺序组织，缺一不可：

```
SCENE CONTEXT       场景上下文（承接上一镜，1-2 句）
STRICT / WORLD LOCK 铁律区（本段所有硬约束集中声明）
ACTIVE REFERENCES   本段激活的资产引用清单（角色/场景/道具 @引用）
LOCATION MAP        空间布局锚点（方位/距离/几何关系）
FIRST FRAME         第 0 帧画面状态（开局即定）
FORMAT MODE         格式（时长/画幅/帧率/慢动作策略）
OPTICS              光学（胶片/镜头/颗粒/快门）
CAMERA              摄影机（运镜/机位/性格）
ACTION TIMING       动作时间轴（逐 beat 秒级编排）
PHYSICS             物理（重量/惯性/接触阴影）
LIGHTING            光线（光源/色温/方向）
AUDIO               声音（环境 SFX/台词/音乐规则）
CHARACTER ACTING    表演（微表情/反应节奏）
STYLE               风格（导演风格转述/质感）
QUALITY             质量（8K/毛孔级皮肤/实拍感）
POSITIVE CONSTRAINTS 正约束（明确"画面里必须有"什么）
```

**关键设计原则：**
- 骨架字段按"**信息被 AI 消费的优先级**"排序——铁律和空间关系在最前，动作在中间，风格质量收尾
- 每个字段只写一次，后面动作段**直接引用**前面锁定的内容（"Camera rules continue"），不重复堆砌
- 结尾固定写 `References = visual identity / costume / environment matching only. Generate 100% original continuous live-action cinematography from scratch.` —— 参考图只做身份/风格匹配，动态画面 100% 原创生成

**对比本 skill 五段式【风格→色卡参考→镜头→时间轴→声音】：** 本 skill 是短内容（≤15s/段）的紧凑结构；HELL GRIND 骨架是长内容（多镜头/多 cut）的展开结构。两者互补——短段用五段式，长段/多镜头段用本节骨架。

---

## 二、资产引用体系（REFERENCE SYSTEM）——长片一致性的根基

### 2.1 资产编号规则
- 每个资产（角色/场景/道具）用 `<<<uuid>>>` + `[imageN]` 双标识，文字描述兜底
- **同一角色分状态建资产**：如 `@roco`（常态）/ `@roco_wet`（湿身）/ `@roco_blood`（带伤）——同段提示词只激活需要的状态
- 关键道具独立建资产：`<<<e396547e...>>>`（水晶剑）、`<<<fdb45b20...>>>`（平板）、`<<<8673588e...>>>`（炸弹盒）

### 2.2 引用使用规则（三段式约束）
1. **身份引用**：角色/场景/道具的完整外观只在资产里定义，提示词正文只写"怎么用"
2. **状态引用**：`@roco_wet` 这种状态资产，提示词里写明"wet state only"或"bare-arm state"
3. **切换引用**：角色中途变身/受伤时，用"IDENTITY SWITCH"规则显式声明——`<<<A>>> → <<<B>>>`，从某帧起只用 B，杜绝中途漂移

### 2.3 参考图纪律
- 所有参考图标注用途：`CHARACTER REF — appearance only` / `SCENE REF — space only` / `ELEMENT REF — appearance only, do not copy framing` / `Style/element reference only`
- 场景参考图分**正面/背面**（FRONT SIDE / BACK SIDE）两张，明确哪个方向有什么
- 环境参考图允许继承"风格/色调/氛围"，**禁止复制构图和机位**

---

## 三、统一大气指令（GLOBAL ATMOSPHERE LOCK）——跨镜头一致性的杀手锏

HELL GRIND 对战场类场景发明了"统一指令"模式：**把贯穿所有镜头的大气参数单独写成一块，要求每段提示词原样复制**。这是长片不漂移的核心秘密。

### 3.1 锁定参数清单（每个都要写死）
| 参数 | 写法示例 |
|------|---------|
| 色温 | `整个画面色温约4500K冷阴天日光` |
| 雪暴等级 | `blizzard级暴雪，每帧至少100-200片可见雪花，大型雪片+细雪粒共存` |
| 能见度 | `能见度严格限制在30-50米` |
| 调色板 | `60:30:10：60%白雪+30%冷蓝灰雾+10%暗酒红（唯一暖色强调）` |
| 光线 | `完全overcast冷漫射光，无阳光直射，无阴影硬度` |
| 地平线 | `无可见地平线，天空+雪原+雾融合为连续灰白色调` |
| 风向 | `主导风向从画面左侧吹向右侧，偶尔反转` |

### 3.2 无限军团模式（无尽援军/地下再生）
- **无尽援军**：每 2-3 秒从画面边缘/雾里冲出 3-5 个新敌人，旧敌倒下立即填补——战场永远不会少敌人
- **地下再生**：骷髅手破雪抓出/头颅顶起雪面/整身爬出，每镜至少 5-8 次，常在前中景明显位置
- **第 0 帧已在战场中心**：没有"开始战斗"过渡，第 0 秒就已被包围，无静止帧
- 后景敌人运动矢量永远指向主角（朝中心涌动）

### 3.3 史诗规模写法
- 不写"数万"这种不可渲染数量词 → 写 `单帧可见500-1000人，暗示10000+在更远处`、`后景延伸到雾里看不到尽头`
- 人群不是克隆：写 `3种武士样式混合，任何一帧同时可见几种不同样式`（精英/中级/腐朽三级混合）
- 混乱无序指令：`不是整齐战线，是混乱无序的死亡狂潮，各方向各速度各高度各姿态`

---

## 四、铁律区写法（STRICT / HARD LOCK）——用"必须有"代替"不要"

### 4.1 正约束（POSITIVE CONSTRAINTS）
写"画面里**必须有**什么"，而非"不要什么"：
- `EXACT 3 CHARACTERS` / `STRICT: EXACTLY FOUR. No duplicates` —— 精确人数
- `jaxx = ONLY dark skin yellow hair, black leather gloves always` —— 每角色外观唯一锚点
- `在镜头第0帧，两支yari长矛绝对必须由骑兵双手紧握` —— 关键道具开局状态锁死
- `盾牌开拍前已长好` / `shield ALREADY GROWN at start` —— 避免生成中途变化

### 4.2 硬锁清单（HARD LOCK）
慢动作、位置锚点、角色解剖、动作编排、硬切转场、光线——**每个都单独列一条 HARD LOCK**：
```
⚠️ SLOW MOTION (HARD LOCK): 全程慢动作 ~3-4x
⚠️ LOCATION ANCHORS (HARD LOCK): 弧形混凝土墙必须在两cut中都可见
⚠️ MONSTER ANATOMY (HARD LOCK): 右臂是骨刃，没有手没有指头
⚠️ ACTION CHOREOGRAPHY (HARD LOCK): 拳头触脸瞬间水晶尖刺爆发
⚠️ HARD-CUT TRANSITION (HARD LOCK): 只有一次硬切，无溶解无匹配剪辑
```

### 4.3 几何锁定（GEOMETRY / SPATIAL BLOCKING）
复杂空间关系写成可验证的几何描述：
- 罗盘定向：`NORTH = 天窗墙，SOUTH = 门洞墙，EAST = 怪物侧，WEST = 主角侧`
- 锁定距离：`两人间隔 EXACTLY 2.5 米`、`柱子距三人 NW 对角线 ~10.4 米`
- 锚点不动：`柱子固定在其建筑锚点，不跟随角色移动`
- 人物比例锚点：`怪物 360cm 高，头是人类的全身两倍高`、`人类主角 180cm`

---

## 五、动作编排（ACTION TIMING）——秒级 beat 写作

### 5.1 单镜头动作 beat 格式
```
动作(0-2秒, ...): [核心动作] + [SLOW-MOTION段落标记, 时间放慢4-6倍] + 慢动作细节 + [视频回到正常速度]
```
- 每个 beat 开头标注时间段，动作写清"谁做什么，结果如何"
- 慢动作段落在括号内显式标注（`[SLOW-MOTION段落]`），并说明放慢倍数
- 关键击杀/冲击瞬间用 `动态 CU插入: macro CU on ... (85mm, 0.5秒)` 插入特写

### 5.2 帧率渐变（IN-CAMERA FRAME RATE RAMPS）
一镜到底内的帧率切换写法（HELL GRIND 独创）：
```
60fps → 240fps（重慢动作，每个动作逐帧可读）→ ⚡10000fps（子弹时间，世界冻结，粒子悬空）
```
- 10000fps 只给 3 个峰值瞬间：抓握瞬间/落地反弹瞬间/爆炸绽放瞬间
- `所有ramp都在机内完成，同一镜头内，绝不是剪辑切`

### 5.3 多镜头段（multishot sequence）格式
```
multishot sequence — 15 SECONDS · 21:9 · 8K · 60fps · hard cuts only · exactly 6 numbered shots
```
- 每镜开头：`SHOT 1 — 0.0-2.5s — 标题: 24mm wide low...`
- 每镜之间：`HARD CUT — [大气参数锁定摘要]`（把必须延续的参数浓缩成一行，防止漂移）
- 每镜内：动作 → 背景反应（人群/环境如何响应）→ macro CU 插入

### 5.4 多角色时序拆分
同 §4.6.7 但更严格：每个 beat 只保一个主角色动作，其他角色只写"在场状态"（如"两人在背景做俯卧撑"），避免 AI 算力偏移。

---

## 六、战斗戏专项（COMBAT PROTOCOLS）

### 6.1 血液/死亡规则统一
- 不死系死亡 = 黑色尘雾/黑沙：`被切部位崩解成黑色烟雾，血液本质是黑色烟雾`
- 武器切割规则：`切开即崩解，两半在空中分离后整体变黑色尘雾爆发`
- 物理武器 vs 有机武器区分：`整条手臂变成水晶武器——不是握在手中的武器` / `骨刃是身体的一部分，没有手没有握柄`

### 6.2 战斗摄影机性格
- `非常活跃手持剧烈摇晃反应性相机，像战地摄影师冲入战场`——摄影机是第二个角色
- 反应性 jolt：`当Roco被打：摄影机急剧反应性jolt模拟冲击`
- 动态 CU 频率：`每0.5-1秒插入一个超快CU(0.2-0.5秒)`，用 whip pan 连接
- 参考风格转述：`Kurosawa Ran最终决战+Helm's Deep+300+Northman+Battle of the Bastards的史诗混合`

### 6.3 一镜到底战斗（ONER）
- `SINGLE CONTINUOUS HANDHELD ONER, NO editorial cuts`——无剪辑，whip-pan 是机内运动不是剪辑
- 三段结构：PHASE A 中段开场（in medias res）→ PHASE B 格挡反击波 → PHASE C 连杀狂潮 → PHASE D 持续战斗无结局
- 马匹规则：`马永不停在主角处，永不撞盾，从旁全速掠过像水流绕石`——写死 AI 容易翻车的物理规则
- 结尾不解决：`take ends mid-action`——战斗继续

### 6.4 体力/疲劳递进
长战斗戏写主角的疲劳递进：`呼吸更明显（呼气有白气）、转身稍慢、剑臂开始累、95%招架干净但有一刀擦过肩甲`——让 AI 呈现真实消耗感。

---

## 七、表演与情绪（ACTING & EMOTION）——SOLO PORTRAIT 范本

### 7.1 情绪弧线时间轴（10 秒单人特写范本）
```
0.0-3.0s 持续醒悟开始: 眼神下移看向伤者, 脸是敞开的, 瞳孔放大, 浅震惊呼吸
3.0-6.0s 醒悟加深为悲伤: 眉毛中心上挑(悲伤肌), 嘴唇抿紧, 胸口深颤呼吸, 一滴泪滑过血迹
6.0-10.0s 悲伤转为暴怒: 眼神抬起转向敌人方向, 瞳孔收缩, 眉毛下压, 下颌紧咬, 面部肌肉可见微颤, 太阳穴血管鼓起
```

### 7.2 表演硬规则
- **台词前后各留 1 秒静默**：`每句台词前至少1秒沉默，后至少1秒沉默`——镜头先拍脸再开口，说完继续 hold
- **台词内容绝不视觉化**：对白提到的人和事不出现在画面，无闪回无幻影
- **声音优先混音**：说话时环境声自动 duck 到低音量，声音干净近距离收音
- **只演剧本台词**：无即兴、无嘟囔、无多余叹息、无画外音；没台词就是沉默

### 7.3 毛孔级皮肤（皮肤=表演的一部分）
`pore-level realism — vellus hair（毳毛）, asymmetric moles（不对称痣）, capillary flush（毛细血管泛红）, pore-shadow matching on-set light`——皮肤细节跟光走。

---

## 八、环境镜头（ENVIRONMENT SHOT）——城市/自然空镜范本

### 8.1 城市航拍空镜（8 秒范本）
- 完整参数锁：`600米高度+15度前倾+地平线在y=35%+2.39:1+整段匀速右移`
- 运动层级：`摄影机: 匀速横移；环境: 斜雨贯穿每个景深；主体: 两辆车缓慢爬行；内部: 云层内3次无声片状闪电`
- 闪电时刻表：`0.8秒(深处中央云,150ms)+3.2秒(左侧中距云,200ms)+6.1秒(最右边缘云,120ms)`——每次配一声数秒后的闷雷
- 调色板锁定：`60:30:10：60%深炭灰阴影+30%冷青绿实用光(钠灯/窗格/雾气)+10%暖琥珀点缀(车窗/霓虹)`
- 连续性锁：`始终只有两辆车，第三辆永不出现；地铁高架始终空载；云层始终厚重永不散`

### 8.2 自然亲密空镜（5 秒范本）
- 机位：`手持中景开始 → 缓慢匀速后拉dolly → 两人从画面中心变小融入广阔自然`
- 情绪：`两人前额相抵静止 → 世界在他们周围展开`
- 负向清单极详细：`无音乐无接吻无慢动作无快移无抖动无变焦无航拍无仰拍无他人无胡须无纹身无首饰无对白无文字`

---

## 九、图像编辑提示词（IMAGE EDITING）——损伤修正范本

### 9.1 修正式编辑提示词结构
```
Edit this image. [总目标: 把损伤降到写实克制水平] Apply these corrections consistently across all views.
CHANGE 1 — [删除类]: 移除头发里白色针状物, 完全清除
CHANGE 2 — [削减类]: 面部伤口从"恐怖片受害者"减到: 右眉上一道2cm细线+右颧骨一处擦伤——完整清单就这两处
PRESERVE — [保留类]: 左侧永久疤痕原样保留, 所有新伤只在右侧
CHANGE 3 — [比例类]: 灰尘减少50%, 裤子/外套/皮肤分别说明
CHANGE 4 — [可读性]: 服装原色必须可读(黑裤是黑不是泥棕)
Final goal: [最终画面一句话]
```

### 9.2 修正类提示词原则
- 删除/削减/保留三类分开写，**每类独立成 CHANGE 块**
- 削减给"完整清单"：`这就是面部损伤的完整清单`——防止 AI 自己加戏
- 负向清单给具体参照物：`NOT horror movie victim, NOT covered in chunky debris, NOT caked in dirt`
- 保留项写死：身份/面部结构/体型/发型/服装/姿势/三视图布局/背景

---

## 十、统一风格前缀（STYLE PREFIX / GLOBAL STYLE BLOCK）

HELL GRIND 每段都带一段"基础设定前缀"，与 §1.7 基-氛-画 完全同构，可直接复用：

```
Style: 8K IMAX. Photorealistic — no 3D render, no game engine, no game-cutscene aesthetic.
Cinematography: Emmanuel Lubezki × Roger Deakins.   ← 用法: 转述为"自然光+逆光+大气雾霾", 不写导演名(§0.3红线)
Lighting: Natural light only — contre-jour backlight, camera on shadow side, atmospheric haze throughout.
Color: 60:30:10 — dominant / secondary / accent.
Camera: Physical cine lens. 180° shutter motion blur.
Skin: Pore-level realism — vellus hair, asymmetric moles, capillary flush.
Acting: Hollywood — micro-pauses before reactions, precise eye-line, wet living eyes with catch-lights.
Physics: Gravity and inertia respected — mass has real weight, correct contact shadows. No floating props.
Composition: Rule of thirds + golden ratio. Every person moving from frame one.
Continuity: Characters, props, environment identical across every cut. No identity drift.
Technical: 24fps smooth motion. 8K detail. No jitter.
Audio: Environmental SFX only. No music. No subtitles.
```

**导演风格转述表（HELL GRIND 实际用到的）：**
| 原参考 | 提示词转述写法 |
|--------|---------------|
| Lubezki × Deakins | 自然光+逆光（contre-jour）+大气雾霾+手持 |
| Kurosawa Ran | 动态对称构图+史诗战场+戏剧性天气+低饱和 |
| John Wick / The Raid | 一镜到底走廊打斗+干净利落击杀节拍+摄影机活在暴力里 |
| Terrence Malick Tree of Life | 亲密连接消融于广阔自然+缓慢后拉 |
| Cuaron Children of Men | 世界密度+手持长镜头 |
| Villeneuve Sicario | 监视级克制+低照度实用光 |
| 动漫终战（Bleach/鬼灭） | 爆裂动作+关键帧定格+"漫画静止帧"节拍 |

---

## 十一、项目级方法论总结（HELL GRIND 的工程秘密）

1. **一致性不是靠"记得"，是靠"复制"**——统一大气指令/无限军团指令/第0帧指令，要求每段原样粘贴
2. **资产是长片的命**——每角色每状态独立资产，变身用 IDENTITY SWITCH 切换
3. **正约束优于负约束**——"EXACT 3 CHARACTERS"比"不要出现第4个人"有效
4. **几何锁死**——罗盘+距离+锚点，AI 才不会让空间漂移
5. **硬切=状态摘要**——HARD CUT 后面跟一行大气参数摘要，防止切镜后漂移
6. **长片=多段骨架**——每段独立完整骨架，段间靠"Scene context: 承接上一镜"衔接
7. **负向清单收尾**——每段结尾列 AVOID/NEGATIVES，把最容易翻车的点列全

> 与 §0.3 红线的关系：HELL GRIND 提示词里直接写导演名（Lubezki/Deakins/Kurosawa），但本 skill 的 Seedance 实测红线要求**不写人名**——本文件所有示例均已转述为描述性写法（"自然光+逆光+大气雾霾"），直接可用。
