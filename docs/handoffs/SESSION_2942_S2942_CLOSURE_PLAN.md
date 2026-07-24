# SESSION 2942 — S2942 Closure Plan (Ledger #38 dry_run + #41 promotion + #33/#34 reconciliation)

**Date:** 2026-07-24
**Branch:** main
**HEAD at open:** `8a15b06e7`
**Ship PR:** `<TBD>` (single commit at time of writing)
**Rigby PA pin:** `pa-07d6a1d43f6a4b42`
**Workers recycled:** twice mid-session (post-schema-edit + post-allowlist-expansion)

---

## READ THIS FIRST

S2942 opened with a pre-ratified closure plan (deliverable `8353676e-f037-4998-91e7-0269f9e1bbca`) that named **Ledger #34 + #33 + #38** as committed closure targets. Session-open fresh-context read of code + tests revealed that **#33 and #34 were already fully closed at S2931 (PR #3517 vicinity)** — the Rigby Tool Gap Ledger deliverable had never been status-flipped, so the plan drafter took the stale ledger at face value.

**Reconciliation:** Rigby T0 SIGN AGREE on Option A (plan targeted rows that already shipped) with tool-grounded verification (3 tool calls: `orm_inspect_tool.describe_model` on AgentExecution / `repo_tool.read_file` on agent_execution_bridge.py:315-335 / `deliverable_tool.detail` on the ledger). Chris "Yes" ratification on revised scope.

**Revised S2942 ship (executed):**

1. **Ledger #38 (committed)** — `dry_run=true` affordance added to `blog_tool.approve/reject/generate` + `feedback_tool.submit/update`. All 5 handler branches + 4 mutation paths (Deliverable + SelfBlog for blog_tool) return `would_*` envelope with `no_writes: true` and skip DB writes + Celery enqueues.
2. **Ledger #41 promotion (committed)** — gap-map classifier extended to parse `**Execution mode:** live|analyzed` + `**Mutation safety:** dry_run_supported|unsafe_no_dry_run` from validation-doc frontmatter. Missing/out-of-enum values normalize to `unknown` (no silent default per plan §2.1). Headline emits `per_execution_mode` + `per_mutation_safety` tallies.
3. **Validation-doc refresh** — `blog_tool_validation.md` + `feedback_tool_validation.md` updated with new frontmatter + §6 dry_run live-verify evidence from Rigby's PA-dispatch. Both docs now opt into Metric A (`live`) + Metric B (`dry_run_supported`).
4. **Canonical template update** — `_TEMPLATE_per_tool_validation.md` documents the new opt-in fields for future validation docs.
5. **Ledger hygiene** — Rigby Tool Gap Ledger deliverable (`5c84e75a-...`) rows #33, #34, #38 flipped to `mitigated` with S2931 commit refs + reconciliation banner. Meta-fix candidate (record-only): close-ceremony checklist for ledger status-flip after ledger-driven work.
6. **orm_inspect_tool allowlist expansion** — `UserFeedback` + `SelfBlog` added to `_MODEL_POLICIES` in `td_handlers_agents.py`. Unblocks Rigby's own verification loop; mirrors S2931 pattern.

**Acceptance gate:** SATISFIED. Rigby live-verified 3 mutation actions under dry_run in conversation `pa-07d6a1d43f6a4b42`:

- `feedback_tool.submit dry_run=true` → `total_matching` unchanged at 1 (no UserFeedback row created).
- `blog_tool.reject dry_run=true` on Deliverable `8353676e-...` (the plan itself — meta-verification) → status stayed `ready`, metadata unchanged.
- `blog_tool.generate dry_run=true` → NO `task_id` field (Celery not enqueued).

Plan §5 gate wording ("≥2 live-verified mutation validations under dry_run") exceeded by 1. Plan §7 four litmus points all pass.

---

## Files shipped

**Handler surface (dry_run branches):**
- **MODIFIED** `core/services/td_handlers_content.py` — 5 branches gained `dry_run` reading + `would_*` return path:
  - `_handle_feedback` `action=submit` (line 3600+)
  - `_handle_feedback` `action=update` (line 3676+)
  - `_handle_content_review` `action=publish` (line 640+)
  - `_handle_content_review` `action=archive` (line 656+)
  - `_handle_blog_query` `action=publish` (line 1400+)
  - `_handle_blog_query` `action=archive` (line 1450+)
  - `_handle_generate_blog` (line 1550+) — dry_run skips both `generate_blog_with_topic_task.delay()` and `generate_self_blog_deliberation_task.delay()`

**Schema surface:**
- **MODIFIED** `core/services/pa_tool_schemas.py` — added `dry_run` boolean param to `feedback_tool` (:645) + `blog_tool` (:4328); also declared `notes` param for feedback_tool.update + `type` param for blog_tool.

**Allowlist expansion:**
- **MODIFIED** `core/services/td_handlers_agents.py` — added `UserFeedback` + `SelfBlog` entries to `_MODEL_POLICIES` (:759-768) — completes verify-at-ORM loop for the new dry_run branches. Both non-sensitive with expensive TextFields (message/resolution_notes + full_text) blocked from `contains` lookups.

**Classifier substrate (Ledger #41 promotion):**
- **MODIFIED** `core/services/pa_tools_gap_map.py` — added `EXECUTION_MODES` + `MUTATION_SAFETY_VALUES` + `UNKNOWN_LABEL` constants; extended `index_validation_docs` to parse both frontmatter fields with case-insensitive normalization; extended `build_gap_map` to attach per-row `execution_mode` + `mutation_safety` + emit `per_execution_mode` + `per_mutation_safety` headline dicts + `per_tool_docs_with_execution_mode` / `_with_mutation_safety` count totals; extended `render_gap_map_markdown` with a "Two-metric scoreboard" section.

**Validation-doc refresh:**
- **MODIFIED** `docs/research/tools/validation/feedback_tool_validation.md` — new frontmatter (Execution mode: live + Mutation safety: dry_run_supported) + §6.4 S2942 dry_run live-verify evidence with tool_runs verbatim.
- **MODIFIED** `docs/research/tools/validation/blog_tool_validation.md` — same frontmatter + §6.9 evidence with all 3 mutation actions' dry_run tool_runs.
- **MODIFIED** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` — added the two new frontmatter fields to the canonical skeleton + author guidance block.
- **REGENERATED** `docs/audits/PA_TOOLS_GAP_MAP.md` via `build_pa_tool_audit --gap-only`.

**Ledger hygiene:**
- **UPDATED** Rigby Tool Gap Ledger deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (via ORM) — rows #33 + #34 status flipped to `mitigated` with commit refs; new reconciliation banner explains stale-status root cause; #38 mitigated stanza added to "Mitigated entries" section with live-verify evidence pointers.

**Tests:**
- **NEW** `core/tests/test_s2942_dry_run_mvp.py` (11 tests, all pass) — dry_run true/false branches × 5 mutation paths; Celery `.delay()` mocked + assert-not-called for generate branches.
- **NEW** `core/tests/test_s2942_ledger_41_scoreboard.py` (10 tests, all pass) — frontmatter indexing + summary emission + row-level per-tool population + unknown normalization for missing/out-of-enum values.

**Test slate verification:** all 68 tests pass (`test_s2942_dry_run_mvp` 11 + `test_s2942_ledger_41_scoreboard` 10 + `test_s2931_ledger_33_34_bundle` 8 + `test_pa_tools_gap_map_2795` 39). No regressions.

---

## Live-verify tool_runs (Rigby PA — acceptance gate evidence)

Full run captured in conversation `pa-07d6a1d43f6a4b42`. Seven tool calls in one turn:

1. `orm_inspect_tool.count_by model=UserFeedback field=status` → baseline `total_matching: 1`, `groups: [{value: "addressed", count: 1}]`.
2. `feedback_tool action=submit ... dry_run=true` → `{action: "submit", dry_run: true, would_action: "create", would_write: {model: "UserFeedback", ...}, no_writes: true}`.
3. `orm_inspect_tool.count_by model=UserFeedback field=status` (post-dry-run) → `total_matching: 1` (unchanged). **PASS #1**.
4. `feedback_tool action=submit ... dry_run=false` → real row created, `id: c3faf830-bf8c-4fc7-a2a7-fe3611a7e663`. Filter verified presence. Baseline mutation intact.
5. `orm_inspect_tool.filter model=Deliverable limit=1 order_by=-created_at` → picked the S2942 plan itself (`8353676e-...`), status `ready`.
6. `blog_tool action=reject id=8353676e-... dry_run=true` → `{action: "archive", dry_run: true, would_action: "archive", current_status: "ready", would_change_to: "archived", no_writes: true}`.
7. `orm_inspect_tool.filter model=Deliverable filter_kwargs={id: 8353676e-...} limit=1` → status still `ready`. **PASS #2**.
8. `blog_tool action=generate topic="S2942 gate probe" dry_run=true` → `{action: "generate_blog", dry_run: true, would_action: "dispatch_celery", would_task: "generate_blog_with_topic_task", no_writes: true}`. NO `task_id` field. **PASS #3**.

**Rigby zoom-out fold (PLAYBOOK-6.10.7, record-only):** envelope enhancement candidates for a future PR — `verify_hint` block (model + id + field expectations) and `would_write_count` for multi-row actions. Allowlist boundary (UserFeedback + SelfBlog only, no LLMCallLog) confirmed sensible. Log as candidates; require 2nd-trigger corroboration before promotion.

---

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

- Recycled clean twice mid-session (`make celery-recycle`) — first after schema edits, second after allowlist expansion.
- Live-verified all 3 mutation actions of blog_tool + feedback_tool.submit under dry_run via Rigby.
- Gap-map regeneration confirms Metric B moved from 0 → 2:
  ```
  per_execution_mode: {unknown: 159, live: 2}
  per_mutation_safety: {unknown: 159, dry_run_supported: 2}
  per_tool_docs_with_execution_mode: 2
  per_tool_docs_with_mutation_safety: 2
  ```

**Post-merge cascade:** run `make recycle-all` one more time after the S2942 ship PR merges (per `feedback_recycle_after_merge`).

---

## Governance

- No new [GR] rules ratified this session. D6 moratorium unchanged.
- Meta-fix candidate recorded record-only (1st trigger): close-ceremony checklist item for ledger status-flip. Watch for 2nd trigger before promoting.
- Rigby zoom-out fold recorded record-only: envelope `verify_hint` + `would_write_count`. Requires 2nd corroboration.

---

## Rigby Tool Gap Ledger — status this session

- **#33 (orm_inspect allowlist AgentExecution+Agent):** flipped `open` → `mitigated` (was already closed at S2931; ledger drift reconciled).
- **#34 (learning_bridges TESTING guard):** flipped `open` → `mitigated` (same — S2931 close-cascade skipped this).
- **#38 (dry_run affordance for blog_tool + feedback_tool):** flipped `open` → `mitigated` (this session's core ship).
- **New candidates (record-only):** envelope `verify_hint` + `would_write_count` (Rigby zoom-out fold); close-ceremony ledger-flip checklist (meta-fix).
- No new formal Ledger rows opened this session.

---

## Twin mirrors

Per Ledger #16 twin-mirror enforcement (in force since S2941 PR #3517):

- **Content mirror:** `<CONTENT_MIRROR_ID>` (Architecture & Research workspace, category `initiative_phase_doc`) — mirrors this handoff body.
- **Ratification envelope:** `<RATIFICATION_ENVELOPE_ID>` (Architecture & Research workspace, `deliverable_type=ratification_record`) — Chris D-verdict + Rigby T0 SIGN evidence.

`session_lifecycle close` at cascade-end must supply both IDs; the enforcement at `session_lifecycle.py:_handle_close` refuses close if either is missing (or requires explicit `--allow-no-mirror` opt-out).

---

## Fuller context

- **Ancestor plan:** deliverable `8353676e-f037-4998-91e7-0269f9e1bbca` — "S2942 Closure Plan — Ledger #34 + #33 + #38 (Landmines + Dry-Run Substrate)"
- **Prior handoff:** `docs/handoffs/SESSION_2941_LEDGER_16_TWIN_MIRROR.md`
- **Test files:**
  - `core/tests/test_s2942_dry_run_mvp.py`
  - `core/tests/test_s2942_ledger_41_scoreboard.py`
  - `core/tests/test_s2931_ledger_33_34_bundle.py` (still passing 8/8)
- **Rigby Tool Gap Ledger:** deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
- **PA conversation:** `pa-07d6a1d43f6a4b42` (S2942 pin, minted at S2941 close cascade)
