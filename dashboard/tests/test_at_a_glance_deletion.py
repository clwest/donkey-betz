"""Session 1237 P2.c — dashboard/at_a_glance.py deletion guard.

Pre-deletion this was a 414-line error log analyzer (`ErrorAnalyzer`
class) with a pattern-matching map suggesting auto-fixes for known
errors. Zero importers anywhere in the codebase — verified via grep
across .py / .sh / .md / .yml / .toml files. Same orphan pattern as
`intelligence/core.py` (Session 1236 PR #2641) and the Tranche 3
scripts (Session 1236 PR #2646).

Bonus context: the error-pattern map's suggested fix for
`database "ai_unified_platform" does not exist` was outdated
(suggested `sed -i "" "s/ai_unified_platform/unified_donkey_betz/g"
ai_core/settings.py`). The real fix (per the Session 1235-1236 P5#3
audit) is to pivot calling code to live ORM. With no readers of the
map, fixing the stale data is meaningless — deletion is right.

Per Chris's confirmation at Session 1237 P2.c framing pivot: file
identified as orphan code during the originally-planned "update
error-pattern map" task; deletion approved.

Run::

    python manage.py test dashboard.tests.test_at_a_glance_deletion -v 2 --keepdb
"""

import importlib.util

from django.test import TestCase


class AtAGlanceDeletionTests(TestCase):
    """Guards against restoration of the deleted error log analyzer."""

    def test_dashboard_at_a_glance_module_does_not_exist(self):
        spec = importlib.util.find_spec('dashboard.at_a_glance')
        self.assertIsNone(
            spec,
            "dashboard/at_a_glance.py was deleted in Session 1237 P2.c "
            "(orphan code, zero callers in the codebase, stale "
            "error-pattern map). If you need to add a new error "
            "analyzer, write it against the CURRENT dead-substrate "
            "pivot pattern (Session 1235-1236 P5#3 audit) — NOT the "
            "pre-deletion sed-rename suggestion which assumed a "
            "single-file rename would resolve the issue.",
        )

    def test_no_residual_importers_after_deletion(self):
        """Greps the codebase for residual imports / string refs to
        the deleted module. If any caller reappears, this test fails
        with a clear pointer at the deletion rationale."""
        import subprocess
        from pathlib import Path
        repo_root = Path(__file__).resolve().parent.parent.parent
        result = subprocess.run(
            ['grep', '-rEn',
             '--include=*.py',
             '--exclude-dir=archive',
             '--exclude-dir=__pycache__',
             '--exclude-dir=.venv',
             # Match real import statements OR class references, not
             # the deletion-guard itself.
             r'(from dashboard\.at_a_glance|import dashboard\.at_a_glance|ErrorAnalyzer)',
             str(repo_root)],
            capture_output=True, text=True,
        )
        matches = [
            l for l in result.stdout.strip().split('\n')
            if l and 'test_at_a_glance_deletion' not in l
        ]
        self.assertEqual(
            matches, [],
            f"Found residual imports of dashboard.at_a_glance: {matches}. "
            "The module was deleted; either remove the imports or "
            "revert the deletion deliberately.",
        )
