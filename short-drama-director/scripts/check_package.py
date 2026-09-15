#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V6.8 语义回归检查（最小集）：
① 可灵：只能出现在 LEGACY/移除声明行，不得作为正式支持模型
② 角色资产：CURRENT 标准只能是 4 View（"三视图"仅允许出现在 LEGACY/历史说明行）
③ Prompt 格式命名：禁止"八段式/六栏/九栏"；七段式定义与接续状态尾行口径必须存在
④ LEGACY：V3 空间系统与 CHANGELOG 必须带 LEGACY 标记
⑤ README/SKILL：版本号与 Seedance 2.5/2.0 关键产品规则一致
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
check("references 规则库完整（38 份）", len(refs) == 38, f"实际 {len(refs)} 份")

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
check("⑤ 版本一致（SKILL/README 均 V6.8）", "V6.8" in skill and "V6.8" in readme)
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

# ---------- 汇总 ----------
print("-" * 40)
if FAILED:
    print(f"[-] {len(FAILED)} 项未通过: {FAILED}")
    sys.exit(1)
print(f"[+] 全部检查通过（references {len(refs)} 份 · V6.8）")
