#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sd-feed-engine V8.2.0-SLIM 提示词一键防穿帮清洗器（--autofix）

功能：
1. 自动清理【画幅风格】【STYLE】【场景资产】【核心人物】【PERFORMANCE】【时间轴分镜】【音效】前中段误写的「无文字水印/无字幕/无乱码/针对性禁项/严禁…」等禁项，并全部归拢到文末【强制禁止项】；
2. 自动校正【STYLE｜视觉风格】紧跟【画幅风格】之下、【PERFORMANCE｜表演与动作】紧跟【核心人物】之下（不再放在文末）。

用法:
    python sd-feed-engine/scripts/autofix_feed.py <投喂稿.md> [-o fixed.md]
    python sd-feed-engine/scripts/autofix_feed.py --self-test
"""
import argparse
import re
import sys

EARLY_NEG_RE = re.compile(r"[，,、\s]*(?:无文字水印|无文字|无水印|无字幕|无乱码)")


def autofix_text(text):
    collected_bans = []
    style_block = []
    perf_block = []
    other_lines = []

    cur_tag = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("【STYLE｜") or s.startswith("【STYLE|"):
            cur_tag = "STYLE"
            style_block.append(line)
            continue
        if s.startswith("【PERFORMANCE｜") or s.startswith("【PERFORMANCE|"):
            cur_tag = "PERF"
            perf_block.append(line)
            continue
        if s.startswith("【"):
            cur_tag = "OTHER"

        if cur_tag == "STYLE":
            if s.startswith("针对性禁项"):
                collected_bans.append(re.sub(r"^针对性禁项\s*[:：]\s*", "", s).replace(" / ", "、"))
                continue
            style_block.append(line)
            continue
        if cur_tag == "PERF":
            m_ban = re.search(r"[，,；;]?\s*(严禁[^，。；\n]+)", line)
            if m_ban:
                collected_bans.append(m_ban.group(1))
                line = line[:m_ban.start()] + line[m_ban.end():]
                line = line.rstrip("，,；; ")
            if line.strip():
                perf_block.append(line)
            continue

        other_lines.append(line)

    # Strip early negative words from non-ban lines & reorder STYLE/PERF right after 画幅风格 / 核心人物
    out_lines = []
    in_ban_section = False
    removed_count = len(collected_bans)

    def _insert_after_section(lines_buf, target_prefix, block_to_insert):
        if not block_to_insert:
            return lines_buf
        res = []
        inserted = False
        i = 0
        while i < len(lines_buf):
            res.append(lines_buf[i])
            if not inserted and lines_buf[i].strip().startswith(target_prefix):
                i += 1
                while i < len(lines_buf) and not lines_buf[i].strip().startswith("【"):
                    res.append(lines_buf[i])
                    i += 1
                res.extend(block_to_insert)
                inserted = True
                continue
            i += 1
        if not inserted:
            res = block_to_insert + res
        return res

    for line in other_lines:
        s = line.strip()
        if s.startswith("【强制禁止项】"):
            in_ban_section = True
            if collected_bans:
                extra = "、".join(collected_bans)
                line = line.rstrip("。") + "，" + extra + "。"
            if "水印" not in line and "字幕" not in line:
                line = line.rstrip("。") + "，禁止任何字幕、文字、乱码或水印。"
            out_lines.append(line)
            continue
        if s.startswith("【") and not s.startswith("【强制禁止项】"):
            in_ban_section = False
        if not in_ban_section and EARLY_NEG_RE.search(line):
            new_line = EARLY_NEG_RE.sub("", line)
            new_line = re.sub(r"([：:])[，,、\s]+", r"\1", new_line)
            if new_line != line:
                removed_count += 1
            out_lines.append(new_line)
        else:
            out_lines.append(line)

    if not in_ban_section and collected_bans and not any(l.strip().startswith("【强制禁止项】") for l in out_lines):
        out_lines.append("【强制禁止项】：" + "、".join(collected_bans) + "，禁止任何字幕、文字、乱码或水印。")

    out_lines = _insert_after_section(out_lines, "【画幅风格】", style_block)
    out_lines = _insert_after_section(out_lines, "【核心人物】", perf_block)

    return "\n".join(out_lines) + ("\n" if text.endswith("\n") else ""), removed_count


def self_test():
    sample = (
        "【画幅风格】：16:9 横屏，电影写实，无文字水印。\n"
        "【场景资产】：@SCN-破庙\n"
        "【核心人物】：@主角（30岁男）\n"
        "【时间轴分镜】：00:00-00:03 特写，纸面无乱码。\n"
        "【强制禁止项】：禁止穿模。\n"
        "【STYLE｜视觉风格 · 全片锁死】\n"
        "成像底层：虚幻5 CG\n"
        "针对性禁项：禁2D卡通描边 / 禁现代建筑元素\n"
        "【PERFORMANCE｜表演与动作 · 全片锁死】\n"
        "每招必现真实发力重量感，严禁轻飘悬浮\n"
    )
    fixed, cnt = autofix_text(sample)
    assert cnt >= 4, f"应清理并归拢至少4处禁项，实得 {cnt}"
    assert "针对性禁项" not in fixed.split("【强制禁止项】")[0]
    assert "严禁轻飘悬浮" not in fixed.split("【强制禁止项】")[0]
    assert fixed.index("【STYLE｜") < fixed.index("【场景资产】")
    assert fixed.index("【PERFORMANCE｜") < fixed.index("【时间轴分镜】")
    assert "禁2D卡通描边" in fixed.split("【强制禁止项】")[1]
    assert "严禁轻飘悬浮" in fixed.split("【强制禁止项】")[1]
    print("[+] autofix_feed.py self-test PASSED")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    p = argparse.ArgumentParser(description="sd-feed-engine V8.2.0-SLIM 提示词一键防穿帮清洗器")
    p.add_argument("feed_md", help="待清洗投喂稿 .md")
    p.add_argument("-o", "--out", default=None, help="输出路径（不传则覆盖原文件）")
    args = p.parse_args()
    txt = open(args.feed_md, encoding="utf-8").read()
    fixed, cnt = autofix_text(txt)
    target = args.out or args.feed_md
    with open(target, "w", encoding="utf-8").write(fixed) if False else open(target, "w", encoding="utf-8") as f:
        f.write(fixed)
    print(f"[+] 已调整 STYLE/PERFORMANCE 落位并归拢 {cnt} 处禁项至文末【强制禁止项】 -> {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
