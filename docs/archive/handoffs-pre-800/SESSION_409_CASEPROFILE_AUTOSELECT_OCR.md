# Session 409 Handoff: CaseProfile Auto-Select + OCR Support

**Date:** December 10, 2025
**Status:** Production Ready - Sent to Real Colorado Lawyer for Review!

---

## Summary

Session 409 focused on critical bugfixes that prevented the Legal Assistant from properly using CaseProfile data (including opposing counsel info) when generating motions. Also added OCR support for scanned PDFs and mythology validation to prevent hallucinations.

---

## Key Fixes Applied

### 1. Mythology Validation (Anti-Hallucination)

**Problem:** `LegalDocDrafterAgent` was NOT calling `_validate_output()` - critical hallucination prevention gap.

**Fix:** Added validation at two return points:
- Line 1183: `result = self._validate_output(result)` in `execute()`
- Line 2764: `result = self._validate_output(result)` in `_execute_denied_motion_pipeline()`

**File:** `core/agents/legal/legal_doc_drafter_agent.py`

### 2. Document Brain Case Dropdown

**Problem:** Cases from Case Setup not appearing in Document Brain dropdown.

**Root Cause:**
- Frontend checked `if (data.success && data.cases)` but API returned without `success` field
- Frontend used `c.status === 'Active'` but DB stores `'active'` (lowercase)

**Fixes:**
- **Backend** (`core/views_legal_cases.py`): Added `'success': True` to API responses (lines 44, 69)
- **Frontend** (`legal_assistant_panel.html`): Changed to `const cases = data.cases || []` and `c.status === 'active'`

### 3. Document Upload Authentication

**Problem:** Document upload was using plain `fetch()` without credentials.

**Fix:** Changed `uploadLitigationDocument()` to use `authenticatedFetch()` (line 2741-2745 in `legal_assistant_panel.html`)

### 4. OCR Fallback for Scanned PDFs

**Problem:** Court docket PDFs are often scanned images - PyMuPDF's `page.get_text()` returns empty.

**Fix:** Added OCR fallback in `_extract_pdf_text()` using PyMuPDF rendering + pytesseract:

**File:** `core/services/litigation_brain.py` (lines 284-321)

```python
def _extract_pdf_text_ocr(self, content: bytes) -> str:
    import fitz  # PyMuPDF
    import pytesseract
    from PIL import Image
    import io
    doc = fitz.open(stream=io.BytesIO(content), filetype="pdf")
    text_parts = []
    for page_num, page in enumerate(doc):
        mat = fitz.Matrix(2, 2)  # 2x zoom for better OCR
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        page_text = pytesseract.image_to_string(img)
        text_parts.append(page_text)
    return '\n\n'.join(text_parts)
```

**Dependencies installed:**
- `pytesseract` (Python wrapper)
- `tesseract` system binary (already at `/opt/homebrew/bin/tesseract`)
- Uses PyMuPDF for rendering (NOT poppler - avoids disk space issues)

### 5. CaseProfile Auto-Select Fallback (CRITICAL FIX)

**Problem:** `active_case_id` was stored in session but lost after server restarts. Motion analysis would fall back to document extraction, missing opposing counsel info.

**Symptom:** Conferral emails addressed to "Susannah" (respondent) instead of "Taylor Hartin" (opposing counsel).

**Fix:** Enhanced `_get_active_case_profile_data()` to auto-select user's only active case:

**File:** `core/agents/legal/legal_doc_drafter_agent.py` (lines 4042-4053)

```python
# Session 409: Fallback - if user has ONLY ONE case, use that
if not case and request and hasattr(request, 'user') and request.user.is_authenticated:
    user_cases = CaseProfile.objects.filter(user=request.user, status='active')
    if user_cases.count() == 1:
        case = user_cases.first()
        logger.info(f"Session 409: Using user's only active case: {case.case_number}")
    elif user_cases.count() > 1:
        logger.info(f"Session 409: User has {user_cases.count()} cases - requires explicit selection")
```

**Result:** Users with 1 case automatically get CaseProfile data (including opposing counsel) without needing to click "Use This Case" button.

---

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/legal/legal_doc_drafter_agent.py` | Mythology validation (2 lines), CaseProfile auto-select fallback (12 lines) |
| `core/views_legal_cases.py` | Added `success: true` to API responses |
| `ai_core/templates/components/panels/legal_assistant_panel.html` | Document Brain dropdown fix, `authenticatedFetch()` for uploads |
| `core/services/litigation_brain.py` | OCR fallback method, debug logging |
| `docs/CAPABILITIES.md` | Updated to Session 409 |
| `CLAUDE.md` | Updated Recent Sessions |

---

## Database State

- **CaseProfiles:** 1 (25DR576 - Christopher West v. Susannah West)
- **Opposing Counsel:** Taylor Hartin (Hartin Law, LLC)
- **All migrations applied:** Yes (checked all apps)

---

## Known Issues / Future Work

1. **"My Case Files" tab** - User reported it stopped working during Session 409. Server logs show API returning 200 OK, so likely a frontend JS issue. Needs investigation.

2. **Disk space** - `brew install poppler` failed with "No space left on device". User needs to clean up disk if poppler is needed in the future.

3. **Multiple cases** - If user has >1 case, they must click "Use This Case" button. Could add a case selector dropdown to motion analysis UI.

---

## Testing the Fix

1. Start server: `make start`
2. Go to Legal Assistant > Chat tab
3. Upload a denied motion PDF
4. Click "Analyze"
5. Check server logs for: `Session 409: Using user's only active case: 25DR576`
6. Verify conferral email addresses "Taylor" (opposing counsel), not "Susannah" (respondent)

---

## Lawyer Review

Motion output was sent to a real Colorado family law attorney for review. Awaiting feedback on:
- JDF format compliance
- Legal accuracy of procedural guidance
- Conferral email appropriateness
- Overall usefulness for pro se litigants

---

## Quick Reference

```bash
# Check if CaseProfile is being found
grep "Session 409" server.log | grep -i "case"

# Verify mythology validation
grep "_validate_output" core/agents/legal/legal_doc_drafter_agent.py

# Test OCR
.venv/bin/python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```
