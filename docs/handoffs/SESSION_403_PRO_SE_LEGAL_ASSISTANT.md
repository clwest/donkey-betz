# Session 403: Pro Se Legal Assistant MVP

**Date:** December 9, 2025
**Status:** Phase 1 + Phase 2 Complete ✅
**Focus:** Colorado Divorce with Children

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
# Created
core/agents/legal/__init__.py
core/agents/legal/legal_doc_drafter_agent.py
ai_core/spiders/specialized/colorado_family_law_spider.py
ai_core/spiders/specialized/justia_playwright_spider.py
docs/SESSION_403_LEGAL_ASSISTANT_GAP_ANALYSIS.md
docs/handoffs/SESSION_403_PRO_SE_LEGAL_ASSISTANT.md

# Modified
ai_core/spiders/spider_registry.py (added 2 spiders)
core/agent_router.py (added LegalDocDrafterAgent)
core/assistant/tool_definitions.py (added tool definition)
core/prompts/tool_descriptions.py (added tool description)
core/agents/personal_assistant_agent.py (added keywords, routing, delegate enum)
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

## What's Next (Phase 3 - Optional)

1. **Dedicated API Endpoints** (`core/views_legal.py`):
   - POST /api/legal/research/ (currently uses /api/chat/)
   - POST /api/legal/draft/
   - GET /api/legal/history/

2. **Models** (for case management):
   - LegalCase (case details, parties, dates)
   - LegalDocument (generated documents with status tracking)

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
