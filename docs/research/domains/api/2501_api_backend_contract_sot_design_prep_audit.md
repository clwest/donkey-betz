---
title: "Backend API Contract Source-of-Truth Design-Prep Audit (Group 2500 P1 Cat A)"
session: 2501
status: active (S2501 P1 Cat A Backend API Contract SoT Design-Prep — child audit CLOSED post-Chris "commit it" ratification 2026-07-05. Playbook §11.2 20-section child-audit template TWENTIETH-consecutive application after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401+S2402+S2403+S2404 nineteen prior. **Rigby SIGN cycle 1 COMPLETE 2026-07-05 via dedicated fresh SIGN isolation pin `pa-5b099c873b404e1b` (EIGHTEENTH consecutive dedicated fresh SIGN pin retirement in Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/S2401/S2402/S2403/S2404/S2499/S2500 seventeen prior — retired via `session_tool.retire force=true` at cycle close, updated_count=1, previously_active=true). 4-batch × 5-Q = 20-Q child-audit cadence per S2201-S2404 nine-consecutive tested pattern (TENTH-consecutive application). Rigby overall confidence HIGH across all 4 batches. Cycle 2 NOT required per explicit Rigby verdict at batch 4 close. 18 folds landed pre-Chris-ratification aggregate across 4 batches (batch 1: 4 folds; batch 2: 5 folds including Q7 STRENGTHEN verifier-loop-during-SIGN §14.6 F6 v0 three-shape → v1 FOUR-shape family expansion with 93-site non-DRF JsonResponse fourth family discovery; batch 3: 5 folds; batch 4: 4 folds; Q3 + Q18 SIGN-clean). Within 15-25-fold S2201-S2404 empirical baseline. Chris "commit it" 2026-07-05 ratified 18 folds wholesale — status flipped `draft` → `active` per playbook §16 draft-first workflow. Arc pin `pa-a03b111768464b3f` ACTIVE + PRESERVED through S2501 per playbook §16 arc-standard behavior — no retirement until S2599 xx99 close.)
arc: Research Group 2500 (API — Contract SoT + Silent-401 Downstream Remediation + Session-Lifecycle API Contracts + Per-Endpoint Permission-Floor Registry Design-Prep + REST↔WS T7 Joint 2500+2600) — S2501 P1 Cat A Backend API Contract SoT Design-Prep child audit
category: research (playbook §11.2 20-section child-audit template TWENTIETH-consecutive application)
authors: Claude Code (S2501 P1 Cat A draft 2026-07-05 post-parent-scoping-merge HEAD `77564f76`; parent-Claude verifier-loop applied per playbook §14 pre-draft on 6-Explore-agent sub-agent claims — 4 corrections landed pre-draft); Rigby SIGN cycle 1 COMPLETE via dedicated fresh SIGN isolation pin `pa-5b099c873b404e1b` (EIGHTEENTH consecutive dedicated fresh SIGN pin retirement in Research OS) — 18 folds landed pre-Chris-ratification aggregate across 4 batches per playbook §15; Chris "commit it" 2026-07-05 ratified 18 folds wholesale
verifier_loop: >
  Parent-Claude verifier-loop applied per playbook §14 on 6-Explore-agent
  sub-agent claims pre-draft. Four verifier corrections landed pre-draft:

  1. **HEAD baseline reconciliation.** Explore agents reported HEAD
     `77564f76` (post-parent-scoping-merge PR #2920); parent scoping doc
     recorded `4e6c1ee8` (pre-merge). Both are correct at their
     respective timestamps. S2501 draft records HEAD `77564f76` as the
     authoritative session HEAD.

  2. **URL path count re-baseline.** Explore Agent 3 reported 1,871
     `path()` patterns across 5 URL files (core/urls.py 1,782 +
     core/urls_unified.py 44 + core/urls_real_data.py 9 +
     core/urls_provenance.py 19 + sports/urls.py 17). Parent-Claude
     verifier re-ran + confirmed. Also verified 2 `re_path()` patterns
     in core/urls.py = **1,873 total URL patterns** at HEAD. PLATFORM_
     INVENTORY.md reports 1,864 — **9-pattern drift** (0.48%; drift
     accumulated since PLATFORM_INVENTORY generation at Git HEAD
     `e617af59` 2026-07-05 15:51:41 → S2500 parent scoping merge
     `77564f76`).

  3. **401 response shape verifier correction.** Explore Agent 4
     reported 401 response body uses `APIResponseEnvelope.error()`
     shape (`{"success": false, "error": {"code","message","details"}}`).
     Parent-Claude verifier grepped `APIResponseEnvelope.error|
     APIResponseEnvelope.success` across the codebase and found only
     **9 total usages**. Grepped `status=401|HTTP_401|status.HTTP_401`
     and found **161 direct 401 emission sites**. Grepped
     `raise NotAuthenticated|NotAuthenticated()` and found **0
     matches** — DRF's implicit permission-check flow dominates for
     permission-inherited endpoints (returns `False` from
     `IsAuthenticated.has_permission()`, DRF internally raises 401
     with default `{"detail": "..."}` shape via its own exception
     handler).

     **Verifier-corrected conclusion at HEAD:** three co-existing 401
     shapes on the backend at HEAD `77564f76`:
     (a) DRF default `{"detail": "..."}` — dominant for permission-
         inherited endpoints (implicit-inheritance rate ~80-90% per
         S2402 §14.5 F-B-CRIT-1);
     (b) `APIResponseEnvelope.error()` shape `{"success": false,
         "error": {"code","message","details"}}` — 9 hand-invoked
         sites;
     (c) Bare `Response({...}, status=401)` dict returns — ~152 sites
         (161 direct emission sites − 9 APIResponseEnvelope
         invocations).
     This heterogeneity is Cat A boundary evidence for the ternary
     arc seam (i)/(ii)/(iii) — heavily supports (ii) declared-but-
     uneven contracts or (iii) implicit shape accretion.

  4. **`platform_architecture_inventory.md` §3.22 API Layer row
     EXISTS.** Parent scoping §2.2 recorded "§3.30 API layer TBD
     baseline — Cat A P1 re-verifies whether §3.30 exists as authored
     or requires synthesis at S2501 open." Verifier resolved: §3.30
     is **Body Systems + BodyCoordinator** (line 2222); the **API
     Layer row is §3.22** (line 1648, table row line 232), with
     posture STABLE (Architecture Maturity) + MODERATE (Research
     Coverage) — 1,857 URL patterns / 208 view files / ~51
     WebSocket consumers / Fleet signature auth. This is a positive
     resolution of parent scoping §2.2 uncertainty; S2501 §11 records
     the correction, and §7.3 xx99 anchor-update recommendation
     revises (does not create) the §3.22 row.

  Verifier discipline aligned with S2404 §14.6 F-D-CALL-1 verifier
  correction pattern (F-D-CALL-1 count 803 corrected during draft
  writing per Cat D verifier-loop). Six additional Cat-A-relevant
  verifier confirmations (all sub-agent claims verified accurate at
  HEAD): 96 total Serializer classes (Agent 1 said 95 — minor
  undercount +1); 91 `class Meta: model = X` matches (Agent 1
  verified); 563 concrete Django models (PLATFORM_INVENTORY says 585
  — 22-model drift, likely abstract models excluded from grep);
  SPECTACULAR_SETTINGS = 4 keys at `core/settings.py:1600-1605`
  (Agent 2 verified: TITLE + DESCRIPTION + VERSION +
  SERVE_INCLUDE_SCHEMA=False); CODEOWNERS EXISTS at repo root
  (established at S2499 Group 2400 Auth AU-D5 close per Cat D
  F-D-OWN-1 remediation) — but `/sports/views.py` + `/core/views*.py`
  NOT explicitly listed (fall to default `* @clwest`); §3.22 API
  Layer row EXISTS at line 1648 (Agent 5 correct; parent scoping
  §2.2 imprecise).
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                                            # runtime counts anchor (1,864 path() per Git HEAD `e617af59` — 9-pattern drift vs S2501 verified 1,873 at HEAD `77564f76`)
  - docs/PLATFORM_WHAT_IT_IS.md                                                           # narrative anchor
  - docs/research/platform_architecture_inventory.md                                      # S1273 32-domain map §3.22 API Layer STABLE + MODERATE (line 1648; row 22 table line 232)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                              # process contract §11.2 TWENTIETH application
  - docs/research/domains/api/2500_api_domain_scoping.md                                   # primary predecessor input — S2500 parent scoping §3.A Cat A mission + AC #1/#2/#4/#7 boundary + §7 anti-scope + §6 P-1 to P-11 parked items
  - docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md # §14.1 F1 SoT-ABSENT + §14.6 F5 drf-spectacular INSTALLED but wired ONLY in sports/views.py + §19.1 R1 whole-platform contract SoT rollout + §20.6 Path A/B/C triad + REST-native axis
  - docs/research/domains/frontend/2299_frontend_canonical_summary.md                     # §5.1 canonical seam ("declared-but-unenforced contracts") + §8.2 T2 Group 2500 API cross-arc handoff bundle + §8.3 R6 error-boundary framework BLOCKING PREREQUISITE
  - docs/research/domains/auth/2499_auth_canonical_summary.md                             # T2 Group 2500 API cross-arc handoff — 7 CF-*1 flags (CF-D1 typed-error-envelope + CF-D2 803-call-sites + CF-D3 79-raw-fetch + CF-B1 per-endpoint permission registry + CF-B3 PHANTOM + CF-B4 stacking + CF-C1 refresh + CF-C2 Clear-Site-Data + CF-C3 storageKeys)
  - docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md    # §14.5 21-loci permission-floor rate + §19.1 (a)/(b)/(c) three-option Cat B PRIMARY (c) LONG-TERM GOVERNANCE
  - docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md # §14.5 803 consumer classification + §19.1 α/β/γ × 2 typed-error-envelope Cat D CF-D1
  - sports/views.py                                                                       # 16 @extend_schema decorators at lines 58, 117, 164, 344, 357, 385, 500, 568, 744, 848, 887, 907, 924, 953, 987, 1023 (HEAD-verified)
  - core/settings.py                                                                      # `SPECTACULAR_SETTINGS = {...}` at 1600-1605; INSTALLED_APPS lines 161-215 (drf_spectacular ABSENT); REST_FRAMEWORK lines 645-669 (DEFAULT_PERMISSION_CLASSES=IsAuthenticated; NO EXCEPTION_HANDLER override)
  - core/api_responses.py                                                                 # APIResponseEnvelope.error() shape at lines 53-98 (9 total usages across codebase — minority envelope)
  - CODEOWNERS                                                                            # established at S2499 Group 2400 Auth AU-D5 (Cat D F-D-OWN-1 remediation); default `* @clwest`; API-slice-specific paths NOT explicitly listed
  - requirements.txt                                                                      # drf-spectacular==0.28.0 INSTALLED (verified via `import drf_spectacular`)
delegated_from:
  - Group 2500 S2500 §3.A Cat A mission — "Establish research-only + design-prep baseline for backend API contract source-of-truth"
  - Group 2200 S2203 §14.1 F1 (backend API contract SoT-ABSENT — cross-arc DEFERRED to Group 2500 per §20.6 Option (c))
  - Group 2200 S2203 §14.6 F5 (drf-spectacular INSTALLED but wired ONLY in sports/views.py — KEY VERIFIER FINDING extended at S2501 per §14.6 below)
  - Group 2200 S2299 §5.1 canonical seam ("declared-but-unenforced contracts" / "design-latent infrastructure — partially scaffolded; unevenly wired")
  - Group 2200 S2299 §8.2 T2 handoff bundle to Group 2500 API
  - Group 2400 S2402 CF-B1 per-endpoint permission registry Cat B (c) LONG-TERM GOVERNANCE — Cat A boundary at declaration side
  - Group 2400 S2404 CF-D1 typed-error-envelope Cat D α/β/γ — Cat A boundary at declaration side
delegates_to:
  - S2599 xx99 canonical summary (Group 2500 close) — anchor-update recommendations for PLATFORM_INVENTORY §API autoblock + PLATFORM_WHAT_IT_IS §API narrative subsection + docs/topics/api.md + ARCHITECTURE_INDEX Path A/B/C decision matrix pointer
  - S2502 P2 Cat B Frontend API-client Architecture design-prep — inherits 803 consumer call-site re-verify from Cat A boundary + 47 exported TypeScript interfaces + 18 DEAD-CANDIDATE api-modules + 79 raw-fetch bypass reconciliation
  - S2503 P3 Cat C Error-envelope + refresh + logout API contracts design-prep — inherits three co-existing 401 shapes at HEAD from Cat A boundary + APIResponseEnvelope 9-usage minority envelope evidence
  - S2504 P4 Cat D Permission-floor registry design-prep + REST↔WS T7 joint — inherits per-endpoint permission_classes coverage matrix + ~40 WS emit-site inventory from Cat A boundary
lens: >
  Cat A boundary lens question (subordinated to Group 2500 central
  lens Chris-locked "agree all" 2026-07-05 with OpenAPI-canonical
  clause per Rigby SIGN-preview Q2 fold):

  "Does the backend API surface at HEAD `77564f76` DECLARE its
  contract source-of-truth (typed request/response schemas + typed
  error envelopes + per-endpoint permission-floor declarations) — or
  are these contracts EMERGENT from runtime/serialization/client
  inference?"

  Cat A boundary evidence-only: Cat A collects DECLARATION evidence
  (what the backend declares to schema consumers) without recommending
  Path A/B/C verdict, without authoring @extend_schema retrofit, and
  without picking typed-client codegen framework (§7 anti-scope #7).
  Verdict on ternary seam (i) coherent contract spine / (ii)
  declared-but-uneven contracts / (iii) implicit shape accretion is
  a Chris-D-verdict-request at S2599 xx99 close after all 4 children
  have contributed evidence.
playbook_application: §11.2 20-section child-audit template TWENTIETH-consecutive application per S2500 §5 child mission sequence; §13 six-parallel-Explore-agent sweep contract applied at S2501 open — 6 Explore agents dispatched with self-contained briefs (Models + Persistence / Services + Runtime Flows / APIs + Tools + Tasks + Commands / Integrations + Cross-Domain / Documentation + Prior Research / Drift + Debt + Ownership + Maturity); §14 parent-Claude verifier-loop applied pre-draft — 4 corrections landed pre-draft; §15 SIGN cycle 1 REQUIRED at child-audit stage per playbook §15 stage-scoped routing — routed via dedicated fresh SIGN isolation pin (NOT arc pin `pa-a03b111768464b3f`) per playbook §15 SIGN-isolation discipline (EIGHTEENTH consecutive dedicated fresh SIGN pin candidate under Research OS after 17 prior); §16 arc pin `pa-a03b111768464b3f` PRESERVED through S2501 per playbook §16 arc-standard behavior (no retirement until S2599 xx99 close)
---

# Backend API Contract Source-of-Truth Design-Prep Audit (Group 2500 P1 Cat A)

> **ACTIVE.** S2501 P1 Cat A child audit CLOSED post-Chris
> "commit it" ratification 2026-07-05 (HEAD `77564f76`).
> 6-parallel-Explore-agent sweep + parent-Claude verifier-loop per
> playbook §14 (4 pre-draft corrections) + Rigby SIGN cycle 1 via
> dedicated fresh SIGN isolation pin `pa-5b099c873b404e1b` (18 folds
> landed pre-Chris-ratification across 4 batches; Rigby overall
> confidence HIGH; cycle 2 NOT required; SIGN pin RETIRED at cycle
> close — EIGHTEENTH consecutive dedicated fresh SIGN pin retirement
> in Research OS). Chris "commit it" 2026-07-05 ratified — status
> flipped `draft` → `active` per playbook §16 draft-first workflow.
> Arc pin `pa-a03b111768464b3f` PRESERVED through S2501 (no
> retirement until S2599 xx99 close per playbook §16 arc-standard
> behavior). TWENTIETH-consecutive playbook §11.2 20-section child-
> audit template application.

> **Cat A boundary discipline paramount.** Cat A collects EVIDENCE
> for future Chris-D-verdicts on Path A/B/C triad (S2203 §20.6),
> Cat C α/β/γ typed-error-envelope (S2499 CF-D1), Cat D per-endpoint
> permission registry (S2499 CF-B1). Cat A does NOT recommend
> verdicts; Cat A does NOT author code; Cat A does NOT pick codegen
> frameworks (§7 anti-scope #7).

## 1. Executive Summary

Backend API Contract SoT layer at HEAD `77564f76` is
**INFRASTRUCTURE-SCAFFOLDED + APP-DISCONNECTED + DECORATOR-INERT** —
`drf-spectacular==0.28.0` is pip-installed (verified via `import
drf_spectacular`), `SPECTACULAR_SETTINGS = {...}` is configured at
`core/settings.py:1600-1605` with 4 keys (TITLE + DESCRIPTION +
VERSION + `SERVE_INCLUDE_SCHEMA=False`), 16 `@extend_schema`
decorators are applied in `sports/views.py` (lines 58, 117, 164,
344, 357, 385, 500, 568, 744, 848, 887, 907, 924, 953, 987, 1023),
0 `@extend_schema` in `core/*.py` (~209 view files), but
`drf_spectacular` is **NOT registered in INSTALLED_APPS** (verified
against `core/settings.py:161-215`) and **no `SpectacularAPIView`
URL route is registered** (only `path('api/bpaas/schema/', ...)` at
`core/urls.py:4891` which is a custom endpoint, not drf-spectacular).
`python manage.py spectacular` returns "Unknown command." Result:
the 16 sports/views.py `@extend_schema` decorators are effectively
inert; no runtime OpenAPI schema generation occurs.

**This is a materially stronger negative than S2203 §14.6 F5
"INSTALLED-PARTIAL-WIRED" claim.** The evidence at HEAD is: INSTALLED
+ CONFIGURED + PARTIALLY-DECORATED + FULLY-DISCONNECTED. This
resolves S2299 §6 UNKNOWN 5 (drf-spectacular schema.yaml generation
feasibility) with a **negative outcome** — schema generation is not
possible at HEAD without at minimum: (1) adding `drf_spectacular` to
`INSTALLED_APPS`, (2) registering `SpectacularAPIView` URL route,
(3) resolving whatever caused the app to be omitted from
INSTALLED_APPS despite the SPECTACULAR_SETTINGS + decorator adoption
demonstration existing.

**Contract-declaration surface enumeration at HEAD (Cat A DECLARATION
BOUNDARY, per playbook §5 phase discipline research-only + design-
prep):**

- **`@extend_schema` decoration rate:** 16 of 1,873 total URL patterns
  = **~0.85% decoration rate** (numerator 16 sports; denominator
  verified: 1,782 core/urls.py path() + 44 core/urls_unified.py + 9
  core/urls_real_data.py + 19 core/urls_provenance.py + 17
  sports/urls.py + 2 re_path in core/urls.py = 1,873; PLATFORM_
  INVENTORY.md 1,864 = **9-pattern drift**).
- **Field-level / class-level contract decorator adoption rate:**
  `@extend_schema_serializer` = 0; `@extend_schema_view` = 0;
  `@extend_schema_field` = 0; `inline_serializer()` = 0;
  `OpenApiExample` / `OpenApiResponse` = 0. **Zero adoption of
  drf-spectacular's deeper decoration primitives.**
- **DRF Serializer/ModelSerializer coverage:** 96 total Serializer +
  ModelSerializer subclasses across the repo (verified); 91 declare
  a `class Meta: model = X` binding (Cat A per verifier-corrected
  Agent 1 report); 563 concrete Django models per grep at HEAD
  (PLATFORM_INVENTORY.md reports 585 — 22-model drift, likely
  abstract models excluded from grep). **Model → serializer coverage
  ≈ 91/563 = 16.2%.**
- **Runtime 401 response shape heterogeneity (three co-existing
  shapes):** (a) DRF default `{"detail": "..."}` — dominant for
  permission-inherited endpoints (implicit-inheritance rate ~80-90%
  per S2402 §14.5 F-B-CRIT-1); (b) `APIResponseEnvelope.error()`
  shape `{"success": false, "error": {"code","message","details"}}`
  — 9 hand-invoked sites at `core/api_responses.py:53-98`; (c) bare
  `Response({...}, status=401)` dict returns — ~152 sites (161
  direct 401 emission sites − 9 APIResponseEnvelope invocations).
  **`REST_FRAMEWORK` has NO `EXCEPTION_HANDLER` override** (verified
  at `core/settings.py:645-669`) — DRF's default exception handler
  produces `{"detail": "..."}` when no view-code intervenes.

**Contract-declaration surface verdict (Cat A boundary):** At the
declaration level, the platform's API contract source-of-truth is
**a heterogeneous mix of (a) declared-but-inert (`@extend_schema`
decorators dormant), (b) declared-through-serializer-coverage (~16.2%
model → serializer rate), (c) declared-through-view-code-envelope
(APIResponseEnvelope at 9 sites), (d) declared-by-DRF-default
(implicit-inheritance for ~80-90% of endpoints), and (e) undeclared
(bare `Response({...})` dict returns)**. Cat A boundary evidence is
consistent with both (ii) declared-but-uneven contracts and (iii)
implicit shape accretion; Cat A does not assign weights or select a
verdict — weights are deferred to S2599 xx99 close after all 4
children contribute evidence. Evidence in this audit does not rule
out (i) coherent contract spine; it only establishes that the
current OpenAPI declaration mechanism is disconnected at HEAD
(Rigby SIGN cycle 1 batch 1 Q1 fold — verdict-neutrality precision).

**Biggest Cat-A-boundary gaps (§19 recommends future research —
Chris-D-verdict-request):**
1. drf-spectacular app-registration + URL-routing wire-up
   prerequisite blocks Path A/B/C triad measurement.
2. `@extend_schema` decoration rate ~0.85% cannot support Path A
   evaluation without a per-endpoint retrofit design-prep spec.
3. Three co-existing 401 shapes at HEAD blocks Cat C α/β/γ + Cat D
   typed-error-envelope decision spaces from measuring "current
   state" — envelope shape is not a single fact.

**What comes next.** S2502 Cat B receives Cat A boundary evidence
for 803 consumer call-site re-verify at HEAD; S2503 Cat C receives
Cat A three-co-existing-401-shapes evidence; S2504 Cat D receives
Cat A per-endpoint permission_classes coverage matrix + ~40 WS
emit-site inventory. S2599 xx99 close synthesizes arc-seam verdict.

## 2. Domain Purpose

**Playbook §9 canonical Q1-Q2 — What is this domain?**

The Backend API Contract SoT layer is the **declaration-side
substrate** of the Donkey Betz REST + WebSocket API surface — the
mechanism by which the backend tells (a) frontend consumers, (b)
mobile consumers, (c) tooling consumers, (d) API-adjacent research/
audit consumers what shapes it accepts (request bodies + query
parameters + path parameters) and what shapes it returns (typed
success responses + typed error envelopes + per-endpoint auth
requirements). At HEAD `77564f76`, the layer is
**INFRASTRUCTURE-SCAFFOLDED + APP-DISCONNECTED + DECORATOR-INERT**
per §1 evidence.

**What Cat A's boundary is:** the DECLARATION side. Cat A owns
questions of the shape "does the backend DECLARE X to consumers?"
Cat A does NOT own questions of the shape "does the frontend
CONSUME X correctly?" (Cat B P2 owns), "does the ERROR-envelope
UX-policy propagate?" (Cat C P3 owns), or "does the PERMISSION-floor
REGISTRY track per-endpoint enforcement?" (Cat D P4 owns).

**Domain purpose scope discipline (per playbook §5 phase discipline
research-only + design-prep):** Cat A collects evidence for future
Chris-D-verdicts. Cat A does NOT recommend, decide, or author.
Everything below is EVIDENCE. Nothing below is DIRECTIVE.

## 3. Canonical Entry Points

**Playbook §9 canonical Q3 — Where does the domain enter the system?**

### 3.1 drf-spectacular infrastructure entry points (at HEAD `77564f76`)

| Entry Point | Location | State | Cite |
|---|---|---|---|
| Python package | `drf-spectacular==0.28.0` | INSTALLED (verified `import drf_spectacular` succeeds) | `requirements.txt` |
| Settings block | `SPECTACULAR_SETTINGS = {...}` | 4 keys defined — TITLE, DESCRIPTION, VERSION, `SERVE_INCLUDE_SCHEMA=False` | `core/settings.py:1600-1605` |
| INSTALLED_APPS registration | `'drf_spectacular'` in INSTALLED_APPS list | **ABSENT** — app never registered despite settings + decorator adoption | `core/settings.py:161-215` (54 apps listed, no drf_spectacular) |
| URL route | `SpectacularAPIView` / `SpectacularSwaggerView` / `SpectacularRedocView` | **ABSENT** — only custom `bpaas_schema` endpoint | `core/urls.py:4891` (`path('api/bpaas/schema/', bpaas_schema, name='bpaas-schema')` — CUSTOM, not drf-spectacular) |
| Management command | `python manage.py spectacular` | **UNKNOWN COMMAND** — schema generation not possible at HEAD | shell verification 2026-07-05 |

**Consequence:** all 16 `@extend_schema` decorators in
`sports/views.py` are decorator-inert. Cat A's Explore Agent 2
described this as "orphaned metadata" — annotation exists at parse
time but no runtime schema generation occurs because the schema-
generator app is never loaded. **Cat A characterizes the state as
FULLY-DISCONNECTED (i.e., disconnection is from executable schema
generation + routing; decorators exist but are inert without the
app / command / route)** (Rigby SIGN cycle 1 batch 1 Q2 optional
fold — parenthetical precision to preempt pedantry).

### 3.2 `@extend_schema` decoration inventory (16 total at HEAD)

Per-decorator disposition per verifier-corrected Explore Agent 1
analysis (Cat A boundary, DECLARATION side only):

| Line | Decorator kind | Uses `responses=` | Uses `request=` | Uses `inline_serializer()` |
|---|---|---|---|---|
| 58 | @extend_schema | ✓ responses=LeagueStandingsSerializer | — | — |
| 117 | @extend_schema | — (summary-only) | — | — |
| 164 | @extend_schema | — (summary-only) | — | — |
| 344 | @extend_schema | ✓ | — | — |
| 357 | @extend_schema | — (summary-only) | — | — |
| 385 | @extend_schema | — (summary-only) | — | — |
| 500 | @extend_schema | — (summary-only) | — | — |
| 568 | @extend_schema | ✓ | — | — |
| 744 | @extend_schema | — (summary-only) | — | — |
| 848 | @extend_schema | — (summary-only) | — | — |
| 887 | @extend_schema | — (summary-only) | — | — |
| 907 | @extend_schema | — (summary-only) | — | — |
| 924 | @extend_schema | — (summary-only) | — | — |
| 953 | @extend_schema | — (summary-only) | — | — |
| 987 | @extend_schema | — (summary-only) | — | — |
| 1023 | @extend_schema | — (summary-only) | — | — |

**Cat A boundary observation:** even within the 16-decorator sports
demonstration, only 3 of 16 (~18.8%) declare a `responses=` typed
schema. 13 of 16 (~81.2%) are summary-only annotations that would
generate an empty schema entry even if drf-spectacular were wired.
This is Cat A boundary evidence that the demonstration coverage
overstates the declaration depth — a Path A retrofit against 1,873
endpoints would need not just app-registration + URL-routing +
decorator-application but also `responses=` schema authoring per
endpoint.

### 3.3 REST-side view file inventory

- 209 files matching `core/views*.py` per PLATFORM_INVENTORY.md.
- 0 `@extend_schema` decorators across the 209 files
  (verifier-confirmed).
- `sports/views.py` = 1,039 LOC + 16 `@extend_schema` decorators
  (verifier-confirmed).

### 3.4 URL routing entry points

- `core/urls.py` = 1,782 `path()` + 2 `re_path()` patterns.
- `core/urls_unified.py` = 44 `path()` patterns.
- `core/urls_real_data.py` = 9 `path()` patterns.
- `core/urls_provenance.py` = 19 `path()` patterns.
- `sports/urls.py` = 17 `path()` patterns.
- **Total = 1,873 URL patterns at HEAD `77564f76`** (verifier-
  corrected; PLATFORM_INVENTORY.md 1,864 is 9-pattern drift).

## 4. Major Models

**Playbook §9 canonical Q4-Q5 — What are the major models + how do
they relate?**

**Cat A boundary: DRF Serializer / ModelSerializer inventory as
contract DECLARATION artifacts** (not the domain data models
themselves — those are inventoried by their owning-arc audits).

### 4.1 Serializer class inventory at HEAD

- **Total DRF `Serializer` + `ModelSerializer` subclasses across
  repo: 96** (parent-Claude verifier-corrected from Explore Agent 1
  95; grep pattern
  `^class \w+\(.*(ModelSerializer|serializers\.Serializer|Serializer)\)`
  across `**/*.py`).
- **Serializer subclasses declaring `class Meta: model = <M>`: 91**
  (grep pattern `class Meta:` followed by `model = ` within 3 lines
  = 91 matches).
- **Serializer files:** primary loci at `sports/serializers.py`,
  `core/serializers_agents.py`, `content/serializers.py`, and view-
  adjacent inline serializers in `core/views_workspace_api.py`,
  `core/views_preview_api.py`, etc.

### 4.2 Model → Serializer contract coverage rate

- 563 concrete Django models via grep
  `^class \w+\(.*models\.Model` (excluding abstract mixins).
- PLATFORM_INVENTORY.md reports 585 models — **22-model drift**
  (likely abstract models included in inventory count but excluded
  from Cat A grep).
- **91 models with declared ModelSerializer binding / 563 concrete
  models = ~16.2% model → serializer coverage rate at HEAD.**

**Cat A boundary observation:** at contract-DECLARATION level, the
platform has ~84% of its data models with no ModelSerializer
binding. This does not mean these models are unused via API — many
are served via bare `Response({...})` dict returns or via
serializers defined inline within view code. Cat A boundary evidence
for the arc seam: the contract SoT relies MORE on runtime
serialization patterns and view-code envelope construction than on
declared-serializer-binding.

### 4.3 Money-path / governance-path / PA-path serializer distribution

Per Explore Agent 1 + parent-Claude verifier corroboration:

- **Money-path serializers (~25 total):** `LeagueSerializer` /
  `TeamSerializer` / `GameSerializer` / `BettingMarketSerializer` /
  `BetSerializer` / `ArbitrageOpportunitySerializer` /
  `BettingRecommendationSerializer` / `SportsAnalyticsSerializer`
  etc. (`sports/serializers.py:18-598`). Mostly ModelSerializer;
  some inline custom (e.g., `UserBettingStatsSerializer`,
  `MarketAnalysisSerializer`).
- **Governance-path serializers (~35 total):**
  `UnifiedAgentTemplateSerializer` /
  `AgentExecutionSerializer` /
  `AgentOrchestrationSerializer` /
  `AgentChannelSerializer` /
  `AgentChannelMessageSerializer` etc.
  (`core/serializers_agents.py:25-407+`). ModelSerializer-dominated.
- **PA-path serializers (~35 total):** `ContentTemplateSerializer` /
  `DocumentSerializer` / `ContentGenerationSerializer`
  (`content/serializers.py:21-155`); `WorkspaceContextSerializer`
  (`core/views_workspace_api.py:38`); `ProjectRepoSerializer`
  (`core/views_preview_api.py:35`). ModelSerializer-dominated with
  significant inline serializer authoring in view files.

**Money-path sample of endpoint response construction pattern
(Explore Agent 1 sample; parent-Claude spot-verified):**

| Endpoint | Response Type | Verifier-supported |
|---|---|---|
| `LeagueViewSet.standings` (sports/views.py:63) | (a) Serializer(...).data | Yes |
| `LeagueViewSet.betting_trends` (sports/views.py:119) | (c) bare dict | Yes |
| `TeamViewSet.betting_analytics` (sports/views.py:166) | (c) bare dict | Yes |
| `GameViewSet.odds` (sports/views.py:349) | (a) Serializer(...).data | Yes |
| `BettingMarketViewSet.odds_comparison` (sports/views.py:500) | (c) bare dict | Yes |
| `BettingMarketViewSet.analysis` (sports/views.py:568) | (a) Serializer(...).data | Yes |
| `BetViewSet.stats` (sports/views.py:746) | (c) bare dict | Yes |
| `ArbitrageOpportunityViewSet.scan` (sports/views.py:848) | (c) bare dict | Yes |

**Cat A boundary observation:** even in the sole `@extend_schema`-
decorated module, ~60% of endpoints use bare `Response({...})`
returns (bypass ModelSerializer typing). This is Cat A DECLARATION-
boundary evidence for arc seam (ii)/(iii): the contract is heavily
runtime-shape-emergent even at the demonstration surface.

## 5. Major Services

**Playbook §9 canonical Q6-Q7 — What are the major services + what
do they do?**

**Cat A boundary: drf-spectacular's schema generator + related
management commands + tool-dispatcher schema awareness.**

### 5.1 drf-spectacular schema generator — DISCONNECTED at HEAD

The `drf_spectacular.generators.SchemaGenerator` engine is the
service that would (if wired) walk the URL router + `@extend_schema`
decorators + Serializer classes and emit OpenAPI 3.0 schema. At HEAD
`77564f76` the engine is not invoked because:

1. `drf_spectacular` not in INSTALLED_APPS (`core/settings.py:161-215`).
2. No `SpectacularAPIView` URL route (`core/urls.py` grep for
   `SpectacularAPIView|schema/openapi` returns 0 matches beyond
   custom `bpaas_schema` at line 4891).
3. `python manage.py spectacular` returns "Unknown command"
   (verified 2026-07-05).

### 5.2 Contract-adjacent management commands

Explore Agent 3 grepped `core/management/commands/` (199 commands
per PLATFORM_INVENTORY.md) for names matching
`schema|spec|openapi|contract|verify_doc|verify_api|api_lint` and
found:

- **`verify_doc_claims.py`** — Doc-vs-reality claim verifier (built
  Session 1099 post-agent-system audit for detecting ~7 distinct
  drifts between docs and runtime). **Not schema-contract-focused**
  — verifies documentation drift, not API schema drift. Cat A
  boundary observation: verifier for API contract SoT does NOT exist
  at HEAD (drift-verifier infrastructure gap for the SoT layer
  itself).
- **`celery_inspect_report.py`** — Celery task inspection (Cat A
  irrelevant).
- **Zero matches for `schema`, `spec`, `openapi`, `contract` at
  command-name level** across the 199 commands.

### 5.3 `APIResponseEnvelope` service — 9 hand-invoked sites (minority envelope)

`core/api_responses.py:53-98` defines
`APIResponseEnvelope.error()` producing shape:

```json
{
  "success": false,
  "error": {
    "code": "<machine-readable-error-code>",
    "message": "<human-readable-message>",
    "details": <optional>
  }
}
```

**Cat A verifier-corrected finding:** parent-Claude grepped
`APIResponseEnvelope\.error|APIResponseEnvelope\.success` and found
**9 total usages** across the codebase. This is a **minority
envelope** — not the dominant shape. The dominant shape is DRF's
default `{"detail": "..."}` for permission-inherited endpoints (per
§5.4 below) plus bare `Response({...}, status=401)` at ~152 sites
(per §7.2 below).

### 5.4 DRF permission-check + exception-handler chain

Cat A DECLARATION-boundary shape of 401 responses depends on which
service produces them:

- **`REST_FRAMEWORK` at `core/settings.py:645-669`:** declares
  `DEFAULT_PERMISSION_CLASSES = ['rest_framework.permissions.IsAuthenticated']`
  (line 652) + `DEFAULT_AUTHENTICATION_CLASSES` = 2 custom classes
  (`MobileTokenAuthentication` + `CsrfExemptSessionAuthentication`).
  **NO `EXCEPTION_HANDLER` override** (grep verified 2026-07-05).
- Consequence: for the ~80-90% of endpoints inheriting DEFAULT
  permission (per S2402 §14.5 F-B-CRIT-1), DRF's built-in exception
  handler produces `{"detail": "Authentication credentials were not
  provided."}` on permission fail.
- **0 `raise NotAuthenticated` matches** across the codebase — DRF's
  implicit permission-check flow dominates (returns `False` from
  `IsAuthenticated.has_permission()`, DRF internally raises the
  exception with default flat body shape).

### 5.5 Tool-dispatcher schema awareness

Per Explore Agent 3: `core/services/tool_dispatcher.py:1265` handles
PA-tool-schema live-reload; `core/services/tool_dispatcher.py:435`
registers `platform_config_tool`. **Tool-dispatcher's schema-
awareness is INTERNAL to the PA-tool registry system, not connected
to API-contract SoT.** Cat A boundary observation: schema-awareness
exists at the PA-tool layer but does NOT propagate to a broader API-
contract SoT service.

**Boundary note (Rigby SIGN cycle 1 batch 1 Q4 fold — pattern-
analogy capture without recommendation):** the PA tool schema
system is not part of the external API contract SoT, but it is
relevant as an existence proof for a registry-driven contract
surface (typed schema + dispatch gating + runtime validation).
Cat A records it only as a pattern analogue, not as an
implementation recommendation. Whether the PA-tool-schema pattern
generalizes to the API contract SoT layer is out of Cat A boundary
scope; Chris-D-verdict-request at S2599 xx99 close if load-bearing.

## 6. Major APIs and Interfaces

**Playbook §9 canonical Q8-Q9 — What are the major API endpoints +
their contracts?**

**Cat A owns the API-slice manifest draft per AC #7 (Chris "agree
all" 2026-07-05 with Rigby SIGN cycle 1 Q3-1 spec-only guardrail
fold — deliverable is a measurement SPEC, not a shipped script).**

### 6.1 Scoped API-slice manifest (draft candidate for AC #7)

**Money-path slice (partial enumeration — 10 representative
endpoints):**

| Method | Path | View | File:Line | @extend_schema? | permission_classes? | Response shape |
|---|---|---|---|---|---|---|
| POST | `/api/v1/betting/place/` | `place_bet` | `core/views_betting.py:21` | — | inherit (IsAuth default) | bare dict |
| POST | `/api/v1/betting/wager/` | `log_wager` | `core/views_odds_sports.py:2621` | — | inherit | bare dict |
| GET | `/api/v1/betting/wagers/` | `get_wagers` | `core/views_betting.py` | — | inherit | bare dict |
| POST | `/api/v1/betting/wagers/<uuid>/settle/` | `settle_wager` | `core/views_betting.py:273` | — | inherit | bare dict |
| GET | `/api/v1/betting/stats/` | `get_betting_stats` | `core/views_betting.py` | — | inherit | bare dict |
| GET | `/api/v1/revenue/stats/` | `revenue_stats_view` | `core/views_revenue_tracking.py` | — | inherit | bare dict |
| GET | `/api/distribution/revenue/dashboard/` | `revenue_dashboard` | `core/views_revenue_analytics.py:779` | — | inherit | bare dict |
| POST | `/api/stripe/subscribe/` | `stripe_subscribe` | `core/views_stripe_billing.py:1152` | — | inherit | bare dict |
| GET | `/api/stripe/invoices/` | `stripe_invoices` | `core/views_stripe_billing.py:3763` | — | inherit | bare dict |
| GET | `/api/stripe/payment-methods/` | `stripe_payment_methods` | `core/views_stripe_billing.py:3759` | — | inherit | bare dict |

**Cat A boundary observation:** **0 of 10 sampled money-path
endpoints have `@extend_schema` decoration at HEAD.** Cat A DOES
NOT recommend decoration; Cat A records the coverage gap as
Chris-D-verdict-request evidence.

**Governance-path slice (partial enumeration — 10 representative):**

| Method | Path | View | File:Line | @extend_schema? |
|---|---|---|---|---|
| GET | `/api/boardroom/decisions/` | `get_boardroom_decisions` | `core/views_agent_learning.py:1657` | — |
| POST | `/api/boardroom/decisions/<uuid>/promote/` | `promote_decision` | `core/views_agent_learning.py:2103` | — |
| POST | `/api/boardroom/decisions/<uuid>/reject/` | `reject_decision` | `core/views_agent_learning.py` | — |
| GET | `/api/boardroom/decisions/prioritized/` | `get_prioritized_decisions` | `core/urls.py:3458` | — |
| POST | `/api/cockpit/approvals/decision/<str>/decide/` | `cockpit_approve_decision` | `core/urls.py:1726` | — |
| POST | `/api/cockpit/approvals/gate/<str>/decide/` | `cockpit_approve_gate` | `core/urls.py:1727` | — |
| GET | `/api/boardroom/governance-stats/` | `get_governance_stats` | `core/urls.py:3464` | — |
| GET | `/api/decisions/<uuid>/` | `get_decision_detail` | `core/urls.py:2222` | — |
| POST | `/api/time-travel/decision/` | `record_decision` | `core/urls.py:3587` | — |
| GET | `/api/platform/governance/` | `governance_view` | `core/urls.py:4551` | — |

**PA-path slice (partial enumeration — 10 representative):**

| Method | Path | View | File:Line | @extend_schema? |
|---|---|---|---|---|
| POST | `/api/pa/chat/` | `unified_pa_chat` | `core/views_personal_assistant.py:267` | — |
| GET | `/api/pa/chat/status/<str:task_id>/` | `pa_chat_status` | `core/urls.py:2509` | — |
| GET | `/api/pa/context/` | `unified_pa_context` | `core/views_personal_assistant.py:832` | — |
| POST | `/api/assistant/chat/` (compat) | `assistant_chat_bypass` | `core/urls.py:2490` | — |
| GET | `/api/assistant/context/` | `get_assistant_context` | `core/urls.py:2495` | — |
| GET | `/api/assistant/preferences/` | `get_user_preferences_api` | `core/urls.py:2494` | — |
| POST | `/api/assistant/voice/` | `voice_to_assistant` | `core/urls.py:2492` | — |
| GET | `/api/assistant/learning/` | `get_learning_summary` | `core/urls.py:2496` | — |
| GET | `/api/v1/assistant/context/` (compat) | `assistant_context` | `core/urls.py:2485` | — |
| POST | `/api/assistant/attention/unified/` | `get_unified_attention` | `core/urls.py:2505` | — |

**Cat A boundary observation:** **0 of 30 sampled endpoints across
all three paths have `@extend_schema` decoration** — money-path,
governance-path, PA-path all inhabit the 1,857-of-1,873 undecorated
denominator. The 16 `@extend_schema`-decorated endpoints in
`sports/views.py` do not overlap with the scoped slice.

### 6.1.1 Repeatable Measurement Harness — Spec Only (Non-Implementation)

**Rigby SIGN cycle 1 batch 2 Q6 fold — explicit harness spec added
to keep AC #7 spec-only guardrail intact + preempt de-facto-shipped-
artifact drift.**

Cat A boundary posture: the endpoint enumeration in §6.1 is
necessary but not sufficient to satisfy AC #7 "measurement _spec_
(commands + report schema + acceptance thresholds), not a shipped
script or CI job in this arc" (Rigby SIGN cycle 1 Q3-1 parent
scoping fold). §6.1.1 declares harness intent without shipping.

- **Inputs:**
  - Codebase at a given commit SHA (e.g., HEAD `77564f76` at S2501
    close).
  - Endpoint slice manifest source (§6.1 table + future extensions).
  - Optional: pgspider inventory freshness anchor
    (PLATFORM_INVENTORY.md `path()` count).
- **Proposed commands (examples, non-binding — Cat A does NOT
  commit to specific tooling per §7 anti-scope #7):**
  - `python manage.py show_urls` OR grep-based URL discovery
    (`grep -c "^\s*path(" core/urls*.py sports/urls.py`) for route
    enumeration.
  - `ripgrep` patterns for `@extend_schema`, `permission_classes`,
    `Response(`, `APIResponseEnvelope`, `status=401`,
    `JsonResponse(`.
- **Report schema (JSON / CSV columns — spec-level only):**
  - Aggregate counts: `@extend_schema` coverage / permission-floor
    declaration coverage / typed-response coverage / typed-error
    coverage / raw-fetch bypass counts.
  - Per-endpoint rows: method / path / view / file:line /
    `@extend_schema?` / `permission_classes?` / response-shape
    classification.
- **Acceptance thresholds:** **NONE in Cat A** (explicitly deferred
  to S2599 xx99 close or later verdict per S2500 §6 P-1 parked item
  + Rigby SIGN cycle 1 Q3-2 fold at parent scoping).
- **Non-goal:** no CI job, no committed script in this arc, no
  post-arc T-slot binding. Harness implementation deferred to a
  post-arc ADR or Group 2500 code-arc T-slot per S2500 §7 anti-
  scope discipline. Cat A ships the spec; Chris-D-verdict on
  implementation posture at S2599 xx99 close.

### 6.2 Custom API contract-adjacent surfaces

Per Explore Agent 3 verifier-cross-check at HEAD:

| Endpoint | View | File:Line | Cat A observation |
|---|---|---|---|
| `/api/bpaas/schema/` | `bpaas_schema` | `core/urls.py:4891` (via `core/views_bpaas_api.py:22`) | Custom BUILD_PACKET_SCHEMA JSON return; NOT drf-spectacular. |
| `/api/conversation-contract/overview/` | `get_conversation_contract_overview` | `core/urls.py:3436` | Conversation-contract metadata; different SoT (PA-conversation-shape contract). |
| `/api/conversation-contract/<uuid>/` | `get_conversation_contract_detail` | `core/urls.py:3437` | Same PA-conversation contract layer. |
| `/api/deliberation/sessions/<uuid>/contracts/` | `deliberation_contracts` | `core/urls.py:1656` | Deliberation-session contract layer; content-pipeline scope. |

**Cat A boundary observation:** custom contract-adjacent endpoints
exist for domain-specific artifact contracts (build-packet /
conversation / deliberation) but there is **no unified API-contract-
SoT endpoint** analogous to `SpectacularAPIView` or a repo-wide
`/api/schema/` route. Cat A DECLARATION-boundary evidence: the
declaration surface is fragmented by artifact-type rather than
platform-wide.

## 7. Runtime Flows

**Playbook §9 canonical Q10-Q11 — What are the primary runtime flows
through the domain?**

### 7.1 Sports @extend_schema-decorated endpoint runtime flow (decorator INERT)

Representative endpoint: `LeagueViewSet.standings()` at
`sports/views.py:62-110`:

```
URL route:   GET /api/v1/sports/leagues/{id}/standings/
             (sports/urls.py:37 registers LeagueViewSet via DRF router)

Decorator:   @extend_schema(summary="Get league standings",
                            responses={200: LeagueStandingsSerializer})
             (sports/views.py:58-61)

View:        LeagueViewSet.standings() (sports/views.py:62-110)
             → self.get_object() → League ORM instance
             → league.teams.filter(...).order_by(...)
             → constructs standings_data dict (line 72-84)
             → constructs response_data dict (line 102+)

Serializer:  LeagueStandingsSerializer DEFINED at
             sports/serializers.py:18-43 but INVOKED at runtime
             ONLY implicitly via bare Response(response_data)
             — NOT `LeagueStandingsSerializer(response_data).data`
             (line 102+).

Response:    return Response(response_data) — bare dict, NOT
             serializer-serialized, NOT drf-spectacular-schema-
             validated at runtime.

Schema generation: @extend_schema metadata is IGNORED at runtime
                   → No schema introspection occurs
                   → No OpenAPI entry generated
                   → Metadata survives in Python AST but never
                     reaches OpenAPI engine (drf_spectacular
                     app is not in INSTALLED_APPS).
```

**Cat A boundary observation:** even at the sole `@extend_schema`-
decorated surface, the DECORATOR IS INERT for two orthogonal reasons:
(1) drf-spectacular app is not registered, and (2) the view code
bypasses the declared serializer by returning a bare dict. Both
would need remediation for Path A retrofit design-prep. Cat A does
NOT recommend either remediation; Cat A records both as evidence
for Chris-D-verdict-request.

### 7.2 Core endpoint runtime flow (no schema declaration)

Representative endpoint: `chat_with_assistant()` at
`core/views_personal_assistant.py:31-100` (money-path/PA-path
adjacent — PA chat is CLAUDE.md canonical entry point):

```
URL route:   POST /api/pa/chat/
             (core/urls.py:2508 registers unified_pa_chat)

Decorators:  @csrf_exempt
             @api_view(['POST'])
             @permission_classes([IsAuthenticated])
             (core/views_personal_assistant.py:30-32)
             → NO @extend_schema

View:        chat_with_assistant(request) (line 33-99)
             → extracts request.data.message, context, generate_audio
             → routes through UnifiedPAEntrypoint (Session 932)
             → async_to_sync(pa.process_message)(...)
             → returns Response({'success': True, 'data': {...}})

Serializer:  NONE. Hand-constructed response dict.

Response:    return Response({'success': True, 'data': {...}})
             — bare dict, no schema metadata.

Schema generation: NONE. Endpoint undocumented in any OpenAPI.
```

**Cat A boundary observation:** the CLAUDE.md canonical PA entry
point (`/api/pa/chat/`) has zero contract SoT declaration at HEAD.
This is directly relevant to Group 2600 PA T3 cross-arc handoff:
Group 2600 will inherit the "PA endpoint contract SoT-ABSENT"
evidence from Cat A boundary. Cat A does NOT recommend a PA-
endpoint retrofit — that's Group 2600's scope.

### 7.3 401 response emission runtime flow (three co-existing shapes)

Per parent-Claude verifier-corrected finding:

**Path (a) — DRF-default 401 emission (implicit-inheritance
dominant):**
```
Request without auth token → DRF APIView.dispatch()
→ authenticate() runs 2 custom classes (MobileTokenAuth +
  CsrfExemptSessionAuth)
→ if no user resolved → check_permissions()
→ IsAuthenticated.has_permission() returns False
→ DRF exception_handler (default; no override at
  core/settings.py:645-669)
→ Response body: {"detail": "Authentication credentials were not
  provided."}
```

**Path (b) — `APIResponseEnvelope.error()` 401 emission (9 hand-
invoked sites minority):**
```
Request → view function
→ view logic detects auth-adjacent condition
→ return APIResponseEnvelope.error(
    message="...",
    error_code="...",
    status_code=401
  )
→ Response body: {"success": false, "error": {"code",
  "message", "details"}}
```

**Path (c) — bare DRF `Response({...}, status=401)` (~59 sites):**
```
Request → view function
→ view logic detects auth-adjacent condition
→ return Response({"message": "...", ...}, status=401)
  or similar hand-constructed shape
→ Response body: heterogeneous ad-hoc dict (varies per view; goes
  through DRF renderer)
```

**Path (d) — non-DRF Django `JsonResponse({...}, status=401)`
(~93 sites; Rigby SIGN cycle 1 batch 2 Q7 STRENGTHEN verifier-loop
finding):**
```
Request → function-based view (or view-adjacent helper)
→ view logic detects auth-adjacent condition
→ return JsonResponse(
    {'success': False, 'error': 'Authentication required'},
    status=401
  )
→ Response body: {"success": false, "error": "<string>"}
  — error as STRING (not dict like APIResponseEnvelope)
  — bypasses DRF renderer entirely
```

Sample sites: `core/views_deploy.py:21,79`;
`core/views_video.py:1898,2108,2345,2594,2838,3115`. This is a
fourth 401 shape family, discovered at Cat A verifier-loop
(strengthened from §14.6 F6 v0 three-shape framing).

**Cat A boundary evidence:** **FOUR co-existing 401 shapes at
HEAD** (verifier-corrected from v0 three-shapes framing at Rigby
SIGN cycle 1 batch 2 Q7 STRENGTHEN):
- (a) DRF default `{"detail": "..."}` — implicit-inheritance
  ~80-90% dominant;
- (b) `APIResponseEnvelope.error()` — 9 sites — dict error with
  `code` / `message` / `details`;
- (c) bare DRF `Response({...}, status=401)` — ~59 sites — ad-hoc
  DRF-rendered dict;
- (d) non-DRF `JsonResponse({'success': False, 'error':
  '<string>'}, status=401)` — 93 sites — bypass-DRF envelope with
  string error.

This is Chris-D-verdict-input for Cat C α/β/γ (typed-error-envelope
message/UX policy nested in Cat D mechanism γ per S2404 Rigby Q6
fold). Cat A does NOT recommend shape unification; Cat A records
the current state.

**Exhaustiveness note (Rigby SIGN cycle 1 batch 2 Q7 STRENGTHEN
fold):** This section covers observed 401 response-body shapes in
Django + DRF view execution paths. Cat A additionally checked for
(a) middleware-short-circuit 401 responses at
`UnifiedTokenAuthenticationMiddleware` in `core/auth_middleware.py`
(finding: line 884 `JsonResponse` return is a 429 rate-limit, NOT
a 401 — no middleware 401 short-circuit body observed at HEAD); (b)
non-DRF Django view 401 responses (finding: 93 sites, path (d)
above); (c) `ValidationError` + `401` proximity in exception-
handler remaps (finding: 1 match at `content/providers/base.py:271`
in provider layer, not a DRF 401 shape — provider-side exception
catch, not response-body shape). Result: no additional 401 shape
families unaccounted for beyond (a)-(d).

## 8. Data Ownership and Lifecycle

**Playbook §9 canonical Q12-Q13 — Who owns the data + what is its
lifecycle?**

**Cat A boundary: contract-DECLARATION artifact ownership + lifecycle
of contract declarations, not domain data model ownership.**

- **`SPECTACULAR_SETTINGS` block ownership:** Not explicitly
  assigned in CODEOWNERS. Falls to default `* @clwest`. Lifecycle:
  SPECTACULAR_SETTINGS was added to `core/settings.py` at some
  prior session (git blame candidate — Cat A does not enumerate;
  historical provenance not load-bearing for the design-prep
  question).
- **`@extend_schema` decorator ownership in `sports/views.py`:** Not
  explicitly listed in CODEOWNERS. Falls to default `* @clwest`.
  Lifecycle: 16 decorators applied incrementally per S2203 §14.6 F5
  historical provenance (not re-verified at S2501).
- **`APIResponseEnvelope` ownership (`core/api_responses.py`):**
  EXPLICITLY listed in CODEOWNERS as `/core/api_responses.py
  @clwest` per S2499 Group 2400 Auth arc AU-D5 close.
- **DRF Serializer ownership across 96 subclasses:** Not explicitly
  listed for `sports/serializers.py`, `core/serializers_agents.py`,
  `content/serializers.py`. Fall to default `* @clwest`.

**Cat A boundary observation:** contract-DECLARATION artifact
ownership is centralized to `@clwest` via default rule at HEAD; only
the `APIResponseEnvelope` service is explicitly ownership-declared
(as fallout from Group 2400 Auth AU-D5). This is a Cat A boundary
data point for future maintainer-decision batch: if API-contract
maintainers diversify beyond sole operator, contract-DECLARATION
ownership needs explicit assignment at file-precision (see §18
Ownership Gaps).

**Provenance policy (Rigby SIGN cycle 1 batch 2 Q8 fold — explicit
policy tightening):** Provenance is collected only when it changes
present-day ownership/intent (e.g., experimental vs programmatic
adoption). Otherwise, provenance is explicitly out-of-scope for
Cat A. The two highest-signal provenance pointers Cat A leaves for
xx99 close consideration (lightweight, not a blame census): (i) the
SPECTACULAR_SETTINGS introduction session/commit (if easily
identifiable via git blame or handoff cross-reference); (ii) the
first `@extend_schema` introduction session/commit in
`sports/views.py`. Cat A does NOT enumerate these at HEAD; xx99
close may choose to collect them if Chris-D-verdict on the "is
sports drf-spectacular a one-off experiment or platform program?"
question requires this evidence.

## 9. Integrations With Other Domains

**Playbook §9 canonical Q14 + Q17-Q18 + Q21-Q22 — What are the domain
integrations + boundaries?**

**Table format per playbook §11.2 §9 requirement.**

| Adjacent Domain | Cat A Boundary Integration Point | File:Line | Cross-arc coordination |
|---|---|---|---|
| Group 2400 Auth (S2402 CF-B1 per-endpoint permission registry) | `permission_classes` DRF attribute declaration at view-level = DECLARATION side of the registry Cat D (S2504) formalizes as REGISTRY side | `core/settings.py:652-653` (default IsAuth) + `sports/views.py:48,258` (explicit AllowAny examples) + `persistence/views.py:50,111,297,510,619,665,702` (explicit IsAuth examples) | Cat A boundary evidence → Cat D S2504 owner |
| Group 2400 Auth (S2404 CF-D1 typed-error-envelope Cat D α/β/γ) | 401 response body DECLARATION at Cat A boundary (three co-existing shapes per §7.3); Cat D S2504 formalizes mechanism (γ = RQ error callback + top-level ErrorBoundary per S2404 Rigby Q6 fold) | `core/api_responses.py:53-98` (envelope shape) + `core/settings.py:645-669` (no EXCEPTION_HANDLER override) | Cat A boundary evidence → Cat C S2503 (message/UX policy nested inside envelope γ) + Cat D S2504 (mechanism) |
| Group 2200 Frontend (S2203 §20.6 Path A/B/C triad — REST-native contract-strictness axis) | Backend contract-DECLARATION density: 16-of-1,873 decorator adoption + 16.2% ModelSerializer coverage + 3 co-existing 401 shapes = evidence density for Chris-D-verdict on Path A vs B vs C | Aggregate across `sports/views.py` + 96 serializers + 161 401 emission sites | Cat A collects evidence — verdict deferred to S2599 xx99 Chris-D-verdict-request |
| Group 2200 Frontend (S2203 §14.1 F1 SoT-ABSENT) | Backend-side SoT-ABSENT = Cat A boundary confirms F1 at HEAD with deeper evidence than S2203 measured (app-registration + URL-routing gaps beyond decorator-partial-wiring) | `core/settings.py:161-215` (INSTALLED_APPS lacks drf_spectacular) + `core/urls.py:4891` (only bpaas_schema custom route) | Cat A extends S2203 F1 evidence |
| Group 2600 PA (workspace-context authz at API layer) | `/api/pa/chat/` + `/api/assistant/*` endpoints declare no contract SoT; workspace-context authz declared implicitly via `permission_classes = [IsAuthenticated]` at `core/views_personal_assistant.py:32` | `core/views_personal_assistant.py:31-99` (PA chat endpoint = 0 @extend_schema) + `core/views_workspace_api.py` (workspace endpoints = 0 @extend_schema) | Cat A boundary evidence → Group 2600 PA T3 handoff |
| Group 1700 Observability (silent-401 rate telemetry + envelope enforcement locus) | 161 direct 401 emission sites at HEAD; instrumentation for rate/frequency telemetry absent; envelope-enforcement locus decision joins Group 1700 authority-provenance decision | `core/settings.py:645-669` (no `EXCEPTION_HANDLER` override) + 161 grep-based emission-site count (not per-site instrumented) | Cat A boundary evidence → Group 1700 T4 handoff |
| Group 2300 Mobile (parallel API contract declaration boundary) | Backend contract SoT declared once (drf-spectacular schema output) would in principle serve both web + mobile consumers identically; at HEAD the SoT is not generated → mobile app cannot consume declared contract | See §3.1 — no schema generation at HEAD | Cat A boundary evidence → Group 2300 T5 handoff |
| Group 1600 Content (content-adjacent APIs) | Content endpoints (`ContentGenerationSerializer` + `DocumentSerializer` + `ContentTemplateSerializer`) declare via ModelSerializer but not via @extend_schema | `content/serializers.py:21-155` + `core/views_content*.py` | Adjacent; Cat A boundary observation only |
| Group 1900 Authority Enforcement (governance-path adjacent) | governance-path endpoints (`get_boardroom_decisions` etc.) declare via bare Response({}) dict returns | `core/views_agent_learning.py:1657,2103` + `core/urls.py:3458,3464,1726,1727,2222,3587,4551` | Adjacent; Cat A boundary observation only |
| Group 1500 Sports (demonstration-surface ownership; Rigby SIGN cycle 1 batch 2 Q9 fold — promoted from implicit to explicit integration row to prevent "Sports is only an example" drift) | Group 1500 Sports owns `sports/views.py` (16 `@extend_schema` decorators — the sole platform-wide demonstration of decorator adoption) + `sports/serializers.py` (~25 money-path Serializer classes); currently INERT at HEAD due to drf-spectacular disconnect but is the live integration dependency for any Path A / B / C future retrofit; Cat A boundary: Group 1500's decorator pattern is proof-of-adoption but NOT a Cat A recommendation to canonize | `sports/views.py:58,117,164,344,357,385,500,568,744,848,887,907,924,953,987,1023` + `sports/serializers.py:18-598` | Group 1500 as future canonical pilot surface if Path A/B/C ratified — Chris-D-verdict-request at S2599 xx99 close |
| Group 1300 Memory / KB / RAG (Rigby SIGN cycle 1 batch 2 Q9 conditional row) | If consumer-facing REST endpoints for retrieval / ingest / semantic-search exist as URL routes (kb_ingest, semantic_search, embed_documents), those are Cat A boundary integration; if tool-only via PA gateway, adjacency is preserved but Cat A boundary is "tool-surface only" | Cat A does NOT enumerate at S2501; S2502 Cat B verifies REST-endpoint vs tool-only disposition at HEAD; deferred to S2502 for exhaustive REST-endpoint scope | Cat A boundary observation: adjacency preserved with disposition-pending flag |
| Group 2000+ Event/Integration Runtime (Celery-adjacent REST endpoints; Rigby SIGN cycle 1 batch 2 Q9 conditional row) | REST endpoints that submit async work and return `task_id` / `status` have distinct contract-SoT concerns (envelope shape for the task_id payload + error shape for enqueue failure + permission floor for async submission). Example: `/api/pa/chat/status/<str:task_id>/` at `core/urls.py:2509` returns task-completion payload | `core/urls.py:2509` (pa_chat_status) + adjacent Celery-status endpoints; count at HEAD: NOT enumerated at S2501 (Cat A boundary observation only) | Cat A boundary observation; Group 2000+ arc (if opened) may inherit T-slot |

**Cat A boundary discipline preservation (playbook §5 phase
discipline):** Cat A collects EVIDENCE at every integration surface;
Cat A does NOT recommend design outcomes; verdict resolution
deferred to owning arcs (Cat D S2504 for permission-floor +
typed-error-envelope; Cat C S2503 for message/UX policy; Group 2600
PA T3 for workspace-context authz; Group 1700 T4 for observability;
Group 2300 T5 for mobile parallel).

## 10. Event Flows

**Playbook §9 canonical Q19-Q20 — What are the primary event flows?**

**Cat A boundary observation:** the Backend API Contract SoT layer is
NOT event-driven at HEAD. `@extend_schema` decoration is compile-
time metadata; DRF Serializer instantiation is per-request runtime
serialization; APIResponseEnvelope invocation is per-view-call.
There are no signals, no Celery tasks, no channels-layer events
associated with contract-SoT declaration or enforcement.

**One adjacent event flow (Cat A boundary observation only):**

- `core/services/tool_dispatcher.py:1265` — PA-tool-schema
  live-reload handler. When PA tool schema files change, tool-
  dispatcher re-registers tool handlers. **This is a PA-tool schema
  registry event flow, NOT an API-contract SoT event flow.** Cat A
  boundary distinguishes tool-schema (PA-internal) from API-contract-
  schema (external consumer-facing).

**§10 gap acknowledgment:** Cat A boundary does not surface event
flows because none exist at contract-SoT level at HEAD.

**Event adjacency scan (Rigby SIGN cycle 1 batch 2 Q10 STRENGTHEN
fold — brief adjacency inventory to avoid argument-by-omission):**

1. **`verify_doc_claims` doc drift verification** — Cat A verified
   at HEAD: the command exists (`core/management/commands/
   verify_doc_claims.py`) but Cat A did not confirm whether it is
   Celery-scheduled. If scheduled, it is a **doc / claims
   verification event loop**, not an API contract SoT event loop —
   adjacent but not integrated.
2. **drf-spectacular schema-generation triggers** — schema
   generation via `SpectacularAPIView` route (if wired) OR
   `python manage.py spectacular` (if command registered) is
   **on-demand, NOT signal-driven**. Both entry points are
   disconnected at HEAD (per §3.1). No post-decoration signals
   trigger schema regen.
3. **PA-tool-schema live-reload** (`core/services/tool_dispatcher.
   py:1265`) — PA-tool schema reload signal; adjacent to contract-
   SoT layer only as pattern analogue (per §5.5 boundary note);
   NOT an API contract SoT event.

**Neutrality guard (Rigby SIGN cycle 1 batch 2 Q10 STRENGTHEN
fold):** absence of contract-SoT events at HEAD is **evidence
about operationalization, NOT a verdict on ternary seam (i) / (ii)
/ (iii)**. An eventful contract-SoT layer would have signals for
"decoration-added" / "serializer-schema-updated" / "endpoint-
registered-without-decoration"; at HEAD zero such signals exist.
This is a Cat A boundary observation about the OPERATIONAL state,
not a Cat A verdict on the DECLARATION state.

## 11. Existing Documentation

**Playbook §9 canonical Q10 — What documentation exists on the
domain?**

Predecessor documentation Cat A consumed:

| Predecessor Doc | Cat A-Relevant Sections | State |
|---|---|---|
| `docs/research/domains/api/2500_api_domain_scoping.md` | §3.A Cat A mission (lines 675-724) + §6 P-1 to P-11 parked items + §5 child mission sequence + §7 anti-scope (8 items) + §8 decisions | primary predecessor — S2500 parent scoping |
| `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` | §14.1 F1 SoT-ABSENT + §14.6 F5 drf-spectacular installed but wired only in sports + §14.3 F3 silent-401 SYSTEMIC + §19.1 R1 whole-platform contract SoT rollout + §20.6 POSTURE-DECISION evidence plan | KEY VERIFIER FINDING F5 extended at S2501 §14.6 |
| `docs/research/domains/frontend/2299_frontend_canonical_summary.md` | §5.1 canonical seam "declared-but-unenforced contracts" + §8.2 T2 Group 2500 API cross-arc handoff bundle + §8.3 R6 error-boundary framework BLOCKING PREREQUISITE + §5.4 Cross-arc coordination flag #2 | 2299 T2 handoff = load-bearing Cat A input |
| `docs/research/domains/auth/2499_auth_canonical_summary.md` | 7 CF-*1 cross-arc flags to Group 2500 (CF-D1 typed-error-envelope Cat D α/β/γ + CF-D2 F-D-CALL-1 803 consumer + CF-D3 F-D-BYPASS-1 79 raw fetch + CF-B1 per-endpoint permission registry + CF-B3 STAFF_REQUIRED_PATHS PHANTOM + CF-B4 auth_views_enhanced.py stacking + CF-C1 F-C-REFRESH-1 refresh + CF-C2 F-C-CSD-1 Clear-Site-Data + CF-C3 F-C-STORE-1 storageKeys) | 2499 T2 handoff = load-bearing Cat A input; §9 boundary integrations mapped |
| `docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` | §14.5 21-loci permission-floor rate + §19.1 (a)/(b)/(c) three-option Cat B PRIMARY (c) LONG-TERM GOVERNANCE | Cat A DECLARATION-side of Cat B registry-side |
| `docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md` | §14.5 803 consumer classification + §19.1 α/β/γ × 2 typed-error-envelope Cat D CF-D1 | Cat A DECLARATION-boundary of Cat D mechanism-side |
| `docs/research/platform_architecture_inventory.md` §3.22 API Layer | Row 22 STABLE + MODERATE at line 232 table + full row at line 1648 (1,857 URL patterns / 208 view files / ~51 WebSocket consumers / Fleet signature auth) | **§3.22 EXISTS** — parent scoping §2.2 said "§3.30 TBD" but §3.30 is Body Systems (verifier-corrected) |
| `docs/PLATFORM_INVENTORY.md` | Runtime inventory: 1,864 path() patterns; 209 core/views*.py files; 199 mgmt commands; 585 concrete models | **9-pattern URL drift** + **22-model drift** at HEAD vs verifier count |
| `docs/PLATFORM_WHAT_IT_IS.md` | Narrative anchor; NO §API narrative subsection at HEAD | Cat A P1 output candidate: propose §API subsection add at S2599 xx99 close |
| `docs/topics/*.md` | NO `docs/topics/api.md` at HEAD | S2500 §9 defers `docs/topics/api.md` CREATE to S2599 xx99 if load-bearing |
| `docs/research/domains/api/2500_api_domain_scoping.md` §3.5 API-adjacent probes disposition table (Rigby SIGN cycle 1 batch 3 Q11 fold — explicit predecessor row for parent's "what was checked / what was deferred" map) | 12 API-adjacent probes (OpenAPI 3.0 vs 3.1 fork / typed-client codegen framework / gRPC-GraphQL-tRPC / API versioning / rate limiting / CORS / idempotency / pagination / caching+ETag / WS protocol / WS auth handshake / API telemetry) with per-probe disposition (IN-SCOPE / NON-CANDIDATE / CROSS-ARC FLAG) | Cat A honors §3.5 dispositions throughout this audit — no probe outside the disposition table is elevated at S2501 |
| `docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` §14.5 21-loci methodology (Rigby SIGN cycle 1 batch 3 Q11 fold — methodology provenance not just finding) | Structured locus-scanning methodology: 21 permission-floor loci (routes + middleware + view-decorators + serializers + etc.) traced end-to-end to produce ~80-90% implicit-inheritance rate estimate | Cat A uses adjacent locus-scanning method for @extend_schema decoration coverage baseline; methodology-provenance cited to preempt "why this coverage lens?" question at xx99 |
| Session 1099 `verify_doc_claims` doc-drift infrastructure (Rigby SIGN cycle 1 batch 3 Q11 fold — provenance for drift-verifier infrastructure gap in §5.2) | No dedicated Session 1099 doc found in `docs/handoffs/` search at S2501 time (Cat A recorded: "predecessor doc not identified; only code-level adjacency exists at `core/services/doc_claim_verification.py` + `core/management/commands/verify_doc_claims.py`") | Cat A frames drift-verifier infrastructure gap in §5.2 grounded in the code-level adjacency, not invented at S2501 |

**Cat A documentation gap observations:**
1. No `docs/topics/api.md` analog to `docs/topics/auth.md` (shipped
   at S2499 close per AU-D2 + AU-D7 fold). S2500 §6 P-2 parked
   `docs/topics/api.md` CREATE to S2599 xx99 close if load-bearing.
2. No `PLATFORM_INVENTORY §API` autoblock analog to `§Auth` (shipped
   at S2499 close). S2500 §6 P-1 parked as Cat A P1 output candidate
   (proposal-only per Rigby SIGN cycle 1 Q3-2 fold — implementation
   deferred to post-arc ADR or Group 2500 code-arc T-slot).
3. No `PLATFORM_WHAT_IT_IS §API` narrative subsection.

## 12. Research Coverage

**Playbook §9 canonical Q11 — What research exists on this domain?**

**Classification per playbook §12: LIGHT-to-MODERATE** (candidate;
Chris-D-verdict at S2599 xx99 close).

**Rationale:** Prior arcs (S2203, S2402, S2404) have measured the
frontend-side + permission-side + silent-401-side of the API
contract boundary. No dedicated backend-side contract SoT audit
exists prior to S2501. The S2500 parent scoping + this S2501 Cat A
audit together are the first backend-contract-SoT-focused research;
prior work is boundary-adjacent (frontend consumers describe the
gap; permission-floor audit describes the enforcement inconsistency;
silent-401 audit describes the runtime symptom).

- **NONE — insufficient?** No — S2203 §14.6 F5 named the drf-
  spectacular partial-wiring gap explicitly (which S2501 §14.6
  extends with deeper evidence).
- **LIGHT — plausible.** Multiple audits reference the gap; no
  dedicated backend contract-SoT audit exists at HEAD until S2501
  itself.
- **MODERATE — supportable.** S2203 §14.6 + S2299 §5.1 + S2402
  §14.5 + S2404 §14.5 + S2500 §3.A + this S2501 audit together form
  a coherent multi-arc research foundation; the 32-domain map §3.22
  API Layer row exists at STABLE + MODERATE per platform_
  architecture_inventory.md.
- **DEEP — premature.** DEEP requires multiple focused docs, audits,
  or research docs on the backend contract SoT layer specifically.
  S2501 is the first such focused doc.
- **CANONICAL — premature.** CANONICAL requires clear source-of-
  truth docs actively maintained. `docs/topics/api.md` does not
  exist at HEAD; PLATFORM_INVENTORY §API autoblock does not exist.

**Cat A recommendation to xx99 (verdict-neutral):** cite S2501 as
first focused backend-contract-SoT research; classification landing
zone LIGHT-to-MODERATE candidate; final classification deferred to
S2599 xx99 close after all 4 children contribute evidence. **Cat A
does not select LIGHT vs MODERATE at this stage; xx99 closes
classification** (Rigby SIGN cycle 1 batch 3 Q12 optional micro-
guard fold — makes deferral explicit against any leak of "leans
moderate" interpretation).

## 13. Architecture Maturity

**Playbook §12 classification: PARTIAL** (candidate;
Chris-D-verdict at S2599 xx99 close).

**Rationale:**
- **EXPERIMENTAL** — insufficient; the layer is used (16 decorators
  applied + 96 Serializer classes shipping) so not purely prototype.
- **PARTIAL** — best-fit. Infrastructure exists (config + pip +
  decorators + Serializer classes + APIResponseEnvelope service +
  custom bpaas_schema endpoint) but is unevenly wired (drf-
  spectacular app not registered + no URL route + 0.85% decoration
  rate + 16.2% ModelSerializer coverage + 3 co-existing 401 shapes).
  Cat A boundary evidence directly supports PARTIAL: "works in
  places but not cohesive or fully wired" (playbook §12
  definition).
- **WORKING** — arguable but premature. WORKING requires "operational,
  used, but with gaps or drift." At HEAD the contract SoT is
  operationally NOT-CONNECTED (drf-spectacular app disconnect) —
  gaps are structural, not operational drift.
- **STABLE / CANONICAL** — clearly premature.

**Cat A boundary observation:** at 32-domain-map level, §3.22 API
Layer is documented as STABLE + MODERATE (line 232 + line 1648).
The §3.22 posture is a HIGHER-LEVEL rollup (REST + WebSocket URL
patterns + view files + WebSocket consumers + Fleet signature
auth). Cat A's PARTIAL verdict is at the CONTRACT-SoT-DECLARATION
sub-layer specifically. These are consistent: the API Layer exists
+ works + is used (STABLE), while the Contract SoT DECLARATION sub-
layer within it is PARTIAL. **S2599 xx99 close is expected to
preserve §3.22 API Layer STABLE + MODERATE; it may optionally add a
sub-row / note for the Contract SoT DECLARATION sub-layer as
PARTIAL** (Rigby SIGN cycle 1 batch 3 Q13 fold — modality
tightened from "should preserve...adding" to "expected to
preserve...may optionally add" to preserve Cat A design-prep
boundary discipline; Cat A does NOT direct architecture-inventory
revision).

## 14. Known Drift

**Playbook §9 canonical Q26 — What drift exists between docs and
runtime?**

### 14.1 F1 — S2203 §14.1 F1 SoT-ABSENT RE-VERIFIED at HEAD (with deeper evidence)

**Predecessor claim (S2203 §14.1 F1):** "Backend API contract
source-of-truth absent. drf-spectacular infrastructure installed but
wired ONLY in sports/views.py (16 decorators)."

**S2501 verifier at HEAD `77564f76`:**
- `drf-spectacular==0.28.0` INSTALLED via pip — verified (`import
  drf_spectacular` succeeds).
- `SPECTACULAR_SETTINGS = {...}` defined at
  `core/settings.py:1600-1605` — verified (4 keys).
- **`drf_spectacular` NOT in INSTALLED_APPS** — verified against
  `core/settings.py:161-215` (54 apps listed; drf_spectacular absent).
- **NO `SpectacularAPIView` URL route registered** — verified via
  grep `SpectacularAPIView|schema/` across `core/urls*.py`; only
  `path('api/bpaas/schema/', bpaas_schema, name='bpaas-schema')`
  at `core/urls.py:4891` (CUSTOM, not drf-spectacular).
- **`python manage.py spectacular` returns "Unknown command"** —
  verified 2026-07-05.
- 16 `@extend_schema` in `sports/views.py` — verified (lines 58,
  117, 164, 344, 357, 385, 500, 568, 744, 848, 887, 907, 924, 953,
  987, 1023).
- 0 `@extend_schema` in `core/*.py` — verified (grep across 209
  view files).

**S2501 extension of F1 evidence:** the state at HEAD is stronger
negative than S2203 measured. S2203 §14.6 F5 characterized as
"INSTALLED-PARTIAL-WIRED"; S2501 verifier confirms **INSTALLED +
CONFIGURED + PARTIALLY-DECORATED + FULLY-DISCONNECTED**. Even the 16
`@extend_schema` decorators in `sports/views.py` do not produce
runtime schema output because the schema-generator app is not
registered.

**Severity (Cat A DECLARATION-boundary):** HIGH baseline; CRITICAL
for money-path + governance-path + PA-path endpoints where
consumers must infer contract shape at runtime.

**Class:** `technical_debt` (structural — infrastructure installed
but disconnected) + `missing_connection` (declared-in-settings +
declared-via-decorators but not-installed-as-app).

**Cat A boundary observation:** S2501 resolves S2299 §6 UNKNOWN 5
(drf-spectacular schema.yaml generation feasibility) with **NEGATIVE
outcome**. Path A retrofit design-prep at S2501 (and continuing
through S2504 + S2599 xx99) must account for the app-registration +
URL-routing prerequisite alongside decorator extension.

### 14.2 F2 — URL pattern count drift (9-pattern drift; observation)

**PLATFORM_INVENTORY.md claim (Git HEAD `e617af59`, 2026-07-05
15:51:41):** 1,864 `path()` patterns across all `core/urls*.py`
files.

**S2501 verifier at HEAD `77564f76` (post-parent-scoping-merge):**
1,873 total URL patterns (1,871 `path()` across 5 files + 2
`re_path()` in core/urls.py).

**Delta:** +9 patterns (0.48% drift). Likely due to parent scoping
merge PR #2920 adding no runtime URLs (docs-only) but PLATFORM_
INVENTORY not yet regenerated between S2500 parent scoping + S2501
open.

**Class:** `observation` (inventory-freshness drift, not runtime
drift). Severity: LOW. Recorded here for xx99 cross-reference; no
fix needed until PLATFORM_INVENTORY regenerated post-arc via
`generate_platform_inventory` command.

### 14.3 F3 — Model count drift (22-model drift; observation)

**PLATFORM_INVENTORY.md claim:** 585 concrete Django models across
23 apps.

**S2501 verifier:** 563 concrete models via grep `^class \w+\(.*
models\.Model` (excluding abstract mixins).

**Delta:** 22-model drift. Likely due to grep-based method excluding
abstract mixins that PLATFORM_INVENTORY's Python-based introspection
includes. Not a Cat A finding; Cat A records for cross-reference.

**Class:** `observation` (methodology delta, not runtime drift).
Severity: LOW.

### 14.4 F4 — §3.22 API Layer row EXISTS (parent scoping §2.2 imprecision resolved)

**Parent scoping claim (S2500 §2.2, lines 476-483):** "Row 30 API
layer (or equivalent) — TBD baseline — Cat A P1 re-verifies whether
§3.30 exists as authored or requires synthesis at S2501 open."

**S2501 verifier at HEAD:** `platform_architecture_inventory.md`
§3.30 is Body Systems + BodyCoordinator (line 2222). The **API
Layer row is §3.22** at line 1648, table row 232 with posture
**STABLE + MODERATE** (1,857 URL patterns / 208 view files / ~51
WebSocket consumers / Fleet signature auth).

**Class:** `observation` (parent-scoping-doc imprecision, not
runtime drift). Severity: LOW. Cat A resolves as positive: §3.22
API Layer row EXISTS + is posture-labeled + is inventory-current.
S2599 xx99 anchor-update recommendation should REVISE (not CREATE)
the §3.22 row with Cat A + Cat B + Cat C + Cat D evidence at close.

### 14.5 F5 — S2203 §14.6 F5 EXTENDED at S2501 (KEY VERIFIER FINDING)

Per §14.1 F1 above, S2203 §14.6 F5 (drf-spectacular INSTALLED but
wired ONLY in sports/views.py) is EXTENDED at S2501 with the deeper
evidence of INSTALLED_APPS absence + URL-routing absence + command-
recognition absence. This is a Cat A KEY VERIFIER FINDING:

**Refutation-would-look-like criteria (from S2500 parent scoping
Refutation-would-look-like block, Rigby SIGN cycle 1 Q4-1 fold —
4 criteria):**
1. `python manage.py spectacular --file schema.yaml` generates
   coherent OpenAPI 3.0 schema for money-path + governance-path +
   PA-path scoped slice. **REFUTED at HEAD** (Unknown command).
2. `core/*.py` endpoint declarations consistently @extend_schema-
   decorated across the slice. **REFUTED at HEAD** (0 decorators in
   core/*.py).
3. Typed client derivation aligns with runtime responses/errors at
   api.ts consumption points. **NOT MEASURABLE at HEAD** (no
   generated schema to derive from).
4. Per-endpoint permission-floor registry derivable from
   `permission_classes` declarations without ad-hoc
   STAFF_REQUIRED_PATHS augmentation. **PARTIALLY REFUTED at HEAD**
   (~80-90% implicit-inheritance per S2402 §14.5 F-B-CRIT-1 means
   registry cannot be derived from declarations alone; STAFF_
   REQUIRED_PATHS augmentation IS present per S2499 CF-B3).

**Cat A boundary count:** **3 of 4 refute** (criteria 1, 2, 4);
1 criterion NOT MEASURABLE. Per parent scoping §lens block: "≥3
refute → coherent spine holds"; **wait — the phrasing needs care.**
Actually rereading S2500 lens block: **"≥3 refute → coherent spine
holds; 0-1 refute → accretion holds; 2 refute → declared-but-uneven
middle."** But the criteria are stated as "Refutation would look
like" (i.e., what would demonstrate the coherent spine); so REFUTED
at HEAD means: the refutation criterion is NOT SATISFIED at HEAD =
NOT a refutation of the accretion hypothesis. **Cat A verifier-
loop note:** the parent scoping phrasing is subject to Q4-1
interpretation risk. The S2599 xx99 canonical summary should clarify
the direction of "refute" language before drawing arc verdict —
this is Cat A boundary evidence, not verdict. **This tally is not
a Cat A verdict**; it is a structured evidence snapshot whose
interpretation depends on the corrected refutation-direction
wording, finalized at S2599 xx99 (Rigby SIGN cycle 1 batch 3 Q14
fold — explicit non-verdict qualifier to close the "tally =
verdict" misread loophole).

### 14.6 F6 — FOUR co-existing 401 shapes at HEAD (NEW; verifier-loop-expanded from v0 three-shape framing)

**Cat A verifier-corrected finding (Rigby SIGN cycle 1 batch 2 Q7
STRENGTHEN expansion from v0 three-shape framing):** four co-
existing 401 response body shapes at HEAD `77564f76` —
- (a) DRF default `{"detail": "..."}` — dominant for permission-
  inherited endpoints (implicit-inheritance rate ~80-90% per S2402
  §14.5 F-B-CRIT-1);
- (b) `APIResponseEnvelope.error()` shape `{"success": false,
  "error": {"code","message","details"}}` — 9 hand-invoked sites at
  `core/api_responses.py:53-98` (minority);
- (c) bare DRF `Response({...}, status=401)` — ~59 sites; ad-hoc
  DRF-rendered dict; heterogeneous shape;
- (d) non-DRF Django `JsonResponse({"success": false, "error":
  "<string>"}, status=401)` — **93 sites** at HEAD (verified via
  grep `JsonResponse.*status.*401|HttpResponse.*status.*401`
  --include="*.py" | grep -v migrations = 93 matches; sample sites
  `core/views_deploy.py:21,79`, `core/views_video.py:1898,2108,
  2345,2594,2838,3115`); error as STRING (not dict); bypasses DRF
  renderer.

Total = 161 direct 401 emission sites at HEAD; 9 (b) + 93 (d) +
~59 (c) accounts for the total, with (a) as a fifth flow-path (DRF
default via exception-handler-chain when no view code intervenes;
non-additive to the 161 emission-site count because DRF-default
path emits via internal exception handler, not view-code
`status=401` return).

**Cat A boundary evidence (verifier-loop-strengthened):** this
heterogeneity is consistent with both arc-seam (ii) declared-but-
uneven contracts and (iii) implicit shape accretion; Cat A does
NOT assign weights (per Q1 fold verdict-neutrality discipline).
Cat C S2503 inherits this evidence for message/UX policy design-
prep; Cat D S2504 inherits for mechanism design-prep. **The
existence of shape family (d) — non-DRF JsonResponse pattern with
string error — is significant because it bypasses BOTH the DRF
exception handler AND the APIResponseEnvelope helper**, making
frontend typed-error-envelope work harder (frontend can't rely on
either DRF or APIResponseEnvelope shape uniformly).

**Classification (Rigby SIGN cycle 1 batch 1 Q5 fold — reframed from
severity-verb to impact-classification to preserve Cat A boundary
discipline; no remediation prescribed in Cat A):** contract
fragmentation; ownership unresolved (to be assigned in xx99
ownership map).

**Impact:** HIGH on contract observability / client predictability
(classification only; no remediation prescribed in Cat A). Blocks
Cat C α/β/γ + Cat D typed-error-envelope current-state measurement
because the current-state is not a single fact — it is a
distribution across four shape families.

## 15. Known Technical Debt

**Playbook §9 canonical Q23 — What technical debts exist?**

**Top-5 Cat A technical debt observations (ranked by contract-
observability impact; non-prescriptive)** — Rigby SIGN cycle 1
batch 3 Q15 fold (section header renamed from "top 5 load-bearing,
ranked" to explicit non-prescriptive labeling; §14.6 v0 three-shape
→ v1 four-shape finding does NOT trigger reorder because item 5 is
downstream symptom-layer while items 1-2 are SoT scaffolding
disconnect + scope magnitude):

1. **Half-wired drf-spectacular** — INSTALLED_APPS absent +
   SPECTACULAR_SETTINGS present + 16 decorators demonstrating
   pattern + no URL routes. Blocks code-generation toolchain
   downstream (frontend api.ts type-generation). File:line:
   `core/settings.py:1600-1605` + `core/settings.py:161-215` +
   `core/urls.py` (no SpectacularAPIView). Cat A boundary
   observation; remediation policy Chris-D-verdict at S2599 xx99.
2. **~1,857 undeclared endpoints** (1,873 total − 16 declared =
   1,857) as denominator for Cat A contract-DECLARATION measurement.
   No @extend_schema + no auto-discovery capability without
   serializer_class enforcement. **Evidence for Path A/B/C triad;
   NOT a recommendation to decorate all endpoints in this phase**
   (Rigby SIGN cycle 1 batch 3 Q15 fold — non-recommendation
   qualifier inside item to prevent misread as directive).
3. **`permission_classes` implicit inheritance** ~80-90% per S2402
   F-B-CRIT-1 + `core/settings.py:652-653` DEFAULT_PERMISSION_CLASSES
   IsAuthenticated. Contract surface undefined at view level; silent-
   401 risk inherited to Cat A boundary. File:line:
   `core/settings.py:652-653` + `sports/views.py:45-984` (LeagueViewSet
   line 45 no explicit permission_classes = inherits default). Cat
   A boundary observation; enforcement decision belongs to Cat D
   S2504.

   > **S2990 HEAD re-verify note (2026-07-27, HEAD `808c50603`).** Line
   > refs drifted: `DEFAULT_PERMISSION_CLASSES` is at `core/settings.py:737-738`.
   > `LeagueViewSet` example no longer applies at HEAD (`sports/views.py:48`
   > now declares `permission_classes = [permissions.AllowAny]`). Runtime
   > URL-resolver walk finds **19 of 818 DRF class-based views (2.3%)**
   > inheriting implicitly, not the estimated ~80-90%. Full coverage matrix
   > + cluster distribution + Cat D S2504 boundary framing collected at
   > `docs/research/domains/api/2990_permission_classes_implicit_inheritance_evidence_report.md`.
   > Original S2402/S2501 evidence preserved as historical artifact; addendum
   > added forward-pointing only, per S2990 Rigby SIGN cycle agreement.
4. **Bare `Response({...})` dict returns bypass ModelSerializer
   typing.** ~60% of sampled money-path endpoints per §4.3;
   generalized to entire API surface per §7.2 evidence. Cat A
   boundary observation; typing-adoption decision belongs to Cat
   B S2502 + Cat A future design-prep at S2599 xx99.
5. **Four co-existing 401 shapes at HEAD** per §14.6 F6 (verifier-
   loop-expanded from v0 three-shape framing at Rigby SIGN cycle 1
   batch 2 Q7 STRENGTHEN). **This is a symptom / fragmentation
   observation; remediation policy belongs to Cat C S2503 (message/
   UX policy) + Cat D S2504 (mechanism)** (Rigby SIGN cycle 1
   batch 3 Q15 fold — symptom-layer + downstream-ownership tag).

**Cat A boundary discipline preservation:** debts observed +
ranked by contract-observability impact; **NOT recommendation** at
any item. Chris-D-verdict-request at S2599 xx99 close after all 4
children contribute evidence.

## 16. Boundary Violations

**Playbook §9 canonical Q24 — What boundary violations exist?**

**Cat A boundary observation:** Cat A DOES NOT own boundary
violation classification — playbook §12 finding-type
`boundary_violation` requires evidence of a boundary that IS
declared and is being violated. At HEAD the contract-SoT boundary
is largely NOT DECLARED (per §14.1 F1 + §14.5 F5), so **for Cat A
purposes, "boundary violation" is usually a less useful frame than
"missing / undeclared contract surface" — Cat D may still classify
specific items as violations depending on enforcement mechanisms**
(Rigby SIGN cycle 1 batch 4 Q16 fold — de-scoping softened to
Cat-A-local scope without pre-judging Cat D S2504 taxonomy).

**Adjacent boundary violation candidates observed but not owned by
Cat A:**
- S2499 CF-B4 F-B-HIGH-4 `auth_views_enhanced.py` `@authentication_
  classes([])` + `[IsAuthenticated]` stacking across 4 files (auth-
  boundary violation) — S2504 Cat D findings-appendix per S2500 §3.D.
- S2499 CF-B3 F-B-HIGH-1 `STAFF_REQUIRED_PATHS` 2-of-3 PHANTOM
  entries (auth-boundary augmentation violation) — S2504 Cat D
  findings-appendix per S2500 §3.D.

Cat A boundary: NOT OWNED.

## 17. Duplicate or Overlapping Systems

**Playbook §9 canonical Q25 — What duplicate or overlapping systems
exist?**

**Cat A boundary observation:** two contract-DECLARATION substrates
overlap in scope but do not integrate at HEAD:

1. **drf-spectacular schema-generator app** (INSTALLED but not
   INSTALLED_APPS-registered; produces OpenAPI 3.0 spec via
   `@extend_schema` decorators) — dormant at HEAD.
2. **Custom `bpaas_schema` endpoint** (`core/urls.py:4891` →
   `core/views_bpaas_api.py:22` → returns
   `BUILD_PACKET_SCHEMA` JSON — build-packet-specific contract) —
   operational at HEAD.

**Overlap scope:** both are "schema-return endpoints" that expose
some contract shape to consumers. `bpaas_schema` is domain-scoped
(build-packet artifact contract); drf-spectacular would be
platform-scoped (all URL patterns). No integration between them at
HEAD; no evidence that either references the other.

**Class:** `duplicate_model` (loose) OR `unclear_owner` (which
schema-return endpoint owns which scope?). Severity: LOW — the two
serve non-overlapping needs at HEAD.

**Additional overlap: FOUR co-existing error / auth-failure response
substrates** (Rigby SIGN cycle 1 batch 4 Q17 fold — updated from v0
three-substrate framing to reflect §14.6 F6 v1 four-shape expansion
during Rigby SIGN cycle 1 batch 2 Q7 STRENGTHEN verifier-loop):

1. **DRF default exception handler family** — `{"detail": "..."}`
   shape via DRF's `rest_framework.views.exception_handler` for
   permission-inherited endpoints (implicit-inheritance ~80-90% per
   S2402 §14.5 F-B-CRIT-1). Sample locus:
   `core/settings.py:645-669` (no `EXCEPTION_HANDLER` override).
2. **`APIResponseEnvelope.error()` family** — `{"success": false,
   "error": {"code","message","details"}}` shape; 9 hand-invoked
   sites. Sample locus: `core/api_responses.py:53-98`.
3. **DRF bare `Response({...}, status=401)` dict family** — ~59
   sites; heterogeneous ad-hoc dict shapes; go through DRF
   renderer. Sample locus: cross-cutting across
   `core/views_*.py` + `sports/views.py`.
4. **Non-DRF `JsonResponse({"success": false, "error":
   "<string>"}, status=401)` string family** — 93 sites; bypass DRF
   renderer entirely. Sample loci: `core/views_deploy.py:21,79` +
   `core/views_video.py:1898,2108,2345,2594,2838,3115`.

Class: `duplicate_model` (four envelope shape families for the same
"auth failure" semantic; contract-SoT DECLARATION side
undifferentiated between them). Severity: Cat A boundary
observation only; remediation policy belongs to Cat C S2503 +
Cat D S2504 per §14.6 F6 downstream-ownership tag.

## 18. Ownership Gaps

**Playbook §9 canonical Q27 — What ownership gaps exist?**

CODEOWNERS AT HEAD (established S2499 Group 2400 Auth arc AU-D5 per
Cat D F-D-OWN-1 remediation):

- **Default:** `* @clwest` (sole operator).
- **Explicitly declared for Cat-A-adjacent surfaces:**
  - `/core/auth_middleware.py @clwest`
  - `/core/auth_views.py @clwest`
  - `/core/auth_views_enhanced.py @clwest`
  - `/core/api_responses.py @clwest` (APIResponseEnvelope service)
  - `/core/services/fleet_auth_drf.py @clwest`
  - `/core/vip_middleware.py @clwest`
  - `/core/models_vip_invite.py @clwest`
  - `/core/ws_auth_middleware.py @clwest`
  - `/frontend/src/lib/api.ts @clwest` (Cat B scope; Cat A boundary
    reference)
  - `/docs/research/ @clwest`

**UNASSIGNED at Cat A boundary (fall to default):**
- `/sports/views.py` (only `@extend_schema` demonstration surface —
  should Cat A recommend explicit ownership? NO, per Cat A boundary
  discipline. Chris-D-verdict-request at S2599 xx99 close.)
- `/core/views*.py` (209 view files, ~1,857 undecorated endpoints
  denominator).
- `/sports/serializers.py`, `/core/serializers_agents.py`,
  `/content/serializers.py` (96 Serializer subclasses).
- `core/settings.py` SPECTACULAR_SETTINGS block (contract-declaration
  substrate).
- `core/urls.py` schema route (custom bpaas_schema owner is
  UNDECLARED at file level; falls to default).

**Severity:** LOW at HEAD (sole-operator context per S2201 §14
rationale). Becomes MEDIUM at the moment a second contributor
joins. Cat A boundary: this is CODEOWNERS-batch T-slot maintainer-
decision material (Chris-D-verdict-request at S2599 xx99 close),
NOT a Cat A directive.

## 19. Future Research — Chris-D-verdict-request evidence (non-prescriptive)

**Playbook §9 canonical Q28 — What should be researched next?**

**Rigby SIGN cycle 1 batch 4 Q19 fold — section retitled from
"Recommended Future Research" to "Future Research — Chris-D-
verdict-request evidence (non-prescriptive)" to preempt the "Cat A
recommends" misread. Tiers below are decision candidates / evidence
prompts, NOT recommendations.**

Ranked by architectural uncertainty × risk × unblocked flows per
playbook §19. Cat A collects evidence for future Chris-D-verdicts;
Cat A does NOT recommend implementation.

### 19.1 CRITICAL tier — evidence collected for S2599 xx99 close

**R1 — [S2599 xx99 close Chris-D-verdict-request] Path A/B/C triad
resolution for backend contract SoT.** Cat A boundary evidence:
16-of-1,873 decorator adoption + 96 Serializer classes with 16.2%
model → serializer coverage + three co-existing 401 shapes +
INSTALLED_APPS absence + URL-routing absence. This is
Chris-D-verdict-request evidence, NOT a Cat A verdict. Path A / B /
C from S2203 §20.6:
- **Path A** — Full-spectrum strict contract rollout (drf-
  spectacular platform-wide + codegen + zod validation +
  standardized error envelopes for all 93 api-modules); LARGE blast
  radius.
- **Path B** — Money-path/integrity-critical only (strict contract
  on ~10-15 modules); BOUNDED blast radius.
- **Path C** — Strict for integrity/governance/money/state-changing
  REST endpoints; lighter for read-only/display-only; MIDDLE
  ground.

Cat A boundary preserved: Cat A does NOT recommend Path A/B/C
verdict; Cat A provides EVIDENCE for the Chris-D-verdict at S2599
xx99 close.

**R2 — [S2599 xx99 close Chris-D-verdict-request] drf-spectacular
wire-up decision point (Rigby SIGN cycle 1 batch 4 Q19 fold —
rephrased from imperative-verb list to decision-point framing to
prevent misread as directive).** Whether to wire drf-spectacular
(INSTALLED_APPS registration + schema-generating URL routes +
management-command availability) as the OpenAPI SoT mechanism —
Cat A evidence indicates current disconnection at three orthogonal
loci per §14.5 F5 Refutation criteria + §7.1 runtime flow:
- (i) `drf_spectacular` absent from INSTALLED_APPS at
  `core/settings.py:161-215`.
- (ii) No `SpectacularAPIView` URL route registered at
  `core/urls.py` (or any `core/urls_*.py`).
- (iii) SPECTACULAR_SETTINGS + 16 decorators exist WITHOUT app
  registration — provenance of this state is not established at
  S2501 (per §8 provenance policy: collected only if it changes
  present-day ownership/intent).

Implementation planning deferred to S2599 xx99 close or post-arc
ADR. Cat A boundary preserved: Cat A does NOT direct wire-up
sequencing; Cat A records the decision point as Chris-D-verdict-
request evidence.

### 19.2 HIGH tier — evidence for S2504 Cat D + S2503 Cat C

**R3 — [S2504 Cat D boundary evidence] Per-endpoint
`permission_classes` coverage matrix at HEAD.** Cat A boundary
evidence for Cat D per-endpoint permission-floor registry design-
prep (Cat B (c) per S2402 §19.1 + S2499 CF-B1). Per-endpoint
declaration coverage rate = evidence density Cat D consumes at
S2504 to formalize the (b)/(c) trade-off. Cat A collects at HEAD;
Cat D formalizes at S2504.

**R4 — [S2503 Cat C boundary evidence] Three co-existing 401 shapes
current-state.** Cat A boundary evidence for Cat C α/β/γ typed-
error-envelope decision-space (Cat C β = message/UX policy nested
inside Cat D mechanism γ per S2404 Rigby Q6 fold). Cat C S2503
inherits Cat A evidence: (a) DRF default `{"detail":"..."}` for
inherited permission fails; (b) APIResponseEnvelope shape for 9
hand-invoked sites; (c) bare `Response({...},status=401)` at ~152
sites plurality.

### 19.3 MEDIUM tier — evidence for S2502 Cat B + S2599 xx99 anchor-update

**R5 — [S2502 Cat B boundary evidence] 803 consumer call-site
re-verify at HEAD** (per S2500 §3.A + Rigby SIGN cycle 1 Q2-1 fold —
Cat B re-verifies at S2502 HEAD, not Cat C). Cat A boundary: 803
= 57 direct + 667 hook + 79 raw fetch at S2404 HEAD; re-verify at
S2502 HEAD in case new hooks/raw fetches landed since S2404 close.

**R6 — [S2599 xx99 close artifact candidate] docs/topics/api.md
CREATE + PLATFORM_INVENTORY §API autoblock + PLATFORM_WHAT_IT_IS
§API narrative subsection (Rigby SIGN cycle 1 batch 4 Q19 fold —
recast from "anchor-update recommendation" to "xx99-close artifact
candidate" to prevent misread as Cat A directive; Cat A does NOT
schedule or author these).** Analog to Group 2400 close
`docs/topics/auth.md` + `§Auth` autoblock + narrative subsection.
Cat A boundary evidence supports the candidacy; Chris-D-verdict at
S2599 xx99 close on scope (proposal-only per S2500 §6 P-1 + Rigby
SIGN cycle 1 Q3-2 parent scoping fold). Doc-system owner (per S2499
AU-D5 + `/docs/research/` CODEOWNERS entry) agrees at xx99 close
before any authoring commences.

**R7 — [S2599 xx99 close anchor-update recommendation]
platform_architecture_inventory.md §3.22 API Layer REVISE (not
CREATE).** Per §14.4 F4. Cat A boundary evidence supports revising
the STABLE + MODERATE posture to reflect Contract SoT DECLARATION
sub-layer PARTIAL status; overall §3.22 API Layer STABLE +
MODERATE posture preserved.

### 19.4 Boundary questions Cat A must NOT resolve (§16 anti-scope
guardrails)

Cat A discovers scope-magnets; Cat A enumerates evidence only:

1. **Should drf-spectacular move to INSTALLED_APPS + should we wire
   a SpectacularAPIView URL route?** Cat A collects evidence about
   app absence; Chris-D-verdict at S2599 xx99 close.
2. **Should openapi-typescript / orval / kubb be adopted for
   frontend typed-client codegen?** Explicit S2500 §7 anti-scope #7;
   Cat A collects feasibility-adjacent evidence only.
3. **Should `@extend_schema` decoration become mandatory across
   1,873 endpoints?** Cat A identifies undeclared endpoints; Chris-
   D-verdict at S2599 xx99 close.
4. **Should `permission_classes` inheritance be replaced with
   explicit per-view declarations?** S2504 Cat D scope; Cat A
   boundary evidence.
5. **Should DRF exception-handler layer include typed error-envelope
   schema (401/403/500)?** S2503 Cat C + S2504 Cat D scope; Cat A
   boundary evidence.
6. **Should we migrate from Django REST Framework to FastAPI /
   GraphQL / tRPC for contract-first API design?** Explicit S2500
   §7 anti-scope #6; Cat A observes half-wired schema-generation as
   evidence, not recommendation.
7. **Should backend contract SoT be single source of truth for
   frontend TS types + should frontend deploys block if schema-
   generation fails?** S2502 Cat B + S2599 xx99 xx99 close scope;
   Cat A boundary evidence.
8. **Should we add a Cat A drift verifier claim to track
   "@extend_schema coverage rate" and fail CI if drift exceeds
   threshold?** Cat A proposes verifier-infrastructure candidate;
   scope-decision at S2599 xx99 close.

## 20. Appendix

### 20.1 Files inspected

Direct-read files (parent Claude verifier-loop):
- `docs/research/domains/api/2500_api_domain_scoping.md` (§3.A + §5
  + §6 + §7 + §8 + §9)
- `docs/research/domains/frontend/2203_frontend_api_contract_
  boundary_discipline_audit.md` (§14.1 F1 + §14.6 F5 + §19.1 R1 +
  §20.6)
- `docs/research/domains/frontend/2299_frontend_canonical_summary.md`
  (§5.1 + §5.4 + §8.2 + §8.3)
- `docs/research/domains/auth/2499_auth_canonical_summary.md` (CF-*1
  flags to Group 2500)
- `docs/research/domains/auth/2402_authorization_permission_floor_
  uniformity_audit.md` (§14.5 + §19.1)
- `docs/research/domains/auth/2404_frontend_integration_silent_401_
  systemic_resolution_audit.md` (§14.5 + §19.1)
- `docs/research/platform_architecture_inventory.md` §3.22 (line
  1648) + row 22 table (line 232)
- `docs/PLATFORM_INVENTORY.md` (URL Routes 1,864; Views 209; Mgmt
  Commands 199; Models 585)
- `docs/PLATFORM_WHAT_IT_IS.md` (§API narrative subsection absent
  at HEAD)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 + §13 + §14 +
  §15)
- `00-START-NEXT-SESSION.md` (full read at S2501 open)
- `sports/views.py` (16 @extend_schema decorators + line
  disposition per §3.2 above)
- `sports/urls.py` (17 path() patterns)
- `core/settings.py:161-215` INSTALLED_APPS + `core/settings.py:645-
  669` REST_FRAMEWORK + `core/settings.py:1600-1625` SPECTACULAR_
  SETTINGS
- `core/api_responses.py:53-98` APIResponseEnvelope.error()
- `core/urls.py` (1,782 path() + 2 re_path())
- `core/urls_unified.py` (44 path())
- `core/urls_real_data.py` (9 path())
- `core/urls_provenance.py` (19 path())
- `CODEOWNERS` (established S2499 AU-D5)
- `requirements.txt` (drf-spectacular==0.28.0 INSTALLED)

Sub-agent reads (Explore Agents 1-6 delegated per playbook §13):
- Agent 1 Models + Persistence: 96 Serializer classes; 91
  ModelSerializer bindings; 563 concrete Django models;
  `sports/serializers.py:18-598` + `core/serializers_agents.py:25-
  407+` + `content/serializers.py:21-155`.
- Agent 2 Services + Runtime Flows: `SPECTACULAR_SETTINGS` 4-key
  shape; `verify_doc_claims.py` doc-drift focus (not schema-drift);
  `LeagueViewSet.standings` @extend_schema-decorated-but-inert
  runtime flow; `chat_with_assistant` no-decoration flow;
  `APIResponseEnvelope.error()` shape at `core/api_responses.py:53-
  98`; no `EXCEPTION_HANDLER` override at `core/settings.py:645-
  669`.
- Agent 3 APIs + Tools + Tasks + Commands: 1,871 path() + 2 re_path
  = 1,873 URL patterns; @extend_schema coverage matrix per-app; 3-
  slice API-slice manifest draft (money-path + governance-path +
  PA-path); custom `bpaas_schema` endpoint at `core/urls.py:4891`.
- Agent 4 Integrations + Cross-Domain: per-endpoint
  permission_classes sample (~65% implicit-inheritance); 401
  envelope shape (APIResponseEnvelope — parent-Claude verifier
  corrected to three co-existing shapes); Path A/B/C backend
  evidence density; Group 2600/1700/2300 downstream flags.
- Agent 5 Documentation + Prior Research: full extraction of S2500
  §3.A + S2203 §14.1/§14.6/§14.3/§19.1/§20.6 + S2299 §5.1/§8.2/
  §8.3/§5.4 + S2499 CF-*1 + S2402 §14.5/§19.1 + platform_
  architecture_inventory §3.22 (Agent 5 correctly identified §3.22
  API Layer; parent scoping §2.2 said §3.30 which is Body Systems).
- Agent 6 Drift + Debt + Ownership + Maturity: research coverage
  LIGHT-to-MODERATE candidate; architecture maturity EXPERIMENTAL-
  to-PARTIAL candidate (S2501 §13 selects PARTIAL); risk MEDIUM-to-
  HIGH candidate; finding-type primary `missing_connection` + `un-
  clear_owner`; debt topology top 5; CODEOWNERS audit; boundary
  questions Cat A must NOT resolve.

### 20.2 Grep commands used

Load-bearing grep patterns (parent-Claude verifier-run at HEAD
`77564f76`):

```bash
# @extend_schema decoration count
grep -c "@extend_schema" sports/views.py       # 16 (verified)
grep -rl "@extend_schema" core/*.py             # 0 (verified)

# URL pattern count
grep -c "^\s*path(" core/urls.py                # 1,782
grep -c "^\s*path(" core/urls_unified.py        # 44
grep -c "^\s*path(" core/urls_real_data.py      # 9
grep -c "^\s*path(" core/urls_provenance.py     # 19
grep -c "^\s*path(" sports/urls.py              # 17
grep -c "^\s*re_path(" core/urls.py             # 2
# Total: 1,873

# Serializer count
grep -rE "^class \w+\(.*(ModelSerializer|serializers\.Serializer|
Serializer)\)" --include="*.py"                 # 96
grep -rn "class Meta:$" -A 3 --include="*.py" |
  grep -E "model = " | wc -l                    # 91

# 401 emission sites
grep -rn "status=401|HTTP_401|status.HTTP_401"
  --include="*.py" | grep -v migrations | wc -l # 161
grep -rn "APIResponseEnvelope\.error|
  APIResponseEnvelope\.success"
  --include="*.py" | wc -l                      # 9
grep -rn "raise NotAuthenticated|NotAuthenticated()"
  --include="*.py" | wc -l                      # 0

# INSTALLED_APPS + SPECTACULAR
grep -n "drf_spectacular|drf-spectacular|SPECTACULAR"
  core/settings.py                              # SPECTACULAR_SETTINGS
                                                # at line 1600
grep -A 60 "^INSTALLED_APPS" core/settings.py |
  grep drf_spectacular                          # 0 matches

# Model count
grep -rE "^class \w+\(.*models\.Model" --include="*.py" |
  grep -v abstract | wc -l                      # 563
```

### 20.3 Docs inspected

Predecessor docs read at file:line precision per §11 above.
Additional docs consulted:
- `docs/research/OPEN_ARCS.md` (Group 2500 arc In-progress row).
- `docs/research/ARCHITECTURE_INDEX.md` (v82+ post-Group-2400
  close).

### 20.4 Unresolved unknowns (promotes to S2599 xx99 §6)

- **U1** — Historical reason for INSTALLED_APPS omission despite
  SPECTACULAR_SETTINGS + 16 decorators + pip-install existing at
  HEAD. Rigby SIGN cycle 1 batch 4 Q20 fold — reduced to one-liner:
  provenance of omission is unknown and non-load-bearing unless
  ownership/intent ambiguity requires it (per §8 provenance policy).
- **U2** — Exhaustive count of `@extend_schema`-decorated endpoints
  across ALL of `sports/views.py` + `sports/urls.py`-registered
  DRF ViewSets (does the 16-decorator count fully cover the sports
  surface or only partially?). Cat A boundary: sample-based
  observation; full sports-surface coverage measurement deferred to
  S2504 Cat D if load-bearing for permission-floor registry.
- **U3** — Full inventory of the ~152 bare `Response({...},
  status=401)` sites (161 emission sites minus 9 APIResponseEnvelope
  invocations minus DRF-default-path sites). Grep-based estimate at
  Cat A boundary; per-site classification (which shape does each
  emit?) is Cat C S2503 scope for message/UX policy design-prep.
- **U4** — Whether the 22-model drift (563 grep vs 585 PLATFORM_
  INVENTORY) is entirely abstract-mixin methodology delta or
  includes runtime drift. Cat A boundary: observation only;
  PLATFORM_INVENTORY regeneration + generator introspection deferred
  to xx99 close cascade.
- **U5** — Whether the 9-pattern URL drift (1,873 verified vs
  1,864 PLATFORM_INVENTORY) is stable or continuing to accumulate.
  Cat A boundary: observation only; PLATFORM_INVENTORY regeneration
  deferred to xx99 close cascade.

### 20.5 Conflicts between sources

| Source A | Source B | Conflict | Cat A resolution |
|---|---|---|---|
| S2500 parent scoping §2.2 (says "§3.30 API layer TBD baseline") | platform_architecture_inventory.md §3.22 API Layer STABLE+MODERATE (line 1648) | S2500 §2.2 was imprecise about section number | §14.4 F4 records verifier resolution — §3.22 API Layer EXISTS |
| PLATFORM_INVENTORY.md (1,864 URL patterns) | S2501 verifier (1,873 URL patterns at HEAD `77564f76`) | 9-pattern drift | §14.2 F2 records observation; xx99 close cascade regenerates PLATFORM_INVENTORY |
| PLATFORM_INVENTORY.md (585 models) | S2501 verifier grep (563 models excluding abstract) | 22-model drift | §14.3 F3 records observation; methodology delta not runtime drift |
| Explore Agent 4 claim (APIResponseEnvelope is the dominant 401 shape) | Parent-Claude verifier grep (APIResponseEnvelope = 9 usages; DRF default dominates) | Agent 4 overreached | §7.3 records verifier-corrected finding — three co-existing 401 shapes |
| Explore Agent 1 claim (95 total Serializer classes) | Parent-Claude verifier grep (96 total) | Minor undercount +1 | §4.1 records verifier-corrected 96 count |
| S2203 §14.6 F5 characterization ("INSTALLED-PARTIAL-WIRED") | S2501 verifier (INSTALLED_APPS absent + URL-routing absent) | S2203 measured decorator side only | §14.1 F1 records extended S2501 finding — INSTALLED + CONFIGURED + PARTIALLY-DECORATED + FULLY-DISCONNECTED |
| S2501 draft v0 §14.6 F6 (three co-existing 401 shapes) | Rigby SIGN cycle 1 batch 2 Q7 STRENGTHEN verifier-loop finding (four co-existing 401 shape families — added shape (d) non-DRF `JsonResponse` with error-as-string at 93 sites) | v0 undercounted; Q7 STRENGTHEN found shape (d) as distinct substrate bypassing DRF renderer entirely | §14.6 F6 v1 records four shape families; §17 duplicate/overlap zone (ii) updated to four substrates per Q17 fold |
| S2501 draft v0 §6.1 (endpoint enumeration) | Rigby SIGN cycle 1 batch 2 Q6 fold (AC #7 spec-only guardrail requires §6.1.1 measurement-harness spec addition) | v0 read as inventory drift toward de-facto shipped artifact | §6.1.1 added: Inputs + Proposed commands (non-binding) + Report schema + Acceptance thresholds NONE in Cat A + Non-goal (no CI job) |
| S2501 draft v0 §9 (9 integration rows) | Rigby SIGN cycle 1 batch 2 Q9 fold (missing Group 1500 Sports explicit + Group 1300 Memory conditional + Group 2000+ Celery conditional rows) | v0 read Group 1500 Sports as only implicit example | §9 rows 11, 12, 13 added — Sports promoted to explicit integration; Memory + Celery-adjacent as conditional rows |
| S2501 draft v0 §14.5 F5 refutation tally (3-of-4 refute + 1 not-measurable) | Rigby SIGN cycle 1 batch 3 Q14 fold (non-verdict qualifier) | v0 tally read as verdict-adjacent language | §14.5 F5 explicit "This tally is not a Cat A verdict" statement added — evidence snapshot only |
| S2501 draft v0 §19 title "Recommended Future Research" | Rigby SIGN cycle 1 batch 4 Q19 fold (retitled to "Future Research — Chris-D-verdict-request evidence (non-prescriptive)") | v0 title read as Cat A recommends | §19 retitled + R2 rephrased to decision-point framing + R6 recast to xx99 artifact candidate |

### 20.6 Verifier-loop corrections (Rigby SIGN fold notes)

**Rigby SIGN cycle 1 CLOSE — cycle 2 NOT required per explicit
Rigby verdict at batch 4 close: "Cycle 2 only needed if you
discover new evidence that changes core claims; remaining edits are
framing/clarity updates, not new research mandates."**

- **Cadence per feedback_rigby_sign_worker_instability_recovery** —
  4-batch × 5-Q = 20-Q child-audit cadence per S2201-S2404 nine-
  consecutive tested pattern (TENTH-consecutive application at
  S2501 P1 Cat A). Batches: batch 1 §1-§5 framing + entry + models
  + services; batch 2 §6-§10 APIs + flows + ownership + integrations
  + events; batch 3 §11-§15 docs + coverage + maturity + drift +
  debt; batch 4 §16-§20 boundaries + duplicates + ownership +
  future + appendix.

- **Fold count summary (Rigby SIGN cycle 1 batches 1-4 aggregate,
  Rigby SIGN cycle 1 batch 4 Q20 additional-fold — final count at
  cycle close):**
  - **Batch 1 (Q1-Q5): 4 folds landed** — Q1 verdict-neutrality
    language tightening (§1 end); Q2 optional parenthetical
    (§3.1); Q4 pattern-analogy boundary note (§5.5); Q5 severity
    → impact-classification reframing (§14.6 F6). Q3 SIGN clean.
  - **Batch 2 (Q6-Q10): 5 folds landed** — Q6 §6.1.1 measurement-
    harness spec-only subsection add; Q7 STRENGTHEN (§14.6 F6 v0
    three-shape → v1 FOUR-shape family expansion via verifier-loop;
    §7.3 exhaustiveness note; shape (d) 93-site non-DRF JsonResponse
    family added); Q8 §8 provenance policy tightening; Q9 §9 rows
    11-13 added (Group 1500 Sports explicit + Group 1300 Memory
    conditional + Group 2000+ Celery conditional); Q10 STRENGTHEN
    §10 event adjacency scan + neutrality guard.
  - **Batch 3 (Q11-Q15): 5 folds landed** — Q11 §11 3 predecessor
    rows added (S2500 §3.5 disposition + Group 2400 §14.5 21-loci
    methodology + Session 1099 "no doc found" note); Q12 §12 "Cat
    A does not select LIGHT vs MODERATE" micro-guard; Q13 §13
    modality tightened (should → expected to; adding → may
    optionally add); Q14 §14.5 non-verdict tally qualifier; Q15
    §15 section header rename + item 2 non-recommendation qualifier
    + item 5 symptom-layer + downstream-ownership tag.
  - **Batch 4 (Q16-Q20): 4 folds landed** — Q16 §16 boundary-
    violation phrasing softened to Cat-A-local scope; Q17 §17
    duplicate/overlap zone (ii) updated from three → four
    substrates (post-§14.6 v1 expansion); Q19 §19 retitled +
    R2 rephrased to decision-point framing + R6 recast to xx99
    artifact candidate; Q20 §20.4 U1 reduced to one-liner + §20.5
    conflicts table updated with 5 verifier-loop-and-SIGN-batch-2/
    3/4 rows + §20.7 arc metadata verifier-loop summary added. Q18
    SIGN clean.
  - **Aggregate: 18 folds landed pre-Chris-ratification** across 4
    batches; Q3 + Q18 SIGN-clean (2 questions passed without
    folds). Within the "15-25 folds" S2201-S2404 empirical baseline
    per feedback_rigby_sign_worker_instability_recovery batching
    pattern.

- **Additional verifier-loop-during-SIGN find (batch 2 Q7
  STRENGTHEN):** Rigby's Q7 STRENGTHEN prompted parent-Claude to
  verify the 3 gap probes (ValidationError + 401 proximity /
  middleware short-circuit / non-DRF Django 401 emitters). Grep
  found 93 non-DRF JsonResponse 401 emitters at HEAD — significant
  fourth-family finding that materially expanded §14.6 F6 v0 three-
  shape → v1 four-shape framing. This is a within-cycle verifier-
  loop-during-SIGN discipline application (analog to S2404 §14.6
  F-D-CALL-1 count 803-correction during draft writing per Cat D
  Rigby cycle 1).

- **Cycle 2 NOT required** per Rigby explicit verdict at batch 4
  close 2026-07-05. Cat A boundary integrity preserved; remaining
  edits (all landed) are framing/clarity updates, not new research
  mandates.

- **Chris-ratifiable at child audit stage** per playbook §16 draft-
  first workflow.

### 20.7 S2501 arc metadata

- **HEAD:** `77564f76aa509e8807020730df1d85e2f5aee0d8`
  (post-parent-scoping merge PR #2920; parent scoping doc referenced
  pre-merge HEAD `4e6c1ee8`).
- **Arc pin:** `pa-a03b111768464b3f` (ACTIVE + PRESERVED per
  playbook §16 arc-standard behavior; TWELFTH formal arc pin under
  Research OS).
- **SIGN pin (S2501 SIGN cycle 1):** PENDING — dedicated fresh
  isolation pin to be minted at draft-complete via
  `session_tool.create_fresh` per playbook §15; EIGHTEENTH-
  consecutive dedicated fresh SIGN pin candidate.
- **Playbook §11.2 application:** TWENTIETH-consecutive 20-section
  child-audit template application (after S1301+S1401+S1501+S1601+
  S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+
  S2203+S2204+S2401+S2402+S2403+S2404 nineteen prior).
- **Draft-first workflow per playbook §16:** status `draft` at
  write; flips to `active` on Chris "commit it" ratification post-
  SIGN cycle 1 close.
