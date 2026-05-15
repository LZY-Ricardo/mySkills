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


def _run_git_ok(args: list[str]) -> str:
    code, stdout, stderr = _run_git(args)
    if code != 0:
        raise RuntimeError(f"git command failed: {' '.join(args)} :: {stderr or stdout}")
    return stdout


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


def _infer_file_category(path: str) -> str:
    normalized = path.replace("\\", "/").lower()
    name = normalized.rsplit("/", 1)[-1]
    suffix = Path(name).suffix

    if normalized.startswith(".github/workflows/"):
        return "ci"
    if name in {"package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "requirements.txt", "pyproject.toml"}:
        return "build"
    if "test" in normalized or "spec" in normalized:
        return "test"
    if suffix in {".md", ".rst", ".txt"} or "readme" in name:
        return "docs"
    if suffix in {".yml", ".yaml", ".toml", ".ini", ".json"}:
        return "config"
    if suffix in {".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs", ".sh"}:
        return "script"
    return "other"


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


def _status_family(status: str) -> str:
    if not status:
        return "unknown"
    prefix = status[0]
    return {
        "A": "added",
        "M": "modified",
        "D": "deleted",
        "R": "renamed",
        "C": "copied",
        "U": "unmerged",
    }.get(prefix, "other")


def _suggest_commit_type(categories: set[str]) -> str:
    if categories == {"docs"}:
        return "docs"
    if categories == {"test"}:
        return "test"
    if categories == {"ci"}:
        return "ci"
    if categories == {"build"}:
        return "build"
    if categories <= {"config"}:
        return "chore"
    if categories & {"script", "other"}:
        return "feat"
    return "chore"


def _summarize_group(scope: str, categories: set[str], file_count: int) -> str:
    if categories == {"docs"}:
        return f"整理{scope}文档变更"
    if categories == {"ci"}:
        return f"调整{scope}持续集成配置"
    if categories == {"build"}:
        return f"更新{scope}构建依赖"
    if categories == {"config"}:
        return f"调整{scope}配置"
    if categories == {"test"}:
        return f"补充{scope}测试"
    if categories & {"script", "other"}:
        return f"完善{scope}相关改动"
    return f"整理{scope}的{file_count}处变更"


def _analyze_change_set(
    files: list[dict],
    top_dirs: dict[str, int],
    category_counts: dict[str, int],
    partially_staged_files: list[str],
) -> dict:
    reasons: list[str] = []
    split_blockers: list[str] = []
    non_root_dirs = {name: count for name, count in top_dirs.items() if name != "root"}
    ranked_dirs = sorted(non_root_dirs.items(), key=lambda item: (-item[1], item[0]))
    status_counts = Counter(_status_family(file.get("status", "")) for file in files)

    if len(non_root_dirs) >= 2:
        if len(ranked_dirs) == 1 or ranked_dirs[0][1] - ranked_dirs[1][1] <= 1:
            reasons.append("顶层目录分布分散，单一 scope 不明显")

    significant_categories = [name for name, count in category_counts.items() if count > 0]
    if len(significant_categories) >= 2:
        reasons.append("同时包含多种文件类别，可能是混合改动")

    if len(files) >= 5 and len(non_root_dirs) >= 2:
        reasons.append("变更文件较多且分布离散，单次提交摘要可能不够聚焦")

    if len(status_counts) >= 3:
        reasons.append("新增、修改、删除等状态混合，可能包含多个工作单元")

    if partially_staged_files:
        split_blockers.append("存在部分暂存文件，自动拆分会误带未暂存内容")

    return {
        "split_recommended": bool(reasons),
        "can_auto_split": not partially_staged_files,
        "reasons": reasons,
        "split_blockers": split_blockers,
        "partially_staged_files": sorted(partially_staged_files),
        "category_counts": dict(sorted(category_counts.items())),
        "status_counts": dict(sorted(status_counts.items())),
    }


def _build_group_suggestions(files: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = {}
    for file_info in files:
        path = file_info.get("path", "")
        top_dir = _normalize_scope(_top_dir(path))
        category = file_info.get("category") or _infer_file_category(path)
        group_key = top_dir if top_dir != "root" else f"root-{category}"
        groups.setdefault(group_key, []).append(file_info)

    suggestions: list[dict] = []
    for group_key in sorted(groups):
        group_files = sorted(groups[group_key], key=lambda item: item.get("path", ""))
        top_dirs = Counter(_normalize_scope(_top_dir(item.get("path", ""))) for item in group_files)
        categories = {item.get("category") or _infer_file_category(item.get("path", "")) for item in group_files}
        scope = _infer_scope(dict(top_dirs))
        commit_type = _suggest_commit_type(categories)
        suggestions.append(
            {
                "group_key": group_key,
                "scope": scope,
                "file_count": len(group_files),
                "files": [item.get("path", "") for item in group_files],
                "categories": sorted(categories),
                "type": commit_type,
                "summary_seed": _summarize_group(scope, categories, len(group_files)),
            }
        )
    return suggestions


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
    unstaged_name_only = _run_git_ok(["diff", "--name-only"])

    files = _parse_name_status(name_status)
    for file_info in files:
        file_info["top_dir"] = _normalize_scope(_top_dir(file_info.get("path", "")))
        file_info["category"] = _infer_file_category(file_info.get("path", ""))
    dirs = [_normalize_scope(_top_dir(f.get("path", ""))) for f in files if f.get("path")]
    top_dirs = dict(Counter(dirs))
    inferred_scope = _infer_scope(top_dirs)
    category_counts = Counter(file_info["category"] for file_info in files if file_info.get("path"))
    staged_paths = {file_info.get("path", "") for file_info in files if file_info.get("path")}
    unstaged_paths = {line.strip() for line in unstaged_name_only.splitlines() if line.strip()}
    partially_staged_files = sorted(staged_paths & unstaged_paths)
    analysis = _analyze_change_set(files, top_dirs, dict(category_counts), partially_staged_files)
    suggested_groups = _build_group_suggestions(files)

    payload = {
        "repo_root": repo_root,
        "branch": branch,
        "staged": {
            "file_count": len(files),
            "files": files,
            "top_dirs": top_dirs,
            "inferred_scope": inferred_scope,
        },
        "analysis": analysis,
        "suggested_groups": suggested_groups,
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
