"""Tests for the signal_studio_judge_stats PA tool (Session 1140).

Exercises the handler in `core.services.td_handlers_core.CoreHandlersMixin.
_handle_signal_studio_judge_stats` against a mocked signal-studio
endpoint. Live HTTP isn't covered here — that's verified at session
close by Rigby calling the tool via PA chat.

Covers:
- Default `days=7` when payload omits the field.
- Bounds clamping (1..90, falls back to 7 on garbage).
- Happy path: 200 with valid JSON → `{ok: True, **body}`.
- HTTP error (500) → `{ok: False, error: ...}` envelope, not raise.
- httpx network error → `{ok: False, error: signal-studio unreachable}`.
- Non-JSON 200 → `{ok: False, error: not JSON}`.
- URL respects SIGNAL_STUDIO_API_URL env override.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

# Pull the handler off the mixin without instantiating the full
# ToolDispatcher (which requires Django app config). We bind it to a
# trivial object so `self` has somewhere to live.
from core.services.td_handlers_core import CoreHandlersMixin


class _Host:
    """Minimal host for the mixin method — no behavior needed."""
    pass


def _bind_handler():
    host = _Host()
    return CoreHandlersMixin._handle_signal_studio_judge_stats.__get__(host)


# ─── Helpers ──────────────────────────────────────────────────────────


def _mock_response(status_code: int, body, *, raises: Exception | None = None):
    """Build a MagicMock that mimics httpx.Response for the handler."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.text = body if isinstance(body, str) else str(body)
    if raises is not None:
        resp.json.side_effect = raises
    else:
        resp.json.return_value = body
    return resp


def _patch_httpx_client(resp=None, raise_on_get: Exception | None = None):
    """Patch httpx.Client to return a configured response or raise."""
    client_cm = MagicMock()
    if raise_on_get is not None:
        client_cm.__enter__.return_value.get.side_effect = raise_on_get
    else:
        client_cm.__enter__.return_value.get.return_value = resp
    client_cm.__exit__.return_value = False
    return patch("httpx.Client", return_value=client_cm)


# ─── Tests ────────────────────────────────────────────────────────────


class TestSignalStudioJudgeStatsTool:
    def test_default_days_when_payload_empty(self):
        body = {"days": 7, "total": 5, "rejection_rate": 0.4}
        handler = _bind_handler()
        with _patch_httpx_client(_mock_response(200, body)) as p:
            result = handler("signal_studio_judge_stats", {}, "user-1", "trace-1")
        assert result["ok"] is True
        assert result["days"] == 7
        assert result["total"] == 5
        # URL inspected via the call's first positional arg
        call_url = p.return_value.__enter__.return_value.get.call_args[0][0]
        assert "days=7" in call_url

    def test_days_clamped_to_max_90(self):
        body = {"days": 90, "total": 0, "rejection_rate": 0.0}
        handler = _bind_handler()
        with _patch_httpx_client(_mock_response(200, body)) as p:
            handler("signal_studio_judge_stats", {"days": 1000}, "u", "t")
        url = p.return_value.__enter__.return_value.get.call_args[0][0]
        assert "days=90" in url

    def test_days_clamped_to_min_1(self):
        body = {"days": 1, "total": 0, "rejection_rate": 0.0}
        handler = _bind_handler()
        with _patch_httpx_client(_mock_response(200, body)) as p:
            handler("signal_studio_judge_stats", {"days": 0}, "u", "t")
        url = p.return_value.__enter__.return_value.get.call_args[0][0]
        assert "days=1" in url

    def test_garbage_days_falls_back_to_default_7(self):
        body = {"days": 7, "total": 0}
        handler = _bind_handler()
        with _patch_httpx_client(_mock_response(200, body)) as p:
            handler("signal_studio_judge_stats", {"days": "not-a-number"}, "u", "t")
        url = p.return_value.__enter__.return_value.get.call_args[0][0]
        assert "days=7" in url

    def test_happy_path_returns_endpoint_json_with_ok_envelope(self):
        body = {
            "days": 7, "total": 100, "rejected": 15, "summarized": 80, "raw": 5,
            "rejection_rate": 0.1579,
            "by_cluster_method": {
                "entity_token_v1": {"total": 60, "rejected": 5, "summarized": 55, "rejection_rate": 0.0833},
                "legacy": {"total": 40, "rejected": 10, "summarized": 25, "rejection_rate": 0.2857},
            },
            "by_pattern_type": {"demand_spike": {"total": 50, "rejected": 8}},
        }
        handler = _bind_handler()
        with _patch_httpx_client(_mock_response(200, body)):
            result = handler("signal_studio_judge_stats", None, "u", "t")
        assert result["ok"] is True
        assert result["rejection_rate"] == 0.1579
        assert result["by_cluster_method"]["entity_token_v1"]["rejection_rate"] == 0.0833

    def test_http_500_returns_error_envelope_not_raise(self):
        handler = _bind_handler()
        with _patch_httpx_client(_mock_response(500, "internal error")):
            result = handler("signal_studio_judge_stats", {}, "u", "t")
        assert result["ok"] is False
        assert "HTTP 500" in result["error"]
        # Per Rigby's review on PR #2169: surface status_code on HTTP
        # failures so debugging doesn't require log diving.
        assert result["status_code"] == 500
        assert result["days"] == 7

    def test_network_error_returns_error_envelope(self):
        handler = _bind_handler()
        with _patch_httpx_client(raise_on_get=httpx.ConnectError("conn refused")):
            result = handler("signal_studio_judge_stats", {}, "u", "t")
        assert result["ok"] is False
        assert "unreachable" in result["error"]
        assert "conn refused" in result["error"]
        # No status_code on transport-layer failure — there was no
        # response. The error string carries the diagnostic.
        assert "status_code" not in result

    def test_non_json_200_returns_error_envelope(self):
        handler = _bind_handler()
        resp = _mock_response(200, "<html>not json</html>", raises=ValueError("Expecting value"))
        with _patch_httpx_client(resp):
            result = handler("signal_studio_judge_stats", {}, "u", "t")
        assert result["ok"] is False
        assert "not JSON" in result["error"]
        # 200 + unparseable body: surface status_code so a caller can
        # distinguish "endpoint live but returning HTML" from "endpoint
        # down". Per Rigby's PR #2169 review.
        assert result["status_code"] == 200

    def test_env_override_changes_base_url(self, monkeypatch):
        monkeypatch.setenv("SIGNAL_STUDIO_API_URL", "http://signal_studio_api:8007")
        body = {"days": 7, "total": 0}
        handler = _bind_handler()
        with _patch_httpx_client(_mock_response(200, body)) as p:
            handler("signal_studio_judge_stats", {}, "u", "t")
        url = p.return_value.__enter__.return_value.get.call_args[0][0]
        assert url.startswith("http://signal_studio_api:8007/api/judge-stats")

    def test_default_url_when_env_unset(self, monkeypatch):
        monkeypatch.delenv("SIGNAL_STUDIO_API_URL", raising=False)
        body = {"days": 7, "total": 0}
        handler = _bind_handler()
        with _patch_httpx_client(_mock_response(200, body)) as p:
            handler("signal_studio_judge_stats", {}, "u", "t")
        url = p.return_value.__enter__.return_value.get.call_args[0][0]
        assert url.startswith("http://localhost:8007/api/judge-stats")

    def test_trailing_slash_on_env_stripped(self, monkeypatch):
        monkeypatch.setenv("SIGNAL_STUDIO_API_URL", "http://signal_studio_api:8007/")
        body = {"days": 7, "total": 0}
        handler = _bind_handler()
        with _patch_httpx_client(_mock_response(200, body)) as p:
            handler("signal_studio_judge_stats", {}, "u", "t")
        url = p.return_value.__enter__.return_value.get.call_args[0][0]
        # No double-slash before /api/
        assert "//api/" not in url.replace("http://", "")
