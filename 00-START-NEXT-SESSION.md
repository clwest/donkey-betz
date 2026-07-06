# Next Session — Start Here

---

## READ THIS FIRST — S2600 P0 PARENT SCOPING COMMITTED + T3 GROUP 2600 PA ARC ACTIVE + S2601 P1 CAT A NEXT

**S2600 P0 Group 2600 PA parent scoping doc COMMITTED 2026-07-06.** Playbook §11.1 20-section parent-scoping template SEVENTH-consecutive-in-parent-with-4-children track application (after Groups 1900 + 2000+ + 2100 + 2200 + 2400 + 2500 six prior); THIRTEENTH-consecutive application overall. Chris short command "start research group 2600" 2026-07-06 matches OS §3.2 deterministic route + S2599 §8.2 T3 T-slot queue standing; no D-override invoked. Doc: `docs/research/domains/pa/2600_pa_domain_scoping.md` — 573 lines post-fold (9 shape-card + 4 SIGN cycle 1 folds baked). Chris "agree all" 2026-07-06 ratified 9 shape-card folds wholesale pre-drafting + Chris "commit it" 2026-07-06 ratified 4 SIGN cycle 1 STRENGTHEN folds at HIGH confidence via dedicated fresh SIGN pin `pa-499cc1897b0d4a3e` (retired at cycle close via `session_tool.retire force=true`; TWENTY-THIRD consecutive dedicated fresh SIGN pin retirement in Research OS). Arc pin `pa-c17a8d7e0660413b` PRESERVED through arc for arc-thread continuity per playbook §16.

**Group 2500 API arc CLOSED at S2599 xx99 2026-07-06.** Group 2600 PA arc OPENED at S2600 parent scoping 2026-07-06. **NEXT: S2601 P1 Cat A PA endpoint contract SoT declaration design-prep** per §5.1 child mission sequence.

### `tools/pa_local.sh:348` ROTATED at S2600 open to `pa-c17a8d7e0660413b`

`tools/pa_local.sh:348` `--conversation` value rotated from retired `pa-a03b111768464b3f` (Group 2500 API arc pin retired at S2599 xx99 close) → new Group 2600 arc pin `pa-c17a8d7e0660413b` at S2600 open turn 2. Header ledger updated with "Current value: Session 2600 arc pin" + S2600-open stanza + S2500-open/close historical stanzas preserved (chronological, newest first).

**S2601 P1 arc-open protocol:** `tools/pa_local.sh` invocation now routes to active Group 2600 arc pin. Verify `service_context: local` via `platform_config_tool overview` at S2601 open turn 1 before any Cat A audit work.

## READ THIS SECOND — S2601 P1 CAT A PA ENDPOINT CONTRACT SOT DECLARATION DESIGN-PREP QUEUED

**S2601 P1 is the NEXT child per §5.1 child mission sequence** in `docs/research/domains/pa/2600_pa_domain_scoping.md`. Focus:

- **PA endpoint contract SoT declaration disposition** per-endpoint recorded (Path A / Path B / Path C+island per F8 baseline).
- **10+ PA-path endpoints minimum** — extendable to N = all discovered at opening inventory:
  - `POST /api/pa/chat/` — CLAUDE.md canonical entry (F8 baseline attention); `core/views_personal_assistant.py:33-99`
  - `GET /api/pa/chat/status/<str:task_id>/` — async result polling
  - `GET /api/pa/context/` — assistant context extraction
  - `POST /api/assistant/chat/` (compat) — routes through `assistant_chat_bypass`
  - `GET /api/assistant/context/`, `preferences/`, `learning/`, `attention/unified/`
  - `POST /api/assistant/voice/` — voice-to-assistant transcription
  - `GET /api/v1/assistant/context/` (compat)
- **F11 denominator + inventory-table deliverable** at Cat A close: one-page PA-path endpoint inventory table (method + path + view + file:line + disposition column) used to compute AC#1 ≥90% coverage + verify denominator.
- **F8 baseline codification:** Cat A opening turn 1 MUST inventory whether `/api/pa/chat/` already has any documented OpenAPI operationId or schema declaration outside `@extend_schema` (docstring introspection / external OpenAPI YAML). If NONE exists, Path C-pure is strictly-worse relative to Path C+island.
- **F13 parallel evidence-collection permission:** Cat B (U6 WS envelope + U7 paStore field-list) + Cat D (PA-related WS channel inventory + Consumer class inventory) MAY collect inventory in parallel with Cat A opening (inventory-only, no option enumeration until Cat A verdict lands; decision-order A→B→C→D preserved).

**S2601 arc-open protocol:**
1. `tools/pa_local.sh "platform_config_tool action=overview"` → verify `service_context: local` + `railway_environment: local` + `database_name: unified_donkey_betz` + `default_llm_provider: openai` under active Group 2600 arc pin `pa-c17a8d7e0660413b`.
2. Read `docs/research/domains/pa/2600_pa_domain_scoping.md` fully — DIRECT PARENT for Cat A + §3.A Cat A scope + §5.3 AC#1 measurability threshold + §5.1 F13 parallel evidence-collection clause.
3. Read `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md` fully — PARENT-arc predecessor (CF-2600-PA origin + 30-endpoint sample methodology + 0-of-30 @extend_schema baseline).
4. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 child audit template + §21 short-command vocabulary + §13 sub-agent Explore contracts.
5. Read the 5 CF-* handed forward: CF-2600-PA (S2501 Cat A) + F-B-HIGH-3 (S2402 preserved through S2504) + Group 2500 Cat A verdict (which Path A/B/C ratified at platform-wide? — S2501 §14 or S2599 §8.1 P0-A execution row).
6. Draft Cat A shape-card 4-Q (Q1 endpoint slice enumeration + Q2 lens question inheritance + Q3 acceptance criteria per-endpoint recorded + Q4 anti-scope inheriting parent §7). Route to Rigby SIGN-preview via arc pin `pa-c17a8d7e0660413b` (single-batch × 4-Q preview cadence per S1899-S2600 NINE-consecutive-at-parent-scoping tested pattern; TENTH-consecutive-at-child-scoping candidate).
7. Fold SIGN-preview edits pre-drafting.
8. Draft full Cat A audit doc as `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` per playbook §11.2 20-section template.
9. Route full doc to Rigby SIGN cycle 1 via dedicated fresh SIGN isolation pin (TWENTY-FOURTH consecutive candidate) per playbook §15 SIGN-isolation discipline.
10. Fold SIGN edits + retire SIGN pin at close.
11. Present Chris ratification card. Status flips `draft` → `active` on ratification.

## READ THIS THIRD — S2600 PARENT SCOPING LOAD-BEARING OUTPUTS

**Parent scoping doc at `docs/research/domains/pa/2600_pa_domain_scoping.md`:**

- **§2.6 Central lens (F10 two-lens split):**
  - §2.6.A baseline inheritance constraint: PA inherits Group 2500 verdict unless overridden with justification + compensating controls.
  - §2.6.B PA delta-decision: Does /api/pa/chat/ (CLAUDE.md canonical entry) warrant stricter contract declaration than baseline; if so, at which boundary layer?
- **§3 4-child taxonomy (Option C ratified):**
  - Cat A (S2601) — PA endpoint contract SoT declaration design-prep; Path A/B/C+island axes; F8 baseline codification.
  - Cat B (S2602) — PA-client contract surface design-prep; F1 hard boundary (contract-typing + field-list ONLY); assistantApi.ts + paStore + tools/pa_chat.py; a/b/c typed island / SHAPE-BLIND / hybrid; U6+U7 evidence-gap closure turn 1.
  - Cat C (S2603) — PA workspace-context authz + session-lifecycle; F2 2 parallel sub-tracks C1 authz (F5 closure) + C2 lifecycle (α/β/γ inherit or PA-override).
  - Cat D (S2604) — REST↔WS T7 joint contract SoT dual-owner PA side; Path A/B/C strictness; Cat D γ mechanism-nesting applied at PA layer.
- **§5.3 8 acceptance criteria** (F4+F5+F6+F11+F12 folds applied): AC#1 ≥90% + denominator + inventory table / AC#2 T7 strictness / AC#3 F-B-HIGH-3 closure / AC#4 PA-client shape + U7 / AC#5 session-lifecycle + retention / AC#6 3 probes / AC#7 spec-only KEEP-BINDING / AC#8 T7 cross-transport consistency.
- **§7 10 anti-scope items** (F7 fold added #9 LLM provider/model + #10 agent timeout).
- **§8.1 Q1-Q4 shape card ratified** (Chris "agree all" 2026-07-06); **§8.2 9-fold shape-card record**; **§8.2b 4-fold SIGN cycle 1 record**; **§8.5 SIGN cycle 1 verdict HIGH confidence**.
- **§6 11 parked candidates** — P-1 PA voice/TTS contract / P-2 PA telemetry envelope Group 1700 handoff / P-3 PA 3-way chat UX (NON-CANDIDATE per F1) / P-4 PA async task lifecycle Celery / P-5 Fleet PA federation / P-6 prompt engineering / P-7 memory Group 1300 / P-8 LLM provider (F7) / P-9 agent timeout (F7) / P-10 Discord PA / P-11 PA content-scoring.
- **§4 runtime target 6 sessions; runtime cap 8** with 2 explicit trigger conditions (Cat A >20 endpoints or Cat D >10 WS channel variations).

## READ THIS FOURTH — LOAD-BEARING INPUTS FOR NEXT SESSION

**S2601 P1 Cat A arc-open must consume:**
- `docs/research/domains/pa/2600_pa_domain_scoping.md` (S2600 parent scoping — DIRECT PARENT + §3.A Cat A scope + §5.3 AC + §5.1 F13 parallel evidence-collection clause + §2.6 central lens)
- `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md` (S2501 Cat A — PARENT-arc predecessor + CF-2600-PA origin + PA-path endpoint 0/30 @extend_schema evidence + 30-endpoint sample methodology)
- `docs/research/domains/api/2599_api_canonical_summary.md` (S2599 xx99 — Group 2500 API canonical verdict inheritance + §8.2 T-slot queue advance record)
- `docs/research/domains/auth/2402_auth_permission_floor_uniformity_audit.md` (S2402 — F-B-HIGH-3 workspace-membership implicit-gate origin for Cat C1 handoff — not S2601 primary but forward reference)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 child audit template + §14 evidence rules + §15 SIGN cadence + §16 draft-first workflow + §13 sub-agent Explore contracts

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2600 close residuals — post-parent-scoping docs cascade PR

Per Chris "commit it" ratification at S2600 close 2026-07-06:

- **Post-commit docs cascade PR** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Verify final chunk count + provenance-json refresh in PR body.

- **ARCHITECTURE_INDEX.md + OPEN_ARCS.md deferred anchor cascade** (extends S2599 xx99 close deferrals):
  - **AU-4** ARCHITECTURE_INDEX §1.98 S2600 backfill (Group 2600 PA parent scoping registration) + v93 → v94 version bump.
  - **AU-5** ARCHITECTURE_INDEX §8 timeline: 1 row added (S2600 parent scoping).
  - **AU-6** ARCHITECTURE_INDEX §3 domain map PA row update: OPENED as new domain (or check if pa/ existed prior — first row at Group 2600).
  - **AU-9** ARCHITECTURE_INDEX §9 roadmap T-slot queue advance: T3 Group 2600 PA (NOW IN-PROGRESS) → T4 Group 1700 Observability (NEXT) → T5 Group 2300 Mobile (parallel) → T6 Group 1600 Content per S2599 §8.2 xx99 canonical summary.
  - **OPEN_ARCS.md** Group 2500 API row already transitioned In-progress → Closed at this session; Group 2600 PA row already added to In-progress at this session.

- **Deep anchor-update items deferred from S2599** (still pending):
  - **AU-1** PLATFORM_INVENTORY §API autoblock CREATE (with Cat D §1.1 D1-D6 Denominator Contract per Rigby Q2 fold; generator extends `gather_inventory()` per S2499 precedent).
  - **AU-3** PLATFORM_WHAT_IT_IS §API narrative subsection CREATE.
  - **AU-10** `docs/topics/api.md` CREATE (analog to `docs/topics/auth.md` per S2499 AU-D2 + AU-D7).
  - **AU-11** `platform_architecture_inventory.md` §3.22 API Layer REVISE.
  - **AU-12** CODEOWNERS cockpit surface refinement deferred to S2601+ per CODEOWNERS lines 8-13 explicit deferral.

### Group 2400 + Group 2500 post-arc remediation queue (unchanged carry into S2601)

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

### T-slot follow-on queue (post-Group-2600-close forward look)

- **T3 Group 2600 PA** — **NOW IN-PROGRESS** at parent scoping S2600 (2026-07-06). Runtime target 6 sessions per parent §4.
- **T4 Group 1700 Observability cross-arc handoff bundle** — QUEUED after Group 2600 close. Consumes CF-D6 secondary stakeholder from S2504 Q9 fold + F-D-CALL-1 803-scale observability implications.
- **T5 Group 2300 Mobile (parallel)** — QUEUED after Group 2600 close. CF-D4 + CF-C4 + Cat A CF-4 + Cat D CF-D6 secondary stakeholder — parallel silent-401 audit for mobile app.
- **T6 Group 1600 Content** — QUEUED after Group 2600 close per Cat C S2503 Rigby SIGN Q11 fold CF-C8.
- **Maintainer-decision batch** — CODEOWNERS API-slice discipline + DEAD-CANDIDATE consolidated cleanup (18 modules verified zero-consumer at S2502) + api.ts extraction execution + storageKeys registry + basic vs enhanced logout consolidation + STAFF_REQUIRED_PATHS 2-of-3 phantom cleanup + `@authentication_classes([])` 3-file × 6-site stacking cleanup.

### Session count status

- Group 2500 API arc CLOSED at S2599 xx99 close 2026-07-06.
- Group 2400 Auth arc CLOSED at S2499 (prior arc).
- Group 2600 PA arc OPENED at S2600 parent scoping 2026-07-06 (1 of 6 sessions shipped).
- THIRTEENTH formal arc pin under Research OS (`pa-c17a8d7e0660413b`) — after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200/2400/2500 twelve prior.
- TWENTY-THIRD consecutive dedicated fresh SIGN pin retirement at S2600 close (SIGN pin `pa-499cc1897b0d4a3e`).
- SEVENTH-consecutive parent-with-4-children arc under Research OS (Groups 1900 + 2000+ + 2100 + 2200 + 2400 + 2500 + 2600 candidate) — MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails SEVENTH-consecutive extension candidate.
- SEVENTH-consecutive-in-parent-with-4-children track playbook §11.1 template application at S2600 (after Groups 1900+2000++2100+2200+2400+2500 six prior); THIRTEENTH-consecutive playbook §11.1 application overall.
- NINTH-consecutive-at-parent-scoping single-batch × 4-Q Rigby SIGN cadence application at S2600 (after S1499 + S1899 + S1999 + S2099 + S2199 + S2299 + S2400 + S2500 eight prior).

## SESSION READY CHECK (before opening S2601 P1 Cat A child audit)

Before drafting Cat A shape card:

1. `tools/pa_local.sh "platform_config_tool action=overview"` → verify `service_context: local` + `railway_environment: local` + `database_name: unified_donkey_betz` + `default_llm_provider: openai` under active Group 2600 arc pin `pa-c17a8d7e0660413b`.
2. Read `docs/research/domains/pa/2600_pa_domain_scoping.md` fully — DIRECT PARENT.
3. Read `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md` fully — PARENT-arc Cat A predecessor + 30-endpoint sample methodology.
4. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 child audit template + §21 short commands + §13 Explore sub-agent contracts.
5. **First execution step at S2601 open:** draft Cat A shape card 4-Q (Q1 endpoint slice enumeration reaffirmation + Q2 lens inheritance from §2.6 + Q3 acceptance criteria for Cat A + Q4 anti-scope inheritance). Route to Rigby SIGN-preview via arc pin `pa-c17a8d7e0660413b` (single-batch × 4-Q preview cadence).
6. Fold SIGN-preview edits.
7. Draft full Cat A child audit doc as `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` per playbook §11.2 template.
8. Deliverable at Cat A close: **one-page PA-path endpoint inventory table** per F11 fold (method + path + view + file:line + disposition column) used to compute AC#1 ≥90% + verify denominator.
9. Route full audit to Rigby SIGN cycle 1 via dedicated fresh SIGN isolation pin (TWENTY-FOURTH consecutive candidate).
10. Fold SIGN edits + retire SIGN pin.
11. Present Chris ratification card. Status flips `draft` → `active`.
12. Docs cascade + handoff + overwrite `00-START-NEXT-SESSION.md` with S2602 P2 Cat B priorities.

**S2601 arc-continue command (Chris short command):** `Continue research group 2600: S2601` or `Continue research group 2600: P1 Cat A endpoint contract SoT` per playbook §21 vocabulary + OS §3.2 deterministic route.
