---
originating_session: 851
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 851: Debate Agent Output Fix

**Date:** January 27, 2026
**Focus:** Fix Debate agents (DebateAdvocateAgent, DebateSkepticAgent) showing "1. Item 1" instead of actual content

---

## Summary

Session 851 fixed the "1. Item 1" bug in Debate agent output rendering, similar to the Session 848 fix for Podcast agents. The bug occurred because the content extraction logic didn't handle the Debate agents' unique output format.

---

## Problem

When DebateAdvocateAgent or DebateSkepticAgent returned results, both the backend file writer and frontend renderer showed:

```
Tool Results:
1. Item 1
2. Item 2
3. Item 3
```

Instead of the actual debate content (research findings, arguments, statements).

---

## Root Cause

### Backend (`core/tasks.py`)
The `_extract_agent_output_content()` function checked for keys like `title`, `name`, `content`, `summary`, `description`, `text` but Debate agents return:

- `research_findings`, `research_summary`, `suggested_angles/concerns`
- `argument_structure` or `critique_structure` with `thesis`, `evidence`, `conclusion`
- `statements` with `opening`, `key_points/key_concerns`, `rebuttals/tough_questions`, `closing`

None of these matched the existing content extraction logic, causing fallback to `f'Item {i}'`.

### Frontend (`SmartOutputRenderer.tsx`)
No `DebateRenderer` component existed to handle the Debate agents' `{role, voice_id, tool_results}` output format.

---

## Solution

### Backend Fix (`core/tasks.py` lines 26764-26830)

Added specific handling for Debate agent output formats:

1. **Research results**: `research_summary`, `research_findings`, `suggested_angles/concerns`
2. **Arguments**: `argument_structure` with `thesis`, `evidence`, `counterargument_handling`, `conclusion`
3. **Critiques**: `critique_structure` with `main_concern`, `evidence`, `probing_questions`, `fair_acknowledgment`
4. **Statements**: `statements` with `opening`, `key_points/key_concerns`, `rebuttals/tough_questions`, `closing`

Also added more fallback keys: `topic`, `role`, `message`, `output`, `analysis`

### Frontend Fix (`SmartOutputRenderer.tsx`)

1. Added `DebateToolResult` and `DebateAgentOutput` interfaces
2. Created `DebateRenderer` component with proper rendering for:
   - Research section with sources and suggested angles/concerns
   - Argument/Critique structure with thesis, evidence, conclusion
   - Debate statements with opening, key points, rebuttals, closing
3. Added detection logic: `isDebateAgentOutput` checks for `role: 'ADVOCATE'|'SKEPTIC'` + `tool_results`
4. Updated `hasToolResults` to skip raw rendering when debate output is detected

---

## Files Changed

| File | Change |
|------|--------|
| `core/tasks.py` | Added debate agent format handling in `_extract_agent_output_content()` |
| `frontend/src/components/SmartOutputRenderer.tsx` | Added `DebateRenderer` component + detection logic |
| `templates/frontend_index.html` | Updated JS/CSS bundle filenames |
| `frontend/dist/index.html` | Updated JS/CSS bundle filenames |

---

## Testing

```bash
# 1. Run a Debate agent via PodcastCoordinatorAgent
# Navigate to Workspace → Command → Run "Create podcast debate about AI automation"

# 2. Verify output shows:
# - Research findings with sources
# - Argument structure with thesis and evidence
# - Debate statements with opening/closing
```

---

## Debate Agent Output Format Reference

```python
# DebateAdvocateAgent/DebateSkepticAgent return:
AgentResult(
    success=True,
    message="Argument prepared",
    data={
        "role": "ADVOCATE" | "SKEPTIC",
        "voice_id": "Rachel" | "Clyde",
        "tool_results": [
            # Research tool
            {
                "topic": "AI Automation",
                "research_summary": "Found X relevant sources...",
                "research_findings": [{"title": "...", "source": "...", "url": "..."}],
                "suggested_angles": ["Economic benefits", "Innovation", ...]
            },
            # Argument/Critique tool
            {
                "argument_structure": {
                    "thesis": "Main point...",
                    "evidence": ["Point 1", "Point 2"],
                    "counterargument_handling": "Response to...",
                    "conclusion": "In conclusion..."
                },
                "argument_strength": "strong"
            },
            # Statements tool
            {
                "statements": {
                    "opening": "Opening statement...",
                    "key_points": ["Point 1", "Point 2"],
                    "rebuttals": ["Rebuttal 1", ...],
                    "closing": "Closing statement..."
                },
                "role": "ADVOCATE",
                "speaking_style": "enthusiastic, uses metaphors"
            }
        ]
    }
)
```

---

## Similar Fixes

This follows the same pattern as Session 848's fix for Podcast agents, which added `text` key extraction for ModeratorAgent output.

---

**Session 851 Complete - Debate agents now render properly**
