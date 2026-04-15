"""
Evidence Cardifier
===================

Transforms raw research outputs (search results, spider hits, research blobs)
into structured Evidence Cards that the ContentWriterAgent can cite directly.

Each Evidence Card is a compact, citable unit:
- A canonical claim (<=30 words)
- A supporting excerpt (<=200 tokens)
- Source metadata (title, domain, URL, date)
- Confidence score and citation label

This is the bridge between messy research and clean, citable content.

Usage:
    from core.services.evidence_cardifier import generate_evidence_cards
    cards = generate_evidence_cards(research_output, brief_topic, max_cards=12)
"""

import hashlib
import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Domains that get a confidence boost (authoritative sources)
AUTHORITY_DOMAINS = {
    # Major tech/business
    'techcrunch.com': 0.15, 'wired.com': 0.15, 'technologyreview.com': 0.2,
    'hbr.org': 0.2, 'mckinsey.com': 0.2, 'deloitte.com': 0.15,
    'gartner.com': 0.2, 'forrester.com': 0.2, 'bloomberg.com': 0.15,
    'reuters.com': 0.15, 'wsj.com': 0.15, 'nytimes.com': 0.1,
    'bbc.com': 0.1, 'bbc.co.uk': 0.1, 'forbes.com': 0.1,
    # Academic/gov
    'arxiv.org': 0.2, 'nature.com': 0.2, 'sciencedirect.com': 0.15,
    'gov': 0.15, 'edu': 0.15, 'acm.org': 0.15, 'ieee.org': 0.15,
    # Industry
    'shrm.org': 0.15, 'stackoverflow.com': 0.1, 'github.com': 0.1,
    'medium.com': 0.05, 'substack.com': 0.05,
}

# Domains that get a confidence penalty
LOW_QUALITY_DOMAINS = {
    'pinterest.com': -0.3, 'quora.com': -0.1, 'ehow.com': -0.3,
    'wikihow.com': -0.1, 'about.com': -0.2,
}

# Regex for detecting statistics/numbers in text
STAT_PATTERN = re.compile(
    r'\b\d+[\.,]?\d*\s*(%|percent|billion|million|thousand|x|fold|hours|days|weeks|months)\b',
    re.IGNORECASE,
)


def generate_evidence_cards(
    research_output: str,
    brief_topic: str,
    brief: Optional[Dict[str, Any]] = None,
    max_cards: int = 12,
    min_confidence: float = 0.3,
) -> List[Dict[str, Any]]:
    """
    Generate Evidence Cards from raw research output.

    Args:
        research_output: Raw research text (from ResearchAgent)
        brief_topic: The workspace brief topic
        brief: Full workspace brief dict (optional)
        max_cards: Maximum cards to produce
        min_confidence: Minimum confidence threshold

    Returns:
        List of Evidence Card dicts, sorted by confidence descending
    """
    if not research_output or len(research_output) < 50:
        logger.warning("Evidence Cardifier: insufficient research input (%d chars)", len(research_output or ''))
        return []

    # Step 1: Extract source blocks from research text
    source_blocks = _extract_source_blocks(research_output)
    logger.info("Evidence Cardifier: extracted %d source blocks from %d chars", len(source_blocks), len(research_output))

    if not source_blocks:
        # Fallback: try to extract claims from raw text without source structure
        source_blocks = _extract_fallback_blocks(research_output)

    # Step 2: Extract claims from each source block using LLM
    raw_cards = _extract_claims_from_blocks(source_blocks, brief_topic, brief)
    logger.info("Evidence Cardifier: extracted %d raw claim cards", len(raw_cards))

    # Step 3: Score and rank cards
    scored_cards = _score_and_rank(raw_cards, brief_topic)

    # Step 4: Deduplicate
    deduped = _deduplicate_cards(scored_cards)

    # Step 5: Filter by confidence and cap
    filtered = [c for c in deduped if c['confidence_score'] >= min_confidence][:max_cards]

    # Step 6: Assign citation labels
    for i, card in enumerate(filtered):
        card['citation_label'] = f"[{i + 1}]"

    logger.info(
        "Evidence Cardifier: produced %d cards (from %d raw, %d after dedup, min_conf=%.2f)",
        len(filtered), len(raw_cards), len(deduped), min_confidence,
    )

    return filtered


def format_cards_for_writer(cards: List[Dict[str, Any]], research_summary: str = '') -> str:
    """
    Format Evidence Cards into a writer-consumable prompt block.

    Returns a compact text block with research summary + card references.
    """
    parts = []

    if research_summary:
        parts.append(f"## Research Summary\n{research_summary[:600]}\n")

    if not cards:
        parts.append("## Evidence Cards\nNo structured evidence available. Write based on research summary only.\n")
        return '\n'.join(parts)

    parts.append(f"## Evidence Cards ({len(cards)} sources)\n")
    parts.append("Use these cards to support claims. Insert citation labels (e.g., [1]) inline.\n")

    for card in cards:
        source = card.get('source', {})
        parts.append(
            f"{card['citation_label']} **{card['claim_text']}**\n"
            f"   Excerpt: \"{card['excerpt'][:200]}\"\n"
            f"   Source: {source.get('title', 'Unknown')} — {source.get('domain', '')} "
            f"({source.get('published_date', 'n.d.')})\n"
            f"   URL: {source.get('url', 'N/A')}\n"
            f"   Confidence: {card['confidence_score']:.0%}\n"
        )

    parts.append("\n## Citation List (include at bottom of article)\n")
    for card in cards:
        source = card.get('source', {})
        parts.append(
            f"{card['citation_label']} {source.get('title', 'Unknown')} — "
            f"{source.get('domain', '')} — {source.get('url', 'N/A')}"
        )

    return '\n'.join(parts)


# === Internal Functions ===

def _extract_source_blocks(research_text: str) -> List[Dict[str, Any]]:
    """Extract structured source blocks from research text."""
    blocks = []

    # Pattern: "- claim/description\n  *Source: Title*\n  *URL: https://...*"
    source_pattern = re.compile(
        r'-\s*(.+?)\n\s*\*Source:\s*(.+?)\*\s*\n\s*\*URL:\s*(https?://\S+)\*',
        re.MULTILINE | re.DOTALL,
    )

    for match in source_pattern.finditer(research_text):
        content = match.group(1).strip()
        source_title = match.group(2).strip()
        url = match.group(3).strip()
        domain = urlparse(url).netloc.replace('www.', '')

        blocks.append({
            'content': content[:500],
            'source': {
                'title': source_title[:200],
                'domain': domain,
                'url': url,
                'published_date': _extract_date(content),
            },
        })

    # Also try: "Source: URL" pattern (simpler)
    simple_pattern = re.compile(
        r'(?:According to|Source:|From)\s+(.+?)(?:\s*[-—]\s*|\s*\()(https?://\S+)',
        re.IGNORECASE,
    )

    seen_urls = {b['source']['url'] for b in blocks}
    for match in simple_pattern.finditer(research_text):
        url = match.group(2).strip().rstrip(')')
        if url in seen_urls:
            continue
        seen_urls.add(url)
        domain = urlparse(url).netloc.replace('www.', '')

        # Get surrounding context (100 chars before and after)
        start = max(0, match.start() - 200)
        end = min(len(research_text), match.end() + 200)
        context = research_text[start:end].strip()

        blocks.append({
            'content': context[:500],
            'source': {
                'title': match.group(1).strip()[:200],
                'domain': domain,
                'url': url,
                'published_date': _extract_date(context),
            },
        })

    return blocks


def _extract_fallback_blocks(research_text: str) -> List[Dict[str, Any]]:
    """Fallback: extract blocks from unstructured text by splitting on URLs."""
    blocks = []
    url_pattern = re.compile(r'(https?://\S+)')

    urls = url_pattern.findall(research_text)
    for url in urls[:20]:
        domain = urlparse(url).netloc.replace('www.', '')
        # Get surrounding text
        idx = research_text.find(url)
        start = max(0, idx - 300)
        end = min(len(research_text), idx + 100)
        context = research_text[start:end].strip()

        blocks.append({
            'content': context[:500],
            'source': {
                'title': domain,
                'domain': domain,
                'url': url.rstrip('.,;)'),
                'published_date': _extract_date(context),
            },
        })

    return blocks


def _extract_claims_from_blocks(
    blocks: List[Dict[str, Any]],
    brief_topic: str,
    brief: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Extract claims from source blocks using a single LLM call."""
    if not blocks:
        return []

    # Build a compact extraction prompt
    block_texts = []
    for i, block in enumerate(blocks[:15]):  # Cap at 15 blocks
        source = block.get('source', {})
        block_texts.append(
            f"[Source {i+1}] {source.get('title', 'Unknown')} ({source.get('domain', '')})\n"
            f"URL: {source.get('url', 'N/A')}\n"
            f"Content: {block['content'][:300]}\n"
        )

    blocks_text = '\n---\n'.join(block_texts)

    extraction_prompt = f"""Extract evidence claims from these sources for an article about: "{brief_topic}"

{blocks_text}

For each source that contains a relevant claim, extract:
1. A concise claim (max 30 words) that supports the article topic
2. The best supporting excerpt (1-2 sentences, quote if possible)
3. Whether the excerpt is a direct quote

Return a JSON array. Each item: {{"source_index": N, "claim_text": "...", "excerpt": "...", "is_quote": true/false}}
Only include claims that DIRECTLY relate to "{brief_topic}". Skip irrelevant sources.
Return at most 12 claims. Return ONLY valid JSON array, no markdown."""

    try:
        from core.llm_enforcer import LLMEnforcer
        enforcer = LLMEnforcer()
        result = enforcer.enforce_real_ai(
            prompt=extraction_prompt,
            agent_name='EvidenceCardifier',
            task_type='extraction',
            max_tokens=1500,
        )

        response_text = result.get('response', '')

        # Parse JSON from response
        claims = _parse_json_array(response_text)
        if not claims:
            logger.warning("Evidence Cardifier: LLM returned no parseable claims")
            return _extract_claims_heuristic(blocks, brief_topic)

        # Convert to card format
        cards = []
        for claim in claims:
            src_idx = claim.get('source_index', 1) - 1
            if src_idx < 0 or src_idx >= len(blocks):
                continue

            block = blocks[src_idx]
            source = block.get('source', {})

            cards.append({
                'id': _generate_card_id(claim.get('claim_text', ''), source.get('url', '')),
                'claim_text': claim.get('claim_text', '')[:120],
                'excerpt': claim.get('excerpt', '')[:400],
                'excerpt_is_quote': claim.get('is_quote', False),
                'source': source,
                'confidence_score': 0.5,  # Will be scored in next step
                'duplicate_count': 1,
                'tags': _detect_claim_tags(claim.get('claim_text', ''), claim.get('excerpt', '')),
            })

        return cards

    except Exception as e:
        logger.warning("Evidence Cardifier: LLM extraction failed: %s — falling back to heuristics", e)
        return _extract_claims_heuristic(blocks, brief_topic)


def _extract_claims_heuristic(blocks: List[Dict[str, Any]], brief_topic: str) -> List[Dict[str, Any]]:
    """Fallback: extract claims using simple heuristics (no LLM)."""
    cards = []
    topic_words = set(brief_topic.lower().split())

    for block in blocks[:12]:
        content = block.get('content', '')
        source = block.get('source', {})

        # Simple relevance: count topic word matches
        content_lower = content.lower()
        matches = sum(1 for w in topic_words if w in content_lower)
        if matches < 2:
            continue

        # Use first sentence as claim
        sentences = re.split(r'[.!?]\s+', content)
        claim = sentences[0][:120] if sentences else content[:120]

        # Use first 2 sentences as excerpt
        excerpt = '. '.join(sentences[:2])[:400] if len(sentences) > 1 else content[:400]

        cards.append({
            'id': _generate_card_id(claim, source.get('url', '')),
            'claim_text': claim,
            'excerpt': excerpt,
            'excerpt_is_quote': False,
            'source': source,
            'confidence_score': 0.3 + (matches * 0.05),
            'duplicate_count': 1,
            'tags': _detect_claim_tags(claim, excerpt),
        })

    return cards


def _score_and_rank(cards: List[Dict[str, Any]], brief_topic: str) -> List[Dict[str, Any]]:
    """Score cards by relevance, authority, and evidence quality."""
    topic_words = set(w.lower() for w in brief_topic.split() if len(w) > 3)

    for card in cards:
        claim_lower = card['claim_text'].lower()
        excerpt_lower = card.get('excerpt', '').lower()
        domain = card.get('source', {}).get('domain', '')

        # Topical relevance (0-1)
        claim_matches = sum(1 for w in topic_words if w in claim_lower)
        excerpt_matches = sum(1 for w in topic_words if w in excerpt_lower)
        topical = min(1.0, (claim_matches * 0.15) + (excerpt_matches * 0.05))

        # Authority score (0-1)
        authority = 0.5  # baseline
        for auth_domain, boost in AUTHORITY_DOMAINS.items():
            if domain.endswith(auth_domain):
                authority += boost
                break
        for bad_domain, penalty in LOW_QUALITY_DOMAINS.items():
            if domain.endswith(bad_domain):
                authority += penalty
                break
        authority = max(0.0, min(1.0, authority))

        # Statistics/numbers boost
        has_stats = bool(STAT_PATTERN.search(card.get('excerpt', '')))
        stat_boost = 0.1 if has_stats else 0.0

        # Duplicate bonus
        dup_bonus = min(0.2, card.get('duplicate_count', 1) * 0.05)

        # Final confidence
        card['confidence_score'] = min(1.0, (
            topical * 0.45 +
            authority * 0.30 +
            dup_bonus * 0.15 +
            stat_boost * 0.10
        ))

    cards.sort(key=lambda c: c['confidence_score'], reverse=True)
    return cards


def _deduplicate_cards(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate cards (same URL + similar claim)."""
    seen = {}  # url -> card
    deduped = []

    for card in cards:
        url = card.get('source', {}).get('url', '')
        claim = card['claim_text'].lower().strip()

        # Check for duplicate URL
        if url and url in seen:
            # Merge: increment duplicate count on the existing card
            seen[url]['duplicate_count'] = seen[url].get('duplicate_count', 1) + 1
            continue

        # Check for very similar claims (>80% word overlap)
        is_dup = False
        for existing in deduped:
            existing_words = set(existing['claim_text'].lower().split())
            claim_words = set(claim.split())
            if existing_words and claim_words:
                overlap = len(existing_words & claim_words) / max(len(existing_words), len(claim_words))
                if overlap > 0.8:
                    existing['duplicate_count'] = existing.get('duplicate_count', 1) + 1
                    is_dup = True
                    break

        if not is_dup:
            if url:
                seen[url] = card
            deduped.append(card)

    return deduped


def _detect_claim_tags(claim: str, excerpt: str) -> List[str]:
    """Detect claim type tags."""
    tags = []
    text = f"{claim} {excerpt}".lower()

    if STAT_PATTERN.search(text):
        tags.append('statistic')
    if any(w in text for w in ['survey', 'study', 'research', 'report', 'analysis']):
        tags.append('research')
    if any(w in text for w in ['example', 'case study', 'company', 'team', 'built', 'implemented']):
        tags.append('example')
    if '"' in excerpt or "'" in excerpt:
        tags.append('quote')
    if any(w in text for w in ['trend', 'growing', 'increasing', 'declining', 'shift']):
        tags.append('trend')

    return tags or ['general']


def _extract_date(text: str) -> Optional[str]:
    """Try to extract a date from text."""
    # Match common date patterns
    patterns = [
        r'(\d{4}-\d{2}-\d{2})',  # 2026-04-04
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+\d{4})',  # April 4, 2026
        r'(\d{1,2}/\d{1,2}/\d{4})',  # 4/4/2026
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def _generate_card_id(claim: str, url: str) -> str:
    """Generate a deterministic card ID."""
    content = f"{claim.lower().strip()}{url.lower().strip()}"
    return f"ec-{hashlib.sha256(content.encode()).hexdigest()[:8]}"


def _parse_json_array(text: str) -> List[Dict[str, Any]]:
    """Parse a JSON array from LLM response text, handling markdown fences."""
    text = text.strip()

    # Strip markdown code fences
    if text.startswith('```'):
        lines = text.split('\n')
        if lines[-1].strip() == '```':
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        text = '\n'.join(lines).strip()

    # Session 1103c: LLM claim-extraction used to silently return [] on
    # JSON parse failure, which meant a malformed model response dropped
    # every claim with zero debuggability. Now we log both the first
    # parse failure and the recovery fallback so we can tell whether the
    # LLM output was genuinely claim-free or just badly formatted.
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
        logger.warning(
            "evidence_cardifier: LLM claim-extraction returned non-list "
            "JSON type=%s — returning empty claims list",
            type(result).__name__,
        )
        return []
    except json.JSONDecodeError as primary_err:
        match = re.search(r'\[[\s\S]*\]', text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError as bracket_err:
                logger.warning(
                    "evidence_cardifier: both direct parse and bracket-"
                    "recovery failed (primary=%s, bracket=%s) — first 200 "
                    "chars of response: %r",
                    primary_err, bracket_err, text[:200],
                )
        else:
            logger.warning(
                "evidence_cardifier: LLM response had no parseable JSON "
                "array (%s) — first 200 chars: %r",
                primary_err, text[:200],
            )
        return []
