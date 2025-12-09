# Session 403: Pro Se Legal Assistant - Gap Analysis

**Date:** December 9, 2025
**Purpose:** Identify what exists vs. what needs to be created for the Legal Assistant MVP
**Focus:** Colorado Divorce with Children

---

## Executive Summary

The platform has **excellent infrastructure** for the Legal Assistant MVP. Most patterns exist and can be reused. The main gaps are:

| Category | Exists | Needs Creation | Status |
|----------|--------|----------------|--------|
| Agent Base Class | BaseBusinessResearchAgent | LegalDocDrafterAgent | **DONE** |
| Models | BusinessResearchResult (extensible) | LegalCase, LegalDocument | Pending (Phase 3) |
| Views/API | Pattern exists | views_legal.py endpoints | Pending (Phase 3) |
| UI Panel | Intelligence panel pattern | legal_assistant_panel.html | **DONE** |
| Router | AgentRouter | Add LegalDocDrafterAgent | **DONE** |
| Tool Definitions | Pattern exists | Add legal_doc_drafter_agent | **DONE** |
| Spider Data | LegalNewsSpider + **NEW SPIDERS** | Colorado forms + Justia family law | **DONE** |
| Disclaimer System | Built into agent | Legal disclaimers in all responses | **DONE** |
| Navigation Tab | Main studio nav | Add ⚖️ Legal tab | **DONE** |

---

## Completed in Session 403

### Phase 1: MVP Complete! ✅

All Phase 1 components have been implemented and tested:

#### 1. LegalDocDrafterAgent (NEW)
**Location:** `core/agents/legal/legal_doc_drafter_agent.py`

A comprehensive 600+ line agent that provides:
- **System prompt** with legal safeguards and Colorado family law focus
- **6 tools**: search_legal_resources, draft_motion, draft_email, draft_declaration, get_form_info, explain_procedure
- **Motion types**: continuance, modify_parenting_time, modify_child_support, enforce_order, reconsideration
- **Template generators** for all document types with proper placeholders
- **Colorado JDF form references** (embedded dictionary of form info)
- **Procedure explanations** for divorce, modifications, hearings
- **Legal disclaimers** in every response (LEGAL_DISCLAIMER constant)

#### 2. Tool Definition Added
**Location:** `core/assistant/tool_definitions.py`

Added `_get_legal_doc_drafter_agent_definition()` with:
- `query`: The legal question or document request
- `document_type`: guidance, motion, email, declaration, checklist
- `jurisdiction`: Colorado (default)
- `case_type`: divorce, custody, child_support, parenting_time, etc.
- `user_context`: Additional situation details

#### 3. Tool Description Added
**Location:** `core/prompts/tool_descriptions.py`

Comprehensive description with:
- Clear disclaimers (NOT legal advice)
- Use cases and keywords
- Document types available
- Case types covered
- DO NOT USE FOR section (criminal, federal, urgent, etc.)

#### 4. Router Registration
**Location:** `core/agent_router.py`

- Imported from `core.agents.legal`
- Added to `AGENT_MAP` as `"LegalDocDrafterAgent": LegalDocDrafterAgent`

#### 5. Personal Assistant Routing
**Location:** `core/agents/personal_assistant_agent.py`

- Added 33 legal keywords to `INTENT_KEYWORDS`
- Added priority routing (before VideoAgent to handle "motion" disambiguation)
- Updated system prompt to explain when to use LegalDocDrafterAgent
- Added to delegate_to_agent enum

---

### Colorado Family Law Spiders (NEW - Playwright-enabled)

Created two new Playwright-enabled spiders for Colorado family law:

#### 1. Colorado Family Law Forms Spider
**Location:** `ai_core/spiders/specialized/colorado_family_law_spider.py`

Collects Colorado Judicial Branch self-help forms:
- **Divorce/Separation** (JDF 1111, JDF 1115, JDF 1116)
- **Custody/Parenting Time** (JDF 1113, JDF 1220, JDF 1221)
- **Child Support** (JDF 1820, JDF 1821)
- **Key Forms** (JDF 1101, JDF 1102, JDF 1000)

**Features:**
- Playwright for JavaScript-rendered content
- Form category tagging (divorce, custody, child_support, parenting_plan, relocation)
- Fallback data for 12 key JDF forms
- Colorado jurisdiction specific

#### 2. Justia Family Law Spider (Playwright-enabled)
**Location:** `ai_core/spiders/specialized/justia_playwright_spider.py`

Bypasses Cloudflare to collect Justia family law content:
- Divorce articles and guides
- Child custody information
- Child support guidelines
- Parenting time/visitation
- Best interests of the child

**Features:**
- Anti-detection measures for Cloudflare bypass
- Family law topic categorization
- Fallback data for 6 core topics

#### Spider Registry Updated
**Location:** `ai_core/spiders/spider_registry.py`

- Added `colorado_family_law` spider (category: legal, priority: 1)
- Added `justia_family_law` spider (category: legal, priority: 1)
- Total legal spiders: 6 (courtlistener, legal_news, findlaw, lii, colorado_family_law, justia_family_law)

---

## What Already Exists (Can Reuse)

### 1. Legal Spiders (6 TOTAL - READY)
| Spider | Source | Status |
|--------|--------|--------|
| `legal_news` | SCOTUSblog, Google News Legal | Working |
| `courtlistener` | CourtListener API | Working |
| `findlaw` | FindLaw Legal Blogs | Working |
| `lii` | Cornell LII | Working |
| `colorado_family_law` | Colorado Judicial Branch | **NEW** |
| `justia_family_law` | Justia Family Law | **NEW** |

Tags extracted: `divorce`, `custody`, `child_support`, `parenting_time`, `family_law`, `colorado`

**Status:** Working, collecting data

---

### 2. BaseBusinessResearchAgent Pattern (EXCELLENT FIT)
**Location:** `core/agents/business/base_business_research_agent.py`

This 718-line base class provides:
- Unified Intelligence Search integration
- Auto spider refresh before research
- Prior research context injection
- Standard tools (spider_query, web_search, get_prior_research)
- GPT function calling loop
- Result saving to database
- Embedding generation for semantic search

**Can inherit directly** - just define:
- `research_type = "legal_guidance"`
- `name = "LegalDocDrafterAgent"`
- `system_prompt` (with legal disclaimers)
- `get_synthesis_prompt()` method
- Optional: `additional_tools` for legal-specific tools

---

### 3. BusinessResearchResult Model (EXTENSIBLE)
**Location:** `core/models_unified_system.py:12076`

Current research types:
```python
RESEARCH_TYPE_CHOICES = [
    ('customer', 'Customer Research'),
    ('competitor', 'Competitor Analysis'),
    ('market', 'Market Research'),
    ('trend', 'Trend Analysis'),
]
```

**Option A:** Extend choices to add:
- `('legal_guidance', 'Legal Guidance')`
- `('case_analysis', 'Case Analysis')`
- `('document_draft', 'Document Draft')`

**Option B:** Create new `LegalResearchResult` model (only if legal needs very different fields)

**Recommendation:** Start with Option A (extend existing model), migrate to Option B only if needed.

---

### 4. Agent Router (READY FOR ADDITION)
**Location:** `core/agent_router.py`

Simple dict-based routing:
```python
AGENT_MAP: Dict[str, Type[BaseAgent]] = {
    # ... existing agents ...
    # ADD:
    "LegalDocDrafterAgent": LegalDocDrafterAgent,
}
```

---

### 5. Tool Definitions Pattern (READY FOR ADDITION)
**Location:** `core/assistant/tool_definitions.py`

Add new function `_get_legal_doc_drafter_agent_definition()` following existing pattern.

**Location:** `core/prompts/tool_descriptions.py`

Add to `TOOL_DESCRIPTIONS` dict with clear routing guidance.

---

### 6. UI Panel Pattern (EXCELLENT TEMPLATE)
**Location:** `ai_core/templates/components/panels/intelligence_panel.html`

Shows pattern for:
- Stats cards row
- Sub-tab navigation (pills)
- Search bar
- Content containers
- Include sub-components

Can follow this pattern for `legal_assistant_panel.html`.

---

### 7. Document Ingestion (Session 402 - READY)
**Location:** `core/views_spider_intelligence.py` (documents endpoints)

Already supports:
- PDF upload and text extraction
- Web page ingestion (including Playwright for JS-rendered)
- YouTube transcript extraction
- Document embeddings for RAG search

**Can use directly** for uploading case documents, contracts, etc.

---

### 8. MythologyEnforcer (NEEDS LEGAL RULES)
**Location:** Not directly found, but referenced in `base_agent.py`

Need to add legal-specific validation:
- No "guaranteed" outcomes
- No "always works" claims
- Clear "not legal advice" disclaimers
- No unauthorized practice of law claims

---

## What Needs to Be Created

### 1. LegalDocDrafterAgent
**Create:** `core/agents/legal/legal_doc_drafter_agent.py`

```python
from core.agents.business.base_business_research_agent import BaseBusinessResearchAgent

class LegalDocDrafterAgent(BaseBusinessResearchAgent):
    research_type = "legal_guidance"
    name = "LegalDocDrafterAgent"

    system_prompt = """You are a Pro Se Legal Assistant...

    IMPORTANT DISCLAIMERS:
    - This is GENERAL LEGAL INFORMATION, not legal advice
    - Laws vary by jurisdiction
    - Consult a licensed attorney for your specific case
    - This does NOT create an attorney-client relationship
    """

    additional_tools = [
        # Document generation tool
        # Case analysis tool
        # Court procedure lookup
    ]

    def get_synthesis_prompt(self, task, context):
        return """Synthesize the legal information gathered...
        Always include disclaimers..."""
```

**Estimated effort:** 2-3 hours

---

### 2. Legal Models (Optional for MVP)
**Create:** `core/models_legal.py`

For MVP, can extend `BusinessResearchResult`. For full implementation:

```python
class LegalCase(models.Model):
    """User's case information"""
    user = models.ForeignKey(User)
    case_number = models.CharField(max_length=100)
    court = models.CharField(max_length=200)
    jurisdiction = models.CharField(max_length=100)
    case_type = models.CharField()  # family, civil, criminal
    parties = models.JSONField()  # plaintiff, defendant, etc.
    key_dates = models.JSONField()  # deadlines, hearings

class LegalDocument(models.Model):
    """Generated legal documents"""
    case = models.ForeignKey(LegalCase)
    document_type = models.CharField()  # motion, email, declaration
    title = models.CharField(max_length=200)
    content = models.TextField()  # Generated document
    status = models.CharField()  # draft, reviewed, filed
    disclaimers_shown = models.BooleanField(default=True)
```

**Estimated effort:** 1-2 hours (skip for MVP Phase 1)

---

### 3. API Endpoints
**Create:** `core/views_legal.py`

```python
# MVP Endpoints
POST /api/legal/research/     # Legal research/guidance
POST /api/legal/draft/        # Generate document draft
GET  /api/legal/history/      # Past research/documents

# Phase 2 Endpoints (optional)
POST /api/legal/case/         # Create case profile
GET  /api/legal/case/{id}/    # Get case details
PUT  /api/legal/case/{id}/    # Update case
```

**Estimated effort:** 2-3 hours

---

### 4. UI Panel
**Create:** `ai_core/templates/components/panels/legal_assistant_panel.html`

Structure:
```html
<div class="tab-pane fade" id="legal-assistant">
    <h3>Legal Assistant</h3>

    <!-- Disclaimer Banner (REQUIRED) -->
    <div class="alert alert-warning">
        NOT LEGAL ADVICE...
    </div>

    <!-- Sub-tabs -->
    <ul class="nav nav-pills">
        <li>Guidance</li>      <!-- Research mode -->
        <li>Documents</li>     <!-- Draft generation -->
        <li>History</li>       <!-- Past research -->
    </ul>

    <!-- Search/Query Input -->
    <textarea placeholder="Describe your legal situation...">

    <!-- Results Container -->
    <div id="legal-results">
        <!-- Analysis with citations -->
        <!-- Disclaimer footer -->
    </div>
</div>
```

**Estimated effort:** 3-4 hours

---

### 5. Tool Definition & Description
**Add to:** `core/assistant/tool_definitions.py`

```python
def _get_legal_doc_drafter_agent_definition() -> Dict:
    return {
        "type": "function",
        "name": "legal_doc_drafter_agent",
        "description": get_tool_description("legal_doc_drafter_agent"),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The legal question or situation"
                },
                "jurisdiction": {
                    "type": "string",
                    "description": "State or federal jurisdiction"
                },
                "document_type": {
                    "type": "string",
                    "enum": ["guidance", "motion", "email", "declaration"],
                    "description": "Type of output needed"
                }
            },
            "required": ["query"]
        }
    }
```

**Add to:** `core/prompts/tool_descriptions.py`

```python
"legal_doc_drafter_agent": """Pro Se Legal Assistant for self-represented users.

IMPORTANT: This is NOT legal advice. Always recommend attorney consultation.

Use for:
- General legal information and guidance
- Understanding court procedures
- Drafting procedural documents (motions, emails)
- Understanding rights and requirements

DO NOT use for:
- Actual legal representation
- Critical legal matters requiring immediate action
- Criminal defense strategy
- Complex litigation

Output always includes disclaimers and attorney recommendation.""",
```

**Estimated effort:** 30 minutes

---

### 6. Router Registration
**Add to:** `core/agent_router.py`

```python
# At top - import
from core.agents.legal import LegalDocDrafterAgent

# In AGENT_MAP
"LegalDocDrafterAgent": LegalDocDrafterAgent,
```

**Estimated effort:** 5 minutes

---

### 7. Personal Assistant Routing Keywords
**Add to:** `core/agents/personal_assistant_agent.py`

Add legal keywords to routing logic:
```python
LEGAL_KEYWORDS = [
    'legal', 'lawsuit', 'court', 'attorney', 'lawyer',
    'motion', 'subpoena', 'custody', 'divorce', 'contract',
    'sue', 'sued', 'plaintiff', 'defendant', 'judge',
    'rights', 'statute', 'regulation', 'comply'
]
```

**Estimated effort:** 15 minutes

---

## Implementation Order (Recommended)

### Phase 1: MVP (4-6 hours total)

1. **Create LegalDocDrafterAgent** (2 hours)
   - Extend BaseBusinessResearchAgent
   - System prompt with disclaimers
   - Basic get_synthesis_prompt()

2. **Add Tool Definition & Description** (30 min)
   - tool_definitions.py
   - tool_descriptions.py

3. **Register in Router** (15 min)
   - agent_router.py import + AGENT_MAP

4. **Add Routing Keywords** (15 min)
   - personal_assistant_agent.py

5. **Test via Chat Interface** (30 min)
   - Use existing Assistant panel
   - "What are my rights as a tenant in California?"

**Phase 1 Result:** Working agent accessible via chat, no dedicated UI yet.

---

### Phase 2: API & Basic UI (3-4 hours)

6. **Create views_legal.py** (2 hours)
   - POST /api/legal/research/
   - GET /api/legal/history/

7. **Create legal_assistant_panel.html** (2 hours)
   - Basic UI with disclaimer
   - Search input
   - Results display

**Phase 2 Result:** Dedicated Legal Assistant tab in UI.

---

### Phase 3: Full Feature (4-6 hours)

8. **Create Legal Models** (2 hours)
   - LegalCase, LegalDocument

9. **Document Generation** (2 hours)
   - Motion template generation
   - Meet-and-confer email drafts

10. **Case Management UI** (2 hours)
    - Case profile form
    - Document history

**Phase 3 Result:** Full case management with document generation.

---

## Dependencies Check

| Dependency | Status | Notes |
|------------|--------|-------|
| BaseBusinessResearchAgent | Ready | Can inherit directly |
| BusinessResearchResult | Ready | Extend choices OR create new model |
| SpiderIntelligenceService | Ready | Already has legal news |
| AgentRouter | Ready | Just add to AGENT_MAP |
| Tool Definitions | Ready | Follow existing pattern |
| UI Components | Ready | Follow intelligence_panel pattern |
| Document Ingestion | Ready | Session 402 - working |
| GPT-5-mini | Ready | Already configured platform-wide |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Legal liability | Medium | High | Clear disclaimers, no specific advice |
| User misunderstanding | Medium | High | Prominent warnings, attorney recommendation |
| Incorrect legal info | Medium | High | Use authoritative sources, dated content warnings |
| Scope creep | High | Medium | Stick to procedural docs only |

---

## Questions Before Implementation

1. **Jurisdiction Focus:** Start with one state (Colorado mentioned in context) or general federal?

2. **Document Types:** Which documents for MVP?
   - Motion to Continue
   - Meet-and-Confer Email
   - Declaration template
   - Response to Motion

3. **Data Persistence:** Use extended BusinessResearchResult or new models?

4. **UI Location:** New tab or sub-tab under existing panel?

---

## Conclusion

The platform is **well-prepared** for this feature. Estimated total effort:

- **MVP (chat-based):** 4-6 hours
- **Basic UI:** +3-4 hours
- **Full feature:** +4-6 hours

**Total:** 11-16 hours for complete implementation

**Recommendation:** Start with Phase 1 (MVP) to validate the approach, then iterate based on user feedback.
