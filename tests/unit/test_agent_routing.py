# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
import os
import django
import pytest

# Django setup for tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_core.settings")
django.setup()

pytestmark = pytest.mark.django_db

from core.models.agents_registry import AgentRegistry  # noqa: E402


@pytest.fixture(scope="module")
def registry():
    """
    Try to load the unified registry. If it doesn't exist in this environment,
    skip the test suite rather than failing during collection.
    """
    try:
        return AgentRegistry.objects.get(registry_name="unified_agent_registry")
    except AgentRegistry.DoesNotExist:
        pytest.skip("No AgentRegistry('unified_agent_registry') present; skipping prompt discovery tests.")


@pytest.mark.parametrize(
    "task",
    [
        "optimize this prompt for better AI responses",
        "improve prompt engineering for my AI system",
        "help me write better prompts for content generation",
        "analyze and improve my prompt performance",
    ],
)
def test_prompt_task_agent_discovery(registry, task, capsys):
    """
    Ensure the registry call returns a list (possibly empty) of agent results,
    each with expected keys when present, and respects the limit.
    """
    print(f"\nTask: {task}")
    agents = registry.find_agents_for_task(task, limit=3)

    # Basic shape assertions
    assert isinstance(agents, list), "Expected a list of agent results"
    assert len(agents) <= 3, "Result list should respect the 'limit=3' parameter"

    # If anything is returned, validate the structure
    for result in agents:
        assert isinstance(result, dict), "Each agent result should be a dict"
        assert "agent_name" in result, "Result missing 'agent_name'"
        assert "score" in result, "Result missing 'score'"
        assert isinstance(result["agent_name"], str)
        # score should be numeric
        assert isinstance(result["score"], (int, float))

    # Nice to have: show what we found in the output
    if agents:
        print("Top agents:")
        for r in agents:
            print(f"  - {r['agent_name']} (score: {r['score']:.2f})")
    else:
        print("  (no matching agents)")

    # Keep pytest output tidy unless -s is passed
    capsys.readouterr()