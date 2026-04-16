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
    # Session 1092: instruction-meta words that pollute keyword extraction.
    # Tasks like "Produce a concise one-paragraph summary of the most
    # important stock market signals" front-load these words ahead of the
    # actual subject matter. Without filtering, top-N keyword slicing
    # picks "produce, concise, paragraph, summary, important" and buries
    # "stock, market, signals" — which is what broke canary v2.
    'produce', 'concise', 'detailed', 'thorough', 'comprehensive',
    'summary', 'overview', 'analysis', 'report', 'paragraph',
    'important', 'top', 'best', 'main', 'key', 'major',
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
    'first', 'second', 'third', 'last', 'recent', 'latest',
    'create', 'generate', 'write', 'draft', 'compose', 'list',
    'title', 'titled', 'deliverable', 'output', 'result',
    'canary', 'test', 'verify', 'check',
    'citation', 'citations', 'cite', 'reference', 'references',
    'needed', 'required', 'optional', 'please',
    'brief', 'short', 'long', 'quick', 'fast',
    'hours', 'minutes', 'days', 'weeks', 'months', 'years',
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

    # Use brief topic as primary seed if available (it's the actual user intent)
    brief_topic = brief.get('topic', '').strip()
    if brief_topic:
        clean_topic = brief_topic
    else:
        clean_topic = extract_topic_from_task(seed_text)

    # Extract keywords from the CLEAN topic (not the full task string).
    # Session 1092: keep natural reading order so the actual subject words
    # ("stock signals") rank ahead of meta words ("important", "produce").
    keywords = _extract_keywords(clean_topic)
    topic_keywords = ' '.join(keywords[:6])

    # Broader query — first 3 significant words in original order.
    broader_topic = ' '.join(keywords[:3])

    # Get focus areas and audience from brief
    focus_areas = brief.get('focus_areas', [])
    if isinstance(focus_areas, str):
        focus_areas = [focus_areas]
    audience = brief.get('audience', '')

    # Strategy 1: Direct brief topic as-is (highest priority — exact user intent)
    queries.append({
        'query': clean_topic[:200],
        'strategy': 'direct_brief_topic',
        'priority': priority,
        'source_hint': 'news',
    })
    priority += 1

    # Strategy 2: Brief topic + focus areas (combine topic with each focus area)
    for area in focus_areas[:3]:
        if isinstance(area, str) and area.strip():
            queries.append({
                'query': f"{clean_topic[:100]} {area.strip()}",
                'strategy': 'topic_plus_focus',
                'priority': priority,
                'source_hint': 'search',
            })
            priority += 1

    # Strategy 3: Keyword extract (priority 3+)
    if topic_keywords and topic_keywords != clean_topic[:50]:
        queries.append({
            'query': topic_keywords,
            'strategy': 'keyword_extract',
            'priority': priority,
            'source_hint': 'search',
        })
        priority += 1

    # Strategy 4: Paraphrases (priority 4-6)
    for template in PARAPHRASE_TEMPLATES[:3]:
        query = template.format(topic_keywords=topic_keywords)
        queries.append({
            'query': query,
            'strategy': 'paraphrase',
            'priority': priority,
            'source_hint': 'search',
        })
        priority += 1

    # Strategy 5: Audience-specific (if audience provided)
    if audience:
        queries.append({
            'query': f"{clean_topic[:100]} for {audience}",
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


def extract_topic_from_task(task_text: str) -> str:
    """
    Session 1103: Extract the actual research topic from a verbose task string.

    Pipeline tasks often include boilerplate like 'Deep dive research on...',
    'Topic/Focus:', workspace IDs, audience descriptions, etc. This strips
    all that to find the real topic the user cares about.
    """
    text = task_text.strip()

    # Try explicit topic markers first
    topic_patterns = [
        r'Topic/Focus:\s*(.+?)(?:\.|Target audience|Audience|Tone:|Additional context|$)',
        r'Topic:\s*(.+?)(?:\.|Target audience|Audience|Tone:|Additional context|$)',
        r'Focus:\s*(.+?)(?:\.|Target audience|Audience|Tone:|Additional context|$)',
        r'(?:Research Task|Research):\s*(.+?)(?:\.(?:\s+[A-Z])|Target audience|Tone:|$)',
        r'research (?:on|about|into|regarding)\s+(.+?)(?:\.(?:\s+[A-Z])|Target audience|Tone:|$)',
    ]
    for pattern in topic_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            topic = match.group(1).strip().rstrip('.,;')
            if len(topic) > 10:
                return topic[:200]

    # Strip common instruction prefixes
    cleaned = re.sub(
        r'^(?:Deep dive research on the top trending topics using web search and spider data\.\s*)?',
        '', text, flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r'^(?:Perform|Conduct|Do|Run|Execute)\s+(?:a\s+)?(?:comprehensive\s+|detailed\s+|thorough\s+)?'
        r'(?:research|investigation|analysis)\s+(?:on|about|into|for|regarding)\s+',
        '', cleaned, flags=re.IGNORECASE
    )

    # Strip trailing metadata (workspace IDs, audience, instructions, pipeline boilerplate)
    cleaned = re.sub(r'\s*(?:Target audience|Audience|Tone|Additional context|Canary workspace|workspace \w{8}).*$',
                     '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'\s*\[User Context:.*$', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'\s*—\s*(?:produce|run|return|this run).*$', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    # Strip pipeline instruction sentences
    cleaned = re.sub(r'\.\s+(?:Produce|Include|Return|Use|Run|Generate|Create)\s+.+$', '',
                     cleaned, flags=re.IGNORECASE | re.DOTALL)

    # Strip UUID-like patterns and hex IDs
    cleaned = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '', cleaned)
    cleaned = re.sub(r'\b[0-9a-f]{8,}\b', '', cleaned)

    cleaned = cleaned.strip().rstrip('.,;')
    if cleaned and len(cleaned) > 10:
        return cleaned[:200]

    return task_text[:200]


def _extract_keywords(text: str) -> list:
    """Extract meaningful keywords from text.

    Session 1092:
    - Strip ResearchAgent's [User Context: ...] tail before extraction —
      otherwise user-profile noise ("Alex Chen", "analytical", "balanced")
      contaminates query generation (canary v2 produced "alex anal balanced
      based" queries that hit marine biology / labor docs instead of stocks).
    - Return a *list* preserving first-occurrence order rather than a set, so
      callers using `sorted(...)[:N]` no longer reorder alphabetically and
      drop the actual subject words.  Order-preserving means the literal
      task wording dominates ranking, which is what callers actually want.
    """
    if not text:
        return []
    cleaned = re.sub(r'\s*\[User Context:.*$', '', text, flags=re.DOTALL)
    cleaned = re.sub(
        r'\s*\[Past research patterns:.*$', '', cleaned, flags=re.DOTALL
    )
    seen = set()
    ordered = []
    for raw in re.findall(r'\b[a-zA-Z]{3,}\b', cleaned.lower()):
        if raw in STOPWORDS or raw in seen:
            continue
        seen.add(raw)
        ordered.append(raw)
    return ordered


def _generate_broader_queries(seed_text: str) -> List[Dict[str, Any]]:
    """Generate broader fallback queries.

    Session 1092: keep keyword order from the cleaned seed text; alphabetical
    sort buried subject words behind meta words like "concise", "important".
    """
    keywords = _extract_keywords(seed_text)
    broader = ' '.join(keywords[:3])
    return [
        {'query': f"{broader} overview trends", 'strategy': 'broaden_retry'},
        {'query': f"{broader} analysis 2026", 'strategy': 'broaden_retry'},
    ]


def _generate_narrow_queries(seed_text: str, keywords: list) -> List[Dict[str, Any]]:
    """Generate narrower retry queries.

    Session 1092: keywords arrive as an ordered list (was a set). Use natural
    order so retry queries reflect the literal task wording instead of
    alphabetically-sorted noise.
    """
    kw_list = list(keywords)
    return [
        {'query': f'"{" ".join(kw_list[:4])}"', 'strategy': 'narrow_exact'},
        {'query': f"{' '.join(kw_list[:5])} solutions case study", 'strategy': 'narrow_specific'},
    ]
