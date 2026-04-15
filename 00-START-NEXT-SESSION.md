# Next Session — Start Here

**Date:** April 14, 2026 (very late)
**Previous Session:** Half-Built Features Audit — Silent failures + Dead endpoints batches 1-5 + PA UX fixes (11 commits on `docs/session-end-ml-fix-plus-audit-pivot`, nothing pushed yet)
**PA Conversation:** Last used `pa-00df63bcf289` (local). Rigby confirmed `work_tool(action='stats')` and `ops_tool(action='overview')` both work now.
**Status:** Local 4-worker stack stable on solo pool (default + dedicated pa + long_running + broadcast). MLEngine deadlock permanently fixed via class-level state cache. 12 silent-failure fixes + 47 dead routes deleted + ~1,900 lines of dead view code removed.

---

## 🚨 RESUME HERE — What Was Accomplished This Session

### 1. MLEngine mutex deadlock (permanently fixed)
Root cause turned out to be that every new `MLEngine()` instance re-ran the full torch/sklearn/MLX initialization stack, and on macOS under any threaded worker pool the concurrent library globals would re-trip `mutex.cc` RAW Lock deadlocks. Four attempts narrowed it:
  - `1a597722` SKIP_NLP_MODELS env var (still deadlocked)
  - `eaa66a7f` per-instance threading.Lock (still deadlocked — each instance had its own lock)
  - `f501d3b7` class-level lock (still deadlocked — new instances re-ran the heavy path)
  - `0645c748` **class-level state cache** (first instance loads once, every subsequent `MLEngine()` copies from cached class attrs and skips `_initialize_ml_stack()` entirely). ALSO split the `pa` queue onto its own dedicated `--pool=solo` worker so Rigby is never blocked by long COOAgent runs.

### 2. Silent-failure audit — 12 fixes across 3 batches
- **Batch 1 `6b34f737`:** `agent_llm_router._economy_if_healthy` now fail-safes to 'premium' on tracker failure; `knowledge_first_router` spider freshness narrow-excepts and logs bad `found_at`; `track_generated_image/video` replaced with ducktyped module-level helpers in `core/epa_handlers_utility.py` that work on both EPA and PersonalAIAssistant cached objects.
- **Batch 2 `9851adc3`:** `agent_monitoring` ImportError swallows replaced with WARNING logs; `agent_llm_router.log_llm_call` uses `get_or_create` so first-call-per-agent telemetry persists; `initiative_integration_service` missing current_stage row now marks initiative 'blocked' instead of reporting healthy; `experiment_learning_enhancer` risk-factor loop narrowed.
- **Batch 3 `f939ab75`:** `unified_pa_entrypoint._get_user_workspace_id` logs when workspace scoping is dropped; strategic memory ImportError now loud; `tool_dispatcher.record_op` failures logged with tool name; `workflow_engine` collects + logs missing `ImageHistory` IDs; `conversation_initiative_pipeline` content_type fallback logged.

### 3. PA UX papercuts — 2 fixes
Rigby's GPT-5.2 kept guessing natural action names that didn't exist, hitting 'Unknown action' errors and burning conversations:
- `50e57406` **`work_tool(action='stats')`**: added real stats action that returns aggregate counts (initiatives by status, action items, workflows, agent_conversations). Smoke test returned 248 initiatives / 34 workflows / 18,079 agent conversations.
- `0c0eb2e1` **`ops_tool(action='overview')`**: added bundled snapshot (version + slo_status + failure_signatures + noise_metrics) so Rigby can answer 'how's production' in one call.

### 4. Dead-endpoint cleanup — 47 routes deleted across 5 batches
| Commit | Deleted | Impact |
|---|---|---|
| `2639bbfa` | 7 legacy `/api/unified/*` routes + 2 view files | −650 lines |
| `1b7224f7` | 10 per-body-system `/api/*/status/` routes | superseded by `/api/body/vitals/` |
| `0a3548ad` | 11 `/api/ab-testing/*` routes | kept goals import alive |
| `ba3cf7ad` | 7 `/api/verify/*` + view file | −272 lines |
| `4e3c83ac` | 12 `/monitoring/*` routes + view file | −985 lines |

`python manage.py check` passes with 0 issues at every step.

### 5. Local DB + config
- Created `donkeyking` superuser on local DB (password `Crypto$donkey2026`). Previously only `admin` existed.
- Makefile now launches 4 workers with `SKIP_NLP_MODELS=1 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES TOKENIZERS_PARALLELISM=false` env vars.
- Default worker is `--pool=solo` (eliminates all threading races at the cost of one-task-at-a-time execution).
- Missing `core_failure_signature` table turned out to be a red herring — Django's `pg_tables` query was flaky, table actually exists.

---

## Next Session — PICK UP FROM HERE

### Remaining from the audit
- **~28 misc dead endpoints** still in `docs/audit-2026/HALF_BUILT_FEATURES_AUDIT.md` "Other Dead Endpoints" bucket (agent testing/debugging, spider diagnostics, partnership health, session status, dashboard health variants, learning status, interview status, LLM routing status, etc.). Same pattern applies — grep frontend, delete routes + view files, `manage.py check`, commit.
- **30+ more `except: pass`** blocks in `core/services/`. Focused on the PA/tool-dispatch hot path so far; next candidates are content pipeline, workflow engine, evidence gatherer, decision extractor, claude_code_engineer.
- **14 hidden pages** routed but not in sidebar nav — decide which should be promoted vs deleted.
- **Frontend "Coming Soon" stubs** in `ContentPage.tsx` — remove or wire up.
- **Neural Orchestra mock data** — audit flag, not yet touched.

### Actually-real concerns Rigby flagged during session
- **Spider / ingestion throughput**: only 135 SpiderData rows in last 24h despite 79 registered spiders (many producing 3-5/day). Not catastrophic but worth investigating why many spiders are near-silent.
- **SignalCluster pipeline**: only **10 records total ever** — pipeline is producing but the aggregation layer has barely run. Likely a beat-schedule gap. Separate investigation.
- **ResearchAgent**: 226 completed / 16 failed / 8 in-progress — actually healthy (92% success). Rigby's body-system vibes were alarmist.

### Branch state
- Branch: `docs/session-end-ml-fix-plus-audit-pivot`
- 11 commits on top of `8347fbb2` — none pushed. Still local only. Decide whether to PR or continue grinding first.

### Local stack commands
```bash
make start && make celery         # 4 workers + beat (solo default + pa, threads long_running + broadcast)
.venv/bin/celery -A core inspect ping    # verify nodes
open http://127.0.0.1:8000/ai-studio/    # UI (donkeyking / Crypto$donkey2026)

# Talk to local Rigby
PA_API_URL=http://localhost:8000 PA_API_TOKEN=19f3b711b2b1995255c5cc0e4182e085423c6557 \
  .venv/bin/python tools/pa_chat.py "message" --conversation pa-00df63bcf289
```

---

## 🚨 ORIGINAL PRIORITY 0 (for reference) — Half-Built Features Audit

**Before recording any more videos, work through `docs/audit-2026/HALF_BUILT_FEATURES_AUDIT.md` with Rigby running locally.** Chris wants the platform fully healthy locally before the next video, and THEN pick a new real-time-data demo.

Audit categories to knock out (from `HALF_BUILT_FEATURES_AUDIT.md`):

| Category | Count | Severity | Notes |
|---|---|---|---|
| Silent method failures (called, undefined) | 2 critical + 10+ high | CRITICAL | `track_generated_image/video` on wrong class; `get_coleadership_opinion` pattern |
| Broad `except: pass` in critical services | 100+ | HIGH | Worst 6 fixed prior session; `agent_llm_router.py`, `agent_monitoring.py`, etc. remain |
| Dead API endpoints (backend wired, frontend never calls) | ~75 | MEDIUM | Verification/testing system (7), plus many more — wire them up or delete |
| Orphaned Celery tasks | 3 dead + 4 blocked | LOW | `remediation pipeline` permanently blocked per Session 1031 |
| Frontend stubs / "Coming Soon" | 6+ | MEDIUM | |
| Hidden pages (routed but not in sidebar nav) | 14 | LOW | |
| Frontend mock data / hardcoded values | 2 pages | MEDIUM | Neural Orchestra lineage |

**Workflow (with Rigby local):**
1. Start fresh PA conversation, tell Rigby to read `docs/audit-2026/HALF_BUILT_FEATURES_AUDIT.md` and pick 1 category to start with.
2. Claude Code + Rigby pair on it: Rigby enumerates the broken items + proposes fix order, Claude Code implements, tests locally, commits per-category feature branch + PR.
3. After each category closes, rerun the audit script (if one exists) or manually verify the fixed items. Update the audit doc with DONE markers.
4. Keep the Focus Flow outreach list (`d35a22a3`) frozen until audit is clean — don't send the demo until the platform it demos has no silent failures.
5. Once audit is clean, THEN pick a new video idea per the real-time-data / agent-orchestration angle Chris wants.

## PRIORITY 1: Pick a new video idea (AFTER audit is clean)

Per Chris's guidance: next video is NOT an app build — it's Rigby using **agents + real-time data** to produce something impressive. Candidates:
- Live Operator Edge weekly issue generation (spiders → signal aggregation → 3-agent debate → EditorAgent → PublishGate → deliverable)
- Market Intelligence Brief live (stocks desk: 154 alerts, 124 SEC filings, bull/bear debate zone)
- Signal → Initiative → Deliverable pipeline run on a single hot topic

Do NOT re-pick Pomodoro / task manager territory (Focus Flow owns it).

---

## What Was Done (April 14, 2026 — late session) — Local Celery Fix

### PR #1871: MLEngine lazy `__init__` to avoid worker mutex deadlock
- **Root cause chain (3 compounding bugs):**
  1. `MLEngine.__init__` eagerly called `_initialize_nlp_models()` which loaded DistilBERT + PyTorch + MPS device init → `[mutex.cc : 452] RAW: Lock blocking` deadlock in Celery worker parent on macOS
  2. Celery worker ran 8 days ML-deadlocked while Beat kept scheduling tasks into Redis → **332,964 stale entries in the default queue** alone
  3. Fresh workers that managed to boot got swamped draining the stale queue; PA tasks sat indefinitely behind 8 days of backlog
- **Fix:** `ml/core/ml_engine.py` — cheap `__init__` + lazy init via `__getattribute__` guard on `models`, `sport_models`, `scalers`, `user_profile`, `sentiment_analyzer`. Flag flips before init runs so attribute access inside init path doesn't re-enter.
- **Verified:** `MLEngine()` constructs in 0.67s with `_initialized=False`, fresh Celery worker boots to pingable in 1s (was never responding before), local PA chat round-trip works end-to-end.
- **Also purged:** 332k stale default queue + all other stale queues except `pa` (via `redis-cli DEL`). Fresh worker drained the backlog cleanly after that.
- **Merge note:** Needs Railway billing to clear before production deploy.

## What Was Done (April 13–14, 2026) — App Jam #1

### Focus Flow — one-prompt-to-public-repo demo (new public repo)
- **Repo:** https://github.com/clwest/focus-flow (public, default branch `main`, commit `5f07778`)
- **Stack:** FastAPI + SQLModel + SQLite (backend) / Vite + React + Tailwind (frontend) — matches `docs/topics/react-fastapi-template.md`
- **Flow:** Chris asked Rigby for an app idea → Rigby scoped Focus Flow (Pomodoro + task manager) → Claude Code scaffolded backend + frontend + README in ~90 minutes → Rigby created deliverables, outreach list, recording script → single public repo + 60s demo video pending recording
- **Backend:** 11 endpoints from Rigby's spec (health, me, tasks CRUD, start/stop session, sessions list, stats). `X-Demo-User` header auth. Seeds demo user + 3 tasks on startup. Smoke tested end-to-end.
- **Frontend:** Single-page dashboard (task list + detail/timer/history), 3 presets (25m/50m/1m-demo), client-side countdown, live stats header, dark theme. Prod build 148 KB JS / 48 KB gzipped.
- **Workspace:** Claude–Rigby App Jam - Workspace 2 (`4861b057-71b6-4eb7-aac1-72a28e91ef82`)
- **Deliverables shipped (in workspace):**
  - `5c06002f-ecb7-4804-9baa-9b67f773d1ba` — Focus Flow — App Jam Starter (README + acceptance checklist + pre-recording checklist + repo URL)
  - `0a4fcd45-f153-4da9-9782-452825d4a6c9` — Focus Flow — 60s Recording Script (Chris POV: "I asked Rigby for an app idea, she and Claude Code did everything else")
  - `d35a22a3-47ce-43c7-bdf0-1a205da49edd` — Focus Flow — Video Outreach List (8 verified prospects)

### Rigby tool verification + outreach research
- **Why:** Chris suspected Rigby's tools were hung / broken during prospect research; real issue turned out to be Rigby's placeholder-pattern behavior (from memory `feedback_rigby_deliverable_content.md`), not tooling.
- **Verified working:** `web_search` (Serper API, ~900 ms avg), `deliverable_tool` (`list`/`detail`/`create`/`update`/`append`), `intelligence_tool`. No hangs, no broken endpoints.
- **Root cause of earlier "detail fetch returned list":** GPT-5.2 sent `action='list'` (default) instead of `action='detail'`. Code in `core/services/td_handlers_agents.py:1358` handles `detail` correctly. Fix = tell Rigby to pass `action='detail', id=<uuid>, full=true` with nothing else set (the smart-inference on `td_handlers_agents.py:1173` flips `list → create` when `title+content` present).
- **Unblock pattern that worked:** Claude Code seeded first 3 prospects using its own `WebSearch`, then handed them to Rigby as a table template with instructions to do the remaining 5 one row at a time, with `web_search` per row, and to mark unverifiable buckets as `NO VERIFIED CANDIDATE` rather than invent. Matches `feedback_rigby_deliverable_content.md` rule.
- **Outreach list outcome:** 8-row table with 7 verified prospects (Peter Steinberger, Theo Browne, swyx, Ben Tossell, Pieter Levels, AgentOps, Fireship) + 1 intentional `NO VERIFIED CANDIDATE` for the Show HN / dev-rel bucket after 3 failed searches. Repo URL embedded 9+ times in deliverable. Final length 3,964 chars.

### What Was Done (April 9–12, 2026) — 2 PRs Merged Prior Session

### PR #1867: Operator Edge Landing Page + Subscriber API
- `NewsletterSubscriber` model with email, name, source, UTM tracking, referral codes
- `POST /api/newsletter/subscribe/` — public, no auth, dedup + re-subscribe handling
- `GET /api/newsletter/count/` — public subscriber count for social proof
- `/operator-edge` public route (no login required) with:
  - Hero section, email signup form, 6 feature cards (Top Signal, What Broke, Autopilot Move, Cost Watch, What Changed, Deep Dive)
  - Platform stats (79 spiders, 218 agents, 3 reviewers, 72h freshness)
  - Audience targeting (SREs, AI Product Leads, Founders & Builders)
  - Dark theme, indigo/emerald gradient branding, UTM capture
- Migration 0326 applied on Railway

### PR #1868: Newsletter Auth Bypass
- Added `/api/newsletter/` to auth middleware `PUBLIC_PATHS`
- Newsletter endpoints were returning 401 — now publicly accessible
- Smoke tested on production: subscribe + count both working

### Rigby: Issue #1 Validation + Publish Prep
- Found Issue #1 deliverable (`c73a507a`) on production
- Validated against Template v1 — identified 6 missing sections
- Drafted all missing sections: Top Signal, What Broke, Autopilot Move, Cost Watch, What Changed, Forward CTA
- Added sponsor slot placeholder with UTM tracking template
- Created 3 subject line options
- Updated deliverable with publish-ready markdown
- Created Sponsor One-Pager deliverable (`f76cbd95`) for outreach

### Patent Strategy Discussion
- 12 patent disclosures already written (Disclosures A-L) + 4 executive summaries
- Strongest candidates: Claims-based deliberation (D), Structured debate + decision enforcement (F), Signal-to-initiative provenance (G)
- Strategic opportunities: licensing revenue, competitive moat, partnership leverage, valuation impact, PaaS possibilities
- Jeremy (patent lawyer, superuser account) ready to move forward

---

## PRIORITY 1: Claude–Rigby App Jam #2 (NEXT SESSION GOAL)

Fresh session kicks off with: **Chris asks Rigby for a new app idea, Rigby + Claude Code build it end-to-end, ship public repo, record a second demo video, fire the Focus Flow outreach list at the same time.**

Pattern to replicate from App Jam #1:
1. Fresh PA conversation, ask Rigby for a scoped MVP (problem statement, acceptance criteria, 10–12 endpoints max, demo-able in 60s).
2. Claude Code scaffolds a new sibling repo under `~/development/<app-name>/` using React+Vite+FastAPI template (NOT Next.js — see `feedback_stack_preference.md`).
3. One public GitHub repo with README + acceptance checklist + run instructions.
4. Rigby creates 3 deliverables in a fresh App Jam workspace: starter+checklist, 60s recording script (Chris POV), outreach list (8 prospects, same format as `d35a22a3`).
5. Record + publish, then fire DMs.

**Do NOT re-pick Pomodoro/task-manager territory** — Focus Flow already occupies that slot.

**Guardrails for Rigby (from App Jam #1 lessons):**
- She defaults to "report progress, wait for guidance" when research is ambiguous. Unblock by seeding 2–3 rows yourself and handing her the pattern.
- Smart-inference on `deliverable_tool` flips `action=list → create` whenever `title+content` are both passed. For detail reads, send ONLY `action='detail', id=<uuid>, full=true`.
- For research, tell her to call `web_search` **per row**, not once for the whole list. Require `NO VERIFIED CANDIDATE` when a bucket comes up empty instead of fabricating.

## PRIORITY 2: Focus Flow Follow-through

- Record the 60s demo (script is `0a4fcd45` in workspace `4861b057`).
- Fire DMs from outreach list (`d35a22a3`, 8 prospects, 7 verified).
- Optional polish: `/api/seed/preview` route, deploy preview (Vercel/Render), PREP.md committed to repo root.

## PRIORITY 3: Operator Edge Launch (Continued)

### Done
- Pipeline built and tested end-to-end
- First issue generated, validated, and publish-ready
- Landing page live at `/operator-edge` on production
- Subscriber API working (smoke tested)
- Sponsor One-Pager drafted
- Beat schedule set for weekly Friday 6 AM MST

### Next Steps
1. **Create Beehiiv account** — Rigby recommends Beehiiv over Substack for growth + sponsor revenue
2. **Publish Issue #1** — Soft-launch to seed list first, monitor 24-48h, then public push
3. **Build subscriber base** — Referral program, signup popups, social distribution
4. **Sponsor prospecting** — Use Sponsor One-Pager, target DevOps/SRE/cloud tooling companies
5. **Automate subscriber sync** — Connect Beehiiv API to NewsletterSubscriber model

## PRIORITY 2: Agent Quality Monitoring

### Remaining items
- TrendAnalysisAgent has a `NoneType.__format__` error in its trend-search tool — needs null-guard fix
- Content pipeline `content_list` default filter returns 0 items (defaults to `status='ready'` — confusing but not broken)
- EditorAgent fix needs production verification (just deployed)

## PRIORITY 3: Continue Silent Failure Stress Testing (Carried Forward)

### From the original audit
- **~75 dead API endpoints** — documented in `docs/audit-2026/HALF_BUILT_FEATURES_AUDIT.md`
- **100+ `except: pass` blocks** — worst 6 fixed, many more in `core/services/`
- **Neural Orchestra mock data** — sometimes serves fake data
- **14 hidden pages** — routed but not in sidebar nav

## PRIORITY 4: Revenue Plays (Strategy from Rigby)

1. **Operator Edge Newsletter** — Landing page live, Issue #1 ready to publish
2. **Deliverable Packages** — Bundle high-quality deliverables into sellable kits ($1.5K-$4.5K)
3. **Betting Intelligence** — 676 predictions, needs accuracy validation (sports pipeline re-enabled)
4. **Build-for-Hire** — Founder Toolkit proves capability ($8K-$25K per engagement)

## PRIORITY 5: Patent Process

- 12 disclosures ready (A-L), 4 executive summaries
- Jeremy has superuser account — coordinate with him
- Focus on Disclosures D, F, G first (most novel, broadest defensibility)
- Opens up: licensing, PaaS, partnership leverage, valuation lift

## PRIORITY 6: Backlog (Carried Forward)

- Deploy remaining 5 apps (SellerPilot, SignalStudio, ScoutPlays, ComplianceSentinel, Ironwood)
- Content Packets UI — packet detail page showing items grouped by role
- Opportunity data quality (scoring logic needed)
- Founder Toolkit testing (MentorForge → PitchDeckForge → DealFlowTracker flow)

---

## Beat Task Status

### Enabled (77 tasks)
- Body systems (10), Signal pipeline (3), Content pipeline (14), Sports pipeline (10), Infrastructure (40)

### Deliberately Disabled (155 tasks)
- All 13 agent category rotation tasks
- All autonomous agent exercises
- Agent conversation/dream/thinking cycles
- Remediation pipeline (blocked per Session 1031)
- HiveMind sessions, multi-agent panels
- **Rule:** Do NOT re-enable agent exercises without real bounded tasks. Processing pipelines OK, unsolicited content = noise.

---

## Accounts

- `donkeyking` (Chris) — superuser/owner, pro tier on MentorForge
- `jessica` — superuser, business side
- `jeremy` — superuser, patent lawyer (account created Apr 2, never logged in)

## How to Work with Rigby

```bash
# Use existing conversation
python tools/pa_chat.py "message" --tools --conversation pa-223d084d4b9f

# Or create fresh
python tools/pa_chat.py "message" --tools

# Local
bash tools/pa_local.sh "message"
```

## Founder Toolkit Repos
- Landing: github.com/clwest/founder-toolkit
- MentorForge: github.com/clwest/mentorforge (Render: mentorforge-bj25.onrender.com)
- PitchDeck: github.com/clwest/pitchdeckforge
- DealFlow: github.com/clwest/dealflowtracker
- Contracts: github.com/clwest/contract-concierge
