---
title: "Session 1116 Part 1 — 24/7 Global AI strategic pivot + live intel panel shipped"
date: 2026-05-20
status: superseded-by-companion
session: 1116
previous_handoff: SESSION_1115_CODE_HEALTH_REFACTORS.md
companion_handoff: SESSION_1116_PART_2_INTEGRATIONS_AND_CHANNELS.md
---

> **Heads up — this is only Session 1116's first half.** The session
> kept going after this handoff was written and added 8 more PRs
> (second integration `/shipped`, new Channels section, Lab Wave 2,
> domain corrections, Fly.io migration plan, section renumber fix).
> Part 2 is documented in
> [`SESSION_1116_PART_2_INTEGRATIONS_AND_CHANNELS.md`](SESSION_1116_PART_2_INTEGRATIONS_AND_CHANNELS.md).
> Read both for the complete Session 1116 picture.

# Session 1116 Part 1 — 24/7 Global AI strategic pivot + live intel panel shipped

> **Read this if** you need the May 2026 brand-pivot context — Donkey Betz
> → 24/7 Global AI, why the Character OS merge got parked, and how u-d-b
> now powers the marketing site at `/now`. Two strategy docs landed,
> three PRs shipped, two repos touched.

## TL;DR

Strategic session that flipped from "decompose the monolith" to "ship one
polished product, keep the monolith as the engine":

| What | Where it landed |
|---|---|
| **Brand pivot framing** — Donkey Betz → 24/7 Global AI | `docs/24_7_GLOBAL_AI_APP_ATLAS.md` (v1) |
| **Merge-readiness audits** (cost / connections / telemetry / prep) | `docs/COST_SURVIVAL_AUDIT.md`, `docs/CONNECTION_CENSUS_2026_05.md`, `docs/TELEMETRY_PLAN_2026_05.md`, `docs/MERGE_PREP_TIER_4.md` |
| **Character OS merge parked** | Counter-proposal stays in tree; Slice 4 (avatar realtime) becomes a v2 unlock for when a paying customer asks for a face |
| **First u-d-b → public surface integration shipped** | Live intel panel at `/now` on 247globalai.com — backend PR #2093 + frontend 24-7-ai-global PR #1, both merged |

Three PRs merged in this session: **#2092** (8 strategy docs), **#2093**
(public-intel backend endpoint), and **24-7-ai-global #1** (`/now` page).

## The strategic arc — how the framing moved

1. **Started with:** "Donkey Betz is too big, break it into apps." Atlas v0
   proposed Suite + Verticals + Lab carved out of the u-d-b monolith.
2. **Realized halfway through:** Chris already built and deployed
   `24-7-ai-global` (Next.js + Vercel) **today** with a locked Suite of 4
   (PitchDeckForge, DealFlowTracker, Contract Concierge, MentorForge),
   3 Verticals (AI Content Studio, VehicleMatch, JobFlow), and 5 Lab
   entries (context-kit, Character OS, founder-toolkit triplet). **u-d-b
   and Rigby are not in the public taxonomy.**
3. **Reframe:** u-d-b is **the engine** that powers the public Suite, not
   a 13th product competing with them. The five integration ideas in
   `docs/247_LIVE_INTELLIGENCE_PANEL_SKETCH.md` § C.5 are the new path.
4. **Atlas v1:** narrowed Phase 1 from "Legal + Markets + Studio + flagship"
   to "Rigby standalone only" — but on second thought (driven by the
   24-7-ai-global discovery), even that is deferred. **No new product is
   the Phase 1; powering the existing public Suite is the Phase 1.**

## What shipped (code)

### Backend — PR #2093 (squash-merged as `83711686`)

`feat(intel): public-read intelligence endpoint for 247globalai.com`

- `core/views_public_intelligence.py` (new, 148 LOC)
  - `PublicIntelligenceNowView` (`APIView`, AllowAny + `PublicIntelTokenAuth`)
  - `PublicIntelTokenAuth` — header `X-Intel-Token` matched against
    `settings.PUBLIC_INTEL_TOKEN`. **Default-off** — empty env var rejects
    every request.
  - `PublicIntelThrottle` — 30 reqs/min/IP via `SimpleRateThrottle`.
  - `_public_cluster_dict` — hand-shaped JSON dict. NEVER serializes
    `spider_data_ids`, `sample_signals`, or `trigger_event_ids`.
  - `PUBLIC_PATTERN_TYPE_WHITELIST` — 7 pattern types. The 3
    "weakness-shaped" patterns (`knowledge_gap`, `content_gap`,
    `user_need`) are filtered out — not marketing-appropriate.
- `core/urls.py` — `GET /api/public/intelligence/now/` registered
- `core/settings.py` — `PUBLIC_INTEL_TOKEN = os.environ.get(...)` added
- `core/tests/test_public_intel_endpoint.py` (new, 9 tests):
  - Token required, wrong token rejected, valid token 200
  - Pattern whitelist + 24h window filter
  - **Paranoid field redaction** (parsed JSON + raw body inspection)
  - Payload contract shape exact match
  - Keywords ≤6 + ≤40 chars each
  - Stats top-pattern aggregation
  - Default-off behavior when token env empty (separate test class)

**Local verification:** full test suite blocked by known local Postgres
password gap (Session 1115 § J). **Import smoke test confirmed:** view
+ test imports clean, URL reverses to `/api/public/intelligence/now/`,
whitelist sized correctly. CI ran the full suite green.

### Frontend — 24-7-ai-global PR #1 (squash-merged as `5f0e505`)

`feat(now): live intelligence panel at /now powered by u-d-b`

- `src/lib/intel.ts` (new) — typed fetch wrapper, 5-min ISR, pretty
  source names, relative-time formatter, graceful null on missing env
  or upstream failure
- `src/app/now/page.tsx` (new) — server component matching homepage
  editorial aesthetic (Plate 02 caption, rise animation, gold/ink/cream)
- `src/components/intel/ClusterCard.tsx` (new) — per-cluster card with
  strength/confidence/novelty ladder, keywords, source breakdown
- `src/components/intel/IntelStatsStrip.tsx` (new) — 3-stat editorial
  strip
- `src/components/intel/AllQuietPanel.tsx` (new) — graceful empty +
  outage state
- `src/components/SiteHeader.tsx` — "Now" added to `DEFAULT_NAV`
  between The Lab and Operations

**Build verification:** `pnpm build` green. `/now` in route table with
`Revalidate: 5m, Expire: 1y` — ISR configured. Static prerender at build
time exercised the AllQuietPanel failure path (no env vars → null
fetch → AllQuietPanel render).

### Strategy docs — PR #2092 (squash-merged as `1304dbab`)

Eight docs landed in one PR (zero runtime change):

| Doc | What it is |
|---|---|
| `docs/MERGE_PROPOSAL_CHARACTER_OS.md` | Sidecar variant of Character OS merge (pre-pivot context) |
| `docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md` | Native variant (5 slices). **Now parked** — v2 backlog. |
| `docs/COST_SURVIVAL_AUDIT.md` (Tier 1) | 4 ✗ rows: ElevenLabs/Stability/Runway/Replicate calls fire but cost is never persisted. **Gates** restoring OpenAI credits on shipping per-workspace cost telemetry. |
| `docs/CONNECTION_CENSUS_2026_05.md` (Tier 2) | 8-surface stranded-vs-connected survey; applies Session 1115's "detectors are wrong on first pass" lesson. Proposes 7 new audit commands. |
| `docs/TELEMETRY_PLAN_2026_05.md` (Tier 3) | Telemetry roadmap |
| `docs/MERGE_PREP_TIER_4.md` | Tier 4 workstream prep |
| `docs/24_7_GLOBAL_AI_APP_ATLAS.md` (v1) | Soft-cut architecture, Phase 1 = Rigby standalone only, Character OS parked, verticals deferred to Phase 3+ |
| `docs/247_LIVE_INTELLIGENCE_PANEL_SKETCH.md` | Architecture sketch for the integration that shipped in this session |

## Operator action required (Jessica)

The endpoint is **default-off** until two env vars land:

```bash
# 1. Generate one shared token (anywhere)
openssl rand -hex 16

# 2. Railway, u-d-b production (web service):
PUBLIC_INTEL_TOKEN=<token>

# 3. Vercel, 24-7-ai-global project (Production + Preview):
UDB_API_URL=https://donkey-betz-platform-production.up.railway.app
UDB_PUBLIC_INTEL_TOKEN=<same token>

# 4. Verify:
curl -H "X-Intel-Token: <token>" https://donkey-betz-platform-production.up.railway.app/api/public/intelligence/now/
# expect: 200 with JSON

curl https://donkey-betz-platform-production.up.railway.app/api/public/intelligence/now/
# expect: 401
```

Until that ships, `/now` renders `AllQuietPanel` with "the wire is dark for
a moment" — by design, on-brand, safe.

**Kill-switch:** unset `PUBLIC_INTEL_TOKEN` on Railway → endpoint 401s
within ~5 min (Vercel ISR cache expiry).

## What didn't get done this session

- **Phase 0 cost-survival work** (still gating, but not started). The 4
  ✗ rows in COST_SURVIVAL_AUDIT § A are blockers for any multi-tenant
  pricing — `LLMCallLog.workspace` FK + `ExternalAPICallLog` model +
  per-workspace daily cap + `cost_per_workspace_today` query.
- **The other 4 integration ideas** from
  `docs/247_LIVE_INTELLIGENCE_PANEL_SKETCH.md` § C.5:
  - **#2** Unpause SignalStudio by pointing it at u-d-b's spider feed
  - **#3** "Talk to 24/7 Global AI" Rigby chat widget (gated)
  - **#4** Live "what's shipping" panel from Initiative pipeline
  - **#5** Advisor wisdom → contextual help on Suite products
- **Atlas § J open questions** — pricing anchors, daily $ cap defaults,
  what survives the stripped consumer Rigby UI, sports betting fate
- **`products.ts` modification** on 24-7-ai-global main — small change
  was in working tree at branch cut; left untouched per system reminder.
  Chris should commit or revert it separately.

## Next-session entry points

1. **Wait for Jessica's env-var setup**, then verify `/now` renders real
   signals (not AllQuietPanel) on 247globalai.com.
2. **Pick the next integration** from the 5-item list. Recommended order
   given current state:
   a. **#4 Initiative changelog panel** — same architecture pattern as
      `/now`, ~2-3 hr, zero new infra.
   b. **#5 Advisor wisdom hovers** — also zero new infra; high
      brand-amplifying value across every Suite product page.
   c. **#3 Chat widget** — biggest conversion bet but needs rate-limit
      thinking + cost gate.
   d. **#2 SignalStudio unpause** — separate repo, larger surface, do
      this only if Chris wants to unpause the founder-toolkit triplet.
3. **Phase 0 cost work** — if/when Chris is ready to start enabling paid
   surfaces. Roughly a week of focused work.

## Notable gotchas captured

- **`get_pattern_type_display()` works at runtime but Pyright doesn't
  see it.** Use `dict(SignalCluster.PATTERN_TYPE_CHOICES).get(...)` as
  the typed alternative when adding new public-surface views.
- **`SPIDER_REGISTRY` is not a module-level constant.** Use
  `from ai_core.spiders.spider_registry import get_spider_registry`
  and call `.list_spiders()` for the count.
- **Local Postgres password gap persists** — full test runs can't happen
  on Chris's machine. Workflow: write the test, run an import smoke test
  locally, push to CI for the real run.

## Memories saved this session

- [Jessica owns deployment, may move off Railway](../../memory/project_jessica_deployment_owner.md)
- [24/7 Global AI brand locked + Suite/Verticals/Lab structure live](../../memory/project_247_global_ai_brand_locked.md)

## References

- u-d-b backend PR: https://github.com/clwest/donkey-betz-platform/pull/2093
- 24-7-ai-global frontend PR: https://github.com/clwest/24-7-ai-global/pull/1
- Strategy-docs PR (8 docs): https://github.com/clwest/donkey-betz-platform/pull/2092
- Atlas v1: `docs/24_7_GLOBAL_AI_APP_ATLAS.md`
- Live intel sketch: `docs/247_LIVE_INTELLIGENCE_PANEL_SKETCH.md`
- Cost survival gate: `docs/COST_SURVIVAL_AUDIT.md` § J
- 24-7-ai-global live taxonomy source: `/Users/donkeyking/development/24-7-ai-global/src/lib/products.ts`
