"""LegalCase + LegalDocument model tests (S2802 Phase 2).

Guards against schema drift on the models that back the Colorado Family Law
agent's persistence layer:
  M1  LegalCase.user FK → user CASCADE delete removes the case
  M2  LegalDocument.case FK → case DELETE sets doc.case = NULL (SET_NULL, not CASCADE)
  M2b LegalDocument.user FK → user CASCADE delete removes doc
  M3  LegalDocument.document_type choices — all 10 canonical values accepted;
      unrecognized value fails full_clean()
  M4  LegalDocument.status choices + default='draft'
  M5  LegalDocument default ordering: `-created_at` (newest first)

Model source: core/models_unified_system.py (LegalCase line 17114, LegalDocument line 17252).
Meta: LegalDocument ordering=['-created_at']; case on_delete=SET_NULL; user on_delete=CASCADE.

Run: python manage.py test core.tests.test_legal_models -v2
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import LegalCase, LegalDocument

User = get_user_model()


class LegalModelSchemaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='legal_model_test_s2802', password='x')
        cls.case = LegalCase.objects.create(
            user=cls.user,
            case_type='custody',
            title='Test Case',
            court='Denver District Court',
            county='Denver',
            jurisdiction='Colorado',
        )

    # ---------------------------------------------------------------- M1
    def test_m1_case_user_fk_on_delete_is_cascade(self):
        # Assert schema config directly rather than triggering cross-app
        # cascade delete (User FK reverse-cascades pull in every model with
        # a User FK, including apps whose migrations are missing in the
        # test DB — out of scope for this arc).
        from django.db.models import CASCADE
        self.assertIs(
            LegalCase._meta.get_field('user').remote_field.on_delete,
            CASCADE,
            'LegalCase.user must be on_delete=CASCADE',
        )

    # ---------------------------------------------------------------- M2
    def test_m2_document_case_set_null_on_delete(self):
        doc = LegalDocument.objects.create(
            user=self.user,
            case=self.case,
            document_type='motion',
            title='Motion Test',
            content='body',
        )
        LegalCase.objects.filter(id=self.case.id).delete()
        doc.refresh_from_db()
        self.assertIsNone(doc.case_id, 'doc.case must be SET NULL (not CASCADE) on LegalCase delete')

    def test_m2b_document_user_fk_on_delete_is_cascade(self):
        from django.db.models import CASCADE
        self.assertIs(
            LegalDocument._meta.get_field('user').remote_field.on_delete,
            CASCADE,
            'LegalDocument.user must be on_delete=CASCADE',
        )

    # ---------------------------------------------------------------- M3
    def test_m3_document_type_choices_all_ten_accepted(self):
        for choice in ['motion', 'email', 'declaration', 'checklist', 'response',
                       'petition', 'agreement', 'letter', 'notes', 'other']:
            doc = LegalDocument(
                user=self.user,
                document_type=choice,
                title=f'T {choice}',
                content='body',
                generation_context={'test': True},
            )
            doc.full_clean()  # should not raise

    def test_m3b_document_type_invalid_choice_rejected(self):
        doc = LegalDocument(
            user=self.user,
            document_type='not_a_real_type',
            title='Bad',
            content='body',
            generation_context={'test': True},
        )
        with self.assertRaises(ValidationError):
            doc.full_clean()

    # ---------------------------------------------------------------- M4
    def test_m4_status_default_and_choices(self):
        doc = LegalDocument.objects.create(
            user=self.user,
            document_type='motion',
            title='Status Test',
            content='body',
        )
        self.assertEqual(doc.status, 'draft', 'LegalDocument.status must default to "draft"')

        for choice in ['draft', 'review', 'finalized', 'filed', 'sent', 'archived']:
            doc = LegalDocument(
                user=self.user,
                document_type='motion',
                title=f'S {choice}',
                content='body',
                status=choice,
                generation_context={'test': True},
            )
            doc.full_clean()

    def test_m4b_status_invalid_rejected(self):
        doc = LegalDocument(
            user=self.user,
            document_type='motion',
            title='Bad status',
            content='body',
            status='not_a_status',
            generation_context={'test': True},
        )
        with self.assertRaises(ValidationError):
            doc.full_clean()

    # ---------------------------------------------------------------- M5
    def test_m5_default_ordering_newest_first(self):
        older = LegalDocument.objects.create(
            user=self.user,
            document_type='motion',
            title='Older',
            content='old',
        )
        # Bump created_at backward by 1h to force ordering signal
        LegalDocument.objects.filter(id=older.id).update(
            created_at=timezone.now() - timedelta(hours=1)
        )
        newer = LegalDocument.objects.create(
            user=self.user,
            document_type='motion',
            title='Newer',
            content='new',
        )

        ordered = list(LegalDocument.objects.filter(user=self.user).values_list('id', flat=True))
        self.assertEqual(
            ordered[:2], [newer.id, older.id],
            'Default ordering must be -created_at (newest first)',
        )
