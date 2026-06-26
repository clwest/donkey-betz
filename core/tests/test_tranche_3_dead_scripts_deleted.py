"""Session 1236 P5#3 audit Tranche 3 — dead one-shot scripts deletion guard.

Regression-guard tests that the 5 deleted one-shot scripts stay
deleted. All 5 targeted the dead `unified_embeddings` table /
`ai_unified_platform` DB, had zero callers anywhere in the codebase
(verified via grep), and were functionally redundant with existing
live mgmt commands.

Run::

    python manage.py test core.tests.test_tranche_3_dead_scripts_deleted -v 2 --keepdb
"""

from pathlib import Path

from django.test import TestCase


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class Tranche3DeadScriptsDeletionTests(TestCase):
    """Guards against restoration of the deleted scripts.

    If any of these files reappear with the pre-deletion dead-
    substrate shape (psycopg2 to ai_unified_platform, raw SQL to
    unified_embeddings), the regression test fails with a pointer
    at the deletion rationale.
    """

    DELETED_SCRIPTS = (
        # Path relative to repo root, intent (for failure message)
        ('scripts/backfill_embeddings.py',
         'One-shot embedding backfill targeting AgentKnowledge / '
         'SpiderData / UnifiedEmbedding. Mixed real-ORM + dead-table '
         'raw SQL. Redundant with live mgmt cmds (embed_documents, '
         'sync_docs_index_to_documents).'),
        ('scripts/upload_unified_docs.py',
         'One-shot docs upload script. Superseded by the live cascade: '
         'build_docs_index → build_rag_corpus → '
         'sync_docs_index_to_documents → embed_documents (now also '
         'auto-fired by core.tasks.refresh_docs_corpus beat task per '
         'Session 1235 PR #2634).'),
        ('scripts/verification/check_embeddings_integration.py',
         'One-shot verification of "migrated embeddings with the RAG '
         'system." The migration is long-done; this script targeted '
         'the dead unified_embeddings table.'),
        ('scripts/verification/verify_and_enable_embeddings.py',
         'One-shot verify + enable embeddings setup script. Targeted '
         'dead ai_unified_platform DB; the live equivalent is '
         'embed_documents mgmt cmd.'),
        ('scripts/verification/verify_complete_isolation.py',
         'One-shot memory isolation acceptance test. Pre-pivot '
         'targeted unified_embeddings; live isolation is enforced via '
         'UserEmbedding user_id FK + memory_access_control decorators '
         '(Session 1235 PR #2639 validated this surface).'),
    )

    def test_all_deleted_scripts_stay_deleted(self):
        for rel_path, intent in self.DELETED_SCRIPTS:
            with self.subTest(file=rel_path):
                full = REPO_ROOT / rel_path
                self.assertFalse(
                    full.exists(),
                    f"{rel_path} reappeared after Session 1236 Tranche 3 "
                    f"deletion. Intent of original: {intent}. "
                    "If you need to add a new script with this name, "
                    "ensure it does NOT replicate the pre-deletion shape "
                    "(psycopg2 raw SQL to non-existent "
                    "ai_unified_platform / unified_embeddings).",
                )
