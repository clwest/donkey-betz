# pyright: reportMissingImports=false, reportGeneralTypeIssues=false
"""
Tests for /api/documents/ingest-url/ endpoint.

Verifies that failed URL processing returns 400 (not 500) with the correct
error message — regression test for the ProcessingResult.error vs
.error_message AttributeError bug.
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import pytest
from unittest.mock import patch
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from content.processors import ProcessingResult

pytestmark = pytest.mark.django_db

User = get_user_model()


def _get_user():
    return (
        User.objects.filter(is_superuser=True).first()
        or User.objects.first()
        or User.objects.create_user(username="testuser", email="test@example.com")
    )


def _make_request(user, data):
    """Build a DRF-compatible POST request with authentication."""
    factory = APIRequestFactory()
    request = factory.post(
        "/api/documents/ingest-url/",
        data=data,
        format="json",
    )
    force_authenticate(request, user=user)
    return request


class TestIngestUrlFailurePath:
    """Regression tests: failed ProcessingResult must yield 400, not 500."""

    def test_single_page_processing_failure_returns_400(self):
        """When URLProcessor returns success=False, endpoint returns 400 with error."""
        from core.views_rag_embeddings import ingest_url

        failed_result = ProcessingResult(
            success=False,
            error_message="Connection timed out fetching URL",
        )

        user = _get_user()
        request = _make_request(user, {"url": "https://example.com/broken"})

        with patch(
            "content.processors.DocumentProcessingPipeline"
        ) as MockPipeline:
            MockPipeline.return_value.process_url.return_value = failed_result
            response = ingest_url(request)

        assert response.status_code == 400, (
            f"Expected 400 but got {response.status_code}"
        )
        assert response.data["success"] is False
        assert "Connection timed out" in response.data["error"]

    def test_processing_failure_error_message_not_empty(self):
        """When error_message is empty, fallback text is returned."""
        from core.views_rag_embeddings import ingest_url

        failed_result = ProcessingResult(success=False, error_message="")

        user = _get_user()
        request = _make_request(user, {"url": "https://example.com/empty-error"})

        with patch(
            "content.processors.DocumentProcessingPipeline"
        ) as MockPipeline:
            MockPipeline.return_value.process_url.return_value = failed_result
            response = ingest_url(request)

        assert response.status_code == 400
        assert response.data["error"] == "Failed to process URL"

    def test_missing_url_returns_400(self):
        """Missing url field returns 400."""
        from core.views_rag_embeddings import ingest_url

        user = _get_user()
        request = _make_request(user, {})

        response = ingest_url(request)

        assert response.status_code == 400
        assert "required" in response.data["error"].lower()

    def test_processing_result_error_alias_works(self):
        """ProcessingResult.error property returns error_message."""
        result = ProcessingResult(
            success=False, error_message="Something broke"
        )
        assert result.error == "Something broke"
        assert result.error is result.error_message
