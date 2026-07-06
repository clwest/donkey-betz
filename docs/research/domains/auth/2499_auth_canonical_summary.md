---
title: "Group 2400 Auth — Canonical Summary (S2499 xx99 arc close)"
status: active
authority: research
version: v1
session_added: 2499
last_verified: 2026-07-05
domain_slug: auth
research_group: 2400
child_slot: xx99
companion_anchors:
  - CLAUDE.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
  - docs/research/domains/auth/2400_auth_domain_scoping.md
  - docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md
  - docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md
  - docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md
  - docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md
related:
  - docs/research/domains/frontend/2299_frontend_canonical_summary.md   # Group 2200 T1 handoff
  - docs/research/platform_architecture_inventory.md                    # §3.27 baseline
delegates_to:
  - Group 2500 API (T2 arc after Group 2400 close)
  - Group 2600 PA (T3 arc after Group 2500 close)
  - Group 1700 Observability (T4 umbrella roll-up)
  - Group 2300 Mobile (parallel auth audit)
head_commit_before: 4e6c1ee8
head_commit_after: TBD (S2499 merge PR TBD)
arc_pin: pa-6279ead1714c4630 (RETIREMENT-AT-CLOSE per playbook §16 arc-close discipline)
sign_pin: TBD (fresh isolation pin minted at Rigby SIGN cycle 1 open)
verifier_loop: |
  xx99 canonical summaries do NOT spawn sub-agents per playbook §11.3
  note; single-doc synthesis by parent Claude. Load-bearing inputs
  consumed: S2400 parent scoping (§5 acceptance criteria + §7
  anti-scope) + Cat A (S2401) + Cat B (S2402) + Cat C (S2403) + Cat
  D (S2404) child audit docs at HEAD 4e6c1ee8. Consolidation
  discipline: dedupe findings by same-issue-lineage (F-VIP-1 ↔ F-C-VIP-1
  + F-TOKEN-1 ↔ F-C-REFRESH-1 + F-DUP-2 ↔ F-C-DUP-3 preserved from
  Cat C Q16a fold discipline — NOT merged; provenance preserved).
  Cross-arc coordination flag roll-up per Cat C Q11 fold: CF-A/B/C/D
  → observability umbrella roll-up to Group 1700 single tracking unit.

  Rigby SIGN routing: MANDATORY per playbook §15 stage-scoped
  routing (canonical summary = required light SIGN via dedicated
  fresh isolation pin). Expected cadence: single-batch × 4-Q per
  S1399-S2299 TEN-consecutive tested pattern — ELEVENTH-consecutive
  same-cadence application candidate at canonical-summary stage.

  This session marks MC-4 dial-back-resolution 5th confirming arc
  RESOLUTION (Group 2400 Auth 4-child structure completes MC-4
  CODIFICATION-CONFIRMED-with-scope-guardrails across-5-consecutive-arcs:
  1900 + 2000+ + 2100 + 2200 + 2400 — resolving S2199 Q3 STRENGTHEN
  dial-back). Auth was materially different in scope (full auth stack,
  not a single UI surface family) — 5th-arc extension IS a validated
  stress test per S2299 canonical summary §5.3 formulation.
owner: claude (S2499 xx99 draft; Rigby SIGN cycle 1 pending)
---

# Group 2400 Auth — Canonical Summary (S2499 xx99 arc close)

> **What this doc is for.** Group 2400 Auth arc closes here. This
> canonical summary consolidates Cat A (Authentication Surface +
> Trust Boundaries, S2401) + Cat B (Authorization + Permission-Floor
> Uniformity, S2402) + Cat C (Session Lifecycle + Logout Cleanup
> Contract, S2403) + Cat D (Frontend Integration + Silent-401
> SYSTEMIC Resolution, S2404). Delivers Chris D-verdict inputs on
> three decision spaces (Cat B a/b/c + Cat C α/β/γ + Cat D α/β/γ ×
> 2), rolls up 26 cross-arc coordination flags, applies the ELEVENTH
> §11.3 §10 meta-methodology retrospective, and retires the arc pin.
>
> **Anti-scope preserved.** This summary does NOT: (a) author any
> ADR (session-model, per-endpoint permission registry, typed-error
> envelope, whitelist replacement); (b) fix any finding (all
> graduate to T-slot post-arc queue); (c) extend into MFA/OAuth/SSO
> framework additions (Anti-scope #6 preserved); (d) extend into
> mobile app auth (Anti-scope #4 preserved, Group 2300); (e)
> re-scope beyond what the four children delivered. xx99 is
> consolidation + Chris D-verdict + roll-up + close, not new
> authoring.

---

## 1. Executive Summary

Group 2400 Auth shipped four child audits — Cat A Authentication
Surface + Trust Boundaries (S2401), Cat B Authorization +
Permission-Floor Uniformity (S2402), Cat C Session Lifecycle +
Logout Cleanup Contract (S2403), Cat D Frontend Integration +
Silent-401 SYSTEMIC Resolution (S2404) — under arc pin
`pa-6279ead1714c4630` preserved through all four children per
playbook §16 arc-standard behavior. Runtime target 6 sessions
ACHIEVED (parent scoping + 4 children + this xx99 = 6/6). Rigby
SIGN discipline held across every stage: parent scoping SIGN
Medium-High + Cat A MED 0.74 + Cat B MED-HIGH ~0.80 + Cat C
MED-HIGH ~0.82 + Cat D MED-HIGH ~0.80-0.85 (Cat D the highest child
confidence in the arc, with monotonically-increasing confidence
across children as the arc's method matured). Each child audit
retired a dedicated fresh SIGN pin at cycle close per playbook §15
SIGN-isolation discipline — this xx99 will be the SIXTEENTH
consecutive dedicated fresh SIGN pin retirement in Research OS.

**Answering the central lens question** (Chris-locked at S2400
open): *"Is the platform's auth model a contract (explicit trust
boundaries + declared permission floors + declared session /
refresh / logout semantics + consistent failure surfacing), or an
accretion of per-surface defaults whose failures are silently
swallowed (e.g., silent 401 / permissive fallbacks / ad-hoc public
path lists)?"* **Canonical verdict: ACCRETION with declared-but-unenforced
contracts.** Mechanisms generally work at file-precision in the
sampled surfaces (Rigby SIGN Q1 fold — 2026-07-05: not claiming
absolute across every subsystem; sampled coverage per §14.5 rate
tables in each child arc): DRF Token auth, ProtectedRoute gate,
Zustand persist, backend `APIResponseEnvelope`, request + response
interceptors, ~65 `@token_auth_required` decorator applications at
HEAD. But the *contract* — the promise that a mechanism means what
its name implies — is silently violated across all four contract
axes examined. Cat A found trust boundaries
declared without runtime enforcement (VIP demo prompt-only, Fleet
permissive fallback, PURGE_SECRET hardcoded fallback, WebSocket
middleware DEAD in ASGI stack); Cat B found permission floors
implicit at ~80-90% ESTIMATE inheritance rate with silent-401
SYSTEMIC as necessary-enabling downstream symptom; Cat C found the
session lifecycle contract undeclared across 14 of 15 client-side
persistence surfaces (6.7% declared cleanup rate) + zero
Clear-Site-Data emission + no refresh endpoint + VIPInvite
account_expires_at declared-fictional; Cat D found the frontend
caller surface silent-swallows 401 at ~99% rate across 803 consumer
call-sites (57 direct + 667 useQuery/useMutation + 79 raw fetch
bypass) with zero typed AxiosError catches and zero error
boundaries. The pattern is not scattered defects — it is one
architectural posture (declared contract without enforcement or
observability) surfacing consistently at every axis the arc looked
at.

**What the arc delivered beyond enumeration.** Three three-option
decision spaces enumerated with evidence + recommendation leans for
Chris D-verdict: Cat B (a) uniform IsAuthenticated / (b) split
read-write + client-side auth-check-on-write [Cat B PRIMARY for
REMEDIATION WINDOW] / (c) per-endpoint permission registry [Cat B
PRIMARY for LONG-TERM GOVERNANCE]; Cat C (α) silent-refresh / (β)
explicit-re-login [Cat C proposes as least-assumption default] /
(γ) hybrid; Cat D typed-error-envelope (α) throw typed exceptions
/ (β) return discriminated-union / (γ) React Query error callbacks
+ ErrorBoundary [Cat D PRIMARY DEFAULT] AND Cat D whitelist-
replacement (α) explicit endpoint list / (β) backend-header / (γ)
per-api-module `authHandling: 'default' | 'suppress_redirect'`
string enum [Cat D PRIMARY DEFAULT]. Cat D Rigby Q6 fold
reconciled γ as mechanism with Cat C β as UX policy (γ = RQ error
callback + top-level ErrorBoundary; Cat C β "explicit re-login" =
message/UX policy nested inside γ). Cat D §19.1 handler discipline
requires distinguishing 401/403 vs network/offline vs 5xx and
copy MUST avoid time-based "expired" language until F-C-VIP-1
(VIPInvite.account_expires_at not enforced at runtime) resolves.

**Codification candidate at §10.2.** Cat C established
silent-degrade-vs-explicit-failure ambiguity on session-lifecycle
plane as playbook §20 codification candidate TRIGGER #1 (13 of 14
findings silent-degrade class = 92.9%); Cat D CONFIRMED TRIGGER #2
on 401-handling plane (17 of 19 findings silent-degrade class =
89.5%; 2 governance-class findings F-D-OWN-1 + F-D-OWN-2 explicitly
named as non-silent-degrade per Rigby Q5 fold). Cat D Rigby Q5 fold
tightened the codification claim: silent-degrade dominance persists
across Cat C and Cat D exceeding §20 dual-trigger threshold; promote
to playbook v3 candidate focused on **auth failure handling
(401/403/refresh/logout)** with explicit UX + telemetry requirements
— scope-bounded to auth plane, not general silent-degrade-anywhere.
This is Group 2400's contribution to the research process itself,
not just the domain being researched.

**MC-4 resolution.** Group 2400 Auth's 4-child structure completes
MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails across-5-consecutive-arcs
(1900 + 2000+ + 2100 + 2200 + 2400), resolving the S2199 Q3
STRENGTHEN dial-back at this xx99 close. Auth was materially
different in scope than any prior arc (full auth stack across
backend middleware + backend views + frontend interceptor + Zustand
stores + Sidebar logout onClick + WebSocket auth middleware) — 5th-arc
extension IS a validated stress test per S2299 canonical summary
§5.3 formulation. **Resolution is methodological, not platform-state
(Rigby SIGN Q2 fold — 2026-07-05):** the playbook's 4-child-arc
pattern is *codification-confirmed with scope guardrails across 5
consecutive arcs, including a full-stack stress test in Auth* —
not "the platform's auth is fixed." Findings graduate to T-slot
post-arc queue; the platform's auth remediation lives in §8 P0
batch, not in this xx99. MC-14 CANDIDATE-threshold-satisfied
extended to 5-arc-stages via Group 2200 + Group 2400 Cat A + Cat B
+ Cat C + Cat D = 5 confirming arc-stages preserving arc-pin
through all child sessions per playbook §16 — **still CANDIDATE
per Rigby SIGN Q2 fold**; codification-confirmation threshold
proposal deferred to §10.4 (5 arc-stages = provisional-confirmed;
needs 1 additional non-adjacent domain OR 2 more groups to flip
CODIFICATION-CONFIRMED).

**What ships next.** Chris D-verdicts at this xx99 close on Cat B
(a)/(b)/(c) + Cat C (α)/(β)/(γ) + Cat D α/β/γ × 2. Post-arc T-slot
executes the rank-1 co-equal P0 batch (14 items across P0-A
platform-wide + P0-B token-lifecycle + P0-C endpoint-specific per
Cat D Rigby Q15 fold tiered ordering — co-equal contract preserved
per Cat A/B/C precedent; tiers surface blast-radius truth for
sequencing). T2 Group 2500 API arc opens next (per S2299 §8.2
post-Group-2400 queue) with silent-401 + refresh + logout-envelope
+ Clear-Site-Data + typed-error-envelope + per-endpoint permission
registry design-prep as core scope. F-C-VIP-1 risk-gate constraint
must resolve BEFORE any α/β/γ envelope UX ships (Cat C preservation
through xx99).

---

## 2. What This Arc Answered

Per-child rollup of the 28 canonical questions (playbook §9). Each
child answered a subset; consolidated below.

### Cat A (S2401) — Authentication Surface + Trust Boundaries

- **Q1-Q2 Domain purpose + boundaries** answered — authentication
  is the platform's identity-attach layer; boundaries include
  standard user token, VIP demo, Fleet HMAC, service tokens
  (`PA_DB_HEALTH_RPC_TOKEN`, `PUBLIC_INTEL_TOKEN`), staff/reviewer
  path lists.
- **Q3 Canonical entry points** answered — `core/auth_middleware.py:
  563-681` UnifiedTokenAuthenticationMiddleware (~108 PUBLIC_PATHS);
  `.py:541-544, 610-614` STAFF_REQUIRED_PATHS; `.py:548-556, 615-623`
  REVIEWER_BLOCKED_PATHS; `core/services/fleet_auth_drf.py:65-150`
  FleetSignatureAuthentication; `core/vip_middleware.py:50-105` VIP
  demo; `core/auth_middleware.py:36-81` `@token_auth_required`
  decorator (65 uses / 10 files at HEAD; drift-down from 68/9 at
  S2401 close).
- **Q4-Q9 Models + services + APIs + runtime flows + data
  ownership** answered — token model DRF `authtoken` (no expiry);
  `UnifiedUser` model; middleware chain enforces default
  `TokenAuthentication` unless a PUBLIC_PATHS match; 14 gate
  mechanisms enumerated at §14.5 trust-boundary rate table.
- **Q10-Q13 Documentation + research + maturity** answered — no
  dedicated `docs/topics/auth.md` at HEAD (AU-1 anchor-update);
  MODERATE research coverage post-arc.
- **Q19-Q22 Cross-domain integrations** answered — 7 cross-arc
  flags CF-1 → CF-7 emitted (see §9).
- **Q23-Q27 Drift + debt + boundaries + duplicates + ownership**
  answered — 5 headline findings F-CRIT-1 PURGE_SECRET + F-BND-4a
  bet-placement unauth + F-BND-4b reviewer inversion + F-CRIT-2
  503-fork zero-coverage + F-HIGH-1 VIP TWO-LAYER drift; §14.5
  trust-boundary rate table 3 PRESENT + 2 PARTIAL + 9 ABSENT.
- **Q28 Future research** answered — §19 POSTURE-DECISION triad +
  §12 6 CANONICAL blockers.

### Cat B (S2402) — Authorization + Permission-Floor Uniformity

- **Q1-Q9** answered — authorization is the platform's
  permission-floor plane; ~1,864 `path()` patterns × permission
  floor cell inventoried via 20-endpoint stratified sample
  framework; ~80-90% ESTIMATE implicit-inheritance rate.
- **Q19-Q22** answered — 5 cross-arc flags CF-B1 → CF-B5.
- **Q23-Q27** answered — 7 headline findings F-B-CRIT-1
  implicit-inheritance ~80-90% ROOT CAUSE + F-B-CRIT-2 silent-401
  SYSTEMIC as necessary-enabling downstream symptom + F-B-HIGH-1
  STAFF_REQUIRED_PATHS 2-of-3 PHANTOM + F-B-HIGH-2 F-BND-4a/4b
  REVIEWER_BLOCKED DEAD-CODE + F-B-HIGH-3 workspace-membership
  implicit gate + F-B-HIGH-4 auth_views_enhanced.py
  `@authentication_classes([])` stacking (4 files) + F-B-MED-1 2
  mythology `@permission_classes([])` empty declarations.
- **Q28** answered — §19.1 three-option decision space (a)/(b)/(c)
  + §19.2 rank-1 co-equal P0 batch.

### Cat C (S2403) — Session Lifecycle + Logout Cleanup Contract

- **Q1-Q9** answered — session lifecycle is the token
  issuance/refresh/logout/cleanup plane; §14.2 15-surface storageKeys
  × logout-cleanup CONTRACT table (1 CLEAN + 3 PARTIAL + 11
  NO-CLEANUP; declared cleanup rate 1/15 = 6.7%); §14.3 21-loci
  lifecycle-observability rate (5 WORKING + 5 PARTIAL + 11 DEAD).
- **Q19-Q22** answered — 7 cross-arc flags CF-C1 → CF-C7.
- **Q23-Q27** answered — 7 headline findings F-C-VIP-1 HIGH
  (declared-fictional class introduced this arc) + F-C-REFRESH-1
  HIGH + F-C-CSD-1 HIGH + F-C-STORE-1 HIGH + F-C-COOKIE-1 LOW-MED
  + F-C-LOGOUT-1 MED + F-C-COCKPIT-1 MED.
- **Q28** answered — §19.1 three-option decision space
  (α)/(β)/(γ); Cat C proposes β explicit-re-login as
  least-assumption default; F-C-VIP-1 risk-gate constraint for any
  α/β/γ shipping.

### Cat D (S2404) — Frontend Integration + Silent-401 SYSTEMIC Resolution

- **Q1-Q9** answered — frontend integration is the caller-side
  symptom plane; 803 consumer call-sites (57 direct api.<verb>() +
  667 useQuery/useMutation + 79 raw fetch bypass); 90.2%
  interceptor-routed + 9.8% bypass; ~99% silent-swallow rate at
  api.ts:48-56; verifier-loop resolved denominator from S2203 A3
  ~630 baseline.
- **Q19-Q22** answered — 7 cross-arc flags CF-D1 → CF-D7 including
  CF-D5 R6 error-boundary framework as BLOCKING PREREQUISITE for
  option-γ per Rigby Q18 fold.
- **Q23-Q27** answered — 11 headline findings F-D-CALL-1 HIGH +
  F-D-BYPASS-1 HIGH + F-D-SIDEBAR-1 HIGH NEW-BEYOND-CAT-C +
  F-D-ENVELOPE-1 HIGH + F-D-BOUNDARY-1 HIGH + F-D-PA-1 HIGH (Rigby
  Q10 escalated MED→HIGH) + F-D-WHITELIST-1 MED + F-D-OWN-1 MED
  governance non-silent-degrade + F-D-OWN-2 MED governance
  non-silent-degrade + F-D-EVENT-1 MED + F-D-COCKPIT-1 MED.
- **Q28** answered — §19.1 typed-error-envelope decision space
  (α/β/γ) + whitelist-replacement decision space (α/β/γ × 2 second
  axis); Cat D proposes γ × γ as PRIMARY DEFAULT; §19.2 rank-1
  co-equal P0 batch with Rigby Q15 fold tiered ordering P0-A/B/C.

**28-question coverage across arc:** All 28 questions addressed
across the four children with per-child specialization. Cat A + Cat
B focus on the backend-side model (Q1-Q9 domain + Q23-Q27 drift);
Cat C bridges backend + frontend session-lifecycle contract (Q9
data ownership + Q23-Q27 drift both planes); Cat D closes the
frontend caller-side symptom loop (Q19-Q22 integrations + Q23-Q27
drift).

---

## 3. Consolidated Domain Shape

The auth surface at HEAD `4e6c1ee8` is a **contract mesh with
declared-but-unenforced boundaries + observable-but-untyped
failure surfacing + implicit-permission-floor inheritance +
undeclared-session-lifecycle-cleanup + silent-401-SYSTEMIC caller
side**. Single mental model:

```
                 ┌─────────────────────────────────────┐
                 │      IDENTITY-ATTACH LAYER          │  (Cat A)
                 │  Token / VIP / Fleet / Service      │
                 │      + ~108 PUBLIC_PATHS            │
                 └──────────────┬──────────────────────┘
                                │
                                │ [MECHANISM WORKS at file-precision]
                                │ [CONTRACT VIOLATED at boundary:
                                │  VIP prompt-only + Fleet fallback
                                │  + PURGE_SECRET hardcoded + WS DEAD]
                                │
                 ┌──────────────▼──────────────────────┐
                 │      AUTHORIZATION FLOOR            │  (Cat B)
                 │  ~1,864 path() × permission floor   │
                 │  ~80-90% ESTIMATE implicit-inherit  │
                 └──────────────┬──────────────────────┘
                                │
                                │ [FLOOR IS IMPLICIT — cannot observe]
                                │ [CANNOT distinguish 401 vs 403 vs 500
                                │  without inspecting error.response]
                                │
                 ┌──────────────▼──────────────────────┐
                 │      SESSION LIFECYCLE PLANE        │  (Cat C)
                 │  Token permanent + no refresh       │
                 │  + Zero Clear-Site-Data emission    │
                 │  + 14/15 surfaces NO-CLEANUP        │
                 │  + VIP account_expires_at DECLARED- │
                 │    FICTIONAL (14d not enforced)     │
                 └──────────────┬──────────────────────┘
                                │
                                │ [CONTRACT UNDECLARED + UNENFORCED]
                                │ [SIDEBAR logout does NOT revoke
                                │  backend token — attacker-valid
                                │  window indefinite]
                                │
                 ┌──────────────▼──────────────────────┐
                 │      FRONTEND CALLER SURFACE        │  (Cat D)
                 │  803 consumer call-sites            │
                 │  ~99% silent-swallow rate           │
                 │  + 79 raw fetch bypass (9.8%)       │
                 │  + 0 typed AxiosError catches       │
                 │  + 0 error boundaries anywhere      │
                 └─────────────────────────────────────┘

                 Cross-cutting all four layers:
                 - Silent-degrade dominant class (Cat C 92.9% + Cat D 89.5%)
                 - Q20 fold TRIGGER #1 (Cat C) + TRIGGER #2 (Cat D)
                 - Two-trigger codification threshold met at §10.2
```

Four contract-surface axes; each layer works mechanically; each
layer silently violates its contract at boundary. The pattern
generalizes across the whole auth stack — this is the arc's
consolidated finding.

**Numerical summary at HEAD `4e6c1ee8` (canonical figures
consolidating child-audit HEAD-verifications):**

| Axis | Metric | Value |
|---|---|---|
| Identity-attach | Auth mechanisms | 6 (token + VIP + Fleet + 2 service tokens + Django session) |
| Identity-attach | `@token_auth_required` decorator uses | 65 across 10 files (definition + 64 across 9 view files) |
| Identity-attach | Trust boundaries with smoke-test coverage | 3 PRESENT + 2 PARTIAL + 9 ABSENT |
| Authorization | `path()` patterns | ~1,864 |
| Authorization | Permission-floor implicit-inheritance rate | ~80-90% ESTIMATE |
| Authorization | STAFF_REQUIRED_PATHS phantom entries | 2 of 3 |
| Authorization | 21-loci permission-floor enforcement | 10 WORKING + 6 PARTIAL + 4 EXPERIMENTAL + 3 MED-HIGH drift + 1 DEAD |
| Session lifecycle | Token expiry field | NONE (DRF `authtoken` no expires_at) |
| Session lifecycle | Refresh endpoint | ABSENT |
| Session lifecycle | Clear-Site-Data emission | ZERO (verified zero-match grep) |
| Session lifecycle | 15-surface storageKeys cleanup rate | 1 CLEAN + 3 PARTIAL + 11 NO-CLEANUP (6.7% declared cleanup rate) |
| Session lifecycle | 21-loci observability | 5 WORKING + 5 PARTIAL + 11 DEAD |
| Session lifecycle | VIPInvite.account_expires_at enforcement | ZERO (declared-fictional 14d) |
| Frontend caller | Consumer call-sites | 803 total (57 direct + 667 hook + 79 raw fetch) |
| Frontend caller | Interceptor coverage | 90.2% (724 of 803) |
| Frontend caller | Silent-swallow rate | ~99% |
| Frontend caller | Typed AxiosError catches | 0 |
| Frontend caller | Error boundaries | 0 |
| Frontend caller | Whitelist substring match false-positives | 0 (BRITTLE forward) |

---

## 4. Cross-Cutting Patterns

Themes visible only across multiple children — patterns Cat A / Cat
B / Cat C / Cat D individually could not have surfaced.

### 4.1 Declared-but-unenforced contract pattern (all 4 categories)

Every child surfaced instances where a mechanism *declares* a
contract but the runtime does not *enforce* it:

- Cat A: `VIP demo` middleware declares read-only for
  `vip_demo_viewer` role (prompt-only injection) but PA has no
  runtime gate on write operations from that role;
  `FleetSignatureAuthentication` declares HMAC signature check but
  permissive fallback silently passes unverified callers to
  downstream capability check.
- Cat B: DRF default `TokenAuthentication` declares
  `IsAuthenticated` inheritance for ~80-90% of endpoints implicitly,
  but rate is UNOBSERVABLE (no registry + no CI test-harness);
  STAFF_REQUIRED_PATHS declares 3 gated paths but 2 of 3 are phantom
  entries (no `path()` registration).
- Cat C: `VIPInvite.account_expires_at` (14d) declared as field in
  model + returned in response body but NEVER checked at runtime
  (declared-fictional class introduced this arc). Response body
  returns `account_expires_at.isoformat()` — server tells client an
  expiry it will never enforce.
- Cat D: `frontend/src/lib/api.ts:47` inline comment declares "Only
  redirect to login for explicit auth endpoints / Other 401s should
  be handled by the component" — implying component-level handling —
  but 0 typed AxiosError catches + 0 error boundaries + ~99%
  silent-swallow rate means the "handled by the component" contract
  is NOT enforced. Sidebar.tsx:356 declares logout via
  authStore.logout() but does NOT call `authApi.logout()` — declares
  logout without backend revoke.

**Pattern generalizes.** This is one architectural posture, not
scattered defects. The pattern is *declaration-without-enforcement*.
It surfaces at every axis the arc looked at.

### 4.2 Silent-degrade class dominance (Cat C 92.9% + Cat D 89.5%)

Playbook §14 finding-type discipline classifies findings by class.
Cat C established silent-degrade as dominant class (13 of 14
findings; 92.9%); Cat D confirmed (17 of 19 findings; 89.5%; 2
non-silent-degrade findings both governance class: F-D-OWN-1
CODEOWNERS + F-D-OWN-2 CI test-harness — named explicitly per Rigby
Q5 fold to preserve unambiguity). **Q20 fold TRIGGER #1 (Cat C) +
TRIGGER #2 (Cat D) two-trigger codification threshold met.** See
§10.2 for codification candidate.

### 4.3 Same-issue-lineage cross-references (preserved per Cat C Q16a fold discipline)

Findings that surface the same underlying issue across multiple
children get lineage-preserved cross-references, NOT merged:

- **F-VIP-1 (Cat A) ↔ F-C-VIP-1 (Cat C)** — VIP demo enforcement
  surface. Cat A frames as "prompt-only injection soft gate";
  Cat C frames as "account_expires_at 14d declared-fictional".
  Two different mechanisms; one underlying "VIP enforcement" gap.
- **F-TOKEN-1 (Cat A) ↔ F-C-REFRESH-1 (Cat C)** — no expiry +
  no refresh = implicit permanent-token contract absent password
  event. Cat A frames as "no expires_at field"; Cat C frames as
  "no refresh endpoint".
- **F-DEC-1 (Cat A) ↔ F-B-CRIT-2 (Cat B) ↔ F-D-CALL-1 (Cat D)** —
  decorator drift → permission-floor implicit-inheritance → silent-
  401 SYSTEMIC caller surface. Three arcs' framings of one contract
  gap (auth failure not first-class typed).
- **F-BND-4a (Cat A) ↔ F-B-HIGH-2 (Cat B)** — bet-placement unauth
  write. Cat A framed as PUBLIC_PATHS + REVIEWER_BLOCKED inversion;
  Cat B re-verified at HEAD and confirmed REVIEWER_BLOCKED entry is
  DEAD CODE (middleware early-returns on PUBLIC match at line 570;
  REVIEWER check at line 668 never reached). Cat B refined the
  finding without merging.

**Provenance discipline preserves per-arc framings.** Merging would
lose the analytic lens each child brought.

### 4.4 Two-sided FE-symptom-vs-BE-model framing (Cat B ↔ Cat D)

Cat B established F-B-CRIT-2 silent-401 SYSTEMIC as **necessary-
enabling downstream symptom** of Cat B F-B-CRIT-1 permission-floor
implicit-inheritance (~80-90% rate). Cat D delivered the caller-side
evidence at 803-scale + verifier-loop-resolved denominator. Neither
child alone could have delivered the framing — Cat B provided the
BE-model ROOT CAUSE; Cat D provided the FE-symptom scale evidence.
This two-sided framing was pre-scoped in S2203 §14 F3 + S2204 §19.1
R1 mirror; Group 2400 arc executed the two-sided consolidation.

### 4.5 Governance-class findings surface across arc governance layer

Governance-class findings (playbook §11 finding-type
`unclear_owner` + `missing_connection` at governance layer) surface
consistently across all four categories:

- Cat A F-DOC-1 no `docs/topics/auth.md`
- Cat B F-B-OWN-6 no CI test-harness for permission-floor
  enforcement
- Cat C AU-C series anchor-update gaps (no PLATFORM_INVENTORY
  §Auth autoblock + no PLATFORM_WHAT_IT_IS §Auth narrative + no
  session_lifecycle topic doc)
- Cat D F-D-OWN-1 CODEOWNERS absent at all 3 canonical locations +
  F-D-OWN-2 no CI test-harness for silent-401 rate

**Governance layer is uniformly EXPERIMENTAL across all four arc
categories.** No CODEOWNERS. No CI enforcement. No dedicated topic
docs. No anchor-update surface. Cat D §14.1 classification of
governance findings as non-silent-degrade (distinct from technical/
runtime findings) is the arc's finest-grain evidence that this
pattern is not accidental — it is a distinct EXPERIMENTAL layer.

### 4.6 Cat C introduced two new classes; both re-used by Cat D

- **Declared-fictional class** (Cat C Q4 fold — distinguishes
  "field exists in code/config but no enforcement path" from silent-
  swallow which requires an actual code path that discards a failure).
  Cat D re-uses via F-D-ENVELOPE-1 framing (typed-error-envelope
  declared possible via `InternalAxiosRequestConfig` extension but no
  runtime enforcement).
- **Three-axis maturity lens** (Cat C Q1 fold — WORKING mechanisms
  / PARTIAL lifecycle correctness / EXPERIMENTAL governance).
  Cat D re-uses in §13 verdict (Mechanisms WORKING + Contract
  semantics PARTIAL + Governance EXPERIMENTAL). Overall PARTIAL.

Both classes should promote to playbook v3. See §10.2.

---

## 5. Resolved Contradictions

Where children disagreed; canonical verdict + rationale.

### 5.1 Decorator count drift (Cat A 68/9 vs Cat D 65/10)

- **Cat A (S2401):** claimed `@token_auth_required` at 68 uses
  across 9 view files.
- **Cat D (S2404) verifier-loop at HEAD `31398008`:** 65
  occurrences across 10 files (10th = `auth_middleware.py:1`
  definition site; applied uses = 64 across 9 view files).

**Canonical verdict:** 65 occurrences / 10 files at HEAD; applied
uses = 64 / 9 view files. Cat A baseline drifted DOWN by ~3-4 uses
between S2401 close and S2404 open, attributed to S2101–S2402 DRF
`permission_class` migrations (visible in git log). Semantic finding
UNCHANGED — F-DEC-1 STILL-LIVE at HEAD. Cat A count preserved as
historical baseline; Cat D count adopted as canonical at HEAD.

### 5.2 Silent-401 call-site denominator (S2203 ~630 vs Cat D 803)

- **S2203 A3 baseline** (Group 2200 arc; pre-Group-2400): ~630 of
  ~1,300 gated call-sites at silent-401 risk. Grep-based; wrapper-
  duplicate acknowledged (S2203 §14 F3 Q14 hedge).
- **Cat D (S2404) verifier-loop:** 913 direct `api.<verb>()` (856
  are API-METHOD-DEFINITIONS in api.ts; 57 direct consumer sites) +
  667 useQuery/useMutation + 79 raw fetch() bypass = **803 total
  consumer call-sites**; 724 interceptor-routed (90.2%) + 79 bypass
  (9.8%).

**Canonical verdict:** 803 total consumer call-sites at HEAD. S2203
~630 baseline was interceptor-routed-only + hedged for wrapper
duplicates; consumer-total is larger. Neither is wrong for its
question — S2203 answered "how many gated sites are at risk of
silent-401 via api.ts interceptor" (~630); Cat D answered "what is
the total consumer call-site surface including bypass" (803). Both
figures preserved; Cat D 803 adopted as canonical for total
denominator.

### 5.3 F-D-PA-1 severity (Cat D pre-SIGN MED vs Rigby Q10 fold HIGH)

- **Cat D pre-SIGN draft:** rated F-D-PA-1 (PA-chat endpoints do
  not match whitelist; 401 mid-conversation = silent reject) as
  MED severity.
- **Rigby SIGN cycle 1 Q10 fold:** ESCALATE TO HIGH. Rationale: PA
  is control-plane UX per CLAUDE.md workflow rules; silent-401
  mid-conversation looks like agent-hang UX and breaks the core
  workflow; severity should reflect blast radius + user-trust
  impact, not just endpoint count.

**Canonical verdict:** F-D-PA-1 HIGH at Cat D close. Chris "commit
it" ratification carried through. Pattern reinforcement: severity
in this arc reflects blast radius + user-trust impact, not endpoint
count alone.

### 5.4 Silent-401 SYSTEMIC framing (Cat B "ROOT CAUSE" vs Cat D "SYMPTOM")

- **Cat B (S2402) §14 F-B-CRIT-2:** silent-401 SYSTEMIC is a
  NECESSARY-ENABLING-CONDITION downstream of F-B-CRIT-1
  permission-floor implicit-inheritance (~80-90% ESTIMATE). Cat B
  frames F-B-CRIT-1 as ROOT CAUSE + F-B-CRIT-2 as SYMPTOM.
- **Cat D (S2404) §2 + §14 F-D-CALL-1:** silent-401 SYSTEMIC is the
  caller-side visible manifestation across 803 consumer call-sites.
  Cat D frames F-B-CRIT-2 as the SYSTEMIC finding it audits at scale.

**Canonical verdict:** NO CONTRADICTION. Cat B's ROOT CAUSE (BE
model) + SYMPTOM (visible behavior) framing preserved. Cat D
delivered the SYMPTOM's scale evidence + decision-space enumeration.
Both framings hold simultaneously — this is the two-sided FE-symptom-
vs-BE-model discipline (see §4.4).

---

## 6. Unresolved Unknowns

Explicit list; promotes to §8.

- **U1 Exact React Query `TError` generic adoption rate.** Cat D
  Agent 4 sampled 5 files with typed generics; whether `TError`
  populated in any of the 5 requires per-file read (deferred).
  Estimated ≤1% of 667 RQ sites have TError set.
- **U2 79 raw fetch site classification.** Cat D counted 79 bypass
  sites; per-site classification (auth-required vs public vs
  streaming/SSE + credentials mode + response type) deferred to
  post-arc T-slot per Rigby Q17 fold research item (2b).
- **U3 Session 819 formal design doc for "selective 401 redirect".**
  Inline comment at api.ts:46-47 documents intent; no external
  handoff design doc located. Sufficient for HEAD verification;
  formal-doc-existence UNKNOWN.
- **U4 Actual permission-floor inheritance rate.** Cat B ESTIMATE
  ~80-90%; whole-platform enumeration would require path()-by-
  path() audit. Bounded range acceptable for xx99; exact rate
  deferred to Group 2500 API arc registry construction.
- **U5 Cross-tab logout propagation intent.** F-C-TAB-1 CONFIRMED
  zero adoption at HEAD; design-space (BroadcastChannel vs storage
  event) deferred per Cat C anti-scope #5 (session-model authoring
  post-arc).
- **U6 Backend Clear-Site-Data emission feasibility for Group 2500
  API arc.** Cat C F-C-CSD-1 confirms zero emission at HEAD; option-β
  whitelist replacement backend-header pattern (Cat D §19.1) feasibility
  is UNKNOWN at Group 2400 close pending Group 2500 API scoping.
- **U7 `paStore.syncUser` field-list completeness.** Cat C §14.2
  paStore PARTIAL cleanup surface; complete field-list requires
  Group 2600 PA workspace-context audit (CF-C2 + CF-D2 delegation).

---

## 7. Anchor-Update Recommendations

Concrete proposed edits. This xx99 does NOT apply anchor edits
directly (per playbook §11.3 rule — ARCHITECTURE_INDEX v-bump commit
applies them). Recommendations aggregated from Cat A AU-1 + Cat B
AU-B2 + Cat C AU-C1..AU-C5 + Cat D AU-D1..AU-D7.

### 7.1 PLATFORM_INVENTORY.md

**AU-1 (Cat A) + AU-B2 (Cat B) + AU-C2 (Cat C) + AU-D3 (Cat D) —
CREATE `§Auth` autoblock.** No dedicated Auth section exists at
HEAD; Auth surfaces are inventoried indirectly via routes + views +
models. Add:

- Auth mechanism inventory table (6 mechanisms: token + VIP + Fleet
  + 2 service tokens + Django session)
- `@token_auth_required` decorator use count (65 at HEAD)
- ~108 PUBLIC_PATHS + STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS
  counts + phantom rate (2 of 3 STAFF_REQUIRED phantom per Cat B)
- Trust-boundary rate (14 mechanisms × 3 PRESENT + 2 PARTIAL + 9
  ABSENT smoke-test coverage per Cat A §14.5)
- Permission-floor 21-loci rate (10 WORKING + 6 PARTIAL + 4
  EXPERIMENTAL + 3 MED-HIGH drift + 1 DEAD per Cat B §14.5)
- 15-surface storageKeys cleanup rate (1 CLEAN + 3 PARTIAL + 11
  NO-CLEANUP; 6.7% declared cleanup rate per Cat C §14.2)
- 21-loci lifecycle-observability rate (5 WORKING + 5 PARTIAL + 11
  DEAD per Cat C §14.3)
- Cat D 803-consumer-call-site inventory (57 direct + 667 hook + 79
  raw fetch; 90.2% interceptor-routed + 9.8% bypass; ~99%
  silent-swallow rate per Cat D §14.5)
- Add regeneration hook per `generate_platform_inventory` command
  (autoblock generation from `gather_inventory().auth`).

### 7.2 PLATFORM_WHAT_IT_IS.md

**AU-B (Cat B) + AU-C3 (Cat C) + AU-D4 (Cat D) — CREATE `§Auth`
narrative subsection.** No dedicated Auth subsection exists at
HEAD. Add narrative for:

- The four-layer contract mesh (identity-attach + authorization
  floor + session lifecycle plane + frontend caller surface) —
  reuse §3 domain-shape diagram
- Declared-but-unenforced contract pattern as the arc's core
  finding
- Silent-degrade dominant class + Q20 fold codification candidate
  (scope-bounded to auth-failure-handling per §10.2)
- Three-axis maturity lens (WORKING mechanisms / PARTIAL contract
  semantics / EXPERIMENTAL governance)
- Three three-option decision spaces + Chris D-verdicts (post-xx99
  ratification)

### 7.3 ARCHITECTURE_INDEX.md

**AU-D6 (Cat D) — Add "Auth failure handling decision matrix
(α/β/γ typed-error-envelope × α/β/γ whitelist axis)" pointer.**
Prevents future audits from re-deriving the design space. Add
compact pointer in ARCHITECTURE_INDEX §7 decision matrix cross-link
section.

**Also:** ARCHITECTURE_INDEX v87 → v88 with §1.91 `2499_auth_canonical_summary.md`
registration above §1.90 `2404_frontend_integration_silent_401_systemic_resolution_audit.md`
(this xx99's registration).

### 7.4 Other affected docs

- **AU-D2 (Cat D) — CREATE `docs/topics/auth.md`** with 4
  subsections mirroring the four contract axes (Cat A mechanism
  inventory + Cat B permission-floor uniformity + Cat C session
  lifecycle + Cat D FE integration).
- **AU-D7 (Cat D) — Inside `docs/topics/auth.md`** add
  DOC_LIFECYCLE cross-link note indicating (i) where "current
  state vs target state" lives; (ii) how future sessions should
  supersede this doc — prevents narrative drift as α/β/γ options
  ship.
- **AU-D1 (Cat D) — refresh `docs/topics/frontend.md`** with
  silent-401 pattern + typed-error-envelope + error-boundary
  framework subsection. Cross-link to new `docs/topics/auth.md`.
- **AU-D5 (Cat D) — CREATE CODEOWNERS declaration.** Absent at all
  3 canonical locations (`.github/`, root, `docs/`) per Cat D
  F-D-OWN-1 HEAD-verified. Frontend api.ts + authStore.ts owned de
  facto by Chris; cross-arc typed-error-envelope + whitelist-
  replacement ownership UNASSIGNED at close.
- **AU-C4 (Cat C — optional) — CREATE `docs/topics/session_lifecycle.md`**
  if session-lifecycle contract warrants dedicated narrative post-
  Chris-D-verdict on Cat C (α/β/γ). Otherwise fold into AU-D2 topics/
  auth.md subsection.
- **`docs/AGENTS.md` + `docs/SERVICES.md`** — no immediate anchor
  updates required (auth surface unchanged at code level; findings
  are contract/observability gaps).

---

## 8. Follow-On Research Queue

Ranked next-mission list. Consolidated from Cat A/B/C/D §19 items +
Cat D §19.2 rank-1 co-equal P0 batch with Rigby Q15 fold tiered
ordering.

### 8.1 P0 rank-1 co-equal batch (14 items; tiered per Cat D Rigby Q15 fold)

**Co-equal contract preserved** per Cat A/B/C precedent. Tiers
surface blast-radius truth for implementation sequencing, not
priority downgrade.

**P0-A (platform-wide / whole-auth-surface blast radius):**
- Cat D F-D-CALL-1 803-scale silent-401 remediation
- Cat D F-D-BYPASS-1 79-raw-fetch bypass reconciliation
- Cat D F-D-ENVELOPE-1 Typed-error-envelope (α/β/γ post-Chris-D-verdict)
- Cat D F-D-BOUNDARY-1 Error-boundary framework establishment (S2299 §8.3 R6 execution; BLOCKING PREREQUISITE for option-γ per CF-D5)

**P0-B (token lifecycle / security window):**
- Cat D F-D-SIDEBAR-1 Sidebar backend-token-revoke fix (single-line addition per Cat C AU-C1)
- Cat C F-C-REFRESH-1 refresh discipline decision-space execution
- Cat C F-C-VIP-1 VIPInvite.account_expires_at ENFORCEMENT (risk-gate prerequisite for α/β/γ)
- Cat C F-C-CSD-1 Clear-Site-Data emission on logout
- Cat C F-C-STORE-1 15-surface × logout-cleanup declared contract execution

**P0-C (endpoint-specific):**
- Cat A F-CRIT-1 PURGE_SECRET hardcoded fallback remediation (preserved)
- Cat A F-BND-4a Unauthenticated bet-placement WRITE remediation (preserved money-path boundary)
- Cat B F-B-CRIT-1 Permission-floor implicit-inheritance ~80-90% (Chris D-verdict this xx99 on (a)/(b)/(c))
- Cat B F-B-CRIT-2 Silent-401 SYSTEMIC (Cat D delivered 803-scale evidence + α/β/γ × 2 decision-space)
- Cat D F-D-WHITELIST-1 Whitelist replacement (α/β/γ post-Chris-D-verdict this xx99)

### 8.2 P1 batch (governance + observability)

- **Cat D F-D-OWN-1** — CODEOWNERS declaration (single-file addition)
- **Cat D F-D-OWN-2 + Cat B F-B-OWN-6** — CI test-harness for silent-401 rate + permission-floor enforcement (bundled per Rigby Q13 lean)
- **Cat A + Cat C + Cat D anchor-update batch** — execute §7.1-§7.4 anchor updates during T2 Group 2500 API arc or as standalone maintainer-decision batch
- **Cat D F-D-EVENT-1** — auth-event emission on observability channels (CF-D3 to Group 1700 umbrella roll-up)
- **Cat D F-D-COCKPIT-1** — 16 cockpit `<Navigate>` NOT wrapped by ProtectedRoute (persistent 2-audit re-verification signals ownership-drift risk per Rigby Q19 fold; attach to F-D-OWN-1/OWN-2 governance remediation)

### 8.3 P2 batch (research + follow-on)

- **Silent-401 rate telemetry design** — CF-D3 to Group 1700
- **79-raw-fetch site classification refinement** (Rigby Q17 fold) —
  3-axis by auth-required vs public + credentials mode + response
  type
- **PA-chat 401 UX design** — CF-D2 to Group 2600 PA
- **Cross-tab logout propagation design** — F-C-TAB-1 extension
- **OPTIONAL Non-401 failure envelope audit** (Rigby Q17 fold) —
  JSON parse + network offline + timeout + aborted; extends
  F-D-ENVELOPE-1 beyond 401 plane
- **Backend refresh endpoint design** (F-C-REFRESH-1 remediation
  design-prep) — Group 2500 API arc scope

### 8.4 T-slot cross-arc handoff bundles

- **T2 Group 2500 API** (NEXT arc after Group 2400 close per S2299
  §8.2) — CF-A + CF-B + CF-C + CF-D roll-up delivers: refresh
  endpoint + logout envelope + Clear-Site-Data emission spec +
  typed-error-envelope (Cat D α/β/γ) + per-endpoint permission
  registry (Cat B c) + F-B-HIGH-1 STAFF_REQUIRED_PATHS phantom
  cleanup + F-B-HIGH-4 auth_views_enhanced.py fixes
- **T3 Group 2600 PA** (after Group 2500 close) — CF-B2 + CF-C2 +
  CF-D2 delivers: workspace-context authz + `session_tool.retire`
  on user logout + PA-chat 401 UX design + paStore field-list
  completeness
- **T4 Group 1700 Observability** (after Group 2600 close) — CF-A
  CF-2 + CF-B5 + CF-C3 + CF-D3 umbrella roll-up: 503-fork
  asymmetry + login/logout event emit + silent-401 rate telemetry
  + suppress_redirect telemetry + smoke-test coverage per gate
  mechanism
- **T5 Group 2300 Mobile** (CF-D4) — parallel silent-401 audit for
  mobile app (Expo scaffolding); ensure 401-handling parity
  between web + mobile OR document divergence explicitly

---

## 9. Cross-Links to Delegated Arcs

26 total cross-arc coordination flags emitted across Cat A + Cat B
+ Cat C + Cat D; consolidated into 7 delegate arcs.

| Delegate arc | Contributing flags | Roll-up scope |
|---|---|---|
| **Group 2500 API (T2 NEXT)** | CF-3 Cat A + CF-B1 Cat B + CF-C1 Cat C + CF-D1 Cat D | Refresh endpoint + logout envelope + Clear-Site-Data + typed-error envelope (Cat D α/β/γ) + per-endpoint permission registry (Cat B c) + response envelope shape (`APIResponseEnvelope`) formalization + drf-spectacular retrofit for typed responses |
| **Group 2600 PA (T3)** | CF-1 Cat A + CF-B2 Cat B + CF-C2 Cat C + CF-D2 Cat D | Workspace-context authz + `session_tool.retire` cascade on user logout + PA-chat 401 UX design + paStore field-list completeness + WORKSPACE_AWARE_AGENTS 20-agent audit |
| **Group 1700 Observability (T4 UMBRELLA ROLL-UP)** | CF-2 Cat A + CF-B5 Cat B + CF-C3 Cat C + CF-D3 Cat D | Single tracking unit with sub-bullets per Cat C Q11 fold + extends Cat A CF-2 + Cat B CF-B5. Sub-bullets: 503-fork asymmetry smoke-test + login/logout event emit + silent-401 rate telemetry + `authHandling: 'suppress_redirect'` telemetry + auth-event observability per gate mechanism + smoke-test coverage inventory per mechanism (blocker to acceptance criterion #6) |
| **Group 2300 Mobile (parallel arc)** | CF-4 Cat A + CF-C4 Cat C + CF-D4 Cat D | MobilePushToken.revoked_at cascade + parallel silent-401 audit for mobile app + Cat D 401-handling parity between web + mobile |
| **Group 2200 post-arc T-slot (R6 execution)** | CF-6 Cat A + CF-B3 Cat B + CF-C5 Cat C + CF-D5 Cat D | Error-boundary framework establishment ⚠ BLOCKING PREREQUISITE for Cat D option-γ per Cat D Rigby Q18 fold — γ mechanism requires top-level `<ErrorBoundary>` wrapper existing. Cat D unblocks via decision-space documentation; R6 execution owed to post-arc T-slot |
| **Group 1900 Governance (KillSwitch preservation)** | CF-5 Cat A + CF-D6 Cat D | KillSwitch attestation on typed-401 boundary preserved. Ensure auth-error-swallow does not bypass kill-switch semantics if governance decisions cross 401 boundary. No new work; boundary preservation only |
| **Group 2400 Auth INTERNAL post-arc (this xx99)** | CF-7 Cat A External Integrations + CF-B4 Cat B + CF-C6 Cat C + CF-D7 Cat D | α/β/γ × 2 intersection with Cat C α/β/γ intersection with Cat B a/b/c; three-decision-space intersection resolves at this xx99 via Chris D-verdicts |

**Cross-arc coordination discipline** per Cat C Q11 fold: 4 arcs'
observability flags roll up into single Group 1700 tracking unit
with sub-bullets, not 4 separate handoffs. Prevents 4-way
duplicate work at Group 1700 execution.

---

## 10. What This Research Taught Us About How to Do Research

**ELEVENTH-consecutive §10 meta-methodology application** after
S1399 first + S1499 second + S1599 third + S1699 fourth + S1799
fifth + S1899 sixth + S1999 seventh + S2099 eighth + S2199 ninth +
S2299 tenth. Per Chris directive S1399 close 2026-07-01 + adopted
as playbook §11.3 §10 non-negotiable per feedback_xx99_meta_methodology_section.

### 10.1 What worked (methodology validated across this arc)

- **Same-issue-lineage cross-reference discipline (Cat C Q16a fold
  introduced; Cat D preserved).** Preserving per-arc framings of
  the same underlying issue without merging kept each child's
  analytic lens visible. F-VIP-1 ↔ F-C-VIP-1 kept prompt-only gate
  (Cat A) + declared-fictional field (Cat C) both visible even
  though they share underlying "VIP enforcement" gap. **Validated
  across 2 arcs (Cat C introduction + Cat D preservation).**
- **Three-axis maturity lens (Cat C Q1 fold introduced; Cat D
  preserved).** Mechanisms WORKING + Contract semantics PARTIAL +
  Governance EXPERIMENTAL splits let PARTIAL verdict at whole-arc
  level rest on evidence, not vibes. Cat D re-applied at §13.
  **Validated across 2 arcs (Cat C introduction + Cat D
  preservation).**
- **Verifier-loop pre-Rigby-SIGN discipline (playbook §14).** Cat
  D's 3 sub-agent conflicts (decorator count drift + denominator
  ambiguity + fetch-bypass accounting) all resolved pre-draft;
  none shipped to Rigby. Prevents Rigby-SIGN-poisoning-with-stale-
  claims failure mode. **Validated across every child in Group
  2400 (Cat A caught 1 conflict + Cat B caught 5 + Cat C caught 1
  + Cat D caught 3).**
- **Dedicated fresh SIGN isolation pin per stage (playbook §15).**
  Preventing SIGN-conversation pollution across stages let each
  child's SIGN cycle start clean. 15 consecutive retirements
  across the Research OS as of Cat D close; xx99 will make 16.
  **Zero SIGN-worker instability observed at any child cycle in
  Group 2400.**
- **4-batch × 5-Q child-audit cadence + single-batch × 4-Q
  canonical-summary cadence (playbook §15).** NINTH-consecutive
  child-audit cadence application at Cat D; ELEVENTH-consecutive
  canonical-summary cadence application will land at this xx99
  close. **Both cadences hold at MC-10 codification-ready.**
- **Two-sided FE-symptom-vs-BE-model framing pre-scoped from
  Group 2200 T1 handoff (S2203 §14 F3 + S2204 §19.1 R1 mirror).**
  Cat B delivered ROOT CAUSE; Cat D delivered SYMPTOM scale. Not
  merged; both framings preserved (see §5.4). **Validated as
  cross-arc handoff discipline generalizes from single arc's F1
  framing to multi-arc's ROOT-CAUSE-plus-SYMPTOM two-sidedness.**

### 10.2 What to codify into playbook v3 (per §20 two-triggers rule)

- **Silent-degrade-vs-explicit-failure ambiguity — CODIFICATION
  CANDIDATE CONFIRMED at two-trigger threshold.** Cat C (S2403) =
  TRIGGER #1 (13 of 14 findings silent-degrade class = 92.9%). Cat
  D (S2404) = TRIGGER #2 (17 of 19 findings silent-degrade class =
  89.5%; 2 non-silent-degrade findings both governance class per
  Cat D Rigby Q5 fold). Two-trigger threshold met per playbook §20
  codification rule. **Tightened codification claim** per Cat D
  Rigby Q5 fold: silent-degrade dominance persists across Cat C
  and Cat D exceeding §20 dual-trigger threshold; promote to
  playbook v3 candidate focused on **auth failure handling
  (401/403/refresh/logout) with explicit UX + telemetry
  requirements** — scope-bounded to auth plane where the two
  triggers were observed. NOT general silent-degrade-anywhere
  codification.
- **Conditional promotion rule (Rigby SIGN Q3 fold — 2026-07-05):**
  promote to *general* silent-degrade codification if a 3rd
  trigger appears in a non-auth plane (Groups 2500 API / 2600 PA
  / 1700 Observability). Auth-failure-handling scope-bounding
  holds at this xx99 close; general codification blocked pending
  cross-plane trigger.
- **Declared-fictional class (Cat C Q4 fold) + Three-axis maturity
  lens (Cat C Q1 fold) — CODIFICATION CANDIDATES pending 2nd
  trigger.** Both classes introduced Cat C; both preserved by Cat
  D. Cat D counts as 1st preservation, not 2nd trigger — waiting
  for a future arc to independently derive either class to hit
  two-trigger threshold.
- **Ownership-drift risk flag on re-verification patterns (Cat D
  Rigby Q19 fold introduced).** F-D-COCKPIT-1 kept at MED severity
  but flagged with ownership-drift-risk narrative because Cat C ↔
  Cat D two-audit re-verification without fix indicates ownership
  drift. Pattern-candidate for playbook v3 §14 severity classification
  ("MED + ownership-drift-risk" as codified severity annotation).
  Awaits 2nd application.

### 10.3 What didn't work / anti-patterns to avoid

- **Cat A count baselines drift silently across arcs.** Cat A's
  "68 uses / 9 view files" for `@token_auth_required` was the
  authoritative count at S2401 close. Between S2401 and S2404 the
  code drifted (~3-4 uses removed via DRF permission_class
  migrations) and Cat D verifier-loop had to resolve the delta.
  **Anti-pattern:** treating in-doc numeric counts as authoritative
  across arcs without HEAD-verification. **Mitigation:** every
  child arc verifier-loop-verifies inherited counts at HEAD before
  citing them.
- **Sub-agent denominator disagreement without ground-truth grep.**
  Cat D Agent 3 said 913+97 = ~1,010; Agent 4 said 667; Agent 6
  said 478. Three sub-agents; three answers; no ground truth
  without parent-Claude verifier-loop grep. **Anti-pattern:** trust
  sub-agent counts without independent verification. **Mitigation:**
  parent Claude runs the definitive count grep + reconciles.
- **Sub-agent single-point-enforcement over-claim (Cat D Agent 2
  said "zero wrapper duplication + single point of auth
  enforcement"; missed 79 raw fetch bypass surfaced by Agents 3 +
  6).** Anti-pattern: sub-agents claim exhaustive coverage they
  cannot deliver. **Mitigation:** cross-check across agents;
  discrepancy is signal.
- **Sidebar logout backend-revoke gap missed by Cat C.** Cat C §7
  audited logout endpoints (backend view side); Cat D found the
  frontend caller side (Sidebar.tsx:356 does NOT call
  authApi.logout()). **Anti-pattern:** audit endpoint without
  auditing which callers invoke it. **Mitigation:** child scopes
  should explicitly enumerate caller sites of every endpoint.
- **Wrapper `pa_local.sh` requires per-cycle SIGN-pin swap + restore.**
  Rigby SIGN cycles need dedicated fresh isolation pin; wrapper
  hardcodes conversation ID at line 280. Every child cycle
  requires: (i) mint fresh pin; (ii) swap wrapper line 280 to
  fresh pin; (iii) run SIGN; (iv) retire pin; (v) restore wrapper
  line 280 to arc pin. **Manual dance; error-prone.** Recommend
  playbook v3 note + future runtime automation (out of scope for
  this xx99).

### 10.4 Suggestions for the playbook itself

- **§11.2 child-audit template §14 severity classification** —
  extend to allow severity annotations (e.g., "MED +
  ownership-drift-risk" per Cat D Rigby Q19 fold). Current strict
  {LOW / MEDIUM / HIGH / CRITICAL / UNKNOWN} enum is
  under-expressive for signals that don't warrant severity bump
  but do warrant explicit surfacing.
- **§11.2 §14 finding-type classification** — add
  "declared-fictional" as canonical class alongside existing
  {missing_connection, overcoupling, duplicate_model, event_gap,
  boundary_violation, circular_dependency, unclear_owner, drift,
  technical_debt, extraction_candidate, mature_primitive,
  dead_code, unknown} per Cat C Q4 fold introduction preserved by
  Cat D.
- **§14 verifier-loop discipline** — explicitly require
  parent-Claude verifier-loop to run definitive-count greps for
  any numeric claim any sub-agent makes. Would have caught the
  denominator ambiguity earlier + saved a verifier-loop cycle.
- **§15 dedicated fresh SIGN isolation pin discipline** — playbook
  should explicitly note the `tools/pa_local.sh` wrapper-swap
  dance + suggest future runtime automation (e.g.,
  `tools/pa_sign.sh` wrapper that accepts `--pin` arg).
- **§16 arc-pin preservation MC-14 threshold-check discipline
  (extended per Rigby SIGN Q2 fold — 2026-07-05).**
  Group 2400 close extends MC-14 CANDIDATE-threshold-satisfied to
  5-arc-stages (Group 2200 + Cat A + Cat B + Cat C + Cat D).
  **Proposed playbook §16 threshold rule:** 5 arc-stages =
  **provisional-confirmed**; codification-confirmation requires 1
  additional non-adjacent domain (e.g., payments/billing or
  content publishing) OR 2 more groups. 5 stages is strong
  evidence but not the final threshold unless §10.4 amendment
  ratifies. Preserves MC-14 as CANDIDATE at this xx99 close.
- **§11.3 §10 "next-arc-can-do-this" section (S2299 Q4
  suggestion carried forward).** Not adopted at this xx99; still
  recommended for S2599+ if load-bearing.

### 10.5 Suggestions for future canonical summaries (optional)

- **Consolidated numerical summary table in §3 domain shape.**
  Cat D's §3 table structure (Axis / Metric / Value) collapsed
  Cat A/B/C/D's numbers into one 20-row scanreable table. This xx99
  §3 preserves the format. Future canonical summaries with 4+
  children should adopt this pattern by default.
- **§5 resolved contradictions section** should be preserved as
  distinct from §4 cross-cutting patterns. §5 resolves disagreement
  (who was right / why); §4 identifies emergent themes only visible
  across children. Both worth keeping.
- **Cross-arc coordination flag roll-up single-tracking-unit
  discipline (Cat C Q11 fold + reinforced by Cat D CF-D3 extension).**
  When 4 arcs' flags roll up into one delegate arc (e.g., Group
  1700 Observability), track as single unit with sub-bullets to
  prevent 4-way duplicate handoff at delegate arc execution.
  Recommend §9 always applies this discipline for delegate arcs
  receiving ≥3 upstream flags.

---

## 11. Arc Change Log

Which child, which session, which Rigby verdict, which fold edits.

| Session | Child | Date | Rigby verdict | Fold count | Confidence | SIGN pin | Distinguishing property |
|---|---|---|---|---|---|---|---|
| **S2400** | Parent scoping | 2026-07-05 | SIGN-with-edits | 4 | Medium-High | `pa-32400781523b4d5b` (retired) | Playbook §11.1 20-section template TENTH application; MC-4 5th confirming arc candidate opened |
| **S2401** | P1 Cat A Authentication + Trust Boundaries | 2026-07-05 | SIGN-with-edits | 20 | MED 0.74 | `pa-f0b18d20dbc244ef` (retired) | F-BND-4 split via SIGN-cycle grep-verify (F-BND-4a CRITICAL + F-BND-4b HIGH; compound drift caught); §14.5 trust-boundary rate 3/2/9; §12 6 CANONICAL blockers |
| **S2402** | P2 Cat B Authorization + Permission-Floor | 2026-07-05 | SIGN-with-edits | 20 | MED-HIGH ~0.80 | `pa-d1d4c68981fc4b3c` (retired) | F-B-CRIT-2 silent-401 SYSTEMIC as necessary-enabling downstream symptom of F-B-CRIT-1 ~80-90% implicit-inheritance; §14.5 21-loci permission-floor rate; §19.1 three-option (a)/(b)/(c) decision space; introduced denominator-ambiguity Q20 fold |
| **S2403** | P3 Cat C Session Lifecycle + Logout Cleanup | 2026-07-05 | SIGN-with-edits | 32 | MED-HIGH ~0.82 | `pa-5096f5fc07754b18` (retired) | First arc to introduce four-class canonical-seam vocabulary (silent-swallow + contract-absent + declared-fictional + partial-contract); §14.2 15-surface × cleanup 1/3/11; §14.3 21-loci lifecycle-observability 5/5/11; §19.1 three-option (α)/(β)/(γ); introduced silent-degrade-vs-explicit-failure Q20 fold TRIGGER #1 |
| **S2404** | P4 Cat D Frontend Integration + Silent-401 SYSTEMIC | 2026-07-05 | SIGN-with-edits | 12 | MED-HIGH ~0.80-0.85 (HIGHEST child) | `pa-015448e962ad4038` (retired) | First arc to enumerate two-axis three-option decision space (α/β/γ × 2); first arc to identify option-γ as mechanism-vs-UX-policy composition (Rigby Q6 fold); first arc to enumerate governance-class non-silent-degrade findings alongside silent-degrade dominance; first arc to identify cross-arc flag as BLOCKING PREREQUISITE (Rigby Q18 fold); Q20 fold TRIGGER #2 CONFIRMED |
| **S2499** | xx99 Canonical Summary + Arc Close | 2026-07-05 | Pending | TBD | Pending | TBD (fresh minted) | ELEVENTH-consecutive §11.3 12-section application + §10 meta-methodology; ELEVENTH formal arc-pin retirement (`pa-6279ead1714c4630`); MC-4 5th confirming arc RESOLUTION (across-5-consecutive-arcs 1900+2000++2100+2200+2400) resolving S2199 Q3 STRENGTHEN dial-back |

**Arc totals:** 6 sessions (parent + 4 children + xx99) = runtime
target ACHIEVED per S2400 §5 (runtime cap 8 not invoked). 88 folds
landed across the arc pre-Chris-ratification (4 + 20 + 20 + 32 + 12
+ TBD xx99). 5 SIGN pins retired (parent + 4 children); xx99 will
retire SIGN pin #6. Arc pin `pa-6279ead1714c4630` PRESERVED through
all 5 sessions; RETIRED at this xx99 close (ELEVENTH formal arc-pin
retirement in Research OS).

---

## 12. Appendix — Provenance

**Files inspected (all HEAD-verified at `4e6c1ee8`):**

- Parent scoping: `docs/research/domains/auth/2400_auth_domain_scoping.md` (§5 acceptance criteria + §7 anti-scope + §3 child taxonomy + §3.5 auth-adjacent probes disposition + §7.1 leak-vector guardrails)
- Cat A: `docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md` (headline findings + §14.5 trust-boundary rate + §19 POSTURE-DECISION triad + §12 CANONICAL blockers)
- Cat B: `docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` (headline findings + §14.5 21-loci permission-floor rate + §19.1 three-option decision space (a)/(b)/(c))
- Cat C: `docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md` (headline findings + §14.2 15-surface × cleanup + §14.3 21-loci lifecycle-observability + §19.1 three-option (α)/(β)/(γ) + F-C-VIP-1 risk-gate constraint)
- Cat D: `docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md` (headline findings + §14.5 803-call-site classification + §19.1 α/β/γ × 2 decision spaces + §14.1 silent-degrade rate 17/19 89.5% + Q20 TRIGGER #2 CONFIRMED)
- Group 2200 canonical summary: `docs/research/domains/frontend/2299_frontend_canonical_summary.md` (T1 handoff bundle + §10 meta-methodology exemplar)
- Playbook: `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.3 12-section template + §11.3 §10 meta-methodology non-negotiable + §15 SIGN discipline + §16 arc-standard behavior)

**Grep patterns re-executed at HEAD `4e6c1ee8` (spot-checks; not exhaustive):**

Cat D §14.5 canonical figures re-confirmed at HEAD: 65
`@token_auth_required` across 10 files (64 uses / 9 view files
applied); 913 direct `api.<verb>()` across 21 files; 667 useQuery/
useMutation across 74 files; 79 raw fetch() across 31 files; 1
axios.create() instance at `frontend/src/lib/api.ts:13`; 0
`AxiosError | axios.isAxiosError` matches; 0 error boundaries; 0
`noAuthRedirect` flag adoption; 0 `Clear-Site-Data` emission in
`core/`; CODEOWNERS ABSENT at `.github/`, root, `docs/`.

**Rigby SIGN cycle 1 conversation record (executed 2026-07-05):**

- **Fresh isolation pin:** `pa-146fbdd1f1ca41e2` (minted at this xx99 SIGN open via `session_tool.create_fresh`)
- **Cadence:** single-batch × 4-Q (matches S1399-S2299 TEN-consecutive canonical-summary tested pattern; ELEVENTH-consecutive same-cadence application)
- **Verdict + confidence:** SIGN-WITH-EDITS at HIGH confidence ~0.88 (**highest confidence in Group 2400 arc**, exceeding Cat A 0.74 + Cat B ~0.80 + Cat C ~0.82 + Cat D ~0.80-0.85). Rigby explicit: "OK to close in cycle 1 — no cycle 2 headline fold-verification needed."
- **Tally:** 3 AGREE (Q1 + Q3 + Q4) + 1 STRENGTHEN (Q2) resulting in 4 fold operations (Q1 minor phrasing tightening + Q2 MC-4 resolution scope + MC-14 threshold clarification + Q3 conditional promotion rule + Q4 close-out confirmation).
- **Pin retirement:** at cycle 1 close via `session_tool.retire` — SIXTEENTH consecutive dedicated fresh SIGN pin retirement in Research OS after 10 xx99 + 1 parent-scoping-light-SIGN + Cat A + Cat B + Cat C + Cat D = 15 prior.

**Fold ledger:**

| # | Q ref | Section | Fold summary |
|---|---|---|---|
| 1 | Q1 AGREE + minor edit | §1 Executive Summary | Tightened "Mechanisms work correctly at file-precision level across every subsystem examined" → "Mechanisms generally work at file-precision in the sampled surfaces" (avoid absolute language; per §14.5 rate-table sampled coverage) |
| 2 | Q2 STRENGTHEN | §1 Executive Summary MC-4 paragraph | Added: "Resolution is methodological, not platform-state" clarification per Rigby fold — codification-confirmed with scope guardrails across 5 consecutive arcs including full-stack stress test in Auth, NOT "the platform's auth is fixed" |
| 3 | Q2 STRENGTHEN | §10.4 playbook suggestions | Extended §16 arc-pin preservation MC-14 threshold-check with proposed rule: 5 arc-stages = provisional-confirmed; codification-confirmation requires 1 additional non-adjacent domain OR 2 more groups. Preserves MC-14 as CANDIDATE at this xx99 close |
| 4 | Q3 AGREE + suggested edit | §10.2 codification candidate | Added conditional promotion rule: "promote to *general* silent-degrade codification if a 3rd trigger appears in a non-auth plane (Groups 2500/2600/1700)." Auth-failure-handling scope-bounding holds at this xx99 close |

**Arc pin retirement (this session):**

- `pa-6279ead1714c4630` MUST be retired at S2499 close via `session_tool.retire` per playbook §16 arc-close discipline
- ELEVENTH formal arc-pin retirement in Research OS after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200 prior ten
- `tools/pa_local.sh:280` requires downstream update to next-arc's fresh pin at Group 2500 API arc-open (T2 next per S2299 §8.2)

**Meta-methodology continuity:**

- ELEVENTH-consecutive playbook §11.3 §10 application (S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299 ten prior + this)
- ELEVENTH-consecutive playbook §11.3 12-section canonical-summary template application (same chain)
- MC-3 canonical-summary count extended to 11
- MC-5 §11.2 20-section child-audit template count at 16 (Cat D was §11.2 NINETEENTH-consecutive application; xx99 does NOT apply §11.2 — but Cat D closes MC-5 at 16 for the arc)
- MC-4 dial-back RESOLUTION at this xx99 close: 5th confirming arc across-5-consecutive-arcs (1900 + 2000+ + 2100 + 2200 + 2400) resolves S2199 Q3 STRENGTHEN dial-back per S2299 §5.3 formulation; Auth was materially different in scope (full auth stack, not a single UI surface family) — 5th-arc extension IS a validated stress test
- MC-10 codification-ready at 10-arc baseline (9 arcs of 20-Q child cadence + 6 arcs of parent-scoping-light-SIGN cadence + 11 arcs of canonical-summary cadence, minus overlap)
- MC-14 CANDIDATE-threshold-satisfied extended to 5-arc-stages (Group 2200 + Group 2400 Cat A + Cat B + Cat C + Cat D = 5 confirming arc-stages arc-pin-preservation-CHECKABLE §16 rule)

---

**End of S2499 Group 2400 Auth Canonical Summary.**
