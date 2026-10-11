# -*- coding: utf-8 -*-
"""合成音效：用 ffmpeg 生成 7 个基础占位音效（重低音冲击、甩镜嗖、蓄力上扬、水花炸裂、低吼震颤、水晶叮、入水闷响）。
用法：python 合成音效.py [输出目录]（默认 ./音效库）
这些只是占位：冲击与低吼的低频尚可，"嗖"和水花偏电子；正式版建议换成剪映音效库里挑的真实音效。
依赖：ffmpeg 在 PATH 中。
"""
import os
import subprocess
import sys

SFX = {
    "重低音冲击.wav": ("0.9*sin(2*PI*(60-30*t)*t)*exp(-2.6*t)+0.5*(random(0)*2-1)*exp(-9*t)", 1.6,
                   "lowpass=f=180,lowpass=f=180,volume=2.2,alimiter=limit=0.95,afade=t=out:st=1.2:d=0.4"),
    "甩镜嗖.wav": ("(random(0)*2-1)*pow(sin(PI*t/0.7),2)", 0.7,
                "bandpass=f=900:width_type=o:w=2,highpass=f=250,volume=1.8,alimiter=limit=0.9"),
    "蓄力上扬.wav": ("0.5*sin(2*PI*(150*t+260*t*t))*pow(t/1.4,2)+0.35*(random(0)*2-1)*pow(t/1.4,3)", 1.4,
                 "highpass=f=120,volume=1.6,alimiter=limit=0.9"),
    "水花炸裂.wav": ("(random(0)*2-1)*exp(-5*t)", 1.0,
                 "highpass=f=700,lowpass=f=7000,volume=1.4,alimiter=limit=0.9"),
    "低吼震颤.wav": ("(random(0)*2-1)*(0.6+0.4*sin(2*PI*7*t))*sin(PI*t/1.8)", 1.8,
                 "lowpass=f=140,lowpass=f=140,volume=4,alimiter=limit=0.9"),
    "水晶叮.wav": ("(0.5*sin(2*PI*1760*t)+0.35*sin(2*PI*2637*t)+0.25*sin(2*PI*3520*t)+0.15*sin(2*PI*5274*t))*exp(-3.2*t)", 1.8,
                "volume=1.2,alimiter=limit=0.9,afade=t=out:st=1.4:d=0.4"),
    "入水闷响.wav": ("0.9*sin(2*PI*(140-60*t)*t)*exp(-9*t)+0.4*(random(0)*2-1)*exp(-14*t)", 0.6,
                 "lowpass=f=600,volume=1.8,alimiter=limit=0.9"),
}


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for name, (expr, dur, af) in SFX.items():
        path = os.path.join(out_dir, name)
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"aevalsrc='{expr}':s=48000:d={dur}",
               "-af", af, path]
        subprocess.run(cmd, check=True)
        print("已生成", path)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "音效库")
