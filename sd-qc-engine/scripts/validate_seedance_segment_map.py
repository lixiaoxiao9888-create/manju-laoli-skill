#!/usr/bin/env python3
import argparse
import json
import math
import sys
from pathlib import Path

ROOT_FIELDS = {
    "schema_version", "artifact_type", "project_id", "stage_id",
    "artifact_version", "input_versions", "scope", "status",
    "assumptions", "open_items", "payload",
}
ENTRY_TYPES = {
    "SCENE_ENTRY", "VISIBLE_CUT", "CONTINUOUS_TAKE",
    "HIDDEN_SEAM", "GENERATION_ONLY_BOUNDARY",
}
EXIT_TYPES = {
    "VISIBLE_CUT", "CONTINUOUS_TAKE", "HIDDEN_SEAM",
    "GENERATION_ONLY_BOUNDARY", "SCENE_END",
}
ALIGNMENTS = {
    "ALIGNED_AT_SEGMENT_END", "NO_APPROVED_CUT_AVAILABLE",
    "PROTECTED_CONTINUATION", "SCENE_END",
}
DIALOGUE_INTEGRITY = {
    "WHOLE", "CLAUSE_HEAD", "CLAUSE_MIDDLE", "CLAUSE_TAIL",
}
SEGMENT_FIELDS = {
    "segment_id", "duration", "shot_ids", "story_units",
    "dialogue_slices", "visual_action_units", "boundary_from_previous",
    "boundary_to_next", "boundary_selection", "continuity_handoff",
    "entry_state", "exit_state", "next_first_action",
}
BOUNDARY_FIELDS = {
    "type", "director_cut_directive_id", "hidden_seam_id",
    "reason", "safety_checks",
}
SAFETY_FIELDS = {
    "dialogue_safe", "action_safe", "reaction_safe", "camera_safe",
}
SELECTION_FIELDS = {
    "selected_time", "candidate_type", "why_selected",
    "approved_cut_candidates_before_deadline", "cut_alignment",
    "cut_alignment_override_reason",
}
HANDOFF_FIELDS = {
    "anchor_description", "must_match",
    "previous_approved_tail_ref_required", "tail_usage",
}
DIALOGUE_FIELDS = {
    "dialogue_id", "speaker_id", "voice_id", "exact_text",
    "start", "end", "integrity", "split_anchor",
    "continues_to_segment_id",
}


def close(a, b, tolerance=1e-6):
    return math.isclose(float(a), float(b), abs_tol=tolerance)


def require_keys(value, fields, label, errors):
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return {}
    for field in sorted(fields):
        if field not in value:
            errors.append(f"{label}.{field} is required")
    return value


def validate(data):
    errors = []
    missing = sorted(ROOT_FIELDS - set(data))
    if missing:
        errors.append(f"missing root fields: {', '.join(missing)}")
    if data.get("schema_version") != "3.0":
        errors.append("schema_version must be 3.0")
    if data.get("artifact_type") != "EDITING_PLAN":
        errors.append("artifact_type must be EDITING_PLAN")
    if data.get("stage_id") != "16":
        errors.append("stage_id must be 16")
    payload = data.get("payload")
    if not isinstance(payload, dict):
        return errors + ["payload must be an object"]
    profile = payload.get("target_profile")
    max_allowed = 15
    if not isinstance(profile, dict):
        errors.append("payload.target_profile must be an object")
    else:
        pname = profile.get("name")
        if pname in ("SEEDANCE_2_5", "SEEDANCE_2.5"):
            max_allowed = 30
        elif pname != "SEEDANCE_2":
            errors.append("payload.target_profile.name must be SEEDANCE_2 or SEEDANCE_2_5")
        maximum = profile.get("max_segment_seconds")
        if not isinstance(maximum, (int, float)) or maximum <= 0 or maximum > max_allowed:
            errors.append(f"payload.target_profile.max_segment_seconds must be > 0 and <= {max_allowed}")
        if profile.get("reference_mode") not in ("OMNI_REFERENCE", "FIRST_LAST_FRAME"):
            errors.append("payload.target_profile.reference_mode must be OMNI_REFERENCE or FIRST_LAST_FRAME")

    segments = payload.get("segments")
    if not isinstance(segments, list) or not segments:
        return errors + ["payload.segments must be a non-empty array"]
    seen = set()
    previous_exit = None
    dialogue_links = []
    dialogue_slices_by_segment = {}
    for index, raw in enumerate(segments):
        label = f"payload.segments[{index}]"
        segment = require_keys(raw, SEGMENT_FIELDS, label, errors)
        segment_id = segment.get("segment_id")
        if not isinstance(segment_id, str) or not segment_id:
            errors.append(f"{label}.segment_id is required")
        elif segment_id in seen:
            errors.append(f"duplicate segment_id: {segment_id}")
        seen.add(segment_id)
        duration = segment.get("duration")
        if not isinstance(duration, (int, float)) or duration <= 0 or duration > max_allowed:
            errors.append(f"{label}.duration must be > 0 and <= {max_allowed}")
        if not isinstance(segment.get("shot_ids"), list) or not segment.get("shot_ids"):
            errors.append(f"{label}.shot_ids must be a non-empty array")
        if not isinstance(segment.get("story_units"), list) or not segment.get("story_units"):
            errors.append(f"{label}.story_units must be a non-empty array")
        if not isinstance(segment.get("visual_action_units"), list):
            errors.append(f"{label}.visual_action_units must be an array")
        entry_type = segment.get("boundary_from_previous")
        if entry_type not in ENTRY_TYPES:
            errors.append(f"{label}.boundary_from_previous is invalid")
        if index == 0 and entry_type != "SCENE_ENTRY":
            errors.append(f"{label}.boundary_from_previous must be SCENE_ENTRY")
        if index > 0 and entry_type != previous_exit:
            errors.append(
                f"{label}.boundary_from_previous {entry_type} "
                f"does not match previous exit {previous_exit}"
            )

        boundary = require_keys(
            segment.get("boundary_to_next"), BOUNDARY_FIELDS,
            f"{label}.boundary_to_next", errors,
        )
        exit_type = boundary.get("type")
        if exit_type not in EXIT_TYPES:
            errors.append(f"{label}.boundary_to_next.type is invalid")
        checks = require_keys(
            boundary.get("safety_checks"), SAFETY_FIELDS,
            f"{label}.boundary_to_next.safety_checks", errors,
        )
        for field in SAFETY_FIELDS:
            if checks.get(field) is not True:
                errors.append(f"{label}.boundary_to_next.safety_checks.{field} must be true")
        if exit_type == "VISIBLE_CUT" and not boundary.get("director_cut_directive_id"):
            errors.append(f"{label} VISIBLE_CUT requires director_cut_directive_id")
        if exit_type != "VISIBLE_CUT" and boundary.get("director_cut_directive_id"):
            errors.append(f"{label} non-visible boundary cannot carry director_cut_directive_id")
        if exit_type == "HIDDEN_SEAM" and not boundary.get("hidden_seam_id"):
            errors.append(f"{label} HIDDEN_SEAM requires hidden_seam_id")

        selection = require_keys(
            segment.get("boundary_selection"), SELECTION_FIELDS,
            f"{label}.boundary_selection", errors,
        )
        selected_time = selection.get("selected_time")
        if isinstance(duration, (int, float)) and (
            not isinstance(selected_time, (int, float)) or not close(selected_time, duration)
        ):
            errors.append(f"{label}.boundary_selection.selected_time must equal duration")
        candidates = selection.get("approved_cut_candidates_before_deadline")
        if not isinstance(candidates, list):
            errors.append(
                f"{label}.boundary_selection.approved_cut_candidates_before_deadline must be an array"
            )
        alignment = selection.get("cut_alignment")
        if alignment not in ALIGNMENTS:
            errors.append(f"{label}.boundary_selection.cut_alignment is invalid")
        if exit_type == "VISIBLE_CUT" and alignment != "ALIGNED_AT_SEGMENT_END":
            errors.append(f"{label} VISIBLE_CUT must be ALIGNED_AT_SEGMENT_END")
        if candidates and exit_type != "VISIBLE_CUT" and not selection.get("cut_alignment_override_reason"):
            errors.append(
                f"{label} skips an approved cut without cut_alignment_override_reason"
            )

        handoff = require_keys(
            segment.get("continuity_handoff"), HANDOFF_FIELDS,
            f"{label}.continuity_handoff", errors,
        )
        if not handoff.get("anchor_description"):
            errors.append(f"{label}.continuity_handoff.anchor_description is required")
        if not isinstance(handoff.get("must_match"), list) or not handoff.get("must_match"):
            errors.append(f"{label}.continuity_handoff.must_match must be a non-empty array")
        if index > 0 and handoff.get("previous_approved_tail_ref_required") is not True:
            errors.append(
                f"{label}.continuity_handoff.previous_approved_tail_ref_required must be true"
            )
        expected_usage = (
            "STATE_REFERENCE_ONLY" if entry_type == "VISIBLE_CUT"
            else "EXACT_CONTINUATION" if index > 0 else "NOT_APPLICABLE"
        )
        if handoff.get("tail_usage") != expected_usage:
            errors.append(
                f"{label}.continuity_handoff.tail_usage must be {expected_usage}"
            )

        dialogues = segment.get("dialogue_slices")
        dialogue_slices_by_segment[segment_id] = dialogues if isinstance(dialogues, list) else []
        if not isinstance(dialogues, list):
            errors.append(f"{label}.dialogue_slices must be an array")
        else:
            for dialogue_index, raw_dialogue in enumerate(dialogues):
                dialogue_label = f"{label}.dialogue_slices[{dialogue_index}]"
                dialogue = require_keys(raw_dialogue, DIALOGUE_FIELDS, dialogue_label, errors)
                if not dialogue.get("exact_text"):
                    errors.append(f"{dialogue_label}.exact_text is required")
                start, end = dialogue.get("start"), dialogue.get("end")
                if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
                    errors.append(f"{dialogue_label}.start/end must be numeric")
                elif start < 0 or end <= start or (
                    isinstance(duration, (int, float)) and end > duration
                ):
                    errors.append(f"{dialogue_label}.start/end must fit inside segment")
                integrity = dialogue.get("integrity")
                if integrity not in DIALOGUE_INTEGRITY:
                    errors.append(f"{dialogue_label}.integrity is invalid")
                if integrity != "WHOLE" and not dialogue.get("split_anchor"):
                    errors.append(f"{dialogue_label}.split_anchor is required for split dialogue")
                if integrity in {"CLAUSE_HEAD", "CLAUSE_MIDDLE"} and not dialogue.get(
                    "continues_to_segment_id"
                ):
                    errors.append(
                        f"{dialogue_label}.continues_to_segment_id is required"
                    )
                elif integrity in {"CLAUSE_HEAD", "CLAUSE_MIDDLE"}:
                    dialogue_links.append((dialogue_label, dialogue))
        previous_exit = exit_type
    if previous_exit != "SCENE_END":
        errors.append("last segment must end with SCENE_END")
    for dialogue_label, dialogue in dialogue_links:
        target_id = dialogue.get("continues_to_segment_id")
        target_slices = dialogue_slices_by_segment.get(target_id)
        if target_slices is None:
            errors.append(f"{dialogue_label} continues to missing segment {target_id}")
            continue
        matches = [
            item for item in target_slices
            if isinstance(item, dict)
            and item.get("dialogue_id") == dialogue.get("dialogue_id")
            and item.get("speaker_id") == dialogue.get("speaker_id")
            and item.get("voice_id") == dialogue.get("voice_id")
            and item.get("integrity") in {"CLAUSE_MIDDLE", "CLAUSE_TAIL"}
        ]
        if not matches:
            errors.append(
                f"{dialogue_label} has no matching dialogue continuation in {target_id}"
            )
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plan")
    args = parser.parse_args()
    with Path(args.plan).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("PASS")


def self_test():
    """★P11 新增（2026-10-24）：本脚本此前完全游离在自测体系外。
    它是 Seedance 分段映射表的唯一校验器——它若悄悄放行，分段表就是一张没人核过的表。
    这里钉死四类负例：浮点容差、缺字段、非对象、空数据/版本号错。"""
    ok = True
    if not close(0.5, 0.5 + 1e-9) or close(0.5, 0.6):
        print("FAIL self-test: close 容差判定错误"); ok = False
    errs = []
    require_keys({"a": 1}, {"a", "b"}, "x", errs)
    if not any("x.b is required" in e for e in errs):
        print("FAIL self-test: require_keys 漏报缺字段", errs); ok = False
    errs = []
    require_keys([], {"a"}, "y", errs)
    if not any("must be an object" in e for e in errs):
        print("FAIL self-test: require_keys 未拦截非对象", errs); ok = False
    e1 = validate({})
    if not e1 or not any("missing root fields" in x for x in e1):
        print("FAIL self-test: validate({}) 未报根字段缺失", e1); ok = False
    e2 = validate({"schema_version": "2.0"})
    if not any("schema_version" in x for x in e2):
        print("FAIL self-test: schema_version 非 3.0 未报错", e2); ok = False
    e3 = validate({"schema_version": "3.0", "artifact_type": "EDITING_PLAN",
                   "stage_id": "16", "payload": []})
    if not any("payload must be an object" in x for x in e3):
        print("FAIL self-test: payload 非对象未报错", e3); ok = False
    e4 = validate({"schema_version": "3.0", "artifact_type": "EDITING_PLAN", "stage_id": "16",
                   "payload": {"target_profile": {"name": "SEEDANCE_2", "max_segment_seconds": 15,
                                                  "reference_mode": "OMNI_REFERENCE"},
                               "segments": []}})
    if not any("payload.segments" in x for x in e4):
        print("FAIL self-test: 空 segments 未报错", e4); ok = False
    print('[+] self-test PASSED' if ok else 'FAIL self-test')
    return ok


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    main()
