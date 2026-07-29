"""S3039 S7: ThinkingAgent async-boundary regression tests.

Prior state (S2951 fix): ``_execute_sync`` scoped
``DJANGO_ALLOW_ASYNC_UNSAFE='true'`` around ``asyncio.run(self.think(...))``
to permit sync ORM inside ``think() → _format_context_for_thinking →
_build_intelligent_prompt`` (which calls ``UserPreferences.objects``,
semantic-search helpers, policy-context ORM, etc.).

That toggle raced across concurrent runs on ``--pool=threads
--concurrency=2``: thread A's finally-block could pop the process-global
env var while thread B was still mid-sync-ORM inside its own
``asyncio.run``, tripping Django's ``SynchronousOnlyOperation``. Six such
failures surfaced on 2026-07-25 (S3037 audit finding S7).

S3039 fix: route ``_format_context_for_thinking`` through
``sync_to_async(thread_sensitive=True)`` so the ORM runs on a
dedicated worker thread with no active loop, and drop both env-var
toggles.

These tests lock in the new invariants:

- ``execute()`` never mutates ``DJANGO_ALLOW_ASYNC_UNSAFE`` (Rigby SIGN
  ask #3).
- Two concurrent ``execute()`` calls with a widened race window never
  raise ``SynchronousOnlyOperation`` (Rigby SIGN ask #2).
- ``think()`` awaits its sync-ORM prompt-formatter (spot-check that we
  didn't regress the routing).
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
import os
import time
from unittest.mock import AsyncMock, patch

from django.test import SimpleTestCase

from core.agents.thinking_agent import ThinkingAgent


_FAKE_LLM_JSON = '{"reflection": "ok", "insights": [], "decisions": []}'


class ThinkingAgentAsyncBoundaryTest(SimpleTestCase):
    """Locks in the S3039 S7 invariants — no env-var mutation, no
    SynchronousOnlyOperation under concurrent execution."""

    def _make_agent(self):
        agent = ThinkingAgent.__new__(ThinkingAgent)
        agent.name = "ThinkingAgent"
        agent.user = None
        agent._tt_enabled = False
        agent._tt_session = None
        agent._tt_decision_count = 0
        agent._tt_start_time = 0.0
        agent.thinking_prompt = "<test-thinking-prompt>"
        return agent

    def test_execute_does_not_mutate_django_allow_async_unsafe(self):
        """Rigby SIGN ask #3: assert env-var invariant before/after execute."""
        agent = self._make_agent()

        prior = os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE")
        self.addCleanup(
            lambda: (
                os.environ.__setitem__("DJANGO_ALLOW_ASYNC_UNSAFE", prior)
                if prior is not None
                else os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE", None)
            )
        )

        with patch.object(agent, "gather_context", return_value={"lookback_hours": 24}), \
                patch.object(
                    agent, "_format_context_for_thinking", return_value="prompt"
                ), \
                patch.object(
                    agent, "_call_llm",
                    new=AsyncMock(return_value=_FAKE_LLM_JSON),
                ), \
                patch.object(agent, "_save_to_deliverable", return_value=None):
            agent.execute(task="env-var-invariant probe")

        after = os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE")
        self.assertEqual(
            prior,
            after,
            (
                "execute() must not mutate DJANGO_ALLOW_ASYNC_UNSAFE — "
                "S3039 S7 removed the process-global toggle in favor of "
                "sync_to_async at the ORM call site."
            ),
        )

    def test_concurrent_executes_with_widened_race_window_do_not_raise(self):
        """Rigby SIGN ask #2: two concurrent execute() calls with a
        monkeypatched sleep inside ``_format_context_for_thinking`` (the
        old sync-ORM window) must not raise SynchronousOnlyOperation.

        Pre-fix, the process-global env var would have been popped by
        whichever coroutine finished first, tripping the other's sync
        ORM in ``_build_intelligent_prompt``. Post-fix, ORM is confined
        to a sync_to_async worker with no loop, so overlap is safe.
        """
        agent_a = self._make_agent()
        agent_b = self._make_agent()

        # Widen the race window: sleep inside the ORM-heavy path so both
        # threads are guaranteed to overlap on the (formerly) shared env var.
        def _slow_format(context):
            time.sleep(0.25)
            return "prompt"

        errors = []

        def _run(agent):
            try:
                with patch.object(agent, "gather_context", return_value={"lookback_hours": 24}), \
                        patch.object(
                            agent, "_format_context_for_thinking",
                            side_effect=_slow_format,
                        ), \
                        patch.object(
                            agent, "_call_llm",
                            new=AsyncMock(return_value=_FAKE_LLM_JSON),
                        ), \
                        patch.object(agent, "_save_to_deliverable", return_value=None):
                    return agent.execute(task="concurrent race probe")
            except Exception as e:  # noqa: BLE001 — we want to see anything
                errors.append(f"{type(e).__name__}: {e}")
                return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(_run, agent_a), pool.submit(_run, agent_b)]
            results = [f.result(timeout=30) for f in futures]

        self.assertFalse(
            errors,
            f"Concurrent execute() raised — pre-S7 env-var race would surface here: {errors}",
        )
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertTrue(r.success, f"Expected success, got: {r}")

    def test_think_awaits_sync_to_async_format_call(self):
        """Spot-check that ``think`` routes _format_context_for_thinking through
        sync_to_async instead of calling it synchronously — if a future edit
        reverts to a plain sync call this test fails first."""
        agent = self._make_agent()

        call_ctx = {}

        def _record_call(context):
            # If this ran on the event-loop thread we'd see a loop; via
            # sync_to_async we shouldn't.
            try:
                asyncio.get_running_loop()
                call_ctx["loop_active"] = True
            except RuntimeError:
                call_ctx["loop_active"] = False
            return "prompt"

        with patch.object(
            agent, "_format_context_for_thinking", side_effect=_record_call
        ), patch.object(
            agent, "_call_llm",
            new=AsyncMock(return_value=_FAKE_LLM_JSON),
        ):
            asyncio.run(agent.think({}))

        self.assertIs(
            call_ctx.get("loop_active"),
            False,
            (
                "_format_context_for_thinking must run in a thread without an "
                "active event loop (sync_to_async worker); it appears to be "
                "running on the loop thread, which would re-open the S2951 "
                "SynchronousOnlyOperation surface."
            ),
        )

    def test_think_is_still_a_coroutine(self):
        """Guardrail: think() must remain an async def — the fix keeps the
        async signature and only changes what happens inside."""
        self.assertTrue(
            inspect.iscoroutinefunction(ThinkingAgent.think),
            "ThinkingAgent.think must be async def",
        )


