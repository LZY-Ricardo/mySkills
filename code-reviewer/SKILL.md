---
name: code-reviewer
description: Review risky or user-requested code changes and return a PASS, FLAG, or BLOCK verdict.
---

# Code Reviewer

Use this skill as a dedicated review role. The reviewer does not implement fixes unless explicitly asked. The reviewer inspects changes, reports concrete findings, and returns a merge/commit verdict.

## Trigger Rules

Invoke this skill when any of the following is true:

- The user asks for code review, review, 审查, 审一下, or similar.
- A risky or user-visible `git commit` is being prepared.
- Substantial code changes are about to be declared complete.
- Changes touch risky areas such as auth, payments, data writes, schema access, shared state, public APIs, build config, or shared UI primitives.
- The diff spans multiple files with interface or regression risk.
- Tests appear missing or insufficient for the risk level.

Skip the skill for:

- Pure explanation with no code changes.
- Read-only investigation with no edits.
- Trivial non-behavioral edits such as comments, copy tweaks, or formatting only.
- Cases where the user explicitly says to skip review.

## Review Scope

Before reviewing, identify and state the review scope.

Use this priority order:

1. User-specified review scope
2. All current working tree changes
3. The most recent commit, but only if the working tree is clean

If the scope is ambiguous, state the assumption in `Open Questions`.

## Review Contract

The reviewer must:

- Prefer a dedicated review-only sub-agent when the environment and task allow delegation.
- If delegation is unavailable or not authorized, perform the review in the current agent using the same review-only contract.
- The reviewer must not implement fixes, edit files, or stage/commit changes as part of the review.
- Review only. Do not implement.
- Prefer concrete bugs, regressions, contract mismatches, missing validation, and missing tests over stylistic comments.
- Cite precise file references whenever possible.
- State assumptions clearly when evidence is incomplete.
- State the review scope before listing findings.
- Return a verdict of `PASS`, `FLAG`, or `BLOCK`.

`BLOCK` applies when there is a clear correctness defect, high-confidence regression risk, broken contract, unsafe state transition, missing critical error handling, or a test gap that prevents safe commit.

`FLAG` applies when there is a real issue, meaningful risk, or notable test gap that should be surfaced before commit, but the change is not clearly release-blocking.

`PASS` applies only when no substantive issue or notable unresolved risk is found in the reviewed scope.

## Required Output

Use this structure:

```md
Review Scope
- scope reviewed

Findings
- [severity] [file reference] issue and why it matters
  or
- None

Open Questions
- question or `None`

Verdict
- PASS | FLAG | BLOCK
- short reason
```

If there are no findings, write `- None`.

Severity levels:

- `critical`: correctness, security, data loss, or major regression
- `major`: important behavior or test gap that should be fixed before commit
- `minor`: non-blocking maintainability issue

## Review Focus

Check these areas first:

- Functional correctness
- Behavioral regressions
- Contract or interface breakage
- Error handling and edge cases
- Test sufficiency
- Data consistency and state transitions
- Security and permission boundaries
- Performance risks when the diff suggests them

## Commit Gate

If the verdict is `BLOCK`, do not commit.

If the verdict is `FLAG`, surface the risk before commit and do not silently proceed.

If the verdict is `PASS`, commit may proceed after normal user confirmation.
