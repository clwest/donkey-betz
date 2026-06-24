"""Session 1230 P4 — Engineer request_mode + clarification-stall contract tests.

Locks the behavior that closes the Session 1229 Step 5 behavioral delta on
the OpenAI fallback path: given the task `"List 3 Python files in
core/services/ + line counts (markdown table only)"`, gpt-5-mini ran 12
``read_file`` iterations (correct readonly work) and then returned `"I'm
ready to make the change, but I don't yet know what you want me to do.
Could you please clarify the engineering task?"`. Root cause was the single
SYSTEM_PROMPT being anchored to write-mode work; under tool pressure
gpt-5-mini pattern-matched the dominant framing and asked for clarification.

Rigby's design call (Session 1230) — three layers tested here:

1. Two system prompts (ANSWER_SYSTEM_PROMPT vs CHANGE_SYSTEM_PROMPT),
   selected at dispatch via ``request_mode``.
2. Verb heuristic ``_infer_request_mode`` resolves ``'auto'`` to one of
   the two modes; conservative default is ``'answer'``.
3. Final-message clarification-stall contract: on answer-mode tasks, if
   the final text matches a stall marker, retry once with a hard
   "do not ask for clarification" preamble; if the retry also stalls,
   the envelope flips to ``status='contract_failure'``.

Run::

    python manage.py test core.tests.test_engineer_request_mode -v2
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.test import TestCase

from core.services.claude_code_engineer import (
    ANSWER_SYSTEM_PROMPT,
    CHANGE_SYSTEM_PROMPT,
    _CHANGE_VERBS,
    _CLARIFICATION_STALL_MARKERS,
    _SYSTEM_PROMPT_BY_MODE,
    _infer_request_mode,
    _looks_like_clarification_stall,
    execute_engineering_task,
)


# ============================================================================
# Verb heuristic
# ============================================================================


class InferRequestModeTests(TestCase):
    """`_infer_request_mode` — verb-based 'answer' vs 'change' detection."""

    def test_session_1229_line_count_task_resolves_to_answer(self):
        """The original Session 1229 Step 5 task that triggered the bug."""
        task = "List 3 Python files in core/services/ + line counts (markdown table only)"
        self.assertEqual(_infer_request_mode(task), 'answer')

    def test_explicit_change_verbs_resolve_to_change(self):
        for verb in ['add', 'fix', 'refactor', 'implement', 'rename', 'write']:
            with self.subTest(verb=verb):
                task = f"{verb.capitalize()} the foo bar"
                self.assertEqual(_infer_request_mode(task), 'change')

    def test_change_verb_after_clause_boundary_triggers_change(self):
        task = "Look at core/services/foo.py. Fix the broken handler."
        self.assertEqual(_infer_request_mode(task), 'change')

    def test_change_verb_embedded_in_noun_does_not_trigger(self):
        """`create_pr` as a tool reference must not flag change mode."""
        task = "List the args accepted by the create_pr tool helper."
        self.assertEqual(_infer_request_mode(task), 'answer')

    def test_empty_task_defaults_to_answer(self):
        self.assertEqual(_infer_request_mode(''), 'answer')
        self.assertEqual(_infer_request_mode('   '), 'answer')
        self.assertEqual(_infer_request_mode(None), 'answer')

    def test_case_insensitive(self):
        self.assertEqual(_infer_request_mode('FIX the bug'), 'change')
        self.assertEqual(_infer_request_mode('Implement caching'), 'change')

    def test_ambiguous_question_defaults_to_answer(self):
        for task in [
            "What does the workspace_id field default to?",
            "Where is the TEMPLATE_LEAK_TITLE_TOKENS gate evaluated?",
            "How many agents are registered in AGENT_MAP?",
            "Show me the docstring on build_semantic_research_title.",
        ]:
            with self.subTest(task=task):
                self.assertEqual(_infer_request_mode(task), 'answer')


# ============================================================================
# Clarification-stall detector
# ============================================================================


class ClarificationStallDetectorTests(TestCase):
    """`_looks_like_clarification_stall` — must catch the exact Session 1229
    Step 5 response and similar shapes."""

    def test_session_1229_response_matches(self):
        text = (
            "I'm ready to make the change, but I don't yet know what you want "
            "me to do. Could you please clarify the engineering task? For "
            "example:\n\n- Describe the bug or feature..."
        )
        self.assertTrue(_looks_like_clarification_stall(text))

    def test_clean_answer_does_not_match(self):
        text = (
            "| File | Lines |\n|---|---|\n"
            "| core/services/foo.py | 1234 |\n"
            "| core/services/bar.py | 567 |\n"
            "| core/services/baz.py | 890 |\n"
        )
        self.assertFalse(_looks_like_clarification_stall(text))

    def test_empty_string_does_not_match(self):
        self.assertFalse(_looks_like_clarification_stall(''))
        self.assertFalse(_looks_like_clarification_stall(None))

    def test_case_insensitive(self):
        self.assertTrue(
            _looks_like_clarification_stall("COULD YOU PLEASE CLARIFY THE TASK?")
        )

    def test_each_marker_is_detectable(self):
        for marker in _CLARIFICATION_STALL_MARKERS:
            with self.subTest(marker=marker):
                # Wrap each marker in surrounding text to confirm substring match.
                text = f"prefix prefix {marker} suffix suffix"
                self.assertTrue(_looks_like_clarification_stall(text))


# ============================================================================
# Prompt selection
# ============================================================================


class PromptSelectionTests(TestCase):
    """`_SYSTEM_PROMPT_BY_MODE` must cover both modes; prompts must reflect
    their intent."""

    def test_both_modes_have_prompts(self):
        self.assertIn('answer', _SYSTEM_PROMPT_BY_MODE)
        self.assertIn('change', _SYSTEM_PROMPT_BY_MODE)
        self.assertIsNotNone(_SYSTEM_PROMPT_BY_MODE['answer'])
        self.assertIsNotNone(_SYSTEM_PROMPT_BY_MODE['change'])

    def test_answer_prompt_forbids_clarification(self):
        prompt = ANSWER_SYSTEM_PROMPT.lower()
        # Each of these must be in the answer prompt; missing any means the
        # contract has weakened.
        for required in [
            'do not ask for clarification',
            'readonly',
            'do not create branches',
        ]:
            with self.subTest(required=required):
                self.assertIn(required, prompt)

    def test_change_prompt_keeps_write_framing(self):
        prompt = CHANGE_SYSTEM_PROMPT.lower()
        self.assertIn('create a branch', prompt)
        self.assertIn('commit', prompt)

    def test_prompts_are_distinct(self):
        self.assertNotEqual(ANSWER_SYSTEM_PROMPT, CHANGE_SYSTEM_PROMPT)


# ============================================================================
# Dispatcher: mode resolution + retry contract
# ============================================================================


def _stub_openai_client(messages_to_return):
    """Build a stub OpenAI client whose `chat.completions.create` returns
    one stub `message` per call, in order. Each entry is a string (becomes
    the assistant content with finish_reason='stop')."""
    client = MagicMock()
    responses = []
    for content in messages_to_return:
        msg = MagicMock()
        msg.content = content
        msg.tool_calls = None
        choice = MagicMock()
        choice.message = msg
        choice.finish_reason = 'stop'
        resp = MagicMock()
        resp.choices = [choice]
        responses.append(resp)
    client.chat.completions.create.side_effect = responses
    return client


class DispatchModeResolutionTests(TestCase):
    """`execute_engineering_task` resolves `request_mode='auto'` via heuristic
    and respects explicit overrides."""

    @patch('core.services.claude_code_engineer._ensure_git_repo', lambda: None)
    @patch('core.services.claude_code_engineer._post_to_conversation', lambda *a, **k: None)
    @patch.dict('os.environ', {'CLAUDE_CODE_ENGINE_PROVIDER': 'openai'}, clear=False)
    def test_explicit_answer_mode_passes_answer_prompt_to_openai(self):
        captured = {}
        client = MagicMock()

        def _capture(*args, **kwargs):
            captured['messages'] = kwargs.get('messages')
            msg = MagicMock()
            msg.content = '| File | Lines |\n|---|---|\n| a.py | 10 |'
            msg.tool_calls = None
            choice = MagicMock()
            choice.message = msg
            choice.finish_reason = 'stop'
            resp = MagicMock()
            resp.choices = [choice]
            return resp

        client.chat.completions.create.side_effect = _capture
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=client,
        ):
            result = execute_engineering_task(
                task_description='Show me the foo bar.',
                conversation_id=None,
                max_iterations=3,
                request_mode='answer',
            )
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['mode'], 'answer')
        # System message must be ANSWER_SYSTEM_PROMPT.
        self.assertEqual(captured['messages'][0]['role'], 'system')
        self.assertEqual(captured['messages'][0]['content'], ANSWER_SYSTEM_PROMPT)

    @patch('core.services.claude_code_engineer._ensure_git_repo', lambda: None)
    @patch('core.services.claude_code_engineer._post_to_conversation', lambda *a, **k: None)
    @patch.dict('os.environ', {'CLAUDE_CODE_ENGINE_PROVIDER': 'openai'}, clear=False)
    def test_explicit_change_mode_passes_change_prompt_to_openai(self):
        captured = {}
        client = MagicMock()

        def _capture(*args, **kwargs):
            captured['messages'] = kwargs.get('messages')
            msg = MagicMock()
            msg.content = 'Branch + PR created.'
            msg.tool_calls = None
            choice = MagicMock()
            choice.message = msg
            choice.finish_reason = 'stop'
            resp = MagicMock()
            resp.choices = [choice]
            return resp

        client.chat.completions.create.side_effect = _capture
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=client,
        ):
            result = execute_engineering_task(
                task_description='Look at foo.',
                conversation_id=None,
                max_iterations=3,
                request_mode='change',
            )
        self.assertEqual(result['mode'], 'change')
        self.assertEqual(captured['messages'][0]['content'], CHANGE_SYSTEM_PROMPT)

    @patch('core.services.claude_code_engineer._ensure_git_repo', lambda: None)
    @patch('core.services.claude_code_engineer._post_to_conversation', lambda *a, **k: None)
    @patch.dict('os.environ', {'CLAUDE_CODE_ENGINE_PROVIDER': 'openai'}, clear=False)
    def test_auto_mode_on_answer_task_resolves_to_answer(self):
        client = _stub_openai_client(['answer'])
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=client,
        ):
            result = execute_engineering_task(
                task_description='List 3 Python files in core/services/ + line counts.',
                conversation_id=None,
                max_iterations=3,
                request_mode='auto',
            )
        self.assertEqual(result['mode'], 'answer')

    @patch('core.services.claude_code_engineer._ensure_git_repo', lambda: None)
    @patch('core.services.claude_code_engineer._post_to_conversation', lambda *a, **k: None)
    @patch.dict('os.environ', {'CLAUDE_CODE_ENGINE_PROVIDER': 'openai'}, clear=False)
    def test_auto_mode_on_change_task_resolves_to_change(self):
        client = _stub_openai_client(['change made'])
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=client,
        ):
            result = execute_engineering_task(
                task_description='Fix the broken handler in foo.py.',
                conversation_id=None,
                max_iterations=3,
                request_mode='auto',
            )
        self.assertEqual(result['mode'], 'change')

    @patch('core.services.claude_code_engineer._ensure_git_repo', lambda: None)
    @patch('core.services.claude_code_engineer._post_to_conversation', lambda *a, **k: None)
    @patch.dict('os.environ', {'CLAUDE_CODE_ENGINE_PROVIDER': 'openai'}, clear=False)
    def test_unknown_request_mode_falls_back_to_auto(self):
        client = _stub_openai_client(['answer'])
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=client,
        ):
            result = execute_engineering_task(
                task_description='What is foo?',
                conversation_id=None,
                max_iterations=3,
                request_mode='banana',
            )
        # 'banana' is unknown → falls back to heuristic → 'answer'
        self.assertEqual(result['mode'], 'answer')
        self.assertEqual(result['status'], 'success')


# ============================================================================
# Dispatcher: clarification-stall retry contract
# ============================================================================


class ClarificationStallRetryTests(TestCase):
    """On answer-mode tasks, a stall triggers ONE retry with a hardened
    preamble. If the retry also stalls, status flips to `contract_failure`."""

    @patch('core.services.claude_code_engineer._ensure_git_repo', lambda: None)
    @patch('core.services.claude_code_engineer._post_to_conversation', lambda *a, **k: None)
    @patch.dict('os.environ', {'CLAUDE_CODE_ENGINE_PROVIDER': 'openai'}, clear=False)
    def test_stall_then_clean_answer_returns_success(self):
        # First call stalls; second call (the retry) produces a clean answer.
        client = _stub_openai_client([
            "Could you please clarify the engineering task?",
            "| File | Lines |\n|---|---|\n| a.py | 10 |",
        ])
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=client,
        ):
            result = execute_engineering_task(
                task_description='List 3 Python files with line counts.',
                conversation_id=None,
                max_iterations=3,
                request_mode='answer',
            )
        self.assertEqual(result['status'], 'success')
        # The clean answer is the summary.
        self.assertIn('| File | Lines |', result['summary'])
        # Two LLM calls were made (original + retry).
        self.assertEqual(client.chat.completions.create.call_count, 2)

    @patch('core.services.claude_code_engineer._ensure_git_repo', lambda: None)
    @patch('core.services.claude_code_engineer._post_to_conversation', lambda *a, **k: None)
    @patch.dict('os.environ', {'CLAUDE_CODE_ENGINE_PROVIDER': 'openai'}, clear=False)
    def test_stall_then_stall_returns_contract_failure(self):
        client = _stub_openai_client([
            "Could you please clarify the engineering task?",
            "I'm not sure what you want — please describe the bug.",
        ])
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=client,
        ):
            result = execute_engineering_task(
                task_description='List 3 Python files with line counts.',
                conversation_id=None,
                max_iterations=3,
                request_mode='answer',
            )
        self.assertEqual(result['status'], 'contract_failure')
        self.assertEqual(result['mode'], 'answer')
        # The summary still surfaces the bad text so caller sees what happened.
        self.assertIn('not sure', result['summary'].lower())
        self.assertEqual(client.chat.completions.create.call_count, 2)

    @patch('core.services.claude_code_engineer._ensure_git_repo', lambda: None)
    @patch('core.services.claude_code_engineer._post_to_conversation', lambda *a, **k: None)
    @patch.dict('os.environ', {'CLAUDE_CODE_ENGINE_PROVIDER': 'openai'}, clear=False)
    def test_clean_answer_first_try_does_not_retry(self):
        client = _stub_openai_client([
            "| File | Lines |\n|---|---|\n| a.py | 10 |",
        ])
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=client,
        ):
            result = execute_engineering_task(
                task_description='List 3 Python files with line counts.',
                conversation_id=None,
                max_iterations=3,
                request_mode='answer',
            )
        self.assertEqual(result['status'], 'success')
        # Only ONE LLM call — no retry triggered.
        self.assertEqual(client.chat.completions.create.call_count, 1)

    @patch('core.services.claude_code_engineer._ensure_git_repo', lambda: None)
    @patch('core.services.claude_code_engineer._post_to_conversation', lambda *a, **k: None)
    @patch.dict('os.environ', {'CLAUDE_CODE_ENGINE_PROVIDER': 'openai'}, clear=False)
    def test_change_mode_does_not_retry_on_clarification(self):
        """Change-mode tasks legitimately ask for clarification when the task
        is ambiguous (e.g. "fix the bug" with no bug specified). Retry must
        NOT fire — that would be over-eager."""
        client = _stub_openai_client([
            "Could you please clarify which bug you want fixed?",
        ])
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=client,
        ):
            result = execute_engineering_task(
                task_description='Fix the bug.',
                conversation_id=None,
                max_iterations=3,
                request_mode='change',
            )
        # Status stays 'success' because change mode allows clarification.
        self.assertEqual(result['status'], 'success')
        self.assertEqual(client.chat.completions.create.call_count, 1)


# ============================================================================
# Smoke: each declared change verb is detectable
# ============================================================================


class ChangeVerbCoverageTests(TestCase):
    """Smoke check: every verb in `_CHANGE_VERBS` resolves to 'change' when
    used at the start of a task. Locks against future regressions where a
    verb is added to the tuple but the regex doesn't pick it up."""

    def test_each_change_verb_at_clause_start(self):
        for verb in _CHANGE_VERBS:
            with self.subTest(verb=verb):
                task = f"{verb.capitalize()} the foo helper to add bar."
                self.assertEqual(
                    _infer_request_mode(task), 'change',
                    msg=f"Verb {verb!r} did not trigger change mode.",
                )
