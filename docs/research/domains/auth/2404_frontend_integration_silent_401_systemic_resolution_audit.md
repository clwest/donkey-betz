---
title: "Frontend Integration + Silent-401 SYSTEMIC Resolution — S2404 P4 Cat D Child Audit"
status: active
authority: research
version: v1
session_added: 2404
last_verified: 2026-07-05
domain_slug: auth
research_group: 2400
child_slot: P4
companion_anchors:
  - CLAUDE.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/domains/auth/2400_auth_domain_scoping.md
  - docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md
  - docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md
  - docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md
  - docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md
  - docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md
  - docs/research/domains/frontend/2204_frontend_session_state_persistence_discipline_audit.md
  - docs/research/domains/frontend/2299_frontend_canonical_summary.md
related:
  - docs/research/domains/frontend/2202_frontend_client_state_data_flow_discipline_audit.md
  - docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md
delegates_to:
  - docs/research/domains/auth/2499_auth_canonical_summary.md  # future xx99
head_commit_before: 31398008
head_commit_after: TBD (S2404 merge PR TBD)
arc_pin: pa-6279ead1714c4630  # PRESERVED per playbook §16 arc-standard behavior
sign_pin: pa-015448e962ad4038  # RETIRED at S2404 SIGN cycle 1 close 2026-07-05 via `session_tool.retire` (updated_count=6, retired=true, previously_active=true — FIFTEENTH consecutive dedicated fresh SIGN pin retirement in Research OS after 10 xx99 + 1 parent-scoping + Cat A + Cat B + Cat C + this cycle)
verifier_loop: |
  Parent-Claude verifier-loop pre-Rigby-SIGN caught 3 sub-agent
  conflicts pre-draft (playbook §14 discipline; extends S2403
  precedent that caught VIP invite exchange + Django logout
  HEAD-verification conflicts):

  1. **Decorator count drift** — Agent 2 reported 65 uses / 10 files
     for `@token_auth_required`; Agent 3 reported 9 files; Cat A
     S2401 baseline was "68 uses / 9 view files." Parent-Claude
     grep at HEAD `31398008`: **65 occurrences across 10 files**
     (auth_middleware.py:1 is the decorator DEFINITION site;
     applied to views = 64 uses across 9 view files). Cat A count
     has drifted DOWN by 3-4 uses since S2401 close (likely S2101–
     S2402 DRF permission_class migrations). Applied CANONICAL:
     "65 occurrences across 10 files at HEAD" throughout §5 + §14.
  2. **Call-site denominator ambiguity** — Agent 3 reported 913
     direct `api.<verb>()` occurrences + 97 async invocations =
     ~1,010; Agent 4 reported 667 `useQuery`/`useMutation`;
     Agent 6 reported 478 total invocations. Parent-Claude grep:
     **913 direct `api.<verb>()` across 21 files** (of which
     api.ts itself has 856 = API-METHOD-DEFINITIONS, not consumer
     call-sites; net consumer-side direct = 57 across 20 files)
     + **667 useQuery/useMutation across 74 files** + **79 raw
     fetch() across 31 files** = **803 total consumer call-sites
     at HEAD `31398008`**. S2203 A3 ~630 baseline was
     interceptor-routed-only; consumer-total is larger. Applied
     CANONICAL: "803 total consumer call-sites; 724 route through
     api.ts interceptor; 79 bypass entirely (9.8%)" throughout
     §6 + §14 + §17.
  3. **Fetch-bypass accounting** — Agent 2 initially reported
     "zero wrapper duplication + single point of auth enforcement";
     Agent 3 + Agent 6 both surfaced 79 raw `fetch()` calls that
     bypass the interceptor entirely. Parent-Claude grep confirms
     **79 raw fetch() across 31 files at HEAD `31398008`**. Applied
     CANONICAL: "wrapper-duplicate ZERO (single axios instance);
     interceptor-bypass NON-ZERO (79 raw fetch)" throughout §5 +
     §17 to preserve S2203 §14 F3 Q14 discipline. This is a Cat D
     NEW-EVIDENCE finding beyond S2203 baseline.

  Verifier-loop also HEAD-verified 6 Cat A/B/C findings STILL-LIVE
  (F-DEC-1 drift-down but CONFIRMED-STILL-LIVE; F-WS-1 CONFIRMED;
  F-B-CRIT-2 silent-401 SYSTEMIC CONFIRMED; F-C-VIP-1 CONFIRMED;
  F-C-CSD-1 CONFIRMED zero Clear-Site-Data emission; F-C-COCKPIT-1
  CONFIRMED-STILL-LIVE at `frontend/src/App.tsx:134-149`).

  Verifier-loop also HEAD-verified 4 NEW evidence points beyond
  Cat A/B/C: (a) Sidebar logout at `frontend/src/components/layout/
  Sidebar.tsx:356` does NOT call `authApi.logout()` — clears
  authStore only, backend token never revoked via sidebar path
  (NEW HIGH FINDING F-D-SIDEBAR-1); (b) 79 raw fetch() bypass
  interceptor (F-D-BYPASS-1); (c) zero `AxiosError` typed catches
  across whole frontend (F-D-ENVELOPE-1); (d) CODEOWNERS file
  missing at `.github/`, root, and `docs/` (F-D-OWN-1 confirms
  Cat A/B/C ownership gap thesis extends to frontend integration
  surface).
owner: claude (S2404 draft; Rigby SIGN cycle 1 pending)
---

# S2404 P4 Cat D — Frontend Integration + Silent-401 SYSTEMIC Resolution Audit

> **Scope reminder (from S2400 §3.D).** This audit enumerates the
> **frontend surface of the auth contract**: `frontend/src/lib/api.ts`
> silent-401 handler + whitelist substring behavior + ~803 total
> consumer call-site blast radius (extends S2203 A3 ~630 baseline)
> + typed error envelope design candidates + error-boundary
> integration coordination. Executes T1 cross-arc handoff readiness
> per S2299 §8.2 4-axis bundle owed to Group 2400 Auth (silent-401
> resolution + logout cleanup + session lifecycle model +
> permission-floor uniformity). Re-verifies Cat A + Cat B + Cat C
> findings at HEAD `31398008`.
>
> **Anti-scope preserved** (per S2400 §3.5 + §7.1 leak-vector
> guardrails). This audit does NOT: (a) author the typed-error
> envelope ADR; (b) author the whitelist-replacement ADR; (c) fix
> any finding (all findings graduate to T-slot post-arc queue at
> S2499 xx99 close); (d) extend into MFA/OAuth/SSO framework
> additions (Anti-scope #6 preserved); (e) extend into mobile app
> auth (Anti-scope #4 preserved, Group 2300); (f) re-scope
> session-model beyond Cat C's α/β/γ recommendation lean.
>
> **Two-sided framing.** This is the FE-symptom side of the
> silent-401 SYSTEMIC contract. The BE-model side (F-B-CRIT-1
> permission-floor implicit-inheritance ROOT CAUSE) is owned by
> Cat B; Cat D consumes it and audits caller-side symptom.
> Preserves S2203 §14 F3 + S2204 §19.1 R1 two-sided contract.

---

## 1. Executive Summary

**Domain in one paragraph.** The frontend integration surface at
HEAD `31398008` is a **single centralized axios instance**
(`frontend/src/lib/api.ts:13`) with request + response
interceptors, feeding **803 consumer call-sites** across the whole
frontend. The response interceptor (`api.ts:42-62`) is the sole
401 handler; it applies a **whitelist substring rule** (`url.includes('/auth/') || url.includes('/login')`)
to decide whether to force logout + redirect (~2-5 call-sites
match) versus silently reject with `console.warn` (~798+
call-sites — the SYSTEMIC silent-401 pattern per S2203 §14 F3).
Zero error boundaries anywhere in the frontend, zero typed
`AxiosError` catches, zero `noAuthRedirect` flag adoption. Sidebar
logout onClick (`Sidebar.tsx:356`) calls `authStore.logout()` +
`syncUser(null)` but does **NOT** invoke `authApi.logout()` —
backend token is never revoked via sidebar path (NEW HIGH FINDING
F-D-SIDEBAR-1 beyond Cat C). 79 raw `fetch()` calls across 31
files bypass the interceptor entirely (F-D-BYPASS-1). CODEOWNERS
file absent (F-D-OWN-1).

**Biggest gaps.** (1) **F-D-CALL-1 HIGH**: 803 consumer
call-sites, ~99% (798+) silently swallow 401 with only
`console.warn` — the S2203 §14 F3 SYSTEMIC pattern extends beyond
its ~630 baseline. (2) **F-D-BYPASS-1 HIGH**: 79 raw fetch() calls
(~9.8% of consumer sites) bypass the interceptor entirely — no
token attach, no 401 catch. (3) **F-D-SIDEBAR-1 HIGH**: Sidebar
logout does not revoke backend token (`authApi.logout()` never
called); Cat C F-C-STORE-1 6.7% cleanup rate is companion symptom.
(4) **F-D-WHITELIST-1 MED (S2203 §14 F3.5 extension)**: substring
`/auth/` + `/login` is BRITTLE; zero false-positives at HEAD but
pattern scales badly with future auth-endpoint additions.
(5) **F-D-ENVELOPE-1 HIGH**: zero typed `AxiosError` catches
across whole frontend; typed-error-envelope adoption is greenfield.

**Biggest strengths.** (1) **Single axios instance** (api.ts:13)
— zero wrapper duplication at the axios layer (single point of
enforcement OPPORTUNITY). (2) **Existing `InternalAxiosRequestConfig`
extension** at api.ts:4-8 (Session 968 metadata pattern) —
non-breaking extension point ready for `noAuthRedirect?: boolean`
option (γ). (3) **Zustand persist middleware correctly clears
authStore on logout()** — 1 of 15 surfaces (Cat C §14.2 F-C-STORE-1
CLEAN row) works as declared. (4) **ProtectedRoute gate** at
`frontend/src/App.tsx:47-59` correctly redirects unauthenticated
users; wraps top-level route tree (S2201 §14 pattern preserved
STILL-LIVE at HEAD). (5) **React Query is installed +
widely-adopted** (667 `useQuery`/`useMutation` occurrences across
74 files) — option (γ) React-Query error-callback path has
existing infrastructure, unlike option (α) exception hierarchy or
option (β) discriminated-union which are greenfield refactors.

**What should be researched next.** (a) Backend must decide α/β/γ
typed-error-envelope + whitelist-replacement design (§19.1 three-
option decision space for each). (b) F-C-VIP-1 risk-gate must
resolve BEFORE any α/β/γ ships (Cat C constraint preserved).
(c) Error-boundary framework (S2299 §8.3 R6) must land jointly
with option-γ adoption. (d) CODEOWNERS declaration (F-D-OWN-1)
should land during T1 execution, not deferred. (e) Post-arc
smoke-test authoring for silent-401 acceptance criteria per
§14.5 rate table (extends Cat A/B/C §19.4 recommendations to
xx99 anchor-update).

**Runtime target.** Cat D closes S2404 P4 as fourth-of-four
child audits under Group 2400 Auth arc pin `pa-6279ead1714c4630`
(PRESERVED per playbook §16). Next: S2499 xx99 canonical summary
consolidates all four categories + Chris D-verdict on Cat B
(a)/(b)/(c) + Cat C (α)/(β)/(γ) + Cat D α/β/γ × 2 (envelope +
whitelist replacement).

---

## 2. Domain Purpose

**Central question the audit answers** (per S2400 §3.D):
*Does the frontend integration surface expose auth failures as
first-class typed errors observable at every gated call site, or
does the "silent-401 SYSTEMIC" + "brittle whitelist" pattern
(S2203 §14 F3 F3.5) require redesign at the api.ts layer +
cross-arc coordination with error-boundary framework +
typed-error-envelope adoption?*

**Answer at HEAD `31398008`.** **The frontend integration surface
does NOT expose auth failures as first-class typed errors.**
The `api.ts:48-56` silent-401 handler intercepts all 401 responses
and applies a whitelist substring rule that force-logout-redirects
only ~2-5 auth endpoints; the remaining ~798+ consumer call-sites
receive `Promise.reject(error)` with untyped Axios `error` object
and only `console.warn` telemetry. Zero call-sites explicitly type
+ catch `AxiosError` (grep verified at HEAD: 0 matches for
`AxiosError|axios.isAxiosError` across `frontend/src/`). React
Query is installed and widely adopted (667 hook occurrences) but
no `useQuery<TData, TError>` generic populates a TError type at
HEAD, and no `QueryClient` default `onError` handler discriminates
401 from 500 from business errors. **Redesign at api.ts layer +
cross-arc coordination with error-boundary framework +
typed-error-envelope adoption IS required.** This audit enumerates
the three-option design space for each; ADR authoring is post-arc
per S2400 anti-scope #5.

**Acceptance criteria (from S2400 §5).** Cat D partially advances
two acceptance criteria without closing either:

| Criterion | Pre-Cat-D | Post-Cat-D expected | Gap |
|---|---|---|---|
| **#1 Permission-floor observability** | S2203 A3 sampled 20 endpoints, ~40% untraced; S2402 F-B-CRIT-1 estimated ~80-90% implicit-inheritance rate | 803 consumer call-sites enumerated by inheritance-path (57 direct api + 667 hook-wrapped + 79 raw fetch); silent-401 rate ~99% CONFIRMED at HEAD | Gap closes IF Cat D α/β/γ envelope ships (post-arc). If γ centralized, observable via QueryClient telemetry only. |
| **#2 Failure surfacing** | ~99% silent-swallow; no typed error envelope; console.warn only on non-auth 401s | Three-option decision-space enumerated; option-γ has existing RQ infra; α/β are greenfield refactors; recommendation lean surfaced | Gap closes IF option lands post-arc; deferred to xx99 D-verdict + implementation T-slot. |

**Cat D does NOT close either criterion in-arc.** Post-arc
T-slot (rank-1 co-equal batch alongside Cat A F-CRIT-1 + Cat B
F-B-CRIT-1 + Cat C F-C-VIP-1) is the delivery vehicle.

### 2.1 Cat D closes vs defers (Rigby SIGN Q14 fold — 2026-07-05)

Explicit tabulation so the acceptance-criteria delta is
unambiguous for xx99 consumption:

| Category | Item |
|---|---|
| **Closes (this arc)** | 803-scale consumer call-site surface quantification (57 direct + 667 hook + 79 raw fetch) |
| **Closes (this arc)** | 79 raw fetch bypass inventory (F-D-BYPASS-1) |
| **Closes (this arc)** | Sidebar-logout-does-not-revoke-backend-token gap confirmation (F-D-SIDEBAR-1) |
| **Closes (this arc)** | Typed-error-envelope + whitelist-replacement decision spaces (α/β/γ × 2 enumerated with leans) |
| **Closes (this arc)** | F-C-VIP-1 risk-gate preservation as UX-copy constraint (Rigby Q9 fold) |
| **Closes (this arc)** | Q20 fold TRIGGER #2 codification candidate confirmation |
| **Closes (this arc)** | Cat A/B/C findings STILL-LIVE re-verification at HEAD `31398008` |
| **Defers (post-arc T-slot)** | Envelope adoption implementation (γ mechanism + β UX policy) |
| **Defers (post-arc T-slot)** | Error-boundary framework establishment (S2299 §8.3 R6 execution) |
| **Defers (post-arc T-slot)** | Whitelist replacement implementation |
| **Defers (post-arc T-slot)** | Backend logout envelope + Clear-Site-Data emission |
| **Defers (post-arc T-slot)** | Refresh-endpoint discipline (F-C-REFRESH-1) |
| **Defers (post-arc T-slot)** | Sidebar backend-revoke fix (F-D-SIDEBAR-1 single-line fix) |
| **Defers (post-arc T-slot)** | CI test-harness + CODEOWNERS declaration wiring (F-D-OWN-1 + F-D-OWN-2) |
| **Defers (post-arc T-slot)** | 79-raw-fetch per-site migration classification |

---

## 3. Canonical Entry Points

All file:line HEAD-verified at `31398008`.

| Entry point | File:line | Role |
|---|---|---|
| **axios instance creation** | `frontend/src/lib/api.ts:13` | Sole `axios.create({ baseURL, headers, timeout: 90000, withCredentials: true })` in whole frontend (grep verified: 1 instance) |
| **`InternalAxiosRequestConfig` extension** | `frontend/src/lib/api.ts:4-8` | Session 968 metadata pattern; existing extension point for future flags (e.g., `noAuthRedirect?: boolean`) |
| **request interceptor (token attach)** | `frontend/src/lib/api.ts:27-40` | Reads token from `useAuthStore.getState().token` at `:29`; attaches `Authorization: Token ${token}` header at `:35`; header omitted if token is null |
| **response interceptor (401 handler)** | `frontend/src/lib/api.ts:42-62` | Sole 401 handler in frontend; whitelist substring check at `:50`; force-logout-redirect at `:53-56`; silent `console.warn` at `:58` for non-auth 401 |
| **whitelist substring rule** | `frontend/src/lib/api.ts:50` | `const isAuthEndpoint = url.includes('/auth/') || url.includes('/login')` — S2203 §14 F3.5 BRITTLE |
| **`authApi` group** | `frontend/src/lib/api.ts:73-79` | 4 methods: `login()`, `logout()`, `getUser()`, `validateToken()` |
| **`authStore` (Zustand + persist)** | `frontend/src/stores/authStore.ts:20-52` | Store with `token`, `user`, `isAuthenticated` + `login()`, `logout()`, `setUser()`; persist name `auth-storage` |
| **`authStore.logout()`** | `frontend/src/stores/authStore.ts:34-39` | Sets `token: null, user: null, isAuthenticated: false`; Zustand persist writes null-record to localStorage `auth-storage` key |
| **`ProtectedRoute` gate** | `frontend/src/App.tsx:47-59` | Reads `isAuthenticated` from authStore; if false → `<Navigate to="/login" replace />`; syncs `paStore.syncUser(user?.id ?? null)` on every render |
| **Sidebar logout onClick** | `frontend/src/components/layout/Sidebar.tsx:356` | `onClick={() => { setUserMenuOpen(false); syncUser(null); logout() }}` — DOES NOT call `authApi.logout()` (F-D-SIDEBAR-1 NEW HIGH FINDING) |
| **Backend basic logout** | `core/auth_views.py:84-94` | `logout_view` — no permission decorator; silent-200 on unauth (Cat C F-C-LOGOUT-1) |
| **Backend enhanced logout** | `core/auth_views_enhanced.py:539-556` | `logout_enhanced_view` — `@permission_classes([IsAuthenticated])`; no `Clear-Site-Data` header (Cat C F-C-CSD-1) |
| **Backend 401 envelope** | `core/api_responses.py:143-149` | `APIResponseEnvelope.unauthorized(message)` returns `{ "success": false, "error": { "code": "authentication_required", "message": ... } }` |
| **cockpit two-stage redirects** | `frontend/src/App.tsx:134-149` | 16 `<Navigate>` entries NOT wrapped by ProtectedRoute (Cat C F-C-COCKPIT-1 CONFIRMED-STILL-LIVE at HEAD) |
| **Raw fetch bypass sites** | 79 sites across 31 files | Bypass interceptor entirely — no token attach, no 401 catch. Notable: `LiveMetricsDashboard.tsx` uses raw `fetch('/api/platform/live-metrics/', {credentials:'include'})` |

---

## 4. Major Models

| Model | File:line | Cat D-relevant fields | HEAD status |
|---|---|---|---|
| **DRF `Token`** (upstream) | `rest_framework.authtoken.models.Token` (venv) | `key`, `user` (OneToOne), `created` (auto_now_add). **NO `expires_at` field.** No local subclass exists (grep verified: 0 matches for `class Token` or `AbstractToken` inheritance in `core/models_*.py`). | CONFIRMED-STILL-LIVE-AT-HEAD-31398008. Implicit contract: token permanent absent password event. F-C-REFRESH-1 downstream. |
| **`VIPInvite`** two-timestamp lifecycle | `core/models_vip_invite.py:71-72, 96-103` | `token_expires_at` (72h default) + `account_expires_at` (14d default); `is_valid` at `:96-103` checks ONLY `token_expires_at` | CONFIRMED-STILL-LIVE-AT-HEAD-31398008. F-C-VIP-1 risk-gate for α/β/γ envelope UX. |
| **`authStore`** (Zustand persist) | `frontend/src/stores/authStore.ts:11-18` | `AuthState` interface: `token: string \| null` + `user: User \| null` + `isAuthenticated: boolean` + 3 actions (`login`, `logout`, `setUser`). **NO error/errorMessage/errorCode field.** | ZERO DRIFT from Cat C §14.2 declaration. No typed error channel; option-α/β adoption would require adding error field. |
| **`User`** (frontend interface) | `frontend/src/stores/authStore.ts:4-9` | `id: number`, `username`, `email`, `platform_role?: string` | ZERO DRIFT. Sparse subset of backend user model; sufficient for auth gating. |
| **Backend `APIResponseEnvelope`** | `core/api_responses.py:60-149` | `success` (bool) + `error: { code, message }` + optional `data`. `unauthorized(message)` returns 401 with `error_code: 'authentication_required'`. | CONFIRMED-STILL-LIVE-AT-HEAD-31398008. Envelope EXISTS at backend but frontend does NOT type-catch it. |

**No new models introduced by Cat D scope.** All findings target
existing model behavior + missing frontend-side typing.

---

## 5. Major Services

| Service | File:line | Role | HEAD state |
|---|---|---|---|
| **axios `api` singleton** | `frontend/src/lib/api.ts:13-24` | `axios.create({ baseURL: API_BASE_URL, headers: {'Content-Type': 'application/json'}, timeout: 90000, withCredentials: true })`. Sole instance in frontend (grep verified: 1 `axios.create(` match). | WORKING (mechanism-level). Zero wrapper duplication. |
| **request interceptor** | `frontend/src/lib/api.ts:27-40` | Reads token from `useAuthStore.getState().token`; attaches `Authorization: Token ${token}` if truthy; omits header entirely if null. Debug logging gated on `NODE_ENV === 'development' \|\| config.url?.includes('/platform/')`. | WORKING. Correct conditional attach; no `Token null` leakage. |
| **response interceptor** | `frontend/src/lib/api.ts:42-62` | Passes through 2xx untouched; on 401, checks whitelist substring; if match → `useAuthStore.getState().logout()` + `window.location.href = '/login'`; else → `console.warn` only. Always `Promise.reject(error)` regardless. No retry. | PARTIAL. Mechanism works; **contract semantics broken** — 803 consumer call-sites cannot distinguish 401 from network error from 500 without inspecting `error.response?.status` themselves. |
| **`useAuthStore` (Zustand + persist)** | `frontend/src/stores/authStore.ts:20-52` | `create<AuthState>()(persist(setter, { name: 'auth-storage', partialize: subset }))`. Actions mutate token/user/isAuthenticated in-place. | WORKING. Zustand persist correctly writes cleared state on `logout()`. |
| **`authApi` group** | `frontend/src/lib/api.ts:73-79` | 4 methods invoking `/v1/auth/login/`, `/v1/auth/logout/`, `/v1/auth/user/`, `/v1/auth/validate-token/`. All match whitelist substring `/auth/`. | WORKING. |
| **`ProtectedRoute` component** | `frontend/src/App.tsx:47-59` | Reads `isAuthenticated` from authStore; syncs `paStore.syncUser(user?.id ?? null)` on every render; if not authenticated → `<Navigate to="/login" replace />` | WORKING (gate mechanism); PARTIAL (cockpit 16 routes bypass — F-C-COCKPIT-1) |
| **`@token_auth_required` decorator** | `core/auth_middleware.py:36-81` (definition) | Alternate token-auth path used by 9 view files. Catches `Token.DoesNotExist` only; infrastructure errors surface as 500 (no 503-fork). Cat A F-DEC-1. | HEAD-verified count: **65 occurrences across 10 files** (down from Cat A "68 uses / 9 view files" baseline — S2101–S2402 DRF permission_class migrations account for drift-down). Applied uses = 64 across 9 view files. |
| **`UnifiedTokenAuthenticationMiddleware`** | `core/auth_middleware.py` (middleware chain) | Main HTTP token-auth path with Session 1171 503-fork for infrastructure errors. Returns `api_unauthorized("Authentication required")` on 401. | WORKING at HTTP path; asymmetric with WS + decorator paths (F-DEC-1 + F-WS-1). |
| **`WebSocketAuthenticationMiddleware`** | `core/auth_middleware.py:739-822` | Cat A F-WS-1 flagged as DEAD CODE (not installed in ASGI stack). `validate_websocket_token` at `:807-822` silent-swallows all exceptions to `None`. | CONFIRMED-STILL-LIVE-AT-HEAD-31398008. WS auth silent-swallow companion to frontend silent-401. |

**Wrapper-duplicate accounting (S2203 §14 F3 Q14).** At HEAD:
- axios instances: **1** (api.ts:13)
- `cockpitApi.ts`: re-uses shared `api` instance; NO independent interceptor
- `apiClient.ts`: re-uses shared `api` with `X-UI-Scope` header extension; NO independent interceptor
- Raw `fetch(` calls: **79 across 31 files** (bypass interceptor entirely — F-D-BYPASS-1)
- Total interceptor-routed sites: 803 − 79 = **724 consumer call-sites route through api.ts:48-56**

---

## 6. Major APIs and Interfaces

**Consumer call-site inventory at HEAD `31398008`** (verifier-loop
canonical figures):

| Layer | Count | Denominator context |
|---|---|---|
| Direct `api.<verb>()` occurrences in `frontend/src/` | 913 across 21 files | 856 are API-METHOD-DEFINITIONS inside `api.ts` (line 856 count = ~93 exported groups × avg-9-methods); 57 are direct consumer call-sites across 20 non-api.ts files |
| `useQuery`/`useMutation` occurrences | 667 across 74 files | React Query wrapper layer (`@tanstack/react-query` present in `frontend/package.json`) |
| Raw `fetch(` occurrences | 79 across 31 files | Bypass interceptor (F-D-BYPASS-1) |
| **Total consumer call-sites** | **803** | 57 direct + 667 hook-wrapped + 79 raw fetch |
| Routes through api.ts interceptor | 724 | 803 − 79 fetch bypass; 90.2% interceptor coverage |
| Bypass api.ts interceptor entirely | 79 | 9.8% of consumer surface |
| Typed `AxiosError` catches | **0** | Grep verified zero `AxiosError \| axios.isAxiosError` matches |
| Error-boundary components | **0** | Grep verified zero `ErrorBoundary \| componentDidCatch \| getDerivedStateFromError` matches |
| `noAuthRedirect` flag adoption | **0** | Option-γ flag pattern is greenfield |

**Money-path + governance-path classification (extends S2203 §3
per S2400 §3.D output (b) CRITICAL classification):**

| Path class | Endpoint-line hits in api.ts | Notable groups | Silent-401 exposure |
|---|---|---|---|
| **Money-path (CRITICAL)** | 40 endpoint-line hits + 1,182 keyword mentions across 109 files | `bettingApi` (line 1229), `revenueApi` (line 4182), `incomeBuilderApi` (line 590), `distributionApi` (line 847), `portfolioApi` (line 1575) | 10 write-path endpoints (place-bet, log-wager, settle-wager, cancel-wager, quick-pick, income-plan create/execute, revenue-record). None match whitelist. 401 → silent reject; component MUST handle. |
| **Governance-path (CRITICAL)** | 104 endpoint-line hits + 1,053 keyword mentions across 54 files | `decisionsApi` (line 550), `dreamsApi` (line 217), `advisorsApi` (line 2166), `platformApi` (line 3257) | 9 write-path endpoints (decisions approve/reject/promote, dreams react/rate/trigger, advisors consult, create-initiative-from-decision). None match whitelist. 401 → silent reject. |
| **PA-path (SIGNIFICANT)** | ~15 endpoints under `assistantApi` (line 1147) | `paChat`, `paChatStatus`, `paContext`, `paConversations` | 3+ endpoints (`/pa/chat/`, `/pa/chat/status/`, `/pa/conversations/`) don't match whitelist. 401 mid-conversation → silent reject; PA UI enters undefined state (NEW EVIDENCE — extends Cat C CF-C2 to Cat D). |
| **Read-path aggregate** | 588 GET calls | Cross-cutting | Silent reject on 401; stale data risk. |
| **Write-path aggregate** | 362 POST/PUT/PATCH/DELETE | Cross-cutting | Silent reject on 401; write-through-anonymous risk if BE gate soft. |

**Whitelist false-positive audit (S2203 §14 F3.5).** Zero
false-positives at HEAD. All 5 endpoints matching `/auth/`
substring (`/v1/auth/login/`, `/v1/auth/logout/`, `/v1/auth/user/`,
`/v1/auth/validate-token/`, `/v1/auth/change-password/` at api.ts:1077)
are legitimate auth endpoints. No non-auth endpoints contain the
substrings. **BRITTLE forward — pattern scales badly with future
auth-endpoint additions or any endpoint containing `/authorized-*`
or `/login-events/` shape.**

**Miss-set analysis (endpoints that VALIDATE token but DON'T match
whitelist).** These are NOT auth-endpoint miss-sets per se; they
are the general SYSTEMIC surface — every gated endpoint returns
401 on token expiry, and none but the 5 auth endpoints trigger
force-logout. This is the S2203 §14 F3 SYSTEMIC finding at
HEAD-verified 803-call-site scale.

---

## 7. Runtime Flows

**Flow A: Successful authenticated request (positive path).**

```
component → useQuery/useMutation → api.<verb>(url, data)
  → axios request interceptor (api.ts:27-40)
    → reads token from useAuthStore.getState().token
    → attaches Authorization: Token ${token} header
  → HTTP request to backend
  → backend UnifiedTokenAuthenticationMiddleware validates token
    → hard runtime gate; token valid → user attached to request
  → view/serializer processes
  → 200 response
  → axios response interceptor pass-through (api.ts:44)
  → React Query success cache
  → component receives data
```

**Flow B: 401 on auth endpoint (whitelist match; force-logout).**

```
component → authApi.logout() or authApi.getUser() → api.get('/v1/auth/user/')
  → request interceptor attaches token (may be stale)
  → backend middleware returns 401
    → { "success": false, "error": { "code": "authentication_required", "message": "..." } }
  → response interceptor (api.ts:42-62)
    → status === 401 ✓
    → url = '/v1/auth/user/'
    → isAuthEndpoint = url.includes('/auth/') ✓
    → useAuthStore.getState().logout()
      → set({ token: null, user: null, isAuthenticated: false })
      → Zustand persist writes { token:null, user:null, isAuthenticated:false } to localStorage['auth-storage']
    → window.location.href = '/login'
      → full page reload
      → main.tsx bootstraps
      → App.tsx renders ProtectedRoute
      → isAuthenticated === false
      → <Navigate to="/login" replace />
      → login page renders
```

**Flow C: 401 on non-auth endpoint (SILENT reject — SYSTEMIC).**

```
component → useQuery/useMutation → api.get('/v1/agents/list/') [or any of 798+ non-auth endpoints]
  → request interceptor attaches token (may be stale)
  → backend middleware returns 401
    → { "success": false, "error": { "code": "authentication_required", "message": "..." } }
  → response interceptor (api.ts:42-62)
    → status === 401 ✓
    → url = '/v1/agents/list/'
    → isAuthEndpoint = url.includes('/auth/') || url.includes('/login') = false
    → SKIP force-logout branch
    → console.warn('Authentication required for:', '/v1/agents/list/')
    → Promise.reject(error)
  → React Query onError (if wired — RARE)
    → typically UNWIRED; error propagates as promise rejection
  → component
    → try/catch (if present) OR
    → useQuery { error } destructure (untyped)
    → NO redirect
    → NO state clear
    → stale UI persists; user may not notice
```

**Flow D: Sidebar logout (F-D-SIDEBAR-1 NEW HIGH FINDING).**

```
Sidebar user clicks Logout
  → onClick handler at Sidebar.tsx:356
  → setUserMenuOpen(false)
  → syncUser(null)  // paStore sync — clears PA conversations
  → logout()         // authStore.logout()
    → set({ token: null, user: null, isAuthenticated: false })
    → Zustand persist writes cleared state to localStorage
  → NO authApi.logout() call
  → NO HTTP request to /v1/auth/logout/
  → BACKEND TOKEN NEVER REVOKED
  → If user re-logs-in same browser session, may still have valid token in DB
  → If token leaked (XSS, malicious extension), it remains valid on backend
  → User is redirected to /login on next protected-route navigation (via ProtectedRoute)
```

**F-D-SIDEBAR-1 HIGH.** Sidebar logout onClick at
`frontend/src/components/layout/Sidebar.tsx:356` does NOT invoke
`authApi.logout()` (i.e., HTTP `POST /v1/auth/logout/`). Backend
DRF token is never `delete()`ed via sidebar path. Combined with
Cat A F-DEC-1 no `token_expires_at` and Cat C F-C-REFRESH-1 no
refresh endpoint, this creates an ATTACKER-VALID window: any
leaked token remains valid indefinitely (until password change or
DB-side cleanup). Frontend-only clear is insufficient for the
"logout-means-token-revoked" implicit contract. **This is NEW
evidence beyond Cat C** — Cat C §7 documented "logout endpoint
behavior" but did not audit **which client-side surfaces call
which logout endpoint variant**.

**Flow E: Raw fetch bypass (F-D-BYPASS-1 NEW HIGH FINDING).**

```
component → const response = await fetch('/api/platform/live-metrics/', { credentials: 'include' })
  → HTTP request to backend (no Authorization: Token header)
  → backend middleware falls back to session-cookie auth via withCredentials
  → session valid → 200 (relies on cookie); OR session invalid → 401
  → No axios interceptor triggered
  → NO force-logout on 401 even if endpoint is `/v1/auth/*`
  → component MUST manually catch + handle
```

79 raw fetch calls across 31 files. Notable examples:
- `frontend/src/components/platform/LiveMetricsDashboard.tsx:94`
  — `fetch('/api/platform/live-metrics/', {credentials: 'include'})`
- `frontend/src/pages/BlogViewerPage.tsx` (2 fetch sites)
- `frontend/src/pages/DemoHomePage.tsx` (via LiveMetricsDashboard usage)
- `frontend/src/hooks/usePageTracking.ts:1` (1 fetch site)

Bypass rate: 79 / 803 = **9.8% of consumer call-sites bypass
interceptor entirely.**

---

## 8. Data Ownership and Lifecycle

**Token lifecycle at HEAD `31398008`.**

| Stage | Owner | Surface | Contract |
|---|---|---|---|
| Issuance | Backend `login_view` (`core/auth_views.py:65-75`) | `POST /v1/auth/login/` returns `{ token, user }` | DRF `Token.objects.get_or_create(user=user)` — reuses existing token if present, else creates. No expiry field. |
| Persistence (backend) | `rest_framework.authtoken.models.Token` | PostgreSQL `authtoken_token` table | No `expires_at` column. Token permanent absent explicit revoke. |
| Persistence (frontend) | Zustand `authStore` + persist middleware | localStorage `auth-storage` key | Serialized `{ token, user, isAuthenticated }` JSON blob. Zustand rehydrates on page load. |
| Attach to request | `frontend/src/lib/api.ts:27-40` request interceptor | Every axios request routes through this | `Authorization: Token ${token}` header on non-null token. |
| Refresh | **N/A — no refresh endpoint** (F-C-REFRESH-1 CONFIRMED-STILL-LIVE) | — | Token permanent absent password event. |
| Revoke via API | Backend `logout_view` at `core/auth_views.py:84-94` (basic; no permission decorator) OR `logout_enhanced_view` at `core/auth_views_enhanced.py:539-556` (`@permission_classes([IsAuthenticated])`) | `POST /v1/auth/logout/` | `request.user.auth_token.delete()`. Enhanced variant silent-swallows exceptions to log. |
| Revoke via Frontend (Sidebar) | `Sidebar.tsx:356` onClick | localStorage clear only (via authStore.logout + Zustand persist) | **DOES NOT call authApi.logout()** — F-D-SIDEBAR-1 HIGH. Backend token never revoked via this path. |
| Silent expiry (client-side) | **NONE** (F-C-VIP-1 companion) | — | Token cannot expire client-side without server signaling; VIPInvite.account_expires_at declared but not enforced. |
| Session cookie (compatibility path) | Django session middleware | `sessionid` HTTP-only cookie | Set by backend on session-auth flows (admin, staff login form); frontend uses `withCredentials: true` to include. |

**localStorage surface at HEAD** (extends Cat C §14.2 15-surface
baseline; NO DRIFT verified):

- `auth-storage` (authStore Zustand persist): CLEAN — cleared on `logout()`. 1 of 15 surfaces (6.7% cleanup rate).
- 11+ localStorage keys NO-CLEANUP: workspace, profile, workspace-members, workspace-roles, workspace-permissions, user-prefs, notifications, demo-mode-session, theme, language, etc.
- 3 PARTIAL: paStore (workspace-context boundary), pipeline_dismissed, podcast_voice_profile
- 1 Session 968 X-UI-Scope ring buffer (dev-only)
- 0 sessionStorage
- 0 IndexedDB
- 1 cookie (`sessionid`) — backend-owned, frontend read-only via withCredentials

---

## 9. Integrations With Other Domains

Extends S2400 §3.D output (e) cross-arc coordination flags with
Cat A/B/C findings inheritance.

| Cross-arc flag | Owning arc | Handoff | Cat D discharge |
|---|---|---|---|
| **CF-D1** | Group 2500 API (T2) | API refresh endpoint + logout envelope + Clear-Site-Data emission decision + typed-error-envelope adoption + per-endpoint permission registry design-prep. Consumes Cat B §19.1 (a)/(b)/(c) + Cat C §19.1 (α)/(β)/(γ) + Cat D §19.1 α/β/γ × 2 (envelope + whitelist replacement). | Cat D enumerates + escalates to xx99. |
| **CF-D2** | Group 2600 PA (T3) | `session_tool.retire` on user logout cascade + workspace-context authz + paStore field-list completeness + PA-chat silent-401 exposure (extends Cat C CF-C2). PA-chat endpoints (`/pa/chat/`, `/pa/chat/status/`, `/pa/conversations/`) do NOT match whitelist — 401 mid-conversation silently rejected. | Cat D surfaces + escalates. |
| **CF-D3** | Group 1700 Observability (T4) | Extends Cat A CF-2 + Cat B CF-B5 + Cat C CF-C3 into xx99 §5.4 Observability umbrella roll-up. 401-event emission + retry-budget telemetry + silent-401 rate observability + error-boundary catch-emit + logout-cascade audit trail. | Cat D adds silent-401 rate telemetry + logout-cascade audit to roll-up scope. |
| **CF-D4** | Group 2300 Mobile | Mobile app parallel silent-401 audit (Expo scaffolding at row 19). Ensure 401-handling parity between web + mobile OR document divergence explicitly. | Cat D flags; Group 2300 executes when arc opens. |
| **CF-D5** ⚠ BLOCKING PREREQUISITE for option-γ (Rigby SIGN Q18 fold — 2026-07-05) | Group 2200 post-arc T-slot | R6 error-boundary framework establishment. Requires cross-arc coordination with T1 Group 2400 Auth (session model) + T2 Group 2500 API (typed responses). **Cat D lean for option-γ typed-error-envelope depends on top-level `<ErrorBoundary>` wrapper existing** — without R6 execution, option-γ cannot surface caught errors to user-visible UX. R6 is therefore a blocking prerequisite for γ mechanism landing, not merely a cross-arc handoff. | Cat D delivers decision-space to xx99; R6 execution readiness depends on T1 + T2 + is itself the blocking prerequisite for γ mechanism. |
| **CF-D6** | Group 1900 Governance | KillSwitch attestation on typed-401 boundary preserved. Ensure auth-error-swallow does not bypass kill-switch semantics if governance decisions cross 401 boundary. | Cat D re-verifies at close — kill-switch semantics NOT altered by Cat D scope. |
| **CF-D7** | Group 2400 Auth INTERNAL (xx99) | Silent-401 + typed-error-envelope + Cat C three-option decision-space intersection with F-C-CSD-1 (Clear-Site-Data) + F-C-STORE-1 (15-surface cleanup) + F-C-TAB-1 (cross-tab sync). Cat D α/β/γ × 2 decision-space and Cat C (α/β/γ) decision-space intersect. | Cat D fully enumerates intersection at §19; xx99 consolidates Chris D-verdict. |

**Findings inheritance table (compact — full per-category detail in §14).**

| Finding ID | Source arc | Cat D relevance | HEAD status | Cat D re-verification |
|---|---|---|---|---|
| F-DEC-1 | Cat A S2401 | Frontend-adjacent (9 view files caller-surface uses decorator; frontend does not know which error path is in use) | HEAD-verified: 65 occurrences / 10 files (drift-down from 68/9 baseline) | CONFIRMED-STILL-LIVE-AT-HEAD-31398008 with numeric drift-down |
| F-WS-1 | Cat A S2401 | Frontend-adjacent (WS auth silent-swallow parallels frontend silent-401 SYSTEMIC) | Companion pattern; WS middleware DEAD at HEAD per S2202 F1 | CONFIRMED-STILL-LIVE-AT-HEAD-31398008 |
| F-CRIT-1 | Cat A S2401 | Backend-only; NOT frontend-visible | PURGE_SECRET hardcoded fallback at `core/views_home.py:259` | Out-of-scope for Cat D re-verification |
| F-BND-4a | Cat A S2401 | CRITICAL money-path frontend caller (BettingPage `placeBetMutation`) | Unauth bet-placement inversion at `/api/v1/betting/place/` | Frontend inheritance: any α/β/γ envelope must preserve BettingPage behavior |
| F-B-CRIT-1 | Cat B S2402 | ROOT CAUSE of silent-401 SYSTEMIC (implicit-inheritance ~80-90%) | CONFIRMED at HEAD via §14.5 trust-boundary rate table | Cat D reports SYSTEMIC symptom rate 803-scale |
| F-B-CRIT-2 | Cat B S2402 | Silent-401 SYSTEMIC (necessary-enabling-condition downstream of F-B-CRIT-1) | CONFIRMED-STILL-LIVE-AT-HEAD-31398008 | Cat D consumes as primary target |
| F-B-MED-3 | Cat B S2402 | HTTP-path 503-fork asymmetry (Session 1171 lineage) | HTTP-only per S2403; caller-side symptom | Cat D audits FE-caller side |
| F-B-HIGH-1 | Cat B S2402 | STAFF_REQUIRED_PATHS phantom-entries | 2 of 3 phantom confirmed at HEAD | Not Cat D scope (backend cleanup) |
| F-B-HIGH-4 | Cat B S2402 | auth_views_enhanced.py `@authentication_classes([])` + `[IsAuthenticated]` per-site | 4 files at HEAD | Not Cat D scope (backend cleanup) |
| F-B-OWN-6 | Cat B S2402 | CI test-harness permission-floor enforcement absent | ABSENT at HEAD | Cat D extends: no CI test-harness for silent-401 rate either — see F-D-OWN-2 |
| F-C-VIP-1 | Cat C S2403 | HIGH risk-gate for α/β/γ expiry-signal-bearing UX | CONFIRMED-STILL-LIVE-AT-HEAD-31398008 via `models_vip_invite.py:96-103` | Cat D respects constraint — envelope UX must not surface expiry signals until F-C-VIP-1 resolves |
| F-C-REFRESH-1 | Cat C S2403 | HIGH — no refresh endpoint | ABSENT at HEAD (grep zero-match for refresh in `core/urls*.py` auth-surface) | CONFIRMED-STILL-LIVE-AT-HEAD-31398008 |
| F-C-CSD-1 | Cat C S2403 | HIGH — zero Clear-Site-Data on logout | CONFIRMED-STILL-LIVE-AT-HEAD-31398008 (grep zero-match) | Cat D flags CF-D1 dependency |
| F-C-STORE-1 | Cat C S2403 | HIGH — 14/15 client-side surfaces lack declared logout-cleanup | Zero DRIFT from Cat C declaration | Cat D confirms via authStore.ts HEAD-read; extends via F-D-SIDEBAR-1 |
| F-C-COOKIE-1 | Cat C S2403 | LOW-MED — SESSION_COOKIE_DOMAIN + PATH undeclared | ABSENT declaration at HEAD | Not Cat D scope (backend settings) |
| F-C-LOGOUT-1 | Cat C S2403 | MED — basic logout no permission decorator; silent-200 on unauth | CONFIRMED at HEAD via `auth_views.py:84-94` | Cat D confirms via Flow D |
| F-C-COCKPIT-1 | Cat C S2403 | MED — 16 cockpit `<Navigate>` NOT wrapped by ProtectedRoute | CONFIRMED-STILL-LIVE at `frontend/src/App.tsx:134-149` | Cat D re-verifies STILL-LIVE at HEAD |
| F-C-TAB-1 | Cat C S2403 outstanding queue | MED — cross-tab storage-event listener absent | Grep zero-match for `BroadcastChannel` or `window.addEventListener('storage'` at HEAD | Cat D confirms |

---

## 10. Event Flows

**Zero WS auth events emitted at HEAD.** No login / logout / session-expiry / 401-error events emitted on any observability channel:

- `CeleryTaskEvent` / `AuditLogEntry` / `LLMCallEvent` / `AgentLifecycleEvent` — none receive frontend auth events.
- Django signals — no `user_logged_in` / `user_logged_out` handlers in `core/signals*.py` for auth-view completions.
- Frontend telemetry — `console.warn('Authentication required for:', url)` at `api.ts:58` is the ONLY signal, and it is browser-side (not persisted).
- No `storage` event listener; multi-tab logout does not propagate (F-C-TAB-1 CONFIRMED-STILL-LIVE at HEAD).

**Cat D event-flow deliverable to xx99:** enumerate the 8+ missing
event-emit points and route to CF-D3 Group 1700 Observability
umbrella roll-up. See §14 F-D-EVENT-1 finding.

---

## 11. Existing Documentation

| Doc | Coverage of Cat D scope | Gap |
|---|---|---|
| `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` §14 F3 + F3.5 | Silent-401 SYSTEMIC at ~630 baseline; whitelist BRITTLE | Cat D extends to 803-scale + adds F-D-SIDEBAR-1 + F-D-BYPASS-1 |
| `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md` §15.5 | Silent 401 systemic + no error boundaries anywhere | Cat D confirms zero error boundaries at HEAD |
| `docs/research/domains/frontend/2202_frontend_client_state_data_flow_discipline_audit.md` §14 | WS auth silent-swallow F1 MOCK-DATA-CONSUMER; frontend receives AnonymousUser fallback | Cat D companion evidence for F-WS-1 |
| `docs/research/domains/frontend/2204_frontend_session_state_persistence_discipline_audit.md` §14 F1 | 15-surface storageKeys baseline (12 direct localStorage + 3 Zustand persist) | Cat D re-verifies at HEAD with zero drift |
| `docs/research/domains/frontend/2299_frontend_canonical_summary.md` §5.1 + §8.2 + §8.3 | Canonical seam statement + T1 4-axis handoff + R6 error-boundary framework | Cat D executes T1 readiness + R6 unblocking |
| `docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md` | Cat A findings F-CRIT-1, F-BND-4a, F-DEC-1, F-WS-1 + §14.5 trust-boundary rate | Cat D re-verifies subset at HEAD |
| `docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` | Cat B findings F-B-CRIT-1, F-B-CRIT-2 + §19.1 (a)/(b)/(c) three-option | Cat D consumes as primary target |
| `docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md` | Cat C findings F-C-* + §19.1 (α)/(β)/(γ) three-option | Cat D consumes + intersects with Cat D α/β/γ × 2 |
| `docs/topics/frontend.md` | UI/feature-focused; DOES NOT cover silent-401 pattern | GAP — Cat D §19.4 AU-D1 anchor-update recommendation for post-arc |
| `docs/topics/auth.md` | DOES NOT EXIST at HEAD | GAP — Cat D §19.4 AU-D2 recommendation (extends Cat A/B/C AU-1/AU-B2/AU-C1) |
| `docs/topics/session_lifecycle.md` | DOES NOT EXIST at HEAD | GAP — Cat C AU-C4 flags; Cat D concurs post-Chris-D-verdict on α/β/γ |
| CODEOWNERS (root, `.github/`, `docs/`) | DOES NOT EXIST at HEAD | GAP — F-D-OWN-1 NEW HIGH FINDING (extends Cat A/B/C ownership gap thesis to frontend integration surface) |

---

## 12. Research Coverage

**Classification per playbook §12: MODERATE**

Cat D scope has existing MODERATE-CANONICAL research coverage
(S2203 established baseline; S2201 established error-boundary gap;
S2299 established canonical seam statement + T1 handoff; Cat A/B/C
established backend-side model). Cat D extends coverage from
MODERATE to MODERATE-verging-DEEP:

- **MODERATE per S2203 A3 baseline** (~630 call-sites estimate; wrapper-duplicate acknowledged)
- **MODERATE per S2201 §15.5** (no error boundaries; silent 401 systemic)
- **DEEP per S2202 §14 F1 + S2299 §5.1** (canonical seam statement bridging Group 2200 → Group 2400)
- **DEEP per Cat A + Cat B + Cat C** (backend session-model + permission-floor + logout-cleanup contract audits)

Cat D adds:
- 803-scale call-site enumeration (extends S2203 ~630)
- 79-fetch-bypass discovery (F-D-BYPASS-1 — new)
- Sidebar-logout-does-not-revoke-backend-token (F-D-SIDEBAR-1 — new)
- Money/governance/PA path classification (extends S2203 A3)
- Typed-error-envelope + whitelist-replacement three-option × two decision spaces (α/β/γ × 2)

**Post-Cat-D verdict: DEEP.** All four contract axes (silent-401 + logout cleanup + session lifecycle + permission-floor uniformity) now have dedicated audit docs. xx99 will consolidate.

---

## 13. Architecture Maturity

**Classification per playbook §12: PARTIAL**

| Axis | Verdict | Evidence |
|---|---|---|
| **Mechanisms** | WORKING | axios interceptor fires correctly; token injected via request.use; 401 response.use catches status; `logout()` mutation works; ProtectedRoute navigates unauthenticated users; Sidebar clears store. All machinery succeeds at file-precision level. |
| **Contract semantics** | PARTIAL | ~99% of 803 consumer call-sites silently swallow 401 with only `console.warn` telemetry; no typed error envelope; brittle whitelist substring. 14/15 client-side persistence surfaces lack declared logout-cleanup contract. Backend 401 envelope exists (`api_responses.py:143-149`) but frontend does not typed-catch it. |
| **Governance / observability** | EXPERIMENTAL | No permission-floor registry (Cat B F-B-CRIT-1); no CI test-harness (F-B-OWN-6 + F-D-OWN-2); no CODEOWNERS (F-D-OWN-1); no observability event emit on auth events (F-D-EVENT-1); no error-boundary framework (S2299 §8.3 R6); silent-401 treated as default behavior, not anti-pattern. |

**Overall verdict: PARTIAL.** Mechanisms work; contract semantics
are unenforced; governance is EXPERIMENTAL. "Works in places but
not cohesive" per playbook §12 PARTIAL definition. Silent-401
pattern is **declared-fictional** — the api.ts:47 comment "Only
redirect to login for explicit auth endpoints / Other 401s should
be handled by the component" IMPLIES component-level handling, but
0 explicit `AxiosError` catches + 0 error boundaries + `console.warn`
only signal means the "handled by the component" contract is NOT
enforced.

---

## 14. Known Drift

### 14.1 Findings summary (Cat D findings enumerated + Cat A/B/C re-verifications)

| Finding ID | Class (S1274 §11) | Severity | Class family | HEAD status |
|---|---|---|---|---|
| **F-D-CALL-1** (NEW) | `technical_debt` | HIGH | silent-degrade | 803 consumer call-sites; ~99% silent-swallow rate CONFIRMED at HEAD |
| **F-D-BYPASS-1** (NEW) | `boundary_violation` | HIGH | silent-degrade | 79 raw fetch() across 31 files bypass interceptor entirely at HEAD |
| **F-D-SIDEBAR-1** (NEW) | `missing_connection` | HIGH | silent-degrade | Sidebar.tsx:356 does NOT call authApi.logout(); backend token never revoked via sidebar path |
| **F-D-WHITELIST-1** (extends S2203 F3.5) | `drift` | MED | silent-degrade | Whitelist substring `/auth/` + `/login` BRITTLE; 0 false-positives at HEAD but scales badly |
| **F-D-ENVELOPE-1** (NEW) | `missing_connection` | HIGH | silent-degrade | 0 typed AxiosError catches; typed-error-envelope adoption is greenfield |
| **F-D-BOUNDARY-1** (NEW) | `missing_connection` | HIGH | silent-degrade | 0 error boundaries anywhere in frontend (S2201 §15.5 CONFIRMED-STILL-LIVE at HEAD) |
| **F-D-OWN-1** (NEW) | `unclear_owner` | MED | governance | CODEOWNERS file absent at `.github/`, root, `docs/`; api.ts + authStore.ts de facto owned by Chris but undeclared |
| **F-D-OWN-2** (extends F-B-OWN-6) | `unclear_owner` | MED | governance | No CI test-harness for silent-401 rate observability (companion to F-B-OWN-6) |
| **F-D-EVENT-1** (NEW) | `event_gap` | MED | silent-degrade | Zero auth-event emission (login/logout/401/expiry) on any observability channel; console.warn only signal is browser-side |
| **F-D-PA-1** (extends Cat C CF-C2) | `technical_debt` | HIGH (Rigby SIGN Q10 fold — 2026-07-05: escalated MED→HIGH because PA chat is control-plane UX; silent-401 looks like agent-hang and breaks the core workflow; severity reflects blast radius + user-trust impact, not just endpoint count) | silent-degrade | PA-chat endpoints (`/pa/chat/`, `/pa/chat/status/`, `/pa/conversations/`) do NOT match whitelist; 401 mid-conversation silently rejected — PA UI enters undefined state |
| **F-D-COCKPIT-1** (extends Cat C F-C-COCKPIT-1) | `drift` | MED + ownership-drift-risk flag (Rigby SIGN Q19 fold — 2026-07-05: MED preserved but repeated two-audit re-verification without fix indicates ownership-drift risk; attach to F-D-OWN-1 / F-D-OWN-2 governance remediation) | silent-degrade | 16 cockpit `<Navigate>` at `frontend/src/App.tsx:134-149` NOT wrapped by ProtectedRoute — CONFIRMED-STILL-LIVE-AT-HEAD |
| F-DEC-1 (Cat A re-verified) | `drift` | HIGH | silent-degrade | 65 occurrences / 10 files at HEAD (down from 68/9 baseline). **Rigby SIGN Q8 fold — 2026-07-05:** Cat A counts drifted; finding semantics unchanged; definition-site (`auth_middleware.py:1`) now included in grep denominator but excluded from applied-use count (applied uses = 64 / 9 view files at HEAD). |
| F-WS-1 (Cat A re-verified) | `drift` | HIGH | silent-degrade | WS auth silent-swallow CONFIRMED-STILL-LIVE-AT-HEAD-31398008 |
| F-B-CRIT-1 (Cat B re-verified) | `technical_debt` | CRITICAL | silent-degrade | Permission-floor implicit-inheritance ~80-90% (ROOT CAUSE of silent-401 SYMPTOM) |
| F-B-CRIT-2 (Cat B re-verified) | `technical_debt` | CRITICAL | silent-degrade | Silent-401 SYSTEMIC CONFIRMED-STILL-LIVE-AT-HEAD-31398008 |
| F-C-VIP-1 (Cat C re-verified) | `technical_debt` | HIGH | silent-degrade | `VIPInvite.account_expires_at` NOT enforced at HEAD; risk-gate for α/β/γ envelope UX |
| F-C-REFRESH-1 (Cat C re-verified) | `missing_connection` | HIGH | silent-degrade | No refresh endpoint at HEAD; implicit permanent-token contract |
| F-C-CSD-1 (Cat C re-verified) | `technical_debt` | HIGH | silent-degrade | Zero Clear-Site-Data emission on logout CONFIRMED-STILL-LIVE-AT-HEAD |
| F-C-STORE-1 (Cat C re-verified) | `technical_debt` | HIGH | silent-degrade | 14/15 surfaces NO-CLEANUP; 6.7% cleanup rate ZERO-DRIFT from Cat C |

**Silent-degrade class rate at Cat D (Rigby SIGN Q5 fold — 2026-07-05).**
17 of 19 findings above (89.5%) are silent-degrade class. The two
non-silent-degrade findings are both **governance class**:
**F-D-OWN-1** (CODEOWNERS absent) and **F-D-OWN-2** (CI test-harness
absent). **CONFIRMS Q20 fold TRIGGER #2 CANDIDATE** for playbook §20
codification-candidate promotion at S2499 xx99 close (Cat C = TRIGGER
#1 at 13-of-14 silent-degrade = 92.9%; Cat D = TRIGGER #2 at 17-of-19
= 89.5%; both above codification threshold; two-trigger threshold
met — silent-degrade dominance persists across Cat C and Cat D).

### 14.2 Silent-401 SYSTEMIC drift matrix at HEAD

| Drift dimension | Numerator | Denominator | Rate | Evidence |
|---|---|---|---|---|
| Consumer call-sites with NO first-class error surfacing | ~798 | 803 | ~99% | Grep verified: 0 typed AxiosError catches; 0 error boundaries; 65 `onError` callbacks at RQ layer per Agent 6 sample (13.6% of RQ layer; ~4% of total 803 surface) |
| Consumer call-sites using RQ error typing vs raw try/catch vs no handler | RQ+onError sample: 65; raw try/catch sample: ~134; total non-handled: majority | 803 | ~99% silent-degrade | Break-down: ~65 RQ onError + ~134 raw try/catch + rest silent (sample-derived, extrapolated from grep counts) |
| Whitelist substring `/auth/` + `/login` false-positives | 0 | 5 auth-endpoint matches | 0% | Grep verified at HEAD: no non-auth endpoints contain the substrings |
| Non-api.ts axios instances OR raw fetch() bypassing interceptor | 79 (raw fetch) + 0 (extra axios instances) | 803 | 9.8% bypass rate | Grep verified: 1 axios.create at api.ts:13; 79 raw fetch() across 31 files |

### 14.3 21-loci lifecycle-observability rate extension (extends Cat C §14.3)

Cat C established 5 WORKING + 5 PARTIAL + 11 DEAD (21 loci total).
Cat D adds SILENT-401-specific loci:

| Locus (Cat D extension) | Status at HEAD | Evidence |
|---|---|---|
| Login event emit → Observability | DEAD | No signal handler; no CeleryTaskEvent; no AuditLogEntry |
| Logout event emit → Observability | DEAD | No signal handler; no cascade broadcast |
| 401 response emit → Observability | DEAD | `console.warn` only; not persisted |
| Session-expiry event emit → Observability | DEAD (F-C-VIP-1 companion) | No client-side detection; no server-side push |
| Sidebar logout → authApi.logout() call | DEAD | F-D-SIDEBAR-1 — backend never notified |
| Silent-401 telemetry rate | DEAD | Not measured; not surfaced |
| Cross-tab logout propagation | DEAD | F-C-TAB-1 CONFIRMED |
| ErrorBoundary catch-emit | DEAD | 0 error boundaries at HEAD |
| Typed-AxiosError classification | DEAD | 0 typed catches at HEAD |
| noAuthRedirect flag adoption | DEAD | 0 adoption at HEAD |
| Interceptor bypass event (79 raw fetch) | DEAD | F-D-BYPASS-1 — not observable |

**Cat D rate extension: 0 WORKING + 0 PARTIAL + 11 DEAD** (silent-401 slice of 21-loci extended framework).

### 14.4 15-surface storageKeys × logout-cleanup CONTRACT re-verification

Zero drift from Cat C §14.2 at HEAD `31398008`:
- 1 CLEAN (`auth-storage` cleared via Zustand persist on `authStore.logout()`)
- 3 PARTIAL (paStore syncUser incomplete; pipeline_dismissed workspace-change; podcast_voice_profile change)
- 11 NO-CLEANUP
- **Cleanup contract rate: 1 of 15 = 6.7% CONFIRMED**

Cat D adds:
- **F-D-SIDEBAR-1 caveat:** `authStore.logout()` at Sidebar.tsx:356 does not call `authApi.logout()`, so even the 1 CLEAN surface has an incomplete BACKEND-SIDE revoke. Backend `authtoken_token` row remains until password event OR user hits enhanced logout via API.

### 14.5 803-call-site classification by inheritance-path (extends Cat A §14.5 trust-boundary rate table format)

| Inheritance path | Count | Silent-401 exposure | Interceptor coverage |
|---|---|---|---|
| **Direct `api.<verb>()` in consumer code** (non-api.ts files) | 57 | Silent reject (except 5 auth endpoints matching whitelist) | 100% (interceptor-routed) |
| **`useQuery`/`useMutation` React Query wrappers** | 667 | Silent reject; RQ `error` field untyped; `onError` callback wired at ~10% (65/667) sample rate | 100% (interceptor-routed) |
| **Raw `fetch()` calls (F-D-BYPASS-1)** | 79 | No interceptor triggered; no auth-token attach; no 401 catch; component MUST manually handle | **0% (bypass)** |
| **TOTAL consumer call-sites** | **803** | ~99% silent-degrade rate | 90.2% interceptor coverage |

---

## 15. Known Technical Debt

Ranked by architectural uncertainty × risk × unblocked flows.

1. **F-B-CRIT-2 silent-401 SYSTEMIC + F-D-CALL-1 803-scale extension (rank-1 co-equal with Cat A F-CRIT-1 + Cat B F-B-CRIT-1 + Cat C F-C-VIP-1).** ROOT CAUSE downstream of Cat B F-B-CRIT-1 implicit-inheritance rate. Blocks acceptance criteria #1 + #2. Post-arc T-slot at S2499 xx99 close.
2. **F-D-BYPASS-1 79-raw-fetch bypass (NEW HIGH).** 9.8% of consumer surface bypasses interceptor entirely; no token attach + no 401 catch. Requires either (a) migrate fetch→api conversions per-site OR (b) global fetch wrapper at api-boundary layer.
3. **F-D-SIDEBAR-1 backend-token-not-revoked-via-sidebar (NEW HIGH).** Sidebar.tsx:356 clears authStore but does not call `authApi.logout()`. Any leaked token remains valid indefinitely absent F-C-REFRESH-1 refresh endpoint OR password event.
4. **F-D-ENVELOPE-1 zero typed AxiosError catches (NEW HIGH).** Typed-error-envelope adoption is greenfield; three options (α/β/γ) enumerated at §19.1 for xx99 D-verdict.
5. **F-D-BOUNDARY-1 zero error boundaries (S2201 §15.5 CONFIRMED-STILL-LIVE).** No framework to surface silent-swallowed 401s. R6 execution readiness gated on T1 + T2.
6. **F-D-WHITELIST-1 brittle substring whitelist (S2203 §14 F3.5 extension).** Zero false-positives at HEAD but scales badly. Three replacement options (α/β/γ) enumerated at §19.1.
7. **F-D-PA-1 PA-chat silent-401 exposure.** `/pa/chat/*` endpoints do NOT match whitelist; session expiry mid-conversation leaves PA UI in undefined state. CF-D2 to Group 2600 PA.
8. **F-D-EVENT-1 zero auth-event emission.** No observability signal on login/logout/401/expiry. CF-D3 to Group 1700 Observability umbrella roll-up.
9. **F-D-OWN-1 CODEOWNERS absent + F-D-OWN-2 CI test-harness absent.** Governance layer for silent-401 rate is EXPERIMENTAL; extends F-B-OWN-6 CI enforcement gap.
10. **F-DEC-1 + F-WS-1 (Cat A) + F-C-VIP-1 + F-C-REFRESH-1 + F-C-CSD-1 + F-C-STORE-1 (Cat C) all CONFIRMED-STILL-LIVE.** Inherited debt; execution owed to post-arc T-slot per §19.2 rank-1 co-equal batch (extends Cat A F-CRIT-1 + F-BND-4a preservation).

---

## 16. Boundary Violations

**F-D-SIDEBAR-1** (NEW HIGH; §7 Flow D). Sidebar logout onClick at
`frontend/src/components/layout/Sidebar.tsx:356` violates the
implicit "logout-means-token-revoked" contract:
- Frontend: clears localStorage via `authStore.logout()` + Zustand persist.
- Backend: `authtoken_token` row remains until enhanced logout endpoint invoked OR password event.
- Attacker-valid window: any leaked token remains valid indefinitely.

**F-D-BYPASS-1** (NEW HIGH; §5 wrapper-duplicate accounting). 79
raw `fetch()` calls across 31 files violate the "all HTTP requests
route through interceptor" implicit contract:
- No token attach on bypass path.
- No 401 catch on bypass path.
- Relies solely on session cookie (via `credentials: 'include'`).
- Zero visibility into 9.8% of frontend HTTP surface.

**F-C-COCKPIT-1 CONFIRMED (extends Cat C).** 16 cockpit
`<Navigate>` at `frontend/src/App.tsx:134-149` NOT wrapped by
ProtectedRoute; unauthenticated navigation to `/cockpit/*` routes
falls through to redirect targets rather than login gate. STILL-LIVE
at HEAD.

**F-BND-4a (Cat A) preserved.** Unauth bet-placement at
`/api/v1/betting/place/` (money-path CRITICAL); BettingPage
`placeBetMutation` frontend caller inherits inversion — must be
preserved by any α/β/γ envelope.

---

## 17. Duplicate or Overlapping Systems

**Zero axios wrapper duplication (S2203 §14 F3 Q14 preservation).**
Single `api = axios.create({...})` instance at
`frontend/src/lib/api.ts:13`. `cockpitApi.ts` + `apiClient.ts`
re-use shared `api` instance; no independent interceptor. Signal:
API-boundary consolidation is COMPLETE at axios layer.

**79-raw-fetch interceptor-bypass (F-D-BYPASS-1).** NOT a
wrapper-duplicate — it is a **contract-bypass**. 79 sites use raw
`fetch()` because either (a) the endpoint doesn't need auth (public
paths — 12+ known via S2204 baseline); OR (b) developer chose
fetch for simplicity (SSE, streams, non-JSON payloads); OR (c)
copy-paste from external examples. Not all 79 need migration —
audit-out-of-scope-fix per S2400 anti-scope #7 (findings graduate
to T-slot).

**Multiple redirect paths at Sidebar vs api.ts.** Sidebar clears
authStore + navigates via ProtectedRoute; api.ts:55 uses
`window.location.href = '/login'` (full page reload). Two logout
UX paths co-exist; contract semantics differ (sidebar preserves
localStorage keys except authStore; api.ts full-page-reload
re-hydrates from localStorage but session-clear via Zustand
persist is identical). NOT redundant — surfaces different UX
intent. Cat D flags for xx99 review under CF-D7 (Cat C α/β/γ
intersection).

---

## 18. Ownership Gaps

**F-D-OWN-1 NEW HIGH.** CODEOWNERS file absent at all three
canonical locations: `.github/CODEOWNERS`, `CODEOWNERS` (repo
root), `docs/CODEOWNERS`. HEAD-verified. `api.ts` + `authStore.ts`
+ Sidebar.tsx logout code owned de facto by Chris (git log
verified) but not declared. Cross-arc typed-error-envelope
ownership + whitelist-replacement ownership UNASSIGNED. Extends
Cat A/B/C ownership-gap thesis (Cat A F-DOC-1 + Cat B F-B-OWN-6 +
Cat C AU-C series) to frontend integration surface.

**F-D-OWN-2 MED (extends F-B-OWN-6).** No CI test-harness for
silent-401 rate observability. Cat B F-B-OWN-6 flagged
permission-floor enforcement gap; Cat D extends to silent-401
rate telemetry gap. Post-arc governance gate item.

**Cross-arc ownership map (compact):**

| Axis | HEAD state | Owner declared? | Post-arc owner candidate |
|---|---|---|---|
| `frontend/src/lib/api.ts` | Chris West (git-log de facto) | NO — CODEOWNERS absent | Frontend maintainer (Chris/donkey-betz-eng lane) |
| `frontend/src/stores/authStore.ts` | Chris West (git-log de facto) | NO | Frontend maintainer |
| Typed-error-envelope design (cross-arc α/β/γ) | UNCLEAR — spans Cat D + Group 2200 R6 + Group 2500 API | NO | Chris D-verdict at xx99 selects; owner-of-record = Group 2500 API arc lead (T2) |
| Whitelist-replacement design (α/β/γ × 2) | UNCLEAR | NO | Chris D-verdict at xx99 selects; owner-of-record = api.ts maintainer + Group 2500 API arc lead |
| Backend Clear-Site-Data emission (F-C-CSD-1) | UNCLEAR | NO | Group 2500 API arc lead + backend auth-view owner |
| Sidebar logout backend-revoke fix (F-D-SIDEBAR-1) | UNCLEAR | NO | Frontend maintainer (T-slot post-arc single-line fix) |

---

## 19. Recommended Future Research

### 19.1 Three-option decision spaces (Cat D α/β/γ × 2)

**Typed-error-envelope design candidates** (per S2400 §3.D output (c)):

**Option (α) — Throw typed exceptions per HTTP status.**
- Frontend approach: response interceptor throws `UnauthorizedError`, `PermissionError`, `ValidationError`, `ServerError` classes; components catch typed.
- Call-site touches: ~413 silent-swallow sites need explicit `try/catch` OR error-boundary catch-emit.
- Backend contract dep: YES — requires discriminated error envelope backend must emit uniformly (`api_responses.py` envelope exists but not fully-typed).
- Risk: HIGH. Changes execution flow across ~800 call-sites; risk of partial rollout leaving some unguarded.
- Aligns with: exception-based error handling paradigm.

**Option (β) — Return discriminated-union response types.**
- Frontend approach: wrap each `api.<verb>()` return type as `Result<T, E> = { ok: true; data: T } | { ok: false; error: E }`.
- Call-site touches: ~413 sites must pattern-match `result.ok` before accessing data.
- Backend contract dep: PARTIAL — envelope shape can be inferred from response body; backend contract unchanged at network layer.
- Risk: MEDIUM. Refactoring-heavy but backward-compatible at Promise layer.
- Aligns with: functional / Rust-style error handling paradigm.

**Option (γ) — React-Query error callbacks + `QueryClient` default `onError` handler + error boundary.**
- Frontend approach: leverage existing 667 useQuery/useMutation hooks; add typed `onError` per hook OR centralize at QueryClient level. Add top-level `<ErrorBoundary>` wrapper at App.tsx.
- Call-site touches: ~5-10 component-tree touches + QueryClient config + error boundary wrapper.
- Backend contract dep: NO (leverages RQ mechanics; backend unchanged).
- Risk: LOW. Requires QueryClient reconfiguration + error boundary adoption at framework level, not per-call-site.
- Aligns with: React Query idiom (existing infra); minimizes call-site friction.

**Cat D lean for xx99 Chris D-verdict (Rigby SIGN Q6 fold — 2026-07-05).**
Option **(γ) React-Query error callbacks + top-level ErrorBoundary**
as PROPOSED PRIMARY DEFAULT for REMEDIATION WINDOW — **γ is the
fastest path to *explicit failure + recoverability*** given React
Query saturation (667 hook sites); it does NOT preclude later (β)
discriminated-union adoption at the API layer as envelope shape
stabilizes. **Explicit reconciliation with Cat C:** adopt Cat C's
"explicit re-login" semantics **as the default handler *inside*
(γ)** — γ is the mechanism (RQ error callbacks + boundary);
Cat C β is the message/UX policy (explicit re-login, not silent
refresh). Option **(β) discriminated union** and Option **(α)
typed exceptions** as post-arc ENHANCEMENT candidates.

**Handler-behavior discipline (Rigby SIGN Q9 fold — 2026-07-05).**
Whatever option ships, the handler MUST distinguish three error
classes at minimum: (i) 401/403 auth-failure; (ii) network/offline;
(iii) 5xx server-error. Silent-swallow of any of these three
degrades observability; conflating them produces wrong UX.

**Copy guidance for auth-failure UX (Rigby SIGN Q9 fold — 2026-07-05;
Cat C F-C-VIP-1 risk-gate preservation).** Because F-C-VIP-1
(VIPInvite.account_expires_at not enforced at runtime) is a
risk-gate for shipping any expiry-signal-bearing UX, the auth
handler MUST NOT surface "Session expired" or other time-based
expiry copy. Use **"Sign-in required" / "Authentication required"
/ "Please sign in again"** (no time-based claim) until F-C-VIP-1
enforces expiry post-arc. This preserves Cat C constraint while
allowing option-γ envelope to ship.

**Whitelist-replacement design candidates** (per S2400 §3.D output (d)):

**Option (α) — Explicit endpoint list registry.**
- Approach: replace `url.includes('/auth/') || url.includes('/login')` with `AUTH_REDIRECT_ENDPOINTS.has(url)`.
- Where it lives: `frontend/src/lib/authEndpoints.ts` (new file) OR inline constant.
- Cost: single-file addition; explicit maintenance burden.
- Grep at HEAD: no existing endpoint-list constant.

**Option (β) — 401-response-suppression header from backend.**
- Approach: backend sets custom header (e.g., `X-Suppress-Auth-Redirect: true`) on 401 responses when frontend should handle locally.
- Cost: backend middleware change; requires cross-arc coordination with Group 2500 API.
- Grep at HEAD: no existing custom-header pattern for 401 responses in `core/auth_middleware.py` or `core/api_responses.py`.

**Option (γ) — Per-api-module explicit `noAuthRedirect` flag.**
- Approach: extend `InternalAxiosRequestConfig` interface with `noAuthRedirect?: boolean`; call sites explicitly opt out of redirect.
- Cost: extends existing `InternalAxiosRequestConfig` extension pattern at `api.ts:4-8` (Session 968 precedent). Non-breaking extension.
- Grep at HEAD: 0 `noAuthRedirect` occurrences; greenfield.

**Cat D lean for xx99 Chris D-verdict (Rigby SIGN Q7 fold — 2026-07-05).**
Option **(γ) per-api-module explicit-intent flag** as PROPOSED
PRIMARY DEFAULT. **Naming discipline:** use a **string enum**,
not a boolean — `authHandling: 'default' | 'suppress_redirect'`
is harder to misuse than `noAuthRedirect?: boolean` (the boolean
form is ambiguous about undefined-vs-false semantics + reads
awkwardly at call site). **Telemetry requirement:** every call
site that opts into `authHandling: 'suppress_redirect'` MUST emit
a telemetry event (extends CF-D3 Group 1700 Observability roll-up)
so silent-suppression is observable. Option **(α) explicit
endpoint list** as SIMPLER FALLBACK if per-module flag adoption
stalls. Option **(β) backend-header** as OPTIMAL POST-ARC candidate
once backend Group 2500 API landing.

### 19.2 Post-arc rank-1 co-equal P0 batch (extends Cat A/B/C)

Post-Cat-D rank-1 batch (POST-ARC, not this session's authoring
scope). **Co-equal per Cat A/B/C precedent preserved.** Rigby SIGN
Q15 fold — 2026-07-05 — adds tiered ordering rationale INSIDE the
co-equal list (blast-radius + exploitability) so the plan captures
blast-radius truth without reopening the co-equal contract.

**P0-A (platform-wide / whole-auth-surface blast radius):**
- **Cat D F-D-CALL-1** 803-scale silent-401 remediation
- **Cat D F-D-BYPASS-1** 79-raw-fetch bypass reconciliation
- **Cat D F-D-ENVELOPE-1** Typed-error-envelope (α/β/γ decision post-Chris-D-verdict)
- **Cat D F-D-BOUNDARY-1** Error-boundary framework establishment (S2299 §8.3 R6 execution)

**P0-B (token lifecycle / security window):**
- **Cat D F-D-SIDEBAR-1** Sidebar backend-token-revoke fix (single-line addition per Cat C AU-C1)
- **Cat C F-C-REFRESH-1** refresh discipline decision-space execution
- **Cat C F-C-VIP-1** VIPInvite.account_expires_at ENFORCEMENT (risk-gate prerequisite for α/β/γ)
- **Cat C F-C-CSD-1** Clear-Site-Data emission on logout
- **Cat C F-C-STORE-1** 15-surface × logout-cleanup declared contract execution

**P0-C (endpoint-specific):**
- **Cat A F-CRIT-1** PURGE_SECRET hardcoded fallback remediation (preserved)
- **Cat A F-BND-4a** Unauthenticated bet-placement WRITE remediation (preserved money-path boundary)
- **Cat B F-B-CRIT-1** Permission-floor implicit-inheritance ~80-90% (Chris D-verdict at xx99 on (a)/(b)/(c))
- **Cat B F-B-CRIT-2** Silent-401 SYSTEMIC (Cat D delivers 803-scale evidence + α/β/γ × 2 decision-space)
- **Cat D F-D-WHITELIST-1** Whitelist replacement (α/β/γ decision post-Chris-D-verdict; low-cost)

**Ordering rationale:** P0-A items block T1 handoff execution and
have platform-wide reach; P0-B items are prerequisite gates for
P0-A γ envelope UX (F-C-VIP-1 preserves copy discipline; F-D-SIDEBAR-1
closes attacker-valid window); P0-C items are single-endpoint or
narrow-surface remediations that can proceed in parallel with A + B
once decision-space is ratified. Co-equal contract preserved: all
14 items are P0; the A/B/C tiers surface blast-radius truth for
implementation sequencing, not priority downgrade.

### 19.3 Follow-on research queue (Cat D contributions)

Ranked by architectural uncertainty × risk × unblocked flows.
Rigby SIGN Q17 fold — 2026-07-05 — adds item (2b) raw-fetch
classification refinement + optional item (7) non-401 failure
envelope audit so γ mechanism does not become "401-only" and miss
other silent-degrade modes.

1. **Silent-401 rate telemetry design** — how to instrument the 803-scale silent-swallow rate as observable signal (F-D-OWN-2 extension). Requires collaboration with Group 1700 Observability.
2. **79-raw-fetch site classification (coarse)** — which of 79 need migration to `api.<verb>()`, which are legitimately public/streaming/SSE?
2. **(2b) Raw-fetch classification refinement (Rigby SIGN Q17 fold)** — classify 79 raw fetches into three axes: (i) *auth-required vs public vs metrics/health*; (ii) *credentials mode* (`credentials: 'include'` changes cookie-fallback behavior); (iii) *response type* (JSON vs SSE vs streams). Prereq for (2) migration decision.
3. **PA-chat 401 UX design** — how should PA UI respond to mid-conversation 401? Reconnect flow? Re-login modal? Session-restore-conversation? (CF-D2 to Group 2600 PA)
4. **Cross-tab logout propagation design** — F-C-TAB-1 needs `storage` event listener OR BroadcastChannel; Cat D confirms zero adoption at HEAD (extends Cat C).
5. **CODEOWNERS declaration** — F-D-OWN-1 remediation; single-file addition; post-arc governance gate.
6. **Error-boundary framework establishment** — S2299 §8.3 R6; unblocked by Cat D α/β/γ envelope decision + T1 + T2.
7. **(OPTIONAL if scope allows — Rigby SIGN Q17 fold) Non-401 failure envelope audit** — γ mechanism must not become "401-only" and miss other silent-degrade modes. Audit surface: JSON parse failure, network offline, timeout, aborted request. Extends F-D-ENVELOPE-1 beyond 401 plane.

### 19.4 Anchor-update recommendations for S2499 xx99

Cat D contributes to §7 xx99 anchor-update batch (concrete edits;
xx99 authors, not this doc):

- **AU-D1** `docs/topics/frontend.md` (EXISTS at HEAD, 12,471 bytes) — add silent-401 pattern + typed-error-envelope + error-boundary framework subsection. Cross-link to `docs/topics/auth.md` (proposed).
- **AU-D2** `docs/topics/auth.md` (DOES NOT EXIST at HEAD) — CREATE with subsections for (i) auth mechanism inventory (Cat A), (ii) permission-floor uniformity (Cat B), (iii) session lifecycle + logout cleanup (Cat C), (iv) frontend integration + silent-401 (Cat D). Extends Cat A AU-1 + Cat B AU-B2 + Cat C AU-C1 recommendations to full new-doc creation.
- **AU-D3** `PLATFORM_INVENTORY.md` §Auth autoblock (DOES NOT EXIST at HEAD) — extends Cat A/B/C recommendations. Add columns for silent-401-rate + typed-error-envelope-adoption + interceptor-bypass rate.
- **AU-D4** `PLATFORM_WHAT_IT_IS.md` §Auth narrative subsection (DOES NOT EXIST at HEAD) — extends Cat A/B/C recommendations. Add narrative for silent-degrade-vs-explicit-failure ambiguity as codified §20 weak-spot pattern (post-Q20 fold TRIGGER #2 confirmation).
- **AU-D5** CODEOWNERS declaration — extends F-D-OWN-1 remediation.
- **AU-D6** (Rigby SIGN Q16 fold — 2026-07-05) `docs/research/ARCHITECTURE_INDEX.md` (create-if-missing at target location) — add a short "**Auth failure handling decision matrix (α/β/γ typed-error-envelope × α/β/γ whitelist-replacement axis)**" pointer so future audits don't re-derive the design space. Cross-links to xx99 §7 anchor-update batch.
- **AU-D7** (Rigby SIGN Q16 fold — 2026-07-05) `docs/topics/auth.md` (new per AU-D2) MUST include DOC_LIFECYCLE cross-link note indicating (i) where "current state vs target state" lives; (ii) how future sessions should supersede this doc — prevents narrative drift as α/β/γ options ship and decision-space collapses.

### 19.5 Q20 fold candidate promotion — CONFIRMED

**Silent-degrade vs explicit-failure ambiguity codification (Rigby
SIGN Q5 fold — 2026-07-05).**
- Cat C = TRIGGER #1 (13-of-14 findings silent-degrade class = 92.9%)
- Cat D = TRIGGER #2 CONFIRMED (17-of-19 findings silent-degrade class = 89.5%; §14.1 table; two governance-class findings F-D-OWN-1 + F-D-OWN-2 explicitly named as non-silent-degrade)
- Two-trigger threshold met per playbook §20 codification-candidate promotion rule
- **Tightened codification claim:** silent-degrade dominance persists across Cat C and Cat D, exceeding the §20 dual-trigger threshold; promote to v3 candidate focused on **auth failure handling (401/403/refresh/logout)** with explicit UX + telemetry requirements. Not general silent-degrade-anywhere codification — scope-bounded to auth plane where the two triggers were observed.
- Recommend S2499 xx99 §10.2 codify as playbook v3 candidate under above scope-bounded framing.

---

## 20. Appendix

### 20.1 Files inspected (HEAD-verified at `31398008`)

**Frontend:**
- `frontend/src/lib/api.ts` (4,194 lines; sole axios instance)
- `frontend/src/stores/authStore.ts` (52 lines)
- `frontend/src/App.tsx` (161 lines; 62 `<Route>` entries)
- `frontend/src/components/layout/Sidebar.tsx` (line 356 logout onClick)
- `frontend/src/lib/cockpitApi.ts` (re-uses shared `api`)
- `frontend/src/lib/apiClient.ts` (re-uses shared `api`)
- `frontend/src/main.tsx` (QueryClient bootstrap)
- `frontend/src/components/platform/LiveMetricsDashboard.tsx` (raw fetch bypass exemplar)
- `frontend/package.json` (@tanstack/react-query present; no react-error-boundary)

**Backend:**
- `core/auth_views.py:65-75, 84-94, 118-126` (login/logout/current_user)
- `core/auth_views_enhanced.py:539-556` (enhanced logout)
- `core/auth_middleware.py:36-81, 632-633, 807-822` (decorator + middleware + WS middleware)
- `core/api_responses.py:60-149` (envelope)
- `core/models_vip_invite.py:71-72, 96-103` (two-timestamp model)

**Docs:**
- `docs/research/domains/auth/2400_auth_domain_scoping.md` §3.D + §3.5 + §7.1
- `docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md` §7 + §14 + §19
- `docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` §14 + §19.1
- `docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md` §14.2 + §14.3 + §19.1
- `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` §14 F3 + F3.5 + A3
- `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md` §15.5
- `docs/research/domains/frontend/2204_frontend_session_state_persistence_discipline_audit.md` §14 F1
- `docs/research/domains/frontend/2299_frontend_canonical_summary.md` §5.1 + §8.2 + §8.3
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 + §12 + §13

### 20.2 Grep patterns used (HEAD-verified)

| Pattern | Path | Result |
|---|---|---|
| `@token_auth_required` | `core/` | 65 across 10 files (10th = `auth_middleware.py:1` definition) |
| `api\.(get\|post\|put\|delete\|patch)\(` | `frontend/src/` | 913 across 21 files (856 defined in `api.ts`; 57 direct consumer) |
| `useQuery\|useMutation` | `frontend/src/` | 667 across 74 files |
| `fetch\(` | `frontend/src/` | 79 across 31 files (F-D-BYPASS-1) |
| `axios\.create\(` | `frontend/src/` | 1 match at `api.ts:13` (single instance) |
| `AxiosError\|axios\.isAxiosError` | `frontend/src/` | 0 matches (F-D-ENVELOPE-1) |
| `ErrorBoundary\|componentDidCatch\|getDerivedStateFromError` | `frontend/src/` | 0 matches (F-D-BOUNDARY-1 / S2201 §15.5 CONFIRMED) |
| `noAuthRedirect` | `frontend/src/` | 0 matches (option-γ greenfield) |
| `Clear-Site-Data` | `core/` | 0 matches (F-C-CSD-1 CONFIRMED-STILL-LIVE) |
| `.github/CODEOWNERS` + `CODEOWNERS` (root) + `docs/CODEOWNERS` | filesystem | ALL 3 MISSING (F-D-OWN-1) |

### 20.3 Unresolved unknowns

- **U1** Exact React Query `TError` generic adoption rate: 5 files use typed generics per Agent 4 sample; whether TError is populated in any of the 5 requires per-file read (deferred to xx99 anchor-audit if needed). Estimated ≤1% of 667 RQ sites have TError set.
- **U2** Exact non-api.ts direct consumer call-site count: 57 = 913 − 856 assumes all 856 api.ts occurrences are API-METHOD-DEFINITIONS. Some may be internal helper uses. Refinement deferred to post-arc T-slot if needed for T1 execution.
- **U3** 79 raw fetch site classification (public vs SSE vs streams vs migration-candidates): sample audit deferred to post-arc.
- **U4** Session 819 formal design doc for "selective 401 redirect" pattern: only inline comments found in api.ts:46-47; no external handoff design doc located (per Agent 2). Sufficient for HEAD verification; formal-doc-existence UNKNOWN.
- **U5** Cross-tab logout propagation via BroadcastChannel vs `storage` event: F-C-TAB-1 confirmed at HEAD; design-space deferred to Cat C post-arc T-slot (not Cat D scope per S2400 anti-scope #5).

### 20.4 Conflicts between sources (verifier-loop pre-Rigby-SIGN discipline)

Three sub-agent conflicts resolved before Rigby SIGN routing (see
`verifier_loop` frontmatter for detail):

1. **Decorator count drift.** Agent 2 said 65 uses / 10 files; Agent 3 said 9 files; Cat A baseline was 68 / 9. HEAD grep: 65 / 10 (10th = definition site at `auth_middleware.py:1`); applied uses = 64 / 9. Cat D adopts 65/10 for full transparency; text notes applied uses = 64/9.
2. **Call-site denominator ambiguity.** Agent 3 said 913 + 97; Agent 4 said 667; Agent 6 said 478. Resolved: 913 direct api.<verb>() (856 API-defs in api.ts + 57 direct consumer) + 667 useQuery/useMutation + 79 raw fetch = 803 total consumer call-sites. Cat D adopts 803 as canonical.
3. **Fetch-bypass accounting.** Agent 2 initially said "single point of enforcement"; Agents 3 + 6 correctly identified 79 raw fetch bypass. Cat D adopts 79 fetch bypass as CANONICAL (F-D-BYPASS-1 NEW HIGH FINDING).

### 20.5 Verifier-loop corrections (Rigby SIGN cycle 1 fold notes)

**Rigby SIGN cycle 1 executed 2026-07-05.** Fresh isolation pin
`pa-015448e962ad4038` minted via `session_tool.create_fresh`; 20-Q
in 4-batch × 5-Q cadence per S2201–S2403 EIGHT-consecutive tested
pattern (NINTH-consecutive 20-Q cadence application). Pin retired
at cycle 1 close via `session_tool.retire` (updated_count=6,
retired=true, previously_active=true — FIFTEENTH consecutive
dedicated fresh SIGN pin retirement in Research OS).

**Verdict:** SIGN-WITH-EDITS at MED-HIGH confidence (~0.80-0.85;
per Rigby Q20 "close cycle 1 as SIGN-WITH-EDITS at ~0.80-0.85;
no cycle 2 needed. Fold edits are crisp and non-controversial —
mostly phrasing/structure").

**Tally:** 11 AGREE + 9 STRENGTHEN across 20 Q. All 9 STRENGTHEN
folded pre-Chris-ratification. Detailed fold ledger at §20.7.

### 20.6 Fold ledger (Rigby SIGN cycle 1)

12 folds landed pre-Chris-ratification per playbook §20.6 fold
ledger discipline (extends Cat C 32-fold precedent to Cat D 12-fold
close):

| # | Q ref | Section | Fold summary |
|---|---|---|---|
| 1 | Q5 STRENGTHEN | §14.1 + §19.5 | Corrected silent-degrade rate from 18/19 (94.7%) to 17/19 (89.5%); explicitly named the two non-silent-degrade findings as **governance class** (F-D-OWN-1 CODEOWNERS absent + F-D-OWN-2 CI test-harness absent); tightened codification claim from "silent-degrade anywhere" to "auth failure handling (401/403/refresh/logout) with explicit UX + telemetry requirements" — scope-bounded to observed trigger surface. |
| 2 | Q6 STRENGTHEN | §19.1 envelope | Reframed option-γ as "fastest path to explicit failure + recoverability"; explicit reconciliation with Cat C: γ = mechanism (RQ error callbacks + boundary), β = message/UX policy (adopt Cat C "explicit re-login" semantics as default handler inside γ); γ does not preclude later (β) discriminated-union adoption at API layer. |
| 3 | Q7 STRENGTHEN | §19.1 whitelist | Renamed flag from `noAuthRedirect?: boolean` to `authHandling: 'default' \| 'suppress_redirect'` string enum (harder to misuse than boolean); required telemetry event on every `suppress_redirect` use (extends CF-D3 Group 1700 Observability roll-up). |
| 4 | Q8 AGREE + minor edit | §14.1 F-DEC-1 row | Added explicit fold note: "Cat A counts drifted; finding semantics unchanged; definition-site (auth_middleware.py:1) now included in grep denominator but excluded from applied-use count (applied uses = 64 / 9 view files at HEAD)." |
| 5 | Q9 STRENGTHEN | §19.1 envelope | Added handler-behavior discipline: MUST distinguish 401/403 vs network/offline vs 5xx. Added copy guidance: avoid time-based "Session expired" language until F-C-VIP-1 resolves; use "Sign-in required" / "Authentication required" / "Please sign in again" (no time-based claim). Preserves Cat C F-C-VIP-1 risk-gate constraint. |
| 6 | Q10 AGREE | §14.1 F-D-PA-1 row | Escalated F-D-PA-1 severity MED → HIGH. Rationale: PA is control-plane UX per CLAUDE.md workflow rules; silent-401 mid-conversation looks like agent-hang and breaks core workflow; severity reflects blast radius + user-trust impact, not just endpoint count. |
| 7 | Q14 STRENGTHEN | §2.1 NEW subsection | Added "Cat D closes vs defers" mini-table with 7 CLOSES rows (surface quantification, raw fetch inventory, sidebar gap, decision-space, VIP copy constraint, Q20 fold candidate, Cat A/B/C STILL-LIVE re-verification) + 8 DEFERS rows (envelope adoption, error-boundary framework, whitelist replacement, backend logout envelope + CSD, refresh discipline, sidebar backend-revoke fix, CI + CODEOWNERS wiring, 79-fetch per-site migration). |
| 8 | Q15 STRENGTHEN | §19.2 rank-1 P0 batch | Preserved co-equal P0 contract per Cat A/B/C precedent; added tiered ordering rationale INSIDE the co-equal list. P0-A (platform-wide/whole-auth-surface): F-D-CALL-1 + F-D-BYPASS-1 + F-D-ENVELOPE-1 + F-D-BOUNDARY-1. P0-B (token lifecycle/security window): F-D-SIDEBAR-1 + F-C-REFRESH-1 + F-C-VIP-1 + F-C-CSD-1 + F-C-STORE-1. P0-C (endpoint-specific): F-CRIT-1 + F-BND-4a + F-B-CRIT-1 + F-B-CRIT-2 + F-D-WHITELIST-1. Blast-radius truth captured; co-equal contract preserved. |
| 9 | Q16 STRENGTHEN | §19.4 anchor updates | Added AU-D6 (docs/research/ARCHITECTURE_INDEX.md — add "Auth failure handling decision matrix (α/β/γ × whitelist-replacement axis)" pointer; create-if-missing) + AU-D7 (docs/topics/auth.md new per AU-D2 MUST include DOC_LIFECYCLE cross-link note — current-state vs target-state location + supersession discipline). |
| 10 | Q17 STRENGTHEN | §19.3 follow-on research queue | Added item (2b) raw-fetch classification refinement (3 axes: auth-required vs public vs metrics/health + credentials mode + response type) as prereq for item (2) migration decision. Added OPTIONAL item (7) non-401 failure envelope audit (JSON parse + network offline + timeout + aborted) so γ mechanism does not become "401-only" and miss other silent-degrade modes. |
| 11 | Q18 AGREE + micro-edit | §9 CF-D5 row | Added ⚠ BLOCKING PREREQUISITE marker to CF-D5 row + expanded description: "Cat D lean for option-γ typed-error-envelope depends on top-level ErrorBoundary wrapper existing — without R6 execution, option-γ cannot surface caught errors to user-visible UX. R6 is therefore a blocking prerequisite for γ mechanism landing, not merely a cross-arc handoff." |
| 12 | Q19 STRENGTHEN | §14.1 F-D-COCKPIT-1 row | MED severity preserved; narrative fold: "MED + repeated re-verification (Cat C → Cat D across two audits) indicates ownership-drift risk; attach to F-D-OWN-1 / F-D-OWN-2 governance remediation." Captures the signal without inflating severity. |

**All 12 folds landable pre-Chris-ratification.** Cycle 2 not
required per Rigby cycle 1 MED-HIGH confidence + all folds
non-controversial (mostly phrasing / structure per Q20 verdict).

### 20.7 Rigby SIGN cycle 1 conversation record

- **Fresh isolation pin:** `pa-015448e962ad4038` (minted via `session_tool.create_fresh` at S2404 SIGN open 2026-07-05)
- **Cadence:** 4-batch × 5-Q = 20 Q (matches S2201–S2403 EIGHT-consecutive tested pattern; NINTH application)
- **Batch 1 (headlines + Q20 fold candidate):** 4 AGREE + 1 STRENGTHEN (Q5)
- **Batch 2 (decision-space + inheritance):** 2 AGREE + 3 STRENGTHEN (Q6 + Q7 + Q9 + Q10 minor)
- **Batch 3 (maturity + governance + acceptance):** 3 AGREE + 2 STRENGTHEN (Q14 + Q15)
- **Batch 4 FINAL (anchor + cross-arc + close):** 2 AGREE + 3 STRENGTHEN (Q16 + Q17 + Q18 minor + Q19)
- **Pin retirement:** cycle 1 close via `session_tool.retire` (updated_count=6, retired=true, previously_active=true — FIFTEENTH consecutive dedicated fresh SIGN pin retirement in Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299 ten prior xx99 + S2400 parent-scoping-light-SIGN + S2401 Cat A + S2402 Cat B + S2403 Cat C + this cycle)
- **Wrapper handling:** `tools/pa_local.sh:280` swapped to SIGN pin during cycle 1; RESTORED to arc pin `pa-6279ead1714c4630` immediately post-retire per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails

### 20.6 Rigby SIGN cycle 1 payload structure (pre-routing plan)

Expected cadence per S2201–S2403 EIGHT-consecutive tested pattern:
**4-batch × 5-Q = 20-Q child-audit cadence** (playbook §15
stage-scoped routing).

Batch 1 (headline + finding-shape): F-D-CALL-1 + F-D-BYPASS-1 +
F-D-SIDEBAR-1 + F-D-ENVELOPE-1 + F-D-BOUNDARY-1 severity + class
+ silent-degrade-class rate.

Batch 2 (cross-arc + inheritance): Cat A F-DEC-1 drift-down
65/10 vs 68/9 baseline preservation; F-B-CRIT-2 803-scale extension
math; F-C-STORE-1 zero-drift-preservation vs F-D-SIDEBAR-1
new-finding delta.

Batch 3 (decision-space + option leans): α/β/γ × 2 (envelope +
whitelist replacement) framing; Cat D lean recommendations
(option-γ envelope + option-γ whitelist replacement) vs Cat C α/β/γ
(β explicit-re-login) intersection at CF-D7.

Batch 4 (Q20 fold + governance + close): silent-degrade codification
promotion (two-trigger threshold) evidence; CODEOWNERS F-D-OWN-1
+ CI-harness F-D-OWN-2 governance gate stance; §19.4 anchor-update
AU-D1–AU-D5 xx99 handoff.

---

**End of S2404 P4 Cat D child audit.**
