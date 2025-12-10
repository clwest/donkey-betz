# Session 403/404/405: Pro Se Legal Assistant MVP

**Date:** December 9, 2025
**Status:** Phase 1 + Phase 2 + Phase 3 + Phase 4 (Motion Rewriting) + Phase 5 (Text Cleanup & Learning) Complete ✅
**Focus:** Colorado Divorce with Children + Case File Upload/Analysis + Motion Rewriting + Text Formatting

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

## Phase 4: Motion Rewriting Engine (Session 404) ✅

Based on real-world feedback from a denied motion, implemented comprehensive motion rewriting capabilities.

### Key Feedback Addressed

**What was working:**
- ✅ Correctly identified all denial reasons
- ✅ Stayed on safe side of legal advice line
- ✅ Understood Colorado specifics without hallucinating statutes

**What needed improvement:**
- ❌ Was analyzing but not converting to correct JDF format
- ❌ Over-explained optional strategy instead of "do this, not that"
- ❌ Used placeholders like "JDF XXXX" instead of form names
- ❌ Did not output ready-to-file affidavit-style drafts

### New Tools Added (Session 404)

| Tool | Purpose |
|------|---------|
| `analyze_denied_motion` | Analyze why motion was denied, identify all deficiencies |
| `rewrite_motion` | Generate corrected motion in proper JDF format with affidavit |
| `generate_evidence_checklist` | Create checklist of required exhibits for motion type |
| `check_non_party_issues` | Detect non-party relief requests and provide corrections |

### JDF Form Scaffolding

Added comprehensive form mapping (`JDF_FORM_MAPPING`) for:
- `emergency_parenting` - Emergency Orders (no standard JDF)
- `restrict_parenting` - JDF 1220 (Motion to Modify Parenting Time)
- `modify_parenting_time` - JDF 1220 + JDF 1221 (Affidavit)
- `enforce_order` - Motion for Citation for Contempt
- `modify_child_support` - JDF 1820 or JDF 1821
- `third_party_interference` - JDF 1220 or Contempt

### Statutory Criteria Categories

Added `STATUTORY_CRITERIA` mapping to align facts with procedural requirements WITHOUT citing statute numbers:
- `emergency_restriction` - Imminent danger requirements
- `modification` - Changed circumstances + best interests
- `contempt` - Willful violation requirements

### Non-Party Rule Detection

Added `NON_PARTY_INDICATORS` list and detection logic:
- Detects requests for relief against girlfriends, boyfriends, grandparents, etc.
- Explains why courts cannot order non-parties
- Provides correct procedure: "Order [Party] to ensure [non-party] does not..."

### Updated System Prompt

Completely rewrote system prompt to:
1. ONLY discuss procedural paths, not strategy
2. Never say "Consider requesting..." (that's strategy)
3. Always identify correct JDF form by official title
4. When user uploads denied motion, follow structured analysis:
   - A. Correct form identification
   - B. Why original was denied
   - C. Separate filings needed
   - D. Draft affidavit in proper sworn format
   - E. Draft motion in JDF structure
   - F. Proposed order template
   - G. Evidence/exhibit checklist

### Motion Rewriter Output Structure

When `rewrite_motion` is called, output includes:
1. **Header** - Case caption with form reference
2. **Motion Section** - Numbered factual allegations
3. **Specific Incidents** - Dated incident timeline
4. **Relief Requested** - What court is being asked to do
5. **Legal Basis** - Criteria category (no statute citations)
6. **Sworn Affidavit** - Facts restated under penalty of perjury
7. **Proposed Order** - Ready for judge signature
8. **Evidence Checklist** - Motion-type specific requirements
9. **Filing Instructions** - Next steps

---

## Phase 5: Text Cleanup & Collective Learning (Session 405) ✅

Based on ChatGPT's review of the generated motion output, implemented comprehensive text cleanup and learning integration.

### Issues Fixed (Patches 4D-4H)

| Issue | Fix | Patch |
|-------|-----|-------|
| PDF artifacts (docket refs, page numbers) | Pre-extraction cleanup patterns | 4D |
| "Immediate Emergency Basis" showing in output | Multiple regex cleanup patterns | 4D.7 |
| Grammar errors ("escalating, harmful, and constitutes") | Regex replacement for clean prose | 4D.7 |
| "Today's Incident" (wrong for later filing) | Replaced with "The Incident on [date]" | 4G |
| Bullet points on same line (`● A ● B ● C`) | Newline insertion + HTML formatting | 4F, 4H |
| Giant paragraphs instead of numbered facts | Proper segmentation in `_build_clean_allegations()` | 4E |
| Single newlines collapsing in HTML | Convert `\n` to `<br>` in frontend | 4H |

### New Methods Added

| Method | Purpose |
|--------|---------|
| `postprocess_extracted_facts()` | Final cleanup layer after fact extraction |
| `cleanup_generated_facts_block()` | Remove boilerplate patterns from generated text |
| `_extract_third_party_segment()` | Extract third-party status bullet list |
| `_extract_respondent_failures_segment()` | Extract respondent failures bullet list |
| `_save_legal_memory()` | Save legal-specific patterns to LegalMemory |
| `_ensure_agent_registered()` | Ensure LegalDocDrafterAgent is in Agent database |

### Collective Intelligence Integration

The LegalDocDrafterAgent now participates in collective learning:

1. **Agent Registration** - Auto-registers in Agent database on init
2. **Learning Hooks** - Fires after every denied motion rewrite:
   - `_record_learning_outcome()` - XP and pattern detection
   - `_create_execution_memory()` - Persistent execution memory
   - `_share_knowledge()` - Share pattern with other agents
   - `_save_legal_memory()` - Legal-specific memory storage
3. **LegalMemory Records** - Created for each motion rewrite with:
   - Relief type, jurisdiction, facts count
   - Key insights and applicable scenarios
   - Agent FK linkage

### Frontend Improvements (Patch 4H)

Updated `formatLegalResponse()` in `legal_assistant_panel.html`:
- Unicode bullet points (`●`, `•`, etc.) → HTML list items
- Single newlines → `<br>` tags
- "Today's Incident" → "The Incident on" (frontend fallback)
- Proper indentation for bullet lists

### Files Modified

```
# Backend
core/agents/legal/legal_doc_drafter_agent.py
  - Added postprocess_extracted_facts() (~80 lines)
  - Added cleanup_generated_facts_block() (~70 lines)
  - Added _save_legal_memory() (~30 lines)
  - Added _ensure_agent_registered() (~15 lines)
  - Modified _execute_denied_motion_pipeline() (learning hooks)
  - Modified _build_clean_allegations() (proper segmentation)

# Frontend
ai_core/templates/components/panels/legal_assistant_panel.html
  - Updated formatLegalResponse() (bullet and newline handling)
```

---

## Validation (Session 405) ✅

**ChatGPT reviewed the generated motion output and confirmed:**

> "Your system's rewrite is correct, court-ready, and properly formatted. There are zero red flags. If anything, it is better than what many self-represented litigants file."

---

## Phase 6: Recommended Enhancements (ChatGPT Feedback)

Based on expert review, these 5 enhancements would make the system production-grade:

### 1. Relief Against Third Parties Filter ⭐
**Problem:** System detects non-party issues but doesn't auto-rewrite.
**Enhancement:** Auto-convert "Camille shall not..." → "Respondent shall ensure that Camille does not..."
**Priority:** High - This is a common denial reason

### 2. Emergency vs Non-Emergency Detector ⭐⭐
**Problem:** Magistrates deny motions labeled "emergency" that lack emergency requirements.
**Enhancement:**
- Detect if harm is immediate
- Advise whether situation qualifies for C.R.S. § 14-10-129.5
- Warn when something is NOT actually an emergency
**Priority:** Critical - Emergency misuse is a top denial reason

### 3. Court Order Being Modified Detector
**Problem:** JDF motions require attachment of the order being modified.
**Enhancement:** Auto-prompt: "Upload the existing order (Exhibit X) before filing."
**Priority:** Medium - Document requirement

### 4. Conflict With Prior Orders Detector
**Problem:** Requests may contradict existing court orders.
**Enhancement:** Flag conflicts between requested relief and uploaded orders.
**Priority:** Medium - Requires order parsing

### 5. Likelihood of Success Confidence Meter ⭐⭐⭐
**Problem:** Users don't know if their motion has a chance.
**Enhancement:** Score based on:
- Relief scope (narrower = better)
- Evidence strength (documented = better)
- Procedural posture (timing)
- CO case law signals
**Priority:** High - "Killer feature" per ChatGPT

---

## Session 405 Implementation Status

| Enhancement | Status | Tool Name |
|-------------|--------|-----------|
| #1 Relief Against Third Parties Auto-Rewrite | ✅ IMPLEMENTED | `check_non_party_issues` |
| #2 Emergency vs Non-Emergency Detector | ✅ IMPLEMENTED | `assess_emergency_status` |
| #3 Court Order Being Modified Detector | ✅ IMPLEMENTED | `check_order_attachment_required` |
| #4 Conflict With Prior Orders Detector | ✅ IMPLEMENTED | `detect_order_conflicts` |
| #5 Likelihood of Success Confidence Meter | ✅ IMPLEMENTED | `assess_likelihood_of_success` |

### Enhancement Details

#### #1: Third-Party Auto-Rewrite
Automatically converts problematic third-party relief requests:
- `"Camille shall not..."` → `"Respondent shall ensure that Camille does not..."`
- `"Order [Name] to..."` → `"Order Respondent to ensure that [Name]..."`
- `"Prohibit [Name] from..."` → `"Order Respondent to ensure that [Name] is not..."`

#### #2: Emergency Assessment
Detects true emergency factors (physical danger, CPS, flight risk) vs non-emergency situations (communication, schedule disputes, parenting disagreements).
- Returns `is_emergency`, `emergency_confidence`, and `recommendation`
- Warns when "emergency" is claimed but no emergency factors present
- Recommends correct form (Emergency Motion vs JDF 1220)

#### #3: Court Order Attachment Check
Detects when motion requires attachment of existing court order:
- Modification motions require the order being modified
- Enforcement/contempt motions require the order being violated
- Auto-prompts user to upload if missing

#### #4: Conflict With Prior Orders Detector
Analyzes motion requests against existing court orders to detect:
- **Direct Contradictions:** Motion asks for opposite of what's ordered (e.g., joint→sole custody)
- **Duplicate Requests:** Motion asks for what's already in place
- **Missing Order Reference:** Modification without citing the order being modified
- **Holiday/Schedule Conflicts:** Changes to existing holiday provisions

Conflict severity levels: LOW (⚠️), MEDIUM (🟡), HIGH (🟠), CRITICAL (🔴)

Provides specific recommendations:
- "Cite the specific provision you want changed"
- "Explain changed circumstances"
- "Acknowledge the existing order"
- References C.R.S. § 14-10-129 modification requirements

#### #5: Likelihood of Success Meter
Scores motion 0-100 based on four factors (25 points each):
- **Relief Scope:** Narrower requests score higher
- **Evidence Strength:** Documentary evidence, specific dates
- **Procedural Posture:** Verification, caption, proposed order
- **Case Law Signals:** Favorable terms ("changed circumstances") vs harmful ("revenge")

Rating scale:
- 🟢 75-100: HIGH - Strong likelihood of success
- 🟡 50-74: MODERATE - Reasonable chances, could be improved
- 🟠 25-49: LOW - Needs significant improvement
- 🔴 0-24: VERY LOW - Likely to be denied without changes

### Session 405 Integration Fixes

After implementing all 5 enhancements, several integration issues were discovered and fixed:

1. **Court Order Upload Handling**
   - Court orders were incorrectly being analyzed through the denied motion pipeline
   - Fixed: Court orders now get a simple acknowledgment message and are stored for future reference
   - User sees "✅ COURT ORDER SAVED" with explanation of how it will be used

2. **Auto-Fetch Court Orders for Conflict Detection**
   - When analyzing a motion, the system now automatically fetches uploaded court orders
   - Court order text is passed to `_detect_order_conflicts()` as context
   - Up to 5 most recent court orders, 15K chars max to prevent token overflow

3. **Document Type String Matching**
   - Bug: `_check_order_attachment_required` expected `'court order'` (with space)
   - Database stores `'court_order'` (with underscore)
   - Fixed: Now matches both formats

4. **Generic Motion Wording**
   - Changed "Upload your denied motion" to "Upload your motion"
   - Works for any motion type, not just denied motions

### Complete Flow

1. **Upload Court Order** → Stored with "✅ COURT ORDER SAVED" message
2. **Upload Motion** → Full analysis pipeline runs:
   - Step 2.5: Emergency assessment
   - Step 2.6: Court order attachment check (recognizes uploaded orders)
   - Step 2.7: Conflict detection (uses uploaded court order text)
   - Step 3-6: Facts extraction, rewrite, success meter

---

## What's Next (Phase 7 - Optional)

1. **Document Pinning** - Reference specific documents in ongoing chat
2. **OCR Support** - Handle scanned PDF documents
3. **Case Timeline** - Visual timeline of case events from documents
4. **Auto-Detection** - Automatically detect document type from content
5. **Multi-Motion Package** - Generate all required separate filings at once

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
- Uses GPT function calling with **12 specialized tools**:
  1. `search_legal_resources` - Search spider data for legal info
  2. `draft_motion` - Generate motion templates
  3. `draft_email` - Generate meet-and-confer emails
  4. `draft_declaration` - Generate sworn declarations
  5. `analyze_denied_motion` - Analyze why motion was denied
  6. `rewrite_motion` - Generate corrected JDF-style motion
  7. `generate_evidence_checklist` - Create exhibit checklist
  8. `check_non_party_issues` - Detect & auto-rewrite third-party relief
  9. `assess_emergency_status` - Emergency vs non-emergency classification
  10. `check_order_attachment_required` - Detect missing court order attachment
  11. `detect_order_conflicts` - Detect conflicts with existing orders
  12. `assess_likelihood_of_success` - Calculate 0-100 success score
- Integrates with spider network for legal data
- Records decisions for debugging (Time Travel)
- Generates knowledge attribution for transparency
- Participates in collective intelligence (shares learned patterns)

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
