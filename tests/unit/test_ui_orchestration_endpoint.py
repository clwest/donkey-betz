# pyright: reportMissingImports=false, reportGeneralTypeIssues=false
import os, json, pytest, types
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_core.settings")
pytestmark = pytest.mark.django_db

from sports.models import Game
import requests


class _FakeResp:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text or json.dumps(self._payload)
    def json(self):
        return self._payload


def test_ui_orchestration_endpoint_smoke(monkeypatch):
    game = Game.objects.filter(
        home_team__name__icontains="Alabama",
        away_team__name__icontains="Wisconsin"
    ).first()
    if not game:
        pytest.skip("Required game (Wisconsin @ Alabama) not found.")

    url = "http://localhost:8000/api/odds/orchestrate/"
    payload = {
        "game_id": str(game.id),
        "home_team": game.home_team.name,
        "away_team": game.away_team.name,
        "league": "NCAAF",
        "subscription_tier": "premium",
        "selected_agents": ["odds-calculation-agent", "kelly-bet-sizing-agent"],
    }

    def _fake_post(u, json=None, *a, **kw):
        assert u == url
        assert json and json.get("game_id") == payload["game_id"]
        return _FakeResp(
            200,
            {
                "success": True,
                "task_id": "fake-task-123",
                "status": "queued",
                "websocket_channel": "ws://fake/channel",
            },
        )

    monkeypatch.setattr(requests, "post", _fake_post)
    resp = requests.post(url, json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("success") is True
    assert data.get("task_id") == "fake-task-123"