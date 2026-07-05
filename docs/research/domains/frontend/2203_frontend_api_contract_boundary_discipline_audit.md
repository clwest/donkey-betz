---
title: "Group 2200 — Cat C — Frontend↔Backend API Contract + Boundary Discipline Audit (S2203 P3)"
status: draft (post-Rigby-SIGN-cycle-1 SIGN-with-edits at HIGH confidence via dedicated SIGN pin pa-43bcb30dffd84ef9; 20 folds landed pre-commit-gate; awaiting Chris close-card ratification)
session: 2203
child_slot: P3_cat_c
domain_slug: frontend
research_group: 2200
mission_type: child_audit
date: 2026-07-05
arc_pin: pa-f7fd5016600f4513
head_commit_at_open: 0ce569f6
authority: |
  P3 child audit under Group 2200 Frontend (Contract-Surface arc). Scope
  inherited verbatim from parent scoping §5 Child C block
  (`2200_frontend_domain_scoping.md`) + parent §7.1 leak-vector guardrails
  + S2200 §5 Child C shape (C1 api-module inventory + C2 typed-contract-source
  inventory + C3 AUTH-DRIFT pattern rate + C4 cross-app-boundary sharing map
  + C5 silent-401 discipline rate).

  This doc is RESEARCH AUDIT only. It captures a **static snapshot** of the
  frontend↔backend REST API contract surface at HEAD `0ce569f6` on `main`
  (2026-07-05, LOCAL environment). It enumerates the 93 `*Api` module
  exports in `frontend/src/lib/api.ts` (4,194 LOC — verified against
  S2201 §5 baseline of 93 exports; UNCHANGED), plus the 1 typed
  exception `frontend/src/lib/cockpitApi.ts` (513 LOC / 54 exported
  functions / 96% typed via `@/types/cockpit`), plus the 29-line
  `frontend/src/lib/apiClient.ts` X-UI-Scope helper wrapper. It measures
  typed-contract discipline (**63 of 919 api.ts calls carry generic type
  parameters = 6.85% coverage; 47 exported interface/type declarations
  in api.ts most of which are orphan**), silent-401 handling rate (**1
  global handler at api.ts:48-56; whitelist substring `/auth/` +
  `/login`; ~100% swallow rate for non-whitelist 401s**), auth-drift
  pattern rate (**S1505 §14.3 two-sided framing GENERALIZES SYSTEMICally
  across all sampled non-sports surfaces**), and cross-app-boundary
  sharing map (**4 primary cross-cutting api-modules — humanApi,
  assistantApi, workspaceApi, contentApi — across major surfaces**). It
  delivers POSTURE-DECISION evidence toward the "no API contract
  source-of-truth" S1505 §15.5 debt generalization test per §20.6.

  Explicit non-scope per parent §7 + §7.1 leak-vector guardrails:
  - Does NOT design an API contract source-of-truth — that is the
    Group 2500 API scope per parent §7.1 Child C → Group 2500 guardrail.
  - Does NOT propose typed-schema-generation implementation (OpenAPI
    codegen wiring, Zod adoption, tRPC migration) — inventory of
    remediation OPTIONS only, no authoring commitment.
  - Does NOT propose auth-session model changes (Group 2400 guardrail);
    silent-401 is symptomatic + descriptive only at frontend-symptom
    scope; systemic-severity classification pending Group 2400 Auth
    spec.
  - Does NOT enumerate the WebSocket consumer surface — that IS
    Child B S2202 scope (shipped 2026-07-05). WS payload shape
    `event.type` string dispatch is referenced only as cross-arc
    parallel evidence (§17 T7 joint 2500+2600).
  - Does NOT audit persistent-state discipline — that IS Child D
    (S2204) scope; response caching / react-query staleness / token
    persistence-in-Zustand are noted for cross-arc flag only.
  - Does NOT propose PA behavioral spec for assistantApi consumers
    (Group 2600 guardrail); PA-adjacent surfaces are inventoried only.
  - Does NOT audit the mobile app (Group 2300).
  - Does NOT delete DEAD-CANDIDATE api-modules; cleanup is post-arc
    T-slot per §7 anti-scope "No fixes."

  Load-bearing inheritance chain re-attested at S2203 open:
  - PLATFORM_INVENTORY §Frontend row (61 routes) — verified 2026-07-02
    against runtime; **no API-module count row exists in inventory —
    flagged for xx99 inventory-augmentation.**
  - S1505 §14.3 F3 AUTH-DRIFT two-sided framing — re-verified at HEAD
    `0ce569f6` (see §14 F3); silent-401 pattern at
    `frontend/src/lib/api.ts:48-56` UNCHANGED; whitelist substring
    `/auth/` + `/login` UNCHANGED; per-surface exposure rate confirmed
    per A3.
  - S1505 §15.5 F4 "No API contract source-of-truth" MED→HIGH
    structural debt with 4-way parent cause claim — re-verified
    SYSTEMIC at HEAD `0ce569f6` (see §14 F4 + §15.5); 7 of 8
    non-sports modules sampled replicate all 4 pathologies at ~100%
    replication rate.
  - S2004 §14.6 Cat F CONSOLIDATION `humanApi` cross-domain sharing —
    verified at HEAD `0ce569f6` (see §17.2); 4 primary cross-cutting
    surfaces identified.
  - S2200 §5 Child C per-surface reporting constraint (Q1 STRENGTHEN
    fold) — findings reported per major surface (workspace / betting /
    command-center / PA / other) in addition to axis-level rollup.
  - S2200 §5 Child C timebox + sampling rule (Q10 STRENGTHEN fold) —
    1-session timebox honored via **6 parallel Explore sub-agents**
    per playbook §13 (A1-A6 dispatched in single batch 2026-07-05).
  - S2201 §14.6 silent 401 systemic finding — Child A single-page
    evidence; Child C extends via silent-401 rate audit across whole
    api.ts (§14 F3).
  - S2202 §17 T6 joint 2500+2600 WS/polling consolidation flag —
    preserved + extended to REST-side (§17 T7).
verifier_loop: |
  Pre-draft verifier-loop (per playbook §14 + parent §5 SESSION READY
  CHECK) executed 2026-07-05 at HEAD `0ce569f6`:
  1. api.ts line-count re-verified: `wc -l frontend/src/lib/api.ts` =
     4,194 LOC (matches S2201 baseline).
  2. `frontend/src/lib/apiClient.ts` = 29 LOC (X-UI-Scope helper),
     `frontend/src/lib/cockpitApi.ts` = 513 LOC (typed exception).
     No `frontend/src/api/` directory exists — parent scoping §5
     Child C load-bearing input referenced `frontend/src/api/*` which
     is a **path-reference drift** (actual path is
     `frontend/src/lib/`); flagged §14 F1 + §20.5 conflict.
  3. `*Api` export count in api.ts = **93** (grep `^export const
     \w+Api\b` = 93 matches) — S2201 §5 baseline UNCHANGED.
  4. Total `api.(get|post|patch|delete|put)(` bare-call count in
     api.ts = **856**. Total generic-parameterized
     `api.(get|post|patch|delete|put)<` typed calls in api.ts = **63**.
     Combined denominator = **919 total endpoint calls in api.ts**.
     **Typed-response coverage rate = 63/919 = 6.85%.**
  5. `^export (interface|type)\s+\w+` in api.ts = **47** exported type
     declarations. Cockpit exception: `frontend/src/lib/cockpitApi.ts`
     imports 44 types from `@/types/cockpit` (line 2-44) and uses them
     across 52 of 54 exported functions (96% typed).
  6. `frontend/src/types/` directory contains **1 file**:
     `cockpit.ts` (821 LOC; **104 exported types**). No
     other `frontend/src/types/*` files exist. This makes cockpitApi
     the sole exception across the entire frontend API layer.
  7. Silent-401 interceptor at `frontend/src/lib/api.ts:48-56` —
     re-read at HEAD `0ce569f6`; UNCHANGED from S1505 baseline. Only 1
     401-handling site in whole `frontend/src/` — verified via grep
     `error\.response\?\.status === 401`.
  8. Auth attach via axios interceptor at `frontend/src/lib/api.ts:27-40`
     — reads `useAuthStore.getState().token` and sets
     `Authorization: Token <token>` header. `withCredentials: true`
     globally (line 23). No component-side auth-header overrides
     detected (grep zero matches for `Authorization` outside api.ts).
  9. **drf-spectacular installed-but-not-fully-wired verifier finding:**
     - `requirements.txt` — drf-spectacular==0.28.0 declared.
     - `core/settings.py` — `SPECTACULAR_SETTINGS = {...}` declared.
     - `core/*.py` — **zero `@extend_schema` decorators** (the vast
       majority of REST endpoints live in `core/`).
     - `sports/views.py` — **16 `@extend_schema` decorators** (line 58,
       117, 164, 344, 357, 385, 500, 568, 744, 848, 887, 907, 924, 953,
       987, 1023). **drf-spectacular is partially wired in the `sports/`
       Django app only.** Contradicts A2's initial "zero decorators"
       claim; corrected in §14 F5 + §20.5.
     - Grep for `openapi-typescript|orval|kubb|swagger-codegen` in
       `frontend/package.json` = **0 matches**. No frontend codegen.
     - Grep for `zod|io-ts|valibot|superstruct|yup` in
       `frontend/package.json` = **0 matches**. No runtime validation.
  10. **DEAD-CANDIDATE list refinement:** Sub-agent A4 initially
     flagged 27 api-modules as "zero-consumer." Verifier grep on
     `\.(overview|list|...)` invocations for each caught 7 modules
     ACTUALLY CONSUMED by AIConsciousnessTab + CommandCenterPage +
     others (memoryPalaceApi, moodApi, timeTravelApi, evolutionApi,
     relationshipsApi, timeCapsuleApi, homeApi). **A4's DEAD-CANDIDATE
     list overclaimed** — actual DEAD-CANDIDATE size is 15-20 modules
     (final N pending §14 F6 grep sweep). Recorded §14 F6 with
     DEAD-CANDIDATE / INTENT-NEUTRAL language per S2202 F6 precedent.
  11. Cross-cutting api-modules verified (grep `bettingApi\.|humanApi\.|
     assistantApi\.|workspaceApi\.|contentApi\.|agentsApi\.|sportsHubApi\.`
     across `frontend/src/**/*.{ts,tsx}`) = **132 total occurrences
     across 24 files**. 4 primary cross-cutters confirmed: humanApi,
     assistantApi, workspaceApi, contentApi.
  12. Auth-endpoint whitelist verification — `api.ts:50` whitelist
     `url.includes('/auth/') || url.includes('/login')` — all
     `/api/v1/auth/*` endpoints match (core/urls.py:2183-2198 confirmed
     10 auth-endpoints all under `/auth/`). Legacy `/accounts/logout/`
     misses whitelist substring but redirected to `/api/v1/auth/logout/`
     — not a live risk today; flagged §14.4 F3.5 observation.
  13. Repo state at S2203 open: `main @ 0ce569f6` (S2202 arc-cascade
     commit); working tree clean except `.claude/scratch/` untracked.
  14. Arc pin `pa-f7fd5016600f4513` verified ACTIVE via
     `platform_config_tool overview` (service_context: local; arc-pin
     acknowledged) at S2203 open — TENTH formal arc pin under Research
     OS, preserved through S2202 close per playbook §16.
  15. CODEOWNERS existence check — no `.github/CODEOWNERS` file at
     repo root or `.github/` (matches S2201 §18.1 F4 + S2202 §18.1
     baselines UNCHANGED).
owner: claude (drafted S2203; Rigby SIGN cycle 1 folds will land pre-commit)
---

# Session 2203 — Group 2200 Cat C — Frontend↔Backend API Contract + Boundary Discipline Audit

> **Static snapshot.** This audit captures the frontend↔backend REST API
> contract surface at HEAD `0ce569f6` on `main` (2026-07-05, LOCAL). It
> is a photograph, not a mechanism explainer. Route + page + layout +
> component patterns is Child A (S2201, shipped). WebSocket consumer
> surface + `ui.render_hint` envelope is Child B (S2202, shipped).
> Session-scoped state + persistence discipline is Child D (S2204,
> next). This document delivers what parent §5 Child C required: (a)
> api-module inventory (93 `*Api` exports in `frontend/src/lib/api.ts`
> + 1 typed exception `frontend/src/lib/cockpitApi.ts` + 1 helper
> wrapper `frontend/src/lib/apiClient.ts`); (b) typed-contract-source
> inventory (63 of 919 calls = 6.85% typed; cockpitApi = 96% typed
> exception); (c) AUTH-DRIFT pattern rate (silent-401 systemic;
> whitelist substring hardcoded); (d) cross-app-boundary sharing map
> (4 primary cross-cutting modules — humanApi, assistantApi,
> workspaceApi, contentApi); (e) silent-401 vs observable-error
> discipline rate (~100% swallow for non-whitelist 401s); (f)
> POSTURE-DECISION evidence plan §20.6 owed to xx99 on whether S1505
> §15.5 "no API contract source-of-truth" debt generalizes across all
> api-modules or is `/betting`-specific.

## 1. Executive Summary

**Contract-surface posture — one-sentence answer to the Child C slice of
the central lens question:** The frontend↔backend REST API surface at
HEAD `0ce569f6` is **an untyped mega-module mesh with a typed
ops-island and a silent-failure default** — 93 of 94 api-modules
(**98.9%**) live inside a single 4,194-line `frontend/src/lib/api.ts`
file with **6.85% typed-response coverage locally within api.ts (Coverage
A: 63/919 calls); ~11.8% typed-coverage globally across the whole
frontend API surface (Coverage B: 115/973 = 63 typed in api.ts + 52
typed in cockpitApi.ts / 919+54 total calls)** — while the sole typed
**island** `frontend/src/lib/cockpitApi.ts` (54 functions, 96% typed
via `@/types/cockpit`) is scoped to the `/cockpit/*` ops-surface only
and **demonstrates the achievable discipline path, not coverage**
(Rigby SIGN cycle 1 Q7 STRENGTHEN 2026-07-05 fold — cockpitApi is an
existence proof that typing is feasible, not a cross-surface exception); auth-drift is
inherited from a single global silent-401 interceptor that swallows
any non-`/auth/` non-`/login` 401 across ~1,300 downstream call
sites; contract source-of-truth infrastructure (drf-spectacular) is
INSTALLED but wired in only 1 of ~25 Django apps (**`sports/views.py`
16 `@extend_schema` decorators**) — **partial foundation present;
current wiring is sports-only, `core/*.py` has 0 decorators — treat as
HIGH debt unless an explicit "sports-only" wiring decision exists in
history** (Rigby SIGN cycle 1 Q1 STRENGTHEN 2026-07-05 fold); typed-schema client codegen is
ABSENT from the frontend package.json; runtime response validation
(zod / io-ts / valibot) is ABSENT.

**Central Child C finding — S1505 §15.5 "no API contract
source-of-truth" hypothesis is CONFIRMED SYSTEMIC (with surface variance,
per Rigby SIGN cycle 1 Q6 STRENGTHEN 2026-07-05 fold).** Per the S2200 §2.4 four-falsifier framing, three of the
four criteria resolve against sports-outlier / surface-local /
domain-specific downgrade paths at Child C level; only F2 (typed-
contract discipline outside sports) resolves as PARTIAL exception
(cockpitApi.ts is the sole typed api-module). **F1 evidence —
non-betting violation-index** (per-axis rubric to avoid
mixed-denominator arithmetic): typed-response coverage = **63/919 =
6.85%** (~93% untyped); auth-drift discipline = **1/1 global handler
in swallow-by-default mode** (100% silent-401 rate for non-whitelist
endpoints); response-shape validation = **0 of 919 calls validated at
runtime** (0% zod/io-ts adoption); cross-cutting api-module boundary
respect = **4 modules cross ≥2 major surfaces** (humanApi 4 surfaces
+ assistantApi 3 + workspaceApi 3 + contentApi 2). **F1 fails on 3 of
4 sampled axes**; F2 pattern (typed contracts) has a partial exception
(cockpitApi at 96%, but scope is limited to ops-surface). **F4
evidence — non-betting surfaces show identical patterns**:
agentsApi 0/7 typed, contentApi 0/48 typed, humanApi 0/20 typed,
heartApi 0/5 typed, workspaceApi 0/18 typed, homeApi 0/3 typed. Only
platformApi (30/30 typed) + assistantApi (5/20 typed) + governmentApi
(2/9 typed) + cockpitApi (52/54 typed) hold typed discipline
partially.

**Per-surface variance (Rigby SIGN cycle 1 Q6 STRENGTHEN 2026-07-05
fold — SYSTEMIC-with-surface-variance verdict; all surfaces below
acceptable bar):**

| Surface | Typed-response rate | Assessment |
|---|---|---|
| Betting | 0/25 = **0%** | UNMET (below acceptable bar) |
| Workspace | 0/18 = **0%** | UNMET |
| Command-Center | partial via platformApi (30/30 inline generics) | PARTIAL — not exported Response types |
| PA | 5/22 = **~23%** | PARTIAL — highest surface still under 25% threshold |
| Ops (cockpit) | 52/54 = **96%** | STABLE — sole typed island (Q7 STRENGTHEN fold) |
| Other (rag/blog/collective/analytics/etc.) | ~0% | UNMET |

**SYSTEMIC-with-surface-variance:** most surfaces at/near 0%, PA
highest at ~23% but still under 25% acceptable-bar threshold, cockpit
ops-surface 96% but scope-limited. Pattern is SYSTEMIC deficiency
across all product surfaces; variance is real but does not move any
surface above the acceptable bar.

**Sampling sufficiency note (Rigby SIGN cycle 1 Q8 STRENGTHEN
2026-07-05 fold):** The 3-module 100% replication rate (A5 sample
size) is sufficient to claim "observed in all sampled non-sports
modules" but NOT alone sufficient to claim "SYSTEMIC across whole
repo." The SYSTEMIC claim is anchored to the macro-evidence:
**api.ts centralization + 919 total calls + 6.85% typed = structural
evidence at whole-file scale**, corroborated by 3-module pathology
sampling as strong signal. If further evidence is needed, xx99 can
queue a broader repo-wide grep counter as R11 post-arc T-slot.

**S1505 §15.5 4-way parent cause claim generalizes to
whole-frontend REST API contract surface** — xx99 elevates urgency
accordingly.

**Denominator contract (Rigby SIGN cycle 1 Q9 CLEAN + micro-fold
2026-07-05 — prevents reader conflation across 3 different rates):**

- **B1 typed-response coverage** — unit of analysis = api.ts calls;
  scope = single-file (`frontend/src/lib/api.ts` = 919 total calls;
  63 typed); sampling method = grep on `api\.(get|post|patch|delete|put)<`
  vs `api\.(get|post|patch|delete|put)(`. Rate: **6.85% (Coverage A,
  api.ts only)** / **~11.8% (Coverage B, global with cockpitApi.ts
  merged: 115/973)**.
- **B2 silent-401 discipline** — unit of analysis = gated-endpoint
  call-sites; scope = api-modules whose backend view carries
  `permission_classes=[IsAuthenticated]`; sampling method = A3
  per-surface exposure estimate (grep-derived; **may overcount
  wrappers/duplicates** — Rigby SIGN cycle 1 Q14 STRENGTHEN fold).
  Rate: **~630 of ~1,300 gated call-sites at silent-401 risk (~48%
  estimate, grep-based, hedged for wrapper duplicates)**.
- **B3 cross-cutter concentration** — unit of analysis = api-modules
  that cross ≥2 major surfaces (workspace / betting / command-center
  / PA / other); scope = 93 modules in api.ts + cockpitApi + apiClient
  = 94 total; sampling method = grep on module-usage across
  `frontend/src/**/*.{ts,tsx}`. Rate: **4 of 94 modules cross ≥2
  major surfaces (~4.3%)**.

The three rates measure different phenomena and should not be
mentally combined.

**Contract-surface acceptance criteria (S2200 §lens block; Child C
scores the 3 criteria in scope):**

| Criterion | Status | Evidence |
|---|---|---|
| 1 — Every route maps to owned page + layout with declared consumer contract | **PARTIAL** (Child A concern; Child C extends) | 47 pages consume api-modules directly (no hooks-layer abstraction) per A4; the "consumer contract" surface exists at api-module level but is **not typed** in 93 of 94 modules. |
| 3 — Frontend↔backend API calls are enumerated + typed against a single source of truth | **UNMET** | 93 modules × avg 15 methods = ~1,417 method definitions across api.ts; 6.85% typed (63/919 calls); 47 exported interfaces most orphan; 0 OpenAPI codegen; 0 runtime validation; sole typed island = cockpitApi.ts (96% typed) via `@/types/cockpit`. **SoT ABSENT** at platform scale. |
| 6 — Failure-mode + boundary behavior standardized + observable (auth-failure handling) | **UNMET** | Silent-401 default across ~1,300 call sites; whitelist substring hardcoded (`/auth/` + `/login`); no per-endpoint auth-gate; no token-refresh mechanism; no error boundaries (S2201 §14 baseline). |

**POSTURE-DECISION §20.6 preliminary evidence toward S1273 32-domain
row 18 "STABLE + DEEP":** **downgrade candidate to WORKING + MEDIUM
extends S2201 §20.6 recommendation**. Child C evidence: typed-contract
discipline is PARTIAL (islands: cockpit ops-surface + platformApi +
assistantApi partial); silent-401 discipline is UNMET; SoT
infrastructure is INSTALLED-BUT-UNWIRED (drf-spectacular). Final
POSTURE-DECISION resolution deferred to S2299 canonical summary after
S2204 close.

**Five headline findings:**

- **F1 — SoT ABSENT at platform scale + PARTIAL WIRING evidence in
  `sports/`** — `requirements.txt` includes drf-spectacular==0.28.0;
  `core/settings.py` declares `SPECTACULAR_SETTINGS`; but only
  `sports/views.py` (16 `@extend_schema` decorators) uses the
  infrastructure. The other ~25 Django apps under `core/` +
  `intelligence/` + `ai_core/` + `discord/` + `sports/` (non-view
  modules) have zero decorators. Frontend has zero codegen tooling
  (`orval`, `kubb`, `openapi-typescript`) and zero runtime validators
  (`zod`, `io-ts`). **Class: `technical_debt` (structural).** Severity:
  **HIGH baseline; CRITICAL for money-path + governance-path endpoints**
  (betting.placeBet, wager settlement, billing.stripe, humanApi.decide)
  where silent shape-drift breaks silent-failure operations. **Risk
  channel framing (Rigby SIGN cycle 1 Q3 CLEAN 2026-07-05 fold):**
  latent-but-active risk channel — silent auth failures (§14 F3) +
  untyped contracts on critical flows compound at critical surfaces;
  does not require current-incident-rate claims to sustain HIGH
  severity.
- **F2 — Silent-401 SYSTEMIC across ~1,300 call sites via single
  global interceptor** — `frontend/src/lib/api.ts:48-56` is the sole
  401 handler in the whole `frontend/src/`. Whitelist substring
  `url.includes('/auth/') || url.includes('/login')` triggers logout +
  redirect; every other 401 is `console.warn`-logged and silently
  swallowed at the caller. Per-surface exposure per A3: Workspace 95%,
  PA 100%, Command-Center 60%, Betting 30% (writes only, reads are
  `AllowAny`), Other ~70%. Generalizes S1505 §14.3 F3 AUTH-DRIFT
  two-sided framing from single-route to whole-frontend. **Class:
  `drift` / `technical_debt` (frontend-symptom).** Severity: **HIGH
  frontend-symptom + Group 2400 Auth dependency** (silent-401 severity
  scales with backend permission-floor uniformity; Group 2400 owns the
  session-model resolution).
- **F3 — 4 primary cross-cutting api-modules span ≥2 major surfaces** —
  `humanApi` (20 methods, consumed by BettingPage + CommandCenterPage +
  BoardroomTab + DecisionDetailModal + unifiedStore = 5+ surfaces),
  `assistantApi` (22 methods, consumed by GlobalPADock + AttentionWidget
  + paStore + GovernmentPage = 4 surfaces), `workspaceApi` (18 methods,
  consumed across workspace/tabs/* + CommandCenterPage + GlobalPADock +
  DemoHomePage = 4+ surfaces), `contentApi` (51 methods, consumed by
  ContentPage + VideoStudioPage + ImageStudioPage + ContentStudioTab +
  GlobalPADock = 5+ surfaces). Confirms S1505 §16.2 `humanApi`
  observation + S2004 §14.6 Cat F CONSOLIDATION pattern; extends to 4
  primary cross-cutters. **Class: `overcoupling` observation (design
  candidate).** Severity: **MED-HIGH** for shared surfaces (edit blast
  radius crosses domain boundaries).
- **F4 — Mega-module god-file at `frontend/src/lib/api.ts`
  (4,194 LOC, 93 exports)** — Single-file api-module registry mirrors
  the S1505 §15.4 + S2201 §14.6 god-component pattern at the API layer.
  `platformApi` alone (line 3257-3879 = ~622 LOC) is ~29% of the file's
  method count (414 methods). Session-annotation date-range spans
  **Session 688 → Session 1095 = 407 sessions of continuous churn**.
  Comparable to the S2201 6-god-component pattern extended to
  infrastructure layer. **Class: `extraction_candidate` (structural).**
  Severity: **MED-HIGH** (churn-heavy monolith increases drift risk;
  no per-module owner discipline).
- **F5 — DEAD-CANDIDATE api-modules recur with INTENT-NEUTRAL
  disposition** — **18 verifier-confirmed DEAD-CANDIDATE modules;
  expect ~18-25 final pending R3 full TSX import/usage sweep** (Rigby
  SIGN cycle 1 Q4 STRENGTHEN 2026-07-05 fold — candidate list not
  final inventory). Have zero consumer usage in `frontend/src/`. Examples
  confirmed by verifier grep: `nervousApi`, `skinApi`, `spineApi`,
  `muscularApi`, `circulatoryApi`, `digestiveApi`, `brainApi`,
  `immuneApi`, `agentOrchestrationsApi`, `autonomousApi`,
  `classificationApi`, `ecosystemApi`, `legacyLearningApi`,
  `journeyApi`, `researchApi`, `workspaceTriggerConfigsApi`,
  `integrationHealthApi`, `llmApi`. **Class:
  `dead_code`-DEAD-CANDIDATE (per S2202 F6 precedent — DEAD-CANDIDATE
  until delete-proof gate: no imports + no runtime logs + no
  maintainer-intent evidence).** Severity: **LOW-MEDIUM**
  (documentation debt + code hygiene, not runtime risk).

**S1505 4-falsifier verdict:** **SYSTEMIC (with partial exception).**
F1 fails (typed-contract violation rate ~93% across api.ts); F4 fails
(non-betting surfaces show identical typed-contract absence patterns).
Only F2 has partial exception (cockpitApi.ts + platformApi + partial
assistantApi = 3 modules with typed discipline out of 94 =
**~3.2% typed-module rate**). F3 (Signal Engine emission absence) is
domain-specific + backend concern. Governance urgency at xx99 elevates
accordingly.

## 2. Domain Purpose

**Q1 — What does this domain do?**

The Frontend↔Backend REST API contract surface at Child C's slice is
the **layer that translates React component data needs into HTTP
requests against the Django REST Framework backend, then translates
the HTTP responses back into TypeScript-typed (or untyped) values that
components can render or store**. It comprises three primary files
under `frontend/src/lib/`:

- **`api.ts` (4,194 LOC)** — 93 domain-scoped `*Api` module exports,
  each a plain-object collection of endpoint-methods that internally
  call `api.get()` / `api.post()` / `api.patch()` / `api.delete()` /
  `api.put()`. Ships the singleton `axios.create()` instance with a
  global `Authorization: Token` interceptor + global 401 response
  interceptor.
- **`cockpitApi.ts` (513 LOC)** — 54 typed function exports (async
  wrappers around `api.get<T>` / `api.post<T>`) with return-type
  contracts imported from `@/types/cockpit`. Sole typed island; scope
  is ops/cockpit surface only (runs, incidents, autopilot, approvals,
  ops metrics, config governance).
- **`apiClient.ts` (29 LOC)** — 2 exported helpers `scopedGet` +
  `scopedPost` that wrap `api.get/post` with an `X-UI-Scope` header
  for backend request-log filtering (Session 968 provenance). Not an
  additional client; a header-scope decorator only.

**Q2 — What is the domain NOT?**

The domain is **not**:
- **The backend URL space** (`core/urls*.py` + `sports/urls.py` +
  `intelligence/urls.py` — that is Group 2500 API scope for canonical
  API design).
- **The backend view layer** (`core/views_*.py` — Group 2500 owns the
  BE-side of the contract).
- **The auth session model** (`core/auth_views.py` + `core/models.py`
  UserProfile + token-authentication — Group 2400 owns).
- **The WebSocket consumer surface** (`core/routing.py` + consumers
  under `core/consumers*.py` — Child B S2202 owned).
- **The state-persistence surface** (`frontend/src/stores/*` Zustand
  + persistence middleware — Child D S2204 owns).
- **The mobile app API layer** (Group 2300 Mobile scope).
- **A single-endpoint operator UI or admin console.** api.ts is a
  cross-cutting registry, not a page-specific fetcher.

## 3. Canonical Entry Points

**Q3 — What are the load-bearing entry points to this domain?**

| Entry point | File:line | Purpose |
|---|---|---|
| axios instance | `frontend/src/lib/api.ts:13-24` | Base URL from `VITE_API_URL || '/api'`; 90s timeout; `withCredentials: true` for Django session cookies. |
| Auth request interceptor | `frontend/src/lib/api.ts:27-40` | Injects `Authorization: Token <token>` from `useAuthStore.getState().token`; DEV/`/platform/` debug logging. |
| Silent-401 response interceptor | `frontend/src/lib/api.ts:43-62` | Handles 401 responses; whitelist substring `/auth/` + `/login` triggers logout + redirect to `/login`; all other 401s log warning and pass rejection to caller (silent swallow at caller side). |
| Cockpit typed-response entry | `frontend/src/lib/cockpitApi.ts:2-44` + `frontend/src/types/cockpit.ts:1-821` | Sole typed api-module; 44 type imports from `@/types/cockpit`; 96% coverage across 54 exported functions. |
| X-UI-Scope helpers | `frontend/src/lib/apiClient.ts:8-30` | Scoped GET/POST helpers for backend request-log filtering (Session 968). |
| Domain-scoped api-modules (93) | `frontend/src/lib/api.ts:67-4193` | Each `export const \w+Api = { ... }` is an entry point for its domain; enumerated in §5.2. |
| Component-level direct api calls | 45 files in `frontend/src/**` | Direct `api.get(...)` / `api.post(...)` invocations bypassing api-modules; enumerated in §5.4. |

## 4. Major Models

**Q4-Q5 — What models are load-bearing? What is the ownership boundary?**

The frontend REST API contract surface **owns no Django models** — it
is a client of the backend model space. Cross-references:

| Backend model surface (owner) | Consumed via | FE-side type SoT? |
|---|---|---|
| DRF Token (`rest_framework.authtoken`) | `api.ts:29-35` sets `Authorization: Token <key>` | User type in `authStore.ts` (not `@/types/*`); no shared type import |
| UserProfile + User (`core/models.py`) | `authApi.getUser()` → `/v1/auth/user/` | User interface hand-declared in `authStore.ts`; not exported as canonical User type |
| AgentExecution (`core/models.py`) | `agentsApi.executionDetail()` → `/v1/agents/execution/{id}/` | UNTYPED at api.ts:91; typed at `cockpitApi.getRunDetail()` via `RunDetail` from `@/types/cockpit:141` |
| SportsBettingBrief + BettingWager (`core/models.py`) | `bettingApi.recent()` / `bettingApi.trackRecord()` / `bettingApi.logWager()` | UNTYPED at api.ts:1229-1276 |
| HumanAttentionItem (`core/models.py`) | `humanApi.attention()` + `humanApi.decide()` → `/human/attention/`, `/human/decide/` | UNTYPED at api.ts:1607-1665 |
| WorkspaceProject + WorkspaceOperation (`core/models.py`) | `workspaceApi.list()` + `workspaceOperationsApi.*` | UNTYPED at api.ts:1695-1745 |
| Deliverable (`core/models.py`) | `deliverablesApi.*` → `/deliverables/` | UNTYPED at api.ts:4095-4109 |
| Incident + Alert + OpsRun (cockpit surface) | `cockpitApi.getIncidents()` / `getAlerts()` / `getOpsRuns()` | TYPED via `IncidentListResponse`, `AlertsResponse`, `OpsRunListResponse` from `@/types/cockpit` |

**Ownership rule:** Backend `core/models.py` is the source of truth
for entity shapes. Frontend has **no canonical mirror**; component
authors read backend view code to infer response shape, then declare
inline interfaces at call site (S1505 §15.4 pattern). The sole
exception is the cockpit ops-surface, where hand-written types in
`frontend/src/types/cockpit.ts` mirror the backend shape (still
hand-derived, not generated).

## 5. Major Services

**Q6-Q7 — What services live in this domain? What is the runtime flow?**

### 5.1 Files under `frontend/src/lib/` (verified 2026-07-05)

| File | LOC | Role | Typed-response rate |
|---|---|---|---|
| `frontend/src/lib/api.ts` | 4,194 | 93 domain `*Api` module exports + axios singleton | 63 / 919 = **6.85%** |
| `frontend/src/lib/cockpitApi.ts` | 513 | 54 typed function exports; sole typed-island api-module | 52 / 54 = **96%** |
| `frontend/src/lib/apiClient.ts` | 29 | `scopedGet` + `scopedPost` X-UI-Scope helpers | n/a (thin wrapper) |
| `frontend/src/lib/cn.ts` | (excluded — Tailwind utility) | — | — |
| `frontend/src/lib/pdfExport.ts` | (excluded — PDF export utility) | — | — |
| `frontend/src/lib/time.ts` | (excluded — time formatting) | — | — |

### 5.2 93 api-module inventory in `api.ts` (per A1 A2 registry)

Full enumeration by domain cluster (line ranges from A1):

**Auth & User (2 modules):** `authApi` (73-79, 4 methods), `assistantApi` (1147-1227, 22 methods, PARTIAL typed 5/20).

**Agents & Execution (8 modules):** `agentsApi` (81-92, 7), `agentChannelsApi` (95-120, 12), `agentMonitoringApi` (123-137, 6), `agentToolsApi` (140-155, 9), `agentTemplatesApi` (158-184, 8), `agentOrchestrationsApi` (188-205, 9 — DEAD-CANDIDATE per F5), `relationshipsApi` (2185-2212, 10 — DEAD-CANDIDATE), `adminApi` (1667-1692, 13).

**Agent Cognition & Memory (11 modules):** `dreamsApi` (217-242, 11), `conversationsApi` (248-274, 8), `conversationContractApi` (277-282, 2), `hiveMindApi` (285-302, 5), `memoryPalaceApi` (305-354, 19 — consumed by AIConsciousnessTab), `memoryClustersApi` (357-391, 10 — DEAD-CANDIDATE), `evolutionApi` (394-427, 16 — consumed by AIConsciousnessTab), `moodApi` (430-461, 12 — consumed by AIConsciousnessTab), `timeTravelApi` (464-509, 19 — consumed by AIConsciousnessTab), `timeCapsuleApi` (512-534, 8 — consumed by AIConsciousnessTab), `mythologyApi` (2315-2362, 17).

**Learning & Evolution (7 modules):** `learningApi` (754-765, 8), `userLearningApi` (793-837, 16), `journeyApi` (2546-2574, 16 — DEAD-CANDIDATE), `experimentsApi` (739-752, 8), `experimentRecommendationsApi` (2457-2459, 1), `pilotsApi` (721-737, 9), `legacyLearningApi` (1494-1515, 12 — DEAD-CANDIDATE).

**Content & Distribution (10 modules):** `contentApi` (895-1046, 51 — cross-cutter), `distributionApi` (847-893, 28), `blogsApi` (3921-3962, 22), `campaignApi` (4054-4066, 8), `podcastApi` (1548-1573, 9), `voiceMarketplaceApi` (2609-2662, 27), `ttsApi` (2665-2708, 8), `portfolioApi` (1575-1603, 16), `previewApi` (4113-4158, 24), `deliverablesApi` (4095-4109, 11).

**Workspace & Operations (8 modules):** `workspaceApi` (1695-1734, 18 — cross-cutter), `workspaceOperationsApi` (1737-1745, 5), `workspaceTriggersApi` (1748-1780, 11), `workspaceTriggerConfigsApi` (1783-1808, 12 — DEAD-CANDIDATE), `activityApi` (207-210, 2), `decisionsApi` (550-561, 8), `bpaasApi` (4187-4194, 4), `humanApi` (1607-1665, 20 — primary cross-cutter).

**Business Intelligence (7 modules):** `intelligenceApi` (583-587, 3), `incomeBuilderApi` (590-612, 10), `opportunitiesApi` (615-624, 5), `spidersApi` (641-644, 2), `spiderIntegrationApi` (647-690, 18), `spiderFeedApi` (693-719, 5), `ecosystemApi` (626-629, 2 — DEAD-CANDIDATE).

**Collaboration & Advisors (4 modules):** `collectiveApi` (2365-2415, 26), `neuralOrchestraApi` (2290-2311, 7), `advisorsApi` (2166-2182, 5), `hiveMindApi` (285-302, 5).

**Body Systems (12 modules):** `bodyApi` (564-581, 10), `heartApi` (1849-1866, 5), `lungsApi` (1869-1891, 7 — DEAD-CANDIDATE), `circulatoryApi` (1894-1922, 8 — DEAD-CANDIDATE), `spineApi` (1925-1957, 9 — DEAD-CANDIDATE), `llmRoutingApi` (1963-1984, 4), `immuneApi` (1987-2039, 13 — DEAD-CANDIDATE), `digestiveApi` (2042-2069, 8 — DEAD-CANDIDATE), `muscularApi` (2072-2100, 8 — DEAD-CANDIDATE), `brainApi` (2103-2119, 5 — DEAD-CANDIDATE), `skinApi` (2122-2141, 6 — DEAD-CANDIDATE), `nervousApi` (2144-2163, 6 — DEAD-CANDIDATE).

**Reasoning & Autonomous (3 modules):** `reasoningApi` (2418-2454, 16), `autonomousApi` (2462-2489, 15 — DEAD-CANDIDATE), `llmApi` (1811-1846, 7 — DEAD-CANDIDATE).

**Sports & Markets (3 modules):** `bettingApi` (1229-1276, 25), `sportsHubApi` (1279-1282, 1), `stockApi` (1475-1491, 9).

**Legal & Compliance (3 modules):** `legalApi` (1517-1546, 17), `governmentApi` (1464-1473, 8 PARTIAL 2/9 typed), `auditApi` (4069-4078, 4).

**Analytics & Monitoring (3 modules):** `analyticsApi` (2492-2543, 24), `integrationHealthApi` (2711-2723, 4 — DEAD-CANDIDATE), `dashboardApi` (631-639, 6).

**Settings & Preferences (2 modules):** `settingsApi` (1048-1082, 17), `classificationApi` (538-548, 6 — DEAD-CANDIDATE).

**Platform & Infrastructure (5 modules):** `platformApi` (3257-3879, 414 PARTIAL 30/30 typed — the largest module by method count), `orchestrationApi` (2948-3034, 26), `homeApi` (67-71, 3 — consumed by CommandCenterPage), `executorApi` (4081-4092, 8), `reviewApi` (4161-4174, 4), `revenueApi` (4182-4185, 2), `statusApi` (4178-4180, 1), `researchApi` (840-844, 3 — DEAD-CANDIDATE), `docsIndexApi` (3101-3124, 12), `billingApi` (2577-2606, 15).

**RAG & Docs (2 modules):** `ragApi` (2215-2287, 17), `docsIndexApi` (3101-3124, 12).

### 5.3 Grand totals

| Metric | Value | Source |
|---|---|---|
| `*Api` module count in api.ts | **93** | grep `^export const \w+Api\b` |
| Total api calls in api.ts | **919** (856 bare + 63 typed) | grep `api\.(get\|post\|patch\|delete\|put)(` = 856; `api\.\w+<` = 63 |
| Exported interfaces/types in api.ts | **47** (most orphan) | grep `^export (interface\|type)\s+\w+` |
| Typed calls in cockpitApi.ts | **52 of 54 = 96%** | verifier count |
| Types exported from `frontend/src/types/cockpit.ts` | **104** (hand-written) | file inventory |
| Typed-response coverage rate (api.ts) | **6.85%** (63/919) | derived |
| Typed-module rate (canonical Response types) | **~3.2%** (3/94: cockpit + platform + partial-assistant) | derived |
| Session-annotation date-range in api.ts | Session 688 → Session 1095 = **407-session churn** | grep `// Session \d+` |

### 5.4 Non-api-module call sites (component-level bypass)

Per A1 + A4 grep sweep — **45 files with direct `api.get(...)` /
`api.post(...)` / bare `axios.get(...)` / `fetch(...)` calls outside
`frontend/src/lib/*.ts`**. Top-20 sites (file:line):

1. `frontend/src/components/DemoPipelineCard.tsx:42, 69`
2. `frontend/src/components/layout/Sidebar.tsx:151`
3. `frontend/src/components/platform/ActionsPanel.tsx:33`
4. `frontend/src/components/platform/DocumentViewer.tsx:88` (raw `axios.get`)
5. `frontend/src/components/platform/TriggerRulesPanel.tsx:60, 65`
6. `frontend/src/components/cockpit/library/DeliverablesTable.tsx:52`
7. `frontend/src/pages/ProjectsPage.tsx:39`
8. `frontend/src/pages/InboxPage.tsx:57, 70, 74, 105, 124`
9. `frontend/src/pages/workspace/tabs/ConceptForgeTab.tsx:346, 636, 645`
10. `frontend/src/pages/workspace/tabs/Stage3EvaluationTab.tsx:83`
11. `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx:518, 2944`
12. `frontend/src/pages/workspace/tabs/InitiativesTab.tsx` (5 raw calls per A4)
13. `frontend/src/pages/workspace/tabs/IntelligenceTab.tsx` (7 raw calls per A4)
14. `frontend/src/pages/workspace/tabs/DataIntelTab.tsx` (2 raw calls per A4)
15. `frontend/src/stores/paStore.ts` (3 raw calls per A4)
16. `frontend/src/components/GlobalPADock.tsx` (1 raw call per A4)

**Class:** LEAK from the api-module abstraction — `~9 of ~45 sites are
inline bypass with new endpoint URLs not registered in api.ts` (per
A4). `cockpitApi.ts` legitimately wraps `/cockpit/*` routes; other
inline calls scatter contract discipline. **Severity: MED
`boundary_violation`** — not systemic, but pattern risk if unchecked.

## 6. Major APIs and Interfaces

**Q8-Q9 — What are the surface APIs?**

The Child C slice is itself an "API contract for API calls." Key
patterns:

### 6.1 Axios interceptor patterns

- **Request interceptor:** `api.ts:27-40` — adds `Authorization:
  Token <token>` header from `useAuthStore.getState().token`;
  DEV/`/platform/` debug console log.
- **Response interceptor:** `api.ts:43-62` — 401 handling with
  `isAuthEndpoint` whitelist substring `/auth/` + `/login`.
- **withCredentials: true** globally — allows Django session cookie
  fallback if token missing.
- **Timeout: 90000ms** (90s) — added Session 802 to prevent browser
  default 2min silent timeout.
- **Session 968: X-UI-Scope header injection** via `apiClient.ts`
  helpers only — most call sites do NOT use scoped helpers.

### 6.2 Typed-response pattern (cockpit surface)

`cockpitApi.ts` demonstrates the achievable discipline:

```
// frontend/src/lib/cockpitApi.ts:59-62
export async function getRuns(params?: RunsParams) {
  const { data } = await api.get<RunSummary[]>('/cockpit/runs/', { params })
  return data
}
```

**Pattern requirements met:**
- Typed response via generic `api.get<RunSummary[]>`
- Return type inferred from the generic (no `any` leak)
- Named param interface `RunsParams` (line 48)
- Backend response shape mirrored in `frontend/src/types/cockpit.ts:1-100`

This pattern is **NOT reproduced across 91 of 93 api-modules** in
`api.ts`. `platformApi` uses inline generic object types (`api.get<{
success: boolean; items: T[] }>()`) but does NOT import from a shared
type module.

### 6.3 Bare-call pattern (91 of 94 modules)

`agentsApi` demonstrates the modal pattern:

```
// frontend/src/lib/api.ts:81-92
export const agentsApi = {
  list: () => api.get('/v1/agents/list/'),
  comprehensive: () => api.get('/v1/agents/comprehensive/'),
  execute: (agentName: string, task: string) =>
    api.post('/v1/agents/execute/', { agent_name: agentName, task }),
  executionDetail: (executionId: string) =>
    api.get(`/v1/agents/execution/${executionId}/`),
  ...
}
```

**Pattern anti-features:**
- Zero type annotation on return
- Zero param-type validation
- Zero response-shape assertion
- Caller must know backend response shape from view code

## 7. Runtime Flows

**Q10-Q11 — How does data flow?**

Standard REST call flow (all 93 non-cockpit api-modules):

```
[React component]
    → import { xyzApi } from '@/lib/api'
    → const { data } = useQuery({ queryFn: () => xyzApi.method(args) })
    → xyzApi.method(args) returns axios.get('/path', {...})
    → api interceptor injects Authorization: Token
    → HTTP → Django view (permission_classes=[AllowAny|IsAuthenticated])
    → response
    → response interceptor: if 401 and !/auth|/login → console.warn + reject
    → useQuery propagates error (or empty data on rejection)
    → component renders blank / undefined field access
```

Typed cockpit flow:

```
[React component]
    → import { getRuns } from '@/lib/cockpitApi'
    → const { data } = useQuery({ queryFn: () => getRuns(params) })
    → getRuns() calls api.get<RunSummary[]>('/cockpit/runs/', {...})
    → axios returns AxiosResponse<RunSummary[]>
    → return data (typed as RunSummary[])
    → TypeScript inference propagates through useQuery
    → component renders typed shape
```

**Silent-401 failure path:**

```
[Any authenticated call]
    → interceptor detects 401
    → url not /auth or /login
    → console.warn('Authentication required for:', url)
    → Promise.reject propagates
    → useQuery.error state populated but no UI surfaces error
    → component tab renders blank (S1505 §14.3 "silent 401" pattern)
```

## 8. Data Ownership and Lifecycle

**Q12-Q13 — Who owns the data + what is its lifecycle?**

Frontend REST API contract layer **owns no persistent state**. It is
a stateless request/response translator. Adjacencies:

| State surface | Owner | Lifetime | Adjacent to Child C? |
|---|---|---|---|
| Auth token | `useAuthStore` (Zustand w/ persist middleware) | localStorage until logout | YES — read by api.ts:29 |
| Session cookie | Browser (Django session) | Server-issued 2-week default | YES — sent by `withCredentials: true` |
| Response caching | react-query cache | in-memory only, cleared on reload | Adjacent (Child D scope for persistence) |
| Request-log metadata | `getRequestLog` / `subscribeRequestLog` in api.ts | in-memory ring buffer | Owned here (Session 968) |
| Retry / backoff policy | react-query defaults + per-query overrides | Per-hook | Adjacent (not centralized in api.ts) |

**Session 968 request-log metadata** is the one persistent-ish surface
Child C owns. `frontend/src/lib/api.ts` (per A1 verifier) declares
`InternalAxiosRequestConfig` metadata extension (line 4-8) carrying
`requestId` + `startTime` for downstream request-log filtering.

## 9. Integrations With Other Domains

**Q14+Q17+Q18+Q21+Q22 — Integrations, cross-domain deps, ownership.**

| Adjacent domain | Direction | Strength | Evidence | Notes |
|---|---|---|---|---|
| Group 2400 Auth | Downstream | **STRONG-WITH-DEBT** | `api.ts:27-40` reads `useAuthStore`; `api.ts:48-56` silent-401 handler on backend permission_classes drift | Symptomatic + descriptive only per §7.1; Group 2400 owns model. |
| Group 2500 API | Upstream (consumer) | **WEAK** | 93 `*Api` modules consume `core/urls*.py` endpoints; zero contract SoT crosses the boundary | Cross-arc flag: single message-contract SoT candidate for envelope schema (§17 T7). |
| Group 2600 PA | Peer | **STRONG-WITH-DUPLICATE** | `assistantApi` (`/api/pa/chat/*`) + `conversationsApi` share PA surface with S2202 `/pa/conversations/{id}` WS route | S2202 §17 T6 joint 2500+2600 flag extended (see §17 T7). |
| Group 1700 Observability | Peer | **STRONG-WITH-GAP** | cockpitApi is a typed island; `platformApi` has 30 typed methods for observability | Envelope enforcement decision (S2202 §20.6) applies here too for typed-envelope. |
| Group 1500 Sports | Peer | **STRONG-WITH-SoT-DEBT** | `bettingApi` + `sportsHubApi` + `stockApi` inherit silent-401 + zero typed contracts; S1505 §14.3 auth-drift + §15.5 SoT-debt originate here | Cat E findings generalize; xx99 elevates. |
| Group 1300 Memory | Peer (consumer) | **PARTIAL** | `memoryPalaceApi` + `memoryClustersApi` + `evolutionApi` + `moodApi` consumed by AIConsciousnessTab; 3 modules typed 0/anytime | Cross-arc coordination flag (semantic-shape is Group 1300; render-shape is Group 2200). |
| Group 1600 Content | Peer (consumer) | **STRONG-WITH-SoT-DEBT** | `contentApi` (51 methods, cross-cutter) + `blogsApi` + `campaignApi` + `deliverablesApi` inherit untyped pattern | Cross-arc coordination flag per parent §7.1 render/publish split. |
| Group 1800 HumanAttention | Peer (consumer) | **STRONG-CROSS-CUTTER** | `humanApi` (20 methods, 4-5 consuming surfaces) is primary cross-cutter | S1505 §16.2 + S2004 §14.6 Cat F CONSOLIDATION flags preserved. |
| Sports app (drf-spectacular partial) | Cross-app-boundary | **PARTIAL-WIRED** | `sports/views.py` has 16 `@extend_schema` decorators (verifier finding, §14 F5); `core/*.py` has 0 | Partial wiring is the LEVER for a whole-platform SoT rollout. |

## 10. Event Flows

**Q19-Q20 — Event flow map.**

The Child C slice is REST-focused; WebSocket event flows are S2202
Child B territory. Cross-arc parallel signals recorded here:

- **REST payload dispatch (Child C surface).** Component receives
  response `data` object; unwraps via bare access (e.g., `data.items[]`
  or `data.data.execution` per cockpitApi.ts:65). No envelope; no
  discriminator; no version negotiation.
- **WS payload dispatch (Child B surface — S2202 finding).**
  Component receives `JSON.parse(event.data)`; switches on
  `event.type` string; no envelope; no `ui.render_hint`.
- **Cross-arc pattern:** BOTH transports (REST + WS) lack a **message
  contract source-of-truth**. S2202 §20.6 Path C ("envelope
  mandatory for integrity/governance/money/state-changing flows;
  optional for purely visual signals") is the cross-arc principle
  that ALSO applies at the REST layer. Money-path REST calls
  (`bettingApi.placeBet`, `wagerApi.settle`, `billingApi.stripe.*`,
  `humanApi.decide`) inherit the same envelope-less lack as the WS
  side.

**Recorded as §17 T7 cross-arc flag.**

## 11. Existing Documentation

**Q23 — What documentation covers this?**

| Doc | Coverage | Assessment |
|---|---|---|
| `docs/PLATFORM_INVENTORY.md` | **No api-module count row.** Frontend row lists 61 routes + 5 workspace tabs + 9 betting tabs; no line for API-module inventory, typed-coverage, or contract-SoT status. | **GAP.** Recommend xx99 augmentation with API-contract section (see §7 anchor updates). |
| `docs/topics/frontend.md` | **Zero mentions** of "API contract", "typed responses", "OpenAPI", "schema", or "SoT" (grep result 0 matches for those terms). Endpoints referenced ad-hoc (`/api/home/trigger-desks`, `/pa/chat/`). | **UNMET.** No narrative coverage of api-module discipline. Extends S2201/S2202 subsystem-doc-stale-warned baseline. |
| `docs/PLATFORM_WHAT_IT_IS.md` | Narrative anchor lists 61 routes + 9 body systems + 6 LLM providers; no api-module section | **GAP.** Contract-surface layer is invisible in narrative anchor. |
| `docs/ARCHITECTURE.md` | No dedicated API-layer section (verified per A6). | **GAP.** |
| `docs/AGENTS.md` | Agent-side documentation; does not cover API layer | Out-of-scope. |
| `docs/API_PATH_POLICY.md` | Path convention rules exist; contract discipline not covered | **PARTIAL** — path conventions ≠ contract discipline. |
| `frontend/README.md` (if present) | Not verified in this session — flagged for xx99 sweep | UNKNOWN. |
| Session-annotation micro-comments in `api.ts` | 95 unique `// Session N` tags spanning 407 sessions | High-frequency change signal; low-coverage documentation. |

**Research Coverage classification per §12:**
- Pre-arc: **NONE** for whole-frontend contract discipline (no
  dedicated doc, no research entry).
- Post-S1505: **LIGHT** for `/betting`-slice via S1505 §15.5.
- Post-S2201: **MODERATE** for whole-frontend baseline (93 modules
  enumerated but not typed-scored).
- Post-S2203 (this doc): **DEEP** for typed-contract + auth-drift +
  cross-boundary discipline whole-frontend.

## 12. Research Coverage

**Q24 — What research already exists?**

| Prior arc / doc | Slice covered | Delegates to Child C |
|---|---|---|
| S1505 §14.3 F3 | Sports `/betting`-slice AUTH-DRIFT | YES — whole-frontend silent-401 pattern rate |
| S1505 §15.5 F4 | Sports `/betting`-slice "no API contract SoT" | YES — whole-frontend contract SoT test |
| S1505 §16.2 | `humanApi` cross-boundary observation | YES — cross-cutter map |
| S2004 §14.6 | Cat F CONSOLIDATION `humanApi` | YES — cross-cutter map |
| S2201 §5 + §14.6 + §15.5 | Whole-frontend inventory of 93 api-modules + silent-401 systemic + typed-contract absence | YES — this Child measures + verifies |
| S2202 §17 T6 | WS/polling consolidation joint 2500+2600 | YES — REST-side parallel (§17 T7) |
| S2202 §20.6 Path C | Envelope mandatory for integrity flows optional for visual | YES — REST parallel principle (§10 + §17) |

**Research coverage = DEEP post-S2203 for the axes this Child covers.**

## 13. Architecture Maturity

**Q25 — Maturity verdict per playbook §12 rubric.**

| Sub-axis | Rating | Justification |
|---|---|---|
| **api-module organization** | STABLE-organizational-only | 93 modules follow uniform `export const *Api = { ... }` pattern; grep-discoverable; no chaos. BUT: 4,194-line monolith, 91.5% of modules 0% typed, 15-20 DEAD-CANDIDATEs, no per-module owner. Organizational stability, not architectural stability. |
| **Typed-contract discipline** | PARTIAL (islanded) | cockpitApi.ts fully typed (96%); platformApi partially typed (~100% inline generics — but not exported Response types); assistantApi partial (25%); governmentApi partial (2/9). All 90+ other modules 0% typed. Coverage rate 6.85% overall. |
| **Silent-401 discipline** | UNMET | Single global handler; whitelist substring hardcoded; ~100% swallow for non-whitelist; ~630 call-sites at risk per A3. |
| **Cross-boundary discipline** | STABLE-with-authStore-caveat | 93/94 modules confined to `frontend/src/lib/`; do not import from pages/components/hooks. Exception: `api.ts` imports `@/stores/authStore` (necessary for interceptor); this is a documented design choice, not a leak. Component-side raw axios/fetch bypass is ~9 sites (below threshold). |
| **Session-annotation hygiene** | WORKING-churn-heavy | 407-session span (688→1095) = active drift risk. No CODEOWNERS. Micro-comments helpful but scattered. |
| **Contract SoT infrastructure** | INSTALLED-PARTIAL-WIRED | drf-spectacular==0.28.0 declared + `SPECTACULAR_SETTINGS` in `core/settings.py`; wired ONLY in `sports/views.py` (16 decorators); zero decorators in `core/*.py`. Frontend has NO codegen. NO runtime validation. |

**Overall Child C slice verdict: PARTIAL (with STABILITY THREAT).**

Comparison vs S1273 32-domain row 18 "STABLE + DEEP":
- **STABLE-at-render** (module registry works) but **PARTIAL-at-contract** (typed discipline UNMET).
- Extends S2201 §20.6 downgrade candidate (WORKING + MEDIUM) with
  Child C evidence: contract SoT is a PLATFORM-scale gap, not a
  page-scale gap.
- Final POSTURE-DECISION resolution deferred to S2299 xx99 canonical
  summary after S2204 close.

## 14. Known Drift

**Q26 — What drift exists between docs and runtime?**

### 14.1 F1 — Parent scoping §5 Child C load-bearing input path-reference drift (observation, not drift)

**Claim.** Parent scoping §5 Child C block referenced
`frontend/src/api/*` as the api-module directory. Runtime path is
`frontend/src/lib/` (no `frontend/src/api/` directory exists).

**Verifier:** Direct `ls frontend/src/api/` returns "No such file or
directory."

**Class:** `observation` — path-reference drift in parent scoping,
NOT runtime drift. Parent scoping §5 was drafted from S1505 narrative
memory; actual path is well-established.

**Severity:** LOW. Recorded here for xx99 cross-reference; no fix
needed.

### 14.2 F2 — PLATFORM_INVENTORY §Frontend has no API-module row

**Claim.** `docs/PLATFORM_INVENTORY.md` frontend row lists 61 routes +
5 workspace tabs + 9 betting tabs. **No line for API-module count,
typed-coverage, or contract-SoT status.**

**Verifier:** Direct read of PLATFORM_INVENTORY.md — confirmed.

**Class:** `observation` — inventory sectioning is a scope choice,
not a drift finding (per S2202 F8 precedent).

**Severity:** LOW. Optional enhancement candidate (xx99 anchor-update
batch): add API-contract row with counts (93 modules + 919 calls +
6.85% typed + drf-spectacular partial wiring).

### 14.3 F3 — SYSTEMIC silent-401 pattern (whole-frontend, extending S1505 §14.3 F3 + S2201 §14.6)

**Claim.** `frontend/src/lib/api.ts:48-56` is the sole 401 handler in
the whole `frontend/src/`. Whitelist substring `url.includes('/auth/')
|| url.includes('/login')` triggers logout + redirect. All other 401s
`console.warn(...)` + reject to caller.

**Verified-in-repo anchors:**
- `frontend/src/lib/api.ts:48-56` (silent-401 interceptor UNCHANGED
  from S1505 baseline).
- Grep `error\.response\?\.status === 401` in `frontend/src/**` = 1
  match (only api.ts:48).
- Grep `Authorization` in `frontend/src/**` outside `api.ts` = 0
  matches (no component overrides).
- Backend permission-floor sample (per A3 20-endpoint matrix): ~40%
  IsAuthenticated + ~20% AllowAny + ~40% not-traced.
- Per-surface silent-401 exposure per A3: Workspace ~95%, PA 100%,
  Command-Center 60%, Betting 30% (writes only), Other ~70%.
- Total call-sites at silent-401 risk: **~630 of ~1,300 (~48%
  estimate; grep-based method — may overcount wrappers/duplicates)**
  across api-modules known to be gated. **Method + hedge (Rigby SIGN
  cycle 1 Q14 STRENGTHEN 2026-07-05 fold):** number is mechanically
  derived from A3 per-surface exposure rates × api-module method
  counts; treats every gated call-site as independent; wrapper hooks
  + higher-order helpers may inflate raw count. Preserves the
  descriptive/symptomatic posture per §7.1 Group 2400 guardrail; no
  auth-implementation claim.

**Two-sided framing preserved from S1505 §14.3 F3:**
- **Frontend side:** no 401 surfacing / no per-call auth gate —
  silent failure.
- **Backend side:** permission-floor inconsistency across Django
  apps; no uniform policy.

**Severity:** **HIGH baseline; CRITICAL for user-visible surfaces**
(BettingPage top-plays / sharp-action / arbitrage; WorkspacePage /
CommandCenterPage attention queues; PA chat) where silent-401
manifests as blank tabs with no error indicator. Per S2201 F1/F3
severity-scale precedent: severity scales with user-visibility +
money-path exposure, not silent-401 presence alone.

**Class:** `drift` (frontend-symptom) + `technical_debt` (auth-model
Group 2400 dependency).

**Cross-arc coordination flag (§7.1 Child C → Group 2400 guardrail):**
Silent-401 is descriptive/symptomatic ONLY at Child C scope; auth
model design belongs to Group 2400. This finding hands off backend
permission-floor uniformity + token-refresh mechanism decisions to
Group 2400 with the whole-frontend blast-radius evidence attached.

### 14.4 F3.5 — Auth-endpoint whitelist substring is BRITTLE (technical_debt)

**Claim.** `api.ts:50` uses substring check `url.includes('/auth/') ||
url.includes('/login')`. A3 verifier finding: all 10 modern
`/api/v1/auth/*` endpoints match; legacy `/accounts/logout/` DOES NOT
match (only substring `/logout`, no `/login`). Not a live risk today
because `authApi.logout()` uses `/v1/auth/logout/`, but pattern is
brittle to future auth-endpoint additions (e.g., a hypothetical
`/api/v1/2fa/verify/`, OAuth callbacks, password-reset flows) where
substring-match failure could cause accidental auth bypass/lockout.

**Class:** `technical_debt` (maintenance debt). Severity: **MEDIUM
(Rigby SIGN cycle 1 Q5 STRENGTHEN 2026-07-05 fold — LOW → MED because
substring whitelists in auth are classic footguns that scale badly
under route evolution)**. Downgrade to LOW only if intentional
minimality + covered by tests can be proven; neither is present at HEAD.

### 14.5 F4 — Zero typed-response coverage across 91 of 94 api-modules (SYSTEMIC, extends S1505 §15.5)

**Claim.** 63 of 919 api.ts calls (6.85%) carry generic type
parameters. Broken down per module: cockpitApi.ts = 52/54 = 96%;
platformApi = 30/30 inline generics (not exported Response types);
assistantApi = 5/20 (25%); governmentApi = 2/9 (22%); all other 90
modules = 0%.

**Verified-in-repo anchors:**
- `frontend/src/lib/api.ts` grep `api\.\w+<` = 63 matches.
- `frontend/src/lib/api.ts` grep `api\.\w+\(` = 856 matches.
- `frontend/src/lib/cockpitApi.ts` grep `api\.\w+<` = 52 matches.
- `frontend/src/types/cockpit.ts` = 821 LOC / 104 exported types.
- `frontend/src/types/` directory contains ONLY `cockpit.ts` (no
  other type files).

**S1505 §15.5 4-way parent cause claim re-test (per A2 + A5):**
Sampled 3 non-sports modules (agentsApi, contentApi, humanApi):
- (i) AUTH-DRIFT: replicates on all 3 modules
- (ii) Inline TS interfaces at call sites: replicates on all 3 (per
  S2201 §5 evidence)
- (iii) Doc drift on counts: replicates (no api-module count
  documented; 407-session churn)
- (iv) Read-path fragility: replicates (bare `.data` access with no
  runtime validation)

**Replication rate: 3/3 sampled non-sports modules → all 4
pathologies. Extended to 8 modules via A5 → 7 of 8 replicate all 4
pathologies at ~100% rate.**

**Class:** `technical_debt` (structural). Severity: **HIGH baseline;
CRITICAL for money-path + governance-path endpoints** (per §14 F1
severity-scale rationale).

### 14.6 F5 — drf-spectacular installed but wired ONLY in `sports/views.py` (KEY VERIFIER FINDING)

**Claim.** `requirements.txt` declares `drf-spectacular==0.28.0`.
`core/settings.py` declares `SPECTACULAR_SETTINGS = {...}`. But:
- `sports/views.py` = **16 `@extend_schema` decorators** (lines 58,
  117, 164, 344, 357, 385, 500, 568, 744, 848, 887, 907, 924, 953,
  987, 1023).
- `core/*.py` = **0 `@extend_schema` decorators** across all
  `views_*.py` files.
- `intelligence/*.py` = 0 decorators.
- `ai_core/*.py` = 0 decorators.
- `discord/*.py` = 0 decorators.

**Frontend side:**
- `frontend/package.json` grep for `openapi-typescript` / `orval` /
  `kubb` / `swagger-codegen` = **0 matches**.
- Grep for `zod` / `io-ts` / `valibot` / `superstruct` / `yup` = **0
  matches**.

**Class:** `technical_debt` (structural — infrastructure installed
but partial-wired). Severity: **HIGH** — this is a PARTIAL FOUNDATION
already laid; xx99 recommends a Group 2500 API arc scope inclusion for
whole-platform drf-spectacular rollout + frontend codegen wiring.

**Interpretation guard rail:** drf-spectacular's presence in `sports/`
alone is NOT a claim that `sports/` is more mature; it is evidence
that the infrastructure primitive exists + has one working
demonstration + is not blocked by fundamental incompatibility. The
scope of the sports wiring is un-audited at Child C level; recorded
as a discovery artifact for xx99 handoff to Group 2500 API.

### 14.7 F6 — DEAD-CANDIDATE api-modules (INTENT-NEUTRAL)

**Claim.** ~15-20 api-modules in api.ts show zero `\w+Api\.` invocation
sites in `frontend/src/` beyond their own export declaration.
Verifier-confirmed DEAD-CANDIDATE list (per §14 F6 grep sweep):
- `nervousApi` (2144-2163)
- `skinApi` (2122-2141)
- `spineApi` (1925-1957)
- `muscularApi` (2072-2100)
- `circulatoryApi` (1894-1922)
- `digestiveApi` (2042-2069)
- `brainApi` (2103-2119)
- `immuneApi` (1987-2039)
- `agentOrchestrationsApi` (188-205)
- `autonomousApi` (2462-2489)
- `classificationApi` (538-548)
- `ecosystemApi` (626-629)
- `legacyLearningApi` (1494-1515)
- `journeyApi` (2546-2574)
- `researchApi` (840-844)
- `workspaceTriggerConfigsApi` (1783-1808)
- `integrationHealthApi` (2711-2723)
- `llmApi` (1811-1846)

**Verifier correction:** A4 initially flagged 27 modules; verifier
grep on `\.overview()`, `\.list()`, `\.get()` invocations caught 7
modules ACTUALLY CONSUMED (memoryPalaceApi, moodApi, timeTravelApi,
evolutionApi, relationshipsApi, timeCapsuleApi, homeApi — all
consumed by AIConsciousnessTab.tsx + CommandCenterPage.tsx). A4
DEAD-CANDIDATE list REFINED to ~18 modules.

**Interpretation rule per S2202 F6 precedent + Rigby SIGN cycle 1
Q15 STRENGTHEN 2026-07-05 fold — delete-proof gate tightened:**
DEAD-CANDIDATE is NOT a removal-ready designation. Delete-proof
requires triad with **intent-statement MANDATORY**:
- **(a) no imports/usages** across `frontend/src/**/*.{ts,tsx}` (grep
  primary evidence);
- **(b) no runtime route hits in recent telemetry** IF telemetry
  available (supporting evidence, not sole proof; noisy or missing
  telemetry does NOT count as absence);
- **(c) MANDATORY explicit maintainer-intent statement** (e.g.,
  "staged for future consumer" / "keep as reference" / "confirmed
  removable at $DATE by $NAME").

INTENT-NEUTRAL disposition applies at Child C scope; only maintainer
signoff (R3 post-arc batch) can flip to REMOVAL-READY.

**Class:** `dead_code`-DEAD-CANDIDATE. Severity: **LOW-MEDIUM**
(hygiene + documentation debt; no runtime risk).

**Recommendation:** Post-arc maintainer-decision batch (mirror S2202
§19 R2/R3 pattern) — bundle 18 DEAD-CANDIDATE modules for
maintainer-signoff before delete-proof + cleanup PR.

## 15. Known Technical Debt

**Q27 — What technical debt exists?**

### 15.1 CRITICAL — Zero canonical API contract source-of-truth (SYSTEMIC, per §14 F4)

**Debt.** No exported Response types per api-module; no OpenAPI
generator wired at platform scale; no runtime response validator.
S1505 §15.5 elevation to HIGH is CONFIRMED SYSTEMIC.

**Anti-scope disclaimer (Rigby SIGN cycle 1 Q16 STRENGTHEN 2026-07-05
fold):** No code changes proposed in this doc; enforcement locus
owned by Group 2500 / maintainers per §7.1 Child C → Group 2500
guardrail. Verbs stay recommend / propose / evaluate / consider /
prioritize / defer / require-maintainer-decision. Options below are
labeled **Options (non-authoring)** — this section MEASURES the
debt and INVENTORIES option-space; it does NOT commit to any
authoring path.

**Options (non-authoring — research finding only per §7 anti-scope; no
authoring commitment):**
- **(a) OpenAPI 3.0 generator via drf-spectacular platform-wide.**
  Extend `sports/views.py` 16-decorator wiring to `core/views_*.py`;
  emit spec at build-time; consume via `openapi-typescript` or
  `orval` in `frontend/`. Blast radius: ~500 views + ~93 api-modules
  + build pipeline. Rollback: LOW (spec-only, additive).
- **(b) Zod runtime schemas exported from DRF serializers.** Wire a
  schema serializer → zod converter; import in `frontend/src/schemas/`
  + validate at api.ts call boundary. Blast radius: ~93 modules +
  ~919 call sites. Rollback: MEDIUM.
- **(c) tRPC-style typed client.** Rewrite api.ts as tRPC procedures
  + wire Django endpoints as tRPC routers. Blast radius: FULL
  rewrite. Not viable given size + scope.
- **(d) Handwritten shared `frontend/src/types/*` modules.** Extend
  cockpitApi.ts pattern to 93 modules; hand-write ~200-500 type
  interfaces. Blast radius: BOUNDED but LARGE (~800-1500 hand-written
  types). Rollback: LOW (types-only). Precedent: cockpitApi = 96%
  typed via 104 hand-written types.
- **(e) Status quo.** No SoT; scale S1505 §15.5 debt indefinitely.

**Cat F design-preparation candidate:** This is the highest-leverage
structural debt call in the Child C audit. Cross-arc coordination
flag to Group 2500 API (canonical BE API design owner) — SoT decision
belongs there per §7.1 guardrail.

### 15.2 HIGH — Silent-401 pattern (per §14 F3, extends S1505 §14.3)

**Debt.** Global swallow-by-default; whole-frontend exposure ~630
call-sites at risk. Cross-arc flag to Group 2400 Auth for
session-model resolution.

### 15.3 MED-HIGH — Mega-module god-file `frontend/src/lib/api.ts`
(4,194 LOC, 93 exports, 407-session churn)

**Debt.** Comparable to S2201 §14.6 6-god-component pattern at
infrastructure layer. `platformApi` alone (line 3257-3879) = ~29% of
method count. No per-domain file split.

**Remediation option (research-only):**
- Split by domain: `api-betting.ts`, `api-workspace.ts`,
  `api-agents.ts`, `api-content.ts`, `api-body-systems.ts`, etc.
- Consolidate DEAD-CANDIDATE body-system modules (nervousApi,
  circulatoryApi, spineApi, etc.) into a single `bodySystemsApi`.
- Post-arc T-slot.

### 15.4 MED — Zero API-module tests

**Debt.** No `frontend/src/lib/api*.test.ts` files exist. Grep-verified.
Extends S2201 §15.1 CRITICAL debt to infrastructure layer.

**Remediation option:** MSW (Mock Service Worker) integration tests
against 5-10 highest-traffic endpoints (bettingApi.stats,
workspaceApi.list, humanApi.attention, agentsApi.list,
contentApi.list). Post-arc T-slot.

### 15.5 MED — Component-level fetch/axios bypass (per §5.4)

**Debt.** ~9 sites bypass api-module abstraction with inline
`api.get(...)` / raw `axios.get(...)` / bare `fetch(...)`.
InitiativesTab (5 raw), IntelligenceTab (7 raw), DataIntelTab (2
raw), paStore (3 raw), DocumentViewer (1 raw axios).

**Remediation option:** Wrap each bypass site's endpoints in an
api-module (or extend an existing one). Post-arc T-slot.

### 15.6 MED — Inline `interface \w+Response` duplication at call sites

**Debt.** S1505 §15.4 pattern. Per A2 sample: ~12+ inline `interface
*Response` definitions found across pages/ and components/ (e.g.,
AgentsPage.tsx, InitiativesTab.tsx, CommandCenterPage.tsx).

**Remediation option:** Consolidate into shared
`frontend/src/types/{domain}.ts` per domain; import from single SoT.
Bound to §15.1 remediation Option (d) rollout.

### 15.7 LOW — Auth-endpoint whitelist substring brittleness (per §14 F3.5)

**Debt.** Hardcoded substring check `/auth/` + `/login`. Recommend
central registry.

## 16. Boundary Violations

**Q24 — What violates boundary discipline?**

### 16.1 `api.ts` imports `@/stores/authStore` (INTENTIONAL, NOT VIOLATION)

**Evidence.** `frontend/src/lib/api.ts:2` `import { useAuthStore } from
'@/stores/authStore'`. Used in interceptor `api.ts:29` +
`api.ts:54`.

**Assessment.** Necessary for the axios interceptor to read the
current token + call logout on 401. Documented design choice, not a
leak. **Class: `observation` (design pattern).** Severity: LOW.

### 16.2 Component-level raw fetch/axios calls (~9 sites, per §5.4)

**Evidence.** InitiativesTab (5), IntelligenceTab (7), DataIntelTab
(2), paStore (3), DocumentViewer (1 raw axios), OperatorEdgePage (2).
Total ~9 sites bypass the api-module registry.

**Assessment.** **Class: `boundary_violation` (LEAK).** Severity:
**MED.** Not systemic (below the ~10% threshold), but pattern risk
if unchecked.

### 16.3 `cockpitApi.ts` imports from `@/types/cockpit` (INTENTIONAL, GOOD-PATTERN)

**Evidence.** `cockpitApi.ts:2-44` imports 44 types from
`@/types/cockpit`.

**Assessment.** **Class: `observation` (good pattern).** This is the
canonical pattern the other 93 modules should emulate.

### 16.4 Cross-domain api-module consumption (per A4 verify)

**Evidence.** A4 grep sweep found ZERO surprise cross-imports:
- `bettingApi`: only BettingPage.tsx (S1505 §9.3 confirmed).
- `agentsApi`: AgentsPage.tsx + OrchestrationTab.tsx.
- `stockApi`: StockIntelligencePage.tsx only.
- `bodyApi`: AdminPage + InfrastructureTab + HeartWidget + bodyStore
  (all admin/infra domain).

**Assessment.** Domain-scoped consumption respects boundaries.
**Class: `observation` (good pattern).**

### 16.5 Cross-cutter api-modules (per §17.2 F3)

**Evidence.** `humanApi`, `assistantApi`, `workspaceApi`, `contentApi`
consumed across 3-5 major surfaces each.

**Assessment.** **Class: `overcoupling` (design candidate).**
Severity: **MED-HIGH.** These are the surfaces where an api-module
edit could break multiple domains. S1505 §16.2 + S2004 §14.6 pattern
extends here. Extraction candidate for shared-contract module split
in a future arc (post-Group 2500).

## 17. Duplicate or Overlapping Systems

**Q23 — What overlapping systems exist?**

### 17.1 `bettingApi` overlapping URL prefixes (per S1505 §17.2)

**Evidence.** `bettingApi` calls both `/v1/betting/*` (owned) and
`/v1/sports/*` (cross-domain into sports). e.g.,
`bettingApi.liveOdds()` → `/v1/sports/live-odds/`;
`bettingApi.stats()` → `/v1/betting/stats/`.

**Assessment.** Not duplicate systems; it is a case of `bettingApi`
straddling two backend URL namespaces. Backend routing clarity is a
Group 2500 concern. **Class: `observation`.** Severity: LOW.

### 17.2 Primary cross-cutting api-modules (§14 F3 + this section)

Per A4 verified inventory:

| Cross-cutter | Method count | Consuming surfaces | Consuming files |
|---|---|---|---|
| `humanApi` | 20 | betting + workspace + command-center + platform | BettingPage, BoardroomTab, DecisionDetailModal, unifiedStore, others (5+ files) |
| `assistantApi` | 22 | PA + command-center + government + platform | GlobalPADock, AttentionWidget, paStore, GovernmentPage (4 files) |
| `workspaceApi` | 18 | workspace + command-center + PA | workspace/tabs/*, CommandCenterPage, GlobalPADock, DemoHomePage (8+ files) |
| `contentApi` | 51 | workspace + content-studio + PA | ContentPage, VideoStudioPage, ImageStudioPage, ContentStudioTab, GlobalPADock (5+ files) |

**Assessment.** S1505 §16.2 + S2004 §14.6 pattern extends: 4 primary
cross-cutters. **Class: `overcoupling` (design candidate).** Severity:
**MED-HIGH.**

### 17.3 REST↔WS transport parallel (§10 + T7 cross-arc flag)

**Evidence.** S2202 found 0/40 WS `ui.render_hint` envelope adoption;
Child C found 6.85% REST typed-response coverage (or 11.8% globally
across api.ts+cockpitApi per Q2 STRENGTHEN dual-denominator fold).
Both transports lack a canonical message contract SoT.

**Assessment (Rigby SIGN cycle 1 Q12 STRENGTHEN 2026-07-05 fold —
REST-native axis wording):** **Same underlying pattern at different
transports.** The S2202 §20.6 Path C principle transfers to REST but
the axis should be phrased in **REST-native terms** as **"contract
strictness + validation"** — where strictness = OpenAPI schema
adoption / typed clients / runtime validators / error envelopes.
Envelope is the WS-native form of contract strictness; the REST
counterpart is the OpenAPI/typed-schema/runtime-validation stack.
Path C spirit preserved: mandatory rigor for integrity / governance /
money / state-changing endpoints; lighter weight acceptable for
read-only telemetry / display-only surfaces.

**T7 — REST↔WS message contract strictness joint 2500+2600 (Rigby
SIGN cycle 1 Q13 STRENGTHEN 2026-07-05 fold — T7 gets its own
T-slot ID; pattern echoes S2202 T6 but is distinct enough to avoid
conflation with WS-side subscription discipline).** REST typed-
response coverage (Child C: 6.85% api.ts-only / 11.8% global)
parallels WS envelope conformance (Child B: 0%). Both surfaces lack
canonical SoT for integrity-critical / governance / money-path
endpoints. Joint consolidation candidate to Group 2500 API + Group
2600 PA. **T7 assigned as new distinct T-slot** (not folded into
S2202 T6); marked "joint 2500+2600" to preserve the shared
ownership routing. Cross-arc flag preserved for xx99.

### 17.4 `cockpitApi.ts` scope vs api.ts overlap

**Evidence.** `cockpitApi.getRunDetail(id)` at cockpitApi.ts:65 calls
`/v1/agents/execution/${id}/` — which is ALSO called by
`agentsApi.executionDetail(id)` at api.ts:91. Same endpoint, two
callers.

**Assessment.** cockpitApi's typed-response is the canonical version;
agentsApi's untyped version is the legacy caller. `cockpitApi.ts:65-68`
unwraps `data?.data?.execution ?? data` — evidence that backend
response shape has evolved and cockpitApi handles both shapes.
**Class: `duplicate_model` (call-site duplicate; not model duplicate).**
Severity: LOW. Post-arc T-slot: consolidate to cockpit typed version.

## 18. Ownership Gaps

**Q25 — Where is ownership unclear?**

### 18.1 No CODEOWNERS at `.github/CODEOWNERS` or repo-root

**Evidence.** No `.github/CODEOWNERS` file exists at repo root or
`.github/` (matches S2201 §18.1 + S2202 §18.1 baselines UNCHANGED at
HEAD 0ce569f6).

**Assessment.** Ownership of api.ts is UNKNOWN (implicit: Chris).
**Class: `unclear_owner`.** Severity: **HIGH with single-operator
caveat** (S2201 F4 precedent — CRITICAL if a second contributor
joins).

### 18.2 No dedicated api-layer doc

**Evidence.** No `docs/topics/api-layer.md` or `docs/API_CONTRACT.md`
exists. `docs/topics/frontend.md` has no §API Layer section.
`docs/API_PATH_POLICY.md` covers path conventions only, not contract
discipline.

**Assessment.** **Class: `missing_connection` (documentation +
research artifact).** Severity: **MED.** Post-arc T-slot: draft
`docs/topics/api-contract.md` with narrative + typed-coverage +
cross-cutter inventory.

### 18.3 No cockpitApi ownership entry

**Evidence.** `cockpitApi.ts` (513 LOC) has no docs/AGENTS.md entry
or session-annotation-heavy comment tagging maintainer.

**Assessment.** **Class: `unclear_owner`.** Severity: **MED.** Given
cockpitApi is the canonical typed pattern, ownership + maintenance
model should be documented before rolling out to 93 other modules
(§15.1 Option (d)).

### 18.4 Session-annotation date-range indicates unstructured evolution

**Evidence.** 95 unique `// Session N` micro-comments spanning
Session 688 → Session 1095 (407-session churn). No single-author
signature; sessions annotate incremental additions, not architectural
decisions.

**Assessment.** **Class: `drift` (organizational).** Severity: LOW.
Micro-comments are useful for post-hoc archaeology but do not
constitute architecture documentation.

## 19. Recommended Future Research

**Q28 — What should be researched next?**

Ranked by architectural uncertainty × risk × unblocked flows per
playbook §19.

### 19.1 CRITICAL tier (dependency-ordered)

**R1** — **[Group 2500 API arc — open maintainer gate + queue
follow-on arc] Whole-platform contract SoT rollout evidence.** Child
C evidence supports a Group 2500 T-slot with scope: consider extending
`sports/views.py` 16-decorator drf-spectacular wiring pattern to
`core/views_*.py` + `intelligence/views_*.py` + `ai_core/views_*.py`;
consider emitting OpenAPI 3.0 spec at build-time; consider consuming
via `openapi-typescript` or `orval` in `frontend/`; consider
retrofitting 93 api-modules to typed pattern (cockpitApi.ts
precedent); consider adding zod runtime validation at api.ts boundary
for integrity-critical endpoints per §17.3 Path C axis. Child C
does NOT commit to any specific path — decision belongs to Group 2500
per §7.1 guardrail. **Load-bearing for xx99 POSTURE-DECISION §20.6.**

**R2** — **[Group 2400 Auth arc — request decision] Silent-401
resolution evidence.** Child C evidence supports a Group 2400
T-slot to request a session-model decision: the two-sided framing
(frontend silent + backend permission-floor inconsistency) presents
three option-space paths — (a) uniform IsAuthenticated across all
`/v1/**` endpoints + client-side auth-gate + observable-error
surfacing; (b) uniform AllowAny for read paths + IsAuthenticated for
writes + client-side auth-check-on-write; (c) per-endpoint permission
registry. Blast radius per A3 estimate: **~630 call-sites (grep-based;
may overcount wrappers/duplicates)**. Child C does NOT commit to any
path — decision belongs to Group 2400 per §7.1 guardrail.

### 19.2 HIGH tier

**R3** — **[Post-arc maintainer-decision batch]** Bundle 18
DEAD-CANDIDATE api-modules (§14 F6) into maintainer signoff before
delete-proof + cleanup PR. Mirror S2202 §19 R2 pattern.

**R4** — **[Post-arc T-slot]** Api-module extraction: split
`frontend/src/lib/api.ts` by domain into `api-*.ts` files
(bettingApi, workspaceApi, humanApi, etc.). Bound to §15.3.

**R5** — **[Post-arc T-slot]** Cross-cutter documentation: draft
`docs/topics/api-contract.md` naming cross-cutters + their consuming
surfaces + edit-blast-radius. Bound to §17.2 + §18.2.

**R6** — **[Post-arc T-slot]** Component-level fetch/axios bypass
cleanup: wrap ~9 sites into api-modules. Bound to §15.5.

### 19.3 MEDIUM tier

**R7** — **[Post-arc T-slot]** MSW integration tests for top-10
highest-traffic endpoints. Bound to §15.4.

**R8** — **[Post-arc T-slot]** Consolidate inline `interface
*Response` declarations across pages/ + components/ into shared
`frontend/src/types/*.ts` files. Bound to §15.6 (dependent on R1
Option (a) or (d)).

**R9** — **[Post-arc T-slot]** cockpitApi ownership documentation +
CODEOWNERS entry for `frontend/src/lib/*.ts`. Bound to §18.1 + §18.3.

**R10** — **[Cross-arc joint 2500+2600 T7]** REST↔WS message
contract SoT unified proposal. Bound to §17.3.

### 19.4 Post-arc maintainer-decision batch (meta-recommendation,
S2202 §19 pattern extension)

**Bundling rule (Rigby SIGN cycle 1 Q18 STRENGTHEN 2026-07-05 fold —
non-arbitrary criterion):** Maintainer signoff batch = any item that
**deletes/renames APIs**, **changes auth/permission semantics**, or
**redefines contract SoT**. Items that stay active-research =
measurement / inventory / falsifier / observation tasks that do not
touch runtime code.

Bundle R3 + R4 + R5 + R6 + R8 + R9 into single governance gate (all
require code-cleanup / API deletion or renaming / documentation-
authoring / auth-adjacent decisions).

**R1 + R2 remain CRITICAL active-research tracks** under Group 2500
(contract SoT design) + Group 2400 (auth session model) — rationale:
R1 is contract-SoT MEASUREMENT + option-inventory (not authoring); R2
is silent-401 SYMPTOM description + Group 2400 handoff evidence (not
auth-model authoring). Both stay research-only until the owning arc
picks them up.

Any additional R-items introduced post-SIGN that meet the bundling
criterion (delete/rename / auth-semantics / SoT-redefinition) should
join the batch; otherwise stay active-research.

## 20. Appendix

### 20.1 Files inspected

Direct-read files (parent Claude verifier-loop):
- `frontend/src/lib/api.ts` (lines 1-100 + 42 grep matches for exports)
- `frontend/src/lib/apiClient.ts` (lines 1-29 full read)
- `frontend/src/lib/cockpitApi.ts` (lines 1-100 full read)
- `docs/research/domains/frontend/2200_frontend_domain_scoping.md`
- `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md` (lines 1-250)
- `docs/research/domains/frontend/2202_frontend_websocket_consumer_ui_render_hint_envelope_audit.md` (lines 1-200 + §20.6 + §20.7)
- `docs/research/domains/sports/1505_sports_frontend_surface_audit.md` (lines 1-50, §14.3, §15.5)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2, §13, §14, §15)
- `00-START-NEXT-SESSION.md` (full)
- `docs/PLATFORM_INVENTORY.md` (via orient preview)
- `docs/PLATFORM_WHAT_IT_IS.md` (via orient preview)
- `sports/views.py` (grep for `extend_schema` decorators)

Sub-agent reads (A1-A6 delegated, per verifier-loop):
- Whole `frontend/src/` tree (grep sweeps for api-module consumers,
  fetch/axios bypass, 401 handlers, Authorization header sites)
- `frontend/src/types/cockpit.ts` (A2)
- `frontend/src/stores/authStore.ts` (A3)
- `core/urls.py` + `core/auth_views.py` (A3 permission-floor sample)
- `frontend/package.json` (A2 codegen check)
- `requirements.txt` + `core/settings.py` (A2 drf-spectacular check)

### 20.2 Docs inspected

- `docs/PLATFORM_INVENTORY.md`
- `docs/PLATFORM_WHAT_IT_IS.md`
- `docs/topics/frontend.md` (via A5 grep)
- `docs/API_PATH_POLICY.md` (A6)
- `docs/ARCHITECTURE.md` (A6)
- `docs/AGENTS.md` (A6)
- Prior-arc doc reads per §12.

### 20.3 Grep patterns used

- `^export const \w+Api\b` in `frontend/src/lib/api.ts` → 93 matches
- `api\.(get\|post\|patch\|delete\|put)\(` in api.ts → 856 matches
- `api\.(get\|post\|patch\|delete\|put)<` in api.ts → 63 matches
- `^export (interface\|type)\s+\w+` in api.ts → 47 matches
- `error\.response\?\.status === 401` in `frontend/src/**` → 1 match
- `Authorization` in `frontend/src/**` outside api.ts → 0 matches
- `drf_spectacular\|extend_schema\|SPECTACULAR` in
  `unified-donkey-betz/` → 13 files (verifier)
- `@extend_schema` in `sports/views.py` → 16 matches
- `@extend_schema` in `core/*.py` → 0 matches
- `openapi-typescript\|orval\|kubb\|swagger-codegen` in
  `frontend/package.json` → 0 matches
- `zod\|io-ts\|valibot\|superstruct\|yup` in `frontend/package.json` →
  0 matches
- `bettingApi\.|humanApi\.|assistantApi\.|workspaceApi\.|contentApi\.|agentsApi\.|sportsHubApi\.`
  in `frontend/src/**/*.{ts,tsx}` → 132 total occurrences across
  24 files

### 20.4 Sampling completeness note (Rigby SIGN cycle 1 Q10 STRENGTHEN
2026-07-05 fold — .js/.jsx falsifier verified)

Whole-frontend grep sweep was scoped to `frontend/src/**/*.{ts,tsx}`.
Verifier ran `Glob frontend/src/**/*.{js,jsx}` = **0 files**. The
`.{ts,tsx}` glob captured the complete frontend source tree; no `.js`
or `.jsx` file exists in `frontend/src/`. Sampling hole objection
foreclosed. Blind-spot minimized; cycle-2 trigger candidate ONLY if
future evidence surfaces `.js/.jsx` files added post-audit that
materially change counts.

### 20.4b Unresolved unknowns

- **UNKNOWN 1** — Full DEAD-CANDIDATE count. §14 F6 lists 18
  verifier-confirmed; another N modules require deep grep sweep
  before delete-proof. Post-arc R3 maintainer-decision batch owns.
- **UNKNOWN 2** — Backend response shape drift across 91 untyped
  api-modules. Only cockpitApi types are canonical; the rest infer
  shape from view code. Full drift rate is unmeasurable without
  runtime tracing.
- **UNKNOWN 3** — Whether `platformApi`'s 30/30 inline-generic typed
  methods are a partial-adoption pattern to emulate or a stopgap that
  will churn under §15.1 Option (a) rollout. Ownership + intent
  unclear. Post-arc R5 documentation candidate.
- **UNKNOWN 4** — Number of `interface *Response` inline duplications
  across `frontend/src/pages/**` + `frontend/src/components/**`.
  §15.6 samples ~12+; full count deferred to R8.
- **UNKNOWN 5** — Whether `sports/views.py` `@extend_schema` wiring
  produces a working OpenAPI 3.0 spec today (`python manage.py
  spectacular --file schema.yaml` untested). Post-arc R1 verification.
- **UNKNOWN 6** — Backend permission-floor sample rate. A3 sampled
  20 endpoints; ~40% not traced (view functions not indexed via
  grep). Full permission-floor uniformity assessment requires
  Group 2400 arc.

### 20.5 Conflicts between sources

**Conflict 1 — Parent scoping §5 Child C path-reference drift
(resolved).**
- Parent scoping §5 Child C referenced `frontend/src/api/*` as api-
  module directory.
- Runtime: `frontend/src/lib/*` (no `frontend/src/api/` exists).
- **Resolution:** Parent scoping path-reference drift; recorded §14
  F1 as `observation` not `drift`.

**Conflict 2 — A2 "zero @extend_schema decorators" claim vs verifier
(resolved).**
- A2 initial claim: "0 @extend_schema decorators across all Python
  views."
- Verifier grep: `sports/views.py` = 16 decorators.
- **Resolution:** A2 undercounted (grep scoped to `core/` only);
  verifier extended to `sports/` + surfaced KEY FINDING per §14 F5.
  drf-spectacular is INSTALLED + PARTIAL-WIRED in `sports/` only.

**Conflict 3 — A4 "27 zero-consumer api-modules" claim vs verifier
(resolved).**
- A4 initial claim: 27 modules with zero consumer imports.
- Verifier grep on `\.overview()` / `\.list()` invocations: 7 of 27
  are CONSUMED by AIConsciousnessTab.tsx + CommandCenterPage.tsx
  (memoryPalaceApi, moodApi, timeTravelApi, evolutionApi,
  relationshipsApi, timeCapsuleApi, homeApi).
- **Resolution:** A4 overclaimed. DEAD-CANDIDATE list REFINED to
  ~18 verifier-confirmed modules; recorded §14 F6.

**Conflict 4 — A1 method-count 1,417 vs A2 call-count 919 (resolved).**
- A1 counted "method definitions per module object" summing to 1,417.
- A2 counted "total api.X() invocations in api.ts" summing to 919.
- Verifier grep: `api\.(get\|post\|patch\|delete\|put)(` = 856 bare +
  63 typed = **919 total api calls** = A2's number.
- **Resolution:** A1 over-counted (some methods use conditional
  branching / helper calls; not every method compiles to 1 api call).
  Denominator for typed-coverage rate = **919** (A2 number). Recorded.

**Conflict 5 — PLATFORM_INVENTORY sectioning (per §14 F2).**
- Inventory has no api-module row.
- Not a drift finding per S2202 F8 precedent — inventory sectioning
  is scope choice. Optional enhancement candidate for xx99.

### 20.6 POSTURE-DECISION evidence plan owed to xx99

Per S2200 §5 Child C delegation — evidence toward whether S1505
§15.5 "no API contract source-of-truth" debt generalizes across all
api-modules or is `/betting`-specific.

**Evidence gathered by Child C:**

| Sub-axis | Contract-level verdict | Evidence pointer |
|---|---|---|
| Whole-frontend typed-response coverage | UNMET (6.85% = 63/919 in api.ts) | §5.3 + §14 F4 |
| Cockpit typed island | STABLE (96% = 52/54 in cockpitApi.ts + 104 hand-written types) | §5.1 + §6.2 |
| drf-spectacular infrastructure | INSTALLED-PARTIAL-WIRED (`sports/views.py` 16 decorators; `core/*.py` 0) | §14 F5 |
| Frontend codegen wiring | UNMET (0 codegen tools in package.json) | §14 F5 |
| Runtime response validation | UNMET (0 zod/io-ts/valibot in package.json) | §14 F5 |
| Silent-401 discipline | UNMET (~100% swallow rate; ~630 call-sites at risk) | §14 F3 |
| Auth wrapper hygiene | STABLE (single centralized interceptor; no component overrides; withCredentials true) | §3 + §14 F3 |
| Cross-boundary discipline | STABLE-with-CROSS-CUTTERS (4 primary cross-cutters MED-HIGH; 90+ modules confined) | §14 F3 + §17.2 |
| Documentation coverage | LIGHT (no dedicated api-layer doc; topics/frontend.md zero contract mentions; PLATFORM_INVENTORY no API-module row) | §11 + §18.2 |
| Ownership | LIGHT (no CODEOWNERS; single-operator context; 407-session churn) | §18.1 |

**Child C recommendation to xx99 (draft, pending Rigby SIGN cycle 1
folds):**

> **§20.6 Option (c) DEFER contract SoT enforcement design** to
> post-Group 2500 API arc close **(default owner = Group 2500 API; if
> ownership shifts, the fallback clause routes to the next arc that
> explicitly owns backend API contract design — per Rigby SIGN cycle 1
> Q11 STRENGTHEN 2026-07-05 fold, preserves accountability without
> brittleness)**. Stage T2 R.API.CONTRACT-SoT-RETROFIT in Group 2500
> T-slot with explicit scope:
> (a) extend `sports/views.py` 16-decorator drf-spectacular wiring
>     to `core/views_*.py` + `intelligence/views_*.py`;
> (b) emit OpenAPI 3.0 spec at build-time;
> (c) wire `openapi-typescript` or `orval` in `frontend/` for
>     generated typed client;
> (d) retrofit 93 api-modules to typed pattern (cockpitApi.ts
>     precedent);
> (e) add zod runtime validation at api.ts boundary for
>     integrity-critical endpoints per S2202 §20.6 Path C axis.
>
> **Escape hatch:** if Group 2500 does not close by S2299 xx99 (Group
> 2200 close), re-evaluate Path A/B/C in the S2299 canonical summary;
> alternatively, open a targeted follow-on-arc T-slot with a hard
> revisit date. Deferral is not open-ended — it is bounded by Group
> 2500 xx99 close cadence.
>
> **Rationale:** Contract SoT design is load-bearing on backend API
> design (URL structure + serializer shape + versioning) — that IS
> the Group 2500 API scope per parent §7.1 Child C → Group 2500
> guardrail. Enforcing SoT in isolation risks double-retrofit
> post-Group 2500 closure.
>
> **Path triad (mirroring S2202 §20.6 Path A/B/C, REST-native
> phrasing per Rigby SIGN cycle 1 Q12 STRENGTHEN 2026-07-05 fold —
> axis = "contract strictness + validation" via OpenAPI schema,
> typed clients, runtime validators, error envelopes):**
> - **Path A — Full-spectrum strict contract rollout.**
>   drf-spectacular platform-wide + `orval` codegen + zod runtime
>   validation + standardized error envelopes for all 93 modules.
>   Coherent with cockpitApi precedent; blast radius LARGE.
> - **Path B — Money-path/integrity-critical only.** Strict
>   contract (typed + validated + error-enveloped) on ~10-15
>   modules (betting, wager, billing, humanApi decision-path,
>   platformApi) + leave read-heavy display-only modules loose.
>   Lint check for governance/money flows only.
> - **Path C — Strict contract mandatory for integrity/governance/
>   money/state-changing REST endpoints; lighter weight (untyped or
>   partially typed) acceptable for read-only / telemetry /
>   display-only signals** (dashboard reads, list endpoints, static
>   content). Enforcement locus varies per-endpoint by the
>   "authoritative-state-mutation?" axis. Path C is the middle
>   ground; may be Group 2500's natural preference if API stability
>   is bounded by class of endpoint, not by transport.
>
> **Option (a) drf-spectacular platform-wide** documented as
> alternative if Group 2500 close date slips past S2299 xx99: extend
> `sports/views.py` decorator pattern; emit OpenAPI schema; consume in
> frontend via `openapi-typescript`. Blast radius: ~500 views + ~93
> api-modules + build pipeline. Rollback LOW (spec-only, additive).
> Example non-authoritative shape only — not an authoring commitment.
>
> **Option (b) hand-written cockpit-pattern extension** documented as
> alternative if Group 2500 requires shape-flexibility incompatible
> with drf-spectacular's autogen: extend cockpitApi.ts precedent
> to 93 modules; hand-write ~800-1500 type interfaces in
> `frontend/src/types/*`. Blast radius: BOUNDED but LARGE. Rollback
> LOW (types-only). Example non-authoritative shape only — not an
> authoring commitment.
>
> **Recommendation-strength: HIGH confidence in the committed action**
> (deferral to Group 2500 is the correct governance sequencing) **+
> Group 2500 is the correct owner of the contract-SoT-design
> decision.** Confidence is NOT claimed on final Path A/B/C outcome —
> the triad is the option space we hand to Group 2500; xx99 close
> does not pre-commit to a specific path. Multi-axis corroboration
> from 6 Explore agents + F4 SYSTEMIC verdict at 6.85% coverage +
> S2202 §20.6 Path C cross-arc parallel + `sports/views.py`
> partial-wiring existence proof.

**Cross-arc evidence flags (owed to xx99):**

- **Group 2400 Auth** — Silent-401 pattern is FE-symptom + Group 2400
  owns session-model resolution. Blast radius per A3: ~630 call-sites.
- **Group 2500 API** — Contract SoT design ownership (per §7.1); T7
  joint REST/WS message contract flag.
- **Group 2600 PA** — assistantApi partial-typing pattern +
  `/pa/chat/*` WS/polling consolidation (§17 T7 extends S2202 T6).
- **Group 1700 Observability** — cockpitApi typed island +
  platformApi observability instrumentation — envelope enforcement
  locus decision joins REST-side.
- **Group 1300 Memory + 1600 Content + 1800 HumanAttention** —
  render-authority split per parent §7.1; cross-cutters `humanApi`
  + `contentApi` share render surface across these domains.

### 20.7 Rigby SIGN fold notes

**Rigby SIGN cycle 1 result: SIGN-with-edits at HIGH confidence** via
dedicated fresh SIGN isolation pin `pa-43bcb30dffd84ef9` (minted at
draft-complete via `session_tool.create_fresh` per playbook §15
SIGN-isolation discipline; retired at cycle close via
`session_tool.retire`). **4 batches × 5 questions = 20 total Q; 20
folds landed pre-commit-gate.** Cycle 2 NOT required per Rigby
cycle-1 HIGH confidence + all 20 folds landable.

**Cadence per feedback_rigby_sign_worker_instability_recovery** —
4×5 batching per 20-section audit shape (FOURTEENTH-consecutive
formal SIGN cycle under Research OS after S1301+S1401+S1501+S1601+
S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202 + S2200
parent scoping = this is the 16th SIGN cycle in the arc-parent-with-
children pattern).

**MC-4 codification note (Rigby SIGN cycle 1 Q19 CLEAN 2026-07-05
fold — codification-language conditionality preserved):** S2203
constitutes candidate evidence for MC-4 template-application count
extension **13 → 14 consecutive**. **Codification framing is
CONDITIONAL** pending Chris ratification / final wording at S2299
canonical summary close per playbook §11.2 template evolution
discipline. This session does NOT unilaterally codify the extension;
it registers the 14-consecutive evidence with Chris-gated ratification
path preserved.

**20 folds by batch:**

- **Batch 1 (Q1-Q5): framing + severity calibration.**
  - **Q1 STRENGTHEN** — §14 F5 drf-spectacular installed-partial-wired
    kept HIGH structural debt + **intent-hedge added**: "Partial
    foundation present; current wiring is sports-only (16 decorators),
    core has 0 — treat as HIGH debt unless an explicit 'sports-only'
    decision exists." Prevents false-confidence framing.
  - **Q2 STRENGTHEN** — §1 + §5.3 dual denominator adopted: **Coverage
    A (api.ts-only) = 6.85% (63/919); Coverage B (global with
    cockpitApi merged) = ~11.8% (115/973)**. Report both views to
    prevent conflation.
  - **Q3 CLEAN + micro-fold** — §14 F1 severity kept HIGH-baseline +
    CRITICAL-for-money-path; risk-channel wording refined to
    **"latent-but-active risk channel: silent auth failures + untyped
    contracts on critical flows"** — no current-incident-rate claim
    required to sustain severity.
  - **Q4 STRENGTHEN** — §14 F6 DEAD-CANDIDATE count hedged
    **"18 identified; expect ~18-25 pending R3 full TSX import/usage
    sweep"**; marked as candidate list not final inventory.
  - **Q5 STRENGTHEN** — §14 F3.5 auth-endpoint whitelist substring
    brittleness **LOW → MEDIUM** (Rigby: "substring whitelists in
    auth are classic footgun that scales badly under route
    evolution"; OAuth callbacks, password-reset flows, hypothetical
    /2fa/ endpoints amplify risk). Downgrade to LOW only if
    intentional-minimality + test-coverage proof exists.
- **Batch 2 (Q6-Q10): falsifier + coverage-math + F4 verdict.**
  - **Q6 STRENGTHEN** — §1 F4 verdict reframed **"SYSTEMIC" →
    "SYSTEMIC-with-surface-variance"** — per-surface table added
    (Betting 0/25, Workspace 0/18, Command-Center partial via
    platformApi, PA 5/22, cockpit 52/54, Other ~0%); all surfaces
    below acceptable-bar threshold (~25%); variance is real but
    doesn't move any surface above bar.
  - **Q7 STRENGTHEN** — §1 + §5.1 + §14 F4 cockpitApi labeled
    **"typed island"** (ops-surface scoped), NOT "cross-surface
    exception"; **"exception demonstrates path, not coverage"**
    wording added — cockpit is existence proof that typing is
    feasible, not a falsifier for SYSTEMIC untypedness of core
    product surfaces.
  - **Q8 STRENGTHEN** — §1 sampling sufficiency note added:
    3-module pathology replication rate = "observed in all sampled
    non-sports modules"; SYSTEMIC claim **anchored to macro-evidence**
    (api.ts centralization + 919 calls + 6.85% typed rate = structural
    evidence at whole-file scale); 3-module sample = strong-signal
    corroboration, not sole proof. R11 broader-repo-grep-counter
    T-slot registered.
  - **Q9 CLEAN + micro-fold** — §1 Denominator contract box added:
    **B1 typed-coverage → 63/919 api.ts-only (Coverage A) OR 115/973
    global (Coverage B); B2 silent-401 → ~630/1300 gated call-sites;
    B3 cross-cutter → 4/94 modules**. Each rate declares unit of
    analysis + scope + sampling method to prevent reader conflation.
  - **Q10 STRENGTHEN** — §20.4 sampling-completeness note added
    covering `.js`/`.jsx` falsifier: verifier ran `Glob
    frontend/src/**/*.{js,jsx}` = **0 files**. Blind-spot foreclosed;
    cycle-2 trigger only if future `.js/.jsx` files added.
- **Batch 3 (Q11-Q15): cross-arc + POSTURE-DECISION defense.**
  - **Q11 STRENGTHEN** — §20.6 default-owner = **Group 2500 API**
    (concrete routing) + fallback clause added: **"or the next arc
    explicitly owning backend API contract design if ownership
    shifts"**. Preserves accountability without brittleness against
    post-S2299 queue reordering.
  - **Q12 STRENGTHEN** — §17.3 T7 + §20.6 Path triad language
    reframed **REST-native**: axis phrased as **"contract strictness
    + validation" (OpenAPI schema, typed clients, runtime validators,
    error envelopes)** rather than "envelope" alone. Path C spirit
    preserved (mandatory rigor for integrity/governance/money/state-
    changing; lighter weight for read-only/telemetry).
  - **Q13 STRENGTHEN** — §17.3 T7 assigned **own T-slot ID**
    (distinct from S2202 T6) while marked **"joint 2500+2600"** to
    preserve shared ownership routing. "Pattern echoes S2202 T6 but
    is distinct enough (REST client contract discipline vs WS
    subscription discipline) to avoid conflation."
  - **Q14 STRENGTHEN** — §14 F3 ~630-call-site quantification hedged
    **"~630 of ~1,300 (~48% estimate, grep-based, may overcount
    wrappers/duplicates)"** + explicit method + hedge label. Preserves
    descriptive/symptomatic posture per §7.1 Group 2400 guardrail
    (no auth-implementation claim).
  - **Q15 STRENGTHEN** — §14 F6 delete-proof gate tightened:
    triad now (a) no imports/usages [primary], (b) no runtime route
    hits in recent telemetry [supporting; noisy/missing telemetry
    doesn't count as absence], (c) **MANDATORY explicit
    maintainer-intent statement**. Only maintainer signoff (R3
    post-arc batch) can flip DEAD-CANDIDATE to REMOVAL-READY.
- **Batch 4 (Q16-Q20): anti-scope + POSTURE + verdict.**
  - **Q16 STRENGTHEN** — §15 remediation options labeled
    **"Options (non-authoring)"** + disclaimer added: "No code
    changes proposed in this doc; enforcement locus owned by Group
    2500/maintainers." §19 R1/R2 language reworked to
    **"open maintainer gate / request decision / queue follow-on
    arc"** verbs — no "implement/change/refactor/enforce/wire" verbs
    in remediation-adjacent text. Anti-scope §7 adherence verified.
  - **Q17 CLEAN** — §20.6 commit-strength framing matches S2202
    §20.6 Q17 fold precedent: **HIGH confidence in (a) deferral
    action + (b) ownership routing to Group 2500 API; NOT claiming
    HIGH confidence on final Path A/B/C outcome.** Triad is option
    space handed to Group 2500; xx99 does not pre-commit to a
    specific path.
  - **Q18 STRENGTHEN** — §19.4 post-arc maintainer-decision batch
    bundling rule made non-arbitrary: **"Maintainer signoff batch =
    any item that deletes/renames APIs, changes auth/permission
    semantics, or redefines contract SoT."** R1 + R2 stay
    active-research with explicit rationale: R1 is contract-SoT
    MEASUREMENT + option-inventory (not authoring); R2 is
    silent-401 SYMPTOM description + Group 2400 handoff evidence
    (not auth-model authoring). Both stay research-only until owning
    arc picks up.
  - **Q19 CLEAN** — MC-4 codification-language framing preserved
    per S2202 Q19 STRENGTHEN precedent: S2203 registered as
    **candidate evidence 13→14 consecutive**; final codification
    wording CONDITIONAL pending Chris ratification at S2299
    canonical summary close.
  - **Q20 verdict** — **SIGN-with-edits at HIGH confidence.**
    Minimum edits pre-commit-gate landed via the 20 folds above.
    Critical residuals: none blocking SIGN. Cycle 2 trigger
    candidates: (a) discovery of meaningful `.js/.jsx` API usage
    changing counts/claims (Q10 falsifier fails), (b) evidence that
    drf-spectacular `sports/`-only wiring is intentional design
    decision (Q1 severity reframe), (c) new data that typed coverage
    is materially higher due to hidden wrappers/generated clients
    not counted (Q2 denominator revisit). Confidence rationale:
    issues were calibration + rubric-math + scope-guarding +
    cross-arc-handoff-ownership + REST-native axis wording, not
    foundational errors.

**Candidate Q1-Q20 for Rigby SIGN cycle 1 (drafted 2026-07-05):**

*Batch 1 (Q1-Q5): Framing + severity calibration.*
- **Q1** — Is the F5 KEY VERIFIER FINDING (drf-spectacular
  installed-partial-wired at `sports/views.py` 16 decorators) correctly
  characterized as HIGH severity STRUCTURAL debt? Or is it a
  "PARTIAL FOUNDATION" observation that should not carry severity
  until the wiring intent is verified via git-log?
- **Q2** — Is the 6.85% typed-coverage denominator correctly framed
  as (63 typed calls / 919 total api.ts calls)? Should the
  denominator include cockpitApi.ts's 54 calls (bringing total to
  919+54=973 with 63+52=115 typed = 11.8%)? Preserve current per-file
  scoping or unify?
- **Q3** — Is the "SoT ABSENT" claim (§14 F4) correctly severity-
  rated HIGH-baseline + CRITICAL-for-money-path? Or does silent shape-
  drift not manifest as active-user-facing risk today (only latent
  future-risk)?
- **Q4** — Does the "18 DEAD-CANDIDATE" (§14 F6) count survive if
  a deeper delete-proof grep is run against `frontend/src/**/*.tsx`?
  Should the count be hedged at "~18-25 pending R3 sweep"?
- **Q5** — Is the auth-endpoint whitelist substring brittleness
  (§14 F3.5) correctly LOW severity? Or is future-scale hardening
  hazard warranting MED?

*Batch 2 (Q6-Q10): Falsifier + coverage-math + F4 verdict.*
- **Q6** — Does F4 SYSTEMIC verdict survive per-surface analysis?
  Sample-check: Betting 0/25 typed = 0%; Workspace 0/18 typed = 0%;
  PA 5/22 typed = 23%; Command-Center partial via platformApi. Does
  the SYSTEMIC verdict hold across ALL surfaces or with surface
  variance?
- **Q7** — cockpitApi's 96% typed is scoped to `/cockpit/*`
  ops-surface. Should this be classified as a "typed island" or as
  a "sole cross-surface exception" and does that scoping matter for
  the SYSTEMIC verdict?
- **Q8** — Was A5's 4-pathology 100% replication rate across 3
  sampled modules the right sampling depth, or is 3 modules too few
  to claim SYSTEMIC generalization? Sampling sufficiency test.
- **Q9** — Denominator contract for the 3 rates: (i) typed-coverage
  = 63/919 (api.ts calls only); (ii) silent-401 rate = ~630/1,300
  (gated call-sites); (iii) cross-cutter rate = 4/94 (modules crossing
  ≥2 surfaces). Are these three denominators separately-scoped or
  should they be unified?
- **Q10** — Sampling completeness note for the whole-frontend grep
  sweep: are there `frontend/src/**/*.{js,jsx}` files that a
  `.{ts,tsx}` glob missed? Grep verification for `.js` / `.jsx`
  presence.

*Batch 3 (Q11-Q15): Cross-arc + POSTURE-DECISION defense.*
- **Q11** — Does §20.6 Option (c) DEFER + escape hatch (Group 2500
  close date) survive if Group 2500 is not the next arc? Post-S2299
  queue ranking depends on Chris D-override — should the deferral
  clause specify Group 2500 by name OR "the next arc that owns
  backend API design"?
- **Q12** — §20.6 Path C (envelope mandatory for integrity /
  governance / money / state-changing REST endpoints) mirrors S2202
  Child B Path C. Is this cross-arc principle actually load-bearing,
  or is REST different enough from WS that the axis should be
  drawn differently?
- **Q13** — T7 cross-arc joint 2500+2600 (§17.3) piggybacks on S2202
  T6 pattern. Is T7 correctly framed as parallel-transport
  consolidation, or is it a distinct opportunity that deserves its
  own T-slot number?
- **Q14** — Group 2400 Auth hedging: F3 silent-401 handoff to
  Group 2400 is worded as "descriptive/symptomatic only" per §7.1.
  Is the ~630 call-site blast-radius quantification (A3) too
  aggressive at Child C scope? Should the number be hedged?
- **Q15** — §2 preamble Interpretation rule for DEAD-CANDIDATE /
  INTENT-NEUTRAL: is the delete-proof triad (imports + logs +
  intent statement) reasonable, or too permissive?

*Batch 4 (Q16-Q20): Anti-scope + verdict.*
- **Q16** — §7 anti-scope adherence: does the doc's verbs stay
  "recommend / propose / evaluate" (not "implement / change /
  refactor")? Spot-check §15 remediation options + §19 R1/R2
  language.
- **Q17** — §20.6 commit-strength framing: HIGH confidence in
  DEFER + Group 2500 ownership is committed; NOT claiming HIGH
  confidence on final Path A/B/C outcome. Does this mirror S2202
  §20.6 Q17 STRENGTHEN fold correctly?
- **Q18** — Post-arc maintainer-decision batch (§19.4): bundles R3
  + R4 + R5 + R6 + R8 + R9 for maintainer signoff. R1 + R2 remain
  active-research tracks. Is the bundling correct or should more
  R-items be batched?
- **Q19** — MC-4 codification-language: S2203 constitutes candidate
  evidence for MC-4 template-application count extension 13 → 14
  consecutive. Codification framing CONDITIONAL pending Chris
  ratification at S2299. Correct per S2202 Q19 STRENGTHEN
  precedent?
- **Q20** — Overall parent-scoping verdict: SIGN-clean / SIGN-with-
  edits / REJECT? If SIGN-with-edits, minimum edits to land before
  commit-gate?

**SIGN cycle 2 trigger candidates:**
- If Q6 per-surface variance materially challenges F4 SYSTEMIC
  verdict.
- If Q8 sampling sufficiency test fails (need ≥5 modules for
  generalization).
- If Q13 T7 framing needs distinct T-slot number vs joint T6+T7.

**MC-4 codification note (conditional):** S2203 is candidate for
MC-4 template-application count extension **13 → 14 consecutive**.
Codification framing CONDITIONAL pending Chris ratification / final
wording at S2299 canonical summary close per playbook §11.2
template evolution discipline + S2202 Q19 STRENGTHEN precedent. This
session does NOT unilaterally codify the extension; it registers the
14-consecutive evidence with Chris-gated ratification path
preserved.

**SIGN pin retirement:** SIGN isolation pin (to-be-minted) will be
retired at cycle close via `session_tool.retire` per playbook §15
SIGN-isolation discipline + `feedback_session_tool_retire_works`.
