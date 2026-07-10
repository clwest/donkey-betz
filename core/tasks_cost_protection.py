"""
Cost Protection Celery tasks — Session 2735 Cost Protection Campaign P1.

One beat task, ``check_cost_thresholds``, that runs the threshold monitor
across all three windows (hour / day / month) and dispatches an HAI when
any window breaches. **Monitor-only at ship** — never calls
``governance.set_mode('freeze')`` regardless of ``cost_protection_enforce_mode``
config value. Enforcement flip is deferred to a later phase per Chris's
enforcement-gate discipline (runtime validation + monitor observation
period + explicit approval).

Cat A discipline: no new architecture. Uses:
- ``cost_threshold_monitor.check_all_windows`` — the new read-only
  service in this campaign
- ``HumanAttentionBridge.create_cost_breach_attention`` — 11th producer
  method on the pre-existing bridge
- HAI Delivery Fanout receivers (Discord + Web Push) shipped in the
  prior campaign — automatically fan the ``critical`` HAI to those
  channels
- Existing ``@shared_task`` pattern + ``default`` queue

Beat schedule: registered in ``core/celery.py`` at 15-minute intervals.
"""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name='check_cost_thresholds',
    queue='default',
    ignore_result=True,
    soft_time_limit=60,
)
def check_cost_thresholds():
    """Compute cost breach status across hour/day/month windows.

    Dispatches ``HumanAttentionBridge.create_cost_breach_attention`` for
    each window whose spend exceeds the configured threshold. Multiple
    windows can breach in the same tick (e.g., a spend spike will trip
    hour + day simultaneously); each gets its own HAI with a distinct
    ``idempotency_key`` so ``HumanInterfaceService.create_attention_item``
    dedup keeps the inbox tidy but does not collapse cross-window
    breaches into one row.

    Returns a structured summary for observability.
    """
    from core.services.cost_threshold_monitor import (
        check_all_windows,
        read_enforce_mode,
    )
    from core.services.human_attention_bridge import attention_bridge

    mode = read_enforce_mode()
    if mode == 'freeze':
        # Deliberately noisy log: enforcement mode is set but this
        # release does NOT implement the freeze dispatch. Anyone who
        # flipped the config to 'freeze' should know monitor-only is
        # still the behavior on this build.
        logger.warning(
            '[COST_MONITOR] cost_protection_enforce_mode=freeze but '
            'enforcement dispatch is not implemented in this release; '
            'behavior is monitor-only regardless.'
        )

    results = check_all_windows()
    breached = []
    for result in results:
        logger.info(
            '[COST_MONITOR] window=%s actual=$%.4f threshold=%s '
            'breached=%s rows=%d',
            result.window,
            float(result.actual_usd),
            (f'${float(result.threshold_usd):.4f}'
                if result.threshold_usd is not None else 'unset'),
            result.breached,
            result.row_count,
        )
        if result.breached:
            breached.append(result)

    # S2739 Cost Protection P2+ observation-period foothold (Cat 2
    # o1). would_freeze is a shadow counterfactual: True iff mode is
    # 'freeze' AND at least one window breached this tick — the exact
    # condition under which enforcement (if wired) would flip
    # governance. Emitted ONLY on breach so operators intentionally
    # testing with mode='freeze' but sub-threshold spend do not see
    # spurious shadow logs each tick. Fires on the same tick / same
    # breach set as the HAI dispatch below — the two share a
    # per-tick semantic even though the idempotency_key itself is
    # owned by the bridge (per Rigby Cat B SIGN pa-f2bc0abba82849a9).
    would_freeze = (mode == 'freeze' and bool(breached))
    if would_freeze:
        breached_windows = ','.join(b.window for b in breached)
        logger.warning(
            '[COST_MONITOR] would_freeze=True mode=freeze '
            'breach_count=%d windows=%s — enforcement not wired '
            'this release; HAI dispatched instead',
            len(breached), breached_windows,
        )

    # Rigby SIGN pa-188ec20f274c42e4 Q3 refinement: consolidate all
    # simultaneously-breached windows into ONE HAI so a spike (which
    # trips hour + day + month at the same time) does not spam the
    # inbox / fanout channels with three separate critical items.
    hai_dispatched = 0
    if breached:
        try:
            attention_bridge.create_cost_breach_attention(
                breached, would_freeze=would_freeze,
            )
            hai_dispatched = 1
        except Exception as e:  # pragma: no cover — defensive
            logger.warning(
                '[COST_MONITOR] bridge dispatch failed (%s: %s); '
                'HAI not created for this tick',
                type(e).__name__, e,
            )

    return {
        'mode': mode,
        'would_freeze': would_freeze,
        'windows_checked': len(results),
        'windows_breached': len(breached),
        'hai_dispatched': hai_dispatched,
        'summary': [
            {
                'window': r.window,
                'actual_usd': float(r.actual_usd),
                'threshold_usd': (
                    float(r.threshold_usd)
                    if r.threshold_usd is not None else None
                ),
                'breached': r.breached,
                'row_count': r.row_count,
            }
            for r in results
        ],
    }
