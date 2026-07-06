# Next Session — Start Here

---

## READ THIS FIRST — GROUP 2500 API ARC OPEN + S2501 P1 CAT A QUEUED

**Group 2500 API arc OPENED at S2500 parent scoping doc 2026-07-05.** Arc pin `pa-a03b111768464b3f` MINTED via `session_tool.create_fresh` — **TWELFTH formal arc pin under Research OS** after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200/2400 prior eleven. Runtime target 6 sessions per parent §5 (S2500 + S2501-S2504 + S2599 xx99); **1 of 6 shipped**.

`tools/pa_local.sh:280` points at active arc pin `pa-a03b111768464b3f` (rotated at S2500 open from retired `pa-6279ead1714c4630` per playbook §16 arc-open fresh-thread discipline). Bare invocation `tools/pa_local.sh "message"` routes into the Group 2500 API arc thread.

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

Per `.env` PA_API_TOKEN is production; bare `pa_chat.py` against local without local-token override → 401. Always use `tools/pa_local.sh` (sets URL + local token).

## READ THIS SECOND — S2501 P1 CAT A BACKEND API CONTRACT SOT DESIGN-PREP QUEUED

**S2501 P1 Cat A is the NEXT child audit** per S2500 parent §5 child mission sequence Chris-locked "agree all" 2026-07-05. Playbook §11.2 20-section child-audit template TWENTIETH-consecutive application candidate after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401+S2402+S2403+S2404 nineteen prior.

- **Arc pin STATUS:** `pa-a03b111768464b3f` ACTIVE + PRESERVED per playbook §16 arc-standard behavior (no retirement until S2599 xx99 close). TWELFTH formal arc pin under Research OS.
- **SIGN pin STATUS:** Fresh SIGN isolation pin to be minted at S2501 open per playbook §15 SIGN-isolation discipline (EIGHTEENTH consecutive dedicated fresh SIGN pin candidate).

## READ THIS THIRD — S2500 PARENT SCOPING LOAD-BEARING OUTPUTS FOR S2501

**Group 2500 central lens question** (Chris "agree all" 2026-07-05 ratified with OpenAPI-canonical clause per Rigby SIGN-preview Q2 fold):

> *"Does the platform's API surface have a source-of-truth contract (typed responses + typed errors + per-endpoint permission floor + refresh + logout envelope), with OpenAPI as the canonical SoT (and typed client as a derived artifact) — or is it an accretion of implicit shapes with drf-spectacular partial-wiring at sports only + silent-401 SYSTEMIC downstream symptom?"*

**Candidate arc seam (verdict-neutral ternary per Rigby SIGN cycle 1 Q4-2 fold):** Evidence may support **(i) coherent contract spine**, **(ii) declared-but-uneven contracts**, or **(iii) implicit shape accretion**. Children collect evidence supporting any of the three; parent verdict CONFIRMED or REFUTED accordingly.

**Refutation-would-look-like 4 criteria per Rigby SIGN cycle 1 Q4-1 fold:**
1. `python manage.py spectacular --file schema.yaml` generates coherent OpenAPI 3.0 schema for money-path + governance-path + PA-path scoped slice.
2. `core/*.py` endpoint declarations consistently @extend_schema-decorated across the slice at HEAD.
3. Typed client derivation aligns with runtime responses/errors observed at api.ts consumption points — no silent inference drift.
4. Per-endpoint permission-floor registry can be derived directly from `permission_classes` declarations without ad-hoc STAFF_REQUIRED_PATHS augmentation.

≥3 refute → coherent spine holds; 0-1 refute → accretion holds; 2 refute → declared-but-uneven middle.

**S2501 P1 Cat A scope (Chris-locked at parent scoping):**
- **§3 Canonical Entry Points:** `sports/views.py` (16 @extend_schema decorators as HEAD baseline) + `core/*.py` (0 decorators baseline) + `drf-spectacular==0.28.0` INSTALLED + `python manage.py spectacular --file schema.yaml` (untested per S2299 §6 UNKNOWN 5 — **first execution step at S2501 open**).
- **§4-§9 backend contract layer:** DRF Serializer/ModelSerializer hierarchy + spectacular schema generator + URL-registered endpoints inventory + request→view→serializer→response flow + adjacent-domain integrations.
- **§14 Known Drift:** SoT-ABSENT F1 (RE-VERIFY at HEAD); Path A/B/C triad status per S2203 §20.6.
- **§19 Recommended Future Research:** Chris-D-verdict on Path A/B/C triad; drf-spectacular platform-wide retrofit design-prep; PLATFORM_INVENTORY §API autoblock proposal-only (per Rigby SIGN cycle 1 Q3-2 fold); `docs/topics/api.md` CREATE proposal (deferred to S2599 xx99).

**S2501 acceptance criteria (per parent §3 AC #1-#7):**
- AC #1 Contract SoT observability (Cat A owns @extend_schema coverage matrix)
- AC #2 Typed error envelope contract (Cat A boundary; primary owner is Cat C)
- AC #4 Per-endpoint permission-floor observability (Cat A boundary; primary owner is Cat D)
- AC #7 Scoped API-slice definition + repeatable coverage measurement — **Cat A owns API-slice manifest for backend surface** (spec-only per Rigby SIGN cycle 1 Q3-1 fold)

**S2501 anti-scope (per parent §7):**
- No backend API implementation (no code PR).
- No new endpoint authoring.
- No typed-client/codegen framework selection.
- No auth mechanism changes.

## READ THIS FOURTH — LOAD-BEARING INPUTS FOR S2501

**S2501 must consume + re-verify at HEAD:**
- `docs/research/domains/api/2500_api_domain_scoping.md` (primary predecessor — S2500 parent scoping doc; §3.A Cat A mission + acceptance + inheritance + §6 parked items + §9 next-step)
- `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` (§14 F1 SoT-ABSENT + §20.6 Path A/B/C triad + §19.1 R1)
- `docs/research/domains/frontend/2299_frontend_canonical_summary.md` (§5.1 canonical seam + §8.2 T2 handoff + §8.3 R6)
- `docs/research/domains/auth/2499_auth_canonical_summary.md` (26 cross-arc flags → 7 delegate arcs including 7 CF-*1 flags inherited by Group 2500)
- `docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` (Cat B (c) per-endpoint permission registry design-prep candidate — Cat A boundary via permission_classes declaration coverage)
- `docs/research/platform_architecture_inventory.md` §3.30 API layer (or nearest §3.27 Auth adjacent for permission-floor context)
- `requirements.txt` (drf-spectacular==0.28.0 INSTALLED verification)

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2500 arc-open cascade residuals

Per Chris "commit it" ratification at S2500 close:

- **Post-commit docs cascade PR** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Executed in-session pre-commit; verify final chunk count + provenance-json refresh in PR body.
- **Deferred anchor-update items to S2501 Cat A output or S2599 xx99 close:**
  - PLATFORM_INVENTORY §API autoblock CREATE — Cat A P1 output candidate (proposal-only per Rigby SIGN cycle 1 Q3-2 fold; formal autoblock code addition at follow-on cascade PR post-S2599 xx99)
  - PLATFORM_WHAT_IT_IS §API narrative subsection CREATE — deferred to Cat A P1 output + S2599 xx99 close recommendation
  - `docs/topics/api.md` CREATE — analog to `docs/topics/auth.md` shipped at S2499 close; deferred to S2599 xx99 close if load-bearing
  - ARCHITECTURE_INDEX Path A/B/C + α/β/γ × 3 decision matrix pointer — parallel to Group 2400 AU-D6 α/β/γ × 2 pointer
  - CODEOWNERS API-slice discipline — deferred to post-arc T-slot if F-D-OWN-1 remediation-model extends to API layer

### Group 2400 post-arc remediation queue (unchanged carry into S2501 execution scope)

Per S2499 §8.1 rank-1 co-equal P0 batch preserved from Cat A/B/C/D + Cat D Rigby Q15 fold tiered ordering. Distribution across arcs unchanged; Group 2500 arc scope inherits P0-A + P0-B items for design-prep.

**P0-A platform-wide (S2501-S2504 execution scope):**
- F-D-CALL-1 803-scale silent-401 remediation (typed-error-envelope Cat D α/β/γ) — Cat C P3 primary owner
- F-D-BYPASS-1 79-raw-fetch bypass reconciliation — Cat B P2 primary owner
- F-D-ENVELOPE-1 typed-error-envelope — Cat C P3 primary owner
- F-D-BOUNDARY-1 error-boundary framework establishment — Cat C P3 boundary; primary owner is S2299 §8.3 R6 execution (Group 2200 post-arc T-slot BLOCKING PREREQUISITE)

**P0-B token lifecycle / security window (S2501-S2504 execution scope):**
- F-D-SIDEBAR-1 Sidebar backend-token-revoke fix — deferred to post-arc PR post-S2504
- F-C-REFRESH-1 refresh discipline decision-space execution — Cat C P3 primary owner
- F-C-VIP-1 VIPInvite.account_expires_at ENFORCEMENT — cross-arc gate (Cat C boundary; risk-gate prereq)
- F-C-CSD-1 Clear-Site-Data emission on logout — Cat C P3 primary owner
- F-C-STORE-1 15-surface × logout-cleanup declared contract execution — Cat C P3 primary owner

**P0-C endpoint-specific (distributed across arcs; some remain Group 2400 backlog):**
- F-CRIT-1 PURGE_SECRET hardcoded fallback remediation — Group 2400 backlog
- F-BND-4a Unauthenticated bet-placement WRITE remediation — Group 2400 backlog
- F-B-CRIT-1 Permission-floor implicit-inheritance ~80-90% — Cat D P4 primary owner
- F-B-CRIT-2 Silent-401 SYSTEMIC (Cat D delivered 803-scale evidence at S2404) — Cat C P3 + Cat D P4
- F-D-WHITELIST-1 Whitelist replacement (Cat D α/β/γ × 2 second axis) — Cat C P3 primary owner

### T-slot follow-on queue (post-Group-2500-close forward look)

- **T3 Group 2600 PA cross-arc handoff bundle** — QUEUED after Group 2500 close — workspace-context authz + `session_tool.retire` cascade on user logout + PA-chat 401 UX design + paStore field-list completeness + REST↔WS T7 joint co-owner
- **T4 Group 1700 Observability cross-arc handoff bundle** — QUEUED after Group 2600 close — 503-fork asymmetry + login/logout event emit + silent-401 rate telemetry + `authHandling: 'suppress_redirect'` telemetry + smoke-test coverage per gate mechanism (umbrella roll-up per Cat C Q11 fold + Cat D CF-D3 discipline)
- **T5 Group 2300 Mobile (parallel)** — CF-D4 + CF-C4 + Cat A CF-4 — parallel silent-401 audit for mobile app + MobilePushToken.revoked_at cascade + 401-handling parity between web + mobile
- **Maintainer-decision batch** — CODEOWNERS API-slice discipline + DEAD-CANDIDATE consolidated cleanup + api.ts extraction execution + storageKeys registry (deferred from S2499 close)

### Session count status

- Group 2500 API arc OPEN at S2500 (1 of 6 sessions shipped)
- Group 2400 Auth arc CLOSED at S2499 (previous arc)
- ELEVENTH-consecutive parent-scoping template application at S2500
- TWELFTH formal arc pin ACTIVE at S2500 open (`pa-a03b111768464b3f`)
- SEVENTEENTH consecutive dedicated fresh SIGN pin retirement completed at S2500 parent-scoping SIGN cycle 1 close

## SESSION READY CHECK (before opening S2501 P1 Cat A)

Before drafting the S2501 P1 Cat A child audit:

1. `tools/pa_local.sh "platform_config_tool action=overview"` → verify `service_context: local` + `railway_environment: local` + `database_name: unified_donkey_betz` + `default_llm_provider: openai` under active arc pin `pa-a03b111768464b3f`.
2. `session_tool action=create_fresh` → mint fresh SIGN isolation pin for S2501 SIGN cycle 1 (EIGHTEENTH consecutive dedicated fresh SIGN pin candidate). Do NOT dispatch S2501 audit content through the SIGN pin until draft is complete; use arc pin `pa-a03b111768464b3f` for interim tool calls.
3. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 20-section child-audit template + §13 six-parallel-Explore-agent sweep contract + §14 verifier-loop discipline + §15 SIGN cadence stage-table.
4. Read `docs/research/domains/api/2500_api_domain_scoping.md` fully — S2501's primary predecessor input (§3.A Cat A mission + §2 evidence-provenance + §5 sequence + §6 P-1 through P-11 parked items + §8 decisions + §9 next-step).
5. Read `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` §14 F1 SoT-ABSENT + §20.6 Path A/B/C triad + §19.1 R1 + escape hatch preserved per Q11 STRENGTHEN.
6. Read `docs/research/domains/frontend/2299_frontend_canonical_summary.md` §5.1 canonical seam + §8.2 T2 handoff bundle + §8.3 R6 error-boundary framework.
7. **First execution step at S2501 open: RESOLVE S2299 §6 UNKNOWN 5** via `python manage.py spectacular --file schema.yaml`. Verifies drf-spectacular actually generates working OpenAPI 3.0 spec from existing 16 @extend_schema decorators at HEAD. Positive → baseline for Path A retrofit design-prep; negative → design-prep must include spectacular wire-up debugging as first Cat A deliverable.
8. Dispatch 6-parallel-Explore-agent sweep per playbook §13 (Agent 1 Models + Persistence — DRF Serializer/ModelSerializer hierarchy + @extend_schema payload types; Agent 2 Services + Runtime Flows — spectacular schema generator + management commands + request→view→serializer→response; Agent 3 APIs + Tools + Tasks + Commands — 1,864 URL routes vs @extend_schema-decorated subset; Agent 4 Integrations + Cross-Domain — Group 2400 permission-floor overlap + Group 2200 §20.6 Path A/B/C; Agent 5 Documentation + Prior Research — S2203 F1 + S2299 §8.2 T2 + Group 2400 CF-*1; Agent 6 Drift + Debt + Ownership + Maturity — SoT-ABSENT rate + `@extend_schema` coverage + Path A/B/C posture).
9. Parent-Claude verifier-loop applied per playbook §14 on sub-agent claims pre-draft.
10. Draft the S2501 20-section child audit per playbook §11.2 skeleton.
11. Route to Rigby SIGN cycle 1 via dedicated fresh SIGN isolation pin (NOT arc pin) per playbook §15; 4-batch × 5-Q = 20-Q child-audit cadence per S2201-S2404 nine-consecutive tested pattern (TENTH-consecutive candidate); expected 15-25 folds landable pre-Chris-ratification.
12. Fold SIGN edits; retire SIGN pin at cycle close via `session_tool.retire` (EIGHTEENTH consecutive dedicated fresh SIGN pin retirement candidate).
13. Present Chris ratification card ("commit it" candidate). Status flips `draft` → `active` on ratification per playbook §16 draft-first workflow.
14. Fresh arc pin `pa-a03b111768464b3f` PRESERVED through S2501 per playbook §16 arc-standard behavior.
15. **After S2501 close: S2502 P2 Cat B Frontend API-client architecture design-prep next** — playbook §11.2 20-section child-audit template + Rigby SIGN cycle 1 via dedicated fresh SIGN isolation pin + 4-batch × 5-Q cadence per S2201-S2501 ten-consecutive tested pattern (ELEVENTH-consecutive candidate).

**S2501 open command (Chris short command):** `Continue research group 2500: Cat A` or `Start S2501` or equivalent invocation matching playbook §21 vocabulary + OS §3.2 deterministic route.
