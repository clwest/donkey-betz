# Session 1240 — Frontend rot audit (3 PRs) + AgentsPage crash defenses (2 PRs) + AgentsPage reality map

**Session window:** 2026-06-26 (Friday afternoon → late evening MDT), after Session 1239 PA tools audit close.

**Theme:** Five-PR cleanup + crash-defense arc on the frontend, plus an end-of-session AgentsPage data-wiring audit producing the Session 1241 UI-only backlog. All work landed before tomorrow morning's 07:00 MDT `morning_brief` 3rd-fire cumulative verification window (Sub-step D PRs cumulatively live for the first time).

---

## TL;DR

- **Frontend rot audit arc:** 3 PRs delete 6,891 lines of provably-dead React (Sessions 1067 + 1035 consolidation leftovers). 15 typecheck errors retired, 0 new errors. Same shape as Session 1237 P2.b core/views.py shadow-delete.
- **Live AgentsPage crash defenses:** 2 PRs defend Tools tab + Templates tab + 2 detail modals against undefined-field assumptions (`.replace`, `.toLocaleString`). User-reported crashes resolved.
- **Daphne stale-template trap discovered + memory'd:** 5-day daphne uptime + repeated `npm run build` cycles → daphne serves an `index.html` whose source no longer exists on disk. Lost ~15 min before catching it. Memory `feedback_daphne_stale_template_cache.md` added.
- **AgentsPage reality map:** 5 surfaces audited + reframed via Chris's "should it be connected?" question. Rigby cross-checked each. Five-row punch list produced for Session 1241 (UI-only focus).

**Net stats:**
- 5 PRs, all admin-merged via `gh pr merge --admin --merge --delete-branch`
- 8 files modified across all PRs (+114 / -6,898)
- 0 production regressions (frontend-only changes, typecheck baseline 242 → 227)
- 1 new memory rule + index entry

---

## Session 1240 PRs

| PR | Subject | Net | Typecheck Δ |
|---|---|---|---|
| [#2666](https://github.com/clwest/donkey-betz-platform/pull/2666) (PR-A) | DashboardPage.tsx orphan delete | -1,007 | 242→242 (0) |
| [#2667](https://github.com/clwest/donkey-betz-platform/pull/2667) (PR-B) | BoardroomPage + GovernancePage dead imports | -2,441 | 242→233 (-9) |
| [#2668](https://github.com/clwest/donkey-betz-platform/pull/2668) (PR-C) | PlatformPage + 3 transitive dead tabs + types.ts cleanup | -3,443 | 242→236 (-6) |
| [#2669](https://github.com/clwest/donkey-betz-platform/pull/2669) | AgentsPage Tools tab defensive crash guards | +6/-6 | 227→227 |
| [#2670](https://github.com/clwest/donkey-betz-platform/pull/2670) | AgentsPage Templates tab + tool detail modal toLocaleString defenses | +2/-2 | 227→227 |

**Cumulative typecheck delta: 242 → 227 errors (-15 retired, 0 new).**

---

## Frontend rot audit arc (PRs A/B/C)

### Recon (start of session)

Surveyed 61 routes in `App.tsx` by 4 signals:
1. Git last-real-feature-commit (excluding XSS/typing sweeps)
2. Line count
3. Mock/fake/TODO density
4. Dead-import status (imported but route redirects, or orphan with zero callers)

Top 4 candidates surfaced:
- **#1 (highest rot density):** BoardroomPage + GovernancePage — imported in App.tsx but routes redirect to workspace tabs
- **#2 (true orphan):** DashboardPage — exports defined but zero callers, not even App.tsx imports
- **#3 (consequential rot):** AgentsPage — 4,695 lines, last real feature commit Feb (Session 782), only post-Feb commit is XSS sweep
- **#4 (mock-data history):** NeuralOrchestraPage

### Rigby cross-check

Routed candidate list through Rigby (`pa-a2443db2e43a42dc`):
- Service context confirmed local (`platform_config_tool overview`)
- Conversation health 85/continue at audit open
- Verdict: **proceed with #1+#2 cleanup arc this session**, defer #3 (AgentsPage real refactor) to its own session, skip #4 (uncertainty).

### Guardrails cleared

Before deletion:
- `grep -rn "<BoardroomPage\|<GovernancePage\|<DashboardPage" src` → zero JSX usage
- `grep -rn "lazy.*Boardroom\|import.*GovernancePage\|...DashboardPage" src` → zero dynamic/lazy imports
- Redirect routes `/boardroom`, `/governance`, `/dashboard` confirmed still referenced by live code (CommandCenterPage:379, GovernancePage:392, etc.) — preserved

### PR-A: DashboardPage orphan delete (-1,007 lines)

True orphan, zero callers anywhere. Same shape as Session 1237 P2.c `dashboard/at_a_glance.py` orphan delete.

### PR-B: BoardroomPage + GovernancePage dead-import cleanup (-2,441 lines)

Both components imported in `App.tsx:40-41` but routes (`/boardroom`, `/governance`) redirect to workspace tabs since Session 1067 consolidation. Page components never rendered. Imports dropped; redirect routes kept.

### PR-C: PlatformPage cascade (-3,443 lines)

**Scope grew beyond original promise.** After confirming PlatformPage was dead (route `/platform` redirects to `/workspace` since Session 1035), three workspace tab files turned out to be sole-PlatformPage callers — a Session 1035 platform→workspace merge artifact:

| Deleted file | Lines |
|---|---|
| `pages/PlatformPage.tsx` | 213 |
| `pages/workspace/tabs/CommandTab.tsx` | 1,423 |
| `pages/workspace/tabs/SystemTab.tsx` | 97 |
| `pages/workspace/tabs/LearningJourneyTab.tsx` | 1,635 |

Plus symbol cleanup in `pages/workspace/types.ts` (~70 lines): `PlatformTab`, `PLATFORM_TABS`, `LEGACY_TO_PLATFORM`, `normalizePlatformTab`, `legacyTabToSubTab`, `PlatformTabConfig` — all sole-PlatformPage consumers.

Smoking gun in WorkspacePageNew.tsx:100:
```tsx
// PLATFORM_TABS/LEGACY_TO_PLATFORM no longer needed — platform merged into workspace
```
The merge was complete in code but left the dead tab files + type symbols behind.

**`/platform` redirect route kept** — `DemoHomePage:218` + `appManifest.ts` still navigate to it.

---

## AgentsPage live-crash defenses (PRs #2669, #2670)

### First crash: Tools tab

Chris clicked Agents → Tools tab and hit:
```
TypeError: Cannot read properties of undefined (reading 'replace')
  at Array.map (AgentsPage Tools tab render)
```

Crash site: `AgentsPage.tsx:2548` — `tool.tool_type.replace('_', ' ')`.

PR #2669 defended 3 sites in the Tools area:
- 2548: Tools grid → `tool.tool_type?.replace('_', ' ') ?? 'unknown'`
- 2566: Tools usage count → `(tool.usage_count ?? 0).toLocaleString()`
- 4555: Tool detail modal → `selectedTool.tool_type?.replace('_', ' ') ?? 'unknown'`

### Diagnosis fork: stale bundle vs. real bug

Independent ORM check showed **zero `AgentTool` rows with null/empty `tool_type`** (19 rows, all valid). The crash came from Chris's browser running a stale built bundle (`index-CLo74mv-.js`, mtime June 23). Defensive fix shipped anyway — right baseline regardless of trigger.

### Daphne stale-template trap (NEW Session 1240 memory)

After rebuild + bundle freshening, Chris still hit `/static/assets/index-CLo74mv-.js 404` plus CSS MIME-type errors **even after clear-site-data + hard refresh**. Diagnosis:

1. `grep -rln "<stale-hash>" .` → zero source files on disk
2. `curl http://localhost:8000/login` → HTML still references stale hashes
3. `ps -ef | grep daphne` → daphne running since **Tuesday 11 PM (5 days)**

**Root cause:** daphne caches `index.html` content in-memory even with `DEBUG=True`. Across multiple `npm run build` cycles the file on disk gets overwritten but daphne keeps serving its initial-read content. `pkill -f daphne && rm -f .daphne.pid && make start` fixes instantly.

Memory `feedback_daphne_stale_template_cache.md` added + indexed in MEMORY.md. Symptom shape captured for next time.

### Second crash: Templates tab

After daphne restart + fresh bundle, Chris hit follow-on crash on Templates tab:
```
TypeError: Cannot read properties of undefined (reading 'toLocaleString')
```

Crash site: `AgentsPage.tsx:2779` — `template.usage_count.toLocaleString()`. Same pattern as the Tools-tab crash, different field. PR #2670 defended:
- 2779: Templates grid → `(template.usage_count ?? 0).toLocaleString()`
- 4577: Tool detail modal stats grid → `(selectedTool.usage_count ?? 0).toLocaleString()`

Lines 1603 + 3807 (`execution.tokens_used.toLocaleString()`) intentionally left alone — already truthy-guarded by `if (execution.tokens_used && > 0)`.

**Lesson:** AgentsPage's `.usage_count`/`.tool_type` assumptions are spread across 4 tabs + 2 modals. Fix-one-site-at-a-time catches one crash but leaves the rest as landmines. Future field-presence defenses should grep the whole file for the receiver name rather than chase individual stack traces.

---

## AgentsPage reality map — what's actually connected

After the Templates fix landed, Chris pivoted: "I don't think there's any real data connected to a lot of the UI. Should we dig into that next?"

Time-boxed mapping pass (~45 min) over the 7 tabs + 3 top-level sections. Then a sharp reframe from Chris: **don't conflate "empty data" with "fake UI" — ask "should it be connected?"** for each empty surface.

### Live data verified (Django shell ORM probes)

| Tab | Backend rows (local) | Status |
|---|---|---|
| Directory | **23 active agents** (vs 89 in PLATFORM_INVENTORY — 60+ invisible) | ⚠️ Wired but undercount |
| Activity | 946 executions, 313 in 72h | ✅ Wired correctly |
| Tools | 19 tools all active | ✅ Wired correctly |
| Templates | 23 templates fully populated; `learning_enabled=False` on ALL 23 | ✅ Wired (flag suspicious) |
| Monitoring | feeds off AgentExecution | ✅ Likely wired |

### Empty + Rigby's "what's missing" reads

For each empty surface, write-path search (`grep "ModelName.objects.create"`) showed whether code paths exist but aren't firing.

**A. DIRECTORY 23 vs 89 — registry→DB sync gap.**
- AGENT_MAP is the code registry (83 entries)
- AgentsPage reads `UnifiedAgentTemplate` DB rows (23 only)
- An upsert command exists somewhere; either not running locally, prod-gated, or filters most agents out
- **Fix shape:** QUICK-MEDIUM (find + run the upsert, or pivot page to AGENT_MAP)

**B. DECISIONS — UI points at the wrong model.**
- `DecisionRecord` table: 0 rows, 0 writers anywhere in codebase
- BUT `auto_promote_low_risk_decisions` beat task runs every 2h on local, successfully — it operates on governance/Boardroom decision objects, NOT `DecisionRecord`
- `DecisionRecord` is "scaffold/legacy model UI is pointed at incorrectly" (Rigby)
- **Fix shape:** QUICK WIN — repoint UI at the model the boardroom flow uses. ~1 PR.

**C. DREAMS — beat tasks are maintenance not generators.**
- 3 enabled beat tasks: `cleanup-stale-dreams`, `dream-daily-surfacing`, `maintain-dream-backlog`
- `maintain-dream-backlog` ran today in 37ms — too fast to have created dreams (housekeeping only)
- AgentDream creation gated on **upstream initiative triggers** (`tasks_initiatives.py:907`, td_handlers, mgmt commands)
- No initiatives → no dreams → empty sidebar
- **Fix shape:** MEDIUM — trigger one initiative cycle to populate, OR find why initiatives aren't firing locally

**D. CHANNELS — missing publisher hook. (Chris: "don't delete this — inter-agent collaboration vision still on roadmap")**
- 5 writer paths exist (`slack_consumer`, `project_deployment`, `universal_integration`, views/agents.py user CRUD)
- ALL are user-initiated entry points — NOT "agent execution emits to channel"
- Rigby's design read: **should be an event-stream projection** — AgentExecution started/completed/failed + deliverable created + initiative status change → routed into channels by family/desk/workspace
- Missing piece: a publisher hook layer that listens to runtime events and writes channel messages
- **Fix shape:** REAL ARC. Multi-PR. Design session first.

**E. LEARNING — feedback-processing not firing + instrumentation layer missing.**
- `LearningInsight` has 2 writers in `models_feedback_processing.py` (lines 257, 314) but no rows locally — likely feedback-processing signal not firing, or filter conditions blocking
- `AgentLearningSession` + `AgentCollaboration` have **zero writers anywhere** — pure scaffolds
- Rigby's design read: AgentLearningSession = durable "learning episode" (what failed, what changed, outcome); AgentCollaboration = cross-agent edges (review/edit/use of another agent's artifact)
- Missing: instrumentation layer listening to review/feedback/deliverable events
- **Fix shape:** REAL ARC. Multi-PR. Design session first.

### Synthesis for Session 1241

Chris's framing: "all 4 of these things are features that we had built but I don't know what we are missing to achieve it." Treat all 5 as **wiring archaeology**, not feature/delete decisions.

Recommended attack order (Chris-discretion):
1. **B (Decisions repoint)** — quick win, validates the playbook in one PR
2. **A (Directory sync)** — visibility bug, restores 60+ invisible agents to the page
3. **C (Dreams trigger)** — fire one initiative cycle to populate the sidebar
4. **D, E** — design sessions first, multi-PR each (defer past S1241)

---

## Active conversation at S1240 close

- **`pa-a2443db2e43a42dc`** — final health: **60 / suggest_fresh** (turn_count=21, 5 topics, 21h duration). Rotation triggered correctly at session close.
- **`pa-634b8fef344d4af2`** — fresh conversation created via `session_tool action=create_fresh` titled "Session 1241 — AgentsPage reality reconnect (UI-only focus)". Seeded with the 5-surface punch list + S1240 close summary via `carry_forward_summary`. **This is the pinned conversation for S1241.**

`tools/pa_local.sh` updated to point at `pa-634b8fef344d4af2`. Previous pin retired.

---

## Worker / infra state

- **No backend code touched.** All Session 1240 changes are frontend-only (React deletions + crash guards) + 2 doc files (handoff + memory).
- **No new `@shared_task`.** No celery worker restart needed.
- **No PeriodicTask changes.** Beat unchanged.
- **Daphne restarted twice** during the session (once for stale-template fix, once after PR #2670 merge + rebuild). Currently fresh as of ~17:45 MDT.
- Bundle current: `index-DvjPdujY.js` (sha 2eae26d5).

---

## Chris-side carryover into Session 1241

Unchanged from Session 1239:
- Anthropic credit refill at https://console.anthropic.com/billing
- CI billing still failing — all 5 Session 1240 PRs admin-merged via `--admin`

---

## Operational invariants added Session 1240

- **Frontend rot signal pattern locked in:** route consolidation arcs (Session 1067, 1035) leave page components + transitive helpers behind. Future rot audits should grep `<PageName>` JSX usage + `import.*PageName` for dead-import detection, plus check `App.tsx` for redirect-only routes.
- **AgentsPage field-presence assumptions widespread:** `.usage_count`, `.tool_type`, similar fields assumed required across 4 tabs + 2 modals. Future hardening on this page should grep for field name, not chase individual stack traces.
- **Daphne stale-template trap:** long-uptime daphne caches `index.html` content across rebuilds. Symptom: server returns hashes that don't match any file on disk. Fix: daphne restart (memory rule).
- **AgentsPage reality map exists as Session 1241 entry point:** 5-surface punch list (Directory, Decisions, Dreams, Channels, Learning) with Rigby's "what's missing" reads. Channels explicitly preserved per Chris's vision.

---

## Memory updates Session 1240

- **NEW:** `feedback_daphne_stale_template_cache.md` (long-running daphne + rebuilds → stale HTML served; fix is daphne restart). Indexed in MEMORY.md after the celery PID cache entry.
