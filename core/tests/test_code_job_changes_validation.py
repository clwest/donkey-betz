"""
Tests for CodeJob implement pipeline — changes schema validation & guardrails.

Covers:
- IMPLEMENT_FAILED: 'str' object has no attribute 'get' (PR #1548)
- CODEJOB_ANCHOR_NOT_FOUND: all edits fail to match search text
- CODEJOB_FILE_TOO_LARGE: target file exceeds _MAX_EDIT_FILE_SIZE
"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from core.tasks import (
    CodeJobAnchorNotFoundError,
    CodeJobError,
    CodeJobFileTooLargeError,
    _MAX_EDIT_FILE_SIZE,
)


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


def _make_claude_response(tool_input, tool_use_id='toolu_test_001'):
    """Build a mock Anthropic response with a tool_use block."""
    block = MagicMock()
    block.type = 'tool_use'
    block.name = 'apply_file_changes'
    block.id = tool_use_id
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
        }, tool_use_id='toolu_bad_001')

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
        }, tool_use_id='toolu_good_002')

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
        # Verify retry messages include tool_result block (Anthropic protocol)
        retry_call_kwargs = client.messages.create.call_args_list[1]
        retry_messages = retry_call_kwargs.kwargs.get('messages', retry_call_kwargs[1].get('messages', []))
        # The user retry message should contain a tool_result block
        user_retry_msg = [m for m in retry_messages if m.get('role') == 'user' and isinstance(m.get('content'), list)]
        assert len(user_retry_msg) >= 1, 'Retry should include structured user message with tool_result'
        tool_results = [
            block for msg in user_retry_msg
            for block in msg['content']
            if isinstance(block, dict) and block.get('type') == 'tool_result'
        ]
        assert len(tool_results) >= 1, 'Retry user message must include tool_result block'
        assert tool_results[0]['tool_use_id'] == 'toolu_bad_001'

    def test_changes_missing_raises(self):
        """Missing changes key — should raise (existing behavior)."""
        tool_input = {
            'commit_message': 'fix it',
        }

        # The existing code raises RuntimeError for no changes
        with pytest.raises(RuntimeError):
            self._call_implement(tool_input)


class TestAnchorNotFound:
    """Test CODEJOB_ANCHOR_NOT_FOUND guardrail."""

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
        self.shell.return_value = MagicMock(returncode=0, stdout='', stderr='')

    def _call_implement(self, tool_input):
        from core.tasks import _implement_with_claude

        mock_response = _make_claude_response(tool_input)

        with patch('anthropic.Anthropic') as mock_cls:
            client = MagicMock()
            mock_cls.return_value = client
            client.messages.create.return_value = mock_response

            with patch('core.tasks._gather_repo_context', return_value='ctx'):
                return _implement_with_claude(
                    self.workdir, self.run, self.plan, self.log_fn, self.shell
                )

    def test_all_anchors_missing_raises(self, tmp_path):
        """When ALL edits for a file have missing anchors, raise CODEJOB_ANCHOR_NOT_FOUND."""
        target = tmp_path / 'app.py'
        target.write_text('def hello():\n    return 1\n')
        self.workdir = str(tmp_path)

        tool_input = {
            'changes': [{
                'path': 'app.py',
                'action': 'patch',
                'content': json.dumps([
                    {'search': 'THIS DOES NOT EXIST', 'replace': 'new code'},
                    {'search': 'NEITHER DOES THIS', 'replace': 'other code'},
                ]),
            }],
            'commit_message': 'fix: update',
        }

        with pytest.raises(CodeJobAnchorNotFoundError, match='CODEJOB_ANCHOR_NOT_FOUND'):
            self._call_implement(tool_input)

    def test_anchor_error_contains_context(self, tmp_path):
        """Error context includes path and failed edit details."""
        target = tmp_path / 'service.py'
        target.write_text('class Service:\n    pass\n')
        self.workdir = str(tmp_path)

        tool_input = {
            'changes': [{
                'path': 'service.py',
                'action': 'patch',
                'content': json.dumps([
                    {'search': 'def nonexistent():', 'replace': 'def fixed():'},
                ]),
            }],
            'commit_message': 'fix: service',
        }

        with pytest.raises(CodeJobAnchorNotFoundError) as exc_info:
            self._call_implement(tool_input)

        assert exc_info.value.context['path'] == 'service.py'
        assert len(exc_info.value.context['failed_edits']) == 1

    def test_partial_anchor_failure_raises(self, tmp_path):
        """When ANY edit has a missing anchor, raise even if others match."""
        target = tmp_path / 'mixed.py'
        original = 'line_one = 1\nline_two = 2\n'
        target.write_text(original)
        self.workdir = str(tmp_path)

        tool_input = {
            'changes': [{
                'path': 'mixed.py',
                'action': 'patch',
                'content': json.dumps([
                    {'search': 'line_one = 1', 'replace': 'line_one = 99'},
                    {'search': 'MISSING ANCHOR', 'replace': 'nope'},
                ]),
            }],
            'commit_message': 'fix: partial',
        }

        with pytest.raises(CodeJobAnchorNotFoundError) as exc_info:
            self._call_implement(tool_input)

        # Context should show 1 failed, 1 succeeded
        assert exc_info.value.context['edits_succeeded'] == 1
        assert len(exc_info.value.context['failed_edits']) == 1
        # File must NOT be modified (no partial writes)
        assert target.read_text() == original

    def test_file_not_modified_on_anchor_failure(self, tmp_path):
        """File contents must NOT change when all anchors fail."""
        target = tmp_path / 'safe.py'
        original = 'keep_me = True\n'
        target.write_text(original)
        self.workdir = str(tmp_path)

        tool_input = {
            'changes': [{
                'path': 'safe.py',
                'action': 'patch',
                'content': json.dumps([
                    {'search': 'WRONG ANCHOR', 'replace': 'keep_me = False'},
                ]),
            }],
            'commit_message': 'fix: safe',
        }

        with pytest.raises(CodeJobAnchorNotFoundError):
            self._call_implement(tool_input)

        # File must be untouched
        assert target.read_text() == original


class TestFileTooLarge:
    """Test CODEJOB_FILE_TOO_LARGE guardrail."""

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
        self.shell.return_value = MagicMock(returncode=0, stdout='', stderr='')

    def _call_implement(self, tool_input):
        from core.tasks import _implement_with_claude

        mock_response = _make_claude_response(tool_input)

        with patch('anthropic.Anthropic') as mock_cls:
            client = MagicMock()
            mock_cls.return_value = client
            client.messages.create.return_value = mock_response

            with patch('core.tasks._gather_repo_context', return_value='ctx'):
                return _implement_with_claude(
                    self.workdir, self.run, self.plan, self.log_fn, self.shell
                )

    def test_oversized_patch_target_raises(self, tmp_path):
        """Patch target exceeding _MAX_EDIT_FILE_SIZE raises CODEJOB_FILE_TOO_LARGE."""
        target = tmp_path / 'big.py'
        target.write_text('x' * (_MAX_EDIT_FILE_SIZE + 1))
        self.workdir = str(tmp_path)

        tool_input = {
            'changes': [{
                'path': 'big.py',
                'action': 'patch',
                'content': json.dumps([
                    {'search': 'x', 'replace': 'y'},
                ]),
            }],
            'commit_message': 'fix: big file',
        }

        with pytest.raises(CodeJobFileTooLargeError, match='CODEJOB_FILE_TOO_LARGE'):
            self._call_implement(tool_input)

    def test_just_under_limit_succeeds(self, tmp_path):
        """File exactly at the limit should NOT raise."""
        content = 'a' * (_MAX_EDIT_FILE_SIZE - 1) + '\n'  # exactly at limit
        target = tmp_path / 'borderline.py'
        target.write_text(content)
        self.workdir = str(tmp_path)

        search_text = content[:50]
        replace_text = 'b' * 50

        tool_input = {
            'changes': [{
                'path': 'borderline.py',
                'action': 'patch',
                'content': json.dumps([
                    {'search': search_text, 'replace': replace_text},
                ]),
            }],
            'commit_message': 'fix: borderline',
        }

        result = self._call_implement(tool_input)
        assert 'borderline.py' in result

    def test_just_over_limit_raises(self, tmp_path):
        """File 1 byte over the limit should raise."""
        content = 'a' * (_MAX_EDIT_FILE_SIZE + 1)
        target = tmp_path / 'over.py'
        target.write_text(content)
        self.workdir = str(tmp_path)

        tool_input = {
            'changes': [{
                'path': 'over.py',
                'action': 'patch',
                'content': json.dumps([
                    {'search': 'a', 'replace': 'b'},
                ]),
            }],
            'commit_message': 'fix: over',
        }

        with pytest.raises(CodeJobFileTooLargeError) as exc_info:
            self._call_implement(tool_input)

        assert exc_info.value.context['path'] == 'over.py'
        assert exc_info.value.context['size'] == _MAX_EDIT_FILE_SIZE + 1
        assert exc_info.value.context['limit'] == _MAX_EDIT_FILE_SIZE

    def test_oversized_create_raises(self, tmp_path):
        """Create/overwrite action with oversized content raises CODEJOB_FILE_TOO_LARGE."""
        self.workdir = str(tmp_path)

        tool_input = {
            'changes': [{
                'path': 'new_big.py',
                'action': 'create',
                'content': 'x' * 600_000,  # exceeds _MAX_FILE_SIZE (500KB)
            }],
            'commit_message': 'fix: create big',
        }

        with pytest.raises(CodeJobFileTooLargeError, match='CODEJOB_FILE_TOO_LARGE'):
            self._call_implement(tool_input)

    def test_file_not_modified_on_size_error(self, tmp_path):
        """Original file must not be modified when size check fails."""
        original = 'z' * (_MAX_EDIT_FILE_SIZE + 100)
        target = tmp_path / 'untouched.py'
        target.write_text(original)
        self.workdir = str(tmp_path)

        tool_input = {
            'changes': [{
                'path': 'untouched.py',
                'action': 'patch',
                'content': json.dumps([
                    {'search': 'z', 'replace': 'MODIFIED'},
                ]),
            }],
            'commit_message': 'fix: nope',
        }

        with pytest.raises(CodeJobFileTooLargeError):
            self._call_implement(tool_input)

        assert target.read_text() == original


class TestCodeJobErrorHierarchy:
    """Test typed exception structure."""

    def test_base_class_inheritance(self):
        assert issubclass(CodeJobAnchorNotFoundError, CodeJobError)
        assert issubclass(CodeJobFileTooLargeError, CodeJobError)
        assert issubclass(CodeJobError, RuntimeError)

    def test_error_code_in_message(self):
        err = CodeJobAnchorNotFoundError('test msg', path='foo.py')
        assert 'CODEJOB_ANCHOR_NOT_FOUND' in str(err)
        assert err.code == 'CODEJOB_ANCHOR_NOT_FOUND'
        assert err.context == {'path': 'foo.py'}

    def test_file_too_large_code(self):
        err = CodeJobFileTooLargeError('big file', size=999)
        assert err.code == 'CODEJOB_FILE_TOO_LARGE'
        assert err.context['size'] == 999
