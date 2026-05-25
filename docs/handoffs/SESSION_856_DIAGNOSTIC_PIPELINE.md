---
originating_session: 856
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 856 - Diagnostic Pipeline & Agent Content Review Fixes

**Date:** January 28, 2026
**Focus:** Diagnostic Pipeline System + Agent Output Display Improvements
**PRs:** #396, #397, #398, #399, #400

---

## What Was Accomplished

### 1. Diagnostic Pipeline System (PR #396)

Created a complete failure detection → diagnosis → prescription system.

**New Models** (`core/models_diagnostic_pipeline.py`):
| Model | Purpose |
|-------|---------|
| `FailureSignature` | Groups failures by stable signature (e.g., `OPENAI_429_QUOTA`) |
| `FailureDetection` | Raw failure recording without analysis |
| `FailureDiagnosis` | Root cause analysis with multi-source evidence |
| `FailurePrescription` | Ranked, scoped solutions (immediate/structural/observability) |

**New Services**:
| Service | File | Purpose |
|---------|------|---------|
| `FailureSignatureGenerator` | `failure_signature_generator.py` | Generates stable signatures from errors |
| `DiagnosticPipelineService` | `diagnostic_pipeline.py` | Main orchestrator |
| `EvidenceGatherer` | `evidence_gatherer.py` | Collects evidence from multiple sources |
| `SolutionRanker` | `solution_ranker.py` | Templates + ranking for solutions |

**Key Features**:
- Evidence priority system (stops at 80% confidence)
- Guardrails: 6h cooldown, 3+ sample threshold, known outage detection
- Initiative integration for remediation workflows

### 2. Retry Logic + Content Review (PR #397)

- Added retry logic for transient failures
- Improved content review UI handling

### 3. ResolveAgent Output Fix (PR #398)

- Fixed ResolveAgent to show descriptive messages instead of raw JSON
- Added actionable_config for content review

### 4. Agent Content Review Fixes (PR #399)

Added `ActionableOutputConfig` and descriptive messages to 9 agents:
- VideoAgent
- AudioAgent
- VideoEditingAgent
- ImageEditingAgent
- DevOpsAgent
- FullStackDeveloperAgent
- CodeReviewAgent
- PromptEngineeringAgent
- WorkflowAgent

### 5. ContentWriterAgent & LegalDocDrafterAgent (PR #400)

**ContentWriterAgent**:
- Message now shows: `Blog Post: "Title" | 1,500 words | professional tone | for developers`
- Updated payload_fields for better summary display

**LegalDocDrafterAgent**:
- Added ActionableOutputConfig with actions: Approve, Request Revision, Reject, Consult Attorney
- Added payload_fields for summary display

---

## Files Created

| File | Purpose |
|------|---------|
| `core/models_diagnostic_pipeline.py` | All diagnostic models |
| `core/services/failure_signature_generator.py` | Signature generation |
| `core/services/diagnostic_pipeline.py` | Main orchestrator |
| `core/services/evidence_gatherer.py` | Evidence collection |
| `core/services/solution_ranker.py` | Solution templates + ranking |

## Files Modified

| File | Change |
|------|--------|
| `core/agents/content_writer_agent.py` | Descriptive messages + improved payload_fields |
| `core/agents/legal/legal_doc_drafter_agent.py` | Added actionable_config |
| `core/agents/resolve_agent.py` | Added actionable_config + descriptive messages |
| `core/agents/video_agent.py` | Added actionable_config + descriptive messages |
| `core/agents/audio_agent.py` | Added actionable_config + descriptive messages |
| `core/agents/video_editing_agent.py` | Added actionable_config + descriptive messages |
| `core/agents/image_editing_agent.py` | Added actionable_config + descriptive messages |
| `core/agents/devops_agent.py` | Added actionable_config + descriptive messages |
| `core/agents/fullstack_developer_agent.py` | Added actionable_config + descriptive messages |
| `core/agents/code_review_agent.py` | Added actionable_config + descriptive messages |
| `core/agents/prompt_engineering_agent.py` | Added actionable_config + descriptive messages |
| `core/agents/workflow_agent.py` | Added actionable_config + descriptive messages |

---

## Session 856 PRs

| PR | Feature |
|----|---------|
| #396 | Diagnostic Pipeline System |
| #397 | Retry logic + Content review improvements |
| #398 | ResolveAgent output fix |
| #399 | Add actionable_config to 9 agents |
| #400 | ContentWriterAgent + LegalDocDrafterAgent display fixes |

---

## Architecture: Diagnostic Pipeline

```
Detection (what) → Diagnosis (why) → Prescription (fix)

1. FailureSignature - Groups failures by stable signature
2. FailureDetection - Records raw failure data
3. FailureDiagnosis - Analyzes root cause with evidence gathering
4. FailurePrescription - Generates ranked solutions by scope
```

**Evidence Priority** (stops at 80% confidence):
1. Raw exception/status code
2. Provider/endpoint info
3. Rate-limit metadata
4. Recent system events
5. LLM synthesis (last resort)

**Guardrails**:
| Guardrail | Value | Purpose |
|-----------|-------|---------|
| Cooldown per signature | 6 hours | Don't re-diagnose same issue |
| Minimum sample threshold | 3 failures | Don't diagnose noise |
| Known outage detection | Skip if degraded | Don't blame ourselves |
| Evidence confidence threshold | 0.8 | Stop gathering when confident |

---

## Next Steps

1. **Run migrations** for diagnostic models
2. **Test diagnostic pipeline** with simulated failures
3. **Integrate with ThinkingAgent** for diagnostic context
4. **Add Celery tasks** for periodic diagnostic runs
5. **Check for more agents** that may need content review fixes

---

**Session 856 Complete - Diagnostic Pipeline + 12 Agent Display Fixes**
