---
title: "Rigby standalone — Phase 1 flagship brief"
status: draft (Session 1135 discovery, rev. 2 post-Rigby review, pending Chris confirmations)
session: 1135
generated: 2026-05-23
revised: 2026-05-23 (Rigby review pass applied)
workspace: Donkey Betz
companion_docs:
  - 24_7_GLOBAL_AI_APP_ATLAS.md
  - specs/FLEET_CAPABILITY_BUSINESS_SPEC.md
  - UDB_BEHAVIOR_LAYER.md
  - UDB_TRANSLATION_LAYER.md
authors: claude + jessica (discovery pass) → rigby (review applied)
---

# Rigby standalone — Phase 1 flagship brief

## 1. What it is

**"24/7 Global AI is your personal AI assistant that never sleeps — it watches 80 global data sources, has 80+ specialised agents on call, and 100+ tools so it can actually do things, not just talk."** (Atlas §C.2 canonical marketing pitch.)

*Note: pitch numbers are directional; current counts verified on local as of 2026-05-23 (103 tool schemas, 74 enabled agents, 80 spiders) appear in §3 and supersede the round figures in the quote. Production parity not asserted.*

**Phase 1 scope:** Rigby is a research-and-draft engine running on local today. She produces; the customer ships. Tools that connect to a customer's external accounts (Gmail, Google Calendar, LinkedIn, CRM) do not exist yet and are Phase 2 candidates driven by customer demand.

## 2. Who buys it

**Hypothesis (A/B, pending customer-discovery validation):** two target audiences, no narrowing yet.
- **A.** Solo founders (building side projects or early-stage companies)
- **B.** Small-agency owners (with billable workload, looking for AI leverage)

**Buyer = user.** Self-serve via Stripe checkout. No sales team. No procurement.

*Validation gate: pick A vs B (or both) after first 10 paying customers tell us which voice converts.*

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

| Lever | Plan |
|---|---|
| **Channel** | *Proposed (pending Chris greenlight + budget):* Paid ads from day one + warm/personal network. No newsletter funnel (audience = 0). |
| **Pricing** | $30/mo flat, single tier, 7-day free trial |
| **Cap behavior** | Daily $ cap per customer (number TBD — Atlas suggests $1.50; pending Chris confirmation per §9 Decision 3) |
| **CTA** | "Start using Rigby — $30/mo, 7-day trial" → Stripe → onboarding |
| **What's included** | Chat + tools + files + history (running on local today; consumer-facing deploy pending), 1 seat, daily cap |
| **Customer-facing surface** | `app.247globalai.com` (consumer persona, build status TBC) — stripped to chat, file upload/download, conversation history, "what Rigby can do" catalog |
| **Hidden from consumer** | *Proposed list (needs Chris per-item confirmation; only Sports Betting hide is directly Atlas-cited):* Boardroom, Governance, Platform, Agents panel, Advisors, Neural Orchestra, Initiatives admin, Intelligence, Image/Video Studio, Sports Betting (legacy), Government, Legal-as-domain |
| **Safety guardrails** | No medical/legal/specific-investment advice. No personalized betting picks. No claims about features not built. "Powered by LLMs, may be wrong" disclaimer. (Expandable later.) |
| **Execution posture** | Rigby drafts; customer ships. No outbound action on customer's external accounts. Publishing to OUR channels (newsletter/blog/Discord) stays internal-only. |

## 8. Spokesperson alignment (Phase 4+, parked)

Per Atlas §C.5, J.2.8: Character OS / avatar / voice = parked until a paying customer demands a face. Phase 1 is text-only. When unparked, persona-narrated dashboards + brand-voice-locked video become the visible Pro/Business tier upsell.

## 9. Decisions still needed (escalate to Chris)

*Re-ordered per Rigby review: build status + cap/cost gating moved to top because they block multiple downstream decisions.*

| # | Question | Why it matters |
|---|---|---|
| 1 | **`app.247globalai.com` build status — what's done in the repo?** | Determines whether Phase 1 product is "API + internal UI" vs "consumer app." Unlocks proof-pick + Phase 0 timeline. |
| 2 | **Pick canonical proof: Candidate A (local-internal demo) or Candidate B (consumer signup flow)?** | §4 currently hedges. Chris picks the single Phase 1 truth we sell against. |
| 3 | **Confirm $1.50/day cap per customer + cost-tracking shipped as Phase 0 GATING** | Without this, paid ads at $30/mo can produce negative unit economics. Not optional. |
| 4 | **Paid ads budget** | How much per month to test the channel? |
| 5 | **Trademark filing green-light** | 1–2 hr of legal work; recommended before paid ads scale brand visibility. |
| 6 | **When does the landing page have to pick a voice** (founders vs agencies)? | Both audiences for discovery, but copy eventually picks one. |

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
**Next step:** Rigby quick "looks good?" pass on rev. 2. Then Chris ratifies the 6 open decisions in §9. Then brief becomes locked Phase 1 source-of-truth.
