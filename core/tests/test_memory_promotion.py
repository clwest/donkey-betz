"""Tests for the Durable Memory Promotion scoring and trigger logic."""

import pytest
from core.services.memory_promotion_service import (
    score_for_promotion,
    extract_promotion_content,
    _contains_secret,
    _infer_tags,
)


class TestScoring:
    """Test promotion score calculations."""

    def test_milestone_only(self):
        score, details = score_for_promotion("We deployed the new version to Railway")
        assert score >= 3
        assert details['milestones']

    def test_milestone_with_identifier(self):
        score, details = score_for_promotion(
            "Deployed v2.3.1 to https://donkey-betz-platform-production.up.railway.app"
        )
        assert score >= 7  # milestone(3) + version(2) + base_url(2)
        assert 'version_build' in details['identifiers']
        assert 'base_url' in details['identifiers']

    def test_bundle_id_with_milestone(self):
        score, details = score_for_promotion(
            "Submitted to TestFlight — com.donkeyking.betz v1.2.0 (42)"
        )
        assert score >= 7  # milestone(3) + bundle_id(2) + version(2)
        assert 'bundle_id' in details['identifiers']

    def test_wiring_statement(self):
        score, details = score_for_promotion(
            "frontend calls endpoint /api/pa/chat/ for PA messages"
        )
        assert score >= 2
        assert details['wiring']

    def test_repo_slug(self):
        score, details = score_for_promotion(
            "Deployed clwest/unified-donkey-betz to production"
        )
        assert score >= 5  # milestone(3) + repo_slug(2)
        assert 'repo_slug' in details['identifiers']

    def test_worker_queue_mention(self):
        score, details = score_for_promotion(
            "celery-pa worker restarted with new config"
        )
        assert 'worker_queue' in details['identifiers']

    def test_low_score_generic_message(self):
        score, details = score_for_promotion(
            "Can you help me write a blog post about cooking?"
        )
        assert score <= 4

    def test_secret_blocked(self):
        score, details = score_for_promotion(
            "Deployed with API key sk-1234567890abcdefghijklmnop"
        )
        assert score == 0
        assert details.get('blocked') == 'contains_secret'

    def test_jwt_blocked(self):
        score, details = score_for_promotion(
            "Token is eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        )
        assert score == 0

    def test_commit_sha_with_deploy(self):
        score, details = score_for_promotion(
            "Deployed commit abc1234 to production"
        )
        assert score >= 5
        assert 'commit_sha' in details['identifiers']

    def test_railway_service_name(self):
        score, details = score_for_promotion(
            "Railway service: celery-content is now running with --pool=prefork"
        )
        assert 'railway_service' in details['identifiers'] or 'worker_queue' in details['identifiers']

    def test_multiple_identifiers_capped(self):
        """Identifier score is capped at +6."""
        score, details = score_for_promotion(
            "Deployed v1.0.0 from clwest/betz to https://app.up.railway.app "
            "with celery-worker on port PORT=8080 commit abcdef1"
        )
        assert score <= 10

    def test_ci_wiring(self):
        score, details = score_for_promotion(
            "CI workflow is github-actions deploy.yml on push to main"
        )
        assert details['wiring']

    def test_start_command_wiring(self):
        score, details = score_for_promotion(
            "start command: daphne -b 0.0.0.0 -p 8000 core.asgi:application"
        )
        assert details['wiring']


class TestSecretDetection:

    def test_api_key(self):
        assert _contains_secret("sk-abc123456789012345678901234567")

    def test_github_token(self):
        assert _contains_secret("ghp_abcdefghij1234567890abcdefghij123456")

    def test_private_key(self):
        pem_header = "-----BEGIN %s KEY-----" % "PRIVATE"
        assert _contains_secret(pem_header)

    def test_password_assignment(self):
        assert _contains_secret("password=mysecretpass123")

    def test_clean_text(self):
        assert not _contains_secret("Deployed v2.0 to Railway")


class TestTagInference:

    def test_deploy_tags(self):
        tags = _infer_tags("deployed to railway production")
        assert 'deploy' in tags
        assert 'railway' in tags

    def test_mobile_tags(self):
        tags = _infer_tags("submitted to TestFlight iOS build")
        assert 'mobile' in tags
        assert 'testflight' in tags

    def test_repo_tags(self):
        tags = _infer_tags("pushed to github repository")
        assert 'repo' in tags

    def test_max_five_tags(self):
        tags = _infer_tags(
            "deployed to railway after github CI pipeline with rollback migration testflight"
        )
        assert len(tags) <= 5


class TestContentExtraction:

    def test_structured_output(self):
        details = {
            'milestones': ['deployed'],
            'identifiers': {
                'base_url': ['https://app.up.railway.app'],
                'version_build': ['v2.3.1'],
            },
            'wiring': [],
        }
        content = extract_promotion_content("some text", details)
        assert 'Event: deployed' in content
        assert 'Base Url: https://app.up.railway.app' in content
        assert 'Version Build: v2.3.1' in content

    def test_wiring_output(self):
        details = {
            'milestones': [],
            'identifiers': {},
            'wiring': ['frontend calls /api/pa/chat/'],
        }
        content = extract_promotion_content("some text", details)
        assert 'Topology:' in content
