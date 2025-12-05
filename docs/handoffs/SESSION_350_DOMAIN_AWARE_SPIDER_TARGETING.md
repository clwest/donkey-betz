# Session 350: Domain-Aware Spider Targeting + Business Viability Check

**Date:** December 4, 2025
**Focus:** Make business research agents return domain-specific data, not generic AI/tech news
**Status:** Complete

---

## Summary

This session addressed critical feedback from reviewing business research PDFs: the spiders were feeding generic AI/tech news articles instead of domain-specific research for business ideas. For example, an "AI-powered fitness coaching app" project was receiving articles about Meta design systems and geothermal energy instead of fitness, wellness, and AI coaching content.

### Key Improvements

1. **Idiot Protector**: Viability check that warns users about impractical/joke business ideas
2. **Domain Extraction Service**: Extracts business domain from project descriptions
3. **Domain-Targeted Spider Queries**: Business agents now use domain-specific search terms
4. **Honest Data Reporting**: When domain-specific data is limited, the system honestly reports this
5. **Trend Analysis Fix**: Fixed extraction of trend data for UI display (was showing "1 data point", now shows actual trend count)

---

## Problem Statement

**ChatGPT Feedback on Business Research PDFs:**
> "The spiders gather what look like 'general tech/AI' or 'current affairs' pieces. For example, even if I said 'AI fitness coach app,' the articles discuss Meta's design, LLM confessions, geothermal energy, etc. None relate to the fitness industry."

**Root Cause:** Spider data categories (ai_ml, tech_trends, etc.) are too broad and don't match specific business domains like fitness, fintech, or edtech.

---

## Solution: Domain Extraction Service

### New File: `core/services/domain_extraction_service.py`

A comprehensive service that:
1. Extracts the primary business domain from project descriptions
2. Generates domain-specific spider search queries
3. Maps domains to appropriate spider categories
4. Recommends relevant subreddits for research
5. Uses GPT-4o-mini for enhanced extraction with keyword fallback

### 13 Supported Business Domains

| Domain | Tags | Example Business |
|--------|------|------------------|
| `fitness_health` | fitness, gym, workout, nutrition | AI fitness coaching app |
| `saas_b2b` | SaaS, enterprise, B2B, software | Project management tool |
| `ecommerce_retail` | shop, store, retail, marketplace | Online clothing store |
| `fintech_finance` | fintech, banking, investment, crypto | Payment processing app |
| `edtech_learning` | education, learning, courses, tutoring | Online tutoring platform |
| `food_restaurant` | restaurant, food delivery, meal prep | Meal kit delivery service |
| `mental_health` | therapy, counseling, wellness, mindfulness | Mental health app |
| `ai_ml` | AI, machine learning, NLP, automation | AI content generator |
| `creator_economy` | creator, influencer, content, social media | Creator monetization platform |
| `real_estate` | property, housing, real estate, rental | Property management software |
| `gaming_entertainment` | gaming, esports, entertainment, streaming | Game streaming platform |
| `travel_hospitality` | travel, booking, hotel, tourism | Travel booking app |
| `general_startup` | (fallback) | Generic startup ideas |

### Domain Extraction Result

```python
@dataclass
class DomainExtractionResult:
    primary_domain: str          # e.g., "fitness_health"
    domain_tags: List[str]       # e.g., ["fitness", "health", "ai", "coaching"]
    spider_queries: List[str]    # e.g., ["AI fitness coaching", "fitness app market 2024"]
    spider_categories: List[str] # e.g., ["ai_ml", "innovation"]
    subreddits: List[str]        # e.g., ["r/fitness", "r/personaltraining"]
    confidence: float            # 0.0-1.0
    reasoning: str               # GPT's explanation
```

---

## Implementation Details

### 1. Business Viability Check ("Idiot Protector")

Added to both `CompetitorAnalysisAgent` and `CustomerResearchAgent`:

```python
def _check_business_viability(self, task: str) -> Dict[str, Any]:
    """Session 350: Check if business idea is viable before research."""
    # Uses GPT-4o-mini to score 0-100
    # Detects jokes, absurd ideas, impractical concepts
    # Returns warning message for low-scoring ideas
```

**Example:**
- Input: "An Onion Bar - a restaurant that only serves raw onions with salt"
- Output: `viability_score: 15, is_joke: True, warning: "This appears to be an impractical or joke business idea..."`

### 2. Domain Targeting in Project Context

Updated `_get_project_context()` in both agents:

```python
def _get_project_context(self, project_id: str) -> Dict:
    # ... existing code ...

    # Session 350: Domain targeting
    domain_targeting = project.get_domain_targeting()
    if domain_targeting:
        context['domain_targeting'] = domain_targeting
        context['primary_domain'] = domain_targeting.get('primary_domain')
        context['domain_tags'] = domain_targeting.get('domain_tags', [])
        context['spider_queries'] = domain_targeting.get('spider_queries', [])
        context['domain_subreddits'] = domain_targeting.get('subreddits', [])
```

### 3. Domain-Aware Spider Queries

When searching spider data, agents now use domain-specific queries:

```python
# Use domain-targeted queries for spider search
domain_queries = project_context.get('spider_queries', [])
for query in domain_queries[:3]:  # Use top 3 domain queries
    search_results = unified_search.unified_search(query, limit=5)
```

### 4. Honest Data Reporting

Synthesis results now include domain relevance metrics:

```python
'domain_relevance': {
    'score': 45,  # Percentage of items matching domain tags
    'domain_relevant_items': 9,
    'total_items': 20,
    'primary_domain': 'fitness_health',
    'is_domain_specific': True  # True if score >= 30%
}
```

When domain-specific data is limited, the analysis honestly acknowledges this limitation.

---

## Files Modified

| File | Changes |
|------|---------|
| `core/services/domain_extraction_service.py` | **NEW** - 350 lines, domain extraction logic |
| `core/models_partnership.py` | Added domain targeting methods (lines 432-523) |
| `core/agents/business/competitor_analysis_agent.py` | Viability check + domain targeting |
| `core/agents/business/customer_research_agent.py` | Viability check + domain targeting |
| `core/services/research_orchestrator.py` | **Fixed** `_extract_research_summary()` for trend_analysis |

---

## Model Changes: PartnershipProject

New methods added to `PartnershipProject`:

```python
def extract_and_save_domains(self, use_gpt: bool = True) -> dict:
    """Extract domain information and save to metadata."""

def get_domain_targeting(self) -> dict:
    """Get domain targeting info, extracting if not already present."""

@property
def primary_domain(self) -> str

@property
def domain_tags(self) -> list

@property
def spider_queries(self) -> list

@property
def domain_subreddits(self) -> list
```

---

## Bug Fix: Project Deletion 500 Error

**Problem:** DELETE `/api/creative-projects/{id}/delete/` returned 500 Internal Server Error

**Root Cause:** Migration 0065 was marked as applied but tables weren't actually created:
- `core_projectresearchfeedback` - Missing
- `core_projectspiderpriority` - Missing

**Fix:** Manually created tables via SQL:
```sql
CREATE TABLE core_projectresearchfeedback (
    id SERIAL PRIMARY KEY,
    project_id UUID REFERENCES core_partnershipproject(id),
    ...
);
CREATE TABLE core_projectspiderpriority (
    id SERIAL PRIMARY KEY,
    project_id UUID REFERENCES core_partnershipproject(id),
    ...
);
```

---

## Bug Fix: Trend Analysis UI Display

**Problem:** Trend Analysis section showed "1 data point" and just echoed the task text instead of displaying actual trend data.

**Root Cause:** `_extract_research_summary()` in `research_orchestrator.py` was:
1. Using `len(tool_results)` = 1 as the data point count (instead of extracting `result['data_points']`)
2. Displaying the task text as summary instead of extracting trend topics

**Fix:** Updated `_extract_research_summary()` for `trend_analysis` type to:
1. Navigate into `tool_results[0]['result']` to get actual trend data
2. Extract `data_points`, `sources`, `trends`, and `discussions` from the result
3. Build a formatted summary with trend topics and relevance scores

**Before:**
- 1 data point
- "Analyzed trends: Analyze current market trends..."

**After:**
- 21 data points
- **Top Trends (15 found):**
  - InterviewFlowAI - AI Interviews (relevance: 47%) - producthunt
  - Building a Clinical AI Assistant... (relevance: 45%) - devto
  - etc.

---

## Testing

### Domain Extraction Test

```python
# In Django shell
from core.services.domain_extraction_service import get_domain_extraction_service

service = get_domain_extraction_service()
result = service.extract_domains("AI-powered fitness coaching app that creates personalized workout plans")

print(f"Primary Domain: {result.primary_domain}")  # fitness_health
print(f"Tags: {result.domain_tags}")  # ['fitness', 'health', 'ai', 'coaching', 'personalization']
print(f"Subreddits: {result.subreddits}")  # ['r/fitness', 'r/personaltraining', 'r/homegym']
```

### Viability Check Test

```python
# Absurd idea detection
from core.agents.business.competitor_analysis_agent import CompetitorAnalysisAgent

agent = CompetitorAnalysisAgent()
result = agent._check_business_viability("An Onion Bar - restaurant serving only raw onions")
print(f"Viability Score: {result['viability_score']}")  # ~15
print(f"Is Joke: {result['is_joke']}")  # True
print(f"Warning: {result['warning']}")  # "This appears to be impractical..."
```

---

## Bug Fix: [Learned] Prefix Accumulation

**Problem:** Agent Learning Activity feed showed accumulated `[Learned]` prefixes:
```
📖 [Learned] [Learned] [Learned] Guru - Freelance Int
```

**Root Cause:** When knowledge is transferred A → B → C, each transfer added a new `[Learned]` prefix.

**Fixes:**
1. `core/tasks.py`: Strip existing prefixes before adding new one
2. `core/tasks.py`: Clean title in `transfer_summary`
3. `core/services/collective_intelligence.py`: Strip prefixes in API response
4. `ai_core/templates/ai_image_studio.html`: Strip prefixes in UI display
5. Database cleanup: Fixed 20 existing entries

**Result:**
- Before: `[Learned] [Learned] [Learned] Guru - Freelance Int`
- After: `Guru - Freelance Intelligence`

---

## Next Session Priorities (Session 351)

1. **Agent Knowledge Application to Research**: Investigate if agent-shared knowledge and conversations are being applied to business research
2. **Boardroom Integration**: Apply Boardroom discussions/decisions to business research when relevant
3. **Agent Conversation → Research Pipeline**: Ensure insights from agent discussions feed into research synthesis

---

## Related Documentation

- Session 349: `docs/handoffs/SESSION_349_PROMPT_VS_CHAT_AUDIT_AND_INTEGRATION.md`
- Session 348: `docs/handoffs/SESSION_348_RESEARCH_PIPELINE_FIXES.md`
- Architecture: `docs/ARCHITECTURE.md`
