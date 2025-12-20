# Session 508 - Spider Fixes & Discord Command Limit

**Date:** December 19, 2025
**Previous Session:** 507 (Narrative Drift Discord Commands)
**Status:** COMPLETE

---

## Summary

Fixed spider execution errors and Discord's 100 command limit that was preventing new commands from syncing.

---

## Discord Command Limit Fix

Discord has a hard 100 command limit per guild. After adding 4 narrative drift commands in Session 507, we had 103 commands.

**Removed 4 low-usage commands:**
1. `/beep` - Voice test command
2. `/server-info` - Server config utility
3. `/brief-feedback` - Market Intelligence Brief rating
4. `/action` - Trading action tracking

**Result:** 99 commands syncing successfully.

---

## Spider Fixes

### 1. findlaw Error: 'list' object has no attribute 'get'

**Root Cause:** Spider's `fetch_data()` returns a list, but task code expected a dict.

**Fix:** Normalized raw_data returns in `core/tasks.py`:
- Lines 342-350: Sync spider path
- Lines 878-886: Async spider path
- Lines 924-929: Final item_count calculation

Also fixed `core/views_spider_dashboard.py` lines 134-150 to handle both dict and list formats.

### 2. colorado_family_law & justia_family_law: Partial Status (0 items)

**Root Cause:** These spiders weren't in the lightweight execution handler lists.

**Fix in `core/tasks.py`:**
- Lines 1144-1145: Added to `SPIDER_CONFIGS` dict
- Line 1251: Added to `_collect_legal_platform()` handler check
- Lines 1708-1746: Added actual spider execution handlers that call `fetch_data_sync()`

**Result:** colorado_family_law now collects 55 forms, justia_family_law collects legal articles.

---

## Files Modified

| File | Changes |
|------|---------|
| `core/services/discord_bot.py` | Removed 4 commands, fixed sync logic |
| `core/tasks.py` | Fixed list handling, added legal spider handlers |
| `core/views_spider_dashboard.py` | Fixed raw_data list handling |
| `00-START-NEXT-SESSION.md` | Updated command count to 99 |
| `docs/handoffs/SESSION_507_NARRATIVE_DISCORD_COMMANDS.md` | Added command limit fix section |

---

## Commits

1. `2454b7b` - fix(Session 507): Discord 100 command limit - removed 4 low-usage commands
2. `e97313a` - fix(Session 507): Spider execution - handle list returns and add legal spiders

---

## Session 509 Priority: Domain-Specific Source Weighting

### Problem Identified
All narrative domains are pulling evidence from the **same general sources** (Axios, Variety, Google News, etc.). Evidence is matched by keywords only, not source specialty.

**Current Evidence Distribution:**
| Domain | Evidence Count | Issue |
|--------|---------------|-------|
| tech | 425 | General feeds - acceptable |
| climate | 329 | Pulling from Variety, Scary Mommy, Eater - NOT climate sources! |
| markets | 231 | Bloomberg, SEC, Finnhub - appropriate |
| geopolitics | 196 | NPR, BBC, Politico - appropriate |
| culture | 68 | General feeds - acceptable |
| politics | 65 | Politico, NPR - appropriate |
| crypto | 63 | Mixed sources |
| health | 33 | StatNews + general - needs more health sources |

### Recommended Solution
Implement **domain-source affinity scoring** in `core/services/narrative_drift_service.py`:

```python
DOMAIN_SOURCE_WEIGHTS = {
    'climate': {
        'preferred': ['noaa.gov', 'epa.gov', 'nature.com', 'sciencedaily.com'],
        'weight_boost': 1.5
    },
    'markets': {
        'preferred': ['bloomberg.com', 'sec.gov', 'wsj.com', 'reuters.com'],
        'weight_boost': 1.3
    },
    'health': {
        'preferred': ['nih.gov', 'statnews.com', 'webmd.com', 'healthline.com'],
        'weight_boost': 1.4
    },
    'crypto': {
        'preferred': ['coindesk.com', 'cointelegraph.com', 'decrypt.co'],
        'weight_boost': 1.3
    }
}
```

When collecting evidence, boost confidence for domain-appropriate sources.

---

## Session 509 Priority: Mythology Verification

### Current Status
Mythology validation exists in `LegalDocDrafterAgent` (lines 1183, 2764) to prevent legal hallucinations.

### Recommended Integration Points for Narrative Drift
1. **NarrativeEvidence creation** (`core/services/narrative_drift_service.py`)
   - Before storing evidence, verify source URL is real and accessible
   - Cross-reference claims with multiple sources before high confidence

2. **Shift detection** (`detect_shifts()` method)
   - Require minimum 3 corroborating sources before declaring a shift
   - Flag single-source shifts as "unverified"

3. **Watch notifications**
   - Include source count in notifications: "Shift detected (5 sources)" vs "(1 source - unverified)"

### Implementation Pattern
```python
def _verify_evidence(self, evidence_data: dict) -> dict:
    """Mythology verification for narrative evidence."""
    source_url = evidence_data.get('source_url', '')

    # 1. Verify URL is valid and accessible
    if not self._is_valid_source(source_url):
        evidence_data['verified'] = False
        evidence_data['confidence'] *= 0.5
        return evidence_data

    # 2. Check against known reliable sources
    if self._is_preferred_source(source_url, evidence_data['domain']):
        evidence_data['confidence'] *= 1.3
        evidence_data['verified'] = True

    return evidence_data
```

---

## Other Session 509 Ideas

1. Run spider network sweep to verify all legal spiders work
2. Continue Discord vs Web feature parity
3. Add automated Discord notifications when watched narratives shift
4. Consider Huggingface sentiment model for ML-based narrative detection

---

## System Status

| Metric | Value |
|--------|-------|
| Discord Commands | 99 |
| Narrative Commands | 9 |
| Legal Spiders | 6 (courtlistener, justia, findlaw, lii, colorado_family_law, justia_family_law) |
| Spider Errors | 0 (fixed) |
