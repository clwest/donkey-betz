"""
Search Strategy Service
========================

Shared service that generates intelligent query plans for research agents.
Instead of doing a single search with the literal user input, this service
produces multiple query variants using paraphrasing, broadening, and
narrowing strategies.

Used by: ResearchAgent, TopicMinerAgent, TrendAnalysisAgent, and any
agent that needs to search for information.

Usage:
    from core.services.search_strategy_service import generate_query_plan

    plan = generate_query_plan(
        seed_text="Why most AI teams never get past the demo stage",
        workspace_brief={"topic": "...", "audience": "...", "focus_areas": [...]},
    )
    # Returns: [
    #   {"query": "AI teams stuck demo stage production gap", "strategy": "keyword_extract", "priority": 1},
    #   {"query": "why AI projects fail to move from prototype to production", "strategy": "paraphrase", "priority": 2},
    #   {"query": "AI deployment challenges enterprise teams", "strategy": "broaden", "priority": 3},
    #   ...
    # ]
"""

import logging
import re
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


# Stopwords to filter from keyword extraction
STOPWORDS = frozenset([
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'can', 'shall', 'to', 'of', 'in', 'for',
    'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
    'and', 'but', 'or', 'nor', 'not', 'so', 'yet', 'both', 'each',
    'how', 'what', 'when', 'where', 'which', 'who', 'why', 'most',
    'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them',
    'never', 'get', 'past', 'about', 'just', 'more', 'very', 'too',
])

# Paraphrase templates — deterministic, no LLM needed
PARAPHRASE_TEMPLATES = [
    "why {topic_keywords} happens",
    "{topic_keywords} challenges and solutions",
    "how to overcome {topic_keywords}",
    "{topic_keywords} best practices 2026",
    "common mistakes {topic_keywords}",
    "{topic_keywords} case studies examples",
    "experts opinions {topic_keywords}",
    "{topic_keywords} industry trends",
]

# Broadening templates — expand the search scope
BROADEN_TEMPLATES = [
    "{broader_topic} industry challenges",
    "{broader_topic} common failures",
    "{broader_topic} success factors",
    "{broader_topic} transformation journey",
]

# Narrowing templates — focus on specific angles
NARROW_TEMPLATES = [
    "{topic_keywords} {focus_area}",
    "{focus_area} {topic_keywords} strategies",
    "{topic_keywords} for {audience}",
]


def generate_query_plan(
    seed_text: str,
    workspace_brief: Optional[Dict[str, Any]] = None,
    max_queries: int = 8,
) -> List[Dict[str, Any]]:
    """
    Generate a prioritized search query plan from a seed topic.

    Args:
        seed_text: The original topic/question
        workspace_brief: Optional workspace context {topic, audience, focus_areas, notes}
        max_queries: Maximum number of queries to generate

    Returns:
        List of query dicts: [{query, strategy, priority, source_hint}]
    """
    brief = workspace_brief or {}
    queries = []
    priority = 1

    # Extract keywords from seed
    keywords = _extract_keywords(seed_text)
    topic_keywords = ' '.join(sorted(keywords)[:6])

    # Get broader topic (first 3-4 significant words)
    broader_topic = ' '.join(sorted(keywords)[:3])

    # Get focus areas and audience from brief
    focus_areas = brief.get('focus_areas', [])
    if isinstance(focus_areas, str):
        focus_areas = [focus_areas]
    audience = brief.get('audience', '')

    # Strategy 1: Direct seed (priority 1)
    queries.append({
        'query': seed_text[:200],
        'strategy': 'direct_seed',
        'priority': priority,
        'source_hint': 'news',
    })
    priority += 1

    # Strategy 2: Keyword extract (priority 2)
    if topic_keywords and topic_keywords != seed_text[:50]:
        queries.append({
            'query': topic_keywords,
            'strategy': 'keyword_extract',
            'priority': priority,
            'source_hint': 'search',
        })
        priority += 1

    # Strategy 3: Paraphrases (priority 3-5)
    for template in PARAPHRASE_TEMPLATES[:3]:
        query = template.format(topic_keywords=topic_keywords)
        queries.append({
            'query': query,
            'strategy': 'paraphrase',
            'priority': priority,
            'source_hint': 'search',
        })
        priority += 1

    # Strategy 4: Focus area narrowing (priority 6+)
    for area in focus_areas[:2]:
        if isinstance(area, str) and area.strip():
            for template in NARROW_TEMPLATES[:1]:
                query = template.format(
                    topic_keywords=topic_keywords,
                    focus_area=area.strip(),
                    audience=audience or 'professionals',
                )
                queries.append({
                    'query': query,
                    'strategy': 'narrow_focus',
                    'priority': priority,
                    'source_hint': 'search',
                })
                priority += 1

    # Strategy 5: Audience-specific (if audience provided)
    if audience:
        queries.append({
            'query': f"{topic_keywords} {audience}",
            'strategy': 'audience_targeted',
            'priority': priority,
            'source_hint': 'search',
        })
        priority += 1

    # Strategy 6: Broadening (last resort)
    for template in BROADEN_TEMPLATES[:2]:
        query = template.format(broader_topic=broader_topic)
        queries.append({
            'query': query,
            'strategy': 'broaden',
            'priority': priority,
            'source_hint': 'search',
        })
        priority += 1

    # Deduplicate and cap
    seen = set()
    unique_queries = []
    for q in queries:
        key = q['query'].lower().strip()
        if key not in seen:
            seen.add(key)
            unique_queries.append(q)

    return unique_queries[:max_queries]


def evaluate_search_results(
    query_plan: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    seed_text: str,
) -> Dict[str, Any]:
    """
    Evaluate whether search results are sufficient and on-topic.

    Returns:
        {
            'sufficient': bool,
            'quality_score': 0-100,
            'total_results': int,
            'on_topic_results': int,
            'recommendation': 'proceed' | 'retry_broader' | 'retry_narrower' | 'escalate',
            'next_queries': [...] (if retry recommended),
        }
    """
    if not results:
        return {
            'sufficient': False,
            'quality_score': 0,
            'total_results': 0,
            'on_topic_results': 0,
            'recommendation': 'retry_broader',
            'next_queries': _generate_broader_queries(seed_text),
        }

    seed_keywords = _extract_keywords(seed_text)
    total = len(results)

    # Check how many results are on-topic
    on_topic = 0
    for r in results:
        content = str(r.get('content', r.get('snippet', r.get('text', '')))).lower()
        title = str(r.get('title', '')).lower()
        match_count = sum(1 for kw in seed_keywords if kw in content or kw in title)
        if match_count >= 2:
            on_topic += 1

    quality = int((on_topic / max(total, 1)) * 100)

    if on_topic >= 3 and quality >= 40:
        return {
            'sufficient': True,
            'quality_score': quality,
            'total_results': total,
            'on_topic_results': on_topic,
            'recommendation': 'proceed',
        }
    elif on_topic >= 1:
        return {
            'sufficient': False,
            'quality_score': quality,
            'total_results': total,
            'on_topic_results': on_topic,
            'recommendation': 'retry_narrower',
            'next_queries': _generate_narrow_queries(seed_text, seed_keywords),
        }
    else:
        return {
            'sufficient': False,
            'quality_score': quality,
            'total_results': total,
            'on_topic_results': on_topic,
            'recommendation': 'retry_broader',
            'next_queries': _generate_broader_queries(seed_text),
        }


def _extract_keywords(text: str) -> set:
    """Extract meaningful keywords from text."""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return {w for w in words if w not in STOPWORDS}


def _generate_broader_queries(seed_text: str) -> List[Dict[str, Any]]:
    """Generate broader fallback queries."""
    keywords = _extract_keywords(seed_text)
    broader = ' '.join(sorted(keywords)[:3])
    return [
        {'query': f"{broader} overview trends", 'strategy': 'broaden_retry'},
        {'query': f"{broader} analysis 2026", 'strategy': 'broaden_retry'},
    ]


def _generate_narrow_queries(seed_text: str, keywords: set) -> List[Dict[str, Any]]:
    """Generate narrower retry queries."""
    kw_list = sorted(keywords)
    return [
        {'query': f'"{" ".join(kw_list[:4])}"', 'strategy': 'narrow_exact'},
        {'query': f"{' '.join(kw_list[:5])} solutions case study", 'strategy': 'narrow_specific'},
    ]
