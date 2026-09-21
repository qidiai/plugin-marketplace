#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""report_check.py — 政府资金申请报告质量门（gov-fund-application Step 5）

用法:
    python report_check.py <报告.md|目录>

目录模式取目录下第一个 .md。任一 error → exit 1。
硬规则来源：莒南县申报通知（资金闭合/比例）、发改委编制要点（八章/预备费/绩效四件套）。
零第三方依赖。
"""
import re
import sys
from pathlib import Path

CHAPTERS = [
    ("项目概况", r"项目概况"),
    ("项目背景与必要性", r"背景[与和]必要性"),
    ("项目符合性与建设条件", r"符合性[与和]建设条件|符合性"),
    ("建设方案", r"建设方案"),
    ("投资估算与资金筹措", r"投资估算|资金筹措"),
    ("项目实施进度", r"实施进度|建设工期"),
    ("绩效目标", r"绩效目标"),
    ("风险评估与防控", r"风险(评估|分析)"),
]

# 分领域补助比例上限（%，2025 莒南通知口径，属地当年度通知优先）
DOMAIN_CAPS = [
    ("环境基础设施", 60), ("水污染治理", 60), ("垃圾分类", 60),
    ("物流", 30), ("用能设备", 20), ("工业", 15), ("能源电力", 15),
]
DEFAULT_CAP = 80

EMPTY_PHRASES = ["进一步加强", "有效提升", "持续推进", "不断完善", "明显提升", "显著改善"]
VAGUE_SCOPE = ["等相关项目", "等类似项目", "等有关项目"]

NUM = r"([\d,，]+(?:\.\d+)?)"
WAN = rf"{NUM}\s*万?元"


def to_wan(num_str: str, unit_yi: bool = False) -> float:
    v = float(num_str.replace(",", "").replace("，", ""))
    return v * 10000 if unit_yi else v


def find_money(text: str, keyword: str):
    """找 keyword 之后(同行内)最近的金额(万元)。支持亿元。"""
    for line in text.splitlines():
        pos = line.find(keyword)
        if pos < 0:
            continue
        for m in re.finditer(r"([\d,，]+(?:\.\d+)?)\s*(亿|万)?元", line[pos:]):
            v = to_wan(m.group(1), m.group(2) == "亿")
            if v > 0:
                return v, line.strip()
    return None, None


# 渠道分组：同组只取第一个命中，避免关键词互含导致重复计数
CHANNEL_GROUPS = {
    "自有资金": ("企业自有", "自有资金", "自筹资金"),
    "银行贷款": ("银行贷款", "贷款"),
    "特别国债": ("特别国债", "国债资金"),
    "专项债": ("专项债",),
    "其他渠道": ("其他渠道", "其他资金"),
}


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    p = Path(argv[0])
    if p.is_dir():
        mds = sorted(p.glob("*.md"))
        if not mds:
            print("目录下无 .md 报告")
            return 2
        p = mds[0]
    text = p.read_text(encoding="utf-8-sig")
    errors, warns = [], []

    # 1) 八章必备
    for name, pat in CHAPTERS:
        if not re.search(pat, text):
            errors.append(f"缺少必备章节: {name}")

    # 2) 资金闭合
    total, tline = find_money(text, "总投资")
    channels = {}
    for gname, kws in CHANNEL_GROUPS.items():
        for kw in kws:
            v, l = find_money(text, kw)
            if v is not None:
                channels[gname] = v
                break
    if total is None:
        errors.append("未找到『总投资』金额（格式示例：总投资 25000 万元）")
    elif not channels:
        warns.append("未识别各渠道资金明细，请人工核对资金闭合（各渠道相加＝总投资）")
    else:
        s = sum(channels.values())
        if abs(s - total) > total * 0.005:
            names = " + ".join(f"{k}:{v:g}万" for k, v in channels.items())
            errors.append(f"资金不闭合: {names} = {s:g}万 ≠ 总投资 {total:g}万（{tline}）")

    # 3) 国债申请比例
    if total:
        bond, bline = find_money(text, "特别国债")
        if bond is None:
            bond, bline = find_money(text, "国债资金")
        if bond is not None:
            ratio = bond / total * 100
            domain, cap = None, DEFAULT_CAP
            for d, c in DOMAIN_CAPS:
                if d in text:
                    domain, cap = d, c
                    break
            if ratio > cap + 0.1:
                errors.append(f"申请国债 {bond:g}万 占总投资 {ratio:.1f}% 超上限 {cap}%"
                              f"（领域判定: {domain or '未识别，按默认80%'}）")
            else:
                print(f"  [ok] 国债占比 {ratio:.1f}% ≤ {cap}%")

    # 4) 绩效四件套（含碳减排）
    if re.search(r"绩效目标", text):
        if not re.search(r"碳减排|减碳|节能量|二氧化碳|标煤", text):
            errors.append("绩效目标缺碳减排效益（2026 年起必填：年节能量/减碳量）")

    # 5) 空洞表述
    for w in EMPTY_PHRASES:
        n = len(re.findall(w, text))
        if n:
            warns.append(f"空洞表述『{w}』出现 {n} 次——改为可量化表述或删除")

    # 6) 模糊建设内容
    for w in VAGUE_SCOPE:
        if w in text:
            errors.append(f"建设内容含模糊表述『{w}』——必须明确具体")

    # 7) 预备费
    m = re.search(r"预备费[^%\n]*?(\d+(?:\.\d+)?)\s*%", text)
    if m and float(m.group(1)) > 5:
        errors.append(f"预备费 {m.group(1)}% 超上限 5%")

    status = "PASS" if not errors else "FAIL"
    print(f"[{status}] {p.name}  ({len(errors)} error / {len(warns)} warning)")
    for e in errors:
        print(f"    ERROR: {e}")
    for w in warns:
        print(f"    warn : {w}")
    return 1 if errors else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    sys.exit(main(sys.argv[1:]))
