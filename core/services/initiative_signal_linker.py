"""
Initiative Signal Linker
========================

Session 1016: Automatically links new initiatives to relevant SignalClusters
using embedding-based semantic similarity.

Problem: Initiatives are created without signal_cluster links, making it hard
to trace what evidence triggered them and whether they're grounded in real data.

Solution: When an initiative is created, compare its description against recent
SignalCluster keywords/sample_signals using embeddings. Link the best match
above a similarity threshold.

Usage:
    from core.services.initiative_signal_linker import auto_link_initiative_signals

    auto_link_initiative_signals(initiative)
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.60


def find_matching_signal_cluster(initiative) -> Optional[object]:
    """
    Find the best matching SignalCluster for an initiative using embeddings.

    Compares initiative description against recent SignalCluster keywords
    and sample_signals text. Returns the best match above SIMILARITY_THRESHOLD.

    Returns:
        SignalCluster instance or None
    """
    from core.models_signal_intelligence import SignalCluster
    from core.services.embedding_service import get_embedding_service

    description = initiative.description or initiative.name or ''
    if len(description.strip()) < 10:
        return None

    # Get recent active/triggered clusters with keywords
    clusters = SignalCluster.objects.filter(
        status__in=['active', 'triggered', 'detecting'],
    ).exclude(
        keywords=[],
    ).order_by('-detected_at')[:50]

    if not clusters:
        return None

    try:
        service = get_embedding_service()

        # Embed the initiative description
        init_embedding = service.get_embedding_sync(description[:2000])
        if not init_embedding:
            return None

        best_cluster = None
        best_score = 0.0

        for cluster in clusters:
            # Build cluster text from keywords + sample signals
            keywords_text = ', '.join(cluster.keywords or [])
            samples_text = ' '.join(
                s.get('text', '')[:200]
                for s in (cluster.sample_signals or [])[:5]
            )
            cluster_text = f"{cluster.name} {keywords_text} {samples_text}".strip()

            if len(cluster_text) < 10:
                continue

            cluster_embedding = service.get_embedding_sync(cluster_text[:2000])
            if not cluster_embedding:
                continue

            # Cosine similarity
            import numpy as np
            a = np.array(init_embedding)
            b = np.array(cluster_embedding)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            if norm_a == 0 or norm_b == 0:
                continue
            score = float(np.dot(a, b) / (norm_a * norm_b))

            if score > best_score:
                best_score = score
                best_cluster = cluster

        if best_cluster and best_score >= SIMILARITY_THRESHOLD:
            logger.info(
                f"[signal_linker] Matched '{initiative.name[:50]}' to cluster "
                f"'{best_cluster.name[:50]}' (score={best_score:.3f})"
            )
            return best_cluster

        logger.debug(
            f"[signal_linker] No match above {SIMILARITY_THRESHOLD} for "
            f"'{initiative.name[:50]}' (best={best_score:.3f})"
        )
        return None

    except Exception as e:
        logger.warning(f"[signal_linker] Embedding comparison failed: {e}")
        return None


def auto_link_initiative_signals(initiative) -> bool:
    """
    Attempt to link an initiative to a matching SignalCluster.

    Safe to call on any initiative — no-ops if already linked or no match found.

    Returns:
        True if a link was established, False otherwise
    """
    # Skip if already linked
    if getattr(initiative, 'signal_cluster_id', None):
        return False

    try:
        cluster = find_matching_signal_cluster(initiative)
        if cluster:
            initiative.signal_cluster = cluster
            initiative.save(
                update_fields=['signal_cluster'],
                skip_invariant_check=True,
            )
            logger.info(
                f"[signal_linker] Linked initiative '{initiative.name[:50]}' "
                f"to cluster '{cluster.name[:50]}'"
            )
            return True
    except Exception as e:
        logger.warning(f"[signal_linker] Auto-link failed for '{initiative.name[:50]}': {e}")

    return False
