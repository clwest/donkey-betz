"""PaMessageFeedback Endpoint — Regression Tests

Session 1243: rebuilds the stillborn endpoint from Session 1085 (URL+view
existed since S1085, but the model + migration were never created — every
POST 500'd with "relation does not exist").

Endpoint contract:
  POST /api/pa/feedback/
    body: {conversation_id, message_index, rating, note?}
    auth: required (IsAuthenticated)
    rating: must be +1 (thumbs up) or -1 (thumbs down)
    behavior: upsert keyed on (user, conversation_id, message_index)

Run: python manage.py test core.tests.test_pa_message_feedback -v2
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import PaMessageFeedback

User = get_user_model()


class PaMessageFeedbackEndpointTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='pa_fb_test', password='x')
        cls.other = User.objects.create_user(username='pa_fb_other', password='x')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = '/api/pa/feedback/'

    def test_post_thumbs_up_creates_row(self):
        resp = self.client.post(
            self.url,
            {'conversation_id': 'pa-test1', 'message_index': 2, 'rating': 1, 'note': 'helpful'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['rating'], 1)

        row = PaMessageFeedback.objects.get(
            user=self.user, conversation_id_str='pa-test1', message_index=2
        )
        self.assertEqual(row.rating, 1)
        self.assertEqual(row.note, 'helpful')
        self.assertEqual(str(row.id), data['id'])

    def test_post_thumbs_down_creates_row(self):
        resp = self.client.post(
            self.url,
            {'conversation_id': 'pa-test2', 'message_index': 5, 'rating': -1, 'note': 'wrong'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        row = PaMessageFeedback.objects.get(
            user=self.user, conversation_id_str='pa-test2', message_index=5
        )
        self.assertEqual(row.rating, -1)

    def test_invalid_rating_400(self):
        for bad in (0, 2, -2, 'up', None):
            resp = self.client.post(
                self.url,
                {'conversation_id': 'pa-x', 'message_index': 0, 'rating': bad},
                format='json',
            )
            self.assertEqual(resp.status_code, 400, f'rating={bad!r} should 400')
            self.assertIn('error', resp.json())

    def test_unauthenticated_blocked(self):
        anon = APIClient()
        resp = anon.post(
            self.url,
            {'conversation_id': 'pa-y', 'message_index': 0, 'rating': 1},
            format='json',
        )
        self.assertIn(resp.status_code, (401, 403))

    def test_resubmit_updates_in_place(self):
        # First submit: thumbs up
        r1 = self.client.post(
            self.url,
            {'conversation_id': 'pa-up', 'message_index': 7, 'rating': 1, 'note': 'good'},
            format='json',
        )
        self.assertEqual(r1.status_code, 200)
        first_id = r1.json()['id']

        # Resubmit: thumbs down + new note
        r2 = self.client.post(
            self.url,
            {'conversation_id': 'pa-up', 'message_index': 7, 'rating': -1, 'note': 'changed mind'},
            format='json',
        )
        self.assertEqual(r2.status_code, 200)

        # Same row, updated values, NOT duplicated
        rows = PaMessageFeedback.objects.filter(
            user=self.user, conversation_id_str='pa-up', message_index=7
        )
        self.assertEqual(rows.count(), 1)
        row = rows.first()
        self.assertEqual(row.rating, -1)
        self.assertEqual(row.note, 'changed mind')
        self.assertEqual(str(row.id), first_id)  # same row, same id

    def test_different_users_independent(self):
        # Same conversation_id + message_index, different users → two rows
        self.client.post(
            self.url,
            {'conversation_id': 'pa-shared', 'message_index': 1, 'rating': 1},
            format='json',
        )
        other_client = APIClient()
        other_client.force_authenticate(user=self.other)
        other_client.post(
            self.url,
            {'conversation_id': 'pa-shared', 'message_index': 1, 'rating': -1},
            format='json',
        )
        rows = PaMessageFeedback.objects.filter(
            conversation_id_str='pa-shared', message_index=1
        )
        self.assertEqual(rows.count(), 2)
