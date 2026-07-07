"""Arc I-0100 P4 Stop Condition #3 — regression coverage for the
PA↔LLMCallEvent correlation contract per ADR-0002 §3.3.

Verifies the four §3.3 join queries work end-to-end for PA turns
when ``PA_AGENT_EXECUTION_WRITE_ENABLED=True``, plus preserves
pre-Stop-3 behavior when the flag is OFF.

Scope of coverage:

1. **PA turn → LLM calls (§3.3 query #1)**: given a PA
   ``AgentExecution.id``, filtering ``LLMCallEvent`` by
   ``execution_id`` returns the PA-loop calls.
2. **LLM call → PA turn (§3.3 query #2)**: given an
   ``LLMCallEvent.execution_id``, the reverse
   ``AgentExecution.objects.filter(id=...)`` resolves to a
   ``PersonalAssistant`` agent row.
3. **Retries share execution_id (§3.3 query #3)**: multiple
   ``LLMCallEvent`` rows with distinct ``call_id`` share one
   ``execution_id`` when the agentic loop retries within a turn.
4. **Existing non-PA behavior unchanged**: a `code_review_agent`-
   style call using ``llm_call_span`` directly still produces its
   own LLMCallEvent row with the non-PA agent_name.
5. **Flag-OFF rollback**: with
   ``PA_AGENT_EXECUTION_WRITE_ENABLED=False``, calling
   ``_pa_wrapped_enforce_real_ai`` bypasses the wrapper — zero
   LLMCallEvent rows are created and no execution_id is emitted.

Approach: test ``_pa_wrapped_enforce_real_ai`` directly by
patching ``self.llm_enforcer.enforce_real_ai`` with a fake that
returns a synthetic enforcer-shape dict. Avoids the full
``process_message`` LLM plumbing while exercising the exact
``llm_call_span`` wrapping logic.

Run::

    python manage.py test core.tests.test_pa_llm_call_span_wiring -v2 --keepdb
"""
from __future__ import annotations

import asyncio
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from core.models_llm_telemetry import LLMCallEvent
from core.models_unified_system import Agent, AgentExecution
from core.services.unified_pa_entrypoint import UnifiedPAEntrypoint


User = get_user_model()


def _fake_enforcer_response(
    *, content: str = "hello", input_tokens: int = 42, output_tokens: int = 7,
):
    """Return a synthetic dict matching the shape of
    ``llm_enforcer.enforce_real_ai`` — flat token counts, no
    nested usage. The wrapper builds a synthetic ``usage`` shape
    from these keys for LLMCallEvent token capture."""
    return {
        "success": True,
        "content": content,
        "response": content,
        "response_id": "resp-fake-123",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "reasoning_tokens": 0,
        "cached_input_tokens": 0,
        "tokens": input_tokens + output_tokens,
        "cost": 0.0001,
        "truncated": False,
        "cost_estimator_version": "v2_cached_tokens",
    }


class PALLMCallSpanWiringTests(TestCase):
    """PA-only ``_pa_wrapped_enforce_real_ai`` regression coverage."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="p4-stop3-wiring",
            email="p4-stop3-wiring@example.com",
            password="x",
        )

    def _make_entry(self):
        entry = UnifiedPAEntrypoint(
            user=self.user,
            conversation_id="pa-stop3-wiring-01",
        )
        entry._lane = "default"
        return entry

    def _pa_llm_events_qs(self, execution_id):
        return LLMCallEvent.objects.filter(execution_id=execution_id)

    # ─── ADR-0002 §3.3 query #1 — PA turn → LLM calls ────────────────

    @override_settings(PA_AGENT_EXECUTION_WRITE_ENABLED=True)
    def test_query1_pa_turn_to_llm_calls_join_works(self):
        """Given a PA AgentExecution.id, filtering LLMCallEvent by
        execution_id returns the PA-loop LLM call rows."""
        entry = self._make_entry()
        pa_row = entry._maybe_create_pa_turn_execution(
            "hello PA", trace_id="pa-q1-1", context={},
        )
        self.assertIsNotNone(pa_row)

        with patch.object(
            entry.llm_enforcer, "enforce_real_ai",
            return_value=_fake_enforcer_response(),
        ):
            result = asyncio.run(entry._pa_wrapped_enforce_real_ai(
                pa_row, "pa-q1-1", 0,
                prompt="hello PA",
                input_messages=[{"role": "user", "content": "hello"}],
                tools=None,
                previous_response_id=None,
                task_type="conversation",
                max_tokens=2000,
                agent_name="PersonalAssistant",
                trace_id="pa-q1-1",
            ))
        self.assertEqual(result["success"], True)

        # §3.3 query #1
        events = self._pa_llm_events_qs(pa_row.id)
        self.assertEqual(events.count(), 1)
        row = events.first()
        self.assertEqual(row.agent_name, "PersonalAssistant")
        self.assertEqual(row.provider, "openai")
        self.assertEqual(row.status, "SUCCESS")
        # Synthetic usage flowed into tokens_in/tokens_out
        self.assertEqual(row.tokens_in, 42)
        self.assertEqual(row.tokens_out, 7)
        # Metadata pa_trace_id populated
        self.assertEqual(row.metadata.get("pa_trace_id"), "pa-q1-1")
        self.assertEqual(row.metadata.get("iteration"), 0)

    # ─── ADR-0002 §3.3 query #2 — LLM call → PA turn ─────────────────

    @override_settings(PA_AGENT_EXECUTION_WRITE_ENABLED=True)
    def test_query2_llm_call_to_pa_turn_reverse_join_works(self):
        """Given LLMCallEvent.execution_id, the reverse
        AgentExecution.objects.filter(id=<exec_id>) resolves to a
        PersonalAssistant agent row."""
        entry = self._make_entry()
        pa_row = entry._maybe_create_pa_turn_execution(
            "reverse join test", trace_id="pa-q2-1", context={},
        )
        with patch.object(
            entry.llm_enforcer, "enforce_real_ai",
            return_value=_fake_enforcer_response(),
        ):
            asyncio.run(entry._pa_wrapped_enforce_real_ai(
                pa_row, "pa-q2-1", 0,
                prompt="reverse",
                input_messages=[{"role": "user", "content": "reverse"}],
                tools=None,
                previous_response_id=None,
                task_type="conversation",
                max_tokens=2000,
                agent_name="PersonalAssistant",
                trace_id="pa-q2-1",
            ))

        llm_call = self._pa_llm_events_qs(pa_row.id).first()
        self.assertIsNotNone(llm_call)
        self.assertIsNotNone(llm_call.execution_id)

        # §3.3 query #2
        resolved = AgentExecution.objects.filter(id=llm_call.execution_id).first()
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.agent.name, "PersonalAssistant")

    # ─── ADR-0002 §3.3 query #3 — retries share execution_id ─────────

    @override_settings(PA_AGENT_EXECUTION_WRITE_ENABLED=True)
    def test_query3_retries_share_execution_id(self):
        """Multiple LLMCallEvent rows with distinct call_id share
        one execution_id when the agentic loop retries within a
        turn (agentic-loop iterations)."""
        entry = self._make_entry()
        pa_row = entry._maybe_create_pa_turn_execution(
            "retry chain", trace_id="pa-q3-1", context={},
        )
        with patch.object(
            entry.llm_enforcer, "enforce_real_ai",
            return_value=_fake_enforcer_response(),
        ):
            # Simulate 3 loop iterations
            for iteration in range(3):
                asyncio.run(entry._pa_wrapped_enforce_real_ai(
                    pa_row, "pa-q3-1", iteration,
                    prompt=f"iteration {iteration}",
                    input_messages=[{"role": "user", "content": f"iter {iteration}"}],
                    tools=None,
                    previous_response_id=None,
                    task_type="conversation",
                    max_tokens=2000,
                    agent_name="PersonalAssistant",
                    trace_id="pa-q3-1",
                ))

        events = self._pa_llm_events_qs(pa_row.id)
        self.assertEqual(events.count(), 3)
        # All three share execution_id
        exec_ids = set(events.values_list("execution_id", flat=True))
        self.assertEqual(exec_ids, {pa_row.id})
        # But have distinct call_ids
        call_ids = set(events.values_list("call_id", flat=True))
        self.assertEqual(len(call_ids), 3)
        # Iterations differ in metadata
        iterations = {e.metadata.get("iteration") for e in events}
        self.assertEqual(iterations, {0, 1, 2})

    # ─── Existing non-PA llm_call_span behavior unchanged ────────────

    def test_existing_non_pa_llm_call_span_still_works(self):
        """Non-PA callers using llm_call_span directly (e.g.
        code_review_agent) still produce LLMCallEvent rows with
        their own agent_name — unchanged by PA wrapper."""
        import uuid

        from core.services.llm_call_wrapper import llm_call_span

        fake_agent_execution_id = uuid.uuid4()
        with llm_call_span(
            provider="openai",
            model="gpt-5.2",
            execution_id=fake_agent_execution_id,
            agent_name="CodeReviewAgent",
            metadata={"caller_test": True},
        ) as span:
            span.attach_response({"usage": {"input_tokens": 11, "output_tokens": 22}})

        events = LLMCallEvent.objects.filter(execution_id=fake_agent_execution_id)
        self.assertEqual(events.count(), 1)
        row = events.first()
        self.assertEqual(row.agent_name, "CodeReviewAgent")
        self.assertNotEqual(row.agent_name, "PersonalAssistant")
        self.assertEqual(row.status, "SUCCESS")
        self.assertEqual(row.tokens_in, 11)
        self.assertEqual(row.tokens_out, 22)

    # ─── Flag-OFF rollback preserves pre-Stop-3 behavior ─────────────

    @override_settings(PA_AGENT_EXECUTION_WRITE_ENABLED=False)
    def test_flag_off_bypasses_wrapper_zero_llm_events(self):
        """Flag OFF: _pa_wrapped_enforce_real_ai bypasses
        llm_call_span entirely. Zero LLMCallEvent rows created,
        pre-Stop-3 behavior preserved bit-for-bit."""
        entry = self._make_entry()
        # Flag OFF → create returns None
        pa_row = entry._maybe_create_pa_turn_execution(
            "flag off", trace_id="pa-off-1", context={},
        )
        self.assertIsNone(pa_row)

        baseline = LLMCallEvent.objects.filter(
            agent_name="PersonalAssistant"
        ).count()

        with patch.object(
            entry.llm_enforcer, "enforce_real_ai",
            return_value=_fake_enforcer_response(),
        ):
            result = asyncio.run(entry._pa_wrapped_enforce_real_ai(
                pa_row, "pa-off-1", 0,  # pa_row is None here
                prompt="off",
                input_messages=[{"role": "user", "content": "off"}],
                tools=None,
                previous_response_id=None,
                task_type="conversation",
                max_tokens=2000,
                agent_name="PersonalAssistant",
                trace_id="pa-off-1",
            ))
        self.assertEqual(result["success"], True)

        # Zero new LLMCallEvent rows
        after = LLMCallEvent.objects.filter(
            agent_name="PersonalAssistant"
        ).count()
        self.assertEqual(after, baseline)

    # ─── Cross-cutting invariant ─────────────────────────────────────

    @override_settings(PA_AGENT_EXECUTION_WRITE_ENABLED=True)
    def test_pa_turn_end_to_end_all_four_queries(self):
        """Cross-cutting: single PA turn with 2 loop iterations
        satisfies all four §3.3 queries + non-PA row remains
        untouched."""
        import uuid

        from core.services.llm_call_wrapper import llm_call_span

        entry = self._make_entry()
        pa_row = entry._maybe_create_pa_turn_execution(
            "end-to-end", trace_id="pa-e2e-1", context={},
        )

        with patch.object(
            entry.llm_enforcer, "enforce_real_ai",
            return_value=_fake_enforcer_response(),
        ):
            for iteration in range(2):
                asyncio.run(entry._pa_wrapped_enforce_real_ai(
                    pa_row, "pa-e2e-1", iteration,
                    prompt="e2e",
                    input_messages=[{"role": "user", "content": "e2e"}],
                    tools=None,
                    previous_response_id=None,
                    task_type="conversation",
                    max_tokens=2000,
                    agent_name="PersonalAssistant",
                    trace_id="pa-e2e-1",
                ))

        # Also add a non-PA call
        other_exec_id = uuid.uuid4()
        with llm_call_span(
            provider="openai",
            model="gpt-5.2",
            execution_id=other_exec_id,
            agent_name="ThinkingAgent",
        ):
            pass

        # Query #1: PA turn → LLM calls
        pa_events = self._pa_llm_events_qs(pa_row.id)
        self.assertEqual(pa_events.count(), 2)
        for e in pa_events:
            self.assertEqual(e.agent_name, "PersonalAssistant")

        # Query #2: LLM call → PA turn
        one_call = pa_events.first()
        reverse = AgentExecution.objects.filter(id=one_call.execution_id).first()
        self.assertEqual(reverse.agent.name, "PersonalAssistant")

        # Query #3: retries share execution_id
        exec_ids = set(pa_events.values_list("execution_id", flat=True))
        self.assertEqual(exec_ids, {pa_row.id})

        # Non-PA row still exists + unaffected
        non_pa = LLMCallEvent.objects.filter(execution_id=other_exec_id)
        self.assertEqual(non_pa.count(), 1)
        self.assertEqual(non_pa.first().agent_name, "ThinkingAgent")
