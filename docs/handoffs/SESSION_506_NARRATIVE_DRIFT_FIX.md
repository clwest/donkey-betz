# Session 506 - Narrative Drift Detection Fix

**Date:** December 19, 2025
**Previous Session:** 505 (Spider Routing Fixes)
**Status:** COMPLETE

---

## Summary

Fixed the Narrative Drift sub-tab on the Autonomous Systems Dashboard which wasn't detecting or creating NarrativeShift records despite evidence being collected.

**Root Cause:** The `_scan_domain()` method in `NarrativeDriftCoordinator` was detecting shifts but only returning them in a list - it never actually created `NarrativeShift` database records!

---

## Issues Fixed

### 1. NarrativeShift Records Never Created

**Problem:** The `_scan_domain()` method detected when contradicting evidence exceeded supporting evidence, but only appended the shift to a return list - it never called `NarrativeShift.objects.create()`.

**File:** `core/agents/narrative/narrative_drift_coordinator.py:268-276`

**Before (broken):**
```python
if recent_contradicts > recent_supports and recent_count >= 3:
    result['shifts'].append({
        'narrative_id': str(narrative.id),
        'title': narrative.title,
        'signal': 'Contradicting evidence exceeds supporting',
        'confidence': 0.6 + (0.1 * min(recent_contradicts - recent_supports, 4)),
        'summary': f"'{narrative.title}' is receiving more contradicting evidence"
    })
```

**After (fixed):**
```python
if recent_contradicts > recent_supports and recent_count >= 3:
    confidence = 0.6 + (0.1 * min(recent_contradicts - recent_supports, 4))
    shift_summary = f"'{narrative.title}' is receiving more contradicting evidence"

    # Check for existing shift (avoid duplicates)
    existing_shift = NarrativeShift.objects.filter(
        old_narrative=narrative,
        detected_at__gte=cutoff
    ).first()

    if existing_shift:
        shift_id = str(existing_shift.id)
    else:
        # Create actual NarrativeShift record!
        shift = NarrativeShift.objects.create(
            old_narrative=narrative,
            new_narrative=None,
            domain=domain,
            shift_summary=shift_summary,
            old_narrative_summary=narrative.description or narrative.title,
            new_narrative_summary="To be determined by analysis",
            confidence=Decimal(str(confidence)),
            importance=Decimal('0.5'),
            trigger_events=[f"Contradicting evidence ({recent_contradicts}) > supporting ({recent_supports})"],
            evidence_sources=[str(e.id) for e in recent_evidence[:10]]
        )
        shift_id = str(shift.id)

        # Update narrative status
        narrative.status = NarrativeStatus.SHIFTING
        narrative.save()

    result['shifts'].append({...})
```

### 2. Scan Window Too Short

**Problem:** The autonomous cycle used a 6-hour window, but shifts are more likely to be detected over longer periods.

**File:** `core/agents/narrative/narrative_drift_coordinator.py:681`

**Fix:** Increased `hours_back` from 6 to 12 hours.

### 3. UI "Active" Count Showing 0

**Problem:** The JavaScript expected `status_breakdown.active` but the API returned actual status names (`emerging`, `dominant`, `shifting`).

**File:** `ai_core/templates/components/panels/autonomous_dashboard_panel.html:969-973`

**Fix:** Changed to calculate "Active" as sum of emerging + dominant + shifting.

### 4. Domain Coverage Wrong Colors

**Problem:** The color mapping used wrong domain names (ai, finance, jobs) instead of actual names (politics, markets, tech, culture, etc.).

**File:** `ai_core/templates/components/panels/autonomous_dashboard_panel.html:1030-1041`

**Fix:** Updated domainColors mapping to match actual NarrativeDomain choices.

### 5. Enhanced Sentiment Detection

**Problem:** The basic sentiment detection used only 5 positive and 5 negative words, leading to most evidence being classified as "neutral".

**File:** `core/agents/narrative/narrative_drift_coordinator.py:32-220`

**New `NarrativeSentimentAnalyzer` Class:**
- **100+ weighted keywords** (strong=2.0, standard=1.0, mild=0.5)
- **6 domain-specific vocabularies** (tech, markets, politics, crypto, climate, health)
- **Negation detection** ("not successful" → contradicts)
- **Contradiction phrases** ("despite claims", "myth", "hype")
- **Confidence scoring** with 30% margin requirement

```python
class NarrativeSentimentAnalyzer:
    POSITIVE_WORDS = {
        'breakthrough': 2.0, 'revolutionary': 2.0, 'success': 1.0, 'growth': 1.0, ...
    }
    NEGATIVE_WORDS = {
        'crash': 2.0, 'collapse': 2.0, 'fail': 1.0, 'decline': 1.0, ...
    }
    DOMAIN_KEYWORDS = {
        'tech': {'positive': {'disrupting': 1.5, ...}, 'negative': {'bug': 1.0, ...}},
        'markets': {...}, 'politics': {...}, 'crypto': {...}, 'climate': {...}, 'health': {...}
    }
    NEGATION_WORDS = {'not', 'no', 'never', "n't", "don't", ...}
    CONTRADICTION_PHRASES = ['actually', 'myth', 'hype', 'misleading', ...]

    @classmethod
    def analyze(cls, content: str, domain: str = None, narrative_title: str = None) -> Tuple[str, float]:
        # Returns (sentiment, confidence) with negation-aware scoring
```

**Test Results:**
| Content | Result | Confidence |
|---------|--------|------------|
| "AI is making breakthrough progress in reasoning" | supports | 0.75 |
| "Company reports record growth and rising profits" | supports | 0.67 |
| "Critics say the technology has failed to deliver" | contradicts | 0.67 |
| "Despite claims, the project was not successful" | contradicts | 0.71 |
| "The crash wiped out billions in value" | contradicts | 0.67 |
| "The weather was nice today" | neutral | 0.00 |

---

## Verification Results

After applying the fix, tested with 24-hour window:

| Narrative | Confidence | Shift ID |
|-----------|------------|----------|
| Immigration is the top voter concern | 0.7 | 0977c02b |
| AI art is not real art | 0.8 | 4f1489a3 |

**NarrativeShifts: 1 → 3 (+2 new)**

---

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/narrative/narrative_drift_coordinator.py` | Added NarrativeShift record creation, increased scan window to 12h, added NarrativeSentimentAnalyzer class (~190 lines) |
| `ai_core/templates/components/panels/autonomous_dashboard_panel.html` | Fixed "Active" count calculation, updated domain colors mapping |

---

## Technical Notes

### Narrative Drift Detection Logic

For a shift to be detected:
1. `recent_contradicts > recent_supports` - More contradicting than supporting evidence
2. `recent_count >= 3` - At least 3 pieces of evidence in the time window

### Sentiment Distribution

The evidence processing tends to classify most items as "neutral" or "supports", making shifts relatively rare. This is by design - shifts should be significant events.

### Duplicate Prevention

The fix includes duplicate checking to avoid creating the same shift multiple times if the detection runs frequently.

---

## Session 507 Ideas

1. ✅ ~~Improve sentiment detection~~ - **DONE** (NarrativeSentimentAnalyzer with 100+ keywords)
2. Consider integrating Huggingface sentiment model for ML-based detection
3. Consider lowering the threshold from contradicts > supports to contradicts >= supports
4. Add more narratives to track across different domains
5. Create Discord commands for Narrative Drift monitoring
