#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""short-drama-factory v5.1 抗上下文压缩滚动递进状态包生成器

用法:
    python scripts/rolling_checkpoint.py <剧本目录> [--ledger 台账.md] [--out rolling-state.md]
    python scripts/rolling_checkpoint.py --self-test
"""
import argparse
import os
import re
import sys

EP_NAME_RE = re.compile(r"^(?:EP|ep|第)?0*(\d+)(?:集)?\.md$")


def find_episodes(script_dir):
    eps = []
    if not os.path.isdir(script_dir):
        return eps
    for fn in os.listdir(script_dir):
        m = EP_NAME_RE.match(fn)
        if m:
            eps.append((int(m.group(1)), os.path.join(script_dir, fn)))
    eps.sort(key=lambda x: x[0])
    return eps


def extract_ep_summary(ep_num, text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    scenes = [re.sub(r"^(?:\[场景\]|【场景】|##?\s*场景)\s*[:：]?\s*", "", l)
              for l in lines if l.startswith(("[场景]", "【场景】"))]
    chars = []
    for l in lines:
        if l.startswith(("[人物]", "【人物】")):
            raw = re.sub(r"^(?:\[人物\]|【人物】)\s*[:：]?\s*", "", l)
            for c in re.split(r"[、,，/]", raw):
                c = re.sub(r"（[^）]*）|\([^)]*\)", "", c).strip()
                if c and c not in chars:
                    chars.append(c)
    hook = ""
    m = re.search(r"【本集断章卡点】\s*[:：]?\s*(.+)", text)
    if m:
        hook = m.group(1).strip()
    money = re.findall(r"\d+(?:\.\d+)?\s*(?:万|亿|千|百)?(?:元|两|块)", text)
    tail_actions = [l for l in lines if l.startswith("△")][-2:]
    return {
        "ep": ep_num,
        "scenes": scenes,
        "chars": chars,
        "hook": hook,
        "money": list(dict.fromkeys(money))[:8],
        "tail_actions": tail_actions,
    }


def build_checkpoint(script_dir, ledger_path=None):
    eps = find_episodes(script_dir)
    if not eps:
        return "# 滚动递进状态包\n\n> 未在目录中发现已写单集剧本（支持 `EP01.md` / `1.md` / `第1集.md`）。\n"

    summaries = []
    all_chars = []
    all_money = []
    for num, path in eps:
        txt = open(path, encoding="utf-8-sig").read()
        s = extract_ep_summary(num, txt)
        summaries.append(s)
        for c in s["chars"]:
            if c not in all_chars:
                all_chars.append(c)
        for m in s["money"]:
            if m not in all_money:
                all_money.append(m)

    ep_range = f"第 {summaries[0]['ep']}~{summaries[-1]['ep']} 集（共 {len(summaries)} 集）"
    recent = summaries[-2:]

    out = [
        f"# 抗上下文压缩滚动递进状态包（{ep_range}）",
        "",
        "> 批量连写时，仅挂载本状态包 + 最近 1~2 集尾段即可续写，严禁把前序全部正文塞进上下文。",
        "",
        "## 一、全局硬事实锚定",
        f"- **已写集数**：{ep_range}",
        f"- **已出场具名角色**：{'、'.join(all_chars) if all_chars else '（未标注 [人物] 行）'}",
        f"- **出现过的关键金额/数值**：{'、'.join(all_money) if all_money else '（暂无）'}",
    ]
    if ledger_path and os.path.isfile(ledger_path):
        out.append(f"- **关联台账**：`{os.path.basename(ledger_path)}`（已挂载）")

    out += ["", "## 二、最近两集尾态与接续接口（下一集开头必接）"]
    for s in recent:
        out.append(f"### 第 {s['ep']} 集")
        out.append(f"- **末场空间**：{s['scenes'][-1] if s['scenes'] else '（未标注）'}")
        out.append(f"- **尾段动作**：{' / '.join(s['tail_actions']) if s['tail_actions'] else '（无）'}")
        out.append(f"- **断章卡点**：{s['hook'] or '（缺失）'}")
        out.append("")

    return "\n".join(out)


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ep1 = os.path.join(td, "EP01.md")
        ep2 = os.path.join(td, "EP02.md")
        open(ep1, "w", encoding="utf-8").write(
            "第【1】集\n[场景]：内景·正堂·日\n[人物]：甲（主角）、乙\n△ 甲把二十万两银票拍在桌上。\n【本集断章卡点】：门被踹开。（黑屏）\n"
        )
        open(ep2, "w", encoding="utf-8").write(
            "第【2】集\n[场景]：内景·库房·夜\n[人物]：甲、丙\n△ 甲锁上库房铜锁。\n【本集断章卡点】：火把亮起。（黑屏）\n"
        )
        md = build_checkpoint(td)
        assert "第 1~2 集" in md, "应识别集数范围"
        assert "甲" in md and "丙" in md, "应汇总出场角色"
        assert "二十万两" in md or "20" in md or "库房" in md, "应提取关键尾态"
    print("[+] rolling_checkpoint.py self-test PASSED")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    p = argparse.ArgumentParser(description="short-drama-factory v5.1 滚动递进状态包生成器")
    p.add_argument("script_dir", help="已写单集剧本目录")
    p.add_argument("--ledger", default=None, help="台账路径")
    p.add_argument("--out", default=None, help="输出文件路径（默认打印到 stdout）")
    args = p.parse_args()
    md = build_checkpoint(args.script_dir, args.ledger)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[+] 已生成滚动状态包: {args.out}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
