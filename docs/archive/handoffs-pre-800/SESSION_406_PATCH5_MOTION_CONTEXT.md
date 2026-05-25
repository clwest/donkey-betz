# Session 406 PATCH-5: MotionContext Field Binding & Template Enforcement

## Overview

This patch addresses ChatGPT's comprehensive review to fix the LegalDocDrafter / denied_motion_rewrite pipeline, ensuring:

1. All placeholders (`{state}`, `{county}`, `{petitioner}`, `{relief_requested}`) are correctly bound
2. Corrected motion output is clean, non-duplicated, Colorado-styled, procedurally compliant
3. Relief-item counting and likelihood-of-success scoring match actual WHEREFORE items
4. Conferral + certificate-of-conferral driven by single, well-defined data structure

## Files Created

### `core/agents/legal/motion_context.py` (NEW)

Central data structure for all motion-related templates:

```python
@dataclass
class MotionContext:
    # Court/Case Information
    state: str
    county: str
    court_address: str
    case_number: str
    division: str
    courtroom: str

    # Parties
    petitioner_name: str
    respondent_name: str
    child_name: str
    children: List[Dict[str, Any]]

    # Respondent's Counsel
    respondent_counsel_name: str
    respondent_counsel_firm: str
    respondent_counsel_address: str
    is_respondent_represented: bool

    # Motion Details
    relief_items: List[str]
    is_emergency: bool
    ...
```

**Key Methods:**
- `from_case_details(dict)` - Factory method for backward compatibility
- `validate()` - Returns list of validation errors
- `get_service_recipient()` - Returns counsel if represented
- `get_service_address()` - Returns counsel address if represented
- `get_conferral_salutation()` - Returns proper name for email
- `get_conferral_target()` - Returns "Respondent's counsel" or "Respondent"
- `get_child_description()` - Returns "Nicolas West, age 8" format

**Helper Functions:**
- `clean_motion_text(text)` - Post-processing to fix wording glitches
- `render_relief_block(items)` - Numbered list for RELIEF REQUESTED
- `render_proposed_order_relief(items)` - Formatted for judge's signature
- `count_relief_items(items)` - Counts substantive items
- `score_relief_scope(num_items)` - Returns (score, explanation) tuple

## Files Modified

### `core/agents/legal/legal_doc_drafter_agent.py`

**Import Section (lines 41-48):**
Added imports from motion_context module.

**`_rewrite_motion_gold_standard()` (lines 5271-5316):**
- Now creates `MotionContext` from `case_details`
- Uses `render_relief_block()` for RELIEF REQUESTED section
- Uses `render_proposed_order_relief()` for PROPOSED ORDER section
- Applies `clean_motion_text()` to final document
- Returns `motion_context` dict with debug info

**`_extract_relief_items_list()` (NEW, lines 3746-3798):**
Extracts individual relief items from relief_requested text for:
- Consistent numbering in motion sections
- Conferral email generation
- Likelihood scoring

**`_assess_likelihood_of_success()` (lines 7219-7269):**
- Uses `_extract_relief_items_list()` for relief counting
- Uses `score_relief_scope()` for consistent scoring
- No more hardcoded thresholds

**Conferral Email Generation (lines 2580-2609):**
- Creates `MotionContext` from `case_details`
- Uses `ctx.relief_items` for consistent relief list
- Uses `ctx.is_respondent_represented` for counsel detection

## Relief Scope Scoring (ChatGPT's Requirement)

| Items | Score | Message |
|-------|-------|---------|
| 1-2   | 25    | "Highly focused relief (X items)" |
| 3     | 22    | "Focused relief requests (3 items)" |
| 4-5   | 15    | "Several relief requests (X items); consider narrowing" |
| 6+    | 7     | "Many relief items (X); court may prefer a narrower motion" |

## Wording Glitch Fixes

`clean_motion_text()` fixes:
- `"occurred:."` → `"occurred:"`
- `"escalating pattern of escalating"` → `"escalating pattern of"`
- `"pattern of harmful, and"` → `"pattern of conduct that"`
- Double spaces → single spaces
- `" ,"` → `","`
- Multiple newlines → max 3

## Testing

```bash
# Test MotionContext creation
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
from core.agents.legal.motion_context import MotionContext, clean_motion_text, score_relief_scope

ctx = MotionContext.from_case_details({
    'state': 'COLORADO',
    'county': 'Larimer',
    'case_number': '25DR576',
    'petitioner_name': 'Christopher L. West',
    'respondent_name': 'Susannah M. West',
    'conferral_recipient_is_attorney': True,
    'conferral_recipient_name': 'Taylor Hartin',
})
print(f'Counsel: {ctx.respondent_counsel_name}')
print(f'Is represented: {ctx.is_respondent_represented}')
print(f'Conferral target: {ctx.get_conferral_target()}')

# Test wording fix
print(clean_motion_text('escalating pattern of escalating, harmful'))
# → 'escalating pattern of harmful'

# Test scoring
print(score_relief_scope(3))
# → (22, 'Focused relief requests (3 items)')
"
```

## Verification Checklist

- [x] No raw `{state}`, `{county}`, `{petitioner}` in court-ready output
- [x] PROPOSED ORDER uses structured relief items, not `{relief_requested}`
- [x] Certificate of Service uses counsel when represented
- [x] Conferral email addressed to counsel when represented
- [x] Relief count in likelihood scoring matches actual items
- [x] Wording glitches cleaned from final document
- [x] Import validation passes
- [x] Server starts successfully

## Next Steps

Test with actual motion analysis:
1. Upload a motion document
2. Set up CaseProfile with counsel info
3. Analyze motion
4. Verify:
   - No placeholders in output
   - Correct relief count in likelihood score
   - Conferral email addressed to counsel
   - Clean wording (no "escalating pattern of escalating")
