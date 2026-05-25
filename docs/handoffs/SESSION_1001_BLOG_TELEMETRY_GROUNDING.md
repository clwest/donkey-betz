---
originating_session: 1001
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1001: Ground Blog Generation in Real Telemetry Data

**Date:** February 13, 2026
**Focus:** Inject real operational data into blog generation so ContentWriterAgent cites verifiable metrics instead of fabricating claims

## Problem

ContentWriterAgent generates blog posts from thin research (a headline + 500-char snippet + aggregate counts) and is prompted to "expand with your own insights." It fabricates specific operational claims ("hit a wall last Tuesday," "diagnosed in 200ms," "processed thousands of decisions") because it has no real telemetry to cite. Deliberation reviewers catch the worst offenders (all 3 reviewers voted REVISE on fabricated blogs), but 3,896 drafts sit with unverifiable claims. Zero blogs have a `trace_id` linking to real events.

## Changes

### 1. New function: `_build_operational_context()` (core/tasks.py)

~100-line standalone function that queries 4 telemetry models and returns a markdown string:

| Section | Model | Data |
|---------|-------|------|
| Agent Executions (72h) | `AgentExecution` | Total/completed/failed, success rate, avg execution time, 3 recent with agent name + task + timing |
| Background Tasks (72h) | `CeleryTaskEvent` | Total/success/failure, reliability %, avg duration, top 3 failing task names |
| System Health | `HeartBeat` | Latest score, status, component breakdown |
| Recent Decisions | `AgentDecisionSummary` | 3 recent with topic, stance, insights, participants |

Each section in its own try/except for graceful degradation. Returns `""` on total failure. Header: `## Operational Telemetry (Real Data -- cite these, do not invent)`.

### 2. Pipeline 1 injection (core/tasks.py)

After all topic-category blog_research assembly completes, appends `_build_operational_context()` output to `blog_research`. This ensures every self-blog has real operational data to cite regardless of topic category (trending, dreams, conversations, system).

### 3. Prompt language fixes (core/tasks.py)

Replaced 3 confabulation-encouraging lines:

| Before | After |
|--------|-------|
| "Add your own analysis and perspective. Make it valuable to readers." | "Ground all claims in the data provided above. Do not invent operational statistics or fabricate specific incidents." |
| "...expand on it with your own insights. Make it valuable, not just a summary." | "...Ground all claims in the provided research and telemetry. Make it valuable and specific, not generic." |
| "...add your own perspective, and make it thought-provoking." | "...Explore the themes using the operational data provided, and make it thought-provoking." |

### 4. Anti-fabrication prompt (core/agents/content_writer_agent.py)

Added 2 new bullet points to `## IMPORTANT` section in `_build_content_prompt()`:
- "When referencing operational metrics, use ONLY exact numbers from the Operational Telemetry section"
- "Do NOT fabricate specific incidents, error messages, or recovery narratives"

Changed "Include practical examples and actionable insights where appropriate" to "Include practical examples from the provided data where appropriate".

### 5. Pipeline 2 injection (core/services/content_deliberation_runner.py)

In `_generate_draft()`, after claims_pack research assembly, appends operational context via runtime import from `core.tasks`. No circular import risk (same pattern as existing runtime imports).

## Files Changed (3)

| File | Lines | Change |
|------|-------|--------|
| `core/tasks.py` | +~108 | `_build_operational_context()`, Pipeline 1 injection, 3 prompt fixes |
| `core/agents/content_writer_agent.py` | +2, ~1 edit | Anti-fabrication bullets in IMPORTANT section |
| `core/services/content_deliberation_runner.py` | +7 | Pipeline 2 operational context injection |

## Verification

- `python -c "import core.tasks"` -- no import errors
- `_build_operational_context()` returns real markdown with agent execution stats, health scores, and decision summaries
- CeleryTaskEvent gracefully skipped locally (table only on Railway) -- works in production
