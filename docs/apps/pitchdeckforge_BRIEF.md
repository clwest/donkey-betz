---
title: "Pitch Deck Forge — Phase 1 brief (products.ts-anchored)"
status: draft (Session 1135 discovery, pending Rigby review + Chris ratification)
session: 1135
generated: 2026-05-23
workspace: Donkey Betz
companion_docs:
  - 24_7_GLOBAL_AI_APP_ATLAS.md
  - apps/mentorforge_BRIEF.md
  - apps/contract_concierge_BRIEF.md
  - apps/dealflowtracker_BRIEF.md
  - UDB_BEHAVIOR_LAYER.md
  - UDB_TRANSLATION_LAYER.md
source_of_truth: "24-7-ai-global/src/lib/products.ts PRODUCTS[1] (slug: pitchdeckforge)"
authors: claude + jessica (discovery pass) → rigby (review pending)
---

# Pitch Deck Forge — Phase 1 brief

> **Source of truth:** `24-7-ai-global/src/lib/products.ts` PRODUCTS[1]. All product framing below traces back there.

## 1. What it is

**Tagline (per products.ts):** *"AI investor decks — described to PDF in minutes."*

**Elevator (per products.ts):** *"Describe the company; ship a polished, investor-ready 10-slide deck with speaker notes, executive summary, and a 90-second pitch script. Four template styles tuned to different investor personas, plus bonus market-context, Q&A, and competitive-landscape slides for Pro."*

**Pillar:** Innovation. **Arc:** Pitch. **Suite product #2** (no. II).

**Phase 1 scope:** Describe-to-deck workflow producing investor-ready 10-slide decks with speaker notes + executive summary + 90-second script. Four template styles tuned to different investor personas. Per-slide AI regeneration with custom instructions. Pro tier adds market context, VC Q&A prep, competitive landscape slides.

**Status:** **shipped, live at https://pitchdeckforge.vercel.app**

## 2. Who buys it

**Target (per products.ts):** Founders raising seed → Series B.

**Concrete buyer profiles:**
- Solo founder prepping first investor meetings (seed stage)
- Startup CEO refreshing deck for follow-on rounds (A / B)
- Founder team needing fast deck iteration during fundraising sprint

**Buyer = User.** Self-serve via Stripe. Free starter tier; Pro/Team self-upgrade.

## 3. What's built (per products.ts — shipped today)

| Component | Status | Source |
|---|---|---|
| 4 deck styles · investor-persona prompts | Shipped | products.ts features[0] |
| 10 slides + TL;DR + 90-second script | Shipped | products.ts features[1] |
| Per-slide AI regeneration with custom instructions | Shipped | products.ts features[2] |
| Bonus slides: Market Context · VC Q&A · Competitive Landscape (Pro tier) | Shipped | products.ts features[3] |
| Three-tier billing (Starter / Pro / Team) | Shipped | products.ts pricing block |
| Stack: React 19 · FastAPI · Postgres · OpenAI · Stripe-ready | Shipped | products.ts stack |
| Production URL | Live | https://pitchdeckforge.vercel.app |
| Fleet runtime (localhost:8004 API, localhost:5176 web) | Live on local | Session 1126 |
| `slide.regenerated` SSE event | Live | Session 1129 mention; supports per-slide AI regeneration feature |

## 4. What proves it's real

**Canonical proof:** Visit https://pitchdeckforge.vercel.app → sign in → describe company → pick template style → generate 10-slide deck with speaker notes + 90-sec script → per-slide AI regenerate with custom instructions if needed → export.

**Local interim proof:** localhost:5176 (web) + localhost:8004/api/health (backend).

## 5. What's missing (gap to "selling at full GTM")

### Phase 0 gating items

| Item | Status | Effort |
|---|---|---|
| Per-customer cost tracking (shared portfolio infra) | Not done | ~3 days shared |
| Daily $ cap per customer enforcement | Not done | ~1 day |
| Stripe SKU + webhook verification (Pro $29, Team $79 per products.ts) | Verify status | Small |
| MentorForge Founder Project handoff verification (Pitch Deck Forge accepts brief from mentor session) | Verify status | Small (integration smoke) |

### What's NOT needed for Phase 1
- New product copy or audience reframing — products.ts already locks both.
- Pricing — Free / $29 Pro / $79 Team already locked in products.ts.
- Stack changes.

## 6. Buildable in one sprint?

**Phase 0 wrap (~1 week aggregate)** — small, because shipped. Same shape as MentorForge + Contract Concierge: verify + cost/cap infra (shared with portfolio).

## 7. GTM sketch

| Lever | Plan |
|---|---|
| **Surface** | https://pitchdeckforge.vercel.app (shipped) + 24-7-ai-global studio site listing |
| **Pricing (per products.ts)** | Free Starter / $29 Pro / $79 Team |
| **What's included per tier** | Starter Free: 2 decks · all 4 styles. Pro $29: Unlimited · bonus slides · share links. Team $79: 5 seats · expert review · API. |
| **CTA** | "Start free — 2 decks · all 4 styles" → upgrade to Pro for unlimited + bonus slides |
| **Cross-Suite hook** | Mentor Forge build-planning session can hand outline to Pitch Deck Forge (per MentorForge spokesperson doc). |
| **Disclaimers** | "AI-generated deck content is a starting point; review with your team and an investor-savvy advisor before any high-stakes pitch." |
| **Forbidden in product + marketing** | "Guaranteed funding" / "will get you funded" claims; specific success-rate statistics without backing data; comparisons to specific named VCs. |

## 8. Spokesperson alignment (Phase 4+, parked)

Per Atlas §C.5: Character OS / avatar / voice = parked until paying customer demands a face. Phase 1 is text-only deck generation. Phase 4+ unlocks: AI-narrated deck walkthroughs (mentor voice walks through the 90-second script); persona-voiced pitch coaching for mock-investor sessions.

## 9. Decisions still needed (escalate to Chris)

**Closed by products.ts as canonical:**
- ✅ Product framing locked per products.ts PRODUCTS[1]
- ✅ Pricing locked: Free / $29 Pro / $79 Team
- ✅ Audience locked: Founders raising seed → Series B
- ✅ Status: shipped
- ✅ Production URL: https://pitchdeckforge.vercel.app
- ✅ 4 deck styles + 10 slides + 90-sec script + per-slide regen

**Still open for Chris:**

| # | Question | Why it matters |
|---|---|---|
| 1 | **Stripe SKU + webhook verification** — Pro $29 + Team $79 live in prod? | Reveals true Phase 0 effort for billing |
| 2 | **Phase 0 cost-attribution shared across portfolio** | Atlas-level requirement (4th product in same shared infra need) |
| 3 | **MentorForge → PitchDeckForge handoff verification** — does build-planning session export correctly? | Suite cross-product story |
| 4 | **Template style enumeration** — products.ts says 4 styles "tuned to different investor personas"; are styles named + locked anywhere? | Marketing copy clarity |
| 5 | **Expert review (Team tier)** — products.ts says Team includes "expert review"; who provides this + at what SLA? | Team tier value-prop |

## 10. Honest claim audit (per translation layer §2)

**We do NOT claim:**
- AI decks will get you funded or improve fundraising outcomes.
- Specific number of paying customers.
- Cross-Suite handoff (MentorForge → PitchDeckForge) is operational today without verification (per §9 #3).
- Template style names beyond what products.ts names (none enumerated; 4 styles exist per features).
- "Expert review" for Team tier is live operational (verify per §9 #5).

**We DO claim (per products.ts ground truth):**
- Pitch Deck Forge is shipped and live at https://pitchdeckforge.vercel.app.
- 4 deck styles tuned to investor personas.
- 10 slides + TL;DR + 90-second pitch script per generated deck.
- Per-slide AI regeneration with custom instructions.
- Pro tier bonus slides: Market Context + VC Q&A + Competitive Landscape.
- Pricing: Free / $29 Pro / $79 Team per products.ts.
- Pillar: Innovation. Arc: Pitch. Suite product #2.
- Stack: React 19 · FastAPI · Postgres · OpenAI · Stripe-ready.
- Fleet runtime on local (localhost:8004 API, localhost:5176 web).
- `slide.regenerated` SSE event supports per-slide regen workflow.

---

**Brief authored:** Session 1135 (Claude + Jessica discovery pass, products.ts-anchored).
**Source of truth:** `24-7-ai-global/src/lib/products.ts` PRODUCTS[1].
**Next step:** Rigby review for honest framing. Then Chris ratifies the 5 open decisions in §9. Then brief becomes locked Phase 1 source-of-truth for Pitch Deck Forge.
