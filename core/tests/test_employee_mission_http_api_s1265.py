"""Session 1265 P1 — read-only Employee/Mission HTTP API tests.

Locks the 5 endpoints introduced in ``core/views_employee_api.py``:

  1. ``GET /api/employees/``
  2. ``GET /api/employees/<handle>/``
  3. ``GET /api/employees/<handle>/jobs/<job_key>/status/``
  4. ``GET /api/missions/<id>/``
  5. ``GET /api/missions/<id>/evidence/``

Contract focus per Rigby SIGN-with-edits:

  * D1 — response shapes MUST mirror ``employee_tool`` /
    ``derive_status`` / ``evidence_for_mission`` verbatim (contract
    tests deep-equal both surfaces).
  * D3 — ``IsAdminUser`` gate: non-staff authenticated users get
    403; anonymous gets 401/403.
  * S1265 P1 add — verbose=true returns full error_tail; verbose=false
    returns preview + has_full_error_tail.
  * S1265 P1 add — mission detail returns 8 contract fields always
    present (id, status, run_kind, triggered_by, started_at,
    finished_at, mission_id, summary).

Real PostgreSQL per S1234 memory rule.

Run::

    .venv/bin/python manage.py test \\
        core.tests.test_employee_mission_http_api_s1265 -v 2 --keepdb
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from core.employees import list_employees
from core.models_ops_runs import OpsRun


# ═════════════════════════════════════════════════════════════════════
# §1 — User fixtures
# ═════════════════════════════════════════════════════════════════════


def _make_staff_user(username: str = "test_staff_s1265") -> Any:
    User = get_user_model()
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={"is_staff": True, "is_superuser": False},
    )
    if not user.is_staff:
        user.is_staff = True
        user.save(update_fields=["is_staff"])
    return user


def _make_regular_user(username: str = "test_regular_s1265") -> Any:
    User = get_user_model()
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={"is_staff": False, "is_superuser": False},
    )
    if user.is_staff:
        user.is_staff = False
        user.save(update_fields=["is_staff"])
    return user


# ═════════════════════════════════════════════════════════════════════
# §2 — Auth gate (D3)
# ═════════════════════════════════════════════════════════════════════


class EmployeeApiAuthGateTest(TestCase):
    """D3 contract — IsAdminUser gate denies non-staff."""

    def test_anonymous_user_blocked(self):
        client = Client()
        r = client.get("/api/employees/")
        # IsAdminUser denies anon — DRF returns 403 for default
        # SessionAuthentication with no credentials.
        self.assertIn(r.status_code, (401, 403))

    def test_authenticated_non_staff_blocked(self):
        """Non-staff authenticated user gets 403.

        Locks Rigby D3 flip — these endpoints expose JobContract
        shapes + ops telemetry and must not be visible to a
        random logged-in user on a multi-tenant platform.
        """
        client = Client()
        client.force_login(_make_regular_user())
        r = client.get("/api/employees/")
        self.assertEqual(r.status_code, 403)

    def test_staff_user_passes(self):
        client = Client()
        client.force_login(_make_staff_user())
        r = client.get("/api/employees/")
        self.assertEqual(r.status_code, 200)


# ═════════════════════════════════════════════════════════════════════
# §3 — Endpoint 1: /api/employees/
# ═════════════════════════════════════════════════════════════════════


class EmployeeListEndpointTest(TestCase):
    """``GET /api/employees/`` — happy path."""

    def setUp(self):
        self.client = Client()
        self.client.force_login(_make_staff_user())

    def test_returns_registered_employees(self):
        r = self.client.get("/api/employees/")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["count"], len(list_employees()))
        self.assertEqual(len(data["employees"]), data["count"])
        # Every employee row has the AIEmployee-shape keys
        # ``_dataclass_to_jsonable`` produces.
        for emp in data["employees"]:
            self.assertIn("handle", emp)
            self.assertIn("display_name", emp)


# ═════════════════════════════════════════════════════════════════════
# §4 — Endpoint 2: /api/employees/<handle>/
# ═════════════════════════════════════════════════════════════════════


class EmployeeDetailEndpointTest(TestCase):
    """``GET /api/employees/<handle>/`` — shape mirrors employee_tool describe."""

    def setUp(self):
        self.client = Client()
        self.client.force_login(_make_staff_user())

    def test_returns_employee_and_jobs(self):
        r = self.client.get("/api/employees/rigby/")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["action"], "describe")
        self.assertEqual(data["employee"]["handle"], "rigby")
        self.assertGreaterEqual(data["job_count"], 1)
        self.assertEqual(len(data["jobs"]), data["job_count"])
        for job_entry in data["jobs"]:
            self.assertIn("key", job_entry)
            self.assertIn("contract", job_entry)

    def test_unknown_handle_returns_404_with_known_employees(self):
        r = self.client.get("/api/employees/nonexistent_handle_xyz/")
        self.assertEqual(r.status_code, 404)
        data = r.json()
        self.assertFalse(data["ok"])
        self.assertIn("error", data)
        self.assertIn("known_employees", data)
        self.assertIsInstance(data["known_employees"], list)

    def test_shape_matches_public_helper_contract(self):
        """Contract test — HTTP response equals the shape computed from
        the same public helpers ``employee_tool`` uses.

        Locks Rigby SIGN-clean D1: 'verify outputs match existing
        employee_tool behavior.' Compares against the public helper
        surface (``get_employee`` + ``list_jobs_with_keys`` +
        ``_dataclass_to_jsonable``) rather than reaching into
        ``ToolDispatcher._handle_employee_tool`` — both code paths
        share the same shared serializer, so this catches any future
        drift between them.
        """
        from core.employees import get_employee, list_jobs_with_keys
        from core.services.td_handlers_employee import _dataclass_to_jsonable

        # Reconstruct the contract from the same building blocks both
        # surfaces use. If either surface deviates, the deep-equal
        # below will diverge.
        employee = get_employee("rigby")
        expected_employee = _dataclass_to_jsonable(employee)
        expected_jobs = [
            {"key": key, "contract": _dataclass_to_jsonable(job)}
            for key, job in list_jobs_with_keys("rigby")
        ]

        r = self.client.get("/api/employees/rigby/")
        self.assertEqual(r.status_code, 200)
        http_result = r.json()

        # Shape + value contract — every key in the describe envelope
        # plus the nested employee/jobs payloads.
        self.assertTrue(http_result["ok"])
        self.assertEqual(http_result["action"], "describe")
        self.assertEqual(http_result["employee"], expected_employee)
        self.assertEqual(http_result["job_count"], len(expected_jobs))
        self.assertEqual(http_result["jobs"], expected_jobs)


# ═════════════════════════════════════════════════════════════════════
# §5 — Endpoint 3: /api/employees/<handle>/jobs/<job_key>/status/
# ═════════════════════════════════════════════════════════════════════


class EmployeeJobStatusEndpointTest(TestCase):
    """``GET /api/employees/<handle>/jobs/<job_key>/status/``."""

    def setUp(self):
        self.client = Client()
        self.client.force_login(_make_staff_user())

    def test_default_window_returns_status(self):
        r = self.client.get(
            "/api/employees/rigby/jobs/docs_manager/status/"
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        # ``derive_status`` returns ``ok=True`` for successful
        # computation; the value of mission counts depends on test
        # DB state, but the envelope must be present.
        self.assertTrue(data.get("ok"))

    def test_explicit_window_30d(self):
        r = self.client.get(
            "/api/employees/rigby/jobs/docs_manager/status/?window=30d"
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json().get("ok"))

    def test_invalid_window_400(self):
        r = self.client.get(
            "/api/employees/rigby/jobs/docs_manager/status/?window=99d"
        )
        self.assertEqual(r.status_code, 400)
        data = r.json()
        self.assertFalse(data["ok"])
        self.assertEqual(data["valid_windows"], ["7d", "30d", "90d"])

    def test_unknown_employee_404(self):
        r = self.client.get(
            "/api/employees/nobody/jobs/docs_manager/status/"
        )
        self.assertEqual(r.status_code, 404)
        self.assertIn("known_employees", r.json())

    def test_unknown_job_404(self):
        r = self.client.get(
            "/api/employees/rigby/jobs/nonexistent_job/status/"
        )
        self.assertEqual(r.status_code, 404)
        self.assertIn("known_jobs", r.json())


# ═════════════════════════════════════════════════════════════════════
# §6 — Endpoint 4: /api/missions/<id>/
# ═════════════════════════════════════════════════════════════════════


class MissionDetailEndpointTest(TestCase):
    """``GET /api/missions/<id>/``."""

    def setUp(self):
        self.client = Client()
        self.client.force_login(_make_staff_user())
        self.mission = OpsRun.objects.create(
            domain="mission",
            run_kind="docs_cascade",
            run_type="test_s1265",
            status="passed",
            triggered_by="test_s1265",
            title="test mission",
            summary={"verdict": "certified"},
        )

    def test_returns_8_contract_fields(self):
        """Field-presence contract test per Rigby S1265 P1 add.

        These 8 fields MUST always be present (even if null) so
        downstream status views can safely assume shape stability.
        """
        r = self.client.get(f"/api/missions/{self.mission.id}/")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["ok"])
        mission = data["mission"]
        for field in (
            "id",
            "status",
            "run_kind",
            "triggered_by",
            "started_at",
            "finished_at",
            "mission_id",
            "summary",
        ):
            self.assertIn(
                field,
                mission,
                f"mission_detail must always include {field!r}",
            )

    def test_finished_at_null_for_running(self):
        """Running missions have ``finished_at = None``; the contract
        says the field must still be present.
        """
        running = OpsRun.objects.create(
            domain="mission",
            run_kind="docs_cascade",
            run_type="test_s1265",
            status="running",
            triggered_by="test_s1265",
            title="running mission",
            summary={},
        )
        r = self.client.get(f"/api/missions/{running.id}/")
        self.assertEqual(r.status_code, 200)
        mission = r.json()["mission"]
        self.assertIn("finished_at", mission)
        self.assertIsNone(mission["finished_at"])

    def test_unknown_mission_404(self):
        ghost = uuid4()
        r = self.client.get(f"/api/missions/{ghost}/")
        self.assertEqual(r.status_code, 404)
        data = r.json()
        self.assertFalse(data["ok"])
        self.assertEqual(data["error"], "mission_not_found")


# ═════════════════════════════════════════════════════════════════════
# §7 — Endpoint 5: /api/missions/<id>/evidence/
# ═════════════════════════════════════════════════════════════════════


class MissionEvidenceEndpointTest(TestCase):
    """``GET /api/missions/<id>/evidence/`` — verbose contract."""

    def setUp(self):
        self.client = Client()
        self.client.force_login(_make_staff_user())
        # Build a mission summary with a multi-line error_tail so
        # the verbose=true vs verbose=false contract is observable.
        self.error_tail = "\n".join(
            f"line_{i}" for i in range(50)
        )
        self.mission = OpsRun.objects.create(
            domain="mission",
            run_kind="docs_cascade",
            run_type="test_s1265",
            status="failed",
            triggered_by="test_s1265",
            title="failed mission",
            summary={
                "verdict": "failed",
                "failed_step": "test_step",
                "error_tail": self.error_tail,
            },
        )

    def test_verbose_false_returns_preview_and_flag(self):
        r = self.client.get(f"/api/missions/{self.mission.id}/evidence/")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        # ``evidence_for_mission`` nests ``summary`` under ``ops_run``;
        # the preview/has_full_error_tail mutation happens in-place
        # on that nested dict.
        self._assert_preview_contract(data, expect_full=False)

    def test_verbose_true_returns_full_error_tail(self):
        """Verbose=true contract per Rigby S1265 P1 add.

        The endpoint MUST forward verbose=True to evidence_for_mission
        so the full error_tail is returned, NOT the preview.
        """
        r = self.client.get(
            f"/api/missions/{self.mission.id}/evidence/?verbose=true"
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self._assert_preview_contract(data, expect_full=True)

    def test_unknown_mission_returns_404(self):
        ghost = uuid4()
        r = self.client.get(f"/api/missions/{ghost}/evidence/")
        self.assertEqual(r.status_code, 404)
        data = r.json()
        self.assertEqual(data.get("error"), "mission_not_found")

    def _assert_preview_contract(self, data: dict, expect_full: bool) -> None:
        """Locate ``ops_run.summary`` + assert error_tail vs preview shape.

        ``evidence_for_mission`` nests the mutated summary under
        ``ops_run.summary``. ``verbose=True`` keeps ``error_tail`` in
        that summary; ``verbose=False`` swaps it for
        ``error_tail_preview`` + ``has_full_error_tail``. Both
        branches drop the un-needed sibling key.
        """
        summary = (data.get("ops_run") or {}).get("summary") or {}
        if expect_full:
            self.assertIn(
                "error_tail",
                summary,
                "verbose=true must include the full error_tail",
            )
            self.assertEqual(summary["error_tail"], self.error_tail)
            self.assertNotIn("error_tail_preview", summary)
        else:
            self.assertIn(
                "error_tail_preview",
                summary,
                "verbose=false must include error_tail_preview",
            )
            self.assertIn(
                "has_full_error_tail",
                summary,
                "verbose=false must include has_full_error_tail boolean",
            )
            self.assertNotIn(
                "error_tail",
                summary,
                "verbose=false must NOT leak the full error_tail",
            )
