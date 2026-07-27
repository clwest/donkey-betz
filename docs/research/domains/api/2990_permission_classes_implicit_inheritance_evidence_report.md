---
title: "2990 — permission_classes Implicit Inheritance — Evidence Report"
status: evidence
session: 2990
generated: 2026-07-27
originating_finding: 3fbd8098-82d8-4d27-bc3c-83f29677446f
source_audit: docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md
head_at_generation: 808c50603
category: research_evidence
non_prescriptive: true
methodology_reference: docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md
enforcement_owner_arc: Cat D S2504
---

# 2990 — `permission_classes` Implicit Inheritance — Evidence Report

## 1. Staleness & drift corrections (READ FIRST)

The originating finding was indexed from a S2402/S2501 snapshot. Between then and HEAD `808c50603`, the following specific claims have drifted:

| Claim in finding / source audit | State at HEAD `808c50603` | Correction |
|---|---|---|
| `DEFAULT_PERMISSION_CLASSES` at `core/settings.py:652-653` | Actual location: **`core/settings.py:737-738`** | Line refs stale — settings file has grown since S2402. Value unchanged (`IsAuthenticated`). |
| `sports/views.py:45` `LeagueViewSet` "no explicit permission_classes = inherits default" | `LeagueViewSet` **now declares** `permission_classes = [permissions.AllowAny]` at `sports/views.py:48` | Concrete example is wrong at HEAD. Someone added `AllowAny` between S2402 and S2990. |
| `~80-90% implicit-inheritance rate` per S2402 §14.5 F-B-CRIT-1 (measured via 21-loci grep methodology) | Runtime URL-resolver walk at HEAD: **2.3% implicit inheritance** among DRF class-based views (19 of 818) | Rate estimate off by an order of magnitude. See §3 for measurement methodology + reconciliation with S2402. |

**These corrections do not invalidate the underlying concern** (implicit inheritance is a real contract-observability question). They do mean the specific numeric and file-line evidence in the finding needs to be treated as **stale until re-verified at HEAD**, which is what this report does.

## 2. Boundaries (non-prescriptive)

Mirroring the source audit's §19 boundary framing (`2501_api_backend_contract_sot_design_prep_audit.md:1480-1492`):

**What this report deliberately does NOT do:**

1. **Does not recommend "enforce" vs "accept default inheritance."** The audit assigns this decision to **Cat D S2504** (`2501...audit.md:1541-1547` R3 + `1600-1602` anti-scope #4). This report provides evidence for that verdict, not the verdict itself.
2. **Does not propose per-view rollout sequencing, CI-fail thresholds, or lint rules.** Those are downstream of the Cat D decision.
3. **Does not re-score severity or rewrite the S2402 / S2501 audits.** Historical audits are preserved as-is; a small forward-pointing addendum is added at the referenced bullet (see companion edit to `2501...audit.md:1335-1342`).
4. **Does not classify individual implicit-inheritance views as "high-risk" vs "acceptable."** Risk framing belongs to the Cat D decision context.

## 3. Snapshot + methodology

| Field | Value |
|---|---|
| Repo HEAD | `808c50603` |
| Generated | 2026-07-27 |
| Method | `django.urls.get_resolver().url_patterns` walk + `view_cls.__dict__` introspection for own-attribute (not inherited) `permission_classes` |
| Scope | Every DRF class-based view (`APIView` or `ViewSetMixin` subclass) reachable via Django's URL resolver from `ROOT_URLCONF = core.urls` |

**Why runtime walk vs static grep:**

The S2402 audit's "~80-90% implicit" figure was estimated via a **static 21-loci grep methodology** (`docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` §14.5 F-B-CRIT-1; referenced in `2501...audit.md:1013`). That methodology counts textual absence of `permission_classes = ...` across view files.

This report uses a **runtime URL-resolver walk**, which:
- Only counts views actually reachable via a URL pattern (a class defined but not routed doesn't count).
- Uses `view_cls.__dict__` to distinguish views that declare `permission_classes` **on the class itself** from those that inherit it from a base class (which the audit's grep methodology may have missed).

Both are valid measurements of different things. The runtime measurement is the one that matters for actual request-time permission enforcement.

## 4. Findings

### 4.1 Coverage measurement (runtime, HEAD `808c50603`)

| Metric | Count | Share |
|---|---:|---:|
| Total URL patterns walked (all layers) | 2,904 | — |
| Non-DRF endpoints (Django views, admin, catch-alls, WebSocket routes) | 1,819 | — |
| DRF class-based view classes (unique) | 818 | 100.0% |
| ├─ With explicit `permission_classes` on the class | **799** | **97.7%** |
| └─ Without explicit — inherits `DEFAULT_PERMISSION_CLASSES` | **19** | **2.3%** |
| DRF `@api_view` function views detected via `hasattr(cb, 'cls')` | 0 | — |

Note on the "0 function views" line: introspection via `cb.cls` did not surface any function-based `@api_view` handlers as a distinct bucket at HEAD. That may reflect (a) the codebase using class-based views nearly exclusively, or (b) an introspection blind spot. It does not change the class-based-view coverage measurement, which is the primary interest.

### 4.2 Full enumeration of the 19 implicit-inheritance views

Sorted by module. Third-party rows marked; they are not fixable in-repo.

| Module.Class | Source location |
|---|---|
| `core.views_preview_api.FeedbackItemViewSet` | `core/views_preview_api.py:336` |
| `core.views_preview_api.PreviewEnvironmentViewSet` | `core/views_preview_api.py:186` |
| `core.views_preview_api.ProjectEnvVarViewSet` | `core/views_preview_api.py:172` |
| `core.views_preview_api.ProjectRepoViewSet` | `core/views_preview_api.py:158` |
| `core.views_preview_api.WorkspaceProjectViewSet` | `core/views_preview_api.py:144` |
| `intelligence.views.IncomeActionPlanView` | `intelligence/views.py:352` |
| `intelligence.views.IncomeBuilderAnalysisView` | `intelligence/views.py:123` |
| `intelligence.views.LiveOpportunitiesView` | `intelligence/views.py:79` |
| `intelligence.views.LivePredictionsView` | `intelligence/views.py:101` |
| `intelligence.views.SkynetStatusView` | `intelligence/views.py:43` |
| `rest_framework.routers.APIRootView` | *[3rd-party — DRF internal, not fixable in-repo]* |
| `sports.views.ArbitrageOpportunityViewSet` | `sports/views.py:835` |
| `sports.views.BetViewSet` | `sports/views.py:722` |
| `sports.views.BettingMarketViewSet` | `sports/views.py:556` |
| `sports.views.BettingRecommendationViewSet` | `sports/views.py:870` |
| `sports.views.SportsAnalyticsViewSet` | `sports/views.py:942` |
| `sports.views.SportsUtilityViewSet` | `sports/views.py:984` |
| `sports.views.SportsbookViewSet` | `sports/views.py:489` |
| `sports.views.TeamViewSet` | `sports/views.py:152` |

**In-repo count: 18** (excluding the DRF `APIRootView`).

### 4.3 Cluster distribution

The 18 in-repo implicit-inheritance views cluster into three modules:

| Cluster | View count | Domain semantics |
|---|---:|---|
| `sports/views.py` — betting-adjacent ViewSets | 8 | Money-path / integrity-critical (Path B/C candidates per source audit) |
| `intelligence/views.py` — income + skynet views | 5 | Income-generation flow (money-path adjacent) |
| `core/views_preview_api.py` — preview infra ViewSets | 5 | Dev/staging infrastructure (not user-facing money) |

**Observation without recommendation:** all 18 in-repo views currently inherit `IsAuthenticated`, so runtime behavior is not silently permissive. The concern the finding raises is contract-observability (a future edit to `DEFAULT_PERMISSION_CLASSES` would silently affect all 18), not a current security gap. The Cat D S2504 decision context is whether to make this observability property explicit at each view.

### 4.4 State-changing exposure among the 18

For a Path C-style analysis (strict for state-changing, lighter for read-only), the implicit-inheritance list splits as follows based on view class semantics:

- **State-changing ViewSets** (support POST/PUT/PATCH/DELETE via router): all 8 `sports/*` ViewSets + all 5 `core.views_preview_api.*` ViewSets = **13 views**.
- **Read-only class-based views** (`generics.RetrieveAPIView` / `ListAPIView` / bespoke read-only `APIView`): 5 `intelligence/*` views appear read-only by name; verification would require per-view HTTP-method inspection deferred to Cat D S2504.

Enumeration only; classification into "must-declare" vs "may-inherit" is Cat D scope.

## 5. Path A/B/C linkage (verbatim from source audit)

Because the enforcement decision sits alongside Path A/B/C strategic axis, quoted verbatim from `2501_api_backend_contract_sot_design_prep_audit.md:1503-1511`:

> **Path A** — Full-spectrum strict contract rollout (drf-spectacular platform-wide + codegen + zod validation + standardized error envelopes for all 93 api-modules); LARGE blast radius.
>
> **Path B** — Money-path/integrity-critical only (strict contract on ~10-15 modules); BOUNDED blast radius.
>
> **Path C** — Strict for integrity/governance/money/state-changing REST endpoints; lighter for read-only/display-only; MIDDLE ground.

**Cross-reference (evidence only, not verdict):** the 18 in-repo implicit views map onto these Paths as follows —

- **Path B scope** would touch the 8 `sports/*` betting ViewSets (money-path).
- **Path C scope** would touch the 8 sports ViewSets + likely the 5 `intelligence/*` views (income money-path adjacent), leaving `core.views_preview_api.*` as "may inherit."
- **Path A scope** would touch all 18.

## 6. R3 anchor (verbatim from source audit)

The source audit's R3 explicitly designates permission-classes coverage as evidence-collection for Cat D S2504 (`2501...audit.md:1541-1547`):

> **R3 — [S2504 Cat D boundary evidence] Per-endpoint `permission_classes` coverage matrix at HEAD.** Cat A boundary evidence for Cat D per-endpoint permission-floor registry design-prep (Cat B (c) per S2402 §19.1 + S2499 CF-B1). Per-endpoint declaration coverage rate = evidence density Cat D consumes at S2504 to formalize the (b)/(c) trade-off. Cat A collects at HEAD; Cat D formalizes at S2504.

Boundary question #4 from `2501...audit.md:1600-1602`:

> **Should `permission_classes` inheritance be replaced with explicit per-view declarations?** S2504 Cat D scope; Cat A boundary evidence.

## 7. Next

- Enforcement verdict is scheduled for **Cat D S2504**. This report is the coverage-matrix evidence R3 was designed to consume.
- The originating `DocResearchFinding` should be closed on the Findings surface with an appropriate mode. As at S2990, the surface offers only `open` / `fixed`; the closer-fit modes surfaced across findings #2 and #3 of this session are **"evidence delivered (decision pending)"** and **"stale → re-verify required."** Not fixed here; noted as a v2 Findings-surface follow-up.

## 8. Provenance

- **Finding source:** `DocResearchFinding` row indexed from `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md:1335-1342` at S2989 Phase B via `python manage.py index_doc_research_findings`.
- **Send-to-Rigby spec generator:** `core/services/briefing_spec_generator.py` (S2989 Phase A) produced Deliverable `3fbd8098-82d8-4d27-bc3c-83f29677446f`.
- **Execution session:** S2990, Flow A (real-use loop of the Findings surface, finding #3 of 3).
- **Rigby SIGN cycle:** joint agreement on execution shape (X = ship evidence report + small audit addendum; NOT Y = enforce; NOT Z = mark informational) reached before authoring; three `tool_run` citations against source audit + settings + sports views per PLAYBOOK-7.7.2.
- **Data-collection HEAD:** `808c50603`.
- **Sibling report from same session:** `docs/research/domains/api/2990_backend_contract_undeclared_endpoints_evidence_report.md` (PR #3644, finding #2 of 3).
