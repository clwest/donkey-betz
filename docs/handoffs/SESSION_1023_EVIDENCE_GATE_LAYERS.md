---
originating_session: 1023
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1023 — Evidence Gate Layers 1-3

**Date:** February 16, 2026
**PRs:** #1262, #1263, #1264

## Problem

Agents synthesize "beautiful nonsense" — structured JSON analysis from zero-relevance spider data. A HuggingFace ML page mentioning "blockchain" in a tag scored `relevance=1.0` for blockchain queries, and agents produced confident-looking reports grounded on this irrelevant data.

## Changes

### Layer 1: CompetitorAnalysisAgent (PR #1262)

**File:** `core/agents/business/competitor_analysis_agent.py`

Added two hard gates in `_synthesize_analysis()` before the LLM call:
1. `< 3` data points total -> return `insufficient_evidence`
2. `0` domain-relevant items when domain_tags exist and score < 15% -> return `insufficient_evidence`

`execute()` checks `synthesis.get('status') == 'insufficient_evidence'` and returns a proper AgentResult instead of hallucinated analysis.

### Layer 2: BaseBusinessResearchAgent (PR #1263)

**File:** `core/agents/business/base_business_research_agent.py`

Added evidence gate after `_execute_gpt_loop()` returns. Affects all subclasses: `ContentStrategyAgent`, `MarketingStrategyAgent`. Same domain relevance scoring logic as Layer 1.

### Layer 3: build_provenance() Infrastructure (PR #1264)

**File:** `core/agents/report_schemas.py`

Added two new optional params to `build_provenance()`:
- `min_source_records: int = 0` — gate on minimum record count
- `domain_match_rate: Optional[float] = None` — gate on domain relevance (< 15% blocks publishing)

Added `domain_match_rate` field to `ReportProvenance` dataclass with serialization and markdown output. Backward-compatible — existing callers pass no new args, behavior unchanged.

**Layer 3b (future):** Per-agent adoption — each of 20+ provenance-tracked agents should compute and pass `domain_match_rate`.

## Testing

All 3 layers verified on Railway. CompetitorAnalysisAgent returns `insufficient_evidence` when given irrelevant spider data instead of hallucinating analysis.
