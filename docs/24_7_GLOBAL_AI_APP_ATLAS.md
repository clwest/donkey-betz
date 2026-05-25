<!-- DOC-POINTER-V1 (Session 1146) -->
> **Canonical strategy anchor — refresh-in-place; do not move.**
> Listed in `CLAUDE.md` + `00-START-NEXT-SESSION.md` as the platform's strategy anchor. Counts in this doc are narrative (Atlas-level: phase definitions, pricing bands, graduation rules); for runtime platform counts see [`docs/PLATFORM_INVENTORY.md`](PLATFORM_INVENTORY.md) (per `DOC_LIFECYCLE.md` §2c sole-counts-source rule).
> **Last reviewed for drift labeling:** Session 1146 (2026-05-25)
> **Companion canon:** [`docs/canon/INDEX.md`](canon/INDEX.md) (canon registry) + [`docs/INDEX.md`](INDEX.md) (doc corpus index) + [`docs/PLATFORM_WHAT_IT_IS.md`](PLATFORM_WHAT_IT_IS.md) (narrative anchor).

# 24/7 Global AI — App Atlas (v1)

**Date:** 2026-05-20
**Author:** Claude Code, Session 1116
**Status:** **v1 — Rigby-standalone Phase 1 locked.** Verticals deferred to Phase 3+. Operator + Rigby still need to shape pricing and timeline.
**Revision:** v0 → v1 — narrowed Phase 1 from "Legal + Markets + flagship" to "Rigby standalone only," parked the Character OS merge, pushed all verticals to Phase 3+.
**Companion docs:** [`COST_SURVIVAL_AUDIT.md`](COST_SURVIVAL_AUDIT.md), [`CONNECTION_CENSUS_2026_05.md`](CONNECTION_CENSUS_2026_05.md), [`MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) *(parked)*

> **Atlas v1 ratification — Session 1137 + 1141 (2026-05-24).**
> Atlas v1 (this doc, Session 1116) defined Phase 1 = Rigby standalone
> and parked verticals to Phase 3+. Subsequent Atlas-implied decisions
> (pricing per app, cost-attribution rules, take-public trigger,
> trademark, graduation rules, GTM channels, persona naming) were
> locked by Jessica in Session 1137 (22 decisions across 4 phases)
> and ratified by Chris in Session 1141 (17 accept-as-written + 3
> ratify-shipped + 2 with Jessica clarification redlines).
>
> **Atlas-relevant decisions worth knowing:**
> - **Decision 1** (take-public): defer Rigby launch until ≥2 Suite products at ≥$500 MRR each AND concrete Rigby standalone answer
> - **Decision 2** (24/7 Global AI trademark): wait, same trigger as Decision 1
> - **Decision 4** (Suite vs LAB graduation): revenue-only, ≥$1K MRR sustained ≥2 months
> - **Decision 5** (Rigby pricing): $30/mo (top of the $20-30 Atlas band)
> - **Decisions 6/7/8** (Suite Pro/Team pricing for SS/SP/CS): see SESSION_1137 handoff
> - **Decision 9** (cost attribution): formal rules supersede Atlas Phase 1's "~$1.50/day per-account cap"
> - **Decision 10** (Stripe SKU wiring): 1-by-1 — Signal Studio → SellerPilot → ComplianceSentinel
> - **Decision 13** (Signal Studio legal demand-gate): F1 spec shipped Session 1138
> - **Decisions 15a-c** (GTM channels per product): see SESSION_1137 handoff
>
> Full decision text + Chris's tech-feasibility scan + Jessica
> clarification redlines: [`SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md`](handoffs/SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md)
> + [`SESSION_1141_JESSICA_RATIFICATION_DEEP_DIVES.md`](handoffs/SESSION_1141_JESSICA_RATIFICATION_DEEP_DIVES.md).
> Atlas's strategic shape (Rigby Phase 1 first, verticals deferred,
> Character OS Phase 4+) is unchanged by these decisions — they refine
> the *how* and *how much*, not the *what*.

---

## TL;DR

1. **Brand:** Donkey Betz → **24/7 Global AI**. Sports betting demotes from headline product to one of many verticals (or gets cut entirely).
2. **Cut style:** **Soft cut.** Monorepo stays. Shared core (Django + Postgres + Celery + spider runtime + agent registry). Each app gets its own front-end persona, route prefix, billing tier, and *can* later split to its own deploy without rewriting.
3. **Phase 1 flagship: Rigby = "24/7 Global AI", shipped standalone.** Text only, no avatar, no vertical add-ons. The personal AI assistant with 101 tools, 80 spiders feeding it, 83 agents it can dispatch. Ship one polished product before fragmenting attention across verticals.
4. **Hard prerequisite:** the 4 ✗ rows in `COST_SURVIVAL_AUDIT.md` § A get fixed *before* any external SaaS launch. Without per-workspace cost attribution, multi-tenant pricing is uninsurable.
5. **Two-thirds of the existing monolith is *not* customer-facing.** Spider network, body systems, signal aggregation, advisor council, initiative pipeline, self-awareness — these are *infrastructure that powers the apps*, not apps themselves. The Atlas separates the two cleanly.
6. **8 standalone sibling apps already exist outside this repo.** They're part of the answer, not the problem. Some plug into 24/7 Global AI; some stay independent.
7. **Character OS merge is parked.** The architectural design (`MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`) stays in tree as a v2 unlock for when Rigby has revenue and customers ask for a face. Slice 3 (general-purpose video finishing layers) is the only piece that could ship independently — and only if Phase 1 has bandwidth left over (it won't).
8. **Verticals (Markets, Content, Studio, Legal) defer to Phase 3+.** They exist in the platform today and stay reachable inside Rigby's tool surface for power users — they just aren't packaged as paid products until after Rigby converts paying customers.

---

## A. The strategic shift, framed honestly

### What changed

- **Donkey Betz brand → 24/7 Global AI.** Sports/betting was the original wedge; the platform grew beyond it. The brand now under-sells what's been built (a multi-agent intelligence + content + studio platform). "24/7 Global AI" describes what it actually is.
- **Monolith → portfolio.** Today: one Django app, one frontend, 11 Procfile processes, 570 models, 2,164 URL routes, 397 Celery tasks. Hard to demo, harder to sell, impossible to price per-feature.
- **Survival mode.** Per memory `project_current_state_2026_04.md`: out of OpenAI credits, money to replenish currently zero, stepping back from features. Decomp must produce *shippable* income, not architecture-astronomy.

### What does NOT change

- Source-of-truth precedence: `PLATFORM_INVENTORY.md` > `PLATFORM_WHAT_IT_IS.md` > everything else.
- The codebase. **Soft cut.** No giant migration. No new repos. Files stay where they are. We add **app-boundary annotations** and **per-app frontend personas**, not new packages.
- Rigby. She stays the conversational front door across every app in the portfolio.

---

## B. Soft cut — what it means technically

This is the architectural decision the Atlas is built on. If this is wrong, everything below is wrong.

### B.1 What "soft cut" means

| Concern | Soft cut answer |
|---|---|
| Repo | One repo (this one) |
| Database | One Postgres + pgvector (one) |
| Redis | One Redis cluster (3 DB indices) |
| Backend code | One Django project, one `core/` directory |
| Backend deployment | Same 11 Procfile processes |
| Celery workers | Shared workers, queues can be partitioned per-app later |
| Frontend | One React app, **multiple personas** (different landing, nav, theme, route prefix per app) |
| Billing | One Stripe account, **per-app product/plan**, per-workspace meter |
| Cost telemetry | Per-workspace + per-app attribution (requires `LLMCallLog.workspace` FK + `ExternalAPICallLog` — see § F) |
| URL routing | `app.247globalai.com/{flagship,markets,content,studio,legal,...}` — single deploy, persona resolved by subdomain or path prefix |

### B.2 What a "soft cut" app actually IS

An app under 24/7 Global AI is a **bundle** of:

1. **A persona slug** (`flagship`, `markets`, `content`, `studio`, `legal`, ...)
2. **A frontend persona** — landing page, branded layout, focused nav (subset of the 50-route App.tsx)
3. **An allow-list of PA tools and agents** the assistant can use in this app's context
4. **A billing product** in Stripe (plan, price, included credits)
5. **A scoped workspace bootstrap** — when user creates account on `markets.247globalai.com`, they get a Workspace pre-loaded with finance-relevant settings
6. **A telemetry tag** so `LLMCallLog` and `ExternalAPICallLog` records know which app generated the cost

That's it. No new Django apps. No new repos. No new databases. Just **app boundary as configuration**.

### B.3 Why soft cut (and not hard cut)

| Reason | Detail |
|---|---|
| Budget | Per `COST_SURVIVAL_AUDIT.md`, OpenAI credits are off. Hard cut = 5+ new Railway services × $5-20/mo each + auth wrappers + DB-per-app. Soft cut = same bill |
| Time | Hard cut is a 3-6 month rewrite. Soft cut is 2-4 weeks per app (mostly frontend + billing) |
| Reuse | Agents, spiders, advisors, body systems, signals — every app benefits. Hard cut means duplicating or building a shared service layer (which becomes a new monolith) |
| Reversibility | Soft cut → hard cut is straightforward once an app proves traction. Hard cut → soft cut is a nightmare |

### B.4 When soft cut breaks (the limits to acknowledge)

- **Noisy-neighbor on Celery.** One app's runaway agent dispatch can starve another app. Mitigation: per-app queues + per-workspace budget caps (§ F).
- **Schema drift pressure.** If "Markets" wants a custom `MarketSnapshot` model and "Studio" wants a custom `VideoTimeline` model, the shared DB grows. Mitigation: each app's models live in its own module (`markets/models.py`, `studio/models.py`), enforced by review.
- **Auth/permissions.** A user with a Markets-only sub shouldn't see Studio in the nav. Mitigation: per-workspace feature flags + per-app frontend persona.
- **Bundle size.** One React build serving 5 personas balloons. Mitigation: code-split per persona, lazy-load by route.

---

## C. Flagship recommendation — Rigby = "24/7 Global AI"

### C.1 Why Rigby, not Markets or Content

I looked at every candidate. Scored on five dimensions: brand fit, defensibility, monetization clarity, time-to-revenue, alignment with what's actually built.

| Candidate | Brand fit | Defensible vs incumbents | Monetization | Time-to-rev | Built? | Score |
|---|---|---|---|---|---|---|
| **Rigby (PA)** | ★★★★★ | ★★★★☆ (101 tools + agents + spiders is uncommon) | ★★★★☆ ($20-50/mo SaaS) | ★★★★☆ (needs billing + persona) | ★★★★★ | **22/25** |
| Markets/Stocks | ★★★★☆ | ★★★☆☆ (vs Koyfin, Stockanalysis.com) | ★★★★★ ($50-200/mo) | ★★★☆☆ (needs polish) | ★★★★☆ | 19/25 |
| Content pipeline | ★★★☆☆ | ★★★☆☆ (vs Copy.ai, Jasper) | ★★★☆☆ ($30-100/mo) | ★★☆☆☆ (needs UX work) | ★★★★☆ | 15/25 |
| Studio (video/audio) | ★★★☆☆ | ★★★☆☆ (vs ElevenLabs direct, Synthesia) | ★★★★☆ (per-render or sub) | ★★☆☆☆ (cost-blocked) | ★★★★☆ | 16/25 |
| Operator Edge (newsletter) | ★★☆☆☆ | ★★★★☆ (audience already validated) | ★★★☆☆ (Substack/Patreon-style) | ★★★★★ (live) | ★★★★★ | 19/25 |
| Sports betting | ★☆☆☆☆ (brand explicitly demoting) | ★★☆☆☆ (legal complexity) | ★★★☆☆ | ★★☆☆☆ | ★★★★☆ | 12/25 |

### C.2 The Rigby pitch — one sentence

> **"24/7 Global AI is your personal AI assistant that never sleeps — it watches 80 global data sources, has 80+ specialised agents on call, and 100+ tools so it can actually *do things*, not just talk."**

That sentence is buildable today against the current platform. Every claim is runtime-verifiable.

### C.3 Why this naming works architecturally

If the **flagship is Rigby**, then "verticals" become natural sub-products:

- **24/7 Markets** — "Rigby + the finance toolkit." Same assistant, scoped to stock/crypto/economic spiders, finance agents, market alerts.
- **24/7 Studio** — "Rigby + the creative toolkit." Same assistant, scoped to image/video/audio generation tools, content writer + editor agents.
- **24/7 Content** — "Rigby + the publishing toolkit." Same assistant, scoped to content deliberation, evidence cards, editorial gate.
- **24/7 Legal** — "Rigby + the legal toolkit." Same assistant, scoped to legal doc drafter, court spiders, parenting-time templates.
- **24/7 Dev** — "Rigby + the build toolkit." Same assistant, scoped to code agents, refactor tools, Founder Toolkit lineage.

The customer mental model becomes: **"It's the same AI, with different specialties you unlock."** That's a clean upsell ladder vs. "buy five separate apps."

### C.4 What this means for Operator Edge

Operator Edge stays — but as a **marketing channel and content product**, not a competing flagship. It's the newsletter where 24/7 Global AI's intelligence gets distilled for human readers. Subscribers there are the funnel into the SaaS.

### C.5 What Phase 1 explicitly does NOT include

To keep Phase 1 sharp and the runway intact:

- **No avatar, no face, no voice.** Text chat only. Avatar is a Phase 4+ upsell when revenue supports it. See Character OS parked decision (§ J).
- **No vertical apps as packaged products.** Markets, Content, Studio, Legal stay reachable inside Rigby's tool surface for power users — they just don't have their own landing pages, billing tiers, or marketing in Phase 1.
- **No Character OS merge.** Slices 1-5 of the avatar plan are deferred. The doc stays as a v2 backlog.
- **No Operator Edge restructure.** The newsletter keeps publishing on its current cadence; treat it as marketing for Rigby, not a product to re-platform.
- **No Discord bot expansion.** 96 existing commands stay; no new surfaces.
- **No new agent rotations or beat tasks.** Per memory `feedback_agent_noise.md`.
- **No sibling-repo integration work.** DealFlowTracker, PitchDeckForge, etc. stay independent. Cross-sell later, not now.

The bet: **one polished, paying product > five half-built products.**

---

## D. The Atlas — every shippable surface, classified

Notation: `[T]` = ships today, `[W]` = needs work (weeks not months), `[A]` = aspirational / partially built. Numbers tie back to `PLATFORM_INVENTORY.md` headline counts.

### Tier 1 — The Engine (foundation, never decomposed)

| Surface | What it is | Status | Notes |
|---|---|---|---|
| Django core + Postgres + pgvector | The app server, the DB | [T] | 570 models, single connection pool |
| Redis (3 DBs) | Cache, broker, channels | [T] | — |
| Celery (11 processes) | Worker fleet, beat | [T] | Per `Procfile`. Memory-tuned hard for Railway 512MB |
| Spider runtime (`ai_core/spiders/`) | 80 spiders, 41 categories | [T] | The intelligence layer. Powers every app. |
| Agent registry (`AGENT_MAP`, 83 agents) | 73 enabled, 8 rerouted, 1 blocked | [T] | Dispatchable from PA, beat rotations, initiative pipeline |
| LLM router (`core/services/agent_llm_router.py`) | 6 providers, fallback chains | [T] | OpenAI, Anthropic, Together, DeepSeek, Gemini, Ollama |
| Body systems (`BodyCoordinator`) | 9 health subsystems | [T] | Internal observability. Probably never customer-facing |
| Signal aggregation | 10 SignalCluster pattern types | [T] | Spider → signal → initiative bridge |
| LearningBridge ABC + 9 bridges | Cross-system learning | [T] | Closed Session 1115 |
| Initiative pipeline (5 stages) | Dreams → Actions | [T] | Long-running orchestration |

**Engine never decomposes.** It's plumbing that serves every app above.

### Tier 2 — The Brain (the flagship surface)

| Surface | What it is | Status | Notes |
|---|---|---|---|
| **Rigby (PA)** | GPT-5.2 function calling, 101 schemas, 166 handlers | [T] | The product surface for "24/7 Global AI" the brand |
| PA tool dispatcher (`core/services/tool_dispatcher.py`) | Routes LLM tool calls to handlers | [T] | 166 handlers |
| PA enrichment pipeline (8 services) | Context bundling, deliverables, workspace memory | [T] | Per `unified_pa_entrypoint.py` |
| Workspace model | 5-tab modular workspace UI | [T] | `FilesTab`, `WorkTab`, `IntelligenceTab`, `SystemTab`, `HomeTab` |
| Command Center | PA chat surface | [T] | `frontend/src/pages/CommandCenterPage.tsx` |
| Conversation memory | Persistent per-conversation state | [T] | Pgvector-backed |
| Workspace files (preview / edit / history) | File surface in workspace | [T] | Session 1110+ work |

**This is the product.** Everything in Tier 1 feeds it.

### Tier 3 — The Verticals (5 apps under 24/7 Global AI brand)

Each vertical is a **persona** of Rigby plus a curated tool-set + agent-set + scoped spiders + frontend persona. None require new repos.

#### 3.1 — 24/7 Markets

| Component | Source | Status |
|---|---|---|
| Stock dashboard | `frontend/src/pages/StockIntelligencePage.tsx` | [T] |
| Crypto/markets nav | Existing `BettingPage.tsx` repurposed | [W] |
| Finance spiders (7) | `polygon`, `finnhub`, `sec_edgar`, `coingecko`, `etherscan`, `yahoo_finance`, `financial` | [T] |
| Stock agents (12) | BullCase, BearCase, MarketAnomalyDetector, SignalScanner, StockAuditCoordinator, InstitutionalWatcher, etc. | [T] |
| PA tools (subset) | `stock_tool`, `market_movement_tool`, `signal_cluster_tool` (verify present) | [T-W] |
| Brief generation | Existing stock briefs pipeline | [T] |
| Per-app frontend persona | New (route prefix + landing) | [W] |
| Billing tier | New (Stripe product) | [W] |

**Demote:** sports betting under `BettingPage.tsx` becomes a sub-tab inside Markets or gets cut entirely. Brand explicitly moves away from "Donkey Betz."

#### 3.2 — 24/7 Content

| Component | Source | Status |
|---|---|---|
| Content deliberation pipeline | `content_deliberation_runner.py` + ClaimsPack + reviewers + PublishGate | [T] |
| Content scoring | `content_scoring_service.py` | [T] |
| Content agents (20) | ContentWriter, Editor, ContrarianAgent, VoiceCritic, EditorAgent, etc. | [T] |
| Content spiders (3) | `medium`, `substack`, `producthunt` | [T] |
| Topic-mining → blog → publish loop | Existing | [T] |
| Operator Edge integration | Existing landing page | [T] |
| Per-app frontend persona | New | [W] |
| Billing tier | New | [W] |

**Operator Edge nests here** as the public-facing newsletter showcase. Subscribers convert into Content SaaS users.

#### 3.3 — 24/7 Studio

| Component | Source | Status |
|---|---|---|
| Image studio | `ImageStudioPage.tsx`, `ImageAgent`, `ImageEditingAgent` | [T] |
| Video studio | `VideoStudioPage.tsx`, `VideoEditingAgent`, `TalkingCharacterAgent`, `ResolveAgent` | [T] |
| Audio | `AudioAgent` (currently blocked), `DiscordVoiceService` | [W] (audio rotation disabled — quota burn risk) |
| Resolve Node | DaVinci video pipeline (live on Railway) | [T] |
| Media library | `media_tool`, `MediaPage.tsx` | [T] |
| 3D | `ThreeDAgent` | [A] |
| Per-app frontend persona | New | [W] |
| Billing tier | New (per-render meter likely) | [W] |

**Cost-blocked until `ExternalAPICallLog` ships.** Per `COST_SURVIVAL_AUDIT.md` § D.2: "Slice 2 of the Character OS merge fires Runway through Rigby. Single 50-message session = ~$50 in renders silently spent." Studio is the highest-risk app to launch without cost telemetry.

#### 3.4 — 24/7 Legal

| Component | Source | Status |
|---|---|---|
| LegalDocDrafterAgent | `core/agents/legal/legal_doc_drafter_agent.py` | [T] |
| Legal spiders (6) | `colorado_family_law`, `courtlistener`, `findlaw`, `justia_family_law`, `lii`, `legal_news` | [T] |
| LegalPage | `frontend/src/pages/LegalPage.tsx` | [T] |
| Parenting-time / motion / meet-and-confer templates | Existing legal-doc-drafter subagent | [T] |
| Per-app frontend persona | New | [W] |
| Billing tier | New | [W] |

**Niche but specific** — strong PMF candidate if marketed to pro-se litigants (Colorado family law especially given the existing spider). Lowest cost-of-goods of any vertical.

#### 3.5 — 24/7 Dev (optional — could merge with Studio or split later)

| Component | Source | Status |
|---|---|---|
| Code agents | `CodeGeneratorAgent` (blocked), `CodeReviewAgent` (rerouted), `FullStackDeveloperAgent` (rerouted) | [W] (most rerouted) |
| Founder Toolkit lineage | PitchDeckForge, DealFlowTracker, MentorForge (external sibling apps) | [T-external] |
| AppForge / Build Planning | `project_founder_toolkit_crossapp.md` | [W] |
| Focus Flow | External sibling repo | [T-external] |
| Per-app frontend persona | New | [A] |
| Billing tier | New | [A] |

**Hold this one.** Most code agents are rerouted. The standalone sibling apps already serve this audience. Decide post-flagship.

### Tier 4 — Internal Surfaces (not customer-facing)

These power the apps above. Don't sell them — sell what they enable.

| Surface | Role |
|---|---|
| Advisor Council (30 advisors: Buffett, Wood, Dalio, etc.) | Boardroom deliberation seasoning |
| Boardroom / Deliberation engine | Multi-reviewer consensus |
| ConceptForge | Idea generation upstream of deliberation |
| Self-Awareness System | Internal observability |
| Discord bot (96 commands, 25 Cogs) | Personal interface; *could* become a 24/7 Global AI Discord embed |
| Body systems monitor | Internal health |
| Doc verification framework | Internal correctness |
| Spider Network admin | Internal ops |

**Decision:** internal stays internal. Maybe expose Boardroom as a power-user feature inside Rigby ("ask the council") — but not as a standalone app.

### Tier 5 — Standalone Sibling Apps (external repos)

Already exist at `/Users/donkeyking/development/{name}`:

| App | Status | Plug into 24/7 Global AI? |
|---|---|---|
| `dealflowtracker/` | Standalone React+FastAPI | Yes — as integration / data source for Markets vertical |
| `pitchdeckforge/` | Standalone | Optional — could become "24/7 Dev: PitchDeck" |
| `sellerpilot/` | Standalone | TBD — what does it do? |
| `character-os/` | Standalone (web/ subdir) | **Already mid-merge.** See `MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`. |
| `magical_mountains/` | Next.js | Probably independent (game/creative project) |
| `worker-time-off/` | React+FastAPI | Independent business product |
| `dbao-studio/` | React+FastAPI | Likely related to unified-donkey-betz studio? Audit needed |
| `nicolas/` | Next.js | TBD |
| `focus-flow` (public GitHub) | FastAPI+React | Independent; demo-grade |

**Recommendation:** don't try to fold these in. Let them be independent products. Some (DealFlowTracker, MentorForge) become *referrals* from inside 24/7 Global AI ("we have a tool for that — try our DealFlow tracker"). Cross-sell, don't merge.

### Tier 6 — Demote / Archive

| Surface | Action | Reason |
|---|---|---|
| Donkey Betz / sports betting frontend | Demote to a Markets sub-tab or cut | Brand explicitly moves away |
| Ironwood Protocol (game) | Independent passion project | Out of scope for 24/7 Global AI brand |
| Aspirational dashboards (Neural Orchestra, Mythology Lab, Conversation Contract, etc.) | Hide from default nav, keep code | Per `CONNECTION_CENSUS_2026_05.md`: many routes are stranded; surface in "Labs" tab only |
| Old cockpit routes | Already redirected to workspace | Done — see `App.tsx` cockpit redirects |
| `frontend/components/generated/`, half-built dashboards | Untrack on next cleanup PR | Per Session 1112 PR-A pattern |

---

## E. Dependency graph

What each app needs from Tier 1 (engine) and Tier 2 (brain):

```
Tier 1 (Engine)
   |
   +-- Postgres + pgvector ------- ALL apps
   +-- Redis ------------------------ ALL apps
   +-- Celery fleet ----------------- ALL apps
   +-- Spider runtime --------------- Markets, Content, Legal, (Studio: less)
   +-- Agent registry --------------- ALL apps (different subsets)
   +-- LLM router ------------------- ALL apps
   +-- Signal aggregation ----------- Markets, Content
   +-- Initiative pipeline ---------- Content, Markets
   +-- Body systems ----------------- internal only
   +-- LearningBridge --------------- internal (improves all over time)
   |
Tier 2 (Brain — Rigby)
   |
   +-- Workspace model -------------- ALL apps
   +-- PA tool dispatcher ----------- ALL apps (different tool allow-lists)
   +-- Conversation memory ---------- ALL apps
   +-- Command Center UI ------------ Flagship / Rigby ("24/7 Global AI")
   |
Tier 3 (Verticals)
   |
   +-- 24/7 Markets ---- needs: Finance spiders, Stock agents, market tools
   +-- 24/7 Content ---- needs: Content agents, Content spiders, deliberation pipeline
   +-- 24/7 Studio ----- needs: Resolve Node, Image/Video agents, MEDIA-COST LOG (blocking)
   +-- 24/7 Legal ------ needs: Legal spiders, LegalDocDrafter, document templates
   +-- 24/7 Dev -------- needs: Code agents (mostly rerouted today), Founder Toolkit
```

Two implications:
1. **Studio is the most cost-risky app.** Don't launch until `ExternalAPICallLog` exists.
2. **Markets and Legal are the cleanest cuts.** Both have all dependencies green. Both have niche audiences.

---

## F. Cost-survival constraints (the gating reality)

Pulled forward from `COST_SURVIVAL_AUDIT.md` § J:

| Constraint | Affects which apps | Blocker level |
|---|---|---|
| No per-workspace cost attribution | ALL multi-tenant apps | **HARD BLOCKER** — cannot price per-workspace until `LLMCallLog.workspace` FK ships |
| No log table for Runway/ElevenLabs/Stability/Replicate | Studio (especially), Content (image gen) | **HARD BLOCKER for Studio** |
| No per-workspace daily $ cap | ALL | **HARD BLOCKER** — one runaway workspace can burn entire pool |
| No provider circuit-breaker | ALL | Medium — retries on 429/402 burn credits |
| Per-task daily fire cap on PAID-MEDIA tasks | Content (podcast), Studio (video) | Medium |

**Implication:** the path-of-least-resistance MVP is **Legal** — least cost-intensive, smallest LLM token spend, narrow audience. Markets next. Studio LAST, after cost logging is built.

This re-orders the launch sequence. See § H.

---

## G. Naming conventions (draft)

Brand: **24/7 Global AI**
Flagship: **24/7 Global AI** (the assistant — same name as brand)
Verticals: **24/7 Markets**, **24/7 Content**, **24/7 Studio**, **24/7 Legal**, **24/7 Dev** (or whatever sticks)

**Domain:** `247globalai.com` is **owned and live** (Vercel-served, production custom domain on the `24-7-ai-global` Next.js project). The Vercel preview URL `24-7-ai-global.vercel.app` is preview-only.

**Sub-app subdomains** (proposed, not yet provisioned — DNS work for later if/when verticals get their own personas):
- `markets.247globalai.com`
- `content.247globalai.com`
- `studio.247globalai.com`
- `legal.247globalai.com`
- `app.247globalai.com` → flagship / Rigby
- `edge.247globalai.com` → Operator Edge

**Action remaining:** trademark check on "24/7 Global AI" (USPTO TESS search + optional Intent-to-Use 1(b) filing before the brand spreads further). The .com is already secured.

---

## H. Phased cut plan (v1 — Rigby standalone first)

**One product. Ship it. Then decide.** Phases sequenced by cost-survival constraints and the "one polished product > five half-built products" rule.

### Phase 0 — Foundation (4-6 weeks, no external launches)

| # | Item | Why | Effort |
|---|---|---|---|
| 1 | Ship `LLMCallLog.workspace` FK + caller plumbing | Per-workspace cost attribution prerequisite | ~3 days |
| 2 | Ship `ExternalAPICallLog` + persist 11 cost-calc call sites | Per-workspace media cost attribution | ~1 day |
| 3 | Ship `cost_per_workspace_today` query + PA tool | Operator visibility | ~1 day |
| 4 | Ship per-workspace daily $ cap (`budget_gate.check()`) | Hard cap before any multi-tenant launch | ~1 day |
| 5 | Brand decision lock: 24/7 Global AI + Rigby naming | Marketing alignment | ~3 days |
| 6 | Trademark check on "24/7 Global AI" (USPTO TESS + optional ITU filing) — `.com` already owned and live | Legal safety | ~1-2 hr |
| 7 | Per-app persona scaffolding in React frontend (route prefix + theme system) | Multi-persona-ready frontend even though Phase 1 only uses one | ~1 week |
| 8 | Stripe product for flagship tier (Rigby standalone) | Revenue plumbing | ~2 days |

**Output of Phase 0:** the platform is *safe to multi-tenant*, the brand is locked, the per-app machinery exists. Zero customer-facing change yet.

### Phase 1 — Rigby standalone, no avatar, no verticals (4-6 weeks)

**The single focus.** Everything else is deferred until Rigby has paying customers.

| # | Item | Why |
|---|---|---|
| 1 | Frontend persona: `app.247globalai.com` — landing, signup, billing portal, chat | The product surface |
| 2 | Strip the consumer workspace UI to chat + files + history + a few tool toggles | Power-user workspace stays as `/workspace` internal; consumer view is focused |
| 3 | Auth + paid signup flow through Stripe (`flagship` tier, $20-30/mo) | The one paid product |
| 4 | Onboarding: 5-min "Rigby is working for me" first-run | Conversion shapes |
| 5 | Per-workspace cost dashboard surfaced in account settings | Customer transparency, regulatory hygiene |
| 6 | Rigby-as-flagship landing page at `247globalai.com` — single CTA, no "verticals coming soon" | Focus, not throat-clearing |
| 7 | Operator Edge issue: "What 24/7 Global AI actually is — try Rigby for $X/mo" | Convert newsletter subs to first paying customers |
| 8 | Per-account daily $ cap defaulted at a number Chris can stomach (e.g. $1.50/day, ~$45/mo cost ceiling per seat) | Survive a bad actor with a single seat |

**Phase 1 KPIs:**
- First paying customer (week 6).
- 5 paying customers (week 8-10).
- Per-seat unit economics positive (LLM spend / seat ≤ 50% of subscription price).

**Phase 1 is done when:** the unit economics check out *and* Rigby has at least 10 paying users who stayed past the first month.

### Phase 2 — Listen, fix, iterate (8-12 weeks, no new apps)

**No new product launches.** This phase is exclusively about Rigby's first cohort.

| # | Focus | Output |
|---|---|---|
| 1 | Conversion-funnel telemetry | Where do trials fall off? |
| 2 | Tool-call success rate per agent the LLM picks | Which Rigby muscles get used? Which don't? |
| 3 | Customer-interview cycle (5-10 interviews) | What feature would they pay 2x for? |
| 4 | Cost-per-seat reality check | Refine the daily $ cap default |
| 5 | Decide Phase 3 first-vertical based on customer pull, not founder intuition | If Markets customers asked, launch Markets. If Legal, launch Legal |

**Phase 2 exit gate:** customer-validated decision on which vertical lights up first.

### Phase 3 — First vertical add-on (decision deferred to end of Phase 2)

Verticals become **feature packs inside Rigby**, not separate products. Customer pays the flagship tier ($20-30/mo) and optionally unlocks one or more vertical packs ($10-30/mo each).

| Possible vertical pack | Audience signal | Cost shape | Risk |
|---|---|---|---|
| **Markets pack** | Self-directed traders, finance ops folks | LLM-heavy; needs alert-budget cap | Medium |
| **Legal pack** | Pro-se litigants (esp. Colorado family law), solo legal ops | LLM-only, lowest cost-of-goods | Low |
| **Content pack** | Solo creators, indie newsletters | LLM + occasional image-gen | Medium |
| **Studio pack** | Video creators | Runway/ElevenLabs/Stability — highest cost | **HIGH — defer to Phase 4+** |

### Phase 4+ — Studio, Character OS unlock, international, sibling-app cross-sell

Defer. None of this is in scope until Rigby + at least one vertical pack are profitable.

If a paying customer says "I'd pay you $50/mo extra to have Rigby with a face," **then** the Character OS merge unparks. Not before.

---

## I. What I deliberately did NOT do

- **No new code.** This is strategy, not implementation.
- **No new repos.** Soft cut means no repo proliferation.
- **Soft name lock only.** Brand "24/7 Global AI" is locked enough to ship the live site at `247globalai.com`; trademark filing is still recommended before scaling the brand further.
- **No commitment to a sports-betting fate.** I recommend demoting, but Chris's call.
- **No removal of any existing surface.** `CONNECTION_CENSUS_2026_05.md` correctly says: detectors first, deletes later. Same applies here.
- **No promise of timelines below 4 weeks.** Per memory `feedback_no_fluff_verify_truth.md`, anything faster would be aspirational.

---

## J. Open questions for Rigby + Chris

These need real answers before this Atlas becomes a plan. v1 has narrowed the list — most pricing/ordering questions are now Phase 2/3 problems, not Phase 1 problems.

### J.1 Phase 1 (decide now)

1. **Trademark check on "24/7 Global AI"** — the brand is locked in practice (site is live at `247globalai.com`, .com is owned), but no USPTO TESS check or filing has happened yet. ~1-2 hr of legal-adjacent work. Recommended before scaling the brand further (paid ads, press, partnerships).

2. **Phase 1 flagship pricing — $20/mo or $30/mo?** Sensitive to expected cost-per-seat (the daily $ cap × 30). My instinct: start at $30 with a 7-day trial; lower if conversion is weak. Raising prices later is harder than lowering them.

3. **Phase 1 daily $ cap per seat — $1, $1.50, or $2?** Direct lever on profitability. Lower = safer + cheaper to support, higher = better customer experience. Recommend $1.50 default + override per workspace.

4. **What survives the stripped consumer Rigby UI?** The internal workspace has 5 tabs and dozens of surfaces. The consumer version should probably be: chat, file upload/download, conversation history, maybe a "what Rigby can do" tool catalog. Everything else (boardroom, neural orchestra, mythology lab, government, advisors panel, ironwood, etc.) hides until the user upgrades to a power-tier or unlocks a vertical pack.

5. **Sports betting in Phase 1 — hidden or visible?** The legacy `BettingPage.tsx` exists. Two options: (a) hide it from the consumer Rigby persona entirely (cleanest), (b) keep it reachable for legacy Donkey Betz users on a separate URL `legacy.donkeybetz.com`. My recommendation: (a). The rebrand is the point.

### J.2 Phase 2 (decide after Phase 1 has data)

6. **Which vertical pack launches first** — Markets, Legal, Content? Defer this until 10 paying Rigby customers tell us what they actually want. Founder intuition is wrong about this more often than not.

7. **Operator Edge — keep publishing during Phase 1, or pause?** Recommend keep publishing; treat each issue as a Rigby ad. Restructure conversation waits for Phase 2.

8. **Character OS — leave parked or actively cut?** Recommend leave parked. The doc + design work stays in tree (zero ongoing cost). Unpark only if a paying customer asks for an avatar.

### J.3 Phase 3+ (decide later)

9. **Standalone sibling apps — cross-sell, integration tier, or absorb?** Defer to Phase 3+. Most likely answer: cross-sell only (zero integration work).
10. **Soft cut vs hard cut for portfolio effect** — only re-open if a vertical generates $5k+/mo standalone and warrants its own deploy.
11. **Subscription pricing for verticals** — gut-check $10-30/mo as pack pricing on top of flagship $30. Verify with customer interviews.

---

## K. References

- `docs/PLATFORM_INVENTORY.md` — runtime source of truth
- `docs/PLATFORM_WHAT_IT_IS.md` — narrative anchor
- `docs/COST_SURVIVAL_AUDIT.md` — cost gating constraints
- `docs/CONNECTION_CENSUS_2026_05.md` — what's actually connected
- `docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md` — concurrent merge in flight
- `docs/MERGE_PREP_TIER_4.md` — merge-prep workstream
- `docs/TELEMETRY_PLAN_2026_05.md` — telemetry roadmap (Tier 3)
- `frontend/src/App.tsx` — current 50+ routes
- `Procfile` — current 11-process deployment shape
- Memory: `project_current_state_2026_04.md` — survival-mode constraints

---

**End of v0 draft.** Hand to Rigby next: workspace ticket for review, answers to § J, then a v1 with operator-decided positions.
