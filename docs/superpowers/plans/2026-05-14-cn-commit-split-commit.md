# cn-commit Split Commit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `cn-commit` so mixed staged changes trigger a user choice between one commit, split commits, or stopping for manual reorganization.

**Architecture:** Keep `collect_staged_facts.py` as the structured analyzer, teach it to classify files and suggest groups, then update `SKILL.md` so the skill consumes that analysis during its conversational flow. Verification stays script-driven through `selftest.py`.

**Tech Stack:** Python, Git CLI, Markdown

---

### Task 1: Expand staged facts analysis

**Files:**
- Modify: `cn-commit/scripts/collect_staged_facts.py`
- Test: `cn-commit/scripts/selftest.py`

- [ ] **Step 1: Add a failing self-test for mixed staged detection**

```python
def test_collect_staged_facts_flags_mixed_changes() -> None:
    ...
    assert_true(payload["analysis"]["split_recommended"], "expected split recommendation")
    assert_true(payload["analysis"]["reasons"], "expected non-empty reasons")
```

- [ ] **Step 2: Run self-test to verify it fails**

Run: `python cn-commit/scripts/selftest.py`
Expected: FAIL because `analysis.split_recommended` and mixed reasons are not yet present.

- [ ] **Step 3: Implement file categorization and mixed-change analysis**

```python
def _infer_file_category(path: str) -> str:
    ...

def _analyze_change_set(files: list[dict], top_dirs: dict[str, int]) -> dict:
    ...
```

- [ ] **Step 4: Run self-test to verify the new detection passes**

Run: `python cn-commit/scripts/selftest.py`
Expected: PASS for the mixed-detection test.

- [ ] **Step 5: Commit**

```bash
git add cn-commit/scripts/collect_staged_facts.py cn-commit/scripts/selftest.py
git commit -m "feat(cn-commit): analyze mixed staged changes"
```

### Task 2: Add deterministic split grouping

**Files:**
- Modify: `cn-commit/scripts/collect_staged_facts.py`
- Test: `cn-commit/scripts/selftest.py`

- [ ] **Step 1: Add a failing self-test for split grouping**

```python
def test_collect_staged_facts_suggests_split_groups() -> None:
    ...
    assert_true(len(payload["suggested_groups"]) >= 2, "expected multiple suggested groups")
```

- [ ] **Step 2: Run self-test to verify it fails**

Run: `python cn-commit/scripts/selftest.py`
Expected: FAIL because `suggested_groups` does not exist or is incomplete.

- [ ] **Step 3: Implement deterministic grouping output**

```python
def _build_group_suggestions(files: list[dict]) -> list[dict]:
    ...
```

- [ ] **Step 4: Run self-test to verify grouping passes**

Run: `python cn-commit/scripts/selftest.py`
Expected: PASS for the grouping test with stable group names and files.

- [ ] **Step 5: Commit**

```bash
git add cn-commit/scripts/collect_staged_facts.py cn-commit/scripts/selftest.py
git commit -m "feat(cn-commit): suggest split commit groups"
```

### Task 3: Document the new conversational flow

**Files:**
- Modify: `cn-commit/SKILL.md`
- Modify: `cn-commit/scripts/example.py`

- [ ] **Step 1: Add a failing self-test for documentation expectations**

```python
def test_skill_doc_mentions_split_commit_choices() -> None:
    content = SKILL_MD.read_text(encoding="utf-8")
    assert_true("拆分提交" in content, "expected split-commit flow in SKILL.md")
```

- [ ] **Step 2: Run self-test to verify it fails**

Run: `python cn-commit/scripts/selftest.py`
Expected: FAIL because the current documentation does not describe the new choices.

- [ ] **Step 3: Update `SKILL.md` and helper entrypoint text**

```text
一次提交 / 拆分提交（推荐） / 暂不提交，手动整理
```

- [ ] **Step 4: Run self-test to verify the docs test passes**

Run: `python cn-commit/scripts/selftest.py`
Expected: PASS for the documentation checks.

- [ ] **Step 5: Commit**

```bash
git add cn-commit/SKILL.md cn-commit/scripts/example.py cn-commit/scripts/selftest.py
git commit -m "docs(cn-commit): document split commit workflow"
```

### Task 4: End-to-end verification

**Files:**
- Verify only: `cn-commit/scripts/collect_staged_facts.py`
- Verify only: `cn-commit/scripts/selftest.py`
- Verify only: `cn-commit/SKILL.md`

- [ ] **Step 1: Run the full self-test suite**

Run: `python cn-commit/scripts/selftest.py`
Expected: all checks PASS.

- [ ] **Step 2: Inspect staged analysis output against this repository**

Run: `python cn-commit/scripts/collect_staged_facts.py`
Expected: valid JSON output when staged changes exist, with `analysis` and `suggested_groups`.

- [ ] **Step 3: Review diff for scope and clarity**

Run: `git diff --stat`
Expected: only `cn-commit` files plus spec/plan docs changed for this feature.
