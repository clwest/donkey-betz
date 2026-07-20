# S2841 Strategic Discovery — What Donkey Betz Actually Is

**Session:** S2841 (opened 2026-07-19; discovery output preserved here)
**Author:** Claude Code + Rigby SIGN (independent Phase 5 challenge)
**Git HEAD at authoring:** `63306c21005a`
**Playbook version:** v0.8.0 (205 rules; unchanged this session)
**Scope:** Platform (whole-DBZ discovery under Research OS §5 request-classification)
**Status:** **RATIFIED WITH REFINEMENTS (Chris D0–D6, S2842, 2026-07-19)** — see canonical companion [`S2841_PRESSURE_TEST_ADDENDUM.md`](S2841_PRESSURE_TEST_ADDENDUM.md)
**Ratification envelope:** twin-mirrored to Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` by Rigby (addendum + envelope)
**Twin workspace mirror:** Rigby-created content deliverable `d8e093a1-0d27-4829-aa34-92f3a9b774bd` in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`

> **RATIFICATION BANNER — S2842 (2026-07-19):** This discovery is ratified as a strategic document with refinements. Chris issued D0–D6 verdicts after independent Chris + ChatGPT re-evaluation, Claude + Rigby parallel independent re-scoring on two new dimensions (Self-Acceleration + Compound Advantage), and a filesystem investigation of `/Users/donkeyking/development/` that materially changed the Foundry (OPP-7) evidence base. The canonical companion document [`S2841_PRESSURE_TEST_ADDENDUM.md`](S2841_PRESSURE_TEST_ADDENDUM.md) captures the pressure-test cycle end-to-end and supersedes this doc's §6.7 (OPP-7) classification. All future references to the S2841 discovery should cite BOTH docs. D6 declares strategic discovery closed; S2843 opens with wedge selection.

---

## 0. Why this doc exists

Chris invoked a two-part strategic experiment this session:

1. **Part 1 (Startup Protocol Experiment):** Treat S2841 as a fresh CTO-lens platform assessment. Do not default to previous-arc work. Present current state, opportunities, and joint Claude+Rigby recommendation.
2. **Part 2 (Strategic Discovery Experiment):** Strip every prior framing. Determine what Chris has *actually* built, not what he thinks he built. Look for hidden products / accidental capability combinations / commercial opportunities that emerge because current framing has been too narrow.

Chris then asked us to persist the entire output to `/docs/` and workspace so the findings would not evaporate. This document is that persistence. No implementation was performed. No ratification has occurred. All D-verdicts (D0–D6 below) are open.

---

## 1. The single most important finding (put first so it isn't lost)

**Chris has already been through this discovery exercise once.**

- **Atlas v1** was authored at Session 1116 (May 2026) and ratified at Sessions 1137 + 1141.
- Atlas v1 concluded:
  - Rebrand: Donkey Betz → **24/7 Global AI**
  - Phase 1 flagship: **Rigby standalone at $30/mo**
  - Verticals (betting, legal, content, studio, dev) deferred to **Phase 3+**
  - Hard prerequisite: **`LLMCallLog.workspace` FK + per-workspace cost cap**
- Source: [`docs/24_7_GLOBAL_AI_APP_ATLAS.md`](../../24_7_GLOBAL_AI_APP_ATLAS.md) §TL;DR + §C.1 + §C.5 + §F
- Ratification: `docs/handoffs/SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md` + `docs/handoffs/SESSION_1141_JESSICA_RATIFICATION_DEEP_DIVES.md`

**That plan was never executed.** The ~1,700 sessions between Atlas v1 ratification (S1141) and this discovery (S2841) added governance depth (Playbook v0.1 → v0.8.0, IOS, AEP, ratification envelopes, 206-row content audits) with **zero external revenue** and **zero paying users** across the entire fleet (main app + 8 sibling apps).

The intervening blocker is small: **~2 weeks of engineering** to add `LLMCallLog.workspace` FK and enable per-workspace cost caps. This has been documented as HARD BLOCKER in `docs/COST_SURVIVAL_AUDIT.md` §A and `docs/narratives/WORKSPACES_AND_SCOPING.md` §30–§31 across the entire window.

The strategic question is therefore not "what should DB become?" — Atlas answered that. The urgent question is **"why haven't we executed what we already decided?"**

---

## 2. Chris's original prompts (verbatim, for provenance)

### 2.1 Part 1 — Startup Protocol Experiment

> Do not immediately recommend work. Instead, treat this as a strategic startup after a completed research arc.
>
> **Phase 1 — Independent Platform Assessment.** Before proposing any implementation work, perform an assessment of the current platform state using all available sources (startup documents, repository, architecture, research, ratified canonical summaries, Playbook, and current implementation). Your goal is not to continue the previous session. Your goal is to determine the current state of Donkey Betz as if you were a newly hired CTO reviewing the platform.
>
> Report on: overall platform maturity / major completed systems / major systems still incomplete / capabilities that exist but are underutilized / areas where documentation, implementation, and architecture disagree / technical debt / product debt / UX gaps / highest-risk areas / highest-opportunity areas.
>
> Do not suggest solutions yet.
>
> **Phase 2 — Rigby Strategic SIGN.** Before returning recommendations to me, perform a strategic SIGN with Rigby. Rigby's role is not to verify code correctness. Rigby's job is to independently answer: *"Given everything currently built and documented, what should Donkey Betz become better at next?"*
>
> Rigby should independently inspect the platform and then compare her conclusions with yours. I want: agreements / disagreements / missing observations / alternative priorities / confidence for each recommendation. Rigby should challenge assumptions rather than simply confirm them.
>
> **Phase 3 — Joint Recommendation.** Only after both assessments are complete should you produce recommendations. Rank recommendations by: expected user impact / strategic leverage / engineering effort / dependency risk / confidence. For each recommendation explain: why now, what evidence supports it, what becomes possible afterward, what user problem does it solve, why is it higher priority than the alternatives.
>
> **Phase 4 — Executive Brief.** Finish with a concise executive briefing. Include: Green/Yellow/Red assessment for Architecture / Documentation / Research / Implementation / Product / User Experience / Reliability. Top Three Strategic Opportunities. Biggest Remaining Bottleneck. Claude Recommendation. Rigby Recommendation. Joint Recommendation. Chris Decision Required.
>
> Do not assume the next task is the previous task. Treat this as a fresh strategic assessment of the entire platform and let the evidence determine what should happen next.

### 2.2 Part 2 — Strategic Discovery Experiment

> Do not begin implementation. Forget what Chris thinks Donkey Betz is. Do not assume the platform is primarily: a legal product / a sports-betting product / a content platform / a personal assistant / a multi-agent engineering system / an AI governance platform / any other previously stated product category.
>
> Treat every existing description, roadmap, active initiative, recent session, and named product surface as a hypothesis rather than a conclusion. Your task is to determine what Donkey Betz actually is, what valuable products may already be hidden inside it, and what the platform could become if we stopped optimizing around Chris's current mental model.
>
> **Core Question:** What company, product, or platform has Chris accidentally built? Look for opportunities that may not have been intentionally designed but emerge from combinations of capabilities that already exist. The goal is not to recommend another isolated feature. The goal is to identify valuable systems, products, workflows, or businesses that are currently hidden because the platform has been viewed too narrowly or because its components have mostly been evaluated independently.

Full prompt covered 8 phases: Asset Discovery / Hidden Product Discovery / Emergent Capability Analysis / Forest-for-the-Trees Challenge / Rigby Independent Strategic Challenge / Reconciliation / Opportunity Portfolio (7–12 opportunities, ≥half not on current Colorado/Betting/Newsletter/Outreach lists) / Strategic Conclusions (12 questions) / Final Executive Brief. Full text preserved in session transcript.

---

## 3. Phase 1–4 findings (Claude independent CTO pass)

### 3.1 Overall platform maturity

Technical depth is high, product surface is low.

- 927K LOC across 55K files
- 83 agents (74 enabled, 9 rerouted); 90 rows in Agent table
- 80 spiders across 41 categories; ~1.14M SpiderItemHash deduped items
- 114 PA tool schemas + 156 handlers + 8 enrichment services
- 585 concrete Django models across 23 apps
- 415 user-defined Celery tasks (92 enabled + 5 disabled in beat schedule)
- 585 concrete models; 385 migrations
- 61 frontend routes across 5-tab workspace + 9-tab betting dashboard
- 96 Discord commands across 25 Cogs
- 30 advisor personas (prompt-only, no capability specialization)
- 3,288 documents embedded (pgvector HNSW)
- 702 stored deliverables (62 ratification records, 106 research, 168 analysis, 251 document, 29 initiative_phase_doc)
- 62 initiatives total (5 ACTIVE — all substrate/governance/wiring)
- 205 Playbook rules across 11 chapters (4 FULL, 6 STUB, 1 partial)

Codebase and governance substrate are mature. Product activation and reachability are not.

### 3.2 Major completed systems

- **Personal Assistant (Rigby):** GPT-5.2 function calling, 114 tool schemas, 156 handlers, 8 enrichment services, dedicated PA queue — fully operational
- **RAG / knowledge pipeline:** intent gates (Patterns B/C/D shipped), metadata layer at 0 mismatches, docs cascade automated
- **Agent orchestration:** 83 agents, deterministic AGENT_MAP routing, provenance tracking, learning hooks
- **Spider network:** 78/80 wired, 41 categories, ~1.14M deduped items
- **Employee OS:** AIEmployee + JobContract frozen dataclasses + MissionRunner + OpsRun/OpsRunEvent audit; 4 production employees (Rigby, Platform Auditor, Chief of Staff, Docs Manager)
- **Constitutional governance:** Playbook v0.8.0 + AEP v0.1 Stage 2 default + IOS lifecycle + ratification envelope pattern + Rigby SIGN pressure-test protocol
- **Colorado Family Law Phases 0–4a:** real personal-user value shipped (mission-first template proven)
- **Docs alignment substrate (S2818–S2831):** Pattern B/C/D + DORMANT registry + user-facing diagnostics tab

### 3.3 Major systems still incomplete

- BettingPage: race conditions on sharp/arb tabs (`enabled: activeTab === 'sharp'`), no add-to-watching mutation
- CommandCenter dashboard: 70% Rigby chat wrapper; "Run All Desks" hidden behind `readyCount > 0`
- HomeTab first-run: workspace-scoped queries with no "create workspace" CTA — new sessions land blank
- Newsletter publishers (Beehiiv/Buttondown): `NotImplementedError` stubs
- Preview deploy service: 4 `NotImplementedError` stubs; HeyGen realtime avatar (F2F paused): 4 stubs
- Cockpit autopilot policy: 4/4 rows `enabled=False` (autonomous incident response dormant)
- 8 of 16 Workspace System subtabs are stubs pending cockpit migration
- `LLMCallLog.workspace` FK: **not implemented** — hard blocker on multi-tenant pricing per `docs/24_7_GLOBAL_AI_APP_ATLAS.md#24` + `docs/COST_SURVIVAL_AUDIT.md#8` + `docs/narratives/WORKSPACES_AND_SCOPING.md#30`

### 3.4 Capabilities that exist but are underutilized

- **114 PA tools** — 0 discoverable UI triggers; docs corpus already pre-endorses tool-catalog UI (`docs/24_7_GLOBAL_AI_APP_ATLAS.md#29`)
- **Strategic memory + research synthesis** services — no research-session tab
- **Spider health signals** — 78/80 wired, no dashboard visibility
- **Orphaned routes** (Billing / Analytics / Media / ProjectHub) — wired, unlinked from navbar
- **276 of 370 `@task` decorators** not in beat schedule (dead paths or on-demand only)
- **Discord bot** — 96 commands, admin hardcoded to Chris (user ID `264555101581082624` at `core/services/discord_bot.py:134-135`); ZERO external users
- **Employee OS + MissionRunner + OpsRun audit substrate** — production-tested with 4 employees; never externalized

### 3.5 Documentation ↔ implementation ↔ architecture disagreements

- `verify_doc_claims --only-drift` reports 8 medium drifts:
  - mgmt commands docs say 199, actual 215
  - PA tools: CAPABILITIES.md=86, AGENTS.md=89, actual 114
  - services: SERVICES.md says 103 files, actual 379
  - 3 broken beat task refs (`check-beat-health` → `check_beat_health`, `check-cost-thresholds` → `check_cost_thresholds`, `check-process-staleness` → `check_process_staleness`)
- **"Orphan" is semantically inconsistent:** `deliverable_tool.stats` reports `orphans=95` alongside `workspace_orphans=0` — two orphan definitions being conflated (Rigby caught this in Phase 2 & Phase 5)
- **87 blank `agent_name` deliverables** — attribution hygiene shaky despite governance work
- MEMORY.md has 2 debunked entries (`status_code=` bug in `views_rag_observability.py`, LucideIcon typing in `WorkspacePageNew.tsx`) — both false alarms per Phase 1 tech-debt scan

### 3.6 Technical debt

- `models_unified_system.py` = 21K LOC god-object, 39 `DEPRECATED` markers
- 276 orphaned Celery tasks (registered, no beat schedule, no discoverable caller)
- Frontend test coverage: **2 tests / 172 components (~1.2%)**
- Schema churn spike: 3 migrations in 5 days across legal + observability (S2782–S2806)
- Session lifecycle command floods stdout with DEBUG (drowns the pin output)
- 3 spider-intelligence endpoints appear `@csrf_exempt` with no auth guard — **security exposure risk** if publicly discovered

### 3.7 Product debt

- **21 sessions (S2820–S2840) → 1 net-new user-facing capability shipped** (thin RAG diagnostics tab); Explore agent categorized the window as ~50% governance / ~40% substrate / ~5% product / ~5% doc audit
- **9 consecutive governance sessions S2832–S2840** — longest streak in visible window
- **5 ACTIVE initiatives are 100% wiring/governance/alignment substrate** — 0% consumer product
- 702 stored deliverables dominated by governance/research/ratification categories (62 `ratification_record` alone)
- No TTFV (time-to-first-value) metric exists
- 8 sibling apps (MentorForge, Signal Studio, DealFlowTracker, Character OS, PitchDeckForge, Focus Flow, SellerPilot, ComplianceSentinel) all deployed to Vercel with **0 verified paying customers** and **7/7 UNREACHABLE** per Session 1223 fleet health check

### 3.8 User experience gaps

- Golden path (login → workspace → do work) breaks without a pre-existing workspace
- AdminPage has no access guard (`frontend/src/App.tsx:99`) — pre-prod acceptable but external exposure risk
- Marketing surfaces (LandingPage, DemoHomePage) polished; underlying capability not demonstrable
- Chris (the first user) cannot get through his own product without terminal fallback

### 3.9 Highest-risk areas

1. **21K-LOC god-object model file** with active schema churn in legal/observability
2. **Governance streak diminishing returns** — 9 sessions of ratifications improved internal correctness with zero user delta
3. **Portfolio-vs-request mismatch** — Chris asks for pivot; 5 ACTIVE initiatives all point at meta-substrate
4. **Attribution hygiene** — 87 blank agent_name deliverables + orphan definition conflation = ROI measurement unreliable
5. **`LLMCallLog.workspace` FK missing** — every multi-tenant revenue path is blocked

### 3.10 Highest-opportunity areas

1. **Rigby is best-in-class internal AI operator** — 114 tools + 8 enrichment services + GPT-5.2 function calling + ToolCallRecord provenance + workspace scoping + persona translation — but siloed behind chat
2. **Colorado Family Law is proof mission-first shipping works** — Phases 0–4a shipped
3. **RAG substrate at 0 mismatches** — any mission built on top gets grounding for free
4. **Spider network 78/80 wired** — data available; dashboard/mission surface missing
5. **Employee OS + MissionRunner audit substrate** — enterprise-grade AI-ops audit trail Chris has accidentally built while nobody sells it as a product

---

## 4. Phase 5 — Rigby independent SIGN (verbatim structure)

Rigby was routed the discovery framing WITHOUT Claude's synthesis. She was instructed to independently inspect the platform via PA tools (`deliverable_tool`, `work_tool.initiative_list`, `active_repo_tool`, `search_docs`, `platform_awareness_tool`, `kb_tool.semantic_search`, `session_tool.list_recent`) and challenge Claude's assumptions based on a 10-item bias checklist.

Rigby's tool_runs verified non-empty (anti-rubber-stamp gate held). Full response length: 22,915 chars. Key sections:

### 4.1 What DBZ actually is (Rigby's one-paragraph framing)

> Donkey Betz, as shipped today, is a **production multi-agent operations substrate** that can generate and govern large volumes of artifacts (deliverables, initiatives, audits, ratifications) and expose many vertical "app-like" routes (betting, stocks, content studios, RAG, billing, analytics, portfolio, governance/admin) but whose **dominant realized output** is **internal operator/governance work product** (702 deliverables with heavy research/governance mix, 62 ratification records; only 5 ACTIVE initiatives and all are wiring/governance substrate), and whose own strategic anchor documents explicitly frame the intended product as **Rigby standalone / 24/7 Global AI** gated on **per-workspace cost attribution** and other "Phase 0" foundations that are *documented as not fully implemented*.

### 4.2 Rigby's top 5 assets (her ranking)

1. **Evidence-bearing autonomous production system (artifact factory + audit trail)** — 702 deliverables at scale with structured lifecycle
2. **Route + tool gateway surface (unified capability API)** — many app-like surfaces on one substrate
3. **Cost survival / spend telemetry + governance-as-code (even if incomplete)** — most agent platforms lack this
4. **Spider + intelligence desk substrate (continuous intake → clustering → briefs)**
5. **Soft-suite architecture: many sibling app lanes in one deploy**

### 4.3 Rigby's top 5 hidden products

1. **Audit-grade "AI Work Ledger" for regulated teams** (MED confidence) — "AI does work and produces a ledger of what happened: artifacts + provenance + permissions + cost boundaries"
2. **Always-on "Desk Analyst" service** (MED-HIGH as service, LOW-MED as SaaS)
3. **Multi-tenant "Capability Bundle" engine for Chris's sibling apps** (MED)
4. **"Deliverable QA + Publication pipeline as a service"** (LOW-MED)
5. **"AI Ops Cockpit" for teams running agents (not building them)** (MED)

### 4.4 Rigby's top 3 emergent capability combinations

- **Combo A:** "Evidence-backed autonomous execution under explicit constraints" — closer to "AI work accounting" than "AI chat"
- **Combo B:** "Signal intake → desk brief → action queue" — converts research into operations
- **Combo C:** "Soft-suite platform: many vertical shells on shared substrate" — platform productization disguised as monolith

### 4.5 Rigby's forest-for-trees findings (blunt)

- **"More governance artifacts" as a substitute for choosing a buyer.** All 5 ACTIVE initiatives are substrate/governance. That's rational if the goal is "never lie to ourselves," but it's also a way to avoid commitment to a commercial wedge.
- **Technical sophistication hid weak user value.** "Many things" is not a product. Deliverable mix shows internal correctness and auditability dominated external outcomes.
- **Governance as substitute for product commitment.** Atlas already answered "Phase 1 = Rigby standalone" — yet today's ACTIVE initiatives are still substrate. Stuck in Phase 0/0.5.
- **Overlooked strongest commercial product hiding as overhead:** cost survival + audit ledger. Most agent platforms cannot credibly sell to enterprise because they can't answer *"What did it do, who approved it, what did it cost?"*. Chris's docs are obsessed with this for a reason. That obsession is not overhead; it's the product.

### 4.6 Rigby's blunt challenges to Claude (before seeing Claude's synthesis)

1. Reachability without buyer = internal admin console
2. Portfolio-truth-today is still governance-heavy (not just recent bias)
3. Verticals are Atlas-parked (betting/legal → Phase 3+); don't reintroduce them as Phase 1
4. Any product requiring Chris in terminal is not a product
5. Number of capabilities used ≠ product value; one coherent workflow beats capability count
6. Ignoring cost attribution = fantasy roadmap

### 4.7 Rigby's direct answers

- **Is Chris's vision too small / broad / mis-framed / right?** **Too broad in surfaces, too small in recognizing what he accidentally built.** The accidental product is not a bunch of vertical apps; it's **AI work accounting + governance + execution substrate** that could be sold as managed service or compliance-grade platform.
- **What company might DBZ become if current framing is removed?** A company that sells **"audit-grade AI operations"**: always-on research/ops execution with durable artifacts, approvals, constraints, and cost accountability. Think: **"the QuickBooks / Jira of AI work,"** not "another assistant UI."
- **Larger opportunity underneath current surfaces?** Yes: **the ledger + constraint engine** is the wedge. UI surfaces are incidental. Moat is the ability to answer: *what ran, why, what it produced, who approved, what it cost, what changed over time*.

---

## 5. Phase 6 — Reconciliation

### 5.1 Strong agreements between Claude and Rigby

1. DBZ is not a consumer product; it's an AI-agent operations infrastructure substrate producing governance-grade artifacts.
2. The hidden crown jewel is the audit-graded "AI Work Ledger" — durable artifacts + provenance + constraints + cost accountability.
3. Atlas v1 (Rigby standalone Phase 1 + verticals deferred) remains correct and unexecuted.
4. `LLMCallLog.workspace` FK is the single most-important technical blocker; documented as such for ~1,700 sessions.
5. Governance-as-substitute-for-commitment is the dominant anti-pattern.
6. 5 ACTIVE initiatives = 100% substrate. No consumer product will emerge without portfolio pivot.
7. Any product requiring Chris in the terminal is not a product.

### 5.2 Material disagreements (winner named)

- **Claude's Phase-3 REC 1 was Colorado Family Law Phase 4.** **Rigby wins** — Colorado is Chris's personal use, not a scalable buyer thesis.
- **Claude proposed "Tools Panel + spider dashboard + golden path".** **Rigby wins** — internal admin console trap.
- **Claude framed the wedge as "reachability".** **Rigby wins** — the wedge is the evidence contract ("what ran / why / who approved / what it cost"), not the surface.

### 5.3 Ideas rejected after challenge

- Sports betting as strategic mission (Atlas v1 already demoted; Rigby confirms)
- Tools Panel as top rec (admin console)
- Spider dashboard as top rec (only if serves chosen mission)
- Any single-vertical product as Phase 1 flagship (Atlas v1 already answered)

### 5.4 Ideas strengthened by evidence

- **"AI Work Ledger" as the hidden product** — verified via 702 deliverables, 62 ratification records, ToolCallRecord persistence, MissionRunner + OpsRun/OpsRunEvent + Employee OS
- **Rigby is uniquely differentiated from ChatGPT/Claude/Cursor** — verified via file:line: ToolCallRecord provenance (`tool_dispatcher.py:1029`), workspace scoping (`unified_pa_entrypoint.py:2260`), persona translation with truth hygiene (`UDB_TRANSLATION_LAYER.md:162`), structured error classification (`tool_dispatcher.py:181`)
- **Employee OS could be extracted in 3-9 days per coupling point** (escalation sink / verdict sink / shift-report sink) — near-term unbundleable

### 5.5 Opportunities one saw and the other missed

- **Claude found:** Discord distribution vacuum (96 commands, admin hardcoded to Chris only); 8 sibling apps deployed with 0 paying users; 3 spider-intelligence endpoints publicly accessible without auth (security exposure); Employee OS as extractable OSS + SaaS
- **Rigby found:** "AI Work Ledger" as a coherent product category (QuickBooks-of-AI-work framing); "always-on Desk Analyst" workflow already latent; "Soft-Suite platform" as productization of the monolith itself; the framing that governance is a way to avoid commitment

### 5.6 Assumptions that could not be verified

- Discord bot has any external users (evidence suggests: no)
- Any sibling app has any real users (evidence: all "Phase 0 gating", 0 verified)
- Actual audience size (no numbers on newsletter, Twitter, GitHub)
- Whether "audit-graded AI ops" as a market category has real buyers (never buyer-interviewed)

### 5.7 Evidence gaps affecting confidence

- Zero buyer conversations conducted
- Adjacent competitor products (LangSmith, Braintrust, Humanloop, PagerDuty for AI) may adequately serve the "audit-graded AI ops" niche
- Real enterprise buyer interviews required to validate

---

## 6. Phase 7 — Opportunity Portfolio (9 ranked)

Ranking rubric: (a) foundation actually exists, (b) time to revenue < 12 weeks favored, (c) differentiation is real, (d) doesn't require Chris in terminal, (e) clear buyer with painful problem. **6 of 9 are net-new opportunities not on the current Colorado/Betting/Newsletter/Outreach lists.**

### 6.1 ⭐ OPP-1 — Rigby standalone (Atlas v1 Phase 1 flagship, unexecuted)

| Field | Value |
|---|---|
| Buyer | Solopreneurs, small consultancy owners, operators doing complex work who've hit ChatGPT context/hallucination limits |
| Pain | "ChatGPT forgets what it did, invents facts, no audit trail, no persona control" |
| Promise | AI teammate that persists, proves work, translates for different audiences |
| Capabilities used | 114 PA tools + 156 handlers + workspace scoping + persona translation + ToolCallRecord + 8 enrichment services + GPT-5.2 function calling |
| Foundation evidence | Fully working internally; Atlas v1 ratified pricing $30/mo (S1141) |
| Missing | `LLMCallLog.workspace` FK; multi-tenant hardening; billing wiring; consumer UI |
| Time to first user outcome | 4–6 weeks (10 beta users) |
| Time to first revenue | 6–10 weeks |
| Distribution | Twitter, indie-hacker, Product Hunt, existing Discord, waitlist |
| Differentiation | tool_runs audit + workspace persistence + persona translation — no ChatGPT/Claude/Cursor equivalent |
| Defensibility | MED (mechanism copyable in 6–12 months; enrichment services + culture harder) |
| Effort | HIGH (multi-tenant + billing + consumer UI + FK) |
| Dependency risk | Cost attribution FK gates everything |
| Market risk | MED — does market actually pay $30/mo for "provable AI teammate" vs. $20 ChatGPT Plus? |
| Operator dependence | MED (Chris presence for launch, then automatable) |
| Confidence | MED (highest is Atlas already ratified this) |
| Why hiding | Ratified 12 months ago, kept blocked on FK |
| Falsify | 10 beta users churn without converting to paid |

### 6.2 ⭐ OPP-2 — Governance Consulting (CTO-as-a-service for AI teams codifying methodology) — NET-NEW

| Field | Value |
|---|---|
| Buyer | Mid-size AI startups (Series A–B), enterprise AI ops teams, defense contractors deploying LLM agents |
| Pain | "We ship AI agents fast but keep making the same mistakes; no methodology, no audit, no way to justify decisions to leadership/legal/regulators" |
| Promise | "We install Playbook methodology + evidence-cited decisions + agent-audit substrate in 8–12 weeks" |
| Capabilities used | Playbook v0.8.0 (205 rules as proof-of-work); AEP; IOS; Rigby SIGN model; ratification envelopes; canonical summaries |
| Foundation | Chris has this running internally; nobody else does |
| Missing | Sales channel; first case study; pricing model; deliverable templates for external clients |
| Time to first outcome | 2–4 weeks (first paid engagement scoped) |
| Time to first revenue | 4–8 weeks ($10–100k engagement) |
| Distribution | Warm intros via AI-ops communities; content marketing (blog series about Playbook methodology); LinkedIn |
| Differentiation | Living implementation with 205 rules is proof-of-work no vendor has |
| Defensibility | MED (methodology teachable; culture harder to replicate) |
| Effort | LOW (services, no product) |
| Dependency risk | Chris's time (single-founder bottleneck) |
| Market risk | MED (competes with McKinsey Digital / BCG X / boutique AI consultancies) |
| Operator dependence | HIGH (Chris IS the product initially) |
| Confidence | **MED-HIGH** (fastest concrete revenue path) |
| Why hiding | Framed as internal-only substrate; never packaged as service |
| Falsify | 20 outreach → 0 engagements = wrong buyer OR wrong positioning |

### 6.3 ⭐ OPP-3 — "AI Work Ledger" / OpsRun Cloud (audit-grade AI ops platform) — NET-NEW

| Field | Value |
|---|---|
| Buyer | Compliance-heavy AI ops teams (finance, healthcare, defense, regulated fintech) |
| Pain | "Our AI does work; we can't prove what / why / who approved / what it cost" |
| Promise | Every AI action → durable queryable audit-exportable record with cost attribution |
| Capabilities used | Employee OS + MissionRunner + OpsRun + OpsRunEvent + LLMCallEvent + ToolCallRecord + ratification envelopes + Playbook governance |
| Foundation | 702 deliverables + 62 ratifications + 4 production employees + full audit substrate shipped |
| Missing | Multi-tenant hardening; RBAC; SIEM/SOC2 export; LLMCallLog.workspace FK; Django ORM decoupling |
| Time to first outcome | 8–12 weeks (design partner pilot) |
| Time to first revenue | 12–16 weeks |
| Distribution | Direct sales; AI-ops conferences (Ray Summit, DevDay); regulated-industry contacts |
| Differentiation | Adjacent products (LangSmith = observability; Braintrust = eval; PagerDuty = incident) — no direct competitor combines governance + audit + cost |
| Defensibility | MED-HIGH (methodology + culture harder than mechanism) |
| Effort | HIGH (12–20 weeks unbundle + 4–6 weeks compliance layer) |
| Dependency risk | Cost attribution FK; multi-tenant test |
| Market risk | MED (category exists in adjacent form; DBZ combines uniquely but market may prefer point tools) |
| Operator dependence | HIGH initially |
| Confidence | MED-HIGH (biggest strategic play; longest horizon) |
| Why hiding | Appears as internal governance overhead; the overhead IS the product |
| Falsify | 5 design partner interviews reveal buyers prefer LangSmith + custom audit tooling |

### 6.4 OPP-4 — Employee OS OSS + SaaS (AI-agent audit library, hosted service tier) — NET-NEW

| Field | Value |
|---|---|
| Buyer | LangChain/LangGraph/AutoGen users (OSS market); enterprise AI ops teams (SaaS tier) |
| Pain | "My agents run daily but I have no visibility into failure patterns, dedupe, or audit trail" |
| Promise | 5-line integration → federated failure clustering + 24h escalation dedupe + hierarchical audit |
| Capabilities used | Employee OS primitives (AIEmployee + JobContract + MissionRunner + OpsRun) |
| Foundation | 4 production employees running (Rigby, Platform Auditor, Chief of Staff, Docs Manager) |
| Missing | Decouple 3 coupling points (escalation sink, verdict sink, shift-report sink); OSS docs |
| Time to first outcome | 3–4 weeks (OSS release + docs) |
| Time to first revenue | 8–12 weeks (first enterprise design partner @ $500–5000/mo) |
| Distribution | Hacker News / GitHub / PyPI (OSS wedge); AI-ops conference sponsorship; consulting-led |
| Differentiation | Production-tested primitives + calendar-day idempotency + error-signature dedupe |
| Defensibility | MED (copyable in 3–6 months) |
| Effort | MED (~4–6 weeks) |
| Dependency risk | LOW (decoupling is 1–3 days per coupling point) |
| Market risk | LOW-MED (OSS wedge with SaaS upsell is proven pattern) |
| Operator dependence | LOW (self-serve OSS) |
| Confidence | MED-HIGH |
| Why hiding | Internal library nobody sees |
| Falsify | OSS release → <100 stars in 30 days = category doesn't exist |

### 6.5 OPP-5 — Discord AI Teammate (Rigby-as-Discord-bot with provable work) — NET-NEW

| Field | Value |
|---|---|
| Buyer | Discord communities running small businesses (indie devs, crypto DAOs, agency ops, creator collectives) |
| Pain | "Chatbots hallucinate; we can't audit what our AI teammate did" |
| Promise | AI teammate that responds in Discord, proves its work, joins your team's workflow |
| Capabilities used | Discord bot (96 commands, already built) + Rigby + workspace scoping + ToolCallRecord |
| Foundation | Bot exists, admin hardcoded to Chris only — flipping open is small change |
| Missing | Multi-guild support; billing; permission model; Discord App Directory listing |
| Time to first outcome | 2–3 weeks (5 beta Discord servers) |
| Time to first revenue | 4–6 weeks ($10–50/mo per server) |
| Distribution | Discord App Directory + community outreach |
| Differentiation | 96 commands ready + tool_runs audit + persona translation |
| Defensibility | LOW-MED (Discord app market crowded; tool_runs audit rare) |
| Effort | MED (multi-tenant Discord) |
| Dependency risk | LOW (bot infra exists) |
| Market risk | HIGH (untested consumer market) |
| Operator dependence | LOW-MED |
| Confidence | LOW-MED |
| Why hiding | Bot built for Chris only; never opened |
| Falsify | 5 beta servers → 0 conversion after 30 days |

### 6.6 OPP-6 — Colorado Family Law Practice Companion (vertical extension of Phases 0-4a)

| Field | Value |
|---|---|
| Buyer | Colorado family law solo practitioners + pro-se litigants |
| Pain | Family law changes, form updates, precedent searches take hours |
| Promise | Real-time change alerts + form auto-populate + case-law summaries |
| Capabilities used | Colorado Family Law spider (Playwright unique moat) + Rigby + Legal Doc Drafter + Phases 0-4a shipped |
| Foundation | Phases 0-4a actually shipped and Chris uses personally |
| Missing | Multi-user; billing; CO bar marketing |
| Time to first outcome | 4-8 weeks (10 CO bar beta) |
| Time to first revenue | 8-12 weeks ($99-299/mo) |
| Distribution | CO Bar Association + LegalTech directories |
| Differentiation | State-specific + Playwright scraping unique; already-working mission template |
| Defensibility | HIGH within CO; MED nationally (state-by-state expansion) |
| Effort | MED |
| Dependency risk | Cost FK |
| Market risk | MED (single-state niche) |
| Confidence | MED (Chris personal-value proven; extension unproven) |
| Falsify | 10 beta practitioners → 0 conversion |

### 6.7 OPP-7 — Cross-App AI Fleet Activation (Rigby as gateway to 8 sibling apps) — NET-NEW

> **⚠️ SUPERSEDED by [`S2841_PRESSURE_TEST_ADDENDUM.md`](S2841_PRESSURE_TEST_ADDENDUM.md) §6 (Chris D3, S2842).** The original classification below (LOW confidence, "0 users = distribution problem") was based on the fleet_health probe alone. Filesystem investigation of `/Users/donkeyking/development/` revealed the foundry is **architecturally real + substantially implemented + operationally dormant**, ~2–3 weeks from reusable capability. Corrected SA: **8**, CA: **9** (from Claude 10/10 + Rigby 6/8). Read the addendum §4 (foundry evidence investigation) + §6 (revised classification) before citing this section.


| Field | Value |
|---|---|
| Buyer | MentorForge / Signal Studio / DealFlowTracker existing waitlist users (if any) |
| Pain | Sibling apps unmonetizable alone; users need reason to sign up |
| Promise | One Rigby account = access to whole Suite |
| Capabilities used | Rigby + workspace + capability bundles (spec exists) |
| Foundation | 8 sibling apps deployed to Vercel; 7/7 UNREACHABLE per Session 1223; Signal Studio F1 stub only |
| Missing | Cross-app auth; capability bundle enforcement; LLMCallLog.workspace FK; user acquisition |
| Time to first outcome | 12-16 weeks |
| Time to first revenue | 16-24 weeks |
| Confidence | LOW (Atlas v1 already deprioritized as Phase 3+) |
| Falsify | Sibling apps already show 0 users = distribution problem not integration problem |

### 6.8 OPP-8 — AI-Employee-as-a-Service for creator collectives — NET-NEW

| Field | Value |
|---|---|
| Buyer | Content agencies, creator collectives, podcast networks |
| Pain | "We need dedicated AI teammate per project; hiring humans is expensive" |
| Promise | Contract an AI employee via Rigby — she works in your Slack/Discord + delivers audit-graded output |
| Capabilities used | Rigby + Employee OS + JobContract + MissionRunner + Content pipeline |
| Foundation | 4 production employees prove the pattern |
| Missing | Multi-tenant; per-employee billing; Slack integration |
| Time to first outcome | 6-10 weeks |
| Time to first revenue | 12-16 weeks |
| Confidence | LOW-MED |

### 6.9 OPP-9 — Newsletter-as-Signal-Ledger (audit-graded briefing product)

| Field | Value |
|---|---|
| Buyer | Founders / investors / ops leaders wanting daily briefings with provenance |
| Pain | Aggregator briefs lack provenance and personalization |
| Promise | Every claim in your brief cites source + score + agent-of-record |
| Foundation | Operator Edge newsletter exists (0 verified subs) |
| Missing | Subscriber acquisition, personalization, paid tier |
| Confidence | LOW-MED (crowded market) |

---

## 7. Phase 8 — Strategic Conclusions (12 questions answered)

1. **What has Chris actually built?** A production **AI operations infrastructure substrate** — durable multi-agent workflows with governance-grade artifact production, provenance, and audit trail. Rigby (AI operator) + Employee OS (audit-graded execution) + Playbook (methodology) + Deliverables (durable artifacts) + Spiders (data) + Ratification envelopes.

2. **Most valuable capability?** Rigby's **provable-work tool_runs + workspace scoping + persona translation** combination. No ChatGPT/Claude/Cursor competitor equivalently provides this.

3. **Most overlooked capability?** **Employee OS + MissionRunner audit substrate.** Chris has accidentally built what enterprises pay LangSmith + PagerDuty + Splunk to approximate.

4. **Most valuable combination?** **Employee OS + Rigby + Playbook + Ratification envelope = "AI work accounting."** Rigby's framing — QuickBooks/Jira of AI work.

5. **Closest to already existing?** **Rigby standalone** (Atlas v1 Phase 1 flagship). 90% built; waiting on cost FK + billing + consumer UI. 6-10 weeks work.

6. **Largest long-term potential?** **"AI Work Ledger" / OpsRun Cloud** for regulated AI ops. Category could be worth $50-500M ARR for the winner.

7. **Fastest revenue?** **Governance Consulting.** 4-8 weeks to first $10-100k engagement. Playbook = proof-of-work.

8. **Best demonstrates the DBZ thesis?** **Employee OS as OSS + SaaS.** Positions DBZ as "we shipped the primitives; here's the library, here's the hosted version."

9. **Should be abandoned / deprioritized?**
   - Post-2899 execution arc Class 4 (6 broken citations, no user consequence)
   - Playbook v0.9 amendment arc (4 candidates for substrate no user has touched)
   - BettingPage as strategic product (Atlas v1 already demoted)
   - Sibling app activation as near-term (Phase 3+ per Atlas)
   - Colorado Phase 4 beyond personal use
   - Any further governance additions until cost FK ships

10. **What should DB become better at next?** **Converting an AI action into a durable, provable, cost-attributed record for an external buyer.** (Not "converting a fresh session into value" — that was Phase-2-only framing; the discovery revealed the accountability trail IS the product.)

11. **What company might this become?** **"Ledger" / "OpsRun Cloud" — the audit-grade infrastructure company for AI-agent operations.** Not another assistant.

12. **Larger opportunity underneath?** **Yes — the AI-agent-operations-as-audit-graded-infrastructure category.** Chris has built a working prototype of what the industry will need in 2-5 years as AI regulation catches up (SOC2 for LLM agents, EU AI Act audit trails, financial services LLM compliance). Category could be worth $10-100M ARR for the winner.

---

## 8. Final Executive Brief

### 8.1 What Donkey Betz Appears to Be

A single-operator internal ops cockpit with 83 agents, 80 spiders, 114 PA tools, 585 models, 415 Celery tasks, extensive governance substrate, and zero external users or revenue. Eight deployed sibling apps with zero paying customers each. Discord bot with 96 commands, admin hardcoded to Chris.

### 8.2 What Chris Thinks He Built

A personal AI assistant + multi-agent engineering platform + AI research operating system that will eventually pivot to consumer verticals (currently naming candidates as sports betting, Colorado legal, content newsletter, outreach).

### 8.3 What May Actually Have Been Built

An **AI-agent operations infrastructure company** with all primitives for "audit-grade AI work" — durable artifacts + provenance + cost accountability + adversarial verification (Rigby SIGN) + agent-employer-of-record contracts (Employee OS) + workspace-scoped multi-tenancy. The consumer wedge candidates are downstream applications of the substrate, not the substrate itself.

### 8.4 The Three Most Surprising Hidden Opportunities

1. **Governance Consulting** — sell Playbook methodology to other AI teams TODAY for $50-100k engagements. Fastest revenue path. Zero code work. The 205 rules are proof-of-work no vendor has.
2. **Employee OS as OSS + SaaS** — audit-substrate library + hosted service. 3-9 days per coupling point to decouple. OSS launch → SaaS tier is a proven wedge pattern.
3. **Rigby-as-Discord-teammate** — 96-command bot dropped into external servers. Distribution channel already exists (Discord App Directory); admin hardcoded (small flip); tool_runs audit is genuinely unique.

### 8.5 The Strongest Existing Product

**Rigby.** File:line evidence shows genuine differentiation from ChatGPT/Claude/Cursor (ToolCallRecord provenance, workspace scoping, persona translation, structured error semantics). Atlas v1 correctly identified this as Phase 1 flagship. Unshipped for ~1,700 sessions.

### 8.6 The Strongest New Product Opportunity

**"AI Work Ledger" / OpsRun Cloud.** Employee OS + MissionRunner + OpsRun/OpsRunEvent + ToolCallRecord + Ratification envelope + Playbook governance productized as audit-grade AI ops platform. Enterprise buyer category exists (regulated finance / healthcare / defense). 12-16 weeks unbundle + 4-6 weeks compliance layer.

### 8.7 The Most Valuable Shared Integration Seam

**`LLMCallLog.workspace` FK + per-workspace cost cap.** Single ~2-week engineering task unblocks Rigby standalone, AI Work Ledger, Employee OS SaaS, Cross-App Fleet, and every other multi-tenant revenue path. Documented as HARD BLOCKER for ~1,700 sessions. Never shipped.

### 8.8 The Biggest Strategic Blind Spot

**Chris has already been through this discovery** (Atlas v1, S1116/S1137/S1141). He ratified "Rigby standalone as Phase 1 flagship" 12+ months ago and hasn't executed. Instead ~1,700 sessions have added governance depth without shipping the ratified plan. The blind spot is not "what should we build" — it's **"why haven't we executed what we already decided."**

### 8.9 The Biggest Forest-for-the-Trees Finding

**Governance is being used as a substitute for product commitment.** 9 consecutive sessions of governance work with 0 user delta. 5 ACTIVE initiatives are all substrate/wiring. Playbook has 205 rules for a codebase with 1 user. The substrate is now more mature than the product it's meant to support. Every problem looks like a substrate problem because there's no external buyer forcing product-shaped feedback.

### 8.10 Claude's Recommendation

Ship `LLMCallLog.workspace` FK in 2 weeks. Then run parallel 30-day bets on (a) Rigby standalone activation with 10 beta users, (b) Governance Consulting outreach to 20 potential clients. Freeze all governance/audit arc work during this window.

### 8.11 Rigby's Recommendation

Reframe the platform as **"audit-grade AI work accounting"** and stop treating verticals as the product. Choose one buyer path (compliance-grade AI ops team OR solo operator wanting provable AI teammate) and instrument TTFV metric. Do not add features until first paying customer exists.

### 8.12 Joint Recommendation

Both agents converge: **Chris has built an AI-agent operations infrastructure substrate, not a consumer product. The Atlas v1 plan (Rigby standalone as Phase 1 flagship) was correct and remains unexecuted.** Freeze governance work, ship cost-attribution FK, validate audit-grade AI ops thesis with real buyers within 30 days. **Do the buyer validation before deciding between Rigby standalone (OPP-1), Governance Consulting (OPP-2), or AI Work Ledger (OPP-3) as the primary product bet.**

---

## 9. One Bet for the Next 30 Days — "The Ledger Bet"

Bounded 30-day experiment that tests the central thesis without committing the whole platform.

### 9.1 Week 1-2
- Ship `LLMCallLog.workspace` FK + per-workspace cost cap (the ~1,700-session blocker)
- Fix the 87 blank-`agent_name` attribution issue
- No other feature work

### 9.2 Week 2-3
- Instrument OpsRun/OpsRunEvent/ToolCallRecord as a **public API** + export format
- Add a "Ledger Export" surface that dumps 30 days of AI activity as (a) markdown report, (b) JSON, (c) CSV
- Add one internal Chris-triggered demo showing the export in action

### 9.3 Week 3-4
- Reach out to 20 potential buyers across 3 categories:
  - 8 × compliance-heavy AI teams (finance ops, healthcare AI, regulated fintech)
  - 6 × mid-size AI startups doing agent-based products (governance consulting fit)
  - 6 × operators / consultancies who might pay $30/mo for Rigby standalone
- Sell 3-5 pilot conversations at $500-5000 discovery fee OR paid consulting hour
- Positioning A/B test: "QuickBooks of AI work" vs. "The compliance layer for LLM agents" vs. "Provable AI teammate for solo operators"

### 9.4 Bounded scope

No new features. No new agents. No new spiders. No new Playbook rules. No governance work. No new verticals.

### 9.5 Measurable success

- 3+ real buyer conversations completed (recorded, transcript stored as deliverable with provenance)
- 1+ signed pilot LOI at $500-5000/mo OR 1 signed consulting engagement at $10k+
- `LLMCallLog.workspace` FK shipped + verified working in multi-tenant test
- Ledger export format validated by ≥1 external reviewer

### 9.6 Falsifiable failure

- 20 outreach → 0 conversations = wrong buyer category; reframe
- 3 conversations → 0 pilot LOI = wrong problem framing; iterate positioning
- Cannot ship FK in 30 days = organizational failure to execute; **this is the more important signal**

---

## 10. Chris Decision Surface (D0-D6, all open)

- **D0 (meta-decision):** Atlas v1 has been ratified but unexecuted for ~1,700 sessions. Do we (a) **archive** Atlas v1 and re-plan from scratch, OR (b) **commit** to executing the ratified plan? Current state — ratified + unexecuted — is neither, and self-defeating.

- **D1:** Adopt the reframing: **DBZ = AI-agent operations infrastructure company** (not consumer product; not vertical stack; not personal ops platform)?

- **D2:** Commit to **"The Ledger Bet"** as the 30-day bounded experiment (single north-star = 20 buyer conversations + 1 LOI + FK shipped)?

- **D3:** **Freeze** Playbook v0.9 amendment arc + post-2899 execution arc + all governance work during the 30-day bet window?

- **D4:** Approve **buyer outreach to 20 potential customers** (Chris speaks, no full sales cycle expected — this is user research)?

- **D5:** If the bet succeeds (D-signal defined above), commit next 90 days to productizing **Rigby (OPP-1) + AI Work Ledger (OPP-3) + Employee OS OSS (OPP-4)** as a coherent audit-grade AI ops product?

- **D6:** If the bet **fails** (0 buyer signal after 20 outreach), commit to that as decisive evidence that the "audit-grade AI ops" thesis is wrong — and revert to Atlas v1 Phase 1 Rigby-standalone-consumer path?

---

## 11. Provenance & method

### 11.1 Independent inspection evidence

**Claude used:**
- Direct file reads: `docs/PLATFORM_INVENTORY.md`, `docs/UDB_BEHAVIOR_LAYER.md`, `docs/UDB_TRANSLATION_LAYER.md`, `docs/24_7_GLOBAL_AI_APP_ATLAS.md`, `docs/research/OPEN_ARCS.md`, `00-START-NEXT-SESSION.md`, `CLAUDE.md`, `MEMORY.md`
- Bash: `brew services list`, `python manage.py verify_doc_claims --only-drift`, `python manage.py backfill_document_status_from_docs_index --dry-run`, `git rev-parse HEAD`, `python manage.py session_lifecycle open`
- 5 parallel Explore agents:
  - PA tools as productizable AI-employee surface (700-word report, file:line evidence)
  - Governance stack as enterprise AI-agent SaaS (700-word report)
  - Spider network + RAG as intelligence data product (650-word report)
  - Employee OS + MissionRunner as AI-employee product (700-word report)
  - External distribution + Suite integrations + Discord (700-word report)
- 3 additional Explore agents (Phase 1 CTO assessment): recent-session velocity, frontend/UX state, tech debt

**Rigby used** (verified via tool_runs verbose):
- `deliverable_tool.list show_all=true` + `deliverable_tool.stats show_all=true full_by_agent=true`
- `work_tool.initiative_list status=all/ACTIVE`
- `active_repo_tool.get`
- `platform_awareness_tool.system_overview` + `platform_awareness_tool.get_manifest`
- `search_docs` with strategic queries (Atlas, moat, buyer, LLMCallLog cost attribution, etc.)
- `kb_tool.semantic_search` with authority_weighted=true
- `session_tool.list_recent`

### 11.2 Session metadata

- Pin minted: `pa-9729e4f9925445c2` (label `s2841-strategic-cto-assessment`)
- Two dispatches to Rigby:
  - Phase 2 SIGN (12,451 chars response; 5 tool calls)
  - Phase 5 independent discovery (22,915 chars response; 7 tool calls)
- Anti-rubber-stamp gate held both times (tool_runs non-empty per `feedback_verify_rigby_tool_runs_before_trusting_sign`)

### 11.3 What was NOT done

- No code was written or edited
- No PRs opened
- No ratification envelope authored (this is discovery output, not ratified plan)
- No workspace deliverable created ratification-scoped (twin mirror is content-only, per `feedback_twin_deliverable_at_every_ratification`)
- No implementation of any recommendation
- No `make recycle-all` (no code shipped this session)

### 11.4 Twin-pointer

- **Repo:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md` (this file)
- **Handoff:** `docs/handoffs/SESSION_2841_STRATEGIC_DISCOVERY.md`
- **Workspace:** Rigby-created content deliverable in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` (ID filled at close)
- **Session pin:** `pa-9729e4f9925445c2` (still live; retire at S2841 close)
