#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sd-feed-engine V8.2.0-SLIM 结构化投喂包导出器（支持 JSON 与 CSV 批量导出）

用法:
    python sd-feed-engine/scripts/export_feed_bundle.py <投喂稿.md> [-o feed_bundle.json] [--csv feed_shots.csv]
    python sd-feed-engine/scripts/export_feed_bundle.py --self-test
"""
import argparse
import csv
import json
import re
import sys


def parse_feed_md(text):
    segments = []
    cur = None
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        m_seg = re.match(r"^#{1,3}\s*第\s*(\d+)\s*段|^【第\s*(\d+)\s*段", s)
        if m_seg:
            if cur:
                segments.append(cur)
            seg_id = int(m_seg.group(1) or m_seg.group(2))
            figs = []
            cur = {"segment": seg_id, "header": s, "fields": {}, "shots": [], "refs": figs}
            continue
        if cur is None:
            continue
        for fig in re.findall(r"图\d+", s):
            if fig not in cur["refs"]:
                cur["refs"].append(fig)
        m_field = re.match(r"^【([^】]+)】\s*[:：]?\s*(.*)$", s)
        if m_field:
            cur["fields"][m_field.group(1).strip()] = m_field.group(2).strip()
            continue
        m_shot = re.match(r"^(?:镜\s*\d+|Shot\s*\d+|\d+[-~]\d+s|\[\d+[-~]\d+s\]|\d{2}:\d{2}-\d{2}:\d{2})(.*)$", s, re.I)
        if m_shot:
            cur["shots"].append(s)
    if cur:
        segments.append(cur)
    return {
        "schema": "manju-laoli-skill/feed-bundle-v2",
        "segment_count": len(segments),
        "segments": segments,
    }


def write_csv(data, csv_path):
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["segment", "shot_index", "timecode_and_prompt", "ref_images", "aspect_style"])
        for seg in data["segments"]:
            refs = " ".join(seg.get("refs", []))
            style = seg["fields"].get("画幅风格", "")
            for idx, sh in enumerate(seg["shots"], 1):
                w.writerow([seg["segment"], idx, sh, refs, style])


def self_test():
    import os, tempfile
    sample = (
        "## 第1段（22s）\n"
        "【画幅风格】：16:9 横屏，电影写实\n"
        "【场景资产】：@SCN-正堂（图1/图2）\n"
        "【站位声明】：机位侧=南；固定可见锚=【正堂桌】\n"
        "00:00-00:04 中景，角色A（图3）推门入内。\n"
        "00:04-00:09 近景，角色B抬眼冷笑。\n"
    )
    res = parse_feed_md(sample)
    assert res["segment_count"] == 1
    assert len(res["segments"][0]["shots"]) == 2
    assert "图1" in res["segments"][0]["refs"] and "图3" in res["segments"][0]["refs"]
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tf:
        cp = tf.name
    write_csv(res, cp)
    csv_txt = open(cp, encoding="utf-8-sig").read()
    os.remove(cp)
    assert "00:00-00:04" in csv_txt and "图1" in csv_txt
    print("[+] export_feed_bundle.py self-test PASSED")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    p = argparse.ArgumentParser(description="sd-feed-engine V8.2.0-SLIM 结构化投喂包导出器")
    p.add_argument("feed_md", help="终检通过的投喂稿 .md")
    p.add_argument("-o", "--out", default=None, help="输出 JSON 文件路径")
    p.add_argument("--csv", default=None, help="输出逐镜 CSV 文件路径（适合多维表格/批处理）")
    args = p.parse_args()
    txt = open(args.feed_md, encoding="utf-8").read()
    data = parse_feed_md(txt)
    if args.csv:
        write_csv(data, args.csv)
        print(f"[+] 已导出逐镜 CSV: {args.csv}")
    js = json.dumps(data, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(js)
        print(f"[+] 已导出投喂包 JSON: {args.out}")
    elif not args.csv:
        print(js)
    return 0


if __name__ == "__main__":
    sys.exit(main())
