# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2966 CLOSED. Golden Evals validator harness **PR-2b (Rigby fabrication runners + slice 8 dogfood + AgentRouter dispatch) shipped**. PR #3573 merged at HEAD `76710a425` (+1,596 / -175 across 3 files). 6 Rigby-specific fabrication predicates (2 ledger-gated / 1 partial-downgrade / 3 non-gated) + `one_of` branch dispatcher (per S2963 canon_v2 §4 ≤2 branches) + 7 per-agent canonicalizers (Research / DevOps / Workflow / Legal / Content / Competitor / Rigby) + `AgentRouter.route()` dispatch pathway (Rigby SIGN D1 Option C — simpler than the 00-START-listed Celery/two-phase options) + marker-based row resolver + `process_pa_chat_task.apply().get()` synchronous ChatConversation dispatch + shared `_validate_and_wrap` all landed. End-to-end dogfood — 3 substrate/agent pairings PASSED (SIA/AgentExecution: `primary_row_id=4cd44d35` closes S2965 empty-gap / Rigby/ChatConversation: `primary_row_id=4652` first slice-8 real dispatch / Research/AgentExecution: multi-agent router path smoke). **S2965 PR-2a known limitation CLOSED** (direct `.execute()` bypass replaced with canonical `AgentRouter.route()` write path). **10 consecutive terminal ratifications S2957→S2966.** **S2967 first-action = nightly beat task + pass-rate drift dashboard** (per S2963 arc structure) — or a per-slice PR to graduate named per-slice predicates from INCONCLUSIVE.

**Golden Evals arc status:**

| Session | Phase | Ship | HEAD |
|---------|-------|------|------|
| S2954 | arc open | Tier-1 list + Day-1 scope | (arc-open doc) |
| S2955-S2962 | Tier-1 spec-authoring (8/8) | 8 canon_v1 YAMLs | `6bf8d9a81` (S2962) |
| S2963 | arc close | canon_v2 ratification (6 items) | `882626d8f` |
| S2964 | harness PR-1 (foundation) | allowlist + EvalRunContext scaffold + skeleton adapters + mgmt cmd + `GoldenEvalRun` model | `137410e86` |
| S2965 | harness PR-2a (executors + runners + --execute) | JSON Schema executor + fault-injection parser + universal runners + SIA canonicalizer + full adapter build-out + `--execute` flag + SIA end-to-end dogfood | `38ee09602` |
| **S2966** | **harness PR-2b (Rigby runners + slice 8 dogfood + AgentRouter dispatch)** | **6 Rigby fabrication predicates + one_of dispatcher + 7 canonicalizers + AgentRouter.route() dispatch + marker resolver + process_pa_chat_task synchronous dispatch + SIA/Rigby/Research end-to-end dogfood** | **`76710a425`** |
| S2967 (next) | nightly beat + drift dashboard | scheduled runs + pass-rate telemetry, OR per-slice predicate graduation | TBD |

**Canon_v2 items — code landing status:**

| Item | Ratified S2963 | Landed at PR-1 (S2964) | Landed at PR-2a (S2965) | Landed at PR-2b (S2966) |
|------|----------------|------------------------|-------------------------|-------------------------|
| 1 — `orm_inspect_tool` allowlist | ✅ | ✅ | — | — |
| 2 — source stratification | ✅ | ✅ (helper) | ✅ (adapter enforcement + safety net) | — |
| 3 — opt-in `latency_ms` evidence class | ✅ | ✅ (dataclass field) | ✅ (adapter opt-in path exercised) | — |
| 4 — receipt-contamination predicate | ✅ | ✅ (helper) | ✅ (adapter enforcement + safety net) | — |
| 5 — fault-injection selector convention | ✅ | ⏭ | ✅ (parser rejects handler-registry keys) | ✅ (one_of aggregation) |
| 6 — `EvalRunContext` shape | ✅ | ✅ (dataclass + validation) | ✅ (extended with `evidence_source` + `ledger_health`) | ✅ (7 more canonicalizers + ChatConversation dispatch branch) |

**PRs shipped this session (S2966):**
- u-d-b PR **#3573** — S2966 PR-2b Golden Evals harness Rigby runners + slice 8 dogfood + AgentRouter dispatch (+1,596 / -175).
- u-d-b PR **#TBD** — S2966 close cascade (handoff + this 00-START refresh + wrapper pin bump).

**Post-merge:** `make recycle-all` executed per PLAYBOOK-7.4.4 (workers advanced to sha=`76710a4251e5`).

**Governance:** Rigby T1 pre-code SIGN = 10 tool_run verifications + 5 decisions all AGREE + 4 REVISE nuances accepted (marker location / mixed one_of resolution / max-signal governing principle / HEAD drift correction). Zoom-out ratification: maximum signal with degraded labels over maximum correctness. Chris D-verdict via terminal after plain-English framing (Q1 "do we lose anything?" / Q2 "is it more work later?"). Rigby A2 post-code SIGN = 10 tool_run verifications independently confirmed SIA row + ChatConversation row + registries + GoldenEvalRun table row count.

**Rigby Tool Gap Ledger:**
- **Ledger #20 — no change** (`ToolCallRecord.trace_id` NULL on 100% of rows). Fix in separate arc.
- **Ledger #21 — no change** (PA→ToolCallRecord write silent regression). Fix in separate arc.
- **Ledger #17 — no change** (Chris terminal path continues; **10 consecutive terminal ratifications S2957→S2966**).
- **Ledger #19 — no change** (allowlist landed S2964; still discharged).
- **Rigby outbound-messaging gap candidate — RE-SCOPED S2966 post-close** (2 triggers observed for arbitrary-outbound sub-case; async completion notification VERIFIED working via post-close flow test — see §Flow test correction). NOT promoting to urgent arc.

Full session context: `docs/handoffs/SESSION_2966_GOLDEN_EVALS_HARNESS_PR2B.md`.

---

## S2967 open sequence

**S2967 first-action = Path A** — nightly beat + pass-rate drift dashboard. **Ratified 2026-07-25 (Chris terminal) after S2966 post-close flow test** (see §Flow test correction below).

**Path A (RATIFIED for S2967):** Ship a Celery beat task that runs `run_golden_evals --execute` across all 8 slices on a schedule + a UI/API to surface pass-rate trends per-slice/per-prompt/per-substrate. Uses `GoldenEvalRun` rows already persisting (112 as of S2966 close). Per S2963 arc structure "S2965+ nightly beat + drift dashboard".

**Path B (deferred):** Per-slice named predicate graduation — register named predicates that currently return INCONCLUSIVE. Small per-slice PRs; SIA first as smallest.

**Path C (deferred):** Ledger #20 + #21 fix arc. Populate `trace_id` at ToolCallRecord write sites; investigate + fix silent PA write regression at `tool_dispatcher.py:1043`; migrate `ToolCallRecord.conversation_id` to CharField or add UUID coerce helper. Unblocks Rigby fabrication predicates from perpetual INCONCLUSIVE.

### Flow test correction (S2966 post-close, 2026-07-25)

Chris asked whether the flow "Rigby researches platform → proposes business → dispatches agents → returns findings" actually works today. Live test dispatched `bash tools/pa_local.sh "Rigby — real end-to-end test..."` at 19:55:25 UTC.

**Result: FLOW WORKS.** Rigby:
1. Ran 4 platform-research tools (`kb_tool`, `search_docs`, `ops_digest_tool`, `agent_introspection_tool`).
2. Proposed a concrete business: "Close Pack + Outreach Sequencer" — AI tool converting service offer → proposal + contract + invoice + 3-touch email sequence. 30-day shippable.
3. Dispatched 3 real async agents via `universal_agent_tool` with `auto_followup=true`:
   - `CustomerResearchAgent` (task `f711a403-…`) — completed at 19:56:13 (3,829 tokens)
   - `CompetitorAnalysisAgent` (task `8e51cb69-…`) — completed at 19:56:24 (3,223 tokens)
   - `OpportunityScoringAgent` (task `a69dc4fa-…`) — completed at 20:00:02 (4,444 tokens)
4. All 3 `AgentFollowupSubscription` rows fired (`state='fired'`) via `fire_agent_followup_subscriptions` at `tasks_agents.py:337`.
5. 3 completion notifications posted back to conversation `pa-bb3ef373c93847db` as `source='pa' intent='agent_completion'` ChatConversation rows.
6. 2 Deliverables persisted (Customer Research `b2eccbbb-…`, Competitor Analysis `e6bc8628-…`) — visible in workspace UI.

**Correction to S2966 handoff §"Rigby outbound-messaging gap SECOND TRIGGER OBSERVED":** the promotion candidate was mis-scoped. The gap conflated (a) async agent-completion notification — which WORKS end-to-end via `fire_agent_followup_subscriptions` — with (b) arbitrary outbound (Rigby proactively starting a new topic in a thread she wasn't called into) — which is a distinct, lower-urgency gap with 2 observed triggers (S2965 D-verdict framing / S2966 D-verdict framing). Neither trigger blocks Chris's core flow. Not promoting to urgent arc; if it recurs on end-user-visible surfaces (not SIGN cycle relay), reconsider then.

### Universal open sequence (unchanged)

1. **Live-verify S2953 drift scanner:** `bash tools/pa_local.sh "run agent_capability_drift_tool action=summary"` — expect shape (83/92/59/1 → 77 active).
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --check` — confirm gap-map headline (`100 full / 2 untested` last observed at S2963).
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2967 pin (retired at S2966 close cascade).
4. **Read S2966 handoff + PR-2b shipped code:** `docs/handoffs/SESSION_2966_GOLDEN_EVALS_HARNESS_PR2B.md` + `core/services/golden_evals/` (runners with Rigby predicates + one_of + canonicalizers × 8) + `core/management/commands/run_golden_evals.py` (AgentRouter dispatch + ChatConversation branch).
5. **Read canon_v2 doc if not already loaded:** `docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md` (190 lines).
6. **Verify Rigby Tool Gap Ledger:** deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` — no delta this session; log Rigby outbound-messaging gap next session (second trigger observed).

### S2967 scope note

**In scope for S2967 (Chris to pick path):** nightly beat + drift dashboard (Path A) OR per-slice named predicate graduation (Path B) OR Ledger #20 + #21 fix arc (Path C).

**Out of scope for S2967:** WorkflowOrchestrationAgent wrapper key-name mismatch (F1 from S2958). Latent migration drift remediation.

### Capability Manifest — build spec (parallel-track from A1 Phase 1 start)

_(unchanged — see prior S2953 close snapshots; not part of Golden Evals arc)_

### A1 Phase 1 still ahead (after harness + drift dashboard land)

Chris's 4 open questions from scoping deliverable `7870eca9` still gate Phase 1 code:

1. **Minimum evidence standard** we promise? (run IDs + failure signature samples vs metrics only)
2. **Default turnaround SLA** we can consistently hit without heroics?
3. Sell as **agent-system audit** (end-to-end) or **toolchain reliability audit** (tools/contracts) first?
4. **Legal posture** for handling customer logs (retention window, deletion guarantee, allowed data types)?

### Deferred queue (updated at S2966 close)

**S2966 additions:**
- **Nightly beat + drift dashboard (S2967 Path A candidate):** Celery beat task running `run_golden_evals --execute` across 8 slices + pass-rate telemetry surface.
- **Per-slice named predicate graduation (S2967 Path B candidate):** register SIA-specific / Rigby-slice-specific / other agent-specific predicates that currently return INCONCLUSIVE. Small per-slice PRs.
- **Separate arc (S2967 Path C candidate):** Ledger #20 + #21 code fixes — populate `trace_id` at ToolCallRecord write sites, investigate + fix silent PA write regression, migrate `ToolCallRecord.conversation_id` field type or add UUID coerce helper. Unblocks Rigby fabrication predicates from perpetual INCONCLUSIVE.
- **Rigby outbound-messaging gap** — **SECOND TRIGGER OBSERVED S2966**. Promote from candidate to logged ledger entry next session.

**Carry forward from S2965:**
- S2965 known limitation CLOSED S2966 (primary_row_id populated via canonical AgentRouter write path).

**Carry forward from S2964:**
- Latent migration drift (Narrative* / HAIDispatchLog AlterField pile).
- `claude_code_tool` stdout / duration_ms capture gap (Probe 3 caveat from S2964).
- Complex-boolean-in-canon-doc misread pattern (one trigger observed).

**Carry forward from S2963:**
- Fold P2 / S1 / U1 / P1 / V1 / U2 — all DISCHARGED as canon_v2 Items 1/2/3/4/5/6 at S2963 arc-close.

**Long-standing (carry forward):**
- Docs restructuring arc (Chris-ratified S2800).
- Slice 5-hardening executable invariants.
- Tier 2 lint promotion.
- Advanced paste-UUID fallback for cluster picker.
- Server-side search + pagination on `/eligible/`.
- Z1/Z2/Z4 signal-dispatch UI polish.
- Rank + cap + paginate follow-ups.
- Per-pattern-type diversity floors.
- Ledger candidates backlog.
- W2 #1 / #2b / #2c pending Chris re-slate.
- LLMCallLog field splits.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os follow-ons.

---

## What's forbidden at S2966 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2966 new forbidden entries:** none.

Canon_v2 forbid (fault-injection selectors) is now **actively enforced in code** at `core/services/golden_evals/fault_injection.py:parse_selector` — bare identifiers or non-importable dotted paths raise `FaultInjectionSelectorError` at load time.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2965 additions to the deferred queue:** (see above §Deferred queue).

**Long-standing:**
- Docs restructuring arc (Chris-ratified S2800).
- Slice 5-hardening executable invariants.
- Tier 2 lint promotion.
- Advanced paste-UUID fallback for cluster picker.
- Server-side search + pagination on `/eligible/`.
- Z1/Z2/Z4 signal-dispatch UI polish.
- Rank + cap + paginate follow-ups.
- Per-pattern-type diversity floors.
- Ledger candidates backlog.
- W2 #1 / #2b / #2c pending Chris re-slate.
- LLMCallLog field splits.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) + pre-A1 capability triage (S2952) + capability substrate (S2953) + Golden Evals arc (S2954-**S2965**) are adjacent-domain net-new engineering + arc substrate, not sweep work.

**Total remaining sweep tools: 0.**

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force)

1. **Spend lane:** A4 warm-up uses separate budget lane/cap; must NOT consume A1 shipping spend.
2. **Evidence tag:** All A4 artifacts labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up constrained to fixed timebox + fixed send count (3-5 total intros).
6. **No bespoke follow-ups.**

---

## For fuller context (S2846 → S2965)

See:
- **S2965 handoff (current):** `docs/handoffs/SESSION_2965_GOLDEN_EVALS_HARNESS_PR2A.md`
- **S2965 shipped code:**
  - `core/services/golden_evals/` — canonicalizers.py + executors.py + fault_injection.py + runners.py + context.py (extended) + adapters/{agent_execution,chat_conversation}.py (extended)
  - `core/management/commands/run_golden_evals.py` (extended with `--execute` mode)
  - `core/models_golden_evals.py` (extended with `evidence_source` + `ledger_health`)
  - `core/migrations/0396_s2965_golden_eval_evidence_source_ledger_health.py`
- **S2964 handoff:** `docs/handoffs/SESSION_2964_GOLDEN_EVALS_HARNESS_PR1.md`
- **S2964 shipped code:**
  - `core/models_golden_evals.py` (GoldenEvalRun)
  - `core/services/golden_evals/` (package: context + adapters + loader — extended at S2965)
  - `core/management/commands/run_golden_evals.py` — extended at S2965
  - `core/services/td_handlers_agents.py:820-870` (canon_v2 Item 1 allowlist additions)
- **S2963 handoff:** `docs/handoffs/SESSION_2963_GOLDEN_EVALS_ARC_CLOSE_CANON_V2.md`
- **S2963 canon_v2 ratification doc:** `docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md` (190 lines)
- **S2962 handoff:** `docs/handoffs/SESSION_2962_GOLDEN_EVALS_SLICE_8_RIGBY_YAML.md`
- **S2962 shipped code:** `evals/tier1/rigby_agent.yaml` (1,628 lines, 18 prompts, eighth canon_version=1 reference / FIRST non-AgentExecution substrate)
- **S2961 handoff:** `docs/handoffs/SESSION_2961_GOLDEN_EVALS_SLICE_7_COMPETITOR_YAML.md`
- **S2961 shipped code:** `evals/tier1/competitor_analysis_agent.yaml` (1232 lines)
- **S2960 handoff:** `docs/handoffs/SESSION_2960_GOLDEN_EVALS_SLICE_6_CONTENT_YAML.md`
- **S2960 shipped code:** `evals/tier1/content_writer_agent.yaml` (950 lines)
- **S2959 handoff:** `docs/handoffs/SESSION_2959_GOLDEN_EVALS_SLICE_5_LEGAL_YAML.md`
- **S2959 shipped code:** `evals/tier1/legal_doc_drafter_agent.yaml` (794 lines)
- **S2958 handoff:** `docs/handoffs/SESSION_2958_GOLDEN_EVALS_SLICE_4_WORKFLOW_YAML.md`
- **S2958 shipped code:** `evals/tier1/workflow_orchestration_agent.yaml` (801 lines)
- **S2957 handoff:** `docs/handoffs/SESSION_2957_GOLDEN_EVALS_SLICE_3_DEVOPS_YAML.md`
- **S2957 shipped code:** `evals/tier1/devops_agent.yaml` (612 lines)
- **S2956 handoff:** `docs/handoffs/SESSION_2956_GOLDEN_EVALS_SLICE_2_RESEARCH_YAML.md`
- **S2956 shipped code:** `evals/tier1/research_agent.yaml` (523 lines)
- **S2955 handoff:** `docs/handoffs/SESSION_2955_GOLDEN_EVALS_SLICE_1_SIA_YAML.md`
- **S2955 shipped code:** `evals/tier1/system_intelligence_agent.yaml` (canon_version=1 original reference, 463 lines)
- **S2954 arc-open handoff:** `docs/handoffs/SESSION_2954_GOLDEN_EVALS_ARC_OPEN.md`
- **S2954 arc-open scoping doc:** `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md` (95 lines)
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope (unchanged, S2951):** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`) — updated at S2965 with #20 + #21.
- **Ledger #17 (S2957):** `db316865-d08c-4cc1-9d8e-cfac249e8c89` — Chat UI response-relay gap (unchanged this session)
- **Chat UI relay design task (S2957):** `f3f140f9-87bf-488b-8757-eab5d8058f45`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
