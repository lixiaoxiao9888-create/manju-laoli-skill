# -*- coding: utf-8 -*-
"""渲染整集：按 拼接草稿.py 同一份 JSON 剪辑方案，用 ffmpeg 直接渲染成片 mp4（含变速/推/震/冲/闪、压低原声、音效、背景音乐）。

用法：
  python 渲染整集.py <剪辑方案.json> <输出.mp4> [--宽 1080 --高 1920]

方案格式同 拼接草稿.py；另外每个段落可加（只影响本脚本，剪映草稿里请手动对应）：
  "画面": {"裁切": [x, y, w, h]}          该段先按比例裁掉穿帮区域再放大回画幅（0~1 的相对坐标）
  "分段" 里每段可再加 +镜（水平镜像，用于修正左右关系）
背景音乐写法同 拼接草稿.py："背景音乐": {"文件": ..., "音量": 0.45}。
依赖：ffmpeg、ffprobe 在 PATH。
"""
import json
import tempfile
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib

jy = importlib.import_module("生成剪映草稿")
cut = importlib.import_module("动作剪辑")

PUSH_MAX = 1.25
SHAKE_AMP_X, SHAKE_AMP_Y, SHAKE_DECAY = 18, 13, 1.6


def parse(spec):
    mirror = spec.endswith("+镜") or "+镜+" in spec
    seg = jy.parse_full(spec.replace("+镜", ""))
    seg["mirror"] = mirror
    return seg


FONT = "C\\:/Windows/Fonts/msyhbd.ttc"   # drawtext 里冒号要转义


def wrap_sub(text, limit=12):
    """超过 limit 字折成两行：优先在中间附近（±4 字内）的标点后断，否则从正中断。"""
    if len(text) <= limit:
        return [text]
    mid = len(text) / 2
    cuts = [i + 1 for i, ch in enumerate(text[:-1]) if ch in "，、；…—" and abs(i + 1 - mid) <= 4 and text[i + 1] not in "—…"]
    if not cuts:   # 中间附近没标点：任何标点只要两行都不超过 14 字也行，免得把词拆开
        cuts = [i + 1 for i, ch in enumerate(text[:-1]) if ch in "，、；" and max(i + 1, len(text) - i - 1) <= 14]
    i = min(cuts, key=lambda c: abs(c - mid)) if cuts else round(mid)
    return [text[:i], text[i:]]


def build(plan_path, out, W=1080, H=1920):
    base = os.path.dirname(os.path.abspath(plan_path))
    plan = json.load(open(plan_path, encoding="utf-8"))
    fill = float(plan.get("画面填充", 1.0))
    inputs, chains, labels = [], [], []
    sfx, dips, subs, plates = [], [], [], []
    cursor = 0.0
    k = 0
    for part in plan["段落"]:
        src = os.path.join(base, part["素材"])
        inputs.append(src)
        ii = len(inputs) - 1
        crop = part.get("画面", {}).get("裁切")
        part_start = cursor
        for entry in part["分段"]:
            spec, zoom, (fx, fy) = jy.seg_entry(entry)
            full = parse(spec)
            for p in jy.expand(full):
                a, b, sp = p["a"], p["b"], p["sp"]
                dur = (b - a) / sp
                nfr = max(1, round(dur * 24))   # 帧精确：每小段画面固定 nfr 帧，声音裁/补到同样时长（否则每段多 ~1 帧，整集累计音画错位 ~1s）
                dur = nfr / 24
                v = f"[{ii}:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp}"
                if crop:
                    x, y, w, h = crop
                    v += f",crop=iw*{w}:ih*{h}:iw*{x}:ih*{y}"
                if full["mirror"]:
                    v += ",hflip"
                # 铺满画幅（cover）再按 画面填充 放大
                zf = fill * zoom
                v += (f",scale={W}*{zf}:{H}*{zf}:force_original_aspect_ratio=increase,"
                      f"crop={W}:{H}:'max(0,min(iw-{W},iw*{fx}-{W}/2))':'max(0,min(ih-{H},ih*{fy}-{H}/2))',"
                      f"setsar=1,fps=24")
                if p["push"]:
                    frames = max(1, round(dur * 24))
                    v += (f",zoompan=z='1+{PUSH_MAX - 1}*pow(on/{frames}\\,2)'"
                          f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps=24")
                if p["shake"] and p["first"]:
                    v += (f",scale=iw*1.08:ih*1.08,crop={W}:{H}"
                          f":x='(iw-ow)/2+{SHAKE_AMP_X}*sin(t*55)*exp(-t*{SHAKE_DECAY})'"
                          f":y='(ih-oh)/2+{SHAKE_AMP_Y}*cos(t*47)*exp(-t*{SHAKE_DECAY})'")
                if p["flash"] and p["first"]:
                    v += ",fade=t=in:st=0:d=0.09:color=white"
                chains.append(v + f",tpad=stop_mode=clone:stop=4,trim=end_frame={nfr},setpts=PTS-STARTPTS,setsar=1[v{k}]")
                aud = f"[{ii}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo"
                if sp != 1:
                    aud += "," + cut.atempo_chain(sp)
                aud += f",apad,atrim=0:{dur:.6f},asetpts=PTS-STARTPTS"
                chains.append(aud + f"[a{k}]")
                labels.append(f"[v{k}][a{k}]")
                k += 1
                cursor += dur
        s, d = jy.parse_extras([f"音效:{x}" for x in part.get("音效", [])] +
                               [f"静:{x}" for x in part.get("静", [])])
        sfx += [(part_start + t, path, vol) for t, path, vol in s]
        subs += [(part_start + float(x["起"]), part_start + float(x["止"]), x["文"], x.get("类型", "")) for x in part.get("字幕", [])]
        plates += [(part_start + float(x["起"]), x) for x in part.get("人名条", [])]
        dips += [(part_start + a, part_start + b, vol) for a, b, vol in d]
    total = cursor
    chains.append("".join(labels) + f"concat=n={k}:v=1:a=1[vcat0][acat]")
    # 字幕：白字黑描边，下三分之一；类型 OS（心声/画外）用淡蓝色。每条一个 drawtext，文字走 textfile 避免转义问题
    vlab, tmpfiles = "[vcat0]", []
    n = 0
    for a, b, text, kind in subs:
        if kind == "标题":   # 居中大字（片尾"下一单元"、章节卡）：华文行楷金色，淡入淡出 0.4s
            tf = os.path.join(tempfile.gettempdir(), f"sub_{os.getpid()}_{n}.txt")
            open(tf, "w", encoding="utf-8").write(text)
            tmpfiles.append(tf)
            al = f"if(lt(t,{a}+0.4),(t-{a})/0.4,if(gt(t,{b}-0.4),({b}-t)/0.4,1))"
            chains.append(f"{vlab}drawtext=fontfile='C\\:/Windows/Fonts/STXINGKA.TTF':textfile='{tf.replace(chr(92), '/').replace(':', chr(92) + ':')}':"
                          f"fontsize=110:fontcolor=0xE8C478:alpha='{al}':shadowx=0:shadowy=0:borderw=2:bordercolor=0x3A2A10:"
                          f"x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,{a:.3f},{b:.3f})'[vs{n}]")
            vlab = f"[vs{n}]"
            n += 1
            continue
        color = "0xBFE6FF" if kind == "OS" else "white"
        lines = wrap_sub(text)
        for j, line in enumerate(lines):   # 每行单独一个 drawtext，各自居中
            tf = os.path.join(tempfile.gettempdir(), f"sub_{os.getpid()}_{n}.txt")
            open(tf, "w", encoding="utf-8").write(line)
            tmpfiles.append(tf)
            y = f"h*0.70+{(j - (len(lines) - 1)) * 80}"
            chains.append(f"{vlab}drawtext=fontfile='{FONT}':textfile='{tf.replace(chr(92), '/').replace(':', chr(92) + ':')}':"
                          f"fontsize=62:fontcolor={color}:borderw=6:bordercolor=black:shadowx=2:shadowy=3:shadowcolor=black@0.6:"
                          f"x=(w-text_w)/2:y={y}:enable='between(t,{a:.3f},{b:.3f})'[vs{n}]")
            vlab = f"[vs{n}]"
            n += 1
    for j, (t0, x) in enumerate(plates):   # 人名条：先用 人名条.py 渲染带透明通道的 mov，再按时间叠上
        mov = os.path.join(tempfile.gettempdir(), f"plate_{os.getpid()}_{j}.mov")
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "人名条.py"), "--名", x["名"],
                        "--身份", x.get("身份", ""), "--印", x.get("印", ""), "--侧", x.get("侧", "左"),
                        "--时长", str(x.get("时长", 2.0)), "--输出", mov], check=True, capture_output=True)
        tmpfiles.append(mov)
        inputs.append(mov)
        ii = len(inputs) - 1
        chains.append(f"[{ii}:v]setpts=PTS-STARTPTS+{t0:.3f}/TB[pl{j}];{vlab}[pl{j}]overlay=0:0:eof_action=pass[vp{j}]")
        vlab = f"[vp{j}]"
    chains.append(f"{vlab}null[vcat]")
    # 压低原声
    adip = "[acat]"
    for i, (a, b, vol) in enumerate(dips):
        chains.append(f"{adip}volume={vol}:enable='between(t,{a:.3f},{b:.3f})'[ad{i}]")
        adip = f"[ad{i}]"
    mix = [adip]
    for t, path, vol in sfx:
        inputs.append(path)
        ii = len(inputs) - 1
        ms = int(round(t * 1000))
        chains.append(f"[{ii}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},adelay={ms}|{ms}[s{ii}]")
        mix.append(f"[s{ii}]")
    bgm = plan.get("背景音乐")
    if bgm:
        inputs.append(os.path.join(base, bgm["文件"]))
        ii = len(inputs) - 1
        chains.append(f"[{ii}:a]aresample=48000,aformat=channel_layouts=stereo,volume={bgm.get('音量', 0.5)},"
                      f"afade=t=out:st={max(0, total - 1.0):.2f}:d=1.0[bgm]")
        mix.append("[bgm]")
    chains.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,"
                  f"atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
    fc = ";\n".join(chains)
    script = out + ".filter.txt"
    with open(script, "w", encoding="utf-8") as f:
        f.write(fc)
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for p in inputs:
        cmd += ["-i", p]
    cmd += ["-/filter_complex", script, "-map", "[vcat]", "-map", "[aout]",
            "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    os.remove(script)
    for tf in tmpfiles:
        os.remove(tf)
    print(f"已渲染 {out}，约 {total:.1f} 秒，片段 {k}，音效 {len(sfx)}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    W = int(args[args.index("--宽") + 1]) if "--宽" in args else 1080
    H = int(args[args.index("--高") + 1]) if "--高" in args else 1920
    build(args[0], args[1], W, H)
