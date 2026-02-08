"""
Phase 4: Content Deliberation Pipeline Tests

8 tests covering claims, validation, deliberation flow, and graceful degradation.
"""

import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.test import TestCase
from django.utils import timezone

from core.services.content_claims import ClaimsPack, SpiderClaim, make_claim_id
from core.services.content_review_panel_v2 import (
    _make_fail_payload,
    validate_review_payload,
)


class TestClaimsPack(TestCase):
    """Tests for ClaimsPack and SpiderClaim dataclasses."""

    def test_claims_pack_builds(self):
        """Builder returns ClaimsPack with unique deterministic claim_ids and URLs."""
        claims = [
            SpiderClaim(
                claim_id=make_claim_id('https://example.com/article-1', 'AI Market Grows'),
                claim_text='AI market projected to reach $500B',
                source_url='https://example.com/article-1',
                source_title='AI Market Grows',
                spider_name='tech_spider',
                confidence=0.7,
                claim_type='factual',
            ),
            SpiderClaim(
                claim_id=make_claim_id('https://example.com/article-2', 'Robots Rising'),
                claim_text='Robots are becoming more capable',
                source_url='https://example.com/article-2',
                source_title='Robots Rising',
                spider_name='news_spider',
                confidence=0.5,
                claim_type='analytical',
            ),
        ]
        pack = ClaimsPack(
            topic='AI trends',
            assembled_at=timezone.now().isoformat(),
            claims=claims,
            sources=[{'url': c.source_url, 'title': c.source_title} for c in claims],
            stats={'total_claims': 2, 'factual': 1, 'analytical': 1, 'speculative': 0},
        )

        assert len(pack.claims) == 2
        # All claim_ids are unique
        ids = [c.claim_id for c in pack.claims]
        assert len(set(ids)) == 2
        # All claim_ids start with C-
        assert all(cid.startswith('C-') for cid in ids)
        # All have URLs
        assert all(c.source_url for c in pack.claims)

    def test_claim_id_deterministic(self):
        """Same URL+title produces the same claim_id across calls."""
        url = 'https://example.com/test-article'
        title = 'Test Article Title'

        id1 = make_claim_id(url, title)
        id2 = make_claim_id(url, title)
        assert id1 == id2

        # Different URL -> different ID
        id3 = make_claim_id('https://example.com/other', title)
        assert id1 != id3

        # Normalization: https vs http, trailing slash
        id4 = make_claim_id('http://example.com/test-article/', title)
        assert id4 == id1  # Same after normalization

    def test_claims_pack_prompt_block(self):
        """to_prompt_block() contains [C- markers."""
        claim = SpiderClaim(
            claim_id='C-abc1234567',
            claim_text='Test claim about AI',
            source_url='https://example.com',
            confidence=0.7,
            claim_type='factual',
        )
        pack = ClaimsPack(
            topic='test',
            assembled_at=timezone.now().isoformat(),
            claims=[claim],
        )

        block = pack.to_prompt_block()
        assert '[C-abc1234567]' in block
        assert 'Test claim about AI' in block
        assert 'CLAIMS DATA' in block


class TestReviewPayloadValidation(TestCase):
    """Tests for structured reviewer output validation."""

    def test_review_payload_validation_pass(self):
        """Valid JSON passes validate_review_payload."""
        payload = {
            'reviewer': 'SkepticReviewer',
            'verdict': 'PASS',
            'top_issues': [
                {
                    'type': 'generic',
                    'detail': 'Some sections are too generic',
                    'claim_ids': [],
                    'severity': 'low',
                }
            ],
            'required_changes': ['Add more specific examples'],
            'suggested_edits': ['Consider restructuring section 3'],
            'confidence': 0.85,
        }

        is_valid, errors = validate_review_payload(payload)
        assert is_valid is True
        assert errors == []

    def test_review_payload_validation_fail(self):
        """Invalid/missing keys fail validation."""
        # Missing required keys
        payload = {
            'reviewer': 'SkepticReviewer',
            'verdict': 'INVALID_VERDICT',  # invalid
            # missing: top_issues, required_changes, suggested_edits, confidence
        }

        is_valid, errors = validate_review_payload(payload)
        assert is_valid is False
        assert len(errors) > 0
        # Should flag invalid verdict
        assert any('verdict' in e for e in errors)
        # Should flag missing keys
        assert any('missing' in e for e in errors)

    def test_reviewer_failure_becomes_fail_verdict(self):
        """Reviewer error -> synthetic FAIL payload returned."""
        fail = _make_fail_payload('TestReviewer', 'LLM error: timeout')

        assert fail['reviewer'] == 'TestReviewer'
        assert fail['verdict'] == 'FAIL'
        assert fail['confidence'] == 0.0
        assert len(fail['top_issues']) == 1
        assert fail['top_issues'][0]['type'] == 'reviewer_error'
        assert 'LLM error' in fail['top_issues'][0]['detail']

        # Validate it passes our own validation
        is_valid, errors = validate_review_payload(fail)
        assert is_valid is True


class TestDeliberationRunner(TestCase):
    """Tests for the full deliberation pipeline."""

    @patch('core.services.content_deliberation_runner.ContentDeliberationRunner._run_publish_gate')
    @patch('core.services.content_deliberation_runner.ContentDeliberationRunner._run_review_conversation')
    @patch('core.services.content_deliberation_runner.ContentDeliberationRunner._generate_draft')
    @patch('core.services.claims_pack_builder.ClaimsPackBuilder.build')
    def test_selfblog_links_deliberation(
        self, mock_build, mock_draft, mock_review, mock_gate
    ):
        """After runner, stats_snapshot['deliberation']['session_id'] is set."""
        from core.models_unified_system import SelfBlog

        # Setup mocks
        mock_build.return_value = ClaimsPack(
            topic='test',
            assembled_at=timezone.now().isoformat(),
            claims=[SpiderClaim(
                claim_id='C-test123456',
                claim_text='Test claim',
                source_url='https://example.com',
                confidence=0.7,
                claim_type='factual',
            )],
            sources=[{'url': 'https://example.com', 'title': 'Test'}],
            stats={'total_claims': 1, 'factual': 1, 'speculative': 0, 'analytical': 0},
        )

        mock_draft.return_value = (
            'This is a test blog about AI trends [C-test123456].',
            {
                'title': 'Test Blog Post',
                'intro': 'Test intro',
                'sections': [{'header': 'Section 1', 'content': 'Content'}],
                'conclusion': 'Test conclusion',
                'full_text': 'This is a test blog about AI trends [C-test123456].',
                'meta_description': 'Test blog post',
                'keywords': ['AI', 'trends'],
            },
        )

        fake_session_id = str(uuid.uuid4())
        mock_review.return_value = (
            [
                {'reviewer': 'SkepticReviewer', 'verdict': 'PASS',
                 'top_issues': [], 'required_changes': [], 'suggested_edits': [],
                 'confidence': 0.9},
                {'reviewer': 'FactCheckReviewer', 'verdict': 'PASS',
                 'top_issues': [], 'required_changes': [], 'suggested_edits': [],
                 'confidence': 0.85},
            ],
            fake_session_id,
            {'chosen_path': 'PUBLISH this blog', 'decision_owner': 'EditorAgent'},
        )

        mock_gate.return_value = MagicMock(
            decision='publish',
            quality_score=0.85,
            novelty_score=0.7,
            structure_score=0.8,
            notes='Good quality',
        )

        from core.services.content_deliberation_runner import ContentDeliberationRunner
        runner = ContentDeliberationRunner()
        result = runner.run_blog(topic='AI trends', voice='professional')

        assert result['selfblog_id'] is not None
        assert result['deliberation_session_id'] == fake_session_id
        assert result['decision'] == 'PUBLISH'

        # Verify blog has deliberation metadata
        blog = SelfBlog.objects.get(id=result['selfblog_id'])
        delib = blog.stats_snapshot.get('deliberation', {})
        assert delib['session_id'] == fake_session_id
        assert delib['decision'] == 'PUBLISH'
        assert delib['claims_count'] == 1

    @patch('core.services.content_deliberation_runner.ContentDeliberationRunner._run_review_conversation')
    @patch('core.services.content_deliberation_runner.ContentDeliberationRunner._generate_draft')
    @patch('core.services.claims_pack_builder.ClaimsPackBuilder.build')
    def test_graceful_degradation_panel_failed(
        self, mock_build, mock_draft, mock_review
    ):
        """All reviewers fail -> blog saved as draft with 'panel_failed'."""
        from core.models_unified_system import SelfBlog

        mock_build.return_value = ClaimsPack(
            topic='test',
            assembled_at=timezone.now().isoformat(),
            claims=[],
            sources=[],
            stats={'total_claims': 0, 'factual': 0, 'speculative': 0, 'analytical': 0},
        )

        mock_draft.return_value = (
            'Draft text for testing.',
            {
                'title': 'Test Draft',
                'intro': 'Intro',
                'sections': [],
                'conclusion': 'Conclusion',
                'full_text': 'Draft text for testing.',
                'meta_description': '',
                'keywords': [],
            },
        )

        # All reviewers return FAIL with reviewer_error
        mock_review.return_value = (
            [
                _make_fail_payload('SkepticReviewer', 'LLM timeout'),
                _make_fail_payload('FactCheckReviewer', 'LLM timeout'),
            ],
            None,  # no session ID
            None,  # no mandate
        )

        from core.services.content_deliberation_runner import ContentDeliberationRunner
        runner = ContentDeliberationRunner()
        result = runner.run_blog(topic='test topic', voice='casual')

        assert result['selfblog_id'] is not None
        assert result['status'] == 'draft'

        # Verify blog is saved with panel_failed gate_notes
        blog = SelfBlog.objects.get(id=result['selfblog_id'])
        assert blog.status == 'draft'
        assert blog.gate_notes == 'panel_failed'
