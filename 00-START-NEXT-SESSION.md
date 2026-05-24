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

## SESSION 1135 LANDED — All 8 app briefs shipped + products.ts discovery + 9 PRs merged

**Final handoff**: [`docs/handoffs/SESSION_1135_FINAL_CLOSE.md`](docs/handoffs/SESSION_1135_FINAL_CLOSE.md) (supersedes the mid-session `SESSION_1135_APP_DISCOVERY_SPRINT.md` written before the products.ts discovery)

**8 app briefs all merged to main** + the Colorado Family Law spin-off preserved as future-concept:

| # | App | File | Source of truth |
|---|---|---|---|
| 1 | Rigby standalone | `docs/apps/rigby_standalone_BRIEF.md` | products.ts LAB[7] |
| 2 | Signal Studio | `docs/apps/signal_studio_BRIEF.md` | products.ts LAB[3] |
| 3 | Contract Concierge | `docs/apps/contract_concierge_BRIEF.md` | products.ts PRODUCTS[2] |
| 4 | Mentor Forge | `docs/apps/mentorforge_BRIEF.md` | products.ts PRODUCTS[0] |
| 5 | Pitch Deck Forge | `docs/apps/pitchdeckforge_BRIEF.md` | products.ts PRODUCTS[1] |
| 6 | Deal Flow Tracker | `docs/apps/dealflowtracker_BRIEF.md` | products.ts PRODUCTS[3] |
| 7 | SellerPilot | `docs/apps/sellerpilot_BRIEF.md` | products.ts LAB[2] |
| 8 | ComplianceSentinel | `docs/apps/compliancesentinel_BRIEF.md` | products.ts LAB[4] |
| (concept) | Colorado Family Law Concierge | `docs/apps/colorado_family_law_concierge_FUTURE_CONCEPT.md` | Phase 2+ spin-off (engine exists; product is separate) |

**Critical pattern lesson:** read `24-7-ai-global/src/lib/products.ts` FIRST before hypothesizing product intent from Atlas + fleet routing + handoffs. The mid-session discovery of products.ts (a 606-line hand-authored canonical source of truth for the entire portfolio) reframed the first 3 briefs and unlocked the next 5 without needing Chris's intent input.

**54 open Chris decisions** across the 8 briefs + 7 cross-cutting items — see `SESSION_1135_FINAL_CLOSE.md` §"Chris's action items."

---

## SESSION 1136 — CURRENT ENTRY POINT

### FIRST THING — sanity check before any new work

1. `cd ~/development/infra && make up`
2. `make all` (or `make start && make celery` from u-d-b)
3. `make status` — confirm 7 fleet apps + u-d-b all healthy
4. `tools/pa_local.sh "platform_config_tool overview"` — confirm `service_context: local`
5. Read `docs/handoffs/SESSION_1135_FINAL_CLOSE.md` for full session arc

### PRIMARY TASK options for Session 1136

Discovery sprint is complete (8 of 8 apps briefed). Chris picks Session 1136 focus:

**Option A — Chris ratification pass.** Work through the 54 open §9 decisions across the 8 briefs. Likely batched by theme (Stripe / pricing / cost-attribution / engine-mismatch / cross-Suite handoffs / legal / trademark) rather than one brief at a time.

**Option B — Phase 0 portfolio infrastructure** (the cross-cutting items from the SESSION_1135_FINAL_CLOSE):
- `LLMCallLog.workspace` FK + daily $ cap — shared infra for all 8 (~5-6 days)
- Stripe SKU verification across 4 shipped Suite products (Mentor Forge, Pitch Deck Forge, Contract Concierge, Deal Flow Tracker)
- Stripe SKU + pricing lock across 3 LAB-tier paid products (SellerPilot, ComplianceSentinel, Signal Studio)
- Trademark filing on "24/7 Global AI"

**Option C — Engine-mismatch resolutions** in fleet routing config:
- Contract Concierge → currently routes to `legal_doc_drafter_agent`; should route to commercial-contracts agent
- ComplianceSentinel → currently `null`; decide route to `security_agent` (named in roles) or stay null

**Option D — Cross-Suite handoff verification.** MentorForge → PitchDeckForge / ContractConcierge / DealFlowTracker is the cross-Suite story per products.ts. Verify end-to-end.

**Option E — Colorado Family Law Concierge spin-off exploration** per `docs/apps/colorado_family_law_concierge_FUTURE_CONCEPT.md`. The legal_doc_drafter_agent engine exists; Atlas §H Phase 3 named Colorado family law as a strong PMF candidate. Phase 2+ work — explore further, park, or kill.

### Brief template established by Session 1135 (for any future per-app work)

Each brief lands at `docs/apps/<slug>_BRIEF.md` with these 10 sections:

1. **What it is** — anchored on products.ts pitch + elevator
2. **Who buys it** — products.ts target field
3. **What's built** — table verified against runtime + products.ts features
4. **What proves it's real** — canonical proof + interim local proof + launch-day proof
5. **What's missing** — Phase 0 GATING items (5.1) + other prerequisites (5.2) + not-gaps-but-worth-naming (5.3)
6. **Buildable in one sprint?** — sizing per item
7. **GTM sketch** — channel / pricing / CTA / disclaimers / scope / forbidden
8. **Spokesperson alignment** — Phase 4+ Character OS unpark
9. **Decisions still needed** — closed by products.ts + Jessica + still open for Chris
10. **Honest claim audit** — "we do NOT claim" / "we DO claim" per translation layer §2

`source_of_truth:` field in frontmatter cites the products.ts array index.

### Process learnings (worth keeping for any future per-app brief)

- **products.ts is the canonical public-surface source of truth.** Read it FIRST.
- **Atlas-recommended next-phase positioning ≠ current positioning.** If products.ts marks something `Private` or `in-development`, that's the public-surface status of record.
- **Each fleet repo has its own context-kit pattern** at `docs/PROJECT_WHAT_IT_IS.md`.
- **Spokesperson docs at `docs/spokesperson/`** = editorial source of truth.
- **Fleet routing defaults can be wiring details, NOT product intent.**
- **Phase 0 cost-attribution is portfolio-wide, not per-app.**
- **products.ts-anchored briefs need much less review** than hypothesized briefs.

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
- [Session 1135 mid-session handoff (superseded)](docs/handoffs/SESSION_1135_APP_DISCOVERY_SPRINT.md)
- [Session 1135 FINAL close (this entry's prior session)](docs/handoffs/SESSION_1135_FINAL_CLOSE.md)

---

*Last overwrite: Session 1135 FINAL close → 1136 entry (all 8 app briefs merged; products.ts discovery captured as critical pattern lesson; 54 Chris decisions + 7 cross-cutting items bookmarked in FINAL_CLOSE handoff; 5 path options for Session 1136 listed above; (Y) reject-mode + (A) action-card stay queued in parallel), 2026-05-23.*
