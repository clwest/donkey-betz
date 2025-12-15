# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Test agent execution with correct field names
"""
import os
import uuid
import django
import pytest

# Use Django in tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_core.settings")
django.setup()

pytestmark = pytest.mark.django_db

from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution  # noqa: E402


@pytest.fixture
def agent():
    """Provide any available agent for testing."""
    # Session 452: Use any agent, not specifically 'odds' (sports betting removed)
    # If no agents exist in test DB, create a minimal test agent
    agent = UnifiedAgentTemplate.objects.first()
    if agent is None:
        agent = UnifiedAgentTemplate.objects.create(
            name="TestAgent",
            agent_type="content_generation",
            description="Test agent for unit testing",
            system_prompt="You are a test agent.",
            llm_provider="openai",
            llm_model="gpt-4o-mini",
            is_active=True,
        )
    return agent


def test_agent_fields_and_execution(agent):
    print("\n" + "=" * 60)
    print("AGENT FIELD NAME VERIFICATION")
    print("=" * 60)

    assert agent is not None, "❌ No agents found in database"

    print(f"\n✅ Agent: {agent.name}")
    print(f"   Provider field: llm_provider = '{agent.llm_provider}'")
    print(f"   Model field: llm_model = '{agent.llm_model}'")

    print("\n📋 All agent fields:")
    for field in agent._meta.fields:
        if any(x in field.name for x in ("provider", "model", "llm")):
            value = getattr(agent, field.name, None)
            print(f"   {field.name}: {value}")

    print("\n🧪 Testing execution creation...")
    execution = AgentExecution.objects.create(
        execution_id=f"test_{uuid.uuid4().hex[:8]}",
        template=agent,
        task_description="Test: Verify agent execution with correct field names",
        task_type="test",
        status="pending",
    )
    try:
        assert execution.pk is not None
        print(f"✅ Created execution: {execution.execution_id}")
    finally:
        execution.delete()
        print("🧹 Cleaned up test execution")

    print("\n✨ SUCCESS: Agent model is using correct field names!")
    print("   - Use 'llm_provider' not 'provider'")
    print("   - Use 'llm_model' not 'model'")
    print("\n" + "=" * 60 + "\n")