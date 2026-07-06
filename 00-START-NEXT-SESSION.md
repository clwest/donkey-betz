# Next Session — Start Here

---

## READ THIS FIRST — GROUP 2400 AUTH ARC CLOSED + GROUP 2500 API ARC QUEUED

**Group 2400 Auth arc CLOSED at S2499 xx99 canonical summary 2026-07-05.** Arc pin `pa-6279ead1714c4630` RETIRED via `session_tool.retire` force=true (updated_count=25, retired=true, previously_active=true — **ELEVENTH formal arc-pin retirement in Research OS** after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200 prior ten). Runtime target 6 sessions ACHIEVED — 6/6 = 100%.

`tools/pa_local.sh:280` still points at retired pin `pa-6279ead1714c4630` — **MUST rotate to next-arc's fresh pin at S2500 open** per playbook §16 arc-open fresh-thread discipline (see §Arc-open mechanics for S2500 below).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**WARNING:** Bare invocation currently routes into retired thread `pa-6279ead1714c4630`. Do NOT dispatch through `pa_local.sh` until S2500 arc-open completes fresh-pin mint + wrapper rotation.

Per `.env` PA_API_TOKEN is production; bare `pa_chat.py` against local without local-token override → 401. Always use `tools/pa_local.sh` (sets URL + local token) after wrapper rotation.

## READ THIS SECOND — S2500 T2 GROUP 2500 API ARC-OPEN QUEUED

**Group 2500 API is the T2 NEXT arc** per S2299 §8.2 + S2499 §8.4. Selected as NEXT because 4 of 4 Group 2200 children referenced API contract discipline (S2203 F1 SoT-ABSENT + F3 silent-401 + F4 mega-module api.ts + F5 DEAD-CANDIDATE modules) + all 4 Cat A/B/C/D children of Group 2400 emitted CF-*1 flags to Group 2500 (refresh endpoint + logout envelope + Clear-Site-Data + typed-error-envelope + per-endpoint permission registry design-prep + drf-spectacular retrofit).

- **Arc pin STATUS:** RETIRED (Group 2400 pin `pa-6279ead1714c4630` retired at S2499 close); TWELFTH formal arc pin to be minted at S2500 open per playbook §16 arc-open fresh-thread discipline.
- **Arc queue standing:** T2 NEXT per S2299 §8.2 post-Group-2400 queue. Alternative queue candidates per project memory post-S2099 ranking: 2300 Mobile / 2500 API / 2600 PA. Chris D-override at S2199 close 2026-07-05 ratified Group 2400 Auth over Mobile queue candidate; expect similar D-override opportunity at S2500 open for API vs Mobile vs PA queue order.

## READ THIS THIRD — S2499 CANONICAL SUMMARY LOAD-BEARING INPUTS FOR S2500 ARC-OPEN

**Group 2400 Auth canonical verdict** (Chris "commit it" 2026-07-05 ratified): **"ACCRETION with declared-but-unenforced contracts."** Mechanisms generally work at file-precision in the sampled surfaces; contract silently violated across all 4 axes examined. Pattern generalizes — one architectural posture, not scattered defects.

**Cat A/B/C/D findings STILL-LIVE at HEAD `4e6c1ee8`:**
- **F-DEC-1** `@token_auth_required` decorator drift 65 uses / 10 files (drift-down from Cat A 68/9 baseline; applied uses 64/9 with definition site in denominator)
- **F-WS-1** WebSocket auth middleware DEAD in ASGI stack
- **F-CRIT-1** PURGE_SECRET hardcoded fallback `'donkey-purge-2026'` at `core/views_home.py:259`
- **F-BND-4a** Unauthenticated bet-placement WRITE endpoint (money-path boundary violation)
- **F-B-CRIT-1** Permission-floor implicit-inheritance ~80-90% ESTIMATE (ROOT CAUSE)
- **F-B-CRIT-2** Silent-401 SYSTEMIC (SYMPTOM downstream of F-B-CRIT-1)
- **F-B-HIGH-1** STAFF_REQUIRED_PATHS 2-of-3 PHANTOM entries
- **F-B-HIGH-4** auth_views_enhanced.py `@authentication_classes([])` + `[IsAuthenticated]` stacking (4 files)
- **F-C-VIP-1** VIPInvite.account_expires_at 14d NOT enforced at runtime (declared-fictional class)
- **F-C-REFRESH-1** No session-token refresh endpoint
- **F-C-CSD-1** Zero Clear-Site-Data emission on logout
- **F-C-STORE-1** 14 of 15 client-side persistence surfaces lack DECLARED logout-cleanup contract (6.7% declared cleanup rate)
- **F-D-CALL-1** 803 consumer call-sites at HEAD (57 direct + 667 hook + 79 raw fetch); ~99% silent-swallow rate
- **F-D-BYPASS-1** 79 raw fetch() across 31 files bypass interceptor entirely (9.8% of surface)
- **F-D-SIDEBAR-1** Sidebar.tsx:356 does NOT call authApi.logout(); backend token never revoked via sidebar path
- **F-D-ENVELOPE-1** 0 typed AxiosError catches; envelope adoption greenfield
- **F-D-BOUNDARY-1** 0 error boundaries anywhere
- **F-D-PA-1** PA-chat 401 mid-conversation = agent-hang UX
- **F-D-OWN-1** CODEOWNERS absent (F-D-OWN-1 REMEDIATED at S2499 close via minimum viable CODEOWNERS creation)

**Three three-option decision spaces surfaced for Chris D-verdict during S2500 execution:**
- **Cat B a/b/c** (permission-floor): Cat B PRIMARY = (b) split-read-write + client-side auth-check-on-write for REMEDIATION WINDOW + (c) per-endpoint permission registry PRIMARY for LONG-TERM GOVERNANCE
- **Cat C α/β/γ** (session-lifecycle): Cat C PROPOSED = (β) explicit re-login as least-assumption default
- **Cat D α/β/γ × 2** (typed-error-envelope + whitelist-replacement):
  - Envelope: **γ RQ error callback + top-level ErrorBoundary** as PROPOSED PRIMARY DEFAULT (γ = mechanism; Cat C β "explicit re-login" = message/UX policy nested inside γ per Cat D Rigby Q6 fold)
  - Whitelist: **γ per-api-module `authHandling: 'default' | 'suppress_redirect'` string enum + telemetry on every suppress_redirect use** as PROPOSED PRIMARY DEFAULT (Cat D Rigby Q7 fold — NOT boolean; harder to misuse)

**Cat D Rigby Q9 fold handler discipline** (must be preserved at S2500 execution):
- Handler MUST distinguish 401/403 vs network/offline vs 5xx
- Copy MUST avoid time-based "expired" language until F-C-VIP-1 resolves (use "Sign-in required" / "Authentication required" preserving Cat C risk-gate)

**§14 Silent-degrade dominance** — 17 of 19 Cat D findings (89.5%) + 13 of 14 Cat C findings (92.9%) are silent-degrade class; two-trigger threshold met at S2499 close. **Codification candidate scope-bounded** to auth-failure-handling (401/403/refresh/logout) per Cat D Rigby Q5 fold + xx99 Rigby SIGN Q3 fold **conditional promotion rule**: general silent-degrade codification blocked pending 3rd trigger in non-auth plane (Groups 2500 API / 2600 PA / 1700 Observability). **S2500 execution watch list**: does silent-degrade class appear in Group 2500's own findings? If YES → conditional promotion triggered; general codification promoted at S2599 xx99.

**Cross-arc coordination flags Group 2500 API arc INHERITS from Group 2400 close (CF-D1 + CF-B1 + CF-C1 + Cat A CF-3 roll-up):**
- Refresh endpoint contract (F-C-REFRESH-1 downstream)
- Logout envelope + Clear-Site-Data emission spec (F-C-CSD-1 remediation)
- Typed-error-envelope Cat D α/β/γ decision-space
- Per-endpoint permission registry Cat B c decision-space
- drf-spectacular retrofit for typed responses (S2203 F1 SoT platform-wide)
- F-B-HIGH-1 STAFF_REQUIRED_PATHS phantom entries cleanup
- F-B-HIGH-4 auth_views_enhanced.py fixes

## READ THIS FOURTH — S2500 P0 GROUP 2500 API PARENT SCOPING SCOPE

**S2500 = P0 parent scoping** per playbook §11.1 20-section parent-scoping template. **ELEVENTH-consecutive parent-scoping application candidate** after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200/2400 prior ten.

**Scope (proposed; Chris ratifies via shape-card at arc-open):**
- Backend API contract SoT (drf-spectacular platform-wide retrofit; sports/views.py 16 @extend_schema decorators + core/*.py 0 decorators baseline per S2203 F1)
- Money-path API surface (BettingPage `placeBetMutation` + revenueApi + incomeBuilderApi + distributionApi)
- Governance-path API surface (decisionsApi + dreamsApi + advisorsApi + platformApi)
- PA-path API surface (assistantApi + /pa/chat/*)
- Refresh endpoint contract (F-C-REFRESH-1 downstream)
- Logout envelope + Clear-Site-Data emission (F-C-CSD-1 remediation)
- Typed-error-envelope contract (Cat D α/β/γ input)
- Per-endpoint permission registry design-prep (Cat B c input)
- API-module extraction (S2203 R4; api.ts 4194-LOC + 93 exports + 407-session churn)
- REST↔WS message contract strictness joint 2500+2600 (S2203 T7 + S2202 T6)

**Central question the S2500 arc answers.** *Does the platform's API surface have a source-of-truth contract (typed responses + typed errors + per-endpoint permission floor + refresh + logout envelope) or is it an accretion of implicit shapes with drf-spectacular partial-wiring at sports only + silent-401 SYSTEMIC downstream symptom?*

**Load-bearing inputs (S2500 must consume + re-verify at HEAD):**
- `docs/research/domains/auth/2499_auth_canonical_summary.md` (S2499 xx99 canonical summary — this arc's primary predecessor input)
- `docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md` §19.1 α/β/γ × 2 decision spaces + §14.5 803-consumer-call-site classification
- `docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` §19.1 (a)/(b)/(c) three-option + §14.5 21-loci permission-floor rate
- `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` §14 F1 SoT-ABSENT + F3 silent-401 SYSTEMIC + F3.5 whitelist BRITTLE + F5 18 DEAD-CANDIDATE modules
- `docs/research/domains/frontend/2299_frontend_canonical_summary.md` §5.1 canonical seam + §8.2 T1 handoff + §8.3 R6

**Rigby SIGN cycle 1 REQUIRED via dedicated fresh isolation pin per playbook §15** (parent scoping = required light SIGN; single-batch × 4-Q cadence per S1899-S2400 SEVEN-consecutive tested pattern — SEVENTH-consecutive candidate).

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2499 arc-close cascade residuals

Per Chris "commit it" ratification at S2499 close:

- **Post-commit docs cascade PR-γ** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Executed in-session pre-commit; verify final chunk count + provenance-json refresh in PR body.
- **Deferred anchor-update items to T2 Group 2500 API arc or follow-on PR-γ:**
  - PLATFORM_INVENTORY §Auth autoblock CREATE (AU-1+AU-B2+AU-C2+AU-D3) — requires `gather_inventory()` code change; scope for T2 or code-arc
  - PLATFORM_WHAT_IT_IS §Auth narrative subsection CREATE (AU-B+AU-C3+AU-D4) — needs careful prose; defer to follow-on
  - ARCHITECTURE_INDEX α/β/γ × 2 decision matrix pointer (AU-D6) — small addition; can go in follow-on cascade PR-γ
  - Refresh `docs/topics/frontend.md` (AU-D1) — needs careful prose; defer to follow-on
  - OPTIONAL `docs/topics/session_lifecycle.md` (AU-C4) — Chris-optional; defer to Chris-D-verdict on Cat C α/β/γ

### S2499 Group 2400 findings post-arc remediation queue (P0 rank-1 co-equal batch with Cat D tiered ordering)

Per S2499 §8.1 rank-1 co-equal P0 batch preserved from Cat A/B/C/D + Cat D Rigby Q15 fold tiered ordering (POST-ARC — S2500 execution scope + Chris D-verdicts):

**P0-A platform-wide (Group 2500 API arc scope + Group 2200 R6 execution):**
- F-D-CALL-1 803-scale silent-401 remediation (typed-error-envelope Cat D α/β/γ + R6 error-boundary framework)
- F-D-BYPASS-1 79-raw-fetch bypass reconciliation
- F-D-ENVELOPE-1 typed-error-envelope (Cat D α/β/γ post-Chris-D-verdict at S2500 arc)
- F-D-BOUNDARY-1 error-boundary framework establishment (S2299 §8.3 R6 BLOCKING PREREQUISITE for option-γ)

**P0-B token lifecycle / security window (Group 2500 API arc scope):**
- F-D-SIDEBAR-1 Sidebar backend-token-revoke fix (single-line addition per Cat C AU-C1)
- F-C-REFRESH-1 refresh discipline decision-space execution
- F-C-VIP-1 VIPInvite.account_expires_at ENFORCEMENT (risk-gate prerequisite for α/β/γ)
- F-C-CSD-1 Clear-Site-Data emission on logout
- F-C-STORE-1 15-surface × logout-cleanup declared contract execution

**P0-C endpoint-specific (distributed across arcs; some remain Group 2400 backlog):**
- F-CRIT-1 PURGE_SECRET hardcoded fallback remediation (preserved from Cat A)
- F-BND-4a Unauthenticated bet-placement WRITE remediation (preserved money-path boundary)
- F-B-CRIT-1 Permission-floor implicit-inheritance ~80-90% (Chris D-verdict at S2500 on (a)/(b)/(c))
- F-B-CRIT-2 Silent-401 SYSTEMIC (Cat D delivered 803-scale evidence; T2 execution scope)
- F-D-WHITELIST-1 Whitelist replacement (Cat D α/β/γ post-Chris-D-verdict at S2500)

### Group 2200 T-slot follow-on queue (post-Group-2400-close update)

- **T1 Group 2400 Auth cross-arc handoff bundle** — DELIVERED by Group 2400 arc (S2401-S2499) — all 4 axes discharged
- **T2 Group 2500 API cross-arc handoff bundle** — NEXT arc per S2299 §8.2 + S2499 §8.4 — refresh endpoint + logout envelope + Clear-Site-Data + typed-error-envelope + per-endpoint permission registry + drf-spectacular retrofit + F-B-HIGH-1 phantom cleanup + F-B-HIGH-4 auth_views_enhanced.py fixes
- **T3 Group 2600 PA cross-arc handoff bundle** — QUEUED after Group 2500 close — workspace-context authz + `session_tool.retire` cascade on user logout + PA-chat 401 UX design + paStore field-list completeness
- **T4 Group 1700 Observability cross-arc handoff bundle** — QUEUED after Group 2600 close — 503-fork asymmetry + login/logout event emit + silent-401 rate telemetry + `authHandling: 'suppress_redirect'` telemetry + smoke-test coverage per gate mechanism (umbrella roll-up per Cat C Q11 fold + Cat D CF-D3 discipline)
- **T5 Group 2300 Mobile (parallel)** — CF-D4 + CF-C4 + Cat A CF-4 — parallel silent-401 audit for mobile app + MobilePushToken.revoked_at cascade + 401-handling parity between web + mobile
- **Maintainer-decision batch (5 items governance gate)** — CODEOWNERS SHIPPED at S2499 close per AU-D5 (minimum viable) — remaining: DEAD-CANDIDATE consolidated cleanup + api.ts extraction + storageKeys registry + cockpitApi ownership
- **T2 post-arc T-slot (10 items)** — per S2299 §8
- **T3 conditional post-arc (4 items)** — cross-tab sync + Betting session-scoped state + runtime schema validation + REST↔WS joint T7

### S2199 post-arc T-slot execution queue (unchanged carry into S2500)

19 T-slot items distributed across 6 arcs + Employee OS per S2199 §8. All post-arc execution, NOT blocking S2500.

### Session count status

- Group 2400 Auth arc CLOSED at S2499 (6 of 6 sessions shipped; 6/6 = 100%)
- Group 2500 API queued NEXT (T2 per S2299 §8.2 + S2499 §8.4)
- ELEVENTH-consecutive parent-scoping template application candidate at S2500 open
- ELEVENTH formal arc-pin retirement completed at S2499 close; TWELFTH formal arc pin to be minted at S2500 open

## SESSION READY CHECK (before opening S2500 P0 parent scoping)

Before drafting the S2500 parent scoping doc:

1. `tools/pa_local.sh "platform_config_tool action=overview"` → **NOTE: Wrapper still points at retired pin `pa-6279ead1714c4630` — MUST rotate first** (see step 2)
2. **Arc-open mechanics — rotate arc pin:**
   - `tools/pa_local.sh "session_tool action=create_fresh"` (or via new fresh pin invocation) → mint TWELFTH formal arc pin under Research OS
   - Edit `tools/pa_local.sh:280` — rotate from retired `pa-6279ead1714c4630` to fresh arc pin per playbook §16 arc-open fresh-thread discipline
   - Verify fresh pin health_check via `platform_config_tool action=overview` (recommendation=continue expected) + pin ownership as chris per feedback_pa_local_verify_ownership.md
3. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.1 20-section parent-scoping template + §11.1 exemplar chain (S2400 most recent) for shape reference
4. Read `docs/research/domains/auth/2499_auth_canonical_summary.md` fully — S2500's primary predecessor load-bearing input (canonical verdict + 3 decision spaces + rank-1 co-equal P0 batch + §9 cross-arc flags CF-D1 → CF-D7)
5. Read `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` §14 F1 SoT-ABSENT + F3 silent-401 + F3.5 whitelist + F4 mega-module + F5 DEAD-CANDIDATE
6. Read `docs/research/domains/frontend/2299_frontend_canonical_summary.md` §5.1 canonical seam + §8.2 T1 handoff + §8.3 R6
7. Read `docs/research/platform_architecture_inventory.md` §3.30 API layer (or nearest) for §3.27-analog baseline
8. Draft the S2500 20-section parent scoping doc per §11.1 skeleton
9. Route to Rigby SIGN cycle 1 via dedicated fresh isolation pin per playbook §15 (parent scoping = required light SIGN); expected cadence single-batch × 4-Q per S1899-S2400 SEVEN-consecutive tested pattern (SEVENTH-consecutive candidate)
10. Fold SIGN edits; land as `status: draft` on filesystem; present Chris ratification shape-card (Chris typically ratifies via "agree all" or "commit it")
11. Fresh arc pin PRESERVED through S2500 per playbook §16 arc-standard behavior
12. **After S2500 parent scoping close: S2501 P1 first child audit next** — playbook §11.2 20-section child-audit template + Rigby SIGN cycle 1 via dedicated fresh isolation pin + 4-batch × 5-Q cadence per S2201-S2404 nine-consecutive tested pattern (TENTH-consecutive candidate)

**S2500 open command (Chris short command):** `Start research group 2500: API` or `Start research group 2500` or equivalent invocation.
