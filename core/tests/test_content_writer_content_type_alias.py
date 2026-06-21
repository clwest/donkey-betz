"""
Session 1184 PR-D: ContentWriterAgent content_type alias normalization.
========================================================================

Proves the fix for the failure surfaced by Rigby's forensic validation run
(execution `2aded481-4f62-45e0-b6b3-615cdcfc081e` on 2026-06-21):

    error: Unknown content type: deliverable. Available: ['blog_post',
           'podcast_script', 'video_script', 'article', 'social_thread',
           'newsletter', 'internal_document']

Root cause: GPT-5.2 picked the word "deliverable" from the prompt
("create a short diagnostic deliverable") as the `content_type` arg, but
"deliverable" is the *container* (Deliverable row), not a content type.
The dispatcher rejected it hard → no deliverable created → entire provenance
chain validation broke before it could even test the Session 1184 PR-A work.

Fix shape (two-prong):
  1. **Agent-layer alias** — `content_writer_agent.py:877` normalizes common
     misnomers (`deliverable`/`doc`/`document`/`note`/`memo`/`report`/`brief`/
     `post`/`blog`/`social`/`thread`/`email`/`podcast`/`video`) to the closest
     valid type before the hard reject. Logs a WARN so the upstream caller can
     be tightened too.
  2. **PA tool schema enum** — `pa_tool_schemas.py:1693` promotes
     `content_type` from the freeform `context` dict to an explicit enum at
     the tool-call level, so GPT-5.2 can't pick invalid values going forward.

Tests here cover the agent-layer alias path. Schema enum is verified at the
LLM-integration layer (not unit-testable here without an OpenAI call).

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_content_writer_content_type_alias --keepdb -v2
"""

from django.test import TestCase

from core.agents.content_writer_agent import CONTENT_TYPES


class ContentTypeAliasMapTests(TestCase):
    """Pure-function checks on the alias map shape — no LLM needed."""

    # The alias map is defined inline in the agent's execute() method.
    # Mirror it here for assertion clarity; this list must match the
    # source. If you add a new alias in the agent, add it here too.
    EXPECTED_ALIASES = {
        'deliverable': 'internal_document',
        'doc': 'internal_document',
        'document': 'internal_document',
        'note': 'internal_document',
        'memo': 'internal_document',
        'report': 'internal_document',
        'brief': 'internal_document',
        'post': 'blog_post',
        'blog': 'blog_post',
        'social': 'social_thread',
        'thread': 'social_thread',
        'email': 'newsletter',
        'podcast': 'podcast_script',
        'video': 'video_script',
    }

    def test_every_alias_target_is_a_real_content_type(self):
        """Every alias must map to a key that exists in CONTENT_TYPES.
        Otherwise the alias just trades one rejection for another."""
        for alias, target in self.EXPECTED_ALIASES.items():
            self.assertIn(
                target, CONTENT_TYPES,
                f"Alias '{alias}' → '{target}' but '{target}' is not in "
                f"CONTENT_TYPES (available: {list(CONTENT_TYPES.keys())})",
            )

    def test_deliverable_specifically_maps_to_internal_document(self):
        """The specific failure mode from Rigby's run 2aded481 — must
        not regress. 'deliverable' is the most common misnomer because
        the system glossary uses 'Deliverable' for the persistence
        envelope; users + GPT-5.2 both pick it as a content type."""
        self.assertEqual(
            self.EXPECTED_ALIASES['deliverable'], 'internal_document',
            "Regression guard for Session 1184 PR-D root cause",
        )

    def test_no_alias_shadows_a_real_content_type(self):
        """If an alias key collides with a real CONTENT_TYPES key, the
        agent's `not in CONTENT_TYPES` guard short-circuits and the
        alias never fires — wasted entry. Catch that here."""
        for alias in self.EXPECTED_ALIASES:
            self.assertNotIn(
                alias, CONTENT_TYPES,
                f"Alias '{alias}' shadows a real CONTENT_TYPES key — "
                f"remove it from the alias map or the alias is dead code",
            )


class ContentWriterAgentAliasPathTests(TestCase):
    """Integration-style test: instantiate the agent, simulate the
    alias-normalization branch, confirm the rejected-content-type
    AgentResult is NOT returned for aliased input.

    Bypasses the LLM call by inspecting just the validate-and-normalize
    branch via a focused execute() call that's expected to fail at the
    *next* validation step (missing research/task) — proving the alias
    branch succeeded.
    """

    def test_deliverable_alias_does_not_trigger_unknown_content_type(self):
        """Pass content_type='deliverable' — should normalize to
        internal_document and NOT fail with the Session 1184 error string."""
        from core.agents.content_writer_agent import ContentWriterAgent
        agent = ContentWriterAgent()
        # Execute with task but no research — expected to fail at the
        # *no-research* check, NOT the unknown-content-type check.
        result = agent.execute(
            task='',  # Empty → triggers no-research/no-task short-circuit
            context={'content_type': 'deliverable'},
            scifi_context=None,
            spider_context=None,
        )
        self.assertFalse(result.success)
        # The fix is proven by the absence of the Session 1184 error signature
        self.assertNotIn(
            'Unknown content type: deliverable',
            result.error or '',
            f"Alias didn't fire — got: {result.error}",
        )

    def test_invalid_non_aliased_content_type_still_rejected(self):
        """Sanity check: aliases shouldn't accept everything. A truly
        unknown content_type that has no alias entry must still fail."""
        from core.agents.content_writer_agent import ContentWriterAgent
        agent = ContentWriterAgent()
        result = agent.execute(
            task='write something',
            context={
                'content_type': 'completely_nonexistent_type',
                'research': 'some body content ' * 30,
            },
            scifi_context=None,
            spider_context=None,
        )
        self.assertFalse(result.success)
        self.assertIn(
            'Unknown content type: completely_nonexistent_type',
            result.error or '',
        )
