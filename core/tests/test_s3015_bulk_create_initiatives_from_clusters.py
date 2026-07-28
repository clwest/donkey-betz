"""Session 3015 (U3): Tests for bulk_create_initiatives_from_clusters_view.

Extends S3014 (U2) single-cluster contract to N-at-once. Parallels S3013 U1
BulkAttentionDecideView shape.

Contract enforced:
* POST /api/platform/signal-cluster/bulk-create-initiative/ accepts {cluster_ids: [...]}.
* Returns 200 for well-formed requests (partial failures are per-row).
* Per-row error semantics: initiative failure = row failure; brief failure = warning.
* Summary counts: {requested, succeeded, failed, briefs_requested, briefs_succeeded, briefs_failed}.
* Preserves request order + de-dupes within request.
* generate_brief=false skips all briefs.
* 400 on missing/empty cluster_ids or invalid JSON.
"""
from __future__ import annotations

import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from core.models_document_registry import Initiative
from core.models_signal_intelligence import SignalCluster
from core.models_skin_layer import ProjectWorkspace
from core.tests.helpers.token_auth import token_client_for


User = get_user_model()

BULK_URL = "/api/platform/signal-cluster/bulk-create-initiative/"


def _make_staff(username: str):
    user = User.objects.create_user(username=username, email=f"{username}@example.com", password="test-pw")
    user.is_staff = True
    user.save(update_fields=["is_staff"])
    ProjectWorkspace.objects.create(
        user=user,
        name=f"{username}-workspace",
        root_path=f"/tmp/{username}",
    )
    return user


def _make_cluster(name: str, pattern: str = "demand_spike") -> SignalCluster:
    return SignalCluster.objects.create(
        name=name,
        pattern_type=pattern,
        confidence=0.75,
        strength=0.7,
        urgency=0.5,
        novelty=0.5,
        keywords=["kw1", "kw2"],
        source_breakdown={"bluesky": 3},
        sample_signals=[{"source": "bluesky", "text": "sample"}],
    )


class BulkCreateInitiativesFromClustersTests(TestCase):
    def setUp(self):
        self.user = _make_staff("bulk_cluster_user")
        self.client = Client(HTTP_HOST="localhost:8000")
        self.client.force_login(self.user)

    def _post(self, payload):
        return self.client.post(BULK_URL, data=json.dumps(payload), content_type="application/json")

    def test_bulk_creates_multiple_initiatives_with_briefs(self):
        clusters = [_make_cluster(f"Bulk cluster {i}") for i in range(3)]
        response = self._post({"cluster_ids": [str(c.id) for c in clusters]})
        self.assertEqual(response.status_code, 200)
        body = response.json()

        self.assertTrue(body["success"])
        self.assertEqual(body["summary"]["requested"], 3)
        self.assertEqual(body["summary"]["succeeded"], 3)
        self.assertEqual(body["summary"]["failed"], 0)
        self.assertEqual(body["summary"]["briefs_succeeded"], 3)
        self.assertEqual(len(body["results"]), 3)

        for cluster, row in zip(clusters, body["results"]):
            self.assertEqual(row["cluster_id"], str(cluster.id))
            self.assertIsNotNone(row["initiative"])
            self.assertIsNotNone(row["deliverable"])
            self.assertNotIn("error", row)

        # ORM verify all initiatives exist with correct provenance
        for cluster in clusters:
            initiative = Initiative.objects.get(parent_topic=f"signal_cluster:{cluster.id}")
            self.assertEqual(initiative.status, Initiative.Status.TRIAGE)
            self.assertIsNotNone(initiative.target_workspace_id)

    def test_generate_brief_false_skips_all_briefs(self):
        clusters = [_make_cluster(f"No-brief cluster {i}") for i in range(2)]
        response = self._post({
            "cluster_ids": [str(c.id) for c in clusters],
            "generate_brief": False,
        })
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["summary"]["succeeded"], 2)
        self.assertEqual(body["summary"]["briefs_requested"], 0)
        self.assertEqual(body["summary"]["briefs_succeeded"], 0)
        for row in body["results"]:
            self.assertIsNone(row["deliverable"])

    def test_partial_failure_unknown_cluster_reported_per_row(self):
        real = _make_cluster("Real cluster")
        import uuid
        fake_id = str(uuid.uuid4())
        response = self._post({"cluster_ids": [str(real.id), fake_id]})
        self.assertEqual(response.status_code, 200)
        body = response.json()

        self.assertEqual(body["summary"]["requested"], 2)
        self.assertEqual(body["summary"]["succeeded"], 1)
        self.assertEqual(body["summary"]["failed"], 1)

        # Preserves order
        self.assertEqual(body["results"][0]["cluster_id"], str(real.id))
        self.assertIsNotNone(body["results"][0]["initiative"])
        self.assertEqual(body["results"][1]["cluster_id"], fake_id)
        self.assertIn("not found", body["results"][1]["error"].lower())

    def test_partial_failure_dedupe_hit_reported_per_row(self):
        cluster = _make_cluster("Dedupe target")
        # Pre-create initiative with the exact name the core helper will pick
        Initiative.objects.create(
            name=f"Demand Spike: {cluster.name}",
            description="already here",
            status=Initiative.Status.ACTIVE,
            owner=self.user,
            target_workspace=ProjectWorkspace.objects.filter(user=self.user).first(),
        )
        # Now request bulk with two clusters (one dedupe hit, one fresh)
        fresh = _make_cluster("Fresh dedupe test")
        response = self._post({"cluster_ids": [str(cluster.id), str(fresh.id)]})
        self.assertEqual(response.status_code, 200)
        body = response.json()

        self.assertEqual(body["summary"]["succeeded"], 1)
        self.assertEqual(body["summary"]["failed"], 1)

        # Row for dedupe hit has error + existing_initiative pointer
        dedupe_row = next(r for r in body["results"] if r["cluster_id"] == str(cluster.id))
        self.assertIn("already exists", dedupe_row["error"].lower())
        self.assertIn("existing_initiative", dedupe_row)

    def test_dedupes_ids_within_request(self):
        cluster = _make_cluster("Dupe id test")
        cid = str(cluster.id)
        response = self._post({"cluster_ids": [cid, cid, cid]})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["summary"]["requested"], 1)  # after de-dup
        self.assertEqual(body["summary"]["succeeded"], 1)
        self.assertEqual(len(body["results"]), 1)

    def test_empty_cluster_ids_returns_400(self):
        response = self._post({"cluster_ids": []})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_missing_cluster_ids_returns_400(self):
        response = self._post({"generate_brief": True})
        self.assertEqual(response.status_code, 400)

    def test_invalid_json_returns_400(self):
        response = self.client.post(BULK_URL, data="not json", content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_bulk_cluster_limit_enforced(self):
        """Rigby A2 zoom-out: max batch size cap prevents accidental huge selections."""
        import uuid
        fake_ids = [str(uuid.uuid4()) for _ in range(101)]
        response = self._post({"cluster_ids": fake_ids})
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertFalse(body["success"])
        self.assertIn("max batch size", body["error"].lower())

    def test_preserves_request_order(self):
        clusters = [_make_cluster(f"Order {i}") for i in range(5)]
        cluster_ids = [str(c.id) for c in clusters]
        response = self._post({"cluster_ids": cluster_ids})
        body = response.json()
        returned_order = [r["cluster_id"] for r in body["results"]]
        self.assertEqual(returned_order, cluster_ids)

    def test_token_auth_reaches_bulk_endpoint_parity(self):
        """S3016 Fold E: Token-auth (React frontend) must reach this endpoint.

        Regression guard for the S3015 hotfix class — a bare-prefix entry in
        UnifiedTokenAuthenticationMiddleware.PUBLIC_PATHS would short-circuit
        before token parsing, drop the caller to AnonymousUser, and produce
        a 403 or empty result. Session-auth (force_login, see other tests)
        would not surface the regression.
        """
        clusters = [_make_cluster(f"Token parity {i}") for i in range(2)]
        cluster_ids = [str(c.id) for c in clusters]
        token_client = token_client_for(self.user)
        response = token_client.post(
            BULK_URL,
            data=json.dumps({"cluster_ids": cluster_ids, "generate_brief": False}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["summary"]["requested"], 2)
        self.assertEqual(body["summary"]["succeeded"], 2)
        # Provenance goes to the same user's workspace under Token-auth.
        # Assert target_workspace.user_id — anon-fallthrough could pass
        # owner_id via other code paths; anon cannot resolve the user's
        # first workspace.
        for cluster in clusters:
            initiative = Initiative.objects.get(parent_topic=f"signal_cluster:{cluster.id}")
            self.assertEqual(initiative.owner_id, self.user.id)
            self.assertIsNotNone(initiative.target_workspace_id)
            self.assertEqual(initiative.target_workspace.user_id, self.user.id)
