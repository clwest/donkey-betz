---
title: "Spokesperson corpus + Character OS bridge — narrative (batch O)"
status: draft (batch O of Session 1158 corpus-narrative program; final entry)
last_updated: 2026-05-25
session: 1158
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1-LOCKED (Rigby, Session 1158)
companion_docs:
  - docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md
  - docs/narratives/FLEET_INTEGRATION.md
  - docs/narratives/STRATEGY_247_GLOBAL_AI.md
  - docs/PLATFORM_INVENTORY.md
provenance_confidence: MEDIUM (anchored to MEMORY.md feedback entries on avatar architecture; SESSION_1117 handoff; PR #2100 docs/spokesperson-corpus-pattern; MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md is parked design)
provenance_note: This is the most "vision-stage" of the 15 narratives. The spokesperson corpus + Character OS bridge exists as a working first-pass (Session 1117 shipped) plus parked architectural design. Strategic future via Atlas Phase 4+. Counts and details are sparser than other narratives because most of the work is queued, not shipped. Uncertainty labelled inline.
---

# Spokesperson corpus + Character OS bridge

> The vision: Rigby with a face. Locally-grounded
> spokesperson videos for personal / portfolio use — built
> on the fleet integration (M) and the 24/7 Global AI
> strategy (N). Session 1117 shipped the first pass
> (corpus + fleet-net + consult_engine bridge live).
> Character OS merge proposal is parked. Per Atlas v1,
> this is Phase 4+ work — unlocked when Phase 1 (Rigby
> standalone) has revenue.

---

## 1. What this is

The spokesperson corpus + Character OS bridge is the
platform's answer to "what if Rigby could appear as a
person?" — generated video of a consistent character,
grounded in the platform's actual corpus (not invented),
usable for personal portfolio and content distribution.

This narrative covers:

- **The Character OS repo** — a separate codebase
  (`~/development/character-os/`) for the spokesperson /
  avatar layer. Has an active Claude Code session per
  memory `project_character_os_active_cc.md`. Read-only
  from u-d-b sessions (don't interfere).
- **The spokesperson corpus pattern** — a corpus-of-self
  approach where the platform builds up an inventory of
  what it has shipped, said, and decided. The spokesperson
  uses this corpus as the truth-anchor for generated video.
  PR #2100 (`docs/spokesperson-corpus-pattern`) is the
  reference doc.
- **Session 1117 first-pass shipped** — corpus + fleet-net
  + consult_engine bridge end-to-end live. The fleet
  integration (narrative M) was the unlocking technical
  layer.
- **Avatar architecture trade-off** — conversational
  LLM-driven (Runway gwm1, can't be reliably steered) vs
  push-to-speak (HeyGen, D-ID, takes text + voice). Two
  fundamentally different product shapes; pick by use case.
- **Character OS merge proposal (parked)** —
  `docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`. The design
  for merging Character OS back into u-d-b. Sits in tree
  as a v2 unlock. Per Atlas v1: parked until Phase 1 has
  revenue.

The strategic positioning: per Atlas v1 (narrative N),
Character OS is **Phase 4+ work**. Phase 1 (Rigby
standalone, text-only, no avatar) ships first. Slice 3
(general-purpose video finishing layers) could ship
independently if Phase 1 has bandwidth — Atlas v1 says it
won't.

The operational positioning right now: **local-only
default.** Memory rule `feedback_local_only_default.md`:
don't drive prod verification, deploys, or Jessica
follow-ups; local-only is the mode unless Chris
explicitly flips the switch.

---

## 2. Core objects & vocabulary

| Term | Meaning |
|---|---|
| **Character OS** | The separate repo (`~/development/character-os/`) holding the spokesperson / avatar layer. NOT part of u-d-b. Has its own active Claude Code session per memory `project_character_os_active_cc.md`. |
| **Spokesperson corpus** | A corpus-of-self: an inventory of what the platform has shipped, said, decided. Used as truth-anchor for generated spokesperson video. Pattern doc: PR #2100 `docs/spokesperson-corpus-pattern`. |
| **consult_engine bridge** | The integration layer between u-d-b and Character OS. Lets Character OS query u-d-b for grounding data (corpus retrieval, recent ops facts, etc.). First pass shipped Session 1117. |
| **Atlas Phase 4+** | The Character OS unlock gate. Per `docs/24_7_GLOBAL_AI_APP_ATLAS.md` v1: Phase 4+ work is unlocked when Phase 1 (Rigby standalone) has revenue. Phase 4 is currently parked. |
| **`MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`** | The parked design for merging Character OS back into u-d-b. In tree. Architectural reference for the v2 unlock. |
| **Conversational LLM-driven avatar (Runway gwm1)** | One avatar architecture. The avatar service owns the LLM server-side; you can't reliably steer it via tool descriptions. Tool descriptions on Runway realtime avatars control WHEN tools fire but ignore narration instructions ("Before invoking, voice X"). Same class of bug as greeting bias. Don't embed narration cues — contract-test them as absent. Memory: `feedback_runway_tool_descriptions_gate_selection_not_narration.md`. |
| **Push-to-speak avatar (HeyGen, D-ID)** | The other architecture. Takes text + voice; you control what the avatar says. Picked when steerability matters more than visual conversational quality. |
| **Picking the architecture** | By use case, not by visual quality. Per memory `feedback_avatar_architecture_split.md`: conversational LLM-driven for "let the avatar improvise" use cases; push-to-speak for "the avatar must say exactly this" use cases. |
| **`docs/spokesperson-corpus-pattern`** | PR #2100 (open). Contains the spokesperson corpus pattern + 24/7 Global AI instance slice. Reference architecture. |
| **Local-only default (memory rule)** | `feedback_local_only_default.md`. Don't drive prod verification, deploys, or Jessica follow-ups. Local-only is the mode unless Chris flips the switch. Applies to Character OS bridge work too. |
| **"Connection work, not invention"** | Per memory `project_local_portfolio_rigby_grounding.md`. Network the laptop-local fleet (u-d-b, context-kit, Character OS, every app + its database), apply context-kit / spokesperson-corpus per app, aggregate into Character OS so a locally-grounded Rigby can generate spokesperson videos for personal / portfolio use without going public. |
| **Slice 3 — general-purpose video finishing** | Per Atlas v1: "the only piece that could ship independently — and only if Phase 1 has bandwidth left over (it won't)." The "Rigby gets a face" track has an internal slice that could be productized solo if Phase 1 frees up budget. |

---

## 3. Milestone timeline

| When | Change shipped | Why | Outcome | Status | Pointers |
|---|---|---|---|---|---|
| **Vision — Rigby with a face (Inferred, pre-Session 1117)** | The idea of generated spokesperson video for the platform: Rigby as a visible character. Initial work scoped through `MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md` (parked design). | The platform's value goes beyond text. A face increases distribution potential — content marketing, video portfolios, social. Plus the platform already has the AI backend (Rigby) to drive what the face says. | Architectural design exists in tree; conversation with Character OS as a separate repo begins. | **Parked** — the merge proposal sits in tree as v2 reference. | `docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md` |
| **Avatar architecture investigation — conversational vs push-to-speak** | Empirical finding: Runway gwm1 conversational LLM-driven avatars **can't be reliably steered via tool descriptions**. Tool descriptions gate WHEN tools fire but ignore narration instructions (e.g., "Before invoking, voice X"). Same class of bug as greeting bias. Don't embed narration cues — contract-test them as absent. **HeyGen and D-ID** are push-to-speak avatars — text + voice in, video out. Picked when steerability matters more than visual conversational quality. **Choice is by use case, not visual quality.** | The team learned (the hard way) that conversational LLM-driven avatars are not "controllable AI with a face" — they're "AI with a face that ignores your control inputs in the way LLMs typically do." Push-to-speak gives full control at the cost of conversation-fluency. | Two memory entries captured. Future decisions about avatar use are framed against use case (conversational vs steerability). | **Active rules-in-memory.** Both architectures still considered; pick depends on need. | Memory: `feedback_avatar_architecture_split.md`, `feedback_runway_tool_descriptions_gate_selection_not_narration.md` |
| **Session 1117 — first pass shipped (corpus + fleet-net + consult_engine bridge)** | Corpus + fleet-net + consult_engine bridge end-to-end live. The first proof case for "u-d-b is the brain bridge for a fleet of laptop-local apps" (cross-ref M milestone 1). Carryover items: seed u-d-b local DB, expand bridge tool catalogue, ingest other apps' corpora. | The vision needed a working first pass — not a full system, just proof that corpus + bridge + spokesperson layer could connect. Session 1117 was that proof. Critically: did NOT replace Phase 1 (Rigby standalone); proved the Phase 4+ unlock pattern. | First-pass infrastructure live. The bridge works. The corpus pattern is documented in PR #2100. Three carryover items queued. | **Active first pass.** Production-grade Character OS work is deferred per Atlas. | Memory: `project_local_portfolio_rigby_grounding.md`; `docs/handoffs/SESSION_1117_LOCAL_PORTFOLIO_GROUNDING_BRIDGE.md` |
| **PR #2100 — `docs/spokesperson-corpus-pattern` (open)** | Spokesperson corpus pattern documentation. 24/7 Global AI instance slice. Open PR. | The pattern of "corpus-of-self as truth-anchor for generated character output" needed a reference doc. PR #2100 is that doc. | Pattern documented; PR #2100 awaiting merge. | **Open PR.** Not yet merged. | https://github.com/clwest/donkey-betz-platform/pull/2100 (per memory) |
| **Session 1141 — Atlas v1 ratification confirmed Phase 4+ parking** | Chris's ratification of Jessica's 22 decisions (cross-ref N milestone 7) explicitly reaffirmed Atlas v1's Phase 4+ parking of Character OS. No accelerator triggered. | Phase 4+ work is gated on Phase 1 revenue. Without that, Character OS stays parked. Chris ratified the gate. | Character OS officially Phase 4+ work. Parked design + first-pass-shipped + queued for revenue trigger. | **Active strategy.** Parked. | Cross-ref `docs/narratives/STRATEGY_247_GLOBAL_AI.md` milestone 7 |
| **Steady-state — "Connection work, not invention" framing** | Per memory `project_local_portfolio_rigby_grounding.md`: networking the laptop-local fleet (u-d-b, context-kit, Character OS, every app + DB), applying context-kit / spokesperson-corpus per app, aggregating into Character OS for locally-grounded spokesperson videos. Personal / portfolio use; not public. Headline project for the next session Chris flags. | The work to do is **connection**, not new invention. The infrastructure exists (u-d-b agents + spider + corpus + RAG + fleet HMAC + Character OS first pass). Connecting them in a coherent way is what produces value. Avoids feature creep. | The framing is the active mode for any Character OS / spokesperson work. "Don't invent; connect." | **Active framing.** | Memory: `project_local_portfolio_rigby_grounding.md` |

---

## 4. What came of it

### Wins

- **First pass shipped.** Session 1117 proved the corpus
  + fleet-net + consult_engine bridge end-to-end. Not a
  demo — a working first pass.
- **Avatar architecture trap is documented.** Two memory
  rules capture the conversational-vs-push-to-speak
  split + the Runway tool-description bug class. Future
  decisions don't repeat the discovery cost.
- **Phase 4+ parking is explicit.** Atlas v1 + Chris's
  ratification mean Character OS work isn't speculative
  burn — it's a deliberate Phase 4+ that unlocks on
  Phase 1 revenue.
- **Connection-not-invention framing.** Memory captures
  the discipline that the right Character OS work is
  connecting existing primitives, not building new ones.
- **`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md` stays
  in tree.** Parked but available. When Phase 4+ fires,
  the architectural reference is there.
- **Spokesperson corpus pattern is documented.** PR #2100
  has the reference. Open — but the doc exists.
- **`feedback_local_only_default.md` enforces survival
  mode.** No production deploys of Character OS work
  while Phase 1 hasn't shipped. Aligns with cost
  discipline.

### Tradeoffs

- **Parked design risks staleness.**
  `MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md` is in tree but
  not actively maintained. The longer it sits, the more
  the rest of the platform evolves around it.
- **PR #2100 is open.** Not yet merged. The
  spokesperson corpus pattern doc is in branch limbo.
- **Conversational LLM-driven avatars don't steer
  reliably.** Real product constraint. Anyone planning
  a "Rigby has a face that responds to me" product has
  to either accept the loss of control or pick
  push-to-speak.
- **Character OS is a separate repo with its own active
  CC session.** Cross-repo work requires coordination
  to avoid stepping on the other agent's work
  (memory rule: read-only from u-d-b).
- **No revenue trigger means no acceleration.** Phase
  1 must succeed for Phase 4+ to be more than vision
  work. If Phase 1 stalls, Phase 4+ stays parked
  indefinitely.
- **Provenance confidence is MEDIUM, not HIGH.** This
  narrative covers more vision than shipped state. Most
  details trace to memory + parked docs, not runtime
  evidence. Treat the milestone timeline as "what we've
  told ourselves about this work" not "what's running
  in production."
- **Three carryover items from Session 1117** are
  queued but not yet checked off: seed u-d-b local DB,
  expand bridge tool catalogue, ingest other apps'
  corpora. No session-by-session tracking surfaced.

### Follow-on systems enabled

- **Fleet integration (M)** is the technical foundation.
  Character OS was the first multi-repo proof case;
  fleet HMAC + brain bridge are the connection layer.
- **24/7 Global AI strategy (N)** — Phase 4+ work is
  gated here. The strategic context for Character OS.
- **Knowledge + RAG + Memory (H)** — spokesperson
  corpus is a corpus-of-self pattern. The infrastructure
  (Document table, embeddings) is reusable.
- **PA (D)** — `consult_engine` bridge talks to PA's
  underlying capabilities (run_agent, search_docs,
  agent_introspection_tool).

---

## 5. Current state snapshot

> Source: Memory `project_local_portfolio_rigby_grounding.md`
> + Session 1117 handoff + `MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md` +
> Atlas v1 § 7 (Character OS parking) + memory
> `feedback_avatar_architecture_split.md` +
> `feedback_runway_tool_descriptions_gate_selection_not_narration.md`.

**Character OS repo.** `~/development/character-os/`. Has
its own active Claude Code session. Read-only from u-d-b
sessions (memory rule).

**Bridge components shipped.**
- Corpus (per Session 1117).
- fleet-net Docker network (cross-ref narrative M).
- consult_engine bridge.

**Carryover (queued).**
- Seed u-d-b local DB.
- Expand bridge tool catalogue.
- Ingest other apps' corpora.

**Avatar architectures.**
- **Runway gwm1** (conversational LLM-driven). Can't be
  reliably steered via tool descriptions. Tool descriptions
  gate WHEN tools fire; narration cues are ignored. Pick
  when conversational quality matters; accept loss of
  control.
- **HeyGen / D-ID** (push-to-speak). Takes text + voice;
  full steerability. Pick when control matters;
  conversational fluency is rougher.

**Phase positioning (Atlas v1).** Phase 4+. Unlocked when
Phase 1 (Rigby standalone) has revenue. Cross-ref
narrative N.

**Parked design.** `docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`
in tree. Not actively maintained; available for v2
reference.

**Open PR.** #2100 — `docs/spokesperson-corpus-pattern`.

**Framing.** "Connection work, not invention" per memory
`project_local_portfolio_rigby_grounding.md`. Local-only
default per `feedback_local_only_default.md`.

**Where to look when something stops working.**
- Character OS bridge call fails → check consult_engine
  endpoint; check `fleet-net` Docker network has both
  containers attached; check HMAC sign-key
  (cross-ref M § 5 footgun).
- Spokesperson corpus stale → regenerate per the
  pattern doc (PR #2100); ingest fresh ops facts via
  MemoryPromotionService logs.
- Avatar output ignoring narration cues → not a
  configuration problem; it's the architecture. Tool
  descriptions don't gate narration in Runway. Switch
  to push-to-speak for "must say exactly this" use
  cases.
- Carryover items (Session 1117) — DB seed, tool
  catalogue, app corpora ingestion — not tracked in any
  topic doc; status is whatever the Character OS active
  CC session reports.
- Phase 4+ gate fires accidentally — check Decision 1
  trigger (≥ 2 Suite products at ≥ $500 MRR each AND
  concrete Rigby answer); per Atlas v1, Phase 4+ work
  shouldn't start until Phase 1 has revenue.

---

## 6. Open questions / unknown outcomes

- **Three Session 1117 carryover items.** *Known:*
  named (seed u-d-b local DB, expand bridge tool
  catalogue, ingest other apps' corpora). *Unknown:*
  current status; whether any have been closed in
  parallel Character OS CC sessions.
- **PR #2100 merge status.** *Known:* open as of
  memory date. *Unknown:* current state.
- **Character OS repo composition.** *Known:* it
  exists; it has its own CC session. *Unknown:* what
  it actually contains in detail — read-only mode means
  we don't survey it from u-d-b sessions.
- **`MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md` freshness.**
  *Known:* it's in tree. *Unknown:* how stale it is
  vs current platform shape; how much would need
  updating before the v2 unlock could use it.
- **Avatar architecture choice for the production
  spokesperson.** *Known:* both architectures
  documented. *Unknown:* which (if either) is the
  Phase 4+ default. Probably a "decide when revenue
  triggers" question.
- **Slice 3 (general-purpose video finishing).**
  *Known:* Atlas v1 says it could ship independently.
  *Unknown:* whether any scoping has happened. Atlas
  says Phase 1 won't have bandwidth.
- **Personal vs public distinction.** *Known:*
  spokesperson is "personal / portfolio use" per
  memory. *Unknown:* whether there's a separate
  "public spokesperson" track or whether this stays
  private until Phase 4+ revenue.
- **Corpus-of-self schema.** *Known:* PR #2100 is the
  reference pattern doc. *Unknown:* the schema (fields,
  ingestion cadence, freshness rules). Not in
  PLATFORM_INVENTORY.
- **Character OS's relationship to context-kit.**
  *Known:* memory mentions both. *Inferred:* context-kit
  provides the orient/anchor pattern; Character OS uses
  the pattern. *Unknown:* whether Character OS
  consumes context-kit as a library, or just applies
  its design.

---

## 7. Source index

### Primary doc sources

- `docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md` —
  parked merge design.
- `docs/24_7_GLOBAL_AI_APP_ATLAS.md` § 7 — Phase 4+
  parking statement.
- `docs/narratives/FLEET_INTEGRATION.md` (M) — fleet
  technical foundation.
- `docs/narratives/STRATEGY_247_GLOBAL_AI.md` (N) —
  strategic Phase taxonomy.

### Named session handoffs cited above

- `docs/handoffs/SESSION_1117_LOCAL_PORTFOLIO_GROUNDING_BRIDGE.md`
  — first pass shipped.
- Atlas v1 Phase 4+ parking — Sessions 1116, 1141.

### Memory anchors

- `project_local_portfolio_rigby_grounding.md` —
  vision + first pass + carryover.
- `project_character_os_active_cc.md` — Character OS
  repo + active CC session (read-only).
- `feedback_avatar_architecture_split.md` —
  conversational vs push-to-speak rules.
- `feedback_runway_tool_descriptions_gate_selection_not_narration.md`
  — Runway tool description footgun.
- `feedback_local_only_default.md` — local-only mode.

### Open PR

- PR #2100 — `docs/spokesperson-corpus-pattern` (open).

### Code anchors

- `~/development/character-os/` — separate repo (do not
  edit from u-d-b sessions per memory rule).
- u-d-b side bridge code: TBD per Session 1117 PR /
  branch. Not enumerated in PLATFORM_INVENTORY runtime.

### Verification commands

- `python manage.py generate_platform_inventory` —
  inventory check (will not surface Character OS
  artifacts).
- `python manage.py verify_doc_claims --only-drift` —
  drift check.
- PA tool: `paid_interest_status` — Phase 1 demand-gate
  status (Decision 13).
- Atlas v1 read: `docs/24_7_GLOBAL_AI_APP_ATLAS.md` —
  strategic framing.
