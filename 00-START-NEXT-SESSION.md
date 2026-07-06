# Next Session — Start Here

---

## READ THIS FIRST — S2601 P1 CAT A COMMITTED + T3 GROUP 2600 PA ARC 2-OF-6 SHIPPED + S2602 P2 CAT B NEXT

**S2601 P1 Cat A PA Endpoint Contract SoT Design-Prep child audit COMMITTED 2026-07-06.** Playbook §11.2 20-section child-audit template TWENTY-FIRST-consecutive application (after S1301/S1401/S1501/S1601/S1701/S1801/S1901/S2001/S2101/S2102/S2103/S2104/S2201/S2202/S2203/S2204/S2401/S2402/S2403/S2404/S2501 twenty prior). Doc: `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` — ~750 lines post-fold (7 SIGN cycle 1 folds S1-S7 baked). Chris "agree all" 2026-07-06 ratified all 9 shape-card SIGN-preview folds wholesale pre-drafting + Chris "agree all" 2026-07-06 ratified 7 SIGN cycle 1 STRENGTHEN folds via 2-pin recovery pattern per `feedback_rigby_sign_worker_instability_recovery.md` (Pin 1 `pa-ad162d8af36c4985` TWENTY-FOURTH consecutive dedicated fresh SIGN pin retirement — Batch 1/2 substantive verdicts + turn-3 worker instability at close prompt + retired 5 rows; Pin 2 `pa-767dddd95cb24099` TWENTY-FIFTH consecutive candidate — recovery ultra-short-ping + titles-only close + retired 3 rows). Parent-Claude verifier-loop applied as compensating quality gate: 2 recovery-pin Q4 suggestions (Q4.3 remediation ladder + Q4.4 verification harness) REJECTED as Cat A boundary violations. Cycle 2 NOT required. Arc pin `pa-c17a8d7e0660413b` PRESERVED through S2601.

**Group 2600 PA arc 2-of-6 sessions shipped** (S2600 parent scoping + S2601 Cat A). **NEXT: S2602 P2 Cat B PA-client contract surface design-prep** per §5.1 child mission sequence.

### `tools/pa_local.sh:348` UNCHANGED at S2601 close — arc pin PRESERVED

`tools/pa_local.sh:348` `--conversation` value UNCHANGED at S2601 close — arc pin `pa-c17a8d7e0660413b` continues to route all Claude Code → Rigby chatter through the Group 2600 PA arc pin per playbook §16 arc-standard behavior (no rotation until arc close at S2699 xx99).

**S2602 P2 arc-continue protocol:** `tools/pa_local.sh` invocation continues to route to active Group 2600 arc pin. Verify `service_context: local` via `platform_config_tool overview` at S2602 open turn 1 before any Cat B audit work.

## READ THIS SECOND — S2602 P2 CAT B PA-CLIENT CONTRACT SURFACE DESIGN-PREP QUEUED

**S2602 P2 is the NEXT child per §5.1 child mission sequence** in `docs/research/domains/pa/2600_pa_domain_scoping.md`. Focus:

- **PA-client contract surface design-prep** — F1 hard boundary (contract-typing + field-list ONLY; NO UI/UX behavior changes + NO state-mgmt refactors + NO frontend build/bundling changes + NO frontend testing framework decisions).
- **Three consumer surfaces:**
  - `frontend/src/lib/api.ts` — assistantApi module (subset of 93 apiModule / 4,194 LOC file per S2202 baseline)
  - `frontend/src/stores/paStore.ts` (or equivalent) — paStore field list resolution
  - `tools/pa_chat.py` — CLI wrapper 3-way chat message envelope contract
- **Chris-D-verdict axes (Cat B):**
  - **(a)** Typed assistantApi.ts island — analog to cockpitApi.ts 96%-typed exemplar per S2502
  - **(b)** SHAPE-BLIND flow-through preserved — PA-client stays untyped consistent with 7.36% platform-wide typed rate
  - **(c)** Hybrid — typed for PA-response envelope shape (success/error boundary) but SHAPE-BLIND for message payload (streaming tokens + tool-run objects + audio_url)
- **U6 + U7 evidence-gap closure turn 1 (F9 fold parent scoping):**
  - **U6** (WS envelope-schema type UNKNOWN): inventory PA-related WS channels (subset of platform 120) + sample envelope shape on chat-response streaming + task-status broadcast + async-audio-url delivery. Decision-space (TypedDict / Protocol / BaseModel) cannot be enumerated pre-inventory.
  - **U7** (paStore field-list completeness UNKNOWN): dump paStore full field list (currently observed: 3-of-9 syncUser fields wiped at logout per S2503 CF-C3; remaining 6 fields intent-preserved OR cleanup-debt UNKNOWN).
- **F10a fold guardrail:** NO Cat B option enumeration until inventory confirms U6/U7. If Cat B opening reveals materially different shape than expected, parent scoping §3.B revises.
- **Cat A inheritance:** consume `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` §6.1 F11 canonical endpoint inventory table (34 endpoints × 11 columns) + §7.2 REST-side "task-based async, NO streaming" statement + §14 verifier-loop corrections (PAResponse EXISTS + tool schemas = 113 + enrichment services = 8) + §16.1 F-B-HIGH-3 REST-boundary state.

**S2602 arc-open protocol:**
1. `tools/pa_local.sh "platform_config_tool action=overview"` → verify `service_context: local` + `railway_environment: local` + `database_name: unified_donkey_betz` + `default_llm_provider: openai` under active Group 2600 arc pin `pa-c17a8d7e0660413b`.
2. Read `docs/research/domains/pa/2600_pa_domain_scoping.md` fully — DIRECT PARENT for Cat B + §3.B Cat B scope + §5.3 AC + §2.5 evidence gaps.
3. Read `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` fully — SIBLING PRIOR-CHILD (Cat A) — §6.1 F11 canonical endpoint inventory + §14 verifier-corrections + §19 recommended future research.
4. Read `docs/research/domains/frontend/2202_frontend_api_client_surface_audit.md` — PARENT-arc predecessor (assistantApi module inventory + cockpitApi 96%-typed exemplar; 7.36% platform-wide typed rate baseline).
5. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 child audit template + §21 short-command vocabulary + §13 sub-agent Explore contracts + §14 verifier-loop discipline + §15 SIGN-isolation.
6. Read the 4 CF-* handed forward + F-* preserved: CF-2600-PA (S2501 Cat A) origin + F-B-HIGH-3 preserved (S2402→S2504→S2601 Cat A boundary) + PA-client shape-blind pattern (S2504 SHAPE-BLIND interceptor).
7. Draft Cat B shape-card 4-Q (Q1 consumer surface enumeration + Q2 lens inheritance from §2.6 + Q3 acceptance criteria for Cat B + Q4 anti-scope inheritance). Route to Rigby SIGN-preview via arc pin `pa-c17a8d7e0660413b` (single-batch × 4-Q preview cadence per S1899-S2601 TENTH-consecutive tested pattern; ELEVENTH-consecutive-at-child-scoping candidate).
8. Fold SIGN-preview edits pre-drafting.
9. Draft full Cat B audit doc as `docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md` per playbook §11.2 20-section template.
10. Route full doc to Rigby SIGN cycle 1 via dedicated fresh SIGN isolation pin (TWENTY-SIXTH consecutive candidate) per playbook §15 SIGN-isolation discipline. Preemptive: batch SIGN into 2-batch × 2-Q for doc >4k words per `feedback_rigby_sign_worker_instability_recovery.md`.
11. Fold SIGN edits + retire SIGN pin at close.
12. Present Chris ratification card. Status flips `draft` → `active` on ratification.

## READ THIS THIRD — S2601 CAT A LOAD-BEARING OUTPUTS

**Cat A audit doc at `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md`:**

- **§6.1 F11 canonical PA-path endpoint inventory table** — 34 endpoints × 11 evidence columns. **AC-A2 canonical artifact — later sessions (Cat B/C/D + S2699 xx99) MUST NOT re-inventory PA-path endpoints; cite this table.**
- **§3.3 F8 baseline codification NEGATIVE at `/api/pa/chat/`** — 4-row evidence table. Per S1 fold: any Chris-D-verdict selecting Path C-pure at S2699 xx99 would explicitly accept CLAUDE.md canonical PA entry point remains without machine-consumable REST-boundary contract declaration at HEAD.
- **§6.2 per-endpoint disposition (AC-A1 measurability)** — 0 Path A eligible + 1 Path B eligible (PaMessageFeedback) + 33 Path C+island eligible + 0 UNKNOWN existence-of-declaration + 5 UNKNOWN def-site (rows 1 assistant_context aggregator + rows 31-34 dev/minimal). AC-A1 = 100% categorized.
- **§7.1-§7.2 REST-side "task-based async, NO streaming" statement** — Cat A REST-side evidence for AC#8 F12 T7 cross-transport consistency check; Cat D S2604 owns WS-side.
- **§16.1 F-B-HIGH-3 workspace-membership implicit-gate location** at `core/agents/base_agent.py:5355 execute_with_workspace()`. Per S7 fold: Cat C1 S2603 owns closure verdict; Cat A does not pronounce constraint.
- **§14 5 pre-draft verifier-loop corrections + §20.5 4 conflicts logged + §20.6 verifier-loop summary + §20.8 SIGN cycle 1 fold record (S1-S7).**

## READ THIS FOURTH — LOAD-BEARING INPUTS FOR NEXT SESSION

**S2602 P2 Cat B arc-open must consume:**
- `docs/research/domains/pa/2600_pa_domain_scoping.md` (S2600 parent scoping — DIRECT PARENT + §3.B Cat B scope + §5.3 AC + §2.5 U6/U7 evidence gaps + §2.6 central lens)
- `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` (S2601 Cat A — SIBLING PRIOR-CHILD + §6.1 F11 canonical inventory + §7.2 streaming-negative + §14 verifier corrections + §16.1 F-B-HIGH-3 boundary)
- `docs/research/domains/frontend/2202_frontend_api_client_surface_audit.md` (S2202 Cat B — PARENT-arc predecessor + assistantApi module inventory + cockpitApi 96%-typed exemplar)
- `docs/research/domains/api/2599_api_canonical_summary.md` (S2599 xx99 — Group 2500 API canonical verdict inheritance)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 + §13 + §14 + §15 + §16 + §21

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2601 close residuals — post-Cat-A-audit docs cascade PR

Per Chris "agree all" ratification at S2601 close 2026-07-06:

- **Post-commit docs cascade PR** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Verify final chunk count + provenance-json refresh in PR body.

- **ARCHITECTURE_INDEX.md + OPEN_ARCS.md deferred anchor cascade** (extends S2600 close deferrals):
  - **AU-4** ARCHITECTURE_INDEX §1.99 S2601 backfill (Group 2600 PA Cat A child audit registration) + v94 → v95 version bump.
  - **AU-5** ARCHITECTURE_INDEX §8 timeline: 1 row added (S2601 Cat A).
  - **AU-6** ARCHITECTURE_INDEX §3 domain map PA row: Cat A closed at S2601; 3-of-4 children remaining.
  - **AU-9** ARCHITECTURE_INDEX §9 roadmap T-slot queue advance: unchanged (T3 Group 2600 PA still in-progress; T4 Group 1700 Observability queued after Group 2600 close).
  - **OPEN_ARCS.md** Group 2600 PA row S2601 child-registration update (in-progress → 2-of-6 sessions shipped).

- **Deep anchor-update items deferred from S2599** (still pending):
  - **AU-1** PLATFORM_INVENTORY §API autoblock CREATE (with Cat D §1.1 D1-D6 Denominator Contract per Rigby Q2 fold; generator extends `gather_inventory()` per S2499 precedent).
  - **AU-3** PLATFORM_WHAT_IT_IS §API narrative subsection CREATE.
  - **AU-10** `docs/topics/api.md` CREATE (analog to `docs/topics/auth.md` per S2499 AU-D2 + AU-D7).
  - **AU-11** `platform_architecture_inventory.md` §3.22 API Layer REVISE.
  - **AU-12** CODEOWNERS cockpit surface refinement deferred to S2601+ per CODEOWNERS lines 8-13 explicit deferral.

### Group 2400 + Group 2500 post-arc remediation queue (unchanged carry into S2602)

**P0-A platform-wide (S2599 xx99 execution scope carry):**
- **AU-U1** Route→view normalization pass to compute D4 unique-view denominator (blocks ratio-comparison truth + Cat B (c) permission-floor governance verdict-confidence but NOT tactical P0-A execution per Rigby Q4 STRENGTHEN fold blocking-vs-non-blocking clarifier).
- F-D-CALL-1 803-scale silent-401 remediation.
- F-D-BYPASS-1 79-raw-fetch bypass reconciliation.
- F-D-ENVELOPE-1 typed-error-envelope execution.
- F-D-BOUNDARY-1 error-boundary framework establishment.

**P0-B token lifecycle / security window (unchanged):**
- F-D-SIDEBAR-1 Sidebar backend-token-revoke fix (single-line).
- F-C-REFRESH-1 refresh discipline decision-space execution.
- F-C-VIP-1 VIPInvite.account_expires_at ENFORCEMENT.
- F-C-CSD-1 Clear-Site-Data emission on logout.
- F-C-STORE-1 15-surface × logout-cleanup declared contract execution.

**P0-C endpoint-specific (unchanged):**
- F-CRIT-1 PURGE_SECRET hardcoded fallback remediation.
- F-BND-4a Unauthenticated bet-placement WRITE remediation.
- F-B-CRIT-1 Permission-floor implicit-inheritance ~80-90% (blocks on AU-U1 D4).
- F-B-CRIT-2 Silent-401 SYSTEMIC.
- F-D-WHITELIST-1 Whitelist replacement (γ PROPOSED PRIMARY per Rigby Q7 fold).
- F-D-REGISTRY-1 Per-endpoint permission-floor registry.
- F-D-WSENVELOPE-1 WS message-contract SoT.

### T-slot follow-on queue (post-Group-2600-close forward look — unchanged)

- **T3 Group 2600 PA** — **IN-PROGRESS**, 2-of-6 sessions shipped (S2600 parent scoping + S2601 Cat A closed).
- **T4 Group 1700 Observability cross-arc handoff bundle** — QUEUED after Group 2600 close.
- **T5 Group 2300 Mobile (parallel)** — QUEUED after Group 2600 close.
- **T6 Group 1600 Content** — QUEUED after Group 2600 close per Cat C S2503 Rigby SIGN Q11 fold CF-C8.
- **Maintainer-decision batch** — CODEOWNERS API-slice discipline + DEAD-CANDIDATE consolidated cleanup + api.ts extraction execution + storageKeys registry + basic vs enhanced logout consolidation + STAFF_REQUIRED_PATHS 2-of-3 phantom cleanup + `@authentication_classes([])` 3-file × 6-site stacking cleanup + dev/minimal PA routes (S2601 §17 DEAD-CANDIDATE handoff).

### Session count status

- Group 2500 API arc CLOSED at S2599 xx99 close 2026-07-06.
- Group 2400 Auth arc CLOSED at S2499 (prior arc).
- Group 2600 PA arc — 2-of-6 sessions shipped (S2600 parent scoping 2026-07-06 + S2601 Cat A 2026-07-06).
- **TWENTY-FIFTH consecutive dedicated fresh SIGN pin retirement** at S2601 close (Pin 2 `pa-767dddd95cb24099`) — cumulative across Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/S2401/S2402/S2403/S2404/S2499/S2500/S2501/S2502/S2503/S2504/S2599/S2600/S2601-Pin-1/S2601-Pin-2 twenty-four prior + 25th.
- SEVENTH-consecutive parent-with-4-children arc under Research OS (Groups 1900 + 2000+ + 2100 + 2200 + 2400 + 2500 + 2600 candidate) — MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails SEVENTH-consecutive extension.
- TWENTY-FIRST-consecutive playbook §11.2 20-section child-audit template application at S2601 (after 20 prior).
- **FIRST FULL 2-pin recovery pattern application under Research OS** at S2601 close per `feedback_rigby_sign_worker_instability_recovery.md` — prior applications recovered on Pin 1 without needing Pin 2.

## SESSION READY CHECK (before opening S2602 P2 Cat B child audit)

Before drafting Cat B shape card:

1. `tools/pa_local.sh "platform_config_tool action=overview"` → verify `service_context: local` + `railway_environment: local` + `database_name: unified_donkey_betz` + `default_llm_provider: openai` under active Group 2600 arc pin `pa-c17a8d7e0660413b`.
2. Read `docs/research/domains/pa/2600_pa_domain_scoping.md` fully — DIRECT PARENT.
3. Read `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` fully — SIBLING PRIOR-CHILD (Cat A) + §6.1 F11 canonical inventory + §7.2 streaming-negative + §14 verifier corrections + §16.1 F-B-HIGH-3 boundary.
4. Read `docs/research/domains/frontend/2202_frontend_api_client_surface_audit.md` — PARENT-arc Cat B predecessor + cockpitApi 96%-typed exemplar.
5. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 child audit template + §13 6-parallel-Explore-agent contract + §14 verifier-loop + §15 SIGN discipline + §16 arc-standard behavior + §21 short-command vocabulary.
6. **First execution step at S2602 open:** draft Cat B shape card 4-Q (Q1 consumer surface enumeration + Q2 lens inheritance from §2.6 + Q3 acceptance criteria for Cat B — U6/U7 evidence-gap closure turn 1 discipline + Q4 anti-scope inheritance). Route to Rigby SIGN-preview via arc pin `pa-c17a8d7e0660413b` (single-batch × 4-Q preview cadence).
7. Fold SIGN-preview edits.
8. Six-parallel-Explore-agent sweep per playbook §13 dispatched at S2602 open turn 2 (after shape-card ratification) — Agent 3 owns U6 WS envelope inventory + U7 paStore field-list dump.
9. Parent-Claude verifier-loop applied pre-draft per playbook §14 (S2601 pattern: 5 corrections at draft; preemptive).
10. Draft full Cat B child audit doc as `docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md` per playbook §11.2 template.
11. Route full audit to Rigby SIGN cycle 1 via dedicated fresh SIGN isolation pin (TWENTY-SIXTH consecutive candidate). **Preemptive: batch SIGN into 2-batch × 2-Q for doc >4k words** per `feedback_rigby_sign_worker_instability_recovery.md`.
12. Fold SIGN edits + retire SIGN pin.
13. Present Chris ratification card. Status flips `draft` → `active`.
14. Docs cascade + handoff + overwrite `00-START-NEXT-SESSION.md` with S2603 P3 Cat C priorities.

**S2602 arc-continue command (Chris short command):** `Continue research group 2600: S2602` or `Continue research group 2600: P2 Cat B client contract surface` per playbook §21 vocabulary + OS §3.2 deterministic route.
