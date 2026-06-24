"""
Session 1224 P1 — OpportunityDraftGenerator unit tests.

Covers:
  - contactability gate (url-with-domain vs metadata-only vs nothing)
  - synthetic SpiderData seed idempotency
  - candidate selection excludes opportunities with existing touch-1 drafts
  - daily cap halts further generation
  - round-robin offer distribution across multiple candidates
  - fallback email used when LLM raises
"""
from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models_outreach import OutreachDraft
from core.models_unified_system import Opportunity, SpiderData
from core.services.ops_autopilot.outreach_generation import (
    OpportunityDraftGenerator,
)

User = get_user_model()


def _llm_returns(subject: str, body: str):
    """Patch render_email to return a stable payload, skipping the LLM call."""
    return patch.object(
        OpportunityDraftGenerator,
        'render_email',
        return_value={'subject': subject, 'body': body, 'fallback': False},
    )


class OpportunityDraftGeneratorContactabilityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_outreach', password='x',
        )

    def _make_opp(self, **overrides):
        defaults = dict(
            user=self.user,
            title='Test opportunity',
            opportunity_type='gig',
            source='test',
            description='Test description',
            status='active',
            match_score=50,
        )
        defaults.update(overrides)
        return Opportunity.objects.create(**defaults)

    def test_url_with_domain_is_contactable(self):
        opp = self._make_opp(url='https://example.com/jobs/123')
        self.assertTrue(OpportunityDraftGenerator.is_contactable(opp))

    def test_metadata_email_is_contactable(self):
        opp = self._make_opp(metadata={'contact_email': 'a@b.com'})
        self.assertTrue(OpportunityDraftGenerator.is_contactable(opp))

    def test_company_plus_domain_metadata_is_contactable(self):
        opp = self._make_opp(metadata={
            'company_name': 'Acme', 'domain': 'acme.com',
        })
        self.assertTrue(OpportunityDraftGenerator.is_contactable(opp))

    def test_company_only_is_not_contactable(self):
        opp = self._make_opp(metadata={'company_name': 'Acme'})
        self.assertFalse(OpportunityDraftGenerator.is_contactable(opp))

    def test_no_url_no_metadata_is_not_contactable(self):
        opp = self._make_opp()
        self.assertFalse(OpportunityDraftGenerator.is_contactable(opp))


class OpportunityDraftGeneratorSeedTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='seed_user', password='x')
        self.opp = Opportunity.objects.create(
            user=self.user,
            title='Seed test',
            opportunity_type='gig',
            source='test',
            description='desc',
            url='https://example.com',
        )

    def test_ensure_spider_data_seed_creates_row(self):
        seed = OpportunityDraftGenerator.ensure_spider_data_seed(self.opp)
        self.assertEqual(
            seed.spider_name,
            OpportunityDraftGenerator.SEED_SPIDER_NAME,
        )
        self.assertEqual(seed.data_type, OpportunityDraftGenerator.SEED_DATA_TYPE)
        self.assertEqual(seed.raw_data['opportunity_id'], str(self.opp.id))

    def test_ensure_spider_data_seed_is_idempotent(self):
        first = OpportunityDraftGenerator.ensure_spider_data_seed(self.opp)
        second = OpportunityDraftGenerator.ensure_spider_data_seed(self.opp)
        self.assertEqual(first.id, second.id)
        self.assertEqual(SpiderData.objects.filter(
            spider_name=OpportunityDraftGenerator.SEED_SPIDER_NAME,
            raw_data__opportunity_id=str(self.opp.id),
        ).count(), 1)


class OpportunityDraftGeneratorSelectionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='sel_user', password='x')

    def _make_opp(self, title, **overrides):
        defaults = dict(
            user=self.user,
            title=title,
            opportunity_type='gig',
            source='test',
            description='desc',
            status='active',
            url='https://example.com/' + title,
            match_score=50,
        )
        defaults.update(overrides)
        return Opportunity.objects.create(**defaults)

    def test_excludes_opportunities_with_existing_touch_one_draft(self):
        opp_with_draft = self._make_opp('with-draft')
        seed = OpportunityDraftGenerator.ensure_spider_data_seed(opp_with_draft)
        OutreachDraft.objects.create(
            spider_data_id=seed.id,
            opportunity=opp_with_draft,
            lead_title='existing',
            body_text='body',
            touch_number=1,
            status='draft',
        )
        opp_fresh = self._make_opp('fresh')

        qs = OpportunityDraftGenerator.select_candidate_queryset(scope='all')
        ids = list(qs.values_list('id', flat=True))
        self.assertIn(opp_fresh.id, ids)
        self.assertNotIn(opp_with_draft.id, ids)

    def test_scope_mine_filters_to_user(self):
        other = User.objects.create_user(username='other', password='x')
        Opportunity.objects.create(
            user=other,
            title='other',
            opportunity_type='gig',
            source='test',
            description='desc',
            status='active',
            url='https://example.com/other',
        )
        mine = self._make_opp('mine')

        qs = OpportunityDraftGenerator.select_candidate_queryset(
            scope='mine', user=self.user,
        )
        ids = list(qs.values_list('id', flat=True))
        self.assertEqual(ids, [mine.id])


class OpportunityDraftGeneratorGenerateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='gen_user', password='x')

    def _make_opp(self, suffix, **overrides):
        defaults = dict(
            user=self.user,
            title=f'Gen {suffix}',
            opportunity_type='gig',
            source='test',
            description='desc',
            status='active',
            url=f'https://example{suffix}.com',
            match_score=50,
        )
        defaults.update(overrides)
        return Opportunity.objects.create(**defaults)

    def test_generate_creates_drafts_up_to_limit(self):
        for i in range(3):
            self._make_opp(i)

        with _llm_returns('Sub', 'Body'):
            result = OpportunityDraftGenerator.generate(limit=2)

        self.assertEqual(result['created'], 2)
        self.assertEqual(result['daily_cap'], 5)
        self.assertEqual(OutreachDraft.objects.count(), 2)

    def test_generate_skips_uncontactable(self):
        # No url, no metadata — uncontactable
        Opportunity.objects.create(
            user=self.user,
            title='dead',
            opportunity_type='gig',
            source='test',
            description='desc',
            status='active',
        )
        self._make_opp('good')

        with _llm_returns('Sub', 'Body'):
            result = OpportunityDraftGenerator.generate(limit=5)

        self.assertEqual(result['created'], 1)
        self.assertEqual(result['skipped_uncontactable'], 1)

    def test_generate_respects_daily_cap(self):
        # Pre-populate today with cap-many drafts from this generator
        seed_opp = self._make_opp('seed')
        seed = OpportunityDraftGenerator.ensure_spider_data_seed(seed_opp)
        for i in range(OpportunityDraftGenerator.DAILY_GENERATE_CAP):
            OutreachDraft.objects.create(
                spider_data_id=seed.id,
                lead_title=f'pre {i}',
                lead_source=OpportunityDraftGenerator.SEED_SPIDER_NAME,
                body_text='body',
                touch_number=1,
                status='draft',
            )
        # Add a fresh candidate the cap should block
        self._make_opp('new')

        with _llm_returns('Sub', 'Body'):
            result = OpportunityDraftGenerator.generate(limit=5)

        self.assertEqual(result['created'], 0)
        self.assertEqual(result.get('note'), 'daily cap reached')

    def test_generate_round_robins_offers(self):
        for i in range(3):
            self._make_opp(i)

        with _llm_returns('Sub', 'Body'):
            result = OpportunityDraftGenerator.generate(
                limit=3,
                offers=['ai_automation', 'content_engine', 'consulting'],
            )

        offers_used = [d['offer_key'] for d in result['drafts']]
        self.assertEqual(
            sorted(offers_used),
            ['ai_automation', 'consulting', 'content_engine'],
        )

    def test_render_email_fallback_used_when_llm_fails(self):
        opp = self._make_opp('fall', metadata={'company_name': 'Acme'})
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            side_effect=RuntimeError('llm down'),
        ):
            rendered = OpportunityDraftGenerator.render_email(opp, 'consulting')
        self.assertTrue(rendered['fallback'])
        self.assertIn('Chris / Donkey Betz', rendered['body'])
