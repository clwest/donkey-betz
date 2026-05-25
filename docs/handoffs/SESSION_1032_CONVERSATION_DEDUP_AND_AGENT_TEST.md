---
originating_session: 1032
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1032 — Conversation Dedup & 79-Agent Stress Test

**Date:** February 18, 2026
**Focus:** Fuzzy conversation deduplication, router-level agent blocking, agent failure messages, comprehensive agent stress test

## Conversation Dedup

**Problem:** 12 identical AgentConversation records for "Analyze competitor content on the candidate topics" — each a standalone conversation starting from scratch. System spawned the same topic as different types (Discussion, Panel, brainstorm, devils_advocate) with different agent pairs.

**Root cause:** Dedup checked exact `topic` match but "Discussion: X" never matched "Panel: X". `DeduplicationService.find_similar_conversation()` (Session 549) already existed with prefix stripping and Jaccard similarity, but was never called.

**Fix:** Wired existing `find_similar_conversation()` into both `run_agent_conversation` and `run_multi_agent_conversation` in `core/tasks.py`. Extended window from 6h to 48h. Added continuity injection — when a conversation IS allowed (topic not seen in 48h), prior conclusions are injected so agents build on past work.

## Router-Level Agent Blocking

Added `_NON_SPECIALIST` routing override in `AgentRouter.route()` — pattern-matches specialist tasks and reroutes from non-specialist agents (WorkflowAgent, VideoAgent, etc.) to correct specialists.

## 79-Agent Stress Test

Comprehensive test of all routable agents: **73 PASS, 6 FAIL (92.4% pass rate)**. Each agent tested with realistic task + context via `AgentRouter.route()`. All failures were pre-existing issues (missing API keys, external service quotas), not code bugs.

## Agent Failure Message Fixes

4 agents had incorrect error patterns:
- Agents calling `WebSearchTool.search()` instead of `.execute()`
- Missing evidence normalization for `web_search` returns (dict with `results` key, not a list)
