#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V6.9 语义回归检查（最小集）：
① 可灵：只能出现在 LEGACY/移除声明行，不得作为正式支持模型
② 角色资产：CURRENT 标准只能是 4 View（"三视图"仅允许出现在 LEGACY/历史说明行）
③ Prompt 格式命名：禁止"八段式/六栏/九栏"；七段式定义与接续状态尾行口径必须存在
④ LEGACY：V3 空间系统与 CHANGELOG 必须带 LEGACY 标记
⑤ README/SKILL：版本号与 Seedance 2.5/2.0 关键产品规则一致
⑥ 场景拼接图口径；⑦ 首尾帧仅限 2.5；⑧ validate_prompt 出稿门禁
⑨ V6.9：segment-splicing / vo-os-weaving 两新库 + C14 + SKILL 〇节 D 锁
⑩ V6.9 修订：C15 拉伸凑时门（时长由内容倒推，禁拉伸凑满剧本标注）+ 法则 17 禁拉伸条款
⑰ 规则自洽门：被废止示范句仅允许出现在警示语境（示范句验证纪律 · 治"规则层产毒"）
⑱ V6.9.8：MiniMax H3 格式支线（h3-adapter.md / SKILL 三选项与法则 25 / model-adapters 特性行 / README / validate_prompt H1~H12）
外加原有静态检查：SKILL frontmatter、references 完整性。"""
import os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILED = []

def read(rel):
    with open(os.path.join(BASE, rel), "r", encoding="utf-8") as f:
        return f.read()

def scan_md_files():
    out = []
    for root, _dirs, files in os.walk(BASE):
        for fn in files:
            if fn.endswith(".md"):
                out.append(os.path.join(root, fn))
    return out

def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(name)

# ---------- 原有静态检查 ----------
skill = read("SKILL.md")
check("SKILL.md frontmatter name", "name: short-drama-director" in skill)
refs = [f for f in os.listdir(os.path.join(BASE, "references")) if f.endswith(".md")]
check("references 规则库完整（41 份）", len(refs) == 41, f"实际 {len(refs)} 份")

# ---------- ① 可灵残留 ----------
KLING_OK = re.compile(r"LEGACY|不再|已移除|历史|移除可灵|去可灵")
bad_kling = []
for p in scan_md_files():
    for i, line in enumerate(read(os.path.relpath(p, BASE)).splitlines(), 1):
        if "可灵" in line and not KLING_OK.search(line):
            bad_kling.append(f"{os.path.relpath(p, BASE)}:{i}")
check("① 可灵不作为正式支持模型（仅 LEGACY/移除声明行可提及）", not bad_kling, "; ".join(bad_kling[:5]))
check("① model-adapters 含可灵 LEGACY 声明", "LEGACY·可灵 (Kling)" in read(os.path.join("references", "model-adapters.md")))

# ---------- ② 4 View 口径 ----------
VIEW_OK = re.compile(r"LEGACY|旧称|旧「|历史")
bad_view = []
for p in scan_md_files():
    rel = os.path.relpath(p, BASE)
    if rel.startswith("CHANGELOG"):  # 历史沿革文件整体已带 LEGACY 声明
        continue
    for i, line in enumerate(read(rel).splitlines(), 1):
        if "三视图" in line and not VIEW_OK.search(line):
            bad_view.append(f"{rel}:{i}")
check("② CURRENT 角色资产标准仅 4 View（三视图仅存于 LEGACY 说明行）", not bad_view, "; ".join(bad_view[:5]))
check("② asset-spatial-ledger 定义 4 View 资产参考图", "角色 4 View 资产参考图（CURRENT 标准" in read(os.path.join("references", "asset-spatial-ledger.md")))

# ---------- ③ Prompt 格式命名 ----------
all_md = "\n".join(read(os.path.relpath(p, BASE)) for p in scan_md_files())
_ban=[l for l in all_md.splitlines() if re.search(r"八段式|六栏|九栏", l) and not re.search(r"禁|别名", l)]
check("③ 禁用「八段式/六栏/九栏」别名（禁令声明行除外）", not _ban, "; ".join(_ban[:3]))
ma = read(os.path.join("references", "model-adapters.md"))
check("③ 七段式唯一命名+接续状态尾行口径（model-adapters §5）",
      "「七段式」为唯一命名" in ma and "接续状态】是【时间轴分镜】段强制尾行" in ma)

# ---------- ④ LEGACY 标记 ----------
check("④ spatial-reference-system-V3 带 LEGACY/备查标记",
      "LEGACY / 备查（V6.8 标记）" in read(os.path.join("references", "spatial-reference-system-V3.md")))
check("④ CHANGELOG 带 LEGACY/HISTORY 声明", "LEGACY/HISTORY 声明" in read("CHANGELOG.md"))

# ---------- ⑤ README/SKILL 一致 ----------
readme = read("README.md")
check("⑤ 版本一致（SKILL/README 均 V6.9）", "V6.9" in skill and "V6.9" in readme)
check("⑤ 模型支持口径一致（2.5/2.0/即梦，无可灵）",
      all(("Seedance 2.5" in doc and "Seedance 2.0" in doc) for doc in (skill, readme))
      and not [l for l in readme.splitlines() if "可灵" in l and not re.search(r"移除|残留|LEGACY", l)])
check("⑤ 模型前置锁定保留（SKILL 〇节）", "强制二选一" in skill and "停下询问用户" in skill)

# ---------- ⑥ 场景拼接图口径（2026-09-15 四向校准）----------
asl = read(os.path.join("references", "asset-spatial-ledger.md"))
check("⑥ 场景拼接图=左 2/3 高空鸟瞰透视 + 右 1/3 四向缩略图",
      "左 2/3" in asl and "高空鸟瞰" in asl and "四视角缩略图" in asl)
check("⑥ 场景拼接图硬规则（交叉可定位/纯场景禁人物/16:9）",
      "交叉可定位" in asl and "纯场景禁人物" in asl and "16:9" in asl)
check("⑥ 旧口径「关键区域细节三联」已清零",
      "细节三联" not in asl)
chk = read(os.path.join("references", "★ prompt-feeding-checklist.md"))
check("⑥ 场景双图铁律（功能图 + 场景拼接图）",
      "场景双图" in chk and "场景拼接图" in chk)

# ---------- ⑦ 首尾帧仅限 2.5（2026-09-15 用户裁定）----------
# 2.0 语境行不得把首尾帧当作可用能力（排除“无首尾帧/禁用/不适用/禁止”等否定表述）
NEG = re.compile(r"无首尾帧|禁用|不适用|禁止|不得|排除|2\.0 无")
bad_fl = []
for p in scan_md_files():
    rel = os.path.relpath(p, BASE)
    if rel.startswith("CHANGELOG"):
        continue
    for i, line in enumerate(read(rel).splitlines(), 1):
        if ("2.0" in line or "2．0" in line) and ("首帧" in line or "尾帧" in line) and not NEG.search(line):
            bad_fl.append(f"{rel}:{i}")
check("⑦ 2.0 语境无首尾帧（仅否定/禁用表述可提及）", not bad_fl, "; ".join(bad_fl[:5]))
check("⑦ SKILL 〇节含「首尾帧仅限 2.5」硬约束 + 参考模式二选一默认①",
      "首尾帧仅限 Seedance 2.5" in skill and "全能参考模式（默认推荐）" in skill)
check("⑦ model-adapters §1.5 标明仅 2.5",
      "仅锁定 2.5 后必答" in read(os.path.join("references", "model-adapters.md")))

# ---------- ⑧ 稿件级门禁脚本（V6.8 新增 validate_prompt.py · 出稿时门）----------
import subprocess
vp = os.path.join(BASE, "scripts", "validate_prompt.py")
check("⑧ validate_prompt.py 存在（稿件级出稿门禁）", os.path.exists(vp))
if os.path.exists(vp):
    try:
        r = subprocess.run([sys.executable, vp, "--self-test"], capture_output=True,
                           text=True, timeout=30)
        check("⑧ validate_prompt.py self-test 通过", r.returncode == 0,
              (r.stdout or r.stderr)[-120:])
    except Exception as e:
        check("⑧ validate_prompt.py self-test 通过", False, str(e))
    vp_src = read(os.path.join("scripts", "validate_prompt.py"))
    check("⑧ validate_prompt 含 C8 2.0 首尾帧禁用门", "C8 Seedance 2.0 全面禁用首尾帧" in vp_src)
    check("⑧ validate_prompt 含 C9 平台高危词门", "C9 正文出现平台高危词" in vp_src)
    check("⑧ validate_prompt 含 C13 镜长雷同节奏门", "C13 镜长雷同" in vp_src)
    check("⑧ SKILL 含法则 17 镜长节奏铁律", "镜长节奏铁律" in read("SKILL.md"))
chk_vp = read(os.path.join("references", "★ prompt-feeding-checklist.md"))
check("⑧ checklist 挂线 validate_prompt（出稿门禁）", "validate_prompt" in chk_vp)
skill_vp = read("SKILL.md")
check("⑧ SKILL 架构树/指令挂线 validate_prompt", "validate_prompt.py" in skill_vp)

# ---------- ⑨ V6.9 段缝 D 锁 + 画外声规程（2026-09-18）----------
check("⑨ segment-splicing.md 存在（段缝衔接·D 锁规程）",
      os.path.exists(os.path.join(BASE, "references", "segment-splicing.md")))
check("⑨ vo-os-weaving.md 存在（旁白独白编织规程）",
      os.path.exists(os.path.join(BASE, "references", "vo-os-weaving.md")))
seg = read(os.path.join("references", "segment-splicing.md"))
voos = read(os.path.join("references", "vo-os-weaving.md"))
check("⑨ segment-splicing 含末态双保险与空镜三用法",
      "末态继承双保险" in seg and "段缝换机位铁律" in seg and "空镜过渡三用法" in seg)
check("⑨ vo-os-weaving 含三纪律（篇幅卡口/OS 声画分离/VO 冷漠审视）",
      "篇幅钢性卡口" in voos and "声画分离红线" in voos and "冷漠审视法则" in voos)
check("⑨ SKILL 〇节含 D·段缝衔接方式三选一锁", "段缝衔接方式三选一" in skill)
check("⑨ SKILL 含法则 18 段缝与画外声", "段缝末态继承与画外声规程" in skill)
check("⑨ model-adapters 接续状态具体末帧口径（套话废止）",
      "写具体末帧画面" in ma and "严格继承" in ma)
if os.path.exists(vp):
    check("⑨ validate_prompt 含 C14 画外声门", "C14" in vp_src and "声画分离红线" in vp_src)
    check("⑨ checklist 挂线 segment-splicing / vo-os-weaving",
          "segment-splicing" in chk_vp and "vo-os-weaving" in chk_vp)

# ---------- ⑩ V6.9 修订：时长守恒·禁拉伸凑满（C15 · 2026-09-18 晚）----------
if os.path.exists(vp):
    check("⑩ validate_prompt 含 C15 拉伸凑时门", "C15" in vp_src and "拉伸凑" in vp_src)
check("⑩ SKILL 含禁拉伸凑满条款（法则 17 修订）",
      "禁拉伸" in skill or "拉伸凑" in skill)
check("⑩ checklist 挂线 C15（时长守恒·禁拉伸凑时）",
      "C15" in chk_vp or "禁拉伸凑" in chk_vp)
check("⑩ README 机检口径已升级（C1~C15 → C1~C16）", "C1~C15" in readme or "C1~C16" in readme)

# ---------- ⑪ V6.9.3：对白语气位规范（C16 · 2026-09-19）----------
check("⑪ model-adapters 含 §5.2 对白语气规范（三要素之三）",
      "5.2 对白语气规范" in ma and "HOW THEY SOUND" in ma)
check("⑪ 语气位 2.0/2.5 同规格必写（2.0 不因无音色锁而降级）",
      "同规格要求，不做降级" in ma and "2.0 与 2.5 都必写语气" in ma)
check("⑪ 音色锁仅 2.5 且可选、不做资产体系",
      "音色锁（仅 2.5 · 可选 · 不做资产体系）" in ma)
check("⑪ 语气词分流表判据（麦克风/摄像机）存在", "麦克风能录到" in ma)
check("⑪ 反形容词听觉层豁免（声音层不受约束）",
      "听觉层豁免" in read(os.path.join("references", "cinematic-dramaturgy-rules.md")))
check("⑪ 语速联动（语气档决定语速档）",
      "语气 → 语速档联动" in read(os.path.join("references", "dialogue-speed-check.md")))
if os.path.exists(vp):
    check("⑪ validate_prompt 含 C16 对白语气门", "C16" in vp_src and "语气错位" in vp_src)
    check("⑪ validate_prompt C16 三判据齐备（错位/缺失/空泛词）",
          "C16a" in vp_src and "C16b" in vp_src and "C16c" in vp_src)
check("⑪ SKILL 含法则 19 对白三要素·语气位必写", "对白三要素·语气位必写" in skill)
check("⑪ checklist 挂线语气位（对白四查 + §5.2）",
      "对白四查" in chk_vp and "语气位必写" in chk_vp and "§5.2" in chk_vp)
check("⑪ README 机检口径已升级（口径随版本递进，≥C1~C16）", "C1~C1" in readme or "C1~C2" in readme)
check("⑪ 上游分界直取（剧本端 v3.4.3 神态短语 ｜ 规格互认）",
      "｜" in ma and "原文搬进语气位" in ma)
# ---------- ⑫ V6.9.3 续：人物账连续·摆位必入画（C17 · 2026-09-19）----------
check("⑫ model-adapters 含 §5.0.1 摆位必入画规程", "摆位必入画" in ma and "5.0.1" in ma)
check("⑫ 站位不漂移 + 入画交代条款齐备", "不得漂移" in ma and "入画" in ma)
check("⑫ validate_prompt 含 C17 摆位必入画门", "C17" in vp_src and "摆位必入画" in vp_src)
check("⑫ C17 离画/退场豁免词齐备", "离画" in vp_src and "退场" in vp_src)
check("⑫ SKILL 含法则 20 人物账连续", "人物账连续·摆位必入画" in skill)
check("⑫ checklist 挂线 C17（铁律 11 + P2）", "摆位必入画" in chk_vp)
check("⑫ README 机检口径已升级（≥C1~C17）", "C1~C1" in readme or "C1~C2" in readme)

# ---------- ⑬ V6.9.4：首镜锚定·景别一致·姿态延续·视线指派（C18 · 2026-09-19）----------
check("⑬ model-adapters 含 §5.0.2 首镜锚定规程", "首镜锚定" in ma and "5.0.2" in ma)
check("⑬ 四铁律齐备（锚/景别/姿态/视线）",
      "首镜人物锚" in ma and "景别三一致" in ma and "姿态延续" in ma and "视线指派" in ma)
check("⑬ validate_prompt 含 C18 门（四判据 a/b/c/d）",
      all(k in vp_src for k in ("C18a", "C18b", "C18c", "C18d")))
check("⑬ C18 判据锚定实测病灶（空床/视线黏道具/姿态回退）",
      "空镜" in vp_src and "把玩" in vp_src and "撑起" in vp_src)
check("⑬ SKILL 含法则 21 首镜锚定·视线指派", "首镜锚定" in skill and "视线指派" in skill)
check("⑬ checklist 挂线 C18（铁律 12）", "视线指派" in chk_vp and "姿态延续" in chk_vp)
check("⑬ README 机检口径已升级（≥C1~C18）", "C1~C1" in readme or "C1~C2" in readme)
check("⑬ model-adapters 含 §5.0.3 道具光效·表情锚·外观锚·跨镜在场", "5.0.3" in ma and "道具光效" in ma)
check("⑬ validate_prompt 含 C18e 反光道具光效门", "C18e" in vp_src and "不发光" in vp_src)
check("⑬ SKILL/checklist 挂线道具光效（C18e）", "道具光效" in skill and "道具光效" in chk_vp)

# ---------- ⑭ V6.9.5：禁令失效三改法（C19 · 2026-09-19）----------
check("⑭ model-adapters 含 §5.0.4 禁令失效三改法", "5.0.4" in ma and "禁令失效三改法" in ma)
check("⑭ 三改法齐备（换词/主体优先/触发器移除）",
      "换词" in ma and "主体优先" in ma and "触发器移除" in ma)
check("⑭ 对否定不敏感·对词根敏感口径在案", "对否定不敏感" in ma and "对词根敏感" in ma)
check("⑭ validate_prompt 含 C19 门（a 裸禁令词/b 光路触发器/c 首镜主体优先）",
      "C19a" in vp_src and "C19b" in vp_src and "C19c" in vp_src)
check("⑭ C19d 具象光源映射门（映出火苗→光斑语言）", "C19d" in vp_src and "光斑" in vp_src)
check("⑭ 少形容词密度纪律在案（model-adapters §5.0.4）", "少形容词" in ma)
check("⑭ C19 豁免兼容 C18e（正向材质描写放行）", "pos_declared" in vp_src)
check("⑭ SKILL 含法则 22 禁令失效三改法", "禁令失效三改法" in skill)
check("⑭ checklist 挂线 C19（铁律 13）", "禁令失效三改法" in chk_vp and "C19" in chk_vp)
check("⑭ SKILL 机检口径升至 C1~C19", "C1~C19" in skill)
check("⑭ README 机检口径已升级（≥C1~C19）", "C1~C1" in readme or "C1~C2" in readme)

# ---------- ⑮ 组：V6.9.6 禁止项栏目纪律 ----------
check("⑮ model-adapters §5.0.4 含栏目纪律条款", "栏目纪律" in ma)
check("⑮ 正向指令禁入·否定式同样禁入 口径在案",
      "正向执行指令禁入" in ma or "正向指令禁入" in ma)
check("⑮ 禁止项合法内容三类在案（画面/文字/音频）", "音频" in ma and "角标" in ma)
check("⑮ validate_prompt 含 C19e 门（e-a 正向指令/e-b 裸禁令词）",
      "C19e" in vp_src and "C19E_POS_RE" in vp_src and "C19E_NEG_WORDS" in vp_src)
check("⑮ C19e 判据锚定实测病灶（首帧正向指令/保持材质）",
      "即[^。；]" in vp_src or "保持[^。；]" in vp_src)
check("⑮ C18e 与 C19e 分工口径在案（neg 由 C19e-b 检出）", "C19e-b" in vp_src)
check("⑮ self-test 含 C19e 用例（41/41b/42/42b）", "C19e" in vp_src and "应报 C19e" in vp_src)
check("⑮ SKILL 含法则 22 栏目纪律", "栏目纪律" in skill and "禁令失效三改法" in skill)
check("⑮ checklist 铁律 13 含栏目纪律", "栏目纪律" in chk_vp)
check("⑮ SKILL 版本块升 V6.9.6", "V6.9.6" in skill)
check("⑮ README 版本升 V6.9.6", "V6.9.6" in readme)
check("⑮ CHANGELOG 含 V6.9.6 条目", "V6.9.6" in read("CHANGELOG.md"))

# ---------- ⑯ 组：V6.9.7 首镜单主体锚定与具象化（C20 · 2026-09-19）----------
check("⑯ model-adapters §5.0.2 含单主体铁律", "单主体铁律" in ma)
check("⑯ 并列主体/同框句式禁令在案", "并列主体" in ma and "同框" in ma)
check("⑯ §5.0.4 旧示范句标注废止", "已废止（V6.9.7）" in ma)
check("⑯ 抽象形容删除纪律在案（成线/轻蜷）", "抽象形态" in ma and "轻蜷" in ma)
check("⑯ validate_prompt 含 C20 门（a 并列主体/b 悬空指代/c 抽象形态）",
      all(k in vp_src for k in ("C20a", "C20b", "C20c")))
check("⑯ C20 三常量在案",
      all(k in vp_src for k in ("MULTI_SUBJ_RE", "DANGLING_DEIXIS_RE", "ABSTRACT_SHAPE_RE")))
check("⑯ self-test 含 C20 用例（43/43b/44/44b/45/45b）",
      "应报 C20a" in vp_src and "应报 C20b" in vp_src and "应报 C20c" in vp_src)
check("⑯ C19 修复建议不再传播旧句式「首帧即人物近景画面」",
      "首帧即人物近景画面" not in vp_src)
check("⑯ checklist 铁律 14 + 旧否定式写法已修订",
      "首镜单主体锚定" in chk_vp and "已废止" in chk_vp)
check("⑯ SKILL 含法则 23 首镜单主体锚定", "首镜单主体锚定" in skill)
check("⑯ SKILL 机检口径升至 C1~C20", "C1~C20" in skill)
check("⑯ SKILL 版本块升 V6.9.7", "V6.9.7" in skill)
check("⑯ README 版本升 V6.9.7 且机检口径 C1~C20", "V6.9.7" in readme and "C1~C20" in readme)
check("⑯ CHANGELOG 含 V6.9.7 条目", "V6.9.7" in read("CHANGELOG.md"))
# --- ⑯续：C20d 道具光效归零（V6.9.7 续增） ---
check("⑯ validate_prompt 含 C20d 门（光效共现/贴近光源）",
      all(k in vp_src for k in ("C20d", "PROP_LIGHT_RE", "LAMP_NEAR_RE")))
check("⑯ self-test 含 C20d 用例（46/46b/46c）",
      "应报 C20d" in vp_src)
check("⑯ 修复建议不再传播光斑语言/举到灯旁旧写法（自测反例除外）",
      vp_src.count("指甲盖大的一片暖黄光斑") <= 1          # 仅允许 self-test 46 反例保留
      and "举到灯旁" not in vp_src
      and "火光从侧面照在玉面上" not in vp_src
      and "受油灯照射处只有" not in vp_src.split("def _self_test")[0])
check("⑯ model-adapters 道具光效条为零光效口径",
      "零光效描写" in read("references/model-adapters.md"))
check("⑯ SKILL/checklist 含零光效口径",
      "零光效描写" in skill and "零光效描写" in chk_vp)
check("⑯ CHANGELOG 含 C20d 条目", "C20d" in read("CHANGELOG.md"))
# --- ⑯续2：C16d 道具动作与语气冲突（V6.9.7 续增） ---
check("⑯ validate_prompt 含 C16d 门（闲适道具动作×强情绪语气）",
      all(k in vp_src for k in ("C16d", "IDLE_PROP_RE", "TONE_SEVERE")))
check("⑯ self-test 含 C16d 用例（47/47b/47c）", "应报 C16d" in vp_src)
check("⑯ model-adapters 道具动作与语气一致条在案",
      "道具动作与语气一致" in read("references/model-adapters.md"))
check("⑯ SKILL 法则 19 含 C16d 口径", "道具动作与语气一致" in skill)
check("⑯ CHANGELOG 含 C16d 条目", "C16d" in read("CHANGELOG.md"))

# ---------- ⑰ 组：规则自洽门 · 示范句验证纪律（V6.9.7 根因复盘）----------
# 根因：历轮废镜示范句（同框句/光斑句/举到灯旁/面无笑意）全是当轮先验新造、未实拍验证，
# 其中两处还嵌在机检修复建议文案里被产物照抄（传染源）。本门让规则文档自己过自己的禁令：
# 被废止句式的关键词只允许出现在警示语境（已废止/禁写/替代/病根复盘等），裸出现即 FAIL。
DEAD_PATTERNS = (
    "首帧即这只手",                 # V6.9.5 同框句 → 两张脸（V6.9.7 废止）
    "指甲盖大的一片暖黄光斑",        # V6.9.5/6 光斑语言 → 玉佩点火（V6.9.7 废止）
    "火光从侧面照在玉面",            # V6.9.5 侧受光建议 → 玉佩点火（V6.9.7 废止）
    "举到油灯旁",                   # V6.9.5 贴近光源动作 → 玉佩点火（V6.9.7 废止）
    "面无笑意",                     # V6.9.4 否定式表情 → 甜笑（V6.9.5 废止）
    "漏雨成线",                     # 抽象形态形容（V6.9.7 废止）
    "映出油灯火苗",                  # 具象光源映射（V6.9.7 废止）
)
WARN_MARKS_17 = ("已废止", "废止", "禁写", "禁入", "禁止", "不得", "一律删", "⚠️", "❌",
                 "替代", "规避", "裸禁令", "病根", "无视", "画不出来", "翻车")
RULE_DOCS_17 = ("references/model-adapters.md", "SKILL.md",
                "references/★ prompt-feeding-checklist.md",
                "references/seedance-render-engine.md")
viol17 = []
for doc17 in RULE_DOCS_17:
    try:
        txt17 = read(doc17)
    except Exception:
        continue
    for i17, ln17 in enumerate(txt17.splitlines(), 1):
        for pat17 in DEAD_PATTERNS:
            if pat17 in ln17 and not any(m in ln17 for m in WARN_MARKS_17):
                viol17.append(f"{doc17}:{i17}『{pat17}』")
check("⑰ 规则自洽门：被废止句式仅存于警示语境（规则不产毒）", not viol17, "; ".join(viol17[:6]))
check("⑰ 示范句验证纪律挂线 model-adapters §5.0.5",
      "示范句验证纪律" in read("references/model-adapters.md"))
check("⑰ SKILL 挂线示范句验证纪律（法则 24）",
      "示范句验证纪律" in skill and "先验创作" in skill)
check("⑰ CHANGELOG 含示范句根因复盘", "根因复盘" in read("CHANGELOG.md"))

# ---------- ⑱ V6.9.8 MiniMax H3 格式支线（2026-09-20）----------
check("⑱ h3-adapter.md 存在（H3 格式支线·★权威）",
      os.path.exists(os.path.join(BASE, "references", "h3-adapter.md")))
h3 = read(os.path.join("references", "h3-adapter.md"))
check("⑱ h3-adapter 含两 checkpoint 与两套字段集",
      "H3-Base-FL2VA" in h3 and "H3-Base-Ref2VA" in h3
      and "subject_definitions" in h3 and "integrated_multimodal_description" in h3)
check("⑱ h3-adapter 含素材上限（9 图/3 视频/3 音频/总 12）",
      "≤9 张" in h3 and "总数 ≤12" in h3 and "不能作为唯一输入" in h3)
check("⑱ h3-adapter 含 9 张取材策略与两套投喂载荷",
      "9 张取材策略" in h3 and "h3_context_ir" in h3 and "conditions" in h3)
check("⑱ h3-adapter 含 H1~H12 机检与真人脸红线澄清",
      "H1~H12" in h3 and "H3 官方没有这条" in h3)
check("⑱ h3-adapter 含语气位继承（法则 19 对齐）",
      "语气位必须继承" in h3 and "语气词禁写进画面段" in h3)
check("⑱ h3-adapter 含摆位必入画继承（法则 20 对齐）",
      "摆位必入画" in h3 and "已出画" in h3)
check("⑱ h3-adapter 含首镜锚定/单主体继承（法则 21/23 对齐）",
      "首镜锚定" in h3 and "单主体" in h3 and "同框" in h3)
check("⑱ h3-adapter 含禁令改法继承（法则 22 对齐）",
      "否定式不进正文" in h3 or "只写\"有什么\"" in h3)
check("⑱ SKILL 〇节 A 含 H3 三选项与格式转换支线",
      "MiniMax H3" in skill and "格式转换支线" in skill and "强制二选一" in skill)
check("⑱ SKILL 含法则 25（H3 格式支线）", "MiniMax H3 格式支线" in skill)
check("⑱ SKILL 指令路由挂线 /H3提示词", "/H3提示词" in skill)
check("⑱ SKILL 架构树挂线 h3-adapter + 41 份", "h3-adapter.md" in skill and "41 份" in skill)
check("⑱ model-adapters 含 §二 H3 特性行与 §三 第 8 条",
      "MiniMax H3**（格式支线）" in ma and "A 锁选 MiniMax H3 时另加" in ma)
check("⑱ README 含 H3 支线能力行与 41 份规则库",
      "h3-adapter" in readme and "41 个专业规则库" in readme)
if os.path.exists(vp):
    check("⑱ validate_prompt 含 H 系列门（H1~H12）",
          "H1 Ref2VA 缺段" in vp_src and "H8 七段式栏名泄漏" in vp_src and "H12" in vp_src)
    try:
        r = subprocess.run([sys.executable, vp, "--self-test"], capture_output=True,
                           text=True, timeout=30)
        check("⑱ validate_prompt self-test（C 系列 + H 系列）通过", r.returncode == 0,
              (r.stdout or r.stderr)[-160:])
    except Exception as e:
        check("⑱ validate_prompt self-test（C 系列 + H 系列）通过", False, str(e))

# ---------- 汇总 ----------
print("-" * 40)
if FAILED:
    print(f"[-] {len(FAILED)} 项未通过: {FAILED}")
    sys.exit(1)
print(f"[+] 全部检查通过（references {len(refs)} 份 · V6.9）")
