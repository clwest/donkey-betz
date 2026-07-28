"""Session 3013 (U1): Mutation-path tests for BulkAttentionDecideView.

Extends the auth-regression contract from S2785 (test_decision_approve_auth_regression_2785.py)
which only covered auth blocking. This suite covers the actual mutation path — catching the
latent defect where the endpoint wrote invalid status values ('approved'/'rejected' are NOT
in HumanAttentionItem.STATUS_CHOICES) and to a nonexistent field ('handled_at').

Contract enforced by these tests:
* API accepts past-tense enum: 'approved' / 'ignored' / 'rejected'.
* Model persistence uses canonical enums:
  - approved/rejected → status=STATUS_ACTED, decision=DECISION_APPROVE/DECISION_REJECT
  - ignored → status=STATUS_IGNORED, decision=DECISION_IGNORE
* Uses decided_at (canonical field), not handled_at (doesn't exist).
* Only pending items are mutated (status filter preserved).
* User scope preserved (cross-user items untouched).
"""
from __future__ import annotations

import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from core.models_human_interface import HumanAttentionItem
from core.tests.helpers.token_auth import token_client_for


User = get_user_model()


def _make_staff(username: str) -> User:
    user = User.objects.create_user(username=username, email=f"{username}@example.com", password="test-pw")
    user.is_staff = True
    user.save(update_fields=["is_staff"])
    return user


def _make_item(user: User, urgency: str = "medium", item_type: str = "decision") -> HumanAttentionItem:
    return HumanAttentionItem.objects.create(
        user=user,
        source_type="test",
        source_id="test-source",
        source_agent="test-agent",
        item_type=item_type,
        title=f"Test item ({urgency})",
        summary="Body under test.",
        urgency=urgency,
        priority_score=1.0,
        status=HumanAttentionItem.STATUS_PENDING,
    )


class BulkAttentionDecideMutationTests(TestCase):
    """Mutation-path coverage for POST /api/human/attention/bulk-decide/."""

    def setUp(self) -> None:
        self.user = _make_staff("bulk_mut_user")
        self.other = _make_staff("bulk_mut_other")
        self.client = Client()
        self.client.force_login(self.user)

    def _post(self, payload: dict):
        return self.client.post(
            "/api/human/attention/bulk-decide/",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_approved_maps_to_acted_status_and_approve_decision(self) -> None:
        items = [_make_item(self.user) for _ in range(3)]
        response = self._post({"decision": "approved", "item_ids": [str(i.id) for i in items]})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["count"], 3)

        for item in items:
            item.refresh_from_db()
            self.assertEqual(item.status, HumanAttentionItem.STATUS_ACTED)
            self.assertEqual(item.decision, HumanAttentionItem.DECISION_APPROVE)
            self.assertIsNotNone(item.decided_at)

    def test_rejected_maps_to_acted_status_and_reject_decision(self) -> None:
        items = [_make_item(self.user) for _ in range(2)]
        response = self._post({"decision": "rejected", "item_ids": [str(i.id) for i in items]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)

        for item in items:
            item.refresh_from_db()
            self.assertEqual(item.status, HumanAttentionItem.STATUS_ACTED)
            self.assertEqual(item.decision, HumanAttentionItem.DECISION_REJECT)
            self.assertIsNotNone(item.decided_at)

    def test_ignored_maps_to_ignored_status_and_ignore_decision(self) -> None:
        items = [_make_item(self.user) for _ in range(2)]
        response = self._post({"decision": "ignored", "item_ids": [str(i.id) for i in items]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)

        for item in items:
            item.refresh_from_db()
            self.assertEqual(item.status, HumanAttentionItem.STATUS_IGNORED)
            self.assertEqual(item.decision, HumanAttentionItem.DECISION_IGNORE)
            self.assertIsNotNone(item.decided_at)

    def test_persisted_status_values_are_in_model_status_choices(self) -> None:
        """Regression: pre-fix code wrote status='approved'/'rejected' which violate STATUS_CHOICES."""
        item = _make_item(self.user)
        self._post({"decision": "approved", "item_ids": [str(item.id)]})
        item.refresh_from_db()
        valid_statuses = {choice for choice, _ in HumanAttentionItem.STATUS_CHOICES}
        self.assertIn(item.status, valid_statuses)

    def test_invalid_decision_returns_400(self) -> None:
        response = self._post({"decision": "approve", "item_ids": []})  # imperative form rejected
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_invalid_json_returns_400(self) -> None:
        response = self.client.post(
            "/api/human/attention/bulk-decide/",
            data="not-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_only_pending_items_mutated(self) -> None:
        pending = _make_item(self.user)
        already_acted = _make_item(self.user)
        already_acted.status = HumanAttentionItem.STATUS_ACTED
        already_acted.decision = HumanAttentionItem.DECISION_REJECT
        already_acted.save(update_fields=["status", "decision"])

        response = self._post({"decision": "approved", "item_ids": [str(pending.id), str(already_acted.id)]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

        pending.refresh_from_db()
        already_acted.refresh_from_db()
        self.assertEqual(pending.status, HumanAttentionItem.STATUS_ACTED)
        self.assertEqual(pending.decision, HumanAttentionItem.DECISION_APPROVE)
        # Already-acted item unchanged
        self.assertEqual(already_acted.decision, HumanAttentionItem.DECISION_REJECT)

    def test_cross_user_items_untouched(self) -> None:
        mine = _make_item(self.user)
        theirs = _make_item(self.other)

        response = self._post({"decision": "approved", "item_ids": [str(mine.id), str(theirs.id)]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

        mine.refresh_from_db()
        theirs.refresh_from_db()
        self.assertEqual(mine.status, HumanAttentionItem.STATUS_ACTED)
        self.assertEqual(theirs.status, HumanAttentionItem.STATUS_PENDING)  # untouched

    def test_token_auth_reaches_bulk_decide_endpoint_parity(self) -> None:
        """S3016 Fold E: Token-auth (React frontend) must reach BulkAttentionDecideView.

        Same regression class as the S3015 hotfix — a PUBLIC_PATHS bare prefix
        matching `/api/human/attention/` would silently drop Token-auth callers
        to AnonymousUser, so cross-user scoping would leave `mine.count() == 0`
        and this mutation would appear to succeed on nothing. Session-auth
        tests above would not surface it.
        """
        items = [_make_item(self.user) for _ in range(2)]
        token_client = token_client_for(self.user)
        response = token_client.post(
            "/api/human/attention/bulk-decide/",
            data=json.dumps({"decision": "approved", "item_ids": [str(i.id) for i in items]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["count"], 2)
        for item in items:
            item.refresh_from_db()
            self.assertEqual(item.status, HumanAttentionItem.STATUS_ACTED)
            self.assertEqual(item.decision, HumanAttentionItem.DECISION_APPROVE)
