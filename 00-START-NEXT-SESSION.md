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

## SESSION 1138-1140 LANDED — Decision-13 + clusterer + judge-stats arc

The last three sessions form a coherent measurement-instrumentation arc on top of Session 1138's Decision-13 demand-gate. All three are merged to main:

**Session 1138 (F1) — paid-interest demand-gate.** `FleetPaidInterest` table + fleet-HMAC POST + `paid_interest_status` PA tool. PRs: u-d-b#2162 (`9c8425f9`), signal-studio#15 (`1e6dbb4`). Final handoff: [`SESSION_1138_F1_PAID_INTEREST_IMPLEMENTATION.md`](docs/handoffs/SESSION_1138_F1_PAID_INTEREST_IMPLEMENTATION.md).

**Session 1139 — entity-token clusterer.** Replaced the verb-keyword fallback clusterer with an entity-token one, gated behind a `cluster_method` discriminator (`legacy` / `entity_token_v1`). Pre-fix baseline: signal-studio's LLM judge rejected **112/131 = 85.5%** of upstream clusters as incoherent. PR u-d-b#2165 (`aac43d31`), follow-up evidence-URL fix `370d49ae`. Final handoff: [`SESSION_1139_UPSTREAM_CLUSTERING_QUALITY.md`](docs/handoffs/SESSION_1139_UPSTREAM_CLUSTERING_QUALITY.md).

**Session 1140 — mirror + judge-stats tool.** signal-studio mirror now persists `cluster_method` + new `/api/judge-stats` endpoint returns the LLM judge accept/reject breakdown by `cluster_method` and `pattern_type`. New u-d-b PA tool `signal_studio_judge_stats` GETs it (auth-less, `SIGNAL_STUDIO_API_URL` env). PRs: signal-studio#17 (`19dfe102`), u-d-b#2169 (`4086019d`). Also Rigby-design-reviewed mid-session: she stripped stale acceptance numbers from the LLM-facing schema (they belong in handoffs/start-here, not in the tool). Final handoff: [`SESSION_1140_CLUSTER_METHOD_MIRROR_AND_JUDGE_STATS.md`](docs/handoffs/SESSION_1140_CLUSTER_METHOD_MIRROR_AND_JUDGE_STATS.md).

---

## SESSION 1141 — CURRENT ENTRY POINT

### FIRST THING — Restart daphne + every celery worker for the new PA tool

The Session 1140 `signal_studio_judge_stats` handler is on disk but the running daphne/celery processes are still pinned to the pre-merge tool registry. Until you bounce them, Rigby will return "no such tool" when you try it.

```bash
pkill -f "daphne -b 127.0.0.1 -p 8000"
pkill -f "celery -A core"
make start && make celery
# Smoke check:
tools/pa_local.sh "signal_studio_judge_stats with days=7"
```

Expected: `{ok: true, days: 7, total: ..., rejection_rate: ..., by_cluster_method: {...}, by_pattern_type: {...}}`. If `ok: false / signal-studio unreachable`, signal-studio's docker stack isn't running — `make up` from `~/development/infra`.

### SECOND — Live rejection-rate measurement (Session 1139/1140 acceptance test)

This is the load-bearing question for the Session 1139 entity-token rewrite. Until the answer arrives, the rewrite's quality bar is hypothetical.

**Two preconditions:**
1. **≥24h since the Session 1139 PR landed** (2026-05-24 18:03 UTC), so celery-beat has produced enough v1-tagged rows for a real sample. As of 2026-05-25 18:03 UTC this is satisfied.
2. **Stack with working pgvector.** Local `$libdir/vector` blocker still in effect — measure against the docker stack (`~/development/infra/make up`) or production.

**Once both hold, ask Rigby:**

```text
signal_studio_judge_stats with days=7
```

Then read `by_cluster_method.entity_token_v1.rejection_rate`.

**Acceptance bar (Rigby-locked, do not edit without re-anchoring):**
- **< 30%** → victory. Queue legacy bulk-archive (see THIRD).
- **30–60%** → partial. Decide whether Option B (embedding-based clustering) is worth the spend.
- **≥ 60%** → close to the 85.5% baseline. Escalate to Option B.

Fallback if Rigby/PA loop isn't available:

```bash
# Direct curl against signal-studio docker:
curl -s "http://localhost:8007/api/judge-stats?days=7" | jq .by_cluster_method

# Or docker exec into Postgres:
cd ~/development/signal-studio
docker compose exec -T signal_studio_postgres psql -U signalstudio -d signalstudio -c \
  "SELECT cluster_method, summary_quality, COUNT(*) FROM signal_clusters
   GROUP BY 1, 2 ORDER BY 1, 2;"
```

### THIRD — Conditional on SECOND landing < 30%: legacy bulk-archive

Only after 7–14 days of v1 running cleanly AND the SECOND measurement says victory:

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

### Chris's tech queue (carried over from Session 1138/1140)

1. **Contract Concierge fleet routing fix** (Q1) — architecture: new agent / extend `legal_doc_drafter_agent` / remove default
2. **Signal Studio engine-side enrichment integration** (Q3) — architecture: v2 question
3. **ComplianceSentinel fleet routing** (Q4) — architecture: `security_agent` / null / skip u-d-b
4. **Engine-mismatch resolutions** (cross-cutting C5)
5. **Phase 0 cost-attribution SCHEMA** — UNBLOCKED by Jessica's Decision 9. Chris designs `LLMCallLog.workspace` FK + daily cap + soft-degrade-to-gpt-5-mini + portfolio kill switch.
6. **SellerPilot Render API Blueprint deployment** — ops (deferred per local-only mode)
7. **ComplianceSentinel Render API Blueprint deployment** — ops (deferred per local-only mode)
8. **Rigby products.ts update** — fires when Decision 1 trigger met
9. **Atlas deviation ratification** (cross-cutting C7)
10. **F5 audit** — verify the 4 PitchDeckForge styles meaningfully differ in code (~15 min)
11. **F7 Stripe verification collaboration** — Jessica drives, Chris's Stripe access

### Phase 5 audit queue (Jessica-driven)

| # | Action | Your time |
|---|---|---|
| F5 | Audit 4 PitchDeckForge styles in code (with Chris) | 5 min review |
| F6 | Ask 3 fund operators about intake widget (Decision 22 trigger) | days-weeks of outreach |
| F7 | Stripe verification audit on 4 Suite products (with Chris) | 30-60 min |
| #23 | Cross-Suite handoff E2E matrix | 1-2 hr |
| #24 | TOS + e-signature legal review status check | 5 min ping; days wait |
| #25 | Marketplace policy research (SellerPilot) | 30 min review |
| #27 | Rigby repo audit — what's in 24-7-ai-global for Rigby standalone | 5 min review |

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
- **Local `$libdir/vector` pgvector path mismatch** blocks any Django query touching SpiderData / other VectorField tables. Known local-env issue (same blocker since Session 1131). Workaround: defer live verification to Docker / production stack.
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

### (A) Action-card pre-generation for curated — visible-feature alternative, STILL queued

**Rigby locked the design fork**: child rows (typed `CuratedSignalEntry` rows for actions), NOT payload blob.

**Estimate**: ~1 session. ~10 LLM calls/day per curator run.

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

### Other carryovers

- **Legacy SignalCluster bulk-archive** (Session 1139 follow-up, now Session 1141 THIRD if SECOND lands < 30%) — after 7-14 days of v1 running cleanly, bulk-archive rows with `cluster_method='legacy' AND (status != 'active' OR created_at < cutoff OR strength < threshold)`. Avoid tying to judge-reject mapping on day 1.
- **signal-studio mirror dep gap** (Session 1140 discovery) — `stripe` + `httpx` were missing from `backend/.venv` until ad-hoc `pip install`. Not committed. Future smoke-test sessions should re-pip from `requirements.txt` rather than assume venv is current.
- **Vercel preview deploy on signal-studio** — failed during Session 1140 signal-studio#17 merge. Backend-only diff couldn't have caused it; pre-existing flake or quota issue. Worth a separate look if frontend redeploys are needed.
- **Ops view fork decision** (Session 1136 PARKED) — Chris picks: kill / radical-simplify / different medium / redirect with new interview
- **Capability spec Phase 0 scaffolding** — gated on per-app intent (Session 1135 done, Session 1137 ratified Jessica side)
- **Semantic `category`** — `pattern_type` is the honest placeholder.
- **`docs/SERVICES.md` drift** — header says 320 service files; reality after 1132 is 336.
- **ai-content-studio#2** — Docker foundation PR. Back burner.
- **24-7-ai-global** — Next.js, not yet Dockerized. Surface for Rigby standalone Phase 1 (deferred per Decision 1).
- **Per-user filter at u-d-b's replay endpoint** — optional `?user_id=…` query param.
- **DB-dependent tests** for fleet emit predicate + cursor advancement + curator dedup + PA-chat audit — requires test DB with pgvector.
- **context-kit doctor floor:** `10 OK / 2 warnings` (both upstream).
- **`character-os`** — Another Claude Code instance may be active there. Read-only is fine; don't push PRs there. Per Atlas, Phase 4+ parked.

---

## SESSION 1131-1140 HANDOFFS

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

---

*Last overwrite: Session 1140 close → Session 1141 entry. Headline 1141 work: restart daphne+celery to pick up `signal_studio_judge_stats` registration, then run the live rejection-rate measurement against the post-merge stack to close out the Session 1139 acceptance test. Pre-merge baseline: 112/131 = 85.5% legacy rejection; target for v1: <30%. Acceptance bar Rigby-locked.*
