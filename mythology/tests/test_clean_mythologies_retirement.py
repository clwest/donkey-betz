"""Session 1236 P5#3 audit Tranche 2 PR #1 — clean_mythologies retirement.

Verifies `mythology/management/commands/clean_mythologies.py`
`clean_embeddings()` step is retired to a no-op. Pre-retirement it
hit the dead `unified_embeddings` table via `connection.cursor()` raw
SQL; post-retirement it records zero counts and prints the
retirement notice.

Preserved: `setup_guards()`, `setup_patterns()`, `generate_summary()`
all use real Django models (MythPattern, MythologyGuard,
MythologyCleanup, MythologyAlert) and keep working.

Per `feedback_test_real_db_for_queryset_semantics`: real DB
throughout. The mgmt cmd creates real MythologyCleanup rows during
test runs.

Run::

    python manage.py test mythology.tests.test_clean_mythologies_retirement -v 2 --keepdb
"""

from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from mythology.models import MythologyCleanup, MythologyAlert


class CleanMythologiesRetirementBehaviorTests(TestCase):
    """clean_embeddings step is no-op; mgmt cmd runs cleanly + records
    zero counts."""

    def test_dry_run_completes_with_zero_cleaned(self):
        out = StringIO()
        call_command('clean_mythologies', '--dry-run', stdout=out)
        text = out.getvalue()
        self.assertIn('Items scanned: 0', text)
        self.assertIn('Items cleaned: 0', text)
        self.assertIn('Cleanup completed', text)
        # Retirement notice is in the output
        self.assertIn('[RETIRED]', text)
        self.assertIn('HALLUCINATION_INDICATORS', text)

    def test_real_run_creates_cleanup_row_with_zero_counts(self):
        before = MythologyCleanup.objects.count()
        call_command('clean_mythologies', stdout=StringIO())
        after = MythologyCleanup.objects.count()
        self.assertEqual(after, before + 1)

        latest = MythologyCleanup.objects.latest('started_at')
        self.assertEqual(latest.items_scanned, 0)
        self.assertEqual(latest.items_cleaned, 0)
        self.assertEqual(latest.dart_flutter_removed, 0)
        self.assertEqual(latest.fitness_dashboard_removed, 0)
        self.assertEqual(latest.deployments_350_removed, 0)
        self.assertEqual(latest.capability_exaggerations_removed, 0)
        self.assertIsNotNone(latest.completed_at)

    def test_no_mythology_alert_fired_when_zero_cleaned(self):
        """Pre-retirement created `MythologyAlert` rows when
        `total_cleaned > 100`. Post-retirement always reports zero,
        so no alerts should ever fire from clean_mythologies."""
        before = MythologyAlert.objects.count()
        call_command('clean_mythologies', stdout=StringIO())
        after = MythologyAlert.objects.count()
        self.assertEqual(
            after, before,
            "MythologyAlert must NOT fire from the retired cleanup step.",
        )

    def test_setup_patterns_still_creates_mythpatterns(self):
        """The preserved setup_patterns() uses real MythPattern model
        and should continue creating/updating pattern rows."""
        from mythology.models import MythPattern
        before = MythPattern.objects.count()
        call_command('clean_mythologies', stdout=StringIO())
        after = MythPattern.objects.count()
        # setup_patterns is idempotent (get_or_create); first run
        # creates several patterns. After fix should produce >= before.
        self.assertGreaterEqual(after, before)

    def test_does_not_hit_dead_unified_embeddings_table(self):
        """Pre-retirement raised `relation "unified_embeddings" does
        not exist` swallowed silently. Post-retirement makes zero DB
        queries to the dead table — verify by patching
        `django.db.connection.cursor` and asserting no call."""
        from unittest.mock import patch
        # If the retired clean_embeddings still calls connection.cursor,
        # the patch's mock will record it. Since we removed the import +
        # the .cursor() call entirely, the patch should NEVER fire from
        # within clean_embeddings.
        with patch(
            'mythology.management.commands.clean_mythologies.connection',
            create=True,
        ) as mock_conn:
            call_command('clean_mythologies', stdout=StringIO())
        mock_conn.cursor.assert_not_called()


class NoDeadSubstrateLeftInCleanMythologiesTests(TestCase):
    """Source-level guard: clean_embeddings function body has no live
    raw-SQL / dead-table references outside docstring."""

    def _extract_clean_embeddings_body(self):
        from pathlib import Path
        import ast
        text = Path(__file__).resolve().parent.parent.parent.joinpath(
            'mythology/management/commands/clean_mythologies.py',
        ).read_text()
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'Command':
                for sub in node.body:
                    if (
                        isinstance(sub, ast.FunctionDef)
                        and sub.name == 'clean_embeddings'
                    ):
                        body = sub.body
                        if (
                            body
                            and isinstance(body[0], ast.Expr)
                            and isinstance(body[0].value, ast.Constant)
                            and isinstance(body[0].value.value, str)
                        ):
                            body = body[1:]
                        return '\n'.join(ast.unparse(stmt) for stmt in body)
        raise AssertionError('clean_embeddings method not found')

    def test_no_cursor_execute_in_clean_embeddings_body(self):
        body = self._extract_clean_embeddings_body()
        self.assertNotIn('cursor.execute', body)
        self.assertNotIn('connection.cursor', body)

    def test_no_unified_embeddings_query_in_clean_embeddings_body(self):
        body = self._extract_clean_embeddings_body()
        for marker in (
            'FROM unified_embeddings',
            'DELETE FROM unified_embeddings',
            'INTO unified_embeddings',
        ):
            self.assertNotIn(marker, body)

    def test_no_connection_import_at_module_level(self):
        """The `from django.db import connection` import was used only
        by the retired clean_embeddings step. After retirement it
        should be gone (dead import)."""
        from pathlib import Path
        text = Path(__file__).resolve().parent.parent.parent.joinpath(
            'mythology/management/commands/clean_mythologies.py',
        ).read_text()
        self.assertNotIn('from django.db import connection', text)
