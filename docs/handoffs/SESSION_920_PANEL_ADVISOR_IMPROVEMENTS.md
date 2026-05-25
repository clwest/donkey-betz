---
originating_session: 920
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 920: Panel/Advisor System Improvements

**Date:** February 3, 2026
**PR:** #804
**Branch:** `feature/session-920-panel-advisor-improvements`
**Status:** Ready for Review

---

## Overview

Implemented 6 improvements to panel/advisor output quality based on ChatGPT feedback analysis. These changes address placeholder leakage, repeated content, unlabeled estimates, and missing decision context in panel outputs.

---

## Changes Made

### 1. Dedupe Post-Processor

**File:** `core/services/deduplication_service.py`

Added `dedupe_decision_summary_blocks()` method for hash-based deduplication of repeated DecisionSummary blocks in panel output.

```python
def dedupe_decision_summary_blocks(self, text: str) -> Tuple[str, bool]:
    """Hash-based deduplication of repeated blocks."""
    # Returns (deduped_text, dedupe_applied)
```

**Usage:** Call before `extract_decision_summary()` in conversation_roles.py.

---

### 2. Provenance Headers

**File:** `core/conceptforge/orchestrator.py`

Added provenance metadata to stage outputs in `_execute_stage()`:

```python
provenance_header = {
    'generated_at': timezone.now().isoformat(),
    'generated_at_local': timezone.localtime().strftime('%Y-%m-%d %H:%M %Z'),
    'inputs_used': list(previous_outputs.keys()) + [f"source:{run.source_id}"],
    'freshness_window': '72h',
    'validation_status': 'validated' if output_metadata.get('is_valid') else 'unvalidated',
    'publishable': quality_score >= 0.80,
}
```

---

### 3. Placeholder Validation

**File:** `core/conceptforge/orchestrator.py`

Added `INVALID_TOPICS` constant and validation in `_build_stage_inputs()`:

```python
INVALID_TOPICS = {'target', 'unknown', 'none', 'untitled', '[learned]', 'n/a', ''}

# If invalid topic detected, auto-generate from content or domain+timestamp
```

---

### 4. Extended DecisionSummary

**File:** `core/conversation_roles.py`

Extended `extract_decision_summary()` to parse new fields:

| Field | Description |
|-------|-------------|
| `decision.chosen` | The recommended approach/path forward |
| `decision.rejected_options` | Alternatives considered but not chosen |
| `why_now` | Why this should be prioritized now |
| `risk_assessment.biggest_risk` | Primary risk or concern |
| `risk_assessment.mitigation` | How to address the risk |
| `operating_constraints.delivery_cost` | Hours/days estimate |
| `operating_constraints.cac_ceiling` | Max customer acquisition cost |
| `operating_constraints.legal_gating` | Compliance requirements |
| `operating_constraints.staffing` | Required skills |

---

### 5. Enhanced Validation

**File:** `core/conversation_roles.py`

Updated `validate_decision_summary()` to require new fields:

```python
is_valid = (
    insights_count >= 3 and
    has_feature and
    next_steps_count >= 2 and
    not is_generic and
    has_decision and  # NEW requirement
    has_risk          # NEW requirement
)
```

Detailed `rejection_reason` now lists all failed requirements.

---

### 6. Estimate Labeling

**File:** `core/conversation_roles.py`

Added `validate_estimates()` function:

```python
def validate_estimates(text: str) -> Dict:
    """Check estimates are cited or labeled."""
    # Returns {'all_valid': bool, 'invalid_estimates': list, 'valid_estimates': list}
```

**Citation markers:** "based on", "according to", "data shows", "source:", etc.
**Estimate labels:** "estimate:", "assumption:", "confidence:", "approximately", etc.

---

### 7. Experiment Collision Control

**New File:** `core/services/experiment_collision_service.py`

New service to prevent multiple A/B tests from running on same target page:

```python
class ExperimentCollisionService:
    COLLISION_WINDOW_DAYS = 14

    def check_collision(self, experiment_type, target_page, ...) -> Dict:
        """Check if proposed experiment would collide with active ones."""

    def get_active_experiments(self, target_page=None) -> List[Dict]:
        """Get list of currently active experiments."""

    def suggest_experiment_timing(self, target_page, duration_days=14) -> Dict:
        """Suggest optimal timing for a new experiment."""
```

---

### 8. Updated Conclusion Prompts

**File:** `core/tasks.py`

Updated the conclusion prompt template (lines ~6607-6650) to require new sections:

```
Decision:
- Chosen Direction: [The recommended approach]
- Rejected Options: [Alternatives not chosen]

Why Now: [Priority reasoning]

Risk Assessment:
- Biggest Risk: [Primary risk]
- Mitigation: [How to address]

Operating Constraints:
- Delivery Cost: [Estimate or "N/A"]
- CAC Ceiling: [Max cost or "N/A"]
- Legal Gating: [Requirements or "None"]
- Staffing: [Skills or "Current team sufficient"]
```

Updated both fallback placeholders to include these sections.

---

## Testing Performed

```bash
# Test extract_decision_summary with new fields
python manage.py shell -c "
from core.conversation_roles import extract_decision_summary
result = extract_decision_summary(test_text)
print(f'Decision chosen: {result[\"decision\"].get(\"chosen\")}')
print(f'Risk biggest: {result[\"risk_assessment\"].get(\"biggest_risk\")}')
"

# Test validate_estimates
python manage.py shell -c "
from core.conversation_roles import validate_estimates
result = validate_estimates('Based on data, 50% will convert')
print(f'all_valid: {result[\"all_valid\"]}')
"

# Test dedupe_decision_summary_blocks
python manage.py shell -c "
from core.services.deduplication_service import get_deduplication_service
service = get_deduplication_service()
result, applied = service.dedupe_decision_summary_blocks(text_with_dupes)
print(f'Dedupe applied: {applied}')
"

# Test ExperimentCollisionService
python manage.py shell -c "
from core.services.experiment_collision_service import get_experiment_collision_service
service = get_experiment_collision_service()
result = service.check_collision('a/b_test', 'homepage')
print(f'has_collision: {result[\"has_collision\"]}')
"
```

All tests passed.

---

## Files Changed

| File | Lines | Description |
|------|-------|-------------|
| `core/services/deduplication_service.py` | +63 | dedupe_decision_summary_blocks() |
| `core/conceptforge/orchestrator.py` | +36 | Provenance headers, placeholder validation |
| `core/conversation_roles.py` | +241 | Extended extraction, validation, estimate validation |
| `core/tasks.py` | +57 | Updated prompts with new sections |
| `core/services/experiment_collision_service.py` | +266 | **NEW** - Collision detection |

**Total:** +663 lines

---

## Integration Points

### For calling dedupe:
```python
from core.services.deduplication_service import get_deduplication_service
service = get_deduplication_service()
deduped_text, was_deduped = service.dedupe_decision_summary_blocks(raw_text)
```

### For checking collisions:
```python
from core.services.experiment_collision_service import get_experiment_collision_service
service = get_experiment_collision_service()
result = service.check_collision('a/b_test', 'pricing_page', planned_duration_days=14)
if result['has_collision']:
    logger.warning(result['recommendation'])
```

### For validating estimates:
```python
from core.conversation_roles import validate_estimates
result = validate_estimates(summary_text)
if not result['all_valid']:
    logger.warning(f"Unlabeled estimates: {result['invalid_estimates']}")
```

---

## Next Steps

1. **Monitor** DecisionSummary validation failures in production to tune requirements
2. **Consider** adding experiment collision checks to the ConceptForge pipeline
3. **Evaluate** adding estimate validation to the panel output post-processor
4. **Track** provenance header usage in downstream consumers

---

## Related Sessions

- Session 918: Report Provenance + PDF Export (established provenance patterns)
- Session 909: DecisionSummary validation (generic penalty)
- Session 840: High-value signal extraction
- Session 786: DecisionSummary format requirement

---

**Author:** Claude Code (Session 920)
**Reviewed:** Pending
