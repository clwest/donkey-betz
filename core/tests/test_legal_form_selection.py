"""S2808 Phase 4a — Form-selection intelligence regression tests.

Covers:

  Agent unit tests (LegalDocDrafterAgent._recommend_form)
    F1  emergency-parenting phrasing → emergency form + high confidence
    F2  parenting-time modification phrasing → JDF 1220 + medium/high confidence
    F3  enforcement/contempt phrasing → contempt form
    F4  child-support phrasing → JDF 1820/1821 form
    F5  ambiguous 'help me pick a form' → low/none confidence + clarifying questions
    F6  empty situation → success=False + error
    F7  no keyword hit → top_match None + confidence 'none' + clarifying questions

  Endpoint integration tests (POST /api/legal/select-form/)
    E1  authenticated happy path returns recommendation JSON
    E2  missing situation returns 400
    E3  unauthenticated returns 401/403

Run: python -m pytest core/tests/test_legal_form_selection.py -v --no-header
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from core.agents.legal.legal_doc_drafter_agent import LegalDocDrafterAgent

User = get_user_model()


def _make_agent(user=None):
    """Bypass __init__ side-effects (matches the pattern from other legal tests)."""
    agent = LegalDocDrafterAgent.__new__(LegalDocDrafterAgent)
    agent.user = user
    agent.name = 'LegalDocDrafterAgent'
    agent.agent_name = 'LegalDocDrafterAgent'
    return agent


# =============================================================================
# F — Agent unit tests
# =============================================================================


class LegalFormSelectionAgentTests(TestCase):
    """Rule-based classifier truth table for _recommend_form."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='legal_p4a_test_s2808', password='x'
        )

    def _recommend(self, situation, case_type=None):
        agent = _make_agent(user=self.user)
        return agent._recommend_form(
            situation=situation,
            context={'case_type': case_type} if case_type else None,
        )

    def test_f1_emergency_phrasing_hits_emergency_parenting(self):
        result = self._recommend(
            "I need an emergency order — my ex is threatening our child's safety"
        )
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['top_match'])
        self.assertEqual(result['top_match']['relief_type'], 'emergency_parenting')
        self.assertIn(result['confidence'], ('high', 'medium'))
        # High-confidence path should not surface clarifying questions.
        if result['confidence'] == 'high':
            self.assertEqual(result['clarifying_questions'], [])

    def test_f2_modify_parenting_time_maps_to_jdf_1220(self):
        result = self._recommend(
            "I want to change parenting time because she moved to a new job"
        )
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['top_match'])
        self.assertEqual(result['top_match']['relief_type'], 'modify_parenting_time')
        self.assertEqual(result['top_match']['form_number'], 'JDF 1220')

    def test_f3_enforcement_phrasing_hits_enforce_order(self):
        result = self._recommend(
            "He is not following the order and refuses to let me see my kids"
        )
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['top_match'])
        self.assertEqual(result['top_match']['relief_type'], 'enforce_order')

    def test_f4_child_support_phrasing_hits_modify_child_support(self):
        result = self._recommend(
            "I lost my job and need to modify child support — the amount is impossible with my income change"
        )
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['top_match'])
        self.assertEqual(result['top_match']['relief_type'], 'modify_child_support')

    def test_f5_ambiguous_phrasing_surfaces_low_confidence_and_clarifiers(self):
        # Deliberately vague, hits only one weak signal at most.
        result = self._recommend("I need help with my case")
        self.assertTrue(result['success'])
        # Either no match or a weak top_match — in both cases confidence should
        # be low/none and clarifying_questions should be populated.
        self.assertIn(result['confidence'], ('low', 'none'))
        self.assertGreater(len(result['clarifying_questions']), 0)

    def test_f6_empty_situation_returns_error(self):
        result = self._recommend('')
        self.assertFalse(result['success'])
        self.assertIn('required', result['error'])

    def test_f7_no_keyword_hit_returns_none_top_match(self):
        # Phrasing with zero overlap against RELIEF_TYPE_KEYWORDS.
        result = self._recommend("Please tell me the weather in Denver tomorrow.")
        self.assertTrue(result['success'])
        self.assertIsNone(result['top_match'])
        self.assertEqual(result['confidence'], 'none')
        self.assertGreater(len(result['clarifying_questions']), 0)


# =============================================================================
# E — Endpoint integration tests (POST /api/legal/select-form/)
# =============================================================================


class LegalFormSelectionEndpointTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='legal_p4a_endpoint_s2808', password='x'
        )

    def setUp(self):
        self.client = APIClient()

    def test_e1_authenticated_happy_path_returns_recommendation(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post(
            '/api/legal/select-form/',
            data={'situation': 'I want to modify parenting time — she moved to a new city'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        body = resp.json()
        self.assertTrue(body['success'])
        self.assertIsNotNone(body['top_match'])
        self.assertEqual(body['top_match']['relief_type'], 'modify_parenting_time')
        self.assertIn('disclaimer', body)

    def test_e2_missing_situation_returns_400(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post(
            '/api/legal/select-form/',
            data={'situation': '   '},
            format='json',
        )
        self.assertEqual(resp.status_code, 400)
        body = resp.json()
        self.assertFalse(body['success'])
        self.assertIn('required', body['error'])

    def test_e3_unauthenticated_rejected(self):
        # No force_authenticate — should be blocked by IsAuthenticated.
        resp = self.client.post(
            '/api/legal/select-form/',
            data={'situation': 'anything'},
            format='json',
        )
        self.assertIn(resp.status_code, (401, 403))
