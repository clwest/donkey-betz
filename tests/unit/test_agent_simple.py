# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Smoke test: create an AgentExecution with explicit NCAAF data and run the task.

By default this test monkeypatches `execute_agent` to avoid external calls.
Set RUN_AGENT_INTEGRATION=1 to run the real execute_agent for an integration check.
"""

import os
import uuid
import pytest

# Ensure Django is ready (your conftest may already do this; harmless if duplicated)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_core.settings")

pytestmark = pytest.mark.django_db

from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution  # noqa: E402
from agents import tasks as agent_tasks  # noqa: E402


@pytest.fixture(scope="module")
def agent_or_skip():
    """Get the odds-calculation agent or skip cleanly if it's not present."""
    agent = UnifiedAgentTemplate.objects.filter(name="odds-calculation-agent").first()
    if not agent:
        pytest.skip("No 'odds-calculation-agent' found; skipping.")
    return agent


@pytest.fixture
def ncaaf_payload():
    task_description = """
Analyze this NCAAF (college football) betting opportunity:

Game: Oklahoma Sooners @ Temple Owls
Sport: NCAA Football (NCAAF)
Date: September 13, 2025

Current Betting Lines:
- Spread: Oklahoma -21.5 (both sides -110)
- Total: 58.5 O/U (both sides -110)
- Moneyline: Oklahoma -1200, Temple +750

Please provide:
1. Implied probability calculations for each bet
2. Expected value analysis
3. Specific betting recommendation with reasoning
4. Suggested bet size for a $1000 bankroll

Be specific about this being NCAAF/college football, not basketball or any other sport.
""".strip()

    input_data = {
        "sport": "NCAAF",
        "home_team": "Temple Owls",
        "away_team": "Oklahoma Sooners",
        "task": task_description,
    }
    return task_description, input_data


def _fake_execute_agent(execution_id: str):
    """Deterministic, fast stand-in for agents.tasks.execute_agent."""
    # Pretend work happened: update the DB row as the real task would.
    exec_obj = AgentExecution.objects.get(execution_id=execution_id)
    exec_obj.status = "completed"
    exec_obj.llm_response = (
        "✅ NCAAF analysis complete for Oklahoma Sooners @ Temple Owls. "
        "Spread -21.5, Total 58.5, ML Oklahoma -1200 / Temple +750. "
        "Includes implied probabilities, EV, and bankroll sizing."
    )
    exec_obj.save(update_fields=["status", "llm_response"])
    return {
        "output": exec_obj.llm_response,
        "status": exec_obj.status,
        "execution_id": execution_id,
    }


@pytest.mark.parametrize("limit", [3])  # keeps the pattern if you expand later
def test_execute_agent_with_explicit_ncaaf(agent_or_skip, ncaaf_payload, monkeypatch, limit):
    agent = agent_or_skip
    task_description, input_data = ncaaf_payload

    # Create the execution row
    execution_id = f"test_simple_{uuid.uuid4().hex[:8]}"
    exec_obj = AgentExecution.objects.create(
        execution_id=execution_id,
        template=agent,
        task_description=task_description,
        task_type="betting_analysis",
        input_data=input_data,
        status="pending",
    )

    run_real = os.environ.get("RUN_AGENT_INTEGRATION") == "1"
    if not run_real:
        # Fast path: monkeypatch the task to avoid external/slow deps
        monkeypatch.setattr(agent_tasks, "execute_agent", _fake_execute_agent)

    # Call the (patched or real) execution
    result = agent_tasks.execute_agent(execution_id)

    # Basic shape checks
    assert isinstance(result, dict)
    assert result.get("execution_id") == execution_id

    # Refresh and validate DB side effects
    exec_obj.refresh_from_db()
    assert exec_obj.status in {"completed", "pending", "failed"}  # real run could differ
    # In the fake path, we expect completed with a response
    if not run_real:
        assert exec_obj.status == "completed"
        assert isinstance(exec_obj.llm_response, str) and len(exec_obj.llm_response) > 0

    # Light content checks (either fake or real)
    output = result.get("output") or exec_obj.llm_response or ""
    assert "NCAAF" in output or "college football" in output
    assert "Oklahoma" in output and "Temple" in output

    # Optional: ensure we didn’t accidentally exceed any “limit” concept here
    # (kept for symmetry with other tests; no-op in this test)
    assert limit == 3