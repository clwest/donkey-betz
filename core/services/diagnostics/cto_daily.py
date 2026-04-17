"""
CTOAgent daily platform-reliability diagnostic.
================================================

First consumer of `core.services.scheduled_diagnostic_runner`. This module
owns everything CTO-specific: metrics shape (CeleryTaskEvent + AgentExecution
rollups), threshold gates, prompt template, body sections. The generic
runner owns orchestration (two-task pattern, feature flags, dedupe +
cooldown, payload cap, Template v1 wrapper).

Originally implemented in core/tasks_ops.py (Session 1093 PR #1983). Moved
here in Session 1094 so the runner primitive could be reused for COOAgent,
PlatformAuditAgent, and other diagnostic agents.

Behavior is byte-for-byte identical to the Session 1093 implementation —
same env vars, same thresholds, same Template v1 body, same cache key
prefix (`cto_diag:*`), same MT date bucket, same 240s post countdown.
Verified via `core/tests/test_cto_daily_diagnostic_via_runner.py`.

Env var reference
-----------------

Feature flags (both OFF by default):
    CTO_DIAGNOSTIC_ENABLED          gates the whole task
    CTO_DIAGNOSTIC_POSTING_ENABLED  gates only the governance post
                                    (lets you run in observation mode)

Threshold tunables (all optional — defaults chosen in Session 1093):
    CTO_DIAG_MIN_TOTAL_24H          (50)   sample guard for global gates
    CTO_DIAG_FAILRATE_HIGH          (0.06) high-severity fail rate threshold
    CTO_DIAG_FAILRATE_CRIT          (0.10) critical-severity fail rate threshold
    CTO_DIAG_DELTA_HIGH             (0.02) delta vs 7d baseline
    CTO_DIAG_NEW_SIG_COUNT          (5)    new failure signature min occurrences
    CTO_DIAG_AGENT_SPIKE_MIN        (5)    per-agent fail count spike floor
    CTO_DIAG_COOLDOWN_HOURS_HIGH    (20)   cooldown for high/medium severity
    CTO_DIAG_COOLDOWN_HOURS_CRIT    (6)    cooldown for critical severity

Scheduling:
    CTO_DIAG_QUEUE                  (long_running)
    CTO_DIAG_WORKSPACE_ID           (None) optional workspace for the alert
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


# =============================================================================
# Env helpers (CTO-specific threshold vars — tunables for the gate evaluator)
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

def collect_metrics(now: datetime, cutoff_24h: datetime, cutoff_7d: datetime) -> Dict[str, Any]:
    """Collect 24h + 7d metrics from CeleryTaskEvent + AgentExecution.

    Mirrors the query shapes in core/services/td_handlers_ops.py (slo_status
    + failure_signatures) so this diagnostic stays attribution-aligned with
    ops_tool. If you change one, change the other.
    """
    from core.models_celery_telemetry import CeleryTaskEvent
    from core.models_unified_system import AgentExecution
    from django.db.models import Count

    # AgentExecution-based stats (canonical "what's failing" source)
    exec_24h_total = AgentExecution.objects.filter(created_at__gte=cutoff_24h).count()
    exec_24h_failed = AgentExecution.objects.filter(
        created_at__gte=cutoff_24h, status='failed'
    ).count()
    exec_7d_total = AgentExecution.objects.filter(created_at__gte=cutoff_7d).count()
    exec_7d_failed = AgentExecution.objects.filter(
        created_at__gte=cutoff_7d, status='failed'
    ).count()

    fail_rate_24h = (exec_24h_failed / exec_24h_total) if exec_24h_total else 0.0
    fail_rate_7d = (exec_7d_failed / exec_7d_total) if exec_7d_total else 0.0
    delta_vs_7d = fail_rate_24h - fail_rate_7d

    top_failing_agents_24h = list(
        AgentExecution.objects.filter(
            created_at__gte=cutoff_24h, status='failed'
        ).values('agent__name').annotate(count=Count('id')).order_by('-count')[:10]
    )
    agent_7d = dict(
        (r['agent__name'], r['count'])
        for r in AgentExecution.objects.filter(
            created_at__gte=cutoff_7d, status='failed'
        ).values('agent__name').annotate(count=Count('id'))
    )

    # Timeout subset
    timeout_24h = AgentExecution.objects.filter(
        created_at__gte=cutoff_24h, status='failed',
        error_message__icontains='timed out',
    ).count()

    # Failure signatures from CeleryTaskEvent
    sig_24h = list(
        CeleryTaskEvent.objects.filter(
            started_at__gte=cutoff_24h, status='FAILURE'
        ).values('task_name', 'error_type')
        .annotate(count=Count('id')).order_by('-count')[:20]
    )
    sig_prior_7d_keys = set(
        (r['task_name'], r['error_type'])
        for r in CeleryTaskEvent.objects.filter(
            started_at__gte=cutoff_7d,
            started_at__lt=cutoff_24h,
            status='FAILURE',
        ).values('task_name', 'error_type').annotate(count=Count('id'))
    )
    new_signatures = [
        s for s in sig_24h
        if (s['task_name'], s['error_type']) not in sig_prior_7d_keys
    ]

    return {
        'window_24h': {
            'since': cutoff_24h.isoformat(),
            'until': now.isoformat(),
            'total': exec_24h_total,
            'failed': exec_24h_failed,
            'fail_rate': round(fail_rate_24h, 6),
            'timeout_failed': timeout_24h,
        },
        'window_7d': {
            'since': cutoff_7d.isoformat(),
            'until': now.isoformat(),
            'total': exec_7d_total,
            'failed': exec_7d_failed,
            'fail_rate': round(fail_rate_7d, 6),
        },
        'delta_vs_7d': round(delta_vs_7d, 6),
        'top_failing_agents_24h': top_failing_agents_24h,
        'agent_7d_failed_counts': agent_7d,
        'top_signatures_24h': sig_24h[:5],
        'new_signatures_24h': new_signatures[:5],
    }


# =============================================================================
# Gate evaluator
# =============================================================================

def evaluate_gate(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate CTO threshold gates. Returns runner-compatible gate dict.

    Severity precedence: critical > high > medium.
    """
    min_total = _env_int('CTO_DIAG_MIN_TOTAL_24H', 50)
    failrate_high = _env_float('CTO_DIAG_FAILRATE_HIGH', 0.06)
    failrate_crit = _env_float('CTO_DIAG_FAILRATE_CRIT', 0.10)
    delta_high = _env_float('CTO_DIAG_DELTA_HIGH', 0.02)
    new_sig_count = _env_int('CTO_DIAG_NEW_SIG_COUNT', 5)
    agent_spike_min = _env_int('CTO_DIAG_AGENT_SPIKE_MIN', 5)

    reasons: List[str] = []
    details: List[str] = []
    severities: List[str] = []

    w24 = metrics['window_24h']
    total_24h = w24['total']
    fail_rate_24h = w24['fail_rate']
    delta = metrics['delta_vs_7d']

    # Denominator guard
    if total_24h < min_total:
        return {
            'tripped': False,
            'severity': None,
            'reasons': ['INSUFFICIENT_DATA'],
            'reason_details': [
                f'Only {total_24h} executions in last 24h '
                f'(min {min_total} required to evaluate global gates)'
            ],
        }

    # Global fail-rate gates
    if fail_rate_24h >= failrate_crit:
        reasons.append('GLOBAL_FAILRATE_CRIT')
        details.append(
            f'Global failure rate {fail_rate_24h * 100:.1f}% >= '
            f'critical threshold {failrate_crit * 100:.1f}% (n={total_24h})'
        )
        severities.append('critical')
    elif fail_rate_24h >= failrate_high:
        reasons.append('GLOBAL_FAILRATE_HIGH')
        details.append(
            f'Global failure rate {fail_rate_24h * 100:.1f}% >= '
            f'high threshold {failrate_high * 100:.1f}% (n={total_24h})'
        )
        severities.append('high')

    if delta >= delta_high:
        reasons.append('DELTA_VS_7D_HIGH')
        details.append(
            f'Failure rate +{delta * 100:.1f}pp vs 7d baseline '
            f'(24h {fail_rate_24h * 100:.1f}% vs '
            f'7d {metrics["window_7d"]["fail_rate"] * 100:.1f}%)'
        )
        severities.append('high')

    # Per-agent spike gate
    agent_7d = metrics['agent_7d_failed_counts']
    spiking_agents: List[Dict[str, Any]] = []
    total_failed_24h = w24['failed']
    for row in metrics['top_failing_agents_24h']:
        name = row['agent__name'] or 'Unknown'
        cnt = row['count']
        baseline_daily_avg = (agent_7d.get(name, 0) / 7.0) if agent_7d.get(name) else 0
        spike_floor = max(3, 3 * baseline_daily_avg)
        if cnt >= agent_spike_min and cnt >= spike_floor:
            share_of_failures = (cnt / total_failed_24h) if total_failed_24h else 0
            spiking_agents.append({
                'agent': name,
                'count_24h': cnt,
                'baseline_daily_avg_7d': round(baseline_daily_avg, 2),
                'share_of_failures': round(share_of_failures, 3),
            })
            sev = 'high' if share_of_failures >= 0.20 else 'medium'
            severities.append(sev)
    if spiking_agents:
        reasons.append('AGENT_SPIKE')
        details.append(
            'Agent failure spikes: '
            + ', '.join(
                f'{a["agent"]}({a["count_24h"]}, '
                f'{a["share_of_failures"] * 100:.0f}% of fails)'
                for a in spiking_agents[:3]
            )
        )

    # New signature gate
    new_sigs_over_threshold = [
        s for s in metrics['new_signatures_24h'] if s['count'] >= new_sig_count
    ]
    if len(new_sigs_over_threshold) >= 2:
        reasons.append('NEW_SIGNATURE_CRIT')
        details.append(
            f'{len(new_sigs_over_threshold)} new failure signatures '
            f'each >= {new_sig_count} occurrences in 24h: '
            + ', '.join(
                f'{s["task_name"]}/{s["error_type"]}({s["count"]})'
                for s in new_sigs_over_threshold[:3]
            )
        )
        severities.append('critical')
    elif len(new_sigs_over_threshold) == 1:
        s = new_sigs_over_threshold[0]
        reasons.append('NEW_SIGNATURE_HIGH')
        details.append(
            f'New failure signature {s["task_name"]}/{s["error_type"]} '
            f'with {s["count"]} occurrences in 24h '
            f'(>= {new_sig_count} threshold)'
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
        'spiking_agents': spiking_agents,
        'new_signatures': new_sigs_over_threshold,
    }


# =============================================================================
# Dedupe payload builder
# =============================================================================

def build_dedupe_payload(
    metrics: Dict[str, Any],
    gate: Dict[str, Any],
    date_bucket: str,
) -> Dict[str, Any]:
    """Stable fingerprint for 'same-shape diagnostic already posted today'.

    Tolerant to small reordering of top-N lists (sort_keys applied at hash
    time by the runner).
    """
    return {
        'date_bucket': date_bucket,
        'severity': gate.get('severity'),
        'gate_reasons': sorted(gate.get('reasons', [])),
        'fail_rate_24h': round(metrics['window_24h']['fail_rate'], 3),
        'delta_vs_7d': round(metrics['delta_vs_7d'], 3),
        'top_agents': [
            (r['agent__name'] or 'Unknown', r['count'])
            for r in metrics['top_failing_agents_24h'][:5]
        ],
        'top_signatures': [
            (s['task_name'], s['error_type'], s['count'])
            for s in metrics['top_signatures_24h'][:5]
        ],
    }


# =============================================================================
# Prompt builder
# =============================================================================

def build_agent_prompt(metrics: Dict[str, Any], gate: Dict[str, Any]) -> str:
    """Compact metrics bundle + explicit ask for CTOAgent."""
    bundle = {
        'window_24h': metrics['window_24h'],
        'window_7d': metrics['window_7d'],
        'delta_vs_7d': metrics['delta_vs_7d'],
        'top_failing_agents': metrics['top_failing_agents_24h'][:5],
        'top_signatures_24h': metrics['top_signatures_24h'],
        'new_signatures_24h': metrics['new_signatures_24h'],
        'gate': {
            'severity': gate['severity'],
            'reasons': gate['reasons'],
            'details': gate['reason_details'],
        },
    }
    return (
        'You are running the daily CTO platform reliability diagnostic. '
        'The threshold gate has tripped — produce a structured incident report.\n\n'
        'METRICS BUNDLE (live data, do not invent numbers):\n'
        '```json\n'
        f'{json.dumps(bundle, indent=2, default=str)}\n'
        '```\n\n'
        'Output sections (markdown, in this order):\n'
        '1. **Severity:** restate the gate severity\n'
        '2. **Headline:** one-sentence summary of the most acute regression\n'
        '3. **Top failure clusters:** bulleted list, root-cause hypothesis '
        'for each (1-2 sentences max)\n'
        '4. **Recommended actions:** max 3 concrete next steps with owner '
        'hints (e.g., "investigate agent_router heartbeat", '
        '"review CTOAgent timeout ladder")\n'
        '5. **Confidence:** low/medium/high — how confident are you in the '
        'root-cause hypotheses given only the bundle\n\n'
        'Do not editorialize beyond the data. Cite the exact metric numbers '
        'you reference. Do not exceed 600 words.'
    )


# =============================================================================
# Headline + title builders
# =============================================================================

def build_headline(metrics: Dict[str, Any], gate: Dict[str, Any]) -> str:
    severity = (gate.get('severity') or 'UNKNOWN').upper()
    headline_reason = gate['reasons'][0] if gate.get('reasons') else 'gate_tripped'
    return (
        f'{severity} — fail24h '
        f'{metrics["window_24h"]["fail_rate"] * 100:.1f}% '
        f'(Δ{metrics["delta_vs_7d"] * 100:+.1f}pp vs 7d) — '
        f'primary trigger: `{headline_reason}`'
    )


def build_title(metrics: Dict[str, Any], gate: Dict[str, Any], date_label: str) -> str:
    severity = (gate.get('severity') or 'UNKNOWN').upper()
    return (
        f'CTO Daily Diagnostic — '
        f'{date_label} — '
        f'{severity} — '
        f'fail24h {metrics["window_24h"]["fail_rate"] * 100:.1f}% '
        f'(Δ{metrics["delta_vs_7d"] * 100:+.1f}pp)'
    )


# =============================================================================
# Section renderers (for Template v1 extra_sections)
# =============================================================================

def render_24h_metrics(metrics: Dict[str, Any], gate: Dict[str, Any]) -> List[str]:
    return [
        f'- Total executions: {metrics["window_24h"]["total"]}',
        f'- Failed: {metrics["window_24h"]["failed"]} '
        f'({metrics["window_24h"]["fail_rate"] * 100:.2f}%)',
        f'- Δ vs 7d baseline: '
        f'{metrics["delta_vs_7d"] * 100:+.2f}pp '
        f'(7d rate {metrics["window_7d"]["fail_rate"] * 100:.2f}%)',
        f'- Timeout failures: {metrics["window_24h"]["timeout_failed"]}',
    ]


def render_top_failing_agents(metrics: Dict[str, Any], gate: Dict[str, Any]) -> List[str]:
    rows = metrics['top_failing_agents_24h'][:5]
    return [f'- {r["agent__name"] or "Unknown"}: {r["count"]}' for r in rows]


def render_top_signatures(metrics: Dict[str, Any], gate: Dict[str, Any]) -> List[str]:
    rows = metrics['top_signatures_24h'][:5]
    return [
        f'- `{s["task_name"]}` / `{s["error_type"]}`: {s["count"]}'
        for s in rows
    ]


def render_new_signatures(metrics: Dict[str, Any], gate: Dict[str, Any]) -> List[str]:
    """Optional section — only renders if there are new signatures."""
    rows = metrics.get('new_signatures_24h') or []
    if not rows:
        return []
    return [
        f'- `{s["task_name"]}` / `{s["error_type"]}`: {s["count"]}'
        for s in rows[:5]
    ]


# =============================================================================
# Config object — pre-built, post_task_callable late-bound by tasks.py
# =============================================================================

def build_config():
    """Lazy import of the runner (avoids top-level import cycle in tasks.py).

    tasks.py calls this after its `@shared_task` wrappers are defined,
    then assigns the post wrapper to `CTO_CONFIG.post_task_callable`.
    """
    from core.services.scheduled_diagnostic_runner import DiagnosticConfig

    return DiagnosticConfig(
        name='cto_daily_diagnostic',
        diagnostic_type='cto_daily_diagnostic',
        agent_name='CTOAgent',
        source_agent='CTOAgent',
        log_prefix='CTO-DIAG',
        metrics_collector=collect_metrics,
        gate_evaluator=evaluate_gate,
        prompt_builder=build_agent_prompt,
        dedupe_payload_builder=build_dedupe_payload,
        headline_builder=build_headline,
        title_builder=build_title,
        extra_sections=[
            ('24h Metrics', render_24h_metrics),
            ('Top Failing Agents (24h)', render_top_failing_agents),
            ('Top Failure Signatures (24h)', render_top_signatures),
            ('New Failure Signatures (24h)', render_new_signatures),
        ],
        post_task_import_path='core.tasks:post_cto_daily_diagnostic',
        enabled_env='CTO_DIAGNOSTIC_ENABLED',
        posting_enabled_env='CTO_DIAGNOSTIC_POSTING_ENABLED',
        cache_key_prefix='cto_diag',
        workspace_id_env='CTO_DIAG_WORKSPACE_ID',
        # CTO-specific override — queue env var from Session 1093
        queue=os.environ.get('CTO_DIAG_QUEUE', 'long_running'),
    )
