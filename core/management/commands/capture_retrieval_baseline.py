"""Cycle 1A KFI-3 (ADR-0130 §2.3) — SC-7 retrieval baseline capture.

Runs a fixture set of queries against ``core.rag_integration.search_embeddings``
and writes the top-K results to JSON. Used to capture PRE-implementation
baseline then re-run POST-implementation for SC-7 preservation check via
the companion ``compare_retrieval_baseline`` command.

Usage:
    python manage.py capture_retrieval_baseline \
        --output content/tests/fixtures/retrieval_baseline_20260708_pre.json

    python manage.py capture_retrieval_baseline \
        --output content/tests/fixtures/retrieval_baseline_20260708_post.json \
        --with-authority-variants
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from core.rag_integration import search_embeddings


# Chris's 4 KFI-3 discoverability queries + ADR §2.3 SC-7 extended
# baseline suite (≥20 queries).
_CHRIS_KFI3_QUERIES = [
    'canonical_authority field ADR-0120 Document model',
    'KFI-2 canonical_authority backfill signal-safe QuerySet update',
    'Deliverable Document mirror ADR-0110 workspace_canonical',
    'Workspace canonical governance Cycle 1A ADR',
]

_SC7_EXTENDED_QUERIES = [
    'docs cascade sync build_docs_index',
    'Rigby PA function calling GPT-5.2',
    'Celery worker long_running queue',
    'AGENT_MAP agent routing',
    'signal handler post_save Deliverable',
    'RAG embedding pgvector cosine similarity',
    'session handoff Cycle 1A implementation',
    'workspace deliverable ratification record',
    'content Document raw_content processed_content',
    'spider network intelligence signal',
    'DocumentEmbedding chunk_index embedding_model',
    'canonical governance ratifier authority',
    'file_path docs prefix imported source',
    'orphan chunk exclusion filter retrieval',
    'similarity threshold text-embedding-3-small',
    'processing_log add_processing_log Document',
]


class Command(BaseCommand):
    help = 'Capture a retrieval baseline snapshot (KFI-3 SC-7 preservation).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output', dest='output', required=True,
            help='Output JSON path for the baseline snapshot.',
        )
        parser.add_argument(
            '--limit', dest='limit', type=int, default=10,
            help='Top-K per query (default 10).',
        )
        parser.add_argument(
            '--with-authority-variants', dest='with_variants',
            action='store_true',
            help=(
                'Also capture authority_weighted=True and '
                'canonical_authority=workspace_canonical variants. Use '
                'post-implementation to compare against pre-baseline.'
            ),
        )

    def handle(self, *args, **options):
        output_path = Path(options['output'])
        limit = options['limit']
        with_variants = options['with_variants']

        queries = _CHRIS_KFI3_QUERIES + _SC7_EXTENDED_QUERIES

        snapshot = {
            'version': 1,
            'queries': [],
        }

        for q in queries:
            row = {
                'query': q,
                'default': self._snapshot_query(q, limit),
            }
            if with_variants:
                row['authority_weighted'] = self._snapshot_query(
                    q, limit, authority_weighted=True,
                )
                row['workspace_canonical_filter'] = self._snapshot_query(
                    q, limit, canonical_authority='workspace_canonical',
                )
            snapshot['queries'].append(row)
            self.stdout.write(
                f'  captured {q!r} -> {len(row["default"])} rows (default)'
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(snapshot, indent=2, default=str))
        self.stdout.write(
            f'Baseline written: {output_path} '
            f'({len(queries)} queries, limit={limit}, variants={with_variants})'
        )

    def _snapshot_query(self, query, limit, **kwargs):
        rows = search_embeddings(query=query, limit=limit, **kwargs)
        return [
            {
                'chunk_id': r['id'],
                'title': r['metadata'].get('title'),
                'file_path': r['metadata'].get('file_path'),
                'canonical_authority': r.get('canonical_authority'),
                'similarity_score': r.get('similarity_score'),
                'weighted_score': r.get('weighted_score'),
            }
            for r in rows
        ]
