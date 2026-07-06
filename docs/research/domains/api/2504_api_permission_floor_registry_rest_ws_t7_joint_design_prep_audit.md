---
title: "API Permission-Floor Registry + REST↔WS T7 Joint Design-Prep — S2504 P4 Cat D Child Audit"
status: active
authority: research
research_group: S2504
child_slot: P4
chris_ratification: "commit it" 2026-07-06 (post-Rigby-SIGN-cycle-1-close via retired SIGN pin pa-1aad569644364682)
arc: Research Group 2500 (API — Contract SoT + Silent-401 Downstream Remediation + Session-Lifecycle API Contracts + Per-Endpoint Permission-Floor Registry Design-Prep + REST↔WS T7 Joint 2500+2600)
head_sha: 87624a3d
open_date: 2026-07-05
companion_docs:
  - docs/research/domains/api/2500_api_domain_scoping.md
  - docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md
  - docs/research/domains/api/2502_api_frontend_client_architecture_design_prep_audit.md
  - docs/research/domains/api/2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md
  - docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md
  - docs/research/domains/auth/2499_auth_canonical_summary.md
  - docs/research/domains/frontend/2202_frontend_websocket_consumer_ui_render_hint_envelope_audit.md
  - docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
verifier_loop:
  - "Parent-Claude 6-parallel-Explore-sweep dispatched per playbook §13 (Agents 1–6 covering Models+Persistence / Services+Runtime / APIs+Tools+Tasks+Commands / Integrations+Cross-Domain / Documentation+Prior-Research / Drift+Debt+Ownership+Maturity)."
  - "Parent-Claude verifier-loop applied per playbook §14: 4 sub-agent conflicts resolved via definitive HEAD greps (PUBLIC_PATHS 263 vs 265 → 265 via Python-parser confirmed; REVIEWER_BLOCKED_PATHS 12 vs 18 → 7 via Python-parser confirmed = -5 REDUCTION drift from S2402; WS routes 51 vs 120 → 120 confirmed = -5 drift from S2202 125; @authentication_classes([]) 4 vs 3 files → 3 files at HEAD = 1-file REDUCTION drift from S2402 baseline as core/views_nervous.py was cleaned up)."
  - "Rigby SIGN cycle 1 PENDING via dedicated fresh SIGN isolation pin pa-1aad569644364682 (TWENTY-FIRST consecutive dedicated fresh SIGN pin candidate); 4-batch × 5-Q = 20-Q child-audit cadence per S2201-S2503 twelve-consecutive tested pattern (THIRTEENTH-consecutive candidate)."
---

# Session 2504 — Group 2500 API Cat D Permission-Floor Registry + REST↔WS T7 Joint Design-Prep

**HEAD SHA at S2504 open:** `87624a3d` (commit: `docs: refresh docs cascade artifacts after S2503 close (#2926)`).

**Boundary discipline (mirror Cat A + Cat B + Cat C posture):** Cat D enumerates + inventories + measures + classifies + defers + proposes evidence-collection; Cat D does NOT prescribe (a)/(b)/(c) permission-floor Cat B option selection, per-endpoint registry mechanism selection, REST↔WS message-contract strictness selection, or execution locus for whitelist-replacement γ mechanism. All "recommendations" in §19 are Chris-D-verdict-request evidence for S2599 xx99 close, NOT directives. Verbs stay `enumerate / inventory / measure / classify / verify / re-verify / defer / propose evidence-collection`.

**Playbook §11.2 20-section child-audit template TWENTY-THIRD-consecutive application** after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401+S2402+S2403+S2404+S2501+S2502+S2503 twenty-two prior.

---

## §1 Executive Summary

At HEAD `87624a3d`, the Donkey Betz platform has **no dedicated per-endpoint permission-floor registry infrastructure** for the (c) LONG-TERM GOVERNANCE layer (S2499 CF-B1) beyond isolated exemplars such as `FleetCapabilityRequired`, and **no REST↔WS message-contract strictness SoT** at the T7 joint layer (S2203 §17.3 verbatim declaration). Both categories remain **greenfield design-prep candidates** for S2599 xx99 Chris-D-verdict (per Rigby SIGN cycle 1 Q1 STRENGTHEN fold — "zero" language softened to "no dedicated ... beyond isolated exemplars" to preserve boundary against categorical over-claim).

The permission-floor stack operates across four **architecturally independent** layers with no cross-layer SoT: (i) DRF DEFAULT_PERMISSION_CLASSES = `[IsAuthenticated]` at `core/settings.py:652-653` (implicit-inheritance baseline preserving F-B-CRIT-1 ~80-90% rate), (ii) explicit `@permission_classes` DRF decorator (**838 sites via `@api_view` across 106 files** + **74 class-attribute ViewSet declarations across 20 files**), (iii) path-list gates in `core/auth_middleware.py` (6 lists: PUBLIC_PATHS 265 + PUBLIC_PATHS_EXACT 2 + OPTIONAL_AUTH_PATHS 7 + STAFF_REQUIRED_PATHS 3 + REVIEWER_BLOCKED_PATHS 7 + REVIEWER_ALLOWED_PATHS 1 = **285 entries total**, down from S2402 290-baseline via -5 REVIEWER_BLOCKED_PATHS reduction), (iv) 3 custom Permission classes (`FleetSignatureRequired` + `FleetCapabilityRequired` at `core/services/fleet_auth_drf.py:176, 215` + `PublicIntelTokenAuth` at `core/views_public_intelligence.py:37`).

The REST↔WS T7 joint stack shows **complete architectural disjointness**: REST emits `APIResponseEnvelope` typed shape (`core/api_responses.py:53-98`, 9 hand-invoked sites) alongside 4 competing 401 shape families (RE-VERIFIED IDENTICAL from S2501 F6 / S2503 F1); WS emits **raw `json.dumps` dicts** across **87 Consumer class definitions across 55 files** (S2202 baseline preserved; **0/40 envelope conformance** at consumer-class sampling; **120 WS route entries** across 5 routing.py files, -5 drift from S2202 125 baseline).

Cat D inherits 6 BINDING findings from Group 2400 Auth arc close via S2499 §8.1 rank-1 P0 batch: F-B-CRIT-1 permission-floor implicit-inheritance ~84.4%, F-B-CRIT-2 silent-401 SYSTEMIC (extended to 803-scale by Cat D S2404 F-D-CALL-1 and preserved to S2503), F-B-HIGH-1 STAFF_REQUIRED_PATHS 2-of-3 PHANTOM (findings-appendix per Rigby Q1 P4-retitle fold), F-B-HIGH-2 `/api/v1/betting/place/` PUBLIC + REVIEWER_BLOCKED inversion dead-code, F-B-HIGH-3 workspace-membership implicit gate (CF-B2 → Group 2600 PA), F-B-HIGH-4 `@authentication_classes([])` stacking (findings-appendix, 1-file REDUCTION at HEAD).

The **primary Cat D design-prep contribution** is (i) full enumeration of the DECLARATION-side + PATH-LIST-side + CUSTOM-CLASS-side + WS-CONSUMER-side permission-floor surface at HEAD, (ii) formal identification of `FleetCapabilityRequired.for_capability()` as **the concrete production exemplar for Cat B (c) per-endpoint registry pattern** (capability-per-endpoint factory method demonstrating the (c) design is not theoretical), (iii) enumeration of the REST↔WS T7 joint scope (120 WS route entries + 87 Consumer classes + 40+ emit sites sample all operating with zero cross-transport contract SoT), and (iv) preservation of Cat C S2503 §16 Level 0 explicit-contract-missing anchor extended from "error envelope + refresh + logout semantics" to include "per-endpoint permission-floor + REST↔WS message contract strictness."

**Summary observation at HEAD (per Rigby SIGN cycle 1 Q1 STRENGTHEN fold — "bottom line" softened to observation phrasing):** authorization appears operational, but observability + SoT for per-endpoint permission-floor intent is not systematically declared at the (c) LONG-TERM GOVERNANCE layer (F-B-CRIT-1 observability gap RE-CONFIRMED at HEAD — no registry model + no admin UI + no centralized floor introspection beyond isolated exemplars); the REST↔WS transport pair operates in **architecturally parallel isolation** with no shared cache + no cross-transport sync + no invalidation-hook linkage + no shared message-contract SoT. Cat D S2504 delivers boundary evidence + decision candidates for Chris-D-verdict at xx99 on both axes (permission-floor registry (a)/(b)/(c) + REST↔WS T7 Path A/B/C strictness); execution + option selection remain undecided; deferred to post-arc T-slots + xx99 verdict ratification.

### §1.1 Denominator Contract

For every rate-claim in this document, unit-of-analysis + scope + verification-method disclosed inline. Load-bearing denominators reused at HEAD `87624a3d`.

**Denominator Definitions block (per Rigby SIGN cycle 1 Q2 STRENGTHEN fold — future readers must not overfit to the 49% number):**

- **D1: URL route count (core-only)** = 1,856 `path()|re_path()` entries in `core/urls*.py` (4 files). Not equivalent to unique view functions/classes; a single view can be attached to multiple routes.
- **D2: Permission decoration sites** = 838 `@permission_classes` decorator invocations across 106 files. Includes duplicate decorations on the same view (some views stack multiple decorator sets); NOT one-to-one with unique views.
- **D3: Class-attribute permission_classes sites** = 74 `permission_classes = [...]` declarations across 20 class-based ViewSets or GenericAPIView subclasses; each propagates to N action methods per ViewSet (not per-route direct correspondence).
- **D4: Unique view functions/classes** = UNKNOWN at Cat D S2504 (requires route→view normalization pass; deferred).
- **D5: WS route count** = 120 `path()|re_path()` in `**/routing.py` (5 files); not equivalent to unique Consumer classes.
- **D6: Consumer class definitions** = 87 `^class \w+Consumer(...)?:` matches across 55 files; not equivalent to unique active emit sites (S2202 baseline "~40 unique consumer classes with `group_send`" measures a different sub-denominator).

| Metric | Denominator | Verification | Notes |
|---|---|---|---|
| URL route count (core-only) | 1,856 | Parent-Claude ripgrep `^\s*(?:path\|re_path)\(` in `core/urls*.py` at HEAD | 4 files (urls.py:1,784 + urls_unified.py:44 + urls_real_data.py:9 + urls_provenance.py:19); PLATFORM_INVENTORY autoblock 1,864 → -8 drift <1% non-load-bearing |
| URL route count (all-repo) | 2,031 | Parent-Claude ripgrep across all `**/urls*.py` at HEAD | 26 files; includes sports/urls.py:17, intelligence/urls.py:26+5=31, agents/urls.py:11+14=25, mythology/urls.py:17, self_awareness/urls.py:11, ai_platform/urls.py:10, etc. |
| WS route count | 120 | Parent-Claude ripgrep `^\s*(?:re_)?path\(` in `**/routing.py` | 5 files (core/routing.py:107 + ai_core/intelligence/routing.py:5 + ai_core/routing.py:3 + sports/routing.py:3 + intelligence/routing.py:2); S2202 baseline 125 → -5 drift |
| Consumer class definitions | 87 | Parent-Claude ripgrep `^class\s+\w+Consumer(?:\(.*\))?\s*:` type=py | Across 55 files; core/consumers_base.py alone has 20 Consumer class definitions; S2202 baseline "~40 unique consumer classes with `group_send`" = subset of 87 (unique classes with active emit sites); Agent 3 sampled 47 unique classes |
| Explicit `@permission_classes` decorator sites | 838 | Parent-Claude ripgrep `@permission_classes` type=py | Across 106 files; includes `@api_view` stacked decorations; S2501 sampled "0 of 30 have explicit `@permission_classes`" in money-path + governance-path + PA-path sample (biased toward implicit-inherit paths) |
| Class-attribute `permission_classes = [...]` declarations | 74 | Agent 1 targeted enumeration | Across 20 files; class-based ViewSet + generic view subclasses; distinct from decorator-based function views |
| `@api_view` decorator sites | 838 | Parent-Claude ripgrep type=py | Function-based DRF view total; used as denominator for decorator co-declaration rate |
| Custom Permission classes | 3 | Agent 1 targeted enumeration | `FleetSignatureRequired` at `core/services/fleet_auth_drf.py:176`, `FleetCapabilityRequired` at `core/services/fleet_auth_drf.py:215`, `PublicIntelTokenAuth` at `core/views_public_intelligence.py:37` |
| Path-list gate entries (total) | 285 | Parent-Claude Python-parser count | PUBLIC_PATHS 265 + PUBLIC_PATHS_EXACT 2 + OPTIONAL_AUTH_PATHS 7 + STAFF_REQUIRED_PATHS 3 + REVIEWER_BLOCKED_PATHS 7 + REVIEWER_ALLOWED_PATHS 1; S2402 baseline 290-total → -5 REVIEWER_BLOCKED_PATHS REDUCTION drift |
| Permission-floor 21-loci enforcement points | 21 (RE-VERIFIED IDENTICAL) | S2402 §14.5 baseline + Cat D HEAD grep | 10 WORKING + 6 PARTIAL + 4 EXPERIMENTAL + 3 MED-HIGH drift + 1 DEAD (S2402 classifications preserved at HEAD; no drift) |
| Silent-401 rate (consumer call-sites) | 803 | S2502 §20.4 RE-VERIFIED per S2503 §1.1; Cat D preserves | 57 direct + 667 useQuery/useMutation + 79 raw fetch; RE-VERIFY exhaustive count deferred to Cat D findings-appendix |
| 4 401 shape family count | 4 | S2501 §14.6 F6 RE-VERIFIED per S2503 §14.1 F1 | Family A DRF `{"detail":"..."}` + Family B APIResponseEnvelope typed + Family C bare `{"message":"..."}` + Family D `{"success":false,"error":str}`; RE-VERIFIED IDENTICAL at HEAD (3-session zero-delta since S2501) |
| CODEOWNERS Cat D file assignment | 6-of-10 (60%) | Agent 4 targeted CODEOWNERS read | Backend: 6-of-6 assigned (@clwest for `core/auth_middleware.py`, `core/services/fleet_auth_drf.py`, `core/ws_auth_middleware.py`, `core/api_responses.py`, `core/auth_views.py`, `core/auth_views_enhanced.py`); frontend: 4-of-4 assigned (`api.ts`, `authStore.ts`, `Sidebar.tsx`, `App.tsx`); 4 additional files UNASSIGNED (deferred to S2600+ per CODEOWNERS lines 8-13 explicit deferral: `useWebSocket.ts`, `cockpitApi.ts`, `cockpitQueries.ts`, `types/cockpit.ts`, `apiClient.ts`, `core/routing.py` implicit only via `*` fallback) |

**Sampling completeness:** Cat D used 6-parallel-Explore sweeps + targeted verifier-loop greps; did NOT perform exhaustive Cartesian per-endpoint enumeration (deferred to Cat D findings-appendix scope or post-arc T-slot execution). Per-endpoint declaration coverage at HEAD is not exhaustively enumerated; instead, Cat D preserves S2402 §14.5 F-B-CRIT-1 implicit-inheritance ~80-90% baseline + provides a stratified sample per Agent 3 (25-endpoint sample yielded 79.3% explicit-decorator rate; biased sample not extrapolable to platform-wide rate).

**Denominator reconciliation (per Rigby SIGN cycle 1 Q2 STRENGTHEN fold):** the 838/1,856 = 49% "route-indexed explicit surface ratio" is NOT the same measurement as S2402's ~84.4% implicit-inheritance estimate — S2402's ~84.4% is a **view-level inheritance inference** (per-view unique-declaration coverage); this doc's 838/1,856 is a **route-level site ratio** (per-route decoration-invocation count). **These are not directly comparable until unique-view mapping (D4) is computed.** **xx99 decision candidate:** whether to fund a route→view normalization pass to compute a single comparable explicitness metric — Cat D S2504 does NOT commit to this exhaustive audit (that becomes a prescription); Chris-D-verdict at xx99 owns the funding decision.

### §1.2 Do Not Misread

Three anti-misread guardrails specific to Cat D scope:

1. **Label independence rule (extends Cat C §1.2 note 1):** (a)/(b)/(c) across Cat B permission-floor decision-space is INDEPENDENT of Path A/B/C in S2203 §20.6 T7 REST↔WS strictness decision-space unless explicitly coupled by xx99 verdict. Cat B (c) per-endpoint registry could operate under REST↔WS Path A OR Path B OR Path C strictness posture; the two axes are orthogonal. Similarly, Cat D typed-error-envelope α/β/γ (S2404 §19.1 preserved) and Cat D whitelist-replacement α/β/γ (Rigby Q7 `authHandling` enum) are INDEPENDENT of permission-floor (a)/(b)/(c) selection. **The ONE established nesting from Cat C S2503 §9.1 (Rigby SIGN Q12 fold): Cat D γ = mechanism; Cat C β = UX policy nested inside γ default handler. All other pairings INDEPENDENT.**

2. **F-B-CRIT-1 IMPLICIT-INHERITANCE ~84.4% does NOT imply "explicit-decoration should be universal."** The finding statement is "84.4% of endpoints at HEAD have no explicit `@permission_classes` decorator and inherit from `DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]`." Cat D does NOT recommend explicit decoration everywhere. Explicit vs implicit is a downstream trade-off (declarability + governance vs boilerplate + churn). Chris-D-verdict at xx99 owns the (a)/(b)/(c) selection. Cat D enumerates the CURRENT state + trade-offs of each option; does NOT prescribe.

3. **T7 REST↔WS "same underlying pattern at different transports" does NOT imply "REST and WS must share message shapes."** The finding statement is "contract strictness axis (typed schema / runtime validation / envelope conformance) can be applied to both surfaces, and both currently lack SoT for integrity-critical / governance / money-path endpoints." Cat D does NOT recommend protocol-level convergence (that is explicitly out-of-scope per S2500 §6 P-6 boundary preservation). Cat D enumerates the parallel; enforcement rigor scaling per endpoint's mutation gravity is Chris-D-verdict at xx99. **Any protocol redesign or forced shape unification is out of scope for Cat D** (per Rigby SIGN cycle 1 Q3 STRENGTHEN fold — explicit out-of-scope guardrail); this document only inventories current disjointness and decision points for xx99.

---

## §2 Domain Purpose

**Cat D scope within Group 2500 API arc:** the CONTRACT-DECLARATION-DENSITY + CROSS-TRANSPORT-PARALLEL layer between Cat A DECLARATION-side (backend contract SoT + @extend_schema × @permission_classes intersection at REST layer) and Cat B CONSUMER-side (frontend api-client architecture + 803 call-sites + interceptor pattern) and Cat C CONTRACT-INTERSECTION layer (error envelope + refresh + logout semantics forming implicit contract mesh).

**What Cat D exists to answer:**

- What is the CURRENT state of per-endpoint permission-floor declaration ACROSS all 1,864 URL routes at REST + ~120 WS routes at ASGI layer?
- Where does the permission-floor "registry" live IMPLICITLY at HEAD — path-list gates (`PUBLIC_PATHS`), DRF DEFAULT, class-attribute inheritance, custom Permission classes — and what is the maturity + observability of each layer?
- What is the concrete production example that demonstrates Cat B (c) per-endpoint registry is architecturally VIABLE (not theoretical)?
- What is the REST↔WS T7 joint scope for message-contract strictness parallel — where does REST have typed contracts (APIResponseEnvelope) and where does WS not (raw `json.dumps` dicts) — and what is the surface of ~40 WS emit-site sample × ~803 REST call-site parallel?
- What Chris-D-verdict-request evidence should Cat D hand forward to S2599 xx99 close (permission-floor (a)/(b)/(c) selection + REST↔WS Path A/B/C strictness selection + F-B-HIGH-1/2 governance-batch decisions + F-B-HIGH-4 stacking-cleanup decisions)?

**What Cat D does NOT own:**

- Selection of (a)/(b)/(c) permission-floor option (Chris-D-verdict at xx99).
- Selection of Path A/B/C REST↔WS strictness posture (Chris-D-verdict at xx99).
- Execution of any P0-A/B/C item from S2499 §8.1 (execution deferred to post-arc T-slots).
- Envelope-shape SoT selection (Cat A scope + xx99 verdict).
- Refresh endpoint necessity (Cat C α/β/γ + xx99 verdict, coupled to session-lifecycle R1).
- Clear-Site-Data emission locus (Cat C 3-locus enumeration + xx99 verdict).
- F-C-VIP-1 enforcement locus (Cat C 4-option rubric + xx99 verdict or post-arc dedicated ADR).
- Protocol-level REST↔WS convergence (out-of-scope per S2500 §6 P-6).
- Backend token model rewrite (F-TOKEN-1 no `expires_at`; coupled to R3 xx99 verdict on refresh endpoint necessity).

---

## §3 Canonical Entry Points

### §3.1 Backend REST permission-floor entry points

| Entry point | File:line | Purpose |
|---|---|---|
| `DEFAULT_PERMISSION_CLASSES` | `core/settings.py:652-653` | DRF-wide implicit-inheritance baseline: `['rest_framework.permissions.IsAuthenticated']`; sets the implicit floor for all endpoints that DO NOT declare `@permission_classes` explicitly. |
| `DEFAULT_AUTHENTICATION_CLASSES` | `core/settings.py:658-661` | DRF-wide authentication: `MobileTokenAuthentication` + `CsrfExemptSessionAuthentication`. Note NO EXCEPTION_HANDLER override — DRF's built-in handler emits `{"detail": "..."}` (Family A) for inherited-default authorization failures. |
| `UnifiedTokenAuthenticationMiddleware` | `core/auth_middleware.py:85` | Django middleware — first line of authorization defense; enforces path-list gates BEFORE DRF permission-class dispatch. |
| Path-list constants (6 constants) | `core/auth_middleware.py:94-561` | PUBLIC_PATHS (line 94-509, 265 entries) + PUBLIC_PATHS_EXACT (line 513-516, 2 entries) + OPTIONAL_AUTH_PATHS (line 521-538, 7 entries) + STAFF_REQUIRED_PATHS (line 541-545, 3 entries) + REVIEWER_BLOCKED_PATHS (line 548-556, 7 entries) + REVIEWER_ALLOWED_PATHS (line 559-561, 1 entry). Total 285 entries. |
| `@permission_classes` decorator | 838 sites across 106 files | Function-based `@api_view` explicit permission declaration. |
| `permission_classes = [...]` class attribute | 74 sites across 20 files (Agent 1 enumeration) | Class-based ViewSet + GenericAPIView explicit permission declaration; inherits to all action methods on the ViewSet unless overridden per-action. |

### §3.2 Custom Permission classes (3 total)

| Class | File:line | Purpose |
|---|---|---|
| `FleetSignatureRequired` | `core/services/fleet_auth_drf.py:176` | Reject requests lacking verified fleet identity; gates fleet-only endpoints. Consumed by `core/views_fleet_artifacts.py:294, 560` + `core/views_fleet_paid_interest.py:90`. |
| `FleetCapabilityRequired` | `core/services/fleet_auth_drf.py:215` | Require specific capability on fleet identity (e.g., `"artifacts.can_push"`). Exposes `.for_capability(*path: str)` classmethod returning `_Bound` subclass with `capability_path` tuple + `has_permission()` check against `FleetServiceIdentity` model. **Concrete production exemplar of a DRF-layer capability gating *mechanism*** (declarable intent + model-backed check) that could support a future per-endpoint registry — **however, no centralized registry/catalog, admin UI, CI/lint enforcement, or governance workflow was found at HEAD; this is not a complete Cat B (c) implementation.** (Per Rigby SIGN cycle 1 Q5 STRENGTHEN fold — softened to mechanism vs governance-system distinction.) **Exemplar of *mechanism*, not *governance system*.** |
| `PublicIntelTokenAuth` | `core/views_public_intelligence.py:37` | Public intelligence endpoints authentication (bearer token validation for third-party integrations). |

### §3.3 WebSocket auth entry points

| Entry point | File:line | Purpose |
|---|---|---|
| `application` (ASGI ProtocolTypeRouter) | `core/asgi.py:14-33` | ASGI mount; wraps HTTP + WebSocket + Channel layers. |
| `TokenAuthMiddlewareStack` (WS wrapper) | `core/asgi.py:28-32` | Applied to `websocket` protocol: `TokenAuthMiddlewareStack(URLRouter(websocket_urlpatterns))`. |
| `TokenAuthMiddleware` (Channels middleware) | `core/ws_auth_middleware.py:24` | Actual middleware class; extracts token from `?token=<token>` query string; validates via `get_user_from_token` ORM lookup. |
| `get_user_from_token` (validation helper) | `core/ws_auth_middleware.py:15-21` | `@database_sync_to_async` — Token.objects.get(key=token_key) → user; on `Token.DoesNotExist` returns `AnonymousUser()` (silent fallback; NO close-with-code). |
| `WebSocketAuthenticationMiddleware` (parallel HTTP middleware) | `core/auth_middleware.py:739, 785-800` | Alternative token extraction: query string OR `Authorization: Bearer/Token` header OR `X-Api-Key` custom header. |
| `REQUIRE_WEBSOCKET_AUTH` (dead setting) | `core/auth_middleware.py:762` | Settings-based required-auth gate; grep confirms **zero enforcement path at HEAD** — never referenced in `application()` return path (S2402 §14.5 21-loci table Cat D confirmation locus 20 "DEAD"). **T-slot candidate (post-arc / xx99):** decide whether to delete `REQUIRE_WEBSOCKET_AUTH` (dead) or re-enable it with explicit semantics + tests; Cat D records this as a dead-code classification, not an action recommendation. **No change is proposed here.** (Per Rigby SIGN cycle 1 Q4 AGREE fold — observation-only.) |
| WebSocket routing tables | 5 files: `core/routing.py:107` + `ai_core/intelligence/routing.py:5` + `ai_core/routing.py:3` + `sports/routing.py:3` + `intelligence/routing.py:2` = **120 total** WS route entries | All routed through TokenAuthMiddlewareStack via `websocket_urlpatterns` composition. |

### §3.4 Client-side WS subscription entry points

| Entry point | File:line | Purpose |
|---|---|---|
| `useWebSocket` base hook | `frontend/src/hooks/useWebSocket.ts` (S2502 §5 CODEOWNERS UNASSIGNED) | Factory function; consumers instantiate via named exports for typed subscription-sites: `useSystemEvents()`, `useAgentUpdates()`, `useLearningFeed()`, `useAgentConversations()`, `useHeartUpdates()` + 2 generic dynamic hooks (`/ws/pa/conversations/{id}/`, `/ws/dashboard/`). |
| S2502 targeted enumeration | 8 subscription sites (5 typed hooks + 2 generic + 1 dashboard) | S2502 §6.4 hedge: "8 identified from targeted enumeration — NOT exhaustive." Full enumeration deferred to Cat D S2504 T7 joint. |
| Token attach for WS handshake | `useAuthStore.getState().token` → query param `?token=` per S2502 §5 | Same token as REST; single-token dual-transport at HEAD (RE-VERIFIED via §3.3 middleware read). |

### §3.5 Client-side REST interceptor entry points

| Entry point | File:line | Purpose |
|---|---|---|
| `axios` client instance | `frontend/src/lib/api.ts:20-27` | Base URL + credentials + Authorization header interceptor. |
| `request` interceptor | `frontend/src/lib/api.ts:20-24` | Reads `useAuthStore.getState().token`; attaches as `Authorization: Bearer <token>` header on every REST request. |
| `response` interceptor (SHAPE-BLIND) | `frontend/src/lib/api.ts:43-62` | RE-VERIFIED IDENTICAL to S2503 F5 (5-session zero-delta since S2404): reads only `error.response?.status === 401` (not body); branches solely on `url.includes('/auth/') \|\| url.includes('/login')`; all 4 401 shape families flow through the SAME non-auth reject-and-console.warn branch. **SHAPE-BLIND state preserved at HEAD; CONDITIONAL CRITICAL two-part trigger per S2503 §14.3 Rigby Q5 STRENGTHEN fold.** |

---

## §4 Major Models

### §4.1 DRF Permission model taxonomy

DRF's `BasePermission` abstract at `rest_framework/permissions.py` is the parent class; concrete at u-d-b:

| Type | Example classes | File:line | Runtime role |
|---|---|---|---|
| DRF built-ins | `AllowAny`, `IsAuthenticated`, `IsAdminUser`, `IsAuthenticatedOrReadOnly` | (external) | Used pervasively in `@permission_classes([...])` decorations |
| Custom (fleet auth) | `FleetSignatureRequired`, `FleetCapabilityRequired` | `core/services/fleet_auth_drf.py:176, 215` | Fleet identity + capability check via `FleetServiceIdentity` model |
| Custom (public intel) | `PublicIntelTokenAuth` | `core/views_public_intelligence.py:37` | Third-party bearer-token validation |

**Cat D observation:** total custom Permission class count at HEAD = **3**; **no capability-composition combinators** (AND / OR / NOT) beyond DRF's built-in `&` `|` operators; **no policy-composition SDK**; **no capability registry model** (FleetCapabilityRequired.for_capability accepts hardcoded string paths per-view; no admin UI or DB-backed capability registry exists at HEAD).

### §4.2 Token models

| Model | Class | File:line | Expiry policy |
|---|---|---|---|
| DRF `Token` (built-in) | `rest_framework.authtoken.models.Token` | (external; imported at `core/auth_middleware.py:13`) | **NO `expires_at` field** (F-TOKEN-1 preserved from Cat A); `Token.objects.get(key=token_key)` returns user indefinitely until row deleted |
| `MobilePushToken` | (project model) | `core/models_mobile.py:9` | `revoked_at` soft-delete marker; NO auto-expiry |
| `VIPInvite.token` | `VIPInvite` | `core/models_vip_invite.py:33` | `token_expires_at` default now + 72h (via `_default_token_expires`); `account_expires_at` default now + 14d (via `_default_account_expires`) — **DECLARED but NOT ENFORCED at HEAD** (F-C-VIP-1 preserved from S2403 → S2503; risk-gate for expiry-signal-bearing UX) |
| `FleetServiceKey` | `FleetServiceKey` | `core/models/fleet.py:131` | `not_before`, `not_after` explicit validity window; status: active/draining/disabled |

### §4.3 Per-endpoint permission registry candidate models

**Result: ZERO registry models exist at HEAD.**

Parent-Claude ripgrep for `APIEndpoint`, `RouteFloor`, `EndpointPermission`, `RoutePerm`, `EndpointAuth`, `PermissionRegistry` in `core/models*.py` + all app-level `models.py` returned no matches. Agent 1 confirmed.

**Cat B (c) LONG-TERM GOVERNANCE per-endpoint registry per S2499 CF-B1 = GREENFIELD at HEAD.** No prototype code, no migration, no admin UI, no `/api/v1/admin/permission-registry/` route.

### §4.4 WORKSPACE_AWARE_AGENTS implicit-gate model

| Constant | File:line | Cat D observation |
|---|---|---|
| `WORKSPACE_AWARE_AGENTS` | `core/epa_handlers_tools.py` (~line 191-217; 20 agent handles) | Handler-layer permission-floor constant — agents in this list dispatch via `agent.execute_with_workspace()` requiring `workspace_id` in payload. **F-B-HIGH-3 lineage: workspace-membership enforcement happens INSIDE `execute_with_workspace()` (not audited by Cat B); at HTTP + DRF permission-class layer, no permission-class check enforces workspace-membership.** Cross-arc CF-B2 handoff to Group 2600 PA per S2402 §19.3. |

---

## §5 Major Services

### §5.1 DRF permission dispatcher

DRF's `APIView.dispatch` → `check_permissions()` (external code at `rest_framework/views.py`) is the runtime dispatcher. Flow:

1. Django resolves URL to view class + action; instantiates view.
2. DRF `initialize_request()` attaches DRF `Request` wrapper.
3. `perform_authentication()` runs each class in `authentication_classes` (or DEFAULT); first successful attaches user.
4. `check_permissions()` runs each class in `permission_classes` (or DEFAULT `[IsAuthenticated]`); ANY `has_permission()` returning `False` → `PermissionDenied` OR `NotAuthenticated` raised.
5. DRF exception handler formats response: **default handler emits `{"detail": "..."}` (Family A per S2501 F6 canonical / S2503 F1)** unless `EXCEPTION_HANDLER` overridden. Cat D RE-VERIFIED at HEAD: NO EXCEPTION_HANDLER override in `core/settings.py` (Agent 2 confirmed).

### §5.2 Middleware permission-floor dispatcher

`core/auth_middleware.py:UnifiedTokenAuthenticationMiddleware.process_request()` (S2402 §14.5 anchor):

1. Line 566: Non-API filter → return None (skip auth for non-`/api/` paths).
2. Line 570: PUBLIC_PATHS prefix check → return None (bypass auth entirely).
3. Line 574: PUBLIC_PATHS_EXACT check → return None.
4. Line 579: OPTIONAL_AUTH_PATHS → return None (anon allowed; scope['user'] = AnonymousUser).
5. Line 599: DRF `force_authenticate()` support → return None.
6. Line 605-618: Session auth + STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS checks → 403 or None.
7. Line 628: Token extraction from `Authorization` header.
8. Line 633: No token → `api_unauthorized("Authentication required")` = Family B (APIResponseEnvelope typed).
9. Line 644-658: Token validation → 401 Family B or 503 (auth_backend_unavailable).
10. Line 661: STAFF check on token user → `api_forbidden("Staff access required")` = Family B.
11. Line 667: REVIEWER_BLOCKED check on token user → `api_forbidden("Read-only reviewer access...")` = Family B.
12. Line 676: Attach user → return None (dispatch continues to DRF).

**Cat D observation:** middleware dispatcher emits Family B (APIResponseEnvelope) for ALL enforcement paths; DRF dispatcher emits Family A for permission-class violations. **This split IS the source of the 4-shape 401 heterogeneity finding (F1 preserved from S2501 F6 / S2503 F1) — no upstream normalization exists between middleware Family B and DRF Family A.** Family C bare `{"message"}` at `auth_views_enhanced.py:554` and Family D `{"success":false,"error":str}` at 5 `views_*.py` files are ad-hoc emissions in view code, not from either dispatcher.

### §5.3 WS consumer auth dispatcher

`core/ws_auth_middleware.py:TokenAuthMiddleware.__call__()` flow:

1. Line 35-37: `parse_qs(scope['query_string'])` → extract `token=<key>` from query string.
2. Line 40-41: `scope['user'] = await get_user_from_token(token)` → ORM lookup.
3. Line 15-21: `Token.objects.get(key=token_key)` → user attach; on `DoesNotExist` → `AnonymousUser()`.
4. Line 42+: pass to inner `AuthMiddlewareStack` + URLRouter.
5. Consumer `async connect()` reads `scope['user']`; consumer-level authorization is per-consumer discretion (no uniform pattern at HEAD).

**Cat D observation:** WS auth is **silent-degrade by default at middleware layer** — invalid token → AnonymousUser fallback, NO close-with-code 4001 at middleware level. Any consumer-level `if not scope['user'].is_authenticated: await self.close(code=4001)` pattern is per-consumer implementation. `REQUIRE_WEBSOCKET_AUTH` setting exists (`core/auth_middleware.py:762`) but is **DEAD at HEAD** — never referenced in the return path (S2402 §14.5 locus 20 DEAD-classification RE-VERIFIED IDENTICAL at HEAD).

### §5.4 Per-endpoint permission-floor registry candidate service

**Result: ZERO candidate service exists at HEAD.**

Parent-Claude ripgrep for `permission_floor_service`, `endpoint_registry_service`, `PermissionRegistry`, `EndpointRegistry` in `core/services/*.py` returned no matches. Agent 1 + Agent 2 confirmed.

**Cat B (c) design-prep target = GREENFIELD service layer.** Cat D S2504 does NOT propose service architecture (deferred to xx99 verdict + post-arc dedicated design PR); Cat D delivers boundary evidence.

### §5.5 FleetCapabilityRequired as Cat B (c) exemplar

`core/services/fleet_auth_drf.py:215-263` — `FleetCapabilityRequired` class demonstrates that a per-endpoint capability-declaration pattern is architecturally viable AT DRF permission-class layer:

```python
class FleetCapabilityRequired(permissions.BasePermission):
    ...
    @classmethod
    def for_capability(cls, *path: str):
        class _Bound(cls):
            capability_path = path
        return _Bound
```

Usage pattern per `core/views_fleet_artifacts.py:294`:

```python
@permission_classes([
    FleetSignatureRequired,
    FleetCapabilityRequired.for_capability("artifacts", "can_push"),
])
def push_artifact_view(request):
    ...
```

**Cat D observation (per Rigby SIGN cycle 1 Q5 STRENGTHEN fold — softened to mechanism-vs-governance-system distinction):** this is **a concrete production exemplar of the DRF-layer capability gating MECHANISM** (declarable intent + model-backed check) that could serve as a building block for Cat B (c) per-endpoint registry pattern from S2499 CF-B1 — the factory method `.for_capability(*path)` demonstrates that per-endpoint permission declarations (capability strings, role strings, workspace-scoped strings) can attach at DRF layer + evaluate against a backing model (`FleetServiceIdentity` here; could be `EndpointPermissionRegistry` at (c) full implementation). **However, this is exemplar of MECHANISM, not GOVERNANCE SYSTEM** — no centralized registry/catalog, admin UI, CI/lint enforcement, or governance workflow ships at HEAD; the (c) LONG-TERM GOVERNANCE surface layer would need those additive components. Cat B's option (c) proposal is not architecturally theoretical (DRF-layer viability demonstrated), but the full governance layer remains greenfield.

---

## §6 Major APIs and Interfaces

### §6.1 REST endpoint denominator + declaration coverage

**HEAD `87624a3d`:** 1,856 URL routes in `core/urls*.py` (4 files); 2,031 URL routes repo-wide (26 files); PLATFORM_INVENTORY autoblock 1,864 (drift -8 core-only, <1% non-load-bearing).

**Explicit declaration coverage (from Agent 3 25-endpoint stratified sample):**

| Category | Sample size | Explicit rate | Note |
|---|---|---|---|
| Money-path (`views_betting.py`, `views_stripe_billing.py`, `views_revenue.py`) | 5 | 100% (5/5) | High-integrity category; explicit declarations expected + observed |
| Governance (`views_workspace_api.py`, `views_workspace_templates.py`, `views_workspace_triggers.py`) | 5 | 40% (2/5) | ViewSet-based; class-attribute `permission_classes` INHERITED to actions but not decorator-visible at endpoint level |
| PA (`views_personal_assistant.py`, `views_employee_api.py`) | 5 | 100% (5/5) | PA endpoints declare IsAuthenticated or IsAdminUser explicitly |
| Sensitive-write (`views_deploy.py`, `views_agent_execution.py`, `views_stock_intelligence.py`) | 5 | 60% (3/5) | Mixed pattern; some endpoints use inline `request.user.is_authenticated` check instead of decorator |
| Read-only telemetry (`views_dashboard_stats.py`, `views_analytics_real.py`) | 5 | 100% (5/5) | Explicit `AllowAny` or `IsAuthenticated` declarations |

**Cat D observation:** Agent 3 stratified sample is 79.3% explicit-decoration (23/29), BUT this is a BIASED sample toward endpoints already flagged as sensitive/governance/money. **Extrapolating to 84.4% implicit-inheritance baseline (S2402 F-B-CRIT-1) requires exhaustive per-endpoint audit** — Cat D preserves S2402 baseline as authoritative for platform-wide rate; sample only informs stratified sub-rates. **Because strata intentionally overweight sensitive/flagged endpoints that are more likely to carry explicit declarations, 79.3% should be treated as an upper-bound indicator for high-risk surfaces, not a platform-wide explicitness estimate. This sample is risk-weighted, whereas S2402's baseline is population-weighted.** (Per Rigby SIGN cycle 1 Q6 STRENGTHEN fold — upper-bound / risk-weighted-vs-population-weighted disambiguation.)

### §6.2 @extend_schema × @permission_classes intersection

**S2501 Cat A baseline preserved:** 16 `@extend_schema` decorators across the repo, ALL confined to `sports/views.py`; ZERO in `core/*.py` or other apps. Co-declaration with `@permission_classes` at HEAD: NONE of the 16 `@extend_schema` endpoints declare `@permission_classes` explicitly (all inherit DEFAULT `[IsAuthenticated]`). **Adoption rate at HEAD: 0.86% (16/1,864).** Cat A F1 SoT-ABSENT preserved.

### §6.3 WS endpoint denominator + emit-site enumeration

**HEAD `87624a3d`:** 120 WS route entries across 5 routing.py files; 87 Consumer class definitions across 55 files (`^class \w+Consumer(...)?:` grep); ~40 unique consumer classes with active emit sites per S2202 baseline; targeted enumeration by Agent 3 sampled 47+ Consumer classes with `group_send/send_json`.

**WS auth uniformity: 100%** — all 120 route entries route through `TokenAuthMiddlewareStack` via `websocket_urlpatterns` composition per `core/asgi.py:28-32`. Agent 3 sampled 30+ consumer classes; found NO consumer that bypasses the middleware stack.

**8 identified WS subscription sites (S2502 §5 CONSUMER-side targeted enumeration preserved):**

| Client hook | Server endpoint | Consumer class (per Agent 3) | Notes |
|---|---|---|---|
| `useSystemEvents()` | `/ws/system-events/` | `SystemEventsConsumer` at `core/consumers/system_events_consumer.py` | Auth-gated via TokenAuthMiddlewareStack |
| `useAgentUpdates()` | `/ws/agent-updates/` | `AgentUpdatesConsumer` | Auth-gated |
| `useLearningFeed()` | `/ws/learning-feed/` | `LearningFeedConsumer` at `core/learning_feed_consumer.py` | Auth-gated |
| `useAgentConversations()` | `/ws/agent-conversations/` | Defined; unused at HEAD | Auth-gated |
| `useHeartUpdates()` | `/ws/heart/` | HeartWidget consumer | Auth-gated |
| Generic `useWebSocket()` | `/ws/pa/conversations/{id}/` | `PAConversationConsumer` at `core/consumers_pa_conversation.py` | HYBRID REST+WS; per-conversation token check |
| Generic `useWebSocket()` | `/ws/dashboard/` | `DashboardConsumer` (multiple candidates) | HYBRID |
| Generic `useWebSocket()` | `/ws/heart/` | HeartWidget dashboard | Auth-gated |

**Cat D observation:** S2502 hedge preserved — "8 identified from targeted enumeration; not exhaustive." Cat D S2504 RE-VERIFIES 120 route entries but does NOT perform exhaustive per-client-subscription enumeration (deferred to Cat D findings-appendix or post-arc T-slot execution scope).

### §6.4 PA tool surface authorization

`core/services/tool_dispatcher.py:Dispatcher.execute` (per Agent 3):

- **Per-user allowed-tools ACL:** `AssistantProfile.get_allowed_tools()` at `~L688-720` enforces per-user tool access; unauthorized tool call → `ToolResult.TOOL_PERMISSION_DENIED` at ~L702.
- **Audit trail:** `ToolCallRecord` telemetry at ~L1115 records ALL execution paths (success/deny/timeout).
- **Workspace-context authorization gap:** `WORKSPACE_AWARE_AGENTS` (20 agents at `core/epa_handlers_tools.py`) — dispatcher checks `if agent_name in WORKSPACE_AWARE_AGENTS and write_to_workspace:` → routes to `execute_with_workspace()`; the membership check itself is INSIDE that method (F-B-HIGH-3 CF-B2 → Group 2600 PA).

### §6.5 Celery task authorization

Per Agent 3 exhaustive review: **all Celery tasks correctly accept `user_id` as parameter (not `request.user`)**; ZERO `request.user` references in task definitions across `core/tasks*.py` + `ai_core/tasks.py`. Async authorization delegation is sound (S2402 §14.5 locus 21 EXPERIMENTAL preserved; no runtime enforcement beyond parameter-carrying).

### §6.6 Management command authorization

Per Agent 3: no `manage.py` command has a `permission_classes` equivalent; sensitive commands like `migrate_pa_identity`, `create_test_token`, `build_platform_inventory` operate on shell-access-only trust (S2402 §14.5 locus 22 WORKING preserved via shell-access as implicit gate).

---

## §7 Runtime Flows

### §7.1 REST authorized request flow (happy path)

1. Client `axios` request from `frontend/src/lib/api.ts:20-27` — request interceptor attaches `Authorization: Bearer <token>` from `useAuthStore.getState().token`.
2. Django URL dispatch → `UnifiedTokenAuthenticationMiddleware.process_request()` at `core/auth_middleware.py:85`.
3. Path-list gate evaluation (§5.2 steps 1-6) → not-PUBLIC + not-OPTIONAL + not-STAFF-blocked + not-REVIEWER-blocked.
4. Token extraction → `Token.objects.get(key=<token>)` → user attach → `request.user = user`.
5. View resolution + DRF `initialize_request` + `perform_authentication` (idempotent; middleware already attached).
6. `check_permissions` → all in `permission_classes` (or DEFAULT `[IsAuthenticated]`) return `True` → `has_permission()` OK.
7. View action executes; returns `Response(...)` or `APIResponseEnvelope.success(...)`.

### §7.2 REST 401 flow (unauthorized; 4 shape families)

**Family A (DRF default `{"detail":"..."}`):** IF endpoint uses inherited `[IsAuthenticated]` from DEFAULT and no valid token → DRF's `IsAuthenticated.has_permission()` returns `False` → `NotAuthenticated` raised → DRF exception handler formats `{"detail": "Authentication credentials were not provided."}`. Emitted at `core/auth_views.py:79-81, 91, 94, 123-126` (login-failure, logout success/exception, current_user unauth) and DRF's built-in handler.

**Family B (APIResponseEnvelope typed):** IF middleware auth check fails (no token, invalid token, STAFF/REVIEWER gate) → `api_unauthorized("Authentication required")` at `core/auth_middleware.py:79, 633, 658` → APIResponseEnvelope at `core/api_responses.py:143-149` emits `{"success":false,"error":{"code":"...","message":"..."}}`.

**Family C (bare `{"message":"..."}`):** IF endpoint code emits `Response({"message": "..."}, status=401)` inline — 1 known site at `core/auth_views_enhanced.py:554` (enhanced logout).

**Family D (`{"success":false,"error":str}`):** IF endpoint code emits `JsonResponse({"success":false,"error":"..."}, status=401)` inline — 6+ sites at `core/views_deploy.py:21, 79` + `core/views_agent_learning.py:2299, 2373` + `core/views_auto_fix.py:26` + `core/views_business_ideas.py:142-143`.

**Cat D observation:** the 4 shape families originate at 3 distinct emission tiers (middleware Family B, DRF Family A, view-code Families C+D) with NO upstream normalization. **F1 preserved from S2501 F6 → S2503 F1 → Cat D RE-VERIFIED IDENTICAL at HEAD (`87624a3d`) = 3-session zero-delta.** **Decision-space note (xx99 / Cat C territory):** whether to preserve multi-family 401 shapes with client-side discrimination, or define a single normalization SoT upstream, is deferred. **Cat D records the current absence of normalization at HEAD; does NOT prescribe normalization design.** (Per Rigby SIGN cycle 1 Q7 AGREE fold — decision-space pointer without prescription; envelope SoT selection is Cat C xx99 R2 verdict territory.)

### §7.3 WebSocket authorized connect flow

1. Client `useWebSocket` hook constructs URL: `ws://localhost:8000/ws/<path>/?token=<token>` (query-param token; `token` sourced from `useAuthStore.getState().token`).
2. Django Channels ASGI accepts WS handshake → `application` at `core/asgi.py:14-33` → `TokenAuthMiddlewareStack` wraps URLRouter.
3. `TokenAuthMiddleware.__call__` at `core/ws_auth_middleware.py:24` extracts `token` from `parse_qs(scope['query_string'])`.
4. `get_user_from_token(token)` at line 15-21 → `Token.objects.get(key=token)` → user attach OR AnonymousUser fallback.
5. Inner `AuthMiddlewareStack` → URLRouter → Consumer class instantiation.
6. `Consumer.async connect()` reads `scope['user']`; per-consumer authorization pattern (accept + attach OR close-with-code).

### §7.4 WebSocket unauthorized connect flow

If token invalid or missing: `get_user_from_token` returns `AnonymousUser()` (line 15-21 `except Token.DoesNotExist: return AnonymousUser()`). **NO close-with-code at middleware level.**

- Consumer's `async connect()` decides: some consumers accept anonymous, some reject via `await self.close(code=4001)`.
- No uniform pattern at HEAD; per-consumer discretion.
- `REQUIRE_WEBSOCKET_AUTH` setting is DEAD (S2402 §14.5 locus 20 preserved) — no code path references it.

**Cat D observation:** WS auth is **silent-degrade at middleware layer** (anonymous fallback rather than close-with-code); enforcement varies per consumer. This is the WS parallel to F-B-CRIT-2 silent-401 at REST layer. **Not directly comparable: REST silent-401 is per-request; WS silent-degrade is per-connection/handshake and may manifest as downstream per-message failures depending on consumer behavior.** No equivalent 803-scale-consumer-call-site telemetry exists for WS at HEAD (denominator + scale not measured). **Measurement candidate (Group 1700 Observability handoff — extends CF-D3):** define a WS unauthorized-connect metric (attempts/week, anonymous fallbacks/week, per-consumer reject codes) to bound prevalence. Cat D does NOT propose enforcement change; enumerates state; does NOT commit to WS silent-degrade denominator measurement at this scope (handoff to Group 1700 Observability). (Per Rigby SIGN cycle 1 Q8 STRENGTHEN fold — REST-vs-WS unit-mismatch clarification + Group 1700 measurement handoff without Cat D obligation.)

---

## §8 Data Ownership and Lifecycle

### §8.1 Permission-floor declaration lifecycle

**Declaration:** happens at code-write time via `@permission_classes` decorator, class attribute, custom Permission subclass, or path-list constant addition. **No code-review checklist, CI lint rule, or other governance gate was observed at HEAD that enforces explicit permission-floor declaration for new REST endpoints.** No mechanism was found at HEAD that systematically verifies (during review or CI) that newly added endpoints have an explicit permission-floor declaration. **Whether explicit per-endpoint declaration is required (vs relying on defaults/inheritance) is a xx99 governance decision; Cat D records the current absence of an enforcement mechanism and does not prescribe a policy.** (Per Rigby SIGN cycle 1 Q10 STRENGTHEN fold — boundary-safe rewrite; removed "MUST" prescriptive language + added xx99 deferral.)

**Runtime enforcement:** happens at every request via middleware → DRF dispatcher. Cache: DRF built-ins are stateless; custom classes may hit DB (e.g., `FleetCapabilityRequired.has_permission()` queries `FleetServiceIdentity`).

**Observability:** ABSENT at HEAD. Zero admin UI showing "what permission_classes does endpoint X declare?" — reader must grep code. F-B-CRIT-1 observability gap preserved.

### §8.2 Token lifecycle

**Creation:** login flow at `core/auth_views.py:53` → `Token.objects.get_or_create(user=user)` — DRF built-in; one-token-per-user.

**Validation:** `Token.objects.get(key=<token>)` at middleware layer (REST + WS).

**Expiry:** DRF `Token` has NO `expires_at` field (F-TOKEN-1); permanent unless manually deleted or user account disabled.

**Revocation:** manual DB delete OR `auth_views.py:logout_view` at line 79-94 (`request.user.auth_token.delete()`).

**Cross-transport lifecycle risk:** WS handshakes accept token at connect-time; if token revoked mid-session, the WS session persists until client-side disconnect (no server-side kill mechanism at HEAD). F-D-SIDEBAR-1 preserved from S2404 → S2503 F8 (Sidebar user-menu logout does NOT call `authApi.logout()` → server-side Token row persists after Zustand logout).

### §8.3 Path-list gate lifecycle

**Editing:** hand-edit `core/auth_middleware.py:94-561` (285 total entries). Zero governance gate — no code-review checklist, no CI lint, no CODEOWNERS-scoped review requirement beyond the file-level `@clwest` assignment.

**Testing:** zero automated smoke-test coverage for path-list gate correctness at HEAD (S2402 §14.5 F-B-HIGH-1 phantom finding evidence: 2 of 3 STAFF_REQUIRED_PATHS entries reference routes that DO NOT exist at HEAD).

**Cat D observation:** PATH-LIST GATE REGISTRY at `auth_middleware.py` operates as a **shadow per-endpoint registry** at STRING-MATCHING granularity — the closest thing to a Cat B (c) per-endpoint registry that exists at HEAD, but it's implemented as hardcoded Python lists with prefix-matching (PUBLIC_PATHS + STAFF_REQUIRED + REVIEWER_BLOCKED) or exact-matching (PUBLIC_PATHS_EXACT + REVIEWER_ALLOWED) rather than a database-backed declarative registry with admin UI + governance workflow.

---

## §9 Integrations With Other Domains

### §9.1 Cat D α/β/γ intersection model (Cat C S2503 §9.1 preserved + extended)

**Four independent decision-spaces Cat D touches:**

1. **Typed-error-envelope Cat D α/β/γ (S2404 §19.1 → S2503 §9.1 preserved):**
   - α: React Query global onError + interceptor override per module
   - β: Interceptor-only + typed AxiosError catches inline at every consumer
   - γ (PROPOSED PRIMARY per Cat C Rigby Q6 fold): RQ error callback + top-level ErrorBoundary; **γ = mechanism; Cat C β "explicit re-login" = message/UX policy nested inside γ** (ONE established nesting from Cat C S2503 Q12)

2. **Whitelist-replacement Cat D α/β/γ (S2404 §19.1 → S2503 §9.1 preserved):**
   - α: `AUTH_REDIRECT_ENDPOINTS.has(url)` explicit endpoint list
   - β: `X-Suppress-Auth-Redirect` backend response header
   - γ (PROPOSED PRIMARY per Cat C Rigby Q7 fold): Per-api-module `authHandling: 'default' | 'suppress_redirect'` string enum + telemetry on every `suppress_redirect` use

3. **Permission-floor Cat B (a)/(b)/(c) (S2402 §19.1 preserved):**
   - (a) Uniform `IsAuthenticated` across all `/v1/**` + client-side auth-gate + observable-error surfacing (NOT recommended per Cat B — LARGE blast radius; 6-8 weeks; DIFFICULT reversibility)
   - (b) Uniform `AllowAny` for read paths + `IsAuthenticated` for writes + client-side auth-check-on-write (Cat B PRIMARY for REMEDIATION WINDOW)
   - (c) Per-endpoint permission registry (Cat B PRIMARY for LONG-TERM GOVERNANCE per S2499 CF-B1)

4. **REST↔WS T7 Path A/B/C strictness (S2203 §20.6 preserved):**
   - Path A: Full-spectrum strict contract rollout (drf-spectacular platform-wide + orval codegen + zod runtime validation + standardized error envelopes for all 93 modules; LARGE blast radius)
   - Path B: Money-path/integrity-critical only (~10-15 modules; BOUNDED)
   - Path C: Strict for integrity/governance/money/state-changing REST endpoints; lighter for read-only/telemetry (MIDDLE ground)

**Cat D observation:** the ONE established nesting (Cat D γ = mechanism; Cat C β = UX policy nested inside γ default handler) from Cat C S2503 §9.1 IS THE ONLY CROSS-DECISION-SPACE COUPLING. All other pairings are INDEPENDENT unless explicitly coupled by xx99 verdict. Per §1.2 note 1: (a)/(b)/(c) permission-floor decision is INDEPENDENT of Path A/B/C strictness selection is INDEPENDENT of α/β/γ typed-error-envelope selection is INDEPENDENT of α/β/γ whitelist-replacement selection is INDEPENDENT of α/β/γ session-lifecycle selection.

### §9.2 Cross-arc coordination flags (preserved + extended)

| Flag | Owner | Cat D contribution |
|---|---|---|
| CF-B1 (Group 2500 API) | Group 2500 API (this arc) | Cat D S2504 matures Cat B (c) per-endpoint registry into design-prep spec + provides FleetCapabilityRequired.for_capability() as concrete production exemplar (§3.2, §5.5) |
| CF-B2 (Group 2600 PA) | Group 2600 PA | Cat D S2504 enumerates workspace-membership implicit-gate surface (`WORKSPACE_AWARE_AGENTS` 20 agents at `core/epa_handlers_tools.py`) but does NOT propose enforcement; handoff to Group 2600 PA per S2402 §19.3 preserved |
| CF-C1 (Group 2500 API) | Group 2500 API (this arc) | Cat C S2503 CLOSED as design-prep evidence-plane; Cat D S2504 does NOT re-audit refresh + logout + Clear-Site-Data |
| CF-C2 (Group 2600 PA) | Group 2600 PA | PA workspace-context lifecycle + session_tool.retire on user logout — Cat D references; does NOT re-scope |
| CF-C3 (Group 1700 Observability) | Group 1700 Observability | Auth event stream — Cat D notes zero structured event emission at HEAD; does NOT re-scope |
| CF-D1 (Group 2500 API) | Group 2500 API (this arc) | Typed-error-envelope α/β/γ inherited by Cat D via CONSUMER-side attach point at api.ts:43-62; Cat D does NOT re-decide envelope shape (Cat A domain) |
| CF-D5 (Group 2200 Frontend post-arc T-slot) | Group 2200 Frontend | R6 error-boundary framework = BLOCKING PREREQUISITE for γ typed-error-envelope; Cat D preserves prerequisite flag |
| CF-C8 (Group 1600 Content NEW per Cat C S2503 Rigby Q11) | Group 1600 Content | Envelope-shape variability leaks into editor/publisher UX; Cat D preserves flag |
| **CF-D6 NEW (this audit)** | Group 2500 API + Group 2600 PA (dual-owner) | **REST↔WS T7 joint contract SoT** — 120 WS route entries + 87 Consumer classes + 0% envelope conformance at HEAD; parallel to REST 803 call-sites + 4-shape 401 heterogeneity + 6.85% typed api.ts; **greenfield design-prep for Chris-D-verdict at xx99 on Path A/B/C strictness**. **Secondary stakeholders (non-owners):** Group 1700 Observability for emission/telemetry implications (envelope-shape telemetry + per-endpoint compliance metrics); Group 2300 Mobile for client interception/shape-discrimination implications (parallel silent-degrade at mobile client if Path B or C ratified). (Per Rigby SIGN cycle 1 Q9 AGREE fold — dual-owner sufficient + secondary stakeholders enumerated; no flag-explosion.) |

### §9.3 Fleet API adjacency

FleetCapabilityRequired at `core/services/fleet_auth_drf.py:215-263` is the concrete production exemplar for Cat B (c) per-endpoint pattern. Usage pattern (per `core/views_fleet_artifacts.py:294`):

```python
@permission_classes([
    FleetSignatureRequired,
    FleetCapabilityRequired.for_capability("artifacts", "can_push"),
])
def push_artifact_view(request):
    ...
```

**Cat D observation:** the `.for_capability(*path)` classmethod factory demonstrates the (c) design pattern IS viable at DRF layer — per-endpoint capability declaration + backing model check (`FleetServiceIdentity`). **Cat B (c) full implementation would parallel this pattern with `EndpointPermissionRegistry` model backing + admin UI + CI-lint gate.** Cat D S2504 cites as evidence exemplar; does NOT prescribe architecture.

---

## §10 Event Flows

### §10.1 REST 401 event flow (currently zero-emission)

At HEAD `87624a3d`, no structured event emission for auth-plane events (login/logout/401/expiry). CF-C3 → Group 1700 Observability preserved from S2499 §9. Cat D observation: silent-401 SYSTEMIC at 803-scale (F-B-CRIT-2 preserved from S2402 → S2404) is symptom of both (a) shape-blind interceptor at api.ts:43-62 and (b) zero telemetry emission for authorization events. **CF-D3 preserved — telemetry design deferred to Group 1700.**

### §10.2 WS disconnect event flow (currently zero-emission)

At HEAD, WS disconnect events (token revoked mid-session, client explicit disconnect, network drop) emit NO structured telemetry. Consumer-level `async disconnect(close_code)` implementations vary; no uniform observability pattern. Cat D observation: parallel to §10.1; deferred to Group 1700 Observability.

### §10.3 Permission denial event flow (currently minimal)

Middleware emits log lines via `logger.warning("Authentication required")` at `core/auth_middleware.py:633`; DRF-emitted `PermissionDenied` bubbles through DRF's `exception_handler` (default emits `{"detail": "..."}` to client, no structured event). Zero permission-denial event emission to observability plane.

---

## §11 Existing Documentation

### §11.1 Current documentation touching Cat D scope

| Doc | Status | Cat D relevance |
|---|---|---|
| `docs/topics/auth.md` | EXISTS (created S2499 close per AU-D2) | Group 2400 Auth close deliverable; documents auth-domain surface + permission-floor + session-lifecycle; Cat D reads but does NOT modify |
| `docs/topics/api.md` | MISSING (S2500 §6 P-1 parked; deferred to S2599 xx99 close post-arc cascade PR) | Analog to `auth.md`; Cat D S2504 does NOT create; xx99 canonical summary handoff artifact |
| `docs/topics/frontend.md` | EXISTS (S2499 AU-D1 refresh candidate) | General frontend topic; silent-401 pattern + typed-error-envelope + error-boundary framework subsection deferred to AU-D1 |
| `docs/PLATFORM_INVENTORY.md` | EXISTS (§API autoblock CREATE deferred per S2500 §6 P-1) | Runtime inventory anchor; Cat D §API autoblock addition deferred to post-arc cascade PR |
| `docs/PLATFORM_WHAT_IT_IS.md` | EXISTS (§API narrative subsection CREATE deferred per S2500 §6 P-2 candidate) | Narrative anchor; Cat D §API subsection addition deferred to post-arc cascade PR |
| `docs/ARCHITECTURE.md` / `docs/research/ARCHITECTURE_INDEX.md` | EXISTS (Path A/B/C decision matrix pointer + CONSUMER-side Path A/B/C independence note + Cat C α/β/γ intersection model pointer + §16 Level 0 explicit-contract-missing anchor pointer all deferred to xx99 post-arc cascade PR) | Cat D preserves anchor-update batch for xx99 |
| `docs/research/domains/api/*` | 4 files exist (S2500 parent + S2501 Cat A + S2502 Cat B + S2503 Cat C) | Cat D S2504 is 5th; S2599 xx99 is 6th |

### §11.2 Cat D anchor-update batch (deferred to S2599 xx99 close)

Extends Cat A + Cat B + Cat C deferred batch. **Deferring these doc edits preserves arc consistency: child audits enumerate evidence; xx99 performs canonical doc reconciliation.** (Per Rigby SIGN cycle 1 Q11 AGREE fold — anti-fatigue guard justification.)

- `docs/topics/api.md` CREATE — recast Cat D contribution: permission-floor 4-layer split + FleetCapabilityRequired exemplar + REST↔WS T7 joint architecture + 8-dimension maturity table (extends Cat C §13 with Cat D dimensions).
- PLATFORM_INVENTORY §API autoblock — add Cat D denominators: 285 path-list gate entries + 74 class-attribute declarations + 838 decorator sites + 3 custom Permission classes + 120 WS route entries + 87 Consumer class definitions + 0% WS envelope conformance rate.
- PLATFORM_WHAT_IT_IS §API narrative subsection — describe 4-layer permission-floor split + REST↔WS architectural disjointness + Cat D α/β/γ + Cat B (a)/(b)/(c) + Path A/B/C decision-space intersection.
- `platform_architecture_inventory.md` §3.22 API Layer REVISE with Cat A + Cat B + Cat C + Cat D combined DECLARATION + CONSUMER + CONTRACT + REGISTRY sub-layer evidence.
- ARCHITECTURE_INDEX Cat D α/β/γ intersection pointer + REST↔WS T7 joint pointer + §16 Level 0 extended-anchor pointer + FleetCapabilityRequired exemplar reference.

---

## §12 Research Coverage

### §12.1 Prior research lineage

**Direct predecessors (BINDING inheritance):**

| Doc | Class | Contribution to Cat D |
|---|---|---|
| S2402 `2402_authorization_permission_floor_uniformity_audit.md` | Cat B (Group 2400 Auth) | F-B-CRIT-1 implicit-inheritance ~84.4% + Cat B (a)/(b)/(c) decision-space + §14.5 21-loci enforcement table + F-B-HIGH-1/2/3/4 + PUBLIC_PATHS 265 baseline (RE-VERIFIED IDENTICAL) + REVIEWER_BLOCKED_PATHS drift observation (S2402 baseline 12 → HEAD 7; -5 REDUCTION drift NEW to Cat D) |
| S2499 `2499_auth_canonical_summary.md` | xx99 (Group 2400 Auth) | CF-B1 per-endpoint registry Cat B (c) LONG-TERM GOVERNANCE + §8.1 rank-1 P0 batch (14 co-equal items) + CF-D1 typed-error-envelope + CF-D3 silent-401 rate telemetry (Group 1700 handoff) + CF-D5 error-boundary framework prereq (Group 2200 handoff) |
| S2500 `2500_api_domain_scoping.md` | Parent scoping (this arc) | Cat D §3.D mission verbatim (Permission-Floor Registry + REST↔WS T7 Joint Design-Prep) + §5 child sequence position + §6 P-1 through P-11 parked items (especially P-10 rate-limiting Cat D scope + P-11 pagination Cat A scope) |
| S2501 `2501_api_backend_contract_sot_design_prep_audit.md` | Cat A (this arc) | DECLARATION-side @extend_schema × @permission_classes intersection (16-of-1,873 = 0.86% adoption) + Path A/B/C decision matrix evidence + F1 SoT-ABSENT + F5 drf-spectacular partial-wiring + F6 4-shape 401 anchor |
| S2502 `2502_api_frontend_client_architecture_design_prep_audit.md` | Cat B (this arc) | CONSUMER-side 803 call-sites (57 direct + 667 hook + 79 raw fetch) + 8 WS subscription sites + 93 apiModules + 18 DEAD-CANDIDATE + F3 SHAPE-BLIND interceptor characterization + F-D-CALL-1/F-D-BYPASS-1 CONSUMER-side manifestation |
| S2503 `2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md` | Cat C (this arc) | CONTRACT-INTERSECTION layer + F1 4-shape 401 RE-VERIFIED + F3 refresh absent + F4 CSD zero + F5 SHAPE-BLIND RE-VERIFIED + F6 basic-vs-enhanced key drift + F7 F-C-VIP-1 4-option rubric + F8 F-D-SIDEBAR-1 Cat D owner + §9.1 α/β/γ intersection model with ONE established nesting + §16 Level 0 explicit-contract-missing anchor |

**Adjacent references (evidence-consuming, not BINDING inheritance):**

| Doc | Class | Cat D use |
|---|---|---|
| S2202 `2202_frontend_websocket_consumer_ui_render_hint_envelope_audit.md` | Group 2200 Frontend Cat B | §17 T6 message routing + 120 WS route baseline (RE-VERIFIED 125 → 120 = -5 drift) + 0/40 envelope conformance + WS consumer auth uniformity 100% via TokenAuthMiddlewareStack |
| S2203 `2203_frontend_api_contract_boundary_discipline_audit.md` | Group 2200 Frontend Cat C | §17.3 T7 REST↔WS parallel verbatim declaration + §14 F1 SoT-ABSENT anchor + §14 F4/F5 CONSUMER-side + §20.6 Path A/B/C decision-space |
| S2404 `2404_frontend_integration_silent_401_systemic_resolution_audit.md` | Group 2400 Auth Cat D | Origin of F-D-CALL-1 803-scale + F-D-BYPASS-1 79-raw-fetch + F-D-WHITELIST-1 shape-blind + F-D-SIDEBAR-1 + F-D-ENVELOPE-1 α/β/γ + F-D-BOUNDARY-1 R6 prerequisite |

### §12.2 Research coverage classification (per playbook §12 vocabulary)

**Coverage labels reflect HEAD implementation evidence depth, not conceptual-spec depth** (per Rigby SIGN cycle 1 Q12 STRENGTHEN fold — spec-vs-evidence classification clarification).

- **Permission-floor DECLARATION-side (REST):** MODERATE (Cat A S2501 covered baseline + intersection; Cat D S2504 extends with 74 class-attr + 838 decorator denominators)
- **Permission-floor CONSUMER-side (frontend caller):** MODERATE (Cat B S2502 covered 803 call-sites + interceptor)
- **Permission-floor CUSTOM-CLASS layer:** LIGHT (Cat D S2504 first enumeration: 3 custom Permission classes + FleetCapabilityRequired exemplar)
- **Permission-floor PATH-LIST-GATE layer:** DEEP (S2402 Cat B baseline + Cat D S2504 RE-VERIFY at HEAD with drift observation)
- **Permission-floor REGISTRY layer (Cat B (c)):** LIGHT (Cat D S2504 first design-prep declaration; greenfield inventory; no full governance system evidence at HEAD)
- **WS auth uniformity:** DEEP (S2202 Cat B baseline + S2402 §14.5 locus 18-20 + Cat D RE-VERIFY at HEAD with -5 route drift)
- **REST↔WS T7 message-contract parallel:**
  - **T7 conceptual contract (S2202/S2203):** MODERATE (spec depth — T6/T7 declared with parallel structure per S2202 §17 + S2203 §17.3)
  - **T7 HEAD implementation evidence + SoT:** LIGHT (evidence depth — Cat D S2504 first design-prep enumeration; greenfield SoT at HEAD)
- **Session-lifecycle interaction (refresh, logout, expiry):** DEEP (Cat C S2503 CLOSED as design-prep evidence-plane)
- **Envelope-shape SoT:** MODERATE (Cat A + Cat C converge; Cat D preserves)

---

## §13 Architecture Maturity — Cat D 8-Dimension Table

Cat D extends Cat C S2503 §13 8-dimension table (which introduced "Contract SoT / ownership maturity" NEW dimension per Rigby Q17 fold) with Cat D-specific dimensions:

| # | Dimension | Classification | Evidence |
|---|---|---|---|
| 1 | Per-endpoint `permission_classes` declaration coverage | **PARTIAL** | ~84.4% implicit-inheritance rate (S2402 baseline preserved); 838 explicit decorator sites + 74 class-attr sites at HEAD; zero platform-wide observability |
| 2 | Custom Permission class ecosystem maturity | **EXPERIMENTAL** | 3 production classes (FleetSignatureRequired, FleetCapabilityRequired, PublicIntelTokenAuth); zero policy-composition SDK; zero capability registry model backing |
| 3 | Path-list gate registry maturity (auth_middleware.py) | **WORKING** | 285 total entries across 6 constants; centralized string-matching; zero governance gatekeeper; accretion drift + duplicate entries per S2402 §11 evidence |
| 4 | WS consumer auth uniformity | **WORKING** | 100% route through TokenAuthMiddlewareStack at HEAD (120/120); consumer-level rejection variance (per-consumer discretion); silent-degrade at middleware layer |
| 5 | REST↔WS message-contract parallel maturity (T7 joint) | **EXPERIMENTAL** | REST APIResponseEnvelope typed at Family B (9 hand-invoked sites) + 4-shape heterogeneity elsewhere; WS raw `json.dumps` dicts (0/40 envelope conformance per S2202 F3); ZERO cross-transport contract SoT |
| 6 | Per-endpoint permission REGISTRY (Cat B (c)) maturity | **GREENFIELD** | Zero registry infrastructure at HEAD (Cat B (c) LONG-TERM GOVERNANCE per S2499 CF-B1); FleetCapabilityRequired.for_capability() exemplar demonstrates pattern viability |
| 7 | Silent-401 UX contract (from F-B-CRIT-2 + F-D-CALL-1) | **HIGH baseline + CONDITIONAL CRITICAL** | SHAPE-BLIND interceptor at api.ts:43-62 (RE-VERIFIED IDENTICAL at HEAD across 5 sessions since S2404); ~803 consumer call-sites (S2502 preserved); F5 CONDITIONAL CRITICAL two-part trigger per S2503 Q5 preserved |
| 8 | Whitelist-replacement α/β/γ mechanism | **GREENFIELD** | Zero implementation at HEAD; Cat C Q7 fold `authHandling: 'default' \| 'suppress_redirect'` string enum + telemetry proposal PROPOSED PRIMARY γ; awaits xx99 verdict |

**Overall verdict:** Cat D confirms the same EXPERIMENTAL-to-PARTIAL depending-on-dimension pattern from Cat C S2503, **extended with 2 GREENFIELD dimensions (permission-floor registry + whitelist-replacement mechanism) and 1 WORKING dimension (path-list gate registry) and 1 EXPERIMENTAL dimension (REST↔WS T7 parallel)**. The MATURITY GAP is not implementation-completeness (mechanisms work at HEAD) but **CONTRACT-CLARITY + OBSERVABILITY** — what SHOULD the per-endpoint permission-floor SoT be? What SHOULD the REST↔WS message-contract SoT be? Both remain xx99 verdict-requests.

**Anti-dilution note (per Rigby SIGN cycle 1 Q13 AGREE fold):** dimensions are kept constant across arc children for comparability; overlap is tolerated when dimensions map to distinct decision-spaces. Each row above has an implicit owner/decision pointer (e.g., dimension 6 → CF-B1 → xx99 R1; dimension 5 → CF-D6 → xx99 R2; dimension 7 → Cat C S2503 F5 → xx99 R2 territory; dimension 8 → Cat C S2503 §9.1 whitelist α/β/γ → xx99 R1) so the table does not read as a grab bag.

---

## §14 Known Drift

### §14.1 F-D-REGISTRY-1 — Per-endpoint permission-floor registry ABSENT at HEAD [NEW]

**Class:** `missing_connection` + `technical_debt` (governance). **Severity:** HIGH baseline (LONG-TERM GOVERNANCE gap per S2499 CF-B1).

**Evidence:** Parent-Claude ripgrep for `APIEndpoint`, `RouteFloor`, `EndpointPermission`, `PermissionRegistry` in `core/models*.py` + all app-level `models.py` = **zero matches**. `core/services/permission_floor_service.py` = does not exist. `core/services/endpoint_registry_service.py` = does not exist. Admin UI + `/api/v1/admin/permission-registry/` route = do not exist.

**Cat B (c) LONG-TERM GOVERNANCE per S2499 CF-B1 = GREENFIELD at HEAD.** No prototype code, no migration file, no schema.

**Boundary preservation:** F-D-REGISTRY-1 statement is "no per-endpoint permission-floor registry infrastructure exists at HEAD." Cat D does NOT prescribe (a) vs (b) vs (c) selection. Chris-D-verdict at xx99 owns Cat B (a)/(b)/(c) option ratification.

**Classification note (per Rigby SIGN cycle 1 Q14 AGREE fold):** F-D-REGISTRY-1 + F-D-WSENVELOPE-1 + F-D-4LAYERSPLIT-1 are **design-plane SoT gaps (`missing_connection`), not violations of an explicitly adopted standard.** "boundary_violation" classification is deliberately NOT applied to these findings because they represent contract-SoT absences at design-plane level rather than breach of an explicitly contracted standard. Severity remains HIGH (governance impact + client-observability ambiguity) but the ontology stays evidence-based.

### §14.2 F-D-WSENVELOPE-1 — WS message-contract SoT ABSENT at HEAD [NEW]

**Class:** `missing_connection` + `technical_debt`. **Severity:** HIGH baseline (T7 joint scope per S2203 §17.3 preserved).

**Evidence:** Parent-Claude ripgrep for `TypedDict`, `Protocol`, `BaseModel`, `dataclass` in `core/consumers*.py` + `**/consumers*.py` = zero matches for WS envelope shape. Zero `channels_graphql` in requirements. Zero `.schema.json` files for WS message types. WS emits raw `json.dumps` dicts with ad-hoc `{type, data, timestamp}` fields per consumer (`core/consumers_pa_conversation.py:10-23` event-type strings as COMMENTS, not enforced).

**S2202 §14 F3 preserved:** 0/40 unique consumer classes with `group_send` conform to `ui.render_hint` envelope schema; 5-session zero-delta.

**Boundary preservation:** F-D-WSENVELOPE-1 statement is "no WS message-contract SoT infrastructure exists at HEAD." Cat D does NOT prescribe REST-shape convergence (out-of-scope per S2500 §6 P-6); does NOT propose Path A/B/C strictness selection.

### §14.3 F-D-4LAYERSPLIT-1 — Permission-floor stack fragmented across 4 architecturally independent layers [NEW SYNTHESIS]

**Class:** `technical_debt` + `unclear_owner`. **Severity:** MEDIUM (governance discipline gap).

**Evidence:** 4 layers operate at HEAD with no cross-layer SoT:

1. **DRF DEFAULT layer** — `DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]` at `core/settings.py:652-653`. Implicit-inheritance floor for all endpoints.
2. **Explicit decorator layer** — `@permission_classes([...])` at 838 sites across 106 files + `permission_classes = [...]` class attribute at 74 sites across 20 files.
3. **Path-list gate layer** — 6 constants in `core/auth_middleware.py`; 285 total entries; PREFIX-matching + EXACT-matching rules; enforced at middleware BEFORE DRF dispatch.
4. **Custom Permission class layer** — 3 classes (`FleetSignatureRequired`, `FleetCapabilityRequired`, `PublicIntelTokenAuth`); each defines its own model-backed check.

**Order of precedence:** middleware path-list (layer 3) evaluates FIRST; if match short-circuits with return None (PUBLIC) or 401/403 (STAFF/REVIEWER), DRF dispatch never runs. **This is the source of F-B-HIGH-2 dead-code inversion at `/api/v1/betting/place/` (PUBLIC_PATHS at line 198 + REVIEWER_BLOCKED_PATHS at line 550) — public bypass at layer 3 short-circuits before layer 2 evaluates.**

**Boundary preservation:** F-D-4LAYERSPLIT-1 statement is "no cross-layer permission-floor SoT exists at HEAD." Cat D does NOT prescribe consolidation to single layer; layers may all coexist under Cat B (c) design if xx99 selects registry pattern.

### §14.4 F-B-CRIT-1 permission-floor implicit-inheritance RE-VERIFIED [PRESERVED FROM S2402]

**Class:** `technical_debt`. **Severity:** CRITICAL for observability; LOW for correctness.

**Evidence at HEAD `87624a3d`:** S2402 baseline preserved: ~1,576 of ~1,866 endpoints (~84.4%) inherit `[IsAuthenticated]` from `DEFAULT_PERMISSION_CLASSES` (no explicit `@permission_classes` decorator).

Cat D contributes RE-VERIFY denominators at HEAD:
- Total core-only URL routes: 1,856 (S2402 said ~1,866; -10 drift, non-load-bearing).
- Explicit `@permission_classes` decorator sites: 838 across 106 files.
- Class-attribute `permission_classes = [...]` declarations: 74 sites across 20 files.
- Custom Permission class sites: ~5 (FleetSignatureRequired + FleetCapabilityRequired stacked at 3 view files + PublicIntelTokenAuth at 1 view file).

Cat D observation: 838 + 74 = **912 total explicit permission-declaration sites** across 106+20=126 files. If each site corresponds to a unique endpoint, explicit-declaration rate = 912/1,856 ≈ 49%. **But this contradicts S2402's 84.4% implicit-inheritance rate.** Discrepancy is because (a) 838 counts every decorator invocation including duplicates on same view (some views stack multiple decorators); (b) class-attr propagates to N ViewSet actions each; (c) S2402 measured "endpoint declaration coverage" via per-endpoint stratified sampling, not raw grep. **Cat D preserves S2402 baseline as authoritative** — exhaustive per-endpoint audit at HEAD deferred to post-arc T-slot; Cat D flags the discrepancy as an area for future denominator-alignment work.

### §14.5 F-B-CRIT-2 silent-401 SYSTEMIC RE-VERIFIED [PRESERVED FROM S2402 → S2404 → S2503]

**Class:** `technical_debt` + `drift`. **Severity:** HIGH baseline; CONDITIONAL CRITICAL per S2503 F5 two-part trigger preserved.

**Evidence at HEAD `87624a3d`:** api.ts:43-62 SHAPE-BLIND interceptor RE-VERIFIED IDENTICAL to S2503 F5 baseline (5-session zero-delta since S2404); reads only `error.response?.status === 401` (not body); branches solely on `url.includes('/auth/') \|\| url.includes('/login')`; all 4 401 shape families flow through the SAME non-auth reject-and-console.warn branch.

Consumer call-site denominator: 803 (57 direct + 667 useQuery/useMutation + 79 raw fetch per S2502 §20.4 preserved).

**Cat D observation:** Cat D S2504 does NOT re-audit 803-scale call-sites (Cat B S2502 owns denominator; Cat D preserves via reference). Cat D adds: **the same silent-degrade pattern extends to WS auth at consumer-connect level** — invalid token → AnonymousUser fallback → consumer-level rejection variance. WS silent-degrade parallel is not currently instrumented at HEAD (zero telemetry emission per §10.2); parallel scale is much smaller (per-connection rather than per-call) so not directly comparable to 803 baseline.

### §14.6 F-B-HIGH-2 /api/v1/betting/place/ PUBLIC + REVIEWER_BLOCKED inversion dead-code RE-VERIFIED [PRESERVED FROM S2402]

**Class:** `boundary_violation` + `dead_code`. **Severity:** MEDIUM (F-BND-4b at S2402); CRITICAL when combined with F-BND-4a unauthenticated write.

**Evidence at HEAD `87624a3d`:** `core/auth_middleware.py:198` PUBLIC_PATHS entry `'/api/v1/betting/place/'` PRESERVED; `core/auth_middleware.py:550` REVIEWER_BLOCKED_PATHS entry `'/api/v1/betting/place/'` PRESERVED. Middleware early-return at line 570 (PUBLIC match) short-circuits BEFORE line 668 (REVIEWER_BLOCKED check) — reviewer-block is dead code for this endpoint.

**Cat D observation:** F-B-HIGH-2 remains a Cat B (c) design-prep artifact — if registry-pattern (c) ratified at xx99, the registry declarative floor would surface the double-declaration + resolve ambiguously OR require explicit precedence rule at registry layer. Cat D preserves finding; execution deferred to post-arc T-slot (Cat B S2402 §19.2 rank-2).

### §14.7 F-B-HIGH-1 STAFF_REQUIRED_PATHS 2-of-3 PHANTOM RE-VERIFIED [PRESERVED FROM S2402; FINDINGS-APPENDIX per Rigby Q1]

**Class:** `dead_code` + `drift`. **Severity:** MEDIUM.

**Evidence at HEAD `87624a3d`:** `core/auth_middleware.py:541-545` STAFF_REQUIRED_PATHS 3 entries preserved: `/api/v1/admin/` + `/api/v1/system/` (or similar) + `/api/v1/metrics/admin/`. Parent-Claude URL grep: `path\(['\"]api/v1/admin/` = 0 matches; `path\(['\"]api/v1/metrics/admin/` = 0 matches. **2-of-3 phantom preserved** — only 1 STAFF_REQUIRED_PATHS entry has a corresponding registered route at HEAD.

**Findings-appendix classification per S2500 Rigby SIGN Q1 P4-retitle fold** (moved from framing to appendix to prevent P4 reading as "auth hardening PR"); execution locus = post-arc T-slot maintainer-decision batch.

### §14.8 F-B-HIGH-4 @authentication_classes([]) stacking REDUCTION DRIFT [PRESERVED FROM S2402; FINDINGS-APPENDIX per Rigby Q1]

**Class:** `technical_debt` + `configuration` (governance). **Severity:** HIGH overall; CRITICAL-per-site for `core/auth_views_enhanced.py:560` (contains login/token flow).

**Evidence at HEAD `87624a3d`:** parent-Claude ripgrep `@authentication_classes\(\[\]\)` returns **6 sites across 3 files** (S2402 baseline was 4 files):

- `ai_core/api/freelance_api.py:888, 931` (2 sites; anon-browse intentional)
- `core/views_preferences.py:793, 1242, 1296` (3 sites)
- `core/auth_views_enhanced.py:560` (1 site; CRITICAL-per-site — contains logout endpoint)

**Cat D drift observation NEW:** S2402 baseline listed `core/views_nervous.py` as 4th file; **at HEAD `87624a3d` `core/views_nervous.py` has ZERO `@authentication_classes([])` sites** — **1-file REDUCTION drift from S2402 baseline**. This is a CLOSED-finding drift observation (`views_nervous.py` remediation shipped between S2402 close and S2503 close; Cat D does NOT re-audit remediation history).

**Findings-appendix classification per S2500 Rigby SIGN Q1 P4-retitle fold.**

### §14.9 REVIEWER_BLOCKED_PATHS REDUCTION DRIFT [NEW OBSERVATION]

**Class:** `drift`. **Severity:** LOW (governance discipline).

**Evidence at HEAD `87624a3d`:** Parent-Claude Python-parser count of `core/auth_middleware.py:548-556` REVIEWER_BLOCKED_PATHS list returns **7 string entries** (S2402 §14.5 baseline said 12 entries → -5 REDUCTION drift). PUBLIC_PATHS remains 265 (identical). STAFF_REQUIRED_PATHS remains 3 (identical). Other lists identical to S2402 baseline.

**Cat D observation (per Rigby SIGN cycle 1 Q15 STRENGTHEN fold — intent-attribution softened to observed outcome):** **Observed reduction drift (12→7) suggests pruning; intent/lineage not established here.** Not a defect; Cat D flags as drift observation for anchor-update batch tracking. **Optional post-arc task (xx99 / T-slot):** git lineage trace in `core/auth_middleware.py` to identify the pruning commit + rationale.

### §14.10 WS route -5 drift [NEW OBSERVATION]

**Class:** `drift`. **Severity:** LOW (denominator alignment).

**Evidence at HEAD `87624a3d`:** Parent-Claude ripgrep `^\s*(?:re_)?path\(` in `**/routing.py` returns **120 total entries** (S2202 baseline 125 → -5 drift). Distribution: core/routing.py:107 + ai_core/intelligence/routing.py:5 + ai_core/routing.py:3 + sports/routing.py:3 + intelligence/routing.py:2 = 120.

**Cat D observation:** Small denominator drift; not a defect. Reflects natural route churn between S2202 close and S2504 open. Documented for xx99 anchor-update batch.

---

## §15 Known Technical Debt

Consolidated Cat D technical-debt matrix (extending S2503 §15 with Cat D-specific items):

| Item | Severity | Class | Cat D observation |
|---|---|---|---|
| Zero per-endpoint permission-floor registry (F-D-REGISTRY-1) | HIGH | governance-debt | Greenfield at HEAD; Cat B (c) LONG-TERM GOVERNANCE per S2499 CF-B1; xx99 verdict-request |
| Zero WS message-contract SoT (F-D-WSENVELOPE-1) | HIGH | contract-debt | Greenfield at HEAD; T7 joint per S2203; xx99 verdict-request |
| Permission-floor 4-layer split (F-D-4LAYERSPLIT-1) | MEDIUM | governance-debt | 4 architecturally independent layers; no cross-layer SoT; source of F-B-HIGH-2 inversion |
| DRF Token no `expires_at` (F-TOKEN-1 from Cat A preserved) | MEDIUM | data-contract debt | Coupled to R3 xx99 verdict on refresh-endpoint necessity |
| Path-list gate accretion drift + duplicates (S2402 evidence) | MEDIUM | registry-debt | 285 total entries at HEAD; PUBLIC_PATHS 265 has 8+ duplicates per S2402; zero governance gatekeeper |
| STAFF_REQUIRED_PATHS 2-of-3 phantom (F-B-HIGH-1) | MEDIUM | dead-code | RE-VERIFIED at HEAD; findings-appendix |
| `/api/v1/betting/place/` PUBLIC+REVIEWER_BLOCKED inversion (F-B-HIGH-2) | MEDIUM-CRITICAL | boundary_violation + dead-code | RE-VERIFIED at HEAD |
| `@authentication_classes([])` stacking (F-B-HIGH-4) | HIGH | permission-debt | RE-VERIFIED at HEAD; -1 file drift from S2402; CRITICAL-per-site for auth_views_enhanced.py:560 |
| WS silent-degrade at middleware layer (§7.4) | MEDIUM | UX-contract debt | Silent AnonymousUser fallback; per-consumer rejection variance; parallel to REST F-B-CRIT-2 |
| Zero authorization event emission (§10) | MEDIUM | observability-debt | CF-C3/CF-D3 → Group 1700 handoff preserved |
| SHAPE-BLIND interceptor (F5 preserved from S2404 → S2503) | HIGH baseline + CONDITIONAL CRITICAL | UX-contract | Cat D preserves via reference; 5-session zero-delta |
| 79-raw-fetch bypass (F-D-BYPASS-1 preserved) | MEDIUM | boundary_violation | Cat B S2502 CLOSED as design-prep; Cat D post-arc T-slot per-site classification |
| Custom Permission class ecosystem thin (§4.1) | LOW | ecosystem-debt | 3 classes; zero policy-composition SDK; not a blocker for (c) design but limits reuse |

---

## §16 Boundary Violations — Level 0 Anchor Extended

### §16.1 Level 0 explicit-contract-missing anchor (Cat C S2503 §16 preserved + extended)

**Cat C S2503 anchor (verbatim preserved):** "the platform currently lacks an explicit, centralized API contract for (error envelope + refresh + logout semantics). Cat C records evidence of an *implicit* contract (Level 2) and its violations; whether to formalize a first-class contract (and where it lives) is deferred to xx99."

**Cat D S2504 observes (per Rigby SIGN cycle 1 Q16 STRENGTHEN fold — Level 0 anchor de-inflation to preserve signaling value):** two additional contract-SoT absences adjacent to the Level 0 anchor: **per-endpoint permission-floor semantics + REST↔WS message-contract strictness semantics**. Cat D records evidence of implicit contracts at each layer (DRF DEFAULT + explicit decorator + path-list gate + custom class = 4 implicit layers; REST APIResponseEnvelope + WS raw `json.dumps` = 2 implicit transports) and their governance gaps (F-D-REGISTRY-1, F-D-WSENVELOPE-1, F-D-4LAYERSPLIT-1); whether to formalize first-class contracts (permission-floor registry via Cat B (c) OR message-contract SoT via T7 Path selection) is deferred to xx99.

**These are recorded as Level 0-adjacent candidates for xx99 consolidation, NOT a redefinition of the Level 0 anchor.** Cat C S2503 canonical Level 0 anchor scope (3 domains: error envelope + refresh + logout) is preserved. Cat D adds 2 adjacent candidates (permission-floor + REST↔WS strictness); xx99 canonical summary owns whether to consolidate into a single Level 0 anchor covering 5 domains, keep separate anchors, or restructure. **All axes remain Chris-D-verdict at xx99.** This adjacency framing prevents the reader from missing the primary "which contracts should exist as first-class SoT?" decision axis at xx99 close without inflating the Level 0 anchor prematurely.

### §16.2 Level 1 primary-posture boundary (preserved)

Formal CONTRACTS for permission-floor + REST↔WS message shapes not declared at HEAD — "boundary violation" frame under-applies at this level.

### §16.3 Level 2 implicit-contract violations (preserved + extended)

Cat D preserves Cat C S2503 §16 Level 2 violations (F-D-BYPASS-1, F-D-SIDEBAR-1, F-C-STORE-1) and adds:

- **F-B-HIGH-2** — `/api/v1/betting/place/` implicit-contract violation: same route declared as PUBLIC + REVIEWER_BLOCKED simultaneously; contract-precedence ambiguous.
- **F-B-HIGH-4** — `@authentication_classes([])` at `auth_views_enhanced.py:560` stacked with `@permission_classes([IsAuthenticated])`: DRF auth doesn't run; middleware precedence masks the mismatch; implicit-contract-vs-declared-contract confusion.
- **F-D-WSENVELOPE-1** — WS `{type, data, timestamp}` ad-hoc dicts are the implicit contract; consumers rely on undeclared shape; producer changes silently break consumers.

---

## §17 Duplicate or Overlapping Systems

### §17.1 4-layer permission-floor stack (F-D-4LAYERSPLIT-1 lineage)

Cat D observation: DRF DEFAULT + explicit decorator + path-list gate + custom Permission class all provide "authorization-floor" semantics at different granularity + timing:

- **DRF DEFAULT layer** — global fallback; applies to ALL endpoints unless overridden.
- **Explicit decorator layer** — per-endpoint override.
- **Path-list gate layer** — cross-cutting URL-pattern override; evaluates BEFORE DRF.
- **Custom Permission class layer** — declarative per-endpoint capability check.

These are NOT DUPLICATE (each serves distinct role); they OVERLAP in coverage. `/api/v1/betting/place/` PUBLIC_PATHS + REVIEWER_BLOCKED_PATHS inversion (F-B-HIGH-2) is the concrete evidence that layer-3 (path-list) short-circuits layer-2 (DRF permission_classes) silently.

### §17.2 Two logout envelope shapes (F6 preserved from Cat C S2503)

Basic logout at `core/auth_views.py:91, 94` emits `Response({'detail': ...})`; enhanced logout at `core/auth_views_enhanced.py:554` emits `Response({'message': ...})`. Same semantic; different top-level keys. Cat C S2503 §14.6 F6 preserved; Cat D notes as overlap+drift.

### §17.3 REST↔WS message-emission divergence

REST `APIResponseEnvelope` at 9 hand-invoked sites vs Family A DRF default at inherited-DEFAULT paths vs Family C/D at inline emissions vs WS raw `json.dumps` at 87 Consumer classes. Cat D observation: these are DIFFERENT emission-mechanisms serving analogous roles (structured response envelope); zero cross-mechanism contract SoT.

---

## §18 Ownership Gaps

### §18.1 CODEOWNERS assignment status at HEAD `87624a3d`

Cat D file scope + assignment status (per Agent 4 + Agent 6 read of `./CODEOWNERS`):

| File | Cat D scope? | CODEOWNERS status |
|---|---|---|
| `core/auth_middleware.py` | YES (path-list gates entry point) | ✓ `@clwest` (line 21) |
| `core/auth_views.py` | YES (basic logout emission Family A) | ✓ `@clwest` (line 22) |
| `core/auth_views_enhanced.py` | YES (F6 emission Family C; F-B-HIGH-4 CRITICAL-per-site) | ✓ `@clwest` (line 23) |
| `core/api_responses.py` | YES (APIResponseEnvelope Family B) | ✓ `@clwest` (line 24) |
| `core/services/fleet_auth_drf.py` | YES (FleetCapabilityRequired exemplar) | ✓ `@clwest` (line 25) |
| `core/ws_auth_middleware.py` | YES (WS auth middleware) | ✓ `@clwest` (line 28) |
| `core/asgi.py` | YES (ASGI ProtocolTypeRouter mount) | ✓ `@clwest` fallback via `*` |
| `core/routing.py` | YES (107 core WS route entries) | ⚠ implicit-only via `*` fallback; NO explicit file-level assignment at HEAD |
| `core/consumers*.py` (55 files) | YES (87 Consumer class definitions) | ⚠ implicit-only via `*` fallback; NO explicit file-level assignment |
| `frontend/src/lib/api.ts` | YES (SHAPE-BLIND interceptor) | ✓ `@clwest` (line 31) |
| `frontend/src/stores/authStore.ts` | YES (token lifecycle + persist store) | ✓ `@clwest` (line 32) |
| `frontend/src/components/layout/Sidebar.tsx` | YES (F-D-SIDEBAR-1 partial logout) | ✓ `@clwest` (line 33) |
| `frontend/src/App.tsx` | YES (ProtectedRoute + cockpit legacy redirects) | ✓ `@clwest` (line 34) |
| `frontend/src/hooks/useWebSocket.ts` | YES (WS subscription hook factory + 8 subscription sites) | ⚠ UNASSIGNED; deferred to S2600+ per CODEOWNERS lines 8-13 explicit-deferral comment |
| `frontend/src/lib/cockpitApi.ts` | YES (96% typed island; adjacent to Cat D scope) | ⚠ UNASSIGNED; deferred to S2600+ |
| `frontend/src/hooks/cockpitQueries.ts` | YES (React Query hooks) | ⚠ UNASSIGNED; deferred to S2600+ |
| `frontend/src/lib/apiClient.ts` | YES (adjacent to api.ts) | ⚠ UNASSIGNED; deferred to S2600+ |
| `frontend/src/types/cockpit.ts` | YES (typed schema island) | ⚠ UNASSIGNED; deferred to S2600+ |

**Cat D observation:** backend Cat D surface **~95%-explicit-assigned** (7 files explicit + `core/routing.py` + `core/consumers*.py` via `*` fallback); frontend Cat D surface **4-of-9 explicit-assigned (~44%)**. Frontend gaps are DECLARED-INTENTIONAL per CODEOWNERS lines 8-13 explicit-deferral to S2600+ Group 2200 T-slot maintainer-decision batch. Sole-operator context per S2201 §14 rationale preserved; no immediate action required.

**F-D-OWN-1 lineage note (per Rigby SIGN cycle 1 Q17 AGREE fold — safe closure language; no over-claim):** Cat D provides updated ownership telemetry and reduces uncertainty for backend scope; frontend ownership remains partially unresolved and is deferred to S2600+ per CODEOWNERS. **F-D-OWN-1: partial-scope resolution (backend clarified; frontend deferred).** Cat D does NOT declare F-D-OWN-1 "closed" — closure condition remains post-arc T-slot maintainer decision.

### §18.2 Cat D-specific ownership handoff to Group 2600

Per S2402 CF-B2 preserved: PA workspace-context authorization (F-B-HIGH-3 workspace-membership implicit gate) hands off to Group 2600 PA arc. Cat D enumerates surface (`WORKSPACE_AWARE_AGENTS` 20 agents at `core/epa_handlers_tools.py:191-217`) but does NOT propose enforcement design.

---

## §19 Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows.

### R1 [S2599 xx99 close Chris-D-verdict-request] — Cat B (a)/(b)/(c) permission-floor selection

Cat B S2402 §19.1 three-option decision-space + S2499 CF-B1 preservation: (a) uniform IsAuthenticated (NOT recommended per Cat B; LARGE blast radius), (b) split read-write + client-side auth-check-on-write (Cat B PRIMARY for REMEDIATION WINDOW), (c) per-endpoint permission registry (Cat B PRIMARY for LONG-TERM GOVERNANCE).

**Cat D contribution:** boundary evidence — the FleetCapabilityRequired.for_capability() production exemplar at `core/services/fleet_auth_drf.py:215-263` **demonstrates that a capability-gating MECHANISM PRIMITIVE (per-endpoint declarable intent + model-backed check) is viable at HEAD; it does NOT demonstrate a full Cat B (c) registry/governance system (catalog/admin UI/CI-lint gate/workflow)** (per Rigby SIGN cycle 1 Q18 STRENGTHEN fold — mechanism-vs-governance-system distinction preserved across §5.5 + §9.3 + R1; prevents over-claim reversal of Q5 fold). Registry model + admin UI + CI-lint gate + governance workflow are additive to the mechanism primitive; the DRF permission-class layer supports per-endpoint capability declaration at code-write time.

**Verdict-request:** Chris-D-verdict at xx99 on (a)/(b)/(c) selection. Cat D enumerates trade-offs + provides exemplar; does NOT recommend.

### R2 [S2599 xx99 close Chris-D-verdict-request] — REST↔WS T7 Path A/B/C strictness selection

S2203 §20.6 three-option decision-space verbatim preserved: Path A (full-spectrum strict), Path B (money-path/integrity-critical only), Path C (strict for integrity/governance/money/state-changing; lighter for read-only).

**Cat D contribution:** boundary evidence — REST 4-shape 401 heterogeneity + 6.85% typed api.ts CONSUMER-side + WS raw `json.dumps` dicts at 87 Consumer classes with 0% envelope conformance = current-state maturity table for xx99 verdict input.

**Verdict-request:** Chris-D-verdict at xx99 on Path A/B/C selection. Cat D enumerates + measures; does NOT recommend.

### R3 [S2599 xx99 close artifact candidate] — docs/topics/api.md CREATE

Extends Cat C S2503 R8 recommendation: Cat D contribution to `docs/topics/api.md` if created at xx99 close would include (i) 4-layer permission-floor split narrative, (ii) FleetCapabilityRequired exemplar reference for Cat B (c) pattern, (iii) REST↔WS T7 joint architecture description, (iv) 4-shape 401 heterogeneity + 6.85% typed api.ts + 0% WS envelope conformance denominators, (v) 8-dimension Cat D maturity table (§13).

### R4 [S2599 xx99 close anchor-update batch] — PLATFORM_INVENTORY §API autoblock

S2500 §6 P-1 preserved: PLATFORM_INVENTORY §API autoblock CREATE deferred to xx99 post-arc cascade PR. Cat D denominators contribute: 285 path-list gate entries, 74 class-attribute declarations, 838 explicit `@permission_classes` decorator sites, 3 custom Permission classes, 120 WS route entries, 87 Consumer class definitions, 0% WS envelope conformance rate.

### R5 [S2599 xx99 close anchor-update batch] — PLATFORM_WHAT_IT_IS §API narrative

S2500 §6 P-2 candidate preserved. Cat D narrative contribution: 4-layer permission-floor split + REST↔WS architectural disjointness + Cat D α/β/γ × Cat B (a)/(b)/(c) × Path A/B/C intersection.

### R6 [S2504 Cat D boundary evidence] — WS consumer auth uniformity vs consumer-level rejection variance

Cat D evidence: 120 WS route entries at HEAD all route through `TokenAuthMiddlewareStack` (100% uniform middleware coverage); consumer-level rejection variance NOT audited exhaustively at HEAD (per-consumer `async connect()` implementation varies).

**Handoff:** Cat D S2504 documents uniformity evidence; comprehensive per-consumer authorization audit deferred to post-arc T-slot execution scope.

### R7 [S2504 Cat D + post-arc T-slot maintainer-decision batch] — F-B-HIGH-1 STAFF_REQUIRED_PATHS phantom cleanup + F-B-HIGH-4 stacking cleanup

Both findings preserved from S2402 + relegated to findings-appendix per Rigby SIGN Q1 P4-retitle fold. Execution locus = post-arc T-slot maintainer-decision batch or dedicated cleanup PR.

**Cat D observation on F-B-HIGH-4:** -1 file REDUCTION drift from S2402 baseline (`core/views_nervous.py` cleaned up); remaining 3 files with 6 stacking sites at HEAD. `core/auth_views_enhanced.py:560` CRITICAL-per-site (contains logout).

### R8 [S2599 xx99 close Chris-D-verdict-request] — REVIEWER_BLOCKED_PATHS -5 REDUCTION drift

Cat D drift observation NEW: 12 (S2402 baseline) → 7 (HEAD `87624a3d`). Positive governance signal (list pruned). No action required beyond xx99 anchor-update batch documentation.

### R9 [POST-ARC T-slot maintainer-decision batch] — Custom Permission class ecosystem expansion

Cat D observation: 3 custom Permission classes at HEAD; zero policy-composition SDK; no capability registry model. IF Cat B (c) ratified at xx99 R1, custom Permission class ecosystem expansion becomes execution-plane concern.

### R10 [POST-ARC T-slot dual-owned: Cat D + Group 2600 PA] — REST↔WS T7 joint contract SoT

**CF-D6 NEW cross-arc coordination flag** — dual-ownership with Group 2600 PA per S2500 §3.D "REST↔WS T7 joint 2500+2600" language. Cat D enumerates surface (120 WS routes + 87 Consumer classes + 0% envelope conformance); Group 2600 PA co-authors envelope-shape design if xx99 ratifies Path A/B/C with WS-in-scope. **R10 execution is downstream of R2's Path A/B/C verdict (which defines which contract is made SoT)** (per Rigby SIGN cycle 1 Q19 AGREE fold — light lineage linkage without ownership entanglement; depends_on: R2).

### R11 [S2599 xx99 close Chris-D-verdict-request] — Path-list gate consolidation to registry (F-D-4LAYERSPLIT-1 execution)

IF Cat B (c) ratified at xx99 R1, F-D-4LAYERSPLIT-1 becomes execution question: should path-list gates in `core/auth_middleware.py` migrate to registry-declarative pattern? Cat D does NOT prescribe consolidation; enumerates the option. If R1 selects (b), path-list gates remain WORKING at current maturity + shadow-registry function preserved.

---

## §20 Appendix

### §20.1 Files inspected + tools used

**Backend Python files:**
- `core/settings.py` (DEFAULT_PERMISSION_CLASSES + DRF config)
- `core/auth_middleware.py` (path-list gates + middleware dispatcher)
- `core/auth_views.py`, `core/auth_views_enhanced.py` (logout envelope emissions)
- `core/api_responses.py` (APIResponseEnvelope Family B)
- `core/services/fleet_auth_drf.py` (FleetSignatureRequired + FleetCapabilityRequired)
- `core/ws_auth_middleware.py`, `core/asgi.py` (WS auth stack)
- `core/routing.py` (WS route entries)
- `core/epa_handlers_tools.py` (WORKSPACE_AWARE_AGENTS constant)
- `core/services/tool_dispatcher.py` (PA tool ACL enforcement)
- `core/consumers*.py` (55 files with 87 Consumer class definitions; sampled)

**Frontend TS/TSX files:**
- `frontend/src/lib/api.ts` (SHAPE-BLIND response interceptor)
- `frontend/src/stores/authStore.ts` (token lifecycle)
- `frontend/src/components/layout/Sidebar.tsx` (F-D-SIDEBAR-1)
- `frontend/src/App.tsx` (ProtectedRoute)
- `frontend/src/hooks/useWebSocket.ts` (8 subscription sites; sampled)

**CODEOWNERS:** `./CODEOWNERS` (Cat D file-level assignments verified)

**PLATFORM_INVENTORY:** `docs/PLATFORM_INVENTORY.md` (1,864 URL routes autoblock reference)

**Playbook + predecessor docs:** DOMAIN_RESEARCH_PLAYBOOK.md §11.2/§13/§14/§15 + 2500 parent + 2501/2502/2503 sibling audits + 2202/2203 frontend WS + 2402 auth Cat B + 2499 auth canonical + 2404 Cat D silent-401 systemic

### §20.2 Grep patterns used (parent-Claude direct greps)

```
DEFAULT_PERMISSION_CLASSES (core/settings.py)
@permission_classes (all py files)
permission_classes\s*=\s* (all py files; class-attribute)
@authentication_classes\(\[\]\) (all py files; F-B-HIGH-4 verify)
@permission_classes\(\[\]\) (all py files; F-B-MED-1 verify)
@api_view (all py files; @api_view co-declaration denominator)
FleetCapabilityRequired|FleetSignatureRequired (all py files)
STAFF_REQUIRED_PATHS|REVIEWER_BLOCKED_PATHS|REVIEWER_ALLOWED_PATHS|PUBLIC_PATHS|OPTIONAL_AUTH_PATHS|PUBLIC_PATHS_EXACT (core/auth_middleware.py)
^\s*(?:path|re_path)\( (**/urls*.py)
^\s*(?:re_)?path\( (**/routing.py)
^class\s+\w+Consumer(?:\(.*\))?\s*: (all py files; Consumer class count)
\.(?:group_send|send_json|send)\( (core/consumers*.py; emit-site sample)
async_to_sync\(channel_layer\.group_send\)|channel_layer\.group_send (all py files; emit-site cross-check)
```

Python-parser used for definitive path-list count (block-scoped entry count) — invoked via `python3 -c` inline script; counts string entries per constant.

### §20.3 Unresolved unknowns

1. **Exhaustive per-endpoint permission-floor coverage rate at HEAD:** Cat D preserves S2402 §14.5 F-B-CRIT-1 baseline ~84.4% implicit-inheritance; exhaustive per-endpoint audit not performed (deferred to post-arc T-slot execution scope). Denominator alignment work needed to reconcile 838 decorator sites + 74 class-attr sites (912 total explicit) vs 1,856 core URL routes (49% raw rate vs 15.6% S2402-implied explicit rate).

2. **Exhaustive per-consumer WS authorization pattern audit:** Cat D notes 120 WS route entries + 87 Consumer classes at HEAD; per-consumer `async connect()` authorization pattern (accept + attach vs close-with-code) NOT enumerated exhaustively (deferred to post-arc T-slot execution scope).

3. **F-D-CALL-1 803-scale RE-VERIFY at HEAD:** Cat D preserves S2502 §20.4 baseline via reference; exhaustive parent-Claude enumeration not performed (deferred).

4. **F-D-BYPASS-1 79-raw-fetch RE-VERIFY at HEAD:** Cat D preserves via reference; per-site classification refinement deferred to post-arc T-slot.

5. **Historical remediation lineage for -5 REVIEWER_BLOCKED_PATHS drift + -1 file REDUCTION F-B-HIGH-4 drift:** Cat D notes drift observations but does NOT audit which PR/commit shipped the reductions (out-of-scope for design-prep).

### §20.4 Verifier-loop history

**Sub-agent conflict resolution log (parent-Claude verifier-loop per playbook §14):**

| Conflict | Resolution |
|---|---|
| Agent 2 said PUBLIC_PATHS = 263 entries; Agent 6 said 265 | Parent-Claude Python-parser count returned 265 → Agent 6 correct; Agent 2 was off by 2 (likely comment or blank line miscount) |
| Agent 2 said REVIEWER_BLOCKED_PATHS = 18; Agent 6 said 11; S2402 said 12 | Parent-Claude Python-parser count returned 7 → NEW drift observation; all sub-agents wrong or measuring at different scope; documented as F-14.9 NEW |
| Agent 3 said "51 WS patterns in core/routing.py" + "59 total WS patterns"; parent-Claude grep said 107 core + 120 total | Parent-Claude grep authoritative; Agent 3 miscounted (may have used stricter pattern like `websocket_urlpatterns` matches vs `path()|re_path()` entries) |
| S2402 said 4 files with `@authentication_classes([])`; Agent 4 said 4; parent-Claude grep at HEAD returned 3 files (6 sites) | Parent-Claude grep authoritative; NEW -1 file REDUCTION drift observation (`core/views_nervous.py` remediated between S2402 close and HEAD `87624a3d`) |

**RE-VERIFY at HEAD execution notes:**
- HEAD SHA recorded: `87624a3d` at S2504 open (from `git rev-parse HEAD` + `git log -1 --format='%h %s'`)
- All load-bearing denominators (URL routes, WS routes, Consumer classes, path-list entries, permission-decoration sites, custom Permission classes) verified via parent-Claude direct greps
- S2402/S2202/S2203/S2404/S2501/S2502/S2503 baselines preserved by reference; drift observations documented as NEW findings only when parent-Claude direct grep contradicts predecessor claim
- **Conflict count within expected range** (S2201-S2503 twelve-consecutive tested pattern ~3-7 conflicts per child); **no evidence the 6-parallel sweep was mis-scoped** (per Rigby SIGN cycle 1 Q20 AGREE fold — verifier-loop discipline proportionate).

### §20.5 Rigby SIGN fold notes (Rigby SIGN cycle 1 CLOSED)

**SIGN pin used:** `pa-1aad569644364682` (TWENTY-FIRST consecutive dedicated fresh SIGN pin under Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/S2401/S2402/S2403/S2404/S2499/S2500/S2501/S2502/S2503 twenty prior).

**Cadence applied:** 4-batch × 5-Q = 20-Q child-audit cadence per S2201-S2503 twelve-consecutive tested pattern THIRTEENTH-consecutive application; retired via `session_tool.retire force=true` at cycle close.

**Rigby verdict at cycle 1 close:** SIGN-with-edits + **cycle 2 NOT required** (no new research; only phrasing + anchoring precision). Overall confidence HIGH.

**Total folds landed pre-Chris-ratification: 20** (within 15-25 empirical baseline per S2201-S2503 tested pattern):

- **Batch 1 (Q1-Q5) — §1-§5 Executive + Denominator + Purpose + Entry Points + Models:**
  - Q1 AGREE: soften "zero" language + swap prescription verbs (Executive Summary + Bottom line → Summary observation)
  - Q2 STRENGTHEN: Denominator Definitions block (D1-D6) + S2402 reconciliation sentence + xx99 decision candidate flag
  - Q3 STRENGTHEN: append explicit "out-of-scope for Cat D" guardrail to §1.2 note 3
  - Q4 AGREE: REQUIRE_WEBSOCKET_AUTH T-slot candidate + "No change is proposed here"
  - Q5 STRENGTHEN: FleetCapabilityRequired mechanism-vs-governance-system distinction (§3.2 + §5.5)

- **Batch 2 (Q6-Q10) — §6-§10 APIs + Runtime + Data Ownership + Integrations + Event Flows:**
  - Q6 STRENGTHEN: 79.3% upper-bound risk-weighted-vs-population-weighted disambiguation
  - Q7 AGREE: §7.2 decision-space pointer without prescribing normalization (Cat C R2 territory)
  - Q8 STRENGTHEN: §7.4 REST-per-request vs WS-per-connection unit-mismatch + Group 1700 Observability measurement handoff
  - Q9 AGREE: CF-D6 secondary stakeholders (non-owners) line
  - Q10 STRENGTHEN: §8.1 "MUST" prescriptive language removed + xx99 governance deferral

- **Batch 3 (Q11-Q15) — §11-§15 Documentation + Research Coverage + Maturity + Drift + Debt:**
  - Q11 AGREE: anti-fatigue justification for anchor-update deferral
  - Q12 STRENGTHEN: coverage labels "HEAD implementation evidence depth vs conceptual-spec depth" clarification + T7 split into spec-vs-evidence
  - Q13 AGREE: 8-dimension anti-dilution note + owner/decision pointer per row
  - Q14 AGREE: findings classification "design-plane SoT gaps (missing_connection), not violations of an explicitly adopted standard"
  - Q15 STRENGTHEN: REVIEWER_BLOCKED_PATHS intent-attribution softened to "observed reduction drift suggests pruning; intent/lineage not established here" + optional lineage T-slot task

- **Batch 4 (Q16-Q20) — §16-§20 Boundary Violations + Duplicate/Overlap + Ownership + Recommendations + Appendix:**
  - Q16 STRENGTHEN: Level 0 anchor de-inflation — Cat D adds "Level 0-adjacent candidates for xx99 consolidation" instead of expanding Level 0 scope
  - Q17 AGREE: F-D-OWN-1 partial-scope resolution language (backend clarified; frontend deferred); avoid "closed"
  - Q18 STRENGTHEN: R1 mechanism-primitive-vs-governance-system exact rewrite preserved across §5.5 + §9.3 + R1
  - Q19 AGREE: R10 depends_on: R2 lineage linkage (light; no ownership entanglement)
  - Q20 AGREE: verifier-loop count 4 within expected ~3-7 range; no mis-scope evidence

**Post-fold status:** draft ready for Chris ratification ("commit it" candidate). Status flips `draft` → `active` per playbook §16 draft-first workflow on Chris ratification.

**Verifier-loop fold consistency:** all 20 folds preserve Cat D boundary discipline (enumerate + inventory + measure + classify + defer; does NOT prescribe). No new research triggered by SIGN cycle 1.
