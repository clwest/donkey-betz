---
title: "2990 — Backend Contract Undeclared Endpoints — Evidence Report"
status: evidence
session: 2990
generated: 2026-07-27
originating_finding: b62c2403-fdf6-427f-bf51-2abab64cb171
source_audit: docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md
head_at_generation: ec34f772a
category: research_evidence
non_prescriptive: true
---

# 2990 — Backend Contract Undeclared Endpoints — Evidence Report

## Snapshot

| Field | Value |
|---|---|
| Repo HEAD | `ec34f772a` |
| Generated | 2026-07-27 |
| Method | Live query of `/api/schema/` (drf-spectacular AutoSchema, enabled at S2990 PR #3642) + `grep -rn "@extend_schema"` over `**/*.py` + `PLATFORM_INVENTORY.md` URL-pattern count |
| Originating finding | `DocResearchFinding` → Deliverable `b62c2403-fdf6-427f-bf51-2abab64cb171` |
| Originating audit | `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md` §Known Technical Debt + §19.1 R1 |

## Boundaries (non-prescriptive)

**This document is EVIDENCE for a future Chris-D-verdict, not a recommendation.** It mirrors the source audit's own §19 boundary framing, which retitled its own recommendations section to *"Future Research — Chris-D-verdict-request evidence (non-prescriptive)"* to preempt the *"Cat A recommends"* misread (source: `2501_api_backend_contract_sot_design_prep_audit.md:1480-1492`).

**What this report deliberately does NOT do:**

1. **Does not recommend Path A, Path B, or Path C.** Choice is reserved for Chris-D-verdict at S2599 xx99 close per `2501...audit.md:1513-1515`.
2. **Does not recommend mass `@extend_schema` decoration** across the 1,871 endpoints. Explicitly out-of-scope per `2501...audit.md:1597-1599` (audit anti-scope guardrail #3).
3. **Does not recommend adopting `openapi-typescript` / `orval` / `kubb`** or any frontend typed-client codegen tool. Explicitly out-of-scope per `2501...audit.md:1594-1596` (audit anti-scope guardrail #2).
4. **Does not propose sequencing, checklists, owner assignments, ROI estimates, or CI-fail thresholds.** Those are strategic decisions downstream of the Path choice.
5. **Does not transform the Path A/B/C definitions** into a plan; quotes them verbatim from the source audit and stops there.

The purpose of this report is to provide *current-state numeric evidence* against which a future Path decision can be made with real numbers.

---

## Findings

### 1. Coverage denominator + numerator

Two denominators are in play depending on the framing:

| Denominator basis | Count | Numerator (`@extend_schema` decorators) | Coverage |
|---|---:|---:|---:|
| **All Django URL patterns** (`path()` calls across `core/urls*.py`) — the audit's original denominator | **1,871** | 16 | **0.86%** |
| **DRF-representable subset** (paths that appear in the generated OpenAPI schema at `/api/schema/`) | **918** | 16 | **1.74%** |

Notes:
- URL-pattern count of **1,871** comes from `PLATFORM_INVENTORY.md` (regenerated 2026-07-22, HEAD `1d634966f`). The S2501 audit used **1,873**; the two-pattern delta is within noise for a repo that has landed multiple PRs between the two measurements.
- **918** is the count of distinct paths that drf-spectacular could enumerate through DRF view introspection — Django function views, admin, WebSocket consumers, catch-alls, and non-DRF `path()` entries do not surface.
- The audit's original "16-of-1,873" and "~1,857 undeclared" number remains directionally accurate. After S2990 PR #3642 wired drf-spectacular, those 16 decorators — previously inert at `sports/views.py` — now produce real OpenAPI metadata, but the raw coverage numerator is unchanged.

### 2. Location of all declared endpoints

All 16 `@extend_schema` sites live in a single file:

`sports/views.py` — lines 58, 117, 164, 344, 357, 385, 500, 568, 744, 848, 887, 907, 924, 953, 987, 1023.

Zero `@extend_schema` decorators exist anywhere else in the codebase (verified via `grep -rn "@extend_schema" **/*.py`; other hits are import statements, comments, or docs).

This matches the audit's Group 1500 Sports evidence row: *"currently INERT at HEAD due to drf-spectacular disconnect but is the live integration dependency for any Path A / B / C future retrofit"* (`2501...audit.md:929`). Post-S2990, the "INERT" qualifier no longer applies — the decorators are now active — but the sole-file concentration does.

### 3. Method breakdown (DRF-schema subset)

From the 918-path DRF-representable subset:

| HTTP method | Operation count |
|---|---:|
| GET | 565 |
| POST | 389 |
| DELETE | 37 |
| PUT | 29 |
| PATCH | 22 |
| **Total operations** | **1,042** |

### 4. State-changing vs read-only classification

Bucketing paths (not operations) by whether they have any state-changing verb:

| Bucket | Path count | Share |
|---|---:|---:|
| **State-changing** (any POST / PUT / PATCH / DELETE) | 438 | 47.7% |
| **Read-only** (GET-only) | 480 | 52.3% |

This bucketing is the axis Path C uses (*"strict for integrity/governance/money/state-changing REST endpoints; lighter for read-only/display-only"* — `2501...audit.md:1509-1511`). The evidence: a Path C rollout would touch ~438 paths for strict-contract enforcement and ~480 paths for lighter treatment.

### 5. Per-module distribution (top-level namespace)

The DRF-representable schema spans **121 distinct top-level modules** (i.e., first path segment after `/api/` or `/api/v1/`). The S2501 audit referenced "93 api-modules"; the delta reflects module growth in the ~500 sessions between S2501 and S2990.

Top 30 modules by path count in the generated schema:

| Module | Paths |
|---|---:|
| `sports` | 52 |
| `content` | 46 |
| `analytics` | 41 |
| `workflows` | 37 |
| `agents` | 27 |
| `workspaces` | 26 |
| `projects` | 23 |
| `legal` | 21 |
| `betting` | 21 |
| `intelligence` | 21 |
| `collaboration` | 17 |
| `learning` | 17 |
| `mythology` | 17 |
| `preview` | 17 |
| `assistant` | 16 |
| `collective` | 16 |
| `pa` | 16 |
| `preferences` | 16 |
| `reasoning` | 16 |
| `video` | 16 |
| `persistence` | 15 |
| `auth` | 14 |
| `creative-projects` | 13 |
| `profile` | 13 |
| `stripe` | 13 |
| `initiatives` | 12 |
| `stocks` | 12 |
| `training` | 12 |
| `self-awareness` | 12 |
| `freelance` | 10 |

Remaining 91 modules have ≤10 paths each and are not enumerated inline; they aggregate to ~120 additional paths.

### 6. Serializer-class enforcement

Rough count via `grep -c "^\s*serializer_class\s*=" $(files-containing-ViewSet-or-APIView)`: **38 declarations** of `serializer_class = ...` across DRF view files.

Reconciliation with the audit's *"96 Serializer classes"* number: the audit measured the count of `class X(Serializer)` / `class X(ModelSerializer)` definitions (**supply side**). This report measures the count of DRF views that BIND a serializer via `serializer_class = ...` (**consumption side**). Both numbers are relevant to a Path decision:

- The 96 count says: 96 Serializer classes exist in the codebase.
- The 38 count says: 38 DRF views wire one of those Serializers as their explicit contract.
- The gap (96 supply vs 38 consumption) suggests many Serializers are used ad-hoc inside view methods rather than declared at the view level — which is exactly the *"auto-discovery blocked without serializer_class enforcement"* pattern the finding calls out.

### 7. Post-S2990 state change relative to audit

The S2501 audit measured a repo where drf-spectacular was **half-wired** (SPECTACULAR_SETTINGS present, no INSTALLED_APPS entry, no schema URL). S2990 PR #3642 and PR #3643 shipped:

- `drf_spectacular` added to `INSTALLED_APPS` (`core/settings.py:222`)
- `DEFAULT_SCHEMA_CLASS = 'drf_spectacular.openapi.AutoSchema'` added to `REST_FRAMEWORK` (`core/settings.py:742-743`)
- Three schema URL routes wired: `/api/schema/`, `/api/schema/swagger-ui/`, `/api/schema/redoc/` (`core/urls.py:5051-5062`)
- Schema endpoints moved to `PUBLIC_PATHS` in `UnifiedTokenAuthenticationMiddleware` (`core/auth_middleware.py:513`)

**What this changed for the numbers in this report:** the 16 `sports/views.py` decorators now produce real OpenAPI metadata (previously inert). Coverage denominator/numerator is unchanged. What changed is **enforcement mechanism availability** — a Path decision that requires drf-spectacular is now unblocked at the infrastructure layer; only the decoration decision remains.

---

## Path A/B/C — verbatim from source audit

Quoted verbatim from `2501_api_backend_contract_sot_design_prep_audit.md:1503-1511`:

> **Path A** — Full-spectrum strict contract rollout (drf-spectacular platform-wide + codegen + zod validation + standardized error envelopes for all 93 api-modules); LARGE blast radius.
>
> **Path B** — Money-path/integrity-critical only (strict contract on ~10-15 modules); BOUNDED blast radius.
>
> **Path C** — Strict for integrity/governance/money/state-changing REST endpoints; lighter for read-only/display-only; MIDDLE ground.

**Audit's own boundary reminder** immediately following the triad (`2501...audit.md:1513-1515`):

> Cat A boundary preserved: Cat A does NOT recommend Path A/B/C verdict; Cat A provides EVIDENCE for the Chris-D-verdict at S2599 xx99 close.

---

## Next

Chris-D-verdict on Path A/B/C is scheduled for S2599 xx99 close per the source audit. This report is the evidence artifact that verdict was designed to consume.

If the S2599 xx99 close is not yet reached at the time the corresponding `DocResearchFinding` is closed on the Findings surface, the appropriate close mode is *"evidence delivered / deferred (decision pending)"* rather than *"fixed via PR"*. The surface does not currently expose that close mode as of S2990; that is a v2 Findings-surface follow-up, not a blocker on this report.

---

## Provenance

- **Finding source:** `DocResearchFinding` row indexed from `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md::Known Technical Debt` at S2989 Phase B via `python manage.py index_doc_research_findings`.
- **Send-to-Rigby spec generator:** `core/services/briefing_spec_generator.py` (S2989 Phase A) produced Deliverable `b62c2403-fdf6-427f-bf51-2abab64cb171`.
- **Execution session:** S2990, Flow A (real-use loop of the Findings surface).
- **Rigby SIGN cycle:** joint agreement on execution shape (ship report per ACs with pinned Boundaries section) reached before authoring; two `tool_run` citations against the source audit per PLAYBOOK-7.7.2.
- **Data-collection HEAD:** `ec34f772a` (post-S2990 PR #3643 merge).
