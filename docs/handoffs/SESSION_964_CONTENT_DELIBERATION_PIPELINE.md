---
originating_session: 964
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 964: Phase 4 — Multi-Agent Content Deliberation Pipeline

**Date:** February 7, 2026
**Status:** Complete
**Branch:** main

---

## Problem Statement

Content generation via `ContentWriterAgent` had no deliberation persistence. The Session 961 review panel worked but produced no evidence pack, no trace, no claim tracking, and no structured reviewer output. Blog posts were published without formal review accountability.

---

## What Was Built

### Full Deliberation Pipeline (v2 path, old flow untouched)

**Spider signals -> ClaimsPack -> ContentWriter draft (citing claims) -> 3-reviewer panel -> DecisionEnforcer (PUBLISH/REVISE/KILL) -> PublishGate -> SelfBlog with `stats_snapshot['deliberation']`**

### 1. Content Claims System (`content_claims.py`)

| Component | Purpose |
|-----------|---------|
| `SpiderClaim` dataclass | Single sourced claim with deterministic ID, confidence, type |
| `ClaimsPack` dataclass | Bundle of claims with `to_prompt_block()`, `to_evidence_sources()`, `to_evidence_claims()` |
| `make_claim_id()` | Deterministic: `C-` + sha256(normalized_url + title)[:10] |

### 2. Claims Pack Builder (`claims_pack_builder.py`)

Queries two sources in priority order:
- **SpiderData** (last 72h) — iterates `raw_data['items']`, extracts description/summary as factual claims (0.7 confidence) or title-only as speculative (0.3)
- **SignalCluster** (active) — extracts `sample_signals` as speculative claims (0.4 confidence)

Topic matching: tokenize topic (words >3 chars), filter by token match. Dedup by normalized URL. Freshness-sorted.

### 3. Content Review Panel v2 (`content_review_panel_v2.py`)

3 structured reviewers (existing `content_review_panel.py` untouched):

| Reviewer | Trigger | Focus |
|----------|---------|-------|
| `SkepticReviewer` | Always | Claims without evidence, generic filler, hallucination risk |
| `FactCheckReviewer` | Always | Claim ID → URL mapping, freshness, unsourced assertions |
| `DomainPersonaReviewer` | 0-1, by domain | Domain-specific accuracy and depth |

**Structured output:** JSON with `reviewer`, `verdict` (PASS/REVISE/FAIL), `top_issues`, `required_changes`, `suggested_edits`, `confidence`.

**Validation failure → synthetic FAIL payload** (not skip) so DecisionEnforcer sees it.

### 4. Content Deliberation Runner (`content_deliberation_runner.py`)

Full pipeline with graceful degradation (every step try/except):

| Step | Action | Failure Mode |
|------|--------|-------------|
| 1 | Build ClaimsPack | Empty claims, continue |
| 2 | Draft via ContentWriterAgent | Return early |
| 3 | Review conversation via ConversationOrchestrator | Draft with 'panel_failed' |
| 4 | Extract decision from ExecutionMandate | Default REVISE |
| 5 | If REVISE: one rewrite pass | Use original draft |
| 6 | Append claims to evidence pack | Skip silently |
| 7 | Save SelfBlog with deliberation metadata | Return early |
| 8 | PublishGate (only if PUBLISH) | Draft fallback |

**Status mapping:**
- PUBLISH + gate pass → `status='pending_review'`, `content_type='public'`
- PUBLISH + gate fail → `status='draft'`, gate_notes from PublishGate
- REVISE → `status='draft'`
- KILL → `status='draft'`, `content_type='internal'`
- All reviewers fail → `status='draft'`, `gate_notes='panel_failed'`

### 5. Celery Task + API Endpoint

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/research/self-blog/generate-v2/` | Dispatches `generate_self_blog_deliberation_task` |
| `GET /api/blog/<uuid>/deliberation/` | Returns full deliberation replay for a blog |

### 6. ContentWriterAgent Enhancement

Added optional `claims_block` parameter to `_build_content_prompt()` that appends citation rules for `[C-xxxxxxxxxx]` inline markers.

---

## Files

### New Files (5)

| File | Lines | Purpose |
|------|-------|---------|
| `core/services/content_claims.py` | ~100 | SpiderClaim + ClaimsPack dataclasses |
| `core/services/claims_pack_builder.py` | ~210 | Builds ClaimsPack from SpiderData + SignalCluster |
| `core/services/content_review_panel_v2.py` | ~210 | 3 structured reviewers with LLM + validation |
| `core/services/content_deliberation_runner.py` | ~310 | Full pipeline runner |
| `core/tests/test_phase4_content_deliberation.py` | ~250 | 8 tests |

### Modified Files (4)

| File | Changes |
|------|---------|
| `core/agents/content_writer_agent.py` | Added `claims_block` param to `_build_content_prompt()` |
| `core/tasks.py` | Added `generate_self_blog_deliberation_task` Celery task |
| `core/urls.py` | Added 2 URL routes |
| `core/views_deliberation.py` | Added `blog_deliberation_detail()` view |
| `core/views_research_demo.py` | Added `generate_v2_blog_api()` view |

### Existing Infrastructure Reused (not modified)

| Component | File |
|-----------|------|
| ConversationOrchestrator | `conversation_orchestrator.py` |
| EvidencePackBuilder | `evidence_pack_builder.py` |
| SessionTraceBuilder | `session_trace_builder.py` |
| DeliberationSession/Turn/ContractRecord | `models_deliberation.py` |
| DecisionEnforcerAgent | `decision_enforcer_agent.py` |
| PublishGate | `publish_gate.py` |
| DomainContentContextBuilder | `domain_content_context.py` |

---

## Testing

- **8/8 Phase 4 tests pass** (claims, determinism, prompt block, validation, reviewer failure, deliberation flow, graceful degradation)
- **45/45 Phase 2 regression tests pass**
- No migrations needed — deliberation metadata stored in existing `stats_snapshot` JSONField

---

## Architecture Decisions

1. **Parallel v2 path** — old flow completely untouched, can A/B test v1 vs v2
2. **stats_snapshot['deliberation'] dict** — no FK migration needed for deliberation metadata
3. **KILL → still creates SelfBlog** as `status='draft'`, `content_type='internal'` for audit trail
4. **Reviewer validation failure → FAIL verdict** so DecisionEnforcer sees the failure explicitly
5. **Deterministic claim IDs** — `C-` + sha256(normalized_url + title)[:10] for cross-reference
6. **ConversationOrchestrator reuse** — gets session/turn/evidence/trace persistence for free
