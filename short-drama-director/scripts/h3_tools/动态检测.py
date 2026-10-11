# -*- coding: utf-8 -*-
"""动态检测：逐 0.5 秒统计相邻帧运动量，标出"定格"和"冲一下就停"。
用法：python 动态检测.py [--动作] <视频.mp4> [更多视频...]
  默认按文戏标准（合格 3 / 定格 2）；加 --动作 按动作段标准（合格 6 / 定格 3，均值需 ≥ 8）。
依赖：ffmpeg 在 PATH 中。
"""
import re
import subprocess
import sys

BUCKET = 0.5      # 秒
FREEZE = 2.0      # 低于此值视为几乎静止
OK = 3.0          # 合格线
SPIKE = 12.0      # 猛冲阈值
MEAN_OK = 0.0     # 全片均值下限（动作段才启用）


def motion_series(path):
    cmd = ["ffmpeg", "-hide_banner", "-i", path, "-an", "-vf",
           "scale=168:-2,tblend=all_mode=difference,signalstats,"
           "metadata=print:key=lavfi.signalstats.YAVG", "-f", "null", "-"]
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore").stderr
    fps = 24.0
    m = re.search(r"(\d+(?:\.\d+)?) fps", out)
    if m:
        fps = float(m.group(1))
    vals = [float(v) for v in re.findall(r"YAVG=([0-9.]+)", out)]
    return fps, vals


def report(path):
    fps, vals = motion_series(path)
    per = max(1, int(round(fps * BUCKET)))
    buckets = [sum(vals[i:i + per]) / len(vals[i:i + per]) for i in range(0, len(vals), per)]
    print(f"\n== {path}")
    print("  ".join(f"{i*BUCKET:.1f}s:{b:.1f}" for i, b in enumerate(buckets)))
    problems = []
    run = 0
    for i, b in enumerate(buckets):
        run = run + 1 if b < FREEZE else 0
        if run * BUCKET == 1.0:
            problems.append(f"定格：{(i - run + 1) * BUCKET:.1f}s 起连续 ≥1s 运动量 < {FREEZE}")
        if b > SPIKE and i + 2 < len(buckets) and max(buckets[i + 1:i + 3]) < OK:
            problems.append(f"冲一下就停：{i * BUCKET:.1f}s 冲到 {b:.1f}，随后 1s 内跌到 < {OK}")
    low = sum(1 for b in buckets if b < OK)
    mean = sum(buckets) / len(buckets)
    print(f"全片均值 {mean:.1f}；低于合格线 {OK} 的分桶：{low}/{len(buckets)}")
    if MEAN_OK and mean < MEAN_OK:
        problems.append(f"整体偏慢：均值 {mean:.1f} < {MEAN_OK}（动作段看起来会像慢速幻灯片）")
    print("\n".join(problems) if problems else "未发现定格或猛冲后停住")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    args = sys.argv[1:]
    if args and args[0] == "--动作":
        args = args[1:]
        FREEZE, OK, MEAN_OK = 3.0, 6.0, 8.0
    for p in args:
        report(p)
