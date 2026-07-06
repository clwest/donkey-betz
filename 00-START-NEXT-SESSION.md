# Next Session — Start Here

---

## READ THIS FIRST — S2599 XX99 CLOSED + GROUP 2500 API ARC CLOSED + T3 GROUP 2600 PA QUEUED

**S2599 xx99 Group 2500 API canonical summary CLOSED 2026-07-06.** Rigby SIGN cycle 1 COMPLETE via dedicated fresh SIGN isolation pin `pa-59d9583dc4da4d5e` — **TWENTY-SECOND consecutive dedicated fresh SIGN pin retirement** under Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/S2401/S2402/S2403/S2404/S2499/S2500/S2501/S2502/S2503/S2504 twenty-one prior. Chris "commit it" 2026-07-06 ratified 5 folds wholesale — status flipped `draft` → `active`. **Arc pin `pa-a03b111768464b3f` RETIRED at close via `session_tool.retire force=true` — TWELFTH formal arc-pin retirement in Research OS.** Runtime target 6 sessions ACHIEVED — 6/6 = 100%; SIXTH-consecutive parent-with-4-children arc close — MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails extended.

**Group 2500 API arc CLOSED.** Group 2400 Auth arc closed at S2499; Group 2500 API closes at S2599; T3 Group 2600 PA is NEXT per T-slot queue.

### CRITICAL: `tools/pa_local.sh:312` STILL POINTS at RETIRED pin

`tools/pa_local.sh` header ledger (line 56ff) updated with S2500 arc retirement stanza at S2599 close 2026-07-06. **Wrapper hard-code at line 312 STILL POINTS at retired pin `pa-a03b111768464b3f`** per S2500 parent scoping deferral + S1700 → S1800 open precedent (documented at the retired-S1800 stanza in `tools/pa_local.sh` header).

**Group 2600 PA arc-open session MUST rotate `tools/pa_local.sh:312` at open before ANY further work.** Any bare invocation of `tools/pa_local.sh` after retirement will route to a retired pin and fail. Fresh Group 2600 arc pin to be minted at arc-open via `session_tool action=create_fresh`.

## READ THIS SECOND — T3 GROUP 2600 PA CROSS-ARC HANDOFF BUNDLE QUEUED

**T3 Group 2600 PA is the NEXT arc per §8.2 T-slot queue** in `docs/research/domains/api/2599_api_canonical_summary.md`. Consumes: 4 CF-* originated S2501-S2504:

- **CF-2600-PA** (S2501 Cat A origin) — `/api/pa/chat/` + `/api/assistant/*` endpoints declare NO contract SoT at HEAD; workspace-context authz declared implicitly only.
- **CF-D6** (S2504 Cat D origin) — REST↔WS T7 joint contract SoT dual-owned Group 2500 API + Group 2600 PA. Secondary stakeholders: Group 1700 Observability + Group 2300 Mobile.
- **PA endpoint DECLARATION** — Cat A §3 evidence at `core/views_personal_assistant.py:31-99` (0 @extend_schema decorators) + `core/views_workspace_api.py` (PA endpoints).
- **Workspace-context authz** — Cat D §14 evidence.

Group 2600 arc-open protocol:
1. Mint fresh Group 2600 arc pin via `session_tool action=create_fresh` title="Group 2600 PA arc pin (S2600 open)".
2. Rotate `tools/pa_local.sh:312` from retired `pa-a03b111768464b3f` to new arc pin.
3. Update `tools/pa_local.sh` header ledger with S2500 retirement stanza + S2600 open stanza per S2000/S2100/S2200/S2400/S2500 documentation pattern.
4. Read `docs/research/domains/api/2599_api_canonical_summary.md` fully — DIRECT PREDECESSOR input for Group 2600 PA arc.
5. Read `docs/research/domains/auth/2499_auth_canonical_summary.md` fully — prior-prior arc close model.
6. Read the 4 handed-forward CF-* flags in detail.
7. Draft Group 2600 PA parent scoping doc per playbook §11.1.

## READ THIS THIRD — S2599 XX99 CANONICAL SUMMARY LOAD-BEARING OUTPUTS

**xx99 canonical summary shipped at `docs/research/domains/api/2599_api_canonical_summary.md`:**

- **§1 Executive Summary** — Central lens question answered. Canonical verdict: "MECHANISM working at file-precision + DECLARATION SoT absent or non-uniform across all four contract axes; majority IMPLICIT-INHERITANCE with ISLAND-DECLARATION pockets + ZERO cross-transport SoT; gap is design-plane governance, not runtime failure."
- **§3 Consolidated Domain Shape** — 4-plane ASCII stack (Backend DECLARATION / Wire CONTRACT / Consumer DECLARATION / Permission-floor + REST↔WS) + 30+ row consolidated numerical summary.
- **§4 Six cross-cutting patterns** — declared-but-unenforced / SHAPE-BLIND consumer surface / greenfield governance layers / fragmentation across parallel layers / boundary discipline preservation / CF-* propagation.
- **§5 Four resolved contradictions** — URL pattern drift; route-indexed 49% vs view-inheritance ~84.4% under D1-D6 Denominator Contract; taxonomy Cat C Family A/B/C/D adopted over Cat A shape (a)/(b)/(c)/(d); F-B-HIGH-2 S2402 origin attribution; two-sided SHAPE-BLIND-vs-permission-floor framing preserved.
- **§6 Eight unresolved unknowns** — U1 D4 unique-view denominator + U2 drf-spectacular feasibility + U3 refresh semantics + U4 CSD header value spec + U5 cross-tab logout propagation intent + U6 WS envelope-schema type + U7 paStore field-list completeness + U8 79-raw-fetch per-site classification.
- **§7 Fourteen anchor-update recommendations** — AU-1 PLATFORM_INVENTORY §API autoblock + AU-3 PLATFORM_WHAT_IT_IS §API narrative + AU-4/5/6/7/8/9 ARCHITECTURE_INDEX §1.93-97 + §8 timeline + §3 domain map + §5 gap + §7 decision matrix + §9 roadmap + AU-10 docs/topics/api.md CREATE + AU-11 platform_architecture_inventory.md §3.22 REVISE + AU-12 CODEOWNERS cockpit refinement + AU-13 OPEN_ARCS transition + AU-14 pa_local.sh ledger (S2500 retirement stanza ADDED this session).
- **§8 Follow-on research queue** — P0-A + P0-B + P0-C rank-1 co-equal batch preserved; T3→T4→T5→T6 T-slot queue; Rank-3 post-arc ADR candidates.
- **§10 Meta-methodology retrospective** — TWELFTH-consecutive §11.3 §10 5-subsection application (what worked / v3 codification candidates / anti-patterns / playbook suggestions / future canonical summary suggestions).

## READ THIS FOURTH — LOAD-BEARING INPUTS FOR NEXT SESSION

**Group 2600 PA arc-open must consume:**
- `docs/research/domains/api/2599_api_canonical_summary.md` (S2599 xx99 close — DIRECT PREDECESSOR + arc-close canonical verdict)
- `docs/research/domains/api/2500_api_domain_scoping.md` (S2500 parent scoping — §3.5 API-adjacent probes disposition + §6 P-1 through P-11 parked items + §7 anti-scope)
- `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md` (S2501 Cat A — CF-2600-PA origin + `/api/pa/chat/` + `/api/assistant/*` PA endpoint DECLARATION side)
- `docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md` (S2504 Cat D — CF-D6 REST↔WS T7 joint dual-owner origin + FleetCapabilityRequired mechanism-primitive exemplar)
- `docs/research/domains/auth/2499_auth_canonical_summary.md` (prior arc close pattern model)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.1 parent scoping template + §11.3 canonical-summary template + §14 evidence rules + §15 SIGN cadence + §16 draft-first workflow

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2599 xx99 close residuals — post-arc anchor-cascade PR

Per Chris "commit it" ratification at S2599 xx99 close 2026-07-06:

- **Post-commit docs cascade PR** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Verify final chunk count + provenance-json refresh in PR body.

- **ARCHITECTURE_INDEX.md + OPEN_ARCS.md deferred anchor cascade** (extends S2501+S2502+S2503+S2504+S2599 xx99 close deferrals):
  - **AU-4** ARCHITECTURE_INDEX §1.93 S2501 backfill + §1.94 S2502 backfill + §1.95 S2503 registration + §1.96 S2504 registration + §1.97 S2599 xx99 canonical summary registration + v88 → v93 version bump.
  - **AU-5** ARCHITECTURE_INDEX §8 timeline: 5 rows added (S2501 + S2502 + S2503 + S2504 + S2599 xx99).
  - **AU-6** ARCHITECTURE_INDEX §3 domain map API row update: WORKING mechanism / PARTIAL declaration.
  - **AU-7** ARCHITECTURE_INDEX §5 gap entries: close Group 2400 CF-B1/CF-D1/CF-C1/C2/C3 markers as research-CLOSED design-prep evidence-plane; open new Group 2500 §8 P0-tier gap markers.
  - **AU-8** ARCHITECTURE_INDEX §7 decision-matrix rows for 4 quadrants (Cat A Path A/B/C + Cat B (a)/(b)/(c) + Cat C α/β/γ + Cat D Path A/B/C REST↔WS T7 strictness).
  - **AU-9** ARCHITECTURE_INDEX §9 roadmap T-slot queue advance to T3 Group 2600 PA (NEXT) → T4 Group 1700 Observability → T5 Group 2300 Mobile (parallel) → T6 Group 1600 Content.
  - **AU-13** OPEN_ARCS.md Group 2500 API row transition In-progress → Closed; NEXT column update to "T3 Group 2600 PA queued".

- **Deep anchor-update items** (deferred from S2501+S2502+S2503+S2504+S2599 xx99 close for post-arc anchor-cascade PR OR follow-up PR at Group 2600 arc-open):
  - **AU-1** PLATFORM_INVENTORY §API autoblock CREATE (with Cat D §1.1 D1-D6 Denominator Contract explicitly named per Rigby Q2 fold; generator extends `gather_inventory()` per S2499 precedent).
  - **AU-3** PLATFORM_WHAT_IT_IS §API narrative subsection CREATE.
  - **AU-10** `docs/topics/api.md` CREATE (analog to `docs/topics/auth.md` per S2499 AU-D2 + AU-D7).
  - **AU-11** `platform_architecture_inventory.md` §3.22 API Layer REVISE (sub-layer breakdown: DECLARATION PARTIAL + CONSUMER PARTIAL + CONTRACT PARTIAL + REGISTRY GREENFIELD).
  - **AU-12** CODEOWNERS cockpit surface refinement (cockpitApi.ts + cockpitQueries.ts + apiClient.ts + types/cockpit.ts + useWebSocket.ts) deferred to S2600+ per CODEOWNERS lines 8-13 explicit deferral.

### Group 2400 + Group 2500 post-arc remediation queue (unchanged carry into S2600)

**P0-A platform-wide (S2599 xx99 execution scope owned; Cat D new-owner rows integrated):**
- **AU-U1** Route→view normalization pass to compute D4 unique-view denominator. Blocks ratio-comparison truth + Cat B (c) permission-floor governance verdict-confidence but NOT tactical P0-A execution (per Rigby Q4 STRENGTHEN fold blocking-vs-non-blocking clarifier).
- F-D-CALL-1 803-scale silent-401 remediation.
- F-D-BYPASS-1 79-raw-fetch bypass reconciliation.
- F-D-ENVELOPE-1 typed-error-envelope execution.
- F-D-BOUNDARY-1 error-boundary framework establishment — BLOCKING PREREQUISITE for Cat D γ mechanism.

**P0-B token lifecycle / security window:**
- F-D-SIDEBAR-1 Sidebar backend-token-revoke fix (single-line).
- F-C-REFRESH-1 refresh discipline decision-space execution (coupled to α/β/γ verdict).
- F-C-VIP-1 VIPInvite.account_expires_at ENFORCEMENT (4 candidates + Rigby Q18 rubric).
- F-C-CSD-1 Clear-Site-Data emission on logout (3 candidate loci).
- F-C-STORE-1 15-surface × logout-cleanup declared contract execution.

**P0-C endpoint-specific:**
- F-CRIT-1 PURGE_SECRET hardcoded fallback remediation.
- F-BND-4a Unauthenticated bet-placement WRITE remediation.
- F-B-CRIT-1 Permission-floor implicit-inheritance ~80-90% (blocks on AU-U1 D4).
- F-B-CRIT-2 Silent-401 SYSTEMIC.
- F-D-WHITELIST-1 Whitelist replacement (γ PROPOSED PRIMARY per Rigby Q7 fold).
- **F-D-REGISTRY-1 NEW** Per-endpoint permission-floor registry.
- **F-D-WSENVELOPE-1 NEW** WS message-contract SoT.
- **F-D-4LAYERSPLIT-1 NEW** Permission-floor 4-layer split cross-layer SoT (CONTINGENT on registry verdict).

### T-slot follow-on queue (post-Group-2500-close forward look)

- **T3 Group 2600 PA cross-arc handoff bundle** — NEXT per T-slot queue. Consumes 4 CF-* originated S2501-S2504.
- **T4 Group 1700 Observability cross-arc handoff bundle** — QUEUED after Group 2600 close. Extended CF-D6 secondary stakeholder from Q9 fold.
- **T5 Group 2300 Mobile (parallel)** — CF-D4 + CF-C4 + Cat A CF-4 + Cat D CF-D6 secondary stakeholder — parallel silent-401 audit for mobile app.
- **T6 Group 1600 Content (per Cat C S2503 Rigby SIGN Q11 fold CF-C8)** — Content/Publishing surfaces call auth-protected endpoints; envelope-shape variability leaks into editor/publisher UX.
- **Maintainer-decision batch** — CODEOWNERS API-slice discipline + DEAD-CANDIDATE consolidated cleanup (18 modules verified zero-consumer at S2502) + api.ts extraction execution + storageKeys registry + basic vs enhanced logout consolidation + STAFF_REQUIRED_PATHS 2-of-3 phantom cleanup + `@authentication_classes([])` 3-file × 6-site stacking cleanup.
- **CODEOWNERS cockpit refinement** — cockpitApi.ts + hooks/cockpitQueries.ts + apiClient.ts + types/cockpit.ts + useWebSocket.ts ownership assignment deferred to S2600+ per CODEOWNERS lines 8-13.

### Session count status

- Group 2500 API arc CLOSED at S2599 xx99 close 2026-07-06 (6 of 6 sessions shipped: S2500 parent + S2501 Cat A + S2502 Cat B + S2503 Cat C + S2504 Cat D + S2599 xx99).
- Group 2400 Auth arc CLOSED at S2499 (prior arc).
- TWENTY-THIRD-consecutive child-audit template application (S2504).
- TWELFTH formal arc pin RETIRED at S2599 xx99 close (`pa-a03b111768464b3f`) — after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2499 eleven prior.
- TWENTY-SECOND consecutive dedicated fresh SIGN pin retirement at S2599 xx99 close (SIGN pin `pa-59d9583dc4da4d5e`) — after twenty-one prior.
- TWELFTH-consecutive §11.3 12-section canonical-summary template application at S2599 xx99.
- TWELFTH-consecutive §11.3 §10 5-subsection meta-methodology template application at S2599 xx99 (adopted S1399 close 2026-07-01 per Chris directive; unbroken S1399 → S2599).
- SIXTH-consecutive parent-with-4-children arc close (Groups 1900 + 2000+ + 2100 + 2200 + 2400 + 2500) — MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails extended.

## SESSION READY CHECK (before opening Group 2600 PA arc)

Before minting the Group 2600 PA arc pin + drafting parent scoping:

1. **Rotate `tools/pa_local.sh:312` FIRST.** Bare invocation before rotation will route to retired pin `pa-a03b111768464b3f` and fail. Mint fresh Group 2600 arc pin: `python tools/pa_chat.py "session_tool action=create_fresh title='Group 2600 PA arc pin (S2600 open)'"` (via override PA_API_TOKEN or via direct authentication for local — pa_local.sh unusable until rotated). Then edit `tools/pa_local.sh:312` `--conversation` value to new pin.
2. `tools/pa_local.sh "platform_config_tool action=overview"` (post-rotation) → verify `service_context: local` + `railway_environment: local` + `database_name: unified_donkey_betz` + `default_llm_provider: openai` under new Group 2600 arc pin.
3. Update `tools/pa_local.sh` header ledger with S2500 retirement stanza (already exists at line 56ff from S2599 close) + S2600 open stanza per S2000/S2100/S2200/S2400/S2500 documentation pattern.
4. Read `docs/research/domains/api/2599_api_canonical_summary.md` fully — DIRECT PREDECESSOR + arc-close canonical verdict.
5. Read `docs/research/domains/auth/2499_auth_canonical_summary.md` fully — prior-prior arc close model per playbook §11.3.
6. Read the 4 CF-* handed-forward flags per S2599 §9 delegated-arcs table + §8.2 T-slot queue for Group 2600 PA scope.
7. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.1 parent scoping template + §21 short start commands.
8. **First execution step at Group 2600 open:** draft parent scoping shape card (Q1 taxonomy + Q2 central lens + Q3 acceptance criteria + Q4 anti-scope) per S2500 parent scoping precedent + route to Rigby SIGN-preview via new arc pin (single-batch × 4-Q preview cadence per S1899-S2500 EIGHT-consecutive tested pattern EIGHTH-consecutive candidate).
9. Playbook §11.1 parent scoping template application (SEVENTH-consecutive per playbook §11.1 template; S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2500 eleven prior actually — SEVENTH-consecutive-in-parent-with-children track per Groups 1900+2000++2100+2200+2400+2500 six prior).
10. Route parent scoping to Rigby SIGN cycle 1 via dedicated fresh SIGN isolation pin (NOT arc pin) per playbook §15 SIGN-isolation discipline (TWENTY-THIRD consecutive dedicated fresh SIGN pin candidate at close).
11. Fold SIGN edits; retire SIGN pin at cycle close via `session_tool.retire`.
12. Present Chris ratification card ("commit it" candidate). Status flips `draft` → `active` on ratification per playbook §16 draft-first workflow.
13. Docs cascade + handoff + overwrite `00-START-NEXT-SESSION.md` with S2601 P1 child priorities.

**Group 2600 PA arc-open command (Chris short command):** `Start research group 2600: PA` or equivalent invocation matching playbook §21 vocabulary + OS §3.2 deterministic route.
