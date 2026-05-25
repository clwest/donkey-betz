---
originating_session: 1021
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1021 - Initiative Pipeline Integrity

**Date:** February 16, 2026
**PRs:** #1250, #1251, #1252

## Problems

### 1. DRAFT Stages with Documents Silently Skipped (PR #1250)
After Session 1020's Stage 2+ document creation fix, stages had `status='DRAFT'` with a valid `document_id`. But `advance_initiative_pipeline` only matched stages with `status='PENDING' AND NOT document_id` — so DRAFT stages with docs were silently skipped, never approved, never advancing.

### 2. Pipeline Generated Docs for Future Stages Out of Order (PR #1251)
`advance_initiative_pipeline` looped `for stage_num in range(1, 6)` and generated documents for ANY `PENDING` stage without a doc — regardless of whether prior stages were approved. This caused:
- Stage 3 and 4 docs generated while initiative was stuck at Stage 2
- When Stage 2 was unblocked, the pipeline rubber-stamped approvals through 4 stages in 10 minutes with zero new work
- "Audit integrity-monitoring" jumped from Stage 2 → Stage 5 instantly with no real progression

### 3. All Stage Documents Contained Garbage Data (PR #1252)
Deep audit of ALL Research Briefs (Stage 1) and Prototype Plans (Stage 2) on Railway revealed:
- **Stage 1 docs**: ~263 chars of parroted prompt instructions ("Research on: Research this topic using EXTERNAL sources...")
- **Stage 2 docs**: ~140 char random blog post summaries about the Government Shutdown — completely unrelated to initiative topics
- Root cause: `TechnicalDocumentAgent` called with no `topic` (fell back to "Untitled Topic"), no `research_context`, and no tools to do actual research — so it hallucinated

## Solutions

### Fix 1: DRAFT Stage Approval (PR #1250)
Added second condition in `advance_initiative_pipeline` to detect `DRAFT` stages with existing documents. These get approved without regenerating documents. Added `needs_document` flag to skip document generation for stages that already have docs.

### Fix 2: No Stage Skip-Ahead (PR #1251)
Replaced `for stage_num in range(1, 6)` loop with `init.current_stage` lookup:
- Only processes the initiative's current stage — never scans ahead
- Verifies prior stage is `APPROVED` before proceeding (Stage 1 exempt — no prior)
- Prevents document generation or approval for any stage beyond `current_stage`

### Fix 3: Real System Data Gathering (PR #1252)
Added `_gather_initiative_research(initiative, stage_num)` function that queries 4 real data sources:
1. **SpiderData** — keyword search on `embedding_text__icontains` (last 14 days, up to 5 hits)
2. **SignalClusters** — keyword search on `name__icontains` (last 14 days, up to 3 hits)
3. **AgentConversations** — keyword search on `topic__icontains` with `conclusion` field (last 14 days, up to 3 hits)
4. **Deliverables** — existing deliverables for the initiative (up to 3)

Keyword extraction from initiative name (words > 3 chars, common stop words excluded, max 6 keywords).

Updated task prompt:
- Injects `REAL DATA` section with formatted query results
- Instructions: "Reference SPECIFIC data points from the REAL DATA section"
- Anti-hallucination: "If no real data was found, clearly state 'No data available'"
- Anti-blog: "Do NOT produce blog-style content — this is a technical document"

Also passes `topic` and `research_context` to agent context (were missing before).

## Files Modified

| File | Changes |
|------|---------|
| `core/tasks.py` | PR #1250: DRAFT stage detection + `needs_document` flag |
| `core/tasks.py` | PR #1251: `current_stage` anchoring + prior stage check |
| `core/tasks.py` | PR #1252: `_gather_initiative_research()` + updated prompts + context passing |

## Verification

### PR #1250 (DRAFT approval)
- Deployed and verified: 2 initiatives progressed to Stage 5, 6 to Stage 3 within 30 minutes

### PR #1251 (No skip-ahead)
- Deployed: prevents future stage document generation
- New initiatives will progress one stage at a time

### PR #1252 (Real data gathering)
- Deployed via GitHub push, auto-deploying to all Railway services
- Pending verification: next initiative stage advancement cycle should produce documents with real spider data, signal clusters, and conversation conclusions

## Key Discoveries

### Stage Document Audit Results
All 8 active initiatives audited on Railway:
- **Every Stage 1 doc**: Parroted prompt instructions instead of research
- **Every Stage 2 doc**: Random blog summary about Government Shutdown
- **No initiative had a document with data relevant to its topic**

### Root Cause Chain
1. `advance_initiative_pipeline` calls `TechnicalDocumentAgent.execute(task=prompt, context={...})`
2. Context dict had NO `topic` key → agent fell back to "Untitled Topic"
3. Context dict had NO `research_context` → agent had nothing to reference
4. `TechnicalDocumentAgent._call_llm()` uses plain `gpt-4o` with NO tools → can't do web search or spider queries
5. Agent hallucinated content (blog summaries) or parroted the prompt instructions

### The "Rubber-Stamp" Pattern
When `range(1, 6)` loop generated docs for future stages while current stage was stuck:
- Stages 3-4 got documents created on Feb 15 (while initiative was stuck at Stage 2)
- Session 1021 PR #1250 unblocked Stage 2 approval
- Pipeline approved Stage 2 → saw Stage 3 already had doc → approved → same for Stage 4 → Stage 5
- 4 stages approved in 10 minutes (03:44 to 03:54) with zero new work

## Key Gotchas

- `InitiativeStage`: import from `core.models_document_registry` (NOT `core.models_unified_system`)
- `Deliverable`: import from `core.models_deliverables` (NOT `core.models_document_registry`)
- `AgentConversation.conclusion` is the summary field (NOT `messages_data`)
- Initiative `current_stage` is the canonical "where are we" indicator — don't scan all 5 stages independently
- `TechnicalDocumentAgent` has NO tools — it can only work with data you give it in the prompt/context
