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

# ---------- 汇总 ----------
print("-" * 40)
if FAILED:
    print(f"[-] {len(FAILED)} 项未通过: {FAILED}")
    sys.exit(1)
print(f"[+] 全部检查通过（references {len(refs)} 份 · V6.8）")
