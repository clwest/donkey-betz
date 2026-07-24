"""Tests for Ledger #16 (S2941) — twin-mirror enforcement at session close.

Covers the two layers:

1. ``core.services.twin_mirror_enforcement.assert_twin_mirror_at_close``
   pure-Python assertions (refuse path, allow path, mutual exclusion,
   malformed UUID, missing row, diagnostic flag, wrong deliverable_type).

2. ``session_lifecycle close`` CLI integration — the refuse path must
   raise ``CommandError`` **before** any DB write (no retire, no mint).

Run::

    python manage.py test core.tests.test_session_lifecycle_twin_mirror -v2
"""
from __future__ import annotations

import re
import tempfile
import uuid
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from core.models import ChatConversation
from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace
from core.services.twin_mirror_enforcement import (
    TwinMirrorEnforcementError,
    assert_twin_mirror_at_close,
)


_TEST_USERNAME = "twin_mirror_test_user"


def _wrapper_body(pin: str) -> str:
    return f'python tools/pa_chat.py "$@" --tools --conversation {pin}\n'


class _WrapperFileMixin:
    def _write_fixture(self, body: str) -> Path:
        f = tempfile.NamedTemporaryFile(
            mode="w", suffix=".sh", delete=False, encoding="utf-8",
        )
        f.write(body)
        f.close()
        self.addCleanup(lambda: Path(f.name).unlink(missing_ok=True))
        return Path(f.name)


class TwinMirrorServiceTests(TestCase):
    """Direct tests on ``assert_twin_mirror_at_close`` — no CLI, no wrapper."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(
            username=f"twin-svc-{uuid.uuid4().hex[:8]}",
            email="twin@example.com",
            password="x",
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name="Twin Mirror Test Workspace",
        )

    def _make_deliverable(self, **overrides):
        defaults = dict(
            title="Twin-mirror test row",
            content="# Body\n\nSubstantial body." * 10,
            agent_name="Rigby",
            category="PA Created",
            deliverable_type="document",
            status="ready",
            user=self.user,
            workspace=self.workspace,
        )
        defaults.update(overrides)
        return Deliverable.objects.create(**defaults)

    def test_refuses_when_no_flags_provided(self):
        with self.assertRaises(TwinMirrorEnforcementError) as ctx:
            assert_twin_mirror_at_close(
                content_mirror_id=None,
                ratification_envelope_id=None,
                allow_no_mirror=False,
            )
        self.assertIn("Ledger #16", str(ctx.exception))
        self.assertIn("--allow-no-mirror", str(ctx.exception))

    def test_refuses_when_only_content_id_provided(self):
        with self.assertRaises(TwinMirrorEnforcementError) as ctx:
            assert_twin_mirror_at_close(
                content_mirror_id=str(uuid.uuid4()),
                ratification_envelope_id=None,
                allow_no_mirror=False,
            )
        self.assertIn("--ratification-envelope-id", str(ctx.exception))

    def test_refuses_when_only_envelope_id_provided(self):
        with self.assertRaises(TwinMirrorEnforcementError) as ctx:
            assert_twin_mirror_at_close(
                content_mirror_id=None,
                ratification_envelope_id=str(uuid.uuid4()),
                allow_no_mirror=False,
            )
        self.assertIn("--content-mirror-id", str(ctx.exception))

    def test_refuses_when_allow_no_mirror_combined_with_ids(self):
        with self.assertRaises(TwinMirrorEnforcementError) as ctx:
            assert_twin_mirror_at_close(
                content_mirror_id=str(uuid.uuid4()),
                ratification_envelope_id=str(uuid.uuid4()),
                allow_no_mirror=True,
            )
        self.assertIn("mutually exclusive", str(ctx.exception))

    def test_allow_no_mirror_returns_allowed_result(self):
        result = assert_twin_mirror_at_close(
            content_mirror_id=None,
            ratification_envelope_id=None,
            allow_no_mirror=True,
        )
        self.assertEqual(result.mode, "allowed_no_mirror")
        self.assertIsNone(result.content_mirror_id)
        self.assertIsNone(result.ratification_envelope_id)

    def test_refuses_malformed_content_uuid(self):
        with self.assertRaises(TwinMirrorEnforcementError) as ctx:
            assert_twin_mirror_at_close(
                content_mirror_id="not-a-uuid",
                ratification_envelope_id=str(uuid.uuid4()),
                allow_no_mirror=False,
            )
        self.assertIn("--content-mirror-id", str(ctx.exception))

    def test_refuses_malformed_envelope_uuid(self):
        with self.assertRaises(TwinMirrorEnforcementError) as ctx:
            assert_twin_mirror_at_close(
                content_mirror_id=str(uuid.uuid4()),
                ratification_envelope_id="not-a-uuid",
                allow_no_mirror=False,
            )
        self.assertIn("--ratification-envelope-id", str(ctx.exception))

    def test_refuses_when_content_row_missing(self):
        envelope = self._make_deliverable(
            deliverable_type="ratification_record",
            title="Envelope row",
        )
        with self.assertRaises(TwinMirrorEnforcementError) as ctx:
            assert_twin_mirror_at_close(
                content_mirror_id=str(uuid.uuid4()),  # not in DB
                ratification_envelope_id=str(envelope.id),
                allow_no_mirror=False,
            )
        self.assertIn("not found", str(ctx.exception))

    def test_refuses_when_envelope_row_missing(self):
        content = self._make_deliverable(title="Content row")
        with self.assertRaises(TwinMirrorEnforcementError) as ctx:
            assert_twin_mirror_at_close(
                content_mirror_id=str(content.id),
                ratification_envelope_id=str(uuid.uuid4()),  # not in DB
                allow_no_mirror=False,
            )
        self.assertIn("not found", str(ctx.exception))

    def test_refuses_when_content_row_is_diagnostic(self):
        content = self._make_deliverable(
            title="Diagnostic content", diagnostic_status="diagnostic",
        )
        envelope = self._make_deliverable(
            deliverable_type="ratification_record", title="Envelope",
        )
        with self.assertRaises(TwinMirrorEnforcementError) as ctx:
            assert_twin_mirror_at_close(
                content_mirror_id=str(content.id),
                ratification_envelope_id=str(envelope.id),
                allow_no_mirror=False,
            )
        self.assertIn("diagnostic", str(ctx.exception))
        self.assertIn("--content-mirror-id", str(ctx.exception))

    def test_refuses_when_envelope_row_is_diagnostic(self):
        content = self._make_deliverable(title="Content")
        envelope = self._make_deliverable(
            deliverable_type="ratification_record",
            title="Diagnostic envelope",
            diagnostic_status="diagnostic",
        )
        with self.assertRaises(TwinMirrorEnforcementError) as ctx:
            assert_twin_mirror_at_close(
                content_mirror_id=str(content.id),
                ratification_envelope_id=str(envelope.id),
                allow_no_mirror=False,
            )
        self.assertIn("diagnostic", str(ctx.exception))
        self.assertIn("--ratification-envelope-id", str(ctx.exception))

    def test_refuses_when_envelope_is_wrong_deliverable_type(self):
        content = self._make_deliverable(title="Content")
        envelope = self._make_deliverable(
            deliverable_type="document",  # NOT ratification_record
            title="Wrong type envelope",
        )
        with self.assertRaises(TwinMirrorEnforcementError) as ctx:
            assert_twin_mirror_at_close(
                content_mirror_id=str(content.id),
                ratification_envelope_id=str(envelope.id),
                allow_no_mirror=False,
            )
        self.assertIn("deliverable_type", str(ctx.exception))
        self.assertIn("ratification_record", str(ctx.exception))

    def test_refuses_when_both_ids_are_the_same(self):
        """Ledger #16 requires two distinct artifacts (Rigby T1 F-BLOCKING)."""
        envelope = self._make_deliverable(
            deliverable_type="ratification_record",
            title="Would-be-both",
        )
        with self.assertRaises(TwinMirrorEnforcementError) as ctx:
            assert_twin_mirror_at_close(
                content_mirror_id=str(envelope.id),
                ratification_envelope_id=str(envelope.id),
                allow_no_mirror=False,
            )
        self.assertIn("DIFFERENT", str(ctx.exception))

    def test_verified_path_returns_populated_result(self):
        content = self._make_deliverable(title="Content mirror row")
        envelope = self._make_deliverable(
            deliverable_type="ratification_record",
            title="Ratification envelope row",
        )
        result = assert_twin_mirror_at_close(
            content_mirror_id=str(content.id),
            ratification_envelope_id=str(envelope.id),
            allow_no_mirror=False,
        )
        self.assertEqual(result.mode, "verified")
        self.assertEqual(result.content_mirror_id, content.id)
        self.assertEqual(result.ratification_envelope_id, envelope.id)
        self.assertEqual(result.content_mirror_title, "Content mirror row")
        self.assertEqual(
            result.ratification_envelope_title, "Ratification envelope row",
        )


class SessionLifecycleCloseIntegrationTests(_WrapperFileMixin, TestCase):
    """CLI-level tests — refuse path must not touch DB or wrapper."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create(username=_TEST_USERNAME)
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name="Session Lifecycle Test WS",
        )

    def _make_deliverable(self, **overrides):
        defaults = dict(
            title="row",
            content="body " * 30,
            agent_name="Rigby",
            category="PA Created",
            deliverable_type="document",
            status="ready",
            user=self.user,
            workspace=self.workspace,
        )
        defaults.update(overrides)
        return Deliverable.objects.create(**defaults)

    def _existing_pin(self) -> str:
        pin = "pa-abcdef0123456789"
        ChatConversation.objects.create(
            conversation_id=pin,
            user_id=self.user.id,
            session_title="prior session",
            user_message="hi",
            assistant_response="hi",
            session_active=True,
        )
        return pin

    def test_close_refuses_when_no_mirror_flags(self):
        """No mirror flags + no --allow-no-mirror → refuse, DB untouched."""
        pin = self._existing_pin()
        wrapper = self._write_fixture(_wrapper_body(pin))

        with self.assertRaises(CommandError) as ctx:
            call_command(
                "session_lifecycle", "close",
                "--label", "s2941-test",
                "--user", _TEST_USERNAME,
                "--wrapper-path", str(wrapper),
                stdout=StringIO(),
                stderr=StringIO(),
            )
        self.assertIn("Ledger #16", str(ctx.exception))

        # Wrapper untouched, prior pin still active.
        self.assertEqual(wrapper.read_text().strip(), _wrapper_body(pin).strip())
        row = ChatConversation.objects.get(conversation_id=pin)
        self.assertTrue(row.session_active)

    def test_close_allows_when_allow_no_mirror_passed(self):
        """--allow-no-mirror → proceeds and logs audit line."""
        pin = self._existing_pin()
        wrapper = self._write_fixture(_wrapper_body(pin))
        out = StringIO()
        call_command(
            "session_lifecycle", "close",
            "--label", "s2941-cascade",
            "--user", _TEST_USERNAME,
            "--wrapper-path", str(wrapper),
            "--allow-no-mirror",
            stdout=out,
        )
        output = out.getvalue()
        self.assertIn("close complete", output)
        self.assertIn("[TWIN-MIRROR ALLOW_NO_MIRROR]", output)

        # Wrapper WAS rewritten with a new pin.
        self.assertNotEqual(
            wrapper.read_text().strip(), _wrapper_body(pin).strip(),
        )

    def test_close_proceeds_when_mirror_ids_verify(self):
        pin = self._existing_pin()
        wrapper = self._write_fixture(_wrapper_body(pin))
        content = self._make_deliverable(title="Content mirror doc")
        envelope = self._make_deliverable(
            deliverable_type="ratification_record",
            title="Ratification envelope doc",
        )
        out = StringIO()
        call_command(
            "session_lifecycle", "close",
            "--label", "s2941-verified",
            "--user", _TEST_USERNAME,
            "--wrapper-path", str(wrapper),
            "--content-mirror-id", str(content.id),
            "--ratification-envelope-id", str(envelope.id),
            stdout=out,
        )
        output = out.getvalue()
        self.assertIn("close complete", output)
        self.assertIn("[TWIN-MIRROR VERIFIED]", output)
        self.assertIn(str(content.id), output)
        self.assertIn(str(envelope.id), output)

    def test_close_refuses_when_envelope_row_wrong_type(self):
        pin = self._existing_pin()
        wrapper = self._write_fixture(_wrapper_body(pin))
        content = self._make_deliverable(title="Content")
        envelope = self._make_deliverable(
            deliverable_type="document", title="Wrong type",
        )
        with self.assertRaises(CommandError) as ctx:
            call_command(
                "session_lifecycle", "close",
                "--label", "s2941-wrongtype",
                "--user", _TEST_USERNAME,
                "--wrapper-path", str(wrapper),
                "--content-mirror-id", str(content.id),
                "--ratification-envelope-id", str(envelope.id),
                stdout=StringIO(),
                stderr=StringIO(),
            )
        self.assertIn("ratification_record", str(ctx.exception))
        # Wrapper untouched
        self.assertEqual(wrapper.read_text().strip(), _wrapper_body(pin).strip())

    def test_close_refuses_when_mutex_violated_via_cli(self):
        """CLI plumbing test for mutual exclusion (Rigby T1 non-blocking ask)."""
        pin = self._existing_pin()
        wrapper = self._write_fixture(_wrapper_body(pin))
        content = self._make_deliverable(title="Content")
        envelope = self._make_deliverable(
            deliverable_type="ratification_record", title="Envelope",
        )
        with self.assertRaises(CommandError) as ctx:
            call_command(
                "session_lifecycle", "close",
                "--label", "s2941-mutex",
                "--user", _TEST_USERNAME,
                "--wrapper-path", str(wrapper),
                "--content-mirror-id", str(content.id),
                "--ratification-envelope-id", str(envelope.id),
                "--allow-no-mirror",
                stdout=StringIO(),
                stderr=StringIO(),
            )
        self.assertIn("mutually exclusive", str(ctx.exception))
        # Wrapper untouched
        self.assertEqual(wrapper.read_text().strip(), _wrapper_body(pin).strip())

    def test_retire_only_close_bypasses_twin_mirror(self):
        """--retire-only is a recovery path, not a ratification ceremony."""
        pin = self._existing_pin()
        wrapper = self._write_fixture(_wrapper_body(pin))
        out = StringIO()
        call_command(
            "session_lifecycle", "close",
            "--retire-only",
            "--user", _TEST_USERNAME,
            "--wrapper-path", str(wrapper),
            stdout=out,
        )
        output = out.getvalue()
        self.assertIn("close complete", output)
        self.assertNotIn("[TWIN-MIRROR", output)
