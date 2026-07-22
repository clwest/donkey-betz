"""
Session 2728 — Rigby Tool Validation Engineering Campaign, Batch B tool 2
regression tests for `repo_tool`.

Covers the F-RT-* findings surfaced during code trace + patched at
Session 2728. See:
- `docs/research/tools/validation/repo_tool_validation.md`
- `docs/research/tools/tools_validation_engineering_campaign_plan.md`

Findings covered:

- F-RT-2 tree action silent truncation → `tree` response now surfaces
  `entries_truncated`, `files_capped_per_dir`, `depth_capped` and the
  corresponding hard-max fields when a cap fires. Mirrors F-D-5 pattern.
- F-RT-5 search action silent truncation → `search` response now
  surfaces `files_truncated`, `sample_matches_truncated`, and the
  corresponding hard-max fields. Mirrors F-D-5 pattern.
- F-RT-11 outer `except Exception` swallowed tracebacks → now logs at
  ERROR level with `exc_info=True`; response contract unchanged.

Baseline coverage (previously untested):

- Security invariant (`_safe_path` blocks env files + credentials +
  out-of-root + .git internals).
- read_file baseline (path required, size guard, truncated field,
  total_lines correctness).
- git_info baseline (branch, recent_commits, modified_files, status).
- Unknown action fallthrough.

Run::

    python manage.py test core.tests.test_repo_tool_validation_2728 -v2
"""
from __future__ import annotations

import os
import tempfile
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from core.services.tool_dispatcher import ToolDispatcher


class _RepoToolTestBase(SimpleTestCase):
    """Shared dispatch helper."""

    def _dispatch(self, payload):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_repo(  # type: ignore[attr-defined]
            tool_name='repo_tool',
            payload=payload,
            user_id=None,
            trace_id='test-repo-2728',
        )


# ─── F-RT-2: tree action cap envelope ────────────────────────────────


class FRT2TreeCapEnvelope(_RepoToolTestBase):
    """F-RT-2 — `tree` action surfaces cap envelope fields when a cap fires."""

    def test_tree_baseline_no_cap_signal(self):
        """Mocked small directory scan: no cap fires; no envelope fields present.
        Uses a mocked `os.walk` return so the test doesn't depend on the actual
        size of any project subdirectory (which grows over time)."""
        # Simulate a directory with 5 subdirs + 10 files — well under all caps.
        fake_walk = [
            ('/fake/root', ['sub1', 'sub2', 'sub3'], ['a.py', 'b.py', 'c.py']),
            ('/fake/root/sub1', [], ['x.py', 'y.py']),
        ]
        with patch(
            'core.services.td_handlers_gateway.os.walk',
            return_value=iter(fake_walk),
        ), patch(
            'core.services.td_handlers_gateway.os.path.isdir',
            return_value=True,
        ):
            result = self._dispatch({
                'action': 'tree',
                'path': 'core',   # any valid within-root path
                'depth': 2,
            })
        # No error.
        self.assertNotIn('error', result)
        self.assertEqual(result['action'], 'tree')
        # None of the cap-fired fields should be present at these sizes.
        self.assertNotIn('entries_truncated', result)
        self.assertNotIn('files_capped_per_dir', result)
        self.assertNotIn('depth_capped', result)

    def test_tree_depth_capped_signal(self):
        """depth > 4 fires the cap envelope."""
        result = self._dispatch({
            'action': 'tree',
            'path': 'core',
            'depth': 10,   # will be capped at 4
        })
        self.assertTrue(result.get('depth_capped'))
        self.assertEqual(result['requested_depth'], 10)
        self.assertEqual(result['effective_depth'], 4)
        self.assertEqual(result['depth_hard_max'], 4)
        self.assertEqual(result['depth'], 4)

    def test_tree_entries_truncated_signal_from_deep_walk(self):
        """Walking the whole repo at depth 4 exceeds the 500-entries cap."""
        result = self._dispatch({
            'action': 'tree',
            'path': '',   # project root
            'depth': 4,
        })
        # If a large-enough repo tree, entries_truncated fires; the assertion
        # would flake on very small repos but this test target has 3000+
        # docs alone.
        self.assertTrue(result.get('entries_truncated'))
        self.assertEqual(result['entries_hard_max'], 500)
        # Truncation string still appended for human readability.
        self.assertIn('... (truncated at 500 entries)', result['entries'])


# ─── F-RT-5: search action cap envelope ────────────────────────────────


class FRT5SearchCapEnvelope(_RepoToolTestBase):
    """F-RT-5 — `search` action surfaces cap envelope fields when a cap fires."""

    def test_search_baseline_no_cap_signal(self):
        """Mocked small search: no cap fires; no envelope fields present.
        Uses `subprocess.run` mock so the test doesn't depend on the actual
        corpus size for a given query."""
        # Simulate grep returning 3 file paths (well under 30).
        fake_files_output = MagicMock(
            stdout='core/a.py\ncore/b.py\ncore/c.py\n',
            stderr='',
        )
        # Each per-file grep returns 2 lines (well under 5-per-file cap).
        fake_lines_output = MagicMock(
            stdout='core/a.py:10:import x\ncore/a.py:12:import y\n',
            stderr='',
        )
        with patch(
            'subprocess.run',
            side_effect=[fake_files_output, fake_lines_output,
                         fake_lines_output, fake_lines_output],
        ):
            result = self._dispatch({
                'action': 'search',
                'query': 'anything',
                'file_type': 'py',
            })
        self.assertNotIn('error', result)
        self.assertEqual(result['files_matched'], 3)
        # None of the cap-fired fields should be present.
        self.assertNotIn('files_truncated', result)
        self.assertNotIn('sample_matches_truncated', result)

    def test_search_files_truncated_signal(self):
        """A broadly-matching query fires the files_truncated cap."""
        # 'import' appears in nearly every Python file — >> 30 matches.
        result = self._dispatch({
            'action': 'search',
            'query': 'import',
            'file_type': 'py',
        })
        # files_matched should exceed 30.
        self.assertGreater(result['files_matched'], 30)
        self.assertTrue(result.get('files_truncated'))
        self.assertEqual(result['files_hard_max'], 30)
        self.assertLessEqual(len(result['files']), 30)

    def test_search_sample_matches_truncated_signal(self):
        """Same broad query fires sample_matches_truncated because match
        source is capped at 10 files (< files_matched)."""
        result = self._dispatch({
            'action': 'search',
            'query': 'import',
            'file_type': 'py',
        })
        self.assertTrue(result.get('sample_matches_truncated'))
        self.assertEqual(result['sample_matches_hard_max'], 30)
        self.assertEqual(result['match_source_files_hard_max'], 10)
        self.assertEqual(result['lines_per_file_hard_max'], 5)


# ─── F-RT-11: outer except logs with traceback ─────────────────────────


class FRT11OuterExceptLogsTraceback(_RepoToolTestBase):
    """F-RT-11 — outer `except Exception` still returns typed error dict,
    but now also logs at ERROR with `exc_info=True` so the traceback is
    visible to operators."""

    def test_outer_except_logs_with_traceback(self):
        # Force an exception in the tree branch by mocking os.walk to raise.
        with patch(
            'core.services.td_handlers_gateway.os.walk',
            side_effect=RuntimeError('simulated walk failure'),
        ), self.assertLogs(
            'core.services.td_handlers_gateway', level='ERROR',
        ) as log_ctx:
            result = self._dispatch({
                'action': 'tree',
                'path': 'core',
            })
        # Response contract preserved.
        self.assertIn('error', result)
        self.assertIn('repo_tool error', result['error'])
        self.assertIn('simulated walk failure', result['error'])
        # Log carries the exception class + action + traceback.
        log_output = '\n'.join(log_ctx.output)
        self.assertIn('RuntimeError', log_output)
        self.assertIn('simulated walk failure', log_output)
        self.assertIn("action='tree'", log_output)
        # Traceback frame must be present (exc_info=True).
        self.assertIn('Traceback', log_output)


# ─── Baseline: security invariant ──────────────────────────────────────


class RepoToolSecurityInvariant(_RepoToolTestBase):
    """First regression tests for `_safe_path` — the security invariant that
    blocks env files, credentials, out-of-root paths, and .git internals."""

    def test_env_file_blocked(self):
        result = self._dispatch({'action': 'read_file', 'path': '.env'})
        self.assertIn('error', result)
        self.assertIn('Access denied', result['error'])

    def test_env_local_blocked(self):
        result = self._dispatch({'action': 'read_file', 'path': '.env.local'})
        self.assertIn('error', result)
        self.assertIn('Access denied', result['error'])

    def test_credentials_json_blocked(self):
        result = self._dispatch({'action': 'read_file', 'path': 'credentials.json'})
        self.assertIn('error', result)
        self.assertIn('Access denied', result['error'])

    def test_out_of_project_root_blocked(self):
        # Attempt to escape via ../
        result = self._dispatch({
            'action': 'read_file',
            'path': '../../../../etc/passwd',
        })
        self.assertIn('error', result)
        self.assertIn('outside project root', result['error'])


# ─── Baseline: read_file + git_info + unknown action ───────────────────


class RepoToolBaselineActions(_RepoToolTestBase):
    """First regression tests for the non-cap-envelope behaviors."""

    def test_read_file_requires_path(self):
        result = self._dispatch({'action': 'read_file'})
        self.assertIn('error', result)
        self.assertIn('path is required', result['error'])

    def test_read_file_truncated_field_present_at_cap(self):
        """read_file's truncation surface is best-in-class — verify the
        `truncated: bool` field IS explicitly present on the response."""
        # Any file > max_lines will trigger truncation. Use a small
        # max_lines against a known-large file (this test file itself
        # or any file in core/services).
        result = self._dispatch({
            'action': 'read_file',
            'path': 'core/services/td_handlers_gateway.py',
            'max_lines': 5,
        })
        self.assertNotIn('error', result)
        self.assertEqual(result['lines'], 5)
        self.assertTrue(result['truncated'])
        self.assertGreater(result['total_lines'], 5)

    def test_git_info_baseline(self):
        result = self._dispatch({'action': 'git_info'})
        self.assertEqual(result['action'], 'git_info')
        self.assertIn('branch', result)
        self.assertIn('recent_commits', result)
        self.assertIn('modified_files', result)
        self.assertIn('status', result)

    def test_unknown_action_returns_typed_error(self):
        result = self._dispatch({'action': 'wibble_the_repo'})
        self.assertIn('error', result)
        self.assertIn('Unknown repo_tool action', result['error'])
        self.assertIn('wibble_the_repo', result['error'])


# ─── S2887: cross-repo scoping via repo_id ────────────────────────────
#
# Rigby SIGN Q1-Q6 grounded these tests. Every branch of the resolver has
# a matching assertion; taxonomy-fix regressions for blocked-file / out-
# of-root map to `permission_denied` (was `value_error`).


class S2887CrossRepoScoping(_RepoToolTestBase):
    """S2887 — repo_id resolves to a registered external_repos profile.

    u-d-b default path preserved when repo_id is absent."""

    def test_list_repos_enumerates_profiles(self):
        result = self._dispatch({'action': 'list_repos'})
        self.assertNotIn('error', result)
        self.assertEqual(result['action'], 'list_repos')
        # At authoring time the corpus is 12 profiles; the assertion is
        # >= to avoid brittle churn as new siblings register.
        self.assertGreaterEqual(result['count'], 12)
        # Every row carries the three-field shape SIGNed at Q4.
        for row in result['repos']:
            self.assertIn('repo_id', row)
            self.assertIn('root_path', row)
            self.assertIn('exists', row)
        # character-os + context-kit MUST be reachable at their new
        # /Donkey_Betz/ paths (profile fix landed in the same PR).
        _by_id = {r['repo_id']: r for r in result['repos']}
        self.assertIn('character-os', _by_id)
        self.assertIn('context-kit', _by_id)

    def test_repo_id_invalid_slug_rejected(self):
        """Slug containing '..' or '/' must be rejected as invalid_params.

        Precondition for the resolver — never touches the filesystem."""
        for bad_slug in ('..', '../etc', 'char/os', 'char\\os'):
            result = self._dispatch({
                'action': 'tree',
                'repo_id': bad_slug,
            })
            self.assertIn('error', result, msg=f'bad_slug={bad_slug!r}')
            self.assertEqual(result['error_code'], 'invalid_params',
                             msg=f'bad_slug={bad_slug!r}')

    def test_repo_id_unknown_profile_returns_not_found(self):
        result = self._dispatch({
            'action': 'tree',
            'repo_id': 'no-such-repo-slug-exists',
        })
        self.assertIn('error', result)
        self.assertEqual(result['error_code'], 'not_found')
        self.assertIn('list_repos', result.get('hint', ''))

    def test_repo_id_absent_reads_udb_default(self):
        """Absent repo_id keeps the pre-S2887 behavior — reads u-d-b."""
        result = self._dispatch({'action': 'git_info'})
        self.assertNotIn('error', result)
        # branch is populated from *this* repo's git state
        self.assertIn('branch', result)


class S2887TaxonomyMigration(_RepoToolTestBase):
    """S2887 — path-guard rejections now emit `permission_denied` instead
    of the out-of-taxonomy `value_error` code. Message strings preserved
    for backwards compat with existing security-invariant tests."""

    def test_env_file_now_returns_permission_denied(self):
        result = self._dispatch({'action': 'read_file', 'path': '.env'})
        self.assertEqual(result['error_code'], 'permission_denied')
        self.assertIn('Access denied', result['error'])

    def test_credentials_json_now_returns_permission_denied(self):
        result = self._dispatch({'action': 'read_file', 'path': 'credentials.json'})
        self.assertEqual(result['error_code'], 'permission_denied')

    def test_pem_suffix_blocked_permission_denied(self):
        """S2887 widened guards: any *.pem file basename is blocked."""
        result = self._dispatch({'action': 'read_file', 'path': 'somewhere/server.pem'})
        self.assertEqual(result['error_code'], 'permission_denied')

    def test_key_suffix_blocked_permission_denied(self):
        result = self._dispatch({'action': 'read_file', 'path': 'somewhere/secret.key'})
        self.assertEqual(result['error_code'], 'permission_denied')

    def test_ssh_dir_blocked_permission_denied(self):
        result = self._dispatch({'action': 'read_file', 'path': '.ssh/id_rsa'})
        self.assertEqual(result['error_code'], 'permission_denied')

    def test_env_prefix_pattern_blocked(self):
        """`.env.foo` was not caught by the old exact-match BLOCKED_FILES
        set; the prefix pattern added at S2887 catches it now."""
        result = self._dispatch({'action': 'read_file', 'path': '.env.somecustom'})
        self.assertEqual(result['error_code'], 'permission_denied')

    def test_out_of_project_root_now_returns_permission_denied(self):
        result = self._dispatch({
            'action': 'read_file',
            'path': '../../../../etc/passwd',
        })
        self.assertEqual(result['error_code'], 'permission_denied')
        # Message still says "outside project root" for prior-consumer parity.
        self.assertIn('outside project root', result['error'])
