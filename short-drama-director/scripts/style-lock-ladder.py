# -*- coding: utf-8 -*-
"""
I 画风锁 · 递进式选择引擎
来源：审计工作区原型 f_lock_ladder.py，逻辑未改，仅改在案口径。
Step1 影像基底(自动) → Step2 技法家族(给3族) → Step3 导演卡(≤4张) → Step4 可选辅助质感
设计要点：每步都在排除；排除链可追溯；同族 ≤2 张；打斗★/特效★ 为硬门槛。
用法：python style-lock-ladder.py  （内置 5 个题材自测例）
"""
import re

# ============================================================
# 风格库：(编号, 名称, 技法族, 打斗★, 特效★, 一句话特征, 易跑偏, AI落地度, 题材)
# ============================================================
T1, T2, T3, T4, T5, T6, T7, T8 = "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"

STYLES = [
    # ---- T1 刃光派 ----
    (9,  "徐克",      T1, 3, 3, "高反差硬光·广角低机位仰拍·体积雾·凌厉升格", "塑料三渲二 / 游戏CG均匀打光", "B", "武侠玄幻"),
    (7,  "路阳",      T1, 3, 2, "冷青灰配烛火暖橙·低机位贴身跟拍·快刃三五合", "长镜过难须拆跟拍切镜 / 禁五彩仙侠光球", "B", "武侠动作"),
    (12, "袁和平",    T1, 3, 2, "硬桥硬马真实发力链·兵器形制特写·中全景交代", "招式堆砌 / 禁隔空对波", "B", "武侠动作"),
    (38, "塔伦蒂诺",  T1, 3, 1, "极低机位仰拍·复古类型色·章节感",           "时代错位 / 特效单薄",       "A", "犯罪暴力"),
    (44, "昆汀",      T1, 3, 1, "低机位仰拍·章节字幕·九十年代质感",        "同上",                     "A", "犯罪暴力"),
    (39, "芬奇",      T1, 2, 2, "冷绿低照度·硬边光·秩序构图",             "过冷过暗 / 打斗看不清",    "A", "悬疑犯罪"),
    (37, "维伦纽瓦",  T1, 2, 3, "单色主导·巨物压迫·尘雾弥漫",             "色调过灰 / 节奏拖沓",      "A", "科幻史诗"),
    (42, "库布里克",  T1, 3, 2, "绝对对称·冷暖极端分离·固定长镜",         "AI难撑，须降级为固定对称", "C", "哲学惊悚"),
    # ---- T2 冷峻秩序派 ----
    (10, "王家卫",    T2, 0, 0, "抽帧残影·霓虹暖黄交错·狭窄空间贴身手持", "禁粒子禁高帧率，打戏禁用", "B", "都市情感"),
    (33, "朴赞郁",    T2, 3, 2, "中轴对称·高对比·冷蓝深红",               "造作 / 仪式感过重",        "A", "惊悚暴力"),
    (52, "罗杰·狄金斯", T2, 2, 2, "阴影侧取景·纯实用光源·冷暖分离·10~15cm缓推", "禁无源夜戏蓝光 / 禁正面平光", "A", "实拍光影"),
    (11, "杜琪峰",    T2, 0, 1, "长焦压缩·冷静机位·疏离构图·灰蓝调",     "节奏过平 / 缺情绪抓手",    "A", "都市写实"),
    (40, "韦斯·安德森", T2, 0, 0, "正面中轴·粉彩低饱和·舞台式布景",        "打斗变摆拍",                "A", "喜剧美学"),
    (41, "大卫·林奇",  T2, 1, 1, "强色光源·广角变形·梦境空间",           "非自然配色 / 观众出戏",    "B", "超现实"),
    # ---- T3 柔光写实派 ----
    (17, "李安",      T3, 0, 1, "自然侧光·中景为主·低饱和·留白",         "节奏过缓 / 缺视觉冲击",    "A", "克制写实"),
    (25, "是枝裕和",  T3, 0, 0, "家庭实景·窗侧自然光·中近景",             "无动作 / 情绪平",          "A", "家庭日常"),
    (31, "高畑勋",    T3, 2, 1, "淡雅写实·温和光·织物与器物细节",         "动作幅度小",                "A", "温柔写实"),
    (30, "铃木敏郎",  T3, 0, 0, "水彩手绘·柔和日光·淡雅彩",               "无动作",                    "A", "生活质感"),
    (51, "吕贝·贝松", T3, 1, 1, "儿童视角低机位·暖自然光·静谧",           "不适合打斗",                "A", "童年视角"),
    # ---- T4 浓艳装饰派 ----
    (1,  "张艺谋",    T4, 1, 2, "大色块·对称仪式感·民艺浓艳",             "配色过艳 / 人物失焦",      "A", "仪式叙事"),
    (21, "王童",      T4, 1, 1, "民间装饰纹样·浓饱和·图画性构图",         "画面拥挤 / 缺纵深",        "A", "视觉华丽"),
    (15, "李少红",    T4, 0, 1, "柔焦·浓艳绸缎·对称帘幕·烛光暖影",       "过甜 / 缺质感",             "A", "古典唯美"),
    (16, "刘镇伟",    T4, 1, 2, "高饱和奇幻·柔光人像·蓝紫幻光",         "廉价影楼感",                "A", "港式奇幻"),
    (35, "金炯柱",    T4, 0, 1, "高饱和撞色·装饰性构成·时尚造型感",       "过时尚 / 脱离题材",         "A", "时尚视觉"),
    # ---- T5 纪实手持派 ----
    (18, "侯孝贤",    T5, 0, 0, "固定远景长镜·真实环境光",                "打斗会被看淡",              "B", "文艺写实"),
    (34, "李沧东",    T5, 0, 0, "粗粝手持·真实自然光·灰土调",             "非动作向",                  "A", "社会写实"),
    (45, "索德伯格",  T5, 1, 0, "冷调自然光·轻手持·街拍感",               "动作松散",                  "A", "街拍犯罪"),
    (57, "荒木经惟",  T5, 0, 1, "高ISO噪点·侵入式近距·弱光冷绿",          "噪点过量 / 人物变形",      "B", "侵入视角"),
    (53, "霍伊特",    T5, 1, 0, "手持·自然光·自然运动模糊·抓拍构图",      "画面不稳 / 主体丢失",       "A", "纪录感"),
    # ---- T6 极端写意派 ----
    (49, "塔可夫斯基", T6, 0, 1, "自然光·水与雾·极长镜",                  "AI亦难撑，须拆静帧+慢镜",   "C", "诗电影"),
    (61, "斯文·尼奎斯特", T6, 0, 0, "自然光·柔和低反差·中远景·静止长拍",       "无动作",                    "B", "极简长镜"),
    (23, "北野武",    T6, 1, 0, "极简固定镜·大段空镜·骤停画格",           "打斗会被剪成静止",           "C", "极简暴力"),
    (8,  "毕赣",      T6, 0, 0, "潮湿雾气·隧道霓虹·长焦压缩",             "时间失速，无动作语法",       "C", "文艺诗电影"),
    (50, "帕索里尼",  T6, 1, 1, "极远景平视·黄昏低角度光·油画笔触",       "人物过小 / 叙事断裂",       "B", "古典油画"),
    # ---- T7 神话史诗派 ----
    (66, "暗黑神话游戏CG", T7, 3, 3, "虚幻5主机游戏CG·高精PBR战损甲胄·暗黑高光比·丁达尔体积雾", "禁2D卡通平涂 / 禁轻飘无重力", "A", "游戏CG暗黑神话"),
    (72, "东方神话3D奇幻", T7, 3, 3, "东方神话3D电影感·织金玉石次表面散射·青绿赤金·巨物法相奇观", "禁2D粗黑边 / 禁阴暗废土风", "A", "东方神话3D"),
    (6,  "乌尔善",    T7, 3, 3, "岩画兽纹·巨大体量对比·土红骨白·篝火暖光", "西方奇幻铠甲 / 廉价土黄",   "A", "神话史诗(实拍)"),
    (47, "卡梅隆",    T7, 2, 3, "巨物·冷蓝·高动态范围·奇观场面",         "重技术轻动作",              "A", "技术奇观"),
    (29, "大友克洋",  T7, 2, 3, "冷金属机械·微距·硬表面反射",             "机械过密 / 人物被吞",       "A", "机甲科幻"),
    (36, "诺兰",      T7, 2, 2, "巨物尺度·冷蓝高对比·中轴对称",           "动作偏重 / 节奏慢",         "A", "科幻动作"),
    (46, "雷德利",    T7, 1, 2, "古典油画感·厚实暗部·暖金烛光",           "打斗偏阵仗",                "A", "古典史诗"),
    (22, "黑泽明",    T7, 3, 1, "自然硬光·实景搭景·多机位群像",          "无特效传统 / 需另补",        "A", "时代剧"),
    # ---- T8 动画与国漫3D/CG派 ----
    (65, "国漫3D仙侠",     T8, 3, 3, "次世代国漫3D半写实·PBR丝绸金玉·丁达尔云雾·流光剑气", "禁2D粗黑描边 / 禁廉价塑料反光", "A", "国漫3D修仙玄幻"),
    (71, "国漫3D进阶水墨", T8, 3, 3, "国漫3D三渲二水墨·枯笔飞白描边·狂草墨韵刀气·朱砂留白对冲", "禁退化为2D剪纸 / 禁死灰滤镜", "A", "3D进阶水墨国风"),
    (64, "MAPPA",     T8, 3, 3, "厚涂质感·高对比阴影·动态变形帧",         "日式赛璐璐 / 表情崩坏",      "A", "2D都市动画厚涂"),
    (62, "吉卜力",    T8, 2, 2, "手绘水彩背景·柔和日光·云与风写实",       "偏飞行自然 / 非硬核打斗",   "A", "奇幻日常"),
    (63, "新海诚",    T8, 1, 2, "极致高饱和天空·强烈光斑·玻璃反射",       "过甜 / 人物失真",            "A", "都市青春"),
    (68, "押井守动画向", T8, 2, 3, "冷调·玻璃幕墙·手绘人物+3D背景",       "混合质感不统一",             "B", "赛博动画"),
]

FAMILY_NAME = {
    T1: "刃光派",   T2: "冷峻秩序派", T3: "柔光写实派", T4: "浓艳装饰派",
    T5: "纪实手持派", T6: "极端写意派", T7: "神话史诗派", T8: "动画与国漫3D/CG派",
}
FAMILY_FEATURE = {
    T1: "高反差硬光 · 强轮廓 · 广角低机位仰拍 · 升格慢镜",
    T2: "冷蓝灰调 · 中轴对称 · 几何分割 · 低照度",
    T3: "窗侧自然光 · 低对比 · 中近景 · 克制表演",
    T4: "大色块 · 高饱和 · 对称仪式感 · 民艺纹样",
    T5: "粗粝手持 · 自然光 · 灰土调 · 颗粒不修饰",
    T6: "大留白 · 极简 · 非自然色 · 极长镜",
    T7: "巨大体量对比 · 逆光尘雾 · 图腾兽纹 · 硬表面机械",
    T8: "次世代国漫3D建模 · 游戏CG · 3D三渲二进阶水墨 · 2D厚涂赛璐璐",
}

# ★互斥族对：不可作为「主 + 辅」混用
EXCLUSIVE = [({T1}, {T3}), ({T1}, {T4}), ({T1}, {T5}),
             ({T7}, {T8}), ({T2}, {T4}), ({T6}, {T4})]

# ============================================================
# Step 1 · 影像基底
# ============================================================
BASE_ANIME   = "3D CG 动画"
BASE_LIVE    = "真人实拍质感"
BASE_2D      = "2D 手绘动画"
BASE_INK     = "水墨二维"

# 各族适配哪些基底（T8 动画与国漫3D/CG派只配动画基底，T1/T3/T5 等通用）
FAMILY_BASE = {
    T1: [BASE_ANIME, BASE_LIVE, BASE_2D],
    T2: [BASE_LIVE, BASE_ANIME],
    T3: [BASE_LIVE, BASE_2D],
    T4: [BASE_LIVE, BASE_2D, BASE_ANIME],
    T5: [BASE_LIVE],
    T6: [BASE_LIVE, BASE_2D, BASE_INK],
    T7: [BASE_ANIME, BASE_LIVE],
    T8: [BASE_ANIME, BASE_2D, BASE_INK],
}

# ============================================================
# 题材 → 技法族路由（每场只给 3 族）
# ============================================================
GENRE_FAMILY = [
    (["玄幻", "仙侠", "修真", "斗法", "神魔", "法术"], [T1, T7, T8]),
    (["武侠", "武打", "械斗", "江湖", "刀剑"],         [T7, T1, T3]),
    (["机甲", "赛博", "科幻战斗"],                    [T7, T8, T2]),
    (["异能", "超能力", "都市战斗"],                  [T8, T1, T2]),
    (["悬疑", "犯罪", "暗杀", "警匪", "追车"],        [T2, T5, T1]),
    (["战争", "史诗", "神话"],                        [T7, T1, T6]),
    (["恐怖", "惊悚", "灵异"],                        [T2, T5, T1]),
    (["都市情感", "情感", "都市", "职场", "甜宠", "爱情"], [T2, T3, T4]),
    (["怀旧", "年代", "复古", "回忆"],                [T2, T4, T3]),
    (["文艺", "静思", "诗", "散文", "家庭", "日常"],  [T6, T3, T5]),
    (["青春", "校园", "成长"],                        [T8, T3, T6]),
    (["喜剧", "荒诞"],                                [T2, T4, T5]),
]

GENRE_COMBAT  = ["玄幻","仙侠","修真","武侠","武打","格斗","动作","战斗","打斗","打戏",
                 "械斗","暗杀","枪战","追车","战争","搏杀","厮杀"]
GENRE_NOCOMBAT = ["都市情感","情感","文艺","静思","家庭","日常","青春","怀旧","年代",
                  "甜宠","职场","商战","悬疑文戏","心理","生活流","散文",
                  "文戏","纯对话","剧情向"]   # ★P8 补：文戏/纯对话 是分镜稿最常用的「无打斗」自述词
NEG_PREFIX = ["无", "不", "没有", "没", "非", "零", "免", "去"]
# ★P8 补：旧实现用 `(p + w) in t` 逐字拼接，只能识别**紧贴**的「无打斗／没有打斗」；
#   「没有**任何**打斗」「不含一点打斗」这类中间隔字的否定仍然判成**有打斗**
#   （实测：题材串「都市甜宠办公室，两人对话，纯文戏，没有任何打斗」→ 含打斗=True，
#    依据「信号词打斗」→ 甜宠项目被塞一张仙侠打斗卡）。
#   现改为**前置窗口否定判定**：关键词前 8 字内出现否定词即视为已被否定。
_NEG_WINDOW_RE = re.compile(
    r"(?:毫无|没有任何|没有|不含|无任何|全无|无|没|不|非|零|免|去)[^，。；、！？\s]{0,4}$")


def _negated_at(t, start):
    return bool(_NEG_WINDOW_RE.search(t[max(0, start - 8):start]))


def _live_hits(t, words):
    """返回在**非否定语境**下真实出现的词（每个词只看首处出现即可）。"""
    out = []
    for w in words:
        for m in re.finditer(re.escape(w), t):
            if not _negated_at(t, m.start()):
                out.append(w)
                break
    return out
VFX_HIGH_SIG = ["法术","斗法","玄幻","仙侠","修真","神通","法阵","大招","神魔","仙术","异能","风暴","领域"]
COMBAT_SIG = ["打斗","打戏","战斗","对决","开打","武打","搏杀","厮杀","对招","交手","格斗","斗法","大战"]


def detect_combat(t):
    live = _live_hits(t, COMBAT_SIG)          # 非否定语境的打斗信号
    hc = _live_hits(t, GENRE_COMBAT)          # 非否定语境的题材词
    hn = [w for w in GENRE_NOCOMBAT if w in t]
    if not live and not hc:
        _raw = [w for w in COMBAT_SIG if w in t]
        if _raw:
            return False, f"否定式（「{_raw[0]}」前有否定词）"
    if hn and not hc:
        return False, f"题材词「{hn[0]}」非动作向"
    if hc:
        return True, f"题材词「{hc[0]}」"
    if live:
        return True, f"信号词「{live[0]}」"
    return False, "无打斗信号"


def detect_base(t):
    if any(w in t for w in ["禅意", "水墨", "古风意蕴"]):
        return BASE_INK
    if any(w in t for w in ["玄幻", "仙侠", "机甲", "神魔", "3D", "国漫", "高燃"]):
        return BASE_ANIME
    if any(w in t for w in ["手绘", "童话", "水彩", "赛璐璐"]):
        return BASE_2D
    return BASE_LIVE


# ★P8（2026-10-24 · 采纳网友建议书 P-02）：影像基底是**必问项**，不是自动判定项。
#   病根：旧版第 193 行字面写「（不问，自动带出）」，而 style-lock-protocol.md:46 是
#   2026-10-13 用户裁定原文「影像基底不得由执行者自动带出……用户未表态 = 停下询问」。
#   脚本与协议直接冲突，且**执行者会照脚本走**——真人项目被自动判成 3D CG，画质词 /
#   骨相 / 候选池 / 打戏档位全错在源头（用户原话：「我这个是真人的哈」）。
#   故 detect_base() 降级为**倾向提示**（suggest），只有用户显式给了 --base 才出卡。
BASE_ALIASES = [
    (BASE_LIVE,  ("真人", "实拍", "liveaction", "live-action", "live")),
    (BASE_2D,    ("2d", "手绘", "赛璐璐", "动画2d", "厚涂")),
    (BASE_ANIME, ("3d", "cg", "国漫", "三维", "动画3d", "anime")),
    (BASE_INK,   ("水墨", "ink", "国风意蕴")),
]


def parse_base(raw):
    """把用户回答规整到四种基底之一；认不出返回 None（不许猜）。"""
    if not raw:
        return None
    s = str(raw).strip().lower().replace(" ", "")
    for canon, keys in BASE_ALIASES:
        if s == canon.lower().replace(" ", ""):
            return canon
        for k in keys:
            if k in s:
                return canon
    return None


def route_family(t):
    best = None
    for keys, fams in GENRE_FAMILY:
        hit = [k for k in keys if k in t]
        if hit and (best is None or len(hit) > best[0]):
            best = (len(hit), fams, hit[0])
    if best:
        return best[1], best[2]
    return [T1, T2, T3], "未命中（默认综合）"


# ============================================================
# 主流程
# ============================================================
def recommend(text, top=4, base=None):
    lines = []
    # ---- Step 1 ----
    suggest = detect_base(text)
    combat, why = detect_combat(text)
    vfx_high = any(w in text for w in VFX_HIGH_SIG)

    lines.append("=" * 84)
    lines.append(f"题材输入：{text}")
    lines.append("=" * 84)
    lines.append("")
    if base is None:
        # ★P8：不问就不出卡。出卡 = 默认替用户拍了形态，正是 2026-10-13 裁定要禁的事。
        lines.append("【Step 1 · 影像基底】⛔ 必问项 · 不得自动带出")
        lines.append("   请先向用户确认，四选一（用户未表态 = 停下询问，禁自行判定）：")
        lines.append("     ① 真人实拍质感    ② 2D 手绘（赛璐璐／厚涂）")
        lines.append("     ③ 3D CG（国漫3D／游戏CG）    ④ 水墨二维")
        lines.append(f"   机器识别倾向：{suggest} —— **仅供提示，不得当结论**")
        lines.append("   （依据：style-lock-protocol.md §三 · 2026-10-13 用户裁定「形态必问」）")
        lines.append("")
        lines.append("   → 用户明确后重跑：python style-lock-ladder.py \"<题材>\" --base=真人|2D|3D|水墨")
        lines.append("   → 基底一旦判错，画质词／形体骨相／候选池／打戏档位全部跟着错，且错在源头、下游无从纠正")
        return "\n".join(lines)
    lines.append(f"【Step 1 · 影像基底】用户已确认：{base}")
    lines.append(f"   → 打斗={combat}（依据：{why}）  高特效={vfx_high}")
    if suggest != base:
        lines.append(f"   ⚠ 机器倾向原为「{suggest}」，与用户确认不一致 → **以用户为准**，"
                     f"并按真人/形态口径重写 STYLE_PROFILE")

    # ---- Step 2 ----
    fams, gk = route_family(text)
    lines.append("")
    lines.append("【Step 2 · 技法家族】给你 3 族（其余已排除）")
    excluded_fams = [f for f in FAMILY_NAME if f not in fams]
    for f in fams:
        lines.append(f"   ◆ {f} {FAMILY_NAME[f]:<7}  {FAMILY_FEATURE[f]}")
    lines.append(f"   命中题材族：{gk}")
    lines.append(f"   已排除 {len(excluded_fams)} 族："
                 + " · ".join(f"{FAMILY_NAME[f]}" for f in excluded_fams))
    if combat:
        lines.append("   原因：这些族的打斗承载均 ≤★1，且部分与硬边打光互斥")

    # ---- Step 3 ----
    # 排除链：① 基底冲突 ② 打斗门槛 ③ 特效门槛
    pool, excl = [], []
    for s in STYLES:
        num, name, fam, fight, fx, look, warn, grade, genre = s
        if base not in FAMILY_BASE[fam]:
            excl.append((name, fam, f"与影像基底「{base}」冲突"))
            continue
        if fam not in fams:
            excl.append((name, fam, "不在本次技法家族内"))
            continue
        if combat:
            if fight <= 1:
                excl.append((name, fam, f"打斗承载 ★{fight}，不适合打戏"))
                continue
            if vfx_high and fx < 2:
                excl.append((name, fam, f"特效承载 ★{fx}，撑不住高特效打斗"))
                continue
        pool.append(s)

    # ★★排序规则（唯一一套，有无打斗通用）：
    #   题材亲和度优先 → 能力总分次之
    #   反面教材（已实测抓到）：无条件按 打斗★+特效★ 排，
    #     会让「都市悬疑格斗」场景把武侠史诗的徐克顶到 A 卡 —— 纯荒谬。
    AFFINITY = {
        # 打戏向
        "国漫3D仙侠": ["国漫", "3D", "玄幻", "仙侠", "修仙", "修真", "斗法", "法术", "剑气", "宗门", "高燃"],
        "暗黑神话游戏CG": ["游戏CG", "CG", "黑神话", "暗黑", "神话", "神魔", "虚幻5", "重工业", "妖魔", "古刹"],
        "国漫3D进阶水墨": ["水墨", "三渲二", "国风", "国漫", "3D", "武侠", "仙侠", "剑道", "狂草", "写意", "斗法"],
        "东方神话3D奇幻": ["神话", "神魔", "法相", "奇幻", "国漫", "3D", "仙侠", "追光", "天庭"],
        "徐克":   ["实拍", "武侠", "江湖", "刀剑", "打斗", "香港"],
        "乌尔善": ["实拍", "上古", "战争", "史诗", "封神"],
        "MAPPA":  ["2D", "厚涂", "都市异能", "异能", "超能力", "日漫"],
        "维伦纽瓦": ["科幻", "巨物", "神魔", "对轰", "机甲"],
        "卡梅隆": ["科幻", "巨物", "技术", "奇观", "对轰"],
        "大友克洋": ["机甲", "机械", "赛博", "科幻"],
        "诺兰":   ["科幻", "巨物", "悬疑", "结构"],
        "黑泽明": ["武侠", "时代", "史诗", "群像", "战争"],
        "雷德利": ["战争", "史诗", "古典"],
        "袁和平": ["武侠", "动作", "兵器"],
        "路阳":   ["武侠", "动作", "长镜"],
        "昆汀":   ["犯罪", "追车", "枪战", "暴力", "章节"],
        "塔伦蒂诺": ["犯罪", "暴力", "复古", "章节"],
        "朴赞郁": ["暴力", "惊悚", "犯罪", "对称", "仪式"],
        "芬奇":   ["悬疑", "犯罪", "暗杀", "惊悚", "秩序", "冷"],
        "温子仁": ["恐怖", "惊悚", "幽闭", "灵异"],
        "大友":   ["机甲", "机械"],
        # 情感/文艺向
        "王家卫": ["情感", "都市", "怀旧", "年代", "夜", "暧昧", "回忆", "爱情"],
        "李安":   ["情感", "家庭", "克制", "现实", "亲情", "伦理"],
        "是枝裕和": ["日常", "家庭", "情感", "孩子", "温情"],
        "高畑勋": ["日常", "温柔", "手绘", "童话", "治愈"],
        "铃木敏郎": ["日常", "手绘", "水彩", "治愈"],
        "李少红": ["古典", "唯美", "柔焦", "绸缎", "爱情"],
        "张艺谋": ["仪式", "浓艳", "叙事", "民艺", "古装"],
        "王童":   ["浓艳", "华丽", "装饰", "民艺", "古装"],
        "刘镇伟": ["奇幻", "港式", "柔光", "爱情"],
        "金炯柱": ["时尚", "高饱和", "都市", "甜宠"],
        "杜琪峰": ["都市", "写实", "疏离", "长焦", "警匪"],
        "韦斯·安德森": ["喜剧", "荒诞", "对称", "舞台", "荒诞喜"],
        "大卫·林奇": ["梦境", "超现实", "非自然", "悬疑"],
        # 写实/纪实向
        "侯孝贤": ["写实", "远景", "生活", "文艺", "年代"],
        "李沧东": ["社会", "写实", "灰调", "粗粝", "现实"],
        "索德伯格": ["街拍", "自然", "冷调", "犯罪", "年代"],
        "荒木经惟": ["侵入", "弱光", "日常", "噪点", "纪实"],
        "霍伊特":   ["纪录", "手持", "抓拍", "运动"],
        # 极端写意向
        "塔可夫斯基": ["诗", "静思", "长镜", "水", "哲思"],
        "斯文·尼奎斯特":  ["极简", "静思", "静止", "自然光", "长镜", "哲思"],
        "北野武": ["极简", "暴力", "骤停", "悬疑"],
        "毕赣":  ["诗", "文艺", "湿", "梦境"],
        "帕索里尼": ["古典", "油画", "远景", "神话题"],
        # 动画向
        "吉卜力": ["奇幻", "日常", "手绘", "童话", "治愈"],
        "新海诚": ["青春", "都市", "校园", "高饱和"],
        "押井守动画向": ["赛博", "科幻", "玻璃", "都市"],
        "押井守": ["赛博", "科幻", "孤独", "都市"],
    }

    def aff(s):
        return sum(1 for w in AFFINITY.get(s[1], []) if w in text)
    #题材亲和优先 → 能力总分次之
    pool.sort(key=lambda s: (aff(s), s[3] + s[4]), reverse=True)
    picked, per_fam = [], {}
    for s in pool:
        f = s[2]
        if per_fam.get(f, 0) >= 2:
            continue
        per_fam[f] = per_fam.get(f, 0) + 1
        picked.append(s)
        if len(picked) >= top:
            break

    lines.append("")
    lines.append(f"【Step 3 · 导演卡】候选池 {len(pool)} 组 · 已排除 {len(excl)} 组 · 出卡 {len(picked)} 张")
    lines.append("")
    for i, (num, name, fam, fight, fx, look, warn, grade, genre) in enumerate(picked):
        tag = "【默认推荐】" if i == 0 else ""
        label = "ABCD"[i] if i < 4 else str(i + 1)
        lines.append(f"  {label} {tag}{name}向· {fam} {FAMILY_NAME[fam]} · {genre}")
        lines.append(f"      看得见：{look}")
        lines.append(f"      易跑偏：{warn}")
        fs = "★" * fight if fight else "—"
        xs = "★" * fx if fx else "—"
        lines.append(f"      打斗 {fs:<4} 特效 {xs:<4}    AI 落地度 {grade}")
        if grade == "B":
            lines.append(f"      系统将自动补写法约束（B级）")
        if grade == "C":
            lines.append(f"      ★视频模型难稳定呈现，须先确认降级方案")
    lines.append("")
    lines.append(f"  D 自定义 → 你直接描述，我按你的描述建 STYLE_BIBLE")

    # ---- Step 4 ----
    # ★修正：Step4 是「选定主族之后，问能不能配辅助族」，
    #   不是把所有候选族都标成可叠加。必须走互斥对查表。
    # ★2026-10-15 修复：候选池被排除链排空时，原代码直接 `picked[0][1]` / `FAMILY_NAME[None]`
    #   → IndexError / KeyError 崩溃（实测「水墨 悬疑 犯罪」：INK 基底 + T2/T5/T1 均不支持 INK）。
    #   排除链本就允许排空（可追溯），排空必须优雅降级、保留排除明细，不得崩。
    main_fam = picked[0][2] if picked else None
    lines.append("")
    lines.append("【Step 4 · 可选辅助质感】（可选；不指定 = 不叠加，按主族执行）")
    if not picked:
        lines.append("   ⚠️ 排除链把候选池排空：没有任何导演卡同时满足"
                     "「影像基底 × 技法家族 × 打斗/特效门槛」。")
        lines.append("   处理建议：① 换更宽的题材词（去掉「水墨」这类强基底词）；"
                     "② 直接走 D 自定义描述你要的质感；③ 核对题材与影像基底是否冲突。")
    else:
        lines.append(f"   假设你选了 A {picked[0][1]}向 · 主族 = {main_fam} {FAMILY_NAME[main_fam]}")
        lines.append("   可叠加的辅助族：")
        any_ok = False
        for f in FAMILY_NAME:
            if f == main_fam:
                continue
            conflict = any((main_fam == a and f == b) or (main_fam == b and f == a)
                           for a, b in EXCLUSIVE)
            if conflict:
                continue
            if f not in fams:
                continue          # 只在本次候选族内谈叠加
            eff = {
                T1: "硬光打戏 + 厚涂质感（已实测成立）",
                T2: "硬边轮廓 + 冷调秩序",
                T3: "强化自然光下的动势",
                T4: "史诗体量 + 浓艳民艺",
                T5: "秩序构图 + 粗粝手持",
                T6: "冷调 + 留白疏离",
                T7: "硬光 + 上古图腾",
                T8: "硬光打戏 + 厚涂质感（已实测成立）",
            }.get(f, "视参数组兼容度而定")
            lines.append(f"     ✓ {f} {FAMILY_NAME[f]:<7} → {eff}")
            any_ok = True
        if not any_ok:
            lines.append("     （本次候选族内无族可叠加，直接按主族执行）")
        lines.append("   不可叠加（互斥，写死，与是否在本场候选无关）：")
        any_bad = False
        for a, b in EXCLUSIVE:
            if main_fam in (a, b):
                other = (b if main_fam == a else a)
                lines.append(f"     ✗ {other} {FAMILY_NAME[other]:<7} → 互斥"
                             f"（{FAMILY_FEATURE[main_fam][:10]}… ↔ {FAMILY_FEATURE[other][:10]}…）")
                any_bad = True
        if not any_bad:
            lines.append("     （无）")

    # ---- 排除明细 ----
    lines.append("")
    lines.append("【排除明细】（让你知道系统替你做了什么）")
    from collections import defaultdict
    byreason = defaultdict(list)
    for nm, fam, rs in excl:
        byreason[rs].append(nm)
    for rs, names in byreason.items():
        lines.append(f"   · {rs}（{len(names)} 组）：" + " · ".join(names[:10])
                     + (" …" if len(names) > 10 else ""))

    return "\n".join(lines)


if __name__ == "__main__":
    # ★P8（2026-10-24 · 采纳网友建议书 P-01）：旧版 __main__ 只循环硬编码示例，**全程不读
    #   sys.argv** → 任何输入都输出同一套「3D CG + 打斗=True（依据：题材词「玄幻」）」，
    #   SKILL 与协议宣称的「题材→候选池路由引擎」实际是**演示脚本**。使用者拍甜宠会拿到
    #   仙侠打斗卡。现改为：位置参数=题材，--base=用户已确认的影像基底，--demo=原示例回归。
    import sys

    # 回归锁案例（--demo / 无参数时跑；亦作 2026-10-15 INK 排空回归）
    demo_cases = [
        "玄幻仙侠打斗，有法术特效",
        "都市情感夜戏，无打斗",
        "现代都市悬疑，追车加近身格斗",
        "神魔级对轰，特效很重",
        "年代怀旧文戏，两个人回忆往事",
        # ★2026-10-15 回归锁：INK 水墨基底 + 不支持水墨的题材族 → 候选池排空，
        #   旧代码在此 IndexError/KeyError 崩溃；修复后应优雅降级（出卡 0 张 + 排空提示）。
        "水墨 悬疑 犯罪",
    ]

    args = [a for a in sys.argv[1:]]
    # ★P9：包内惯例是 `--self-test`，本脚本原先只有 `--demo` →「自检三件套」在这里
    #   按名字找不到入口（check_package ◑25 已把这条做成结构断言）。别名等价。
    _selftest = "--self-test" in args
    if not args or "--demo" in args or _selftest:
        print("【演示模式】出卡基底按各示例各自的机器倾向（仅演示，禁当判定依据）")
        print("实质使用：python style-lock-ladder.py \"<题材>\" --base=真人|2D|3D|水墨\n")
        for c in demo_cases:
            print(recommend(c, base=detect_base(c)))
            print("\n\n")
        if _selftest:
            print(f"[+] style-lock-ladder self-test PASSED（{len(demo_cases)} 组内置示例全部出卡未崩）")
        sys.exit(0)

    base_raw, text_parts, top = None, [], 4
    for a in args:
        if a.startswith("--base="):
            base_raw = a.split("=", 1)[1]
        elif a == "--base":
            base_raw = "__MISSING__"      # 只写 --base 不给值 → 视为未确认
        elif a.startswith("--top="):
            try:
                top = max(1, int(a.split("=", 1)[1]))
            except ValueError:
                pass
        elif not a.startswith("--"):
            text_parts.append(a)
    text = " ".join(text_parts).strip()
    if not text:
        print("用法：python style-lock-ladder.py \"<题材串>\" --base=真人|2D|3D|水墨 [--top=4]")
        print("      python style-lock-ladder.py --demo        # 跑内置回归示例（--self-test 等价）")
        sys.exit(2)

    base = parse_base(base_raw) if base_raw and base_raw != "__MISSING__" else None
    if base_raw and base_raw != "__MISSING__" and base is None:
        print(f"⚠ 无法识别 --base=「{base_raw}」→ 按「未确认」处理，不出卡。")
        print("   可写：真人 / 实拍 / 2D / 手绘 / 3D / CG / 水墨")
        base = None

    print(recommend(text, top=top, base=base))
    if base is None:
        # 退出码 3 = 明确信号「等用户回答，不是错误，也不是完成」
        sys.exit(3)