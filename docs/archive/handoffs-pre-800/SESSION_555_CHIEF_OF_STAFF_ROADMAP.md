# Chief of Staff Layer - Complete Roadmap

**Created:** Session 555 (December 25, 2025)
**Purpose:** Transform agent conversations from ephemeral debates into tracked, executable, learning work

---

## The Problem

Your agents are a **brilliant advisory board** that:
- Has production-quality strategic debates
- Proposes concrete experiments and plans
- Identifies risks and mitigations
- Generates actionable insights

But they're **shouting into the void** because:
- Proposals aren't extracted from conversations
- Approved items don't get executed
- No synthesis of what's happening
- No way for humans to provide feedback
- Agents never learn from outcomes

---

## The Solution: Chief of Staff Layer

A four-phase implementation that creates the missing layer between agent intelligence and human action.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CHIEF OF STAFF LAYER                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Phase A              Phase B              Phase C                  │
│  ┌──────────┐        ┌──────────┐        ┌──────────┐              │
│  │ Artifact │   →    │Execution │   →    │  Weekly  │              │
│  │Extraction│        │ Pipeline │        │Synthesis │              │
│  └──────────┘        └──────────┘        └──────────┘              │
│       ↑                   ↑                   ↓                     │
│       │                   │                   │                     │
│  Conversations       Approved            Briefs to                 │
│  → Proposals         Items               Human                     │
│                                               │                     │
│                      Phase D                  │                     │
│                    ┌──────────┐               │                     │
│                    │  Human   │ ←─────────────┘                     │
│                    │ Feedback │                                     │
│                    └──────────┘                                     │
│                         │                                           │
│                         ↓                                           │
│                   Agent Learning                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase Summary

| Phase | Name | What It Does | Key Deliverable |
|-------|------|--------------|-----------------|
| A | Artifact Extraction | Pulls proposals, risks, experiments from conversations | ConversationArtifact model + extraction service |
| B | Execution Pipeline | Turns approved artifacts into tracked work | ExecutionItem model + execution service |
| C | Weekly Synthesis | Summarizes activity into readable briefs | IntelligenceBrief model + synthesis service |
| D | Human Feedback | Lets humans respond and teach agents | HumanFeedback model + learning records |

---

## Implementation Order

### Phase A: Artifact Extraction (START HERE)
**Handoff:** `SESSION_555_PHASE_A_ARTIFACT_EXTRACTION.md`

Must be done first because:
- Creates the data structure (ConversationArtifact) that B, C, D depend on
- Enables visibility into what agents are proposing
- Populates "Proposals Awaiting Decision" in Boardroom

**Estimate:** 1-2 sessions

### Phase B: Execution Pipeline
**Handoff:** `SESSION_555_PHASE_B_EXECUTION_PIPELINE.md`

Requires Phase A because:
- ExecutionItem is created from approved ConversationArtifact
- Can't execute what hasn't been extracted

**Estimate:** 2-3 sessions

### Phase C: Weekly Synthesis
**Handoff:** `SESSION_555_PHASE_C_WEEKLY_SYNTHESIS.md`

Can run in parallel with B, but better after A:
- Synthesis includes artifact counts
- Better with execution outcomes to report

**Estimate:** 1-2 sessions

### Phase D: Human Feedback Loop
**Handoff:** `SESSION_555_PHASE_D_HUMAN_FEEDBACK_LOOP.md`

Should be last because:
- Provides feedback on artifacts, executions, briefs
- Needs all the targets to exist first

**Estimate:** 2 sessions

---

## New Models Summary

| Model | Phase | Purpose |
|-------|-------|---------|
| `ConversationArtifact` | A | Extracted actionable item from conversation |
| `ExecutionItem` | B | Tracked work item from approved artifact |
| `ExecutionUpdate` | B | Progress updates on executions |
| `IntelligenceBrief` | C | Synthesized weekly/daily report |
| `HumanFeedback` | D | Human input on any system output |
| `AgentLearningFromFeedback` | D | Records of what agents learned |

---

## New Services Summary

| Service | Phase | Purpose |
|---------|-------|---------|
| `ArtifactExtractionService` | A | Extracts artifacts from conversations |
| `ExecutionService` | B | Manages execution lifecycle |
| `IntelligenceSynthesisService` | C | Generates briefs |
| `FeedbackService` | D | Processes human feedback |

---

## New Celery Tasks Summary

| Task | Phase | Schedule |
|------|-------|----------|
| `batch_extract_artifacts` | A | Every hour |
| `process_pending_executions` | B | Every 10 minutes |
| `check_stale_executions` | B | Daily |
| `generate_daily_brief` | C | 8 AM daily |
| `generate_weekly_brief` | C | Monday 9 AM |
| `process_pending_feedback` | D | Every 5 minutes |

---

## UI Changes Summary

| Component | Phase | Change |
|-----------|-------|--------|
| Boardroom | A | Add "Proposals Awaiting Decision" section |
| Dashboard | B | Add "Active Executions" tracker |
| Home | C | Add "Intelligence Brief" prominent display |
| Everywhere | D | Add feedback buttons to all agent outputs |

---

## Success Metrics

After all phases complete:

1. **Extraction Rate:** >80% of actionable proposals extracted from conversations
2. **Decision Time:** Proposals decided within 48 hours on average
3. **Execution Completion:** >70% of approved items reach completion
4. **Brief Engagement:** Weekly brief opened within 24 hours
5. **Feedback Volume:** At least 5 feedback items per week
6. **Learning Application:** >90% of feedback applied to agents

---

## The Complete Data Flow

```
Spider Data
    ↓
Agent Knowledge
    ↓
Agent Conversations ──→ Phase A: Artifact Extraction
    ↓                          ↓
Agent Dreams            ConversationArtifacts
    ↓                          ↓
Boardroom ←──────────── Proposals Queue
    ↓
User Decision (Approve/Reject/Defer)
    ↓
Phase B: Execution Pipeline
    ↓
ExecutionItem (tracked work)
    ↓
Agent Executes
    ↓
Outcome Recorded
    ↓
Phase C: Weekly Synthesis
    ↓
IntelligenceBrief
    ↓
Human Reviews
    ↓
Phase D: Human Feedback
    ↓
Agent Learning Records
    ↓
Improved Future Conversations
    ↓
(cycle repeats)
```

---

## Quick Reference: File Locations

All handoffs in: `docs/handoffs/`

- `SESSION_555_PHASE_A_ARTIFACT_EXTRACTION.md`
- `SESSION_555_PHASE_B_EXECUTION_PIPELINE.md`
- `SESSION_555_PHASE_C_WEEKLY_SYNTHESIS.md`
- `SESSION_555_PHASE_D_HUMAN_FEEDBACK_LOOP.md`
- `SESSION_555_CHIEF_OF_STAFF_ROADMAP.md` (this file)

---

## Starting Phase A

When ready to begin:

1. Read `SESSION_555_PHASE_A_ARTIFACT_EXTRACTION.md`
2. Create `core/models_conversation_artifacts.py`
3. Create migration
4. Create `core/services/artifact_extraction.py`
5. Add API endpoints
6. Add UI section
7. Test extraction
8. Add Celery task

---

**This roadmap transforms your advisory board into an executive team that executes.**
