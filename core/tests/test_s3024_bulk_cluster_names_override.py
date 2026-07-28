"""Session 3024 (U6): Per-row name override for bulk cluster → initiative promotion.

Extends S3015 (U3) `bulk_create_initiatives_from_clusters_view` with an
optional `names` dict keyed by cluster_id. Missing keys, empty strings, and
a non-dict `names` param all silently fall back to the backend default
(`{pattern_label}: {cluster.name}`), which core also 200-char-caps.

Rigby A1 REVISE: frontend always sends the full `names` dict so the final
name is never inferred from "did the UI diff against a default" — this
suite pins the invariant that the endpoint is keyed by cluster_id, not by
list position (so cluster_ids order need not match `names` insertion order).
"""
from __future__ import annotations

import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from core.models_document_registry import Initiative
from core.models_signal_intelligence import SignalCluster
from core.models_skin_layer import ProjectWorkspace


User = get_user_model()

BULK_URL = "/api/platform/signal-cluster/bulk-create-initiative/"


def _make_staff(username: str):
    user = User.objects.create_user(
        username=username, email=f"{username}@example.com", password="test-pw"
    )
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


class BulkClusterNamesOverrideTests(TestCase):
    def setUp(self):
        self.user = _make_staff("bulk_names_user")
        self.client = Client(HTTP_HOST="localhost:8000")
        self.client.force_login(self.user)

    def _post(self, payload):
        return self.client.post(BULK_URL, data=json.dumps(payload), content_type="application/json")

    def test_names_dict_overrides_default_per_row(self):
        c1 = _make_cluster("Cluster One")
        c2 = _make_cluster("Cluster Two")
        response = self._post({
            "cluster_ids": [str(c1.id), str(c2.id)],
            "names": {
                str(c1.id): "Custom name for one",
                str(c2.id): "Custom name for two",
            },
            "generate_brief": False,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["summary"]["succeeded"], 2)

        i1 = Initiative.objects.get(parent_topic=f"signal_cluster:{c1.id}")
        i2 = Initiative.objects.get(parent_topic=f"signal_cluster:{c2.id}")
        self.assertEqual(i1.name, "Custom name for one")
        self.assertEqual(i2.name, "Custom name for two")

    def test_missing_key_falls_back_to_default(self):
        """Sparse dict — only one row overridden, other row uses default."""
        c1 = _make_cluster("Sparse One")
        c2 = _make_cluster("Sparse Two")
        response = self._post({
            "cluster_ids": [str(c1.id), str(c2.id)],
            "names": {str(c1.id): "Overridden one"},
            "generate_brief": False,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["summary"]["succeeded"], 2)

        i1 = Initiative.objects.get(parent_topic=f"signal_cluster:{c1.id}")
        i2 = Initiative.objects.get(parent_topic=f"signal_cluster:{c2.id}")
        self.assertEqual(i1.name, "Overridden one")
        # Default = "Demand Spike: Sparse Two"
        self.assertEqual(i2.name, "Demand Spike: Sparse Two")

    def test_empty_string_falls_back_to_default(self):
        """A row explicitly set to '' still falls back to the default (matches core)."""
        c = _make_cluster("Empty Override")
        response = self._post({
            "cluster_ids": [str(c.id)],
            "names": {str(c.id): "   "},  # whitespace-only stripped by core
            "generate_brief": False,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["summary"]["succeeded"], 1)

        i = Initiative.objects.get(parent_topic=f"signal_cluster:{c.id}")
        self.assertEqual(i.name, "Demand Spike: Empty Override")

    def test_non_dict_names_param_gracefully_ignored(self):
        """A frontend bug sending names as a string / list must not 500."""
        c = _make_cluster("Non-Dict Names")
        response = self._post({
            "cluster_ids": [str(c.id)],
            "names": "oops-should-be-a-dict",
            "generate_brief": False,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["summary"]["succeeded"], 1)

        i = Initiative.objects.get(parent_topic=f"signal_cluster:{c.id}")
        self.assertEqual(i.name, "Demand Spike: Non-Dict Names")

    def test_long_per_row_name_truncated_to_200_chars(self):
        """Frontend maxLength mirrors backend cap; endpoint enforces regardless."""
        c = _make_cluster("Long-name row")
        long_name = "X" * 500  # 500-char, well over the 200 cap
        response = self._post({
            "cluster_ids": [str(c.id)],
            "names": {str(c.id): long_name},
            "generate_brief": False,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["summary"]["succeeded"], 1)

        i = Initiative.objects.get(parent_topic=f"signal_cluster:{c.id}")
        self.assertEqual(len(i.name), 200)
        self.assertEqual(i.name, "X" * 200)

    def test_names_applied_by_cluster_id_not_by_position(self):
        """Rigby A1 REVISE regression: cluster_ids order MUST NOT drift the mapping.

        The endpoint keys off cluster_id in the `names` dict. Reversing
        `cluster_ids` while keeping the same `names` dict must produce the
        same per-row name assignment, not a shuffled one.
        """
        c1 = _make_cluster("Pos row A")
        c2 = _make_cluster("Pos row B")
        response = self._post({
            # Reverse order on the wire.
            "cluster_ids": [str(c2.id), str(c1.id)],
            "names": {
                str(c1.id): "Belongs to A",
                str(c2.id): "Belongs to B",
            },
            "generate_brief": False,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["summary"]["succeeded"], 2)

        # Assignment is by ID, not by index in cluster_ids.
        i1 = Initiative.objects.get(parent_topic=f"signal_cluster:{c1.id}")
        i2 = Initiative.objects.get(parent_topic=f"signal_cluster:{c2.id}")
        self.assertEqual(i1.name, "Belongs to A")
        self.assertEqual(i2.name, "Belongs to B")
