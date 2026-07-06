# Auth — Topic Reference (Group 2400 anchor)

> **Anchor context** (per S2499 xx99 Group 2400 canonical summary
> AU-D2 + AU-D7 recommendations). This doc consolidates the auth
> narrative surface across the platform. Four contract axes were
> audited under Research Group 2400 (Auth — Session Lifecycle +
> Permission Floor + Silent-401 Resolution) at HEAD `4e6c1ee8`
> (S2499 close). Runtime state may drift; see DOC_LIFECYCLE
> cross-link at bottom for how future sessions should supersede.

---

## What auth is (in one sentence)

The identity-attach + permission-floor + session-lifecycle +
frontend-caller contract mesh that gates ~1,864 `path()` patterns
+ 803 frontend consumer call-sites against 6 authentication
mechanisms (DRF Token + VIP demo + Fleet HMAC + 2 service tokens +
Django session).

## Canonical verdict from Group 2400 arc

**"ACCRETION with declared-but-unenforced contracts."** Mechanisms
generally work at file-precision in the sampled surfaces; the
*contract* — the promise that a mechanism means what its name
implies — is silently violated across all four contract axes
examined. See
[`docs/research/domains/auth/2499_auth_canonical_summary.md`](../research/domains/auth/2499_auth_canonical_summary.md)
§1 for the full framing.

## Four contract axes

### 1. Authentication Surface + Trust Boundaries (Cat A)

Reference audit:
[`docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md`](../research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md).

- **6 mechanisms** — DRF `TokenAuthentication` (~65
  `@token_auth_required` decorator uses at HEAD across 10 files);
  VIP demo (prompt-only injection; no runtime gate); Fleet HMAC
  (permissive fallback; downstream capability check); 2 service
  tokens (`PA_DB_HEALTH_RPC_TOKEN`, `PUBLIC_INTEL_TOKEN`); Django
  session (compatibility path).
- **Path lists** — ~108 PUBLIC_PATHS + STAFF_REQUIRED_PATHS +
  REVIEWER_BLOCKED_PATHS + REVIEWER_ALLOWED_PATHS in
  `core/auth_middleware.py`. 2 of 3 STAFF_REQUIRED_PATHS are
  phantom entries per Cat B F-B-HIGH-1 HEAD-verification.
- **Trust-boundary rate** — 14 gate mechanisms × 3 PRESENT + 2
  PARTIAL + 9 ABSENT smoke-test coverage (Cat A §14.5).
- **Known unsafe edges** — VIP demo prompt-only (F-VIP-1 ↔
  F-C-VIP-1 declared-fictional at Cat C); Fleet permissive
  fallback (F-BND-4); PURGE_SECRET hardcoded fallback (F-CRIT-1);
  WebSocket auth middleware DEAD in ASGI stack (F-WS-1); Session
  1171 503-fork zero smoke-test coverage (F-CRIT-2).

### 2. Authorization + Permission-Floor Uniformity (Cat B)

Reference audit:
[`docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md`](../research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md).

- **~1,864 `path()` patterns × permission floor cell** —
  ~80-90% ESTIMATE implicit-inheritance rate (F-B-CRIT-1). Whole-
  platform permission-floor uniformity CANNOT be observed without
  a registry.
- **F-B-CRIT-2 silent-401 SYSTEMIC as necessary-enabling downstream
  symptom** of F-B-CRIT-1 (BE-model ROOT CAUSE; Cat D delivered
  SYMPTOM scale evidence at 803 consumer call-sites).
- **21-loci permission-floor rate** — 10 WORKING + 6 PARTIAL + 4
  EXPERIMENTAL + 3 MED-HIGH drift + 1 DEAD carry-over (Cat B
  §14.5).
- **Cat B three-option decision space** — (a) uniform
  IsAuthenticated NOT recommended (blast radius) + (b) split
  read-write + client-side auth-check-on-write PRIMARY for
  REMEDIATION WINDOW + (c) per-endpoint permission registry
  PRIMARY for LONG-TERM GOVERNANCE.

### 3. Session Lifecycle + Logout Cleanup Contract (Cat C)

Reference audit:
[`docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md`](../research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md).

- **Token model** — DRF `authtoken` (no `expires_at` field); no
  refresh endpoint (F-C-REFRESH-1); implicit permanent-token
  contract absent password event.
- **VIPInvite two-timestamp lifecycle** — `token_expires_at` (72h;
  enforced) + `account_expires_at` (14d; **NOT enforced at
  runtime** — F-C-VIP-1 declared-fictional class).
- **15-surface storageKeys × logout-cleanup CONTRACT** — 1 CLEAN
  (`auth-storage` functional-null-state) + 3 PARTIAL (paStore
  syncUser + pipeline_dismissed + podcast_voice_profile) + 11
  NO-CLEANUP; declared cleanup rate 1/15 = 6.7% (F-C-STORE-1).
- **Backend Clear-Site-Data** — ZERO emission on logout at HEAD
  (F-C-CSD-1).
- **21-loci lifecycle-observability rate** — 5 WORKING + 5 PARTIAL
  + 11 DEAD (Cat C §14.3).
- **Cat C three-option decision space** — (α) silent-refresh + (β)
  explicit re-login (Cat C proposes as least-assumption default
  for xx99 evaluation) + (γ) hybrid.
- **F-C-VIP-1 risk-gate constraint** — Shipping any user-facing
  lifecycle change relying on expiry semantics without ALSO
  closing F-C-VIP-1 creates misleading safety signal; treat as
  prerequisite for any α/β/γ expiry-signal-bearing UX.

### 4. Frontend Integration + Silent-401 SYSTEMIC Resolution (Cat D)

Reference audit:
[`docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md`](../research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md).

- **803 total consumer call-sites at HEAD** — 57 direct
  `api.<verb>()` + 667 `useQuery`/`useMutation` React Query
  wrappers + 79 raw `fetch()` bypass. 724 interceptor-routed
  (90.2%); 79 bypass (9.8%); **~99% silent-swallow rate**.
- **Silent-401 handler** — `frontend/src/lib/api.ts:48-56` with
  whitelist substring `url.includes('/auth/') || url.includes('/login')`
  BRITTLE forward (F-D-WHITELIST-1); 0 typed `AxiosError` catches
  (F-D-ENVELOPE-1); 0 error boundaries anywhere (F-D-BOUNDARY-1).
- **Sidebar logout does NOT revoke backend token** —
  `frontend/src/components/layout/Sidebar.tsx:356` clears
  authStore + syncUser(null) via Zustand persist but does NOT call
  `authApi.logout()` (F-D-SIDEBAR-1 NEW HIGH FINDING beyond Cat C).
- **PA-chat 401 exposure** — `/pa/chat/`, `/pa/chat/status/`,
  `/pa/conversations/` endpoints do NOT match whitelist; 401
  mid-conversation = silent reject = agent-hang UX (F-D-PA-1 HIGH
  per Rigby Q10 fold).
- **Cat D typed-error-envelope three-option decision space** —
  (α) throw typed exceptions + (β) discriminated-union returns +
  (γ) React Query error callbacks + top-level `<ErrorBoundary>`.
  **Cat D proposes (γ) as PRIMARY DEFAULT** with Cat C β
  "explicit re-login" nested inside γ as UX policy (Rigby Q6
  fold — γ = mechanism, β = UX policy).
- **Cat D whitelist-replacement three-option decision space** —
  (α) explicit endpoint list registry + (β) 401-response-suppression
  header from backend + (γ) per-api-module `authHandling: 'default'
  | 'suppress_redirect'` string enum + telemetry on every
  `suppress_redirect` (Rigby Q7 fold).
- **Handler discipline** (Rigby Q9 fold) — MUST distinguish
  401/403 vs network/offline vs 5xx; copy MUST avoid time-based
  "expired" language until F-C-VIP-1 resolves (use "Sign-in
  required" / "Authentication required" preserving Cat C
  risk-gate).

## Silent-degrade-vs-explicit-failure ambiguity codification candidate

Playbook §20 codification candidate; two-trigger threshold MET at
Group 2400 close:

- **TRIGGER #1** — Cat C 92.9% silent-degrade class (13 of 14
  findings) on session-lifecycle plane.
- **TRIGGER #2** — Cat D 89.5% silent-degrade class (17 of 19
  findings; 2 non-silent-degrade findings both governance class:
  F-D-OWN-1 CODEOWNERS + F-D-OWN-2 CI test-harness) on
  401-handling plane.

**Scope-bounded codification (per Cat D Rigby Q5 fold + xx99 Rigby
SIGN Q3 fold):** promote to playbook v3 candidate focused on
**auth failure handling (401/403/refresh/logout) with explicit UX +
telemetry requirements** — NOT general silent-degrade-anywhere
codification. **Conditional promotion rule:** general codification
if a 3rd trigger appears in a non-auth plane (Groups 2500 API /
2600 PA / 1700 Observability).

## Post-arc Follow-On T-slot handoffs

- **T2 Group 2500 API (NEXT arc after Group 2400 close)** — CF-D1
  + CF-B1 + CF-C1 roll-up: refresh endpoint + logout envelope +
  Clear-Site-Data emission spec + typed-error-envelope (Cat D
  α/β/γ) + per-endpoint permission registry (Cat B c) design-prep.
- **T3 Group 2600 PA** — CF-D2 + CF-B2 + CF-C2 roll-up:
  workspace-context authz + `session_tool.retire` cascade on user
  logout + PA-chat 401 UX design + paStore field-list completeness.
- **T4 Group 1700 Observability umbrella roll-up** — CF-D3 + CF-B5
  + CF-C3 + Cat A CF-2: 503-fork asymmetry + login/logout event
  emit + silent-401 rate telemetry + `authHandling: 'suppress_redirect'`
  telemetry + smoke-test coverage per gate mechanism.
- **T5 Group 2300 Mobile** — CF-D4 + CF-C4 + Cat A CF-4: parallel
  silent-401 audit for mobile app + MobilePushToken.revoked_at
  cascade + 401-handling parity between web + mobile OR document
  divergence.
- **Group 2200 post-arc R6** — BLOCKING PREREQUISITE for Cat D
  option-γ (per CF-D5 Rigby Q18 fold): top-level `<ErrorBoundary>`
  framework establishment.
- **Group 1900 Governance** — CF-D6 + Cat A CF-5: KillSwitch
  attestation on typed-401 boundary preserved. No new work;
  boundary preservation only.

## P0 rank-1 co-equal remediation batch (14 items; tiered per Cat D Rigby Q15 fold — co-equal preserved)

**P0-A (platform-wide / whole-auth-surface blast radius):**
F-D-CALL-1 + F-D-BYPASS-1 + F-D-ENVELOPE-1 + F-D-BOUNDARY-1.

**P0-B (token lifecycle / security window):** F-D-SIDEBAR-1 +
F-C-REFRESH-1 + F-C-VIP-1 + F-C-CSD-1 + F-C-STORE-1.

**P0-C (endpoint-specific):** F-CRIT-1 + F-BND-4a + F-B-CRIT-1 +
F-B-CRIT-2 + F-D-WHITELIST-1.

Co-equal contract preserved per Cat A/B/C precedent; A/B/C tiers
surface blast-radius truth for implementation sequencing, not
priority downgrade.

## Key files

**Backend:**
- `core/auth_middleware.py` — UnifiedTokenAuthenticationMiddleware + `@token_auth_required` decorator + WebSocket middleware (DEAD)
- `core/auth_views.py` — login + logout + current_user views
- `core/auth_views_enhanced.py` — logout_enhanced_view (`@permission_classes([IsAuthenticated])`)
- `core/api_responses.py` — `APIResponseEnvelope` (backend 401 shape `{success: false, error: {code, message}}`)
- `core/services/fleet_auth_drf.py` — FleetSignatureAuthentication
- `core/vip_middleware.py` — VIP demo middleware (prompt-only)
- `core/models_vip_invite.py` — VIPInvite two-timestamp model

**Frontend:**
- `frontend/src/lib/api.ts` — sole `axios.create()` at `:13`; response interceptor `:42-62`; request interceptor `:27-40`; whitelist substring `:50`
- `frontend/src/stores/authStore.ts` — Zustand persist auth store; `logout()` at `:34-39`
- `frontend/src/App.tsx` — ProtectedRoute gate `:47-59`; 16 cockpit `<Navigate>` `:134-149` (NOT wrapped by ProtectedRoute)
- `frontend/src/components/layout/Sidebar.tsx:356` — logout onClick (does NOT call `authApi.logout()`)

## Ownership status (F-D-OWN-1 CODEOWNERS gap)

At Group 2400 close: CODEOWNERS file **ABSENT** at `.github/`,
root, `docs/` — Cat D F-D-OWN-1 HEAD-verified. Frontend
`api.ts` + `authStore.ts` owned de facto by Chris West per git log.
Cross-arc typed-error-envelope + whitelist-replacement ownership
UNASSIGNED at close. See CODEOWNERS at repo root for post-arc
declaration.

## DOC_LIFECYCLE cross-link

**Current state vs target state.**

- **Current state** (this doc): Reference summary at Group 2400
  close (HEAD `4e6c1ee8`). Consolidates Cat A/B/C/D findings +
  three-decision-space enumeration.
- **Target state**: Post-arc remediation lands via T2 Group 2500
  API + T3 Group 2600 PA + T4 Group 1700 Observability + Group
  2200 R6 error-boundary framework execution. As α/β/γ options
  ship, this doc's decision-space sections become historical;
  chosen option becomes canonical narrative.

**Supersession discipline** (per Cat D AU-D7 recommendation).
Future sessions supersede this doc as follows:
1. When Chris D-verdict on Cat B (a)/(b)/(c) lands → §Authorization
   section rewrites decision-space as chosen option + rationale.
2. When Chris D-verdict on Cat C (α)/(β)/(γ) lands → §Session
   Lifecycle section rewrites decision-space as chosen option.
3. When Chris D-verdict on Cat D α/β/γ × 2 lands → §Frontend
   Integration section rewrites decision-space as chosen option.
4. When each P0 batch item ships → §Post-arc T-slot handoff row
   updates to "SHIPPED" with PR link.
5. When docs/topics/session_lifecycle.md spawns per AU-C4
   (optional) → §Session Lifecycle contents move there; this
   doc cross-links.

**Runtime state may drift.** For source-of-truth counts on
`@token_auth_required` uses + PUBLIC_PATHS + 803 consumer
call-sites, run `python manage.py verify_doc_claims --only-drift`.
For anchor counts, see `PLATFORM_INVENTORY.md` (regenerable).

---

**Anchor status:** `status: active` at Group 2400 close 2026-07-05.
Companion research: `docs/research/domains/auth/2499_auth_canonical_summary.md`.
