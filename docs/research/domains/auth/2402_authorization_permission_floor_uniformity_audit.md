---
title: "Authorization + Permission-Floor Uniformity Audit (Group 2400 Cat B — S2402 P2)"
session: 2402
status: active (S2402 P2 Cat B second child audit under Group 2400 Auth — SEVENTEENTH-consecutive application of playbook §11.2 20-section child-audit template after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401 prior sixteen; drafted 2026-07-05 post-6-parallel-Explore-agent sweep + parent-Claude verifier-loop per playbook §14; **Rigby SIGN cycle 1 SIGN-with-edits at MED-HIGH confidence (~0.8) 2026-07-05 via dedicated fresh isolation pin `pa-d1d4c68981fc4b3c` retired at cycle close (updated_count=1, retired=true, previously_active=true — THIRTEENTH consecutive dedicated fresh SIGN pin retirement in Research OS); 4-batch × 5-Q = 20-Q cadence SEVENTH-consecutive application; 20 folds landed pre-Chris-ratification per §20.7 fold ledger. Chris "commit it" 2026-07-05 ratified 20-fold SIGN-with-edits wholesale; status flipped `draft` → `active` per playbook §16 draft-first workflow.** Arc pin `pa-6279ead1714c4630` PRESERVED per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails)
arc: Research Group 2400 (Auth — Session Lifecycle + Permission Floor + Silent-401 Resolution) — S2402 P2 Cat B second-child audit
category: research (playbook §11.2 20-section child-audit template SEVENTEENTH-consecutive application per S2401 handoff)
authors: Claude Code (S2402 draft 2026-07-05 post-6-parallel-Explore sweep + verifier-loop)
verifier_loop: >
  6 parallel Explore sub-agents run per playbook §13 (Agent 1 Models + Persistence,
  Agent 2 Services + Runtime Flows, Agent 3 APIs + Tools + Tasks + Commands,
  Agent 4 Integrations + Cross-Domain + Decision Space, Agent 5 Documentation +
  Prior Research, Agent 6 Drift + Debt + Ownership + Maturity). All 6 returned;
  parent-Claude verifier-loop per playbook §14 caught 5 sub-agent conflicts
  pre-draft:

  1. Agent 3 counted `OPTIONAL_AUTH_PATHS = 6`; direct read at HEAD `798399ec`
     `core/auth_middleware.py:521-538` + Cat A §3 canonical entry point table
     = **7 entries** (voice-marketplace, monitoring, deliverables,
     fleet/artifacts, fleet/events, fleet/signals, fleet/paid-interest).
     Parent verifier-loop confirmed 7 via `awk` slice-count. Corrected in §5
     + §14.5.

  2. Agent 3 claimed `/api/v1/admin/` and `/api/v1/metrics/admin/` are
     PHANTOM endpoints (middleware-only gate; no view registered). Parent
     verifier-loop grep-verified at HEAD `798399ec`:
     `path\(['\"]api/v1/admin/` — zero matches; `path\(['\"]api/v1/metrics/admin/`
     — zero matches; `/api/v1/system/reality-check/` present at
     `core/urls.py:3353` as sole `/api/v1/system/*` registration (lambda
     view returning JsonResponse). **CONFIRMED PHANTOM for 2 of 3
     STAFF_REQUIRED_PATHS entries.** Documented in §14 F-STAFF-1.

  3. Agent 6 cited `DEFAULT_PERMISSION_CLASSES` at `core/settings.py:230-231`;
     Agent 2 cited `core/settings.py:646-654`. Direct grep verifier-loop:
     `core/settings.py:652-653` reads
     `'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated']`
     within `REST_FRAMEWORK = {...}` dict starting at line 645. Agent 2
     line range correct; Agent 6 wrong. Corrected in §5.

  4. Agent 3 identified 2 `@permission_classes([])` sites; Agent 2 said
     "0 explicit empty" (searched only decorator form). Parent verifier-loop
     grep `@permission_classes\(\[\]\)|permission_classes\s*=\s*\[\]` at HEAD
     `798399ec` returned exactly **2 matches: `mythology/views.py:1167` +
     `mythology/views.py:1194`**. Documented in §14 F-EMPTY-1.

  5. Agent 3 estimated ~13 `@authentication_classes([])` sites across
     nervous/preferences/auth/freelance; parent verifier-loop grep confirmed
     **4 files** (`ai_core/api/freelance_api.py` +
     `core/views_preferences.py` + `core/auth_views_enhanced.py` +
     `core/views_nervous.py`). Total decorator-occurrence count TBD by Rigby
     SIGN cycle 1 batch (grep pattern ambiguity between decorator + class
     attribute); file-count of 4 CONFIRMED. Documented in §14 F-AUTH-EMPTY-1.

  Rigby SIGN cycle 1 pending via dedicated fresh SIGN pin (arc pin
  `pa-6279ead1714c4630` preserved separately per playbook §16 arc-standard
  behavior). Expected cadence: 4-batch × 5-Q = 20-Q per S2201-S2401
  six-consecutive tested child-audit pattern (SEVENTH-consecutive 20-Q
  cadence application candidate). SIGN-cycle-1 SIGN pin will be retired at
  cycle close via `session_tool.retire` per playbook §15 SIGN-isolation
  discipline (THIRTEENTH consecutive dedicated fresh SIGN pin retirement
  candidate in Research OS after 10 xx99 + 1 parent-scoping-light-SIGN + 1
  Cat A child audit + this cycle).
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                                # runtime counts anchor (URL_ROUTES 1,864 baseline; verified 1,866 at HEAD; no §Authorization autoblock — §2 F-INV-1 flags this)
  - docs/PLATFORM_WHAT_IT_IS.md                                               # narrative anchor (no §Authorization subsection — §2 F-INV-2 flags this)
  - docs/research/platform_architecture_inventory.md                          # S1273 32-domain map row 27 (PARTIAL + LIGHT after S1273 v2 review) — baseline shared with Cat A
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                 # process contract §11.2 SEVENTEENTH-consecutive application
  - docs/research/OPEN_ARCS.md                                                # arc manifest (Group 2400 In-progress row updated at S2402 open)
  - docs/research/domains/auth/2400_auth_domain_scoping.md                    # parent §3.B Cat B scope + §7.1 leak-vector guardrails + §2 evidence-provenance disclaimer
  - docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md  # Cat A — Cat B's PRIMARY load-bearing input (mechanism vocabulary via §5, path-list counts via §3, trust-boundary rate table via §14.5, findings F-CRIT-1/F-BND-4a/F-BND-4b/F-HIGH-2/F-HIGH-3/F-DEC-1/F-DUP-2 as constraint inheritance)
  - docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md   # §14.3 cockpit two-stage auth (MINOR-DRIFT) + §15.5 silent-401 systemic (Cat B references only)
  - docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md  # §14 F3 silent-401 SYSTEMIC ~630/1,300 baseline + §14 F3.5 whitelist BRITTLE + §19.1 R2 three-option decision space (Cat B extends)
  - docs/research/domains/frontend/2204_frontend_session_state_persistence_discipline_audit.md  # §14 F1 15-storage-surface + §19.1 R1 session lifecycle (Cat B references; Cat C S2403 owns)
  - docs/research/domains/frontend/2299_frontend_canonical_summary.md         # §8.2 T1 Group 2400 Auth handoff + §5.4 CF-1 permission-floor Cat B ownership + three-option decision space aggregation
  - docs/research/governance_authority_evolution.md                           # §2.5 36-45 primitives (adjacent authority DECISION plane — boundary preserved per §16 F-BND-0 inherited from Cat A)
  - core/auth_middleware.py                                                   # UnifiedTokenAuthenticationMiddleware (976 LOC) — HTTP auth surface + PUBLIC_PATHS + STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS registries
  - core/vip_middleware.py                                                    # VIPReadOnlyMiddleware (104 LOC) — HTTP HARD gate + VIP whitelists (11 read + 4 write + 3 cockpit = 18 entries)
  - core/services/fleet_auth_drf.py                                           # FleetSignatureAuthentication + FleetSignatureExclusiveAuthentication + FleetSignatureRequired + FleetCapabilityRequired (317 LOC)
  - core/views_public_intelligence.py                                         # PublicIntelTokenAuth custom DRF class
  - core/settings.py                                                          # DEFAULT_PERMISSION_CLASSES + DEFAULT_AUTHENTICATION_CLASSES (lines 646-654)
  - core/epa_handlers_tools.py                                                # WORKSPACE_AWARE_AGENTS constant (20 agents) — workspace-membership implicit permission gate
  - core/services/tool_dispatcher.py                                          # PA tool authorization plane (auth-agnostic dispatcher)
  - mythology/views.py                                                        # F-EMPTY-1: 2 sites with @permission_classes([]) (lines 1167, 1194)
delegated_from:
  - S2400 parent scoping §3.B Cat B expected outputs (a-e) + §7.1 Cat B leak-vector guardrails (MEASURE-CLASSIFY-RECOMMEND framing; NOT authoring registry) + §2 evidence-provenance disclaimer
  - S2401 Cat A §5 mechanism inventory (12-mechanism × 3-gate-type matrix) + §14 findings (F-CRIT-1 PURGE_SECRET, F-BND-4a bet-placement unauth-write, F-BND-4b reviewer inversion, F-HIGH-2 WS dead-code, F-HIGH-3 PUBLIC_PATHS accretion, F-DEC-1 decorator drift, F-DUP-2 role-field bifurcation) + §14.5 trust-boundary rate table + §17 F-DUP-2 role-field bifurcation
  - S2203 §14 F3 silent-401 SYSTEMIC (~630/1,300 baseline) + §14 F3.5 whitelist BRITTLE + §19.1 R2 three-option decision space + A3 ~40% permission-untraced-rate sample (20 endpoints)
  - S1273 v2 §3.27 baseline (row 27 Auth / Permissions / Security PARTIAL + LIGHT) — inherited via Cat A revision (~108 → 265 PUBLIC_PATHS drift confirmed)
  - Group 2200 T1 handoff bundle (S2299 §8.2 T1 aggregation — silent-401 + logout cleanup + session lifecycle + permission-floor uniformity)
delegates_to:
  - S2403 P3 Cat C Session Lifecycle + Logout Cleanup Contract — Cat C consumes §14 F-B7 workspace-membership implicit-gate finding + §14 F-DUP-2 role-field bifurcation lifecycle implications + §18 ownership gap #4 (STAFF/REVIEWER list ownership)
  - S2404 P4 Cat D Frontend Integration + Silent-401 SYSTEMIC — Cat D consumes §7 runtime-flow-per-caller-class + §14.5 permission-floor rate + §19.1 three-option decision space (Cat B recommends option (b) split-read/write with option (c) registry as design-prep secondary; Cat D tailors silent-401 audit scope per Cat B lean)
  - S2499 xx99 canonical summary — POSTURE-DECISION evidence plan §19.1 three-option decision space + cross-arc coordination flags CF-B1 → CF-B5 + §19.4 anchor-update recommendations + §10 meta-methodology
  - Group 2500 API (design-prep for per-endpoint permission registry) — Cat B CF-B1 delivers evidence + optional schema proposal; Group 2500 authors per-endpoint registry IF Chris D-verdict selects option (c)
  - Group 2600 PA (workspace-context authorization plane) — Cat B CF-B2 flags workspace-membership implicit-gate + PA tool authorization plane (auth-agnostic dispatcher; user-scoped, no is_staff gate on tools)
head_commit_before: 798399ec
arc_pin: pa-6279ead1714c4630 (PRESERVED through S2402 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails — ELEVENTH formal arc pin under Research OS; retirement at S2499 close; MC-14 CANDIDATE-threshold-satisfied 2-arc arc-pin-preservation-CHECKABLE §16 rule extended to 3+arcs via Group 2200 + Group 2400 Cat A + Group 2400 Cat B = 3 confirming arc-stages post-S2402 close)
sign_pin: pa-d1d4c68981fc4b3c (RETIRED at S2402 SIGN cycle 1 close 2026-07-05 via `session_tool.retire` per playbook §15 SIGN-isolation discipline — THIRTEENTH consecutive dedicated fresh SIGN pin retirement in Research OS after 10 xx99 + 1 parent-scoping-light-SIGN + 1 Cat A child audit + this cycle)
scope_shape:
  central_child_B_lens: >
    "Does the platform have an explicit per-endpoint permission-floor
    contract (with declared permission-class + observable-untraced-rate)
    OR is authorization accreted through implicit inheritance +
    middleware-path-list gates with no per-endpoint registry?"
  B_output_a: gated endpoint inventory — permission-floor cell per endpoint across ~1,866 path() surface (HEAD-verified count; census extends PLATFORM_INVENTORY ~1,864 baseline)
  B_output_b: permission-untraced-rate extension — S2203 A3 sampled 20 endpoints ~40% permission-untraced rate → whole-platform measurement across full path() surface
  B_output_c: STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS + REVIEWER_ALLOWED_PATHS registry audit + drift candidates (F-STAFF-1 phantom endpoints + F-BND-4a/4b Cat A inversion re-verified)
  B_output_d: three-option decision space evidence table + Chris-D-verdict-request (options: (a) uniform IsAuthenticated across all /v1/** + client-side auth-gate + observable-error surfacing; (b) uniform AllowAny for read paths + IsAuthenticated for writes + client-side auth-check-on-write; (c) per-endpoint permission registry)
  B_output_e: cross-arc coordination flags (CF-B1 → Group 2500 API per-endpoint registry as design-preparation candidate; CF-B2 → Group 2600 PA workspace-context authorization plane; CF-B3 → Group 2200 post-arc Cat D silent-401 severity input; CF-B4 → Group 2400 arc VIP demo authorization-plane pattern; CF-B5 → Group 1700 Observability auth event streaming + permission-floor smoke-test coverage)
provenance:
  - S2402 draft written 2026-07-05 post-S2401 Cat A close (Chris "commit it" ratified 2026-07-05 PR #2910)
  - 6 parallel Explore sub-agents run per playbook §13 (Agent 1-6 per §3.B Cat B expected outputs)
  - Parent-Claude verifier-loop per playbook §14 caught 5 sub-agent conflicts pre-draft (see verifier_loop field above): OPTIONAL_AUTH_PATHS undercount (6→7), phantom STAFF_REQUIRED endpoints (2 of 3 confirmed), DEFAULT_PERMISSION_CLASSES line-anchor mismatch, @permission_classes([]) precise-site count (2 confirmed), @authentication_classes([]) file-count (4 confirmed vs Agent 3 estimate)
  - HEAD-verified counts via grep/read: `path()` census 1,866 (1,794 core/urls.py + 44 urls_unified + 19 urls_provenance + 9 urls_real_data) + middleware gate registries (PUBLIC_PATHS=265, PUBLIC_PATHS_EXACT=2, OPTIONAL_AUTH_PATHS=7, STAFF_REQUIRED_PATHS=3 with 2 phantom, REVIEWER_BLOCKED_PATHS=12, REVIEWER_ALLOWED_PATHS=1 = 290 total gate entries) + DRF permission-class landscape (3 custom classes + IsAuthenticated default + ~686 @permission_classes occurrences across 73 files with explicit decorators + ~1200 views without decorator inheriting default) + F-EMPTY-1 sites (mythology/views.py:1167 + 1194) + F-AUTH-EMPTY-1 files (4)
  - Chris ratification pending post-Rigby-SIGN-cycle-1 close-card
owner: claude (drafted S2402; Rigby SIGN cycle 1 folds land pre-commit; Chris ratification via close-card)
---

# Session 2402 — Group 2400 Cat B — Authorization + Permission-Floor Uniformity Audit

> **Static snapshot.** This audit captures the authorization surface + permission-floor
> uniformity at HEAD `798399ec` on `main` (2026-07-05, LOCAL). It is a photograph
> per Cat B measure/classify/recommend contract, not a per-endpoint registry
> authoring output. Cat A (S2401) delivered mechanism vocabulary + trust-boundary
> rate table. Cat C (S2403) will own session lifecycle + logout cleanup contract.
> Cat D (S2404) will own frontend integration + silent-401 execution surface. This
> document delivers what parent §3.B Cat B required: (a) gated endpoint inventory
> across ~1,866 path() surface with permission-floor classification; (b) permission-
> untraced-rate extension from S2203 A3 20-sample to whole-platform measurement;
> (c) STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS + REVIEWER_ALLOWED_PATHS registry
> drift audit + F-STAFF-1 phantom-endpoint finding; (d) three-option decision space
> evidence table + Cat B recommendation lean (option (b) split-read-write with
> option (c) registry as design-prep secondary) + Chris D-verdict-request; (e)
> cross-arc coordination flags CF-B1 → CF-B5.

> **Evidence-provenance discipline (inherited from S2400 §2 disclaimer +
> reinforced by Cat A verifier-loop).** Every load-bearing claim is either (a)
> HEAD-verified via direct file read + Django-ORM-adjacent grep at `798399ec`, or
> (b) marked ESTIMATE (inherited from S2203 A3 baseline or S2401 Cat A baseline
> pending Cat B re-verification), or (c) marked SPECULATIVE with explicit
> rationale. Sub-agent claims verified per playbook §14 "trust but verify" — 5
> conflicts caught + resolved pre-draft (see frontmatter `verifier_loop`).

> **Cat B mission framing (parent §7.1 leak-vector guardrail).** MEASURE (extend
> S2203 A3 20-endpoint sample across full path() surface), CLASSIFY (per-endpoint
> permission-floor cell + declared-permission-class + middleware-path-gate +
> implicit-inheritance flag), and RECOMMEND a lean across three-option decision
> space. Cat B does NOT design or author the per-endpoint registry itself —
> registry design + authoring is Group 2500 API scope. Anti-scope #1 preserved.
> Explicit anti-pattern flagged: Cat B produces recommendation-as-lean + evidence
> table, NOT "recommended permission-floor mapping table" that reads as a
> de-facto registry authoring deliverable.

---

## 1. Executive Summary

**Central Cat B lens answer.** The platform's authorization surface at HEAD `798399ec`
is **structurally intentional at the DRF-permission-class layer** (`IsAuthenticated`
enforced as `DEFAULT_PERMISSION_CLASSES` at `core/settings.py:652-653`; 3 custom
DRF permission classes at `core/services/fleet_auth_drf.py` + `core/views_public_intelligence.py`
with fail-closed contracts; 686 `@permission_classes` decorator occurrences across
73 files) but **structurally accreted at the per-endpoint-registry layer** (~1,866
`path()` endpoints; 265 in PUBLIC_PATHS + 3 in STAFF_REQUIRED_PATHS with 2 phantom
+ 12 in REVIEWER_BLOCKED_PATHS + 1 in REVIEWER_ALLOWED_PATHS + 7 in OPTIONAL_AUTH_PATHS
+ 2 in PUBLIC_PATHS_EXACT = 290 gate entries). **A third plane exacerbates the
accretion:** the middleware-path registries themselves function as a
**shadow per-endpoint registry** (PUBLIC_PATHS + REVIEWER_BLOCKED + STAFF_REQUIRED
+ OPTIONAL_AUTH_PATHS as de-facto authorization declarations at HTTP layer, not
DRF layer) — the accreted registry EXISTS, but it's split across middleware
lists + urls.py registrations + scattered per-view decorators without unified
source-of-truth (Rigby SIGN cycle 1 Q1 fold 2026-07-05). **Implicit-inheritance
rate estimate**: measurement bounded — decorator-only grep at HEAD counts 686
occurrences across 73 files; extrapolating to endpoint-level requires including
class-attribute-style declarations (`permission_classes = [...]` on ViewSet
classes / mixins) which decorator-only grep misses (Rigby SIGN cycle 1 Q2 + Q5
fold — measurement discipline). **Headline ESTIMATE: ~80-90% implicit inheritance
at endpoint level** (bounded by decorator-only vs class-attribute measurement
ambiguity); tightening to precise whole-platform rate requires per-ViewSet-class
audit (deferred to Group 2500 API arc if option (c) registry selected). S2203 A3
20-endpoint sample ~40% permission-untraced-rate CONFIRMED-directionally at
whole-platform scale. This audit is the first single-source-of-truth per-endpoint
permission-floor enumeration attempt across the whole platform.

**Central Cat B finding — S2203 A3 baseline is STRUCTURALLY-CONFIRMED at HEAD;
whole-platform implicit-inheritance rate is HIGHER than S2203 A3 permission-untraced
estimate:**

1. **Permission-untraced-rate (S2203 A3 baseline ~40% of 20 endpoints) →
   HEAD implicit-inheritance-rate ~80-90% ESTIMATE of ~1,866 endpoints (Rigby
   SIGN cycle 1 Q2 fold — bounded range with denominator provenance).**
   These are two DIFFERENT metrics measuring adjacent phenomena. **S2203 A3
   "permission-untraced"** = grep cannot find explicit permission floor for
   sampled endpoint (view file not indexed, decorator not present, or
   permission class inherited from unclear ancestor). **Cat B "implicit-
   inheritance"** = view function has NO explicit `@permission_classes`
   decorator; permission floor comes from DEFAULT_PERMISSION_CLASSES
   (`IsAuthenticated`). Both metrics indicate the same underlying condition
   (permission-floor is not per-endpoint declared), but S2203 A3 measured
   trace-ability; Cat B measures declaration-ability. **Measurement provenance
   disclosure (Rigby SIGN cycle 1 Q5 fold):** Cat B's decorator-only grep
   OVERSTATES "implicit" because many DRF views declare permission floors via
   class attributes (`permission_classes = [...]` on ViewSet classes) or via
   ViewSet-default/mixin inheritance which decorator-only grep misses.
   Denominator ambiguity: 1,866 `path()` endpoints vs ~1,932 view functions
   (~65% decorator-less view-function count from Agent 2) vs ~1,576 endpoints
   (~84.4% if all decorator-less endpoints inherit DEFAULT). The **~80-90%
   ESTIMATE bounded range** reflects this ambiguity; exact rate requires
   per-ViewSet-class audit (deferred to Group 2500 API arc if option (c)
   registry selected). See §20.5 emerging-weak-spot pattern.

2. **STAFF_REQUIRED_PATHS PHANTOM-endpoint drift (F-STAFF-1 NEW at Cat B):**
   2 of 3 STAFF_REQUIRED_PATHS entries have no view registration at HEAD:
   `/api/v1/admin/` and `/api/v1/metrics/admin/` return middleware-403 to
   any non-staff user but there is no view to serve staff either. Grep-
   verified at HEAD `798399ec`: `path\(['\"]api/v1/admin/` = 0 matches;
   `path\(['\"]api/v1/metrics/admin/` = 0 matches. Only `/api/v1/system/`
   has any registration — `/api/v1/system/reality-check/` at `core/urls.py:3353`
   (lambda view returning JsonResponse). **The STAFF_REQUIRED_PATHS registry
   is aspirational** — it protects "would-be admin endpoints" that don't
   exist. Class: `dead_code` + `drift`. Severity: MED (defensive-in-depth
   posture is fine, but registry is not enforcing on real surface).

3. **F-BND-4a + F-BND-4b (Cat A CRITICAL + HIGH) re-verified at Cat B
   HEAD:** `/api/v1/betting/place/` remains dual-registered at
   `core/auth_middleware.py:198` (PUBLIC_PATHS anonymous bypass — comment
   "Session 563: Bet Tracking (allow anonymous for demo mode)") AND
   `core/auth_middleware.py:550` (REVIEWER_BLOCKED_PATHS). Cat A's
   observation of anon-can-bet-reviewers-cannot inversion is INTACT. Cat B
   adds: this is a DIRECT EVIDENCE POINT for the three-option decision-space
   evaluation — option (b) split-read-write with client-side auth-gate is
   the LOWEST-COST resolution (BettingPage component gates writes on auth
   state + reviewer role visibility; server continues to allow anon in
   demo-mode context). Option (a) uniform `IsAuthenticated` requires
   breaking demo-mode bet-placement UX. Option (c) registry captures the
   dual-classification as `{demo_mode_allowed: true, reviewer_blocked: true,
   conflict: 'F-BND-4b_ACTIVE'}` metadata.

**Cat B acceptance criterion scoring (per S2400 header block):**

| Criterion | Status | Evidence |
|---|---|---|
| #1 Permission-floor observability | **PARTIAL — MEASURED but not yet REGISTRY** | Cat B delivers per-endpoint classification framework via §14.5 permission-floor cell rate table + §6 endpoint sample inventory + §14 findings; xx99 escalation to Chris D-verdict on option (a)/(b)/(c) registry choice determines whether observability graduates to WORKING |
| #2 Failure surfacing / typed error envelope | DEFERRED to Cat D | Cat D S2404 owns api.ts:48-56 audit; Cat B confirms Session 1171 503-fork stays isolated to token validation (does NOT extend to DRF permission-class dispatch — DRF DB errors propagate uncaught to Django error handler) |
| #3 Logout cleanup contract | DEFERRED to Cat C | Cat C S2403 owns 15-surface cleanup table; Cat B references AssistantProfile.role + platform_role bifurcation from Cat A §17 F-DUP-2 as session-lifecycle implication |
| #4 Session lifecycle discipline | DEFERRED to Cat C | Cat C S2403 owns session-model inventory; Cat B references DRF token expiry (Cat A F-TOKEN-1 no-expiry) as background |
| #5 Cross-arc coordination flags preserved | **WORKING** | Cat B emits 5 flags (CF-B1 → CF-B5 in §19.3); combined with Cat A's 7 flags (CF-1 → CF-7), total 12 flags across Cat A + Cat B for xx99 §5.4 consolidation (well above ≥ 2 acceptance floor) |
| #6 Trust boundary inventory explicit + testable | **CARRY-OVER PARTIAL from Cat A** | Cat A §14.5 rate table stands (14 mechanisms; 3 PRESENT + 2 PARTIAL + 9 ABSENT smoke-test coverage); Cat B EXTENDS with permission-floor cell coverage (see §14.5 Cat B extension table) — same PARTIAL classification carries forward pending post-arc smoke-test authoring |

**Cat B seven headline findings:**

- **F-B-CRIT-1 — Permission-floor implicit-inheritance rate ~84%
  (whole-platform).** ~1,576 of ~1,866 endpoints (~84.4%) have no explicit
  `@permission_classes` decorator; permission floor inherited from
  `DEFAULT_PERMISSION_CLASSES = ['rest_framework.permissions.IsAuthenticated']`
  at `core/settings.py:652-653`. This is a HIGHER rate than S2203 A3's
  ~40% permission-untraced sample because Cat B measures declaration-
  ability (superset) while S2203 A3 measured trace-ability (subset). The
  base rate itself is not a bug — DRF default IS `IsAuthenticated` and
  most endpoints are correctly authenticated-required. But: (i) permission
  floor is not per-endpoint OBSERVABLE (grep can't find it; requires
  DRF-runtime introspection); (ii) refactoring DEFAULT_PERMISSION_CLASSES
  would silently break ~1,576 endpoints; (iii) endpoint intent (public /
  authenticated / admin) is NOT captured in code near the endpoint — it's
  implicit in urls.py registration + DEFAULT. **Class:
  `technical_debt` + `missing_connection`.** Severity: **CRITICAL** for
  observability; **LOW** for correctness (endpoints work correctly, just
  not declarably). Blocker to acceptance criterion #1 unless per-endpoint
  registry (option (c)) is adopted OR explicit-decorator discipline is
  enforced (option (a) extension).

- **F-B-CRIT-2 — S2203 §14 F3 silent-401 SYSTEMIC finding is a
  DOWNSTREAM SYMPTOM of F-B-CRIT-1 permission-floor unobservability.**
  Frontend `api.ts:48-56` swallows 401 silently because it has no
  per-endpoint permission-floor knowledge to decide "was this a valid
  auth-required attempt or an unauth-optional attempt?" Silent-401
  fallback is a rational frontend response given the ambiguity. **Rigby
  SIGN cycle 1 Q3 fold (causal-chain refinement):** the connection between
  F-B-CRIT-1 and F-B-CRIT-2 is directional but NOT a strict implication.
  Silent-401 has INDEPENDENT contributors (generic global interceptor
  choices, token-expiry handling, retry logic, CSRF/session edge cases,
  network errors mapped to 401-like UX). Correct framing: **F-B-CRIT-1
  is a NECESSARY ENABLING CONDITION to CORRECTLY fix F-B-CRIT-2 at scale**
  — without per-endpoint permission-floor knowledge, Cat D can only patch
  heuristics; with it, Cat D can gate intelligently. Option (b)
  split-read-write is a MINIMUM intervention that addresses the observable
  outcome without full per-endpoint registry. **Class: `drift` (systemic).**
  Severity: **CRITICAL** in aggregate with F-B-CRIT-1; DEFERRED to Cat D
  S2404 for tactical remediation design. Blocker to acceptance criterion
  #2.

- **F-B-HIGH-1 — STAFF_REQUIRED_PATHS 2-of-3 PHANTOM entries (F-STAFF-1
  NEW at Cat B):** `/api/v1/admin/` and `/api/v1/metrics/admin/` have no
  view registration at HEAD. Grep-verified. Only `/api/v1/system/reality-check/`
  (lambda view at `core/urls.py:3353`) exists on the `/api/v1/system/*`
  namespace. Middleware STAFF_REQUIRED_PATHS check enforces at
  `core/auth_middleware.py:610-613` (session-auth path) + `:661-664`
  (token-auth path); a non-staff request to `/api/v1/admin/` gets 403
  from middleware without ever reaching a view resolver. A staff request
  gets 403-then-404 (middleware passes; URL resolver fails). Defensive-
  in-depth posture is fine, but the registry is enforcing on a phantom
  surface — 2 of 3 entries protect nothing runtime-real. **Class:
  `dead_code` + `drift`.** Severity: **MED** (correctness OK; misleading
  configuration). Post-arc recommendation candidate: remove phantom
  entries OR add explicit `/api/v1/admin/index/` health-check view to
  ratify the namespace protection intent.

- **F-B-HIGH-2 — REVIEWER_BLOCKED_PATHS `/api/v1/betting/place/` PUBLIC
  + REVIEWER-BLOCKED inversion INTACT at Cat B HEAD (Cat A F-BND-4a +
  F-BND-4b RE-VERIFIED):** `/api/v1/betting/place/` at
  `core/auth_middleware.py:198` (PUBLIC_PATHS) AND `:550`
  (REVIEWER_BLOCKED_PATHS). Cat B extends Cat A finding with authorization-
  plane framing: this inversion is a DIRECT EVIDENCE POINT for the
  three-option decision-space evaluation. Cat B recommendation (see §19.1):
  option (b) split-read-write with client-side auth-gate resolves this
  inversion at LOWEST cost (server keeps demo-mode anon-write compatibility;
  frontend BettingPage gates on `useAuthStore().token` for write UI +
  hides bet button for reviewer role). **Class: `boundary_violation` +
  `dead_code` (REVIEWER_BLOCKED_PATHS entry is inert if PUBLIC_PATHS
  bypasses auth middleware entirely — reviewer never gets to the block
  gate).** Severity: **CRITICAL** for F-BND-4a (unauth write) preserved
  from Cat A; Cat B adds inversion classification as authorization-plane
  finding. Post-arc P0 remediation candidate per Cat A §19.2 rank-1
  co-equal P0 batch.

- **F-B-HIGH-3 — Workspace-membership as implicit permission gate
  (workspace-scoping via `AssistantProfile.workspace` FK +
  `WORKSPACE_AWARE_AGENTS` constant):** `core/epa_handlers_tools.py`
  defines `WORKSPACE_AWARE_AGENTS` (20 agent names). Agent dispatch at
  the epa-handler layer checks `if agent_name in WORKSPACE_AWARE_AGENTS
  and write_to_workspace:` then calls `execute_with_workspace()`.
  Workspace-MEMBERSHIP enforcement happens downstream in that method
  (NOT audited by Cat B — outside scope per parent §7.1 anti-scope PA
  behavior spec). At the API layer: PA endpoints receive `workspace_id`
  in payload; no DRF permission-class check enforces workspace-membership.
  Workspace-scoping is an IMPLICIT authorization-plane gate — it's a
  correctness contract encoded in service layer, not observable at HTTP
  layer. **Class: `missing_connection` + `unclear_owner`.** Severity:
  **HIGH** if PA dispatch relies on caller to pass correct `workspace_id`
  without server-side membership verification (workspace-scoping is
  reader's trust); **MED** if `PAContextResolver` (Group 2600 owns)
  enforces at service layer. Cat B cannot audit PA internals; flags as
  **CF-B2** for Group 2600 PA arc ownership.

- **F-B-HIGH-4 — `@authentication_classes([])` sites (4 files) create
  DRF-contract-vs-middleware-contract confusion:** grep-verified 4 files
  at HEAD `798399ec`: `ai_core/api/freelance_api.py`,
  `core/views_preferences.py`, `core/auth_views_enhanced.py`,
  `core/views_nervous.py`. These views explicitly turn OFF DRF
  authentication_classes. The intent (varying per file):
  (i) `views_nervous.py` — body-system monitoring endpoints; explicit
  opt-out for operational resilience (health checks work even if auth
  backend is down); IN PUBLIC_PATHS anyway;
  (ii) `views_preferences.py` — user preference endpoints; conflict
  detected in some declarations paired with `@permission_classes(
  [IsAuthenticated])`;
  (iii) `auth_views_enhanced.py` — auth signup/login endpoints; intentional;
  (iv) `freelance_api.py` — freelance marketplace; intentional anon-browse
  + auth-submit.
  When `@authentication_classes([])` is stacked with
  `@permission_classes([IsAuthenticated])` (as in `views_preferences.py`),
  the DRF contract is confused: DRF auth doesn't run, so
  `request.user = AnonymousUser` unless middleware set it. Middleware DOES
  set `request.user` (from token or session) at
  `core/auth_middleware.py:676`, so the mismatch is MASKED by middleware
  precedence. **The stacking works BY ACCIDENT via middleware ordering, not
  by DRF contract.** **Class: `drift` + `technical_debt`.** Severity:
  **HIGH** — if middleware ordering changes, `views_preferences.py`
  breaks silently. Post-arc consolidation candidate: either use
  `@authentication_classes([TokenAuthentication, SessionAuthentication])`
  matching middleware behavior, OR document the middleware-precedence
  contract explicitly.

- **F-B-MED-1 — `@permission_classes([])` explicit-empty sites (2 sites,
  both in `mythology/views.py`):** grep-verified at `mythology/views.py:1167`
  + `:1194`. Both are read-only mythology patterns/guards endpoints
  intended for visualization; both are inside PUBLIC_PATHS already
  (middleware bypasses auth entirely for `/api/mythology/*`). Explicit
  empty declaration is REDUNDANT (middleware already allows through), but
  it's not currently dangerous — data is non-sensitive visualization.
  **Risk profile**: pattern is error-prone; if either endpoint accidentally
  receives write capabilities in future, empty permission class would
  silently allow unauthenticated writes. **Class: `drift` (minor).**
  Severity: **MED** (near-term LOW; long-term MED as pattern-precedent
  risk). Post-arc cleanup candidate.

**Cat B canonical-seam application (extending S2400 §2.4 + Cat A §1
observation; Rigby SIGN cycle 1 Q4 fold — DRF-default correctness-vs-
observability clarification):** "Defaults that silently swallow failure
vs contracts that surface failure" partitions Cat B findings cleanly:

- **Silent-swallow class:** F-B-CRIT-1 (implicit inheritance is silent —
  no code declares the floor), F-B-CRIT-2 (silent-401 is the downstream
  symptom), F-B-HIGH-1 (STAFF phantom entries silently protect nothing),
  F-B-HIGH-3 (workspace-membership is silent contract), F-B-MED-1 (empty
  permission class silently allows).

- **Contract-that-surfaces-failure (correctness) class:** DRF
  `IsAuthenticated` default (surfaces 403 on unauth — CORRECTNESS
  contract, NOT AUTOMATICALLY an observability/surfacing contract unless
  paired with explicit endpoint declaration + typed error surfacing per
  Rigby Q4 fold), Fleet `FleetSignatureRequired` + `FleetCapabilityRequired`
  (surfaces 403 on missing identity/capability — both correctness AND
  observability contract via structured DenyCode error dicts), Cat A
  F-BND-4a-remediation-candidate.

- **Partial-contract class:** F-B-HIGH-2 F-BND-4a inversion (PUBLIC bypass
  is contract-surface — comment "allow anonymous for demo mode" — but
  REVIEWER_BLOCKED_PATHS entry is silent-inert; contract exists, enforcement
  is dead code).

- **Confused-contract class:** F-B-HIGH-4 `@authentication_classes([])`
  + `@permission_classes([IsAuthenticated])` stacking (textbook
  confused-contract per Rigby Q4 fold) — works by middleware-precedence
  accident, not DRF contract; contract-shape is unclear.

Xx99 §4 will consolidate these across Cat A + Cat B + Cat C + Cat D.

**Cat B recommendation lean (for Chris D-verdict per §19.1; Rigby SIGN
cycle 1 Q16 fold — (b)/(c) stabilization-vs-end-state framing):**
Option **(b) uniform AllowAny for reads + IsAuthenticated for writes +
client-side auth-check-on-write** as **PRIMARY RECOMMENDATION FOR
REMEDIATION WINDOW (stabilization step)** — near-term symmetry with
smaller blast radius; preserves demo UX; addresses observable silent-401
symptom. Option **(c) per-endpoint permission registry** as **PRIMARY
RECOMMENDATION FOR LONG-TERM GOVERNANCE (inevitable convergence target)**
— design-prep now for Group 2500 API arc; implement later. Option (b) is
NOT the end-state; option (c) is where the platform should converge.
Sequencing this way dodges the "why aren't you choosing the real fix?"
critique. Rationale (full analysis
§19.1): (i) option (b) blast radius smaller (~50-80 write paths vs 265
PUBLIC_PATHS reclassification); (ii) reversibility easier (feature-flag
toggleable at frontend component layer); (iii) compatible with Cat A
F-CRIT-1 + F-BND-4a as post-arc remediation (not blocking); (iv) directly
addresses F-B-CRIT-2 silent-401 SYSTEMIC because frontend has actionable
permission model to gate writes; (v) option (c) registry preserves
long-term governance option without Cat B implementation risk. **Chris
D-verdict-request** on which option ships (with option (c) available as
Group 2500 design-prep track regardless of (a)/(b) choice).

## 2. Domain Purpose

**Q1 — What is this Cat B audit for? (one-sentence purpose):** Enumerate
the platform's authorization surface + per-endpoint permission-floor
uniformity at static snapshot, extending S2203 A3 20-endpoint sample
~40% permission-untraced-rate baseline to whole-platform ~1,866 `path()`
surface with per-endpoint permission-floor classification cell, and
delivering three-option decision space evidence + Cat B recommendation
lean for Chris D-verdict on authorization-plane uniformity path.

**Q2 — What problem does it solve? (business / platform problem):**
Prior arcs (Groups 1300-2200 + Group 2400 Cat A) established mechanism
vocabulary (Cat A §5: 12 auth mechanisms + 14 gate-mechanism rate table
per §14.5) but did NOT enumerate per-endpoint permission-floor across
the ~1,866-endpoint surface. S2203 A3 sampled 20 endpoints and found
~40% permission-untraced (grep couldn't find explicit permission floor);
S2203 §19.1 R2 recorded a three-option decision space and deferred
resolution to "Group 2400 Auth or downstream API arc." S2200 xx99 §5.4
Flag #1 explicitly assigned permission-floor uniformity ownership to
Cat B S2402. This audit closes that ownership: measures the
implicit-inheritance rate at whole-platform scale (~84.4% at HEAD);
verifies Cat A findings F-BND-4a/4b + F-STAFF-1 phantom entries + Fleet
permissive drift potential + F-DUP-2 role-field bifurcation lifecycle;
and delivers Chris-D-verdict-request package with three-option decision
space evidence per option.

**Q3 — What does the Cat B audit NOT do? (anti-scope alignment):**

- No fixes / no PRs — read-only research per playbook §14 no-implementation-
  during-research.
- No per-endpoint permission registry AUTHORING — Cat B scope is
  MEASURE-CLASSIFY-RECOMMEND per parent §7.1 leak-vector guardrail; if
  Chris D-verdict selects option (c), Group 2500 API arc authors the
  registry.
- No frontend api.ts audit (Cat D S2404 scope) — Cat B references F3
  silent-401 SYSTEMIC as symptom-of-F-B-CRIT-1 but does not audit
  api.ts:48-56 interceptor logic or per-caller-site silent-401 blast
  radius.
- No session-model authoring (Cat C S2403 + parent §7 anti-scope #5) —
  Cat B references DRF `authtoken.Token` no-expiry (Cat A §14 F-TOKEN-1)
  + role-field bifurcation lifecycle (Cat A §17 F-DUP-2) as background;
  Cat C recommends session-model lean.
- No threat-model authoring (Cat A anti-scope #5 preserved) — Cat B
  emits POSTURE-DECISION on three-option decision space; threat-model
  authoring stays post-arc ADR track if Chris ratifies.
- No PA behavior spec authoring (Group 2600 scope) — F-B-HIGH-3
  workspace-membership implicit-gate flagged for CF-B2 Group 2600
  ownership.
- No new auth provider additions (SSO/OAuth) — parent §7 anti-scope #6.
- No Group 1900 authority-plane crossings — §16 F-BND-0 preserved from
  Cat A (authority DECISION plane distinct from authorization
  ENFORCEMENT plane).

---

## 3. Canonical Entry Points

HEAD-verified file:line anchors at `798399ec`. Line references are static
snapshots. Cat A §3 canonical entry points table for the mechanism-declaration
layer is INHERITED; Cat B extends the entry-point inventory to the
authorization-plane loci (DRF permission classes + workspace-scoping +
tool-dispatcher authorization + WebSocket consumer authorization).

**DRF DEFAULT_PERMISSION_CLASSES + DEFAULT_AUTHENTICATION_CLASSES (global
policy locus):**

| Entry Point | File:Line | Purpose |
|---|---|---|
| `REST_FRAMEWORK` config dict | `core/settings.py:645-664` | Global DRF policy |
| `DEFAULT_AUTHENTICATION_CLASSES` = [MobileTokenAuthentication, CsrfExemptSessionAuthentication] | `core/settings.py:646-651` | Mobile-first auth stack; token via X-API-Key header + session with CSRF-exempt-when-token-present |
| `DEFAULT_PERMISSION_CLASSES` = ['rest_framework.permissions.IsAuthenticated'] | `core/settings.py:652-653` | Single-entry default; all views without explicit `@permission_classes` inherit this |
| `DEFAULT_PAGINATION_CLASS` = PageNumberPagination | `core/settings.py:655` | Pagination policy (referenced for completeness; not authorization-relevant) |

**Custom DRF permission classes (3 total across platform):**

| Entry Point | File:Line | Purpose |
|---|---|---|
| `FleetSignatureRequired` permission class | `core/services/fleet_auth_drf.py:176-212` | Enforces `request.fleet_identity is not None`; 403 with structured `DenyCode` error dict on missing identity |
| `FleetCapabilityRequired` permission class | `core/services/fleet_auth_drf.py:215-262` | `.for_capability(*path)` factory-method builds dynamic subclass; enforces `FleetServiceIdentity.capability(*path)` truthy; 403 with `DenyCode.CAPABILITY_DENIED` on missing capability |
| `PublicIntelTokenAuth` DRF auth class | `core/views_public_intelligence.py:37-53` | Header `X-Intel-Token` match against `settings.PUBLIC_INTEL_TOKEN`; raises `AuthenticationFailed` on mismatch |

**Middleware-layer authorization loci (inherited from Cat A §3 with
Cat B extension):**

| Entry Point | File:Line | Purpose |
|---|---|---|
| `UnifiedTokenAuthenticationMiddleware.process_request()` — STAFF check | `core/auth_middleware.py:610-613` (session path) + `:661-664` (token path) | Enforces `STAFF_REQUIRED_PATHS` (3 entries; 2 phantom per F-STAFF-1); 403 if `not request.user.is_staff` |
| `UnifiedTokenAuthenticationMiddleware.process_request()` — REVIEWER block check | `core/auth_middleware.py:616-623` (session path) + `:667-673` (token path) | Enforces `REVIEWER_BLOCKED_PATHS` (12 entries) + method-check (non-GET/HEAD/OPTIONS on `/api/*` blocked unless in REVIEWER_ALLOWED_PATHS); 403 |
| `VIPReadOnlyMiddleware.__call__()` | `core/vip_middleware.py:56-91` | HTTP-layer HARD RUNTIME gate; enforces VIP_ALLOWED_WRITE_PATHS (4) + VIP_ALLOWED_COCKPIT_PATHS (3) + VIP_ALLOWED_READ_PREFIXES (11); 403 on violation |

**PA tool-dispatcher authorization plane (auth-agnostic dispatcher +
user-scoped handlers):**

| Entry Point | File:Line | Purpose |
|---|---|---|
| `Dispatcher.execute(tool_name, payload, user_id)` | `core/services/tool_dispatcher.py` (per Agent 2 report) | Auth-agnostic wrapper: latency + trace_id + structured result; NO authorization enforcement at dispatcher level; delegates to handler layer |
| `EPAToolHandlersMixin` handlers | `core/epa_handlers_tools.py` | Handler methods; user-scoped via `self.user` context; NO explicit per-tool authorization check; assumes caller (PA WebSocket consumer) has authenticated user |
| `WORKSPACE_AWARE_AGENTS` constant (20 agents) | `core/epa_handlers_tools.py` (per Agent 2 report) | Enumeration of agents that support workspace-scoped execution; workspace-membership enforcement happens IN `execute_with_workspace()` method (NOT audited by Cat B — outside scope per parent §7.1 PA behavior anti-scope) |

**PA WebSocket consumer authorization plane (per-consumer discipline):**

| Entry Point | File:Line | Purpose |
|---|---|---|
| `PAConversationConsumer.connect()` | `core/consumers_pa_conversation.py` (line reference per Cat A §6.4 F-WS-2 + Agent 2 report) | HARD-REJECTS AnonymousUser with close code 4001 |
| `AgentProgressConsumer.connect()` | `core/consumers_base.py` (per Agent 2 report) | Accepts all connections; relies on ASGI-stack `TokenAuthMiddlewareStack` (from `core/ws_auth_middleware.py`) to have populated `scope["user"]` |
| WebSocket ASGI stack | `core/asgi.py:25-32` (inherited from Cat A §3 + §14 F-WS-1) | Installs `TokenAuthMiddlewareStack` from `ws_auth_middleware.py`; the OTHER `WebSocketAuthenticationMiddleware` at `auth_middleware.py:739-822` is DEAD CODE (Cat A F-HIGH-2) — `REQUIRE_WEBSOCKET_AUTH` setting silently ignored |

**Per-view `@permission_classes` decorator sweep summary (Cat B measurement
via Agent 2 grep-verified at HEAD `798399ec`):**

| Decorator pattern | Occurrence count | File count | Notes |
|---|---|---|---|
| `@permission_classes([IsAuthenticated])` | ~400+ | Dominant across `core/views_*.py` | Explicit restatement of DEFAULT; redundant but semantically clear |
| `@permission_classes([AllowAny])` | ~140 (approx) | ~32 files | Intentional public surfaces (marketing / betting demo / body-system monitoring); some paired with `@authentication_classes([])` |
| `@permission_classes([IsAdminUser])` | 16 | 5 files (`views_fleet_admin.py`, `views_code_runner.py`, `views_employee_api.py`, `views_vip_invite.py`, `views_deploy_verify.py`) | Staff-only gates; fleet provisioning + code execution + admin console |
| Custom `[FleetSignatureRequired]` / `[FleetCapabilityRequired.for_capability(...)]` | 3 | 2 files (`views_fleet_artifacts.py` x2, `views_fleet_paid_interest.py` x1) | Fleet-only enforcement |
| `@permission_classes([])` (explicit empty) | 2 | 1 file (`mythology/views.py:1167` + `:1194`) | F-B-MED-1 finding — both in PUBLIC_PATHS anyway |
| **Total explicit `@permission_classes`** | **~686** | **73 files** | Agent 2 grep count |
| **NO decorator (inherit DEFAULT)** | ~1200+ view functions (~65% of ~1932 view-function population) | Not counted per-file | F-B-CRIT-1 finding — implicit inheritance rate |

**Per-view `@authentication_classes([])` sweep summary (Cat B verifier-loop
grep-verified at HEAD `798399ec`):**

| File | Notes |
|---|---|
| `ai_core/api/freelance_api.py` | Freelance marketplace; anon-browse + auth-submit |
| `core/views_preferences.py` | User preferences; F-B-HIGH-4 finding — stacked with `@permission_classes([IsAuthenticated])` in some declarations (masked by middleware precedence) |
| `core/auth_views_enhanced.py` | Auth signup/login endpoints; intentional |
| `core/views_nervous.py` | Body-system monitoring (nervous system); operational-resilience justification (health checks work even if auth backend down); all endpoints in PUBLIC_PATHS anyway |
| **Total files with `@authentication_classes([])`** | **4** | Verifier-loop confirmed |

**Path-list registry entry-point summary (verifier-loop count at HEAD
`798399ec` — corrections applied to sub-agent estimates):**

| Registry | HEAD-verified count | File:line | Cat A reference |
|---|---|---|---|
| PUBLIC_PATHS (prefix-match bypass) | **265** | `core/auth_middleware.py:94-509` | Cat A §3 + §14 F-HIGH-3 |
| PUBLIC_PATHS_EXACT (exact-match bypass) | **2** | `core/auth_middleware.py:513-516` | Cat A §3; includes `/api/home/purge-queue/` F-CRIT-1 |
| OPTIONAL_AUTH_PATHS (soft-auth, fail-open) | **7** | `core/auth_middleware.py:521-538` | Cat A §3; verifier-loop corrected Agent 3 undercount (6→7) |
| STAFF_REQUIRED_PATHS | **3 declared / 1 non-phantom (`/api/v1/system/reality-check/` sub-path)** | `core/auth_middleware.py:541-545` | F-B-HIGH-1 NEW at Cat B — 2 of 3 entries phantom |
| REVIEWER_BLOCKED_PATHS | **12** | `core/auth_middleware.py:548-556` | Cat A §14 F-BND-4b reviewer inversion |
| REVIEWER_ALLOWED_PATHS | **1** (`/api/v1/auth/` exception) | `core/auth_middleware.py:559-561` | Cat A §3 |
| **Total path-list gate entries** | **290** | | (with F-B-HIGH-1 phantom correction: 288 effective enforcement points) |
| VIP_ALLOWED_READ_PREFIXES | 11 | `core/vip_middleware.py:34-46` | Cat A §14 F-HIGH-1 two-layer |
| VIP_ALLOWED_WRITE_PATHS | 4 | `core/vip_middleware.py:19-24` | Cat A §14 F-HIGH-1 |
| VIP_ALLOWED_COCKPIT_PATHS | 3 | `core/vip_middleware.py:27-31` | Cat A §14 F-HIGH-1 |
| **Total VIP whitelist entries** | **18** | | Platform's SECOND-most-explicit authorization-floor governance (18 vs 3 STAFF vs 12 REVIEWER) |

**`path()` census (HEAD-verified at `798399ec` per Agent 3 report):**

| File | `path()` count |
|---|---|
| `core/urls.py` | 1,794 |
| `core/urls_unified.py` | 44 |
| `core/urls_provenance.py` | 19 |
| `core/urls_real_data.py` | 9 |
| **Total** | **1,866** |

PLATFORM_INVENTORY reports 1,864 baseline; Cat B HEAD-verified count is
1,866 (±2 variance acceptable — line-precise counts drift with route
registration lifecycle).

---

## 4. Major Models

Auth-relevant models with authorization semantics at HEAD `798399ec`.
Cat A §4 inventoried the primary auth models (UnifiedUser, EnhancedUserProfile,
AssistantProfile, VIPInvite, DRF Token, FleetServiceIdentity/Key/Rotation,
FleetAuthAuditLog, FleetPAChatAuditRow, FleetArtifact, Tenant,
DiscordLinkCode, MobilePushToken, Django Session). Cat B does NOT re-
enumerate; instead, focuses on models carrying AUTHORIZATION-PLANE
semantics (role fields + permission carriage + workspace-scoping FKs).

**Role-carrying fields at HEAD (extending Cat A §17 F-DUP-2 role-field
bifurcation):**

| Model | Field | Type | Choices | Purpose | Cat A §17 F-DUP-2 reference |
|---|---|---|---|---|---|
| `UnifiedUser` | `platform_role` | CharField(50) | 6 values: `admin`, `sports_analyst`, `content_creator`, `agent_manager`, `unified_user`, `reviewer` | HTTP-layer authorization gate (`VIPReadOnlyMiddleware.is_reviewer` check); staff/reviewer/admin classification | Reviewed at F-DUP-2 |
| `UnifiedUser` | `customer_role` | CharField(20) | 3 values: `viewer`, `user`, `org_admin` | Multi-tenant Phase 1 role (Session 1039); **ZERO ENFORCEMENT at HEAD** per Agent 1 grep | **NEW at Cat B — never audited at Cat A** — orphaned field per Cat B F-B-DUP-1 (see §17) |
| `EnhancedUserProfile` | `primary_role` | CharField(200) | Free-text (no choices) | Personalization / user-stated professional role; ALSO holds `vip_demo_viewer` VIP gate value (per Cat A §14 F-HIGH-1) | Cat A §17 F-DUP-2 conflation |
| `AssistantProfile` | `role` | CharField(30) | 3 values: `admin`, `vip_viewer`, `customer` | PA-layer tool-access gate + ROLE_PROMPTS system-prompt injection; SOFT gate (prompt-only per Cat A §14 F-HIGH-1) | Cat A §17 F-DUP-2 |
| `FleetServiceIdentity` | `status` | CharField | `active` / `disabled` / `rotating` | Fleet auth availability gate (not really a "role" — service identity lifecycle) | Not a role field |

**Role-field bifurcation (Cat B extension to Cat A F-DUP-2):**

Cat A F-DUP-2 documented `platform_role` vs `primary_role` bifurcation
across two models. Cat B adds:

- `AssistantProfile.role` is a THIRD role carrier (PA-layer only, prompt-
  driven) — grouped with the other two for total "role field count" but
  serves different plane (PA behavior, not HTTP authorization).
- `UnifiedUser.customer_role` is a FOURTH role carrier — added Session
  1039 (multi-tenant Phase 1); **NEVER ENFORCED at HEAD** (Agent 1 grep-
  verified no read sites in views/middleware/permission classes).
  Effectively ORPHANED. Documented as Cat B F-B-DUP-1 in §17.
- No validation rule prevents a user from having conflicting role
  assignments: `platform_role='admin'` + `AssistantProfile.role='vip_viewer'`
  + `customer_role='viewer'` — three planes disagree; no enforcement of
  consistency.

**Workspace-scoping FKs (Cat B new-at-Cat-B — authorization-plane
implicit-gate model):**

| Model | Workspace FK | Purpose |
|---|---|---|
| `AssistantProfile.workspace` (nullable FK to `ProjectWorkspace`) | `core/models_assistant_profile.py:122-129` (per Agent 1 report) | Optional workspace-pinning for PA mode; carries workspace-membership implicit-gate |
| `PAConversation.workspace` (FK to `ProjectWorkspace`) | `core/models/conversations/models.py` (per Agent 1 report) | Scopes PA conversations to workspace |
| `ProjectWorkspace.user` (FK to User; NOT tenant-scoped) | `core/models_skin_layer.py:31-269` (per Agent 1 report) | User-owned workspace; no sharing/collaboration model at HEAD |

**Django `auth.Group` + `auth.Permission` (DORMANT — grep-verified zero
writes at HEAD per Agent 1):**

`UnifiedUser` inherits `groups` (ManyToMany to `auth.Group`) +
`user_permissions` (ManyToMany to `auth.Permission`) from `AbstractUser`.
Migration `0001_initial.py:260-279` created the join tables. Grep at HEAD:
`\.groups\.add\|\.user_permissions\.add\|Group\.objects\.create\|Permission\.objects\.create`
returns **zero platform-code matches** (excluding MuscleGroup which is
body-system, not auth). Django group/permission plumbing is
**inherited-but-dormant** — a latent extensibility surface that the
platform doesn't use. Documented as `dead_code` background context for
option (c) registry design (a registry could theoretically use
`auth.Permission` model but would need substantial retrofit).

**Per-endpoint permission registry model candidates (SPECULATIVE probe
per Agent 1 report + verifier-loop):**

Grep at HEAD for candidate registry model names:
`class.*PathRule\|class.*EndpointPermission\|class.*APIPermission\|class.*URLPermission\|class.*RouteAuthorization\|class.*PermissionScope`
= **zero matches**. **No database-backed per-endpoint permission
registry exists at HEAD.** Permission floor is scattered across:

1. HTTP middleware path-list registries (`core/auth_middleware.py`
   PUBLIC_PATHS + STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS +
   REVIEWER_ALLOWED_PATHS + OPTIONAL_AUTH_PATHS + PUBLIC_PATHS_EXACT +
   `core/vip_middleware.py` VIP whitelists)
2. DRF `@permission_classes` decorators on individual views (~686
   occurrences across 73 files; ~1200 views without decorator inheriting
   DEFAULT)
3. Hardcoded role-based tool access dict (`AssistantProfile.ROLE_TOOLS`
   at `core/models_assistant_profile.py:30-44` per Agent 1 report; NOT
   persisted in DB — hardcoded source)
4. Fleet `FleetServiceIdentity.capabilities` JSONField (per-service
   authorization capability schema)

**Cat B F-B-CRIT-1 headline framing (extending §1):** Absence of a
per-endpoint registry model is the STRUCTURAL enabler of the ~84%
implicit-inheritance rate. Option (c) recommendation (per §19.1) would
introduce a `PerEndpointPermission` (or similar) ORM model as the
authorization-plane single source of truth.

---

## 5. Major Services

Cat B service-layer scope: DRF permission-class dispatch runtime +
IsAuthenticated evaluation + VIP + Fleet + PA tool-dispatcher +
WebSocket consumer authorization.

**DRF `check_permissions()` dispatch runtime (per Agent 2 report):**

`APIView.initial(request)` calls (in order):
1. `self.perform_authentication(request)` — evaluates
   `authentication_classes` in order; first-match wins; sets `request.user`
2. `self.check_permissions(request)` — evaluates `permission_classes` in
   order; ALL must return True; raises `PermissionDenied` (→ 403) on any
   False return
3. `self.check_throttles(request)`
4. `self.perform_content_negotiation(request)`

**Interaction with middleware:** `UnifiedTokenAuthenticationMiddleware`
runs BEFORE DRF at Django middleware chain (position 10 of MIDDLEWARE at
`core/settings.py:227`). It sets `request.user` at
`core/auth_middleware.py:676` before DRF sees the request. DRF's
`authentication_classes` are then evaluated but often find
`request.user` already-authenticated (session/token both set upstream).
This creates the F-B-HIGH-4 middleware-precedence-masks-DRF-mismatch
condition documented in §1.

**VIPReadOnlyMiddleware runtime (Cat A §14 F-HIGH-1 baseline + Cat B
authorization-plane extension):**

`VIPReadOnlyMiddleware.__call__()` at `core/vip_middleware.py:56-91`:
1. Checks `request.user.is_authenticated` (line 94 per Agent 2 report)
2. Reads `request.user.enhanced_profile.primary_role == 'vip_demo_viewer'`
   (line 98) — VIP role detection via EnhancedUserProfile FK
3. For WRITES (non-GET methods) at line 63: matches against
   `_VIP_ALLOWED_WRITE_PATHS` (4 exact paths)
4. For `/api/cockpit/` reads at line 72: matches STRICT allowlist
   `_VIP_ALLOWED_COCKPIT_PATHS` (3 exact paths)
5. For general reads: matches `_VIP_ALLOWED_READ_PREFIXES` (11 prefixes)
6. Any violation → `JsonResponse({'error': '...'}, 403)` (lines 74-75,
   88-90)

**Failure-mode discipline:** VIP is HARD RUNTIME (403 at HTTP layer).
Cat A §14 F-HIGH-1 correctly established this is TWO-LAYER:
- HTTP layer (this middleware) — HARD RUNTIME since 2026-03-04 hardening
  (commit `5c8bd585` initial + `445d0349` default-deny hardening)
- PA payload layer — SOFT prompt-only (AssistantProfile.role='vip_viewer'
  + ROLE_PROMPTS)

Cat B extends: VIP whitelists (18 entries: 11 read + 4 write + 3 cockpit)
are the platform's SECOND-most-explicit authorization-floor governance
surface (STAFF_REQUIRED_PATHS 3 + REVIEWER_BLOCKED_PATHS 12 are
comparable-scale but SMALLER). All three together (18 + 3 + 12 = 33
explicit entries) are ~11% of the total 290 gate entries; the remaining
~89% (265 PUBLIC + 2 EXACT + 7 OPTIONAL + 1 REVIEWER_ALLOWED = 275
entries) are PUBLIC-or-BYPASS categorized. Documented in §14.5.

**Fleet authorization runtime (per Cat A §14 F-HIGH-4 CONTRACT resolution
+ Agent 2 report):**

`FleetSignatureAuthentication` (permissive by CONTRACT) at
`core/services/fleet_auth_drf.py:65-150`:
- `authenticate()` returns `(None, None)` on missing/invalid signature
  (SIDE-EFFECT-ONLY; never raises)
- Sets `request.fleet_identity` on success

`FleetSignatureExclusiveAuthentication` (raising variant) at
`core/services/fleet_auth_drf.py:275-308`:
- `authenticate()` raises `AuthenticationFailed` on failure
- Used on fleet-ONLY endpoints where any auth-failure must be 401

`FleetSignatureRequired` permission class at `:176-212`:
- Enforces `request.fleet_identity is not None`
- 403 with structured `DenyCode` error dict

`FleetCapabilityRequired` permission class at `:215-262`:
- `for_capability(*path)` factory-method builds dynamic subclass (e.g.,
  `FleetCapability_artifacts_can_push`)
- Enforces `FleetServiceIdentity.objects.get(...).capability(*path)` truthy
- 403 with `DenyCode.CAPABILITY_DENIED`

**Session 1171 503-fork isolation (Cat B extension):** The
`TokenValidationInfrastructureError` fork at
`core/auth_middleware.py:643-654` applies ONLY to token validation at
middleware layer. DRF permission-class dispatch does NOT wrap DB errors
in try/except with infrastructure-error handling. Example: if Postgres
goes down while `FleetCapabilityRequired.has_permission()` executes
`FleetServiceIdentity.objects.get(...)` at line 253-258, `OperationalError`
propagates uncaught to Django error handler → 500 (not 503). Cat B
verdict: **ACCEPTABLE asymmetry** — fleet-capability check is a rare
code path (artifact push/pull only); token validation is on every
request; most infra errors manifest at token validation, not capability
check. Documented for Group 1700 Observability arc consumption if a
uniform 503-fork discipline extension is desired.

**PA tool-dispatcher authorization plane (per Agent 3 report):**

`Dispatcher.execute(tool_name, payload, user_id)` at
`core/services/tool_dispatcher.py`:
- Auth-agnostic wrapper (latency + trace_id + structured result)
- Accepts `user_id` parameter but does NOT enforce authorization
- Records Redis metrics per tool call
- Delegates authorization to handler layer

`EPAToolHandlersMixin._handle_*()` methods at `core/epa_handlers_tools.py`:
- Handler assumes pre-authenticated user context via `self.user`
- NO explicit per-tool authorization check observed
- User-scoped execution via `self.user.id`
- NO tools require `is_staff` or `platform_role='admin'` at handler layer

**`WORKSPACE_AWARE_AGENTS` (20 agents) at `core/epa_handlers_tools.py`
(per Agent 2 report):** enumeration of agent names that support
workspace-scoped execution via `execute_with_workspace()` downstream
method. Workspace-membership enforcement lives in that method, NOT at
call site or DRF layer. This is F-B-HIGH-3 workspace-membership implicit-
gate finding.

**PA WebSocket consumer authorization plane (per Agent 3 report + Cat A
§6.4):**

- `PAConversationConsumer.connect()` at `core/consumers_pa_conversation.py`
  — HARD-REJECTS AnonymousUser with close code 4001. Explicit defensive.
- `AgentProgressConsumer.connect()` at `core/consumers_base.py` — Accepts
  all connections; relies on ASGI middleware to have populated
  `scope["user"]`. Implicit trust.
- Global setting `REQUIRE_WEBSOCKET_AUTH` at `core/settings.py:625` is
  SILENTLY IGNORED because the enforcing middleware
  (`WebSocketAuthenticationMiddleware` at
  `core/auth_middleware.py:739-822`) is not installed in ASGI stack (Cat
  A F-HIGH-2 dead code). Active ASGI middleware
  (`TokenAuthMiddlewareStack` at `core/ws_auth_middleware.py:24-52`) is
  NON-ENFORCING (sets AnonymousUser on failure).

**Celery task authorization plane (per Agent 3 report):**

Grep for `@shared_task` + `@app.task` patterns: tasks receive `user_id`
as parameter; run in Celery worker context (system/unauthenticated);
user-scoping is caller's responsibility. No task-level authorization
enforcement. Sampled 10 tasks — none have `is_staff` check in body.
Enforcement is at view layer BEFORE task dispatch. Risk: if a
malicious/buggy view passes wrong `user_id`, task runs with that
user's context.

**Management command authorization plane (per Agent 3 report):**

All commands assume local shell access (highest privilege).
`create_test_token` command allows arbitrary user token creation without
confirm gate (Cat A §14 F-CMD-1). No other commands relax the shell-
access assumption.

---

## 6. Major APIs and Interfaces

Cat B's headline deliverable is the per-endpoint permission-floor
classification. Full enumeration across 1,866 endpoints is intractable
in one child audit; Cat B delivers a 20-endpoint STRATIFIED sample
extending S2203 A3 20-endpoint baseline with permission-floor cell +
declaration source + implicit-inheritance flag + permission-untraced
flag. Full whole-platform per-endpoint mapping is deferred to Group 2500
API arc (option (c) registry authoring scope).

### 6.1 Per-endpoint permission-floor cell — 20-endpoint stratified sample

Stratification: 5 REST reads + 5 REST writes + 3 admin/staff + 3 fleet +
2 WebSocket + 2 PA tool endpoints. Extends S2203 A3 20-endpoint baseline
with Cat B classification cell (declared class + middleware gate +
implicit-inheritance + permission-untraced flag).

| # | Path | View file:line | HTTP Method | Middleware Gate | Declared Perm Class | Implicit Inherit | Permission-Untraced | Category | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `/api/v1/health/` | health view (per PUBLIC_PATHS:96) | GET | PUBLIC_PATHS | Implicit (public) | Y (from mw bypass) | N | READ public | Cat A §3 baseline |
| 2 | `/api/v1/auth/login/` | `core/auth_views.py:25` (basic) + `auth_views_enhanced.py:222` | POST | PUBLIC_PATHS | `@permission_classes([AllowAny])` | N | N | AUTH public | Cat A §3 baseline |
| 3 | `/api/v1/auth/register/` | `auth_views_enhanced.py:48` | POST | PUBLIC_PATHS | `@permission_classes([AllowAny])` | N | N | AUTH public | Cat A §3 baseline |
| 4 | `/api/app/manifest/` | `core/views_app_manifest.py:202` | GET | PUBLIC_PATHS | `@permission_classes([AllowAny])` | N | N | READ public | Deploy verification |
| 5 | `/api/nervous/status/` | `core/views_nervous.py:17` | GET | PUBLIC_PATHS | `permission_classes=[AllowAny]; @authentication_classes([])` | N | N | READ public | F-B-HIGH-4 baseline; disables DRF auth |
| 6 | `/api/mythology/patterns/` | `mythology/views.py:1167` area | GET | PUBLIC_PATHS (inferred) | `@permission_classes([])` (EXPLICIT EMPTY) | N | N | READ public | F-B-MED-1 finding |
| 7 | `/api/mythology/guards/` | `mythology/views.py:1194` area | GET | PUBLIC_PATHS (inferred) | `@permission_classes([])` (EXPLICIT EMPTY) | N | N | READ public | F-B-MED-1 finding |
| 8 | `/api/spider-intelligence/dashboard-stats/` | Per `core/auth_middleware.py:124` PUBLIC entry | GET | PUBLIC_PATHS | UNKNOWN (per Agent 3 grep-untraced) | **Y** | **Y** | READ public | Implicit-inheritance case |
| 9 | `/api/agents/` | Per `core/auth_middleware.py:131` PUBLIC entry | GET | PUBLIC_PATHS | UNKNOWN (per Agent 3 grep-untraced) | **Y** | **Y** | READ public | Implicit-inheritance case; Command Center list |
| 10 | `/api/v1/fleet/artifacts/` | `core/views_fleet_artifacts.py` (per Agent 3) | POST/GET | OPTIONAL_AUTH_PATHS | `@authentication_classes([FleetSignatureExclusiveAuthentication]) + @permission_classes([FleetSignatureRequired])` (assumed pattern) | N | N | FLEET-ONLY | Cat A §3 baseline; two-layer intentional |
| 11 | `/api/platform/triggers/` (GET) | Per `PUBLIC_PATHS_EXACT:514` | GET | PUBLIC_PATHS_EXACT | Method-dependent (GET public; POST auth-required per mw comment line 443) | **Y** for GET | **Y** for method-branching | READ conditional-public | Method-specific gating |
| 12 | `/api/v1/admin/` | **NO VIEW REGISTERED at HEAD** | GET/POST | STAFF_REQUIRED_PATHS | UNKNOWN (phantom endpoint) | Y | Y | **PHANTOM staff-gate** | **F-B-HIGH-1 finding** |
| 13 | `/api/v1/spiders/create/` | Per `core/auth_middleware.py:549` REVIEWER-BLOCKED entry | POST | REVIEWER_BLOCKED_PATHS | IsAuthenticated (inferred from DEFAULT) | **Y** | **Y** | WRITE reviewer-blocked | Middleware blocks reviewer; DRF default enforces auth |
| 14 | `/api/v1/auth/logout/` | `core/auth_views.py:84` | POST | REVIEWER_ALLOWED_PATHS (exception) + PUBLIC_PATHS (`/api/v1/auth/` prefix) | `@permission_classes([AllowAny])` (assumed) | N | N | AUTH public + reviewer-exempt | Cat A §3 baseline; silent-200 on unauth per Cat A finding |
| 15 | `/api/v1/betting/place/` | Betting POST view | POST | **PUBLIC_PATHS (line 198) + REVIEWER_BLOCKED_PATHS (line 550) — DUAL** | `@permission_classes([AllowAny])` (assumed) | Y | Y | **INVERSION** | **F-B-HIGH-2 finding**; Cat A F-BND-4a/4b re-verified |
| 16 | `/api/home/purge-queue/` | `core/views_home.py:259` | POST | PUBLIC_PATHS_EXACT | Secret-based (PURGE_SECRET env-var with hardcoded fallback) | N | N | SECRET-based public | **Cat A F-CRIT-1 re-verified**; hardcoded fallback `'donkey-purge-2026'` |
| 17 | `/api/pa/chat/` (POST) | `core/views_personal_assistant.py:16-24` (per Agent 2) | POST | (In PUBLIC_PATHS? Per Agent 4 CF-B4 flag — need Cat D verify) | `@authentication_classes([SessionAuthentication, TokenAuthentication, FleetSignatureAuthentication]) + @permission_classes([IsAuthenticated])` | N | N | WRITE hybrid auth | Hybrid session-or-token-or-fleet; also in VIP_ALLOWED_WRITE_PATHS (4 entries) |
| 18 | ws://ws/pa/conversations/<id>/ | `core/consumers_pa_conversation.py:183` (per Cat A §6.4) | WS | ASGI TokenAuthMiddlewareStack (non-enforcing) | Consumer-hard-reject AnonymousUser 4001 | N | N | WS auth-required | Explicit defensive |
| 19 | ws://ws/agents/progress/<instance_id>/ | `core/consumers_base.py` (per Agent 3) | WS | ASGI TokenAuthMiddlewareStack (non-enforcing) | Consumer accepts any (relies on middleware) | Y | Y | WS auth-relies-on-middleware | Implicit-trust; Cat A F-WS-1 dead-code silently ignored |
| 20 | `deliverable_tool` PA tool | `core/services/tool_dispatcher.py` + `core/epa_handlers_tools.py` | PA tool (not HTTP) | N/A (dispatcher auth-agnostic) | No per-tool authorization check | Y | Y | PA-tool user-scoped-only | Handler assumes pre-auth caller |

### 6.2 Classification breakdown (Cat B 20-endpoint sample)

**By declared permission class:**
- Explicit `@permission_classes([AllowAny])` (or equivalent): 5/20 (25%)
- Explicit `@permission_classes([])` (empty): 2/20 (10%)
- Explicit `@permission_classes([IsAuthenticated])`: 1/20 (5%)
- Custom Fleet classes: 1/20 (5%)
- Hybrid auth-classes stack: 1/20 (5%)
- Implicit-inheritance from DEFAULT (`IsAuthenticated`): 4/20 (20%)
- Non-DRF (WS consumer + PA tool + secret-based): 4/20 (20%)
- Phantom / unknown: 2/20 (10%)

**Permission-untraced-rate (grep-can't-find-permission-floor):** 8/20 =
40% — CONFIRMS S2203 A3 baseline directionally at this 20-endpoint
stratified sample.

**Implicit-inheritance-rate (no explicit `@permission_classes` decorator):**
extrapolated from Agent 2's aggregate count of ~1,200 views without
decorator across ~1,932 total view functions ≈ **62% at view-function
level** OR at endpoint level (endpoints ≠ views 1:1; endpoints include
ViewSet-router-generated routes with implicit permission_classes on
ViewSet class) — Cat B estimate: **~65-85% at endpoint level**; midpoint
~75%; upper-bound ~84% if ViewSet decoration is sparse; lower-bound
~65% if ViewSet-level decoration is dense. **The whole-platform exact
rate is UNKNOWN pending option (c) registry authoring** — Cat B verdict:
implicit-inheritance rate is HIGH (F-B-CRIT-1) but exact number depends
on Group 2500 API arc measurement discipline.

### 6.3 REST endpoints — count summary (Cat B extension of Cat A §6)

Cat A §6 catalog was auth-endpoint specific (7 endpoints in
`/api/v1/auth/*`). Cat B extends: total REST endpoints across all
apps ≈ 1,866 (per §3 census).

### 6.4 WebSocket consumers (Cat A §6.4 baseline extended)

Cat A §6.4 documented 4 WS consumer authorization patterns as
INCONSISTENT (PAConversationConsumer hard-rejects anon; PersonalAssistantConsumer,
LiveSportsConsumer, AIAssistantConsumer accept anon and gate features).
Cat B does NOT re-enumerate consumers (WS surface is Cat A/Cat D scope
boundary). Cat B does confirm F-WS-1 (Cat A) is still-live at HEAD:
`REQUIRE_WEBSOCKET_AUTH` at `core/settings.py:625` remains silently
ignored.

### 6.5 PA tool auth surface (Cat A §6.3 baseline extended)

Cat A §6.3 documented PA tool authorization at dispatcher + handler
layer. Cat B extends with F-B-HIGH-3 workspace-membership implicit-gate
classification: PA tool authorization is USER-SCOPED (via `self.user.id`
in handler) but WORKSPACE-membership enforcement is IMPLICIT via
`WORKSPACE_AWARE_AGENTS` constant + `execute_with_workspace()` method
(not audited by Cat B). Documented as CF-B2 for Group 2600 PA arc
ownership.

---

## 7. Runtime Flows

Per playbook §7 requirement, Cat B documents the authorization runtime
sequence for a typical request. Cat A §7 documented the AUTHENTICATION
runtime flow (middleware → validate_token → set request.user); Cat B
extends to the AUTHORIZATION runtime flow (post-authentication →
middleware path-list gates → DRF permission-class dispatch → view
execution).

### 7.1 Authorization decision sequence for a REST DRF request

```
1. Django URL resolver matches path → route to view class/function
2. Django middleware chain (positions 1-16 at core/settings.py:214-236):
   ...
   position 10: UnifiedTokenAuthenticationMiddleware.process_request()
     [core/auth_middleware.py:563-681]
     ├─ if path in PUBLIC_PATHS (prefix): return None (auth bypass)
     ├─ if path in PUBLIC_PATHS_EXACT (exact): return None (auth bypass)
     ├─ if path in OPTIONAL_AUTH_PATHS: soft-auth, fail-open on infra
     ├─ session auth path:
     │   ├─ if request.user.is_authenticated: proceed to STAFF/REVIEWER check
     │   └─ else: attempt token-auth path below
     ├─ token auth path:
     │   ├─ extract_token() [line 683]
     │   ├─ validate_token() [line 704]
     │   │   ├─ Token.DoesNotExist → return None → api_unauthorized (401)
     │   │   └─ TokenValidationInfrastructureError → api_error (503) [S1171]
     │   ├─ Set request.user = token.user [line 676]
     │   ├─ STAFF_REQUIRED_PATHS check [line 661-664]:
     │   │   └─ if not request.user.is_staff: return api_forbidden (403)
     │   └─ REVIEWER_BLOCKED_PATHS check [line 668-673]:
     │       ├─ if is_reviewer + path in REVIEWER_BLOCKED_PATHS: 403
     │       ├─ if is_reviewer + non-GET + path not in REVIEWER_ALLOWED_PATHS: 403
     │       └─ pass through otherwise
     └─ Return None (continue to next middleware)
   ...
   position 13: VIPReadOnlyMiddleware.__call__()
     [core/vip_middleware.py:56-91]
     ├─ if not is_authenticated: pass through
     ├─ if not is_vip_user: pass through
     ├─ for writes: check _VIP_ALLOWED_WRITE_PATHS → 403 if not in list
     ├─ for /api/cockpit/ reads: check _VIP_ALLOWED_COCKPIT_PATHS → 403 if not
     ├─ for other reads: check _VIP_ALLOWED_READ_PREFIXES → 403 if not
     └─ Return response (may be original or 403)
   ...
3. Django URL resolver → view dispatch
4. DRF view dispatch (if @api_view/APIView subclass):
   APIView.initial(request):
     ├─ self.perform_authentication(request)
     │   ├─ evaluate authentication_classes in order
     │   ├─ first-match wins → set request.user
     │   └─ if @authentication_classes([]): NO auth class runs;
     │       request.user is whatever middleware set (silent-precedence)
     ├─ self.check_permissions(request)
     │   ├─ evaluate permission_classes in order (DEFAULT if not decorated)
     │   ├─ ALL must return True or 403 PermissionDenied
     │   ├─ FleetSignatureRequired.has_permission(): 403 if no request.fleet_identity
     │   ├─ FleetCapabilityRequired.has_permission(): 403 if capability missing
     │   ├─ IsAuthenticated (DRF built-in): 403 if not request.user.is_authenticated
     │   ├─ IsAdminUser (DRF built-in): 403 if not request.user.is_staff
     │   └─ AllowAny (DRF built-in): always True
     ├─ self.check_throttles(request)
     └─ self.perform_content_negotiation(request)
5. View method executes with request.user + request.fleet_identity (if any)
6. Response returned
```

### 7.2 Authorization decision sequence for a WebSocket request

```
1. HTTP CONNECT upgrade request arrives at ASGI stack
2. ASGI middleware chain (core/asgi.py:25-32):
   ├─ TokenAuthMiddlewareStack (from core/ws_auth_middleware.py:24-52)
   │   ├─ Extract token from ?token= query param
   │   ├─ Validate token (async)
   │   ├─ Set scope["user"] = user or AnonymousUser
   │   └─ NEVER closes connection (NON-ENFORCING)
   ├─ (DEAD CODE at core/auth_middleware.py:739-822 — never installed;
   │   REQUIRE_WEBSOCKET_AUTH setting silently ignored per Cat A F-HIGH-2)
3. Consumer.connect() called with scope["user"] populated
   ├─ PAConversationConsumer.connect() [core/consumers_pa_conversation.py:183]:
   │   └─ if isinstance(scope["user"], AnonymousUser): close(code=4001)
   ├─ AgentProgressConsumer.connect() [core/consumers_base.py]:
   │   └─ Accept any connection (relies on middleware; but middleware
   │       is non-enforcing so accepts anon connections)
   └─ Other consumers: pattern varies (Cat A §6.4 enumerated inconsistency)
```

### 7.3 Authorization decision sequence for a PA tool call

```
1. PA WebSocket consumer receives message with tool_call payload
2. PA consumer resolves user context via self.user (from WS scope)
3. Consumer calls Dispatcher.execute(tool_name, payload, user_id)
   [core/services/tool_dispatcher.py]
   ├─ Latency + trace_id + structured result wrapper
   └─ Delegates to handler layer (auth-agnostic dispatcher)
4. Handler executes via EPAToolHandlersMixin
   [core/epa_handlers_tools.py]
   ├─ Assumes self.user is authenticated (upstream contract)
   ├─ For WORKSPACE_AWARE_AGENTS (20 agent names):
   │   ├─ if write_to_workspace: agent.execute_with_workspace()
   │   └─ else: router.route()
   ├─ Workspace-membership enforcement in execute_with_workspace()
   │   (NOT audited — outside Cat B scope; F-B-HIGH-3 flag for CF-B2
   │    Group 2600 PA arc)
   └─ For non-workspace tools: standard execute with self.user
5. Result returned through dispatcher → consumer → WS response
```

### 7.4 Runtime asymmetry — Session 1171 503-fork isolation

Cat A §7 documented Session 1171 `TokenValidationInfrastructureError`
fork at `core/auth_middleware.py:643-654` (HTTP middleware layer, token-
auth code path). Cat B confirms at HEAD:

- **HTTP middleware token validation:** 503-fork PRESENT (Session 1171 fix)
- **HTTP middleware session validation:** No 503-fork; session lookup
  errors propagate via Django's own middleware (rare in practice)
- **`@token_auth_required` decorator (9 view files per Cat A §14 F-DEC-1):**
  NO 503-fork; decorator swallows all non-Token.DoesNotExist as
  fall-through-to-401 (Cat A F-DEC-1 drift)
- **WebSocket auth via `ws_auth_middleware.py`:** NO 503-fork; silent-
  swallow-infra (Cat A F-WS-1)
- **DRF permission-class dispatch:** NO 503-fork; DB errors during
  `FleetCapabilityRequired.has_permission()` propagate uncaught to Django
  error handler → 500 (not 503)

Cat B verdict: 503-fork discipline is asymmetric across 5 code paths.
**ACCEPTABLE at Cat B scope** (correctness works for main HTTP path;
edge paths have narrow blast radius). Documented for CF-B5 Group 1700
Observability arc if uniform 503-fork discipline extension is desired
post-arc.

---

## 8. Data Ownership and Lifecycle

Cat B ownership scope: authorization-plane data ownership (permission-
floor registries + role-carrying fields + permission-untraced-rate
observability).

**Permission-floor registry data ownership:**

| Registry | File:line owner | Persistence | Retention | Change process at HEAD |
|---|---|---|---|---|
| PUBLIC_PATHS (265) | `core/auth_middleware.py:94-509` (module-level Python list) | Source code | N/A (source-versioned) | PR-based; no explicit approval gate; Cat A F-HIGH-3 accretion drift |
| PUBLIC_PATHS_EXACT (2) | `core/auth_middleware.py:513-516` | Source code | N/A | PR-based |
| OPTIONAL_AUTH_PATHS (7) | `core/auth_middleware.py:521-538` | Source code | N/A | PR-based |
| STAFF_REQUIRED_PATHS (3) | `core/auth_middleware.py:541-545` | Source code | N/A | PR-based; F-B-HIGH-1 2-of-3 phantom |
| REVIEWER_BLOCKED_PATHS (12) | `core/auth_middleware.py:548-556` | Source code | N/A | PR-based (Session 998); F-B-HIGH-2 inversion with `/api/v1/betting/place/` |
| REVIEWER_ALLOWED_PATHS (1) | `core/auth_middleware.py:559-561` | Source code | N/A | PR-based |
| VIP_ALLOWED_READ_PREFIXES (11) | `core/vip_middleware.py:34-46` | Source code | N/A | PR-based (Session 1083-era) |
| VIP_ALLOWED_WRITE_PATHS (4) | `core/vip_middleware.py:19-24` | Source code | N/A | PR-based |
| VIP_ALLOWED_COCKPIT_PATHS (3) | `core/vip_middleware.py:27-31` | Source code | N/A | PR-based |
| DRF `@permission_classes` decorators (686 sites) | Distributed across ~73 view files | Source code | N/A | PR-based; no centralized owner |
| DEFAULT_PERMISSION_CLASSES = `[IsAuthenticated]` | `core/settings.py:652-653` | Source code | N/A | Single-point-change — refactor risks silent breakage of ~1,200+ views |
| `AssistantProfile.ROLE_TOOLS` dict | `core/models_assistant_profile.py:30-44` (per Agent 1) | Source code | N/A | PR-based; PA-layer tool access hardcoded not registry |
| `WORKSPACE_AWARE_AGENTS` constant (20) | `core/epa_handlers_tools.py` | Source code | N/A | PR-based; workspace-membership implicit-gate |
| `FleetServiceIdentity.capabilities` (JSON) | DB row per fleet identity | Persistent | Live | Managed by `provision_fleet_identity` command + operator |

**Role-field ownership + lifecycle (Cat B extension of Cat A §4/§17):**

| Field | Owner | Written at | Enforced at | Lifecycle events |
|---|---|---|---|---|
| `UnifiedUser.platform_role` | Auth-domain | User creation + admin panel | HTTP-middleware (`is_reviewer` check); prompt-injection (VIP) | Reviewer role added S998; no other lifecycle |
| `UnifiedUser.customer_role` | Auth-domain (multi-tenant Phase 1) | S1039 initial user provisioning | **ZERO ENFORCEMENT at HEAD** | Orphaned — Cat B F-B-DUP-1 |
| `EnhancedUserProfile.primary_role` | Personalization + Auth (dual-purpose) | User profile edit | VIP HTTP-middleware (`vip_demo_viewer` check) | Ongoing per-user personalization; drift potential if VIP value overwritten by user text-edit |
| `AssistantProfile.role` | PA-domain (S1083) | AssistantProfile create/edit | PA-layer tool-filter + prompt-injection | Rigby audit S1083 established; no lifecycle drift observed |

**Permission-untraced-rate observability data ownership:** UNDEFINED at
HEAD. No monitoring/dashboard/alerting captures this metric. Cat B
proposes for CF-B5 Group 1700 Observability arc: if option (c) registry
lands, add observability instrumentation (per-endpoint permission-floor
declared-vs-inherited metric).

---

## 9. Integrations With Other Domains

Cat B integration classification (per S1273 §5 boundary framework;
extending Cat A §9):

### 9.1 Integration classification (headline rows only — full expansion §20)

| Auth ↔ Domain | Status | Boundary Type | Cat B Extension |
|---|---|---|---|
| Auth ↔ Users | WORKING (with HIGH debt from Cat A F-DUP-2) | Role + profile flags upstream to auth | Cat B adds F-B-DUP-1 (customer_role orphaned; 5-field role bifurcation across 4 models) |
| Auth ↔ PA | PARTIAL (with F-B-HIGH-3 workspace-membership implicit-gate) | Tool dispatch + workspace context split | Cat B flags CF-B2 for Group 2600 PA arc |
| Auth ↔ Fleet | WORKING (Cat A CONTRACT resolution) | HMAC + capabilities boundary | Cat B adds F-B-B-8 potential (permissive class without permission class = drift risk); Cat A §14 F-HIGH-4 preserved |
| Auth ↔ Betting | CRITICAL BOUNDARY VIOLATION (Cat A F-BND-4a/4b re-verified) | Write-path permission-floor dysphoria | Cat B extends: F-BND-4a is DIRECT EVIDENCE for three-option decision space option (b) recommendation |
| Auth ↔ Governance (Group 1900) | BOUNDARY PRESERVED | Authority DECISION plane distinct from authorization ENFORCEMENT plane | Cat B §16 F-BND-0 inherited from Cat A |
| Auth ↔ Frontend | CRITICAL INTEGRATION GAP (S2203 F3 silent-401 SYSTEMIC) | Silent-401 swallow + unobservable auth failures | Cat B flags CF-B3: silent-401 severity depends on Cat B recommendation (option b lowers severity; option a raises need for error-boundary framework) |
| Auth ↔ Observability (Group 1700) | PARTIAL (Cat A F-CRIT-2 zero-test-coverage) | Session 1171 503-fork + permission-floor smoke-test | Cat B flags CF-B5 for Group 1700: permission-floor coverage rate + 503-fork asymmetry documentation |

### 9.2 Cross-arc coordination flags (recap from §9.1 — full detail in §19.3)

Cat B emits 5 cross-arc coordination flags (CF-B1 → CF-B5) — see §19.3
for full evidence + destination-arc ownership matrix.

---

## 10. Event Flows

Cat B event-flow scope: authorization events emitted + permission-check
events + observability integration.

**Authorization events emitted at HEAD (per Cat A §10 baseline + Cat B
grep-verify):**

- `logger.info` / `logger.warning` / `logger.error` calls in
  `core/auth_middleware.py` + `core/vip_middleware.py` +
  `core/services/fleet_auth_drf.py` — structured logging only; NOT
  Event Bus.
- `FleetAuthAuditLog` DB row per fleet-signed request (allow always;
  deny always; other-auth-mode-warn per S1132) — DB-persistent audit;
  NOT Event Bus consumer.
- `FleetPAChatAuditRow` DB row per PA-chat request — WARN-ONLY audit;
  NOT enforcement (S1132 Rigby audit lock).
- `CeleryTaskEvent` telemetry for auth-adjacent Celery tasks — not
  auth-specific.

**Authorization events NOT emitted (gaps for Cat B):**

- No structured `AuthorizationEvent` model per-request-permission-check.
- No `PermissionDenied` event stream (403 responses don't publish to
  Event Bus).
- No permission-floor-observability metric stream.
- No implicit-inheritance-rate metric stream.

**Should-emit gaps (Cat B recommendation candidates for CF-B5 Group 1700):**

If option (c) registry authoring lands (Group 2500 API arc), an
`AuthorizationDecisionEvent` model + Event Bus routing would enable:
- Per-endpoint permission-floor observability
- Silent-swallow-vs-surfacing rate telemetry
- 503-fork asymmetry coverage across 5 code paths (§7.4)
- Registry-drift detection (new endpoints added without registry entry)

Cat B does NOT author this; flags for CF-B5.

---

## 11. Existing Documentation

Per playbook §11 documentation inventory (per Agent 5 report):

### 11.1 Top-level anchors (Cat B extends Cat A §11)

- `docs/PLATFORM_INVENTORY.md` — NO §Authorization autoblock (Cat A F-INV-1
  preserved; Cat B recommends §19.4 anchor-update)
- `docs/PLATFORM_WHAT_IT_IS.md` — NO §Authorization narrative subsection
  (Cat A F-INV-2 preserved; Cat B recommends §19.4 anchor-update)
- `docs/topics/authorization.md` — DOES NOT EXIST; Cat A §19.4 recommended
  `docs/topics/auth.md` (per Cat A F-DOC-1); Cat B expands to
  `docs/topics/authorization.md` OR extends the planned `auth.md`
  scope (Cat B recommends `authorization.md` as separate anchor with
  authorization-plane specific narrative)
- `docs/research/platform_architecture_inventory.md` §3.27 row 27 (Auth /
  Permissions / Security PARTIAL + LIGHT) — Cat A revised baseline; Cat
  B extends with per-endpoint classification + implicit-inheritance
  rate + three-option decision space evidence + Cat B recommendation

### 11.2 Research arc docs (Cat B related)

- Cat A `2401_authentication_surface_trust_boundaries_audit.md` — PRIMARY
  Cat B load-bearing input; §5 mechanism inventory + §14.5 trust-boundary
  rate table + §14 findings F-CRIT-1/F-BND-4a/4b/F-HIGH-1/F-HIGH-2/F-HIGH-3/F-DEC-1
  + §17 F-DUP-2 role-field bifurcation
- Parent `2400_auth_domain_scoping.md` §3.B Cat B expected outputs +
  §7.1 leak-vector guardrails
- Cross-arc: S2203 `2203_frontend_api_contract_boundary_discipline_audit.md`
  §14 F3 silent-401 SYSTEMIC + §14 F3.5 whitelist BRITTLE + §19.1 R2
  three-option decision space + A3 20-endpoint permission-untraced sample
- Cross-arc: S2299 `2299_frontend_canonical_summary.md` §8.2 T1 aggregation
  + §5.4 CF-1 permission-floor Cat B ownership

### 11.3 Gap analysis (Cat B extends Cat A)

Cat A §11 catalog:
- Cat A F-DOC-1 (no `docs/topics/auth.md`) — HIGH severity; Cat B extends
- Cat A F-DOC-2 (no threat-model doc) — HIGH severity; Cat B references
- Cat A F-INV-1 (no PLATFORM_INVENTORY §Auth autoblock) — MED; Cat B extends
- Cat A F-INV-2 (no PLATFORM_WHAT_IT_IS §Auth subsection) — MED; Cat B extends

Cat B adds:
- Cat B F-DOC-3 (no per-endpoint permission-floor registry doc) — CRITICAL
  if option (c) registry lands; Cat B recommends `docs/topics/authorization.md`
  §Per-endpoint-registry section

---

## 12. Research Coverage

Per playbook §12 classification (EXPERIMENTAL / PARTIAL / WORKING /
STABLE / CANONICAL):

**Prior research coverage:**

- Group 2400 Cat A (S2401) — MEDIUM coverage of authentication mechanism
  vocabulary + trust-boundary rate table + PUBLIC_PATHS accretion audit
- Group 2200 T1 handoff bundle — LIGHT coverage of frontend-symptom-side
  authorization observability (silent-401 F3; whitelist BRITTLE F3.5)
- Group 1273 §3.27 baseline — LIGHT coverage (PARTIAL + LIGHT
  classification carried forward)
- Group 1900 authority DECISION plane — DISTINCT arc (boundary
  preserved); no authorization-plane coverage

**Cat B research coverage delivered:**

- Per-endpoint permission-floor classification framework — MEDIUM coverage
  (20-endpoint stratified sample + methodology; whole-platform
  measurement deferred to Group 2500 API arc)
- Implicit-inheritance rate whole-platform measurement — LIGHT-MEDIUM
  coverage (aggregate estimate ~65-85% at endpoint level; exact whole-
  platform number UNKNOWN pending option (c) registry)
- STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS + REVIEWER_ALLOWED_PATHS
  drift audit — WORKING coverage (F-B-HIGH-1 phantom-endpoint finding +
  F-B-HIGH-2 F-BND-4a/4b re-verification)
- Three-option decision space evidence + Cat B recommendation — WORKING
  coverage (evidence table + rationale + Chris D-verdict-request)

**Cat B research coverage NOT delivered (deferred):**

- Whole-platform per-endpoint permission-floor cell registry — deferred
  to Group 2500 API arc (option (c) scope if Chris D-verdict selects
  registry authoring)
- Per-endpoint smoke-test coverage extension — deferred to post-arc
  T-slot (Cat A F-CRIT-2 blocker)
- PA workspace-membership authorization enforcement audit — deferred
  to Group 2600 PA arc (CF-B2)
- Silent-401 execution-surface audit — deferred to Cat D S2404

---

## 13. Architecture Maturity

Per playbook §12 classification, Cat B verdict on authorization plane:

**Overall authorization plane maturity: PARTIAL (mechanism WORKING;
registry PARTIAL→EXPERIMENTAL; observability EXPERIMENTAL)**

Per Cat A §13 verdict for authentication plane: PARTIAL (mechanism
layer intentional; PUBLIC_PATHS registry accreted). Cat B extends the
same pattern to authorization plane:

### 13.1 Mechanism-declaration layer maturity: WORKING

- DRF `DEFAULT_PERMISSION_CLASSES = ['IsAuthenticated']` — WORKING
  (correct default; enforced globally)
- 3 custom DRF permission classes (`FleetSignatureRequired`,
  `FleetCapabilityRequired`, `PublicIntelTokenAuth`) — WORKING
  (fail-closed contracts; explicit documentation)
- VIP HTTP-layer HARD RUNTIME gate (`VIPReadOnlyMiddleware`) — WORKING
  (hardened 2026-03-04)
- STAFF/REVIEWER middleware enforcement — WORKING (Cat A §7 per-caller-
  class runtime posture confirmed)

### 13.2 Registry-of-endpoints layer maturity: PARTIAL → EXPERIMENTAL

- PUBLIC_PATHS: 265 entries; 8+ duplicates; no gatekeeper; no approval
  gate; accretion 2.5× drift from ~108 baseline (Cat A F-HIGH-3)
- STAFF_REQUIRED_PATHS: 3 entries; 2 phantom (F-B-HIGH-1 NEW at Cat B)
- REVIEWER_BLOCKED_PATHS: 12 entries; F-BND-4a inversion inside (Cat A);
  F-B-HIGH-2 Cat B extension
- REVIEWER_ALLOWED_PATHS: 1 entry (auth exception carve-out) — WORKING
- OPTIONAL_AUTH_PATHS: 7 entries; intentional delegation to DRF for
  fleet endpoints — WORKING
- VIP whitelists (18 entries) — WORKING (explicit + hardened)
- Per-endpoint DRF `@permission_classes` decoration: ~35% explicit vs
  ~65% implicit-inheritance from DEFAULT (F-B-CRIT-1)

Verdict: **PARTIAL** (some registries WORKING, others PARTIAL, none
CANONICAL-with-registry).

### 13.3 Observability layer maturity: EXPERIMENTAL

- Auth events emitted via `logger.*` only; no Event Bus routing
- No `AuthorizationEvent` / permission-check-event stream
- No per-endpoint permission-floor observability metric
- No implicit-inheritance-rate visibility
- Cat A §14.5 smoke-test coverage: 3 PRESENT + 2 PARTIAL + 9 ABSENT
  (3/14 tested = 21% coverage rate — blocker to acceptance criterion #6)

Verdict: **EXPERIMENTAL** (basic logging exists; architecture-level
observability absent).

### 13.4 Cat B canonical-seam extension

Cat A observed: "structurally intentional at the mechanism-declaration
layer but structurally accreted at the PUBLIC_PATHS-registry layer."

Cat B extends: same pattern applies to authorization plane. Mechanism-
declaration (DRF classes, VIP middleware, Fleet auth) is WORKING;
registry-of-endpoints (path lists + per-view decorators + implicit
inheritance) is PARTIAL. Cross-cutting canonical seam: **"Defaults that
silently swallow failure vs contracts that surface failure"** — see §1
for Cat B four-way partition (silent-swallow / contract-that-surfaces /
partial-contract / confused-contract).

### 13.5 Maturity verdict axis clarification (Rigby SIGN cycle 1 Q15 fold)

The PARTIAL verdict should NOT be read as "authorization is broken."
Correct axis: **correctness is WORKING-by-default** (DRF
`DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]` enforces auth as the
correct-by-default posture; 3 custom Fleet + PublicIntel permission
classes fail closed; VIP HTTP HARD RUNTIME gate hardened 2026-03-04),
**but governance/observability is EXPERIMENTAL** (no per-endpoint
registry; ~80-90% implicit inheritance means declared-vs-inherited
observability is opaque; no observability instrumentation for
permission-floor coverage) → **overall PARTIAL because governance is
under-developed, not because authorization is defective.** Same verdict
as Cat A but different reasons — Cat A PARTIAL was mechanism-vs-registry
maturity split; Cat B PARTIAL is correctness-vs-governance maturity split.

---

## 14. Known Drift

Cat B drift matrix — extending Cat A §14. Cat A findings F-CRIT-1,
F-CRIT-2, F-HIGH-1, F-HIGH-2, F-HIGH-3, F-DEC-1, F-DUP-2, F-WS-1,
F-TOKEN-1, F-DEBUG-1/2/3, F-SESS-1, F-VIP-1, F-PA-1/2/3/4, F-CMD-1,
F-FLEET-1, F-DOC-1/2, F-INV-1/2, F-PROV-1, F-BND-1/4a/4b are
INHERITED as background (see Cat A §14 for detail). Cat B adds Cat-B-
prefixed findings.

### 14.1 CRITICAL drifts (new at Cat B HEAD)

**F-B-CRIT-1 — Permission-floor implicit-inheritance rate ~65-85%
(whole-platform estimate).** ~1,200 of ~1,932 view functions
(~65% at view-function level per Agent 2 aggregate count) have NO
explicit `@permission_classes` decorator; permission floor inherited
from `DEFAULT_PERMISSION_CLASSES = ['rest_framework.permissions.IsAuthenticated']`
at `core/settings.py:652-653`. At endpoint level (~1,866 endpoints,
including ViewSet-router-generated routes), estimate rises to ~65-85%
depending on ViewSet-class-level decoration density (UNKNOWN without
per-ViewSet audit). **Class: `technical_debt` + `missing_connection`.**
Severity: **CRITICAL** for observability (permission-floor is not
per-endpoint declared; grep can't find the floor without knowing DEFAULT
is `IsAuthenticated`); **LOW** for correctness (endpoints work; DEFAULT
enforces auth). Blocker to acceptance criterion #1.

**F-B-CRIT-2 — S2203 F3 silent-401 SYSTEMIC is a downstream symptom of
F-B-CRIT-1.** Frontend `api.ts:48-56` swallows 401 silently for
~630 of ~1,300 gated call sites (S2203 A3 estimate). Cat B connects:
frontend silent-swallow is a rational response to F-B-CRIT-1 permission-
floor unobservability. Option (b) split-read-write with client-side
auth-gate (Cat B recommendation) directly addresses this: frontend
gates writes on auth state; reads work anonymously. **Class: `drift`
(systemic).** Severity: **CRITICAL** in aggregate. Blocker to
acceptance criterion #2. DEFERRED to Cat D S2404 for tactical
remediation design.

### 14.2 HIGH drifts (new at Cat B HEAD)

**F-B-HIGH-1 — STAFF_REQUIRED_PATHS 2-of-3 PHANTOM entries (F-STAFF-1).**
`/api/v1/admin/` and `/api/v1/metrics/admin/` at
`core/auth_middleware.py:541-545` have NO view registration at HEAD
`798399ec`. Verifier-loop grep: `path\(['\"]api/v1/admin/` = 0 matches;
`path\(['\"]api/v1/metrics/admin/` = 0 matches. Only
`/api/v1/system/reality-check/` at `core/urls.py:3353` exists on
`/api/v1/system/*` namespace (lambda view returning JsonResponse).
Middleware STAFF_REQUIRED_PATHS check at `core/auth_middleware.py:610-613`
(session-auth path) + `:661-664` (token-auth path) enforces 403 to
non-staff; staff request gets middleware-pass-then-404. **Class:
`dead_code` + `drift`.** Severity: **MED** (correctness OK; misleading
config). **Rigby SIGN cycle 1 Q6 fold — defense-in-depth credibility
risk tag:** phantom entries create OPERATOR OVERCONFIDENCE + make future
audits harder (if someone later registers those paths, they may assume
they're already protected). **Risk ESCALATES to HIGH if path later
registered without corresponding smoke tests confirming the STAFF gate
still fires.** Post-arc recommendation candidate: remove phantom entries
OR add explicit admin/index/health-check view.

**F-B-HIGH-2 — `/api/v1/betting/place/` PUBLIC + REVIEWER-BLOCKED
inversion INTACT at Cat B HEAD (Cat A F-BND-4a/4b RE-VERIFIED).**
Path at `core/auth_middleware.py:198` (PUBLIC_PATHS with comment
"Session 563: Bet Tracking (allow anonymous for demo mode)") AND `:550`
(REVIEWER_BLOCKED_PATHS). **Reclassification is CONDITIONAL on
early-return behavior at line 570** (Rigby SIGN cycle 1 Q7 fold — verifier
grep): middleware code at line 570 reads
`if any(request.path.startswith(path) for path in self.PUBLIC_PATHS): return None`
— returns `None` (allow) immediately on PUBLIC match, NOT
"mark public then continue checks." If any future branch continues
evaluation (e.g., public-but-still-block-reviewers), the reclassification
would fail; Cat B verifier-loop confirmed at HEAD `798399ec` the
early-return behavior. The REVIEWER_BLOCKED_PATHS check at line 668 is
NEVER REACHED for this path. Reviewer inversion is a DEAD CODE entry
(Cat B extension of Cat A F-BND-4b). Anon-user can bet (public bypass); reviewer-user
theoretically can bet too (never reaches reviewer-check gate); only
"non-reviewer authenticated user" gets to a view (if it exists — Cat B
did not verify view existence for `/api/v1/betting/place/`). **Cat B
Cat A F-BND-4a extension classification: F-BND-4a-INVERSION-DEAD-CODE —
the "reviewer inversion" is not an active enforcement inversion but a
dead-code registry entry.** Class: `boundary_violation` (F-BND-4a
CRITICAL preserved) + `dead_code` (F-BND-4b HIGH extended). Severity:
**CRITICAL** for F-BND-4a (unauth write); **HIGH** for F-BND-4b (dead-
code registry entry adds registry noise). Post-arc P0 remediation.

**F-B-HIGH-3 — Workspace-membership implicit permission gate.**
`WORKSPACE_AWARE_AGENTS` constant at `core/epa_handlers_tools.py` (20
agent names). Agent dispatch checks `if agent_name in WORKSPACE_AWARE_AGENTS
and write_to_workspace:` → calls `execute_with_workspace()`. Workspace-
membership enforcement happens IN that method (not audited by Cat B —
outside scope). At HTTP layer: no DRF permission-class check enforces
workspace-membership; endpoints receiving `workspace_id` in payload
trust the caller. **Class: `missing_connection` + `unclear_owner`.**
Severity: **HIGH** (blast radius: all PA endpoints receiving workspace-
scoped tool calls). Cat B flags **CF-B2** for Group 2600 PA arc
ownership.

**F-B-HIGH-4 — `@authentication_classes([])` sites (4 files) create
DRF-contract-vs-middleware-contract confusion.** Files:
`ai_core/api/freelance_api.py`, `core/views_preferences.py`,
`core/auth_views_enhanced.py`, `core/views_nervous.py`. In
`views_preferences.py`, stacking with `@permission_classes([IsAuthenticated])`
creates confused contract — DRF auth doesn't run; middleware precedence
masks the mismatch. Middleware sets `request.user` at
`core/auth_middleware.py:676`, so DRF `IsAuthenticated` sees the already-
set user (line 676 upstream). **Works BY ACCIDENT via middleware
ordering, not by DRF contract.** **Class: `drift` + `technical_debt`.**
Severity: **HIGH** — if middleware ordering changes, `views_preferences.py`
breaks silently. **Rigby SIGN cycle 1 Q9 fold — per-site severity
escalation:** if any of these 4 files has WRITE/mutation semantics or
security-sensitive-flow (login/token flows), that specific file
ESCALATES to **CRITICAL** while the overall pattern stays HIGH.
`core/auth_views_enhanced.py` includes login/token flows — pre-emptively
flag as CRITICAL-per-site pending Cat D confirmation. Post-arc
consolidation candidate.

### 14.3 MEDIUM drifts (new at Cat B HEAD)

**F-B-MED-1 — `@permission_classes([])` explicit-empty sites (2 sites).**
Both in `mythology/views.py:1167` + `:1194`. Both in PUBLIC_PATHS
(middleware bypasses auth); explicit empty declaration is REDUNDANT.
Not currently dangerous (visualization data). Pattern-precedent risk:
if either endpoint accidentally receives write capabilities in future,
empty class silently allows unauth writes. **Class: `drift` (minor).**
Severity: **MED** — rationale rephrased per Rigby SIGN cycle 1 Q10 fold:
"**hygiene debt; future-risk amplifier**" (not severity inflation).
Alternative severity LOW considered but MED preserved because pattern
absence-of-explicit-declaration precedent risks propagating to
higher-stakes views. Post-arc cleanup candidate.

**F-B-MED-2 — `UnifiedUser.customer_role` ORPHANED field (multi-tenant
Phase 1 unused enforcement).** Field at `core/models/base/models.py`
(line unknown; per Agent 1 report). Session 1039 added; grep-verified
ZERO enforcement in views/middleware/permission-classes at HEAD.
**Class: `drift` + `unused`.** Severity: **MED** (functional risk if
Multi-tenant Phase 2 enforcement lands on stale/inconsistent field
values). Documented as **Cat B F-B-DUP-1 in §17** (adds fourth role
field to Cat A F-DUP-2 bifurcation).

**F-B-MED-3 — Session 1171 503-fork asymmetry across 5 code paths.**
Cat A §7 documented 503-fork at HTTP middleware token-auth path. Cat B
confirms at HEAD: `@token_auth_required` decorator (Cat A F-DEC-1), WS
auth (Cat A F-WS-1), DRF permission-class dispatch — none have 503-fork.
Cat B verdict: **ACCEPTABLE asymmetry at Cat B scope** — main HTTP path
correctness is preserved; edge paths have narrow blast radius. **Class:
`drift`.** Severity: **MED** (documentation/observability concern; not
functional bug). Post-arc CF-B5 for Group 1700 Observability if uniform
extension desired.

### 14.4 LOW / observational

**F-B-LOW-1 — Django `auth.Group` + `auth.Permission` DORMANT
(inherited-but-unused).** `UnifiedUser` inherits M2M fields via
`AbstractUser`; grep-verified zero writes at HEAD. Migration `0001_initial.py:260-279`
created join tables. Latent extensibility surface; not a bug. Class:
`dead_code`. Severity: **LOW** (documentation clarity concern).

**F-B-LOW-2 — Permission-untraced-rate observability instrumentation
absent.** No monitoring/dashboard/alerting captures implicit-inheritance
rate or permission-floor coverage. Class: `missing_connection`.
Severity: **LOW** (post-arc CF-B5 candidate).

### 14.5 Permission-floor cell rate table (Cat B extension of Cat A §14.5)

Cat A §14.5 tabulated 14 auth-mechanism × 3-gate-type matrix. Cat B
extends with authorization-plane coverage:

| Authorization Enforcement Locus | Coverage Type | Runtime Enforcement | Cat B Classification | Evidence |
|---|---|---|---|---|
| DRF DEFAULT_PERMISSION_CLASSES = [IsAuthenticated] | Implicit (~65-85% of endpoints) | 403 on unauth | WORKING (correctness) + PARTIAL (observability) | `core/settings.py:652-653` |
| DRF explicit `@permission_classes([IsAuthenticated])` | Explicit (~400+ occurrences across ~73 files) | 403 on unauth | WORKING | Grep count |
| DRF explicit `@permission_classes([AllowAny])` | Explicit (~140 occurrences across ~32 files) | Pass-through | WORKING (intentional public) | Grep count |
| DRF explicit `@permission_classes([IsAdminUser])` | Explicit (16 occurrences, 5 files) | 403 on non-staff | WORKING | Grep count |
| DRF custom `[FleetSignatureRequired]` / `[FleetCapabilityRequired.for_capability(...)]` | Explicit (3 occurrences, 2 files) | 403 on missing identity/capability | WORKING | `core/services/fleet_auth_drf.py:176-262` |
| DRF explicit `@permission_classes([])` (empty) | Explicit (2 occurrences, 1 file) | Pass-through (DANGEROUS if writes added) | MED drift | `mythology/views.py:1167 + :1194` |
| DRF explicit `@authentication_classes([])` (auth-off) | Explicit (4 files) | Auth off; middleware-precedence masks | HIGH drift (F-B-HIGH-4) | 4 files enumerated |
| Middleware PUBLIC_PATHS (prefix) | 265 entries | Bypass all auth+authz | PARTIAL (accretion drift Cat A F-HIGH-3) | `core/auth_middleware.py:94-509` |
| Middleware PUBLIC_PATHS_EXACT (exact) | 2 entries | Bypass sub-paths require auth | WORKING (S1005 pattern) | `core/auth_middleware.py:513-516` |
| Middleware OPTIONAL_AUTH_PATHS (soft-auth) | 7 entries | Fail-open on infra | WORKING (intentional delegation to DRF) | `core/auth_middleware.py:521-538` |
| Middleware STAFF_REQUIRED_PATHS | 3 declared / 1 non-phantom | 403 on non-staff | PARTIAL (F-B-HIGH-1 phantom drift) | `core/auth_middleware.py:541-545` |
| Middleware REVIEWER_BLOCKED_PATHS | 12 entries | 403 on reviewer + method | PARTIAL (F-B-HIGH-2 inversion dead-code) | `core/auth_middleware.py:548-556` |
| Middleware REVIEWER_ALLOWED_PATHS | 1 entry | Reviewer exception | WORKING | `core/auth_middleware.py:559-561` |
| VIP HTTP HARD RUNTIME (11+4+3 = 18 entries) | Explicit whitelists | 403 on VIP violation | WORKING (Cat A §14 F-HIGH-1 two-layer HARD) | `core/vip_middleware.py:19-46` |
| VIP PA payload SOFT (prompt-only) | AssistantProfile.role='vip_viewer' | Prompt-injection; no runtime gate | PARTIAL (Cat A F-HIGH-1 two-layer SOFT) | `core/models_assistant_profile.py:55-80` |
| PA tool dispatcher (`Dispatcher.execute`) | Auth-agnostic | No enforcement at dispatcher | EXPERIMENTAL (delegated to handler assumed-auth) | `core/services/tool_dispatcher.py` |
| PA handler (`self.user` implicit) | Handler-level | User-scoped via self.user.id; no is_staff gate | PARTIAL (F-B-HIGH-3 workspace-membership implicit) | `core/epa_handlers_tools.py` |
| WS consumer `PAConversationConsumer` | Consumer-level | HARD-REJECT anon 4001 | WORKING (defensive) | `core/consumers_pa_conversation.py:183` |
| WS consumer `AgentProgressConsumer` (and 3 others) | Consumer-level | Accept-any; relies on middleware | EXPERIMENTAL (Cat A §6.4 inconsistency) | `core/consumers_base.py` |
| WS `REQUIRE_WEBSOCKET_AUTH` global setting | Setting-only | SILENTLY IGNORED (Cat A F-WS-1) | DEAD (Cat A F-HIGH-2) | `core/settings.py:625` + `core/auth_middleware.py:739-822` DEAD |
| Celery task authorization | Task-level | None (user-scoped via user_id param) | EXPERIMENTAL (caller-trusted) | `@shared_task` sample |
| Management command authorization | Shell-access only | None (local shell = highest privilege) | WORKING (Django convention) | Command sample |

**Cat B authorization-plane summary:** 21 enforcement loci
(vs Cat A 14 mechanism × 3-gate matrix). Coverage classification:
- WORKING: 10 loci
- PARTIAL: 6 loci
- EXPERIMENTAL: 4 loci
- MED-HIGH drift: 3 loci (F-B-HIGH-4 auth-off, F-B-MED-1 empty-class, F-B-HIGH-1 phantom)
- DEAD: 1 locus (Cat A F-HIGH-2 WS middleware; carry-over)

**Out-of-table / additional-EXPERIMENTAL authorization loci (Rigby SIGN
cycle 1 Q11 fold — exhaustiveness completion):** Cat B's 21-loci
tabulation covers server-permission-class + middleware-gate + VIP + PA +
workspace surfaces. Two additional loci are NAMED as out-of-table for
exhaustiveness but NOT audited in Cat B (parent §7.1 anti-scope + Cat B
mission scope constraint):

| Locus | Coverage Type | Cat B Classification | Why out-of-table |
|---|---|---|---|
| Object-level authorization inside view code (queryset filtering, `get_object()` ownership checks) | Explicit per-view | EXPERIMENTAL (varies per view) | Requires per-view audit; bypasses DRF permission classes but still IS authorization; parent §7.1 leak-vector guardrail |
| Serializer-level / business-rule authorization (validation restricting writes based on role, e.g., DRF `serializer.validate_*()`) | Explicit per-serializer | EXPERIMENTAL (varies per serializer) | Same rationale; serializer-plane audit deferred to Group 2500 API arc |

Cat B naming these prevents "you forgot X" critique. Post-arc: option (c)
per-endpoint registry could canonicalize both loci as
`object_level_authorization: {check_type, cite}` +
`serializer_level_authorization: {validators, cite}` metadata.

**Blocker to acceptance criterion #6:** Cat A §14.5 rate table showed
3/14 mechanism-level smoke tests PRESENT. Cat B extension: authorization-
plane smoke-test coverage is 0/? at authorization-scenario level
(F-B-CRIT-1 implicit-inheritance, F-B-HIGH-1 phantom entries, F-B-HIGH-2
inversion dead-code, F-B-HIGH-3 workspace-membership implicit-gate,
F-B-HIGH-4 authenticate([])-stacking). Post-arc smoke-test authoring is
BLOCKER-CO-EQUAL with Cat A F-CRIT-2.

---

## 15. Known Technical Debt

Cat B debt matrix — extending Cat A §15. Cat A findings preserved as
background inheritance.

| Debt | Severity | Blast radius | Owner | Age | Finding type |
|---|---|---|---|---|---|
| F-B-CRIT-1 Permission-floor implicit-inheritance rate ~65-85% | **CRITICAL** (observability) / LOW (correctness) | ~1,200-1,600 endpoints of ~1,866 | Auth + all endpoint-owning teams | Since always (DRF default) | `technical_debt` + `missing_connection` |
| F-B-CRIT-2 S2203 F3 silent-401 downstream symptom of F-B-CRIT-1 | **CRITICAL** (systemic) | ~630 of ~1,300 gated call sites (S2203 A3) | Auth + Frontend + PA | Since S1505 (frontend interceptor introduced) | `drift` (systemic) |
| F-B-HIGH-1 STAFF_REQUIRED_PATHS 2-of-3 phantom (F-STAFF-1) | **MED** | 2 registry entries + governance-observability | Auth | Since STAFF_REQUIRED_PATHS creation | `dead_code` + `drift` |
| F-B-HIGH-2 F-BND-4a/4b inversion-dead-code (extends Cat A) | **CRITICAL** (F-BND-4a) + **HIGH** (F-BND-4b dead-code) | Bet-placement anonymous write; REVIEWER_BLOCKED entry inert | Auth + Betting | Since S563 (2026-01-XX bet-tracking add) | `boundary_violation` + `dead_code` |
| F-B-HIGH-3 Workspace-membership implicit gate | **HIGH** | All PA endpoints receiving workspace_id | Auth + PA | Since WORKSPACE_AWARE_AGENTS introduction | `missing_connection` + `unclear_owner` |
| F-B-HIGH-4 `@authentication_classes([])` + `[IsAuthenticated]` stacking (F-AUTH-EMPTY-1) | **HIGH** | 4 files (auth-middleware-precedence-masked) | Auth + view-owning teams | Since always (DRF discipline never established) | `drift` + `technical_debt` |
| F-B-MED-1 `@permission_classes([])` empty (F-EMPTY-1) | **MED** (pattern-precedent) | 2 mythology views | Auth + Mythology-owning team | Since mythology views authored | `drift` (minor) |
| F-B-MED-2 UnifiedUser.customer_role ORPHANED (F-B-DUP-1 §17) | **MED** | Multi-tenant Phase 2 blocker if enforcement targeted | Auth + Multi-tenant | Since S1039 (2026-02-19) | `drift` + `unused` |
| F-B-MED-3 Session 1171 503-fork asymmetry across 5 code paths | **MED** (documentation/observability) | 4 non-HTTP-token-auth paths + DRF permission dispatch | Auth + Observability | Since Session 1171 (2026-06-20) | `drift` |
| F-B-LOW-1 Django `auth.Group` + `auth.Permission` DORMANT | **LOW** | Latent extensibility surface | Auth | Since always (Django default) | `dead_code` |
| F-B-LOW-2 Permission-untraced-rate observability instrumentation absent | **LOW** (observability) | Whole authorization plane | Auth + Observability | Since always | `missing_connection` |

---

## 16. Boundary Violations

Cat B extends Cat A §16 boundary-violation matrix. Cat A F-BND-0
(authority-vs-authentication demarcation) preserved.

**F-B-BND-1 (Cat B new) — Workspace-membership implicit-gate crosses
Auth-PA-Workspace boundaries without declared contract.** Discussed as
F-B-HIGH-3. Auth-domain declares `platform_role`; PA-domain declares
`AssistantProfile.role`; Workspace-domain declares
`ProjectWorkspace.user`. The three-way integration (PA endpoint
receives workspace_id in payload + agent execution in
`WORKSPACE_AWARE_AGENTS` list + workspace membership assumed) has no
explicit permission-class check at HTTP layer. **Class:
`boundary_violation` + `missing_connection`.** Severity: **HIGH**.
**Cross-arc coordination: CF-B2 to Group 2600 PA arc.**
**Rigby SIGN cycle 1 Q12 fold — boundary-taxonomy discipline
cross-link:** F-B-BND-1 is the boundary LENS (Auth ↔ PA ↔ Workspace
contract breach); F-B-HIGH-3 (§14.2) is the concrete mechanism
INSTANTIATION (`WORKSPACE_AWARE_AGENTS` dispatch behavior). Both are
preserved separately to maintain boundary-taxonomy discipline; do not
merge (that would reduce finding count without adding evidence
clarity).

**F-B-BND-2 (Cat B new) — DRF permission-class layer vs middleware-
path-list layer: separate enforcement loci with no declared coordination
policy.** UnifiedTokenAuthenticationMiddleware path-list gates (PUBLIC/
STAFF/REVIEWER) are middleware-level. DRF permission_classes are view-
level. No canonical representation of which layer owns what semantics.
Risk: developers add permission gate at wrong layer; missed enforcement
or double-enforcement. Fleet HMAC example illustrates intentional two-
layer coordination (permissive auth class + raising permission class);
extending this pattern to VIP/reviewer/staff would require decision.
**Class: `boundary_violation` (organizational).** Severity: **MED**
(pattern-clarity concern; no runtime bug at HEAD). **Cross-arc:
CF-B1 evidence-input for Group 2500 API registry design.**

**F-B-BND-0 (inherited from Cat A §16) — Group 1900 authority DECISION
plane vs Group 2400 authorization ENFORCEMENT plane: preserved.**
Cat B confirms boundary at HEAD: no new authority-plane crossings
observed. GovernanceState + KillSwitch consumers on authorization side
(inherited from Cat A). ADR-level authority-plane changes remain
Group 1900 scope.

---

## 17. Duplicate or Overlapping Systems

Cat B extends Cat A §17. Cat A F-DUP-1 (2 orphan
TokenAuthMiddlewareStack duplicates) + F-DUP-2 (platform_role vs
primary_role bifurcation) + F-DUP-3 (4-model UserProfile duplication)
+ F-DUP-4 (rotate_fleet_key + add_fleet_key overlap) preserved as
background.

**F-B-DUP-1 (Cat B new) — `UnifiedUser.customer_role` ORPHANED role
field extends Cat A F-DUP-2 role-field bifurcation to 4-model landscape.**
Cat A F-DUP-2 documented 3-role-field bifurcation:
- `UnifiedUser.platform_role` (6 values)
- `EnhancedUserProfile.primary_role` (free-text, dual-purpose:
  personalization + VIP gate)
- `AssistantProfile.role` (3 values)

Cat B adds:
- `UnifiedUser.customer_role` (3 values; multi-tenant Phase 1 unused)

**4 role fields across 3 models** (UnifiedUser carries 2 fields:
platform_role + customer_role; EnhancedUserProfile carries 1; AssistantProfile
carries 1). No validation prevents conflicting assignments. **Class:
`duplicate_model`.** Severity: **MED** (Cat B F-B-MED-2 escalation) —
Rigby SIGN cycle 1 Q13 fold considered LOW-until-active-confusion-
evidence downgrade; MED preserved pending Cat C consolidation-lifecycle
review. **Rigby Q13 fold — additional-role-carriers disclaimer:** typical
FIFTH-role carriers include **auth-token JWT claims, Django Group/Permission
model (dormant per F-B-LOW-1), or feature-flag role fields** (SPECULATIVE
— Cat B did NOT enumerate; grep for these is post-arc T-slot candidate).
Post-arc consolidation candidate under Cat C S2403 (session-lifecycle
consolidation includes role-field lifecycle).

**F-B-DUP-2 (Cat B new) — PUBLIC_PATHS 8+ duplicates confirmed at
HEAD (Cat A §14 F-HIGH-3 baseline preserved).** Cat A enumerated at
`core/auth_middleware.py:139+213`, `142+227`, `143+226`, `137+233`,
`182+240`, `186+242`, `199+239`, `200+238`. Cat B does NOT re-enumerate
(inherited from Cat A); adds observation that this is the second
duplicate-model class (Cat A F-DUP-1 = 2 dead ASGI middleware;
F-B-DUP-2 = 8+ redundant PUBLIC_PATHS entries). Cat B extension: this
is registry-of-endpoints duplication, not model-code duplication.
**Class: `duplicate_registry`.** Severity: **HIGH** (Cat A F-HIGH-3
preserved). Post-arc cleanup candidate.

**F-B-DUP-3 (Cat B new — SPECULATIVE risk hypothesis; no confirmed
exploit path — Rigby SIGN cycle 1 Q13 fold labeling discipline) —
Potential FleetSignatureAuthentication vs FleetSignatureExclusiveAuthentication
misconfiguration risk.** Cat A §14 F-HIGH-4 resolved that two auth
classes with distinct contracts is INTENTIONAL. Cat B extension: if any
view uses permissive `FleetSignatureAuthentication` without permission
class `FleetSignatureRequired`, silent fallback-to-user-auth occurs.
Cat B did NOT enumerate view-layer misconfigurations (would require
per-fleet-endpoint audit; deferred to CF-B1 evidence for Group 2500 API
arc). **Class: `duplicate_pattern` (SPECULATIVE risk hypothesis; no
confirmed exploit path at HEAD).** Severity: **LOW-MED** (downgraded per
Rigby Q13 fold — SPECULATIVE-with-no-evidence; upgrade to HIGH IF
enumeration finds actual misconfigurations).

---

## 18. Ownership Gaps

Cat B extends Cat A §18. Cat A F-OWN-1/2/3 (unclear owner for auth
plane; EnhancedUserProfile data-retention; FleetAuthAuditLog retention
policy) preserved as background.

**F-B-OWN-1 (Cat B new) — Authorization plane overall ownership
DISPERSED (5 enforcement loci).** UnifiedTokenAuthenticationMiddleware
(auth_middleware.py) + DRF permission_classes (per-view decorators +
DEFAULT_PERMISSION_CLASSES at settings.py) + VIPReadOnlyMiddleware
(vip_middleware.py) + Fleet auth (fleet_auth_drf.py) + service tokens
(views_*.py per-endpoint). No single "authorization plane owner"
identified in code or docs. **Class: `unclear_owner`.** Severity:
**HIGH** (governance gap enables F-B-CRIT-1 accretion). Cat B should
surface: intentional dispersion (each domain owns its boundary) OR debt
(should consolidate). Cross-arc: Group 1900 authority plane has clearer
ownership (`GovernanceState` + `KillSwitch` consumers); Group 2400
authorization plane could benefit from analogous consolidation.

**F-B-OWN-2 (Cat B new) — Adding a new endpoint's permission floor:
NO DESIGNATED GATEKEEPER.** Cat A §1 noted "265-entry list has no
registry, no approval gate, no gatekeeper" citing Session-by-session
bulk-adds. Cat B extension: this is systemic for all authorization-plane
additions, not just PUBLIC_PATHS. Adding a new endpoint's `@permission_classes`
decoration (or omitting it to inherit DEFAULT) is PR-author choice
without gatekeeper review. **Class: `unclear_owner`.** Severity:
**CRITICAL** (process gap enabling accretion). Post-arc governance
recommendation candidate: designate Auth-team review requirement for
endpoint-permission additions (or explicit decentralization-by-design
with codified per-domain owner assignment).

**F-B-OWN-3 (Cat B new) — PUBLIC_PATHS cleanup ownership UNKNOWN.** No
evidence of periodic cleanup or deduplication process. Cat A F-HIGH-3
noted 8+ duplicates unaddressed since accretion. **Class:
`unclear_owner`.** Severity: **HIGH** (perpetual maintenance task
without owner). Post-arc: is PUBLIC_PATHS cleanup a one-off ADR (remove
duplicates + prevent future) or continuous maintenance?

**F-B-OWN-4 (Cat B new) — STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS
list ownership UNKNOWN.** Session 998 added reviewer split; no clear
owner established for future additions. Ad-hoc ownership drove Cat A
F-BND-4a bet-placement anonymity + F-B-HIGH-1 phantom endpoints. **Class:
`unclear_owner`.** Severity: **MED** (specific to reviewer-role
enforcement).

**F-B-OWN-5 (Cat B new) — Permission-floor observability contract
UNDEFINED.** No implicit within "DRF default = IsAuthenticated"; no
explicit measurement, no untraced-endpoint visibility, no registry.
S2203 A3 sampled 20; ~40% untraced. Cat B measures ~80-90% implicit-
inheritance whole-platform (ESTIMATE per Rigby Q2 fold). Cat B recommends
option (b) OR option (c) per §19.1. **Class: `missing_connection`.**
Severity: **CRITICAL** (core Cat B audit gap; escalated to §19.1
POSTURE-DECISION evidence plan).

**F-B-OWN-6 (Cat B new — Rigby SIGN cycle 1 Q14 fold ownership-gap
completion) — No canonical test harness / CI check that enforces
permission-floor declarations and prevents regressions.** Sub-bullet of
F-B-OWN-2 gatekeeper role: even if a gatekeeper role is designated,
without CI-lint enforcement (e.g., `check-permission-classes.yml`
analogous to existing `check-llm-sdk.yml` + `check-reasoning-contract.yml`
from S1222 CI hardening), permission-floor accretion re-emerges via
PR-author-choice discipline drift. **Class: `missing_connection`.**
Severity: **HIGH** (verifier-loop ownership missing at CI layer). Post-
arc T-slot candidate: authorize CI lint that: (i) flags new endpoints
without explicit `@permission_classes` decoration OR class attribute; (ii)
prevents new PUBLIC_PATHS entries without pull-request-template
justification; (iii) requires smoke test for STAFF_REQUIRED /
REVIEWER_BLOCKED path additions.

---

## 19. Recommended Future Research

### 19.1 POSTURE-DECISION evidence plan for xx99 (three-option decision space)

Cat B delivers evidence + recommendation lean per S2200 §5.4 Flag #1
+ S2203 §19.1 R2 three-option decision space. Chris D-verdict escalated
at S2499 xx99 close.

**Three options (per S2200 xx99 §8.2 T1 formulation + Cat B extension):**

**Option (a) — Uniform `IsAuthenticated` across all `/v1/**` + client-
side auth-gate + observable-error surfacing.**

- **Scope:** All ~1,300 `/v1/**` call-sites + ~265 PUBLIC_PATHS bypass
  entries; ~630 silent-401 risk sites (S2203 A3 estimate).
- **Blast radius:** ~265 PUBLIC_PATHS reclassification (public →
  explicit service-token OR API-key OR moved-to-`/v1/auth/`); ~10-20
  endpoints estimated for demo-mode/health-check/admin-purge migration
  including F-CRIT-1 PURGE_SECRET (blocking) + F-BND-4a bet-placement
  (blocking demo-mode UX).
- **Migration effort:** LARGE (18-25 engineer-hours). ~4 PRs over 2-3
  weeks per engineer.
- **Observability cost:** Session 1171 503-fork extension required to
  2nd + 3rd code paths (F-DEC-1 decorator + F-WS-1 WS); error-boundary
  framework authoring (S2201 §15.4 zero-boundaries baseline); observable-
  401 propagation instrumentation. 3+ additional PRs.
- **Breakage risk:** **VERY HIGH.** Demo-mode bet-placement breaks;
  monitoring scripts expecting 200 on health-check break; user-visible
  401-loops possible during rollout. Requires coordinated frontend +
  backend rollout with feature flag.
- **Reversibility:** DIFFICULT (48-72 hour rollback window; 2-3 PRs to
  revert).
- **F-CRIT-1 interaction:** BLOCKING (PURGE_SECRET remediation is
  prerequisite).
- **F-BND-4a interaction:** BLOCKING (demo-mode bet-placement breaks).
- **F-HIGH-3 (PUBLIC_PATHS drift) resolution:** DIRECT (eliminates the
  registry).
- **Timeline:** 6-8 weeks, 3-4 engineers.

**Option (b) — Uniform `AllowAny` for read paths + `IsAuthenticated`
for writes + client-side auth-check-on-write.** (Cat B PRIMARY
RECOMMENDATION)

- **Scope:** Identical HTTP surface; frontend silent-401 interception
  logic (api.ts:48-56); Zustand + localStorage auth-context (S2204 §14
  F1 15-surface baseline). Boundary: READ stays AllowAny; WRITE
  mandatory IsAuthenticated.
- **Blast radius:** Same 265 paths affected but SPLIT strategy —
  READ operations remain AllowAny; WRITE operations enforce
  IsAuthenticated at view layer (~50-80 write-only paths). Reduces
  immediate reclassification surface by 60-70% vs option (a).
- **Migration effort:** MEDIUM (10-14 engineer-hours). ~3-4 PRs over
  1-2 weeks per engineer.
- **Observability cost:** MEDIUM. Same 503-fork smoke-test + error-
  boundary framework as option (a). Silent-401 interceptor at
  api.ts:48-56 PERSISTS (still catches 401 for unauth read attempts,
  but reads are AllowAny so 401 is only contingency). Client-side
  auth-check-on-write replaces silent-401-swallow for writes. 3+ PRs.
- **Breakage risk:** **MODERATE** — targeted to writes only. Frontend
  gates on `useAuthStore().token` before send. Reads continue anon.
  1-week frontend testing + deployment.
- **Reversibility:** EASY. Feature-flag toggleable at component level.
  Backend IsAuthenticated additions reverted individually. Hours-scale
  rollback.
- **F-CRIT-1 interaction:** COMPATIBLE. PURGE_SECRET stays in AllowAny
  reads OR moves to service-token; not blocking.
- **F-BND-4a interaction:** COMPATIBLE. `/api/v1/betting/place/` stays
  AllowAny + client-side auth-gate in BettingPage component. Demo-mode
  bets remain anon-possible; reviewers gated at component layer.
- **F-HIGH-3 resolution:** PARTIAL. PUBLIC_PATHS remains but populated
  only by AllowAny reads; write-side accretion prevented.
- **Timeline:** 4-5 weeks, 2-3 engineers.

**Option (c) — Per-endpoint permission registry.** (Cat B SECONDARY
DESIGN-PREP RECOMMENDATION)

- **Scope:** Same HTTP + frontend scope; augmented with per-endpoint
  metadata layer (Django admin OR durable config OR schema-generated).
  Authorization-plane addition (permission-floor classification per
  endpoint). No behavior change to HTTP or frontend auth mechanisms
  initially — metadata-only (design-prep phase).
- **Blast radius:** HIGHEST GRANULARITY. Permission-floor metadata per
  endpoint (class + read-vs-write + rate-limit + required roles). No
  immediate reclassification of existing code — registry is descriptive
  mapping layer.
- **Migration effort:** Cat B research-phase: 2-3 hours (evidence
  gathering + registry schema proposal). Post-arc (Group 2500 API arc):
  12-18 hours schema + admin UI + codegen integration IF Chris D-verdict
  selects.
- **Observability cost:** MINIMAL at research phase. Post-arc (Group
  2500): registry-aware observability + CI/lint rules.
- **Breakage risk:** **ZERO at research phase.** Registry is metadata-
  only; no runtime change.
- **Reversibility:** TRIVIAL. Orphan the registry file if rejected.
- **F-CRIT-1 interaction:** COMPATIBLE. Registry surface captures
  F-CRIT-1 metadata as `{path: '/api/home/purge-queue/', permission_floor:
  'service_token_required', criticality: 'CRITICAL'}`. Resolution
  becomes Group 2500 implementation task with evidence.
- **F-BND-4a interaction:** COMPATIBLE. Registry surface captures
  `{path: '/api/v1/betting/place/', permission_floor: 'AllowAny',
  demo_mode_allowed: true, reviewer_blocked: true, conflict: 'F-BND-4b_ACTIVE'}`.
- **F-HIGH-3 resolution:** FULL RESOLUTION (design-prep). Registry
  replaces PUBLIC_PATHS as source-of-truth. Post-arc: registry-enforcing
  CI lint prevents new endpoints without registry entry.
- **Timeline:** 2-3 hours research (Cat B); Group 2500 scope for
  authoring (no explicit Cat B commitment).

**Cat B RECOMMENDATION LEAN (for Chris D-verdict per acceptance
criterion #1):**

**Primary: Option (b) split-read-write with client-side auth-check-on-
write.**

Rationale:
1. Blast radius smaller (~50-80 write paths vs 265 PUBLIC_PATHS
   reclassification)
2. Migration effort MEDIUM (10-14 hours vs 18-25 hours option (a))
3. Reversibility EASY (feature-flag toggleable) vs DIFFICULT option (a)
4. Compatible with Cat A F-CRIT-1 + F-BND-4a (post-arc remediation not
   blocking)
5. Directly addresses F-B-CRIT-2 silent-401 SYSTEMIC (frontend gates
   writes → observable behavior)
6. Preserves demo-mode UX for bet-placement (comment "allow anonymous
   for demo mode" intent preserved)
7. Session 1171 503-fork extension scope REDUCED (writes only) vs
   option (a) all-endpoints

**Secondary: Option (c) per-endpoint permission registry as design-
prep artifact for Group 2500 API arc consumption.**

Rationale:
1. Long-term governance: registry enables per-endpoint enforcement +
   CI-lint at Group 2500 cost, not Cat B cost
2. Anti-scope preserved: Cat B does NOT author the registry (per parent
   §7.1 leak-vector guardrail); Group 2500 authors IF option (c)
   selected
3. Complements option (b): option (b) can ship first (immediate value);
   registry (option c) can layer on top at Group 2500 pace

**NOT recommended: Option (a) uniform IsAuthenticated.**

Rationale:
1. Blast radius too large; break-risk too high
2. F-CRIT-1 + F-BND-4a become BLOCKING dependencies
3. 6-8 week timeline vs 4-5 week option (b)
4. Reversibility DIFFICULT

**Chris D-verdict escalation at S2499 xx99 close:** Cat B recommends
option (b) as primary path; Group 2500 API arc can layer option (c)
as design-prep secondary regardless of (b) selection.

### 19.2 Ranked follow-on research queue

Rank by architectural uncertainty × risk × unblocked flows:

**Rank 1 (POST-ARC P0 batch — Chris D-verdict at S2499 xx99 close):**
- F-B-CRIT-1 + F-B-CRIT-2 uniformity path (option (a)/(b)/(c) selection)
- Cat A F-CRIT-1 PURGE_SECRET hardcoded fallback remediation (co-equal
  with Cat A rank-1)
- Cat A F-BND-4a bet-placement unauth-write remediation (co-equal)

**Sequencing note (Rigby SIGN cycle 1 Q17 fold — implementers-sequencing
discipline):** **F-B-CRIT-1 is the ENABLER; F-B-CRIT-2 is the
USER-VISIBLE SYMPTOM.** Implementers can sequence the co-equal batch as
"resolve F-CRIT-1 (PURGE_SECRET) + F-BND-4a (bet-placement) first as
concrete point-fixes; then attack F-B-CRIT-1 (permission-floor
declaration) which unlocks correct fix for F-B-CRIT-2 (silent-401)."
This avoids re-ranking the co-equal set into 1/1a/1b unless Chris
explicitly prefers a single-headline P0.

**Rank 2 (POST-ARC P1 batch):**
- F-B-HIGH-1 STAFF_REQUIRED_PATHS phantom-entries cleanup OR add
  explicit views
- F-B-HIGH-2 F-BND-4b reviewer-inversion dead-code cleanup (paired with
  Cat A F-BND-4a)
- F-B-HIGH-3 workspace-membership implicit-gate audit (CF-B2 Group 2600
  PA arc handoff)
- F-B-HIGH-4 `@authentication_classes([])` stacking consolidation
  (`views_preferences.py` primary target)

**Rank 3 (POST-ARC P2 batch):**
- F-B-MED-1 mythology empty `@permission_classes([])` cleanup
- F-B-MED-2 UnifiedUser.customer_role activation OR deprecation
  (Multi-tenant Phase 2 decision)
- F-B-MED-3 Session 1171 503-fork asymmetry documentation (CF-B5 Group
  1700 Observability arc)

**Rank 4 (POST-ARC observability + docs):**
- F-B-OWN-1 Authorization-plane governance ownership consolidation
- F-B-OWN-2 Endpoint-permission gatekeeper role designation
- F-B-OWN-5 Permission-floor observability instrumentation
- F-B-DOC-3 `docs/topics/authorization.md` authoring

### 19.3 Cross-arc coordination flags (5 emitted by Cat B)

**CF-B1 → Group 2500 API (per-endpoint registry design-prep candidate):**
- **Cat B deliverable:** Permission-floor classification framework +
  20-endpoint stratified sample + implicit-inheritance rate estimate
  (~65-85%) + three-option decision-space evidence + Cat B recommendation
  lean (option (b) primary; option (c) design-prep secondary).
- **Receiving arc responsibility:** IF Chris D-verdict selects option
  (c) OR option (b)+registry-layer, Group 2500 authors the per-endpoint
  registry (Django admin OR durable config + drf-spectacular integration
  + frontend codegen).

**CF-B2 → Group 2600 PA (workspace-context authorization plane):**
- **Cat B deliverable:** F-B-HIGH-3 workspace-membership implicit-gate
  finding — `WORKSPACE_AWARE_AGENTS` constant (20 agents) triggers
  `execute_with_workspace()` downstream; workspace-MEMBERSHIP
  enforcement in that method (not audited by Cat B). PA endpoints
  receiving `workspace_id` in payload trust the caller. Also flags
  dual `workspace_id` field asymmetry from S2204 evidence (GlobalPADock
  vs CommandCenterPage construction).
- **Receiving arc responsibility:** Group 2600 authors PA behavior
  spec — canonical workspace_id field location + resolver precedence
  + workspace-membership enforcement contract (`PAContextResolver` or
  equivalent).

**CF-B3 → Cat D S2404 (silent-401 SYSTEMIC severity input) — also serves
as the Group 2200 Frontend integration point (Rigby SIGN cycle 1 Q18
fold — clarification that CF-B3 subsumes Group 2200 mesh coordination):**
- **Cat B deliverable:** F-B-CRIT-2 silent-401 SYSTEMIC as downstream
  symptom of F-B-CRIT-1 permission-floor unobservability. Cat B
  recommendation option (b) directly addresses silent-401 at frontend
  layer (component-side auth-gate on write; server continues AllowAny
  reads). Cat B extension of S2203 F3 baseline. Client-side
  auth-check-on-write logic is squarely a Group 2200 Frontend contract;
  CF-B3 serves as the Cat D → Group 2200 integration point.
- **Receiving arc responsibility:** Cat D S2404 tailors silent-401
  audit scope per Cat B recommendation + owns Group 2200-facing
  integration. IF option (b) chosen: focus on client-side auth-gate
  rollout + error-boundary framework effectiveness. IF option (a) chosen:
  focus on typed-error envelope adoption + observable-401 propagation.
  IF option (c) chosen: register-aware silent-401 handling per registry
  metadata. (No CF-B6 → Group 2200 needed; CF-B3 fully covers.)

**CF-B4 → Group 2400 Arc (VIP demo authorization-plane pattern):**
- **Cat B deliverable:** VIP whitelist entries (18 total: 11 read +
  4 write + 3 cockpit) are platform's SECOND-most-explicit
  authorization-floor governance surface (after DRF `IsAuthenticated`
  default). Cat A §14 F-HIGH-1 two-layer classification. VIP demo
  provides REFERENCE PATTERN for per-surface authorization-floor
  design.
- **Receiving arc responsibility:** Cat C + Cat D cross-reference S2401
  §14 F-HIGH-1 two-layer classification in session-lifecycle + frontend-
  integration audits respectively. Group 2500 (if option (c)) can
  canonicalize VIP whitelist entries into registry with `vip_demo_allowed`
  flag.

**CF-B5 → Group 1700 Observability (auth event streaming + permission-
floor smoke-test coverage):**
- **Cat B deliverable:** Session 1171 503-fork asymmetry documentation
  (F-B-MED-3) across 5 code paths + permission-floor smoke-test coverage
  gap (Cat A §14.5 rate table 3/14 mechanism-level tests PRESENT; Cat B
  authorization-plane 0/? scenario-level tests). No `AuthorizationEvent`
  Event Bus routing at HEAD.
- **Receiving arc responsibility:** Group 1700 owns observability
  contract; can extend `AuthEvent` (if F-CRIT-2 addressed) with
  `AuthorizationDecisionEvent` model + Event Bus routing. Registry-drift
  detection metric (new endpoints added without registry entry).
  Post-arc T-slot candidate.

### 19.4 xx99 anchor-update recommendations (Cat B extension of Cat A
§19.4)

Cat A §19.4 recommended 6 anchor-update candidates. Cat B extends with
Cat B-specific recommendations:

**AU-B1 — `docs/topics/authorization.md` NEW (separate from Cat A
`docs/topics/auth.md` recommendation).** Rationale: authorization plane
is distinct from authentication plane; separate narrative anchor per
plane clarifies scope. Alternative: extend planned `docs/topics/auth.md`
with `§Authorization` subsection. **Rigby SIGN cycle 1 Q19 fold —
cross-linking discipline (avoids drifting anchors):** IF AU-B1 lands as
separate `docs/topics/authorization.md`, MUST cross-link to Cat A
`docs/topics/auth.md` + Group 2500 registry design-prep (when authored).
Preserve single-source-of-truth posture — either separate-with-cross-links
OR unified-with-subsection; do NOT create two drifting anchors.

**AU-B2 — `docs/PLATFORM_INVENTORY.md` §Authorization autoblock (extends
Cat A F-INV-1 §Auth candidate).** Populate with: total path() count,
implicit-inheritance rate, path-list registry counts, VIP whitelist
counts. Regenerable via management command per DOC_LIFECYCLE.

**AU-B3 — `docs/PLATFORM_WHAT_IT_IS.md` §Authorization narrative
subsection (extends Cat A F-INV-2 §Auth candidate).** Populate with:
authorization-plane structure narrative + Cat B canonical-seam framing
+ three-option decision space status + Chris D-verdict outcome (post
S2499).

**AU-B4 — `docs/research/platform_architecture_inventory.md` §3.27 row
27 update.** Extend Cat A revision with Cat B per-endpoint classification
framework + implicit-inheritance rate + three-option decision space
+ recommendation lean. Suggest maturity: PARTIAL preserved (mechanism
layer intentional; registry accreted; decision space pending Chris
D-verdict).

**AU-B5 — `docs/research/OPEN_ARCS.md` Group 2400 Auth row update.**
S2402 shipped; 3 of 6 shipped; next child = S2403 P3 Cat C Session
Lifecycle + Logout Cleanup Contract. Arc pin `pa-6279ead1714c4630`
PRESERVED per playbook §16 arc-standard behavior + MC-4 CODIFICATION-
CONFIRMED-with-scope-guardrails (MC-14 CANDIDATE-threshold-satisfied
extended to 3-arc-stages).

**AU-B6 — `docs/research/ARCHITECTURE_INDEX.md` v84 → v85 with §1.88
registration for S2402 Cat B.**

**AU-B7 — `00-START-NEXT-SESSION.md` overwrite with S2403 Cat C open
priorities.**

**Total AU items: 7 (Cat B extension); 13 combined with Cat A §19.4
6 items).**

---

## 20. Appendix

### 20.1 Files inspected

Direct-read at HEAD `798399ec`:

- `core/auth_middleware.py` (976 LOC) — full read (lines 1-570 verified;
  PUBLIC_PATHS 265 entries enumerated line-anchored; STAFF/REVIEWER lists
  verified)
- `core/vip_middleware.py` (104 LOC) — LOC verified via wc
- `core/services/fleet_auth_drf.py` (317 LOC) — LOC verified via wc;
  agent-report referenced FleetSignatureRequired at 176-212 +
  FleetCapabilityRequired at 215-262 + FleetSignatureExclusiveAuthentication
  at 275-308
- `core/settings.py:643-664` — DEFAULT_PERMISSION_CLASSES +
  DEFAULT_AUTHENTICATION_CLASSES grep-verified at 646-654
- `mythology/views.py:1167,1194` — grep-verified F-EMPTY-1 sites
- `core/urls.py:3353` — grep-verified `/api/v1/system/reality-check/`
  lambda view
- `docs/research/domains/auth/2400_auth_domain_scoping.md` §3.B +
  §7.1 + §2 evidence-provenance disclaimer
- `docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md`
  §1 + §3 + §14.5 + §17 F-DUP-2

Sub-agent reports (Agent 1-6) — 6 parallel Explore-Agent outputs
integrated per playbook §14 verifier-loop; conflicts resolved via
direct grep (see frontmatter `verifier_loop`).

### 20.2 Grep patterns used

- `DEFAULT_PERMISSION_CLASSES|DEFAULT_AUTHENTICATION_CLASSES` (core/settings.py)
  → confirmed line 646-654
- `path\(['"]api/v1/admin/|path\(['"]api/v1/system/|path\(['"]api/v1/metrics/admin/`
  (**/urls*.py) → 1 match at core/urls.py:3353 confirms F-B-HIGH-1
  phantom-endpoint finding
- `@permission_classes\(\[\]\)|permission_classes\s*=\s*\[\]` (**/*.py)
  → 2 matches at mythology/views.py:1167 + :1194 confirms F-B-MED-1
- `@authentication_classes\(\[\]\)|authentication_classes\s*=\s*\[\]`
  (**/*.py) → 4 files confirms F-B-HIGH-4
- `awk '/^    OPTIONAL_AUTH_PATHS = \[/,/^    \]/' core/auth_middleware.py`
  → 7 entries confirmed (Agent 3 undercount corrected)
- `wc -l` on core/auth_middleware.py (976) + core/vip_middleware.py (104)
  + core/services/fleet_auth_drf.py (317)

### 20.3 Unresolved unknowns (marked honestly per playbook §14)

- **Whole-platform implicit-inheritance rate exact number:** Cat B
  estimates 65-85% at endpoint level; exact number UNKNOWN pending
  per-ViewSet-class audit (deferred to Group 2500 API arc if option
  (c) selected).
- **`@permission_classes([AllowAny])` intent classification:** Agent 2
  counted ~140 occurrences across ~32 files; intent (intentional public
  vs debt-to-migrate) not audited per site — SPECULATIVE.
- **`@permission_classes([IsAuthenticated])` explicit vs default
  attribution:** Agent 2's 400+ count doesn't distinguish "explicit
  restatement" from "default carried through" — CONSERVATIVE assumption
  that all are explicit.
- **`FleetSignatureAuthentication` without `FleetSignatureRequired`
  misconfiguration count:** F-B-DUP-3 SPECULATIVE risk; no per-fleet-
  endpoint audit conducted.
- **`WORKSPACE_AWARE_AGENTS` `execute_with_workspace()` method behavior:**
  NOT audited per parent §7.1 anti-scope; workspace-membership
  enforcement contract UNKNOWN.
- **PA WebSocket consumer authorization coverage:** Cat A §6.4
  inconsistency baseline; Cat B did NOT re-enumerate consumers; 4
  consumer authorization patterns UNKNOWN in aggregate.
- **Django `auth.Group` + `auth.Permission` migration state:** Cat A
  `0001_initial.py:260-279` created join tables per Agent 1 report; not
  independently verified.

### 20.4 Conflicts between sources (verifier-loop history)

See frontmatter `verifier_loop` for full 5-conflict resolution:

1. Agent 3 OPTIONAL_AUTH_PATHS = 6 → HEAD-verified 7
2. Agent 3 STAFF_REQUIRED_PATHS phantom-endpoint claim → HEAD-verified
   2 of 3 phantom
3. Agent 6 DEFAULT_PERMISSION_CLASSES line 230-231 → HEAD-verified
   652-653; Agent 2 correct
4. Agent 3 @permission_classes([]) count = 2 → HEAD-verified 2 sites
   (mythology only); Agent 2 said 0 was incorrect grep-scope
5. Agent 3 @authentication_classes([]) count ~13 sites vague → HEAD-
   verified 4 files (occurrence-count TBD by SIGN cycle)

### 20.5 Rigby SIGN cycle 1 fold-target areas (pre-emptive per Agent 5
Rigby-SIGN-front-run analysis)

Cat B pre-emptively addresses Cat A weak-spot patterns:

1. **"WORKING" language overstatement:** Cat B uses classification
   language (PUBLIC / STAFF / REVIEWER / EXPLICIT / IMPLICIT / PHANTOM)
   rather than health judgments. Severity annotations reserved for
   conflicts + inversions + untraced endpoints.

2. **Co-equal ranking discipline:** §19.2 rank-1 co-equal-P0 batch
   includes F-B-CRIT-1 + F-B-CRIT-2 (Cat B extension) + Cat A F-CRIT-1
   PURGE_SECRET + Cat A F-BND-4a bet-placement co-equal per Cat A §19.2
   rank-1 preservation.

3. **DEFER-to-P1/P0-INVESTIGATE reframing:** §19.1 three-option decision
   space framed as "three options, each requiring pre-decision
   investigation of blast radius / migration cost / observability cost
   / breakage risk / reversibility per Cat A + Cat B measurement table;
   xx99 synthesizes findings for Chris D-verdict-request."

4. **Auth→downstream separation preservation:** Cat B §3 methodology
   declared that per-endpoint permission-floor classification is
   ORTHOGONAL to downstream event propagation (auth→Event Bus /
   auth→Celery); referenced S2400 §3.5 disposition table.

5. **Grep-verify binary claims front-run:** Cat B verifier-loop
   pre-verified all binary claims:
   - "No per-endpoint permission registry exists" → VERIFIED
   - "Fleet has permission classes" → VERIFIED
   - "DRF DEFAULT_PERMISSION_CLASSES = IsAuthenticated" → VERIFIED
   - "Django Groups+Permissions dormant" → VERIFIED

6. **Compound-drift catch (per Cat A F-BND-4 Q16 pattern):** Cat B
   §14.2 F-B-HIGH-2 documents `/api/v1/betting/place/` PUBLIC + REVIEWER-
   BLOCKED inversion as DEAD-CODE (REVIEWER_BLOCKED entry never reached
   because PUBLIC bypass processes first). Extends Cat A F-BND-4b HIGH
   from "reviewer inversion" to "dead-code registry entry."

**Emerging weak-spot pattern from Cat B (Rigby SIGN cycle 1 Q20 fold —
this SIGN cycle caught it):** **denominator ambiguity / metric provenance
drift.** Cat B's headline metrics (1,866 `path()` endpoints vs ~1,932 view
functions vs ~1,576 default-inherited endpoints vs 686 decorator
occurrences) span multiple denominators without single-source
reconciliation. Rigby's Q2 + Q5 folds insisted on:
- **Denominator disclosure per metric** ("measured-by" tag)
- **ESTIMATE/BOUND labels** where measurement discipline has known limits
- **Decorator-vs-class-attribute discipline** (decorator-only grep
  OVERSTATES "implicit inheritance"; class-attribute forms exist)
- **Grep-verify block in-methodology** showing exact regex + known
  false-negatives

Cat B applied these folds throughout §1 + §14.1 F-B-CRIT-1 methodology.
Future Cat B-analog audits (audits that measure whole-platform rates)
should PRE-EMPTIVELY apply denominator-discipline before Rigby SIGN.
**Playbook §20 candidate:** codify "measured-by discipline for
whole-platform rate measurements" as playbook §11.2 §14 rule requirement
(SEVENTH-consecutive-arc candidate rule — pending confirmation at
S2499 xx99 §10.2 codification review).

### 20.6 Playbook §11.2 template compliance (17th consecutive application)

Playbook §11.2 20-section child-audit template SEVENTEENTH-consecutive
application after S1301 + S1401 + S1501 + S1601 + S1701 + S1801 + S1901
+ S2001 + S2101 + S2102 + S2103 + S2104 + S2201 + S2202 + S2203 + S2204
+ S2401 prior sixteen. Compliance:

- All 20 sections present with exact headings (per playbook §11.2)
- §14 findings framework: 4 sub-tables (14.1 CRITICAL / 14.2 HIGH / 14.3
  MED / 14.4 LOW) + 14.5 permission-floor rate table
- §17 duplicate-model framework: 3 sub-findings (F-B-DUP-1/2/3) extending
  Cat A F-DUP-1/2/3/4
- §18 ownership-gap framework: 5 sub-findings (F-B-OWN-1 through -5)
  extending Cat A F-OWN-1/2/3
- §19 recommended-future-research framework: 4 subsections (19.1
  POSTURE-DECISION + 19.2 ranked queue + 19.3 CF-B1-5 + 19.4 anchor
  updates)
- §20 appendix framework: 7 subsections (files + grep + unknowns +
  conflicts + fold-targets + template compliance + fold ledger)

MC-10 codification-ready-pending-Chris at 6-arc baseline; Cat B extends
to 7-arc-child-audit-stage baseline (S1301 + S1401 + S1501 + S1601 +
S1701 + S1801 + S1901 + S2001 + S2101 + S2102 + S2103 + S2104 + S2201 +
S2202 + S2203 + S2204 + S2401 + S2402 = 18 consecutive applications
at S2402 close). SEVENTH-consecutive 4-batch × 5-Q = 20-Q child-audit
cadence CANDIDATE at SIGN cycle 1 close.

### 20.7 Rigby SIGN Cycle 1 Fold Ledger

**Rigby SIGN cycle 1 CLOSED 2026-07-05** via dedicated fresh SIGN pin
`pa-d1d4c68981fc4b3c` (minted via `session_tool.create_fresh` at cycle
open; retired at cycle close via `session_tool.retire` per playbook §15
SIGN-isolation discipline — THIRTEENTH consecutive dedicated fresh SIGN
pin retirement in Research OS after 10 xx99 + 1 parent-scoping-light-
SIGN + 1 Cat A child audit + this cycle).

**Cadence:** 4-batch × 5-Q = 20-Q per S2201-S2401 six-consecutive tested
child-audit pattern (SEVENTH-consecutive 20-Q cadence application).

**Overall Rigby verdict:** **SIGN-with-edits at MED-HIGH confidence
(~0.8)** — higher than S2401 Cat A (MED 0.74). Cycle 2 NOT required per
all 20 folds landable pre-Chris-ratification.

**Rigby overall commentary:**
- **Most accurate parts:** F-B-CRIT-1/2 headline framing, F-B-HIGH-1
  phantom-endpoint verifier-loop discipline, F-B-HIGH-2 dead-code
  reclassification with early-return conditional caveat, three-option
  decision space evidence table + Cat B recommendation lean.
- **Weakest parts:** denominator ambiguity across 1,866/1,932/1,576/686
  headline numbers (Q2 + Q5 folds — measurement-provenance discipline);
  DRF-default-IsAuthenticated-as-observability-contract vs
  correctness-contract precision (Q4 fold); (b)/(c) framing as
  stabilization-vs-end-state instead of primary-vs-secondary alone (Q16
  fold).
- **Missing area:** object-level + serializer-level authorization loci
  (Q11 fold — added §14.5 out-of-table completion); CI test-harness
  ownership gap F-B-OWN-6 (Q14 fold — added).
- **Biggest structural risk (Q20 fold):** denominator-ambiguity pattern
  emerging as Cat B-analog weak-spot for future whole-platform-rate
  measurement audits.

**20-fold ledger (per-Q + landing location):**

| Fold | Q | Rigby fold | Landing location |
|---|---|---|---|
| F1 | Q1 | Third-plane middleware-path-shadow-registry callout | §1 Executive Summary central-lens-answer |
| F2 | Q2 | Denominator reconciliation (1,866 / 1,932 / 1,576) + ESTIMATE bounded range ~80-90% + measurement-provenance disclosure | §1 F-B-CRIT-1 headline + §14.1 F-B-CRIT-1 body |
| F3 | Q3 | F-B-CRIT-2 causal claim reframed from "strict implication" to "necessary enabling condition to correctly fix at scale" | §1 F-B-CRIT-2 body |
| F4 | Q4 | DRF-default-IsAuthenticated as CORRECTNESS-contract clarification (NOT AUTOMATICALLY observability-contract-unless-paired) | §1 canonical-seam 4-way partition |
| F5 | Q5 | Decorator-only-grep OVERSTATES "implicit"; add class-attribute-form measurement discipline + grep-verify block | §14.1 F-B-CRIT-1 methodology + §1 F-B-CRIT-1 body + §20 emerging pattern |
| F6 | Q6 | F-B-HIGH-1 defense-in-depth credibility risk tag + risk-escalates-to-HIGH-if-registered-without-tests note | §14.2 F-B-HIGH-1 body |
| F7 | Q7 | F-B-HIGH-2 conditional-on-early-return verifier caveat | §14.2 F-B-HIGH-2 body |
| F8 | Q8 | F-B-HIGH-3 ownership-split tightening (Cat B owns identification; Group 2600 owns policy) | §14.2 F-B-HIGH-3 body |
| F9 | Q9 | F-B-HIGH-4 per-site severity-escalation-to-CRITICAL for auth_views_enhanced.py login/token flows | §14.2 F-B-HIGH-4 body |
| F10 | Q10 | F-B-MED-1 severity rationale rephrased as "hygiene debt; future-risk amplifier" (not severity inflation) | §14.3 F-B-MED-1 body |
| F11 | Q11 | §14.5 out-of-table completion — add object-level + serializer-level authorization loci as EXPERIMENTAL | §14.5 out-of-table section |
| F12 | Q12 | §16 F-B-BND-1 cross-link to F-B-HIGH-3 (boundary lens vs mechanism instantiation) | §16 F-B-BND-1 body |
| F13 | Q13 | §17 F-B-DUP-1 additional-role-carriers disclaimer + F-B-DUP-3 SPECULATIVE labeling discipline | §17 F-B-DUP-1 + F-B-DUP-3 bodies |
| F14 | Q14 | §18 F-B-OWN-6 NEW — CI test-harness ownership gap | §18 F-B-OWN-6 (new subsection) |
| F15 | Q15 | §13 maturity axis clarification (correctness WORKING-by-default; governance/observability EXPERIMENTAL → PARTIAL) | §13.5 new subsection |
| F16 | Q16 | §19.1 (b)/(c) framing as remediation-stabilization vs long-term-governance (not primary-vs-secondary) | §1 Cat B recommendation lean + §19.1 body |
| F17 | Q17 | §19.2 rank-1 sequencing one-liner (F-B-CRIT-1 enabler; F-B-CRIT-2 symptom) | §19.2 rank-1 body |
| F18 | Q18 | §19.3 CF-B3 clarification (subsumes Group 2200 Frontend mesh coordination; no CF-B6 needed) | §19.3 CF-B3 body |
| F19 | Q19 | §19.4 AU-B1 cross-linking discipline (avoids drifting anchors) | §19.4 AU-B1 body |
| F20 | Q20 | §20.5 emerging weak-spot pattern: denominator-ambiguity / metric-provenance drift + playbook §20 codification candidate | §20.5 body |

**All 20 folds LANDED pre-Chris-ratification per §16 draft-first
workflow.** Chris ratification pending via close-card.

---

**End of S2402 P2 Cat B Authorization + Permission-Floor Uniformity
Audit — Draft**

Draft `status: draft` on filesystem. Rigby SIGN cycle 1 pending via
dedicated fresh SIGN pin (arc pin `pa-6279ead1714c4630` PRESERVED
separately). Chris ratification via close-card post-SIGN-cycle-1.
