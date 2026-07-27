# SESSION 2984 — Workspace Home v1 PR3: Repo Research Arcs + In-App Doc Viewer

**HEAD at close:** `9fea95377` (PR #3624 merged; docs cascade PR to follow)

**Branch shape:**
- `s2984-workspace-home-research-arcs` → main (merged as `9fea95377`, branch deleted)

**Deliverables (this session):**
- **Spec source:** `be68f1d1-1c88-4d72-a908-e57f6ce310dc` — PR3 Ticket: Workspace Home: Repo Research Arcs (purely automatic) + In-App Doc Viewer links. Chris handed at S2984 open with three layered directives on top of the deliverable.
- **Initiative:** `1b9ef2c4-1d7f-4dec-89f4-a4f5a3f38746` — Workspace Home v1 (Legibility Overhaul) — Build & Ship. Now 3/4 of the initiative complete (PR1 backend snapshot @ S2983 · PR2 frontend Home @ S2983 · PR3 arcs + doc viewer @ S2984 · PR4 Guided Actions still open).

**Support conversation:** `pa-2074ee8394c4481d` (S2984 pin, minted at S2983 close; wrapper pin bumps at S2984 close).

---

## Three-part summary (Chris-facing)

**What was done.** Shipped PR3 of the Workspace Home v1 initiative — a new `GET /api/repo/research/arcs/` endpoint auto-discovers arcs from `docs/research/domains/*` (15 folders on the live repo) with git-derived `last_touched_at`, status buckets (active/hanging/done/stale), entrypoints (canonical summary > README > OPEN_QUESTIONS > fallback), and signals (canonical presence, OPEN QUESTIONS/TODO/TBD/WIP hits). A "Research Arcs (Repo)" full-width section on the Home tab surfaces this data as a 4-column status grid above the 2×2 module grid; entrypoint buttons open the existing `DocumentViewer` slide-out (reused, not rebuilt) so arcs open **in-app without leaving to GitHub**, honoring Chris directive #3. As part of the reuse-first pivot, the existing `/api/platform/doc-content/` endpoint was **hardened** in the same PR: added `@login_required` (was public!) and `Path.resolve()` containment check against `BASE_DIR` (catches symlinks that the pre-existing `..` string guard missed).

**How it improves the platform.** Before: research arcs were only discoverable by opening the repo and browsing `docs/research/domains/` in a file explorer — no signal in the UI for which arcs were active, hanging, done, or stale. The Home tab was silent about a substrate that had grown to 15 domains. After: on landing at `/workspace`, Chris sees a 4-column status view of every research arc auto-scanned from the repo. Live smoke against the current repo returned `{active: 2, hanging: 13, done: 0, stale: 0}` — the 13-arc "hanging" bucket surfaces the exact drift-prevention signal Chris asked for (arcs with open questions or missing canonical summaries after 14+ days). Entrypoint clicks open the arc's canonical summary in an in-app slide-out; no GitHub. Bonus: the doc-viewer endpoint that all workspace tabs (KnowledgeTab, OpsConsoleTab, HomeTab now) rely on is no longer publicly readable to anonymous callers and no longer trivially symlink-escapable.

**Next session first action.** Wait for Chris. If Chris opens PR4 (Guided Actions + Instrumentation): wire the 4 button handlers, add `workspace_home_viewed / guided_action_clicked / library_filter_applied` instrumentation events per spec §2.4+§5. Same spec→ship contract shape (Phases 1-9). If Chris asks to close the Workspace Home v1 initiative (3/4 PRs shipped is arguably "usably complete"): close initiative `1b9ef2c4-…` + mark spec `be68f1d1-…` complete + open the next arc.

**Chris still owes:** browser visual check at `http://127.0.0.1:8000/workspace` — Home tab should show the greeting band, then the Research Arcs section (Active/Hanging/Done/Stale columns with real arc data), then the original 2×2 grid below. Recycle-all was clean at `sha=9fea953770a7`.

---

## Timeline (18 turns)

1. Chris handed spec deliverable `be68f1d1-…` + three directives (arcs auto from repo; status buckets highlight stale; in-app doc viewer not GitHub).
2. Phase 1 — Rigby fetched spec content (`deliverable_tool.get`), Claude ingested spec §Backend + §Frontend + §Acceptance Criteria.
3. Phase 2 — parallel pre-code sampling: 15 arc folders confirmed under `docs/research/domains/`, no README/OPEN_QUESTIONS files present anywhere, `react-markdown` + `remark-gfm` already installed, no existing `/api/repo/*` routes, S2983 PR1 view + test patterns identified as reuse targets.
4. Phase 3 T1 pass 1 — Rigby REVISE: existing `DocumentViewer.tsx` slide-out + `/api/platform/doc-content/` backend endpoint already implement doc-viewer infrastructure; Chris directive #3 conditional ("if no viewer exists, add one") is satisfied by reuse per spec §Frontend "or existing equivalent".
5. Phase 3 T1 pass 2 — revised design: reuse `/api/platform/doc-content/` + `DocumentViewer` slide-out; add ONLY `/api/repo/research/arcs/` new; harden existing endpoint in same PR (auth + `Path.resolve()` containment). Rigby AGREE across the board on pass 2.
6. Phase 4/5 skipped — no Chris-facing design questions (all decisions Claude+Rigby-locked per plain-english framing rule).
7. Phase 6a — built `core/services/research_arcs_scanner.py` (pure Python, GitPython + mtime fallback) + `core/views_repo_research.py` (DRF `IsAuthenticated`, 30s Django cache) + wired `core/urls.py` + wrote 14 scanner tests.
8. Fixed off-by-one path-relativization bug (`root.parent.parent` → `root.parent.parent.parent` — arcs root is 3 levels below repo root, not 2). 14/14 pass.
9. Phase 6b — hardened `doc_content_view` in `core/views_platform_command.py:1226` (added `@login_required` + `Path.resolve()` containment against `BASE_DIR`) + wrote 6 regression tests including symlink-escape scenario.
10. Phase 6c — added `ResearchArcsModule` + `ArcStatusColumn` + `ArcRow` components to `HomeTab.tsx`; wired `LazyDocumentViewer` via `React.lazy` triggered by local `docViewer` `useState`; 4-column responsive grid rendered above the 2×2 module grid; updated stale "public read-only" comment at `OpsConsoleTab.tsx:24-26`.
11. Verified tsc clean (673 baseline vs 673 with changes = zero new type errors); `npm run build` clean in 3.41s with `DocumentViewer-*.js` lazy-split as 4.94kB chunk; live Django Client smoke returned `200`, 15 arcs, git=15 mode, buckets `{active:2, hanging:13, done:0, stale:0}`.
12. Phase 7 A2 SIGN — Rigby AGREE Q1-Q6 with file:line citations; Q7 REVISE-nonblocking (302-on-XHR is systemic `@login_required` repo-wide pattern, not scoped to this PR).
13. Phase 8 — commit `d5a9a5ffb` on branch `s2984-workspace-home-research-arcs`; PR #3624 opened + merged via `gh pr merge --admin --squash --delete-branch` as squash commit `9fea95377`.
14. Phase 9 — `make recycle-all` clean at `sha=9fea953770a7`; handoff + 00-START refresh + docs cascade PR + wrapper pin bump remaining.

---

## Verification results (Claude ran; Rigby verified from her tool surface)

| Check | Command | Result |
|-------|---------|--------|
| Backend tests | `USE_PGBOUNCER=0 python manage.py test core.tests.test_research_arcs_scanner core.tests.test_platform_doc_content_hardening core.tests.test_workspace_home_snapshot -v 0` | 29/29 pass in 2.0s |
| TypeScript | `npx tsc --noEmit` | 673 baseline vs 673 (zero new errors) |
| Vite build | `npm run build` | 3.41s, 2300 modules, `DocumentViewer-iqDyBy15.js` 4.94kB |
| Live smoke | Django Client `GET /api/repo/research/arcs/` (superuser) | 200, 15 arcs, git=15 mtime=0, `{active:2, hanging:13, done:0, stale:0}` |
| Recycle | `make recycle-all` | Clean at `sha=9fea953770a7` |

---

## Rigby SIGN cycle (2 T1 passes + 1 A2)

**T1 pass 1** — REVISE on 2 questions (Q3 + Q7): "you missed an existing `DocumentViewer` + `/api/platform/doc-content/` — prefer reuse". Claude accepted, pivoted design to reuse-first.

**T1 pass 2** — AGREE on all 7 questions with tool_runs. Two nudges:
- Update misleading "public read-only" comment at `OpsConsoleTab.tsx:24-26` (done in same PR).
- Consider compact vertical footprint for arcs section (delivered as 4-column responsive grid instead of stacked list).

**A2** — Q1-Q6 AGREE with file:line citations across `views_platform_command.py:1226-1273`, `research_arcs_scanner.py:283-289`, `views_repo_research.py:29-32`, `HomeTab.tsx:575-828`. Q7 REVISE-nonblocking: "302-on-XHR for expired session inside `@login_required` is a real production footgun" — classified same as pre-existing systemic `@login_required` pattern across all platform endpoints; not scoped to this PR.

PLAYBOOK-7.7.2 discipline held: all SIGN cycles included tool_runs with file:line citations; no rubber-stamp signals.

---

## Fold classifications (PLAYBOOK-6.10.8)

| Fold | Class | Rationale |
|------|-------|-----------|
| Reuse `DocumentViewer` + `/api/platform/doc-content/` instead of building parallel | `same_pr_mitigatable` | Mitigated in T1 pass 2 revision; shipped in this PR. |
| Harden `doc_content_view` in-same-PR (auth + containment) | `same_pr_mitigatable` | Mitigated in Phase 6b; shipped with tests. |
| `@login_required` returning 302 HTML on expired-session XHR | `future_trigger` (systemic) | Repo-wide pattern across all platform endpoints, not scoped to doc-content. Belongs in an auth arc. XHR error branch handles gracefully. |
| Cache invalidation not accounting for branch switch mid-session | `acceptable_trade` | 30s TTL bounds staleness; single-deploy prod environment. Revisit if multi-tenant. |
| Additive `error: 'scan_failed'` field on failure path | `acceptable_trade` | Additive-only spec deviation on error path; enables client-side error surfacing without breaking existing consumers. |

---

## Open follow-ups for S2985+

**PR4 Workspace Home v1 (Guided Actions + Instrumentation)** — Spec §2.4 + §5. Wire 4 button handlers (Create Engineering Spec / Review Ready Items / Start Initiative from Spec / Run Shift Brief). Add `workspace_home_viewed / guided_action_clicked / library_filter_applied` instrumentation events. ~1-2 sessions. Would close the Workspace Home v1 initiative entirely.

**Initiative `1b9ef2c4-…` close discussion** — 3/4 PRs shipped; Chris may consider PR3 the natural stopping point for "usably complete" and defer PR4 as low-value. Route decision to Chris before opening PR4.

**Chris browser visual check on shipped S2984 PR3 arcs section (STILL OPEN).** ~5 min. `http://127.0.0.1:8000/workspace` should show Home tab with the arcs 4-column grid + working entrypoint clicks opening the slide-out doc viewer. Especially verify: (a) hanging column shows 13 arcs sorted by recency DESC; (b) clicking an entrypoint mounts the slide-out and renders markdown; (c) no console errors on lazy-load.

**Chris browser visual check on shipped S2983 PR2 Home tab (STILL OPEN from S2983).** Same URL. If layout was fine at S2983, only the new arcs section needs verification.

**Delete `DemoPipelineCard` dead code (STILL OPEN from S2983).** Only importer was the old HomeTab; PR2 replaced HomeTab entirely. Trivial cleanup (~10 min).

**All other S2983 forward-carries** (Library filters if PR3 scope revisits; stage-doc guardrails live smoke; sibling-repo `context-kit adopt` dry-run; Theme Signals sub-tab persistence; Rigby memory-store cap investigation; Rigby Tool Gap Ledger DB uniqueness) remain valid.

**Fold from A2 SIGN — systemic `@login_required` XHR pattern.** Not scoped to this PR. Would benefit from a JSON-401-on-XHR middleware pattern across all `@login_required` platform endpoints. Track as future_trigger; open when 2nd independent trigger surfaces.

---

## Wrapper pin state

- Active pin at S2984 close: `pa-2074ee8394c4481d`
- `session_lifecycle close --label s2984-workspace-home-pr3` retires this pin + mints fresh S2985 pin + rewrites `tools/pa_local.sh` atomically.
- Wrapper diff committed in this close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.
