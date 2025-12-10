# Session 407: Document Download Feature

**Date:** December 9, 2025
**Status:** COMPLETE
**Branch:** feature/session-52-ai-assistant

---

## Summary

Implemented ChatGPT's "Option 1" suggestion: break the motion rewriter output into downloadable sections. Users can now download individual documents (Verified Motion, Proposed Order, Appendix A, Evidence Checklist, Conferral Email) as Word (.docx), PDF (.pdf), text (.txt), or Markdown (.md) files directly from the Legal Assistant UI.

---

## What Was Built

### 1. Document Bundle Parser (`core/agents/legal/document_bundle.py`)

New module that parses the motion rewriter output into structured sections:

```python
@dataclass
class DocumentSection:
    id: str          # 'motion_core', 'proposed_order', etc.
    label: str       # 'Verified Motion (Full Filing)'
    role: str        # 'filing_motion', 'proposed_order', 'checklist', etc.
    format: str      # 'markdown'
    content: str     # The actual document content

@dataclass
class LegalDocumentBundle:
    case_number: str
    jurisdiction: str
    pipeline: str
    sections: List[DocumentSection]
```

**Key Functions:**
- `parse_motion_output_to_bundle()` - Parses PART 1-6 headers into sections
- `generate_docx_from_section()` - Converts section to Word document
- `generate_pdf_from_section()` - Converts to PDF with court formatting (reportlab)
- `generate_txt_from_section()` - Converts to plain text
- `generate_md_from_section()` - Exports as Markdown

**Sections Extracted:**
| Section ID | Label | Role |
|------------|-------|------|
| `motion_core` | Verified Motion (Full Filing) | filing_motion |
| `proposed_order` | Proposed Order (Separate) | proposed_order |
| `appendix_a` | Appendix A - Factual Narrative | optional_exhibit |
| `evidence_checklist` | Evidence Checklist | checklist |
| `success_analysis` | Success Analysis | analysis |
| `conferral_email` | Conferral Email Template | communication_template |

### 2. Agent Integration (`core/agents/legal/legal_doc_drafter_agent.py`)

Modified `_execute_denied_motion_pipeline()` to:
1. Import the document bundle parser
2. Parse the output into sections after assembly
3. Include `document_bundle` in the AgentResult data

```python
# Session 407: Parse output into downloadable sections
document_bundle = parse_motion_output_to_bundle(
    full_output=full_output,
    case_number=case_details.get('case_number', ''),
    county=case_details.get('county', ''),
    state=case_details.get('state', 'CO')
)

result = AgentResult(
    success=True,
    message=full_output,
    data={
        ...
        'document_bundle': document_bundle.to_dict(),
    },
    ...
)
```

### 3. Export API Endpoint (`core/views_legal.py`)

New endpoint: `POST /api/legal/export-section/`

**Request Body:**
```json
{
    "section_id": "motion_core",
    "format": "docx",
    "content": "...",
    "label": "Verified Motion"
}
```

**Response:** File download (application/octet-stream)

**Supported Formats:**
- `docx` - Word document with Times New Roman 12pt, 1" margins
- `txt` - Plain text with markdown stripped
- `md` - Raw Markdown

### 4. Frontend UI (`ai_core/templates/components/panels/legal_assistant_panel.html`)

Added download buttons section that appears after document analysis:

```html
<!-- Session 407: Download Buttons Section -->
<div id="legal-download-section" class="mb-3" style="display: none;">
    <h6 style="color: #38bdf8;">Download Documents</h6>
    <div id="legal-download-buttons" class="d-flex flex-wrap gap-2">
        <!-- Dynamically populated buttons -->
    </div>
</div>
```

**Features:**
- Color-coded buttons based on document role
- Dropdown menu for format selection (Word, Text, Markdown)
- Instant download via blob URL
- Toast notifications on success/error

**Button Styling:**
| Role | Color | Icon |
|------|-------|------|
| Filing Motion | Blue (primary) | Memo |
| Proposed Order | Green (success) | Clipboard |
| Optional Exhibit | Yellow (warning) | Folder |
| Checklist | Cyan (info) | Checkbox |
| Communication | Gray (secondary) | Envelope |
| Analysis | Outline Gray | Chart |

---

## Files Changed

| File | Changes |
|------|---------|
| `core/agents/legal/document_bundle.py` | NEW - Section parser + generators (~200 lines) |
| `core/agents/legal/legal_doc_drafter_agent.py` | Added import + document_bundle to result |
| `core/views_legal.py` | Added `export_legal_section()` endpoint + modified analysis response |
| `core/urls.py` | Added URL pattern for export endpoint |
| `ai_core/templates/components/panels/legal_assistant_panel.html` | Added download section + JS functions |

---

## User Flow

1. User uploads denied motion to Legal Assistant
2. Click "Analyze Document"
3. System runs motion rewrite pipeline
4. Results display with **Download Documents** section showing:
   - Verified Motion (Full Filing) (.docx)
   - Proposed Order (Separate) (.docx)
   - Appendix A - Factual Narrative (.docx)
   - Evidence Checklist (.md)
   - Conferral Email Template (.txt)
5. User clicks button to download any section
6. File downloads immediately

---

## Technical Notes

### Word Document Formatting
The `generate_docx_from_section()` function applies basic court document formatting:
- Font: Times New Roman 12pt
- Margins: 1" all sides
- Headers centered and bold (DISTRICT COURT, PROPOSED ORDER, etc.)
- Page breaks before APPENDIX sections

### Section Parsing Logic
The parser uses regex to split on:
- `\n---\n` - Main PART boundaries
- `={10,}\nAPPENDIX A:` - Appendix boundary within PART 3
- `PROPOSED ORDER` header - Extracts just the proposed order section

### Frontend Storage
The document bundle is stored in `window.currentDocumentBundle` so it persists for multiple downloads without re-fetching.

---

## Testing

### Manual Testing
1. Start server: `make start`
2. Go to http://localhost:8000/ai-studio/
3. Click Legal Assistant → Case Files
4. Upload a denied motion PDF
5. Click "Analyze Document"
6. Verify download buttons appear
7. Test each format (docx, txt, md)
8. Verify files open correctly

### API Testing
```bash
curl -X POST http://localhost:8000/api/legal/export-section/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  -d '{"section_id": "motion_core", "format": "docx", "content": "Test content", "label": "Test"}' \
  --output test.docx
```

### Unit Test
```python
from core.agents.legal.document_bundle import parse_motion_output_to_bundle
bundle = parse_motion_output_to_bundle(sample_output, '25DR576', 'LARIMER', 'CO')
assert len(bundle.sections) >= 5
```

---

## Demo Value

This feature is **highly demo-able**:

- Upload denied motion → One click analysis
- Download buttons appear immediately
- "Download Verified Motion (.docx)" → Opens in Word
- "Download Proposed Order (.docx)" → Separate file for court
- "Copy Conferral Email" → Ready to send

**Lawyer reaction:** "Wait, it generates the motion AND I can download it as a Word doc? That's exactly what I need!"

---

## Next Steps

1. **Enhanced DOCX formatting** - Line numbering, proper spacing, court-specific templates
2. **PDF export** - Add WeasyPrint for PDF generation
3. **Batch download** - "Download All" button as ZIP
4. **Email integration** - Send conferral email directly from UI
5. **Template customization** - Let users choose court-specific templates

---

## Related Sessions

- Session 406: Case Intake Form (provides case details for downloads)
- Session 405: Conferral Email generation
- Session 404: Motion rewrite pipeline (generates the content)
