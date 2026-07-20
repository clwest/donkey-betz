# S2841 D0–D6 Pressure-Test Addendum — Canonical Companion

**Session:** S2842 (opened 2026-07-19; addendum authored + ratified in-session)
**Parent doc:** [`S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`](S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md)
**Author:** Claude Code + Rigby (independent pressure-test); Chris ratification (D0–D6)
**Git HEAD at authoring:** `3b5d9a489`
**Playbook version:** v0.8.0 (205 rules; unchanged this session)
**Status:** **RATIFIED (Chris D0–D6, S2842)**
**Ratification envelope:** twin-mirrored to Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` by Rigby
**Scope:** Companion document to the S2841 discovery — captures Chris + ChatGPT independent re-evaluation, adopted evaluation dimensions, Foundry evidence investigation, and D0–D6 verdicts

---

## 0. Why this addendum exists

Chris passed the S2841 discovery + 9-opportunity portfolio to ChatGPT for independent CTO-lens investment-committee review. ChatGPT + Chris independently re-scored each opportunity and flagged **two evaluation dimensions that neither Claude nor Rigby had used** in the original discovery: Self-Acceleration and Compound Advantage. Chris also surfaced a structural hypothesis — that the 9 opportunities may not be 9 separate companies but layers of one ecosystem — and provided critical context that reframed OPP-7 (Cross-App Fleet) from "manage 8 apps" to "application foundry that lowers marginal cost of App #9."

Before issuing D-verdicts, Chris commissioned Claude and Rigby to independently re-score the portfolio using the new dimensions, investigate whether the "8 apps already exist" claim held under evidence, and pressure-test the layered restructuring hypothesis.

This addendum captures that pressure-test cycle end-to-end. It is a **canonical companion** to S2841 — the discovery doc names *what was found*; this addendum names *what survived Chris + ChatGPT + Rigby's second-order review*.

---

## 1. New evaluation dimensions (ADOPTED per D2)

Chris ratified these as durable evaluation criteria for future strategic opportunities:

### 1.1 Self-Acceleration (SA)

> **How much of building THIS business can Donkey Betz itself automate?**

Evaluate across: research, documentation, engineering, marketing, SEO, sales collateral, customer onboarding, proposals, legal drafts, competitive analysis, QA, release notes, operations.

- **1–3:** Business is dominantly human-executed; DBZ can automate <30% of the build.
- **4–6:** Substantial DBZ automation possible (30–70%), but critical path work requires humans.
- **7–8:** DBZ automates most artifacts + operations (70–90%); humans focus on judgment/relationships.
- **9–10:** Foundry-level: DBZ builds it substantially by itself; humans provide direction, not labor.

### 1.2 Compound Advantage (CA)

> **If this business succeeds, does Donkey Betz itself become better?**

Evaluate across: new Playbook rules, better ratifications, improved RAG, reusable templates, stronger methodology, hardened primitives, product-tested audit substrate, richer capability graph, external validation.

- **1–3:** Business is a revenue stream but doesn't feed the platform.
- **4–6:** Modest improvements flow back — one or two primitives get better.
- **7–8:** Strong compounding — every customer materially improves platform capability.
- **9–10:** Structural flywheel — the business's growth *is* the platform's growth.

### 1.3 Composition with existing evaluation criteria

SA + CA are **additive**, not replacement, for the existing S2841 §6 rubric (buyer / pain / promise / capabilities used / foundation / missing / time-to-outcome / time-to-revenue / distribution / differentiation / defensibility / effort / dependency risk / market risk / operator dependence / confidence / why hiding / falsify).

Total per-opportunity fields under the codified framework: **20 fields (18 original + SA + CA)**.

---

## 2. Independent re-scoring — side-by-side

Both Claude (Code) and Rigby (via PA tool_runs, `deliverable_tool.detail` + `fleet_health` for evidence grounding) independently re-scored each opportunity. Neither saw the other's scores before publication.

| OPP | Claude SA | Rigby SA | Δ | Claude CA | Rigby CA | Δ |
|---|---:|---:|---:|---:|---:|---:|
| OPP-1 Rigby standalone | 8 | 7 | -1 | 8 | 8 | 0 |
| OPP-2 Governance Consulting | 6 | **8** | **+2** | 10 | 9 | -1 |
| OPP-3 AI Work Ledger | 7 | 6 | -1 | 9 | **10** | +1 |
| OPP-4 Employee OS OSS + SaaS | 8 | 7 | -1 | 9 | 9 | 0 |
| OPP-5 Discord AI Teammate | 8 | **6** | **-2** | 6 | 6 | 0 |
| OPP-6 CO Family Law | 5 | 5 | 0 | 4 | 6 | +2 |
| **OPP-7 Foundry (reframed)** | **10** | **6** | **-4** | **10** | **8** | **-2** |
| OPP-8 AI-Employee-as-a-Service | 7 | 7 | 0 | 8 | 7 | -1 |
| OPP-9 Newsletter | 9 | 8 | -1 | 5 | 6 | +1 |

### 2.1 Rigby's SA+CA weighted top-4

**OPP-3, OPP-2, OPP-4, OPP-1** (order depends on time horizon).

### 2.2 Claude's SA+CA weighted top-tier

Foundry + Governance Consulting extracted from ranking as layer-2 / flywheel; remaining application-layer top-3: **OPP-4, OPP-3, OPP-1**. Substantial overlap with Rigby.

### 2.3 Agreements (strong signal)

- Both moved Q1 rankings the same direction: OPP-2 + OPP-4 rise; OPP-6 falls; OPP-9 stays lower-tier.
- Both answered Q2 (does OPP-7 change with foundry context) YES.
- Both answered Q3 (should portfolio reorganize as layers) YES with the same caveat.
- Both zoom-out folds converged on the same anti-pattern: **layered architecture can become a permission slip to never pick a wedge / governance-as-avoidance.**

---

## 3. Material disagreements + resolution

### 3.1 OPP-7 Foundry — Rigby's evidence-grounded 6/8 beat Claude's ungrounded 10/10

Claude scored OPP-7 as 10/10 on the foundry reframing after accepting Chris's framing that "the 8 apps already exist." Rigby scored 6/8 because she ran `fleet_health(include_healthy=true)` and got hard evidence: **7/7 sibling apps UNREACHABLE** (connection refused on localhost:8002-8008). Her framing was more honest: *"CA rises to ~8 under Foundry framing, but execution readiness looks low unless/until 'apps are reachable + shared auth + shared billing/cost attribution' is real."*

**Resolution:** neither score survived the subsequent /development/ investigation (§4 below). Corrected scoring in §6.

**Lesson codified:** Score accepted framings only after grounding in tool evidence. Rigby's fleet_health tool-run corrected Claude's ungrounded acceptance. This is `feedback_verify_rigby_tool_runs_before_trusting_sign` operating in reverse — Rigby's grounding caught Claude's ungrounded score.

### 3.2 OPP-2 Governance Consulting SA — Rigby's 8 beat Claude's 6

Claude fixated on "Chris's hours are the deliverable — cannot yet auto-run engagements." Rigby credited the artifact factory: diagnostics, templates, reports, and client deliverables can be auto-produced at ~80%; Chris-time is a relationship/trust bottleneck, not an artifact bottleneck.

**Resolution:** Rigby's framing is closer to actual delivery reality. Consulting-as-artifact-production is DBZ-native.

### 3.3 OPP-5 Discord SA — Rigby's 6 beat Claude's 8

Claude assumed multi-tenant Discord + billing = shippable. Rigby added: "growth/distribution + multi-guild permissions are not self-built." Distribution is not free.

**Resolution:** Rigby's 6 is the honest score. Claude priced distribution as free.

### 3.4 OPP-6 CO Family Law CA — Rigby's 6 vs Claude's 4

Modest disagreement. Rigby saw legal-pipeline/spider improvements as spilling over to the platform; Claude saw the CO domain as too narrow to compound broadly. Both defensible; keeping both scores in the record.

---

## 4. Foundry evidence investigation (`/Users/donkeyking/development/`)

Chris directed Claude to look around `/development/` because the fleet_health probe only tested "running on localhost right now," not "code exists / is real / is inheritable." This investigation is the load-bearing evidence for D3 (Foundry status revision).

### 4.1 Directory census — 9 sibling directories exist

| App | LOC | Commits | Last touched | Branch |
|---|---:|---:|---|---|
| character-os | **167,574** | 468 | 2026-05-26 | feat/doc-claim-verifier |
| signal-studio | 7,489 | 37 | 2026-05-24 | main |
| contract-concierge | 6,482 | 32 | 2026-05-22 | main |
| mentorforge | 5,286 | 37 | 2026-05-23 | main |
| pitchdeckforge | 4,663 | 43 | 2026-05-22 | feat/session-1133-fleet-pa-signing |
| dealflowtracker | 3,915 | 25 | 2026-05-23 | feat/session-1133-fleet-pa-signing |
| compliancesentinel | 3,449 | 18 | 2026-05-23 | feat/session-1133-fleet-pa-signing |
| sellerpilot | 3,279 | 18 | 2026-05-23 | feat/session-1133-fleet-pa-signing |
| focus-flow | 722 | 1 | 2026-04-13 | main (dead scaffold) |

**Total: 202,859 LOC across 9 sibling directories, all last touched between April and May 2026 (~1,700 DBZ sessions ago).** These are not scratch scaffolds — they are production-shape repositories.

### 4.2 Pattern A — Fleet foundry (7 apps sharing brain_client)

Every one of the 7 fleet apps (mentorforge / contract-concierge / pitchdeckforge / sellerpilot / dealflowtracker / signal-studio / compliancesentinel) has structurally identical scaffolding:

**Top-level:**
- `CLAUDE.md` + `00-START-NEXT-SESSION.md` (context-kit pattern inherited)
- `backend/app/` (FastAPI + SQLAlchemy + Pydantic — NOT Django)
- `frontend/`, `docker-compose.yml`, `render.yaml`, `start.sh`

**Every backend contains the same 5 shared files:** `auth.py`, `brain_client.py`, `models.py`, `stripe_billing.py`, `fleet_signer.py`.

**`brain_client.py` docstring (verbatim from mentorforge, byte-identical across all 7):**

> "The PA (Rigby) is the 'brain' for the fleet; this client lets this app ask Rigby a question and wait for a deliberated answer... Everything else must stay byte-identical across the 7 fleet repos so that the next round (Phase 2C) can pull this file into a shared package without per-repo divergence patches."

**DBZ side is fully wired to receive them:**

- **13 `fleet_*.py` services** in `core/services/`: `fleet_routing.py`, `fleet_auth.py`, `fleet_auth_drf.py`, `fleet_routing_dispatch.py`, `fleet_signals.py`, `fleet_events.py`, `fleet_provisioning.py`, `fleet_pa_chat_audit.py`, `fleet_rotation.py`, `fleet_paid_interest.py`, `fleet_signer.py`, `fleet_event_cleanup.py`, `fleet_artifact_cleanup.py`, `fleet_health_rollup.py`
- **`config/fleet_agent_routing.json`** — all 7 apps registered with `defaults` + `allowlists` + `roles` + `force_allowed`
- **Cross-app auth via `X-Fleet-*` signature headers** — Move 1 of the fleet routing arc, bidirectional signing (fleet_signer.py on both sides)

**Completion state:** Session 1128 Phase 2B (contract additions back-propagated from contract-concierge) shipped. Phase 2C (extract `brain_client.py` into shared package, resolve 5 stale feature branches, verify fleet auth-signing E2E) never completed. Estimate to revive: **~2–3 weeks of engineering** to bring the fleet from "built but dormant" to "runnable and shareable."

**Why fleet_health said 7/7 UNREACHABLE:** nobody's running the containers. Code exists, config exists, auth protocol exists, billing wiring exists — the fleet is dormant, not absent.

### 4.3 Pattern B — Product-family foundry (character-os + reserved `*OS` slots)

**Character OS is a Live, Phase 4-complete SaaS product** — separate from the 7-app fleet, under a different pattern:

- **Product:** *"Persistent AI spokespeople — small businesses create reusable on-camera identities (powered by Runway's avatar API) that star across video ads, conversational sessions, and finishing-layer composites."*
- **Stack:** Django DRF shell + FastAPI media engine + React/Vite SPA + Celery + Redis + Postgres/pgvector
- **Scale:** 167K LOC, 468 commits, 8 Django apps, ~16 models, 80+ `/api/*` routes, 25 `/internal/*` media-engine routes
- **Feature-complete arcs:** 4-step create-spokesperson wizard (SESSION 132), knowledge arc K1-K9, video composition V0-V15, realtime WebRTC R1-R5
- **Billing:** own `shell/apps/billing/` Django app with tier-based billing model already migrated
- **Current state:** 1-developer / 0-customer — pre-revenue but launch-ready

**24/7 Global AI parent brand codified** in `docs/247_GLOBAL_AI_OVERVIEW.md`:

| Product | Status |
|---|---|
| CharacterOS | **Live (Phase 4 complete)** |
| DealerOS | Reserved |
| AgentOS | Reserved |
| OpsOS | Reserved |
| VoiceOS | Reserved |
| SupportOS | Reserved |

Positioning: *"24/7 GLOBAL AI is a premium enterprise AI infrastructure company. Each `*OS` is a focused vertical with shared design, shared identity, and shared operational principles."* Tagline: **"ALWAYS ON. ALWAYS SMART. ALWAYS GLOBAL."**

**This is the same 24/7 Global AI brand Atlas v1 proposed rebranding DBZ into (May 2026).** The brand didn't die — it moved. Character OS ships under it as the flagship; the 6 reserved slots are the productization of the layered architecture.

**Character OS is actively integrating with DBZ right now.** Recent character-os commits:

```
21f359c  feat: doc-claim verifier + 3 seed claims + CI gate
92455f1  chore: SESSION 216 close — inventory regen
0dd9c14  docs(realtime): SESSION 216 reframe — bridge tools are product pattern, not dogfood
9cf6896  docs: cross-CC handoff card for Rigby F2F on u-d-b
00c2586  docs: SESSION 215 close — bridge tools soft-deprecated, Rigby F2F → u-d-b
e8c3589  feat(realtime): consult_engine bridge tool + u-d-b spokesperson corpus ingest
```

Character OS calls DBZ Rigby via `shell/apps/realtime/tools/consult_engine.py` as an in-product knowledge/consultation engine. Session 216 soft-deprecated the bridge tools in favor of Rigby F2F on u-d-b, and imported DBZ's `doc_claim_verifier` pattern (which is why the branch is `feat/doc-claim-verifier`).

Character OS README (§Provenance): *"`unified-donkey-betz` is a **donor** repo for selective agent + embedding + memory module ports. Not merged in bulk."* Character OS treats DBZ as a methodology + component donor, not a runtime dependency.

### 4.4 Summary — foundry evidence

The "foundry" claim resolves into **two separate patterns**:

- **Pattern A (Fleet foundry):** built ~Session 1128 Phase 2B → dormant since. ~2–3 weeks from re-runnable.
- **Pattern B (Product-family foundry):** actively producing Live products (CharacterOS Phase 4 complete); DBZ integration seam currently being iterated in parallel character-os sessions.

The "why haven't we executed what we already decided?" question has a partial answer that neither S2841 nor Rigby had surfaced: **Chris HAS been executing — but in Character OS, not DBZ.** The 214+ character-os sessions parallel the ~1,700 DBZ sessions. From DBZ's perspective it looks like nothing shipped; from the whole-ecosystem perspective a Live product exists under the intended 24/7 Global AI brand.

---

## 5. Layered architecture (ADOPTED per D1)

Chris ratified the reframing of Donkey Betz as three layers plus a commercialization flywheel:

### 5.1 Layer 1 — Operating System

**Substrate primitives that produce audit-graded artifacts:**
- Rigby (PA gateway; 113 tool schemas + 156 handlers + 8 enrichment services)
- Employee OS (AIEmployee + JobContract + MissionRunner + OpsRun + OpsRunEvent)
- Governance (Engineering Playbook v0.8.0 = 205 rules; ratification envelopes; canonical summaries; ADRs)
- Memory (ConversationMemory + memory persistence + embedding pipeline)
- RAG (documents + chunks + doc_claim_verification + `verify_doc_claims`)
- Ledger (ToolCallRecord + LLMCallEvent + deliverables + workspace scoping)

### 5.2 Layer 2 — Application Foundry

**Repeatable capability to launch and operate new applications:**
- Fleet foundry (brain_client + fleet_signer + fleet_agent_routing + 13 fleet_*.py services on DBZ)
- Product-family foundry (context-kit pattern + CLAUDE.md + 5-anchor docs + session-ledger discipline + shared brand/design system)
- Rigby-as-consultation-engine (consult_engine bridge, currently being upgraded to F2F integration)

### 5.3 Layer 3 — Applications

**Products built on Layers 1+2:**
- **Live:** CharacterOS (24/7 Global AI Phase 4)
- **Dormant but built:** 7 fleet apps (mentorforge, pitchdeckforge, contract-concierge, sellerpilot, dealflowtracker, signal-studio, compliancesentinel)
- **Reserved slots:** DealerOS, AgentOS, OpsOS, VoiceOS, SupportOS
- **Application-shape opportunities:** Rigby standalone (OPP-1), Discord AI Teammate (OPP-5), CO Family Law (OPP-6), AI-Employee-as-a-Service (OPP-8), Newsletter (OPP-9)

### 5.4 Commercialization flywheel — Governance Consulting

**Not a standalone platform — the revenue motion that finances and improves the whole ecosystem.**

Every consulting engagement generates: new Playbook rules, refined ratification patterns, cross-industry-validated methodology, canonical templates. Each engagement compounds Layer 1 governance capability. This is why OPP-2 scored 8/9 SA/CA — the artifact-production is DBZ-native, and the compounding is structural.

---

## 6. Revised OPP-7 classification (per D3)

**OPP-7 (Application Foundry) is no longer classified as aspirational.**

New status:

| Attribute | Value |
|---|---|
| **Architecturally real** | ✅ brain_client + fleet_signer bi-directional signing + fleet_agent_routing.json + 13 fleet_*.py services + 7 apps with byte-identical shared files |
| **Substantially implemented** | ✅ Session 1128 Phase 2B complete; 5 apps on stale `feat/session-1133-fleet-pa-signing` branch with contract additions ready to merge |
| **Operationally dormant** | ⚠️ 7/7 apps not currently running (containers not up); fleet auth-signing not verified E2E since Session 1133 |
| **Time to reusable capability** | **~2–3 weeks engineering:** (1) merge 5 stale feature branches OR pull work forward to main, (2) extract brain_client.py into shared package (Phase 2C planned), (3) verify fleet auth-signing E2E with at least 1 app running against DBZ, (4) `docker-compose up` end-to-end smoke test across all 7 apps |
| **Corrected SA/CA** | SA: **8**, CA: **9** (was Claude 10/10, Rigby 6/8) |
| **Blocker** | NOT "does the foundry exist" — it does. Real blocker is Phase 2C completion + revive of dormant apps. |

**Revised confidence:** MED-HIGH (was LOW in original S2841 §6.7). The foundry is not Atlas v2 — it's a completed-but-unshipped substrate that fits the same failure-mode pattern as Atlas v1 Rigby standalone: substantial substrate + small remaining engineering + long dormancy in favor of governance work.

**Update to `S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md` §6.7:** the parent doc's OPP-7 fields (confidence: LOW; falsify: "sibling apps already show 0 users") are superseded by this section. The parent doc carries a ratification banner pointing here.

---

## 7. Convergent zoom-out findings

Both Claude and Rigby, independently, produced zoom-out folds that landed on the same three concerns — near-identical phrasings:

| Concern | Claude phrasing | Rigby phrasing |
|---|---|---|
| Restructuring ≠ shipping | *"Restructuring can become a substitute for shipping. Atlas v1 sits ~1,700 sessions unexecuted."* | *"Layer framing can become a permission slip to never pick a wedge... governance-as-avoidance."* |
| Foundry evidence gap | *"Foundry story is Atlas v2 if apps aren't real. Verify compile/user-pathway of 8 sibling apps."* | *"'8 apps exist' may be true as repos/routes, but if unreachable + no users, existence can mislead prioritization — sunk-cost gravity disguised as leverage."* |
| Cash-generation constraint | *"Consulting requires Chris's time at every engagement — human-bounded flywheel."* | *"GTM coupling risk: a Foundry is not a buyer. You end up selling platform story to nobody while building more substrate."* |

**Two independent evaluations converging on the same three concerns is a strong signal.** These are the actual failure modes Atlas v1 taught. The layered restructuring inherits Atlas's lesson only if it triggers wedge-selection, not more meta-work.

---

## 8. Commercialization wedge (D4 OPEN)

Chris ratified D4: **no additional strategic restructuring before selecting ONE buyer and ONE monetization motion.** The next execution phase must have a single primary objective.

### 8.1 Wedge candidates (based on §2 scoring + §4 evidence)

| Wedge | Buyer | Motion | Time to first revenue | Compound to platform |
|---|---|---|---|---|
| **(a) Rigby standalone (Atlas v1 Phase 1)** | Solopreneurs, small operators | $30/mo consumer subscription | 6–10 weeks | High (recursion) |
| **(b) Fleet foundry Phase 2C** | Internal (unblocks 7 dormant apps for later monetization) | No direct revenue; enables future | 2–3 weeks engineering + then Layer 3 revenue | High (unblocks 6 reserved *OS slots) |
| **(c) CharacterOS to first paying customer** | Small-business operators (video ads) | Tier-based billing (already wired) | 4–8 weeks (launch/marketing) | High (validates 24/7 Global AI `*OS` family) |
| **(d) Governance Consulting engagements** | Mid-size AI startups, enterprise AI ops teams | $10–100k engagements | 4–8 weeks | Highest (flywheel; every engagement improves Playbook) |
| **(e) Employee OS OSS release** | LangChain/LangGraph/AutoGen users (OSS market) | OSS wedge → SaaS tier | 3–4 weeks OSS + 8–12 weeks first enterprise pilot | High (contributors improve primitives) |

### 8.2 Wedge-selection is the S2843 opening question

D4 forbids restructuring before wedge selection. S2843 opens with Chris choosing one of (a)–(e) — or a hybrid pairing if the two chosen are structurally compatible (e.g., d+e both compound governance/methodology). No further strategic discovery arcs open until the wedge is chosen and execution begins.

### 8.3 Cross-cutting dependency

**The Ledger Bet (proposed in S2841 §9) is load-bearing under multiple wedges:**
- Wedge (a): `LLMCallLog.workspace` FK is Rigby standalone's multi-tenant blocker.
- Wedge (b): Fleet foundry Phase 2C revive needs fleet auth-signing verified E2E, which reveals workspace-scoping gaps.
- Wedge (c): CharacterOS billing needs per-customer cost attribution when it starts charging → same FK.

Any wedge Chris chooses among (a)/(b)/(c) can plausibly fold the Ledger Bet into its first 2–4 weeks of execution.

---

## 9. D-Verdicts (D0–D6 verbatim + status)

Ratified by Chris via terminal on 2026-07-19 (S2842). Verbatim capture:

### D0 — RATIFY WITH REFINEMENTS
> *"S2841 is fundamentally correct and should be accepted as a strategic document, incorporating the pressure-test findings and corrected Foundry evidence."*

**Status:** ✅ RATIFIED. Parent doc `S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md` carries a ratification banner pointing here.

### D1 — APPROVE the layered architecture
> *"Ratify the reframing of Donkey Betz as: Layer 1: Operating System / Layer 2: Application Foundry / Layer 3: Applications / Governance Consulting as a commercialization flywheel, not a standalone platform."*

**Status:** ✅ RATIFIED. §5 above is the canonical definition of the layers.

### D2 — APPROVE the new evaluation framework
> *"Future strategic opportunities should include: Self-Acceleration, Compound Advantage. These dimensions proved valuable and materially improved the analysis."*

**Status:** ✅ RATIFIED. §1 above is the canonical rubric. All future strategic opportunity evaluations use these two dimensions in addition to the existing 18-field rubric.

### D3 — REVISE OPP-7 (Foundry)
> *"The Foundry is no longer classified as 'aspirational.' New status: Architecturally real / Substantially implemented / Operationally dormant / Approximately 2–3 weeks from becoming a reusable internal capability."*

**Status:** ✅ RATIFIED. §6 above is the canonical revised classification. Parent doc §6.7 superseded by this section.

### D4 — REQUIRE a commercialization wedge
> *"No additional strategic restructuring before selecting ONE buyer and ONE monetization motion. The next execution phase must have a single primary objective."*

**Status:** ✅ RATIFIED. Wedge candidates enumerated in §8. Chris selects wedge at S2843 open.

### D5 — CREATE the pressure-test addendum
> *"Accept Rigby's proposed S2841 D0–D6 Pressure-Test Addendum as the canonical companion document capturing: Independent review / Self-Acceleration / Compound Advantage / Foundry investigation / Revised conclusions / Remaining risks."*

**Status:** ✅ THIS DOCUMENT. Twin-mirrored to workspace `b4503364-2573-4401-9e28-61a739e0ce50` by Rigby per `feedback_rigby_writes_workspace_deliverables`.

### D6 — CLOSE strategic discovery
> *"Declare S2841 complete after the addendum is incorporated. The next phase is execution — not additional strategic discovery. Future work should focus on shipping the chosen wedge rather than expanding the opportunity portfolio."*

**Status:** ✅ RATIFIED. S2841 arc CLOSED in `docs/research/OPEN_ARCS.md` at S2842 close. Discovery moratorium in effect: no new strategic discovery arcs open until (a) the D4 wedge is selected AND (b) meaningful execution progress is demonstrated on the chosen wedge.

---

## 10. What's next — execution, not discovery (per D6)

**S2843 opens with wedge selection** (D4). Chris chooses one of the (a)–(e) candidates enumerated in §8.1. Once selected, that wedge becomes the single primary objective for the next 30–90 days.

**Discovery moratorium:** no new strategic discovery / opportunity portfolio / restructuring arcs open until execution progress is demonstrated on the chosen wedge. Governance work (Playbook amendments, ratification cadence, docs cascades) continues but is de-prioritized against ship-work.

**Ledger Bet integration:** whichever wedge Chris picks among (a)/(b)/(c), fold the Ledger Bet (`LLMCallLog.workspace` FK + per-workspace cost cap + OpsRun/OpsRunEvent/ToolCallRecord as public API + Ledger export) into its first 2–4 weeks of execution. This satisfies both the multi-tenant blocker AND provides the audit substrate the AI Work Ledger opportunity needs.

**Fleet foundry Phase 2C:** if Chris selects wedge (b) directly, execute inline. If Chris selects (a) or (c), fold Phase 2C into the wedge's first 4 weeks as an enabler for future *OS launches. If Chris selects (d) or (e), defer Phase 2C to a post-wedge-validation window.

---

## 11. Provenance & method

### 11.1 Tool-grounded evidence

- **Rigby's independent re-scoring:** `deliverable_tool.detail(id=d8e093a1-0d27-4829-aa34-92f3a9b774bd, full=true, content_offset=12000..)` for OPP-1..OPP-9 source text; `fleet_health(include_healthy=true)` for foundry probe. Non-empty tool_runs verified per `feedback_verify_rigby_tool_runs_before_trusting_sign`.
- **Claude's foundry investigation:** direct filesystem inspection of `/Users/donkeyking/development/{mentorforge,contract-concierge,pitchdeckforge,sellerpilot,dealflowtracker,signal-studio,compliancesentinel,character-os,focus-flow}` + `git log --oneline` per repo + `find`+`wc -l` for LOC census + Read of `brain_client.py` + `fleet_agent_routing.json` + `character-os/README.md` + `character-os/docs/247_GLOBAL_AI_OVERVIEW.md` + `character-os/docs/CHARACTER_OS_WHAT_IT_IS.md`.

### 11.2 Session metadata

- **Session:** S2842 (this addendum authored in-session after Chris D0–D6 verdicts)
- **PA conversation pin:** `pa-9729e4f9925445c2` (S2841 strategic CTO assessment pin) — **RETIRED at S2842 close** (force=true; seventy-second consecutive per S2770+ pattern)
- **Chat message ID (Rigby's Q1-Q3 response):** ChatConversation.id=3725 (2026-07-20 05:06:55 UTC; 7,941 chars)
- **Git HEAD at authoring:** `3b5d9a489`
- **Playbook version:** v0.8.0 (205 rules; unchanged this session)

### 11.3 Twin-pointer (twin canonical representations per `feedback_twin_deliverable_at_every_ratification`)

**Repo canonical (content deliverable):**
- Discovery: `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- Addendum (this doc): `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`
- Session handoff: `docs/handoffs/SESSION_2842_S2841_RATIFIED_D0_D6.md`
- Arc manifest: `docs/research/OPEN_ARCS.md` (S2841 row → CLOSED)

**Workspace canonical (Rigby-authored per `feedback_rigby_writes_workspace_deliverables`):**
- Content mirror of this addendum
- Ratification envelope (governance category, deliverable_type `ratification_record`)
- Location: Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`

### 11.4 What was NOT done

- No code was written this session (except this + related repo docs).
- No PRs were opened for the fleet Phase 2C revive (deferred to post-wedge-selection execution).
- No character-os code was modified (character-os is Chris's other Claude Code session; cross-repo coordination is a separate arc if Chris chooses wedge (c)).
- No new PA tools, new agents, new spiders, new Playbook rules, or new governance work shipped. Discovery moratorium (D6) begins effective this ratification.

---

*End of addendum. Ratified 2026-07-19 (S2842) by Chris via D0–D6 terminal verdicts. Canonical companion to S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md. All future references to S2841 discovery should cite BOTH docs.*
