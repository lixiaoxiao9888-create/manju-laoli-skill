"""标准库正反例；临时输出全部位于系统临时目录并自动清理。

P14：包内不再存放示例工程文件（案例示例已整体剔除）。本测试所需的工程数据
以 `_FIXTURE` 常量内联在脚本里，运行期写入系统临时目录再交给被测函数读取——
测试夹具不是「示例」，不进交付物。
"""
import atexit
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import project_bundle as bundle


SCRIPT = Path(__file__).with_name("project_bundle.py")

# 两段各 15 秒、共 30 秒的最小合规工程（测试夹具 · 内联 · 非交付示例）
_FIXTURE = {
    "project": {"model": "Seedance 2.0", "video_aspect": "9:16",
                "asset_aspect": "16:9", "total_duration": 30},
    "characters": [
        {"id": "char-lin", "visual_age": 28,
         "description": "短黑发，浅蓝棉衬衣，深灰长裤，右腕戴布绳。"},
    ],
    "assets": [
        {"id": "asset-lin", "type": "character", "aspect": "16:9",
         "prompt": "28岁短黑发人物，浅蓝棉衬衣、深灰长裤、右腕布绳，日常比例，白色背景四视图。待验证，未实拍。",
         "refs": ["char-lin"]},
        {"id": "asset-room", "type": "scene", "aspect": "16:9",
         "prompt": "修理室母版，木桌在窗下，左侧窗户向右投射午后自然光，桌上只有一台旧收音机，无人。待验证，未实拍。",
         "refs": []},
        {"id": "asset-radio", "type": "prop", "aspect": "16:9",
         "prompt": "棕色木壳旧收音机，圆形黑色旋钮，亚麻扬声器网，纯道具展示。待验证，未实拍。",
         "refs": []},
    ],
    "segments": [
        {
            "id": "seg-01", "duration": 15,
            "entry_state": "林坐在窗下木桌前，收音机静音，右手放在桌边。",
            "exit_state": "林坐在窗下木桌前，右手握住收音机旋钮，收音机发出音乐。",
            "shots": [
                {"id": "shot-001", "start": 0, "end": 3,
                 "action": "林的右手从桌边伸向棕色收音机，左窗自然光照亮袖口。",
                 "camera": "手部近景，缓慢跟随右手。", "dialogues": [],
                 "asset_refs": ["asset-lin", "asset-room", "asset-radio"]},
                {"id": "shot-002", "start": 3, "end": 7,
                 "action": "林抬眼看着木桌上的收音机，双唇张开，眉头收紧。",
                 "camera": "面部近景，轻推至眼睛。",
                 "dialogues": [{"character_id": "char-lin", "text": "再试一次。"}],
                 "asset_refs": ["asset-lin", "asset-room"]},
                {"id": "shot-003", "start": 7, "end": 12,
                 "action": "林右手握住黑色旋钮，缓缓转动，亚麻网罩轻微振动。",
                 "camera": "旋钮特写，固定机位观察转动。", "dialogues": [],
                 "asset_refs": ["asset-lin", "asset-radio"]},
                {"id": "shot-004", "start": 12, "end": 15,
                 "action": "林保持坐姿和右手握旋钮的动作，收音机响起音乐，木桌背景稳定。",
                 "camera": "中景，缓慢拉开建立人物与木桌关系。", "dialogues": [],
                 "asset_refs": ["asset-lin", "asset-room", "asset-radio"]},
            ],
        },
        {
            "id": "seg-02", "duration": 15,
            "entry_state": "林坐在窗下木桌前，右手握住收音机旋钮，收音机发出音乐。",
            "exit_state": "林坐在窗下木桌前，双手放在腿上，收音机继续播放音乐。",
            "shots": [
                {"id": "shot-005", "start": 0, "end": 4,
                 "action": "林松开旋钮，右手移回木桌边，窗光继续从左侧照入。",
                 "camera": "侧面中近景，跟随手部回移。", "dialogues": [],
                 "asset_refs": ["asset-lin", "asset-room", "asset-radio"]},
                {"id": "shot-006", "start": 4, "end": 7,
                 "action": "林双唇张开，目光落在收音机扬声器网罩上，眉头舒展。",
                 "camera": "面部近景，小幅推近记录反应。",
                 "dialogues": [{"character_id": "char-lin", "text": "原来你还会唱。"}],
                 "asset_refs": ["asset-lin", "asset-radio"]},
                {"id": "shot-007", "start": 7, "end": 12,
                 "action": "林将双手放在腿上，保持坐姿听音乐，木桌和左侧窗框同时入画。",
                 "camera": "中景，向右平移露出窗框。", "dialogues": [],
                 "asset_refs": ["asset-lin", "asset-room", "asset-radio"]},
                {"id": "shot-008", "start": 12, "end": 15,
                 "action": "林保持双手放腿上的坐姿，棕色收音机继续播放音乐，窗光落在木桌。",
                 "camera": "全景，固定机位保留人物和收音机关系。", "dialogues": [],
                 "asset_refs": ["asset-lin", "asset-room", "asset-radio"]},
            ],
        },
    ],
}

_FIXTURE_DIR = None


def _fixture_path():
    """把内联夹具写到系统临时目录，返回路径（供 CLI 子进程用例复用）。"""
    global _FIXTURE_DIR
    if _FIXTURE_DIR is None:
        _FIXTURE_DIR = tempfile.mkdtemp(prefix="sd-bundle-fixture-")
        atexit.register(shutil.rmtree, _FIXTURE_DIR, True)
        Path(_FIXTURE_DIR, "fixture-project.json").write_text(
            json.dumps(_FIXTURE, ensure_ascii=False, indent=2), encoding="utf-8")
    return Path(_FIXTURE_DIR, "fixture-project.json")


class ProjectBundleTests(unittest.TestCase):
    def setUp(self):
        self.data = bundle.load_project(_fixture_path())

    def codes(self):
        return {x["code"] for x in bundle.validate(self.data)["issues"]}

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                              capture_output=True, encoding="utf-8",
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"})

    def test_valid_fixture_and_no_mutation(self):
        before = copy.deepcopy(self.data)
        report = bundle.validate(self.data)
        self.assertEqual(report, {"structural_status": "valid", "semantic_status": "needs_review", "issues": []})
        self.assertEqual(before, self.data)
        self.assertEqual([s["duration"] for s in self.data["segments"]], [15, 15])

    def test_duplicate_shot_across_segments(self):
        self.data["segments"][1]["shots"][0]["id"] = "shot-001"
        self.assertIn("DUPLICATE_ID", self.codes())

    def test_duplicate_ids_all_entity_types(self):
        for field in ("characters", "assets", "segments"):
            with self.subTest(field=field):
                original = copy.deepcopy(self.data)
                self.data[field].append(copy.deepcopy(self.data[field][0]))
                self.assertIn("DUPLICATE_ID", self.codes())
                self.data = original

    def test_dangling_references(self):
        for target, key, value in (
            (self.data["assets"][0], "refs", ["missing"]),
            (self.data["segments"][0]["shots"][0], "asset_refs", ["char-lin"]),
            (self.data["segments"][0]["shots"][1]["dialogues"][0], "character_id", "asset-lin"),
        ):
            with self.subTest(key=key):
                old = target[key]
                target[key] = value
                self.assertIn("DANGLING_REF", self.codes())
                target[key] = old

    def test_visual_age_rejects_float_bool_string_negative(self):
        for age in (28.0, True, "28", -1, None):
            with self.subTest(age=age):
                self.data["characters"][0]["visual_age"] = age
                self.assertIn("VISUAL_AGE", self.codes())

    def test_assets_are_landscape_independent_of_video(self):
        self.assertEqual(self.data["project"]["video_aspect"], "9:16")
        self.data["assets"][0]["aspect"] = "9:16"
        self.assertIn("ASSET_ASPECT", self.codes())
        self.data["assets"][0]["aspect"] = "16:9"
        self.data["project"]["asset_aspect"] = "9:16"
        self.assertIn("ASSET_ASPECT", self.codes())

    def test_total_duration(self):
        self.data["project"]["total_duration"] = 29
        self.assertIn("TOTAL_DURATION", self.codes())

    def test_coverage_gap_overlap_outside_zero_and_tail(self):
        original = copy.deepcopy(self.data)
        for index, key, value in ((0, "start", 1), (1, "start", 2), (1, "start", 4),
                                  (3, "end", 16), (0, "end", 0), (3, "end", 14)):
            with self.subTest(index=index, key=key, value=value):
                self.data = copy.deepcopy(original)
                self.data["segments"][0]["shots"][index][key] = value
                self.assertIn("SHOT_COVERAGE", self.codes())

    def test_state_mismatch_requires_transition_but_not_semantic_pass(self):
        segment = self.data["segments"][1]
        segment["entry_state"] = "林站在门口。"
        self.assertIn("STATE_TRANSITION", self.codes())
        segment["transition"] = "空镜交代时间流逝，再切门口。"
        report = bundle.validate(self.data)
        self.assertEqual(report["structural_status"], "valid")
        self.assertEqual(report["semantic_status"], "needs_review")
        segment["transition"] = " "
        self.assertIn("SCHEMA", self.codes())

    def test_dialogue_budget_is_cumulative_warning(self):
        shot = self.data["segments"][0]["shots"][0]
        shot["dialogues"] = [{"character_id": "char-lin", "text": "一" * 9}] * 2
        report = bundle.validate(self.data)
        self.assertEqual(report["structural_status"], "valid")
        warnings = [x for x in report["issues"] if x["code"] == "DIALOGUE_BUDGET"]
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["level"], "WARN")
        self.assertEqual(report["semantic_status"], "needs_review")

    def test_invalid_schema_shapes_and_numbers(self):
        for data in (None, [], {}, {**self.data, "segments": []},
                     {**self.data, "assets": [None]}):
            with self.subTest(data=data):
                self.assertEqual(bundle.validate(data)["structural_status"], "error")
        for value in (True, float("nan"), float("inf"), "30", 0, -1):
            self.data["project"]["total_duration"] = value
            self.assertIn("SCHEMA", self.codes())

    def test_export_same_shots_deterministic_and_correct_stage(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "out"
            bundle.export_bundle(self.data, output)
            self.assertEqual({p.name for p in output.iterdir()}, {"assets-prompts.md", "P3CLEAN_GRID.md"})
            docs = {p.name: p.read_text(encoding="utf-8") for p in output.iterdir()}
            self.assertEqual(docs, bundle.render(self.data, bundle.validate(self.data)))
            for document in docs.values():
                self.assertIn("needs_review", document)
                for segment in self.data["segments"]:
                    for shot in segment["shots"]:
                        self.assertIn(f"### {shot['id']} [{shot['start']}-{shot['end']}s]", document)
                        self.assertIn(shot["action"], document)
                        self.assertIn(shot["camera"], document)
                        for dialogue in shot["dialogues"]:
                            self.assertIn(dialogue["text"], document)
            self.assertIn("# P3CLEAN_GRID", docs["P3CLEAN_GRID.md"])
            self.assertIn("布局：2 行 × 2 列", docs["P3CLEAN_GRID.md"])
            self.assertIn("无文字", docs["P3CLEAN_GRID.md"])

    def test_error_export_never_creates_output(self):
        self.data["segments"][0]["shots"][0]["asset_refs"] = ["missing"]
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "out"
            with self.assertRaises(bundle.BundleError):
                bundle.export_bundle(self.data, output)
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "out"
            output.mkdir()
            sentinel = output / "assets-prompts.md"
            sentinel.write_bytes(b"original")
            with self.assertRaises(bundle.BundleError):
                bundle.export_bundle(self.data, output)
            self.assertEqual(sentinel.read_bytes(), b"original")
            self.assertEqual(list(output.iterdir()), [sentinel])

    def test_write_failure_leaves_no_partial_files(self):
        with tempfile.TemporaryDirectory() as temp:
            real_write = Path.write_text
            calls = 0

            def fail_second(path, *args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("模拟第二份文件写入失败")
                return real_write(path, *args, **kwargs)

            with patch.object(Path, "write_text", fail_second):
                with self.assertRaises(OSError):
                    bundle.export_bundle(self.data, Path(temp) / "out")
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_cli_validate_and_export(self):
        self.assertEqual(self.cli("validate", _fixture_path()).returncode, 0)
        with tempfile.TemporaryDirectory() as temp:
            result = self.cli("export", _fixture_path(), "-o", Path(temp) / "out")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["semantic_status"], "needs_review")
            self.assertTrue((Path(temp) / "out" / "P3CLEAN_GRID.md").is_file())

    def test_cli_bad_json_duplicate_keys_nan_and_missing_file(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "bad.json"
            output = Path(temp) / "out"
            for content in ("{", '{"project": 1, "project": 2}', '{"x": NaN}', '{"x": Infinity}'):
                source.write_text(content, encoding="utf-8")
                result = self.cli("export", source, "-o", output)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertFalse(output.exists())
                self.assertEqual({p.name for p in Path(temp).iterdir()}, {"bad.json"})
            self.assertEqual(self.cli("validate", Path(temp) / "missing.json").returncode, 1)

    def test_warning_does_not_block_export(self):
        self.data["segments"][0]["shots"][0]["dialogues"] = [{"character_id": "char-lin", "text": "长" * 100}]
        with tempfile.TemporaryDirectory() as temp:
            bundle.export_bundle(self.data, Path(temp) / "out")
            self.assertIn("DIALOGUE_BUDGET", (Path(temp) / "out" / "P3CLEAN_GRID.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
