# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2928 CLOSED SLICE 5 AT 14/14 + CONTENT-SHAPE FAIL FOLD PROMOTED (2/2 → RATIFIED). **S2929 OPENS WITH RE-SCOPE DECISION** — sweep is DONE for the 5-slice `td_handlers_*` cadence; remaining 15 untested tools are scattered across 8 files. D6 MORATORIUM STILL IN FORCE.

**Refreshed 2026-07-24 (S2928 close).** Batch 4 (FINAL) shipped as fork A doc-only close per Chris D-verdict at T0 SIGN. PR #3491 landed both remaining Slice 5 tools (`content_writer_agent` + `image_editing_agent`) as validated_full + Slice 5 CLOSE artifact codifying the agent-forwarding authoring pattern. Post-merge live-dispatch confirmed the **content-shape FAIL 2nd-instance** on `marketing_strategy_agent` (data.keys() = ['query'] only; false-success message claiming "3 data sources" but zero structured content). 1st instance was S2926 `CompetitorAnalysisAgent` — both share `BaseBusinessResearchAgent` base class. **Fold PROMOTED (2/2 → RATIFIED); Fold is class-scoped to BaseBusinessResearchAgent subclasses.**

**PRs shipped this session:**
- u-d-b PR [#3491](https://github.com/clwest/donkey-betz-platform/pull/3491) — Slice 5 batch 4 FINAL (validated_full + Slice 5 CLOSE artifact), merged at `63e006b11`.
- u-d-b PR `<TBD>` — S2928 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Tools shipped this session (2 — Slice 5 batch 4 FINAL; CLOSES Slice 5 at 14/14):**
- `content_writer_agent` → ContentWriterAgent (register at `tool_dispatcher.py:333`; mapping row `td_handlers_agents.py:115`). **Batch 4 completion-verify representative** (Rigby T0 SIGN Q2 verdict — highest-signal content-shape FAIL 2nd-instance surface). Completion PASSED with rich content + auto-Deliverable. Noted doc-vs-reality extraction-path drift: `td_handlers_agents.py:170-171` says `metadata.content.full_text`; actual is `data.content.full_text`. Informational (not a FAIL); Slice 5-hardening candidate.
- `image_editing_agent` → ImageEditingAgent (register at `tool_dispatcher.py:313`; mapping row `td_handlers_agents.py:88`). Receipt-verify only. **Last media-family tool in Slice 5.** Post-merge observation: tool-error branch (fake image_id) short-circuits before AgentExecution row is persisted — documented UX gap for Slice 5-hardening.

All 2 dispatch through shared handler `_handle_agent_tool` at `tool_dispatcher.py:1196` (same as batches 1+2+3). Async receipt shape: `{task_id, mode: 'async', agent, auto_followup, follow_up_will_fire, message}`. Queue: `long_running`.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3491 recycled clean at `sha=63e006b11`: 5 fresh workers + beat, zero surviving old PIDs.
- Rigby dispatch **3/3 receipt PASS** (task_ids `b3572962` content_writer / `0805d152` image_editing / `d5a9138c` marketing_strategy — all with correct `agent` mapping).
- DISPATCH 4 (S2927 workflow_orchestration_agent ORM tree enumeration) blocked by Rigby tool-gap: `orm_inspect_tool` allowlist omits AgentExecution + AgentResult. **Rigby surfaced honestly + logged to Ledger deliverable 5c84e75a-... (881 chars appended).** Workaround: `execution_history_tool.detail` for parent shape (worked); child enumeration blocked. Parent AE `20ad3024-...` shows `data.step_results: []` + `data.project_created: null` — distinct "work-not-done vs schema-preserved" class, 1st documented instance (NOT content-shape FAIL class; NOT a Fold trigger yet).

**§5a end-to-end classification (batch 4):** `content_writer_agent` = `external` amplified via LLM egress + auto-Deliverable INSERT with post_save cascade (deliverable_status + deliverable_mirror + document_processing signals); `image_editing_agent` = `external` amplified via Cloudinary media provider egress (external mutation surface, not tracked in local DB unless persisted).

**Rigby tool-gap Ledger append (S2928):** `orm_inspect_tool` allowlist expansion needed for AgentExecution + AgentResult. Priority MEDIUM. Substrate fix defers to engineering slate.

**Sweep progress (post-S2928, gap-map regen at close):**
- **Slice 1 (`td_handlers_ops`):** unchanged.
- **Slice 2 (`td_handlers_agents`):** CLOSED at S2912.
- **Slice 3 (`td_handlers_core`):** CLOSED at S2917.
- **Slice 4 (`td_handlers_gateway`):** CLOSED at S2924 (17/17).
- **Slice 5 (`tool_dispatcher`, 14 tools): CLOSED at S2928 (14/14).**
- Total corpus untested: **15** post-S2928 (from 17 pre-S2928).
- Gap map: **83 full · 11 partial · 7 unknown · 15 untested** (verified via `python manage.py build_pa_tool_audit --gap-only`).

**Remaining 15 untested tools scattered across 8 handler files (no clean "one file = one slice" mapping possible):**
- `td_handlers_content.py` — 6 tools (`blog_tool`, `execution_history_tool`, `feedback_tool`, `learning_patterns_tool`, `recent_activity_tool`, `surgical_moves_status_tool`) — largest remaining cluster
- `td_handlers_employee.py` — 2 tools (`employee_tool`, `mission_verdict`)
- `td_handlers_codejobs.py` — 1 tool (`code_job_tool`)
- `td_handlers_newsletter.py` — 1 tool (`newsletter_tool`)
- `td_handlers_railway.py` — 1 tool (`railway_tool`)
- `td_handlers_rigby_shift_brief.py` — 1 tool
- `td_handlers_rigby_work_queue.py` — 1 tool (`rigby_work_item`)
- `td_handlers_governance.py` — 1 tool (`zoom_out_tool`)
- `spider_data_aggregation_tool.py` — 1 tool (standalone file, no `td_handlers_*` prefix)

Full session context: `docs/handoffs/SESSION_2928_SLICE_5_CLOSE_BATCH_4.md`.

---

## S2929 open sequence — RE-SCOPE DECISION REQUIRED

**Slice 5 CLOSED is a natural pivot point.** The 5-slice `td_handlers_*` cadence that structured S2892 → S2928 is DONE. The remaining 15 untested tools don't fit the same slice shape (scattered across 8 files). **Chris directive to bias engineering / net-new builds over audit-of-what-exists at session open** (per `feedback_engineering_bias_over_audit`) means S2929 should propose net-new candidates FIRST before defaulting to more sweep work.

### Step 1 — Chris picks S2929 arc scope

**Option A (NET-NEW ENGINEERING — Chris-directive-aligned first):**
Actively propose 1-3 net-new candidates. Draft options for T0 SIGN:
- (A1) **BaseBusinessResearchAgent content-shape FAIL Fold REMEDIATION** — fix the ratified Fold at the base class. Root cause suspected in `AgentResult` construction path (query echoed to `data.query`, analysis payload not written to `data.content`). Concrete engineering — 1-2 files touched, base class + subclass verification. Reduces false-success signal risk platform-wide.
- (A2) **NEW UI/API/pipeline candidate** per Chris directive S2745 — e.g., a workspace tab surfacing Fold ledger status, an agent capability page, a real-time content-shape validator dashboard. Requires proposal + Rigby SIGN.
- (A3) **New spider or agent capability** — untapped data source or business capability. Requires proposal + Rigby SIGN.

**Option B (SLICE 5-HARDENING — Fork B deferred from S2928):**
Ship the 3-4 executable invariants Chris deferred by fork A at S2928 T0. Concrete slate:
- Output-envelope assertion test for content agents (BaseBusinessResearchAgent enforcement — direct Fold codification).
- Schema-required-field regularization lint (detect drift between `pa_tool_schemas.py` shape and handler expectations).
- Envelope-shape assertion (enforce 6-key async receipt envelope at handler level).
- Context-promotion consistency check (assert new top-level schema key is either in `_CONTEXT_PROMOTE_KEYS` or intentionally nested).
Estimated 1 focused session. Ships "close with teeth" for Slice 5 before any Slice 6+ opens.

**Option C (SLICE 6+ CONTENT HANDLER BATCH — sweep continuation):**
Open Slice 6 = `td_handlers_content.py` (6 untested tools: `blog_tool`, `execution_history_tool`, `feedback_tool`, `learning_patterns_tool`, `recent_activity_tool`, `surgical_moves_status_tool`). Largest remaining cluster; same shape as prior slices (single-file, multi-action handler pattern from Slices 1-4). If Chris wants to close the whole sweep before pivoting, this is the natural next slice.

**Option D (DOCS RESTRUCTURING ARC — queued at S2800):**
Chris directive S2800 close 2026-07-16 (per `project_docs_restructuring_arc_queued`): "next session opens a parent-scoped research arc auditing `/docs/` using the `/docs/research/` pattern itself." Was blocked behind sweep; NOW UNBLOCKED with Slice 5 CLOSED. Fresh session, first-action fresh mint. Output = design proposal + migration plan; NOT code changes / file moves.

**Option E (RIGBY TOOL-GAP LEDGER SLATE):**
Chris directive per `feedback_rigby_tool_gap_ledger`: "Claude reviews ledger at session close, picks 1-2 for next slate." Current Ledger has multiple entries; latest is `orm_inspect_tool` allowlist expansion. Substrate work — 1-3 tool-gap fixes as one PR. Reduces Rigby's tool-surface friction directly.

**Recommended framing for T0 SIGN:** propose one option from A / B / C / D / E with rationale. Present to Chris as plain-English decision (per `feedback_plain_english_decision_framing_for_chris`) — "do we lose anything?" + "is it more work later?" for each fork.

### What's forbidden at S2929 (D6 MORATORIUM still in force)

All S2925/S2926/S2927 forbidden entries carry forward (see S2927 handoff §Forbidden entries and S2928 handoff §"What's forbidden at S2929" — comprehensive list). **S2928 updates below.**

**S2928 promoted Fold (removed from "candidate" status):**
- ~~"content-shape FAIL surfaces only under completion-verify" Fold candidate~~ **RATIFIED at S2928 as BaseBusinessResearchAgent Content-Shape FAIL Fold.** Class-scoped to BaseBusinessResearchAgent subclasses. Any future 3rd/4th BaseBusinessResearchAgent instance is a **corroborating observation** not a new-Fold trigger. Ratified Fold pending remediation (Option A1 or Option B above).

**S2928 new forbidden entries (all 1st-instance — require corroborating trigger before promotion):**
- **No "work-not-done vs schema-preserved" Fold promotion without 2nd instance.** 1st (S2927 `workflow_orchestration_agent` completion — envelope schema populated correctly per template contract, but `step_results: []` + `project_created: null` indicate no sub-agent work happened). Distinct from Content-Shape FAIL class (envelope-key-missing). Watch for 2nd in future template-driven fanout tools.
- **No "extraction-contract doc-vs-reality drift" Fold promotion without 2nd instance.** 1st (S2928 `content_writer_agent` completion — actual path `data.content.full_text`, documented at `td_handlers_agents.py:170-171` as `metadata.content.full_text`). Watch for 2nd in Slice 6+ completion-verifies.
- **No "error-branch AE-not-persisted" Fold promotion without 2nd instance.** 1st (S2928 `image_editing_agent` tool-error branch). Watch for 2nd in Slice 6+ media/gateway tools.
- **No "Rigby tool-gap unblocking substrate arc" without explicit Chris directive.** 1st (S2928 `orm_inspect_tool` allowlist gap logged to Ledger). Multi-hour cleanup work; deferred to engineering slate.

**S2927 forbidden entries (carried forward):** No "template-driven bounded fanout via WorkflowOrchestrationAgent" Fold promotion without 2nd instance (1st S2927; corroborated shape at S2928 DISPATCH 4 but NOT a Fold trigger — the S2928 observation classifies as "work-not-done" not template-fanout); no "PR-A prerequisite → PR-B pattern-shape" Fold promotion without recurrence (1st S2927); no "multi-tool-single-class asymmetry doc-authoring pattern" Fold promotion without 3rd instance (2nd S2927 at Chris's validation-based ladder; **3 mapping-level instances verified at S2928 T0 SIGN** but Chris's gate is validation-based, not mapping-based — pending `security_agent` validation).

**S2926 forbidden entries (carried forward):** No "wrong-model reference to sister model in same registry" Fold promotion without 2nd instance; no "third-tier identifier surface in AgentResult" Fold promotion without 2nd instance; no "media provider egress as distinct §5a downstream axis" Fold promotion without 2nd instance (1st S2926 create_brand_video; corroborated at S2928 image_editing_agent doc but NOT a Fold trigger — shape is documented, not a new class instance); no "semantic-alias contract for shared-agent tool_names" Fold promotion without corroboration.

**S2925 + prior forbidden entries (carried forward):** D6 STRATEGIC DISCOVERY MORATORIUM; no R1a-shaped proposals; no v2 → v3 harness schema bump without substrate-arc-scoped SIGN; **no new gate/lint proposals** (Slice 5-hardening session per Option B is Chris-gated Slate, not a Playbook amendment); no agent-substrate validation arc; no `minimal_safe_args_v2` arc without explicit Chris directive; and all other S2925-prior entries per S2927 handoff §"S2925 + prior forbidden entries" — no changes at S2928.

### What's queued but deferred (do NOT open unless Chris directs)

- **Slice 5-hardening session (NEW post-S2928):** 3-4 executable invariants deferred per fork A decision. Content of Option B above.
- **BaseBusinessResearchAgent content-shape FAIL remediation** — Ratified Fold; specific engineering item (Option A1 above).
- **`orm_inspect_tool` allowlist expansion** (S2928 Ledger entry) — add AgentExecution + AgentResult. MEDIUM priority.
- **CompetitorAnalysisAgent content-FAIL remediation** (S2926 Ledger `5703a6c8-...`) — now folded under BaseBusinessResearchAgent Fold. Same engineering scope as Option A1.
- **Ledger #34 broader stale-model sweep** — multi-hour engineering.
- **Bundled dev-env drift slate** — S2919 narrative + S2925 Ledger #33/#34 legacy + AgentTaskExecution pre-existing pyright drift + S2927-observed `td_handlers_agents.py` pyright drift (10 diagnostics latent).
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note. Unchanged.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate + Ledger candidate: media_tool.delete IRREVERSIBLE** — 2/3. Unchanged.
- **S2909-S2927 Ledger candidates** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **S2919 narrative_tool dev-env drift** — unchanged.
- **S2925 Ledger #34 (LOW)** — broader stale-model latent bug; multi-hour cleanup deferred; may become substrate work.
- **S2926 Ledger candidate — AgentTaskExecution pre-existing pyright drift** — Candidate for bundled dev-env drift slate.
- **R1 fleet reject-mode flip** — deferred.
- **Docs restructuring arc** (`project_docs_restructuring_arc_queued`) — **NOW UNBLOCKED with Slice 5 CLOSED** (Option D above).
- W2 #1 / #2b / #2c — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris skipped at S2849.
- LLMCallLog field splits — migration required.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os side follow-ons.

---

## Sweep progress tracker (Path B ratified S2892) — SLICE 5 CLOSED

**Slice 1 — `td_handlers_ops` (17 registered tools):** UNCHANGED (per prior handoffs).
**Slice 2 — `td_handlers_agents` (25 tools):** **CLOSED at S2912.**
**Slice 3 — `td_handlers_core` (22 tools):** **CLOSED at S2917 (22/22).**
**Slice 4 — `td_handlers_gateway` (17 tools):** **CLOSED at S2924 (17/17).**
**Slice 5 — `tool_dispatcher` (14 tools): CLOSED at S2928 (14/14).** ✅ COMPLETED

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix). S2921 §5a 4-tier taxonomy amendment shipped as doc-only sweep substrate. S2923 latent-cascade authoring convention shipped as doc-level rationale-writing pattern. S2924 Slice 4 §5a tier distribution artifact shipped as slice-close reference. S2925 Slice 5 batch 1 end-to-end §5a classification pattern shipped as authoring guidance in-doc. **S2927 delivered no new substrate arcs** — pure sweep-batch + 1 latent-bug fix. **S2928 delivered Slice 5 CLOSE artifact + Content-Shape FAIL Fold PROMOTION** (2/2 ratified) — no new substrate arcs; documented Fold codification via handoff + CLOSE artifact + 00-START "removed from candidate" status.

**Total remaining tools to close:** **15 across 8 handler files.** Not a clean "single-slice" mapping.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2928 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2928: zero A4 spend** — pure sweep-batch engineering (Slice 5 batch 4 FINAL + Slice 5 CLOSE artifact + close cascade). A1 shipping spend was 1 substantive PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2928)

See:
- **S2928 handoff (current):** `docs/handoffs/SESSION_2928_SLICE_5_CLOSE_BATCH_4.md`
- **S2927 handoff:** `docs/handoffs/SESSION_2927_SLICE_5_BATCH_3.md`
- **S2926 handoff:** `docs/handoffs/SESSION_2926_SLICE_5_BATCH_2.md`
- **S2925 handoff:** `docs/handoffs/SESSION_2925_SLICE_5_BATCH_1.md`
- **S2924 handoff:** `docs/handoffs/SESSION_2924_SLICE_4_CLOSE_BATCH_7.md`
- **Slice 5 CLOSE artifact (NEW):** `docs/audits/pa_tools/substrate/slice_5_close_artifact.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (§5a 4-tier blast-radius taxonomy amended S2921; Slice 5 end-to-end classification guidance in-doc post-S2925 + corroborated across S2926/S2927/S2928)
- **S2928 per-tool validation docs (batch 4):** `docs/research/tools/validation/{content_writer_agent,image_editing_agent}_validation.md`
- **S2927 per-tool validation docs (batch 3):** `docs/research/tools/validation/{workflow_orchestration_agent,content_strategy_agent,marketing_strategy_agent,strategic_review}_validation.md`
- **S2927 regression test:** `core/tests/test_tool_to_agent_name_mapping.py` (3 tests)
- **S2926 per-tool validation docs (batch 2):** `docs/research/tools/validation/{create_brand_video,video_editing_agent,three_d_generation_agent,character_training_agent}_validation.md`
- **S2925 per-tool validation docs (batch 1):** `docs/research/tools/validation/{brand_strategy_agent,competitor_analysis_agent,customer_research_agent,create_project_from_research}_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (100 per-tool validation docs post-S2928)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (1 new entry this session — `orm_inspect_tool` allowlist gap).
- **BaseBusinessResearchAgent content-shape FAIL Fold (RATIFIED S2928):** engineering item in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` — deliverable `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5` (was S2926-scoped as CompetitorAnalysisAgent-only; now Fold-scoped to BaseBusinessResearchAgent).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
