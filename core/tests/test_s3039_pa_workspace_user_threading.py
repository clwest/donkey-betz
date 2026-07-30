"""S3039 D10-follow: PA direct-enforce_real_ai callers must pass user.

Backfills the code-path bug the S3039 D10 audit surfaced: 50.7% of
Rigby's LLMCallLog rows landed with NULL workspace because 4 direct
`self.llm_enforcer.enforce_real_ai` call sites in
`unified_pa_entrypoint.py` bypassed `_pa_wrapped_enforce_real_ai`
(which auto-injects user at line ~886) without threading `user`
themselves. Fix: added `user=self.user` to each site.

This test locks in the invariant so a future edit that adds a new
direct call site without the kwarg fails CI. Grep-based (line-level
whitelist) rather than AST — the pattern is simple + stable.

Invariant: every occurrence of `self.llm_enforcer.enforce_real_ai(`
in `unified_pa_entrypoint.py` must be one of:
  a) inside `_pa_wrapped_enforce_real_ai` (line ~885-910), which
     already `setdefault('user', ...)` at the top;
  b) a docstring reference (backticked or plain-text mention);
  c) a direct call whose kwargs include `user=self.user` within a
     small window after the opening call.
"""
from __future__ import annotations

import re
from pathlib import Path

from django.test import SimpleTestCase


PA_ENTRYPOINT = Path(__file__).resolve().parent.parent / 'services' / 'unified_pa_entrypoint.py'

# Line window after `self.llm_enforcer.enforce_real_ai,` to scan for the
# `user=` kwarg. Real call sites in the file span 6-14 lines; 20 is a
# safe upper bound that won't false-positive on the wrapper (which
# self-references itself inline).
_KWARG_WINDOW_LINES = 20

# Lines inside `_pa_wrapped_enforce_real_ai` where auto-injection lives —
# the wrapper's own `self.llm_enforcer.enforce_real_ai(**enforcer_kwargs)`
# calls at lines 891/909 rely on the setdefault at line ~886, so they
# don't need per-call user= threading.
_WRAPPER_METHOD_NAME = '_pa_wrapped_enforce_real_ai'


class PADirectEnforcerCallsInjectUserTests(SimpleTestCase):
    """Every direct enforce_real_ai call outside the PA wrapper must
    pass user=self.user, or LLMCallLog.workspace lands NULL."""

    def setUp(self):
        self.assertTrue(
            PA_ENTRYPOINT.exists(),
            f'Expected PA entrypoint at {PA_ENTRYPOINT}',
        )
        self.source = PA_ENTRYPOINT.read_text()
        self.lines = self.source.splitlines()

    def _wrapper_line_range(self):
        """Locate `_pa_wrapped_enforce_real_ai` method by finding its
        `async def` line and the next top-level `async def`/`def` at
        the same indentation."""
        start = None
        for i, line in enumerate(self.lines):
            if re.search(rf'\basync\s+def\s+{_WRAPPER_METHOD_NAME}\b', line):
                start = i
                indent = len(line) - len(line.lstrip())
                break
        self.assertIsNotNone(start, f'Could not locate {_WRAPPER_METHOD_NAME}')
        # Find end: next def at same or shallower indent
        end = len(self.lines)
        for j in range(start + 1, len(self.lines)):
            stripped = self.lines[j].lstrip()
            if (stripped.startswith('def ') or stripped.startswith('async def ')):
                if len(self.lines[j]) - len(stripped) <= indent:
                    end = j
                    break
        return start, end

    def test_no_direct_enforcer_call_without_user_kwarg(self):
        wrapper_start, wrapper_end = self._wrapper_line_range()

        # Match only call sites — the `.enforce_real_ai(` or
        # `.enforce_real_ai,` pattern (asyncio.to_thread threads the
        # method as a callable, so the trailing `,` shape is common).
        # Ignore docstring/backticked references.
        pattern = re.compile(r'self\.llm_enforcer\.enforce_real_ai\s*[,(]')

        offenders = []
        for i, line in enumerate(self.lines):
            if not pattern.search(line):
                continue
            # Skip the wrapper's own inline calls — the wrapper injects
            # user via setdefault at its top.
            if wrapper_start <= i < wrapper_end:
                continue
            # Skip docstring / backticked mentions defensively — those
            # would not match `enforce_real_ai\s*[,(]` typically, but
            # belt-and-suspenders in case a future edit inlines a code
            # snippet in a docstring.
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith('```'):
                continue

            # Scan the next window for user= OR **enforcer_kwargs/**kwargs
            # spread (Rigby SIGN ask #2 — accept indirect user-passing shapes
            # in case a future refactor threads args via a dict).
            window = '\n'.join(self.lines[i:i + _KWARG_WINDOW_LINES])
            has_user = re.search(r'\buser\s*=', window) is not None
            has_kwargs_spread = re.search(
                r'\*\*(enforcer_kwargs|kwargs|payload)\b', window,
            ) is not None
            if not has_user and not has_kwargs_spread:
                offenders.append(
                    f'unified_pa_entrypoint.py:{i + 1}: direct '
                    f'`self.llm_enforcer.enforce_real_ai` call missing '
                    f'`user=` kwarg within {_KWARG_WINDOW_LINES} lines. '
                    f'Line: {stripped!r}. Add `user=self.user` or route '
                    f'through _pa_wrapped_enforce_real_ai — otherwise '
                    f'LLMCallLog.workspace lands NULL and PA attribution '
                    f'gap in audit_llmcalllog_workspace_gaps reopens.'
                )

        self.assertFalse(
            offenders,
            f'\n\n{len(offenders)} direct enforce_real_ai call(s) '
            f'missing user threading:\n\n' + '\n\n'.join(offenders),
        )

    def test_wrapper_still_setdefaults_user(self):
        """The centralized user-injection line at the top of
        `_pa_wrapped_enforce_real_ai` must remain intact — it's the
        primary defense for callers that DO route through the wrapper.
        A refactor that drops it would silently re-open the gap for
        wrapper-routed calls even after this fix."""
        wrapper_start, wrapper_end = self._wrapper_line_range()
        wrapper_body = '\n'.join(self.lines[wrapper_start:wrapper_end])
        self.assertRegex(
            wrapper_body,
            r"enforcer_kwargs\.setdefault\(['\"]user['\"]",
            "_pa_wrapped_enforce_real_ai must retain its "
            "`enforcer_kwargs.setdefault('user', ...)` line — that's the "
            "centralized workspace-attribution defense for wrapper-routed "
            "PA LLM calls.",
        )
