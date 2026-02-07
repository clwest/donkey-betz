# Session 961 - Start Here

**Previous Session:** 960 (Phase 0 Connectors + AgentOutputEnvelope)
**Date:** February 7, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **166 INITIATIVES** | **Risk-Aware RAG: COMPLETE** | **Doc Classification: 562 DOCS** | **Boardroom ML: ACTIVE** | **Unified PA: ANALYTICAL ADVISOR** | **Voice System: COMPLETE** | **Learning Loop: REFINED** | **Agent Provenance: 26+ AGENTS** | **RAG Observability UI: COMPLETE** | **PA Intelligence Enrichment: ACTIVE** | **Phase 0 Connectors: COMPLETE**

---

## Session 960 Summary (Just Completed)

### Phase 0: Connectors Only - COMPLETE (22 tests passing, Railway verified)

Implemented lightweight connectors between existing subsystems. No new Django models, no migrations, all changes additive and backward-compatible.

#### What Was Built

| Phase | Component | Summary |
|-------|-----------|---------|
| **0.1** | SourceInfo + Claim extensions | `source_type`, `content_hash` on SourceInfo; `claim_id`, `source_ids`, `challenged_by`, `status` on Claim |
| **0.2** | BaseAgent doc tracking | `_docs_consumed` list, `get_docs_consumed()`, SHA-256 hashing in `_read_doc()` |
| **0.3** | Provenance merging | `build_provenance()` accepts `internal_sources` (SourceInfo or dict), merges into provenance |
| **0.4** | Contract serialization | Already existed - all 3 contracts have `to_dict()`. Tests added. |
| **0.5** | DecisionEnforcer fallback | Auto-triggers for debate/planning/critique when no `decision_summary` extracted |
| **0.6** | Strategic Memory enrichment | `LearningPatternEngine` wired into PA `reasoning` intent via `strategic_memory` key |
| **0.A-B** | AgentOutputEnvelope | New schema + `validate_envelope()` with CitationGateService integration |
| **0.C** | PublishGate integration | `_check_envelope()` validates envelope in blog metadata |
| **0.D** | Tests | 22 tests across 5 test classes |

**Files Modified:**
| File | Changes |
|------|---------|
| `core/agents/report_schemas.py` | SourceInfo + Claim extensions, build_provenance internal_sources |
| `core/agents/base_agent.py` | _docs_consumed tracking, get_docs_consumed(), _read_doc() instrumentation |
| `core/conversation_orchestrator.py` | Fallback DecisionEnforcer auto-trigger |
| `core/services/unified_pa_entrypoint.py` | Strategic memory enrichment for reasoning intent |
| `core/services/artifact_envelope.py` | **NEW** - AgentOutputEnvelope schema + validation |
| `core/services/publish_gate.py` | _check_envelope() integration |
| `core/tests/test_phase0_connectors.py` | **NEW** - 22 tests |
| `docs/audits/PHASE0_APPLIED_NOTES.md` | **NEW** - Full implementation notes |

---

## What Phase 0 Enables (Next Steps)

Phase 0 laid the connectors. Phase 1-3 from `docs/audits/SURGICAL_MOVES_UNIFICATION_AUDIT.md` can now build on them:

### Phase 1: Docs as First-Class Cognitive Organ
- Internal doc reads are now tracked (`get_docs_consumed()`)
- Provenance can merge internal sources (`build_provenance(internal_sources=...)`)
- **Next:** Wire doc reads into agent execute() flows, add doc versioning

### Phase 2: Deliberation Sessions
- DecisionEnforcer now auto-triggers for debates without summaries
- Contracts have serialization for JSON storage
- **Next:** Build DeliberationSession model or use existing JSON fields

### Phase 3: Strategic Memory Layer
- PA reasoning intent now pulls learning patterns
- **Next:** Expand to other intents, add memory write-back from PA interactions

### AgentOutputEnvelope Pipeline
- Envelope schema defined with claims, citations, internal refs
- PublishGate checks for envelope in blog metadata
- **Next:** Wire ContentWriterAgent to produce envelopes, populate paragraph citations

---

## PRIORITY OPTIONS FOR NEXT SESSION

### Option A: Multi-Agent Content Review Panel (HIGH IMPACT)
Wire persona agents + advisors into a post-generation content review step:
- Inject domain-specific spider data into persona review prompts
- Expert personas challenge weak claims, suggest missing data
- Advisor frameworks apply quality lenses
- DecisionEnforcer decides: publish, revise, or kill
- **Key files:** `content_writer_agent.py`, `persona_agent_context.py`, `conversation_orchestrator.py`

### Option B: ConceptForge → Content Pipeline Connection
Wire ConceptForge dossier output into ContentWriterAgent prompts:
- When ConceptForge completes a dossier, feed insights into content generation
- Structured claims from research stage become content anchors
- **Key files:** `core/conceptforge/orchestrator.py`, `content_writer_agent.py`

### Option C: Spider Data → Structured Claims
Transform spider data from vague summaries to structured source claims:
- Spider results with URLs, dates, authors, specific claims
- Citation injection at generation time (not just context)
- Confidence scoring per paragraph based on source count
- **Key files:** `spider_context_builder.py`, `content_writer_agent.py`

### Option D: Wire ContentWriterAgent → AgentOutputEnvelope
- Have ContentWriterAgent produce envelopes with claims and paragraph citations
- Populate internal_refs from `get_docs_consumed()`
- Run `validate_envelope()` before saving to SelfBlog
- Store envelope in blog metadata JSON field
- **Key files:** `content_writer_agent.py`, `artifact_envelope.py`, `publish_gate.py`

### Option J: Critical Docs Management UI
### Option K: RAG Retrieval Analytics
### Option L: Provenance Dashboard

---

## Recent Session History

| Session | Focus | PRs |
|---------|-------|-----|
| **960** | Phase 0 Connectors - SourceInfo/Claim extensions, doc tracking, DecisionEnforcer fallback, strategic memory, AgentOutputEnvelope | - |
| **959** | PA Intelligence Upgrade - Analytical advisor with enrichment pipeline | #954 |
| **957** | RAG Observability Frontend - Complete UI dashboard for risk-aware RAG system | #943 |
| **954-956** | Doc Classification + Boardroom ML + Initiative Cleanup + Learning Loop + RAG Observability + Provenance Extension + ML UI + Learning UI | #935-#942 |
| **953** | Agent Provenance Expansion - 18 agents with provenance tracking | - |
| **952** | Narrative Injection Enhancement - Topic filtering, diversity, fallbacks | #929, #930 |
| **951** | PA Platform Query Tool - Query deliverables, reports, initiatives | #929 |
| **950** | Kalshi Sports Categorization + Workspace Scroll + Stock Analysis Fix | #924, #926, #927 |
| **949** | Risk-Aware RAG - Dual-channel retrieval, RESERVED budget, risk re-ranking | #920, #921, #922 |

---

## Key Files Reference

### Session 960 - Phase 0 Connectors
| File | Purpose |
|------|---------|
| `core/agents/report_schemas.py` | SourceInfo/Claim extensions, build_provenance with internal_sources |
| `core/agents/base_agent.py` | _docs_consumed tracking in _read_doc() |
| `core/services/artifact_envelope.py` | AgentOutputEnvelope schema + validate_envelope() |
| `core/services/publish_gate.py` | _check_envelope() integration |
| `core/conversation_orchestrator.py` | DecisionEnforcer fallback auto-trigger |
| `core/services/unified_pa_entrypoint.py` | Strategic memory enrichment |
| `docs/audits/PHASE0_APPLIED_NOTES.md` | Full implementation notes |
| `docs/audits/SURGICAL_MOVES_UNIFICATION_AUDIT.md` | Master audit document |

### Agent Collaboration Architecture (Reference)
| File | Purpose |
|------|---------|
| `core/services/persona_agent_context.py` | Maps 139 persona agents to spider data via PERSONA_SPIDER_MAPPINGS |
| `core/conceptforge/orchestrator.py` | 6-stage pipeline with persona + advisor integration |
| `core/conceptforge/panels.py` | 25 legendary advisor profiles + debate pairs |
| `core/conversation_orchestrator.py` | Multi-agent debates with tension enforcement |
| `core/agents/decision_enforcer_agent.py` | Forces decisions after debate (banned hedging phrases) |
| `core/agents/content_writer_agent.py` | Content generation with 10-layer prompt assembly |
| `core/services/publish_gate.py` | Quality thresholds: 0.75 quality, 0.6 novelty, 0.55 structure |

---

**Session 961 Focus: Choose from Options A, B, C, D above (multi-agent content improvement / envelope wiring) or J, K, L (UI improvements)!**
