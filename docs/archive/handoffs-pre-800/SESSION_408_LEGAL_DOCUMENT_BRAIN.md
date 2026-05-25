# Session 408: Legal Document Brain - Multi-Document Litigation Management

**Date:** December 9, 2025
**Status:** Complete
**Focus:** Multi-document ingestion, case knowledge graph, auto-response generation

---

## Summary

Implemented a comprehensive Legal Document Brain system that enables users to upload ALL case documents (court orders, motions, responses, evidence, court rules), automatically builds a Case Knowledge Graph linking everything together, detects contradictions between documents, and generates court-ready responses to opposing party filings.

This transforms the Legal Assistant from a single-document tool into a full litigation case management system.

---

## What Was Built

### 1. Database Models (`core/models_legal.py`)

**New Models Added:**

| Model | Purpose |
|-------|---------|
| `LitigationDocument` | Extended document model with 5 categories, 25+ document types |
| `CaseKnowledgeGraph` | The "case_context.json" - stores extracted knowledge from all documents |
| `DocumentRelationship` | Links documents (responds_to, contradicts, supports, etc.) |
| `GeneratedResponse` | Stores auto-generated responses with all components |
| `ExhibitList` | Auto-generated exhibit lists |
| `CaseMemorandum` | High-level case summaries |

**Document Categories:**
1. **Court Orders:** Temporary Orders, Prior Parenting, Status Quo, Restrictions, Emergency Rulings
2. **Motions:** My Motion, Opposing Motion, Pending Motion
3. **Responses/Replies:** Response, Reply, Exhibit Attachment, Affidavit
4. **Evidence:** Messages, Call Logs, Calendars, Photos, Transcripts, Notes
5. **Court Rules:** C.R.C.P., JDF Forms, Local Standards, Division Requirements

### 2. Processing Services (`core/services/litigation_brain.py`)

**Four Main Components:**

| Service | Purpose |
|---------|---------|
| `LegalDocumentIngestor` | Processes uploads, extracts text (PDF/DOCX/TXT), auto-classifies documents |
| `LegalContextBuilder` | Builds the Case Knowledge Graph - extracts parties, timeline, allegations, contradictions |
| `LegalResponseWriter` | Generates responses with Admit/Deny/Insufficient, legal standard, argument, relief |
| `LegalFilingPackager` | Bundles documents for filing (Response, Proposed Order, Exhibit List, etc.) |

**Knowledge Graph Extracts:**
- Parties and their roles
- Timeline of events from all documents
- Allegations by each party
- Legal issues identified
- Claims and counterclaims
- Relief requested per motion
- Evidence referenced
- **Cross-document contradictions**
- Procedural posture
- Response deadlines (21-day rule)
- Unaddressed issues
- Misinformation flags

### 3. API Endpoints (`core/views_legal.py`)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/legal/litigation/<case_id>/documents/` | GET | List all documents organized by category |
| `/api/legal/litigation/<case_id>/documents/upload/` | POST | Upload and process document |
| `/api/legal/litigation/<case_id>/knowledge-graph/` | GET | Get case knowledge graph |
| `/api/legal/litigation/<case_id>/knowledge-graph/rebuild/` | POST | Force rebuild of knowledge graph |
| `/api/legal/litigation/<case_id>/responses/` | GET | List auto-generated responses |
| `/api/legal/litigation/<doc_id>/generate-response/` | POST | Generate response to a filing |
| `/api/legal/litigation/response/<response_id>/` | GET | Get full response details |
| `/api/legal/litigation/response/<response_id>/package/` | POST | Create filing package |
| `/api/legal/litigation/document-types/` | GET | Get all document type options |

### 4. Frontend UI (`legal_assistant_panel.html`)

**New "Document Brain" Tab** with 6 inner tabs:

1. **Court Orders** - Upload temporary orders, parenting orders, restrictions
2. **Motions** - Upload your motions and opposing party's motions
3. **Responses** - Upload opposing party's responses, exhibits, affidavits
4. **Evidence** - Upload messages, call logs, photos, transcripts
5. **Knowledge Graph** - View extracted parties, contradictions, timeline, deadlines
6. **Auto-Generated** - View and download generated responses

**Features:**
- Case selector dropdown
- Upload modal with document type selection
- "Generate Response" button on opposing party's motions
- Real-time knowledge graph visualization
- Filing package download

---

## How It Works

### Upload Flow
1. User selects a case in Document Brain
2. User clicks "Upload" on appropriate category tab
3. Modal opens with document type options, filing party, dates
4. Document is uploaded and processed:
   - Text extracted (PDF via PyMuPDF, DOCX via python-docx)
   - Document type auto-detected if not specified
   - Filing party detected from content
   - Metadata extracted (dates, parties, allegations, relief)
5. Knowledge graph marked for rebuild

### Knowledge Graph Flow
1. User uploads documents
2. On rebuild (automatic or manual), system:
   - Processes each document
   - Extracts parties, dates, allegations, claims
   - Detects contradictions between documents
   - Calculates response deadlines
   - Identifies unaddressed issues
3. Knowledge graph stored as JSON in database

### Response Generation Flow
1. User uploads opposing party's motion
2. User clicks "Generate Response"
3. System:
   - Retrieves case knowledge graph
   - Analyzes motion allegations
   - Generates Admit/Deny responses
   - Creates factual corrections
   - Applies legal standard
   - Constructs argument
   - Requests appropriate relief
   - Creates proposed order
   - Builds exhibit list
4. Response saved and accessible in Auto-Generated tab

---

## Files Modified/Created

### Created
- `core/services/litigation_brain.py` - Main processing services
- `core/migrations/0078_session_408_litigation_management.py` - Database migration
- `docs/handoffs/SESSION_408_LEGAL_DOCUMENT_BRAIN.md` - This file

### Modified
- `core/models_legal.py` - Added 6 new models
- `core/views_legal.py` - Added 9 new API endpoints
- `core/urls.py` - Added URL routes
- `ai_core/templates/components/panels/legal_assistant_panel.html` - Added Document Brain UI

---

## Technical Notes

### Document Type Detection
The system uses regex patterns to auto-detect document types:
- "temporary orders" → `temporary_orders`
- "parenting plan" → `prior_parenting`
- "motion to modify" → `my_motion`
- "response to motion" → `response`

### Contradiction Detection
Simple heuristic: looks for negation words in similar-topic claims from opposing parties.
Future enhancement: Use LLM for deeper semantic analysis.

### Response Deadlines
Colorado family law: 21 days to respond to a motion served in-state.
System automatically calculates and highlights upcoming deadlines.

---

## Usage Example

```python
# Upload a document
from core.services.litigation_brain import get_document_ingestor

ingestor = get_document_ingestor()
result = ingestor.process_document(
    case_profile_id=case.id,
    file_content=file_bytes,
    filename="Taylor_Motion_to_Modify.pdf",
    user_category="motion",
    user_document_type="opposing_motion",
    filing_party="respondent"
)

# Rebuild knowledge graph
from core.services.litigation_brain import get_context_builder

builder = get_context_builder()
result = builder.rebuild_knowledge_graph(case.id)
print(f"Found {result['contradictions_found']} contradictions")

# Generate response
from core.services.litigation_brain import get_response_writer

writer = get_response_writer()
result = writer.generate_response(document_id)
print(result['full_document'])  # Court-ready response
```

---

## Next Steps (Session 409+)

1. **LLM Integration** - Use GPT for deeper allegation analysis and contradiction detection
2. **PDF Export** - Add WeasyPrint for PDF generation of responses
3. **Batch Upload** - Support ZIP file upload with multiple documents
4. **Evidence OCR** - Extract text from image evidence (screenshots)
5. **Calendar Integration** - Sync deadlines with user's calendar
6. **Email Integration** - Auto-generate and send conferral emails

---

## Legal Disclaimer

This system provides **GENERAL LEGAL INFORMATION**, not legal advice. It does not create an attorney-client relationship. Users should consult a licensed attorney for advice specific to their situation.
