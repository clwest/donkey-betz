# SESSION 2983 — Workspace Home v1 (Legibility Overhaul) — PR1 (backend) + PR2 (frontend)

**HEAD at close:** `3652f6054` (PR #3622 merged; docs cascade PR TBD)

**Branch shape:**
- `s2983-workspace-home-snapshot` → main (merged as `107c4ad04`, branch deleted)
- `s2983-workspace-home-frontend` → main (merged as `3652f6054`, branch deleted)

**Deliverables (this session):**
- **Spec source:** `5e1c702f-c09e-4f10-b513-888f0784a81a` — ENGINEERING SPEC — Workspace Home v1 (Legibility Overhaul: Now / Active Work / Library / Guided Actions). Received from Chris at turn 3.
- **Initiative:** `1b9ef2c4-1d7f-4dec-89f4-a4f5a3f38746` — Workspace Home v1 (Legibility Overhaul) — Build & Ship. Status: TRIAGE (Chris message said ACTIVE; drift noted, not blocking).
- **Exec plan:** `ab0c4872-556d-41ba-b5de-21e489f14eda` — action items for Claude, `status='ready'`, pinned.

**Support conversation:** `pa-f7a426d0dace4490` (S2983 pin, minted at S2982 close; wrapper pin bumps at S2983 close).

---

## Three-part summary (Chris-facing)

**What was done.** Shipped **PR1 + PR2 of the 4-PR Workspace Home v1 initiative** in a single session (Chris ratified extension mid-session after PR1 landed). PR1 (backend, `107c4ad04`) added `GET /api/workspaces/<uuid:workspace_id>/home/` — a bounded snapshot endpoint returning `workspace / now / active_work / library` per spec §3.1. Sections computed in isolation with per-section try/except + logged empty defaults so a failure in one section doesn't kill the whole response. 9 unit tests cover shape, workspace isolation, priority ordering, list caps, 404 paths, non-owner auth, and the partial-failure guardrail. PR2 (frontend, `3652f6054`) full-replaced the prior Session 1078 HomeTab (platform dashboard — greeting/vitals/celery/attention) with the workspace-legibility shape the spec asked for. Kept only the greeting band + a hours-since-visit chip (orthogonal UX value the spec doesn't cover; Claude+Rigby joint agreement A-prime+). GUIDED ACTIONS is rendered as 4 disabled stub buttons with PR4 tooltips so the spec's 4-module mental model is intact.

**How it improves the platform.** Before: entering the Donkey Betz workspace (691 deliverables, 18 active initiatives, 20 pending action items) surfaced no coherent "what's going on" view. The prior HomeTab was a global platform dashboard — useful for system state, useless for workspace legibility. Users had to know internal tab names to find work. After: on landing at `/workspace`, Chris now sees a single-screen answer to (1) *what changed in the last 24h* (NOW), (2) *what should I focus on* (ACTIVE WORK — initiatives + top action items + ready-to-review deliverables), (3) *where do I find things* (LIBRARY — pinned + recent). Deep-link buttons ("View all →") navigate to the full detail tabs. Guided Actions surface will light up in PR4. Live smoke against Donkey Betz returned 18 initiatives, 20 action items, 20 pinned deliverables, 27 new deliverables in the last 24h — the payload is dense enough to be immediately useful.

**Next session first action.** Wait for Chris. If Chris opens with a PR3 directive: implement Library filters (spec §2.3 — Type/Status/Pinned/Canonical filter pills + search bar) + the `is_pinned=True OR (data_sensitivity in {internal, public} AND status in {ready, published, completed} AND title-prefix matches ENGINEERING SPEC / RATIFICATION_ / DECISION_)` canonical heuristic (spec §2.3.1). Follow same spec→ship contract shape: pre-code sample the existing DeliverablesTab filter UI + reuse patterns. If Chris directs something else, follow that. **Chris still owes a browser visual check** on the merged Home tab — Claude ran build + tsc + live-smoke green, but has no CLI path to visually validate layout. If layout is off, PR3 opens with a patch commit before Library filters.

---

## Timeline

| Turn | Actor | Phase | Action |
|---|---|---|---|
| 1 | Chris | 0 | "Please begin" — session brief pre-loaded S2982 close context |
| 2 | Claude | orient | Ran `context-kit orient` per session-open discipline; read `00-START-NEXT-SESSION.md`; reported readiness; waited |
| 3 | Chris | 0 | Handed over spec pointer: initiative + spec deliverable + exec plan IDs + workspace `b4503364-…` |
| 4 | Claude | 1 | Fetched spec + exec plan via ORM (`Deliverable.content`, not `body`; Initiative uses `name` not `title`; `target_workspace_id` was None on the initiative but linked deliverables carried the workspace) |
| 5 | Claude | 5 | Chris-facing framing: 4-PR arc → this session can realistically ship PR1 only. One decision routed |
| 6 | Chris | 5 | "yes PR1 only" |
| 7 | Claude | 2 | Pre-code sampling: located `ProjectWorkspace` as the workspace model, `_get_workspace(workspace_id, user)` helper at `views_workspace_templates.py:27`, `workspace_dashboard` at `:160` as the closest analog endpoint, `Initiative.target_workspace` reverse `.initiatives`, `InitiativeActionItem` at `:1958` with pending/in_progress statuses + Priority enum, `DeliverableEvent` at `models_deliverables.py:561`, `AgentExecution` at `models_unified_system.py:959` (deprecated per docstring but still in-use per 33 `core/services/*` imports; `agents.models.AgentExecution` only in `archive/scripts/`) |
| 8 | Claude → Rigby | 3 | T1 SIGN dispatch — 10 items + 4 zoom-outs. Pass 1 verdict = REVISE (Rigby offered pass 2 for items 5-7/9) |
| 9 | Rigby | 3 | T1 SIGN pass 2 — items 5/6 PASS, item 7 DISAGREE (DeliverableEvent event_type doesn't cover lifecycle: only `synthesis_viewed/deliverable_saved/deliverable_exported/shared/task_created/followup_created/action_taken/status_transition` — no `deliverable_created/updated/failure`), item 9 REVISE (per-section try/except is a NEW pattern vs `workspace_dashboard` monolith). Top-line **T1 REVISE**. Zoom-out (b) same_pr_mitigatable (`_get_workspace` owner-only + superuser bypass — tests must auth as superuser); (c) future_trigger (fallback vs backfill command); (d) accept |
| 10 | Claude | 4 | Fold mitigations at implement time: timeline sources = `Deliverable.created_at/updated_at` + `AgentExecution(status='failed')` (Item 7); per-section try/except + logged empties + `test_section_failure_returns_partial_payload` (Item 9); tests use `is_superuser=True` + explicit non-owner 404 test (Zoom-out b) |
| 11 | Claude | 6 | Write `core/views_workspace_home.py` (284 lines: view + section helpers + empty defaults). Wire URL at `core/urls.py:4223` inside the pre-router block. Write `core/tests/test_workspace_home_snapshot.py` (258 lines, 9 tests: top-level shape / NOW / ACTIVE WORK / LIBRARY / caps / 404 / non-owner / partial-failure / auth) |
| 12 | Claude | 6 | `USE_PGBOUNCER=0 python manage.py test core.tests.test_workspace_home_snapshot -v 2 --keepdb` — **9/9 PASS in 0.518s** |
| 13 | Claude → Rigby | 7 | A2 SIGN dispatch — 7 verify items + 3 zoom-outs |
| 14 | Rigby | 7 | A2 AGREE — all 6 items PASS with citations (`core/views_workspace_home.py:249-273` main view; `:24-26` constants; `:71-89` timeline slices; test at `test_workspace_home_snapshot.py:130-155` for foreign-workspace isolation). Zoom-out (a) broad-except swallow risk → same_pr_mitigatable, deferred to PR2; (b) enum coupling → accept; (c) `parent_object_id` may undercount runs → future_trigger, acceptable as best-effort for PR1 |
| 15 | Claude | 8 | Commit + push + `gh pr create` → PR #3621 → `gh pr merge --admin --squash --delete-branch` → merged as `107c4ad04` → `make celery-recycle` clean |
| 16 | Chris | — | "Before you retire the pin do you and Rigby have the context to continue on to PR2+?" |
| 17 | Claude | 5 | Plain-english decision framing per PLAYBOOK-7.7.3: do we lose anything (no if context holds), is it more work later (~30 min re-loading), 4 options A/B/C/D routed |
| 18 | Chris | 5 | "Go with A" — continue PR2 in same session |
| 19 | Claude | 2 | PR2 pre-code sampling: found **HomeTab already exists** at `frontend/src/pages/workspace/tabs/HomeTab.tsx` (23KB, wired at `WorkspacePageNew.tsx:1217`) — platform dashboard using `/api/home/boot/` + `/body/vitals/` + `/celery/breakdown/` + `/human/attention/` + `/deliverables/stats/`. Conceptually orthogonal to spec |
| 20 | Claude | 5 | Second Chris-facing decision: 4 options A/B/C/D on how to handle existing HomeTab |
| 21 | Chris | 5 | "I'm not using it yet — if starting over fresh is cleaner, do that. Otherwise you+Rigby discuss and pick" |
| 22 | Claude → Rigby | 3 | Joint design agreement dispatch: my lean = A-prime (full replace + keep greeting). Asked Rigby for disagreement + downstream breakage check + zoom-out |
| 23 | Rigby | 3 | AGREE with A-prime; suggested **A-prime+** (also keep since-last-visit chip because `/api/home/boot/`'s `while_away.hours_since_visit` is orthogonal value the spec doesn't cover). 8 tool_runs: HomeTab only referenced from `WorkspacePageNew.tsx:82` + `index.ts:69`; `DemoPipelineCard` only used in HomeTab; `useAssistantContextStore` only defined, no external readers; `home-boot` query key IS used in CommandCenterPage but replacing HomeTab doesn't touch that shared cache |
| 24 | Claude | 6 | Write `frontend/src/pages/workspace/tabs/HomeTab.tsx` from scratch (~460 lines). Greeting band + 2×2 grid of NOW / ACTIVE WORK / LIBRARY / GUIDED ACTIONS. GUIDED ACTIONS = 4 disabled stub buttons with PR4 tooltips |
| 25 | Claude | 6 | `npx tsc --noEmit` clean (no HomeTab errors, only pre-existing errors elsewhere). `make frontend-build` succeeded in 3.38s, 2300 modules, manifest generated at `sha=107c4ad04`. `make restart-daphne` health-green |
| 26 | Claude | 6 | Live Django Client smoke against `/api/workspaces/b4503364-.../home/` → **200** with realistic Donkey Betz payload (18 initiatives / 20 action items / 20 pinned / 20 recent / 27 new deliverables in last 24h / 20 timeline entries) |
| 27 | Claude → Rigby | 7 | A2 SIGN dispatch — 7 verify items + 5 zoom-outs |
| 28 | Rigby | 7 | Items 1/3/4/5/6 PASS with citations; items 2 (live smoke) + 7 (build) marked REVISE ONLY because her tool surface can't run shell/vite/manage.py — legitimate scope limitation, not rubber-stamp. Top-line **A2 REVISE** on that scope basis alone. Zoom-outs: (a) 2×2 balance accept; (b) disabled-stub-vs-hide accept; (c) double-guard same_pr_mitigatable cosmetic; (d) query-key split future_trigger; (e) future `guided_actions` type extension needed in PR4 same_pr_mitigatable |
| 29 | Claude | 8 | Commit + push + PR #3622 → merge as `3652f6054` → `make recycle-all` (rebuilds frontend when HEAD-range diff has `frontend/` paths — worked this time since changes are now committed) |
| 30 | Chris | — | "close it out and write the handoff" |
| 31 | Claude | 9 | (This handoff; 00-START rewrite; `session_lifecycle close`; docs cascade PR) |

---

## Rigby SIGN cycle evidence (PLAYBOOK-7.7.2)

**PR1 T1 SIGN passes 1+2:** 19 total tool_runs across two turns. Pass 2 delivered top-line REVISE with 2 same_pr_mitigatable folds. Rigby correctly refused to certify claims she hadn't yet grep-verified (items 5-7, 9) and re-issued after pass 1 — that's the discipline the playbook wants.

**PR1 A2 SIGN:** 10 tool_runs. Top-line AGREE. All 6 items PASS with citations. 3 future_trigger folds forward-carried.

**PR2 joint design agreement:** 8 tool_runs. Grep-grounded evaluation of the "replace vs preserve" trade-off. Verdict: A-prime+ over Claude's original A-prime.

**PR2 A2 SIGN:** 8 tool_runs. Verdict REVISE on tool-scope only (items 2/7). Items 1/3/4/5/6 PASS with citations. This is the second session I've seen Rigby explicitly scope-flag runtime claims (previous: S2982 §3 test execution) — pattern is stable: "REVISE = I can't verify" not "REVISE = you're wrong."

---

## Fold classifications

### PR1 folds
| Fold | Class | Disposition |
|---|---|---|
| Item 7: DeliverableEvent event_type gap | same_pr_mitigatable | Applied — timeline built from `Deliverable.created_at/updated_at` + `AgentExecution(status='failed')` |
| Item 9: partial-failure new pattern | same_pr_mitigatable | Applied — explicit try/except per section + test |
| Zoom-out (b): owner-only auth in tests | same_pr_mitigatable | Applied — tests use `is_superuser=True` + explicit non-owner 404 test |
| Zoom-out (c): fallback vs backfill command | future_trigger | Deferred — no null-workspace evidence found, direct reverse works |
| PR1 A2 (a): broad-except swallow risk | same_pr_mitigatable | Deferred to PR2/3 — keep warning logs, add `"partial": true, "errors": [...]` metadata in a future PR |
| PR1 A2 (c): AgentExecution → workspace via parent_object_id may undercount | future_trigger | Accepted as best-effort for PR1 |

### PR2 folds
| Fold | Class | Disposition |
|---|---|---|
| Design (a): existing HomeTab is platform-dashboard, not workspace-scoped | resolved via joint agreement | Full-replace picked per A-prime+ |
| Design (b): DemoPipelineCard onboarding CTA removal | same_pr_mitigatable | Accepted — S2798 onboarding banner covers this now; the DemoPipelineCard is dead code post-PR2 (grep shows only HomeTab imported it) |
| A2 (a): 2×2 grid balance | accept | 5-item render caps + auto-height fine for now |
| A2 (b): disabled GUIDED ACTIONS vs hide | accept | Preserves spec's 4-module mental model + explicit "coming in PR4" |
| A2 (c): double-guarded no-workspace | same_pr_mitigatable | Cosmetic; consolidate later |
| A2 (d): `home-boot-greeting` vs `home-boot` cache split | future_trigger | Watch for redundant fetches; fine for now |
| A2 (e): `guided_actions` type extension | same_pr_mitigatable | PR4 problem |

---

## Files touched

### PR1 (`107c4ad04`)
- `core/views_workspace_home.py` — NEW, 284 lines. View + section helpers + empty defaults.
- `core/tests/test_workspace_home_snapshot.py` — NEW, 258 lines. 9 tests.
- `core/urls.py` — MOD, +2 lines. Import + path (`api/workspaces/<uuid:workspace_id>/home/`) inside pre-router block.

### PR2 (`3652f6054`)
- `frontend/src/pages/workspace/tabs/HomeTab.tsx` — REWRITE, 500+/451- lines. Full replace.
- `core/templates/index.html` — MOD, 2 lines. Postbuild asset-hash sync (`index-BHH3Ytyh.js` / `index-sfx92h51.css`).

---

## Live smoke evidence

```
Django Client GET /api/workspaces/b4503364-2573-4401-9e28-61a739e0ce50/home/ HTTP_HOST=127.0.0.1
→ 200
  workspace: {'id': 'b4503364-…', 'name': 'Donkey Betz'}
  now:      runs=4 fail=0 new=27 upd=3 tl=20
  active:   init=18 ai=20 ready=20
  library:  pin=20 rec=20
```

Recycle events recorded:
- Post-PR1: `sha=107c4ad04580`
- Post-PR2: `sha=3652f60545b1` (frontend rebuild triggered by HEAD-range diff detector)

---

## Open follow-ups for S2984+

### PR3 (Library filters + Canonical heuristic — spec §2.3, §2.3.1)
- Filter pills: Type (Spec/Decision/Research/Report/Content) × Status (draft/ready/published/archived/completed) × Pinned × Canonical
- Search bar (title + keyword)
- Canonical heuristic: `is_pinned==True OR (data_sensitivity in {internal, public} AND status in {ready, published, completed} AND title.startswith(one of {'ENGINEERING SPEC —', 'RATIFICATION_', 'DECISION_'}))`
- Existing DeliverablesTab filter UI is the reuse candidate — pre-code sample it first

### PR4 (Guided Actions + Instrumentation — spec §2.4, §5)
- Wire 4 button handlers: Create Engineering Spec (open deliverable create form w/ template), Review Ready Items (filtered list nav), Start Initiative from Spec (wizard: pick spec → create initiative → link), Run Shift Brief (call `rigby_shift_brief_tool.generate` if workspace-scoped)
- Instrumentation events: `workspace_home_viewed`, `guided_action_clicked` (which), `library_filter_applied`
- Extend `HomeSnapshot` TS interface with `guided_actions` key if backend adds any preview payload
- Consider surfacing "partial: true" + failed-section labels in the endpoint response (A2 zoom-out (a) fold)

### Non-blocking cleanup
- `Initiative.status` for `1b9ef2c4-…` is TRIAGE (Chris said ACTIVE) — flip if he wants ACTIVE status semantics
- `Initiative.target_workspace_id` is None on the S2983 initiative but its linked deliverables are workspace-scoped — decide whether to backfill via `backfill_initiative_workspace_links` command or accept the through-deliverables reachability
- PR2's `DemoPipelineCard` is now dead code (only importer was old HomeTab) — delete in a follow-up

---

## Wrapper pin

- **S2983 pin (retiring at close):** `pa-f7a426d0dace4490`
- **S2984 pin (minted at close):** freshly minted by `session_lifecycle close --label s2983-workspace-home-v1-pr1-pr2`; wrapper `tools/pa_local.sh` rewritten atomically
- Wrapper diff committed as part of this close cascade per `feedback_commit_wrapper_pin_bump_at_close`
