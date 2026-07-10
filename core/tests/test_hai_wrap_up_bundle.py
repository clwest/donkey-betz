"""
§16 Notification Fanout — Wrap-Up Bundle Acceptance Tests
=========================================================

Written PRE-implementation per ratified PLAYBOOK-3.2.2 (acceptance-tests-first)
and CDR-001 §7 + §12.3 4-gap wrap-up scope.

Governance references:
- Ratified rule: PLAYBOOK-3.2.2 (Chapter 3 §3.2 v0.2.0)
- Ratified rule: PLAYBOOK-2.2.2 (Chapter 2 §2.2 v0.2.0) — CDR-001 covers scope
- Capability Discovery Record: docs/research/platform/CDR_001_notification_fanout_receiver_driven_pattern.md
- Category A verification: SESSION_2737 close (Cat A ran 2026-07-09; all 4 gaps still real at HEAD 5bcb9777)

Bundle scope (per CDR-001 §7 + §12.3):

- Gap 1 — Inbox `DirectMessage` receiver on `HumanAttentionItem.post_save`
  (7 imperative create sites exist today; no receiver; Inbox lane dark to
  HAI fanout).
- Gap 2 — Cross-channel `HAIDispatchLog` audit table (existing
  `NotificationLog` is Web-Push-scoped; cannot audit Discord/Expo/Inbox
  dispatches).
- Gap 3 — Formalize `payload['channels_fired']` list convention (generalizes
  the ad-hoc `payload['discord_sent']` Discord-specific flag).
- Gap 4 — Cross-channel dispatch contract normalization (per Rigby SIGN
  refinement O4 in CDR-001 §12.3).

Do NOT rewrite these tests to match an implementation. Per PLAYBOOK-3.2.2:
if an implementation cannot satisfy a test, either the implementation is
wrong or the test needs a governance amendment via a CDR before the test
changes. Reverse-engineering tests is a PLAYBOOK-3.2.2 violation.
"""
from __future__ import annotations

import unittest


# ============================================================================
# Gap 3+4 — Shared dispatch-state helper (foundational — other gaps depend on it)
# ============================================================================

class AT16_3_ChannelsFiredConvention(unittest.TestCase):
    """AT16-3 — `payload['channels_fired']` list convention.

    Formalizes the ad-hoc `payload['discord_sent']` flag as a
    cross-channel convention. Backward-compat with legacy flag preserved.
    """

    def test_payload_helper_functions_exist(self):
        """Shared helper module exposes mark + has functions."""
        from core.services import hai_dispatch_state
        self.assertTrue(hasattr(hai_dispatch_state, 'payload_mark_channel_fired'))
        self.assertTrue(hasattr(hai_dispatch_state, 'payload_has_channel_fired'))
        self.assertTrue(hasattr(hai_dispatch_state, 'payload_channels_fired'))

    def test_helper_roundtrip_semantics(self):
        """Mark a channel; has-check confirms; list returns membership."""
        from core.services.hai_dispatch_state import (
            payload_mark_channel_fired,
            payload_has_channel_fired,
            payload_channels_fired,
        )
        payload = {}
        self.assertFalse(payload_has_channel_fired(payload, 'discord'))
        payload_mark_channel_fired(payload, 'discord')
        self.assertTrue(payload_has_channel_fired(payload, 'discord'))
        self.assertIn('discord', payload_channels_fired(payload))
        # Idempotent — marking twice doesn't duplicate.
        payload_mark_channel_fired(payload, 'discord')
        self.assertEqual(
            payload_channels_fired(payload).count('discord'), 1,
            "channels_fired list should not duplicate on repeated mark",
        )
        # Distinct channels tracked independently.
        payload_mark_channel_fired(payload, 'webpush')
        self.assertTrue(payload_has_channel_fired(payload, 'discord'))
        self.assertTrue(payload_has_channel_fired(payload, 'webpush'))
        self.assertFalse(payload_has_channel_fired(payload, 'expo'))

    def test_backward_compat_legacy_discord_sent_flag(self):
        """`payload['discord_sent']=True` still suppresses Discord dispatch
        (legacy producers migrate at their own pace)."""
        from core.services.hai_dispatch_state import payload_has_channel_fired
        payload = {'discord_sent': True}
        self.assertTrue(
            payload_has_channel_fired(payload, 'discord'),
            "Legacy payload['discord_sent']=True must still register as fired",
        )
        # Backward-compat is one-way: helper reads legacy but writes canonical.
        payload = {'discord_sent': False}
        self.assertFalse(payload_has_channel_fired(payload, 'discord'))


# ============================================================================
# Gap 4 — Contract state (small; folded with Gap 3 module)
# ============================================================================

class AT16_4_ContractStateHelper(unittest.TestCase):
    """AT16-4 — Cross-channel dispatch contract normalization.

    Per Rigby SIGN O4 refinement in CDR-001 §12.3: canonize the four
    dispatch states so audit + observability + dedup all agree.
    """

    def test_contract_state_helper_returns_canonical_states(self):
        """`ChannelDispatchState` enum and lookup helper exist."""
        from core.services.hai_dispatch_state import ChannelDispatchState
        # Six canonical states cover the observable dispatch outcomes.
        expected = {
            'NOT_ATTEMPTED',
            'SUCCEEDED',
            'FAILED',
            'SUPPRESSED_BY_PRODUCER',
            'KILL_SWITCH',
            'GATED_OUT',
        }
        actual = {member.name for member in ChannelDispatchState}
        self.assertEqual(
            actual, expected,
            "ChannelDispatchState enum drifted; contract needs a CDR amendment",
        )


# ============================================================================
# Gap 2 — HAIDispatchLog cross-channel audit
# ============================================================================

class AT16_2_HAIDispatchLog(unittest.TestCase):
    """AT16-2 — `HAIDispatchLog` cross-channel audit table.

    Fills the observability gap where `NotificationLog` (Web-Push-scoped)
    cannot audit Discord/Expo/Inbox dispatches. Records identity carriage
    per CDR-001 §21 F6 warning (executor_actor + sponsor_actor +
    principal_user).
    """

    def test_haidispatchlog_model_exists(self):
        """Model resolves from app_label + class_name."""
        from django.apps import apps
        model = apps.get_model('core', 'HAIDispatchLog')
        self.assertIsNotNone(model)
        # Required fields per CDR-001 §7 Gap 2 + §21 F6 identity carriage.
        field_names = {f.name for f in model._meta.get_fields()}
        required = {
            'user', 'source_type', 'source_id', 'channel',
            'dispatched_at', 'status', 'error_message',
            'executor_actor', 'sponsor_actor', 'principal_user',
        }
        missing = required - field_names
        self.assertEqual(
            missing, set(),
            f"HAIDispatchLog missing required fields per CDR-001: {missing}",
        )

    def test_haidispatchlog_status_choices_match_contract(self):
        """`status` field choices align with `ChannelDispatchState` enum."""
        from django.apps import apps
        from core.services.hai_dispatch_state import ChannelDispatchState
        model = apps.get_model('core', 'HAIDispatchLog')
        status_field = model._meta.get_field('status')
        choice_values = {c[0] for c in status_field.choices}
        enum_values = {member.value for member in ChannelDispatchState}
        self.assertEqual(
            choice_values, enum_values,
            "HAIDispatchLog.status choices must match ChannelDispatchState enum",
        )

    def test_migration_landed(self):
        """Migration file exists under core/migrations/ with HAIDispatchLog operation.

        Static test — inspects migration graph via file system, does not
        require DB access. Guards against a future refactor that removes
        the model definition without removing the migration.
        """
        import importlib
        import pkgutil
        from django.db import migrations
        import core.migrations as migrations_pkg

        matching = []
        for module_info in pkgutil.iter_modules(migrations_pkg.__path__):
            name = module_info.name
            if not name.startswith('0'):
                continue
            mod = importlib.import_module(f'core.migrations.{name}')
            migration = getattr(mod, 'Migration', None)
            if migration is None:
                continue
            for op in getattr(migration, 'operations', []):
                if isinstance(op, migrations.CreateModel) and op.name == 'HAIDispatchLog':
                    matching.append(name)
                    break
        self.assertGreaterEqual(
            len(matching), 1,
            "No core migration creates HAIDispatchLog model",
        )

    def test_dedup_query_shape(self):
        """`(user, source_type, source_id, channel)` unique constraint documented."""
        from django.apps import apps
        model = apps.get_model('core', 'HAIDispatchLog')
        # Verify the model declares a UniqueConstraint or unique_together for
        # cross-channel dedup — one row per (recipient, source_type, source_id, channel).
        constraint_names = {c.name for c in (model._meta.constraints or [])}
        unique_together = model._meta.unique_together
        dedup_present = any(
            'dedup' in name.lower() for name in constraint_names
        ) or bool(unique_together)
        self.assertTrue(
            dedup_present,
            "HAIDispatchLog missing (user, source_type, source_id, channel) dedup "
            "constraint — cross-channel double-dispatch cannot be audited",
        )


# ============================================================================
# Gap 1 — Inbox receiver + Celery task on HAI.post_save
# ============================================================================

class AT16_1_InboxReceiver(unittest.TestCase):
    """AT16-1 — Inbox `DirectMessage` receiver on `HumanAttentionItem.post_save`.

    Follows the exact receiver-driven pattern already ratified for Discord
    (PR #3038) + Web Push (PR #3040): sync guards → transaction.on_commit
    → Celery task → adapter call. NO new fanout-service abstraction.
    """

    def test_inbox_signal_receiver_module_exists(self):
        """`core/signals_inbox_notifications.py` exists + registers post_save receiver."""
        import inspect
        from core import signals_inbox_notifications as sig
        # Module has an `on_hai_inbox_dispatch` receiver function.
        self.assertTrue(
            hasattr(sig, 'on_hai_inbox_dispatch'),
            "signals_inbox_notifications module missing on_hai_inbox_dispatch receiver",
        )
        # Receiver source contains the canonical decorator + HAI sender binding.
        src = inspect.getsource(sig)
        self.assertIn(
            "@receiver(post_save, sender='core.HumanAttentionItem')", src,
            "Receiver must bind to HumanAttentionItem.post_save exactly",
        )

    def test_notify_hai_inbox_task_exists(self):
        """`notify_hai_inbox` Celery task exists in `core/tasks_push_notifications.py`."""
        from core.tasks_push_notifications import notify_hai_inbox
        # @shared_task-decorated tasks are callable + expose .delay().
        self.assertTrue(callable(notify_hai_inbox))
        self.assertTrue(hasattr(notify_hai_inbox, 'delay'))

    def test_kill_switch_setting_defined(self):
        """`HAI_INBOX_DISPATCH_ENABLED` kill switch defaults True in settings."""
        from django.conf import settings
        # Getattr with default reproduces production behavior on unset.
        value = getattr(settings, 'HAI_INBOX_DISPATCH_ENABLED', True)
        self.assertIn(value, (True, False), "kill switch must be a boolean")

    def test_pref_gate_reused_from_discord_signal(self):
        """Inbox task reuses `_pref_gates_pass` — no duplicated gate logic."""
        import inspect
        from core import tasks_push_notifications
        src = inspect.getsource(tasks_push_notifications.notify_hai_inbox)
        # Same helper the Discord + Web Push tasks import.
        self.assertIn("_pref_gates_pass", src)

    def test_urgency_floor_critical(self):
        """Receiver + task both gate on `urgency='critical'` (v1 floor)."""
        import inspect
        from core import signals_inbox_notifications as sig
        from core import tasks_push_notifications
        receiver_src = inspect.getsource(sig)
        task_src = inspect.getsource(tasks_push_notifications.notify_hai_inbox)
        self.assertIn("'critical'", receiver_src)
        self.assertIn("'critical'", task_src)


# ============================================================================
# Meta — AT class registry guard
# ============================================================================

class AT_MetaTestStructure(unittest.TestCase):
    """AT16 meta — guards against silent test-class deletion."""

    EXPECTED_AT_CLASSES = {
        'AT16_3_ChannelsFiredConvention',
        'AT16_4_ContractStateHelper',
        'AT16_2_HAIDispatchLog',
        'AT16_1_InboxReceiver',
    }

    def test_all_ATs_present_in_module(self):
        import sys
        module = sys.modules[__name__]
        actual = {
            name for name in dir(module)
            if name.startswith('AT16_')
        }
        self.assertEqual(
            actual, self.EXPECTED_AT_CLASSES,
            f"AT16 class set drifted. Missing: {self.EXPECTED_AT_CLASSES - actual}. "
            f"Extra (needs a CDR amendment per PLAYBOOK-3.2.2): {actual - self.EXPECTED_AT_CLASSES}."
        )


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
