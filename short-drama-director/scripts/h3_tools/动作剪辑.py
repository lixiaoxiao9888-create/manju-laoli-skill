# -*- coding: utf-8 -*-
"""动作剪辑：按分段给 H3 生成的视频变速、加关键帧猛推、加冲击震屏、曲线加速、冲击闪帧、砍尾，然后自动做动态检测。

用法：
  python 动作剪辑.py <输入.mp4> <输出.mp4> 段1 段2 ...

每段写成  起点-终点@倍速[+推][+震][+冲][+闪]，时间单位秒，例如：
  0.3-6@1.2  6-7.5@1.8  7.5-8.9@1+推  8.9-10.8@1+震+闪  2.9-5.1@1+冲
  +推：该段由慢到快放大到 1.25 倍（补"猛推"）
  +震：该段加由强到弱的震屏（冲击用）
  +冲：曲线加速——该段切成四小段，速度依次为 0.75/1.0/1.4/2.0 倍（乘以段倍速），先慢后快冲进下一刀
       （相当于剪映"曲线变速"的蓄力→爆发；不与 +推 同用）
  +闪：冲击闪帧——段首 2 帧由白闪入（命中瞬间的冲击帧）
最后一段的音频自动做 0.4 秒淡出。没写到的时间（如结尾定格）直接丢弃。
依赖：ffmpeg、ffprobe 在 PATH 中。
"""
import os
import re
import subprocess
import sys

PUSH_MAX = 1.25
SHAKE_AMP_X, SHAKE_AMP_Y, SHAKE_DECAY = 14, 10, 1.6
RAMP = (0.75, 1.0, 1.4, 2.0)   # 曲线加速四段的相对倍速


def probe_size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    w, h = out.split(",")[:2]
    return int(w), int(h)


def atempo_chain(speed):
    # atempo 单级范围 0.5~2.0，超出就串联
    parts, s = [], speed
    while s > 2.0:
        parts.append("atempo=2.0")
        s /= 2.0
    while s < 0.5:
        parts.append("atempo=0.5")
        s /= 0.5
    parts.append(f"atempo={s:.4f}")
    return ",".join(parts)


def parse(spec):
    m = re.fullmatch(r"([\d.]+)-([\d.]+)@([\d.]+)((?:\+推|\+震|\+冲|\+闪)*)", spec)
    if not m:
        raise SystemExit(f"段格式不对：{spec}（应为 起点-终点@倍速[+推][+震][+冲][+闪]）")
    a, b, sp, flags = float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4)
    if b <= a or sp <= 0:
        raise SystemExit(f"段数值不对：{spec}")
    seg = dict(a=a, b=b, sp=sp, push="+推" in flags, shake="+震" in flags,
               ramp="+冲" in flags, flash="+闪" in flags)
    if seg["ramp"] and seg["push"]:
        raise SystemExit(f"{spec}：+冲 不与 +推 同用")
    return seg


def expand(seg):
    """把一段展开成实际渲染的小片：普通段 1 片，曲线加速段 4 片。"""
    if not seg["ramp"]:
        return [dict(seg, first=True)]
    step = (seg["b"] - seg["a"]) / len(RAMP)
    out = []
    for k, r in enumerate(RAMP):
        out.append(dict(seg, a=seg["a"] + k * step, b=seg["a"] + (k + 1) * step, sp=seg["sp"] * r,
                        first=(k == 0)))
    return out


def build(inp, out, specs):
    w, h = probe_size(inp)
    pieces = [p for s in specs for p in expand(parse(s))]
    chains, labels = [], []
    for i, p in enumerate(pieces):
        a, b, sp = p["a"], p["b"], p["sp"]
        v = f"[0:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp}"
        if p["push"]:
            frames = max(1, round((b - a) / sp * 24))
            v += (f",zoompan=z='1+{PUSH_MAX - 1}*pow(on/{frames}\\,2)'"
                  f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}:fps=24")
        if p["shake"] and p["first"]:
            v += (f",scale=iw*1.08:ih*1.08,crop={w}:{h}"
                  f":x='(iw-ow)/2+{SHAKE_AMP_X}*sin(t*55)*exp(-t*{SHAKE_DECAY})'"
                  f":y='(ih-oh)/2+{SHAKE_AMP_Y}*cos(t*47)*exp(-t*{SHAKE_DECAY})'")
        if p["flash"] and p["first"]:
            v += ",fade=t=in:st=0:d=0.09:color=white"
        chains.append(v + f"[v{i}]")
        aud = f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS"
        if sp != 1:
            aud += "," + atempo_chain(sp)
        if i == len(pieces) - 1:
            dur = (b - a) / sp
            aud += f",afade=t=out:st={max(0, dur - 0.4):.3f}:d=0.4"
        chains.append(aud + f"[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    fc = ";".join(chains) + ";" + "".join(labels) + f"concat=n={len(pieces)}:v=1:a=1[v][a]"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", inp, "-filter_complex", fc,
           "-map", "[v]", "-map", "[a]", "-r", "24", "-c:v", "libx264", "-crf", "18",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", out]
    subprocess.run(cmd, check=True)
    total = sum((p["b"] - p["a"]) / p["sp"] for p in pieces)
    print(f"已输出 {out}，约 {total:.1f} 秒")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    build(sys.argv[1], sys.argv[2], sys.argv[3:])
    checker = os.path.join(os.path.dirname(os.path.abspath(__file__)), "动态检测.py")
    subprocess.run([sys.executable, checker, "--动作", sys.argv[2]])
