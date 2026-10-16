# -*- coding: utf-8 -*-
"""build_board_lite.py — 轻量离线分镜看板编译器（轻量版 · 简化自 7.3.0 模块 K）

用法:
    python scripts/build_board_lite.py <项目.md> [--out <看板.html>]

产出:
    单文件离线 HTML 看板（CSS/JS 全内嵌，双击浏览器即开，零依赖/零数据库/零端口）

看板区块（与 6.8.3 同构，砍掉 N1~N11 检查层 / validate 依赖 / json 快照）:
    创作蓝图层: Ⅰ 创作基准(P0A) · Ⅱ 剧本层(P1) · Ⅲ 视听圣经(P1)
    分镜生产层: ① 时间轴泳道 · ② 镜头卡矩阵(拆解) · ③ 投喂提示词原文(成品)
                ④ 资产总表(P2) · ⑤ 资产出图提示词(P2.5·与③必同板) · ⑥ 发布文案(P6·可选)

输入 md 最小契约:
    # 项目标题
    【画幅】：16:9        【模型版本】：2.5        ← A/B 双锁回显
    ## P0A · 创作基准     ← 可选表格: 项 | 内容
    ## P1 · 剧本          ← 可选，正文照录
    ## P1 · 视听圣经      ← 可选表格或正文
    ## P2 · 资产清单      ← 表格: 编码 | 名字 | 视图 | @图片N
    ## P2.5 · 资产出图提示词
    ### CHR-001 · 林越 · 主角角色基准图
    ```text 出图提示词 ```
    ## P4 · 投喂提示词    ← 分镜提示词（与 ⑤ 必同板呈现）
    ### 段1
    【核心人物】：…        ← 段级栏（可选，显示为标签）
    ```text 投喂提示词 ```
    [0-3秒] 镜头内容      ← 逐镜拆解行
    ## P6 · 发布文案      ← 可选: 【标题】【封面文案】【正文】【话题标签】

轻量铁律（简化自 6.8.3 K1~K7，只留 4 条）:
    K-lite-1  md 是唯一真相，看板只读不回写；改稿改 md 后重编译
    K-lite-2  缺字段降级不中断：缺什么显示"未解析到"并记 WARN，看板永远出得来
    K-lite-3  拆解视图与原文并存：逐镜表/镜头卡用于定位问题，围栏原文可整段复制投喂
    K-lite-4  ⑤ 资产出图提示词与 ③ 分镜投喂提示词必须同板呈现（缺 P2.5 → WARN）
"""

import argparse
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# 兼容三种镜行写法：本包原生 `00:00-00:05 [镜头1] …` / `[00:00-00:05] …` / `[0-3秒] …`
TS_RE = re.compile(
    r"^\s*(?:[\[【]?\s*镜头\s*\d+\s*[\]】]?\s*[,，]?\s*)?"
    r"\[?\s*(\d{1,2}(?::\d{2})?(?:\.\d+)?)\s*s?\s*[-~～—→]\s*"
    r"(\d{1,2}(?::\d{2})?(?:\.\d+)?)\s*(?:秒|s)?\s*\]?\s*[,，]?\s*(.*)$", re.I)
SHOT_NO_RE = re.compile(r"^[\[【]?\s*镜头\s*\d+\s*[\]】]?\s*[,，]?\s*")


def shot_text(s: str) -> str:
    """镜行文本：剥掉 `[镜头N] ` 前缀，卡片上只留景别·运镜·动作。"""
    return SHOT_NO_RE.sub("", (s or "").strip())
FENCE_RE = re.compile(r"```(?:text|prompt)?\s*\n(.*?)```", re.S)
FIELD_RE = re.compile(r"^【([^】]{2,8})】\s*[:：]\s*(.+)$")


def to_seconds(tok: str) -> float:
    """时码 → 秒。兼容 MM:SS / MM:SS.s / MM:SS.ss 与纯秒。

    ⚠️ 秒位必须 float()（2026-10-14 Agent 修复）：
    原实现写 `int(s)`，遇半秒时码 `00:10.5` 直接抛 ValueError，
    该镜行随即被调用点的 `except ValueError: continue` **静默跳过**——
    实测《盐枭劫-60s测试局》源稿 17 镜只解析出 10 镜（丢 7 镜 / 41%），
    看板与 SRT·CSV·JSON 三导出的全片时间轴随之出现 7 秒空洞，而 CLI 零告警。
    本包真实产物普遍使用半秒粒度（`00:10.5` / `00:03.5`），故此处必须收 float。
    """
    tok = tok.strip().replace("：", ":")
    if ":" in tok:
        m, s = tok.split(":", 1)
        return int(m) * 60 + float(s)
    return float(tok)


def table_rows(lines):
    rows = []
    for l in lines:
        if l.startswith("|") and "---" not in l:
            cells = [c.strip() for c in l.strip("|").split("|")]
            if cells and cells[0]:
                rows.append(cells)
    return rows


# ── 宽容章节识别：不要求 md 照抄「## P2 · 资产清单」这类标题，按关键词归区 ──
def zone_of(title: str) -> str:
    t = title or ""
    if re.search(r"发布文案|P6", t) and not re.search(r"投喂", t):
        return "publish"
    if re.search(r"出图提示词|P2\.5|P2c|资产出图", t):
        return "ap"
    if re.search(r"投喂提示词|P4|分镜提示词", t):
        return "seg"
    if re.search(r"视听圣经|风格圣经", t):
        return "bible"
    if re.search(r"剧本|故事|梗概", t):
        return "script"
    if re.search(r"资产清单|资产表|P2", t):
        return "assets"
    if re.search(r"创作基准|P0A", t):
        return "p0a"
    return ""


# 资产表头别名 → 标准字段（兼容「类 | 编码 | 类型 | 出图 | 复用单元」这类自定义列序）
HEAD_ALIAS = {
    "code": ["编码", "code", "资产编码", "id", "资产id"],
    "name": ["名字", "名称", "角色", "人物", "资产", "name", "资产名"],
    "view": ["视图", "出图", "出图类型", "规格", "类型", "view"],
    "img":  ["@图片n", "图号", "图片", "参考图", "img", "绑定图"],
}


def map_head(cells):
    """表头行 → {标准字段: 列索引}；返回 None 表示不像表头，退回按位置取。
    按「标准字段 × 别名优先级」扫描（而非按列顺序），保证"出图"优先于"类型"命中 view。"""
    norm = [re.sub(r"[\s*`_@]", "", c).lower() for c in cells]
    idx = {}
    for std, aliases in HEAD_ALIAS.items():
        for a in aliases:
            an = re.sub(r"[\s*`_@]", "", a).lower()
            if an in norm:
                idx[std] = norm.index(an)
                break
    return idx or None


def clean_code(s: str) -> str:
    """子标题里的资产编码清洗：`1. `@CHR-沈砚`` → `@CHR-沈砚`"""
    s = (s or "").strip()
    s = re.sub(r"^\d+[.、)]\s*", "", s)     # 去前导序号
    s = s.replace("`", "").strip()
    return s


def parse_md(md_text: str) -> dict:
    lines = md_text.splitlines()
    data = {"title": "分镜看板",
            "meta": {"画幅": "未锁定", "模型版本": "未锁定"},
            "p0a": [], "script": [], "bible": [],
            "assets": [], "asset_prompts": [], "publish": [],
            "segments": [], "warnings": [], "_head": None, "extras": []}

    section = ""          # 当前 ## 章节
    seg = None            # 当前段
    ap = None             # 当前资产出图条目
    sub_head = ""         # 当前 ### 子标题
    in_fence = False
    plain = []            # 当前章节的普通正文行

    def _extra_block(title, block):
        """未归区章节的内容块（K-lite-6：md 里写的每一样东西都必须出现在看板上）。"""
        if not data["extras"] or data["extras"][-1]["title"] != title:
            data["extras"].append({"title": title, "body": []})
        data["extras"][-1]["body"].append(block)

    pending_tbl = []      # 剧本区/未归区的待归组表格行（按 markdown 分隔行切成多张表）

    def _push_tbl(rows, z):
        block = {"t": "tbl", "rows": rows}
        if z == "script":
            data["script"].append(block)
        else:
            _extra_block(section, block)

    def flush_tbl():
        nonlocal pending_tbl
        if pending_tbl:
            rows, pending_tbl = pending_tbl, []
            _push_tbl(rows, zone_of(section) if section else "")

    def flush_plain():
        nonlocal plain
        if not plain:
            return
        text = "\n".join(plain).strip()
        plain = []
        if not text:
            return
        z = zone_of(section) if section else ""
        if not section:
            _extra_block("（卷首说明）", {"t": "p", "v": text})
        elif "剧本" in section or z == "script":
            data["script"].append({"t": "p", "v": text})
        elif z == "bible":
            data["bible"].append(text)
        elif "P0A" in section or z == "p0a" or "创作基准" in section:
            data["p0a"].append({"k": section, "v": text})
        elif z == "":
            _extra_block(section, {"t": "p", "v": text})

    for raw in lines:
        line = raw.rstrip()
        s = line.strip()

        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            if ap is not None:
                ap.setdefault("fence_body", []).append(line)
            elif seg is not None:
                seg.setdefault("fence_body", []).append(line)
            continue

        if pending_tbl and not (s.startswith("|") and section):
            flush_tbl()          # 表格被正文/标题/围栏打断 → 先落表，保原文顺序

        if s.startswith("# ") and data["title"] == "分镜看板":
            flush_plain()
            data["title"] = s[2:].strip()
            continue

        m_sec = re.match(r"^##\s+(.+)$", s)
        if m_sec:
            flush_plain()
            section = m_sec.group(1).strip()
            seg, ap, sub_head = None, None, ""
            data["_head"] = None            # 表头映射不跨章节
            if re.match(r"^【?投喂单元", section) or re.match(r"^段\s*\d", section):
                seg = {"no": len(data["segments"]) + 1, "name": section,
                       "raw": "", "shots": [], "fields": {}, "warnings": []}
                data["segments"].append(seg)
                continue
            if zone_of(section) == "":
                data["extras"].append({"title": section, "body": []})
            continue

        m_sub = re.match(r"^#{3,4}\s+(.+)$", s)
        if m_sub:
            flush_plain()
            sub_head = m_sub.group(1).strip()
            z_sec = zone_of(section)
            # 段标题宽容：`### 段1` / `### U01 · …` / `### 第1段` 都认
            if re.match(r"^段\s*\d", sub_head) or re.match(r"^U\d+\b", sub_head) \
               or re.match(r"^第\s*\d+\s*段", sub_head):
                seg = {"no": len(data["segments"]) + 1, "name": sub_head,
                       "raw": "", "shots": [], "fields": {}, "warnings": []}
                data["segments"].append(seg)
                ap = None
            elif z_sec == "ap":
                parts = [p.strip() for p in sub_head.split("·")]
                ap = {"code": clean_code(parts[0]) if parts else sub_head,
                      "_match": sub_head,
                      "name": clean_code(parts[1]) if len(parts) > 1 else "",
                      "desc": parts[2] if len(parts) > 2 else "",
                      "raw": ""}
                data["asset_prompts"].append(ap)
                seg = None
            else:
                ap = None
            continue

        fm_meta = FIELD_RE.match(s)
        if fm_meta:
            key, val = fm_meta.group(1), fm_meta.group(2).strip()
            if key in ("画幅", "模型版本"):        # A/B 双锁：任意位置声明都认
                data["meta"][key] = val
                continue
            if seg is not None:
                seg["fields"][key] = val
                continue
            if zone_of(section) == "publish":
                data["publish"].append({"k": key, "v": val})
                continue

        if s.startswith("|") and section:
            z = zone_of(section)
            if "---" in s and z in ("script", ""):
                # markdown 分隔行＝表头确认：把已收的「表头+数据」落表，末行留给下一张表当表头
                if len(pending_tbl) > 1:
                    head = pending_tbl[-1]
                    _push_tbl(pending_tbl[:-1], z)
                    pending_tbl = [head]
                continue
            rows = table_rows([s])
            if rows:
                cells = rows[0]
                k0 = re.sub(r"[*`]", "", cells[0]).strip()
                # meta 兜底：从 A/B 双锁表等任意表格里捞模型版本/画幅
                if data["meta"]["模型版本"] == "未锁定" and "模型版本" in k0 and len(cells) > 1:
                    m = re.search(r"Seedance\s*[\d.]+|\d+(?:\.\d+)?", re.sub(r"[*`]", "", cells[1]))
                    if m:
                        data["meta"]["模型版本"] = m.group(0).strip()
                if data["meta"]["画幅"] == "未锁定" and "画幅" in k0 and len(cells) > 1:
                    m = re.search(r"\d{1,2}\s*:\s*\d{1,2}", cells[1])
                    if m:
                        data["meta"]["画幅"] = re.sub(r"\s", "", m.group(0))
                if z in ("script", ""):
                    flush_plain()            # 先落之前挂着的正文，保原文顺序
                    pending_tbl.append(cells)
                elif z == "assets":
                    head = map_head(cells)   # 表头探测只在资产区生效（防止吞掉剧本区表头行）
                    if head is not None:
                        data["_head"] = head
                        continue
                    h = data.get("_head")
                    if h:
                        g = lambda f: cells[h[f]] if f in h and h[f] < len(cells) else ""
                        row = {"code": g("code") or cells[0], "name": g("name"),
                               "view": g("view"), "img": g("img"), "extra": []}
                        used = set(h.values())
                        row["extra"] = [c for i, c in enumerate(cells)
                                        if i not in used and c and c not in ("类", "编码")]
                    else:
                        row = {"code": cells[0], "name": cells[1] if len(cells) > 1 else "",
                               "view": cells[2] if len(cells) > 2 else "",
                               "img": cells[3] if len(cells) > 3 else "", "extra": []}
                    if row["code"] and row["code"] not in ("编码",):
                        data["assets"].append(row)
                elif z == "p0a":
                    if cells[0] not in ("项",):
                        data["p0a"].append({"k": cells[0], "v": " | ".join(cells[1:])})
                elif z == "bible":
                    data["bible"].append(" | ".join(cells))
                continue

        if seg is not None:
            fmt = TS_RE.match(s)
            if fmt:
                try:
                    start, end = to_seconds(fmt.group(1)), to_seconds(fmt.group(2))
                except ValueError:
                    seg["warnings"].append(
                        f"镜行时码无法解析、该镜已被跳过（看板与三导出会缺此镜）：{s[:40]}")
                else:
                    seg["shots"].append({"no": len(seg["shots"]) + 1,
                                         "start": start, "end": end,
                                         "text": shot_text(fmt.group(3))})
                continue
        plain.append(line)

    flush_tbl()
    flush_plain()

    # 围栏原文归属：段 / 资产出图
    parts = re.split(r"^#{2,4}\s+", md_text, flags=re.M)
    def fence_of(body):
        fs = FENCE_RE.findall(body)
        return max(fs, key=len).strip() if fs else ""
    for seg in data["segments"]:
        token = seg["name"].split()[0]                 # 段1 / U01 / 第1段
        for chunk in parts[1:]:
            first = chunk.splitlines()[0].strip()
            if first == seg["name"] or first.startswith(token):
                seg["raw"] = fence_of("\n".join(chunk.splitlines()[1:]))
                break
    for ap in data["asset_prompts"]:
        for chunk in parts[1:]:
            first = chunk.splitlines()[0].strip()
            if first == ap.get("_match") or first.startswith(ap.get("_match", "\0")):
                ap["raw"] = fence_of("\n".join(chunk.splitlines()[1:]))
                break

    # 校验（轻量 WARN 层）
    for seg in data["segments"]:
        if not seg["raw"]:
            seg["warnings"].append("未找到 ```text 围栏投喂原文（无法直接复制投喂）")
        _skipped = []
        if not seg["shots"]:
            for l in seg["raw"].splitlines():     # K-lite-2 降级：从围栏内提取时间戳
                fm = TS_RE.match(l.strip())
                if fm:
                    try:
                        a, b = to_seconds(fm.group(1)), to_seconds(fm.group(2))
                    except ValueError:
                        # ★2026-10-14 Agent 修复：原为裸 `continue` —— 丢镜不留痕。
                        # 静默丢镜会让看板与三导出悄悄缺镜（实测曾丢 41%），必须记账。
                        _skipped.append(l.strip()[:48])
                        continue
                    seg["shots"].append({"no": len(seg["shots"]) + 1,
                                         "start": a, "end": b, "text": shot_text(fm.group(3))})
        # ★丢镜安全网（2026-10-14 Agent 新增）：以「原文带时码的行数」为基准对账，
        #   任何解析器缺陷造成的静默丢镜都会被这一条兜住，不必逐类枚举病因。
        _tc_lines = [l for l in seg["raw"].splitlines() if TS_RE.match(l.strip())]
        if _skipped:
            seg["warnings"].append(
                f"有 {len(_skipped)} 行镜行时码无法解析、该镜已被跳过"
                f"（看板与 SRT/CSV/JSON 三导出会缺这些镜）：{'；'.join(_skipped[:4])}"
                + ("…" if len(_skipped) > 4 else ""))
        if len(_tc_lines) > len(seg["shots"]):
            _lost = len(_tc_lines) - len(seg["shots"])
            seg["warnings"].append(
                f"丢镜告警：原文带时码的镜行 {len(_tc_lines)} 行，仅解析出 {len(seg['shots'])} 镜，"
                f"缺 {_lost} 镜——请核对镜行时码写法（支持 `MM:SS` / `MM:SS.s` / `Xs-Ys` / `N-N秒`）")
        if not seg["shots"]:
            seg["warnings"].append("未解析到 [起-止秒] 逐镜时间戳行")
        else:
            prev = None
            for sh in seg["shots"]:
                if prev is not None and sh["start"] < prev - 0.01:
                    seg["warnings"].append(f"镜头时间码回跳：{sh['start']:g}s 早于上镜结束 {prev:g}s")
                    break
                prev = sh["end"]
        for w in seg["warnings"]:
            data["warnings"].append({"seg": seg["no"], "msg": f"{seg['name']}：{w}"})

    for ap in data["asset_prompts"]:
        if not ap["raw"]:
            data["warnings"].append({"seg": 0, "msg": f"资产出图提示词 {ap['code']} 未找到 ```text 围栏原文"})
    if not data["segments"]:
        data["warnings"].append({"seg": 0, "msg": "全档未解析到「### 段N」分镜段——请检查标题契约"})
    if not data["asset_prompts"]:
        data["warnings"].append({"seg": 0,
            "msg": "未解析到「## P2.5 · 资产出图提示词」——⑤ 资产出图提示词与 ③ 分镜投喂提示词必须同板呈现（K-lite-4）"})
    else:
        for _it in data["asset_prompts"]:
            _bd = (_it.get("raw") or "").strip()
            _cd = (_it.get("code") or _it.get("name") or "").upper()
            _missing_fp = (
                len(_bd) < 150
                or "同板四视图" in _bd or "T-pose" in _bd or "九机位小图" in _bd or "详见 P2" in _bd or "不另写文字描述" in _bd
                or ("CHR" in _cd and not ("无脸全身" in _bd or "featureless face" in _bd))
                or ("SCN" in _cd and not ("九宫格" in _bd or "摄影机矩阵" in _bd))
            )
            if _missing_fp:
                data["warnings"].append({
                    "seg": 0, "lvl": "WARN", "code": "K-lite-4b",
                    "msg": f"K-lite-4b 资产「{_it.get('code') or _it.get('name', '')}」出图提示词疑似简笔空壳（仅 {len(_bd)} 字或未落权威模板指纹）——须按 sd-asset-engine 权威模板写满（角色四字段模板 / 场景母版+九宫格8字段 / 道具4格）"
                })
    if data["meta"]["画幅"] == "未锁定":
        data["warnings"].append({"seg": 0, "msg": "未声明【画幅】——B 锁未锁定（用户未指定 ≠ 默认 9:16）"})
    if data["meta"]["模型版本"] == "未锁定":
        data["warnings"].append({"seg": 0, "msg": "未声明【模型版本】——A 锁未锁定（用户未指定 ≠ 默认 2.5）"})

    # 时间轴排布：段内独立计时 → 按累计偏移铺成整片时间轴（泳道才读得出 57s 成片节奏）
    off = 0.0
    for seg in data["segments"]:
        seg["off"] = off
        if seg["shots"]:
            off += max(sh["end"] for sh in seg["shots"])

    # 资产引用段：用编码在段原文里回查（如 @CHR-沈砚 出现在哪些段）
    for a in data["assets"]:
        code = a.get("code", "")
        a["refs"] = [seg["no"] for seg in data["segments"] if code and code in seg["raw"]]
    return data


def total_duration(data):
    """各段独立计时（每段都从 0 起）→ 累加成整片时长；连续时间轴 → 取最大 end。"""
    segs = [s for s in data["segments"] if s["shots"]]
    if not segs:
        return 0
    starts = [s["shots"][0]["start"] for s in segs]
    if starts and all(abs(x - starts[0]) < 0.01 for x in starts) and starts[0] == 0:
        return sum(max(sh["end"] for sh in s["shots"]) for s in segs)
    return max(max(sh["end"] for sh in s["shots"]) for s in segs)


def build_html(d: dict) -> str:
    payload = {
        "meta": {"model": d["meta"]["模型版本"], "aspect": d["meta"]["画幅"],
                 "seg_count": len(d["segments"]),
                 "shot_count": sum(len(s["shots"]) for s in d["segments"]),
                 "total": total_duration(d),
                 "built_at": datetime.now().strftime("%Y-%m-%d %H:%M")},
        "p0a": d["p0a"], "script": d["script"], "bible": d["bible"],
        "assets": d["assets"], "aprompts": d["asset_prompts"], "publish": d["publish"],
        "segments": d["segments"], "warnings": d["warnings"], "extras": d["extras"],
    }
    return TEMPLATE.replace("@@DATA@@", json.dumps(payload, ensure_ascii=False)) \
                   .replace("@@TITLE@@", html.escape(d["title"], quote=True))


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>@@TITLE@@ · 分镜看板</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#F7F6F2;color:#1F1E1B;
 font:14px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:20px}
h1{font-size:19px;font-weight:600;margin:0 0 4px}
h2{font-size:15px;font-weight:600;margin:26px 0 10px;padding-bottom:6px;border-bottom:1px solid #E2E0D9}
.sub{color:#6B6963;font-size:12px;font-weight:400}
.bar{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 4px}
.chip{background:#fff;border:1px solid #E2E0D9;border-radius:8px;padding:6px 10px;font-size:12px}
.chip b{font-weight:600}
.chip.k{color:#0C447C}.chip.warn{color:#854F0B;border-color:#EF9F27}
.seg-f{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}
.seg-f button{cursor:pointer;background:#fff;border:1px solid #E2E0D9;border-radius:999px;padding:4px 12px;font-size:12px}
.seg-f button.on{background:#185FA5;border-color:#185FA5;color:#fff}
.f{border:1px solid #E2E0D9;background:#fff;border-radius:8px;padding:8px 10px;margin:6px 0;font-size:12.5px}
.f .code{font-family:ui-monospace,Consolas,monospace;font-weight:600;margin-right:6px;color:#854F0B}
.lane{margin:8px 0}
.lane .nm{font-size:12px;color:#6B6963;margin-bottom:3px}
.lane .track{position:relative;height:32px;background:#fff;border:1px solid #E2E0D9;border-radius:6px}
.blk{position:absolute;top:3px;height:26px;border-radius:4px;background:#E6F1FB;border:1px solid #85B7EB;
 font-size:11px;color:#0C447C;text-align:center;line-height:24px;overflow:hidden;cursor:default}
.blk.s1{background:#E1F5EE;border-color:#5DCAA5;color:#085041}
.blk.s2{background:#FAEEDA;border-color:#EF9F27;color:#633806}
.blk.s3{background:#EEEDFE;border-color:#AFA9EC;color:#3C3489}
.blk:hover{outline:2px solid #185FA5}
.ruler{position:relative;height:16px;margin-top:2px}
.ruler span{position:absolute;top:4px;font-size:10.5px;color:#888780;transform:translateX(-50%)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(258px,1fr));gap:8px}
.card{background:#fff;border:1px solid #E2E0D9;border-radius:8px;padding:9px 10px;font-size:12px}
.card .hd{display:flex;justify-content:space-between;font-weight:600;margin-bottom:5px;font-size:12.5px}
.card .row{color:#444441;margin:3px 0}
.card .row i{color:#888780;font-style:normal;margin-right:3px}
table{width:100%;border-collapse:collapse;font-size:12px;background:#fff}
th,td{border:1px solid #E2E0D9;padding:5px 7px;text-align:left;vertical-align:top}
th{background:#F1EFE8;font-weight:600}
td.num{text-align:center;font-family:ui-monospace,Consolas,monospace}
.aimg{display:inline-block;font-size:11px;padding:1px 7px;border-radius:999px;background:#E6F1FB;
 border:1px solid #85B7EB;color:#0C447C;font-weight:600;white-space:nowrap}
.asegs{font-size:11.5px;color:#185FA5}
details.pbox{background:#fff;border:1px solid #E2E0D9;border-radius:8px;margin:8px 0;padding:10px 12px}
details.pbox>summary{cursor:pointer;font-size:12.5px;color:#33312C;list-style:none}
details.pbox>summary::-webkit-details-marker{display:none}
details.pbox>summary::before{content:"▸ ";color:#888780}
details.pbox[open]>summary::before{content:"▾ "}
.cpbtn{float:right;font-size:11.5px;padding:2px 9px;border-radius:5px;border:1px solid #85B7EB;
 background:#E6F1FB;color:#0C447C;cursor:pointer}
.cpbtn:hover{background:#D6E9FA}
pre{white-space:pre-wrap;word-break:break-word;font-family:ui-monospace,Consolas,"Courier New",monospace;
 font-size:12px;line-height:1.68;color:#33312C;background:#FAF9F5;border:1px solid #E2E0D9;
 border-radius:6px;padding:10px 12px;margin:8px 0 2px}
.note{font-size:11.5px;color:#888780;margin-top:6px}
.zone{font-size:12px;font-weight:600;letter-spacing:.06em;background:#E6F1FB;color:#0C447C;
 border:1px solid #85B7EB;border-radius:6px;padding:5px 10px;margin:26px 0 2px}
.zone.prod{background:#F1EFE8;border-color:#D3D1C7;color:#6B6963}
.kv{margin:9px 0}
.kv .k2{font-size:11px;color:#888780;letter-spacing:.04em;margin-bottom:2px}
.kv .v2{font-size:12.5px;line-height:1.72;color:#33312C;white-space:pre-wrap;word-break:break-word}
.script .sc{background:#fff;border:1px solid #E2E0D9;border-radius:8px;padding:9px 11px;margin:7px 0}
.script .sc .bd{font-size:12.5px;line-height:1.72;color:#33312C;white-space:pre-wrap}
.chips{display:flex;flex-wrap:wrap;gap:4px;margin-top:2px}
.chips .c2{font-size:11px;padding:1px 7px;border-radius:999px;background:#F7F6F2;border:1px solid #E2E0D9;color:#6B6963}
.hide{display:none}
.bline{background:#fff;border:1px solid #E2E0D9;border-radius:8px;padding:10px 12px;margin:8px 0}
.bline .bt{font-size:11px;color:#888780;letter-spacing:.04em;margin-bottom:3px}
.bline .bv{font-size:12.5px;color:#33312C;line-height:1.7;white-space:pre-wrap}
footer{text-align:center;color:#9A968C;font-size:11.5px;padding:16px 0 26px}
</style></head><body><div class="wrap">
<h1>@@TITLE@@</h1>
<div class="sub" id="hdr"></div>
<div class="bar" id="bar"></div>
<div class="seg-f" id="filters"></div>
<div id="alerts"></div>
<div class="zone">创作蓝图层 · P0~P1 —— 先看这里（故事 / 基准 / 风格）</div>
<h2>Ⅰ · 创作基准 <span class="sub">（P0A · 表格项 → 看板行）</span></h2><div id="p0a"></div>
<h2>Ⅱ · 剧本层 <span class="sub">（P1 产出物 · 正文照录）</span></h2><div id="script"></div>
<h2>Ⅲ · 视听圣经 <span class="sub">（P1 一次锁定 · 全片继承）</span></h2><div id="bible"></div>
<div class="zone prod">分镜生产层 · P2~P6 —— 拿去干活的那一份（资产 / 分镜 / 投喂 / 文案）</div>
<h2>① 时间轴泳道</h2><div id="lanes"></div>
<h2>② 镜头卡矩阵 <span class="sub">（拆解视图 — 逐镜栏位）</span></h2><div class="cards" id="cards"></div>
<h2>③ 投喂提示词原文 <span class="sub">（成品视图 — 照录未改写，可整段复制直接投喂）</span></h2><div id="prompts"></div>
<h2>④ 资产总表 <span class="sub">（人物 / 场景 / 道具 → 图号 → 引用段 · 来自 P2 资产清单）</span></h2><div id="assets"></div>
<h2>⑤ 资产出图提示词 <span class="sub">（成品视图 — 生成人物 / 场景 / 道具资产图用，可整段复制；<b>不是</b>视频投喂提示词，与 ③ 必同板）</span></h2><div id="aprompts"></div>
<h2>⑥ 发布文案</h2><div id="copy"></div>
<h2>⑦ 其他章节 <span class="sub">（md 内未被归区的章节 · 原文照录，K-lite-6 信息零丢失）</span></h2><div id="extras"></div>
<div class="note" id="foot"></div>
<footer>由 scripts/build_board_lite.py 生成 · 源 md 是唯一真相，本看板只读不回写 · 双击即开，零依赖</footer>
</div>
<script>
const D = @@DATA@@;
let curSeg = 0, onlyBad = false;
const esc = s => (s==null?'':String(s)).replace(/[&<>]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const segBad = n => D.warnings.some(w=>w.seg===n);
// 内容块渲染：连续 row 合并成表格，p 块照录（K-lite-6 信息零丢失）
function renderBlocks(bl){
  let out='', tbl=null;
  const flushT=()=>{ if(tbl){ out+='<table>'+tbl.map((r,i)=>'<tr>'+r.map(c=>(i?'<td>':'<th>')+esc(c)+'</td>').join('')+'</tr>').join('')+'</table>'; tbl=null; } };
  (bl||[]).forEach(b=>{
    if(b.t==='row'){ (tbl=tbl||[]).push(b.cells||[]); }
    else if(b.t==='tbl'){ flushT(); out+='<table>'+(b.rows||[]).map((r,i)=>'<tr>'+r.map(c=>(i?'<td>':'<th>')+esc(c)+'</td>').join('')+'</tr>').join('')+'</table>'; }
    else { flushT(); out+='<div class="bd">'+esc(b.v)+'</div>'; }
  });
  flushT();
  return out;
}

function hdr(){
  const p = D.meta;
  document.getElementById('hdr').textContent =
    `模型 ${p.model} · 画幅 ${p.aspect} · ${p.seg_count} 段 / ${p.shot_count} 镜 / 总时长 ${p.total}s · 编译于 ${p.built_at}`;
  document.getElementById('bar').innerHTML =
    `<div class="chip k"><b>轻量校验</b> ${D.warnings.length} WARN / 0 ERROR</div>`
    + `<button class="chip" onclick="toggleOnly()" id="btnOnly">只看告警</button>`
    + `<button class="chip" onclick="exportSRT()">⬇ 导出 SRT 字幕</button>`
    + `<button class="chip" onclick="exportTimelineCSV()">⬇ 导出剪辑时间线 CSV</button>`
    + `<button class="chip" onclick="exportPayloadJSON()">⬇ 导出 API 载荷 JSON</button>`;
}
function toggleOnly(){ onlyBad=!onlyBad; document.getElementById('btnOnly').classList.toggle('on',onlyBad);
  document.getElementById('btnOnly').classList.toggle('warn',onlyBad); paint(); }

function segBtns(){
  document.getElementById('filters').innerHTML =
    `<button class="${curSeg===0?'on':''}" onclick="setSeg(0)">全部段</button>`
    + D.segments.map(s=>`<button class="${curSeg===s.no?'on':''}" onclick="setSeg(${s.no})">${esc(s.name)}</button>`).join('');
}
function setSeg(n){ curSeg=n; segBtns(); paint(); }
const vis = n => (!onlyBad || segBad(n)) && (curSeg===0 || curSeg===n);

function paint(){
  hdr(); segBtns();
  // 告警区
  const al = D.warnings.map(w=>`<div class="f"><span class="code">WARN</span>${esc(w.msg)}</div>`).join('');
  document.getElementById('alerts').innerHTML = al || '';
  // Ⅰ 创作基准
  document.getElementById('p0a').innerHTML = D.p0a.length
    ? '<table><tr><th style="width:150px">项</th><th>内容</th></tr>'
      + D.p0a.map(x=>`<tr><td>${esc(x.k)}</td><td>${esc(x.v)}</td></tr>`).join('') + '</table>'
    : '<div class="f">未解析到「## P0A · 创作基准」章节</div>';
  // Ⅱ 剧本
  document.getElementById('script').innerHTML = (D.script && D.script.length)
    ? `<div class="script"><div class="sc">${renderBlocks(D.script)}</div></div>`
    : '<div class="f">未解析到「## P1 · 剧本」章节</div>';
  // Ⅲ 视听圣经
  document.getElementById('bible').innerHTML = D.bible.length
    ? D.bible.map(b=>`<div class="bline"><div class="bv">${esc(b)}</div></div>`).join('')
    : '<div class="f">未解析到「## P1 · 视听圣经」章节</div>';
  // ① 时间轴泳道
  const total = Math.max(D.meta.total, 1);
  document.getElementById('lanes').innerHTML = D.segments.map(s=>{
    const cls = ['','s1','s2','s3'];
    const off = s.off||0;
    const blocks = s.shots.map((sh,i)=>{
      const a=sh.start+off, b=sh.end+off;
      const L=(a/total*100).toFixed(2), W=Math.max((b-a)/total*100,1.2).toFixed(2);
      return `<div class="blk ${cls[i%4]}" style="left:${L}%;width:${W}%"
        title="段内 ${sh.start}-${sh.end}s（整片 ${a}-${b}s） ${esc(sh.text)}">镜${sh.no}</div>`;
    }).join('');
    const ticks = Array.from({length:5},(_,i)=>{
      const t=Math.round(total*i/4);
      return `<span style="left:${i*25}%">${t}s</span>`;
    }).join('');
    return `<div class="lane ${vis(s.no)?'':'hide'}"><div class="nm">${esc(s.name)} · ${esc(String(s.shots.length))} 镜 · 整片 ${off}s 起</div>
      <div class="track">${blocks}</div><div class="ruler">${ticks}</div></div>`;
  }).join('') || '<div class="f">未解析到分镜段</div>';
  // ② 镜头卡矩阵
  document.getElementById('cards').innerHTML = D.segments.filter(s=>vis(s.no)).flatMap(s=>
    s.shots.map(sh=>`<div class="card"><div class="hd"><span>${esc(s.name)} · 镜${sh.no}</span>
      <span class="ph">[${sh.start}-${sh.end}s] · ${Math.max(sh.end-sh.start,0).toFixed(1).replace(/\.0$/,'')}s</span></div>
      <div class="row">${esc(sh.text)||'—'}</div></div>`)).join('')
    || '<div class="f">无镜头卡</div>';
  // ③ 投喂原文
  document.getElementById('prompts').innerHTML = D.segments.filter(s=>vis(s.no)).map((s,i)=>{
    const chips = Object.entries(s.fields||{}).map(([k,v])=>`<span class="c2">${esc(k)}：${esc(v)}</span>`).join('');
    return `<details class="pbox" open><summary>${esc(s.name)} · ${s.shots.length} 镜
      <button class="cpbtn" onclick="cp('p${s.no}',event)">复制投喂原文</button></summary>
      ${chips?`<div class="chips">${chips}</div>`:''}
      <pre id="p${s.no}">${esc(s.raw||'（未解析到围栏原文）')}</pre></details>`;
  }).join('') || '<div class="f">无投喂原文</div>';
  // ④ 资产总表
  document.getElementById('assets').innerHTML = D.assets.length
    ? '<table><tr><th>编码</th><th>名字</th><th>视图 / 出图</th><th>@图片N</th><th>附加信息</th><th>引用段</th></tr>'
      + D.assets.map(a=>`<tr><td>${esc(a.code)}</td><td>${esc(a.name||'—')}</td><td>${esc(a.view||'—')}</td>
        <td><span class="aimg">${esc(a.img||'未绑图')}</span></td>
        <td class="asegs">${esc((a.extra||[]).join(' · '))||'—'}</td>
        <td class="asegs">${(a.refs||[]).length?('段 '+a.refs.join('、')):'—'}</td></tr>`).join('') + '</table>'
    : '<div class="f">未解析到「## P2 · 资产清单」表格</div>';
  // ⑤ 资产出图提示词（与 ③ 必同板）；同一场景资产的连排条目（①②③）聚合为一张卡
  const _grp=[];
  D.aprompts.forEach((a,i)=>{
    const g=_grp[_grp.length-1];
    if(g&&g.code===a.code&&a.code.indexOf('@SCN-')===0){g.items.push([a,i]);}
    else{_grp.push({code:a.code,items:[[a,i]]});}
  });
  document.getElementById('aprompts').innerHTML = _grp.length
    ? _grp.map(g=>{
        if(g.items.length===1){
          const [a,i]=g.items[0];
          return `<details class="pbox" open><summary>${esc(a.code)} · ${esc(a.name)}
            <button class="cpbtn" onclick="cp('a${i}',event)">复制出图提示词</button></summary>
            ${a.desc?`<div class="note">${esc(a.desc)}</div>`:''}
            <pre id="a${i}">${esc(a.raw||'（未解析到围栏原文）')}</pre></details>`;
        }
        return `<details class="pbox" open><summary>${esc(g.code.replace(/^@/,''))} · ${g.items.map(x=>esc(x[0].name)).join('+')} · ${g.items.length} 条复制全部
            <button class="cpbtn" onclick="cpall('${g.items.map(x=>'a'+x[1]).join('|')}',event)">复制全部</button></summary>
            ${g.items.map(([a,i])=>`<div class="note">${esc(a.name)}
              <button class="cpbtn" onclick="cp('a${i}',event)">复制本条</button></div>
              <pre id="a${i}">${esc(a.raw||'（未解析到围栏原文）')}</pre>`).join('')}
          </details>`;
      }).join('')
    : '<div class="f">未解析到「## P2.5 · 资产出图提示词」（K-lite-4：与 ③ 必同板，请补齐章节）</div>';
  // ⑥ 发布文案
  document.getElementById('copy').innerHTML = D.publish.length
    ? D.publish.map(x=>`<div class="kv"><div class="k2">${esc(x.k)}</div><div class="v2">${esc(x.v)}</div></div>`).join('')
    : '<div class="f">未解析到「## P6 · 发布文案」（可选章节）</div>';
  // ⑦ 其他章节（未归区原文照录）
  document.getElementById('extras').innerHTML = (D.extras && D.extras.length)
    ? D.extras.map(x=>`<details class="pbox"><summary>${esc(x.title)}</summary>${renderBlocks(x.body)||'<div class="f">（空）</div>'}</details>`).join('')
    : '<div class="note">（无未归区章节）</div>';
  document.getElementById('foot').textContent =
    `本看板为轻量版：无 N1~N11 深度检查层与状态快照；深度质检请走 P0~P2 质检门禁与改动后复验铁律。`;
}

function cp(id,e){
  const t=document.getElementById(id).innerText;
  const done=()=>{e.target.innerText='已复制 ✓';setTimeout(()=>{e.target.innerText='复制';},1200);};
  const fail=()=>{e.target.innerText='复制失败·请手动全选';setTimeout(()=>{e.target.innerText='复制';},2000);};
  const legacy=()=>{try{const ta=document.createElement('textarea');ta.value=t;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.focus();ta.select();const ok=document.execCommand('copy');document.body.removeChild(ta);ok?done():fail();}catch(err){fail();}};
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(done).catch(legacy);}
  else{legacy();}
}

function cpall(ids,e){
  const t=ids.split('|').map(id=>document.getElementById(id).innerText).join('\\n\\n');
  const done=()=>{e.target.innerText='已复制全部 ✓';setTimeout(()=>{e.target.innerText='复制全部';},1500);};
  const fail=()=>{e.target.innerText='复制失败·请手动全选';setTimeout(()=>{e.target.innerText='复制全部';},2000);};
  const legacy=()=>{try{const ta=document.createElement('textarea');ta.value=t;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.focus();ta.select();const ok=document.execCommand('copy');document.body.removeChild(ta);ok?done():fail();}catch(err){fail();}};
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(done).catch(legacy);}
  else{legacy();}
}
function dlBlob(filename, content, mime){
  const blob = new Blob([content], {type: mime});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(()=>{ URL.revokeObjectURL(a.href); document.body.removeChild(a); }, 300);
}
function fmtSrtTime(sec){
  // ★2026-10-15 修复：原 `ms=Math.round((sec%1)*1000)` + `totalS=Math.floor(sec)` 分立取整，
  //   小数位进位到 1000ms 时印出非法 `,1000` 且秒位不结转。改为「总毫秒一次取整再拆分」。
  let totalMs = Math.round(sec * 1000); if (totalMs < 0) totalMs = 0;
  const ms = totalMs % 1000;
  const totalS = Math.floor(totalMs / 1000);
  const s = totalS % 60;
  const m = Math.floor(totalS / 60) % 60;
  const h = Math.floor(totalS / 3600);
  const pad = (n, w=2) => String(n).padStart(w, '0');
  return `${pad(h)}:${pad(m)}:${pad(s)},${pad(ms, 3)}`;
}
function exportSRT(){
  let idx = 1, lines = [];
  (D.segments||[]).forEach(seg=>{
    const off = seg.off || 0;
    (seg.shots||[]).forEach(sh=>{
      const m = (sh.text||'').match(/台词：【([^】]+)】/);
      if(m && !m[1].startsWith('无')){
        lines.push(`${idx++}\n${fmtSrtTime(off + sh.start)} --> ${fmtSrtTime(off + sh.end)}\n${m[1]}\n`);
      }
    });
  });
  dlBlob((D.meta&&D.meta.title||'short_drama') + '.srt', lines.join('\n') || '1\n00:00:00,000 --> 00:00:02,000\n（无对白）\n', 'text/plain;charset=utf-8');
}
function exportTimelineCSV(){
  const escCsv = v => '"' + String(v==null?'':v).replace(/"/g, '""') + '"';
  const rows = [['段落', '镜号', '段内起秒', '段内止秒', '全片起秒', '全片止秒', '时长(s)', '镜头内容与台词']];
  (D.segments||[]).forEach(seg=>{
    const off = seg.off || 0;
    (seg.shots||[]).forEach(sh=>{
      rows.push([seg.name, '镜'+sh.no, sh.start, sh.end, off+sh.start, off+sh.end, Math.max(sh.end-sh.start,0), sh.text||'']);
    });
  });
  const csv = '\uFEFF' + rows.map(r=>r.map(escCsv).join(',')).join('\r\n');
  dlBlob((D.meta&&D.meta.title||'short_drama') + '_timeline.csv', csv, 'text/csv;charset=utf-8');
}
function exportPayloadJSON(){
  dlBlob((D.meta&&D.meta.title||'short_drama') + '_payload.json', JSON.stringify(D, null, 2), 'application/json;charset=utf-8');
}
paint();
</script></body></html>"""


def export_srt_text(data):
    idx, lines = 1, []
    def _fmt(sec):
        # ★2026-10-15 修复：原 `ms=int(round((sec%1)*1000))` + `ts=int(sec)` 分立取整，
        #   当小数位进位到 1000ms（如 4.9995→round(999.5)=1000）会印出非法 `,1000`
        #   且秒位不结转 → 00:00:04,1000（SRT 毫秒须 000~999）。改为「总毫秒一次取整再拆分」。
        total_ms = max(int(round(sec * 1000)), 0)
        ms = total_ms % 1000
        ts = total_ms // 1000
        return f"{ts // 3600:02d}:{(ts // 60) % 60:02d}:{ts % 60:02d},{ms:03d}"
    for seg in data.get("segments", []):
        off = seg.get("off", 0)
        for sh in seg.get("shots", []):
            m = re.search(r"台词：【([^】]+)】", sh.get("text", ""))
            if m and not m.group(1).startswith("无"):
                lines.append(f"{idx}\n{_fmt(off + sh['start'])} --> {_fmt(off + sh['end'])}\n{m.group(1)}\n")
                idx += 1
    return "\n".join(lines)


def export_timeline_csv_text(data):
    def _esc(v):
        return '"' + str(v if v is not None else "").replace('"', '""') + '"'
    rows = [["段落", "镜号", "段内起秒", "段内止秒", "全片起秒", "全片止秒", "时长(s)", "镜头内容与台词"]]
    for seg in data.get("segments", []):
        off = seg.get("off", 0)
        for sh in seg.get("shots", []):
            rows.append([
                seg.get("name", ""),
                f"镜{sh.get('no', '')}",
                sh.get("start", 0),
                sh.get("end", 0),
                off + sh.get("start", 0),
                off + sh.get("end", 0),
                round(max(sh.get("end", 0) - sh.get("start", 0), 0), 2),
                sh.get("text", ""),
            ])
    return "\ufeff" + "\r\n".join(",".join(_esc(c) for c in r) for r in rows)


def self_test():
    sample = (
        "# 测试剧目\n"
        "## 【投喂单元 1/1 · 段1】\n"
        "```text\n"
        "【画幅风格】16:9 横屏\n"
        "【场景资产】@走廊\n"
        "【核心人物】@甲\n"
        "【站位声明】@甲（画面左）\n"
        "【时间轴分镜】\n"
        "[镜头1] 0-4秒，中景·平视·固定。甲开口。声音：无。台词：【甲（低沉）：“你好。”】\n"
        "[镜头2] 4-8秒，近景·平视·缓推。甲定格。声音：无。台词：无。\n"
        "【音效】环境音\n"
        "【强制禁止项】无字幕\n"
        "```\n"
    )
    d = parse_md(sample)
    assert len(d["segments"]) == 1 and len(d["segments"][0]["shots"]) == 2
    srt = export_srt_text(d)
    csv_txt = export_timeline_csv_text(d)
    html = build_html(d)
    assert "00:00:00,000 --> 00:00:04,000" in srt and "你好" in srt
    assert "镜1" in csv_txt and "exportSRT()" in html and "exportTimelineCSV()" in html

    # ---- 2026-10-14 Agent 修复回归锁：半秒时码 MM:SS.s 必须被正确解析，且不得丢镜 ----
    for _tok, _exp in (("00:10.5", 10.5), ("00:03.5", 3.5), ("00:12.5", 12.5),
                       ("00:04", 4.0), ("12.5", 12.5), ("0-3秒", None)):
        if _exp is not None:
            _got = to_seconds(_tok)
            assert abs(_got - _exp) < 1e-9, f"to_seconds({_tok!r}) = {_got}，应为 {_exp}"
    sample2 = (
        "# 半秒时码回归用例\n"
        "## 【投喂单元 1/1 · 段1】\n"
        "```text\n"
        "【画幅风格】16:9 横屏\n"
        "【场景资产】@走廊\n"
        "【核心人物】@甲\n"
        "【站位声明】@甲（画面左）\n"
        "【时间轴分镜】\n"
        "00:00-00:04 [镜头1] 中景 · 平视 · 固定。甲开口。声音：无。台词：【甲（低沉）：“一。”】\n"
        "00:04-00:08 [镜头2] 近景 · 平视 · 缓推。甲转头。声音：无。台词：无。\n"
        "00:08-00:10.5 [镜头3] 特写 · 平视 · 固定。甲眨眼。声音：无。台词：无。\n"
        "00:10.5-00:12.5 [镜头4] 近景 · 斜角 · 极缓慢推。甲抬手。声音：无。台词：无。\n"
        "00:12.5-00:15 [镜头5] 中景 · 正面 · 缓拉。甲定格。声音：无。台词：无。\n"
        "【音效】环境音\n"
        "【强制禁止项】无字幕\n"
        "```\n"
    )
    d2 = parse_md(sample2)
    _shots2 = d2["segments"][0]["shots"]
    assert len(_shots2) == 5, f"半秒时码稿应解析出 5 镜，实得 {len(_shots2)} 镜（丢镜即本用例拦截目标）"
    assert abs(_shots2[2]["end"] - 10.5) < 1e-9 and abs(_shots2[3]["start"] - 10.5) < 1e-9, \
        "半秒时码应解为 10.5s（原缺陷为 10.05s）"
    assert not any("丢镜" in w["msg"] or "跳过" in w["msg"] for w in d2["warnings"]), \
        f"半秒时码稿不应报丢镜告警：{[w['msg'] for w in d2['warnings']]}"

    # ---- 2026-10-15 Agent 修复回归锁：SRT 毫秒进位 ----
    #   原 `_fmt` 用 `ms=int(round((sec%1)*1000))` + `ts=int(sec)` 分立取整，
    #   小数位进位到 1000ms（如 4.9995→round(999.5)=1000）会印出非法 `,1000` 且秒位不结转。
    #   改为「总毫秒一次取整再拆分」后，4.9995s 必须结转为 00:00:05,000。
    _d3 = parse_md(
        "# SRT进位\n"
        "## 【投喂单元 1/1 · 段1】\n"
        "```text\n"
        "【画幅风格】16:9 横屏\n"
        "【场景资产】@走廊\n"
        "【核心人物】@甲\n"
        "【站位声明】@甲（画面左）\n"
        "【时间轴分镜】\n"
        "0-4.9995s [镜头1] 中景。甲。台词：【甲：“进位测试。”】\n"
        "```\n"
    )
    _srt3 = export_srt_text(_d3)
    assert ",1000" not in _srt3, f"SRT 毫秒不得进位成非法 ,1000：{_srt3!r}"
    assert "00:00:05,000" in _srt3, f"4.9995s 应结转为 00:00:05,000：{_srt3!r}"
    assert "00:00:00,000 --> 00:00:05,000" in _srt3, f"进位后起止应连续：{_srt3!r}"
    print("[+] build_board_lite self-test PASSED")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?")
    ap.add_argument("--out", default=None)
    ap.add_argument("--export-srt", default=None, help="同时导出 .srt 字幕文件")
    ap.add_argument("--export-csv", default=None, help="同时导出剪辑时间线 .csv 文件")
    ap.add_argument("--export-json", default=None, help="同时导出结构化 API 载荷 .json 文件")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    if not a.src:
        ap.print_help()
        sys.exit(2)
    src = Path(a.src)
    if not src.exists():
        print(f"[X] 源文件不存在：{src}")
        sys.exit(1)
    data = parse_md(src.read_text(encoding="utf-8"))
    out = Path(a.out) if a.out else src.with_name(src.stem + "_分镜看板.html")
    out.write_text(build_html(data), encoding="utf-8")
    n_shots = sum(len(s["shots"]) for s in data["segments"])
    print(f"[+] 段落：{len(data['segments'])} · 镜头：{n_shots} · 资产：{len(data['assets'])} · 出图提示词：{len(data['asset_prompts'])}")
    print(f"[+] 总时长：{total_duration(data):g}s · WARN：{len(data['warnings'])}")
    for w in data["warnings"]:
        print(f"    ⚠ {w['msg']}")
    print(f"[+] 看板：{out}")
    if a.export_srt:
        Path(a.export_srt).write_text(export_srt_text(data), encoding="utf-8")
        print(f"[+] SRT 字幕：{a.export_srt}")
    if a.export_csv:
        Path(a.export_csv).write_text(export_timeline_csv_text(data), encoding="utf-8")
        print(f"[+] 剪辑时间线 CSV：{a.export_csv}")
    if a.export_json:
        Path(a.export_json).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[+] API 载荷 JSON：{a.export_json}")


if __name__ == "__main__":
    main()
