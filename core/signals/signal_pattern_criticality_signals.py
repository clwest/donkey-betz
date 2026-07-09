"""
Signal pattern criticality → HAI signals — Session 2734
=======================================================

Capability Chain §6 wire-up: when the SignalAggregationService writes a
``SignalCluster`` whose ``strength`` crosses the configurable
``signal_pattern_criticality_threshold`` (default 0.9), automatically
create a ``HumanAttentionItem`` for admin users so critical patterns
(fraud detection, trend spike, high-strength demand signal) escalate
within seconds instead of waiting for a human to inspect the
signal-studio dashboard.

Chain:
    SignalAggregationService.cluster_and_persist()
    → SignalCluster.save()
    → [this receiver, on_commit]
    → HumanAttentionBridge.create_signal_pattern_attention(cluster)
    → HumanInterfaceService.create_attention_item(source_type='signal_pattern')
    → HumanAttentionItem row
    → Frontend inbox / cockpit surface

Threshold contract:
    * Read at each receiver fire from
      ``SystemConfiguration(key='signal_pattern_criticality_threshold')``.
    * Missing / non-numeric config falls back to
      ``_DEFAULT_THRESHOLD`` (0.9), matching audit §3.8 speculative
      default.
    * Chris can tune the threshold via ``governance_tool.set_config`` or
      any equivalent SystemConfiguration write path — no code change
      required.

Kill switch:
    ``settings.SIGNAL_PATTERN_CRITICALITY_ENABLED`` (default True).
    Setting to False disables the receiver entirely so a bad threshold
    or a broken bridge can never spam the attention stream.
"""
import logging

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save

logger = logging.getLogger(__name__)

_DEFAULT_THRESHOLD = 0.9
_CONFIG_KEY = 'signal_pattern_criticality_threshold'


def _read_threshold() -> float:
    """Read the criticality threshold from SystemConfiguration.

    Fails safe to ``_DEFAULT_THRESHOLD`` on any error (missing row,
    non-numeric value, DB unavailable). Never raises.
    """
    try:
        from core.models.system import SystemConfiguration
        entry = SystemConfiguration.objects.filter(
            key=_CONFIG_KEY, is_active=True,
        ).values_list('value', flat=True).first()
        if entry is None or entry == '':
            return _DEFAULT_THRESHOLD
        return float(entry)
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            "[SIGNAL_PATTERN_CRITICALITY] threshold read failed "
            "(%s: %s); using default %.2f",
            type(e).__name__, e, _DEFAULT_THRESHOLD,
        )
        return _DEFAULT_THRESHOLD


def _create_attention(cluster):
    """Dispatch to the HumanAttentionBridge on-commit."""
    try:
        from core.services.human_attention_bridge import attention_bridge
        attention_bridge.create_signal_pattern_attention(cluster)
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            "[SIGNAL_PATTERN_CRITICALITY] bridge dispatch failed "
            "cluster_id=%s (%s: %s)",
            getattr(cluster, 'id', None), type(e).__name__, e,
        )


def escalate_signal_pattern(sender, instance, created, **kwargs):
    """Post-save receiver on ``SignalCluster``.

    Escalates to HAI when:
      * the row was newly created (not update);
      * ``strength >= threshold``;
      * kill switch is not tripped.

    Broadcast is scheduled via ``transaction.on_commit`` so a
    rolled-back cluster row produces no phantom attention item.
    """
    if not getattr(settings, 'SIGNAL_PATTERN_CRITICALITY_ENABLED', True):
        return
    if not created:
        return

    strength = float(getattr(instance, 'strength', 0.0) or 0.0)
    threshold = _read_threshold()
    if strength < threshold:
        return

    transaction.on_commit(lambda: _create_attention(instance))


def connect_signal_pattern_criticality_signals():
    """Wire the SignalCluster post_save receiver.

    Registered from ``core/apps.py::CoreConfig._register_signals`` at
    Django startup. Idempotent via ``dispatch_uid``.
    """
    from core.models_signal_intelligence import SignalCluster
    post_save.connect(
        escalate_signal_pattern,
        sender=SignalCluster,
        dispatch_uid=(
            "core.signals.signal_pattern_criticality_signals"
            ".escalate_signal_pattern"
        ),
    )
    logger.info(
        "[SIGNAL_PATTERN_CRITICALITY_SIGNALS] receiver wired "
        "on SignalCluster.post_save (default threshold=%.2f)",
        _DEFAULT_THRESHOLD,
    )
