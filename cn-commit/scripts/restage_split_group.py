#!/usr/bin/env python3
"""
Restage one suggested split-commit group from a collect_staged_facts plan file.

This script only changes the index. It does not touch working tree content.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _run_git(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _run_git_checked(args: list[str]) -> str:
    code, stdout, stderr = _run_git(args)
    if code != 0:
        raise RuntimeError(f"git command failed: {' '.join(args)} :: {stderr or stdout}")
    return stdout


def _chunked(items: list[str], size: int = 100) -> list[list[str]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def _head_exists() -> bool:
    code, _, _ = _run_git(["rev-parse", "--verify", "HEAD"])
    return code == 0


def _unstage_paths(paths: list[str]) -> None:
    if not paths:
        return

    if _head_exists():
        for chunk in _chunked(paths):
            _run_git_checked(["reset", "-q", "HEAD", "--", *chunk])
        return

    for chunk in _chunked(paths):
        _run_git_checked(["rm", "--cached", "-q", "-f", "--", *chunk])


def _stage_paths(paths: list[str]) -> None:
    if not paths:
        raise RuntimeError("selected group has no files to stage")
    for chunk in _chunked(paths):
        _run_git_checked(["add", "--", *chunk])


def _load_plan(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Restage one split-commit group from a plan file.")
    parser.add_argument("--plan-file", required=True, help="Path to collect_staged_facts JSON output")
    parser.add_argument("--group-key", required=True, help="Target suggested_groups[].group_key")
    args = parser.parse_args()

    plan_path = Path(args.plan_file)
    if not plan_path.exists():
        print(f"[ERROR] plan file not found: {plan_path}", file=sys.stderr)
        return 2

    plan = _load_plan(plan_path)
    analysis = plan.get("analysis", {})
    if not analysis.get("can_auto_split", False):
        blockers = analysis.get("split_blockers") or ["plan does not allow auto split"]
        print(f"[ERROR] auto split blocked: {'; '.join(blockers)}", file=sys.stderr)
        return 3

    suggested_groups = plan.get("suggested_groups") or []
    target_group = next((group for group in suggested_groups if group.get("group_key") == args.group_key), None)
    if target_group is None:
        print(f"[ERROR] group not found: {args.group_key}", file=sys.stderr)
        return 4

    staged_files = [file_info.get("path", "") for file_info in plan.get("staged", {}).get("files", []) if file_info.get("path")]
    target_files = target_group.get("files") or []
    unknown_files = sorted(set(target_files) - set(staged_files))
    if unknown_files:
        print(f"[ERROR] group contains files outside original staged set: {', '.join(unknown_files)}", file=sys.stderr)
        return 5

    _run_git_checked(["rev-parse", "--is-inside-work-tree"])
    _unstage_paths(staged_files)
    _stage_paths(target_files)

    print(f"[OK] restaged group `{args.group_key}` with {len(target_files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
