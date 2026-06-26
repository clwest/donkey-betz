"""Session 1236 P5#3 audit Tranche 4 — dead pre-existing unit tests deletion guard.

Regression-guard tests that the 6 deleted pytest-skipped tests stay
deleted. All 6 had `pytestmark = [pytest.mark.django_db,
pytest.mark.skip(reason="Requires unified_embeddings table from
production DB")]` since Session 452 — zombie tests providing zero CI
signal while still costing collection overhead + reader attention.

Per the audit DoD: dead DB/table references should not remain in
production code paths. Test code that's been auto-skipping for
hundreds of sessions qualifies.

Run::

    python manage.py test core.tests.test_tranche_4_dead_unit_tests_deleted -v 2 --keepdb
"""

from pathlib import Path

from django.test import TestCase


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class Tranche4DeadUnitTestsDeletionTests(TestCase):
    """Guards against restoration of the 6 deleted skipped tests."""

    DELETED_TESTS = (
        'tests/unit/test_code_embeddings.py',
        'tests/unit/test_code_rag.py',
        'tests/unit/test_embeddings_rag.py',
        'tests/unit/test_encryption_migration.py',
        'tests/unit/test_rag_direct.py',
        'tests/unit/test_rag_with_existing_embeddings.py',
    )

    def test_all_deleted_unit_tests_stay_deleted(self):
        for rel_path in self.DELETED_TESTS:
            with self.subTest(file=rel_path):
                full = REPO_ROOT / rel_path
                self.assertFalse(
                    full.exists(),
                    f"{rel_path} reappeared after Session 1236 Tranche 4 "
                    "deletion. These tests were marked "
                    "pytest.skip(reason=\"Requires unified_embeddings "
                    "table from production DB\") since Session 452 — "
                    "zombie tests against the dead substrate. If you "
                    "need to test embedding integration, write fresh "
                    "tests against the live `DocumentEmbedding` / "
                    "`UserEmbedding` ORM (see Session 1234 D12+ "
                    "PRs #2621 and #2631 for the live pivot patterns)."
                )
