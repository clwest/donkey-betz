"""Session 1225 P2 — Celery beat task wrapper test.

Verifies the thin wrapper at core.tasks.generate_outreach_drafts_daily
calls OpportunityDraftGenerator.generate with the right kwargs and
returns its result unchanged. The generator itself is exhaustively
covered by core.tests.test_outreach_generation.
"""
from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase

from core.tasks import generate_outreach_drafts_daily


class GenerateOutreachDraftsDailyTests(TestCase):
    def test_calls_generator_with_defaults(self):
        with patch(
            'core.services.ops_autopilot.OpportunityDraftGenerator.generate',
            return_value={'created': 3, 'daily_cap': 5},
        ) as mock_gen:
            result = generate_outreach_drafts_daily.apply().get()
        mock_gen.assert_called_once_with(limit=5, scope='all', offers=None)
        self.assertEqual(result['created'], 3)
        self.assertEqual(result['daily_cap'], 5)

    def test_passes_through_kwargs(self):
        with patch(
            'core.services.ops_autopilot.OpportunityDraftGenerator.generate',
            return_value={'created': 1},
        ) as mock_gen:
            generate_outreach_drafts_daily.apply(
                kwargs={'limit': 1, 'scope': 'mine', 'offers': ['consulting']},
            ).get()
        mock_gen.assert_called_once_with(
            limit=1, scope='mine', offers=['consulting'],
        )
