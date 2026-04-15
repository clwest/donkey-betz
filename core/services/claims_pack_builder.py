"""
Phase 4: Claims Pack Builder

Queries SpiderData (last 72h) and SignalCluster (active, keyword-matched)
to assemble a ClaimsPack for the content deliberation pipeline.

Sources in priority order:
1. SpiderData raw_data['items'] — factual/speculative based on description presence
2. SignalCluster sample_signals — speculative claims from pattern detection

Singleton: get_claims_pack_builder()
"""

import logging
import re
from datetime import timedelta
from typing import List, Optional, Set

from django.utils import timezone

from core.services.content_claims import ClaimsPack, SpiderClaim, make_claim_id

logger = logging.getLogger(__name__)

# Module-level singleton
_builder_instance = None


def get_claims_pack_builder():
    """Singleton accessor."""
    global _builder_instance
    if _builder_instance is None:
        _builder_instance = ClaimsPackBuilder()
    return _builder_instance


def _tokenize_topic(topic: str) -> Set[str]:
    """Split topic into words >3 chars for matching (pattern from spider_intelligence.py)."""
    words = re.findall(r'[a-zA-Z]{4,}', topic.lower())
    return set(words)


def _matches_topic(text: str, tokens: Set[str]) -> bool:
    """Return True if text contains any topic token."""
    if not tokens:
        return True  # no filter
    text_lower = (text or '').lower()
    return any(tok in text_lower for tok in tokens)


class ClaimsPackBuilder:
    """Builds a ClaimsPack from SpiderData and SignalCluster sources."""

    def build(self, topic: str, max_claims: int = 20) -> ClaimsPack:
        """
        Assemble a ClaimsPack for the given topic.

        Args:
            topic: Content topic to gather claims for
            max_claims: Maximum number of claims to include

        Returns:
            ClaimsPack with deduplicated, freshness-sorted claims
        """
        claims: List[SpiderClaim] = []
        seen_urls: Set[str] = set()
        tokens = _tokenize_topic(topic)

        # Source 1: SpiderData (last 72h)
        try:
            claims.extend(self._from_spider_data(tokens, seen_urls))
        except Exception as e:
            logger.warning(f"[Phase 4] SpiderData claim extraction failed: {e}")

        # Source 2: SignalCluster (active, keyword match)
        try:
            claims.extend(self._from_signal_clusters(tokens, seen_urls))
        except Exception as e:
            logger.warning(f"[Phase 4] SignalCluster claim extraction failed: {e}")

        # Source 3: User-uploaded documents (RAG semantic search)
        try:
            claims.extend(self._from_user_documents(topic, seen_urls))
        except Exception as e:
            logger.warning(f"[Phase 4] User document claim extraction failed: {e}")

        # Sort by freshness (newest first) then cap
        claims.sort(key=lambda c: c.retrieved_at or '', reverse=True)
        claims = claims[:max_claims]

        pack = ClaimsPack(
            topic=topic,
            assembled_at=timezone.now().isoformat(),
            claims=claims,
            sources=self._unique_sources(claims),
            stats={
                'total_claims': len(claims),
                'factual': sum(1 for c in claims if c.claim_type == 'factual'),
                'speculative': sum(1 for c in claims if c.claim_type == 'speculative'),
                'analytical': sum(1 for c in claims if c.claim_type == 'analytical'),
                'user_sourced': sum(1 for c in claims if c.spider_name == 'user_document'),
            },
        )
        logger.info(
            f"[Phase 4] ClaimsPack built: {len(claims)} claims for '{topic[:50]}' "
            f"(factual={pack.stats['factual']}, speculative={pack.stats['speculative']})"
        )
        return pack

    def _from_spider_data(
        self, tokens: Set[str], seen_urls: Set[str]
    ) -> List[SpiderClaim]:
        """Extract claims from SpiderData items (last 72h)."""
        from core.models_unified_system import SpiderData

        cutoff = timezone.now() - timedelta(hours=72)
        entries = SpiderData.objects.filter(created_at__gte=cutoff).order_by('-created_at')[:200]

        claims: List[SpiderClaim] = []
        for entry in entries:
            raw_data = entry.raw_data
            if isinstance(raw_data, str):
                try:
                    import json
                    raw_data = json.loads(raw_data)
                except (json.JSONDecodeError, TypeError):
                    continue
            if not isinstance(raw_data, dict):
                continue

            items = raw_data.get('items', [])
            for item in items:
                title = item.get('title') or item.get('name') or ''
                url = item.get('url') or item.get('link') or ''

                if not title or len(title) < 10:
                    continue

                # Topic matching
                desc = item.get('description') or item.get('summary') or item.get('snippet') or ''
                combined = f'{title} {desc}'
                if not _matches_topic(combined, tokens):
                    continue

                # Dedup by normalized URL
                norm_url = (url or '').strip().lower().rstrip('/')
                if norm_url and norm_url in seen_urls:
                    continue
                if norm_url:
                    seen_urls.add(norm_url)

                claim_id = make_claim_id(url, title)

                # Determine claim type and confidence based on description presence
                if desc:
                    claim_text = desc[:300]
                    claim_type = 'factual'
                    confidence = 0.7
                else:
                    claim_text = title
                    claim_type = 'speculative'
                    confidence = 0.3

                freshness_hours = 0.0
                if entry.created_at:
                    delta = timezone.now() - entry.created_at
                    freshness_hours = round(delta.total_seconds() / 3600, 1)

                claims.append(SpiderClaim(
                    claim_id=claim_id,
                    claim_text=claim_text,
                    source_url=url,
                    source_title=title[:100],
                    source_author=item.get('author', ''),
                    published_at=item.get('published') or item.get('date') or '',
                    retrieved_at=entry.created_at.isoformat() if entry.created_at else '',
                    spider_name=entry.spider_name,
                    freshness_hours=freshness_hours,
                    evidence_excerpt=desc[:150] if desc else '',
                    confidence=confidence,
                    claim_type=claim_type,
                ))

        return claims

    def _from_signal_clusters(
        self, tokens: Set[str], seen_urls: Set[str]
    ) -> List[SpiderClaim]:
        """Extract speculative claims from active SignalClusters."""
        from core.models_signal_intelligence import SignalCluster

        clusters = SignalCluster.objects.filter(status='active').order_by('-detected_at')[:50]

        claims: List[SpiderClaim] = []
        for cluster in clusters:
            # Match on cluster keywords
            keywords = cluster.keywords or []
            cluster_text = f'{cluster.name} {" ".join(keywords)}'
            if not _matches_topic(cluster_text, tokens):
                continue

            samples = cluster.sample_signals or []
            for sample in samples:
                text = sample.get('text', '')
                source = sample.get('source', cluster.name)
                if not text or len(text) < 10:
                    continue

                claim_id = make_claim_id(source, text[:100])

                claims.append(SpiderClaim(
                    claim_id=claim_id,
                    claim_text=text[:300],
                    source_url='',
                    source_title=cluster.name,
                    spider_name=source,
                    retrieved_at=cluster.detected_at.isoformat() if cluster.detected_at else '',
                    confidence=0.4,
                    claim_type='speculative',
                ))

        return claims

    def _from_user_documents(
        self, topic: str, seen_urls: Set[str]
    ) -> List[SpiderClaim]:
        """Extract claims from user-uploaded RAG documents via semantic search."""
        from core.services.embedding_service import get_embedding_service

        embedding_service = get_embedding_service()
        try:
            result = embedding_service.create_embedding(
                text=topic[:8000],
                model="text-embedding-3-small",
                agent_name='ClaimsPackBuilder'
            )
            query_vector = result.embedding
        except Exception as e:
            logger.warning(f"[Phase 4] Embedding for user doc search failed: {e}")
            return []

        from content.models import DocumentEmbedding

        try:
            results = DocumentEmbedding.cosine_similarity_search(
                query_vector=query_vector, limit=10, min_similarity=0.4
            )
        except Exception as _e:
            logger.warning(
                "claims_pack_builder._from_user_documents: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return []

        claims: List[SpiderClaim] = []
        for chunk in results:
            doc = chunk.document
            url = doc.source_url or ''
            norm_url = url.strip().lower().rstrip('/')
            if norm_url and norm_url in seen_urls:
                continue
            if norm_url:
                seen_urls.add(norm_url)

            claim_id = make_claim_id(url or str(doc.id), doc.title)

            freshness_hours = 0.0
            if doc.created_at:
                delta = timezone.now() - doc.created_at
                freshness_hours = round(delta.total_seconds() / 3600, 1)

            claims.append(SpiderClaim(
                claim_id=claim_id,
                claim_text=chunk.chunk_text[:300],
                source_url=url,
                source_title=doc.title[:100],
                spider_name='user_document',
                freshness_hours=freshness_hours,
                evidence_excerpt=chunk.chunk_text[:150],
                confidence=0.8,
                claim_type='factual',
            ))

        return claims

    @staticmethod
    def _unique_sources(claims: List[SpiderClaim]) -> List[dict]:
        """Deduplicated source list for metadata."""
        seen: Set[str] = set()
        sources: List[dict] = []
        for c in claims:
            key = c.source_url or c.spider_name
            if key in seen:
                continue
            seen.add(key)
            sources.append({
                'url': c.source_url,
                'title': c.source_title,
                'spider': c.spider_name,
            })
        return sources
