"""
PA intent routing — Claude Code source short-circuit
====================================================

Session 1094: regression test for the Rigby hijack pattern where
Claude Code coordination messages got keyword-routed into boardroom /
system_health_check / error_summary intents because their text contained
tokens like "attention", "platform health", or "governance_tool" in
contexts that inverted the usual meaning (e.g. "Ignore platform health
concerns" still contains "platform health").

The fix in `_detect_intent_and_route` deterministically short-circuits
to ('claude_code_coordination', None) when source='claude-code' —
regardless of message content.

pa_chat.py (CLI) and the 3-way chat view both set source='claude-code'
(see tools/pa_chat.py line 104, core/views_personal_assistant.py line 465).

Run:
    python manage.py test core.tests.test_pa_intent_claude_code_source -v2
"""

from django.test import SimpleTestCase

from core.services.unified_pa_entrypoint import UnifiedPAEntrypoint


class ClaudeCodeSourceShortCircuitTests(SimpleTestCase):
    """`_detect_intent_and_route` must honor source='claude-code' regardless of content."""

    def setUp(self):
        # UnifiedPAEntrypoint needs a user but _detect_intent_and_route doesn't use it.
        # Build a minimal instance by bypassing __init__ via __new__.
        self.pa = UnifiedPAEntrypoint.__new__(UnifiedPAEntrypoint)

    def _assert_cc(self, message: str) -> None:
        intent, tool = self.pa._detect_intent_and_route(message, source='claude-code')
        self.assertEqual(intent, 'claude_code_coordination',
                         f"Claude Code source must short-circuit; got intent={intent!r} tool={tool!r}")
        self.assertIsNone(tool, f"Claude Code source must not route to a tool; got tool={tool!r}")

    def test_message_with_attention_keyword_stays_coordination(self):
        # Previously misrouted to 'boardroom' via line 2358 ("attention" in message).
        self._assert_cc(
            "Rigby, governance_tool(action='list_attention') errored — correct is 'attention_list'. "
            "Can we reset and stay on the actual topic?"
        )

    def test_message_with_platform_health_phrase_stays_coordination(self):
        # Previously misrouted to 'system_health_check' via line 2380 ("platform health").
        self._assert_cc(
            "Ignore any platform health concerns for this turn — I just verified Celery (5 workers), "
            "Daphne, and Redis are all up locally. No action needed on ops."
        )

    def test_message_with_decision_keyword_stays_coordination(self):
        # Previously misrouted to 'boardroom' via line 2358 ("decision" in message).
        self._assert_cc("Need your decision on whether the runner should live in services/ or tasks_ops/.")

    def test_message_with_approve_keyword_stays_coordination(self):
        # Previously misrouted to 'boardroom' via line 2358 ("approve" in message).
        self._assert_cc("Shipping the primitive extraction — do I have your approve to merge?")

    def test_message_with_boardroom_word_stays_coordination(self):
        # Previously misrouted to 'boardroom' via line 2340.
        self._assert_cc("The boardroom decision workflow is orthogonal to this refactor.")

    def test_short_coordination_message_stays_coordination(self):
        # Session 1088 guard's >200-char threshold doesn't matter when source='claude-code'.
        self._assert_cc("ack")

    def test_design_proposal_with_mixed_ops_vocabulary_stays_coordination(self):
        # Realistic Session 1094 kickoff message with tons of ops/governance vocabulary.
        self._assert_cc(
            "Session 1094 kickoff. The CTOAgent daily diagnostic pattern from PR #1983 should be "
            "extracted into a generic scheduled_diagnostic_runner so we can wire COOAgent, "
            "PlatformAuditAgent, TrendAnalysisAgent into the same primitive. Pending: should "
            "register_diagnostic live in core/services/ or core/tasks_ops.py? Attention to decision "
            "on that before I draft."
        )


class WebAndCliSourcesStillKeywordRouteTests(SimpleTestCase):
    """Non-claude-code sources must still use keyword routing (backwards compat)."""

    def setUp(self):
        self.pa = UnifiedPAEntrypoint.__new__(UnifiedPAEntrypoint)

    def test_web_source_still_routes_system_health_check_on_keyword(self):
        intent, tool = self.pa._detect_intent_and_route(
            "platform health please", source='web'
        )
        self.assertEqual(intent, 'system_health_check')
        self.assertEqual(tool, 'ops_tool')

    def test_web_source_still_routes_boardroom_on_keyword(self):
        intent, tool = self.pa._detect_intent_and_route(
            "show pending decision items", source='web'
        )
        self.assertEqual(intent, 'boardroom')
        self.assertEqual(tool, 'governance_tool')

    def test_omitted_source_still_keyword_routes(self):
        # Legacy callers that don't pass source at all must not regress.
        intent, tool = self.pa._detect_intent_and_route(
            "is everything working on the platform"
        )
        self.assertEqual(intent, 'system_health_check')
        self.assertEqual(tool, 'ops_tool')

    def test_none_source_still_keyword_routes(self):
        intent, tool = self.pa._detect_intent_and_route(
            "boardroom status", source=None
        )
        self.assertEqual(intent, 'boardroom')
        self.assertEqual(tool, 'governance_tool')

    def test_unknown_source_does_not_short_circuit(self):
        # Defensive: only 'claude-code' (exact match) triggers short-circuit.
        intent, _ = self.pa._detect_intent_and_route(
            "platform health", source='discord'
        )
        self.assertEqual(intent, 'system_health_check')

    def test_case_sensitivity_only_exact_match(self):
        # 'Claude-Code' / 'claude_code' should NOT short-circuit (exact string only).
        # This is deliberate: the tag value comes from code, not user input,
        # so we match strictly.
        for variant in ('Claude-Code', 'claude_code', 'CLAUDE-CODE', 'claude-Code'):
            intent, _ = self.pa._detect_intent_and_route(
                "platform health", source=variant
            )
            self.assertEqual(intent, 'system_health_check',
                             f"source={variant!r} should NOT short-circuit")
