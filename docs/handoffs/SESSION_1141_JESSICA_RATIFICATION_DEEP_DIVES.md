---
title: "Session 1141 — Chris's ratification deep dives on Jessica's 22 decisions"
date: 2026-05-24
status: complete
session: 1141
originating_session: 1141
previous_handoff: SESSION_1140_ACTION_CARDS_VERTICAL_SLICE.md
companion: SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md
owner: chris (ratifier) + claude (facilitator)
outcome: 17 accept-as-written + 3 ratify-shipped + 2 with Jessica clarification redlines (Decisions 9 and 19)
provenance_confidence: HIGH
provenance_note: Hand-authored handoff. Cited by Session 1158 narrative N (24/7 Global AI strategy milestone 7) — Chris's ratification of Jessica's 22 strategic decisions; F5 PitchDeckForge audit found Angel + Strategic don't map to existing code templates.
---

# Session 1141 — Chris's ratification deep dives

> **Purpose.** Session 1137 closed with 22 Jessica-locked decisions. The 1137
> handoff named Chris's ratification pass as the next-session-primary. This
> doc holds the tech-feasibility deep dives Chris drives on the decisions
> that touch implementation (#9, #10, #19, #15a-c) plus the bulk
> accept/redline calls on the remaining 17.
>
> **Source.** Decision text + Jessica-side rationale live in
> `SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md`. This doc only adds
> Chris's tech read + ratification status.

## Ratification status overview

| # | Decision | Status | Notes |
|---|---|---|---|
| 1 | Rigby take-public | ✅ accept | Jessica-side; no tech impact |
| 2 | 24/7 Global AI trademark | ✅ accept | Jessica-side; no tech impact |
| 3 | Colorado Family Law Concierge | ✅ accept | No product to build |
| 4 | Suite vs LAB graduation rule | ✅ accept | MRR tracking covered by Decisions 9 + 10 |
| 5 | Rigby pricing $30/mo | ✅ accept | Stripe SKU when Decision 1 trigger fires |
| 6 | Signal Studio pricing | ✅ accept | Stripe SKU input for Decision 10 |
| 7 | SellerPilot pricing | ✅ accept | Stripe SKU input for Decision 10 |
| 8 | ComplianceSentinel pricing | ✅ accept | Stripe SKU input for Decision 10 |
| **9** | **Cost attribution business rules** | ⚠️ **accept w/ 3 Jessica redlines** | See §Decision 9 deep dive |
| **10** | **Stripe SKU wiring sequence** | ✅ accept | See §Decision 10 deep dive |
| 11 | Rigby ads budget | ✅ accept | Jessica-side; no tech |
| 12 | PitchDeckForge Team tier defer | ✅ ratify shipped (F2, 1137) | Already done |
| 13 | Signal Studio legal review demand-gate | ✅ ratify shipped (F1, 1138) | Already done |
| 14 | ComplianceSentinel legal pre-approve $3K | ✅ accept | Capital allocation; no tech |
| **15a-c** | **GTM channels SS / SP / CS** | ✅ accept | See §Decision 15 deep dive |
| 16 | Operator Edge cross-promo placements | ✅ accept | Properly deferred (ad-server when ≥2K subs) |
| 17 | Rigby canonical proof hybrid | ✅ accept | Candidate A is current state |
| 18 | MentorForge persona naming functional | ✅ ratify shipped (F3, 1137) | Already done |
| **19** | **PitchDeckForge style names** | ⚠️ **accept w/ 1 Jessica redline + Chris retune** | See §Decision 19 + F5 deep dive |
| 20 | DealFlowTracker LP exports PDF+Excel | ✅ accept | PDF + Excel libs when product is built |
| 21 | DealFlowTracker API exposure defer | ✅ accept | Demand-gate; no tech |
| 22 | DealFlowTracker public intake widget defer+audit | ✅ accept | Jessica-driven audit |

**Headline:** 17 accept-as-written + 3 ratify-shipped + 2 with Jessica clarifications = 22/22 closed.

---

## Decision 9 — Cost attribution business rules

**Status:** deep-dive complete; **accept with 3 clarification redlines back to Jessica**.

### The decision precisely stated

- **Portfolio cap (daily):** `max($1.67, 40% × trailing-30d-MRR / 30)`
- **Per-customer cap (daily):** `25% × monthly_subscription / 30`
- **Behavior at cap:** soft-degrade to gpt-5-mini for remainder of day; resets midnight
- **Hard kill switch:** on portfolio cap
- **Telemetry:** daily Slack/Discord summary to Jessica + Chris

### Math at the inflection points

| State | Portfolio cap/day | Implied cost-of-revenue |
|---|---|---|
| $0 MRR (today) | $1.67 ($50/mo floor) | n/a |
| $1K MRR | $13.33 ($400/mo) | 40% |
| $5K MRR | $66.67 ($2K/mo) | 40% |
| $10K MRR | $133 ($4K/mo) | 40% |

| Per-customer at subscription | Daily cap | Notes (vs gpt-5-mini pricing) |
|---|---|---|
| $30/mo (Rigby) | $0.25 | ~833K output tokens/day — generous |
| $49/mo (Signal Studio Pro) | $0.41 | very generous |
| $79/mo (ComplianceSentinel Pro) | $0.66 | very generous |
| $249/mo (Team) | $2.08 | huge headroom |

**Verdict on shape:** math is conservative and self-funding. Approve.

### Tech-feasibility ratify checklist (Chris's call)

1. **Trailing 30d as the denominator.** Protective on upside (launch spike doesn't raise cap immediately), but lagging on downside (churn doesn't shrink cap for ~30 days → overshoot risk during decline). **Settle at schema time** — could split (trailing 7d for downside, trailing 30d for upside) but starts complex.
2. **Soft-degrade trigger ambiguity.** "100% cap" applies to which cap? Per-customer 100% should degrade just that customer; portfolio 100% should degrade everyone. The handoff doesn't fully separate these — **lock with Jessica before schema** (see redline 1 below).
3. **Hard kill threshold.** Jessica wrote "kill switch on portfolio cap" but soft-degrade already fires at 100% portfolio. Is hard-kill at exactly 100% (sharper than per-customer) or at 120%/150% (escalation past soft-degrade)? **Lock with Jessica** (see redline 2 below).
4. **Internal/agent/beat-task spend.** Content generation, action-card generator, signal aggregation, agent rotations all draw LLM tokens but aren't tied to a paying customer. Two paths: (a) draw from portfolio cap with no per-customer accounting, or (b) synthetic "internal" workspace with its own budget allocation. **Lock with Jessica** (see redline 3 below).
5. **Customer upgrade lag.** When customer goes $30 → $249, cap rise = real-time on Stripe webhook or daily reconcile? **Settle at schema time** — real-time is fine if webhook handler updates a cached `monthly_subscription` field on the workspace.
6. **Already-on-gpt-5-mini at cap.** If a customer is already on minimal model and hits per-customer cap, "soft-degrade" is a no-op. Hard cut or let through with flag? **Settle at schema time** — recommend hard cut with a "today exhausted" UI signal.

### Open redlines back to Jessica (3 items)

1. **Lock soft-degrade scope explicitly.** Per-customer 100% degrades that customer; portfolio 100% degrades everyone. Confirm.
2. **Lock hard-kill threshold explicitly.** 100% portfolio (= immediate kill on first overshoot) or 120%/150% (= escalation tier above soft-degrade). Pick one number.
3. **Lock internal-spend accounting.** Synthetic "internal" workspace with its own allocation, OR draw straight from portfolio cap with no attribution. Pick one — informs the `LLMCallLog.workspace` FK nullability.

### Open business questions (flag for follow-up, not blocking)

- **40% portfolio is gross COGS.** Stripe fees (~3%), hosting, other per-customer costs need to leave room before LLM budget. Effective LLM budget is closer to 30% MRR. Worth re-anchoring with Jessica once Stripe goes live.
- **"Daily summary" timezone.** Mountain time at midnight after daily rollup completes? Confirm.

### Chris's recommendation

**Accept Decision 9 with three clarification redlines back to Jessica.** Items 1, 2, 6 of the ratify checklist are tech-implementation calls — Chris's lane to settle when writing the Phase 0 schema. Items 3, 4, 5 require Jessica's business call before schema lock.

---

## Decision 10 — Stripe SKU wiring sequence

**Status:** deep-dive complete; **accept as written (zero Jessica redlines)**.

### The decision precisely stated

Jessica locked: **(b) 1-by-1**: Signal Studio → SellerPilot → ComplianceSentinel.

Rationale (per 1137 handoff): "sequenced engineering load to prevent context-switch tax."

### Why this order specifically

| Product | Readiness | Pre-work needed before Stripe |
|---|---|---|
| **Signal Studio** | Most mature (Phase 1+2 shipped, 1138 paid-interest gate live, 1140 action cards live) | Decision 13 trigger needs to fire OR Jessica override |
| **SellerPilot** | Fleet-routed, Render deploy queued (tech-queue #6) | Render deploy first → public API → then Stripe |
| **ComplianceSentinel** | Fleet routing unresolved (tech-queue Q4), legal review pre-approved $3K (Decision 14) | Routing fix + Render deploy (#7) + legal in parallel |

Ordering matches readiness gradient. No reason to push back.

### Tech-feasibility ratify checklist

1. **"1-by-1" interpretation.** "Context-switch tax" rationale points to "ship SS fully, observe, THEN start SP code" — not "ship all three at once, go-live sequentially." Calendar-meaningful: SP code work starts only after SS is in customer hands.
2. **Shared billing infra strategy.** Build pragmatic-for-SS, refactor at SP when its needs (Shopify Partner-paid model, etc.) force the abstractions. YAGNI applies — three SaaS billing setups are not radically different. Avoid over-abstracting day-one.
3. **Hard ordering: Decision 9 schema MUST land before Decision 10.** Stripe webhook writes `workspace.monthly_subscription` which is the input to per-customer cap math. If Phase 0 cost-attribution schema isn't shipped first, webhook has nothing to write to. **This is a hard constraint, not a preference.**
4. **F1 paid-interest trigger is the SS go-live gate.** SS Stripe code can ship + merge, but customer flow only opens when ≥5 users / 90 days OR ≥1 with willing-pay ≥$49 OR Jessica override (per F1 spec, shipped 1138). At $0 MRR today, trigger almost certainly hasn't fired. **SS Stripe = code-complete, switched off, until trigger.**
5. **SP + CS Render deploys are upstream.** Both on tech queue (#6, #7). Stripe is downstream of "the product has a public API to bill against." Can do local-only Stripe testing without deploys, but not go-live.

### Open redlines back to Jessica

**Zero.** Sequencing is sound, rationale holds. All dependencies are Chris-side.

### Chris-side implementation sequence (settled here)

1. **Phase 0 cost-attribution schema** (Decision 9 implementation) — prerequisite for everything else
2. **SS Stripe wiring** — code-complete, merged, switched off pending F1 trigger fire OR Jessica override
3. **SP Render deploy → SP Stripe wiring** (sequenced after SS is in customer hands)
4. **CS routing fix + Render deploy + legal kickoff → CS Stripe wiring** (sequenced after SP)

### Chris's recommendation

**Accept Decision 10 as written.** Implementation sequence locked above. No bounce-back to Jessica needed.

---

## Decision 19 + F5 — PitchDeckForge template style names

**Status:** deep-dive complete + F5 audit complete; **accept Decision 19 names with 1 Jessica clarification redline + Chris-side code retune required**.

### The decision precisely stated

Jessica locked: **(b) Persona-typed names** — VC-Standard / Angel / Strategic / Growth.

### F5 audit findings — code reality (`pitchdeckforge/backend/app/main.py:632-653`)

4 templates exist with meaningfully different system prompts, slide guidance, and tones:

| Code template | What it actually does | Axis |
|---|---|---|
| **clean** | Minimal aesthetic, whitespace-heavy, "let the data speak," 3 bullets max | aesthetic |
| **investor** | Institutional VC focus: TAM/SAM/SOM, MRR/ARR, unit economics, financial rigor | audience |
| **growth** | Narrative arc: hook → conflict → proof → vision, 3-year momentum story | narrative shape |
| **product** | Product-led: user scenarios, screenshots-implied, DAU/retention/NPS | audience |

**F5 verdict:** the 4 templates DO meaningfully differ (different prompts, different guidance, different tone descriptors). ✅

### The mismatch

| Jessica's locked name | Closest code template | Match quality |
|---|---|---|
| VC-Standard | `investor` | Strong (both institutional VC audience) |
| Growth | `growth` | Exact match |
| **Angel** | _none_ | **NO MATCH** — angel investors have a distinct profile not currently coded |
| **Strategic** | _none_ | **NO MATCH** — strategic/corporate investors not currently coded |
| (unmapped code template) | `clean` | Has no Jessica name; it's an aesthetic not an audience |
| (unmapped code template) | `product` | Has no Jessica name; product-led targets is its own audience |

**Dimensional mismatch:** Jessica's names imply 4 audience personas (who's reading). Code differentiates on aesthetic + audience + narrative shape. Axes don't line up.

### Public-side context (`24-7-ai-global/src/lib/products.ts`)

- Line 67: "4 deck styles · investor-persona prompts" — Jessica's persona-typed framing already in marketing copy
- Line 78: "Starter · Free · 2 decks · all 4 styles" — names need to be public-ready before this ships publicly
- The 4 specific names (VC-Standard / Angel / Strategic / Growth) are NOT in `products.ts` yet — F5 is genuinely gating the publish step

### Three paths considered

1. **Retune prompts to match Jessica's audiences.** Rewrite `clean` for Angel audience, rewrite `product` for Strategic audience. Keep `investor` → VC-Standard, `growth` → Growth. **Cost: ~2 system prompts + slide guidance, ~20-50 lines each. Best alignment.**
2. **Keep code as-is, ship Jessica's names as labels only.** Users pick "Angel," get clean-style deck. **Low effort, high deception risk.**
3. **Bounce names back to Jessica: rename to match code's actual axes.** **Risks "audit found small gap → relitigate decision" trap. Jessica's business call was right.**

### Chris's recommendation

**Path 1 — retune the two unmapped templates to match Jessica's locked names.** Decision 19 was a naming decision; the names she picked map to audiences. Right response when audit finds a code gap is to retune the code, not retreat the names.

### Open redline back to Jessica (1 item)

- **Confirm clean-template fate.** Retired or renamed-then-retuned? If retired, ship 3 styles publicly instead of 4. If retuned, what audience does "Angel" represent precisely (smaller checks → narrative bias? Just "individual investor" generic)?

### Chris-side work unlocked by ratification

- Retune `clean` template's system prompt + slide guidance for "Angel" audience (after Jessica confirms the audience definition)
- Retune `product` template's system prompt + slide guidance for "Strategic" audience
- Rename `clean` → angel, `investor` → vc_standard, `growth` → growth (no-op), `product` → strategic in `TEMPLATE_CONFIGS` dict
- Add migration to map any existing deck rows with old template names → new names (frontend `App.tsx:307,481-484,978-989` also needs name updates)
- Update `24-7-ai-global/src/lib/products.ts` Starter tier blurb when names ship publicly

---

## Decision 15a-c — GTM channels

**Status:** deep-dive complete; **accept all three as written (zero Jessica redlines)**.

### The decisions precisely stated

- **15a (Signal Studio):** (c) Direct outreach + Operator Edge cross-promo
- **15b (SellerPilot):** (d) Sequenced — Reddit r/AmazonFBA first → direct outreach when ≥10 customers → Shopify Partner ecosystem
- **15c (ComplianceSentinel):** (e) Sequenced — Content + Communities first (compliance buyers buy on authority)

### Tech-feasibility scan

**15a — Signal Studio**

| Channel | Tech coupling |
|---|---|
| Direct outreach | Zero. Manual sales motion. |
| Operator Edge cross-promo | Low. Newsletter mentions Signal Studio; Signal Studio UI links back. Optional UTM attribution param for conversion measurement. |

**15b — SellerPilot**

| Phase | Tech coupling |
|---|---|
| Reddit r/AmazonFBA first | Zero code. Manual posts. Optional `/from/reddit` landing route for attribution. |
| Direct outreach @ ≥10 customers | Zero code. |
| Shopify Partner ecosystem | **Real engineering** (OAuth, app store listing, partner-token billing, install webhooks). Multi-week sprint. **Properly deferred** behind the ≥10-customer milestone. |

**15c — ComplianceSentinel**

| Channel | Tech coupling |
|---|---|
| Content marketing | Minimal. Blog/resource hub on 24-7-ai-global Next.js side. Doesn't touch product code. |
| Communities | Zero code. |

### Open redlines back to Jessica

**Zero.** All three are GTM/business calls with low or properly-deferred tech coupling. 15b's sequencing is a good example of Decision 9's cost discipline applied to engineering load.

### Chris-side notes (settle at implementation time)

- **15a:** Define UTM tag convention once for the whole Suite (`?utm_source={origin}&utm_medium={channel}&utm_campaign={product}`). Pure ops/analytics.
- **15a/16 connection:** Operator Edge "inline-only now; rotated paid placements when ≥2K subscribers." Current state needs zero ad-server infra. When 16 triggers, placement-rotation mechanism needed.
- **15b:** Reddit landing route on 24-7-ai-global = 5-minute Next.js add. Optional but cheap.
- **15b Shopify Partner:** When triggered, multi-week sprint. Flag on future roadmap as "real engineering investment."
- **15c:** Blog/resource hub is Jessica + 24-7-ai-global frontend work. Out of scope for u-d-b backend.

### Chris's recommendation

**Accept Decisions 15a, 15b, 15c as written. Zero Jessica redlines.**

---

## Remaining 17 decisions — bulk pass

All 17 default-accepted after Chris's tech-feasibility scan. Three (12, 13, 18) are "ratify already-shipped state" rather than "approve new work."

| # | Decision | Tech impact | Status |
|---|---|---|---|
| 1 | Rigby take-public defer | None | **Accept** |
| 2 | 24/7 Global AI trademark wait | None | **Accept** |
| 3 | Colorado Family Law Concierge park | None (no product) | **Accept** |
| 4 | Suite vs LAB graduation rule (≥$1K MRR sustained ≥2 mo) | MRR tracking covered by Decision 9 + 10 | **Accept** |
| 5 | Rigby pricing $30/mo | Stripe SKU when Decision 1 trigger fires | **Accept** |
| 6 | Signal Studio Free/$49/$99 | Stripe SKU inputs for Decision 10 | **Accept** |
| 7 | SellerPilot Free/$39/$99 | Stripe SKU inputs for Decision 10 | **Accept** |
| 8 | ComplianceSentinel Free/$79/$249 | Stripe SKU inputs for Decision 10 | **Accept** |
| 11 | Rigby ads budget defer | None | **Accept** |
| 12 | PitchDeckForge Team tier defer + rebrand | **Already shipped** (F2 in 1137) | **Accept (ratify shipped state)** |
| 13 | Signal Studio legal review demand-gate | **Already shipped** (F1 spec in 1138) | **Accept (ratify shipped state)** |
| 14 | ComplianceSentinel legal pre-approve $3K | None (capital allocation) | **Accept** |
| 16 | Operator Edge cross-promo (inline now; paid @ ≥2K subs) | Inline = zero; paid = ad-server infra when triggered | **Accept** |
| 17 | Rigby canonical proof hybrid (A now → B on launch) | Candidate A is current state | **Accept** |
| 18 | MentorForge persona naming functional | **Already shipped** (F3 in 1137) | **Accept (ratify shipped state)** |
| 20 | DealFlowTracker LP exports PDF + Excel v1 | PDF + Excel export libs when product is built (scoped) | **Accept** |
| 21 | DealFlowTracker API exposure defer | None (demand-gate) | **Accept** |
| 22 | DealFlowTracker intake widget defer + audit-ask | None (Jessica-driven audit) | **Accept** |

---

## Ratification close-out

### Final composite status (all 22)

| Bucket | Count | Decisions |
|---|---|---|
| **Accept as-written** | 17 | 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 14, 15a, 15b, 15c, 16, 17, 20, 21, 22 |
| **Accept (ratify already-shipped state)** | 3 | 12, 13, 18 |
| **Accept with Jessica redlines** | 2 | 9 (three clarifications), 19 (one clarification + Chris-side retune) |

19 of 22 are pure-accept. 3 are "ratify already-shipped." 2 need Jessica clarification before Chris can fully implement.

### Draft message to Jessica (via Rigby)

Four clarification asks to bounce back, framed as a single message so Jessica can answer in one sitting:

```text
Chris ratification pass complete on the 22 decisions from Session 1137.
17 accept as-written, 3 ratify already-shipped state, 2 need brief
clarification before tech implementation can lock cleanly:

Decision 9 (cost attribution rules):
  1. Soft-degrade scope: per-customer 100% degrades just that
     customer; portfolio 100% degrades everyone. Confirm?
  2. Hard-kill threshold: soft-degrade fires at 100%. Hard-kill
     at 100% (= immediate kill on first overshoot) or 120% / 150%
     (= escalation tier above soft-degrade)? Pick one number.
  3. Internal-spend accounting: agent rotations, content gen,
     action-card generator, signal aggregation all draw LLM tokens
     but have no paying customer. Synthetic "internal" workspace
     with its own budget allocation, OR draw straight from portfolio
     cap with no per-workspace attribution? Pick one — informs the
     LLMCallLog.workspace FK nullability.

Decision 19 (PitchDeckForge style names):
  4. F5 audit found 2 of your 4 names (VC-Standard, Growth) map
     cleanly to existing code templates; the other 2 (Angel,
     Strategic) don't match any current template. Recommendation
     is Chris-side retune of the two unmapped templates (clean,
     product) to match Angel and Strategic audiences. Question:
     does "Angel" mean specifically smaller-check individual
     investors (founder narrative > data rigor), or just
     "non-institutional"? Answer drives the system prompt rewrite.

All other 18 decisions accepted; tech sequencing locked in
deep-dive doc (docs/handoffs/SESSION_1141_JESSICA_RATIFICATION_DEEP_DIVES.md).
```

### Tech-side implementation sequence (now unblocked)

1. **Phase 0 cost-attribution schema** (Decision 9 implementation, gated on Jessica's 3 clarifications above)
2. **Signal Studio Stripe wiring** (Decision 10 implementation, gated on Phase 0)
3. **PitchDeckForge template retune + rename** (Decision 19 implementation, gated on Jessica's clarification #4)
4. **F5 audit findings written** — Chris-side code retune work scoped in deep-dive doc above

### Process notes worth keeping

- **F5 audit surfaced a real gap** — Jessica's naming decision (Decision 19) implied audience-typed prompts, but only 2 of 4 code templates were audience-typed. The audit caught it before names shipped publicly. F5's value was non-zero.
- **17 of 22 accept-as-written** suggests Jessica's Session 1137 marathon was well-calibrated. The redlines are scoped to implementation-blocker clarifications, not strategic disagreements.
- **"Ratify already-shipped state" is a distinct bucket** — 3 of the 22 decisions had already been implemented as F1/F2/F3 deliverables. Worth flagging explicitly in future ratification passes so it's not silently re-accepted.
