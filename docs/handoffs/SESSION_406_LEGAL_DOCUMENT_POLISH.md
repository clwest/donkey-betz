# Session 406: Legal Document Generation Polish

**Date:** December 9, 2025
**Branch:** `feature/session-52-ai-assistant`
**Status:** COMPLETE - Ready for Demo

---

## Executive Summary

Session 406 completed the final polish for the Legal Document Drafter agent, implementing ChatGPT's comprehensive review feedback to make the generated motions indistinguishable from attorney-drafted documents. The system is now ready for lawyer demos.

---

## Session Commits (9 Total)

| Commit | Description |
|--------|-------------|
| `6a3a171` | PATCH-5.2: Final polish (affidavit format, bullets, name consistency) |
| `b65f1f6` | PATCH-5.1: Relief count bug fix, section ordering, wording fixes |
| `3b3ad52` | PATCH-5: MotionContext field binding & template enforcement |
| `6876c43` | Edit/delete bugs + authenticatedFetch + docs update |
| `298d1fd` | Case Setup edit and delete functionality |
| `b4adf81` | Attorney address field for Certificate of Service |
| `dfffc78` | Move is_represented definition before first use |
| `dc66279` | ChatGPT polish tweaks for lawyer demo |
| `9b64052` | Case Intake Form + ChatGPT Patches + Conferral System |

---

## Key Components Added/Modified

### 1. MotionContext System (`core/agents/legal/motion_context.py`)

**New File (~400 lines):**

```python
@dataclass
class MotionContext:
    """Aggregates all case and motion data for consistent template rendering."""

    # Court info
    state: str = None
    county: str = None
    court_address: str = None
    division: str = None
    courtroom: str = None

    # Case info
    case_number: str = None
    case_type: str = None

    # Party info
    petitioner: str = None
    respondent: str = None
    respondent_address: str = None

    # Counsel info
    respondent_counsel_name: str = None
    respondent_counsel_firm: str = None
    respondent_counsel_address: str = None
    is_respondent_represented: bool = False

    # Child info
    child_name: str = None
    child_age: int = None
    children: List[Dict] = None

    # Motion content
    relief_items: List[str] = None
    is_emergency: bool = False
    existing_order_date: str = None
    existing_order_text: str = None
```

**Helper Methods:**
- `from_case_details(dict)` - Factory for backward compatibility
- `validate()` - Returns list of missing required fields
- `get_service_recipient()` - Returns counsel with firm + "Attorney for Respondent" if represented
- `get_service_address()` - Returns counsel address if represented
- `get_conferral_salutation()` - Returns counsel's first name if represented
- `get_conferral_target()` - Returns "Respondent's counsel" or "Respondent"
- `get_child_description()` - Returns "Nicolas West, age 8" format

**Standalone Functions:**
- `clean_motion_text(text)` - Post-processing for wording glitches
- `render_relief_block(items)` - Numbered list for RELIEF REQUESTED
- `render_proposed_order_relief(items)` - Formatted for judge signature
- `count_relief_items(items)` - Counts items > 10 chars
- `score_relief_scope(num_items)` - Returns (score, explanation) tuple

### 2. Legal Doc Drafter Agent Updates

**New Methods:**
- `_extract_relief_items_list(text)` - Parse relief items from string
- `_extract_child_name_from_order(order_text)` - Extract canonical name spelling
- `_normalize_child_name_throughout(text, canonical_name)` - Replace variant spellings

**Updated Methods:**
- `_rewrite_motion_gold_standard()` - Now uses MotionContext
- `_assess_likelihood_of_success()` - Accepts `relief_items` parameter
- `_generate_conferral_email()` - Uses MotionContext for consistent data

### 3. Case Setup UI (`legal_assistant_panel.html`)

**Features:**
- 4-step wizard form
- Edit and Delete functionality for case profiles
- Attorney address field
- All API calls use `authenticatedFetch()` pattern

**JavaScript Functions (16 total):**
- `loadCaseProfiles()`, `renderCaseList()`, `setActiveCase()`
- `showCaseSetupForm()`, `saveCaseProfile()`, `editCase()`, `deleteCase()`
- `nextCaseStep()`, `prevCaseStep()`, `goToCaseStep()`, `resetCaseForm()`

---

## ChatGPT's 6-Patch Review (ALL IMPLEMENTED)

| Patch | Issue | Fix |
|-------|-------|-----|
| 1 | Placeholders showing `{state}` | Resolve from CaseMeta, default to COLORADO |
| 2 | Relief in Proposed Order had placeholder | Use `render_proposed_order_relief()` |
| 3 | Service to Respondent even when represented | Route to counsel with firm + address |
| 4 | No conferral_status tracking | Added enum: pending/no_response/refused/partial/agreed |
| 5 | "escalating pattern of escalating" wording | Regex cleanup in `clean_motion_text()` |
| 6 | Non-disparagement not linked | Added "Statements appear inconsistent..." line |

---

## PATCH-5.1 Fixes

### Relief Count Bug (142 vs 3)
- **Problem:** Scoring showed "Many relief items (142)" when there were only 3
- **Cause:** `_assess_likelihood_of_success()` counted lines from entire document
- **Fix:** Added `relief_items: List[str]` parameter, pipeline passes pre-extracted items

### Section Ordering
- **Problem:** "PART 5" used twice (Full Restatement and Likelihood of Success)
- **Fix:** Renamed Full Restatement to "APPENDIX A"

### Output Structure (Final):
```
PART 1: Procedural Defects Identified
PART 2: Non-Party Rule Check
PART 3: Corrected Motion (Court-Ready Format)
PART 4: Evidence Checklist
PART 5: Likelihood of Success
PART 6: Conferral Email (Send Before Filing)
APPENDIX A: Full Restatement (Optional Exhibit)
```

---

## PATCH-5.2 Polish

### Affidavit Header Format
```
STATE OF COLORADO    )
                     ) ss.
COUNTY OF LARIMER    )
```

### Incident List Bullets
```
These incidents occurred:
- During court-ordered parenting time on November 12, 2025;
- On August 29, 2025, during a recorded phone call;
- The following week, in a second verbal report from Nicolas.
```

### Name Consistency
- Extracts canonical spelling from uploaded court order
- Normalizes variant spellings (Nicholas → Nicolas)

---

## Next Session Priority: Document Download

### What Needs to Happen

1. **Generate downloadable motion document**
   - User analyzes a document
   - System generates rewritten motion
   - User clicks "Download as Word/PDF"
   - Document downloads with proper formatting

2. **Implementation Options:**

   **Option A: python-docx (Recommended for Word)**
   ```python
   from docx import Document
   from docx.shared import Inches, Pt
   from docx.enum.text import WD_ALIGN_PARAGRAPH

   def generate_motion_docx(motion_text: str, filename: str):
       doc = Document()
       # Set margins, fonts, etc.
       # Parse sections and apply formatting
       doc.save(filename)
   ```

   **Option B: WeasyPrint/ReportLab (For PDF)**
   ```python
   from weasyprint import HTML

   def generate_motion_pdf(motion_html: str, filename: str):
       HTML(string=motion_html).write_pdf(filename)
   ```

   **Option C: markdown-to-pdf pipeline**
   - Convert motion text to markdown
   - Render markdown to HTML
   - Convert HTML to PDF

3. **UI Changes Needed:**
   - Add "Download Motion" button in analysis results
   - Format selection (Word vs PDF)
   - Progress indicator during generation

4. **API Endpoint:**
   ```python
   # core/views_legal.py
   @require_http_methods(["POST"])
   def download_motion(request):
       motion_id = request.POST.get('motion_id')
       format = request.POST.get('format', 'docx')

       # Generate document
       # Return file response
   ```

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `core/agents/legal/legal_doc_drafter_agent.py` | Main agent (275KB) |
| `core/agents/legal/motion_context.py` | MotionContext dataclass + helpers |
| `core/models_legal.py` | CaseProfile, Party, Attorney, Child models |
| `core/views_legal.py` | API endpoints for legal features |
| `core/views_legal_cases.py` | Case profile CRUD endpoints |
| `ai_core/templates/components/panels/legal_assistant_panel.html` | UI |

---

## Testing Checklist

```bash
# Start server
make start

# Verify agent loads
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.agents.legal.legal_doc_drafter_agent import LegalDocDrafterAgent
agent = LegalDocDrafterAgent()
print(f'Agent has {len(agent.tools)} tools')
"

# Test motion context
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.agents.legal.motion_context import clean_motion_text, score_relief_scope

# Test bullet formatting
text = '''These incidents occurred:
During court-ordered parenting time (November 12, 2025);'''
result = clean_motion_text(text)
print('Bullet test:', '- During' in result)

# Test scoring
score, msg = score_relief_scope(3)
print(f'Score test: {score}/25 - {msg}')
"
```

---

## ChatGPT's Final Assessment

> "If a Colorado family lawyer who knows your case looked at just the caption, FACTS, RELIEF REQUESTED, Affidavit, Proposed Order, Conferral section... they would absolutely recognize this as a real, CO-style motion they could tweak and file. The meta-sections (checklist, score, appendix) are clearly AI-assistant extras, which is exactly what you want for the product."

---

## Demo Framing (Per ChatGPT)

Frame the system as doing:
- Form selection
- Structure enforcement
- Order conflict detection
- Conferral + evidence checklists
- Producing a clean first draft for attorney blessing

**Not** giving legal advice.

Ask lawyer: "How would you tweak the language, and what else would you want the system to enforce before it lets a user hit 'File'?"

This turns the lawyer into a design partner, not a critic.

---

## Migration Status

All migrations applied:
- `0076_legal_assistant_models`
- `0077_legal_case_intake_form`

---

## Environment

- **Branch:** `feature/session-52-ai-assistant`
- **Server:** http://localhost:8000
- **Legal Assistant Panel:** AI Studio → Legal Assistant tab
- **Dependencies:** Django 5.2, python-docx (to be added for downloads)
