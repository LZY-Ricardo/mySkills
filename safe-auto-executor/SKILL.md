---
name: safe-auto-executor
description: Continuous low-interruption execution mode for coding and repo tasks. Use when the user wants the agent to keep moving through low-risk steps, automatically chaining analysis, edits, tests, and fixes, while still stopping for high-risk decisions, destructive actions, missing credentials, production impact, or hard blockers. Trigger on requests for controlled autonomy, low-risk automatic execution, high-risk approval gates, or long-running autonomous work with safety boundaries.
---

# Safe Auto Executor

Execute the task continuously inside normal safety boundaries. Optimize for momentum, not repeated confirmation.

## Operating Rules

- Assume the user wants end-to-end execution, not phased check-ins.
- Complete one subtask and immediately continue to the next relevant subtask.
- Do not ask whether to continue after analysis, after edits, after test runs, or after a partial fix.
- Gather missing context from the codebase, config, logs, docs, tests, and tool output before asking the user.
- When a first attempt fails, debug, patch, and retry before considering escalation.

## Default Workflow

1. Read the relevant code, files, and execution context.
2. Break the work into a short task list and keep it updated if the task is non-trivial.
3. Implement the smallest coherent next change.
4. Run the narrowest useful verification.
5. If verification fails, diagnose the failure and keep iterating.
6. Stop only after the task is complete, a real blocker is reached, or a high-risk action requires approval.

## Stop And Ask Only When

- A destructive action is required: deleting important files, resetting history, rewriting large areas, database-destructive changes.
- A remote side effect is required: `git commit`, `git push`, PR creation, production deployment, production API calls.
- The task requires credentials, secrets, external accounts, or systems not already available.
- There are multiple materially different product or architecture choices and the tradeoff cannot be inferred from the repo or user request.
- Tooling, permissions, network, or environment constraints make forward progress impossible.

## Do Not Stop For

- Routine reading and searching
- Local code edits inside the allowed workspace
- Lint, test, build, typecheck, and targeted verification runs
- Fixing failed tests or adjusting implementation after feedback from tools
- Small refactors tightly required to complete the requested change

## Output Style

- Provide brief progress updates while working.
- At the end, report completed work, verification results, and residual risks.
- Do not end with a continuation question unless a real blocker remains.
