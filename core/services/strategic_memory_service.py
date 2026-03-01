"""
Session 962 Phase 2 + Phase 3.1: Strategic Memory Service

Turns passive memory/logs into an active strategic layer that answers:
- "Have we tried this before?"
- "What tends to fail here?"
- "What strategy has worked historically?"

Queries across: AgentMemory (pgvector), LearningPattern, DecisionRecord,
AgentDecisionSummary, DeliberationSession/Turn/ContractRecord.

Phase 3.1: include_embeddings flag (default off) keeps pgvector off the
critical path. 120s response cache via Django cache (Redis / LocMem).
"""

import copy
import hashlib
import json
import logging
import time
from datetime import timedelta
from typing import Optional

from django.core.cache import cache as django_cache
from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)

CACHE_TTL = 120  # seconds

# Source weights for ranking
SOURCE_WEIGHTS = {
    'agent_memory': 1.00,
    'learning_pattern': 0.85,
    'decision_record': 0.75,
    'decision_summary': 0.75,
    'deliberation_session': 0.65,
    'contract_record': 0.55,
    'conversation': 0.70,
    'deliberation_turn': 0.45,
}


def _recency_bonus(created_at) -> float:
    """Gentle recency multiplier."""
    if not created_at:
        return 0.0
    now = timezone.now()
    age = now - created_at
    if age <= timedelta(days=30):
        return 0.10
    elif age <= timedelta(days=180):
        return 0.05
    return 0.0


def _text_relevance(query_tokens: set, text: str, max_score: float = 1.0) -> float:
    """Simple token overlap relevance score."""
    if not text or not query_tokens:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for t in query_tokens if t in text_lower)
    if not hits:
        return 0.0
    return min(hits / len(query_tokens), 1.0) * max_score


def _tokenize_query(query: str) -> set:
    """Tokenize query into meaningful search terms."""
    stop_words = frozenset({
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'shall', 'can', 'need',
        'what', 'which', 'who', 'whom', 'this', 'that', 'these',
        'those', 'am', 'been', 'being', 'and', 'but', 'or', 'nor',
        'not', 'so', 'very', 'just', 'about', 'above', 'after',
        'before', 'between', 'into', 'through', 'during', 'with',
        'from', 'for', 'of', 'on', 'in', 'to', 'by', 'at', 'it',
        'its', 'we', 'our', 'i', 'my', 'me', 'you', 'your', 'he',
        'she', 'they', 'them', 'how', 'when', 'where', 'why',
        'tried', 'try', 'before',
    })
    tokens = set()
    for word in query.lower().split():
        cleaned = ''.join(c for c in word if c.isalnum())
        if cleaned and len(cleaned) > 2 and cleaned not in stop_words:
            tokens.add(cleaned)
    return tokens


def _cache_key(prefix: str, query: str, top_k: int, include_embeddings: bool, scope: dict = None) -> str:
    """Build a deterministic cache key for strategic memory queries."""
    raw = f"{prefix}:{query}:{top_k}:{include_embeddings}:{json.dumps(scope or {}, sort_keys=True)}"
    return f"smem:{hashlib.sha256(raw.encode()).hexdigest()[:24]}"


class StrategicMemoryService:
    """Unified strategic memory layer across all system data sources."""

    def query_precedents(
        self,
        query: str,
        top_k: int = 10,
        scope: Optional[dict] = None,
        include_embeddings: bool = False,
    ) -> dict:
        """
        Search across all memory sources for relevant precedents.

        Args:
            query: Natural language search query
            top_k: Maximum results to return
            scope: Optional filters (e.g., {'source_types': ['agent_memory']})
            include_embeddings: If True, search AgentMemory via pgvector (slow).
                Default False keeps embeddings off the critical path.

        Returns:
            Unified result payload with ranked results from multiple sources.
        """
        t_start = time.time()
        tokens = _tokenize_query(query)
        results = []
        stats = {'searched': {}, 'timings_ms': {}}
        scope = scope or {}
        allowed_types = scope.get('source_types')

        # Phase 3.1: Check cache
        cache_key = _cache_key('prec', query, top_k, include_embeddings, scope)
        cached = django_cache.get(cache_key)
        if cached is not None:
            result = copy.deepcopy(cached)
            result['stats']['cache_hit'] = True
            return result

        # Build Q filter for icontains text search
        def q_text_filter(field: str) -> Q:
            """Build OR filter matching any token."""
            q = Q()
            for token in tokens:
                q |= Q(**{f'{field}__icontains': token})
            return q

        if not tokens:
            return {
                'query': query, 'top_k': top_k,
                'results': [], 'stats': stats,
            }

        # --- 1) AgentMemory (embedding similarity if available, else text) ---
        # Phase 3.1: Only search when include_embeddings=True
        if include_embeddings and (not allowed_types or 'agent_memory' in allowed_types):
            t0 = time.time()
            try:
                results.extend(self._search_agent_memories(query, tokens, top_k))
                stats['searched']['agent_memory'] = True
            except Exception as e:
                logger.warning(f"[Phase 2] AgentMemory search failed: {e}")
                stats['searched']['agent_memory'] = f'error: {e}'
            stats['timings_ms']['agent_memory'] = round((time.time() - t0) * 1000)
        else:
            stats['searched']['agent_memory'] = False

        # --- 2) LearningPattern ---
        if not allowed_types or 'learning_pattern' in allowed_types:
            t0 = time.time()
            try:
                results.extend(self._search_learning_patterns(tokens, top_k))
                stats['searched']['learning_pattern'] = True
            except Exception as e:
                logger.warning(f"[Phase 2] LearningPattern search failed: {e}")
                stats['searched']['learning_pattern'] = f'error: {e}'
            stats['timings_ms']['learning_pattern'] = round((time.time() - t0) * 1000)

        # --- 3) DecisionRecord ---
        if not allowed_types or 'decision_record' in allowed_types:
            t0 = time.time()
            try:
                results.extend(self._search_decision_records(tokens, top_k))
                stats['searched']['decision_record'] = True
            except Exception as e:
                logger.warning(f"[Phase 2] DecisionRecord search failed: {e}")
                stats['searched']['decision_record'] = f'error: {e}'
            stats['timings_ms']['decision_record'] = round((time.time() - t0) * 1000)

        # --- 4) AgentDecisionSummary ---
        if not allowed_types or 'decision_summary' in allowed_types:
            t0 = time.time()
            try:
                results.extend(self._search_decision_summaries(tokens, top_k))
                stats['searched']['decision_summary'] = True
            except Exception as e:
                logger.warning(f"[Phase 2] AgentDecisionSummary search failed: {e}")
                stats['searched']['decision_summary'] = f'error: {e}'
            stats['timings_ms']['decision_summary'] = round((time.time() - t0) * 1000)

        # --- 5) DeliberationSession ---
        if not allowed_types or 'deliberation_session' in allowed_types:
            t0 = time.time()
            try:
                results.extend(self._search_deliberation_sessions(tokens, top_k))
                stats['searched']['deliberation_session'] = True
            except Exception as e:
                logger.warning(f"[Phase 2] DeliberationSession search failed: {e}")
                stats['searched']['deliberation_session'] = f'error: {e}'
            stats['timings_ms']['deliberation_session'] = round((time.time() - t0) * 1000)

        # --- 6) DeliberationTurn (capped) ---
        if not allowed_types or 'deliberation_turn' in allowed_types:
            t0 = time.time()
            try:
                results.extend(self._search_deliberation_turns(tokens, min(top_k, 5)))
                stats['searched']['deliberation_turn'] = True
            except Exception as e:
                logger.warning(f"[Phase 2] DeliberationTurn search failed: {e}")
                stats['searched']['deliberation_turn'] = f'error: {e}'
            stats['timings_ms']['deliberation_turn'] = round((time.time() - t0) * 1000)

        # --- 7) ContractRecord ---
        if not allowed_types or 'contract_record' in allowed_types:
            t0 = time.time()
            try:
                results.extend(self._search_contract_records(tokens, top_k))
                stats['searched']['contract_record'] = True
            except Exception as e:
                logger.warning(f"[Phase 2] ContractRecord search failed: {e}")
                stats['searched']['contract_record'] = f'error: {e}'
            stats['timings_ms']['contract_record'] = round((time.time() - t0) * 1000)

        # --- 8) Recent PA Conversations ---
        if not allowed_types or 'conversation' in allowed_types:
            t0 = time.time()
            try:
                from core.models import ChatConversation
                convos = ChatConversation.objects.filter(
                    Q(user_message__icontains=query) | Q(assistant_response__icontains=query)
                ).order_by('-created_at')[:5]
                for c in convos:
                    text = f"{c.user_message[:200]} → {c.assistant_response[:200]}"
                    score = (
                        _text_relevance(tokens, text) * 0.6
                        + _recency_bonus(c.created_at) * 0.4
                    )
                    if score > 0.1:
                        results.append({
                            'source': 'conversation',
                            'text': text,
                            'score': score * SOURCE_WEIGHTS['conversation'],
                            'created_at': c.created_at,
                            'metadata': {'conversation_id': c.conversation_id},
                        })
                stats['searched']['conversation'] = True
            except Exception as e:
                logger.warning(f"[MEMORY] Conversation search failed: {e}")
                stats['searched']['conversation'] = f'error: {e}'
            stats['timings_ms']['conversation'] = round((time.time() - t0) * 1000)

        # Sort by final_score descending
        results.sort(key=lambda r: r['score'], reverse=True)
        results = results[:top_k]

        stats['timings_ms']['total'] = round((time.time() - t_start) * 1000)
        stats['result_count'] = len(results)
        stats['cache_hit'] = False

        result = {
            'query': query,
            'top_k': top_k,
            'results': results,
            'stats': stats,
        }
        django_cache.set(cache_key, result, CACHE_TTL)
        return result

    def get_failure_signatures(
        self,
        domain: Optional[str] = None,
        top_k: int = 10,
    ) -> dict:
        """
        Aggregate failure patterns from LearningPattern into signatures.

        Groups by pattern_type, computes failure rates and common issues.
        """
        from core.models_unified_system import LearningPattern

        t_start = time.time()

        qs = LearningPattern.objects.filter(is_active=True)

        # Filter failure-related patterns
        failure_types = [
            'tool_failure', 'quality_regression', 'hallucination',
            'error_pattern', 'failure', 'bug', 'regression',
        ]
        type_q = Q()
        for ft in failure_types:
            type_q |= Q(pattern_type__icontains=ft)

        # Also check description for failure indicators
        desc_q = Q(description__icontains='fail') | Q(description__icontains='error') | Q(description__icontains='broken')
        qs = qs.filter(type_q | desc_q)

        if domain:
            qs = qs.filter(
                Q(pattern_type__icontains=domain) |
                Q(description__icontains=domain)
            )

        patterns = list(qs.order_by('-updated_at')[:100])

        # Group by pattern_type
        groups = {}
        for p in patterns:
            key = p.pattern_type or 'unknown'
            if key not in groups:
                groups[key] = {
                    'pattern_type': key,
                    'count': 0,
                    'total_applied': 0,
                    'total_success': 0,
                    'descriptions': [],
                    'last_seen_at': None,
                }
            g = groups[key]
            g['count'] += 1
            g['total_applied'] += p.times_applied
            g['total_success'] += p.success_when_applied
            g['descriptions'].append(p.description[:200])
            if p.updated_at and (not g['last_seen_at'] or p.updated_at > g['last_seen_at']):
                g['last_seen_at'] = p.updated_at

        # Build ranked signatures
        signatures = []
        for key, g in groups.items():
            failure_rate = None
            if g['total_applied'] > 0:
                failure_rate = round(1.0 - (g['total_success'] / g['total_applied']), 2)

            signatures.append({
                'pattern_type': g['pattern_type'],
                'count': g['count'],
                'failure_rate': failure_rate,
                'last_seen_at': g['last_seen_at'].isoformat() if g['last_seen_at'] else None,
                'common_issues': g['descriptions'][:3],
            })

        signatures.sort(key=lambda s: s['count'], reverse=True)
        signatures = signatures[:top_k]

        return {
            'domain': domain,
            'top_k': top_k,
            'signatures': signatures,
            'total_patterns_scanned': len(patterns),
            'timings_ms': round((time.time() - t_start) * 1000),
        }

    def recommend_strategy(
        self,
        objective: str,
        top_k: int = 5,
        include_embeddings: bool = False,
    ) -> dict:
        """
        Recommend strategy for an objective based on historical data.

        Returns common blockers, success patterns, and do/don't guidance.
        """
        # Phase 3.1: Check cache
        cache_key = _cache_key('strat', objective, top_k, include_embeddings)
        cached = django_cache.get(cache_key)
        if cached is not None:
            result = copy.deepcopy(cached)
            result['stats']['cache_hit'] = True
            return result

        t_start = time.time()
        tokens = _tokenize_query(objective)

        # Search precedents focused on decisions and deliberations
        precedents = self.query_precedents(
            objective, top_k=15,
            scope={'source_types': [
                'decision_record', 'decision_summary',
                'deliberation_session', 'learning_pattern',
            ]},
            include_embeddings=include_embeddings,
        )

        # Separate success vs failure patterns
        from core.models_unified_system import LearningPattern
        success_patterns = []
        avoid_patterns = []

        # Get success patterns
        success_q = Q()
        for token in tokens:
            success_q |= Q(description__icontains=token)

        successes = LearningPattern.objects.filter(
            success_q, is_active=True, times_applied__gt=0,
        ).order_by('-confidence')[:20]

        for p in successes:
            rate = p.success_when_applied / p.times_applied if p.times_applied > 0 else 0
            entry = {
                'description': p.description[:200],
                'confidence': round(p.confidence, 2),
                'success_rate': round(rate, 2),
                'times_applied': p.times_applied,
            }
            if rate >= 0.6:
                success_patterns.append(entry)
            elif rate < 0.4 and p.times_applied >= 2:
                avoid_patterns.append(entry)

        success_patterns.sort(key=lambda x: x['success_rate'], reverse=True)
        avoid_patterns.sort(key=lambda x: x['success_rate'])

        # Build do/don't bullets
        do_bullets = []
        for sp in success_patterns[:top_k]:
            do_bullets.append(f"{sp['description']} (success rate: {sp['success_rate']:.0%})")

        dont_bullets = []
        for ap in avoid_patterns[:top_k]:
            dont_bullets.append(f"{ap['description']} (success rate: {ap['success_rate']:.0%})")

        result = {
            'objective': objective,
            'top_k': top_k,
            'precedents': precedents['results'][:top_k],
            'success_patterns': success_patterns[:top_k],
            'avoid_patterns': avoid_patterns[:top_k],
            'recommendations': {
                'do': do_bullets[:top_k],
                'dont': dont_bullets[:top_k],
            },
            'stats': {
                'precedents_found': len(precedents['results']),
                'success_patterns_found': len(success_patterns),
                'avoid_patterns_found': len(avoid_patterns),
                'timings_ms': round((time.time() - t_start) * 1000),
                'cache_hit': False,
            },
        }
        django_cache.set(cache_key, result, CACHE_TTL)
        return result

    # ------------------------------------------------------------------
    # Private search methods for each source
    # ------------------------------------------------------------------

    def _search_agent_memories(self, query: str, tokens: set, top_k: int) -> list:
        """Search AgentMemory via embedding similarity (preferred) or text fallback."""
        from core.models_unified_system import AgentMemory

        results = []

        # Try embedding search first
        try:
            from core.services.memory_embedding_service import get_memory_embedding_service
            svc = get_memory_embedding_service()
            query_embedding = svc._generate_embedding(query)

            if query_embedding:
                memories = list(AgentMemory.objects.filter(
                    embedding__isnull=False,
                    safety_class__in=['approved', 'candidate'],
                ).only(
                    'id', 'title', 'content', 'memory_type',
                    'importance_score', 'created_at', 'source_id',
                    'embedding',
                )[:200])

                for mem in memories:
                    similarity = svc._cosine_similarity(query_embedding, mem.embedding)
                    if similarity < 0.2:
                        continue
                    weight = SOURCE_WEIGHTS['agent_memory']
                    recency = _recency_bonus(mem.created_at)
                    final_score = round(similarity * weight + recency, 4)

                    results.append({
                        'source_type': 'agent_memory',
                        'id': str(mem.id),
                        'title': mem.title,
                        'summary': (mem.content or '')[:300],
                        'created_at': mem.created_at.isoformat() if mem.created_at else None,
                        'trace_id': mem.source_id or '',
                        'score': final_score,
                        'metadata': {'memory_type': mem.memory_type, 'importance': mem.importance_score},
                        'ref': f'AgentMemory:{mem.id}',
                        'links': {},
                    })

                results.sort(key=lambda r: r['score'], reverse=True)
                return results[:top_k]
        except Exception as e:
            logger.info(f"[Phase 2] Embedding search unavailable, falling back to text: {e}")

        # Text fallback
        text_q = Q()
        for token in tokens:
            text_q |= Q(title__icontains=token) | Q(content__icontains=token)

        memories = AgentMemory.objects.filter(text_q).order_by(
            '-importance_score', '-created_at',
        )[:top_k]

        for mem in memories:
            relevance = _text_relevance(tokens, f"{mem.title} {mem.content}")
            weight = SOURCE_WEIGHTS['agent_memory']
            recency = _recency_bonus(mem.created_at)
            final_score = round(relevance * weight + recency, 4)

            results.append({
                'source_type': 'agent_memory',
                'id': str(mem.id),
                'title': mem.title,
                'summary': (mem.content or '')[:300],
                'created_at': mem.created_at.isoformat() if mem.created_at else None,
                'trace_id': mem.source_id or '',
                'score': final_score,
                'metadata': {'memory_type': mem.memory_type, 'importance': mem.importance_score},
                'ref': f'AgentMemory:{mem.id}',
                'links': {},
            })

        return results[:top_k]

    def _search_learning_patterns(self, tokens: set, top_k: int) -> list:
        """Search LearningPattern via text search on description."""
        from core.models_unified_system import LearningPattern

        # Cap to 8 longest tokens to limit OR clause explosion
        capped = sorted(tokens, key=len, reverse=True)[:8]

        text_q = Q()
        for token in capped:
            text_q |= Q(description__icontains=token) | Q(pattern_type__icontains=token)

        patterns = LearningPattern.objects.filter(
            text_q, is_active=True,
        ).order_by('-confidence', '-created_at')[:top_k]

        results = []
        for p in patterns:
            relevance = _text_relevance(tokens, f"{p.pattern_type} {p.description}")
            weight = SOURCE_WEIGHTS['learning_pattern']
            recency = _recency_bonus(p.created_at)
            final_score = round(relevance * weight + recency, 4)

            results.append({
                'source_type': 'learning_pattern',
                'id': str(p.id),
                'title': p.pattern_type,
                'summary': (p.description or '')[:300],
                'created_at': p.created_at.isoformat() if p.created_at else None,
                'trace_id': '',
                'score': final_score,
                'metadata': {
                    'confidence': p.confidence,
                    'times_applied': p.times_applied,
                    'success_when_applied': p.success_when_applied,
                },
                'ref': f'LearningPattern:{p.id}',
                'links': {},
            })

        return results

    def _search_decision_records(self, tokens: set, top_k: int) -> list:
        """Search DecisionRecord via text on reasoning/action."""
        from core.models_decision_records import DecisionRecord

        text_q = Q()
        for token in tokens:
            text_q |= Q(reasoning__icontains=token) | Q(action__icontains=token) | Q(task_summary__icontains=token)

        records = DecisionRecord.objects.filter(text_q).order_by('-created_at')[:top_k]

        results = []
        for r in records:
            relevance = _text_relevance(tokens, f"{r.action} {r.reasoning} {r.task_summary}")
            weight = SOURCE_WEIGHTS['decision_record']
            recency = _recency_bonus(r.created_at)
            final_score = round(relevance * weight + recency, 4)

            results.append({
                'source_type': 'decision_record',
                'id': str(r.id),
                'title': f"{r.agent_name}: {r.decision_type}",
                'summary': (r.reasoning or r.action or '')[:300],
                'created_at': r.created_at.isoformat() if r.created_at else None,
                'trace_id': str(r.trace_id) if r.trace_id else '',
                'score': final_score,
                'metadata': {
                    'agent_name': r.agent_name,
                    'decision_type': r.decision_type,
                    'confidence': r.confidence,
                    'was_successful': r.was_successful,
                },
                'ref': f'DecisionRecord:{r.id}',
                'links': {},
            })

        return results

    def _search_decision_summaries(self, tokens: set, top_k: int) -> list:
        """Search AgentDecisionSummary via text on topic/recommended_stance/rationale."""
        from core.models_unified_system import AgentDecisionSummary

        text_q = Q()
        for token in tokens:
            text_q |= (
                Q(topic__icontains=token) |
                Q(recommended_stance__icontains=token) |
                Q(rationale__icontains=token)
            )

        summaries = AgentDecisionSummary.objects.filter(text_q).order_by('-created_at')[:top_k]

        results = []
        for s in summaries:
            relevance = _text_relevance(tokens, f"{s.topic} {s.recommended_stance} {s.rationale}")
            weight = SOURCE_WEIGHTS['decision_summary']
            recency = _recency_bonus(s.created_at)
            final_score = round(relevance * weight + recency, 4)

            results.append({
                'source_type': 'decision_summary',
                'id': str(s.id),
                'title': s.topic,
                'summary': (s.recommended_stance or '')[:300],
                'created_at': s.created_at.isoformat() if s.created_at else None,
                'trace_id': str(s.trace_id) if s.trace_id else '',
                'score': final_score,
                'metadata': {
                    'decision_type': s.decision_type,
                    'impact_area': s.impact_area,
                    'status': s.status,
                    'is_canonical': s.is_canonical,
                },
                'ref': f'AgentDecisionSummary:{s.id}',
                'links': {},
            })

        return results

    def _search_deliberation_sessions(self, tokens: set, top_k: int) -> list:
        """Search DeliberationSession via text on objective."""
        from core.models_deliberation import DeliberationSession

        text_q = Q()
        for token in tokens:
            text_q |= Q(objective__icontains=token)

        sessions = DeliberationSession.objects.filter(text_q).order_by('-created_at')[:top_k]

        results = []
        for s in sessions:
            relevance = _text_relevance(tokens, s.objective or '')
            weight = SOURCE_WEIGHTS['deliberation_session']
            recency = _recency_bonus(s.created_at)
            final_score = round(relevance * weight + recency, 4)

            results.append({
                'source_type': 'deliberation_session',
                'id': str(s.id),
                'title': f"Deliberation: {(s.objective or '')[:80]}",
                'summary': (s.objective or '')[:300],
                'created_at': s.created_at.isoformat() if s.created_at else None,
                'trace_id': s.trace_id or '',
                'score': final_score,
                'metadata': {
                    'session_type': s.session_type,
                    'status': s.status,
                    'participant_count': len(s.participants) if s.participants else 0,
                },
                'ref': f'DeliberationSession:{s.id}',
                'links': {
                    'detail': f'/api/deliberation/sessions/{s.id}/',
                },
            })

        return results

    def _search_deliberation_turns(self, tokens: set, top_k: int) -> list:
        """Search DeliberationTurn via text on content (capped)."""
        from core.models_deliberation import DeliberationTurn

        text_q = Q()
        for token in tokens:
            text_q |= Q(content__icontains=token)

        turns = DeliberationTurn.objects.filter(text_q).select_related(
            'session',
        ).order_by('-created_at')[:top_k]

        results = []
        for t in turns:
            relevance = _text_relevance(tokens, (t.content or '')[:1000])
            weight = SOURCE_WEIGHTS['deliberation_turn']
            recency = _recency_bonus(t.created_at)
            final_score = round(relevance * weight + recency, 4)

            results.append({
                'source_type': 'deliberation_turn',
                'id': t.id,
                'title': f"Turn {t.turn_number}: {t.agent_name}",
                'summary': (t.content or '')[:300],
                'created_at': t.created_at.isoformat() if t.created_at else None,
                'trace_id': t.trace_id or '',
                'score': final_score,
                'metadata': {
                    'agent_name': t.agent_name,
                    'role': t.role,
                    'turn_number': t.turn_number,
                    'session_id': str(t.session_id),
                },
                'ref': f'DeliberationTurn:{t.id}',
                'links': {
                    'session': f'/api/deliberation/sessions/{t.session_id}/',
                },
            })

        return results

    def _search_contract_records(self, tokens: set, top_k: int) -> list:
        """Search ContractRecord via Python-side filtering on contract_data JSON."""
        from core.models_deliberation import ContractRecord

        # JSONField doesn't support icontains — fetch recent and filter in Python
        recent_contracts = ContractRecord.objects.order_by('-created_at')[:100]
        contracts = []
        for c in recent_contracts:
            data_str = str(c.contract_data or {}).lower()
            if any(token in data_str for token in tokens):
                contracts.append(c)
                if len(contracts) >= top_k:
                    break

        results = []
        for c in contracts:
            data_str = str(c.contract_data or {})
            relevance = _text_relevance(tokens, data_str[:1000])
            weight = SOURCE_WEIGHTS['contract_record']
            recency = _recency_bonus(c.created_at)
            final_score = round(relevance * weight + recency, 4)

            # Extract a summary from contract_data
            summary = ''
            if isinstance(c.contract_data, dict):
                summary = c.contract_data.get('chosen_path', '') or c.contract_data.get('question', '') or str(c.contract_data)[:200]

            results.append({
                'source_type': 'contract_record',
                'id': c.id,
                'title': f"Contract: {c.contract_type}",
                'summary': str(summary)[:300],
                'created_at': c.created_at.isoformat() if c.created_at else None,
                'trace_id': c.trace_id or '',
                'score': final_score,
                'metadata': {
                    'contract_type': c.contract_type,
                    'session_id': str(c.session_id),
                },
                'ref': f'ContractRecord:{c.id}',
                'links': {
                    'session': f'/api/deliberation/sessions/{c.session_id}/',
                },
            })

        return results

    def format_for_pa(self, query: str, top_k: int = 7) -> str:
        """
        Format strategic memory results for PA enrichment injection.
        Compact format with token budget control.
        """
        precedents = self.query_precedents(query, top_k=top_k, include_embeddings=False)
        failures = self.get_failure_signatures(top_k=3)

        parts = []

        # Top precedents
        if precedents['results']:
            parts.append("Precedents:")
            for r in precedents['results'][:3]:
                parts.append(
                    f"- [{r['source_type']}] {r['title'][:80]}: "
                    f"{r['summary'][:120]}"
                )

        # Failure signatures
        if failures['signatures']:
            parts.append("\nFailure Patterns:")
            for sig in failures['signatures'][:3]:
                rate_str = f" (fail rate: {sig['failure_rate']:.0%})" if sig['failure_rate'] is not None else ""
                parts.append(f"- {sig['pattern_type']}{rate_str}: {sig['common_issues'][0][:100] if sig['common_issues'] else 'N/A'}")

        if not parts:
            return f"No precedents found for: {query[:80]}\nStats: {precedents['stats']}"

        return '\n'.join(parts)


# Singleton
_service_instance = None


def get_strategic_memory_service() -> StrategicMemoryService:
    """Get the global StrategicMemoryService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = StrategicMemoryService()
    return _service_instance
