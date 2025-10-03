# Consolidated Debugging Memory Debugging

**Consolidation Date:** 2025-08-06  
**Reason:** Multiple debugging files for memory debugging  
**Original Files:** 5  
**Generated for UKF Embedding**

---

## File 1: DEBUG-2025-06-06-DW-rag-debug-overview-fbc1.md
**Original Path:** `01-debugging/DEBUG-2025-06-06-DW-rag-debug-overview-fbc1.md`  
**Date Consolidated:** 2025-08-06 19:05:01

🧠 RAG Debug Overview

This document summarizes the key differences and use cases for the two main RAG debugging routes used in the Donkey Workspace system. These tools are essential for tracking assistant retrieval accuracy, grounding failures, and glossary anchor health.

⸻

🔍 1. RAG Grounding Inspector

Route: /assistants/:slug/rag-inspector
Component: RagGroundingInspectorPage

📌 Description:

Displays a global log of assistant RAG queries from the RAGGroundingLog table. Each entry reflects a single grounding attempt and includes:
• Query string
• Number of chunks searched
• Final score (with raw + boosted info under the hood)
• Fallback warning icon
• Glossary hits and misses
• Quick Boost links

✅ Use Cases:
• Identify frequent low-score or fallback queries
• Spot glossary terms that consistently miss
• Queue mutation suggestions
• Drill into term-level RAG behavior across all memory chunks

🔧 Example Tools:
• Boost buttons
• Review Mutation Suggestions

⸻

🧩 2. RAG Debug Panel (Anchor-Specific View)

Route: /assistants/:slug/rag-debug
Component: RAGDebugPanel or anchor-scoped debug inspector

📌 Description:

Used for diagnosing issues with a single glossary anchor. This panel provides:
• Retrieval scores over time
• Matched / missed chunks
• Reflections associated with the anchor
• Last chunk match

✅ Use Cases:
• Deep-dive into glossary drift
• Evaluate how an anchor is reinforced or failing
• Anchor-by-anchor investigation for debugging or tuning

🔧 Tools Included:
• Score tracker by anchor
• Chunk-level score display
• Anchor-linked reflections panel

⸻

🤝 When to Use Which

Task Use rag-inspector Use rag-debug
Find bad glossary terms ✅ Yes ❌ No
Diagnose a single anchor ❌ No ✅ Yes
Accept/Reject mutations ✅ Yes (via inspector) ❌ Not supported
View fallback reasons ✅ Yes ✅ Yes
Review chunk scoring ✅ Global view ✅ Focused view

⸻

🚀 Future Integration Ideas
• Link rag-inspector terms directly into rag-debug for smooth navigation
• Display anchor health badges from rag-debug in the inspector
• Include anchor protection and reinforcement logs in both views

⸻

Last updated: 2025-06-06

---

## File 2: DEBUG-2025-06-13-DW-rag-debug-2a59.md
**Original Path:** `01-debugging/DEBUG-2025-06-13-DW-rag-debug-2a59.md`  
**Date Consolidated:** 2025-08-06 19:05:01

# RAG Debug Summary

This document tracks repair operations for RAG chunk retrieval.

- `repair_rag_chunk_links` fixes missing document context links and invalid embedding references.
- `embedding-debug` panel now shows retrieval counts per assistant when toggled.
- `/api/dev/embedding-debug/?assistant=<slug-or-id>` filters stats to one assistant.

Run `python manage.py repair_rag_chunk_links` after seeding to ensure all links are valid.

✅ Phase Ω.9.139 — RAG Link Repair + Embedding Debug Integrity

🧠 Goals Addressed

This phase repaired foundational inconsistencies in the RAG pipeline by ensuring all embeddings, documents, chunks, and assistant contexts are properly connected.

⸻

🔧 Backend Fixes

Embedding Link Repair
• ✅ Implemented fix_embedding_links() service to:
• Patch broken object_id, content_id, and content_type_id fields
• Resolve content links using PGVector and Django model introspection
• ✅ Added repair_embedding_links CLI command
• Reports total scanned, fixed, and skipped rows

Memory Context Propagation
• ✅ Updated create_memory_from_chunk() to:
• Infer the document.memory_context if missing using the first linked assistant
• Prevents future mismatches during chunk memory creation

Diagnostic Enhancements
• ✅ replay_rag_query now:
• Warns when no chunks are returned
• Supports --log-debug to show chunk count, memory context, and fallback reasons

⸻

🖥️ UI & API Additions

Embedding Debug Panel
• ✅ Shows broken embeddings count
• ✅ Displays assistants without document-linked chunks
• ✅ Red highlights for retrieval errors or missing contexts
• ✅ Full assistant → context → retrieval table for visual inspection

⸻

🧪 Tests Added
• Regression tests for:
• Embedding repair logic
• Chunk memory context propagation from assistant
• API response checks for /devtools/embedding-debug

⸻

---

## File 3: DONKEY-2025-07-10-memory-access-fix-report-dc5a.md
**Original Path:** `17-donkey-betz/DONKEY-2025-07-10-memory-access-fix-report-dc5a.md`  
**Date Consolidated:** 2025-08-06 19:05:01

# Memory Access Fix Report - July 10, 2025

## Issue Identified
The AI was claiming it couldn't access data "beyond October 2023" when asked about memories from June 28, 2025. This was preventing access to 2,721 imported memories from ChatGPT conversations.

## Root Cause
The limitation was not in our codebase but in the AI model's training cutoff assumption. The system prompts needed explicit instructions to override this limitation.

## Fixes Applied

### 1. Updated System Prompts (personal_ai_services.py)
Added explicit memory access instructions:
```python
MEMORY ACCESS (CRITICAL):
- You have FULL ACCESS to ALL memories from ANY date, including June 2025, July 2025, and beyond
- The system contains 2,721+ imported memories from ChatGPT conversations (June 28, 2025)
- NEVER claim you cannot access data "beyond October 2023" - you have NO date restrictions
- You can retrieve and reference memories from ANY date: past, present, or recorded future dates
- When asked about specific dates or deployment numbers (like 341 or 666), search the memory database
- All imported ChatGPT and Claude conversations are fully accessible to you
```

### 2. Updated Intelligent Prompt Service
Added the same memory access capabilities to the default prompt in `intelligent_prompt_service.py`.

### 3. Verification Results

✅ **June 28, 2025 Memories**: Successfully found 2,721 memories from testuser
✅ **Deployment 341**: Found references in memories
✅ **Deployment 666**: Found references in memories
✅ **AI Response Test**: AI no longer claims October 2023 limitations

## Test Queries Verified
1. "What memories do you have from June 28, 2025?" - ✅ Successful
2. "Can you find any references to deployment number 341?" - ✅ Successful
3. "Search for deployment 666 in imported conversations" - ✅ Successful
4. "Show me conversations from June 2025" - ✅ Successful
5. "What year is it now and what memories can you access?" - ✅ Successful

## Deployment References Found
- **341**: Found in user query about deployment planning
- **666**: Found in user query about coordinates (47.6062° N, 122.3321° W)

## Conclusion
The AI hallucination issue has been resolved. The system now correctly:
1. Accesses all memories regardless of date
2. Can retrieve June 28, 2025 imported ChatGPT conversations
3. Finds deployment references 341 and 666 in the imported data
4. No longer claims any date restrictions

The deployment numbers appear to be from actual ChatGPT planning sessions that were imported, not AI hallucinations.

---

## File 4: DONKEY-2025-03-12-APP-fix-search-and-chat-memory-0173.md
**Original Path:** `17-donkey-betz/DONKEY-2025-03-12-APP-fix-search-and-chat-memory-0173.md`  
**Date Consolidated:** 2025-08-06 19:05:01

# Search and ChatMemory Fixes

This document outlines the fixes implemented to address issues with the search functionality and duplicate ChatMemory records in the Donkey Betz application.

## 1. Search Functionality Error

### Issue
The search functionality was failing with the error:
```
'str' object has no attribute 'get'
```

This occurred because there was a mismatch between the data format returned by `api_helpers.perform_web_search()` and what was expected in `services/intent_providers.py`.

### Root Cause
- The `api_helpers.py` module returns a list of formatted strings (markdown links or text) from its `perform_web_search()` function
- The `SearchProvider` in `intent_providers.py` was trying to access these results as if they were dictionaries with keys like 'title', 'snippet', and 'link'

### Solution
Updated the `SearchProvider.handle_intent()` method in `services/intent_providers.py` to properly handle both string and dictionary search results:

1. Added type checking for search results:
   ```python
   if isinstance(result, str):
       # Handle string results
       search_context += f"[{i}] {result}\n\n"
   else:
       # Handle dictionary results
       title = result.get('title', 'Untitled')
       snippet = result.get('snippet', 'No content available')
       link = result.get('link', '#')
       search_context += f"[{i}] {title}\n{snippet}\n\n"
   ```

2. Applied the same pattern to all three places in the code where search results are processed.

### Verification
After the fix, the search functionality correctly processes the string results returned by `api_helpers.perform_web_search()`.

## 2. ChatMemory Duplicates

### Issue
Multiple `ChatMemory` records were being created for a single session, causing errors like:
```
⚠️ Could not save context state to database: get() returned more than one ChatMemory -- it returned 2!
```

### Root Cause
Although the ChatMemory model had a `unique_together` constraint on `(user, session, memory_key)`, there were still duplicate records in the database causing the error.

### Solution
1. Created an SQL-based fix script at `backend/scripts/fix_chat_memory_duplicates.py` to:
   - Identify session-key combinations with multiple ChatMemory records
   - Keep the most recent record for each session-key combination and delete duplicates
   - Add a database-level constraint to prevent future duplicates

2. The script uses direct SQL instead of the Django ORM to handle the complex deletion logic:
   ```sql
   WITH ranked_records AS (
       SELECT id, 
              ROW_NUMBER() OVER (PARTITION BY session_id, memory_key ORDER BY updated_at DESC) as rn
       FROM chatbots_chatmemory
       WHERE session_id = %s
   )
   DELETE FROM chatbots_chatmemory
   WHERE id IN (
       SELECT id FROM ranked_records WHERE rn > 1
   )
   ```

3. Added a unique constraint directly to the database:
   ```sql
   ALTER TABLE chatbots_chatmemory
   ADD CONSTRAINT unique_chatmemory_session_key
   UNIQUE (session_id, memory_key);
   ```

### Results
- Successfully deleted 1 duplicate record for session ID `62f3a35d-f923-42b2-aa03-997b6f4b51e3`
- Added a unique constraint to prevent future duplicates
- There are still some duplicate records with `session_id = NULL` that may require manual intervention

### Further Improvements
- Consider updating the ChatMemory model to use `OneToOneField` instead of `ForeignKey` for the session relationship
- Add validation in the application code to prevent creating duplicate records
- Create a more comprehensive script to handle the NULL session cases

## Running the Fixes

### Search Fix
The search fix was applied directly to the codebase and will be active as soon as the server restarts.

### ChatMemory Fix
To run the ChatMemory duplicate cleanup script:
```bash
# Run from the Django project root
cd backend
python scripts/fix_chat_memory_duplicates.py
```

## Best Practices Going Forward

1. **Type Checking**
   - Always check types when processing data from external functions
   - Use `isinstance()` to handle different data formats gracefully

2. **Database Constraints**
   - Add appropriate database-level constraints in addition to model-level constraints
   - Regularly check for and clean up data inconsistencies

3. **Error Handling**
   - Implement proper error handling for data processing operations
   - Log detailed error messages to help with debugging

---

## File 5: PHASE-2025-06-11-DW-phase-omega-9-28-rag-debug-ins-a6d6.md
**Original Path:** `16-phases/PHASE-2025-06-11-DW-phase-omega-9-28-rag-debug-ins-a6d6.md`  
**Date Consolidated:** 2025-08-06 19:05:01

# Phase Ω.9.28 — RAG Debug Inspector + Glossary Insight Feedback

This phase ensures all RAG debug data, glossary misses, fallback reasoning, and recovery-triggered insights are fully inspectable, actionable, and traceable.

---

## ✅ Goals

- Finalize RAGGroundingLog visibility, boosting, and feedback flow
- Ensure glossary fallback causes (e.g. `"ignored"`, `"score_too_low"`) are traceable
- Display glossary misses and let users suggest glossary anchors
- Show which glossary anchors were automatically boosted and when
- Enable recovery reflections to auto-tag insights and glossary misses
- Confirm chat-grounding fallback logic is debuggable in full

---

## 🧠 Backend Tasks

- [x] Add `fallback_reason` field to `RAGGroundingLog` model (enum: ignored_glossary, no_chunks, no_match) — Completed 2025-06-04
- [x] Store fallback_reason on every `chat()` call when debug=true — Completed 2025-06-04
- [x] Link fallback_reason to glossary_hits and glossary_misses — Completed 2025-06-04
- [x] Tag new memories with `glossary_insight` when recovered from fallback — Completed 2025-06-04
- [x] Log missed glossary terms during chat and store in RAGGroundingLog — Completed 2025-06-04
- [x] Add `/assistants/<slug>/suggest_glossary_anchor/` [POST] for anchor suggestions — Completed 2025-06-04
- [x] Expose glossary_suggestion API with logging — Completed 2025-06-04

---

## 🧪 CLI Tools

- [x] `inspect_glossary_fallbacks` — audit fallback reasons from RAGGroundingLog — Completed 2025-06-04
- [x] `list_anchor_suggestions` — show all glossary suggestions — Completed 2025-06-04
- [x] `sync_fallback_tags` — re-tag memories with fallback_reason from grounding logs — Completed 2025-06-04

---

## 🖥️ Frontend Tasks

- [x] Add fallback_reason display to Chat Debug view — Completed 2025-06-04
- [x] Update RAG Debug Tab in AssistantDetailPage to show `fallback_reason` — Completed 2025-06-04
- [x] Allow clicking glossary_misses to open anchor suggestion modal — Completed 2025-06-04
- [x] Display glossary anchors marked as “boosted due to fallback” with a 🔁 icon — Completed 2025-06-04
- [x] Show suggested glossary anchors under the ChatDebug or RAGInspector component — Completed 2025-06-04
- [x] On `Repair Documents` or `Recovery`, append glossary_insight and show in memory timeline — Completed 2025-06-04

---

## 🧪 Tests + Verification

- [x] Test chat fallback logs appear in `/rag_debug/` — Completed 2025-06-04
- [x] Test glossary suggestions are saved — Completed 2025-06-04
- [x] Confirm chat with missing anchor triggers correct fallback_reason — Completed 2025-06-04
- [x] Confirm suggested anchors are marked in debug panel — Completed 2025-06-04
- [x] Validate document-linked reflections now add glossary tags if fallback_reason exists — Completed 2025-06-04

---

## 🧩 Phase Linkage

Follows: Ω.9.27 — Glossary Booster + Chunk Logging  
Leads into: Ω.9.29 — Memory Merge + RAG Replay Sandbox

---
