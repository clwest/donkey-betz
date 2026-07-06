# Next Session — Start Here

---

## READ THIS FIRST — S2603 P3 CAT C COMMITTED + T3 GROUP 2600 PA ARC 4-OF-6 SHIPPED + S2604 P4 CAT D NEXT

**S2603 P3 Cat C PA Workspace-Context Authz + Session-Lifecycle Design-Prep child audit COMMITTED 2026-07-06.** Playbook §11.2 20-section child-audit template TWENTY-THIRD-consecutive application (after S1301/S1401/S1501/S1601/S1701/S1801/S1901/S2001/S2101/S2102/S2103/S2104/S2201/S2202/S2203/S2204/S2401/S2402/S2403/S2404/S2501/S2601/S2602 twenty-two prior). Doc: `docs/research/domains/pa/2603_pa_workspace_authz_session_lifecycle_design_prep_audit.md` — 1001 lines / ~16k words post-fold (5 SIGN cycle 1 STRENGTHEN folds F-C3/F-C4/F-C5/F-C6/F-C7 + 2 new DEBT items DEBT-C1-7/DEBT-C1-8 + §7.2 fails-closed clarifier + §7.2 workspace_id provenance enumeration + §19.1 CRITICAL research follow-on baked). Chris "agree all" 2026-07-06 ratified 2 shape-card SIGN-preview folds (F-C1 + F-C2) wholesale pre-drafting + Chris "agree all" 2026-07-06 ratified 5 SIGN cycle 1 STRENGTHEN folds (F-C3 through F-C7) + 2 new DEBT items + clarifiers via **SINGLE-PIN close pattern** (2-pin recovery NOT required — preemptive 2-batch × 2-Q batching from turn 1 prevented worker instability). Pin `pa-9f37a2818961487f` TWENTY-SEVENTH consecutive dedicated fresh SIGN pin retirement — Batch 1 (Q1+Q2 coverage+maturity) HIGH confidence with F-C3+F-C4+F-C5 STRENGTHEN + Batch 2 (Q3+Q4 debt+boundary) HIGH confidence with F-C6+F-C7 STRENGTHEN + retired 1 row. Cycle 2 NOT required. Arc pin `pa-c17a8d7e0660413b` PRESERVED through S2603.

**Group 2600 PA arc 4-of-6 sessions shipped** (S2600 parent scoping + S2601 Cat A + S2602 Cat B + S2603 Cat C). **NEXT: S2604 P4 Cat D REST↔WS T7 joint dual-owner PA side** per §5.1 child mission sequence.

### `tools/pa_local.sh:348` UNCHANGED at S2603 close — arc pin PRESERVED

`tools/pa_local.sh:348` `--conversation` value UNCHANGED at S2603 close — arc pin `pa-c17a8d7e0660413b` continues to route all Claude Code → Rigby chatter through the Group 2600 PA arc pin per playbook §16 arc-standard behavior (no rotation until arc close at S2699 xx99).

**S2604 P4 arc-continue protocol:** `tools/pa_local.sh` invocation continues to route to active Group 2600 arc pin. Verify `service_context: local` via `platform_config_tool overview` at S2604 open turn 1 before any Cat D audit work.

## READ THIS SECOND — S2604 P4 CAT D REST↔WS T7 JOINT DUAL-OWNER PA SIDE QUEUED

**S2604 P4 is the NEXT child per §5.1 child mission sequence** in `docs/research/domains/pa/2600_pa_domain_scoping.md`. Focus: PA REST↔WS T7 joint contract SoT (dual-owner PA side). Apply Group 2500 Cat D γ mechanism-nesting decision at PA layer.

### Scope

- PA-related WS channels (subset of platform 120 total per S2504 baseline):
  - Chat-response streaming (token-by-token delivery from PA agent loop).
  - Task-status broadcast (async PA task completion + tool-run updates).
  - Async-audio-url delivery (voice-response TTS URL push — S2602 §6.3 F-B3 re-labeled from "async-audio-url delivery WS" to "REST-embedded" per verifier-loop; verify at S2604 opening).
  - Any PA-related consumer classes among the 87 platform total (Cat D S2604 opening inventory).
- Cat B §6.2 F-B3 U6 baseline: 1 PA-client WS channel + 3 canonical message classes (message.created / agent.completed / rigby.tool.* lifecycle) — envelope grade `observed-JSON-only` at HEAD.
- Cat C §7.2 AC-C1-4 T7 REST-side statement: "PA REST-side workspace-context enforcement is handler-internal implicit-gate at `execute_with_workspace()`; WS-side enforcement is UNKNOWN pending Cat D S2604 evidence."

### Chris-D-verdict axes

- **Path A** — Typed WS envelope schema at all PA-related consumers (TypedDict / Protocol / BaseModel — U6 evidence-gap resolution required first at Cat B opening, closed by Cat B §6.2 F-B3 evidence).
- **Path B** — Envelope declared at CONNECT handshake only; message-shape SoT-declared but non-enforced (island-declaration on connect, SHAPE-BLIND on message payload).
- **Path C** — WS message-contract SoT-declared for all PA-related channels; streaming exception carve-out for chat-response (streaming tokens explicitly non-conformant + documented).

### Cat A + Cat B + Cat C inheritance for S2604

Cat A inheritance (S2601):
- §6.1 F11 canonical PA-path endpoint inventory (34 endpoints) — AC-A2 canonical artifact; DO NOT re-inventory.
- §7.2 REST-side "task-based async, NO streaming" statement — Cat A canonical evidence for AC#8 F12 T7 cross-transport consistency check.

Cat B inheritance (S2602):
- §6.2 F-B3 U6 WS envelope inventory: 1 PA-client channel + 3 canonical classes — AC-B3 canonical artifact for U6 evidence-gap closure.
- §6.3 F-B3 REST-embedded async-audio-url observation — Cat D S2604 Path A/B/C verdict scope.
- §15.2 CF-D6 REST↔WS T7 joint contract SoT coordination debt.

Cat C inheritance (S2603):
- §7.2 AC-C1-4 T7 REST-side statement: "REST-side workspace-context enforcement is handler-internal implicit-gate; WS-side UNKNOWN pending Cat D S2604 evidence."
- §16.1 F5 fold hard "INVALID" language for Path C-pure (analog constraint may apply to Cat D S2604 if coupling evidence surfaces).

### Cross-arc coordination

- **CF-D6** dual-owner: Group 2500 side owned by S2504 arc-close design-prep; Group 2600 side owned by S2604 PA-slice application.
- **Secondary stakeholders:** Group 1700 Observability (envelope-shape telemetry + per-endpoint compliance metrics) + Group 2300 Mobile (parallel arc, secondary stakeholder — client interception at mobile PA client inherits from Cat D verdict).

**S2604 arc-open protocol:**
1. `tools/pa_local.sh "platform_config_tool action=overview"` → verify `service_context: local` + `railway_environment: local` + `database_name: unified_donkey_betz` + `default_llm_provider: openai` under active Group 2600 arc pin `pa-c17a8d7e0660413b`.
2. Read `docs/research/domains/pa/2600_pa_domain_scoping.md` fully — DIRECT PARENT for Cat D + §3.D scope + §5.3 AC + §2.5 evidence gaps.
3. Read `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` — SIBLING PRIOR-CHILD Cat A (§6.1 F11 canonical inventory + §7.2 REST-side task-based-async statement).
4. Read `docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md` — SIBLING PRIOR-CHILD Cat B (§6.2 F-B3 U6 WS envelope inventory + §6.3 F-B3 REST-embedded async-audio-url + §15.2 CF-D6 coordination debt).
5. Read `docs/research/domains/pa/2603_pa_workspace_authz_session_lifecycle_design_prep_audit.md` — SIBLING PRIOR-CHILD Cat C (§7.2 AC-C1-4 T7 REST-side statement + §16.1 F5 fold analog).
6. Read `docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md` — CF-D6 ORIGIN (Cat D side of dual-owner).
7. Read `docs/research/domains/api/2599_api_canonical_summary.md` — Group 2500 API canonical verdict inheritance + Cat D γ mechanism-nesting decision.
8. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 child audit template + §21 short-command vocabulary + §13 sub-agent Explore contracts + §14 verifier-loop discipline + §15 SIGN-isolation.
9. Draft Cat D shape-card 4-Q (Q1 Path A/B/C axes for PA WS envelope strictness + Q2 REST↔WS T7 cross-transport consistency lens + Q3 acceptance criteria for Cat D + Q4 anti-scope inheritance). Route to Rigby SIGN-preview via arc pin `pa-c17a8d7e0660413b` (single-batch × 4-Q preview cadence per S1899-S2603 TWELVE-consecutive tested pattern; THIRTEENTH-consecutive-at-child-scoping candidate).
10. Fold SIGN-preview edits pre-drafting.
11. Draft full Cat D audit doc as `docs/research/domains/pa/2604_pa_rest_ws_t7_joint_dual_owner_design_prep_audit.md` per playbook §11.2 20-section template.
12. Route full doc to Rigby SIGN cycle 1 via dedicated fresh SIGN isolation pin (TWENTY-EIGHTH consecutive candidate) per playbook §15 SIGN-isolation discipline. Preemptive: batch SIGN into 2-batch × 2-Q per S2602 + S2603 SUCCESS pattern per `feedback_rigby_sign_worker_instability_recovery.md`.
13. Fold SIGN edits + retire SIGN pin at close.
14. Present Chris ratification card. Status flips `draft` → `active` on ratification.

## READ THIS THIRD — S2603 CAT C LOAD-BEARING OUTPUTS

**Cat C audit doc at `docs/research/domains/pa/2603_pa_workspace_authz_session_lifecycle_design_prep_audit.md`:**

- **§6.1 F-C3 workspace-touching subset rule** (Rigby SIGN Batch 1 fold ratified 2026-07-06): "touches workspace iff calls WorkspaceManager.get_active_workspace OR dispatches an agent in WORKSPACE_AWARE_AGENTS OR reads/writes ProjectWorkspace-bound models." Makes ~8-12 INDIRECT bucket auditable at xx99.
- **§6.1 C1 workspace-scoped-data-touching subset:** 1 DIRECT (`/api/pa/chat/` row 16) + ~8-12 INDIRECT + ~14 NO touch + 4 UNKNOWN (dev/minimal per Cat A §14 gap). C1 denominator locked.
- **§7.2 REST-side C1 statement + §7.2 fails-closed clarifier** (Rigby SIGN Batch 1 Q2a): execute_with_workspace() returns structured error dict on failure; NO silent-degrade fallback. workspace_id 5-source provenance enumerated (DEBT-C1-8).
- **§8.4 U7 canonical inheritance** (Cat B §4.1 F-B4): paStore 16 fields, 5 syncUser-wiped, 2 UNKNOWN intent (isDockOpen, isDockMinimized), 9 non-wiped. 2 UNKNOWN → AC-C2-4 verdict scope.
- **§8.7 retention window fragmented across 6 declaration points** (5 partial + 1 UNDECLARED); 24-hour lookback hardcoded at `get_or_create_session()` line 212 is mechanism constant (F-C5), NOT policy declaration.
- **§8.8 F-C4 PA-produced outputs retention-impact surfaces**: Deliverable + Blog + DocumentEmbedding + ToolCallRecord — inherited consequence of Cat C2 verdict.
- **§13 maturity:** Both C1 + C2 PARTIAL — MECHANISM WORKING + DECLARATION EXPERIMENTAL.
- **§14 4 verifier corrections + §14.2 4 confirmed drifts (D1-D5) + §14.3 verify_doc_claims 0 C1/C2 claims.**
- **§15.1 8 debt items C1 (DEBT-C1-1..8, including F-C6 severity rubric)** + **§15.2 8 debt items C2 (DEBT-C2-1..8, including F-C6 verdict-scope governance gap framing).**
- **§16.1 F5 discipline INVALID hard language (F-C7):** Path C-pure "fails closure and must be recorded as rejected / non-ratifiable."
- **§16.4 Cat-C-1..9 micro-anti-scope enumeration** (ID-stable per F-B9 precedent).
- **§20.6 SIGN cycle 1 fold record (5 folds + 2 new DEBT items + clarifiers baked).**

## READ THIS FOURTH — LOAD-BEARING INPUTS FOR NEXT SESSION

**S2604 P4 Cat D arc-open must consume:**
- `docs/research/domains/pa/2600_pa_domain_scoping.md` (S2600 parent scoping — DIRECT PARENT + §3.D + §5.3 AC + §2.5 evidence gaps)
- `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` (S2601 Cat A — §6.1 F11 canonical inventory + §7.2 REST-side task-based-async)
- `docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md` (S2602 Cat B — §6.2 F-B3 U6 WS envelope inventory + §6.3 F-B3 REST-embedded async-audio-url + §15.2 CF-D6 debt)
- `docs/research/domains/pa/2603_pa_workspace_authz_session_lifecycle_design_prep_audit.md` (S2603 Cat C — §7.2 AC-C1-4 T7 REST-side statement + §16.1 F5 fold analog)
- `docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md` (CF-D6 ORIGIN + 285-entry path-list gate + WS Consumer class inventory)
- `docs/research/domains/api/2599_api_canonical_summary.md` (Group 2500 canonical verdict + Cat D γ mechanism-nesting)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 + §13 + §14 + §15 + §16 + §21

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2603 close residuals — post-Cat-C-audit docs cascade PR

Per Chris "agree all" ratification at S2603 close 2026-07-06:

- **Post-commit docs cascade PR** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Verify final chunk count + provenance-json refresh in PR body.

- **ARCHITECTURE_INDEX.md + OPEN_ARCS.md deferred anchor cascade** (extends S2600 + S2601 + S2602 close deferrals):
  - **AU-11** ARCHITECTURE_INDEX §1.NN S2603 backfill (Group 2600 PA Cat C child audit registration) + v-bump.
  - **AU-12** ARCHITECTURE_INDEX §8 timeline: 1 row added (S2603 Cat C).
  - **AU-13** ARCHITECTURE_INDEX §3 domain map PA row: Cat C closed at S2603; 1-of-4 children remaining.
  - **AU-14** ARCHITECTURE_INDEX §9 roadmap T-slot queue advance: unchanged.
  - **OPEN_ARCS.md** Group 2600 PA row S2603 child-registration update (in-progress → 4-of-6 sessions shipped).

- **Cat C new anchor-update candidates for S2699 xx99:**
  - **AU-C1** PLATFORM_INVENTORY §Agents autoblock EXTEND (WORKSPACE_AWARE_AGENTS 20-count row addition — Rigby SIGN Batch 1 highlighted absence).
  - **AU-C2** `docs/topics/personal-assistant.md` §Workspace-enforcement subsection SPEC (Path C+compensating requirement per parent §5.3 AC#3; Cat C spec-only per Cat-C-9 anti-scope).
  - **AU-C3** `docs/topics/personal-assistant.md` §Session-lifecycle subsection SPEC (C2 verdict-scope; content depends on α/β/γ/PA-override selection at xx99).
  - **AU-C4** `docs/PLATFORM_WHAT_IT_IS.md` PA subsection audit-trail claim reconciliation (Cat C §14.2 D3 new drift; either drift-fix OR Path C+compensating spec fulfillment).
  - **AU-C5** `docs/decisions/ADR-NN-workspace-context-authorization-boundary.md` CREATE (Path C+compensating requirement (ii) per parent §5.3 AC#3; Cat C spec-only per Cat-C-9 anti-scope).

- **Deep anchor-update items deferred from S2599 + S2600 + S2601 + S2602** (still pending — carried forward):
  - AU-1/AU-3/AU-10/AU-11/AU-12 (Group 2500 API arc close residuals) + AU-B1/AU-B2/AU-B3/AU-B4 (S2602 Cat B close residuals).

### Group 2400 + Group 2500 post-arc remediation queue (unchanged carry into S2604)

**P0-A platform-wide (S2599 xx99 execution scope carry):**
- AU-U1 Route→view normalization pass to compute D4 unique-view denominator.
- F-D-CALL-1 803-scale silent-401 remediation.
- F-D-BYPASS-1 79-raw-fetch bypass reconciliation.
- F-D-ENVELOPE-1 typed-error-envelope execution.
- F-D-BOUNDARY-1 error-boundary framework establishment.

**P0-B token lifecycle / security window (unchanged):**
- F-D-SIDEBAR-1, F-C-REFRESH-1, F-C-VIP-1, F-C-CSD-1, F-C-STORE-1.

**P0-C endpoint-specific (unchanged):**
- F-CRIT-1, F-BND-4a, F-B-CRIT-1, F-B-CRIT-2, F-D-WHITELIST-1, F-D-REGISTRY-1, F-D-WSENVELOPE-1.

### T-slot follow-on queue (post-Group-2600-close forward look — unchanged)

- **T3 Group 2600 PA** — **IN-PROGRESS**, 4-of-6 sessions shipped (S2600 parent scoping + S2601 Cat A + S2602 Cat B + S2603 Cat C).
- **T4 Group 1700 Observability** — QUEUED after Group 2600 close.
- **T5 Group 2300 Mobile (parallel)** — QUEUED after Group 2600 close.
- **T6 Group 1600 Content** — QUEUED after Group 2600 close per Cat C S2503 Rigby SIGN Q11 fold CF-C8.
- **Maintainer-decision batch** (unchanged carry).

### Session count status

- Group 2500 API arc CLOSED at S2599 xx99 close 2026-07-06.
- Group 2400 Auth arc CLOSED at S2499 (prior arc).
- Group 2600 PA arc — **4-of-6 sessions shipped** (S2600 parent scoping 2026-07-06 + S2601 Cat A 2026-07-06 + S2602 Cat B 2026-07-06 + S2603 Cat C 2026-07-06).
- **TWENTY-SEVENTH consecutive dedicated fresh SIGN pin retirement** at S2603 close (Pin `pa-9f37a2818961487f`).
- SEVENTH-consecutive parent-with-4-children arc under Research OS — MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails SEVENTH-consecutive extension.
- **TWENTY-THIRD-consecutive playbook §11.2 20-section child-audit template application** at S2603 (after 22 prior).
- **SECOND SINGLE-PIN close in Group 2600 PA arc** — S2601 Cat A required 2-pin recovery (8,729 words + turn-3 worker instability); S2602 Cat B (10,689 words) closed with 1 pin via preemptive 2-batch × 2-Q batching from turn 1; S2603 Cat C (~16k words) closed with 1 pin via same preemptive 2-batch × 2-Q batching. Recovery pattern preserved as fallback per `feedback_rigby_sign_worker_instability_recovery.md`; single-pin close is preferred when preemptive batching is applied from the start.

## SESSION READY CHECK (before opening S2604 P4 Cat D child audit)

Before drafting Cat D shape card:

1. `tools/pa_local.sh "platform_config_tool action=overview"` → verify `service_context: local` + `railway_environment: local` + `database_name: unified_donkey_betz` + `default_llm_provider: openai` under active Group 2600 arc pin `pa-c17a8d7e0660413b`.
2. Read `docs/research/domains/pa/2600_pa_domain_scoping.md` fully — DIRECT PARENT.
3. Read `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` — SIBLING Cat A (§6.1 F11 + §7.2 REST-side task-based-async).
4. Read `docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md` — SIBLING Cat B (§6.2 F-B3 U6 WS envelope inventory + §6.3 F-B3 REST-embedded async-audio-url + §15.2 CF-D6 debt).
5. Read `docs/research/domains/pa/2603_pa_workspace_authz_session_lifecycle_design_prep_audit.md` — SIBLING Cat C (§7.2 AC-C1-4 T7 REST-side statement + §16.1 F5 fold analog).
6. Read `docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md` — CF-D6 ORIGIN.
7. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 + §13 + §14 + §15 + §16 + §21.
8. **First execution step at S2604 open:** draft Cat D shape card 4-Q (Q1 Path A/B/C axes for PA WS envelope strictness + Q2 REST↔WS T7 cross-transport consistency lens + Q3 AC set + Q4 anti-scope inheritance). Route to Rigby SIGN-preview via arc pin `pa-c17a8d7e0660413b`.
9. Fold SIGN-preview edits.
10. Six-parallel-Explore-agent sweep per playbook §13 dispatched at S2604 open turn 2 (after shape-card ratification).
11. Parent-Claude verifier-loop applied pre-draft per playbook §14 (S2601 5-corrections + S2602 7-corrections + S2603 4-corrections precedent).
12. Draft full Cat D child audit doc as `docs/research/domains/pa/2604_pa_rest_ws_t7_joint_dual_owner_design_prep_audit.md` per playbook §11.2 template.
13. Route full audit to Rigby SIGN cycle 1 via dedicated fresh SIGN isolation pin (TWENTY-EIGHTH consecutive candidate). **Preemptive: batch SIGN into 2-batch × 2-Q per S2602 + S2603 SUCCESS pattern** per `feedback_rigby_sign_worker_instability_recovery.md`.
14. Fold SIGN edits + retire SIGN pin.
15. Present Chris ratification card. Status flips `draft` → `active`.
16. Docs cascade + handoff + overwrite `00-START-NEXT-SESSION.md` with S2699 xx99 canonical summary priorities.

**S2604 arc-continue command (Chris short command):** `Continue research group 2600: S2604` or `Continue research group 2600: P4 Cat D REST↔WS T7 joint` per playbook §21 vocabulary + OS §3.2 deterministic route.
