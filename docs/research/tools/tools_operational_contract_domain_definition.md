# Tools Operational Contract — Domain Definition (Phase 0)

**Session:** 2728 (opening the Tools arc)
**Date:** 2026-07-08
**Status:** Research proposal — Phase 0 Domain Definition only. Awaiting Chris's review before any subsequent research or authoring proceeds.
**Predecessors:**
- Session 2727: Engineering Playbook v0.1.0 ratified — tag `playbook-v0.1.0`, body commit `b372edfe127f1af59c4322871092aa7151669463`, content_hash `sha256:0205af5b74d34d686d064552b28989c472e2b4048c780a873e4e03193de988ab`, workspace ratification record `RATIFICATION_20260708_PLAYBOOK_v0_1_0` = `b083c034-5aba-4dc3-9758-57eba29b4bf2` in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`.
- Group 2600 PA (S2699 close, 2026-07-06): outward-facing PA contract-plane arc — `docs/research/domains/pa/2699_pa_canonical_summary.md`. Verdict: *"MECHANISM is OPERATIONAL across all four contract planes; DECLARATION/SoT is consistently partial/implicit across all four planes; arc-close diagnosis is design-plane governance."*
- Cross-Domain Integration Audit §14.16 (2026-07-06 refresh): PA cross-domain integration diagnosis at HEAD.
- Groups 1300 / 1700 / 1800 / 1900 / 2000+ / 2100 / 2200 / 2400 / 2500: canonical summaries closed and available as evidence.
- I-0100 Observability Correlation Spine + Mission Evidence Substrate (S2700 close, 2026-07-07); I-0200 RAG Corpus Substrate Maturity Gradient (S2701 close, 2026-07-07): recent implementation arcs.
- MEMORY.md (auto-loaded at every session open) — ~90 crystallized feedback rules governing PA / Rigby / Claude operational discipline. Currently the de-facto operational-contract layer, made authoritative-by-reference via Playbook §5.2.1.

**Author:** Claude (Opus 4.7, 1M context)

**Scope constraints (this session):** Research only. No architecture proposals. No Tool Contract authoring. No implementation. No workspace deliverables created. No modifications to any constitutional artifact. No `OPEN_ARCS.md` row. No arc-pin mint. No routing to Rigby. This document is the sole artifact of the session. Repository ends clean — this file, plus its parent directory `docs/research/tools/`, only.

**Explicit intent per mission (verbatim from Chris):**

> *"We are attempting to answer one constitutional question: 'What operational contracts actually exist between Rigby and every platform capability?' Our goal is not to describe how tools SHOULD work. Our goal is to discover how they ACTUALLY work. Assume many current assumptions are incorrect. Use the exact evidence-first methodology that produced the Engineering Playbook. Observe reality first. Challenge assumptions. Pressure-test conclusions. Differentiate: documented behavior / runtime behavior / observed behavior / constitutional requirements. Do not merge those together. Before proposing any architecture, perform domain definition only. Do NOT organize by implementation. Instead organize by constitutional responsibility. One of the largest discoveries of the Playbook was that architecture emerged from evidence instead of design. Apply exactly the same philosophy here."*

---

## 1. Executive summary

**Question:** *What operational contracts actually exist between Rigby and every platform capability?*

**Answer from Phase 0 evidence (not architecture — description of the domain the question opens):**

The question opens an architectural domain distinct from every closed arc to date. Prior arcs have studied capabilities themselves (Memory, Content, Sports, etc.), the substrates capabilities emit into (Events, Observability, Auth), or the contract SURFACES that expose capabilities to callers (Group 2500 API, Group 2600 PA endpoint SoT, Group 2200 Frontend). None have studied **the invariant surface at the reach** — the promise a capability makes to an agentic caller mid-turn, and the promise the agentic caller makes to the capability.

Rigby is today's only observed instance of an agentic caller. The domain generalizes but SHOULD scope-lock to Rigby to keep evidence primary rather than speculative.

**Working domain name (candidate — pressure-test invited):** *Personal Assistant Operational Contract Domain*, arc-slug `tools` (per Chris's directory placement).

**Constitutional home candidate:** Engineering Playbook v0.1.0 **Chapter 5 (PA / Rigby Collaboration)** is currently a STUB with three rules (5.1.1, 5.2.1, 5.3.1). §5.5 explicitly reserves four extension points that this domain fills exactly:
1. PA tool call discipline codification
2. Verifier-loop pattern extensions for cross-workspace work
3. Placeholder-stall recovery discipline
4. Multi-agent authoring coordination (parked — presumes >1 concurrent agent)

Whether the arc's output belongs (a) as MINOR amendments to Ch 5 promoting STUB → FULL, (b) as standalone ADRs referencing Ch 5 §5.5 as extension-point home, or (c) as a companion layer doc parallel to `UDB_BEHAVIOR_LAYER.md` / `UDB_TRANSLATION_LAYER.md` — is a Chris-gated decision AT arc close, not a Phase 0 assertion.

**Evidence separation held throughout (§0.4 discipline):**

- **[D]** *Documented*: current-state topic docs, PLATFORM_WHAT_IT_IS narrative.
- **[R]** *Runtime*: PLATFORM_INVENTORY autoblock + code at HEAD `9d158805`.
- **[O]** *Observed*: MEMORY.md feedback rules (crystallized failure modes), handoff post-mortems, close-doc verdicts.
- **[C]** *Constitutional*: ratified Playbook rules, ratified ADRs, ratified workspace records.

These four often disagree in this domain. Naming where and why is part of the arc's constitutional weight.

**Proposed research decomposition (candidate 5-child taxonomy — awaits ratification):** Parent scoping (P0) + five children (P1 Authority Carriage / P2 Capability Contract / P3 Knowledge Substrate / P4 Failure & Recovery / P5 Verifier-Loop) + xx99 canonical summary. Runtime target 6 sessions per playbook §11 precedent across seven prior parent-with-4-children arcs.

---

## Table of contents

1. [Executive summary](#1-executive-summary)
2. [Phase 0 orientation report](#2-phase-0-orientation-report)
3. [Phase 1 constitutional context](#3-phase-1-constitutional-context)
4. [Phase 2 the actual constitutional question](#4-phase-2-the-actual-constitutional-question)
5. [Phase 3 domain boundary map](#5-phase-3-domain-boundary-map)
6. [Phase 4 domain inventory](#6-phase-4-domain-inventory)
7. [Phase 5 natural categories](#7-phase-5-natural-categories)
8. [Phase 6 overlap with prior arcs](#8-phase-6-overlap-with-prior-arcs)
9. [Phase 7 existing constitutional documents that govern portions](#9-phase-7-existing-constitutional-documents-that-govern-portions)
10. [Phase 8 evidence base already in-repo](#10-phase-8-evidence-base-already-in-repo)
11. [Phase 9 proposed research decomposition (candidate)](#11-phase-9-proposed-research-decomposition-candidate)
12. [Risks](#12-risks)
13. [Unknowns](#13-unknowns)
14. [What this document explicitly does not do](#14-what-this-document-explicitly-does-not-do)

---

## 2. Phase 0 orientation report

**Session opens against Playbook v0.1.0 ratified; no active implementation arc; no active research arc.**

### 2.1 Repository state (primary evidence)

| Field | Value | Source |
|---|---|---|
| Branch | `main` | `git status` |
| HEAD | `9d158805` (Merge PR #3009 — SESSION 2727 handoff + anchors) | `git rev-parse HEAD` |
| Working tree | clean pre-authoring; this file is the sole delta | `git status` |
| Behind/ahead origin/main | 0 / 0 | `git status` |
| Pending migrations | 0 | (S2727 close verified; no code changed since) |
| Recent activity | Last 5 merges (top of `git log`): #3009 handoff + anchors, #90c277f6 handoff draft, #3008 Canon Registry, #dd635690 Canon Registry S2727 Step 10, #d82b450a frontmatter fill | `git log --oneline -5` |

### 2.2 Constitutional state (primary evidence, per S2727 close)

| Field | Value |
|---|---|
| Playbook body commit | `b372edfe127f1af59c4322871092aa7151669463` |
| Playbook tag | `playbook-v0.1.0` (annotated, applied to `d82b450a`) |
| Playbook content_hash | `sha256:0205af5b74d34d686d064552b28989c472e2b4048c780a873e4e03193de988ab` |
| Ratification record | `RATIFICATION_20260708_PLAYBOOK_v0_1_0` = `b083c034-5aba-4dc3-9758-57eba29b4bf2` |
| Workspace | `a9a16593-e0a4-44dc-8256-efc65d524b3c` (Architecture & Research) |
| Constitutional debt | CD-47 RESOLVED; CD-48 + CD-49 targeted for v0.1.1 PATCH |
| Rule inventory | 190 rules across 11 chapters; 4 FULL (0/1/6/10) + 7 STUB (2/3/4/5/7/8/9); 95 of 190 Rigby-verified PASS |
| Chapter 5 status | STUB — 3 rules (5.1.1, 5.2.1, 5.3.1); §5.5 lists 4 extension points |

Chapter 5 is the natural constitutional home for this arc's outputs. Its stub-state is the pointer that opens this research question — Playbook §5.3.1 defers full authoring to a future MINOR amendment; §5.5 lists the specific extension points a MINOR amendment would address.

### 2.3 Prior-arc coverage relevant to this domain

The tools/agentic-caller contract question intersects **12 prior research arcs**. All are closed; none has covered the inward-facing agent-capability contract as its primary study.

| Arc | Closed | Coverage relevant to this domain |
|---|---|---|
| Group 1300 Memory | S1399 | Rigby's memory + knowledge access substrate (P3 candidate input) |
| Group 1500 Sports | S1599 | Adjacent — one of many capabilities Rigby reaches for |
| Group 1600 Content | S1699 | Adjacent — content-plane capabilities Rigby dispatches |
| Group 1700 Observability | S1799 | Telemetry emission substrate Rigby MUST honor (P4 + X-OBSERVABILITY input) |
| Group 1800 HumanAttention | S1899 | Where Rigby raises HAI events; when (adjacent) |
| Group 1900 Authority Enforcement | S1999 | Per-user authority, KillSwitch reachability (P1 candidate input) |
| Group 2000+ Event/Integration | S2099 | Tool→handler emission contract, envelope discipline (P2 candidate input) |
| Group 2100 RAG / Document Loading | S2199 | Knowledge substrate governance (P3 candidate input) |
| Group 2200 Frontend | S2299 | Adjacent — workspace-context resolver from client side |
| Group 2400 Auth | S2499 | Session lifecycle, silent-401 SYSTEMIC (P1 candidate input) |
| Group 2500 API | S2599 | Contract SoT, REST↔WS T7 (P2 candidate input) |
| Group 2600 PA (outward-facing) | S2699 | Complement — outward-facing contract-plane arc; this arc studies inward-facing |
| I-0100 Observability Correlation Spine | S2700 | trace_id, PA→AgentExecution write, RIGBY_DELEGATION flag (P4 input) |
| I-0200 RAG Corpus Substrate Maturity | S2701 | ADR-0004 PROVISIONAL (P3 input) |

**Consequence:** This arc is disproportionately a **unification arc**. Most primary evidence is already in closed-arc outputs. The novelty is (a) integrating them into an inward-facing agent-capability contract statement, (b) mapping to Ch 5 STUB extension points, and (c) surfacing where operational contracts are ratified vs merely observed.

### 2.4 Runtime state (primary evidence, PLATFORM_INVENTORY 2026-07-05)

| Runtime surface | Count | Source |
|---|---|---|
| PA tool schemas | 113 | `pa_tool_schemas.py` |
| PA tool handlers | 156 | `tool_dispatcher.py` |
| Enrichment services | 8 | `unified_pa_entrypoint.py` context-building |
| WORKSPACE_AWARE_AGENTS | 20 | `core/epa_handlers_tools.py` constant |
| Total AGENT_MAP agents | 83 (74 enabled, 9 rerouted, 0 blocked) | `agent_router.py` |
| LLM providers | 6 | `LLMProviderRegistry` |
| Signal pattern types | 10 | `SignalCluster` |
| Discord commands | 96 (48 slash + 48 prefix) | `discord_bot.py` (11,676 lines) |
| Body systems | 9 | `run_all_systems_scan` |
| Beat schedule | 92 enabled + 5 disabled | `PeriodicTask` rows |

**Schema/handler ratio 113/156 is a domain-defining evidence point** — it says the observable surface Rigby's LLM sees (schemas) is a proper subset of the total handler capability. What Rigby *can* do vs what she *knows she can do* is an observable gap. Naming why the gap exists — intentional gating, drift, undeclared handlers — is inventory work for the arc.

### 2.5 Context-kit health

Narrative anchor (`PLATFORM_WHAT_IT_IS.md`) and runtime anchor (`PLATFORM_INVENTORY.md`) exist. `CLAUDE.md` L7 blockquote is the S2727-refreshed constitutional anchor pointing at Playbook v0.1.0 + workspace `a9a16593-…`. `00-START-NEXT-SESSION.md` is the S2727-close-authored version listing four candidate priorities; this arc does not appear in that list because the arc is being opened this session by direct Chris directive, not inherited from S2727.

Orientation complete. Proceeding to constitutional context.

---

## 3. Phase 1 constitutional context

### 3.1 Playbook v0.1.0 Chapter 5 (verbatim excerpts, per HEAD `9d158805`)

**§5.1.1 [EP]:** *"Chapter 5 codifies Personal Assistant collaboration discipline by reference to the auto-loaded MEMORY rules at `MEMORY.md` in the repository root. This chapter MUST NOT duplicate the collaboration rules codified in MEMORY.md; it references them and identifies their integration with Playbook amendment discipline."*

**§5.2.1 [EP]:** *"The collaboration protocol adopted for agent-mediated authoring work is: the author directs; the Personal Assistant executes; the author verifies. This protocol is codified in the MEMORY.md rule `feedback_claude_directs_rigby_then_verifies` and the verifier-loop pattern is codified in the MEMORY.md rule `feedback_verifier_loop_pattern`."*

**§5.3.1 [EP]:** *"Full authoring of Chapter 5's constitutional treatment of Personal Assistant collaboration is deferred to a future MINOR amendment. Until then, MEMORY.md remains the authoritative source for the collaboration protocol."*

**§5.5 Extension points (informative):**
- PA tool call discipline codification.
- Verifier-loop pattern extensions for cross-workspace work.
- Placeholder-stall recovery discipline.
- Multi-agent authoring coordination.

### 3.2 Reading Ch 5 against this arc's mission

Ch 5 is scoped to **authoring collaboration** — the Chris ↔ Claude ↔ Rigby three-way. The mission opens a broader question: what is Rigby's operational contract with **every platform capability**, not only her role as authoring executor.

Two possible relationships:

1. **Ch 5 hosts the arc's output.** Ch 5 is the constitutional chapter for anything PA/Rigby-related; this arc's findings become MINOR-amendment rules at §5.4+ addressing the extension points at §5.5.
2. **This arc's output is broader than Ch 5.** If the inventory reveals that Rigby's operational-contract discipline touches capability-general concerns (e.g., freshness invariants for RAG, provenance carriage under PIC-10) that don't reduce to "PA collaboration," the arc may recommend either (a) growing Ch 5's scope from "collaboration" to "operational contract" (Playbook §10.2 MINOR amendment lifecycle), or (b) authoring a companion layer doc parallel to UDB_BEHAVIOR_LAYER.

Which of (1) or (2) is correct is a **Phase 4 or Phase 5 arc-close decision, not a Phase 0 assertion.**

### 3.3 MEMORY.md as the current authoritative operational-contract layer

Playbook §5.2.1 makes MEMORY.md authoritative-by-reference for the author-directs/PA-executes/author-verifies protocol. MEMORY.md at the current HEAD contains ~90 feedback rules governing PA/Rigby/Claude collaboration and operational discipline. Many of them are one-line pointers to detail files; the aggregate weight is ~95KB of crystallized failure-mode + success-mode rules.

**Constitutional character of MEMORY.md rules:** they are **[O] observed**, not **[C] constitutional**. They achieve authoritative status via Ch 5.2.1's reference, but their per-rule content is not individually ratified. This dual character — observed content held authoritative by constitutional reference — is a domain-specific artifact this arc must acknowledge before proposing changes to it.

### 3.4 Adjacent constitutional layers (not overlapping)

- **`UDB_BEHAVIOR_LAYER.md`** governs Rigby's *voice and substance discipline at the LLM surface* (what she says, how she says it, whether she preserves rendered facts across turns). Adjacent to this arc; not overlapping. The mission is not about how Rigby speaks — it is about what contracts govern her reach.
- **`UDB_TRANSLATION_LAYER.md`** governs *persona-based framing shifts* (same fact → different vocabulary per audience). Adjacent; not overlapping.
- **`CLAUDE.md`** governs *Claude's session-open behavior in this repository*. Includes the Rigby-first-comms rule and the "Claude directs, Rigby executes, Claude verifies" collaboration shape. Anchors the collaboration protocol at the caller side; does not govern Rigby's own operational discipline at the capability side.
- **Playbook Chapter 6 (FULL) PIC-10** provides the provenance classification standard that any operational contract using citations must satisfy. Cross-cutting; applies inside every category this arc surfaces.
- **Playbook Chapter 9 (STUB) Recovery Playbooks** is the natural constitutional home for cross-cutting recovery discipline beyond PA scope. This arc's P4 category may output rules that belong in Ch 9 rather than Ch 5.
- **Playbook Chapter 10 (FULL) Evolution and Amendment** governs how any amendments this arc proposes get authored, reviewed, and ratified. Every arc output is bound by Ch 10.

---

## 4. Phase 2 the actual constitutional question

**Restated precisely (mission verbatim):** *What operational contracts actually exist between Rigby and every platform capability?*

**Underneath that surface, four deeper questions:**

1. **Directionality.** The word "contract" is bidirectional. This arc must characterize both directions independently. Direction A = what the capability owes Rigby at call-boundary (freshness, workspace-scope preservation, error typing, telemetry emission, provenance carriage). Direction B = what Rigby owes the capability at call-return (actor identity carriage, workspace-mode gating, budget honor, verifier posture, no silent-fail acceptance). Prior arcs consistently studied capabilities themselves (correctness of the capability's own logic); this arc studies the *invariant at the reach*, which is a different constitutional concept.

2. **Aggregation.** The word "every" implies an enumeration. How large is the enumeration? Prior evidence suggests it is very large — 113 tool schemas, 156 handlers, 8 enrichment services, 20 workspace-aware agents, 30 advisors, 83 agents, 6 gateway tools, 6 LLM providers, ~415 Celery tasks. The arc must decide whether to enumerate per-capability (impossibly large) or to type capabilities into classes where each class shares a contract shape (tractable). Class-first is the only viable discipline; the class taxonomy IS the arc's output.

3. **Authority.** Whose ratification makes an operational contract *constitutional* rather than *observed*? Playbook §5.2.1 answers one specific case (Chris ratifies via Ch 5 reference to MEMORY.md); the general answer for capability-level operational contracts is not currently ratified. The arc must characterize the ratification pathway for operational-contract rules alongside the rules themselves.

4. **Reification.** Where does an operational contract *live*? Options observed in existing evidence: (a) code (Python constant, dataclass, decorator); (b) documentation (topic doc, ADR, Playbook chapter); (c) MEMORY.md (feedback rule); (d) runtime configuration (feature flag, env var, DB row); (e) test (regression, smoke); (f) telemetry (emitted metric, dashboard threshold). Each substrate has different ratification and revision properties. The arc must characterize where each contract-class SHOULD live and why.

**Challenging the default:** the reflexive answer is *"just document the tool schemas and their expected behavior."* That answer is wrong because:

- Tool schemas describe the *interface* the LLM sees; they do not describe the *invariants the capability owes the agent* (freshness, workspace-scope preservation, provenance carriage, failure typing). A schema documents shape; a contract documents promise.
- Not all Rigby↔capability reaches go through tool schemas. Enrichment services fire pre-turn without LLM decision. Context builders inject silently. Feature flags gate silently. Substantial portions of Rigby's operational reach are non-tool.
- The 113/156 schema/handler ratio proves a subset of capability is intentionally not exposed to the LLM. That gating is itself an operational contract — one that is not currently ratified.

---

## 5. Phase 3 domain boundary map

Every boundary carries an invariant. Naming the invariant is Phase 0 work; enforcing it is later-phase work.

| Boundary | Inside domain | Outside domain | Invariant at the boundary |
|---|---|---|---|
| **Upper (System Owner)** | How Chris's ratification directives flow into Rigby's runtime context | What Chris chooses to ask for (product/business intent) | Rigby's context MUST reflect the current Playbook + ratified ADR set; drift is a contract violation |
| **Left (caller / frontend)** | Actor identity + workspace_id + trust boundary conveyance from caller INTO Rigby's turn | `/api/pa/chat/` endpoint SoT (Group 2600 owned); PA-client typed contract (Group 2600 owned); frontend contract-surface (Group 2200 owned) | Rigby MUST NOT infer actor or workspace from message text; the caller MUST carry them |
| **Right (per-capability)** | The invariants each capability owes Rigby at call-boundary + what Rigby owes at call-return | Each capability's internal correctness (owned by its own arc) | Capability MUST type its errors, honor workspace scope, emit telemetry, carry provenance |
| **Bottom (substrate)** | How Rigby's operational context (workspace_id, session pin, trace_id, actor identity) survives Celery / Redis / PostgreSQL boundaries | Broker capacity / infrastructure health (Group 1700 owned) | Serialization boundaries MUST NOT drop operational context; loss = contract violation |
| **Top (LLM)** | Contracts that must exist so LLM-shaped calls behave correctly (autofill vulnerability, tool-count budget, cost boundedness) | LLM correctness / prompt voice (UDB layers own) | Schema declarations MUST NOT trust LLM defaults; handlers MUST treat autofilled params as adversarial |

---

## 6. Phase 4 domain inventory

Raw inventory of things *inside* the domain, grouped by primary evidence source. **Not yet decomposed into categories.** Each item names its evidence class in shorthand.

### 6.1 What Rigby knows she can do

- Tool schema surface — 113 OpenAI function-calling schemas **[R: `pa_tool_schemas.py`]**. What the LLM sees at turn start.
- Tool handler surface — 156 registered handlers **[R: `tool_dispatcher.py`]**. What can actually execute. The 43-handler gap between schema and dispatch is an unratified operational contract.
- Gateway consolidation — 6 primary gateway tools (`governance_tool`, `work_tool`, `content_tool`, `intelligence_tool`, `ops_tool`, `studio_tool`) absorb ~13 predecessor tools **[R: topic doc §Tool Schemas]**. Meta-consolidation pattern.
- `run_agent` meta-tool — 77+ agent enum accessible via one schema entry **[R: topic doc]**. Deep aggregation.
- 20 WORKSPACE_AWARE_AGENTS — a subset of agents whose tool-call requires workspace_id **[R: `core/epa_handlers_tools.py`]**. Boundary declaration.
- `agent_introspection_tool` disjoint taxonomy — 2 blocked + 8 rerouted + 72 fully-enabled = 82 total agents **[R: topic doc]**. Categorization discipline.

### 6.2 Actor + workspace + authority carriage

- Global vs workspace PA modes **[D: topic doc]**. Workspace mode activates only from explicit `workspace_id` / `AssistantProfile.workspace` / workspace-aware UI context; text-only inference is forbidden.
- `execute_with_workspace()` at `core/agents/base_agent.py:5355` **[R]** + `WorkspaceManager.get_active_workspace()` at `workspace_manager.py:1697` **[R]** — canonical workspace resolution path.
- KillSwitch + GovernanceState per-plane reachability from Rigby **[C: Group 1900 findings]** — currently 0 enforcement readers for authority / KillSwitch.
- CF-C2 session-lifecycle PA slice **[O: Group 2600 close doc]** — session_tool retire on user logout is a cross-arc coordination flag.
- CF-B3 workspace-membership implicit permission gate via WORKSPACE_AWARE_AGENTS **[O: Group 2402 close doc]** — F-B-HIGH-3 identified but ownership between Cat B (identification) and Group 2600 (policy) is split.
- FleetSignatureAuthentication conveys NO workspace_id **[O: cross-domain audit §14.16]** — PA → Fleet-Federation reach is MISSING.
- Pin ownership verification — `feedback_pa_local_verify_ownership` — before first `tools/pa_local.sh` call in a session, confirm token resolves to `donkeyking` not admin **[O]**.

### 6.3 Capability contract shape

- Silent fail vs typed error at handler boundary **[O: `feedback_editor_fail_loud` — Editor/operator agents MUST edit not generate; fallback belongs at dispatcher not agent]**.
- LLM autofill vulnerability — GPT-5.2 fills every declared optional boolean with `False`, even when user didn't ask **[O: `feedback_llm_autofills_boolean_params_with_false`]**. `is not None` handler checks fire on autofill. Truthy-only check is the safe pattern.
- Boolean-vs-string sentinel discipline — `orphans` string sentinel pattern **[O: same feedback rule]**.
- `deliverable_tool.create` silently defaults new rows to `status=completed` regardless of explicit `status='draft'` param **[O: `feedback_deliverable_create_defaults_to_completed`]**. Confirmed S1241.
- `deliverable_tool.update status=completed` silently ignores the status field **[O: `feedback_deliverable_status_via_content_complete`]** — PublishGate state machine ownership at content_tool, not deliverable_tool.update.
- `deliverable_tool.update` silently falls back to `action=list` above ~6-7kB payload **[O: `feedback_deliverable_tool_use_append_for_large_payloads`]** — root cause unknown; workaround is `append`.
- `auto_followup=False` suppresses completion-banner subscription **[O: `feedback_auto_followup_false_suppresses_banner`]** — correct for forensic dispatches; wrong for normal conversation. `AgentExecution.input_data['context']['auto_followup']` is the ORM check before chasing WS/daphne bugs.
- Procfile ↔ Makefile queue parity **[O: `feedback_procfile_makefile_queue_parity`]** — task_routes queue must be consumed by BOTH Procfile and Makefile or dispatch silently queues forever. `claude_code_tool` failed multi-session on this.
- Anthropic + OpenAI factory required **[O: `feedback_anthropic_client_factory` + `feedback_openai_client_factory`]** — bare client instantiation defaults to 600s timeout. Factory usage is a constitutional contract enforced by CI lint (`check-llm-sdk.yml`).
- gpt-5* `max_completion_tokens` floor = 4000 **[O: `feedback_gpt5_max_completion_tokens_floor`]** — reasoning tokens consume 1500-2000 before output. Below floor returns empty content silently.
- Agent fail-loud rule **[O: `feedback_editor_fail_loud`]** — editor/operator agents MUST fail loud.

### 6.4 Knowledge & retrieval substrate

- Docs cascade is 4-step, not 1-step **[O: `feedback_docs_pipeline_4_step_cascade`]** — `build_docs_index` alone only refreshes file index. Full cascade: (1) build_docs_index (2) build_rag_corpus (3) sync_docs_index_to_documents (4) `--embed` or embed_documents `--all-unembedded`.
- Docs cascade runs at every arc/session close-out **[O: `feedback_docs_cascade_at_every_close`]** — extends the 4-step rule; not doing this means Rigby search stale and long-term research continuity degrades.
- Cascade PR must include the embed step **[O: `feedback_cascade_pr_must_include_embed_step`]** — S1802 close caught 6 unembedded docs plus 2 prior sessions' worth of synced-but-unembedded work.
- ADR-0004 PROVISIONAL — RAG Corpus Substrate Maturity Gradient **[C: I-0200 close, S2701]** — first PROVISIONAL ADR in the corpus; two-field pattern (`status: accepted` + `provisional: true`).
- Session 1234 close found prod corpus 12d stale + 1820 docs never pushed **[O: same feedback rule]** — freshness failure at scale.
- `search_docs` GPT-5.2 autofill trap — autofills `originating_session=0` **[O: `feedback_ratification_workflow_gotchas`]** — use `kb_tool` route instead.

### 6.5 Context injection & enrichment

- 8 enrichment services fire pre-turn: `intelligence_enricher`, `blog_performance`, `domain_context`, `spider_trends`, `advisor`, `strategic_memory`, `proactive_intelligence`, `platform_briefing` **[R: topic doc §Enrichment Pipeline]**.
- Timeouts on every DB-touching context step (2-5s) **[R: topic doc §Context Building]** — Postgres connection hangs at 134s observed on Railway force graceful degradation.
- Relevance gating — 15% keyword overlap threshold; content-related intents skip the gate **[R]**.
- Enrichment caps 1500-2000 chars per section (S1006 raised from 300-600, which was discarding 85-95% of data) **[R + O]**.

### 6.6 Session, turn & lifecycle discipline

- SIGN pin worker instability at turn 2 **[O: `feedback_rigby_sign_worker_instability_recovery`]** — fresh Rigby SIGN pin returning generic "issue processing" errors after 2 substantive turns → pin poisoned at LLM boundary. Recovery: retire jammed pin + mint fresh + ultra-short ping first. Two-pin ceiling before falling back to parent-Claude verifier-loop.
- `session_tool.retire` works — do not fall back to abandon-plus-repin **[O: `feedback_session_tool_retire_works`]** — the retire action is live; the stale belief in prior docs is wrong.
- `pa_chat.py` token still needs override **[O: `feedback_pa_chat_local_override`]** — bare invocation against local without explicit local-token override → 401. Always use `tools/pa_local.sh` or set `PA_API_TOKEN` explicitly.
- PA worker manual restart needs `PA_USE_FUNCTION_CALLING=true` env **[O: `feedback_pa_worker_function_calling_env`]** — `make celery` sets it; ad-hoc worker startup does not. Without it, source=claude-code messages short-circuit to no-tool path and Rigby returns text-only "no tool access" refusals.
- Response_id / previous_response_id caching for multi-turn **[R]** — 90% cached input discount on follow-up turns.
- Conversation history — `ChatConversation` model with DB-backed memory (S1030); load last 10 rows on PA init so context survives Celery `max_tasks_per_child` recycles **[R]**.
- Tool-call metadata persistence — `ChatConversation.metadata` stores `tool_calls` list + `response_id` (S1036) **[R]**.

### 6.7 Failure classification & recovery

- Placeholder-stall pattern **[O: `feedback_rigby_tool_verification`]** — Chris says "tools seem broken/hung" → read the verbose `Tool Runs` block; usually placeholder-stall not outage.
- Silent-401 SYSTEMIC via api.ts:48-56 whole-frontend ~100% swallow rate **[O: Group 2200 S2203 F2]** — ~630 of ~1300 gated call-sites at silent-401 risk.
- Router heartbeat NOT dead code **[O: `feedback_router_heartbeat_not_dead`]** — `agent_router._router_heartbeat_loop` is live for non-PA dispatches. Two parallel paths exist; both must use `save(update_fields=[...])`.
- Local Celery stall 6-step diag sequence **[O: `feedback_local_celery_stall_playbook`]** — CeleryTaskEvent → queue depths → `inspect ping` → log grep for `mutex.cc` → purge stale queues → restart without beat.
- AUDIT_FINDINGS.md #12 is the canonical Celery deferred-by-policy list **[O]** — before declaring any Celery task orphan, cross-reference §12 (S1115 audit, 272→10 orphan reduction). `python manage.py audit_celery_zero_fire` (S1245) mirrors KNOWN_DEFERRED set.
- Fleet caller verification before Celery deletes **[O: `feedback_fleet_caller_verification_before_celery_deletes`]** — 3-axis sweep required (cross-repo grep + Rigby ops_tool.celery_task_history + ORM FleetServiceKey probe).
- Verify before deleting "dead" code **[O: `feedback_verify_before_deleting_dead_code`]** — grep direct callers + stringified refs + `docs/` + last 5-10 handoffs + audit deliverables via Rigby.
- Ratification workflow gotchas **[O: `feedback_ratification_workflow_gotchas`]** — five known gotchas at ratification workflow surface.

### 6.8 Provenance, trace & observability emission

- LLMCallEvent + ToolCallRecord + OpsRunEvent + CeleryTaskEvent + AgentExecution — 5 parallel execution telemetry layers **[O: cross-domain audit §1]** plus 14+ event-shaped models. No central intake. `RIGBY_EVENT_INTAKE_ENABLED=False` default.
- I-0100 Observability Correlation Spine + Mission Evidence Substrate **[C: S2700 close]** — trace_id write-side fix + PA→AgentExecution wire + MISSION_RUNNER + RIGBY_DELEGATION staged unlock. Both flags remain `false` by default at `core/settings.py:138-140` and `:173-174`.
- EventBus partially implemented, weakly adopted, unverified end-to-end **[O: cross-domain audit §1]** — 8 Redis Streams + 1 DLQ; 3 consumer groups; 5 publisher wrappers; at least 1 active caller (`scoring_dispatcher.py`). Coverage + observability + adoption problem, not binary off state.
- Cross-cutting X-PROVENANCE — every category emits provenance under Playbook Ch 6 PIC-10. This is a cross-cutting invariant, not a standalone subdomain.

### 6.9 Verifier-loop constitutional posture

- Playbook §5.2.1 codifies the "author directs, PA executes, author verifies" protocol via MEMORY reference **[C]**.
- `feedback_claude_directs_rigby_then_verifies` — code/PRs/file edits stay with Claude; investigations/audits/deliverable edits route to Rigby; Claude verifies via ORM/git/file read.
- `feedback_verifier_loop_pattern` — verifier catches Rigby's placeholder pattern + wrong-baseline-default pattern before shipping.
- `feedback_rigby_scope` — do not do ops/verification Rigby can do itself.
- `feedback_rigby_collaboration` — read her FULL responses; answer her questions; don't cherry-pick and go solo.
- `feedback_triage_decision_card_pattern` — batch decisions ≥3 items get tight cards with proposed action + Claude lean + Rigby lean + "agree all" override.

### 6.10 Cost, budget & runtime bounds

- gpt-5-mini `max_completion_tokens` floor 4000 **[O]**.
- PA task `time_limit=300s` / `soft_time_limit=280s` **[R]**.
- Railway ~30s proxy timeout forces async Celery pattern **[R]**.
- Tool schema tokens ~5,000 input; system prompt ~2,500; conversation history ~3,000; tool results ~1,000; output ~500 **[D + R: topic doc §Cost]**.
- ~$0.027 per 1-tool turn first message; ~$0.009 follow-up with cache **[D]**.

### 6.11 Default behaviors

- `deliverable_tool.create` → `status=completed` default **[O]**.
- Boolean autofill → `False` default **[O]**.
- `deliverable_tool.update` payload > ~6-7kB → silent fallback to `action=list` **[O]**.
- `pa_chat.py` bare invocation post-S1249 → LOCAL default (was PROD) **[O]**.
- Feature flag defaults — `RIGBY_DELEGATION_ENABLED=false`, `PA_AGENT_EXECUTION_WRITE_ENABLED=false`, `RIGBY_EVENT_INTAKE_ENABLED=false`, `PA_USE_FUNCTION_CALLING=true` on Railway (env-set) **[C + R]**.

---

## 7. Phase 5 natural categories

Grouping the raw inventory (§6) by shared constitutional weight — not by implementation.

### 7.1 Primary categories (each carries independent constitutional weight)

**P-AUTHORITY-CARRIAGE** — Actor identity + workspace-scope + authority conveyance from caller through Rigby's turn into every capability call and every emitted event. Answers: on whose behalf is Rigby acting; how does workspace_id survive Celery/Redis/PostgreSQL/LLM boundaries; when does KillSwitch or GovernanceState reach Rigby. Inventory sections consumed: §6.2. Prior arcs consumed: 1900, 2400 CF-C2, 2402 F-B-HIGH-3, 2600 close.

**P-CAPABILITY-CONTRACT** — Tool schema → handler contract shape; typed vs silent errors; default-value discipline (autofill); safe-default posture; discovery model; the 113/156 schema-vs-handler ratio and its intentional or drift-driven nature. Answers: what does a capability owe Rigby at call-boundary; what does Rigby owe a capability at call-return. Inventory sections consumed: §6.1, §6.3, §6.11. Prior arcs consumed: 2500 (contract SoT), 2000+ (event contracts).

**P-KNOWLEDGE-SUBSTRATE** — Rigby's access model to the corpus (RAG, KB, `search_docs`, docs cascade) including provenance-class carriage into retrieved evidence, freshness thresholds, and staleness detection. Answers: how does Rigby know what she thinks she knows; when is her knowledge substrate authoritative. Inventory sections consumed: §6.4, §6.5 (partial). Prior arcs consumed: 1300, 2100, I-0200 ADR-0004.

**P-FAILURE-AND-RECOVERY** — Placeholder-stall, silent-fail, worker jam, pin poison, autofill=False, queue parity, banner suppression — as a classification standard and recovery playbook set. Answers: what shape does a Rigby failure take; what recovery is constitutional vs ad-hoc. Inventory sections consumed: §6.6, §6.7, §6.8 (partial). Prior arcs consumed: 1700, I-0100. Potential secondary constitutional home: Playbook Ch 9 (STUB Recovery Playbooks).

**P-VERIFIER-LOOP** — The constitutional posture of "Claude directs, Rigby executes, Claude verifies" and its exceptions. Answers: when is Rigby's output authoritative; when MUST it be independently verified; what does the verifier owe. Inventory sections consumed: §6.9. Prior arcs consumed: Playbook Ch 5 §5.2.1 (direct anchor). This is the only category with an existing ratified rule; the others are new constitutional territory.

### 7.2 Cross-cutting attributes (apply inside every primary category, not standalone subdomains)

**X-FRESHNESS** — every category has a freshness clock (auth session TTL, tool schema drift, embed staleness, docs cascade lag).

**X-PROVENANCE** — every category emits or carries provenance under Playbook Ch 6 PIC-10.

**X-OBSERVABILITY** — every category MUST emit telemetry (LLMCallEvent + ToolCallRecord + OpsRunEvent + trace_id).

**X-DEFAULT-BEHAVIOR** — every category has a "what happens when unsure" default whose safety must be characterized.

**X-COST-BOUND** — every category operates under a token / time / budget bound (Ch 8 STUB Runtime Discipline touches this).

Cross-cutting attributes are best captured as **invariants inside each primary category's child audit**, not as independent arcs. This mirrors Playbook Ch 6 PIC-10 discipline — provenance is one chapter; it applies to every rule everywhere. Opening independent arcs for cross-cutting attributes would duplicate ratified work.

### 7.3 Chris's example list — mapped against emergent categories

Chris named 15 candidate categories with the instruction to challenge, merge, split, or replace them. Mapping:

| Chris's candidate | Placement in emergent structure |
|---|---|
| Knowledge Retrieval | P3 KNOWLEDGE-SUBSTRATE |
| Repository Truth | P3 KNOWLEDGE-SUBSTRATE (via canonical_authority) + P1 AUTHORITY-CARRIAGE |
| Workspace Truth | P1 AUTHORITY-CARRIAGE |
| Runtime Execution | P4 FAILURE-AND-RECOVERY + X-COST-BOUND |
| Worker Lifecycle | P4 FAILURE-AND-RECOVERY |
| Search Behavior | P3 KNOWLEDGE-SUBSTRATE |
| Context Injection | P2 CAPABILITY-CONTRACT (enrichment services are non-tool capabilities) + P3 (RAG-fed context) |
| Provenance | X-PROVENANCE (cross-cutting; already ratified in Ch 6) |
| Authority | P1 AUTHORITY-CARRIAGE |
| Freshness | X-FRESHNESS (cross-cutting) |
| Failure Classification | P4 FAILURE-AND-RECOVERY |
| Recovery | P4 FAILURE-AND-RECOVERY |
| Observability | X-OBSERVABILITY (cross-cutting) |
| Tool Discovery | P2 CAPABILITY-CONTRACT |
| Tool Safety | P2 CAPABILITY-CONTRACT + X-DEFAULT-BEHAVIOR (cross-cutting attribute of P2) |
| Default Behaviors | X-DEFAULT-BEHAVIOR (cross-cutting) |

Collapse rationale:
- "Repository Truth" and "Workspace Truth" both reduce to *authority-scope carriage* at different scales. Same constitutional weight; collapse to P1.
- "Failure Classification" + "Recovery" are the two directions of the same category. Collapse to P4.
- "Provenance" / "Freshness" / "Observability" / "Default Behaviors" appear in every primary category. Cross-cutting attributes, not standalone.
- "Tool Discovery" + "Tool Safety" both describe the schema-and-dispatch contract shape. Collapse to P2.
- "Search Behavior" + "Knowledge Retrieval" are two verbs for the same substrate. Collapse to P3.

**Net result:** 15 example candidates → 5 primary categories + 5 cross-cutting attributes.

---

## 8. Phase 6 overlap with prior arcs

Ranked by dependency weight for this arc's proposed child structure.

| Prior arc | Overlap direction | Coverage this arc receives | Coverage this arc adds |
|---|---|---|---|
| **Group 2600 PA (S2699)** | Complement, not overlap | 2600 studied outward-facing contract; PA-endpoint SoT + PA-client typed contract + session-lifecycle CF-C2 + workspace-authz F-B-HIGH-3 | Inward-facing contract at every capability reach |
| **Group 1900 Authority Enforcement (S1999)** | P1 primary input | Per-user-authority emission wiring; KillSwitch enforcement gaps; 4-plane governance non-composition | Contract at Rigby's reach for each governance plane |
| **Group 2400 Auth (S2499)** | P1 primary input | Session lifecycle + silent-401 SYSTEMIC + trust-boundary carriage; canonical verdict *"ACCRETION with declared-but-unenforced contracts"* | Rigby-specific session-carriage discipline |
| **Group 2100 RAG (S2199) + I-0200 (S2701)** | P3 primary input | Corpus governance; ADR-0004 PROVISIONAL maturity gradient; provenance carriage into retrieved evidence | Rigby's authority to trust retrieved evidence + freshness invariants |
| **Group 1300 Memory (S1399)** | P3 primary input | 5+ memory stores; consolidation contract unclear | Rigby's access invariants for memory |
| **Group 1700 Observability (S1799) + I-0100 (S2700)** | P4 + X-OBSERVABILITY primary input | 5 parallel telemetry layers; RIGBY_EVENT_INTAKE_ENABLED=false; trace_id write-side fix; RIGBY_DELEGATION staged unlock | Per-category telemetry-emission invariants |
| **Group 2000+ Event/Integration (S2099)** | P2 primary input | Tool→handler contract emission; envelope discipline (`ui.render_hint`); F.PER-USER-AUTHORITY emission wiring | Per-capability event-emission contracts at Rigby's reach |
| **Group 1800 HumanAttention (S1899)** | Adjacent | HAI event schema; when Rigby raises HAI items | HAI raise-authority as a Rigby operational contract |
| **Group 2500 API (S2599)** | Adjacent | Contract SoT + drf-spectacular sports-only partial-wiring + REST↔WS T7 | Rigby's use of API contracts as reach targets |
| **Group 2200 Frontend (S2299)** | Adjacent | Workspace-context resolver from client side; silent-401 SYSTEMIC frontend-side | Client-injected context reception invariants |
| **Cross-Domain Audit §14** | Meta-baseline | §14.16 PA integration + §14.15 API + 12 domain refresh entries | Aggregation into inward-facing contract statement |

---

## 9. Phase 7 existing constitutional documents that govern portions

| Document | Governance scope | Current maturity | Relationship to this arc |
|---|---|---|---|
| Playbook v0.1.0 Ch 5 (STUB) | PA/Rigby collaboration; rules 5.1.1, 5.2.1, 5.3.1 | STUB; §5.5 lists 4 extension points | **Primary constitutional home candidate** |
| Playbook Ch 6 PIC-10 (FULL) | X-PROVENANCE cross-cutting attribute | FULL | Cross-cutting invariant; applies inside every arc output |
| Playbook Ch 9 (STUB) | Recovery playbooks | STUB | Secondary constitutional home for P4 outputs beyond Rigby scope |
| Playbook Ch 8 (STUB) | Runtime discipline | STUB | Adjacent for X-COST-BOUND cross-cutting |
| Playbook Ch 10 (FULL) | Evolution and amendment | FULL | Governs how any amendments this arc proposes get authored, reviewed, ratified |
| MEMORY.md | ~90 feedback rules; de-facto operational-contract layer | Living; authoritative-by-reference via Ch 5.2.1 | **Primary evidence base**; potential subject of promotion into Ch 5 |
| UDB_BEHAVIOR_LAYER.md | Rigby's voice/substance discipline at LLM surface | Active | Adjacent; not overlapping |
| UDB_TRANSLATION_LAYER.md | Persona-based framing shifts | Active | Adjacent; not overlapping |
| CLAUDE.md | Session-open guidance for Claude; Rigby-first comms | Active | Anchors caller-side collaboration; adjacent |
| `docs/topics/personal-assistant.md` | Current-state PA topic doc | Drifts (DOC-POINTER-V1 warned) | Documentary evidence with known drift |
| Group 2699 PA canonical summary | Outward-facing PA contract-plane verdict | Closed 2026-07-06 | Complement to this arc |
| I-0100 close doc | RIGBY_DELEGATION_ENABLED flag guardrail | Closed 2026-07-07 | Direct P4 + X-OBSERVABILITY input |
| I-0200 close doc + ADR-0004 PROVISIONAL | RAG corpus substrate maturity gradient | Closed 2026-07-07 | Direct P3 input |
| Cross-Domain Audit §14.16 | PA cross-domain integration | Refreshed 2026-07-06 | Aggregation baseline |

**Constitutional home decision (deferred to arc close):** whether the arc's output belongs (a) in Ch 5 (chapter-scale MINOR amendment; possibly promoting STUB → FULL), (b) as standalone ADRs referencing Ch 5 §5.5 as extension-point home, or (c) as a new companion layer doc parallel to `UDB_BEHAVIOR_LAYER.md` / `UDB_TRANSLATION_LAYER.md` (candidate name: `UDB_OPERATIONAL_CONTRACT_LAYER.md`).

---

## 10. Phase 8 evidence base already in-repo

**MEMORY.md ~90 feedback rules** — the observed-behavior corpus for this domain (largest single evidence pool; auto-loaded on every session).

**Prior arc close docs (12 arcs + 2 implementation arcs)** — all directly usable:
- `docs/research/domains/pa/2699_pa_canonical_summary.md`
- `docs/research/domains/api/2599_api_canonical_summary.md`
- `docs/research/domains/auth/2499_auth_canonical_summary.md`
- `docs/research/domains/frontend/2299_frontend_canonical_summary.md`
- `docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md`
- `docs/research/domains/event_integration_architecture/2099_event_integration_architecture_canonical_summary.md`
- Groups 1300 / 1500 / 1600 / 1700 / 1800 / 1900 xx99 summaries
- `docs/research/implementation/observability_spine_mission_evidence_substrate/I-010099_*.md`
- `docs/research/implementation/rag_corpus_substrate_maturity/I-020099_*.md`

**Cross-Domain Integration Audit §14** — 12 refresh entries + baseline.

**Runtime code at HEAD `9d158805`:**
- `core/services/unified_pa_entrypoint.py` (7,613 lines)
- `core/services/tool_dispatcher.py` (156 handlers)
- `core/services/pa_tool_schemas.py` (113 schemas)
- 8 enrichment service modules
- `core/agent_router.py` (AGENT_MAP + routing)
- `core/epa_handlers_tools.py` (WORKSPACE_AWARE_AGENTS)
- `core/agents/base_agent.py` (`execute_with_workspace`)
- `core/workspace_manager.py` (`get_active_workspace`)

**PLATFORM_INVENTORY autoblock** — runtime counts, last regenerated 2026-07-05.

**Playbook v0.1.0 body** — 1,249 lines; Chapter 5 STUB is 27 lines (§5.1–§5.5).

**Consequence for arc discipline:** primary evidence collection is estimated at 20-30% of arc work. Aggregation, gap detection, and constitutional statement authoring are 70-80%. This differs from prior domain-scoping arcs which were more primary-evidence-collection-heavy (e.g., Groups 1500 Sports, 1600 Content).

---

## 11. Phase 9 proposed research decomposition (candidate)

**Parent arc:** Tools / PA Operational Contracts

**Directory (proposed):** `docs/research/tools/` — parallel to `docs/research/platform/` per Chris's directive.

**Note on directory placement:** the standard playbook §11 pattern places domain research under `docs/research/domains/<slug>/`. Chris's directive places this arc under `docs/research/tools/` at the same level as `docs/research/platform/`. This treats the arc's constitutional weight as platform-scope, not domain-scope — analogous to how `platform/` produced the Engineering Playbook. The naming is Chris-locked; the child docs still follow the `NN00_/NN01_/NN02_/…/NN99_` convention within.

**Proposed session sequence (candidate; awaits ratification):**

- **S2728 P0 parent scoping** — `tools/tools_operational_contract_domain_definition.md` (this document) + a subsequent `tools_domain_scoping.md` post-review if Chris ratifies the decomposition.
- **S2729 P1 Cat A AUTHORITY-CARRIAGE** — Actor identity + workspace-scope + authority conveyance from caller through Rigby's turn into every capability call.
- **S2730 P2 Cat B CAPABILITY-CONTRACT** — Tool schema → handler contract shape; typed vs silent errors; default-value discipline; discovery model; safe-default posture.
- **S2731 P3 Cat C KNOWLEDGE-SUBSTRATE** — Rigby's access model to the corpus (RAG, KB, docs cascade); provenance-class carriage; freshness thresholds; staleness detection.
- **S2732 P4 Cat D FAILURE-AND-RECOVERY** — Failure classification standard + recovery playbook set for Rigby↔capability reaches.
- **S2733 P5 Cat E VERIFIER-LOOP** — Constitutional posture of "Claude directs, Rigby executes, Claude verifies" + exceptions + verifier obligations.
- **S2799 xx99 canonical summary** — playbook §11.3 THIRTEENTH-consecutive-candidate application; meta-methodology §10.

**Runtime target:** 6 sessions (parent + 5 children + xx99). Cap: 8. Matches the seven-consecutive prior parent-with-4-children arc precedent extended by one child.

**Meta-methodology observations if runtime target holds:**
- **MC-4** (arc-pin routing arc-standard for parent-with-N-children) would extend from CODIFICATION-CONFIRMED-with-scope-guardrails through an EIGHTH-consecutive application — the first stress-test with a 5-child rather than 4-child arc.
- **MC-5** (playbook §11.2 20-section child template) would extend by 5 more consecutive applications.
- **MC-3** (canonical summary count) would advance from 12 to 13.

**Candidate meta-observations from this Phase 0:**
- **MC-tools-1 CANDIDATE:** unification arcs (arcs where primary evidence is already in prior closed arcs) may need a modified §11.2 child template emphasizing aggregation + gap-detection rather than primary discovery. First observation; requires second arc for two-triggers threshold.
- **MC-tools-2 CANDIDATE:** cross-cutting-attribute treatment (Freshness / Provenance / Observability / Default-Behavior applied inside each primary category) may be a durable pattern candidate. First observation.

**Anti-scope (for parent scoping to codify if Chris ratifies):**
- No changes to `/api/pa/chat/` endpoint contract (2600 owned).
- No changes to PA-client typed contract surface (2600 owned).
- No changes to LLM voice or persona (UDB layers own).
- No implementation, no ADR authoring, no Playbook amendment inside this arc. Outputs are research + fold recommendations. Amendments follow Playbook Ch 10 lifecycle, post-arc.
- No cross-repo federated Rigby (parked per MEMORY project note).
- No individual capability correctness audit (each capability arc owns).
- No changes to MEMORY.md content inside this arc (evidence base preservation).

**Alternative decompositions considered and rejected at Phase 0** (surfaced for Chris to pressure-test):
- **Fold P5 into P4.** Rejected — would lose the ratified §5.2.1 anchor; verifier-loop is the only category with existing constitutional weight.
- **Split P3 into P3a Knowledge Retrieval + P3b Repository/Workspace Truth.** Rejected — evidence suggests they compose (workspace_id is one dimension of retrieval authority).
- **Add P6 Multi-agent authoring coordination.** Rejected — Ch 5 §5.5 extension point presumes >1 concurrent agent; Rigby is currently the only one. Park until second agent surfaces.
- **Convert to single mega-audit (no children).** Rejected — evidence volume argues against; 5 primary categories carry independent constitutional weight.
- **Open as 4-child arc matching seven prior parent-with-4-children precedent.** Rejected — collapsing P5 into P4 or P1 loses ratified anchor at §5.2.1; the 5th child is worth the extension.

---

## 12. Risks

**R1. Constitutional-home ambiguity risks a pre-committed structure.** Ch 5 is currently STUB; growing it to FULL via MINOR amendments is one path; spinning off a companion layer doc is another; using standalone ADRs is a third. If the arc pre-commits to any of the three at Phase 0, it forecloses a valid alternative before evidence supports the choice. Mitigation: hold constitutional-home decision at arc close (xx99), not at Phase 0 or child open.

**R2. MEMORY.md rules are observed, not constitutional — promoting them naïvely could lose their evolutionary character.** MEMORY.md is a living failure-mode + success-mode corpus. Constitutionalizing it wholesale would freeze it. Constitutionalizing subsets would need discipline for which rules stay in MEMORY and which get promoted. Mitigation: the arc must characterize the promotion pathway alongside any promotion candidates.

**R3. 12+ prior arcs overlap this domain — coordination cost is high.** Unification arcs risk (a) re-litigating prior arc decisions, (b) missing prior arc cross-cutting handoff items already routed elsewhere, (c) inheriting stale numbers from arcs whose evidence has moved. Mitigation: parent scoping doc must include a cross-arc handoff register with explicit T-slot ownership.

**R4. The 113/156 schema/handler ratio may be intentional AND drift.** Not one or the other. Some undeclared handlers are internal (called by other handlers); some are intentionally gated from LLM access; some are drift from removed schemas that lost their declaration. The arc must characterize each of the 43 non-schema-declared handlers before proposing what the ratio "should" be. Naïve reconciliation would ratify drift as intent.

**R5. Chris's "assume many current assumptions are incorrect" framing means MEMORY.md rules may themselves be wrong at HEAD.** The arc must re-verify each cited MEMORY rule against current runtime state before treating it as evidence. Some rules have been superseded by fixes (S1249 URL trap fix superseded parts of `feedback_pa_chat_local_override`). Mitigation: verifier-loop per rule, per child audit.

**R6. Rigby's constitutional posture is dual — she is both a subject of the operational contract (an agent bound by it) and an executor of the arc's research (SIGN cycles on the arc's outputs).** She reviews rules that constrain her. Playbook §5.2.1 already ratifies this posture; the arc must not naïvely propose changes that break it.

**R7. Playbook v0.1.1 PATCH work (CD-48 + CD-49) is queued.** If v0.1.1 lands during this arc, Ch 5 §-numbering may drift. Mitigation: coordinate arc timing with Chris; if v0.1.1 opens mid-arc, arc pauses per playbook §16 arc-standard.

**R8. Runtime target 6 sessions with 5-child structure is untested precedent.** MC-4 through seven prior arcs is 4-child-shaped. Extending to 5 children may reveal template-application friction; may require §11.2 template adjustment mid-arc. Mitigation: parent scoping doc's §16 arc-standard section names contingency (fall back to 4-child if P5 collapse becomes correct mid-arc).

---

## 13. Unknowns

**U1.** Whether the 5-child structure is the correct decomposition or whether evidence collection will merge P1↔P2 (authority is a special case of capability contract) or split P3 (knowledge substrate too large for one child audit).

**U2.** Whether MEMORY.md should be constitutionally promoted (specific rules ratified into Ch 5) or preserved as living observed-behavior corpus. Ch 5.2.1 currently makes MEMORY.md authoritative-by-reference — Chris may or may not want that to persist.

**U3.** Whether the constitutional output belongs in Ch 5 (chapter-scale MINOR), standalone ADRs referencing Ch 5 §5.5, or a companion layer doc. Precedent supports all three.

**U4.** Whether P5 (Verifier-Loop) should also touch Ch 5 §5.2.1 as an amendment or leave §5.2.1 stable and add §5.4+.

**U5.** Whether Playbook Ch 9 (STUB Recovery Playbooks) is the correct secondary home for P4 outputs that go beyond Rigby scope, or whether P4 stays scoped to Rigby-only and Ch 9 is left for a future non-PA recovery arc.

**U6.** Whether the 43-handler gap (156 handlers − 113 schemas) is intentional, drift, internal, or a mix. Enumeration required.

**U7.** Whether cross-cutting attributes (X-FRESHNESS / X-PROVENANCE / X-OBSERVABILITY / X-DEFAULT-BEHAVIOR / X-COST-BOUND) should be captured inside each primary category's child audit or lifted to the xx99 canonical summary as arc-wide invariants.

**U8.** Whether this arc opens at S2728 (the next natural session number) or whether Chris ratifies at a different opening — arc-open timing is Chris-gated.

**U9.** Whether the constitutional weight this arc produces is significant enough to be a **Cycle 2** substrate (per 2712 §17 Cycle 2 hardening candidate priorities) or a MINOR-amendment cluster inside the existing Playbook.

**U10.** Whether "PA Operational Contracts" is the right domain name, or "Tools Operational Contracts" (per directory placement), or "Agent-Capability Contracts" (per constitutional-generality preference), or something else. Chris-locked directory is `tools/`; body-name is unresolved.

---

## 14. What this document explicitly does not do

- Does NOT propose architecture. No Options A/B/C. No recommendation.
- Does NOT author Tool Contracts.
- Does NOT open the arc (no `OPEN_ARCS.md` row; no arc pin mint; no scoping doc creation; no directory beyond `docs/research/tools/`).
- Does NOT route to Rigby (no SIGN pass; wrong phase; Rigby is subject of the arc as well as reviewer of its outputs).
- Does NOT propose amendments to Playbook Ch 5 (constitutional-home decision deferred to arc close).
- Does NOT propose promotion of any MEMORY.md rule (promotion-pathway characterization is part of the arc's work, not this document).
- Does NOT propose changes to any prior-arc output.
- Does NOT create workspace deliverables.
- Does NOT run docs cascade (no doc changes to sync).
- Does NOT flip any feature flag or make any runtime change.

**This document is a Phase 0 domain definition. It waits for Chris to ratify, modify, or reject the proposed decomposition before any subsequent research or authoring proceeds.**
