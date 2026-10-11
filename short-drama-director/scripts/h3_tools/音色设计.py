# -*- coding: utf-8 -*-
"""音色设计：用 MiniMax voice_design 接口，按文字描述给每个角色"捏"一个音色，存下试听音频当 H3 的参考音频（每段最多 3 条）。

用法（PowerShell）：
  $env:MINIMAX_API_KEY = "你的key"           # 只在当前窗口有效；key 不要写进任何文件
  python 工具/音色设计.py --列表              # 只列出角色和描述，不调用接口、不花钱
  python 工具/音色设计.py 主角A 角色C（男）        # 只做这几个角色
  python 工具/音色设计.py --全部
  python 工具/音色设计.py 主角A --版本 2        # 同一角色再抽一版（存成 v2，不覆盖 v1）

输出：P4任务/音色库/<角色>/v<N>.mp3（试听音频，直接当参考音频用）、v<N>.json（接口原始返回，去掉音频后存档，含 voice_id）。
接口返回的字段名没有在中文文档里核实过：脚本会在返回里找十六进制音频字段（trial_audio / audio 等），找不到就把原始返回存下来并报错，不会静默失败。
"""
import argparse
import json
import os
import sys
import urllib.request

API = "https://api.minimax.cn/v1/voice_design"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "音色库")

# 试听文本是为定音色自写的，不用剧中台词；长度约 8~12 秒，覆盖平静和情绪两种语气。
ROLES = {
    "主角A": ("十八九岁的少年，男声。声音偏低、清冷、咬字清楚，语速偏慢；平静里透着城府和寒意，几乎不带情绪起伏，偶尔一丝很淡的嘲讽笑意。",
             "人心最是难测，可我从来不赌人心。你想要什么，我很清楚；我要的东西，你给不起。"),
    "反派B": ("活了几百年的老魔头，男声。嗓音沙哑粗粝、低沉浑厚，像砂纸磨过喉咙；说话慢而阴狠，得意时放声狂笑，笑声里带着嘶哑的喉音。",
              "哈哈哈……等了这么多年，终于等到今天。你们这些蝼蚁，只配做我的血食。"),
    "老者D": ("七八十岁的老人，男声。声音干涩苍老、冷硬，中气很足；平时冷笑讥讽，发怒时陡然拔高，尖利刺耳。",
              "师兄啊师兄，你躲了这么多年，到头来还是落在我手里。给我滚出来！"),
    "角色C（男）": ("十八九岁的少年，明确是男声，不是女声也不是童声。音色清朗干净但偏低，有胸腔共鸣，略带一点沙；语气慵懒随性，带着玩世不恭的笑意，说到兴头上会轻轻笑出声。",
              "有意思，真有意思。这世上无聊的人太多了，难得碰上一个，让我想多活几天。"),
    "角色C（女）": ("十八九岁的少女，女声。音色清冷干净，偏低，不甜不嗲；语气淡然随性，带着一点戏谑的笑意。",
              "有意思，真有意思。原来换了一副身子，看这世间，又是另一番滋味。"),
    "修士甲": ("四十多岁的粗壮汉子，男声。嗓音粗哑洪亮，带点市井气，说话大大咧咧，爱起哄，笑起来很响。",
             "哈哈，就这点本事也敢来吓唬我们？兄弟们，别听他的，接着干！"),
    "修士乙": ("二十出头的瘦高小伙，男声。声音偏尖细，带一点鼻音，语速快，咋咋呼呼，一激动就破音。",
             "快快快，别愣着啦！东西都拿出来，晚了可就来不及了！"),
}


def find_hex_audio(d):
    """在返回 JSON 里找十六进制编码的音频字段。"""
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, str) and len(v) > 2000 and all(c in "0123456789abcdefABCDEF" for c in v[:200]):
                return k, v
            r = find_hex_audio(v)
            if r:
                return r
    return None


def strip_audio(d):
    if isinstance(d, dict):
        return {k: (f"<{len(v)} 个十六进制字符，已存 mp3>" if isinstance(v, str) and len(v) > 2000 else strip_audio(v)) for k, v in d.items()}
    return d


def design(name, ver, key):
    prompt, text = ROLES[name]
    body = json.dumps({"prompt": prompt, "preview_text": text}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(API, data=body, method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        res = json.loads(r.read().decode("utf-8"))
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    hit = find_hex_audio(res)
    json.dump({"角色": name, "描述": prompt, "试听文本": text, "返回": strip_audio(res)},
              open(os.path.join(d, f"v{ver}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if not hit:
        raise SystemExit(f"{name}：返回里没找到音频字段，原始返回已存 {d}\\v{ver}.json，请把它发给 Claude 看。")
    mp3 = os.path.join(d, f"v{ver}.mp3")
    open(mp3, "wb").write(bytes.fromhex(hit[1]))
    vid = res.get("voice_id") or (res.get("data") or {}).get("voice_id")
    print(f"{name}：已存 {mp3}（字段 {hit[0]}），voice_id = {vid}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("角色", nargs="*")
    ap.add_argument("--全部", action="store_true")
    ap.add_argument("--列表", action="store_true")
    ap.add_argument("--版本", type=int, default=1)
    a = ap.parse_args()
    if a.列表:
        for k, (p, t) in ROLES.items():
            print(f"【{k}】{p}\n    试听：{t}")
        return
    names = list(ROLES) if a.全部 else a.角色
    bad = [n for n in names if n not in ROLES]
    if not names or bad:
        raise SystemExit(f"角色写错或没写：{bad or '（空）'}；可选：{'、'.join(ROLES)}")
    key = os.environ.get("MINIMAX_API_KEY")
    if not key:
        raise SystemExit("没有设置 MINIMAX_API_KEY 环境变量（PowerShell：$env:MINIMAX_API_KEY = \"你的key\"）")
    for n in names:
        if os.path.exists(os.path.join(OUT, n, f"v{a.版本}.mp3")):
            print(f"{n}：v{a.版本} 已存在，跳过（要再抽一版请加 --版本 {a.版本 + 1}）")
            continue
        design(n, a.版本, key)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
