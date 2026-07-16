"""Legal endpoints — cross-user access regression tests (S2802 Phase 1).

Covers the 4 view functions refactored to scoped `.filter(id=X, case_profile__user=user).first()`:
  - POST /api/legal/litigation/<document_id>/generate-response/  → generate_response_to_filing
  - GET  /api/legal/litigation/document/<document_id>/thread/     → get_document_thread
  - GET  /api/legal/litigation/response/<response_id>/            → get_generated_response
  - POST /api/legal/litigation/response/<response_id>/package/    → create_filing_package

Prior implementation did unscoped `.objects.get(id=...)` + post-hoc `if doc.case_profile.user != user`.
Defense-in-depth, not exploit, but fragile against refactor. New implementation forbids the
lookup at query time.

Run: python manage.py test core.tests.test_legal_cross_user_access -v2
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models_legal import CaseProfile, GeneratedResponse, LitigationDocument

User = get_user_model()


class LegalCrossUserAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='legal_owner_s2802', password='x')
        cls.intruder = User.objects.create_user(username='legal_intruder_s2802', password='x')

        cls.case = CaseProfile.objects.create(
            user=cls.owner,
            case_number='2026DR-TEST-1',
            case_type='custody',
            county='Denver',
            state='Colorado',
        )
        cls.doc = LitigationDocument.objects.create(
            case_profile=cls.case,
            category='motion',
            document_type='opposing_motion',
            filing_party='opposing_party',
            litigation_role='opposing_filing',
            title='Test Opposing Motion',
        )
        cls.response = GeneratedResponse.objects.create(
            case_profile=cls.case,
            responds_to=cls.doc,
            response_content='Test response content',
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.intruder)

    def test_generate_response_to_filing_rejects_cross_user(self):
        resp = self.client.post(
            f'/api/legal/litigation/{self.doc.id}/generate-response/'
        )
        self.assertEqual(resp.status_code, 404, resp.content)
        body = resp.json()
        self.assertFalse(body.get('success'))
        # Regression: writer.generate_response(doc) MUST NOT run for intruder →
        # no new GeneratedResponse row got created for owner's case
        self.assertEqual(
            GeneratedResponse.objects.filter(case_profile=self.case).count(),
            1,
            'generate_response service ran despite unauthenticated caller',
        )

    def test_get_document_thread_rejects_cross_user(self):
        resp = self.client.get(
            f'/api/legal/litigation/document/{self.doc.id}/thread/'
        )
        self.assertEqual(resp.status_code, 404, resp.content)
        body = resp.json()
        self.assertFalse(body.get('success'))
        # 404 body must not leak thread/chain data
        self.assertNotIn('thread', body)
        self.assertNotIn('chain', body)

    def test_get_generated_response_rejects_cross_user(self):
        resp = self.client.get(
            f'/api/legal/litigation/response/{self.response.id}/'
        )
        self.assertEqual(resp.status_code, 404, resp.content)
        body = resp.json()
        self.assertFalse(body.get('success'))
        self.assertNotIn('response', body)

    def test_create_filing_package_rejects_cross_user(self):
        resp = self.client.post(
            f'/api/legal/litigation/response/{self.response.id}/package/',
            {'formats': ['docx', 'txt']},
            format='json',
        )
        self.assertEqual(resp.status_code, 404, resp.content)
        body = resp.json()
        self.assertFalse(body.get('success'))
        self.assertNotIn('package', body)

    def test_owner_generate_response_reaches_service_boundary(self):
        # Positive path — owner passes ownership check + reaches
        # writer.generate_response(doc). The service call may error downstream
        # (no LLM in tests), but the response must NOT be a 404 from the
        # ownership check.
        self.client.force_authenticate(user=self.owner)
        resp = self.client.post(
            f'/api/legal/litigation/{self.doc.id}/generate-response/'
        )
        self.assertNotEqual(resp.status_code, 404, resp.content)

    def test_owner_get_document_thread_reaches_model_method(self):
        self.client.force_authenticate(user=self.owner)
        resp = self.client.get(
            f'/api/legal/litigation/document/{self.doc.id}/thread/'
        )
        self.assertNotEqual(resp.status_code, 404, resp.content)

    def test_owner_get_generated_response_returns_200(self):
        self.client.force_authenticate(user=self.owner)
        resp = self.client.get(
            f'/api/legal/litigation/response/{self.response.id}/'
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        body = resp.json()
        self.assertTrue(body['success'])
        self.assertEqual(body['response']['id'], str(self.response.id))

    def test_unknown_id_returns_404(self):
        # An ID that doesn't exist at all also 404s (same shape as cross-user)
        # — no information leak between "not owned" and "doesn't exist".
        import uuid
        fake_id = uuid.uuid4()
        self.client.force_authenticate(user=self.owner)

        for path in [
            f'/api/legal/litigation/{fake_id}/generate-response/',
            f'/api/legal/litigation/document/{fake_id}/thread/',
            f'/api/legal/litigation/response/{fake_id}/',
            f'/api/legal/litigation/response/{fake_id}/package/',
        ]:
            method = self.client.post if path.endswith(('response/', 'package/')) else self.client.get
            resp = method(path)
            self.assertEqual(resp.status_code, 404, f'{path} → {resp.status_code}\n{resp.content}')
