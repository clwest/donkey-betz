"""Session 1197 — Initiative.kind classification regression tests.

Covers the three production hooks shipped in PRs #2416/#2417/#2418:

A. Migration 0362 — Initiative.kind enum + related_initiatives JSONField.
B. apply_initiative_kind_classification mgmt cmd — idempotent classifier.
C. report_initiative_kinds mgmt cmd — backfill-safety heuristic flags.

Acceptance criteria mapping (from INITIATIVES_FIRST_BACKBONE.md §7):
- AC11 → test_kind_field_choices, test_default_kind_is_project
- AC12 → test_apply_idempotent_on_rerun
- AC13 → test_split_pair_links_bidirectional
- AC14 → test_report_no_prefix_clusters_post_apply

Local-run note (Session 1195 Plan C / Session 1196 PR #5 carryover):
    Default local DATABASE_URL routes through pgbouncer (transaction
    pool on :5433) which can't proxy ``CREATE DATABASE``, so Django's
    test runner can't spin up ``test_unified_donkey_betz``. CI runs
    against a direct Postgres connection and is the authoritative
    runner for this suite. To run locally, point either
    ``DJANGO_TEST_DATABASE_URL`` or ``TEST_DATABASE_URL`` at a direct
    (non-pooled) Postgres DSN with CREATEDB on the user, or run inside
    the docker-compose stack that exposes Postgres directly.

    Behavior smoke-verified during PRs #2417/#2418 against the live DB
    via the ``--apply`` and report cmd output. This file codifies those
    smoke checks for regression coverage.

Run::

    python manage.py test core.tests.test_initiative_kind_classification -v2
"""

import io
import json
import uuid

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from core.models_document_registry import Initiative
from core.models_skin_layer import ProjectWorkspace
from core.management.commands.apply_initiative_kind_classification import (
    SPEC as KIND_SPEC,
)


User = get_user_model()


def _make_workspace_fixture(cls):
    cls.user = User.objects.create_user(
        username=f'kind-test-{uuid.uuid4().hex[:8]}',
        email='kind-test@example.com',
        password='x',
        is_superuser=True,
    )
    cls.workspace = ProjectWorkspace.objects.create(
        user=cls.user, name='Kind Test Workspace',
        allow_autonomous_writes=True,
    )


def _call(cmd_name, *args, **kwargs):
    """Invoke a mgmt cmd and return its stdout as a string."""
    out = io.StringIO()
    call_command(cmd_name, *args, stdout=out, **kwargs)
    return out.getvalue()


# ────────────────────────────────────────────────────────────────────────
# Schema tests (AC11)
# ────────────────────────────────────────────────────────────────────────


class KindFieldSchemaTest(TestCase):
    """AC11 — kind field exists with 4 expected choices."""

    def test_kind_field_choices(self):
        choices = [c[0] for c in Initiative.Kind.choices]
        self.assertEqual(
            sorted(choices),
            sorted(['project', 'recurring_artifact', 'investigation', 'spec_backlog']),
        )

    def test_kind_field_max_length(self):
        field = Initiative._meta.get_field('kind')
        self.assertEqual(field.max_length, 24)

    def test_kind_field_indexed(self):
        field = Initiative._meta.get_field('kind')
        self.assertTrue(field.db_index)

    def test_related_initiatives_default_is_list(self):
        # Use Django field default callable (not the field literal).
        field = Initiative._meta.get_field('related_initiatives')
        self.assertEqual(field.default(), [])


# ────────────────────────────────────────────────────────────────────────
# Model defaults
# ────────────────────────────────────────────────────────────────────────


class KindDefaultsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_workspace_fixture(cls)

    def test_default_kind_is_project(self):
        init = Initiative.objects.create(
            name=f'Default Kind Test {uuid.uuid4().hex[:6]}',
            target_workspace=self.workspace,
        )
        self.assertEqual(init.kind, 'project')

    def test_default_related_initiatives_is_empty_list(self):
        init = Initiative.objects.create(
            name=f'Default Links Test {uuid.uuid4().hex[:6]}',
            target_workspace=self.workspace,
        )
        self.assertEqual(init.related_initiatives, [])


# ────────────────────────────────────────────────────────────────────────
# apply_initiative_kind_classification mgmt cmd
# ────────────────────────────────────────────────────────────────────────


class ApplyCommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_workspace_fixture(cls)

    def _apply(self):
        return _call(
            'apply_initiative_kind_classification',
            '--apply',
            '--workspace-id', str(self.workspace.id),
            '--json-only',
        )

    def test_dry_run_writes_nothing(self):
        starting_count = Initiative.objects.count()
        out = _call(
            'apply_initiative_kind_classification',
            '--workspace-id', str(self.workspace.id),
            '--json-only',
        )
        report = json.loads(out)
        self.assertEqual(report['mode'], 'dry-run')
        self.assertIsNone(report['applied'])
        self.assertEqual(Initiative.objects.count(), starting_count)

    def test_apply_creates_11_initiatives_from_spec(self):
        # SPEC has 11 rows; in a fresh test DB none of the existing_id
        # references resolve, so all 11 are creates.
        out = self._apply()
        report = json.loads(out)
        self.assertEqual(report['mode'], 'apply')
        created = report['applied']['created_or_matched']
        self.assertEqual(set(created.keys()),
                         {entry['key'] for entry in KIND_SPEC})
        # All target_workspace_id should be our test workspace.
        for spec_entry in KIND_SPEC:
            init = Initiative.objects.get(id=created[spec_entry['key']])
            self.assertEqual(str(init.target_workspace_id), str(self.workspace.id))
            self.assertEqual(init.kind, spec_entry['kind'])

    def test_apply_idempotent_on_rerun(self):
        """AC12 — second --apply produces zero net writes."""
        self._apply()  # First call.
        out = self._apply()  # Second call.
        report = json.loads(out)
        applied = report['applied']
        self.assertEqual(applied['kind_updated'], {})
        self.assertEqual(applied['split_links_written'], [])

    def test_split_pair_links_bidirectional(self):
        """AC13 — clusters 3 and 9 produce 4 directional link writes."""
        out = self._apply()
        report = json.loads(out)
        links = report['applied']['split_links_written']
        self.assertEqual(len(links), 4)
        # Build {from_key: relation} map and validate directional pattern.
        by_from = {link['from_key']: link['relation'] for link in links}
        self.assertEqual(by_from['3a'], 'spawns')
        self.assertEqual(by_from['3b'], 'spawned_from')
        self.assertEqual(by_from['9a'], 'spawns')
        self.assertEqual(by_from['9b'], 'spawned_from')

    def test_split_pair_back_references_match_ids(self):
        """3a.related_initiatives[0].id == 3b.id AND vice versa."""
        out = self._apply()
        report = json.loads(out)
        created = report['applied']['created_or_matched']
        init_3a = Initiative.objects.get(id=created['3a'])
        init_3b = Initiative.objects.get(id=created['3b'])
        self.assertEqual(init_3a.related_initiatives[0]['id'], str(init_3b.id))
        self.assertEqual(init_3a.related_initiatives[0]['relation'], 'spawns')
        self.assertEqual(init_3b.related_initiatives[0]['id'], str(init_3a.id))
        self.assertEqual(init_3b.related_initiatives[0]['relation'], 'spawned_from')


# ────────────────────────────────────────────────────────────────────────
# report_initiative_kinds mgmt cmd (AC14)
# ────────────────────────────────────────────────────────────────────────


class ReportCommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_workspace_fixture(cls)

    def test_cross_tab_counts_match_population(self):
        # Build a known-shape population: 2 projects, 1 recurring_artifact.
        Initiative.objects.create(
            name=f'P1 {uuid.uuid4().hex[:6]}',
            kind='project', status='ACTIVE',
            target_workspace=self.workspace,
        )
        Initiative.objects.create(
            name=f'P2 {uuid.uuid4().hex[:6]}',
            kind='project', status='COMPLETED',
            target_workspace=self.workspace,
        )
        Initiative.objects.create(
            name=f'R1 {uuid.uuid4().hex[:6]}',
            kind='recurring_artifact', status='ACTIVE',
            target_workspace=self.workspace,
        )

        out = _call(
            'report_initiative_kinds',
            '--workspace-id', str(self.workspace.id),
            '--json-only',
        )
        report = json.loads(out)
        self.assertEqual(report['cross_tab']['project']['ACTIVE'], 1)
        self.assertEqual(report['cross_tab']['project']['COMPLETED'], 1)
        self.assertEqual(report['cross_tab']['recurring_artifact']['ACTIVE'], 1)

    def test_prefix_cluster_flags_contrived_case(self):
        """3+ project rows sharing a 24-char prefix → flagged."""
        prefix = 'DailyMetricsRun 2026-06-'  # exactly 24 chars
        for day in (15, 16, 17, 18):
            Initiative.objects.create(
                name=f'{prefix}{day} {uuid.uuid4().hex[:4]}',
                kind='project',
                target_workspace=self.workspace,
            )

        out = _call(
            'report_initiative_kinds',
            '--workspace-id', str(self.workspace.id),
            '--json-only',
        )
        report = json.loads(out)
        prefixes_flagged = [c['prefix'] for c in report['prefix_clusters']]
        self.assertIn(prefix.strip(), prefixes_flagged)

    def test_no_prefix_clusters_after_session_1197_apply(self):
        """AC14 — running the apply cmd then the report shows no flags
        (because the apply cmd correctly pulls recurring streams out of
        the project kind)."""
        _call(
            'apply_initiative_kind_classification',
            '--apply',
            '--workspace-id', str(self.workspace.id),
            '--json-only',
        )
        out = _call(
            'report_initiative_kinds',
            '--workspace-id', str(self.workspace.id),
            '--json-only',
        )
        report = json.loads(out)
        self.assertEqual(report['prefix_clusters'], [])
        self.assertEqual(report['high_deliverable_projects'], [])
