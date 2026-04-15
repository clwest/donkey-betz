# Session 1083 Marathon — ML Isolation + Dead Endpoint Sweep

**Date:** April 15, 2026
**Branch merged to main:** `fix/half-built-frontend-sweep-1083` (PR #1873) + 7 follow-up PRs (#1874-#1882)
**PA Conversation (LOCAL):** `pa-3a0db697c2fd`
**Pair:** Claude Code + Rigby (local PA)
**Duration:** ~4 hours

## TL;DR

11 PRs merged. Priority B (macOS MLEngine mutex deadlock) contained after 4 prior failed attempts over previous sessions. 1 critical NameError live bug fixed in `tasks_initiatives`. 20 dead endpoints removed. 1 Makefile queue containment. 1 routing heartbeat thread added (architecturally correct but not yet verified writing to DB — see Known Gaps).

## The 11 PRs

| # | Round | Commit | Title | Rationale |
|---|-------|--------|-------|-----------|
| #1873 | 34 | `f531d380` | Half-built frontend sweep | 32-commit marathon branch from the prior session, merged after Rigby's verification of live user-facing flows |
| #1874 | 39 | `88adb573` | `tasks_initiatives:2097` undefined `agent_name` | Surfaced during post-#1873 WARN/ERROR watch — fired 3× in 3 min on local default worker. Round-27 undefined-name sweep missed it because a broad `except Exception` masked the NameError as a warning log |
| #1875 | 40 | `8c79d0b2` | Router heartbeat thread | `agent_router._create_execution_record` now spawns a daemon heartbeat loop that touches `last_heartbeat_at` every 2 min until execution leaves `in_progress`. Round 36 initialized the field but never updated it — daemon thread closes the gap |
| #1876 | 41 | `402ab922` | ML singleton locks + 3 skip guards | `get_ml_scoring_engine` + `get_model_registry` + `ModelRegistry.get_model` all got thread-safe double-checked locking. `RandomForestWrapper`, `MLPWrapper`, `DistilBERTWrapper` all got `SKIP_NLP_MODELS=1` early-return guards |
| #1877 | 42 | `5e98ad6e` | `MLScoringEngine` class-level `_load_model` lock | `XGBoostWrapper._load_model` at model_registry.py:188 instantiates `MLScoringEngine` directly, bypassing the singleton. Class lock catches ALL instantiation paths |
| #1878 | 43 | `9110a8e9` | `MLPWrapper` SKIP guard (third MLEngine call site) | Round 41's 3-wrapper grep missed this one. Log tracing caught the `MLX not available` warning firing between two SKIP lines, revealing an unguarded path |
| #1879 | 44 | `058207ce` | 20 dead endpoints removed | Mechanical sweep of `docs/audit-2026/HALF_BUILT_FEATURES_AUDIT.md` "Other Dead Endpoints" bucket. Each endpoint verified zero frontend callers before deletion. `manage.py check` clean post-deletion |
| #1880 | 45 | `987d8843` | `XGBoostWrapper` SKIP guard | Eliminated the duplicate `ml_scoring_engine Loaded` race. After this round, the log shows only ONE ml_scoring_engine load per worker startup |
| #1881 | 46 | `7b3f24cb` | SHAP `TreeExplainer` skip | Last heavy native op in `_load_model` besides joblib itself. SHAP uses OpenMP threads that contend with lightgbm's pool |
| #1882 | 47 | `d5b0c08f` | **Nuclear** `ModelRegistry.get_model` skip | After 6 rounds of individual wrapper guards the deadlock STILL fired via `IsolationForestWrapper` and `KMeansWrapper` which import `core.services.ml_algorithms` (sklearn + numpy OMP libs). Round 47 short-circuits at the registry entrypoint so NO wrapper is ever instantiated on macOS workers |
| (in #1873) | 38 | (squashed) | `Makefile` default queue reduction | Dropped `sports,ml` from the default worker's `--queues` list as immediate containment before round 41 landed. `default,agents,content` only |

## The ML isolation hunt — full story

### Round 34 (merge PR #1873)
Started the session with the open marathon branch (32 commits, 120 files). Rigby's call: **merge, contain, verify — not more whack-a-mole.** Merged cleanly after verifying live user-facing flows (deliverables list, ResearchAgent dispatch, SignalCluster pipeline).

### Round 38 — Makefile containment
First sign of trouble: default worker deadlocked on ResearchAgent dispatch within 40s of boot. `[mutex.cc : 452] RAW: Lock blocking` signature. Quick containment: dropped `sports,ml` from the default worker's queue list so ResearchAgent tasks on `agents` queue wouldn't transitively pull sports models. **Didn't fix the deadlock** — it fired again on the next restart because the agents queue path ALSO pulled ML.

### Round 39 — `tasks_initiatives.py:2097` NameError (not ML-related)
During the post-#1873 WARN/ERROR watch, caught `[INITIATIVE→DELIVERABLE] Failed to create deliverable: name 'agent_name' is not defined` firing 3x in 3 minutes. Line 2097 passed `agent_name=agent_name` to `create_deliverable()` but the name was never bound in that scope. Replaced with literal `'TechnicalDocumentAgent'` (the agent instantiated at line 2006).

### Round 40 — Router heartbeat thread
Meanwhile, Rigby's diagnosis of ResearchAgent success rate (37.5% wall-clock timeout BREACH, 11/11 failures with `last_heartbeat_at == created_at`) revealed that round 36's heartbeat-init-on-create fix was incomplete — the field was set once at create but never updated during the agent's run. Added a daemon heartbeat thread to `_create_execution_record` that writes every 2 min until the execution leaves `in_progress`, mirroring the pattern in `tasks_agents._impl_execute_agent_task`.

### Rounds 41-47 — the ML isolation cascade

This is where the session got interesting. Each round surfaced a NEW path that needed guarding:

**Round 41** (PR #1876):
- Added double-checked locking to `get_ml_scoring_engine()`, `get_model_registry()`, and `ModelRegistry.get_model()`
- Added `SKIP_NLP_MODELS=1` early-return guards to `RandomForestWrapper._get_engine()`, `MLPWrapper._get_engine()`, `DistilBERTWrapper._get_analyzer()`
- **Still deadlocked.** Log showed `ml_scoring_engine Loaded` firing twice 3ms apart — concurrent instantiation bypassing the singleton lock.

**Round 42** (PR #1877):
- Traced bypass to `XGBoostWrapper._load_model` at `model_registry.py:188` — directly does `engine = MLScoringEngine(model_type=MODEL_TYPE_XGBOOST)` instead of going through `get_ml_scoring_engine()`
- Added a class-level lock on `MLScoringEngine._load_model` to serialize ALL load paths regardless of instantiation site
- **Still deadlocked.** The class lock worked (two loads became sequential 3ms apart instead of parallel) but the deadlock fired anyway.

**Round 43** (PR #1878):
- Noticed `MLX not available` warning firing between RF SKIP and DistilBERT SKIP log lines — the 209ms gap was `MLPWrapper._get_engine()` running unguarded and pulling `from ml.core.ml_engine import MLEngine`
- Added `SKIP_NLP_MODELS=1` guard to MLPWrapper (third MLEngine call site that round 41 missed)
- **Still deadlocked.** Round 41 got 3 of 3 MLEngine callers wrong on the first grep — MLPWrapper was the one I missed.

**Round 44** (PR #1879) — pivot break
- Chris said roll all day. Rigby picked dead endpoint cleanup as a parallel productive target while we watched the deadlock verification drain
- 20 dead backend routes + 4 frontend API methods removed
- `manage.py check` clean
- Not ML-related but shipped during the session

**Round 45** (PR #1880):
- Back to the hunt. `ml_scoring_engine Loaded` was STILL firing twice (3ms apart) even with rounds 41+42 in place — because `XGBoostWrapper._load_model` creates a DIFFERENT `MLScoringEngine` instance, and the class lock serializes the load but doesn't prevent the SECOND load from happening
- Added `SKIP_NLP_MODELS=1` guard to `XGBoostWrapper._load_model` BEFORE the direct `MLScoringEngine(...)` call
- **Finally collapsed `ml_scoring_engine Loaded` to exactly ONE line.** Deadlock STILL fired ~1ms after the last wrapper SKIP log.

**Round 46** (PR #1881):
- With `ml_scoring_engine` loading only once, the remaining heavy op inside `_load_model` was `shap.TreeExplainer(self.model)` — SHAP uses OpenMP native threads for TreeExplainer init, and OpenMP pools race with lightgbm's own OMP pool
- Added `SKIP_NLP_MODELS=1` check inside `_load_model` to skip the SHAP init entirely; `self.explainer = None` is safe because scoring works without the explainer (it's for explanation metadata only)
- **Still deadlocked.** SHAP skip fired (verified in log), but deadlock appeared ~1ms later.

**Round 47** (PR #1882) — THE FIX:
- Final log trace showed the 209ms gap between `RandomForestWrapper` SKIP and `MLPWrapper` SKIP was `IsolationForestWrapper` and `KMeansWrapper` both importing `core.services.ml_algorithms` (`FraudDetector` + `CustomerSegmentation`)
- `ml_algorithms` imports sklearn and numpy at module level → native OpenMP thread pools → race with the just-loaded lightgbm pool → Abseil RAW lock fires
- **Rather than whack-a-mole guarding every wrapper**, short-circuited at the `ModelRegistry.get_model()` entry point. Returns None immediately when `SKIP_NLP_MODELS=1`. No wrapper is ever looked up, no module-level import cascade, no OMP race.
- **Clean.** Worker ran 2+ minutes cycling through SignalScanner/ArbitrageDetector/MarketAnomalyDetector with zero mutex.cc, zero ml loads, zero algorithms imports.

### Why rounds 41-46 are still load-bearing
Production (Linux Railway) workers do NOT set `SKIP_NLP_MODELS=1` — they use MLEngine + SHAP normally because Linux pthread_mutex semantics don't deadlock the way macOS does. Rounds 41-46 are defence-in-depth for any future scenario where two threads genuinely race on ML singleton init on ANY platform. Round 47 is the macOS-specific workaround that makes the environment survive at all.

## The local vs prod Rigby trap

Mid-session Chris caught that every `pa_chat.py` call was going to production Rigby instead of local. `tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. All the smoke test results Rigby had been giving me (826 deliverables, 10 signal clusters, ResearchAgent dispatches) were against PRODUCTION data, not local. Chris couldn't see our activity in his local ChatUI because our conversation was happening on prod.

**Fix for next session:** the new `00-START-NEXT-SESSION.md` has a prominent warning at the very top with the correct LOCAL invocation. Always export `PA_API_URL=http://localhost:8000` and use token `19f3b711b2b1995255c5cc0e4182e085423c6557` (the .env has the PROD token, don't use it for local work).

## Session-end state

### Git / PRs
- Main at `d5b0c08f` (round 47 squash merge)
- 8 feature branches deleted after squash-merge
- `fix/half-built-frontend-sweep-1083` branch still exists (PR #1873 was squash-merged but branch not deleted — that's fine, it's the session's home branch)
- No pending tracked changes in working tree

### Local stack
- Daphne up on :8000
- 3 Celery worker nodes (default solo, pa solo, long_running threads, broadcast threads) — beat running
- Default worker PID 55126 (as of wrap-up) was cycling agent tasks normally, no deadlock

### Queue pressure
- default queue ~608 items (beat accumulation across 8 worker restarts today)
- agents queue ~40
- content queue ~174
- long_running queue 0
- pa queue 0
- Should drain naturally over the next hour as the surviving worker processes through

### SLOs
- 1h agent wall-clock timeout rate: 0.0% (0/25) — clean post-round-47
- 24h rate: 30.49% (25/82) — still reflects pre-round-47 zombies, should self-heal over the next 23 hours

### Cost (6h window)
- $5.56 across 1865 calls
- +252% vs prior 6h — attributable to 8 worker restart cycles during debugging
- Not a concern; normal debug-session cost profile

## Known gaps (carried to next session)

1. **Round 40 heartbeat thread not observed writing** — daemon thread architecture is correct but Rigby's polls show `seconds_since_heartbeat` growing linearly on new executions (390-560s on 4 newest rows at session end). Hypothesis: `close_old_connections()` + Django threadlocal DB state preventing writes from detached threads. Fix next session by adding log lines at daemon-thread entry and verifying it actually starts.

2. **ResearchAgent end-to-end completion not yet clean-run verified** — 6 dispatches this session; all either hit the ML deadlock (rounds 1-5) or got stuck behind a deep queue after round 47. Next session should let the queue drain first, then dispatch fresh with empty agents-queue state to verify a clean run.

3. **CLOSE_WAIT hang (separate bug class)** — mid-session, default worker PID 49924 sat at 0% CPU for 15m 44s on a TCP CLOSE_WAIT state (Anthropic API connection remote-closed, Python client never read EOF). This is a DIFFERENT bug than the mutex.cc deadlock. Not fixed today. Worth a dedicated round: trace `core/services/llm_provider_registry.py` Anthropic client setup and httpx timeout config.

4. **Dead endpoint cleanup ~13 candidates remain** — from the "Other Dead Endpoints" audit bucket. Partnership API routes, journey-status, diagnostic-master, remaining LLM routing variants. Same pattern as round 44.

5. **24 stale "in_progress" ResearchAgent zombies** — created during session 1083's earlier deadlocks, currently being watchdog-cleaned at the 60-min mark. 17 `TIMEOUT_WATCHDOG_CLEANUP_ResearchAgent` signatures observed. Will finish clearing over the next hour.

## Lessons for next session

- **Pair-program with Rigby via repo_tool recon.** Rigby's grep+read_file via OpenAI function calling is faster at locating bug sites than manual Grep tool calls. Ask her for file:line targets BEFORE diving in.
- **Trust log sequences over hypotheses.** Every time I theorized about the deadlock cause, I was partly wrong until I traced the exact log sequence between known-good and known-bad lines. Round 47 came from "what happened in the 209ms gap between these two SKIP log lines?" — that question unblocked the whole thing.
- **Nuclear options beat whack-a-mole when the surface is large.** Rounds 41-46 were each correct individually but the wrapper surface (17 classes in ModelRegistry) was larger than the grep-and-guard approach could cover. Round 47 eliminated the whole cascade at one entry point.
- **Always verify you're on the right instance first.** Run `platform_config_tool overview` before any real pa_chat work. Don't trust conversation IDs.
- **The audit doc is the source of truth for what's dead.** `docs/audit-2026/HALF_BUILT_FEATURES_AUDIT.md` has buckets that are still actionable — keep nibbling at them between bigger targets.

## Pair-mode credit

This session was almost entirely Rigby-driven on target selection and verification, with Claude Code executing edits and commits. The pattern of "Rigby ranks + picks, Claude Code ships, both verify" worked well for the deep ML hunt (7 consecutive rounds of code ship → verify → find next gap). Session 1083's marathon branch pattern from the prior session scales — as long as the PA has the tools + fresh context, the pair can sustain 11+ PRs in a single session without degrading quality.
