# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + S2403 CLOSED + S2404 CAT D QUEUED

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token).

**S2403 GROUP 2400 AUTH P3 CAT C CHILD AUDIT COMMITTED AT 2026-07-05.** Group 2400 Auth arc pin `pa-6279ead1714c4630` PRESERVED through S2403 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails (MC-14 CANDIDATE-threshold-satisfied extended to 4-arc-stages via Group 2200 + Group 2400 Cat A + Cat B + Cat C = 4 confirming arc-stages). `tools/pa_local.sh:280` unchanged. S2403 SIGN pin `pa-5096f5fc07754b18` retired at child-audit SIGN cycle 1 close (FOURTEENTH consecutive dedicated fresh SIGN pin retirement — 10 xx99 + 1 parent-scoping-light-SIGN + Cat A + Cat B + this cycle).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.** Pin ownership already verified as chris at S2401 open (conversation_owner_match=true) — Cat A + Cat B + Cat C preserved pin, so verification carries forward.

## READ THIS SECOND — GROUP 2400 AUTH ARC IN-PROGRESS (4 OF 6 SHIPPED); NEXT = S2404 P4 CAT D FRONTEND INTEGRATION + SILENT-401 SYSTEMIC RESOLUTION

**Group 2400 Auth: S2403 P3 Cat C CLOSED 2026-07-05.** Chris "commit it" 2026-07-05 ratified 32-fold SIGN-with-edits wholesale at MED-HIGH confidence (~0.82; HIGHER than Cat A 0.74 + Cat B ~0.8); status flipped `draft` → `active`. EIGHTEENTH-consecutive application of playbook §11.2 20-section child-audit template per S2402 handoff.

- **Arc pin PRESERVED:** `pa-6279ead1714c4630` per playbook §16 arc-standard behavior (retirement at S2499 close)
- **SIGN pin RETIRED:** `pa-5096f5fc07754b18` at S2403 SIGN cycle 1 close (updated_count=4)
- **Arc progress:** S2400 parent scoping (shipped) + S2401 P1 Cat A (shipped) + S2402 P2 Cat B (shipped) + S2403 P3 Cat C (shipped) → **S2404 P4 Cat D Frontend Integration + Silent-401 SYSTEMIC Resolution (NEXT)** → S2499 xx99. Runtime target 6 sessions — **4 of 6 shipped**; runtime cap 8.
- **MC-4 dial-back-resolution 5th confirming arc candidate** — Group 2400 4-child structure post-S2403 close continues MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails momentum toward across-5-consecutive-arcs, resolving S2199 Q3 STRENGTHEN dial-back at S2499 close.

## READ THIS THIRD — S2403 CAT C LOAD-BEARING INPUTS FOR S2404 CAT D

**S2403 7 headline findings (post-Rigby-SIGN-fold ranking; 4 HIGH + 3 non-HIGH):**

- **F-C-VIP-1 HIGH** (declared-fictional class) — `VIPInvite.account_expires_at` (14d) NOT ENFORCED at runtime; HEAD-verified via `views_vip_invite.py:85-163` + `invite.is_valid` at `models_vip_invite.py:95-103` checks ONLY `token_expires_at`; response body returns `account_expires_at.isoformat()` at `:161` (server tells client an expiry it will NEVER enforce). Risk-gating prerequisite for shipping any α/β/γ expiry-signal-bearing UX.
- **F-C-REFRESH-1 HIGH** (contract-absent class) — No session-token refresh endpoint; grep zero-match for auth-surface refresh in `core/urls.py` (3 `refresh` matches all non-auth). Combined with Cat A F-TOKEN-1: implicit contract "token permanent absent password event."
- **F-C-CSD-1 HIGH** (contract-absent class) — Zero Clear-Site-Data header emission on logout at HEAD `8bc1b0c0`. Neither `logout_view` (`auth_views.py:84-94`) nor `logout_enhanced_view` (`auth_views_enhanced.py:539-556`) sets the header.
- **F-C-STORE-1 HIGH** (silent-swallow aggregate + contract-absent per-surface) — 14 of 15 client-side persistence surfaces lack DECLARED logout-cleanup contract. S2204 §14 F1 15-surface baseline PRESERVED at HEAD (zero delta). Declared cleanup rate 1/15 = 6.7%.
- **F-C-COOKIE-1 LOW-MED** (contract-absent class; documentary gap only) — `SESSION_COOKIE_DOMAIN` + `SESSION_COOKIE_PATH` + `CSRF_COOKIE_DOMAIN` NOT declared. Django defaults correct at HEAD.
- **F-C-LOGOUT-1 MED** (silent-swallow class) — Basic logout (`auth_views.py:84-94`) has NO permission decorator; silent 200 on unauth. Enhanced fixes with `@permission_classes([IsAuthenticated])` at `:540`.
- **F-C-COCKPIT-1 MED** (silent-swallow bounded) — Cockpit two-stage MINOR-DRIFT re-verified STILL-LIVE at HEAD `frontend/src/App.tsx:134-149` (16 `/cockpit/*` `<Navigate>` NOT wrapped by `ProtectedRoute`).

**§14.2 15-surface storageKeys × logout-cleanup CONTRACT table** — 1 CLEAN (`auth-storage` functional-null-state) + 3 PARTIAL + 11 NO-CLEANUP; 8 of 15 surfaces have MED+ cross-user leakage severity.

**§14.3 21-loci lifecycle-observability rate table extension** — 5 WORKING + 5 PARTIAL + 11 DEAD; blocker to acceptance criterion #4 (session-lifecycle discipline undeclared at more than half of observable surfaces).

**7 cross-arc coordination flags emitted** (CF-C1 → Group 2500 API refresh + logout envelope + Clear-Site-Data + CF-C2 → Group 2600 PA workspace-context + session_tool retire on user logout + CF-C3 → Group 1700 Observability lifecycle transition observability single tracking unit with sub-bullets; explicitly extends Cat A CF-2 + Cat B CF-B5 for xx99 §5.4 Observability umbrella roll-up + CF-C4 → Group 2300 Mobile MobilePushToken revoked_at cascade + CF-C5 → Group 2200 Frontend R1/R5/R6 execution + CF-C6 → Cat D S2404 silent-401 + typed-error envelope alignment + CF-C7 → Group 1900 Governance KillSwitch attestation on logout boundary preserved).

**Cat C recommendation lean for xx99 Chris D-verdict:** Option **(β) explicit-re-login** as PROPOSED PRIMARY DEFAULT for REMEDIATION WINDOW (compatible with F-TOKEN-1 baseline; no refresh endpoint required; user-visible = observable; compatible with Cat D typed-error-envelope work) + Option **(α) silent-refresh** and Option **(γ) hybrid** as post-arc ENHANCEMENT candidates.

**Cat C emerging weak-spot pattern (Q20 fold):** **silent-degrade vs explicit-failure ambiguity on session-lifecycle plane** — playbook §20 codification candidate at S2499 xx99 close. Distinct from Cat B denominator-ambiguity (Cat B = measurement/metrics; Cat C = runtime UX/telemetry). 13-of-14 Cat C findings are silent-degrade class. **Two-trigger rule:** Cat C = TRIGGER #1; Cat D likely surfaces TRIGGER #2 in silent-401 SYSTEMIC audit (F-C-CSD-1 + F-C-STORE-1 + F-C-TAB-1 all point to Cat D's frontend caller surface).

**S2404 Cat D inherits from Cat A + Cat B + Cat C:** Cat A §7 runtime-flow-per-caller-class + §14.5 trust-boundary rate table + Cat B §14 F-B-CRIT-2 silent-401 SYSTEMIC (necessary-enabling-condition downstream of F-B-CRIT-1) + Cat B §14.5 21-loci permission-floor rate table + §19.1 three-option decision space precedent (a/b/c) + Cat C §14.2 15-surface storageKeys × logout-cleanup CONTRACT table + §14.3 21-loci lifecycle-observability rate table + §19.1 three-option decision space (α/β/γ) + F-C-VIP-1 risk-gating constraint + emerging weak-spot Q20 fold silent-degrade-vs-explicit-failure TRIGGER #2 candidate.

## READ THIS FOURTH — S2404 P4 CAT D SCOPE (FRONTEND INTEGRATION + SILENT-401 SYSTEMIC RESOLUTION)

**S2404 = P4 Cat D fourth child audit under Group 2400.** NINETEENTH-consecutive application of playbook §11.2 20-section child-audit template after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401+S2402+S2403 prior eighteen.

**Scope** (per S2400 parent scoping §3.D):
- Enumerate the frontend surface of the auth contract: `frontend/src/lib/api.ts:48-56` silent-401 handler + whitelist substring behavior + ~630 call-site blast radius (S2203 A3 baseline) + typed error envelope design candidates + error-boundary framework integration coordination
- Execute T1 cross-arc handoff: how does Group 2400 Auth deliver the contract to the frontend such that acceptance criteria #1 (permission-floor observability) + #2 (failure surfacing) both hold at api.ts layer?
- Re-verify Cat A + Cat B + Cat C findings at HEAD: Session 1171 503-fork exists on HTTP path only (Cat A F-DEC-1 decorator + F-WS-1 WS + Cat B F-B-MED-3 asymmetry) — Cat D audits FE-caller side of these

**Central question the audit answers.** *Does the frontend integration surface expose auth failures as first-class typed errors observable at every gated call site, or does the "silent-401 SYSTEMIC" + "brittle whitelist" pattern (S2203 §14 F3 F3.5) require redesign at the api.ts layer + cross-arc coordination with error-boundary framework + typed-error-envelope adoption?*

**Expected outputs (per S2400 §3.D):**
- (a) `api.ts:48-56` audit — full behavior enumeration (redirect target + whitelist substring rules + retry semantics + wrapper-duplicate accounting from S2203 Q14)
- (b) Silent-401 call-site inventory — extend S2203 A3 grep-based ~630 estimate. Per call-site: money-path / governance-path / read-path / write-path classification (CRITICAL for money + governance)
- (c) Typed error envelope design candidates three options: (α) throw typed exceptions per HTTP status; (β) return discriminated-union response types; (γ) React-Query error callbacks with typed error envelope. Recommend a lean; escalate to Chris D-verdict.
- (d) Whitelist replacement design — S2203 §14 F3.5 BRITTLE substring → replacement candidates: (α) explicit endpoint list registry; (β) 401-response-suppression header from BE; (γ) per-api-module explicit `noAuthRedirect` flag
- (e) Cross-arc coordination flags — error-boundary framework (S2299 §8.3 R6) + typed-error-envelope adoption (Group 2200 post-arc T-slot) + T1 handoff execution readiness + Cat C three-option decision space intersection

**Load-bearing inputs (Cat D must consume + re-verify at HEAD):**
- `frontend/src/lib/api.ts:48-56` silent-401 handler + interceptor logic
- `frontend/src/lib/api.ts` axios request interceptor at `:29` (reads token from authStore)
- `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` §14 F3 silent-401 SYSTEMIC + F3.5 whitelist BRITTLE + A3 ~630 call-site grep baseline
- `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md` §15.5 silent 401 systemic + no error boundaries anywhere
- `docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md` §7 runtime-flow-per-caller-class + §14.5 trust-boundary rate + F-DEC-1 `@token_auth_required` decorator drift (68 uses across 9 view files)
- `docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` §14 F-B-CRIT-2 silent-401 SYSTEMIC + §14.5 21-loci permission-floor + §19.1 three-option decision space (a/b/c)
- `docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md` §14.2 15-surface × cleanup + §14.3 21-loci lifecycle-observability + §19.1 three-option decision space (α/β/γ) + F-C-VIP-1 risk-gating constraint

**Sub-agent dispatch** per playbook §13 six-parallel-agent shape:
- Agent 1 Models + Persistence — Token expiry field candidates + response envelope shape candidates (typed error envelope options)
- Agent 2 Services + Runtime Flows — api.ts interceptor behavior + axios retry semantics + frontend router integration (`ProtectedRoute` gate; `Sidebar.tsx:356` logout onClick)
- Agent 3 APIs + Tools + Tasks + Commands — silent-401 call-site inventory extension (S2203 A3 ~630 baseline; grep for `await api.` + `api.get/post/put/delete/patch(` sites; money-path/governance-path classification)
- Agent 4 Integrations + Cross-Domain — S2203 F3 wrapper-duplicate accounting + Group 2200 error-boundary R6 execution readiness + Cat C 15-surface cleanup coordination + typed-error-envelope adoption blueprint
- Agent 5 Documentation + Prior Research — S2203 F3/F3.5 aggregation + S2201 §15.5 + Cat A/B/C findings inheritance table
- Agent 6 Drift + Debt + Ownership + Maturity — silent-401 SYSTEMIC drift matrix + typed-error-envelope debt matrix + FE integration ownership + PARTIAL maturity verdict; silent-degrade-vs-explicit-failure Q20 TRIGGER #2 confirmation candidate

**Rigby SIGN cycle 1 REQUIRED** per playbook §15 stage-scoped routing (child audit = required full SIGN via dedicated fresh isolation pin). Expected cadence: 4-batch × 5-Q = 20 total Q per S2201-S2403 EIGHT-consecutive tested pattern (NINTH-consecutive 20-Q cadence application candidate; MC-10 codification-ready-pending-Chris at 9-arc baseline).

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2403 arc-close cascade residuals

Per Chris "commit it" ratification at S2403 close:

- **Post-commit docs cascade** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Execute post-merge.
- **Auth topic doc gap preserved** — `docs/topics/auth.md` + `docs/topics/session_lifecycle.md` do NOT exist. Cat C AU-C1 recommends session-lifecycle subsection in prospective topics/auth.md; if separate, MUST cross-link. Candidate S2499 xx99 anchor-update recommendations per Cat C §19.4.
- **`PLATFORM_INVENTORY §Auth` autoblock gap preserved** — no dedicated Auth autoblock exists. Candidate S2499 xx99 anchor-update recommendations per Cat A §19.4 AU-1 + Cat B AU-B2 + Cat C AU-C2.
- **`PLATFORM_WHAT_IT_IS §Auth` narrative subsection gap preserved** — no dedicated Auth subsection exists. Candidate S2499 xx99 anchor-update recommendations per Cat A + Cat B + Cat C §19.4.
- **Session-lifecycle test coverage gap** — 0-of-17 session-lifecycle endpoints have declared smoke-test coverage. Blocker to acceptance criterion #6 for session plane; extends Cat A F-CRIT-2 pattern. Post-arc smoke-test authoring.

### S2403 CRITICAL findings post-arc remediation queue (Cat C additions to Cat A + Cat B rank-1)

Per Cat C §19.2 rank-1 co-equal P0 batch preserved from Cat A + Cat B + extended by Cat C (POST-ARC — not this session's authoring scope):

- **Cat A F-CRIT-1** PURGE_SECRET hardcoded fallback remediation (P0 PR)
- **Cat A F-BND-4a** Unauthenticated bet-placement WRITE remediation (P0 PR)
- **F-C-VIP-1 NEW P0 CANDIDATE** — VIPInvite.account_expires_at ENFORCEMENT (runtime middleware check OR periodic beat task); risk-gate prerequisite for shipping any α/β/γ expiry-signal-bearing UX per §19.1 constraint
- **F-B-CRIT-1** Permission-floor implicit-inheritance rate ~80-90% ESTIMATE (post-arc option (a)/(b)/(c) Chris D-verdict at xx99)
- **F-B-CRIT-2** Silent-401 SYSTEMIC as F-B-CRIT-1 downstream symptom (owned by Cat D S2404 — this arc's next session)
- **F-B-HIGH-1** STAFF_REQUIRED_PATHS phantom-entries cleanup OR add explicit views
- **F-B-HIGH-4** auth_views_enhanced.py `@authentication_classes([])` + `[IsAuthenticated]` per-site CRITICAL escalation
- **F-B-OWN-6** CI test-harness enforce permission-floor declarations
- **F-C-REFRESH-1** refresh discipline decision-space execution (post-Chris-verdict at xx99)
- **F-C-CSD-1** Clear-Site-Data emission on logout
- **F-C-STORE-1** 15-surface × logout-cleanup declared contract execution
- **F-C-TAB-1** cross-tab storage-event listener

### Group 2200 T-slot follow-on queue (owed to Group 2400+ execution — unchanged)

- **T1 Group 2400 Auth cross-arc handoff bundle** — being executed by THIS arc (S2401-S2404) — silent-401 + logout cleanup + session lifecycle + permission-floor uniformity — **S2403 Cat C DELIVERED session-lifecycle evidence** + Cat D S2404 owns silent-401 SYSTEMIC + typed-error envelope + T1 handoff execution readiness
- **T2 Group 2500 API cross-arc handoff bundle** — NEXT arc after Group 2400 close per S2299 §8.2 (Cat B CF-B1 + Cat C CF-C1 both elevate registry + refresh-endpoint + logout-envelope + Clear-Site-Data design-prep candidate)
- **T3 Group 2600 PA cross-arc handoff bundle** — QUEUED after Group 2500 close (Cat B CF-B2 + Cat C CF-C2 both elevate workspace-context authz + `session_tool.retire` cascade + paStore field-list completeness)
- **T4 Group 1700 Observability cross-arc handoff bundle** — QUEUED after Group 2600 close (Cat B CF-B5 + Cat C CF-C3 both elevate 503-fork asymmetry + login/logout event emit + smoke-test coverage; xx99 Observability umbrella roll-up)
- **Maintainer-decision batch (5 items governance gate)** — CODEOWNERS + DEAD-CANDIDATE consolidated cleanup + api.ts extraction + storageKeys registry + cockpitApi ownership
- **T2 post-arc T-slot (10 items)** — per S2299 §8
- **T3 conditional post-arc (4 items)** — cross-tab sync + Betting session-scoped state + runtime schema validation + REST↔WS joint T7

### S2199 post-arc T-slot execution queue (unchanged carry into S2404)

19 T-slot items distributed across 6 arcs + Employee OS per S2199 §8. All post-arc execution, NOT blocking S2404.

### Session count status

- Group 2400 In-progress at 4 of 6 sessions (S2400 parent + S2401 P1 Cat A + S2402 P2 Cat B + S2403 P3 Cat C shipped)
- Next child = S2404 P4 Cat D Frontend Integration + Silent-401 SYSTEMIC Resolution
- Next `xx99` at S2499 canonical summary (playbook §11.3 ELEVENTH application per current TENTH baseline)

## SESSION READY CHECK (before opening S2404 P4 Cat D)

Before drafting the S2404 child audit doc:

1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local` (Group 2400 arc pin `pa-6279ead1714c4630` PRESERVED through S2403; `tools/pa_local.sh:280` unchanged from S2400 open)
2. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 20-section child-audit template + §11.2 exemplar chain (S2403 P3 Cat C most recent) for shape reference
3. Read `docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md` fully — Cat D's primary Cat-C-inheritance load-bearing input; §14.2 15-surface × cleanup + §14.3 21-loci lifecycle-observability + §19.1 three-option decision space (α/β/γ) precedent for Cat D's typed-error-envelope three-option (α/β/γ)
4. Read `docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` §14 F-B-CRIT-2 silent-401 SYSTEMIC necessary-enabling-condition + §19.1 three-option decision space (a/b/c) precedent
5. Read `docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md` §7 runtime-flow-per-caller-class + §14.5 trust-boundary rate + F-DEC-1 decorator drift + F-WS-1 WS silent-swallow
6. Read `docs/research/domains/auth/2400_auth_domain_scoping.md` §3.D P4 Cat D expected outputs + §3.5 auth-adjacent probes disposition + §7.1 leak-vector guardrails
7. Read `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` §14 F3 silent-401 SYSTEMIC + F3.5 whitelist BRITTLE + A3 ~630 call-site grep baseline
8. Read `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md` §15.5 silent 401 systemic + error boundary gap
9. Dispatch 6-Explore-agent parallel sweep per playbook §13 (Agents 1-6 per §3.D expected outputs)
10. Draft the 20-section audit per §11.2 skeleton; verifier-loop per §14 discipline pre-Rigby-SIGN (especially: Rigby caught VIP invite exchange + Django logout HEAD-verification blocking-fold at Cat C Batch 2 — Cat D should PRE-EMPTIVELY HEAD-verify all load-bearing claims before Rigby-SIGN; denominator discipline pre-emption succeeded at Cat C — apply same discipline to Cat D)
11. Route to Rigby SIGN cycle 1 via dedicated fresh isolation pin per playbook §15 (child audit = required full SIGN); expected cadence 4-batch × 5-Q = 20-Q per S2201-S2403 EIGHT-consecutive tested pattern
12. Fold SIGN edits; land as `status: draft` on filesystem; present Chris ratification card
13. Arc pin `pa-6279ead1714c4630` preserved through S2404 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails + MC-14 CANDIDATE-threshold-satisfied extended-to-4-arc-stages
14. **After Cat D close: xx99 S2499 canonical summary next** — playbook §11.3 12-section canonical-summary template + §11.3 §10 meta-methodology ELEVENTH application after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299 ten prior

**S2404 open command (Chris short command):** `Continue research group 2400: P4 Cat D` or `Continue research group 2400: silent-401` or equivalent invocation.
