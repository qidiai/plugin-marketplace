#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""card_check.py — 角色卡质量门（drama-character-card Step 5）

用法:
    python card_check.py <目录|json文件...>

目录模式递归读 <目录>/cards/*.json；文件模式逐个校验。
任一 error → exit 1。warning 不阻断。
零第三方依赖（Python 3.9+ 标准库）。
"""
import json
import re
import sys
from pathlib import Path

TIERS = {"protagonist", "major", "supporting", "minor"}
MAX_NOT = 5
MAX_PROMPT_LEN = 1500
QUALITY_WORDS = [
    "美丽", "优雅", "气质", "漂亮", "英俊", "帅气", "好看",
    "beautiful", "elegant", "pretty", "gorgeous", "attractive", "charming",
]
CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u30ff\uac00-\ud7af]")
NOT_RE = re.compile(r"\bnot\b", re.IGNORECASE)


def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


class CardReport:
    def __init__(self, path: Path):
        self.path = path
        self.errors = []
        self.warnings = []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def check_card(path: Path) -> CardReport:
    rep = CardReport(path)
    try:
        card = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as e:  # noqa: BLE001
        rep.err(f"JSON 解析失败: {e}")
        return rep

    cid = card.get("id", "<无id>")

    # 1) 结构完整性
    for field in ("id", "name", "tier", "one_liner", "identity_block", "image_prompt"):
        if not card.get(field):
            rep.err(f"[{cid}] 缺必需字段: {field}")
    anchors = card.get("anchors")
    if not isinstance(anchors, list) or not anchors:
        rep.err(f"[{cid}] anchors 必须是非空数组（识别锚点）")
    voice = card.get("voice") or {}
    if not voice.get("timbre_prompt"):
        rep.err(f"[{cid}] 缺 voice.timbre_prompt（音色提示词）")
    persona = card.get("persona") or {}
    if not persona.get("contrast"):
        rep.warn(f"[{cid}] persona.contrast 缺失（反差点）")

    # 2) tier 枚举
    if card.get("tier") and card["tier"] not in TIERS:
        rep.err(f"[{cid}] tier 非法: {card['tier']!r}（允许 {sorted(TIERS)}）")

    image_prompt = card.get("image_prompt", "")
    identity_block = card.get("identity_block", "")
    timbre = voice.get("timbre_prompt", "")

    # 3) 语言分工：生成提示词禁止 CJK
    for label, text in (("image_prompt", image_prompt),
                        ("identity_block", identity_block),
                        ("voice.timbre_prompt", timbre)):
        if text and CJK_RE.search(text):
            rep.err(f"[{cid}] {label} 含 CJK 字符——锁面/图片/音色提示词必须纯英文")

    # 4) image_prompt 禁止出现中文名与别名
    names = [card.get("name", "")] + list(card.get("aliases") or [])
    for n in names:
        if n and n in image_prompt:
            rep.err(f"[{cid}] image_prompt 含中文称呼 {n!r}——请用角色码 {cid} 指代")

    # 5) NOT 词 ≤ MAX_NOT
    not_count = len(NOT_RE.findall(image_prompt))
    if not_count > MAX_NOT:
        rep.err(f"[{cid}] image_prompt 含 {not_count} 个 NOT（上限 {MAX_NOT}，过多降低生效率）")

    # 6) 长度上限
    if len(image_prompt) > MAX_PROMPT_LEN:
        rep.err(f"[{cid}] image_prompt {len(image_prompt)} 字符（上限 {MAX_PROMPT_LEN}）")

    # 7) 锁面逐字入提示词（忽略大小写、空白归一）
    locks = card.get("locks") or []
    if len(locks) > 5:
        rep.warn(f"[{cid}] 连续性锁 {len(locks)} 把（建议一集 ≤5，过多挤占提示词）")
    np = norm_ws(image_prompt)
    for i, lock in enumerate(locks, 1):
        face = (lock.get("face") or "").strip()
        if not face:
            rep.err(f"[{cid}] 第 {i} 把锁缺 face 字段")
            continue
        if CJK_RE.search(face):
            rep.err(f"[{cid}] 第 {i} 把锁 face 含 CJK——锁面必须英文")
        elif norm_ws(face) not in np:
            rep.err(f"[{cid}] 锁面未逐字出现在 image_prompt: {face!r}"
                    f"（提示词可在锁面周围加语法，但不得改写锁面内部）")

    # 8) 锚点质量词（警告级）
    for a in anchors or []:
        for w in QUALITY_WORDS:
            if w.lower() in str(a).lower():
                rep.warn(f"[{cid}] 锚点含空泛质量词 {w!r}: {a!r}（应为可见、可比较的事实）")
                break

    # 9) 主角/重要配角特写数量
    if card.get("tier") in ("protagonist", "major"):
        closeups = persona.get("five_closeups") or []
        if len(closeups) < 5:
            rep.warn(f"[{cid}] {card.get('tier')} 角色的 5 特写人格锚定只有 {len(closeups)} 条")

    return rep


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    targets = []
    for a in argv:
        p = Path(a)
        if p.is_dir():
            cards_dir = p / "cards"
            base = cards_dir if cards_dir.is_dir() else p
            found = sorted(base.glob("*.json"))
            if not found:
                print(f"未找到角色卡: {base}\\*.json")
                return 2
            targets.extend(found)
        elif p.is_file():
            targets.append(p)
        else:
            print(f"路径不存在: {p}")
            return 2

    total_e = total_w = 0
    for t in targets:
        rep = check_card(t)
        status = "PASS" if not rep.errors else "FAIL"
        print(f"[{status}] {t.name}  ({len(rep.errors)} error / {len(rep.warnings)} warning)")
        for e in rep.errors:
            print(f"    ERROR: {e}")
        for w in rep.warnings:
            print(f"    warn : {w}")
        total_e += len(rep.errors)
        total_w += len(rep.warnings)

    print(f"\n共 {len(targets)} 张卡: {total_e} error / {total_w} warning")
    return 1 if total_e else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    sys.exit(main(sys.argv[1:]))
