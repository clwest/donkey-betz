---
originating_session: 952
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 952 - Narrative Injection Enhancement

**Date:** February 6, 2026
**Focus:** Fix ContentWriterAgent blogs defaulting to "kalshi spider pulled 500 items"
**PRs:** #929 (PA Platform Query), #930 (Narrative Injection Enhancement)

---

## Summary

Fixed two issues this session:
1. PA Platform Query Tool (merged from Session 951)
2. ContentWriterAgent blogs always referencing Kalshi spider telemetry instead of narrative-worthy incidents

---

## Issue 1: Kalshi Spider Spam in Blog Posts

### Problem
ContentWriterAgent blogs always included "kalshi spider pulled 500 items" or similar spider telemetry in the "builder stories" section. This was not a compelling narrative - it's routine data collection, not an incident.

### Root Cause Analysis
Traced the data flow:
1. `ContentWriterAgent.execute()` → `_prepare_initial_context()`
2. → `_generate_enhanced_prompt()` → `FlagshipBlogTemplate`
3. → `generate_flagship_prompt_injection()` → `NarrativeInjectionService.get_recent_incidents()`
4. → `_get_spider_discoveries()` treated routine spider runs as "incidents"

The `_get_spider_discoveries()` method was pulling spider data aggregation records and framing them as narrative-worthy incidents when they're just telemetry.

### Solution - PR #930

Multi-layered enhancement to `NarrativeInjectionService`:

#### 1. Removed Spider Telemetry from Incidents
Spider data collection is not narrative-worthy. Removed `_get_spider_discoveries()` from the incident pipeline.

#### 2. Added Topic Relevance Filtering
New `DOMAIN_KEYWORDS` dictionary maps 6 domains to keywords:
```python
DOMAIN_KEYWORDS = {
    'ai': ['ai', 'agent', 'llm', 'gpt', 'machine learning', ...],
    'finance': ['stock', 'market', 'trading', 'investment', ...],
    'sports': ['sports', 'betting', 'odds', 'nba', 'nfl', ...],
    'tech': ['software', 'code', 'developer', 'api', ...],
    'content': ['blog', 'content', 'writing', 'podcast', ...],
    'business': ['startup', 'revenue', 'growth', ...],
}
```

New methods:
- `_detect_topic_domain(topic)` - Detect domains from topic keywords
- `_filter_by_topic_relevance(incidents, topic)` - Filter incidents by domain match
- `_infer_incident_domain(incident)` - Infer domain from incident content

#### 3. Added Diversity Constraints
`_apply_diversity_constraints(incidents)` ensures max 1 incident per type (learning, decision, recovery, etc.) to prevent same-type dominance.

#### 4. Added Fallback Incidents
When database has no real incidents, provide 3 curated fallback incidents:
```python
FALLBACK_INCIDENTS = [
    {
        'type': 'learning',
        'title': 'System Evolution',
        'narrative': "Our AI learns from every interaction...",
        'domain': ['ai', 'tech'],
        'is_fallback': True
    },
    {
        'type': 'decision',
        'title': 'Autonomous Decision-Making',
        'narrative': "The system makes informed decisions...",
        'domain': ['ai', 'business'],
        'is_fallback': True
    },
    {
        'type': 'recovery',
        'title': 'Resilience by Design',
        'narrative': "When issues arise, the system self-heals...",
        'domain': ['tech', 'ai'],
        'is_fallback': True
    }
]
```

---

## Issue 2: PA Platform Query Tool

### Problem
PA couldn't answer questions like "what reports have been written by agents" because it had no tool for querying the database.

### Solution - PR #929
Added `platform_query_tool` with 5 query types:
- `deliverables` - Blog posts, reports, analyses
- `audit_reports` - Agent audit findings
- `initiatives` - Tracked initiatives
- `agent_outputs` - Outputs by specific agent
- `content_summary` - Overview of all platform content

---

## Files Changed

| File | Changes |
|------|---------|
| `core/services/content_voice_system.py` | DOMAIN_KEYWORDS, FALLBACK_INCIDENTS, topic filtering, diversity constraints, removed spider telemetry |
| `core/personal_ai_assistant_enhanced.py` | Added platform_query_tool (Session 951) |

---

## Testing

```python
# Test NarrativeInjectionService
from core.services.content_voice_system import NarrativeInjectionService

service = NarrativeInjectionService()

# Test fallback incidents (when DB empty)
incidents = service.get_recent_incidents(limit=3, topic="AI agents")
print(f"Got {len(incidents)} incidents")
for inc in incidents:
    print(f"  - [{inc['type']}] {inc['title']} (fallback: {inc.get('is_fallback', False)})")

# Test topic filtering
finance_incidents = service.get_recent_incidents(limit=3, topic="stock market analysis")
sports_incidents = service.get_recent_incidents(limit=3, topic="NBA betting odds")
```

---

## ChatGPT Recommendations Implemented

From the ChatGPT analysis of our content system:

| Recommendation | Status |
|---------------|--------|
| 1. Split Incidents from Telemetry | ✅ Removed spider telemetry |
| 2. Add topic relevance gating | ✅ DOMAIN_KEYWORDS + filtering |
| 3. Add diversity constraints | ✅ Max 1 per incident type |
| 4. Add narrative-worthy threshold | ⏳ Future enhancement |
| 5. Fix 0 incidents starvation | ✅ FALLBACK_INCIDENTS |
| 6. Add content-quality linter | ⏳ Future enhancement |

---

## Next Steps

- Consider adding a Telemetry channel for spider stats (separate from narrative incidents)
- Add more fallback incidents for different domains
- Track which fallbacks are used most often to inform real incident creation

---

## Verification

After deployment, check that blog posts no longer reference spider data collection in builder stories. The incidents should be:
1. Relevant to the blog topic
2. Diverse (not all same type)
3. Narrative-worthy (not telemetry)
