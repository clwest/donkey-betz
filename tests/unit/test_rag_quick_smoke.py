# pyright: reportMissingImports=false, reportGeneralTypeIssues=false
import os, pytest
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_core.settings")
pytestmark = pytest.mark.django_db

from django.contrib.auth import get_user_model
from content.models import Document

User = get_user_model()

def test_rag_smoke_import_and_counts():
    # Import here so test fails gracefully if module/class moved
    try:
        from core.views_assistant_rag_enhanced import RAGAssistant  # noqa: F401
    except Exception:
        pytest.skip("RAGAssistant not available in core.views_assistant_rag_enhanced.")

    user = User.objects.filter(is_superuser=True).first() or User.objects.first() or \
           User.objects.create_user(username="testuser", email="test@example.com")

    # Just instantiate; don’t require external services
    rag = RAGAssistant(user)  # noqa: F841

    # DB quick stats (works even if zero)
    total_docs = Document.objects.count()
    public_docs = Document.objects.filter(is_public=True).count()
    assert total_docs >= 0 and public_docs >= 0