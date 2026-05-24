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
3. **`docs/24_7_GLOBAL_AI_APP_ATLAS.md`** — **strategy anchor**. Phase 1 = Rigby standalone flagship at `app.247globalai.com` ($20-30/mo). Sibling apps deferred. Character OS Phase 4+, parked.
4. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + display rules + constraints.
5. **`docs/UDB_TRANSLATION_LAYER.md`** — audience contract + no-claims rule.
6. **`docs/specs/FLEET_CAPABILITY_MANIFEST_SPEC.md`** (v3) — engineering spec for per-app authz, Atlas-anchored.
7. **`docs/specs/FLEET_CAPABILITY_BUSINESS_SPEC.md`** (v3) — GTM framing of the same, Atlas-anchored.
8. **Archive / handoff docs** — historical unless promoted by `docs/handoffs/CURRENT.md` or this file.

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

## SESSION 1136 — context-kit ops view PARKED

**Final handoff:** [`docs/handoffs/SESSION_1136_OPS_VIEW_PARKED.md`](docs/handoffs/SESSION_1136_OPS_VIEW_PARKED.md)

**TL;DR:** Built a working v1 of `/ops` page on `context-kit start` server (two-panel dashboard, 10-app picker, real blocker/deliverable/deploy-readiness data, Rigby translation-layer review applied). Jessica rejected the dashboard shape: *"feels complicated, hard to even compare these, probably the UI I don't love."* Parked on `clwest/context-kit` branch `feat/jessica-ops-view` (~1360 lines, committed `87c8ae9`, NOT pushed, NOT merged). Data plumbing reusable for any future re-attempt.

**Where it lives:**
- u-d-b: branch `docs/session-1136-ops-view-parked` — this handoff + 1137 entry (PR pending)
- context-kit: branch `feat/jessica-ops-view` — parked code, local only

---

## SESSION 1137 — CURRENT ENTRY POINT

### FIRST THING — Chris decides on the ops view fork

The ops view from Session 1136 is parked. The underlying need (Jessica seeing Claude's work in her terms) still exists. Chris needs to pick one of:

| # | Option | Cost | What survives |
|---|---|---|---|
| 0 | **Redirect entirely** — re-interview Jessica differently before re-attempting | varies | nothing on the branch reused |
| 1 | **Kill** — close the branch, lessons live in the 1136 handoff | 0 | branch unmerged forever |
| 2 | **Radical simplification** — 1 page, no panels, no picker, 3 lines per app | ~30 min | 100% of data plumbing |
| 3 | **Different medium** — CLI `context-kit ops <app>` plain-text card OR daily Slack/Discord snippet | ~1–2 hr | 100% of data plumbing |

**Recommended pre-step:** ask Jessica what she'd ACTUALLY read on her worst Monday morning, BEFORE picking a fork. The audience interview in 1136 captured features but not gestalt (see 1136 handoff §"What we learned" #3).

### Sanity check before any new work

1. `cd ~/development/infra && make up`
2. `make all` (or `make start && make celery` from u-d-b)
3. `make status` — confirm 7 fleet apps + u-d-b all healthy
4. `tools/pa_local.sh "platform_config_tool overview"` — confirm `service_context: local`
5. Read `docs/handoffs/SESSION_1136_OPS_VIEW_PARKED.md` for full session arc

### If Chris picks fork 2 or 3 (reusable code)

The branch `feat/jessica-ops-view` on `clwest/context-kit` (commit `87c8ae9`, local-only) contains:
- `_OPS_KNOWN_APPS` (10 apps)
- `_ops_app_path`, `_ops_active_session` (handoff-derived session number), `_ops_last_handoff`, `_ops_recent_commits` (`git log -5`), `_ops_blockers` (carryover-section parser), `_ops_deliverables` (`gh pr list`), `_ops_deploy_readiness` (5 PASS/FAIL/UNKNOWN checks), `_collect_ops_state`
- All return shapes designed to back any UI format (dashboard, plain-text card, daily snippet)

To revive: `cd ~/development/context-kit && git checkout feat/jessica-ops-view`

### If Chris picks fork 0 or 1 (kill / redirect)

- `git -C ~/development/context-kit branch -D feat/jessica-ops-view` if killing outright
- OR leave the branch indefinitely as documentation of the attempt
- Update `context-kit/docs/proposals/ops-view-page.md` frontmatter `status: parked` → `status: killed` if going full kill

---

## CARRYOVER FROM 1135-PRE — Still queued in parallel

These were the original 1134/1135 candidates. They remain valid and should ship in parallel — none blocked by 1136.

### (Y) Reject-mode flip in unified_pa_chat — STILL queued

**Rigby's lock on the 3-day window**: post-merge, mainline, persistent envs — NOT "since I proved it locally in 1133." The thing being validated is that real callers from main with committed env wiring reliably send fleet HMAC AND no legitimate bearer-only+claim traffic exists. Observability starts after Chris merges the 5 PRs.

**Two paths Rigby will accept**:
- **Default path** — wait for merge + envs in mainline, then start 3-day clock. Lower risk, sharper signal.
- **Staged path** — Stage 1 (immediately) "soft deny" only when routing claim present, behind feature flag; Stage 2 (post-merge + telemetry window) "hard deny."

**Lock from 1132 + 1133**: deny condition is narrow:
```
(fleet_identity is None) AND (routing claim present in body) → 403
```
NOT "no fleet identity ever" — bearer-only must still work for non-fleet callers (Chris's web UI, CLI tests, etc.).

**Pre-flip audit checklist (Rigby's 4 sweeps)** — grep across u-d-b before changing the gate. (See full 1133 close brief if executing.)

**Estimate**: ~half a session + 1 session of audit-sweep work if needed.

### (A) Action-card pre-generation for curated — visible-feature alternative, STILL queued

**Rigby locked the design fork**: child rows (typed `CuratedSignalEntry` rows for actions), NOT payload blob.

**Estimate**: ~1 session. ~10 LLM calls/day per curator run. Curated tab UX gains instant action plans (no "Generate Action" click).

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
bearer_from_fleet = rows.filter(auth_mode='bearer_only').exclude(claimed_app_slug='')
print(f'bearer-only with fleet app_slug claim (72h): {bearer_from_fleet.count()}')
for slug, n in Counter(bearer_from_fleet.values_list('claimed_app_slug', flat=True)).most_common():
    print(f'  {slug}: {n}')
mismatches = rows.filter(match=False)
print(f'mismatches (claimed != verified) 72h: {mismatches.count()}')
"
```

If bearer-only-with-claim count is 0 across all 7 fleet apps for ≥3 days post-merge, (Y) is safe to flip.

---

## CARRYOVER FROM 1135 — Chris ratification track (separate from 1137 primary)

The 54 per-app open decisions + 7 cross-cutting items from Session 1135 are still queued for whichever session Chris green-lights them. See `docs/handoffs/SESSION_1135_FINAL_CLOSE.md` §"Chris's action items" for the full list. Includes:

- **Phase 0 portfolio infrastructure** — `LLMCallLog.workspace` FK + daily $ cap (cross-cutting, all 8 apps)
- **Stripe SKU verification** — 4 Suite products + Contract Concierge
- **Stripe SKU + pricing lock** — SellerPilot, ComplianceSentinel, Signal Studio (LAB tier)
- **Cross-Suite handoff verification** — MentorForge → other Suite products
- **Engine-mismatch resolutions** — Contract Concierge fleet routing, ComplianceSentinel fleet routing
- **Trademark filing on "24/7 Global AI"**

---

## OPERATIONAL NOTES (carry forward)

These are locked in code/tests but worth remembering when touching adjacent areas:

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

---

## CARRYOVERS (open / parked, not blocking)

- **(Y) Reject-mode flip** — see above
- **(A) Action-card pre-gen** — see above
- **Ops view fork decision** — see Session 1137 entry above
- **Capability spec Phase 0 scaffolding** — gated on per-app intent (Session 1135 done)
- **Evidence URL field** — both signal phases ship `url=""`. Cleanest path: enrichment agent populates it. Signal Studio Phase 0 GATING.
- **Semantic `category`** — `pattern_type` is the honest placeholder.
- **`docs/SERVICES.md` drift** — header says 320 service files; reality after 1132 is 336.
- **ai-content-studio#2** — Docker foundation PR. Back burner.
- **24-7-ai-global** — Next.js, not yet Dockerized. Surface for Rigby standalone Phase 1.
- **Per-user filter at u-d-b's replay endpoint** — optional `?user_id=…` query param.
- **DB-dependent tests** for fleet emit predicate + cursor advancement + curator dedup + PA-chat audit — requires test DB with pgvector.
- **context-kit doctor floor:** `10 OK / 2 warnings` (both upstream).
- **`character-os`** — Another Claude Code instance may be active there. Read-only is fine; don't push PRs there. Per Atlas, Phase 4+ parked.

---

## SESSION 1131-1136 HANDOFFS

- [Session 1131 Phase 1 close](docs/handoffs/SESSION_1131_SIGNAL_STUDIO_PHASE_1.md)
- [Session 1131 Phase 2 close](docs/handoffs/SESSION_1131_PHASE_2_SIGNAL_CURATOR.md)
- [Session 1132 close](docs/handoffs/SESSION_1132_LIVE_REFRESH_AND_PA_AUDIT.md)
- [Session 1133 close](docs/handoffs/SESSION_1133_FLEET_PA_SIGNING_BACKPROP.md)
- [Session 1134 close](docs/handoffs/SESSION_1134_CAPABILITY_SPECS_ATLAS_ANCHOR.md)
- [Session 1135 mid-session handoff (superseded)](docs/handoffs/SESSION_1135_APP_DISCOVERY_SPRINT.md)
- [Session 1135 FINAL close](docs/handoffs/SESSION_1135_FINAL_CLOSE.md)
- [Session 1136 ops view PARKED (this entry's prior session)](docs/handoffs/SESSION_1136_OPS_VIEW_PARKED.md)

---

*Last overwrite: Session 1136 PARKED close + Chris directive → 1137 entry (Chris picks ops-view fork: kill / radical-simplify / different medium / redirect; data plumbing on context-kit branch `feat/jessica-ops-view` commit `87c8ae9` reusable for forks 2/3; (Y) reject-mode + (A) action-card stay queued in parallel; Session 1135 ratification track unchanged), 2026-05-23.*
