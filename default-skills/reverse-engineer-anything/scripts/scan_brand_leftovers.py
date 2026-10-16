#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan_brand_leftovers.py — REA qidicode 适配版：品牌残留字符串扫描器。

用法:
    python scan_brand_leftovers.py <pe文件> [-o out.json]
    python scan_brand_leftovers.py <目录>   [-o out.json]     # 批量（非递归，仅顶层文件）

纯 Python 3 标准库实现，Windows 兼容，无第三方依赖。

逻辑:
    读文件字节 -> 提取 ASCII 字符串(>=6 可打印字符) 与 UTF-16LE 字符串(>=6 字符)
    -> 对关键词清单做大小写不敏感匹配 -> 汇总每关键词命中次数 + 前 5 条命中上下文(截断 120 字符)。

免责声明: 品牌残留命中仅为字符串线索，不等于功能残留；须回源码确认后处置。
"""
import argparse
import hashlib
import json
import os
import re
import sys

# 关键词清单（品牌残留名单 + 常见变体）
# 注意：匹配为大小写不敏感（见 scan_strings）——勿加纯大小写重复项（如 "GROK" 与 "grok"），否则同义、只会输出重复计数。
KEYWORDS = [
    "grok.com",
    "x.ai",
    "xai",
    "grok",
    "supergrok",
    "cli-chat-proxy",
    "assets.grok",
    "Grok Build",
    "api.x.ai",
    "grok_bot",
    "grok-build",
]

DISCLAIMER = "品牌残留命中仅为字符串线索，不等于功能残留；须回源码确认后处置。扫描样本可能带出文件内嵌的密钥/token 字样；输出 JSON 只落临时目录，不得把敏感样本贴进对外报告或提交物"

MIN_LEN_ASCII = 6      # ASCII 字符串最短可打印字符数
MIN_LEN_UTF16 = 6      # UTF-16LE 字符串最短字符数
CONTEXT_MAXLEN = 120   # 单条命中上下文截断长度
SAMPLES_PER_KEYWORD = 5  # 每关键词保留的样本条数

# ASCII 可打印串: 0x20-0x7e 连续 >=MIN_LEN_ASCII
_ASCII_RE = re.compile(rb"[\x20-\x7e]{%d,}" % MIN_LEN_ASCII)
# UTF-16LE 串: (可打印ASCII + 0x00) 重复 >=MIN_LEN_UTF16
_UTF16LE_RE = re.compile(b"(?:[\x20-\x7e]\x00){%d,}" % MIN_LEN_UTF16)


def extract_strings(data):
    """返回 (ascii_strings, utf16le_strings)。"""
    ascii_strings = [m.group().decode("latin-1") for m in _ASCII_RE.finditer(data)]
    utf16_strings = [m.group().decode("utf-16-le") for m in _UTF16LE_RE.finditer(data)]
    return ascii_strings, utf16_strings


def scan_strings(strings):
    """对字符串列表做关键词匹配，返回 hits 字典。"""
    lowered = [(s, s.lower()) for s in strings]
    hits = {}
    for kw in KEYWORDS:
        kwl = kw.lower()
        count = 0
        samples = []
        seen = set()
        for orig, low in lowered:
            occurrences = low.count(kwl)
            if occurrences:
                count += occurrences
                if orig not in seen and len(samples) < SAMPLES_PER_KEYWORD:
                    seen.add(orig)
                    snippet = orig if len(orig) <= CONTEXT_MAXLEN else orig[:CONTEXT_MAXLEN]
                    samples.append(snippet)
        if count:
            hits[kw] = {"count": count, "samples": samples}
    return hits


def scan_file(path):
    """扫描单个文件，返回结果字典。"""
    with open(path, "rb") as fh:
        data = fh.read()
    sha256 = hashlib.sha256(data).hexdigest()
    ascii_strings, utf16_strings = extract_strings(data)
    strings = ascii_strings + utf16_strings
    hits = scan_strings(strings)
    return {
        "file": os.path.abspath(path),
        "sha256": sha256,
        "size": len(data),
        "strings_scanned": len(strings),
        "hits": hits,
        "disclaimer": DISCLAIMER,
    }


def build_report(target):
    """对文件或目录构建报告对象。"""
    if os.path.isdir(target):
        results = []
        for name in sorted(os.listdir(target)):
            p = os.path.join(target, name)
            if os.path.isfile(p):
                results.append(scan_file(p))
        return {
            "directory": os.path.abspath(target),
            "count": len(results),
            "results": results,
            "disclaimer": DISCLAIMER,
        }
    if os.path.isfile(target):
        return scan_file(target)
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="品牌残留字符串扫描器（grok/x.ai 等），仅作线索，须回源码确认。"
    )
    parser.add_argument("target", help="待扫描的 PE/二进制文件路径，或目录（批量）")
    parser.add_argument("-o", "--output", help="将 JSON 结果写入该文件（UTF-8）")
    args = parser.parse_args(argv)

    if not os.path.exists(args.target):
        sys.stderr.write("error: 路径不存在: %s\n" % args.target)
        return 2

    report = build_report(args.target)
    if report is None:
        sys.stderr.write("error: 既非文件也非目录: %s\n" % args.target)
        return 2

    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.write("\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
