"""Smoke tests for the Session 1221 P1 OpenAI total-request bound.

The helper ``_run_openai_create_with_total_cap`` in ``core/agents/base_agent.py``
wraps the sync OpenAI SDK call in a threadpool future and raises ``TimeoutError``
when the cap is exceeded. Closes the ``httpx.Timeout(read=90s)`` per-chunk
loophole documented in deliverable ``7ae61cf7-…``.

These tests exercise the helper in isolation (no real OpenAI client, no
``BaseAgent`` subclass) so they run fast and have no network dependencies.
"""

import time

import pytest

from core.agents.base_agent import _run_openai_create_with_total_cap


def test_returns_value_when_call_finishes_under_cap():
    """The wrap is transparent on the success path — it returns whatever
    the underlying ``create_fn`` returned."""
    sentinel = {'choices': [{'message': {'content': 'hello'}}]}

    def fake_create(**kwargs):
        return sentinel

    result = _run_openai_create_with_total_cap(
        fake_create,
        {'model': 'gpt-5-mini', 'messages': []},
        total_request_cap_s=5.0,
        agent_name='TestAgent',
    )

    assert result is sentinel


def test_passes_kwargs_through_to_create_fn():
    """Kwargs are forwarded verbatim — important because the upstream
    caller passes ``model``, ``messages``, ``max_completion_tokens``,
    ``tools``, ``tool_choice``."""
    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return 'ok'

    _run_openai_create_with_total_cap(
        fake_create,
        {
            'model': 'gpt-5.2',
            'messages': [{'role': 'user', 'content': 'hi'}],
            'max_completion_tokens': 4000,
            'tools': [{'type': 'function'}],
            'tool_choice': 'auto',
        },
        total_request_cap_s=2.0,
        agent_name='TestAgent',
    )

    assert captured['model'] == 'gpt-5.2'
    assert captured['messages'] == [{'role': 'user', 'content': 'hi'}]
    assert captured['max_completion_tokens'] == 4000
    assert captured['tools'] == [{'type': 'function'}]
    assert captured['tool_choice'] == 'auto'


def test_raises_timeout_when_call_exceeds_cap():
    """The dominant failure mode: slow-streaming gpt-5.x reasoning that
    never trips ``read=90s`` but exceeds the wall-clock budget. The wrap
    must raise ``TimeoutError`` exactly when the cap elapses."""

    def slow_create(**kwargs):
        time.sleep(5)  # well past the cap below
        return 'never returned'

    with pytest.raises(TimeoutError) as excinfo:
        _run_openai_create_with_total_cap(
            slow_create,
            {'model': 'gpt-5-mini', 'messages': []},
            total_request_cap_s=0.5,
            agent_name='AudioAgent',
        )

    assert 'AudioAgent' in str(excinfo.value)
    assert '0.5' in str(excinfo.value)


def test_timeout_message_names_the_cap_value():
    """The error message must surface the actual cap so operators reading
    logs can correlate with the per-agent ``llm_timeout * 2.5`` formula."""
    def slow_create(**kwargs):
        time.sleep(2)

    with pytest.raises(TimeoutError) as excinfo:
        _run_openai_create_with_total_cap(
            slow_create,
            {},
            total_request_cap_s=0.2,
            agent_name='CTOAgent',
        )

    msg = str(excinfo.value)
    assert 'OpenAI total-request timeout' in msg
    assert 'CTOAgent' in msg
    assert '0.2' in msg


def test_propagates_underlying_create_fn_exception():
    """If the SDK call raises a non-timeout exception (e.g., auth error,
    API error), the wrap surfaces it unchanged — no swallowing."""

    class FakeAPIError(RuntimeError):
        pass

    def failing_create(**kwargs):
        raise FakeAPIError('rate limit')

    with pytest.raises(FakeAPIError) as excinfo:
        _run_openai_create_with_total_cap(
            failing_create,
            {},
            total_request_cap_s=5.0,
            agent_name='TestAgent',
        )

    assert 'rate limit' in str(excinfo.value)


def test_unknown_agent_name_defaults_to_unknown_string():
    """Defensive: an empty ``agent_name`` doesn't produce a confusing
    "in '" or stray-quote message."""

    def slow_create(**kwargs):
        time.sleep(2)

    with pytest.raises(TimeoutError) as excinfo:
        _run_openai_create_with_total_cap(
            slow_create,
            {},
            total_request_cap_s=0.1,
            agent_name='',
        )

    assert 'unknown' in str(excinfo.value)
