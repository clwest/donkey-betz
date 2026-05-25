---
originating_session: 997
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 997: Mythology Validation for PA Responses + PublishGate Scoring

**Date:** February 12, 2026
**Focus:** Wire existing mythology services into LLM output paths to prevent fabrication

## Problem

The platform had mythology validation services (built earlier) but they weren't wired into the two main LLM output paths: PA responses and the content PublishGate. This meant fabricated or risky claims could flow through unchecked.

## What Was Built

### 1. PA Response Validation (`unified_pa_entrypoint.py`)
- Every PA response is validated through mythology services after generation
- Risk > 0.3: response is flagged internally for review
- Risk > 0.7: disclaimer is appended to the response
- Anti-fabrication prompts added to `_generate_direct_response` and `_build_analytical_prompt`

### 2. PublishGate Mythology Score (`publish_gate.py`)
- New `mythology_score` dimension added to the PublishGate scoring system
- Content with mythology risk > 0.5 is capped at 'enhance' tier (cannot auto-publish)
- Integrated into `content_deliberation_runner.py` pipeline

## Files Changed (3)

| File | Change |
|------|--------|
| `core/services/unified_pa_entrypoint.py` | PA response mythology validation + anti-fabrication prompts |
| `core/services/publish_gate.py` | New mythology_score dimension, risk > 0.5 caps at 'enhance' |
| `core/services/content_deliberation_runner.py` | Wire mythology score into deliberation pipeline |

## Verification

- PA responses with fabricated claims now get flagged/disclaimed
- Content pipeline blocks risky content from auto-publishing
