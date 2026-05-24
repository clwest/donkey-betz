---
title: "Rigby standalone — Phase 1 GTM proposal (currently-private product)"
status: draft (Session 1135 discovery, rev. 3 — corrected against products.ts; this brief proposes a public Phase 1 launch of a currently-private product)
session: 1135
generated: 2026-05-23
revised: 2026-05-23 (rev. 3 — corrected against products.ts; rev. 2 framed Rigby as "Phase 1 flagship" but products.ts treats Rigby as "in-development, private, standalone surface forthcoming")
workspace: Donkey Betz
companion_docs:
  - 24_7_GLOBAL_AI_APP_ATLAS.md
  - apps/contract_concierge_BRIEF.md
  - apps/signal_studio_BRIEF.md
  - UDB_BEHAVIOR_LAYER.md
  - UDB_TRANSLATION_LAYER.md
source_of_truth: "24-7-ai-global/src/lib/products.ts LAB[7] (slug: rigby; status: in-development, subStatus: Private)"
authors: claude + jessica (discovery pass) → rigby (review applied) → corrected against products.ts ground truth
---

# Rigby standalone — Phase 1 GTM proposal

> **⚠️ Source of truth + reality check:** Per `24-7-ai-global/src/lib/products.ts` LAB[7] (entry no. XV), **Rigby is currently `in-development · Private`** — *"private today; public decomposition pending — for those who refuse to wait until Monday morning."* This brief is a **Phase 1 GTM proposal** for how to take that currently-private product to public market. It is NOT a description of an existing public product. Rev. 1-2 framed Rigby as the "Phase 1 flagship at app.247globalai.com" per Atlas, but products.ts (the marketing-page source of truth) treats Rigby as not-yet-public.

## 1. What it is (products.ts canonical framing)

**Tagline (per products.ts):** *"An agentic personal assistant with a brain."*

**Elevator (per products.ts):** *"The proprietor's personal AI. A function-calling agentic loop on top of six LLM providers with 101 typed tools and 166 handlers wired into spider data, agent dispatch, advisor consultation, and the full Suite. Private today; public decomposition pending — for those who refuse to wait until Monday morning."*

**Pillar:** Impact. **Arc:** Companion. **Tier:** LAB (engine reveal, no. XV). **Status:** in-development · Private.

**Phase 1 GTM proposal scope (THIS BRIEF):** propose taking the currently-private Rigby public as a standalone subscription product at `app.247globalai.com`. The Atlas (Session 1116) recommended this as Phase 1 of the broader portfolio. products.ts confirms the standalone surface is "forthcoming." This brief is the GTM build plan to get from "private" to "public."

**Phase 1 capability scope:** Research-and-draft engine + tool dispatch + agent consultation. Tools that connect to a customer's external accounts (Gmail, Google Calendar, LinkedIn, CRM) do not exist yet and are Phase 2 candidates driven by customer demand.

## 2. Who buys it

**Per products.ts target:** *"Operators who refuse to wait for the work week."*

**Phase 1 GTM proposal — interpretation of "operators":**
- Founders / solo operators / small-team leads who use AI tools daily
- People who currently rely on ChatGPT/Claude for assistant-style workflows but want spider-data grounding + agent dispatch + advisor consultation
- Both rev. 1-2 hypothesis audiences (solo founders + small-agency owners) fit under this canonical "operators" framing

**Buyer = user.** Self-serve via Stripe checkout. No sales team. No procurement.

*Rev. 1-2 had "Hypothesis A/B" framing. Rev. 3 keeps the hypothesis posture but anchors it in products.ts's "operators" target rather than extrapolating two audience types from scratch.*

## 3. What's built (real shipping evidence)

*Counts below from local manifest scan 2026-05-23 against `core/services/pa_tool_schemas.py`, `AGENT_MAP`, `ai_core/spiders/`, and `PLATFORM_INVENTORY.md`.*

| Component | Status | Notes |
|---|---|---|
| PA chat brain (`POST /api/pa/chat/`) | Live | u-d-b core path, GPT-5.2 function calling |
| Tool surface | Live | 103 schemas, 168 handlers (verified 2026-05-23) |
| Specialist agents | Live | 74 enabled in AGENT_MAP (83 total entries; verified 2026-05-23) |
| Live data sources | Live | 80 spiders across 41 categories (verified 2026-05-23) |
| Workspace UI (`/workspace`) | Live | Primary tabs: Home, Work, Build, Intelligence, System (5 primary; sub-tabs include Deliverables under Work and Files under System). Layout defined in `frontend/src/pages/WorkspacePageNew.tsx`. Subject to UI iteration. |
| Command Center (PA chat surface) | Live | Where Rigby actually runs today |
| Conversation memory | Live | Persistent memory support exists (pgvector-backed); cross-session continuity subject to auth + memory policy |
| Brand domain `247globalai.com` | Live | Vercel-served, public marketing site |
| Repo for `app.247globalai.com` consumer app | Exists | Build status TBC — see §5 + §9 |
| PA-chat audit trail | Live | Per-call telemetry (Session 1132) |

## 4. What proves it's real

**Canonical Phase 1 proof: NOT YET PICKED.** Two candidate proofs documented below; Chris picks one as the single proof we'll sell against (see §9 Decision 1).

**Candidate A — Local-internal demo (deterministic, available today):**
> Open Command Center at `localhost:8080` → ask Rigby: *"Research [topic X] and save it as a deliverable."* → watch her dispatch web_search + research_and_create_tool + a specialist agent → receive a written answer (sources included when web_search fires) → confirm the saved deliverable appears in `/workspace` under **Work → Deliverables** sub-tab. Tool runs visible in verbose log.

**Candidate B — Consumer signup flow (not yet verifiable):**
> Visitor lands on `app.247globalai.com` → signs up via Stripe → reaches chat → asks Rigby a question → receives answer. Requires consumer-app repo build status confirmation (§9 Decision 2).

## 5. What's missing (gap to "could sell for real")

### 5.1 [PHASE 0 GATING — launch-blocking]

**These two are NOT optional for a $30/mo product. Without them, paid ads can create negative unit economics instantly:**

| Item | Status | Effort | Why gating |
|---|---|---|---|
| Per-customer cost tracking (`LLMCallLog.workspace` FK) | **Not done** | ~3 days | No attribution = no insight into per-customer margin |
| Daily $ spending cap per customer | **Not done** | ~1 day | One runaway customer burns the pool; depends on cost tracking |

### 5.2 Other Phase 0 prerequisites (per Atlas §H)

| Item | Status | Effort |
|---|---|---|
| Media-cost tracking (Runway/ElevenLabs/Stability) | **Not done** | ~1 day (only matters when Studio activates, Phase 4+) |
| "Cost per customer today" report | **Not done** (depends on cost tracking) | ~1 day |
| Trademark check on "24/7 Global AI" | **Not done** | 1–2 hr |
| Consumer-facing `app.247globalai.com` build | **Repo exists, build status TBC** | ~1 week if fresh |
| Stripe product + hook | **Stripe set up, hook needs adding** | Small |
| Consumer UI strip (hide internal surfaces) | **Not done** | Medium |

### 5.3 Not gaps, but worth naming
- No external-account integrations (Gmail/Calendar/LinkedIn/CRM). Phase 2 trigger = customer demand.
- No public newsletter audience (Atlas assumed Operator Edge funnel; audience is currently 0).

## 6. Buildable in one sprint?

**Phase 0 in aggregate: LARGE (~3–4 weeks).**

Per-item sizing:
- Stripe hook addition: **SMALL**
- Trademark check: **SMALL** (legal admin)
- Daily cap + cost tracking (Phase 0 gating items, 5.1): **MEDIUM** (~1 week)
- Consumer persona UI scaffolding: **MEDIUM** (~1 week)
- `app.247globalai.com` consumer-facing build: **BLOCKED on status check** (size unknown until Chris confirms current state of that repo)

## 7. GTM sketch

> **⚠️ Pricing reality:** products.ts has **no pricing block for Rigby** (it's `Private`). The $30/mo + $1.50/day cap below are Atlas (Session 1116) recommendations + Phase 1 GTM proposal numbers, NOT currently in market. Chris ratifies all pricing at GTM lock.

| Lever | Plan |
|---|---|
| **Channel (proposed)** | *Pending Chris greenlight + budget:* Paid ads + warm/personal network. No newsletter funnel (Operator Edge audience exists per products.ts CHANNELS[0] but not as a paying-customer funnel yet). |
| **Pricing (Atlas-suggested, Chris ratifies)** | $30/mo flat, single tier, 7-day free trial (per Atlas §H Phase 1). Compare to Suite products in products.ts at $29-99/mo. |
| **Cap behavior (Atlas-suggested)** | Daily $ cap per customer (Atlas suggests $1.50; pending Chris confirmation per §9). |
| **CTA (proposed)** | "Start using Rigby — $30/mo, 7-day trial" → Stripe → onboarding |
| **What's included (proposed Phase 1 scope)** | Chat + tools + files + history (running on local today; consumer-facing public deploy pending), 1 seat, daily cap |
| **Customer-facing surface (proposed)** | `app.247globalai.com` per Atlas §G subdomain plan (build status = §9 Decision 1) — stripped to chat, file upload/download, conversation history, "what Rigby can do" catalog |
| **Hidden from consumer (proposed list)** | *Needs Chris per-item confirmation:* Boardroom, Governance, Platform, Agents panel, Advisors, Neural Orchestra, Initiatives admin, Intelligence, Image/Video Studio, Sports Betting (legacy), Government, Legal-as-domain |
| **Safety guardrails** | No medical/legal/specific-investment advice. No personalized betting picks. No claims about features not built. "Powered by LLMs, may be wrong" disclaimer. (Expandable later.) |
| **Execution posture** | Rigby drafts; customer ships. No outbound action on customer's external accounts. Publishing to OUR channels (newsletter/blog/Discord) stays internal-only. |

## 8. Spokesperson alignment (Phase 4+, parked)

Per Atlas §C.5, J.2.8: Character OS / avatar / voice = parked until a paying customer demands a face. Phase 1 is text-only. When unparked, persona-narrated dashboards + brand-voice-locked video become the visible Pro/Business tier upsell.

## 9. Decisions still needed (escalate to Chris)

> Re-ordered per Rigby review: build status + cap/cost gating block multiple downstream decisions. Plus a new top-level question added in rev. 3: products.ts treats Rigby as `Private`; does Chris commit to taking it public per this brief?

| # | Question | Why it matters |
|---|---|---|
| 0 | **Confirm "take Rigby public" decision** — products.ts has Rigby as `in-development · Private`. This brief proposes a Phase 1 public launch. Does Chris confirm that's the direction, or does Rigby stay private through a different phase? | Reframes everything downstream. If "stay private," this brief becomes archival exploration. |
| 1 | **`app.247globalai.com` build status — what's done in the repo?** | Determines whether Phase 1 product is "API + internal UI" vs "consumer app." Unlocks proof-pick + Phase 0 timeline. |
| 2 | **Pick canonical proof: Candidate A (local-internal demo) or Candidate B (consumer signup flow)?** | §4 currently hedges. Chris picks the single Phase 1 truth we sell against. |
| 3 | **Confirm $1.50/day cap per customer + cost-tracking shipped as Phase 0 GATING** | Without this, paid ads at $30/mo can produce negative unit economics. Not optional. |
| 4 | **Pricing lock — $30/mo or different?** products.ts has no Rigby pricing block; Atlas suggests $30. | Locks Stripe SKU + ad copy. |
| 5 | **Paid ads budget** | How much per month to test the channel? |
| 6 | **Trademark filing green-light** | 1–2 hr of legal work; recommended before paid ads scale brand visibility. |
| 7 | **When does the landing page have to pick a voice** (founders vs agencies vs broader operators)? | Both audiences for discovery, but copy eventually picks one. |
| 8 | **Update products.ts to reflect Phase 1 launch when ready** | products.ts is the source of truth for the public-facing portfolio. When Rigby goes public, its entry needs to update from `in-development · Private` to `shipped` with pricing tier. |

## 10. Honest claim audit (per translation layer §2)

**We do NOT claim:**
- Rigby can act on a customer's behalf in their email/calendar/social today.
- A working consumer signup flow at `app.247globalai.com` exists.
- Per-customer cost attribution is live.
- A paying customer exists.
- Continuous 24/7 monitoring or personalized watchlist alerts (the pitch's "never sleeps" line is brand framing; Phase 1 does not implement background per-user alerting).
- Enterprise compliance posture (SOC 2, HIPAA, GDPR, etc.). Capability bundle + audit log are the *foundation* for these, not a current claim.

**We DO claim:**
- The brain (PA chat, tools, agents, spiders, memory) is operational and verifiable on local today.
- The brand and domain `247globalai.com` are owned and live.

---

**Brief authored:** Session 1135 (Claude + Jessica discovery pass).
**Rev. 2:** Rigby review pass applied — 14 mechanical fixes (count alignment, deterministic proof, hypothesis labeling, source citations, expanded claim audit, §9 reorder, Phase 0 gating elevation).
**Rev. 3:** Discovery of `24-7-ai-global/src/lib/products.ts` as canonical source of truth revealed rev. 1-2 framed Rigby as "Phase 1 flagship" but products.ts treats Rigby as `in-development · Private` ("standalone surface forthcoming"). Rev. 3 reframes brief as a **Phase 1 GTM proposal** for taking the currently-private Rigby public, not a description of an existing public product. Updated header note, §1 grounded in products.ts pitch + elevator, §2 anchored in canonical "Operators who refuse to wait for the work week" target, §7 marked pricing as Atlas-suggested-pending-Chris (not currently in products.ts), §9 added Decision 0 ("confirm take-public decision") + Decision 8 ("update products.ts when launched").
**Next step:** Rigby review for honest framing on rev. 3. Then Chris ratifies the 9 open decisions in §9 (especially Decision 0). Then brief becomes locked Phase 1 GTM proposal for Rigby standalone.
