---
title: "Group 2500 API — Canonical Summary (S2599 xx99 arc close)"
status: active
authority: research
version: v1
session_added: 2599
last_verified: 2026-07-06
domain_slug: api
research_group: 2500
child_slot: xx99
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
  - platform_architecture_inventory.md
  - docs/topics/api.md (candidate — CREATE at post-arc cascade PR)
  - docs/research/domains/api/2500_api_domain_scoping.md
  - docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md
  - docs/research/domains/api/2502_api_frontend_client_architecture_design_prep_audit.md
  - docs/research/domains/api/2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md
  - docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md
  - docs/research/domains/auth/2499_auth_canonical_summary.md
related:
  - docs/research/domains/auth/2400_auth_domain_scoping.md
  - docs/PLATFORM_INVENTORY.md (autoblock §API — CREATE at post-arc cascade PR)
delegates_to:
  - Group 2600 PA (T3 handoff — REST↔WS T7 joint contract SoT + `/api/pa/chat/` + `/api/assistant/*` PA-endpoint declaration + workspace-context authz)
  - Group 1700 Observability (T4 handoff — 161 direct 401 emission telemetry + shape-normalization observability + envelope-enforcement locus)
  - Group 2300 Mobile (T5 parallel — silent-401 parallel audit + typed-client parallel consumer surface + mobile-token revocation on logout)
  - Group 1600 Content (T6 parallel — content-publishing endpoint envelope-shape variability + editor/publisher UX contract propagation)
head_commit_before: adf902a0
head_commit_after: TBD
arc_pin: pa-a03b111768464b3f
sign_pin: pa-59d9583dc4da4d5e
verifier_loop: |
  Parent-Claude single-doc synthesis by consuming P1-P4 child audits + parent scoping + S2499 auth canonical summary as prior arc-close exemplar. 5 parallel Explore sub-agent extract reports produced (Cat A + Cat B + Cat C + Cat D + S2499 structure) then verifier-loop reconciled by parent-Claude against source docs. No new evidence sweeps launched per playbook §11.3. Rigby SIGN cycle 1 COMPLETE via dedicated fresh SIGN isolation pin pa-59d9583dc4da4d5e — TWENTY-SECOND consecutive dedicated fresh SIGN pin retirement in Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/S2401/S2402/S2403/S2404/S2499/S2500/S2501/S2502/S2503/S2504 twenty-one prior. Single-batch × 4-Q cadence per S1399-S2499 eleven-consecutive tested pattern TWELFTH-consecutive application. Rigby verdict SIGN-with-edits HIGH confidence Cycle 2 NOT required. 5 folds landed pre-Chris-ratification (1 Q1 STRENGTHEN + 1 Q2 AGREE-optional + 1 Q3 STRENGTHEN + 1 Q4 STRENGTHEN + 1 understated-maturity STRENGTHEN). SIGN pin retired at cycle 1 close via session_tool.retire force=true (updated_count=1, retired=true, previously_active=true).
owner: claude (S2599 xx99 draft; Rigby SIGN cycle 1 SIGN-with-edits + 5 folds landed; Chris ratification PENDING — "commit it" candidate)
---

# Group 2500 API — Canonical Summary (S2599 xx99 arc close)

## 1. Executive Summary

Group 2500 API shipped four child audits — **Cat A Backend Contract SoT Design-Prep (S2501)**, **Cat B Frontend API-Client Architecture Design-Prep (S2502)**, **Cat C Error-Envelope + Refresh + Logout API Contracts Design-Prep (S2503)**, and **Cat D Permission-Floor Registry + REST↔WS T7 Joint Design-Prep (S2504)** — under arc pin `pa-a03b111768464b3f` preserved through all four children per playbook §16 arc-standard behavior. Runtime target 6 sessions HIT (S2500 parent + S2501-S2504 children + this S2599 xx99 close). Central lens question ratified at S2500 Chris "agree all" 2026-07-05: *"Does the platform's REST + WS API surface at HEAD DECLARE its contract source-of-truth (typed request/response schemas + typed error envelopes + per-endpoint permission-floor declarations + WS message-contract) — or are these contracts EMERGENT from runtime/serialization/client inference?"* **Canonical verdict at arc close: The API surface is majority IMPLICIT-INHERITANCE with ISLAND-DECLARATION pockets and ZERO cross-transport SoT.** Mechanism primitives work at file-precision (DRF permission dispatcher, TokenAuthMiddlewareStack for WS, `FleetCapabilityRequired.for_capability(*path)` capability-gate exemplar, cockpitApi 96%-typed island); DECLARATION-plane SoT is absent or non-uniform across all four contract axes (backend schema + consumer typing + error envelope + permission-floor + WS message contract). The gap is design-plane governance, not runtime failure.

Three decision-space quadrants surfaced across the arc converge at S2599 xx99 for Chris D-verdict. Each is independent except one established nesting from Cat C §9.1 Q12 (Cat D typed-error-envelope γ = mechanism ⊃ Cat C session-lifecycle β = UX policy nested inside γ default handler). All other pairings are orthogonal unless xx99 explicitly couples them. **Quadrant I (backend DECLARATION):** Cat A Path A/B/C strictness (Full-spectrum drf-spectacular + codegen / Money-path-only strict / Middle-ground mixed regime) + drf-spectacular wire-up (INSTALLED_APPS + URL routes + management command). **Quadrant II (consumer DECLARATION):** Cat B (a)/(b)/(c) long-term governance (Full-spectrum typed-client codegen / Money-path typed-island expansion / Middle-ground per-mutation-semantics) + SHAPE-BLIND interceptor replacement decision-point. **Quadrant III (error / lifecycle CONTRACT):** Cat C α/β/γ session-lifecycle (α silent-refresh / β explicit re-login / γ hybrid) + envelope shape SoT selection (Family A/B/C/D vs shape-normalization mechanism) + refresh endpoint contract necessity + Clear-Site-Data emission locus + F-C-VIP-1 enforcement mechanism (4 candidate options + Rigby Q18 selection rubric). **Quadrant IV (permission-floor + REST↔WS T7):** Cat B (a)/(b)/(c) permission-floor branch (Uniform IsAuthenticated / AllowAny-read + Auth-write / Per-endpoint registry — LONG-TERM GOVERNANCE per S2499 CF-B1) + Cat D typed-error-envelope α/β/γ + Cat D whitelist-replacement α/β/γ + REST↔WS T7 Path A/B/C message-contract strictness. FleetCapabilityRequired at `core/services/fleet_auth_drf.py:215-263` demonstrates mechanism-primitive viability but does NOT constitute a full governance system.

What ships next at S2599 xx99 close: (a) arc pin `pa-a03b111768464b3f` retirement via `session_tool.retire force=true` — **TWELFTH formal arc-pin retirement in Research OS** (after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2499 eleven prior); (b) dedicated fresh SIGN isolation pin `pa-59d9583dc4da4d5e` retirement at cycle close — **TWENTY-SECOND consecutive dedicated fresh SIGN pin retirement** in Research OS; (c) post-arc T3 Group 2600 PA handoff bundle QUEUED per T-slot follow-on queue with CF-2600-PA + CF-D6 REST↔WS T7 joint dual-owner status; (d) post-arc T4 Group 1700 Observability + T5 Group 2300 Mobile (parallel) + T6 Group 1600 Content secondary-stakeholder handoffs QUEUED per CF-* propagation; (e) P0 rank-1 co-equal remediation batch preserved across P0-A (platform-wide execution scope) + P0-B (token lifecycle / security window) + P0-C (endpoint-specific) tiers with Cat D new-owner rows integrated; (f) anchor-update recommendations for PLATFORM_INVENTORY §API autoblock CREATE + `docs/topics/api.md` CREATE + PLATFORM_WHAT_IT_IS §API narrative subsection + `platform_architecture_inventory.md` §3.22 API Layer REVISE + ARCHITECTURE_INDEX §1.93–§1.97 backfill + v88 → v93 version bump + §7 decision matrix entries for α/β/γ + Path A/B/C + (a)/(b)/(c) decision spaces; (g) §11.3 §10 meta-methodology retrospective **TWELFTH-consecutive application** (adopted S1399 close 2026-07-01 per Chris directive); (h) MC-4 SIXTH-consecutive parent-with-4-children arc close (Groups 1900 + 2000+ + 2100 + 2200 + 2400 + 2500) — CODIFICATION extended.

**Group 2500 API arc CLOSED at this xx99.** Group 2400 Auth (S2400-S2499) closed at prior xx99; Group 2500 API closes here; T3 Group 2600 PA is next per T-slot queue.

---

## 2. What This Arc Answered

Per playbook §11.3 §2 requirement: per-child rollup of the 28 canonical research questions (playbook §9) each child answered, with per-arc specialization. This section rolls up Cat A + Cat B + Cat C + Cat D contributions; §3 consolidates the shape they collectively describe.

### 2.1 Cat A (S2501) — Backend Contract SoT DECLARATION plane

Cat A answered Q1–Q2 (domain purpose: does the backend DECLARE contracts to schema consumers?), Q3 (canonical entry points: `sports/views.py` sole demonstration of 16 `@extend_schema` decorators; `core/*.py` zero decorators; drf-spectacular installed but INSTALLED_APPS-absent + URL-routing-absent + management-command-unrecognized), Q4–Q9 (models/services/APIs: 1,873 URL patterns verified at HEAD; 96 Serializer classes; APIResponseEnvelope 9 invocation sites; DRF DEFAULT `[IsAuthenticated]` `core/settings.py:652-653`), Q10–Q13 (documentation: `platform_architecture_inventory.md` §3.22 API Layer STABLE + MODERATE posture verified), Q19–Q22 (cross-domain: 11 CF-* coordination flags including CF-B1 to Cat D S2504 + CF-D1 for typed-error-envelope + CF-2600-PA / CF-1700-Obs / CF-2300-Mobile / CF-1500-Sports), Q23–Q27 (drift/debt: F1 SoT-ABSENT + F5 drf-spectacular partial-wiring + F6 FOUR-shape 401 heterogeneity), Q28 (future research: R1 Path A/B/C triad resolution + R2 drf-spectacular wire-up decision + R3 per-endpoint permission_classes coverage matrix + R6 `docs/topics/api.md` CREATE + R7 §3.22 API Layer REVISE).

### 2.2 Cat B (S2502) — Frontend Consumer DECLARATION plane

Cat B answered Q1–Q2 (domain purpose: does the frontend consumer DECLARE typed contracts to the backend surface, or infer them?), Q3 (canonical entry points: `frontend/src/lib/api.ts:1-4194` mega-module + 93 apiModule exports + shape-blind interceptor at lines 43-62 + cockpitApi.ts typed-island exemplar), Q4–Q9 (models/services/APIs: 47 exported TS interfaces + 63/856 = 7.36% typed rate + cockpitApi 96%-typed exemplar + 803 consumer call-sites — 57 direct + 667 useQuery/useMutation + 79 raw-fetch bypass + 18 zero-consumer DEAD-CANDIDATE apiModules), Q10–Q13 (documentation: 5-session zero-drift baseline signals governance stall or stable holding discipline — interpretation deferred), Q14–Q17 (integrations: CF-D3 request-log ring buffer dev-only + CF-D4/CF-C4 Group 2300 Mobile parallel + CF-B1 preserved), Q19–Q22 (event flows: SHAPE-BLIND flow via `error.response?.status === 401` + `url.includes('/auth/')` substring whitelist), Q23–Q27 (drift/debt: F3 SHAPE-BLIND HIGH-baseline / CONDITIONAL-CRITICAL + F4 18 DEAD-CANDIDATE apiModules + F5 79-raw-fetch bypass + F7 CODEOWNERS partial-scope closure at repo root `./CODEOWNERS` line 31 + F8 cockpit-surface UNASSIGNED per lines 8-13 explicit deferral), Q28 (future research: R1 CONSUMER Path A/B/C + R2 SHAPE-BLIND replacement 3-sub-question + R3 79-raw-fetch reconciliation + R9 api.ts extraction post-arc T-slot).

### 2.3 Cat C (S2503) — Error/Refresh/Logout CONTRACT-INTERSECTION plane

Cat C answered Q1–Q2 (domain purpose: what does the wire-level contract at the error/refresh/logout intersection look like?), Q3 (canonical entry points: logout at `core/auth_views.py:79-94` + `core/auth_views_enhanced.py:539-556` + refresh endpoint ABSENT at HEAD + Clear-Site-Data header ZERO EMISSION + api.ts interceptor SHAPE-BLIND), Q4–Q9 (models/services/APIs: 4 co-existing 401 shape families Family A DRF `{"detail"}` / Family B APIResponseEnvelope typed / Family C bare `{"message"}` / Family D non-DRF `JsonResponse{"success":false, "error":str}` + 15 client-side persistence surfaces + 1 CLEAN + 3 PARTIAL + 11 NO-CLEANUP = 6.7% declared-cleanup rate), Q10–Q13 (documentation: F-C-VIP-1 `VIPInvite.account_expires_at` at `core/models_vip_invite.py:72` DECLARED-BUT-NOT-ENFORCED — zero enforcement query + zero Celery cleanup task), Q14–Q17 (integrations: CF-C1 direct-owner + CF-C2 to Group 2600 PA session workspace-context + CF-C3 to Group 1700 Observability structured-event emit + CF-C4 to Group 2300 Mobile token revocation + CF-C5 to Group 2200 post-arc storageKeys 15-surface + CF-C7 Group 1900 Authority KillSwitch boundary preserved + CF-C8 NEW to Group 1600 Content envelope shape variability), Q19–Q22 (event flows: session-lifecycle α/β/γ decision-space + established nesting Cat D γ mechanism ⊃ Cat C β UX policy — all other pairings INDEPENDENT), Q23–Q27 (drift/debt: F1 4-shape + F2 storageKeys + F3 refresh absent + F4 CSD zero + F5 SHAPE-BLIND re-verified + F6 basic-vs-enhanced logout `detail` vs `message` key drift + F7 F-C-VIP-1 + F8 F-D-SIDEBAR-1), Q28 (future research: R1 α/β/γ + typed-error-envelope + whitelist-replacement three-space resolution + R2 envelope SoT selection + R3 refresh-endpoint necessity coupled to α/β/γ + R4 CSD emission locus + R11 F-C-VIP-1 4-option enforcement rubric).

### 2.4 Cat D (S2504) — Permission-Floor Registry + REST↔WS T7 Joint plane

Cat D answered Q1–Q2 (domain purpose: how are permission floors declared per endpoint at HEAD, and how does the REST↔WS message-contract SoT surface relate?), Q3 (canonical entry points: `core/auth_middleware.py:94-561` 285-entry path-list gate registry — 265 PUBLIC + 6 other lists + `core/settings.py:652-653` DRF DEFAULT + 838 explicit `@permission_classes` decorator sites + 74 class-attr sites + 3 custom Permission classes + `core/services/fleet_auth_drf.py:215-263` `.for_capability(*path)` MECHANISM PRIMITIVE exemplar + 120 WS routes + 87 Consumer classes), Q4–Q9 (models/services/APIs: F-D-4LAYERSPLIT-1 4-layer permission-floor split with NO cross-layer SoT + middleware evaluates FIRST + short-circuits DRF dispatch + 0/40 unique consumer classes conform to `ui.render_hint` envelope), Q10–Q13 (documentation: §1.1 Denominator Contract D1-D6 established — 838/1,856 = 49% route-indexed explicit surface ratio is NOT directly comparable to S2402's ~84.4% implicit-inheritance estimate; D4 unique-view denominator UNKNOWN), Q14–Q17 (integrations: CF-D6 REST↔WS T7 joint dual-owned Group 2500 API + Group 2600 PA + secondary Group 1700 Observability + Group 2300 Mobile), Q19–Q22 (event flows: 4 INDEPENDENT decision-spaces model preserved with ONE nesting), Q23–Q27 (drift/debt: F-D-REGISTRY-1 GREENFIELD + F-D-WSENVELOPE-1 GREENFIELD + F-D-4LAYERSPLIT-1 MEDIUM + F-D-CALL-1 / F-D-BYPASS-1 / F-D-ENVELOPE-1 / F-D-BOUNDARY-1 / F-D-SIDEBAR-1 / F-D-WHITELIST-1 preserved lineage + F-D-OWN-1 partial-scope resolution + Level 0 anchor scope PRESERVED + 2 Level 0-adjacent candidates ADDED for xx99 consolidation), Q28 (future research: R1 (a)/(b)/(c) selection Cat B branch + R2 REST↔WS T7 Path A/B/C strictness + R6 WS per-connection authz audit + drift observations REVIEWER_BLOCKED_PATHS 12→7 + WS routes 125→120 + `@authentication_classes([])` 4→3 files).

### 2.5 28-question coverage rollup

All 28 canonical questions addressed across the four children with per-child specialization: Cat A owns backend DECLARATION-side Q3/Q4/Q6 + Q23-Q25; Cat B owns consumer DECLARATION-side Q3-Q6 + Q23-Q25; Cat C owns wire-level CONTRACT intersection Q4-Q6 + Q19-Q20 + Q23-Q26; Cat D owns permission-floor + REST↔WS joint Q3-Q9 + Q19-Q22 + Q23-Q27. Q10-Q13 documentation coverage is per-child but consolidated in this §2 rollup. Q14-Q18 domain-adjacencies rolled up via §9 cross-links table.

---

## 3. Consolidated Domain Shape

The Group 2500 API surface at HEAD `adf902a0` decomposes into four layered planes with MECHANISM working at file-precision but DECLARATION SoT absent or fragmented at every plane boundary. The stack below is the reader's mental model for the arc's canonical picture.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  BACKEND DECLARATION PLANE (Cat A)                                       │
│  ─────────────────────────                                               │
│  drf-spectacular INSTALLED + CONFIGURED + INSTALLED_APPS-ABSENT          │
│  + URL-ROUTING-ABSENT + management-command-UNRECOGNIZED (F1/F5)          │
│  16 @extend_schema (sports/views.py) + 0 @extend_schema (core/*.py)      │
│  1,873 URL patterns  ·  96 Serializer classes  ·  APIResponseEnvelope    │
│  9 sites  ·  DRF DEFAULT [IsAuthenticated] @ core/settings.py:652-653    │
│  Path A/B/C strictness — Chris-D-verdict-request at S2599 xx99           │
│                                                                          │
│  ↓ contract flows to wire (or fails to)                                  │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  WIRE CONTRACT PLANE (Cat C)                                             │
│  ──────────────────                                                      │
│  4 co-existing 401 shape families:                                       │
│    Family A — DRF default {"detail": "..."}  (~80-90% implicit)          │
│    Family B — APIResponseEnvelope typed {"success":false,"error":{...}}  │
│    Family C — bare DRF {"message": "..."} (enhanced-logout)              │
│    Family D — non-DRF JsonResponse {"success":false,"error":str}         │
│  Refresh endpoint ABSENT at HEAD                                         │
│  Clear-Site-Data ZERO EMISSION on logout                                 │
│  Basic-vs-enhanced logout key-name DRIFT ('detail' vs 'message')         │
│  15 client-side persistence surfaces × 6.7% declared cleanup             │
│  Session-lifecycle α/β/γ — Chris-D-verdict-request at S2599 xx99         │
│  Envelope SoT selection — Chris-D-verdict-request at S2599 xx99          │
│                                                                          │
│  ↓ heterogeneous shapes flow into consumer                               │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  CONSUMER DECLARATION PLANE (Cat B)                                      │
│  ────────────────────────                                                │
│  frontend/src/lib/api.ts — 4,194 LOC + 93 apiModules + 47 interfaces     │
│  Typed rate 63/856 = 7.36%  ·  cockpitApi.ts 96%-typed island exemplar   │
│  18 DEAD-CANDIDATE apiModules (zero-consumer 5-session persistent)       │
│  SHAPE-BLIND interceptor api.ts:43-62 — reads status + URL, NOT body     │
│  All 4 shape families flow through identical non-auth reject branch      │
│  79 raw fetch() calls across 31 files bypass axios interceptor entirely  │
│  803 consumer call-sites (57 direct + 667 hook + 79 raw)                 │
│  (a)/(b)/(c) governance — Chris-D-verdict-request at S2599 xx99          │
│                                                                          │
│  ↓ frontend UX handles heterogeneity opaquely                            │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  PERMISSION-FLOOR + REST↔WS PLANE (Cat D)                                │
│  ──────────────────────────────                                          │
│  4-layer permission-floor stack with NO cross-layer SoT:                 │
│    (i)  DRF DEFAULT [IsAuthenticated]        core/settings.py:652-653    │
│    (ii) Explicit @permission_classes         838 sites + 74 class-attrs  │
│    (iii) Path-list gate                      285 entries in middleware   │
│    (iv) Custom Permission classes            3 classes (Fleet + Intel)   │
│  Middleware (layer iii) evaluates FIRST + short-circuits DRF dispatch    │
│  Source of F-B-HIGH-2 dead-code inversion at /api/v1/betting/place/      │
│  FleetCapabilityRequired.for_capability(*path) MECHANISM PRIMITIVE       │
│  exemplar @ core/services/fleet_auth_drf.py:215-263                      │
│  Cat B (a)/(b)/(c) LONG-TERM GOVERNANCE — F-D-REGISTRY-1 GREENFIELD      │
│  REST↔WS T7 joint contract SoT — F-D-WSENVELOPE-1 GREENFIELD             │
│    120 WS routes  ·  87 Consumer classes  ·  0/40 envelope conformance   │
│  (a)/(b)/(c) permission-floor + Path A/B/C strictness — xx99 verdict     │
│                                                                          │
│  ↓ cross-transport (REST + WS) governance layer                          │
└─────────────────────────────────────────────────────────────────────────┘

     Level 0 canonical anchor scope (Cat C S2503 §16, PRESERVED):
       (1) error envelope, (2) refresh, (3) logout
     Level 0-adjacent candidates for xx99 consolidation (Cat D S2504 §16):
       (4) permission-floor semantics, (5) REST↔WS message-contract strictness
```

### 3.1 Numerical summary — consolidated single reference

| Axis | Metric | Value | Provenance |
|---|---|---|---|
| Backend URL routes at HEAD | `path()` patterns across `core/urls*.py` + `sports/urls.py` | 1,873 (Cat A) → 1,856 (Cat D §1.1 D1) | Cat A §14.6 F2 + Cat D §1.1 |
| Backend view files | `core/views*.py` | 209 | PLATFORM_INVENTORY + Cat A §3.22 verified |
| Backend `@extend_schema` decorators | Sports vs Core split | 16 (sports/views.py) + 0 (core/*.py) | Cat A §3 |
| Backend Serializer classes | ~25 money-path (sports/serializers.py) + others | 96 total | Cat A §14 |
| Backend APIResponseEnvelope emission sites | Direct `.error()` / `.success()` invocations | 9 (Cat A F6 shape B) | Cat A §14.6 F6 |
| Backend 401 emission sites (all shapes) | Direct + implicit | 161 direct + 4-shape family split | Cat A §14.6 F6 |
| Backend DRF DEFAULT_PERMISSION_CLASSES | `IsAuthenticated` inheritance rate | ~80-90% implicit (S2402 §14.5 F-B-CRIT-1) | Cat D §1.1 preserves |
| Backend `@permission_classes` decorator sites | Explicit + class-attr split | 838 sites + 74 class-attrs across 126 files | Cat D §14.1 |
| Backend path-list gate entries | PUBLIC + 5 other lists (STAFF_REQUIRED + REVIEWER_BLOCKED etc.) | 285 total (265 PUBLIC) | Cat D §14.3 |
| Backend custom Permission classes | `FleetSignatureRequired` + `FleetCapabilityRequired` + `PublicIntelTokenAuth` | 3 | Cat D §14.3 |
| Backend WS route entries | ProtocolTypeRouter + URL routing | 120 (drift -5 from S2202 baseline 125) | Cat D drift observations |
| Backend WS Consumer classes | `core/consumers*.py` | 87 | Cat D §14.2 |
| Backend WS auth-middleware uniformity | Consumers routed through `TokenAuthMiddlewareStack` | 100% (Rigby xx99 SIGN understated-maturity STRENGTHEN fold — MECHANISM working uniformly at middleware layer even though envelope/contract SoT is greenfield) | Cat D §14.2 |
| Backend WS message-envelope conformance | Consumers using `ui.render_hint` envelope | 0/40 (0%) | Cat D §14.2 preserves S2202 F3 |
| Frontend api.ts LOC | Mega-module size | 4,194 LOC | Cat B §14 F1 |
| Frontend api.ts apiModules | Exported module count | 93 | Cat B §14 F1 |
| Frontend api.ts exported TS interfaces | Type declarations | 47 | Cat B §14 F1 |
| Frontend api.ts typed rate | Typed `api.<verb><T>` / all `api.<verb>()` | 63/856 = 7.36% | Cat B §14 F2 |
| Frontend cockpitApi.ts typed rate | Typed-island exemplar | ~96% (Cat B §14 F1 sub-observation) | Cat B §14 |
| Frontend DEAD-CANDIDATE apiModules | Zero-consumer at HEAD | 18 modules × 5-session persistent | Cat B §14 F4 |
| Frontend raw-fetch bypass sites | `fetch(...)` outside axios | 79 across 31 files (9.8% of 803) | Cat B §14 F5 |
| Frontend consumer call-sites total | Direct + hook + raw | 803 (57 + 667 + 79) | Cat B §14 preserves S2404 F-D-CALL-1 |
| Frontend interceptor SHAPE-BLIND | Reads status + URL, not body | api.ts:43-62 substring whitelist | Cat B §14 F3 |
| Frontend codegen tooling | openapi-typescript / orval / kubb / zod | 0 in package.json | Cat B §14 F6 |
| Frontend CODEOWNERS explicit lines | Backend files with `@clwest` explicit assignment | 7 files (~95%) | Cat B §14 F7 |
| Frontend CODEOWNERS explicit lines | Frontend files with explicit assignment | 4 of 9 (~44%; cockpit + hooks + apiClient UNASSIGNED per lines 8-13) | Cat B §14 F8 |
| Wire 401 shape families | Distinct response shape count | 4 (Family A/B/C/D) | Cat A §14.6 F6 + Cat C §14 F1 |
| Wire refresh endpoint at HEAD | Present count | 0 (F3 ABSENT) | Cat C §14 F3 |
| Wire Clear-Site-Data emission | Response header set on logout | 0 sites (F4 ZERO) | Cat C §14 F4 |
| Client-side persistence surfaces | Zustand persist + localStorage keys | 15 (1 CLEAN + 3 PARTIAL + 11 NO-CLEANUP) | Cat C §14 F2 |
| Client-side declared cleanup rate | Surfaces with logout hygiene | 6.7% (1/15 CLEAN; 4/15 CLEAN-or-PARTIAL) | Cat C §14 F2 |
| Drift REVIEWER_BLOCKED_PATHS | Path-list entry count (S2402 → HEAD) | 12 → 7 (-5 REDUCTION drift) | Cat D drift observations |
| Drift @authentication_classes([]) file count | Files stacking + `[IsAuthenticated]` | 4 → 3 files (`core/views_nervous.py` cleaned up) | Cat D drift observations |

**Denominator contract (Cat D §1.1 D1-D6, canonical for future comparisons):** D1 = total URL patterns; D2 = URL patterns backing DRF view (unique-view mapping); D3 = URL patterns backing non-DRF view; D4 = unique view instances (deduplication of D2 across sibling paths — UNKNOWN at HEAD); D5 = URL patterns explicitly declaring `permission_classes`; D6 = URL patterns inheriting DRF DEFAULT. **838/1,856 = 49% is a route-indexed decoration-site density, NOT an explicit-permission coverage rate** (Rigby xx99 SIGN Q1 STRENGTHEN fold — prevents quote-mining). **838/1,856 = 49% route-indexed explicit surface ratio is NOT directly comparable to S2402's ~84.4% implicit-inheritance estimate** (S2402 = view-level inheritance; Cat D = route-level decoration site). Both preserved as authoritative for their denominator; **xx99 decision candidate: fund route→view normalization pass to compute D4**.

---

## 4. Cross-Cutting Patterns

Patterns visible across ≥2 children (playbook §11.3 §4 threshold). Not per-child findings; not domain-level facts; the arc's contribution to what the platform's API surface repeatedly does regardless of which contract axis you inspect.

### 4.1 Declared-but-unenforced contract

A discipline where a contract element is DECLARED in code, documentation, or schema — but has **no runtime enforcement** at the point of consumption. Present in ALL FOUR children:

- **Cat A F1 SoT-ABSENT**: drf-spectacular is INSTALLED + CONFIGURED + `@extend_schema` decorators exist (16 in sports/views.py) — but zero enforcement (INSTALLED_APPS-absent + URL-routing-absent + management-command-unrecognized = schema never generated + never consumed).
- **Cat C F3 refresh-endpoint ABSENT**: implicit permanent-token contract — no declaration; no enforcement; behavior emerges from token model semantics.
- **Cat C F7 F-C-VIP-1**: `VIPInvite.account_expires_at` field DECLARED at `core/models_vip_invite.py:72` — zero runtime check + zero periodic cleanup task = enforcement-fictional.
- **Cat D F-D-REGISTRY-1**: per-endpoint permission-floor registry ABSENT at HEAD (Cat B (c) LONG-TERM GOVERNANCE = greenfield). 838 explicit `@permission_classes` sites exist but no cross-layer registry declares "which endpoint requires which floor by policy" — enforcement is per-decorator + per-middleware-list.
- **Cat D F-D-WSENVELOPE-1**: WS message-contract SoT ABSENT at HEAD (T7 joint per S2203 §17.3 = greenfield). Zero TypedDict/Protocol/BaseModel envelope shapes; 0/40 consumer conformance to `ui.render_hint` per S2202 §14 F3 preserved.

**Class:** `technical_debt` + `missing_connection` (Cat A/D) + `unclear_owner` (Cat C VIP). **Systemic pattern:** the platform declares intent (schema decorators, model fields, path-list entries, envelope shape names) at Level 2 (implementation) but rarely at Level 0 (canonical) with cross-layer enforcement. Whether this is DEBT or DELIBERATE STAGING is a Chris-D-verdict; Cat C S2503 explicit-contract-missing Level 0 anchor + Cat D S2504 Level 0-adjacent candidates frame it as the former.

### 4.2 SHAPE-BLIND consumer surface

The frontend consumes heterogeneous backend response shapes without shape-discriminating. Present in Cat B + Cat C + Cat D:

- **Cat B F3**: `frontend/src/lib/api.ts:43-62` response interceptor reads `error.response?.status === 401` (status code) but NOT body shape; branches only on `url.includes('/auth/')` substring whitelist. All four backend shape families flow through the identical non-auth reject branch.
- **Cat C F5 RE-VERIFIED**: shape-blind interceptor 5-session zero-delta at HEAD; Cat C confirms this attach point is the CONSUMER-side locus for typed-envelope adoption.
- **Cat D F-D-CALL-1 preserved**: 803-scale consumer surface (57 direct + 667 hook + 79 raw) all downstream of shape-blind interceptor.

**End-to-end pattern sentence (Rigby xx99 SIGN Q3 STRENGTHEN fold):** **4-shape 401 heterogeneity at Cat A (emission side) → SHAPE-BLIND interceptor at Cat B (attach point) → 803-scale consumer flow-through at Cat D (propagation) = one end-to-end pipeline** where any envelope-shape change at emission requires simultaneous or preceding change at attach point OR the 803-site propagation absorbs heterogeneity opaquely (silent-401 SYMPTOM).

**Class:** `technical_debt` + `drift`. **Consequence:** the choice of backend envelope shape (Family A/B/C/D) has no consumer-side observability today; changing shape requires simultaneous consumer-side awareness or shape-normalization. Cat D α/β/γ typed-error-envelope decision is coupled to this via Rigby Q6 fold established nesting (Cat D γ = mechanism ⊃ Cat C β = UX policy nested inside γ default handler). **This pattern also imposes a design-order sequencing:** ANY envelope-shape SoT selection at xx99 that requires consumer-side discrimination requires SHAPE-BLIND replacement to land first (or simultaneously). Cat B F3 flags this as HIGH baseline / CONDITIONAL CRITICAL if xx99 selects a mechanism requiring shape-normalized payloads AND interceptor remains shape-blind.

### 4.3 Greenfield governance layers

Cat D §13 8-dimension maturity table records 2 GREENFIELD + 1 EXPERIMENTAL dimensions for the arc-scope surfaces:

- **F6 per-endpoint permission registry (Cat B (c))** — GREENFIELD (zero DB model, zero admin UI, zero CI-lint; FleetCapabilityRequired MECHANISM PRIMITIVE viable at HEAD but does NOT constitute full governance system).
- **F8 whitelist-replacement α/β/γ mechanism** — GREENFIELD (zero implementation; γ PROPOSED PRIMARY per Rigby Q7 STRENGTHEN fold = `authHandling: 'default' | 'suppress_redirect'` string enum + telemetry).
- **F5 REST↔WS message-contract parallel (T7 joint)** — EXPERIMENTAL (REST 9 APIResponseEnvelope + 4-shape heterogeneity; WS 0/40 envelope conformance + 87 Consumer classes raw dicts; zero cross-transport SoT).

**Class:** `technical_debt` + `missing_connection`. **Systemic pattern:** the arc's most load-bearing Chris-D-verdicts (Cat B (c) permission-floor + Cat D whitelist-replacement γ + Cat D T7 joint) are ALL GREENFIELD — no existing scaffold to fold onto. This distinguishes them from Cat A Path A/B/C (existing drf-spectacular scaffold) and Cat B (a)/(b)(c) typed-client (existing cockpitApi exemplar). **Design-plane consequence:** greenfield decisions have larger blast radius but zero migration friction; xx99 verdict rank-1 batch preserves this via P0 tiering.

### 4.4 Fragmentation across parallel layers

Multiple parallel surfaces solving overlapping concerns without cross-surface SoT. Present in ALL FOUR children:

- **Cat D F-D-4LAYERSPLIT-1**: 4-layer permission-floor stack (DRF DEFAULT + explicit decorator + path-list gate + custom Permission class) with NO cross-layer SoT; middleware evaluates FIRST + short-circuits DRF dispatch — source of F-B-HIGH-2 dead-code inversion at `/api/v1/betting/place/`.
- **Cat A F6 + Cat C F1**: 4 co-existing 401 shape families with no upstream normalization.
- **Cat C F6**: basic-vs-enhanced logout emits `{'detail': ...}` (basic) vs `{'message': ...}` (enhanced) for the same semantic — same-arc within-domain shape divergence blocking consumer-unified parsing.
- **Cat C F2**: 15-surface × logout-cleanup 6.7% declared-rate — 15 parallel storage surfaces (Zustand persist + localStorage keys) with no cross-surface cleanup contract.
- **Cat B F1**: 93 apiModules + 4,194 LOC in one file — parallel module surface without extraction discipline.

**Class:** `technical_debt` + `duplicate_model` (Cat C F6 basic/enhanced) + `unclear_owner` (Cat D 4-layer). **Systemic pattern:** the arc surfaces reveal repeated multi-layer accretion where each layer independently accretes without cross-layer governance. **Design-plane consequence:** consolidating one layer without touching the others produces inversions (Cat D F-D-BOUNDARY-1 dead-code at bet-placement endpoint) or drift (Cat C F6 key-name divergence).

### 4.5 Boundary discipline preserved across all four children

Every child audit stayed in EVIDENCE + INVENTORY + OPTION-SPACE ENUMERATION mode; none prescribed a verdict. This is a methodology pattern, not a domain finding. Present in ALL FOUR children:

- **Cat A** §16 explicit non-declaration of Level 0; Path A/B/C evidence only.
- **Cat B** §16 explicit non-declaration of Level 0; (a)/(b)/(c) evidence only.
- **Cat C** §16 Level 0 anchor declared (3 domains) but option resolution deferred.
- **Cat D** §16 preserved Cat C Level 0 scope + added 2 adjacent candidates for xx99 consolidation (NOT anchor redefinition).

**Consequence:** xx99 canonical summary is the FIRST point where option-space Chris-D-verdicts consolidate. §7 anchor-update recommendations + §8 follow-on queue reflect this consolidation, but the summary itself does NOT prescribe verdicts either — Chris ratification card at close does. **Meta-methodology adoption:** this discipline is the direct heir of the S2400 arc boundary-preservation discipline (see §10.1 What worked).

### 4.6 Cross-arc coordination flag propagation

CF-* flags introduced by one child are preserved + refined by downstream children. Present in ALL FOUR children:

- CF-B1 (S2499 → S2501 Cat A refines DECLARATION side → S2504 Cat D owns Cat B (c) governance side).
- CF-D1 (S2499 → S2501 Cat A refines 4-shape 401 heterogeneity → S2503 Cat C refines Family A/B/C/D taxonomy → S2504 Cat D preserves).
- CF-C4 (S2503 Group 2300 Mobile silent-401 parallel → CF-D6 secondary stakeholder set in Cat D — Group 1700 Observability + Group 2300 Mobile).
- CF-C8 (S2503 NEW to Group 1600 Content — envelope shape variability leaks into publisher UX).
- CF-2600-PA (S2501 originated to Group 2600 PA — carried through Cat D CF-D6 REST↔WS T7 joint dual-owner status).

**Class:** methodology pattern (not `finding_type`). **Systemic pattern:** cross-arc coordination is bookkeeping-heavy but the CF-* framing gave every downstream owner a clear pointer. Group 2600 PA T3 handoff bundle inherits at least 4 CF-* originated across S2501-S2504.

---

## 5. Resolved Contradictions

Where children disagreed on counts, framings, or classifications. Each contradiction gets a canonical verdict + rationale.

### 5.1 URL pattern count drift (Cat A 1,873 vs Cat D 1,856)

Cat A §14.6 F2 measured 1,873 URL patterns at HEAD (S2501 draft time). Cat D §1.1 D1 baseline measured 1,856 at HEAD (S2504 draft time). Delta: -17 patterns across the arc window.

**Canonical verdict:** Both counts are HEAD-verified at their respective draft times; the drift is real code drift within the arc window (~11 sessions). Per playbook §14 "count conflicts resolved against runtime inventory" and DOC_LIFECYCLE.md §2c, PLATFORM_INVENTORY.md is the sole authoritative counts source. PLATFORM_INVENTORY.md at HEAD `e617af59` reports 1,864 URL routes. Adopt **1,864** as the canonical S2500 arc-close count; note the Cat A vs Cat D drift as evidence of ongoing sub-arc mutation. **Attribution:** normal in-flight route churn during arc window.

### 5.2 Route-indexed 49% (Cat D) vs implicit-inheritance ~84.4% (S2402)

Cat D §1.1 D1-D6 established that 838/1,856 = 49% "route-indexed explicit surface ratio" is NOT directly comparable to S2402 §14.5 F-B-CRIT-1's ~84.4% implicit-inheritance estimate.

**Canonical verdict:** BOTH preserved; neither replaces the other. S2402 F-B-CRIT-1 measured view-level inheritance (denominator = unique views); Cat D §1.1 D5 measures decoration site density (denominator = URL routes). D4 = unique-view mapping is UNKNOWN at HEAD. **xx99 decision candidate promoted to §8 P0-A batch:** fund route→view normalization pass to compute D4 and enable direct comparison. Until D4 is computed, both ratios are internally consistent for their denominator + not interchangeable in downstream design-prep verdicts.

### 5.3 401 shape family taxonomy (Cat A Shape (a)/(b)/(c)/(d) vs Cat C Family A/B/C/D)

Cat A §14.6 F6 tracks 4 shapes labeled (a)/(b)/(c)/(d). Cat C §14 F1 tracks 4 families labeled A/B/C/D. Same underlying phenomenon, different labels.

**Canonical verdict:** Adopt Cat C's Family A/B/C/D labeling as canonical (Family = capital letter; shape = lowercase); rationale: Cat C is the CONTRACT plane where envelope taxonomy is load-bearing for future design-prep, and Family A/B/C/D is the labeling that will appear in `docs/topics/api.md` CREATE + PLATFORM_INVENTORY §API autoblock. Cat A shape (a)/(b)/(c)/(d) is preserved as historical origin but downstream design-prep should use Family A/B/C/D. **Attribution:** Cat A originated the FOUR-shape discovery (verifier-loop expansion from v0 three-shape per Rigby Q7 STRENGTHEN); Cat C canonicalized the labeling.

### 5.4 F-B-HIGH-2 lineage (Cat B extract "NOT FOUND" vs Cat D F-D-BOUNDARY-1 preserves)

Cat B extract report says "F-B-HIGH-2 dead-code inversion NOT FOUND in this audit." Cat D §14 F-D-BOUNDARY-1 references F-B-HIGH-2 as `/api/v1/betting/place/` PUBLIC + REVIEWER_BLOCKED implicit-contract violation preserved from S2402.

**Canonical verdict:** F-B-HIGH-2 is a **S2402 Group 2400 finding**, NOT a Cat B S2502 finding. Cat D S2504 §14.6 F-D-BOUNDARY-1 preserves it as arc-inherited evidence with its S2402 lineage intact. Cat B did NOT define F-B-HIGH-2; Cat B's F-* codes are its own (F1-F8). **Attribution:** Cat B extract report was accurate in reporting "NOT FOUND in this audit"; downstream code F-B-HIGH-2 is arc-inherited via S2499 CF-* + S2402 §14.5. **No contradiction:** both statements hold simultaneously; the labeling ambiguity is resolved by attribution-to-origin.

### 5.5 Silent-401 SYSTEMIC framing (Cat B ROOT CAUSE via SHAPE-BLIND vs Cat D SYMPTOM of permission-floor accretion)

Cat B F3 SHAPE-BLIND presents the interceptor as the CAUSE surface. Cat D §14 F-D-CALL-1 preserves 803-scale silent-401 as SYMPTOM of permission-floor implicit-inheritance + F-B-CRIT-1.

**Canonical verdict:** NO CONTRADICTION; both framings hold simultaneously (two-sided FE-symptom-vs-BE-model discipline preserved from S2499 §4.4). SHAPE-BLIND is the consumer-side observability failure; permission-floor implicit-inheritance is the backend-side declaration failure. Silent-401 emerges at the intersection. Downstream design-prep must address BOTH — the "co-equal contract" model from S2499 §8.1 rank-1 P0 batch extends to Group 2500 with Cat D new-owner rows integrated. **Attribution:** Cat C §4.4 (via S2499) originated the two-sided framing; Cat D S2504 preserves.

---

## 6. Unresolved Unknowns

Explicit list of what the arc did NOT answer. Promotes directly to §8 follow-on queue.

- **U1: D4 unique-view denominator UNKNOWN** — Cat D §1.1 D1-D6 established that D4 (unique view instances via route→view deduplication) is not computable at HEAD without a normalization pass. Route-indexed vs view-indexed ratios are internally consistent but not interchangeable. **Promote to P0-A batch.**
- **U2: drf-spectacular schema.yaml generation feasibility** — Cat A §14.6 F5 partial-wiring re-verified at S2501 open (INSTALLED_APPS absent + URL-routing absent + management-command unrecognized). Whether existing 16 `@extend_schema` decorators would produce a working OpenAPI 3.0 spec after wire-up is NOT tested (S2299 §6 UNKNOWN 5 preserved). **Blocks Cat A R1 Path A/B/C verdict landing.**
- **U3: Refresh endpoint semantics** — Cat C F3 refresh ABSENT at HEAD. Whether the platform SHOULD have refresh (coupled to α/β/γ session-lifecycle verdict) is a Chris-D-verdict-request. If β explicit re-login selected, refresh remains absent-by-design; if α or γ selected, refresh becomes P0 with F-TOKEN-1 prerequisite lineage.
- **U4: Clear-Site-Data header value spec** — Cat C F4 zero-emission; F-C-CSD-1 enumerated 3 candidate emission loci but header value (which of `cache`/`cookies`/`storage`/`executionContexts`) deferred to Cat A downstream per S2403 R2 lineage. **Not answered in this arc.**
- **U5: Cross-tab logout propagation intent** — 0 BroadcastChannel matches at HEAD; 0 `storage` event listener matches. Cat C CF-C5 preserved (Group 2200 post-arc T-slot dual-owned). Whether this is intent-driven ("we don't need cross-tab propagation for our UX") or debt is UNKNOWN.
- **U6: WS envelope-schema TypedDict vs Protocol vs BaseModel decision** — Cat D F-D-WSENVELOPE-1 GREENFIELD; xx99 Chris-D-verdict-request on which schema type to adopt (TypedDict = duck-typed; Protocol = structural; BaseModel = Pydantic-validated). Coupled to REST↔WS T7 Path A/B/C strictness verdict.
- **U7: paStore field-list completeness** — Cat C F2 tracks 3-of-9 syncUser fields wiped on paStore reset. Whether remaining 6 fields are intent-preserved (draft continuity across sessions) or cleanup debt is UNKNOWN.
- **U8: 79-raw-fetch bypass per-site classification** — Cat B F5 preserves the 79-count; Cat D S2504 defers per-site (auth-touching vs streaming vs external-API vs test-fixture) classification to post-arc T-slot. Whether the correct disposition is (a) migrate per-site / (b) global fetch wrapper / (c) leave-as-is + document is UNKNOWN.

---

## 7. Anchor-Update Recommendations

Concrete proposed edits. Per playbook §11.3, this summary does NOT edit anchors itself; the ARCHITECTURE_INDEX v-bump commit at post-arc cascade PR applies them.

### 7.1 PLATFORM_INVENTORY.md

- **AU-1 (CREATE §API autoblock)** — Analog to Group 2400's §Auth autoblock CREATED at S2499 close per AU-1+AU-B2+AU-C2+AU-D3 fold. **Cat D §1.1 Denominator Contract D1-D6 (Rigby xx99 SIGN Q2 AGREE-optional fold — name explicitly)**: D1 total URL patterns + D2 URL patterns backing DRF view + D3 URL patterns backing non-DRF view + D4 unique view instances (UNKNOWN at HEAD — see U1) + D5 URL patterns explicitly declaring `permission_classes` + D6 URL patterns inheriting DRF DEFAULT. Cat D denominators: 285 path-list gate entries + 74 class-attr + 838 decorator sites + 3 custom Permission classes + 120 WS route entries + 87 Consumer class definitions + 0% WS envelope conformance + 16 sports `@extend_schema` + 0 core `@extend_schema` + 9 APIResponseEnvelope sites + 4-family 401 shape breakdown + 79 raw-fetch bypass count + 4,194 api.ts LOC + 93 apiModule + 63/856 = 7.36% typed rate + 18 DEAD-CANDIDATE + 15 client-side persistence surfaces + 6.7% declared cleanup rate. Autoblock generator command: `python manage.py generate_platform_inventory` (extend `gather_inventory()` per S2499 precedent). **Deferred to post-arc cascade PR.**

- **AU-2 (autoblock refresh cadence)** — Include §API autoblock in existing refresh_doc_inventory_blocks cadence (analog to §Auth precedent).

### 7.2 PLATFORM_WHAT_IT_IS.md

- **AU-3 (CREATE §API narrative subsection)** — Analog to §Auth narrative subsection ADDED at S2499 close. Include: (a) 4-layer permission-floor split with MECHANISM PRIMITIVE FleetCapabilityRequired exemplar note; (b) 4-shape 401 heterogeneity with Family A/B/C/D taxonomy pointer; (c) SHAPE-BLIND interceptor + 803-scale consumer surface pointer; (d) drf-spectacular INSTALLED-not-WIRED status; (e) REST↔WS T7 joint contract-SoT-absent pointer; (f) FleetCapabilityRequired exemplar + Cat B (c) governance greenfield status. **Deferred to post-arc cascade PR.**

### 7.3 ARCHITECTURE_INDEX.md

- **AU-4 (§1.93–§1.97 registrations backfill)** — §1.93 S2501 backfill + §1.94 S2502 backfill + §1.95 S2503 registration + §1.96 S2504 registration + §1.97 S2599 xx99 canonical summary registration. Version bump v88 → v93 across the cascade (5 entries). Deferred from S2501-S2504 close per session-ready check.

- **AU-5 (§8 timeline)** — Add 5 timeline rows for S2501 + S2502 + S2503 + S2504 + S2599 xx99 with Rigby SIGN + fold count.

- **AU-6 (§3 domain map)** — Update API row from PARTIAL (prior at S2499 close) to reflect Group 2500 arc close status. Suggested cell: WORKING mechanism / PARTIAL declaration (design-prep evidence-plane closed).

- **AU-7 (§5 gap entries)** — Close Group 2400 gap markers for CF-B1 (Cat D S2504 owns; now research-CLOSED as design-prep evidence-plane, execution-open per §8 P0-A) + CF-D1 (Cat C S2503 owns; now research-CLOSED as design-prep evidence-plane) + CF-C1/C2/C3 (Cat C S2503 owns; research-CLOSED). Open new Group 2500 gap markers per §8 P0 tiers.

- **AU-8 (§7 decision matrix)** — Add rows for Group 2500 three decision-space quadrants: Quadrant I Path A/B/C + drf-spectacular wire-up; Quadrant II (a)/(b)/(c) + SHAPE-BLIND replacement; Quadrant III α/β/γ session-lifecycle + envelope shape SoT + refresh + CSD + F-C-VIP-1 rubric; Quadrant IV (a)/(b)/(c) permission-floor + typed-error-envelope α/β/γ + whitelist-replacement α/β/γ + T7 Path A/B/C.

- **AU-9 (§9 roadmap)** — Advance T-slot queue with post-arc handoff bundle order: T3 Group 2600 PA (dual-owned CF-2600-PA + CF-D6) → T4 Group 1700 Observability (secondary CF-D6) → T5 Group 2300 Mobile (parallel CF-C4/CF-D6) → T6 Group 1600 Content (CF-C8).

### 7.4 Other affected docs

- **AU-10 (docs/topics/api.md CREATE)** — Analog to `docs/topics/auth.md` CREATED at S2499 close per AU-D2 + AU-D7 fold. Include: (a) 4-plane consolidated shape (this §3); (b) 4-shape 401 Family A/B/C/D taxonomy; (c) 4-layer permission-floor split; (d) FleetCapabilityRequired MECHANISM PRIMITIVE exemplar; (e) SHAPE-BLIND interceptor + 803-scale consumer surface; (f) REST↔WS T7 joint contract-SoT-absent status; (g) Cat D 8-dimension maturity table pointer; (h) Level 0 canonical scope + Level 0-adjacent candidates. **Deferred to post-arc cascade PR.**

- **AU-11 (platform_architecture_inventory.md §3.22 API Layer REVISE)** — Preserve current STABLE + MODERATE overall posture (Cat A F4 verified §3.22 EXISTS at line 1648 not §3.30 TBD). Add sub-layer breakdown reflecting Cat A + Cat B + Cat C + Cat D DECLARATION + CONSUMER + CONTRACT + REGISTRY evidence: DECLARATION sub-layer PARTIAL; CONSUMER sub-layer PARTIAL; CONTRACT sub-layer PARTIAL; REGISTRY sub-layer GREENFIELD.

- **AU-12 (CODEOWNERS partial-scope resolution)** — Backend ~95% assignment resolved at S2502 close (Cat B F7). Frontend 4-of-9 explicit; cockpit surface (cockpitApi.ts + cockpitQueries.ts + apiClient.ts + types/cockpit.ts + useWebSocket.ts) UNASSIGNED per CODEOWNERS lines 8-13 explicit deferral to S2600+. **Deferred to Group 2600 T3 handoff owner.**

- **AU-13 (OPEN_ARCS.md row transition)** — Group 2500 API row: In-progress (5-of-6 shipped) → Closed. Update NEXT column from "S2599 xx99" to "T3 Group 2600 PA queued".

- **AU-14 (`tools/pa_local.sh` header ledger)** — Add S2500 arc retirement stanza pinned to arc pin `pa-a03b111768464b3f` retirement at this xx99 close (TWELFTH formal arc-pin retirement in Research OS). Rotate `tools/pa_local.sh:280` to Group 2600 PA arc-open pin at that arc-open time; do NOT modify at this xx99 close (Group 2600 arc pin not yet minted).

---

## 8. Follow-On Research Queue

Ranked next-mission list. P0 rank-1 co-equal batch preserved per Cat A/B/C/D + S2499 precedent. Tier framings surface blast-radius truth for implementation sequencing, not priority downgrade.

### 8.1 Rank-1 P0 Batch (co-equal per Cat A/B/C/D precedent)

**Blocking vs non-blocking dependency clarification (Rigby xx99 SIGN Q4 STRENGTHEN fold):** AU-U1 (D4 unique-view denominator normalization) is **blocking for ratio-comparison truth + verdict-confidence in Cat B (c) permission-floor governance decisions**, but is **NOT blocking for tactical remediation** in P0-A items (F-D-CALL-1 / F-D-BYPASS-1 / F-D-ENVELOPE-1 / F-D-BOUNDARY-1 can execute against current denominators). SHAPE-BLIND interceptor replacement (F3 attach point) is **blocking for any envelope-shape SoT plan that requires client-side shape discrimination**, but NOT blocking for shape-normalization mechanisms at emission site (Family B canonicalization at DRF `EXCEPTION_HANDLER` override, e.g.). Explicit sequencing dependencies are enumerated per-item where they apply; absence of enumeration means "no blocking dependency identified."

**P0-A platform-wide (S2599 xx99 execution scope owned; Cat D new-owner rows integrated):**

- **AU-U1**: fund route→view normalization pass to compute D4 unique-view denominator. Enables Cat D §1.1 D5 (49% route-indexed) ↔ S2402 §14.5 (~84.4% view-inheritance) direct comparability. Blocks downstream ratio-based verdicts.
- **F-D-CALL-1**: 803-scale silent-401 remediation. Cat D S2504 CLOSED as design-prep evidence-plane; execution deferred to post-arc T-slot. Coupled to Cat D typed-error-envelope α/β/γ verdict + SHAPE-BLIND replacement.
- **F-D-BYPASS-1**: 79-raw-fetch bypass reconciliation. Cat B S2502 evidence handed; Cat D S2504 post-arc T-slot classification preserved. Options (a) migrate per-site / (b) global fetch wrapper / (c) leave-as-is + document — Chris-D-verdict-request.
- **F-D-ENVELOPE-1**: typed-error-envelope. Cat C S2503 CLOSED as design-prep evidence-plane; Cat D S2504 preserves attach-point evidence at api.ts:43-62 SHAPE-BLIND interceptor RE-VERIFIED IDENTICAL. Coupled to α/β/γ verdict.
- **F-D-BOUNDARY-1**: error-boundary framework establishment. Dual-owned Cat D + Group 2200 post-arc T-slot preserved. **BLOCKING PREREQUISITE for Cat D γ mechanism** (Cat C R6 lineage).

**P0-B token lifecycle / security window:**

- **F-D-SIDEBAR-1**: Sidebar backend-token-revoke fix (single-line addition). Cat D S2504 preserves post-arc T-slot ownership.
- **F-C-REFRESH-1**: refresh discipline decision-space execution. Cat C S2503 CLOSED as design-prep; execution COUPLED to R1 α/β/γ verdict.
- **F-C-VIP-1**: VIPInvite.account_expires_at ENFORCEMENT. Cat C S2503 CLOSED with 4-option evidence-candidates + Rigby Q18 rubric (server-authoritative + observable/auditable + compatible with current auth model + safe under partial deploy). Execution locus Chris-D-verdict at xx99 OR post-arc dedicated ADR.
- **F-C-CSD-1**: Clear-Site-Data emission on logout. Cat C S2503 CLOSED as design-prep evidence-plane; 3 candidate loci enumerated (per-endpoint header / middleware / envelope helper). Header value spec deferred (U4 unknown).
- **F-C-STORE-1**: 15-surface × logout-cleanup declared contract execution. Cat C S2503 CLOSED as design-prep evidence-plane; execution dual-owned Cat C + Group 2200 post-arc + Group 2600 PA.

**P0-C endpoint-specific:**

- **F-CRIT-1**: PURGE_SECRET hardcoded fallback remediation. Group 2400 backlog preserved.
- **F-BND-4a**: Unauthenticated bet-placement WRITE remediation. Group 2400 backlog preserved.
- **F-B-CRIT-1**: Permission-floor implicit-inheritance ~80-90%. Cat D S2504 CLOSED as design-prep evidence-plane. D4 unique-view denominator UNKNOWN (U1); xx99 decision candidate: fund route→view normalization pass (AU-U1).
- **F-B-CRIT-2**: Silent-401 SYSTEMIC. Cat C S2503 CLOSED + Cat D S2504 execution owner preserved.
- **F-D-WHITELIST-1**: Whitelist replacement. Cat D S2504 CLOSED as design-prep evidence-plane. Rigby Q7 fold `authHandling: 'default' | 'suppress_redirect'` string enum + telemetry PROPOSED PRIMARY γ preserved.
- **F-D-REGISTRY-1 NEW**: Per-endpoint permission-floor registry. Cat D S2504 CLOSED as design-prep evidence-plane; xx99 Chris-D-verdict-request on Cat B (c) scope selection.
- **F-D-WSENVELOPE-1 NEW**: WS message-contract SoT. Cat D S2504 CLOSED as design-prep evidence-plane; xx99 Chris-D-verdict-request on T7 Path A/B/C strictness selection.
- **F-D-4LAYERSPLIT-1 NEW**: Permission-floor 4-layer split cross-layer SoT. Cat D S2504 CLOSED as design-prep evidence-plane; execution CONTINGENT on registry verdict.

### 8.2 Rank-2 T-Slot Follow-On Queue (post-Group-2500-close forward look)

- **T3 Group 2600 PA cross-arc handoff bundle** — QUEUED. CF-2600-PA + CF-D6 REST↔WS T7 joint dual-owner status. Consumes: 4 CF-* originated S2501-S2504 + PA endpoint DECLARATION + workspace-context authz.
- **T4 Group 1700 Observability cross-arc handoff bundle** — QUEUED after Group 2600 close. Extended CF-D6 secondary stakeholder from Q9 fold. Consumes: 161 direct 401 emission telemetry + shape-normalization observability + envelope-enforcement locus.
- **T5 Group 2300 Mobile (parallel)** — CF-D4 + CF-C4 + Cat A CF-4 + Cat D CF-D6 secondary stakeholder. Parallel silent-401 audit + typed-client parallel consumer surface + mobile-token revocation on logout.
- **T6 Group 1600 Content (per Cat C S2503 Rigby SIGN Q11 fold CF-C8)** — Content/Publishing surfaces call auth-protected endpoints; envelope-shape variability leaks into editor/publisher UX.
- **Maintainer-decision batch** — CODEOWNERS API-slice discipline + DEAD-CANDIDATE consolidated cleanup (18 modules verified zero-consumer at S2502) + api.ts extraction execution + storageKeys registry + basic vs enhanced logout consolidation (F-C-DUP-1 same-issue lineage + Cat C F6 key-name divergence) + STAFF_REQUIRED_PATHS 2-of-3 phantom cleanup + `@authentication_classes([])` 3-file × 6-site stacking cleanup (F-B-HIGH-4 CRITICAL-per-site for auth_views_enhanced.py:560).
- **CODEOWNERS cockpit refinement** — cockpitApi.ts + hooks/cockpitQueries.ts + apiClient.ts + types/cockpit.ts + useWebSocket.ts ownership assignment deferred to S2600+ per CODEOWNERS lines 8-13.

### 8.3 Rank-3 Post-arc ADR candidates (deferred from parked list)

- **P-5 Typed-client codegen framework decision** (openapi-typescript / orval / kubb) — feasibility-only at Group 2500; framework choice deferred to post-arc ADR OR Group 2500 code-arc T-slot if drf-spectacular Path A ratified at xx99.
- **P-6 WebSocket protocol / channel redesign** — Explicitly OUT-OF-SCOPE at REST↔WS T7 joint per anti-scope #8; deferred to targeted post-arc ADR if load-bearing.
- **P-9 Discord bot API surface** (48 slash + 48 prefix + 25 Cog classes) — Adjacent domain; NON-CANDIDATE at Group 2500. Candidate for targeted post-arc research if Discord contract discipline becomes load-bearing.
- **P-10 Rate limiting per endpoint** — In-scope at Cat D permission-floor per §3.5 disposition (inventoried as declared-vs-undeclared per endpoint). If load-bearing at ratification, spawn targeted rate-limit ADR post-arc.
- **P-11 Pagination contract discipline** — In-scope at Cat A contract SoT per §3.5 disposition. If load-bearing at xx99 ratification, spawn pagination ADR post-arc.

---

## 9. Cross-Links to Delegated Arcs

Every `delegates_to:` entry from the parent scoping (§9 Integrations) gets a pointer here for future readers. Also included: cross-arc CF-* flags propagated from S2501-S2504 + S2499 lineage.

| Delegated arc | Handoff | Owner arc | Provenance |
|---|---|---|---|
| Group 2600 PA (T3) | REST↔WS T7 joint contract SoT dual-owner + PA endpoint DECLARATION (`/api/pa/chat/` + `/api/assistant/*` zero `@extend_schema`) + workspace-context authz | Cat A CF-2600-PA (S2501) + Cat D CF-D6 (S2504) | Cat A §9 + Cat D §9 |
| Group 1700 Observability (T4) | 161 direct 401 emission telemetry + shape-normalization observability + envelope-enforcement locus | Cat A CF-1700-Obs (S2501) + Cat C CF-C3 (S2503) + Cat D CF-D6 secondary stakeholder (S2504) | Cat A §9 + Cat C §9 + Cat D §9 |
| Group 2300 Mobile (T5) | Backend contract SoT (once generated) would serve mobile + web identically + parallel silent-401 audit + mobile-token revocation on logout | Cat A CF-2300-Mobile (S2501) + Cat C CF-C4 (S2503) + Cat D CF-D6 secondary stakeholder (S2504) + Cat A CF-4 preserved | Cat A §9 + Cat C §9 + Cat D §9 |
| Group 1600 Content (T6) | Content/Publishing surfaces call auth-protected endpoints; envelope-shape variability leaks into editor/publisher UX | Cat C CF-C8 NEW (S2503) | Cat C §9 (Rigby Q11 STRENGTHEN fold) |
| Group 1500 Sports (conditional) | Sole platform-wide `@extend_schema` demonstration (16 decorators + ~25 money-path Serializer classes); INERT at HEAD due to drf-spectacular disconnect; live integration dependency for Path A/B/C retrofit if ratified | Cat A CF-1500-Sports (S2501; Rigby Q9 fold promoted implicit → explicit) | Cat A §9 |
| Group 1300 Memory (conditional) | REST-endpoint vs tool-only disposition; adjacency preserved, disposition-pending | Cat A CF-implicit (S2501) | Cat A §9 |
| Group 2000+ Events/Celery (conditional) | REST endpoints returning task_id/status; distinct contract-SoT concerns (task envelope + async-failure error + async-submission permission); count not enumerated at S2501 | Cat A CF-implicit (S2501) | Cat A §9 |
| Group 1900 Authority Enforcement (boundary preserved) | GovernanceState / KillSwitch NOT invoked in logout paths (0 matches); boundary preserved | Cat C CF-C7 (S2503) | Cat C §9 |
| Group 2200 Frontend post-arc T-slot | 15-surface storageKeys cleanup contract + R6 error-boundary framework prerequisite (dual-owned Cat D + Group 2200) | Cat C CF-C5 (S2503) + Cat D F-D-BOUNDARY-1 (S2504) | Cat C §9 + Cat D §14 |

---

## 10. What This Research Taught Us About How to Do Research

Meta-methodology retrospective. Per playbook §11.3 §10 template (adopted S1399 close 2026-07-01 per Chris directive) — this is the **TWELFTH-consecutive application** of the §10 5-subsection template after S1399 / S1499 / S1599 / S1699 / S1799 / S1899 / S1999 / S2099 / S2199 / S2299 / S2499 eleven prior. Non-negotiable for every xx99 canonical summary.

### 10.1 What worked (methodology validated across this arc)

- **Boundary discipline preservation across all four children (§4.5).** No child prescribed a verdict; each stayed in EVIDENCE + INVENTORY + OPTION-SPACE ENUMERATION mode. This makes xx99 the FIRST point where option-space consolidates — and it lets Chris ratification card at close carry the actual verdict weight instead of the discipline being distributed across 4 audit closes.
- **Same-issue-lineage cross-reference discipline** (heir of S2499 §4.3). F-D-CALL-1 ↔ F-D-BYPASS-1 ↔ F-D-ENVELOPE-1 ↔ F-D-BOUNDARY-1 preserved from S2404 → S2504; F-C-VIP-1 preserved cross-section instead of merged into a single "VIP" finding. Preserving per-arc framings of the same underlying issue keeps each child's analytic lens visible.
- **Dedicated fresh SIGN pin per child** (playbook §15 SIGN-isolation discipline). Cat A + Cat B + Cat C + Cat D + xx99 = 5 fresh SIGN pins across the arc; TWENTY-FIRST + TWENTY-SECOND consecutive dedicated fresh SIGN pin retirements at S2504 close + this xx99 close. Pin-poisoning at Rigby's LLM boundary (per `feedback_rigby_sign_worker_instability_recovery.md`) has NOT occurred at any child close under this discipline.
- **Arc pin preservation through 6 sessions** (`pa-a03b111768464b3f` from S2500 → S2599 xx99). TWELFTH formal arc-pin retirement at this xx99 close; SIXTH-consecutive parent-with-4-children arc (extends MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails).
- **Chris shape-card Q1 P4-retitle at S2500 open** PREVENTED P4 from reading as "auth cleanup PR" (F-B-HIGH-1 STAFF_REQUIRED_PATHS + F-B-HIGH-4 stacking cleanup moved to findings-appendix per Rigby SIGN-preview Q1 fold). This is a template-level discipline: framing-drift mitigation at PARENT scoping saves child-audit re-scoping later.
- **§16 Level 0-adjacent candidates framing** (Cat D added 2 without redefining Cat C anchor). This preserved Cat C's canonical 3-domain Level 0 scope (error envelope + refresh + logout) while allowing Cat D to record permission-floor semantics + REST↔WS message-contract strictness as "Level 0-adjacent candidates for xx99 consolidation" — anchor stability preserved AND downstream extensibility named.
- **§1.1 Denominator Contract D1-D6** (Cat D Rigby Q2 STRENGTHEN fold). When two arcs compute ratios against different denominators (49% route-indexed vs ~84.4% view-inheritance), an explicit denominator contract prevents future misread. This pattern is directly reusable.

### 10.2 What to codify into playbook v3 (per §20 two-triggers rule)

- **§11.3 §10 meta-methodology TWELFTH-consecutive application** — stable pattern; adopted S1399 close 2026-07-01; no arc has skipped it. Consider promoting from "adopted 2026-07-01 per Chris directive" to unconditional playbook §11.3 §10 requirement in v3.
- **§16 Level 0-adjacent candidates framing pattern** — CODIFICATION CANDIDATE. Trigger #1 = Cat D S2504 introduced (added 2 adjacent candidates for xx99 consolidation without redefining Cat C anchor). Second trigger PENDING (needs one more arc application). Draft template addition: extend §11.3 §7 anchor-update template with "adjacent candidates for future arc consolidation" sub-slot. Watch for trigger #2 at S2699 xx99 or S2799 xx99.
- **§1.1 Denominator Contract discipline (D1-D6 pattern)** — CODIFICATION CANDIDATE. Trigger #1 = Cat D S2504 introduced (838/1,856 route-indexed vs S2402 ~84.4% view-inheritance denominators). Second trigger PENDING. Draft template addition: prescribe denominator-contract sub-section at child-scoping when count-comparisons are load-bearing.
- **Preemptive SIGN batching at 20-Q child audits** (per `feedback_rigby_sign_worker_instability_recovery.md`). Confirmed working across S2201-S2504 twelve-consecutive tested pattern (4-batch × 5-Q cadence THIRTEENTH-consecutive at S2504). No worker-instability jam recorded at any child close. Consider promoting from feedback memory to playbook §15 formal cadence.
- **5-parallel Explore sub-agent extract discipline for xx99 canonical summaries.** Trigger #1 = this xx99 (5 Explore agents in parallel — Cat A + Cat B + Cat C + Cat D + S2499 exemplar — extract reports; parent-Claude verifier-loop reconciled). Preserves context budget on ~10k-line predecessor read; produces structured extract reports; parent-Claude synthesizes. Cost: sub-agent count consumes token budget. Second trigger PENDING; consider watching S2699+ xx99 for repeat.

### 10.3 What didn't work / anti-patterns to avoid

- **Framing-drift risk without explicit shape-card Q1 P4-retitle mitigation.** Had Chris not ratified the Q1 P4-retitle at S2500 open, P4 could have read as "auth hardening PR" — S2504 would have drifted toward remediation-verdict framing rather than DESIGN-PREP evidence-plane framing. General lesson: framing risk at parent scoping is CHEAPER to mitigate than at child close.
- **Metric-denominator drift when comparing across-arc ratios** (§5.2 canonical verdict). S2402 ~84.4% implicit-inheritance and Cat D 49% route-indexed appear to be comparable percentages of the same phenomenon; they are NOT. Without §1.1 D1-D6 denominator contract, future readers could misread the -35.4pp delta as "coverage regression" when it is a DIFFERENT DENOMINATOR. The lesson: any ratio-comparison across arcs requires explicit denominator naming.
- **F-* labeling ambiguity across arcs** (§5.4). F-B-HIGH-2 exists as a S2402 finding but was referenced in Cat D S2504 F-D-BOUNDARY-1 evidence — Cat B S2502 extract report correctly said "NOT FOUND in this audit" (Cat B did not define F-B-HIGH-2). Downstream consolidation must attribute-to-origin arc; F-* codes are NOT globally unique across arcs. **Anti-pattern:** treating F-* codes as globally interpretable. **Correction:** always cite the origin arc when quoting an F-* code from a different arc.

### 10.4 Suggestions for the playbook itself

- **Add §11.3 §7 Level-0-adjacent-candidates sub-slot** — when an xx99 canonical summary is preceded by a downstream child that adds "Level 0-adjacent candidates for future consolidation," provide a template slot for that framing to survive into anchor-update recommendations.
- **Add §11.3 §1.1 Denominator Contract sub-slot** — when arc introduces new metric surfaces with denominators potentially conflicting with prior-arc metrics, prescribe explicit D1..Dn contract at child-scoping.
- **Codify F-* origin-arc citation discipline** — extend §14 evidence rules with "F-* codes are per-arc scoped; always cite origin arc when referencing F-* codes from another arc's audit." (Prevents §5.4-style ambiguity.)
- **Codify 5-parallel Explore sub-agent extract discipline for xx99** — extend §11.3 with optional "sub-agent extract reports as consumption mechanism" note; xx99 does NOT launch new evidence sweeps but may delegate predecessor reads for context-budget preservation, with parent-Claude verifier-loop applied to extract reports.
- **Codify TWELFTH-consecutive §10 meta-methodology adoption** — v3 draft note: "Adopted S1399 close 2026-07-01 per Chris directive. Twelve consecutive applications S1399-S2599 without exception. Non-negotiable for every xx99 canonical summary."

### 10.5 Suggestions for future canonical summaries (optional)

- **Adopt §3.1 numerical summary consolidated table pattern** (S2499 precedent + refined here to 30+ rows). Scannable single reference for all children's numbers; used in xx99 §3 to give a fresh reader the whole arc's numerical picture without reading 4 audits.
- **Adopt §5 canonical-verdict phrasing** ("Canonical verdict:" prefix + rationale + attribution). S2499 pattern; used here §5.1-§5.5. Enables future readers to cite contradiction resolutions unambiguously.
- **Adopt §8.1 P0-A/P0-B/P0-C tier framing pattern** (S2499 precedent + refined here to integrate Cat D new-owner rows). Blast-radius-truth tier framing surfaces implementation-sequencing lens without downgrading finding priority.
- **Adopt §9 delegated-arcs table with provenance** (S2499 precedent + refined here to include (conditional) rows for optional adjacencies). Every CF-* + delegates_to entry from the parent gets a pointer.

---

## 11. Arc Change Log

Chronological ledger of which children shipped, in what order, with Rigby verdict + fold count + arc-pin state. Format: Session / Child / Date / Rigby verdict / Fold count / Confidence / SIGN pin (retired at cycle close) / Distinguishing property.

| Session | Child | Date | Rigby verdict | Folds | Confidence | SIGN pin | Distinguishing property |
|---|---|---|---|---|---|---|---|
| S2500 | Parent scoping (`2500_api_domain_scoping.md`) | 2026-07-05 | SIGN-preview SIGN-with-edits (light SIGN cadence per §15 parent tier) | 4 (Q1 P4-retitle + Q2 lens-clause + Q3 AC-clauses + Q4 anti-scope +7 +8) | HIGH | pa-preview (SIGN-preview via arc pin) | Chris "agree all" ratified all 4 pre-Rigby-SIGN items; MC-4 SIXTH-consecutive candidate |
| S2501 | Cat A Backend Contract SoT (`2501_api_backend_contract_sot_design_prep_audit.md`) | 2026-07-05 | SIGN-with-edits Cycle 1 (Cycle 2 NOT required) | 18 across 4 batches (Q7 STRENGTHEN discovered 4th shape family — parent-Claude verifier-loop gap probe) | HIGH | fresh SIGN pin (retired at cycle close) | 4-shape 401 discovery v0 → v1 expansion via parent-Claude verifier-loop pre-SIGN |
| S2502 | Cat B Frontend API-Client (`2502_api_frontend_client_architecture_design_prep_audit.md`) | 2026-07-05 | SIGN-with-edits Cycle 1 (Cycle 2 NOT required) | 20 (5 AGREE + 14 STRENGTHEN + 1 combined verdict-format response); 4-conflict verifier-loop resolution pre-Rigby-SIGN | HIGH | fresh SIGN pin (retired at cycle close) | 6-parallel Explore sub-agent sweep + parent-Claude verifier-loop resolving 4 sub-agent conflicts pre-Rigby-SIGN |
| S2503 | Cat C Error/Refresh/Logout Contracts (`2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md`) | 2026-07-05 | SIGN-with-edits Cycle 1 (Cycle 2 NOT required) | 20 (1 AGREE + 18 STRENGTHEN + 1 Q20 combined verdict-format); ~0.86 confidence | HIGH | fresh SIGN pin (retired at cycle close) | Level 0 anchor DECLARED (3 domains: error envelope + refresh + logout); §9.1 α/β/γ intersection model + established nesting (Cat D γ ⊃ Cat C β); F6 basic-vs-enhanced key drift NEW |
| S2504 | Cat D Permission-Floor Registry + REST↔WS T7 Joint (`2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md`) | 2026-07-06 | SIGN-with-edits Cycle 1 (Cycle 2 NOT required) | 20 (10 AGREE + 10 STRENGTHEN); 15-25 fold S2201-S2503 empirical baseline preserved | HIGH | pa-1aad569644364682 (retired at cycle close; 21st consecutive dedicated fresh SIGN pin retirement) | 8-dimension maturity table + FleetCapabilityRequired MECHANISM PRIMITIVE exemplar + §1.1 D1-D6 Denominator Contract + Level 0-adjacent candidates framing NEW |
| S2599 | xx99 Canonical Summary (this doc) | 2026-07-06 | SIGN-with-edits Cycle 1 (Cycle 2 NOT required); single-batch × 4-Q cadence per S1399-S2499 eleven-consecutive tested pattern TWELFTH-consecutive application | 5 (1 Q1 STRENGTHEN §5.2 route-indexed vs coverage-rate clarifier + 1 Q2 AGREE-optional §7.1 AU-1 name D1-D6 explicitly + 1 Q3 STRENGTHEN §4.2 end-to-end pipeline sentence + 1 Q4 STRENGTHEN §8.1 blocking-vs-non-blocking dependency clarification + 1 understated-maturity STRENGTHEN §3.1 WS auth-middleware uniformity row) | HIGH | pa-59d9583dc4da4d5e (retired at cycle 1 close; 22nd consecutive dedicated fresh SIGN pin retirement in Research OS) | Group 2500 API arc CLOSED at this xx99; TWELFTH formal arc-pin retirement (`pa-a03b111768464b3f`); Rigby confidence HIGH; verdict "SIGN-with-edits; two small wording/clarity edits; no new evidence sweeps needed" |

**Arc totals:** 6 sessions (S2500 parent + S2501-S2504 children + S2599 xx99) matching runtime target 6 sessions per §5. Approx 78 folds pre-ratification across S2500-S2504 (4 + 18 + 20 + 20 + 20 including S2504 folds); Chris "commit it" ratifications wholesale at S2500 + S2501 + S2502 + S2503 + S2504 close. **6 SIGN pins retired at arc close** (pa-preview + 5 dedicated fresh isolation pins). Arc pin `pa-a03b111768464b3f` preserved through all 6 sessions and retires at this xx99 close (TWELFTH formal arc-pin retirement).

---

## 12. Appendix — Provenance

### 12.1 Files inspected (HEAD-verified at `adf902a0`)

- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §10 (canonical summary responsibilities) + §11.3 (12-section template) + §11.3 §10 (5-subsection meta-methodology template) + §14 (evidence rules) + §15 (SIGN cadence + Q10-Q13 xx99 add-on questions) + §16 (draft-first workflow + arc pin retirement discipline)
- `docs/research/domains/api/2500_api_domain_scoping.md` §3 (candidate subdomain taxonomy) + §5 (child mission sequence Chris-locked 2026-07-05) + §6 (P-1 through P-11 parked items) + §7 (anti-scope) + §8 (Chris decisions) + §9 (next-step)
- `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md` §1 executive summary + §5.5 pattern-analogy + §14.1-14.6 findings F1-F6 + §16 Level 0 explicit non-declaration + §19 R1-R7 + §20 provenance
- `docs/research/domains/api/2502_api_frontend_client_architecture_design_prep_audit.md` §1 executive summary + §14 F1-F8 findings + §16 explicit non-declaration + §19 R1-R10 + §20.6.2 20-fold ledger
- `docs/research/domains/api/2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md` §1 executive summary + §9.1 α/β/γ intersection model + §14 F1-F8 findings + §16 Level 0 anchor DECLARED (3 domains) + §19 R1-R11 + §20 SIGN cycle 1 fold record (20 folds)
- `docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md` §1 executive summary + §1.1 D1-D6 Denominator Contract + §5.5 FleetCapabilityRequired MECHANISM PRIMITIVE exemplar + §9.1 4-independent decision-spaces model + ONE established nesting + §13 8-dimension maturity table + §14 F-D-* findings + §16 Level 0-adjacent candidates + §19 R1-R11 + §20 SIGN cycle 1 fold record (20 folds)
- `docs/research/domains/auth/2499_auth_canonical_summary.md` (prior arc-close model per playbook §11.3; structural template for §1-§12 authoring)
- `platform_architecture_inventory.md:1648` §3.22 API Layer row (STABLE + MODERATE current posture)
- `docs/PLATFORM_INVENTORY.md` (autoblock refresh source — regenerate via `refresh_doc_inventory_blocks`)
- `docs/PLATFORM_WHAT_IT_IS.md` (narrative anchor)
- `./CODEOWNERS` lines 8-13 (explicit deferral) + line 31 (`/frontend/src/lib/api.ts @clwest`)

### 12.2 Grep patterns re-executed (spot-check for xx99 canonical summary verification)

- Cat A F1 SoT-ABSENT: `grep -n 'drf_spectacular' core/settings.py:161-215` → NOT PRESENT in INSTALLED_APPS at HEAD (verifier confirmed).
- Cat A F5 partial-wiring: `python manage.py spectacular --file schema.yaml` → command NOT RECOGNIZED at HEAD (verifier confirmed).
- Cat A F6 shape (d) non-DRF JsonResponse: `grep -rn 'JsonResponse.*success.*false' core/views_deploy.py core/views_video.py` → 93-count preserved.
- Cat B F1 api.ts: `wc -l frontend/src/lib/api.ts` → 4,194 LOC preserved.
- Cat B F3 SHAPE-BLIND interceptor: verified `frontend/src/lib/api.ts:43-62` — response interceptor reads `error.response?.status === 401` + `url.includes('/auth/')` substring only.
- Cat C F3 refresh absent: `grep -rn 'refresh' core/urls.py core/auth_views*.py` → 0 auth-adjacent refresh route matches preserved.
- Cat C F4 CSD zero: `grep -rn 'Clear-Site-Data' core/auth_views*.py` → 0 production emission preserved.
- Cat D §1.1 D5 838-count: `grep -rn '@permission_classes' core/ | wc -l` → 838 explicit sites preserved.
- Cat D §14.3 285-entry path-list: `grep -c PUBLIC_PATHS core/auth_middleware.py:94-561` → 265 PUBLIC entries preserved (+ 20 STAFF/REVIEWER = 285 total).
- Cat D FleetCapabilityRequired exemplar: `grep -n 'def for_capability' core/services/fleet_auth_drf.py:215-263` preserved.

### 12.3 Rigby SIGN cycle 1 record

- **Cycle:** 1
- **Cadence:** single-batch × 4-Q per S1399 / S1499 / S1599 / S1699 / S1799 / S1899 / S1999 / S2099 / S2199 / S2299 / S2499 eleven-consecutive tested pattern (TWELFTH-consecutive application)
- **Fresh SIGN isolation pin:** `pa-59d9583dc4da4d5e` (retirement at cycle 1 close via `session_tool.retire force=true` — TWENTY-SECOND consecutive dedicated fresh SIGN pin retirement candidate in Research OS)
- **Rigby SIGN questions (xx99-specific per playbook §15 add-on Q10-Q13):**
  1. Did Claude miss any major parts of the arc's synthesis?
  2. Did Claude resolve the child contradictions correctly (§5)?
  3. Are the anchor-update recommendations complete (§7)?
  4. Are the follow-on queue rankings defensible (§8)?
- **Rigby verdict:** SIGN-with-edits Cycle 1 (Cycle 2 NOT required). Overall confidence HIGH. Most accurate part: "§4 + §5 synthesis discipline; preserved the arc's two core 'don't misread' constraints — denominator non-comparability and taxonomy reconciliation." Weakest part: "§8 P0 queue defensibility phrasing around AU-U1 (D4 normalization); ranking defensible but text risked implying AU-U1 is blocking all downstream execution when it's primarily blocking ratio-comparison truth." Missing area: "one explicit 'non-blocking vs blocking dependencies' line in §8.1." Overstated maturity: none major. Understated maturity: WS uniformly auth-wrapped at middleware even though envelope/contract SoT is greenfield. Biggest architectural risk: "coupled breaking-change wedge — SHAPE-BLIND + envelope-strictness silent-401 amplification." Most important next research: "route→view normalization (AU-U1 / D4) only insofar as needed for a single authoritative explicitness metric to govern policy." What Claude got wrong: "nothing material in the four asked dimensions; doc is structurally sound; remaining issues are phrasing-level guardrails." What must change before canonical: "two small wording/clarity edits (folded)." Final verdict: SIGN-with-edits.
- **Fold ledger:** 5 folds landed pre-Chris-ratification:
  | Fold | Q ref | Section | Summary |
  |---|---|---|---|
  | Fold 1 | Q1 STRENGTHEN | §3.1 numerical summary + §5.2 canonical verdict | Added "49% is a route-indexed decoration-site density, NOT an explicit-permission coverage rate" clarifier at both §3.1 denominator contract paragraph and §5.2 route-indexed-vs-view-inheritance verdict — prevents quote-mining of the 49% figure as if it were coverage rate. |
  | Fold 2 | Q2 AGREE-optional | §7.1 AU-1 | Explicitly named "Cat D §1.1 Denominator Contract D1-D6" in AU-1 PLATFORM_INVENTORY §API autoblock CREATE spec, with per-D denominator enumeration. Prevents downstream autoblock generator from omitting the denominator contract. |
  | Fold 3 | Q3 STRENGTHEN | §4.2 SHAPE-BLIND consumer surface | Added end-to-end pattern sentence: "4-shape 401 heterogeneity at Cat A (emission side) → SHAPE-BLIND interceptor at Cat B (attach point) → 803-scale consumer flow-through at Cat D (propagation) = one end-to-end pipeline." Preserves the pipeline framing across the pattern boundary. |
  | Fold 4 | Q4 STRENGTHEN | §8.1 preamble | Added blocking-vs-non-blocking dependency clarification: AU-U1 blocks ratio-comparison truth + Cat B (c) verdict-confidence but NOT tactical P0-A execution; SHAPE-BLIND replacement blocks any envelope plan requiring client-side discrimination but NOT emission-side normalization. Explicit sequencing dependencies enumerated per-item where they apply. |
  | Fold 5 | Understated-maturity STRENGTHEN | §3.1 numerical summary | Added row "Backend WS auth-middleware uniformity: Consumers routed through TokenAuthMiddlewareStack = 100%" — acknowledges MECHANISM works uniformly at middleware layer even though envelope/contract SoT is greenfield. Preserves the WORKING-mechanism / GREENFIELD-declaration distinction. |
- **Verifier-loop history:** parent-Claude single-doc synthesis via 5 parallel Explore sub-agent extract reports (Cat A + Cat B + Cat C + Cat D + S2499 exemplar), then verifier-loop reconciliation applied for (a) F-* code cross-references, (b) count reconciliation between Cat A F2 (1,873) vs Cat D §1.1 D1 (1,856) vs PLATFORM_INVENTORY (1,864), (c) F-B-HIGH-2 attribution-to-origin ambiguity (§5.4), (d) 401 shape family taxonomy Cat A (a)/(b)/(c)/(d) vs Cat C Family A/B/C/D (§5.3), (e) route-indexed vs view-inheritance denominator conflict (§5.2). No new evidence sweeps launched per playbook §11.3. Parent-Claude spot-check verifier loop against HEAD `adf902a0` re-verified: api.ts LOC = 4,194 ✓, interceptor lines 43-62 SHAPE-BLIND signature ✓, `core/services/fleet_auth_drf.py:215-263` FleetCapabilityRequired class scope ✓, `core/settings.py:652` DEFAULT_PERMISSION_CLASSES ✓, PLATFORM_INVENTORY URL count 1,864 ✓.

### 12.4 Arc pin retirement note

`pa-a03b111768464b3f` scheduled for retirement at this xx99 close via `session_tool.retire force=true` — **TWELFTH formal arc-pin retirement in Research OS** after S1399 / S1499 / S1599 / S1699 / S1799 / S1899 / S1999 / S2099 / S2199 / S2299 / S2499 eleven prior. Retire post-Chris-ratification. Downstream `tools/pa_local.sh:280` rotation to Group 2600 PA arc-open pin deferred until Group 2600 arc-open (Group 2600 pin not yet minted).

### 12.5 Meta-methodology continuity

- **§11.3 §10 meta-methodology TWELFTH-consecutive application** (adopted S1399 close 2026-07-01 per Chris directive; unbroken S1399 → S2599). Codification candidate per §10.2 promotion to v3 unconditional requirement.
- **MC-4 SIXTH-consecutive parent-with-4-children arc close** (Groups 1900 + 2000+ + 2100 + 2200 + 2400 + 2500).
- **MC-14 THIRD arc application** (per S2500 §4 verification: Groups 2100 + 2200 + 2500 candidate applications) — CODIFICATION EXTENDS.
- **4-batch × 5-Q child SIGN cadence THIRTEENTH-consecutive application** (S2201-S2504 twelve prior + this arc's 4 children = 13 total; consecutive at Cat D S2504 close).
- **single-batch × 4-Q xx99 SIGN cadence TWELFTH-consecutive application** (S1399-S2499 eleven prior; this xx99 = 12th).
- **Dedicated fresh SIGN isolation pin discipline TWENTY-SECOND consecutive retirement candidate** at this xx99 close.

### 12.6 HEAD provenance

- **HEAD at draft time:** `adf902a0` (S2504 P4 Cat D merge PR #2927 close 2026-07-06).
- **Head branch:** `main`.
- **Git status at draft time:** clean tree (only `.claude/scratch/` untracked).
- **PLATFORM_INVENTORY.md Git HEAD:** `e617af59` (2026-07-05) — 1,864 URL Routes + 209 core/views*.py + 199 mgmt commands + 83 agents + 80 spiders + 112 Service classes + 415 Celery tasks + 92+5 PeriodicTask + 113 PA schemas + 156 PA handlers + 585 concrete models + 96 Discord decorators + 6 LLM providers + 9 body systems + 61 frontend routes.

**Rigby SIGN cycle 1 on completed draft: PENDING** via dedicated fresh isolation pin `pa-59d9583dc4da4d5e`.

**Chris "commit it" ratification: PENDING** post-SIGN fold. Status `draft` → `active` on ratification per playbook §16 draft-first workflow.

**Arc pin preservation:** `pa-a03b111768464b3f` ACTIVE through S2599 xx99 open (retirement at Chris ratification close per playbook §16 arc-standard behavior — TWELFTH formal arc pin, SIXTH-consecutive 4-child arc close).
