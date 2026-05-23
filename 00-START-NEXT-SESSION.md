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
3. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + display rules + constraints.
4. **`docs/UDB_TRANSLATION_LAYER.md`** — audience contract + no-claims rule.
5. **Archive / handoff docs** — historical unless promoted by `docs/handoffs/CURRENT.md` or this file.

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

## SESSIONS 1131 + 1132 LANDED — signal-studio full vertical slice + 1132 polish

**Session 1131 — signal-studio vertical slice**
- Phase 1 ([handoff](docs/handoffs/SESSION_1131_SIGNAL_STUDIO_PHASE_1.md)): pull endpoint + emit + ingest + backfill. 5 hardcoded seeds → 131 real clusters live via SSE. u-d-b [#2138](https://github.com/clwest/donkey-betz-platform/pull/2138) + signal-studio [#12](https://github.com/clwest/signal-studio/pull/12)
- Phase 2 ([handoff](docs/handoffs/SESSION_1131_PHASE_2_SIGNAL_CURATOR.md)): SignalCuratorAgent daily Top 10 by score 0.9·strength + 0.1·recency, dedup by (pattern_type, topic_key), cap of 3/type. u-d-b [#2140](https://github.com/clwest/donkey-betz-platform/pull/2140) + signal-studio [#13](https://github.com/clwest/signal-studio/pull/13)

**Session 1132 — Curated tab live refresh + PA-chat audit**
- Full handoff: [`docs/handoffs/SESSION_1132_LIVE_REFRESH_AND_PA_AUDIT.md`](docs/handoffs/SESSION_1132_LIVE_REFRESH_AND_PA_AUDIT.md)
- (C) Curated tab live SSE refresh: ~5s latency u-d-b → browser. signal-studio [#14](https://github.com/clwest/signal-studio/pull/14)
- (B-scaffold) PA-chat warn-only audit: `FleetPAChatAuditRow` table. u-d-b [#2142](https://github.com/clwest/donkey-betz-platform/pull/2142). **NO ENFORCEMENT** — visibility only.

**Burned-in gotcha (saved to memory):** Fleet HMAC clients sign with `SHA256(raw_secret).hexdigest()`, not the raw secret. Symptom is 401 `signature_mismatch`. Reference impl: `contract-concierge/backend/app/fleet_signer.py:141`.

**1132 discoveries (documented inline, not new memory rules):**
- Django session middleware can satisfy `SessionAuthentication` even for curl-style requests with `Authorization: Token`. Read the `Authorization` header directly when classifying auth mode rather than trusting DRF's `successful_authenticator`.
- `request.fleet_identity` is a **dict**, not an ORM row — `.get("app_slug")`, not `getattr(_, "app_slug")`. Documented inline in `core/services/fleet_pa_chat_audit.py`.

---

## SESSION 1133 — CURRENT ENTRY POINT (X locked + 5 enhancements)

> **Rigby locked** (conversation pa-d19c1674b936, Session 1132 close):
> **Session 1133 = (X)**. Back-prop FLEET_* env vars to the remaining
> 5 fleet repos. 5 small PRs (one per repo), not one ops-rollup. (A)
> and (Y) explicitly held unless Chris overrides at session start.

### FIRST THING — Sanity check before any new work

1. `cd ~/development/infra && make up`
2. `make all` (or `make start && make celery` from u-d-b)
3. `curl -s http://localhost:8007/api/signals | jq '.total'` → expect 131-ish (5 seed + N real)
4. `curl -s http://localhost:8007/api/signals/curated | jq '.total'` → expect 10 (if curator has run)
5. Visual check at `localhost:5173`: "All Signals" + "Curated Top 10" tabs render with real data; clicking Curated and triggering `curate_and_emit()` from u-d-b shell should surface a "🟢 New curated set — refresh" pill within ~5s
6. **NEW for 1133**: check the PA-chat audit table to see current rollout state:
   ```bash
   cd ~/development/unified-donkey-betz
   .venv/bin/python manage.py shell -c "
   from core.models.fleet import FleetPAChatAuditRow
   from collections import Counter
   from django.utils import timezone
   from datetime import timedelta
   since = timezone.now() - timedelta(hours=24)
   rows = FleetPAChatAuditRow.objects.filter(created_at__gte=since)
   print(f'audit rows (24h): {rows.count()}')
   print('by auth_mode:')
   for am, n in Counter(rows.values_list(\"auth_mode\", flat=True)).most_common():
       print(f'  {am}: {n}')
   bearer_claims = rows.filter(auth_mode=\"bearer_only\").exclude(claimed_app_slug=\"\")
   print(f'bearer-only with body app_slug claim: {bearer_claims.count()}')
   mismatches = rows.filter(match=False)
   print(f'mismatches (claimed != verified): {mismatches.count()}')
   "
   ```

If anything is off, fix it before starting new work.

### Three credible candidates for Session 1133 (Rigby to pick)

#### (X) FLEET_* env back-prop to 5 fleet repos — **LOCKED for 1133**
- **Estimate**: ~1 session, mostly mechanical
- **Strategy lock (Rigby)**: 5 small PRs (one per repo). NOT an ops-rollup PR. Easier rollback + isolated failures + easier review.
- **Why it matters**: unlocks the reject-mode-flip prerequisite by getting `auth_mode=fleet_signature` rows from mentorforge / pitchdeckforge / sellerpilot / dealflowtracker / compliancesentinel into the audit table
- **What's done already**: contract-concierge (1129) + signal-studio (Phase 1) have `FLEET_KEY_ID` + `FLEET_SERVICE_SECRET`. Their `brain_client.py` is byte-identical to the other 5; auto-signs once env vars land
- **Canonical env var set** (Rigby's lock — keep identical across all repos to avoid drift):
  ```
  FLEET_APP_SLUG=<app-slug>
  FLEET_KEY_ID=fs_<appslug>_k1
  FLEET_SERVICE_SECRET=<32-byte-raw-secret-shown-once-at-mint>
  ```
- **Work per repo**:
  1. `python manage.py provision_fleet_identity --app-slug <name>` on u-d-b (one-time mint, secret shown once — save to repo `.env` immediately)
  2. Add the three env vars above to the repo's `.env` + `docker-compose.yml` (mirror contract-concierge's compose block exactly)
  3. `docker compose up -d --build --force-recreate <repo>_api`
  4. **Goal metric (Rigby's lock)**: at least 1 live audit row showing ALL three:
     - `auth_mode='fleet_signature'`
     - `verified_app_slug='<that app>'`
     - `has_fleet_identity=True`
     This is the only proof that env + signing wiring is actually working end-to-end. "Request succeeded" is NOT the goal metric — given the DRF auth-classifier weirdness from 1132, treat the audit row as source of truth.
  5. **Bearer-only canary smoke per repo** (Rigby's lock): also verify bearer-only paths still get audited as `auth_mode='bearer_only'` and remain fail-open. Confirms HMAC is the dominant path without breaking warn-only.
- **Nice-to-have if time** (Rigby's suggestion): add a short repo-local README snippet ("How to provision identity + set FLEET_* + verify audit row") so future repos don't repeat wiring drift.

#### (A) Action-card pre-generation for curated
- **Estimate**: ~1 session
- **Cost**: bounded LLM (~10 calls/day per curator run)
- **Visible UX win**: Curated tab cards show instant action plans
- **Rigby's locked shape** (from Phase 1 close, preserved): pre-generate u-d-b-side, include in `signal.curated_published` payload OR in `CuratedSignalEntry` child rows. signal-studio is a renderer, not an LLM executor
- **Open design question for Rigby**: payload vs child rows? Payload is simpler (event self-contained); child rows are queryable (admin can see historical action plans per snapshot). Lean child rows for the same reason Phase 2 picked typed snapshot table over column-on-cluster

#### (Y) Reject-mode flip in unified_pa_chat
- **Pre-req**: (X) done AND audit table shows ≥3 days of clean (signed + matching) telemetry
- **Estimate**: ~half a session of careful config + verification
- **Lock from 1132**: the existing Session 1129 Move 1 gate is the enforcement point; flipping is just changing the log-only behavior to deny when `fleet_identity` is None AND a routing/app_slug claim is present
- **NOT a session 1133 candidate** unless (X) has shipped and the audit data is clean — Rigby's hard rule: do NOT ship partial auth enforcement

**My read**: (X) → (Y) is the security-focused arc (X this session, Y when telemetry is clean). (A) is the visible-feature path if Chris wants polish over security.

**Rigby's lock**: (X) for 1133. (A) and (Y) explicitly held unless Chris overrides at session start.

### Recommended Rigby coordination for Session 1133

Direction is locked. Only re-engage Rigby if:
- **Chris overrides** the (X) lock at session start (e.g. wants (A) instead)
- **The provision flow surfaces a design fork** (e.g. you discover one of the 5 repos doesn't have `brain_client.py` or has a divergent version that won't auto-sign — would change the back-prop unit of work)
- **A canary smoke fails** in a way that suggests the existing 1129 Move 1 path is broken for that app (not just env-var-missing) — pull her in before patching

Otherwise: provision identities, update env + compose, recreate containers, verify audit rows for each app, open 5 small PRs.

### Operational notes carried forward from 1131 + 1132

These are locked in code/tests but worth remembering when touching adjacent areas:

- **Fleet HMAC sign-key = SHA256(secret), not raw secret.** Saved to memory. Any new fleet client must follow this contract.
- **`init_db()` does not migrate existing tables** (signal-studio side). Schema additions need `_ensure_schema()` calls in BOTH startup paths (`main.py` startup hook AND `seed.py` before its first query — Dockerfile runs seed before uvicorn).
- **brain_events.py is byte-identical across all 7 fleet repos.** Future event prefixes plug into the HANDLERS prefix router in `signal_ingest.py` (one tuple, no parallel listener).
- **EventSource is browser-only.** 2-hop pattern still applies: u-d-b emits → fleet backend server-to-server subscribes → fleet backend re-emits to browser.
- **Daphne + sync generator + Redis pub/sub = hang.** Use `async def event_generator` + `redis.asyncio` for any new SSE endpoint.
- **Docker rebuild gotcha.** `docker compose up -d --build` doesn't always recreate the container — use `--force-recreate`. Don't run parallel builds across 6+ repos.
- **`/api/fleet/*` paths are in `OPTIONAL_AUTH_PATHS`.** Signed-but-tokenless is the canonical fleet auth shape.
- **Django 5 `db_default` for DB-managed defaults** (Postgres sequences, `gen_random_uuid()`, `now()`). `null=True` alone makes Django pass NULL in INSERT and overrides the DB DEFAULT.
- **Phase 2 topic-key gotcha**: upstream keywords mix PATTERN_TYPE_KEYWORDS indicator words with topics. `topic_key_for_cluster` in `signal_curator_service.py` prefers `cluster.name` first then keywords, with a stop-word filter on BOTH. If you add new pattern types or change `_generate_topic_name`, update the stop-word set.
- **Session middleware can satisfy SessionAuthentication** (1132 discovery). Don't trust DRF's `successful_authenticator` to identify the auth mode if you need to distinguish bearer-token from session callers. Read the `Authorization` header directly.
- **`request.fleet_identity` is a dict, not an ORM row** (1132 gotcha). Use `.get("app_slug")`, not `getattr`.

### Carryovers (open / parked, not blocking)

- **(A) Action-card pre-gen for curated** — see candidate above.
- **(Y) Reject-mode flip in unified_pa_chat** — see candidate above.
- **Evidence URL field** — both phases ship `url=""`. Cleanest path: enrichment agent populates it.
- **Semantic `category`** — `pattern_type` is the honest placeholder.
- **`docs/SERVICES.md` drift** — header says 320 service files; reality after 1132 is 336.
- **ai-content-studio#2** — Docker foundation PR. Back burner.
- **24-7-ai-global** — Next.js, not yet Dockerized.
- **Per-user filter at u-d-b's replay endpoint** — optional `?user_id=…` query param.
- **DB-dependent tests** for fleet emit predicate + cursor advancement + curator dedup + PA-chat audit — requires test DB with pgvector.
- **context-kit doctor floor:** `10 OK / 2 warnings` (both upstream).
- **`character-os`** — Another Claude Code instance may be active there. Read-only is fine; don't push PRs there.

### Open PR stack from sessions 1131 + 1132

When Chris is ready to review/merge, the order is:

```
main
  ↑
docs/session-1131-close (#2139)
  ↑
docs/session-1131-phase-2-close (#2141)
  ↑
docs/session-1132-close (this branch when it lands)

feat/signal-studio-phase-1-pull-endpoint (#2138)  ← u-d-b Phase 1 code
  ↑
feat/phase-2-signal-curator-agent (#2140)         ← u-d-b Phase 2 code
  ↑
feat/pa-chat-audit-scaffold (#2142)               ← u-d-b 1132 (B) code

signal-studio main
  ↑
feat/phase-1-fleet-signal-ingest (#12)
  ↑
feat/phase-2-curated-signals (#13)
  ↑
feat/curated-live-refresh (#14)                   ← signal-studio 1132 (C) code
```

Each handoff is stacked on the previous; each feat branch is stacked on the previous feat. Merge in order if you want clean linear history; out of order works too — GitHub rebases automatically.

### Original three-candidate framing (preserved for context)

Before Rigby locked (X), the three options were:

1. **(X)** FLEET_* env back-prop — the picked one
2. **(A)** Action-card pre-gen for curated — held, Rigby noted it "adds LLM surface area; keep behind (X) unless Chris explicitly wants UX polish now"
3. **(Y)** Reject-mode flip — held behind (X) + clean telemetry window

If Chris wants to override (X) at session start, the candidates and their tradeoffs are all in the [Session 1132 close handoff](docs/handoffs/SESSION_1132_LIVE_REFRESH_AND_PA_AUDIT.md).

---

## SESSION 1131 + 1132 HANDOFFS

- [Session 1131 Phase 1 close](docs/handoffs/SESSION_1131_SIGNAL_STUDIO_PHASE_1.md)
- [Session 1131 Phase 2 close](docs/handoffs/SESSION_1131_PHASE_2_SIGNAL_CURATOR.md)
- [Session 1132 close](docs/handoffs/SESSION_1132_LIVE_REFRESH_AND_PA_AUDIT.md)

---

## SESSION 1130 — TWO SESSIONS BACK (Move 3 R2 reconnect-resilience)

Full handoff: [`docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md`](docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md).

---

*Last overwrite: Session 1132 close → 1133 entry (X locked by Rigby), 2026-05-22 evening.*
