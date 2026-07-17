"""S2804 Phase 3.1 P0 — agent drafting reliability regression tests.

Covers the two-layer defense that prevents "Draft ready!" with nothing persisted:

  Layer A — Classifier + forced tool_choice
    T3   BaseAgent._call_openai propagates tool_choice override to create_kwargs
    T3b  BaseAgent._call_openai default (no arg) preserves "auto" behavior
    T2   Classifier truth table — drafting vs info vs unknown
      T2a  Chris regression phrasing → 'drafting', 'motion'
      T2b  Noun-only info query (Rigby SIGN Fold 1) → 'info', None
      T2c  Info-phrase denylist ("what is a motion") → 'info', None
      T2d  Ambiguous non-drafting text → 'unknown', None
      T2e  Draft an email → 'drafting', 'email'
      T2f  Prepare a declaration → 'drafting', 'declaration'

  Layer B — Fallback save
    T1   Chris end-to-end regression: dispatch Chris's exact phrasing with GPT
         returning ONLY content (no tool_call) → LegalDocument row created +
         fallback_used context marker set (Rigby SIGN B1)
    T4   Fallback fires for intent=drafting + no tool document + non-empty content
    T5   Fallback does NOT fire for intent=info even if content is empty
    T5b  Fallback does NOT fire for intent=unknown

Run: python manage.py test core.tests.test_legal_agent_drafting_reliability -v2 --noinput
"""

from contextlib import contextmanager
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase

from core.agents.legal.legal_doc_drafter_agent import LegalDocDrafterAgent
from core.models_unified_system import LegalDocument

User = get_user_model()


@contextmanager
def _noop_session(*args, **kwargs):
    yield None


def _make_agent(user=None, case_id=None):
    """Build a LegalDocDrafterAgent with all __init__ side-effects bypassed.

    Reuses the pattern from test_legal_agent_execution.py:_make_agent — same
    attr enumeration from BaseAgent.__init__:477-488.
    """
    agent = LegalDocDrafterAgent.__new__(LegalDocDrafterAgent)
    agent.user = user
    agent.name = 'LegalDocDrafterAgent'
    agent.agent_name = 'LegalDocDrafterAgent'
    agent.case_id = case_id
    agent._current_case = None
    agent._spider_service = None
    agent._semantic_search = None
    agent._tt_decision_count = 0
    agent._intelligent_context = ''
    agent._client = None
    agent._learning_loop = None
    agent._memory_service = None
    agent._agent_model = None
    agent._mythology_enforcer = None
    agent._progress_service = None
    agent._llm_router = None
    agent._accumulated_cost = 0.0
    agent._accumulated_tokens = 0
    agent._health_check_mode = False

    agent.time_travel_session = _noop_session
    agent._build_intelligent_prompt = Mock(return_value='intelligent prompt')
    agent._extract_spider_intelligence = Mock(return_value={'has_data': False, 'trends': []})
    agent._validate_task = Mock(return_value=True)
    agent.record_decision = Mock()
    agent.mark_decision_outcome = Mock()
    agent._record_learning_outcome = Mock()
    agent._build_legal_prompt = Mock(return_value='legal prompt body')
    return agent


# =============================================================================
# T2 — Classifier truth table (pure function; no DB, no LLM)
# =============================================================================

class LegalAgentIntentClassifierTests(SimpleTestCase):
    def _classify(self, task, context=None):
        agent = _make_agent(user=None)
        return agent._classify_task_intent(task, context or {})

    def test_t2a_chris_regression_phrasing_classifies_as_drafting_motion(self):
        intent, target = self._classify(
            'Draft a motion to modify visitation to every weekend from every other weekend'
        )
        self.assertEqual(intent, 'drafting')
        self.assertEqual(target, 'motion')

    def test_t2b_noun_only_info_query_classifies_as_info(self):
        # Rigby SIGN Fold 1 mitigation — noun without drafting verb ≠ drafting
        intent, target = self._classify('deadline for a motion to modify visitation')
        self.assertEqual(intent, 'info')
        self.assertIsNone(target)

    def test_t2c_info_phrase_denylist_overrides_verb_plus_noun(self):
        # "what is" is in the denylist → info even if verb+noun would otherwise match
        intent, target = self._classify('what is the deadline to draft a motion?')
        self.assertEqual(intent, 'info')

    def test_t2d_ambiguous_non_drafting_returns_unknown(self):
        intent, target = self._classify('help me understand Colorado family law')
        self.assertEqual(intent, 'unknown')
        self.assertIsNone(target)

    def test_t2e_draft_email_classifies_as_email(self):
        intent, target = self._classify('Draft a meet-and-confer email to opposing counsel')
        self.assertEqual(intent, 'drafting')
        self.assertEqual(target, 'email')

    def test_t2f_prepare_declaration_classifies_as_declaration(self):
        intent, target = self._classify('Prepare a declaration about the parenting time facts')
        self.assertEqual(intent, 'drafting')
        self.assertEqual(target, 'declaration')


# =============================================================================
# T3 — BaseAgent._call_openai tool_choice propagation
# =============================================================================

class BaseAgentToolChoicePropagationTests(SimpleTestCase):
    """T3 + T3b — Rigby SIGN Fold 4 mitigation. Verify the tool_choice kwarg
    threads through _call_openai to the OpenAI create_kwargs without breaking
    prior 'auto' default behavior."""

    def _make_probe_agent(self):
        agent = LegalDocDrafterAgent.__new__(LegalDocDrafterAgent)
        # Minimal attrs — enough for _call_openai to construct create_kwargs.
        agent.name = 'ProbeAgent'
        agent.agent_name = 'ProbeAgent'
        agent.user = None
        agent.can_delegate = False
        agent._client = Mock()
        agent._current_delegation_context = {}
        agent._accumulated_cost = 0.0
        agent._accumulated_tokens = 0
        agent._health_check_mode = False
        agent.llm_timeout = 90.0
        # Bypass tools-selection / budget / streaming complexity — just want
        # to intercept the create_kwargs at _run_openai_create_with_total_cap.
        agent._get_tools_with_shared = Mock(return_value=[
            {'type': 'function', 'function': {'name': 'draft_motion'}},
        ])
        agent._get_execution_budget = Mock(return_value={'max_completion_tokens': 1000})
        return agent

    def _capture_kwargs(self, agent, tool_choice=None):
        captured = {}

        def _fake_call(sdk_fn, create_kwargs, cap, agent_name=None, **_):
            captured.update(create_kwargs)
            # Return a mock response with the shape _call_openai expects
            return Mock(
                choices=[Mock(message=Mock(content='ok', tool_calls=None))],
                usage=Mock(prompt_tokens=1, completion_tokens=1, total_tokens=2),
                model='gpt-5.2',
            )

        with patch(
            'core.agents.base_agent._run_openai_create_with_total_cap',
            side_effect=_fake_call,
        ):
            try:
                agent._call_openai('test prompt', tool_choice=tool_choice)
            except Exception:
                # We only need create_kwargs captured; downstream handling is
                # irrelevant for this test.
                pass
        return captured

    def test_t3_forced_tool_choice_dict_propagates(self):
        agent = self._make_probe_agent()
        forced = {'type': 'function', 'function': {'name': 'draft_motion'}}
        captured = self._capture_kwargs(agent, tool_choice=forced)
        self.assertEqual(captured.get('tool_choice'), forced,
                         'tool_choice dict override must reach OpenAI create_kwargs')

    def test_t3b_no_tool_choice_defaults_to_auto(self):
        agent = self._make_probe_agent()
        captured = self._capture_kwargs(agent, tool_choice=None)
        self.assertEqual(captured.get('tool_choice'), 'auto',
                         'default (None) must preserve prior "auto" behavior')


# =============================================================================
# T1 + T4 + T5 — Fallback save behavior (requires DB)
# =============================================================================

class LegalAgentFallbackSaveTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='legal_p3_1_test_s2804', password='x')

    def _run_execute_with_gpt_response(self, task, gpt_response):
        """Drive agent.execute() with a stubbed GPT response and return result."""
        agent = _make_agent(user=self.user)
        agent._call_openai = Mock(return_value=gpt_response)
        agent._execute_tool_call = Mock(side_effect=AssertionError(
            'should not run when GPT returns no tool_calls'
        ))
        return agent.execute(
            task=task,
            context={},
            scifi_context={},
            spider_context={},
        )

    def test_t1_chris_regression_content_only_gpt_produces_document(self):
        """The exact bug Chris hit at S2803 close browser test."""
        chris_task = (
            'Draft a motion to modify visitation to every weekend from every other weekend'
        )
        gpt_content = (
            '# MOTION TO MODIFY PARENTING TIME\n\n'
            'Placeholder motion body responding to Chris regression task.'
        )
        result = self._run_execute_with_gpt_response(
            chris_task,
            {'tool_calls': [], 'content': gpt_content},
        )
        self.assertTrue(result.success, result.error)

        # Fallback should have persisted a motion document for this drafting
        # intent, even without a tool_call.
        docs = LegalDocument.objects.filter(user=self.user, document_type='motion')
        self.assertEqual(docs.count(), 1,
                         'Chris regression: no LegalDocument was persisted — Phase 3.1 P0 regression')
        doc = docs.first()
        self.assertIn('MOTION TO MODIFY PARENTING TIME', doc.content)
        # Rigby SIGN B1 recovery marker in generation_context
        self.assertTrue(
            doc.generation_context.get('phase3_1_fallback_used'),
            'Fallback recovery marker missing — B1 requirement'
        )

    def test_t4_fallback_fires_for_drafting_intent_with_no_tool_doc(self):
        result = self._run_execute_with_gpt_response(
            'Draft a motion to modify parenting time',
            {'tool_calls': [], 'content': 'Motion body content here...'},
        )
        self.assertTrue(result.success)
        self.assertEqual(
            LegalDocument.objects.filter(user=self.user, document_type='motion').count(), 1
        )

    def test_t5_fallback_does_NOT_fire_for_info_intent(self):
        # Info query — even with content-only GPT response, no doc should be saved.
        result = self._run_execute_with_gpt_response(
            'What is the deadline for a motion to modify visitation?',
            {'tool_calls': [], 'content': 'The deadline is typically 14 days...'},
        )
        self.assertTrue(result.success)
        self.assertEqual(
            LegalDocument.objects.count(), 0,
            'Fallback fired for info intent — Fold 1 mitigation regression'
        )

    def test_t5b_fallback_does_NOT_fire_for_unknown_intent(self):
        result = self._run_execute_with_gpt_response(
            'Tell me about Colorado family law in general',
            {'tool_calls': [], 'content': 'Colorado family law covers...'},
        )
        self.assertTrue(result.success)
        self.assertEqual(
            LegalDocument.objects.count(), 0,
            'Fallback fired for unknown intent — over-triggering'
        )
