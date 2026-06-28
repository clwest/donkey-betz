"""
Session 1251 PR 12A — rigby_shift_brief_tool integration tests.

Real-DB end-to-end exercises of :func:`build_shift_brief` and the
``rigby_shift_brief_tool`` dispatcher handler. Acceptance criteria from
``00-START-NEXT-SESSION.md``:

  - Single invocation produces the brief in < 5s.
  - Output < 1200 chars.
  - Reuses ≥ 5 existing PA tools.
  - No new model / migration / flag.
  - Side-effect free (read-only).
  - Handles all-four-S1250-flags-OFF gracefully.

These tests assert structure + char cap + graceful-degradation behavior.
The 7 sub-tools are exercised via the real dispatcher; if any of them
raise inside the test environment, the brief still renders and the
failing sub-tool is recorded in ``degraded_fields``.
"""
from __future__ import annotations

import unittest.mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import ChatConversation
from core.services.rigby_shift_brief import (
    MAX_BRIEF_CHARS,
    S1250_FLAGS,
    build_shift_brief,
)
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


class RigbyShiftBriefStructureTests(TestCase):
    """Verify the 6-section structure and the <1200 char cap."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="shiftbrieftester",
            password="x",
            email="shiftbrief@example.com",
        )
        self.conversation_id = "pa-shiftbrief-test"
        for _ in range(3):
            ChatConversation.objects.create(
                conversation_id=self.conversation_id,
                user=self.user,
                session_title="Shift brief test thread",
                user_message="ping",
                assistant_response="pong",
            )

    def test_returns_ok_with_required_keys(self):
        result = build_shift_brief(
            user_id=self.user.id,
            conversation_id=self.conversation_id,
        )
        self.assertTrue(result["ok"])
        for key in ("summary_text", "traffic_light", "sections", "metadata"):
            self.assertIn(key, result)

    def test_six_sections_present(self):
        result = build_shift_brief(
            user_id=self.user.id,
            conversation_id=self.conversation_id,
        )
        sections = result["sections"]
        for key in (
            "top_priority",
            "platform_health",
            "active_risks",
            "what_changed",
            "what_not_to_work_on",
            "next_action",
        ):
            self.assertIn(key, sections, f"missing section: {key}")

    def test_summary_text_under_char_cap(self):
        result = build_shift_brief(
            user_id=self.user.id,
            conversation_id=self.conversation_id,
        )
        self.assertLessEqual(
            len(result["summary_text"]),
            MAX_BRIEF_CHARS,
            f"brief too long: {len(result['summary_text'])} chars",
        )

    def test_traffic_light_is_one_of_three_states(self):
        result = build_shift_brief(
            user_id=self.user.id,
            conversation_id=self.conversation_id,
        )
        self.assertIn(result["traffic_light"], {"GREEN", "YELLOW", "RED"})

    def test_metadata_reports_tools_called(self):
        result = build_shift_brief(
            user_id=self.user.id,
            conversation_id=self.conversation_id,
        )
        tools_called = result["metadata"]["tools_called"]
        # At least the 7 sub-tools we orchestrate (one may be skipped if
        # conversation_id is None, but we pass one above).
        self.assertGreaterEqual(
            len(tools_called),
            6,
            f"expected ≥6 sub-tools, got {len(tools_called)}: {tools_called}",
        )

    def test_summary_text_contains_all_section_headers(self):
        result = build_shift_brief(
            user_id=self.user.id,
            conversation_id=self.conversation_id,
        )
        text = result["summary_text"]
        for header in (
            "Top priority",
            "Platform health",
            "Active risks",
            "What changed",
            "What NOT to work on",
            "Suggested next action",
        ):
            self.assertIn(header, text, f"missing header: {header!r}")


class RigbyShiftBriefFlagDefaultsTests(TestCase):
    """Acceptance criterion #7 — gracefully handles all-S1250-flags-OFF."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="flagstester", password="x", email="flag@example.com",
        )

    def test_renders_with_default_flag_state(self):
        # No flag overrides — relies on settings defaults (all OFF per
        # Session 1250 PR audit §2 of the capability handoff).
        result = build_shift_brief(user_id=self.user.id)
        self.assertTrue(result["ok"])
        # When all flags OFF, the "what NOT to work on" advice should hint
        # at the dormant pipeline.
        skip_text = " ".join(result["sections"]["what_not_to_work_on"]).lower()
        self.assertIn("dormant", skip_text)

    def test_renders_with_all_flags_on(self):
        overrides = {flag: True for flag in S1250_FLAGS}
        with self.settings(**overrides):
            result = build_shift_brief(user_id=self.user.id)
        self.assertTrue(result["ok"])
        # Active risks should now flag the unusual flag state.
        risks_text = " ".join(result["sections"]["active_risks"]).lower()
        self.assertIn("flag", risks_text)


class RigbyShiftBriefDegradationTests(TestCase):
    """Verify a sub-tool failure populates degraded_fields without raising."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="degraded", password="x", email="degraded@example.com",
        )

    def test_sub_tool_exception_lands_in_degraded_fields(self):
        # Patch one sub-tool to blow up. The brief must still render, the
        # failing sub-tool name must be in degraded_fields, and the brief
        # text must still contain all 6 section headers.
        with unittest.mock.patch.object(
            ToolDispatcher,
            "_handle_audit",
            side_effect=RuntimeError("simulated audit failure"),
        ):
            result = build_shift_brief(user_id=self.user.id)

        self.assertTrue(result["ok"])
        self.assertIn("audit_findings", result["metadata"]["degraded_fields"])
        # Other sub-tools should still be present in tools_called.
        self.assertIn("ops_digest", result["metadata"]["tools_called"])
        # And the brief should still have all 6 headers.
        for header in (
            "Top priority",
            "Platform health",
            "Active risks",
            "What changed",
            "What NOT to work on",
            "Suggested next action",
        ):
            self.assertIn(header, result["summary_text"])


class RigbyShiftBriefDispatcherIntegrationTests(TestCase):
    """Verify the dispatcher handler wraps the helper correctly."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="dispatcher", password="x", email="dispatch@example.com",
        )

    def test_handler_returns_structured_payload(self):
        dispatcher = ToolDispatcher()
        result = dispatcher._handle_rigby_shift_brief(  # type: ignore[attr-defined]
            tool_name="rigby_shift_brief_tool",
            payload={"action": "generate"},
            user_id=self.user.id,
            trace_id="test-shift-brief",
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["tool"], "rigby_shift_brief_tool")
        self.assertEqual(result["action"], "generate")
        self.assertIn("summary_text", result)
        self.assertLessEqual(len(result["summary_text"]), MAX_BRIEF_CHARS)

    def test_handler_rejects_unknown_action(self):
        dispatcher = ToolDispatcher()
        result = dispatcher._handle_rigby_shift_brief(  # type: ignore[attr-defined]
            tool_name="rigby_shift_brief_tool",
            payload={"action": "post"},
            user_id=self.user.id,
            trace_id="test-shift-brief",
        )
        self.assertFalse(result["ok"])
        self.assertIn("Unknown action", result["error"])


class RigbyShiftBriefRegistrationTests(TestCase):
    """Verify the tool is registered and discoverable via the schema."""

    def test_tool_registered_in_dispatcher(self):
        dispatcher = ToolDispatcher()
        self.assertIn(
            "rigby_shift_brief_tool",
            dispatcher._tool_handlers,  # type: ignore[attr-defined]
        )

    def test_schema_exposes_tool(self):
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS

        names = {s.get("name") for s in PA_TOOL_SCHEMAS}
        self.assertIn("rigby_shift_brief_tool", names)
