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
RESTAGE = SCRIPT_DIR / "restage_split_group.py"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_skill_doc_uses_repo_relative_commands() -> None:
    content = SKILL_MD.read_text(encoding="utf-8")
    assert_true("C:/Users/lenovo/.codex/skills/cn-commit/scripts" not in content, "SKILL.md still contains a hard-coded Windows path")


def test_skill_doc_mentions_split_commit_choices() -> None:
    content = SKILL_MD.read_text(encoding="utf-8")
    assert_true("拆分提交" in content, "expected split-commit flow in SKILL.md")
    assert_true("一次提交" in content, "expected single-commit option in SKILL.md")
    assert_true("手动整理" in content, "expected manual reorganization option in SKILL.md")


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
        assert_true(payload["analysis"]["split_recommended"] is False, "single-directory staged change should not recommend split")


def test_collect_staged_facts_flags_mixed_changes_and_groups() -> None:
    with tempfile.TemporaryDirectory(prefix="cn-commit-selftest-") as temp_dir:
        repo = Path(temp_dir)
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.name", "Self Test"], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "selftest@example.com"], cwd=repo, check=True, capture_output=True, text=True)

        (repo / "docs").mkdir(parents=True, exist_ok=True)
        (repo / "scripts").mkdir(parents=True, exist_ok=True)
        (repo / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
        (repo / "docs" / "guide.md").write_text("# guide\n", encoding="utf-8")
        (repo / "scripts" / "tool.py").write_text("print('ok')\n", encoding="utf-8")
        (repo / ".github" / "workflows" / "ci.yml").write_text("name: ci\n", encoding="utf-8")

        subprocess.run(
            ["git", "add", "docs/guide.md", "scripts/tool.py", ".github/workflows/ci.yml"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )

        result = subprocess.run(
            [sys.executable, str(COLLECT)],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        assert_true(payload["analysis"]["split_recommended"], "expected split recommendation for mixed staged changes")
        assert_true(payload["analysis"]["reasons"], "expected non-empty mixed-change reasons")
        assert_true(len(payload["suggested_groups"]) >= 2, "expected multiple suggested groups")
        group_names = [group["group_key"] for group in payload["suggested_groups"]]
        assert_true(group_names == sorted(group_names), f"expected deterministic group order, got: {group_names}")
        assert_true(payload["analysis"]["can_auto_split"], "expected full-file staged changes to allow auto split")


def test_collect_staged_facts_blocks_auto_split_for_partially_staged_file() -> None:
    with tempfile.TemporaryDirectory(prefix="cn-commit-selftest-") as temp_dir:
        repo = Path(temp_dir)
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.name", "Self Test"], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "selftest@example.com"], cwd=repo, check=True, capture_output=True, text=True)

        tracked = repo / "module.py"
        tracked.write_text("line1\nline2\nline3\n", encoding="utf-8")
        subprocess.run(["git", "add", "module.py"], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True, text=True)

        tracked.write_text("line1 staged\nline2 unstaged\nline3\n", encoding="utf-8")
        patch = """diff --git a/module.py b/module.py
index 83db48f..f00c965 100644
--- a/module.py
+++ b/module.py
@@ -1,3 +1,3 @@
-line1
+line1 staged
 line2
 line3
"""
        subprocess.run(
            ["git", "apply", "--cached", "--unidiff-zero", "-"],
            cwd=repo,
            input=patch,
            check=True,
            capture_output=True,
            text=True,
        )

        result = subprocess.run(
            [sys.executable, str(COLLECT)],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        assert_true(payload["analysis"]["split_recommended"] is False, "single file should not recommend split")
        assert_true(payload["analysis"]["can_auto_split"] is False, "partial staging should block auto split")
        assert_true(payload["analysis"]["partially_staged_files"] == ["module.py"], f"unexpected partially staged files: {payload['analysis']['partially_staged_files']}")


def test_restage_split_group_rebuilds_index_for_selected_group() -> None:
    with tempfile.TemporaryDirectory(prefix="cn-commit-selftest-") as temp_dir:
        repo = Path(temp_dir)
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.name", "Self Test"], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "selftest@example.com"], cwd=repo, check=True, capture_output=True, text=True)

        (repo / "docs").mkdir(parents=True, exist_ok=True)
        (repo / "scripts").mkdir(parents=True, exist_ok=True)
        (repo / "docs" / "guide.md").write_text("# guide\n", encoding="utf-8")
        (repo / "scripts" / "tool.py").write_text("print('ok')\n", encoding="utf-8")
        subprocess.run(["git", "add", "docs/guide.md", "scripts/tool.py"], cwd=repo, check=True, capture_output=True, text=True)

        plan_file = repo / "plan.json"
        collect = subprocess.run(
            [sys.executable, str(COLLECT)],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )
        plan_file.write_text(collect.stdout, encoding="utf-8")

        subprocess.run(
            [sys.executable, str(RESTAGE), "--plan-file", str(plan_file), "--group-key", "docs"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )

        staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )
        assert_true(staged.stdout.strip().splitlines() == ["docs/guide.md"], f"unexpected staged files after regroup: {staged.stdout!r}")


TESTS = [
    ("SKILL.md avoids environment-specific paths", test_skill_doc_uses_repo_relative_commands),
    ("SKILL.md documents split-commit choices", test_skill_doc_mentions_split_commit_choices),
    ("validate_message accepts a compliant Chinese commit", test_validate_message_accepts_valid_commit),
    ("validate_message rejects summary without Chinese", test_validate_message_rejects_missing_chinese_summary),
    ("collect_staged_facts infers scope from staged files", test_collect_staged_facts_infers_scope),
    ("collect_staged_facts flags mixed changes and suggests groups", test_collect_staged_facts_flags_mixed_changes_and_groups),
    ("collect_staged_facts blocks auto split for partially staged file", test_collect_staged_facts_blocks_auto_split_for_partially_staged_file),
    ("restage_split_group rebuilds index for one suggested group", test_restage_split_group_rebuilds_index_for_selected_group),
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
