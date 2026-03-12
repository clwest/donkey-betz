"""Unit tests for core/services/td_handlers_codejobs.py

Covers:
- Defaulting behaviour (no test_command => 'make test-fast')
- Allowlist acceptance
- Allowlist rejection
"""

import pytest

from core.services.td_handlers_codejobs import (
    DEFAULT_TEST_COMMAND,
    ALLOWED_TEST_COMMANDS,
    resolve_test_command,
    handle_code_job,
)


class TestResolveTestCommand:
    def test_none_defaults_to_make_test_fast(self):
        assert resolve_test_command(None) == DEFAULT_TEST_COMMAND

    def test_empty_string_defaults_to_make_test_fast(self):
        assert resolve_test_command('') == DEFAULT_TEST_COMMAND

    @pytest.mark.parametrize('cmd', sorted(ALLOWED_TEST_COMMANDS))
    def test_allowed_commands_accepted(self, cmd):
        assert resolve_test_command(cmd) == cmd

    def test_disallowed_command_raises(self):
        with pytest.raises(ValueError, match='not allowed'):
            resolve_test_command('rm -rf /')

    def test_disallowed_command_message_lists_allowed(self):
        try:
            resolve_test_command('make hack')
        except ValueError as exc:
            msg = str(exc)
            for allowed in ALLOWED_TEST_COMMANDS:
                assert allowed in msg

    def test_make_test_fast_is_in_allowlist(self):
        assert 'make test-fast' in ALLOWED_TEST_COMMANDS

    def test_make_test_is_in_allowlist(self):
        assert 'make test' in ALLOWED_TEST_COMMANDS

    def test_make_lint_is_in_allowlist(self):
        assert 'make lint' in ALLOWED_TEST_COMMANDS


class TestHandleCodeJob:
    def test_no_test_command_key_defaults(self):
        result = handle_code_job({'task_prompt': 'add feature'})
        assert result['test_command'] == DEFAULT_TEST_COMMAND

    def test_explicit_none_defaults(self):
        result = handle_code_job({'task_prompt': 'fix bug', 'test_command': None})
        assert result['test_command'] == DEFAULT_TEST_COMMAND

    def test_explicit_empty_string_defaults(self):
        result = handle_code_job({'task_prompt': 'fix bug', 'test_command': ''})
        assert result['test_command'] == DEFAULT_TEST_COMMAND

    def test_allowed_command_preserved(self):
        result = handle_code_job({'task_prompt': 'add tests', 'test_command': 'make test'})
        assert result['test_command'] == 'make test'

    def test_make_lint_preserved(self):
        result = handle_code_job({'task_prompt': 'lint', 'test_command': 'make lint'})
        assert result['test_command'] == 'make lint'

    def test_disallowed_command_raises(self):
        with pytest.raises(ValueError, match='not allowed'):
            handle_code_job({'task_prompt': 'bad job', 'test_command': 'pytest --no-header'})

    def test_original_payload_keys_preserved(self):
        job = {'task_prompt': 'refactor', 'base_branch': 'main', 'test_command': 'make test-fast'}
        result = handle_code_job(job)
        assert result['base_branch'] == 'main'
        assert result['task_prompt'] == 'refactor'

    def test_works_without_repo_row(self):
        """Runtime defaulting must not require a Repo DB row."""
        # No DB interaction should occur
        result = handle_code_job({'task_prompt': 'implement feature'})
        assert result['test_command'] == DEFAULT_TEST_COMMAND
