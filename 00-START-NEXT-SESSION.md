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
8. **`docs/specs/SIGNAL_STUDIO_PAID_INTEREST_SIGNAL_SPEC.md`** (new — Session 1137 F1) — Chris-implementable spec for Decision 13 demand-gate.
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

## SESSION 1137 LANDED — 22 strategic decisions + 4 deliverables

**Final handoff:** [`docs/handoffs/SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md`](docs/handoffs/SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md)

**TL;DR:** Jessica drove a single-session strategic ratification pass through the 54+7 Session 1135 open decisions, landing **22 explicit decisions across 4 phases plus 4 concrete follow-up deliverables**. All 8 app briefs now have `## Session 1137 ratification status` tables appended to §9 showing per-question lock/queue status. Heaviest single-session strategic close in the project's history.

**Pattern across all 22:** revenue-gated triggers + portfolio-consistent pricing + conservative pre-revenue cost discipline + sequenced engineering load + demand-validation gates for non-essential capital + editorial honesty over marketing fluff.

**Where it lives:**
- u-d-b: branch `docs/session-1137-jessica-ratification-1-4` → PR (this entry post-merge)
- mentorforge: separate small PR for F3 BUILD_PLAN drift fix
- 24-7-ai-global: separate small PR for F2 products.ts Team tier truthful blurb

---

## SESSION 1138 LANDED — F1 paid-interest signal implementation

**Final handoff:** [`docs/handoffs/SESSION_1138_F1_PAID_INTEREST_IMPLEMENTATION.md`](docs/handoffs/SESSION_1138_F1_PAID_INTEREST_IMPLEMENTATION.md)

**TL;DR:** Decision 13 demand-gate built end-to-end. `FleetPaidInterest`
table + fleet-HMAC POST endpoint on u-d-b, `paid_interest_status` PA
tool for Jessica, signal-studio backend relay (per-IP rate-limit) +
frontend footer form. Live smoke verified — willing_pay=49 row flips
trigger_state to `ready` correctly.

**Renames Chris ratified mid-session:** generic `FleetPaidInterest`
keyed by `app_slug` (not signal-studio-specific) + `/api/fleet/paid-interest/`
URL (no app slug in path — derived from HMAC). Lets SellerPilot /
ComplianceSentinel reuse the same table when their Decision-13-style
gates come up.

**Honest scope ratification:** Chris pushed back early — signal-studio
has no traffic, so the form will capture no organic signal yet. The
**manual override clause** is the actual working trigger today;
outreach to 5 ICP conversations > waiting on a form. Build was kept
because mechanism is small and ready-for-when-traffic-exists.

**Where it lives:** u-d-b branch `feat/session-1138-paid-interest`
(PR pending), signal-studio branch `feat/paid-interest-form` (PR pending).

---

## SESSION 1139 — CURRENT ENTRY POINT

### Status check before any new work

F1 paid-interest is **fully live including Rigby integration** as of
Session 1138 close. Celery restarted same-session; `pa_local.sh
"paid_interest_status"` returned a 13ms tool run with the expected
JSON envelope. Jessica can ask Rigby "what's the paid-interest signal
status?" today.

Remaining 1138 follow-up: frontend visual smoke (TS build is clean;
browser unverified). Low priority — 5 minutes when Chris is at the
machine: `cd ~/development/signal-studio && docker compose restart
web`, then visit the frontend URL.

### SECOND THING — Chris ratification pass on Session 1137's 22 decisions

Chris reads the 22 Jessica-locked decisions in `SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md` and redlines anything he disagrees with. Especially:

- **Decision 9 cost-attribution rules** (most implementation-heavy; Chris's schema lane)
- **Decision 10 Stripe SKU wiring sequence** (Signal Studio → SellerPilot → ComplianceSentinel) — Chris confirms ordering is feasible given his bandwidth
- **Decision 13 + F1 spec** — F1 IMPLEMENTED Session 1138. Spec file updated to `status: implemented` (DONE). Manual override is the working trigger until signal-studio has traffic.

**No expected redline** on per-product pricing (5-8), GTM channels (15a-c), capital allocation (11, 13, 14), or feature scope cuts (12, 18, 19, 20-22) — those are business-side calls.

### Chris's tech queue (unblocked by Session 1137, parallel execution)

1. **Contract Concierge fleet routing fix** (Q1) — architecture: new agent / extend `legal_doc_drafter_agent` / remove default
2. **Signal Studio engine-side enrichment integration** (Q3) — architecture: v2 question
3. **ComplianceSentinel fleet routing** (Q4) — architecture: `security_agent` / null / skip u-d-b
4. **Engine-mismatch resolutions** (cross-cutting C5)
5. **Phase 0 cost-attribution SCHEMA** — NOW UNBLOCKED. Jessica's business rules in Decision 9 are the input. Chris designs `LLMCallLog.workspace` FK + daily cap enforcement + soft-degrade-to-gpt-5-mini + portfolio kill switch.
6. **SellerPilot Render API Blueprint deployment** — ops
7. **ComplianceSentinel Render API Blueprint deployment** — ops
8. **Rigby products.ts update** — fires when Decision 1 trigger met (currently deferred)
9. **Atlas deviation ratification** (cross-cutting C7) — could be both
10. ~~**F1 Signal Studio paid-interest signal**~~ — IMPLEMENTED Session 1138. See handoff. Next: celery PA worker restart to expose tool to Rigby.
11. **F5 audit** — verify the 4 PitchDeckForge styles meaningfully differ in code (~15 min)
12. **F7 Stripe verification collaboration** — Jessica drives, Chris's Stripe access

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
5. Read `docs/handoffs/SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md` for full session arc

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
- **Format is its own translation axis** — §1.2 governs vocabulary; format-fit (dashboard vs sticker vs CLI) is a separate consideration. (Session 1136 lesson.)
- **Audience interviews need "worst Monday morning" prompt** — Q1-Q6 elicit features but miss format-fit. (Session 1136 lesson.)
- **My on-the-fly rebrand suggestions can be sloppy** — Decision 12 in Session 1137 promised features that don't exist (custom branding, priority queue). Audit existing copy BEFORE proposing rebrand. (Session 1137 lesson, F2 execution.)
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

## SESSION 1131-1137 HANDOFFS

- [Session 1131 Phase 1 close](docs/handoffs/SESSION_1131_SIGNAL_STUDIO_PHASE_1.md)
- [Session 1131 Phase 2 close](docs/handoffs/SESSION_1131_PHASE_2_SIGNAL_CURATOR.md)
- [Session 1132 close](docs/handoffs/SESSION_1132_LIVE_REFRESH_AND_PA_AUDIT.md)
- [Session 1133 close](docs/handoffs/SESSION_1133_FLEET_PA_SIGNING_BACKPROP.md)
- [Session 1134 close](docs/handoffs/SESSION_1134_CAPABILITY_SPECS_ATLAS_ANCHOR.md)
- [Session 1135 FINAL close](docs/handoffs/SESSION_1135_FINAL_CLOSE.md)
- [Session 1136 ops view PARKED](docs/handoffs/SESSION_1136_OPS_VIEW_PARKED.md)
- [Session 1137 Jessica Phases 1-4 ratification (this entry's prior session)](docs/handoffs/SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md)

---

*Last overwrite: Session 1137 close + Jessica 22 decisions + 4 deliverables → Session 1138 entry (Chris ratification pass on Jessica decisions; tech queue unblocked for parallel execution; Phase 5 audit queue carried forward), 2026-05-24.*

*Session 1138 close (2026-05-24, same day): F1 paid-interest signal implemented end-to-end. u-d-b + signal-studio + frontend all touched; live HTTP smoke verified. Next session FIRST THING shifted to celery PA worker restart to expose `paid_interest_status` to Rigby.*

*Session 1138 EXTENDED close (2026-05-24, same day): Chris pushed back that the page wasn't ad-worthy. Round 2 added: LLM summarizer (gpt-5-mini, 19 → 11 distinct insight-grade signals after dedup), `signal_deduper.py` (Jaccard + specific-tag rescue), `signal_summarizer.py` (auto-poll worker, 60s tick, self-maintaining), `/api/summarizer-status` endpoint. **Both PRs merged: u-d-b #2162 (commit 9c8425f9), signal-studio #15 (commit 1e6dbb4).** Total OpenAI spend this session: ~$1.03. Session 1139 entry: upstream clustering quality on u-d-b (multi-day, 85% rejection rate from gpt-5-mini suggests real upstream issue).*
