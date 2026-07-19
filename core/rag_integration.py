"""
RAG (Retrieval-Augmented Generation) Integration
Connects to unified_embeddings table for context retrieval
"""

import logging
import os
import re
import psycopg2
from typing import List, Dict, Any, Optional

# Import the migrated encryption service
from core.encryption_service import get_encryption_service

logger = logging.getLogger(__name__)

def create_embedding(text: str, model: str = "text-embedding-3-small") -> Optional[List[float]]:
    """Create embedding for a text using the centralized EmbeddingService (with Redis cache)."""
    try:
        from core.services.embedding_service import get_embedding_service
        service = get_embedding_service()
        result = service.create_embedding(text, model=model, agent_name='rag_integration', log_usage=True)
        return result.embedding
    except Exception as e:
        logger.error(f"Failed to create embedding: {e}")
        return None

# Cycle 1A KFI-3 (ADR-0130) — authority weights for opt-in ranking.
# workspace_canonical (2.0) > repo_canonical (1.5) > derived (1.0) per ADR §2.1.
# retrieval_boost is orthogonal per 0120 and NOT composed into weighted_score.
_AUTHORITY_WEIGHTS = {
    'workspace_canonical': 2.0,
    'repo_canonical': 1.5,
    'derived': 1.0,
}


# Session 2728 F-RG-1 — Batch B tool 1 close: narrow-except allowlist for
# `search_embeddings`. Extends the S1234 D17-D21 discipline (already applied
# to `search_personal_memories` at line ~441-445 as
# `_PERSONAL_MEMORY_ENV_ERRORS`) to the sibling document-search path so
# environmental errors return `[]` with an error log, but logic errors
# propagate to callers instead of silently degrading to zero-results
# (indistinguishable from "no relevant content"). Same tuple shape as the
# D20 invariant (`test_d20_views_rag_embeddings_narrow_except.py::
# test_all_four_allowlists_have_same_shape` — this becomes the fifth
# allowlist under the D17-D21 pattern). Chris ratified at Batch B tool 1
# close (S2728 handoff).
_RAG_EMBEDDINGS_ENV_ERRORS = (
    __import__('django.db.utils', fromlist=['DatabaseError']).DatabaseError,
    ConnectionError,
    OSError,
)


def _get_authority_weight(authority):
    """Return the authority-tier weight in [1.0, 2.0]; unknown → 1.0."""
    return _AUTHORITY_WEIGHTS.get(authority or '', 1.0)


# S2826 Pattern B — intent-gated file-specific ranking bonus for the
# embedding lane. Chris D-verdict 2026-07-19 (S2826 D1) after S2825
# harvest showed 0/16 retrieval-strict-hit despite the S2818 authority-
# boost pilot being live in the BM25 lane. Step 1a confirmed metadata
# is correct FOR THE TARGET ROWS; Step 1b confirmed the tier-based
# authority_weighted flag is a no-op when target and competitor share
# the same repo_canonical tier. Step 1c decomposed the failure into two
# patterns; Pattern B is "small-gap ranking" (canonical is in the
# candidate pool but loses to same-tier competitors by a ~0.025
# similarity margin). D1 mandates a NARROW intent gate + small bounded
# file-specific bonus, distinct from the coarse tier weighting.
# Sibling of core/rag.py `_COUNT_INTENT_PATTERNS` (BM25 lane substring
# match). Rigby SIGN 2026-07-19 Q1: near-parity with BM25 phrase set;
# intentional divergence on `total` (narrower regex `total\s+\w+` here
# vs bare `total` in BM25) to avoid false positives on words like
# "totally"/"totalitarian" — accepted as design decision, not
# oversight. Do NOT collapse with the SELF_REFERENCE / INDEX_DISCOVERY
# / IDENTITY / doc-class-precedence policy classes per D5 — each keeps
# its own gate + mechanism.
_COUNT_INTENT_PATTERNS = (
    re.compile(r'\bhow\s+many\b', re.I),
    re.compile(r'\bhow\s+much\b', re.I),  # Rigby Q1 parity refinement
    re.compile(r'\bnumber\s+of\b', re.I),
    re.compile(r'\bcount\s+of\b', re.I),
    re.compile(r'\blist\s+all\b', re.I),
    re.compile(r'\btotal\s+(?:number\s+of\s+)?\w+', re.I),
)

# File-specific similarity bonus applied only when the COUNT intent
# gate fires. Value bounded to observed S2825 gaps: Q23 (chunk #28
# celery-tasks) lost by 0.025 to RUNTIME_AUDIT #3; Q21 (chunk #15
# spiders) lost by ~0.026 to PLATFORM_ARCHITECTURE_MAP. +0.05 flips
# both without dominating unrelated retrieval. Do not raise without
# evidence. Do not add other files here without confirming a distinct
# small-gap ranking pattern via Step-1c-shape diagnostic.
_COUNT_INTENT_BONUS = {
    'docs/PLATFORM_INVENTORY.md': 0.05,
}


def _detect_count_intent(query: str) -> bool:
    """Narrow COUNT / sole-authoritative-source intent gate (Pattern B)."""
    if not query:
        return False
    return any(p.search(query) for p in _COUNT_INTENT_PATTERNS)


def search_embeddings(
    query: str,
    limit: int = 5,
    content_types: Optional[List[str]] = None,
    # Session 1234 D15 — lowered default 0.7 → 0.4. Pre-D15 the
    # value was 0.7 in the signature but get_rag_context called with
    # similarity_threshold=0.6 anyway (line 167). With the corpus
    # now backed by text-embedding-3-small (D12 pivot), similarities
    # cluster in the 0.4-0.7 band for related content; 0.7 cut off
    # essentially all real signal. 0.4 keeps obvious noise out while
    # still surfacing the corpus.
    similarity_threshold: float = 0.4,
    namespace: Optional[str] = 'system',
    exclude_personal: bool = True,
    # Session 1234 D12 — D9/D10 filter pushdown
    category: Optional[str] = None,
    document_class: Optional[str] = None,
    is_pinned: Optional[bool] = None,
    min_session: Optional[int] = None,
    include_superseded: bool = False,
    # Cycle 1A KFI-3 (ADR-0130) — authority-aware retrieval.
    canonical_authority: Optional[str] = None,
    authority_weighted: bool = False,
) -> List[Dict[str, Any]]:
    """
    Session 1234 D12 — semantic search over Document corpus via pgvector.

    Pre-D12 this function targeted a `unified_embeddings` table that
    doesn't exist (the real Django table is `persistence_unifiedembedding`,
    which was empty even on local DB). Callers silently degraded to
    "no context" because the SQL failed every time.

    D12 pivots to the populated path: pgvector cosine similarity over
    `DocumentEmbedding` (the table the D9 sync + D10 backfill populated,
    ~16k+ rows post-backfill), joined to `Document` for the D9/D10
    type-aware filter pushdown (category / document_class / is_pinned /
    min_session) and default-exclude-superseded ranking.

    Backward-compat: the original signature kwargs (limit / content_types
    / similarity_threshold / namespace / exclude_personal) remain in
    place. `content_types` is treated as a soft hint mapped to
    `document_class` if not explicitly provided.

    Args:
        query: The search query (text → embedding via OpenAI).
        limit: Max results.
        content_types: Optional list of content types — back-compat hint.
            If `document_class` is also unset, the first entry is used
            as the document_class filter.
        similarity_threshold: Minimum cosine similarity (0-1).
        namespace: (legacy) — informational, not currently filtered.
        exclude_personal: (legacy) — Document table has no personal
            namespace; ignored. Kept for signature stability.
        category, document_class, is_pinned, min_session,
            include_superseded: Session 1234 D9/D10 filter pushdown.
            Same semantics as kb_tool action=documents (#2620).

    Returns:
        List of dicts shaped to the legacy contract:
        ``{id, content, content_type, metadata, importance_score,
        similarity_score}``. The retrieval_boost from D9/D10 maps to
        importance_score so downstream ranking still respects it.
    """
    # Create embedding for the query
    query_embedding = create_embedding(query)
    if not query_embedding:
        logger.error("Failed to create query embedding")
        return []

    try:
        from content.models import Document, DocumentEmbedding, ContentStatus

        # Back-compat: if content_types is given and document_class isn't,
        # use the first content_type as a document_class hint. Avoids
        # breaking callers that passed e.g. ['document_chunk'] from the
        # legacy unified_embeddings era.
        effective_class = document_class
        if effective_class is None and content_types:
            first = content_types[0] if isinstance(content_types, (list, tuple)) and content_types else None
            if first and isinstance(first, str):
                effective_class = first

        # Session 1234 D16 — build the cosine-similarity queryset
        # INLINE (not via the classmethod) so D9/D10 filter pushdown
        # can run BEFORE the slice. The DocumentEmbedding.
        # cosine_similarity_search classmethod returns `qs[:limit]`,
        # which is a sliced queryset — Django raises
        # `Cannot filter a query once a slice has been taken` on any
        # subsequent `.filter()` or `.exclude()`. Pre-D16 the surrounding
        # try/except swallowed that exception and returned [] for every
        # call, which is why D11/D12/D13/D14/D15 all looked correct in
        # tests (mocked QS) but returned 0 chunks in production.
        #
        # Mirror the classmethod's orphan-chunk exclusion + cosine
        # threshold so retrieval still excludes parentless chunks
        # ("Agent Activity Knowledge Base" entries that pollute results).
        #
        # Cycle 1A KFI-3 (ADR-0130, Chris F1 Option B 2026-07-08):
        # workspace-mirror Documents (KFI-1) legitimately have empty
        # file_path — they originate from workspace Deliverables, not
        # from filesystem paths. The default orphan filter would exclude
        # them collaterally. Under Option B, default retrieval MUST
        # remain unchanged; workspace mirrors are reachable ONLY when
        # the caller explicitly requests them via
        # ``canonical_authority='workspace_canonical'``. The narrow
        # branch below substitutes ``source='workspace'`` as the
        # anti-pollution invariant for the explicit-opt-in path,
        # preserving the intent of the orphan exclusion while making
        # the workspace-canonical filter functional.
        from pgvector.django import CosineDistance
        qs = DocumentEmbedding.objects
        if canonical_authority == 'workspace_canonical':
            qs = qs.filter(document__source='workspace')
        else:
            qs = (
                qs
                .filter(document__file_path__isnull=False)
                .exclude(document__file_path='')
            )
        qs = (
            qs
            .annotate(distance=CosineDistance('embedding_vector', query_embedding))
            .filter(distance__lt=(1 - similarity_threshold))
        )

        # D9/D10 filter pushdown via Document join — now all run BEFORE
        # the slice so no `Cannot filter a sliced queryset` blowup.
        if category:
            qs = qs.filter(document__category=category)
        if effective_class:
            qs = qs.filter(document__document_class=effective_class)
        if is_pinned is True:
            # Truthy-only — feedback_llm_autofills_boolean_params_with_false.
            qs = qs.filter(document__is_pinned=True)
        if not include_superseded:
            qs = qs.exclude(document__status=ContentStatus.ARCHIVED)
        # Cycle 1A KFI-3 (ADR-0130 §2.1): canonical_authority filter.
        # Belt-and-suspenders alongside the source='workspace' branch
        # above — narrows repo_canonical / derived requests and adds
        # defense for the hypothetical case of a source='workspace'
        # row that failed to receive canonical_authority='workspace_canonical'.
        if canonical_authority:
            qs = qs.filter(document__canonical_authority=canonical_authority)
        # Session 1234 D14 — positive-only min_session guard.
        # LLM autofills integer params with 0 the same way it autofills
        # booleans with False; treat anything <= 0 as "no filter" so
        # the corpus isn't silently narrowed to handoff-only.
        if min_session is not None:
            try:
                threshold = int(min_session)
                if threshold > 0:
                    # Filter docs whose tags include any session-N >= threshold.
                    # JSONField tag filtering goes through a Python-side pass
                    # because semantics need int parsing of 'session-N' tags.
                    ok_doc_ids = set()
                    for d in Document.objects.filter(
                        id__in=qs.values_list('document_id', flat=True).distinct(),
                    ).only('id', 'tags'):
                        for t in (d.tags or []):
                            if isinstance(t, str) and t.startswith('session-'):
                                try:
                                    if int(t.split('-', 1)[1]) >= threshold:
                                        ok_doc_ids.add(d.id)
                                        break
                                except (ValueError, IndexError):
                                    continue
                    qs = qs.filter(document_id__in=ok_doc_ids)
            except (ValueError, TypeError):
                pass

        # Take final K after filtering.
        #
        # Default (authority_weighted=False): sort by cosine distance
        # ascending = closest match first. Unchanged from HEAD.
        #
        # Cycle 1A KFI-3 (ADR-0130 §2.1): when authority_weighted=True,
        # rank by weighted_score DESC, tie-break by
        # Coalesce(document.updated_at, document.created_at) DESC,
        # final by document.id ASC. The weighted score is computed
        # after retrieval (per-row) rather than pushed into the SQL
        # ORDER BY because CosineDistance annotations complicate ORM
        # arithmetic; the ranking is applied to the retrieved candidate
        # pool. To keep the candidate pool honest, we still ORDER BY
        # distance ASC in SQL and take a candidate window of `limit *
        # 3` (bounded oversample), then apply weighted ordering in
        # Python and truncate to `limit`. The oversample is a
        # bounded implementation detail; downstream consumers see
        # exactly `limit` rows.
        # S2826 Pattern B — narrow COUNT intent gate fires oversample too,
        # since the canonical target may sit at rank #2-#5 by raw distance
        # and the bonus needs a deep enough pool to promote it.
        count_intent_active = _detect_count_intent(query)
        if authority_weighted or count_intent_active:
            candidate_qs = qs.order_by('distance')[:max(limit * 3, limit)]
            chunks = list(candidate_qs.select_related('document'))
        else:
            qs = qs.order_by('distance')[:limit]
            chunks = list(qs.select_related('document'))

        documents = []
        encryption_service = get_encryption_service()

        for chunk in chunks:
            doc = chunk.document
            # Decrypt content if encrypted; chunk_text usually plaintext.
            try:
                content = encryption_service.decrypt(chunk.chunk_text) if chunk.chunk_text else ''
            except Exception:
                content = chunk.chunk_text or ''

            # Cosine similarity = 1 - distance (annotation set by the
            # classmethod). Guard against NaN/inf.
            import math
            distance = getattr(chunk, 'distance', None)
            if distance is None:
                similarity = 0.0
            else:
                similarity = float(1 - distance)
                if math.isnan(similarity) or math.isinf(similarity):
                    similarity = 0.0

            # S2826 Pattern B — compute per-row COUNT bonus INSIDE the
            # loop so it composes naturally into both raw similarity
            # ordering (default path) and weighted_score (when
            # authority_weighted=True). Bonus is 0.0 when the intent
            # gate did not fire or the file is not in the bonus map.
            if count_intent_active:
                count_intent_bonus = _COUNT_INTENT_BONUS.get(doc.file_path or '', 0.0)
            else:
                count_intent_bonus = 0.0
            effective_similarity = similarity + count_intent_bonus

            # Cycle 1A KFI-3 (ADR-0130 §2.1): compute weighted_score when
            # authority_weighted=True. retrieval_boost remains
            # orthogonal per 0120 — NOT composed into weighted_score.
            if authority_weighted:
                authority_weight = _get_authority_weight(doc.canonical_authority)
                weighted_score = effective_similarity * authority_weight
            else:
                authority_weight = None
                weighted_score = None
            documents.append({
                'id': str(chunk.id),
                'content': content[:1000],
                'content_type': doc.document_class or 'document',
                'metadata': {
                    'file_path': doc.file_path,
                    'title': doc.title,
                    'category': doc.category,
                    'document_class': doc.document_class,
                    'is_pinned': doc.is_pinned,
                    'tags': list(doc.tags or []),
                    'chunk_index': chunk.chunk_index,
                    # citation in the same shape as search_docs PA tool
                    'citation': f"[{doc.file_path}#{chunk.chunk_index}]",
                    # Cycle 1A KFI-3 (ADR-0130): canonical_authority
                    # metadata for downstream authority-aware consumers.
                    'canonical_authority': doc.canonical_authority,
                    # Retained for deterministic tie-break sort below.
                    'updated_at': doc.updated_at,
                    'created_at': doc.created_at,
                    'document_id': doc.id,
                },
                # D9/D10 retrieval_boost maps to legacy importance_score.
                'importance_score': float(doc.retrieval_boost or 1.0),
                'similarity_score': similarity,
                # S2826 Pattern B diagnostic (per Chris D2 traceability
                # + Rigby SIGN Q4 refinement) — surfaces gate + bonus
                # provenance so consumers + tests can distinguish raw
                # semantic rank from policy-boosted rank.
                'intent_gate_fired': count_intent_active,
                'intent_gate_name': 'count' if count_intent_active else None,
                'count_intent_bonus': count_intent_bonus,
                'effective_similarity': effective_similarity,
                # Cycle 1A KFI-3: authority-aware retrieval fields.
                # Top-level canonical_authority is always populated;
                # authority_weight + weighted_score are populated only
                # when authority_weighted=True.
                'canonical_authority': doc.canonical_authority,
                'authority_weight': authority_weight,
                'weighted_score': weighted_score,
            })

        # Cycle 1A KFI-3 (ADR-0130 §2.1): apply weighted ranking +
        # deterministic tie-break in Python. Sort key composition:
        #   1. weighted_score DESC
        #   2. Coalesce(document.updated_at, document.created_at) DESC
        #   3. document.id ASC (primary final tie-break per ADR §2.1)
        #   4. chunk.id ASC (post-code SIGN hardening: two chunks from
        #      the same Document tie on 1-3; DocumentEmbedding.id keeps
        #      chunk ordering deterministic)
        if authority_weighted:
            def _sort_key(row):
                meta = row['metadata']
                effective_ts = meta.get('updated_at') or meta.get('created_at')
                doc_id_str = str(meta.get('document_id') or '')
                chunk_id_str = str(row.get('id') or '')
                epoch = effective_ts.timestamp() if effective_ts else 0.0
                return (
                    -row['weighted_score'],
                    -epoch,
                    doc_id_str,
                    chunk_id_str,
                )
            documents.sort(key=_sort_key)
            documents = documents[:limit]
        elif count_intent_active:
            # S2826 Pattern B — when the COUNT intent gate fired and we
            # oversampled the candidate pool, re-sort by (raw similarity +
            # bonus) descending, tie-break identical to authority_weighted
            # path (updated_at DESC then document.id ASC then chunk.id
            # ASC) so downstream ordering stays deterministic even when
            # the bonus creates ties.
            def _count_sort_key(row):
                meta = row['metadata']
                effective_ts = meta.get('updated_at') or meta.get('created_at')
                doc_id_str = str(meta.get('document_id') or '')
                chunk_id_str = str(row.get('id') or '')
                epoch = effective_ts.timestamp() if effective_ts else 0.0
                return (
                    -(row['similarity_score'] + row.get('count_intent_bonus', 0.0)),
                    -epoch,
                    doc_id_str,
                    chunk_id_str,
                )
            documents.sort(key=_count_sort_key)
            documents = documents[:limit]

        # Strip internal tie-break fields before returning to callers.
        for row in documents:
            row['metadata'].pop('updated_at', None)
            row['metadata'].pop('created_at', None)
            row['metadata'].pop('document_id', None)

        logger.info(
            f"Found {len(documents)} relevant chunks for query "
            f"(filters: category={category} class={effective_class} "
            f"is_pinned={is_pinned} min_session={min_session} "
            f"include_superseded={include_superseded} "
            f"canonical_authority={canonical_authority} "
            f"authority_weighted={authority_weighted} "
            f"count_intent_active={count_intent_active})"
        )

        # S2826 Pattern B drift-re-mask detection (Rigby SIGN Q5). WARN
        # when the intent gate fired but none of the canonical targets
        # in _COUNT_INTENT_BONUS surfaced in the returned candidate pool.
        # Root causes the log surfaces: (a) target Document.status drifted
        # from 'processed' back to 'archived' and got filtered by
        # include_superseded=False; (b) target chunk similarity dropped
        # below threshold; (c) target file was removed/renamed. Without
        # this alert, future metadata drift silently erases the Pattern B
        # benefit (the class of drift S2826 root-cause established).
        if count_intent_active and _COUNT_INTENT_BONUS:
            returned_paths = {
                (d.get('metadata') or {}).get('file_path') for d in documents
            }
            missing_targets = [
                p for p in _COUNT_INTENT_BONUS.keys() if p not in returned_paths
            ]
            if missing_targets and len(missing_targets) == len(_COUNT_INTENT_BONUS):
                # ALL canonical targets absent — most likely the metadata
                # drift class. Single-target-missing is expected on off-
                # target queries; all-missing when the gate fires is the
                # concerning shape.
                logger.warning(
                    "[S2826_PATTERN_B_DRIFT] count_intent_active=True but "
                    "NONE of the mapped canonical targets are in the "
                    "returned pool. targets=%s query=%r include_superseded=%s. "
                    "Check Document.status='processed' for these paths; "
                    "S2826 root-cause showed sync_docs_index_to_documents "
                    "update path does not refresh status field.",
                    list(_COUNT_INTENT_BONUS.keys()),
                    query[:200],
                    include_superseded,
                )
        return documents

    except _RAG_EMBEDDINGS_ENV_ERRORS as e:
        # Session 2728 F-RG-1 — narrow except discipline. Pre-patch this
        # branch caught EVERY Exception (ORM, decrypt, math, TypeError from
        # a caller-side bug, etc.) and returned []. That silent zero-results
        # is indistinguishable from "no relevant content" and is the same
        # anti-pattern S1234 D21 fixed for `search_personal_memories`. Now
        # only environmental errors (DB connection lost, network down, OS
        # I/O) return [] with the error log; logic errors propagate so
        # future refactors that break the retrieval path are visible.
        logger.error(
            f"search_embeddings: environmental error: "
            f"{type(e).__name__}: {e}",
            exc_info=True,
        )
        return []

def get_rag_context(query: str, max_tokens: int = 2000, include_personal: bool = False) -> Dict[str, Any]:
    """
    Get RAG context for a query
    
    Args:
        query: The user's query
        max_tokens: Maximum tokens to include in context
        include_personal: Whether to include personal memories (default: False)
        
    Returns:
        Dictionary with context and metadata
    """
    
    # Search for relevant documents
    # Session 1234 D15 — was 0.6; lowered to 0.4 to match the new
    # search_embeddings default. text-embedding-3-small puts related
    # content in the 0.4-0.7 band; 0.6 was cutting most signal.
    documents = search_embeddings(
        query=query,
        limit=10,  # Get more initially, then filter
        similarity_threshold=0.4,
        exclude_personal=not include_personal  # Respect privacy by default
    )
    
    if not documents:
        logger.info("No relevant documents found for RAG")
        return {
            'has_context': False,
            'documents': [],
            'context_text': ""
        }
    
    # Build context text
    context_parts = []
    used_documents = []
    current_tokens = 0
    
    for doc in documents:
        # Estimate tokens (rough approximation)
        doc_tokens = len(doc['content']) // 4
        
        if current_tokens + doc_tokens > max_tokens:
            break
            
        context_parts.append(f"[{doc['content_type'].upper()}] {doc['content']}")
        used_documents.append({
            'id': doc['id'],
            'type': doc['content_type'],
            'similarity': doc['similarity_score']
        })
        current_tokens += doc_tokens
    
    context_text = "\n\n".join(context_parts)
    
    return {
        'has_context': bool(context_text),
        'documents': used_documents,
        'context_text': context_text,
        'total_documents': len(documents),
        'used_documents': len(used_documents)
    }

def _cosine_similarity_python(a, b):
    """Pure-Python cosine similarity for JSON-stored embedding vectors.

    Session 1234 D21 — UserEmbedding.embedding_vector is a JSONField,
    not a pgvector VectorField, so we can't use the native `<=>`
    operator. Python-side cosine is fine for the expected corpus size
    (0 → a few thousand rows per user). When UserEmbedding grows past
    ~10k rows total, migrate the field to pgvector VectorField and
    repoint this function at the native operator.
    """
    if not a or not b or len(a) != len(b):
        return 0.0
    import math
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0 or nb <= 0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


# Session 1234 D21 — Personal-memory search narrow-except allowlist.
# Same shape as D17/D18/D19/D20 (DatabaseError, ConnectionError,
# OSError). The cross-file invariant in
# test_d20_views_rag_embeddings_narrow_except.py is NOT extended to
# include this constant because `rag_integration.py` is the
# rag-integration module proper, not a retrieval helper file. The
# functional contract (narrow same set of env errors) is the same,
# but the module's name doesn't fit the test's existing import paths.
_PERSONAL_MEMORY_ENV_ERRORS = (
    __import__('django.db.utils', fromlist=['DatabaseError']).DatabaseError,
    ConnectionError,
    OSError,
)


def search_personal_memories(
    query: str,
    user_id: Optional[int] = None,
    limit: int = 5,
    similarity_threshold: float = 0.4,
) -> List[Dict[str, Any]]:
    """
    Search a user's personal memories via UserEmbedding semantic search.

    Session 1234 D21 — full rewrite. Pre-D21 this function:
      - Connected to a non-existent `ai_unified_platform` database
        (with a non-existent `ai_unified_user` PG user)
      - Queried a non-existent `unified_embeddings` table
      - Wrapped both errors in a broad try/except → return [], so
        every call silently returned "no memories" indistinguishable
        from "user has no personal memories yet"

    Post-D21 this function:
      - Uses Django ORM against `UserEmbedding` (the populated user-
        scoped embedding store: 0 rows locally, populated on Railway
        when chat injects user memories into the embedding pipeline)
      - Filters by `user_id` + `is_active=True` for strict access
        control (no cross-user leakage; matches the original intent)
      - Computes cosine similarity in Python because UserEmbedding's
        `embedding_vector` is a JSONField (not pgvector VectorField).
        Fine performance-wise for the expected corpus size; migrate
        the field to VectorField when usage grows.
      - Narrows the broad except to env errors only per D17-D20
        discipline. Logic errors propagate so future refactors that
        break this function are visible.
      - Default similarity_threshold lowered 0.7 → 0.4 to match D15
        (text-embedding-3-small puts related content in 0.4-0.7 band).

    Args:
        query: The search query (text → embedding).
        user_id: ID of the user whose memories to search. Required.
        limit: Maximum number of results.
        similarity_threshold: Minimum cosine similarity (0-1).

    Returns:
        List of personal memory dicts with shape:
            {id, content, content_type, metadata, importance_score,
             similarity_score, is_personal}
    """
    if not user_id:
        logger.warning("search_personal_memories: no user_id supplied; refusing")
        return []

    query_embedding = create_embedding(query)
    if not query_embedding:
        logger.error("search_personal_memories: failed to create query embedding")
        return []

    try:
        # Lazy import — UserEmbedding lives in core.models_unified_system
        # which has a heavy import graph; deferring keeps rag_integration
        # importable from views.py without dragging it in.
        from django.apps import apps
        UserEmbedding = apps.get_model('core', 'UserEmbedding')

        qs = UserEmbedding.objects.filter(
            user_id=user_id,
            is_active=True,
        ).only(
            'id', 'content', 'content_type', 'metadata', 'confidence_score',
            'embedding_vector',
        )

        scored = []
        for row in qs:
            vec = row.embedding_vector
            if not vec:
                continue
            sim = _cosine_similarity_python(query_embedding, vec)
            if sim < similarity_threshold:
                continue
            scored.append((sim, row))

        # Sort by similarity * importance descending (matches the pre-D21
        # ranking semantics; `confidence_score` is the closest analog to
        # the pre-D21 `importance_score` field).
        scored.sort(
            key=lambda t: t[0] * float(getattr(t[1], 'confidence_score', 1.0) or 1.0),
            reverse=True,
        )

        documents = []
        for sim, row in scored[:limit]:
            documents.append({
                'id': str(row.id),
                'content': (row.content or '')[:1000],
                'content_type': row.content_type or 'memory',
                'metadata': row.metadata if isinstance(row.metadata, dict) else {},
                'importance_score': float(row.confidence_score or 0.5),
                'similarity_score': sim,
                'is_personal': True,
            })

        logger.info(
            f"search_personal_memories: returned {len(documents)} memories "
            f"for user {user_id} (threshold={similarity_threshold}, "
            f"scored {len(scored)} above threshold of {qs.count()} total)"
        )
        return documents

    except _PERSONAL_MEMORY_ENV_ERRORS as e:
        logger.error(
            f"search_personal_memories: environmental error: "
            f"{type(e).__name__}: {e}"
        )
        return []


def enhance_prompt_with_rag(user_message: str, rag_context: Dict[str, Any]) -> str:
    """
    Enhance the user's prompt with RAG context
    
    Args:
        user_message: Original user message
        rag_context: RAG context from get_rag_context
        
    Returns:
        Enhanced prompt with context
    """
    
    if not rag_context.get('has_context'):
        return user_message
    
    enhanced_prompt = f"""You have access to the following relevant context from the knowledge base:

{rag_context['context_text']}

Based on this context and your knowledge, please answer the following question:

{user_message}

Please incorporate relevant information from the context in your response where appropriate."""
    
    return enhanced_prompt