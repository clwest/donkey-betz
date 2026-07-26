"""
Tests for execute_engineering_task_v2 (Session 2968 PR-A).

Verifies the Option β subprocess dispatch path — the v2 codepath that shells
out to the `claude` CLI instead of running the homegrown v1 LLM loop.

Scope per Rigby T1 SIGN refinements (2026-07-25):
  1. Envelope maps CLI JSON shape correctly (captured from real probe)
  2. Missing CLI binary fails loud with error envelope + no subprocess call
  3. Subprocess timeout returns error envelope (not raise)
  4. cwd= is set to workspace_root_path (Rigby SIGN add)
  5. max_cost_usd < $0.25 refused pre-flight (Rigby SIGN mitigation #1)
  6. --max-turns hard-capped at V2_HARD_MAX_TURNS_CEILING regardless of caller
     (Rigby SIGN mitigation #2)
  7. startup_tax_dominated warning fires when cost >= $0.10 AND turns <= 2

Plus 1 unit test on _v2_pick_primary_model helper (multi-key modelUsage tie-break).

Design pattern mirrors core/tests/test_engineer_budget_caps.py — SimpleTestCase,
mock subprocess.run at claude_code_engineer's import site, drive scenarios via
the mock's return_value / side_effect.
"""
import json
from unittest.mock import patch, MagicMock
from subprocess import TimeoutExpired
from django.test import SimpleTestCase


# ── Captured real CLI JSON shape from 2026-07-25 probe ─────────────────
# `claude -p --output-format json --max-turns 1 --model sonnet "Say the word DONE."`
_REAL_CLI_JSON = {
    "type": "result",
    "subtype": "success",
    "is_error": False,
    "api_error_status": None,
    "duration_ms": 6274,
    "duration_api_ms": 6261,
    "num_turns": 1,
    "result": "DONE",
    "stop_reason": "end_turn",
    "session_id": "66c8f5ed-5799-4ce9-a2ee-561a8b2fb96b",
    "total_cost_usd": 0.12914175,
    "usage": {
        "input_tokens": 3,
        "cache_creation_input_tokens": 33513,
        "cache_read_input_tokens": 11280,
        "output_tokens": 5,
    },
    "modelUsage": {
        "claude-sonnet-4-6": {
            "inputTokens": 3,
            "outputTokens": 5,
            "cacheReadInputTokens": 11280,
            "cacheCreationInputTokens": 33513,
            "webSearchRequests": 0,
            "costUSD": 0.12914175,
            "contextWindow": 200000,
            "maxOutputTokens": 32000,
        }
    },
    "permission_denials": [],
    "terminal_reason": "completed",
    "fast_mode_state": "off",
    "uuid": "8ee5d851-6102-447f-a50c-72ec337835b5",
}


def _make_completed(returncode=0, stdout=None, stderr=""):
    """Build a fake CompletedProcess for subprocess.run mocks."""
    completed = MagicMock()
    completed.returncode = returncode
    completed.stdout = json.dumps(stdout if stdout is not None else _REAL_CLI_JSON)
    completed.stderr = stderr
    return completed


class TestV2EnvelopeShapeMapping(SimpleTestCase):
    """CLI JSON → envelope field mapping (the whole point of the wrapper)."""

    @patch('core.services.claude_code_engineer._post_to_conversation')
    @patch('core.services.claude_code_engineer._resolve_repo_root', return_value='/tmp/repo')
    @patch('core.services.claude_code_engineer.subprocess.run')
    @patch('core.services.claude_code_engineer._CLAUDE_CLI_BIN', '/fake/bin/claude')
    def test_v2_maps_all_fields_from_real_cli_json(
        self, mock_run, mock_repo, mock_post,
    ):
        """All fields captured from the real 2026-07-25 CLI probe map correctly."""
        from core.services.claude_code_engineer import execute_engineering_task_v2

        mock_run.return_value = _make_completed(returncode=0)

        result = execute_engineering_task_v2(
            task_description="Say DONE.",
            workspace_root_path='/tmp/repo',
            max_iterations=10,
            request_mode='answer',
        )

        # Core envelope shape (must match v1)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['summary'], 'DONE')
        self.assertEqual(result['iterations_used'], 1)
        self.assertEqual(result['iterations'], 1)
        self.assertEqual(result['cost_usd'], 0.1291)  # rounded to 4 places
        self.assertEqual(result['repo_root'], '/tmp/repo')
        self.assertFalse(result['budget_exceeded'])
        self.assertEqual(result['files_changed'], [])
        self.assertIsNone(result['pr_url'])

        # v2-specific fields
        self.assertEqual(result['engine_mode'], 'v2')
        self.assertEqual(result['session_id'], '66c8f5ed-5799-4ce9-a2ee-561a8b2fb96b')
        self.assertEqual(result['model_used'], 'claude-sonnet-4-6')
        self.assertEqual(result['model_usage']['claude-sonnet-4-6']['costUSD'], 0.12914175)
        self.assertEqual(result['stop_reason'], 'end_turn')
        self.assertEqual(result['terminal_reason'], 'completed')
        self.assertEqual(result['duration_ms'], 6274)
        self.assertFalse(result['is_error'])
        self.assertIsNone(result['api_error_status'])
        self.assertEqual(result['permission_denials'], [])
        self.assertEqual(result['provider'], 'claude-cli')


class TestV2MissingCliFailsLoud(SimpleTestCase):
    """When shutil.which('claude') returned None at import, dispatch is refused."""

    @patch('core.services.claude_code_engineer._post_to_conversation')
    @patch('core.services.claude_code_engineer._resolve_repo_root', return_value='/tmp/repo')
    @patch('core.services.claude_code_engineer.subprocess.run')
    @patch('core.services.claude_code_engineer._CLAUDE_CLI_BIN', None)
    def test_v2_returns_error_envelope_when_cli_missing(
        self, mock_run, mock_repo, mock_post,
    ):
        """No subprocess call attempted; error envelope explains v1 fallback."""
        from core.services.claude_code_engineer import execute_engineering_task_v2

        result = execute_engineering_task_v2(
            task_description="anything",
            workspace_root_path='/tmp/repo',
        )

        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['engine_mode'], 'v2')
        self.assertIn('CLI not found', result['error'])
        self.assertIn('CLAUDE_CODE_ENGINE_MODE=v1', result['error'])
        mock_run.assert_not_called()
        mock_post.assert_called_once()  # fail-loud posts to conversation


class TestV2TimeoutReturnsEnvelope(SimpleTestCase):
    """Subprocess timeout is caught + surfaced as error envelope (not raised)."""

    @patch('core.services.claude_code_engineer._post_to_conversation')
    @patch('core.services.claude_code_engineer._resolve_repo_root', return_value='/tmp/repo')
    @patch('core.services.claude_code_engineer.subprocess.run')
    @patch('core.services.claude_code_engineer._CLAUDE_CLI_BIN', '/fake/bin/claude')
    def test_v2_timeout_surfaces_as_error_envelope(
        self, mock_run, mock_repo, mock_post,
    ):
        from core.services.claude_code_engineer import execute_engineering_task_v2

        mock_run.side_effect = TimeoutExpired(cmd=['claude'], timeout=60)

        result = execute_engineering_task_v2(
            task_description="anything",
            workspace_root_path='/tmp/repo',
            timeout_seconds=60,
        )

        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['engine_mode'], 'v2')
        self.assertIn('timed out after 60s', result['error'])
        self.assertIsNotNone(result['session_id'])  # generated pre-dispatch


class TestV2UsesWorkspaceRootPathAsCwd(SimpleTestCase):
    """Rigby SIGN add: subprocess.run is called with cwd=workspace_root_path.

    This test proves the S2967 workspace-resolution fix carries through to v2
    (the whole reason we added workspace_id resolution in Slice 7).
    """

    @patch('core.services.claude_code_engineer._post_to_conversation')
    @patch('core.services.claude_code_engineer._resolve_repo_root', return_value='/Users/donkeyking/Donkey_Betz/unified-donkey-betz')
    @patch('core.services.claude_code_engineer.subprocess.run')
    @patch('core.services.claude_code_engineer._CLAUDE_CLI_BIN', '/fake/bin/claude')
    def test_subprocess_cwd_matches_workspace_root_path(
        self, mock_run, mock_repo, mock_post,
    ):
        from core.services.claude_code_engineer import execute_engineering_task_v2

        mock_run.return_value = _make_completed(returncode=0)
        expected_cwd = '/Users/donkeyking/Donkey_Betz/unified-donkey-betz'

        execute_engineering_task_v2(
            task_description="anything",
            workspace_root_path=expected_cwd,
        )

        # subprocess.run was called with cwd=expected_cwd
        call_kwargs = mock_run.call_args.kwargs
        self.assertEqual(call_kwargs['cwd'], expected_cwd)


class TestV2RefusesLowCostCap(SimpleTestCase):
    """Rigby SIGN mitigation #1: v2 refuses max_cost_usd < $0.25.

    CLI startup alone (33K ephemeral cache tokens) burned $0.13 in tonight's
    probe. A sub-$0.25 cap is guaranteed to blow — refuse rather than accept.
    """

    @patch('core.services.claude_code_engineer._post_to_conversation')
    @patch('core.services.claude_code_engineer._resolve_repo_root', return_value='/tmp/repo')
    @patch('core.services.claude_code_engineer.subprocess.run')
    @patch('core.services.claude_code_engineer._CLAUDE_CLI_BIN', '/fake/bin/claude')
    def test_v2_refuses_when_cost_cap_below_floor(
        self, mock_run, mock_repo, mock_post,
    ):
        from core.services.claude_code_engineer import execute_engineering_task_v2

        result = execute_engineering_task_v2(
            task_description="anything",
            workspace_root_path='/tmp/repo',
            max_cost_usd=0.10,  # below $0.25 floor
        )

        self.assertEqual(result['status'], 'error')
        self.assertIn('below v2 floor', result['error'])
        self.assertIn('$0.25', result['error'])
        mock_run.assert_not_called()

    @patch('core.services.claude_code_engineer._post_to_conversation')
    @patch('core.services.claude_code_engineer._resolve_repo_root', return_value='/tmp/repo')
    @patch('core.services.claude_code_engineer.subprocess.run')
    @patch('core.services.claude_code_engineer._CLAUDE_CLI_BIN', '/fake/bin/claude')
    def test_v2_accepts_cost_cap_at_or_above_floor(
        self, mock_run, mock_repo, mock_post,
    ):
        from core.services.claude_code_engineer import execute_engineering_task_v2

        mock_run.return_value = _make_completed(returncode=0)

        result = execute_engineering_task_v2(
            task_description="anything",
            workspace_root_path='/tmp/repo',
            max_cost_usd=0.25,  # exactly at floor
        )

        self.assertNotEqual(result['status'], 'error')
        mock_run.assert_called_once()


class TestV2HardCapsMaxTurns(SimpleTestCase):
    """Rigby SIGN mitigation #2: --max-turns capped at 50 regardless of caller."""

    @patch('core.services.claude_code_engineer._post_to_conversation')
    @patch('core.services.claude_code_engineer._resolve_repo_root', return_value='/tmp/repo')
    @patch('core.services.claude_code_engineer.subprocess.run')
    @patch('core.services.claude_code_engineer._CLAUDE_CLI_BIN', '/fake/bin/claude')
    def test_max_turns_arg_capped_at_ceiling(
        self, mock_run, mock_repo, mock_post,
    ):
        from core.services.claude_code_engineer import (
            execute_engineering_task_v2,
            V2_HARD_MAX_TURNS_CEILING,
        )

        mock_run.return_value = _make_completed(returncode=0)

        # Caller requests 200 iterations; v2 must cap at ceiling (50)
        execute_engineering_task_v2(
            task_description="anything",
            workspace_root_path='/tmp/repo',
            max_iterations=200,
        )

        cmd_args = mock_run.call_args.args[0]  # first positional = cmd list
        max_turns_idx = cmd_args.index('--max-turns')
        capped_value = int(cmd_args[max_turns_idx + 1])
        self.assertEqual(capped_value, V2_HARD_MAX_TURNS_CEILING)


class TestV2StartupTaxWarning(SimpleTestCase):
    """Rigby SIGN refinement #3: startup_tax_dominated warning fires when
    cost >= $0.10 AND num_turns <= 2 (heuristic that startup dominated the run).
    """

    @patch('core.services.claude_code_engineer._post_to_conversation')
    @patch('core.services.claude_code_engineer._resolve_repo_root', return_value='/tmp/repo')
    @patch('core.services.claude_code_engineer.subprocess.run')
    @patch('core.services.claude_code_engineer._CLAUDE_CLI_BIN', '/fake/bin/claude')
    def test_warning_fires_on_tiny_expensive_run(
        self, mock_run, mock_repo, mock_post,
    ):
        from core.services.claude_code_engineer import execute_engineering_task_v2

        # Real probe: 1 turn, $0.129 cost — canonical startup-tax scenario
        mock_run.return_value = _make_completed(returncode=0)

        result = execute_engineering_task_v2(
            task_description="Say DONE.",
            workspace_root_path='/tmp/repo',
        )

        self.assertIn('startup_tax_dominated', result['warnings'])

    @patch('core.services.claude_code_engineer._post_to_conversation')
    @patch('core.services.claude_code_engineer._resolve_repo_root', return_value='/tmp/repo')
    @patch('core.services.claude_code_engineer.subprocess.run')
    @patch('core.services.claude_code_engineer._CLAUDE_CLI_BIN', '/fake/bin/claude')
    def test_no_warning_on_substantial_run(
        self, mock_run, mock_repo, mock_post,
    ):
        from core.services.claude_code_engineer import execute_engineering_task_v2

        # 10 turns, $2.50 — substantial work, no startup-tax warning
        substantial = dict(_REAL_CLI_JSON, num_turns=10, total_cost_usd=2.50)
        mock_run.return_value = _make_completed(returncode=0, stdout=substantial)

        result = execute_engineering_task_v2(
            task_description="Do substantial work.",
            workspace_root_path='/tmp/repo',
        )

        self.assertEqual(result['warnings'], [])


class TestV2BudgetExceededOnDefaultCap(SimpleTestCase):
    """Rigby A2 SIGN F-BLOCKING fix: budget_exceeded must trip when the CLI
    cost exceeds effective_max_cost_usd — regardless of whether the caller
    set max_cost_usd explicitly or the DEFAULT_MAX_COST_USD default fired.
    """

    @patch('core.services.claude_code_engineer._post_to_conversation')
    @patch('core.services.claude_code_engineer._resolve_repo_root', return_value='/tmp/repo')
    @patch('core.services.claude_code_engineer.subprocess.run')
    @patch('core.services.claude_code_engineer._CLAUDE_CLI_BIN', '/fake/bin/claude')
    @patch('core.services.claude_code_engineer.DEFAULT_MAX_COST_USD', 0.50)
    def test_budget_exceeded_trips_on_default_cap(
        self, mock_run, mock_repo, mock_post,
    ):
        from core.services.claude_code_engineer import execute_engineering_task_v2

        # Caller omits max_cost_usd; effective cap = DEFAULT_MAX_COST_USD (patched to $0.50).
        # CLI reports $1.00 cost — should trip budget_exceeded even though
        # caller-supplied cap is None.
        expensive = dict(_REAL_CLI_JSON, total_cost_usd=1.00)
        mock_run.return_value = _make_completed(returncode=0, stdout=expensive)

        result = execute_engineering_task_v2(
            task_description="anything",
            workspace_root_path='/tmp/repo',
            max_cost_usd=None,  # explicit None so default fires
        )

        self.assertEqual(result['status'], 'budget_exceeded')
        self.assertTrue(result['budget_exceeded'])
        self.assertEqual(result['effective_max_cost_usd'], 0.50)
        self.assertEqual(result['cost_usd'], 1.0)


class TestV2PickPrimaryModelHelper(SimpleTestCase):
    """Unit test for _v2_pick_primary_model — multi-key highest-cost tie-break."""

    def test_single_key_returns_the_key(self):
        from core.services.claude_code_engineer import _v2_pick_primary_model

        model_usage = {'claude-sonnet-4-6': {'costUSD': 0.12}}
        self.assertEqual(_v2_pick_primary_model(model_usage), 'claude-sonnet-4-6')

    def test_multi_key_returns_highest_cost(self):
        from core.services.claude_code_engineer import _v2_pick_primary_model

        model_usage = {
            'claude-haiku-4-5': {'costUSD': 0.02},
            'claude-sonnet-4-6': {'costUSD': 0.15},
            'claude-opus-4-6': {'costUSD': 0.85},
        }
        self.assertEqual(_v2_pick_primary_model(model_usage), 'claude-opus-4-6')

    def test_empty_returns_none(self):
        from core.services.claude_code_engineer import _v2_pick_primary_model

        self.assertIsNone(_v2_pick_primary_model({}))
        self.assertIsNone(_v2_pick_primary_model(None))
