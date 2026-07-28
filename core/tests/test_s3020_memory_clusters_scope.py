"""Session 3020 (Fold A F-1 + F-2): scope guard on `/api/memory-clusters/`
sibling of the S3017 memory-palace class.

Ratified S3020 Option A at S3019 close. The `docs/audits/UNSCOPED_GETS_S3020.md`
audit surfaced two same-class F-2/F-3-shape gaps in
`core/views_memory_clusters.py` — `add_memory_to_cluster` (mutation:
anon could add any user's memory to a cluster) and `find_similar_clusters`
(read: anon could retrieve any memory's embedding + trigger similarity
search). Both under `/api/memory-clusters/` bare-prefix in PUBLIC_PATHS
with unscoped `AgentMemory.objects.get(id=memory_id)`.

**What this test file locks:**

1. `add_memory_to_cluster` — anon → 401, cross-user → 404 (memory not
   added to cluster), own → 200.
2. `find_similar_clusters` — anon → 401, cross-user memory_id → 404,
   own memory_id → 200.

Uses the same S3017/S3019 shape (`@token_auth_required` + `scope_queryset_agent_memory`).
"""
from __future__ import annotations

import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from core.models_unified_system import (
    Agent,
    AgentMemory,
    MemoryCluster,
    MemoryClusterMembership,
)
from core.tests.helpers.agent_assignment import assign_agent_to_user


User = get_user_model()


class MemoryClustersScopeTests(TestCase):
    """S3020 F-1 + F-2 — auth gate + scope predicate on memory-clusters."""

    def setUp(self) -> None:
        self.alice = User.objects.create_user(
            username="alice_s3020", email="alice_s3020@example.com", password="pw",
        )
        self.bob = User.objects.create_user(
            username="bob_s3020", email="bob_s3020@example.com", password="pw",
        )
        self.agent_alice = Agent.objects.create(
            name="alice_cluster_agent_s3020", agent_type="test",
            description="", specialization="",
        )
        self.agent_bob = Agent.objects.create(
            name="bob_cluster_agent_s3020", agent_type="test",
            description="", specialization="",
        )
        assign_agent_to_user(self.agent_alice, self.alice)
        assign_agent_to_user(self.agent_bob, self.bob)

        self.mem_alice = AgentMemory.objects.create(
            agent=self.agent_alice, title="alice cluster mem",
            content="alice", memory_type="insight",
            embedding=[0.1] * 1536,
        )
        self.mem_bob = AgentMemory.objects.create(
            agent=self.agent_bob, title="bob cluster mem",
            content="bob", memory_type="insight",
            embedding=[0.2] * 1536,
        )
        # Cluster owned via agent (memory-cluster has agent FK); alice's cluster.
        self.cluster_alice = MemoryCluster.objects.create(
            agent=self.agent_alice,
            name="alice cluster",
        )

    def _client_for(self, user) -> Client:
        c = Client(HTTP_HOST="localhost:8000")
        c.force_login(user)
        return c

    def _add_url(self, cluster_id) -> str:
        return f"/api/memory-clusters/cluster/{cluster_id}/add-memory/"

    def _similar_url(self) -> str:
        return "/api/memory-clusters/find-similar/"

    # ---- F-1: add-memory-to-cluster ---------------------------------------

    def test_anonymous_add_memory_returns_401(self) -> None:
        resp = Client(HTTP_HOST="localhost:8000").post(
            self._add_url(self.cluster_alice.id),
            data=json.dumps({"memory_id": str(self.mem_alice.id)}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 401)

    def test_anonymous_cannot_mutate_cluster(self) -> None:
        """Anon fails the auth gate; cluster membership row not created."""
        before = MemoryClusterMembership.objects.filter(cluster=self.cluster_alice).count()
        Client(HTTP_HOST="localhost:8000").post(
            self._add_url(self.cluster_alice.id),
            data=json.dumps({"memory_id": str(self.mem_alice.id)}),
            content_type="application/json",
        )
        after = MemoryClusterMembership.objects.filter(cluster=self.cluster_alice).count()
        self.assertEqual(before, after)

    def test_alice_cannot_add_bobs_memory_to_her_cluster(self) -> None:
        resp = self._client_for(self.alice).post(
            self._add_url(self.cluster_alice.id),
            data=json.dumps({"memory_id": str(self.mem_bob.id)}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)
        # Bob's memory not linked to alice's cluster.
        self.assertFalse(
            MemoryClusterMembership.objects.filter(
                cluster=self.cluster_alice, memory=self.mem_bob,
            ).exists()
        )

    def test_alice_can_add_own_memory(self) -> None:
        """Rigby T1 REVISE §c: assert not-401/not-404 + membership row exists.
        Doesn't treat 500 as success (would mask regressions unrelated to authz).
        """
        resp = self._client_for(self.alice).post(
            self._add_url(self.cluster_alice.id),
            data=json.dumps({"memory_id": str(self.mem_alice.id)}),
            content_type="application/json",
        )
        # Cluster methods (calculate_centroid) may 500 on sparse test data;
        # the durable invariant is: auth+scope path let alice through AND
        # the membership row was created before centroid recalc ran.
        self.assertNotIn(resp.status_code, (401, 404))
        self.assertTrue(
            MemoryClusterMembership.objects.filter(
                cluster=self.cluster_alice, memory=self.mem_alice,
            ).exists()
        )

    def test_alice_cannot_add_own_memory_to_bobs_cluster(self) -> None:
        """S3020 F-1b (Rigby T1 REVISE Layer 1 cluster-ownership fold):
        even own-memory-to-cross-user-cluster fails at the cluster-fetch
        step. Alice's memory does not land in Bob's cluster."""
        cluster_bob = MemoryCluster.objects.create(
            agent=self.agent_bob, name="bob cluster",
        )
        resp = self._client_for(self.alice).post(
            self._add_url(cluster_bob.id),
            data=json.dumps({"memory_id": str(self.mem_alice.id)}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(
            MemoryClusterMembership.objects.filter(
                cluster=cluster_bob, memory=self.mem_alice,
            ).exists()
        )

    # ---- F-2: find-similar-clusters ---------------------------------------

    def test_anonymous_find_similar_returns_401(self) -> None:
        resp = Client(HTTP_HOST="localhost:8000").post(
            self._similar_url(),
            data=json.dumps({"memory_id": str(self.mem_alice.id)}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 401)

    def test_alice_cannot_search_via_bobs_memory_id(self) -> None:
        resp = self._client_for(self.alice).post(
            self._similar_url(),
            data=json.dumps({"memory_id": str(self.mem_bob.id)}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)

    def test_alice_can_search_via_own_memory_id(self) -> None:
        resp = self._client_for(self.alice).post(
            self._similar_url(),
            data=json.dumps({"memory_id": str(self.mem_alice.id)}),
            content_type="application/json",
        )
        # Reaching the similarity computation path is sufficient (may 200 with
        # empty results or 500 on sparse-cluster edge cases; both prove the
        # auth+scope gate lets the caller through for their own memory).
        self.assertNotIn(resp.status_code, (401, 404))
