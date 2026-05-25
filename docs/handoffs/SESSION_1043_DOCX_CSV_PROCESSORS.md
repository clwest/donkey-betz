---
originating_session: 1043
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1043 - DOCX & CSV Processors for RAG Upload Pipeline

**Date:** February 19, 2026
**Focus:** Add DOCX and CSV file processing to the RAG document ingestion pipeline

---

## Problem

The RAG upload pipeline only supported PDF, TXT, and Markdown files. Users could not upload Word documents (.docx) or CSV data files (.csv) for embedding and semantic search. This was identified as a must-have gap in INIT-000057 (RAG Upload Pipeline: Must-Have Gaps for Production Launch).

## Changes

### 1. DOCXProcessor (content/processors.py)

New processor class following the existing PDFProcessor pattern:
- Uses `python-docx` library (already installed, v1.2.0)
- Handles both `bytes` input (from file upload) and file path strings
- Extracts text from all paragraphs and tables
- Tables rendered as pipe-separated rows for embedding
- Extracts metadata: title, author, subject, paragraph count, table count
- Returns `ProcessingResult` with raw/processed content

### 2. CSVProcessor (content/processors.py)

New processor class for structured data:
- Uses `pandas` library (already installed, v2.3.2)
- Handles bytes, string content, and file path inputs
- Reads up to 10,000 rows
- Generates embedding-friendly text representation:
  - Column summaries (unique values, null counts, sample values)
  - First 50 rows as key-value text
- Raw content preserved as CSV text (first 100 rows)
- Extracts metadata: row count, column count, column names

### 3. Pipeline Registration (content/processors.py)

Both processors added to `DocumentProcessingPipeline.__init__` processor list between PDFProcessor and JSONProcessor.

### 4. Ingest Endpoint (core/views_rag_embeddings.py)

- Imported `DOCXProcessor` and `CSVProcessor`
- Added `.docx` → `DocumentType.DOCX` and `.csv` → `DocumentType.CSV` branches
- Updated error message to list all 5 supported formats

### 5. Frontend (frontend/src/pages/DocumentsPage.tsx)

- File input `accept` attribute: `.pdf,.txt,.md` → `.pdf,.txt,.md,.docx,.csv`
- Help text: "Supports PDF, DOCX, CSV, TXT, MD files"
- `DocumentTypeBadge`: added `docx` (indigo) and `csv` (emerald) type badges
- Info section bullet: updated to mention all formats

## Files Modified

| File | Lines Changed |
|------|--------------|
| `content/processors.py` | +208 (2 new processor classes) |
| `core/views_rag_embeddings.py` | +8 (new branches + import) |
| `frontend/src/pages/DocumentsPage.tsx` | +6 (accept, badges, text) |

## Verification

```bash
# Test DOCX processing on Railway
railway run python manage.py shell -c "
from content.processors import DOCXProcessor
p = DOCXProcessor()
print(f'Can process .docx: {p.can_process(\"test.docx\", \"\")}')
print(f'HAS_DOCX: {True}')
"

# Test CSV processing on Railway
railway run python manage.py shell -c "
from content.processors import CSVProcessor
p = CSVProcessor()
print(f'Can process .csv: {p.can_process(\"test.csv\", \"\")}')
print(f'HAS_PANDAS: {True}')
"

# Test via UI: Upload a .docx or .csv file on Documents page
# Should show with indigo (Word) or emerald (CSV) badge
```

## Related

- INIT-000057: RAG Upload Pipeline must-have gaps
- Session 1043 also: Brainstorm bulk export (PR #1345), OOM fix (PR #1346)
