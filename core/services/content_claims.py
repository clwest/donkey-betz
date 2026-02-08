"""
Phase 4: Content Claims — SpiderClaim and ClaimsPack Dataclasses

Deterministic claim IDs allow inline citation tracking across the
ContentWriter → ReviewPanel → DecisionEnforcer pipeline.

Claim ID: C- + first 10 hex chars of sha256(normalized_url + title)
"""

import hashlib
import re
from dataclasses import dataclass, field
from typing import List, Optional


def _normalize_url(url: str) -> str:
    """Strip trailing slashes, lowercase, remove protocol prefix."""
    url = (url or '').strip().lower()
    url = re.sub(r'^https?://', '', url)
    return url.rstrip('/')


def make_claim_id(source_url: str, title: str) -> str:
    """Deterministic claim ID: C- + sha256(normalized_url + title)[:10]."""
    payload = _normalize_url(source_url) + (title or '').strip()
    digest = hashlib.sha256(payload.encode('utf-8')).hexdigest()[:10]
    return f'C-{digest}'


@dataclass
class SpiderClaim:
    """A single sourced claim from the spider network or signal clusters."""

    claim_id: str
    claim_text: str
    source_url: str = ''
    source_title: str = ''
    source_author: str = ''
    published_at: Optional[str] = None
    retrieved_at: Optional[str] = None
    spider_name: str = ''
    freshness_hours: float = 0.0
    evidence_excerpt: str = ''
    confidence: float = 0.5
    claim_type: str = 'factual'  # factual | analytical | speculative


@dataclass
class ClaimsPack:
    """Bundle of sourced claims ready for LLM consumption and evidence linking."""

    topic: str = ''
    assembled_at: str = ''
    claims: List[SpiderClaim] = field(default_factory=list)
    sources: List[dict] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    def to_prompt_block(self) -> str:
        """Compact text block for LLM prompt with [C-xxxxxxxxxx] markers."""
        if not self.claims:
            return ''
        lines = [f'=== CLAIMS DATA ({len(self.claims)} sourced claims) ===']
        for c in self.claims:
            url_part = f' | {c.source_url}' if c.source_url else ''
            lines.append(f'[{c.claim_id}] ({c.claim_type}, conf={c.confidence:.1f}) '
                         f'{c.claim_text}{url_part}')
        lines.append('=== END CLAIMS ===')
        return '\n'.join(lines)

    def to_evidence_sources(self) -> List[dict]:
        """List of dicts matching EvidencePackBuilder.append_source() shape."""
        seen = set()
        result = []
        for c in self.claims:
            key = _normalize_url(c.source_url)
            if not key or key in seen:
                continue
            seen.add(key)
            result.append({
                'source_id': c.claim_id,
                'source_type': 'spider',
                'name': c.source_title or c.spider_name or 'unknown',
                'endpoint_or_path': c.source_url,
                'retrieved_at': c.retrieved_at or '',
                'content_hash': None,
                'freshness_hours': c.freshness_hours,
            })
        return result

    def to_evidence_claims(self) -> List[dict]:
        """List of dicts matching EvidencePackBuilder.append_claims() shape."""
        return [
            {
                'claim_id': c.claim_id,
                'claim_text': c.claim_text,
                'claim_type': c.claim_type,
                'confidence': c.confidence,
                'source_ids': [c.claim_id],
                'status': 'uncontested',
            }
            for c in self.claims
        ]
