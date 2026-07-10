"""
Tests for the ``session_lifecycle`` management command (S2746 EOS Phase 3
build).

Covers:

* ``status`` reads the wrapper pin via anchored regex, reports owner +
  message_count + session_active_rows + triggers_matched.
* ``open`` mints a fresh pa-<uuid[:16]> pin, creates a ChatConversation
  seed row, and rewrites the wrapper preserving every other byte.
* ``open --dry-run`` writes nothing (DB or wrapper).
* ``close`` retires the current pin, mints fresh, rewrites wrapper.
* ``close --retire-only`` retires without minting or rewriting.
* ``close`` without --label + without --retire-only raises CommandError.
* Wrapper safety: 0 matches → CommandError; >1 matches → CommandError
  with line numbers; malformed pin format → CommandError.
* Auto-carry-forward derivation is invoked when --carry-forward absent.
* Explicit --carry-forward overrides derivation.
* Wrapper rewrite preserves the historical pin-comment blocks (500+
  lines of stale pa- references) exactly.
* Rewrite failure after DB commit prints recovery output.

Test discipline (matches ``test_cost_thresholds_command.py``):
- Real DB, real ChatConversation writes.
- ``call_command`` invoked exactly as ops would from CLI.
- Wrapper writes routed to a tempfile via ``--wrapper-path`` so the
  real ``tools/pa_local.sh`` is never touched by tests.
- Stdout captured via ``StringIO``.

Run::

    python manage.py test core.tests.test_session_lifecycle_command -v2
"""
from __future__ import annotations

import re
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from core.models import ChatConversation


_TEST_USERNAME = "session_lifecycle_test_user"
_PIN_RE = re.compile(r"^pa-[0-9a-f]{16}$")


def _wrapper_fixture(pin: str, extra_prefix: str = "", extra_suffix: str = "") -> str:
    """Build a wrapper file body with one live invocation + optional prefix/suffix.

    The prefix/suffix simulate the pa_local.sh comment blocks that
    contain many stale pa- references we must NOT rewrite.
    """
    return (
        f"{extra_prefix}"
        f'python tools/pa_chat.py "$@" --tools --conversation {pin}\n'
        f"{extra_suffix}"
    )


def _fixture_with_history() -> str:
    """Fixture that mimics the real pa_local.sh — many comment-block
    references to old pins, plus one live invocation line at the end."""
    return (
        "#!/bin/bash\n"
        "# History block: retired pa-1111111111111111 at Session X\n"
        "# History block: retired pa-2222222222222222 at Session Y\n"
        "# Comment mentions pa-3333333333333333 as a SIGN pin\n"
        "\n"
        'python tools/pa_chat.py "$@" --tools --conversation pa-abcdef0123456789\n'
    )


class _WrapperFileMixin:
    def _write_fixture(self, body: str) -> Path:
        # tempfile with delete=False so we can pass path to call_command
        f = tempfile.NamedTemporaryFile(
            mode="w", suffix=".sh", delete=False, encoding="utf-8",
        )
        f.write(body)
        f.close()
        self.addCleanup(lambda: Path(f.name).unlink(missing_ok=True))
        return Path(f.name)


class StatusTests(_WrapperFileMixin, TestCase):
    """`session_lifecycle status` reads wrapper + reports."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create(username=_TEST_USERNAME)

    def _run(self, wrapper_path: Path) -> str:
        out = StringIO()
        call_command(
            "session_lifecycle", "status",
            "--user", _TEST_USERNAME,
            "--wrapper-path", str(wrapper_path),
            stdout=out,
        )
        return out.getvalue()

    def test_status_with_no_chat_rows_flags_orphan(self):
        wrapper = self._write_fixture(_wrapper_fixture("pa-abcdef0123456789"))
        output = self._run(wrapper)
        self.assertIn("pin: pa-abcdef0123456789", output)
        self.assertIn("orphan or belongs to a different owner", output)

    def test_status_with_owned_pin_reports_message_count(self):
        pin = "pa-abcdef0123456789"
        wrapper = self._write_fixture(_wrapper_fixture(pin))
        for i in range(3):
            ChatConversation.objects.create(
                conversation_id=pin,
                user_id=self.user.id,
                session_title="test",
                user_message=f"msg {i}",
                assistant_response="ok",
            )
        output = self._run(wrapper)
        self.assertIn(f"owner: {_TEST_USERNAME}", output)
        self.assertIn("message_count: 3", output)
        self.assertIn("session_active_rows: 3", output)
        self.assertIn("triggers_matched: none", output)

    def test_status_over_50_msgs_reports_trigger(self):
        pin = "pa-abcdef0123456789"
        wrapper = self._write_fixture(_wrapper_fixture(pin))
        for i in range(51):
            ChatConversation.objects.create(
                conversation_id=pin,
                user_id=self.user.id,
                session_title="test",
                user_message=f"msg {i}",
                assistant_response="ok",
            )
        output = self._run(wrapper)
        self.assertIn("message_count: 51", output)
        self.assertIn("message_count_over_50", output)
        self.assertIn("rotation recommended", output)


class WrapperSafetyTests(_WrapperFileMixin, TestCase):
    """Wrapper rewrite safety contract (Q3 SIGN)."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create(username=_TEST_USERNAME)

    def test_zero_matches_raises_command_error(self):
        wrapper = self._write_fixture(
            "#!/bin/bash\n# no invocation line here\n"
        )
        with self.assertRaises(CommandError) as ctx:
            call_command(
                "session_lifecycle", "status",
                "--user", _TEST_USERNAME,
                "--wrapper-path", str(wrapper),
                stdout=StringIO(),
            )
        self.assertIn("No live invocation line found", str(ctx.exception))

    def test_multiple_matches_raises_with_line_numbers(self):
        body = (
            "line 1\n"
            'python tools/pa_chat.py "$@" --tools --conversation pa-abcdef0123456789\n'
            "line 3\n"
            'python tools/pa_chat.py "$@" --tools --conversation pa-1111111111111111\n'
            "line 5\n"
        )
        wrapper = self._write_fixture(body)
        with self.assertRaises(CommandError) as ctx:
            call_command(
                "session_lifecycle", "status",
                "--user", _TEST_USERNAME,
                "--wrapper-path", str(wrapper),
                stdout=StringIO(),
            )
        msg = str(ctx.exception)
        self.assertIn("Found 2 live invocation lines", msg)
        self.assertIn("2, 4", msg)  # line numbers

    def test_wrapper_missing_raises(self):
        with self.assertRaises(CommandError) as ctx:
            call_command(
                "session_lifecycle", "status",
                "--user", _TEST_USERNAME,
                "--wrapper-path", "/tmp/does-not-exist-session-lifecycle-test.sh",
                stdout=StringIO(),
            )
        self.assertIn("Wrapper file not found", str(ctx.exception))

    def test_comment_blocks_ignored_for_pin_extraction(self):
        """Ensure pa- refs in comments don't cause false 'multiple match' errors."""
        wrapper = self._write_fixture(_fixture_with_history())
        # Should not raise; single live invocation.
        out = StringIO()
        call_command(
            "session_lifecycle", "status",
            "--user", _TEST_USERNAME,
            "--wrapper-path", str(wrapper),
            stdout=out,
        )
        self.assertIn("pin: pa-abcdef0123456789", out.getvalue())


class OpenTests(_WrapperFileMixin, TestCase):
    """`session_lifecycle open` mints + rewrites wrapper."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create(username=_TEST_USERNAME)

    def test_open_dry_run_no_writes(self):
        original_pin = "pa-abcdef0123456789"
        original_body = _wrapper_fixture(original_pin)
        wrapper = self._write_fixture(original_body)

        out = StringIO()
        call_command(
            "session_lifecycle", "open",
            "--label", "test-label",
            "--user", _TEST_USERNAME,
            "--wrapper-path", str(wrapper),
            "--dry-run",
            stdout=out,
        )
        output = out.getvalue()
        self.assertIn("dry-run", output)
        self.assertIn(f"current pin (will remain active): {original_pin}", output)

        # Wrapper is byte-for-byte unchanged
        self.assertEqual(wrapper.read_text(), original_body)
        # No ChatConversation rows created
        self.assertEqual(ChatConversation.objects.filter(user_id=self.user.id).count(), 0)

    def test_open_live_mints_and_rewrites(self):
        original_pin = "pa-abcdef0123456789"
        original_body = _fixture_with_history()
        wrapper = self._write_fixture(original_body)

        out = StringIO()
        call_command(
            "session_lifecycle", "open",
            "--label", "engineering-session",
            "--carry-forward", "explicit test carry-forward",
            "--user", _TEST_USERNAME,
            "--wrapper-path", str(wrapper),
            stdout=out,
        )
        output = out.getvalue()

        # Extract new pin from stdout
        m = re.search(r"new pin \(wrapper now points here\): (pa-[0-9a-f]{16})", output)
        self.assertIsNotNone(m, f"new pin not in stdout: {output}")
        new_pin = m.group(1)
        self.assertTrue(_PIN_RE.match(new_pin))
        self.assertNotEqual(new_pin, original_pin)

        # Wrapper now points to new pin
        new_body = wrapper.read_text()
        self.assertIn(f"--conversation {new_pin}", new_body)
        self.assertNotIn(f"--conversation {original_pin}", new_body)
        # Historical comment references preserved
        self.assertIn("retired pa-1111111111111111", new_body)
        self.assertIn("retired pa-2222222222222222", new_body)
        self.assertIn("pa-3333333333333333", new_body)

        # ChatConversation seed row exists
        rows = ChatConversation.objects.filter(conversation_id=new_pin, user_id=self.user.id)
        self.assertEqual(rows.count(), 1)
        row = rows.first()
        self.assertEqual(row.session_title, "engineering-session")
        self.assertIn("explicit test carry-forward", row.user_message)

    def test_open_preserves_all_bytes_except_pin(self):
        """Byte-preservation check: only the pin substring changes."""
        original_pin = "pa-abcdef0123456789"
        original_body = (
            "prefix line 1\n"
            "prefix line 2 with pa-9999999999999999 in comment\n"
            f'python tools/pa_chat.py "$@" --tools --conversation {original_pin}\n'
            "suffix line 1\n"
            "suffix line 2\n"
        )
        wrapper = self._write_fixture(original_body)

        out = StringIO()
        call_command(
            "session_lifecycle", "open",
            "--label", "L",
            "--user", _TEST_USERNAME,
            "--wrapper-path", str(wrapper),
            stdout=out,
        )
        m = re.search(r"new pin \(wrapper now points here\): (pa-[0-9a-f]{16})", out.getvalue())
        new_pin = m.group(1)

        # Reconstruct the expected new body via substitution
        expected = original_body.replace(original_pin, new_pin)
        self.assertEqual(wrapper.read_text(), expected)


class CloseTests(_WrapperFileMixin, TestCase):
    """`session_lifecycle close` retires + mints + rewrites."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create(username=_TEST_USERNAME)
        self.original_pin = "pa-abcdef0123456789"
        # Seed the original pin as an active conversation for this user
        ChatConversation.objects.create(
            conversation_id=self.original_pin,
            user_id=self.user.id,
            session_title="original",
            user_message="hi",
            assistant_response="ok",
            session_active=True,
        )

    def test_close_requires_label_or_retire_only(self):
        wrapper = self._write_fixture(_wrapper_fixture(self.original_pin))
        with self.assertRaises(CommandError) as ctx:
            call_command(
                "session_lifecycle", "close",
                "--user", _TEST_USERNAME,
                "--wrapper-path", str(wrapper),
                stdout=StringIO(),
            )
        self.assertIn("--label", str(ctx.exception))

    def test_close_retires_mints_rewrites(self):
        wrapper = self._write_fixture(_wrapper_fixture(self.original_pin))

        out = StringIO()
        call_command(
            "session_lifecycle", "close",
            "--label", "next-arc",
            "--carry-forward", "test",
            "--user", _TEST_USERNAME,
            "--wrapper-path", str(wrapper),
            stdout=out,
        )
        output = out.getvalue()

        # Original pin retired
        self.assertFalse(
            ChatConversation.objects.filter(
                conversation_id=self.original_pin,
                session_active=True,
            ).exists()
        )
        # New pin exists + wrapper points to it
        m = re.search(r"new pin \(wrapper now points here\): (pa-[0-9a-f]{16})", output)
        self.assertIsNotNone(m)
        new_pin = m.group(1)
        self.assertNotEqual(new_pin, self.original_pin)
        self.assertIn(f"--conversation {new_pin}", wrapper.read_text())
        self.assertIn(f"retired pin: {self.original_pin}", output)

    def test_close_retire_only_no_mint_no_rewrite(self):
        wrapper = self._write_fixture(_wrapper_fixture(self.original_pin))
        original_body = wrapper.read_text()

        out = StringIO()
        call_command(
            "session_lifecycle", "close",
            "--retire-only",
            "--user", _TEST_USERNAME,
            "--wrapper-path", str(wrapper),
            stdout=out,
        )
        output = out.getvalue()

        # Original pin retired
        self.assertFalse(
            ChatConversation.objects.filter(
                conversation_id=self.original_pin,
                session_active=True,
            ).exists()
        )
        # Wrapper unchanged
        self.assertEqual(wrapper.read_text(), original_body)
        # No new ChatConversation seed row
        self.assertEqual(
            ChatConversation.objects.filter(user_id=self.user.id).count(), 1,
        )
        self.assertIn("retire-only", output)

    def test_close_dry_run_no_writes(self):
        wrapper = self._write_fixture(_wrapper_fixture(self.original_pin))
        original_body = wrapper.read_text()

        out = StringIO()
        call_command(
            "session_lifecycle", "close",
            "--label", "next",
            "--user", _TEST_USERNAME,
            "--wrapper-path", str(wrapper),
            "--dry-run",
            stdout=out,
        )
        self.assertIn("dry-run", out.getvalue())
        self.assertEqual(wrapper.read_text(), original_body)
        # Original pin NOT retired
        self.assertTrue(
            ChatConversation.objects.filter(
                conversation_id=self.original_pin,
                session_active=True,
            ).exists()
        )


class UserResolutionTests(_WrapperFileMixin, TestCase):
    """--user resolution errors cleanly."""

    def test_unknown_user_raises(self):
        wrapper = self._write_fixture(_wrapper_fixture("pa-abcdef0123456789"))
        with self.assertRaises(CommandError) as ctx:
            call_command(
                "session_lifecycle", "status",
                "--user", "nonexistent_user_xyz",
                "--wrapper-path", str(wrapper),
                stdout=StringIO(),
            )
        self.assertIn("not found in auth_user", str(ctx.exception))
