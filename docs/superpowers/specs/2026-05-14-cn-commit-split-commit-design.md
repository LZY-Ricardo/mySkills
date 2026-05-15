# cn-commit Split Commit Design

## Goal

Enhance `cn-commit` so it can recognize staged changes that likely mix multiple concerns, ask the user whether to keep a single commit or split the work into multiple commits, and support an end-to-end split-commit workflow that preserves user control.

## Current State

`cn-commit` currently assumes the staged set is suitable for exactly one commit. It reads staged facts, infers a single `scope`, suggests one Chinese Conventional Commit message, validates the message, and commits after explicit confirmation.

That works for focused changes, but it breaks down when the staged set spans multiple directories, multiple file categories, or multiple concerns. In those cases, one commit produces weak history and forces the user to manually reorganize the staging area outside the skill.

## Requirements

1. Detect when staged changes appear mixed or broad rather than tightly focused.
2. Ask the user to choose one of three modes when mixed changes are detected:
   - single commit
   - split commit
   - stop and reorganize manually
3. Keep the current single-commit flow unchanged for focused staged changes.
4. In split mode, propose groups with clear file membership and suggested `type/scope/summary`.
5. Preserve explicit user confirmation before every `git commit`.
6. Avoid pushing, rebasing, or changing remote state.
7. Keep the skill portable across machines and repositories.

## Non-Goals

- Do not infer perfect semantic intent from diffs.
- Do not silently auto-commit multiple groups without user confirmation.
- Do not build a full interactive staging UI inside the skill.

## Detection Strategy

The skill should treat "mixed changes" as a heuristic, not as a hard truth. It should trigger the choice prompt when one or more of these signals appear:

- more than one non-root top-level directory is present and no single directory clearly dominates
- multiple file categories are present, such as docs, scripts, config, or tests
- file count is large enough that one concise summary is likely weak
- change statuses are heterogeneous in a way that suggests separate work units

The detector should produce structured reasons so the skill can explain why it is asking.

## Grouping Strategy

Split suggestions should be deterministic and easy to explain:

1. Group by top-level directory first.
2. If a top-level directory still mixes clearly different file categories, split by file category inside that directory.
3. Keep root files in their own `root` bucket unless they clearly belong with one dominant group.
4. Prefer 2-4 groups when possible; if the staged set explodes into too many tiny groups, recommend manual reorganization instead of forced automation.

Each group should include:

- file list
- top-level directory
- inferred file categories
- suggested Conventional Commit `type`
- suggested `scope`
- suggested Chinese summary seed

## Interaction Flow

### Focused staged changes

The existing flow remains:

1. Read staged facts.
2. Infer `scope`.
3. Suggest one commit message.
4. Validate the message.
5. Show diff stat and ask for confirmation.
6. Run one local `git commit`.

### Mixed staged changes

When the detector fires:

1. Show the staged facts and the reasons the changes look mixed.
2. Ask the user to choose:
   - single commit
   - split commit (recommended)
   - stop and reorganize manually
3. If the user chooses single commit, continue with the standard flow.
4. If the user chooses split commit:
   - generate group suggestions
   - show each group with files and suggested message metadata
   - ask for confirmation before applying staged regrouping
   - create one commit per confirmed group
   - re-stage remaining files between commits as needed
5. If the user chooses manual reorganization, stop without committing.

## Staging Safety

Split mode necessarily changes the staging area. The skill must treat that as a guarded action:

- show the proposed groups before changing the index
- ask for confirmation before regrouping staged files
- use explicit file-based staging operations
- leave unstaged working tree content untouched
- stop immediately if regrouping fails

## Script Changes

`collect_staged_facts.py` should grow into the main analysis source. It should report:

- top-level directory distribution
- file categories
- mixed-change reasons
- whether split prompting is recommended
- suggested groups for split mode

`selftest.py` should verify:

- mixed detection triggers on a synthetic broad staged set
- grouping stays deterministic
- focused changes do not trigger split prompting

`SKILL.md` should document:

- the new mixed-change prompt
- the three user choices
- the split-commit flow and confirmation gates

## Risks

- Grouping can be technically correct but semantically weak.
- Root-level files can be ambiguous.
- Over-eager split prompting can annoy users.

These are acceptable if the tool remains transparent, heuristic, and user-controlled.
