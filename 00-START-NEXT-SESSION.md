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

## SESSION 1133 LANDED — (X) FLEET_* back-prop, 5 of 5

Full handoff: [`docs/handoffs/SESSION_1133_FLEET_PA_SIGNING_BACKPROP.md`](docs/handoffs/SESSION_1133_FLEET_PA_SIGNING_BACKPROP.md).

**Headline**: 5 small PRs opened (one per remaining fleet repo). All 7 fleet repos now have FLEET_* env vars provisioned and sign PA-chat requests with HMAC. Audit telemetry shows `fleet_signature` rows for each. Reject-mode-flip prerequisite (X) is fully delivered.

| Repo | PR |
|---|---|
| mentorforge | [#19](https://github.com/clwest/mentorforge/pull/19) |
| pitchdeckforge | [#18](https://github.com/clwest/pitchdeckforge/pull/18) |
| sellerpilot | [#12](https://github.com/clwest/sellerpilot/pull/12) |
| dealflowtracker | [#16](https://github.com/clwest/dealflowtracker/pull/16) |
| compliancesentinel | [#12](https://github.com/clwest/compliancesentinel/pull/12) |

Combined with contract-concierge (1129) + signal-studio (1131 Phase 1), all 7 fleet repos are wired. Bearer-only canary still works + audited correctly per Rigby's fail-open invariant.

---

## SESSION 1134 — CURRENT ENTRY POINT (needs Rigby pick after audit-window decision)

> **Direction**: not yet locked. (Y) reject-mode flip is the natural next step
> per Rigby's lock from 1132, BUT it requires "≥3 days of clean audit telemetry"
> and (X) just shipped. Brief her with the audit-table state + ask whether the
> 3-day window applies to laptop-local deployment.

### FIRST THING — Sanity check before any new work

1. `cd ~/development/infra && make up`
2. `make all` (or `make start && make celery` from u-d-b)
3. `curl -s http://localhost:8007/api/signals | jq '.total'` → expect 131-ish (5 seed + N real)
4. `curl -s http://localhost:8007/api/signals/curated | jq '.total'` → expect 10 (if curator has run)
5. Visual check at `localhost:5173`: "All Signals" + "Curated Top 10" tabs render with real data; clicking Curated and triggering `curate_and_emit()` from u-d-b shell should surface a "🟢 New curated set — refresh" pill within ~5s
6. **Check the PA-chat audit table — Session 1134 direction hinges on this**:
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
   # The critical metric: bearer-only calls FROM FLEET APPS (claimed_app_slug != '')
   # If this is 0 across all 7 fleet apps for ≥3 days, (Y) is safe.
   bearer_from_fleet = rows.filter(auth_mode='bearer_only').exclude(claimed_app_slug='')
   print(f'bearer-only with fleet app_slug claim (72h): {bearer_from_fleet.count()}')
   for slug, n in Counter(bearer_from_fleet.values_list('claimed_app_slug', flat=True)).most_common():
       print(f'  {slug}: {n}')
   mismatches = rows.filter(match=False)
   print(f'mismatches (claimed != verified) 72h: {mismatches.count()}')
   "
   ```

If anything is off, fix it before starting new work.

### Direction candidates for Session 1134

**Rigby's 1133-close briefing locked the framing for both options** (conversation pa-d19c1674b936). Her crisp top-line for Chris:

> Merge the 5 PRs. Set envs in mainline deploy contexts. Start telemetry clock. In parallel, prep the reject-mode flip BEHIND A FLAG so it's a low-risk toggle once the telemetry window is satisfied. If choosing (A), implement child rows.

#### (Y) Reject-mode flip in unified_pa_chat — PRIMARY (staged)

**Rigby's lock on the 3-day window**: treat it as "post-merge, mainline, persistent envs," NOT "since I proved it locally in 1133." The thing being validated isn't code correctness — it's that REAL CALLERS from main with committed env wiring reliably send fleet HMAC AND no legitimate bearer-only+claim traffic exists. That observability only starts after Chris merges the 5 PRs.

**Two paths Rigby will accept**:

- **Default path** — wait for merge + envs in mainline, then start the 3-day clock. Lower risk, sharper signal.
- **Staged path if Chris wants to ship security NOW**:
  - **Stage 1 (immediately)**: "soft deny" — flip the deny ONLY when a routing claim is present in the body. Include a feature flag / env toggle as escape hatch + loud logging. Roll out with the flag OFF first; flip it on after merge.
  - **Stage 2 (post-merge + minimal telemetry window)**: "hard deny" — keep deny behavior, remove the escape hatch once telemetry is clean.

**Lock from 1132 + 1133 audit table verification**: deny condition is **narrow**:
```
(fleet_identity is None) AND (routing claim present in body) → 403
```
NOT "no fleet identity ever" — bearer-only must still work for non-fleet callers (Chris's web UI, CLI tests, etc.). The Session 1129 Move 1 gate at `views_personal_assistant.py:340-360` is the right point to flip.

**Pre-flip audit checklist (Rigby's 4 sweeps)** — grep across u-d-b before changing the gate:

1. **`app_slug` reads outside the 1129 gate**:
   ```
   grep -rn "context.get(\"app_slug\")\|request.data\[\"context\"\]\[\"app_slug\"\]\|app_slug=" core/
   ```
   Audit any usage in: workspace selection, content routing, tool scoping, initiative scoping, KB ingest tags, publish destinations.

2. **`X-Fleet-` header usage** in business logic (not just auth class/middleware):
   ```
   grep -rn "X-Fleet-" core/ --include="*.py"
   ```
   Business logic should use VERIFIED identity (`request.fleet_identity.get("app_slug")`), not raw headers.

3. **"Fleet identity optional" branches** where claimed slug still influences behavior:
   ```
   grep -rn "if fleet_identity\|fleet_identity is None\|fleet_identity or" core/
   ```
   Pattern to flag: `if fleet_identity: ... else: <still uses claimed slug>`.

4. **Confirm deny condition is narrowly scoped** — bearer-only without claim still works; bearer-only WITH claim gets 403.

**Estimate**: ~half a session for the gate change + flag wiring, plus 1 session of audit-sweep work if needed.

#### (A) Action-card pre-generation for curated — visible-feature alternative

**Rigby locked the design fork**: **child rows** (typed `CuratedSignalEntry` rows for actions), NOT payload blob. Reasons:
- Stable schema + typed fields (title/url/source/summary/category/importance/rationale) beats a blob for rendering, filtering, and QA
- Per-entry evidence/citations attach cleanly
- Diffs + dedupe are easier on rows
- Future scoring, suppression, "why did this appear?" auditing is cheap on rows, painful on JSON blobs

**Estimate**: ~1 session.

**Cost**: bounded LLM (~10 calls/day per curator run).

**Visible UX**: Curated tab cards show instant action plans (no "Generate Action" click).

**Locked shape**: u-d-b pre-generates during the curator run, persists actions as child rows on `CuratedSignalEntry`, includes them in the `signal.curated_published` payload. signal-studio is a pure renderer — no LLM calls on the consumer side.

**My read**: brief Rigby with the audit telemetry first. If Chris wants security finish → (Y) staged (Stage 1 now, Stage 2 after merge). If he wants visible feature → (A) with child rows.

### Recommended Rigby coordination for Session 1134

If Chris locks (Y):
- **Default path**: just merge the 5 PRs first, set envs, wait 3 days, then flip. No code work this session.
- **Staged path**: implement Stage 1 with feature flag off by default. Flip flag on after merge + audit clean.
- Either way, run Rigby's 4-sweep audit checklist BEFORE touching the gate.
- Re-engage Rigby only if an audit sweep surfaces an unexpected consumer of `context.app_slug` outside the 1129 gate.

If Chris locks (A):
- **Design fork already resolved**: child rows for the action data.
- Code u-d-b pre-gen: extend `signal_curator_service.curate_and_emit()` to also call action generation per top-N cluster, persist as `CuratedSignalEntry` child rows (or a new sibling table — flag this fork to Rigby if it surfaces).
- Update `build_curated_envelope()` to include the actions per entry.
- signal-studio side: likely zero changes — `cluster` envelope already passes through; just surface the action rows in the Curated tab UI.

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

### Status of 1131-1133 arc carryovers

- **(X)** FLEET_* env back-prop — **DONE (1133)**, see PRs above
- **(A)** Action-card pre-gen for curated — **deferred candidate for 1134** (above)
- **(Y)** Reject-mode flip — **primary candidate for 1134** (above), gated on audit telemetry

---

## SESSION 1131-1133 HANDOFFS

- [Session 1131 Phase 1 close](docs/handoffs/SESSION_1131_SIGNAL_STUDIO_PHASE_1.md)
- [Session 1131 Phase 2 close](docs/handoffs/SESSION_1131_PHASE_2_SIGNAL_CURATOR.md)
- [Session 1132 close](docs/handoffs/SESSION_1132_LIVE_REFRESH_AND_PA_AUDIT.md)
- [Session 1133 close](docs/handoffs/SESSION_1133_FLEET_PA_SIGNING_BACKPROP.md)

---

## SESSION 1130 — TWO SESSIONS BACK (Move 3 R2 reconnect-resilience)

Full handoff: [`docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md`](docs/handoffs/SESSION_1130_FLEET_EVENTS_MOVE_3_R2.md).

---

*Last overwrite: Session 1133 close → 1134 entry (Y primary, A alternative, both gated on Rigby brief), 2026-05-23.*
