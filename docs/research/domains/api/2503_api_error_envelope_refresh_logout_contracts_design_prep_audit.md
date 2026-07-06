---
title: "API Error-Envelope + Refresh + Logout API Contracts Design-Prep Audit"
status: active
authority: research
version: v1
domain: api
arc: 2500
session_id: 2503
parent_doc: docs/research/domains/api/2500_api_domain_scoping.md
predecessor_docs:
  - docs/research/domains/api/2500_api_domain_scoping.md
  - docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md
  - docs/research/domains/api/2502_api_frontend_client_architecture_design_prep_audit.md
  - docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md
  - docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md
  - docs/research/domains/auth/2499_auth_canonical_summary.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
successor_docs:
  - docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_joint_design_prep_audit.md (planned)
  - docs/research/domains/api/2599_api_canonical_summary.md (planned)
delegates_to: []
last_verified: 2026-07-05
owner: claude (drafted S2503 v1)
head_sha_at_draft: ee7cc0a01812c737bc28798250c100f9cc74d812
verifier_loop: |
  v1 (2026-07-05, S2503): drafted per playbook §11.2 20-section child-audit template
  TWENTY-SECOND-consecutive application after S1301 + S1401 + S1501 + S1601 + S1701
  + S1801 + S1901 + S2001 + S2101 + S2102 + S2103 + S2104 + S2201 + S2202 + S2203
  + S2204 + S2401 + S2402 + S2403 + S2404 + S2501 + S2502 twenty-one prior. **Codification
  language conditionality preserved (Cat B §20.7 Rigby SIGN cycle 1 batch 4 Q19
  fold precedent):** 22-consecutive stable-shape indicates continued strong stability
  signal; promotion to TEMPLATE-CANONICAL requires xx99 / Chris trigger satisfaction
  beyond mere repetition. Cat C does NOT self-codify.

  6-parallel-Explore-agent sweep executed pre-draft per playbook §13 (Agent 1
  Models + Persistence — envelope shape candidates + refresh model + logout envelope
  + storageKeys RE-VERIFY + VIP account_expires_at; Agent 2 Services + Runtime Flows
  — DRF error serialization + logout flow trace + Clear-Site-Data candidate loci +
  api.ts:48-62 SHAPE-BLIND interceptor RE-VERIFY + refresh flow absence + PA/Mobile
  cascade absence; Agent 3 APIs + Tools + Tasks + Commands — logout endpoint
  inventory + refresh absence + candidate spec-space + envelope adoption counts +
  PA tools + Celery task absence; Agent 4 Integrations + Cross-Domain — S2501 F6
  4-shape 401 RE-VERIFY + S2502 F3 interceptor RE-VERIFY + S2403 F-C-STORE-1
  15-surface RE-VERIFY + S2404 F-D-CALL-1 803 downstream RE-VERIFY + 6 cross-arc
  handoff surfaces + F-C-VIP-1 risk-gate; Agent 5 Documentation + Prior Research —
  6 predecessor summaries + 3 topic docs + 3 anchor docs + 2 handoff docs + 7
  CF-C1-CF-C7 flags + MODERATE-with-gaps coverage verdict; Agent 6 Drift + Debt +
  Ownership + Maturity — α/β/γ envelope maturity + α/β/γ whitelist-replacement
  maturity + 4 finding statuses + CODEOWNERS 100% assigned + 5-dim maturity table
  + zero-drift matrix).

  Parent-Claude verifier-loop applied per playbook §14 pre-Rigby-SIGN with SEVEN
  sub-agent conflicts resolved (see §20.5). See §20.1 files inspected.

  Rigby SIGN cycle 1 executed 2026-07-05 (PENDING at draft time; TWENTIETH-consecutive
  dedicated fresh SIGN pin candidate `pa-b19aa931a54a436a`; ELEVENTH-consecutive
  4-batch × 5-Q cadence candidate; fold ledger + verdict populated post-cycle at
  §20.6.2 + §20.6.1).
---

# API Error-Envelope + Refresh + Logout API Contracts Design-Prep Audit

## 1. Executive Summary

**Boundary note (Cat C — Rigby SIGN cycle 1 Q1 STRENGTHEN fold):** This section **enumerates** co-existing contracts at HEAD, **collects evidence**, and **defers** all design selection (α/β/γ), envelope-shape source-of-truth decisions, refresh endpoint necessity, and Clear-Site-Data emission locus to the S2599 xx99 Chris-D verdict. Any "should / need / require / recommend" phrasing anywhere in this document is out of scope and treated as drift.

**Non-goals (Cat C):**
- Prescribe a unified envelope shape.
- Propose refresh endpoint semantics or schema.
- Mandate interceptor behavior or replacement.
- Select logout header emission policy or locus.
- Reassign remediation ownership across arcs.

**Cat C boundary posture (mirror Cat A + Cat B non-prescription discipline; playbook §14 evidence-only, §16 draft-first):** this document ENUMERATES the CONTRACT surface for four distinct-but-intersecting API concerns — typed-error-envelope shape, refresh endpoint semantics, logout response envelope + Clear-Site-Data emission, and logout-cleanup coordination — collects HEAD-verified boundary evidence, and hands Chris-D-verdict-request evidence to S2599 xx99 close. Cat C does NOT prescribe α/β/γ mechanism selection, does NOT propose specific endpoint schemas, does NOT recommend header emission specs, and does NOT authorize storageKeys cleanup policy. All "recommendations" in §19 are non-prescriptive evidence prompts for Chris-D-verdict at xx99.

**HEAD baseline at `ee7cc0a0`** (verified at draft time via `git rev-parse HEAD`):

- **F-C-REFRESH-1 RE-VERIFIED ABSENT** at HEAD (S2403 baseline preserved). Zero session-token refresh endpoint in `core/urls.py` or `core/auth_views*.py`. Grep for `refresh|renew_token` in auth surface returns 6 non-auth matches (all for `refresh_token` OAuth external, `refresh_agent_discovery`, `refresh_project_spiders`). **Zero-delta 2 sessions** (S2403 close 2026-07-03 → S2503 open 2026-07-05).
- **F-C-CSD-1 RE-VERIFIED ZERO EMISSION** at HEAD (S2403 baseline preserved). Grep for `Clear-Site-Data` returns 21 total matches; **zero in production code** — matches confined to docs (`docs/topics/auth.md:92-93`, audit docs, handoffs), scratch files (`.claude/scratch/sign_batch_*.txt`, `.claude/scratch/ratification_card_s2403.txt`), and `tools/pa_local.sh:28,36,46` comments. Both logout views return `Response()` with no header emission. **Zero-delta 2 sessions.**
- **F-C-STORE-1 RE-VERIFIED 6.7% DECLARED-CLEANUP RATE** at HEAD (S2403 §14.2 baseline preserved). 15 client-side persistence surfaces enumerated at HEAD; 1 CLEAN (`auth-storage` functional-null-state per S2204 F6) + 3 PARTIAL (`pa-dock-state` incomplete field-list, `pipeline_dismissed_${workspaceId}` workspace-change cleanup not logout, `podcast_voice_profile_id` change-cleanup not logout) + 11 NO-CLEANUP. **Zero-delta 2 sessions on key names** (line-drift observed on 3 surfaces per §14.2 delta notes; key names identical).
- **F-C-VIP-1 RE-VERIFIED DECLARED-BUT-NOT-ENFORCED** at HEAD (S2403 baseline preserved). `VIPInvite.account_expires_at` field exists at `core/models_vip_invite.py:72` with `_default_account_expires` = 14 days default; zero runtime enforcement (grep for `account_expires_at__lt`, `account_expires_at <`, or `account_expires_at.__lt` in `core/` returns zero matches); zero periodic cleanup task. **Risk-gate constraint preserved:** F-C-VIP-1 remains a shipping prerequisite for any expiry-signal-bearing UX regardless of α/β/γ choice.
- **F3 SHAPE-BLIND interceptor RE-VERIFIED IDENTICAL** at HEAD (S2502 §14.3 baseline preserved). `frontend/src/lib/api.ts:48-62` reads only `error.response?.status === 401` (not body) and branches solely on `url.includes('/auth/') || url.includes('/login')`. All four S2501 F6 shape families flow through the SAME non-auth reject-and-console.warn branch. **Zero-delta 5 sessions since S2404 baseline.**

**Cat C α/β/γ typed-error-envelope decision-space maturity: EXPERIMENTAL** (Cat C classification per §13 maturity table). QueryClient container present at `frontend/src/main.tsx` (Cat C evidence-only; adoption not confirmed at ~5-10 hook config sites). Zero `useQuery.*onError` handler adoption. Zero `QueryClient.*defaultOptions.*onError` global default. Zero `ErrorBoundary`, `componentDidCatch`, or `getDerivedStateFromError` matches in `frontend/src/**` (S2404 F-D-BOUNDARY-1 + S2502 R6 IDENTICAL at HEAD). Zero custom typed-exception classes (`UnauthorizedError`, `PermissionError`, `ValidationError`, `ServerError`). Zero `Result<T, E>` or discriminated-union pattern adoption.

**Cat C whitelist-replacement α/β/γ maturity: EXPERIMENTAL** (Cat C classification). Zero `AUTH_REDIRECT_ENDPOINTS`, zero `X-Suppress-Auth-Redirect` backend header, zero `authHandling` per-api-module string enum. Current implementation is the S2502 F3 SHAPE-BLIND substring match — **NONE of the three α/β/γ options is deployed at HEAD**.

**Cat C mission preservation (Cat A + Cat B seam boundary):** Cat A S2501 CLOSED the DECLARATION-side (16 `@extend_schema` decorators + 4 co-existing 401 shape families + drf-spectacular INSTALLED-CONFIGURED-DECORATED-DISCONNECTED); Cat B S2502 CLOSED the CONSUMER-side ARCHITECTURE (SHAPE-BLIND interceptor + 803 consumer surface + 18 DEAD-CANDIDATE + 79-raw-fetch bypass + 0 codegen + 0 ErrorBoundary). **Cat C is the ERROR-CONTRACT + LIFECYCLE-CONTRACT layer** that lives between them: the error-envelope shape is what backend emits (Cat A domain) AND what frontend consumes (Cat B domain), and the refresh + logout contracts are the lifecycle transitions that both sides observe. Cat C hands Chris-D-verdict-request evidence to S2599 xx99 for α/β/γ intersection resolution with Cat D S2504 (permission-floor registry + REST↔WS T7 joint).

### 1.1 Denominator Contract + Sampling Completeness (Rigby SIGN cycle 1 Cat B Q9 STRENGTHEN precedent extension)

For every rate-claim in this document, unit-of-analysis + scope + verification-method disclosed inline. Load-bearing denominators reused at HEAD:

| Metric | Denominator | Scope | Verification Method |
|---|---|---|---|
| Silent-401 rate | 803 consumer call-sites (S2404 canonical: 57 direct + 667 useQuery/useMutation + 79 raw fetch) | `frontend/src/**` excluding `.js/.jsx` (verified absent at HEAD per S2203 baseline preservation assumption) | S2502 §20.4 grep table RE-VERIFIED at HEAD by Agent 4 |
| storageKeys cleanup rate | 15 total persistent-state surfaces (S2204 F1 baseline preserved) | `frontend/src/**` grep on `persist(` + `localStorage.setItem` + templated keys | S2403 §14.2 table RE-VERIFIED at HEAD by Agent 4 (15/15 keys matched; line-drift on 3 surfaces) |
| Session-lifecycle observability rate | 21 lifecycle-observability loci (S2403 §14.3 baseline preserved) | Auth surface + persistence surface + WS auth surface | S2403 §14.3 table RE-VERIFIED at HEAD by Agent 2 |
| 401 shape family count | 4 (S2501 §14.6 F6 canonical) | `core/**` grep on 401 emission sites | S2501 §14.6 F6 RE-VERIFIED at HEAD by Agent 1 + Agent 3 + parent-Claude reads |
| Envelope adoption rate | 14 APIResponseEnvelope.* sites / total-endpoints-slice UNKNOWN (denominator not established at Cat C scope) | `core/**` grep on `APIResponseEnvelope.*` | Agent 3 grep at HEAD; total-endpoint denominator deferred to xx99 close artifact per S2500 §6 P-1 |
| Interceptor coverage | 90.2% (724/803 = interceptor-routed; 79 raw fetch bypass) | Same as silent-401 rate scope | S2404 §14.5 canonical; RE-VERIFIED at S2502 + S2503 by Agent 4 |
| CODEOWNERS assignment rate for Cat C surface | 100% assigned to `@clwest` (6 of 6 Cat C files declared) | `./CODEOWNERS` file at repo root; Cat C files: `core/api_responses.py`, `core/auth_views.py`, `core/auth_views_enhanced.py`, `frontend/src/lib/api.ts`, `frontend/src/stores/authStore.ts`, `frontend/src/App.tsx` | Agent 6 direct read of `./CODEOWNERS` at HEAD |
| 401 shape-family distribution (Rigby SIGN cycle 1 Q2 STRENGTHEN fold — Metric 8) | 4 families A/B/C/D per §14.1 F1 (S2501 §14.6 F6 canonical); per-family adoption count DEFERRED to xx99 close artifact per S2500 §6 P-1 discipline | All authenticated endpoints capable of returning 401 (denominator NOT established at Cat C scope); numerator = family-count only | Grep + spot-check response bodies in each cited view/middleware per §14.1 evidence |
| Interceptor shape-dependence rate (Rigby SIGN cycle 1 Q2 STRENGTHEN fold — Metric 9 optional) | 0/1 = 0% (SHAPE-BLIND; single branch on status + URL substring; zero branches conditioned on response body shape) | `frontend/src/lib/api.ts:43-62` response interceptor | api.ts direct read + grep on `.data.detail\|.data.message\|.data.error` usage in `frontend/src/**` |

**Sampling completeness note (Rigby SIGN cycle 1 Cat B Q10 STRENGTHEN precedent extension):** Cat C used 6-parallel-Explore sweeps + targeted samples per playbook §13; Cat C did NOT perform exhaustive Cartesian grep. Specifically:

- **Exhaustive verified:** api.ts:48-62 interceptor direct read (parent-Claude); logout view direct read (`core/auth_views.py:84-94`, `core/auth_views_enhanced.py:539-556`); `core/api_responses.py` full-file read (parent-Claude); `refresh|renew_token` grep in `core/urls.py` + `core/auth_views*.py`; `Clear-Site-Data` grep repo-wide + code-only filter; 15-surface storageKeys per-key file:line grep (Agent 4); CODEOWNERS direct read (Agent 6).
- **Targeted (NOT exhaustive):** 4-shape 401 family per-emission-site sample (Agent 1 + Agent 4 sampled 4 representative sites per family; not exhaustive per-endpoint audit); envelope adoption counts (Agent 3 grep on `APIResponseEnvelope.*` + `api_helpers.api_success/api_error` + bare-DRF sample; not per-endpoint verified).
- **Not-in-scope-verified:** exact per-shape-family endpoint count for each of the 4 401 shape families (deferred to xx99 as design-input evidence); per-hook `useQuery.*onError` adoption rate across 667 sites (~0-5% sampled per Agent 6; formal audit deferred); per-endpoint drf-spectacular retrofit surface (Cat A S2501 scope; not re-derived at Cat C).

Macro zero-drift metrics + verifier-loop conflict resolution (§20.5) reduce but do NOT eliminate miss risk. Cycle 2 SIGN NOT scheduled at draft time (pending Rigby verdict).

### 1.2 Do Not Misread (Rigby SIGN cycle 1 Cat B Q17 STRENGTHEN precedent extension)

Two anti-misread guardrails for downstream readers:

- **α/β/γ label independence.** Cat C session-lifecycle α/β/γ (from S2403 §19.1) + Cat D typed-error-envelope α/β/γ (from S2404 §19.1) + Cat D whitelist-replacement α/β/γ (from S2404 §19.1) are THREE distinct decision spaces that share the α/β/γ label for symmetry. Reader MUST NOT couple selections across the three spaces — mixed combinations are valid (e.g., Cat C β explicit re-login + Cat D γ RQ+ErrorBoundary + Cat D γ per-api-module enum). xx99 close synthesizes the three but does not pre-couple them. Rigby SIGN Q6 fold at S2404 §19.1 already established: **γ (Cat D typed-error-envelope) = mechanism; β (Cat C explicit re-login) = message/UX policy nested inside γ**. This nesting is a specific reconciliation, NOT a general coupling.
- **F-C-REFRESH-1 ABSENT does NOT imply "refresh should be added."** The finding statement is "no session-token refresh endpoint exists at HEAD." Cat C does NOT recommend addition. Refresh endpoint contract decision is Chris-D-verdict-request evidence for xx99 close, jointly with Cat C α/β/γ session-lifecycle decision (α silent-refresh REQUIRES refresh endpoint; β explicit re-login does NOT; γ hybrid requires it). Cat C enumerates trade-offs; Chris ratifies at xx99.

---

## 2. Domain Purpose

**Playbook §9 canonical Q1 — What problem does this domain solve?**

The API error-envelope + refresh + logout contracts domain answers: **"How does the backend communicate authentication + lifecycle failures to the frontend, and how does the frontend recover?"** Concretely, Cat C spans the intersection of three surfaces at HEAD:

1. **Error-envelope surface** — the response shape returned by any endpoint when the request fails at the auth boundary (401 unauthorized), the authorization boundary (403 forbidden), the validation boundary (422 / 400), or the server boundary (5xx). At HEAD this surface is HETEROGENEOUS — 4 co-existing shape families per S2501 §14.6 F6 — with NO SoT contract declaration.
2. **Refresh surface** — the mechanism by which a client extends a session/token lifetime without re-authenticating. At HEAD this surface is ABSENT — no session-token refresh endpoint, no client retry-with-refresh logic, no rotation-on-use policy. Implicit contract: token is permanent until explicit `logout` or password-change/reset.
3. **Logout surface** — the coordinated multi-side transition that occurs when a user ends their session. At HEAD this surface is FRAGMENTED — server-side has 2 logout endpoints emitting different response shapes (`{'detail': ...}` vs `{'message': ...}`); frontend Sidebar does NOT call backend logout at all (F-D-SIDEBAR-1); Clear-Site-Data emission is ZERO; storageKeys cleanup rate is 6.7% declared; PA conversation retire + Mobile push token revoke + cross-tab coordination are all ABSENT.

**Playbook §9 canonical Q2 — What are the boundaries?**

Cat C boundary (upstream): the error-envelope shape + refresh discipline + logout mechanism at the API CONTRACT layer. What flows on the wire between backend and frontend.

Cat C boundary (downstream): does NOT include (a) backend implementation of specific endpoints (Cat A + post-arc T-slot); (b) frontend consumer-side path adoption (Cat B); (c) permission-floor policy at endpoint (Cat D S2504); (d) UX copy or component design (Cat C hands typed-error UX policy to Group 2200 R6 owner; hands session-lifecycle UX to Group 2600 PA cross-arc); (e) observability + telemetry (Group 1700 hands off).

Cat C role: **surface the CONTRACT decision-space** so downstream owners can execute.

---

## 3. Canonical Entry Points

**Playbook §9 canonical Q3 — What are the canonical entry points?**

### 3.1 Backend entry points (verified at HEAD `ee7cc0a0`)

| Surface | File:Line | Purpose | Response Envelope Shape |
|---|---|---|---|
| Basic logout endpoint | `core/urls.py:2185` route → `core/auth_views.py:84-94` view | `POST /api/v1/auth/logout/` — delete token; return message | `Response({'detail': 'Successfully logged out'})` (200) OR `Response({'detail': 'Logout successful'})` (200 on exception) |
| Enhanced logout endpoint | `core/urls.py:2196` route → `core/auth_views_enhanced.py:539-556` view | `POST /api/v1/auth/logout-enhanced/` — delete token with `IsAuthenticated` guard | `Response({'message': 'Logged out successfully'})` (200, both success + exception branches) |
| Django accounts/logout | `core/urls.py:1626` route → Django `logout()` + redirect `/login` | `POST accounts/logout/` — Django built-in session termination | Redirect only (no response body); Django default behavior |
| APIResponseEnvelope helpers | `core/api_responses.py:15-234` | Standardized response envelope class + convenience functions | `{"success": bool, "error": {"code": str, "message": str}}` or `{"success": true, "data": ...}` |
| DRF standard Response | Various `core/**/*.py` | Bare DRF `Response({'detail': ...}, status=...)` pattern | `{"detail": "..."}` |
| Bare JsonResponse dict | Various `core/views_*.py` | Manual `JsonResponse({'success': False, 'error': str}, status=401)` pattern | `{"success": false, "error": "..."}` (unstructured error field) |

**F-C-REFRESH-1 explicit absence:** No refresh endpoint at HEAD. The nearest paths are:
- `core/urls.py:747` `refresh_token` — imported as symbol for oauth-refresh at `:2055` `/api/distribution/oauth/<str:platform>/refresh/` (third-party OAuth external, NOT session-token)
- `core/urls.py:1345, 3071` `refresh_agent_discovery` — agent-discovery cache refresh (NOT session-token)
- `core/urls.py:1589, 1925` `refresh_project_spiders` — project spider inventory refresh (NOT session-token)

Grep for `TokenRefreshView`, `SlidingToken`, `SimpleJWT`, `RefreshToken` across `core/**/*.py`: **zero matches** (Agent 1 + Agent 3 confirmed).

### 3.2 Frontend entry points (verified at HEAD)

| Surface | File:Line | Purpose |
|---|---|---|
| Silent-401 response interceptor | `frontend/src/lib/api.ts:43-62` | SHAPE-BLIND — status-only + URL-substring branch. `useAuthStore.getState().logout() + window.location.href='/login'` for auth-endpoint 401; `console.warn(...)` for non-auth 401 |
| Auth token request interceptor | `frontend/src/lib/api.ts:16-38` | Attaches `Authorization: Token <token>` header from `useAuthStore` |
| `authApi.logout()` API client method | `frontend/src/lib/api.ts:76` | `api.post('/v1/auth/logout/')` — bare-call, no response typing |
| `authStore.logout()` Zustand action | `frontend/src/stores/authStore.ts:34-39` | Clears `token`, `user`, `isAuthenticated` from persisted store; sets Zustand persist auth-storage to null-record |
| Sidebar user-menu logout onClick | `frontend/src/components/layout/Sidebar.tsx:356` | `syncUser(null); logout()` — **F-D-SIDEBAR-1 RE-VERIFIED**: does NOT call `authApi.logout()` (backend token revoke) |

### 3.3 Error-envelope emission loci (evidence for design-space; not exhaustive per §1.1)

| Locus | File:Line | Emission Pattern | Shape Family |
|---|---|---|---|
| DRF-auth-failed at middleware | `core/auth_middleware.py:79, 633, 658` | `api_unauthorized(...)` calls (invokes `APIResponseEnvelope.unauthorized()`) | Family B: `{"success": false, "error": {"code": "authentication_required", "message": ...}}` |
| Basic logout success | `core/auth_views.py:91` | `Response({'detail': 'Successfully logged out'})` | Family A: `{"detail": "..."}` DRF default |
| Basic logout exception-swallow | `core/auth_views.py:94` | `Response({'detail': 'Logout successful'})` | Family A: `{"detail": "..."}` |
| Basic login-failure 401 | `core/auth_views.py:79-81` | `Response({'detail': f'Invalid credentials...'}, status=401)` | Family A: `{"detail": "..."}` |
| Basic current_user unauth | `core/auth_views.py:123-126` | `Response({'detail': 'Not authenticated'}, status=401)` | Family A: `{"detail": "..."}` |
| Enhanced logout success | `core/auth_views_enhanced.py:554` | `Response({'message': 'Logged out successfully'})` | Family C: bare DRF dict with `{message: str}` key (distinct from Family A `detail` key) |
| Legacy JsonResponse 401 | `core/views_deploy.py:21, 79`, `core/views_agent_learning.py:2299, 2373`, `core/views_auto_fix.py:26`, `core/views_business_ideas.py:142` | `JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)` | Family D: `{"success": false, "error": "..."}` (unstructured error field; not nested `error.code + error.message`) |

**F-C-CSD-1 explicit absence:** All logout emission loci above return bare `Response(...)` with NO `response['Clear-Site-Data'] = ...` or equivalent header emission. Grep for `Clear-Site-Data` in code-only paths (`--glob '!*.md'`) returns matches only in `tools/pa_local.sh` (audit-tracker comments, lines 28, 36, 46) + `.claude/scratch/` audit scratch files. **Zero production-code emission.**

**Basic vs Enhanced key-name DRIFT (Cat C new observation):** Basic logout emits `{"detail": ...}` (Family A); Enhanced logout emits `{"message": ...}` (Family C-adjacent). Both endpoints share domain semantics (logout success) but return **different top-level keys** — a Cat A F1-adjacent drift at the SoT layer. Cat C evidence-collects; Cat A owns unified-envelope design.

---

## 4. Major Models

**Playbook §9 canonical Q4 — What are the major models?**

### 4.1 DRF Token model (session-token surface)

- **Source:** `rest_framework.authtoken.models.Token` (third-party, not repo-local).
- **Fields at HEAD:** `key` (40-char string), `user` (OneToOne FK to `UnifiedUser`), `created` (DateTimeField). **No `expires_at` field** (Agent 1 verified via `Token.objects` usage at `core/auth_views.py:53` — `Token.objects.get_or_create(user=user)` with zero expiry-related kwargs; no wrapper table extending Token with expiry field found in `core/**/*.py`).
- **Cat A same-issue lineage:** F-TOKEN-1 (S2401 canonical). Cat C classifies under lifecycle plane as F-C-REFRESH-1 (contract-absent class); both IDs preserved for cross-arc traceability.

### 4.2 VIPInvite lifecycle model (risk-gate)

- **Source:** `core/models_vip_invite.py`.
- **Fields at HEAD (verified by Agent 1 + Agent 6):**
  - `token_expires_at` (72h default) — **ENFORCED** at `core/views_vip_invite.py:151-156` via `is_valid` property at `core/models_vip_invite.py:95-103` (checks `token_expires_at > now`).
  - `account_expires_at` (14d default via `_default_account_expires()` at `:26-27`) — **NOT ENFORCED**. Model field exists; API response serializes it (`views_vip_invite.py:74, 161, 213` all call `.isoformat()`); zero runtime check on token-use or invitation-redemption paths.
- **Grep at HEAD for enforcement candidates:** `account_expires_at__lt`, `account_expires_at <`, `account_expires_at.__lt`, `account_expires_at.gt` in `core/**/*.py` = **zero matches** (Agent 1 verified).
- **Grep at HEAD for periodic cleanup:** `VIPInvite` in `core/tasks*.py` + `core/celery.py` + `beat_schedule` references = **zero cleanup tasks** (Agent 3 verified).
- **Risk-gate classification (F-C-VIP-1 RE-VERIFIED):** DECLARED-FICTIONAL. Cat C evidence-collects for §19 risk-gate constraint preservation.

### 4.3 MobilePushToken lifecycle model (cross-arc)

- **Source:** `core/models_mobile.py`.
- **Field at HEAD:** `revoked_at` (DateTimeField, nullable). Field exists; zero logout-path set-site (Agent 2 grep: `MobilePushToken.*revoked_at.*=` in `core/auth_views*.py` = 0 matches).
- **Cross-arc handoff:** CF-C4 to Group 2300 Mobile (S2403 §19 preserved; Cat C RE-VERIFIED zero enforcement at HEAD).

### 4.4 Zustand persist stores (client-side session state model)

3 stores at HEAD (verified by Agent 4):

| Store | File:Line | Persist Key | Cleanup on Logout? |
|---|---|---|---|
| `authStore` | `frontend/src/stores/authStore.ts:43-51` (persist config); `:34-39` (logout action) | `auth-storage` | **YES** (CLEAN; functional-null-state per S2204 F6) |
| `navigationStore` | `frontend/src/stores/navigationStore.ts:98-105` | `navigation-store` | **NO** (`clearHistory` action exists at `:96-97` but NEVER called on logout — S2204 F8) |
| `paStore` | `frontend/src/stores/paStore.ts:395-431` (v3+migrate); `:182-194` (syncUser action) | `pa-dock-state` | **PARTIAL** (`syncUser(null)` wipes messages/conversations/currentInput; does NOT wipe `activeTool`/`recentTool`/`seenSeqs`/`agentCompletionQueue`/`seenCompletions`/`recentAgentCompletion` per S2204 F7) |

### 4.5 Direct localStorage surfaces (client-side session state model, non-Zustand)

12 direct localStorage surfaces at HEAD (Agent 4 verified 12 of 12 key matches; line-drift observed on 3 surfaces per §14.2 delta notes below). See §14.2 table for full inventory.

### 4.6 APIResponseEnvelope (contract model)

- **Source:** `core/api_responses.py:15-204`.
- **Shape at HEAD (Agent 1 + parent-Claude full-file read):**
  - Success: `{"success": true, "data": ..., "message": "..."}` + optional `meta` (pagination) at `:37-51`.
  - Error: `{"success": false, "error": {"code": str, "message": str}}` + optional `error.details` at `:72-98`.
  - Convenience `.unauthorized()` at `:143-149` returns 401 with `error.code="authentication_required"`.
  - Convenience `.forbidden()` at `:151-158` returns 403 with `error.code="access_denied"`.
  - Convenience `.not_found()` at `:160-167` returns 404 with `error.code="not_found"`.
  - Convenience `.validation_error()` at `:169-180` returns 422 with `error.code="validation_error"`.
  - Convenience `.rate_limited()` at `:182-188` returns 429 with `error.code="rate_limited"`.
  - Convenience `.server_error()` at `:190-204` returns 500 with `error.code="server_error"`.
- **Adoption at HEAD (Agent 3 grep):** ~14 `APIResponseEnvelope.*` call sites + ~30+ `api_helpers.api_success/api_error` wrapper adoptions (predominantly in `core/views_ab_testing.py`).
- **Non-adoption evidence:** Neither logout view uses `APIResponseEnvelope` — both use bare `Response(dict)`.

---

## 5. Major Services

**Playbook §9 canonical Q5 — What are the major services?**

### 5.1 DRF exception handling service (implicit)

- **DRF settings at HEAD (verified by Agent 2 read of `core/settings.py:645-669`):**
  - `DEFAULT_AUTHENTICATION_CLASSES`: `[core.mobile_authentication.MobileTokenAuthentication, core.mobile_authentication.CsrfExemptSessionAuthentication]`.
  - `DEFAULT_PERMISSION_CLASSES`: `[rest_framework.permissions.IsAuthenticated]`.
  - `EXCEPTION_HANDLER`: **NOT EXPLICITLY DEFINED** in `REST_FRAMEWORK` dict — defaults to DRF's built-in `exception_handler` (returns `{"detail": ...}` for `AuthenticationFailed`/`PermissionDenied`/`NotAuthenticated`; returns `{"detail": ..., "field_name": [errors]}` for `ValidationError`).
- **Cat C observation:** the absence of a custom `EXCEPTION_HANDLER` is the mechanism by which Family A `{"detail": ...}` shape dominates the 401/403 surface even at endpoints that could opt into Family B via `APIResponseEnvelope`. Any Cat C α/β/γ envelope mechanism that requires shape uniformity would either (a) set a custom `EXCEPTION_HANDLER` at REST_FRAMEWORK settings level, or (b) intercept at middleware level. Cat C enumerates; xx99 Chris-D-verdict.

### 5.2 Logout view functions (basic + enhanced)

- **`core/auth_views.py:84-94`** `logout_view`:
  1. `@api_view(['POST'])` decorator (line 84); NO `@permission_classes(...)` decorator → falls to DRF `DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]` global default.
  2. `try:` block at `:89`.
  3. `request.user.auth_token.delete()` at `:90` — deletes token row.
  4. `return Response({'detail': 'Successfully logged out'})` at `:91` — 200 OK.
  5. `except Exception as e:` at `:92` — swallow all exceptions.
  6. `logger.warning(f"Token deletion failed during logout: {e}")` at `:93`.
  7. `return Response({'detail': 'Logout successful'})` at `:94` — silent-200.
- **Cat A F-C-LOGOUT-1 same-issue lineage (S2403):** basic logout NO `@permission_classes` decorator explicit; DEFAULT_PERMISSION_CLASSES fallback catches; silent-200 on token-delete exception. Cat C RE-VERIFIED at HEAD — the code has NOT been changed.
- **`core/auth_views_enhanced.py:539-556`** `logout_enhanced_view`:
  1. `@api_view(['POST'])` decorator (line 539).
  2. `@permission_classes([IsAuthenticated])` decorator (line 540) — explicit guard.
  3. `try:` block at `:545`.
  4. `request.user.auth_token.delete()` at `:547`.
  5. `except Exception as _e:` at `:548` — swallow with degraded-warning log at `:549-552`.
  6. `return Response({'message': 'Logged out successfully'})` at `:554` — silent-200 on both success + exception branches.
- **Cat A F-C-LOGOUT-2 same-issue lineage (S2403):** enhanced logout silent-200 on token-delete exception. Cat C RE-VERIFIED at HEAD.

### 5.3 Middleware chain (potential Clear-Site-Data emission locus)

- **Middleware inventory at HEAD (Agent 2 grep):**
  - `core/middleware.py:15-71` — `DisableCSRFForAuthEndpoints` — auth-path CSRF bypass; does NOT touch response headers.
  - `core/middleware.py:74-100+` — `RangeRequestMiddleware` — media range requests only.
  - `core/middleware_error_capture.py:13-52` — `RequestErrorCaptureMiddleware` — 500 error capture; does NOT touch auth responses.
- **Clear-Site-Data emission candidate loci (Cat C evidence for design-space, not prescription):**
  1. Locus (a) — logout view direct `response['Clear-Site-Data'] = ...` per-endpoint. Pros: minimal touch. Cons: 2 logout views (basic + enhanced) both need patch; forgetting either creates drift.
  2. Locus (b) — new middleware gated on logout URL. Pros: centralized. Cons: new middleware registration; per-request URL check overhead on non-logout paths.
  3. Locus (c) — new `APIResponseEnvelope.logout_response()` helper. Pros: reusable. Cons: requires refactor of both logout views to opt in.

Cat C enumerates 3 loci per Agent 2 evidence; Chris-D-verdict on locus selection at xx99. Cat C does NOT prescribe locus.

### 5.4 Zustand persist middleware service (client-side)

- `frontend/src/stores/authStore.ts:43-51` — `persist(...)` middleware wraps store creation; `partialize` at `:45-49` filters persisted fields; `key: 'auth-storage'` at `:44`.
- Behavior at logout (Agent 6 confirmed): `logout()` sets `token: null, user: null, isAuthenticated: false`; Zustand persist detects mutation and writes null-record to `localStorage['auth-storage']`. **Functional-null-state per S2204 F6 — the record is not `removeItem`'d, but the values are null.**

### 5.5 PA session_tool service (cross-arc; not lifecycle-owned)

- `core/services/pa_tool_schemas.py:4716-4750` — `session_tool` PA-tool for conversation session management (`whoami`, `retire`, `set_active`).
- **NOT related to Django auth session** (Agent 3 confirmed).
- **F-C-PA-CONV-1 same-issue lineage (S2403):** `session_tool.retire` is NOT called from user-logout paths (grep in `core/auth_views*.py` = 0 matches). Active PA conversation pins persist post-user-logout. Cat C RE-VERIFIED zero-invocation at HEAD.

---

## 6. Major APIs and Interfaces

**Playbook §9 canonical Q6 — What are the major APIs and interfaces?**

### 6.1 Logout endpoint inventory at HEAD (verified by Agent 3)

| Path | HTTP Method | View Function | Permission | Response Shape (200) |
|---|---|---|---|---|
| `/api/v1/auth/logout/` | POST | `core.auth_views.logout_view` | Global default `[IsAuthenticated]` per REST_FRAMEWORK settings (no explicit decorator) | `{"detail": "Successfully logged out"}` OR `{"detail": "Logout successful"}` (exception swallow) |
| `/api/v1/auth/logout-enhanced/` | POST | `core.auth_views_enhanced.logout_enhanced_view` | Explicit `@permission_classes([IsAuthenticated])` | `{"message": "Logged out successfully"}` (both success + exception swallow) |
| `accounts/logout/` | POST | Django default `logout()` + redirect (`core/urls.py:1626` inline lambda) | Django AuthenticationMiddleware default | Redirect to `/login` (no JSON body) |

**Frontend `authApi.logout()`** at `frontend/src/lib/api.ts:76` targets `/v1/auth/logout/` (basic endpoint), NOT `/v1/auth/logout-enhanced/`. Sidebar user-menu at `Sidebar.tsx:356` does NOT invoke `authApi.logout()` at all (F-D-SIDEBAR-1).

### 6.2 Refresh endpoint at HEAD

**ABSENT.** Zero session-token refresh endpoint (Agent 3 verified). Non-auth `refresh_*` endpoints exist for spider/oauth/agent-discovery cache refresh only.

**Candidate refresh endpoint spec-space (Cat C evidence-only for design-space; NOT prescription):**

Following existing auth-endpoint conventions at HEAD, if a refresh endpoint were added (Chris-D-verdict at xx99), plausible shape:

- URL path: `/api/v1/auth/refresh/` (matches `/api/v1/auth/login/` + `/api/v1/auth/logout/` convention).
- Method: POST.
- Body: `{"token": "<current_token>"}` OR `{"refresh_token": "<separate_refresh_token>"}` depending on rotation policy (single-token exchange vs refresh-token pair).
- Response on success: `{"token": "<new_token>", ...}` (matches `login_view` pattern) OR `{"success": true, "data": {"token": ...}}` (matches APIResponseEnvelope shape).
- Response on failure: 401 with envelope-shape-of-choice.

Cat C enumerates the shape choices; α/β/γ session-lifecycle Chris-D-verdict at xx99 determines endpoint necessity + shape.

### 6.3 Error response envelope endpoints (partial inventory; evidence for design-space)

Agent 3 grep at HEAD:

| Envelope pattern | Count | Representative examples |
|---|---|---|
| `APIResponseEnvelope.*` explicit | ~14 sites | `core/api_responses.py:15-234` definition + `core/auth_middleware.py:79, 633, 658` via `api_unauthorized(...)` |
| Bare DRF `Response({'detail': ...})` for 401 | ~6+ sites (sampled) | `core/auth_views.py:79-81, 91, 94, 124-126` |
| `JsonResponse({'success': False, 'error': str})` for 401 | ~40+ sites (sampled; not exhaustive) | `core/views_deploy.py:21, 79`; `core/views_agent_learning.py:2299, 2373`; `core/views_auto_fix.py:26`; `core/views_business_ideas.py:142-143` |
| `api_helpers.api_success/api_error` wrapper | ~30+ sites | `core/views_ab_testing.py` (20+ sites concentrated here) |

**Denominator note:** total-endpoint denominator (S2501 F5 discovery frame) NOT re-derived at Cat C scope; per S2500 §6 P-1 deferred to xx99 close artifact. Rate claims above are ADOPTION counts, not adoption RATES (Cat C does not know the denominator per §1.1 discipline).

### 6.4 Frontend API surface (Cat B RE-VERIFIED at HEAD, Cat C boundary observation)

Cat B S2502 canonical (§14.1 F1 IDENTICAL 5-session drift-frozen preserved):

- `api.ts` = 4194 LOC, 93 apiModule exports, 47 exported interfaces, 856 method-defs internal.
- Consumer surface = 803 total (57 direct + 667 useQuery/useMutation + 79 raw fetch).
- Cat C boundary observation: EVERY consumer surface transit is a potential typed-error-envelope adoption site. Blast radius for α/β/γ mechanism = 803 (interceptor-routed subset = 724 = 90.2% per S2404 §14.5).

### 6.5 PA tools relevant to Cat C

Agent 3 verified: `session_tool` (PA conversation management; NOT Django session) is the only tool touching "session" semantics. No auth/logout/refresh/token PA tool exists at HEAD. Cross-arc CF-C2 handoff to Group 2600 PA references paStore workspace-context + session_tool.retire cascade on user logout (S2403 §19 preserved).

### 6.6 Celery tasks + management commands relevant to Cat C

Agent 3 grep at HEAD:

- Celery tasks referencing `Token`/`account_expires_at`/`revoked_at`/`Clear-Site-Data`/`logout`/`session cleanup`: **zero session-lifecycle cleanup tasks**. Non-relevant matches: Etsy/Gumroad access_token checks (`core/tasks.py:2298-2299, 2385-2386`); non-auth `expires_at` for opportunities/evidence.
- Management commands: **zero** custom `clearsessions`/`logout`/`refresh_token` commands. Django built-in `clearsessions` is available but NOT wired to Celery Beat (no PeriodicTask row).

**Cat C RE-VERIFIED F-C-VIP-1 zero-periodic-cleanup-task baseline (S2403 preserved).**

---

## 7. Runtime Flows

**Playbook §9 canonical Q7 — What are the runtime flows?**

### 7.1 Successful basic-logout flow at HEAD (Agent 2 traced)

1. Frontend: user clicks user-menu logout button at `Sidebar.tsx:356`.
2. Frontend: `setUserMenuOpen(false); syncUser(null); logout()`. **NO `authApi.logout()` call** (F-D-SIDEBAR-1).
3. Frontend `authStore.logout()` at `authStore.ts:34-39`: sets token/user/isAuthenticated to null; Zustand persist writes null-record to `localStorage['auth-storage']`.
4. Frontend: **NO cleanup of the other 14 storageKeys** (F-C-STORE-1 RE-VERIFIED at HEAD).
5. Frontend: user next-navigates (page refresh or route change).
6. On any subsequent API call, `api.ts:20-24` request interceptor reads `useAuthStore.getState().token = null`, does NOT attach `Authorization` header.
7. Backend endpoint returns 401 (per `IsAuthenticated` gate on that endpoint).
8. Frontend response interceptor at `api.ts:48-58` catches 401.
9. If URL matches whitelist (`'/auth/' || '/login'`), interceptor calls `useAuthStore.getState().logout()` + `window.location.href = '/login'`.
10. If URL does not match whitelist, interceptor calls `console.warn(...)` and rejects (SHAPE-BLIND passthrough).

**Server-side sub-flow (via `authApi.logout()` if it were called — Sidebar path skips this):**
1. Backend `POST /api/v1/auth/logout/` at `auth_views.py:84-94`.
2. `@api_view(['POST'])` decorator; DEFAULT_PERMISSION_CLASSES `[IsAuthenticated]`.
3. If authenticated: `request.user.auth_token.delete()` at `:90` deletes DRF Token row; return `Response({'detail': 'Successfully logged out'})` at `:91`.
4. If unauthenticated: `IsAuthenticated` gate rejects with 401.
5. If token-delete raises (e.g., DB error): silent-200 with `Response({'detail': 'Logout successful'})` at `:94` (Cat A F-C-LOGOUT-1 same-issue lineage).
6. **NO `response['Clear-Site-Data']`** — F-C-CSD-1 RE-VERIFIED zero-emission.
7. **NO server-side session flush** (Agent 2 verified: `logout()` from `django.contrib.auth` NOT called; Django session persists at REST endpoint until `SESSION_COOKIE_AGE` expiry).
8. **NO PA conversation retire** (F-C-PA-CONV-1); **NO MobilePushToken.revoked_at** (F-C-MOBILE-1); **NO cross-session revoke** (any OTHER active tokens for same user persist).

### 7.2 Successful enhanced-logout flow at HEAD (Agent 2 traced)

Same as 7.1 with 3 deltas:
1. `@permission_classes([IsAuthenticated])` explicit at `auth_views_enhanced.py:540` (vs implicit global default in basic).
2. Response shape at `:554`: `Response({'message': 'Logged out successfully'})` — **key is `message`, NOT `detail`** (basic vs enhanced key-name DRIFT per §3.3).
3. Both success + token-delete-exception branches converge to same response at `:554` (silent-200 preserved per Cat A F-C-LOGOUT-2 same-issue lineage).

### 7.3 401 error-envelope flow at HEAD (SHAPE-BLIND consumer)

1. Backend endpoint returns 401 with ONE of the 4 shape families:
   - Family A: `{"detail": "..."}` (DRF default via `AuthenticationFailed` or `NotAuthenticated`).
   - Family B: `{"success": false, "error": {"code": "authentication_required", "message": "..."}}` (via `APIResponseEnvelope.unauthorized()` at explicit-envelope-adopting endpoints).
   - Family C: `{"message": "..."}` (bare DRF dict with `message` key instead of `detail` — enhanced-logout style; less common on 401).
   - Family D: `{"success": false, "error": "..."}` (bare JsonResponse with unstructured `error` field).
2. Frontend axios instance at `api.ts:13` receives response.
3. Response interceptor at `api.ts:43-62` catches `error.response?.status === 401` at `:48`.
4. Interceptor branches on `url.includes('/auth/') || url.includes('/login')` at `:50`:
   - True → `useAuthStore.getState().logout()` at `:54` + `window.location.href = '/login'` at `:55` + `console.warn(...)` at `:58` + `return Promise.reject(error)` at `:60`.
   - False → `console.warn('Authentication required for:', url)` at `:58` + `return Promise.reject(error)` at `:60`.
5. **All 4 shape families take the same interceptor branch based on URL only** (shape is IGNORED). The rejected error propagates to whichever consumer awaited the promise.
6. Consumer typically DOES NOT catch (S2404 §14.5: 0 `AxiosError` typed catches + 0 `ErrorBoundary` in `frontend/src/**`). Silent-swallow rate ~99% (S2404 §14.5 canonical).

### 7.4 Refresh flow at HEAD

**ABSENT.** No client-side refresh loop. No 401-retry-with-refresh. No refresh state in `authStore` or elsewhere. Consumer receives 401 → interceptor either redirects (if auth-URL) or console.warn (if non-auth) → no retry attempt.

### 7.5 Cross-tab logout coordination flow at HEAD

**ABSENT** (F-C-TAB-1 S2403 same-issue lineage). Grep at HEAD: zero `BroadcastChannel`, zero `addEventListener.*storage` in `frontend/src/**` production paths (Agent 4 confirmed; S2204 §15.7 baseline preserved).

---

## 8. Data Ownership and Lifecycle

**Playbook §9 canonical Q8 — What is the data ownership and lifecycle?**

### 8.1 Token lifecycle

| Locus | Owner | Persistence | Lifecycle Transition |
|---|---|---|---|
| DRF `Token.key` | Backend DB (postgres row in `authtoken_token` table) | Permanent (no `expires_at` field per §4.1) | Created on login (`auth_views.py:53`); deleted on logout view success; NEVER expires implicitly |
| `authStore.token` | Frontend Zustand persist store | localStorage `auth-storage` key; survives page refresh | Set by `authStore.login`; cleared by `authStore.logout` (functional null); never rotated in-place |
| `Authorization` header | Transient | Attached per-request by `api.ts:20-24` request interceptor from `authStore.token` | Missing when `authStore.token === null` |

### 8.2 Session lifecycle observability (21-loci table, S2403 §14.3 preserved + RE-VERIFIED at HEAD)

Cat C RE-VERIFIES the S2403 baseline unchanged at HEAD `ee7cc0a0` (Agent 2 spot-checked 5 representative loci):

- 5 WORKING loci: cookie SameSite/Secure/HttpOnly (per-env declared at `settings.py:980-998`); session engine + CACHE_ALIAS (`settings.py:1105-1106`); session cookie age 14d (`settings.py:987`); session sliding TTL `SESSION_SAVE_EVERY_REQUEST=True` at `settings.py:1103`; VIP token expiry 72h enforced at `views_vip_invite.py:151-156`.
- 5 PARTIAL loci: token issuance login (partial event emit); token rotation password reset (partial); logout revocation basic (silent 200 on unauth); logout revocation enhanced (silent 200 on token-delete exception); session/token silent-degrade events (F-SESS-1 once-per-startup warning).
- 11 DEAD loci: token expiry (ABSENT); token refresh discipline (ABSENT F-C-REFRESH-1); Clear-Site-Data emission (ABSENT F-C-CSD-1); cookie Domain/Path (Django defaults F-C-COOKIE-1); session fixation defense cycle_key (ABSENT F-C-FIX-1); VIP account expiry 14d (NOT ENFORCED F-C-VIP-1); mobile token revocation on logout (ABSENT CF-C4); 14-of-15 storageKeys no-cleanup (F-C-STORE-1); cross-tab logout propagation (F-C-TAB-1); login/logout event emission (ABSENT CF-C3); role-transition session-scope (ABSENT F-C-ROLE-SCOPE).

**Enforcement summary:** 5 WORKING + 5 PARTIAL + 11 DEAD = 21 loci. Session-lifecycle discipline is undeclared or unenforced at more than half of the observable surfaces. **Cat C RE-VERIFIED — zero-delta from S2403 baseline at HEAD.**

### 8.3 storageKeys lifecycle (15-surface table, S2403 §14.2 baseline preserved)

See §14.2 below for full inventory. Baseline: 1 CLEAN (auth-storage functional-null) + 3 PARTIAL + 11 NO-CLEANUP; declared cleanup rate 1/15 = 6.7%; accidental cleanup rate 3/15 = 20%; no-cleanup rate 11/15 = 73%.

---

## 9. Integrations With Other Domains

**Playbook §9 canonical Q14 + Q17 + Q18 + Q21 + Q22 — Cross-domain integrations.**

Cat C's scope spans **6 identifiable cross-arc coordination surfaces** at HEAD. Table below preserves S2403 §19 CF-C1 through CF-C7 + adds Cat C S2503 evidence for cross-arc integration classification:

| Cross-arc Surface | Cat C Boundary | Handoff Item | Consumer Arc | Evidence at HEAD |
|---|---|---|---|---|
| **CF-C1: Refresh endpoint + logout envelope + Clear-Site-Data** | Cat C direct owner (this session) | Chris-D-verdict-request evidence at §19 | Group 2500 API arc (this domain) | F-C-REFRESH-1 + F-C-CSD-1 + F-C-LOGOUT-1/2 RE-VERIFIED at HEAD |
| **CF-C2: Session workspace-context + session_tool.retire on user-logout** | Cat C boundary (evidence only) | paStore field completeness + workspace-context authz coordination + PA-chat 401 UX + session_tool.retire cascade | Group 2600 PA | Grep at HEAD: `session_tool.retire` in `core/auth_views*.py` = 0 matches; paStore `syncUser(null)` wipes 3 fields, misses 6 fields (S2204 F7 preserved) |
| **CF-C3: Login/logout structured event emit** | Cat C boundary (evidence only) | Silent-401 rate telemetry + envelope-adoption metric emit + Cat D whitelist-γ `authHandling: 'suppress_redirect'` telemetry | Group 1700 Observability | Grep at HEAD: `EventStream.*` in auth flows = 0 matches; no `AuthEvent` model |
| **CF-C4: Mobile token revocation on logout** | Cat C boundary (evidence only) | `MobilePushToken.revoked_at.update(...)` cascade + mobile SDK refresh flow support | Group 2300 Mobile | Grep at HEAD: `MobilePushToken.*revoked_at.*=` in logout paths = 0 matches |
| **CF-C5: 15-surface storageKeys cleanup + R6 error-boundary framework** | Cat C boundary (evidence only) | Frontend cleanup contract execution (15 surfaces) + R6 error-boundary framework establishment (⚠ BLOCKING PREREQUISITE for Cat D γ mechanism per S2499 §9 CF-D5) | Group 2200 post-arc T-slot | Zero `BroadcastChannel` + zero `storage` event + zero `ErrorBoundary` at HEAD |
| **CF-C7: KillSwitch consumer attestation on logout** | Cat C boundary (evidence only; boundary preserved) | Governance-consumer state MUST NOT flip on user-logout | Group 1900 Authority | Grep at HEAD: `GovernanceState` / `KillSwitch` in logout paths = 0 matches (boundary PRESERVED at HEAD; S2403 F-C-BND-0 same-issue lineage) |
| **T7 REST↔WS message-contract joint** | Cat C touches at typed-error-envelope; owned by Cat D + Group 2600 | Envelope-shape parallel at WS emit surface | Cat D S2504 + Group 2600 PA co-authorship | 8 identified WS subscription sites per S2502 §5 targeted enumeration (not exhaustive) |
| **CF-C8: Content / Publishing (Rigby SIGN cycle 1 Q11 STRENGTHEN fold — NEW row)** | Cat C boundary observation only | Content generation + publishing flows call auth-protected endpoints; inconsistent 401/envelope shapes can leak into editor/publisher UX and automation retries. Cat C records contract variability only. | Group 1600 Content (consumer) | Adjacent to Cat A/B/C evidence surfaces; owner records contract variability at consumer level. |

**CF-C7 tightening (Rigby SIGN cycle 1 Q11 STRENGTHEN fold):** boundary preserved at HEAD; Cat C does not modify Authority / KillSwitch contracts. Potential dependency exists if logout is expected to invalidate attested sessions; decision deferred to xx99.

### 9.1 Cross-arc α/β/γ intersection (Cat C + Cat D + Cat B)

**Three decision spaces converge at Cat C evidence-plane** (Rigby SIGN Q6 fold at S2404 §19.1 established the nesting):

1. **Cat C session-lifecycle α/β/γ** (S2403 §19.1 PROPOSED PRIMARY = β explicit re-login):
   - α: Silent-refresh (opaque; hides expiry via automatic refresh). REQUIRES: refresh endpoint (F-C-REFRESH-1 remediation) + Token expiry field + rotation policy + FE 401-retry-with-refresh + cross-tab race handling + mobile SDK support. Blast radius HIGH. Observability cost HIGH.
   - β: Explicit re-login (visible; user-friction; simpler contract). REQUIRES: FE 401-modal integration + Clear-Site-Data emission (F-C-CSD-1 remediation) + logout envelope (F-C-LOGOUT-1 remediation). Blast radius LOW-MED. Observability cost LOW-MED. Compatible with F-TOKEN-1 "no expiry" preservation.
   - γ: Hybrid (silent while active, explicit after N-min idle). SUPERSET of α + β. Blast radius HIGHEST.

2. **Cat D typed-error-envelope α/β/γ** (S2404 §19.1 PROPOSED PRIMARY = γ RQ+ErrorBoundary):
   - α: Throw typed exceptions per HTTP status. Blast radius HIGH.
   - β: Return Result<T, E> discriminated-union. Blast radius MED.
   - γ: React-Query error callbacks + top-level ErrorBoundary + QueryClient default `onError`. Blast radius LOW. **Reconciliation with Cat C:** γ is MECHANISM; Cat C β "explicit re-login" is UX POLICY nested inside γ default handler.

3. **Cat D whitelist-replacement α/β/γ** (S2404 §19.1 PROPOSED PRIMARY = γ per-api-module enum):
   - α: `AUTH_REDIRECT_ENDPOINTS.has(url)` explicit endpoint list. Blast radius MED.
   - β: `X-Suppress-Auth-Redirect` backend response header. Requires backend coordination (Cat A domain).
   - γ: Per-api-module `authHandling: 'default' | 'suppress_redirect'` string enum + telemetry (CF-C3 to Group 1700). Blast radius LOW. Extends existing `InternalAxiosRequestConfig` extension pattern at api.ts:4-8 (Session 968 precedent).

**Cat C boundary preservation (mirror Cat B §19.1 R1 non-verdict qualifier):** the three α/β/γ selections are INDEPENDENT decision spaces (Cat B §1.2 Do Not Misread analog); mixed combinations valid. **The ONE nesting** established at S2404 Rigby Q6 fold: Cat D typed-error-envelope γ = mechanism, Cat C session-lifecycle β = UX policy nested inside γ default handler. This is not a general coupling.

**Intersection model (Rigby SIGN cycle 1 Q12 STRENGTHEN fold — replaces implicit 27-combination enumeration with operational statement):** there are three decision spaces (Cat C lifecycle policy α/β/γ; Cat D typed-error-envelope mechanism α/β/γ; Cat D whitelist-replacement α/β/γ). **Known nesting:** Cat D γ (mechanism) can host Cat C β (UX policy) as a default handler. **All other selections are orthogonal unless explicitly coupled by the xx99 verdict.** Cat C does NOT enumerate the 27 mechanical combinations; xx99 Chris-D-verdict pairs the selections as needed.

### 9.2 Cross-arc gating relationships

Two BLOCKING PREREQUISITE relationships identified:

1. **F-C-VIP-1 → any expiry-signal-bearing UX** (S2404 §19.1 Rigby Q9 fold + S2403 §19.1 preserved): Cat C α or γ (which surfaces expiry to user) OR Cat D γ mechanism copy that says "session expires at X" — MUST NOT ship until `VIPInvite.account_expires_at` enforced. Cat C RE-VERIFIED zero enforcement at HEAD. **Risk-gate constraint preserved.**
2. **R6 ErrorBoundary → Cat D γ mechanism** (S2404 §9 CF-D5 + S2502 §19.2 R6 ⚠ BLOCKING PREREQUISITE marker): Cat D γ (React-Query + top-level ErrorBoundary) CANNOT ship until top-level ErrorBoundary framework is established. Cat C RE-VERIFIED zero ErrorBoundary matches at HEAD. **Dual-ownership handoff (S2502 §19.2 R6 batch 3 Q11 STRENGTHEN):** R6 is BOTH (a) Cat C S2503 typed-envelope prerequisite AND (b) Group 2200 post-arc T-slot global-error-UX framework concern.

**Coordination note (non-prescriptive; Rigby SIGN cycle 1 Q13 STRENGTHEN fold):** R6 spans (a) a **global error UX framework** (Group 2200 ownership) and (b) **typed-envelope consumer requirements** (Cat D / Cat C dependents). Cat C records the dependency as: Group 2200 must ship *some* stable error-boundary hook/contract first (even minimal), after which Cat D / Cat C can attach envelope normalization and auth recovery behaviors. Exact framework design and sequencing are deferred to xx99.

---

## 10. Event Flows

**Playbook §9 canonical Q19 + Q20 — Event flows.**

### 10.1 Auth-lifecycle event emission at HEAD

**ABSENT.** Zero structured events emitted on login, logout, refresh, or session-transition. Grep at HEAD (Agent 2 + Agent 6): `EventStream.*` in auth flows = 0 matches; no `AuthEvent` model in `core/models/**`; no `structured_event.emit(...)` at logout paths.

**FleetAuthAuditLog + FleetPAChatAuditRow** exist (Fleet-forensics tables) but are NOT auth-lifecycle event streams and NOT consumed by Group 1700 Observability arc as event source.

### 10.2 Silent-401 rate telemetry surface (proposed)

Cat C evidence for CF-C3 handoff to Group 1700 Observability (per S2403 §19.4 AU-C2 preserved):

- **Metric candidate 1:** silent-401 rate = (401 response count × non-auth URL) / (total request count). Denominator scope: 803 consumer call-sites (S2404 §14.5 canonical).
- **Metric candidate 2:** envelope-adoption rate = (endpoints emitting envelope shape B) / (endpoints emitting 401). Denominator NOT established at Cat C scope (deferred to xx99).
- **Metric candidate 3:** Cat D γ `authHandling: 'suppress_redirect'` telemetry event count (S2404 §19.1 Rigby Q7 STRENGTHEN requirement).

Cat C evidence-collects metric candidates; Group 1700 owns emission mechanism + storage + dashboard.

### 10.3 Cross-tab logout event flow (proposed)

Cat C evidence for CF-C5 handoff to Group 2200 (per S2403 §19.5 preserved):

- **Mechanism candidate 1:** `BroadcastChannel('auth')` API. Modern browsers; not IE11.
- **Mechanism candidate 2:** `storage` event listener on `localStorage['auth-storage']` mutation. All browsers.

Cat C evidence-collects mechanisms; Group 2200 post-arc T-slot owns adoption.

---

## 11. Existing Documentation

**Playbook §9 canonical Q10 — What documentation exists?**

### 11.1 Topic docs coverage at HEAD (Agent 5 verified)

| Topic Doc | Exists? | Cat C Scope Coverage | Notes |
|---|---|---|---|
| `docs/topics/auth.md` | **YES** (262 lines, 13,170 bytes; last modified 2026-07-05) | **PARTIAL** | 4 subsections created at S2499 close per AU-D2. Section 3 covers Cat C session-lifecycle findings (F-C-REFRESH-1 + F-C-CSD-1 + F-C-STORE-1). Does NOT cover error-envelope mechanism α/β/γ options (Cat C's primary decision-space). |
| `docs/topics/frontend.md` | **YES** | **PARTIAL** | Covers F-B-CRIT-2 silent-401 + R6 error-boundary gap. Does NOT enumerate Cat C error-envelope mechanism options or refresh discipline options. |
| `docs/topics/api.md` | **NO** | N/A | S2500 §6 P-2 + S2501 §19.3 R6 + S2502 §19.3 R7 CREATE candidate; recast to S2599 xx99 close artifact per Cat C boundary discipline. |

### 11.2 Anchor docs coverage at HEAD (Agent 5 verified)

| Anchor Doc | Cat C Scope Coverage | Notes |
|---|---|---|
| `docs/PLATFORM_INVENTORY.md` | **NO §API autoblock** | S2500 §6 P-1 parked item; `docs/PLATFORM_INVENTORY.md` has no dedicated §API autoblock at HEAD. Auth-related counts are scattered. |
| `docs/PLATFORM_WHAT_IT_IS.md` | **NO §API narrative subsection** | S2500 §6 P-1 parked item; narrative anchor does not yet call out API contract discipline as first-class subsystem. |
| `docs/research/ARCHITECTURE_INDEX.md` | **NO auth-failure decision-matrix pointer** | S2499 AU-D6 deferred anchor-update; S2500 §6 P-3 preserved. Cat C α/β/γ + Cat D α/β/γ × 2 pointer NOT yet added. |
| `docs/research/domains/api/2500_api_domain_scoping.md` | **PARENT** | Cat C mission scope defined at §3.C (predecessor input for this document). |
| `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md` | **Predecessor Cat A** | §14.6 F6 4-shape 401 heterogeneity is Cat C's KEY EVIDENCE input for envelope normalization decision. |
| `docs/research/domains/api/2502_api_frontend_client_architecture_design_prep_audit.md` | **Predecessor Cat B** | §14.3 F3 SHAPE-BLIND interceptor + §19.2 R4 R6 are Cat C's KEY EVIDENCE inputs for consumer-side attach point + BLOCKING PREREQUISITE dependencies. |

### 11.3 Auth-domain research library coverage (predecessor cross-arc)

| Doc | Cat C Consumption |
|---|---|
| `docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md` | Cat C session-lifecycle α/β/γ decision-space + 15-surface storageKeys inventory + 21-loci lifecycle-observability rate + F-C-VIP-1 risk-gate + F-C-REFRESH-1 + F-C-CSD-1 + F-C-STORE-1 findings-inheritance |
| `docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md` | Cat D typed-error-envelope α/β/γ + Cat D whitelist-replacement α/β/γ + F-D-CALL-1 803 consumer + F-D-BOUNDARY-1 + F-D-SIDEBAR-1 findings-inheritance |
| `docs/research/domains/auth/2499_auth_canonical_summary.md` | Group 2400 xx99 canonical verdict "ACCRETION with declared-but-unenforced contracts" + CF-C1 through CF-C7 flags + rank-1 co-equal P0 batch preservation |

---

## 12. Research Coverage

**Playbook §9 canonical Q11 — What research coverage exists?**

**Classification: MODERATE-with-gaps** (Cat C classification per playbook §12 ladder; Agent 5 verified).

**Rationale:**

- **DEEP inheritance** for α/β/γ decision spaces: S2403 Cat C session-lifecycle + S2404 Cat D typed-error-envelope + S2404 Cat D whitelist-replacement — all three decision-spaces are documented with option-space + PROPOSED PRIMARY defaults + risk-gates + reconciliation notes.
- **MODERATE evidence** for backend contract gaps: F-C-REFRESH-1 + F-C-CSD-1 + F-C-STORE-1 findings enumerated with severity + blast-radius; S2501 F6 4-shape 401 heterogeneity documented; S2502 SHAPE-BLIND interceptor at api.ts:48-62 documented as attach point.
- **LIGHT evidence** for consumer-side observability: 803 consumer call-site inventory + 0 AxiosError catches + 0 ErrorBoundary + 79-raw-fetch bypass all documented; per-hook adoption rates unknown.
- **NONE-to-LIGHT evidence** for API contract shapes: 4 shape families enumerated but no proposed unified envelope shape; no refresh endpoint schema; no CSD emission spec; storageKeys cleanup coordination not partitioned across arcs.
- **DEEP evidence** for governance + ownership: CF-C1-CF-C7 routing precise; F-C-VIP-1 risk-gate constraint preserved; CODEOWNERS 100% assigned to `@clwest` for Cat C surface (Agent 6 verified).

---

## 13. Architecture Maturity

**Playbook §9 canonical Q12 — What is the architecture maturity?**

Cat C classification per playbook §12 ladder (Agent 6 evidence; **Rigby SIGN cycle 1 Q10 STRENGTHEN fold** — logout envelope + Clear-Site-Data consolidated under parent "Logout contract completeness" with sub-bullets; added **Contract SoT / ownership maturity** dimension per Q10):

| Dimension | Classification | Rationale |
|---|---|---|
| **Typed-error-envelope mechanism** | **EXPERIMENTAL** | QueryClient infra present at `frontend/src/main.tsx`; zero `useQuery.*onError` handler adoption at scale; zero `QueryClient.*defaultOptions.*onError`; zero ErrorBoundary; zero custom typed-exception classes; zero `Result<T, E>` pattern. All 3 α/β/γ options remain greenfield. |
| **Refresh endpoint contract** | **ABSENT** | Zero session-token refresh endpoint; DRF Token has no `expires_at`; implicit permanent-token contract until explicit password event. |
| **Logout contract completeness (parent)** | **PARTIAL** | Consolidated dimension per Q10 fold. Sub-dimensions: |
| ├─ Logout response envelope shape | **PARTIAL (sub-dim)** | Two endpoints emit `{'detail': ...}` (basic) vs `{'message': ...}` (enhanced) — different top-level keys for same semantic. Neither uses APIResponseEnvelope. Silent-200 on unauth (basic) or token-delete exception (both). |
| ├─ Clear-Site-Data header emission | **ABSENT (sub-dim)** | Zero header emission in production code; matches only in docs + audit scratch + `tools/pa_local.sh` comments. |
| └─ Cross-tab logout coordination | **ABSENT (sub-dim)** | Zero BroadcastChannel + zero storage event listener at HEAD. |
| **storageKeys cleanup contract** | **PARTIAL** | 1/15 = 6.7% declared cleanup rate (auth-storage functional-null); 3/15 = 20% accidental; 11/15 = 73% no-cleanup. |
| **VIP account_expires_at enforcement** | **DECLARED-BUT-NOT-ENFORCED** (S2403 lifecycle plane classification) | Field exists at model level with 14d default; zero runtime check; zero periodic beat task. |
| **Silent-401 interceptor discipline** | **PARTIAL (Cat C classification)** | SHAPE-BLIND (Cat B S2502 F3 KEY VERIFIER FINDING RE-VERIFIED); all 4 S2501 F6 shape families flow through identical branch based on URL only. |
| **Contract SoT / ownership maturity (Rigby SIGN cycle 1 Q10 STRENGTHEN fold — NEW dimension)** | **EXPERIMENTAL-to-PARTIAL** | Who owns envelope shape SoT? Not declared. Who owns storage cleanup contract? Not declared. Where are contracts documented + enforced? Scattered (partial coverage in `docs/topics/auth.md`; no `docs/topics/api.md` at HEAD). CODEOWNERS declares file ownership 100% to `@clwest` (sole-operator context); contract-governance ownership NOT declared. |

**Overall Cat C boundary maturity verdict: EXPERIMENTAL-to-PARTIAL depending on dimension.** Cat C boundary observation: the MATURITY GAP is not implementation-completeness (Cat A + Cat B + Cat D are the implementation-completeness arcs) but CONTRACT-CLARITY — what SHOULD the shape/mechanism/lifecycle be? That question belongs to xx99 Chris-D-verdict.

---

## 14. Known Drift

**Playbook §9 canonical Q26 — What drift exists between docs and runtime?**

Consolidated drift matrix at HEAD `ee7cc0a0`. Playbook §12 finding_type strings in bold. Denominator declared per §1.1.

### 14.1 F1 — 4 co-existing 401 shape families RE-VERIFIED IDENTICAL at HEAD (S2501 §14.6 F6 preserved)

**Predecessor claim (S2501 §14.6 F6):** four co-existing 401 shape families with no SoT contract declaration.

**Cat C verifier at HEAD:**
- **Family A (DRF default `{"detail": ...}`):** `core/auth_views.py:79-81, 91, 94, 123-126` (login-failure, logout success/exception, current_user unauth).
- **Family B (APIResponseEnvelope typed):** `core/api_responses.py:143-149` (unauthorized helper); `core/auth_middleware.py:79, 633, 658` (via `api_unauthorized(...)`).
- **Family C (bare DRF dict with `{message: str}`):** `core/auth_views_enhanced.py:554` (enhanced logout success + exception).
- **Family D (JsonResponse `{"success": false, "error": str}`):** `core/views_deploy.py:21, 79`; `core/views_agent_learning.py:2299-2300, 2373`; `core/views_auto_fix.py:26`; `core/views_business_ideas.py:142-143`.

**Delta:** ZERO across 2 sessions since S2501 close.

**Class:** `technical_debt` + `drift`. Severity: **HIGH baseline** at CONTRACT-clarity impact (heterogeneous 401 shape blocks consumer-side unified handling); Cat C boundary observation. Cat D S2404 verdict on γ mechanism preserved.

**Cat C boundary preservation (Rigby SIGN Q17 language-guardrail precedent):** the F1 finding IS the 4-shape-family enumeration; Cat C does NOT recommend which shape to standardize on. That decision is downstream (Cat A owns backend envelope-adoption path; Cat C owns α/β/γ intersection evidence).

### 14.2 F2 — 15-surface storageKeys × logout-cleanup CONTRACT baseline RE-VERIFIED IDENTICAL at HEAD (S2403 §14.2 preserved; line-drift only)

**Predecessor claim (S2403 §14.2):** 15 client-side persistence surfaces with 6.7% declared cleanup rate (1 CLEAN + 3 PARTIAL + 11 NO-CLEANUP).

**Cat C verifier at HEAD** (Agent 4 grep + line-drift reconciliation):

| # | Key | HEAD File:Line | S2403 Baseline File:Line | Line Drift | Cleanup Status |
|---|---|---|---|---|---|
| 1 | `auth-storage` | `authStore.ts:44` | `authStore.ts:43-50` | 0 (within range) | **CLEAN** (functional-null) |
| 2 | `navigation-store` | `navigationStore.ts:99` | `navigationStore.ts:98-105` | 0 (within range) | **NO-CLEANUP** (clearHistory action exists but not called on logout) |
| 3 | `pa-dock-state` | `paStore.ts:396` | `paStore.ts:395-431` | 0 (within range) | **PARTIAL** (syncUser wipes 3 fields, misses 6 fields per S2204 F7) |
| 4 | `assistant-voice-settings` (VOICE_SETTINGS_KEY) | `CommandCenterPage.tsx:166` | `CommandCenterPage.tsx:190` | −24 lines | **NO-CLEANUP** |
| 5 | `cc_dashboard_collapsed` | `CommandCenterPage.tsx:825` | `CommandCenterPage.tsx:825` | 0 | **NO-CLEANUP** |
| 6 | `cc_chat_focus_mode` | `CommandCenterPage.tsx:828` | `CommandCenterPage.tsx:828` | 0 | **NO-CLEANUP** |
| 7 | `pipeline_dismissed_${workspaceId}` | `WorkspaceDashboardPage.tsx:188` | `WorkspaceDashboardPage.tsx:188` | 0 | **PARTIAL** (workspace-change cleanup, not logout) |
| 8 | `demo-pipeline-dismissed` | `DemoPipelineCard.tsx:87` | `DemoPipelineCard.tsx:87` | 0 | **NO-CLEANUP** |
| 9 | `cockpit-focus-mode` | `useFocusMode.ts:13` | `useFocusMode.ts:13` | 0 | **NO-CLEANUP** |
| 10 | `sidebar-collapsed` | `Sidebar.tsx:126` | `Sidebar.tsx:126` | 0 | **NO-CLEANUP** |
| 11 | `sidebar-reference-open` | `Sidebar.tsx:105` | `Sidebar.tsx:105` | 0 | **NO-CLEANUP** |
| 12 | `showDebugPanels` (DEV_KEY) | `PanelDebugDrawer.tsx:6` (const decl) / `:10` (usage) | `PanelDebugDrawer.tsx:10` | −4 to 0 lines (declaration site vs usage site both valid) | **NO-CLEANUP** (dev-only) |
| 13 | `deliverables_view_mode` | `DeliverablesTab.tsx:304` | `DeliverablesTab.tsx:304` | 0 | **NO-CLEANUP** |
| 14 | `cockpit-sidebar-collapsed` | `CockpitSidebar.tsx:101` | `CockpitSidebar.tsx:101` | 0 | **NO-CLEANUP** |
| 15 | `podcast_voice_profile_id` | `ContentStudioTab.tsx:2736` | `ContentStudioTab.tsx:2734` | +2 lines | **PARTIAL** (change-cleanup, not logout) |

**Aggregate:** 1 CLEAN (auth-storage) + 3 PARTIAL (paStore + pipeline_dismissed + podcast_voice_profile) + 11 NO-CLEANUP. **Declared cleanup rate: 1/15 = 6.7% (S2403 IDENTICAL).**

**Line-drift note (Rigby SIGN cycle 1 Q6 STRENGTHEN fold — compressed for scan-friendliness; non-substantive):** F2 table content is **functionally identical** to S2403. Minor file line-number drift observed on 3/15 surfaces (one large shift on surface #4; minor shifts on #12 and #15). No new storage surfaces added; no removals.

**Class:** `technical_debt` + `drift`. Severity: **HIGH baseline** (S2403 preserved). Cat C RE-VERIFIED IDENTICAL at HEAD.

**Cat C boundary observation:** cleanup coordination (which arc owns removal execution) is CROSS-ARC — Cat C hands to Group 2200 post-arc T-slot per CF-C5; Group 2600 PA co-owns paStore-side per CF-C2.

### 14.3 F3 — Refresh endpoint ABSENT at HEAD RE-VERIFIED (S2403 F-C-REFRESH-1 preserved)

**Predecessor claim (S2403 §14.1):** no session-token refresh endpoint at HEAD.

**Cat C verifier at HEAD** (parent-Claude direct grep + Agent 3 verified):

- `refresh|renew_token` in `core/urls.py` = 6 matches. All non-auth:
  - `:747` `refresh_token` (import symbol for `:2055` OAuth external).
  - `:1345, 3071` `refresh_agent_discovery` (agent-discovery cache).
  - `:1589, 1925` `refresh_project_spiders` (project spider cache).
  - `:2055` `path('api/distribution/oauth/<str:platform>/refresh/', refresh_token, ...)` (third-party OAuth external).
- `refresh|renew_token` in `core/auth_views*.py` = **0 matches**.
- `TokenRefreshView`, `SlidingToken`, `SimpleJWT`, `RefreshToken` in `core/**/*.py` = **0 matches** (Agent 1 verified).
- `requirements.txt` — no `djangorestframework-simplejwt` or JWT-refresh library present (Agent 1 verified).

**Delta:** ZERO across 2 sessions since S2403 close.

**Class:** `missing_connection` + `technical_debt`. Severity: **HIGH baseline** (S2403 preserved). Cat C RE-VERIFIED ABSENT at HEAD.

**Lineage note (Rigby SIGN cycle 1 Q4 STRENGTHEN fold — reframed from clean arrow to "related but distinct"):** Cat A F-TOKEN-1 (token lifetime / expiry semantics) is **adjacent** to Cat C F-C-REFRESH-1 (refresh contract absent). They can co-exist or be solved independently: expiry semantics can be addressed without refresh (short-lived sessions + re-auth), and refresh can exist even if expiry semantics are mis-set. Cat C records absence only; design choice deferred. Both IDs preserved for cross-arc traceability per S2403 §15 discipline.

### 14.4 F4 — Clear-Site-Data ZERO EMISSION at HEAD RE-VERIFIED (S2403 F-C-CSD-1 preserved)

**Predecessor claim (S2403 §14.1):** zero Clear-Site-Data header emission on logout at HEAD.

**Cat C verifier at HEAD** (parent-Claude direct grep + Agent 2 verified):

- Repo-wide `Clear-Site-Data` grep = 21 total matches.
- Filtered to code-only (`--glob '!*.md'`) = 6 matches, all in NON-PRODUCTION-CODE:
  - `tools/pa_local.sh:28, 36, 46` (3 matches; audit-tracker comments).
  - `.claude/scratch/sign_batch_2.txt:9`, `.claude/scratch/sign_batch_3.txt:5`, `.claude/scratch/ratification_card_s2403.txt:15, 34` (3 matches; audit scratch files).
- Production code (`core/**/*.py` + `frontend/src/**`) = **0 matches** (Agent 2 verified).
- Neither `logout_view` nor `logout_enhanced_view` sets `response['Clear-Site-Data']` (Agent 2 direct file read).

**Delta:** ZERO across 2 sessions.

**Class:** `drift` + `missing_connection`. Severity: **HIGH baseline** (S2403 preserved).

### 14.5 F5 — SHAPE-BLIND interceptor RE-VERIFIED IDENTICAL at HEAD (S2502 §14.3 F3 preserved; 5-session zero-delta)

**Predecessor claims combined:**
- S2203 §14 F3: silent-401 SYSTEMIC across ~630 call-sites (grep-based estimate).
- S2404 §14.5: 803 consumer classification (57 direct + 667 hook + 79 raw fetch); ~99% silent-swallow rate; 90.2% interceptor coverage.
- S2501 §14.6 F6: FOUR co-existing 401 shape families at HEAD.
- S2502 §14.3 F3: interceptor at `api.ts:43–62` is SHAPE-BLIND; reads only status + URL substring; all 4 shape families take identical non-auth branch.

**Cat C verifier at HEAD (parent-Claude direct read of `api.ts:40-70`):**

```typescript
// Line 43-62 quoted verbatim:
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Session 819: Only redirect to login for explicit auth endpoints
    // Other 401s should be handled by the component (user might just need to refresh)
    if (error.response?.status === 401) {
      const url = error.config?.url || ''
      const isAuthEndpoint = url.includes('/auth/') || url.includes('/login')

      // Only force logout/redirect for auth-related 401s
      if (isAuthEndpoint) {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
      // For other endpoints, just log the error - component can handle it
      console.warn('Authentication required for:', url)
    }
    return Promise.reject(error)
  }
)
```

**Explicit confirmation of Cat B §14.3 F3 4 sub-facts:**
- (a) Reads only `error.response?.status === 401` — not body: **CONFIRMED at line 48.**
- (b) Branches on `url.includes('/auth/') || url.includes('/login')` for isAuthEndpoint: **CONFIRMED at line 50 (exact substring match).**
- (c) Calls `useAuthStore.getState().logout() + window.location.href='/login'` for isAuthEndpoint: **CONFIRMED at lines 54-55.**
- (d) `console.warn + Promise.reject` for non-auth: **CONFIRMED at lines 58 + 60.**

**Delta:** ZERO across 5 sessions since S2404 close (HEAD `31398008` → HEAD `4e6c1ee8` → HEAD `77564f76` → HEAD `548f53a1` → HEAD `ee7cc0a0`).

**Class:** `technical_debt` (structural — shape-blind observer at consumer boundary) + `drift` (interceptor discipline lags Cat A backend heterogeneity documentation). Severity: **HIGH baseline** at consumer-observability impact; **CRITICAL conditional** if Cat C α/β/γ γ mechanism requires shape-normalization landing first as gating prerequisite (Cat C boundary observation; conditional preserved per Cat B §14.3 F3 batch 4 Q17 language guardrail — Cat C does NOT declare CRITICAL unconditional).

**Cat C boundary preservation:** the CRITICAL conditional is TRUE if Cat D γ mechanism (React-Query error callbacks + top-level ErrorBoundary) needs shape-normalization to happen at the interceptor layer BEFORE the RQ error callback runs; otherwise Cat D γ can simply consume whatever shape it receives and treat all 4 as equivalent (since it does not surface shape-specific error codes to UI). **Cat C evidence:** the choice between "interceptor normalizes then RQ handles" vs "RQ handles all 4 shapes uniformly" is Chris-D-verdict at xx99, jointly with Cat D γ mechanism ratification.

**Conditional CRITICAL — two-part trigger (Rigby SIGN cycle 1 Q5 STRENGTHEN fold):** the CRITICAL classification is triggered only if BOTH hold:
1. xx99 verdict selects a mechanism that requires **shape-normalized error payloads** for correct auth recovery behavior.
2. Client interceptor remains **shape-blind** (status-only) with no upstream normalization.

If either condition is false, severity remains **HIGH** (technical debt / drift). **Cat C note:** this does not assert normalization is required — only that certain downstream selections would depend on it.

### 14.6 F6 — Basic vs Enhanced logout key-name DRIFT (Cat C NEW at HEAD)

**Cat C new observation** (parent-Claude direct file read at §5.2):

- Basic logout (`core/auth_views.py:91, 94`) emits `Response({'detail': ...})` — top-level key `detail`.
- Enhanced logout (`core/auth_views_enhanced.py:554`) emits `Response({'message': ...})` — top-level key `message`.

Both endpoints share logout success semantics; both return 200; both are documented as user-facing logout endpoints. Different top-level keys.

**Class:** `drift` (documentary — same-domain-different-shape). **Severity: MEDIUM (contract drift; Rigby SIGN cycle 1 Q7 STRENGTHEN fold — bumped from LOW-MEDIUM):** basic vs enhanced logout emit different top-level message keys (`detail` vs `message`) for the same semantic outcome. Consumers reading only one key will silently lose message visibility. Impact is limited (both 200) but creates cross-surface parsing inconsistency inside the same domain. Cat C boundary observation: this DRIFT is an example of the F1 4-shape heterogeneity at CLOSE range within a single domain (auth); consolidation is Cat A downstream.

### 14.7 F7 — F-C-VIP-1 DECLARED-BUT-NOT-ENFORCED RE-VERIFIED at HEAD (S2403 preserved)

**Predecessor claim (S2403 §14.1 F-C-VIP-1):** `VIPInvite.account_expires_at` field exists at model level but has zero runtime enforcement.

**Cat C verifier at HEAD** (Agent 1 + Agent 6 verified):

- `core/models_vip_invite.py:72` defines `account_expires_at = models.DateTimeField(default=_default_account_expires)`.
- `_default_account_expires` set to now + 14 days per S2403 baseline preservation.
- API response serializes field: `core/views_vip_invite.py:74, 161, 213` all call `.isoformat()`.
- `is_valid` property at `core/models_vip_invite.py:95-103` checks `token_expires_at > now` only, NOT `account_expires_at`.
- Grep `account_expires_at__lt`, `account_expires_at <`, `account_expires_at.__lt`, `account_expires_at.gt` in `core/**/*.py` = **0 matches**.
- Grep for periodic cleanup task referencing `VIPInvite` in `core/tasks*.py` + `core/celery.py` + beat schedule = **0 matches** (Agent 3 verified).

**Delta:** ZERO across 2 sessions.

**Class:** `technical_debt` + `unclear_owner` (lifecycle plane; risk-gate). Severity: **HIGH baseline** (S2403 preserved).

**Cat C boundary observation:** F-C-VIP-1 is preserved as **shipping prerequisite** for any expiry-signal-bearing UX (per S2404 §19.1 Rigby SIGN Q9 fold copy guidance + S2403 §19.1 preservation). Cat C RE-VERIFIED zero enforcement at HEAD; risk-gate constraint preserved regardless of α/β/γ selection.

### 14.8 F8 — Sidebar backend-logout absence (F-D-SIDEBAR-1) RE-VERIFIED IDENTICAL at HEAD (S2404 §16 F-D-SIDEBAR-1 preserved)

**Predecessor claim (S2404 §16):** Sidebar user-menu logout at `frontend/src/components/layout/Sidebar.tsx:356` clears authStore but does NOT call `authApi.logout()` (backend token revoke).

**Cat C verifier at HEAD** (parent-Claude direct grep):
```
Sidebar.tsx:356:  onClick={() => { setUserMenuOpen(false); syncUser(null); logout() }}
```

Confirms `syncUser(null)` (paStore clear) + `logout()` (Zustand authStore.logout). NO `authApi.logout()` call.

**Delta:** ZERO across 5 sessions.

**Class:** `boundary_violation` (frontend-symptom-vs-backend-model). Severity: **MEDIUM** at attacker-valid-token window impact.

**Cat C boundary observation:** F-D-SIDEBAR-1 is a POST-ARC T-slot maintainer-decision batch item per S2404 §19.2 P0-B preservation. Cat C RE-VERIFIED IDENTICAL at HEAD; remediation ownership NOT reassigned to Cat C.

**Ownership note (Rigby SIGN cycle 1 Q9 STRENGTHEN fold):** F-D-SIDEBAR-1 is a **frontend execution** concern (invocation of backend logout / contract alignment) and is expected to land under **Cat D** (frontend contract alignment scope). Cat C records the HEAD state and preserves S2404's "post-arc T-slot" sequencing; no reassignment or remediation plan is proposed here.

---

## 15. Known Technical Debt

**Playbook §9 canonical Q23 — What technical debts exist?**

**Top-5 Cat C Observability Risks** (label renamed from "technical debt" per Cat A + Cat B §15 precedent; ranked by CONSUMER-observability + CONTRACT-clarity impact; non-prescriptive per Cat A + Cat B precedent):

1. **Heterogeneous 401 response shapes across 4 families (F1 RE-VERIFIED)**. Cat A backend surface has 4 co-existing 401 shape families with no SoT contract; Cat B consumer interceptor is SHAPE-BLIND. Combined effect: **no consumer-side shape-uniform handler is possible without either shape-normalization landing at interceptor OR a shape-agnostic γ mechanism at RQ layer**. Blast radius = 803 consumer surface. Cat C boundary observation; α/β/γ intersection Chris-D-verdict at xx99.

2. **Refresh endpoint contract ABSENT (F3 RE-VERIFIED)**. No refresh mechanism at HEAD; F-TOKEN-1 baseline "no expiry" contradiction. Implicit contract = permanent token absent password event. Cat C boundary observation; α session-lifecycle would REQUIRE addition; β does NOT.

3. **Clear-Site-Data ZERO EMISSION (F4 RE-VERIFIED)**. No cross-tab-safe logout hygiene. Cookies + storage + cache persist across auth boundary. Blast contained to first-party by `SESSION_COOKIE_SAMESITE='Strict'` (S2403 §14.1 preserved) but shared-browser cross-user leakage risk remains. Cat C boundary observation; emission locus Chris-D-verdict at xx99.

4. **storageKeys cleanup 6.7% declared rate (F2 RE-VERIFIED)**. 14 of 15 client-side persistence surfaces lack DECLARED logout-cleanup contract. Aggregate cross-user leakage severity: 8-of-15 surfaces have non-NONE severity (S2403 §14.2 preserved). Cat C boundary observation; cleanup coordination CROSS-ARC (Cat C + Group 2200 post-arc T-slot + Group 2600 PA).

5. **F-C-VIP-1 risk-gate DECLARED-FICTIONAL (F7 RE-VERIFIED)**. `VIPInvite.account_expires_at` field exists; zero runtime enforcement; zero periodic cleanup. Blast radius = every VIP account (account persists indefinitely once minted). Cat C boundary observation; enforcement is shipping prerequisite for expiry-signal-bearing UX. **Risk-gate qualifier (Rigby SIGN cycle 1 Q16 STRENGTHEN fold):** F-C-VIP-1 is a *deployment gating constraint* for any expiry-signal UX, but it is not the broadest cross-surface observability / contract inconsistency driver; it is ranked #5 on *surface area*, not on *go / no-go leverage*.

**Cat C boundary discipline preservation (mirror Cat A + Cat B §15 fold):** risks observed + ranked by CONSUMER-observability + CONTRACT-clarity impact; NOT recommendations. Chris-D-verdict-request at S2599 xx99 close after Cat D S2504 completes.

---

## 16. Boundary Violations

**Playbook §9 canonical Q24 — What boundary violations exist?**

**Cat C boundary observation** (mirror Cat A + Cat B §16 fold): at HEAD the CONTRACT surface for error-envelope + refresh + logout is largely NOT DECLARED (per §14 F1 + F3 + F4 + F5 + F6), so "boundary violation" is a less useful frame than "missing / undeclared contract discipline" — Cat D S2504 permission-floor + REST↔WS T7 joint may still classify specific items as violations depending on enforcement mechanisms.

**Level 0 — explicit-contract missing (Rigby SIGN cycle 1 Q17 STRENGTHEN fold — decision-space anchor for xx99):** the platform currently lacks an explicit, centralized API contract for (error envelope + refresh + logout semantics). Cat C records evidence of an *implicit* contract (Level 2) and its violations; whether to formalize a first-class contract (and where it lives) is **deferred to xx99**. This Level-0 anchor prevents the reader from missing the primary "contract should exist?" decision axis at xx99 close.

**Two-level frame (mirror Cat B §16 Q13 fold):** some CONTRACT boundaries are implicitly declared even in the absence of formal spec:

- **Level 1 (primary posture):** formal CONTRACT for error-envelope shape + refresh endpoint + logout envelope not declared — "boundary violation" frame under-applies.
- **Level 2 (implicit-contract exception):** the REST_FRAMEWORK global default `[IsAuthenticated]` + api.ts:20-24 `Authorization` request interceptor + api.ts:48-62 401-response interceptor form an **implicit end-to-end auth-request-response contract**. The following violate that implicit contract at HEAD:
  - **F-D-BYPASS-1 (S2502 §14.5 preserved):** 79 raw `fetch()` calls bypass the axios interceptor entirely; 9.8% of HTTP surface. Cat B RE-VERIFIED; Cat D S2504 post-arc T-slot owns per-site classification.
  - **F-D-SIDEBAR-1 (F8 above):** Sidebar user-menu logout does NOT call `authApi.logout()`; server-side session token persists after logout onClick. Backend Token row remains valid; only frontend state clears.
  - **F-C-STORE-1 (F2 above):** 14 of 15 client-side persistence surfaces lack declared cleanup on logout despite Zustand persist + Sidebar logout being the intended logout mechanism.

**Adjacent boundary violation candidates observed but not owned by Cat C:**

- **F-B-CRIT-2 Silent-401 SYSTEMIC** (S2404 F-D-CALL-1): ~99% silent-swallow rate across 803 consumer sites. Cat D S2404 owner.
- **F-C-COCKPIT-1 (S2403 preserved):** 16 `/cockpit/*` `<Navigate>` at `App.tsx:134-149` NOT wrapped by ProtectedRoute. S2403 baseline STILL-LIVE at HEAD per Agent 6 spot-check. Cross-arc navigation-guard boundary; Group 2200 post-arc R5 cockpit-retirement decision.

Cat C boundary: NOT OWNED at CONTRACT surface directly; adjacent to F-D-BYPASS-1 which Cat B RE-VERIFIED at S2502 §14.5.

---

## 17. Duplicate or Overlapping Systems

**Playbook §9 canonical Q25 — What duplicate or overlapping systems exist?**

**Cat C verifier at HEAD:**

1. **Two logout code paths (F-C-DUP-1 same-issue lineage; S2403 §17 preserved).**
   - Basic logout `core/auth_views.py:84-94` — no explicit permission decorator (falls to global default); silent-200 on unauth via `IsAuthenticated` gate (Cat A F-C-LOGOUT-1 lineage); response `{'detail': ...}`.
   - Enhanced logout `core/auth_views_enhanced.py:539-556` — explicit `@permission_classes([IsAuthenticated])`; silent-200 on token-delete exception (Cat A F-C-LOGOUT-2 lineage); response `{'message': ...}`.
   
   Both delete `request.user.auth_token`; neither flushes Django session; neither emits Clear-Site-Data.
   
   **Class:** `duplicate_pattern` (structure finding preserved). Severity: **MEDIUM** (consolidation candidate post-arc; behavior divergence causes downstream confusion — frontend picks `/v1/auth/logout/` at `api.ts:76` and never uses `/v1/auth/logout-enhanced/`).
   
   **Cat C new observation (basic vs enhanced key-name DRIFT):** §14.6 F6 — different top-level keys for same semantic. Adds a NEW dimension to the S2403 F-C-DUP-1 finding: not just behavior divergence but also response-key divergence.

2. **Two envelope shape systems (Cat C NEW at HEAD).**
   - `APIResponseEnvelope` at `core/api_responses.py:15-234` — typed envelope with `{success, data, message}` for success + `{success, error: {code, message}}` for error.
   - Bare DRF `Response(dict)` — used at `auth_views.py:79-81, 91, 94, 123-126` + `auth_views_enhanced.py:554`.
   - `api_helpers.api_success/api_error` wrappers — used at `views_ab_testing.py` (~20+ sites).
   
   **NOT DUPLICATE** in mechanism (three distinct responsibilities); rather THREE DISJOINT SHAPES that coexist without SoT contract selection. Blast radius per §6.3: ~14 envelope-adopting sites + ~6 bare-DRF + ~40+ JsonResponse-dict + ~30+ api_helpers. **Class:** `overcoupling` (implicit accretion of parallel shape systems).
   
   Cat C boundary observation: consolidation is Cat A domain (backend contract SoT); Cat C evidence-collects for xx99.

3. **Two logout observers (server-side vs client-side) — reframed per Rigby SIGN cycle 1 Q15 STRENGTHEN fold: "complementary but under-specified coupling".**
   - Server-side: `authApi.logout()` → `POST /api/v1/auth/logout/` → delete Token row.
   - Client-side: `useAuthStore.logout()` → clear token/user/isAuthenticated from Zustand persist store.
   
   Sidebar user-menu at `Sidebar.tsx:356` invokes CLIENT-SIDE only (F-D-SIDEBAR-1). **Not duplicates in mechanism** (different layers), **but overlapping in intent** (terminate session). Current state is **implicit co-completion without an explicit contract** that both fire or that either alone is sufficient. **Risk:** partial logout (server token invalidated but client storage persists, or vice versa; F-D-SIDEBAR-1 is the concrete instance where the CLIENT side fires without the SERVER side). Cat C boundary observation — cross-layer contract not declared; decision deferred to xx99.

---

## 18. Ownership Gaps

**Playbook §9 canonical Q27 — What ownership gaps exist?**

CODEOWNERS at HEAD (Cat C surface; Agent 6 verified against repo-root `./CODEOWNERS`, 48 lines):

- **Default:** `* @clwest` (sole operator per line 18).
- **Cat C surface — 100% ASSIGNED:**
  - `frontend/src/lib/api.ts @clwest` (line 31 — silent-401 interceptor).
  - `frontend/src/stores/authStore.ts @clwest` (line 32 — persist store).
  - `frontend/src/components/layout/Sidebar.tsx @clwest` (line 33 — user-menu logout).
  - `frontend/src/App.tsx @clwest` (line 34 — ProtectedRoute + cockpit legacy redirects).
- **Backend files — DEFAULT (via `*` wildcard) — resolves to @clwest:**
  - `core/api_responses.py` — envelope helpers.
  - `core/auth_views.py` — basic logout.
  - `core/auth_views_enhanced.py` — enhanced logout.

**Cat C boundary observation (Rigby SIGN cycle 1 Cat B Q15 STRENGTHEN precedent — cost-of-deferral note):** at HEAD the Cat C surface is 100% assigned to `@clwest` (sole operator context per S2201 §14 rationale). This is DECLARED-INTENTIONAL per CODEOWNERS lines 8-13 explicit-deferral comment (frontend-specific ownership refined at S2600+ per Group 2200 T-slot maintainer-decision batch). Cost-of-deferral: review latency remains single-owner-bounded; drift/defect persistence across sessions bounded by sole-operator context. Cat C does NOT recommend reassignment; the deferral is DECLARED-INTENTIONAL.

**No new HIGH-severity ownership gaps at Cat C scope.**

---

## 19. Recommended Future Research — Chris-D-verdict-request evidence (non-prescriptive)

**Playbook §9 canonical Q28 — What should be researched next?**

**Cat C boundary discipline note (mirror Cat A + Cat B §19 fold):** section labeled "Recommended Future Research — Chris-D-verdict-request evidence (non-prescriptive)" to preempt "Cat C recommends" misread. Tiers below are decision candidates / evidence prompts, NOT recommendations. Cat C collects evidence for future Chris-D-verdicts at xx99; Cat C does NOT recommend implementation.

Ranked by architectural uncertainty × risk × unblocked flows per playbook §19.

### 19.1 CRITICAL tier — evidence collected for S2599 xx99 close

**R1 — [S2599 xx99 close Chris-D-verdict-request] Cat C session-lifecycle α/β/γ + Cat D typed-error-envelope α/β/γ + Cat D whitelist-replacement α/β/γ intersection resolution.**

Cat C boundary evidence: **THREE independent decision-spaces** collected across S2403 + S2404 + this document. Each has a PROPOSED PRIMARY:

- Cat C session-lifecycle (S2403 §19.1 PROPOSED PRIMARY): β explicit re-login.
- Cat D typed-error-envelope (S2404 §19.1 PROPOSED PRIMARY): γ React-Query + top-level ErrorBoundary.
- Cat D whitelist-replacement (S2404 §19.1 PROPOSED PRIMARY): γ per-api-module `authHandling: 'default' | 'suppress_redirect'` string enum + telemetry.

**One established nesting** (S2404 §19.1 Rigby SIGN Q6 fold): Cat D γ = mechanism; Cat C β = UX policy nested inside γ default handler. **All other pairings are INDEPENDENT** (per §1.2 Do Not Misread).

**Cat C boundary preserved (mirror Cat B §19.1 R1 non-verdict qualifier):** Cat C enumerates axes only; Chris-D-verdict at xx99 owns selection. Cat C does NOT recommend PROPOSED PRIMARY ratification.

**R2 — [S2599 xx99 close Chris-D-verdict-request] Envelope shape SoT selection (Family A vs B vs C vs D vs new).**

Cat C evidence per §14.1 F1: 4 co-existing 401 shape families with no SoT contract. Chris-D-verdict at xx99 must select ONE canonical family OR declare "all 4 valid" with normalization mechanism (shape-aware interceptor OR shape-agnostic RQ γ handler). Cat C evidence for xx99:

- Family A `{"detail": ...}` — smallest change (DRF built-in); consumer must not depend on `error` key; limited machine-readability (no error_code).
- Family B APIResponseEnvelope `{success, error: {code, message}}` — most machine-readable + already-scaffolded in `core/api_responses.py:15-234`; requires per-endpoint adoption OR custom DRF `EXCEPTION_HANDLER` at REST_FRAMEWORK level.
- Family C `{"message": ...}` — enhanced-logout-style; not preferred (same-domain drift from Family A).
- Family D `{"success": false, "error": str}` — bare unstructured; NOT preferred for typed-error-envelope adoption per Cat D γ mechanism requirements (γ discriminates on `error.code`).

**HEAD observation (Rigby SIGN cycle 1 Q14 STRENGTHEN fold — softened from "ONLY family" over-commitment):** under the current Cat D γ mechanism assumptions (expects a consistent typed envelope without per-shape branching), **Family B is the lowest-friction fit** because it already matches the typed `APIResponseEnvelope` pattern. Families A/C/D could be made compatible **only with additional shape-normalization (client or server) or by expanding γ to discriminate across multiple keys (`detail` / `message` / `error`)** — decision deferred. Chris-D-verdict on scope of retrofit at xx99. Cat C does NOT recommend.

**R3 — [S2599 xx99 close Chris-D-verdict-request] Refresh endpoint contract necessity (dependent on Cat C session-lifecycle α/β/γ verdict).**

Cat C boundary evidence per §14.3 F3: no session-token refresh endpoint at HEAD. **Refresh endpoint necessity is COUPLED to Cat C session-lifecycle α/β/γ verdict** (R1 above):
- α silent-refresh REQUIRES refresh endpoint.
- β explicit re-login DOES NOT require refresh endpoint.
- γ hybrid REQUIRES refresh endpoint + explicit re-login fallback.

If Chris ratifies β at R1 xx99, F-C-REFRESH-1 remains ABSENT-BY-DESIGN (not defect); Cat A F-TOKEN-1 no-expiry preservation compatible. If Chris ratifies α or γ at R1 xx99, F-C-REFRESH-1 becomes a P0 execution item + F-TOKEN-1 must close first (Token model add `expires_at` field + rotation policy) as strict prerequisite.

Cat C boundary observation: **the R1 verdict determines R3 necessity**. Cat C does NOT recommend either direction.

**R4 — [S2599 xx99 close Chris-D-verdict-request] Clear-Site-Data emission locus (per Agent 2 §5.3 candidate loci).**

Cat C boundary evidence per §14.4 F4 + §5.3: 3 candidate emission loci enumerated (per-endpoint response header, middleware, envelope helper). Chris-D-verdict at xx99 on locus selection. Cat C boundary preserved: header-value spec (e.g., which of `"cache"` / `"cookies"` / `"storage"` / `"executionContexts"` to emit) is downstream Cat A domain per S2403 §19.1 R2 preservation.

### 19.2 HIGH tier — evidence for S2504 Cat D + post-arc T-slot

**R5 — [S2504 Cat D boundary evidence] SHAPE-BLIND interceptor is CONSUMER-side attach point for Cat C α/β/γ + Cat D α/β/γ × 2.**

Cat C evidence per §14.5 F5 + Cat B §19.2 R4 preserved: the interceptor at `api.ts:43-62` is where any consumer-side envelope-adoption mechanism attaches (either replace interceptor OR augment RQ QueryClient default). **Cat C RE-VERIFIED shape-blind + 4-shape flow-through IDENTICAL at HEAD.** Cat D S2504 owns final mechanism design; Cat C hands attach-point evidence.

**R6 — [S2504 Cat D + Group 2200 post-arc T-slot DUAL-OWNED] Error-boundary framework establishment prerequisite.**

Cat C evidence per §14.5 F5 + Cat B §19.2 R6 preserved: 0 `ErrorBoundary` / `componentDidCatch` / `getDerivedStateFromError` matches in `frontend/src/**` at HEAD (RE-VERIFIED). Per S2404 §9 CF-D5 + S2502 §19.2 R6 ⚠ BLOCKING PREREQUISITE marker: **R6 is prerequisite for Cat D γ mechanism**. Dual-ownership handoff preserved (S2502 §19.2 R6 Q11 fold): Cat D S2504 (typed-envelope prerequisite) AND Group 2200 post-arc T-slot (global error UX / boundary framework).

**R7 — [S2504 Cat D + post-arc T-slot] Basic-vs-enhanced logout consolidation (F-C-DUP-1 same-issue lineage + F6 same-domain drift).**

Cat C evidence per §14.6 F6 + §17 F-C-DUP-1: two logout endpoints with divergent contracts (permission decorator asymmetric; response key-name divergence). Cat C boundary observation: consolidation candidate at post-arc T-slot; behavior divergence causes downstream confusion. Cat C does NOT prescribe consolidation path (retire basic vs promote basic vs unify shapes at bridge).

### 19.3 MEDIUM tier — evidence for S2599 xx99 anchor-update

**R8 — [S2599 xx99 close artifact candidate] `docs/topics/api.md` CREATE + PLATFORM_INVENTORY §API autoblock + PLATFORM_WHAT_IT_IS §API narrative subsection.**

Cat C extends Cat B §19.3 R7 + Cat A §19 recommendations + S2500 §6 P-1 with CONTRACT-side evidence: 4 shape families + envelope adoption sites + F-C-REFRESH-1 absence + F-C-CSD-1 zero-emission + F-C-STORE-1 6.7%-rate + 21-loci lifecycle-observability + basic-vs-enhanced key-name drift. Analog to Group 2400 close `docs/topics/auth.md` + §Auth autoblock + narrative subsection per S2499 AU-D2 + AU-D7. **Cat C boundary evidence supports the candidacy; Chris-D-verdict at S2599 xx99 close (proposal-only per S2500 §6 P-1 discipline).**

**R9 — [S2599 xx99 close anchor-update recommendation] `platform_architecture_inventory.md` §3.22 API Layer REVISE (per Cat A §14.4 F4 + Cat B §19.3 R8 + Cat C extension).**

Cat A + Cat B combined revision candidate extended by Cat C CONTRACT-side sub-layer evidence: envelope-shape heterogeneity + refresh contract-absent + logout envelope divergence + storageKeys cleanup 6.7% + Clear-Site-Data zero-emission. Cat A + Cat B + Cat C combined revision candidate at S2599 xx99 anchor-update batch.

**R10 — [Post-arc T-slot maintainer-decision batch] F-D-SIDEBAR-1 backend-token-revoke fix.**

Cat C RE-VERIFIED F8 IDENTICAL at HEAD (Sidebar user-menu does NOT call `authApi.logout()`). Single-line addition per S2404 §19.2 P0-B + S2502 §19.2 preserved. Post-arc T-slot maintainer-decision batch item; NOT owned by Cat C for execution.

**R11 — [S2503 Cat C findings-appendix per playbook §11.2 pattern] F-C-VIP-1 enforcement mechanism candidates (evidence for shipping prerequisite).**

Cat C evidence per §14.7 F7 + S2403 §19.1 risk-gate preservation: F-C-VIP-1 must close before any expiry-signal-bearing UX ships.

**Boundary note (Rigby SIGN cycle 1 Q18 STRENGTHEN fold):** the following mechanisms are listed to describe *where enforcement could technically occur*; Cat C does not select or prefer an option.

Enforcement mechanism candidates (evidence-only, not prescription):
- (a) Middleware check at `core/vip_middleware.py:__call__` — adds `account_expires_at < timezone.now()` check + returns 401/403 with envelope-shape-of-choice.
- (b) Periodic Celery beat task — sweeps expired VIPInvite rows nightly + revokes tokens.
- (c) Model `is_valid` property extension — adds `account_expires_at` check to existing property at `models_vip_invite.py:95-103`; requires per-caller adoption.
- (d) Combination (a) + (b) — middleware for runtime enforcement + beat for cleanup.

**Selection criteria (Rigby SIGN cycle 1 Q18 STRENGTHEN fold — rubric for xx99):** enforcement must be (a) server-authoritative, (b) observable / auditable, (c) compatible with current auth model, and (d) safe under partial deploy.

**Decision owner:** selection of enforcement locus is deferred to xx99 Chris-D verdict.

Cat C enumerates candidates; Chris-D-verdict at xx99 or post-arc dedicated ADR.

### 19.4 Boundary questions Cat C must NOT resolve (§16 anti-scope guardrails)

Cat C discovers scope-magnets; Cat C enumerates evidence only:

1. **Which envelope shape family should be canonical?** R2 above — Chris-D-verdict at xx99.
2. **Should a refresh endpoint be added?** R3 above — dependent on R1 α/β/γ verdict.
3. **Which Clear-Site-Data emission locus to adopt?** R4 above — Chris-D-verdict at xx99.
4. **Should basic and enhanced logout consolidate?** R7 above — post-arc T-slot decision.
5. **Should `EXCEPTION_HANDLER` be customized at REST_FRAMEWORK settings level?** Adjacent to R2 — Cat A downstream.
6. **Should the SHAPE-BLIND interceptor be replaced with shape-aware envelope-normalizer?** R5 — Cat D S2504 mechanism scope; Cat C provides evidence.
7. **Should F-C-VIP-1 enforcement land pre-α/β/γ ratification or post-?** Risk-gate constraint says pre- for expiry-signal-bearing UX; ORDER-of-operations question is Chris-D-verdict at xx99.
8. **Should client-side cross-tab logout coordination adopt BroadcastChannel or storage-event listener?** CF-C5 to Group 2200 post-arc T-slot; Cat C evidence-collects mechanisms.

---

## 20. Appendix

### 20.1 Files inspected (HEAD-verified at `ee7cc0a01812c737bc28798250c100f9cc74d812`)

**Backend:**
- `core/api_responses.py` (234 lines, full read; parent-Claude).
- `core/auth_views.py` (lines 65-130 focused read; parent-Claude).
- `core/auth_views_enhanced.py` (lines 535-560 focused read; parent-Claude).
- `core/settings.py` (lines 645-669 DRF settings; Agent 2).
- `core/middleware.py` + `core/middleware_error_capture.py` (middleware chain enumeration; Agent 2).
- `core/urls.py` (line-scan for auth-related routes; parent-Claude + Agent 3).
- `core/models_vip_invite.py` (lines 26-27, 71-103; Agent 1 + Agent 6).
- `core/models_mobile.py` (MobilePushToken.revoked_at field; Agent 1).
- `core/services/pa_tool_schemas.py` (lines 4716-4750 session_tool; Agent 3).
- `core/tasks.py` + `core/tasks*.py` (grep for auth/session cleanup tasks; Agent 3).
- `core/celery.py` (grep for periodic auth-cleanup; Agent 3).
- `core/management/commands/**` (grep for auth-cleanup commands; Agent 3).

**Frontend:**
- `frontend/src/lib/api.ts` (lines 1-100 request + response interceptor; parent-Claude).
- `frontend/src/stores/authStore.ts` (lines 34-51 logout action + persist config; Agent 1 + Agent 4).
- `frontend/src/stores/navigationStore.ts` (persist config; Agent 4).
- `frontend/src/stores/paStore.ts` (syncUser + persist config; Agent 4).
- `frontend/src/components/layout/Sidebar.tsx` (line 356 logout onClick; parent-Claude direct grep).
- `frontend/src/main.tsx` + `frontend/src/App.tsx` (QueryClient config + ErrorBoundary absence; Agent 6).
- `frontend/src/pages/CommandCenterPage.tsx` (VOICE_SETTINGS_KEY at :166; direct grep).
- `frontend/src/components/PanelDebugDrawer.tsx` (DEV_KEY at :6; direct grep).
- 15-surface storageKeys per-key file:line grep (Agent 4).

**Docs:**
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 20-section template + §13 6-parallel-Explore-sweep + §14 verifier-loop + §15 SIGN cadence + §16 draft-first workflow.
- `docs/research/domains/api/2500_api_domain_scoping.md` (§3.C Cat C mission + §5 sequence + §6 P-1 through P-11; parent-Claude).
- `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md` (§14.6 F6 4-shape 401 heterogeneity + §19.1 R2 + §19.2 R4; Agent 5).
- `docs/research/domains/api/2502_api_frontend_client_architecture_design_prep_audit.md` (§14.3 F3 SHAPE-BLIND interceptor + §19.2 R4 R6; parent-Claude + Agent 5).
- `docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md` (§14.1 findings + §14.2 15-surface + §14.3 21-loci + §19.1 α/β/γ + F-C-VIP-1 + F-C-STORE-1; parent-Claude + Agent 5).
- `docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md` (§19.1 typed-error-envelope α/β/γ + whitelist-replacement α/β/γ; parent-Claude + Agent 5).
- `docs/research/domains/auth/2499_auth_canonical_summary.md` (CF-C1 through CF-C7 + rank-1 P0 batch; Agent 5).
- `docs/topics/auth.md` (existence + coverage assessment; Agent 5 + parent-Claude verified 262 lines).
- `docs/topics/frontend.md` (coverage assessment; Agent 5).

### 20.2 Grep commands used (HEAD-verified)

| Pattern | Path | Result at HEAD |
|---|---|---|
| `refresh\|renew_token` | `core/urls.py` | 6 non-auth matches |
| `refresh\|renew_token` | `core/auth_views*.py` | 0 matches (F-C-REFRESH-1 CONFIRMED) |
| `TokenRefreshView\|SlidingToken\|SimpleJWT\|RefreshToken` | `core/**/*.py` | 0 matches |
| `Clear-Site-Data` | repo-wide | 21 total; 0 production-code (F-C-CSD-1 CONFIRMED) |
| `AUTH_REDIRECT_ENDPOINTS\|X-Suppress-Auth-Redirect\|authHandling\|noAuthRedirect` | `frontend/src/`, `core/` | 0 matches (whitelist-replacement α/β/γ greenfield) |
| `UnauthorizedError\|PermissionError\|ValidationError\|ServerError` custom classes | `frontend/src/` | 0 matches (typed-error-envelope α greenfield) |
| `Result<\|Either<\|Ok<\|Err<` | `frontend/src/` | 0 matches (typed-error-envelope β greenfield) |
| `ErrorBoundary\|componentDidCatch\|getDerivedStateFromError` | `frontend/src/` | 0 matches (F-D-BOUNDARY-1 + R6 IDENTICAL) |
| `AxiosError\|axios.isAxiosError` | `frontend/src/` | 0 matches (F-D-ENVELOPE-1 IDENTICAL) |
| `useQuery.*onError\|defaultOptions.*onError` | `frontend/src/` | 0 (or ~0-5%) matches (α/β/γ γ mechanism EXPERIMENTAL) |
| `account_expires_at__lt\|account_expires_at <\|account_expires_at.__lt` | `core/**/*.py` | 0 matches (F-C-VIP-1 CONFIRMED zero enforcement) |
| `session_tool.retire\|retire_conversation\|session_active=False` in logout paths | `core/auth_views*.py` | 0 matches (F-C-PA-CONV-1 CONFIRMED) |
| `MobilePushToken.*revoked_at.*=` in logout paths | `core/auth_views*.py` | 0 matches (F-C-MOBILE-1 CONFIRMED) |
| `EventStream.*` in auth flows | `core/auth_views*.py` + `core/auth_middleware.py` | 0 matches (F-C-EVENT-1 + CF-C3 CONFIRMED) |
| `api\.interceptors\.request\|api\.interceptors\.response` | `frontend/src/` | 2 pairs (1 for auth+logging in api.ts; 1 for logging ring buffer at api.ts:3990-4048 per Cat B §14.5) |
| `BroadcastChannel\|addEventListener.*storage` | `frontend/src/**` production | 0 matches (F-C-TAB-1 CONFIRMED) |
| `APIResponseEnvelope\.` | `core/` | ~14 sites |
| Basic vs Enhanced key-name divergence | `core/auth_views*.py` | Basic: `{'detail'}` at 91/94; Enhanced: `{'message'}` at 554 (F6 NEW at HEAD) |
| Sidebar onClick logout | `frontend/src/components/layout/Sidebar.tsx:356` | `setUserMenuOpen(false); syncUser(null); logout()` — NO `authApi.logout()` (F-D-SIDEBAR-1 CONFIRMED) |

### 20.3 Docs inspected

Listed at §20.1.

### 20.4 Sampling completeness note

See §1.1. Exhaustive-verified vs targeted vs sampled taxonomy declared inline.

### 20.5 Conflicts between sources (verifier-loop pre-Rigby-SIGN discipline)

**Seven sub-agent conflicts resolved before Rigby SIGN routing** (parent-Claude verifier-loop per playbook §14; **Rigby SIGN cycle 1 Q19 STRENGTHEN fold** — tie-break method added inline per conflict; conflict #3 clarifying clause added):

1. **Envelope shape family enumeration disagreement.** Agent 1 named the 4 shape families as (a) DRF detail / (b) APIResponseEnvelope / (c) bare JsonResponse `{success, error: str}` / (d) responses.py `unauthorized_error()`. Agent 4 named them as (a) APIResponseEnvelope / (b) direct JsonResponse error dict / (c) DRF standard Response / (d) implicit legacy. **Adopted S2501 §14.6 F6 canonical:** (A) DRF default `{"detail": "..."}` (from `AuthenticationFailed`/`NotAuthenticated`) + (B) APIResponseEnvelope typed `{"success": false, "error": {"code": ..., "message": ...}}` + (C) bare DRF dict with `{message: str}` (enhanced logout style) + (D) JsonResponse `{"success": false, "error": str}` (unstructured error). Cat C §14.1 F1 adopts S2501 mapping. **Tie-break method:** playbook canonical adoption (S2501 F6 pre-approved shape enumeration).

2. **803 vs 913 downstream denominator confusion.** Agent 4 wrote "913 direct api calls" as if it were a delta from S2404. **Resolved:** S2404 canonical = 913 total repo grep for `api.<verb>()` = **856 defs inside api.ts** + **57 direct consumer outside api.ts**; consumer-side total = 57 + 667 (useQuery/useMutation) + 79 (raw fetch) = **803**. Agent 4's "913" was mislabeled "direct". Adopted 803 as consumer denominator (§1.1 canonical). **Tie-break method:** repo-wide grep count + S2404 F-D-CALL-1 canonical denominator preservation.

3. **12th localStorage key location drift.** Agent 4 reported `showDebugPanels` at `PanelDebugDrawer.tsx:6` (const declaration site); S2403 baseline at `:10` (localStorage.getItem call site). Both file:line valid for same key. **Conflict #3 resolution (Rigby Q19 STRENGTHEN fold — clarifying clause):** both the **declaration site** (where the key constant / name is defined) and the **usage site(s)** (where it is read / written) are recorded, because line drift often affects one without the other; this preserves reproducibility for future greps and avoids false "missing key" claims. **Tie-break method:** direct HEAD read + adoption of both file:line references.

4. **VOICE_SETTINGS_KEY line drift.** Agent 4 found `assistant-voice-settings` at `CommandCenterPage.tsx:166` (const declaration); S2403 baseline at `:190`. **Verified at HEAD:** const declaration is at `:166` (parent-Claude direct grep). Adopted `:166` as HEAD-canonical; S2403 baseline `:190` reflects pre-HEAD line count. Line-drift is −24 lines due to code churn. **Tie-break method:** direct HEAD read.

5. **Agent 1 "12 vs 11 direct keys" ambiguity.** Agent 1 reported "11 direct keys confirmed, 1 direct unconfirmed (possible false negative)". **Resolved via Agent 4 exhaustive per-key grep:** all 12 direct keys confirmed at HEAD; the "1 unconfirmed" was `showDebugPanels` (Agent 1's grep did not catch it; Agent 4's per-key grep did). Adopted Agent 4's 15-of-15 confirmed baseline. **Tie-break method:** exhaustive per-key grep + S2403 baseline preservation.

6. **docs/topics/auth.md existence disagreement.** Agent 5 said "YES exists with 4 subsections (created at S2499 close per AU-D2)"; unclear from other agents. **Verified via parent-Claude direct read:** file exists at `docs/topics/auth.md`, 262 lines, 13,170 bytes, last modified 2026-07-05. Confirmed 4 subsections per Agent 5 baseline. Adopted YES-EXISTS at §11.1. **Tie-break method:** direct filesystem stat + full-file read.

7. **basic vs enhanced logout response shape difference.** Multiple agents noted the divergence but did NOT flag it as a Cat C-relevant DRIFT. **Parent-Claude elevated to §14.6 F6 NEW finding** — the key-name difference (`detail` vs `message`) between basic and enhanced logout at HEAD is a within-domain shape drift that Cat C should surface. **Tie-break method:** parent-Claude direct file read + elevation to Cat C finding.

All 7 conflicts resolved pre-Rigby-SIGN per playbook §14 verifier-loop discipline.

### 20.6 Verifier-loop corrections (Rigby SIGN cycle 1 fold notes)

**Rigby SIGN cycle 1 executed 2026-07-05.**

- **Fresh isolation pin:** `pa-b19aa931a54a436a` (minted at S2503 open via `session_tool.create_fresh` per playbook §15 SIGN-isolation discipline; TWENTIETH-consecutive dedicated fresh SIGN pin candidate).
- **Cadence:** 4-batch × 5-Q = 20 Q per S2201–S2502 ELEVEN-consecutive tested pattern (TWELFTH-consecutive application).
- **Retirement:** via `session_tool.retire` at cycle close (TWENTIETH-consecutive dedicated fresh SIGN pin retirement candidate).
- **Verdict:** SIGN-WITH-EDITS at ~0.86 confidence. Cycle 2 NOT required per Rigby verdict.
- **Tally:** 20 Q → 1 AGREE (Q3) + 18 STRENGTHEN (Q1, Q2, Q4-Q19) + 1 Q20 combined verdict-format response. All 20 folds landable pre-Chris-ratification.

### 20.6.1 Standard Rigby verdict format (Q20)

- **Overall confidence:** ~0.86 (high, bounded by non-prescriptive posture and HEAD-evidence discipline).
- **Most accurate part:** F1 / F3 / F4 / F5 evidence pack + the explicit boundary / non-goals framing; strongest signal is "co-existing contract families + shape-blind interceptor + refresh / CSD absence" with file:line anchors.
- **Weakest part:** Any language that implies necessity ("ONLY family", "blocking prerequisite") where the dependency is contingent on xx99's mechanism choices. Softened via Q14 + Q13 + Q17 folds.
- **Missing area:** A minimal "decision rubric" for xx99 on how to choose between envelope families / refresh necessity (criteria-only, not recommendation). Cat C gestured at dependencies; adding criteria improves utility without boundary breach. Added via Q18 selection-criteria fold.
- **Overstated maturity:** Any "blocking prerequisite" phrasing that reads deterministic rather than conditional-on-verdict; also any maturity table cell that implies a roadmap rather than a state snapshot. Softened via Q5 conditional-CRITICAL two-part trigger + Q13 coordination-note folds.
- **Understated maturity:** the verifier-loop conflict resolution rigor (§20.5) is a stronger reliability signal than the maturity labels may communicate. Q19 fold added tie-break method + conflict #3 clarifying clause.
- **Biggest architectural risk:** lack of explicit API contract source-of-truth causes silent drift across endpoints (401 shapes, logout messages, storage cleanup, CSD headers), making any γ-style mechanism brittle without normalization / exception-handling governance.
- **Most important next research:** confirm Cat D γ's *minimal required envelope schema* (what fields / keys are required) and whether γ permits multi-shape discrimination; this determines whether "lowest-friction" vs "requires normalization" is the correct framing for R2.
- **What Claude got wrong:** the "Family B is ONLY family that meets γ without shape-transformation" claim was over-committing; softened per Q14 fold to "lowest-friction fit under current γ assumptions". Ensure any "BLOCKING" language is explicitly conditional (Q5 + Q13 folds).
- **What must change before canonical:**
  1. Replace any normative verbs with observation-only (Q1 boundary note + non-goals bullets fold).
  2. Add explicit boundary wrappers around §19.3 option lists (Q8 + Q18 folds).
  3. Tighten conditionality language on R2 / R5 / R6 ("if xx99 selects X, then Y is required"; folds Q5 + Q13 + Q14).
- **Final verdict:** SIGN-WITH-EDITS. Cycle 2 not needed.

### 20.6.2 Fold ledger (20 folds landed pre-Chris-ratification)

| # | Q ref | Batch | Section | Fold summary |
|---|---|---|---|---|
| 1 | Q1 STRENGTHEN | 1 | §1 | Added explicit "Boundary note" + "Non-goals" bullets at §1 opening to preserve non-prescription discipline resilience even if a later sentence accidentally uses "should". |
| 2 | Q2 STRENGTHEN | 1 | §1.1 | Added Metric 8 (401 shape-family distribution) + Metric 9 (Interceptor shape-dependence rate = 0/1 SHAPE-BLIND) to Denominator Contract table; tracks adoption / distribution not just existence. |
| 3 | Q3 AGREE | 1 | §14.1 F1 | HIGH severity preserved as-is; no change. HIGH appropriate for contract-clarity impact; CRITICAL would imply immediate exploit / availability risk. |
| 4 | Q4 STRENGTHEN | 1 | §14.3 F3 | Reframed Cat A F-TOKEN-1 → Cat C F-C-REFRESH-1 lineage from clean arrow to "related but distinct" adjacency; expiry semantics and refresh contract can co-exist or be solved independently. |
| 5 | Q5 STRENGTHEN | 1 | §14.5 F5 | Tightened CONDITIONAL CRITICAL to explicit two-part trigger: (1) xx99 selects mechanism requiring shape-normalized payloads AND (2) interceptor remains shape-blind. Otherwise HIGH. Added Cat C note: "does not assert normalization is required". |
| 6 | Q6 STRENGTHEN | 2 | §14.2 F2 | Compressed per-surface line-drift reporting into single "Line-drift note (non-substantive)" summary; preserves evidence but scan-friendly. |
| 7 | Q7 STRENGTHEN | 2 | §14.6 F6 | Bumped severity LOW-MEDIUM → MEDIUM (contract drift); acknowledges same-semantic-different-key as real cross-surface parsing inconsistency without prescription. |
| 8 | Q8 STRENGTHEN | 2 | §19.3 R11 | Added explicit non-prescription "Boundary note" + "Decision owner" wrappers around 4-option F-C-VIP-1 enforcement mechanism candidates list. |
| 9 | Q9 STRENGTHEN | 2 | §14.8 F8 | Added "Ownership note" — F-D-SIDEBAR-1 expected owner = Cat D (frontend execution / contract alignment); preserves post-arc T-slot sequencing without prescriptive reassignment. |
| 10 | Q10 STRENGTHEN | 2 | §13 maturity table | Consolidated logout envelope + Clear-Site-Data + cross-tab under parent "Logout contract completeness" dimension with sub-bullets; added NEW dimension "Contract SoT / ownership maturity" (EXPERIMENTAL-to-PARTIAL). |
| 11 | Q11 STRENGTHEN | 3 | §9 CF table | Added CF-C8 Content / Publishing row (Group 1600 consumer surface); tightened CF-C7 wording to acknowledge coordination surface potential while preserving "boundary preserved" claim. |
| 12 | Q12 STRENGTHEN | 3 | §9.1 α/β/γ intersection | Replaced implicit 27-combination enumeration with "Intersection model" operational statement: 3 decision spaces + 1 known nesting + "all other selections are orthogonal unless explicitly coupled by xx99 verdict". |
| 13 | Q13 STRENGTHEN | 3 | §9.2 R6 dual-ownership | Added "Coordination note (non-prescriptive)" — Group 2200 must ship *some* stable error-boundary hook / contract first, then Cat D / Cat C attach envelope normalization + auth recovery. Preserves who-blocks-whom sequencing without prescribing framework design. |
| 14 | Q14 STRENGTHEN | 3 | §19.1 R2 | Softened "Family B is ONLY family that meets γ" over-commitment to "lowest-friction fit under current γ assumptions"; acknowledges Families A/C/D could be made compatible via shape-normalization OR γ multi-key discrimination. |
| 15 | Q15 STRENGTHEN | 3 | §17 item 3 | Reframed server-side vs client-side logout observers as "complementary but under-specified coupling" rather than "implicitly-co-completing"; added explicit risk note (partial logout: server-invalidated + client-persistent OR vice versa; F-D-SIDEBAR-1 is concrete instance). |
| 16 | Q16 STRENGTHEN | 4 | §15 rank #5 F7 | Added risk-gate qualifier parenthetical: F-C-VIP-1 is deployment-gating constraint but not broadest cross-surface driver; ranked #5 on surface-area not go/no-go leverage. Preserves ranking intent without silent reordering. |
| 17 | Q17 STRENGTHEN | 4 | §16 | Added Level 0 explicit-contract-missing anchor sentence: "the platform currently lacks an explicit, centralized API contract for (error envelope + refresh + logout semantics)"; preserves boundary while surfacing primary "contract should exist?" decision axis for xx99. |
| 18 | Q18 STRENGTHEN | 4 | §19.3 R11 | Added "Selection criteria (for xx99)" rubric: enforcement must be (a) server-authoritative, (b) observable / auditable, (c) compatible with current auth model, (d) safe under partial deploy. Gives xx99 a rubric without Cat C choosing. |
| 19 | Q19 STRENGTHEN | 4 | §20.5 | Added tie-break method inline per conflict (playbook canonical adoption / repo-wide grep / direct HEAD read / exhaustive per-key grep / direct file read); added conflict #3 clarifying clause on declaration-site vs usage-site preservation. |
| 20 | Q20 combined verdict-format response | 4 | §20.6.1 (populated) | SIGN-WITH-EDITS at ~0.86 confidence. Cycle 2 NOT required. Standard Rigby verdict format populated at §20.6.1. All 20 folds landable pre-Chris-ratification. |

**All 20 folds landable pre-Chris-ratification.** Cycle 2 not required per Rigby cycle-1 ~0.86 confidence + all folds non-controversial (mostly phrasing / structure / boundary-preservation per Q20 verdict).

### 20.7 S2503 arc metadata

- **Arc:** Research Group 2500 (API — Contract SoT + Silent-401 Downstream Remediation + Session-Lifecycle API Contracts + Per-Endpoint Permission-Floor Registry Design-Prep + REST↔WS T7 Joint 2500+2600).
- **Child slot:** P3 Cat C — Error-Envelope + Refresh + Logout API Contracts Design-Prep.
- **Predecessor:** S2500 parent scoping + S2501 P1 Cat A Backend API Contract SoT Design-Prep + S2502 P2 Cat B Frontend API-Client Architecture Design-Prep.
- **Successors:** S2504 P4 Cat D Permission-floor registry design-prep + REST↔WS T7 joint (next); S2599 xx99 canonical summary + arc close.
- **Arc pin:** `pa-a03b111768464b3f` ACTIVE + PRESERVED through S2503 per playbook §16 arc-standard behavior; TWELFTH formal arc pin under Research OS.
- **SIGN pin:** `pa-b19aa931a54a436a` (minted at S2503 open; TWENTIETH-consecutive dedicated fresh SIGN pin candidate).
- **Playbook §11.2 20-section child-audit template TWENTY-SECOND-consecutive application** after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401+S2402+S2403+S2404+S2501+S2502 twenty-one prior. Codification language conditionality preserved (Cat B §20.7 Rigby SIGN cycle 1 batch 4 Q19 fold precedent): 22-consecutive stable-shape indicates continued strong stability signal; promotion to TEMPLATE-CANONICAL requires xx99 / Chris trigger satisfaction beyond mere repetition. Cat C does NOT self-codify. MC-5 CODIFICATION-CONFIRMED-with-scope-guardrails candidate extension 21 → 22 registered for xx99 review.
- **Rigby SIGN cycle 1 COMPLETE** (2026-07-05): SIGN-WITH-EDITS at ~0.86 confidence via dedicated fresh SIGN isolation pin `pa-b19aa931a54a436a` — TWENTIETH-consecutive dedicated fresh SIGN pin retirement candidate. 20 folds landed pre-Chris-ratification per playbook §20.6 fold ledger discipline (see §20.6.2 fold table). Cycle 2 NOT required.
- **TWELFTH-consecutive 4-batch × 5-Q cadence application** candidate after S2201+S2202+S2203+S2204+S2401+S2402+S2403+S2404+S2499+S2501+S2502 eleven prior. Codification framing CONDITIONAL pending xx99 review per Cat B Q19 discipline preservation.
- **Playbook §13 6-parallel-Explore-agent sweep** executed at draft-open per S2201–S2502 pattern; 6 sub-agents dispatched in single message (Models + Persistence; Services + Runtime Flows; APIs + Tools + Tasks + Commands; Integrations + Cross-Domain; Documentation + Prior Research; Drift + Debt + Ownership + Maturity).
- **Playbook §14 verifier-loop** applied pre-Rigby-SIGN with 7 sub-agent conflicts resolved (§20.5).
- **HEAD `ee7cc0a0`** at draft-open (post-S2502 close + S2502 docs cascade).
- **Cat C boundary discipline:** design-preparation + boundary evidence only per playbook §5 phase discipline + S2501 Cat A + S2502 Cat B precedent + S2500 §7 anti-scope; no code changes; no runtime modifications; no remediation prescription; option-space enumeration + Chris-D-verdict-request evidence for S2599 xx99 close.
- **Verbs used:** enumerate / inventory / measure / classify / verify / re-verify / defer / propose evidence-collection. **Verbs NOT used:** decorate / implement / migrate / adopt / remediate / require / fix / correct (except when directly quoting predecessor documents' recommendations or when describing observed HEAD state).
