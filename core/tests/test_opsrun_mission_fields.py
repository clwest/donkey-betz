"""
Tests for the Session 1250 PR 3 OpsRun MissionRun-compatibility fields.

Covers:
- migration applies cleanly (verified by Django test runner setup)
- default domain is ops
- existing OpsRun creation paths still work (no behavior change)
- mission rows can be created with domain='mission'
- ops query excludes mission rows
- mission query excludes ops rows
- mission_id is indexed
- run_kind accepts blank/default

Run::

    python manage.py test core.tests.test_opsrun_mission_fields -v2
"""

from __future__ import annotations

import uuid
from django.db import connection
from django.test import TestCase

from core.models_ops_runs import OpsRun, OpsRunEvent


# ---------------------------------------------------------------------------
# Defaults and round-tripping
# ---------------------------------------------------------------------------


class OpsRunDefaultsTests(TestCase):

    def test_default_domain_is_ops(self):
        run = OpsRun.objects.create(
            title="default-domain-run",
            run_type="manual",
        )
        run.refresh_from_db()
        self.assertEqual(run.domain, "ops")

    def test_default_run_kind_is_blank(self):
        run = OpsRun.objects.create(
            title="default-kind-run",
            run_type="manual",
        )
        run.refresh_from_db()
        self.assertEqual(run.run_kind, "")

    def test_default_mission_id_is_null(self):
        run = OpsRun.objects.create(
            title="default-mid-run",
            run_type="manual",
        )
        run.refresh_from_db()
        self.assertIsNone(run.mission_id)

    def test_existing_run_types_still_work(self):
        """Every legacy run_type creation path remains functional.

        These are the 5 run_type values in current production use
        (ops_loop, smoke_test, deploy_verify, manual, llm_routing).
        None of them should break with the new fields added.
        """
        for run_type in ("ops_loop", "smoke_test", "deploy_verify", "manual", "llm_routing"):
            run = OpsRun.objects.create(
                title=f"legacy-{run_type}",
                run_type=run_type,
            )
            self.assertEqual(run.run_type, run_type)
            # All legacy callers get ops domain implicitly.
            self.assertEqual(run.domain, "ops")
            self.assertEqual(run.run_kind, "")
            self.assertIsNone(run.mission_id)


# ---------------------------------------------------------------------------
# Mission rows + isolation
# ---------------------------------------------------------------------------


class MissionRowIsolationTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # 3 ops rows
        for i in range(3):
            OpsRun.objects.create(
                title=f"ops-row-{i}",
                run_type="manual",
                domain="ops",
            )
        # 2 mission rows
        cls.mission_id_1 = uuid.uuid4()
        cls.mission_id_2 = uuid.uuid4()
        OpsRun.objects.create(
            title="mission-row-1",
            run_type="manual",
            domain="mission",
            run_kind="intake",
            mission_id=cls.mission_id_1,
        )
        OpsRun.objects.create(
            title="mission-row-2",
            run_type="manual",
            domain="mission",
            run_kind="decision",
            mission_id=cls.mission_id_2,
        )

    def test_ops_query_excludes_mission_rows(self):
        titles = set(
            OpsRun.objects.filter(domain="ops").values_list("title", flat=True)
        )
        # Only the 3 ops rows seeded above (plus any leaked from other tests
        # using TransactionTestCase isolation — TestCase wraps in a
        # transaction so this stays clean).
        self.assertEqual(
            titles, {"ops-row-0", "ops-row-1", "ops-row-2"},
            "ops query must not return mission rows",
        )

    def test_mission_query_excludes_ops_rows(self):
        titles = set(
            OpsRun.objects.filter(domain="mission").values_list("title", flat=True)
        )
        self.assertEqual(
            titles, {"mission-row-1", "mission-row-2"},
            "mission query must not return ops rows",
        )

    def test_mission_row_round_trip(self):
        row = OpsRun.objects.get(title="mission-row-1")
        self.assertEqual(row.domain, "mission")
        self.assertEqual(row.run_kind, "intake")
        self.assertEqual(row.mission_id, self.mission_id_1)
        # run_type is preserved orthogonally — not overloaded into mission taxonomy.
        self.assertEqual(row.run_type, "manual")

    def test_mission_id_filter_finds_specific_row(self):
        row = OpsRun.objects.get(mission_id=self.mission_id_2)
        self.assertEqual(row.title, "mission-row-2")
        self.assertEqual(row.run_kind, "decision")


# ---------------------------------------------------------------------------
# Index presence
# ---------------------------------------------------------------------------


class IndexPresenceTests(TestCase):
    """Verify the new fields actually have indexes at the DB level.

    We can't rely on ``introspection.get_constraints`` returning the
    Django-managed index name verbatim, so we inspect both via Django's
    introspection AND by reading the model's _meta to confirm intent.
    """

    def test_domain_field_has_db_index_in_model(self):
        field = OpsRun._meta.get_field("domain")
        self.assertTrue(field.db_index, "OpsRun.domain must declare db_index=True")

    def test_mission_id_field_has_db_index_in_model(self):
        field = OpsRun._meta.get_field("mission_id")
        self.assertTrue(field.db_index, "OpsRun.mission_id must declare db_index=True")

    def test_indexes_exist_at_db_level(self):
        """Inspect the DB to confirm Django created the indexes on apply."""
        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(
                cursor, OpsRun._meta.db_table
            )
        indexed_columns: set[str] = set()
        for meta in constraints.values():
            if meta.get("index") and not meta.get("primary_key"):
                for col in meta.get("columns") or []:
                    indexed_columns.add(col)
        self.assertIn(
            "domain", indexed_columns,
            f"DB-level index on OpsRun.domain missing; indexed cols: {sorted(indexed_columns)}",
        )
        self.assertIn(
            "mission_id", indexed_columns,
            f"DB-level index on OpsRun.mission_id missing; indexed cols: {sorted(indexed_columns)}",
        )


# ---------------------------------------------------------------------------
# OpsRunEvent schema unchanged
# ---------------------------------------------------------------------------


class OpsRunEventSchemaUnchangedTests(TestCase):
    """PR 3 must not alter OpsRunEvent fields."""

    def test_ops_run_event_has_expected_fields_only(self):
        names = {f.name for f in OpsRunEvent._meta.get_fields()}
        # The 5 declared fields plus the auto-PK 'id'.
        # Note: ForeignKey adds both 'run' and 'run_id' under different lookup paths;
        # _meta.get_fields() returns the relation field 'run', not 'run_id'.
        expected = {"id", "run", "event_type", "label", "detail", "created_at"}
        self.assertEqual(
            names, expected,
            f"PR 3 must not change OpsRunEvent schema; got: {sorted(names)}",
        )

    def test_ops_run_event_no_domain_field(self):
        # Confirms PR 3 did NOT bleed domain into the event row schema.
        # The event row's domain is derivable via run__domain join only.
        field_names = {f.name for f in OpsRunEvent._meta.get_fields()}
        self.assertNotIn("domain", field_names)
        self.assertNotIn("run_kind", field_names)
        self.assertNotIn("mission_id", field_names)
