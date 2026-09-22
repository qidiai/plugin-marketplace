#!/usr/bin/env python3
"""novel-craft 章节检查脚本:字数/禁词/转述词/上帝视角自动检查。

用法:
    python check-chapter.py <章节文件.md>
    python check-chapter.py <目录/>   # 检查目录下所有 .md

返回非零退出码 = 有问题,并列出具体命中行。

禁词清单与 references/07-checklists.md 逐条同步:
- 禁词0      : 操/然后/接着/于是/说不清/莫名(成人向作品用"肏"替"操")
- 转述词0    : 她想/她觉得/她感到/她意识到
- 转述词0变体: 缩主语转述句"X想,"(任意人名/称呼后接"想"+标点,清单转述词0的漏网形式)
- 上帝视角0  : 她不知道的是/殊不知
- 作者抒情0  : 青砖上是她家的地
- 心理滤镜0  : 这意味着/原来如此/这说明

规则说明:
1. "操"排除专名"操偶"(若本书把"操偶"作为专名(如某玩法名)则放行——pattern 中 `(?!偶)` 即此意)。
2. 转述词以"后接标点"判定,不误伤"她想起/她想跑"等回忆/意愿动词。
3. "## 构师备注"元数据段整体跳过(备注自述性文字不计入正文,不检查字数与禁词)。
"""

import re
import sys
from pathlib import Path

# 禁词/转述词/上帝视角/作者抒情/心理滤镜 —— 与 07-checklists 同步
# (pattern, 清单出处)
PATTERNS = [
    (r"操(?!偶)", "禁词0(操)"),
    (r"然后", "禁词0(然后)"),
    (r"接着", "禁词0(接着)"),
    (r"于是", "禁词0(于是)"),
    (r"说不清", "禁词0(说不清)"),
    (r"莫名", "禁词0(莫名)"),
    (r"(?:她想|她觉得|她感到|她意识到)(?=[,，。;；:：])", "转述词0"),
    (
        r"(?:[他她你]|[爹娘哥姐爷奶兄弟妹儿女])想(?=[,，。;；:：])",
        "转述词0(缩主语变体)",
    ),
    (r"她不知道的是|殊不知", "上帝视角0"),
    (r"这意味着|原来如此|这说明", "心理滤镜0"),
    (r"青砖上是她家的地", "作者抒情0"),
]
COMPILED = [(re.compile(p), tag) for p, tag in PATTERNS]

# 构师备注段标记:从此行起(含)视为元数据,跳过
NOTE_MARKER = re.compile(r"^\s*##\s*构师备注", re.MULTILINE)


def check_file(path: Path) -> list[str]:
    issues = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="gbk")

    # 切掉"## 构师备注"元数据段,只检查正文
    body_text = NOTE_MARKER.split(text)[0]

    # 字数(仅正文:去标题行/空白)
    body = re.sub(r"^\s*#.*$", "", body_text, flags=re.MULTILINE)
    body = re.sub(r"\s", "", body)
    word_count = len(body)
    if word_count < 3500:
        issues.append(f"字数不足: {word_count} 字 (<3500)")

    # 禁词/转述词/上帝视角(仅正文行)
    for i, line in enumerate(body_text.split("\n"), 1):
        for pattern, tag in COMPILED:
            if pattern.search(line):
                issues.append(f"L{i}: 命中[{tag}] -> {line.strip()[:50]}")

    return issues


def main():
    target = Path(sys.argv[1])
    files = sorted(target.rglob("*.md")) if target.is_dir() else [target]

    total_issues = 0
    for f in files:
        issues = check_file(f)
        if issues:
            total_issues += len(issues)
            print(f"\n=== {f} ===")
            for issue in issues:
                print(f"  ⚠ {issue}")
        else:
            print(f"✓ {f} 通过")

    if total_issues:
        print(f"\n共 {total_issues} 个问题,需修复")
        sys.exit(1)
    print("\n全部通过")


if __name__ == "__main__":
    main()
