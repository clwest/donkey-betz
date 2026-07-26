"""
Tests for the Workspace Home snapshot endpoint (Session 2983).

Spec provenance:
- ENGINEERING SPEC — Workspace Home v1 (Legibility Overhaul)
  deliverable `5e1c702f-c09e-4f10-b513-888f0784a81a`
- Initiative `1b9ef2c4-1d7f-4dec-89f4-a4f5a3f38746`
- Exec plan `ab0c4872-556d-41ba-b5de-21e489f14eda`

Run::

    USE_PGBOUNCER=0 python manage.py test core.tests.test_workspace_home_snapshot -v 2

The pgbouncer note from `test_deliverable_initiative_diagnostics.py:19-33`
applies here.
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.models_deliverables import Deliverable
from core.models_document_registry import Initiative, InitiativeActionItem
from core.models_skin_layer import ProjectWorkspace


User = get_user_model()


LONG = "s2983 workspace home snapshot fixture content. " * 8


def _make_deliverable(*, workspace, initiative=None, title, status="draft", is_pinned=False, deliverable_type="document"):
    return Deliverable.objects.create(
        title=title,
        slug=f"{title.lower().replace(' ', '-')}-{uuid.uuid4().hex[:6]}",
        agent_name="test-agent",
        content=LONG,
        workspace=workspace,
        initiative=initiative,
        status=status,
        is_pinned=is_pinned,
        deliverable_type=deliverable_type,
    )


class WorkspaceHomeSnapshotTests(TestCase):
    """Endpoint smoke + shape + section behavior."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f"s2983-user-{uuid.uuid4().hex[:8]}",
            email="s2983@example.com",
            password="x",
            is_superuser=True,
        )
        cls.other_user = User.objects.create_user(
            username=f"s2983-other-{uuid.uuid4().hex[:8]}",
            email="s2983-other@example.com",
            password="x",
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user,
            name="S2983 Home Workspace",
            allow_autonomous_writes=True,
        )
        cls.other_workspace = ProjectWorkspace.objects.create(
            user=cls.other_user,
            name="S2983 Other Workspace",
            allow_autonomous_writes=True,
        )

        cls.active_initiative = Initiative.objects.create(
            name="S2983 Active Initiative",
            status=Initiative.Status.ACTIVE,
            current_stage=2,
            target_workspace=cls.workspace,
            owner=cls.user,
            next_action="Draft the design memo",
        )
        cls.triage_initiative = Initiative.objects.create(
            name="S2983 Triage Initiative",
            status=Initiative.Status.TRIAGE,
            current_stage=1,
            target_workspace=cls.workspace,
            owner=cls.user,
        )

        InitiativeActionItem.objects.create(
            initiative=cls.active_initiative,
            title="High priority action",
            source_text="high priority action",
            status=InitiativeActionItem.Status.PENDING,
            priority=InitiativeActionItem.Priority.HIGH,
            order=1,
        )
        InitiativeActionItem.objects.create(
            initiative=cls.active_initiative,
            title="Critical priority action",
            source_text="critical priority action",
            status=InitiativeActionItem.Status.IN_PROGRESS,
            priority=InitiativeActionItem.Priority.CRITICAL,
            order=2,
        )
        InitiativeActionItem.objects.create(
            initiative=cls.active_initiative,
            title="Already completed action (excluded)",
            source_text="completed action",
            status=InitiativeActionItem.Status.COMPLETED,
            priority=InitiativeActionItem.Priority.HIGH,
            order=3,
        )

        cls.pinned = _make_deliverable(
            workspace=cls.workspace, initiative=cls.active_initiative,
            title="S2983 Pinned Spec", status="ready", is_pinned=True,
            deliverable_type="engineering_spec",
        )
        cls.ready = _make_deliverable(
            workspace=cls.workspace, initiative=cls.active_initiative,
            title="S2983 Ready Deliverable", status="ready",
        )
        cls.draft = _make_deliverable(
            workspace=cls.workspace, initiative=None,
            title="S2983 Draft Deliverable", status="draft",
        )
        # Belongs to another workspace — must never leak.
        cls.foreign = _make_deliverable(
            workspace=cls.other_workspace, initiative=None,
            title="S2983 Foreign Deliverable", status="ready",
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.url = reverse("workspace-home-snapshot", args=[self.workspace.id])

    def test_endpoint_returns_200_and_top_level_shape(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, response.content)

        payload = response.json()
        self.assertEqual(set(payload.keys()), {"workspace", "now", "active_work", "library"})
        self.assertEqual(payload["workspace"]["id"], str(self.workspace.id))
        self.assertEqual(payload["workspace"]["name"], "S2983 Home Workspace")

    def test_now_section_shape(self):
        payload = self.client.get(self.url).json()
        now = payload["now"]
        self.assertEqual(
            set(now.keys()),
            {
                "window_hours",
                "runs_count",
                "failures_count",
                "new_deliverables_count",
                "updated_deliverables_count",
                "timeline",
            },
        )
        self.assertEqual(now["window_hours"], 24)
        # Fixtures were just created, so new_deliverables_count includes the workspace's rows only.
        self.assertGreaterEqual(now["new_deliverables_count"], 3)
        self.assertIsInstance(now["timeline"], list)
        # Timeline entries have the documented kinds.
        for entry in now["timeline"]:
            self.assertIn(entry["kind"], {"deliverable_created", "deliverable_updated", "agent_run_failed"})

    def test_active_work_section_prioritizes_active_initiatives_and_orders_action_items(self):
        payload = self.client.get(self.url).json()
        aw = payload["active_work"]
        self.assertEqual(set(aw.keys()), {"initiatives", "action_items", "needs_review"})

        # ACTIVE first per spec AC-ACTIVE-1.
        self.assertGreaterEqual(len(aw["initiatives"]), 2)
        self.assertEqual(aw["initiatives"][0]["status"], Initiative.Status.ACTIVE)
        self.assertEqual(aw["initiatives"][0]["id"], str(self.active_initiative.id))
        self.assertEqual(aw["initiatives"][0]["next_action"], "Draft the design memo")
        self.assertEqual(aw["initiatives"][0]["action_items_count"], 2)

        # Action items: critical before high; completed excluded.
        priorities = [item["priority"] for item in aw["action_items"]]
        self.assertEqual(priorities[:2], ["critical", "high"])
        self.assertNotIn("Already completed action (excluded)", [i["title"] for i in aw["action_items"]])

        # Needs review: only ready deliverables from this workspace.
        ready_titles = [d["title"] for d in aw["needs_review"]["ready_deliverables"]]
        self.assertIn("S2983 Pinned Spec", ready_titles)
        self.assertIn("S2983 Ready Deliverable", ready_titles)
        self.assertNotIn("S2983 Draft Deliverable", ready_titles)
        self.assertNotIn("S2983 Foreign Deliverable", ready_titles)
        self.assertEqual(aw["needs_review"]["pending_decisions"], [])

    def test_library_section_pinned_first_then_recent_excluding_pinned(self):
        payload = self.client.get(self.url).json()
        lib = payload["library"]
        pinned_ids = {d["id"] for d in lib["pinned"]}
        recent_ids = {d["id"] for d in lib["recent"]}

        self.assertIn(str(self.pinned.id), pinned_ids)
        self.assertNotIn(str(self.pinned.id), recent_ids, "Pinned must not duplicate into recent")
        self.assertIn(str(self.draft.id), recent_ids)
        self.assertIn(str(self.ready.id), recent_ids)
        self.assertNotIn(str(self.foreign.id), pinned_ids | recent_ids)

    def test_all_list_caps_at_20(self):
        # Add many drafts to exercise the cap; keep it small enough for a fast test.
        for i in range(25):
            _make_deliverable(
                workspace=self.workspace, initiative=None,
                title=f"S2983 Bulk {i}", status="draft",
            )
        payload = self.client.get(self.url).json()
        self.assertLessEqual(len(payload["library"]["recent"]), 20)
        self.assertLessEqual(len(payload["now"]["timeline"]), 20)

    def test_returns_404_for_missing_workspace(self):
        missing = reverse("workspace-home-snapshot", args=[uuid.uuid4()])
        response = self.client.get(missing)
        self.assertEqual(response.status_code, 404)

    def test_non_owner_non_superuser_cannot_reach_workspace(self):
        client = APIClient()
        client.force_authenticate(self.other_user)
        response = client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_section_failure_returns_partial_payload(self):
        """Guardrail: a section raising must not fail the whole response (spec §Implementation notes)."""
        with patch(
            "core.views_workspace_home._build_active_work",
            side_effect=RuntimeError("simulated"),
        ):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(
            payload["active_work"],
            {"initiatives": [], "action_items": [], "needs_review": {"ready_deliverables": [], "pending_decisions": []}},
        )
        # Other sections still populated.
        self.assertIn("timeline", payload["now"])
        self.assertIn("pinned", payload["library"])

    def test_authentication_required(self):
        client = APIClient()  # unauthenticated
        response = client.get(self.url)
        self.assertIn(response.status_code, (401, 403))
