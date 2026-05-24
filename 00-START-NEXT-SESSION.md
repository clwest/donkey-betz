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

## SESSION 1138 LANDED — F1 paid-interest signal implementation

**Final handoff:** [`docs/handoffs/SESSION_1138_F1_PAID_INTEREST_IMPLEMENTATION.md`](docs/handoffs/SESSION_1138_F1_PAID_INTEREST_IMPLEMENTATION.md)

**TL;DR:** Decision 13 demand-gate built end-to-end. `FleetPaidInterest` table + fleet-HMAC POST endpoint on u-d-b, `paid_interest_status` PA tool for Jessica, signal-studio backend relay + frontend footer form. PRs merged: u-d-b #2162 (commit `9c8425f9`), signal-studio #15 (`1e6dbb4`).

---

## SESSION 1139 LANDED — upstream clustering quality (entity-token clusterer)

**Final handoff:** [`docs/handoffs/SESSION_1139_UPSTREAM_CLUSTERING_QUALITY.md`](docs/handoffs/SESSION_1139_UPSTREAM_CLUSTERING_QUALITY.md)

**TL;DR:** Replaced the verb-keyword fallback clusterer in u-d-b's `signal_aggregation_service` with an entity-token clusterer, gated behind a new `cluster_method` field so legacy rows decay naturally (no forced re-cluster). Pre-1139 baseline: signal-studio LLM judge rejected 112/131 = 85.5% of clusters as incoherent; latest 25 u-d-b clusters were 100% generic-verb-fallback names like "Now opportunity window" lumping Trump phone + Hubble + Ebola + NFL.

**Empirical baseline locked** (for the Session 1140 acceptance test):
- u-d-b: 307 SignalCluster rows, all backfilled `cluster_method='legacy'` by migration 0351.
- signal-studio: 131 mirror rows, 112 rejected (85.5%), 19 summarized (14.5%).
- Rigby's design Q1–Q5 ratified mid-session and saved into the handoff.

**Where it lives:** u-d-b branch `feat/session-1139-upstream-clustering-quality` — PR pending (this entry post-merge).

**Honest scope note:** Local live verification of the full pipeline was BLOCKED by the persistent local-env `$libdir/vector` pgvector path mismatch (same blocker that's parked `test_fleet_signals_phase1.py` integration paths since Session 1131). 24 pure-function unit tests cover algorithmic behavior; live rejection-rate measurement is Session 1140's first task once the change runs against production (which has working pgvector).

---

## SESSION 1140 — CURRENT ENTRY POINT

### FIRST THING — Live rejection-rate measurement (Session 1139 acceptance test)

**Pre-req:** Session 1139 PR merged + 24-48h of celery-beat aggregation runs against production-like data so v1 clusters land in both u-d-b and signal-studio's mirror.

```bash
# 1. u-d-b side — fraction of recent clusters tagged v1
cd ~/development/unified-donkey-betz
.venv/bin/python manage.py shell -c "
from core.models_signal_intelligence import SignalCluster
from django.utils import timezone
from datetime import timedelta
from collections import Counter
recent = SignalCluster.objects.filter(
    detected_at__gte=timezone.now() - timedelta(hours=24)
)
print(f'last 24h total: {recent.count()}')
print('by cluster_method:')
for cm, n in Counter(recent.values_list('cluster_method', flat=True)).most_common():
    print(f'  {cm}: {n}')
"

# 2. signal-studio side — rejection rate per cluster_method
#    (after the mirror schema includes cluster_method — see SECOND below)
cd ~/development/signal-studio
docker compose exec -T signal_studio_postgres psql -U signalstudio -d signalstudio -c \
  "SELECT cluster_method, summary_quality, COUNT(*) FROM signal_clusters
   GROUP BY 1, 2 ORDER BY 1, 2;"
```

**Acceptance bar (Rigby-locked Session 1139):**
- v1 rejection rate **< 30%** → declare victory; ship the PA tool; queue legacy bulk-archive for 1141.
- v1 rejection rate **30–60%** → partial win; decide whether Option B (embedding clustering) is worth spend.
- v1 rejection rate **≥ 60%** → close to baseline failure; escalate to Option B.

### SECOND — signal-studio mirror schema accepts `cluster_method`

Session 1139 made u-d-b's `cluster_envelope` emit `cluster_method`. signal-studio's `signal_ingest.py` currently accept-and-ignore (forward compat). To do the per-method breakdown query above, the mirror needs to store it:

1. Add `cluster_method` column to signal-studio's `signal_clusters` table (Alembic migration).
2. Update `signal_ingest.upsert_cluster` (or equivalent) to persist the envelope's `cluster_method` field. Default `'legacy'` for rows ingested before this lands.
3. Small PR in signal-studio.

### THIRD — Rigby's `signal_studio_judge_stats` PA tool (Q3 from Session 1139)

~50 LOC across 2 repos. Surfaces the rejection rate Rigby can query directly without docker exec.

- signal-studio: add `/api/judge-stats?days=N` endpoint returning `{total, rejected, accepted, rejection_rate, by_pattern_type: {...}, by_cluster_method: {...}}`.
- u-d-b: register `signal_studio_judge_stats` PA tool in `pa_tool_schemas.py` + handler in `td_handlers_core.py` + `tool_dispatcher.register(...)`. Tool calls signal-studio over the fleet-net hostname.
- Daphne + celery restart per the canonical PA notes above.

### Chris's tech queue (carried over from Session 1138)

1. **Contract Concierge fleet routing fix** (Q1) — architecture: new agent / extend `legal_doc_drafter_agent` / remove default
2. **Signal Studio engine-side enrichment integration** (Q3) — architecture: v2 question
3. **ComplianceSentinel fleet routing** (Q4) — architecture: `security_agent` / null / skip u-d-b
4. **Engine-mismatch resolutions** (cross-cutting C5)
5. **Phase 0 cost-attribution SCHEMA** — UNBLOCKED by Jessica's Decision 9. Chris designs `LLMCallLog.workspace` FK + daily cap + soft-degrade-to-gpt-5-mini + portfolio kill switch.
6. **SellerPilot Render API Blueprint deployment** — ops
7. **ComplianceSentinel Render API Blueprint deployment** — ops
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
5. Read `docs/handoffs/SESSION_1139_UPSTREAM_CLUSTERING_QUALITY.md` for the clusterer rewrite details and the acceptance protocol.

---

## OPERATIONAL NOTES (carry forward)

These are locked in code/tests but worth remembering when touching adjacent areas:

- **Session 1139 — `cluster_method` discriminator on SignalCluster.** New rows default `entity_token_v1`; backfilled 307 legacy rows. Downstream consumers should filter on `cluster_method='entity_token_v1'` when applying any new quality bar.
- **Session 1139 — entity-token clusterer in `signal_aggregation_service`.** Requires ≥2 shared specific tokens (frequency ≥2 in window) to form a cluster. Better to miss a cluster than create a junk one. Per-pattern min size: `opportunity_window=4`, default 3.
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

- **Legacy SignalCluster bulk-archive** (Session 1139 follow-up) — after 7-14 days of v1 running cleanly, bulk-archive rows with `cluster_method='legacy' AND (status != 'active' OR created_at < cutoff OR strength < threshold)`. Avoid tying to judge-reject mapping on day 1.
- **Ops view fork decision** (Session 1136 PARKED) — Chris picks: kill / radical-simplify / different medium / redirect with new interview
- **Capability spec Phase 0 scaffolding** — gated on per-app intent (Session 1135 done, Session 1137 ratified Jessica side)
- **Evidence URL field** — both signal phases ship `url=""`. Cleanest path: enrichment agent populates it. Signal Studio Phase 0 GATING.
- **Semantic `category`** — `pattern_type` is the honest placeholder.
- **`docs/SERVICES.md` drift** — header says 320 service files; reality after 1132 is 336.
- **ai-content-studio#2** — Docker foundation PR. Back burner.
- **24-7-ai-global** — Next.js, not yet Dockerized. Surface for Rigby standalone Phase 1 (deferred per Decision 1).
- **Per-user filter at u-d-b's replay endpoint** — optional `?user_id=…` query param.
- **DB-dependent tests** for fleet emit predicate + cursor advancement + curator dedup + PA-chat audit — requires test DB with pgvector.
- **context-kit doctor floor:** `10 OK / 2 warnings` (both upstream).
- **`character-os`** — Another Claude Code instance may be active there. Read-only is fine; don't push PRs there. Per Atlas, Phase 4+ parked.

---

## SESSION 1131-1139 HANDOFFS

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

---

*Last overwrite: Session 1139 close → Session 1140 entry. Headline 1140 work: live rejection-rate measurement (Session 1139 acceptance test), signal-studio mirror schema for `cluster_method`, Rigby's `signal_studio_judge_stats` PA tool. Pre-merge baseline: signal-studio judge rejecting 112/131 = 85.5%; target post-merge with v1 clusters is <30%. Acceptance bar Rigby-locked.*
