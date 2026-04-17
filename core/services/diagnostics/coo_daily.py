"""
COOAgent daily operations diagnostic.
======================================

Second consumer of `core.services.scheduled_diagnostic_runner` (after
CTOAgent). Chosen specifically to validate the primitive's generality on
a non-execution-count metrics surface — CTO gates on failure rates,
COO gates on **throughput + aging + SLA breaches** (deliverables,
review backlog, action items, stuck initiatives).

Metrics shape
-------------

Unlike the CTO diagnostic's `{window_24h, window_7d, delta_vs_7d}` shape,
COO uses domain-oriented top-level keys:

    {
        'velocity': {
            'created_24h', 'published_24h',
            'created_7d_avg_daily', 'published_7d_avg_daily',
            'created_delta_pct', 'published_delta_pct',
        },
        'review_backlog': {
            'ready_count', 'ready_p95_age_hours',
            'ready_over_threshold_count', 'oldest_ready_hours',
        },
        'action_items': {
            'pending_by_urgency': {'critical', 'high', 'medium', 'low'},
            'pending_over_sla_by_urgency': {...},
            'oldest_critical_hours',
        },
        'initiatives': {
            'stuck_count', 'stuck_top': [...],
        },
    }

Gates (all env-tunable)
------------------------

    VELOCITY_DROP_HIGH      created delta < -30% AND abs delta >= 5
    PUBLISHING_JAM_CRIT     published=0 in 24h AND ready_count >= 10
    REVIEW_AGE_HIGH         ready p95 age > 24h OR ready_over_threshold >= 5
    OLDEST_REVIEW_HIGH      oldest ready > 48h
    ACTION_BACKLOG_HIGH     pending critical >= 2 OR pending high >= 5
    ACTION_BACKLOG_CRIT     pending critical >= 5
    STUCK_INITIATIVES_HIGH  >= 5 initiatives unchanged > 72h in current_stage

Tunables (env vars)
-------------------

    COO_DIAG_VELOCITY_DROP_PCT         (0.30)   created_delta_pct threshold
    COO_DIAG_VELOCITY_ABS_FLOOR        (5)      absolute delta floor (low-volume guard)
    COO_DIAG_REVIEW_AGE_HOURS          (24)    p95 / over-threshold cutoff
    COO_DIAG_REVIEW_COUNT_MIN          (5)     ready_over_threshold min for HIGH
    COO_DIAG_OLDEST_REVIEW_HOURS       (48)    oldest-ready-hours HIGH threshold
    COO_DIAG_JAM_READY_MIN             (10)    ready_count floor for PUBLISHING_JAM_CRIT
    COO_DIAG_ACTION_CRIT_MIN           (2)     pending critical count → HIGH
    COO_DIAG_ACTION_CRIT_CRIT          (5)     pending critical count → CRITICAL
    COO_DIAG_ACTION_HIGH_MIN           (5)     pending high count → HIGH
    COO_DIAG_STUCK_HOURS               (72)    initiative stage staleness window
    COO_DIAG_STUCK_MIN                 (5)     stuck initiative count → HIGH
    COO_DIAG_STUCK_IGNORE_BEFORE       ("")    ISO date; initiatives updated
                                               before this cutoff are excluded
                                               from the stuck count. Use after
                                               a one-time sediment cleanup so
                                               historical dead weight doesn't
                                               trip the gate forever. Empty =
                                               no filtering (default).
    COO_DIAG_PUBLISHABLE_TYPES         ("")    CSV of deliverable_type values
                                               that actually reach 'published'
                                               status on this platform.
                                               Session 1094 investigation:
                                               only ~1 type (document, from
                                               InitiativePipeline) is auto-
                                               publishing. Most agent output
                                               types (analysis, research,
                                               report, code, etc.) are internal
                                               artifacts that never publish.
                                               When set, the velocity +
                                               publishing_jam + review_age gates
                                               scope to ONLY these types, so
                                               the gates measure the actual
                                               publishing workflow — not
                                               internal-analysis noise that
                                               permanently trips the jam gate.
                                               Empty = all types counted
                                               (default, back-compat).

Feature flags
-------------

    COO_DIAGNOSTIC_ENABLED             gate the whole task (default: false)
    COO_DIAGNOSTIC_POSTING_ENABLED     gate governance posting (default: false)

Rollout plan
------------

Identical to CTO (Session 1093):
  1. Merge with both flags OFF
  2. COO_DIAGNOSTIC_ENABLED=true for 24h observation — check [COO-DIAG] logs
  3. Tune COO_DIAG_* thresholds per observed baseline
  4. COO_DIAGNOSTIC_POSTING_ENABLED=true → daily attention items begin

Publishing pipeline investigation (Session 1094 follow-up)
----------------------------------------------------------

Investigation found that `Deliverable.status='published'` is only set by
one code path (`content_tool.publish` manual PA action) and by one agent
(InitiativePipeline, 10 publishes all-time). Meanwhile scheduled analysis
agents (StockAnalyst / InstitutionalWatcher / MarketAnomaly / BearCase /
BullCase / TechnicalDocument / etc.) produce 400+ `ready` deliverables
per day that never publish — because they're **internal analyses, not
publishable content**.

Consequence: without `COO_DIAG_PUBLISHABLE_TYPES` set, the
PUBLISHING_JAM_CRIT gate will ALWAYS trip because the denominator
includes non-publishing types. Before enabling POSTING, operators
should either:

  (a) Set `COO_DIAG_PUBLISHABLE_TYPES=document,video,edited_content,blog`
      (or whatever types actually flow through publish on your platform)
      so the gate measures the real publishing funnel.

  (b) Introduce an `is_internal` or `requires_publish` flag on the
      Deliverable model and filter by it (larger refactor, cleanest
      long-term answer).

  (c) Migrate scheduled-analysis agents to land in a different status
      (e.g. `completed` instead of `ready`) so they don't pollute the
      publish-pending pile.

This module supports (a) directly via the env var. (b) and (c) are
architectural decisions for a later session.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta, timezone as dt_timezone
from statistics import quantiles
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


# =============================================================================
# Env helpers
# =============================================================================

def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


# =============================================================================
# Metrics collector
# =============================================================================

def _p95_hours(hours_list: List[float]) -> float:
    """p95 of a list of ages in hours. Returns 0.0 on empty input.

    Uses statistics.quantiles(n=100) when possible; falls back to nearest-rank
    for small samples where quantiles() raises StatisticsError.
    """
    if not hours_list:
        return 0.0
    if len(hours_list) < 2:
        return float(hours_list[0])
    try:
        # statistics.quantiles returns cut points; [94] is the 95th percentile
        return float(quantiles(sorted(hours_list), n=100)[94])
    except Exception:
        # Nearest-rank fallback
        sorted_list = sorted(hours_list)
        idx = max(0, int(0.95 * len(sorted_list)) - 1)
        return float(sorted_list[idx])


def collect_metrics(now: datetime, cutoff_24h: datetime, cutoff_7d: datetime) -> Dict[str, Any]:
    """Collect COO-flavored operational metrics.

    Uses canonical Django ORM only — no cross-service calls. Safe to run
    in a beat task without Redis/broker dependencies.
    """
    from core.models_deliverables import Deliverable
    from core.models_human_interface import HumanAttentionItem
    from core.models import Initiative

    # ── Publishable-type filter (Session 1094 investigation)
    # When set, velocity + review_backlog + publishing_jam gates scope to
    # only these deliverable_type values. Prevents the jam gate from
    # permanently tripping on platforms where most agents produce internal
    # analyses (never meant to publish) mixed with the tiny fraction of
    # user-facing content that does. See module docstring.
    publishable_types_raw = os.environ.get('COO_DIAG_PUBLISHABLE_TYPES', '').strip()
    publishable_types: List[str] = [
        t.strip() for t in publishable_types_raw.split(',') if t.strip()
    ] if publishable_types_raw else []

    def _deliverable_base_qs():
        qs = Deliverable.objects.all()
        if publishable_types:
            qs = qs.filter(deliverable_type__in=publishable_types)
        return qs

    # ── Velocity: created vs published, 24h vs 7d-avg-daily baseline
    created_24h = _deliverable_base_qs().filter(created_at__gte=cutoff_24h).count()
    published_24h = _deliverable_base_qs().filter(
        updated_at__gte=cutoff_24h, status='published'
    ).count()
    created_7d = _deliverable_base_qs().filter(created_at__gte=cutoff_7d).count()
    published_7d = _deliverable_base_qs().filter(
        updated_at__gte=cutoff_7d, status='published'
    ).count()
    created_7d_avg_daily = created_7d / 7.0
    published_7d_avg_daily = published_7d / 7.0

    def _delta_pct(recent: float, baseline: float) -> float:
        if baseline <= 0:
            return 0.0
        return round((recent - baseline) / baseline, 4)

    velocity = {
        'created_24h': created_24h,
        'published_24h': published_24h,
        'created_7d_avg_daily': round(created_7d_avg_daily, 2),
        'published_7d_avg_daily': round(published_7d_avg_daily, 2),
        'created_delta_pct': _delta_pct(created_24h, created_7d_avg_daily),
        'published_delta_pct': _delta_pct(published_24h, published_7d_avg_daily),
        'publishable_types_filter': publishable_types or None,
    }

    # ── Review backlog: deliverables in 'ready' — haven't progressed to
    #    published/completed/archived. Age measured from created_at since
    #    'ready' is the first status a deliverable lands in after work.
    review_age_hours_threshold = _env_int('COO_DIAG_REVIEW_AGE_HOURS', 24)
    ready_threshold_cutoff = now - timedelta(hours=review_age_hours_threshold)

    ready_rows = list(
        _deliverable_base_qs().filter(status='ready').values('id', 'created_at', 'title')
    )
    ready_ages_hours = [
        (now - r['created_at']).total_seconds() / 3600.0
        for r in ready_rows if r['created_at']
    ]
    ready_over_threshold = [
        r for r in ready_rows
        if r['created_at'] and r['created_at'] <= ready_threshold_cutoff
    ]
    oldest_ready_hours = max(ready_ages_hours) if ready_ages_hours else 0.0

    review_backlog = {
        'ready_count': len(ready_rows),
        'ready_p95_age_hours': round(_p95_hours(ready_ages_hours), 2),
        'ready_over_threshold_count': len(ready_over_threshold),
        'ready_over_threshold_hours': review_age_hours_threshold,
        'oldest_ready_hours': round(oldest_ready_hours, 2),
        # Top 5 oldest for narrative — title + age
        'oldest_ready_top': [
            {
                'title': (r.get('title') or '')[:80],
                'age_hours': round(
                    (now - r['created_at']).total_seconds() / 3600.0, 1
                ),
            }
            for r in sorted(
                (r for r in ready_rows if r['created_at']),
                key=lambda r: r['created_at'],
            )[:5]
        ],
    }

    # ── Action items: pending count by urgency + over-SLA subset
    #    SLA = same threshold as review_age for simplicity; per-urgency
    #    escalation could come later.
    pending_items = list(
        HumanAttentionItem.objects.filter(status='pending')
        .values('urgency', 'created_at')
    )
    pending_by_urgency: Dict[str, int] = {}
    pending_over_sla_by_urgency: Dict[str, int] = {}
    critical_ages_hours: List[float] = []

    for item in pending_items:
        urgency = item.get('urgency') or 'unknown'
        pending_by_urgency[urgency] = pending_by_urgency.get(urgency, 0) + 1
        if item['created_at'] and item['created_at'] <= ready_threshold_cutoff:
            pending_over_sla_by_urgency[urgency] = (
                pending_over_sla_by_urgency.get(urgency, 0) + 1
            )
        if urgency == 'critical' and item['created_at']:
            critical_ages_hours.append(
                (now - item['created_at']).total_seconds() / 3600.0
            )

    action_items = {
        'pending_by_urgency': pending_by_urgency,
        'pending_over_sla_by_urgency': pending_over_sla_by_urgency,
        'pending_total': sum(pending_by_urgency.values()),
        'oldest_critical_hours': (
            round(max(critical_ages_hours), 2) if critical_ages_hours else 0.0
        ),
    }

    # ── Stuck initiatives: active initiatives whose current_stage hasn't
    #    changed in N hours. Proxy for "stage change" = updated_at since
    #    we don't have an explicit stage-change timestamp.
    #
    # Session 1094 follow-up: optional `COO_DIAG_STUCK_IGNORE_BEFORE` cutoff
    # excludes historical sediment from the count. Chris's local has 147
    # ACTIVE initiatives untouched for 30+ days (oldest 76d) — pure dead
    # weight from earlier sessions. Setting this env var to an ISO date
    # makes the gate ignore anything `updated_at < ignore_before`, so the
    # count reflects current operational state not archaeology. Default
    # empty = no filtering (back-compat). Recommended: clean sediment via
    # `python manage.py cleanup_stale_initiatives --older-than-days 30 --apply`
    # then leave this unset — or set it as a belt-and-suspenders fallback.
    stuck_hours = _env_int('COO_DIAG_STUCK_HOURS', 72)
    stuck_cutoff = now - timedelta(hours=stuck_hours)
    stuck_qs = Initiative.objects.filter(
        status='ACTIVE',
        updated_at__lte=stuck_cutoff,
    )

    ignore_before_raw = os.environ.get('COO_DIAG_STUCK_IGNORE_BEFORE', '').strip()
    ignore_before_applied = False
    if ignore_before_raw:
        try:
            ignore_before_dt = datetime.fromisoformat(ignore_before_raw)
            # Attach tzinfo if the env var was naive (assume UTC — this is
            # an operator knob, not user input)
            if ignore_before_dt.tzinfo is None:
                ignore_before_dt = ignore_before_dt.replace(tzinfo=dt_timezone.utc)
            stuck_qs = stuck_qs.filter(updated_at__gte=ignore_before_dt)
            ignore_before_applied = True
        except (TypeError, ValueError):
            logger.warning(
                'COO_DIAG_STUCK_IGNORE_BEFORE=%r could not be parsed as ISO date '
                '(expected e.g. "2026-03-16" or "2026-03-16T12:00:00") — ignoring',
                ignore_before_raw,
            )

    stuck_rows = list(stuck_qs.values('name', 'current_stage', 'updated_at')[:20])

    initiatives = {
        'stuck_count': stuck_qs.count(),
        'stuck_hours_threshold': stuck_hours,
        'ignore_before': ignore_before_raw if ignore_before_applied else None,
        'stuck_top': [
            {
                'name': (r.get('name') or '')[:80],
                'current_stage': r.get('current_stage'),
                'stale_hours': round(
                    (now - r['updated_at']).total_seconds() / 3600.0, 1
                ) if r.get('updated_at') else None,
            }
            for r in stuck_rows[:5]
        ],
    }

    return {
        'window_24h': {
            'since': cutoff_24h.isoformat(),
            'until': now.isoformat(),
        },
        'window_7d': {
            'since': cutoff_7d.isoformat(),
            'until': now.isoformat(),
        },
        'velocity': velocity,
        'review_backlog': review_backlog,
        'action_items': action_items,
        'initiatives': initiatives,
    }


# =============================================================================
# Gate evaluator
# =============================================================================

def evaluate_gate(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate COO threshold gates. Matches runner's gate dict contract."""
    velocity_drop_pct = _env_float('COO_DIAG_VELOCITY_DROP_PCT', 0.30)
    velocity_abs_floor = _env_int('COO_DIAG_VELOCITY_ABS_FLOOR', 5)
    review_age_hours = _env_int('COO_DIAG_REVIEW_AGE_HOURS', 24)
    review_count_min = _env_int('COO_DIAG_REVIEW_COUNT_MIN', 5)
    oldest_review_hours = _env_int('COO_DIAG_OLDEST_REVIEW_HOURS', 48)
    jam_ready_min = _env_int('COO_DIAG_JAM_READY_MIN', 10)
    action_crit_min = _env_int('COO_DIAG_ACTION_CRIT_MIN', 2)
    action_crit_crit = _env_int('COO_DIAG_ACTION_CRIT_CRIT', 5)
    action_high_min = _env_int('COO_DIAG_ACTION_HIGH_MIN', 5)
    stuck_min = _env_int('COO_DIAG_STUCK_MIN', 5)

    reasons: List[str] = []
    details: List[str] = []
    severities: List[str] = []

    velocity = metrics['velocity']
    review = metrics['review_backlog']
    action = metrics['action_items']
    init = metrics['initiatives']

    # ── VELOCITY_DROP_HIGH: % drop AND absolute floor (per Rigby's feedback —
    #    % alone pages low-volume environments on tiny deltas)
    created_delta = velocity['created_24h'] - velocity['created_7d_avg_daily']
    if (velocity['created_delta_pct'] <= -velocity_drop_pct
            and abs(created_delta) >= velocity_abs_floor):
        reasons.append('VELOCITY_DROP_HIGH')
        details.append(
            f'Created {velocity["created_24h"]} in 24h vs 7d avg '
            f'{velocity["created_7d_avg_daily"]:.1f}/day '
            f'({velocity["created_delta_pct"] * 100:+.1f}%, '
            f'abs Δ {created_delta:+.1f} >= ±{velocity_abs_floor} floor)'
        )
        severities.append('high')

    # ── PUBLISHING_JAM_CRIT: zero published AND ready_count rising.
    #    Strong signal of a quality-gate / channel-auth / permission jam,
    #    not just a quiet day.
    if velocity['published_24h'] == 0 and review['ready_count'] >= jam_ready_min:
        reasons.append('PUBLISHING_JAM_CRIT')
        details.append(
            f'Zero deliverables published in 24h while {review["ready_count"]} '
            f'are stuck in ready (>= {jam_ready_min} jam floor) — quality gate '
            f'or channel-auth issue suspected'
        )
        severities.append('critical')

    # ── REVIEW_AGE_HIGH: p95 age OR count-over-threshold
    if (review['ready_p95_age_hours'] >= review_age_hours
            or review['ready_over_threshold_count'] >= review_count_min):
        reasons.append('REVIEW_AGE_HIGH')
        details.append(
            f'Review backlog aging: p95 age {review["ready_p95_age_hours"]:.1f}h '
            f'(threshold {review_age_hours}h), '
            f'{review["ready_over_threshold_count"]} items older than '
            f'{review_age_hours}h (min {review_count_min} for HIGH)'
        )
        severities.append('high')

    # ── OLDEST_REVIEW_HIGH: oldest single ready > 48h. Per Rigby — p95 alone
    #    can be noisy on low-volume days, but one very stale item is a signal.
    if review['oldest_ready_hours'] >= oldest_review_hours:
        reasons.append('OLDEST_REVIEW_HIGH')
        details.append(
            f'Oldest ready deliverable is {review["oldest_ready_hours"]:.1f}h old '
            f'(threshold {oldest_review_hours}h)'
        )
        severities.append('high')

    # ── ACTION_BACKLOG_HIGH / CRIT: pending critical count driven
    pending_critical = action['pending_by_urgency'].get('critical', 0)
    pending_high = action['pending_by_urgency'].get('high', 0)
    if pending_critical >= action_crit_crit:
        reasons.append('ACTION_BACKLOG_CRIT')
        details.append(
            f'{pending_critical} pending critical HumanAttentionItems '
            f'(>= {action_crit_crit} critical threshold)'
        )
        severities.append('critical')
    elif pending_critical >= action_crit_min or pending_high >= action_high_min:
        reasons.append('ACTION_BACKLOG_HIGH')
        details.append(
            f'{pending_critical} critical + {pending_high} high pending '
            f'action items (>= {action_crit_min} critical OR {action_high_min} high)'
        )
        severities.append('high')

    # ── STUCK_INITIATIVES_HIGH
    if init['stuck_count'] >= stuck_min:
        reasons.append('STUCK_INITIATIVES_HIGH')
        details.append(
            f'{init["stuck_count"]} initiatives stale > '
            f'{init["stuck_hours_threshold"]}h in current_stage '
            f'(min {stuck_min} for HIGH)'
        )
        severities.append('high')

    if not reasons:
        return {
            'tripped': False,
            'severity': None,
            'reasons': [],
            'reason_details': ['All gates within thresholds'],
        }

    if 'critical' in severities:
        severity = 'critical'
    elif 'high' in severities:
        severity = 'high'
    else:
        severity = 'medium'

    return {
        'tripped': True,
        'severity': severity,
        'reasons': reasons,
        'reason_details': details,
    }


# =============================================================================
# Dedupe payload builder
# =============================================================================

def build_dedupe_payload(
    metrics: Dict[str, Any],
    gate: Dict[str, Any],
    date_bucket: str,
) -> Dict[str, Any]:
    """Stable 'same-shape diagnostic already posted today' fingerprint."""
    velocity = metrics.get('velocity', {})
    review = metrics.get('review_backlog', {})
    action = metrics.get('action_items', {})
    init = metrics.get('initiatives', {})
    return {
        'date_bucket': date_bucket,
        'severity': gate.get('severity'),
        'gate_reasons': sorted(gate.get('reasons', [])),
        # Round metric slices so tiny fluctuations don't change the hash
        'created_24h': velocity.get('created_24h'),
        'published_24h': velocity.get('published_24h'),
        'created_delta_pct_rounded': round(velocity.get('created_delta_pct', 0), 2),
        'ready_count': review.get('ready_count'),
        'ready_p95_age_bucket': int(review.get('ready_p95_age_hours', 0) // 6) * 6,
        'oldest_ready_bucket': int(review.get('oldest_ready_hours', 0) // 12) * 12,
        'pending_critical': action.get('pending_by_urgency', {}).get('critical', 0),
        'pending_high': action.get('pending_by_urgency', {}).get('high', 0),
        'stuck_count': init.get('stuck_count'),
    }


# =============================================================================
# Prompt builder — COO voice (concise, action items, top-3 bullets)
# =============================================================================

def build_agent_prompt(metrics: Dict[str, Any], gate: Dict[str, Any]) -> str:
    """COO-voice prompt: concise, bullet-heavy, Top-3 actions."""
    bundle = {
        'velocity': metrics['velocity'],
        'review_backlog': metrics['review_backlog'],
        'action_items': metrics['action_items'],
        'initiatives': metrics['initiatives'],
        'gate': {
            'severity': gate['severity'],
            'reasons': gate['reasons'],
            'details': gate['reason_details'],
        },
    }
    return (
        'You are running the daily COO operations diagnostic. '
        'The threshold gate has tripped — produce a concise ops report '
        'in your characteristic voice: bullets not paragraphs, action '
        'items not narrative.\n\n'
        'METRICS BUNDLE (live data from Deliverable / HumanAttentionItem / '
        'Initiative tables — do not invent numbers):\n'
        '```json\n'
        f'{json.dumps(bundle, indent=2, default=str)}\n'
        '```\n\n'
        'Output sections (markdown, in this order):\n'
        '1. **Severity:** restate the gate severity\n'
        '2. **Headline:** one sentence — the most acute operational issue\n'
        '3. **Top issues:** max 3 bullets — each names a specific cluster '
        '(stuck items, publishing jam, specific pending attention items) '
        'with 1-2 sentence root-cause hypothesis\n'
        '4. **Recommended actions:** max 3 concrete next steps with owner '
        'hints (e.g., "unblock review backlog: publish the 5 oldest ready '
        'items with manual override", "escalate 3 pending critical '
        'HumanAttentionItems to triage")\n'
        '5. **Confidence:** low/medium/high — how confident are you in '
        'the root-cause hypotheses given only the bundle\n\n'
        'Stay concise. Operations needs action, not prose. '
        'Do not exceed 400 words total.'
    )


# =============================================================================
# Headline + title builders
# =============================================================================

def build_headline(metrics: Dict[str, Any], gate: Dict[str, Any]) -> str:
    """One-line severity + metric punchline + primary trigger."""
    severity = (gate.get('severity') or 'UNKNOWN').upper()
    reason = gate['reasons'][0] if gate.get('reasons') else 'gate_tripped'
    velocity = metrics.get('velocity', {})
    return (
        f'{severity} — published {velocity.get("published_24h", 0)}/24h '
        f'(Δ {velocity.get("published_delta_pct", 0) * 100:+.0f}%), '
        f'{metrics.get("review_backlog", {}).get("ready_count", 0)} in review — '
        f'primary trigger: `{reason}`'
    )


def build_title(metrics: Dict[str, Any], gate: Dict[str, Any], date_label: str) -> str:
    severity = (gate.get('severity') or 'UNKNOWN').upper()
    velocity = metrics.get('velocity', {})
    return (
        f'COO Daily Ops Diagnostic — '
        f'{date_label} — '
        f'{severity} — '
        f'pub {velocity.get("published_24h", 0)} '
        f'(Δ{velocity.get("published_delta_pct", 0) * 100:+.0f}%)'
    )


# =============================================================================
# Section renderers
# =============================================================================

def render_velocity(metrics: Dict[str, Any], gate: Dict[str, Any]) -> List[str]:
    v = metrics['velocity']
    return [
        f'- Created (24h): **{v["created_24h"]}** vs 7d avg '
        f'{v["created_7d_avg_daily"]:.1f}/day '
        f'(Δ {v["created_delta_pct"] * 100:+.1f}%)',
        f'- Published (24h): **{v["published_24h"]}** vs 7d avg '
        f'{v["published_7d_avg_daily"]:.1f}/day '
        f'(Δ {v["published_delta_pct"] * 100:+.1f}%)',
    ]


def render_review_backlog(metrics: Dict[str, Any], gate: Dict[str, Any]) -> List[str]:
    r = metrics['review_backlog']
    lines = [
        f'- Ready awaiting publish: **{r["ready_count"]}**',
        f'- p95 age: {r["ready_p95_age_hours"]:.1f}h '
        f'(threshold {r["ready_over_threshold_hours"]}h)',
        f'- Over {r["ready_over_threshold_hours"]}h: '
        f'**{r["ready_over_threshold_count"]}**',
        f'- Oldest item: **{r["oldest_ready_hours"]:.1f}h** old',
    ]
    if r.get('oldest_ready_top'):
        lines.append('')
        lines.append('Oldest ready items:')
        for item in r['oldest_ready_top']:
            lines.append(
                f'  - {item["title"] or "(untitled)"} — {item["age_hours"]:.1f}h'
            )
    return lines


def render_action_items(metrics: Dict[str, Any], gate: Dict[str, Any]) -> List[str]:
    a = metrics['action_items']
    pending = a.get('pending_by_urgency', {})
    over_sla = a.get('pending_over_sla_by_urgency', {})
    lines = [
        f'- Pending total: **{a.get("pending_total", 0)}**',
    ]
    for urgency in ('critical', 'high', 'medium', 'low'):
        cnt = pending.get(urgency, 0)
        over = over_sla.get(urgency, 0)
        if cnt > 0:
            suffix = f' ({over} past SLA)' if over > 0 else ''
            lines.append(f'- {urgency.capitalize()}: {cnt}{suffix}')
    if a.get('oldest_critical_hours', 0) > 0:
        lines.append(
            f'- Oldest critical: **{a["oldest_critical_hours"]:.1f}h** old'
        )
    return lines


def render_stuck_initiatives(metrics: Dict[str, Any], gate: Dict[str, Any]) -> List[str]:
    i = metrics['initiatives']
    if i['stuck_count'] == 0:
        return []
    lines = [
        f'- **{i["stuck_count"]}** initiatives unchanged > '
        f'{i["stuck_hours_threshold"]}h in current_stage',
    ]
    if i.get('stuck_top'):
        lines.append('')
        lines.append('Top stuck:')
        for item in i['stuck_top']:
            stale = (
                f'{item["stale_hours"]:.1f}h' if item['stale_hours'] is not None
                else 'unknown'
            )
            lines.append(
                f'  - {item["name"] or "(unnamed)"} — stage `{item["current_stage"]}` '
                f'({stale} stale)'
            )
    return lines


# =============================================================================
# Config object
# =============================================================================

def build_config():
    """Build the COO DiagnosticConfig. Lazy import of runner."""
    from core.services.scheduled_diagnostic_runner import DiagnosticConfig

    return DiagnosticConfig(
        name='coo_daily_diagnostic',
        diagnostic_type='coo_daily_diagnostic',
        agent_name='COOAgent',
        source_agent='COOAgent',
        log_prefix='COO-DIAG',
        metrics_collector=collect_metrics,
        gate_evaluator=evaluate_gate,
        prompt_builder=build_agent_prompt,
        dedupe_payload_builder=build_dedupe_payload,
        headline_builder=build_headline,
        title_builder=build_title,
        extra_sections=[
            ('24h Velocity', render_velocity),
            ('Review Backlog', render_review_backlog),
            ('Action Items', render_action_items),
            ('Stuck Initiatives', render_stuck_initiatives),
        ],
        post_task_import_path='core.tasks:post_coo_daily_diagnostic',
        enabled_env='COO_DIAGNOSTIC_ENABLED',
        posting_enabled_env='COO_DIAGNOSTIC_POSTING_ENABLED',
        cache_key_prefix='coo_diag',
        workspace_id_env='COO_DIAG_WORKSPACE_ID',
        queue=os.environ.get('COO_DIAG_QUEUE', 'long_running'),
    )
