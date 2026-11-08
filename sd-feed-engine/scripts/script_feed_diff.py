# -*- coding: utf-8 -*-
"""
script_feed_diff.py · 「剧本 ↔ 投喂稿」台词对照校验器
用法：python script_feed_diff.py --script <剧本.md> --feed <投喂稿.md> [--names 陈建国,陈建军,陈建民]

目的：拦截 P4 投喂层「内容级漏执行」——
      投喂稿可以压缩动作行、合并镜头，但**剧本台词不得凭空缺失**
      （尤其题眼句 / 反应镜的因）。缺失即报 FAIL。
定位：与 gate_check.py（六道闸门）、validate_prompt.py（C1~C26＋增量主码 C27~C30 机检）互补，
      专治「格式全对、内容漏句」。
"""
import re, sys, io, argparse, os

if __name__ == '__main__' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def norm(s):
    """归一化：去标点/空白，只留汉字字母数字"""
    return re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]', '', s)


def parse_script(path, names):
    """抽上游台词：(角色, 提示, 台词原文)。自动识别「剧本格式」与「分镜稿格式」。"""
    with open(path, encoding='utf-8') as source:
        txt = source.read()
    out = []
    name_pat = '|'.join(names)
    # 分镜稿格式：台词：角色（提示）："..."  或  台词：无（画外音延续）：角色："..."
    if re.search(r'^台词：', txt, re.M):
        for m in re.finditer(r'^台词：(.+)$', txt, re.M):
            seg = m.group(1)
            # 修正：引号改贪婪 `(.*)"` —— 分镜稿每行仅一句台词；
            # 旧的 `[^"]+` 会被台词内嵌引号（「先认一句"我做得够好了"」）截断。
            for q in re.finditer(r'(' + name_pat + r')(（[^）]*）)?：?"(.*)"', seg):
                out.append((q.group(1), (q.group(2) or '').strip('（）'), q.group(3)))
        return out
    # 剧本格式：角色（提示）：台词
    for m in re.finditer(r'^(' + name_pat + r')(（[^）]*）)?：(.+)$', txt, re.M):
        t = m.group(3).strip()
        if not t or t.startswith('▲') or t.startswith('△'):
            continue
        out.append((m.group(1), (m.group(2) or '').strip('（）'), t))
    return out


def parse_feed(path):
    """抽投喂稿台词：(角色, 语气, 台词原文)"""
    with open(path, encoding='utf-8') as source:
        txt = source.read()
    from gate_check import parse_lines
    return [(role, tone, line) for role, tone, line, _ in parse_lines(txt)]


def ngram_cov(a, b, n=4):
    """a 的 n-gram 有多大比例出现在 b 中（对「长句拆多镜」友好，是缺失判定的主判据）"""
    a, b = norm(a), norm(b)
    if len(a) < n:
        return 1.0 if (a and a in b) else 0.0
    grams = [a[i:i + n] for i in range(len(a) - n + 1)]
    return sum(1 for g in grams if g in b) / len(grams)


def best_match(line, pool, thr=0.55):
    """在 pool 中找与 line 最相似的投喂台词（按最长公共子串比率）"""
    a = norm(line)
    if not a:
        return None, 0.0
    best, score = None, 0.0
    for item in pool:
        b = norm(item[2])
        if not b:
            continue
        # 修正：超短台词（≤3 字，如「嗯。」「怎么？」）走最长公共子串会因
        # 窗口下限 j-i>=3 恒为空 → 一律判 0，误报为「投喂独有」。改为包含判定。
        if len(a) <= 3 or len(b) <= 3:
            s = 1.0 if (a in b or b in a) else 0.0
            if s > score:
                best, score = item, s
            continue
        # 用较长者滑动，找最长公共连续子串
        short, long_ = (a, b) if len(a) <= len(b) else (b, a)
        lo, hi = 0, 0
        for i in range(len(short)):
            for j in range(i + 3, len(short) + 1):
                if short[i:j] in long_:
                    if j - i > hi - lo:
                        lo, hi = i, j
        ov = hi - lo
        s = ov / max(len(a), 1)
        if s > score:
            best, score = item, s
    return (best, score) if score >= thr else (None, score)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--script', required=True)
    ap.add_argument('--feed', required=True)
    ap.add_argument('--names', default='陈建国,陈建军,陈建民,李秀兰,王秀兰')
    ap.add_argument('--thr', type=float, default=0.55)
    a = ap.parse_args()

    script = parse_script(a.script, a.names.split(','))
    feed = parse_feed(a.feed)
    with open(a.feed, encoding='utf-8') as source:
        feed_raw = source.read()

    print(f'=== 剧本↔投喂 台词对照 ===')
    print(f'剧本：{os.path.basename(a.script)}（{len(script)} 句）')
    print(f'投喂：{os.path.basename(a.feed)}（{len(feed)} 句）\n')

    missing, weak = [], []
    feed_all = norm("".join(x[2] for x in feed))
    print('--- 上游台词逐句核对（4-gram 覆盖率，对拆镜友好）---')
    for i, (role, hint, line) in enumerate(script, 1):
        if not norm(line):
            # 修正：纯标点/符号台词（如「陈建民：……」）去标点后为空，
            # 4-gram 无从判定。旧版一律判 0.0，把合法的「沉默标注」误报为缺失；
            # 现改用原文匹配。
            s = 1.0 if line.strip() in feed_raw else 0.0
        else:
            s = ngram_cov(line, feed_all, 4)
        if s < 0.5:
            missing.append((i, role, hint, line, s)); tag = '❌ 缺失'
        elif s < 0.85:
            weak.append((i, role, line, s)); tag = f'⚠ 部分覆盖 {s:.2f}'
        else:
            tag = f'✓ {s:.2f}'
        print(f'{i:2d}. [{tag}] {role}：{line[:46]}')

    # 投喂稿有、剧本无（新增/改写，仅提示）
    print('\n--- 投喂稿独有（剧本无，可能是合理改写或噪声）---')
    extra = 0
    for role, tone, line in feed:
        if not norm(line):
            # 纯标点台词（如「……」）：与上游按原文比对
            if any(line.strip() == x[2].strip() for x in script):
                continue
        elif any(best_match(line, [x], a.thr)[0] for x in script):
            continue
        # 反向匹配
        found = False
        for x in script:
            bm, bs = best_match(x[2], [(role, tone, line)], a.thr)
            if bm:
                found = True
                break
        if not found:
            extra += 1
            print(f'   + {role}（{tone}）：{line[:46]}')
    if extra == 0:
        print('   （无）')

    print('\n=== 汇总 ===')
    print(f'剧本 {len(script)} 句 / 投喂 {len(feed)} 句')
    print(f'❌ 缺失 {len(missing)} 句 / ⚠ 弱匹配 {len(weak)} 句 / 投喂独有 {extra} 句')
    if missing:
        print('\n★ 缺失明细（必须补进投喂稿，否则该镜无因/题眼丢失）：')
        for i, role, hint, line, s in missing:
            print(f'   剧本第 {i} 句 · {role}{("（" + hint + "）") if hint else ""}：{line}')
    sys.exit(2 if missing else (1 if weak else 0))


def self_test():
    """★P11 新增（2026-10-24）：本脚本此前完全游离在自测体系外。
    它对账的是「剧本每一句台词是否都进了投喂稿」，判错的方向两边都致命——
    假报缺失会让作者去补本来就在的台词；漏报缺失就是台词在镜头上凭空消失。
    这里把两条核心判据的正反例钉死。"""
    ok = True
    if norm("你好，世界！A1") != "你好世界A1":
        print("FAIL self-test: norm 未剥离标点", repr(norm("你好，世界！A1"))); ok = False
    if abs(ngram_cov("他推开门走了进去", "他推开门走了进去") - 1.0) > 1e-9:
        print("FAIL self-test: ngram_cov 自比对不为 1.0"); ok = False
    if ngram_cov("他推开门走了进去", "完全不同的一句话内容") >= 0.2:
        print("FAIL self-test: ngram_cov 对无关句给了不应有的相似度"); ok = False
    # 超短台词（「嗯」「怎么？」）走包含判定——旧实现因窗口下限 j-i>=3 恒为 0，
    # 每句「嗯」都被误报成「投喂独有」。
    if ngram_cov("嗯", "他说嗯了一声") != 1.0:
        print("FAIL self-test: 超短台词包含判定失效（旧 bug 复发）"); ok = False
    hit, _ = best_match("嗯。", [("林风", "", "嗯")])
    if hit is None:
        print("FAIL self-test: best_match 未匹配到超短台词（会误报缺失）"); ok = False
    hit2, sc2 = best_match("这句话在池子里根本不存在吧", [("林风", "", "今天天气不错")])
    if hit2 is not None:
        print(f"FAIL self-test: best_match 对无关句误匹配（score={sc2:.2f}）"); ok = False
    print('[+] self-test PASSED' if ok else 'FAIL self-test')
    return ok


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        sys.exit(0 if self_test() else 1)
    main()
