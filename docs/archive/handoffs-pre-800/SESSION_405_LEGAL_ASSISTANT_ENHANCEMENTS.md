# Session 405: Legal Assistant ChatGPT-Recommended Enhancements

**Date:** December 9, 2025
**Status:** COMPLETE ✅
**Branch:** `feature/session-52-ai-assistant`
**Focus:** Implementing 5 production-grade enhancements recommended by ChatGPT for the Pro Se Legal Assistant

---

## Summary

This session implemented all 5 enhancements that ChatGPT recommended after reviewing the Pro Se Legal Assistant's motion rewriting capabilities. ChatGPT validated the system as "court-ready and properly formatted" with "zero red flags" and suggested these enhancements to make it production-grade.

---

## What Was Built

### Enhancement #1: Third-Party Relief Auto-Rewrite ✅

**Problem:** Courts cannot order non-parties (like "Camille") to do anything.

**Solution:** Auto-detect and rewrite problematic third-party relief requests.

**Implementation:** `core/agents/legal/legal_doc_drafter_agent.py` - `_check_non_party_issues()`

**6 Regex Patterns:**
| Original | Auto-Corrected |
|----------|----------------|
| `"Camille shall not [action]"` | `"Respondent shall ensure that Camille does not [action]"` |
| `"Camille must not [action]"` | `"Respondent shall ensure that Camille does not [action]"` |
| `"Order Camille to [action]"` | `"Order Respondent to ensure that Camille [action]"` |
| `"Require Camille to [action]"` | `"Require Respondent to ensure that Camille [action]"` |
| `"Prohibit Camille from [action]"` | `"Order Respondent to ensure that Camille is not [action]"` |
| `"Camille is ordered to [action]"` | `"Respondent is ordered to ensure that Camille [action]"` |

---

### Enhancement #2: Emergency vs Non-Emergency Detector ✅

**Problem:** Users file "emergency" motions for non-emergency situations.

**Solution:** Classify situations and warn when emergency filing is inappropriate.

**Implementation:** `_assess_emergency_status()` method

**Tier 1 - TRUE Emergency Indicators:**
- Physical danger, imminent harm, sexual abuse
- Substance danger, flight risk, protective services involvement
- Self-harm risk, domestic violence

**Tier 2 - NON-Emergency Situations:**
- Communication issues, third-party presence concerns
- Schedule disputes, parenting disagreements
- Historical concerns (not current), emotional-only issues

**Output:**
- `is_emergency`: boolean
- `emergency_confidence`: 0-100%
- `false_emergency_warning`: boolean (warns if claiming emergency without factors)
- References C.R.S. § 14-10-129.5 requirements

---

### Enhancement #3: Court Order Attachment Check ✅

**Problem:** Modification/enforcement motions require attaching the order being modified.

**Solution:** Auto-detect when order attachment is needed and prompt user.

**Implementation:** `_check_order_attachment_required()` method

**Detects:**
- Modification language (modify, change, amend, alter, revise)
- Enforcement language (contempt, violation, enforce, breached)
- Order references (permanent orders, temporary orders, decree, parenting plan)

**Checks:**
- `uploaded_document_types` from context for `'court_order'`
- If modification/enforcement motion AND no court order uploaded → warning

---

### Enhancement #4: Conflict With Prior Orders Detector ✅

**Problem:** Motion requests may contradict existing court orders.

**Solution:** Parse uploaded orders and detect conflicts with motion requests.

**Implementation:** `_detect_order_conflicts()` method (~350 lines)

**Parses Existing Orders For:**
- Parenting time provisions
- Decision-making authority (joint/sole)
- Restrictions (supervision, alcohol, etc.)
- Third-party presence rules
- Holiday schedules

**Detects 6 Conflict Types:**
1. `DIRECT_CONTRADICTION` - Asking for opposite of what's ordered (joint→sole)
2. `DUPLICATE_REQUEST` - Asking for what's already in place
3. `MISSING_ORDER_REFERENCE` - Modification without citing order
4. Holiday/schedule conflicts
5. Unsupervised→Supervised contradictions
6. Custody type changes

**Severity Levels:**
- LOW (⚠️) - Acknowledgment issues
- MEDIUM (🟡) - Missing references
- HIGH (🟠) - Direct contradictions
- CRITICAL (🔴) - Major contradictions

---

### Enhancement #5: Likelihood of Success Confidence Meter ✅

**Problem:** Users don't know if their motion has a chance of success.

**Solution:** Score motions 0-100 based on four factors.

**Implementation:** `_assess_likelihood_of_success()` method

**Scoring (25 points each):**

| Factor | What It Measures |
|--------|------------------|
| **Relief Scope** | Narrower requests score higher |
| **Evidence Strength** | Documentary evidence, specific dates, witnesses |
| **Procedural Posture** | Verification, caption, proposed order, certificate of service |
| **Case Law Signals** | Favorable terms vs harmful terms |

**Rating Scale:**
- 🟢 75-100: HIGH - Strong likelihood of success
- 🟡 50-74: MODERATE - Reasonable chances, could be improved
- 🟠 25-49: LOW - Needs significant improvement
- 🔴 0-24: VERY LOW - Likely to be denied without changes

---

## Integration Fixes

After implementing the 5 enhancements, several integration issues were discovered and fixed:

### Fix 1: Court Order Upload Handling
**Problem:** Court orders were being analyzed through the denied motion pipeline.
**Solution:** Added document_type check in `upload_legal_case_file()` in `views_legal.py`.
**Result:** Court orders now show "✅ COURT ORDER SAVED" message instead of motion analysis.

### Fix 2: Auto-Fetch Court Orders for Conflict Detection
**Problem:** Uploaded court orders weren't being passed to the conflict detector.
**Solution:** Updated `analyze_legal_document()` to fetch user's court orders from database.
**Code Location:** `core/views_legal.py` lines 437-469
```python
court_orders = LegalDocument.objects.filter(
    user=doc.user,
    document_type='court_order'
).order_by('-created_at')[:5]
```

### Fix 3: Document Type String Matching
**Problem:** `_check_order_attachment_required` expected `'court order'` (with space), but database stores `'court_order'` (with underscore).
**Solution:** Updated check to include both formats:
```python
has_uploaded_order = any(
    doc_type.lower() in ['court_order', 'court order', 'order', 'decree', 'parenting plan', 'parenting_plan']
    for doc_type in uploaded_documents
)
```

### Fix 4: Generic Motion Wording
**Problem:** Message said "Upload your denied motion" which is too specific.
**Solution:** Changed to "Upload your motion" to work for any motion type.

---

## Complete User Flow

```
1. User uploads Court Order
   └─→ System shows "✅ COURT ORDER SAVED"
   └─→ Document stored in LegalDocument table
   └─→ No motion analysis runs

2. User uploads Motion (any type)
   └─→ System fetches user's court orders from database
   └─→ Pipeline runs:
       ├─ Step 2.5: Emergency Assessment
       ├─ Step 2.6: Court Order Attachment Check (recognizes uploaded orders)
       ├─ Step 2.7: Conflict Detection (uses court order text)
       ├─ Step 3: Facts Extraction
       ├─ Step 4: Motion Rewrite (JDF format)
       ├─ Step 5: Evidence Checklist
       └─ Step 6: Likelihood of Success Score
```

---

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/legal/legal_doc_drafter_agent.py` | Added 5 enhancement methods (~800 lines), tool definitions, pipeline integration |
| `core/views_legal.py` | Court order handling, auto-fetch court orders for context |
| `docs/handoffs/SESSION_403_PRO_SE_LEGAL_ASSISTANT.md` | Updated with enhancement details and integration fixes |

---

## Tools Added to LegalDocDrafterAgent

The agent now has **12 specialized tools**:

1. `search_legal_resources` - Search spider data for legal info
2. `draft_motion` - Generate motion templates
3. `draft_email` - Generate meet-and-confer emails
4. `draft_declaration` - Generate sworn declarations
5. `analyze_denied_motion` - Analyze why motion was denied
6. `rewrite_motion` - Generate corrected JDF-style motion
7. `generate_evidence_checklist` - Create exhibit checklist
8. `check_non_party_issues` - **Enhancement #1** - Detect & auto-rewrite third-party relief
9. `assess_emergency_status` - **Enhancement #2** - Emergency vs non-emergency classification
10. `check_order_attachment_required` - **Enhancement #3** - Detect missing court order attachment
11. `detect_order_conflicts` - **Enhancement #4** - Detect conflicts with existing orders
12. `assess_likelihood_of_success` - **Enhancement #5** - Calculate 0-100 success score

---

## Commits (Session 405)

```
b126339 docs(Session 405): Update handoff with integration fixes
cd4663c fix(Session 405): Generic motion wording in court order upload message
e8b2e5f fix(Session 405): Fix court order detection in attachment check
b081742 fix(Session 405): Court orders should not run through motion analysis
65d2d1c fix(Session 405): Auto-fetch court orders for conflict detection
e7ee72a feat(Session 405): Complete all 5 ChatGPT-recommended Legal Assistant enhancements
d66bb8e feat(Session 405): ChatGPT-recommended Legal Assistant enhancements
41a0075 feat(Session 405): Add denied motion keywords and logging
a4dc2a9 feat(Session 405): Legal Agent Text Cleanup & Collective Learning Integration
```

---

## Testing

### Quick Verification
```bash
# Start services
make start && make celery

# Test agent import
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
from core.agents.legal import LegalDocDrafterAgent
agent = LegalDocDrafterAgent()
print(f'Tools: {len(agent.TOOLS)}')  # Should be 12
"

# Test conflict detection
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django
django.setup()
from core.agents.legal import LegalDocDrafterAgent
agent = LegalDocDrafterAgent()
result = agent._detect_order_conflicts(
    motion_text='Motion requests sole decision-making authority.',
    existing_order_text='The parties shall have joint decision-making.',
)
print(f'Conflicts: {result[\"has_conflicts\"]}')  # Should be True
print(f'Severity: {result[\"overall_severity\"]}')  # Should be 'high'
"
```

### Full Flow Test
1. Go to http://localhost:8000/ai-studio/
2. Legal Assistant → My Case Files tab
3. Upload a court order (PDF) → Should show "✅ COURT ORDER SAVED"
4. Upload a motion (PDF) → Should show full analysis with:
   - Conflict detection results (using the uploaded court order)
   - Success likelihood score
   - Rewritten motion in JDF format

---

## What's Next (Potential Future Work)

1. **OCR Support** - Handle scanned PDF documents
2. **Case Timeline** - Visual timeline of case events from documents
3. **Auto-Detection** - Automatically detect document type from content
4. **Multi-Motion Package** - Generate all required separate filings at once
5. **Document Pinning** - Reference specific documents in ongoing chat

---

## Architecture Notes

The LegalDocDrafterAgent follows the clean architecture pattern:
- Inherits from `BaseAgent` (with `TimeTravelMixin`)
- Uses GPT function calling with 12 specialized tools
- Integrates with spider network for legal data
- Records decisions for debugging (Time Travel)
- Participates in collective intelligence (shares learned patterns)
- Auto-fetches user's uploaded court orders for context

**Key Pipeline Steps for Denied Motion:**
```
_handle_denied_motion_mode()
├─ Step 1: Detect as denied motion
├─ Step 2: Analyze original motion
├─ Step 2.5: Emergency assessment (Enhancement #2)
├─ Step 2.6: Court order attachment check (Enhancement #3)
├─ Step 2.7: Conflict detection (Enhancement #4)
├─ Step 3: Extract facts
├─ Step 3.5: Extract case metadata
├─ Step 4: Generate rewritten motion (JDF format)
├─ Step 5: Generate evidence checklist
└─ Step 6: Likelihood of success score (Enhancement #5)
```

---

## Important Reminders for Future Sessions

1. **GPT-5-mini is a reasoning model** - Use `max_completion_tokens` (not `max_tokens`), no `temperature` parameter
2. **Court orders should NOT be analyzed** - They're stored for reference only
3. **Document types use underscores** - `'court_order'` not `'court order'`
4. **All 5 enhancements are integrated into the pipeline** - Steps 2.5, 2.6, 2.7, and 6
5. **12 tools total** - The agent has grown from 6 to 12 specialized tools

---

**ChatGPT's Validation:** "Your system's rewrite is correct, court-ready, and properly formatted. There are zero red flags. If anything, it is better than what many self-represented litigants file."
