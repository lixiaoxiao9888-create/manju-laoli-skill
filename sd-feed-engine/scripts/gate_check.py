# -*- coding: utf-8 -*-
"""
gate_check.py · 投喂层闸门校验器（P14 判据级去重版）

用法：python gate_check.py <投喂稿.md> [--model 2.5|2.0] [--assets N] [--mode M0|M1|M2|auto]
                          [--tol 0.8] [--syntax auto|on|off] [--aspect 16:9]
设计依据：sd-feed-engine/references/feed-mode-and-gates.md §二（闸门分工表）

★P14 判据级去重（用户裁定：同一内容不反复检查）
  病灶：本脚本此前把 C 系已经实现的判据又写了一遍，注释里直接标着「（C16b）」「C11」——
        同一个语气位缺失、同一份镜长雷同、同一套七段式字段，出一次稿要查两遍。
  处置：**一条判据只留一处实现**。
    ① 本脚本**只管 C 系没有的四类投喂层判据**（见下「保留清单」）；
    ② 与 C 系重复的判据**整段摘除**，改由 `--syntax` 一次性调用总控机检引擎覆盖，
       等级不变（原 FAIL 项在 C 系里仍是 FAIL 级），不会因去重而放松任何红线；
    ③ 独装本子技能、找不到总控引擎时，自动降级为「只跑本层闸门」并明确提示加跑机检。

  保留清单（C 系无对应实现 · 已逐条实查）：
    闸门0  【】配对闭合 + 镜号连续性（C7 只管七段缺栏、C11 只管接续状态残留，**都不管这两项**）
    闸门1  节奏档位     长段只有 1~2 镜（C1b 管段长区间、C2 管镜数下限，均不等价）
    闸门2  台词时长     字数÷语速+停顿 vs 镜长（语速档解算，C16 系只管语气位有无/质量）
    闸门3  段级字数     单段 2.0 ≤2900/3000、2.5 ≤3600/4000（C4 是**篇级** 6000 字符兜底）
    闸门4  交接话术     「以下是/希望对你有帮助」类 AI 对话残余 + 代码框内外参数位置
    闸门5  图片上限     单段引用图号数按模型分档（2.5→30 / 2.0→9）
    闸门6A 图号越库     稿内图号 ∉ 项目资产库图数
    闸门6B 素材形态     M0/M1/M2 声明一致性 + 接线单双向一致 + 虚假核验断言

  已移交 C 系（本脚本不再重复实现）：
    闸门0·七段式缺字段 → C7；闸门0·【接续状态】残留 → C11
    闸门1b 镜长雷同（同段 ≥4 镜、同值占比 ≥70%）→ C13
    闸门2 台词缺语气位 → C16b

闸门 6 扩展（素材形态一致性 · 权威 = 总控 references/asset-delivery-modes.md）：
  本包**不持有图**——图由用户在外部平台生成并持有。素材形态三档 M0/M1/M2（默认 M1）。
  闸门 6 = 6A 编号一致性 + 6B 素材形态一致性：
    未声明形态 → WARN；M0 稿内出现图号 → FAIL（形态违约）；
    M1 有图号但无《素材接线单》→ WARN；稿内图号 ∉ 接线单图号 → FAIL；
    出现"已核验/核对一致"类断言而形态非 M2 → FAIL（虚假核验）。
"""
import re, sys, io, os, argparse, subprocess

if __name__ == '__main__' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ---------- 语速表 ----------
# 只有"节奏维"词才真正决定语速档；"压着嗓子/嘶哑/沉声"是音质力度描述，不必然慢。
SPEED_BANDS = [
    (r'耳语|气声|一字一顿|一字一停|一字一句|拖长|断续|哽咽|抽气', 2.5, 3.5, '慢速重音（节奏维慢）'),
    (r'低语|低声|压抑|嘶哑|沉声|沉冷|宣判|喃喃|放缓', 3.5, 4.5, '偏慢'),
    (r'争吵|吼|喊|嚷|咆哮|抢话|慌乱|急促|连珠|语速快', 5.0, 6.0, '快速/争吵/抢话'),
]
SPEED_DEFAULT = (3.5, 6.0, '标准~高速（判定按 6 字/秒）')

PAUSE = [('，', 0.2), ('、', 0.2), ('。', 0.4), ('？', 0.4), ('！', 0.4), ('…', 0.8), ('——', 0.6)]

# ---------- 闸门5 单组图片上限（★2026-10-17 分档修复）----------
# 病根：原实现写死 `if len(figs) > 9`，**不读 --model**，与文档闸门5（2.0≤9 / 2.5≤30 / 2.0 单图）
# 脱节 → 双向误判：2.5 挂 10~30 张被误杀（文档允许 30），2.0 挂 2~9 张被漏放。
# 2.0 取值依据：官方参考图槽为「单参考图锁形象、无首尾帧」，但粉丝实测（2026-10-17）
#   平台侧多锚点上传 3~4 张资产图可跑通 → 机检暂取保守值 9，避免既压死实测工作流又放过滥用。
# 权威 = sd-feed-engine/references/feed-mode-and-gates.md 闸门5 与
#        short-drama-director/references/asset-delivery-modes.md 数量上限段。
IMG_LIMIT_BY_MODEL = {'2.5': 30, '2.0': 9, 'jimeng': 9}
IMG_LIMIT_DEFAULT = 9


def img_limit(model, override=0):
    """闸门5 上限解算：显式覆盖优先，否则按 A 锁模型分档。"""
    return override if override else IMG_LIMIT_BY_MODEL.get(model, IMG_LIMIT_DEFAULT)


def img_gate_check(nfig, model, override=0):
    """闸门5 判定：返回 (是否超限, 上限)。★2026-10-17 抽出为纯函数，供 self-test 双向验证。"""
    lim = img_limit(model, override)
    return (nfig > lim, lim)


def parse_units(text):
    """切分投喂单元，返回 [(标题, 代码框正文)]，兼容 ## 【投喂单元...】 / ### 段N... / ### 第N段... / 代码框内含【画幅风格】"""
    unit_hdr_re = re.compile(r'^(?:##\s*【投喂单元[^\n]*|###+\s*(?:第\s*\d+\s*段|段\s*\d+)[^\n]*)', re.M)
    matches = list(unit_hdr_re.finditer(text))
    units = []
    if matches:
        for i, m in enumerate(matches):
            title = m.group(0).lstrip('#').strip()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            chunk = text[start:end]
            fm = re.search(r'```(?:text|prompt)?\s*\n(.*?)```', chunk, re.S)
            if fm and '【画幅风格】' in fm.group(1):
                units.append((title, fm.group(1)))
            elif '【画幅风格】' in chunk and '【时间轴分镜】' in chunk:
                units.append((title, chunk.strip()))
    if not units:
        # 兜底：直接扫描所有包含【画幅风格】与【时间轴分镜】的代码框或段落
        for idx, fm in enumerate(re.finditer(r'```(?:text|prompt)?\s*\n(.*?)```', text, re.S), 1):
            if '【画幅风格】' in fm.group(1) and '【时间轴分镜】' in fm.group(1):
                units.append((f'段{idx}', fm.group(1)))
    return units


# 兼容三形态时码（MM:SS-MM:SS / Xs-Ys / N-N秒）与全半角【镜头N】及「镜号在前/时码在前」双语序
GC_TIME_RE = re.compile(
    r'(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?\s*[-~～→]\s*(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?'
    r'|(\d+(?:\.\d+)?)\s*s\s*[-~～→]\s*(\d+(?:\.\d+)?)\s*s'
    r'|(?:\A|(?<=[\s\[【\]】]))\s*([0-9]|[1-5]\d)(?:\.\d+)?\s*[-~～→]\s*([0-9]|[1-5]\d)(?:\.\d+)?秒',
    re.I)
GC_SHOT_NO_RE = re.compile(r'[\[【]?\s*镜头\s*(\d+)\s*[\]】]?')


def frac_to_sec(frac):
    """秒的小数位 → 秒值（★2026-10-14 Agent 修复：统一小数秒口径）。

    `5`→0.5 · `50`→0.5 · `05`→0.05 —— **按位数换算，不写死 ÷100**。
    原实现写 `fr / 100.0`，把 1 位小数 `.5` 算成 0.05：`00:03.5` → 3.05s。
    闸门 2（字数÷6 对镜长）靠这里的秒值判定，口径错会让边缘稿误放行/误拦截。
    本口径须与总控 `scripts/sd_core.frac_to_sec`、`validate_prompt._frac_to_sec` 三处一致。
    """
    if not frac:
        return 0.0
    return int(frac) / (10 ** len(frac))


def parse_shots(body):
    """解析镜行，返回 [(镜号, 起秒, 止秒, 全行)]，兼容 MM:SS(.s) / Xs-Ys / N-N秒 与全半角镜号。"""
    shots = []
    auto_no = 0
    for line in body.splitlines():
        tm = GC_TIME_RE.search(line)
        if not tm:
            continue
        if tm.group(1) is not None:
            s = int(tm.group(1)) * 60 + int(tm.group(2)) + frac_to_sec(tm.group(3))
            e = int(tm.group(4)) * 60 + int(tm.group(5)) + frac_to_sec(tm.group(6))
        elif tm.group(7) is not None:
            s, e = float(tm.group(7)), float(tm.group(8))
        else:
            s, e = float(tm.group(9)), float(tm.group(10))
        sm = GC_SHOT_NO_RE.search(line)
        auto_no += 1
        no = int(sm.group(1)) if sm else auto_no
        shots.append((no, s, e, line))
    return shots


def parse_lines(body):
    """解析台词，返回 [(角色, 语气, 台词, 全行)]"""
    out = []
    # 修正：引号定界改非贪婪 `(.*?)"】` —— 台词内嵌引号（如「先认一句"我做得够好了"」）
    # 会把旧的 `[^"]*` 截断或整句漏检（静默失检）。新式以「"】」为唯一收尾锚点。
    pattern = r'【([^【】（(:：\n]+?)(?:[（(]([^）)\n]*)[）)])?\s*[:：]\s*["“](.*?)["”]\s*】'
    for m in re.finditer(pattern, body):
        out.append((m.group(1).strip(), (m.group(2) or '').strip(), m.group(3), m.group(0)))
    return out


# ---------- 闸门 6B · 素材形态（权威 = 总控 references/asset-delivery-modes.md） ----------
MODE_DECL = re.compile(r'素材形态[：:]\s*[（(]?\s*(M[012])')
# ★审计补丁P1：放宽标题前缀——「## 五·补 A｜素材接线单」「### 素材接线单（M1 必备）」同为合规写法，
#   旧正则只认「## 素材接线单」开头，导致带章节序号的稿被判「未附接线单」（实测假告警）。
WIRING_HEAD = re.compile(r'^#{2,3}\s*[^\n]{0,12}素材接线单[^\n]*\n', re.M)
# "已核验/核对一致"类虚假核验断言（排除否定与禁止语境）
FAKE_VERIFY = re.compile(r'(?<![未不])已核验|(?<![未不])核对一致|(?<![未不])核验通过|已与《?资产图册》?一致')
NEG_CTX = re.compile(r'未|不|禁止|不得|没有|无核验|仅适用|非')


def split_wiring(text):
    """把整份交付拆成 (提示词正文, 接线单段)。接线单段不计入稿内图号判定。"""
    m = WIRING_HEAD.search(text)
    if not m:
        return text, ''
    rest = text[m.end():]
    nxt = re.search(r'^##\s', rest, re.M)
    end = m.end() + nxt.start() if nxt else len(text)
    return text[:m.start()] + text[end:], text[m.start():end]


def check_asset_mode(text, mode_arg, fails, warns):
    """闸门 6B：素材形态一致性。返回实际生效形态。"""
    decl = MODE_DECL.search(text)
    if mode_arg in (None, '', 'auto'):
        if decl:
            mode = decl.group(1)
        else:
            mode = 'M1'
            warns.append('闸门6B 未声明素材形态（首行应写「素材形态：M0/M1/M2」）——'
                         '形态未定，本次按默认 M1 判定；未声明不得交付')
    else:
        mode = mode_arg.upper()
        if not decl:
            warns.append(f'闸门6B 未声明素材形态，本次按命令行 --mode {mode} 判定——'
                         '交付稿首行仍须补声明')
        elif decl.group(1) != mode:
            warns.append(f'闸门6B 声明形态 {decl.group(1)} 与 --mode {mode} 不一致，'
                         f'按声明 {decl.group(1)} 判定——请核对')
            mode = decl.group(1)

    prompt_text, wiring_text = split_wiring(text)
    figs_prompt = sorted(set(int(x) for x in re.findall(r'图(\d+)', prompt_text)))
    figs_wiring = sorted(set(int(x) for x in re.findall(r'图(\d+)', wiring_text)))

    if mode == 'M0' and figs_prompt:
        fails.append(f'闸门6B 形态违约：声明 M0（纯提示词）却出现图号 {figs_prompt}'
                     '——图号槽位与 M0 互斥，须删净或改声明 M1')
    if mode == 'M1' and figs_prompt:
        if not wiring_text:
            warns.append(f'闸门6B 形态违约：M1 稿件引用图号 {figs_prompt} 但未附《素材接线单》'
                         '——接线单是 M1 交付必备件（§ 素材接线单）')
        else:
            oob = [f for f in figs_prompt if f not in figs_wiring]
            if oob:
                fails.append(f'闸门6B 稿内图号 {oob} 不在《素材接线单》内'
                             '——用户会去挂一张不存在的图')
            if '不控制' not in wiring_text:
                warns.append('闸门6B 接线单缺少「不控制什么」列/说明'
                             '——一张图被当多张用是主要污染源')
    if mode in ('M0', 'M1'):
        for i, line in enumerate(text.split('\n'), 1):
            if FAKE_VERIFY.search(line) and not NEG_CTX.search(line):
                fails.append(f'闸门6B 虚假核验断言（第 {i} 行，形态 {mode}）'
                             '——本包看不到图，不得声称已核验/与资产图册一致')
                break
    return mode


def speech_seconds(line, tone):
    """估算台词秒数 → (最快可行, 最慢舒适, 字数, lo, hi)
    need_fast = n/hi + pause  ← ★判定基准（V7.3.0：hi 通常 = 6 字/秒）
    need_slow = n/lo + pause  ← 舒适参考
    """
    lo, hi = SPEED_DEFAULT[0], SPEED_DEFAULT[1]
    for pat, a, b, _ in SPEED_BANDS:
        if re.search(pat, tone):
            lo, hi = a, b
            break
    n = len(re.findall(r'[\u4e00-\u9fff\w]', line))
    pause = sum(line.count(c) * p for c, p in PAUSE)
    return n / hi + pause, n / lo + pause, n, lo, hi


def self_test():
    """闸门自身解析自检（★2026-10-14 Agent 新增）。

    锁两类「静默失效」：① 小数秒解算（`.5` 曾被算成 0.05s）；② 投喂单元切分。
    这两类一旦失手，闸门会照打 PASS——假 PASS 比假 FAIL 危险一个量级。
    """
    ok = 0
    if frac_to_sec('5') != 0.5 or frac_to_sec('50') != 0.5 or frac_to_sec('05') != 0.05 \
       or frac_to_sec(None) != 0.0:
        print('FAIL self-test: frac_to_sec 位数换算错误（.5 应为 0.5s，.05 应为 0.05s）'); ok = 1
    sh = parse_shots('【时间轴分镜】\n'
                     '00:00-00:04 [镜头1] 中景。甲。\n'
                     '00:04-00:08 [镜头2] 近景。甲。\n'
                     '00:08-00:10.5 [镜头3] 特写。甲。\n'
                     '00:10.5-00:15 [镜头4] 全景。甲。')
    if len(sh) != 4:
        print(f'FAIL self-test: parse_shots 应解析 4 镜，实得 {len(sh)}（丢镜即本用例拦截目标）'); ok = 1
    elif abs(sh[2][2] - 10.5) > 1e-9 or abs(sh[3][1] - 10.5) > 1e-9:
        print(f'FAIL self-test: 00:10.5 应解为 10.5s（旧缺陷为 10.05s），实得 {sh[2][2]}'); ok = 1
    unit_md = ('## 【投喂单元 1/1 · 段1】\n'
               '```text\n【画幅风格】16:9 横屏\n【时间轴分镜】\n'
               '00:00-00:04 [镜头1] 中景 · 平视 · 固定。甲开口。声音：无。台词：【甲：“你好。”】\n'
               '```\n')
    us = parse_units(unit_md)
    if len(us) != 1 or '【画幅风格】' not in us[0][1]:
        print(f'FAIL self-test: parse_units 应切出 1 个投喂单元，实得 {len(us)}'); ok = 1
    # ★2026-10-17 闸门5 分档双向用例（原实现写死 >9，两向都会判错）
    #   误杀向：2.5 挂 12 张，文档允许 30 → 必须判合规（旧实现 FAIL）
    if img_gate_check(12, '2.5')[0]:
        print('FAIL self-test: 闸门5 在 model=2.5 挂 12 图应合规（上限 30），旧写死 9 会误杀'); ok = 1
    elif not img_gate_check(31, '2.5')[0]:
        print('FAIL self-test: 闸门5 在 model=2.5 挂 31 图应超限（上限 30），实判合规'); ok = 1
    #   漏放向：2.0 挂 12 张，上限 9 → 必须判超限（旧实现只到 >9 才拦，2~9 张全放过）
    if not img_gate_check(12, '2.0')[0]:
        print('FAIL self-test: 闸门5 在 model=2.0 挂 12 图应超限（上限 9），实判合规'); ok = 1
    elif img_gate_check(5, '2.0')[0]:
        print('FAIL self-test: 闸门5 在 model=2.0 挂 5 图应合规（粉丝实测 ≥3 可跑通），实判超限'); ok = 1
    elif not img_gate_check(10, '2.0')[0]:
        print('FAIL self-test: 闸门5 在 model=2.0 挂 10 图应超限（上限 9），实判合规'); ok = 1
    elif img_gate_check(40, '2.5', 40)[0]:
        print('FAIL self-test: 闸门5 --img-limit 覆盖失效（40 应放行 40 图）'); ok = 1
    if not ok:
        print('[+] gate_check self-test PASSED')
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('path', nargs='?')
    ap.add_argument('--model', default='2.5')
    ap.add_argument('--assets', type=int, default=9, help='项目资产库总图数')
    ap.add_argument('--img-limit', type=int, default=0, dest='img_limit',
                    help='闸门5 单组图片上限手动覆盖（0=按 --model 分档：2.5→30 / 2.0→9 ）。'
                         '2026-10-17 新增：原实现写死 9，不读模型')
    ap.add_argument('--mode', default='auto', choices=['auto', 'M0', 'M1', 'M2', 'm0', 'm1', 'm2'],
                    help='素材形态（V7.3.0）：auto=按交付稿首行「素材形态：Mx」声明判定，'
                         '未声明时按默认 M1 并告警。权威 = references/asset-delivery-modes.md')
    ap.add_argument('--tol', type=float, default=0.8,
                    help='闸门2 判定容差(s)：V7.3.0 以最快档 6 字/秒为判定基准，'
                         '仅当「字数÷6 + 停顿 > 镜长 + tol」才判真念不完。默认 0.8')
    ap.add_argument('--syntax', default='auto', choices=['auto', 'on', 'off'],
                    help='P14 判据级去重：auto=检测到总控机检引擎就一次性拉取 C 系判据'
                         '（取代本脚本原先重复实现的闸门0/1b/2语气位）；on=强制必须有引擎；'
                         'off=只跑投喂层闸门。')
    ap.add_argument('--aspect', default=None, help='画幅（传给机检引擎做 C6b 三处互校）')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()

    if a.self_test:
        sys.exit(self_test())
    if not a.path:
        ap.print_help(); sys.exit(2)

    with open(a.path, encoding='utf-8') as source:
        text = source.read()
    units = parse_units(text)
    if not units:
        print('未找到投喂单元（## 【投喂单元 N/M】格式）'); sys.exit(2)

    print(f'=== 投喂层闸门 + C 系机检（一次跑完）· {os.path.basename(a.path)} · model={a.model} ===')

    warns, fails, infos = [], [], []
    mode = check_asset_mode(text, a.mode, fails, warns)

    print(f'投喂单元：{len(units)} 段  |  闸门2 判定基准：最快档 6 字/秒（V7.3.0）'
          f'  |  素材形态：{mode}（闸门6B · V7.3.0）\n')

    # ---- 闸门 0 · 结构完整性（P14 逐条核对后的保留项）----
    #   ⚠️ 去重必须逐条核对，不能按名字匹配：本节四项经实查，
    #      · 【】闭合 —— C 系无任何配对判据 → **保留在本层**
    #      · 镜号连续 —— C 系只「识别」镜号用于解析，从不校验连续性 → **保留在本层**
    #      · 七段式缺字段 —— 已由 C7 实现 → 摘除
    #      · 【接续状态】残留 —— 已由 C11 实现（FAIL 级）→ 摘除
    previous_no = None
    for ui, (title, body) in enumerate(units, 1):
        for m in re.finditer(r'【[^】\n]*$', body, re.M):
            fails.append(f'闸门0 段{ui}：【 未闭合（行尾缺 】）→ {m.group(0)[:40]}')
        if body.count('【') != body.count('】'):
            fails.append(f'闸门0 段{ui}：【/】数量不等（{body.count("【")} vs {body.count("】")}）')
        for m in re.finditer(r'台词：【[^】\n]*\n', body):
            fails.append(f'闸门0 段{ui}：台词行未见 】 收尾 → {m.group(0)[:40]}')
        nums = [int(x) for x in GC_SHOT_NO_RE.findall(body)]
        if nums:
            if (nums != list(range(nums[0], nums[0] + len(nums))) or nums[0] < 1
                    or (previous_no is not None and nums[0] not in (1, previous_no + 1))):
                fails.append(f'闸门0 段{ui}：镜号不连续 {nums}')
            previous_no = nums[-1]
        # 七段式缺字段 → C7；【接续状态】残留 → C11（P14 摘除，不重复报）

    for ui, (title, body) in enumerate(units, 1):
        shots = parse_shots(body)
        dur = (shots[-1][2] - shots[0][1]) if shots else 0
        chars = len(body)
        figs = sorted(set(int(x) for x in re.findall(r'图(\d+)', body)))
        print(f'--- 段{ui}: {title}')
        print(f'    镜数={len(shots)}  段长={dur}s  字数={chars}  引用图号={figs}')

        # 闸门1 节奏档位：10s 以上只有 1-2 镜
        if dur >= 10 and len(shots) <= 2:
            warns.append(f'闸门1 段{ui}：{dur}s 只有 {len(shots)} 镜，需慢节奏白名单或补标点镜')
        # 闸门1b 镜长雷同 —— P14 摘除：与机检 C13 同一判据（≥4 镜、同值占比 ≥70%），由 C13 负责

        # 闸门2 台词时长（以最快档 6 字/秒为判定基准）
        #   P14：原此处的「台词缺语气位 → FAIL（C16b）」已整段摘除——C16b 是同一判据的权威实现
        for index, (no, s, e, shot_text) in enumerate(shots):
            dialogue = parse_lines(shot_text)
            if not dialogue:
                continue
            needs = [speech_seconds(line, tone) for _, tone, line, _ in dialogue]
            need_fast = sum(item[0] for item in needs)
            mid = sum((item[0] + item[1]) / 2 for item in needs)
            # 只有末镜显式声明定格时扣减；否定定格和普通收尾不扣秒。
            freeze = re.search(r'(?:末|最后)\s*([0-9]+(?:\.[0-9]+)?|一)\s*秒\s*(?:硬)?定格', shot_text)
            reserve = 0.0
            if index == len(shots) - 1 and freeze and not re.search(
                    r'不|非|无|禁止|取消', shot_text[max(0, freeze.start() - 4):freeze.start()]):
                reserve = 1.0 if freeze.group(1) == '一' else float(freeze.group(1))
            budget = max(0.0, e - s - reserve)
            if need_fast > budget + a.tol:
                warns.append(f'闸门2 段{ui} 镜头{no}：{len(dialogue)} 句累计最快需 '
                             f'{need_fast:.1f}s，可用仅 {budget}s → 真念不完')
            elif mid > budget + a.tol:
                infos.append(f'闸门2 段{ui} 镜头{no}：累计最快 {need_fast:.1f}s，'
                             f'标准档需 {mid:.1f}s，可用 {budget}s → 需快念（非缺陷）')

        # 闸门3 字数（★ 2026-10-13：按模型分档 —— 2.5 可吃更长提示词）
        w_soft, w_hard = (3600, 4000) if a.model == '2.5' else (2900, 3000)
        if chars > w_hard:
            fails.append(f'闸门3 段{ui}：字数 {chars} > {w_hard}（model={a.model} 硬上限），必须压缩')
        elif chars > w_soft:
            warns.append(f'闸门3 段{ui}：字数 {chars} 落在 {w_soft + 1}~{w_hard}（model={a.model}），建议压一轮')

        # 闸门4 可投喂语义
        for bad in ['接下一大分镜', '接下一段', '接分镜', '承接上一段', '接上段']:
            if bad in body:
                fails.append(f'闸门4 段{ui}：含交接话术「{bad}」')
        # 参数行应在代码框外
        # ★P9 修（2026-10-24 全流程自检发现）：旧写法用 `(?<!【画幅风格】)…?aspect_ratio`
        #   做负向后顾——但七段式**法定写法**是 `【画幅风格】16:9 横屏 (aspect_ratio=16:9)`，
        #   `aspect_ratio` 前面隔着「16:9 横屏 (」，后顾永远不成立 →
        #   **每一份合规稿都被判「参数留在代码框内」**。这是条永远亮红灯的死规则。
        #   原意是「参数漏到正文里」才报，故改为：先剥离【画幅风格】整行，再看正文有没有残留。
        _body_wo_aspect = re.sub(r"^【画幅风格】[^\n]*$", "", body, flags=re.M)
        for bad in ('分辨率', 'aspect_ratio'):
            if bad in _body_wo_aspect:
                warns.append(f'闸门4 段{ui}：参数「{bad}」疑似留在代码框内')

        # 闸门5 单组图片数（★2026-10-17 改为按 A 锁模型分档，原写死 9 会误杀 2.5）
        over, img_lim = img_gate_check(len(figs), a.model, a.img_limit)
        if over:
            fails.append(f'闸门5 段{ui}：单段引用 {len(figs)} 个图号 > {img_lim}（model={a.model} 上限）')
        elif len(figs) > 9 and a.model == '2.5':
            infos.append(f'闸门5 段{ui}：单段引用 {len(figs)} 个图号（2.5 上限 {img_lim}，合规）'
                         f'——超过 9 张时请确认每张都有明确职责，多余图位会稀释一致性')

        # 闸门6A 编号一致性（图号是否在资产库范围内）
        oob = [f for f in figs if f > a.assets]
        if oob:
            fails.append(f'闸门6A 段{ui}：引用图号 {oob} 超出资产库（共 {a.assets} 图）')

    print()
    print('=== 投喂层闸门结果 ===')
    if fails:
        print(f'FAIL {len(fails)} 条：')
        for x in fails:
            print('  ✗', x)
    if warns:
        print(f'WARN {len(warns)} 条：')
        for x in warns:
            print('  !', x)
    if infos:
        print(f'INFO {len(infos)} 条（非缺陷，仅提示需快念）：')
        for x in infos:
            print('  i', x)
    if not fails and not warns:
        print('  本层闸门全过（0 FAIL 0 WARN）')

    # ---- P14：C 系判据一次性覆盖（取代原先在本脚本里重复实现的闸门0 / 1b / 2语气位）----
    syntax_fail, syntax_warn, syntax_note = run_syntax_engine(
        a.path, a.model, a.aspect, a.syntax)
    if syntax_note:
        print(f'\n=== 机检引擎（C 系）===')
        print(f'  {syntax_note}')
    if syntax_fail or syntax_warn:
        print(f'  机检 FAIL={syntax_fail}  WARN={syntax_warn}（明细见上方 C 系段落）')

    print(f'\n汇总：投喂层 FAIL={len(fails)}  WARN={len(warns)}  |  '
          f'机检 FAIL={syntax_fail} WARN={syntax_warn}  |  素材形态={mode}（闸门6B）')
    if syntax_note.startswith('已按') or syntax_note.startswith('未检测'):
        print('质检入口：本次只跑投喂层闸门（C 系未执行）——交付前务必另跑一次完整质检。')
    else:
        print('质检入口：本脚本一次跑完「投喂层闸门 + C 系机检」，同一判据不再重复检查。')
    sys.exit(1 if (fails or syntax_fail) else 0)


def _find_engine():
    """定位总控机检引擎（套装同级部署时存在；子技能独立安装时可能不存在）。"""
    here = os.path.dirname(os.path.abspath(__file__))
    # sd-feed-engine/scripts → 套装根 → short-drama-director/scripts/validate_prompt.py
    candidates = [
        os.path.join(here, '..', '..', 'short-drama-director', 'scripts', 'validate_prompt.py'),
        os.path.join(here, '..', '..', '..', 'short-drama-director', 'scripts', 'validate_prompt.py'),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return os.path.abspath(c)
    return None


def run_syntax_engine(path, model, aspect, mode='auto'):
    """调用总控 validate_prompt.py，把 C 系结果并入本次报告。

    返回 (fail_count, warn_count, note)。mode: auto=检测到就跑 / on=必须跑 / off=不跑。
    """
    if mode == 'off':
        return 0, 0, '已按 --syntax off 跳过（仅跑投喂层闸门；建议另行加跑 validate_prompt.py）'
    engine = _find_engine()
    if not engine:
        if mode == 'on':
            return 1, 0, '未找到总控机检引擎 validate_prompt.py（--syntax on 要求必须有）——请先部署 1 总控 + 10 子技能套装'
        return 0, 0, ('未检测到总控机检引擎（子技能独立安装），本次只跑了投喂层闸门；'
                      'C7 七段式 / C2 镜号 / C11 接续状态残留 / C13 镜长雷同 / C16b 语气位 '
                      '需另行加跑 short-drama-director/scripts/validate_prompt.py')
    cmd = [sys.executable, engine, path, '--model', str(model)]
    if aspect:
        cmd += ['--aspect', str(aspect)]
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONIOENCODING': 'utf-8'}
    try:
        proc = subprocess.run(cmd, capture_output=True, encoding='utf-8', env=env)
    except OSError as exc:
        return 0, 0, f'机检引擎调用失败（{exc}），本次只有投喂层闸门结果'
    out = (proc.stdout or '') + (proc.stderr or '')
    print(out.rstrip())
    if proc.returncode == 3:
        return 0, 0, '机检引擎判定「非投喂稿件」，C 系判据未执行（稿件形态请核对）'
    n_fail = sum(1 for line in out.splitlines() if line.startswith('[-] FAIL'))
    n_warn = sum(1 for line in out.splitlines() if line.startswith('[!] WARN'))
    if proc.returncode not in (0, 1):
        return n_fail, n_warn, f'机检引擎异常退出（code={proc.returncode}）'
    return n_fail, n_warn, f'机检引擎已跑通（{os.path.basename(engine)} · model={model}）'


if __name__ == '__main__':
    main()
