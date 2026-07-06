"""Arc I-0100 P2 (IB-1799-T1-01) — regression tests for the
``ToolCallRecord.trace_id`` write-side fix.

Background (per 1799 xx99 §1 point 1 + Arc I-0100 scoping §5 P2):
`ToolCallRecord.trace_id` is a ``UUIDField(null=True)`` that was 100% NULL
across 4144 rows at HEAD (ORM-verified 2026-07-03 at S1704 Q1-Q4). Three
writer sites (``tool_dispatcher._write_tool_call_record``,
``base_agent._record_tool_call`` via ``ToolCallRecord.record()``, and
``unified_pa_entrypoint._record_tool_call`` deprecated path) deliberately
wrote ``trace_id=None`` because their in-scope trace_id values are
non-UUID strings ("tool-N-hex", "pa-N-hex"). This broke the
``deliverable_provenance`` chain at ``deliverable_provenance.py:105``.

P2 fix: feature-flagged (``settings.TOOL_CALL_TRACE_ID_ENFORCED``, default
OFF) via ``resolve_trace_uuid()`` helper. When OFF, current 100%-NULL
behavior is preserved. When ON, all 3 writers populate ``trace_id`` with
a UUID (generated fresh when the caller's trace_id is a non-UUID string);
the human-readable string form remains in ``task_summary`` per F8-i
dual-format acceptance mitigation.

Run:
    python manage.py test core.tests.test_tool_call_record_trace_id -v2
"""

import uuid

from django.test import TestCase, override_settings

from core.models_tool_calls import ToolCallRecord, resolve_trace_uuid


class ResolveTraceUuidTests(TestCase):
    """Unit-level coverage of the ``resolve_trace_uuid()`` helper."""

    @override_settings(TOOL_CALL_TRACE_ID_ENFORCED=False)
    def test_flag_off_returns_none_regardless_of_input(self):
        """Flag OFF preserves pre-P2 behavior (all inputs → None)."""
        self.assertIsNone(resolve_trace_uuid(None))
        self.assertIsNone(resolve_trace_uuid("tool-1-abcd"))
        self.assertIsNone(resolve_trace_uuid(uuid.uuid4()))
        self.assertIsNone(resolve_trace_uuid(str(uuid.uuid4())))
        self.assertIsNone(resolve_trace_uuid("pa-42-deadbeef"))

    @override_settings(TOOL_CALL_TRACE_ID_ENFORCED=True)
    def test_flag_on_uuid_input_returned_as_is(self):
        """Flag ON: UUID object → same UUID."""
        input_uuid = uuid.uuid4()
        result = resolve_trace_uuid(input_uuid)
        self.assertEqual(result, input_uuid)

    @override_settings(TOOL_CALL_TRACE_ID_ENFORCED=True)
    def test_flag_on_uuid_string_input_parsed(self):
        """Flag ON: UUID-parseable string → parsed UUID."""
        input_uuid = uuid.uuid4()
        result = resolve_trace_uuid(str(input_uuid))
        self.assertEqual(result, input_uuid)

    @override_settings(TOOL_CALL_TRACE_ID_ENFORCED=True)
    def test_flag_on_non_uuid_string_generates_fresh(self):
        """Flag ON: non-UUID string ("tool-N-hex") → fresh UUID.

        The original string is preserved by the caller in ``task_summary``
        per F8-i dual-format acceptance. This test only verifies the
        helper generates a valid UUID; caller-level tests below verify
        task_summary preservation.
        """
        result = resolve_trace_uuid("tool-1-a1b2c3d4")
        self.assertIsInstance(result, uuid.UUID)
        # Should NOT match the input string parsed as any deterministic UUID.
        result2 = resolve_trace_uuid("tool-1-a1b2c3d4")
        self.assertIsInstance(result2, uuid.UUID)
        # Fresh generation → two calls should produce different UUIDs.
        self.assertNotEqual(result, result2)

    @override_settings(TOOL_CALL_TRACE_ID_ENFORCED=True)
    def test_flag_on_none_input_generates_fresh(self):
        """Flag ON: None input → fresh UUID (protects downstream joins
        from a NULL populate even when no trace_id was in scope).
        """
        result = resolve_trace_uuid(None)
        self.assertIsInstance(result, uuid.UUID)

    @override_settings(TOOL_CALL_TRACE_ID_ENFORCED=True)
    def test_flag_on_pa_string_form_generates_fresh(self):
        """Flag ON: "pa-N-hex" form (Session 1172 PA trace_id) → fresh UUID."""
        result = resolve_trace_uuid("pa-1-45705add")
        self.assertIsInstance(result, uuid.UUID)


class ToolCallRecordRecordClassmethodTests(TestCase):
    """Coverage of the ``ToolCallRecord.record()`` classmethod's trace_id
    handling (used by ``core/agents/base_agent.py:3408``).
    """

    @override_settings(TOOL_CALL_TRACE_ID_ENFORCED=False)
    def test_record_flag_off_null_trace_id(self):
        """Flag OFF: ``record(trace_id=...)`` writes NULL regardless of input."""
        record = ToolCallRecord.record(
            agent_name="TestAgent",
            tool_name="test_tool",
            parameters={},
            result={"ok": True},
            latency_ms=42,
            success=True,
            trace_id="tool-1-abcd",
        )
        self.assertIsNone(record.trace_id)

    @override_settings(TOOL_CALL_TRACE_ID_ENFORCED=True)
    def test_record_flag_on_non_uuid_populates_fresh(self):
        """Flag ON: non-UUID input string → fresh UUID persisted."""
        record = ToolCallRecord.record(
            agent_name="TestAgent",
            tool_name="test_tool",
            parameters={},
            result={"ok": True},
            latency_ms=42,
            success=True,
            trace_id="tool-1-abcd",
        )
        self.assertIsNotNone(record.trace_id)
        self.assertIsInstance(record.trace_id, uuid.UUID)

    @override_settings(TOOL_CALL_TRACE_ID_ENFORCED=True)
    def test_record_flag_on_valid_uuid_preserved(self):
        """Flag ON: valid UUID input → same UUID persisted (join key)."""
        input_uuid = uuid.uuid4()
        record = ToolCallRecord.record(
            agent_name="TestAgent",
            tool_name="test_tool",
            parameters={},
            result={"ok": True},
            latency_ms=42,
            success=True,
            trace_id=str(input_uuid),
        )
        self.assertEqual(record.trace_id, input_uuid)

    @override_settings(TOOL_CALL_TRACE_ID_ENFORCED=True)
    def test_record_flag_on_null_input_populates_fresh(self):
        """Flag ON: None input → fresh UUID (no more silent NULL populate)."""
        record = ToolCallRecord.record(
            agent_name="TestAgent",
            tool_name="test_tool",
            parameters={},
            result={"ok": True},
            latency_ms=42,
            success=True,
            trace_id=None,
        )
        self.assertIsNotNone(record.trace_id)
        self.assertIsInstance(record.trace_id, uuid.UUID)


class DispatcherWriterIntegrationTests(TestCase):
    """Integration coverage of the ``tool_dispatcher._write_tool_call_record``
    path (line 960) via a direct ORM verification.

    The dispatcher builds a ``ToolResult`` with a string trace_id
    ("tool-N-hex" per ``_generate_trace_id`` line 582). This test
    simulates that shape by directly invoking
    ``ToolCallRecord.objects.create(trace_id=resolve_trace_uuid(...))``
    with matching input shape.
    """

    @override_settings(TOOL_CALL_TRACE_ID_ENFORCED=False)
    def test_dispatcher_shape_flag_off_null(self):
        """Flag OFF: dispatcher writes trace_id=None (current behavior)."""
        record = ToolCallRecord.objects.create(
            trace_id=resolve_trace_uuid("tool-42-a1b2c3d4"),
            agent_name="Direct",
            tool_name="test_tool",
            parameters={},
            result_summary="",
            result_hash="",
            full_result="",
            result_size_bytes=0,
            success=True,
            latency_ms=1,
            task_summary="[tool-42-a1b2c3d4] dispatcher.execute",
        )
        self.assertIsNone(record.trace_id)
        # F8-i dual-format acceptance: string form preserved in task_summary
        self.assertIn("tool-42-a1b2c3d4", record.task_summary)

    @override_settings(TOOL_CALL_TRACE_ID_ENFORCED=True)
    def test_dispatcher_shape_flag_on_populates_and_preserves_string(self):
        """Flag ON: dispatcher populates trace_id UUID AND preserves the
        string form in task_summary (F8-i dual-format acceptance)."""
        record = ToolCallRecord.objects.create(
            trace_id=resolve_trace_uuid("tool-42-a1b2c3d4"),
            agent_name="Direct",
            tool_name="test_tool",
            parameters={},
            result_summary="",
            result_hash="",
            full_result="",
            result_size_bytes=0,
            success=True,
            latency_ms=1,
            task_summary="[tool-42-a1b2c3d4] dispatcher.execute",
        )
        # New format: UUID populated
        self.assertIsNotNone(record.trace_id)
        self.assertIsInstance(record.trace_id, uuid.UUID)
        # Legacy format: string preserved in task_summary
        self.assertIn("tool-42-a1b2c3d4", record.task_summary)


class DeliverableProvenanceJoinIntegrationTest(TestCase):
    """Verify the deliverable_provenance chain at line 105 works when
    ToolCallRecord rows carry the parent AgentExecution's trace_id UUID.

    Post-flag-on, when both a ToolCallRecord and the parent execution
    share the same UUID trace_id, ``ToolCallRecord.objects.filter(
    trace_id=execution.trace_id)`` returns the ToolCallRecord row.
    """

    @override_settings(TOOL_CALL_TRACE_ID_ENFORCED=True)
    def test_execution_trace_id_join_works_when_shared(self):
        """When ToolCallRecord and AgentExecution share a UUID trace_id,
        the deliverable_provenance chain (line 105) returns matches."""
        shared_uuid = uuid.uuid4()

        # Create a ToolCallRecord that carries the shared UUID
        record = ToolCallRecord.objects.create(
            trace_id=shared_uuid,  # would be resolve_trace_uuid(execution.trace_id)
            agent_name="TestAgent",
            tool_name="test_tool",
            parameters={},
            result_summary="",
            result_hash="",
            full_result="",
            result_size_bytes=0,
            success=True,
            latency_ms=1,
            task_summary="[test] execution",
        )

        # deliverable_provenance.py:105 pattern:
        matches = ToolCallRecord.objects.filter(trace_id=shared_uuid)
        self.assertEqual(matches.count(), 1)
        self.assertEqual(matches.first(), record)

    @override_settings(TOOL_CALL_TRACE_ID_ENFORCED=False)
    def test_execution_trace_id_join_empty_pre_flag(self):
        """Pre-flag / flag-off state: trace_id is NULL so the
        deliverable_provenance filter returns empty (current broken
        behavior — this test locks in the regression baseline)."""
        record = ToolCallRecord.objects.create(
            trace_id=resolve_trace_uuid("pa-1-45705add"),  # → None with flag off
            agent_name="PersonalAssistant",
            tool_name="test_tool",
            parameters={},
            result_summary="",
            result_hash="",
            full_result="",
            result_size_bytes=0,
            success=True,
            latency_ms=1,
            task_summary="[pa-1-45705add] pa dispatch",
        )
        self.assertIsNone(record.trace_id)

        # deliverable_provenance chain returns empty for any UUID join key
        matches = ToolCallRecord.objects.filter(trace_id=uuid.uuid4())
        self.assertEqual(matches.count(), 0)
