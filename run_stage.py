#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""漫剧老李 AIGC 全流程 Skill · 统一阶段门禁入口 (run_stage.py · V8.2.0-SLIM-rev4)

将分散在各引擎的阶段检查收口为单入口，避免长流程中漏跑某一环：
    python run_stage.py --stage P0  <00_立项包.md> [--multi-segment]
    python run_stage.py --stage P2  <02_资产交付.md>
    python run_stage.py --stage P4  <05_项目主档.md> [--model 2.5|2.0] [--aspect 16:9|9:16|21:9] [--board]
    python run_stage.py --stage P45 <预演故事板.md>
    python run_stage.py --self-test
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

SCRIPTS = {
    "check_locks": os.path.join(ROOT, "short-drama-director/scripts/check_locks.py"),
    "check_asset_blocks": os.path.join(ROOT, "short-drama-director/scripts/check_asset_blocks.py"),
    "gate_check": os.path.join(ROOT, "sd-feed-engine/scripts/gate_check.py"),
    "audit_contract": os.path.join(ROOT, "short-drama-director/scripts/audit_contract.py"),
    "check_p45": os.path.join(ROOT, "sd-storyboard-engine/scripts/check_p45.py"),
    "build_board_lite": os.path.join(ROOT, "short-drama-director/scripts/build_board_lite.py"),
}


def _run(label, cmd):
    print(f"\n=== [{label}] ===")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"[-] FAILED: {label} (exit={res.returncode})")
        return False
    print(f"[+] PASSED: {label}")
    return True


def self_test():
    missing = [k for k, p in SCRIPTS.items() if not os.path.isfile(p)]
    if missing:
        print(f"[-] run_stage.py self-test FAILED: missing scripts {missing}")
        return 1
    print(f"[+] run_stage.py self-test PASSED ({len(SCRIPTS)} stage scripts wired)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="漫剧老李 Skill 统一阶段门禁入口")
    ap.add_argument("--stage", choices=["P0", "P2", "P4", "P45"], help="目标阶段")
    ap.add_argument("file", nargs="?", help="待检查的 Markdown 文件路径")
    ap.add_argument("--multi-segment", action="store_true", help="P0 多段任务（追加 D 锁必填）")
    ap.add_argument("--model", default="2.5", choices=["2.5", "2.0"], help="P4 模型版本")
    ap.add_argument("--aspect", default="16:9", help="P4 成片画幅")
    ap.add_argument("--board", action="store_true", help="P4 门禁通过后自动编译离线看板 HTML")
    ap.add_argument("--self-test", action="store_true", help="自检脚本接线完整性")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if not args.stage or not args.file:
        ap.print_help()
        return 2

    if not os.path.isfile(args.file):
        print(f"[!] 文件不存在：{args.file}")
        return 2

    ok = True
    if args.stage == "P0":
        cmd = [sys.executable, SCRIPTS["check_locks"], args.file]
        if args.multi_segment:
            cmd.append("--multi-segment")
        ok = _run("P0 锁凭证硬检 (check_locks.py)", cmd)
    elif args.stage == "P2":
        ok = _run("P2 资产块结构机检 (check_asset_blocks.py)",
                  [sys.executable, SCRIPTS["check_asset_blocks"], args.file])
    elif args.stage == "P45":
        ok = _run("P4.5 预演故事板机检 (check_p45.py)",
                  [sys.executable, SCRIPTS["check_p45"], args.file])
    elif args.stage == "P4":
        ok1 = _run("P4 投喂层闸门 + C系机检 (gate_check.py)",
                   [sys.executable, SCRIPTS["gate_check"], args.file,
                    "--model", args.model, "--aspect", args.aspect])
        ok2 = _run("P4 交付契约核销 (audit_contract.py)",
                   [sys.executable, SCRIPTS["audit_contract"], args.file])
        ok = ok1 and ok2
        if ok and args.board:
            ok = _run("P4 离线看板编译 (build_board_lite.py)",
                      [sys.executable, SCRIPTS["build_board_lite"], args.file])

    print(f"\n=== 阶段 {args.stage} 总结论：{'PASSED' if ok else 'FAILED'} ===")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
