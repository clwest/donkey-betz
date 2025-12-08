# pyright: reportMissingImports=false, reportGeneralTypeIssues=false
import os, uuid, pytest
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_core.settings")
pytestmark = pytest.mark.django_db

from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution
from sports.models import Game
from agents import tasks as agent_tasks


def _fake_execute_agent(execution_id: str):
    exec_obj = AgentExecution.objects.get(execution_id=execution_id)
    exec_obj.status = "completed"
    exec_obj.llm_response = (
        "Kelly bet sizing computed for NCAAF: Oklahoma @ Temple, spread -21.5."
    )
    exec_obj.result = {"kelly_fraction": 0.25, "bankroll": 1000, "stake": 62.5}
    exec_obj.save(update_fields=["status", "llm_response", "result"])
    return {"output": exec_obj.llm_response, "status": exec_obj.status, "execution_id": execution_id}


def test_kelly_bet_sizing_for_ncaaf(monkeypatch):
    game = Game.objects.filter(home_team__name__icontains="Temple",
                               away_team__name__icontains="Oklahoma").first()
    if not game:
        pytest.skip("Required game (Temple vs Oklahoma) not found.")

    agent = UnifiedAgentTemplate.objects.filter(name="kelly-bet-sizing-agent").first()
    if not agent:
        pytest.skip("Agent 'kelly-bet-sizing-agent' not found.")

    input_data = {
        "sport": "NCAAF",
        "game_id": str(game.id),
        "home_team": game.home_team.name,
        "away_team": game.away_team.name,
        "league": "NCAA Football",
        "game_time": str(game.scheduled_start),
        "venue": "Lincoln Financial Field",
        "markets": {
            "spread": {"line": -21.5, "home_odds": -110, "away_odds": -110},
            "total": {"line": 58.5, "over_odds": -110, "under_odds": -110},
            "moneyline": {"home_odds": 750, "away_odds": -1200},
        },
        "analysis_request": "Calculate optimal bet size using Kelly Criterion for Oklahoma -21.5 spread",
        "bankroll": 1000,
        "win_probability": 0.65,
        "kelly_fraction": 0.25,
    }

    execution_id = f"test_{agent.name}_{uuid.uuid4().hex[:8]}"
    exec_obj = AgentExecution.objects.create(
        execution_id=execution_id,
        template=agent,
        task_description=f"Analyze NCAAF: {game.away_team.name} @ {game.home_team.name} (Kelly sizing)",
        task_type="betting_analysis",
        input_data=input_data,
        context={"sport": "NCAAF", "test_execution": True},
        status="pending",
    )

    monkeypatch.setattr(agent_tasks, "execute_agent", _fake_execute_agent)
    result = agent_tasks.execute_agent(execution_id)

    exec_obj.refresh_from_db()
    assert result["status"] == "completed"
    assert exec_obj.status == "completed"
    assert "Kelly" in (exec_obj.llm_response or "")
    assert exec_obj.result and "stake" in exec_obj.result