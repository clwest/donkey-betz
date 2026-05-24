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

## SESSION 1135 LANDED — App-by-app discovery sprint started (2 of 8 briefs shipped)

**Full handoff**: [`docs/handoffs/SESSION_1135_APP_DISCOVERY_SPRINT.md`](docs/handoffs/SESSION_1135_APP_DISCOVERY_SPRINT.md)

Discovery pattern validated. Two app briefs landed, both Rigby double-LGTM, both awaiting Chris ratification:

| App | Brief | PR | Open decisions |
|---|---|---|---|
| **Rigby standalone** (Atlas Phase 1 flagship) | `docs/apps/rigby_standalone_BRIEF.md` | [#2147](https://github.com/clwest/donkey-betz-platform/pull/2147) | 6 §9 |
| **Signal Studio Markets edition** (Atlas flagship vertical) | `docs/apps/signal_studio_BRIEF.md` | [#2148](https://github.com/clwest/donkey-betz-platform/pull/2148) | 8 §9 |

**Process pattern (now muscle memory):** Jessica drives discovery in collaborator/ops voice → Claude grounds in Atlas + verified runtime → Rigby reviews (~12 mechanical + ~2 micro fixes per brief) → PR. ~2 hr per brief.

**Bookmarked for Chris:** all 14 open per-app decisions + 6 cross-cutting items consolidated in the 1135 handoff doc under "Chris's action items — consolidated bookmark."

---

## SESSION 1136 — CURRENT ENTRY POINT

### FIRST THING — sanity check before any new work

1. `cd ~/development/infra && make up`
2. `make all` (or `make start && make celery` from u-d-b)
3. `make status` — confirm 7 fleet apps + u-d-b all healthy
4. `tools/pa_local.sh "platform_config_tool overview"` — confirm `service_context: local`
5. Read Session 1135 handoff (above) for full discovery context if resuming with fresh context

### PRIMARY TASK — Continue app discovery sprint (Contract Concierge brief, app 3 of 8)

**Chris's directive** (Session 1134 close, still active):

> *"After everything is anchored I want you and Rigby to begin a
> new session where you guys go through the apps and you tell me
> what we can do with it. I know it's crazy but I want to see if
> you and Rigby can research everything, and create a business
> that has everything I need to start marketing it and you guys
> can build out anything missing."*

### Per-app deliverable (1 doc per app, `docs/apps/<slug>_BRIEF.md`)

For each app, produce:

1. **What it is**: actual product intent, not name-implied. Chris fills or confirms.
2. **Who buys it**: primary user + buyer.
3. **What's built**: real shipping evidence (UI, API, workflows, artifacts).
4. **What proves it's real**: one screenshot / API path / demo step / curl invocation that backs item 3. Forces artifact-backed evidence, not narrative.
5. **What's missing**: gap between "current shipping evidence" and "could sell for real."
6. **Buildable in one sprint?**: small / medium / large / blocked.
7. **GTM sketch**: where customers find it, how they buy, what they pay, what they get.
8. **Spokesperson alignment** (future-state): if/when Phase 4+ activates, which persona + modality fits.

Add `§9 Decisions still needed (escalate to Chris)` and `§10 Honest claim audit` sections per the pattern Sessions 1135 established.

### Order of attack (per Atlas precedence) — updated for Session 1136

1. ~~Rigby standalone~~ — **Done** (PR #2147, awaiting Chris ratification)
2. ~~Signal Studio~~ — **Done** (PR #2148, awaiting Chris ratification)
3. **Contract Concierge** — **Next.** Suite candidate with Draft Library shipped Session 1129; concrete artifact evidence makes discovery faster than apps 4-8.
4. **MentorForge / PitchDeckForge / SellerPilot / DealFlowTracker / ComplianceSentinel** — order by Chris's intent priority (he picks). All 5 have routing-only metadata, no documented intent per Atlas grounding — discovery will need Chris to provide intent first.

### Process per app (Rigby + Claude collaboration)

1. **Rigby reads** what's in u-d-b about the app (fleet routing config, runtime metadata, handoff mentions, any per-app docs).
2. **Rigby produces**: Known for sure / Guessing / Need from Chris — narrowed to this one app, deeper than the Session 1134 grounding pass.
3. **Chris fills gaps** in PA-chat conversation: user, workflow, output, voice, status.
4. **Claude drafts** the brief from grounded intent (not name-extrapolated).
5. **Rigby reviews** the draft for honest framing.
6. **Final brief lands** at `docs/apps/<slug>_BRIEF.md`, workspace-assigned per memory rule.

### Cross-app synthesis (after per-app briefs)

1. **Which app to push to v1 first** after Rigby Phase 1?
2. **Manifest entries** for signal-studio + contract-concierge populated in `config/fleet_agent_routing.json` v3 schema (proof of v3 design under real intent).
3. **Build list** of anything missing — small concrete tickets sized to fit subsequent sessions.
4. **Updated illustrative pricing** in business spec where discovery contradicts current bands.

### Rigby's "Need from Chris" list (from 1134 grounding)

**Global categories** (answer once, applies to all):
1. Intended user + buyer
2. Core workflow(s) + output artifacts
3. Execution posture (analysis-only vs allowed to execute)
4. Data posture (needs spiders? freshness expectations?)
5. Scope boundaries / cross-app calls
6. Brand voice + spokesperson alignment
7. Tier-cut intuition (which dimension defines upgrades?)
8. Status classification (flagship / core SKU / cross-sell / internal / parked)

**Per-app specific questions**: see engineering spec v3 §7 (Primary blocker — fill in next session).

### Out-of-scope for Session 1135

- Implementing the capability bundle (Phase 0 of engineering spec) — comes AFTER 1135 + 1134 (Y) reject-mode flip.
- **No manifest enforcement flips beyond warn-only** during 1135 unless Chris explicitly asks. Keeps discovery from accidentally becoming enforcement work. (Rigby's lock from 1134 close.)
- Character OS / spokesperson work — Atlas Phase 4+, parked.
- New fleet app slugs — work with the 8 surfaces that exist.
- Marketing copy beyond GTM sketches — follow-on session once intent locked.

---

## CARRYOVER FROM 1134-PRE — Still queued in parallel

These were the original 1134 candidates from the 1133 close. They remain valid and should ship in parallel with Session 1135's discovery work — neither blocks the other.

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
- **Capability spec Phase 0 scaffolding** — gated on Session 1135 discovery filling per-app intent for signal-studio + CC
- **Evidence URL field** — both signal phases ship `url=""`. Cleanest path: enrichment agent populates it. **Session 1135 elevated this to Signal Studio Phase 0 GATING** — without source URLs, brief sentences can't link to provenance and the briefing's credibility suffers.
- **Semantic `category`** — `pattern_type` is the honest placeholder.
- **`docs/SERVICES.md` drift** — header says 320 service files; reality after 1132 is 336.
- **ai-content-studio#2** — Docker foundation PR. Back burner.
- **24-7-ai-global** — Next.js, not yet Dockerized. Surface for Rigby standalone Phase 1.
- **Per-user filter at u-d-b's replay endpoint** — optional `?user_id=…` query param.
- **DB-dependent tests** for fleet emit predicate + cursor advancement + curator dedup + PA-chat audit — requires test DB with pgvector.
- **context-kit doctor floor:** `10 OK / 2 warnings` (both upstream).
- **`character-os`** — Another Claude Code instance may be active there. Read-only is fine; don't push PRs there. Per Atlas, Phase 4+ parked.

---

## SESSION 1131-1135 HANDOFFS

- [Session 1131 Phase 1 close](docs/handoffs/SESSION_1131_SIGNAL_STUDIO_PHASE_1.md)
- [Session 1131 Phase 2 close](docs/handoffs/SESSION_1131_PHASE_2_SIGNAL_CURATOR.md)
- [Session 1132 close](docs/handoffs/SESSION_1132_LIVE_REFRESH_AND_PA_AUDIT.md)
- [Session 1133 close](docs/handoffs/SESSION_1133_FLEET_PA_SIGNING_BACKPROP.md)
- [Session 1134 close](docs/handoffs/SESSION_1134_CAPABILITY_SPECS_ATLAS_ANCHOR.md)
- [Session 1135 close (this entry's prior session)](docs/handoffs/SESSION_1135_APP_DISCOVERY_SPRINT.md)

---

*Last overwrite: Session 1135 close → 1136 entry (continue discovery sprint with Contract Concierge; 14 Chris decisions from 1135 briefs bookmarked in handoff; (Y) reject-mode + (A) action-card stay queued in parallel), 2026-05-23.*
