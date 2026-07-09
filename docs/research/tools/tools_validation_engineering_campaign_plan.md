# Rigby Tool Validation Engineering Campaign — Plan

**Session:** 2728 (campaign-plan authoring; execution pending Chris approval)
**Date:** 2026-07-08
**Status:** Campaign plan — awaiting Chris's review before any tool validation begins.
**Predecessors (context only; the constitutional-abstraction detour):**
- `tools_operational_contract_domain_definition.md` (Phase 0 — climbed into abstraction)
- `tools_operational_contract_architecture_pressure_test.md` (Phase 0 disproved)
- `tools_the_unanswered_constitutional_question.md` (question parked; not this campaign's target)

**Author:** Claude (Opus 4.7, 1M context)

**Scope constraints:** Plan only. No tool validation runs. No code patches. No test authoring. No doc changes. No Rigby SIGN routing. No child arcs. This document ends the session; execution begins next session after Chris approves this plan or amends it.

---

## 1. Campaign objective

Empirically verify — by direct execution, not by inference — that each high-priority Rigby tool behaves the way Rigby, Claude, and the schema all THINK it behaves. Where behavior diverges from expectation, decide whether the divergence is a defect, an under-documented default, or intentional-but-hidden discipline. Patch defects. Document the rest. Add regression tests where behavior is now verified. Re-run the tool. Record the final observed state.

The end-state for each tool: **Rigby can reason about the tool correctly because its actual runtime behavior, its schema, its documentation, and its tests all agree.**

The campaign is engineering QA. It is not constitutional research. It is not architecture. It is not theory.

---

## 2. Anti-scope

**Explicitly OUT of this campaign:**

- Answering the parked constitutional question (`tools_the_unanswered_constitutional_question.md`). Findings that reduce to that question get logged and parked; they do not stall a tool's validation.
- Proposing new Playbook chapters, MINOR amendments, or ADRs. If a finding is genuinely constitutional-weight, it is logged as a *Parked-Constitutional* entry and continues to be governed by Ch 5.2.1 reference to MEMORY.md until the parked question is answered.
- New architectural abstractions. No "Operational Contract" reframe. No "Capability Class" invention. Findings speak in the vocabulary of code, schema, dispatch, and test.
- Refactoring for cleanliness. Only defect-driven changes.
- Modifying tool interfaces to add features. This campaign hardens existing tools; it does not extend them.
- Rewriting docs beyond what verified behavior forces. If a doc claim is confirmed accurate, it stays as-is.
- Broad research audits. Every finding names a code path, a schema line, an observed runtime output, or a doc claim — nothing more abstract.
- Non-Rigby callers of these tools. If a tool is used by both Rigby and (e.g.) the frontend, the campaign scope is Rigby's use; other-caller impact gets logged but does not gate closure.

**Explicitly IN:** anything that closes the gap between what Rigby thinks a tool does and what the tool actually does.

---

## 3. Priority ordering

Priority is set by (a) MEMORY.md rule crystallization (evidence of past failure = highest priority), (b) frequency of Rigby's use, (c) cross-tool leverage (validating a shared substrate unblocks multiple downstream tools).

### 3.1 Batch A — MEMORY-crystallized failure targets (highest priority)

Tools that have already produced observed failures with existing MEMORY rules. Validation here has the highest defect-detection expected value.

1. **`deliverable_tool` (create / update / append / list / set_status / content_complete)** — 5+ MEMORY rules crystallized around it (`feedback_deliverable_tool_use_append_for_large_payloads`, `feedback_deliverable_status_via_content_complete`, `feedback_deliverable_create_defaults_to_completed`, `feedback_deliverable_workspace`, `feedback_llm_autofills_boolean_params_with_false` intersects). Multiple silent-fallback + silent-truncation + wrong-default behaviors documented.
2. **`session_tool` (create_fresh / retire / poll / status)** — 2 MEMORY rules (`feedback_session_tool_retire_works`, `feedback_pa_local_verify_ownership`) + the multi-session `pa_local.sh` pin ownership pattern. Recovery from pin poison depends on this tool.
3. **`search_docs` + `kb_tool` search** — MEMORY (`feedback_ratification_workflow_gotchas` — autofills `originating_session=0`) + `feedback_llm_autofills_boolean_params_with_false` (boolean autofill trap). Rigby uses this to reason about the repo; wrong results propagate everywhere.
4. **`claude_code_tool` (task dispatch)** — MEMORY (`feedback_procfile_makefile_queue_parity` — multi-session silent queue-forever failure). Queue-parity bug documented but not verified fixed post-S1249.
5. **`agent_introspection_tool` / `run_agent` meta-tool** — MEMORY (`feedback_auto_followup_false_suppresses_banner` — banner suppression). Rigby uses `run_agent` heavily; silent behavior on `auto_followup=False` was documented but coverage of related dispatch paths unverified.

### 3.2 Batch B — knowledge-substrate tools (Rigby's reasoning depends on these)

6. **RAG retrieval path** (`core/rag_integration.py` + `canonical_authority` weighting).
7. **`repo_tool`** (repository-fact retrieval).
8. **`kb_ingest`** (write side of the KB).
9. **Provenance / `canonical_authority` filtering** (`content/_canonical_authority_helpers.py`).
10. **Workspace retrieval** (`workspace_manager.get_active_workspace` + `execute_with_workspace`).

### 3.3 Batch C — runtime substrate tools (silent-behavior candidates)

11. **Context injection pipeline** (8 enrichment services + timeouts + relevance gating).
12. **Payload-size limits** (deliverable_tool ~6-7 kB silent fallback root cause).
13. **Retrieval limits + hidden filters** (default `limit`, `offset`, and boolean-filter parameters across tools).
14. **ORM helper defaults** (any tool that wraps ORM with defaulted filters — `has_initiative=False` autofill class).
15. **Retry behavior** (retry contract of tool_dispatcher + Celery `pa` queue retries).

### 3.4 Batch D — worker & environment discipline

16. **PA worker `PA_USE_FUNCTION_CALLING` env** (`feedback_pa_worker_function_calling_env`).
17. **Celery worker lifecycle** (`max_tasks_per_child`, PID cache, restart triggers) — MEMORY `feedback_local_celery_stall_playbook`.
18. **Worker cache behavior** (in-worker Python caches vs Redis vs DB).

### 3.5 Rationale for this ordering

Batch A validates known-defective tools first because expected defect yield is high and the fix cost is bounded. Batch B extends validation into the knowledge substrate Rigby's reasoning depends on. Batch C surfaces the silent-behavior class Chris's mission specifically flagged. Batch D closes the loop on worker/env discipline that determines whether tool fixes actually reach Rigby's runtime.

Batches run sequentially per `feedback_no_parallel_research_arcs` discipline. Within a batch, tools run one-at-a-time; a batch does not close until all its tools have a completed validation report.

---

## 4. Tool validation checklist (per-tool)

Applied to every tool. Missing answers are unknowns, not blanks.

**Understanding & schema:**
1. What is the tool intended to do? (1-2 sentences)
2. What does Rigby believe it can do? (from `pa_tool_schemas.py` description field + observed use in prior conversations)
3. What does the schema claim? (verbatim parameters + enum + type)
4. What does the handler actually do? (path traced through `tool_dispatcher.py` handler → downstream service → ORM/Redis/external)

**Defaults & hidden behavior:**
5. What defaults exist for every parameter? (schema default vs handler default — the two often differ)
6. What hidden filters exist? (ORM `.filter()` calls the schema does not surface — the `has_initiative=False` autofill class)
7. What limits exist? (default `limit`, hard cap, unbounded)
8. Can it silently truncate? (payload cap, result cap, LLM-input cap)
9. Can it silently filter? (default filters applied without appearing in output)
10. Can it silently fall back to another action? (the `deliverable_tool.update` → `action=list` case)

**Freshness, provenance, authority:**
11. Can it operate on stale cache/index data? (RAG stale corpus; in-worker Python cache; Redis TTL)
12. What freshness signal exists? (`updated_at`, cascade-run timestamp, none)
13. What provenance signal exists? (`canonical_authority`, `source`, none)
14. What authority/workspace assumptions exist? (WORKSPACE_AWARE gate, actor identity, KillSwitch)

**Runtime dependencies:**
15. What worker/env/queue dependencies exist? (`pa` queue, `PA_USE_FUNCTION_CALLING`, Procfile↔Makefile parity)

**Failure & recovery:**
16. What failure modes are recoverable inside a turn? (retry, fallback, degrade)
17. What failures require STOP-and-report? (fail-loud discipline)
18. What failures require operator action? (worker restart, cascade re-run, migration)

**Coverage & remediation:**
19. What tests currently cover this? (unit + smoke + integration; test file paths)
20. What code/docs/tests need to change? (concrete file:line list, no abstractions)

---

## 5. Evidence logging format

Every tool gets ONE validation report at:

```
docs/research/tools/validation/<tool_name>_validation.md
```

Structure:

```markdown
# <tool_name> — Validation Report

**Tool:** <schema name>
**Handler:** <path:line in tool_dispatcher.py>
**Session validated:** SNNNN
**HEAD at validation:** <sha>
**Reviewed by:** Claude (Opus 4.7, 1M context)
**Rigby cross-check:** yes / no (if yes, conversation_id + turn)

## 1. Intended purpose
## 2. Rigby's belief
## 3. Schema claim (verbatim)
## 4. Handler behavior (traced)
## 5. Defaults inventory
## 6. Hidden filters inventory
## 7. Limits inventory
## 8. Silent-truncation test
## 9. Silent-filter test
## 10. Silent-fallback test
## 11. Staleness test
## 12. Freshness signal
## 13. Provenance signal
## 14. Authority / workspace assumptions
## 15. Runtime dependencies
## 16. Recoverable failure modes
## 17. STOP-and-report failure modes
## 18. Operator-action failure modes
## 19. Existing test coverage
## 20. Change list (code / docs / tests)

## Findings
### F1 <short title>
- Class: DEFECT / UNDER-DOCUMENTED / VERIFIED-CORRECT / PARKED-CONSTITUTIONAL / RIGBY-MISUNDERSTANDING
- Evidence: <code file:line OR runtime output block OR Rigby quote>
- Severity: HIGH / MEDIUM / LOW
- Action: <one of: patch / test / doc / Rigby-note / park>

## Verdict
- Tool status at close: VERIFIED / DEFECT-PATCHED-VERIFIED / DEFECT-UNPATCHED-DEFERRED / BLOCKED
- Rigby-safe: yes / no / conditional (with condition)
- Regression tests added: <path list>
- Docs updated: <path list>
- Follow-ups filed: <MEMORY rule / deliverable / T-slot>
```

**All test runs are captured verbatim** — either as fenced code blocks in the report or (for long outputs) linked to a companion evidence file at `docs/research/tools/validation/evidence/<tool_name>_<test_case>.txt`.

**Rigby cross-checks** are recorded verbatim with conversation_id + turn number. Rigby's interpretation vs the runtime output is a first-class finding class.

---

## 6. Definition of defect

A tool exhibits a **DEFECT** when at least one of these is true:

- **D1.** Handler behavior differs from schema declaration (default value, type, enum membership, required-vs-optional).
- **D2.** Silent truncation, silent filter, or silent fallback occurs without an emitted warning, error, or metadata field surfacing the change.
- **D3.** Documented behavior (in `docs/topics/`, PLATFORM_WHAT_IT_IS, or the schema description) contradicts observed behavior at HEAD.
- **D4.** A MEMORY rule crystallizes a failure mode that is still reproducible at HEAD.
- **D5.** Rigby's schema-driven interpretation of the tool contradicts observed runtime behavior in a way she cannot detect from response payload.
- **D6.** Worker/env/queue dependency is required at runtime but is not declared in schema or documentation (the `PA_USE_FUNCTION_CALLING` class).
- **D7.** A default parameter value at the LLM interface is dangerous (e.g., boolean autofill=False acting as an active filter when the caller intended no filter).
- **D8.** A cross-workspace or cross-authority reach occurs without workspace_id / actor identity carriage that the LLM cannot see.
- **D9.** Test coverage does not exercise a documented behavior (regression risk).
- **D10.** A limit exists but is neither documented nor surfaced when hit (e.g., "list returned 200 rows but count is 340" without truncation flag).

**Not a defect (park instead):**

- Behavior surprising to Rigby but correct per schema + docs (add Rigby-note; do not patch).
- Behavior undocumented but harmless (add doc; do not patch code).
- Behavior that requires answering the parked constitutional question to decide (mark PARKED-CONSTITUTIONAL; continue).

---

## 7. Definition of verified behavior

A tool's behavior is **VERIFIED** when all of these hold:

- **V1.** All 20 checklist questions have concrete answers (not "unknown", not "assumed").
- **V2.** Every silent-behavior test (§4 questions 8-10) was executed and recorded — pass or fail.
- **V3.** Every defect surfaced by the checklist has either (a) been patched and re-tested, (b) been documented with a warning that Rigby will see at schema/description level, or (c) been logged as an accepted trade-off with an explicit `docs/AUDIT_FINDINGS.md` or MEMORY entry.
- **V4.** At least one regression test exists that would fail if the verified behavior regresses. If no automated test is feasible, a manual test procedure is documented at `docs/research/tools/validation/manual_procedures/<tool_name>.md`.
- **V5.** The tool's schema `description` field, its `docs/topics/personal-assistant.md` entry, and the validation report agree.
- **V6.** Rigby's cross-check (if applicable) produced behavior consistent with the validation report — or the disagreement is documented as a Rigby-misunderstanding finding with a schema/description remediation.

**Verified ≠ perfect.** A verified tool may still have known limitations. Verification means the limitations are documented and Rigby can reason about them.

---

## 8. Definition of Rigby-safe behavior

A tool is **RIGBY-SAFE** when Rigby's use of it, driven by the LLM function-calling loop with autofilled defaults, cannot produce silent wrong outcomes.

Formally, a tool is Rigby-safe when:

- **R1.** No parameter has a dangerous default (per §6 D7). Boolean parameters use truthy-only check semantics OR the schema `description` explicitly names False as "filter to false" rather than "no filter."
- **R2.** No handler silently substitutes an action for the requested one (per §6 D2). All fallbacks emit a `warning` or `substituted_action` field in the response.
- **R3.** No handler silently truncates without setting a `truncated: true` or `total_count > returned_count` field in the response.
- **R4.** All hidden filters are named in either the schema `description` or a `filters_applied` response field.
- **R5.** Workspace, actor identity, and authority requirements are declared in the schema or enforced at the handler with a typed error Rigby can reason about — not a silent empty result.
- **R6.** Freshness of retrieved data is surfaced (`retrieved_at`, `source_updated_at`, or an explicit staleness warning).
- **R7.** Provenance of retrieved data is surfaced (`canonical_authority`, `source_kind`, or equivalent).
- **R8.** Worker/env preconditions are checked at the handler and produce a typed error if not met (not a silent no-op).

**Not-Rigby-safe** is a defect class. It is not a rating downgrade — it is a specific patch target.

---

## 9. Initial target batch

**Batch A — five tools, in this order:**

1. **`deliverable_tool` full surface** (create / update / append / list / set_status / content_complete).
   Rationale: 5+ crystallized MEMORY rules; the ~6-7 kB payload silent-fallback root cause is unknown per S1176 F1; status-flip discipline is split between deliverable_tool and content_tool with silent behavior in both. Highest expected defect yield.

2. **`session_tool` full surface** (create_fresh / retire / poll / status / list).
   Rationale: recovery discipline depends on this; `feedback_session_tool_retire_works` corrected a prior stale belief but the full parameter surface has not been enumerated at HEAD.

3. **`search_docs` + `kb_tool.search`**.
   Rationale: Rigby's repo reasoning depends on this; `originating_session=0` autofill trap crystallized in S2727. Boolean autofill class needs full sweep.

4. **`claude_code_tool` dispatch**.
   Rationale: `feedback_procfile_makefile_queue_parity` documented multi-session silent-queue-forever failure; post-S1249 queue parity claim is unverified.

5. **`agent_introspection_tool` + `run_agent`** meta-tool.
   Rationale: Rigby uses `run_agent` heavily; `auto_followup=False` silent-banner-suppression documented but other dispatch-path silent behaviors are unverified.

Batch A completion criterion: five tools, each with a `<tool_name>_validation.md` at VERIFIED or DEFECT-PATCHED-VERIFIED status. Batch B does not open until Batch A closes.

**Batch A stop-and-return-to-Chris triggers** (see §11 stop conditions):
- Any tool surfaces >5 HIGH-severity defects that require architectural discussion.
- Any tool touches the parked constitutional question in a way that changes the campaign scope.
- Two consecutive tools reveal that their handler behavior is different enough from schema that the schema itself needs revision — this signals a schema-level campaign is prerequisite.

---

## 10. Proposed execution sequence

### 10.1 Per-tool sequence (from Chris's mission §Expected Method, ordered)

For each tool, in one session:

1. Read the schema (`pa_tool_schemas.py` — verbatim capture).
2. Read the handler (`tool_dispatcher.py` — trace to downstream).
3. Read related docs (`docs/topics/personal-assistant.md`, any tool-specific reference doc).
4. Author the validation report skeleton with checklist questions and blanks.
5. Execute normal case (a common Rigby-triggered invocation).
6. Execute empty/no-result case (query for something that returns nothing).
7. Execute ambiguous case (partial-match, near-limit).
8. Execute invalid-parameter case (wrong type, out-of-enum, missing required).
9. Execute default-parameter case (all optionals unset — what does the LLM's default-of-False do?).
10. Execute high-volume / limit case if safe (large `limit`, near payload cap).
11. Execute stale/freshness case where possible (query for something known-stale in the corpus).
12. Ask Rigby to use the tool independently for the same query when appropriate. Capture her conversation verbatim.
13. Compare Rigby's interpretation to actual runtime behavior. Log divergences.
14. Classify each finding (§6 defect classes) and each behavior (§7 verification criteria).
15. Patch ONLY concrete defects. Minimal diff. One commit per defect.
16. Add regression tests where possible. One test per defect. Placed in the tool's existing test module or a new `tests/tools/test_<tool>.py`.
17. Update docs only after behavior is verified. Schema description first (it is what Rigby sees); topic doc second; PLATFORM_INVENTORY only if a count changed.
18. Re-run every executed test case after the patch.
19. Record final observed behavior in the report.
20. Close the report — set Verdict block.

### 10.2 Batch sequence

Within Batch A: tools 1 → 2 → 3 → 4 → 5, one at a time, no parallel.

Between batches: Chris review gate. Campaign does not proceed from Batch A → B → C → D without Chris's explicit "continue."

### 10.3 Session shape

- Each tool takes 1 session (0.5-1.5 days).
- Each batch of 5 tools takes ~5-8 sessions.
- Full campaign (Batches A-D, 18 tools): 20-30 sessions.
- Sessions open with `context-kit orient` per standard discipline. No arc-open ceremony (this is a campaign, not a research arc).

### 10.4 Rigby-interaction discipline

- Rigby is invoked only for §10.1 step 12 (independent tool use). She is NOT SIGN-routed on validation reports (this is engineering, not research).
- Rigby's conversation is captured verbatim in the report.
- If Rigby's interpretation diverges from runtime, that IS a finding — usually a schema `description` remediation.
- If Rigby refuses / errors / stalls, apply `feedback_rigby_tool_verification` and `feedback_rigby_sign_worker_instability_recovery`. Log the recovery path.

---

## 11. Stop conditions

The campaign STOPS (or a tool's validation stops) when any of these fire:

- **S1.** A tool validation surfaces >5 HIGH-severity defects requiring architectural discussion. Log all, stop the tool, return to Chris.
- **S2.** A finding depends on the parked constitutional question (`tools_the_unanswered_constitutional_question.md`) for its resolution. Log as PARKED-CONSTITUTIONAL, continue to the next finding.
- **S3.** A patch requires a Playbook amendment, ADR, or new constitutional artifact. Log the finding, do NOT patch, return to Chris.
- **S4.** A defect fix would touch code owned by a closed research arc's ratified conclusion (Group 1900 authority, I-0100 correlation, I-0200 RAG corpus, etc.). Log the finding, do NOT patch, return to Chris.
- **S5.** A tool's handler behavior is so far from the schema that the schema itself needs redesign, not a simple `description` update. Log the finding, stop the tool, return to Chris.
- **S6.** Two consecutive tools in a batch surface the same root-cause pattern that is broader than either tool. Pause the batch, write a short cross-tool finding note, return to Chris to decide whether to promote to a targeted mini-arc or continue tool-by-tool.
- **S7.** A patch causes an unexpected regression in a test outside the tool's own test module. Roll back the patch, log the finding, return to Chris.
- **S8.** Runtime cost of validation exceeds session budget (e.g., stale-case tests require prod-corpus access or expensive re-embed). Log the constraint, defer that specific test, continue with the rest.
- **S9.** Chris explicitly says "stop" or "pause."
- **S10.** Rigby SIGN worker is unreachable AND the tool being validated is one Rigby depends on for her own operational discipline (`session_tool`, PA-side worker tools). Pause; the campaign cannot verify Rigby's use of a tool if Rigby is degraded.

Stop conditions are not campaign termination — they are checkpoints. Chris decides whether to unblock, defer, or replan.

---

## 12. Commit / PR / cascade expectations

### 12.1 Commit shape

- **One commit per concrete change.** No mixed commits.
- Prefix: `tools(validation): <tool_name> — <short description>`.
- Body: cites the validation report path (`docs/research/tools/validation/<tool>_validation.md`) and the finding ID (F1, F2, etc.).
- Co-Authored-By: `Claude Opus 4.7 (1M context) <noreply@anthropic.com>`.
- Chris-gated: no commits without explicit "commit it" per standard workflow.

### 12.2 PR shape

- **One PR per tool at close.** Bundles: (a) all patches, (b) all new tests, (c) the validation report, (d) docs updates driven by that tool.
- Title: `tools/validation: <tool_name> — VERIFIED (N patches, M tests)`.
- Body: verbatim §20 Change list from the validation report, plus a short "Findings summary" block naming each finding by class.
- Description references the validation report explicitly.
- No batch-wide PRs. If a cross-tool patch is needed (rare — §11 S6), it lands as a separate targeted PR outside the tool sequence.

### 12.3 Cascade expectations

After each tool's PR merges, per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`:

1. `python manage.py build_docs_index`.
2. `python manage.py build_rag_corpus` (if any doc changed).
3. `python manage.py sync_docs_index_to_documents` (if any doc changed).
4. `python manage.py embed_documents --all-unembedded` (state chunk count in PR body).
5. `python manage.py build_docs_provenance` (if any doc changed).
6. `python manage.py verify_doc_claims --only-drift` (report any drift caused by the docs update).

The cascade runs as part of the tool's PR body, not as a separate PR. If cascade fails, the tool's PR does not close.

### 12.4 MEMORY.md discipline

- If a validation surfaces a NEW failure mode not already crystallized in MEMORY, append the failure to MEMORY per standard feedback-rule pattern.
- If a validation VERIFIES that an existing MEMORY rule's failure mode is now fixed at HEAD, do NOT delete the rule — annotate it with `**Status:** RESOLVED at S<session> per validation report <path>`.
- If a validation reveals an existing MEMORY rule is now stale (fix landed but rule not updated), update the rule with a `**Verified stale:** <session> — <what changed>` line.
- The MEMORY.md index (`MEMORY.md`) stays under ~200 lines per its own warning; per-rule detail files carry the body.

### 12.5 Handoff & 00-START discipline

- Every session that closes a tool validation writes a handoff at `docs/handoffs/SESSION_<N>_<tool>_validation.md`.
- `00-START-NEXT-SESSION.md` is overwritten with the next tool's target + any active stop-condition state.
- CLAUDE.md is NOT touched during this campaign unless a validation surfaces a bootstrap-anchor drift.

### 12.6 What triggers a Chris-gate (mandatory review before proceeding)

- Any §11 stop condition fires.
- A tool closes at status DEFECT-UNPATCHED-DEFERRED.
- A tool closes with a PARKED-CONSTITUTIONAL finding that materially changes Rigby's use of that tool.
- End of each batch (A → B → C → D).
- Any commit that touches `core/services/tool_dispatcher.py` or `core/services/pa_tool_schemas.py` shape (structural changes, not description edits).

---

## 13. What this document does NOT do

- Does NOT begin validating any tool.
- Does NOT patch any code.
- Does NOT modify any schema.
- Does NOT modify any doc beyond creating this plan.
- Does NOT route to Rigby.
- Does NOT open an OPEN_ARCS row (this is a campaign, not a research arc).
- Does NOT mint an arc pin (session pins mint as needed per tool session; not a persistent arc pin).
- Does NOT create a directory beyond `docs/research/tools/validation/` (which is created lazily when the first tool report lands).

**Awaiting Chris's review. Execution begins next session after "approved" or "amend then approved."**
