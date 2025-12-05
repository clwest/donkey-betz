# Start Next Session Here

**Last Session:** 350 - Domain-Aware Spider Targeting + Business Viability Check
**Date:** December 4, 2025
**Status:** 102 spiders | 36 categories | 79 agents | Domain-Targeted Business Research

---

## What Happened in Session 350

### Domain-Aware Spider Targeting (Major Feature)

**Problem:** Business research PDFs contained generic AI/tech news instead of domain-specific content. An "AI fitness coaching app" project received articles about Meta design and geothermal energy instead of fitness industry content.

**Solution:** Created `DomainExtractionService` that:
1. Extracts primary business domain from project descriptions
2. Generates domain-specific spider search queries
3. Maps to relevant spider categories
4. Recommends domain-specific subreddits
5. Uses GPT-4o-mini with keyword fallback

**13 Business Domains Supported:**
- fitness_health, saas_b2b, ecommerce_retail, fintech_finance
- edtech_learning, food_restaurant, mental_health, ai_ml
- creator_economy, real_estate, gaming_entertainment, travel_hospitality
- general_startup (fallback)

### Business Viability Check ("Idiot Protector")

Added viability scoring to prevent research on absurd business ideas:
- Uses GPT-4o-mini to score ideas 0-100
- Detects jokes/impractical concepts
- Shows warning for low-scoring ideas
- Example: "Onion Bar - restaurant serving only raw onions" → Score: 15, is_joke: True

### Honest Data Reporting

Synthesis results now include domain relevance metrics:
```python
'domain_relevance': {
    'score': 45,  # % of items matching domain tags
    'domain_relevant_items': 9,
    'total_items': 20,
    'is_domain_specific': True  # True if >= 30%
}
```

### Bug Fix: Project Deletion 500 Error

Fixed missing database tables (`core_projectresearchfeedback`, `core_projectspiderpriority`) that were causing project deletion to fail.

---

## Files Created/Modified

| File | Changes |
|------|---------|
| `core/services/domain_extraction_service.py` | **NEW** - Domain extraction service |
| `core/models_partnership.py` | Added domain targeting methods to PartnershipProject |
| `core/agents/business/competitor_analysis_agent.py` | Viability check + domain targeting |
| `core/agents/business/customer_research_agent.py` | Viability check + domain targeting |
| `docs/handoffs/SESSION_350_DOMAIN_AWARE_SPIDER_TARGETING.md` | Session handoff |

---

## Current System State

| Component | Count |
|-----------|-------|
| **Spiders** | **102** |
| **Categories** | **36** |
| **Agents** | **79** (69 legacy + 10 clean) |
| **Data Points** | **9,983+** |
| **Business Domains** | **13** |
| **Research Pipeline** | **Domain-Targeted** |

---

## Quick Start

```bash
make start
make celery  # For background tasks
open http://localhost:8000/ai-studio/
```

---

## Test Domain Targeting

```python
# In Django shell
from core.services.domain_extraction_service import get_domain_extraction_service

service = get_domain_extraction_service()
result = service.extract_domains("AI-powered fitness coaching app")

print(f"Domain: {result.primary_domain}")    # fitness_health
print(f"Tags: {result.domain_tags}")         # ['fitness', 'health', 'ai', 'coaching']
print(f"Subreddits: {result.subreddits}")    # ['r/fitness', 'r/personaltraining']
print(f"Queries: {result.spider_queries}")   # ['AI fitness coaching', 'fitness app market']
```

---

## Next Session Priorities

### Option A: Test Domain-Aware Research End-to-End
Create a new project with a specific domain (e.g., fintech) and verify:
- Domain is correctly extracted
- Spider searches use domain-specific queries
- Research PDFs contain relevant industry content
- Domain relevance score is reported

### Option B: Expand Domain Definitions
Add more specialized domains as needed:
- healthcare_medical
- legal_compliance
- sustainability_green
- pet_animal

### Option C: Domain-Specific Subreddit Integration
Actually query the recommended subreddits during research:
- Use existing Reddit spider infrastructure
- Filter by domain-recommended subreddits
- Prioritize domain content in search results

---

## Key Documentation

- **Session 350 Details:** `docs/handoffs/SESSION_350_DOMAIN_AWARE_SPIDER_TARGETING.md`
- Session 349 Details: `docs/handoffs/SESSION_349_PROMPT_VS_CHAT_AUDIT_AND_INTEGRATION.md`
- Session 348 Details: `docs/handoffs/SESSION_348_RESEARCH_PIPELINE_FIXES.md`
- Architecture: `docs/ARCHITECTURE.md`

---

**Business research now targets domain-specific content with honest data reporting!**
