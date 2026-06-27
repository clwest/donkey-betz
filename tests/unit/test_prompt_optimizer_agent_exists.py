# pyright: reportMissingImports=false, reportGeneralTypeIssues=false
import os, uuid, pytest
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_core.settings")
pytestmark = pytest.mark.django_db

from django.contrib.auth import get_user_model
from core.models.agents_registry import UnifiedAgentTemplate, AgentTaskExecution

User = get_user_model()

def test_intelligent_prompt_agent_presence_and_execution_stub():
    user = User.objects.filter(username="chris").first() or \
           User.objects.first() or \
           User.objects.create_user(username="testuser", email="test@example.com")

    agent = UnifiedAgentTemplate.objects.filter(
        name="Intelligent Prompting Agent", is_active=True
    ).first()
    if not agent:
        pytest.skip("Intelligent Prompting Agent not found or inactive.")

    exec_obj = AgentTaskExecution.objects.create(
        template=agent,
        user=user,
        execution_id=f"test_prompt_opt_{uuid.uuid4().hex[:8]}",
        task_description="Optimize this prompt: 'Write a blog post about AI'",
        task_type="prompt_optimization",
        input_data={
            "original_prompt": "Write a blog post about AI",
            "target_model": "gpt-5-mini",
            "desired_outcome": "Comprehensive, engaging blog post with technical depth",
        },
        context={
            "user_intent": "Create high-quality content",
            "content_type": "blog_post",
            "topic": "artificial_intelligence",
        },
        status="pending",
    )

    # Just sanity-check some fields; no execution here.
    assert exec_obj.template_id == agent.id
    assert "original_prompt" in exec_obj.input_data
    assert isinstance(agent.llm_provider, str)
    assert isinstance(agent.llm_model, str)