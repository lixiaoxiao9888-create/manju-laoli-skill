# -*- coding: utf-8 -*-
"""H3 提示词构建器（V7.1 · 实测项目 EP01~EP02 实战提炼）
用 Python 写一段的 subjects / shots(逐拍) / sound，生成 Ref2VA 六段式提示词，并按官方标准逐格映射分镜。

用法（在项目里写一个小生成器）：
    import sys; sys.path.insert(0, r"<skill>/scripts/h3_tools"); import H3提示词构建器 as b
    shots = [
      b.shot(1, 0, "", "a tight medium close-up of both fighters ... there is no wide shot in this shot",
             "<Subject 2> on the left facing right; <Subject 3> on the right facing left, an arm's length away",
             [(0.0, 0.4, "..."), (0.4, 0.9, "...")]),
      b.shot(2, 2.6, "on the crack of the elbow", "a close shot of <Subject 3> ...", "...", [(2.6, 3.0, "..."), ...]),
    ]
    txt = b.build(n_pictures_storyboard=True, n_shots=6, duration=15, subjects=[...], summary="...",
                  retention=[...], light="dark-red light rising from the lake below", debris="dust, sparks and grit",
                  shots=shots, sound="...")
    txt = b.apply_official_storyboard(txt, [("A", "0.0–0.4", 1), ("B", "0.4–0.9", 1), ...],
                                      "appearance of ... follows <Picture 2> and <Picture 3>")
    open(path, "w", encoding="utf-8").write(txt)
然后跑 validate_prompt.py --model h3（H1~H20）。

内置规则（见 references/h3-production-playbook.md）：
- 风格段：快剪、速度三要素、1~2 帧 hit-stop、斜角、清晰度正向句（不写任何 blur）；
- shot()：拍与拍首尾相接（断言），Blocking 站位，首切 "From the very first frame"，后续切 "At MM:SS.mmm, <trigger>, the camera cuts to"；
- apply_official_storyboard()：字母格逐格映射 + partially_preserved + 正文 "This moment corresponds to Panel X …"。
写拍时自查：每拍 0.4~0.6s、有位移；最后一拍是进行中的动作 + still … as the shot ends；台词拍长 ≥ 字数÷4.2；眼神只写肌肉不写光；伤只写伤口、只在发生那拍写。"""
import re

OS_TEMPLATE = ("<Subject {n}> (S{s}), {voice}, says in an off-screen voiceover: <d>[Chinese] \"{line}\"</d> "
               "while his lips remain completely closed.")


def style(light, debris, direction=""):
    return (f"Cinematic 3D CG style, vertical 9:16 framing, {light}. A fast, violent action sequence: in each shot the camera locks onto "
            "one moving subject and never lets go, the action keeps accelerating from the first frame to the last, and each cut lands at "
            "the very peak of motion so the next shot starts already at full speed — no shot ever winds down before its cut. Whenever "
            "the camera locks onto a moving subject, speed is always shown by three things at once: the background sweeping past "
            f"behind the subject, {debris} whipping across the lens in the foreground, and the subject's own body twisting, "
            "rolling and flailing — the subject is never a still figure in the frame. Rapid, aggressive camera work: whip pans, slam "
            "pushes, fast orbits, heavy camera shake on every impact; every shot starts in the middle of an action with the camera "
            "already moving fast and ends while the action is still moving; hard cuts only, every cut landing on a sudden movement at "
            "its peak; everything plays at full real-time speed from first frame to last — each impact gets only a one-to-two-frame "
            "hit-stop at the moment of contact, then explodes straight back to full speed. Every shot names its framing, its oblique "
            "camera angle and what the camera follows; wide and medium shots are taken from a 30-to-60-degree oblique angle, never a "
            f"flat side-on view.{direction} No character or creature ever holds a pose; the main subjects keep moving through every "
            "shot. Every frame is crisp and sharply focused with fine, clear detail on faces, hair, fabric and creatures, like a "
            "high-shutter-speed cinema camera; speed is shown by movement, flying debris and camera motion.")


def shot(n, start, trigger, framing, blocking, beats):
    """beats: [(a, b, text)]，首尾相接。"""
    for (a1, b1, _), (a2, _, _) in zip(beats, beats[1:]):
        assert abs(b1 - a2) < 1e-6, (n, b1, a2)
    body = " ".join(f"({a:.1f}–{b:.1f}s) {t}" for a, b, t in beats)
    if n == 1:
        head = f"[Shot 1] From the very first frame — {framing}. Blocking: {blocking}."
    else:
        mm, ss = divmod(start, 60)
        head = f"[Shot {n}] At {int(mm):02d}:{ss:06.3f}, {trigger}, the camera cuts to {framing}. Blocking: {blocking}."
    return head + " " + body


def build(n_shots, duration, subjects, summary, retention, light, debris, shots, sound, direction="", music="N/A"):
    pic1 = (f"<Picture 1> is a storyboard sheet for [Shot 1] through [Shot {n_shots}].")   # 由 apply_official_storyboard 改写
    out = ["subject_definitions:", pic1] + subjects
    out += ["", "summary:", f"[reference generation] The target video is a {duration}-second, {n_shots}-shot " + summary.rstrip(".")
            + "; the storyboard <Picture 1> provides the viewpoint, subject placement, and shot order."]
    out += ["", "retention_analysis:", f"<Picture 1> (storyboard for [Shot 1] through [Shot {n_shots}]): weak_reference - only the rough layout and shot order"] + retention
    out += ["", "detailed_description:", style(light, debris, direction)] + shots
    out += ["", "overall_soundscape:", sound, "", "non_diegetic_music:", music, ""]
    return "\n".join(out)


def apply_official_storyboard(s, mapping, appearance_note):
    """mapping = [(panel_letter, beat_tc, shot_no)]，beat_tc 形如 "0.4–0.9"。"""
    lines = s.split("\n")
    by_shot = {}
    for p, _, n in mapping:
        by_shot.setdefault(n, []).append(p)
    parts = []
    for n in sorted(by_shot):
        ps = by_shot[n]
        names = " and ".join(f"Panel {p}" for p in ps)
        parts.append(f"{names} {'is a moment' if len(ps) == 1 else 'are moments'} within [Shot {n}]")
    letters = [m[0] for m in mapping]
    nshot = max(by_shot)
    i = next(k for k, l in enumerate(lines) if l.startswith("<Picture 1> is"))
    lines[i] = (f"<Picture 1> is a storyboard sheet of {len(letters)} lettered panels, {letters[0]} to {letters[-1]}, read left to right and top "
                f"to bottom; each panel marks one exact moment inside [Shot 1] through [Shot {nshot}]: " + "; ".join(parts) + ". Each panel "
                "provides the camera angle, framing, screen positions and direction of motion for its moment; the action flows "
                "continuously into and out of every panel moment without pausing on it.")
    j = next(k for k, l in enumerate(lines) if l.startswith("<Picture 1> (storyboard"))
    lines[j] = (f"<Picture 1> (storyboard sheet, Panels {letters[0]}–{letters[-1]} mapped to moments in [Shot 1] through [Shot {nshot}]): "
                "partially_preserved - retain each panel's camera angle, framing, screen positions and direction of motion at the moment "
                f"it is mapped to; {appearance_note}; the video is full-color cinematic 3D CG in a single full frame, not the sheet's "
                "drawing style, panel borders or letters")
    s = "\n".join(lines).replace(
        "; the storyboard <Picture 1> provides the viewpoint, subject placement, and shot order.",
        f"; the storyboard sheet <Picture 1> marks the camera angle, framing and screen positions of key moments, Panels {letters[0]} to {letters[-1]}.")
    for p, tc, _ in mapping:
        key = f"({tc}s) "
        i = s.index(key)
        m = re.search(r" \(\d+\.\d–\d+\.\d+s\) |\n", s[i + len(key):])
        k = i + len(key) + m.start()
        s = s[:k] + f" This moment corresponds to Panel {p} of <Picture 1>, and the motion carries straight through it." + s[k:]
    return s
