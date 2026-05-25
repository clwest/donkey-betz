# Session 404 Handoff: Pro Se Legal Assistant - Motion Rewriter

**Date:** December 9, 2025
**Session:** 404 (including 404C, 404D, 404E, 404F, Patch 4C)
**Focus:** Transform denied court motions into court-ready documents

---

## Executive Summary

Session 404 built a complete **Motion Rewriter** system that takes a denied court motion PDF, analyzes why it was denied, and generates a corrected, court-ready document in proper Colorado JDF format.

The session progressed through multiple sub-sessions:
- **404C-D**: Initial motion template and output structure
- **404E**: Removed disclaimers from court-ready output
- **404F**: Added county/state inference from court addresses
- **Patch 4C**: Major rewrite of fact extraction for clean numbered allegations

---

## What Was Built

### 1. Motion Rewriter Core (`rewrite_motion` tool)

Takes a denied motion and generates:
- **PART 1**: Corrected caption with proper jurisdiction
- **PART 2**: Relief sought summary
- **PART 3**: Corrected motion in JDF format
- **PART 4**: Evidence checklist
- **PART 5**: Full restatement (1:1 mapping verification)

### 2. County/State Inference (Session 404F)

When court address is extracted but county/state are blank:
```python
# Example: "201 LAPORTE AVENUE, SUITE 100, FORT COLLINS, CO, 80521"
# → County: LARIMER
# → State: COLORADO
```

**Colorado city → county mappings:**
- Fort Collins, Loveland → LARIMER
- Denver → DENVER
- Boulder → BOULDER
- Colorado Springs → EL PASO
- Aurora → ARAPAHOE
- Littleton, Centennial → ARAPAHOE
- Golden, Lakewood → JEFFERSON
- Greeley → WELD
- Pueblo → PUEBLO
- Grand Junction → MESA

### 3. Incident & Enumeration Normalization (Patch 4C)

Completely rewrote `_extract_facts_from_motion()` to handle messy PDF text:

**Problem:** PDFs contain inline semicolon-separated lists like:
```
"1. Today – November 12, 2025 – Father arrived late; 2. August 29, 2025, Father did not show; 3. The following week..."
```

**Solution:** New extraction pipeline:
1. `_extract_incident_candidates()` - Finds date-anchored incidents
2. `_clean_incident_text()` - Removes noise and subheadings
3. `_build_clean_allegations()` - Creates allegations 1-3
4. `_generate_impact_paragraph()` - Creates allegation 4 (impact summary)

**Output Format:**
```
SPECIFIC FACTUAL ALLEGATIONS:
1. On November 12, 2025, Father arrived late for parenting time exchange.
2. On August 29, 2025, Father failed to appear for scheduled exchange.
3. On September 5, 2025, Father arrived one hour late without notice.
4. This pattern of conduct has caused significant disruption to the children's routine and demonstrates a disregard for court-ordered parenting time.
```

### 4. Disclaimer Removal (Session 404E)

Removed HTML disclaimer from `legal_assistant_panel.html`:
```html
<!-- Session 404E: DISCLAIMER REMOVED - Court-ready documents should not have disclaimers -->
```

Court-ready documents should contain NO AI disclaimers.

---

## Files Modified

### Primary Agent File
`core/agents/legal/legal_doc_drafter_agent.py`

**Key Changes:**
| Location | Change |
|----------|--------|
| Line 37 | Added `Tuple` to imports |
| Lines 2243-2275 | Rewrote `_extract_facts_from_motion()` |
| Lines 2277-2388 | New `_extract_incident_candidates()` |
| Lines 2390-2423 | New `_clean_incident_text()` |
| Lines 2425-2430 | New `_extract_date_from_text()` |
| Lines 2432-2481 | New `_build_clean_allegations()` |
| Lines 2483-2534 | New `_generate_impact_paragraph()` |
| Lines 2640-2700 | County/state inference from address |
| Line 3134 | Added `original_motion_content` param to `_rewrite_motion_gold_standard()` |
| Lines 3323-3364 | PART 5: Full Restatement section |

### UI Template
`ai_core/templates/components/panels/legal_assistant_panel.html`

**Change:** Removed disclaimer div (lines 649-655)

### Documentation
- `docs/AGENTS.md` - Updated LegalDocDrafterAgent section
- `docs/CAPABILITIES.md` - Updated Pro Se Legal Assistant section
- `docs/handoffs/SESSION_404_PRO_SE_LEGAL_ASSISTANT.md` - This file

---

## Key Functions Reference

### `_extract_facts_from_motion(motion_content: str) -> List[str]`
Main entry point for fact extraction. Returns 3-4 clean allegations.

### `_extract_incident_candidates(text: str) -> List[Tuple[str, str, int]]`
Returns list of (incident_text, date_string, priority) tuples.

**Priority values:**
- 1 = Explicit date found ("November 12, 2025")
- 2 = Relative time ("the following week")
- 3 = No date but relevant content

### `_clean_incident_text(text: str) -> str`
Removes:
- Subheadings like "Today's Incident – November 12, 2025"
- Leading/trailing punctuation
- PDF artifacts

### `_build_clean_allegations(incidents, original_text) -> List[str]`
Builds allegations 1-3 from top incidents. Ensures "On [date]" format.

### `_generate_impact_paragraph(incidents, original_text) -> str`
Creates allegation 4 using petitioner's language to describe pattern/harm.

### `_extract_case_metadata(content: str) -> Dict`
Extracts: case_number, court_address, petitioner_name, respondent_name, county, state

**Now includes fallback inference:**
```python
if court_address and not county:
    # Parse city from address, map to county
    colorado_city_to_county = {'FORT COLLINS': 'LARIMER', ...}
```

---

## Testing the System

### Upload a Denied Motion
1. Go to http://localhost:8000/ai-studio/
2. Navigate to **Legal Assistant** tab → **My Case Files** sub-tab
3. Upload a denied motion PDF
4. Select document type: "Denied Motion"
5. Click **Analyze**

### Expected Output Structure
```
============================================================
PART 1: CORRECTED CAPTION
============================================================
DISTRICT COURT, COUNTY OF LARIMER, STATE OF COLORADO
Court Address: 201 LAPORTE AVENUE...
Case Number: 2024DR000123
Petitioner: JOHN DOE
Respondent: JANE DOE

============================================================
PART 2: RELIEF SOUGHT SUMMARY
============================================================
- Modify parenting time
- Enforce visitation schedule

============================================================
PART 3: CORRECTED MOTION
============================================================
MOTION TO MODIFY PARENTING TIME

COMES NOW Petitioner, JOHN DOE, and respectfully moves...

SPECIFIC FACTUAL ALLEGATIONS:
1. On November 12, 2025, [incident].
2. On August 29, 2025, [incident].
3. On September 5, 2025, [incident].
4. This pattern of conduct...

============================================================
PART 4: EVIDENCE CHECKLIST
============================================================
[ ] Parenting plan/custody order (REQUIRED)
[ ] Communication logs showing missed exchanges
[ ] Calendar documentation
...

============================================================
PART 5: FULL RESTATEMENT OF PETITIONER'S FACTUAL NARRATIVE
============================================================
[1:1 mapping of all original paragraphs for verification]
```

---

## Known Limitations

1. **Colorado-specific**: City→county mappings only cover major Colorado cities
2. **Date parsing**: Handles common formats but may miss unusual date styles
3. **Relative dates**: "The following week" resolved relative to most recent explicit date
4. **Impact paragraph**: Generated from keywords, not deep semantic understanding

---

## Next Steps / Future Enhancements

1. **More state mappings**: Expand beyond Colorado
2. **Better relative date handling**: Track context across document
3. **Multi-incident deduplication**: Improve similarity detection
4. **Exhibit generation**: Auto-generate referenced exhibits
5. **JDF form auto-fill**: Generate actual fillable PDF forms

---

## Quick Reference

### Server Commands
```bash
# Start server
make start && make celery

# Restart after code changes
pkill -f daphne && make start

# Test health
curl http://localhost:8000/health/ping/
```

### Log Locations
- Daphne: `.daphne.log`
- Celery: `celery.log`
- Django: Console output

### Key Files
```
core/agents/legal/legal_doc_drafter_agent.py  # Main agent
ai_core/templates/components/panels/legal_assistant_panel.html  # UI
core/views_legal.py  # API endpoints
docs/AGENTS.md  # Agent documentation
docs/CAPABILITIES.md  # Feature documentation
```

---

## Session History

| Sub-Session | Focus |
|-------------|-------|
| 404A-B | Initial motion rewriter structure |
| 404C | Motion template refinement |
| 404D | Output structure improvements |
| 404E | Disclaimer removal from court-ready output |
| 404F | County/state inference from addresses |
| Patch 4C | Incident & enumeration normalization |

---

**End of Session 404 Handoff**
