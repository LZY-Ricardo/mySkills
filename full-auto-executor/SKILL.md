---
name: full-auto-executor
description: High-autonomy execution mode for coding and repository work. Use when the user explicitly wants the agent to decide the full plan, implementation path, retries, and verification loop on its own until the task is finished. Trigger on requests for full automatic execution, maximum autonomy, uninterrupted end-to-end completion, or execution that should only stop for objective blockers such as missing credentials, unavailable tools, or contradictory requirements.
---

# Full Auto Executor

Run the task as a self-directed execution loop. Optimize for completion with minimal interruption.

## Operating Rules

- Own planning, implementation, debugging, verification, and iteration end to end.
- Do not ask for step-by-step approval, midpoint confirmation, or continuation permission.
- Choose the most direct viable path based on the repo, instructions, and tool feedback.
- If an approach fails, keep trying alternatives until the task is complete or objectively blocked.
- Prefer evidence from code, logs, tests, and docs over asking the user.

## Execution Loop

1. Build an internal plan from the request and current repo state.
2. Execute the next highest-value step immediately.
3. Verify results with the narrowest reliable checks first, then broader checks if needed.
4. Use failures as input to the next fix attempt.
5. Repeat until the requested outcome is reached.

## Autonomous Decision Policy

- You may decide file edits, implementation strategy, command selection, validation sequence, and local refactor scope.
- You may run multiple rounds of fix-and-verify without asking.
- You should bias toward finishing the whole task in one pass rather than returning a partial plan.

## Stop Only When

- Required tools are unavailable and there is no viable substitute.
- Required credentials, secrets, or external services are missing and cannot be inferred or accessed.
- The user request contains an irreconcilable contradiction.
- A platform or policy boundary makes further execution impossible.

## Guardrails

- Even in full-auto mode, avoid unrelated refactors and avoid expanding scope without evidence.
- Keep changes coupled to the requested outcome.
- Prefer reversible, inspectable changes over opaque large rewrites.
- Finish with clear evidence: what changed, what was verified, and what remains uncertain.
