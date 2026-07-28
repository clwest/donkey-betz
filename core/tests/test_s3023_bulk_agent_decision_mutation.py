"""Session 3023 U4-H: Mutation-path tests for AgentDecisionSummary bulk endpoints.

The capability shipped in S942 (`bulk_promote_decisions` + `bulk_reject_decisions`
at `core/views_agent_learning.py`). Auth blocking was covered by S2785
(`test_decision_approve_auth_regression_2785.py`) and CSRF exemption by S2787
(`test_csrf_enforcement_2787.py`). Neither exercised the write path, so a
latent defect on bulk-reject (stale `updated_at` because `queryset.update()`
bypasses Django's `auto_now=True`) shipped alongside the endpoint.

This suite closes that gap for both endpoints and pins Fix A
(`updated_at=timezone.now()` passed explicitly to `bulk_reject_decisions`'
`queryset.update()` call). Mirrors the S3013 (U1) shape for
BulkAttentionDecideView.
"""
from __future__ import annotations

import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils import timezone

from core.models_unified_system import AgentDecisionSummary
from core.tests.helpers.token_auth import token_client_for


User = get_user_model()


def _make_staff(username: str) -> "User":
    user = User.objects.create_user(
        username=username, email=f"{username}@example.com", password="test-pw"
    )
    user.is_staff = True
    user.save(update_fields=["is_staff"])
    return user


def _make_draft(
    *, topic: str = "Draft", decision_type: str = "product", impact_area: str = "agents",
    status: str = "draft",
) -> AgentDecisionSummary:
    return AgentDecisionSummary.objects.create(
        conversation=None,
        hive_session=None,
        topic=topic,
        decision_type=decision_type,
        impact_area=impact_area,
        recommended_stance="A stance",
        status=status,
    )


class BulkPromoteDecisionsMutationTests(TestCase):
    """POST /api/boardroom/decisions/bulk-promote/."""

    URL = "/api/boardroom/decisions/bulk-promote/"

    def setUp(self) -> None:
        self.user = _make_staff("bulk_ads_promote")
        self.client = Client()
        self.client.force_login(self.user)

    def _post(self, payload: dict):
        return self.client.post(self.URL, data=json.dumps(payload), content_type="application/json")

    def test_bulk_promote_sets_canonical_status_and_is_canonical_and_promoted_at(self) -> None:
        drafts = [_make_draft(topic=f"D{i}") for i in range(3)]
        response = self._post({"decision_ids": [str(d.id) for d in drafts]})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["count"], 3)

        for d in drafts:
            d.refresh_from_db()
            self.assertEqual(d.status, "canonical")
            self.assertTrue(d.is_canonical)
            self.assertIsNotNone(d.promoted_at)
            self.assertEqual(d.promoted_by, "human-bulk")

    def test_bulk_promote_only_touches_draft_status(self) -> None:
        draft = _make_draft(topic="draft-row")
        already_canonical = _make_draft(topic="already", status="canonical")

        response = self._post(
            {"decision_ids": [str(draft.id), str(already_canonical.id)]}
        )
        self.assertEqual(response.status_code, 200)
        # Only the draft was in the filtered queryset (status='draft').
        self.assertEqual(response.json()["count"], 1)

        draft.refresh_from_db()
        already_canonical.refresh_from_db()
        self.assertEqual(draft.status, "canonical")
        # already-canonical row's status was NOT re-written and promoted_by stays None.
        self.assertEqual(already_canonical.status, "canonical")
        self.assertIsNone(already_canonical.promoted_at)

    def test_bulk_promote_by_decision_type_filter(self) -> None:
        product = [_make_draft(topic=f"p{i}", decision_type="product") for i in range(2)]
        experiment = _make_draft(topic="e0", decision_type="experiment")

        response = self._post({"decision_type": "product"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)

        for d in product:
            d.refresh_from_db()
            self.assertEqual(d.status, "canonical")

        experiment.refresh_from_db()
        self.assertEqual(experiment.status, "draft")  # unaffected by filter

    def test_bulk_promote_missing_ids_and_type_returns_400(self) -> None:
        response = self._post({})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_bulk_promote_invalid_json_returns_400(self) -> None:
        response = self.client.post(self.URL, data="not-json", content_type="application/json")
        self.assertEqual(response.status_code, 400)


class BulkRejectDecisionsMutationTests(TestCase):
    """POST /api/boardroom/decisions/bulk-reject/."""

    URL = "/api/boardroom/decisions/bulk-reject/"

    def setUp(self) -> None:
        self.user = _make_staff("bulk_ads_reject")
        self.client = Client()
        self.client.force_login(self.user)

    def _post(self, payload: dict):
        return self.client.post(self.URL, data=json.dumps(payload), content_type="application/json")

    def test_bulk_reject_sets_rejected_status_and_touches_updated_at(self) -> None:
        """S3023 U4-H Fix A regression: queryset.update() must move updated_at.

        Django's auto_now=True is only applied on .save(); it is silently bypassed
        by .update(). Prior code left updated_at stale on bulk-rejected rows,
        distorting audit trails and ordering-by-updated_at views.
        """
        drafts = [_make_draft(topic=f"R{i}") for i in range(2)]
        # Rewind updated_at on both rows so the endpoint MUST move it forward
        # for the regression to pass.
        stale = timezone.now() - timedelta(hours=6)
        AgentDecisionSummary.objects.filter(id__in=[d.id for d in drafts]).update(updated_at=stale)

        response = self._post({"decision_ids": [str(d.id) for d in drafts]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)

        for d in drafts:
            d.refresh_from_db()
            self.assertEqual(d.status, "rejected")
            self.assertGreater(d.updated_at, stale)

    def test_bulk_reject_only_touches_draft_status(self) -> None:
        draft = _make_draft(topic="draft-r")
        already_canonical = _make_draft(topic="already-r", status="canonical")

        response = self._post(
            {"decision_ids": [str(draft.id), str(already_canonical.id)]}
        )
        self.assertEqual(response.status_code, 200)
        # Only the draft was in the queryset (status='draft').
        self.assertEqual(response.json()["count"], 1)

        draft.refresh_from_db()
        already_canonical.refresh_from_db()
        self.assertEqual(draft.status, "rejected")
        self.assertEqual(already_canonical.status, "canonical")  # untouched

    def test_bulk_reject_missing_ids_and_type_returns_400(self) -> None:
        response = self._post({})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_bulk_reject_invalid_json_returns_400(self) -> None:
        response = self.client.post(self.URL, data="not-json", content_type="application/json")
        self.assertEqual(response.status_code, 400)


class BulkDecisionsTokenAuthParityTests(TestCase):
    """S3016 Fold E parity: Token-auth (React frontend) must reach the bulk endpoints.

    /api/boardroom/ is in PUBLIC_PATHS; auth is enforced manually by
    `_require_boardroom_staff`, which parses `Authorization: Token …`. Session-auth
    tests above would not surface a regression that broke that fallback (identical
    class of bug to the S3015 Initiatives hotfix that motivated the helper).
    """

    def setUp(self) -> None:
        self.user = _make_staff("bulk_ads_token")

    def test_bulk_promote_reachable_via_token_auth(self) -> None:
        drafts = [_make_draft(topic=f"tp{i}") for i in range(2)]
        client = token_client_for(self.user)
        response = client.post(
            "/api/boardroom/decisions/bulk-promote/",
            data=json.dumps({"decision_ids": [str(d.id) for d in drafts]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)
        for d in drafts:
            d.refresh_from_db()
            self.assertEqual(d.status, "canonical")

    def test_bulk_reject_reachable_via_token_auth(self) -> None:
        drafts = [_make_draft(topic=f"tr{i}") for i in range(2)]
        client = token_client_for(self.user)
        response = client.post(
            "/api/boardroom/decisions/bulk-reject/",
            data=json.dumps({"decision_ids": [str(d.id) for d in drafts]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)
        for d in drafts:
            d.refresh_from_db()
            self.assertEqual(d.status, "rejected")
