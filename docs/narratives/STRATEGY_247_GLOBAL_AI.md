---
title: "24/7 Global AI — narrative (batch N)"
status: draft (batch N of Session 1158 corpus-narrative program)
last_updated: 2026-05-25
session: 1158
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1-LOCKED (Rigby, Session 1158)
companion_docs:
  - docs/24_7_GLOBAL_AI_APP_ATLAS.md
  - docs/narratives/FLEET_INTEGRATION.md
  - docs/narratives/PERSONAL_ASSISTANT.md
  - docs/PLATFORM_INVENTORY.md
provenance_confidence: HIGH (anchored to docs/24_7_GLOBAL_AI_APP_ATLAS.md v1, Jessica's Session 1137 ratification handoff, Chris's Session 1141 ratification handoff, MEMORY.md 247 global AI brand notes)
provenance_note: This narrative is the strategy-side companion to fleet integration (M). It covers the brand transition (Donkey Betz → 24/7 Global AI), the Suite of 4 + 3 Verticals + 5 Lab structure, the Phase 1 = Rigby standalone constraint, and the 22-decision ratification arc (Jessica Session 1137 → Chris Session 1141). Strategy moves faster than runtime; treat this as a snapshot.
---

# 24/7 Global AI strategy

> The brand + product taxonomy + pricing + GTM story for
> u-d-b's public face. Donkey Betz is the technical
> codebase; 24/7 Global AI is the brand it ships under.
> Phase 1 = Rigby standalone (the personal AI assistant);
> Phase 3+ = verticals; Phase 4+ = Character OS / video
> finishing. This narrative covers what got decided, by
> whom, when, and why.

---

## 1. What this is

24/7 Global AI is the brand the Donkey Betz codebase ships
under. The Atlas (`docs/24_7_GLOBAL_AI_APP_ATLAS.md`) defines:

- **The brand transition** — Donkey Betz (sports-betting wedge)
  → 24/7 Global AI (multi-agent intelligence platform).
- **The cut style** — soft cut. Monorepo stays. Shared core
  (Django + Postgres + Celery + spider runtime + agent
  registry). Each app gets its own front-end persona, route
  prefix, billing tier, and *can* later split to its own
  deploy without rewriting.
- **The Phase taxonomy** — Phase 1 = Rigby standalone; Phase
  2 = ?; Phase 3+ = verticals (Markets, Content, Studio,
  Legal); Phase 4+ = Character OS merge.
- **The Suite of 4** — PitchDeck, DealFlow, Contract
  Concierge, MentorForge (cross-ref narrative M — these are
  fleet apps).
- **The 3 Verticals + 5 Lab** structure underneath.
- **Pricing bands** — $20–30 / mo for Rigby standalone;
  Suite Pro / Team pricing per product.
- **Graduation rules** — Suite vs LAB at ≥ $1K MRR sustained
  ≥ 2 months.

The strategy was ratified across two sessions:

- **Session 1137 (Jessica)** — 22 decisions across 4 phases
  (pricing, GTM, cost attribution, legal demand-gate, etc.).
- **Session 1141 (Chris)** — 17 accept-as-written + 3
  ratify-shipped + 2 clarification redlines.

The Atlas's strategic shape (Rigby Phase 1 first, verticals
deferred, Character OS Phase 4+) is unchanged by those
decisions — they refine the *how* and *how much*, not the
*what*.

The most important fact: **the platform is in survival mode**.
Per memory `project_current_state_2026_04.md`: out of OpenAI
credits at one point; ~$50 credits available 2026-05-21;
stepping back from features. The Atlas's job is to produce
shippable income, not architecture-astronomy.

---

## 2. Core objects & vocabulary

| Term | Meaning |
|---|---|
| **Donkey Betz (the codebase)** | The Django monorepo. `/Users/donkeyking/development/unified-donkey-betz/`. The technical layer. Not the public brand. |
| **24/7 Global AI (the brand)** | The public-facing identity. Hosted at `247globalai.com`. Persona-resolved by subdomain or path prefix. Next.js + Vercel deploy. |
| **Atlas v1** | `docs/24_7_GLOBAL_AI_APP_ATLAS.md`. The strategy anchor. Session 1116 first draft; ratified Session 1137 (Jessica) + Session 1141 (Chris). |
| **Soft cut** | The architectural decision behind the Atlas. **One repo, one DB, one Redis, one Django, one frontend** with per-app personas. NOT separate repos or microservices. Allows per-app pricing / branding / scope without rewriting. |
| **Phase 1 — Rigby standalone** | The "ship one thing first" gate. Rigby as a $20-30/mo personal AI assistant. No avatar. No vertical add-ons. 101 tools (now 106). 80 spiders. 83 agents. Cross-ref narrative D. |
| **Phase 3+ — Verticals** | Markets, Content, Studio, Legal — already exist inside the platform as PA tools / agents. Stay reachable inside Rigby for power users. Don't get packaged as standalone paid products until after Phase 1 has paying customers. |
| **Phase 4+ — Character OS merge** | The "Rigby gets a face" track. Architectural design exists in `MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md` (parked). Unlocked when Phase 1 has revenue + customers ask for it. Slice 3 (general-purpose video finishing) could ship independently if Phase 1 bandwidth allows (per Atlas v1: it won't). |
| **The Suite of 4** | PitchDeck, DealFlow, Contract Concierge, MentorForge. Standalone sibling apps already exist outside the u-d-b repo (cross-ref fleet narrative M). Plug into 24/7 Global AI for some, stay independent for others. |
| **Suite vs LAB graduation** | Per Session 1137 Decision 4: graduate from LAB → Suite at ≥ $1K MRR sustained ≥ 2 months. Revenue-only criterion (not "we feel ready"). |
| **Take-public trigger** | Per Session 1137 Decision 1: defer Rigby launch until ≥ 2 Suite products at ≥ $500 MRR each AND concrete Rigby standalone answer. Practical effect: the public Rigby launch is gated on Suite traction, not on Rigby polish. |
| **24/7 Global AI trademark** | Per Session 1137 Decision 2: wait, same trigger as Decision 1. Don't file trademark until the launch trigger fires. |
| **Rigby pricing $30/mo** | Per Session 1137 Decision 5: top of the $20-30 Atlas band. |
| **Cost-attribution rules (Decision 9)** | Formal per-workspace + per-app cost-attribution rules supersede Atlas Phase 1's "~$1.50/day per-account cap" placeholder. Cost telemetry: `LLMCallLog.workspace` FK + `ExternalAPICallLog`. |
| **Stripe SKU wiring order (Decision 10)** | One-by-one: Signal Studio → SellerPilot → ComplianceSentinel. Not all at once. |
| **Signal Studio legal demand-gate (Decision 13)** | F1 spec shipped Session 1138. `FleetPaidInterest` model gates signal-studio access. Cross-ref narrative M. |
| **GTM channels per product (Decisions 15a-c)** | Per Session 1137; see handoff for full table. |
| **Persona slug** | An app's identifier in the soft-cut model. `flagship`, `markets`, `content`, `studio`, `legal`, etc. Routes to a frontend persona + PA tool allow-list + Stripe product + scoped workspace bootstrap. |
| **Two-thirds infrastructure** | Per Atlas: "two-thirds of the existing monolith is *not* customer-facing." Spider network, body systems, signal aggregation, advisor council, initiative pipeline, self-awareness — all infrastructure that powers the apps, not apps themselves. The Atlas separates the two cleanly. |
| **Cost survival audit** | `docs/COST_SURVIVAL_AUDIT.md` — companion doc. 4 ✗ rows in §A must be fixed before any external SaaS launch. Without per-workspace cost attribution, multi-tenant pricing is uninsurable. |

---

## 3. Milestone timeline

| When | Change shipped | Why | Outcome | Status | Pointers |
|---|---|---|---|---|---|
| **Foundation — Donkey Betz brand + sports-betting wedge** *(pre-Atlas, Inferred + Session 1116 first draft)* | The platform shipped as Donkey Betz with sports betting as the primary headline use case. The brand was the wedge; the codebase grew beyond sports betting (to content pipeline, intelligence desks, multi-agent debate, etc.) but kept the original name. | Sports betting was the first verifiable feedback loop (cross-ref narrative L) — the platform could prove out the multi-agent architecture against an objective ground truth (bets settled). The brand reflected the first wedge, not the full surface. | Donkey Betz brand in production. The codebase outgrew the brand without anyone formally noticing. | **Superseded by Atlas v1.** Donkey Betz is now the codebase name; 24/7 Global AI is the brand. | `docs/PLATFORM_WHAT_IT_IS.md` (renamed pre-Session-1146 reference); memory `project_247_global_ai_brand_locked.md` |
| **Session 1116 — Atlas v0 first draft** | Initial Atlas pass: "Donkey Betz → 24/7 Global AI; Suite of 4 + Verticals; soft cut; Phase 1 = Legal + Markets + flagship." Drafted by Claude Code. Outlined the cut style (soft cut, one repo); the apps under the brand; the strategy for pricing. | The platform's surface was too wide for one product. A brand + product taxonomy was needed before pricing and GTM could be decided. The Atlas was the framework. | First draft existed; "Phase 1 = Legal + Markets + flagship" framing established. | **Superseded by Atlas v1** which narrowed Phase 1 to Rigby standalone. | `docs/24_7_GLOBAL_AI_APP_ATLAS.md` (revision history) |
| **Session 1116→Atlas v1 — narrow Phase 1 to Rigby standalone** | Phase 1 narrowed from "Legal + Markets + flagship" to **Rigby standalone only**. Verticals deferred to Phase 3+. Character OS merge parked. Soft cut model formalized. Atlas v1 stamped as the strategy anchor. | "Ship one thing first" pressure. The original Phase 1 spanned three products; survival mode meant fragmentation would kill all of them. Narrowing to Rigby = "the personal AI assistant" gave the platform one ship-target with the existing 101+ tools / 80 spiders / 83 agents as the value prop. | Atlas v1 in tree. Strategic shape locked: Rigby Phase 1, verticals deferred, Character OS Phase 4+. | **Active strategy anchor.** | `docs/24_7_GLOBAL_AI_APP_ATLAS.md` v1 header; memory `project_current_state_2026_04.md` |
| **Session 1117 — Local portfolio Rigby grounding (the fleet vision)** *(Cross-ref M)* | The framing of "Rigby is the brain bridge for a fleet of laptop-local apps" was floated. Corpus + fleet-net + consult_engine bridge first pass shipped end-to-end. The Suite of 4 + 3 Verticals + 5 Lab structure later defined in the Atlas was operationalized here. | The Atlas needed a technical layer. Fleet integration (narrative M) is that layer. Session 1117 was the proof case: u-d-b is the brain, the fleet apps are the verticals. | First fleet proof case shipped. The Atlas's "soft cut" model now has a working technical pattern. | **Active.** Cross-ref narrative M. | Memory `project_local_portfolio_rigby_grounding.md`; cross-ref `docs/narratives/FLEET_INTEGRATION.md` milestone 1 |
| **Session 1137 — Jessica's 22-decision ratification** | Jessica ratified 22 decisions across 4 phases. Pricing per app (Decisions 5–8: Rigby $30/mo top of band; Suite Pro/Team for SS/SP/CS). Cost-attribution rules (Decision 9 supersedes Atlas's "~$1.50/day per-account cap" placeholder). Take-public trigger (Decision 1: ≥ 2 Suite products at ≥ $500 MRR each AND concrete Rigby answer). Trademark wait (Decision 2: same trigger). Suite-vs-LAB graduation (Decision 4: ≥ $1K MRR sustained ≥ 2 months). Stripe SKU wiring order (Decision 10: Signal Studio → SellerPilot → ComplianceSentinel). F1 demand-gate (Decision 13: spec shipped Session 1138). GTM channels per product (Decisions 15a-c). | The Atlas was a strategic shape; Jessica was needed to put numbers and triggers on it. 22 decisions covered pricing, GTM, cost, legal, graduation, persona naming. The output ratified Atlas's *what* and refined the *how / how much*. | All 22 decisions are now part of the canonical strategy. Full text in `SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md`. | **Active strategy.** Some shipped (Decision 13 → F1 demand-gate); some carryover (Decision 10 → Stripe wiring queued). | `docs/handoffs/SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md`; Atlas v1 header preamble |
| **Session 1138 — F1 paid-interest demand-gate** *(Cross-ref M)* | F1 spec from Decision 13 shipped. `FleetPaidInterest` model + HMAC POST endpoint + `paid_interest_status` PA tool. Signal-studio gated on demand. First production-running piece of the Atlas's vertical-specific demand gating. | The Atlas required demand-gated access for new verticals (a hedge against shipping un-validated). F1 made the gate concrete and proved the pattern. | Demand-gate live for signal-studio. Pattern reusable for SS / SP / CS Stripe wiring. | **Active.** | Cross-ref `docs/narratives/FLEET_INTEGRATION.md` milestone 8; memory entry on Session 1138 |
| **Session 1140 — judge-stats + action-card pre-gen + pgvector blocker closed** | `judge-stats` endpoint + `signal_studio_judge_stats` PA tool. Action-card pre-generation vertical slice (3 PRs). pgvector blocker closed via #2172. signal-studio entity-token clusterer behind `cluster_method` discriminator. | The vertical slice for signal-studio (Decision 13's underlying product) needed real production traffic. Judge stats + action cards made the vertical genuinely useful, not just a demo. | Signal-studio has working vertical features. The Suite of 4 has its first complete product surface. | **Active.** | `00-START-NEXT-SESSION.md` recent arc references |
| **Session 1141 — Chris's ratification** | Chris ratified Jessica's 22 decisions: 17 accept-as-written + 3 ratify-shipped + 2 with Jessica clarification redlines (queued back to Jessica). F5 PitchDeckForge style audit found Angel + Strategic don't map to existing code templates — surfaced as a gap. | The decisions needed Chris's sign-off before being load-bearing. The 17 accept-as-written makes 17 decisions immediately actionable; the 3 ratify-shipped acknowledges work that already happened; the 2 clarifications go back to Jessica. F5 audit finding becomes a queued follow-up. | Strategy ratified. Atlas v1 + Jessica's 22 decisions are the canonical strategic frame. | **Active strategy.** Two clarifications queued. F5 PitchDeckForge gap queued. | `docs/handoffs/SESSION_1141_JESSICA_RATIFICATION_DEEP_DIVES.md`; Atlas v1 header preamble |

---

## 4. What came of it

### Wins

- **Brand matches reality.** Donkey Betz outgrew its
  sports-betting wedge years ago; 24/7 Global AI
  describes the actual platform.
- **Soft cut model is technically operational.** One
  repo, one DB, per-app personas. Adding a vertical is
  a frontend persona + PA tool allow-list + Stripe
  product + workspace bootstrap. No rewrites.
- **Phase 1 = Rigby standalone is the right gate.**
  Survival mode demands one shippable product. Rigby
  exists; 106 tools work; the cost story is the
  remaining blocker, not the capability.
- **22 ratified decisions are durable.** The Atlas's
  *what* + Jessica's *how/how much* + Chris's
  ratification + memory captures = the strategy isn't
  going to drift in the next round of pressure.
- **F1 demand-gate is the first vertical-gated
  feature.** Decision 13 shipped. The pattern is
  reusable for the Stripe SKU wiring order (Decision
  10: SS → SP → CS).
- **Two-thirds infrastructure framing.** The Atlas
  cleanly separates "customer-facing apps" from
  "infrastructure that powers them." The agent
  narrative (A), signal narrative (C), PA narrative
  (D), etc. all cover the infrastructure half; the
  Suite + Verticals + Lab cover the apps half. Both
  halves are honest about which they are.
- **Survival-mode framing.** The Atlas + COST_SURVIVAL_AUDIT
  acknowledge the cost ceiling. Decisions like
  "Stripe SKU wiring 1-by-1" reflect the constraint,
  not aspirational scaling.

### Tradeoffs

- **Phase 1 launch is gated on Suite traction**
  (Decision 1: ≥ 2 Suite products at ≥ $500 MRR
  each). Rigby could be production-ready and still
  deferred if Suite revenue isn't there.
- **Trademark wait** is a similar gate — the brand is
  used internally but not legally protected until
  Decision 1 fires.
- **4 ✗ rows in COST_SURVIVAL_AUDIT §A must be fixed
  before external SaaS launch.** Per-workspace cost
  attribution isn't done; without it, multi-tenant
  pricing is uninsurable.
- **F5 PitchDeckForge gap.** Session 1141 audit found
  Angel + Strategic don't map to existing code
  templates. Open question.
- **Two clarification redlines pending back to
  Jessica.** Until those return, the corresponding
  decisions are not fully ratified.
- **Atlas counts in narrative are not in
  PLATFORM_INVENTORY.** Phase definitions, pricing
  bands, graduation rules are strategy-narrative;
  PLATFORM_INVENTORY only covers runtime. The strategy
  doc has to be hand-updated; it doesn't regenerate.
- **Soft cut model assumes URL routing by subdomain
  or path prefix.** `app.247globalai.com/{flagship,
  markets,content,studio,legal,...}` — the
  Next.js + Vercel deploy needs subdomain routing or
  rewrite rules. Not yet exercised at scale.
- **Local-only default holds (per memory).** Production
  deployment of the fleet apps isn't underway. Atlas
  Phase 1 launch is queued; production-deploy work is
  queued.

### Follow-on systems enabled

- **Fleet integration (M)** is the technical layer
  beneath the Atlas's Suite + Verticals taxonomy.
- **PA (D)** — Rigby is the Phase 1 product itself.
  Every PA capability is what Phase 1 sells.
- **Knowledge + RAG + Memory (H)** — Atlas's
  "two-thirds infrastructure" includes the knowledge
  pipeline; it's behind every app.
- **Decision Command (J)** — `publish_intent` enum,
  governance gates, the canary path all support Atlas
  decisions like demand-gated launches.
- **Sports + Monetization + ML (L)** — sports is one
  of the Verticals in the Atlas; monetization
  (Gumroad, Discord roles) is the existing
  monetization layer before Stripe SKU wiring lands.
- **Spokesperson corpus + Character OS (O)** is Phase
  4+ work — unlocked when Phase 1 has revenue.

---

## 5. Current state snapshot

> Source: `docs/24_7_GLOBAL_AI_APP_ATLAS.md` v1 +
> Session 1137 + 1141 ratification handoffs +
> MEMORY.md `project_247_global_ai_brand_locked.md`.

**Brand.** 24/7 Global AI (public). Donkey Betz (codebase).

**Phase taxonomy.**
- **Phase 1.** Rigby standalone — $30/mo personal AI
  assistant. No avatar, no vertical add-ons. 106 PA
  tools, 80 spiders, 83 agents.
- **Phase 2.** Not formally enumerated; implicit between
  Rigby launch and vertical packaging.
- **Phase 3+.** Verticals (Markets, Content, Studio,
  Legal) packaged as standalone paid products.
- **Phase 4+.** Character OS merge (Rigby gets a face).

**Suite of 4.**
- PitchDeckForge
- DealFlow
- Contract Concierge
- MentorForge

(Cross-ref narrative M — these are fleet apps; soft-cut
technical model.)

**Cut style.** Soft cut. Monorepo. One DB, one Redis,
one Django, one frontend with per-app personas. Each app:
persona slug + frontend persona + PA tool allow-list +
billing product + scoped workspace bootstrap.

**22 ratified decisions (Session 1137 + 1141).**
Pricing per app (Rigby $30/mo; Suite Pro/Team for SS/SP/CS),
cost-attribution rules, take-public trigger (Decision 1),
trademark wait (Decision 2), Suite-vs-LAB graduation
(Decision 4 at ≥ $1K MRR sustained ≥ 2 months), Stripe SKU
wiring order (Decision 10: SS → SP → CS), F1 demand-gate
(Decision 13 shipped), GTM channels per product (Decisions
15a-c).

**Atlas-relevant decision triggers.**
- Decision 1 (take-public): ≥ 2 Suite products at ≥ $500
  MRR each AND concrete Rigby standalone answer.
- Decision 4 (Suite vs LAB graduation): revenue-only,
  ≥ $1K MRR sustained ≥ 2 months.
- Decision 13 (F1): shipped Session 1138.

**Cost survival.** Per `COST_SURVIVAL_AUDIT.md`: 4 ✗
rows in §A must be fixed before external SaaS launch
(per-workspace cost attribution is the headline).
Cost budget $1,500/month (cross-ref narrative E).

**Frontend home.** Next.js + Vercel deploy at
`247globalai.com`. (Live per memory
`project_247_global_ai_brand_locked.md`.)

**Where to look when something stops working.**
- "Are we ready to launch?" → check Decision 1 trigger
  (≥ 2 Suite products at ≥ $500 MRR each + concrete
  Rigby answer). Atlas v1 + Sessions 1137/1141 ratify.
- "What price should X be?" → Atlas Decisions 5–8 cover
  Rigby + SS / SP / CS. Other apps: Atlas + Jessica's
  ratification handoff.
- "Should I ship feature Y to Phase 1 or Phase 3+?" →
  Atlas v1 Phase taxonomy. Rigby standalone (Phase 1)
  is text-only, no avatar, no vertical add-ons; if Y
  touches verticals or avatars, it's Phase 3+ or
  Phase 4+.
- F5 PitchDeckForge style audit gap (Angel +
  Strategic don't map to code templates) → Session
  1141 ratification handoff; open question.
- "Where's the trademark?" → Decision 2: wait until
  Decision 1 trigger fires.
- New vertical demand-gate → reuse F1 pattern
  (`FleetPaidInterest`, narrative M).

---

## 6. Open questions / unknown outcomes

- **Phase 2 definition.** *Known:* Phase 1 = Rigby
  standalone; Phase 3+ = verticals. *Unknown:* what
  Phase 2 is. The Atlas mentions Phase 1 and Phase 3+
  but no Phase 2 details surfaced.
- **F5 PitchDeckForge style audit findings.**
  *Known:* Angel + Strategic don't map to existing
  code templates (Session 1141). *Unknown:* what to
  do — add code templates? change product framing?
- **Two clarification redlines back to Jessica.**
  *Known:* 2 of 22 decisions have Chris clarification
  redlines pending. *Unknown:* current status; resolved
  or pending.
- **Decision 1 trigger status.** *Known:* require ≥ 2
  Suite products at ≥ $500 MRR each + concrete Rigby
  standalone answer. *Unknown:* current Suite revenue;
  whether the trigger is close to firing.
- **COST_SURVIVAL_AUDIT §A fix status.** *Known:* 4
  ✗ rows must be fixed before external SaaS launch.
  *Unknown:* which of the 4 have been closed.
- **Decision 10 Stripe SKU wiring progress.**
  *Known:* SS → SP → CS order. *Unknown:* current
  step.
- **Suite of 4 vs 3 Verticals + 5 Lab.** *Known:* both
  framings exist in MEMORY.md. *Unknown:* whether
  these are different decompositions of the same apps,
  or whether they enumerate different sets.
- **Phase 1 launch readiness.** *Known:* Rigby
  exists; cost story is the blocker. *Unknown:* what
  specific cost-attribution work remains; what the
  cost-attribution shipping target is.
- **u-d-b inclusion in public taxonomy.** *Known:*
  u-d-b is "the engine that powers the public Suite,"
  not a public product itself. *Unknown:* whether
  this stays the case post-launch or whether u-d-b
  itself becomes a public surface for power users.

---

## 7. Source index

### Primary doc sources

- `docs/24_7_GLOBAL_AI_APP_ATLAS.md` — v1 strategy
  anchor.
- `docs/COST_SURVIVAL_AUDIT.md` — companion cost
  reality check.
- `docs/CONNECTION_CENSUS_2026_05.md` — companion
  connection-census doc.
- `docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md` —
  parked Character OS merge proposal.
- `docs/handoffs/SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md`
  — Jessica's 22 decisions.
- `docs/handoffs/SESSION_1141_JESSICA_RATIFICATION_DEEP_DIVES.md`
  — Chris's 17+3+2 ratification.
- `docs/PLATFORM_WHAT_IT_IS.md` — narrative anchor
  (companion).
- `docs/PLATFORM_INVENTORY.md` — runtime inventory.

### Named session handoffs cited above

- Session 1116 — Atlas v0 first draft.
- Atlas v1 narrowing — Phase 1 = Rigby standalone.
- Session 1117 — local-portfolio Rigby grounding
  (cross-ref M).
- Session 1137 — Jessica's 22 decisions.
- Session 1138 — F1 demand-gate (cross-ref M).
- Session 1140 — judge-stats + action-card vertical
  slice + pgvector blocker closed.
- Session 1141 — Chris's ratification.

### Memory anchors

- `project_247_global_ai_brand_locked.md` — brand +
  Suite + Verticals + Lab live.
- `project_current_state_2026_04.md` — survival mode +
  ~$50 credits available.
- `project_local_portfolio_rigby_grounding.md` —
  fleet vision.

### Code anchors

- `core.models` — `FleetPaidInterest` (F1 demand-gate).
- `core/services/pa_tool_schemas.py` —
  `paid_interest_status` PA tool.
- `frontend/` (Next.js + Vercel) — 24/7 Global AI
  public site.

### Verification commands

- `python manage.py generate_platform_inventory` —
  runtime inventory.
- `python manage.py verify_doc_claims --only-drift` —
  drift check.
- PA tool: `paid_interest_status` — F1 gate status.
