# Context Compression Examples

Use these examples to improve trigger recognition and output consistency.

## Example 1: Long implementation thread

### Situation
- The user asked to add a draft-save flow for quotes.
- Several files were inspected.
- A controller, service, and SQL migration were updated.
- The conversation now contains repeated implementation details.

### Good compressed output

```markdown
## Compressed Context
- Goal: Add quote draft save and later submit flow.
- Current status: Backend draft-save path is implemented; final submit path still needs end-to-end verification.
- Decisions:
  - Store drafts separately from final submitted quotes.
  - Reuse existing quote validation where possible to reduce divergence.
  - Keep submit as an explicit action instead of auto-submitting on save.
- Constraints / assumptions:
  - Must remain compatible with current merchant order workflow.
  - Existing quote records and admin views should not break.
- Relevant files / areas:
  - `application/admin/controller/...`
  - `application/common/service/...`
  - `update_quote_draft_service.sql`
- Validation / evidence:
  - SQL migration prepared.
  - Controller/service paths reviewed and modified.
  - Full end-to-end manual verification still pending.
- Open questions / risks:
  - Needs verification whether draft status affects existing list filters.
  - Needs verification whether submit path double-validates unchanged fields.
- Next recommended step: Run draft save → edit draft → submit draft through one complete test flow.
```

### Why this is good
- Keeps durable decisions.
- Preserves the workflow status.
- Avoids replaying every edit step.

---

## Example 2: Debugging with noisy logs

### Situation
- The user reported an order sync failure.
- Terminal output included repeated stack traces.
- Only the latest error and current hypothesis matter now.

### Good compressed output

```markdown
## Compressed Context
- Goal: Fix merchant order sync failure.
- Current status: Failure reproduced during sync job execution.
- Decisions:
  - Focus on the latest reproducible error instead of older traces.
  - Delay schema refactor until root cause is confirmed.
- Constraints / assumptions:
  - Must not break existing scheduled sync jobs.
- Relevant files / areas:
  - `application/api/controller/...`
  - `application/common/model/...`
  - sync job script / cron entry
- Validation / evidence:
  - Latest relevant error: `SQLSTATE[42S22]: Column not found`.
  - Trigger condition: sync job writes merchant order extension fields.
  - Reproduced in current environment.
- Open questions / risks:
  - Needs verification whether the missing column was added in all target databases.
  - Risk of patching code when the real issue is partial migration rollout.
- Next recommended step: Verify schema presence in the active database before changing application logic.
```

### Bad compressed output

```markdown
The user had a sync issue. I checked many logs. There were lots of SQL errors and stack traces. I think the code may be wrong, but maybe the database is also wrong. We should keep debugging.
```

### Why the bad example fails
- Too vague.
- No exact failure retained.
- No next step that another agent can execute.

---

## Example 3: Multi-file code change

### Situation
- A feature touched backend controller, model, and SQL files.
- The user does not need line-by-line narration.

### Good compressed output

```markdown
## Compressed Context
- Goal: Support merchant address apply workflow.
- Current status: Main backend logic is wired; admin-side verification remains.
- Decisions:
  - Keep approval state in the existing merchant flow instead of introducing a separate review table.
  - Expose only the minimal fields required by current UI.
- Constraints / assumptions:
  - Must preserve compatibility with existing merchant records.
- Relevant files / areas:
  - `application/admin/controller/...`
  - `application/common/model/...`
  - `merchant_address_apply.sql`
- Validation / evidence:
  - Data structure and write path updated.
  - No final admin UI regression check yet.
- Open questions / risks:
  - Needs verification whether old records need backfill defaults.
- Next recommended step: Verify create, approve, reject flows in admin.
```

### Compression note
Do not enumerate every modified method unless a method name is critical to the next step.

---

## Example 4: Task switch / handoff

### Situation
- One subtask is mostly done.
- Another agent or future turn needs to continue without rereading the whole transcript.

### Good compressed output

```markdown
## Compressed Context
- Goal: Finish quote draft workflow and prepare for frontend integration.
- Current status: Backend draft-save logic is in place; API contract review and integration test are next.
- Decisions:
  - Drafts remain editable until explicit submit.
  - Submit reuses final validation path.
  - No automatic conversion from draft to final status on save.
- Constraints / assumptions:
  - Existing order quoting flow must remain unchanged for non-draft paths.
- Relevant files / areas:
  - `application/api/controller/...`
  - `application/common/service/...`
  - `update_quote_draft_service.sql`
- Validation / evidence:
  - Core code path updated.
  - SQL prepared.
  - Frontend integration not tested yet.
- Open questions / risks:
  - Needs verification whether frontend expects draft IDs or quote IDs.
- Next recommended step: Confirm API request/response shape before frontend docking.
```

### Why this is good
- Works as a continuation brief.
- Keeps just enough implementation detail.
- Makes the next action obvious.

---

## Example 5: Very high token pressure

### Situation
- The context is nearly full.
- Only a tiny continuation capsule is needed.

### Good capsule output

```markdown
## Context Capsule
- Goal: Fix order sync and complete draft quote workflow.
- Done: Reproduced sync failure; added backend draft-save path.
- Key decisions: Focus on latest reproducible error; keep draft submit explicit.
- Constraints: Do not break existing merchant/order flows.
- Blocker: Need schema verification for missing column and end-to-end draft submit test.
- Next step: Verify active DB schema, then run draft save → submit flow.
```

### Why this is good
- Extremely compact.
- Still continuation-ready.

---

## Example 6: Internal vs user-visible compression

### Internal working brief
Use when compressing for yourself before continuing work.

```markdown
- Goal: Add draft quote workflow.
- Status: save implemented, submit not fully verified.
- Decision: explicit submit only.
- Constraint: keep old quote flow stable.
- Evidence: SQL + controller/service updated.
- Next: run end-to-end verification.
```

### User-visible compressed context
Use when the user benefits from a recap.

```markdown
## Compressed Context
- Goal: Add draft quote workflow without breaking current quote flow.
- Current status: Draft save path is implemented; final submit path still needs complete verification.
- Decisions:
  - Drafts are stored separately from final submitted quotes.
  - Submit remains an explicit action.
- Constraints / assumptions:
  - Existing merchant/order quoting flow must stay compatible.
- Relevant files / areas:
  - backend quote controller/service
  - `update_quote_draft_service.sql`
- Validation / evidence:
  - Core backend path updated.
  - Full manual flow has not been fully verified yet.
- Open questions / risks:
  - Needs verification whether existing filters/status logic include drafts correctly.
- Next recommended step: Run one complete draft save/edit/submit test.
```

---

## Pattern reminders

### Prefer this
- Exact file paths when they matter
- Exact error strings when debugging
- Accepted decisions with rationale
- One clear next step

### Avoid this
- Repeating all prior discussion
- Full log dumps
- Diff narration that can be recovered from git
- Multiple competing next steps unless necessary
