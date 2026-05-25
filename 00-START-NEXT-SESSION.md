# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. If you don't override `PA_API_URL`, every call goes to prod. The `.env` file's `PA_API_TOKEN` is also the **production** token.

### The correct LOCAL invocation
```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=<local-donkeyking-token>      \
.venv/bin/python tools/pa_chat.py "message" --conversation <id>
```

**Before your first `pa_chat.py` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation; use that if you don't want to remember the env vars.

## SOURCE OF TRUTH

1. **`docs/PLATFORM_INVENTORY.md`** — runtime facts (counts, schedules, agents, spiders). Regenerate with `python manage.py generate_platform_inventory`.
2. **`docs/PLATFORM_WHAT_IT_IS.md`** — narrative anchor.
3. **`docs/24_7_GLOBAL_AI_APP_ATLAS.md`** — **strategy anchor**.
4. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + display rules + constraints.
5. **`docs/UDB_TRANSLATION_LAYER.md`** — audience contract + no-claims rule.
6. **`docs/specs/FLEET_CAPABILITY_MANIFEST_SPEC.md`** (v3) — engineering spec for per-app authz, Atlas-anchored.
7. **`docs/specs/FLEET_CAPABILITY_BUSINESS_SPEC.md`** (v3) — GTM framing of the same, Atlas-anchored.
8. **`docs/specs/SIGNAL_STUDIO_PAID_INTEREST_SIGNAL_SPEC.md`** — Decision 13 demand-gate spec (status: implemented, Session 1138).
9. **Archive / handoff docs** — historical unless promoted by `docs/handoffs/CURRENT.md` or this file.

Live drift checks:
- `python manage.py verify_doc_claims --only-drift`
- `.venv/bin/context-kit doctor` — **expected floor: `10 OK / 2 warnings`** (both upstream).
- `python scripts/verify_repo_guardrails.py`

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`).

## ONE-COMMAND LAUNCH — the laptop fleet

```bash
cd ~/development/infra   # private repo: github.com/clwest/infra
make up                  # 7 Docker fleet apps on fleet-net
make all                 # up + u-d-b natively (daphne + celery)
make status              # what's running + URLs
```

## CANONICAL PA / WORKSPACE NOTES

- `POST /api/pa/chat/` is the canonical Rigby endpoint.
- `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compat shims only.
- Rigby resolves `global` vs `workspace` mode from request/profile/context.
- **PA tool registration needs BOTH daphne AND celery restart.** Each celery worker loads its own tool registry. `pkill -f "daphne -b 127.0.0.1 -p 8000"; pkill -f "celery -A core"; make start && make celery`.

---

## SESSION 1138-1141 LANDED — Decision-13 + clusterer + judge-stats arc + Chris ratification

The last four sessions form a coherent measurement-instrumentation arc on top of Session 1138's Decision-13 demand-gate, capped by Session 1141's ratification pass on Jessica's 22 decisions. All four are merged to main:

**Session 1138 (F1) — paid-interest demand-gate.** `FleetPaidInterest` table + fleet-HMAC POST + `paid_interest_status` PA tool. PRs: u-d-b#2162 (`9c8425f9`), signal-studio#15 (`1e6dbb4`). Final handoff: [`SESSION_1138_F1_PAID_INTEREST_IMPLEMENTATION.md`](docs/handoffs/SESSION_1138_F1_PAID_INTEREST_IMPLEMENTATION.md).

**Session 1139 — entity-token clusterer.** Replaced the verb-keyword fallback clusterer with an entity-token one, gated behind a `cluster_method` discriminator (`legacy` / `entity_token_v1`). Pre-fix baseline: signal-studio's LLM judge rejected **112/131 = 85.5%** of upstream clusters as incoherent. PR u-d-b#2165 (`aac43d31`), follow-up evidence-URL fix `370d49ae`. Final handoff: [`SESSION_1139_UPSTREAM_CLUSTERING_QUALITY.md`](docs/handoffs/SESSION_1139_UPSTREAM_CLUSTERING_QUALITY.md).

**Session 1140 — mirror + judge-stats tool.** signal-studio mirror now persists `cluster_method` + new `/api/judge-stats` endpoint returns the LLM judge accept/reject breakdown by `cluster_method` and `pattern_type`. New u-d-b PA tool `signal_studio_judge_stats` GETs it (auth-less, `SIGNAL_STUDIO_API_URL` env). PRs: signal-studio#17 (`19dfe102`), u-d-b#2169 (`4086019d`). Also Rigby-design-reviewed mid-session: she stripped stale acceptance numbers from the LLM-facing schema (they belong in handoffs/start-here, not in the tool). Final handoff: [`SESSION_1140_CLUSTER_METHOD_MIRROR_AND_JUDGE_STATS.md`](docs/handoffs/SESSION_1140_CLUSTER_METHOD_MIRROR_AND_JUDGE_STATS.md).

**Session 1140 post-close — `$libdir/vector` pgvector blocker CLOSED.** Investigated why `signal_studio_judge_stats` was returning legacy-only rows post-deploy. Root cause traced to u-d-b's local Postgres still on plain `postgres:15-alpine` (no pgvector) while every other fleet app's Postgres uses `pgvector/pgvector:pg16` — `aggregate_spider_signals` had been failing every 30 minutes for ~2 days with `OperationalError: could not access file "$libdir/vector"`. Fix shipped in u-d-b#2172 (`3ec9e074`): swap `docker-compose.yml` image to `pgvector/pgvector:pg15` (same major → volume-compatible). End-to-end verified: 19 v1 SignalCluster rows created locally, 3 reached signal-studio's mirror, `entity_token_v1` bucket now visible in `signal_studio_judge_stats`. Volume chown side effect (UID 70→999) documented in PR body. **This closes the Session 1131 pgvector carryover** that's been on the deck for ~3 weeks.

**Session 1140 (A) — action-card pre-generation vertical slice SHIPPED.** Picked up carryover (A) and closed it in the same session via 3 coordinated PRs (Rigby reviewed every one mid-build, all merged). Curated snapshots now ship with LLM-generated action cards paired 1:1 with each cluster_pick. Curated tab → click any cluster → "Suggested Next Steps" section renders action_type badge ("AI draft" vs "Needs retry" pill), concrete steps, and outreach draft (when populated). 3 PRs: u-d-b#2174 (`1c268726`) + signal-studio#18 (`3f279730`) + signal-studio#19 (`11bee51f`). ~2300 LOC, 57 new tests, 80% real LLM cards on live smoke. Full details + Rigby's three design-review passes in [`SESSION_1140_ACTION_CARDS_VERTICAL_SLICE.md`](docs/handoffs/SESSION_1140_ACTION_CARDS_VERTICAL_SLICE.md). **This closes carryover (A)** that was queued from Session 1132.

**Session 1141 — Chris ratification deep dives on Jessica's 22 decisions.** Closed the top-priority punch list item that had been open since Session 1137. Outcome: **17 accept-as-written + 3 ratify-already-shipped + 2 with Jessica clarification redlines = 22/22 closed**. Deep dives on the 4 implementation-affecting decisions: Decision 9 (cost attribution — 3 clarifications), Decision 10 (Stripe SKU sequencing — accept), Decision 19 + F5 audit (PitchDeckForge style names — found Angel + Strategic don't map to existing code templates, retune path recommended), Decision 15a-c (GTM channels — accept). PR u-d-b#2177. Full details + draft Rigby message bouncing 4 redlines to Jessica in [`SESSION_1141_JESSICA_RATIFICATION_DEEP_DIVES.md`](docs/handoffs/SESSION_1141_JESSICA_RATIFICATION_DEEP_DIVES.md). **This closes Chris's punch list item #1.**

---

## SESSION 1143 — CURRENT ENTRY POINT

### Top-of-session goal: /docs/ corpus walk-through (Chris + Claude Code + Rigby)

Chris asked, at Session 1142 close, to spend Session 1143 going through `/docs/` together — Chris driving, Claude Code investigating, Rigby weighing in — to figure out **exactly what's in there**. No specific approach pre-decided.

**Why now:** Even after Session 1142's hygiene pass closed all numeric drift and refreshed Category A headers, the corpus is still **852 active docs, 1,163 superseded, 2 drafts, ~458 markdown files across ~30 subdirs**. Chris hasn't done a comprehensive read in a long time. Goal of Session 1143 = produce a real map of what exists, what's load-bearing vs zombie, what's redundant, what's actually trustworthy.

**Pre-staged context Session 1143 can lean on:**
- `python manage.py verify_doc_claims --only-drift` → 0 drifts (numeric claims clean)
- `python manage.py check_doc_headers --only-stale` → 0 header_lag, 9 frozen Category B docs (untouched since Session 84–1012, full list in PR #2178 body)
- `kb_tool` (Document table) is now populated: **852 docs, 14,149 chunks, 100% embedded** — Rigby can semantic-search the corpus
- `search_docs` PA tool (Session 1142, **gated on PR #2178 merge**) — chunked /docs/ retrieval with `[docs/path#chunk_id]` citations via `.rag/corpus.jsonl` (19,305 chunks, 2,017 files, refreshed 2026-05-24)
- `docs/INDEX.md` + `docs/_index.json` — auto-generated index Rigby's system prompt can reference

**Approach options to pitch Chris when the session opens** (none chosen yet — figure it out together):
- (A) Top-down by category: walk `docs/{topics,handoffs,specs,plans,cleanup,archive,audit-*,...}` and have Rigby summarize each subdir's purpose + cull/promote
- (B) By doc age: start with the 9 frozen Category B docs (`docs/AUTONOMOUS_SYSTEMS.md`, `INTELLIGENCE_SYSTEMS.md`, `MODELS.md`, `ERROR_TRACKING.md`, `DEPLOYMENT_GUIDE.md`, `PERSONA_AGENTS.md`, `docs/agents/README.md`, `GOLDEN_GOOSE_STRATEGY.md`, `SCIFI_FEATURES.md`) and decide archive vs refresh per-doc
- (C) By query-driven discovery: feed Rigby a list of platform topics and ask "which doc(s) cover X?" — surfaces what's discoverable vs orphaned
- (D) By git activity: rank docs by last-commit-age and start where activity dropped off — surfaces zombie clusters

Whatever the approach, **gate on Session 1142 PRs landing first** so search_docs is callable:
- **PR #2178** (`feat/advisor-functional-identities`) — advisor rename + Session 1142 docs hygiene + search_docs PA tool
- **PR #2180** (`fix/markdown-xss-rehype-sanitize`) — ReactMarkdown rehype-sanitize on 10 sites
- **PR #2181** (`fix/pa-cache-race`) — `get_unified_pa` threading.Lock + clear_pa_cache correctness

### Already done in the 1140 post-close session

- ✅ Daphne + every celery worker restarted (`signal_studio_judge_stats` registered, smoke-tested end-to-end at 11ms).
- ✅ signal-studio docker rebuilt with `--force-recreate` (mirror got `cluster_method` column + `/api/judge-stats` endpoint).
- ✅ pgvector unblocked via u-d-b#2172 (`3ec9e074`); `aggregate_spider_signals` now runs against working SpiderData queries.
- ✅ First-pass aggregation produced 19 v1 SignalClusters; 3 reached signal-studio's mirror tagged `entity_token_v1`.
- ✅ Carryover (A) action-card pre-generation shipped end-to-end (3 PRs merged: u-d-b#2174, signal-studio#18, signal-studio#19). Curated snapshots now ship with LLM action cards rendering inline; 8/10 real LLM, 2/10 fallback at current variance. See [`SESSION_1140_ACTION_CARDS_VERTICAL_SLICE.md`](docs/handoffs/SESSION_1140_ACTION_CARDS_VERTICAL_SLICE.md).

### FIRST THING — Read the live rejection rate

Both preconditions for the Session 1139 acceptance test now hold:
1. ✅ Beat-aggregation has produced real v1-tagged rows (3 in signal-studio's mirror, more accumulating as beat fires every 30 min).
2. ✅ Working pgvector — local stack now serves SpiderData queries.

Wait for signal-studio's auto-summarize worker to judge the new v1 rows (they land as `raw` and the worker promotes them to `summarized` or `rejected` on its next cycle), then ask Rigby:

```text
signal_studio_judge_stats with days=7
```

Read `by_cluster_method.entity_token_v1.rejection_rate`. If the bucket is still tiny (n < 20), wait another aggregation cycle or two — a 1-of-3 rejection looks like 33% but isn't a real signal.

**Acceptance bar (Rigby-locked, do not edit without re-anchoring):**
- **< 30%** → victory. Queue legacy bulk-archive (see SECOND).
- **30–60%** → partial. Decide whether Option B (embedding-based clustering) is worth the spend.
- **≥ 60%** → close to the 85.5% baseline. Escalate to Option B.

**Don't read a rejection rate from a < 20 sample.** Wait for accumulation.

Fallback paths if Rigby loop is unavailable:

```bash
# Direct curl against signal-studio:
curl -s "http://localhost:8007/api/judge-stats?days=7" | jq .by_cluster_method

# Or docker exec into Postgres:
cd ~/development/signal-studio
docker compose exec -T signal_studio_postgres psql -U signalstudio -d signalstudio -c \
  "SELECT cluster_method, summary_quality, COUNT(*) FROM signal_clusters
   GROUP BY 1, 2 ORDER BY 1, 2;"

# Or check u-d-b upstream directly (where new v1 rows land first):
.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup()
from core.models_signal_intelligence import SignalCluster
from django.db.models import Count
for row in SignalCluster.objects.values('cluster_method').annotate(n=Count('id')):
    print(row)
"
```

### SECOND — Conditional on FIRST landing < 30%: legacy bulk-archive

Only after 7–14 days of v1 running cleanly AND the FIRST measurement says victory:

```python
# Bulk-archive eligible legacy rows. Conservative predicate: don't tie
# to judge-reject mapping on day 1 — let signal age + status carry the
# decision.
SignalCluster.objects.filter(
    cluster_method='legacy',
).filter(
    Q(status__ne='active') |
    Q(created_at__lt=<cutoff>) |
    Q(strength__lt=<threshold>),
).update(status='archived')
```

Spec the cutoff + threshold with Rigby first. Don't blanket-delete the 307 legacy rows — they're useful as a comparison baseline for the next quality regression.

### Chris's punch list (prioritized — load-bearing items first)

**Load-bearing rationale:** Item 1 (Jessica ratification) closed Session 1141; 4 clarifications now in flight to Jessica. Item 2 (ops view fork) becomes top priority. Items 3-9 are tech-queue work that's unblocked but parallel. Items 10-11 are Jessica-collab. Quick wins (item 9) can land any session.

#### 🔥 Highest-need (you specifically)

1. **~~Ratification pass on Jessica's 22 decisions~~** — ✅ **CLOSED Session 1141** (PR #2177, all 22 decisions ratified). 4 clarifications drafted as a single Rigby message in the deep-dive doc's close-out section. **Next move:** send the message via `tools/pa_local.sh` and unblock Decision 9 schema work + Decision 19 PitchDeckForge retune.

2. **Ops view fork decision** (Session 1136 PARKED — now top priority). Jessica rejected the dashboard shape ("feels complicated"). ~1360 LOC sitting on `clwest/context-kit` branch `feat/jessica-ops-view` commit `87c8ae9` — **not pushed, not merged**. Pick: kill / radical-simplify / different medium / redirect with new interview. Status: **PARKED since Session 1136**.

#### 🛠 Tech queue (you own, unblocked but parallel)

3. **Phase 0 cost-attribution SCHEMA** — `LLMCallLog.workspace` FK + daily cap + soft-degrade-to-gpt-5-mini + portfolio kill switch. **PARTIALLY unblocked by Jessica's Decision 9 + Session 1141 deep dive.** Three Jessica clarifications still pending (soft-degrade scope, hard-kill threshold, internal-spend accounting — see `SESSION_1141_JESSICA_RATIFICATION_DEEP_DIVES.md` §Decision 9). Can scaffold migrations + model in parallel; final policy locks after Jessica responds. Highest tech-queue priority because it underwrites every other Suite product's cost discipline.
4. **Contract Concierge fleet routing fix** (Q1) — architecture decision: new agent / extend `legal_doc_drafter_agent` / remove default.
5. **Signal Studio engine-side enrichment integration** (Q3) — architecture v2 question.
6. **ComplianceSentinel fleet routing** (Q4) — `security_agent` / null / skip u-d-b.
7. **Engine-mismatch resolutions** (cross-cutting C5).
8. **Atlas deviation ratification** (cross-cutting C7).
9. **~~F5 PitchDeckForge styles audit~~** — ✅ **DONE in Session 1141** (audit confirmed 4 templates meaningfully differ; surfaced that Angel + Strategic don't map to existing code templates). Follow-on Chris-side work surfaced as new item 9a below.

9a. **PitchDeckForge template retune (Decision 19 follow-on)** — Gated on Jessica's clarification re clean-template fate (retire vs rename-then-retune for Angel audience). When unblocked: rewrite `clean` → angel system prompt + slide guidance, rewrite `product` → strategic system prompt + slide guidance, rename `TEMPLATE_CONFIGS` keys, add migration for existing deck rows, update frontend selector copy (`App.tsx:307,481-484,978-989`), update `24-7-ai-global/src/lib/products.ts` Starter tier blurb when names ship publicly.

#### 🤝 Jessica-driven (collab role, not lead)

10. **F7 Stripe verification audit** on 4 Suite products — Jessica drives, needs your Stripe access (~30-60 min).
11. **Other Phase 5 audit queue** — F6 (fund operator outreach, days-weeks), #23 (Cross-Suite handoff matrix, 1-2 hr), #24 (TOS legal review, 5 min ping), #25 (Marketplace policy, 30 min review), #27 (Rigby repo audit, 5 min review).

#### ⏸ Gated / deferred (no action needed)

- **Rigby products.ts update** — fires when Decision 1 take-public trigger is met. Currently deferred.
- **SellerPilot + ComplianceSentinel Render Blueprint deploys** — ops, deferred per local-only mode (`feedback_local_only_default.md`).
- **(Y) Reject-mode flip in unified_pa_chat** — gated on 3-day clean audit telemetry post-merge. Currently in flight.

#### ⏳ Passive (in flight, no action needed)

- **v1 rejection-rate measurement** (Session 1139/1140 acceptance test) — beat cron + auto-summarize worker accumulate; read once sample reaches n≥20. **This is the FIRST THING above** — listed here so it stays on the radar.

### Sanity check before any new work

1. `cd ~/development/infra && make up`
2. `make all` (or `make start && make celery` from u-d-b)
3. `make status` — confirm 7 fleet apps + u-d-b all healthy
4. `tools/pa_local.sh "platform_config_tool overview"` — confirm `service_context: local`
5. Read [`docs/handoffs/SESSION_1140_CLUSTER_METHOD_MIRROR_AND_JUDGE_STATS.md`](docs/handoffs/SESSION_1140_CLUSTER_METHOD_MIRROR_AND_JUDGE_STATS.md) for the most recent merge state.

---

## OPERATIONAL NOTES (carry forward)

These are locked in code/tests but worth remembering when touching adjacent areas:

- **Session 1140 — `cluster_method` mirror on signal-studio side.** `signal_clusters.cluster_method VARCHAR(32) DEFAULT 'legacy'`, indexed. `_ensure_schema` ALTERs + backfills existing rows on first boot. `upsert_cluster_from_envelope` reads `envelope.get('cluster_method') or 'legacy'`.
- **Session 1140 — `/api/judge-stats?days=N` on signal-studio (auth-less).** Returns `{total, summarized, rejected, raw, rejection_rate, by_cluster_method, by_pattern_type}`. `rejection_rate` denominator excludes `summary_quality='raw'` so a backlog spike doesn't mask quality.
- **Session 1140 — `signal_studio_judge_stats` PA tool.** Calls signal-studio over `${SIGNAL_STUDIO_API_URL:-http://localhost:8007}`. Days clamped 1..90 client-side. Returns `{ok, status_code?, error?, ...endpoint_json}`. Rigby's design-review rule: tool descriptions stay evergreen — SLO numbers/baselines belong in handoffs, not in the LLM-facing schema (they go stale and bias the model).
- **Session 1139 — `cluster_method` discriminator on SignalCluster.** New rows default `entity_token_v1`; backfilled 307 legacy rows. Downstream consumers should filter on `cluster_method='entity_token_v1'` when applying any new quality bar.
- **Session 1139 — entity-token clusterer in `signal_aggregation_service`.** Requires ≥2 shared specific tokens (frequency ≥2 in window) to form a cluster. Better to miss a cluster than create a junk one. Per-pattern min size: `opportunity_window=4`, default 3.
- **Session 1139 — kill-switch.** `SIGNAL_CLUSTERER_METHOD=legacy` flips the active clusterer at worker boot. Flag both `celery-long-running` AND `celery-long-running-2` together — half-and-half leaves confusing telemetry. Typos fall through to v1 (not legacy) by design.
- **Local `$libdir/vector` pgvector blocker — CLOSED in Session 1140 post-close (#2172, `3ec9e074`).** u-d-b's `docker-compose.yml` postgres service now uses `pgvector/pgvector:pg15` (was plain `postgres:15-alpine`). SpiderData / VectorField queries work locally. **Upgrade gotcha:** the Debian-based image uses postgres UID=999 vs the alpine image's UID=70 — existing volumes need a one-time `chown -R 999:999` (full command in u-d-b#2172 PR body). Fresh `make up` against an empty volume initdb's cleanly with no manual step.
- **Fleet HMAC sign-key = SHA256(secret), not raw secret.** Saved to memory. Any new fleet client must follow this contract.
- **`init_db()` does not migrate existing tables** (signal-studio side). Schema additions need `_ensure_schema()` calls in BOTH startup paths.
- **brain_events.py is byte-identical across all 7 fleet repos.** Future event prefixes plug into the HANDLERS prefix router in `signal_ingest.py`.
- **EventSource is browser-only.** 2-hop pattern still applies: u-d-b emits → fleet backend server-to-server subscribes → fleet backend re-emits to browser.
- **Daphne + sync generator + Redis pub/sub = hang.** Use `async def event_generator` + `redis.asyncio` for any new SSE endpoint.
- **Docker rebuild gotcha.** `docker compose up -d --build` doesn't always recreate the container — use `--force-recreate`. Don't run parallel builds across 6+ repos.
- **`/api/fleet/*` paths are in `OPTIONAL_AUTH_PATHS`.** Signed-but-tokenless is the canonical fleet auth shape.
- **Django 5 `db_default` for DB-managed defaults** (Postgres sequences, `gen_random_uuid()`, `now()`). `null=True` alone makes Django pass NULL in INSERT and overrides the DB DEFAULT.
- **Session middleware can satisfy SessionAuthentication** (1132 discovery). Don't trust DRF's `successful_authenticator`. Read `Authorization` header directly.
- **`request.fleet_identity` is a dict, not an ORM row** (1132 gotcha). Use `.get("app_slug")`, not `getattr`.
- **Format is its own translation axis** — §1.2 governs vocabulary; format-fit (dashboard vs sticker vs CLI) is a separate consideration. (Session 1136 lesson.)
- **Audience interviews need "worst Monday morning" prompt** — Q1-Q6 elicit features but miss format-fit. (Session 1136 lesson.)
- **My on-the-fly rebrand suggestions can be sloppy** — Decision 12 in Session 1137 promised features that don't exist. Audit existing copy BEFORE proposing rebrand. (Session 1137 lesson, F2 execution.)
- **Vague triggers don't fire** — Decision 13's "concrete paying-interest signal" was vague until F1 spec made it specific. Numeric trigger thresholds need explicit lock. (Session 1137 lesson, F1 execution.)
- **Non-local CI doesn't block local-only merges** — Vercel preview deploys, Render builds, Railway preview deploys etc. are advisory only when the work doesn't touch them. If diff is backend-only / local-scope and a deploy-side check fails, note it once and proceed. Reinforced 2026-05-24 (Session 1140) on signal-studio#17 Vercel-failure-but-backend-only merge.

---

## CARRYOVERS (open / parked, not blocking)

### (Y) Reject-mode flip in unified_pa_chat — STILL queued

**Rigby's lock on the 3-day window**: post-merge, mainline, persistent envs. Observability starts after Chris merges the 5 PRs.

**Two paths Rigby will accept**:
- **Default path** — wait for merge + envs in mainline, then start 3-day clock. Lower risk, sharper signal.
- **Staged path** — Stage 1 (immediately) "soft deny" only when routing claim present, behind feature flag; Stage 2 (post-merge + telemetry window) "hard deny."

**Estimate**: ~half a session + 1 session of audit-sweep work if needed.

### ~~(A) Action-card pre-generation for curated~~ — CLOSED Session 1140 (3 PRs)

Shipped end-to-end via u-d-b#2174 (`1c268726`) + signal-studio#18 (`3f279730`) + signal-studio#19 (`11bee51f`). Curated snapshots now produce 10 LLM-generated action cards (≈80% real, ≈20% fallback at current variance) that signal-studio mirrors and renders inline under each curated cluster's detail view. Rigby reviewed every PR mid-build. Full details + Rigby's three design-review passes in [`SESSION_1140_ACTION_CARDS_VERTICAL_SLICE.md`](docs/handoffs/SESSION_1140_ACTION_CARDS_VERTICAL_SLICE.md).

**Spawned follow-ups (now in "Other carryovers" below):** regen scheduler for `needs_regen` rows, copy-button on outreach_draft, curated tab list-card inline preview, legacy-snapshot action backfill.

### Audit telemetry check (relevant for (Y) gate)

```bash
cd ~/development/unified-donkey-betz
.venv/bin/python manage.py shell -c "
from core.models.fleet import FleetPAChatAuditRow
from collections import Counter
from django.utils import timezone
from datetime import timedelta
since = timezone.now() - timedelta(hours=72)
rows = FleetPAChatAuditRow.objects.filter(created_at__gte=since)
print(f'audit rows (72h): {rows.count()}')
print('by auth_mode:')
for am, n in Counter(rows.values_list(\"auth_mode\", flat=True)).most_common():
    print(f'  {am}: {n}')
"
```

If bearer-only-with-claim count is 0 across all 7 fleet apps for ≥3 days post-merge, (Y) is safe to flip.

### Jessica clarifications in flight (Session 1141 close)

Four clarifications drafted in [`SESSION_1141_JESSICA_RATIFICATION_DEEP_DIVES.md`](docs/handoffs/SESSION_1141_JESSICA_RATIFICATION_DEEP_DIVES.md) §close-out, packaged as a single Rigby message. **Next move:** send via `tools/pa_local.sh` and unblock the gated tech work.

- **Decision 9** (3 redlines): soft-degrade scope, hard-kill threshold, internal-spend accounting — unblocks Phase 0 schema final lock
- **Decision 19** (1 redline): clean-template fate (retire vs rename-then-retune for Angel) — unblocks PitchDeckForge template retune

### Other carryovers

- **Action-card regen scheduler** (Session 1140 (A) follow-up) — fallback rows now land as `action_status='needs_regen'`, queryable independently of the `generated_by` audit field. A scheduler can filter on that status + retry with backoff. Needs explicit design pass (rate limit, audit, retry budget, model selection). Per Rigby: deliberate follow-on, NOT to land alongside the slice.
- **Action-card copy button** (Session 1140 (A) Rigby Q4 non-blocking) — outreach_draft block is currently monospace + preserved line breaks. Adding a 1-click Copy button tightens the loop for templates with `[Name]`/`[Role]` placeholders. Frontend-only.
- **Curated tab list-card inline action preview** (Session 1140 (A) deferred) — currently action cards only render in drill-in. A 1-line action title teaser inline on `CuratedSignalCard` would show the actionable angle without click. Separate UX scope.
- **Legacy-snapshot action backfill** (Session 1140 (A) honest-scope) — pre-1140 curated snapshots have no action_cards (the LLM cards never existed). Either run a one-off backfill via `generate_for_snapshot(snapshot_id, only_missing=False)` per old snapshot OR let time-decay carry it (new snapshots inherit the upgraded render naturally).
- **Legacy SignalCluster bulk-archive** (Session 1139 follow-up, now Session 1141 SECOND if FIRST lands < 30%) — after 7-14 days of v1 running cleanly, bulk-archive rows with `cluster_method='legacy' AND (status != 'active' OR created_at < cutoff OR strength < threshold)`. Avoid tying to judge-reject mapping on day 1.
- **v1 accumulation in progress** — as of Session 1140 close: 19 v1 SignalClusters in u-d-b, 3 in signal-studio mirror (passed strength≥0.6 emit predicate). Beat cron `*/30` will accumulate more. Auto-summarize worker on signal-studio side judges them periodically into `summarized` / `rejected`. Read FIRST when sample size ≥20 in the v1 bucket.
- **DB-dependent tests can be re-enabled** — pgvector now works locally (#2172). `test_fleet_signals_phase1.py` integration paths + curator dedup + PA-chat audit tests were parked since Session 1131 specifically because of the pgvector blocker. Separate scope from FIRST; cleanup work for a quieter session.
- **signal-studio mirror dep gap** (Session 1140 discovery) — `stripe` + `httpx` were missing from `backend/.venv` until ad-hoc `pip install`. Not committed. Future smoke-test sessions should re-pip from `requirements.txt` rather than assume venv is current.
- **Vercel preview deploy on signal-studio** — failed during Session 1140 signal-studio#17 merge. Backend-only diff couldn't have caused it; pre-existing flake or quota issue. Worth a separate look if frontend redeploys are needed.
- **Ops view fork decision** (Session 1136 PARKED) — Chris picks: kill / radical-simplify / different medium / redirect with new interview
- **Capability spec Phase 0 scaffolding** — gated on per-app intent (Session 1135 done, Session 1137 ratified Jessica side)
- **Semantic `category`** — `pattern_type` is the honest placeholder.
- **`docs/SERVICES.md` drift** — header says 320 service files; reality after 1132 is 336.
- **ai-content-studio#2** — Docker foundation PR. Back burner.
- **24-7-ai-global** — Next.js, not yet Dockerized. Surface for Rigby standalone Phase 1 (deferred per Decision 1).
- **Per-user filter at u-d-b's replay endpoint** — optional `?user_id=…` query param.
- **context-kit doctor floor:** `10 OK / 2 warnings` (both upstream).
- **`character-os`** — Another Claude Code instance may be active there. Read-only is fine; don't push PRs there. Per Atlas, Phase 4+ parked.

---

## SESSION 1131-1141 HANDOFFS

- [Session 1131 Phase 1 close](docs/handoffs/SESSION_1131_SIGNAL_STUDIO_PHASE_1.md)
- [Session 1131 Phase 2 close](docs/handoffs/SESSION_1131_PHASE_2_SIGNAL_CURATOR.md)
- [Session 1132 close](docs/handoffs/SESSION_1132_LIVE_REFRESH_AND_PA_AUDIT.md)
- [Session 1133 close](docs/handoffs/SESSION_1133_FLEET_PA_SIGNING_BACKPROP.md)
- [Session 1134 close](docs/handoffs/SESSION_1134_CAPABILITY_SPECS_ATLAS_ANCHOR.md)
- [Session 1135 FINAL close](docs/handoffs/SESSION_1135_FINAL_CLOSE.md)
- [Session 1136 ops view PARKED](docs/handoffs/SESSION_1136_OPS_VIEW_PARKED.md)
- [Session 1137 Jessica Phases 1-4 ratification](docs/handoffs/SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md)
- [Session 1138 F1 paid-interest implementation](docs/handoffs/SESSION_1138_F1_PAID_INTEREST_IMPLEMENTATION.md)
- [Session 1139 upstream clustering quality](docs/handoffs/SESSION_1139_UPSTREAM_CLUSTERING_QUALITY.md)
- [Session 1140 cluster_method mirror + judge-stats](docs/handoffs/SESSION_1140_CLUSTER_METHOD_MIRROR_AND_JUDGE_STATS.md)
- [Session 1140 (A) action-card vertical slice](docs/handoffs/SESSION_1140_ACTION_CARDS_VERTICAL_SLICE.md)
- [Session 1141 Jessica ratification deep dives](docs/handoffs/SESSION_1141_JESSICA_RATIFICATION_DEEP_DIVES.md)
- [Session 1142 docs-hygiene + search_docs + 2 stale-finding fixes](docs/handoffs/SESSION_1142_DOCS_HYGIENE_SEARCH_DOCS_AND_AUDIT_FIXES.md)

---

*Last overwrite: Session 1141 close → Session 1142 entry. Session 1141 closed Chris's top-priority punch list item (Jessica's 22 decisions): 17 accept-as-written + 3 ratify-shipped + 2 with clarification redlines. 4 Jessica clarifications drafted as a single Rigby message in the deep-dive doc, packaged for one-shot send next session. Once Jessica responds, Phase 0 cost-attribution schema (Decision 9) and PitchDeckForge template retune (Decision 19) are unblocked. Headline 1142 work is now (a) send the Rigby message, (b) ops view fork decision (item 2, parked since 1136), (c) v1 rejection-rate read once sample is big enough.*
