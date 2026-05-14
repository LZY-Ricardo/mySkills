#!/usr/bin/env python3
"""
Validate a commit message against cn-commit rules.

Rules enforced:
- First line format: type(scope): summary  OR  type: summary
- type must be lowercase English letters
- summary must contain at least 1 Chinese character
- summary length <= 30 characters (counted as Unicode code points)
- body is optional; if present, it must contain at least 1 Chinese character

Usage:
  python validate_commit_msg.py --file "<path/to/message.txt>"
"""

import argparse
import re
import sys
from pathlib import Path


HEADER_RE = re.compile(r"^([a-z]+)(\(([a-z0-9-]+)\))?:\s*(.+)$")
HAS_ZH_RE = re.compile(r"[\u4e00-\u9fff]")
ALLOWED_TYPES = {
    "feat",
    "fix",
    "docs",
    "refactor",
    "chore",
    "test",
    "perf",
    "build",
    "ci",
    "style",
    "revert",
}


def _read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gbk"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def validate_message(message: str) -> tuple[bool, str]:
    content = message.strip("\n")
    if not content.strip():
        return False, "commit message 为空"

    lines = content.splitlines()
    header = lines[0].strip()
    match = HEADER_RE.match(header)
    if not match:
        return (
            False,
            "标题格式不正确，应为 `type(scope): 摘要` 或 `type: 摘要`（type 小写英文）",
        )

    summary = match.group(4).strip()
    commit_type = match.group(1)
    if not summary:
        return False, "摘要不能为空"
    if commit_type not in ALLOWED_TYPES:
        allowed = "|".join(sorted(ALLOWED_TYPES))
        return False, f"type 不在允许集合中：{commit_type}（允许：{allowed}）"
    if len(summary) > 30:
        return False, f"摘要过长：{len(summary)} > 30"
    if not HAS_ZH_RE.search(summary):
        return False, "摘要必须包含中文"

    body = "\n".join(lines[1:]).strip()
    if body and not HAS_ZH_RE.search(body):
        return False, "正文存在但不包含中文（小改动可删除正文）"

    return True, "OK"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate cn-commit commit message.")
    parser.add_argument("--file", required=True, help="Path to commit message file")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"[ERROR] 文件不存在: {path}", file=sys.stderr)
        return 2

    message = _read_text(path)
    ok, reason = validate_message(message)
    if ok:
        print("[OK] commit message 校验通过")
        return 0

    print(f"[ERROR] commit message 校验失败: {reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
