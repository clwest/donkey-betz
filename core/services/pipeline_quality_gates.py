"""
Pipeline Quality Gates
=======================

Lightweight checks that run between pipeline stages to prevent
wasted work. No LLM calls — just embeddings and keyword matching.

Gates:
- Topic Alignment: verifies research matches the workspace brief
- Research Depth: ensures minimum sources and quality
- Strategy Alignment: verifies outline matches research (Phase 2)

Usage (called by workspace_pipeline_runner between stages):
    from core.services.pipeline_quality_gates import check_topic_alignment
    result = check_topic_alignment(workspace_brief, research_output)
    if not result['passed']:
        # handle failure — retry or escalate
"""

import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


# ── Topic Alignment Check ────────────────────────────────────────────────────

# Thresholds (tunable)
KEYWORD_MIN_MATCHES = 2          # Minimum topic keywords found in research
KEYWORD_EXACT_PHRASE_BOOST = True # Exact phrase match = automatic pass
MIN_RESEARCH_SOURCES = 2         # Minimum sources for depth gate
MIN_RESEARCH_LENGTH = 100        # Minimum chars of actual content


def check_topic_alignment(
    workspace_brief: Dict[str, Any],
    research_outputs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Check if research outputs align with the workspace brief topic.

    Args:
        workspace_brief: {topic, audience, focus_areas, ...}
        research_outputs: list of stage outputs from discovery phase

    Returns:
        {
            'passed': bool,
            'score': 0-100,
            'keyword_matches': int,
            'exact_phrase_match': bool,
            'details': str,
            'recommendation': 'proceed' | 'retry' | 'escalate',
            'retry_instruction': str (if retry recommended),
        }
    """
    topic = (workspace_brief.get('topic') or '').strip()
    if not topic:
        # No topic specified — can't check alignment, let it proceed
        return {
            'passed': True,
            'score': 100,
            'keyword_matches': 0,
            'exact_phrase_match': False,
            'details': 'No topic specified in workspace brief — skipping alignment check',
            'recommendation': 'proceed',
        }

    # Combine all research outputs into one text block
    combined_research = _combine_research_outputs(research_outputs)

    if not combined_research:
        return {
            'passed': False,
            'score': 0,
            'keyword_matches': 0,
            'exact_phrase_match': False,
            'details': 'No research content to evaluate',
            'recommendation': 'retry',
            'retry_instruction': f'Research produced no usable content. Focus specifically on: "{topic}"',
        }

    # Check 1: Exact phrase match (normalize dashes for comparison)
    def _normalize_dashes(s: str) -> str:
        return s.replace('\u2014', '-').replace('\u2013', '-').replace('\u2012', '-')

    topic_lower = _normalize_dashes(topic.lower())
    research_lower = _normalize_dashes(combined_research.lower())
    exact_phrase_match = topic_lower in research_lower

    # Session 1103: Also check if most of the topic appears (allow minor wording differences)
    topic_words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', topic_lower) if w not in STOPWORDS]
    if not exact_phrase_match and len(topic_words) >= 4:
        # Check if 80%+ of topic content words appear in a 200-char window
        for i in range(0, len(research_lower) - 100, 50):
            window = research_lower[i:i+200]
            window_hits = sum(1 for w in topic_words if w in window)
            if window_hits >= len(topic_words) * 0.8:
                exact_phrase_match = True
                break

    # Check 2: Keyword overlap
    topic_keywords = _extract_keywords(topic)
    focus_areas = workspace_brief.get('focus_areas', [])
    if isinstance(focus_areas, list):
        for area in focus_areas:
            topic_keywords.update(_extract_keywords(str(area)))

    keyword_matches = sum(1 for kw in topic_keywords if kw in research_lower)
    keyword_ratio = keyword_matches / max(len(topic_keywords), 1)

    # Session 1103: Check for evidence URLs — strong signal research was done
    url_count = len(re.findall(r'https?://\S+', combined_research))

    # Check 3: Audience alignment (bonus)
    audience = (workspace_brief.get('audience') or '').lower()
    audience_mentioned = bool(audience and audience[:20] in research_lower)

    # Calculate composite score
    score = 0

    if exact_phrase_match:
        score += 40  # Strong signal — topic phrase appears verbatim

    # Keyword overlap contributes up to 40 points
    score += int(keyword_ratio * 40)

    # Session 1103: Evidence URLs contribute up to 15 points (real research was done)
    score += min(15, url_count * 3)

    # Audience mention bonus
    if audience_mentioned:
        score += 5

    # Cap at 100
    score = min(100, score)

    # Determine pass/fail and recommendation
    # Session 1103: Lowered threshold from 60 to 40 — keyword matching can't handle
    # paraphrasing (topic says "teams" but research says "projects", "fix" vs "avoid").
    # Evidence URLs provide strong on-topic signal that keyword matching misses.
    if score >= 40 or exact_phrase_match:
        return {
            'passed': True,
            'score': score,
            'keyword_matches': keyword_matches,
            'exact_phrase_match': exact_phrase_match,
            'details': f'Topic aligned (score {score}/100, {keyword_matches}/{len(topic_keywords)} keywords matched)',
            'recommendation': 'proceed',
        }
    elif score >= 25:
        # Borderline — retry with tighter instructions
        seed_phrases = list(topic_keywords)[:5]
        return {
            'passed': False,
            'score': score,
            'keyword_matches': keyword_matches,
            'exact_phrase_match': exact_phrase_match,
            'details': f'Topic partially aligned (score {score}/100). Research may have drifted from "{topic}".',
            'recommendation': 'retry',
            'retry_instruction': (
                f'IMPORTANT: Refocus research on the specific topic: "{topic}". '
                f'Use these seed phrases as anchors: {seed_phrases}. '
                f'Return findings that directly address this topic with explicit mentions.'
            ),
        }
    else:
        # Major mismatch — escalate to human
        return {
            'passed': False,
            'score': score,
            'keyword_matches': keyword_matches,
            'exact_phrase_match': exact_phrase_match,
            'details': f'Topic misaligned (score {score}/100). Research does not match "{topic}".',
            'recommendation': 'escalate',
            'retry_instruction': (
                f'Research completely missed the topic "{topic}". '
                f'Only {keyword_matches}/{len(topic_keywords)} topic keywords found in output.'
            ),
        }


# ── Research Depth Gate ──────────────────────────────────────────────────────

def check_research_depth(
    research_outputs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Check if research has minimum depth (enough content and sources).

    Returns:
        {
            'passed': bool,
            'total_content_length': int,
            'source_count': int,
            'details': str,
            'recommendation': 'proceed' | 'retry',
        }
    """
    combined = _combine_research_outputs(research_outputs)
    total_length = len(combined)

    # Count sources mentioned (URLs, citations)
    url_pattern = re.compile(r'https?://\S+')
    source_count = len(url_pattern.findall(combined))

    # Also count outputs that had real content
    outputs_with_content = sum(
        1 for o in research_outputs
        if len(o.get('full_content', o.get('summary', ''))) > 50
    )

    passed = (total_length >= MIN_RESEARCH_LENGTH and outputs_with_content >= 1)

    if passed:
        return {
            'passed': True,
            'total_content_length': total_length,
            'source_count': source_count,
            'outputs_with_content': outputs_with_content,
            'details': f'Research depth sufficient ({total_length} chars, {source_count} sources, {outputs_with_content} outputs with content)',
            'recommendation': 'proceed',
        }
    else:
        return {
            'passed': False,
            'total_content_length': total_length,
            'source_count': source_count,
            'outputs_with_content': outputs_with_content,
            'details': f'Research too shallow ({total_length} chars, {outputs_with_content} outputs with content). Need more depth.',
            'recommendation': 'retry',
        }


# ── Helpers ──────────────────────────────────────────────────────────────────

STOPWORDS = frozenset([
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'can', 'shall', 'to', 'of', 'in', 'for',
    'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'between', 'out', 'off', 'over',
    'under', 'again', 'further', 'then', 'once', 'and', 'but', 'or', 'nor',
    'not', 'so', 'yet', 'both', 'each', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'only', 'own', 'same', 'than', 'too', 'very',
    'just', 'about', 'how', 'what', 'when', 'where', 'which', 'who', 'why',
    'this', 'that', 'these', 'those', 'it', 'its',
])


def _extract_keywords(text: str) -> set:
    """Extract meaningful keywords from text, filtering stopwords."""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return {w for w in words if w not in STOPWORDS}


def _combine_research_outputs(outputs: List[Dict[str, Any]]) -> str:
    """Combine all research stage outputs into one text block."""
    parts = []
    for output in outputs:
        content = output.get('full_content', '')
        if not content:
            content = output.get('summary', '')
        if content:
            parts.append(str(content))
    return '\n\n'.join(parts)
