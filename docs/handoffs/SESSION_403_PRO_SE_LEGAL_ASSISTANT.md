# Session 403: Pro Se Legal Assistant MVP

**Date:** December 9, 2025
**Status:** Phase 1 + Phase 2 + Phase 3 Complete ✅
**Focus:** Colorado Divorce with Children + Case File Upload/Analysis

---

## Summary

Implemented the Pro Se Legal Assistant MVP for Colorado family law. This agent provides **general legal information only** (NOT legal advice) to help self-represented litigants understand procedures, locate forms, and draft template documents.

---

## What Was Built

### 1. New Spiders (Playwright-enabled)

| Spider | Location | Purpose |
|--------|----------|---------|
| `colorado_family_law` | `ai_core/spiders/specialized/colorado_family_law_spider.py` | Colorado JDF forms (12 key forms with fallback data) |
| `justia_family_law` | `ai_core/spiders/specialized/justia_playwright_spider.py` | Justia family law content (Cloudflare bypass) |

Both spiders:
- Use Playwright for JavaScript-rendered content
- Have anti-detection measures
- Include fallback data for reliability
- Are registered in spider_registry.py

### 2. LegalDocDrafterAgent

**Location:** `core/agents/legal/legal_doc_drafter_agent.py`

A comprehensive agent with:
- **System prompt** with legal safeguards
- **6 tools**: search_legal_resources, draft_motion, draft_email, draft_declaration, get_form_info, explain_procedure
- **Colorado JDF form database** (embedded dictionary)
- **Template generators** for all document types
- **Legal disclaimers** (LEGAL_DISCLAIMER constant) in every response

**Document Types:**
- `guidance`: General legal information
- `motion`: Court filing templates (continuance, modification, enforcement, etc.)
- `email`: Meet-and-confer professional correspondence
- `declaration`: Sworn statement templates
- `checklist`: Step-by-step procedural guides

**Case Types Covered:**
- Divorce (dissolution of marriage)
- Custody (allocation of parental responsibilities)
- Child support
- Parenting time (visitation)
- Modification
- Enforcement

### 3. Wiring & Integration

| Component | File | Changes |
|-----------|------|---------|
| Package | `core/agents/legal/__init__.py` | Created with LegalDocDrafterAgent export |
| Router | `core/agent_router.py` | Added import and AGENT_MAP entry |
| Tool Definition | `core/assistant/tool_definitions.py` | Added `_get_legal_doc_drafter_agent_definition()` |
| Tool Description | `core/prompts/tool_descriptions.py` | Added comprehensive description with disclaimers |
| Personal Assistant | `core/agents/personal_assistant_agent.py` | Added 33 legal keywords, priority routing, delegate enum |

### 4. Routing Tested

All these queries correctly route to LegalDocDrafterAgent:
- "How do I file for divorce in Colorado?"
- "What forms do I need for custody modification?"
- "Draft a motion to continue my hearing"
- "Help me with a child support calculation"
- "I was served divorce papers, what should I do?"
- "What are the parenting time guidelines?"
- "Help me draft a motion to modify parenting time"
- "Explain the custody modification process"
- "What is the JDF 1113 form?"
- "I need help with family court"

---

## Key Files Modified/Created

```
# Created (Phase 1-2)
core/agents/legal/__init__.py
core/agents/legal/legal_doc_drafter_agent.py
ai_core/spiders/specialized/colorado_family_law_spider.py
ai_core/spiders/specialized/justia_playwright_spider.py
docs/SESSION_403_LEGAL_ASSISTANT_GAP_ANALYSIS.md
docs/handoffs/SESSION_403_PRO_SE_LEGAL_ASSISTANT.md

# Created (Phase 3)
core/views_legal.py (518 lines - Complete legal case files API)

# Modified (Phase 1-2)
ai_core/spiders/spider_registry.py (added 2 spiders)
core/agent_router.py (added LegalDocDrafterAgent)
core/assistant/tool_definitions.py (added tool definition)
core/prompts/tool_descriptions.py (added tool description)
core/agents/personal_assistant_agent.py (added keywords, routing, delegate enum)

# Modified (Phase 3)
ai_core/templates/components/panels/legal_assistant_panel.html (added My Case Files sub-tab)
core/urls.py (added 5 legal API routes)
core/agents/legal/legal_doc_drafter_agent.py (added document context injection)
docs/CAPABILITIES.md (added Pro Se Legal Assistant section)
docs/AGENTS.md (updated LegalDocDrafterAgent documentation)
```

---

## Legal Disclaimers

Every response from LegalDocDrafterAgent includes:

```
⚠️ IMPORTANT DISCLAIMER
This is GENERAL LEGAL INFORMATION only, NOT legal advice.
This does NOT create an attorney-client relationship.
Laws vary by jurisdiction and change over time.
Always consult a licensed Colorado attorney for your specific situation.
```

---

## Phase 2: UI Panel Complete ✅

### Legal Assistant Tab
**Location:** `ai_core/templates/components/panels/legal_assistant_panel.html`

Created comprehensive UI panel (~43KB) with:

**Main Features:**
- Prominent disclaimer banner (red warning)
- Stats cards row (Colorado, JDF Forms, Case Types, Doc Types, Legal Spiders, Pro Se)
- 4 sub-tabs: Guidance, Documents, Colorado Forms, Procedures

**Guidance Sub-Tab:**
- Query input textarea
- Case type dropdown (divorce, custody, child_support, etc.)
- Document type dropdown (guidance, motion, email, declaration, checklist)
- Submit button → routes to LegalDocDrafterAgent via chat API
- Results display with copy functionality

**Documents Sub-Tab:**
- Motion templates (Continuance, Modify Parenting Time, Modify Child Support, Enforce Order)
- Other documents (Meet-and-Confer Email, Declaration Template, Checklists)
- Document preview with copy/download buttons

**Colorado Forms Sub-Tab:**
- JDF Form cards organized by category (Divorce, Custody, Child Support)
- Form info popup with description and official link
- 10 key forms: JDF 1101, 1102, 1111, 1115, 1113, 1220, 1221, 1820, 1821, 1000

**Procedures Sub-Tab:**
- Filing procedures (Divorce, File Motion, Modify Parenting Time, Prepare for Hearing)
- Important resources with external links (Colorado Courts, Bar Association, Legal Services)
- Procedure explanation display

**JavaScript Functions:**
- `submitLegalQuery()` - Sends query to chat API with agent hint
- `generateLegalDoc()` - Generates document templates
- `showFormInfo()` - Displays JDF form information
- `explainProcedure()` - Explains court procedures
- `copyLegalResult()`, `copyLegalDoc()`, `downloadLegalDoc()` - Copy/download utilities

### Navigation Tab Added
**Location:** `ai_core/templates/ai_image_studio.html:1670-1675`

```html
<li class="nav-item" role="presentation">
    <button class="nav-link" id="legal-assistant-tab" data-bs-toggle="tab"
            data-bs-target="#legal-assistant" type="button" role="tab"
            title="Pro Se Legal Assistant - Colorado Family Law">
        ⚖️ Legal
    </button>
</li>
```

### Panel Include Added
**Location:** `ai_core/templates/ai_image_studio.html:14032-14036`

```html
{% include "components/panels/legal_assistant_panel.html" %}
```

---

## Phase 3: Case Files Upload & Analysis ✅

### Database Models (Migration 0076)

| Model | Purpose |
|-------|---------|
| `LegalCase` | User's case info (parties, case number, dates, status) |
| `LegalDocument` | Generated/uploaded documents with content storage |
| `LegalResearchResult` | Saved legal research with embeddings |
| `LegalMemory` | Legal-specific learning patterns |

### API Endpoints (core/views_legal.py)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/legal/case-files/` | GET | List all case files with stats |
| `/api/legal/case-files/upload/` | POST | Upload PDF/DOC/TXT file |
| `/api/legal/case-files/<uuid>/` | GET | Get document details |
| `/api/legal/case-files/<uuid>/analyze/` | POST | AI analysis |
| `/api/legal/case-files/<uuid>/delete/` | DELETE | Delete document |

### My Case Files Sub-Tab

Added 5th sub-tab to Legal Assistant panel with:

**UI Components:**
- Stats cards (Total Files, Court Orders, Motions, Processed)
- Drag-and-drop upload zone (10MB max, PDF/DOC/TXT/DOCX)
- Document type selector (Court Order, Denied Motion, Motion, Correspondence, etc.)
- Optional context input for additional info
- Document library table with status badges
- Analysis panel with 4 sections (Summary, Issues, Recommendations, Forms)

**JavaScript Functions:**
- `loadLegalCaseFiles()` - Fetches documents from API
- `uploadLegalCaseFile()` - Handles file upload with FormData
- `viewLegalCaseFile(docId)` - Gets document details
- `analyzeLegalCaseFile(docId)` - Triggers AI analysis
- `deleteLegalCaseFile(docId)` - Deletes document
- `showDocumentAnalysis()` - Displays analysis results
- `askAboutDocument()` - Follow-up question workflow
- `generateCorrectiveFiling()` - Generate refiling based on analysis

### Agent Enhancements

- `_get_uploaded_document_context()` method in LegalDocDrafterAgent
- Regex pattern matching for document IDs in task text
- Auto-injection of uploaded documents into prompts
- Falls back to recent denied motions/court orders if no specific document

### Primary Use Case

Upload a denied motion PDF and magistrate's denial letter to:
1. Get AI analysis of why it was denied
2. Receive recommendations on correct JDF forms
3. Generate properly formatted corrective filing

---

## What's Next (Phase 4 - Optional)

1. **Enhanced Corrective Filing** - Structured form-filling templates
2. **Document Pinning** - Reference specific documents in ongoing chat
3. **OCR Support** - Handle scanned PDF documents
4. **Case Timeline** - Visual timeline of case events from documents
5. **Auto-Detection** - Automatically detect document type from content

---

## Testing

Run the verification:
```bash
.venv/bin/python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from core.agents.legal import LegalDocDrafterAgent
from core.agent_router import AgentRouter

router = AgentRouter()
print(f'LegalDocDrafterAgent registered: {router.is_valid_agent(\"LegalDocDrafterAgent\")}')
"
```

---

## Architecture Notes

The LegalDocDrafterAgent follows the clean architecture pattern:
- Inherits from BaseAgent (with TimeTravelMixin)
- Uses GPT function calling with 6 specialized tools
- Integrates with spider network for legal data
- Records decisions for debugging (Time Travel)
- Generates knowledge attribution for transparency

---

## Important Safeguards

1. **No specific legal advice** - Only general information
2. **Attorney recommendation** - Every response recommends consulting a lawyer
3. **Jurisdiction clarity** - Focused on Colorado, warns about other jurisdictions
4. **Urgent matter warnings** - Recommends immediate legal help for urgent situations
5. **No criminal law** - Explicitly excluded from scope

---

## Known Issues / Areas for Tweaking

### UI/UX
1. **Loading States** - Upload zone needs better loading indicator during processing
2. **Error Messages** - Some error messages could be more user-friendly
3. **Document Preview** - Full document content preview in modal could be improved

### Functionality
1. **Document Type Auto-Detection** - Currently manual; could analyze content
2. **Corrective Filing Button** - Currently sends generic chat message; needs structured template
3. **Follow-up Questions** - "Ask a follow-up question" needs document context preservation
4. **Embedding Generation** - Queued via Celery; should verify RAG search works

### Technical
1. **DOC File Support** - Legacy .doc files use fallback text extraction
2. **Scanned PDFs** - No OCR support yet; only text-based PDFs work
3. **File Size Limit** - 10MB may be too small for complex legal documents
4. **Analysis Prompt** - Could be more specific per document type

---

## Testing Checklist

- [ ] Upload PDF and verify text extraction
- [ ] Upload DOCX and verify text extraction
- [ ] Upload TXT file directly
- [ ] Test file size validation (>10MB rejection)
- [ ] Test invalid file type rejection
- [ ] Test document analysis with denied motion
- [ ] Test document analysis with court order
- [ ] Verify document appears in document library
- [ ] Test delete document
- [ ] Test "Ask a follow-up question" workflow
- [ ] Test "Generate corrective filing" workflow
- [ ] Verify embeddings are generated (check Celery logs)

---

## Quick Start for Next Session

```bash
# Start services
make start
make celery

# Access Legal Assistant
open http://localhost:8000/ai-studio/
# Click "Legal Assistant" tab
# Click "My Case Files" sub-tab

# Test upload
# Drag a PDF to the upload zone
# Select document type (e.g., "Denied Motion")
# Click "Upload & Process"
# Click "Analyze Document" after upload completes
```
