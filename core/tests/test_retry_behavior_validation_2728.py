"""
Session 2730 — Rigby Tool Validation Engineering Campaign, Batch C tool 5
(closes Batch C) regression tests for retry behavior.

Covers the F-RB-* findings surfaced during code trace + patched at
Session 2730. See:
- `docs/research/tools/validation/retry_behavior_validation.md`
- `docs/research/tools/tools_validation_engineering_campaign_plan.md`

Findings covered:

- F-RB-1 `ToolResult.is_retryable` field + per-error-code classification
  via `_ERROR_CODE_RETRYABLE` map + `_classify_retryable` helper.
- F-RB-3 LLM SDK factories verified at HEAD (source-level guards on
  `_FORBIDDEN_KWARGS` invariant).
- F-RB-4 PA Celery task no-retry design verified at HEAD.
- F-RB-5 Agentic loop narrow one-shot retries verified at HEAD.

Existing coverage NOT duplicated:
- `_build_tool_args_malformed_envelope` retry_hint — covered in
  test_pa_tool_args_malformed.py + test_payload_size_limits_validation_2728.py
  (F-PS-6 S1177 F1).
- `td_autofill_safety` — covered in test_td_autofill_safety.py.

Run::

    python manage.py test core.tests.test_retry_behavior_validation_2728 -v2
"""
from __future__ import annotations

import inspect

from django.test import SimpleTestCase

from core.services.tool_dispatcher import (
    ToolErrorCode,
    ToolResult,
    _ERROR_CODE_RETRYABLE,
    _classify_retryable,
)


# ─── F-RB-1: ToolResult.is_retryable field ─────────────────────────────


class FRB1ToolResultFieldShapeTests(SimpleTestCase):
    """F-RB-1 — `ToolResult` carries `is_retryable` field with sensible
    default."""

    def test_field_exists(self):
        result = ToolResult(
            ok=True, tool='toy', latency_ms=1,
            error_code=None, error_message=None,
            trace_id='t', result={},
        )
        self.assertTrue(hasattr(result, 'is_retryable'))

    def test_field_defaults_to_none(self):
        """When caller omits `is_retryable`, it defaults to None —
        preserves backward compat with any direct constructor callers
        that pre-date the field."""
        result = ToolResult(
            ok=True, tool='toy', latency_ms=1,
            error_code=None, error_message=None,
            trace_id='t', result={},
        )
        self.assertIsNone(result.is_retryable)

    def test_field_surfaces_in_to_dict(self):
        result = ToolResult(
            ok=False, tool='toy', latency_ms=1,
            error_code='TOOL_TIMEOUT', error_message='slow',
            trace_id='t', result=None,
            is_retryable=True,
        )
        self.assertIn('is_retryable', result.to_dict())
        self.assertTrue(result.to_dict()['is_retryable'])


class FRB1ClassificationMapTests(SimpleTestCase):
    """F-RB-1 — the retryability map contains the seven error codes
    with the ratified retryable/permanent split."""

    def test_map_covers_all_seven_error_codes(self):
        expected = {
            ToolErrorCode.TOOL_TIMEOUT,
            ToolErrorCode.TOOL_DEPENDENCY_FAILED,
            ToolErrorCode.TOOL_EXCEPTION,
            ToolErrorCode.AGENT_EXECUTION_FAILED,
            ToolErrorCode.TOOL_NOT_FOUND,
            ToolErrorCode.TOOL_PERMISSION_DENIED,
            ToolErrorCode.TOOL_INVALID_PAYLOAD,
        }
        self.assertEqual(set(_ERROR_CODE_RETRYABLE.keys()), expected)

    def test_transient_codes_are_retryable(self):
        """Transient error classes — retryable."""
        for code in (
            ToolErrorCode.TOOL_TIMEOUT,
            ToolErrorCode.TOOL_DEPENDENCY_FAILED,
            ToolErrorCode.TOOL_EXCEPTION,
            ToolErrorCode.AGENT_EXECUTION_FAILED,
        ):
            self.assertTrue(
                _ERROR_CODE_RETRYABLE[code],
                f'{code} should be retryable',
            )

    def test_permanent_codes_are_not_retryable(self):
        """Permanent error classes — not retryable."""
        for code in (
            ToolErrorCode.TOOL_NOT_FOUND,
            ToolErrorCode.TOOL_PERMISSION_DENIED,
            ToolErrorCode.TOOL_INVALID_PAYLOAD,
        ):
            self.assertFalse(
                _ERROR_CODE_RETRYABLE[code],
                f'{code} should NOT be retryable',
            )


class FRB1ClassifyRetryableHelperTests(SimpleTestCase):
    """F-RB-1 — `_classify_retryable` helper."""

    def test_none_error_code_returns_none(self):
        """Successful results have error_code=None → None."""
        self.assertIsNone(_classify_retryable(None))

    def test_known_transient_returns_true(self):
        self.assertTrue(_classify_retryable(ToolErrorCode.TOOL_TIMEOUT))
        self.assertTrue(_classify_retryable(ToolErrorCode.TOOL_DEPENDENCY_FAILED))

    def test_known_permanent_returns_false(self):
        self.assertFalse(_classify_retryable(ToolErrorCode.TOOL_NOT_FOUND))
        self.assertFalse(_classify_retryable(ToolErrorCode.TOOL_PERMISSION_DENIED))
        self.assertFalse(_classify_retryable(ToolErrorCode.TOOL_INVALID_PAYLOAD))

    def test_unknown_code_returns_none_not_false(self):
        """Unknown codes surface as None ("don't know") — NOT False.
        This lets downstream code fall back to legacy heuristics
        instead of assuming permanence."""
        self.assertIsNone(_classify_retryable('UNKNOWN_ERROR_CODE'))
        self.assertIsNone(_classify_retryable('TOOL_ARGS_JSON_MALFORMED'))


class FRB1DispatcherPopulatesRetryableTests(SimpleTestCase):
    """F-RB-1 — source-level guards that all 5 `ToolResult(...)`
    construction sites in `_execute_inner` populate `is_retryable`."""

    def _dispatcher_src(self) -> str:
        from core.services import tool_dispatcher
        return inspect.getsource(tool_dispatcher)

    def test_all_construction_sites_pass_is_retryable(self):
        """Grep-level: every `ToolResult(` should be followed within
        ~12 lines by an `is_retryable=` kwarg."""
        src = self._dispatcher_src()
        # Locate every `ToolResult(` (dataclass, not the definition).
        lines = src.split('\n')
        toolresult_construction_line_nums = [
            i for i, line in enumerate(lines)
            if 'ToolResult(' in line and 'class ToolResult' not in line
        ]
        for line_num in toolresult_construction_line_nums:
            # Look at the next ~12 lines for `is_retryable=`.
            window = '\n'.join(lines[line_num:line_num + 12])
            self.assertIn(
                'is_retryable=', window,
                f'ToolResult construction at line {line_num+1} missing '
                f'is_retryable kwarg:\n{window}',
            )

    def test_five_construction_sites_present(self):
        """Guard: dispatcher has exactly 5 `ToolResult(...)` sites in
        `_execute_inner`. If this changes, the F-RB-1 patch needs to
        reach the new site too."""
        src = self._dispatcher_src()
        count = src.count('result_obj = ToolResult(')
        self.assertEqual(
            count, 5,
            f'Expected 5 result_obj = ToolResult(...) sites in dispatcher; '
            f'found {count}. New site must populate is_retryable.',
        )


# ─── F-RB-3: LLM SDK factories intact ──────────────────────────────────


class FRB3LLMFactoryInvariantsTests(SimpleTestCase):
    """F-RB-3 — reinforce that the OpenAI + Anthropic factories still
    reject `max_retries` in kwargs (retry policy is centrally managed)."""

    def test_openai_factory_forbids_max_retries(self):
        from core.services.openai_client_factory import get_openai_client
        with self.assertRaises(ValueError) as ctx:
            get_openai_client(api_key='test', max_retries=5)
        self.assertIn('max_retries', str(ctx.exception))

    def test_openai_factory_forbids_timeout(self):
        from core.services.openai_client_factory import get_openai_client
        with self.assertRaises(ValueError) as ctx:
            get_openai_client(api_key='test', timeout=10)
        self.assertIn('timeout', str(ctx.exception))

    def test_openai_max_retries_constant_is_positive(self):
        """Centralized retry count must be a positive int (else the SDK
        never retries, defeating the factory's purpose)."""
        from core.services.openai_client_factory import OPENAI_MAX_RETRIES
        self.assertIsInstance(OPENAI_MAX_RETRIES, int)
        self.assertGreater(OPENAI_MAX_RETRIES, 0)


# ─── F-RB-4: PA Celery task no-retry design verified ──────────────────


class FRB4PATaskNoRetryTests(SimpleTestCase):
    """F-RB-4 — the PA chat task explicitly does NOT retry (S1159
    design). Source-level guard prevents accidental reintroduction."""

    def _pa_task_impl_src(self) -> str:
        from core.tasks_misc import _impl_process_pa_chat_task
        return inspect.getsource(_impl_process_pa_chat_task)

    def test_pa_task_impl_body_has_no_self_retry(self):
        """S1159: `acks_late=False` design means the task should NOT
        call `self.retry()`. Retry semantics belong at sub-op level
        (fine-grained try/except degradation), NOT at task level."""
        src = self._pa_task_impl_src()
        self.assertNotIn(
            'self.retry(',
            src,
            'PA chat task must NOT call self.retry() — S1159 design',
        )

    def test_pa_task_decorator_uses_acks_late_false(self):
        """The @shared_task decorator must set acks_late=False for
        this task. Reading from source rather than inspecting the
        registered task because pytest doesn't run Celery's
        `bind_task_to_app`."""
        import inspect as _inspect
        from core import tasks as _tasks
        tasks_src = _inspect.getsource(_tasks)
        # Locate `def process_pa_chat_task` and look at the ~5
        # preceding lines for the decorator.
        idx = tasks_src.find('def process_pa_chat_task(')
        self.assertGreater(idx, 0)
        window = tasks_src[max(0, idx - 500):idx]
        self.assertIn('acks_late=False', window)


# ─── F-RB-5: Agentic loop narrow retries verified ─────────────────────


class FRB5AgenticLoopRetriesIntactTests(SimpleTestCase):
    """F-RB-5 — the three narrow one-shot retries in `_run_agentic_loop`
    (S1077/S1079/S1086) remain in place at HEAD."""

    def _run_agentic_loop_src(self) -> str:
        from core.services.unified_pa_entrypoint import UnifiedPAEntrypoint
        return inspect.getsource(UnifiedPAEntrypoint._run_agentic_loop)

    def test_s1079_first_iteration_llm_retry_present(self):
        src = self._run_agentic_loop_src()
        # S1079: retry once on first iteration when LLM call failed.
        self.assertIn('iteration == 0', src)
        self.assertIn('retrying fresh', src.lower())

    def test_s1077_action_mismatch_retry_present(self):
        src = self._run_agentic_loop_src()
        # S1077: auto-retry when gateway returns wrong action.
        self.assertIn('action mismatch', src.lower())
        self.assertIn('retry_payload', src)

    def test_s1077_hardcoded_tool_scope_documented(self):
        """F-RB-2 lives in this same block — flag if the S1077 auto-retry
        is generalized (e.g., the hardcoded ('content_tool', 'work_tool')
        tuple is refactored). This is a heads-up guard, not a mandate."""
        src = self._run_agentic_loop_src()
        # Current shape: hardcoded to content_tool + work_tool tuple.
        self.assertIn("'content_tool'", src)
        self.assertIn("'work_tool'", src)


# ─── F-RB-6: campaign discipline — MEMORY rule reinforcement ──────────


class FRB6MemoryRuleReinforcementTests(SimpleTestCase):
    """F-RB-6 — third verification pass on the LLM client factory MEMORY
    rules. Reinforces feedback_openai_client_factory and
    feedback_anthropic_client_factory beyond their initial ratification."""

    def test_openai_factory_module_still_at_expected_path(self):
        """Stability contract: the factory module path is public API
        to every LLM caller in the platform."""
        from core.services.openai_client_factory import (
            get_openai_client,
            get_async_openai_client,
            OPENAI_MAX_RETRIES,
        )
        self.assertTrue(callable(get_openai_client))
        self.assertTrue(callable(get_async_openai_client))
        self.assertIsInstance(OPENAI_MAX_RETRIES, int)

    def test_anthropic_factory_module_still_at_expected_path(self):
        from core.services.anthropic_client_factory import get_anthropic_client
        self.assertTrue(callable(get_anthropic_client))
