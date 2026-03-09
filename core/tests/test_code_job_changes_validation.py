"""
Tests for CodeJob implement pipeline — changes schema validation.

Covers the fix for IMPLEMENT_FAILED: 'str' object has no attribute 'get'
when Claude returns changes as a string or list[str] instead of list[dict].
"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest


def _make_log_fn():
    """Return a log_fn mock that records calls."""
    log = MagicMock()
    log.calls = []

    def _log(step, message, level='info'):
        log.calls.append((step, message, level))
        log(step, message, level)

    _log.mock = log
    _log.calls = log.calls
    return _log


def _make_claude_response(tool_input):
    """Build a mock Anthropic response with a tool_use block."""
    block = MagicMock()
    block.type = 'tool_use'
    block.name = 'apply_file_changes'
    block.input = tool_input

    response = MagicMock()
    response.content = [block]
    return response


class TestChangesSchemaValidation:
    """Test that _implement_with_claude rejects malformed changes."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        self.workdir = str(tmp_path)
        self.run = MagicMock()
        self.run.plan_summary = 'Test task'
        self.plan = {
            'task_prompt': 'Test task',
            'acceptance_criteria': [],
            'max_patch_files': 50,
            'path_filters': [],
        }
        self.log_fn = _make_log_fn()
        self.shell = MagicMock()

    def _call_implement(self, tool_input, max_attempts=1):
        """Call _implement_with_claude with a mock Claude response."""
        from core.tasks import _implement_with_claude

        mock_response = _make_claude_response(tool_input)

        with patch('anthropic.Anthropic') as mock_anthropic_cls:
            client = MagicMock()
            mock_anthropic_cls.return_value = client
            client.messages.create.return_value = mock_response

            with patch('core.tasks._gather_repo_context', return_value='mock context'):
                return _implement_with_claude(
                    self.workdir, self.run, self.plan, self.log_fn, self.shell
                )

    def test_happy_path_list_of_dicts(self, tmp_path):
        """changes as list[dict] — happy path."""
        # Create a target file for the patch
        target = tmp_path / 'hello.py'
        target.write_text('print("hello")\n')
        self.workdir = str(tmp_path)
        self.shell.return_value = MagicMock(returncode=0, stdout='', stderr='')

        tool_input = {
            'changes': [
                {
                    'path': 'hello.py',
                    'action': 'patch',
                    'content': json.dumps([
                        {'search': 'print("hello")', 'replace': 'print("world")'}
                    ]),
                }
            ],
            'commit_message': 'fix: update hello',
        }

        result = self._call_implement(tool_input)
        assert 'hello.py' in result
        assert target.read_text() == 'print("world")\n'

    def test_changes_as_string_raises(self):
        """changes as string — should raise INVALID_CHANGES_SCHEMA."""
        tool_input = {
            'changes': 'patch hello.py with new content',
            'commit_message': 'fix it',
        }

        with pytest.raises(RuntimeError, match='INVALID_CHANGES_SCHEMA'):
            self._call_implement(tool_input)

    def test_changes_as_list_of_strings_raises(self):
        """changes as list[str] — should raise INVALID_CHANGE_ITEM."""
        tool_input = {
            'changes': ['hello.py', 'world.py'],
            'commit_message': 'fix it',
        }

        with pytest.raises(RuntimeError, match='INVALID_CHANGE_ITEM'):
            self._call_implement(tool_input)

    def test_changes_as_string_retries(self):
        """changes as string on first attempt triggers retry with corrective prompt."""
        from core.tasks import _implement_with_claude

        # First response: changes as string
        bad_response = _make_claude_response({
            'changes': 'wrong format',
            'commit_message': 'fix',
        })

        # Second response: valid
        target_file = os.path.join(self.workdir, 'fix.py')
        os.makedirs(os.path.dirname(target_file) or self.workdir, exist_ok=True)
        with open(target_file, 'w') as f:
            f.write('old code\n')

        good_response = _make_claude_response({
            'changes': [
                {'path': 'fix.py', 'action': 'patch',
                 'content': json.dumps([{'search': 'old code', 'replace': 'new code'}])}
            ],
            'commit_message': 'fix: correct it',
        })

        self.shell.return_value = MagicMock(returncode=0, stdout='', stderr='')

        with patch('anthropic.Anthropic') as mock_cls:
            client = MagicMock()
            mock_cls.return_value = client
            client.messages.create.side_effect = [bad_response, good_response]

            with patch('core.tasks._gather_repo_context', return_value='ctx'):
                result = _implement_with_claude(
                    self.workdir, self.run, self.plan, self.log_fn, self.shell
                )

        assert 'fix.py' in result
        # Verify retry happened (2 API calls)
        assert client.messages.create.call_count == 2

    def test_changes_missing_raises(self):
        """Missing changes key — should raise (existing behavior)."""
        tool_input = {
            'commit_message': 'fix it',
        }

        # The existing code raises RuntimeError for no changes
        with pytest.raises(RuntimeError):
            self._call_implement(tool_input)
