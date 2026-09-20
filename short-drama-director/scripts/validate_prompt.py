#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_prompt.py — 投喂提示词结构自检（V6.9 · 出稿时门禁）

只查可机械判定的结构/版本问题；空间/遮挡/轴线/动作物理/视线仍由 AI 语义推演
（见 spatial-topview-camera.md 与 quality-gate-review.md），本脚本不越权。

用法：
  python scripts/validate_prompt.py <提示词文件.md|.txt>
      [--model 2.5|2.0|h3] [--mode new|extend] [--json] [--self-test]

  • --model 2.5 / 2.0 → C1~C20（Seedance 侧，本文件主体）
  • --model h3        → H1~H12（MiniMax H3 格式支线，规程见 references/h3-adapter.md）

检查项（C1~C20）：
  C1 时长预算   段时长 ≤ 模型上限（2.5=30s / 2.0=15s）
  C2 切镜上限   镜头数 ≤ ceil(段长/3s)；单镜 <3s 告警
  C3 时间轴     相邻镜头无断档/重叠；time 倒挂拦截
  C4 字符预算   单段 ≤4500 字符
  C5 版本语法   2.0 禁 [SFX:] 与顿挫词；2.5 建议 [SFX:]
  C6 画幅回填   含 aspect_ratio= 或含画幅的【画幅风格】栏
  C7 七段式      核实七段式核心栏齐备（V6.8 唯一命名，不借外部示范格式）
  C8 首尾帧禁用  2.0 出现 首帧:/尾帧:/参考图绑定/Start Frame/End Frame 即拦截（2.0 全面禁用）
  C9 平台高危词  血腥/断肢/裸露/自伤/违法等高危词 → 拦截，走 platform-safety 替代表
  C10 单镜过长   单镜 >6s 告警（talking head 风险）
  C11 接续状态   时间轴分镜末镜后必带【接续状态】尾行（V6.9：纯套话"严格继承"告警，须写具体末帧画面）
  C12 否定式/规则词  正文出现"没有X/不要X"硬删除或"末态继承/拼接节点/换机位"等工作流规则名词 → 告警
  C13 镜长雷同   同段 ≥4 镜时，若同值镜长占比 ≥70% → 告警（节奏缺乏快慢呼吸，镜长应由台词÷语速倒推）
  C14 画外声（V6.9 新增 · vo-os-weaving.md）：
      FAIL  OS 镜行画面段含开口词（声画分离红线）/ OS·VO 写进台词字段 / OS·VO 使用 {} 锁口型
      WARN  段内 OS 镜数 >2 或 VO 镜数 >1；段内 VO+OS 总字数超折算上限（≈20 字/15s 段）
  C15 拉伸凑时（V6.9 修订 · 时长由内容倒推）：
      WARN  无台词镜单镜 >5s / 全段无台词（纯氛围段）时长 >10s——禁止把氛围/过渡镜拉长
            凑满剧本标注的【本集时长】；总时长允许比剧本标注短至 -25%，宁短勿拉
  C16 对白语气（V6.9.3 新增 · model-adapters §5.2 官方对白三要素之三 HOW THEY SOUND）：
      WARN  语气错位（有台词镜行的画面段出现声音词——会被模型当视觉信息渲染）
            语气缺失（有台词镜行未写 `【角色（语气）：“…”】` 的占比 > 50%）
            语气位含空泛结果词（开心/难过/愤怒…，应按四维改写）
            道具动作与语气冲突（V6.9.7 续 · C16d：宣判/强情绪语气位配 把玩/摩挲 等闲适
            道具动作——实测出戏：正俯视宣判还在把玩玉佩。改攥紧/捏住/垂手握着）
  C17 摆位必入画（V6.9.3 续 · model-adapters §5.0.1 人物账连续）：
      WARN  站位声明摆位 ≥2 人时，某人名在全段镜行中一次都未出现、且无 离画/退场/未入镜
            标记 → 人物凭空消失，跨段衔接必穿帮；单人站位段不触发（无跨段风险）
  C18 首镜锚定·景别一致·姿态延续·视线指派（V6.9.4 新增 · model-adapters §5.0.2，
      病灶实测：「重生70」EP01 段1 出片空床无人/视线黏玉佩/清月躺回）：
      WARN  C18a 段首镜：全段第 1 镜既无站位人名、也未声明「空镜」→ 首镜无人物锚，
            模型渲染出空场景（实测出"只有一张床"）
      WARN  C18b 姿态回退：前镜已 撑起/坐起/起身/弹起，后续镜行又出现 躺/卧/蜷/瘫
            且无 跌回/躺回/倒回 等交代 → 状态回退穿帮
      WARN  C18c 视线黏道具：有台词镜行画面段含 把玩/摩挲/摆弄 或 举向/捧向（光源·高处），
            却未写 目光/视线/不落/不离 → 模型默认视线黏在道具上，说话不看人
      WARN  C18d 景别冲突：特写/紧特写/大特写承载空间级事件（房顶/屋顶/屋子/门口/窗外/
            全景…）→ 特写装不下全屋信息，模型只好丢人物保空间（实测出空床）
      WARN  C18e 反光道具（玉佩/银镯/镜面类）镜行无反光道具光效声明：既无正向材质描写
            （实心石质/哑光/原色/光斑）也无声明 → 被渲染成自发光半透明"魔法道具"
  C19 禁令失效三改法 + 栏目纪律（V6.9.5 新增 / V6.9.6 续增 · model-adapters §5.0.4，
      病灶实测：三条否定式禁令两轮全被无视——空房间开场/玉佩全片自发光/宣判词配甜笑）：
      WARN  C19a 裸禁令词污染：镜行内出现 不发光/不透光/不悬浮/面无笑意 等否定式写法
            → 模型对词根敏感，被禁概念词根反被当画面词渲染；改正向材质/肌肉/光路描写
      WARN  C19b 光路触发器：反光道具被 举向/对着/冲向 灯或光 → 正对光源诱发透光自发光
      WARN  C19c 首镜主体优先：段镜1第一个分句以环境开头、人物在后 → 诱导空场景开场
      WARN  C19d 具象光源映射污染：反光道具镜行写 映出/倒映/映着 + 火苗/灯火
            → 模型把「映出+光源名词」读成光源出现在道具上；改写光斑语言
      WARN  C19e 禁止项栏目纪律：e-a 正向执行指令（首帧/保持材质/必须以…为主）混入
            【强制禁止项】→ 该栏被当规避清单读，正向要求两头不生效；e-b 禁止项内出现
            裸禁令词（不发光/面无笑意）→ 否定式同样失效。禁止项只装画面/文字/音频负面清单
  C20 首镜单主体锚定 + 抽象形容（V6.9.7 新增 · model-adapters §5.0.2/§5.0.4，
      病灶实测：「重生70」EP01 段1 镜1 出片两张脸——镜行「首帧即这只手与她的脸同框」）：
      WARN  C20a 并列主体/同框句式：镜行出现 同框/同在画面/一同入画/与…同处 等并列主体写法
            → 模型把「X 与 Y 同框」读成画面里有两个主体（同一主体的手与脸被渲染成两个头/
            两张脸）。首镜锚定句只由**一个具名主体**统摄，部位以「她的/其+部位」从属出现
      WARN  C20b 悬空指示代词：镜行出现 这只手/那张脸 类指代词+身体部位且无归属定语
            → 指代词没有先行词，模型自行补全一个主体（多补出一个头）。改写为「她的一只手」
      WARN  C20c 抽象形态形容：镜行出现 成线/成串/如注/轻蜷/微蜷 等抽象形态·程度副词
            → 模型只渲染可命名的具象形态，抽象副词不被理解（实测「漏雨成线」「手指轻蜷」）。
            改写为可见形态：「雨滴砸在手背上溅开」
      WARN  C20d 道具光效描写：反光道具（玉佩/银镯等）与 光斑/受光/照射/照在/亮起 共现，
            或道具被 举到/凑到 灯火旁——V6.9.5 的"光斑语言"实测仍被渲染成玉佩点火
            （用户：「玉佩上面像个打火机，点了一簇火」）。反光道具**零光效描写**，
            只写材质本色（青玉原色/哑光金属本色），动作上不靠近光源

H 系列（--model h3 · MiniMax H3 格式支线 · V6.9.8 新增 · h3-adapter.md）：
  H1 字段集       Ref2VA 六段齐全且顺序正确；基础模式三字段齐全
  H2 镜号/切点    [Shot 1] 不得带时间戳；[Shot N] 切点 MM:SS.mmm 严格递增
  H3 时长         声明时长落在 4–15s；最后切点 ≤15s
  H4 语言标签     <d> 内必须带语言标签（<d>[Chinese] …</d>）
  H5 参考标签     标签先定义后引用；summary 不引新标签；定义项 >9 告警；定义了却未引用 → 告警
  H6 保留度标记   只用合法英文固定值；retention_analysis 不写 (Sx)
  H7 说话人       (Sx) 按首现顺序从 (S1) 递增编号
  H8 泄漏         七段式栏名/`@` 资产锚点 → FAIL；工作流规则词/内部术语/否定式 → WARN
  H9 画外声       画外声必须紧跟闭口证据；禁用 {} 台词字符
  H10 声音分层    soundscape/music 段不得含 <d>；BGM 段不得复述台词
  H11 语气位继承  发言人首次出场缺语气/音色/语速描述 → WARN（对应法则 19）
  H12 首镜锚定    对应 C18a/C20a/C20b：[Shot 1] 无具名主体 / 并列主体句式 / 悬空指示代词 → WARN
"""
import json
import os
import re
import sys

LIMITS = {"2.5": 30, "2.0": 15}
MAX_CHARS = 4500

TIME_RE = re.compile(
    r"(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?\s*[-~～→]\s*(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?"
    r"|(\d+(?:\.\d+)?)\s*s\s*[-~～→]\s*(\d+(?:\.\d+)?)\s*s", re.I)

# 七段式核心栏（V6.8 model-adapters §5 唯一权威；【接续状态】是【时间轴分镜】尾行，不单列）
SEVEN_SEGMENTS = ["【画幅风格】", "【场景资产】", "【核心人物】", "【站位声明】", "【时间轴分镜】", "【音效】", "【强制禁止项】"]

GORE_WORDS = ["鲜血", "血喷", "血迹", "血溅", "血肉模糊", "鲜血淋漓", "喷血", "流血", "断肢", "截肢",
              "断臂", "断头", "碎尸", "四分五裂", "尸体", "死尸", "惨死", "内脏", "肠子", "脑浆",
              "开膛破肚", "割喉", "绞杀", "虐杀", "凌迟", "透体", "捅穿", "刺穿", "砍断", "撕裂",
              "伤口", "骨裂", "骨骼断裂", "切开", "劈成两段", "斩为两段", "切成两半", "劈成两半",
              "深可见骨", "可见骨", "血污", "血淋淋", "断指", "开膛", "破腹", "掏心", "剥皮",
              "裸体", "裸露", "走光", "露点", "床戏", "自杀", "自残", "割腕", "上吊", "吸毒", "嗑药", "吸毒贩毒"]

# ---- C14 画外声（OS 内心独白 / VO 旁白）——规程见 references/vo-os-weaving.md ----
OS_PAT = re.compile(r"内心独白|（\s*OS\s*）|\(\s*OS\s*\)|\bOS\b|心声")
VO_PAT = re.compile(r"旁白|画外音|（\s*VO\s*）|\(\s*VO\s*\)|\bVO\b")
# 声画分离红线：OS 发声期间画面不得张嘴（只检"声音："前的画面段，防台词文本误伤）
MOUTH_PAT = re.compile(r"张嘴|开口|说道|说着|喊道|喊着|呐喊|嘴里念|嘴唇张开|嘴里说着|开口道|开口说")
VO_OS_QUOTA = 20          # 每 15s 段 VO+OS 总字数折算上限（60~80 字/分钟）；WARN 用
VO_OS_QUOTA_SLACK = 5     # 机检容差线
OS_MAX_SHOTS = 2          # 段内 OS 镜数上限
VO_MAX_SHOTS = 1          # 段内 VO 镜数上限

# ---- C15 拉伸凑时（V6.9 修订 · SKILL 法则 17）——时长由内容倒推，禁拉伸凑满剧本标注时长 ----
NO_DIALOG_SHOT_MAX = 5    # 无台词镜单镜时长上限（s），超出即拉伸嫌疑
PURE_AMBIENT_SEG_MAX = 10 # 全段无台词（纯氛围段）时长上限（s）

# ---- H 系列：MiniMax H3 格式支线（V6.9.8 · references/h3-adapter.md）----
H3_SECTIONS = ["subject_definitions", "summary", "retention_analysis",
               "detailed_description", "overall_soundscape", "non_diegetic_music"]
H3_FIELDS = ["integrated_multimodal_description", "overall_soundscape", "non_diegetic_music"]
H3_MARK_VIS = {"fully_preserved", "partially_preserved", "attribute_transfer", "weak_reference"}
H3_MARK_AUD = {"fully_copy", "partially_copy", "reference", "weak_reference"}
H3_LABEL_RE = re.compile(r"<(Subject|Picture|Video|Audio)\s+(\d+)>")
H3_SHOT_RE = re.compile(r"\[Shot\s+(\d+)\]")
H3_CUT_RE = re.compile(r"\[Shot\s+(\d+)\][^\n]{0,14}?(?:At|在)\s*(\d{1,2}):(\d{2})\.(\d{3})")
H3_SEVEN_LEAK = ["【画幅风格】", "【场景资产】", "【核心人物】", "【站位声明】", "【时间轴分镜】",
                 "【音效】", "【强制禁止项】", "【接续状态】"]
H3_JARGON = ["顿挫", "阻尼", "弹开", "微停顿"]
H3_WORKFLOW = ["末态继承", "拼接节点", "换机位", "同机位硬接"]
H3_MIN_DUR, H3_MAX_DUR = 4, 15
H3_PIC_MAX = 9
H3_VO_EVID = re.compile(r"闭合|闭口|紧闭|lips\s+(?:remain|stay)\s+(?:completely\s+)?closed")
H3_TONE_HINT = re.compile(r"音色|语气|语速|声线|嗓音|男声|女声|童声|气息|平直|平稳|低沉|沙哑|清亮|清冷|温润|明亮|"
                          r"浑厚|尖锐|急促|缓慢|克制|冷淡|温和|冰冷|慵懒|疲惫|哽咽|颤|喘|轻声|低声|高声|低语|耳语|呢喃|"
                          r"压着|斩钉截铁|喊|吼")
# H8 否定式（对应 C19/法则 22：模型对否定不敏感、对词根敏感；H3 正文只写"有什么"）
H3_NEG_PAT = re.compile(r"不要出现|不要有|禁止出现|不能出现|不得出现|"
                        r"没有[\u4e00-\u9fa5]{0,4}(?:人物|角色|家具|背景|文字|字幕|水印)")
# H12 首镜锚定 / 单主体（对应 C18a / C20a / C20b）
H3_PARALLEL_PAT = re.compile(r"同框|同在画面|一同入画|同处一室")
H3_DEIXIS_PAT = re.compile(r"(这只|那只|这个|那个|这双|那副)(手|脸|眼睛|脚|背影|身体)")


def _h3_order(text):
    """返回出现过的六段字段名，按文件顺序。"""
    pat = re.compile(r"^\s*(" + "|".join(H3_SECTIONS) + r")\s*[:：]")
    out = []
    for line in text.splitlines():
        m = pat.match(line)
        if m and m.group(1) not in out:
            out.append(m.group(1))
    return out


def _h3_sections(text):
    """按行首字段名+冒号切分，返回 {字段: 内容}。"""
    pat = re.compile(r"^\s*(" + "|".join(H3_SECTIONS) + r")\s*[:：]\s*(.*)$")
    out, cur = {}, None
    for line in text.splitlines():
        m = pat.match(line)
        if m:
            cur = m.group(1)
            out[cur] = [m.group(2)]
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def validate_h3(text, mode="new"):
    """MiniMax H3 格式支线检查（H1~H12）。规程见 references/h3-adapter.md。"""
    issues, warns = [], []
    sec = _h3_sections(text)
    order = _h3_order(text)
    is_ref = "subject_definitions" in sec

    # H1 字段集
    if is_ref:
        missing = [s for s in H3_SECTIONS if s not in sec]
        if missing:
            issues.append(f"H1 Ref2VA 缺段 {missing}（六段式：subject_definitions/summary/retention_analysis/"
                          "detailed_description/overall_soundscape/non_diegetic_music，顺序不可调换）")
        elif order != H3_SECTIONS:
            issues.append(f"H1 Ref2VA 段序错误：实际 {order}")
    else:
        missing = [f for f in H3_FIELDS if f not in text]
        if missing:
            issues.append(f"H1 基础模式缺字段 {missing}（应为 integrated_multimodal_description / "
                          "overall_soundscape / non_diegetic_music）")

    # H2 镜号与切点（只看正文分镜段：Ref2VA 取 detailed_description，基础模式取全文）
    body = sec.get("detailed_description", "") if is_ref else text
    if re.search(r"\[Shot\s*1\][^\n]{0,14}?(?:At|在)\s*\d{1,2}:\d{2}", body):
        issues.append("H2 [Shot 1] 不得带时间戳（首镜无切点，切点从 [Shot 2] 起）")
    nums = [int(n) for n in H3_SHOT_RE.findall(body)]
    uniq = list(dict.fromkeys(nums))
    cuts = [(int(m[0]), int(m[1]) * 60 + int(m[2]) + int(m[3]) / 1000.0) for m in H3_CUT_RE.findall(body)]
    if uniq:
        if uniq != sorted(uniq):
            issues.append(f"H2 [Shot N] 镜号未递增：{uniq}（首现顺序）")
        want = [n for n in sorted(set(nums)) if n >= 2]
        got = [n for n, _ in cuts]
        miss_cut = [n for n in want if n not in got]
        if miss_cut:
            issues.append(f"H2 [Shot {miss_cut}] 缺切点时间码（MM:SS.mmm）")
    for (n1, t1), (n2, t2) in zip(cuts, cuts[1:]):
        if t2 <= t1:
            issues.append(f"H2 切点未严格递增：[Shot {n1}] {t1}s -> [Shot {n2}] {t2}s")
    if cuts and max(t for _, t in cuts) > H3_MAX_DUR + 0.001:
        issues.append(f"H3 最后切点 {max(t for _, t in cuts)}s > {H3_MAX_DUR}s（H3 单段硬上限 15s；"
                      "Seedance 2.5 的 15~30s 段必须再拆一刀）")

    # H3 时长声明
    decl = None
    m = re.search(r'"?(?:duration_seconds|duration)"?\s*[:=]\s*(\d+(?:\.\d+)?)', text)
    if m:
        decl = float(m.group(1))
    else:
        m2 = re.search(r"时长\s*[:：]\s*(\d+(?:\.\d+)?)\s*(?:s|秒|seconds)", text)
        if m2:
            decl = float(m2.group(1))
    if decl is not None:
        if not (H3_MIN_DUR - 0.01 <= decl <= H3_MAX_DUR + 0.01):
            issues.append(f"H3 声明时长 {decl}s 越界（H3 硬区间 {H3_MIN_DUR}–{H3_MAX_DUR}s）")
    else:
        warns.append(f"H3 未标注目标时长——H3 硬区间 {H3_MIN_DUR}–{H3_MAX_DUR}s，"
                     "建议在稿头或载荷标注 duration_seconds 以便校验")

    # H4 语言标签
    bad_d = re.findall(r"<d>(?!\s*\[)", text)
    if bad_d:
        issues.append(f"H4 <d> 缺语言标签 {len(bad_d)} 处——应为 <d>[Chinese] 原文</d>（语言标签保留原语言，正文语言跟随内容主语言）")

    # H5 参考标签（used 从“定义段之外”统计：标签在其定义行里出现不算被引用）
    if is_ref:
        defined = {(k, int(n)) for k, n in H3_LABEL_RE.findall(sec.get("subject_definitions", ""))}
        rest = text.replace(sec.get("subject_definitions", ""), "")
        used = {(k, int(n)) for k, n in H3_LABEL_RE.findall(rest)}
        undef = sorted(used - defined)
        if undef:
            issues.append(f"H5 未定义标签 {[f'<{k} {n}>' for k, n in undef]}——须先在 subject_definitions 定义后再引用")
        sum_new = {(k, int(n)) for k, n in H3_LABEL_RE.findall(sec.get("summary", ""))} - defined
        if sum_new:
            issues.append(f"H5 summary 引入了新标签 {sorted(sum_new)}（summary 只用已定义标签）")
        if len(defined) > H3_PIC_MAX:
            warns.append(f"H5 subject_definitions 定义 {len(defined)} 项 > H3 Ref2VA 素材上限提示（图 {H3_PIC_MAX} 张）——"
                         "按 h3-adapter.md §四「9 张取材策略」裁剪或合并")
        # 只查 Subject（可复用内容单元）：Picture/Video/Audio 允许只作为来源引用出现在定义行内
        unused = sorted({(k, n) for (k, n) in defined - used if k == "Subject"})
        if unused:
            warns.append(f"H5 定义了却全文未引用 {[f'<{k} {n}>' for k, n in unused]}——白占 9 张额度，"
                         "或人物凭空消失（摆位必入画 · 法则 20）；删掉或补进对应镜头")

    # H6 保留度标记
    ra = sec.get("retention_analysis", "")
    if is_ref and ra:
        for mm in re.finditer(r"[:：]\s*([a-z_]{3,})\s*[-–—]", ra):
            if mm.group(1) not in (H3_MARK_VIS | H3_MARK_AUD):
                issues.append(f"H6 retention_analysis 非法保留度标记「{mm.group(1)}」——合法值：画面 "
                              "fully_preserved/partially_preserved/attribute_transfer/weak_reference；音频 "
                              "fully_copy/partially_copy/reference/weak_reference")
        if re.search(r"[（(]\s*S\d", ra):
            issues.append("H6 retention_analysis 不得写 (Sx)——说话人编号只出现在 detailed_description")

    # H7 说话人编号顺序（兼容半角/全角括号）
    dd = sec.get("detailed_description", "") or text
    seen = []
    for m in re.finditer(r"[（(]\s*(S\d+(?:\s*[,，]\s*S\d+)*)\s*[)）]", dd):
        for sid in re.split(r"[,，]", m.group(1)):
            sid = sid.strip()
            if sid and sid not in seen:
                seen.append(sid)
    if seen and seen != [f"S{i + 1}" for i in range(len(seen))]:
        issues.append(f"H7 (Sx) 未按首现顺序编号：实际首现序 {seen}（应从 (S1) 起递增；未发声角色不给 ID）")

    # H8 泄漏检查
    leak = [s for s in H3_SEVEN_LEAK if s in text]
    if leak:
        issues.append(f"H8 七段式栏名泄漏进 H3 正文 {leak}——H3 支线用原生字段（三字段/六段式），栏名不进正文")
    anchors = sorted(set(re.findall(r"@(?:CHR|SCN|PRP|AUD)-[\w\-]+", text)))
    if anchors:
        issues.append(f"H8 `@` 资产锚点泄漏 {anchors}——H3 用 <Subject N>/<Picture N>/<Video N>/<Audio N> 标签")
    wf = sorted({w for w in H3_WORKFLOW if w in text})
    if wf:
        warns.append(f"H8 工作流规则词混入 {wf}——规则由执行者应用，H3 正文只写画面（同 C12 口径）")
    jg = sorted({w for w in H3_JARGON if w in text})
    if jg:
        warns.append(f"H8 内部术语混入 {jg}——H3 无 Hit-Stop 语法，打击感转译为可见物理描述（接触凝住一拍 + 反作用力）")
    neg = sorted({m.group(0) for m in H3_NEG_PAT.finditer(text)})
    if neg:
        warns.append(f"H8 正文出现否定式 {neg}——模型对否定不敏感、对词根敏感（C19/法则 22）："
                     "删掉否定式，改为正向表述；负面清单不进 H3 正文")

    # H9 画外声
    if re.search(r"画外音|内心独白|旁白|voiceover|\bOS\b|\bVO\b", text):
        if not H3_VO_EVID.search(text):
            issues.append("H9 画外声缺闭口证据——官方要求紧跟「嘴唇完全闭合 / lips remain completely closed」"
                          "（等同 vo-os-weaving 声画分离红线）")
        if re.search(r"\{[^}]*\}", text):
            issues.append("H9 画外声禁用 {} 台词字符（{} 是锁口型对白通道，画外声走正文文字标注）")

    # H10 声音分层
    for f in ("overall_soundscape", "non_diegetic_music"):
        if "<d>" in sec.get(f, ""):
            issues.append(f"H10 {f} 段不得包含对白 <d>——对白只进 detailed_description（基础模式为 integrated_multimodal_description）")
    if re.search(r"台词", sec.get("overall_soundscape", "")):
        warns.append("H10 overall_soundscape 出现「台词」字样——对白不进声音层汇总")
    nd = sec.get("non_diegetic_music", "")
    for m in re.finditer(r"<d>(.*?)</d>", text, re.S):
        body_d = m.group(1).split("]", 1)[-1].strip()
        if body_d and body_d in nd:
            issues.append("H10 non_diegetic_music 复述了台词内容——BGM 段只写配器/速度/节奏/动态，不重复对白")
            break

    # H11 语气位继承（WARN · 对应法则 19 / 官方"发言人首次出现须给发声特征"）
    first_pos = {}
    for m in re.finditer(r"[（(]\s*(S\d+)\s*[)）]", dd):
        sid = m.group(1)
        if sid not in first_pos:
            first_pos[sid] = m.start()
    for sid, pos in first_pos.items():
        if not H3_TONE_HINT.search(dd[max(0, pos - 120):pos + 120]):
            warns.append(f"H11 {sid} 首次出现处缺语气/音色/语速描述——H3 要求发言人首次出场给出发声特征"
                         "（音高/音质/语速/口音），丢了语气等于退掉法则 19（对白三要素之三）")

    # H12 首镜锚定 / 单主体（对应 C18a / C20a / C20b）
    shot1 = ""
    ms = re.search(r"\[Shot\s*1\]([^\n]*(?:\n(?!\s*\[Shot)[^\n]*)*)", body)
    if ms:
        shot1 = ms.group(1)
    if shot1:
        # 首镜锚 = 具名主体（只认 <Subject N>；<Picture/Video/Audio N> 不是主体锚）
        if not re.search(r"<Subject\s+\d+>", shot1):
            warns.append("H12a 首镜无具名主体锚——[Shot 1] 未引用任何 <Subject N>（对应 C18a 首镜人物锚）："
                         "空镜开场须写明「空镜：…」且每段至多 1 镜；否则给首镜一个具名主体（人名或注明归属的部位）")
        par = H3_PARALLEL_PAT.search(shot1)
        if par:
            warns.append(f"H12b 首镜出现并列主体/同框句式「{par.group(0)}」——模型会读成画面里有两个主体"
                         "（C20a：同一主体的手与脸被渲染成两张脸）；锚定句只由**一个具名主体**统摄")
    dei = H3_DEIXIS_PAT.search(body)
    if dei:
        warns.append(f"H12c 悬空指示代词「{dei.group(0)}」——指代词没有先行词，模型自行补一个主体（C20b）："
                     "改写为「她的/其+部位」")

    stats = {"duration_s": decl or (max((t for _, t in cuts), default=0)),
             "shots": len(nums), "chars": len(text)}
    return issues, warns, stats

# ---- C16 对白语气（V6.9.3 新增 · model-adapters §5.2 对白三要素之三）----
# 判据收窄（防 C12/C14 式误报）：① 错位只对"有台词的镜行"判——无台词镜里的声音词属
#   环境音描述（归"声音："段管）；② 可作面部表情理解的词（冷笑/讥诮）须排除表情动词修饰。
TONE_STRONG = ("嘶哑", "沙哑", "低语", "气音", "嘶吼", "低吼", "颤声", "哭腔", "破音",
               "一字一顿", "压着嗓子", "哑着嗓子", "声嘶力竭", "阴阳怪气", "扯着嗓子")
TONE_SOFT = ("冷笑", "嗤笑", "讥诮", "嘲讽")
TONE_FACE_CTX = re.compile(r"挂[着上]|带[着上]|露出|浮现|勾起|扬起|抿|咧|噙|绷|抹")
# C16d 道具动作与语气冲突（V6.9.7 续 · 用户点出「宣判·一字一顿」时刻还在"把玩玉佩"出戏）：
# 闲适把玩类动作只配慢悠悠/玩味语气，强情绪语气时刻必须换攥紧/捏住/垂手握着等贴合动作。
IDLE_PROP_RE = re.compile(r"把玩|摩挲|拨弄|把弄|翻弄|转着")
TONE_SEVERE = ("宣判", "一字一顿", "嘶吼", "咆哮", "低吼", "质问", "冷硬",
               "森然", "咬牙", "发狠", "含恨", "恨意", "暴怒", "压着怒")
TONE_MISS_RATIO = 0.5     # 语气缺失率告警阈值（有台词镜行中未带语气位的占比）
TONE_VAGUE = ("开心", "难过", "生气", "愤怒", "悲伤", "伤心", "高兴", "邪魅", "伤感", "激动")
# 语气位判据：角色名后紧跟括号再接冒号 → `【角色（语气）：“…”】`
TONE_TAG_RE = re.compile(r"[^（()【】\[\]]{1,16}?\s*[（(]\s*([^）)]{1,40}?)\s*[）)]\s*[:：]")

# ---- C17 摆位必入画（V6.9.3 续 · model-adapters §5.0.1 人物账连续）----
ZW_PERSON_RE = re.compile(r"@([^\s@（）()【】，、；;：:]+)")
C17_EXIT_WORDS = ("离画", "退场", "离场", "出画", "未入镜", "不入镜")

# ---- C18 首镜锚定·景别一致·姿态延续·视线指派（V6.9.4 新增 · model-adapters §5.0.2）----
# 病灶实测（「重生70」EP01 段1 出片废镜）：①首镜"特写·顶拍·暴雨砸漏房顶+枯瘦手背"无人物锚
# → 模型渲染出"只有一张床"；②薇薇举玉说话 → 视线黏在玉佩上不看人；③清月镜3撑起半身、
# 镜4又躺回 → 状态回退穿帮。四判据全部按实测病灶收窄，防 C12/C14 式误报。
GAZE_ANCHOR_RE = re.compile(r"目光|视线|不落|不离")          # 视线指派的强标记（"看/盯"不算——指不出锚对象）
IDLE_PROP_RE = re.compile(r"把玩|摩挲|摆弄|把弄")             # 说话同时漫不经心摆弄道具 → 视线黏道具重灾区
LIFT_TOWARD_RE = re.compile(r"[举捧]向")                      # 举向/捧向（光源/高处）→ 道具抢视线重灾区
CU_SHOT_RE = re.compile(r"特写")                              # 特写/紧特写/大特写
SPACE_EVENT_RE = re.compile(r"房顶|屋顶|屋子|屋里|屋内|房间|门口|窗外|院子|全景")
PROPUP_RE = re.compile(r"撑起|坐起|起身|站起|弹起|坐起身")
LIE_RE = re.compile(r"躺|卧|蜷|瘫")
LIEBACK_EXEMPT = ("躺回", "倒回", "跌回", "又躺", "瘫回", "重新躺", "重新蜷", "蜷回")
# C18e 反光道具光效（V6.9.4 拉片反馈）：玉佩被渲染成自发光半透明"魔法道具"——
# V6.9.6 起按 §5.0.4 栏目纪律：镜行内写**正向材质描写**（哑光/实心/石质原色）；
# 禁止项里的「不发光不透光」否定式声明被判失效（被禁词根反被当画面词），由 C19e-b 检出。
# V6.9.7 续（C20d）：材质描写之外的任何光效从句（光斑/受光/照射）也一并归零——实测
# 「指甲盖大暖黄光斑」仍被渲染成玉佩点火。
GLOW_PROP_RE = re.compile(r"玉佩|银镯|宝石|镜子|铜镜|珍珠|金饰|银饰|钻石|水晶")
# C19 禁令失效三改法（V6.9.5 · model-adapters §5.0.4）：视频模型对否定不敏感、对词根敏感——
# 「禁空镜」里的空镜、「不发光」里的发光、「面无笑意」里的笑，被禁概念的词根本身留在提示词里
# 等于把画面词喂给了模型（实测三条禁令全部被无视）。高关联视觉概念必须在镜行内做正向描写。
BARE_NEG_RE = re.compile(r"不发光|不透光|不悬浮|面无笑意|面无笑容|不会发光|不会透光")
LIGHTPATH_RE = re.compile(r"(举向|凑向|对着|冲着|迎向)[^。；]*?(灯|光|火)|冲光")
# C19d 具象光源映射污染（V6.9.5 续）：「玉面映出油灯火苗」——模型不理解"反射"，
# 会把「映出+光源名词」读成"光源出现在道具上"（玉面画小火苗/整体泛光）。改写为光斑语言。
FLAME_MAP_RE = re.compile(r"(映出|倒映|映着|反射出)[^。；]*?(火苗|火焰|灯火|烛火)")
# C20d 道具光效描写归零（V6.9.7 续 · 用户拉片）：V6.9.5 引入的"光斑语言"（受油灯照射处
# 只有指甲盖大一片暖黄光斑）实测仍被渲染成玉佩点火（用户：「玉佩上面像个打火机，点了一簇火」）
# ——道具只要与光/火产生描写关联（光斑/受光/照射/照在/亮起）或动作上贴近光源（举到油灯旁），
# 模型就可能给它点火。唯一正解：反光道具**零光效描写**，只写材质本色（青玉原色/哑光金属本色）。
PROP_LIGHT_RE = re.compile(r"光斑|受光|受[^。；]{0,8}照射|照射|照在|亮起")
LAMP_NEAR_RE = re.compile(r"(举|凑|贴|送|递)[^。；]{0,6}(到|向|至)[^。；]{0,8}(油灯|灯|烛|火)")
# C19e 禁止项栏目纪律（V6.9.6 · model-adapters §5.0.4）：
# 【强制禁止项】被模型当"规避清单"读，只装负面项。正向执行指令（首帧/材质/表情/姿态/视线）写进去
# 两头不生效（既不被当禁令，也不被当执行指令）——实测「全片首帧即镜1的人物近景画面」
# 「道具保持日常石质与金属质感」等同废纸；否定式禁令（不发光/面无笑意）同理失效（C19e-b）。
C19E_POS_RE = re.compile(
    r"(即[^。；]{0,24}?(画面|镜头|首帧)|保持[^。；]{0,14}?(质感|状态|位置|本色)|必须|应写出|应写明|写明|复述|画面主体|以.{1,10}为主|呈[^。；]{0,10}?(色|质|感))")
C19E_NEG_WORDS = ("禁止", "禁", "无", "不", "防", "杜绝", "避免", "杜绝")

# C20 首镜单主体锚定 + 抽象形容（V6.9.7 · model-adapters §5.0.2/§5.0.4）：
# 病灶实测（「重生70」EP01 段1 镜1 出片**两张脸**）：镜行写「首帧即这只手与她的脸同框」——
# 「手」与「脸」被写成**并列名词**，叠加「同框」这个多主体触发词 → 模型读成两个主体，
# 渲染出两个头/两张脸（用户拉片："总共生成了两张脸，最大的祸首就是这儿"）。
# 正解：首镜锚定句只由**一个具名主体**统摄，身体部位一律以「她的/其+部位」从属出现。
MULTI_SUBJ_RE = re.compile(r"同框|同在画面|一同入画|同时入画|与[^。；，]{1,8}同(处|在|入)")
DANGLING_DEIXIS_RE = re.compile(r"[这那](只|双|张|个)(手|脚|脸|眼|肩|手指|手背|身体|背影)")
DEIXIS_OWNED_RE = re.compile(r"[她他其][^。；，]{0,2}$")
ABSTRACT_SHAPE_RE = re.compile(r"成线|成串|成股|如注|连成一线|轻蜷|微蜷")


def parse_time_ranges(text):
    """返回 [(start_s, end_s, line_no)]，兼容 MM:SS(.ff) 与 Xs-Ys。"""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        for m in TIME_RE.finditer(line):
            if m.group(1) is not None:
                fr = int(m.group(3) or 0)
                to = int(m.group(6) or 0)
                s = int(m.group(1)) * 60 + int(m.group(2)) + fr / 100.0
                e = int(m.group(4)) * 60 + int(m.group(5)) + to / 100.0
            else:
                s, e = float(m.group(7)), float(m.group(8))
            out.append((round(s, 2), round(e, 2), i))
    return out


def validate(text, model="2.5", mode="new"):
    issues, warns = [], []
    tr = parse_time_ranges(text)
    dur = round(max((e for s, e, _ in tr), default=0), 2)

    # C1/C2/C3 时间轴
    if tr:
        if dur > LIMITS[model] + 0.01:
            issues.append(f"C1 段时长 {dur}s 超 {model} 上限 {LIMITS[model]}s")
        n = len(tr)
        cap = -(-int(dur + 0.5) // 3) or 1
        if n > cap:
            issues.append(f"C2 镜头数 {n} > 段长÷3s 上限 {cap}")
        for s, e, ln in tr:
            if e <= s:
                issues.append(f"C3 第{ln}行 时间码倒挂 {s}->{e}")
            elif e - s < 3:
                warns.append(f"C2 第{ln}行 单镜 {round(e - s, 2)}s <3s（碎切风险）")
            elif e - s > 6:
                warns.append(f"C10 第{ln}行 单镜 {round(e - s, 2)}s >6s（talking head 风险：单镜预算 3~5s，长台词按 dialogue-doctor 拆 2~3 镜正反打/反应镜头）")
        for (s1, e1, l1), (s2, e2, l2) in zip(tr, tr[1:]):
            if abs(e1 - s2) > 0.05:
                kind = "重叠" if s2 < e1 else "断档"
                warns.append(f"C3 第{l1}->{l2}行 {kind}({e1} vs {s2})")
        if mode == "new" and tr and tr[0][0] > 0.05:
            warns.append("C3 全新生成建议从 0 起手")
    else:
        warns.append("C1-C3 未识别到时间轴（如为纯文生视频短片可忽略）")

    # C4 字符预算
    if len(text) > MAX_CHARS:
        issues.append(f"C4 共 {len(text)} 字符 > 预算 {MAX_CHARS}（按 seedance-render-engine 压缩顺序裁删）")

    # C5 版本语法
    if model == "2.0":
        if "[SFX" in text.upper():
            issues.append("C5 Seedance 2.0 无官方声音字符标记（音效/台词以文字写入镜行、默认由模型生成）")
        for w in ("顿挫", "微停顿", "咬住"):
            if w in text:
                issues.append(f"C5 2.0 禁顿挫词「{w}」（会渲染成真停顿）")
    elif "[SFX" not in text.upper():
        warns.append("C5 2.5 建议用 [SFX:] 原生音效标记")

    # C6 画幅回填
    if not re.search(r"aspect_ratio\s*=", text) and not re.search(r"【画幅风格】[^\n]*(16:9|9:16|21:9|1:1)", text):
        issues.append("C6 缺画幅回填（体内 aspect_ratio= 或【画幅风格】行含 16:9/9:16/21:9）")

    # C7 七段式核心栏
    missing = [seg for seg in SEVEN_SEGMENTS if seg not in text]
    if missing:
        issues.append(f"C7 七段式缺栏 {missing}（V6.8 主格式唯一命名，段序见 model-adapters §5）")

    # C8 2.0 首尾帧禁用（V6.8 重头门）
    fl = re.findall(r"首帧\s*[:：]|尾帧\s*[:：]|参考图绑定|Start\s*Frame|End\s*Frame", text, re.I)
    if fl:
        if model == "2.0":
            issues.append(f"C8 Seedance 2.0 全面禁用首尾帧：出现 {sorted(set(fl))}（2.0 参考图仅锁定形象）")
        else:
            issues.append(f"C8 首尾帧仅限 2.5「参考模式②」：出现 {sorted(set(fl))}——若走默认全能参考模式则删去；确用模式②需标注 mode=first_last_frame")

    # C9 平台高危词
    hits = [w for w in GORE_WORDS if w in text]
    if hits:
        issues.append(f"C9 正文出现平台高危词 {hits}——按 platform-safety-compliance-guide 全类目替代表在成句时直接改写（2.0 提及即召唤，禁靠否定式压制）")

    # C11 接续状态尾行（V6.9：存在性 FAIL + 纯套话 WARN）
    cont_m = re.search(r"【接续状态】[:：]?\s*([^\n]*)", text)
    if tr and not re.search(r"【接续状态】|接续下一段|承接上镜|承接上段", text):
        issues.append("C11 时间轴分镜末镜后缺【接续状态】尾行（每段必带：写具体末帧画面，见 segment-splicing.md §二）")
    elif cont_m and re.fullmatch(r"(角色动作与空间位置)?严格继承[。.]?", cont_m.group(1).strip()):
        warns.append("C11 接续状态是套话「角色动作与空间位置严格继承」——模型每段零记忆，套话继承不了任何画面；"
                     "改写具体末帧（谁+在哪+姿态+关键道具/互动状态，下段自该画面起手，见 segment-splicing.md §二）")

    # C12 否定式硬删除 / 工作流规则词混入
    # 判据收窄两点（否则正常台词/表演描写会被误报，WARN 一多就没人看了）：
    #   ① 只在"指令性正文"上判——台词字段（角色对白）与【强制禁止项】/【音效】（负面词合法通道）内的否定句跳过；
    #   ② 否定词必须搭配"存在性对象"（人物/家具/背景…）才算删除指令；
    #      「睫毛没有颤动」「跟他没有半点关系」是描写与对白，不是"把东西删掉"。
    _neg_obj = (r"(人物|角色|路人|群演|演员|家具|道具|背景|场景|物体|动物|车辆|"
                r"观众|杂物|陈设|装饰|文字|字幕|水印|logo|LOGO)")
    _neg_pat = re.compile(r"(没有|不要出现|禁止出现)([\u4e00-\u9fa5]{0,4})" + _neg_obj)
    for ln in text.splitlines():
        probe = re.sub(r"台词：.*$", "", ln)
        probe = re.sub(r"【强制禁止项】.*$", "", probe)
        probe = re.sub(r"【音效】.*$", "", probe)
        for m in _neg_pat.finditer(probe):
            if not re.search(r"负面|排除|禁止角色变形|无水印|无字幕", probe[max(0, m.start() - 40):m.end() + 40]):
                warns.append(f"C12 正文疑似否定式硬删除「{m.group(0)}」——硬删除应整句移除，负面仅走【强制禁止项】负面词")
    workflow = re.findall(r"末态继承|拼接节点|换机位|同机位硬接|可变数据|每段重写|每段更新", text)
    if workflow:
        warns.append(f"C12 工作流规则名词混入投喂正文 {sorted(set(workflow))}——接续状态只写末帧画面长什么样，规则由执行者应用")

    # C14 画外声（OS/VO）——规程见 vo-os-weaving.md
    os_shots = vo_shots = 0
    vo_os_chars = 0
    for ln_i, line in enumerate(text.splitlines(), 1):
        # 只统计【时间轴分镜】的镜行：OS/VO 是"在某镜里发声"的行为，
        # 【强制禁止项】/【音效】/【接续状态】里出现"画外音/旁白"等字样不是使用，计入会误报配额。
        if not TIME_RE.search(line):
            continue
        is_os, is_vo = bool(OS_PAT.search(line)), bool(VO_PAT.search(line))
        if not (is_os or is_vo):
            continue
        os_shots += is_os
        vo_shots += is_vo
        snd_idx = line.find("声音：")
        dlg_idx = line.find("台词：")
        pic_seg = line[:snd_idx] if snd_idx >= 0 else line[:dlg_idx] if dlg_idx >= 0 else line
        snd_seg = line[snd_idx:] if snd_idx >= 0 else ""
        dlg_seg = line[dlg_idx:] if dlg_idx >= 0 else ""
        # ① 声画分离红线：OS 镜行画面段含开口词
        if is_os and MOUTH_PAT.search(pic_seg):
            issues.append(f"C14 第{ln_i}行 OS 声画分离红线：画面段出现开口词——独白发声时角色必须闭口，"
                          "改闭口神态微特写承载（嘴唇紧闭/瞳孔/手指，见 vo-os-weaving.md 纪律 2）")
        # ② OS/VO 写进台词字段（台词字段只装画内开口对白）
        if dlg_seg and (is_os and OS_PAT.search(dlg_seg) or is_vo and VO_PAT.search(dlg_seg)):
            issues.append(f"C14 第{ln_i}行 OS/VO 写进了台词字段——画外声一律走「声音：」段并标注画外身份，台词字段写\"台词：无。\"")
        # ③ OS/VO 使用 {} 台词字符（锁口型必穿帮）
        if snd_seg and re.search(r"\{[^}]*\}", snd_seg):
            issues.append(f"C14 第{ln_i}行 OS/VO 使用 {{}} 台词字符——{{}} 是锁口型对白通道，画外声禁用；走声音段文字标注（见 vo-os-weaving.md §二）")
        # 配额统计（中文字符）
        seg = snd_seg if snd_seg else pic_seg
        vo_os_chars += len(re.findall(r"[\u4e00-\u9fa5]", seg))
    if os_shots > OS_MAX_SHOTS:
        warns.append(f"C14 段内 OS 内心独白 {os_shots} 镜 > 上限 {OS_MAX_SHOTS}——独白是配额制工具，超量即广播剧化（vo-os-weaving.md 纪律 1）")
    if vo_shots > VO_MAX_SHOTS:
        warns.append(f"C14 段内 VO 旁白 {vo_shots} 镜 > 上限 {VO_MAX_SHOTS}——旁白一点定调即可，多则听书化")
    budget = VO_OS_QUOTA * max(1, round(dur / 15)) if dur else VO_OS_QUOTA
    if vo_os_chars > budget + VO_OS_QUOTA_SLACK:
        warns.append(f"C14 段内 VO+OS 总字数≈{vo_os_chars} 字 > 折算上限 {budget} 字（60~80 字/分钟钢性卡口，容差线 +{VO_OS_QUOTA_SLACK}）——删到只剩点题句")

    # C13 镜长雷同（节奏呼吸 · quality-gate-review P1 反例）
    if len(tr) >= 4:
        from collections import Counter
        durs = [round(e - s, 2) for s, e, _ in tr]
        cnt = Counter(durs)
        top_dur, top_n = cnt.most_common(1)[0]
        ratio = top_n / len(durs)
        if ratio >= 0.7:
            warns.append(f"C13 镜长雷同：{top_n}/{len(durs)} 镜均为 {top_dur}s（占比 {ratio:.0%}）——节奏缺乏快慢呼吸；镜长应按台词字数÷语速(3.5~5字/s)+情绪节拍倒推，禁机械等分（quality-gate-review P1「时长全篇雷同」反例）")

    # C15 拉伸凑时（V6.9 修订 · 法则 17：总时长同样由内容倒推，禁拉伸凑满剧本标注时长）
    lines_all = text.splitlines()
    has_dialogue = bool(re.search(r"台词：\s*(?!无)", text))
    if tr:
        for s, e, ln in tr:
            line = lines_all[ln - 1] if 0 < ln <= len(lines_all) else ""
            d = round(e - s, 2)
            if d > NO_DIALOG_SHOT_MAX and re.search(r"台词：\s*无", line) \
                    and not OS_PAT.search(line) and not VO_PAT.search(line):
                warns.append(f"C15 第{ln}行 无台词镜 {d}s >{NO_DIALOG_SHOT_MAX}s——镜长必须由内容倒推，"
                             "禁止把氛围/过渡镜拉长凑满剧本标注的【本集时长】（一句≤40字动作行合理节拍≤6s）；"
                             "总时长允许比剧本标注短至 -25%，宁短勿拉")
        if not has_dialogue and dur > PURE_AMBIENT_SEG_MAX:
            warns.append(f"C15 全段 {dur}s 无任何台词（纯氛围段）>{PURE_AMBIENT_SEG_MAX}s——若非 D 锁③空镜过渡（1~2s）"
                         "或蓄意留白的爆点镜，即为拉伸凑时；压缩节拍或与钩子台词合并同段")

    # C16 对白语气（V6.9.3 · model-adapters §5.2 官方对白三要素之三 HOW THEY SOUND）
    # 只扫【时间轴分镜】的镜行；只统计"有台词"的镜行（"台词：无。"不参与语气判定）。
    _dlg = []
    for ln_i, line in enumerate(text.splitlines(), 1):
        if not TIME_RE.search(line):
            continue
        di = line.find("台词：")
        if di < 0:
            continue
        if line[di + 3:].strip().startswith("无"):
            continue
        _dlg.append((ln_i, line, di))
    if _dlg:
        miss = []
        for ln_i, line, di in _dlg:
            si = line.find("声音：")
            pic = line[:si] if 0 <= si < di else line[:di]
            hit = [w for w in TONE_STRONG if w in pic]
            for w in TONE_SOFT:
                k = pic.find(w)
                if k >= 0 and not TONE_FACE_CTX.search(pic[max(0, k - 8):k]):
                    hit.append(w)
            if hit:
                warns.append(f"C16a 第{ln_i}行 语气错位：画面段出现声音词 {sorted(set(hit))}——"
                             "声音词会被模型当视觉信息渲染（画出一张冷笑的脸），应移入台词语气位 "
                             "`台词：【角色（语气）：“…”】`（model-adapters §5.2）")
            tm = TONE_TAG_RE.search(line[di:])
            if tm is None:
                miss.append(ln_i)
            else:
                v = [w for w in TONE_VAGUE if w in tm.group(1)]
                if v:
                    warns.append(f"C16c 第{ln_i}行 语气位含空泛结果词 {v}——按四维改写"
                                 "（情绪色/力度/音质/节奏），如「压着怒·低语」而非「愤怒」")
                # C16d 道具动作与语气冲突（V6.9.7 续）：闲适把玩 × 宣判/强情绪语气
                am = IDLE_PROP_RE.search(pic)
                tw = [w for w in TONE_SEVERE if w in tm.group(1)]
                if am and tw:
                    warns.append(f"C16d 第{ln_i}行 道具动作与语气冲突：「{am.group(0)}」×语气「{tw[0]}」——"
                                 "闲适把玩配不上宣判/强情绪时刻（实测出戏：正俯视宣判台词还在把玩玉佩）。"
                                 "换成贴合语气的动作：攥紧/捏住/垂手握着（model-adapters §5.0.3）")
        if len(miss) / len(_dlg) > TONE_MISS_RATIO:
            warns.append(f"C16b 语气缺失：{len(miss)}/{len(_dlg)} 条台词未带语气位"
                         f"（缺失率 {len(miss)/len(_dlg):.0%} > 阈值 {TONE_MISS_RATIO:.0%}）——"
                         "台词应写 `台词：【角色（语气）：“…”】`；2.0/2.5 同规格必写，"
                         "缺语气会让声音与表情一并扁平（官方点名 tone_qualifiers）")

    # C17 摆位必入画（V6.9.3 续 · model-adapters §5.0.1 人物账连续）
    # 单场景连续段里人物凭空消失/重现 = 跨段衔接最典型穿帮。单人站位段不触发（无跨段风险）。
    # 站位块 = 【站位声明】行 + 其后连续非【段行（兼容"独占一行、@人名在下一行"的排版）。
    lines_all = text.splitlines()
    zw_i = next((i for i, l in enumerate(lines_all) if l.strip().startswith("【站位声明】")), None)
    zw_people = []
    if zw_i is not None:
        zw_block = lines_all[zw_i]
        j = zw_i + 1
        while j < len(lines_all) and not lines_all[j].strip().startswith("【"):
            zw_block += lines_all[j]
            j += 1
        zw_people = ZW_PERSON_RE.findall(zw_block)
        if len(zw_people) >= 2:
            shot_blob = "".join(l for l in lines_all if TIME_RE.search(l))
            ctx_blob = zw_block + "".join(
                l for l in lines_all if "@CHR-" in l or l.strip().startswith("【接续状态】"))
            gone = []
            for p in zw_people:
                if p in shot_blob:
                    continue
                exempt = False
                for m in re.finditer(re.escape(p), ctx_blob):
                    tail = ctx_blob[m.end():m.end() + 24]
                    if any(w in tail for w in C17_EXIT_WORDS):
                        exempt = True
                        break
                if not exempt:
                    gone.append(p)
            if gone:
                warns.append(
                    "C17 摆位必入画：站位声明摆了位、但全段镜行一次都未带到的人物：" + "、".join(gone)
                    + "——人物凭空消失，跨段衔接必穿帮（model-adapters §5.0.1）。"
                      "给该人物至少一个镜头（正拍/焦外身影/全景群像/反应镜头均算），"
                      "或在站位行写明「离画/退场·去向」；重新入画的段要写明入画方式")

    # C18 首镜锚定·景别一致·姿态延续·视线指派（V6.9.4 · model-adapters §5.0.2）
    # 病根全部来自「重生70」EP01 段1 实拍废镜，四判据见模块 docstring。
    shot_lines = [(ln_i, l) for ln_i, l in enumerate(lines_all, 1) if TIME_RE.search(l)]
    # C18a 段首镜人物锚：首镜无站位人名且未声明「空镜」→ 模型渲染出空场景
    if shot_lines and zw_people:
        first_line = shot_lines[0][1]
        if "空镜" not in first_line and not any(p in first_line for p in zw_people):
            warns.append(f"C18a 第{shot_lines[0][0]}行 段首镜无人物锚：首镜既未带站位人物名、也未声明「空镜」——"
                         "首镜无锚，模型会渲染出空场景（实测出『只有一张床』）。"
                         "首镜写明主体归属（谁的手/谁的身体局部）或改为带站位人物的中近景（model-adapters §5.0.2）")
    # C18b 姿态回退：撑起/坐起/起身之后再出现躺/卧/蜷且无跌回交代 → 状态回退
    propup_seen = False
    for ln_i, l in shot_lines:
        pic_l = l.split("台词：")[0]
        if propup_seen and LIE_RE.search(pic_l) \
                and not any(w in pic_l for w in LIEBACK_EXEMPT):
            warns.append(f"C18b 第{ln_i}行 姿态回退：前镜已撑起/坐起/起身，本镜又躺/卧/蜷且无「跌回/躺回」交代——"
                         "状态回退必穿帮；后续镜写「保持撑坐/已坐起」，确需倒下要写明动作过程（model-adapters §5.0.2）")
        if PROPUP_RE.search(pic_l):
            propup_seen = True
    # C18c 视线黏道具：说话镜把玩/举向道具却未指派视线 → 模型默认看道具不看人
    for ln_i, line, di in _dlg:
        si = line.find("声音：")
        pic = line[:si] if 0 <= si < di else line[:di]
        if (IDLE_PROP_RE.search(pic) or LIFT_TOWARD_RE.search(pic)) \
                and not GAZE_ANCHOR_RE.search(pic):
            warns.append(f"C18c 第{ln_i}行 视线指派缺失：说话同时把玩/举起道具，却未写目光/视线归属——"
                         "模型默认视线黏在道具上，说话不看人（实测：举玉宣判整段盯着玉）。"
                         "补「目光落在XX脸上/视线不落在道具上」（model-adapters §5.0.2）")
    # C18d 景别冲突：特写承载空间级事件 → 模型只好丢人物保空间
    for ln_i, l in shot_lines:
        si = l.find("声音：")
        pic = l[:si] if si >= 0 else l
        if CU_SHOT_RE.search(pic) and SPACE_EVENT_RE.search(pic):
            warns.append(f"C18d 第{ln_i}行 景别冲突：特写镜头承载空间级事件（房顶/屋子/门口/全景…）——"
                         "特写装不下全屋信息，模型只能丢人物保空间（实测出空床）。"
                         "空间事件改中景以上承载，或近景只保留单一局部主体（model-adapters §5.0.2）")
    # C18e 反光道具光效（V6.9.4 拉片反馈；V6.9.5 按 §5.0.4 放行正向材质描写）：
    # 镜行出现玉佩/银镯/镜面等反光道具，而既无镜行正向材质描写（哑光/实心/石质原色）、
    # 【强制禁止项】也未声明光效负面 → 模型渲染成自发光半透明魔法道具（实测）
    if GLOW_PROP_RE.search("".join(l for _, l in shot_lines)):
        ban_m = re.search(r"【强制禁止项】[\s\S]*", text)
        neg_declared = bool(ban_m and "发光" in ban_m.group(0))
        pos_declared = bool(re.search(r"哑光|实心|石质|原色|光斑", "".join(l for _, l in shot_lines)))
        if not (neg_declared or pos_declared):
            warns.append("C18e 反光道具光效未声明：镜行出现玉佩/银镯/镜面类反光道具，但既无正向材质描写"
                         "（实心石质/哑光质感，§5.0.4 首选）也未在【强制禁止项】加光效负面声明——"
                         "实测会被渲染成自发光半透明魔法道具；镜行写明材质正描写 + 主光源在关键镜行复述（model-adapters §5.0.3/§5.0.4）")

    # C19 禁令失效三改法（V6.9.5 · model-adapters §5.0.4）：被禁概念词根污染 / 光路触发器 / 首镜主体优先
    for ln_i, l in shot_lines:
        si = l.find("声音：")
        pic = l[:si] if si >= 0 else l
        neg_hits = BARE_NEG_RE.findall(pic)
        if neg_hits:
            warns.append(f"C19a 第{ln_i}行 裸禁令词污染：镜行内出现「{'、'.join(neg_hits)}」——"
                         "视频模型对否定不敏感、对词根敏感，被禁概念的词根本身会被当画面词渲染"
                         "（实测三条否定式禁令全部被无视）。删掉否定式写法，在镜行内改写为正向"
                         "材质/肌肉/光路描述：道具→「深青色实心哑光石质，玉面呈青玉原色」"
                         "（零光效描写，禁光斑/受光/照射类从句，见 C20d），"
                         "表情→「双唇抿紧、嘴角向下压、下颌绷紧」，"
                         "首帧→「画面主体：<人名>…」单主体开头（禁「X 与 Y 同框」并列主体写法，见 C20a）")
        if LIGHTPATH_RE.search(pic) and GLOW_PROP_RE.search(pic):
            warns.append(f"C19b 第{ln_i}行 光路触发器：反光道具被「举向/对着/冲向灯或光」——"
                         "道具正对光源会诱发模型渲染透光自发光（实测玉佩被画成灯泡）。"
                         "道具不与光源共现：动作上远离灯火，只写材质本色"
                         "（青玉原色/哑光金属本色），不做任何光效描写（见 C20d）")
        if GLOW_PROP_RE.search(pic) and FLAME_MAP_RE.search(pic):
            warns.append(f"C19d 第{ln_i}行 具象光源映射污染：反光道具镜行写「映出/倒映火苗」——"
                         "模型不理解「反射」，会把「映出+光源名词」读成光源出现在道具上"
                         "（玉面画出小火苗/整体泛光）。反光道具零光效描写：删掉全部"
                         "光斑/受光/照射类从句，只写材质本色（如「玉面呈青玉原色」），"
                         "且动作上不靠近光源（model-adapters §5.0.4 / C20d）")
    # C19c 首镜主体优先：每段镜1第一个分句须含人物名/身体局部/「画面主体」，环境前置词诱导空场景开场
    first_shot = next((l for _, l in shot_lines if "[镜头1]" in l), None)
    if first_shot:
        first_clause = re.split(r"[，。；]", first_shot.split("。", 1)[-1] or first_shot, maxsplit=1)[0]
        body_local = re.search(r"的手|的脚|的脸|的手背|的肩膀|的侧脸|的眼|画面主体", first_clause)
        people_in_clause = any(p in first_clause for p in (zw_people or [])) or bool(re.search(r"她|他|其", first_clause[:4]))
        if not (people_in_clause or body_local):
            warns.append("C19c 首镜主体优先：镜1第一个分句以环境开头、人物名/身体局部出现在其后——"
                         "环境前置词会诱导模型渲染空场景开场（实测两轮出空房间大全景）。"
                         "改为「画面主体：<人名>…」或以人名/身体局部开头（model-adapters §5.0.4）")

    # C19e 禁止项栏目纪律（V6.9.6 · model-adapters §5.0.4）：
    # ① 正向执行指令混入【强制禁止项】→ 两头不生效（实测等同废纸）；
    # ② 禁止项里写否定式禁令（不发光/面无笑意）→ 被禁词根反被当画面词渲染，同样失效。
    ban_m2 = re.search(r"【强制禁止项】([\s\S]*)", text)
    if ban_m2:
        ban_blob = ban_m2.group(1)
        for part in re.split(r"[；;]", ban_blob):
            p = part.strip()
            if not p or any(n in p for n in C19E_NEG_WORDS):
                continue
            hit = C19E_POS_RE.search(p)
            if hit:
                warns.append(f"C19e 禁止项栏目错位：正向执行指令「{hit.group(0)}」写进了【强制禁止项】——"
                             "该栏被模型当规避清单读，正向要求放进去既不当禁令也不当指令（实测等同废纸）。"
                             "正向指令回落镜行/【画幅风格】/【站位声明】，禁止项只写负面清单"
                             "（变形/穿模/现代元素/字幕水印/音频约束；model-adapters §5.0.4 栏目纪律）")
                break
        neg_hits2 = sorted(set(BARE_NEG_RE.findall(ban_blob)))
        if neg_hits2:
            warns.append(f"C19e 禁止项裸禁令词：「{'、'.join(neg_hits2)}」——"
                         "否定式禁令在禁止项里同样失效（模型对否定不敏感、对词根敏感，"
                         "被禁概念的词根会被当画面词渲染，实测玉佩仍全片自发光）。"
                         "删掉该声明，改在镜行写正向描写：道具→「哑光金属本色/实心石质+受光处小片光斑」，"
                         "表情→「双唇抿紧、嘴角向下压」（model-adapters §5.0.4）")

    # C20 首镜单主体锚定 + 抽象形容（V6.9.7 · model-adapters §5.0.2/§5.0.4）：
    # 病灶实测：「重生70」EP01 段1 镜1 出片两张脸——镜行「首帧即这只手与她的脸同框」。
    for ln_i, l in shot_lines:
        si = l.find("声音：")
        pic = l[:si] if si >= 0 else l
        ms = MULTI_SUBJ_RE.search(pic)
        if ms:
            warns.append(f"C20a 第{ln_i}行 并列主体/同框句式：「{ms.group(0)}」——"
                         "模型把「X 与 Y 同框」读成画面里有两个主体（实测同一主体的手与脸被渲染成"
                         "两个头/两张脸）。首镜锚定句只由**一个具名主体**统摄（「画面主体：林清月…」），"
                         "身体部位一律以「她的/其+部位」从属出现；确有两个人物时由【站位声明】"
                         "具名双主体承载，镜行内不写「同框」（model-adapters §5.0.2）")
        dm = DANGLING_DEIXIS_RE.search(pic)
        if dm and not DEIXIS_OWNED_RE.search(pic[:dm.start()]):
            warns.append(f"C20b 第{ln_i}行 悬空指示代词：「{dm.group(0)}」无归属定语——"
                         "指代词没有先行词，模型会自行补全一个主体（实拍多补出一个头/一张脸）。"
                         "改写为「她的一只手」这类带归属写法（model-adapters §5.0.2）")
        shape_hits = sorted(set(ABSTRACT_SHAPE_RE.findall(pic)))
        if shape_hits:
            warns.append(f"C20c 第{ln_i}行 抽象形态形容：「{'、'.join(shape_hits)}」——"
                         "模型只渲染可命名的具象形态，抽象形态/程度副词不被理解"
                         "（实测「漏雨成线」「手指轻蜷」）。改写为可见形态："
                         "「雨滴砸在手背上溅开」（model-adapters §5.0.4 镜行少形容词）")
        if GLOW_PROP_RE.search(pic):
            lm = PROP_LIGHT_RE.search(pic)
            if lm:
                warns.append(f"C20d 第{ln_i}行 道具光效描写：「{lm.group(0)}」与反光道具共现——"
                             "道具与光/火产生描写关联就会被模型渲染成发光/点火"
                             "（实测「指甲盖大暖黄光斑」出片玉佩像打火机点了一簇火）。"
                             "反光道具零光效描写：删掉光斑/受光/照射类从句，"
                             "只写材质本色（玉面呈青玉原色/哑光金属本色）（model-adapters §5.0.3）")
            nm = LAMP_NEAR_RE.search(pic)
            if nm:
                warns.append(f"C20d 第{ln_i}行 道具贴近光源动作：「{nm.group(0)}」——"
                             "道具靠近灯火的动作本身就是点火触发器（实测「举到油灯旁」"
                             "出片玉佩上冒火苗）。动作改开：道具只把玩/随身佩戴，不与灯火同框共现")

    return issues, warns, {"duration_s": dur, "shots": len(tr), "chars": len(text)}


def _self_test():
    ok = 1
    # 1) 合规 2.5 样例
    t_ok = ("【画幅风格】16:9 横屏, 电影级质感, PBR, 景深胶片颗粒 (aspect_ratio=16:9)\n"
            "【场景资产】@SCN-厢房（外观以场景参考图锁定）\n"
            "【核心人物】@CHR-女主（外观以人物参考图锁定）\n"
            "【站位声明】：@女主（画面中 · 坐于窗下 · 侧身45°朝左 · 双手交叠膝上）；轴线锁定：单人无轴线；位移：全员原位，无位移。\n"
            "【时间轴分镜】\n"
            "00:00-00:04 [镜头1] 中近景 · 平视 · 缓推。她从袖中抽出信件。声音：[SFX: 纸张摩挲]。台词：无。\n"
            "00:04-00:08 [镜头2] 特写 · 侧角 · 固定。指尖微颤。声音：[SFX: 呼吸]。台词：无。\n"
            "【接续状态】：角色动作与空间位置严格继承\n"
            "【音效】生成音效描述（2.5 用 [SFX:]/<>，2.0 文字描述默认由模型生成）\n"
            "【强制禁止项】画面：角色变形、穿模；文字：无字幕水印\n")
    iss, warns, _ = validate(t_ok, "2.5", "new")
    if iss:
        print("FAIL self-test: 合规 2.5 样例不应报错", iss); ok = 0
    # 2) 2.0 含 [SFX:]
    t_sfx = t_ok.replace("(aspect_ratio=16:9)", "model=seedance-2.0 (aspect_ratio=16:9)")
    iss, _, _ = validate(t_sfx, "2.0", "new")
    if not any("C5" in i for i in iss):
        print("FAIL self-test: 2.0 应拦截 [SFX:]"); ok = 0
    # 3) 2.0 含首尾帧
    t_fl = t_ok + "【参考图绑定】：首帧: a.png, 尾帧: b.png\n"
    iss_t20, _, _ = validate(t_fl, "2.0", "new")
    if not any("C8" in i for i in iss_t20):
        print("FAIL self-test: 2.0 应拦截首尾帧"); ok = 0
    # 3b) 2.5 含首尾帧（非模式②声明）也应拦
    iss_t25, _, _ = validate(t_fl, "2.5", "new")
    if not any("C8" in i for i in iss_t25):
        print("FAIL self-test: 2.5 未标模式②的首尾帧应拦截"); ok = 0
    # 4) 缺站位声明 → C7
    iss, _, _ = validate(t_ok.replace("【站位声明】：@女主（画面中 · 坐于窗下 · 侧身45°朝左 · 双手交叠膝上）；轴线锁定：单人无轴线；位移：全员原位，无位移。\n", ""), "2.5", "new")
    if not any("C7" in i for i in iss):
        print("FAIL self-test: 缺站位声明应报 C7"); ok = 0
    # 5) 超时长 → C1
    t_long = t_ok.replace("00:04-00:08", "00:04-00:40")
    iss, _, _ = validate(t_long, "2.0", "new")
    if not any("C1" in i for i in iss):
        print("FAIL self-test: 2.0 超 15s 应报 C1", iss); ok = 0
    # 6) 高危词 → C9
    t_gore = t_ok.replace("她从袖中抽出信件。", "她嘴角溢出一线鲜血，断肢横飞。")
    iss, _, _ = validate(t_gore, "2.5", "new")
    if not any("C9" in i for i in iss):
        print("FAIL self-test: 高危词应报 C9"); ok = 0
    # 7) 缺接续状态 → C11
    iss, _, _ = validate(t_ok.replace("【接续状态】：角色动作与空间位置严格继承\n", ""), "2.5", "new")
    if not any("C11" in i for i in iss):
        print("FAIL self-test: 缺接续状态应报 C11"); ok = 0
    # 8) 缺画幅 → C6（连【画幅风格】行里的比例一并去掉）
    t_noframe = t_ok.replace("【画幅风格】16:9 横屏, 电影级质感, PBR, 景深胶片颗粒 (aspect_ratio=16:9)",
                             "【画幅风格】电影级质感, PBR, 景深胶片颗粒")
    iss, _, _ = validate(t_noframe, "2.5", "new")
    if not any("C6" in i for i in iss):
        print("FAIL self-test: 缺画幅回填应报 C6"); ok = 0
    # 9) 单镜 >6s → C10 warn
    _, warns, _ = validate(t_ok.replace("00:04-00:08", "00:04-00:15"), "2.5", "new")
    if not any("C10" in w for w in warns):
        print("FAIL self-test: 单镜>6s 应报 C10"); ok = 0
    # 10) 规则词混入 → C12 warn
    _, warns, _ = validate(t_ok.replace("角色动作与空间位置严格继承", "下段末态继承，拼接节点换机位"), "2.5", "new")
    if not any("C12" in w for w in warns):
        print("FAIL self-test: 规则词混入应报 C12"); ok = 0
    # 11) 镜长雷同 → C13 warn
    t_flat = ("【画幅风格】9:16 竖屏, 写实 (aspect_ratio=9:16)\n"
              "【场景资产】@SCN-厅（外观以场景参考图锁定）\n"
              "【核心人物】@CHR-甲（外观以人物参考图锁定）\n"
              "【站位声明】：@甲（画面左 · 立 · 正面朝右）；轴线锁定：单人无轴线；位移：全员原位，无位移。\n"
              "【时间轴分镜】\n"
              "00:00-00:04 [镜头1] 近景 · 平视 · 固定。甲抬眼。声音：无。台词：无。\n"
              "00:04-00:08 [镜头2] 近景 · 平视 · 固定。甲开口。声音：无。台词：【甲：\"一\"】\n"
              "00:08-00:12 [镜头3] 近景 · 平视 · 固定。甲转身。声音：无。台词：无。\n"
              "00:12-00:15 [镜头4] 近景 · 平视 · 固定。甲落座。声音：无。台词：无。\n"
              "【接续状态】：角色动作与空间位置严格继承\n"
              "【音效】生成音效描述（默认由模型生成）\n"
              "【强制禁止项】画面：角色变形；文字：无字幕\n")
    _, warns, _ = validate(t_flat, "2.5", "new")
    if not any("C13" in w for w in warns):
        print("FAIL self-test: 镜长雷同应报 C13", warns); ok = 0
    # 12) C11 接续状态套话 → WARN（V6.9：套话不提供画面信息）
    _, warns, _ = validate(t_ok, "2.5", "new")
    if not any("C11" in w and "套话" in w for w in warns):
        print("FAIL self-test: 接续状态纯套话应报 C11 WARN", warns); ok = 0
    # 13) C14 合规 OS（闭口画面 + 声音段标注画外）→ 不应报 C14 FAIL
    t_os_ok = t_ok.replace(
        "00:04-00:08 [镜头2] 特写 · 侧角 · 固定。指尖微颤。声音：[SFX: 呼吸]。台词：无。",
        "00:04-00:08 [镜头2] 紧特写 · 侧角 · 固定。他嘴唇紧闭，指尖微颤。"
        "声音：[SFX: 雨声] + 画外·内心独白（OS·暗哑）：\"八年了。\"。台词：无。")
    iss, _, _ = validate(t_os_ok, "2.5", "new")
    if any("C14" in x for x in iss):
        print("FAIL self-test: 合规 OS 不应报 C14 FAIL", [x for x in iss if "C14" in x]); ok = 0
    # 14) C14 声画分离红线：OS 镜行画面段开口词 → FAIL
    t_os_mouth = t_os_ok.replace("他嘴唇紧闭，指尖微颤", "他张开嘴说着，指尖微颤")
    iss, _, _ = validate(t_os_mouth, "2.5", "new")
    if not any("C14" in x for x in iss):
        print("FAIL self-test: OS 画面开口应报 C14 FAIL"); ok = 0
    # 15) C14：OS 写进台词字段 → FAIL
    t_os_dlg = t_ok.replace(
        "00:04-00:08 [镜头2] 特写 · 侧角 · 固定。指尖微颤。声音：[SFX: 呼吸]。台词：无。",
        "00:04-00:08 [镜头2] 特写 · 侧角 · 固定。指尖微颤。声音：[SFX: 呼吸]。台词：【女主（内心独白）：\"八年了\"】")
    iss, _, _ = validate(t_os_dlg, "2.5", "new")
    if not any("C14" in x for x in iss):
        print("FAIL self-test: OS 进台词字段应报 C14 FAIL"); ok = 0
    # 16) C14：OS 使用 {} 台词字符（锁口型）→ FAIL
    t_os_brace = t_ok.replace(
        "00:04-00:08 [镜头2] 特写 · 侧角 · 固定。指尖微颤。声音：[SFX: 呼吸]。台词：无。",
        "00:04-00:08 [镜头2] 特写 · 侧角 · 固定。他嘴唇紧闭。声音：{内心独白：八年了}。台词：无。")
    iss, _, _ = validate(t_os_brace, "2.5", "new")
    if not any("C14" in x for x in iss):
        print("FAIL self-test: OS 用 {} 台词字符应报 C14 FAIL"); ok = 0
    # 17) C15 拉伸凑时：全段 13s 无台词三镜（EP01 暴雨段复现）→ C15 WARN
    t_stretch = ("【画幅风格】9:16 竖屏, 年代质感 (aspect_ratio=9:16)\n"
                 "【场景资产】@SCN-土坯房（外观以场景参考图锁定）\n"
                 "【核心人物】@CHR-女主（外观以人物参考图锁定）\n"
                 "【站位声明】：@女主（画面中下 · 蜷于土炕 · 面朝上）；轴线锁定：单人无轴线；位移：全员原位，无位移。\n"
                 "【时间轴分镜】\n"
                 "00:00-00:05 [镜头1] 近景 · 略俯视 · 固定。暴雨砸漏屋顶，水珠砸在枯瘦手背。声音：雨声。台词：无。\n"
                 "00:05-00:10 [镜头2] 特写 · 平视 · 缓推。她枯瘦的手抓了抓破被，指尖泛白。声音：雨声。台词：无。\n"
                 "00:10-00:13 [镜头3] 特写 · 微仰 · 固定。她抬眼看向门口方向，目光涣散。声音：雨声。台词：无。\n"
                 "【接续状态】：女主蜷在土炕抬眼望门，破被半盖——下段自她撑身起手。\n"
                 "【音效】雨声\n"
                 "【强制禁止项】画面：角色变形；文字：无字幕水印\n")
    iss, warns, _ = validate(t_stretch, "2.0", "new")
    if not any("C15" in w for w in warns):
        print("FAIL self-test: 13s 无台词纯氛围段应报 C15 WARN", warns); ok = 0
    # 18) C15 无台词单镜超 5s → C15 WARN
    t_stretch2 = t_stretch.replace(
        "00:10-00:13 [镜头3] 特写 · 微仰 · 固定。她抬眼看向门口方向，目光涣散。声音：雨声。台词：无。",
        "00:10-00:16 [镜头3] 特写 · 微仰 · 固定。她抬眼看向门口方向，目光涣散。声音：雨声。台词：无。")
    iss, warns, _ = validate(t_stretch2, "2.0", "new")
    if not any("C15" in w and "无台词镜" in w for w in warns):
        print("FAIL self-test: 无台词镜 6s 应报 C15 WARN", warns); ok = 0
    # 19) C12 误报回归：台词里的否定句（角色对白）不应判「否定式硬删除」
    t_dlg_neg = t_ok.replace("台词：无。", "台词：【女主（冷淡）：\"这事跟他没有半点关系。\"】")
    _, warns, _ = validate(t_dlg_neg, "2.5", "new")
    if any("C12" in w and "没有半点" in w for w in warns):
        print("FAIL self-test: 台词内的否定句不应报 C12 硬删除", warns); ok = 0
    # 19b) C12 正例：画面描述里的指令性硬删除仍应报
    t_pic_neg = t_ok.replace("她从袖中抽出信件。", "画面中没有人物，没有家具，只有空墙。")
    _, warns, _ = validate(t_pic_neg, "2.5", "new")
    if not any("C12" in w for w in warns):
        print("FAIL self-test: 画面指令性硬删除仍应报 C12", warns); ok = 0
    # 20) C14 误报回归：【强制禁止项】/【音效】里出现"画外音/旁白"字样不计入 VO 配额
    t_vo_in_ban = t_ok + "【强制禁止项补充】：画外音不得与画内口型不同步，旁白只作一点定调\n"
    _, warns, _ = validate(t_vo_in_ban, "2.5", "new")
    if any("C14" in w and "总字数" in w for w in warns):
        print("FAIL self-test: 禁止项中的画外音字样不应计入 C14 配额", warns); ok = 0
    # 21) C16a 语气错位：有台词镜行的画面段出现声音词 → WARN
    t_tone_mis = (t_ok.replace("她从袖中抽出信件。", "她嘶哑地抬起头。")
                       .replace("台词：无。", "台词：【女主（气音·发颤）：\"你也配提她。\"】", 1))
    _, warns, _ = validate(t_tone_mis, "2.5", "new")
    if not any("C16a" in w for w in warns):
        print("FAIL self-test: 画面段声音词应报 C16a（语气错位）", warns); ok = 0
    # 22) C16b 语气缺失：有台词镜行全未带语气位 → WARN
    t_tone_miss = t_ok.replace("台词：无。", "台词：【女主：\"你也配提她。\"】")
    _, warns, _ = validate(t_tone_miss, "2.5", "new")
    if not any("C16b" in w for w in warns):
        print("FAIL self-test: 台词未带语气位应报 C16b（语气缺失）", warns); ok = 0
    # 23) C16c 空泛结果词：语气位写「愤怒」→ WARN
    t_tone_vague = t_ok.replace("台词：无。", "台词：【女主（愤怒）：\"你也配提她。\"】", 1)
    _, warns, _ = validate(t_tone_vague, "2.5", "new")
    if not any("C16c" in w for w in warns):
        print("FAIL self-test: 语气位空泛词应报 C16c", warns); ok = 0
    # 24) C16 误报回归：合规语气位 + 表情型「冷笑」（被"挂着"修饰）→ 不报 C16
    t_tone_ok = (t_ok.replace("她从袖中抽出信件。", "她嘴角挂着冷笑，抬手扣住袖口。")
                     .replace("台词：无。", "台词：【女主（压着怒·低语）：\"你也配提她。\"】", 1))
    _, warns, _ = validate(t_tone_ok, "2.5", "new")
    if any("C16" in w for w in warns):
        print("FAIL self-test: 合规语气位与表情型冷笑不应报 C16", warns); ok = 0

    # 25) C17 摆位必入画：站位 ≥2 人、某人全段镜行未带到 → WARN
    t_c17 = (t_ok.replace("【核心人物】@CHR-女主（外观以人物参考图锁定）",
                          "【核心人物】@CHR-女主（外观以人物参考图锁定）\\n@CHR-乙（外观以人物参考图锁定，在场）")
                 .replace("【站位声明】：@女主（画面中 · 坐于窗下 · 侧身45°朝左 · 双手交叠膝上）；轴线锁定：单人无轴线；位移：全员原位，无位移。",
                          "【站位声明】：@女主（画面中 · 坐于窗下 · 侧身45°朝左）、@乙（画面右后 · 门边 · 背身而立）；轴线锁定：左女主右乙；位移：全员原位，无位移。"))
    _, warns, _ = validate(t_c17, "2.5", "new")
    if not any("C17" in w for w in warns):
        print("FAIL self-test: 摆位未入画应报 C17", warns); ok = 0
    # 26) C17 豁免：离画标记者豁免、入画者带名 → 不报 C17
    t_c17_ok = (t_c17.replace("00:00-00:04 [镜头1] 中近景 · 平视 · 缓推。她从袖中抽出信件。",
                              "00:00-00:04 [镜头1] 中近景 · 平视 · 缓推。女主从袖中抽出信件。")
                     .replace("@乙（画面右后 · 门边 · 背身而立）", "@乙（画面右后 · 门边 · 背身而立 · 段末离画去正房）"))
    _, warns, _ = validate(t_c17_ok, "2.5", "new")
    if any("C17" in w for w in warns):
        print("FAIL self-test: 入画+离画豁免不应报 C17", warns); ok = 0
    # 27) C17 单人站位不触发（回归）
    _, warns, _ = validate(t_ok, "2.5", "new")
    if any("C17" in w for w in warns):
        print("FAIL self-test: 单人站位不应报 C17", warns); ok = 0

    # 28) C18a 段首镜无人物锚（首镜只有"她"，站位人名未出现）→ WARN
    _, warns, _ = validate(t_ok, "2.5", "new")
    if not any("C18a" in w for w in warns):
        print("FAIL self-test: 段首镜无人名应报 C18a", warns); ok = 0
    # 29) C18a 修复回归：首镜写明主体归属（女主）→ 不报 C18a
    _, warns, _ = validate(t_ok.replace("她从袖中抽出信件。", "女主从袖中抽出信件。"), "2.5", "new")
    if any("C18a" in w for w in warns):
        print("FAIL self-test: 首镜带站位人名不应报 C18a", warns); ok = 0
    # 30) C18a 空镜声明豁免 → 不报 C18a
    _, warns, _ = validate(t_ok.replace("她从袖中抽出信件。", "空镜：雨夜屋檐滴水。"), "2.5", "new")
    if any("C18a" in w for w in warns):
        print("FAIL self-test: 空镜声明不应报 C18a", warns); ok = 0
    # 31) C18b 姿态回退：镜1撑起、镜2又蜷缩且无交代 → WARN
    t_c18b = t_ok.replace("她从袖中抽出信件。", "女主撑起半身瞪向门口。") \
                 .replace("指尖微颤。", "她蜷缩着闭眼，指尖微颤。")
    _, warns, _ = validate(t_c18b, "2.5", "new")
    if not any("C18b" in w for w in warns):
        print("FAIL self-test: 撑起后又蜷缩应报 C18b", warns); ok = 0
    # 31b) C18b 豁免：带「跌回」动作交代 → 不报
    t_c18b_ok = t_ok.replace("她从袖中抽出信件。", "女主撑起半身瞪向门口。") \
                     .replace("指尖微颤。", "她跌回炕沿蜷缩剧咳。")
    _, warns, _ = validate(t_c18b_ok, "2.5", "new")
    if any("C18b" in w for w in warns):
        print("FAIL self-test: 跌回交代不应报 C18b", warns); ok = 0
    # 32) C18c 视线黏道具：说话镜把玩玉佩、无目光/视线归属 → WARN
    t_c18c = t_ok.replace(
        "00:04-00:08 [镜头2] 特写 · 侧角 · 固定。指尖微颤。声音：[SFX: 呼吸]。台词：无。",
        "00:04-00:08 [镜头2] 特写 · 侧角 · 固定。女主指间把玩玉佩。声音：[SFX: 呼吸]。"
        "台词：【女主（慵懒·慢悠悠）：“你还想要什么。”】")
    _, warns, _ = validate(t_c18c, "2.5", "new")
    if not any("C18c" in w for w in warns):
        print("FAIL self-test: 把玩道具说话无视线指派应报 C18c", warns); ok = 0
    # 32b) C18c 修复回归：补「目光落在…脸上」→ 不报
    t_c18c_ok = t_c18c.replace("女主指间把玩玉佩。", "女主指间把玩玉佩，目光落在对面的人脸上。")
    _, warns, _ = validate(t_c18c_ok, "2.5", "new")
    if any("C18c" in w for w in warns):
        print("FAIL self-test: 有目光归属不应报 C18c", warns); ok = 0
    # 33) C18c 举向光源变体：举玉说话无视线指派 → WARN（「重生70」段1 镜4 实测病灶）
    t_c18c_lift = t_ok.replace(
        "00:04-00:08 [镜头2] 特写 · 侧角 · 固定。指尖微颤。声音：[SFX: 呼吸]。台词：无。",
        "00:04-00:08 [镜头2] 近景 · 微仰 · 固定。女主直起身把玉佩举向油灯冲光，下巴微抬。声音：[SFX: 雨声]。"
        "台词：【女主（宣判·一字一顿）：“你的工作，现在是我的了。”】")
    _, warns, _ = validate(t_c18c_lift, "2.5", "new")
    if not any("C18c" in w for w in warns):
        print("FAIL self-test: 举向光源说话无视线指派应报 C18c", warns); ok = 0
    # 34) C18d 景别冲突：特写承载「暴雨砸漏房顶」空间事件 → WARN（实测出空床病灶）
    t_c18d = t_ok.replace("中近景 · 平视 · 缓推。她从袖中抽出信件。",
                          "特写 · 顶拍俯视 · 固定。暴雨砸漏土坯房顶，水珠成线砸在枯瘦手背上。")
    _, warns, _ = validate(t_c18d, "2.5", "new")
    if not any("C18d" in w for w in warns):
        print("FAIL self-test: 特写承载空间事件应报 C18d", warns); ok = 0
    # 34b) C18d 修复回归：同内容改近景承载 → 不报 C18d
    t_c18d_ok = t_ok.replace("中近景 · 平视 · 缓推。她从袖中抽出信件。",
                             "近景 · 微俯 · 固定。女主蜷卧土炕，房顶漏下的雨水砸在手背上。")
    _, warns, _ = validate(t_c18d_ok, "2.5", "new")
    if any("C18d" in w for w in warns):
        print("FAIL self-test: 近景承载房顶漏雨不应报 C18d", warns); ok = 0

    # 35) C18e 反光道具无光效声明 → WARN（实测玉佩被渲染成自发光魔法道具）
    t_c18e = t_ok.replace("指尖微颤。", "她擦拭玉佩。")
    _, warns, _ = validate(t_c18e, "2.5", "new")
    if not any("C18e" in w for w in warns):
        print("FAIL self-test: 反光道具无禁止项声明应报 C18e", warns); ok = 0
    # 35b) C18e 放行：禁止项声明光效负面 → C18e 不重复报（该写法本身由 C19e-b 单独检出，两门分工不重叠）
    t_c18e_ok = t_c18e.replace("文字：无字幕水印", "文字：无字幕水印；玉佩不发光、不透光、不悬浮")
    _, warns, _ = validate(t_c18e_ok, "2.5", "new")
    if any("C18e" in w for w in warns):
        print("FAIL self-test: 禁止项声明发光负面后不应报 C18e", warns); ok = 0
    # 36) C18e 回归：无反光道具的普通段不报
    _, warns, _ = validate(t_ok, "2.5", "new")
    if any("C18e" in w for w in warns):
        print("FAIL self-test: 无反光道具不应报 C18e", warns); ok = 0

    # 37) C19a 裸禁令词污染：镜行出现「不发光/面无笑意」→ WARN（实测否定式禁令全部被无视）
    t_c19a = t_c18e.replace("她擦拭玉佩。", "她擦拭玉佩，玉佩不发光、面无笑意。")
    _, warns, _ = validate(t_c19a, "2.5", "new")
    if not any("C19a" in w for w in warns):
        print("FAIL self-test: 镜行裸禁令词应报 C19a", warns); ok = 0
    # 37b) C19a 修复回归：改正向材质/肌肉描写 → 不报
    t_c19a_ok = t_c18e.replace("她擦拭玉佩。", "她擦拭玉佩，玉体呈深青色实心哑光石质，她双唇抿紧、嘴角向下压。")
    _, warns, _ = validate(t_c19a_ok, "2.5", "new")
    if any("C19a" in w for w in warns):
        print("FAIL self-test: 正向材质描写不应报 C19a", warns); ok = 0
    # 38) C19b 光路触发器：反光道具「举向…灯/光」→ WARN（实测玉佩被画成灯泡）
    t_c19b = t_c18e_ok.replace("她擦拭玉佩。", "她把玉佩举向油灯冲光。")
    _, warns, _ = validate(t_c19b, "2.5", "new")
    if not any("C19b" in w for w in warns):
        print("FAIL self-test: 举向冲光应报 C19b", warns); ok = 0
    # 39) C19c 首镜主体优先：镜1第一个分句以环境开头 → WARN（实测两轮出空房间开场）
    t_c19c = t_ok.replace("[镜头1] 中近景 · 平视 · 缓推。她从袖中抽出信件。",
                          "[镜头1] 近景 · 微俯 · 固定。土炕上漏雨，她从袖中抽出信件。")
    _, warns, _ = validate(t_c19c, "2.5", "new")
    if not any("C19c" in w for w in warns):
        print("FAIL self-test: 首镜环境开头应报 C19c", warns); ok = 0
    # 39b) C19c 修复回归：首分句即人物名/画面主体 → 不报
    t_c19c_ok = t_ok.replace("[镜头1] 中近景 · 平视 · 缓推。她从袖中抽出信件。",
                             "[镜头1] 近景 · 微俯 · 固定。画面主体：女主蜷卧土炕，她从袖中抽出信件。")
    _, warns, _ = validate(t_c19c_ok, "2.5", "new")
    if any("C19c" in w for w in warns):
        print("FAIL self-test: 首镜画面主体开头不应报 C19c", warns); ok = 0
    # 40) C19d 具象光源映射污染：反光道具镜行「映出火苗」→ WARN（实测模型不理解"反射"）
    t_c19d = t_c18e.replace("她擦拭玉佩。", "她擦拭玉佩，玉面映出一小片油灯火苗。")
    _, warns, _ = validate(t_c19d, "2.5", "new")
    if not any("C19d" in w for w in warns):
        print("FAIL self-test: 玉面映出火苗应报 C19d", warns); ok = 0
    # 40b) C19d 修复回归：改零光效材质本色 → 不报（⚠️ 旧基线"光斑语言"已废止，见 46 C20d）
    t_c19d_ok = t_c18e.replace("她擦拭玉佩。", "她擦拭玉佩，玉面呈青玉原色。")
    _, warns, _ = validate(t_c19d_ok, "2.5", "new")
    if any("C19d" in w for w in warns) or any("C20d" in w for w in warns):
        print("FAIL self-test: 零光效材质本色不应报 C19d/C20d", warns); ok = 0
    # 41) C19e-a 禁止项栏目错位：正向指令混入禁止项 → WARN（实测等同废纸）
    t_c19e_a = t_ok.replace("画面：角色变形、穿模；文字：无字幕水印",
                            "画面：角色变形、穿模；全片首帧即镜1的人物近景画面；文字：无字幕水印")
    _, warns, _ = validate(t_c19e_a, "2.5", "new")
    if not any("C19e" in w for w in warns):
        print("FAIL self-test: 禁止项混入首帧正向指令应报 C19e", warns); ok = 0
    # 41b) C19e-a 回归：正向材质描写混入禁止项同样应报（「保持…质感」同族）
    t_c19e_a2 = t_ok.replace("画面：角色变形、穿模；文字：无字幕水印",
                             "画面：角色变形、穿模；道具保持日常石质与金属质感；文字：无字幕水印")
    _, warns, _ = validate(t_c19e_a2, "2.5", "new")
    if not any("C19e" in w for w in warns):
        print("FAIL self-test: 禁止项混入材质正向描写应报 C19e", warns); ok = 0
    # 42) C19e-b 禁止项裸禁令词：不发光/不透光 → WARN（被禁词根反被当画面词）
    t_c19e_b = t_ok.replace("画面：角色变形、穿模；文字：无字幕水印",
                            "画面：角色变形、穿模；玉佩不发光、不透光；文字：无字幕水印")
    _, warns, _ = validate(t_c19e_b, "2.5", "new")
    if not any("C19e" in w for w in warns):
        print("FAIL self-test: 禁止项裸禁令词应报 C19e", warns); ok = 0
    # 42b) C19e 回归：纯净负面清单禁止项 → 不报（t_ok 基线）
    _, warns, _ = validate(t_ok, "2.5", "new")
    if any("C19e" in w for w in warns):
        print("FAIL self-test: 纯净禁止项不应报 C19e", warns); ok = 0
    # 43) C20a 并列主体/同框句式：镜行「首帧即这只手与她的脸同框」→ WARN（实测出片两张脸）
    t_c20a = t_ok.replace("她从袖中抽出信件。", "她的一只手搭在被外，首帧即这只手与她的脸同框。")
    _, warns, _ = validate(t_c20a, "2.5", "new")
    if not any("C20a" in w for w in warns):
        print("FAIL self-test: 同框并列主体应报 C20a", warns); ok = 0
    # 43b) C20a 修复回归：单主体统摄、无同框句 → 不报
    t_c20a_ok = t_ok.replace("她从袖中抽出信件。", "女主蜷卧炕上，她的一只手搭在被外。")
    _, warns, _ = validate(t_c20a_ok, "2.5", "new")
    if any("C20a" in w for w in warns):
        print("FAIL self-test: 单主体锚定不应报 C20a", warns); ok = 0
    # 44) C20b 悬空指示代词：「这只手」无归属定语 → WARN
    t_c20b = t_ok.replace("她从袖中抽出信件。", "这只手搭在被外。")
    _, warns, _ = validate(t_c20b, "2.5", "new")
    if not any("C20b" in w for w in warns):
        print("FAIL self-test: 悬空指示代词应报 C20b", warns); ok = 0
    # 44b) C20b 回归：「她的一只手」带归属 → 不报
    t_c20b_ok = t_ok.replace("她从袖中抽出信件。", "女主蜷卧，她的一只手搭在被外。")
    _, warns, _ = validate(t_c20b_ok, "2.5", "new")
    if any("C20b" in w for w in warns):
        print("FAIL self-test: 带归属写法不应报 C20b", warns); ok = 0
    # 45) C20c 抽象形态形容：「漏雨成线」「手指轻蜷」→ WARN
    t_c20c = t_ok.replace("她从袖中抽出信件。", "漏雨成线砸在她手背上，手指轻蜷。")
    _, warns, _ = validate(t_c20c, "2.5", "new")
    if not any("C20c" in w for w in warns):
        print("FAIL self-test: 抽象形态形容应报 C20c", warns); ok = 0
    # 45b) C20c 回归：「雨滴砸在手背上溅开」具象形态 → 不报
    t_c20c_ok = t_ok.replace("她从袖中抽出信件。", "雨滴砸在她手背上溅开。")
    _, warns, _ = validate(t_c20c_ok, "2.5", "new")
    if any("C20c" in w for w in warns):
        print("FAIL self-test: 具象形态描写不应报 C20c", warns); ok = 0
    # 46) C20d 道具光效描写：光斑/受光与反光道具共现 → WARN（实测出片玉佩点火）
    t_c20d = t_ok.replace("她从袖中抽出信件。", "她把玩玉佩，玉面受油灯照射处只有指甲盖大的一片暖黄光斑，其余保持青玉原色。")
    _, warns, _ = validate(t_c20d, "2.5", "new")
    if not any("C20d" in w for w in warns):
        print("FAIL self-test: 道具光斑描写应报 C20d", warns); ok = 0
    # 46b) C20d 道具贴近光源动作：「举到油灯旁」→ WARN
    t_c20d2 = t_ok.replace("她从袖中抽出信件。", "她直起身把玉佩举到油灯旁。")
    _, warns, _ = validate(t_c20d2, "2.5", "new")
    if not any("C20d" in w for w in warns):
        print("FAIL self-test: 道具贴近光源动作应报 C20d", warns); ok = 0
    # 46c) C20d 回归：零光效材质本色 → 不报
    t_c20d_ok = t_ok.replace("她从袖中抽出信件。", "她把玩玉佩，玉面呈青玉原色。")
    _, warns, _ = validate(t_c20d_ok, "2.5", "new")
    if any("C20d" in w for w in warns):
        print("FAIL self-test: 零光效材质本色不应报 C20d", warns); ok = 0
    # 47) C16d 道具动作与语气冲突：宣判语气 × 把玩玉佩 → WARN（实测出戏）
    t_c16d = (t_ok.replace("她从袖中抽出信件。", "她直起身，把玩玉佩。")
                  .replace("台词：无。", "台词：【女主（宣判·一字一顿）：\\\"现在是我的了。\\\"】", 1))
    _, warns, _ = validate(t_c16d, "2.5", "new")
    if not any("C16d" in w for w in warns):
        print("FAIL self-test: 宣判语气配把玩道具应报 C16d", warns); ok = 0
    # 47b) C16d 修复回归：改攥紧 → 不报
    t_c16d_ok = (t_ok.replace("她从袖中抽出信件。", "她直起身，攥紧玉佩垂在身侧。")
                    .replace("台词：无。", "台词：【女主（宣判·一字一顿）：\\\"现在是我的了。\\\"】", 1))
    _, warns, _ = validate(t_c16d_ok, "2.5", "new")
    if any("C16d" in w for w in warns):
        print("FAIL self-test: 攥紧道具不应报 C16d", warns); ok = 0
    # 47c) C16d 回归：慢悠悠语气 × 把玩 → 不报（闲适把玩只冲突强情绪语气）
    t_c16d_soft = (t_ok.replace("她从袖中抽出信件。", "她把玩玉佩。")
                       .replace("台词：无。", "台词：【女主（慢悠悠·居高临下）：\\\"姐姐，你听我说。\\\"】", 1))
    _, warns, _ = validate(t_c16d_soft, "2.5", "new")
    if any("C16d" in w for w in warns):
        print("FAIL self-test: 慢悠悠语气配把玩不应报 C16d", warns); ok = 0

    # ---- H 系列：MiniMax H3 格式支线（--model h3 · V6.9.8）----
    h3_ok = ("subject_definitions:\n"
             "<Subject 1> 为 <Picture 1> 中的年轻女子：长发挽低髆、白玉簪，炭灰色高领窄袖长袍。\n"
             "<Subject 2> 为 <Picture 2> 中的年轻男子：深色短发束于脑后，左眉上方一道细疤。\n"
             "<Audio 1> 为 <Subject 1>（S1）的音色参考：低而略带沙哑的女声。\n\n"
             "summary:\n[reference generation + audio reference] 目标视频为 <Subject 1> 与 <Subject 2> 雨夜对坐，"
             "以 <Audio 1> 作 <Subject 1> 的音色参考。\n\n"
             "retention_analysis:\n"
             "<Subject 1>（出现于 [Shot 1]、[Shot 2]）：fully_preserved - 长发低髆与炭灰长袍保留。\n"
             "<Subject 2>（出现于 [Shot 1]、[Shot 2]）：fully_preserved - 深色短发与眉上细疤保留。\n"
             "<Audio 1>：reference - 只取其音色引导念白，不复制原始信号。\n\n"
             "detailed_description:\n目标视频为实拍武侠文戏，夜雨冷青色调，35mm 浅景深。\n"
             "[Shot 1] 全景确立回廊。<Subject 1> 立于木栏旁，以 <Audio 1> 所参考的低而沙哑音色（S1）说：<d>[Chinese] 你迟了半刻。</d> 说完闭口。\n"
             "[Shot 2] 在 00:05.000 处，镜头切至 <Subject 2> 的中近景。<Subject 2>（S2）以平直语速说：<d>[Chinese] 名册，我拿来了。</d>\n\n"
             "overall_soundscape:\n雨打石板，风铃轻响两声。\n\n"
             "non_diegetic_music:\n古琴单音起于慢速，末帧前收掉。\n")
    iss, _, _ = validate_h3(h3_ok)
    if iss:
        print("FAIL self-test: 合规 H3 Ref2VA 样例不应报错", iss); ok = 0
    # H1 缺段
    iss, _, _ = validate_h3(h3_ok.replace("<Subject 1>（出现于 [Shot 1]、[Shot 2]）：fully_preserved - 长发低髆与炭灰长袍保留。\n", "")
                               .replace("<Subject 2>（出现于 [Shot 1]、[Shot 2]）：fully_preserved - 深色短发与眉上细疤保留。\n", "")
                               .replace("<Audio 1>：reference - 只取其音色引导念白，不复制原始信号。\n", "")
                               .replace("retention_analysis:\n", ""))
    if not any("H1" in i for i in iss):
        print("FAIL self-test: Ref2VA 缺段应报 H1", iss); ok = 0
    # H2 首镜带时间戳
    iss, _, _ = validate_h3(h3_ok.replace("[Shot 1] 全景确立回廊。", "[Shot 1] 在 00:00.000 处，全景确立回廊。"))
    if not any("H2" in i for i in iss):
        print("FAIL self-test: [Shot 1] 带时间戳应报 H2"); ok = 0
    # H3 时长越界
    iss, _, _ = validate_h3(h3_ok + '"duration_seconds": 20\n')
    if not any("H3" in i and "越界" in i for i in iss):
        print("FAIL self-test: 声明时长 20s 应报 H3"); ok = 0
    # H4 <d> 缺语言标签
    iss, _, _ = validate_h3(h3_ok.replace("<d>[Chinese] 你迟了半刻。</d>", "<d>你迟了半刻。</d>"))
    if not any("H4" in i for i in iss):
        print("FAIL self-test: <d> 缺语言标签应报 H4"); ok = 0
    # H5 未定义标签
    iss, _, _ = validate_h3(h3_ok.replace("雨夜对坐", "与 <Subject 9> 雨夜对坐"))
    if not any("H5" in i for i in iss):
        print("FAIL self-test: 未定义标签应报 H5"); ok = 0
    # H5 定义了却未引用 → WARN
    _, warns, _ = validate_h3(h3_ok.replace("<Audio 1> 为 <Subject 1>（S1）的音色参考：低而略带沙哑的女声。\n",
                                          "<Audio 1> 为 <Subject 1>（S1）的音色参考：低而略带沙哑的女声。\n"
                                          "<Subject 7> 为 <Picture 7> 中的道具：一只未启用的空碗。\n"))
    if not any("H5" in w and "未引用" in w for w in warns):
        print("FAIL self-test: 定义未引用应报 H5 WARN", warns); ok = 0
    # H6 非法保留度标记
    iss, _, _ = validate_h3(h3_ok.replace("fully_preserved - 长发低髆", "preserved - 长发低髆"))
    if not any("H6" in i for i in iss):
        print("FAIL self-test: 非法保留度标记应报 H6"); ok = 0
    # H7 (Sx) 顺序错
    iss, _, _ = validate_h3(h3_ok.replace("低而沙哑音色（S1）说", "低而沙哑音色（S2）说"))
    if not any("H7" in i for i in iss):
        print("FAIL self-test: (Sx) 顺序错应报 H7"); ok = 0
    # H8 栏名 / @ 锚点泄漏
    iss, _, _ = validate_h3(h3_ok + "【站位声明】：@女主（画面左）；@CHR-女主\n")
    if not any("H8" in i for i in iss):
        print("FAIL self-test: 栏名/锚点泄漏应报 H8"); ok = 0
    # H8 否定式（对应 C19）→ WARN
    _, warns, _ = validate_h3(h3_ok + "不要出现人物，没有背景。\n")
    if not any("H8" in w and "否定式" in w for w in warns):
        print("FAIL self-test: 正文否定式应报 H8 WARN", warns); ok = 0
    # H9 画外声缺闭口证据
    t_h9 = h3_ok.replace("说完闭口。", "说完移开视线。") + "她的内心独白：<d>[Chinese] 再也退不回去了。</d>\n"
    iss, _, _ = validate_h3(t_h9)
    if not any("H9" in i for i in iss):
        print("FAIL self-test: 画外声缺闭口证据应报 H9"); ok = 0
    # H10 声音层含对白
    iss, _, _ = validate_h3(h3_ok.replace("雨打石板，风铃轻响两声。", "雨打石板，风铃轻响两声。<d>[Chinese] 测试</d>"))
    if not any("H10" in i for i in iss):
        print("FAIL self-test: soundscape 含 <d> 应报 H10"); ok = 0
    # H11 语气位缺失应 WARN（两个发言人首次出场都去掉发声特征）
    _, warns, _ = validate_h3(h3_ok.replace("以 <Audio 1> 所参考的低而沙哑音色（S1）说", "（S1）说")
                                     .replace("（S2）以平直语速说", "（S2）说"))
    if not any("H11" in w for w in warns):
        print("FAIL self-test: 发言人首次出场缺语气描述应报 H11 WARN", warns); ok = 0
    # H12a 首镜无具名主体 → WARN
    _, warns, _ = validate_h3(h3_ok.replace("[Shot 1] 全景确立回廊。<Subject 1> 立于木栏旁",
                                           "[Shot 1] 空镜：雨落回廊。"))
    if not any("H12a" in w for w in warns):
        print("FAIL self-test: 首镜无主体锚应报 H12a WARN", warns); ok = 0
    # H12b 并列主体/同框句式 → WARN
    _, warns, _ = validate_h3(h3_ok.replace("[Shot 1] 全景确立回廊。",
                                           "[Shot 1] 全景确立回廊，<Subject 1> 与她的一只手同框。"))
    if not any("H12b" in w for w in warns):
        print("FAIL self-test: 首镜同框句式应报 H12b WARN", warns); ok = 0
    # H12c 悬空指示代词 → WARN
    _, warns, _ = validate_h3(h3_ok.replace("立于木栏旁", "立于木栏旁，这只手搭在栏上"))
    if not any("H12c" in w for w in warns):
        print("FAIL self-test: 悬空指示代词应报 H12c WARN", warns); ok = 0
    print("[+] self-test", "PASSED" if ok else "FAILED")
    return ok


def main():
    argv = sys.argv[1:]
    if "--self-test" in argv:
        sys.exit(0 if _self_test() else 1)
    files = [a for a in argv if not a.startswith("-")]
    if not files:
        print(__doc__); sys.exit(2)

    def opt(flag, default=None):
        return argv[argv.index(flag) + 1] if flag in argv else default

    model = opt("--model", "2.5")
    if model not in ("2.5", "2.0", "h3"):
        print("[-] --model 必须 2.5/2.0/h3"); sys.exit(2)
    if not os.path.exists(files[0]):
        print(f"[-] 文件不存在：{files[0]}"); sys.exit(2)
    try:
        # utf-8-sig：容忍 Windows 记事本/PowerShell 写出的带 BOM 文件（否则首行字段名（如 subject_definitions: / 【画幅风格】）识别失败）
        text = open(files[0], encoding="utf-8-sig").read()
    except UnicodeDecodeError:
        print(f"[-] 文件非 UTF-8 文本：{files[0]}"); sys.exit(2)
    except OSError as e:
        print(f"[-] 读取失败：{e}"); sys.exit(2)
    if model == "h3":
        issues, warns, stats = validate_h3(text, opt("--mode", "new"))
    else:
        issues, warns, stats = validate(text, model, opt("--mode", "new"))
    if "--json" in argv:
        print(json.dumps({"issues": issues, "warnings": warns, "stats": stats},
                         ensure_ascii=False, indent=2))
    else:
        print(f"[+] 时长{stats['duration_s']}s 镜头{stats['shots']} 字符{stats['chars']} | model={model} mode={opt('--mode','new')}")
        for w in warns:
            print("[!] WARN: " + w)
        for e in issues:
            print("[-] FAIL: " + e)
        print("[+] PASSED" if not issues else f"[-] {len(issues)} error(s)")
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()