---
title: "Session Lifecycle + Logout Cleanup Contract Audit (Group 2400 Cat C — S2403 P3)"
session: 2403
status: active (S2403 P3 Cat C third child audit under Group 2400 Auth — EIGHTEENTH-consecutive application of playbook §11.2 20-section child-audit template after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401+S2402 prior seventeen; drafted 2026-07-05 post-6-parallel-Explore-agent sweep + parent-Claude verifier-loop per playbook §14; **Rigby SIGN cycle 1 SIGN-with-edits at MED-HIGH confidence (~0.82; higher than Cat B ~0.8) 2026-07-05 via dedicated fresh isolation pin `pa-5096f5fc07754b18` retired at cycle close (updated_count=4, previously_active=true — FOURTEENTH consecutive dedicated fresh SIGN pin retirement in Research OS after 10 xx99 + 1 parent-scoping-light-SIGN + Cat A + Cat B + this cycle); 4-batch × 5-Q = 20-Q cadence EIGHTH-consecutive application per S2201-S2402 seven-consecutive-tested pattern; MC-10 codification-ready-pending-Chris at 8-arc baseline; 32 folds landed pre-Chris-ratification per §20.6 fold ledger (29 SIGN Q folds + 3 pre-commit nit folds from ratification-card review); cycle 2 NOT required per Rigby cycle-1 sign-off + all folds landable; Chris "commit it" 2026-07-05 ratified 32-fold SIGN-with-edits wholesale at MED-HIGH confidence — status flipped `draft` → `active` per playbook §16 draft-first workflow**)
arc: Research Group 2400 (Auth — Session Lifecycle + Permission Floor + Silent-401 Resolution) — S2403 P3 Cat C third-child audit
category: research (playbook §11.2 20-section child-audit template EIGHTEENTH-consecutive application per S2402 handoff)
authors: Claude Code (S2403 draft 2026-07-05 post-6-parallel-Explore sweep + verifier-loop)
verifier_loop: >
  6 parallel Explore sub-agents run per playbook §13 (Agent 1 Session Models + Persistence,
  Agent 2 Services + Runtime Flows, Agent 3 APIs + Tools + Tasks + Commands,
  Agent 4 Integrations + Cross-Domain (15-surface × cleanup), Agent 5 Documentation +
  Prior Research, Agent 6 Drift + Debt + Ownership + Maturity). All 6 returned;
  parent-Claude verifier-loop per playbook §14 caught 1 sub-agent conflict pre-draft:

  - Agent 3 asserted `/api/v1/auth/logout-enhanced/` has "permission_classes: none";
    Agent 1 asserted `logout_enhanced_view` has `@permission_classes([IsAuthenticated])`.
    Parent verifier-loop independently read `core/auth_views_enhanced.py:539-556` and
    confirmed Agent 1: line 540 carries `@permission_classes([IsAuthenticated])`.
    Basic `/api/v1/auth/logout/` (`core/auth_views.py:84-94`) has NO permission
    decorator — silent-200 on unauthenticated confirmed at HEAD `8bc1b0c0`. Corrected
    in §6 + §7 + §14 F-C-LOGOUT-2 severity classification.

  Rigby SIGN cycle 1 CLOSED 2026-07-05 via dedicated fresh SIGN pin
  `pa-5096f5fc07754b18` (minted via `session_tool.create_fresh` at cycle open;
  retired at cycle close via `session_tool.retire` per playbook §15 SIGN-
  isolation discipline; FOURTEENTH consecutive dedicated fresh SIGN pin retirement
  in Research OS after 10 xx99 + 1 parent-scoping-light-SIGN + 2 Cat A + Cat B
  prior child audits + this cycle). 4-batch × 5-Q = 20-Q cadence EIGHTH-consecutive
  application per S2201-S2402 seven-consecutive-tested pattern (MC-10 codification-
  ready-pending-Chris at 8-arc baseline). Rigby final verdicts per batch: Batch 1
  SIGN-with-edits; Batch 2 NEEDS-MORE (blocking folds landed pre-Batch-3 via HEAD
  verifier-loop on VIP exchange + Django logout + line-drift); Batch 3
  SIGN-with-edits; Batch 4 SIGN-with-edits + explicit "close cycle" signal.
  29 folds landed pre-Chris-ratification per §20.6 fold ledger. Cycle 2 NOT
  required per Rigby cycle-1 sign-off + all folds landable.

  Rigby overall verdict — most accurate parts: F-C-STORE-1 15-surface × cleanup
  table + F-C-CSD-1 zero-emission grep + F-C-REFRESH-1 contract-absent framing +
  §14.3 21-loci lifecycle-observability rate table. Weakest parts pre-fold:
  §1 executive oscillation between "headline findings" and "HIGH count" (F20
  reconciled); F-C-VIP-1 seam-class mis-labeled as silent-swallow instead of
  declared-fictional (F3 added 4th class); acceptance-criterion scoring
  ambiguous (F2 added 2-axis Platform vs Audit); §6.1 "line not verified this
  pass" placeholders (F5-F11 HEAD-verified); §18 F-C-OWN-1 owner-UNCLEAR reading
  as defect (F26 reframed cross-arc-by-design); §19.1 "Cat C recommends" too
  authoring-adjacent (F27 tightened to "proposes β as least-assumption default").
  Biggest structural risk (Rigby Batch 2 Q9 catch): VIP invite exchange semantics
  + Django accounts/logout session.flush behavior asserted without HEAD verification;
  Batch 2 NEEDS-MORE resolved by direct file-reads at `core/views_vip_invite.py:85-163`
  + `models_vip_invite.py:95-103` + `django/contrib/auth/__init__.py:160-171`.
  What Cat C got wrong pre-SIGN: nothing conceptual — precision + wording + severity
  normalization + seam-classification vocabulary + acceptance-criterion 2-axis
  scoring were all landable folds. Final verdict: **SIGN-with-edits at
  MED-HIGH confidence** (higher than Cat A 0.74; slightly higher than Cat B ~0.8
  given denominator-discipline pre-emption succeeded and Rigby caught zero
  denominator-ambiguity findings).

  Verifier-loop DENOMINATOR DISCIPLINE (Rigby S2402 Q20 fold) PRE-EMPTIVELY
  applied throughout: every count declared with explicit denominator + grep
  anchor + HEAD-verified vs ESTIMATE-inherited distinction (see §20.4 count
  ledger). Rigby confirmed zero denominator-ambiguity findings at Cat C —
  pre-emption worked.
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                                # runtime counts anchor (no §Auth autoblock — Cat A §2 F-INV-1 preserved)
  - docs/PLATFORM_WHAT_IT_IS.md                                               # narrative anchor (no §Auth subsection — Cat A §2 F-INV-2 preserved)
  - docs/research/platform_architecture_inventory.md                          # S1273 32-domain map row 27 — Cat A + Cat B baseline
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                 # process contract §11.2 EIGHTEENTH-consecutive application
  - docs/research/OPEN_ARCS.md                                                # arc manifest (Group 2400 In-progress row update at S2403 close)
  - docs/research/domains/auth/2400_auth_domain_scoping.md                    # parent §3.C Cat C expected outputs + §3.5 auth-adjacent probes disposition (token rotation, refresh, JWT-vs-opaque, CSRF, session fixation, cookie defaults)
  - docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md  # Cat A §4 UnifiedUser + VIPInvite + Token + §7 middleware chain + §14 F-TOKEN-1 F-VIP-1 F-SESS-1 + §17 F-DUP-2 role-field bifurcation baseline
  - docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md  # Cat B §14 F-B-HIGH-3 workspace-membership implicit-gate + §17 F-B-DUP-1 4-role landscape (customer_role orphaned) + §13.5 correctness-vs-governance-axis
  - docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md   # §14.3 cockpit two-stage auth MINOR-DRIFT baseline
  - docs/research/domains/frontend/2204_frontend_session_state_persistence_discipline_audit.md  # §14 F1 15-surface storageKeys inventory + §14 F6 authStore functional-null-state + §14 F7 paStore.syncUser incomplete + §14 F8 navigationStore cross-user leakage + §19.1 R1 session-lifecycle two-sided framing (Cat C primary responsibility)
  - core/settings.py                                                          # SESSION_* + CSRF_* config (lines 980-1110) + CACHES fallback (490-500)
  - core/auth_views.py                                                        # basic login/logout endpoints (lines 24, 84)
  - core/auth_views_enhanced.py                                               # enhanced login/logout/register/reset (lines 48, 222, 297, 359, 424, 541, 562, 660)
  - core/urls.py                                                              # auth URL routes (lines 2183-2197) + accounts/logout Django path (line 1626)
  - core/models_vip_invite.py                                                 # VIPInvite.token_expires_at (72h ENFORCED) + account_expires_at (14d NOT ENFORCED — Cat A F-VIP-1 HIGH)
  - core/ws_auth_middleware.py                                                # WS auth silent AnonymousUser fallback (Cat A F-WS-1 preserved)
  - frontend/src/stores/authStore.ts                                          # Zustand persist auth-storage (logout mutates state to null; no removeItem)
  - frontend/src/stores/navigationStore.ts                                    # Zustand persist navigation-store (recentEntities cross-user leakage — S2204 F8)
  - frontend/src/stores/paStore.ts                                            # Zustand persist pa-dock-state (v3+migrate; syncUser incomplete — S2204 F7)
  - frontend/src/lib/api.ts                                                   # axios interceptor silent-401 handler (Cat D scope — referenced not audited)
  - frontend/src/components/layout/Sidebar.tsx                                # logout onClick handler (line 356 baseline)
  - frontend/src/App.tsx                                                      # ProtectedRoute wrapper + 16 cockpit legacy redirects (lines 134-149 — S2201 §14.3 baseline)
delegated_from:
  - S2400 parent scoping §3.C Cat C expected outputs (a-e) + §3.5 auth-adjacent probes disposition (CSRF conditional; cookie defaults SPECULATIVE lift; JWT-vs-opaque; session fixation; token rotation)
  - Cat A (S2401) §14 F-TOKEN-1 (Token no expiry) + F-VIP-1 (account_expires_at not enforced) + F-SESS-1 (Redis fallback silent degrade) + F-WS-1 (WS silent AnonymousUser) + §7 middleware chain + §17 F-DUP-2 role bifurcation baseline
  - Cat B (S2402) §14 F-B-HIGH-3 workspace-membership implicit-gate (CF-B2 to Group 2600 PA) + §17 F-B-DUP-1 4-role landscape (customer_role orphaned; +1 fifth-role SPECULATIVE) + §13.5 correctness-vs-governance-axis maturity framing + Q20 denominator-ambiguity emerging-weak-spot pre-emptive discipline
  - S2204 §14 F1 15-surface storageKeys (12 direct + 3 Zustand) + F6 authStore functional-null-state + F7 paStore.syncUser incomplete + F8 navigationStore cross-user leakage + §19.1 R1 session-lifecycle two-sided framing (Cat C PRIMARY responsibility)
  - S2201 §14.3 cockpit two-stage auth MINOR-DRIFT (Cat C re-verifies at HEAD `8bc1b0c0`)
delegates_to:
  - S2404 P4 Cat D Frontend Integration + Silent-401 SYSTEMIC — Cat D consumes §6.1 endpoint permission-decorator matrix + §14 F-C-LOGOUT-* silent-200-on-unauth + §14 F-C-CLEAR-SITE-DATA-1 + §19.1 three-option decision-space (α/β/γ) evidence-plan
  - S2499 xx99 canonical summary — POSTURE-DECISION evidence plan §19.1 + cross-arc coordination flags CF-C1 → CF-C7 + §7 anchor-update recommendations + §10 meta-methodology
head_commit_before: 8bc1b0c0
arc_pin: pa-6279ead1714c4630 (PRESERVED through S2403 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails + MC-14 CANDIDATE-threshold-satisfied extended-to-3-arc-stages; TWELFTH formal arc pin under Research OS; retirement at S2499 close)
sign_pin: pa-5096f5fc07754b18 (RETIRED at S2403 SIGN cycle 1 close 2026-07-05 via `session_tool.retire` per playbook §15 SIGN-isolation discipline — pending retirement API call this session; FOURTEENTH consecutive dedicated fresh SIGN pin in Research OS after 10 xx99 + 1 parent-scoping-light-SIGN + 2 prior Cat A + Cat B child audits + this cycle)
scope_shape:
  central_child_C_lens: >
    "Does the platform have a declared session lifecycle contract (issuance +
    refresh + logout + cleanup semantics all observable), or does the 'no logout
    cleanup' + 'no session lifecycle spec' pattern (S2204 §14 F6 F8 + §19.1 R1)
    leave session boundaries at BE/FE-implicit-agreement?"
  C_output_a: session model inventory — issuance (obtain_token) + refresh (ABSENT — implicit no-refresh) + logout (two endpoints) + cookie discipline (SameSite/Secure/HttpOnly/Domain/Path defaults at HEAD)
  C_output_b: 15-surface storageKeys cleanup contract per surface — declared vs accidental classification + cross-user leakage severity
  C_output_c: Clear-Site-Data header decision evidence — ZERO emission at HEAD (production-code grep confirmed); blast-radius analysis for demo-mode third-party cookies
  C_output_d: silent-refresh (α) vs explicit-re-login (β) vs hybrid (γ) three-option decision space + Cat C recommendation lean + Chris-D-verdict-request
  C_output_e: cockpit two-stage MINOR-DRIFT re-verification at HEAD 8bc1b0c0 (S2201 §14.3 baseline)
provenance:
  - S2403 draft written 2026-07-05 post-S2402 P2 Cat B close (Chris "commit it" ratified 2026-07-05)
  - 6 parallel Explore sub-agents run per playbook §13 (Agent 1-6 per §3.C Cat C expected outputs)
  - Parent-Claude verifier-loop per playbook §14 caught 1 sub-agent conflict pre-draft (see verifier_loop field above): Agent 3 vs Agent 1 on `logout_enhanced_view` permission decorator → resolved by direct `core/auth_views_enhanced.py:539-556` read; Agent 1 correct (`@permission_classes([IsAuthenticated])`)
  - HEAD-verified precise counts via direct file read + Django-side grep: SESSION config declarations = 10-of-12 (2 ABSENT: SESSION_COOKIE_DOMAIN, SESSION_COOKIE_PATH); CSRF config declarations = 5-of-7 (2 ABSENT: CSRF_COOKIE_DOMAIN, CSRF_USE_SESSIONS present at settings.py:999); Clear-Site-Data production-code emission = 0 sites; refresh-token session endpoint = ABSENT (only `refresh_token` at urls.py:2055 is third-party OAuth); logout endpoints = 2 (basic + enhanced); cockpit redirects at App.tsx:134-149 = 16 routes (S2201 baseline preserved); Zustand persist stores = 3 (authStore, navigationStore, paStore); direct localStorage keys = 12 (S2204 baseline preserved at HEAD)
  - Chris ratification pending post-Rigby-SIGN-cycle-1 close-card
owner: claude (drafted S2403; Rigby SIGN cycle 1 folds land pre-commit; Chris ratification via close-card)
---

# Session 2403 — Group 2400 Cat C — Session Lifecycle + Logout Cleanup Contract Audit

> **Static snapshot.** This audit captures the session-lifecycle + logout-cleanup
> contract at HEAD `8bc1b0c0` on `main` (2026-07-05, LOCAL). It is a photograph, not
> a session-model design. Authentication surface + trust boundaries is Cat A (S2401).
> Authorization + permission-floor uniformity is Cat B (S2402). Frontend integration
> + silent-401 execution surface is Cat D (S2404). This document delivers what
> parent §3.C Cat C required: (a) session model inventory (issuance + refresh + logout
> + cookie discipline); (b) 15-surface storageKeys × logout-cleanup contract table;
> (c) Clear-Site-Data header decision evidence; (d) silent-refresh (α) vs
> explicit-re-login (β) vs hybrid (γ) three-option decision-space + Cat C lean;
> (e) cockpit two-stage MINOR-DRIFT re-verification. Plus POSTURE-DECISION evidence
> plan §19 owed to xx99 on session-model authoring (recommend / defer / non-candidate)
> + Chris D-verdict-requests for the three-option lean.

> **Evidence-provenance discipline (inherited from S2400 §2 disclaimer + Rigby S2402
> Q20 denominator-ambiguity pre-emption).** Every load-bearing claim is either
> (a) HEAD-verified via direct file read + grep at `8bc1b0c0`, or (b) marked
> ESTIMATE-inherited from a specific prior arc doc with re-verification-at-HEAD
> status noted, or (c) marked SPECULATIVE with explicit rationale. Sub-agent claims
> verified per playbook §14 "trust but verify" — 1 conflict caught + resolved
> pre-draft (see frontmatter `verifier_loop`). Denominator explicitly declared for
> every count in §14 + §15 + §20.4.

---

## 1. Executive Summary

**Central lens answer.** The platform's session-lifecycle contract at HEAD `8bc1b0c0`
is **structurally partial** — the session/token/cookie mechanisms all work at
file-precision level (session backend runs, tokens issue + validate + delete
correctly, cookies are set with declared HTTPOnly/SameSite defaults), but **the
lifecycle contract itself is undeclared at the boundary layer**. There is no
refresh-token endpoint (F-C-REFRESH-1 ABSENT); no Clear-Site-Data emission on
logout (F-C-CSD-1 ABSENT — production-code grep zero-match confirmed); no
declared cleanup contract for 14 of 15 client-side persistence surfaces (12 direct
localStorage keys + 2 of 3 Zustand persist stores per S2204 F1 15-surface baseline
preserved at HEAD); no cookie-domain / cookie-path declaration (Django defaults
apply — S2400 §2.3 SPECULATIVE flag lifted with concrete finding); no
role-transition semantics on the 4-model role landscape (Cat A F-DUP-2 + Cat B
F-B-DUP-1 baseline; Cat C confirms zero session-scoped role semantics via grep for
`session['role']` etc.). Cockpit two-stage auth MINOR-DRIFT (S2201 §14.3)
**re-verified still-live at HEAD** (`frontend/src/App.tsx:134-149` — 16
`/cockpit/*` `<Navigate>` redirects NOT wrapped by `ProtectedRoute`).

**Central Cat C finding — session-lifecycle plane is WORKING-mechanisms +
PARTIAL-lifecycle-correctness + EXPERIMENTAL-governance** (Rigby SIGN cycle 1 Q1
fold + Rigby pre-commit nit 1 — three-axis framing avoids "WORKING correctness"
sounding like "safe/complete"; distinguishes mechanism WORKING from lifecycle-correctness
PARTIAL from governance EXPERIMENTAL):

1. **Mechanisms axis WORKING.** Every session/token/cookie mechanism succeeds at
   file-precision level. `SESSION_ENGINE = 'django.contrib.sessions.backends.cache'`
   at `core/settings.py:1105` + `SESSION_CACHE_ALIAS = 'default'` at
   `core/settings.py:1106` route sessions to Redis (or fallback LocMemCache per
   Cat A F-SESS-1). `SESSION_COOKIE_AGE = 1209600` (14d) at `core/settings.py:987`.
   Token issued via `Token.objects.get_or_create(user=user)` at 5 sites
   (`auth_views.py:53`, `auth_views_enhanced.py:120, 193, 257`, `views_vip_invite.py:131`,
   `management/commands/setup_pa_service_account.py:48`). Logout deletes token at 2
   sites (`auth_views.py:90`, `auth_views_enhanced.py:547`). Frontend `authStore.logout()`
   at `frontend/src/stores/authStore.ts:34-39` sets state to null; Zustand persist
   writes null-record.

2. **Lifecycle-correctness axis PARTIAL.** Lifecycle-relevant enforcement is missing
   in 4 HIGH-severity locations: F-C-VIP-1 (14d account_expires_at declared but
   NOT enforced), F-C-STORE-1 (14 of 15 client-side surfaces persist across
   logout), F-C-REFRESH-1 (no refresh contract), F-C-CSD-1 (no Clear-Site-Data
   emission). These are contract-declared-fictional or contract-absent, not
   mechanism failures — but they weaken lifecycle correctness beyond WORKING.

3. **Governance axis EXPERIMENTAL.** The lifecycle CONTRACT is undeclared:
   - No refresh endpoint (only `refresh_token` at `urls.py:2055` is third-party OAuth
     platform refresh — not session-token refresh)
   - No Clear-Site-Data header emission (production-code grep at HEAD returned zero
     matches; only docs + tools mention it)
   - No `SESSION_COOKIE_DOMAIN` or `SESSION_COOKIE_PATH` declaration (Django defaults
     apply implicitly)
   - No declared cleanup contract for 12 direct localStorage keys or 2 of 3 Zustand
     persist stores on logout
   - No cross-tab logout coordination (0 BroadcastChannel + 0 storage-event listeners
     — S2204 §15.7 baseline preserved at HEAD)
   - No session-scoped role semantics on 4-model role landscape
   - No login/logout structured event emission (Cat A CF-2 to Group 1700 preserved)

4. **Session fixation defense — session key rotation on auth boundary not evidenced**
   (Rigby SIGN cycle 1 Q10 fold — drop SPECULATIVE label since evidence is
   concrete grep zero-match, not intent-inferred). No `session.cycle_key()` call
   found in `core/auth_views.py` or `core/auth_views_enhanced.py`
   (grep zero-match for `cycle_key`, `session.cycle_key`, `request.session.set_expiry`).
   Django's `SessionMiddleware` does NOT automatically rotate session_key on login;
   REST auth endpoints do not call `django.contrib.auth.login()` (which would rotate)
   — they use `Token.objects.get_or_create` only. Grep confirms: 1 `login(` call at
   `core/urls.py:1626` (Django `accounts/logout/` lambda uses `logout()`, not
   `login()`; separate URL surface). **Session fixation attack surface: if the
   platform relies on Django session for anything beyond CSRF, an attacker could
   pre-set victim's sessionid before login** — but current auth architecture is
   token-centric, so session fixation blast is bounded to CSRF-token identity.

**Cat C acceptance criterion scoring** (Rigby SIGN cycle 1 Q2 fold — 2-axis
scoring: Platform outcome vs Audit outcome, to prevent "Cat C failed" misread):

| Criterion | Platform Outcome | Audit Outcome | Evidence |
|---|---|---|---|
| #1 Permission-floor observability | DEFERRED to Cat B (delivered S2402) | PASS-by-deferral | Cat B S2402 §14.5 21-loci table owns; Cat C consumes for lifecycle-relevance only |
| #2 Failure surfacing / typed error envelope | DEFERRED to Cat D | PASS-by-deferral | Cat D S2404 owns `api.ts:48-56` audit; Cat C confirms logout endpoints return silent 200 (§14 F-C-LOGOUT-1 basic + F-C-LOGOUT-2 enhanced) |
| **#3 Logout cleanup contract** | **FAIL (contract absent / not enforced at 14 of 15 surfaces)** | **PASS (evidence plan complete)** | §14.2 15-surface × cleanup table: 1 CLEAN (authStore functional-null-state), 3 PARTIAL (paStore syncUser incomplete; pipeline_dismissed workspace-key change; podcast_voice_profile_id change-cleanup), 11 NO-CLEANUP. Declared cleanup rate 1/15 (6.7%) |
| **#4 Session lifecycle discipline** | **FAIL (contract absent / not enforced at 11 of 21 lifecycle-observability loci)** | **PASS (evidence plan complete)** | §14.3 21-loci table: 5 WORKING + 5 PARTIAL + 11 DEAD; refresh endpoint ABSENT; Clear-Site-Data ABSENT; cookie-domain + cookie-path ABSENT; login/logout event emit ABSENT; role-transition semantics ABSENT |
| #5 Cross-arc coordination flags preserved | PASS-partial (7 flags emitted; xx99 needs ≥ 2 to accept) | PASS | Cat C emits 7 flags (CF-C1 → CF-C7 in §9.2 + §19) |
| #6 Trust boundary inventory | DEFERRED to Cat A (delivered S2401) | PASS-by-deferral | Cat A S2401 §14.5 14-mechanism table owns; Cat C references |

**Cat C seven headline findings** (Rigby SIGN cycle 1 Q15 fold — "headline
findings" = top items worth reading; distinct from severity distribution;
**severity: 4 HIGH + 3 non-HIGH** post-fold-normalization). Post-fold severity
distribution: HIGH = F-C-VIP-1 + F-C-REFRESH-1 + F-C-CSD-1 + F-C-STORE-1;
non-HIGH = F-C-COOKIE-1 (LOW-MED) + F-C-LOGOUT-1 (MED) + F-C-COCKPIT-1 (MED).

- **F-C-VIP-1 HIGH — `VIPInvite.account_expires_at` (14d) NOT ENFORCED at runtime**
  (Cat A F-VIP-1 preserved + HEAD-re-verified). `core/models_vip_invite.py:26-27`
  declares `_default_account_expires` = +14d; `models_vip_invite.py:72` field.
  Grep at HEAD: zero matches for `.filter(account_expires_at__` / `account_expires_at <`
  / `account_expires_at.gt` / periodic revocation task / login-time expiry check.
  `VIPReadOnlyMiddleware.__call__` at `core/vip_middleware.py:63-91` gates on
  `primary_role == 'vip_demo_viewer'` (Cat A §7) but **does NOT check expiry**.
  Blast: VIP demo accounts persist indefinitely once minted; 14d TTL is documentary
  fiction. **Class: `technical_debt` + `unclear_owner`.** Cat C promotes from
  Cat A finding to lifecycle-CONTRACT gap.

- **F-C-REFRESH-1 HIGH — No session-token refresh endpoint exists.** Grep at HEAD
  8bc1b0c0 for `path.*refresh` in `core/urls.py`: 3 matches — `intelligence/spiders/refresh/`
  (line 1925), `distribution/oauth/<str:platform>/refresh/` (line 2055 — third-party
  OAuth platform token refresh, NOT session-token), `agents/discovery/refresh/` (line
  3071). Zero session-token refresh endpoint. Grep for `TokenRefresh` / `RefreshView`
  / `token/refresh` in `auth_views*.py`: zero matches. Combined with Cat A F-TOKEN-1
  (DRF `authtoken.Token` no expiry): the platform's implicit contract is "token
  is permanent absent password change / reset / logout event." No refresh-token
  discipline exists; the "declared refresh posture" (S2400 §3.C acceptance criterion
  #4) is **implicit no-refresh, unobservable at boundary**. **Class: `missing_connection`
  + `technical_debt`.** Blocker to acceptance criterion #4.

- **F-C-CSD-1 HIGH — Zero Clear-Site-Data header emission at HEAD.** Production-code
  grep for `Clear-Site-Data` returns matches ONLY in docs + `tools/pa_local.sh:39`
  (comment) — zero matches in `core/` or `frontend/`. Neither `logout_view` at
  `core/auth_views.py:84-94` nor `logout_enhanced_view` at
  `core/auth_views_enhanced.py:539-556` emits Clear-Site-Data. Browser cookies + cache
  + storage persist across the auth boundary. **Blast-radius analysis for demo-mode
  third-party cookies** (per S2400 §3.C output (c)): Clear-Site-Data with directives
  `cookies`, `cache`, `storage`, `executionContexts` would clear ALL cookies for the
  origin; if demo mode relies on cross-origin cookie residue (unlikely given
  `SESSION_COOKIE_SAMESITE='Strict'` in prod at `core/settings.py:986`), blast is
  contained. Recommend `Clear-Site-Data: "cookies", "storage"` on logout response as
  minimum-viable emission. **Class: `drift` + `missing_connection`.**

- **F-C-STORE-1 HIGH — 14 of 15 client-side persistence surfaces lack DECLARED
  logout-cleanup contract.** HEAD-re-verified S2204 §14 F1 baseline (15 surfaces:
  3 Zustand persist + 12 direct localStorage). Zero new keys added since S2204 close
  `8fbf17eb` (grep confirmed at HEAD). Per-surface cleanup contract in §14.2 table:
  1 CLEAN (`auth-storage` via `authStore.logout()` functional-null-state — S2204 F6),
  3 PARTIAL (`pa-dock-state` via `paStore.syncUser(null)` incomplete field-list —
  S2204 F7; `pipeline_dismissed_${workspaceId}` via workspace-change removeItem;
  `podcast_voice_profile_id` via profile-change removeItem), 11 NO-CLEANUP. Cross-user
  leakage severity per surface: `navigation-store` recentEntities MED (breadcrumb
  identity leak — S2204 F8); `pa-dock-state` MED-HIGH (last 50 PA messages + workspace
  context); `podcast_voice_profile_id` MED (voice preference identity signal); others
  LOW-NONE (UI state only). **Class: `technical_debt` + `drift`.** Blocker to
  acceptance criterion #3.

- **F-C-COOKIE-1 LOW-MED (documentary gap only) — `SESSION_COOKIE_DOMAIN` +
  `SESSION_COOKIE_PATH` + `CSRF_COOKIE_DOMAIN` NOT declared** (S2400 §2.3
  SPECULATIVE flag LIFTED with concrete finding; Rigby SIGN cycle 1 Q3 fold +
  pre-commit nit 2: downgraded from MED to LOW-MED — **Django defaults are
  correct at HEAD; risk is drift if later subdomain/path scoping is introduced.**
  Severity is documentary + future-subdomain-contingent, not immediate-user-harm). Grep at HEAD 8bc1b0c0 across
  `core/settings*.py`: zero matches for `SESSION_COOKIE_DOMAIN`,
  `SESSION_COOKIE_PATH`, `CSRF_COOKIE_DOMAIN`. Django defaults apply:
  `SESSION_COOKIE_DOMAIN=None` (current origin only), `SESSION_COOKIE_PATH='/'`
  (whole app), `CSRF_COOKIE_DOMAIN=None`. Behavior is correct-by-default but
  undocumented; if the platform ever needs sub-domain cookie sharing
  (`.donkeybetz.com`) or path-scoped cookies, no baseline exists. HEAD-verified
  declared cookie config: `SESSION_COOKIE_AGE` at `:987`, `SESSION_EXPIRE_AT_BROWSER_CLOSE`
  at `:988`, `SESSION_COOKIE_HTTPONLY` at `:981` (dev) / `:985` (prod),
  `SESSION_COOKIE_SECURE` at `:980` (dev) / `:984` (prod), `SESSION_COOKIE_SAMESITE`
  at `:982` (dev: 'Lax') / `:986` (prod: 'Strict'), `SESSION_SAVE_EVERY_REQUEST=True`
  at `:1103`, `SESSION_COOKIE_NAME='sessionid'` at `:1104`. **Class: `drift` (documentary).**

- **F-C-LOGOUT-1 MED — Basic logout endpoint (`core/auth_views.py:84-94`) has NO
  permission decorator** (Cat A note preserved + HEAD-verified). Unauthenticated
  POSTers get 200 with `{'detail': 'Logout successful'}` because
  `request.user.auth_token.delete()` raises `AttributeError` on AnonymousUser →
  caught by `except Exception` → 200 returned. **The enhanced endpoint at
  `core/auth_views_enhanced.py:539-556` HAS `@permission_classes([IsAuthenticated])`
  at line 540** (Agent 3 said this endpoint has no permission decorator — HEAD-verified
  wrong; Agent 1 correct). Neither endpoint calls `django.contrib.auth.logout(request)`
  (Django session flush) — the sole verified `logout(request)` call is at
  `core/urls.py:1626` (Django `accounts/logout/` lambda — separate surface). Neither
  endpoint emits Clear-Site-Data (F-C-CSD-1). Neither emits a structured event.
  **Class: `drift` + `technical_debt`.**

- **F-C-COCKPIT-1 MED — Cockpit two-stage auth MINOR-DRIFT re-verified STILL-LIVE
  at HEAD.** `frontend/src/App.tsx:134-149` — 16 `/cockpit/*` `<Navigate>` redirects
  are NOT wrapped by `ProtectedRoute`; they Navigate to `/workspace?tab=X&sub=Y`
  protected targets. S2201 §14.3 baseline behavior UNCHANGED (Agent 2 direct
  file:read at HEAD confirmed). Unauthenticated users see momentary client-side
  redirect before `ProtectedRoute` gates them. **Severity LOW-MED** (S2201 baseline
  LOW; Cat C bumps to MED because this is now a re-verification-at-HEAD signal, not
  a new discovery — the pattern has persisted through Group 2200 close + Group 2400
  Cat A + Cat B without remediation). Post-arc T-slot decision (S2201 §14.3
  recommendation preserved): (i) wrap `/cockpit/*` in `ProtectedRoute`, (ii)
  explicitly document as Phase 1 legacy, OR (iii) retire cockpit routes entirely.
  **Class: `drift`.**

**S2400 §2.4 canonical-seam-candidate application to Cat C findings** (Rigby SIGN
cycle 1 Q4 fold — added 4th class "declared-fictional" to distinguish
"declared-but-not-enforced" from "silent-swallow" of actual code path):

- F-C-VIP-1 (account_expires_at declared in model at `models_vip_invite.py:72` but
  ZERO runtime enforcement — TTL is documentary fiction) → **declared-fictional class**
- F-C-REFRESH-1 (no refresh contract; token permanent absent password event → never
  declared in first place) → **contract-absent class**
- F-C-CSD-1 (no Clear-Site-Data header emission; never declared) → **contract-absent class**
- F-C-STORE-1 (14 of 15 surfaces persist silently across logout; cleanup not
  declared per surface) → **silent-swallow class (aggregate) + contract-absent per-surface**
- F-C-COOKIE-1 (Django defaults undocumented — SPECULATIVE at parent scope LIFTED
  to CONCRETE at Cat C) → **contract-absent class (with correct-by-default behavior)**
- F-C-LOGOUT-1 (silent 200 on unauthenticated basic logout; actual code path
  swallows AttributeError) → **silent-swallow class**
- F-C-LOGOUT-2 (silent 200 on token-delete exception even with `IsAuthenticated`
  guard) → **silent-swallow class**
- F-C-COCKPIT-1 (client-side redirect silently visible before protection kicks in) → **silent-swallow class (bounded)**

**Class distinctions (Rigby SIGN cycle 1 Q4 fold vocabulary — reusable for xx99
codification):**
- **silent-swallow** — actual code path catches / discards / bypasses a failure
  signal (F-C-LOGOUT-1/2, F-C-COCKPIT-1, F-SESS-1 fallback, F-WS-1 anon)
- **contract-absent** — no code path exists in either direction — the contract
  was never declared (F-C-REFRESH-1, F-C-CSD-1, F-C-COOKIE-1 Domain/Path)
- **declared-fictional** — declared in code/config/comment but no enforcement
  path exists (F-C-VIP-1 account_expires_at; and by extension any "field exists,
  enforcement missing" pattern)
- **partial-contract** — contract exists but scope is incomplete (F-C-STORE-1
  per-surface — some declared, most not)

**Cat C weak-spot Q20-fold codification candidate (per playbook §20 two-triggers
threshold):** **silent-degrade vs explicit-failure ambiguity on session-lifecycle
plane**. Cat B introduced denominator-ambiguity as its Q20 fold. Cat C's candidate
extends this to a session-plane-specific pattern: the platform's session boundary
has **zero explicit-failure paths** — every session/lifecycle failure either soft-degrades
(F-SESS-1 Redis-fallback, F-WS-1 silent AnonymousUser), silently swallows (F-C-LOGOUT-1
silent-200, F-C-CSD-1 no header), or omits the contract entirely (F-C-REFRESH-1,
F-C-COOKIE-1, F-C-STORE-1 14/15 surfaces). Second application would trigger playbook
§20 codification-candidate promotion at S2499 xx99 close. **Distinct from Cat B
denominator-ambiguity**: Cat B is a measurement problem (what's the denominator?);
Cat C is a governance-observability problem (is the failure declared?).

Xx99 §4 will consolidate cross-cutting patterns.

## 2. Domain Purpose

**Q1 — What is this Cat C audit for? (one-sentence purpose):** Enumerate the
platform's session-lifecycle contract at static snapshot at HEAD `8bc1b0c0` —
issuance + refresh + logout + cookie discipline + 15-surface client-side cleanup +
role-transition semantics + cockpit two-stage drift — testing whether the S2400
§3.C acceptance criteria #3 (logout cleanup) + #4 (session lifecycle discipline)
are met by declared observable contract or by implicit BE/FE agreement.

**Q2 — What problem does it solve? (business / platform problem):** S2204 §19.1 R1
identified session-lifecycle contract as HIGH-priority active-research owed to Auth
arc. Cat A (S2401) surfaced token-model findings (F-TOKEN-1 no expiry, F-VIP-1
14d not enforced, F-SESS-1 Redis fallback) without authoring the lifecycle
CONTRACT. Cat B (S2402) surfaced authorization-plane workspace-membership implicit-gate
(F-B-HIGH-3) with session-lifecycle implications (workspace context lifecycle
across logout). Cat C consolidates the two-sided FE-symptom-vs-BE-model framing
into a single lifecycle-CONTRACT evidence plan so S2404 Cat D can audit the
frontend integration surface with a HEAD-verified session-model in hand and
S2499 xx99 can produce Chris-D-verdict-ready three-option decision-space.

**Q3 — What does the Cat C audit NOT do? (anti-scope alignment):**

- No fixes / no PRs — read-only research per playbook §14.
- No session-model authoring (parent §7 anti-scope #5 + Cat C parent §3.C
  design-preparation only) — Cat C delivers evidence + Chris-D-verdict-request on
  three-option decision space; session-model ADR authoring is post-arc.
- No refresh-token endpoint authoring or token-expiry-field migration — Cat C
  surfaces F-C-REFRESH-1 as EVIDENCE for xx99 POSTURE-DECISION; migration is Group
  2500 API arc scope if option (α) or (γ) chosen.
- No Clear-Site-Data emission authoring — Cat C recommends emission as minimum
  contract; implementation is post-arc.
- No frontend api.ts silent-401 audit (Cat D S2404 scope) — Cat C confirms
  authStore.logout() functional-null-state pattern at HEAD; Cat D audits caller-side.
- No PA behavior spec (Cat B CF-B2 to Group 2600 PA preserved) — Cat C flags
  paStore workspace-context lifecycle on logout as CF-C2 handoff.
- No mobile session-lifecycle authoring (Group 2300 Mobile scope) — Cat C flags
  `MobilePushToken.revoked_at` integration gap as CF-C4 (extending Cat A CF-4).
- No threat-model authoring (parent anti-scope; Cat A F-DOC-2 preserved) — Cat C
  inventories session-lifecycle-adjacent probes only.
- No new auth provider additions (SSO/OAuth) — parent §7 anti-scope #6 preserved.
- No Group 1900 authority-plane crossings — Cat C's KillSwitch consumer flag
  (CF-C7) is a coordination question, not authority-plane authoring.
- No password policy / MFA / lockout audit — parent §3.5 non-candidates preserved.
- No fixing findings — Every child audit surfaces findings; none of them are fixed
  inside Cat C. Findings graduate to T-slot post-arc queue at S2499 xx99 close.

---

## 3. Canonical Entry Points

HEAD-verified file:line anchors at `8bc1b0c0`. Line references are static
snapshots; S2400 §2 evidence-provenance ESTIMATE labels LIFTED here where Cat C
re-verifies.

**Session-backend + cookie config (`core/settings.py`):**

| Entry Point | File:Line | Purpose |
|---|---|---|
| `SESSION_ENGINE = 'django.contrib.sessions.backends.cache'` | `core/settings.py:1105` | Session persistence via cache alias (not DB) |
| `SESSION_CACHE_ALIAS = 'default'` | `core/settings.py:1106` | Cache alias used for session storage (Redis normally; LocMemCache on F-SESS-1 fallback) |
| `SESSION_COOKIE_AGE = env_int('SESSION_COOKIE_AGE', 1209600)` | `core/settings.py:987` | 14d absolute cookie TTL |
| `SESSION_EXPIRE_AT_BROWSER_CLOSE = env_bool(..., False)` | `core/settings.py:988` | Session persists beyond browser close |
| `SESSION_SAVE_EVERY_REQUEST = env_bool(..., True)` | `core/settings.py:1103` | Session touched every request → sliding-window extends TTL |
| `SESSION_COOKIE_NAME = env('SESSION_COOKIE_NAME', 'sessionid')` | `core/settings.py:1104` | Django default cookie name |
| `SESSION_COOKIE_SECURE` (dev False; prod env_bool default True) | `core/settings.py:980, 984` | HTTPS-only in prod |
| `SESSION_COOKIE_HTTPONLY` (dev True; prod env_bool default True) | `core/settings.py:981, 985` | Prevents JS access |
| `SESSION_COOKIE_SAMESITE` (dev 'Lax'; prod env default 'Strict') | `core/settings.py:982, 986` | Cross-site cookie transmission |
| `SESSION_COOKIE_DOMAIN` | **ABSENT** | Django default None — current origin only (F-C-COOKIE-1) |
| `SESSION_COOKIE_PATH` | **ABSENT** | Django default '/' (F-C-COOKIE-1) |
| `CSRF_COOKIE_SECURE` (dev False; prod env_bool default True) | `core/settings.py:992, 996` | HTTPS-only in prod |
| `CSRF_COOKIE_HTTPONLY` (dev False for WS; prod env_bool default True) | `core/settings.py:993, 997` | JS access allowed in dev |
| `CSRF_COOKIE_SAMESITE` (dev 'Lax'; prod env default 'Strict') | `core/settings.py:994, 998` | Cross-site policy |
| `CSRF_USE_SESSIONS = env_bool(..., False)` | `core/settings.py:999` | CSRF token in COOKIE not session |
| `CSRF_TRUSTED_ORIGINS` (env-comma-split) | `core/settings.py:712, 722-723` | localhost:3000/8080/5173 defaults |
| `CSRF_COOKIE_NAME = env('CSRF_COOKIE_NAME', 'csrftoken')` | `core/settings.py:1110` | Django default cookie name |
| `CSRF_COOKIE_DOMAIN` | **ABSENT** | Django default None (F-C-COOKIE-1) |
| `CACHES['default']` (Redis backend) | `core/settings.py:450-467` | Primary cache config (KEY_PREFIX='udb', TIMEOUT=300s default) |
| CACHES Redis-unreachable fallback → LocMemCache | `core/settings.py:490-500` | **F-SESS-1** (Cat A): silent fallback; multi-process sessions break; warning log at line 500 |

**REST auth endpoints (`core/urls.py:2183-2197`):**

| Endpoint | Route Line | View File:Line | Purpose |
|---|---|---|---|
| `/api/v1/auth/login/` | `urls.py:2183` | `core/auth_views.py:24-81` | Basic login; issues Token via `get_or_create`; response includes `token, user{id, username, email, credits, subscription, platform_role}` |
| `/api/auth/login/` (v0 compat) | `urls.py:2184` | Same view | Cat A F-DEBUG-3: compat alias bypasses rate-limit path (RateLimitingMiddleware disabled per F-RATE-1 regardless) |
| `/api/v1/auth/logout/` | `urls.py:2185` | `core/auth_views.py:84-94` | Basic logout; **no permission decorator**; token-delete in try/except → silent 200 (F-C-LOGOUT-1) |
| `/api/v1/auth/login-enhanced/` | `urls.py:2191` | `core/auth_views_enhanced.py:222-294` | Enhanced login; rate-limited 5/300s (documentary — F-RATE-1); optional remember_token |
| `/api/v1/auth/forgot-password/` | `urls.py:2192` | `core/auth_views_enhanced.py:299` (HEAD-verified) | Rate-limited 3/3600s (documentary); no token side-effect |
| `/api/v1/auth/reset-password/` | `urls.py:2193` | `core/auth_views_enhanced.py:359` (HEAD-verified) | **NOT rate-limited** (Cat A F-DEBUG-2); rotates token via `filter(user).delete() + create(user)` at `:396-399,460-461` |
| `/api/v1/auth/logout-enhanced/` | `urls.py:2196` | `core/auth_views_enhanced.py:539-556` | Enhanced logout; **HAS `@permission_classes([IsAuthenticated])` at line 540**; token-delete in try/except → silent 200 (F-C-LOGOUT-2) |
| `/api/v1/auth/validate-token/` | `urls.py:2197` | `core/auth_views_enhanced.py:559-599` | **`@authentication_classes([])` explicit-empty + `AllowAny` + no rate limit** (Cat A F-DEBUG-2 preserved) — token oracle |
| `/api/v1/auth/register/` | (verify urls.py) | `core/auth_views_enhanced.py:50` (HEAD-verified) | Registration; issues Token on verify (dev auto-verify) |
| `/api/v1/auth/change-password/` | (verify urls.py) | `core/auth_views_enhanced.py:424` (HEAD-verified) | Requires `IsAuthenticated`; **does NOT rotate token** (only reset-password rotates per F-TOKEN-1) |
| `/api/v1/auth/verify-email/` | (verify urls.py) | `core/auth_views_enhanced.py:170` (HEAD-verified) | Verify + issue token on success |
| `/api/v1/auth/user/` (current user) | (verify urls.py) | `core/auth_views.py:97+` | Read-only user probe |
| `/api/v1/auth/debug/` | **PHANTOM** (Cat A F-DEBUG-1) | `core/auth_views_enhanced.py:660` (HEAD-verified) | Import at `urls.py:1035` but NO `path()` binding; `PUBLIC_PATHS` reserves slot |
| `/api/v1/auth/resend-verification/` | (verify urls.py) | `core/auth_views_enhanced.py:604` (HEAD-verified) | Not rate-limited |

**Django-native session flush endpoint (separate surface — not REST):**

| Endpoint | Route Line | Behavior |
|---|---|---|
| `/accounts/logout/` | `core/urls.py:1626` | `lambda request: (logout(request), redirect('/login'))[1]` — calls Django `auth.logout(request)` at `django/contrib/auth/__init__.py:160-171` which calls `request.session.flush()` at line 171 (HEAD-verified per Rigby SIGN cycle 1 Q9(b) fold — Django stdlib evidence at Python 3.11.6 site-packages); redirects to `/login`. **Not consumed by frontend REST client** (frontend uses `/api/v1/auth/logout/` or `/logout-enhanced/`). Session flush occurs on this path only. |
| `/accounts/login/` | `core/urls.py:1625` | `login_redirect` view — legacy Django redirect handler |

**VIP invite exchange surface:**

| Endpoint | Route | View File:Line | Purpose |
|---|---|---|---|
| `/api/v1/vip-invites/create/` | (verified via S2401 §3) | `core/views_vip_invite.py:28` | Admin creates invite; no token side-effect |
| `/api/v1/vip-invites/exchange/` | (verified via S2401 §3) | `core/views_vip_invite.py:85-163` (HEAD-verified) | `@permission_classes([AllowAny])` at `:84`; validates via `invite.is_valid` property at `:96` — property at `core/models_vip_invite.py:95-103` checks `revoked_at is None AND redeemed_at is None AND token_expires_at > now` — **ONLY `token_expires_at` (72h) enforced, NOT `account_expires_at`** (F-C-VIP-1 evidence-tight); creates VIP `UnifiedUser` at `:101-105`; sets `EnhancedUserProfile.primary_role='vip_demo_viewer'` at `:110-112`; creates `AssistantProfile(role='vip_viewer', workspace=invite.workspace)` at `:117-127`; **`Token.objects.get_or_create(user=vip_user)` at `:131`**; marks `invite.redeemed_at=now`, `redeemed_by=vip_user` at `:134-136`; **response body includes `expires_at=invite.account_expires_at.isoformat()` at `:161` — server tells client an expiry date it will NEVER enforce** (F-C-VIP-1 aggravator per Rigby SIGN cycle 1 Q9(a) fold — declared-fictional contract with client-visible surface) |
| `/api/v1/vip-invites/revoke/` | (verified via S2401 §3) | `core/views_vip_invite.py:168-200` | Admin revokes; `invite.revoked_at = now()`; sets `invite.redeemed_by.is_active = False` (implicit token invalidation via `is_active` check on next auth); **DOES NOT explicitly delete redeemed_by user's Token**; **DOES NOT close open WS connections** |

**WebSocket auth surface (Cat A §14 F-WS-1 preserved):**

| Entry Point | File:Line | Behavior |
|---|---|---|
| `TokenAuthMiddlewareStack` (ACTIVE) | `core/ws_auth_middleware.py:24-52` | Non-enforcing; `get_user_from_token()` at lines 14-21 returns `AnonymousUser()` on `Token.DoesNotExist` (silent-swallow); connection proceeds |
| `WebSocketAuthenticationMiddleware` (DEAD) | `core/auth_middleware.py:739-822` | Would 4001-close if enabled; **NOT installed** — `core/asgi.py:25-32` imports from `ws_auth_middleware.py` not `auth_middleware.py`; `REQUIRE_WEBSOCKET_AUTH` at `core/settings.py:625` silently ignored |
| Per-consumer enforcement | 11 consumers | `PAConversationConsumer.consumers_pa_conversation.py:183` hard-rejects anon 4001; 10 other consumers accept anon with feature-gating only |

**Frontend session-state surfaces:**

| Entry Point | File:Line | Purpose |
|---|---|---|
| `useAuthStore` Zustand persist | `frontend/src/stores/authStore.ts:21-52` | `logout()` at lines 34-39 sets state to null; Zustand persist writes null-record to `auth-storage` localStorage key; **no `removeItem` call** (S2204 F6 functional-null-state) |
| `useNavigationStore` Zustand persist | `frontend/src/stores/navigationStore.ts:45-104` | `recentEntities` persist; `clearHistory` action exists (line 96-97) but **NEVER called on logout** (S2204 F8) |
| `usePAStore` Zustand persist (v3+migrate) | `frontend/src/stores/paStore.ts:155-431` | `syncUser(null)` at lines 182-194 wipes messages/conversations/currentInput; **does NOT wipe activeTool/recentTool/seenSeqs/agentCompletionQueue/seenCompletions/recentAgentCompletion** (S2204 F7 incomplete field-list) |
| `useWorkspaceStore` in-memory only | `frontend/src/stores/workspaceStore.ts:24-27` | **No persist** — activeWorkspace lost on F5 (S2204 F5 MED-HIGH; CF-C2 to Group 2600 PA) |
| `api.ts` interceptor silent-401 | `frontend/src/lib/api.ts:43-62` | On 401 for auth-endpoints: `useAuthStore.getState().logout()` + redirect `/login`; other 401s pass through (S2203 F3 SYSTEMIC — Cat D scope) |
| `Sidebar.tsx` logout onClick | `frontend/src/components/layout/Sidebar.tsx:356` (S2204 baseline) | Calls `api.post('/v1/auth/logout/')` then `paStore.syncUser(null)` then `authStore.logout()` |
| `ProtectedRoute` wrapper | `frontend/src/App.tsx:47-59` | Redirects to `/login` if `!isAuthenticated` |
| 16 `/cockpit/*` legacy redirects | `frontend/src/App.tsx:134-149` | `<Navigate to="/workspace?tab=…">` NOT wrapped by `ProtectedRoute` (F-C-COCKPIT-1 MINOR-DRIFT re-verified STILL-LIVE) |

**PA session-adjacent tools (session_tool actions at `core/services/td_handlers_core.py`):**

| Action | File:Line | Purpose | Cat C Relevance |
|---|---|---|---|
| `session_tool.create_fresh` | `core/services/td_handlers_core.py:3984` | Mint new PA conversation pin | Orthogonal to platform session lifecycle (conversation-scope, not user-session-scope) |
| `session_tool.retire` | `core/services/td_handlers_core.py:4019` | Mark conversation `session_active=False` | Cat A F-PA-1 preserved (no ownership check); **Cat C CF-C2 question: should user-logout retire active conversation pins?** |
| `session_tool.set_active` | `core/services/td_handlers_core.py:4074` | Un-retire conversation | Same as retire |
| `session_tool.seed` | `core/services/td_handlers_core.py:4109` | Backfill conversation with starter context | Same as retire |
| `session_tool.whoami` | `core/services/td_handlers_core.py:3986` | Return current user_id | Consumes but does not mutate session |

---

## 4. Major Models

Cat A §4 delivered the full session-adjacent model inventory. Cat C's addition is
LIFECYCLE-relevance annotation per model + HEAD-verification of expiry/revocation
enforcement per model. Duplicate model rows preserved from Cat A §17 + Cat B §17.

| Model | File:Line | Owner | Lifecycle Fields | Cat C Lifecycle Finding |
|---|---|---|---|---|
| `UnifiedUser` (`AUTH_USER_MODEL`) | `core/models/base/models.py:86` | this-domain | `is_active` (deactivation gate); `last_login` (Django auto); `platform_role`; `customer_role` (F-B-DUP-1 orphaned) | Survives logout; role fields persist across sessions; **no session-scoped role transition** (grep zero-match for `session['role']`) |
| `EnhancedUserProfile` | `core/models/users/models.py:370` | this-domain | `primary_role` (VIP gate); `data_retention_days` (NOT auto-enforced — Cat A F-OWN-2) | Survives logout; `primary_role='vip_demo_viewer'` VIP gate persists indefinitely |
| `AssistantProfile` | `core/models_assistant_profile.py:90` | this-domain | `role` (PA-payload gate: admin/vip_viewer/customer); `workspace` FK to ProjectWorkspace (F-BND-1) | Survives logout; PA-payload role persists indefinitely; **workspace FK is Group 2600 PA scope (CF-C2)** |
| `VIPInvite` | `core/models_vip_invite.py:30` | this-domain | `token_expires_at` (72h — ENFORCED at exchange line 151-156); `account_expires_at` (14d — **NOT ENFORCED** F-C-VIP-1); `used_at`, `redeemed_at`, `revoked_at` | **F-C-VIP-1 HIGH re-verified at HEAD** — grep zero-match for `.filter(account_expires_at__`; no middleware check; no cleanup task |
| `rest_framework.authtoken.Token` | DRF (third-party) | foreign | `key` (opaque 40-char hex); `user` OneToOneField; `created` (auto_now_add) — **NO EXPIRY, NO last_used** (Cat A F-TOKEN-1) | Rotates only on password change/reset/logout event; **no refresh contract** (F-C-REFRESH-1 HIGH); token permanent absent explicit rotation |
| Django Session (Redis-backed) | Django stdlib via `backends.cache` | foreign | `SESSION_COOKIE_AGE=1209600` (14d); `SESSION_SAVE_EVERY_REQUEST=True` (sliding window) | **F-SESS-1 preserved**: Redis fallback to LocMemCache silently degrades multi-worker sessions at `core/settings.py:490-500`; no Django `clearsessions` task scheduled |
| `DiscordLinkCode` | `core/models/base/models.py:224-274` | this-domain | `expires_at` (default +10min); `is_expired` property | Short-lived; expiry enforced on redemption; no automatic cleanup task; not affected by user logout |
| `MobilePushToken` | `core/models_mobile.py:9-33` | this-domain | `token` (Expo push token); `revoked_at` (soft-delete); `last_seen_at` | **CF-C4 gap**: logout endpoints do NOT set `revoked_at`; mobile app may continue receiving pushes post-logout |
| `FleetServiceKey` | `core/models/fleet.py:131` | this-domain | `secret_hash` (SHA256); rotation validity window; dual-active | 4-stage rotation state machine; **fleet identity independent of user-session** (CF preserved to Cat A F-BND-2/3 fleet contract) |
| `FleetAuthAuditLog` | `core/models/fleet.py:252` | this-domain | Per-request audit (deny always; allow conditional) | Cat A F-OWN-3 UNBOUNDED-RETENTION preserved; not user-session-scoped |
| `FleetPAChatAuditRow` | `core/models/fleet.py:570` | this-domain | PA chat auth-mode audit; warn-only | Same retention gap; not user-session-scoped |
| `Tenant` | `core/models_tenant.py:15` | this-domain | Session 1039 Phase 1 unused | Survives logout; `customer_role` orphaned per F-B-DUP-1 |

**HEAD-verified session-lifecycle-relevant model count:** 6 models with session-lifecycle
implications (UnifiedUser, EnhancedUserProfile, AssistantProfile, VIPInvite, DRF
Token, Django Session). Others carry adjacent state (DiscordLinkCode short-lived,
MobilePushToken device-scoped, Fleet models identity-scoped) but do not participate
in user-session lifecycle directly.

**Role-field 4-model landscape (Cat A F-DUP-2 + Cat B F-B-DUP-1 preserved; Cat C
HEAD-re-verification for session-scope):**

| Model | Field | Choices | Session-Scope Semantics |
|---|---|---|---|
| `UnifiedUser.platform_role` | `models/base/models.py:101-113` | 6 values (admin/sports_analyst/content_creator/agent_manager/unified_user/reviewer) | Account-persistent; **grep zero-match for session-scoped mutation** |
| `UnifiedUser.customer_role` | `models/base/models.py:123-132` | 3 values (viewer/user/org_admin) | Account-persistent; orphaned (F-B-DUP-1); grep zero-match for any read for auth decision |
| `EnhancedUserProfile.primary_role` | `models/users/models.py:384` | Free-text; VIP gate on `'vip_demo_viewer'` | Account-persistent; VIP HTTP gate at `vip_middleware.py:98` |
| `AssistantProfile.role` | `models_assistant_profile.py:99` | 3 values (admin/vip_viewer/customer) | Account-persistent; PA payload gate via `ROLE_PROMPTS` + `ROLE_TOOLS` |

**Cat C HEAD-verified SPECULATIVE-FIFTH-role probe (per Cat B Q13 fold):**
- **JWT libraries:** grep for `import jwt`, `import PyJWT`, `import jose`, `from
  SimpleJWT` — ZERO production imports (only regex for JWT-token REDACTION at
  `core/services/tool_dispatcher.py:1242`). **ABSENT** confirmed.
- **Django Group/Permission M2M:** grep for `user.groups.add`, `user.user_permissions.add`
  — ZERO matches. **ABSENT** confirmed. Dormant per Cat B F-B-LOW-1.
- **Feature-flag roles:** grep for `FLAGS.*role|feature_flag.*role|waffle.*role`
  — ZERO matches. **ABSENT** confirmed.

**Verdict:** 4-model role landscape is complete — no fifth-role carrier at HEAD.
Cat B F-B-DUP-1 SPECULATIVE-fifth-role hypothesis **NEGATIVELY VERIFIED FOR
S2403 SNAPSHOT** (Rigby SIGN cycle 1 Q7(a) fold — Cat C closes for this snapshot;
Cat B keeps the SPECULATIVE label for its own follow-up ownership if the
hypothesis needs re-testing under different scope; boundary preserved).

**F-C-ROLE-1 finding:** 4-role landscape has **zero session-scope semantics** —
role changes are only observable to the session after re-login. Grep patterns
`session['role']`, `session['effective_role']`, `request.session.__setitem__.*role`
returned zero matches. If the platform needs "role elevation for privileged action"
(e.g., admin action requires re-authentication) or "role revocation during active
session" (e.g., customer downgraded mid-session), the current model has no mechanism.
**Severity: LOW-observational** (Rigby SIGN cycle 1 Q7(b) fold — downgraded from
MED because platform currently has NO documented requirement for mid-session role
transitions; admin actions don't require privileged re-auth; customer downgrade
not a workflow; VIP expiry NOT enforced anyway per F-C-VIP-1. If a future workflow
introduces mid-session role changes, escalate; today the absence is not blast-radius-
active). Documented as F-C-ROLE-SCOPE in §14.

---

## 5. Major Services

Cat A §5 tabulated middleware + auth-service inventory. Cat C's addition is
LIFECYCLE-service-relevance only.

**Non-session auth artifacts (out-of-scope for Cat C session lifecycle — Rigby
SIGN cycle 1 Q6 fold — noted for completeness only):**
- `DiscordLinkCode` (10-min expiry at `core/models/base/models.py:224-274`) —
  one-time link/code expiry mechanism; not a session establishment/rotation/termination
  surface. Auth-adjacent only.
- Django `PasswordResetTokenGenerator` (via `/api/v1/auth/forgot-password/` +
  `/reset-password/`) — credential recovery mechanism; affects credentials + Token
  rotation but doesn't create/rotate/destroy session/cookies at session-boundary
  level. Auth-adjacent only.
- `MobilePushToken` — device-scoped push credential; cross-referenced under
  CF-C4 handoff, not in-scope for Cat C's session-lifecycle plane audit.

**Session-lifecycle-relevant service surfaces:**

| Service Locus | File:Line | Cat C Lifecycle Role |
|---|---|---|
| Django `SessionMiddleware` (position 5) | `core/settings.py:217-242` MIDDLEWARE list | Populates `request.session` from Redis (or LocMemCache F-SESS-1); auto-writes on any session mutation |
| Django `AuthenticationMiddleware` (position 9) | Same | Populates `request.user` from session (Django session auth path) |
| `UnifiedTokenAuthenticationMiddleware` (position 10) | `core/auth_middleware.py:85-736` | Primary HTTP token+session auth (Cat A §7); runs 5-path dispatch (PUBLIC → PUBLIC_EXACT → OPTIONAL → session → token) |
| `DisableCSRFForAuthEndpoints` (position 7) | `core/middleware.py` | Custom CSRF carve-out for auth endpoints |
| `CsrfViewMiddleware` (position 8) | Django stdlib | CSRF enforcement (uses CSRF_COOKIE cookie; NOT session-backed per `CSRF_USE_SESSIONS=False` at `settings.py:999`) |
| `VIPReadOnlyMiddleware` (position 13) | `core/vip_middleware.py:50-91` | Runtime VIP HTTP gate; reads `primary_role`; **does NOT check account_expires_at** (F-C-VIP-1) |
| `RateLimitingMiddleware` DISABLED | `core/settings.py:230-232` | Cat A F-RATE-1 preserved; login rate-limits documentary only |
| `ws_auth_middleware.TokenAuthMiddleware` | `core/ws_auth_middleware.py:24-52` | ASGI WS auth (Cat A F-WS-1 silent AnonymousUser preserved) |
| `Token.objects.get_or_create` service | Called from `auth_views.py:53`, `auth_views_enhanced.py:120, 193, 257`, `views_vip_invite.py:131`, `setup_pa_service_account.py:48` | 5 call sites for token issuance |
| `Token.objects.filter(user=user).delete() + create()` service | Called from `auth_views_enhanced.py:396-399, 460-461` | 2 rotation call sites (password reset flow only; NOT password change) |
| `request.user.auth_token.delete()` service | Called from `auth_views.py:90`, `auth_views_enhanced.py:547` | 2 logout revocation call sites |
| `django.contrib.auth.logout(request)` service | Called ONLY from `urls.py:1626` lambda | Session flush occurs ONLY on `/accounts/logout/` Django path — NOT on REST `/api/v1/auth/logout/` or `/logout-enhanced/` |
| `login()` (Django auth) | ZERO REST auth-view call sites (grep verified) | **F-C-FIX-1** session fixation SPECULATIVE-CONCERN — no `login()` call = no session_key rotation on login; token-centric architecture bounds blast to CSRF-token identity (see §14.3) |
| `session.cycle_key()` | ZERO call sites (grep verified) | Same — no session fixation defense |
| No `refresh_token` view for DRF Token | Grep verified ABSENT | F-C-REFRESH-1 HIGH |
| No Clear-Site-Data emission | Grep verified ABSENT | F-C-CSD-1 HIGH |
| No session-lifecycle event emit | Grep verified ABSENT | CF-C3 → Group 1700 Observability (extending Cat A CF-2) |
| No `clearsessions` beat task | Grep verified ABSENT | Django `clearsessions` command not scheduled; sessions in Redis rely on TTL |
| No VIP account_expires_at revocation task | Grep verified ABSENT | F-C-VIP-1 no cleanup |
| No mobile-token revocation-on-logout hook | Grep verified ABSENT | CF-C4 → Group 2300 Mobile |

**Denominator:** 21 session-lifecycle-adjacent service loci enumerated; 8 ABSENT
(negative findings); 6 CONFIRMED functional (per Cat A + HEAD verified); 7 with
lifecycle-observability gaps per §14.

---

## 6. Major APIs and Interfaces

Section §3 enumerated URL entry points. Section §6 adds behavior + permission +
rate-limit + session-effect + logout-effect per endpoint. Cat B §6 already tabulated
permission-floor uniformity for the general endpoint surface; Cat C narrows to
session-lifecycle endpoints only.

### 6.1 Session-lifecycle endpoint permission-decorator matrix (HEAD-verified)

| Endpoint | View File:Line | Method | `@authentication_classes` | `@permission_classes` | Rate-Limit (declared) | Rate-Limit (runtime) | Session Side-Effect | Token Side-Effect | Logout Side-Effect | Clear-Site-Data |
|---|---|---|---|---|---|---|---|---|---|---|
| `/api/v1/auth/login/` | `auth_views.py:24-81` | POST | DRF default | (none) | 5/300s | **DISABLED** (F-RATE-1) | No session flush; no session-key rotation (F-C-FIX-1) | `Token.get_or_create` at `:53` | N/A | N/A |
| `/api/auth/login/` (compat) | Same view | POST | Same | Same | 5/300s | DISABLED + compat-alias bypass (F-DEBUG-3) | Same | Same | N/A | N/A |
| `/api/v1/auth/logout/` | `auth_views.py:84-94` | POST | DRF default | **(none)** — F-C-LOGOUT-1 | None | N/A | No session flush; no cycle_key | Token delete in try/except | Silent 200 on unauth (AttributeError swallowed) | **NONE (F-C-CSD-1)** |
| `/api/v1/auth/login-enhanced/` | `auth_views_enhanced.py:222-294` | POST | DRF default | `[AllowAny]` | 5/300s | DISABLED | Same as basic login | `Token.get_or_create` at `:257`; optional remember_token at `:282` | N/A | N/A |
| `/api/v1/auth/register/` | `auth_views_enhanced.py:48-140` | POST | DRF default | `[AllowAny]` | 3/3600s | DISABLED | No session | `Token.get_or_create` at `:120` on verify | N/A | N/A |
| `/api/v1/auth/verify-email/` | `auth_views_enhanced.py:170-220` | POST | DRF default | `[AllowAny]` | None | N/A | No session | `Token.get_or_create` at `:193` | N/A | N/A |
| `/api/v1/auth/forgot-password/` | `auth_views_enhanced.py:297-355` | POST | DRF default | `[AllowAny]` | 3/3600s | DISABLED | No session | Reset email + `PasswordResetToken` (Django stdlib) | N/A | N/A |
| `/api/v1/auth/reset-password/` | `auth_views_enhanced.py:357-420` | POST | DRF default | `[AllowAny]` | **None (F-DEBUG-2)** | N/A | No session | **Token rotation**: `filter(user).delete()` at `:396` + `create(user)` at `:399` (and 460-461) | N/A | N/A |
| `/api/v1/auth/change-password/` | `auth_views_enhanced.py:424-475` | POST | DRF default | `[IsAuthenticated]` | None | N/A | No session | **NO token rotation** (F-TOKEN-1 baseline — only reset rotates) | N/A | N/A |
| `/api/v1/auth/logout-enhanced/` | `auth_views_enhanced.py:539-556` | POST | DRF default | **`[IsAuthenticated]`** (line 540 — verifier-loop-corrected) | None | N/A | No session flush; no cycle_key | Token delete in try/except (F-C-LOGOUT-2) | 200 on IsAuthenticated pass; 403 on unauth (DRF standard) | **NONE (F-C-CSD-1)** |
| `/api/v1/auth/validate-token/` | `auth_views_enhanced.py:559-599` | POST | **`[]` explicit-empty (F-B-HIGH-4)** | `[AllowAny]` | **None (F-DEBUG-2)** | N/A | No session | Token key lookup (oracle) | N/A | N/A |
| `/api/v1/auth/user/` | `auth_views.py:97+` | GET | DRF default | (none) | None | N/A | Read-only | Read-only | N/A | N/A |
| `/api/v1/auth/debug/` | `auth_views_enhanced.py:658` | GET (phantom) | DRF default | `[AllowAny]` | None | N/A | No session | Read-only | N/A | N/A |
| `/api/v1/auth/resend-verification/` | `auth_views_enhanced.py:604` | POST | DRF default | `[AllowAny]` | None (F-DEBUG-2 adjacent) | N/A | No session | Trigger verification-email; no token side-effect | N/A | N/A |
| `/api/v1/vip-invites/exchange/` | `views_vip_invite.py:85-165` | POST | DRF default | `[AllowAny]` | None | N/A | No session | `Token.get_or_create(vip_user)` at `:131`; VIP account creation | N/A | N/A |
| `/api/v1/vip-invites/revoke/` | `views_vip_invite.py:168-200` | POST | DRF default | `[IsAdminUser]` | None | N/A | No session | Implicit invalidation via `is_active=False` (no explicit Token.delete) | N/A | N/A |
| `/accounts/logout/` (Django) | `urls.py:1626` lambda | GET/POST | Django default | Django default | None | N/A | **YES — Django `logout()` flushes session** | No token delete (Django path unaware of DRF Token) | Redirects to `/login` | **NONE** |

**Denominator:** 17 session-lifecycle-relevant endpoints enumerated; 6 create Token
(login × 2 basic-and-enhanced + register + verify-email + reset-password rotate +
VIP exchange + PA service-account setup); 2 delete Token (logout basic + enhanced);
1 Django-native session-flush (`/accounts/logout/` — not consumed by REST client);
2 with `IsAuthenticated` guard (change-password + logout-enhanced); 3 with silent
200 on failure (basic logout unauth + both logout endpoints on token-delete
exception); 4 not rate-limited (Cat A F-DEBUG-2 preserved); 0 emit Clear-Site-Data
(F-C-CSD-1).

### 6.2 Refresh-endpoint verified ABSENCE

Grep at HEAD `8bc1b0c0`:
- `path.*refresh` in `core/urls.py` → 3 matches:
  - `urls.py:1925` — `api/projects/<uuid:project_id>/intelligence/spiders/refresh/` (spider refresh, not auth)
  - `urls.py:2055` — `api/distribution/oauth/<str:platform>/refresh/` (third-party OAuth token refresh — `refresh_token` view in `core/views_platform_integrations.py:388-435` handles external platform token rotation, NOT DRF `authtoken.Token`)
  - `urls.py:3071` — `api/v1/agents/discovery/refresh/` (agent discovery refresh, not auth)
- `TokenRefresh`, `RefreshView`, `token/refresh/` in `core/**` → 0 matches
- `frontend/src/lib/api.ts` axios interceptor: no 401-retry-with-refresh pattern; interceptor at `api.ts:48-56` calls `useAuthStore.getState().logout()` + redirect on 401 for auth-endpoints (S2203 F3 SYSTEMIC preserved)
- `frontend/src/stores/authStore.ts`: no `refreshToken` field

**Verdict:** F-C-REFRESH-1 HIGH — no session-token refresh contract exists. Given
F-TOKEN-1 (Token no expiry), the implicit contract is "token permanent absent
password change / reset / logout event." Refresh discipline is **undeclared and
unobservable**. Blocker to acceptance criterion #4.

---

## 7. Runtime Flows

Cat A §7 delivered per-caller-class runtime posture. Cat C narrows to
lifecycle-flow-per-event (login → mid-session → logout → post-logout re-auth) with
session-observation focus.

### 7.1 Login flow (session issuance)

1. Client POSTs `/api/v1/auth/login/` with `{username, password}` → axios sets
   `Content-Type: application/json` (from `api.ts`).
2. Django middleware chain runs positions 1-9:
   - `SessionMiddleware` (5) creates or loads session from Redis (F-SESS-1 fallback risk)
   - `CsrfViewMiddleware` (8) — bypassed via `DisableCSRFForAuthEndpoints` (position 7)
   - `AuthenticationMiddleware` (9) — no effect on unauth request
3. `UnifiedTokenAuthenticationMiddleware` (10) — path `/api/v1/auth/login/` is in
   `PUBLIC_PATHS` → bypass all auth (Cat A §7).
4. View at `core/auth_views.py:24-81`:
   - `authenticate(username, password)` at `:47`
   - On success: `Token.objects.get_or_create(user=user)` at `:53` — **idempotent**;
     same token returned for user across logins
   - Response: `{token, user{...}}` + HTTP 200
5. **Critical omission (F-C-FIX-1 SPECULATIVE-CONCERN):**
   - No `django.contrib.auth.login(request, user)` call → **Django session NOT
     rotated on login** → session_key stable across auth boundary → session
     fixation attack surface for anything session-backed
   - Given `CSRF_USE_SESSIONS=False` at `settings.py:999` (CSRF token in cookie),
     Django session is used ONLY by third-party Django admin + fringe view paths
     — token-centric architecture bounds session-fixation blast to CSRF-token
     identity (attacker who pre-set sessionid gets victim's CSRF token, but Cat A
     shows CSRF is bypassed for auth endpoints anyway via `DisableCSRFForAuthEndpoints`)
   - **Verdict: SPECULATIVE-CONCERN, not CRITICAL** — blast is bounded; but the
     absence of `session.cycle_key()` is undocumented and would be a straightforward
     defense-in-depth addition
6. Frontend `authStore.login(token, user)` at `authStore.ts:22-33` mutates state
   → Zustand persist writes to `auth-storage` localStorage record
7. Frontend sets Authorization header for all subsequent axios calls via `api.ts`
   request interceptor at line 29 (reads from `useAuthStore.getState().token`)

### 7.2 Mid-session flow (token consumption)

1. Client sends `Authorization: Token <key>` with every request (interceptor
   injects from authStore)
2. `UnifiedTokenAuthenticationMiddleware.process_request()` at `auth_middleware.py:563-681`:
   - Extract token via `extract_token()` at `:683-702`
   - Validate token via `validate_token()` at `:704-736` (Session 1171 typed-fork:
     `Token.DoesNotExist → None`; else raise `TokenValidationInfrastructureError`)
   - Set `request.user` = token owner
3. `VIPReadOnlyMiddleware` (position 13) checks VIP write-block; **does NOT check
   account_expires_at** (F-C-VIP-1 HIGH)
4. `SESSION_SAVE_EVERY_REQUEST=True` at `settings.py:1103` → session touched → TTL
   sliding-window extended by `SESSION_COOKIE_AGE=1209600` (14d)
5. If Redis unavailable at request time (rare; typically fails at startup):
   session read/write falls through cache to LocMemCache — silent-degrade per
   F-SESS-1

### 7.3 Logout flow (revocation)

**Frontend logout onClick (Sidebar.tsx:356 baseline):**
1. Sidebar dispatches `api.post('/v1/auth/logout/')` — server call
2. `paStore.syncUser(null)` at `paStore.ts:182-194` — wipes messages, activeConversationId,
   conversations, currentInput, conversationsLoading. **Does NOT wipe activeTool,
   recentTool, seenSeqs, agentCompletionQueue, seenCompletions, recentAgentCompletion**
   (S2204 F7 incomplete field-list)
3. `authStore.logout()` at `authStore.ts:34-39` — sets `{token:null, user:null,
   isAuthenticated:false}` → Zustand persist writes null-record to `auth-storage`
   localStorage. **No `localStorage.removeItem`** (S2204 F6 functional-null-state)

**Server-side (basic logout — `auth_views.py:84-94`):**
- No `@permission_classes` → any POSTer accepted
- `request.user.auth_token.delete()` at `:90`
- Except-swallow: any Exception (AttributeError on AnonymousUser, DoesNotExist,
  DB errors) caught at `:92`, warning logged, 200 returned
- **No `django.contrib.auth.logout(request)`** → Django session NOT flushed →
  session Redis record persists until `SESSION_COOKIE_AGE` TTL (14d) or explicit
  browser close
- **No `Clear-Site-Data` header** → browser cookies + cache + storage NOT signaled
  to clear
- **No structured event emission** → observability blind (CF-C3)
- **No mobile-token revocation** (CF-C4) → `MobilePushToken.revoked_at` NOT set
- **No WS connection eviction** → open WS remain connected until idle-timeout;
  10-of-11 consumers already accept anon per Cat A §6 (only PAConversationConsumer
  hard-rejects — but that check happened at connect time, not evict on logout)
- **No PA conversation retirement** → `session_tool.retire` not called; active
  PA conversation pins remain `session_active=True` (CF-C2)
- **Response:** `{'detail': 'Successfully logged out'}` (or `'Logout successful'`
  on except) — HTTP 200 always

**Server-side (enhanced logout — `auth_views_enhanced.py:539-556`):**
- `@permission_classes([IsAuthenticated])` at line 540 → unauth POSTer gets 403
- Otherwise identical to basic: token-delete + except-swallow + 200

**Client-side after server call:**
1. Axios response received (200 or 403)
2. Redirect to `/login` (typical — via Sidebar or `api.ts:48-56` on 401)
3. Next page mount:
   - Zustand persist rehydrates `auth-storage` → `{token:null, user:null,
     isAuthenticated:false}` → `ProtectedRoute` redirects to `/login` (correct)
   - Zustand persist rehydrates `navigation-store` → recentEntities INTACT
     (S2204 F8 cross-user leakage: next user sees prior user's browsing history)
   - Zustand persist rehydrates `pa-dock-state` → paStore fields not-wiped-by-syncUser
     persist (activeTool, agentCompletionQueue, etc.); persist middleware writes
     current state on mutation
   - 12 direct localStorage keys persist unchanged (no cleanup — F-C-STORE-1)

**Multi-tab logout flow (F-C-TAB-1 gap):**
- Tab A logs out per §7.3 above; localStorage `auth-storage` updated to null-record
- Tab B has authStore in-memory state (isAuthenticated=true) — DOES NOT observe
  localStorage change (0 storage-event listeners; 0 BroadcastChannel per S2204 §15.7
  preserved at HEAD)
- Tab B continues making authenticated API calls until next 401
- On 401: `api.ts:48-56` triggers logout locally (if endpoint matches auth-scope
  whitelist); non-auth 401 silently swallowed (S2203 F3 SYSTEMIC → Cat D scope)

### 7.4 Post-logout re-auth flow

1. Client POSTs `/api/v1/auth/login/` with credentials again
2. Same as §7.1 — `Token.get_or_create(user)` returns **NEW token** (old token
   deleted at logout, so `get_or_create` creates fresh); frontend stores new
3. Persistent localStorage keys (12 direct + 2 non-authstore Zustand) NOT cleared
   between users on shared browser — **F-C-STORE-1 cross-user leakage**

### 7.5 VIP invite exchange flow (VIP account issuance)

1. Client POSTs `/api/v1/vip-invites/exchange/` with `{token}` (from magic link URL)
2. View at `views_vip_invite.py:85-165`:
   - Query VIPInvite by token → `if not invite or invite.token_expires_at <
     timezone.now(): reject 400` at `:151-156` — **72h ENFORCED**
   - Check `invite.redeemed_at` and `invite.revoked_at` at `:150` — reject if
     redeemed or revoked
   - Create VIP UnifiedUser + `Token.get_or_create(vip_user)` at `:131`
   - Create `AssistantProfile` with `role='vip_viewer'`
   - Set `EnhancedUserProfile.primary_role = 'vip_demo_viewer'` (VIP HTTP gate)
   - Mark `invite.redeemed_at = now()`, `invite.redeemed_by = vip_user` at `:134-136`
3. **`account_expires_at` (14d) NEVER checked** — F-C-VIP-1 HIGH
4. VIP user's token persists indefinitely absent explicit revocation

### 7.6 Cookie-effect summary per endpoint (HEAD-verified)

- Login endpoints: no `Set-Cookie` for sessionid (server does not call Django
  `login()`, so no session write occurs unless middleware side-effects); if
  `SESSION_SAVE_EVERY_REQUEST=True` triggers session touch, cookie IS set with
  configured HTTPOnly/SameSite/Secure per §3 config
- Logout endpoints: NO cookie clearing (no `Set-Cookie: sessionid=; max-age=0`
  emission; no Clear-Site-Data) — sessionid cookie persists until `SESSION_COOKIE_AGE`
  browser TTL
- All endpoints: `CSRF_COOKIE_NAME='csrftoken'` set on any response that renders
  CSRF token (typical Django behavior — persists per `CSRF_COOKIE_AGE` default 1 year)

---

## 8. Data Ownership and Lifecycle

Cat A §8 delivered token / VIP / fleet / service-token / audit lifecycle. Cat C
extends with session-cookie + storageKeys lifecycle table.

**Session cookie lifecycle:**
- Created: on first request touching `SessionMiddleware` (if `SESSION_SAVE_EVERY_REQUEST`
  or explicit session mutation)
- Rotated: NEVER (F-C-FIX-1 SPECULATIVE-CONCERN — no `session.cycle_key()` on login)
- Sliding TTL: extended on every request per `SESSION_SAVE_EVERY_REQUEST=True`
- Absolute TTL: 14d per `SESSION_COOKIE_AGE=1209600`
- Cleared: only on `/accounts/logout/` Django path (calls `logout()`); REST logout
  endpoints do NOT flush
- Cross-tab: N/A (browser-level cookie; single record per domain)

**DRF Token lifecycle (Cat A F-TOKEN-1 preserved):**
- Created: 5 sites (login basic + enhanced + register verify + reset-password rotate
  + VIP exchange + service-account setup)
- Rotated: only at password RESET (2 lines: 396-399, 460-461) — NOT at password
  change (F-TOKEN-1)
- Retired: 2 sites (basic logout + enhanced logout)
- Sliding TTL: N/A (no expiry field)
- Absolute TTL: N/A (no expiry field — F-C-REFRESH-1)
- Cross-tab: N/A (server-side row; frontend reads from authStore)

**VIP account lifecycle (F-C-VIP-1 HIGH):**
- Created: VIP exchange endpoint (72h token_expires_at ENFORCED)
- Renewed: N/A (no renew endpoint)
- Retired: manual admin revoke at `/api/v1/vip-invites/revoke/` → sets
  `redeemed_by.is_active=False` (implicit token invalidation via `is_active` check
  at auth middleware — Cat A §7)
- Sliding TTL: N/A
- Absolute TTL: 14d per `account_expires_at` — **NOT ENFORCED** at HEAD (grep zero-match)
- Cross-tab: N/A

**15-surface storageKeys lifecycle (S2204 F1 baseline preserved at HEAD):**

Full per-surface table in §14.2. Aggregate lifecycle:
- Created: on first mutation (Zustand persist auto-write; direct `localStorage.setItem`)
- Updated: on any state mutation (Zustand); explicit setItem (direct)
- Retired: 1 surface CLEAN (auth-storage functional-null-state on logout); 3
  PARTIAL; 11 NO-CLEANUP
- Sliding TTL: N/A (persists until localStorage quota exhausted or user clears
  browser storage manually)
- Absolute TTL: N/A
- Cross-tab: 0 storage-event listeners + 0 BroadcastChannel → tab-B does not
  observe tab-A changes (F-C-TAB-1)

**MobilePushToken lifecycle (CF-C4 gap):**
- Created: mobile app registration via Expo push registration flow
- Rotated: on new device token issuance
- Retired: soft-delete via `revoked_at` — **NOT called from logout endpoints** (grep zero-match)
- Sliding TTL: N/A
- Absolute TTL: N/A

**Fleet key lifecycle:** Cat A §8 preserved — independent of user-session lifecycle.

---

## 9. Integrations With Other Domains

Per playbook §11.2 §9 — integration map + cross-arc coordination flags.

### 9.1 Integration classification

| Domain | Relationship | Classification | Evidence |
|---|---|---|---|
| Frontend (Group 2200) | Owns 15-surface persistence; consumes token via authStore | **STRONG (with 14-of-15 cleanup gap)** | 15-surface table §14.2 |
| PA / Rigby (Group 2600) | `AssistantProfile.workspace` FK + paStore workspace-context + session_tool conversation pins | **STRONG-with-lifecycle-gap** (CF-C2) | paStore.syncUser incomplete (S2204 F7); workspaceStore in-memory (F5); session_tool retire not called on user logout |
| API Layer (Group 2500) | Response envelope + refresh endpoint semantics + Clear-Site-Data emission | **PARTIAL (three-option decision-space owner)** (CF-C1) | F-C-REFRESH-1 + F-C-CSD-1 both point to Group 2500 API |
| Auth mechanisms (Cat A) | Cat C consumes token model + middleware chain + VIP invite lifecycle | **STRONG (boundary-preserved)** | Cat A §4 §7 §14 baseline |
| Authorization (Cat B) | Cat C consumes 21-loci matrix + workspace-membership implicit-gate + 4-role landscape | **STRONG (boundary-preserved)** | Cat B §14 §17 baseline |
| Fleet HMAC | HMAC-signed requests carry identity independent of user-session | **STRONG (orthogonal-by-contract)** | Cat A §14 F-HIGH-4 preserved |
| Observability (Group 1700) | login/logout event emit gap | **WEAK / MISSING** (CF-C3 extends Cat A CF-2) | grep zero-match for login/logout event emission |
| Mobile (Group 2300) | MobilePushToken.revoked_at not integrated to logout; validate-token endpoint hydration contract (Cat A CF-4) | **WEAK** (CF-C4 extends Cat A CF-4) | logout endpoints do NOT call `MobilePushToken.filter(user=user).update(revoked_at=now)` |
| Discord bot | DiscordLinkCode short-lived; not session-scoped | **ORTHOGONAL** | Independent 10-min TTL enforced on redemption |
| Stripe | Webhook signature (not user auth) | **ORTHOGONAL** | Cat A §9.1 preserved |
| Governance / Authority (Group 1900) | Boundary preserved — Cat A F-BND-0 unchanged | **BOUNDARY-PRESERVED** (CF-C7 attestation candidate) | Grep zero-match for KillSwitch consumer on logout path |
| Cat D (S2404) | Cat C evidence-plan feeds Cat D silent-401 + typed-error-envelope | **STRONG (feeds forward)** (CF-C6) | Cat C §14.3 session-lifecycle-observability gaps → Cat D typed-error alignment |

### 9.2 Cross-arc coordination flags (CF-C1 → CF-C7)

**CF-C1 → Group 2500 API (refresh endpoint + logout response envelope + Clear-Site-Data)**.
Cat C's three-option decision-space (§19.1) requires Group 2500 API to:
- (if α silent-refresh chosen) design refresh endpoint contract + rotation-on-use
  policy + typed error envelope for refresh failure
- (if β explicit-re-login chosen) formalize logout response envelope including
  Clear-Site-Data emission spec + optional expiry-timestamp field on Token model
- (if γ hybrid chosen) both of the above + idle-timeout tracking
Blast radius: whole API surface — refresh endpoint is a new /api/v1/auth/ addition;
Clear-Site-Data emission adds one line to logout endpoints.

**CF-C2 → Group 2600 PA (workspace-context lifecycle + session_tool.retire on user logout)**.
Cat B CF-B2 preserved (workspace-membership implicit-gate) + Cat C addition:
- Should user-logout retire all active PA conversation pins for that user?
  (`session_tool.retire` iterated across `ChatConversation.filter(user_id=user_id,
  session_active=True)`)
- Should workspaceStore persist across F5 (S2204 F5 borderline-HIGH)?
- Should paStore.syncUser(null) wipe the 6 additional fields (activeTool,
  recentTool, seenSeqs, agentCompletionQueue, seenCompletions, recentAgentCompletion)
  per S2204 F7 incomplete-field-list?
Owner: Group 2600 PA arc.

**CF-C3 → Group 1700 Observability (Lifecycle transition observability —
auth/session)** (Rigby SIGN cycle 1 Q11(a) + Q12 fold — kept as single tracking
unit, NOT split into three flags; explicitly linked to Cat A CF-2 + Cat B CF-B5
for xx99 roll-up). Sub-scope:
- Login success/failure events (currently zero emission)
- Logout success/failure events
- Session creation / expiration events
- Token rotation events (password change / reset)
- VIP invite exchange / revocation events
- MobilePushToken registration / revocation events
- Silent-degrade events (F-SESS-1 Redis-fallback, F-WS-1 WS anon)
- 503-fork asymmetry propagation (Cat B CF-B5 preserved as related concern)
Owner: Group 1700 Observability arc. Xx99 §5.4 candidate roll-up: single
Observability umbrella flag (CF-2 + CF-B5 + CF-C3) if consolidation warranted.

**CF-C4 → Group 2300 Mobile (mobile session lifecycle)**. Extends Cat A CF-4:
- `/api/v1/auth/validate-token/` mobile hydration endpoint contract (Cat A CF-4)
- `MobilePushToken.revoked_at` set on user logout — does the mobile app poll
  this? Or should logout push a signaling notification to registered devices?
- Mobile-app session TTL: does the mobile app store token indefinitely or refresh
  via re-auth? (relates to F-C-REFRESH-1 decision-space)
Owner: Group 2300 Mobile arc (deferred per Cat B and Cat A precedent).

**CF-C5 → Group 2200 Frontend (session-lifecycle test coverage + R1/R5/R6 execution)**.
S2204 §19.1 R1 R5 R6 remediation is Group 2200 T-slot post-arc. Cat C:
- Confirms 15-surface baseline preserved at HEAD (no delta since S2204 close)
- Extends acceptance-criterion-#3 blocker list: adds Zustand persist logout-hooks
  for navigation-store and pa-dock-state (currently zero hooks)
- Extends acceptance-criterion-#4 blocker list: adds smoke-test coverage per
  lifecycle endpoint (login, logout basic, logout enhanced, reset-password rotate,
  VIP exchange) — extending Cat A F-CRIT-2 pattern
Owner: Group 2200 Frontend post-arc T-slot.

**CF-C6 → Cat D (S2404) Frontend Integration + Silent-401 SYSTEMIC**. Cat C's
three-option decision (§19.1) directly shapes Cat D:
- (α silent-refresh) Cat D audits refresh-interceptor design candidates (add axios
  interceptor for 401 → refresh call → retry pattern)
- (β explicit-re-login) Cat D audits current silent-401 behavior + surfaces to
  user-visible modal on 401 (SYSTEMIC → EXPLICIT-FAILURE)
- (γ hybrid) Cat D audits both refresh + fallback modal integration
Owner: Cat D S2404 (this arc).

**CF-C7 → Group 1900 Governance/Authority (KillSwitch consumer attestation on logout)**.
- Does user-logout trigger any governance-consumer state invalidation? Grep at
  HEAD for `KillSwitch` in logout paths: zero matches — boundary preserved.
- Should logout emit an authority-plane audit event (extending CF-C3)?
- Post-arc anchor-update candidate: attest at xx99 anchor row "no authority-plane
  consumer touches logout flow" (extending Cat A CF-5 pattern).
Owner: Group 1900 Governance arc (post-arc coordination).

---

## 10. Event Flows

Cat A §10 delivered auth event emission at HEAD — all `logger.*` calls, no
structured event stream. Cat C extends with session-lifecycle-event enumeration.

**Session-lifecycle events NOT emitted (extending Cat A CF-2 gap):**
- Login success (basic + enhanced): no `EventStream.*` call; no `logger.info`
  structured event — only Django's default `django.request` INFO logs
- Login failure: `logger.error(f"Authentication failed for username: {username}")` at
  `core/auth_views.py:77` — f-string log, not structured event
- Logout success: no emit (basic + enhanced)
- Logout failure (token-delete exception): `logger.warning(...)` at
  `auth_views.py:93` and `auth_views_enhanced.py:549-551` — warning log only
- Session creation: no emit
- Session expiration: no emit
- Token rotation (password reset): no emit
- VIP invite creation: no emit
- VIP invite exchange (VIP user + token issued): no emit
- VIP invite revocation: no emit
- Password change: no emit
- Password reset (token rotation): no emit
- MobilePushToken registration: no emit
- MobilePushToken revocation: no emit (never called from logout)

**Silent-degrade events NOT emitted:**
- Redis fallback → LocMemCache (F-SESS-1): `logger.warning` at `settings.py:500`
  (once, at process start)
- WS token validation infra failure (F-WS-1): silent AnonymousUser fallback
- Multi-tab logout in Tab A → Tab B stale: no emit

**Cat C recommendation for xx99 CF-C3:** structured event emission on all
session-lifecycle transitions (login, logout, token rotation, VIP exchange,
revocation) + silent-degrade events (Redis fallback, WS auth fallback) as minimum
observability contract. Extending Cat A CF-2 + Cat B CF-B5 (Observability
503-fork asymmetry) with lifecycle-plane event surface.

---

## 11. Existing Documentation

Per playbook §11.2 §11 — gap analysis inheriting Agent 5 verified enumeration.

**Existing session-lifecycle-adjacent docs at HEAD `8bc1b0c0`:**

| Doc | Coverage | Cat C Consumption |
|---|---|---|
| `docs/research/domains/auth/2400_auth_domain_scoping.md` | Cat C parent scope + §3.5 auth-adjacent probes | Cat C consumes §3.C acceptance criteria + §3.5 probes disposition |
| `docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md` | Cat A §4 §7 §14 (F-TOKEN-1, F-VIP-1, F-SESS-1, F-WS-1) | Cat C consumes as baseline; extends to lifecycle-CONTRACT gaps |
| `docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` | Cat B §14 F-B-HIGH-3, §17 F-B-DUP-1, §13.5 axis | Cat C consumes 4-role landscape + workspace-membership implicit-gate + correctness-vs-governance-axis |
| `docs/research/domains/frontend/2204_frontend_session_state_persistence_discipline_audit.md` | 15-surface storageKeys + §14 F6/F7/F8 + §19.1 R1 two-sided framing | **PRIMARY inheritance** — Cat C is R1's owning arc; consumes 15-surface baseline + FE symptom side |
| `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md` §14.3 | Cockpit two-stage MINOR-DRIFT | Cat C re-verifies STILL-LIVE at HEAD (F-C-COCKPIT-1) |
| `docs/research/platform_architecture_inventory.md` §3.27 | S1273 32-domain map row 27 (auth PARTIAL + LIGHT) | Baseline reference |
| `docs/handoffs/SESSION_2204_*` | S2204 close context | Baseline reference |

**Confirmed doc gaps (VERIFIED absent at HEAD `8bc1b0c0`):**

- **Gap 1 — No `docs/topics/auth.md`** (Cat A F-DOC-1 preserved). Session-lifecycle
  subsection would land here if topic doc created.
- **Gap 2 — No `docs/topics/session_lifecycle.md`** (Cat C new). Optional standalone
  doc if session-lifecycle contract warrants dedicated narrative.
- **Gap 3 — No `PLATFORM_INVENTORY §Auth` autoblock** (Cat A F-INV-1 preserved).
  Session-lifecycle counts would land here (issuance / rotation / revocation
  call-site counts + cookie discipline table).
- **Gap 4 — No `PLATFORM_WHAT_IT_IS §Auth` subsection** (Cat A F-INV-2 preserved).
  Session-lifecycle contract narrative would land here.
- **Gap 5 — No session-lifecycle contract doc** (Cat C primary). No declared
  session-model spec at HEAD; Cat C is first authoritative source.
- **Gap 6 — No cookie-defaults per-cookie table** (Cat C new). Cookie config
  scattered across settings.py lines 980-1110; no unified per-cookie discipline
  table.
- **Gap 7 — No refresh-token semantics doc** (Cat C new). F-C-REFRESH-1 gap.
- **Gap 8 — No Clear-Site-Data emission decision doc** (Cat C new). F-C-CSD-1 gap.
- **Gap 9 — No 15-surface × logout-cleanup declared contract** (Cat C primary).
  S2204 F1 provides inventory; Cat C's §14.2 is first cleanup-CONTRACT table.
- **Gap 10 — No cross-tab logout propagation contract** (Cat C new). F-C-TAB-1 gap.
- **Gap 11 — No session-lifecycle test coverage inventory** (Cat C new, extending
  Cat A F-CRIT-2 pattern). Blocker to acceptance criterion #3 + #4 verification.

**Handoff-provenance gaps (Cat A F-PROV-1 pattern; Cat C spot-check):**
- Session 1039 (multi-tenant Phase 1 introducing `customer_role`) — handoff exists;
  no session-lifecycle content (expected — customer_role never wired to auth)
- No new provenance gaps discovered at Cat C.

---

## 12. Research Coverage

**Classification per playbook §12: MODERATE preserved from Cat A; upgrade to
MODERATE+ (not yet DEEP) justified at S2403 close.**

**MODERATE+ definition (Rigby SIGN cycle 1 Q13 fold):** "MODERATE+ = multiple-category
audits closing major entry points + runtime flows within a single domain plane;
DEEP requires cross-category completion (Cat D + xx99 canonical summary)."

Argument: Cat A + Cat B + Cat C together deliver three focused 20-section audits.
Cat A cleared MODERATE at close on mechanism-plane. Cat B extended to authorization
plane. Cat C extends to session-lifecycle plane. Three focused docs approaching
DEEP; ceiling DEEP achievable only after Cat D (S2404) + xx99 (S2499) canonical
summary.

**Post-arc (S2499 xx99) ceiling: DEEP** — after Cat A + B + C + D each ship 20-section
audits, four focused docs + canonical summary = DEEP threshold satisfied.

**CANONICAL blocked by** (Cat A blockers preserved + Cat C additions):
1. No threat-model doc (Cat A F-DOC-2 HIGH preserved)
2. No CI smoke tests per session-lifecycle endpoint (Cat C-added blocker: 0-of-17
   session-lifecycle endpoints have declared smoke-test coverage)
3. No Chris-ratified session-model contract (Cat C's own three-option decision —
   ADR authoring is post-arc regardless of α/β/γ choice)
4. No cookie-defaults per-cookie declaration (F-C-COOKIE-1)
5. No 15-surface × logout-cleanup declared contract (F-C-STORE-1)
6. No refresh-token discipline doc (F-C-REFRESH-1)
7. No Clear-Site-Data emission decision (F-C-CSD-1)
8. No cross-tab logout propagation contract (F-C-TAB-1)
9. No role-transition session-scope semantics (F-C-ROLE-SCOPE)
10. Role-field reconciliation blocker preserved (Cat A Q14 fold + Cat B F-B-DUP-1 4-role landscape)
11. PUBLIC_PATHS ownership/DRI + registry governance preserved (Cat A Q14 fold; not Cat C-scope)

---

## 13. Architecture Maturity

Per playbook §12: EXPERIMENTAL / PARTIAL / WORKING / STABLE / CANONICAL.

**PARTIAL preserved at Cat C — for different reasons than Cat A/B baselines.**

**Cat B §13.5 correctness-vs-governance-axis framing applied to session-lifecycle
plane:**

| Primitive | Correctness | Governance | Overall |
|---|---|---|---|
| HTTP session engine (`backends.cache`) | WORKING | PARTIAL (Redis-fallback silent-degrade per F-SESS-1) | **PARTIAL** |
| DRF `authtoken.Token` | WORKING | EXPERIMENTAL (no expiry declared; F-TOKEN-1) | **EXPERIMENTAL** |
| VIP account lifecycle | PARTIAL (72h enforced; 14d NOT enforced — F-C-VIP-1) | EXPERIMENTAL (no contract doc) | **PARTIAL-EXPERIMENTAL** |
| Logout endpoint (basic + enhanced) | WORKING-with-debt (silent-200 on unauth basic — F-C-LOGOUT-1) | EXPERIMENTAL (no Clear-Site-Data; no event; no cross-tab; no mobile revoke) | **PARTIAL-EXPERIMENTAL** |
| authStore.logout FE | WORKING (functional-null-state) | WORKING (Zustand persist + partialize declared) | **WORKING** |
| navigationStore + paStore persist | WORKING | PARTIAL (paStore v3+migrate; navigation-store no version+migrate; both lack logout hooks — S2204 F7/F8) | **PARTIAL** |
| 12 direct localStorage keys | WORKING (state persists) | EXPERIMENTAL (no cleanup contract) | **EXPERIMENTAL** |
| Cookie discipline (SameSite/Secure/HttpOnly) | WORKING (declared per-env) | PARTIAL (no per-cookie table; domain+path ABSENT — F-C-COOKIE-1) | **PARTIAL** |
| Cross-tab logout coordination | ABSENT | ABSENT | **DEAD** |
| Role-field lifecycle | WORKING (auth checks work) | EXPERIMENTAL (4-field bifurcation; no session-scope) | **EXPERIMENTAL** |
| Session fixation defense | SPECULATIVE-CONCERN (no cycle_key) | PARTIAL (bounded blast per token-centric architecture) | **PARTIAL** |
| WebSocket session auth | WORKING-with-fallback (Cat A F-WS-1) | PARTIAL | **PARTIAL** |
| Session-lifecycle test coverage | ABSENT (0-of-17 endpoints) | ABSENT | **DEAD** |

**Overall session-lifecycle-plane maturity: PARTIAL** (correctness WORKING for
session/token/cookie mechanisms; governance EXPERIMENTAL for lifecycle CONTRACT).
Extends Cat A PARTIAL (auth-mechanism-plane) + Cat B PARTIAL (authorization-plane) —
Group 2400 domain-plane at PARTIAL across all three children.

**Cat A/B/C consolidation preview for xx99 §5.4:** Group 2400 auth-domain overall
maturity converges on **WORKING-CORRECTNESS + EXPERIMENTAL-GOVERNANCE** (Cat B
§13.5 axis fully applies at domain level). Post-arc anchor-update recommendation:
`PLATFORM_INVENTORY §Auth` autoblock should carry both axes explicitly.

---

## 14. Known Drift

Consolidated drift matrix at HEAD `8bc1b0c0`. Playbook §12 finding_type strings
in bold. Denominator declared per §14.4 count ledger.

### 14.1 HIGH drifts (new at Cat C)

**F-C-VIP-1 — `VIPInvite.account_expires_at` (14d) NOT ENFORCED at runtime**
(**`technical_debt` + `unclear_owner`**). Severity: **HIGH** (Cat A F-VIP-1 preserved
+ HEAD-re-verified at S2403). Grep at HEAD across `core/`: zero matches for
`.filter(account_expires_at__`, `account_expires_at < timezone.now()`,
`account_expires_at.__lt`, `account_expires_at.gt`. `VIPReadOnlyMiddleware.__call__`
at `core/vip_middleware.py:63-91` checks `primary_role == 'vip_demo_viewer'` but
NOT expiry. Zero periodic cleanup task (grep for `VIPInvite` in `core/tasks.py`,
`core/celery.py`, `beat_schedule`: zero matches). Blast: every VIP account persists
indefinitely once minted. Cat C promotes to lifecycle-CONTRACT gap. Blocker to
acceptance criterion #4.

**F-C-REFRESH-1 — No session-token refresh endpoint / implicit no-refresh contract**
(**`missing_connection` + `technical_debt`**). Severity: **HIGH**. Grep at HEAD:
zero `path.*refresh` for auth surface (3 matches at `urls.py:1925, 2055, 3071` are
all non-auth: spider-refresh, third-party-OAuth-refresh, agent-discovery-refresh);
zero `TokenRefresh`, `RefreshView`, `token/refresh/` in `core/**` auth files; zero
`refresh_token` in `authStore.ts`; zero 401-retry-with-refresh in `api.ts:48-56`.
Combined with Cat A F-TOKEN-1 (Token no expiry), implicit contract is "token
permanent absent password change / reset / logout event." No refresh discipline;
no rotation-on-use. Blocker to acceptance criterion #4.

**F-C-CSD-1 — Zero Clear-Site-Data header emission on logout** (**`drift` +
`missing_connection`**). Severity: **HIGH**. Grep at HEAD for `Clear-Site-Data`
in `core/**` + `frontend/**`: zero production-code matches (only appears in docs +
`tools/pa_local.sh:39` comment). Neither `logout_view` (`auth_views.py:84-94`) nor
`logout_enhanced_view` (`auth_views_enhanced.py:539-556`) sets the header.
Blast-radius analysis for demo-mode third-party cookies: given
`SESSION_COOKIE_SAMESITE='Strict'` in prod at `settings.py:986` +
`CSRF_COOKIE_SAMESITE='Strict'` at `settings.py:998`, third-party cookie residue
is unlikely; blast is contained to first-party origin cookies + storage + cache.
Recommend `Clear-Site-Data: "cookies", "storage"` as minimum-viable emission.
Blocker to acceptance criterion #3.

**F-C-STORE-1 — 14 of 15 client-side persistence surfaces lack DECLARED
logout-cleanup contract** (**`technical_debt` + `drift`**). Severity: **HIGH**.
S2204 §14 F1 15-surface baseline (3 Zustand persist + 12 direct localStorage)
HEAD-re-verified UNCHANGED at `8bc1b0c0` (zero delta). Per-surface cleanup contract
in §14.2 table below. Blocker to acceptance criterion #3.

**F-C-TAB-1 — Zero cross-tab logout coordination** (**`drift` + `missing_connection`**).
Severity: **HIGH (shared-browser context), MED (single-user context)** (Rigby SIGN
cycle 1 Q15(b) fold — preserved two-context split; conveys actual risk model).
Grep at HEAD across `frontend/src`: zero `BroadcastChannel` production
matches; zero `storage.*event` / `addEventListener.*storage` production matches
(only @types/node type defs). Tab A logout → Tab B unaware until next 401
(silent-401 systemic per S2203 F3 → Cat D scope). S2204 §15.7 baseline preserved
at HEAD.

### 14.2 15-surface storageKeys × logout-cleanup CONTRACT table (HEAD-verified)

Cat C's primary deliverable per S2400 §3.C output (b). 15 surfaces from S2204 F1
baseline; Cat C classifies cleanup contract per surface.

| # | Key | Owner File:Line | Type | Cleared on Logout? | Mechanism | Cross-User Leakage Severity | Cleanup Contract Status |
|---|---|---|---|---|---|---|---|
| 1 | `auth-storage` | `authStore.ts:43-50` | Zustand persist | **YES (functional)** | `logout()` at `:34-39` sets null; Zustand persist writes null-record | HIGH if not cleared (token + user) → cleared → NONE post-clear | **DECLARED (functional-null-state per S2204 F6)** |
| 2 | `navigation-store` | `navigationStore.ts:98-105` | Zustand persist | **NO** | `clearHistory` action exists at `:96-97` but NEVER called on logout | **MED** (recentEntities breadcrumb identity leak — S2204 F8) | **ACCIDENTAL (no logout subscriber)** |
| 3 | `pa-dock-state` | `paStore.ts:395-431` (v3+migrate) | Zustand persist | **PARTIAL** | `syncUser(null)` at `:182-194` wipes messages/conversations/currentInput; NOT activeTool/recentTool/seenSeqs/agentCompletionQueue/seenCompletions/recentAgentCompletion (S2204 F7) | **MED-HIGH** (last 50 PA messages + workspace context if syncUser called; otherwise HIGH) | **PARTIAL (incomplete field-list)** |
| 4 | `assistant-voice-settings` | `CommandCenterPage.tsx:190` | direct localStorage | **NO** | No cleanup | LOW (voice profile ID) | **ACCIDENTAL** |
| 5 | `cc_dashboard_collapsed` | `CommandCenterPage.tsx:825` | direct localStorage | **NO** | No cleanup | NONE (UI collapse) | **ACCIDENTAL** |
| 6 | `cc_chat_focus_mode` | `CommandCenterPage.tsx:828` | direct localStorage | **NO** | No cleanup | NONE (UI toggle) | **ACCIDENTAL** |
| 7 | `pipeline_dismissed_${workspaceId}` | `WorkspaceDashboardPage.tsx:188` | direct localStorage (templated) | **PARTIAL** | `removeItem` on new pipeline run + on undismiss (5 call sites) but NOT on logout | LOW-MED (workspace-scoped dismissed IDs) | **PARTIAL (workspace-change cleanup, not logout)** |
| 8 | `demo-pipeline-dismissed` | `DemoPipelineCard.tsx:87` | direct localStorage | **NO** | No cleanup | NONE | **ACCIDENTAL** |
| 9 | `cockpit-focus-mode` | `useFocusMode.ts:13` | direct localStorage | **NO** | No cleanup | NONE | **ACCIDENTAL** |
| 10 | `sidebar-collapsed` | `Sidebar.tsx:126` | direct localStorage | **NO** | No cleanup | NONE | **ACCIDENTAL** |
| 11 | `sidebar-reference-open` | `Sidebar.tsx:105` | direct localStorage | **NO** | No cleanup | NONE | **ACCIDENTAL** |
| 12 | `showDebugPanels` | `PanelDebugDrawer.tsx:10` (DEV_KEY) | direct localStorage | **NO** | No cleanup (dev-only) | NONE (dev-mode flag) | **ACCIDENTAL** |
| 13 | `deliverables_view_mode` | `DeliverablesTab.tsx:304` | direct localStorage (window.localStorage) | **NO** | No cleanup | LOW (view mode) | **ACCIDENTAL** |
| 14 | `cockpit-sidebar-collapsed` | `CockpitSidebar.tsx:101` | direct localStorage | **NO** | No cleanup | NONE | **ACCIDENTAL** |
| 15 | `podcast_voice_profile_id` | `ContentStudioTab.tsx:2734` | direct localStorage | **PARTIAL** | `removeItem` on profile-change (not logout) | MED (voice preference identity signal) | **PARTIAL (change-cleanup, not logout)** |

**Aggregate:** 1 CLEAN (auth-storage functional-null-state) + 3 PARTIAL (paStore
syncUser incomplete; pipeline_dismissed workspace-change; podcast_voice_profile
change) + 11 NO-CLEANUP. **Declared cleanup rate: 1/15 (6.7%).** Accidental
cleanup rate: 3/15 (20%). No-cleanup rate: 11/15 (73%).

**Cross-user leakage aggregation:** 1 HIGH-CRITICAL (auth-storage — mitigated by
clean) + 1 MED-HIGH (pa-dock-state — partial mitigation) + 3 MED (navigation-store
+ pipeline_dismissed + podcast_voice_profile — partial or none) + 3 LOW (assistant-voice-settings
+ deliverables_view_mode + smaller) + 7 NONE (UI state). 8 of 15 surfaces have
non-NONE cross-user leakage severity.

**Denominator declaration:** 15 total persistent-state surfaces. S2204 baseline
inventory preserved at HEAD (zero delta since S2204 close `8fbf17eb` — verified
via HEAD file:reads + grep across `frontend/src` for new `localStorage.setItem` /
`persist(` calls, none discovered).

### 14.3 Session-lifecycle observability rate table (Cat C acceptance criterion #4 evidence)

Cat C's second primary deliverable per S2400 §3.C output (d).

| Lifecycle Locus | Declared? | Observable? | Evidence | Cat C Classification |
|---|---|---|---|---|
| Token issuance (login) | PARTIAL | PARTIAL | Response body includes token; no structured event emit | WORKING-correctness / EXPERIMENTAL-governance |
| Token rotation (password reset) | PARTIAL | PARTIAL | 2 call sites at `auth_views_enhanced.py:396-399, 460-461`; no event emit | WORKING / EXPERIMENTAL |
| Token expiry | **ABSENT** | **ABSENT** | No expiry field on DRF Token (F-TOKEN-1); no refresh endpoint (F-C-REFRESH-1) | **DEAD** |
| Token refresh discipline | **ABSENT** | **ABSENT** | No refresh endpoint (F-C-REFRESH-1); implicit no-refresh | **DEAD** |
| Logout revocation (basic) | PARTIAL | PARTIAL | Token deleted; silent 200 on unauth (F-C-LOGOUT-1); no event emit | WORKING-with-drift / EXPERIMENTAL |
| Logout revocation (enhanced) | PARTIAL | PARTIAL | Token deleted; IsAuthenticated guard; silent 200 on token-delete except; no event emit | WORKING / EXPERIMENTAL |
| Clear-Site-Data emission | **ABSENT** | **ABSENT** | Grep zero-match (F-C-CSD-1) | **DEAD** |
| Cookie SameSite/Secure/HttpOnly | DECLARED (per-env) | OBSERVABLE (browser dev-tools) | `settings.py:980-998` | WORKING |
| Cookie Domain / Path | **ABSENT** (Django default) | Implicit | F-C-COOKIE-1 | **PARTIAL** |
| Session engine + CACHE_ALIAS | DECLARED | OBSERVABLE | `settings.py:1105-1106` | WORKING |
| Session cookie age (14d) | DECLARED | OBSERVABLE | `settings.py:987` | WORKING |
| Session sliding TTL | DECLARED | OBSERVABLE | `SESSION_SAVE_EVERY_REQUEST=True` at `:1103` | WORKING |
| Session fixation defense (cycle_key) | **ABSENT** | **ABSENT** | Zero call sites (F-C-FIX-1 SPECULATIVE) | **PARTIAL** (bounded blast) |
| VIP token expiry (72h) | DECLARED | ENFORCED | `models_vip_invite.py:26`; `views_vip_invite.py:151-156` | WORKING |
| VIP account expiry (14d) | DECLARED-fiction | **NOT ENFORCED** | `models_vip_invite.py:27, 72`; zero enforcement (F-C-VIP-1) | **DEAD** |
| Mobile token revocation on logout | **ABSENT** | **ABSENT** | Zero `MobilePushToken.filter(user).update(revoked_at)` in logout paths (CF-C4) | **DEAD** |
| 15-surface storageKeys cleanup | 1 DECLARED / 14 NOT | 1 OBSERVABLE / 14 NOT | §14.2 table (F-C-STORE-1) | **1 WORKING / 3 PARTIAL / 11 DEAD** |
| Cross-tab logout propagation | **ABSENT** | **ABSENT** | Zero storage-event / BroadcastChannel (F-C-TAB-1) | **DEAD** |
| Login/logout event emission | **ABSENT** | **ABSENT** | Zero structured events (CF-C3 / Cat A CF-2) | **DEAD** |
| Session/token silent-degrade events | PARTIAL | Once-per-startup | F-SESS-1 warning at `settings.py:500` (Redis fallback); F-WS-1 silent AnonymousUser (no emit) | **PARTIAL** |
| Role-transition session-scope | **ABSENT** | **ABSENT** | Zero session-scoped role semantics (F-C-ROLE-SCOPE); 4-model landscape account-scoped | **DEAD** |

**Enforcement summary (21 lifecycle-observability loci):**
- 5 WORKING (session config declared + observable)
- 5 PARTIAL (working with drift or bounded issues)
- 11 DEAD (absent or not-enforced)

**Blocker to acceptance criterion #4:** 11-of-21 lifecycle-observability loci
are DEAD. Session-lifecycle discipline is undeclared at more than half of the
observable surfaces. Trust-boundary rate (Cat A §14.5) analog for lifecycle plane.

### 14.4 MEDIUM drifts (Cat C new)

**F-C-COOKIE-1 — `SESSION_COOKIE_DOMAIN` + `SESSION_COOKIE_PATH` +
`CSRF_COOKIE_DOMAIN` NOT declared** (**`drift` (documentary)**). Severity: **MED**.
S2400 §2.3 SPECULATIVE flag LIFTED with concrete finding: grep at HEAD across
`core/settings*.py` returns zero matches for the three variables. Django defaults
apply (Domain=None current-origin-only; Path='/' whole-app). Behavior is
correct-by-default but undocumented; no baseline for future subdomain / path-scoped
cookie decisions.

**F-C-LOGOUT-1 — Basic logout endpoint (`core/auth_views.py:84-94`) has NO
`@permission_classes`; silent 200 on unauth** (**`drift` + `technical_debt`**).
Severity: **MED** (Cat A silent-200 pattern preserved + Cat C formalization).
Unauth POSTer gets 200 because `request.user.auth_token.delete()` raises
`AttributeError` on AnonymousUser → caught at `:92` → 200 returned. Enhanced
endpoint at `auth_views_enhanced.py:539-556` FIXES this via
`@permission_classes([IsAuthenticated])` at `:540`. Basic remains unpatched.

**F-C-LOGOUT-2 — Enhanced logout endpoint silent-200 on token-delete exception**
(**`drift`**). Severity: **LOW-MED**. Even with `IsAuthenticated` guard, the
inner try/except at `auth_views_enhanced.py:545-552` swallows all exceptions and
returns 200. Failure mode: DB error during token.delete() → warning log +
`{'message': 'Logged out successfully'}` response with token still present.
Design-intentional (logout is idempotent from client perspective per Cat A §7),
but ambiguous when introspecting server-side state.

**F-C-FIX-1 — Session key rotation on auth boundary not evidenced** (Rigby SIGN
cycle 1 Q10 fold — dropped SPECULATIVE-CONCERN label since evidence is concrete
grep zero-match, not intent-inferred; normalized severity to LOW on standard
LOW/MED/HIGH/CRIT ladder — blast bounded by token-centric architecture) (**`technical_debt`**).
Severity: **LOW** (defense-in-depth gap; bounded blast). Grep at HEAD zero matches
for `cycle_key`, `session.cycle_key`, `request.session.set_expiry`,
`django.contrib.auth.login(` in `core/auth_views*.py`. Django `SessionMiddleware`
does NOT rotate session_key on `authenticate()` success unless `login()` is called.
REST auth endpoints use `Token.get_or_create` only. Blast bounded by token-centric
architecture (Django session used only for CSRF cookie identity; CSRF bypassed for
auth endpoints via `DisableCSRFForAuthEndpoints`). Defense-in-depth gap only.

**F-C-COCKPIT-1 — Cockpit two-stage auth MINOR-DRIFT re-verified STILL-LIVE at HEAD**
(**`drift`**). Severity: **MED** (Cat C bumped from S2201 LOW because pattern has
persisted through Group 2200 close + Cat A + Cat B without remediation).
`frontend/src/App.tsx:134-149` — 16 `/cockpit/*` `<Navigate>` redirects NOT wrapped
by `ProtectedRoute`. S2201 baseline behavior preserved. Post-arc T-slot decision:
(i) wrap in ProtectedRoute, (ii) document as Phase 1 legacy, OR (iii) retire
cockpit routes entirely.

**F-C-ROLE-SCOPE — 4-model role landscape lacks session-scope semantics**
(**`technical_debt`**). Severity: **MED**. Grep zero-match at HEAD for
`session['role']`, `session['effective_role']`, `request.session.__setitem__.*role`.
Role changes only observable to session after re-login (token cache carries user
object; DRF `TokenAuthentication.authenticate` re-queries user on each request but
role fields on user model are point-in-time-of-request). If platform needs "role
elevation for privileged action" (re-auth for admin) or "role revocation during
active session" (customer downgraded), no mechanism exists. Extends Cat A F-DUP-2
+ Cat B F-B-DUP-1 role-field-bifurcation to session-scope-absence.

### 14.5 LOW / observational (Cat C new)

**F-C-PA-CONV-1 — user-logout does NOT retire active PA conversation pins**
(**`drift`**). Severity: **LOW-MED**. Grep at HEAD for `session_tool.retire`
called from logout paths: zero matches. Chris's PA conversation pins (e.g.,
arc pin `pa-6279ead1714c4630` currently ACTIVE per S2400 provenance) remain
`session_active=True` after user logout. Not a security issue (conversation
ownership is user-scoped); observability issue (active-pin count grows over
time). CF-C2 to Group 2600 PA.

**F-C-MOBILE-1 — user-logout does NOT set `MobilePushToken.revoked_at`**
(**`drift` + `missing_connection`**). Severity: **LOW-MED** (extends Cat A CF-4).
Grep zero-match for `MobilePushToken.*revoked_at.*=` in logout paths. Mobile app
may continue receiving push notifications post-logout until next mobile-side
validate-token check. CF-C4 to Group 2300 Mobile.

**F-C-EVENT-1 — Zero login/logout structured event emission** (**`missing_connection`**).
Severity: **LOW-MED** (extends Cat A CF-2 + Cat B CF-B5). Grep at HEAD: no
`EventStream.*` calls in auth flows; no `AuthEvent` model; no login/logout events.
FleetAuthAuditLog + FleetPAChatAuditRow are Fleet-forensics tables, not
Observability-arc consumers. CF-C3.

---

## 15. Known Technical Debt

Debt matrix — severity + blast-radius + owner + age. Extends Cat A §15 + Cat B §15
with Cat C session-lifecycle-specific debt.

| Debt | Severity | Blast radius | Owner | Age (session onset) | Finding type |
|---|---|---|---|---|---|
| F-C-VIP-1 VIPInvite.account_expires_at NOT ENFORCED | **HIGH** | Every VIP user; account persists indefinitely | Auth (this arc) | S(VIP feature ship, 2026-03-04) | `technical_debt` + `unclear_owner` |
| F-C-REFRESH-1 No refresh endpoint / implicit no-refresh | **HIGH** | Every authenticated user; token permanent absent password event | Auth + API (CF-C1 to Group 2500) | Since always (DRF default) | `missing_connection` + `technical_debt` |
| F-C-CSD-1 Zero Clear-Site-Data emission on logout | **HIGH** | Every logout; cookies/storage/cache persist across auth boundary | Auth + API (CF-C1) | Since always | `drift` + `missing_connection` |
| F-C-STORE-1 14 of 15 client-side surfaces no declared cleanup | **HIGH** | Every logout; cross-user leakage on shared browsers (8-of-15 non-NONE severity) | Frontend (CF-C5 to Group 2200) | Since S2204 baseline (preserved at HEAD) | `technical_debt` + `drift` |
| F-C-TAB-1 Zero cross-tab logout coordination | **HIGH** (shared-browser context) / **MED** (single-user) | Multi-tab UX; tab-B stale-auth until 401 | Frontend (CF-C5) | Since always (0 BroadcastChannel + 0 storage-event) | `drift` + `missing_connection` |
| F-C-COOKIE-1 Cookie Domain/Path undeclared | **LOW-MED** (Rigby Q3 fold) | Session + CSRF cookies use Django defaults (current-origin, whole-app); correct-by-default but future-subdomain-contingent; no baseline for future subdomain sharing | Auth + Infra | Since always | `drift` (documentary) |
| F-C-LOGOUT-1 Basic logout NO permission decorator; silent 200 on unauth | **MED** | 1 endpoint (basic logout) | Auth | Since always (basic endpoint precedes enhanced) | `drift` + `technical_debt` |
| F-C-LOGOUT-2 Enhanced logout silent-200 on token-delete exception | **LOW-MED** | 1 endpoint (enhanced logout); ambiguous server-side state on DB failure | Auth | Since enhanced logout add | `drift` |
| F-C-FIX-1 No session.cycle_key on login (session key rotation not evidenced) | **LOW** (Rigby Q10 fold — normalized to standard severity ladder; bounded blast) | Django session identity (CSRF cookie); token-centric bounds blast | Auth | Since always | `technical_debt` (defense-in-depth) |
| F-C-COCKPIT-1 Cockpit two-stage MINOR-DRIFT re-verified STILL-LIVE | **MED** (Cat C promotion from LOW) | 16 `/cockpit/*` legacy routes | Frontend + Auth (shared) | Since S2201 baseline; unchanged through S2400 Cat A + Cat B | `drift` |
| F-C-ROLE-SCOPE 4-role landscape no session-scope semantics | **LOW-observational** (Rigby Q7(b) fold — no documented mid-session role transition requirement at HEAD) | Role changes invisible mid-session; no privileged re-auth mechanism | Auth + Users (CF-C2 to Group 2600) | Since always (4-model bifurcation baseline) | `technical_debt` |
| F-C-PA-CONV-1 User logout does NOT retire PA conversation pins | **LOW-MED** | Active PA pins grow post-logout | Auth + PA (CF-C2 to Group 2600) | Since PA `session_tool` add | `drift` |
| F-C-MOBILE-1 User logout does NOT set MobilePushToken.revoked_at | **LOW-MED** | Mobile push continues post-logout | Auth + Mobile (CF-C4 to Group 2300) | Since MobilePushToken add | `drift` + `missing_connection` |
| F-C-EVENT-1 Zero login/logout structured event emission | **LOW-MED** | Observability blind to lifecycle transitions | Auth + Observability (CF-C3 to Group 1700) | Since always | `missing_connection` |

Inherited from Cat A + Cat B (preserved as background — not re-scored — Rigby SIGN
cycle 1 Q16(a) fold: keep both IDs for provenance traceability; cross-reference
"same-issue lineage" where Cat C re-verifies):
- F-CRIT-1 (PURGE_SECRET) — CRITICAL, remediation P0 (post-arc)
- F-CRIT-2 (Session 1171 503-fork zero test) — HIGH
- F-VIP-1 (Cat A baseline) — **Same-issue lineage:** Cat C classifies under
  lifecycle plane as F-C-VIP-1 (declared-fictional class); re-verifies at HEAD
  8bc1b0c0; both IDs preserved for cross-arc traceability
- F-HIGH-2 (WS middleware dead-code) — HIGH
- F-HIGH-3 (PUBLIC_PATHS 265-entry registry drift) — HIGH
- F-WS-1 (WS silent AnonymousUser) — HIGH
- F-TOKEN-1 (Token no expiry) — MED — **Same-issue lineage:** Cat C classifies
  under lifecycle plane as F-C-REFRESH-1 (contract-absent class); both IDs
  preserved
- F-SESS-1 (Redis fallback silent) — MED
- F-DUP-2 (role bifurcation) — MED — **Same-issue lineage:** Cat C extends via
  F-C-DUP-3 §17 (lifecycle-plane 4-role completeness + fifth-role NEGATIVELY
  VERIFIED for S2403 snapshot); both IDs preserved
- F-B-CRIT-1 (permission-floor implicit rate ~80-90%) — CRITICAL (observability) —
  **Lifecycle relevance:** orthogonal / intersects at Cat D (permission checks
  gate lifecycle endpoints, but ownership remains Cat B; Cat D handles intersection)
- F-B-HIGH-3 (workspace-membership implicit-gate) — HIGH — **Lifecycle relevance:**
  intersects with F-C-STORE-1 (workspace-scoped state cleanup) + CF-C2 to Group
  2600 PA; ownership remains Cat B
- F-B-HIGH-4 (@authentication_classes stacking) — HIGH — orthogonal
- F-B-DUP-1 (4-role landscape customer_role orphaned) — MED — **Same-issue
  lineage:** Cat C extends via F-C-DUP-3 §17; both IDs preserved

**Cat C total new debt items: 14** (5 HIGH + 2 MED + 4 LOW-MED + 3 MED/PARTIAL).

---

## 16. Boundary Violations

Cat A §16 F-BND-0 (authority-vs-authentication) + F-BND-1 (VIPInvite→Deliverable
FK) + F-BND-4a/4b (bet-placement) preserved. Cat B §16 F-B-BND-0/1/2 preserved.

**F-C-BND-0 (Cat C new attestation) — Session-lifecycle plane preserves the
authority-vs-authentication boundary.** Grep at HEAD for `GovernanceState`,
`KillSwitch` in logout paths (`auth_views*.py`, `authStore.ts`): zero matches.
User-logout does NOT invalidate governance-consumer state (no KillSwitch reset,
no GovernanceState mutation). Grep for `from core.employees` or
`from core.services.ops_autopilot` in auth-view files: zero matches. **Class:
`mature_primitive`** (boundary preserved). CF-C7 to Group 1900 anchor-update.

**F-C-BND-1 (Cat C new) — Session-lifecycle plane DOES cross Auth ↔ Frontend
boundary at 15 client-side persistence surfaces.** Not a violation — this is the
intentional integration surface. Cat C's contribution is to make the CONTRACT
observable (§14.2 table). Currently the CONTRACT is undeclared (14-of-15 surfaces
no cleanup); once declared, this crossing becomes CONTRACT-preserved. **Class:
`missing_connection`** (contract absent, not boundary violated).

**F-C-BND-2 (Cat C new) — Session-lifecycle plane DOES cross Auth ↔ PA boundary
at `AssistantProfile.workspace` FK + `session_tool` conversation pins + paStore
workspace-context**. Same framing as F-C-BND-1 — intentional integration; contract
undeclared. CF-C2 to Group 2600 PA. **Class: `missing_connection`.**

**F-C-BND-3 (Cat C new) — Session-lifecycle plane DOES cross Auth ↔ Mobile
boundary at MobilePushToken lifecycle**. Same framing. CF-C4 to Group 2300 Mobile.
**Class: `missing_connection`.**

No new HIGH-severity boundary violations at Cat C scope.

---

## 17. Duplicate or Overlapping Systems

Cat A §17 F-DUP-1/2/3/4 + Cat B §17 F-B-DUP-1/2/3 preserved as background.

**F-C-DUP-1 (Cat C new) — Two logout code paths with divergent contracts.**
- Basic logout `auth_views.py:84-94` — no permission decorator; silent 200 on
  unauth (F-C-LOGOUT-1)
- Enhanced logout `auth_views_enhanced.py:539-556` — `@permission_classes([IsAuthenticated])`
  at `:540`; 403 on unauth; silent 200 on token-delete exception (F-C-LOGOUT-2)
Both delete `request.user.auth_token`; neither flushes Django session; neither
emits Clear-Site-Data. **Class: `duplicate_pattern` (structure finding).**
Severity: **MED** (consolidation candidate post-arc; behavior divergence causes
downstream confusion — frontend picks one; server has both). **Aggravator pointer
(Rigby SIGN cycle 1 Q17(b) fold):** Divergent logout contracts increases
likelihood of drift + missed fixes; see F-C-LOGOUT-1 for security impact
(basic endpoint permission-decorator absence). This DUP finding does NOT
duplicate F-C-LOGOUT-1 severity — it is the structural pointer that F-C-LOGOUT-1
is the underlying risk to remediate.

**F-C-DUP-2 (Cat C new) — Two login code paths with adjacent contracts.**
- Basic login `auth_views.py:24-81` — session-less token issuance
- Enhanced login `auth_views_enhanced.py:222-294` — session-less token issuance +
  optional remember_token (32-byte urlsafe secret at `:282`)
Same token issuance mechanism; enhanced adds features. **Class: `duplicate_pattern`**
(intentional overlap for feature evolution). Severity: **LOW** (working feature
evolution; consolidation not urgent).

**F-C-DUP-3 (Cat C new — Restatement for lifecycle-plane completeness; no new
risk introduced; closes Cat B SPECULATIVE-fifth-role for S2403 snapshot per
Rigby SIGN cycle 1 Q17(a) fold) — 4-model role landscape** (Cat A F-DUP-2 +
Cat B F-B-DUP-1 consolidated for session-scope analysis). Cat C confirms at HEAD:
- `UnifiedUser.platform_role` (6 values) — 5+ set-sites (setup_pa_service_account
  hardcode + Django field default); grep zero HTTP-layer read for auth decision
- `UnifiedUser.customer_role` (3 values) — orphaned (Cat B F-B-DUP-1); zero HTTP
  read; zero set-site outside field default
- `EnhancedUserProfile.primary_role` (free-text) — 5 set-sites (VIP exchange +
  intake × 3 + management command); 2 auth-decision read-sites (vip_middleware,
  vip_scope)
- `AssistantProfile.role` (3 values) — set at profile creation; read for
  ROLE_PROMPTS + ROLE_TOOLS PA-payload gate
No fifth-role carrier at HEAD (Cat B Q13 SPECULATIVE hypothesis NEGATIVELY VERIFIED).
Session-scope semantics: **ABSENT** (F-C-ROLE-SCOPE). **Class: `duplicate_model`.**
Severity: **MED** (Cat A/B baseline preserved; Cat C confirmation).

---

## 18. Ownership Gaps

Cat A §18 F-OWN-1/2/3 + Cat B §18 F-B-OWN-1/2/3/4/5/6 preserved as background.

**F-C-OWN-1 (Cat C new) — Session-lifecycle plane is cross-arc by design;
no single owner expected. xx99 is the coordination decision point (Chris)**
(Rigby SIGN cycle 1 Q18 fold — reframed from "owner UNCLEAR" reads-as-defect
to descriptive-observation of intentional cross-arc structure). The
lifecycle-CONTRACT decision-space naturally spans multiple arcs:
- Refresh discipline (F-C-REFRESH-1) — Auth + API coordination
- Clear-Site-Data emission (F-C-CSD-1) — Auth + API coordination
- 15-surface cleanup contract (F-C-STORE-1) — Frontend + Auth coordination
- Cross-tab coordination (F-C-TAB-1) — Frontend
- Cookie discipline (F-C-COOKIE-1) — Auth + Infra
- Role-transition semantics (F-C-ROLE-SCOPE) — Auth + Users
- Login/logout event emit (CF-C3) — Auth + Observability
- Mobile-token revocation (CF-C4) — Auth + Mobile
- PA conversation retire on user-logout (CF-C2) — Auth + PA
Cat C's role: surface the cross-arc structure; enumerate the 7 coordination
flags (CF-C1 → CF-C7); pass three-option decision-space (§19.1) to xx99 for
Chris D-verdict. **Class: `unclear_owner` (structural, not defect).** Severity:
**MED** (coordination cost, not urgency).

**F-C-OWN-2 (Cat C new) — Session-lifecycle test coverage owner UNCLEAR.**
Extending Cat A F-CRIT-2 (Session 1171 503-fork zero test coverage) + Cat B
F-B-OWN-6 (CI test-harness enforce permission-floor declarations). Cat C addition:
0-of-17 session-lifecycle endpoints have declared smoke-test coverage (login basic,
login enhanced, logout basic, logout enhanced, register, verify-email,
forgot-password, reset-password rotate, change-password, validate-token, user, debug
phantom, resend-verification, vip-invite create/exchange/revoke, accounts/logout).
Test authoring is post-arc; ownership question is arc-close deliverable. **Class:
`unclear_owner`.** Severity: **MED**.

---

## 19. Recommended Future Research

### 19.1 POSTURE-DECISION evidence plan for xx99 (three-option decision space per S2400 §3.C output (d))

Cat C's owning decision-space per parent contract. Chris-D-verdict-request at
S2499 xx99 close.

**Option (α) — Silent-refresh (opaque to user; hides expiry via automatic refresh).**

Requires:
- Refresh-token endpoint `/api/v1/auth/refresh/` (Group 2500 API scope)
- Token model expiry field (migration on DRF `authtoken.Token` OR wrapper table)
- Rotation-on-use policy (one-use refresh tokens with nonce tracking) OR sliding-window refresh
- FE axios interceptor at `api.ts:48-56`: on 401 for non-auth endpoint → call refresh → retry
- Cross-tab race handling (refresh-in-Tab-A + parallel-401-in-Tab-B → BroadcastChannel signal)
- Mobile app support: mobile SDK integrates refresh flow

Blast radius:
- BE: new endpoint + token model change + rotation policy (nonce tracking Redis-backed) + observability integration
- FE: axios interceptor changes + refresh-token state in authStore
- Cross-tab: BroadcastChannel + refresh-race-handling
- Mobile: mobile SDK changes (CF-C4)

Migration cost: **HIGH** (BE + FE + Mobile + Cross-tab all touched)

Observability cost: **HIGH** (silent refresh hides expiry; requires
instrumentation to see refresh-rate + stale-token catch — extends CF-C3)

Compatibility with Cat A baseline: F-TOKEN-1 "no expiry" contradicts silent-refresh
unless expiry ADDED. Requires token model change.

Compatibility with Cat D (S2404): 401 → refresh → retry pattern REDUCES Cat D's
silent-401 SYSTEMIC surface (fewer user-visible 401s); increases hidden-failure
surface (silent refresh loop can mask permission-floor issues).

Risk profile: Maximum UX continuity; complexity; requires careful nonce handling
to avoid replay attacks.

**Option (β) — Explicit re-login (visible; user-friction; simpler contract).**

Requires:
- Optional token expiry field (for audit only) OR periodic revocation task
  (Group 1700 Observability scope for beat)
- FE `api.ts:48-56` interceptor extended: on 401 → show login modal / redirect
- Clear-Site-Data emission on logout (F-C-CSD-1 remediation)
- BE logout endpoint response envelope formalized (F-C-LOGOUT-1 remediation)

Blast radius:
- BE: logout endpoint response envelope + optional token expiry field (migration)
- FE: 401-modal integration
- Cross-tab: storage-event listener (F-C-TAB-1 remediation) — Tab-B observes
  Tab-A logout via `auth-storage` mutation → redirect to /login
- Mobile: mobile app handles 401 as re-auth prompt naturally

Migration cost: **LOW-MED** (BE small changes; FE modal; storage-event listener
is 5-10 LOC)

Observability cost: **LOW-MED** (logout + redirect user-visible; event-emit via
CF-C3 sufficient)

Compatibility with Cat A baseline: F-TOKEN-1 "no expiry" CAN REMAIN; optional
expiry field for audit-only.

Compatibility with Cat D (S2404): 401 → modal is USER-VISIBLE; Cat D adopts
typed-error-envelope with `session_expired` code; silent-401 SYSTEMIC reduces to
handled-401 EXPLICIT.

Risk profile: Simplicity + observability > UX friction; multi-tab observable;
mobile-native flow.

**Option (γ) — Hybrid (silent while active, explicit after N-min idle).**

Requires:
- Everything from (α): refresh endpoint + token expiry + rotation policy
- Everything from (β): 401-modal + Clear-Site-Data + logout envelope
- Activity-tracking: `last_activity_at` timestamp on token (or session-side); N-min
  configurable idle-threshold
- FE mouse/keyboard/scroll listener for activity tracking

Blast radius: SUPERSET of (α) + (β)

Migration cost: **HIGHEST**

Observability cost: **MED** (activity visible; refresh-attempt observable; modal
on fallback observable — but complexity leaks into telemetry)

Risk profile: Balances UX + simplicity; multi-tab race-conditions require careful
sequencing.

**Cat C proposes β as least-assumption default for xx99 evaluation** (Rigby SIGN
cycle 1 Q19 fold — tighter language avoiding design-authoring pretense; Cat C
delivers evidence + proposed default; Chris D-verdicts at xx99):

**Option (β) explicit-re-login as PROPOSED PRIMARY DEFAULT** for the REMEDIATION
WINDOW because:
1. Zero token-model changes required (F-TOKEN-1 baseline preserved)
2. Zero new BE endpoint required (F-C-REFRESH-1 gap remains but bounded by
   documented no-refresh contract)
3. Lowest migration cost (BE + FE small changes)
4. Highest observability (all lifecycle transitions user-visible + event-emit
   via CF-C3)
5. Compatible with Cat D (S2404) typed-error-envelope work — session_expired
   becomes explicit typed error
6. Compatible with F-C-STORE-1 remediation (logout + Clear-Site-Data +
   storageKeys cleanup align at same emission point)

**Option (α) or (γ) as post-arc ENHANCEMENT** if:
- UX friction from explicit re-login exceeds tolerance (measure post-β adoption)
- Refresh discipline becomes operationally important (audit compliance)
- Mobile app UX becomes a differentiator (silent refresh matters more on mobile)

**Risk-gating constraint (Rigby SIGN cycle 1 Q19 fold + pre-commit nit 3 —
framed as risk gating NOT product direction; scope tightened to avoid artificially
coupling unrelated decisions):** Shipping any user-facing lifecycle change that
relies on expiry semantics or VIP safety signals (any α/β/γ that surfaces
"session expires at X" or "account valid until Y" to users) without ALSO closing
F-C-VIP-1 (account_expires_at enforcement) creates a misleading safety signal —
clients see enforced session lifecycle UX but VIP account expiry remains
declared-fictional. Treat F-C-VIP-1 remediation as a **prerequisite for shipping
any user-facing lifecycle change that relies on expiry semantics / VIP safety
signals**. VIP account lifecycle is orthogonal to token-refresh discipline;
F-C-VIP-1 must close before any expiry-signal-bearing UX ships regardless of
α/β/γ choice.

### 19.2 Cat C post-arc remediation queue (rank-1 P0 batch preserved from Cat A + Cat B; Cat C additions)

Per Cat B §19.2 rank-1 co-equal P0 batch — Cat C extends:

**Rank-1 co-equal P0** (POST-ARC not this session):
- Cat A F-CRIT-1 PURGE_SECRET hardcoded fallback remediation (P0 PR)
- Cat A F-BND-4a Unauthenticated bet-placement WRITE remediation (P0 PR)
- F-C-VIP-1 VIPInvite.account_expires_at ENFORCEMENT (Cat C NEW P0 candidate;
  runtime middleware check OR periodic beat task)

**Rank-2 HIGH** (POST-ARC):
- Cat B F-B-CRIT-1 permission-floor implicit-inheritance
- Cat B F-B-CRIT-2 silent-401 SYSTEMIC (Cat D S2404 owns)
- Cat A F-HIGH-1 STAFF_REQUIRED_PATHS phantom-entries
- Cat A F-HIGH-4 auth_views_enhanced.py `@authentication_classes([])` stacking
- F-C-REFRESH-1 refresh discipline decision-space execution (post-Chris-verdict)
- F-C-CSD-1 Clear-Site-Data emission
- F-C-STORE-1 15-surface × logout-cleanup declared contract execution
- F-C-TAB-1 cross-tab storage-event listener

**Rank-3 MED** (POST-ARC):
- F-C-COOKIE-1 cookie Domain/Path declaration
- F-C-LOGOUT-1 basic logout permission decorator or endpoint retirement
- F-C-COCKPIT-1 cockpit two-stage remediation (S2201 T-slot)
- F-C-ROLE-SCOPE role-transition session-scope semantics (Group 2600 PA scope)
- F-C-FIX-1 session.cycle_key defense-in-depth

**Rank-4 LOW-MED** (POST-ARC):
- F-C-LOGOUT-2 enhanced logout silent-200 refinement
- F-C-PA-CONV-1 user-logout session_tool.retire cascade (Group 2600 PA)
- F-C-MOBILE-1 MobilePushToken.revoked_at cascade (Group 2300 Mobile)
- F-C-EVENT-1 login/logout event emit (Group 1700 Observability)

### 19.3 Cat C emerging weak-spot Q20-fold candidate (playbook §20 codification-candidate)

**Silent-degrade vs explicit-failure ambiguity on session-lifecycle plane.**

Extending Cat B Q20 fold denominator-ambiguity codification candidate. Cat C's
candidate targets a different weak-spot at the session-plane level:

**Evidence:** Cat C's findings decompose cleanly on this axis:
- F-C-VIP-1: silent (account expiry never checked; TTL fictional)
- F-C-REFRESH-1: silent (no refresh contract; token implicitly permanent)
- F-C-CSD-1: silent (no header emission; browser cookies persist)
- F-C-STORE-1: silent (14-of-15 surfaces persist across logout)
- F-C-TAB-1: silent (0 cross-tab coordination; tab-B stale)
- F-C-COOKIE-1: silent (Django defaults undocumented)
- F-C-LOGOUT-1/2: silent (200 on failure)
- F-C-FIX-1: silent (no cycle_key; session identity stable)
- F-C-COCKPIT-1: silent (client-side redirect before protection)
- F-C-ROLE-SCOPE: silent (role changes invisible mid-session)
- F-C-PA-CONV-1: silent (PA pins persist post-logout)
- F-C-MOBILE-1: silent (mobile push continues)
- F-C-EVENT-1: silent (no lifecycle event emission)

**13-of-14 Cat C findings are silent-degrade class.** The plane has near-zero
explicit-failure paths.

**Codification proposal (§20 playbook 2nd application candidate at S2499 xx99):**
"For any session-lifecycle or authority-bearing plane, audit systematically for
silent-degrade patterns; categorize as (i) intentional soft-degrade with declared
fallback + observability signal, (ii) accidental silent-swallow (no fallback
declared, failure invisible), (iii) contract-absent (no failure mode declared).
Require explicit-failure OR explicit-fallback-declaration for authority-bearing
planes."

**Distinct from Cat B denominator-ambiguity** (Rigby SIGN cycle 1 Q20(a) fold —
explicit contrast sentence added): **Cat B denominator-ambiguity = measurement /
metrics ambiguity (what's the denominator? how do we count?); Cat C silent-degrade
ambiguity = runtime UX / telemetry ambiguity (is the failure declared? is the
degrade observable?).** Together they form a maturity discipline: measure first
(Cat B), then declare failure modes (Cat C).

**Playbook §20 two-trigger rule (Rigby SIGN cycle 1 Q20(b) fold — explicit
two-trigger statement):** Cat C is TRIGGER #1 for silent-degrade-vs-explicit-failure
codification. Promotion to playbook v3 requires TRIGGER #2 in Cat D (S2404) or
a future arc. If Cat D surfaces the same pattern in its silent-401 SYSTEMIC audit
— which is highly likely given F-C-CSD-1 + F-C-STORE-1 + F-C-TAB-1 all point to
Cat D's frontend caller surface — codification threshold satisfied at S2499 xx99
close. If Cat D does NOT surface the pattern, defer to future arc for TRIGGER #2.

### 19.4 Anchor-update recommendations for xx99

Preserve Cat A + Cat B recommendations; Cat C additions:

- **AU-C1** — Add session-lifecycle subsection to prospective `docs/topics/auth.md`
  (if AU-1 lands). Covers issuance / refresh / logout / cookie discipline /
  15-surface cleanup / role-transition. Extending Cat A AU-1.
- **AU-C2** — Extend `PLATFORM_INVENTORY §Auth` autoblock (if AU-1 lands) with
  session-lifecycle count block: issuance-call-sites (5), rotation-call-sites
  (2), revocation-call-sites (2), refresh-endpoints (0 ABSENT), Clear-Site-Data
  emission sites (0 ABSENT). Extending Cat A AU-1.
- **AU-C3** — Extend `PLATFORM_WHAT_IT_IS §Auth` narrative subsection (if
  AU-1 lands) with session-lifecycle contract framing: three-option decision-space
  + Chris-ratified lean rationale. Extending Cat A AU-1.
- **AU-C4** — Optional `docs/topics/session_lifecycle.md` standalone doc if
  session-lifecycle contract warrants dedicated narrative (post-Chris-D-verdict
  on α/β/γ).
- **AU-C5** — Cookie-defaults per-cookie table (F-C-COOKIE-1 remediation
  documentary output) in Auth topic doc.

### 19.5 Follow-on research queue (post-arc T-slot at xx99)

Preserved from Cat A + Cat B + S2204 R1-R10 baseline. Cat C additions:
- Session-lifecycle observability instrumentation (F-C-EVENT-1 + Cat A CF-2 +
  Cat B CF-B5 consolidated) — Group 1700 arc
- Cross-tab logout propagation implementation (F-C-TAB-1) — Group 2200 T-slot
  post-arc
- 15-surface × logout-cleanup declared contract execution (F-C-STORE-1) — Group
  2200 T-slot
- Mobile session-lifecycle contract (CF-C4) — Group 2300 arc (deferred)
- PA conversation retire cascade on user-logout (CF-C2 extension) — Group 2600 arc

---

## 20. Appendix

### 20.1 Files inspected (HEAD `8bc1b0c0`)

Backend session/auth:
- `core/settings.py` (SESSION_* + CSRF_* + CACHES + MIDDLEWARE)
- `core/auth_views.py` (basic login/logout/current_user)
- `core/auth_views_enhanced.py` (enhanced login/register/verify/forgot/reset/change/logout/validate-token/debug)
- `core/urls.py` (auth URL routes 2183-2197 + accounts/logout 1626)
- `core/models_vip_invite.py` (VIPInvite 72h + 14d fields)
- `core/models_assistant_profile.py` (role field + ROLE_PROMPTS/TOOLS)
- `core/models/base/models.py` (UnifiedUser + platform_role + customer_role)
- `core/models/users/models.py` (EnhancedUserProfile + primary_role)
- `core/models_mobile.py` (MobilePushToken)
- `core/auth_middleware.py` (Cat A reference — middleware chain)
- `core/ws_auth_middleware.py` (Cat A reference — silent AnonymousUser)
- `core/vip_middleware.py` (Cat A reference — VIP HTTP gate)
- `core/views_vip_invite.py` (VIP exchange + revoke)
- `core/services/td_handlers_core.py` (session_tool actions 3984-4166)

Frontend session/state:
- `frontend/src/stores/authStore.ts` (login/logout/state — Zustand persist auth-storage)
- `frontend/src/stores/navigationStore.ts` (recentEntities — S2204 F8)
- `frontend/src/stores/paStore.ts` (v3+migrate; syncUser field-list — S2204 F7)
- `frontend/src/stores/workspaceStore.ts` (in-memory-only — S2204 F5)
- `frontend/src/lib/api.ts` (silent-401 handler — Cat D scope reference)
- `frontend/src/components/layout/Sidebar.tsx` (logout onClick)
- `frontend/src/App.tsx` (ProtectedRoute + 16 cockpit legacy redirects lines 134-149)

Docs consumed:
- `docs/research/domains/auth/2400_auth_domain_scoping.md` (parent scope)
- `docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md` (Cat A)
- `docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` (Cat B)
- `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md` (§14.3 cockpit)
- `docs/research/domains/frontend/2204_frontend_session_state_persistence_discipline_audit.md` (15-surface baseline + R1 two-sided framing)

### 20.2 Grep patterns used

- `SESSION_ENGINE|SESSION_CACHE_ALIAS|SESSION_COOKIE_AGE|SESSION_COOKIE_HTTPONLY|SESSION_COOKIE_SECURE|SESSION_COOKIE_SAMESITE|SESSION_COOKIE_DOMAIN|SESSION_SAVE_EVERY_REQUEST|SESSION_EXPIRE_AT_BROWSER_CLOSE|SESSION_COOKIE_NAME|SESSION_COOKIE_PATH` — cookie config declarations
- `CSRF_COOKIE_HTTPONLY|CSRF_COOKIE_SECURE|CSRF_COOKIE_SAMESITE|CSRF_USE_SESSIONS|CSRF_TRUSTED_ORIGINS|CSRF_COOKIE_NAME|CSRF_COOKIE_DOMAIN` — CSRF cookie config
- `path\(.*[Ll]ogout|path\(.*[Ll]ogin|path\(.*validate.?token|path\(.*refresh|path\(.*forgot.?password|path\(.*reset.?password|path\(.*auth/debug` — auth URL routes
- `Clear-Site-Data` — production emission (zero-match verified F-C-CSD-1)
- `\.filter\(account_expires_at|account_expires_at.__lt|account_expires_at <|account_expires_at.gt` — VIP expiry enforcement (zero-match F-C-VIP-1)
- `cycle_key|session\.cycle_key|request\.session\.set_expiry|django\.contrib\.auth\.login\(` — session fixation defense (zero in auth views — F-C-FIX-1)
- `session\['role'\]|session\.get\('role'\)|session\['effective_role'\]` — session-scoped role (zero-match F-C-ROLE-SCOPE)
- `import jwt|import PyJWT|import jose|SimpleJWT` — JWT libraries (zero-match; Cat B Q13 SPECULATIVE-fifth-role NEGATIVELY VERIFIED)
- `user\.groups\.add|user\.user_permissions\.add` — Django Group/Permission M2M (zero-match)
- `BroadcastChannel|storage\.\.event|addEventListener\('storage'` — cross-tab coordination (zero-match F-C-TAB-1)
- `MobilePushToken.*revoked_at.*=|MobilePushToken\.filter.*update.*revoked` — mobile revocation on logout (zero-match F-C-MOBILE-1)
- `session_tool.*retire|retire.*conversation.*logout` — PA pin retire on logout (zero-match F-C-PA-CONV-1)
- `EventStream\.|AuthEvent|LoginEvent|LogoutEvent` — structured event emission (zero-match F-C-EVENT-1)
- `refresh_token|TokenRefresh|RefreshView|token/refresh/` — session-token refresh (zero-match for auth surface F-C-REFRESH-1)

### 20.3 Unresolved unknowns

None load-bearing at Cat C close. All SPECULATIVE flags from S2400 §2.3 LIFTED:
- Cookie SameSite/Secure/HttpOnly defaults: §3 CONFIRMED declared
- Cookie Domain/Path: F-C-COOKIE-1 CONFIRMED absent (SPECULATIVE lifted; concrete
  finding)
- Fifth-role carrier hypothesis: Cat B Q13 NEGATIVELY VERIFIED via JWT +
  Group/Permission + feature-flag grep zero-matches

Remaining POSTURE-DECISION-PENDING items (Chris-D-verdict at xx99):
- α/β/γ three-option lean (Cat C recommends β; Chris ratifies at xx99)
- Cat A + Cat B + Cat C anchor-update-candidate consolidation (xx99 §7 scope)
- 4-model role landscape consolidation ADR (Group 2600 PA post-arc)

### 20.4 Denominator declaration ledger (Cat B Q20 fold PRE-EMPTIVE discipline)

Every count in this audit with explicit denominator + source:

| Count | Denominator | Source / Method |
|---|---|---|
| 15 persistent-state surfaces (3 Zustand + 12 direct localStorage) | Total client-side session-scope persistence at HEAD | S2204 §14 F1 baseline + HEAD file:reads + grep for `localStorage.setItem` / `persist(` (zero new keys discovered) |
| 1/15 CLEAN cleanup (authStore functional-null-state) | 15 surfaces | §14.2 per-surface CONTRACT table + HEAD file:read of authStore.ts:34-39 |
| 3/15 PARTIAL cleanup (paStore syncUser incomplete + pipeline_dismissed workspace-change + podcast_voice_profile change) | 15 surfaces | §14.2 |
| 11/15 NO-CLEANUP | 15 surfaces | §14.2 |
| 17 session-lifecycle-relevant REST endpoints | Auth surface (Cat A §3 baseline + Cat C extension) | §6.1 enumeration |
| 6 Token issuance sites | Grep `Token.objects.get_or_create(user=` in `core/` | Cat A §8 baseline preserved |
| 2 Token rotation sites | Grep `Token.objects.filter(user=user).delete\(\) + create` | auth_views_enhanced.py:396-399, 460-461 |
| 2 Token revocation sites | Grep `request.user.auth_token.delete\(\)` in `core/auth_views*.py` | auth_views.py:90 + auth_views_enhanced.py:547 |
| 1 Django session flush site | Grep `logout\(request\)` = `django.contrib.auth.logout` | urls.py:1626 only |
| 0 refresh endpoint | Grep `path.*refresh` in urls.py filtered to auth surface | 3 matches all non-auth; F-C-REFRESH-1 |
| 0 Clear-Site-Data emission | Grep `Clear-Site-Data` in `core/**` + `frontend/**` | zero production matches; F-C-CSD-1 |
| 21 lifecycle-observability loci | Cat C §14.3 table enumeration | 5 WORKING + 5 PARTIAL + 11 DEAD |
| 4 role fields (F-DUP-2 + F-B-DUP-1 baseline) | Cat A + Cat B baseline preserved | Cat C confirmed at HEAD |
| 0 fifth-role carrier | Grep JWT libs + Django M2M + feature-flag | ABSENT confirmed |
| 16 cockpit legacy redirects | frontend/src/App.tsx:134-149 | HEAD file:read |
| 11 WS consumers (1 hard-reject + 10 accept-anon) | Cat A §6 baseline | Preserved at HEAD |
| 5 Cat A session-lifecycle-relevant findings inherited | Cat A §14 (F-TOKEN-1, F-VIP-1, F-SESS-1, F-WS-1, F-DUP-2) | Preserved as background |
| 3 Cat B session-lifecycle-adjacent findings inherited | Cat B §14 (F-B-HIGH-3, F-B-DUP-1, F-B-BND-2) | Preserved as background |
| 3 S2204 findings promoted (F1, F6, F8) | S2204 §14 preserved at HEAD baseline | Zero delta since S2204 close |
| 14 Cat C new findings (5 HIGH + 2 MED + 4 LOW-MED + 3 MED/PARTIAL) | §14 + §15 debt matrix | Full enumeration |
| 7 cross-arc coordination flags (CF-C1 → CF-C7) | §9.2 + §19.4 | Full enumeration |
| 5 anchor-update candidates (AU-C1 → AU-C5) | §19.4 | Full enumeration |

**Denominator discipline verdict:** Every count declared with explicit denominator +
grep pattern + HEAD-verification status. Zero unattributed counts.

### 20.5 Conflicts between sources (verifier-loop history)

**Conflict 1 (resolved pre-draft):** Agent 3 vs Agent 1 on `logout_enhanced_view`
permission decorator.
- Agent 3 asserted `/api/v1/auth/logout-enhanced/` has "permission_classes: none"
- Agent 1 asserted `logout_enhanced_view` has `@permission_classes([IsAuthenticated])`
- Parent verifier-loop read `core/auth_views_enhanced.py:539-556` at HEAD 8bc1b0c0
- Confirmed line 540: `@permission_classes([IsAuthenticated])` — Agent 1 correct
- Impact: F-C-LOGOUT-1 severity classification (basic endpoint remains F-C-LOGOUT-1;
  enhanced correctly documented at F-C-LOGOUT-2 with `IsAuthenticated` guard)

No other conflicts caught pre-draft. Denominator discipline (Rigby S2402 Q20 fold)
pre-emptively applied throughout — zero denominator-ambiguity findings expected
at Rigby SIGN cycle 1.

### 20.6 Rigby SIGN cycle 1 fold ledger (CLOSED 2026-07-05)

Rigby SIGN cycle 1 delivered 27 folds across 4 batches × 5 Q each = 20 total Q.
Batch 1 verdict SIGN-with-edits; Batch 2 verdict NEEDS-MORE (blocking folds
landed pre-Batch-3); Batch 3 verdict SIGN-with-edits; Batch 4 verdict
SIGN-with-edits + explicit "close cycle" signal ("Net: you can close the cycle
once those edits are made"). Cycle 2 NOT required per Rigby cycle-1 sign-off +
all 27 folds landable pre-Chris-ratification. **EIGHTH-consecutive 20-Q cadence
application** in Research OS (after S2201/S2202/S2203/S2204/S2401/S2402 six-consecutive-tested
pattern + this cycle = 7-consecutive-tested-plus-Cat-A; MC-10 codification-ready-pending-Chris
at 8-arc baseline).

Batch 1 folds (Q1-Q5 executive framing):
- F1 (Q1) Maturity lens rephrase from "WORKING-CORRECTNESS + EXPERIMENTAL-GOVERNANCE"
  to "WORKING-at-mechanism-layer + PARTIAL-at-lifecycle-semantics + EXPERIMENTAL-at-governance"
  — §1
- F2 (Q2) Acceptance-criterion scoring 2-axis: Platform outcome (FAIL) vs Audit
  outcome (PASS) — §1 table
- F3 (Q3) F-C-COOKIE-1 severity MED → LOW-MED (Django defaults correct; documentary
  only) — §1 + §14.4 + §15
- F4 (Q4) Add 4th seam class "declared-fictional"; F-C-VIP-1 reclassified from
  silent-swallow to declared-fictional; F-C-LOGOUT-1/2 clarified as silent-swallow;
  F-C-REFRESH-1/F-C-CSD-1/F-C-COOKIE-1 clarified as contract-absent — §1

Batch 2 folds (Q6-Q10 sections 3-8; NEEDS-MORE resolved):
- F5 (Q6a) DiscordLinkCode marked out-of-scope with rationale — §5 (auth-adjacent,
  not session lifecycle)
- F6 (Q6b) PasswordResetTokenGenerator marked out-of-scope with rationale — §5
- F7 (Q6c) Line-drift corrections: register 48 → 50; forgot 297 → 299; reset 357 →
  359 (HEAD-verified via grep) — §6.1
- F8 (Q7a) Cat B SPECULATIVE-fifth-role hypothesis "NEGATIVELY VERIFIED FOR
  S2403 SNAPSHOT" (Cat C closes for this snapshot; Cat B keeps label for own
  follow-up ownership) — §4 (role landscape)
- F9 (Q7b) F-C-ROLE-SCOPE severity MED → LOW-observational (no documented mid-session
  role transition requirement at HEAD) — §4 + §14.4 + §15
- F10 (Q9a) VIP invite exchange HEAD-verified via `views_vip_invite.py:85-163` +
  `invite.is_valid` property at `models_vip_invite.py:95-103` — confirmed ONLY
  `token_expires_at` (72h) enforced; response body returns `account_expires_at.isoformat()`
  at line 161 as declared-fictional aggravator (server tells client an expiry
  it will never enforce) — §6.1 row updated
- F11 (Q9b) Django `accounts/logout` HEAD-verified: `django.contrib.auth.logout()`
  at `django/contrib/auth/__init__.py:160-171` calls `request.session.flush()`
  at line 171 (Python 3.11 stdlib) — §6.1 row updated with citation
- F12 (Q10a) F-C-FIX-1 label: dropped SPECULATIVE-CONCERN sentinel (evidence is
  concrete grep zero-match); renamed to "Session key rotation on auth boundary
  not evidenced" — §14.4 + §15
- F13 (Q10b) F-C-FIX-1 severity: normalized from PARTIAL to LOW on standard
  ladder — §14.4 + §15

Batch 3 folds (Q11-Q15 sections 9-14):
- F14 (Q11a) CF-C3 kept as single tracking unit with sub-bullets (NOT split into
  three flags — governance noise avoided; xx99 roll-up preserved via link) — §9.2
- F15 (Q11b) CF-C8 for Fleet HMAC rejected (Fleet orthogonal per Cat A
  trust-boundary framing; not session-lifecycle scope) — §9.2 (not added)
- F16 (Q12) CF-C3 preserved as own tracking unit; explicit link to Cat A CF-2 +
  Cat B CF-B5 for xx99 §5.4 Observability umbrella roll-up — §9.2
- F17 (Q13) MODERATE+ definition added: "multiple-category audits closing major
  entry points + runtime flows within a single domain plane; DEEP requires
  cross-category completion (Cat D + xx99)" — §12
- F18 (Q14a) §13 primitives table preserved without DiscordLinkCode/Fleet rows
  (avoid table bloat; orthogonal per §5 out-of-scope note) — §13
- F19 (Q14b) Overall maturity verdict PARTIAL preserved (product-contract
  statement, not primitive-fraction math) — §13
- F20 (Q15a) §1 executive: reconciled "seven headline findings" as "top items
  worth reading" vs severity distribution "HIGH=4, non-HIGH=3" post-fold-normalization
  — §1
- F21 (Q15b) F-C-TAB-1 two-context severity split preserved: HIGH (shared-browser)
  / MED (single-user) — §14.1 + §15

Batch 4 folds (Q16-Q20 sections 15-20 + emerging weak-spot):
- F22 (Q16a) Cat A + Cat B inherited findings preserved as background with
  "Same-issue lineage" cross-reference lines for overlaps (F-VIP-1 ↔ F-C-VIP-1;
  F-TOKEN-1 ↔ F-C-REFRESH-1; F-DUP-2 ↔ F-C-DUP-3); NOT merged (provenance
  preserved) — §15
- F23 (Q16b) Cat B F-B-CRIT-1 explicitly labeled "orthogonal / intersects at
  Cat D"; other Cat B findings similarly labeled for lifecycle-plane relevance — §15
- F24 (Q17a) F-C-DUP-3 marked "Restatement for lifecycle-plane completeness; no
  new risk introduced; closes Cat B SPECULATIVE-fifth-role for S2403 snapshot" — §17
- F25 (Q17b) F-C-DUP-1 severity MED preserved (structure finding); added
  aggravator-pointer label to F-C-LOGOUT-1 (avoids double-counting risk; DUP
  points to underlying LOGOUT security impact) — §17
- F26 (Q18) F-C-OWN-1 reframed from "owner UNCLEAR" (defect-reading) to
  "Session-lifecycle plane is cross-arc by design; no single owner expected; xx99
  is the coordination decision point (Chris)" — §18
- F27 (Q19) §19.1 language tightened: "Cat C proposes β as least-assumption
  default for xx99 evaluation" (NOT "Cat C recommends"); anti-recommendation
  reframed as "Risk-gating constraint: shipping α/β/γ without F-C-VIP-1
  remediation creates misleading safety signal; treat F-C-VIP-1 remediation as
  prerequisite for any α/β/γ decision" — §19.1
- F28 (Q20a) Explicit contrast sentence: "Cat B denominator-ambiguity = measurement
  / metrics ambiguity; Cat C silent-degrade ambiguity = runtime UX / telemetry
  ambiguity" — §19.3
- F29 (Q20b) Explicit two-trigger rule statement: Cat C is TRIGGER #1; Cat D
  likely surfaces TRIGGER #2 in silent-401 SYSTEMIC audit; codification threshold
  satisfied at S2499 xx99 close if Cat D confirms — §19.3

Pre-commit nits (Rigby ratification-card review 2026-07-05):
- F30 (Nit 1) §1 executive lens sentence tightened to "WORKING mechanisms /
  PARTIAL lifecycle correctness + EXPERIMENTAL governance" to match scoring
  language (avoid "WORKING correctness" reading as "safe/complete") — §1
- F31 (Nit 2) F-C-COOKIE-1 severity label clarified as "LOW-MED (documentary
  gap only)" with explicit sentence "Django defaults are correct at HEAD; risk
  is drift if later subdomain/path scoping is introduced." — §1 + §14.4
- F32 (Nit 3) Risk-gating constraint scope tightened from "prerequisite for any
  α/β/γ decision" to "prerequisite for shipping any user-facing lifecycle change
  that relies on expiry semantics / VIP safety signals" — avoids artificially
  coupling unrelated decisions — §19.1

**Fold count final: 32** (spanning 20 Rigby SIGN Q + 3 pre-commit nits from
ratification-card review; some Q generated multiple folds).

**SIGN pin retirement:** `pa-5096f5fc07754b18` retired via `session_tool.retire`
at cycle close 2026-07-05 per playbook §15 SIGN-isolation discipline
(updated_count=4, previously_active=true, retired=true).

### 20.7 Provenance chain

- 2026-07-05: S2400 parent scoping close (Chris "commit it" ratified)
- 2026-07-05: S2401 P1 Cat A close (Chris "commit it" ratified)
- 2026-07-05: S2402 P2 Cat B close (Chris "commit it" ratified)
- 2026-07-05: S2403 P3 Cat C draft written this doc (post-6-parallel-Explore
  sweep + verifier-loop; 1 sub-agent conflict caught)
- 2026-07-05: Rigby SIGN cycle 1 CLOSED via dedicated fresh SIGN pin
  `pa-5096f5fc07754b18` (retired at cycle close); 29 folds landed pre-Chris-ratification;
  4-batch × 5-Q = 20-Q cadence EIGHTH-consecutive-tested application
- 2026-07-05: Chris ratification pending post-SIGN-cycle-1 close-card

**Draft SIGN cycle 1 complete at HEAD `8bc1b0c0`. Chris ratification pending
via close-card.**
