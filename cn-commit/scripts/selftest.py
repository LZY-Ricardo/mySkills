#!/usr/bin/env python3
"""
Minimal self-test for cn-commit scripts and documentation.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from validate_commit_msg import validate_message


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_MD = SCRIPT_DIR.parent / "SKILL.md"
COLLECT = SCRIPT_DIR / "collect_staged_facts.py"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_skill_doc_uses_repo_relative_commands() -> None:
    content = SKILL_MD.read_text(encoding="utf-8")
    assert_true("C:/Users/lenovo/.codex/skills/cn-commit/scripts" not in content, "SKILL.md still contains a hard-coded Windows path")


def test_validate_message_accepts_valid_commit() -> None:
    ok, reason = validate_message(
        "docs(root): 新增仓库级协作规范\n\n补充 AGENTS.md 说明工作流。"
    )
    assert_true(ok, f"expected valid commit message, got: {reason}")


def test_validate_message_rejects_missing_chinese_summary() -> None:
    ok, reason = validate_message("docs(root): add repo guide")
    assert_true(not ok, "expected validator to reject summary without Chinese")


def test_collect_staged_facts_infers_scope() -> None:
    with tempfile.TemporaryDirectory(prefix="cn-commit-selftest-") as temp_dir:
        repo = Path(temp_dir)
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.name", "Self Test"], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "selftest@example.com"], cwd=repo, check=True, capture_output=True, text=True)

        skill_dir = repo / "docs"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "README.md").write_text("# docs\n", encoding="utf-8")

        subprocess.run(["git", "add", "docs/README.md"], cwd=repo, check=True, capture_output=True, text=True)

        result = subprocess.run(
            [sys.executable, str(COLLECT)],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        assert_true(payload["staged"]["inferred_scope"] == "docs", f"unexpected inferred_scope: {payload['staged']['inferred_scope']}")
        assert_true(payload["staged"]["file_count"] == 1, f"unexpected file_count: {payload['staged']['file_count']}")


TESTS = [
    ("SKILL.md avoids environment-specific paths", test_skill_doc_uses_repo_relative_commands),
    ("validate_message accepts a compliant Chinese commit", test_validate_message_accepts_valid_commit),
    ("validate_message rejects summary without Chinese", test_validate_message_rejects_missing_chinese_summary),
    ("collect_staged_facts infers scope from staged files", test_collect_staged_facts_infers_scope),
]


def main() -> int:
    failed = False
    for name, fn in TESTS:
        try:
            fn()
            print(f"PASS {name}")
        except Exception as error:  # noqa: BLE001
            failed = True
            print(f"FAIL {name}", file=sys.stderr)
            print(str(error), file=sys.stderr)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
