# pyright: reportMissingImports=false, reportGeneralTypeIssues=false
import os, pytest
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_core.settings")
pytestmark = pytest.mark.django_db

from django.contrib.auth import get_user_model
from core.agent_integration import AgentRouter, IntelligentPromptOptimizer

User = get_user_model()

def _get_user():
    return User.objects.filter(username="chris").first() or User.objects.first() or \
           User.objects.create_user(username="testuser", email="test@example.com")

def test_routing_and_prompt_flags_smoke():
    user = _get_user()
    router = AgentRouter(user)
    optimizer = IntelligentPromptOptimizer(user)  # noqa: F841

    cases = [
        ("Prompt Optimization Test",
         "How can I improve this prompt: 'Write a blog post'",
         True),
        ("Business Strategy Test",
         "Help me create a business plan for my tech startup",
         False),
        ("Sports Analytics Test",
         "Analyze the betting odds for tonight's game",
         False),
        ("General Assistant Test",
         "What's the weather like today?",
         False),
        ("Complex Prompt Engineering Test",
         "Optimize my AI prompt for content generation with better context and specificity",
         True),
    ]

    for name, msg, expected_prompting in cases:
        use_prompting = router.should_use_intelligent_prompting(msg)
        use_routing = router.should_use_agent_routing(msg)
        assert isinstance(use_prompting, bool) and isinstance(use_routing, bool), name
        # We only assert prompting flag matches expectation (routing may vary by data)
        assert use_prompting == expected_prompting, name

        if use_routing:
            best = router.find_best_agent(msg)
            # best may be None in empty DBs; that’s fine for smoke.
            if best:
                assert "agent_name" in best and "score" in best