"""完整章节分页、真实覆盖与 CLI 兼容性回归。"""
import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import slice_context as slicer


class SliceStabilityTests(unittest.TestCase):
    def test_complete_chapters_and_lossless_pages(self):
        raw = ['# 文档', '前言', '## 第一章', *['正文'] * 80,
               '### 子节', '子节正文', '## 第二章', '末行']
        pages = slicer.chapter_pages(raw, 10)
        self.assertEqual(pages, [(0, 2), (2, 85), (85, 87)])
        self.assertEqual([line for start, end in pages for line in raw[start:end]], raw)

    def test_fences_and_frontmatter_do_not_split(self):
        raw = ['---', 'name: 示例', '---', '# 标题', '## 第一章',
               '```markdown', '## 假标题', '```', '~~~', '## 另一个假标题',
               '~~~', '| 表 |', '|---|', '| 值 |', '## 第二章', '结束']
        self.assertEqual(slicer.chapter_pages(raw, 1), [(0, 4), (4, 14), (14, 16)])

    def test_no_heading_and_empty_file(self):
        self.assertEqual(slicer.chapter_pages(['内容'] * 99, 1), [(0, 99)])
        self.assertEqual(slicer.chapter_pages([], 40), [])

    def test_multiple_top_level_chapters(self):
        self.assertEqual(slicer.chapter_pages(['# 甲', '甲正文', '# 乙', '乙正文'], 1),
                         [(0, 2), (2, 4)])

    def test_coverage_missing_and_non_cumulative(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root, 'fixture.md').write_text('# 标题\n前言\n## 章一\n甲\n## 章二\n乙\n', encoding='utf-8')
            with patch.object(slicer, 'SUITE_DIR', root), patch.object(
                    slicer, 'resolve_files', return_value=['fixture.md', 'missing.md']):
                first = slicer.build_slice('P3', max_lines_per_file=2)
                second = slicer.build_slice('P3', max_lines_per_file=2, page=2)
                self.assertIn('coverage=2/6 行；本页范围=L1-L2', first)
                self.assertIn('未加载=L3-L6', first)
                self.assertIn('未加载=L1-L2、L5-L6', second)
                self.assertIn('；缺失；未加载=全文', first)
                self.assertIn('--page 2', first)
                self.assertNotIn('> 已读子库：', first)
                self.assertNotIn('乙', second)
                with self.assertRaises(ValueError):
                    slicer.build_slice('P3', page=99)

    def test_source_and_previs_resolution(self):
        for source in ('3', '4'):
            for stage in ('P0', 'P1'):
                files = slicer.resolve_files(stage, source=source, previs=True)
                self.assertIn('sd-recon-engine/references/intel-card.md', files)
                self.assertIn('sd-storyboard-engine/references/p45-previs-storyboard.md', files)
                self.assertEqual(len(files), len(set(files)))
        self.assertFalse(any('sd-recon-engine' in p for p in slicer.resolve_files('P0')))
        self.assertFalse(any('p45-previs' in p for p in slicer.resolve_files('P3')))

    def test_all_real_files_are_lossless(self):
        files = set()
        for stage in slicer.STAGE_FILES:
            for combat in ('none', 'R1', 'R2', 'R3'):
                files.update(slicer.resolve_files(stage, combat, '2.5', '3', True))
        for rel in sorted(files):
            with self.subTest(file=rel):
                raw = Path(slicer.SUITE_DIR, rel).read_text(encoding='utf-8').splitlines()
                pages = slicer.chapter_pages(raw, 40)
                self.assertEqual([line for start, end in pages for line in raw[start:end]], raw)
                for left, right in zip(pages, pages[1:]):
                    self.assertEqual(left[1], right[0])

    def cli(self, *args):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
        return subprocess.run([sys.executable, slicer.__file__, *args],
                              capture_output=True, text=True, encoding='utf-8', env=env)

    def test_cli_source_previs_and_continuation(self):
        result = self.cli('--stage', 'P1', '--source', '3', '--previs', '--page', '2')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('sd-recon-engine/references/intel-card.md', result.stdout)
        self.assertIn('p45-previs-storyboard.md', result.stdout)
        self.assertIn('--source 3 --lines 40 --previs --page 3', result.stdout)

    def test_estimate_compatibility(self):
        result = self.cli('--estimate', '--stage', 'P0', '--source', '4', '--previs', '--episodes', '10')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('预算报账', result.stdout)
        self.assertIn('按结构切', result.stdout)
        self.assertIn('当前页输出估算', result.stdout)
        self.assertIn('预算报账', slicer.build_estimate('P3', 'none', '2.5', 'M1', 40, 1, 0))

    def test_invalid_cli_parameters(self):
        for args in [('--page', '0'), ('--lines', '-1'), ('--page', '999999'),
                     ('--episodes', '0'), ('--chars-per-episode', '-1')]:
            with self.subTest(args=args):
                self.assertEqual(self.cli(*args).returncode, 2)

    def test_self_test_compatibility(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(slicer.self_test(), 0)
        result = self.cli('--self-test')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASSED', result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
