#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sd_core.py · 漫剧老李 V7.5.0-SLIM 套装唯一公共解析内核与跨阶段状态台账引擎
定位：
  1. 终结「多脚本各自写正则导致修A漏B」——统一提供 TIME_RE、SHOT_TAG_RE、模型时长与字数契约、
     镜行解析 parse_shots()、时间轴解析 parse_time_ranges()、镜行头提取 extract_shot_head()。
  2. 终结「上游神级卡片在下游被静默丢弃」——提供 project_state.json 结构化状态台账的初始化、
     读写与 P4 投喂稿跨阶段对账校验 verify_feed_against_state()。
用法：
  python3 scripts/sd_core.py --self-test
  python3 scripts/sd_core.py --init-state project_state.json
"""
import argparse
import json
import os
import re
import sys

# ---- 模型契约唯一常量（与 references/model-adapters.md §5 同源）----
MODEL_LIMITS = {"2.5": 30, "2.0": 15}
WORD_LIMITS = {"2.5": (3600, 4000), "2.0": (2900, 3000)}
SEVEN_SEGMENTS = (
    "【画幅风格】",
    "【场景资产】",
    "【核心人物】",
    "【站位声明】",
    "【时间轴分镜】",
    "【音效】",
    "【强制禁止项】",
)

# ---- 唯一权威时间码与镜号正则（兼容 MM:SS(.ff) / Xs-Ys / N-N秒 守卫版 + 全半角镜号）----
TIME_RE = re.compile(
    r"(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?\s*[-~～→]\s*(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?"
    r"|(\d+(?:\.\d+)?)\s*s\s*[-~～→]\s*(\d+(?:\.\d+)?)\s*s"
    r"|(?:\A|(?<=[\s\[【\]】]))\s*([0-9]|[1-5]\d)(?:\.\d+)?\s*[-~～→]\s*([0-9]|[1-5]\d)(?:\.\d+)?秒",
    re.I,
)
SHOT_TAG_RE = re.compile(r"[\[【]?\s*镜头\s*(\d+)\s*[\]】]?")


def frac_to_sec(frac):
    """秒的小数位 → 秒值（★2026-10-14 Agent 修复）。

    `5`→0.5 · `50`→0.5 · `05`→0.05 · `123`→0.123 —— **按位数换算，不写死 ÷100**。
    原实现统一写 `fr / 100.0`：小数位只有 1 位时把 `.5` 算成 0.05，
    使 `00:10.5` 变成 10.05s、`00:03.5` 变成 3.05s ——
    镜长区间最多偏 0.45s，且机检告警里印出的绝对时间点本身是错的。
    本包真实产物普遍使用半秒粒度，故此口径必须按位数判定。
    """
    if not frac:
        return 0.0
    return int(frac) / (10 ** len(frac))


def parse_time_ranges(text):
    """返回 [(start_s, end_s, line_no)]，兼容三形态时码。"""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        for m in TIME_RE.finditer(line):
            if m.group(1) is not None:
                s = int(m.group(1)) * 60 + int(m.group(2)) + frac_to_sec(m.group(3))
                e = int(m.group(4)) * 60 + int(m.group(5)) + frac_to_sec(m.group(6))
            elif m.group(7) is not None:
                s, e = float(m.group(7)), float(m.group(8))
            else:
                s, e = float(m.group(9)), float(m.group(10))
            out.append((round(s, 2), round(e, 2), i))
    return out


def parse_shots(body):
    """解析镜行，返回 [(镜号, 起秒, 止秒, 全行)]，兼容时码在前或镜号在前。"""
    shots = []
    auto_no = 0
    for line in body.splitlines():
        tm = TIME_RE.search(line)
        if not tm:
            continue
        if tm.group(1) is not None:
            s = int(tm.group(1)) * 60 + int(tm.group(2)) + frac_to_sec(tm.group(3))
            e = int(tm.group(4)) * 60 + int(tm.group(5)) + frac_to_sec(tm.group(6))
        elif tm.group(7) is not None:
            s, e = float(tm.group(7)), float(tm.group(8))
        else:
            s, e = float(tm.group(9)), float(tm.group(10))
        sm = SHOT_TAG_RE.search(line)
        auto_no += 1
        no = int(sm.group(1)) if sm else auto_no
        shots.append((no, round(s, 2), round(e, 2), line))
    return shots


def default_project_state():
    """生成标准 project_state.json 模板结构（覆盖 P0~P5 跨阶段核心锁定项）。"""
    return {
        "schema_version": "7.4.23",
        "project_name": "示例短剧项目",
        "locks": {
            "track": "1",
            "source": "1",
            "model": "2.5",
            "aspect": "16:9",
            "delivery": "3",
            "seam": "1",
            "style_card": "现代冷峻写实",
            "asset_mode": "M1",
            "combat_tier": "R1",
        },
        "receipt": {
            "active_plugins": ["sd-decision-engine", "sd-real-engine", "sd-storyboard-engine", "sd-feed-engine"],
            "read_refs": [
                "context-mapping.md",
                "emotion-anchor-table.md",
                "forbidden-zone-whitelist.md",
                "acting-direction.md",
                "blocking-direction.md",
                "kinetic-chain-11.md",
                "defense-evasion-rules.md",
                "impact-physics.md",
            ],
            "fingerprints": [
                "【情绪锚点：E04 压迫对峙（80% 侧45度中近景+缓推）】",
                "【动力链：蹬地→拧胯→转腰→送肩】",
                "【防守态：架臂格挡卸力+胸口衣料凹陷】",
            ],
        },
        "world_anchor": {
            "era_anchor": "2026年现代都市",
            "region": "东亚沿海城市",
            "tech_level": "现代科技",
            "forbidden_elements": ["马车", "长衫", "发髻", "煤油灯"],
            "required_elements": ["混凝土地面", "冷白日光灯管"],
        },
        "characters": {
            "林风": {
                "id": "CHR-01",
                "fig_no": 1,
                "age_anchor": "26~28岁男性",
                "body_anchor": "身高182cm，肩宽腰窄精悍体态",
                "look_3piece": "黑色战术短袖+深灰工装长裤+左眉骨一道浅疤",
                "voice_lock": "低沉微哑青年男声，语速偏慢，尾音冷硬",
                "business": "右手拇指反复攥紧战术手套魔术贴",
                "break_trigger": "然而当听到妹妹名字时，攥紧手指骤停、下颌咬肌绷紧",
                "address_map": {"陈枭": "陈会长"},
                "char_states": {},
            },
            "陈枭": {
                "id": "CHR-02",
                "fig_no": 2,
                "age_anchor": "45~50岁男性",
                "body_anchor": "身高178cm，宽厚微沉体态",
                "look_3piece": "深灰双排扣西装+暗红领带+金丝半框眼镜",
                "voice_lock": "醇厚低沉中年男声，语速平缓带压迫感",
                "business": "慢条斯理擦拭金丝眼镜片",
                "break_trigger": "然而当被逼退半步时，镜片后的眼睑骤然眯紧",
                "address_map": {"林风": "小疯子"},
                "char_states": {
                    "seg_1_detached": {
                        "item": "金丝半框眼镜",
                        "action": "摘下金丝半框眼镜捏在指间",
                        "consequence": "鼻梁两侧留有浅红压痕",
                    }
                },
            },
        },
        "scenes": {
            "地下拳馆走廊": {
                "id": "SCN-01",
                "fig_no": 3,
                "coords": "北侧尽头为铁艺双开门，南侧为水泥长廊出口，东西两侧为斑驳混凝土墙面与明装铁管",
                "set_states": {"default": "顶灯冷白硬光直射，地面有浅水洼反光"},
                "media_layer": "空气中悬浮微弱灰尘颗粒，受顶灯硬光照射清晰可见",
                "lighting": "顶灯冷白硬光自正上做主光 · 硬光质 · 明暗交界利落 · 暗部冷灰补色、禁纯黑（本段唯一光影基准，镜行只写增量/特写眼神光）",
            }
        },
        "props": {
            "旧怀表": {
                "id": "PRP-01",
                "fig_no": 4,
                "material_desc": "黄铜实心哑光表壳，表面有细密划痕，呈暗黄金属本色",
            }
        },
        "segments": [
            {
                "seg_id": "段1",
                "scene": "地下拳馆走廊",
                "segment_type": "战斗动作段",
                "emotion_anchor_id": "E04",
                "camera_combo_80": "中近景 · 侧45度",
                "forbidden_zone_unlock": "A类解锁：贴身格斗爆发瞬间允许正侧面切镜",
                "standing": [
                    "@林风（画面左 · 水泥走廊中段 · 朝右 · 立 · 身后是斑驳混凝土墙面）",
                    "@陈枭（画面右 · 铁门前 · 朝左 · 立 · 身后是铁艺双开门）",
                ],
                "storyboard_panels": [
                    "起势：林风蹬地沉腰蓄力",
                    "接触：拧胯转腰送肩直拳轰向陈枭",
                    "反应：陈枭架臂格挡卸力滑退半步",
                    "出口：两人保持对峙定格",
                ],
                "shots": [
                    {
                        "no": 1,
                        "start": 0,
                        "end": 4,
                        "spec": "中近景 · 85mm · 侧45度 · 极缓慢推",
                        "action": "画面主体：@林风 右手拇指攥紧战术手套魔术贴，听到名字瞬间手指骤停、下颌咬肌绷紧，目光死死钉在 @陈枭 脸上；@陈枭 摘下金丝半框眼镜捏在指间，鼻梁留有浅红压痕",
                        "sound": "[SFX: 皮质摩擦声与低沉电流嗡鸣]",
                        "dialogue": '【林风（压着怒意·低沉微哑·语速偏慢）：“陈会长，这表你认得吧？”】',
                    },
                    {
                        "no": 2,
                        "start": 4,
                        "end": 9,
                        "spec": "中景 · 50mm · 正侧 · 跟移",
                        "action": "@林风 沉腰屈膝，右脚猛然蹬地、拧胯转腰送肩轰出重拳；@陈枭 瞳孔骤缩，双臂交叉架臂格挡卸力，小臂西装布料受击凹陷，整个人向后滑退半步碾开地面浅水洼，命中瞬间画面顿住2帧后稳住重心",
                        "sound": "[SFX: 拳肉沉闷撞击声，鞋底擦地滑水声]",
                        "dialogue": "无",
                    },
                    {
                        "no": 3,
                        "start": 9,
                        "end": 14,
                        "spec": "全景 · 35mm · 略仰 · 缓慢拉远",
                        "action": "@林风 收拳沉肩稳住重心，@陈枭 垂臂立于铁门前呼吸微促，两人隔着水泥走廊对峙",
                        "sound": "[SFX: 粗重呼吸声与走廊回音]",
                        "dialogue": "无",
                    },
                ],
                "sfx_summary": "拳肉闷响、鞋底擦过湿水泥地声、粗重呼吸声，无BGM",
            }
        ],
    }


def verify_feed_against_state(feed_text, state):
    """拿 P4 投喂稿与 project_state.json 做跨阶段精确对账，返回 (issues, warns)。
    专治：P0B 情绪锚点机位、P1 称呼账本/世界锚、P3 角色表演档案声线锁与故事板面板链在 P4 被静默丢弃。
    """
    issues, warns = [], []
    locks = state.get("locks", {})
    # 1. 锁一致性对账（画幅 + 素材形态）
    exp_aspect = locks.get("aspect", "")
    if exp_aspect and exp_aspect not in feed_text:
        issues.append(f"STATE-1 画幅锁丢失：project_state.json 锁定画幅为 {exp_aspect}，但投喂稿未见该画幅")
    exp_mode = locks.get("asset_mode", "")
    if exp_mode and f"素材形态：{exp_mode}" not in feed_text and f"素材形态:{exp_mode}" not in feed_text:
        warns.append(f"STATE-2 素材形态声明偏离：台账锁定为 {exp_mode}，投喂稿顶部未见匹配的素材形态声明")

    # 2. 世界锚对账（年代锚 + 禁用元素）
    wa = state.get("world_anchor", {})
    era = wa.get("era_anchor", "")
    if era and era not in feed_text:
        warns.append(f"STATE-3 世界锚未继承：台账《世界锚卡》锁定年代「{era}」未原样落入投喂稿")
    for bad_elem in wa.get("forbidden_elements", []):
        if bad_elem and bad_elem in feed_text:
            issues.append(f"STATE-4 违反《世界锚卡》禁用元素：正文中出现了被禁时代元素「{bad_elem}」")

    # 3. 角色表演档案（Voice 声线锁 + 年龄锚 + CHAR_STATE 脱离态）对账
    for cname, cinfo in state.get("characters", {}).items():
        if cname not in feed_text:
            continue
        vlock = cinfo.get("voice_lock", "")
        if vlock and vlock not in feed_text:
            warns.append(f"STATE-5 角色「{cname}」的 P3《角色表演档案》Voice 声线锁（「{vlock}」）未落入投喂稿【核心人物】")
        age = cinfo.get("age_anchor", "")
        # M1/M2 全能参考有图模式下，【核心人物】严禁二次复述年龄与外貌，仅 M0 无图模式检查 P4 年龄锚
        if exp_mode == "M0" and age and age not in feed_text:
            warns.append(f"STATE-6 [M0无图模式] 角色「{cname}」的《人物锚卡》年龄锚（「{age}」）未落入投喂稿【核心人物】")
        for st_key, st_val in (cinfo.get("char_states") or {}).items():
            item = st_val.get("item", "")
            if item and item in feed_text and "覆盖角色参考图" not in feed_text:
                warns.append(f"STATE-7 角色「{cname}」存在 CHAR_STATE 脱离项「{item}」，但投喂稿缺「以本段提示词为准，覆盖角色参考图」替换声明")

    # 4. P0B 情绪锚点 80% 机位组合 & P3 故事板面板链对账
    for seg in state.get("segments", []):
        sid = seg.get("seg_id", "段")
        combo = seg.get("camera_combo_80", "")
        if combo:
            # 检查核心景别或角度词是否落在镜行中
            parts = [p.strip() for p in combo.split("·") if p.strip()]
            if parts and not all(p in feed_text for p in parts):
                warns.append(f"STATE-8 [{sid}] P0B《情绪锚点表》锁定的 80% 核心机位组合「{combo}」未在镜行中完整体现")
        panels = seg.get("storyboard_panels", [])
        if panels:
            shots = parse_shots(feed_text)
            if len(shots) == 0:
                issues.append(f"STATE-9 [{sid}] 未解析到任何有效时间轴镜行，无法承接 P3 故事板（共 {len(panels)} 格）")
    return issues, warns


def self_test():
    st = default_project_state()
    assert parse_time_ranges("0-3秒 [镜头1] 中景")[0][:2] == (0.0, 3.0)
    assert parse_time_ranges("[镜头1] 0-4秒，中景")[0][:2] == (0.0, 4.0)
    assert parse_time_ranges("00:00-00:05 [镜头1] 中景")[0][:2] == (0.0, 5.0)
    assert parse_time_ranges("0s-3.5s [镜头1] 中景")[0][:2] == (0.0, 3.5)
    # ★2026-10-14 Agent 修复回归锁：`MM:SS.s` 的 1 位小数必须按位数换算（`.5`=0.5s，非 0.05s）
    assert frac_to_sec("5") == 0.5 and frac_to_sec("50") == 0.5 and frac_to_sec("05") == 0.05
    assert frac_to_sec(None) == 0.0 and frac_to_sec("") == 0.0
    assert parse_time_ranges("00:10.5-00:12.5 [镜头4] 近景")[0][:2] == (10.5, 12.5), \
        "00:10.5 应为 10.5s（原缺陷为 10.05s）"
    assert parse_time_ranges("00:00-00:03.5 [镜头1] 近景")[0][:2] == (0.0, 3.5), \
        "00:03.5 应为 3.5s（原缺陷为 3.05s）"
    assert parse_time_ranges("00:00-00:15.75 [镜头1] 近景")[0][:2] == (0.0, 15.75), \
        "两位小数 .75 应为 0.75s"
    assert parse_shots("00:08-00:10.5 [镜头3] 特写")[0][1:3] == (8.0, 10.5)
    assert len(parse_shots("【镜头1】 0-3秒，中景\n【镜头2】 3-6秒，近景")) == 2
    iss, wrn = verify_feed_against_state("素材形态：M1\n16:9\n2026年现代都市\n00:00-00:04 [镜头1] 中近景 · 侧45度", st)
    assert not iss
    print("[+] sd_core self-test PASSED")
    return 0


def main():
    ap = argparse.ArgumentParser(description="漫剧老李 V7.5.0-SLIM 公共解析内核与状态台账工具")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--init-state", metavar="JSON_PATH", help="生成标准 project_state.json 模板")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(self_test())
    if args.init_state:
        with open(args.init_state, "w", encoding="utf-8") as f:
            json.dump(default_project_state(), f, ensure_ascii=False, indent=2)
        print(f"[+] 已生成项目状态台账模板：{args.init_state}")
        sys.exit(0)
    ap.print_help()


if __name__ == "__main__":
    main()
