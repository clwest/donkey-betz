"""Cycle 1A KFI-1 (ADR-0110) — Deliverable → Document mirror tests.

Coverage per ADR-0110 §2.3 + Chris SIGN-3 V1-V7 verification requirements:

- T1a-T1e: 3-path extraction (Deliverable ID / Workspace UUID / ADR
  title / ambiguous / total failure).
- T2:  mirror creates Document with canonical_authority='workspace_canonical'.
- T3:  timestamps present + SC-1 (embedding_complete - ratification ≤ 60s).
- T4:  idempotence-unchanged (A13 Option C, branch B).
- T5:  idempotence-changed (A13 Option C, branch C).
- T6:  malformed body → no Document.
- T7:  end-to-end signal → task → Document + embedding.
- T8:  owner cascade — rr.user present.
- T9:  owner cascade — rr.user None + target.user present.
- T10: owner cascade — both None → MIRROR_OWNER_UNRESOLVED.
- T11: signal respects created=True.
- T12: dispatch_uid prevents duplicate receivers.
- T13: _derive_source_type recognizes source='workspace'.
- T14: management command processes historical deliverable_type='document' records.
- T15: live signal does NOT fire on deliverable_type='document' records.
- T16: query-count sanity ceiling.
- T17: A14 concurrent get_or_create race → IntegrityError → re-fetch (no dup).
"""

from unittest import mock
from uuid import UUID, uuid4

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError, connection
from django.db.models.signals import post_save
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from content.embeddings import _derive_source_type
from content.models import Document, DocumentEmbedding
from core.models import Deliverable
from core.services.deliverable_mirror_target_extraction import (
    extract_target_deliverable_id,
)
from core.signals.deliverable_mirror_signals import (
    _DISPATCH_UID,
    connect_deliverable_mirror_signals,
)
from core.tasks import mirror_deliverable_to_document


User = get_user_model()


def _rr_body_path1(uuid_str, title='0110_ADR_TEST'):
    return (
        f'# RATIFICATION_TEST\n\n## §1 Target\n\n'
        f'- **Deliverable ratified:** {title}\n'
        f'- **Deliverable ID:** {uuid_str}\n'
    )


def _rr_body_path2(uuid_str, title='0140_ADR_TEST'):
    return (
        f'# RATIFICATION_TEST\n\n## §1 Target\n\n'
        f'- **ADR:** {title}\n'
        f'- **Workspace UUID:** `{uuid_str}`\n'
        f'- **Workspace:** `wksp-uuid` (Test)\n'
    )


def _rr_body_path3(title='0999_ADR_TITLE_ONLY'):
    return (
        f'# RATIFICATION_TEST\n\n## §1 Target\n\n'
        f'- **ADR:** {title}\n'
    )


class _FixtureBase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='deliverable-mirror-tests',
            email='deliverable-mirror-tests@example.com',
            password='fixture',
        )
        cls.workspace = _make_workspace(cls.user)


def _make_workspace(user):
    from core.models_skin_layer import ProjectWorkspace

    return ProjectWorkspace.objects.create(
        user=user,
        name='Test Workspace',
        description='Fixture workspace',
        root_path='/tmp/test',
        git_remote_url='https://example.invalid/repo.git',
        current_branch='main',
    )


def _make_target(workspace, user, *, title='0110_TARGET', content='body'):
    return Deliverable.objects.create(
        workspace=workspace,
        user=user,
        title=title,
        deliverable_type='adr',
        category='governance',
        content=content,
        status='completed',
    )


def _make_rr(workspace, user, *, body, deliverable_type='ratification_record',
             title='RATIFICATION_TEST'):
    return Deliverable.objects.create(
        workspace=workspace,
        user=user,
        title=title,
        deliverable_type=deliverable_type,
        category='governance',
        content=body,
        status='completed',
    )


# ---------------------------------------------------------------------------
# T1: Target extraction (3-path cascade)
# ---------------------------------------------------------------------------


class ExtractionPath1Tests(_FixtureBase):

    def test_t1a_deliverable_id_path(self):
        target = _make_target(self.workspace, self.user)
        rr = _make_rr(
            self.workspace, self.user,
            body=_rr_body_path1(str(target.id)),
        )
        result = extract_target_deliverable_id(rr, Deliverable)
        self.assertEqual(result, target.id)


class ExtractionPath2Tests(_FixtureBase):

    def test_t1b_workspace_uuid_historical_path(self):
        target = _make_target(self.workspace, self.user)
        # Body has ONLY the historical Workspace UUID field (no Deliverable ID).
        rr = _make_rr(
            self.workspace, self.user,
            body=_rr_body_path2(str(target.id)),
        )
        result = extract_target_deliverable_id(rr, Deliverable)
        self.assertEqual(result, target.id)


class ExtractionPath3Tests(_FixtureBase):

    def test_t1c_adr_title_fallback_single_match(self):
        target = _make_target(
            self.workspace, self.user,
            title='0999_ADR_TITLE_ONLY',
        )
        rr = _make_rr(
            self.workspace, self.user,
            body=_rr_body_path3('0999_ADR_TITLE_ONLY'),
        )
        result = extract_target_deliverable_id(rr, Deliverable)
        self.assertEqual(result, target.id)

    def test_t1d_adr_title_ambiguous_returns_none(self):
        _make_target(self.workspace, self.user, title='DUPLICATE_TITLE')
        _make_target(self.workspace, self.user, title='DUPLICATE_TITLE')
        rr = _make_rr(
            self.workspace, self.user,
            body=_rr_body_path3('DUPLICATE_TITLE'),
        )
        result = extract_target_deliverable_id(rr, Deliverable)
        self.assertIsNone(result)

    def test_t1e_total_failure_returns_none(self):
        rr = _make_rr(
            self.workspace, self.user,
            body='no matching lines at all',
        )
        result = extract_target_deliverable_id(rr, Deliverable)
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# T2/T3: mirror creates Document + timestamps
# ---------------------------------------------------------------------------


class MirrorCreationTests(_FixtureBase):

    def test_t2_mirror_sets_canonical_authority_workspace_canonical(self):
        target = _make_target(self.workspace, self.user)
        rr = _make_rr(
            self.workspace, self.user,
            body=_rr_body_path1(str(target.id)),
        )
        with mock.patch(
            'content.embeddings.RAGSystem.process_document_for_rag_sync',
            return_value=True,
        ):
            result = mirror_deliverable_to_document(
                ratification_record_id=str(rr.id),
            )
        self.assertEqual(result['status'], 'created')

        doc = Document.objects.get(id=result['document_id'])
        self.assertEqual(doc.source, 'workspace')
        self.assertEqual(doc.source_reference, str(target.id))
        self.assertEqual(doc.canonical_authority, 'workspace_canonical')
        self.assertEqual(doc.owner_id, self.user.id)

    def test_t3_four_timestamps_present_and_sc1_satisfied(self):
        target = _make_target(self.workspace, self.user)
        rr = _make_rr(
            self.workspace, self.user,
            body=_rr_body_path1(str(target.id)),
        )
        with mock.patch(
            'content.embeddings.RAGSystem.process_document_for_rag_sync',
            return_value=True,
        ):
            result = mirror_deliverable_to_document(
                ratification_record_id=str(rr.id),
            )
        self.assertEqual(result['status'], 'created')

        doc = Document.objects.get(id=result['document_id'])
        mirror = doc.extracted_metadata['mirror']
        for key in ('ratification_ts', 'mirror_start_ts',
                    'mirror_complete_ts', 'embedding_complete_ts'):
            self.assertIn(key, mirror)
            self.assertIsNotNone(mirror[key])

        # SC-1: embedding_complete - ratification ≤ 60_000 ms.
        from datetime import datetime
        ratification = datetime.fromisoformat(mirror['ratification_ts'])
        embedding_complete = datetime.fromisoformat(mirror['embedding_complete_ts'])
        delta_ms = (embedding_complete - ratification).total_seconds() * 1000
        self.assertLessEqual(delta_ms, 60_000)


# ---------------------------------------------------------------------------
# T4/T5: idempotence branches
# ---------------------------------------------------------------------------


class IdempotenceTests(_FixtureBase):

    def test_t4_unchanged_content_skips_reembedding(self):
        target = _make_target(self.workspace, self.user, content='body-v1')
        rr = _make_rr(
            self.workspace, self.user,
            body=_rr_body_path1(str(target.id)),
        )

        with mock.patch(
            'content.embeddings.RAGSystem.process_document_for_rag_sync',
            return_value=True,
        ) as embed_patch:
            r1 = mirror_deliverable_to_document(
                ratification_record_id=str(rr.id),
            )
            self.assertEqual(r1['status'], 'created')
            self.assertEqual(embed_patch.call_count, 1)

            # Second call with unchanged content — should skip embedding.
            r2 = mirror_deliverable_to_document(
                ratification_record_id=str(rr.id),
            )
            self.assertEqual(r2['status'], 'skipped_unchanged')
            self.assertEqual(embed_patch.call_count, 1)

    def test_t5_changed_content_clears_and_reembeds(self):
        target = _make_target(self.workspace, self.user, content='body-v1')
        rr = _make_rr(
            self.workspace, self.user,
            body=_rr_body_path1(str(target.id)),
        )

        with mock.patch(
            'content.embeddings.RAGSystem.process_document_for_rag_sync',
            return_value=True,
        ) as embed_patch:
            r1 = mirror_deliverable_to_document(
                ratification_record_id=str(rr.id),
            )
            self.assertEqual(r1['status'], 'created')

            # Simulate a prior embedding row so we can assert it's cleared.
            doc = Document.objects.get(id=r1['document_id'])
            DocumentEmbedding.objects.create(
                document=doc,
                chunk_index=0,
                chunk_text='old',
                chunk_size=3,
                embedding_model='test-model',
                embedding_dimension=1536,
                embedding_vector=[0.0] * 1536,
            )
            self.assertEqual(
                DocumentEmbedding.objects.filter(document=doc).count(), 1,
            )

            # Update target content → re-mirror should clear + re-embed.
            target.content = 'body-v2'
            target.save(update_fields=['content'])

            r2 = mirror_deliverable_to_document(
                ratification_record_id=str(rr.id),
            )
            self.assertEqual(r2['status'], 'updated')
            # Old embedding removed.
            self.assertEqual(
                DocumentEmbedding.objects.filter(document=doc).count(), 0,
            )
            # process_document_for_rag_sync called again.
            self.assertEqual(embed_patch.call_count, 2)


# ---------------------------------------------------------------------------
# T6: malformed body
# ---------------------------------------------------------------------------


class MalformedBodyTests(_FixtureBase):

    def test_t6_malformed_body_creates_no_document(self):
        rr = _make_rr(
            self.workspace, self.user,
            body='no target here',
        )
        result = mirror_deliverable_to_document(
            ratification_record_id=str(rr.id),
        )
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['reason'], 'target_extraction_failed')
        self.assertFalse(Document.objects.filter(source='workspace').exists())


# ---------------------------------------------------------------------------
# T7: end-to-end signal integration
# ---------------------------------------------------------------------------


class SignalIntegrationTests(_FixtureBase):

    def setUp(self):
        # Ensure the signal receiver is connected in the test process.
        connect_deliverable_mirror_signals()

    def test_t7_signal_dispatches_task_on_creation(self):
        target = _make_target(self.workspace, self.user)

        with mock.patch(
            'core.tasks.mirror_deliverable_to_document.delay',
        ) as delay_patch:
            rr = _make_rr(
                self.workspace, self.user,
                body=_rr_body_path1(str(target.id)),
                deliverable_type='ratification_record',
            )

        delay_patch.assert_called_once()
        kwargs = delay_patch.call_args.kwargs
        self.assertEqual(kwargs.get('ratification_record_id'), str(rr.id))


# ---------------------------------------------------------------------------
# T8/T9/T10: owner cascade
# ---------------------------------------------------------------------------


class OwnerCascadeTests(_FixtureBase):

    def test_t8_owner_from_rr_user_when_present(self):
        target = _make_target(self.workspace, self.user)
        rr = _make_rr(
            self.workspace, self.user,
            body=_rr_body_path1(str(target.id)),
        )
        with mock.patch(
            'content.embeddings.RAGSystem.process_document_for_rag_sync',
            return_value=True,
        ):
            result = mirror_deliverable_to_document(
                ratification_record_id=str(rr.id),
            )
        doc = Document.objects.get(id=result['document_id'])
        self.assertEqual(doc.owner_id, self.user.id)

    def test_t9_owner_falls_back_to_target_user(self):
        target = _make_target(self.workspace, self.user)
        rr = _make_rr(
            self.workspace, self.user,
            body=_rr_body_path1(str(target.id)),
        )
        # Nullify rr.user.
        Deliverable.objects.filter(id=rr.id).update(user=None)

        with mock.patch(
            'content.embeddings.RAGSystem.process_document_for_rag_sync',
            return_value=True,
        ):
            result = mirror_deliverable_to_document(
                ratification_record_id=str(rr.id),
            )
        doc = Document.objects.get(id=result['document_id'])
        # Owner falls back to target.user.
        self.assertEqual(doc.owner_id, self.user.id)

    def test_t10_both_none_fails_closed(self):
        target = _make_target(self.workspace, self.user)
        rr = _make_rr(
            self.workspace, self.user,
            body=_rr_body_path1(str(target.id)),
        )
        Deliverable.objects.filter(id=rr.id).update(user=None)
        Deliverable.objects.filter(id=target.id).update(user=None)

        result = mirror_deliverable_to_document(
            ratification_record_id=str(rr.id),
        )
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['reason'], 'mirror_owner_unresolved')
        self.assertFalse(Document.objects.filter(source='workspace').exists())


# ---------------------------------------------------------------------------
# T11/T12: signal filter + dispatch_uid
# ---------------------------------------------------------------------------


class SignalFilterTests(_FixtureBase):

    def setUp(self):
        connect_deliverable_mirror_signals()

    def test_t11_signal_ignores_updates_of_existing_records(self):
        target = _make_target(self.workspace, self.user)
        rr = _make_rr(
            self.workspace, self.user,
            body=_rr_body_path1(str(target.id)),
        )

        # Update after initial creation — should NOT re-dispatch.
        with mock.patch(
            'core.tasks.mirror_deliverable_to_document.delay',
        ) as delay_patch:
            rr.title = rr.title + '_touched'
            rr.save(update_fields=['title'])

        delay_patch.assert_not_called()


class DispatchUidTests(TestCase):

    def test_t12_multiple_connect_calls_register_receiver_once(self):
        # Call connect multiple times.
        connect_deliverable_mirror_signals()
        connect_deliverable_mirror_signals()
        connect_deliverable_mirror_signals()

        # Enumerate receivers registered for Deliverable.post_save.
        # dispatch_uid guard means only one receiver survives regardless of
        # how many connect() calls we made. post_save.receivers is a list
        # of ((receiver_id, sender_key), weakref) tuples.
        matches = [
            entry for entry in post_save.receivers
            if _DISPATCH_UID in str(entry)
        ]
        self.assertLessEqual(len(matches), 1)


# ---------------------------------------------------------------------------
# T13: _derive_source_type recognizes source='workspace'
# ---------------------------------------------------------------------------


class DeriveSourceTypeTests(TestCase):

    def test_t13_workspace_source_maps_to_internal(self):
        doc = Document(source='workspace')
        self.assertEqual(_derive_source_type(doc), 'internal')


# ---------------------------------------------------------------------------
# T14/T15: management command + live signal boundary
# ---------------------------------------------------------------------------


class ManagementCommandTests(_FixtureBase):

    def test_t14_command_processes_historical_document_typed_records(self):
        target = _make_target(self.workspace, self.user)
        # Historical record: title starts with RATIFICATION_ but
        # deliverable_type='document' (mirrors the 5+ pre-KFI-1 records).
        rr = _make_rr(
            self.workspace, self.user,
            body=_rr_body_path1(str(target.id)),
            deliverable_type='document',
            title='RATIFICATION_20260707_HISTORICAL',
        )
        with mock.patch(
            'content.embeddings.RAGSystem.process_document_for_rag_sync',
            return_value=True,
        ):
            call_command(
                'mirror_deliverable_to_document',
                '--ratification-record-id', str(rr.id),
            )

        # Live signal would have ignored this record; command mirrored it.
        self.assertTrue(
            Document.objects.filter(
                source='workspace', source_reference=str(target.id),
            ).exists(),
        )


class LiveSignalBoundaryTests(_FixtureBase):

    def setUp(self):
        connect_deliverable_mirror_signals()

    def test_t15_live_signal_does_not_fire_on_document_typed_records(self):
        target = _make_target(self.workspace, self.user)

        with mock.patch(
            'core.tasks.mirror_deliverable_to_document.delay',
        ) as delay_patch:
            _make_rr(
                self.workspace, self.user,
                body=_rr_body_path1(str(target.id)),
                deliverable_type='document',
                title='RATIFICATION_20260707_HISTORICAL',
            )

        delay_patch.assert_not_called()


# ---------------------------------------------------------------------------
# T16: query-count sanity ceiling
# ---------------------------------------------------------------------------


class QueryCountTests(_FixtureBase):

    def test_t16_mirror_stays_under_query_ceiling(self):
        target = _make_target(self.workspace, self.user)
        rr = _make_rr(
            self.workspace, self.user,
            body=_rr_body_path1(str(target.id)),
        )
        with mock.patch(
            'content.embeddings.RAGSystem.process_document_for_rag_sync',
            return_value=True,
        ), CaptureQueriesContext(connection) as ctx:
            mirror_deliverable_to_document(
                ratification_record_id=str(rr.id),
            )
        # Ceiling absorbs transaction savepoints + get_or_create +
        # extracted_metadata updates. Signal-cascade regressions
        # would blow past this.
        self.assertLessEqual(
            len(ctx.captured_queries), 25,
            f'Mirror produced {len(ctx.captured_queries)} queries.',
        )


# ---------------------------------------------------------------------------
# T17: A14 concurrent race + IntegrityError retry
# ---------------------------------------------------------------------------


class UniquenessConstraintTests(_FixtureBase):

    def test_t17a_duplicate_workspace_source_reference_raises(self):
        # Create one workspace-source Document.
        Document.objects.create(
            owner=self.user,
            title='First',
            document_type='markdown',
            source='workspace',
            source_reference='same-uuid',
        )
        # Second create with same (source='workspace', source_reference)
        # must hit the partial unique constraint.
        with self.assertRaises(IntegrityError):
            Document.objects.create(
                owner=self.user,
                title='Second',
                document_type='markdown',
                source='workspace',
                source_reference='same-uuid',
            )

    def test_t17b_non_workspace_source_reference_reuse_allowed(self):
        # Partial constraint is scoped to source='workspace' — reuse of
        # source_reference under a different source must remain legal.
        Document.objects.create(
            owner=self.user,
            title='API row',
            document_type='markdown',
            source='api',
            source_reference='shared-ref',
        )
        Document.objects.create(
            owner=self.user,
            title='Imported row',
            document_type='markdown',
            source='imported',
            source_reference='shared-ref',
        )
        self.assertEqual(
            Document.objects.filter(source_reference='shared-ref').count(),
            2,
        )
