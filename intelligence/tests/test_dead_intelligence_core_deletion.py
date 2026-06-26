"""Session 1235 P5#3 audit Tranche 1 PR #6 — intelligence/core.py deletion guard.

Source-level + import-level guards that the deleted `intelligence/core.py`
module stays deleted. Pre-deletion this file was 888 lines of architectural
sketch (UniversalIntelligenceLayer class) with:
- Zero imports anywhere in the codebase
- Connect to non-existent 'intelligence' database
- Heavy unconditional deps (pgvector.psycopg2, openai, redis)

Per Rigby's audit approval (conv pa-0f08fc48ec914917 — "deletion is fine
when caller-evidence is definitive"). If the file is restored in the
future, these tests would force a deliberate update via PR review.

Run::

    python manage.py test intelligence.tests.test_dead_intelligence_core_deletion -v 2 --keepdb
"""

from django.test import TestCase


class IntelligenceCoreDeletionTests(TestCase):
    """Guards against the file's resurrection in its dead-substrate form."""

    def test_intelligence_core_module_does_not_exist(self):
        """The dead module must stay deleted. If reintroduced, it must
        not be the pre-deletion shape (psycopg2.connect to non-existent
        'intelligence' DB)."""
        import importlib.util
        spec = importlib.util.find_spec('intelligence.core')
        self.assertIsNone(
            spec,
            "intelligence/core.py was deleted in Session 1235 P5#3 PR #6 "
            "(zero callers, dead substrate). If you need to add a new "
            "intelligence.core module, ensure it does NOT replicate the "
            "pre-deletion shape: no psycopg2.connect to 'intelligence' DB, "
            "no heavy unconditional imports of pgvector/openai/redis.",
        )

    def test_no_callers_assume_universal_intelligence_layer_exists(self):
        """Verify no production code imports the deleted class. Test
        scans the codebase for residual references that would break if
        someone hand-restored the file."""
        import subprocess
        from pathlib import Path
        repo_root = Path(__file__).resolve().parent.parent.parent
        result = subprocess.run(
            ['grep', '-rEn',
             '--include=*.py',
             '--exclude-dir=archive',
             '--exclude-dir=__pycache__',
             '--exclude-dir=.venv',
             # Pattern: real import statement, not the deletion guard itself
             r'^(from intelligence\.core|import intelligence\.core)',
             str(repo_root)],
            capture_output=True, text=True,
        )
        # exit code 1 = no matches; exit code 0 = matches found
        matches = [
            l for l in result.stdout.strip().split('\n')
            if l and 'test_dead_intelligence_core_deletion' not in l
        ]
        self.assertEqual(
            matches, [],
            f"Found residual imports of intelligence.core: {matches}. "
            "The module was deleted; either remove the imports or "
            "revert the deletion deliberately.",
        )
