#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成短剧全片 12 节拍情绪张力曲线 PNG。

用法：
    python3 generate_emotion_curve.py [-o OUT] [-i BEATS_JSON]

示例：
    python3 generate_emotion_curve.py                      # 默认 12 节拍 → emotion_beat_curve.png
    python3 generate_emotion_curve.py -o curve.png         # 指定输出文件
    python3 generate_emotion_curve.py -i beats.json        # 自定义节拍（[{"name":"起势","value":3.5}, ...]）
"""
import argparse
import json
import os
import sys

# matplotlib 为可选依赖（缺依赖给安装指引，不抛裸 Traceback）
try:
    import matplotlib
    import matplotlib.pyplot as plt
except ImportError:
    print("[-] 缺少依赖：本脚本需要 matplotlib 才能出图。安装：pip install matplotlib")
    print("    （不影响包内其余机检与投喂链路——情绪曲线为可选交付物，节拍数据仍可按 12 节拍手写进投喂稿）")
    sys.exit(2)

# ── 中文字体检测与配置（Windows / macOS / Linux 三平台回退 · 2026-10-11 Windows 修复）──
def _setup_cjk_font():
    """为 matplotlib 配置可用的中文字体，避免图形中文变方块（全平台版）。"""
    from matplotlib import font_manager

    candidates = [
        # Windows（C:/Windows/Fonts）
        "C:/Windows/Fonts/msyh.ttc",     # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",   # 黑体
        "C:/Windows/Fonts/simsun.ttc",   # 宋体
        "C:/Windows/Fonts/Deng.ttf",     # 等线
        # macOS
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        # Linux
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    ]
    for path in candidates:
        if not os.path.exists(path):
            continue
        try:
            font_manager.fontManager.addfont(path)
            name = font_manager.FontProperties(fname=path).get_name()
            matplotlib.rcParams["font.family"] = name
            matplotlib.rcParams["axes.unicode_minus"] = False
            return name
        except Exception:
            continue

    # 兜底：按常见中文字体名扫描系统已装字体（matplotlib 自带索引）
    wanted = ["Microsoft YaHei", "SimHei", "SimSun", "DengXian",
              "PingFang SC", "Hiragino Sans GB", "Songti SC",
              "Noto Sans CJK SC", "Source Han Sans SC", "WenQuanYi Micro Hei"]
    try:
        installed = {f.name for f in font_manager.fontManager.ttflist}
    except Exception:
        installed = set()
    for name in wanted:
        if name in installed:
            matplotlib.rcParams["font.family"] = name
            matplotlib.rcParams["axes.unicode_minus"] = False
            return name

    print("[!] 未找到可用中文字体：图中中文可能显示为方块。")
    print("    Windows：请确认 C:/Windows/Fonts/msyh.ttc（微软雅黑）存在；")
    print("    Linux：可安装 fonts-noto-cjk 或 wqy-microhei 后重试。")
    return None

_setup_cjk_font()

def plot_emotion_curve(beats=None, output_png="emotion_beat_curve.png"):
    """
    绘制 12 节拍短剧全片情绪张力曲线
    """
    if beats is None:
        beats = [
            ("1.起势", 3.5),
            ("2.冲突", 5.0),
            ("3.硬刚", 6.5),
            ("4.对峙", 7.2),
            ("5.蓄势", 4.2),
            ("6.危机", 8.2),
            ("7.高潮", 9.0),
            ("8.绝境", 6.2),
            ("9.反杀", 9.6),
            ("10.终局", 8.0),
            ("11.余波", 7.2),
            ("12.收尾", 4.5)
        ]
    
    names = [b[0] for b in beats]
    scores = [b[1] for b in beats]
    n = len(beats)
    idx = list(range(1, n + 1))

    plt.figure(figsize=(max(8, n * 0.85), 5), dpi=150)
    plt.plot(idx, scores, marker="o", color="#C23B22", linewidth=2.5, markersize=8)

    for i, (name, val) in enumerate(beats):
        plt.text(i + 1, val + 0.25, f"{val}\n{name}", ha="center", fontsize=9, fontweight="bold")

    plt.axhspan(8.5, 10.0, color="#C23B22", alpha=0.15, label="高潮/反杀区")
    plt.axhspan(6.5, 8.5, color="#E67E22", alpha=0.10, label="动作/对峙区")
    plt.axhspan(0, 6.5, color="#3498DB", alpha=0.08, label="发展/蓄势区")

    plt.title(f"短剧全片 {n} 节拍情绪张力曲线 (Emotion Beat Curve)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("节拍序号 (Beat Index)", fontsize=11)
    plt.ylabel("戏剧张力 / 情绪值 (0~10)", fontsize=11)
    plt.ylim(0, 11)
    plt.xticks(idx)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(output_png)
    print(f"[+] Emotion curve saved successfully to: {output_png}")


def _load_beats(path):
    """从 JSON 文件读取自定义节拍：支持 [{"name":..,"value":..}] 或 [["name", value], ...]。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        sys.exit(f"[X] 节拍文件不存在：{path}")
    except json.JSONDecodeError as e:
        sys.exit(f"[X] 节拍 JSON 解析失败：{e}")
    beats = []
    try:
        for item in raw:
            if isinstance(item, dict):
                beats.append((str(item["name"]), float(item["value"])))
            else:
                beats.append((str(item[0]), float(item[1])))
    except (KeyError, IndexError, TypeError, ValueError) as e:
        sys.exit(f"[X] 节拍格式错误（需 name/value 或 [name, value]）：{e}")
    if not beats:
        sys.exit("[X] 节拍列表为空")
    return beats


def main():
    ap = argparse.ArgumentParser(
        prog="generate_emotion_curve.py",
        description="生成短剧全片情绪张力曲线 PNG（默认 12 节拍）。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("-o", "--out", default="emotion_beat_curve.png",
                    help="输出 PNG 路径（默认 emotion_beat_curve.png）")
    ap.add_argument("-i", "--input", default=None,
                    help="自定义节拍 JSON 文件（[{\"name\":\"起势\",\"value\":3.5}, ...]）")
    args = ap.parse_args()

    out = args.out
    if out in ("-h", "--help"):
        ap.error("输出路径不能是 -h/--help")
    if not out.lower().endswith(".png"):
        out += ".png"
    out_dir = os.path.dirname(os.path.abspath(out))
    if not os.path.isdir(out_dir):
        sys.exit(f"[X] 输出目录不存在：{out_dir}")

    beats = _load_beats(args.input) if args.input else None
    plot_emotion_curve(beats=beats, output_png=out)


if __name__ == "__main__":
    main()
