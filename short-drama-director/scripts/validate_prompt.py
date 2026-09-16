#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_prompt.py — 投喂提示词结构自检（V6.8 · 出稿时门禁）

只查可机械判定的结构/版本问题；空间/遮挡/轴线/动作物理/视线仍由 AI 语义推演
（见 spatial-topview-camera.md 与 quality-gate-review.md），本脚本不越权。

用法：
  python scripts/validate_prompt.py <提示词文件.md|.txt>
      [--model 2.5|2.0] [--mode new|extend] [--json] [--self-test]

检查项（C1~C12）：
  C1 时长预算   段时长 ≤ 模型上限（2.5=30s / 2.0=15s）
  C2 切镜上限   镜头数 ≤ ceil(段长/3s)；单镜 <3s 告警
  C3 时间轴     相邻镜头无断档/重叠；time 倒挂拦截
  C4 字符预算   单段 ≤4500 字符
  C5 版本语法   2.0 禁 [SFX:] 与顿挫词；2.5 建议 [SFX:]
  C6 画幅回填   含 aspect_ratio= 或含画幅的【画幅风格】栏
  C7 七段式      核实七段式核心栏齐备（V6.8 唯一命名，不借外部示范格式）
  C8 首尾帧禁用  2.0 出现 首帧:/尾帧:/参考图绑定/Start Frame/End Frame 即拦截（2.0 全面禁用）
  C9 平台高危词  血腥/断肢/裸露/自伤/违法等高危词 → 拦截，走 platform-safety 替代表
  C10 单镜过长   单镜 >6s 告警（talking head 风险）
  C11 接续状态   时间轴分镜末镜后必带【接续状态】尾行
  C12 否定式/规则词  正文出现"没有X/不要X"硬删除或"末态继承/拼接节点/换机位"等工作流规则名词 → 告警
  C13 镜长雷同   同段 ≥4 镜时，若同值镜长占比 ≥70% → 告警（节奏缺乏快慢呼吸，镜长应由台词÷语速倒推）
"""
import json
import os
import re
import sys

LIMITS = {"2.5": 30, "2.0": 15}
MAX_CHARS = 4500

TIME_RE = re.compile(
    r"(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?\s*[-~～→]\s*(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?"
    r"|(\d+(?:\.\d+)?)\s*s\s*[-~～→]\s*(\d+(?:\.\d+)?)\s*s", re.I)

# 七段式核心栏（V6.8 model-adapters §5 唯一权威；【接续状态】是【时间轴分镜】尾行，不单列）
SEVEN_SEGMENTS = ["【画幅风格】", "【场景资产】", "【核心人物】", "【站位声明】", "【时间轴分镜】", "【音效】", "【强制禁止项】"]

GORE_WORDS = ["鲜血", "血喷", "血迹", "血溅", "血肉模糊", "鲜血淋漓", "喷血", "流血", "断肢", "截肢",
              "断臂", "断头", "碎尸", "四分五裂", "尸体", "死尸", "惨死", "内脏", "肠子", "脑浆",
              "开膛破肚", "割喉", "绞杀", "虐杀", "凌迟", "透体", "捅穿", "刺穿", "砍断", "撕裂",
              "伤口", "骨裂", "骨骼断裂", "切开", "劈成两段", "斩为两段", "切成两半", "劈成两半",
              "深可见骨", "可见骨", "血污", "血淋淋", "断指", "开膛", "破腹", "掏心", "剥皮",
              "裸体", "裸露", "走光", "露点", "床戏", "自杀", "自残", "割腕", "上吊", "吸毒", "嗑药", "吸毒贩毒"]


def parse_time_ranges(text):
    """返回 [(start_s, end_s, line_no)]，兼容 MM:SS(.ff) 与 Xs-Ys。"""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        for m in TIME_RE.finditer(line):
            if m.group(1) is not None:
                fr = int(m.group(3) or 0)
                to = int(m.group(6) or 0)
                s = int(m.group(1)) * 60 + int(m.group(2)) + fr / 100.0
                e = int(m.group(4)) * 60 + int(m.group(5)) + to / 100.0
            else:
                s, e = float(m.group(7)), float(m.group(8))
            out.append((round(s, 2), round(e, 2), i))
    return out


def validate(text, model="2.5", mode="new"):
    issues, warns = [], []
    tr = parse_time_ranges(text)
    dur = round(max((e for s, e, _ in tr), default=0), 2)

    # C1/C2/C3 时间轴
    if tr:
        if dur > LIMITS[model] + 0.01:
            issues.append(f"C1 段时长 {dur}s 超 {model} 上限 {LIMITS[model]}s")
        n = len(tr)
        cap = -(-int(dur + 0.5) // 3) or 1
        if n > cap:
            issues.append(f"C2 镜头数 {n} > 段长÷3s 上限 {cap}")
        for s, e, ln in tr:
            if e <= s:
                issues.append(f"C3 第{ln}行 时间码倒挂 {s}->{e}")
            elif e - s < 3:
                warns.append(f"C2 第{ln}行 单镜 {round(e - s, 2)}s <3s（碎切风险）")
            elif e - s > 6:
                warns.append(f"C10 第{ln}行 单镜 {round(e - s, 2)}s >6s（talking head 风险：单镜预算 3~5s，长台词按 dialogue-doctor 拆 2~3 镜正反打/反应镜头）")
        for (s1, e1, l1), (s2, e2, l2) in zip(tr, tr[1:]):
            if abs(e1 - s2) > 0.05:
                kind = "重叠" if s2 < e1 else "断档"
                warns.append(f"C3 第{l1}->{l2}行 {kind}({e1} vs {s2})")
        if mode == "new" and tr and tr[0][0] > 0.05:
            warns.append("C3 全新生成建议从 0 起手")
    else:
        warns.append("C1-C3 未识别到时间轴（如为纯文生视频短片可忽略）")

    # C4 字符预算
    if len(text) > MAX_CHARS:
        issues.append(f"C4 共 {len(text)} 字符 > 预算 {MAX_CHARS}（按 seedance-render-engine 压缩顺序裁删）")

    # C5 版本语法
    if model == "2.0":
        if "[SFX" in text.upper():
            issues.append("C5 Seedance 2.0 无官方声音字符标记（音效/台词以文字写入镜行、默认由模型生成）")
        for w in ("顿挫", "微停顿", "咬住"):
            if w in text:
                issues.append(f"C5 2.0 禁顿挫词「{w}」（会渲染成真停顿）")
    elif "[SFX" not in text.upper():
        warns.append("C5 2.5 建议用 [SFX:] 原生音效标记")

    # C6 画幅回填
    if not re.search(r"aspect_ratio\s*=", text) and not re.search(r"【画幅风格】[^\n]*(16:9|9:16|21:9|1:1)", text):
        issues.append("C6 缺画幅回填（体内 aspect_ratio= 或【画幅风格】行含 16:9/9:16/21:9）")

    # C7 七段式核心栏
    missing = [seg for seg in SEVEN_SEGMENTS if seg not in text]
    if missing:
        issues.append(f"C7 七段式缺栏 {missing}（V6.8 主格式唯一命名，段序见 model-adapters §5）")

    # C8 2.0 首尾帧禁用（V6.8 重头门）
    fl = re.findall(r"首帧\s*[:：]|尾帧\s*[:：]|参考图绑定|Start\s*Frame|End\s*Frame", text, re.I)
    if fl:
        if model == "2.0":
            issues.append(f"C8 Seedance 2.0 全面禁用首尾帧：出现 {sorted(set(fl))}（2.0 参考图仅锁定形象）")
        else:
            issues.append(f"C8 首尾帧仅限 2.5「参考模式②」：出现 {sorted(set(fl))}——若走默认全能参考模式则删去；确用模式②需标注 mode=first_last_frame")

    # C9 平台高危词
    hits = [w for w in GORE_WORDS if w in text]
    if hits:
        issues.append(f"C9 正文出现平台高危词 {hits}——按 platform-safety-compliance-guide 全类目替代表在成句时直接改写（2.0 提及即召唤，禁靠否定式压制）")

    # C11 接续状态尾行
    if tr and not re.search(r"【接续状态】|接续下一段|承接上镜|承接上段", text):
        issues.append("C11 时间轴分镜末镜后缺【接续状态】尾行（每段必带：多段接续默认「角色动作与空间位置严格继承」，R3 终段写终帧定格）")

    # C12 否定式硬删除 / 工作流规则词混入
    for m in re.finditer(r"(没有|不要出现|禁止出现)([\u4e00-\u9fa5]{2,6})", text):
        if not re.search(r"负面|排除|禁止角色变形|无水印|无字幕", text[max(0, m.start() - 40):m.end() + 40]):
            warns.append(f"C12 正文疑似否定式硬删除「{m.group(0)}」——硬删除应整句移除，负面仅走【强制禁止项】负面词")
    workflow = re.findall(r"末态继承|拼接节点|换机位|同机位硬接|可变数据|每段重写|每段更新", text)
    if workflow:
        warns.append(f"C12 工作流规则名词混入投喂正文 {sorted(set(workflow))}——接续状态只写末帧画面长什么样，规则由执行者应用")

    # C13 镜长雷同（节奏呼吸 · quality-gate-review P1 反例）
    if len(tr) >= 4:
        from collections import Counter
        durs = [round(e - s, 2) for s, e, _ in tr]
        cnt = Counter(durs)
        top_dur, top_n = cnt.most_common(1)[0]
        ratio = top_n / len(durs)
        if ratio >= 0.7:
            warns.append(f"C13 镜长雷同：{top_n}/{len(durs)} 镜均为 {top_dur}s（占比 {ratio:.0%}）——节奏缺乏快慢呼吸；镜长应按台词字数÷语速(3.5~5字/s)+情绪节拍倒推，禁机械等分（quality-gate-review P1「时长全篇雷同」反例）")

    return issues, warns, {"duration_s": dur, "shots": len(tr), "chars": len(text)}


def _self_test():
    ok = 1
    # 1) 合规 2.5 样例
    t_ok = ("【画幅风格】16:9 横屏, 电影级质感, PBR, 景深胶片颗粒 (aspect_ratio=16:9)\n"
            "【场景资产】@SCN-厢房（外观以场景参考图锁定）\n"
            "【核心人物】@CHR-女主（外观以人物参考图锁定）\n"
            "【站位声明】：@女主（画面中 · 坐于窗下 · 侧身45°朝左 · 双手交叠膝上）；轴线锁定：单人无轴线；位移：全员原位，无位移。\n"
            "【时间轴分镜】\n"
            "00:00-00:04 [镜头1] 中近景 · 平视 · 缓推。她从袖中抽出信件。声音：[SFX: 纸张摩挲]。台词：无。\n"
            "00:04-00:08 [镜头2] 特写 · 侧角 · 固定。指尖微颤。声音：[SFX: 呼吸]。台词：无。\n"
            "【接续状态】：角色动作与空间位置严格继承\n"
            "【音效】生成音效描述（2.5 用 [SFX:]/<>，2.0 文字描述默认由模型生成）\n"
            "【强制禁止项】画面：角色变形、穿模；文字：无字幕水印\n")
    iss, warns, _ = validate(t_ok, "2.5", "new")
    if iss:
        print("FAIL self-test: 合规 2.5 样例不应报错", iss); ok = 0
    # 2) 2.0 含 [SFX:]
    t_sfx = t_ok.replace("(aspect_ratio=16:9)", "model=seedance-2.0 (aspect_ratio=16:9)")
    iss, _, _ = validate(t_sfx, "2.0", "new")
    if not any("C5" in i for i in iss):
        print("FAIL self-test: 2.0 应拦截 [SFX:]"); ok = 0
    # 3) 2.0 含首尾帧
    t_fl = t_ok + "【参考图绑定】：首帧: a.png, 尾帧: b.png\n"
    iss_t20, _, _ = validate(t_fl, "2.0", "new")
    if not any("C8" in i for i in iss_t20):
        print("FAIL self-test: 2.0 应拦截首尾帧"); ok = 0
    # 3b) 2.5 含首尾帧（非模式②声明）也应拦
    iss_t25, _, _ = validate(t_fl, "2.5", "new")
    if not any("C8" in i for i in iss_t25):
        print("FAIL self-test: 2.5 未标模式②的首尾帧应拦截"); ok = 0
    # 4) 缺站位声明 → C7
    iss, _, _ = validate(t_ok.replace("【站位声明】：@女主（画面中 · 坐于窗下 · 侧身45°朝左 · 双手交叠膝上）；轴线锁定：单人无轴线；位移：全员原位，无位移。\n", ""), "2.5", "new")
    if not any("C7" in i for i in iss):
        print("FAIL self-test: 缺站位声明应报 C7"); ok = 0
    # 5) 超时长 → C1
    t_long = t_ok.replace("00:04-00:08", "00:04-00:40")
    iss, _, _ = validate(t_long, "2.0", "new")
    if not any("C1" in i for i in iss):
        print("FAIL self-test: 2.0 超 15s 应报 C1", iss); ok = 0
    # 6) 高危词 → C9
    t_gore = t_ok.replace("她从袖中抽出信件。", "她嘴角溢出一线鲜血，断肢横飞。")
    iss, _, _ = validate(t_gore, "2.5", "new")
    if not any("C9" in i for i in iss):
        print("FAIL self-test: 高危词应报 C9"); ok = 0
    # 7) 缺接续状态 → C11
    iss, _, _ = validate(t_ok.replace("【接续状态】：角色动作与空间位置严格继承\n", ""), "2.5", "new")
    if not any("C11" in i for i in iss):
        print("FAIL self-test: 缺接续状态应报 C11"); ok = 0
    # 8) 缺画幅 → C6（连【画幅风格】行里的比例一并去掉）
    t_noframe = t_ok.replace("【画幅风格】16:9 横屏, 电影级质感, PBR, 景深胶片颗粒 (aspect_ratio=16:9)",
                             "【画幅风格】电影级质感, PBR, 景深胶片颗粒")
    iss, _, _ = validate(t_noframe, "2.5", "new")
    if not any("C6" in i for i in iss):
        print("FAIL self-test: 缺画幅回填应报 C6"); ok = 0
    # 9) 单镜 >6s → C10 warn
    _, warns, _ = validate(t_ok.replace("00:04-00:08", "00:04-00:15"), "2.5", "new")
    if not any("C10" in w for w in warns):
        print("FAIL self-test: 单镜>6s 应报 C10"); ok = 0
    # 10) 规则词混入 → C12 warn
    _, warns, _ = validate(t_ok.replace("角色动作与空间位置严格继承", "下段末态继承，拼接节点换机位"), "2.5", "new")
    if not any("C12" in w for w in warns):
        print("FAIL self-test: 规则词混入应报 C12"); ok = 0
    # 11) 镜长雷同 → C13 warn
    t_flat = ("【画幅风格】9:16 竖屏, 写实 (aspect_ratio=9:16)\n"
              "【场景资产】@SCN-厅（外观以场景参考图锁定）\n"
              "【核心人物】@CHR-甲（外观以人物参考图锁定）\n"
              "【站位声明】：@甲（画面左 · 立 · 正面朝右）；轴线锁定：单人无轴线；位移：全员原位，无位移。\n"
              "【时间轴分镜】\n"
              "00:00-00:04 [镜头1] 近景 · 平视 · 固定。甲抬眼。声音：无。台词：无。\n"
              "00:04-00:08 [镜头2] 近景 · 平视 · 固定。甲开口。声音：无。台词：【甲：\"一\"】\n"
              "00:08-00:12 [镜头3] 近景 · 平视 · 固定。甲转身。声音：无。台词：无。\n"
              "00:12-00:15 [镜头4] 近景 · 平视 · 固定。甲落座。声音：无。台词：无。\n"
              "【接续状态】：角色动作与空间位置严格继承\n"
              "【音效】生成音效描述（默认由模型生成）\n"
              "【强制禁止项】画面：角色变形；文字：无字幕\n")
    _, warns, _ = validate(t_flat, "2.5", "new")
    if not any("C13" in w for w in warns):
        print("FAIL self-test: 镜长雷同应报 C13", warns); ok = 0
    print("[+] self-test", "PASSED" if ok else "FAILED")
    return ok


def main():
    argv = sys.argv[1:]
    if "--self-test" in argv:
        sys.exit(0 if _self_test() else 1)
    files = [a for a in argv if not a.startswith("-")]
    if not files:
        print(__doc__); sys.exit(2)

    def opt(flag, default=None):
        return argv[argv.index(flag) + 1] if flag in argv else default

    model = opt("--model", "2.5")
    if model not in LIMITS:
        print("[-] --model 必须 2.5/2.0"); sys.exit(2)
    if not os.path.exists(files[0]):
        print(f"[-] 文件不存在：{files[0]}"); sys.exit(2)
    try:
        text = open(files[0], encoding="utf-8").read()
    except UnicodeDecodeError:
        print(f"[-] 文件非 UTF-8 文本：{files[0]}"); sys.exit(2)
    except OSError as e:
        print(f"[-] 读取失败：{e}"); sys.exit(2)
    issues, warns, stats = validate(text, model, opt("--mode", "new"))
    if "--json" in argv:
        print(json.dumps({"issues": issues, "warnings": warns, "stats": stats},
                         ensure_ascii=False, indent=2))
    else:
        print(f"[+] 时长{stats['duration_s']}s 镜头{stats['shots']} 字符{stats['chars']} | model={model} mode={opt('--mode','new')}")
        for w in warns:
            print("[!] WARN: " + w)
        for e in issues:
            print("[-] FAIL: " + e)
        print("[+] PASSED" if not issues else f"[-] {len(issues)} error(s)")
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()