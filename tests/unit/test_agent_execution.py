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

from agents.models import UnifiedAgentTemplate, AgentExecution  # noqa: E402


@pytest.fixture
def agent():
    """Provide an agent matching 'odds' (or None)."""
    return UnifiedAgentTemplate.objects.filter(name__icontains="odds").first()


def test_agent_fields_and_execution(agent):
    print("\n" + "=" * 60)
    print("AGENT FIELD NAME VERIFICATION")
    print("=" * 60)

    assert agent is not None, "❌ No agents found matching 'odds'"

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
        task_description="Test: Calculate odds for Alabama -16.5",
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