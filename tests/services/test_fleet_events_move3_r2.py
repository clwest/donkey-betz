"""Pure-function tests for Move 3 R2 fleet event additions.

DB-dependent surfaces (replay endpoint ordering, TTL deletion) are
exercised by live smoke against the running stack rather than the
Django test DB — the test DB lacks pgvector on this machine. See the
SESSION_1130 handoff for the smoke recipe.

What's covered here:
- `_parse_replay_query` — since/limit parsing, clamping, error messages
- `_parse_last_event_id_seq` — header parsing, negative/non-int rejection
- `_format_sse_event` — SSE `id:` field comes from `seq`, not UUID
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.views_fleet_events import (
    REPLAY_DEFAULT_LIMIT,
    REPLAY_MAX_LIMIT,
    _format_sse_event,
    _parse_last_event_id_seq,
    _parse_replay_query,
)


def _request_with_get(get_params: dict, meta: dict | None = None):
    req = MagicMock()
    req.GET = get_params
    req.META = meta or {}
    return req


# ─── _parse_replay_query ──────────────────────────────────────────────


class TestParseReplayQuery:
    def test_defaults_when_no_params(self):
        since, limit, err = _parse_replay_query(_request_with_get({}))
        assert since == 0
        assert limit == REPLAY_DEFAULT_LIMIT
        assert err is None

    def test_explicit_since_and_limit(self):
        since, limit, err = _parse_replay_query(
            _request_with_get({"since": "42", "limit": "200"})
        )
        assert since == 42
        assert limit == 200
        assert err is None

    def test_limit_clamps_to_max(self):
        since, limit, err = _parse_replay_query(
            _request_with_get({"since": "0", "limit": "999999"})
        )
        assert limit == REPLAY_MAX_LIMIT
        assert err is None

    def test_limit_floor_is_one(self):
        since, limit, err = _parse_replay_query(
            _request_with_get({"limit": "0"})
        )
        assert limit == 1
        assert err is None

    def test_limit_negative_clamps_to_one(self):
        since, limit, err = _parse_replay_query(
            _request_with_get({"limit": "-5"})
        )
        assert limit == 1
        assert err is None

    def test_invalid_since_returns_error(self):
        since, limit, err = _parse_replay_query(
            _request_with_get({"since": "not-a-number"})
        )
        assert err is not None
        assert "since" in err.lower()

    def test_negative_since_rejected(self):
        since, limit, err = _parse_replay_query(
            _request_with_get({"since": "-1"})
        )
        assert err is not None
        assert "since" in err.lower()

    def test_invalid_limit_returns_error(self):
        since, limit, err = _parse_replay_query(
            _request_with_get({"since": "10", "limit": "abc"})
        )
        assert err is not None
        assert "limit" in err.lower()


# ─── _parse_last_event_id_seq ─────────────────────────────────────────


class TestParseLastEventIdSeq:
    def test_missing_header_returns_none(self):
        result = _parse_last_event_id_seq(_request_with_get({}, meta={}))
        assert result is None

    def test_integer_header_parses(self):
        result = _parse_last_event_id_seq(
            _request_with_get({}, meta={"HTTP_LAST_EVENT_ID": "42"})
        )
        assert result == 42

    def test_zero_is_valid(self):
        result = _parse_last_event_id_seq(
            _request_with_get({}, meta={"HTTP_LAST_EVENT_ID": "0"})
        )
        assert result == 0

    def test_negative_rejected(self):
        result = _parse_last_event_id_seq(
            _request_with_get({}, meta={"HTTP_LAST_EVENT_ID": "-1"})
        )
        assert result is None

    def test_non_int_rejected(self):
        result = _parse_last_event_id_seq(
            _request_with_get({}, meta={"HTTP_LAST_EVENT_ID": "abc"})
        )
        assert result is None

    def test_empty_string_returns_none(self):
        result = _parse_last_event_id_seq(
            _request_with_get({}, meta={"HTTP_LAST_EVENT_ID": ""})
        )
        assert result is None


# ─── _format_sse_event ────────────────────────────────────────────────


class TestFormatSseEvent:
    def test_id_field_is_seq_when_present(self):
        envelope = {
            "event_id": "550e8400-e29b-41d4-a716-446655440000",
            "seq": 42,
            "type": "artifact.created",
            "created_at": "2026-05-22T01:00:00Z",
            "app_slug": "contract-concierge",
            "payload": {},
        }
        out = _format_sse_event(envelope).decode("utf-8")
        # SSE id: must be the seq, not the UUID.
        assert "id: 42\n" in out
        assert "event: artifact.created\n" in out
        # UUID still rides in the data: body for callers who want it.
        assert "550e8400" in out

    def test_falls_back_to_uuid_when_no_seq(self):
        envelope = {
            "event_id": "uuid-here",
            "type": "stream.opened",
            "created_at": "",
            "app_slug": "mentorforge",
            "payload": {},
        }
        out = _format_sse_event(envelope).decode("utf-8")
        # No seq → SSE id: is the UUID-ish event_id (back-compat path).
        assert "id: uuid-here\n" in out

    def test_seq_none_falls_back_to_event_id(self):
        # Hello / sentinel envelopes pass seq=None explicitly.
        envelope = {
            "event_id": "hello",
            "seq": None,
            "type": "stream.opened",
            "created_at": "",
            "app_slug": "contract-concierge",
            "payload": {},
        }
        out = _format_sse_event(envelope).decode("utf-8")
        assert "id: hello\n" in out
        # `None` MUST NOT appear in the SSE id field.
        assert "id: None\n" not in out

    def test_terminates_with_blank_line(self):
        envelope = {"seq": 1, "type": "x", "event_id": "abc", "app_slug": "x"}
        out = _format_sse_event(envelope).decode("utf-8")
        # Per SSE spec, events end with a blank line.
        assert out.endswith("\n\n")
