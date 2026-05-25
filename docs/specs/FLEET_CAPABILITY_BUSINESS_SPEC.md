---
title: "Fleet Capability — Business framing & go-to-market (Atlas-anchored)"
status: draft
version: v3 (Atlas-anchored)
session: 1134-pre
generated: 2026-05-23
last_reviewed: 2026-05-24 (Session 1141 pricing supersede pass)
author: claude + rigby (grounding pass)
companion_docs:
  - specs/FLEET_CAPABILITY_MANIFEST_SPEC.md   # the engineering twin of this doc
  - 24_7_GLOBAL_AI_APP_ATLAS.md               # strategy anchor — Phase 1 = Rigby standalone flagship
  - UDB_BEHAVIOR_LAYER.md                     # where brand-voice / claim guardrails live
  - handoffs/SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md   # Jessica's locked pricing + cost-rules
  - handoffs/SESSION_1141_JESSICA_RATIFICATION_DEEP_DIVES.md   # Chris ratification + deep dives on Decisions 9/10/19/15
audience: non-technical (founder/investor/buyer); same truth as the engineering spec, different vocabulary
---

> **Pricing supersede — Session 1137 + 1141.** Sections 5.1 and 5.2
> below were written 2026-05-23 with illustrative pricing bands.
> Session 1137 (2026-05-24) locked the **actual** Suite pricing for
> Signal Studio, SellerPilot, ComplianceSentinel + Rigby flagship +
> cost-attribution rules. Session 1141 (2026-05-24) ratified those
> decisions on Chris's tech side. **The locked values supersede the
> illustrative §5 tables.** This doc still describes the eventual
> tiered Suite *shape*; the actual prices and cost rules now live in
> the Session 1137 handoff (anchor source) and Session 1141 deep dives
> (Chris's tech-feasibility scan + Jessica clarification redlines).
> Specific drifts noted inline at §5.1 and §5.2.

# Fleet Capability — Business Framing (v3, Atlas-anchored)

> **What changed in v3.** v1-v2 framed the GTM as a 7-app tiered
> Suite ready to sell. Rigby's grounding pass (2026-05-23) showed
> that's ahead of where the App Atlas (the actual strategy doc)
> places us. Atlas says **Phase 1 is Rigby standalone at
> `app.247globalai.com` for $20-30/mo** — one focused product
> first, sibling apps explicitly deferred ("Standalone sibling
> apps — defer"). Character OS / spokesperson video is Phase 4+,
> parked until paying customers demand it.
>
> **v3 keeps the capability-bundle design** but re-sequences the
> business story around Atlas: Phase 1 is one product, not seven;
> the tiered Suite is the post-validation evolution; the
> spokesperson tier is the long-term unlock. Every claim in v3
> traces back to either a runtime artifact or to the Atlas itself.

---

## 0. The 60-second version (re-anchored)

**What we're actually shipping next** (per App Atlas Phase 1):

- **Rigby standalone** at `app.247globalai.com`, **$20-30/mo
  flagship subscription**. The text-only personal AI assistant
  with 100+ tools, real-time data, and agent dispatch. **One
  polished product** before fragmenting across verticals.
- **Signal Studio** as the flagship vertical (Atlas-named) —
  already has the most product surface built: live curated signal
  clusters, daily Top-10 snapshots, SSE refresh.
- **Contract Concierge** as the first Suite candidate — has the
  Draft Library demo working end-to-end (artifact push + pull +
  SSE notifications, Session 1129).

**What's deferred per Atlas** (not selling yet):

- mentorforge, pitchdeckforge, sellerpilot, dealflowtracker,
  compliancesentinel — identity provisioned + plumbing wired
  (Sessions 1125–1133), but **product intent for each is
  undefined**. They unpark when (a) the next session's
  app-by-app discovery fills in their intent AND (b) Rigby
  Phase 1 hits its KPIs.
- **Character OS / spokesperson video** — Atlas says park until a
  paying customer asks for a face. Treat as Phase 4+ unlock.

**What this doc is for**: it describes the **tiered Suite + audit-
ready trust + spokesperson video** business that the capability
bundle eventually enables. It is **not** a GTM plan for the next
30 days — that's Atlas Phase 1 (Rigby flagship). Treat v3 of
this doc as the **Phase 2–4+ evolution plan** that activates as
sibling apps unpark and Character OS unparks.

---

## 1. The opportunity

### 1.1 Who hurts today (unchanged)

Small-business operators (solo founders, micro-agencies,
specialized professionals) face two bad choices for AI tooling:

- **Generic ChatGPT-style wrappers** — cheap, but don't know the
  operator's domain, can't see live data, can't take real actions.
- **Custom-built enterprise AI + agency video production** — does
  all of the above, but $50k+ to build and $2k+ per video segment.
  Only Fortune 500 can justify it.

There's a gap in the middle: **pre-tuned, domain-specific AI
products priced for someone running a small business**. Atlas
Phase 1 attacks this gap with Rigby (the personal AI assistant)
first; the tiered Suite + spokesperson video are the long-term
expansion.

### 1.2 What's actually built right now

Per Rigby's grounding pass + Atlas v1:

| Surface | Atlas status | Real shipping evidence |
|---|---|---|
| **Rigby standalone** | Phase 1 flagship | u-d-b's core PA path; 100+ tools; 80 spiders; 83 agents. Web UI being polished. |
| **Signal Studio** | Flagship vertical | Live: SSE-streamed curated signal clusters, Top-10 daily, refresh pill (1131-1132) |
| **Contract Concierge** | Suite candidate | Live: Draft Library, artifact push/pull, two-hop SSE events (1129) |
| mentorforge | Deferred | Identity provisioned; no documented user/workflow/output beyond name |
| pitchdeckforge | Deferred | Identity provisioned; no documented user/workflow/output beyond name |
| sellerpilot | Deferred | Identity provisioned; no documented user/workflow/output beyond name |
| dealflowtracker | Deferred | Identity provisioned; no documented user/workflow/output beyond name |
| compliancesentinel | Deferred | Identity provisioned; routing intentionally disabled (default null, empty allowlist) |

**Honest read**: the "Suite of 7" we sketched in v1-v2 is **3
actively-developed surfaces + 5 deferred apps with plumbing but
no product intent yet**. The discovery work to fill those gaps is
explicitly the next session per Chris.

### 1.3 The spokesperson layer (Character OS) — FUTURE

Per Atlas v1, Character OS / avatar work is **parked** until a
paying customer demands a face. So:

- The spokesperson-as-output story (ads, demos, persona-narrated
  dashboards) is real *in principle* — we own Character OS as a
  separate runtime with active development on its own track.
- But it is **not** part of the near-term GTM. v3 keeps the
  design recorded; v1-v2's framing of "spokesperson tier as the
  visible Pro-tier upsell" is correct strategy but wrong timing.
- The brand-voice promise ("MentorForge can use the Coach
  persona but never the Legal persona") becomes a Phase 4+
  product feature.

### 1.4 The wedge (re-anchored)

For each *actively-developed* surface:

- **Rigby standalone** is the wedge that gets a first cohort of
  paying users at low price. Validates per-seat economics + tool-
  call success metrics before vertical fragmentation.
- **Signal Studio** is the wedge into "people who pay for
  signal/intelligence dashboards" — its live curated experience
  is the differentiator vs static reports.
- **Contract Concierge** is the wedge into "people who pay for
  legal-doc productivity" — Draft Library is the visible "this
  saves me 80% of redline time" moment.

The capability bundle + spokesperson layer become the wedge for
the *eventual* tiered Suite and white-label partner sales. They
are not the wedge for the next 30 days.

---

## 2. The product structure this unlocks (sequenced by Atlas phase)

### 2.1 Phase 1 — Rigby flagship (what to sell NEXT)

Atlas-defined:

- Single product: Rigby at `app.247globalai.com`.
- $20-30/mo flat tier (Atlas Phase 1 KPIs assume positive per-
  seat unit economics at this price).
- Onboarding: 5-min "Rigby is working for me" first-run.
- Per-account daily $ cap (~$1.50/day) to survive a bad actor.
- Phase 1 KPIs: first paying customer in week 6; 5 paying
  customers by week 8-10; LLM spend per seat ≤ 50% of
  subscription.

**Capability bundle role in Phase 1**: minor — Rigby standalone
doesn't need per-app authz scoping because it IS the one app.
The bundle work that ships in Phase 1 supports signal-studio +
contract-concierge as sibling surfaces (audit-ready, scoped,
visible to interested customers but not headline sale).

### 2.2 Phase 2-3 — Tiered Suite per app (when sibling apps unpark)

The structure from v2 (Rigby's corrected tier axes) still holds —
but only activates per app, as each app unparks with documented
product intent:

| Tier axis | What customer experiences |
|---|---|
| **Automation level** | Read + assist → scheduled monitoring + drafts → autopilot within approved scopes |
| **Data freshness** | Weekly → daily → near-real-time |
| **Spokesperson output** | Text only → push-to-speak video (Phase 4+) → multi-persona + conversational (Phase 4+) |
| **Governance & audit** | Basic logs → exportable audit → custom retention + kill-switch |

Each tier is **a slice of capabilities we already have or are
building**. Tier axes are things customers recognize: *"how much
can it do without me approving each step,"* *"how fresh is the
data,"* *"can it speak for my brand on camera,"* *"who can prove
what happened."*

Per Atlas: sibling apps don't enter this tiered model until they
unpark, which requires (a) documented product intent (next
session's work) AND (b) Rigby Phase 1 validating per-seat
economics first.

### 2.3 Phase 4+ — Spokesperson layer activates

Per Atlas: "Slice 4 (avatar realtime) becomes a v2 unlock for
when a paying customer asks for a face."

When the trigger fires:

- Per-app spokesperson allowlist activates (the 5th capability
  axis from the engineering spec).
- Suite pricing adds a spokesperson-minutes meter separate from
  the action meter.
- Brand-voice guarantee becomes a mechanical product feature for
  white-label / partner sales.

### 2.4 Bundle vs. single-app pricing — Phase 3+

When sibling apps unpark and tier per-app, Suite subscription at
~35% off summed Pro is the standard shape. **Not active today**;
recorded for Phase 3+.

---

## 3. The trust story (mostly Phase 2-4+)

### 3.1 Phase 1 trust posture (today)

Rigby standalone needs:

- Per-account daily $ cap (Atlas Phase 1 requirement).
- Per-workspace cost attribution (one of the 4 ✗ rows in
  `COST_SURVIVAL_AUDIT.md` that must close before external
  SaaS launch).
- Basic audit (already shipping via PA-chat audit table from
  Session 1132).

The capability bundle's audit layer adds **per-call observability**
that the Phase 1 launch can leverage day one — "Rigby called
these tools on your behalf this week." Doesn't require per-app
authz scoping (Rigby IS the one app).

### 3.2 Phase 2-3 trust story (when sibling apps unpark)

When a customer asks "what data does Contract Concierge actually
touch on my behalf?", the answer becomes:
**"Contract Concierge can only invoke the legal-drafting
specialist, the contract-clause data feed, and the
document-export action. Everything else is denied by default —
literally the manifest, written in plain English."**

That's the deal-killer-becomes-deal-closer moment for:
- Law firm IT lead doing vendor security review.
- Regulated-industry customer.
- White-label partner.

### 3.3 Phase 4+ brand-voice guarantee (when spokesperson unparks)

The mechanical guarantee — "the system literally cannot
misrepresent your brand" — activates when Character OS unparks.
Until then, brand voice is editorial (behavior layer
guidelines), not enforced.

### 3.4 Audit + kill-switch (cross-phase)

The audit trail + per-customer override (kill-switch) infrastructure
ships in Phase 1 (mostly) and applies to all phases. Same
mechanism is incident response + customer governance lever.

---

## 4. Go-to-market sequencing (re-anchored)

### 4.1 Phase 1 — Rigby flagship only

Per Atlas:

- **Phase 1 wedge** = personal AI assistant at $20-30/mo.
- Discovery = Operator Edge newsletter conversion + indie hacker
  / Twitter communities.
- Sales motion = self-serve, Stripe checkout, no sales team.
- KPIs = first paying customer week 6; 5 by week 8-10; per-seat
  economics positive.

**Sibling apps stay parked**, surfaced only to interested customers
as "coming after Rigby validates." Sibling-app development
continues (signal-studio, contract-concierge) but as the
infrastructure that the post-Rigby tiered Suite will ride on.

### 4.2 Phase 2-3 — Sibling apps unpark per Atlas trigger

When Rigby Phase 1 KPIs hit AND sibling apps have documented
intent (next session's work):

- First-buyer order (per v2): solo founders/coaches → vertical
  specialists → agencies/consultancies for white-label.
- Tier structure from §2.2 activates per app.
- Capability bundle's per-app authz becomes load-bearing for
  white-label sales.

### 4.3 Phase 4+ — Spokesperson layer activates

When a paying customer demands persona-narrated output AND
Character OS unparks:

- Spokesperson allotment per tier becomes a real meter.
- Brand-voice guarantee becomes the white-label closing argument.

### 4.4 What we are NOT selling (cross-phase)

Per existing project rules: we don't sell "the engine" (u-d-b)
directly. The seven apps are eventual products; Rigby standalone
is the Phase 1 product. We don't sell Character OS as a
standalone product; it's the production runtime behind eventual
Phase 4+ spokesperson features. Mentioning the shared backbone in
investor conversations is fine; selling backbone access as a
SKU is a different business not in scope.

---

## 5. Pricing (re-anchored)

### 5.1 Phase 1 — what we actually price first

Per Atlas: **Rigby flagship at $20-30/mo flat**. One product, one
price band, Stripe checkout. Phase 1 KPI gate is per-seat unit
economics (LLM spend per seat ≤ 50% of subscription).

> **Superseded by Session 1137 Decision 5 (2026-05-24)**: Rigby
> flagship locked at **$30/mo flat** (top of the $20-30 band). Per-
> account cap originally noted as ~$1.50/day is now locked at
> **$1.67/day pre-revenue portfolio cap floor + $0.25/day per
> $30/mo customer** per Decision 9. See SESSION_1137 handoff
> (anchor) and SESSION_1141 deep dive (§Decision 9 math + 3 Jessica
> clarification redlines on soft-degrade scope, hard-kill
> threshold, and internal-spend accounting). Activation gated on
> Decision 1 take-public trigger.

### 5.2 Phase 2-3 — illustrative per-app pricing (not committed)

These bands are **for shaping the eventual tiered Suite, not
near-term sales**. Activates per app, as each unparks.

> **Superseded by Session 1137 Decisions 6/7/8 (2026-05-24)** for
> 3 of the 7 apps. Tier names also changed: spec uses Starter/Pro/
> Business; Jessica locked Free/Pro/Team. **The locked values
> below are the authoritative numbers**; the illustrative table
> after this note is preserved for the 4 apps Jessica didn't price
> directly.
>
> | App | Locked tiers (Jessica Session 1137) |
> |---|---|
> | signal-studio | **Free + $49 Pro + $99 Team** (Decision 6) |
> | sellerpilot | **Free + $39 Pro + $99 Team** (Decision 7) |
> | compliancesentinel | **Free + $79 Pro + $249 Team** (Decision 8 — deliberately above portfolio norm for compliance market) |
>
> Stripe SKU wiring sequence locked **1-by-1**: Signal Studio →
> SellerPilot → ComplianceSentinel (Decision 10). Hard prerequisite:
> Phase 0 cost-attribution schema (Decision 9) must land first.
> See SESSION_1141 deep dive §Decision 10 for the full
> implementation sequence.

**Illustrative bands (pre-Session-1137, preserved for the 4
unpriced apps):**

| App | Starter (text only) | Pro (+ spokesperson when Phase 4+) | Business (multi-persona + audit, Phase 4+) |
|---|---|---|---|
| signal-studio | ~~$49~~ → Free / $49 Pro / $99 Team (locked) | ~~$149~~ | ~~$349~~ |
| contract-concierge | $79 | $229 | $549 |
| mentorforge | $29 | $99 | $249 |
| pitchdeckforge | $49 | $149 | $349 |
| sellerpilot | ~~$49~~ → Free / $39 Pro / $99 Team (locked) | ~~$149~~ | ~~$349~~ |
| dealflowtracker | $79 | $199 | $499 |
| compliancesentinel | ~~$99~~ → Free / $79 Pro / $249 Team (locked) | ~~$249~~ | ~~$599~~ |

Suite (all 7) at Pro tier: ~$899/mo (~35% off summed Pro). Suite
at Business tier: ~$1,999/mo. White-label / Enterprise: custom.
**All Phase 3+ — not in market.**

Per-app Pro and Business tiers require the spokesperson layer to
activate (Phase 4+). Until then, only Starter tiers per app would
be sellable, and only after the app has documented intent.

### 5.3 Margin assumptions

- Phase 1 (Rigby): per-seat LLM cost ≤ 50% of $20-30 = $10-15/mo
  ceiling. Validated by daily cap + per-workspace cost attribution.
- Phase 2-3 (per-app Starter tiers): ~20% LLM/infra cost target.
- Phase 4+ (spokesperson tiers): ~25-30% cost target (render
  economics heavier than LLM).

Pricing reviews every 6 months once Phase 1 has real customer
data.

---

## 6. What we have to build to make this real (re-sequenced)

The capability-bundle deliverables from v1-v2 are still correct.
What changes in v3 is **when each ships relative to Atlas
phases**.

### 6.1 Phase 1 prerequisites (already mostly built, finishing now)

- Rigby standalone web app at `app.247globalai.com` (Atlas
  Phase 1 deliverable list — items 1-8).
- Per-workspace cost attribution + per-account daily cap.
- PA-chat audit table (Session 1132 — already shipped).
- Reject-mode flip on `/api/pa/chat/` (1134 (Y) — queued).

### 6.2 Phase 2-3 deliverables (capability bundle for sibling apps)

When sibling apps unpark per Atlas trigger:

- **The capability bundle file** — per-app allowlist for
  specialists / data feeds / scheduled jobs / assistant actions.
  Lives in source control.
- **Per-customer override** — disable specific capabilities for
  a customer account without code deploy. Incident-response
  kill-switch.
- **Capability audit log** — every capability use (or deny) logged
  with timestamps; auditor-exportable CSV.
- **Safety phase** — warn-only logging → ≥3 days clean → enforce
  per axis.
- **Operator view** — Rigby tool or admin UI.

Engineering spec has the full implementation plan
(`FLEET_CAPABILITY_MANIFEST_SPEC.md`).

### 6.3 Phase 4+ deliverable (spokesperson authz + brand-voice)

When Character OS unparks per Atlas trigger:

- Per-app spokesperson allowlist + modalities.
- Render-request boundary between u-d-b (authz) and Character OS
  (execution).
- Behavior-layer policy templates keyed by
  `(app_slug, persona_id, modality)`.

---

## 7. Risks & honest tradeoffs (v3)

### 7.1 What could go wrong

- **Bundle complexity creep.** Three tiers × eventual seven apps
  × five capability axes = unwieldy. Mitigation: keep tiers ≤ 3
  per app, ship one app at a time as it unparks.
- **Building tiers for parked apps.** Premature scoping of
  mentorforge / pitchdeckforge / etc. before their intent is
  documented = wasted work + name-extrapolation risk. Mitigation:
  hard rule — no manifest entry for an app until its intent is
  documented from Chris.
- **Underpricing the render cost** (Phase 4+). Spokesperson render
  economics are materially different from LLM costs and vendor
  pricing can shift. Mitigation: separate meter, pricing reviews.
- **Brand-voice incident** (Phase 4+). Misconfigured allowlist or
  stale override → off-brand persona speaks for an app.
  Mitigation: audit log + kill-switch + warn-only before enforce.
- **Customer confusion at tier boundaries.** Same as v2. Mitigation:
  spokesperson video as visible Pro-tier upsell when Phase 4+
  activates; meanwhile lead with concrete outcomes per app.
- **Bundle becomes a moat against us.** White-label too early →
  customers see the bundle as the product. Mitigation: engine
  improvements continue, custom persona pipelines stay paid tier
  only.
- **Sibling apps stay parked indefinitely.** If Rigby Phase 1
  doesn't hit KPIs OR the next session's discovery doesn't
  produce real intent per app, the Phase 2-3 evolution stalls.
  Mitigation: discovery work is small, KPI gate is honest.

### 7.2 What we explicitly don't claim

- We don't claim the 7-app tiered Suite is shipping. Atlas says
  Phase 1 is Rigby standalone.
- We don't claim a marketplace where third-party developers add
  capabilities.
- We don't claim regulatory certifications (SOC 2, HIPAA, etc.).
  Capability bundle + audit log is the *foundation* for them.
- We don't claim "your data never leaves the platform" — LLM and
  render API calls go to third parties.
- We don't claim spokesperson personas are real people — every
  persona is clearly labeled as a synthesized brand voice (when
  Phase 4+ activates).

---

## 8. Why now (and why not yet)

### 8.1 Why now for Phase 1 (Rigby flagship)

- The engine works. The personal-AI-assistant value prop is
  validated by analogous products.
- Per Atlas, the only blockers are the 4 ✗ rows in
  `COST_SURVIVAL_AUDIT.md` — per-workspace cost attribution +
  daily caps + monitoring. Closing them is small, focused work.
- Operator Edge gives us a paid-conversion funnel.

### 8.2 Why not yet for Phase 2-3 (tiered Suite)

- Per Atlas, sibling apps are intentionally deferred until Rigby
  Phase 1 validates per-seat economics.
- Per Rigby's grounding pass, 5 of 7 sibling apps have no
  documented product intent — selling them now would be selling
  name-implied promises.
- The next session's app-by-app discovery work fills the gap;
  *then* Phase 2-3 becomes meaningful.

### 8.3 Why not yet for Phase 4+ (spokesperson)

- Per Atlas, Character OS / avatar is "parked until a paying
  customer demands it." Build-on-spec instead of build-on-demand
  burns runway with $50 OpenAI credits available.
- The capability bundle's spokesperson axis is recorded as a
  design (in the engineering spec). No implementation until the
  trigger fires.

---

## 9. Decision needed (v3)

Rigby's recommendation post-grounding: **(B-anchored) sequence
per Atlas — Rigby Phase 1 first, capability bundle Phase 0-2 for
the 2 active sibling apps, sibling apps unpark as their intent
gets documented, spokesperson activates at Phase 4+ trigger.**

The four-way fork from v2:

- **(A) Park the spec entirely.** Treat as a thinking artifact;
  return to it when a customer/partner directly demands per-app
  authz.
- **(B-anchored) Ship near-term scope only.** Phase 0-1 for
  signal-studio + contract-concierge after 1134 (Y); defer the
  rest. **My recommendation, mirroring Rigby's grounding.**
- **(C) Try to ship all 7 apps + spokesperson now.** Atlas says
  no. Rigby flagged this as name-extrapolation territory. Don't.
- **(D) Reshape further.** Tell me what's still off.

**If you go with (B-anchored)**, the *immediate* next move is not
this spec's Phase 0 — it's the **app-by-app discovery sprint** with
Rigby that Chris flagged for the next session. That work feeds
back into both specs' Phase 2-3+ triggers.

---

## 10. One-paragraph elevator pitch (re-anchored)

> "We're shipping a personal AI assistant — Rigby — at
> `app.247globalai.com` for $20-30/mo. It's the polished, one-
> product Phase 1 of a longer-term plan to build a Suite of
> domain-specific AI products for small-business operators (legal,
> sales, mentorship, dealflow). Each product gets its own
> capability bundle — a precise slice of the underlying engine
> tuned to the job. The eventual Suite layers in audit-ready
> security for regulated buyers, white-label customization for
> partners, and spokesperson-quality on-camera video for branded
> output. We're not selling the Suite today — we're selling Rigby
> first, validating per-seat economics, then unparking the Suite
> apps one at a time as customer demand and product intent
> justify. The engineering and the strategy are aligned: the
> bundle mechanism gets built incrementally, in step with the
> apps it scopes."
