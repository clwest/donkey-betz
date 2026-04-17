"""
TrendAnalysisAgent daily spider-intelligence anomaly diagnostic.
================================================================

Third consumer of `core.services.scheduled_diagnostic_runner` (after
CTOAgent and COOAgent). Chosen per Rigby's ranking: the metrics surface
(distributional anomaly / cluster velocity / spider coverage /
concentration) is structurally different from both CTO (rollup counts
+ fail rates) and COO (throughput + aging SLAs), which stress-tests
the primitive's ability to handle non-SLA, non-throughput diagnostics.

Metrics shape
-------------

    {
        'spider_volume': {
            'records_24h', 'records_7d', 'records_7d_avg_daily',
            'volume_delta_pct',
            'by_data_type_24h', 'by_spider_24h',
        },
        'spider_coverage': {
            'active_7d_count', 'active_24h_count',
            'silent_in_24h_count', 'silent_spiders': [...],
        },
        'concentration': {
            'top_spider_name', 'top_spider_count', 'top_spider_share',
            'herfindahl_index',
        },
        'clusters': {
            'new_24h', 'new_7d', 'new_7d_avg_daily',
            'velocity_ratio',
            'by_pattern_type_24h', 'by_pattern_type_7d',
            'novel_patterns_24h': [...],
        },
    }

Gates
-----

    VOLUME_DROP_HIGH        24h vol < 50% of 7d avg AND abs >= 20 floor
    VOLUME_DROP_CRIT        24h vol < 20% of 7d avg AND abs >= 20 floor
    SILENT_SPIDERS_HIGH     >= 5 previously-active spiders silent in 24h
    CONCENTRATION_HIGH      top spider's share of 24h volume >= 60%
    CLUSTER_VELOCITY_HIGH   new_clusters_24h >= 3x 7d daily avg
    CLUSTER_VELOCITY_CRIT   new_clusters_24h >= 5x 7d daily avg
    NOVEL_PATTERN_HIGH      new SignalCluster pattern_type absent from 7d baseline

Feature flags (both OFF by default)
    TREND_DIAGNOSTIC_ENABLED
    TREND_DIAGNOSTIC_POSTING_ENABLED

Tunables
    TREND_DIAG_VOLUME_DROP_PCT_HIGH    (0.50)
    TREND_DIAG_VOLUME_DROP_PCT_CRIT    (0.80)
    TREND_DIAG_VOLUME_ABS_FLOOR        (20)
    TREND_DIAG_SILENT_SPIDER_MIN       (5)
    TREND_DIAG_CONCENTRATION_PCT       (0.60)
    TREND_DIAG_CLUSTER_SURGE_HIGH      (3.0)
    TREND_DIAG_CLUSTER_SURGE_CRIT      (5.0)
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


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

def _herfindahl(shares: List[float]) -> float:
    """Herfindahl concentration index. 1.0 = monopoly, 0 = perfect diversity.

    Shares should be fractions of the whole (sum <= 1.0).
    """
    return round(sum(s * s for s in shares), 4)


def collect_metrics(now: datetime, cutoff_24h: datetime, cutoff_7d: datetime) -> Dict[str, Any]:
    """Collect TrendAnalysis-flavored distributional metrics from SpiderData +
    SignalCluster.
    """
    from django.db.models import Count
    from core.models import SignalCluster
    from core.models_unified_system import SpiderData

    # ── Spider volume (records ingested)
    records_24h = SpiderData.objects.filter(created_at__gte=cutoff_24h).count()
    records_7d = SpiderData.objects.filter(created_at__gte=cutoff_7d).count()
    records_7d_avg_daily = records_7d / 7.0

    volume_delta_pct = (
        (records_24h - records_7d_avg_daily) / records_7d_avg_daily
        if records_7d_avg_daily > 0 else 0.0
    )

    by_data_type_24h = dict(
        SpiderData.objects.filter(created_at__gte=cutoff_24h)
        .values('data_type').annotate(c=Count('id'))
        .values_list('data_type', 'c')
    )
    by_spider_24h_rows = list(
        SpiderData.objects.filter(created_at__gte=cutoff_24h)
        .values('spider_name').annotate(c=Count('id'))
        .order_by('-c')
    )
    by_spider_24h = {r['spider_name']: r['c'] for r in by_spider_24h_rows}

    spider_volume = {
        'records_24h': records_24h,
        'records_7d': records_7d,
        'records_7d_avg_daily': round(records_7d_avg_daily, 2),
        'volume_delta_pct': round(volume_delta_pct, 4),
        'by_data_type_24h': by_data_type_24h,
        'by_spider_24h_top': by_spider_24h_rows[:10],
    }

    # ── Spider coverage (silence detection)
    active_7d_set = set(
        SpiderData.objects.filter(created_at__gte=cutoff_7d)
        .values_list('spider_name', flat=True).distinct()
    )
    active_24h_set = set(by_spider_24h.keys())
    silent_in_24h = sorted(active_7d_set - active_24h_set)

    spider_coverage = {
        'active_7d_count': len(active_7d_set),
        'active_24h_count': len(active_24h_set),
        'silent_in_24h_count': len(silent_in_24h),
        'silent_spiders': silent_in_24h[:15],
    }

    # ── Concentration (Herfindahl + top-spider share)
    if records_24h > 0 and by_spider_24h_rows:
        shares = [r['c'] / records_24h for r in by_spider_24h_rows]
        top = by_spider_24h_rows[0]
        concentration = {
            'top_spider_name': top['spider_name'],
            'top_spider_count': top['c'],
            'top_spider_share': round(top['c'] / records_24h, 4),
            'herfindahl_index': _herfindahl(shares),
        }
    else:
        concentration = {
            'top_spider_name': None,
            'top_spider_count': 0,
            'top_spider_share': 0.0,
            'herfindahl_index': 0.0,
        }

    # ── Clusters (SignalCluster velocity + novelty)
    new_clusters_24h = SignalCluster.objects.filter(detected_at__gte=cutoff_24h).count()
    new_clusters_7d = SignalCluster.objects.filter(detected_at__gte=cutoff_7d).count()
    new_clusters_7d_avg_daily = new_clusters_7d / 7.0

    velocity_ratio = (
        new_clusters_24h / new_clusters_7d_avg_daily
        if new_clusters_7d_avg_daily > 0 else 0.0
    )

    by_pattern_type_24h = dict(
        SignalCluster.objects.filter(detected_at__gte=cutoff_24h)
        .values('pattern_type').annotate(c=Count('id'))
        .values_list('pattern_type', 'c')
    )
    # 7d baseline pattern set — anything seen in 7d prior to last 24h
    prior_7d_patterns = set(
        SignalCluster.objects.filter(
            detected_at__gte=cutoff_7d, detected_at__lt=cutoff_24h
        ).values_list('pattern_type', flat=True).distinct()
    )
    novel_patterns_24h = sorted(
        pt for pt in by_pattern_type_24h.keys()
        if pt and pt not in prior_7d_patterns
    )

    clusters = {
        'new_24h': new_clusters_24h,
        'new_7d': new_clusters_7d,
        'new_7d_avg_daily': round(new_clusters_7d_avg_daily, 2),
        'velocity_ratio': round(velocity_ratio, 2),
        'by_pattern_type_24h': by_pattern_type_24h,
        'prior_7d_pattern_count': len(prior_7d_patterns),
        'novel_patterns_24h': novel_patterns_24h,
    }

    return {
        'window_24h': {'since': cutoff_24h.isoformat(), 'until': now.isoformat()},
        'window_7d': {'since': cutoff_7d.isoformat(), 'until': now.isoformat()},
        'spider_volume': spider_volume,
        'spider_coverage': spider_coverage,
        'concentration': concentration,
        'clusters': clusters,
    }


# =============================================================================
# Gate evaluator
# =============================================================================

def evaluate_gate(metrics: Dict[str, Any]) -> Dict[str, Any]:
    volume_drop_pct_high = _env_float('TREND_DIAG_VOLUME_DROP_PCT_HIGH', 0.50)
    volume_drop_pct_crit = _env_float('TREND_DIAG_VOLUME_DROP_PCT_CRIT', 0.80)
    volume_abs_floor = _env_int('TREND_DIAG_VOLUME_ABS_FLOOR', 20)
    silent_spider_min = _env_int('TREND_DIAG_SILENT_SPIDER_MIN', 5)
    concentration_pct = _env_float('TREND_DIAG_CONCENTRATION_PCT', 0.60)
    cluster_surge_high = _env_float('TREND_DIAG_CLUSTER_SURGE_HIGH', 3.0)
    cluster_surge_crit = _env_float('TREND_DIAG_CLUSTER_SURGE_CRIT', 5.0)

    reasons: List[str] = []
    details: List[str] = []
    severities: List[str] = []

    volume = metrics['spider_volume']
    coverage = metrics['spider_coverage']
    concentration = metrics['concentration']
    clusters = metrics['clusters']

    # ── Volume drop (absolute-floor guard per Rigby's pattern)
    #    Baseline must be >= floor for % drop to mean anything
    records_24h = volume['records_24h']
    baseline = volume['records_7d_avg_daily']
    drop_pct = -volume['volume_delta_pct'] if volume['volume_delta_pct'] < 0 else 0
    if baseline >= volume_abs_floor:
        if drop_pct >= volume_drop_pct_crit:
            reasons.append('VOLUME_DROP_CRIT')
            details.append(
                f'Spider volume dropped {drop_pct * 100:.0f}% '
                f'(24h {records_24h} vs 7d avg {baseline:.1f}/day, '
                f'floor {volume_abs_floor}) — severe pipeline failure suspected'
            )
            severities.append('critical')
        elif drop_pct >= volume_drop_pct_high:
            reasons.append('VOLUME_DROP_HIGH')
            details.append(
                f'Spider volume dropped {drop_pct * 100:.0f}% '
                f'(24h {records_24h} vs 7d avg {baseline:.1f}/day, '
                f'floor {volume_abs_floor})'
            )
            severities.append('high')

    # ── Silent spiders (coverage gaps)
    if coverage['silent_in_24h_count'] >= silent_spider_min:
        reasons.append('SILENT_SPIDERS_HIGH')
        details.append(
            f'{coverage["silent_in_24h_count"]} of '
            f'{coverage["active_7d_count"]} 7d-active spiders silent in 24h '
            f'(min {silent_spider_min} for HIGH). '
            f'Top silent: {", ".join(coverage["silent_spiders"][:5])}'
        )
        severities.append('high')

    # ── Concentration (over-reliance on one spider)
    if concentration['top_spider_share'] >= concentration_pct:
        reasons.append('CONCENTRATION_HIGH')
        details.append(
            f'Top spider `{concentration["top_spider_name"]}` = '
            f'{concentration["top_spider_share"] * 100:.0f}% of 24h volume '
            f'(threshold {concentration_pct * 100:.0f}%). '
            f'Herfindahl {concentration["herfindahl_index"]:.3f}'
        )
        severities.append('high')

    # ── Cluster velocity (pattern emergence surge)
    #    Only meaningful when baseline is nonzero
    if clusters['new_7d_avg_daily'] > 0:
        ratio = clusters['velocity_ratio']
        if ratio >= cluster_surge_crit:
            reasons.append('CLUSTER_VELOCITY_CRIT')
            details.append(
                f'SignalCluster velocity {ratio:.1f}x baseline '
                f'(24h {clusters["new_24h"]} vs 7d avg {clusters["new_7d_avg_daily"]:.1f}/day). '
                f'Major pattern emergence or clustering explosion'
            )
            severities.append('critical')
        elif ratio >= cluster_surge_high:
            reasons.append('CLUSTER_VELOCITY_HIGH')
            details.append(
                f'SignalCluster velocity {ratio:.1f}x baseline '
                f'(24h {clusters["new_24h"]} vs 7d avg {clusters["new_7d_avg_daily"]:.1f}/day)'
            )
            severities.append('high')

    # ── Novel pattern types
    if clusters['novel_patterns_24h']:
        reasons.append('NOVEL_PATTERN_HIGH')
        details.append(
            f'{len(clusters["novel_patterns_24h"])} new pattern_type(s) '
            f'in 24h not seen in prior 7d: '
            f'{", ".join(clusters["novel_patterns_24h"][:5])}'
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
    volume = metrics.get('spider_volume', {})
    coverage = metrics.get('spider_coverage', {})
    concentration = metrics.get('concentration', {})
    clusters = metrics.get('clusters', {})
    return {
        'date_bucket': date_bucket,
        'severity': gate.get('severity'),
        'gate_reasons': sorted(gate.get('reasons', [])),
        # Round continuous fields so tiny fluctuations don't change the hash
        'volume_delta_bucket': round(volume.get('volume_delta_pct', 0), 1),
        'silent_count': coverage.get('silent_in_24h_count'),
        # 10% buckets for concentration — 60% and 64% are "same shape"
        'concentration_bucket': round(concentration.get('top_spider_share', 0), 1),
        # 0.5x ratio buckets for velocity
        'velocity_ratio_bucket': round(clusters.get('velocity_ratio', 0) * 2) / 2,
        'novel_pattern_count': len(clusters.get('novel_patterns_24h', [])),
    }


# =============================================================================
# Prompt builder
# =============================================================================

def build_agent_prompt(metrics: Dict[str, Any], gate: Dict[str, Any]) -> str:
    bundle = {
        'spider_volume': metrics['spider_volume'],
        'spider_coverage': metrics['spider_coverage'],
        'concentration': metrics['concentration'],
        'clusters': metrics['clusters'],
        'gate': {
            'severity': gate['severity'],
            'reasons': gate['reasons'],
            'details': gate['reason_details'],
        },
    }
    return (
        'You are running the daily TrendAnalysis spider-intelligence anomaly '
        'diagnostic. The threshold gate has tripped — produce a structured '
        'anomaly report in your characteristic analyst voice.\n\n'
        'METRICS BUNDLE (live data from SpiderData + SignalCluster tables — '
        'do not invent numbers):\n'
        '```json\n'
        f'{json.dumps(bundle, indent=2, default=str)}\n'
        '```\n\n'
        'Output sections (markdown, in this order):\n'
        '1. **Severity:** restate the gate severity\n'
        '2. **Headline:** one-sentence summary of the most acute anomaly\n'
        '3. **Root-cause hypotheses:** max 3 bullets — for each anomaly '
        'named in the gate, propose 1-2 sentence hypothesis grounded in the '
        'metrics (spider pipeline failure? viral event? scheduler issue? '
        'genuine market shift?). Distinguish clearly between data-pipeline '
        'issues (silent spiders, volume drops) and signal-quality issues '
        '(concentration, cluster surge).\n'
        '4. **Recommended actions:** max 3 concrete next steps. Prefer '
        'diagnostic actions over remediation (e.g., "inspect spider X logs '
        'for rate-limiting", "verify scheduler running for spiders '
        '{silent_list}", "review SignalCluster pattern X for root signal").\n'
        '5. **Confidence:** low/medium/high — how confident are you in the '
        'root-cause hypotheses given only the bundle\n\n'
        'Cite the exact metric numbers you reference. Do not exceed 500 words.'
    )


# =============================================================================
# Headline + title
# =============================================================================

def build_headline(metrics: Dict[str, Any], gate: Dict[str, Any]) -> str:
    severity = (gate.get('severity') or 'UNKNOWN').upper()
    reason = gate['reasons'][0] if gate.get('reasons') else 'gate_tripped'
    volume = metrics.get('spider_volume', {})
    coverage = metrics.get('spider_coverage', {})
    return (
        f'{severity} — '
        f'vol24h {volume.get("records_24h", 0)} '
        f'(Δ {volume.get("volume_delta_pct", 0) * 100:+.0f}%), '
        f'{coverage.get("silent_in_24h_count", 0)} silent spiders — '
        f'primary trigger: `{reason}`'
    )


def build_title(metrics: Dict[str, Any], gate: Dict[str, Any], date_label: str) -> str:
    severity = (gate.get('severity') or 'UNKNOWN').upper()
    volume = metrics.get('spider_volume', {})
    return (
        f'TrendAnalysis Daily Anomaly — '
        f'{date_label} — '
        f'{severity} — '
        f'vol {volume.get("records_24h", 0)} '
        f'(Δ{volume.get("volume_delta_pct", 0) * 100:+.0f}%)'
    )


# =============================================================================
# Section renderers
# =============================================================================

def render_spider_volume(metrics: Dict[str, Any], gate: Dict[str, Any]) -> List[str]:
    v = metrics['spider_volume']
    lines = [
        f'- Records (24h): **{v["records_24h"]}** vs 7d avg '
        f'{v["records_7d_avg_daily"]:.1f}/day '
        f'(Δ {v["volume_delta_pct"] * 100:+.1f}%)',
    ]
    if v.get('by_data_type_24h'):
        lines.append('')
        lines.append('Breakdown by data_type:')
        for dt, cnt in sorted(
            v['by_data_type_24h'].items(), key=lambda kv: -kv[1]
        )[:8]:
            lines.append(f'  - {dt}: {cnt}')
    return lines


def render_spider_coverage(metrics: Dict[str, Any], gate: Dict[str, Any]) -> List[str]:
    c = metrics['spider_coverage']
    lines = [
        f'- 7d-active spiders: **{c["active_7d_count"]}**',
        f'- 24h-active spiders: **{c["active_24h_count"]}**',
        f'- Silent in 24h: **{c["silent_in_24h_count"]}**',
    ]
    if c.get('silent_spiders'):
        lines.append('')
        lines.append('Silent spider names:')
        for name in c['silent_spiders'][:10]:
            lines.append(f'  - `{name}`')
    return lines


def render_concentration(metrics: Dict[str, Any], gate: Dict[str, Any]) -> List[str]:
    c = metrics['concentration']
    if not c.get('top_spider_name'):
        return ['- No 24h spider activity to measure concentration']
    return [
        f'- Top spider: `{c["top_spider_name"]}` '
        f'({c["top_spider_count"]} records, '
        f'{c["top_spider_share"] * 100:.0f}% of 24h volume)',
        f'- Herfindahl index: **{c["herfindahl_index"]:.3f}** '
        f'(1.0 = monopoly, lower = diverse)',
    ]


def render_clusters(metrics: Dict[str, Any], gate: Dict[str, Any]) -> List[str]:
    c = metrics['clusters']
    lines = [
        f'- New SignalClusters (24h): **{c["new_24h"]}** vs 7d avg '
        f'{c["new_7d_avg_daily"]:.1f}/day '
        f'(velocity {c["velocity_ratio"]:.1f}x)',
    ]
    if c.get('by_pattern_type_24h'):
        lines.append('')
        lines.append('24h pattern breakdown:')
        for pt, cnt in sorted(
            c['by_pattern_type_24h'].items(), key=lambda kv: -kv[1]
        )[:8]:
            marker = ' **(NEW)**' if pt in (c.get('novel_patterns_24h') or []) else ''
            lines.append(f'  - `{pt or "(none)"}`: {cnt}{marker}')
    return lines


# =============================================================================
# Config
# =============================================================================

def build_config():
    from core.services.scheduled_diagnostic_runner import DiagnosticConfig

    return DiagnosticConfig(
        name='trend_daily_diagnostic',
        diagnostic_type='trend_daily_diagnostic',
        agent_name='TrendAnalysisAgent',
        source_agent='TrendAnalysisAgent',
        log_prefix='TREND-DIAG',
        metrics_collector=collect_metrics,
        gate_evaluator=evaluate_gate,
        prompt_builder=build_agent_prompt,
        dedupe_payload_builder=build_dedupe_payload,
        headline_builder=build_headline,
        title_builder=build_title,
        extra_sections=[
            ('Spider Volume (24h)', render_spider_volume),
            ('Spider Coverage', render_spider_coverage),
            ('Concentration', render_concentration),
            ('SignalCluster Activity', render_clusters),
        ],
        post_task_import_path='core.tasks:post_trend_daily_diagnostic',
        enabled_env='TREND_DIAGNOSTIC_ENABLED',
        posting_enabled_env='TREND_DIAGNOSTIC_POSTING_ENABLED',
        cache_key_prefix='trend_diag',
        workspace_id_env='TREND_DIAG_WORKSPACE_ID',
        queue=os.environ.get('TREND_DIAG_QUEUE', 'long_running'),
    )
