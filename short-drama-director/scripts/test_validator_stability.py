"""校验器稳定性回归；仅用标准库，临时样本不写入项目。"""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
DIRECTOR = ROOT / 'short-drama-director/scripts'
FEED = ROOT / 'sd-feed-engine/scripts'
sys.path[:0] = [str(DIRECTOR), str(FEED)]
import validate_prompt as validator
import audit_contract as audit
import gate_check as gate
import script_feed_diff as diff


class StabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'sample.md'

    def unit(self, start=1, dialogue='', tail=''):
        return ('## 【投喂单元】\n```text\n【画幅风格】\n【场景资产】\n'
                '【核心人物】\n【站位声明】\n【时间轴分镜】\n'
                f'00:00-00:02 [镜头{start}] 台词：{dialogue} {tail}\n```\n')

    def cli(self, module, args):
        output = io.StringIO()
        with patch.object(sys, 'argv', [module.__file__, *args]), contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as result:
                module.main()
        return result.exception.code, output.getvalue()

    def test_dialogue_blocks(self):
        text = '台词：【甲(正常)："先说一句\"你好\""】【乙（急促）：“再说一句”】【丙："缺语气"】'
        self.path.write_text(text, encoding='utf-8')
        lines = gate.parse_lines(text)
        self.assertEqual([x[0] for x in lines], ['甲', '乙', '丙'])
        self.assertEqual(lines[0][2], '先说一句"你好"')
        self.assertEqual(diff.parse_feed(self.path), [x[:3] for x in lines])
        self.assertEqual(gate.parse_lines('【画幅风格】台词：无'), [])

    def test_budget_and_freeze(self):
        for dialogue, tail, overload in [
            ('【甲(正常)："一二三四五六七八九十"】', '', False),
            ('【甲(正常)："一二三四五六七八九十"】', '末1秒定格', True),
            ('【甲(正常)："一二三四五六七八九十"】', '不做末1秒定格', False),
            ('【甲(正常)："一二三四五六七"】【乙(正常)："一二三四五六七"】', '', True),
        ]:
            with self.subTest(tail=tail, dialogue=dialogue):
                self.path.write_text('素材形态：M0\n' + self.unit(dialogue=dialogue, tail=tail), encoding='utf-8')
                _, out = self.cli(gate, [str(self.path), '--tol', '0', '--syntax', 'off'])
                self.assertEqual('真念不完' in out, overload)

    def test_global_ids(self):
        # P14：闸门0 的「七段缺栏 / 接续状态残留」已移交 C 系，本层只留【】配对与镜号连续；
        #   用例走 --syntax off，专测本层镜号判据（否则夹具缺【音效】栏会被 C7 判 FAIL，测不到镜号）。
        for first, second, valid in [(7, 8, True), (1, 1, True), (7, 9, False), (7, 7, False)]:
            self.path.write_text('素材形态：M0\n' + self.unit(first) + self.unit(second), encoding='utf-8')
            code, out = self.cli(gate, [str(self.path), '--syntax', 'off'])
            self.assertEqual(code == 0, valid, out)

    def test_scopes(self):
        # ★P2 口径：feed-only 不再无条件豁免 CT2——只交投喂稿必须在稿内声明「资产另册」，
        #   否则按「资产缺失」FAIL。故夹具须带上该声明（2026-10-23 体检修：本用例曾因此长期红灯）。
        feed = 'M0\n资产另册：三天_资产提示词.md\n【时间轴分镜】【站位声明】'
        self.assertFalse(audit.audit_markdown(feed, delivery='feed-only')[0])
        self.assertTrue(audit.audit_markdown(feed, delivery='full-project')[0])
        self.assertTrue(audit.audit_markdown(feed, delivery='agent-bundle')[0])
        assets = ('全图共4格 无脸全身 五官10项 Voice Description\n'
                  '场景母版 九宫格摄影机矩阵 标注降级条款\n'
                  '道具设定图 正面视图 45°侧视图 俯视图 禁止手持\n')
        self.assertFalse(audit.audit_markdown(feed + assets, delivery='agent-bundle')[0])
        self.assertTrue(audit.audit_markdown('M0', delivery='feed-only')[0])
        with self.assertRaises(ValueError):
            audit.audit_markdown(feed, delivery='typo')

    def test_render_parity(self):
        # 同 test_scopes：feed-only 需声明资产另册（P2 口径），否则 CT2 FAIL 导致期望值失效
        self.path.write_text('M0\n资产另册：三天_资产提示词.md\n【时间轴分镜】【站位声明】', encoding='utf-8')
        cases = [([], [], 0), (['--contract'], [], 1),
                 (['--delivery', 'feed-only'], [], 0),
                 (['--delivery', 'full-project'], [], 1),
                 ([], ['C20c 测试高危'], 1),
                 (['--allow-warn'], ['C20c 测试高危'], 0)]
        for args, warnings, expected in cases:
            with self.subTest(args=args, warnings=warnings):
                def fake(*a, **kw):
                    return [], list(warnings), {'duration_s': 2, 'shots': 1, 'chars': 10}
                with patch.object(validator, '_looks_like_feed', return_value=True), patch.object(validator, 'validate', side_effect=fake):
                    code, text = self.cli(validator, [*args, str(self.path)])
                    jcode, raw = self.cli(validator, [*args, str(self.path), '--json'])
                data = json.loads(raw)
                self.assertEqual((code, jcode), (expected, expected))
                self.assertEqual(bool(data['issues']), bool(expected))
                for issue in data['issues']:
                    self.assertIn(issue, text)
                for warn in data['warnings']:
                    self.assertIn(warn, text)

    def test_contract_fail_closed(self):
        self.path.write_text('【时间轴分镜】', encoding='utf-8')
        for fault in ('missing', 'exception'):
            for json_flag in ([], ['--json']):
                with self.subTest(fault=fault, json_flag=json_flag):
                    failure = (patch.dict(sys.modules, {'audit_contract': None}) if fault == 'missing'
                               else patch.object(audit, 'audit_markdown', side_effect=RuntimeError('故障注入')))
                    with failure, patch.object(validator, '_looks_like_feed', return_value=True), patch.object(
                        validator, 'validate', side_effect=lambda *a, **kw: ([], [], {'duration_s': 0, 'shots': 0, 'chars': 0})):
                        code, out = self.cli(validator, [str(self.path), '--contract', '--allow-warn', *json_flag])
                    self.assertEqual(code, 1)
                    self.assertIn('fail closed', out)
                    if json_flag:
                        self.assertTrue(json.loads(out)['issues'])

    def test_diff_cli(self):
        script = self.path.with_name('script.md')
        script.write_text('甲：你好\n乙：再见\n', encoding='utf-8')
        for text, expected in [('【甲(正常)："你好"】【乙(正常)："再见"】', 0),
                               ('【甲(正常)："你好"】', 2)]:
            self.path.write_text(text, encoding='utf-8')
            code, _ = self.cli(diff, ['--script', str(script), '--feed', str(self.path), '--names', '甲,乙'])
            self.assertEqual(code, expected)

    def test_real_cli_parity(self):
        self.path.write_text('素材形态：M0\n' + self.unit(dialogue='【甲(正常)："你好"】'), encoding='utf-8')
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
        command = [sys.executable, str(DIRECTOR / 'validate_prompt.py'), str(self.path), '--contract']
        text = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', env=env)
        machine = subprocess.run(command + ['--json'], capture_output=True, text=True, encoding='utf-8', env=env)
        self.assertEqual(text.returncode, machine.returncode)
        self.assertEqual(machine.returncode, 1)
        data = json.loads(machine.stdout)
        self.assertTrue(any(x.startswith('C31') for x in data['issues']))
        for issue in data['issues']:
            self.assertIn(issue, text.stdout)
        for warning in data['warnings']:
            self.assertIn(warning, text.stdout)

    def test_existing_self_tests(self):
        for folder, name in [(DIRECTOR, 'validate_prompt.py'), (DIRECTOR, 'audit_contract.py'), (FEED, 'gate_check.py')]:
            with self.subTest(name=name):
                env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
                run = subprocess.run([sys.executable, str(folder / name), '--self-test'],
                                     capture_output=True, text=True, encoding='utf-8', env=env)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
