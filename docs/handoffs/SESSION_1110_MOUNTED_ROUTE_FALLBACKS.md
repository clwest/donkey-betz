---
title: "Session 1110 — mounted broken-route fallbacks (PR 1 of deeper cleanup)"
date: 2026-05-08
status: active
session: 1110
previous_handoff: SESSION_1109_UNTRACK_RAG.md
---

# Session 1110 — mounted broken-route fallbacks (PR 1 of deeper cleanup)

## TL;DR

- **Shipped:** removed five mounted Django routes from the latent-500 list. Each was rendering a template that no longer exists; each now redirects to its React/SPA equivalent or returns a minimal inline HTML fallback that preserves the original status code.
- **Branch:** `fix/mounted-broken-route-fallbacks` (off `main`).
- **Scope is intentionally narrow.** No view deletions, no URL pattern removals, no archival of the broader dormant-module list (`sports_betting/`, `agents/urls_deployment.py`, `revenue/models.py`, `ai_core/intelligence/{monitoring_dashboard,testing_suite}.py`, `frontend/components/generated/`, stale `reports/*.json`). Those stay where they are pending the deeper-review follow-ups.

---

## Why this PR

The Session 1110 deeper connection-status review (verbatim notes in this
session's chat transcript; summarized below) identified four mounted
Django routes guaranteed to 500 because their `render(...)` targets the
SPA migration left behind. A fifth route (`/share/<token>/`) had five
legacy template paths in a state machine, all missing.

Hitting any of them returned a Django `TemplateDoesNotExist` 500. Low
traffic surfaces, but real latent foot-guns — and the kind of thing that
trips up doc-vs-runtime reviewers who try to verify "does this URL
work?" against the inventory.

| Route | Old behavior | New behavior |
|---|---|---|
| `/visualization/` | 500 — rendered missing `visualization.html` | 302 → `/neural-orchestra` |
| `/ai-building-products/` | 500 — rendered missing `ai_building_products_with_agents.html` | 302 → `/agents` |
| `/share/<str:share_token>/` | 500 in 5 distinct legacy template states (expired, password prompt, wrong password, project view, not found, error) | 200/401/404/410/500 with minimal inline HTML fallbacks; status semantics preserved |
| `/nexus/` | 500 — rendered missing `unified_intelligence_dashboard.html` | Serves React SPA shell (URL preserved); auth'd users see `/intelligence` page; unauth'd users get the existing 302 → login |
| `/intelligence/` | 500 (same template) | Same SPA shell delegation; URL preserved |

`/intelligence/` was specifically picked over a redirect-to-`/intelligence`
because the Django route catches the URL first — a redirect would loop
once Django re-evaluates and re-matches the same pattern.

---

## What Shipped

### 1. `core/views_visualization.py`

Replaced the three template renders with redirects. Removed the unused
`cache_page` and `render` imports. Function signatures and decorators
preserved (`@require_GET` stays on `ai_agents_visualization`). Module
docstring updated to flag the redirect intent.

### 2. `core/views_ecosystem.py`

Replaced the single `ai_building_products` render with a redirect to
`/agents`. Removed the unused `from django.shortcuts import render`.
Other functions in the file (`ecosystem_stats`, `ecosystem_live_feed`,
`get_project_status`, `code_preview`) untouched.

### 3. `core/views_share.py`

Added two private helpers:

- `_share_fallback_html(*, title, body)` — the shared dark-theme
  fallback shell.
- `_share_password_form(share_token, error=None)` — POSTs back to
  `/share/<token>/` so the existing password-protected share flow still
  works without the missing template.

Replaced all five `render(...)` calls in `view_shared_project`:

| Old render | Status | New behavior |
|---|---|---|
| `share_expired.html` | 410 GONE | inline fallback: "This share link has expired/been revoked." |
| `share_password.html` (prompt) | 200 | inline password form |
| `share_password.html` (wrong pw) | 401 (was 200) | inline password form with error |
| `public_project_view.html` (success) | 200 | inline "valid share" landing card pointing back to `/` |
| `share_not_found.html` | 404 | inline "share not found" fallback |
| `share_error.html` | 500 | inline "something went wrong" fallback |

Side-effect preservation: the success path still loads
`ImageHistory/VideoHistory/MiniFigAsset` querysets and calls
`share.increment_view_count()` exactly as before, so analytics keep
working. The variables are bound but unused in the fallback body
(prefixed with `_`); they're left in place because removing them would
also remove the side-effect chain and is out of scope for a route
fallback PR.

The wrong-password path moved from `200` to `401` because returning
`200` for a credential rejection violates the existing API behavior
contract. If anything downstream depended on the old `200`, it was
probably already broken — but flagging this for review.

### 4. `core/views_unified_intelligence.py`

Replaced the single `unified_intelligence_dashboard` render with
`react_app(request)` (imported lazily inside the function to avoid an
extra top-level import in this large file). The `@login_required`
decorator stays — preserves the original auth gate. Removed the unused
`from django.shortcuts import render`.

### 5. `core/tests/test_mounted_route_fallbacks.py` (new file)

Six smoke tests, all `SimpleTestCase` (no DB):

- `/visualization/` redirects to `/neural-orchestra` (302).
- `/ai-building-products/` redirects to `/agents` (302).
- `/nexus/` returns non-500 (302 to login when unauthenticated; 200 SPA shell otherwise).
- `/intelligence/` returns non-500 (same).
- `/share/<token>/` returns 404 + fallback body when the share doesn't exist.
- `/share/<token>/` returns 500 + fallback body (NOT a `TemplateDoesNotExist` trace) when the lookup raises.

The two share tests use `unittest.mock.patch` on
`ProjectShare.objects.get` / `.select_related` so the smoke is DB-free.

A DB-backed authenticated test was prototyped but cut — the local
PostgreSQL environment requires test-DB creation auth that's not part
of this PR's scope.

---

## What Did Not Change

- No URL patterns removed. All five paths still resolve to the same view
  functions; only the view bodies changed.
- No view function deletions. `ai_agents_visualization`,
  `activity_monitor`, `ai_building_products` (in both files),
  `view_shared_project`, `unified_intelligence_dashboard` all stay.
- No work on the broader dormant-module list. `sports_betting/`,
  `agents/urls_deployment.py`, `intelligence/urls_ai_jobs.py`,
  `revenue/models.py`, `ai_core/intelligence/{monitoring_dashboard,testing_suite}.py`,
  `frontend/components/generated/`, stale `reports/*.json`, and the
  `templates/{agents,content,invoices}/.gitkeep` orphans are all
  unchanged. They remain pending PR 2/3 of the deeper cleanup.
- No guardrail changes. `--inventory-advisory` flag and DOC_ONLY/CONFLICT
  thresholds are unchanged.
- The Docker subnet stash (`stash@{0}`) is preserved.

---

## Verification

```
.venv/bin/python manage.py check
→ "System check identified no issues (0 silenced)."

.venv/bin/python -m pytest core/tests/test_mounted_route_fallbacks.py -x --tb=short
→ 6 passed in 4.64s

.venv/bin/python scripts/verify_repo_guardrails.py --inventory-advisory
→ PASS summary
  - tracked generated paths: 0
  - context-kit CONFLICT findings: 0
  - context-kit DOC_ONLY findings: 4 (advisory)
```

The four DOC_ONLY findings (agent count, API count, frontend page count,
spider count) are pre-existing advisory drift from the
`docs/PLATFORM_INVENTORY.md` snapshot — not introduced by this PR.

---

## What's Next

Per the deeper review, the next two PRs (after this lands) are:

1. **PR 2 — Pure-artifact untracks (low risk):** untrack
   `frontend/components/generated/` (broken JS, zero importers),
   `reports/*.json` (13 stale 2025-10-02 files, zero readers),
   `frontend/nohup.out`, and the `templates/*/.gitkeep` orphans. Add the
   matching `.gitignore` entries.
2. **PR 3 — Annotation-only (no code-path changes):** add
   `# ARCHIVE-CANDIDATE: not mounted, not installed (Session 1110 review)`
   headers to `sports_betting/*`, `agents/urls_deployment.py` + the 5
   deployment view files, `intelligence/urls_ai_jobs.py`,
   `ai_core/intelligence/{monitoring_dashboard,testing_suite}.py`. Add a
   `revenue/__init__.py` with a comment block flagging
   `revenue/models.py` as broken (one model lacks `app_label`, app not
   in `INSTALLED_APPS`). Update `docs/audit/CLEANUP_PLAN.md` with the
   specific paths.

Both are queued behind product-side calls on the partial systems
(`ai_core/intelligence/orchestration.py` defensive-mock fallback, the
`agents/views_deployment*` bundle, the `sports_betting/` planned-app
status, and whether `revenue/models.py` should be rehomed or dropped).

---

## Files Touched

```
M  core/views_ecosystem.py
M  core/views_share.py
M  core/views_unified_intelligence.py
M  core/views_visualization.py
A  core/tests/test_mounted_route_fallbacks.py
A  docs/handoffs/SESSION_1110_MOUNTED_ROUTE_FALLBACKS.md
M  docs/handoffs/CURRENT.md
M  00-START-NEXT-SESSION.md
```
