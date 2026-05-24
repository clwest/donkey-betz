---
title: "Session 1137 — Jessica Phases 1-4 ratification (22 decisions + 4 deliverables)"
date: 2026-05-24
status: active
session: 1137
previous_handoff: SESSION_1136_OPS_VIEW_PARKED.md
next_session_primary: Chris ratification pass on 22 Jessica-locked decisions + Phase 5 audit batch
team: jessica + claude (rigby looped at session close)
---

# Session 1137 — Jessica Phases 1-4 ratification

> **Read this if** you want the full Session 1137 arc: Jessica drove a single-session
> strategic ratification pass through the 54+7 Session 1135 open decisions, landing
> 22 explicit decisions across 4 phases plus 4 concrete follow-up deliverables. This
> is the heaviest single-session strategic close in the project's history.

## TL;DR

**22 strategic decisions locked + 4 concrete deliverables shipped + 7 follow-up items queued for Phase 5.**

Decisions span: take-public strategy, trademark posture, product spin-off triage,
LAB/Suite graduation rules, pricing locks for 4 products, cost-attribution business
rules, Stripe SKU wiring sequence, capital allocation (ads, expert review, legal
reviews), GTM channel picks for 3 products, Operator Edge cross-promo policy, canonical
proof pick, persona/template naming, DealFlowTracker Fund-tier feature triage.

Pattern across all 22: **revenue-gated triggers + portfolio-consistent pricing +
conservative pre-revenue cost discipline + sequenced engineering load + demand-validation
gates for non-essential capital + editorial honesty over marketing fluff.**

## Lineage

- Session 1135 closed with **54 per-app open decisions + 7 cross-cutting items** across 8 briefs (`docs/handoffs/SESSION_1135_FINAL_CLOSE.md`)
- Session 1136 worked the context-kit ops view side-quest → PARKED at Jessica user-test (`docs/handoffs/SESSION_1136_OPS_VIEW_PARKED.md`)
- Session 1137 (this) returned to the 1135 backlog with Jessica as business decider, Claude as facilitator

## Owner-bucket triage (re-classified per Jessica's frame mid-session)

Initial triage assumed Chris would own most decisions. Jessica corrected:
- **Chris = tech** (architecture, engineering, system decisions)
- **Jessica = business** (pricing, GTM, capital allocation, brand positioning, take-public, legal posture, customer-facing strategy)

Re-triaged buckets:

| Bucket | Count | This session |
|---|---|---|
| Jessica decides (business) | ~40 | 22 ratified (Phase 1-4); ~18 remain in Phase 5+ |
| Chris decides (tech) | ~12 | 0 ratified (queued for Chris session) |
| Both, sequenced (Jessica rule → Chris implements) | ~5 | 1 ratified (Decision 9 cost rules); Chris implementation pending |

## The 22 decisions (consolidated)

### Phase 1 — Foundation strategy

| # | Decision | Lock |
|---|---|---|
| 1 | Rigby take-public | **(c) Defer** — trigger: ≥2 Suite products at ≥$500 MRR each AND concrete "Rigby standalone" answer |
| 2 | "24/7 Global AI" trademark | **(c) Wait** — same trigger as #1; revisit-anytime allowed |
| 3 | Colorado Family Law Concierge | **(b) Park** — until portfolio >$5K MRR OR active vertical-add decision |
| 4 | Suite vs LAB graduation rule | **(a) Revenue-only** — ≥$1K MRR sustained ≥2 months per product |

### Phase 2 — Pricing + cost foundation

| # | Decision | Lock |
|---|---|---|
| 5 | Rigby pricing | **$30/mo** (contingent on launch trigger from Decision 1) |
| 6 | Signal Studio pricing | **Free + $49 Pro + $99 Team** |
| 7 | SellerPilot pricing | **Free + $39 Pro + $99 Team** |
| 8 | ComplianceSentinel pricing | **Free + $79 Pro + $249 Team** (deliberately above portfolio norm for compliance market) |
| 9 | Cost attribution business rules | Portfolio cap = `max($1.67, 40% × trailing-30d-MRR / 30)` per day; per-customer cap = `25% × monthly_subscription / 30` per day; soft degrade to gpt-5-mini at 100% cap; daily Slack/Discord summary to Jessica + Chris; hard kill switch on portfolio cap |
| 10 | Stripe SKU wiring sequence (LAB) | **(b) 1-by-1**: Signal Studio → SellerPilot → ComplianceSentinel |

### Phase 3 — Capital allocation

| # | Decision | Lock |
|---|---|---|
| 11 | Rigby ads budget | **(a) Defer entirely** — revisit on Decision 1 take-public trigger |
| 12 | PitchDeckForge Team tier | **(d) Defer "expert review" + rebrand Team tier** — see F2 deliverable for truthful copy |
| 13 | Signal Studio legal review | **(d) Demand-gate** — $2K cap; trigger condition spec'd in F1 deliverable |
| 14 | ComplianceSentinel legal review | **(b) Pre-approve $3K cap**, deploy on Stripe-ready (compliance market makes demand-gate impractical) |

### Phase 4 — Acquisition + customer-facing polish

| # | Decision | Lock |
|---|---|---|
| 15a | Signal Studio GTM channel | **(c) Direct outreach + Operator Edge cross-promo** |
| 15b | SellerPilot GTM channel | **(d) Sequenced** — Reddit r/AmazonFBA first → direct outreach when ≥10 customers → Shopify Partner ecosystem |
| 15c | ComplianceSentinel GTM channel | **(e) Sequenced** — Content + Communities first (compliance buyers buy on authority) |
| 16 | Operator Edge cross-promo placements | **(b+d) Inline-only now**; rotated paid placements when Operator Edge ≥2K subscribers |
| 17 | Rigby canonical proof | **(d) Hybrid** — Candidate A (local-internal demo) now; upgrade to Candidate B (consumer signup flow) on launch trigger |
| 18 | MentorForge persona naming | **(a) Stay functional** (code reviewer, system designer, etc.) — no individual or famous-style names — plus Phase 5 cleanup for 12-vs-8 persona count drift in BUILD_PLAN.md (F3 deliverable) |
| 19 | PitchDeckForge template styles | **(b) Persona-typed names** — **VC-Standard / Angel / Strategic / Growth** |
| 20 | DealFlowTracker LP exports | **(b) PDF + Excel** for v1; custom branded PDF as v2 feature |
| 21 | DealFlowTracker API exposure | **(e) Defer until first Fund-tier customer asks** — demand-gate |
| 22 | DealFlowTracker public intake widget | **(c) Defer + audit-ask 3 fund operators** — pure question, no commitment; revisit if 2+ say yes meaningfully |

## The 4 deliverables shipped

| ID | Deliverable | File | Repo |
|---|---|---|---|
| **F3** | MentorForge BUILD_PLAN.md drift fix (12 → 8 personas, 2 occurrences) | `docs/BUILD_PLAN.md` | `mentorforge` |
| **F2** | PitchDeckForge Team tier blurb truthful rewrite (`5 seats · expert review · API` → `5 seats · shared workspace · team admin`) | `src/lib/products.ts` Team tier blurb | `24-7-ai-global` |
| **F4** | PitchDeckForge spokesperson doc (new, parallel-structured with MentorForge) | `docs/spokesperson/20_pitchdeckforge.md` | `unified-donkey-betz` |
| **F1** | Signal Studio paid-interest signal spec (turns Decision 13 demand-gate into Chris-buildable spec; ~1.5 days estimated implementation) | `docs/specs/SIGNAL_STUDIO_PAID_INTEREST_SIGNAL_SPEC.md` | `unified-donkey-betz` |

## Phase 5 queue (carried forward — NOT shipped this session)

| # | Action | Owner | Cost |
|---|---|---|---|
| F5 | Audit the 4 PitchDeckForge styles in code — verify they meaningfully differ before names ship publicly | Chris (audit) + Jessica (review) | ~15 min Chris / 5 min Jessica |
| F6 | Ask 3 fund operators about intake widget (Decision 22 trigger) | Jessica (outreach) | days-weeks of wait |
| F7 | Stripe verification audit on 4 Suite products | Jessica + Chris's Stripe access | 30-60 min |
| #23 | Cross-Suite handoff E2E matrix (MentorForge → PitchDeckForge / Contract Concierge / DealFlowTracker) | Jessica drives, Chris/Claude support | 1-2 hr |
| #24 | TOS + e-signature legal review status check (Contract Concierge) | Jessica pings lawyer | 5 min ping; days wait |
| #25 | Marketplace policy research (SellerPilot — Amazon/Etsy/Shopify TOS) | Claude research + Jessica review | ~30 min |
| #27 | Rigby repo audit — what's actually in 24-7-ai-global for Rigby standalone | Claude audit + Jessica review | ~15 min |

## Chris's queue (12 tech decisions Jessica didn't touch)

Held back per Jessica's "business vs tech" frame. Chris owns:

1. Contract Concierge fleet routing fix path (new agent / extend / remove)
2. Signal Studio engine-side enrichment integration (v2 architecture)
3. ComplianceSentinel fleet routing (security_agent / null / skip u-d-b)
4. Engine-mismatch resolutions (cross-cutting C5)
5. Phase 0 cost-attribution SCHEMA (now unblocked — Jessica gave business rules in Decision 9)
6. SellerPilot Render API Blueprint deployment
7. ComplianceSentinel Render API Blueprint deployment
8. Rigby Q8 — products.ts update when public launch ratified (currently deferred per Decision 1)
9. Atlas deviation ratification (cross-cutting C7) — could be both, technically arch direction
10. F1 Signal Studio paid-interest signal — implement per spec (~1.5 days)
11. F5 audit + verify the 4 PitchDeckForge styles meaningfully differ in code
12. F7 Stripe verification audit collaboration (Chris's Stripe access)

## Patterns across all 22 decisions

- **Revenue-gated triggers** for strategic / capital decisions (1, 2, 3, 4, 11, 13)
- **Portfolio-consistent pricing** with deliberate vertical exceptions (8 for compliance market)
- **Conservative pre-revenue cost discipline scaling with success** (9)
- **Sequenced engineering load** to prevent context-switch tax (10, 14, 15b)
- **Honest scope cuts** when features lack delivery mechanism (12)
- **Demand-validation gates** for non-essential capital (13, 21, 22)
- **Editorial honesty over marketing fluff** (16, 18, 19)

## Worked example: how Decision 9 cost rules play out

To make Decision 9 concrete for Chris's schema implementation:

**Pre-revenue (today, $0 MRR):**
- Portfolio cap = `max($1.67, 40% × $0 / 30)` = **$1.67/day** = $50/mo
- Customer paying $30/mo Rigby → per-customer cap = `25% × $30 / 30` = **$0.25/day**
- Customer paying $79/mo ComplianceSentinel Pro → per-customer cap = **$0.66/day**
- Customer paying $249/mo Team → per-customer cap = **$2.08/day**

**At $1K MRR (per-product graduation threshold):**
- Portfolio cap = `max($1.67, 40% × $1000 / 30)` = `max($1.67, $13.33)` = **$13.33/day** = $400/mo

**At $10K MRR:**
- Portfolio cap = `max($1.67, 40% × $10000 / 30)` = **$133/day** = $4K/mo

Behavior at hard cap: **soft degrade to gpt-5-mini for the remainder of day; resets midnight.** Hard kill switch at portfolio cap + admin alert.

## Where the work landed

| Repo | Branch | Files | Status |
|---|---|---|---|
| `unified-donkey-betz` | `docs/session-1137-jessica-ratification-1-4` | Handoff + spokesperson doc + spec + 8 brief §9 appends + start-here overwrite + INDEX regen | PR pending |
| `mentorforge` | (branch) | `docs/BUILD_PLAN.md` (F3) | PR pending |
| `24-7-ai-global` | (branch) | `src/lib/products.ts` (F2 Team tier blurb) | PR pending |

## Sign-off + recommendations for Session 1138

1. **Chris ratification pass** — read the 22 decisions; redline any item where Jessica's read needs adjustment (especially Decision 9 cost rules — implementation-heavy)
2. **Phase 5 audit batch** — Jessica can knock out F5, #27, #24, #25 in ~75 min if Chris agrees with the 22 decisions as written
3. **Implement F1 spec** — Signal Studio paid-interest signal becomes the gating affordance for Decision 13. ~1.5 days Chris work.
4. **Implement Decision 9 cost-attribution schema** — Chris's lane; Jessica's business rules in this handoff are the input
5. **Stripe SKU wiring sequence** — Chris starts on Signal Studio first per Decision 10. Gated on Decision 13's paid-interest signal firing OR Jessica manual override.

## Open question for Chris

Nothing blocking. All 22 decisions are Jessica-business-side; Chris implementations are unblocked but parallel. Worst case: Chris disagrees with cost-rules math in Decision 9 — easy revisit, no architectural impact.

## Process learnings worth keeping

| Lesson | Source moment |
|---|---|
| **Business vs tech split is a real triage axis** — Jessica corrected my initial owner-bucket mid-session ("Chris is tech, I'm business"). Re-triage unlocked 22 vs the ~10 I'd initially queued. | Mid-Phase 2 |
| **"Worst Monday morning" prompt** (Session 1136 lesson) carried forward — used implicitly when offering format choices (e.g., dashboard vs sticker analogy was rejected by Jessica) | Decision 17 (Rigby proof pick) |
| **My on-the-fly rebrand suggestions can be sloppy** — Decision 12 rebrand committed to building features that don't exist (branding, priority queue). F2 surfaced this and Jessica chose truthful-today copy. **Audit existing copy BEFORE proposing rebrand.** | F2 execution |
| **Demand-validation gates compound** — Decisions 13, 21, 22 all use the same demand-gate pattern. Pattern recognition mid-session let Phase 4 close faster (Jessica recognized "this is the same as Decision 13" framing) | Decisions 21, 22 |
| **Numeric trigger thresholds need explicit lock** — Decision 13's "concrete paying-interest signal" was vague until F1 spec made it specific (≥5 users / 90 days OR ≥1 with willing-pay ≥$49 OR Jessica override). **Vague triggers don't fire.** | F1 execution |
| **22 decisions in one session is the upper bound** — natural fatigue point. Lower-value items (Phase 5 audits) should be a different session, not bolted onto a decision marathon. | Session close |

---

**Final close authored:** Session 1137 (Jessica + Claude). 22 decisions + 4 deliverables shipped. Phase 5 queue carried forward. Chris's tech queue unblocked.

**Branch state:** u-d-b `docs/session-1137-jessica-ratification-1-4` (this PR); mentorforge + 24-7-ai-global have parallel small PRs for F3 + F2.

**Bookmarked:** the 22 decisions become the substantive content for Session 1138's first move — Chris's ratification pass.
