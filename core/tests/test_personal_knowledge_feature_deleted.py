"""Session 1235 P5#3 audit Tranche 1 PR #7 — personal-knowledge feature deletion guard.

Verifies the orphan personal-knowledge feature (4 endpoints + the
`core/views_knowledge.py` file + the shadowed/live `personal_knowledge_list`
copies) stay deleted. If anyone restores any piece, these tests fail with
clear pointers at the deletion rationale.

Per Chris's session decision (Session 1235 close): "I do remember when we
started that, but I honestly forgot all about doing it lol." — strongest
possible deletion signal: builder-remembers-but-forgot-using. Same
evidence threshold as `intelligence/core.py` (PR #2641).

Functional redundancy: 4 existing context-injection surfaces already cover
the "give Rigby context about Chris" use case (docs corpus, ConversationMemory,
UserEmbedding, workspace deliverables). A 5th surface would semantically
overlap.

Run::

    python manage.py test core.tests.test_personal_knowledge_feature_deleted -v 2 --keepdb
"""

import importlib.util

from django.test import TestCase
from django.urls import get_resolver


class PersonalKnowledgeFeatureDeletionTests(TestCase):
    """Guards against restoration of the deleted orphan feature."""

    def test_views_knowledge_module_does_not_exist(self):
        spec = importlib.util.find_spec('core.views_knowledge')
        self.assertIsNone(
            spec,
            "core/views_knowledge.py was deleted in Session 1235 P5#3 "
            "Tranche 1 PR #7. If you need to restore the personal-"
            "knowledge feature, ensure it does NOT replicate the pre-"
            "deletion shape (psycopg2 raw SQL to non-existent "
            "ai_unified_platform DB) and pick a real backing model "
            "(likely UserEmbedding with new content_type='personal_knowledge' "
            "CHOICES value + migration). See audit deliverable "
            "feed2d81-ee2f-44c0-8f17-816591d2a3ff.",
        )

    def test_personal_knowledge_list_not_importable_from_core_views(self):
        """The live function used to be at core/views/main.py:1048, the
        shadowed copy at core/views.py:1217. Both were deleted in this PR.
        The `core.views` package re-exports map (`__init__.py`) also no
        longer lists this name."""
        try:
            from core.views import personal_knowledge_list  # noqa: F401
            self.fail(
                "personal_knowledge_list is importable from core.views — "
                "deletion in PR #7 was incomplete."
            )
        except ImportError:
            pass  # expected

    def test_personal_knowledge_list_not_in_main_views_module(self):
        from core.views import main as views_main
        self.assertFalse(
            hasattr(views_main, 'personal_knowledge_list'),
            "personal_knowledge_list exists on core.views.main — "
            "deletion incomplete."
        )

    def test_personal_knowledge_list_not_in_shadowed_views_module(self):
        """The shadowed core/views.py file also had a copy. Both
        deleted in PR #7."""
        import core.views as views_pkg
        # core.views resolves to the package via Python import resolution;
        # the file core/views.py is shadowed and unreachable. Verify the
        # symbol isn't present in either namespace.
        self.assertFalse(
            hasattr(views_pkg, 'personal_knowledge_list'),
            "personal_knowledge_list reappeared on core.views.",
        )

    def test_no_personal_knowledge_url_patterns_registered(self):
        """All 4 URLs under /api/v1/personal-knowledge/* were unwired
        in core/urls.py."""
        all_urls = []

        def collect(patterns, prefix=''):
            for p in patterns:
                if hasattr(p, 'pattern'):
                    full = prefix + str(p.pattern)
                    if hasattr(p, 'url_patterns'):
                        collect(p.url_patterns, full)
                    else:
                        all_urls.append(full)

        collect(get_resolver().url_patterns)
        leftover = [u for u in all_urls if 'personal-knowledge' in u]
        self.assertEqual(
            leftover, [],
            f"Found residual personal-knowledge URL patterns: {leftover}. "
            "Either remove them or revert the deletion deliberately.",
        )
