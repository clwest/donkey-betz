"""
Regression tests for Session 2734 — Capability Chain §6 Signal Detection.

Exercises ``core.signals.signal_pattern_criticality_signals.escalate_signal_pattern``:
the post_save receiver on ``SignalCluster`` that escalates high-strength
patterns to ``HumanAttentionItem`` via ``HumanAttentionBridge`` when the
cluster's ``strength`` crosses the configurable
``signal_pattern_criticality_threshold`` (default 0.9).

Test discipline:
- Real DB. No mocked querysets.
- ``HumanAttentionBridge.create_signal_pattern_attention`` is patched so
  we assert the *receiver's* contract (threshold, kill switch, on_commit
  gating) without touching the ``HumanInterfaceService`` write path.
- Uses ``captureOnCommitCallbacks(execute=True)`` because the receiver
  schedules the escalation via ``transaction.on_commit``.

Chain being tested:

    SignalCluster.save() [strength >= threshold]
    → escalate_signal_pattern (this file)
    → transaction.on_commit → attention_bridge.create_signal_pattern_attention
    → HumanAttentionItem row [asserted in bridge unit tests, not here]

Run::

    python manage.py test core.tests.test_signal_pattern_criticality -v2
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from core.models_signal_intelligence import SignalCluster


_BRIDGE_PATH = (
    "core.services.human_attention_bridge.HumanAttentionBridge."
    "create_signal_pattern_attention"
)
_CONFIG_KEY = "signal_pattern_criticality_threshold"


def _make_cluster(**overrides) -> SignalCluster:
    defaults = dict(
        name="test cluster",
        pattern_type="demand_spike",
        source_breakdown={"bluesky": 5, "reddit": 3},
        strength=0.5,
        keywords=["persona", "customer research"],
    )
    defaults.update(overrides)
    return SignalCluster.objects.create(**defaults)


def _set_threshold(value: str) -> None:
    from core.models.system import SystemConfiguration
    SystemConfiguration.objects.update_or_create(
        key=_CONFIG_KEY,
        defaults={"value": value, "is_active": True},
    )


def _clear_threshold() -> None:
    from core.models.system import SystemConfiguration
    SystemConfiguration.objects.filter(key=_CONFIG_KEY).delete()


class SignalPatternCriticalityHappyPathTests(TestCase):
    """Above-threshold clusters escalate exactly once."""

    def test_default_threshold_escalates_above_0_9(self):
        _clear_threshold()
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            cluster = _make_cluster(strength=0.95)
        mock_bridge.assert_called_once()
        (dispatched_cluster,) = mock_bridge.call_args.args
        self.assertEqual(dispatched_cluster.id, cluster.id)
        self.assertEqual(dispatched_cluster.strength, 0.95)

    def test_exact_threshold_boundary_escalates(self):
        """strength == threshold triggers escalation (>=, not >)."""
        _clear_threshold()
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_cluster(strength=0.9)
        mock_bridge.assert_called_once()

    def test_custom_threshold_via_system_configuration(self):
        """Threshold read from SystemConfiguration at each fire."""
        _set_threshold("0.75")
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_cluster(strength=0.80)
        mock_bridge.assert_called_once()

    def test_bad_config_falls_back_to_default(self):
        """Non-numeric config value falls back to _DEFAULT_THRESHOLD 0.9."""
        _set_threshold("not_a_number")
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            # 0.85 would escalate under a 0.75 custom threshold, but must
            # be REJECTED under the 0.9 default fallback.
            _make_cluster(strength=0.85)
        mock_bridge.assert_not_called()

    def test_config_lookup_db_failure_falls_back_and_receiver_stays_safe(self):
        """SystemConfiguration query itself raises (simulated DB /
        migration / import failure). The receiver must still no-op
        safely — no exception propagates out of ``save()`` — AND the
        default threshold (0.9) is used so a critical strength (0.95)
        continues to escalate correctly.

        Added per Rigby SIGN Q4 refinement (pin pa-d2dd9bb674fe4cae).
        """
        _clear_threshold()

        # Replace ``SystemConfiguration.objects`` with a manager whose
        # ``.filter(...)`` raises — simulates DB migration / connection
        # failure at the config-read path. ``_read_threshold`` must
        # swallow via its inner try/except and return default 0.9.
        raising_manager = MagicMock()
        raising_manager.filter.side_effect = Exception("simulated DB failure")

        with patch(
            "core.models.system.SystemConfiguration.objects",
            new=raising_manager,
        ):
            with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
                # This must NOT raise — SignalCluster.save() is the
                # user-facing contract that must remain intact.
                _make_cluster(strength=0.95)
        # Fallback default 0.9 applied, 0.95 >= 0.9 → escalation fires.
        mock_bridge.assert_called_once()


class SignalPatternCriticalityFilteringTests(TestCase):
    """The receiver filters correctly on threshold + created + kill switch."""

    def test_below_threshold_does_not_escalate(self):
        _clear_threshold()
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_cluster(strength=0.5)
        mock_bridge.assert_not_called()

    def test_just_below_threshold_does_not_escalate(self):
        _clear_threshold()
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_cluster(strength=0.899)
        mock_bridge.assert_not_called()

    def test_update_of_existing_cluster_does_not_re_escalate(self):
        """The receiver requires ``created=True``. Editing a cluster to
        bump its strength above threshold must not trigger a second HAI.
        """
        _clear_threshold()
        # Create below threshold; no escalation.
        with patch(_BRIDGE_PATH) as first_bridge, self.captureOnCommitCallbacks(execute=True):
            cluster = _make_cluster(strength=0.5)
        first_bridge.assert_not_called()

        # Now update the strength — no escalation should fire even
        # though strength crosses the default threshold.
        with patch(_BRIDGE_PATH) as second_bridge, self.captureOnCommitCallbacks(execute=True):
            cluster.strength = 0.98
            cluster.save()
        second_bridge.assert_not_called()

    @override_settings(SIGNAL_PATTERN_CRITICALITY_ENABLED=False)
    def test_kill_switch_disables_escalation(self):
        """``SIGNAL_PATTERN_CRITICALITY_ENABLED=False`` fully disables
        the receiver — no bridge dispatch even for critical strength.
        """
        _clear_threshold()
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_cluster(strength=0.99)
        mock_bridge.assert_not_called()


class SignalPatternCriticalityTransactionSafetyTests(TestCase):
    """Escalation is scheduled on_commit — no phantom items."""

    def test_rolled_back_transaction_does_not_escalate(self):
        _clear_threshold()
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=False):
            _make_cluster(strength=0.95)
        mock_bridge.assert_not_called()
