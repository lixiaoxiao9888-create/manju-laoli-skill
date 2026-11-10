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
# ★P11 修（2026-10-24）：旧版在 import 失败处直接 sys.exit(2)，于是 `--self-test`
#   在无 matplotlib 的环境里**根本跑不起来**——本脚本因此既没有自测，
#   也没人发现它没有自测（check_package 的旧 ◑25 只查源码里有没有 "--self-test" 字符串）。
#   改为「模块恒可加载、绘图时再报错」：让节拍解析这部分纯逻辑在任何环境下都能被验证，
#   绘图部分在依赖缺失时明确标 SKIP，而不是假装通过。
_MPL_OK = True
_MPL_ERR = ""
try:
    import matplotlib
    matplotlib.use("Agg")          # 无显示环境（服务器 / CI）也能出图
    import matplotlib.pyplot as plt
except Exception as _exc:          # ImportError 及后端初始化异常都归这里
    plt = None
    _MPL_OK = False
    _MPL_ERR = f"{type(_exc).__name__}: {_exc}"

_MPL_HINT = ("[-] 缺少依赖：本脚本需要 matplotlib 才能出图。安装：pip install matplotlib\n"
             "    （不影响包内其余机检与投喂链路——情绪曲线为可选交付物，"
             "节拍数据仍可按 12 节拍手写进投喂稿）")

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
    if not _MPL_OK:
        raise RuntimeError("matplotlib 不可用：" + _MPL_ERR)
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


def self_test():
    """★P11 新增（2026-10-24）：本脚本此前完全游离在自测体系外。
    分两层验：① 节拍解析（纯逻辑，任何环境都验）；② 出图（需 matplotlib，缺失则 SKIP 不冒充通过）。"""
    import tempfile
    ok = True
    dm = tempfile.mkdtemp()
    p1 = os.path.join(dm, "beats_dict.json")
    with open(p1, "w", encoding="utf-8") as f:
        json.dump([{"name": "起势", "value": 3.5}, {"name": "高潮", "value": 9}], f)
    b1 = _load_beats(p1)
    if b1 != [("起势", 3.5), ("高潮", 9.0)]:
        print("FAIL self-test: dict 形态节拍解析错误", b1); ok = False
    p2 = os.path.join(dm, "beats_list.json")
    with open(p2, "w", encoding="utf-8") as f:
        json.dump([["起势", 3.5]], f)
    if _load_beats(p2) != [("起势", 3.5)]:
        print("FAIL self-test: 数组形态节拍解析错误", _load_beats(p2)); ok = False
    p3 = os.path.join(dm, "beats_empty.json")
    with open(p3, "w", encoding="utf-8") as f:
        json.dump([], f)
    try:
        _load_beats(p3)
        print("FAIL self-test: 空节拍列表未被拦截"); ok = False
    except SystemExit:
        pass
    if _MPL_OK:
        out = os.path.join(dm, "curve.png")
        try:
            plot_emotion_curve(output_png=out)
        except Exception as exc:
            print(f"FAIL self-test: 绘图异常 {type(exc).__name__}: {exc}"); ok = False
        else:
            if not os.path.exists(out) or os.path.getsize(out) < 2000:
                print("FAIL self-test: PNG 未生成或体积异常"); ok = False
        out2 = os.path.join(dm, "curve2.png")
        try:
            plot_emotion_curve(beats=[("A", 3.0), ("B", 9.0)], output_png=out2)
            if not os.path.exists(out2):
                print("FAIL self-test: 自定义节拍未生成 PNG"); ok = False
        except Exception as exc:
            print(f"FAIL self-test: 自定义节拍绘制失败 {type(exc).__name__}"); ok = False
    else:
        print(f"[SKIP] matplotlib 不可用（{_MPL_ERR[:70]}）——仅验证节拍解析，绘图路径未验证")
    print('[+] self-test PASSED' if ok else 'FAIL self-test')
    return ok


def main():
    if not _MPL_OK:
        print(_MPL_HINT)
        sys.exit(2)
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
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    main()
