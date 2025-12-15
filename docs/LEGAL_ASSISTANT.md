# Legal Assistant - Colorado Family Law

**Built:** Sessions 403-410 (December 9-10, 2025)
**Location:** `core/agents/legal/legal_doc_drafter_agent.py`
**Status:** Production-ready, sent to real Colorado lawyer for review

---

## Executive Summary

A complete pro se legal assistant for Colorado family law cases, featuring:
- Case intake forms with party/attorney/child management
- Document upload with OCR for scanned PDFs
- Motion analysis and JDF-format rewriting
- Document threading (motion -> response -> reply)
- Conferral email generation addressing opposing counsel
- **Mythology validation** to prevent hallucinations

---

## Features

### 1. Case Intake Form (Session 406)

4-step wizard for case setup:

**Step 1: Case Information**
- Case number
- Court name
- Case type (divorce, custody, etc.)
- Filing date

**Step 2: Parties**
- Petitioner name and info
- Respondent name and info
- Party representation status

**Step 3: Children**
- Child names and DOBs
- Current custody arrangement
- Special needs/considerations

**Step 4: Attorneys**
- Opposing counsel information
- Bar number
- Contact details

### 2. Document Upload & OCR (Session 409)

**Supported Formats:**
- PDF (text extraction)
- Scanned PDFs (OCR via pytesseract)
- Word documents
- Text files

**OCR Pipeline:**
```python
# If PyMuPDF text extraction fails
if not text.strip():
    # Convert to images with pdftoppm
    # Run tesseract OCR on each page
    # Combine extracted text
```

### 3. Motion Analysis (Session 404)

**Tool: `analyze_denied_motion`**

Identifies deficiencies in denied motions:
- Missing legal standards
- Procedural errors
- Insufficient evidence
- JDF formatting issues

### 4. Motion Rewriting (Session 404)

**Tool: `rewrite_motion`**

Generates JDF-compliant motions with:
- Proper caption format
- Numbered paragraphs
- Legal citations
- Evidence references
- Proposed order attachment

### 5. Document Threading (Session 410)

**`litigation_role` Field:**
- `motion` - Original motion
- `response` - Response to motion
- `reply` - Reply to response
- `order` - Court order
- `exhibit` - Supporting exhibit
- `other` - Other document types

**API Endpoints:**
- `GET /api/legal/document-threads/<case_id>/` - Get document threads
- `GET /api/legal/document-thread/<doc_id>/` - Get thread for document
- `GET /api/legal/response-candidates/<doc_id>/` - Get documents needing response

### 6. Draft Response Tab (Session 410)

**Config Panel:**
- Select source document
- Choose response type
- Set party filter
- Configure analysis depth

**Preview Panel:**
- Generated response content
- Section breakdown
- Export options

### 7. Conferral Emails (Session 405-409)

**Tool: `draft_email`**

Generates meet-and-confer emails:
- Properly addresses opposing counsel (not respondent!)
- Professional tone
- Cites relevant rules
- Includes deadline calculation

**Key Fix (Session 409):**
```python
# Before: Addressed to respondent "Taylor Hartin"
# After: Addressed to opposing counsel "Katherine Reilly, Esq."
```

### 8. Mythology Validation (Session 409)

**Problem:** LLM would hallucinate legal terms and procedures.

**Solution:** Added `_validate_output()` at lines 1183 and 2764:
```python
def _validate_output(self, content):
    """Check for hallucinated legal terms"""
    mythology_terms = [
        'Colorado Revised Statutes Section 99.999',
        'Form JDF-9999',
        # ... known hallucination patterns
    ]
    for term in mythology_terms:
        if term in content:
            # Flag for review or regenerate
```

---

## Database Models

### CaseProfile

```python
class CaseProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    case_number = models.CharField(max_length=100)
    court_name = models.CharField(max_length=255)
    case_type = models.CharField(max_length=50, choices=CASE_TYPES)
    filing_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
```

### Party

```python
class Party(models.Model):
    case = models.ForeignKey(CaseProfile, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)  # petitioner, respondent
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_pro_se = models.BooleanField(default=False)
```

### Attorney

```python
class Attorney(models.Model):
    case = models.ForeignKey(CaseProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    bar_number = models.CharField(max_length=50, blank=True)
    firm_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    represents = models.CharField(max_length=50)  # petitioner, respondent
```

### Child

```python
class Child(models.Model):
    case = models.ForeignKey(CaseProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    special_needs = models.TextField(blank=True)
```

### LitigationDocument

```python
class LitigationDocument(models.Model):
    case = models.ForeignKey(CaseProfile, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=50)
    litigation_role = models.CharField(max_length=50)  # motion, response, reply, order, exhibit
    content = models.TextField()
    file = models.FileField(upload_to='legal_documents/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    parent_document = models.ForeignKey('self', null=True, blank=True)  # For threading
```

---

## LegalDocDrafterAgent

**Location:** `core/agents/legal/legal_doc_drafter_agent.py`
**Lines:** ~3,000

### Tools (12 total)

| Tool | Purpose |
|------|---------|
| `search_legal_resources` | Search spider network for legal info |
| `draft_motion` | Generate motion templates |
| `draft_email` | Meet-and-confer emails |
| `draft_declaration` | Declaration templates |
| `get_form_info` | Colorado JDF form information |
| `explain_procedure` | Court procedures |
| `analyze_denied_motion` | Identify deficiencies |
| `rewrite_motion` | JDF format rewrite |
| `generate_evidence_checklist` | Exhibit requirements |
| `check_non_party_issues` | Non-party relief detection |
| `auto_rewrite_third_party` | Auto-fix third party issues |
| `detect_emergency` | Emergency motion detection |

### System Prompt

```python
SYSTEM_PROMPT = """You are a Colorado family law legal assistant helping pro se litigants.

Your role is to:
1. Help draft motions in proper JDF format
2. Analyze denied motions and identify deficiencies
3. Generate conferral emails addressing opposing counsel
4. Create evidence checklists
5. Explain procedures in plain language

CRITICAL RULES:
- Never provide legal advice
- Always recommend consulting an attorney for complex matters
- Use Colorado-specific forms and procedures
- Address conferral emails to opposing counsel, not parties
- Validate all citations against known Colorado law
"""
```

---

## UI Components

### Legal Assistant Panel

**Location:** `ai_core/templates/components/panels/legal_assistant_panel.html`

**Tabs:**
1. **My Cases** - List and manage cases
2. **Case Files** - Documents for selected case
3. **Document Brain** - Upload and analyze documents
4. **Draft Response** - Generate responses to filings

### Key Features

**Case Selector:**
- Dropdown with active cases
- Auto-select if only one case (Session 409 fix)
- Session persistence

**Document Upload:**
- Drag-and-drop interface
- Progress indicator
- OCR status display

**Analysis Results:**
- Collapsible sections
- Copy to clipboard
- Export options (Word, PDF, Text, Markdown)

---

## API Endpoints

### Case Management

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/legal/cases/` | List user's cases |
| POST | `/api/legal/cases/` | Create new case |
| GET | `/api/legal/cases/<id>/` | Get case details |
| PUT | `/api/legal/cases/<id>/` | Update case |
| DELETE | `/api/legal/cases/<id>/` | Delete case |

### Document Management

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/legal/documents/<case_id>/` | List case documents |
| POST | `/api/legal/documents/<case_id>/upload/` | Upload document |
| GET | `/api/legal/documents/<id>/` | Get document |
| DELETE | `/api/legal/documents/<id>/` | Delete document |

### Analysis & Generation

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/legal/analyze-motion/` | Analyze motion |
| POST | `/api/legal/rewrite-motion/` | Rewrite motion |
| POST | `/api/legal/draft-response/` | Draft response |
| POST | `/api/legal/draft-conferral/` | Generate conferral email |

### Document Threading (Session 410)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/legal/document-threads/<case_id>/` | Get all threads |
| GET | `/api/legal/document-thread/<doc_id>/` | Get thread for document |
| GET | `/api/legal/response-candidates/<doc_id>/` | Get needs-response docs |

---

## Document Download (Session 407)

**Location:** `core/views_legal.py` - `export_legal_section()`

**Exportable Sections:**
- Verified Motion
- Proposed Order
- Appendix A
- Evidence Checklist
- Conferral Email

**Export Formats:**
- `.docx` (Word) - Uses python-docx
- `.txt` (Plain text)
- `.md` (Markdown)
- `.pdf` (PDF) - Future enhancement

---

## Spider Integration

### Legal Spiders

| Spider | Source | Data |
|--------|--------|------|
| `colorado_courts_spider` | Colorado Judicial | Court forms, procedures |
| `justia_spider` | Justia | Case law, statutes |
| `colorado_statutes_spider` | Colorado.gov | Revised statutes |
| `family_law_spider` | Various | Family law resources |

### Knowledge Pipeline

```
Legal Spiders
    ↓
SpiderData (legal category)
    ↓
Embeddings (text-embedding-3-small)
    ↓
LegalDocDrafterAgent._get_relevant_knowledge_for_task()
    ↓
Injected into agent prompts
```

---

## Session History

| Session | Focus | Key Changes |
|---------|-------|-------------|
| 403 | MVP | Basic case files, document upload, PDF extraction |
| 404 | Motion Rewriter | Analyze + rewrite pipeline, JDF format, 12 tools |
| 405 | ChatGPT Enhancements | 5 new tools, conferral emails |
| 406 | Case Intake Form | 4-step wizard, CaseProfile model, party management |
| 407 | Document Download | Export sections as Word/Text/Markdown |
| 408 | Document Brain | Analysis interface, case dropdown |
| 409 | OCR + Fixes | Scanned PDF support, mythology validation, auto-select |
| 410 | Threading | litigation_role field, response drafting UI |

---

## Known Limitations

1. **Colorado-specific** - Only Colorado family law, not other states
2. **No attorney review** - Outputs need human review
3. **OCR quality** - Depends on scan quality
4. **No e-filing** - Cannot file directly with courts
5. **English only** - No Spanish/other language support

---

## Future Enhancements

### Planned
- [ ] Direct e-filing integration (Colorado Courts E-Filing)
- [ ] Spanish language support
- [ ] Automated deadline tracking
- [ ] Court calendar integration
- [ ] Attorney review workflow

### Wishlist
- Multi-state support
- AI-powered legal research
- Document comparison
- Hearing preparation assistant
- Settlement calculator

---

## Lawyer Feedback

**Status:** Sent to real Colorado family lawyer for review (Session 409)
**Feedback:** Pending

Key questions for lawyer:
1. Is the JDF format correct?
2. Are citations accurate?
3. Is the tone appropriately professional?
4. Any critical missing elements?

---

## Related Documentation

- [AGENTS.md](AGENTS.md) - LegalDocDrafterAgent details
- [docs/handoffs/SESSION_403_PRO_SE_LEGAL_ASSISTANT.md](handoffs/SESSION_403_PRO_SE_LEGAL_ASSISTANT.md)
- [docs/handoffs/SESSION_404_PRO_SE_LEGAL_ASSISTANT.md](handoffs/SESSION_404_PRO_SE_LEGAL_ASSISTANT.md)
- [docs/handoffs/SESSION_409_CASEPROFILE_AUTOSELECT_OCR.md](handoffs/SESSION_409_CASEPROFILE_AUTOSELECT_OCR.md)
- [docs/handoffs/SESSION_410_DOCUMENT_THREADING_RESPONSE_SESSION.md](handoffs/SESSION_410_DOCUMENT_THREADING_RESPONSE_SESSION.md)
