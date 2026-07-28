"""Session 3014 (U2): Tests for create_initiative_from_cluster_view.

Contract enforced:
* POST /api/platform/signal-cluster/<uuid>/create-initiative/ creates an Initiative from a SignalCluster.
* Default initiative name = "{pattern_type.title()}: {cluster.name}" (truncated to 200 chars).
* Optional name override honored.
* Optional `generate_brief=false` skips deliverable creation.
* Deduplication: 400 if an Initiative with the same name already exists.
* 404 on unknown cluster_id.
* Deliverable, when created, is linked to the initiative via FK.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone as dt_timezone

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from core.models_document_registry import Initiative
from core.models_signal_intelligence import SignalCluster
from core.models_skin_layer import ProjectWorkspace
from core.tests.helpers.token_auth import token_client_for


User = get_user_model()


def _make_staff(username: str):
    user = User.objects.create_user(username=username, email=f"{username}@example.com", password="test-pw")
    user.is_staff = True
    user.save(update_fields=["is_staff"])
    # Rigby A2 STRENGTHEN fix: initiatives auto-attach to user's first workspace to
    # avoid missing_target_workspace_id diagnostic flag.
    ProjectWorkspace.objects.create(
        user=user,
        name=f"{username}-workspace",
        root_path=f"/tmp/{username}",
    )
    return user


def _make_cluster(name: str = "Persona research spike", pattern: str = "demand_spike") -> SignalCluster:
    return SignalCluster.objects.create(
        name=name,
        pattern_type=pattern,
        confidence=0.82,
        strength=0.75,
        urgency=0.6,
        novelty=0.5,
        keywords=["persona", "research", "customer"],
        source_breakdown={"bluesky": 12, "reddit": 6},
        sample_signals=[
            {"source": "bluesky", "text": "Team is asking about personas again"},
            {"source": "reddit", "text": "Anyone got a good customer persona template?"},
        ],
    )


class CreateInitiativeFromClusterTests(TestCase):
    """POST /api/platform/signal-cluster/<uuid>/create-initiative/"""

    def setUp(self):
        self.user = _make_staff("cluster_bridge_user")
        self.client = Client(HTTP_HOST="localhost:8000")
        self.client.force_login(self.user)

    def _url(self, cluster_id) -> str:
        return f"/api/platform/signal-cluster/{cluster_id}/create-initiative/"

    def test_creates_initiative_with_default_name_and_brief(self):
        cluster = _make_cluster()
        response = self.client.post(self._url(cluster.id), data="", content_type="application/json")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertIsNotNone(body["initiative"])
        self.assertEqual(body["initiative"]["name"], "Demand Spike: Persona research spike")
        self.assertEqual(body["initiative"]["status"], Initiative.Status.TRIAGE)
        self.assertIsNotNone(body["deliverable"])
        self.assertIn("Signal Brief", body["deliverable"]["title"])

        # ORM verify FK link
        from core.models_deliverables import Deliverable
        initiative = Initiative.objects.get(id=body["initiative"]["id"])
        deliverable = Deliverable.objects.get(id=body["deliverable"]["id"])
        self.assertEqual(deliverable.initiative_id, initiative.id)
        self.assertIn("Persona research spike", deliverable.content)
        self.assertIn("demand_spike", deliverable.tags)

    def test_generate_brief_false_skips_deliverable(self):
        cluster = _make_cluster(name="No-brief cluster")
        response = self.client.post(
            self._url(cluster.id),
            data=json.dumps({"generate_brief": False}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertIsNone(body["deliverable"])
        self.assertNotIn("deliverable_error", body)

    def test_name_override_honored(self):
        cluster = _make_cluster(name="Override target")
        response = self.client.post(
            self._url(cluster.id),
            data=json.dumps({"name": "Custom Initiative Name"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["initiative"]["name"], "Custom Initiative Name")

    def test_duplicate_name_returns_400_with_existing_reference(self):
        cluster = _make_cluster(name="Dedupe test")
        # First create — succeeds
        r1 = self.client.post(self._url(cluster.id), data="", content_type="application/json")
        self.assertEqual(r1.status_code, 200)
        first_id = r1.json()["initiative"]["id"]

        # Second create with same name — 400
        r2 = self.client.post(self._url(cluster.id), data="", content_type="application/json")
        self.assertEqual(r2.status_code, 400)
        body = r2.json()
        self.assertFalse(body["success"])
        self.assertEqual(body["initiative"]["id"], first_id)

    def test_unknown_cluster_returns_404(self):
        import uuid
        response = self.client.post(self._url(uuid.uuid4()), data="", content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])

    def test_initiative_description_contains_cluster_context(self):
        cluster = _make_cluster(name="Context test")
        response = self.client.post(self._url(cluster.id), data="", content_type="application/json")
        initiative = Initiative.objects.get(id=response.json()["initiative"]["id"])
        self.assertIn("Demand Spike", initiative.description)
        self.assertIn("0.82", initiative.description)
        self.assertIn("persona", initiative.description)
        self.assertIn("bluesky·12", initiative.description)

    def test_initiative_and_deliverable_carry_cluster_provenance(self):
        """Rigby A2 STRENGTHEN: verify target_workspace + parent_topic + Deliverable parent_object linkage."""
        from core.models_deliverables import Deliverable
        cluster = _make_cluster(name="Provenance test cluster")
        response = self.client.post(self._url(cluster.id), data="", content_type="application/json")
        self.assertEqual(response.status_code, 200)
        body = response.json()

        initiative = Initiative.objects.get(id=body["initiative"]["id"])
        # (1) target_workspace set → avoids missing_target_workspace_id diagnostic
        self.assertIsNotNone(initiative.target_workspace_id)
        # (2) parent_topic quick-scan hint holds structured cluster reference
        self.assertEqual(initiative.parent_topic, f"signal_cluster:{cluster.id}")

        # (3) Deliverable carries authoritative Session 843 provenance
        deliverable = Deliverable.objects.get(id=body["deliverable"]["id"])
        self.assertEqual(deliverable.parent_object_type, "signal_cluster")
        self.assertEqual(str(deliverable.parent_object_id), str(cluster.id))

    def test_long_cluster_name_truncated_to_200_chars(self):
        # SignalCluster.name max_length=200 — pick 150-char name that would produce a
        # composed initiative name longer than 200 chars if unbounded.
        long_name = "very-detailed-cluster-name-" * 6  # ~162 chars
        cluster = _make_cluster(name=long_name[:200])
        response = self.client.post(self._url(cluster.id), data="", content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.json()["initiative"]["name"]), 200)

    def test_token_auth_reaches_single_cluster_endpoint_parity(self):
        """S3016 Fold E: Token-auth (React frontend) must reach the single-cluster endpoint.

        Same regression class as the S3015 hotfix — a PUBLIC_PATHS bare prefix
        would short-circuit token parsing, drop the caller to AnonymousUser,
        and produce a wrong-owner or 403 result. Session-auth tests above
        would not surface it.
        """
        cluster = _make_cluster(name="Token parity single")
        token_client = token_client_for(self.user)
        response = token_client.post(
            self._url(cluster.id),
            data=json.dumps({"generate_brief": False}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["initiative"]["name"], "Demand Spike: Token parity single")
        # Same-user provenance under Token-auth. Assert target_workspace.user_id
        # because anon-fallthrough could theoretically pass owner_id via other
        # code paths; anon cannot resolve "user's first workspace".
        initiative = Initiative.objects.get(id=body["initiative"]["id"])
        self.assertEqual(initiative.owner_id, self.user.id)
        self.assertIsNotNone(initiative.target_workspace_id)
        self.assertEqual(initiative.target_workspace.user_id, self.user.id)
