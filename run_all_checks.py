#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""漫剧老李 AIGC 全流程 Skill (V8.2.0-SLIM) 根目录统一自检入口

用法:
    python run_all_checks.py
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CHECKS = [
    ("包级完整性校验 (check_package.py)", [sys.executable, os.path.join(ROOT, "short-drama-director/scripts/check_package.py")]),
    ("锁凭证机检自检 (check_locks.py)", [sys.executable, os.path.join(ROOT, "short-drama-director/scripts/check_locks.py"), "--self-test"]),
    ("交付契约核销自检 (audit_contract.py)", [sys.executable, os.path.join(ROOT, "short-drama-director/scripts/audit_contract.py"), "--self-test"]),
    ("投喂层闸门自检 (gate_check.py)", [sys.executable, os.path.join(ROOT, "sd-feed-engine/scripts/gate_check.py"), "--self-test"]),
    ("剧本滚动状态包自检 (rolling_checkpoint.py)", [sys.executable, os.path.join(ROOT, "sd-script-engine/scripts/rolling_checkpoint.py"), "--self-test"]),
    ("剧本可拍性机检 (validate_episode.py)", [sys.executable, os.path.join(ROOT, "sd-script-engine/scripts/validate_episode.py"), "--self-test"]),
    ("投喂包 JSON/CSV 导出自检 (export_feed_bundle.py)", [sys.executable, os.path.join(ROOT, "sd-feed-engine/scripts/export_feed_bundle.py"), "--self-test"]),
    ("提示词一键防字幕清洗自检 (autofix_feed.py)", [sys.executable, os.path.join(ROOT, "sd-feed-engine/scripts/autofix_feed.py"), "--self-test"]),
    ("离线看板编译与另册挂载自检 (build_board_lite.py)", [sys.executable, os.path.join(ROOT, "short-drama-director/scripts/build_board_lite.py"), "--self-test"]),
    ("统一阶段门禁入口自检 (run_stage.py)", [sys.executable, os.path.join(ROOT, "run_stage.py"), "--self-test"]),
]


def main():
    failed = []
    for label, cmd in CHECKS:
        print(f"\n=== {label} ===")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            sys.stdout.write(res.stdout[-1500:] if res.stdout else "")
            if res.stderr:
                sys.stderr.write(res.stderr[-1000:])
            failed.append(label)
            print(f"[-] FAILED: {label}")
        else:
            lines = [l for l in res.stdout.splitlines() if l.strip()]
            for l in lines[-3:]:
                print(l)
            print(f"[+] PASSED: {label}")
    if failed:
        print(f"\n[-] 未全部通过 ({len(failed)} 项): {failed}")
        return 1
    print(f"\n[+] 全部 {len(CHECKS)} 项全流程总检 PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
