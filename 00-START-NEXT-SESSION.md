# Start Next Session Here

**Last Session:** 406 - Legal Document Generation Polish COMPLETE!
**Date:** December 9, 2025
**Status:** Lawyer-ready motions | 9 commits | MotionContext system | Ready for download feature

---

## Session 406 Accomplishments

### MAJOR: MotionContext System (PATCH-5)

Created `core/agents/legal/motion_context.py` (~400 lines):

| Component | Purpose |
|-----------|---------|
| `MotionContext` dataclass | Aggregates all case/motion data for consistent rendering |
| `clean_motion_text()` | Post-processing for wording glitches |
| `render_relief_block()` | Numbered list for RELIEF REQUESTED section |
| `score_relief_scope()` | Relief counting with scoring (1-3 items = 22pts) |

### ChatGPT's 6 Patches + Final Polish

| Patch | Fix |
|-------|-----|
| **1** | Resolve placeholders from CaseMeta |
| **2** | Relief in Proposed Order (full items) |
| **3** | Service goes to counsel if represented |
| **4** | conferral_status enum |
| **5** | Wording glitch fixes |
| **6** | Non-disparagement linkage |
| **5.1** | Relief count bug (142 vs 3) |
| **5.2** | Affidavit format, bullets, name consistency |

### All 9 Commits

| Commit | Description |
|--------|-------------|
| `6a3a171` | PATCH-5.2: Final polish (affidavit, bullets, names) |
| `b65f1f6` | PATCH-5.1: Relief count bug, section ordering |
| `3b3ad52` | PATCH-5: MotionContext field binding |
| `6876c43` | Edit/delete bugs + authenticatedFetch |
| `298d1fd` | Case Setup edit and delete |
| `b4adf81` | Attorney address field |
| `dfffc78` | Variable order fix |
| `dc66279` | ChatGPT polish tweaks |
| `9b64052` | Case Intake Form + Conferral System |

### Output Structure (Final)

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

## Next Session: 407 - Document Download

### Priority 1: Make Documents Downloadable

**User Flow:**
1. User uploads denied motion
2. System generates rewritten motion
3. User clicks "Download as Word" or "Download as PDF"
4. Document downloads with proper court formatting

**Implementation Options:**

**Option A: python-docx for Word (Recommended)**
```python
pip install python-docx

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def generate_motion_docx(motion_text: str, filename: str):
    doc = Document()
    # Parse sections, apply court formatting
    doc.save(filename)
```

**Option B: WeasyPrint for PDF**
```python
pip install weasyprint

from weasyprint import HTML

def generate_motion_pdf(motion_html: str, filename: str):
    HTML(string=motion_html).write_pdf(filename)
```

**Tasks:**
1. Add `python-docx` dependency
2. Create document generation service
3. Add download button to UI
4. Create API endpoint for download
5. Apply proper court formatting (margins, fonts, spacing)

### Priority 2: Active Case Indicator

Show in UI which case is currently active for analysis.

### Priority 3: Auto-populate from OCR

Extract case details from uploaded court orders.

---

## Quick Start

```bash
# Start services
make start && make celery

# Test Legal Assistant
open http://localhost:8000/ai-studio/
# Navigate to Legal Assistant tab

# Run tests
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.agents.legal.motion_context import clean_motion_text, score_relief_scope
print('Score test:', score_relief_scope(3))  # Should be (22, 'Focused relief requests...')
"
```

---

## ChatGPT's Final Assessment

> "If a Colorado family lawyer who knows your case looked at just the caption, FACTS, RELIEF REQUESTED, Affidavit, Proposed Order, Conferral section... they would absolutely recognize this as a real, CO-style motion they could tweak and file."

**Demo Framing:**
- Frame as form selection + structure enforcement + conflict detection
- NOT as giving legal advice
- Ask lawyer: "What would you want the system to enforce before letting a user hit 'File'?"

---

## Key Files

| File | Purpose |
|------|---------|
| `core/agents/legal/legal_doc_drafter_agent.py` | Main agent (275KB, 15 tools) |
| `core/agents/legal/motion_context.py` | MotionContext dataclass + helpers |
| `core/models_legal.py` | Case management models |
| `core/views_legal_cases.py` | Case profile CRUD API |
| `docs/handoffs/SESSION_406_LEGAL_DOCUMENT_POLISH.md` | Full session details |

---

## System Status

| Component | Count/Status |
|-----------|--------------|
| Registered Spiders | 64 |
| Clean Agents | 27 |
| Legal Tools | 15 |
| Session 406 Commits | 9 |
| Motion Quality | Lawyer-ready |

---

## Previous Sessions

- Session 406: Legal Document Polish (THIS SESSION!)
- Session 405: ChatGPT-recommended enhancements (5 tools)
- Session 404: Pro Se Legal Assistant motion rewriter
- Session 403: Legal Assistant MVP
- Session 400: Agent knowledge pipeline

---

**Always read this file first when starting a new session!**
