---
title: "Session 1116 Part 2 — second integration shipped, Channels section launched, Lab Wave 2 + housekeeping"
date: 2026-05-20
status: active
session: 1116
previous_handoff: SESSION_1116_GLOBAL_AI_PIVOT_AND_LIVE_INTEL.md
companion_handoff: SESSION_1116_GLOBAL_AI_PIVOT_AND_LIVE_INTEL.md
---

# Session 1116 Part 2 — second integration shipped, Channels section launched, Lab Wave 2 + housekeeping

> **Read this if** you need the second-half of Session 1116. Part 1
> (linked above) captured the strategic pivot + first u-d-b →
> 247globalai.com integration (live intel panel at `/now`). Part 2
> captures everything that shipped after: the second integration
> (`/shipped` changelog), the new Channels section (5 entries), Lab
> Wave 2 engine reveals (Boardroom + Atelier), domain status
> correction, Fly.io migration plan, and the various small fixes that
> kept the marketing site clean as we extended it.

## TL;DR

Session 1116 kept going after Part 1's handoff merged. **8 more PRs
landed** (13 total across both repos). The marketing site at
`247globalai.com` deepened substantially:

| Aspect | Part 1 state | Part 2 end-state |
|---|---|---|
| Works in Motion | 15 | **22** (+7) |
| Live in Market | 04 | **08** (+4) |
| In the Lab | 08 | **10** (+2 — Boardroom, Atelier) |
| Public-facing routes | `/` + `/now` | `/`, `/now`, **`/shipped`** |
| Lab entries | 8 (5 original + Council/Network/Rigby) | 10 (+Boardroom, Atelier) |
| Channels section | n/a | **new section · 5 entries** |
| Editorial sections (§ 01 → § N) | 7 | **8** (with renumber fix) |
| u-d-b public endpoints | `/api/public/intelligence/now/` | + **`/api/public/changelog/recent/`** |

## What shipped (8 PRs)

### u-d-b (3 merged + 1 parked)

| PR | Title | Status |
|---|---|---|
| #2095 | `feat(changelog): public-read changelog endpoint for 247globalai.com` | ✅ Merged `20fe9a0a` |
| #2096 | `ops(fly): Fly.io migration plan + multi-process fly.toml` | 🅿️ **Open — parked** (operator deferred going live; config + runbook stays as the ready artifact for Jessica when she's ready) |
| #2097 | `docs(atlas): correct domain status — 247globalai.com is owned and live` | ✅ Merged `840d632f` |

### 24-7-ai-global (6 merged)

| PR | Title | Status |
|---|---|---|
| #3 | `chore(stats): bump Live in Market 04 → 07 to reflect Triplet unpause` | ✅ Merged `dbfff5b` |
| #4 | `feat(shipped): /shipped changelog page powered by u-d-b` | ✅ Merged `769d0d0` |
| #5 | `feat(channels): ship Operator Edge as Channel I + new Channels section` | ✅ Merged `d5a0fa2` |
| #6 | `fix(page): renumber downstream sections after Channels insert` | ✅ Merged `9f0e4e7` |
| #7 | `feat(channels): ship Channels II-V — Wire / Dossier / Almanac / Council Sessions` | ✅ Merged `2985bc6` |
| #8 | `feat(lab): wave 2 engine reveal — Boardroom + Atelier` | ✅ Merged `a9a8ecd` |

Plus operator-side commits (@clwest) that landed on `24-7-ai-global` main between Claude's PRs: `3b8e6f3` (wire JobFlow live URL), `248fadf` (revert changelog WIP leak), `1663107` (24-7-ai-global session 001 handoff). All preserved in the merge graph.

## What landed on 247globalai.com

The marketing site (production custom domain, Vercel) now has eight editorial sections:

```
§ 01 — The Charter         (Pillars)
§ 02 — The Suite           (4 buyable products)
§ 03 — Verticals           (3 industry-specific)
§ 04 — The Lab             (10 engine reveals)
§ 05 — Channels            (5 publications)  ← NEW
§ 06 — Around the Clock    (Operations)      ← renumbered from § 05
§ 07 — The Position        (Dossier)         ← renumbered from § 06
§ 08 — Engage              (Commission CTA)  ← renumbered from § 07
```

Plus two standalone routes:
- `/now` — live intelligence wire (PR #1, Part 1)
- `/shipped` — recently-published deliverables ledger (PR #4, this session)

Both still render their AllQuiet/NothingShipped panel until Jessica drops the `PUBLIC_INTEL_TOKEN` env vars.

### The Lab section — 10 entries

| # | Display | subStatus |
|---|---|---|
| VIII | context-kit | OSS |
| IX | Character OS | Pre-Deploy |
| X | SellerPilot | Frontend Live |
| XI | SignalStudio | Frontend Live |
| XII | ComplianceSentinel | Frontend Live |
| XIII | The Council | Internal Use |
| XIV | The Network | Powering /now |
| XV | Rigby | Private |
| **XXI** | **The Boardroom** | **Internal Use** |
| **XXII** | **The Atelier** | **Powering /shipped** |

Gap from XV → XXI is intentional — XVI-XX are Channels (sequential portfolio numbering, not per-section).

### The Channels section — 5 entries (new)

| # | Display | Status | Notes |
|---|---|---|---|
| XVI | The Operator Edge | shipped · Subscribe Open | Newsletter — real, launched April 2026 |
| XVII | The Wire | in-development · Concept | Daily digest from /now signals |
| XVIII | The Dossier | in-development · Concept | Quarterly premium PDF, $29-99/issue |
| XIX | The Almanac | in-development · Planned 2026 | Annual state-of-the-AI-operator report |
| XX | The Council Sessions | in-development · Concept | Podcast/video — hosted, not impersonated |

Section header: "Where the engine speaks." Editorial parallel to `/now` ("what we've noticed") and `/shipped` ("what we've shipped").

## u-d-b new backend (PR #2095)

`feat(changelog): public-read changelog endpoint for 247globalai.com`

- New `core/views_public_changelog.py` — APIView reusing `PublicIntelTokenAuth` from views_public_intelligence
- New `PublicChangelogThrottle` (scope: `public_changelog`, 30/min/IP) — separate bucket from intel so one saturated wire doesn't starve the other
- Filter contract:
  - `publish_intent IN {publish_candidate, publish_required}` — **NEVER** internal_only
  - `status='published'` — NEVER draft/ready/archived
  - `created_at >= now - 30 days`
- Hand-shaped JSON dict — NEVER exposes `workspace`, `initiative`, `dream`, `user`, `source_operation`, `trace_id`, `parent_object_*`, `content_hash`, `slug`, `agent_name`, `content_format`, or full `content`
- 11-test suite — token gating, publish_intent filter, status filter, 30-day window, paranoid body inspection ("ironwood spent 84%" check), payload contract, tag/excerpt truncation, default-off
- Reuses existing `PUBLIC_INTEL_TOKEN` env var — no new operator config needed

## Atlas correction (PR #2097)

`247globalai.com` is owned and live. Five surgical edits in
[`docs/24_7_GLOBAL_AI_APP_ATLAS.md`](../24_7_GLOBAL_AI_APP_ATLAS.md):

- § G "Domain candidates (verify availability)" → "owned and live"
- § G action: trademark check only (.com secured)
- § H Phase 0 #6: trademark check only, effort ~1-2 hr (was ~half day)
- § I "No name lock" → "Soft name lock only" (locked enough to ship)
- § J.1 q#1: "Trademark check on '24/7 Global AI'" (was "Is the brand?")

## Fly.io migration plan (PR #2096 — open, parked)

`fly.toml` (multi-process app config) + `docs/ops/FLY_IO_MIGRATION.md` (12-section runbook). Operator deferred going live; artifacts stay in tree as the ready-to-execute config when Jessica picks the migration up.

Honest cost reality documented in runbook § 8:
- ~$45-60/mo gross at default fly.toml sizes
- ~$25-30/mo lean (drop code_worker to 512MB, run long_running at count=1, merge broadcast into worker)
- **Not** the free-tier escape hatch I framed earlier this session — apologies for that misdirect in the conversation.

PR stays open so it's easy to find later. No deploy work executed against any cloud — pure config + docs.

## Operator state changes captured in memory

[`project_247_global_ai_brand_locked.md`](../../memory/project_247_global_ai_brand_locked.md) updated mid-session:

- `247globalai.com` is owned + live (production custom domain on Vercel, NOT just the vercel.app preview)
- Vercel auto-deploy from the 24-7-ai-global `main` branch lands behind that domain — no DNS work needed for future surfaces
- All 8 marketing-site PRs from this session are visible at production right now

## Notable gotchas captured

- **Branch hygiene mid-session** — operator pushed JobFlow URL + revert + WIP commits to `24-7-ai-global` while Claude was building. Branch was rebased onto current main, Chris's `712a656` WIP commit (changelog scaffolding recovery) preserved in the merge graph with his authorship. Same files we both wrote turned out byte-identical because we both used the panel sketch as source.
- **File watcher quirk** — `Write` tool reported success on `src/lib/changelog.ts` and `src/components/changelog/*.tsx` but they were missing from disk on first `pnpm build`. Re-writing fixed it. Cause unknown but reproducible-once. Worth watching if it happens again.
- **Section numbering drift** — adding `§ 05 — Channels` left existing § 05 (Operations), § 06 (Position), § 07 (Engage) unchanged → duplicate § 05. Fixed in PR #6. Lesson: when inserting a new section by ordinal, always bump all downstream ordinals.

## What's still on the menu (open)

| Bucket | Specifically | Effort |
|---|---|---|
| **Integration #5** | Advisor wisdom hovers on Suite cards | ~3-5 hr — last unhit from original sketch's 5-integration list |
| **Atlas v1 → v2 reframe** | Phase 1 currently says "Rigby standalone"; reality is "u-d-b as engine for the public Suite." Atlas needs the structural rewrite | ~1 hr docs work |
| **Phase 0 cost work** | LLMCallLog.workspace FK + ExternalAPICallLog + cost_per_workspace_today + per-workspace daily cap + build_cost_audit | ~1 week — gates any paid launch |
| **Connection-census detectors** | 7 build_*_audit commands per `CONNECTION_CENSUS_2026_05.md` § K | ~9 days total, highest-leverage: build_route_audit (2 days) |
| **The 4 unbuilt integrations from earlier inventory** | #2 SignalStudio unpause, #3 Rigby chat widget | Per-integration |

## Awaiting others

- **Jessica:** `PUBLIC_INTEL_TOKEN` env var (Railway + Vercel — same token both sides). Once set, `/now` AND `/shipped` light up simultaneously (both use the same token).
- **Jessica:** Fly.io migration if/when (PR #2096 sitting there)
- **You:** Atlas § J open questions (pricing anchors, daily $ cap, what survives the stripped consumer Rigby UI, sports betting fate, integration #5 vs Atlas v2 vs Phase 0 sequencing)

## References

- u-d-b PRs: #2092 (strategy docs), #2093 (intel backend), #2094 (Part 1 handoff), #2095 (changelog backend), **#2096 (Fly.io plan — parked open)**, #2097 (domain correction)
- 24-7-ai-global PRs: #1 (`/now` page), #2 (Lab Wave 1: Council/Network/Rigby), #3 (STATS recount), #4 (`/shipped` page), #5 (Operator Edge as Channel I), #6 (section renumber fix), #7 (Channels II-V), #8 (Lab Wave 2: Boardroom/Atelier)
- Atlas: [`docs/24_7_GLOBAL_AI_APP_ATLAS.md`](../24_7_GLOBAL_AI_APP_ATLAS.md) (now domain-corrected)
- Sketch: [`docs/247_LIVE_INTELLIGENCE_PANEL_SKETCH.md`](../247_LIVE_INTELLIGENCE_PANEL_SKETCH.md) — original 5-integration list
- Fly.io plan: [`docs/ops/FLY_IO_MIGRATION.md`](../ops/FLY_IO_MIGRATION.md) — parked-open in PR #2096
- 24-7-ai-global products source: `/Users/donkeyking/development/24-7-ai-global/src/lib/products.ts` — taxonomy source of truth for the public site
- Part 1 handoff: [`SESSION_1116_GLOBAL_AI_PIVOT_AND_LIVE_INTEL.md`](SESSION_1116_GLOBAL_AI_PIVOT_AND_LIVE_INTEL.md)
