---
name: context-compression
description: Compress long task context into a compact continuation brief when history or token pressure grows.
---

# Context Compression

## Goal
Create a short, loss-minimized working summary that lets the next turn or next agent continue immediately.

## Default behavior
- This skill is proactive, not opt-in.
- When a trigger below applies, compress state for yourself before continuing.
- Do not wait for the user to explicitly say “压缩上下文”.
- Show the compressed summary to the user only when it helps alignment, handoff, recovery, or the user asked for a recap.
- Prefer silent/internal compression over repeating long restatements in normal replies.

## Auto-trigger conditions
- The conversation has many substantial turns.
- Repo exploration, logs, diffs, or terminal output are getting large.
- Multiple files, fixes, or decisions have accumulated.
- You are about to switch subtasks, pause, hand off, or resume later.
- The system indicates long context, many rounds, or token pressure.
- You are about to ask a new question after a long implementation or debugging phase.

## Preserve these first
1. User goal and current success criteria
2. Decisions already made and why
3. Constraints, assumptions, and non-goals
4. Files, functions, commands, and outputs that matter
5. Validation status: tests, lints, errors, blockers
6. The single best next step

## Remove or collapse
- Repeated explanations
- Low-signal logs and stack traces
- Recoverable boilerplate from code
- Dead-end explorations that taught nothing
- Background facts unrelated to the current task

## Workflow
1. Reconstruct the current state in one sentence.
2. Extract only durable facts.
3. Merge duplicates and resolve wording drift.
4. Keep exact literals only when brittle:
   - file paths
   - schema, table, and field names
   - CLI commands and flags
   - API routes
   - exact error messages
5. Rewrite into short bullets grouped by status and decisions.
6. End with open questions and the single best next step.

## Output modes

### Internal working brief
Use by default when no user-visible recap is required.

### User-visible compressed context
Use when a summary helps the user re-align quickly, when handing off, or when resuming after interruption.

Use this template unless the user asks for another format:

```markdown
## Compressed Context
- Goal:
- Current status:
- Decisions:
- Constraints / assumptions:
- Relevant files / areas:
- Validation / evidence:
- Open questions / risks:
- Next recommended step:
```

## Compression rules
- Prefer bullets over paragraphs.
- One fact per bullet.
- Default target: 120-300 words.
- If the task is complex, go up to 500 words.
- If token pressure is severe, produce a capsule of 6-10 bullets.
- Do not invent missing details.
- Mark uncertainty explicitly with `Needs verification`.
- Mention unresolved blockers before nice-to-have details.
- When code matters, include file paths in backticks.
- Keep enough detail that another agent can continue without rereading the full transcript.

## By content type

### Conversation
Keep: requested outcome, decisions, constraints, unresolved asks.
Drop: politeness, repeated clarifications, stale alternatives.

### Code changes
Keep: file path, purpose of change, notable implementation choice, follow-up needed.
Drop: line-by-line narration that can be recovered from the diff.

### Logs and errors
Keep: latest relevant failure, trigger condition, current hypothesis, whether reproduced.
Drop: long repeated traces after the root issue is captured.

### Plans
Keep: current phase, completed steps, pending tasks, dependency order.
Drop: superseded plans.

## Fast capsule format
When a very small summary is needed, output:

```markdown
## Context Capsule
- Goal: ...
- Done: ...
- Key decisions: ...
- Constraints: ...
- Blocker: ...
- Next step: ...
```

## Quality check
Before finishing, ask:
- Could a new agent continue from this without rereading the full history?
- Did I preserve every decision that would be expensive to rediscover?
- Did I remove details that are easy to recover from the codebase or tools?

## Additional resources
- For concrete trigger and output examples, see [examples.md](examples.md)
