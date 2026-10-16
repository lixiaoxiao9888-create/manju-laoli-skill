#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Package Integrity Check —— 包级完整性 / 回归自检（打包与出厂时跑）

现行版本以本文件 `VERSION` 常量为准——**不在 docstring 里写死版本号**
（2026-10-14 代码体检修复：原写死上一版版本号，升版后与正文漂移；且 `.py` 的 docstring
不在 `scan_rule_docs()` 的 `.md` 扫描域内，`[A]`/`◑8` 均未报警 → 逃逸三处版本残留之一）

设计原则（本版重写要点）
----------------------
① **扫描范围 = 全包**（总控 + 12 个子技能）。原实现只 os.walk() 总控目录，
   子技能目录的 Markdown 完全不参与内容规则检查 —— 这是「静默假通过」的根因。
② **版本断言是真断言**（`frontmatter version == VERSION` 常量比较）。原实现的版本一致性检查写成
   "历史文本里是否出现过某个旧串"，因历史记录必然含有旧串而恒真。
③ **输出按域分项**，任何一项 FAIL 即以退出码 1 结束。

检查域
------
[A] 版本一致性   根 SKILL / README / 12 子技能 / CHANGELOG 均为 7.4.20；CURRENT 文档无旧版本串
[B] 结构完整性   总控 references == 47；子技能 == 12；被引用的规则文件真实存在
[C] 内容规则门   可灵 / 三视图 / 格式别名 / 2.0 首尾帧 / 规则自洽门（全包范围）
[D] 机检脚本     全部脚本可编译；validate_prompt.py self-test PASS；关键门在案
[E] 套装路由     四层纵深 / 赛道锁 / 素材来源锁 / 权威归属表 / 强制读取清单 / 12 子技能挂线
               + 四项融合域完整性：㉒ 场面调度权威 / ㉓ 故事板图标准 / ㉔ 场景空间事实五件事 / ㉕ 素材形态与接线单
               + 三项新增域完整性：㉖ 解说叙事引擎与③ 赛道转正 / ㉗ 方言配音控制词典外挂 / ㉘ 打斗规程吸收
               + 跨文件一致性：㉙ 赛道③ C14n 豁免——引擎声明 ↔ 机检实现 ↔ 手册登记 三处互锁
[E+++] 接线修复域：㉚ 三份出图模板完整性（九宫格 / 立绘 / 道具——删掉或字段删空即 FAIL）
               + ㉛ 机检 C 码一致性：validate_prompt.py 实现的 C 系码 ⊆ 机检手册登记的 C 系码（防「脚本有、手册无」）
[E++++] 打戏护栏域：㉜ 两份打戏新库完整性（激烈度硬护栏 / 特效手绘化）
               + C21 三处互锁：三引擎声明 ↔ validate_prompt.py 实现 ↔ 机检手册登记
[E++++] 节奏负载域：㉝ 节奏与渲染负载护栏库完整性 + C22 四处互锁
               + ★防回归：铁律26「动作数上限」必须已接入自检闸口
[E*5] 画风锁域：㉞ style-bible 8 份 + 成稿示例 2 份 + 引擎脚本 2 份完整性
               + C23 三处互锁：validate_prompt.py 实现 ↔ 机检手册登记 ↔ 总控触发门口径
               + 接线防回归：feed 契约 9 / asset 锁系统 I 锁 / 编号裁定（F 锁 = I 锁）在案
[E*6] 禁项单点域：㉟ C24a/b 实现 ↔ 机检手册登记 ↔ C7 前置等价联动 + 自测五组用例在案
[G] 素材形态       M0/M1/M2 权威完整性 / 门禁改判表 / 接线单 / 文字锁 / 三不一要 / 闸门 6B 机检
[F] 外部版本保全 V3.9.0 / V2.6.0 / V5.0.2 / v13.0 未被版本统一误伤
[E*9] 字数口径域：㊲ C4 篇级 4500「单文件」口径 ↔ 闸门3 段级 1900/2000 粒度声明（防单值漂移）
[E*10] 外部增量与病句修复域：㊳ 版本清洗残句清零 / 照明两节 / 高光 8 套 / OTS 拓扑 / C17b
[E*13] 融合规则补载体域（2026-10-10）：㊷ 六个新子码五处互锁
       （规则源文件 ↔ validate_prompt.py ↔ 机检手册 ↔ 子码计数 ↔ 自检用例）
[E*16] 图形化产物与段缝景别承接域（2026-10-11 用户实测反馈）：
       ㊺ 故事板图版式/交付清单/四宫格消歧 ↔ ㊻ C18m 段缝景别落差八互锁（含 C7c 元检查）
[E*23] 前置锁完整性域（2026-10-13 · D 锁缺位修复）：
       ㊼ 「多段任务」判定式 + 判定时点（P0 立项期）+ 六道锁同批锁完 三处互锁（防「自称非多段任务」跳过 D 锁）
       （治「四宫格故事板没出」与「末镜拉全景后下段切中景」两条实跑反馈）
[E*24] 剧本引擎阶段② 更名域（2026-10-13 用户要求「不是动漫IP」）：
       ㊿ 阶段②名「动漫IP开发」→「IP 与角色开发」生效位四处一致 + 旧名清零 + 形态无关声明在案
       （治「真人项目被阶段名误判为动漫项目」）
[E*25] 前置锁默认口子清零域（2026-10-13 用户裁定「这个还是没有给我选」）：
       ◆ C 锁「未指定默认 ③」与 I 锁「按默认推荐卡走」两个口子清零 + 新口径三处同源 + 形态基底改必确认
       （圈码 ㉑~㊿ 已被前序 24 个域占满，本域改用 ◆1~◆4 编号，避免与既有域混淆）
       （治「锁写了默认值、执行者就不弹卡，用户根本没得选」）
[E*26] 道具资产锚点域（2026-10-13 用户发现「提示词里没有道具的 @ 位」）：
       ◇ 关键道具锚点 @PRP- 落位【场景资产】栏（与 @SCN- 并列 · 七段式不增段）+ 旧「@人名/@场景名」两类写法清零
         + 三族锚点同源（asset-spatial-ledger / h3-adapter）+ 投喂引擎与故事板层同步
       （◆1~◆4 已被 [E*25] 占用，本域改用 ◇1~◇3 编号，与 ◆ 组区分）
       （治「人物/场景/站位都有 @ 锚点，唯独道具没有，只能写镜行括号夹注「（图9）」」）
[E*27] 特写占比与分镜字段完整性域（2026-10-13 项目体检修复）：
       ◈ 特写占比口径写死（人物特写含人体局部肢体 / 物件特写不计入 / 判定基准在案）
         + 补机检 C18n（含 4 条自检用例）+ 故事板引擎增设「逐镜九字段完整性」硬自检
       （◇1~◇3 已被 [E*26] 占用，本域改用 ◈1~◈3 编号）
       （治「硬指标只写不检」与「分镜稿漏栏无兜底」：72 镜人物特写 19.4% 低于下限而机检零告警）
[E*28] 粉丝系统性意见全修域（2026-10-13 · 剧本 5 条 + 分镜 3 条 · 全修裁定）：
       ◉ 外部剧本润色层（P0-1 新增 references）+ R1 速查冲突修复（P0-2）
         + 公式去重升级全剧配额（P1-1）+ 分镜形态适配与特写×平视组合禁令（P1-2）
         + 反派能力基线与受挫配额（P2-1）+ 悬念存量配额（P2-2）
         + FACS 形态强制与「叙事/动作/表情」三要素（P3）
       （◈1~◈3 已被 [E*27] 占用，本域改用 ◉1~◉4 编号）
       （治「包自己教出粉丝抱怨的结果」：R1 速查写「不追求人物深度」架空整套成长地图）
[E*29] 台词拟人化域（2026-10-13 · 用户实测「台词对白机械化／不够拟人／缺称呼」）：
       ◐ 新建台词拟人化引擎 dialogue-naturalization.md（含《台词拟人化过站》）
         + 消声音卡三口径分裂（§1.8 YAML 补 address_system / avg_line_length / signature_particles）
         + 表演层坏表演图鉴 8「台词太干净」改指针 + 下游探测器 C28a~c（只报不改）
         + P1 必读清单补台词七维诊断（消「孤儿权威」）
       （◉1~◉4 已被 [E*28] 占用，本域改用 ◐1~◐8 编号）
       （根因：规则在包里却全失效——唯一口语化规则被划归表演层、剧本层读不到 / 七维只诊断不治病
         且要手动触发 / 规则全是否定式、正向供给为零（「拟人」「机械化」「腔调」全包 0 命中）/
         声音卡同概念三个版本互不覆盖 / 下游铁律「台词逐字保留」致上游写错后全链路无人能救）
[E*30] 规则文件挂载一致性域（2026-10-13 · 元层面反思 · 治「★权威 ≠ 会被读到」）：
       ◑ 包内三套重要性清单（唯一权威归属表 / 文件树★ / **八阶段必读清单**）**互无断言** →
         文件可写进表、标上★、画进文件树，却不在必读清单里 —— 照样「是权威」，只是永远没人读。
       修复：总控新增《按需规则文件 · 触发条件台账》（**39 份非必读规则文件全部登记触发条件**）
         + 表演层 `acting-direction.md` 接进 P3 必读（修复前它自声明「P1 写《角色表演档案》」却无读取路径）
[E*31] 资产状态偏离域（2026-10-13 · 用户实测「资产图戴头盔 + 提示词夹头盔 = 两个头盔」）：
       ◒ `CHAR_STATE` 人物持续状态变体（与场景 `SET_STATE` 对称）+ 立绘配饰口径改「默认锁定·可变需声明」
         + 投喂层「资产偏离声明」三件套（`model-adapters.md` §5.0.6）+ 机检 `C29`
       （根因：`SET_STATE` 只管场景 / 换装只解决跨造型 / 穿戴物被写成「固定不可变更」
         → **无优先级声明 → 模型【叠加】而非【替换】**）
[E*35] Agent 系统性修复域（2026-10-15 · 治「大模型修复留下的修A漏B」）：
       ◔ ① **小数秒口径 `MM:SS.s`**：`build_board_lite.to_seconds` 的 `int(s)` 曾把 `00:10.5` 抛 ValueError
         并**静默丢镜**（实测《盐枭劫》稿 17 镜只出 10 镜 = 丢 41%；看板与 SRT/CSV/JSON 三导出时间轴出现 7 秒空洞、
         CLI 零告警）；同一病因的 `fr / 100.0` 把 `.5` 算成 0.05s，脚本内共 **5 处副本**
         → 三脚本统一「按小数位数换算」+ 丢镜安全网（对账「原文带时码行数 vs 已解析镜数」）+ 四处 self-test 回归锁
       ◔ ② **C30c/C30d 触发门**：原只认显式 `--plugin real|xuanhuan|combat`，默认 `auto` 下整组静默不跑，
         与总控 SKILL.md 把回执头/声线锁写成硬规形成空档 → `auto` 判出 R1/R3 打戏档时一并核验
       ◔ ③ **子码计数唯一口径**：手册新增 `SUBCODE-Registry` 机器可读块（现行 **98 条**）为唯一权威；
         ㊾ 由「查『自称 68 条』字符串在不在」改为**真校验**（条数自洽 + 脚本/注册清单/手册三方集合双向相等）；
         ㉛ 新增「总控 SKILL 子码清单完整覆盖注册块（含 `C18a~n` 类范围展开）」断言，堵住「手册有、总控无」
[E*36] 画风锁三方对账域（2026-10-15 Agent 修复 · 治「加卡顶掉老卡 / 漏族 / 数字漂移」）：
       ◔ 病灶：`n` 版补 4 张国漫3D卡时**顶掉了原有 4 张卡**（皮克斯/迪士尼经典/皮埃尔·孔切·平面插画/
         Nelagraphs·长条漫画风），T8 家族缩编致 宫崎骏/京阿尼 掉队，参数库章节号重复、「其余 N 组」算错——
         **全程零断言覆盖**。本域把 12 项全部变成真断言：
         选卡表卡数自洽（◔1）/ 编号唯一（◔2）/ 停用号位声明（◔3）/ 补回卡在位（◔4）/ 移除卡不在选项卡内（◔5）/
         **引擎 STYLES ↔ 文档 T 族表双向一致（成员+家族+星级 · ◔6）** / 引擎已摘除移除卡（◔7）/
         参数库章节号唯一（◔8）/ 补录算式自洽（◔9）/ 全包无旧口径残留（◔10）/ 红线 2 交叉引用在案（◔11）/
         题材矩阵两表声明数 == 实际行数（◔12）
"""
import os
import re
import sys
import py_compile
import subprocess

VERSION = "7.4.20"
EXPECTED_REFS = 48   # 递归计数（38 份顶层规则库 + style-bible 10 份）。⚠️ 注意：SKILL.md 对外统一声明「48 份规则库」（递归口径），**不得写成 38 份**——2026-10-14 修复了此处 38/48 双值悬挂。
SUB_SKILLS = [
    "sd-decision-engine", "sd-recon-engine", "sd-script-engine", "sd-overseas-engine",
    "sd-jieshuo-engine",
    "sd-asset-engine", "sd-storyboard-engine", "sd-combat-engine", "sd-xuanhuan-engine",
    "sd-real-engine", "sd-feed-engine", "sd-qc-engine",
]
# 本包历史版本串（仅允许出现在 CHANGELOG 与 LEGACY/沿革说明行）
# 注：**V7.3.9 起，正文不再保留任何历史版本标注**——此前「V7.3.x 新增·续·修订」类在案溯源标注已全部清除，
#     沿革统一收敛至 CHANGELOG.md。故 7.3 / 7.4 系列（除当前版 VERSION）纳入 OLD_VER_RE 约束。
# ⚠️ 元规则四（断言只锁常量）：排除项由 VERSION 常量派生，**不得写死字面版本号**。
#     实测事故 2026-10-14：升版 7.4.19 时排除项仍写 (?!4\.18) → 新版号被当旧版号误杀 6 处。
#     二次事故（同日）：把前瞻塞在 `7\.` 之后 → 前缀已消费 `7.`，前瞻比对 `4.19` 永久失败。
#     ✅ 正确写法：负向前瞻必须锚在**整个版本号之前**，即在 `V` 后立刻排除当前版全串。
_CUR_ESC = re.escape(VERSION)                    # e.g. 7\.4\.19
OLD_VER_RE = re.compile(
    r"V(?!%s(?!\d))(?:6\.[5-9]|7\.\d+(?:\.\d+)*|8\.\d)(?:\.\d+)*" % _CUR_ESC
)
# 沿革/域命名豁免词：版本串可出现在 LEGACY/沿革/域命名说明行（`.md` 与 `scripts/*.py` 同一口径）。
# ⚠️ 元规则：**豁免词不得让整行放过「规格区」**——表格行不适用（见 ◑9）。
#    「域命名沿革」类标识（如 `section("[E+] V7.3.0 三项融合域")`）是互锁域的**结构性锚点**，
#    删除会破坏引用与可读性，故单列一类显式标注（2026-10-14 补：此前 scripts/*.py 完全不在扫描域内）。
VER_ALLOW_RE = re.compile(r"LEGACY|历史|沿革|代号|废止|不再|不得|旧口径|旧编号|CHANGELOG")
# 外部产品版本（不得被版本统一改写）
EXTERNAL_VERS = ("V3.9.0", "V2.6.0", "V5.0.2", "v13.0")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 总控目录
PKG = os.path.dirname(BASE)                                          # 包根（含总控与 sd-*）
CHANGELOG = os.path.join(BASE, "CHANGELOG.md")

FAILED = []
SECTION = {"cur": None}


def section(name):
    SECTION["cur"] = name
    print()
    print("=" * 62)
    print(name)
    print("=" * 62)


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(f"{SECTION['cur']} / {name}")


def read(path):
    """缺文件返回空串（有韧性）：让"文件不存在"表现为该项 FAIL，而不是整脚本 traceback 崩掉。
    新文件的"存在性"由各自的 os.path.exists() 断言独立覆盖，不会被空串掩盖。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, NotADirectoryError, IsADirectoryError):
        return ""


def rel(p):
    return os.path.relpath(p, PKG)


def scan_md_files():
    """全包扫描（含 12 子技能）—— 原实现只扫总控，是假通过根因。"""
    out = []
    for root, _dirs, files in os.walk(PKG):
        for fn in files:
            if fn.endswith(".md"):
                out.append(os.path.join(root, fn))
    return sorted(out)


def scan_rule_docs():
    """参与内容规则门的文档：全包 Markdown，排除历史沿革文件。"""
    return [p for p in scan_md_files() if os.path.abspath(p) != os.path.abspath(CHANGELOG)]


def sub_skill_path(name):
    for p in (os.path.join(PKG, name), os.path.join(BASE, "skills", name)):
        if os.path.isdir(p):
            return p
    return None


def frontmatter_version(text):
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return None
    m2 = re.search(r'^version:\s*"?([^"\n]+?)"?\s*$', m.group(1), re.M)
    return m2.group(1).strip() if m2 else None


# ---------------------------------------------------------------- [A] 版本一致性
section(f"[A] 版本一致性（唯一现行版本 = {VERSION}）")

skill = read(os.path.join(BASE, "SKILL.md"))
readme = read(os.path.join(BASE, "README.md"))
changelog = read(CHANGELOG)

check(f"根 SKILL.md frontmatter version == {VERSION}",
      frontmatter_version(skill) == VERSION, f"实际 {frontmatter_version(skill)}")
check("根 SKILL.md 声明「现行唯一版本口径」", "现行唯一版本口径" in skill)
check(f"README.md 版本行 = {VERSION}",
      re.search(r"\*\*版本\*\*：V" + re.escape(VERSION), readme) is not None)
check("README.md 声明「现行唯一版本口径」", "现行唯一版本口径" in readme)
check(f"CHANGELOG.md 含 {VERSION} 条目",
      f"## V{VERSION} " in changelog or f"· V{VERSION}：" in changelog or f"V{VERSION} ·" in changelog)
check("CHANGELOG.md 声明「版本编号说明」与当前口径",
      "版本编号说明" in changelog and "不代表当前版本高低" in changelog)

_bad_sub_ver = []
for name in SUB_SKILLS:
    p = sub_skill_path(name)
    if not p:
        continue
    sp = os.path.join(p, "SKILL.md")
    if not os.path.exists(sp):
        _bad_sub_ver.append(f"{name}(缺 SKILL.md)")
        continue
    v = frontmatter_version(read(sp))
    if v != VERSION:
        _bad_sub_ver.append(f"{name}={v}")
check(f"12 子技能 frontmatter version 均为 {VERSION}", not _bad_sub_ver, "; ".join(_bad_sub_ver))

_bad_old = []
for p in scan_rule_docs():
    for i, line in enumerate(read(p).splitlines(), 1):
        if OLD_VER_RE.search(line) and not VER_ALLOW_RE.search(line):
            _bad_old.append(f"{rel(p)}:{i}")
check("CURRENT 文档无旧版本串（仅 LEGACY/沿革/代号行可提及）",
      not _bad_old, "; ".join(_bad_old[:6]))

# ---------------------------------------------------------------- [B] 结构完整性
section("[B] 结构完整性")

refs_dir = os.path.join(BASE, "references")
# 递归计数（含 style-bible/ 子目录知识库），与 SKILL.md/README 的「48 份规则库」口径一致
refs = [os.path.relpath(os.path.join(dp, f), refs_dir).replace("\\", "/")
        for dp, _dn, fn in os.walk(refs_dir) for f in fn if f.endswith(".md")]
check(f"总控 references 规则库 == {EXPECTED_REFS} 份（含 style-bible）",
      len(refs) == EXPECTED_REFS, f"实际 {len(refs)} 份")

_missing_skill = [n for n in SUB_SKILLS if sub_skill_path(n) is None]
check("12 子技能目录全部存在", not _missing_skill, "缺: " + ", ".join(_missing_skill))

_thin_refs = []
for name in SUB_SKILLS:
    p = sub_skill_path(name)
    if not p:
        continue
    rd = os.path.join(p, "references")
    n = len([f for f in os.listdir(rd) if f.endswith(".md")]) if os.path.isdir(rd) else 0
    if n < 3:
        _thin_refs.append(f"{name}({n})")
check("每个子技能 references >= 3 份", not _thin_refs, "; ".join(_thin_refs))

# 被引用的规则文件真实存在（三档解析：同目录相对 → 总控相对 → 包根相对 → 全包同名兜底）
# 注：CHANGELOG 为历史记录，不参与本门（其中的旧路径可能已迁移）
_bad_ref = []
REF_TOKEN = re.compile(r"`((?:references/|scripts/|sd-[a-z\-]+/)[^`<>…*]*?\.(?:md|py))`")
_all_basenames = set()
for _root, _dirs, _files in os.walk(PKG):
    for _fn in _files:
        _all_basenames.add(_fn)
for p in scan_rule_docs():
    here = os.path.dirname(p)
    for tok in REF_TOKEN.findall(read(p)):
        cands = [os.path.join(here, tok), os.path.join(BASE, tok), os.path.join(PKG, tok)]
        if any(os.path.exists(c) for c in cands):
            continue
        if os.path.basename(tok) in _all_basenames:   # 记法省略目录，但文件确实存在
            continue
        _bad_ref.append(f"{rel(p)} → {tok}")
check("被引用的规则/脚本文件真实存在", not _bad_ref, "; ".join(sorted(set(_bad_ref))[:6]))

# ---------------------------------------------------------------- [C] 内容规则门
section("[C] 内容规则门（全包范围，含 12 子技能）")

KLING_OK = re.compile(r"LEGACY|不再|已移除|历史|移除可灵|去可灵")
_bad_kling = []
for p in scan_rule_docs():
    for i, line in enumerate(read(p).splitlines(), 1):
        if "可灵" in line and not KLING_OK.search(line):
            _bad_kling.append(f"{rel(p)}:{i}")
check("① 可灵不作为正式支持模型（仅 LEGACY/移除声明行可提及）", not _bad_kling,
      "; ".join(_bad_kling[:5]))
check("① model-adapters 含可灵 LEGACY 声明",
      "LEGACY·可灵 (Kling)" in read(os.path.join(refs_dir, "model-adapters.md")))

asl = read(os.path.join(refs_dir, "asset-spatial-ledger.md"))
check("② CURRENT 角色提示词标准采用四字段模板",
      all(k in asl for k in ("画幅", "排版结构", "服装与身体材质", "面部特写")))

_ban = [l for l in "\n".join(read(p) for p in scan_rule_docs()).splitlines()
        if re.search(r"八段式|六栏|九栏", l) and not re.search(r"禁|别名", l)]
check("③ 禁用「八段式/六栏/九栏」别名（禁令声明行除外）", not _ban, "; ".join(_ban[:3]))
ma = read(os.path.join(refs_dir, "model-adapters.md"))
check("③ 七段式唯一命名 + 【接续状态】废止口径（model-adapters §5）",
      "「七段式」为唯一命名" in ma and "【接续状态】尾行已于 2026-10-09 废止" in ma)

check("④ spatial-reference-system-V3 带 LEGACY/备查标记",
      "LEGACY" in read(os.path.join(refs_dir, "spatial-reference-system-V3.md")))
check("④ CHANGELOG 带 LEGACY/HISTORY 声明", "LEGACY/HISTORY 声明" in changelog)

NEG = re.compile(r"无首尾帧|禁用|不适用|禁止|不得|排除|2\.0 无|禁投|禁写|残留|出现首尾帧|FAIL")
# ⚠️ 版本号陷阱：包版本串若含 "2.0" 子串，会被本项误判为「Seedance 2.0 语境」。
#    故用负向后顾排除 "7." 前缀，只认真正的模型版本号 2.0。
MODEL_20 = re.compile(r"(?<![\d.])2\.0")
_bad_fl = []
for p in scan_rule_docs():
    for i, line in enumerate(read(p).splitlines(), 1):
        if MODEL_20.search(line) and ("首帧" in line or "尾帧" in line) \
                and not NEG.search(line):
            _bad_fl.append(f"{rel(p)}:{i}")
check("⑦ 2.0 语境无首尾帧（仅否定/禁用表述可提及 · 排除包版本串的子串误判）", not _bad_fl, "; ".join(_bad_fl[:5]))
check("⑦ SKILL 〇节含「首尾帧仅限 2.5」硬约束 + 参考模式二选一默认①",
      "首尾帧仅限 Seedance 2.5" in skill and "全能参考模式（默认推荐）" in skill)

chk_path = os.path.join(refs_dir, "prompt-feeding-checklist.md")
chk = read(chk_path)
check("⑥ 场景拼接图产物已废止（2026-10-11 用户裁定 · 职能并入母版）",
      "拼接图" not in asl)
check("⑥ 旧口径「关键区域细节三联」已清零", "细节三联" not in asl)
check("⑥ 场景双图铁律（母版 → 九宫格 · 按出图顺序）",
      "场景双图" in chk and "场景母版" in chk and "九宫格" in chk)

# ⑰ 规则自洽门：被废止句式只允许出现在警示语境（规则文档自己过自己的禁令）
DEAD_PATTERNS = (
    "首帧即这只手", "指甲盖大的一片暖黄光斑", "火光从侧面照在玉面",
    "举到油灯旁", "面无笑意", "漏雨成线", "映出油灯火苗",
)
WARN_MARKS = ("已废止", "废止", "禁写", "禁入", "禁止", "不得", "一律删", "⚠️", "❌",
              "替代", "规避", "裸禁令", "病根", "无视", "画不出来", "翻车", "已修订")
RULE_DOCS = [
    os.path.join(refs_dir, "model-adapters.md"),
    os.path.join(BASE, "SKILL.md"),
    chk_path,
    os.path.join(refs_dir, "seedance-render-engine.md"),
]
_v17 = []
for doc in RULE_DOCS:
    if not os.path.exists(doc):
        _v17.append(f"缺失 {rel(doc)}")
        continue
    for i, line in enumerate(read(doc).splitlines(), 1):
        for pat in DEAD_PATTERNS:
            if pat in line and not any(m in line for m in WARN_MARKS):
                _v17.append(f"{rel(doc)}:{i}『{pat}』")
check("⑰ 规则自洽门：被废止句式仅存于警示语境（规则不产毒）", not _v17, "; ".join(_v17[:6]))
check("⑰ 示范句验证纪律在案（model-adapters + SKILL 法则 24）",
      "示范句验证纪律" in ma and "示范句验证纪律" in skill and "先验创作" in skill)

# ---------------------------------------------------------------- [D] 机检脚本
section("[D] 机检脚本（编译 / self-test / 关键门在案）")

scripts_dir = os.path.join(BASE, "scripts")
py_files = sorted(f for f in os.listdir(scripts_dir) if f.endswith(".py"))
_compile_fail = []
for fn in py_files:
    try:
        py_compile.compile(os.path.join(scripts_dir, fn), doraise=True)
    except Exception as e:  # noqa: BLE001
        _compile_fail.append(f"{fn}: {e}")
check(f"scripts/ 全部 {len(py_files)} 个脚本可编译", not _compile_fail, "; ".join(_compile_fail[:3]))

vp = os.path.join(scripts_dir, "validate_prompt.py")
check("validate_prompt.py 存在（稿件级出稿门禁）", os.path.exists(vp))
vp_src = read(vp) if os.path.exists(vp) else ""
if os.path.exists(vp):
    try:
        r = subprocess.run([sys.executable, vp, "--self-test"],
                           capture_output=True, text=True, timeout=60)
        check("validate_prompt.py --self-test 通过", r.returncode == 0,
              (r.stdout or r.stderr)[-200:])
    except Exception as e:  # noqa: BLE001
        check("validate_prompt.py --self-test 通过", False, str(e))

for label, needle in [
    ("C8 2.0 禁用首尾帧门", "C8 Seedance 2.0 全面禁用首尾帧"),
    ("C9 平台高危词门", "C9 正文出现平台高危词"),
    ("C13 镜长雷同门", "C13 镜长雷同"),
    ("C14 画外声门", "声画分离红线"),
    ("C15 拉伸凑时门", "拉伸凑"),
    ("C16 对白语气门", "语气错位"),
    ("C17 摆位必入画门", "摆位必入画"),
    ("C18 首镜锚定门", "C18a"),
    ("C19 禁令失效门", "C19a"),
    ("C20 单主体锚定门", "C20a"),
    ("H 系列 H1~H12 门", "H8 七段式栏名泄漏"),
]:
    check(f"validate_prompt 含 {label}", needle in vp_src)

check("SKILL 含法则 17 镜长节奏铁律", "镜长节奏铁律" in skill)
check("SKILL 架构树 / 指令路由挂线 validate_prompt.py", "validate_prompt.py" in skill)
check("checklist 挂线 validate_prompt（出稿门禁）", "validate_prompt" in chk)

# ---------------------------------------------------------------- [E] 套装路由
section("[E] 套装路由与共享契约")

check("SKILL 含套装路由章节与子技能路由表",
      "多技能套装路由" in skill and "子技能路由表" in skill)
check("SKILL 含四层纵深架构说明（L0/L1/L2/L3）",
      all(k in skill for k in ("L0", "L1", "L2", "L3")) and "四层纵深" in skill)
_missing_route = [n for n in SUB_SKILLS if n not in skill]
check("SKILL 挂线全部 12 子技能", not _missing_route, "缺: " + ", ".join(_missing_route))
check("SKILL 含打戏三档分流判定（通用 / R3 玄幻 / R1 写实）",
      "打戏三档分流" in skill and "sd-xuanhuan-engine" in skill and "sd-real-engine" in skill)
check("SKILL 含〇·0 赛道强制分流锁", "〇·0 · 赛道强制分流" in skill)
check("SKILL 含〇·1 素材来源锁 + 正交可组合声明",
      "〇·1 · 素材来源锁定" in skill and "正交可组合" in skill)
check("SKILL 含【强制读取清单】（6 阶段必读表）", "强制读取清单" in skill and "P0·0" in skill)
check("SKILL 含 A 锁三选一（2.5 / 2.0 / MiniMax H3）且 H3 为格式支线",
      "模型版本三选一" in skill and "MiniMax H3" in skill and "格式适配支线" in skill)
check("SKILL 已清除单模型旧句「Seedance 2.5 或 Seedance 2.0」二选一残留",
      "Seedance 2.5** 或 **Seedance 2.0" not in skill)
check("SKILL 含两档运行模式表（严格模式 / 极速模式 · 极速仅软推断〇·0 与〇·1）",
      "严格模式" in skill and "极速模式" in skill and "不推断、不默认" in skill)
check("SKILL 含《规则权威归属表》与冲突裁决顺序",
      "唯一权威归属表" in skill and "冲突裁决顺序" in skill)
check("SKILL 含机检两门制（结构门 C1~C15 / 语义风险门 C16~C20）与分级处置",
      "结构门" in skill and "语义风险门" in skill and "C1~C15" in skill
      and "C16~C20" in skill and "必须清零才交付" in skill
      and "必须由 AI/人工复核后放行" in skill)
check("SKILL 无字面重复段落（「只有一种例外」仅出现 1 次）",
      skill.count("只有一种例外：用户**明确点名**某个子技能") == 1)
check("SKILL 声明规则库份数 == EXPECTED_REFS（元规则四：只锁常量 · 2026-10-14 修 38/48 双值悬挂）",
      f"{EXPECTED_REFS} 份规则库" in skill and "38 份" not in skill)

for name in SUB_SKILLS:
    p = sub_skill_path(name)
    if not p:
        continue
    sp = os.path.join(p, "SKILL.md")
    s = read(sp)
    check(f"子技能 {name} frontmatter 合规（套装前缀 / 版本 / 成员声明）",
          f"V{VERSION} 套装" in s and frontmatter_version(s) == VERSION
          and "short-drama-director" in s)

tr = read(os.path.join(refs_dir, "track-routing.md"))
check("⑳ track-routing 含〇·0 锁与四赛道定义",
      "〇·0" in tr and all(k in tr for k in ("国内剧", "海外剧", "解说类", "其他")))
rce = sub_skill_path("sd-recon-engine")
if rce:
    rce_s = read(os.path.join(rce, "SKILL.md"))
    check("㉑ sd-recon-engine 含采风四步 / 信源三级分级 / 情报卡十三项字段 / 六条证据纪律",
          "采风四步" in rce_s and "T1 一手" in rce_s and "十三项字段" in rce_s
          and "不编造" in rce_s)
    check("㉑ sd-recon-engine 声明轻量版边界（不做打分/门槛/聚簇/台账/定时）",
          "轻量版边界" in rce_s and "不做" in rce_s)
ose = sub_skill_path("sd-overseas-engine")
if ose:
    ose_s = read(os.path.join(ose, "SKILL.md"))
    check("⑳ sd-overseas-engine 含语言与风格合同 + 三级校准状态",
          "语言与风格合同" in ose_s and "region_unvalidated" in ose_s
          and "human_reviewed" in ose_s)
    check("⑳ sd-overseas-engine 声明不替代 sd-script-engine", "不替代" in ose_s)

# ------------------------------------------------- [E+] 三项融合域完整性
section("[E+] V7.3.0 三项融合域（场面调度 / 故事板图 / 场景空间事实）")  # 域命名沿革：V7.3.0 引入，标识保留

# ㉒ 场面调度与站位决策层
bd = read(os.path.join(refs_dir, "blocking-direction.md"))
check("㉒ 场面调度权威文件存在（references/blocking-direction.md）",
      os.path.exists(os.path.join(refs_dir, "blocking-direction.md")))
check("㉒ blocking-direction 含文字平面图 / 权力几何 / 节拍闭环五段 / 对话调度链",
      "文字平面图" in bd and "权力几何" in bd
      and all(k in bd for k in ("起势", "路径", "落点", "接收者反应"))
      and "说话者" in bd and "反应者" in bd)
check("㉒ blocking-direction 含关键道具账（持有 / 手位 / 落点 / 状态）",
      "持有" in bd and "手位" in bd and "落点" in bd)
check("㉒ blocking-direction 声明不重复定义镜头策略四模式（权威仍归 editing-transition-gate）",
      "不重复定义" in bd and "editing-transition-gate" in bd)
check("㉒ 禁图口径已收窄：导演稿允许文字平面图 + 投喂词仍禁任何图",
      "投喂词" in bd and ("图画在导演稿里" in bd or "图在导演稿里" in bd)
      and "投喂词" in read(os.path.join(refs_dir, "model-adapters.md"))
      and "blocking-direction.md" in read(os.path.join(refs_dir, "model-adapters.md")))
check("㉒ SKILL 挂线场面调度（权威归属表 + 强制读取清单 + 路由表）",
      "blocking-direction.md" in skill and "场面调度" in skill)

# ㉓ 故事板图（面板链）
sbe = sub_skill_path("sd-storyboard-engine")
sbs = read(os.path.join(sbe, "references", "storyboard-sheet-template.md")) if sbe else ""
check("㉓ 故事板图标准文件存在（sd-storyboard-engine/references/storyboard-sheet-template.md）",
      bool(sbe) and os.path.exists(os.path.join(sbe, "references", "storyboard-sheet-template.md")))
check("㉓ 故事板图含七态动作相位（起始/过程/接触/顶点/结果/反应/出口）",
      all(k in sbs for k in ("起始", "过程", "接触", "顶点", "结果", "反应", "出口")))
check("㉓ 故事板图声明「每段一张」且「禁机械九宫格」",
      "每段一张" in sbs and "九宫格" in sbs and ("不机械九宫格" in sbs or "禁机械凑九宫格" in sbs or "禁止为了版式好看强行凑 9 格" in sbs))
check("㉓ 故事板图含 CLEAN_GRID 干净版 + 出口帧=下段入口帧 + 面板边界≠剪辑点",
      "CLEAN_GRID" in sbs and "TECHNICAL_ANNOTATED" in sbs
      and ("出口帧 = 下段入口帧" in sbs or "出口】面板 = 下段" in sbs or "出口帧" in sbs)
      and "面板边界" in sbs)
check("㉓ 故事板图声明与九宫格场景图/HTML 看板/15 格 PREVIS 四者互不替代",
      "九宫格场景图" in sbs and "storyboard-board-lite" in sbs)
check("㉓ sd-storyboard-engine SKILL 挂线故事板图（章节 + 规则库索引 + 契约）",
      bool(sbe) and "storyboard-sheet-template.md" in read(os.path.join(sbe, "SKILL.md"))
      and "故事板图" in read(os.path.join(sbe, "SKILL.md")))

# ㉔ 场景空间事实五件事
check("㉔ asset-spatial-ledger §四 含坐标系 / SET_STATE / 空气介质层 / 尺度参照",
      "场景空间坐标系" in asl and "SET_STATE" in asl
      and "空气介质" in asl and ("scale_evidence" in asl or "尺度参照" in asl))
check("㉔ asset-spatial-ledger §四·E 年代锚在案（2026-10-12 新增 · 剧本层《世界锚卡》同源）",
      "年代锚 ERA_ANCHOR" in asl and "禁用元素清单" in asl and "必现元素清单" in asl)
check("㉔ asset-spatial-ledger §一 人物锚在案（年龄锚/体型锚/身份外观三件套 + 反漂移清单）",
      all(k in asl for k in ("年龄锚", "体型锚", "身份外观三件套", "反漂移清单")) and "C26c" in asl)
check("㉔ SET_STATE 声明生效区间与同源变体 + 空气介质禁无源之雾",
      "生效区间" in asl and "同源" in asl and ("无源" in asl or "万能光柱" in asl))
check("㉔ asset-spatial-ledger §三 已挂导演稿上游指针（先有导演稿再写本栏）",
      "blocking-direction.md" in asl)

# ------------------------------------------------- [G] 素材形态与接线单域
section("[G] 素材形态与接线单域（图片入库降级为可选登记）")

_ade = read(os.path.join(refs_dir, "asset-delivery-modes.md"))
check("㉕ 素材形态权威文件存在（references/asset-delivery-modes.md）", bool(_ade.strip()))
check("㉕ 含 M0 / M1 / M2 三形态定义",
      "M0" in _ade and "M1" in _ade and "M2" in _ade
      and "纯提示词" in _ade and "编号占位" in _ade and "已入库" in _ade)
check("㉕ 明写默认形态 = M1（不写默认值执行者就会各写各的）", "默认形态 = M1" in _ade or "默认 M1" in _ade)
check("㉕ 含门禁按形态改判表（覆盖门禁 1~5，且门禁 6 不受影响）",
      "门禁分级生效" in _ade and "门禁 5" in _ade and "门禁 6" in _ade and "不受形态影响" in _ade)
check("㉕ 含文字锁 Text-Lock（M0/M1 一致性替代路径）",
      "Text-Lock" in _ade and "复述块" in _ade and "同上" in _ade)
check("㉕ 含《素材接线单》模板与「你该挂哪张」列",
      "素材接线单" in _ade and "你该挂哪张" in _ade and "不控制什么" in _ade)
check("㉕ 含三不一要（不索要 / 不阻塞 / 不假装 / 要声明）",
      "不索要" in _ade and "不阻塞" in _ade and "不假装" in _ade and "要声明" in _ade)
check("㉕ 含与 A0~A3 的正交说明（A 轴管复杂度 / M 轴管图在不在手里）",
      "正交" in _ade and "A0" in _ade and "A3" in _ade)
check("㉕ 含形态声明纪律（每次交付首行必写）", "素材形态：" in _ade and "首行" in _ade)

_afp = read(os.path.join(refs_dir, "asset-first-pipeline.md"))
check("㉕ asset-first-pipeline 已把「无图不进分镜」改为条件门并指向新权威",
      "改判为条件门" in _afp and "asset-delivery-modes.md" in _afp
      and "没有图\"本身永不构成阻断理由" in _afp)
check("㉕ asset-first-pipeline 门禁表含「形态影响」列", "形态影响" in _afp)
check("㉕ SKILL 核心法则 0 已含素材形态初判 + 默认 M1",
      "素材形态初判" in skill and "默认 M1" in skill)
check("㉕ SKILL 法则 11 已改为「素材形态与唯一事实来源按形态定义」",
      "素材形态与「唯一事实来源」按形态定义" in skill and "仅适用于 M2" in skill)
check("㉕ SKILL §E 含 E.1「图不在本包手里」四铁律",
      "E.1" in skill and "不索要" in skill and "要声明" in skill)
check("㉕ SKILL 权威归属表含第 23 规则域（素材存在形态与接线单）",
      "素材存在形态与接线单" in skill
      and "references/asset-delivery-modes.md" in skill)
check("㉕ SKILL 指令路由含 /素材形态 与 /接线单", "/素材形态" in skill and "/接线单" in skill)
check("㉕ SKILL 共享契约含素材形态条（第 13 条）", "13. **素材形态**" in skill)

_sfe = read(os.path.join(PKG, "sd-feed-engine", "SKILL.md"))
check("㉕ sd-feed-engine 共享契约含素材形态契约 + 首行声明必备",
      "素材形态契约" in _sfe and "素材形态：" in _sfe and "不得交付" in _sfe)
_gc = read(os.path.join(PKG, "sd-feed-engine", "scripts", "gate_check.py"))
check("㉕ gate_check.py 已实现闸门 6B（--mode + 形态一致性）",
      "--mode" in _gc and "check_asset_mode" in _gc and "闸门6B" in _gc)
check("㉕ gate_check.py 含虚假核验拦截（非 M2 不得声称已核验）",
      "虚假核验" in _gc and "已核验" in _gc)
check("㉕ 素材形态机检仍由投喂闸门层承载（未并入 C 系编号——C21 是打戏护栏杆，与素材形态无关）",
      "C21" not in _gc and "素材形态" in _gc)

_cfl = read(os.path.join(refs_dir, "prompt-feeding-checklist.md"))
check("㉕ prompt-feeding-checklist 锚点项已改按形态判定（旧绝对门条目已不存在）",
      "按素材形态判定" in _cfl
      and "- [ ] 锚点全部指向《资产图册》已锁定资产图（无图=门禁 3/4 阻断，回补 P2c）" not in _cfl)
_qgr = read(os.path.join(refs_dir, "quality-gate-review.md"))
check("㉕ quality-gate-review P0 含「虚假核验」与「形态违约」",
      "虚假核验" in _qgr and "形态违约" in _qgr)
_sae = read(os.path.join(PKG, "sd-asset-engine", "SKILL.md"))
check("㉕ sd-asset-engine 含 Step 3.8 素材形态判定 + 禁索要图片",
      "Step 3.8" in _sae and "禁止索要图片" in _sae)
_sqe = read(os.path.join(PKG, "sd-qc-engine", "SKILL.md"))
check("㉕ sd-qc-engine 一致性门按形态改判 + 明确「没有图片不属于缺失」",
      "asset-delivery-modes.md" in _sqe and "没有图片" in _sqe)

# ------------------------------------------------- [E++] 三项新增域
section("[E++] V7.3.1 新增域（解说引擎 / 方言外挂 / 打斗规程）")  # 域命名沿革：V7.3.1 引入，标识保留

# ㉖ 解说叙事类赛道转正 + sd-jieshuo-engine
_jse = sub_skill_path("sd-jieshuo-engine")
_js = read(os.path.join(_jse, "SKILL.md")) if _jse else ""
check("㉖ sd-jieshuo-engine 子技能目录存在", _jse is not None)
check("㉖ sd-jieshuo-engine 含旁白稿 VO Script / 声画信息差 / 三大子类型",
      "旁白稿" in _js and "声画信息差" in _js
      and all(k in _js for k in ("历史人物志", "历史事件", "科普")))
check("㉖ sd-jieshuo-engine 声明 C14 配额豁免（赛道③ 全片 VO）",
      "豁免" in _js and "C14" in _js and "全片 VO" in _js)
check("㉖ sd-jieshuo-engine 三份 references 齐备（旁白稿/历史视觉/爆款公式）",
      bool(_jse) and all(os.path.exists(os.path.join(_jse, "references", f)) for f in
                         ("narration-vo-script.md", "history-visual-style.md", "explainer-formulas.md")))
check("㉖ sd-jieshuo-engine 声明不替代 sd-script-engine", "不替代" in _js)
check("㉖ track-routing ③ 解说叙事类已转正（挂载 sd-jieshuo-engine）",
      "解说叙事类" in tr and "sd-jieshuo-engine" in tr and "预留槽位" not in tr)
check("㉖ SKILL 〇·0 含 ③ 解说叙事类 + 挂载 sd-jieshuo-engine",
      "解说叙事类" in skill and "sd-jieshuo-engine" in skill)
check("㉖ SKILL 权威归属表含解说叙事域（第 24 行）",
      "解说叙事类规则集" in skill and "narration-vo-script" in skill)
check("㉖ SKILL 共享契约含解说叙事条（第 14 条）", "14. **解说叙事**" in skill)
check("㉖ SKILL 指令路由含 /解说", "/解说" in skill)
check("㉖ SKILL 含法则 26 解说叙事类规则", "解说叙事类规则" in skill)

# ㉗ 方言外挂参考
_dv = read(os.path.join(refs_dir, "dialect-voice-control-dictionary.md"))
check("㉗ 方言词典外挂文件存在（references/dialect-voice-control-dictionary.md）", bool(_dv.strip()))
check("㉗ 方言词典含 50 套 + 总控 12 条 + 外挂定位（非规则域）",
      "50 套" in _dv and "总控" in _dv and "外挂" in _dv and "非规则域" in _dv)
check("㉗ SKILL 声明方言词典为外挂（不进权威归属表）",
      "dialect-voice-control-dictionary.md" in skill and "外挂参考" in skill)
check("㉗ SKILL 指令路由含 /方言配音", "/方言配音" in skill)

# ㉘ 打斗规程吸收
_ebp = read(os.path.join(PKG, "sd-xuanhuan-engine", "references", "epic-battlefield-protocols.md"))
check("㉘ 史诗战场协议文件存在（sd-xuanhuan-engine/references/epic-battlefield-protocols.md）",
      bool(_ebp.strip()))
check("㉘ 史诗战场协议含阵营色彩锁 / Z 型移位 / 群战递增 / 武器单次变形 / 蓄力与定格",
      "阵营色彩锁" in _ebp and "Z 型" in _ebp and "递增" in _ebp
      and "武器形态单次变形" in _ebp and "尾帧定格" in _ebp)
_ifa = read(os.path.join(PKG, "sd-combat-engine", "references", "impact-frame-and-banlist.md"))
check("㉘ 冲击帧与负面词库文件存在（sd-combat-engine/references/impact-frame-and-banlist.md）",
      bool(_ifa.strip()))
check("㉘ 冲击帧分级含三级 + 3 帧白闪", "三级" in _ifa and "白闪" in _ifa)
check("㉘ 战斗段「只要音效、禁 BGM」已入声音设计模板",
      "只要音效" in read(os.path.join(PKG, "sd-qc-engine", "references", "sound-design-template.md")))
check("㉘ 参考图投喂顺序已入素材映射",
      "参考图投喂顺序" in read(os.path.join(PKG, "sd-feed-engine", "references", "asset-mapping-and-rules.md")))
check("㉘ SKILL 挂线史诗战场协议与冲击帧词库",
      "epic-battlefield-protocols.md" in skill and "impact-frame-and-banlist.md" in skill)
check("㉘ SKILL 含法则 27 打斗史诗规程", "打斗史诗规程" in skill)

# ㉙ 赛道③ C14n 豁免的三处互锁（引擎声明 ↔ 机检实现 ↔ 手册登记）
# 动机：豁免口径写在 sd-jieshuo-engine，机检实现写在 validate_prompt.py，登记写在 qc 手册——
# 任一处单边改动都会让门禁静默失效（引擎说豁免、脚本没实现 → 误报；脚本实现了、手册没登记 →
# 下游不会传 --track 3 → 照样误报）。故三处同时断言，把"口径一致性"变成可机检项。
_vp = read(os.path.join(BASE, "scripts", "validate_prompt.py"))
check("㉙ validate_prompt.py 支持 --track 参数（〇·0 赛道分流）",
      '"--track"' in _vp and 'NARR_TRACKS = {"3"}' in _vp and "--track 1|2|3|4" in _vp)
check("㉙ validate_prompt.py 含赛道③ C14 豁免分支（is_narr 分流）",
      "is_narr" in _vp and "C14n" in _vp and "NARR_TRACKS" in _vp)
check("㉙ validate_prompt.py 保留 C14 三项 FAIL 红线（豁免不放过红线）",
      "声画分离红线" in _vp and "写进了台词字段" in _vp and "台词字符" in _vp)
check("㉙ validate_prompt.py 含 C14n 旁白-画面映射判据（_pic_content_len）",
      "_pic_content_len" in _vp and "旁白镜无画面描述" in _vp)
check("㉙ validate_prompt.py usage 文档含 --track 说明",
      "--track 1|2|3|4" in _vp)
check("㉙ sd-jieshuo-engine 声明机检实现落在 validate_prompt.py（--track 3）",
      "sd-jieshuo-engine" in _js and "--track 3" in _js and "C14n" in _js)
_mcm = read(os.path.join(PKG, "sd-qc-engine", "references", "machine-check-manual.md"))
check("㉙ qc 机检手册已登记 --track 与 C14 赛道改判表",
      "--track" in _mcm and "C14n" in _mcm and "整体豁免" in _mcm)
check("㉙ SKILL 机检段声明赛道分流（--track / C14n）",
      "--track 1|2|3|4" in skill or "--track 3" in skill)

# ------------------------------------------------- [E+++] 接线修复域
# 动机：三份出图模板（九宫格 / 立绘 / 道具）此前在 128 条断言里**各出现 0 次**——
# 把它们删掉或字段删空，包级校验依然全绿（只保证"每个子技能 references ≥3 份"这个数量条件）。
# 本域把它们的关键字段变成真断言；另加「脚本 C 码 ⊆ 手册 C 码」锁，防文档再次滞后于脚本。
section("[E+++] V7.3.2 接线修复域（三份出图模板完整性 / 机检 C 码一致性）")  # 域命名沿革：V7.3.2 引入，标识保留

# ㉚ 三份出图模板完整性
_ass = sub_skill_path("sd-asset-engine")
_grid_p = os.path.join(_ass, "references", "scene-grid-template.md") if _ass else ""
_port_p = os.path.join(_ass, "references", "character-portrait-templates.md") if _ass else ""
_prop_p = os.path.join(_ass, "references", "prop-template.md") if _ass else ""
check("㉚ 三份出图模板文件均存在（九宫格 / 立绘 / 道具）",
      bool(_ass) and all(os.path.exists(x) for x in (_grid_p, _port_p, _prop_p)))
_grid = read(_grid_p)
_port = read(_port_p)
_prop = read(_prop_p)

check("㉚ 九宫格模板含 8 个结构化字段（内容分配/锁定模式/摄影机矩阵/摄影机参数/光照曝光/标注要求/画面纯净/风格分支）",
      all(k in _grid for k in ("【九宫格内容分配】", "【参考场景锁定模式】", "【九宫格摄影机矩阵】",
                               "【摄影机参数】", "【光照与曝光控制】", "【画面标注要求】",
                               "【画面纯净要求】", "【风格分支】")))
check("㉚ 九宫格模板声明「按空间类型选表」+ 三张替代表 + 「禁止硬凑」",
      "空间类型" in _grid and "表 ①" in _grid and "表 ②" in _grid and "表 ③" in _grid
      and "禁止硬凑" in _grid)
check("㉚ 九宫格模板三张空间类型表齐备（室外独立建筑 / 室内半封闭 / 自然场地·街巷）",
      "室外独立建筑" in _grid and "室内 / 半封闭空间" in _grid and "自然场地 / 街巷" in _grid)
check("㉚ 九宫格模板含标注降级条款（降级 + 编号 + 对照表 + 禁裸格）",
      "降级" in _grid and "编号" in _grid and "对照表" in _grid and "裸格" in _grid)
check("㉚ 九宫格模板含槽位定位句（1 张图 = 9 个视角 = 1 个素材槽）",
      "素材槽" in _grid and "9 个视角" in _grid)
check("㉚ 九宫格模板含模式B 锁定档拆分（允许切换子区域机位 与 仅允许摄影机移动 并存）",
      "允许按子区域切换机位" in _grid and "仅允许摄影机移动" in _grid)
check("㉚ 九宫格模板已与总控 asset-spatial-ledger §四 双向接线（母版 / 站位版 / 出图顺序）",
      "asset-spatial-ledger.md" in _grid and "母版" in _grid and "站位版" in _grid and "出图顺序" in _grid)

check("㉚ 角色提示词权威模板明确四字段与五官描述",
      all(k in read(os.path.join(PKG, "short-drama-director", "references", "asset-spatial-ledger.md"))
          for k in ("画幅", "排版结构", "服装与身体材质", "面部特写"))
      and "五官 10 项" in read(os.path.join(PKG, "short-drama-director", "references", "asset-spatial-ledger.md")))
check("㉚ 立绘模板含「禁止持道具 / 禁止 pose」硬条",
      "手持" in _port and "pose" in _port and "禁止" in _port)
check("㉚ 道具模板含「纯道具 + 禁止出现手/人物剪影」硬条",
      "纯道具" in _prop and "手持" in _prop and "剪影" in _prop and "禁止" in _prop)
check("㉚ 强制读取清单 P2 行：三份出图模板由「按需」改「必读」+ 点名九宫格 8 字段硬产出",
      "必读 `sd-asset-engine/references/scene-grid-template.md`" in skill
      and "九宫格提示词须含 8 字段" in skill
      and "按需 `sd-asset-engine/references/scene-grid-template.md`" not in skill)

# ㉛ 机检 C 码一致性：validate_prompt.py 实现的 C 系码 ⊆ 机检手册登记的 C 系码
_C_PAT = re.compile(r"\bC(?:3[0-9]|2[0-9]|1[0-9]|[1-9])[a-z]?\b")  # 2026-10-14：扩至 C1~C39 及全字母子码（含 C27x/C30a~d），彻底锁死「脚本 ⊆ 手册」
_vp_codes = set(_C_PAT.findall(read(vp)))
_mcm_codes = set(_C_PAT.findall(_mcm))
_miss_mcm = sorted(_vp_codes - _mcm_codes,
                   key=lambda x: (int(re.search(r"\d+", x).group()), x))
check("㉛ 机检手册登记了脚本实现的全部 C 系码（脚本 ⊆ 手册 · 防「脚本有、手册无」）",
      not _miss_mcm, "手册缺登记: " + ", ".join(_miss_mcm))
check("㉛ 手册含「子检查码登记」表（V7.3.2 补登入口）",  # 域命名沿革：V7.3.2 引入，入口保留
      "子检查码登记" in _mcm and "C19a" in _mcm and "C20c" in _mcm and "C16d" in _mcm)
check("㉛ SKILL 机检维度分组同步列出子码清单（C19a~e / C20a~d 全名点名）",
      "C19a" in skill and "C19b" in skill and "C19c" in skill and "C19e" in skill
      and "C20c" in skill and "C18b" in skill)

# ------------------------------------------------- [E*22] 子码计数口径一致性域
# 动机（2026-10-13 整包体检）：上一轮加 C26/C27 时只改了机检手册的计数（当时另有一份微核副本），
# 漏改 README / checklist / 打戏库三处「子检查码共 59 条」，造成同一指标
# 跨文件数值打架（59 vs 64），而 check_package.py **没有任何断言覆盖它**——
# 这是互锁盲区：计数漂移无人管，直到人工体检才发现。本域补上该断言。
section("[E*22] 子码计数口径一致性域（防 59/64 漂移 · 2026-10-13 体检补）")
_readme = read(os.path.join(BASE, "README.md"))
_checklist = read(os.path.join(BASE, "references", "prompt-feeding-checklist.md"))
_combat_guard = read(os.path.join(PKG, "sd-combat-engine", "references",
                                 "combat-rhythm-and-load-guardrails.md"))

# ---------------------------------------------------------------- 子码计数唯一口径
# ★2026-10-15 Agent 修复：原实现只查「自称 68 条」这个字符串在不在，**不校验加总**——
#   故 2026-10-14 把 C26 由 a~d 扩到 a~g 时只改了枚举、忘改总数，造成
#   「自称 68 / 自身枚举加总 71 / 脚本实为 94」三方打架而零告警（[E*22] 建域时想防的正是这类事故）。
# 现口径：手册内 `SUBCODE-Registry` 机器可读块 = 唯一权威清单，三项断言：
#   ① 块内条数 == 手册声称的总数（自洽）
#   ② 块内集合 == 脚本出现的全部子码集合（双向 · 防「脚本有、清单无」）
#   ③ 块内集合 == 手册全文出现的子码集合（双向 · 防「登记了却没进清单」与幽灵码）
# 改名/加码时只需同步这**一个块**，其余计数落点全部引用本常量。
SUBCODE_TOTAL = 98
_SUB_PAT = re.compile(r"\bC\d{1,2}[a-z]\d?\b")
_reg_blk = re.search(r"SUBCODE-Registry:START.*?-->(.*?)<!--\s*SUBCODE-Registry:END",
                     _mcm, re.S)
_registry = _reg_blk.group(1).split() if _reg_blk else []
_reg_set = set(_registry)
_mcm_subs = set(_SUB_PAT.findall(_mcm))
_vp_subs = set(_SUB_PAT.findall(read(vp)))


def _expand_c_ranges(txt):
    """把 `C18a~n` / `C30i~l` 这类范围写法展开成子码集合。

    总控 SKILL.md 用**范围记账**（`C18g~l`），逐字面查会漏判——必须先展开再比对，
    否则会出现「SKILL 明明已覆盖 C18h~l，断言却说缺失」的假 FAIL。
    """
    out = set(_SUB_PAT.findall(txt))
    for m in re.finditer(r"C(\d{1,2})([a-z])\s*~\s*(?:C)?(\d{1,2})?([a-z])", txt):
        fam, a, fam2, b = m.groups()
        if fam2 and fam2 != fam:
            continue
        for o in range(ord(a), ord(b) + 1):
            out.add(f"C{fam}{chr(o)}")
    return out


_skill_subs = _expand_c_ranges(skill)
check("㉛ 总控 SKILL 子码清单完整覆盖 SUBCODE-Registry（防「手册有、总控无」· 含范围展开）",
      not (_reg_set - _skill_subs) and f"全 {SUBCODE_TOTAL} 条" in skill,
      f"总控缺: {sorted(_reg_set - _skill_subs)}")
check("㊾ 子码计数唯一口径：手册 SUBCODE-Registry 块存在，且块内条数 == 声称总数（防「自称 N、实为 M」）",
      bool(_registry) and len(_registry) == SUBCODE_TOTAL
      and f"{SUBCODE_TOTAL} 个子码" in _mcm,
      f"注册清单 {len(_registry)} 条 / 常量 {SUBCODE_TOTAL} 条"
      + ("（未找到 SUBCODE-Registry 块）" if not _registry else ""))
check("㊾ 子码注册清单双向完备：脚本集合 == 清单 == 手册全文集合（防漏登与幽灵码）",
      _vp_subs == _reg_set and _mcm_subs == _reg_set,
      f"脚本有清单无: {sorted(_vp_subs - _reg_set)} ｜ 清单有脚本无: {sorted(_reg_set - _vp_subs)} "
      f"｜ 手册有清单无: {sorted(_mcm_subs - _reg_set)}")
check("㊾ 计数口径单一来源：本文件内所有计数落点均引用 SUBCODE_TOTAL 常量（无写死数字残留）",
      ("68" + " 个子码") not in read(__file__)
      and ("子检查码共 " + "68" + " 条") not in read(__file__))
check("㊾ 子码计数无过时残留：全包不得再出现「子检查码共 59 条」",
      "子检查码共 59 条" not in _readme
      and "子检查码共 59 条" not in _checklist
      and "子检查码共 59 条" not in _combat_guard
      and "子检查码共 59 条" not in _mcm)
check(f"㊾ 三处姊妹落点均声明 {SUBCODE_TOTAL} 条（README / checklist / 打戏库）",
      f"子检查码共 {SUBCODE_TOTAL} 条" in _readme
      and f"子检查码共 {SUBCODE_TOTAL} 条" in _checklist
      and f"子检查码共 {SUBCODE_TOTAL} 条" in _combat_guard)
check("㊾ 主码口径稳定：全包对外仍报 C1~C26（编号不重排）",
      "编号不重排" in skill and "C1~C26" in skill
      and "编号不重排" in _mcm)
check("㊾ 增量主码 C26/C27 均在手册 §二 门禁清单登记主码行",
      re.search(r"^\| C26 \|", _mcm, re.M) is not None
      and re.search(r"^\| C27 \|", _mcm, re.M) is not None)
check("㊾ 手册 §二 子码登记表不含 C27a~d 重复行（C27 只以主码行登记）",
      "| **C27a~d** |" not in _mcm)

# ------------------------------------------------- [E++++] 打戏护栏域
# 动机：外部包 huhe-combat-director V2.1 的「拉片实证层」有四项实测校正规则——
# 对抗激烈度硬护栏 / 特效手绘化铁律 / 减速器配额 / 三层分层写法。全包关键词普查证实
# 本包此前**四项命中全为 0**；且 C1~C20 里**没有任何一项管「打戏到底打没打起来」**。
# 本域把吸收结果变成真断言，并把 C21 做成「引擎声明 ↔ 脚本实现 ↔ 手册登记」三处互锁。
section("[E++++] V7.3.3 打戏护栏域（两份新库完整性 / C21 三处互锁）")  # 域命名沿革：V7.3.3 引入，标识保留

_cb = sub_skill_path("sd-combat-engine")
_cib_p = os.path.join(_cb, "references", "combat-intensity-guardrails.md") if _cb else ""
_vrm_p = os.path.join(_cb, "references", "vfx-rendering-mandate.md") if _cb else ""
check("㉜ 两份打戏新库文件均存在（激烈度硬护栏 / 特效手绘化）",
      bool(_cb) and all(os.path.exists(x) for x in (_cib_p, _vrm_p)))
_cib = read(_cib_p)
_vrm = read(_vrm_p)

check("㉜ 护栏库含六条硬护栏（位移接触 / 构图不许重复 / 贴身时长下限 / 禁摆拍 / 抽特效自检 / 隔空对波定位）",
      all(k in _cib for k in ("每段必含", "相邻两段不许同构图", "贴身对招占比下限",
                              "禁止摆拍动词", "抽掉特效", "隔空对波")))
check("㉜ 护栏库含分层管理（自由组合区 / 硬护栏区）+【快】拍 ≥40% 下限",
      "自由组合区" in _cib and "硬护栏区" in _cib and "≥ 片长 40%" in _cib)
check("㉜ 护栏库含减速器配额（黑白闪 / 定格帧 / 慢镜 三档片长上限）",
      "减速器配额" in _cib and "黑白闪" in _cib and "定格帧" in _cib and "慢镜" in _cib)
check("㉜ 护栏库含节奏零件六件 + 术语避撞声明（勿与文戏「情绪节拍」混用）",
      all(k in _cib for k in ("蓄", "快", "停", "慢", "静", "爆"))
      and "情绪节拍" in _cib and "勿与" in _cib)
check("㉜ 护栏库声明机检载体 C21a~d（三处互锁的「规则侧」）",
      all(k in _cib for k in ("C21a", "C21b", "C21c", "C21d")))

check("㉜ 手绘化库含五手法表 + 禁用孤立概念词硬约束",
      all(k in _vrm for k in ("泼墨", "漫画式平涂色块", "手绘速度线", "墨线勾勒", "笔触状残影"))
      and "禁用" in _vrm and "粒子" in _vrm)
check("㉜ 手绘化库含三层分层写法（外层 / 中层 / 内层 / 边缘附着）",
      all(k in _vrm for k in ("外层", "中层", "内层", "边缘附着")))
check("㉜ 手绘化库含黑白闪三个必须词 + 8K 口径争议备案（登记但不落地）",
      "三个必须词" in _vrm and "8K" in _vrm and "争议备案" in _vrm)

# C21 三处互锁：三引擎声明 ↔ validate_prompt.py 实现 ↔ 机检手册登记
check("㉜ 三处互锁①：三份打戏引擎 SKILL 均声明 C21（引擎侧）",
      all("C21" in read(os.path.join(sub_skill_path(n), "SKILL.md"))
          for n in ("sd-combat-engine", "sd-xuanhuan-engine", "sd-real-engine")
          if sub_skill_path(n)))
check("㉜ 三处互锁①：玄幻 / 真人两引擎回指两份新库（跨引擎共用接线）",
      "combat-intensity-guardrails.md" in read(os.path.join(sub_skill_path("sd-xuanhuan-engine"), "SKILL.md"))
      and "vfx-rendering-mandate.md" in read(os.path.join(sub_skill_path("sd-xuanhuan-engine"), "SKILL.md"))
      and "combat-intensity-guardrails.md" in read(os.path.join(sub_skill_path("sd-real-engine"), "SKILL.md")))
check("㉜ 三处互锁②：validate_prompt.py 实现 C21a~d + --combat 触发门（脚本侧）",
      all(k in _vp for k in ("C21a", "C21b", "C21c", "C21d"))
      and '"--combat"' in _vp and "COMBAT_SIGNAL_RE" in _vp
      and "_combat_on" in _vp and "_combat_ranges" in _vp)
check("㉜ 三处互锁③：机检手册已登记 C21a~d（手册侧）",
      all(k in _mcm for k in ("C21a", "C21b", "C21c", "C21d")))
check("㉜ 总控 SKILL 声明「激烈度门」与 --combat 参数",
      "C21" in skill and "--combat" in skill and "激烈度门" in skill)

# ------------------------------------------- [E++++] 节奏负载域（C22 四处互锁 + 防回归）
section("[E++++] V7.3.4 节奏与渲染负载护栏域（新库完整性 / C22 四处互锁 / 接线防回归）")  # 域命名沿革：V7.3.4 引入，标识保留

_rlg_p = os.path.join(_cb, "references", "combat-rhythm-and-load-guardrails.md") if _cb else ""
check("㉝ 节奏负载护栏库存在", bool(_cb) and os.path.exists(_rlg_p))
_rlg = read(_rlg_p)

check("㉝ 库含独立动作单元 IAU 定义 + 上限表（★上限型，补 C21 方向性缺口）",
      "独立动作单元" in _rlg and "IAU" in _rlg and "上限" in _rlg)
check("㉝ 库含 IAU 上限表分档（≤2s/3s/4s/5s/≥6s）",
      all(k in _rlg for k in ("≤ 2s", "3s", "4s", "5s", "≥6s")))
check("㉝ 库含镜内速度四拍（起·爆·顿·收）+ 顿拍为最关键一拍",
      all(k in _rlg for k in ("起（慢）", "爆（快）", "顿（停）", "收（慢）"))
      and "最关键" in _rlg)
check("㉝ 库含逐镜判定口径 + 禁用『全片总数≥镜数』的反面教材",
      "逐镜" in _rlg and "全片总数" in _rlg and "蒙混过关" in _rlg)
check("㉝ 库含结构标注剥离规则（只剥纯标签·不得连坐正文）",
      "纯结构标注" in _rlg and "连坐" in _rlg)
check("㉝ 库含全身景别下限 + 贴脸档连续上限",
      "全身景别" in _rlg and "中全景" in _rlg and "贴脸档" in _rlg)
check("㉝ 库含四条病根档案（V7.3.3 呆滞出片实证，勿删 · 沿革锚点）",
      all(k in _rlg for k in ("病根①", "病根②", "病根③", "病根④")))
check("㉝ 库声明机检载体 C22a~d（规则侧）",
      all(k in _rlg for k in ("C22a", "C22b", "C22c", "C22d")))
check("㉝ 库含『机检 PASSED ≠ 出片好看』纪律 + 出片复盘义务",
      "PASSED" in _rlg and "出片复盘" in _rlg and "抽帧" in _rlg)

# ★防回归：病根①是「铁律26 动作数上限没进自检闸口」，故断言其必须已接线
_cil = read(os.path.join(_cb, "references", "combat-iron-laws.md"))
check("㉝ ★防回归：铁律26 已补『V7.3.4 接线补闸』说明（病根① 的修复锚点 · 沿革锚点）",
      "接线补闸" in _cil and "A 引擎的硬约束在 B 链上整体失效" in _cil)
check("㉝ ★防回归：铁律26 已声明量化口径改用 IAU 表 + 判罚以 C22 为准",
      "combat-rhythm-and-load-guardrails.md" in _cil and "判罚以 C22 为准" in _cil)

# C22 四处互锁
check("㉝ 四处互锁①：三份打戏引擎 SKILL 均声明 C 码口径（引擎侧 · V7.3.7 起为 C1~C26 · 沿革锚点）",
      all("C1~C26" in read(os.path.join(sub_skill_path(n), "SKILL.md"))
          for n in ("sd-combat-engine", "sd-xuanhuan-engine", "sd-real-engine")
          if sub_skill_path(n)))
check("㉝ 四处互锁①：三引擎规则库索引表均收录新库（路由入口，缺则库白建）",
      all("combat-rhythm-and-load-guardrails.md" in read(os.path.join(sub_skill_path(n), "SKILL.md"))
          for n in ("sd-combat-engine", "sd-xuanhuan-engine", "sd-real-engine")
          if sub_skill_path(n)))
check("㉝ 四处互锁①：三引擎第5步自检闸口均含『六问』（写作期接线）",
      all("六问" in read(os.path.join(sub_skill_path(n), "SKILL.md"))
          for n in ("sd-combat-engine", "sd-xuanhuan-engine", "sd-real-engine")
          if sub_skill_path(n)))
check("㉝ 四处互锁②：validate_prompt.py 实现 C22a~d + 三个辅助函数（脚本侧）",
      all(k in _vp for k in ("C22a", "C22b", "C22c", "C22d"))
      and all(k in _vp for k in ("COMBAT_IAU_RE", "_combat_iau", "_iau_limit",
                                 "_strip_struct_annot", "COMBAT_BEAT_RE")))
check("㉝ 四处互锁②：IAU 计数含『抓住』人名容错（构建期踩坑③的修复锁）",
      "抓住" in _vp and "0,6" in _vp)
check("㉝ 四处互锁②：C22 与 C21 共用 --combat 触发门（未新增独立参数）",
      "C21/C22" in _vp or "C22 打戏节奏" in _vp)
check("㉝ 四处互锁③：机检手册已登记 C22a~d（手册侧）",
      all(k in _mcm for k in ("C22a", "C22b", "C22c", "C22d")))
check("㉝ 四处互锁④：总控 SKILL 声明节奏负载门 + C22",
      "C22" in skill and "combat-rhythm-and-load-guardrails.md" in skill)

# 方向性断言：C21 与 C22 必须同时存在且分工写明（防把上限型判据删掉只剩下限型）
check("㉝ 方向性：C21 与 C22 分工写明（C21 管激烈度下限 / C22 管负载上限）",
      "C21" in _rlg and "C22" in _rlg and "上限型" in _rlg and "不许过载" in _rlg)

# ---------------------------------------------------------------- [F] 外部版本保全
section("[F] 外部版本保全（版本统一不得误伤外来来源）")

_all_text = "\n".join(read(p) for p in scan_md_files())
for v in EXTERNAL_VERS:
    check(f"外部产品版本 {v} 仍存在（未被统一误改）", v in _all_text)

# ---- ㉝ 域加固：结构化定位断言（对抗测试定位到 4 处『关键词判读过松』后新增）----
# 教训：`关键词 in 文件全文` 这种判读无法定位到具体结构——同一关键词在库中多处出现，
# 或与正文引用共用，拆掉一处断言照样通过。对抗测试实测 4/8 漏网，全部由此造成。
# 正法：按结构定位（表格行 / 标题行 / 函数调用），拆一处即倒。
def _row_has(text, key, must):
    """存在同时含 key 与 must 的表格行（以 '|' 开头）。"""
    for ln in text.split("\n"):
        ln = ln.strip()
        if ln.startswith("|") and key in ln and must in ln:
            return True
    return False


def _head_has(text, key, must):
    """存在同时含 key 与 must 的标题行（# / ## / ###）。"""
    for ln in text.split("\n"):
        ln = ln.strip()
        if ln.startswith("#") and key in ln and must in ln:
            return True
    return False


def _in_warns_append(text, code):
    """code 是否真的出现在 warns.append(...) 的调用参数里（而非注释/文档头）。"""
    for m in re.finditer(r"warns\.append\((?:[^()]|\([^()]*\))*\)", text, re.S):
        if code in m.group(0):
            return True
    return False


def _warns_text(text, code):
    """取出该 code 所在的 warns.append(...) 调用全文。"""
    for m in re.finditer(r"warns\.append\((?:[^()]|\([^()]*\))*\)", text, re.S):
        if code in m.group(0):
            return m.group(0)
    return ""


check("㉝ 加固②：C22 机检表逐行标注方向性（C22a/C22b 须为『上限型』）",
      _row_has(_rlg, "**C22a**", "上限型") and _row_has(_rlg, "**C22b**", "上限型"))
check("㉝ 加固③：§2.2 节标题须为『逐镜判定』且显式禁『全片总数』口径",
      _head_has(_rlg, "2.2", "逐镜") and "全片总数" in _rlg)
check("㉝ 加固⑥：三引擎规则库索引表均含新库表格行（区别于正文引用）",
      all(_row_has(read(os.path.join(sub_skill_path(n), "SKILL.md")),
                   "combat-rhythm-and-load-guardrails.md", "|")
          for n in ("sd-combat-engine", "sd-xuanhuan-engine", "sd-real-engine")
          if sub_skill_path(n)))
check("㉝ 加固⑦：C22a~d 均真实落在 warns.append 调用中（不是只写在注释里）",
      all(_in_warns_append(_vp, c) for c in ("C22a", "C22b", "C22c", "C22d")))
# 方向性落到告警措辞：上限型判据必须在文案里对作者明说「上限」与超了什么
check("㉝ 加固⑦：C22a/C22b 告警文案须含『上限』语义（方向性落到措辞）",
      "上限" in _warns_text(_vp, "C22a") and "上限" not in _warns_text(_vp, "C22c"))

# ------------------------------------------------- [E*5] 画风锁域
# 动机：期间徐克版 10 秒实拍复盘证明画风参数组有效（5/5 项量化通过），
# 把「选导演风格」收编为三件套：I 锁 + style-bible 知识库 + C23 机检。
# 本域做真断言：知识库完整性 / 引擎在位 / C23 三处互锁 / 接线防回归。
section("[E*5] V7.3.5 画风锁域（style-bible 完整性 / C23 三处互锁 / 接线防回归）")  # 域命名沿革：标识保留

_sb_dir = os.path.join(BASE, "references", "style-bible")
_sb_files = ("style-lock-protocol.md", "style-archetype-taxonomy.md",
             "director-style-catalog-74.md", "style-fit-and-combat-matrix.md",
             "director-to-prompt-protocol.md", "director-param-library.md",
             "style-prefix-blocks.md", "style-bible-spec.md")
_missing_sb = [f for f in _sb_files if not os.path.isfile(os.path.join(_sb_dir, f))]
check("㉞ style-bible 知识库 8 份齐备（锁规程/六原型/74组/适配矩阵/植入规程/参数源/成品块/交付规范）",
      not _missing_sb, "缺: " + ", ".join(_missing_sb))

_ex_dir = os.path.join(_sb_dir, "examples")
_missing_ex = [f for f in ("demo-feed-wkw-15s.md", "demo-feed-xuke-15s.md")
               if not os.path.isfile(os.path.join(_ex_dir, f))]
check("㉞ style-bible/examples 成稿示例 2 份在位（王家卫 15s / 徐克 10s）",
      not _missing_ex, "缺: " + ", ".join(_missing_ex))

_missing_sl = [f for f in ("style-lock-ladder.py", "style-lock-recommend.py")
               if not os.path.isfile(os.path.join(BASE, "scripts", f))]
check("㉞ 画风锁引擎脚本 2 份在位（ladder / recommend）", not _missing_sl, "缺: " + ", ".join(_missing_sl))

check("㉞ 编号裁定在案：style-lock-protocol.md 注明「方案通称 F 锁 = 包内 I 锁」口径",
      os.path.isfile(os.path.join(_sb_dir, "style-lock-protocol.md"))
      and "F 锁" in read(os.path.join(_sb_dir, "style-lock-protocol.md")))

# C23 三处互锁：脚本实现 ↔ 手册登记 ↔ 总控触发门口径
check("㉞ C23 实现：validate_prompt.py 含 C23a/b/d1/d2/e/f 判据",
      all(c in _vp for c in ("C23a", "C23b", "C23d1", "C23d2", "C23e", "C23f")))
check("㉞ C23 登记：机检手册含 C23a~f 全套子码（C23 七子码逐条登记）",
      all(c in _mcm for c in ("C23a", "C23b", "C23c", "C23d1", "C23d2", "C23e", "C23f")))
check("㉞ C23 口径：总控 SKILL.md 含 I 锁节与 --c23 触发门",
      "画风锁" in skill and "--c23" in skill and "I · 画风锁" in skill)
check("㉞ C23 接线：sd-feed-engine 含画风锁契约、sd-asset-engine 锁系统含 I 锁",
      "画风锁契约" in read(os.path.join(sub_skill_path("sd-feed-engine"), "SKILL.md"))
      and "I·画风锁" in read(os.path.join(sub_skill_path("sd-asset-engine"), "SKILL.md")))
check("㉞ C23 真实落在机检输出中（issues.extend(_c23_iss)，不是只写在注释里）",
      "issues.extend(_c23_iss)" in _vp)

# [E*6] 禁项单点纪律域：C24 实现 ↔ 手册登记 ↔ C7 前置等价
section("[E*6] V7.3.6 禁项单点纪律域（C24a/b 实现 / 登记 / C7 联动 / 自测在案）")  # 域命名沿革：标识保留
check("㉟ C24 实现：validate_prompt.py 含 C24a/C24b 判据与前置变体正则（逐段化 · 2026-10-10）",
      all(c in _vp for c in ("C24a", "C24b", "BAN_FRONT_TAG", "_ban_count", "_pre_n", "_seg_ban"))
      and "_dups" in _vp)
check("㉟ C24 登记：机检手册含 C24a/b（子码计数口径 = SUBCODE_TOTAL）",
      all(c in _mcm for c in ("C24a", "C24b")) and f"{SUBCODE_TOTAL} 个子码" in _mcm)
check("㉟ C24 联动：C7 段7 可由前置变体等价满足（脚本与手册双侧在案）",
      "BAN_FRONT_TAG.search(text)" in _vp and "等价满足" in _mcm)
check("㉟ C24 自测：validate_prompt.py 含 C24 五组用例（合规段7/前置等价/双写/补充变体/缺失）",
      all(c in _vp for c in ("前置禁项块应等价满足", "禁项双写应报 C24a",
                             "禁项补充块应报 C24a", "无禁项块应报 C24b")))


# [E*7] 域（打戏/武学规则域迁出总控 + 零断链）
section("[E*7] V7.3.7 去遗留域（9 份遗留件已删 / 入链点已改 / 新引擎专档在案）")  # 域命名沿革：标识保留
_LEGACY_GONE = [
    "action-cinematography-breakdown.md", "action-previs-15grid.md", "action-ultimate-finisher.md",
    "authentic-martial-taxonomy.md", "combat-direction-engine.md", "combat-rhythm-defense3state.md",
    "martial-arts-arsenal.md", "martial-arts-combat-library.md", "xuanhuan-magic-combat.md",
]
_still = [f for f in _LEGACY_GONE if os.path.exists(os.path.join(refs_dir, f))]
check("㊱ 9 份历史遗留打斗/武学文件已从总控 references 删除", not _still,
      "仍存在: " + ", ".join(_still))
check("㊱ 迁出内容新专档存在（sd-combat-engine/references/tier-and-finisher-system.md）",
      os.path.exists(os.path.join(PKG, "sd-combat-engine", "references", "tier-and-finisher-system.md")))
_tfs = read(os.path.join(PKG, "sd-combat-engine", "references", "tier-and-finisher-system.md"))
check("㊱ 新专档承载三档定档表 + 大招终结技体系（迁入内容完整）",
      all(k in _tfs for k in ("R1 写实克制", "R2 商业高燃", "R3 玄幻大招",
                              "视觉巅峰", "终结技三幕", "模式 A ~ K", "特效生长三段论", "急停弹射")))
_dangling = []
for _p in (os.path.join(BASE, "SKILL.md"), os.path.join(BASE, "README.md"),
           os.path.join(refs_dir, "aspect-ratio-adaptation.md"),
           os.path.join(refs_dir, "blocking-direction.md"),
           os.path.join(refs_dir, "camera-specs-15rules.md"),
           os.path.join(refs_dir, "seedance-render-engine.md"),
           os.path.join(refs_dir, "asset-first-pipeline.md"),
           os.path.join(refs_dir, "prompt-feeding-checklist.md"),
           os.path.join(PKG, "sd-xuanhuan-engine", "SKILL.md"),
           os.path.join(PKG, "sd-real-engine", "SKILL.md"),
           os.path.join(PKG, "sd-storyboard-engine", "references", "storyboard-sheet-template.md")):
    _s = read(_p)
    for _f in _LEGACY_GONE:
        if _f[:-3] in _s:
            _dangling.append(f"{os.path.basename(_p)}→{_f}")
check("㊱ 去遗留后零断链（总控/子技能两侧入链点均已改指）", not _dangling,
      "残留: " + "; ".join(_dangling))
check("㊱ 计数口径同步（SKILL 声明 == EXPECTED_REFS · 元规则四）",
      "45 份" not in skill and "36 份" not in skill and "37 份" not in skill
      and "38 份" not in skill and f"{EXPECTED_REFS} 份规则库" in skill and EXPECTED_REFS == 48)
check("㊲ M1 出图提示词配套纪律（asset-delivery-modes §4.4 · 2026-10-09 用户实测退回）",
      "出图提示词配套纪律" in _ade and "全套 P2.5 出图提示词" in _ade
      and "character-portrait-templates.md" in _ade and "scene-grid-template.md" in _ade
      and "prop-template.md" in _ade)
_pdg = read(os.path.join(PKG, "sd-storyboard-engine", "references", "plot-deduction-grid.md"))
check("㊲ 剧情分镜格（推演宫格）条件必出（plot-deduction-grid §四 · V4.0 回归）",
      "条件必出" in _pdg and "人物一致性试金石" in _pdg
      and "豁免" in _pdg and "禁止静默跳过" in _pdg
      and "条件必出" in skill)
check("㊱ 新引擎索引已挂专档（sd-combat-engine SKILL 索引表含 tier-and-finisher-system）",
      "tier-and-finisher-system.md" in read(os.path.join(PKG, "sd-combat-engine", "SKILL.md")))

# ------------------------------------------------- [E*9] V7.3.9 字数口径统一域（域命名沿革）
# 动机（外部审计 P0「规则与脚本口径统一」）：旧注释写「单段 ≤4500 字符」、实现按整份文件判；
#   且与 gate_check.py 的段级 1900/2000 关系从未写明。本域锁住「粒度 + 权威脚本」的声明，防单边漂移。
section("[E*9] V7.3.9 字数口径统一域（C4 篇级 4500 与闸门3 段级 1900/2000 的粒度声明）")  # 域命名沿革：标识保留
_vp_txt = read(vp)
_mcm_c4 = [l for l in _mcm.splitlines() if l.startswith("| C4 |")]
check("㊲ 机检手册 C4 行标明「单文件」篇级口径 + 指向 gate_check 段级判定",
      bool(_mcm_c4) and "单文件" in _mcm_c4[0] and "4500" in _mcm_c4[0] and "gate_check" in _mcm_c4[0])
check("㊲ validate_prompt 的 C4 注释与常量同步指向 gate_check 段级判定（口径双写）",
      "MAX_CHARS = 4500" in _vp_txt and "gate_check" in _vp_txt)

# ------------------------------------------------- [E*10] V7.4.8 外部增量与版本清洗病句修复域（域命名沿革）
# 动机：① 版本注记清洗中「动态词表内的动词」会与版本号被一并吃掉，留下「已于进 / 已于 按」类残句
#       ——此前的截断扫描只按「格式」写模式，漏了「删除动作的语义后果」这一类。
#       ② 本版吸收外部包的照明（色温对冲 / 气氛介质）与运镜（8 套单技法）增量，须锁住防回退。
section("[E*10] V7.4.8 外部增量与版本清洗病句修复域")  # 域命名沿革：标识保留
_e10_seglink = read(os.path.join(PKG, "sd-storyboard-engine", "references", "segment-linkage.md"))
_e10_segcont = read(os.path.join(PKG, "sd-feed-engine", "references", "segment-continuity-strategy.md"))
_e10_track = read(os.path.join(PKG, "short-drama-director", "references", "track-routing.md"))
_e10_light = read(os.path.join(PKG, "short-drama-director", "references", "lighting-and-antifake.md"))
_e10_camsys = read(os.path.join(PKG, "sd-storyboard-engine", "references", "short-drama-camera-system.md"))
_e10_madapt = read(os.path.join(PKG, "short-drama-director", "references", "model-adapters.md"))
check("㊳ 版本清洗残句已清零（「已于进」/「已于 按此法」类不存在）", not ("已于进" in _e10_seglink or "已于进" in _e10_segcont or "已于 按此法" in _e10_track))
check("㊳ 照明体系含「双色温冷暖对冲」与「空间物理介质」两节（外部增量已吸收）", "双色温冷暖对冲" in _e10_light and "空间物理介质" in _e10_light)
check("㊳ 高光运镜含 8 套单技法镜行参考写法", "单技法镜行参考写法" in _e10_camsys and "Dolly Zoom" in _e10_camsys and "Speed Ramping" in _e10_camsys)
check("㊳ 长对白 OTS 拓扑已并入 model-adapters §5.0.1（与 C17b 同缺口的两面）", "长对白过肩（OTS）双人在场拓扑" in _e10_madapt)
check("㊳ 机检 C17b 已实现（长对白段关系镜缺失告警）", "C17b" in _vp_txt)

# ------------------------------------------------- [E*11] 表演指导层域（C25 三处互锁）
# 动机：2026-10-09 接入粉丝投稿的 ACTING SKILL —— 它补的是本包此前的空白「行为与动机层」
#       （包里原有 FACS 微表情层 + 神态纪律层，但无人管目标/障碍/战术/节拍/潜台词/听与反应）。
#       接入纪律：规则文件必须真实存在、SKILL/README 必须挂路由、C25 必须三处互锁（脚本 ↔ 手册 ↔ 规则域）。
section("[E*11] 表演指导层域（acting-direction 新建 · C25 三处互锁 · 与 C11 反转同批）")
_e11_acting = os.path.join(refs_dir, "acting-direction.md")
check("㊴ 表演指导层文件存在（references/acting-direction.md）", os.path.isfile(_e11_acting))
_e11_at = read(_e11_acting) if os.path.isfile(_e11_acting) else ""
check("㊴ 表演指导层含五支柱（目标 / 障碍与代价 / 战术 / 节拍 / 潜台词）",
      all(w in _e11_at for w in ("目标", "障碍与代价", "战术", "节拍", "潜台词")))
check("㊴ 表演指导层含核心公理与两条招牌律（压力下的行为 / 两个真相律 / 然而当 X）",
      "压力下的行为" in _e11_at and "两个真相" in _e11_at and "然而，当" in _e11_at)
check("㊴ 表演指导层含四层分工表与三环节落点表（与 FACS / 神态纪律正交声明）",
      "神态纪律层" in _e11_at and "行为与动机层" in _e11_at and "落点表" in _e11_at)
check("㊴ 表演指导层标注未实拍验证纪律（【待验证·未实拍】）", "待验证" in _e11_at)
check("㊴ SKILL.md 索引树已挂 acting-direction（★表演指导层）",
      "★ acting-direction.md" in skill)
check("㊴ SKILL.md 唯一权威归属表含「表演（行为与动机层）」域行",
      "行为与动机层" in skill and "acting-direction.md`**" in skill)
check("㊴ README 规则域表已挂表演·行为行",
      "表演·行为" in readme and "acting-direction" in readme)
check("㊴ C25 互锁①：validate_prompt.py 实现 C25a/C25b",
      all(c in _vp_txt for c in ("C25a", "C25b", "C25_BLAND_FACE", "C25_SYNC_CROWD")))
check("㊴ C25 互锁②：机检手册已登记 C25a/C25b（子码计数口径 = SUBCODE_TOTAL）",
      all(c in _mcm for c in ("C25a", "C25b")) and f"{SUBCODE_TOTAL} 个子码" in _mcm)
check("㊴ C25 互锁③：机检手册 C1~C26 门禁清单含「表演层」小节并指向 acting-direction.md",
      "### 表演层" in _mcm and "acting-direction.md" in _mcm)
check("㊴ C25 真实落在机检输出中（warns.append(f\"C25a…\")）",
      'warns.append(f"C25a' in _vp_txt and 'warns.append(f"C25b' in _vp_txt)

# ------------------------------------------------- [E*14] 锚点继承域（C26 · 2026-10-12 新增）
# 动机：粉丝群实测反馈「剧本大纲明确了 2035 年南京…出来的是 80 年代的破街烂车，人物也搞得像协警」
#       「人物年龄、人物身材比例都卡不到」——世界锚与人物锚此前只写在散文里，没落纸也没有会响的检查。
#       本域锁死「剧本层规则源 ↔ 资产层规则源 ↔ 脚本实现 ↔ 手册登记 ↔ 自检用例 ↔ 总控分组」六处一致。
section("[E*14] 锚点继承域（C26a~d 六处互锁 · 世界锚/人物锚/因果表）")
_sbip = read(os.path.join(PKG, "sd-script-engine", "references", "story-bible-and-ip.md"))
_epp = read(os.path.join(PKG, "sd-script-engine", "references", "episode-planning.md"))
_cpt = read(os.path.join(PKG, "sd-asset-engine", "references", "character-portrait-templates.md"))
_ssp = read(os.path.join(PKG, "sd-script-engine", "references", "six-stage-pipeline.md"))
check("㊼ 互锁①：validate_prompt.py 实现 C26a~d + 四个锚点常量表",
      all(c in _vp_txt for c in ("C26a", "C26b", "C26c", "C26d",
                                 "C26_ERA_ANCHOR", "C26_AGE_ANCHOR", "C26_LOOK_ANCHOR",
                                 "C26_OLD_ELEMS", "C26_MODERN_ELEMS")))
check("㊼ 互锁②：机检手册已登记 C26a~d（子码计数口径 = SUBCODE_TOTAL）",
      all(c in _mcm for c in ("C26a", "C26b", "C26c", "C26d")) and f"{SUBCODE_TOTAL} 个子码" in _mcm)
check("㊼ 互锁③：总控 SKILL 机检维度分组含「锚点继承门」行且范围口径已同步 C26a~g",
      "锚点继承门" in skill and "C26a~g" in skill)
check("㊼ 互锁④：剧本层规则源在案（《世界锚卡》+《人物锚卡》+ 七/四铁律 + HANDOFF 交接）",
      "世界锚卡" in _sbip and "人物锚卡" in _sbip and "七条铁律" in _sbip
      and "WORLD_ANCHOR_CARD" in _sbip and "HANDOFF_CARD" in _sbip)
check("㊼ 互锁⑤：剧本层《因果与关系表》+ 情节点密度下限在案（治「没有人情世故」「剧情跳太快」）",
      all(k in _epp for k in ("因果与关系表", "CAUSALITY_AND_RELATION_TABLE", "人情世故",
                              "情节点密度", "理所当然禁令")))
check("㊼ 互锁⑥：阶段③④ 强制产出已接线（缺任一张 = 阶段未完成）",
      "世界锚卡" in _ssp and "人物锚卡" in _ssp and "因果与关系表" in _ssp)
check("㊼ 互锁⑦：资产层落纸（场景年代锚 §四·E + 立绘身份外观三件套 + 资产板人物锚）",
      "年代锚 ERA_ANCHOR" in asl and "身份外观三件套" in asl and "身份外观三件套" in _cpt
      and "反漂移清单" in _cpt)
check("㊼ 互锁⑧：自检含 C26 四组回归用例 + 结构定位（真实落在 warns.append）",
      all(c in _vp_txt for c in ("缺世界锚应报 C26a", "年代锚与正文物证冲突应报 C26b",
                                 "缺年龄锚应报 C26c", "缺身份可渲染外观应报 C26d"))
      and all(_in_warns_append(_vp, c) for c in ("C26a", "C26c", "C26d")))

# ------------------------------------------------- [E*13] 融合规则补载体域（2026-10-10）
# 动机：本包 2026-10-10 从外部包融合 11 条规则，其中可机检的 6 项此前**零执行载体**——
#       "规则写在散文细则里、生成时根本不生效"，只能靠事后人眼发现（正是"越加越不满意"的病根）。
#       本域锁死「规则源文件 ↔ 脚本实现 ↔ 手册登记 ↔ 子码计数 ↔ 自检用例」五处一致，
#       防再次出现"写了规则、却没有会响的检查"。
section("[E*13] 融合规则补载体域（C11b/C12b/C17c/C18f/C20e/C25c 五处互锁）")
_cam_sys = read(os.path.join(PKG, "sd-storyboard-engine", "references", "short-drama-camera-system.md"))
_shot_act = read(os.path.join(PKG, "sd-storyboard-engine", "references", "shot-economy-and-acting.md"))
_seg_spl = read(os.path.join(BASE, "references", "segment-splicing.md"))
_qgr = read(os.path.join(BASE, "references", "quality-gate-review.md"))
check("㊷ 互锁①：validate_prompt.py 实现六个新子码",
      all(c in _vp_txt for c in ("C11b", "C12b", "C17c", "C18f", "C20e", "C25c")))
check("㊷ 互锁②：机检手册已登记六个新子码",
      all(c in _mcm for c in ("C11b", "C12b", "C17c", "C18f", "C20e", "C25c")))
check("㊷ 互锁③：子码计数与手册登记一致（防登记表与计数漂移）",
      f"{SUBCODE_TOTAL} 个子码" in _mcm)
check("㊷ 互锁④：自检含六个新子码的回归用例",
      all(c in _vp_txt for c in ('startswith("C11b")', 'startswith("C12b")', 'startswith("C17c")',
                                 'startswith("C18f")', 'startswith("C20e")', 'startswith("C25c")')))
check("㊷ 互锁⑤：规则源文件在案（景别幅度/过肩几何/假表演/背景锚点/跨项目污染）",
      "景别与表演幅度绑定" in _cam_sys and "过肩镜头几何" in _cam_sys
      and "假表演规避" in _shot_act
      and "背景锚点锁" in _seg_spl
      and "跨项目污染" in _qgr)

# ------------------------------------------------- [E*14] 六维审计补载体域（2026-10-10）
# 动机：用户六维审计（① 前置强制锁 A/B/D ② 段落衔接形式 ③ 出图执行到位 ④ 运镜技法
#       ⑤ 人物遗漏 ⑥ 站位接续）暴露两类根因——
#   ① **机检的「单段假设」**：C1/C2/C3/C4/C17/C24 此前只读文件第一段，而真实交付稿是
#      「提示词组 × N 组」（3 分钟剧 ≈14 段，每段从 00:00 起、≤15s）。后果是合规多段稿
#      **全线误报**（C2 镜头数/ C4 字符/ C24 禁项），且**第 2 段起的人物遗漏抓不到**——
#      正是用户反复反馈的「A 和 B 说话，B 在下一个镜头就不见了」的结构性盲区。
#   ② **「有规则、零机检」**：运镜技法（camera-system §四）、画幅一致性、跨段站位漂移
#      此前只有散文规则、没有会响的检查。
# 纪律：**逐段化 + 新门 = 脚本实现 ↔ 手册登记 ↔ 子码计数 ↔ 自检用例** 四处必须一致。
section("[E*14] 六维审计补载体域（C6b/C17d/C18g~l 逐段化 + 运镜门 · 八处互锁）")
check("㊸ 互锁①：validate_prompt.py 实现八处新子码（C6b / C17d / C18g~l）",
      all(c in _vp_txt for c in ("C6b", "C17d", "C18g", "C18h", "C18i", "C18j", "C18k", "C18l")))
check("㊸ 互锁②：机检手册已登记八处新子码",
      all(c in _mcm for c in ("C6b", "C17d", "C18g", "C18h", "C18i", "C18j", "C18k", "C18l")))
check("㊸ 互锁③：逐段化已落到 C1/C2/C3/C4/C17/C24（防「单段假设」回退）",
      "_split_segments" in _vp_txt and "_segments_time" in _vp_txt and "seg_zw" in _vp_txt
      and "_feed_body" in _vp_txt)
check("㊸ 互锁④：自检含八处新子码的回归用例（含多段稿逐段自查用例）",
      all(c in _vp_txt for c in ('startswith("C6b")', 'startswith("C17d")', 'startswith("C18g")',
                                 'startswith("C18h")', 'startswith("C18i")'))
      and "_t_multi" in _vp_txt)
check("㊸ 互锁⑤：运镜门规则权威在案（§四 逐镜必标运镜 / 固定镜 10% 上限 / 重技法频率上限）",
      "每个镜头必须标注运镜方式" in _cam_sys and "重技法频率上限" in _cam_sys
      and "滑动变焦" in _cam_sys)
check("㊸ 互锁⑥：手册 C6/C17/C18 正文行同步挂上 b/d/g~l 子码（防「表里有、正文无」）",
      "**b** 画幅自相矛盾" in _mcm and "**d** 跨段站位漂移" in _mcm
      and "**g** 镜行未标注运镜" in _mcm and "**l** 重技法名额超限" in _mcm)

# ------------------------------------------------- [E*17] 出稿口径实测修订域（2026-10-12 用户实测 · 三改五互锁）
# 动机：段1《遗嘱头七对峙》+ 段2《头七堂屋争房产》两段实拍复盘，用户三条实测裁定：
#   ① 运镜：原「对话段落不得全程固定」→ 四镜全微运镜，模型把控不住，人物站位/朝向在镜内持续漂移
#      （用户原话「一段有两个这种就够了，剩下的应该是要固定在那聊天」）→ 文戏改「固定为主 · 运镜 ≤2 个/段」
#   ② 视线：站位声明只写身体朝向、不写视线落点 → 三人同镜眼神全部跑偏
#      （用户原话「三个人以上基本上就是乱了」）→ 站位声明必写「视线落点」
#   ③ 段8/段9：约 290 字符固定税、实测没大用 → 未选导演卡时默认不写，美学 ≤15 字并入【画幅风格】
section("[E*17] 出稿口径实测修订域（2026-10-12 用户实测 · 三改五互锁）")

_main_skill = read(os.path.join(BASE, "SKILL.md"))
_feed_skill = read(os.path.join(PKG, "sd-feed-engine", "SKILL.md"))
check("㊽ 互锁①：运镜规则已分文戏/打戏档（2026-10-14 废除15s运镜≤2死名额 · 动静随剧情自然发生）",
      "★ 运镜分档（2026-10-12 用户实测修订 · 文戏 / 打戏分治" in _cam_sys
      and "动静随剧情自然发生" in _cam_sys and "打戏 / 动作段" in _cam_sys)
check("㊽ 互锁②：旧口径「对话段落不得全程固定」已降级为废止说明（不得仍处生效位）",
      "已随本次修订废止" in _cam_sys and "文戏 / 对话段不适用本条" in _cam_sys)
check("㊽ 互锁③：总控法则21④ 视线指派已扩写为「单镜 ≥2 人必写视线落点」",
      "视线指派（★ 2026-10-12 扩写 · 多人同镜硬项）" in _main_skill
      and "视线落点：看向 @某人" in _main_skill)
check("㊽ 互锁④：投喂引擎画风锁契约已改「常规稿不写段8/段9 · 美学 ≤15/30 字并入画幅风格」",
      "常规稿不写段8/段9" in _feed_skill
      and any(x in _feed_skill for x in ("美学短语（≤30 字", "美学短语（≤15 字"))
      and "并入【画幅风格】" in _feed_skill)
check("㊽ 互锁⑤：总控 I 锁段同步登记该路径变更（且保留选卡时仍写段8/9）",
      "2026-10-12 用户实测修订（路径变更）" in _main_skill
      and "仅当用户明确选定导演卡时才落段8/段9" in _main_skill)
# ★ 2026-10-13 措辞同步：C/I 锁升格为强制锁（域 [E*25]）时，段8/段9 触发条件由
#   「未选导演卡」精确化为「用户回『按你的推荐走』/ 未指定具体导演卡」，且「默认路径」改称「路径」。
#   本节互锁④⑤ 的检查串已随之同步，语义未变。

# ------------------------------------------------- [E*18] 粉丝实测修复域（2026-10-13 · 四改八互锁）
# 动机：V7.4 粉丝实测反馈四条（沿革记录）——
#   ① 结尾强行定格与台词冲突（人在说话画面冻住）→ 末镜台词预算 = 镜长 − 1s、末 1 秒禁台词
#   ② 2.5 模型出视频但字数仍限 2000 → 闸门3 按模型分档（2.0: 1900/2000 · 2.5: 2600/3000）
#   ③ 强制禁止项太多 → 段7 极简化为四项（禁字幕/水印/Logo/背景音乐/旁白），长清单按 C19 理论本就有害
#   ④ 资产提示词混入编号/自检/延续备注 + 局部特写带表格文字 + 缺头身比 → 提示词正文纯净四条
section("[E*18] 粉丝实测修复域（2026-10-13 · 四改八互锁）")

_splic = read(os.path.join(BASE, "references", "segment-splicing.md"))
_fmg = read(os.path.join(PKG, "sd-feed-engine", "references", "feed-mode-and-gates.md"))
_gck = read(os.path.join(PKG, "sd-feed-engine", "scripts", "gate_check.py"))
_mads = read(os.path.join(BASE, "references", "model-adapters.md"))
_e18_asa = read(os.path.join(PKG, "sd-asset-engine", "SKILL.md"))
check("㊾ 互锁①：末镜台词静默预算在案（预算 = 镜长 − 1s · 末 1 秒禁台词 · 三个解法）",
      "末镜台词静默预算" in _splic and "末 1 秒（硬定格区）禁台词" in _splic
      and "末镜台词字数预算 = (镜长 − 1 − 标点停顿) × 语速档" in _splic)
check("㊾ 互锁②：闸门3 已按模型分档（文档 + gate_check.py 实现两侧）",
      "Seedance 2.5 放宽到 ≤2600" in _fmg and "w_soft, w_hard = (2600, 3000) if a.model == '2.5'" in _gck)
check("㊾ 互锁③：闸门2 末镜特判在 gate_check.py 落地（budget = hit − 1 + 点名提示）",
      "budget = hit - 1 if is_last else hit" in _gck
      and "定格期被台词占用" in _gck)
check("㊾ 互锁④：段7 禁项极简四项（权威模板 + 长清单禁加理由）",
      "【强制禁止项】画面：禁字幕、禁水印（含 Logo）；音频：禁背景音乐、禁旁白。" in _mads
      and "禁项极简（2026-10-13 粉丝实测修订 · 默认只写四项）" in _mads)
check("㊾ 互锁⑤：资产提示词正文纯净四条（编号/自检延续备注/表格排版/头身比）",
      "提示词正文纯净（2026-10-13 粉丝实测修订）" in _e18_asa
      and "人物提示词主动写头身比" in _e18_asa)

# 三条同源推广断言（2026-10-13 收口）：粉丝反馈不只在权威文件落地，示范稿/模板/姊妹落点须同步
_e18_ra = read(os.path.join(PKG, "sd-real-engine", "references", "render-adapters.md"))
_e18_sbe = read(os.path.join(PKG, "sd-real-engine", "references", "storyboard-example.md"))
_e18_sre = read(os.path.join(refs_dir, "seedance-render-engine.md"))
check("㊾ 互锁⑥：三处示范稿段7 同步极简（旧长清单「禁止角色变形」类串已从示范稿清零）",
      "禁止角色变形" not in _e18_ra and "禁止角色变形" not in _e18_sbe
      and "禁止角色变形" not in _e18_sre
      and "画面：禁字幕、禁水印（含 Logo）；" in _e18_ra
      and "画面：禁字幕、禁水印（含 Logo）；" in _e18_sbe
      and "画面：禁字幕、禁水印（含 Logo）；" in _e18_sre)
_e18_fsk = read(os.path.join(PKG, "sd-feed-engine", "SKILL.md"))
_e18_mcm = read(os.path.join(PKG, "sd-qc-engine", "references", "machine-check-manual.md"))
_e18_sat = read(os.path.join(PKG, "sd-qc-engine", "references", "stage-acceptance-table.md"))
_e18_act = read(os.path.join(refs_dir, "acting-direction.md"))
check("㊾ 互锁⑦：字数分档四处姊妹落点同步（feed SKILL / 机检手册 C4 / 验收表 / 表演文档）",
      all("2.5 ≤2600" in x for x in (_e18_fsk, _e18_mcm, _e18_sat, _e18_act)))
_e18_cpt = read(os.path.join(PKG, "sd-asset-engine", "references", "character-portrait-templates.md"))
check("㊾ 互锁⑧：正文纯净推广到模板骨架（人物骨架主动写头身比 · 2026-10-13 粉丝反馈）",
      "主动写头身比是防「头大身小」的第一道锁" in _e18_cpt)

# ------------------------------------------------- [E*19] 段缝人物进出场域（2026-10-13 · 用户实测反馈）
# 动机：用户实测指出段1（两人对峙）→ 段2（四人围桌）之间「没有任何逻辑的过渡」——
#   包内 C17/C17b/C17c/C17d 全是「同一个人的位置/景别接不接得上」，
#   **没有一条规则管「人数变化」**；C17e 是本缺口的机器载体。
# 纪律：规则（segment-splicing.md §四·补二）+ 总控法则 20·②b + 台账/手册登记 + 机检 C17e，
#   四处缺一即本节 FAIL（防「文档写了、执行时不生效」）。
section("[E*19] 段缝人物进出场域（新增 C17e · 2026-10-13 用户实测）")
_e19_ss = read(os.path.join(PKG, "short-drama-director", "references", "segment-splicing.md"))
_e19_ms = read(os.path.join(PKG, "short-drama-director", "SKILL.md"))
_e19_vp = read(os.path.join(PKG, "short-drama-director", "scripts", "validate_prompt.py"))
_e19_cl = read(os.path.join(PKG, "sd-qc-engine", "references", "continuity-ledger.md"))
_e19_mcm = read(os.path.join(PKG, "sd-qc-engine", "references", "machine-check-manual.md"))

check("㊿ 互锁①：segment-splicing.md 立「§四·补二 段缝人物进出场律」专节 + 四种过渡写法齐备",
      "### 四·补二、段缝人物进出场律" in _e19_ss
      and "画内入画" in _e19_ss and "画外先声" in _e19_ss
      and "空镜转场" in _e19_ss and "末镜行句尾" in _e19_ss)
check("㊿ 互锁②：总控 SKILL.md 法则 20 已扩为 ≥五条铁律，②b「新面孔首现要交代」在案并带 C17e 码",
      "②b **新面孔首现要交代" in _e19_ms
      and "六条铁律" in _e19_ms
      and "`C17e`** 人数变化未交代" in _e19_ms)
check("㊿ 互锁③：validate_prompt.py 实现 C17e（过渡词表 + 名单比对 + 豁免 + 报码文案）",
      "C17E_ENTRANCE_WORDS" in _e19_vp and "C17e 人数变化未交代" in _e19_vp
      and "def _core_people" in _e19_vp and "**`C17e`**" not in _e19_vp)
check("㊿ 互锁④：台账 continuity-ledger.md 登记「新面孔首现要交代」（2b 条）+ 机检手册登记 C17e 行",
      "2b. **新面孔首现要交代**" in _e19_cl
      and "| **C17e** | **人数变化未交代**" in _e19_mcm
      and f"{SUBCODE_TOTAL} 个子码" in _e19_mcm)

# ------------------------------------------------- [E*20] 对话戏节奏与台词密度域（2026-10-13 · 用户实测反馈）
# 动机：用户实测指出三件事——①「台词量太少，这是非常多人反馈的一个问题」；
#   ②「我们现在出的台词更像站桩式对话，一个人说完另一个人说，缺乏快速的正反打」；
#   ③「分镜也很呆板，15 秒切成三四段、每段里就几个词儿，非常呆傻地去执行台词量控制」。
# 根因：包内此前**只有上限、没有下限**（语速档 / 密度表 / 闸门2 / 闸门3 全在防超载）→
#   描述是"必须写"、台词是"可以少写" → 被牺牲的必然是台词；且切镜按"内容块"切而非"回合"切。
# 纪律：规则（shot-economy §五·七 + dialogue-speed-check §一·补三）+ 总控法则 20·②c/⑤ +
#   剧本层过渡（episode-planning §TRANSITION_AS_BEAT）+ 必查清单 + 机检 C27b/c/d，
#   五处缺一即本节 FAIL（防「文档写了、执行时不生效」）。
section("[E*20] 对话戏节奏与台词密度域（新增 C27b/c/d · 2026-10-13 用户实测）")
_e20_sea = read(os.path.join(PKG, "sd-storyboard-engine", "references", "shot-economy-and-acting.md"))
_e20_dsc = read(os.path.join(PKG, "short-drama-director", "references", "dialogue-speed-check.md"))
_e20_ep = read(os.path.join(PKG, "sd-script-engine", "references", "episode-planning.md"))
_e20_chk = read(os.path.join(PKG, "short-drama-director", "references", "prompt-feeding-checklist.md"))

check("㋅ 互锁①：shot-economy-and-acting.md 立「§五·七 对话戏节奏律」"
      "（回合制切镜 + 开口密度下限 + OS/短句化 + 病灶实证表）",
      "## 五·七、对话戏节奏律" in _e20_sea
      and "回合制切镜" in _e20_sea
      and "同一说话人连续占据 ≥2 个完整镜行" in _e20_sea
      and "15 秒 ≥6 次" in _e20_sea
      and "OS（内心独白）是零口型成本" in _e20_sea)
check("㋅ 互锁②：dialogue-speed-check.md 立「§一·补三 台词密度下限」（对话段 ≥2.0 字·秒⁻¹，"
      "空镜/打斗段不设下限）",
      "## 一·补三、 台词密度**下限**" in _e20_dsc
      and "2.0 字·秒⁻¹" in _e20_dsc
      and "空镜段 / 转场段" in _e20_dsc
      and "⛔ 不是\"为加而加\"" in _e20_dsc)
check("㋅ 互锁③：episode-planning.md 立「§ TRANSITION_AS_BEAT 过渡即戏点」"
      "（剧本层造过渡 · 四种类型 · 分镜层只做落地）",
      "TRANSITION_AS_BEAT" in _e20_ep
      and "过渡即戏点" in _e20_ep
      and "动作桥" in _e20_ep and "空镜叙事" in _e20_ep and "声音桥" in _e20_ep
      and "剧本层 = 造过渡" in _e20_ep)
check("㋅ 互锁④：总控 SKILL.md 法则 20 扩为六条铁律 + ②c 过渡归属 + ⑤ 对话节奏在案 + 子码清单登记 C27",
      "六条铁律" in _e19_ms
      and "②c **过渡是剧本层的戏点" in _e19_ms
      and "⑤ **对话戏节奏与台词密度" in _e19_ms
      and "`C27b`** 对话段台词密度" in _e19_ms)
check("㋅ 互锁⑤：必查清单登记 C27 两项（第 29 项对话戏节奏 + 第 30 项台词密度下限 + 第 31 项场次过渡）",
      "| 29 | **对话戏节奏**" in _e20_chk
      and "| 30 | **台词密度下限**" in _e20_chk
      and "| 31 | **场次过渡即戏点**" in _e20_chk)
check("㋅ 互锁⑥：validate_prompt.py 实现 C27b/c/d（段落类型识别 + 密度 + 开口数 + 站桩判据 + 豁免）",
      "C27_DIALOGUE_MARK" in _e19_vp
      and "C27b 对话段台词密度不足" in _e19_vp
      and "C27c 对话段开口次数不足" in _e19_vp
      and "C27d 站桩式对话" in _e19_vp
      and "def _c27_seg_type" in _e19_vp)
check("㋅ 互锁⑦：机检手册登记 C27 主码行（§二 门禁清单）+ C27a~d 进 SUBCODE-Registry 清单",
      re.search(r"^\| C27 \| \*\*对话戏节奏与台词密度下限\*\*", _e19_mcm, re.M) is not None
      and all(c in _e19_mcm for c in ("C27a", "C27b", "C27c", "C27d"))
      and f"{SUBCODE_TOTAL} 个子码" in _e19_mcm
      and "| **C27a~d** |" not in _e19_mcm)
# ── 对话段全面豁免（2026-10-13 用户裁定）──
#   动机：C2/C13/C18j/C18k 是「镜必须少、必须动」这一组判据——正反打的标准形态恰恰相反
#   （固定机位 + 高频切镜换嘴）。文档早有「文戏不受固定上限约束」，但机检未实现，
#   段2 改回合制正反打时被连报 6 条即实证。此处断言「文档口径 ↔ 机检实现」双向对齐。
_e20_cam = read(os.path.join(PKG, "sd-storyboard-engine", "references", "short-drama-camera-system.md"))
check("㋅ 互锁⑧：对话段全面豁免已文档化（shot-economy 豁免表 + camera-system 机检对齐段 + checklist 第 25 项）",
      "对话段全面豁免（2026-10-13 用户裁定" in _e20_sea
      and "机检对齐（2026-10-13 用户裁定）" in _e20_cam
      and "对话段全面豁免（2026-10-13 用户裁定）" in _e20_chk)
check("㋅ 互锁⑨：validate_prompt.py 实现对话段豁免（C2 ÷2s + C13/C18j/C18k 走 _in_dlg）",
      "_dlg_line_ranges" in _e19_vp
      and "def _in_dlg" in _e19_vp
      and "对话段按 ÷2s 放宽以支持正反打" in _e19_vp
      and "_tr_nd = [(s, e, ln) for s, e, ln in tr if not _in_dlg(ln)]" in _e19_vp
      and "_fix_lns_nd = [ln for ln in _fix_lns if not _in_dlg(ln)]" in _e19_vp)

# ── ★ 节奏灵活化（2026-10-13 用户第二轮申明）──
#   动机：用户纠正「**你灵活一点，不要说我说啥就把它完全定死了，这个东西它本身是服务着剧情走的**」；
#   「我**也不知道你为了切而切**，像有一些剧情就**不适合这种来回的切**，**灵活懂吗？是服务剧情的**」。
#   病根：上一轮把规则写成硬指标 —— ①「空镜段不设下限」被读成「空镜禁写台词」，挡掉了
#   「空镜 + 声音先入画」的合法声桥手法；②「同一人不得连续 ≥2 镜独占开口」等三条没有给
#   「该慢的戏」（静场/宣判/留白）留出口；③「全片禁用长镜头」一刀切。
#   纪律：**灵活化必须双向可锁** —— 既要有「默认为主」的硬项，也要有「剧情有理由时走例外 +
#   必须显式标注段落意图」的出口；且总则须上升到总控法则层（否则子技能文档各说各话）。
check("㋅ 互锁⑩：shot-economy 立「★★ 总则：节奏服务剧情，规则不是模板」+ 三条硬指标改为"
      "「适用前提：本段是该有来回的对话戏」+ 总则含剧情性质对照表",
      "★★ 总则：节奏服务剧情，规则不是模板" in _e20_sea
      and "适用前提：本段是\"该有来回\"的对话戏" in _e20_sea
      and "静场对峙 / 宣判 / 留白 / 独白 / 长镜压迫" in _e20_sea
      and "靠沉默和静止更有力" in _e20_sea)
check("㋅ 互锁⑪：shot-economy §五 废除「全片禁用长镜头」一刀切 → 改为四类允许保留 + 写作要求",
      "已废止**" in _e20_sea
      and "允许保留长镜/一镜到底" in _e20_sea)
check("㋅ 互锁⑫：dialogue-speed-check 立「空镜带声是合法且常用的手法」+「总原则」引用块 + "
      "空镜行改为「不设下限，但也不禁言」",
      "空镜带声是合法且常用的手法" in _e20_dsc
      and "但也不禁言" in _e20_dsc
      and "既不强制、也不禁止" in _e20_dsc)
check("㋅ 互锁⑬：总控 SKILL.md 立「法则 20·★ 一切节奏类规则服务剧情，不是模板」（五条要求 · "
      "含禁止把灵活读成可以拍呆）",
      "20·★ **一切节奏类规则服务剧情，不是模板" in _e19_ms
      and "禁止把本条的\"灵活\"读成\"可以拍呆\"" in _e19_ms
      and "空镜带先声是合法且常用的手法" in _e19_ms)
check("㋅ 互锁⑭：必查清单第 32 项「节奏服务剧情」在案（第 29/30 项的前提）",
      "| 32 | **节奏服务剧情**" in _e20_chk)
check("㋅ 互锁⑮：validate_prompt.py 的 C27_NO_DIALOGUE_MARK 词表扩展（静场/留白/氛围段/长镜段/"
      "情绪积累 → 该慢的戏三条全跳过）",
      "静态场" not in _e19_vp
      and "\"静场\"" in _e19_vp
      and "\"留白\"" in _e19_vp
      and "\"氛围段\"" in _e19_vp
      and "\"长镜段\"" in _e19_vp
      and "\"情绪积累\"" in _e19_vp)

# ------------------------------------------------- [E*21] 创意转场手法库域（D 锁 ④ · 2026-10-13 用户追问）
# 动机：用户追问「相似动作 / 前景遮挡 / 形状匹配 / 甩镜 / 闪白 / 画中画 这类转场，
#   我们有没有进行设定？」——实测发现：**结构型衔接（D 锁 ①②③）齐全，但「技巧型转场」这一层缺失**——
#   手法词汇散落在打戏域与 camera-transitions-6types.md，文戏段缝无统一手法库、无大师技巧、无写法示例。
# 纪律：**新能力进包 = 文件存在 + 总控有路由（文件树 + 归属表 + D 锁 ④）+ 文档间互相指认 +
#   计数口径同步（38/48）+ 「按剧情选用非必用」口径在案**，缺一即本节 FAIL。
section("[E*21] 创意转场手法库域（D 锁 ④ · 2026-10-13 用户追问）")
_e21_ctl = read(os.path.join(refs_dir, "creative-transition-library.md"))
_e21_seg = read(os.path.join(refs_dir, "segment-splicing.md"))
_e21_c6 = read(os.path.join(refs_dir, "camera-transitions-6types.md"))
check("ㆂ 互锁①：creative-transition-library.md 在案（文戏六式 + 打戏索引 + 大师技巧辑录）",
      "创意转场手法库" in _e21_ctl
      and "相似动作转场" in _e21_ctl and "形状/图形匹配转场" in _e21_ctl
      and "前景遮挡转场" in _e21_ctl and "甩镜转场" in _e21_ctl
      and "闪白/闪黑转场" in _e21_ctl and "画中画/画框内的画框转场" in _e21_ctl)
check("ㆂ 互锁②：本库「按剧情选用非必用」口径在案（法则 20·★ · 单集 ≤3 处 · 禁为转而转）",
      "转场服务剧情，不是模板" in _e21_ctl
      and "需要时手边有的工具箱" in _e21_ctl
      and "单集 ≤3 处" in _e21_ctl
      and "为转而转" in _e21_ctl
      and "我不是每一段都要用这种比较偏特效一点的转场" in _e21_ctl)
check("ㆂ 互锁③：大师技巧辑录在案（J-cut/L-cut 声先导 + 视线引导 + 时间省略 + 反差错位 + 空间轴线 + 定格抽帧）",
      "J-cut（声先画后）" in _e21_ctl and "L-cut（画先声后）" in _e21_ctl
      and "视线匹配切" in _e21_ctl and "时间省略族" in _e21_ctl
      and "反差与错位族" in _e21_ctl and "空间与轴线族" in _e21_ctl)
check("ㆂ 互锁④：总控 SKILL.md 唯一权威归属表登记「7b 技巧型转场（D 锁 ④）」（★ 新增）",
      "| 7b | **技巧型转场（D 锁 ④）** |" in skill
      and "`references/creative-transition-library.md`（★ 2026-10-13 新增）" in skill)
check("ㆂ 互锁⑤：总控 SKILL.md 文件树挂载 creative-transition-library.md + D 锁由三选一扩为四选一",
      "├── ★ creative-transition-library.md" in skill
      and "### D · 段缝衔接方式四选一" in skill
      and "**④ 技巧型转场（★ 2026-10-13 新增 · 用户追问）**" in skill)
check("ㆂ 互锁⑥：segment-splicing.md（结构化权威）指认 ④ 技巧型在案（分工不替代）",
      "creative-transition-library.md" in _e21_seg)
check("ㆂ 互锁⑦：camera-transitions-6types.md 指认本库为「扩写 + 新增未覆盖手法」",
      "creative-transition-library.md" in _e21_c6)
check("ㆂ 互锁⑧：README 文件清单登记 creative-transition-library 行 + D 锁口径四选一",
      "| 衔接 | `creative-transition-library` |" in read(os.path.join(BASE, "README.md")))
check("ㆂ 互锁⑨：计数口径同步（SKILL 声明 == EXPECTED_REFS · 元规则四）——本库入包后 SKILL 声明须同步",
      f"{EXPECTED_REFS} 份规则库" in skill and EXPECTED_REFS == 48
      and "45 份" not in skill and "37 份" not in skill and "38 份" not in skill)
check("ㆂ 互锁⑩：必查清单登记第 33 项「技巧型转场（D 锁 ④）」（按需 · 非每段必用）",
      "| 33 | **技巧型转场（D 锁 ④）**" in read(os.path.join(refs_dir, "prompt-feeding-checklist.md")))

# ------------------------------------------------- [E*12] 新增能力的「规则化」四互锁域（2026-10-09 用户追问）
# 动机：用户实测指出 —— SHOT_TEXT 卡与出图提示词配套纪律「只有文档、没有规则」：
#   ① SHOT_TEXT 卡在 check_package 零断言、sd-storyboard-engine/SKILL.md 里根本没提（子技能自己不知道有这能力）；
#   ② 出图提示词配套纪律 §4.4 挂总控 references，执行资产的实际入口 sd-asset-engine/SKILL.md 一字未提（不加载）；
#   ③ 剧情分镜格有内容断言但总控归属表无独立归属说明。
# 纪律：**能力进包 = 文件存在 + 子技能入口有规则 + 总控有路由 + 机检有互锁**，四者缺一即本节 FAIL。
section("[E*12] 新增能力「规则化」四互锁域（SHOT_TEXT / 剧情分镜格 / M1 出图三件套）")
_e12_sb = read(os.path.join(PKG, "sd-storyboard-engine", "SKILL.md"))
_e12_sa = read(os.path.join(PKG, "sd-asset-engine", "SKILL.md"))
_e12_sst = read(os.path.join(PKG, "sd-storyboard-engine", "references", "storyboard-sheet-template.md"))
_e12_pdg = read(os.path.join(PKG, "sd-storyboard-engine", "references", "plot-deduction-grid.md"))
_e12_ade = read(os.path.join(refs_dir, "asset-delivery-modes.md"))
check("㊵ SHOT_TEXT 互锁①：总控 SKILL 提及（路由 + 归属表）", "SHOT_TEXT" in skill)
check("㊵ SHOT_TEXT 互锁②：sd-storyboard-engine/SKILL.md 有规则条 + 专节",
      "SHOT_TEXT 分镜线稿卡归属" in _e12_sb and "## 七·二、SHOT_TEXT 分镜线稿卡" in _e12_sb)
check("㊵ SHOT_TEXT 互锁③：模板 §十一 含俯视走位图 + 逐镜卡版式",
      "§十一" in _e12_sst and "俯视" in _e12_sst and "SHOT_TEXT" in _e12_sst)
check("㊵ SHOT_TEXT 互锁④：README 路由提及", "SHOT_TEXT" in readme)
check("㊵ 剧情分镜格 互锁①：文件存在且含「条件必出」",
      os.path.isfile(os.path.join(PKG, "sd-storyboard-engine", "references", "plot-deduction-grid.md"))
      and "条件必出" in _e12_pdg)
check("㊵ 剧情分镜格 互锁②：子技能 SKILL 规则条点名（含条件必出口径）",
      "plot-deduction-grid.md" in _e12_sb and "条件必出" in _e12_sb)
check("㊵ 剧情分镜格 互锁③：总控归属表点名 plot-deduction-grid.md", "plot-deduction-grid.md" in skill)
check("㊵ M1 出图三件套 互锁①：sd-asset-engine/SKILL.md 有交付清单硬纪律",
      "M1 交付三件套" in _e12_sa and "交付不全" in _e12_sa)
check("㊵ M1 出图三件套 互锁②：子技能形态自检含出图提示词齐全性核对",
      "出图提示词齐全性" in _e12_sa)
check("㊵ M1 出图三件套 互锁③：纪律源文件 §4.4 存在且子技能引用",
      "出图提示词配套纪律" in _e12_ade and "asset-delivery-modes.md" in _e12_sa)

# --- ㊶ 角色独立建档与四字段模板（用户明确覆盖旧角色板规则）
_e12_cpt = read(os.path.join(PKG, "sd-asset-engine", "references", "character-portrait-templates.md"))
_e12_asl = read(os.path.join(refs_dir, "asset-spatial-ledger.md"))
_e12_ade = read(os.path.join(refs_dir, "asset-delivery-modes.md"))
_e12_ce = read(os.path.join(refs_dir, "character-extraction.md"))
check("㊶ 角色提示词互锁：四字段模板与独立建档规则在权威文件中明确",
      all(x in _e12_asl for x in ("画幅", "排版结构", "服装与身体材质", "面部特写"))
      and "不做亲缘视觉推导" in _e12_ce
      and "四字段模板" in _e12_ade)

# 2026-10-12 第七轮修正：道具模板补总数声明（与「主图 + 四格板」**同源病灶**）
#   病灶：§二 只写「道具三视角图 + 关键细节特写」→ **无总数声明**，模型可出成 3 格 / 4 格 / 散图 / 5 格
#   现行写法 = 显式总数声明「全图共 4 格」+「不设独立大主图 / 不得出现第 5 格」+ 防重复负向词
#   ⚠️ 与本文件上方「防过度外推」两条并存：道具虽同为 4 格，但**允许格内标注、含细节特写格**，
#      不得据此把角色板的「零文字 + 不出特写格」纪律套到道具图上（§7.11 边界表已登记区分句）
check("㊶ 道具四格 互锁①：道具模板含「全图共 4 格」+「不设独立大主图」+「不得出现第 5 格」+ 防重复负向词",
      "全图共 4 格" in _e12_prop and "不设独立大主图" in _e12_prop
      and "不得出现第 5 格" in _e12_prop and "duplicate view angle panel" in _e12_prop)
check("㊶ 道具四格 互锁②：子技能 SKILL.md 道具行含「全图共 4 格」+ 新增「形态自检⑦ 道具图版式」",
      "全图共 4 格" in _e12_sa and "形态自检⑦ 道具图版式" in _e12_sa)
check("㊶ 道具四格 互锁③：总控 §五 道具执行规范给出四格骨架 + 旧「手持基准」须清零（改「尺寸基准」）",
      "单图四格：正面 / 45°侧视 / 顶部俯视 / 关键细节特写" in _e12_asl
      and "尺寸基准" in _e12_asl and "手持基准" not in _e12_asl)
check("㊶ 道具四格 互锁④：立绘模板 §7.11 边界表登记「道具图同为 4 格」区分句（防与角色板纪律混为一谈）",
      "道具图同为 4 格" in _e12_cpt)
check("㊶ 道具四格 互锁⑤：交付配套纪律 §4.4 道具行含「全图共 4 格」+ 四格枚举（旧「三视角」歧义已清）",
      "全图共 4 格" in _e12_ade and "顶部俯视图 / ④ 关键细节特写" in _e12_ade
      and "不出第 5 格" in _e12_ade)
# 2026-10-12 第七轮（同批）：场景九宫格补**显式**格数声明 —— 与角色板 / 道具同源收口
#   原有「3×3 九宫格」是名称隐含 9 格，非显式总数声明；实测同源风险（模型按加法出第 10 格 / 拆散图）
_e12_sg = read(os.path.join(PKG, "sd-asset-engine", "references", "scene-grid-template.md"))
check("㊶ 九宫格格数 互锁：场景模板含「全图共 9 格，不多不少」显式声明 +「不得出现第 10 格」纪律条",
      "全图共 9 格，不多不少" in _e12_sg and "不得出现第 10 格" in _e12_sg)

# ------------------------------------------------- [E*15] 运行态微核域 → 【2026-10-13 整环移除】
# 用户裁定「彻底删掉微核」。原六互锁（㊹①②③④⑤⑥b）随之下线，改为「移除固化域」。
#
# 移除理由（详见 CHANGELOG `2026-10-13 · 微核整环移除`）：
#   微核的 4 个 `literal` 块（§1 怎么用 / §2 锁速查表 / §5 投喂格式 / §17 生成报告）是
#   `build_core.py` 内的**手写编排文字**，不随全库自动同步。2026-10-13 把 C/I 锁升格为
#   强制锁后，§2《锁速查表》**仍输出已废止口径**（C「不阻塞·按 ③ 走」/ I「可默认」/
#   总括「四锁齐备」），而 §2 又排在**自动抽取的 §3 原文之前**、且被 SKILL.md 指定为
#   「开工先读」→ 执行者读到的第一口径就是过期的，**直接导致锁被跳过**。
#   旧校验（`LITERAL_CHECKS`）只查「名词是否在源中存在」、不查「处置口径是否过期」，拦不住。
#
# 结论：**当「摘要」的位置比原文更靠前时，它的漂移危害 > 没有摘要。** 故取消摘要层，一律读原文。
# 连带移除物：`agent-system-core.md` + `scripts/build_core.py` + 全部引用位点。
# （保留 `subprocess` import——本文件仍用它跑 `validate_prompt.py --self-test`。）
section("[E*15·m] 微核移除固化域（2026-10-13 用户裁定 · 防「摘要层」复活）")

check("㊹m 微核整环移除：包内不得再出现 agent-system-core.md / build_core.py",
      not os.path.exists(os.path.join(BASE, "agent-system-core.md"))
      and not os.path.exists(os.path.join(BASE, "scripts", "build_core.py")))
check("㊹m 总控与 README 均声明「不设摘要层」（约束写进文档，防换人后改回）",
      "不设摘要层" in skill
      and "不设摘要层" in read(os.path.join(BASE, "README.md")))

# ------------------------------------------------- [E*16] 图形化产物与段缝景别承接域（2026-10-11 用户实测反馈）
# 动机（两条实跑反馈）：
#   ① **图形化产物静默跳过**：用户拿修表铺实稿反馈「四宫格的故事板没出」——核查其
#      `修表铺段1/段2` 与官方示范稿后发现：**故事板图与剧情分镜格在实跑中整环未产出**，
#      而全包此前对这两件产物**零断言**。根因不是"忘了写规则"，而是
#      「只有『文戏最小 4 格』这句散文——没有版式名、没有交付清单、也没有会响的检查」：
#      规则不可见，即可被静默跳过。
#   ② **跨段景别落差**：用户问「末帧留一秒拉个全景，下一段切中景会不会很奇怪」——
#      §四 只要求「至少换视角或换景别其一」，于是「全景 → 中景」这类 2 级**反向跳**
#      可合法通过，实测读作跳切。
# 纪律：**新增两条规则 = 规则源 ↔ 脚本实现 ↔ 手册登记 ↔ 自检用例 ↔ 交付清单** 全部在案。
section("[E*16] 图形化产物与段缝景别承接域（2026-10-11 用户实测反馈 · 两域互锁）")

_pfc = read(os.path.join(BASE, "references", "prompt-feeding-checklist.md"))

# ㊺ 图形化产物交付域（故事板图四宫格版式 + 剧情分镜格 · 禁静默跳过）
check("㊺ 互锁①：故事板权威文件给出「版式与格数下限」表（文戏 2×2 四宫格 / 打戏 2×3 六宫格）",
      "2×2 四宫格" in _e12_sst and "2×3 六宫格" in _e12_sst and "版式与格数下限" in _e12_sst)
check("㊺ 互锁②：故事板权威文件 §一 已扩为六条硬规则（含版式下限 + 交付清单必列）",
      "六条硬规则" in _e12_sst and "交付清单必列（禁静默跳过）" in _e12_sst)
check("㊺ 互锁③：子技能 SKILL 有专节（版式表 + 四宫格消歧 + 交付清单格式）并在高频铁律挂线",
      "### 七·一、版式与格数下限" in _e12_sb and "### 七·二、交付清单必列" in _e12_sb
      and "图形化产物必列清单" in _e12_sb)
check("㊺ 互锁④：总控 P3 硬产出与极速直出均写入「图形化交付清单」（不列即禁进 P4）",
      "P3 图形化交付清单" in skill and "禁静默跳过" in skill)
check("㊺ 互锁⑤：「四宫格」两处同名产物已双向消歧（故事板图 vs 剧情分镜格）",
      "四宫格故事板" in _e12_sst and "四宫格故事板" in _e12_pdg and "同名不同物" in _e12_pdg)
check("㊺ 互锁⑥：剧情分镜格文件写入交付清单格式（逐场列 · 不列即未完成）",
      "剧情分镜格：场1 ✅ 四宫格" in _e12_pdg)
check("㊺ 互锁⑦：故事板模板给出文戏 4 格 2×2 四宫格出图范例（含 §6.2b）",
      "### 6.2b 文戏范例" in _e12_sst and "2×2 四宫格" in _e12_sst)

# ㊻ 段缝景别承接域（C18m 八互锁）
check("㊻ 互锁①：规则源在案（segment-splicing §四·补 段缝景别承接律 · 五规则 + 参考必入组）",
      "### 四·补、段缝景别承接律" in _seg_spl and "段落差 = 0 级（同档 · 硬绑定）" in _seg_spl
      and "尾帧参考必进参考组" in _seg_spl)
check("㊻ 互锁②：validate_prompt.py 实现 C18m（9 级阶梯 + 终点/起点景别 + 过渡豁免）",
      all(k in _vp_txt for k in ("C18m", "C18M_LADDER", "_c18m_tail_size",
                                 "_c18m_open_size", "_c18m_bridge")))
check("㊻ 互锁③：机检手册已登记 C18m（C18 行内子码 + 子检查码登记行 + 计数一致）",
      "C18m" in _mcm and "段缝景别落差" in _mcm and f"{SUBCODE_TOTAL} 个子码" in _mcm)
check("㊻ 互锁④：自检含 C18m 四组回归用例（收束后反向收紧报 / 收束后同档不报 / 未收束落差 1 级不报 / 过渡豁免不报）",
      all(k in _vp_txt for k in ("段缝 全景→中景", "末镜收束后同档起手不应报 C18m",
                                 "未收束段缝落差 1 级不应报 C18m",
                                 "写出过渡手段不应报 C18m")))
check("㊻ 互锁⑤：相邻段边界推荐表已加「段缝景别」列 + 规则 7 · 景别阶梯挂跨段指针",
      "段缝景别（末镜终点 → 首镜起点）" in _seg_spl
      and "任意段（景别承接 · 硬性）" in _seg_spl and "跨段承接口径" in _cam_sys)
check("㊻ 互锁⑥：P4 动笔前必查表已挂第 28 项（段缝景别承接 · C18m）",
      "段缝景别承接" in _pfc and "C18m" in _pfc)
check("㊻ 互锁⑧：C7c 站位人物账解析元检查三处互锁（脚本实现 + 手册登记 + 自检用例）",
      "_zw_people_loose" in _vp_txt and "C7c" in _vp_txt and "C7c" in _mcm
      and "站位声明漏 @ 应报 C7c" in _vp_txt and f"{SUBCODE_TOTAL} 个子码" in _mcm)
check("㊻ 互锁⑦：末帧「末 1 秒整秒硬定格 + 前置 0.5 秒收束窗」已标注用户确认（2026-10-12 裁定）",
      "2026-10-12 用户裁定" in _seg_spl and "末 1 秒整秒硬定格" in _seg_spl
      and "尾帧稳定区（= 段缝景别收束窗）" not in _seg_spl
      and "尾帧截图即下段首帧参考图" in _seg_spl)

# ------------------------------------------------- [E*23] 前置锁完整性域
section("[E*23] 前置锁完整性域（D 锁缺位修复 · 2026-10-13）")
# 病灶：全包无「多段任务」判定式 → 执行者可自称「当前非多段任务」合法跳过 D 锁。
# 本域锁死判定式 + 判定时点 + 同批锁完三条，防复发。
check("㊼ 互锁①：总控 §〇 首段写明「多段任务」判定式（目标成片时长 ÷ A 锁单段上限 > 1）",
      "目标成片时长 ÷ A 锁单段上限 > 1" in skill and "多段任务，D 锁必锁" in skill)
check("㊼ 互锁②：判定时点锁死在 P0 立项期（禁以「剧本阶段 / 分镜层」为由推迟）",
      "判定时点 = P0 立项锁定期" in skill and "阶段论 = 漏锁事故的直接成因" in skill)
check("㊼ 互锁③：六道锁同批锁完铁律在案（可分批弹出，但任一批未锁完禁进 P1）",
      "六道锁（〇·0 / 〇·1 / A / B / C / D）须在同一锁定期内一次性锁完" in skill
      and "任一批未锁完禁止进入 P1" in skill)
check("㊼ 互锁④：判定式三处同源（§〇 首段 + 〇节摘要句 + D 锁节，防单点漂移）",
      skill.count("目标成片时长 ÷ A 锁单段上限 > 1") >= 3)

# ------------------------------------------------- [E*24] 剧本引擎阶段② 更名域
section("[E*24] 剧本引擎阶段② 更名域（动漫IP开发 → IP 与角色开发 · 2026-10-13）")
# 病灶：阶段②旧名「动漫IP开发」会让真人项目被误判为动漫项目（用户原话：「这不是动漫 IP 啊」）。
# 本域锁死「新名生效位一致 + 旧名清零 + 形态无关声明在案」，防旧名回流。
_sse_skill = read(os.path.join(PKG, "sd-script-engine", "SKILL.md"))
_sse_ssp = read(os.path.join(PKG, "sd-script-engine", "references", "six-stage-pipeline.md"))
_sse_epp = read(os.path.join(PKG, "sd-script-engine", "references", "episode-planning.md"))
check("㊿ 互锁①：剧本引擎生效位已更名（SKILL 描述/链/路由表/规则表 + 六阶段链 + 分集边界表）",
      "IP 与角色开发" in _sse_skill and _sse_skill.count("IP 与角色开发") >= 4
      and "IP 与角色开发" in _sse_ssp and "IP 与角色开发" in _sse_epp)
check("㊿ 互锁②：旧名已从生效位清零（剧本引擎 SKILL 与六阶段流程不得再出现旧名）",
      "动漫IP开发" not in _sse_skill and "动漫IP开发" not in _sse_ssp
      and "动漫IP开发" not in _sse_epp)
check("㊿ 互锁③：阶段②「形态无关声明」在案（真人/2D/3D/水墨同走一套角色 IP 化流程）",
      "形态无关声明" in _sbip and "动漫化程度 = 0" in _sbip and "真人实拍质感" in _sbip)
check("㊿ 互锁④：STYLE_PROFILE 的「动漫化程度」字段已标注形态锁取值",
      "动漫化程度（形态锁：真人实拍项目填" in _sbip)

# ------------------------------------------------- [E*25] 前置锁默认口子清零域
section("[E*25] 前置锁默认口子清零域（C/I 锁升格为强制锁 · 2026-10-13 用户裁定）")
# 病灶：C 交付形态「未指定默认 ③，不阻塞创作」+ I 画风锁「可默认值锁 · 未指定 = 按默认推荐卡执行」
# 两个口子让执行者"合法"跳过弹卡（写了默认值就不问了），用户全程没有选择权。
# 用户原话：「这个还是没有给我选。」
# 本域锁死「旧口子清零 + 新口径三处同源 + 形态基底改必确认」，防回流。
_mdl_adp = read(os.path.join(BASE, "references", "model-adapters.md"))
_slp = read(os.path.join(BASE, "references", "style-bible", "style-lock-protocol.md"))
_readme_top = read(os.path.join(BASE, "README.md"))
_sae_skill = read(os.path.join(PKG, "sd-asset-engine", "SKILL.md"))
_sfe_skill = read(os.path.join(PKG, "sd-feed-engine", "SKILL.md"))
check("◆1：C 锁旧口子已清零（§〇 摘要句 / C 锁节标题 / 严格·极速模式对照表 C 列 · 含 model-adapters）",
      "C·交付形态未指定时默认" not in skill
      and "未指定默认 ③" not in skill
      and "未指定默认 ③" not in _mdl_adp)
check("◆2：C 锁新口径三处同源（总控 SKILL + model-adapters + README 均标「强制锁 · 未指定 = 停下询问」）",
      "强制锁 · 与 A/B 同规格；未指定 = 停下询问" in skill
      and "强制锁 · 与 A/B 同规格 · 未指定 = 停下询问" in _mdl_adp
      and "未指定 = 停下询问" in _readme_top)
check("◆3：I 锁旧口子已清零（禁「可默认值锁」），新性质「必弹卡锁」两处同源",
      "可默认值锁" not in skill and "可默认值锁" not in _slp
      and "必弹卡锁" in skill and "必弹卡锁" in _slp
      and "禁止在用户未表态时自行按默认推荐卡执行" in skill)
check("◆4：形态基底改必确认 + 旧引导话术清零 + 下游两引擎同步",
      "不问用户 · 自动带出" not in _slp
      and "Step 1 · 影像基底（★ 2026-10-13 用户裁定：**必须确认**" in _slp
      and "画风想要哪一种？不指定我就按默认卡走」" not in _slp
      and "必弹卡锁" in _sae_skill
      and "未选卡且用户未表态 = 停下询问" in _sfe_skill)

# ------------------------------------------------- [E*26] 道具资产锚点域
section("[E*26] 道具资产锚点域（2026-10-13 用户发现「提示词里没有道具的 @ 位」）")
# 病灶：七段式原只有三类行内锚点——@SCN-（场景）/ @CHR-（人物）/ @角色（站位声明），**关键道具无位可放**。
#      全包 @PRP- 仅 1 处命中（production-ledger-handbook.md 台账手册），投喂层字段定义/示例/机检均未采纳；
#      而 validate_prompt.py 的 H8 正则与 ZW_PERSON_RE 早已认 PRP|ITM|PROP 前缀——
#      属「下游已预留、上游无规定」的反向断链；实跑稿里道具只能写镜行括号夹注「（图9）」。
# 裁定：并入既有【场景资产】栏（七段式不增段）——本域锁死「旧两类写法清零 + 三族锚点同源 + 下游两层同步」。
# 用户原话：「场景资产可供艾特、核心人物可供艾特、站位声明也还有艾特，但是道具呢？」
_dlv26 = read(os.path.join(BASE, "references", "asset-delivery-modes.md"))
_spa26 = read(os.path.join(BASE, "references", "asset-spatial-ledger.md"))
_h3a26 = read(os.path.join(BASE, "references", "h3-adapter.md"))
_amr26 = read(os.path.join(PKG, "sd-feed-engine", "references", "asset-mapping-and-rules.md"))
_sst26 = read(os.path.join(PKG, "sd-storyboard-engine", "references", "storyboard-sheet-template.md"))
check("◇1：asset-delivery-modes 的「新稿一律写」清单已含道具（旧「@人名 / @场景名」两类写法不再裸现）",
      "@人名` / `@场景名` / `@道具名`" in _dlv26
      and "新稿一律写 `@人名` / `@场景名`**" not in _dlv26)
check("◇2：三族锚点同源（asset-spatial-ledger 声明 @CHR/@SCN/@PRP + h3-adapter 映射表含道具行）",
      "@CHR/@SCN/@PRP 属性" in _spa26
      and "【场景资产】`@PRP-xxx`（关键道具" in _h3a26)
check("◇3：七段式权威 + 投喂引擎 + 故事板层三处同步（骨架含 @PRP- · 锚定纪律章节在案 · 道具锚定句式落地）",
      "【场景资产】@SCN-xxx（参考图N）" in _mdl_adp and ";@PRP-xxx" in _mdl_adp.replace("；", ";")
      and "道具锚定纪律（2026-10-13 新增 · 治「道具无 @ 位」）" in _mdl_adp
      and "@PRP-道具名（外观以道具参考图锁定；状态" in _sfe_skill
      and "@PRP-道具名（外观以道具参考图锁定；状态" in _amr26
      and "@PRP-" in _sst26)

# ------------------------------------------------- [E*27] 特写占比与分镜字段完整性域
section("[E*27] 特写占比与分镜字段完整性域（2026-10-13 项目体检修复）")
# 病灶（项目体检实测）：
#   ① 「特写比例区间 25%~40%」是硬指标，但 validate_prompt.py 全脚本**零占比断言**——
#      实测某项目 72 镜人物特写仅 19.4%（低于 25% 下限）而机检 PASSED 零告警。
#      与道具 @PRP 同属「上游有规定、下游无断言」。
#   ② 口径歧义：规则只写「物件特写不计入」，**人体局部肢体（手/拳/肩背）是否计入未定义**。
#   ③ 分镜稿九字段**无任何机检**（validate_prompt 只检投喂稿七段式）→ 某项目 1 镜漏写
#      `光影/色调` 两栏，静默影响下行投喂封装。
# 裁定：① 口径写死（局部肢体计入 / 纯物件不计入 / 判定基准在案）；② 补机检 C18n + 自检用例；
#      ③ 故事板引擎增设「逐镜九字段完整性」硬自检。
_camsys = read(os.path.join(PKG, "sd-storyboard-engine", "references", "short-drama-camera-system.md"))
_vprompt = read(os.path.join(BASE, "scripts", "validate_prompt.py"))
_sbstory = read(os.path.join(PKG, "sd-storyboard-engine", "SKILL.md"))
check("◈1：特写占比口径已写死（「人物特写」定义含人体局部肢体 + 「物件特写」定义 + 判定基准 + 机检指向）",
      "「人物特写」定义（2026-10-13 补齐 · 治口径歧义）" in _camsys
      and "或人的身体局部（手、拳、肩背等肢体）" in _camsys
      and "「物件特写」定义" in _camsys
      and "判定基准（机检同此口径）" in _camsys
      and "机检 C18n 兜底" in _camsys)
check("◈2：validate_prompt.py 已补 C18n（常量 + 实现 + docstring 声明 + 自检用例）",
      "CU_RATIO_MIN, CU_RATIO_MAX = 0.25, 0.40" in _vprompt
      and "C18n 人物特写占比" in _vprompt
      and "WARN  C18n 人物特写占比" in _vprompt
      and "# 70f) C18n" in _vprompt
      and "# 70i) C18n" in _vprompt)
check("◈3：故事板引擎已设「逐镜字段完整性」硬自检（九字段齐全 + 不删行 + 说明机检为何抓不到）",
      "交付前硬自检：逐镜字段完整性" in _sbstory
      and "不得整行删掉" in _sbstory
      and "该缺陷**机检抓不到**" in _sbstory)

# ------------------------------------------------- [E*28] 粉丝系统性意见全修域
section("[E*28] 粉丝系统性意见全修域（2026-10-13 · 剧本 5 条 + 分镜 3 条）")
# 病灶（粉丝针对 6.9 版的系统性实测意见，逐条对照 V7.4.18 · 沿革记录）：
#   剧本① 悬念基本归零 / ② 反派零智商·冲突一起当场被反杀 / ③ 结构注水
#        / ④ 主角满级零认知转变·配角工具人 / ⑤ 爽点公式重复→疲劳
#   分镜⑥ 3D 横屏禁平视脸部特写 / ⑦ 微表情要深入补充 / ⑧ 外部标准剧本无润色层
# 诊断结论：8 条里 4 条真缺口 + 1 条「规则层自污染」（R1 速查「不追求人物深度」架空成长地图）。
# 裁定：全修（P0~P3 七条）。
_polish = read(os.path.join(PKG, "sd-script-engine", "references", "external-script-polish.md"))
_sep = read(os.path.join(PKG, "sd-script-engine", "references", "episode-planning.md"))
_six = read(os.path.join(PKG, "sd-script-engine", "references", "six-stage-pipeline.md"))
_sbip = read(os.path.join(PKG, "sd-script-engine", "references", "story-bible-and-ip.md"))
_scriptskill = read(os.path.join(PKG, "sd-script-engine", "SKILL.md"))
_camsys2 = read(os.path.join(PKG, "sd-storyboard-engine", "references", "short-drama-camera-system.md"))
_sbstory2 = read(os.path.join(PKG, "sd-storyboard-engine", "SKILL.md"))
_master = read(os.path.join(BASE, "SKILL.md"))
check("◉1：外部剧本润色层已落地（权威文件 + 边界三禁 + 六件产出 + 回签流程 + 入口三处）",
      "EXTERNAL_SCRIPT_POLISH" in _polish
      and "润色只补「表演层 + 调度层」，严禁触碰「台词层 / 事件层 / 人物层」" in _polish
      and "润色产出物（六件 · 逐件交付）" in _polish
      and "回签流程（强制 · 不得跳过）" in _polish
      and "外来剧本检测与润色层" in _scriptskill
      and "external-script-polish.md" in _master)
check("◉2：R1 速查冲突已修（限定语 + 删「误会」+ 钩子扩 8 类）+ 能力/认知起点约束",
      "不追求「慢热式」人物深度，但人物弧光状态必须逐集可测" in _sep
      and "禁用「误会」" in _sep
      and "钩子类型**用全 8 类**" in _sep
      and "ability_start" in _sbip
      and "cognition_start" in _sbip
      and "MAX_LEVEL_START" in _sbip)
check("◉3：公式去重升全剧配额 + 阶段升级义务 + 基线差异 + 反派能力基线 + 悬念存量配额",
      "全剧同一公式族出现不得超过 3 次" in _sep
      and "阶段升级义务（★ 新增）" in _sep
      and "新鲜度衰减检查（★ 新增）" in _sep
      and "悬念存量配额（★ 2026-10-13 新增" in _sep
      and "反派能力基线（★ 2026-10-13 新增" in _six
      and "首次交手须占上风或全身而退" in _six)
check("◉4：分镜形态适配 + 特写×平视组合禁令 + FACS 形态强制 + 表演三要素自检",
      "形态 → 机位适配（ESTHETIC-BASE-TO-CAMERA" in _camsys2
      and "「人物脸部特写 × 平视正面」是一个" in _camsys2
      and "影像基底感知契约（★ 2026-10-13 新增" in _sbstory2
      and "表演三要素自查（★ 2026-10-13 新增" in _sbstory2
      and "形态强制项（2026-10-13 新增 · 粉丝实测）" in _master)

# ------------------------------------------------- [E*29] 台词拟人化域
section("[E*29] 台词拟人化域（2026-10-13 · 用户实测「台词机械化」全修）")
# 病灶（用户原话：「台词对白还是过于机械化」「可以增加点拟人的称呼，更加口语化」）：
#   根因审计确认——**规则在包里，但全部失效**：
#     R1 唯一的口语化操作规则（acting-direction 坏表演图鉴 8「台词太干净 → 撒碎屑」）
#        被划归「表演层」，剧本阶段必读清单读不到 → 写剧本的人看不到；
#     R2 台词七维诊断是「事后体检工具」（roundtable-review §1.12.4 明文「本框架不改台词」）
#        + 手动命令触发 + 不在 P1 必读清单 → 孤儿权威（与「微核漂移」同构）；
#     R3 规则**全是否定式**，正向供给为零（全包「拟人」「机械化」「腔调」命中 0；
#        「称呼系统」仅 1 处且是未定义字段名）→ 执行者知道"不要机械"却不知"怎么改"；
#     R4 「人物声音卡」有要求、无载体、无校验，且同概念三个版本互不覆盖
#        （§1.8 YAML 偏偏没有称呼字段 → 阶段③建的卡传不到阶段⑤）；
#     R5 下游铁律「台词逐字保留、不得删改」→ 上游写机械了，P3→P4→成片全链路无人能救，
#        且此前**没有任何机检会报警**（无反馈回路）。
# 修复（方案 A · 治本）：新建台词语感唯一权威 + 接入阶段⑤ 过站 + 消三口径分裂 + 补下游探测器 C28。
_nat = read(os.path.join(PKG, "sd-script-engine", "references", "dialogue-naturalization.md"))
_acting2 = read(os.path.join(PKG, "short-drama-director", "references", "acting-direction.md"))
_mcm2 = read(os.path.join(PKG, "sd-qc-engine", "references", "machine-check-manual.md"))
_readme2 = read(os.path.join(BASE, "README.md"))
_vp2 = read(os.path.join(BASE, "scripts", "validate_prompt.py"))
_track2 = read(os.path.join(BASE, "references", "track-routing.md"))
_checklist2 = read(os.path.join(BASE, "references", "prompt-feeding-checklist.md"))
_combat2 = read(os.path.join(PKG, "sd-combat-engine", "references", "combat-rhythm-and-load-guardrails.md"))
check("◐1：台词拟人化引擎已建（权威文件七要件齐全）",
      "台词拟人化引擎（Dialogue Naturalization · ★权威）" in _nat
      and "称呼系统（★ 本包空白 · 最高优先）" in _nat
      and "ADDRESS_LEDGER" in _nat
      and "「撒碎屑」四法" in _nat
      and "机械化认症表" in _nat
      and "台词拟人化过站（执行流程 · 阶段⑤硬产出）" in _nat
      and "【待验证·未实拍】" in _nat
      and "唯一权威" in _nat)
check("◐2：接入剧本引擎（references 表 + 流程链 + description 触发词）",
      "| [references/dialogue-naturalization.md]" in _scriptskill
      and "台词拟人化过站" in _scriptskill
      and "台词口语化、台词拟人化、台词太机械" in _scriptskill)
check("◐3：阶段⑤ 工序与 §6.8 已挂过站指针",
      "★ 本道工序开工前必须先过《台词拟人化过站》" in _six
      and "它给的是「怎么写」" in _six
      and "以 `dialogue-naturalization.md` 为唯一权威" in _six)
check("◐4：声音卡三口径分裂已消（§1.8 YAML 补三字段 + 唯一模板声明）",
      "address_system" in _sbip
      and "avg_line_length" in _sbip
      and "signature_particles" in _sbip
      and "本 YAML 是唯一卡模板" in _sbip)
check("◐5：表演层坏表演图鉴 8 已改指针（消同规则两处口径）",
      "处方已移至 `sd-script-engine/references/dialogue-naturalization.md` §三" in _acting2
      and "避免同一规则两处口径" in _acting2)
check("◐6：下游探测器 C28 已落地（脚本实现 + 手册登记 + 总控分组 + 三处口径）",
      "C28_BOOKISH" in _vp2
      and "C28b 对话段零语气词" in _vp2
      and "**台词机械化探测**（2026-10-13 新增" in _mcm2
      and "台词语感门" in _master
      and "C28a~c 台词机械化" in _readme2
      and "C28a~c 台词机械化" in _track2
      and "台词机械化自检" in _checklist2)
check(f"◐7：子码计数 {SUBCODE_TOTAL} 全链同步（手册 / README / checklist / 打戏库 四处一致）",
      f"{SUBCODE_TOTAL} 个子码" in _mcm2
      and f"子检查码共 {SUBCODE_TOTAL} 条" in _readme2
      and f"子检查码共 {SUBCODE_TOTAL} 条" in _checklist2
      and f"子检查码共 {SUBCODE_TOTAL} 条" in _combat2)
check("◐8：P1 必读清单已补七维诊断与拟人化引擎（消「孤儿权威」）",
      "dialogue-doctor-7d.md`（台词七维诊断 · 定稿前体检）" in _master
      and "dialogue-naturalization.md`（台词拟人化引擎" in _master)

# ------------------------------------------------- [E*30] 规则文件挂载一致性域
section("[E*30] 规则文件挂载一致性域（2026-10-13 · 治「★权威 ≠ 会被读到」）")
# 元缺陷（2026-10-13 元层面反思确立）：
#   包内有三套**各自手工维护、互无断言**的「文件重要性清单」——
#     ① 唯一权威归属表（SKILL.md §一 · 27 行）
#     ② 文件树 ★ 标记（SKILL.md 文件树区）
#     ③ **八阶段强制读取清单（唯一决定实际读不读的）**
#   ①②③ 之间零一致性断言 → **文件可写进①、标上★、画进②，却不在③里，
#   照样「是权威」，只是永远没人读**（静默失效）。实证：台词七维 `dialogue-doctor-7d`
#   与表演层 `acting-direction`（后者自声明「P1 写《角色表演档案》」却无任何读取路径）。
# 修复：SKILL.md 新增《按需规则文件 · 触发条件台账》，把**不在必读清单**的规则文件
#   全部登记触发条件；本域断言「台账 ∪ 必读清单」== 文件系统里的全部 references，
#   防日后新增规则文件漏登记（这是把「静默失效」变成「打包即报警」的关键一环）。
def _refs_abs():
    _out = []
    for _dp, _dn, _fn in os.walk(os.path.join(BASE, "references")):
        for _f in _fn:
            if _f.endswith(".md"):
                _out.append(os.path.relpath(os.path.join(_dp, _f),
                                            os.path.join(BASE, "references")).replace(os.sep, "/"))
    return sorted(_out)

_sm = _master
# 定位串必须带标题标记（"### ★"）——否则会被正文里的同名引用抢先命中
# （2026-10-13 实测：元规则二引用了台账名，导致 find 命中元规则而非台账标题 → 三条断言集体 FAIL）
_lg = _sm.find("### ★ 按需规则文件 · 触发条件台账")
_ledger = _sm[_lg:_sm.find("\n###", _lg)] if _lg > 0 else ""
_rd = _sm[_sm.find("★ 强制读取清单"):_sm.find("自检动作（AI 助手在每阶段开始时执行）")]
_unregistered = [f for f in _refs_abs()
                 if os.path.basename(f) not in _ledger and os.path.basename(f) not in _rd]
check("◑1 台账已建：不在八阶段必读清单的规则文件已全部登记触发条件（漏一个即 FAIL）",
      bool(_ledger) and not _unregistered)
check("◑2 表演层已接进 P3 必读路径（修复前 acting-direction 无任何读取路径）",
      "★表演环：总控 `references/acting-direction.md`" in _rd
      and "《角色表演档案》（每主要角色一份" in _sm
      and "acting-direction.md" in _ledger)
check("◑3 台账含三条铁律（按需≠可读可不读 / 表外不得再有只标★无触发条件 / 判定权在触发条件）",
      "**「按需」≠「可读可不读」**" in _ledger
      and "本表之外不得再存在" in _ledger
      and "判定权在触发条件" in _ledger)
check("◑4 四条元规则已立（一 同概念单一权威 / 二 挂载即生效 / 三 禁令必须配供给 / 四 断言只锁常量）",
      "元规则一（同概念单一权威" in _sm
      and "元规则二（挂载即生效" in _sm
      and "元规则三（禁令必须配供给" in _sm
      and "把这条禁令整句删掉——执行者还知道该怎么做吗" in _sm
      and "元规则四（断言只能锁" in _sm
      and "这个断言里的数字，改了会不会导致别的提交失败" in _sm)
check("◑5 元规则四已落地：份数断言引用 EXPECTED_REFS 常量 + SKILL 无「38 份」残留",
      "38 份" not in skill
      and "48 份规则库" in skill
      and "EXPECTED_REFS" in open(__file__, encoding="utf-8").read()
      and "f\"{EXPECTED_REFS} 份规则库\"" in open(__file__, encoding="utf-8").read())
# ⚠️ 元规则四自洽：本断言的判据串不得以字面形式出现在本文件（否则自我命中）。
#    故用 chr() 拼接构造禁项，避免断言文本本身触发匹配。
_selfsz = open(__file__, encoding="utf-8").read()
_n60 = "6" + "0"
check("◑6 元规则四已落地：断言文案无过时子码数（52 / 59 / 6" + "0 / 64 / 65）",
      all((n + " 子码口径") not in _selfsz for n in ("52", "59", "64", "65"))
      and ("计数 " + _n60) not in _selfsz
      and ("同步为 " + _n60) not in _selfsz
      and (" " + _n60 + "（防") not in _selfsz)
# ◑7 元规则四 · 版本类断言只锁常量（2026-10-14 实测事故：升版 7.4.19 时
#     OLD_VER_RE 排除项仍写死 (?!4\.18) → 新版号被当旧版号误杀套装 6 处文件，
#     且因命中列表截断显示而被「4 条恒红」掩盖）。
#     判据：OLD_VER_RE 的构造必须以 VERSION 为来源，不得出现任何字面版本号。
_oldver_src = "\n".join(l for l in _selfsz.splitlines()
                        if not l.strip().startswith("#")
                        and ("OLD_VER_RE" in l or "_CUR_ESC" in l))
check("◑7 元规则四已落地：OLD_VER_RE 排除项由 VERSION 常量派生（不得写死字面版本号）",
      "%s" in _oldver_src and "_CUR_ESC" in _oldver_src
      and re.search(r"OLD_VER_RE\s*=\s*re\.compile", _oldver_src) is not None)
# ◑8 防回归 · 本套装自身不得命中「旧版本串」断言（历史事故：命中被前 6 条截断掩盖）
_self_hits = [h for h in _bad_old if not h.startswith(("pingshu-", "short-drama-factory",
                                                       "huhe-", "xuanhuan-", "skill-package-",
                                                       "real-combat-"))]
check("◑8 本套装 13 目录零命中「旧版本串」（防命中被截断显示掩盖）",
      not _self_hits, "; ".join(_self_hits[:6]) or "零命中")
# ◑9 防回归 · 豁免词不得「整行放过」版本串（2026-10-14 实测事故：
#     SKILL.md 权威归属表 #19 行写死 `V7.4.18`，因该行同时出现 `CHANGELOG.md`
#     → 被行级豁免词 `CHANGELOG` 放过，断言与 ◑8 均未报警，逃过整个 V7.4.19 升版）。
#     判据：**表格行（以 | 开头）不适用豁免词**——表格是规格区，不是沿革区。
_bad_tbl = []
for p in scan_rule_docs():
    for i, line in enumerate(read(p).splitlines(), 1):
        if line.lstrip().startswith("|") and OLD_VER_RE.search(line):
            _bad_tbl.append(f"{rel(p)}:{i}")
check("◑9 表格行内无旧版本串（豁免词只对沿革行生效，不适用表格 · 修 #19 逃逸）",
      not _bad_tbl, "; ".join(_bad_tbl[:6]) or "零命中")
# ◑12 脚本 docstring 无写死旧版本串（2026-10-14 代码体检修复）：
#   `scan_rule_docs()` 只扫 .md —— scripts/*.py 的 docstring **不在版本断言覆盖范围内**。
#   实测：check_package.py 自己的 docstring 曾写死上一版版本号（升版后漂移），
#   `[A]`/`◑8` 均未报警。→ 补一条「脚本域」断言，把 .py 也纳入。
_SCRIPT_DIR = os.path.join(BASE, "scripts")
_bad_py = []
for _f in sorted(os.listdir(_SCRIPT_DIR)):
    if not _f.endswith(".py"):
        continue
    for i, line in enumerate(read(os.path.join(_SCRIPT_DIR, _f)).splitlines(), 1):
        # 沿革行豁免口径与 .md 域完全一致（VER_ALLOW_RE）——域命名如
        # `[E+] V7.3.0 三项融合域`、`V7.3.9 起正文不再保留历史版本标注` 属合法沿革。
        if OLD_VER_RE.search(line) and not VER_ALLOW_RE.search(line):
            _bad_py.append(f"{rel(os.path.join(_SCRIPT_DIR, _f))}:{i}")
check("◑12 scripts/*.py 无旧版本串（.py 的 docstring 不在 .md 扫描域 · 补逃逸）",
      not _bad_py, "; ".join(_bad_py[:6]) or "零命中")
# ◑13 单一权威 · IDLE_PROP_RE 只定义一次（2026-10-14 代码体检修复）：
#   实测 L761（C16d 段）与 L807（C18c 段）各定义一次，L807 覆盖 L761 →
#   静默丢掉 `拨弄|翻弄|转着` 三词。属元规则一「同概念单一权威」违规。
_vp_lines = read(vp).splitlines()
_idle_defs = [i for i, l in enumerate(_vp_lines, 1)
              if re.match(r"^IDLE_PROP_RE\s*=", l)]
check("◑13 IDLE_PROP_RE 在 validate_prompt.py 中只定义一次（防二次定义覆盖丢词）",
      len(_idle_defs) == 1, f"定义 {len(_idle_defs)} 处：行 {_idle_defs}")
check("◑13 IDLE_PROP_RE 词表覆盖六词（把玩/摩挲/拨弄/把弄/翻弄/转着）",
      len(_idle_defs) == 1 and all(w in _vp_lines[_idle_defs[0] - 1]
                                   for w in ("把玩", "摩挲", "拨弄", "把弄", "翻弄", "转着")),
      _vp_lines[_idle_defs[0] - 1] if _idle_defs else "未找到定义")
# ◑14 单一权威 · C11b/C17c/C19c/C19e 均按段遍历（2026-10-14 代码体检修复静默失明四条）：
#   病灶：① C11b 取 `_tlines[-1]` 只查全文末镜 → 段1~N-1 全漏；
#        ② C17c 用 `re.search` 只取第一个【站位声明】→ 段2+ 全漏；
#        ③ C19c 硬匹配半角 `[镜头1]` → 全角稿整条静默跳过；
#        ④ C19e 用 `[\s\S]*` 贪婪吞到文末 → 镜行正描写被误判为禁止项错位。
check("◑14 C11b 逐段检查末镜（遍历 seg_zw，不得取全文最后一行）",
      "_c11b_miss" in read(vp) and "for (_n, _b, _l, _blk, _ppl, _shots, _dlgs) in seg_zw:" in read(vp),
      "C11b 仍为全文级实现")
check("◑14 C17c 逐段检查站位声明（遍历 seg_zw，不得只取第一个）",
      "_c17c_miss" in read(vp), "C17c 仍为全文首个匹配")
check("◑14 C19c 镜号判定兼容全角（用 SHOT_TAG_RE，不得硬匹配半角）",
      "_shot_no(l) == 1" in read(vp) or "_shot_no(_l) == 1" in read(vp),
      "C19c 仍硬匹配 [镜头1]")
check("◑14 C19e 禁止项有段界（非贪婪 + 截止下一个【栏位标记）",
      "【强制禁止项】([\\s\\S]*?)(?=\\n【|\\Z|```)" in read(vp),
      "C19e 仍贪婪吞到文末")
# ◑15 TIME_RE 第三形态 `N-N秒`（2026-10-14 用户裁定「更宽容」纳入）：
#   打戏/玄幻稿惯用 `0-3秒` 整数秒时码，旧 TIME_RE 只认 MM:SS 与 Xs-Ys → 整篇被当
#   「无时间轴」，C1~C3/C10/C11b/C17~C25 整套镜级判据静默失效（实测 storyboard-board-lite.md
#   只报一句"C1-C3 未识别到时间轴"）。但裸 `N~N秒` 散文极常见 → 必须带守卫 + 紧写判别。
_vp_txt = read(vp)
# 取 TIME_RE 定义块（从 `TIME_RE = re.compile` 到本块结束 `re.I)`）做局部断言，防全文误命中
_time_def = ""
_m = re.search(r"TIME_RE = re\.compile\([\s\S]*?re\.I\)", _vp_txt)
if _m:
    _time_def = _m.group(0)
check("◑15 TIME_RE 含 N-N秒 第三形态（守卫版 · 散文不误判）",
      bool(_time_def) and "(?<=[\\s\\[【\\]】])" in _time_def and "秒" in _time_def,
      "TIME_RE 未含 N-N秒 第三形态或守卫缺失")
check("◑15 parse_time_ranges 已同步三形态解算（防 float(None) 崩）",
      "m.group(9)" in _vp_txt and "m.group(10)" in _vp_txt,
      "parse_time_ranges 缺第三形态分支——N-N秒 会落到 float(None) 崩溃")
check("◑15 紧写判别在案（秒 前不得有 \\s* · 散文判别特征）",
      "紧写判别" in _vp_txt or "紧写" in _vp_txt,
      "缺紧写判别注释——裸 `1~2 秒` 散文会被误当时码")
check("◑15 self-test 含 N-N秒 双向用例（70l 正例 7 组 / 反例散文判别）",
      "TIME_RE 第三形态判别错误" in _vp_txt and "N-N秒 稿应识别到时间轴" in _vp_txt,
      "self-test 缺 70l/70n 用例")
# ◑10 单一权威 · 单段时长口径收口（2026-10-14 外部评审独立指出「四口径并存」）：
#   曾经：SKILL.md §〇.D.⑦=25~30s ／ SKILL.md §二=每组≤15s ／ seedance-render-engine=严格4~15秒
#        ／ 铁律2=每镜10秒 —— 四处并存互不引用，执行时无法判断听谁。
#   裁定：唯一权威 = model-adapters.md（模型契约表 + §5）；其余一律改指针。
_DUR_ALLOW = ("h3-adapter.md",          # H3 独立通道，可写自己的 4~15s
              "machine-check-manual.md",  # 机检手册复述 C1b 口径（登记用途）
              "model-adapters.md")        # 权威本体
# ⚠️ 元规则四：判据只抓「肯定式写死」，放过「否定式引用」。
#    实测踩坑：首版断言把「⚠️ 本节不再写『每组 ≤15s』」这类**否定句**也判红了。
#    修法 = 否定词先行负向匹配（同句内出现「不再/不适用/仅适用/仅）→ 视为引用，放过。
_NEG_NEAR = re.compile(r"不再|不适用|仅适用|不再另写|废止|禁|❌|⚠️")
_bad_dur = []
for _p in scan_rule_docs():
    _r = rel(_p)
    # ⚠️ 只扫本套装（其余技能有独立治理权，不属本包管辖）
    if not _r.startswith(("short-drama-director/", "sd-")):
        continue
    if os.path.basename(_r) in _DUR_ALLOW:
        continue
    for _i, _line in enumerate(read(_p).splitlines(), 1):
        _hard = (re.search(r"每组\s*[≤<]\s*15\s*[s秒]", _line)
                 or "严格控制在 **4 ~ 15 秒**" in _line)
        if not _hard:
            continue
        # 若同句含否定语（该值被明确否定/限定），不算违反
        _seg = re.split(r"[；;。]", _line)
        if any(_hard and _NEG_NEAR.search(_s) for _s in _seg):
            continue
        # 逐段判定：只在「含该值的那个分句」里找否定词
        for _s in _seg:
            if (re.search(r"每组\s*[≤<]\s*15\s*[s秒]", _s)
                    or "严格控制在 **4 ~ 15 秒**" in _s):
                if not _NEG_NEAR.search(_s):
                    _bad_dur.append(f"{_r}:{_i}")
                break
check("◑10 单段时长口径已收口：除权威与 H3 专档外，无文件再「肯定式写死」每组≤15s / 严格4~15秒",
      not _bad_dur, "; ".join(_bad_dur[:6]) or "零命中")
# ◑11 单一权威声明在位（model-adapters.md 必须显式声明自己是时长/时间码唯一权威）
_mad = read(os.path.join(BASE, "references", "model-adapters.md"))
check("◑11 model-adapters.md 声明「单段时长/组数/镜行时间码」唯一权威",
      "唯一权威声明" in _mad and "全包任何其他文件不得再自行写死时长数字" in _mad)

# ------------------------------------------------- [E*31] 资产状态偏离域
section("[E*31] 资产状态偏离域（2026-10-13 · 用户实测「资产图戴头盔 + 提示词夹头盔 = 两个头盔」）")
# 病根（三条规则叠加）：
#   ① 立绘模板把穿戴物写成「配饰（固定不可变更·保留入图）」；
#   ② SET_STATE 只服务「场景」，**人物无状态变体机制**；
#   ③ 换装机制是「跨造型」（A装/B装各出一图），解决不了「同一场戏内摘下来」。
#   → 资产图锁「戴着头盔」、提示词要「夹着头盔」，**无优先级声明** → 模型【叠加】而非【替换】。
_asl2 = read(os.path.join(BASE, "references", "asset-spatial-ledger.md"))
_ma2 = read(os.path.join(BASE, "references", "model-adapters.md"))
_cpt2 = read(os.path.join(PKG, "sd-asset-engine", "references", "character-portrait-templates.md"))
_vp3 = read(os.path.join(BASE, "scripts", "validate_prompt.py"))
_ckl2 = read(os.path.join(BASE, "references", "prompt-feeding-checklist.md"))
check("◒1：CHAR_STATE 人物持续状态变体已建（四类型 + 三条硬规则 + 「锁的是它长什么样、不是它必须在身上」）",
      "CHAR_STATE · 人物持续状态变体" in _asl2
      and "锁定的是「这个东西长什么样」，不是「它必须在身上」" in _asl2
      and "穿戴增减类" in _asl2
      and "半途矛盾" in _asl2)
check("◒2：立绘模板配饰口径已改（旧「固定不可变更」须清零）",
      "配饰（默认锁定 · 可变需声明）" in _cpt2
      and "锁定的是「它长什么样」，不是「它必须在身上」" in _cpt2
      and "配饰（固定不可变更·保留入图）" not in _cpt2)
check("◒3：投喂层「资产偏离声明」三件套已建（§5.0.6）",
      "资产状态偏离声明" in _ma2
      and "以本段提示词为准，覆盖角色参考图" in _ma2
      and "禁项只作兜底，不能替代替换语" in _ma2)
check("◒4：C29 探测器已落地（脚本实现 + 手册登记 + 总控分组 + checklist 四处一致）",
      "C29_DETACH" in _vp3
      and "C29 疑似资产状态偏离未声明" in _vp3
      and "资产状态偏离探测" in _mcm2
      and "资产状态门" in _master
      and "资产状态偏离" in _ckl2)

# ------------------------------------------------- [E*32] 外挂激活回执·子技能零孤儿·跨脚本全链路一致性域
section("[E*32] 外挂激活回执·12子技能零孤儿·C30指纹探针·跨脚本一致性域（2026-10-14 全链路闭环）")

# ◓1 第一招落地：总控 SKILL.md 含【外挂激活回执头】三行规范（激活外挂 / 已读子库 / 本段调用外挂指纹）
check("◓1 总控 SKILL.md 已立【外挂激活回执头】（激活外挂 / 已读子库 / 本段调用外挂指纹）",
      "外挂激活回执头" in _master
      and "激活外挂：" in _master
      and "已读子库：" in _master
      and "本段调用外挂指纹：" in _master)

# ◓2 第二招落地：P0B 必读含 forbidden-zone-whitelist.md；P3 必读废除「只读 SKILL.md + 招式库」截胡话术，挂载 R1/R3 核心灵魂库
check("◓2 P0B 必读已补 forbidden-zone-whitelist.md，P3 必读已挂载真武动力链与玄幻尺度/三层元素库",
      "forbidden-zone-whitelist.md" in _rd
      and "kinetic-chain-11.md" in _rd
      and "defense-evasion-rules.md" in _rd
      and "impact-physics.md" in _rd
      and "core-combat-laws.md" in _rd
      and "xuanhuan-elements-vfx.md" in _rd
      and "grand-scale-domains.md" in _rd
      and "shot-economy-and-acting.md" in _rd
      and "plot-deduction-grid.md" in _rd
      and "SKILL.md + 招式库" not in _rd)

# ◓3 第二招扩展：12 个子技能全部 77 份 references/*.md 零孤儿断言（既在各自子技能 SKILL.md 挂载，也在总控必读或触发台账挂载）
_sub_orphans_own = []
_sub_orphans_main = []
for _sname in SUB_SKILLS:
    _sp = sub_skill_path(_sname)
    if not _sp:
        continue
    _sskill = read(os.path.join(_sp, "SKILL.md"))
    _sref_dir = os.path.join(_sp, "references")
    if not os.path.isdir(_sref_dir):
        continue
    for _rfn in sorted(os.listdir(_sref_dir)):
        if not _rfn.endswith(".md"):
            continue
        if _rfn not in _sskill:
            _sub_orphans_own.append(f"{_sname}/{_rfn}")
        if _rfn not in _rd and _rfn not in _ledger:
            _sub_orphans_main.append(f"{_sname}/{_rfn}")
check("◓3 12 子技能全部 references 均在各自 SKILL.md 挂载（零子包内孤儿）",
      not _sub_orphans_own, "; ".join(_sub_orphans_own[:6]) or "零孤儿")
check("◓3 12 子技能全部 references 均在总控【强制读取清单 ∪ 触发条件台账】挂载（零跨包孤儿）",
      not _sub_orphans_main, "; ".join(_sub_orphans_main[:6]) or "零孤儿")

# ◓4 第三招落地：validate_prompt.py 实现 C30a/b/c/d 外挂指纹与交接探针，且在手册、总控、checklist 同步登记
check("◓4 C30 外挂指纹与交接探针四处互锁（validate_prompt / 机检手册 / 总控分组 / checklist）",
      all(k in _vp3 for k in ("C30a", "C30b", "C30c", "C30d", "C30_SCALE_4", "C30_KINETIC_11"))
      and all(k in _mcm2 for k in ("C30a", "C30b", "C30c", "C30d"))
      and "外挂指纹与交接门" in _master
      and "外挂激活回执与指纹" in _ckl2)

# ◓5 第四招与多段逐段化全链路闭环（防「修A漏B」）：
#    - _c27_shot_span 复用 parse_time_ranges（不硬编码 MM:SS）
#    - gate_check.py 与 build_board_lite.py 均兼容 N-N秒 与全角【镜头N】
#    - machine-check-manual.md §八 不再写「TIME_RE ❌ 不识别 0-3秒」
#    - validate_seedance_segment_map.py 兼容 SEEDANCE_2_5 (30s)
_gc_txt = read(os.path.join(PKG, "sd-feed-engine", "scripts", "gate_check.py"))
_bbl_txt = read(os.path.join(BASE, "scripts", "build_board_lite.py"))
_vssm_txt = read(os.path.join(PKG, "sd-qc-engine", "scripts", "validate_seedance_segment_map.py"))
check("◓5 跨脚本时间轴与逐段化闭环（_c27_shot_span / gate_check / build_board_lite / 手册§八 / 2.5分段门）",
      "parse_time_ranges(line)" in _vp3
      and "GC_TIME_RE" in _gc_txt and "GC_SHOT_NO_RE" in _gc_txt
      and "[\[【]?" in _bbl_txt
      and "❌ **不识别**" not in _mcm2
      and "SEEDANCE_2_5" in _vssm_txt)

# ------------------------------------------------- [E*33] 四大进阶进化能力互锁域（2026-10-14 架构升级）
section("[E*33] 四大进阶进化能力互锁域（sd_core / slice_context / compile_feed / 拉片诊改与看板三导出）")

# ◓6 进化一：sd_core.py 公共解析与状态台账内核存在且自测通过，validate_prompt 支持 --state 对账
_sd_core_p = os.path.join(BASE, "scripts", "sd_core.py")
_r_sdc = subprocess.run([sys.executable, _sd_core_p, "--self-test"], capture_output=True, text=True) if os.path.isfile(_sd_core_p) else None
check("◓6 sd_core.py 公共解析与 project_state.json 状态台账内核在位且 --self-test 通过",
      _r_sdc is not None and _r_sdc.returncode == 0 and "PASSED" in (_r_sdc.stdout or ""),
      (_r_sdc.stdout or _r_sdc.stderr) if _r_sdc else "缺失 sd_core.py")
check("◓6 validate_prompt.py 已接入 --state 跨阶段状态台账对账模式（verify_feed_against_state）",
      "verify_feed_against_state" in _vp3 and "--state" in _vp3)

# ◓7 进化二：slice_context.py 动态原文切片器存在且 P0~P5 全阶段自测通过
_slice_p = os.path.join(BASE, "scripts", "slice_context.py")
_r_slc = subprocess.run([sys.executable, _slice_p, "--self-test"], capture_output=True, text=True) if os.path.isfile(_slice_p) else None
check("◓7 slice_context.py 动态原文切片器在位且 P0~P5 全阶段 --self-test 通过",
      _r_slc is not None and _r_slc.returncode == 0 and "PASSED" in (_r_slc.stdout or ""),
      (_r_slc.stdout or _r_slc.stderr) if _r_slc else "缺失 slice_context.py")

# ◓8 进化三：compile_feed.py P4 自动装配编译器存在且编译产物 100% 过 validate_prompt 与 gate_check
_comp_p = os.path.join(BASE, "scripts", "compile_feed.py")
_r_cmp = subprocess.run([sys.executable, _comp_p, "--self-test"], capture_output=True, text=True) if os.path.isfile(_comp_p) else None
check("◓8 compile_feed.py P4 投喂自动装配编译器在位且 --self-test 双门全过",
      _r_cmp is not None and _r_cmp.returncode == 0 and "PASSED" in (_r_cmp.stdout or ""),
      (_r_cmp.stdout or _r_cmp.stderr) if _r_cmp else "缺失 compile_feed.py")

# ◓9 进化四（上）：多模态拉片诊改协议（quality-gate-review.md §四 12 类实拍废片矩阵 + SKILL /拉片诊改 指令）
_qgr_txt = read(os.path.join(BASE, "references", "quality-gate-review.md"))
check("◓9 多模态拉片诊改协议在案（quality-gate-review.md §四 12 类症状矩阵 + SKILL /拉片诊改 路由）",
      "多模态拉片诊改协议" in _qgr_txt
      and "十二类实拍高频废片症状" in _qgr_txt
      and "/拉片诊改" in _master
      and "单组时长突破 15 秒" not in _qgr_txt)

# ◓10 进化四（下）：build_board_lite.py 支持一键导出 SRT 字幕 / 剪辑时间线 CSV / API 载荷 JSON 且 --self-test 通过
_bbl_p = os.path.join(BASE, "scripts", "build_board_lite.py")
_r_bbl = subprocess.run([sys.executable, _bbl_p, "--self-test"], capture_output=True, text=True) if os.path.isfile(_bbl_p) else None
check("◓10 build_board_lite.py 支持一键导出 SRT/CSV/JSON 且 --self-test 通过",
      _r_bbl is not None and _r_bbl.returncode == 0 and "PASSED" in (_r_bbl.stdout or "")
      and all(k in _bbl_txt for k in ("exportSRT()", "exportTimelineCSV()", "exportPayloadJSON()", "--export-srt", "--export-csv")),
      (_r_bbl.stdout or _r_bbl.stderr) if _r_bbl else "build_board_lite 自测失败")

# ------------------------------------------------- [E*34] Lubezki×Deakins 物理运镜·光学锁焦·解剖微表·阴面取景融合域（2026-10-14 粉丝 shotlist-builder 吸收）
section("[E*34] Lubezki×Deakins 物理运镜·光学锁焦·解剖微表·阴面取景融合域（shotlist-builder 四大绝活吸收）")

_cam_sys_34 = read(os.path.join(PKG, "sd-storyboard-engine", "references", "short-drama-camera-system.md"))
_act_dir_34 = read(os.path.join(BASE, "references", "acting-direction.md"))
_lgt_af_34 = read(os.path.join(BASE, "references", "lighting-and-antifake.md"))
_eng_cl_34 = read(os.path.join(PKG, "sd-feed-engine", "references", "engineering-language-cleanup.md"))
_cmp_fd_34 = read(os.path.join(BASE, "scripts", "compile_feed.py"))

check("◓11 物理运镜与光学锁焦规程在案（10~15厘米物理限位 / 呼吸微动随动构图 / 单镜分阶段情绪运镜 / 85mm F1.4 锁焦 / 0.3~0.5秒闪切）",
      all(k in _cam_sys_34 for k in (
          "Lubezki × Deakins 物理运镜与光学锁焦规程",
          "10~15 厘米",
          "主动跟随角色脸部运动",
          "单镜内分阶段情绪运镜",
          "85mm",
          "F1.4",
          "0.3~0.5 秒"
      )))

check("◓12 解剖级微表情目录·台词三拍呼吸·焦外听者 0.3~0.5 秒错峰反应在案",
      all(k in _act_dir_34 for k in (
          "解剖级微表情目录",
          "咬肌（masseter）",
          "台词前 / 中 / 后三拍呼吸律",
          "焦外听者非静止与 0.3~0.5 秒错峰反应律"
      )))

check("◓13 阴影侧取景（shadow side）与纯实用光防蓝光色溢（blue spill）及 60:30:10 色彩配比在案",
      all(k in _lgt_af_34 for k in (
          "阴影侧取景（Shadow-Side Shooting）",
          "shadow side",
          "practicals",
          "blue spill",
          "60:30:10"
      )))

check("◓15 D锁首项独立弹出「① 末帧定格承接」且清零旧「①+② 默认组合」捆绑残留",
      "① 末帧定格承接" in skill and "①+② 为连续剧情多段的默认组合" not in skill and "禁止合并为①+②" in skill)
_dpl = read(os.path.join(_sb_dir, "director-param-library.md"))
_spb = read(os.path.join(_sb_dir, "style-prefix-blocks.md"))
check("◓16 画风锁参数库与成品块已补齐路阳+国漫3D仙侠/游戏CG/3D进阶水墨/东方神话3D等 14 张主力卡完整 11 槽位",
      all(k in _dpl and k in _spb for k in ("徐克", "王家卫", "路阳", "袁和平", "乌尔善", "张艺谋", "朴赞郁", "大卫·芬奇", "罗杰·狄金斯", "MAPPA", "国漫3D仙侠", "暗黑神话游戏CG", "国漫3D进阶水墨", "东方神话3D奇幻")))
_sbl_txt = read(os.path.join(BASE, "references", "storyboard-board-lite.md"))
check("◓17 看板契约与 model-adapters 已清除「不另写文字描述/P2.5空壳占位」误导并强制挂接 sd-asset-engine 三模板",
      "character-portrait-templates.md" in _sbl_txt and "scene-grid-template.md" in _sbl_txt and "prop-template.md" in _sbl_txt
      and "不另写文字描述" not in _mdl_adp)
check("◓18 运镜动静随剧情自然发生锁：废除「其余镜头一律写固定」死名额 + C18j非打戏放宽至0.85防误杀",
      "其余镜头一律写固定" not in _cam_sys
      and "_c18j_ratio_cap = CAM_FIXED_RATIO_MAX if _combat_on(text, combat) else 0.85" in _vp3)
_ac_p = os.path.join(BASE, "scripts", "audit_contract.py")
_r_ac = subprocess.run([sys.executable, _ac_p, "--self-test"], capture_output=True, text=True) if os.path.isfile(_ac_p) else None
check("◓19 全流程交付契约与权威源核销器 audit_contract.py 在位且 --self-test 通过（联动 validate_prompt C31 与 SKILL 三防铁律）",
      _r_ac is not None and _r_ac.returncode == 0 and "PASSED" in (_r_ac.stdout or "")
      and "C31" in _vp3 and "audit_contract.py" in _master,
      (_r_ac.stdout or _r_ac.stderr) if _r_ac else "缺失 audit_contract.py")
check("◓20 全能参考极简 @ 铁律（禁二次介绍外观 C26e）+ 随身道具全程 @ 跟随铁律（C26f）在案且互锁",
      "C26e" in _vp3 and "C26f" in _vp3 and "严禁在后面二次介绍" in _mdl_adp and "随身道具全程 @ 跟随铁律" in _mdl_adp)
check("◓21 实测拉片六条死律（禁比喻 C20c / 单人镜禁点名他角 C20f / 禁多重视线 C20g / 群像朝向 C20h / 跨窗递伞穿模与开合态锁 C20i / 悬空局部词 C20j）在案且互锁",
      all(k in _vp3 for k in ("C20f", "C20g", "C20h", "C20i", "C20j", "如钟", "伞尖悬在")) and "5.0.4b 实测拉片" in _mdl_adp and "文戏道具物理因果链与 AIGC 反穿模剧本设计铁律" in _epp)
check("◓22 xuanhuan-combat-director V2.6.0 Ultimate 全量继承与机检闭环（C2支持打戏2~3s细切 / C30a四件套4维全齐AND三层元素 / C30b法武合一11环动力链 / C30e禁相持架招 / C30f禁假攻击 / C30g四收束协议A~D / C30i中全景禁90°正侧拍）",
      all(k in _vp3 for k in ("C30_SCALE_FRAME", "C30_SCALE_MACRO", "C30_SCALE_REF", "C30_SCALE_TINY", "C30e", "C30f", "C30g", "C30i", "_is_cmb_seg"))
      and "xuanhuan-combat-director V2.6.0 Ultimate 全量 9 份库强制必读" in skill)
check("◓14 投喂转译表与 compile_feed.py 遵循 C20m 零默认摄影机理论废话注入互锁",
      "Lubezki × Deakins 物理运镜与光学锁焦转译表" in _eng_cl_34
      and "optics_and_camera_lock" in _cmp_fd_34 and "C20m" in _cmp_fd_34)

_cil_23 = read(os.path.join(PKG, "sd-combat-engine", "references", "combat-iron-laws.md"))
_r1c_23 = read(os.path.join(PKG, "sd-real-engine", "references", "r1-combat-core.md"))
_wkw_23 = read(os.path.join(_sb_dir, "examples", "demo-feed-wkw-15s.md"))
_xuk_23 = read(os.path.join(_sb_dir, "examples", "demo-feed-xuke-15s.md"))
_sbe_23 = read(os.path.join(PKG, "sd-real-engine", "references", "storyboard-example.md"))
check("◓23 全包消除「补丁打补丁/左右互搏」与「独立包没通电」闭环（铁律24禁比喻 / R1定格与C11b打通 / 5份示例清零二次复述 / gate_check兼容###段N / C25d-e与C30j-l通电 / CLI高危硬阻断）",
      "严禁文学比喻" in _cil_23 and "如活物" not in _cil_23
      and "定镜收束" in _vp3 and "「定格」与「定镜收束」分工铁律" in _r1c_23
      and "外观以场景参考图锁定：" not in _wkw_23 and "外观以场景参考图锁定：" not in _xuk_23
      and "不另写文字描述" not in _sbe_23
      and "unit_hdr_re" in _gc_txt
      and all(k in _vp3 for k in ("C25d", "C25e", "C30j", "C30k", "C30l", "FATAL_WARN_PREFIXES", "_is_combat_plugin")))

check("◓24 火山方舟官方（Seedance 2.0/2.5）与 GitHub 五大深水区破局规程在案（四格板裁单图与≥4人Group-First合图 / 每镜句尾环境微锁 / 前删6帧后删1帧与白模中转 / 全模态参考槽与同音字注音 / 原生语速与后期倍速解耦）",
      "5.0.4c 火山方舟官方" in _mdl_adp
      and "Group-First I2V" in _mdl_adp
      and "Shot-Level Lock Tail" in _mdl_adp
      and "前删 6 帧 + 后删 1 帧" in read(os.path.join(BASE, "references", "segment-splicing.md")))

# ================================================================
# [E*36] 画风锁「选卡表 / 引擎 / 参数库」三方对账域（2026-10-15 Agent 修复）
# ================================================================
# 动机：2026-10-14 的 n 版用「加 4 张国漫3D 卡」的方式补卡，却**顶掉了原有 4 张卡**
#       （皮克斯 / 迪士尼经典 / 皮埃尔·孔切·平面插画 / Nelagraphs·长条漫画风），
#       并把 T8 家族缩编（宫崎骏 / 京阿尼 掉出家族）、参数库重复编号 + 「其余 N 组」算错。
#       **全程无任何断言覆盖** —— 换卡 / 漏族 / 数字漂移全靠人工体检才发现。
# 本域把「卡数 / 编号 / 家族归属 / 章节号 / 算式」全部变成真断言。
section("[E*36] 画风锁三方对账域（选卡表 / 推荐引擎 / 参数库 · 2026-10-15 补）")

_sb = os.path.join(BASE, "references", "style-bible")
_cat = read(os.path.join(_sb, "director-style-catalog-74.md"))
_lad = read(os.path.join(BASE, "scripts", "style-lock-ladder.py"))
_pro = read(os.path.join(_sb, "style-lock-protocol.md"))
_par = read(os.path.join(_sb, "director-param-library.md"))
_mtx = read(os.path.join(_sb, "style-fit-and-combat-matrix.md"))

# ---- ① 选卡表：卡数自洽 + 编号唯一 + 停用号位声明 ----
# ⚠️ 卡名单元格可能形如 `**国漫3D仙侠**（玄机/凡人/仙逆系）`，故只强约束「行首是编号 + 至少有第 2 列」，
#    不把卡名内部结构写进正则（写死了会漏掉带括号/斜杠的卡，误报「表头 N 实际 M-7」）。
_cat_rows = re.findall(r"^\|\s*(\d{1,2})\s*\|\s*([^|]+?)\s*\|", _cat, re.M)
_cat_nos = [int(n) for n, _ in _cat_rows]
_cat_names = [re.sub(r"[\s*]", "", nm) for _, nm in _cat_rows]
_cat_total = re.search(r"导演风格候选库（(\d+) 组）", _cat)
_cat_total = int(_cat_total.group(1)) if _cat_total else -1
check("◔1 选卡表卡数自洽：实际行数 == 标题声称组数（防「表头写 N、实际 M」）",
      len(_cat_nos) == _cat_total and _cat_total > 0,
      f"标题称 {_cat_total} 组 · 实际 {len(_cat_nos)} 行")
check("◔2 选卡表编号唯一无重复（防顶号 / 重号）",
      len(set(_cat_nos)) == len(_cat_nos),
      "重号: " + ", ".join(str(x) for x in sorted({n for n in _cat_nos if _cat_nos.count(n) > 1})))
check("◔3 已停用号位 67 / 70 不得再出现在表内，且停用说明在案",
      67 not in _cat_nos and 70 not in _cat_nos
      and "67 / 70 两个号位已停用" in _cat)
check("◔4 四张补回卡（皮克斯 / 迪士尼经典 / 皮埃尔·孔切·平面插画 / Nelagraphs·长条漫画风）"
      "以新号位 73~76 在位",
      all(k in _cat for k in ("皮克斯", "迪士尼经典", "皮埃尔·孔切 / 平面插画", "Nelagraphs / 长条漫画风"))
      and all(str(n) in [str(x) for x in _cat_nos] for n in (73, 74, 75, 76)))
check("◔5 宫崎骏 / 京阿尼 不再作为可选项（表行内已无这两张卡）",
      not any(("宫崎骏" in nm or "京阿尼" in nm) for nm in _cat_names)
      and "宫崎骏" in _cat)   # 卡名只允许出现在「停用说明」里，作为沿革锚点

# ---- ② 引擎与文档 T 族表双向一致（成员 + 星级）----
_eng = {}
for _m in re.finditer(r'\((\d+),\s*"([^"]+)",\s*T(\d),\s*(\d),\s*(\d),', _lad):
    _no, _nm, _f, _a, _b = _m.groups()
    _eng[_nm] = (f"T{_f}", int(_a), int(_b))
_doc = {}
for _line in _pro.splitlines():
    _mm = re.match(r"^\|\s*\*\*(T\d)\*\*\s*\|[^|]*\|[^|]*\|\s*(.+?)\s*\|\s*$", _line)
    if _mm:
        # ⚠️ 分隔符是「空格·空格」，而卡名内部的 · 两侧无空格（罗杰·狄金斯 / 韦斯·安德森 / 吕贝·贝松）
        #    —— 若只按 `·` 切会把这类卡名腰斩，误报「文档独有 安德森 / 林奇 / 狄金斯」。
        for _chunk in re.split(r"\s+·\s+", _mm.group(2)):
            _chunk = _chunk.strip()
            if not _chunk:
                continue
            _parts = _chunk.rsplit(" ", 1)
            if len(_parts) == 2 and re.fullmatch(r"\d/\d", _parts[1]):
                _doc[_parts[0].strip()] = (_mm.group(1), int(_parts[1][0]), int(_parts[1][2]))
check("◔6 引擎 STYLES 与文档 T 族表双向一致（成员集合 + 家族 + 打斗★/特效★）",
      _eng == _doc,
      f"引擎独有: {sorted(set(_eng) - set(_doc))} ｜ 文档独有: {sorted(set(_doc) - set(_eng))} ｜ "
      f"不一致: {[(k, _eng[k], _doc[k]) for k in sorted(set(_eng) & set(_doc)) if _eng[k] != _doc[k]]}")
check("◔7 宫崎骏 / 京阿尼 已从推荐引擎 STYLES 与 AFFINITY 摘除（防「表里没有、引擎还能推」）",
      "宫崎骏" not in _lad and "京阿尼" not in _lad)

# ---- ③ 参数库：章节号唯一 + 补录算式自洽 ----
_par_heads = re.findall(r"^##\s*([一二三四五六七八九十]+)\s*、", _par, re.M)
check("◔8 参数库章节号唯一（防「十二/十三/十四 各出现两次」造成引用歧义）",
      len(set(_par_heads)) == len(_par_heads),
      "重复编号: " + ", ".join(sorted({h for h in _par_heads if _par_heads.count(h) > 1})))
_rest = re.search(r"其余\s*(\d+)\s*组的扩展补录模板", _par)
_rest = int(_rest.group(1)) if _rest else -1
_main_cards = len(re.findall(r"^\|\s*\*\*\d+ [^|]+\|\s*T\d\s", _par, re.M))
check("◔9 参数库补录算式自洽：其余 N == 选卡表卡数 − 已参数化主力卡数",
      _rest == _cat_total - _main_cards and _main_cards > 0,
      f"其余 {_rest} 组 vs 实算 {_cat_total} − {_main_cards} = {_cat_total - _main_cards}")

# ---- ④ 跨文件数字唯一 + 红线 2 交叉引用 ----
check("◔10 全包不得残留「72 组」旧口径（选卡表已 74 组）",
      "72 组" not in _pro + _mtx + _par + read(os.path.join(BASE, "SKILL.md"))
      and "72组" not in read(os.path.join(_sb, "director-style-catalog-74.md")),
      "仍有文件写 72 组")
check("◔11 model-adapters 保留《素材接线单》红线 2「图号双向一致」的就地交叉引用",
      "红线 2" in _mdl_adp and "双向一致" in _mdl_adp)
check("◔12 题材矩阵两表声明数 == 实际行数（防「称 24 组实 26 行」）",
      "筛出的 26 组" in _mtx and "不适合打戏的风格（16 组" in _mtx)

# ---- ⑤ recommend 引擎（题材→候选池）与目录对账（2026-10-15 补 · 防路由静默漏推/幽灵卡）----
#   背景：recommend 是独立原型，check_package 此前只校验 ladder，致它相对目录悄悄漂移而无人发现：
#   #30 挂成押井守（目录 #30=铃木敏郎，押井守实为 #28）、#55 人名错、路由引用 15/17/21/35 却查无此卡。
#   本组把 recommend 的「编号唯一 / 路由引用可达 / 编号不超目录」变成真断言。
#   ✅ #61 歧义已于 2026-10-15 裁定：目录 #61=斯文·尼奎斯特（#52~#61 为摄影大师区块，锡兰不在目录），
#      引擎三处（ladder/protocol/recommend）+ 矩阵 + validate_prompt C23 全部由「锡兰」改「斯文·尼奎斯特」；
#      并新增 ◔16（ladder 卡名↔目录同号位一致）堵住这类「引擎↔目录卡名」漂移。
_rec = read(os.path.join(BASE, "scripts", "style-lock-recommend.py"))
_rec_nums = [int(n) for n in re.findall(r'^\s*\((\d+),\s*"[^"]+",\s*\d,\s*\d,', _rec, re.M)]
check("◔13 recommend 引擎 STYLES 编号唯一无重复",
      len(set(_rec_nums)) == len(_rec_nums),
      "重号: " + ", ".join(str(x) for x in sorted({n for n in _rec_nums if _rec_nums.count(n) > 1})))
_route_ref = set()
# ⚠️ 必须含逗号（≥2 个编号）才算路由列表——否则会把代码里的数组索引 best[0]/s[2] 误当路由。
for _mm in re.finditer(r'\[(\d+(?:\s*,\s*\d+)+)\]', _rec):
    for _x in _mm.group(1).split(","):
        _x = _x.strip()
        if _x.isdigit():
            _route_ref.add(int(_x))
_miss_route = [n for n in sorted(_route_ref) if n not in _rec_nums]
check("◔14 recommend 引擎 GENRE_ROUTES 引用的编号都存在于 STYLES（防「路由查无此卡」静默漏推）",
      not _miss_route, "路由引用但 STYLES 缺失: " + ", ".join(map(str, _miss_route)))
_oob_rec = [n for n in _rec_nums if n not in set(_cat_nos)]
check("◔15 recommend 引擎 STYLES 编号都在选卡表目录内（防引用目录外幽灵卡）",
      not _oob_rec, "目录外编号: " + ", ".join(map(str, _oob_rec)))

# ---- ⑥ ladder STYLES 卡名 ↔ 选卡表目录同号位一致（2026-10-15 补 · 堵 #61 类漂移）----
#   病根：◔6 只校验 ladder↔protocol，从没校验「ladder 卡名 ↔ 目录卡名」→ #61 引擎长期写「锡兰」
#   （目录实为「斯文·尼奎斯特」，且锡兰根本不在 74 卡目录内）而无人发现。本断言把「引擎每个号位的
#   卡名必须能在目录同号位对上」变成真断言。宽松匹配容纳简称：芬奇=大卫·芬奇 / 押井守动画向⊃押井守。
_cat_map = {int(n): re.sub(r"[\s*]", "", nm) for n, nm in _cat_rows}
_lad_pairs = {int(_m.group(1)): _m.group(2)
              for _m in re.finditer(r'\((\d+),\s*"([^"]+)",\s*T\d,\s*\d,\s*\d,', _lad)}
def _name_ok(a, b):
    a = re.sub(r"[\s·]", "", a or ""); b = re.sub(r"[\s·]", "", b or "")
    return (not a or not b) or a == b or a in b or b in a or a[:2] == b[:2]
_name_drift = [(n, nm, _cat_map[n]) for n, nm in _lad_pairs.items()
               if n in _cat_map and not _name_ok(nm, _cat_map[n])]
check("◔16 ladder STYLES 卡名与选卡表目录同号位一致（堵 #61「引擎锡兰 vs 目录斯文·尼奎斯特」类漂移）",
      not _name_drift,
      "卡名漂移: " + "; ".join(f"#{n} {nm}≠{c}" for n, nm, c in _name_drift))

# ---------------------------------------------------------------- 汇总
print()
print("-" * 62)
if FAILED:
    print(f"[-] {len(FAILED)} 项未通过：")
    for f in FAILED:
        print(f"      · {f}")
    sys.exit(1)
print(f"[+] 全部检查通过（现行版本 V{VERSION} · references {len(refs)} 份 · "
      f"{len(SUB_SKILLS)} 子技能 · 全包扫描 {len(scan_md_files())} 个 Markdown）")
