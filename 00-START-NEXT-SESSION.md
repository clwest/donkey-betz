# Next Session — Start Here

---

## ⚠️ READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP ⚠️

**Session 1083 burned an hour because Claude Code sent every `pa_chat.py` call to production Rigby by mistake.** Chris caught it because he wasn't seeing any of our activity in his local ChatUI — our "smoke tests" were returning production data (826 deliverables, 10 signal clusters) while the local stack had different numbers (1041 deliverables, 21 clusters).

### The trap
`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. If you don't override `PA_API_URL`, every call goes to prod. Every. Single. Call.

### The `.env` file has the WRONG token for LOCAL
`.env` has `PA_API_TOKEN=0256880456bb65533c759cc02c62160ce1a72444` — that's the **production** token. If you use it, prod Rigby will accept it.

### The correct LOCAL invocation (memorize this)
```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=19f3b711b2b1995255c5cc0e4182e085423c6557 \
.venv/bin/python tools/pa_chat.py "message" --conversation pa-3a0db697c2fd
```

- **LOCAL URL:** `http://localhost:8000`
- **LOCAL token:** `19f3b711b2b1995255c5cc0e4182e085423c6557` (different from .env)
- **LOCAL conversation:** `pa-3a0db697c2fd` (exists on both instances — they're separate conversations with different histories, but Chris can see the LOCAL one in his ChatUI, NOT the prod one — he has no way to search chat IDs in the UI)

### How to verify you're LOCAL before any real work
Ask Rigby to run `platform_config_tool overview` and confirm the response includes:
- `service_context: local`
- `backend_url: http://localhost:8000`
- `railway_environment: local`

If you see `service_context: production` or any railway URL, you're on the wrong instance. Stop, switch, and replay any work that needs to happen locally.

### Why this matters more than usual
- Chris runs the LOCAL stack for development and watches his LOCAL ChatUI
- He can see new conversations in his sidebar, but cannot search by conversation id
- If our pair-mode chats are going to prod, Chris sees NOTHING in his UI and thinks we're idle
- Also: any destructive actions via pa_chat tools (deliverable deletes, agent blocks, beat changes) go to the WRONG instance

**Before your first `pa_chat.py` call each session, run the LOCAL invocation once and visually verify Rigby's response mentions `local`.** Don't trust conversation IDs to tell you which instance — both have the same IDs.

---

**Date:** April 15, 2026 (end of Session 1083 — ML isolation marathon)
**Previous Session:** Session 1083 Marathon — **11 PRs merged**, Priority B (macOS MLEngine mutex deadlock) contained after 4 prior failed attempts, 20 dead endpoints removed, 1 live NameError bug fixed, full handoff doc at [`docs/handoffs/SESSION_1083_MARATHON.md`](docs/handoffs/SESSION_1083_MARATHON.md).
**PA Conversation (LOCAL):** `pa-3a0db697c2fd` (title: *Session 1083 resume*). Lives in LOCAL instance only — there's a same-ID conversation on PRODUCTION Rigby which is a different conversation. **Always export `PA_API_URL=http://localhost:8000` before calling `pa_chat.py` locally** (default URL points at Railway production).
**Status:** Local 3-worker stack stable, default worker running ML-isolated via 7-round cumulative fix. Priority B effectively done on macOS — ResearchAgent and all other agent paths no longer trigger the `[mutex.cc : 452] RAW: Lock blocking` deadlock.

---

## 🎯 SESSION 1083 MARATHON — What Was Accomplished

This was a one-day pair-programming marathon between Claude Code and Rigby (local PA) that shipped 11 PRs and finally put down the Priority B MLEngine deadlock that had defeated 4 prior sessions.

### 11 PRs merged to main (in order)
| PR | Round | Title | Impact |
|----|-------|-------|--------|
| #1873 | 34 | Half-built frontend sweep | 32 commits, wires HowItWorks stats, fixes fallback LIARs, exposes core routes |
| #1874 | 39 | `tasks_initiatives.py:2097` agent_name NameError | Every initiative→deliverable link was silently failing via broad-except |
| #1875 | 40 | `agent_router._create_execution_record` heartbeat thread | Daemon thread writes last_heartbeat_at every 2 min until execution leaves `in_progress`. Architecturally correct — but see "Still Broken" section below |
| #1876 | 41 | ML singleton locks + 3 skip guards | Thread-safe `get_ml_scoring_engine` + `get_model_registry`, SKIP_NLP_MODELS guard on RandomForest/MLP/DistilBERT wrappers |
| #1877 | 42 | MLScoringEngine class-level lock on `_load_model` | Catches XGBoostWrapper's direct-instantiation bypass path |
| #1878 | 43 | MLPWrapper SKIP guard (third MLEngine call site) | Missed by round 41 grep — caught via log tracing |
| #1879 | 44 | 20 dead endpoints removed | Mechanical sweep of "Other Dead Endpoints" audit bucket; `manage.py check` clean |
| #1880 | 45 | XGBoostWrapper SKIP guard | Eliminated the duplicate `ml_scoring_engine Loaded` race |
| #1881 | 46 | SHAP TreeExplainer skip inside `_load_model` | SHAP's OpenMP threads were the last heavy native op in the load path |
| #1882 | 47 | **Nuclear** `ModelRegistry.get_model` skip | Returns None for every wrapper lookup on `SKIP_NLP_MODELS=1` — eliminates the entire wrapper cascade including `ml_algorithms` imports from Isolation/KMeans wrappers |
| (in #1873) | 38 | Makefile `default` worker queue reduction | Dropped `sports,ml` from default worker queues to contain deadlock before the real fix landed |

### Priority B (MLEngine deadlock) — Root cause + fix chain
**Root cause (new data this session):**
- `tasks_agents._impl_execute_agent_task` wraps `agent.route()` in `ThreadPoolExecutor(max_workers=1)` for wall-clock timeout enforcement → **2 Python threads on `--pool=solo`**
- `AgentModelRouter.AGENT_MODEL_MAP['ResearchAgent']` declares `secondary_model='lightgbm'`
- Router iterates `ModelRegistry.MODEL_CLASSES` (17 wrapper classes) calling `is_available()` on each candidate
- `LightGBMWrapper → MLScoringEngine()` loads lightgbm via `joblib.load` + creates SHAP `TreeExplainer`
- `RandomForestWrapper / MLPWrapper / DistilBERTWrapper` each instantiate `ml.core.ml_engine.MLEngine()` → sports LSTM/NN/NFL/NBA/MLB/NHL joblib loads
- `IsolationForestWrapper / KMeansWrapper` import `core.services.ml_algorithms` (FraudDetector / CustomerSegmentation) which pulls sklearn + numpy native OpenMP
- Multiple native thread pools (lightgbm, SHAP, sklearn, numpy, PyTorch MPS) all init concurrently and Abseil's process-wide `RAW: Lock blocking` fires — **freezes the entire Python process** including daemon threads

**Why 4 prior PRs failed:** they tried to fix MLEngine itself (add locks, lazy init, class-level state cache). The deadlock is not IN MLEngine — it's the CROSS-LIBRARY native mutex race between MLEngine's dependencies and ml_scoring_engine's dependencies when loaded in parallel threads.

**The fix in round 47 (nuclear ModelRegistry skip) is load-bearing.** Rounds 41-46 are defence-in-depth — they still help production workers that don't set SKIP_NLP_MODELS but also don't run on macOS. **Local macOS workers MUST have `SKIP_NLP_MODELS=1` in env** (already set by Makefile).

### Dead endpoint cleanup (round 44)
Removed 20 backend routes + 4 frontend API methods from `core/urls.py` and `frontend/src/lib/api.ts`. Full list in the round 44 PR description. `manage.py check` passes clean. Audit bucket "Other Dead Endpoints (~33)" now down to ~13 remaining candidates for next sweep.

---

## 🚨 RESUME HERE — What Was NOT Finished (known gaps)

### 1. Round 40 heartbeat thread does NOT appear to be writing
- The daemon thread in `agent_router.py _create_execution_record` SHOULD update `last_heartbeat_at` every 2 min until the execution leaves `in_progress`
- Rigby's polls consistently show new ResearchAgent executions with `seconds_since_heartbeat == created_at age` — no periodic writes
- The 4 newest executions (1:01-1:04 MDT, on worker PID 55126) had heartbeat ages 390-560s
- **Hypothesis:** daemon thread starts but `close_old_connections()` + threadlocal DB state may be preventing writes from a detached Django thread. Or: the thread exits silently on an exception.
- **Verification needed:** add a log line at the start of `_router_heartbeat_loop` (not just on failure), restart worker, dispatch fresh ResearchAgent, check if the log appears, then check if the 2-min-tick write happens.

### 2. ResearchAgent end-to-end completion not yet observed clean
- Round 47 verified: 2+ min of zero mutex.cc, zero ml loads — worker cycling through agents normally
- But no ResearchAgent from the 6 dispatches this session has yet COMPLETED (all 4 newest in_progress, older ones watchdog-killed as zombies)
- Queue is deep (608/default + 40/agents + 174/content as of session end) — workload pressure, not deadlock
- **Next session should let the queue drain naturally then re-verify** with a fresh dispatch in a clean queue state

### 3. 24h SLO still shows ~30% wall-clock timeout rate
- As of session end: 30.49% (25/82 in 24h) — unchanged because the window still covers pre-round-47 zombies
- 1h rate is 0.0% (0/25 in last hour) — clean post-round-47
- **Should self-heal over the next 23 hours** as the pre-round-47 failures roll out of the window

### 4. CLOSE_WAIT hang (separate bug, seen mid-session)
- Default worker PID 49924 sat at 0% CPU for 15m on a Anthropic API call stuck in TCP CLOSE_WAIT state
- NOT the mutex.cc deadlock — a different bug class: HTTP client not handling remote EOF
- **Root cause file TBD** — likely in `core/services/llm_provider_registry.py` Anthropic client setup or `httpx` timeout config
- Worth a separate round when you hit it again

### 5. Dead endpoint cleanup not finished
- ~13 more candidates from the "Other Dead Endpoints" audit bucket
- Next sweep should target: partnership API routes, journey-status, diagnostic-master endpoint, remaining LLM routing variants
- Same mechanical pattern: grep frontend, delete route, `manage.py check`, commit

### 6. Round 40 architecturally correct but blocked on item 1
- If item 1 is fixed, round 40 will actually work end-to-end
- If it turns out the daemon-thread-writes-to-DB approach is fundamentally flawed on Django + Celery, a cleaner fix might be to touch heartbeat from inside `BaseAgent.execute()` main loop (single-thread, no DB connection issues)

---

## Known gotchas carried from Session 1083 (don't re-learn these)

### `pa_chat.py` defaults to PRODUCTION
- `tools/pa_chat.py:38` `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`
- **ALWAYS** prepend `PA_API_URL=http://localhost:8000 PA_API_TOKEN=19f3b711b2b1995255c5cc0e4182e085423c6557` for LOCAL calls
- Local token is in 00-START-NEXT-SESSION.md (this file), NOT in `.env` (which has the prod token)
- The conversation ID `pa-3a0db697c2fd` exists on BOTH local and prod instances — they are different conversations with different history. Verify with `platform_config_tool overview` to see `service_context: local` before trusting results.

### Abseil `[mutex.cc : 452] RAW: Lock blocking` is process-wide
- This is a Google Abseil diagnostic from the RAW lock path. On macOS it freezes ALL threads in the process, not just the holding thread.
- Daemon threads, heartbeat threads, celery control threads — all frozen simultaneously when this fires.
- That's why Round 40's daemon heartbeat thread was observed to not fire: the process was OS-locked.

### `--pool=solo` Celery workers still have 2+ Python threads
- `tasks_agents._impl_execute_agent_task` at line ~1912 does `_pool = _TPE(max_workers=1); _future = _pool.submit(_run_route)` for wall-clock timeout enforcement
- This spawns a worker thread — the main thread runs the Celery control plane, the TPE thread runs the agent
- Thread-safety bugs in singletons (ml_scoring_engine, model_registry) can race even on `--pool=solo`

### Pre-commit hook blocks direct commits to `main`
- Always create a feature branch and PR, even for one-line fixes
- `gh pr create ... && gh pr merge --squash --delete-branch` is the fast path
- Round 39 + 42 + 45 + 46 all hit this and had to reroute through a branch

### `SKIP_NLP_MODELS=1` is load-bearing on macOS
- Makefile `celery` target already sets this in the worker env
- Do NOT remove it from the Makefile without first verifying round 47's behavior
- Production (Linux Railway) workers do NOT set SKIP_NLP_MODELS=1 and continue to use MLEngine+SHAP normally — they don't hit the Abseil deadlock because Linux pthread_mutex semantics differ from macOS

---

## Next Session — PICK UP FROM HERE

### Short list of high-value targets (choose 1-2, Rigby can rank)

**A) Fix Round 40 heartbeat thread (1-2 rounds, scoped)**
- Add entry/periodic log lines to `_router_heartbeat_loop` to verify it's starting
- Restart worker, dispatch fresh ResearchAgent in a cleaned queue
- If writes work: verify `seconds_since_heartbeat < 180` for in_progress agents over 10+ min
- If not: consider the alternative of touching heartbeat from inside BaseAgent.execute() main loop

**B) Finish dead endpoint cleanup (1 round, mechanical)**
- ~13 remaining candidates from audit bucket
- Same pattern as round 44

**C) CLOSE_WAIT investigation (1-2 rounds, diagnostic)**
- Trace the `llm_provider_registry.py` Anthropic client setup
- Check httpx timeout config
- Either add timeout or retry-on-close-wait logic

**D) Neural Orchestra mock data audit (flagged in audit doc, not yet touched)**
- 14 hidden pages in audit section 5 already marked RESOLVED this session
- Section 6 mock/stale data may still need work

**E) Operator Edge Issue #1 publish flow** (user-facing launch)
- Deliverable `c73a507a` is publish-ready
- Needs Beehiiv account + soft-launch plumbing

**F) New video idea per 00-START's prior note** — not an app build, an agents+real-time-data demo

### Local stack commands
```bash
make start && make celery       # 3 workers + beat (default solo, pa solo, long_running threads, broadcast threads)
.venv/bin/celery -A core inspect ping    # verify nodes (expect broadcast/long_running/pa — default busy in solo pool)
open http://127.0.0.1:8000/     # UI (donkeyking / Crypto$donkey2026)

# Talk to LOCAL Rigby (must set env vars, pa_chat defaults to prod)
PA_API_URL=http://localhost:8000 PA_API_TOKEN=19f3b711b2b1995255c5cc0e4182e085423c6557 \
  .venv/bin/python tools/pa_chat.py "message" --conversation pa-3a0db697c2fd
```

### Branch state (end of session)
- Main is at commit `d5b0c08f` (round 47 squash merge) — `git log --oneline main -15` shows the full session sequence
- All feature branches deleted after squash-merge (8 of 8)
- Working tree has untracked files only (frontend/dist/assets pycache etc) — no pending tracked changes

---

## 🚨 REFERENCE (carried from previous sessions)

### Beat Task Status
**Enabled (77 tasks):** Body systems (10), Signal pipeline (3), Content pipeline (14), Sports pipeline (10), Infrastructure (40)
**Deliberately Disabled (155 tasks):** All 13 agent category rotations, autonomous exercises, agent conversations/dreams/thinking cycles, remediation pipeline, HiveMind sessions.
**Rule:** Do NOT re-enable agent exercises without real bounded tasks. Processing pipelines OK, unsolicited content = noise.

### Accounts
- `donkeyking` (Chris) — superuser/owner, pro tier on MentorForge, local password `Crypto$donkey2026`
- `jessica` — superuser, business side
- `jeremy` — superuser, patent lawyer

### Founder Toolkit Repos
- Landing: github.com/clwest/founder-toolkit
- MentorForge: github.com/clwest/mentorforge (Render: mentorforge-bj25.onrender.com)
- PitchDeck: github.com/clwest/pitchdeckforge
- DealFlow: github.com/clwest/dealflowtracker
- Contracts: github.com/clwest/contract-concierge

### Focus Flow (App Jam #1 — recording still pending)
- Repo: https://github.com/clwest/focus-flow (public)
- Workspace `4861b057-71b6-4eb7-aac1-72a28e91ef82`, 3 deliverables
- 60s demo script deliverable `0a4fcd45` — NOT YET RECORDED
- Outreach list deliverable `d35a22a3` — NOT YET SENT (frozen until platform audit clean)

### Operator Edge
- Landing page live at `/operator-edge` on production
- Issue #1 deliverable `c73a507a` publish-ready (6 sections drafted)
- Sponsor One-Pager `f76cbd95` created
- Beehiiv account NOT YET CREATED
- Beat schedule set for weekly Friday 6 AM MST
