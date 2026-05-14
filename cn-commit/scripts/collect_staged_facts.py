#!/usr/bin/env python3
"""
Collect staged (cached) git facts for cn-commit.

This script prints JSON to stdout. It is intentionally deterministic and does
not attempt to "summarize" changes in natural language.

Usage:
  python collect_staged_facts.py
"""

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def _decode_bytes(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gbk"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _run_git(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    stdout = _decode_bytes(result.stdout).strip()
    stderr = _decode_bytes(result.stderr).strip()
    return result.returncode, stdout, stderr


def _parse_name_status(output: str) -> list[dict]:
    files: list[dict] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith(("R", "C")) and len(parts) >= 3:
            files.append({"status": status, "path": parts[2], "old_path": parts[1]})
        elif len(parts) >= 2:
            files.append({"status": status, "path": parts[1]})
        else:
            files.append({"status": status, "path": ""})
    return files


def _top_dir(path: str) -> str:
    p = path.replace("\\", "/").lstrip("./")
    if not p or "/" not in p:
        return "root"
    return p.split("/", 1)[0] or "root"


def _normalize_scope(value: str) -> str:
    normalized = value.strip().lower()
    return normalized or "root"


def _infer_scope(top_dirs: dict[str, int]) -> str:
    non_root_dirs = {name: count for name, count in top_dirs.items() if name != "root"}
    if not non_root_dirs:
        return "root"

    ranked = sorted(
        ((_normalize_scope(name), count) for name, count in non_root_dirs.items()),
        key=lambda item: (-item[1], item[0]),
    )
    if len(ranked) == 1:
        return ranked[0][0]

    first_name, first_count = ranked[0]
    second_name, second_count = ranked[1]
    if first_count == second_count and first_name != second_name:
        return "multi"
    return first_name


def main() -> int:
    code, _, _ = _run_git(["rev-parse", "--is-inside-work-tree"])
    if code != 0:
        print("[ERROR] Not inside a git repository.", file=sys.stderr)
        return 2

    code, _, _ = _run_git(["diff", "--cached", "--quiet"])
    if code == 0:
        print("[ERROR] No staged changes found. Use `git add` or `git add -p` first.", file=sys.stderr)
        return 3

    _, repo_root, _ = _run_git(["rev-parse", "--show-toplevel"])
    _, branch, _ = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    _, name_status, _ = _run_git(["diff", "--cached", "--name-status"])
    _, shortstat, _ = _run_git(["diff", "--cached", "--shortstat"])
    _, stat, _ = _run_git(["diff", "--cached", "--stat"])
    _, numstat, _ = _run_git(["diff", "--cached", "--numstat"])

    files = _parse_name_status(name_status)
    dirs = [_normalize_scope(_top_dir(f.get("path", ""))) for f in files if f.get("path")]
    top_dirs = dict(Counter(dirs))
    inferred_scope = _infer_scope(top_dirs)

    payload = {
        "repo_root": repo_root,
        "branch": branch,
        "staged": {
            "file_count": len(files),
            "files": files,
            "top_dirs": top_dirs,
            "inferred_scope": inferred_scope,
        },
        "stats": {
            "shortstat": shortstat,
            "stat": stat,
            "numstat": numstat,
        },
        "paths": {
            "skill_dir": str(Path(__file__).resolve().parent.parent),
        },
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
