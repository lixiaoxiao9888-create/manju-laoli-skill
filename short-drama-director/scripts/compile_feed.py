#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compile_feed.py · P4 投喂提示词自动装配编译器（AI 写戏 · 脚本封装）
设计动机：
  在 P4 阶段让大模型手工拼装七段式，极易漏写「Voice 声线锁」「年龄锚/三件套」「CHAR_STATE 偏离替换语」
  「末镜末 1 秒定格收束句」或「M1 素材接线单」。
  本编译器读取 project_state.json，自动将结构化分镜编译为 100% 符合 C1~C30 与六道闸门的七段式投喂稿。
用法：
  python3 scripts/compile_feed.py --state project_state.json [--out feed.md]
  python3 scripts/compile_feed.py --self-test
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import sd_core


# ★P9 修（C33 缺口）：焦段是镜行**头**的元数据槽，不是镜行正文的「相机说明书废话」。
#   C20m 禁的是正文里写「焦平面死锁面部无漂移 / 浅景深阴影侧取景」这类理论废话；
#   C33 要求每个镜头标注焦段。两码作用域不同（头 vs 正文），此前编译器把两者混为一谈，
#   导致所有产物每镜必报 C33。本表照抄 `sd-storyboard-engine/references/short-drama-camera-system.md` §二。
_FOCAL_RULES = [
    # (匹配词, 兜底焦段) —— 按景别从紧到松匹配，先中近景再中景，避免「中景」吃掉「中近景」
    ("大特写", "100mm"), ("特写", "85mm"), ("中近景", "85mm"),
    ("近景", "85mm"), ("中景", "50mm"), ("全景", "35mm"),
    ("远景", "28mm"), ("大全景", "24mm"), ("空镜", "35mm"),
]
_FOCAL_RE = re.compile(r"\d{1,3}\s*(?:-\s*\d{1,3})?\s*mm|1\s*:\s*1|鱼眼|微距", re.I)


def _ensure_focal(spec, fallback="35mm"):
    """spec 缺焦段时按景别补齐，插入位置固定为「景别 · 焦段 · 角度 · 运镜」——
    焦段是景别的直接属性，插在末尾会读成运镜的修饰语。已有焦段则原样返回（尊重作者判断）。"""
    if not spec:
        spec = "中景 · 平视 · 固定"
    if _FOCAL_RE.search(spec):
        return spec
    fl = fallback
    for kw, f in _FOCAL_RULES:
        if kw in spec:
            fl = f
            break
    parts = [p.strip() for p in spec.split("·") if p.strip()]
    if parts:
        return " · ".join([parts[0], fl] + parts[1:])
    return f"中景 · {fl} · 平视 · 固定"


def _is_crowd_class_c(seg, seg_type=""):
    """C 类判定（crowd-behavior-direction.md §2.1）：密闭双人 / 打戏 / 纯特写 / 声明无人。
    C 类段必须显式写 `除 @XX 外无其他人物`，且机检只查这一句（C40d），不查群像事务。"""
    blob = f"{seg_type} {seg.get('type','')} {seg.get('note','')} {seg.get('sfx_summary','')}"
    if re.search(r"打斗|打戏|动作段|战斗|对决|格斗|冲突动作", blob):
        return True
    if re.search(r"四下无人|空无一人|无人|密室|密闭|独处", blob):
        return True
    shots = seg.get("shots", [])
    if shots and all(("特写" in (s.get("spec") or "")) for s in shots):
        return True
    # 密闭双人：仅两名角色且无群像字段
    chars = re.findall(r"@([^\s（(；;、,]+)", " ".join(seg.get("standing", [])))
    if len(set(chars)) == 2 and not seg.get("crowd"):
        return True
    return False


def _orientation_word(aspect):
    """画幅 → 朝向词。★P11 新增（2026-10-24）。

    病根：旧版把「横屏」写死在【画幅风格】模板里 —— `f"【画幅风格】{aspect} 横屏，…"`。
    于是选 9:16（竖屏短剧的主用画幅）编出来是 **「9:16 横屏」**：一条自相矛盾的指令，
    而且它出现在**每段第一行**，是模型读到的第一个画幅信号。
    （实测：`--aspect` 并不存在，画幅来自 `state["locks"]["aspect"]`，所以这个错误
     对每一个竖屏项目都成立，只是没人把产物读回来验一遍。）
    """
    try:
        w, h = [float(x) for x in re.split(r"\s*[:：]\s*", str(aspect))[:2]]
    except Exception:
        return "横屏"
    if h > w:
        return "竖屏"
    if w / h >= 2.2:
        return "宽银幕"
    return "横屏"


def compile_project_to_feed(state):
    locks = state.get("locks", {})
    mode = locks.get("asset_mode", "M1").upper()
    aspect = locks.get("aspect")
    model = locks.get("model")
    seam = str(locks.get("seam", ""))
    if model not in ("2.0", "2.5"):
        raise ValueError("编译器仅支持显式锁定 model=2.0/2.5")
    if not aspect or not re.fullmatch(r"[1-9]\d*[:：][1-9]\d*", str(aspect)):
        raise ValueError("必须显式锁定有效 aspect，例如 16:9")
    if seam not in ("1", "2", "3", "4"):
        raise ValueError("必须显式锁定 seam=1/2/3/4，不代选 D 锁")
    style_card = locks.get("style_card", "电影级写实质感")
    wa = state.get("world_anchor", {})
    era = wa.get("era_anchor", "现代")
    receipt = state.get("receipt", {})
    plugins = receipt.get("active_plugins", ["sd-storyboard-engine", "sd-feed-engine"])
    read_refs = receipt.get("read_refs", ["model-adapters.md", "segment-splicing.md"])
    fps = receipt.get("fingerprints", ["【默认镜头策略】"])

    out_lines = [
        f"> 模型锁：{model}；画幅锁：{aspect}；D 锁：{seam}",
        f"> 素材形态：{mode}",
        f"> 激活外挂：{' + '.join(plugins)}",
        f"> 已读子库：{' / '.join(read_refs)}",
        f"> 本段调用外挂指纹：{'｜'.join(fps)}",
        "",
    ]

    # ★P9 修（CT2 缺口）：M1/M2 形态下资产由 P2 另册交付，投喂稿只做接线。
    #   但 audit_contract.py 的 CT2-CHR/SCN/PRP 只认稿内写了「资产另册：…」才豁免，
    #   编译器此前从不写 → 它自己产的 M1 稿必然 CT2 三条 FAIL ——链在自己包的门口断掉。
    #   这里按素材形态自动补声明；文件名可由 receipt.asset_book 指定。
    _asset_book = receipt.get("asset_book", "")
    if not _asset_book and mode in ("M1", "M2"):
        _asset_book = "P2-资产提示词.md"
    if _asset_book:
        out_lines.insert(-1, f"> 资产另册：{_asset_book}（角色四格/场景母版+九宫格/道具四格由 P2 另册交付，本稿只做接线）")

    chars = state.get("characters", {})
    scenes = state.get("scenes", {})
    props = state.get("props", {})
    segments = state.get("segments", [])
    total_segs = max(len(segments), 1)
    used_figs = []

    for idx, seg in enumerate(segments, 1):
        sid = seg.get("seg_id", f"段{idx}")
        seg_type = seg.get("segment_type", "对话戏")
        scn_name = seg.get("scene", "")
        scn = scenes.get(scn_name, {})
        scn_fig = scn.get("fig_no")
        if mode != "M0" and scn_fig:
            used_figs.append((scn_fig, f"场景·{scn_name}", "锁定空间几何、建筑材质与主光源方向", "不控制人物站位与动作"))
            scn_tag = f"@{scn_name}（参考图{scn_fig}）"
        else:
            scn_tag = f"@{scn_name}（{scn.get('coords', '')}；{scn.get('set_states', {}).get('default', '')}；{scn.get('media_layer', '')}）"
        # ★时段光影基准（2026-10-15 · model-adapters §5.0.5b）：场景资产立唯一光影基准，镜行只写增量
        _lt = scn.get("lighting", "")
        if _lt:
            scn_tag += f"；时段光影：{_lt}"

        # 组装【核心人物】（自动注入年龄锚 + 三件套 + Voice 声线锁 + CHAR_STATE 脱离替换语）
        cast_parts = []
        for cname, cinfo in chars.items():
            cfig = cinfo.get("fig_no")
            age = cinfo.get("age_anchor", "")
            body = cinfo.get("body_anchor", "")
            look = cinfo.get("look_3piece", "")
            vlock = cinfo.get("voice_lock", "")
            # 检查本段是否有 CHAR_STATE 脱离声明
            dev_clauses = []
            for _k, st_v in (cinfo.get("char_states") or {}).items():
                item = st_v.get("item", "")
                act = st_v.get("action", "")
                cons = st_v.get("consequence", "")
                if item:
                    dev_clauses.append(
                        f"⚠️资产状态偏离声明：本段{cname}{act}（{cons}），关于「{item}」的佩戴状态以本段提示词为准，覆盖角色参考图"
                    )
            dev_str = "；" + "；".join(dev_clauses) if dev_clauses else ""
            if mode != "M0" and cfig:
                used_figs.append((cfig, f"角色·{cname}", f"锁定{cname}面部五官、头身比与基础服装形制", "不控制本段动作姿态与已声明偏离的配饰状态"))
                cast_parts.append(
                    f"@{cname}（参考图{cfig}，声线锁：{vlock}{dev_str}）"
                )
            else:
                cast_parts.append(
                    f"@{cname}：{age}，{body}，{look}（同一张脸跨镜锁定），声线锁：{vlock}{dev_str}"
                )

        # 组装道具锚点（如有）
        for pname, pinfo in props.items():
            pfig = pinfo.get("fig_no")
            mdesc = pinfo.get("material_desc", "")
            if mode != "M0" and pfig:
                used_figs.append((pfig, f"道具·{pname}", f"锁定{pname}外观形制与材质", "不控制持握人物与运动轨迹"))
                scn_tag += f"；@PRP-{pname}（参考图{pfig}）"
            else:
                scn_tag += f"；@PRP-{pname}（{mdesc}）"

        standing_str = "；".join(seg.get("standing", []))
        # ★P9 修（C40d 缺口）：C 类段必须显式写「除 @X 外无其他人物」——
        #   crowd-behavior-direction.md §2.1 原文：C 类（密闭双人/打戏/纯特写/声明无人）
        #   「必须写」这句，且机检对 C 类只查这一句声明。此前编译器从不写，
        #   于是它自己产的每一段打戏稿都必然踩 C40d「群像开关沉默」。
        #   A/B 类反过来禁写（同一事务派了人又说没人 = 自相矛盾指令，模型二选一必崩一边）。
        _c_decl = ""
        if _is_crowd_class_c(seg, seg_type):
            _names = [n for n in re.findall(r"@([^\s（(；;、,]+)", standing_str)]
            if _names:
                _c_decl = f"；{('、'.join('@' + n for n in _names))} 之外无其他人物"
            else:
                _c_decl = "；画面内无其他人物"
        shots = seg.get("shots", [])
        shot_lines = []
        for s_i, sh in enumerate(shots):
            no = sh.get("no", s_i + 1)
            st_t = int(sh.get("start", 0))
            ed_t = int(sh.get("end", st_t + 4))
            t_str = f"{st_t // 60:02d}:{st_t % 60:02d}-{ed_t // 60:02d}:{ed_t % 60:02d}"
            spec = _ensure_focal(sh.get("spec", "中景 · 平视 · 固定"))
            act = sh.get("action", "").rstrip("。； ")
            # 遵循 C20m 铁律：镜行正文严禁默认塞入「85mm F1.4极浅景深阴影侧取景（焦平面全程死锁面部无漂移）/ 10-15厘米 / 极细微规律呼吸式微动」等摄影机说明书废话，100% 留给人物与道具纯物理动作
            opt_lock = sh.get("optics_and_camera_lock", "").strip("。； ")
            if opt_lock and opt_lock not in act:
                act += f"；{opt_lock}"
            # 末镜自动注入「前置 0.5 秒收束窗 + 末 1 秒整秒硬定格」标准句
            if seam == "1" and s_i == len(shots) - 1 and "定格" not in act and "空镜" not in act:
                settle_t = max(st_t, ed_t - 1.5)
                act += f"；第 {settle_t:g} 秒起运动收束，末 1 秒全体人物保持姿态与站位、动作完全静止、画面定格"
            snd = sh.get("sound", "环境音").rstrip("。 ")
            dlg = sh.get("dialogue", "无").rstrip("。 ")
            shot_lines.append(f"{t_str} [镜头{no}] {spec}。{act}。声音：{snd}。台词：{dlg}。")

        sfx_sum = seg.get("sfx_summary", "自然环境音，对白清晰置顶")
        # 遵循 C19 粉色大象效应铁律：不在【强制禁止项】里重复写具体道具名词（如「禁止同时出现两个眼镜」反会诱发双眼镜），全靠【核心人物】正向替换语锁死
        ban_extra = ""

        # ★P11 修（2026-10-24 · 编译器多段产物必被自家 C38 拦）：
        #   病根：P9 只用**单段** state 验过编译器，所以「段缝桥接」这件事从未被触发过。
        #   一旦编译 ≥2 段，`## 【投喂单元 2/N】` 与 ``` 之间什么都没有 → C38 报
        #   「段间缺桥接声明」。编译器自己的产物过不了自己包的门禁，与 P9 是同一类错。
        #   修法：第 2 段起自动在段缝说明区写桥接行（承接 + 声音先入 + 情绪递进），
        #   这三样都在 C38 的桥接词表内。桥接选择是**默认值**，不是替用户拍板——
        #   真要跳切，把这一行改成「硬切跳」即可（C38 同样认）。
        _bridge = []
        if idx > 1:
            bridge = seg.get("bridge", "").strip()
            if not bridge:
                raise ValueError(f"段{idx}缺少 bridge：须由上游提供真实段缝方案，不自动推断尾帧、换场或声音")
            _bridge = [f"> 段缝桥接（段{idx - 1}→段{idx}，D锁{seam}）：{bridge}"]
        out_lines.extend([
            f"## 【投喂单元 {idx}/{total_segs} · {sid}】",
            *_bridge,
            "```text",
            f"【画幅风格】{aspect} {_orientation_word(aspect)}，{era}，{style_card}，{seg_type}（aspect_ratio={aspect}）",
            f"【场景资产】{scn_tag}",
            f"【核心人物】{'；'.join(cast_parts)}",
            f"【站位声明】{standing_str}{_c_decl}",
            "【时间轴分镜】",
            *shot_lines,
            f"【音效】{sfx_sum}",
            # ★P11 修（2026-10-24 · 写法与权威口径脱节）：
            #   旧句「禁止角色面部变形或肢体穿模」是 P6.2 已废止的备用负面词库写法，
            #   权威口径（prompt-feeding-checklist.md §负向词 + model-adapters §5）是
            #   **段7 只写四项极简句**：「画面：禁字幕、禁水印（含 Logo）；音频：禁背景音乐、禁旁白」。
            #   理由：长负面清单有害——被禁词根即画面词，「禁止角色面部变形」等于把
            #   「面部变形」这个词喂给模型（粉色大象）。编译器却在每一段都写它。
            f"【强制禁止项】画面：禁字幕、禁水印（含 Logo）；音频：禁背景音乐、禁旁白{ban_extra}。",
            "```",
            "",
        ])

    # M1 模式下自动编译《素材接线单》
    if mode == "M1" and used_figs:
        seen_f = set()
        uniq_figs = []
        for item in used_figs:
            if item[0] not in seen_f:
                seen_f.add(item[0])
                uniq_figs.append(item)
        uniq_figs.sort(key=lambda x: x[0])
        out_lines.extend([
            "## 素材接线单（M1 编号占位必备 · 平台挂图指南）",
            "",
            "| 图号 | 对应资产 | 你该挂哪张 | 只控制什么 | 不控制什么 |",
            "|---|---|---|---|---|",
        ])
        for fno, aname, ctrl, no_ctrl in uniq_figs:
            out_lines.append(f"| 图{fno} | {aname} | 挂载 P2 产出的「{aname}」设定图 | {ctrl} | {no_ctrl} |")
        out_lines.append("")

    return "\n".join(out_lines)


def self_test():
    # ★P11 升级（2026-10-24 · P9 的漏网之鱼就是「只用单段自测」）：
    #   P9 拿 default_project_state() 的**单段**样例验编译器全绿，于是这两个问题
    #   一直没被测出来：① 多段产物段缝没有桥接声明 → 自家 C38 必报；
    #   ② 两段各双人 → C40c 把人数跨段累加（摆位 4 人）→ 自家 C40c 必报。
    #   自测的输入形态必须覆盖**真实生产形态**（3 分钟剧 ≈14 段），否则绿灯不成立。
    st = sd_core.default_project_state()
    import copy as _copy
    _seg2 = _copy.deepcopy(st["segments"][0])
    _seg2["seg_id"] = "段2"
    _seg2["bridge"] = "承接上段末镜；本例为同场示例，实际尾帧待生成后核验。"
    _seg2["shots"][0]["spec"] = "全景 · 35mm · 略仰 · 缓拉"   # 与段1 末镜同景别，排除 C18m 干扰
    st["segments"] = [st["segments"][0], _seg2]
    feed_md = compile_project_to_feed(st)

    # 0. 多段产物形态断言（P11 新增：把「编译器产物必须长什么样」写死）
    assert feed_md.count("【画幅风格】") == 2, \
        f"多段编译产物段数不对：{feed_md.count('【画幅风格】')} 段"
    assert "段缝桥接" in feed_md, "第 2 段未生成段缝桥接声明（C38 必报）"
    _asp = st["locks"].get("aspect", "16:9")
    assert f"【画幅风格】{_asp} {_orientation_word(_asp)}" in feed_md, \
        f"画幅朝向词与 aspect 不一致：{_asp} 应写「{_orientation_word(_asp)}」"
    assert "禁止角色面部变形或肢体穿模" not in feed_md, \
        "【强制禁止项】仍是废止的长负面清单（权威口径是四项极简句）"

    # 0b. 竖屏不得写成横屏（P11 修的 Bug，必须锁死防复发）
    _st9 = _copy.deepcopy(st)
    _st9["locks"]["aspect"] = "9:16"
    _md9 = compile_project_to_feed(_st9)
    assert "9:16 竖屏" in _md9, "竖屏画幅被写成非竖屏（P11 Bug 复发）"
    assert "9:16 横屏" not in _md9, "「9:16 横屏」自相矛盾文案复发"

    # 1. 对账校验
    iss_s, wrn_s = sd_core.verify_feed_against_state(feed_md, st)
    assert not iss_s and not wrn_s, f"state verify failed: {iss_s} / {wrn_s}"
    # 2. 跑 validate_prompt.py 与 gate_check.py 实测
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(feed_md)
        tmp_path = f.name
    try:
        vp_script = os.path.join(SCRIPT_DIR, "validate_prompt.py")
        # 用 --model 2.5 直接调用 validate_prompt.py
        r1 = subprocess.run(
            [sys.executable, vp_script, tmp_path, "--model", "2.5"],
            capture_output=True,
            text=True,
        )
        assert r1.returncode == 0, f"validate_prompt failed on compiled feed: {r1.stdout}\n{r1.stderr}"
        # ★P9 修：旧断言只看 returncode==0，而 C17f/C33/C40d 全是 WARN ——
        #   自测全绿，产物却带 5 条 WARN 出厂。编译器承诺「编译出 100% 合规的七段式」，
        #   那就必须断言 WARN 也归零，否则这句承诺是空话。
        _vp_warns = [ln for ln in r1.stdout.splitlines() if ln.startswith("[!] WARN:")]
        assert not _vp_warns, (
            "编译产物带 WARN，编译器未履行「100% 合规」承诺：\n  "
            + "\n  ".join(_vp_warns[:10])
        )
        gc_script = os.path.join(os.path.dirname( os.path.dirname(SCRIPT_DIR) ), "sd-feed-engine", "scripts", "gate_check.py")
        r2 = subprocess.run(
            [sys.executable, gc_script, tmp_path, "--model", "2.5"],
            capture_output=True,
            text=True,
        )
        assert r2.returncode == 0, f"gate_check failed on compiled feed: {r2.stdout}\n{r2.stderr}"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    print("[+] compile_feed self-test PASSED (0 FAIL across validate_prompt & gate_check)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="漫剧老李 V7.5.0-SLIM P4 投喂自动装配编译器")
    ap.add_argument("--state", help="project_state.json 路径")
    ap.add_argument("--out", help="输出投喂稿 .md 路径（不指定则打印到标准输出）")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(self_test())
    if not args.state:
        ap.print_help()
        sys.exit(2)
    state = json.load(open(args.state, encoding="utf-8"))
    md = compile_project_to_feed(state)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[+] 已编译生成投喂稿：{args.out}")
    else:
        print(md)


if __name__ == "__main__":
    main()
