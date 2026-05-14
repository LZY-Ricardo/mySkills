# Repository Guidelines

## Instruction Priority
Follow direct user instructions first, then this file, then any external workflow, plugin, or skill system. If an external process conflicts with this repository guide, this file takes precedence for work done here.

## Behavioral Guidelines
Prioritize correctness, clarity, and minimal changes over speed.

1. Think before coding: state assumptions, surface tradeoffs, and ask when something is unclear.
2. Keep it simple: implement only what was requested; avoid speculative abstractions or extra configurability.
3. Make surgical changes: touch only task-related lines, match existing style, and avoid unrelated refactors.
4. Work toward verification: define success criteria first, reproduce bugs when practical, and verify behavior after changes.

For multi-step work, use a short plan with verification per step:

```text
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

## Project Structure & Module Organization
This repository stores personal reusable skills. Each skill lives in its own top-level directory, such as [`cn-commit`](/Users/zyb/workspace/person/mySkills/cn-commit). The only required file in a skill directory is `SKILL.md`, and the filename must always be uppercase. Optional directories include `scripts/`, `agents/`, `assets/`, `examples/`, and `references/`.

## Working With Skills
Treat each skill as a self-contained unit. Keep instructions, scripts, and examples together. Add optional folders only when they serve the skill directly. Example:

```text
my-skill/
  SKILL.md
  scripts/
  agents/
```

Use short lowercase kebab-case names, such as `cn-commit` or `requesting-code-review`.

## Build, Test, and Development Commands
There is no global build system for this repository. Work is usually file-based and script-driven.

- `rg --files .` — list all tracked skill files quickly.
- `python cn-commit/scripts/example.py` — run a local example script.
- `python cn-commit/scripts/validate_commit_msg.py --help` — inspect script usage before changing behavior.
- `git status` — verify which skill directories are being modified.

## Coding Style & Naming Conventions
Write documentation in concise Markdown with clear headings. Keep `SKILL.md` procedural and explicit about when the skill applies. For Python, follow PEP 8, use 4-space indentation, and prefer small single-purpose utilities. Name scripts by function, such as `collect_staged_facts.py`.

## Testing Guidelines
There is no centralized test suite. When adding or updating scripts, run them directly and verify output against a realistic example. If a skill includes validation logic, add or update a runnable example near that skill. Do not document workflows you have not exercised locally.

## Commit & Pull Request Guidelines
Git history is minimal, so use Conventional Commit style going forward, for example: `feat(cn-commit): add staged facts parser`. Keep commits scoped to one skill when practical. For pull requests, include the purpose, affected skill directories, verification commands, and sample output when behavior changes. For instruction-only edits, summarize the workflow change clearly.
