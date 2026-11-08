# -*- coding: utf-8 -*-
"""
I 画风锁 · 推荐引擎（题材 → 候选池）
来源：审计工作区原型 f_lock_recommend.py，逻辑未改，仅改在案口径。
核心：含打斗时硬排除「不适合打戏」的风格，并把能力标签写进候选卡。
知识库：references/style-bible/（74 组候选源 / 适配矩阵 / 锁规程）。
用法：python style-lock-recommend.py "<题材串>" [--top=4]（--demo 跑内置示例）
"""
import re

# 风格库：(编号, 名称, 打斗★, 特效★, 原生题材, 一句话特征, 易跑偏)
STYLES = [
    (65, "国漫3D仙侠",  3, 3, "国漫3D修仙玄幻", "次世代国漫3D半写实·PBR丝绸金玉·丁达尔云雾·流光剑气", "禁2D粗黑描边/禁廉价塑料反光"),
    (66, "暗黑神话游戏CG",3, 3, "主机游戏CG神话", "虚幻5主机游戏CG·高精PBR战损甲胄·暗黑高光比·丁达尔体积雾", "禁2D卡通平涂/禁轻飘无重力"),
    (71, "国漫3D进阶水墨",3, 3, "3D三渲二水墨",   "国漫3D三渲二水墨·枯笔飞白描边·狂草墨韵刀气·朱砂留白对冲", "禁退化为2D平面剪纸/禁死灰滤镜"),
    (72, "东方神话3D奇幻",3, 3, "东方神话3D电影", "东方神话3D电影感·织金玉石次表面散射·青绿赤金·巨物法相奇观", "禁2D粗黑边/禁阴暗废土风"),
    (9,  "徐克",      3, 3, "武侠/玄幻(实拍)", "高反差硬光·广角低机位仰拍·体积雾·凌厉升格", "塑料三渲二/游戏CG打光"),
    (6,  "乌尔善",    3, 3, "神话史诗(实拍)",   "岩画兽纹·巨大体量对比·土红骨白·篝火暖光", "西方奇幻铠甲/廉价土黄"),
    (64, "MAPPA",    3, 3, "2D都市动画厚涂",   "厚涂质感·高对比阴影·动态变形帧", "日式赛璐璐/表情崩坏"),
    (37, "维伦纽瓦",  2, 3, "科幻史诗",   "单色主导·巨物压迫·尘雾弥漫", "色调过灰/节奏拖沓"),
    (47, "卡梅隆",    2, 3, "技术奇观",   "巨物·冷蓝·高动态范围", "重技术轻动作"),
    (28, "押井守",    2, 3, "赛博科幻",   "冷青·玻璃幕墙反射·长焦静止构图", "过于静止/不像打斗"),
    (68, "押井守动画向",2,3, "赛博动画",   "冷调·玻璃幕墙·手绘人物+3D背景", "混合质感不统一"),
    (29, "大友克洋",  2, 3, "机甲科幻",   "冷金属机械·微距·硬表面反射", "机械过密/人物被吞"),
    (12, "袁和平",    3, 2, "武侠动作",   "兵器形制特写·皮甲质感·真实重心发力", "招式堆砌/无镜头语言"),
    (7,  "路阳",      3, 2, "武侠动作",   "长镜头连贯动势·冷调·快刃", "长镜过难/节奏拖"),
    (33, "朴赞郁",    3, 2, "惊悚暴力",   "中轴对称·高对比·冷蓝深红", "造作/仪式感过重"),
    (38, "塔伦蒂诺",  3, 1, "犯罪暴力",   "极低机位仰拍·复古类型色·章节感", "时代错位/特效单薄"),
    (44, "昆汀",      3, 1, "犯罪暴力",   "低机位仰拍·章节字幕·九十年代质感", "同上"),
    (22, "黑泽明",    3, 1, "时代剧",     "自然硬光·实景搭景·多机位群像", "无特效传统/需另补"),
    (39, "大卫·芬奇", 2, 2, "悬疑犯罪",   "冷绿低照度·硬边光·秩序构图", "过冷过暗/打斗看不清"),
    (48, "温子仁",    2, 2, "恐怖惊悚",   "极低照度·幽闭·冷绿·局部强光", "太暗/动作丢失"),
    (36, "诺兰",      2, 2, "科幻动作",   "巨物尺度·冷蓝高对比·中轴对称", "动作偏重/节奏慢"),
    (62, "吉卜力",    2, 2, "奇幻日常",   "手绘水彩背景·柔和日光·云与风写实", "偏飞行自然/非硬核打斗"),
    (42, "库布里克 ⚠️C",3,2, "哲学惊悚",   "绝对对称·冷暖极端分离·固定长镜", "**AI 难撑，须降级为固定对称**"),
    # ---- 不适合打戏（打斗 ★0~★1）----
    (10, "王家卫",    0, 0, "都市情感",   "抽帧残影·霓虹暖黄交错·狭窄空间贴身手持", "**参数组禁粒子禁高帧率，打戏禁用**"),
    (8,  "毕赣",      0, 0, "文艺诗电影", "潮湿雾气·隧道霓虹·长焦压缩", "**时间失速，无动作语法**"),
    (18, "侯孝贤",    0, 0, "文艺写实",   "固定远景长镜·真实环境光", "**打斗会被看淡**"),
    (20, "蔡明亮",    0, 0, "文艺写实",   "极低机位手持·潮湿暗调·慢节奏", "**与打斗节奏对立**"),
    (43, "马利克",    0, 1, "抒情",       "自然光·极低机位·慢镜长焦静观", "**无动作**"),
    # ★2026-10-15 补：路由表引用但 STYLES 缺失的 4 张（原「路由引用却查无此卡」→ 静默漏推）。
    #   星级以 scripts/style-lock-ladder.py（唯一权威）为准，描述取 director-style-catalog-74.md。
    (15, "李少红",    0, 1, "古典唯美",   "柔焦·浓艳绸缎·对称帘幕·烛光暖影", "过甜/缺质感"),
    (17, "李安",      0, 1, "克制写实",   "自然侧光·中景为主·低饱和·留白", "节奏过缓/缺视觉冲击"),
    (21, "王童",      1, 1, "视觉华丽",   "民间装饰纹样·浓饱和·图画性构图", "画面拥挤/缺纵深"),
    (35, "金炯柱",    0, 1, "时尚视觉",   "高饱和撞色·装饰性构成·时尚造型感", "过时尚/脱离题材"),
    (49, "塔可夫斯基 ⚠️C",0,1,"诗电影",   "自然光·水与雾·极长镜", "**AI 亦难撑**"),
    (23, "北野武 ⚠️C", 1, 0, "极简暴力",  "极简固定镜·大段空镜·骤停画格", "**打斗会被剪成静止**"),
    (25, "是枝裕和",  0, 0, "家庭日常",   "家庭实景·窗侧自然光·中近景", "**无动作**"),
    (26, "河濑直美",  0, 0, "抒情",       "逆光柔焦·淡曝光·浅景深", "**无动作**"),
    (27, "岩井俊二",  0, 0, "青春回忆",   "逆光光晕·柔焦·胶片青绿", "**无动作**"),
    (34, "李沧东",    0, 0, "社会写实",   "粗粝手持·真实自然光·灰土调", "**非动作向**"),
    (40, "韦斯·安德森",0,0, "喜剧美学",   "正面中轴·粉彩低饱和·舞台式布景", "**打斗变摆拍**"),
    (45, "索德伯格",  1, 0, "街拍犯罪",   "冷调自然光·轻手持·街拍感", "动作松散"),
    (46, "雷德利",    1, 2, "古典史诗",   "古典油画感·暖金烛光·数字绘景", "打斗偏阵仗"),
    (51, "吕贝·贝松", 1, 1, "童年视角",   "儿童低机位·暖自然光·静谧", "不适合打斗"),
    (55, "维托里奥·斯托拉罗",1,2, "象征用光",   "象征性用光·色彩叙事·强反差光影·明暗块面", "构图优先于动作"),
    (61, "斯文·尼奎斯特", 0, 0, "极简长镜",   "自然光·柔和低反差·中远景·静止长拍", "**无动作**"),
]

# 打斗信号词
COMBAT_SIG = ["打斗","打戏","战斗","对决","开打","武打","搏杀","厮杀","对招","交手","格斗","斗法","大战"]
# 高特效信号
VFX_HIGH_SIG = ["法术","斗法","玄幻","仙侠","修真","神通","法阵","大招","神魔","仙术","异能","风暴","领域"]
# 无特效题材
VFX_LOW_SIG = ["写实","格斗","军警","警匪","追车","暗杀","械斗","都市现实"]

# ★否定语境：命中即把该词从打斗信号里剔除（"无打斗""不打斗""没有打斗""非打斗"…）
NEG_PREFIX = ["无", "不", "没有", "没", "非", "零", "免", "去"]
_NEG_WINDOW_RE = re.compile(
    r"(?:毫无|没有任何|没有|不含|无任何|全无|无|没|不|非|零|免|去)[^，。；、！？\s]{0,4}$")
# 题材关键词（优先于信号词判定"有没有打斗"）
GENRE_COMBAT  = ["玄幻", "仙侠", "修真", "武侠", "武打", "格斗", "动作", "战斗", "打斗", "打戏",
                 "械斗", "暗杀", "枪战", "追车", "战争", "搏杀", "厮杀"]
GENRE_NOCOMBAT = ["都市情感", "情感", "文艺", "静思", "家庭", "日常", "青春", "怀旧", "年代",
                  "甜宠", "职场", "商战", "悬疑文戏", "心理", "生活流", "散文",
                  "文戏", "纯对话", "剧情向"]   # ★P8 补：分镜稿最常用的「无打斗」自述词

# ★题材路由表：题材族 → (首选编号, 次选编号, ...)  顺序即推荐优先级
GENRE_ROUTES = [
    (["国漫3D", "3D国漫", "修仙", "仙侠", "玄幻", "修真", "斗法", "法术"], [65, 71, 66, 72, 9, 6]),
    (["游戏CG", "主机CG", "黑神话", "暗黑神话", "神魔"],         [66, 72, 65, 6]),
    (["水墨", "三渲二", "国风武侠", "进阶水墨"],                 [71, 65, 72, 7]),
    (["武侠", "武打", "械斗", "江湖", "刀剑", "剑客"],           [12, 7, 71, 9, 22]),
    (["机甲", "赛博", "科幻战斗"],                              [29, 68, 28, 47]),
    (["异能", "超能力", "都市战斗"],                            [64, 28, 39, 36]),
    (["悬疑", "犯罪", "暗杀", "警匪", "追车"],                  [39, 48, 33, 45]),
    (["战争", "史诗", "战争场面"],                              [46, 36, 6, 22]),
    (["恐怖", "惊悚", "灵异"],                                  [48, 33, 39, 36]),
    (["都市情感", "情感", "都市", "职场", "甜宠", "爱情"],       [10, 25, 35, 26]),
    (["怀旧", "年代", "复古", "回忆"],                          [10, 15, 21, 17]),
    (["文艺", "静思", "诗", "散文", "家庭", "日常"],            [49, 18, 8, 25]),
    (["青春", "校园", "成长"],                                  [27, 25, 26, 18]),
    (["喜剧", "荒诞"],                                          [40, 44, 34, 61]),
]


def route_genre(genre_text):
    """按题材关键词命中路由表；返回 (首选编号列表, 命中的题材族名) 或 (None, None)"""
    best = None
    for keys, order in GENRE_ROUTES:
        hit = [k for k in keys if k in genre_text]
        if hit and (best is None or len(hit) > best[0]):
            best = (len(hit), order, hit)
    if best:
        return best[1], best[2][0]
    return None, None


def _negated_at(t, start):
    """★P8：前置窗口否定判定。旧版只认紧贴的「无打斗/没有打斗」，
    「没有**任何**打斗」「不含一点打斗」这类隔字否定仍被判成**有打斗**
    ——实测甜宠文戏稿被塞了一张仙侠打斗卡。"""
    return bool(_NEG_WINDOW_RE.search(t[max(0, start - 8):start]))


def _live_hits(t, words):
    out = []
    for w in words:
        for m in re.finditer(re.escape(w), t):
            if not _negated_at(t, m.start()):
                out.append(w)
                break
    return out


def detect_combat(genre_text):
    """
    判定是否含打斗 —— 三步，顺序不可换：
      ① 否定式命中（"无打斗/不打斗/没有打斗/没有任何打斗/非打斗"）→ 直接 False，最高优先级
      ② 题材关键词：命中 GENRE_NOCOMBAT 且未命中 GENRE_COMBAT → False
      ③ 打斗信号词：剔除否定语境后再判
    返回 (combat:bool, 判定依据:str)
    """
    # ① 否定式（关键词前 8 字内出现否定词即视为已否定）
    live = _live_hits(genre_text, COMBAT_SIG)
    hit_c = _live_hits(genre_text, GENRE_COMBAT)
    if not live and not hit_c:
        _raw = [w for w in COMBAT_SIG if w in genre_text]
        if _raw:
            return False, f"否定式（「{_raw[0]}」前有否定词）"

    # ② 题材关键词
    hit_n = [w for w in GENRE_NOCOMBAT if w in genre_text]
    if hit_n and not hit_c:
        return False, f"题材词「{hit_n[0]}」非动作向"

    # ③ 信号词
    if hit_c:
        return True, f"题材词「{hit_c[0]}」"
    if live:
        return True, f"信号词「{live[0]}」"
    return False, "无打斗信号"


def recommend(genre_text):
    combat, why = detect_combat(genre_text)
    vfx_high = any(w in genre_text for w in VFX_HIGH_SIG)
    vfx_low = any(w in genre_text for w in VFX_LOW_SIG)

    excluded = []
    pool = []
    for s in STYLES:
        num, name, fight, fx, native, look, warn = s
        if combat:
            if fight <= 1:
                excluded.append((num, name, "打斗适配 ★%d，不适合打戏" % fight))
                continue
            if vfx_high and fx < 2:
                excluded.append((num, name, "特效承载 ★%d，撑不住高特效打斗" % fx))
                continue
        pool.append(s)

    pool.sort(key=lambda s: (s[2] + s[3]), reverse=True)

    # ★按题材路由重排候选池（题材匹配优先，能力总分只做同族内的次序）
    order, route_key = route_genre(genre_text)
    if order:
        num2s = {s[0]: s for s in pool}
        routed = [num2s[n] for n in order if n in num2s]
        routed_ids = {s[0] for s in routed}
        pool = routed + [s for s in pool if s[0] not in routed_ids]
    return combat, why, vfx_high, pool, excluded, route_key


def render(genre_text, top=4):
    combat, why, vfx_high, pool, excluded, route_key = recommend(genre_text)
    print("=" * 76)
    print(f"题材输入：{genre_text}")
    print(f"含打斗={combat}（依据：{why}）  高特效={vfx_high}   "
          f"题材族={route_key or '未命中'}   候选池 {len(pool)} 组 · 已排除 {len(excluded)} 组")
    print("=" * 76)
    print("\n【候选卡】")
    for i, (num, name, fight, fx, native, look, warn) in enumerate(pool[:top]):
        tag = "【默认推荐】" if i == 0 else ""
        fs = "★" * fight if fight else "—"
        xs = "★" * fx if fx else "—"
        print(f"\n{'ABCD'[i] if i < 4 else i+1} {tag}{name}向 · {native}        打斗 {fs} 特效 {xs}")
        print(f"   看：{look}")
        print(f"   易跑偏：{warn}")
    print(f"\nD 自定义 → 你直接描述，我按你的描述建 STYLE_BIBLE")
    if excluded:
        names = " · ".join(f"{n}" for _, n, _ in excluded[:20])
        print(f"\n[本次已自动排除 {len(excluded)} 组不适合该题材的风格：{names}]")
        print(" [如需其中某个风格拍打戏，请明示——系统会给出降级方案与风险提示]")


if __name__ == "__main__":
    # ★P8（2026-10-24 · 采纳网友建议书 P-01）：旧版 __main__ 只循环 5 组硬编码示例，
    #   **全程不读 sys.argv** → 「题材→候选池路由引擎」实际是演示脚本：任何输入都得到
    #   同一套输出（拍甜宠也会拿到仙侠打斗卡）。现改为位置参数接题材，--demo 跑原示例。
    import sys

    demo_cases = ["15秒玄幻仙侠打斗对决，有法术特效",
                  "都市情感夜戏，无打斗",
                  "年代怀旧文戏，两个人回忆往事",
                  "现代都市悬疑，追车加近身格斗",
                  "都市异能战斗，赛博科幻城市场景"]

    argv = sys.argv[1:]
    # ★P9：`--self-test` 作为 `--demo` 的正式别名（包内惯例统一，见 check_package ◑25）
    _selftest = "--self-test" in argv
    if not argv or "--demo" in argv or _selftest:
        print("【演示模式】以下为内置示例，非本机输入\n")
        for g in demo_cases:
            render(g)
            print("\n")
        if _selftest:
            print(f"[+] style-lock-recommend self-test PASSED（{len(demo_cases)} 组内置示例全部出卡未崩）")
        sys.exit(0)

    text_parts, top = [], 4
    for a in argv:
        if a.startswith("--top="):
            try:
                top = max(1, int(a.split("=", 1)[1]))
            except ValueError:
                pass
        elif not a.startswith("--"):
            text_parts.append(a)
    text = " ".join(text_parts).strip()
    if not text:
        print('用法：python style-lock-recommend.py "<题材串>" [--top=4]')
        print("      python style-lock-recommend.py --demo        # 跑内置示例（--self-test 等价）")
        sys.exit(2)
    render(text, top=top)
    print("\n※ 本卡是「题材→候选池」建议；**影像基底须先由用户确认**（形态必问，"
          "见 style-lock-protocol.md §三 · 2026-10-13 裁定），"
          "基底未定时请勿据此出卡。")