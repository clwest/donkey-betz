#!/usr/bin/env python3
"""
Smoke retrieval test: verify orphan chunks are excluded from RAG results.

Usage:
    python tools/smoke_retrieval_test.py
    python tools/smoke_retrieval_test.py --query "custom query"

On Railway:
    railway run python tools/smoke_retrieval_test.py
"""
import os
import sys
import argparse

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from content.models import DocumentEmbedding
from core.services.embedding_service import get_embedding_service


QUERIES = [
    "CLAUDE.md",
    "Please review the /docs/ to gain completed understanding of everything we have built",
]


def top_hits(query: str, top_k: int = 5):
    service = get_embedding_service()
    vec = service.get_embedding_sync(query[:500])
    from pgvector.django import CosineDistance

    results = (
        DocumentEmbedding.objects.filter(document__file_path__isnull=False)
        .exclude(document__file_path='')
        .annotate(distance=CosineDistance('embedding_vector', vec))
        .filter(distance__lt=0.5)
        .select_related('document')
        .order_by('distance')[:top_k]
    )
    return [
        {
            'score': round(1 - r.distance, 4),
            'file_path': r.document.file_path,
            'title': r.document.title,
        }
        for r in results
    ]


def run(queries, top_k=5):
    ok = True
    for q in queries:
        print(f"\n{'='*60}")
        print(f"Query: {q[:80]}")
        print(f"{'='*60}")
        hits = top_hits(q, top_k)
        if not hits:
            print("  NO HITS (possible issue)")
            ok = False
            continue
        for i, h in enumerate(hits, 1):
            flag = '' if h['file_path'] else ' ** ORPHAN **'
            print(f"  {i}. score={h['score']:.4f}  {h['file_path'] or '(empty)'}  {h['title']}{flag}")

        # Assertions
        orphans_in_top = sum(1 for h in hits if not h['file_path'])
        if orphans_in_top:
            print(f"  FAIL: {orphans_in_top} orphan(s) in top-{top_k}")
            ok = False
        else:
            print(f"  PASS: no orphans in top-{top_k}")

    return ok


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--query', help='Custom query (added to defaults)')
    p.add_argument('--top-k', type=int, default=5)
    args = p.parse_args()

    queries = list(QUERIES)
    if args.query:
        queries.append(args.query)

    success = run(queries, args.top_k)
    sys.exit(0 if success else 1)
