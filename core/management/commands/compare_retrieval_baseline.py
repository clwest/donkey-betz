"""Cycle 1A KFI-3 (ADR-0130 §2.3) — SC-7 retrieval baseline comparison.

Loads a PRE-implementation baseline JSON and a POST-implementation
baseline JSON produced by ``capture_retrieval_baseline``, then computes
Jaccard top-3 overlap + top-1 similarity delta per query. Reports
per-query PASS/FAIL against ADR-0130 SC-7 thresholds:

- Jaccard top-3 overlap ≥ 0.66 (66%)
- top-1 similarity delta ≤ 0.10 (10%)

Also reports the KFI-3 discoverability metric (Chris's 4 queries):
count of queries where a workspace_canonical row appears in top-K
under the workspace_canonical_filter variant.

Usage:
    python manage.py compare_retrieval_baseline \
        --pre content/tests/fixtures/retrieval_baseline_20260708_pre.json \
        --post content/tests/fixtures/retrieval_baseline_20260708_post.json
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


_JACCARD_THRESHOLD = 0.66
_SIMILARITY_DELTA_THRESHOLD = 0.10

_CHRIS_KFI3_QUERIES = {
    'canonical_authority field ADR-0120 Document model',
    'KFI-2 canonical_authority backfill signal-safe QuerySet update',
    'Deliverable Document mirror ADR-0110 workspace_canonical',
    'Workspace canonical governance Cycle 1A ADR',
}


class Command(BaseCommand):
    help = 'Compare PRE vs POST retrieval baselines for SC-7 preservation.'

    def add_arguments(self, parser):
        parser.add_argument('--pre', dest='pre', required=True)
        parser.add_argument('--post', dest='post', required=True)

    def handle(self, *args, **options):
        pre = self._load(options['pre'])
        post = self._load(options['post'])

        pre_by_q = {r['query']: r for r in pre['queries']}
        post_by_q = {r['query']: r for r in post['queries']}

        common = set(pre_by_q) & set(post_by_q)
        if not common:
            raise CommandError('No overlapping queries between pre and post.')

        pass_count = 0
        fail_count = 0
        sc7_failures = []
        kfi3_visible_count = 0

        for q in sorted(common):
            pre_default = pre_by_q[q]['default']
            post_default = post_by_q[q]['default']

            jaccard, top1_delta = self._compute_diff(pre_default, post_default)
            sc7_pass = (
                jaccard >= _JACCARD_THRESHOLD
                and top1_delta <= _SIMILARITY_DELTA_THRESHOLD
            )
            status = 'PASS' if sc7_pass else 'FAIL'
            if sc7_pass:
                pass_count += 1
            else:
                fail_count += 1
                sc7_failures.append((q, jaccard, top1_delta))

            self.stdout.write(
                f'  [{status}] jaccard_top3={jaccard:.2f} '
                f'top1_delta={top1_delta:.3f} — {q}'
            )

            # KFI-3 discoverability: workspace_canonical_filter variant.
            if q in _CHRIS_KFI3_QUERIES:
                ws_rows = post_by_q[q].get('workspace_canonical_filter') or []
                if any(
                    r.get('canonical_authority') == 'workspace_canonical'
                    for r in ws_rows
                ):
                    kfi3_visible_count += 1

        self.stdout.write('')
        self.stdout.write('== SC-7 preservation ==')
        self.stdout.write(
            f'  pass: {pass_count} / {len(common)} '
            f'(Jaccard≥{_JACCARD_THRESHOLD} + top1Δ≤{_SIMILARITY_DELTA_THRESHOLD})'
        )
        if sc7_failures:
            self.stdout.write('  failures:')
            for q, j, d in sc7_failures:
                self.stdout.write(f'    - {q!r}: jaccard={j:.2f} top1Δ={d:.3f}')

        self.stdout.write('')
        self.stdout.write('== KFI-3 discoverability (Chris 4 queries) ==')
        self.stdout.write(
            f'  workspace_canonical_filter surfaces a workspace_canonical row '
            f'in {kfi3_visible_count}/{len(_CHRIS_KFI3_QUERIES)} queries.'
        )

    def _load(self, path_str):
        path = Path(path_str)
        if not path.exists():
            raise CommandError(f'baseline not found: {path}')
        return json.loads(path.read_text())

    def _compute_diff(self, pre_rows, post_rows):
        """Return (jaccard_top3, top1_similarity_delta)."""
        pre_top3 = {r.get('chunk_id') for r in pre_rows[:3] if r.get('chunk_id')}
        post_top3 = {
            r.get('chunk_id') for r in post_rows[:3] if r.get('chunk_id')
        }
        if not pre_top3 and not post_top3:
            jaccard = 1.0
        elif not (pre_top3 | post_top3):
            jaccard = 1.0
        else:
            jaccard = (
                len(pre_top3 & post_top3) / len(pre_top3 | post_top3)
            )

        pre_top1 = (pre_rows[0].get('similarity_score') if pre_rows else None)
        post_top1 = (post_rows[0].get('similarity_score') if post_rows else None)
        if pre_top1 is None and post_top1 is None:
            top1_delta = 0.0
        elif pre_top1 is None or post_top1 is None:
            top1_delta = 1.0
        else:
            top1_delta = abs(float(pre_top1) - float(post_top1))

        return jaccard, top1_delta
