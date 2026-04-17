"""
Scheduled Diagnostic Runner — generic scheduled-agent-as-monitor primitive.
============================================================================

Session 1094: extracted from the CTOAgent daily-diagnostic implementation
(core/tasks_ops.py, Session 1093 PR #1983). The same shape — periodically
gather live state, gate against thresholds, dispatch an agent for narrative
synthesis, post via attention bridge with dedupe + cooldown — applies to
many other agents (COOAgent, PlatformAuditAgent, TrendAnalysisAgent,
MarketIntelligenceAgent, etc).

Two-task pattern (the critical design constraint)
-------------------------------------------------

Never `.get(timeout=N)` inside a Celery task — ties up a worker slot for
the LLM call duration. Instead:

  Task A (run_<name>)
    1. Check feature flag → skip if disabled
    2. Collect metrics via config.metrics_collector
    3. Evaluate gate via config.gate_evaluator
    4. If not tripped → return 'clear' (no agent, no post)
    5. Dedupe + cooldown check → return 'gated' if either hit
    6. Dispatch config.agent_name ASYNC (no blocking .get())
    7. If POSTING_ENABLED → enqueue Task B with countdown=agent_timeout+slack
       else                → return 'log_only' (observation mode)

  Task B (post_<name>)
    1. Idempotence guard via posted_key — skip if already posted
    2. AsyncResult.ready()-check Task A's dispatch
    3. Load narrative if present; if absent, post with "narrative unavailable"
    4. Compose body via Template v1 (locked headings, Recommended Actions cap)
    5. Apply payload size cap (16 KB default) with 3-stage trim
    6. Post via attention_bridge.create_diagnostic_alert()
    7. Set posted_key marker (48h TTL)

This module exposes `run_diagnostic(config)` and `post_diagnostic(config, ...)`
as generic entry points. Each diagnostic defines its own `DiagnosticConfig`
object and thin `@shared_task` wrappers in core/tasks.py that call
these two functions.

Why config objects instead of class hierarchies
------------------------------------------------

Every diagnostic needs the same orchestration shape but totally different
data. Metrics shape for CTOAgent is `{window_24h: {total, failed, ...}}`;
for a TrendAnalysisAgent diagnostic it'd be `{signal_clusters: [...],
anomaly_scores: [...]}`. A class hierarchy would force base-class
abstractions that don't fit. A config object (callables + constants)
keeps the runner as a pure function and the variability as data.

Feature flags (per-diagnostic)
------------------------------

- `<NAME>_ENABLED` — gates whole task (both run_ and post_). OFF-by-default.
- `<NAME>_POSTING_ENABLED` — gates the governance post only. Lets a
  diagnostic run in "observation mode" (compute + dispatch + log) without
  actually landing attention items. OFF-by-default.

Both flags read from `settings.<NAME>` first then fall back to `os.environ.
<NAME>`, so Django settings overrides dev env vars.

Template v1 (locked body shape — do not change without new version)
-------------------------------------------------------------------

    ## Headline
    <1 line — severity + primary metric + delta + #1 reason>

    ## Severity & Gate Reasons
    - Severity: <level>
    - <gate_reasons: one bullet per reason>

    ## <diagnostic's primary-metric section>       (config.extra_sections)
    ...

    [## Optional additional sections]              (config.extra_sections)

    ## <Agent>Analysis
    <agent narrative — LLM output>

    ## Recommended Actions (max 3)
    <extracted from narrative, hard-capped>

The first two sections + Recommended Actions are FIXED. Everything between
is config.extra_sections (list of (heading, render_fn)).

See SESSION_1094_SCHEDULED_DIAGNOSTIC_RUNNER.md for the rollout plan.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# Config dataclass
# =============================================================================

# Type aliases for clarity
MetricsCollector = Callable[[datetime, datetime, datetime], Dict[str, Any]]
# (now, cutoff_24h, cutoff_7d) -> metrics dict
#
# cutoff_24h and cutoff_7d are passed even when the diagnostic only uses one
# window, because many diagnostics need both for delta computation and it's
# cheaper to compute them in the runner than in every collector.

GateEvaluator = Callable[[Dict[str, Any]], Dict[str, Any]]
# metrics -> {tripped: bool, severity: str | None, reasons: list[str],
#             reason_details: list[str], ...extra_gate_fields}
#
# Severity must be one of: 'critical' | 'high' | 'medium' | None. Extra
# fields (e.g., spiking_agents for CTO) are preserved in the final payload.

PromptBuilder = Callable[[Dict[str, Any], Dict[str, Any]], str]
# (metrics, gate) -> agent prompt string

DedupePayloadBuilder = Callable[[Dict[str, Any], Dict[str, Any], str], Dict[str, Any]]
# (metrics, gate, date_bucket) -> dict to be hashed for dedupe key
#
# Why a builder instead of just "hash the metrics"? Different diagnostics
# want different slices of the metrics in the dedupe key. For CTO it's
# (date, severity, reasons, rounded rates, top-5 agents, top-5 signatures) —
# small reordering is OK. For a trend-anomaly diagnostic it might be
# (date, anomaly_cluster_id, severity). Keeping this a per-config callable
# avoids overfitting the dedupe shape to CTO's metrics shape.

HeadlineBuilder = Callable[[Dict[str, Any], Dict[str, Any]], str]
# (metrics, gate) -> 1-line headline for Template v1

SectionRenderer = Callable[[Dict[str, Any], Dict[str, Any]], List[str]]
# (metrics, gate) -> list of body lines (already markdown-formatted, no
# leading heading — runner inserts the heading). Return [] to omit the section.

TitleBuilder = Callable[[Dict[str, Any], Dict[str, Any], str], str]
# (metrics, gate, date_label) -> attention item title


@dataclass
class DiagnosticConfig:
    """Configuration for one scheduled diagnostic.

    Minimum required fields: identity (name, diagnostic_type, agent_name),
    behavior callables (metrics_collector, gate_evaluator, prompt_builder,
    dedupe_payload_builder, headline_builder, title_builder), feature flags
    (enabled_env, posting_enabled_env), and the post-task callable reference
    used for enqueueing the follow-up (post_task_callable).

    Everything else has sensible defaults that match the CTOAgent diagnostic
    semantics (36h dedupe TTL, 20h/6h cooldowns, 16 KB payload cap, MT date
    bucket, 240s post countdown, long_running queue).
    """
    # ── Identity ────────────────────────────────────────────────────────────
    name: str                          # short identifier, e.g. 'cto_daily'
    diagnostic_type: str               # attention_bridge type, e.g. 'cto_daily_diagnostic'
    agent_name: str                    # which agent to dispatch, e.g. 'CTOAgent'
    source_agent: str                  # attribution for attention item (usually == agent_name)
    log_prefix: str                    # e.g. 'CTO-DIAG' (wraps to [<prefix>] / [<prefix>-POST])

    # ── Behavior callables ──────────────────────────────────────────────────
    metrics_collector: MetricsCollector
    gate_evaluator: GateEvaluator
    prompt_builder: PromptBuilder
    dedupe_payload_builder: DedupePayloadBuilder
    headline_builder: HeadlineBuilder
    title_builder: TitleBuilder
    # Body sections between Headline/Severity-Reasons and Agent-Analysis.
    # Each tuple is (heading, render_fn). Heading must NOT include leading
    # '#' — the runner adds '## '.
    extra_sections: List[Tuple[str, SectionRenderer]] = field(default_factory=list)

    # ── Follow-up post task reference ───────────────────────────────────────
    # Dotted import path to the Celery-decorated `post_<name>` task, e.g.
    # 'core.tasks:post_cto_daily_diagnostic'. Resolved via importlib at
    # dispatch time — avoids module-import cycles between tasks.py and
    # diagnostic config modules. Required for posting mode; optional in
    # observation-only mode (posting flag OFF).
    post_task_import_path: str = ''

    # ── Feature flags (env var names — the runner reads them) ──────────────
    enabled_env: str = ''              # e.g. 'CTO_DIAGNOSTIC_ENABLED'
    posting_enabled_env: str = ''      # e.g. 'CTO_DIAGNOSTIC_POSTING_ENABLED'

    # ── Reliability (with CTO-matching defaults) ────────────────────────────
    agent_timeout_seconds: int = 180   # LLM timeout for the dispatched agent
    post_countdown_slack_seconds: int = 60   # extra time before post task runs
    agent_task_expires_seconds: int = 3600
    post_task_expires_seconds: int = 3600
    queue: str = 'long_running'

    # ── Gating / posting behavior ───────────────────────────────────────────
    dedupe_ttl_hours: int = 36
    cooldown_high_hours: int = 20      # for severity != 'critical'
    cooldown_critical_hours: int = 6
    posted_marker_ttl_hours: int = 48
    payload_cap_bytes: int = 16 * 1024
    timezone_name: str = 'America/Denver'
    # Namespaced cache key prefix — uses `name` by default.
    cache_key_prefix: str = ''

    # Optional override of the Recommended Actions extractor. Default is
    # the same regex used by CTOAgent (heading + bullet normalization).
    recommended_actions_extractor: Optional[
        Callable[[str, int], List[str]]
    ] = None
    recommended_actions_max: int = 3

    # Optional workspace id for the attention item (None = unassigned).
    workspace_id_env: str = ''

    def __post_init__(self) -> None:
        if not self.cache_key_prefix:
            self.cache_key_prefix = self.name
        if not self.source_agent:
            self.source_agent = self.agent_name


# =============================================================================
# Flag + env helpers
# =============================================================================

def _env_bool(name: str, default: bool = False) -> bool:
    """Read a bool from settings first, then environ. Matches CTO precedence."""
    if not name:
        return default
    try:
        from django.conf import settings
        raw = getattr(settings, name, None)
        if raw is not None:
            return str(raw).lower() in ('1', 'true', 'yes', 'on')
    except Exception:
        pass
    raw_env = os.environ.get(name)
    if raw_env is None:
        return default
    return raw_env.lower() in ('1', 'true', 'yes', 'on')


def _env_value(name: str) -> Optional[str]:
    """Settings-first, env-fallback string read. Returns None if unset in both."""
    if not name:
        return None
    try:
        from django.conf import settings
        raw = getattr(settings, name, None)
        if raw is not None:
            return str(raw)
    except Exception:
        pass
    return os.environ.get(name)


# =============================================================================
# Default Recommended Actions extractor (shared default; overridable per config)
# =============================================================================

_RECOMMENDED_HEADING_RE = re.compile(
    r'(?:^|\n)\s*(?:#{1,4}\s*|\*\*)?\s*'
    r'recommended\s+actions?'
    r'(?:\s*\(.*?\))?'               # tolerate "(max 3)" suffix
    r'[:\*\s]*\n',                   # trailing colon/asterisk/whitespace then newline
    flags=re.IGNORECASE,
)
_CONFIDENCE_STOP_RE = re.compile(
    r'\n\s*(?:#{1,4}\s*|\*\*)?\s*confidence\b',
    flags=re.IGNORECASE,
)
_NEXT_HEADING_RE = re.compile(r'\n\s*#{1,4}\s+\S')
_BULLET_RE = re.compile(
    r'^\s*(?:[-*]|\d+[.)])\s+(.+?)(?=\n\s*(?:[-*]|\d+[.)])\s+|\Z)',
    flags=re.MULTILINE | re.DOTALL,
)


def default_extract_recommended_actions(narrative: str, max_actions: int = 3) -> List[str]:
    """Pull bullet items from a 'Recommended Actions' section.

    Tolerates:
      - Heading shapes: ## / ### / **Recommended Actions:** / plain
      - Suffix: "(max N)" / nothing
      - Bullet shapes: -, *, 1., 1)

    Stops at:
      - "Confidence" section
      - Next markdown heading

    Returns [] if no recognizable section is found.
    """
    if not narrative:
        return []
    m = _RECOMMENDED_HEADING_RE.search(narrative)
    if not m:
        return []
    section = narrative[m.end():]
    stop = _CONFIDENCE_STOP_RE.search(section)
    if stop:
        section = section[:stop.start()]
    next_heading = _NEXT_HEADING_RE.search(section)
    if next_heading:
        section = section[:next_heading.start()]
    items = [mm.group(1).strip() for mm in _BULLET_RE.finditer(section)]
    cleaned = []
    for it in items:
        normalized = ' '.join(it.split())
        if normalized:
            cleaned.append(normalized)
    return cleaned[:max_actions]


# =============================================================================
# Date-bucket helper
# =============================================================================

def _resolve_import_path(path: str) -> Any:
    """Resolve 'module.path:attribute' into a concrete object.

    Deliberately dotted `:` delimiter instead of `.` to disambiguate
    module-vs-attribute for paths where the last segment could be either
    (e.g. nested task modules).
    """
    if ':' not in path:
        raise ValueError(
            f'import_path must be of form "module.path:attribute" — got {path!r}'
        )
    module_path, attr_name = path.rsplit(':', 1)
    from importlib import import_module
    return getattr(import_module(module_path), attr_name)


def _date_bucket(now: datetime, timezone_name: str) -> str:
    """Local-timezone date bucket for dedupe boundaries (MT by default).

    Dedupe aligns with the operator's working day — the CTO diagnostic
    fires at 7:15 AM MDT, so its dedupe rolls at MT midnight (not UTC
    midnight, which would falsely allow re-posting same-shape diagnostics
    within one "day").
    """
    try:
        import zoneinfo
        return now.astimezone(zoneinfo.ZoneInfo(timezone_name)).strftime('%Y-%m-%d')
    except Exception:
        return now.strftime('%Y-%m-%d')


# =============================================================================
# Dedupe + cooldown
# =============================================================================

def _dedupe_and_cooldown_check(
    config: DiagnosticConfig,
    now: datetime,
    gate: Dict[str, Any],
    metrics: Dict[str, Any],
) -> Dict[str, Any]:
    """Compute dedupe hash + check Redis for prior post within cooldown.

    Returns:
        {
            'should_post': bool,
            'reason': str,
            'dedupe_hash': str,
            'dedupe_key': str,
            'cooldown_key': str,
            'cooldown_hours': int,
            'date_bucket': str,
        }
    """
    from django.core.cache import cache

    severity = gate.get('severity') or 'unknown'
    cooldown_h = (
        config.cooldown_critical_hours if severity == 'critical'
        else config.cooldown_high_hours
    )
    date_bucket = _date_bucket(now, config.timezone_name)

    # Per-config dedupe payload — different diagnostics include different
    # metric slices (see DedupePayloadBuilder docstring).
    dedupe_payload = config.dedupe_payload_builder(metrics, gate, date_bucket)
    dedupe_hash = hashlib.sha256(
        json.dumps(dedupe_payload, sort_keys=True, default=str).encode()
    ).hexdigest()
    prefix = config.cache_key_prefix
    dedupe_key = f'{prefix}:dedupe:{date_bucket}:{dedupe_hash[:12]}'
    cooldown_key = f'{prefix}:cooldown:{severity}'

    if cache.get(dedupe_key):
        return {
            'should_post': False,
            'reason': f'dedupe_hit:{dedupe_hash[:12]}',
            'dedupe_hash': dedupe_hash,
            'dedupe_key': dedupe_key,
            'cooldown_key': cooldown_key,
            'cooldown_hours': cooldown_h,
            'date_bucket': date_bucket,
        }

    if cache.get(cooldown_key):
        return {
            'should_post': False,
            'reason': f'cooldown_active:{severity}:{cooldown_h}h',
            'dedupe_hash': dedupe_hash,
            'dedupe_key': dedupe_key,
            'cooldown_key': cooldown_key,
            'cooldown_hours': cooldown_h,
            'date_bucket': date_bucket,
        }

    return {
        'should_post': True,
        'reason': 'gates_clear',
        'dedupe_hash': dedupe_hash,
        'dedupe_key': dedupe_key,
        'cooldown_key': cooldown_key,
        'cooldown_hours': cooldown_h,
        'date_bucket': date_bucket,
    }


# =============================================================================
# Body composition (Template v1)
# =============================================================================

def _compose_body(
    config: DiagnosticConfig,
    metrics: Dict[str, Any],
    gate: Dict[str, Any],
    narrative: Optional[str],
    narrative_error: Optional[str],
) -> Tuple[str, List[str]]:
    """Compose the attention item body per Template v1.

    Returns (body_markdown, recommended_actions_list).
    """
    severity = (gate.get('severity') or 'UNKNOWN').upper()
    headline = config.headline_builder(metrics, gate)

    lines: List[str] = [
        '## Headline',
        headline,
        '',
        '## Severity & Gate Reasons',
        f'- **Severity:** {severity}',
    ]
    reasons = gate.get('reasons') or []
    details = gate.get('reason_details') or []
    # zip tolerates unequal lengths — pads missing detail with empty string.
    for i, reason in enumerate(reasons):
        detail = details[i] if i < len(details) else ''
        lines.append(f'- `{reason}` — {detail}' if detail else f'- `{reason}`')
    lines.append('')

    # Per-diagnostic extra sections between header and agent analysis.
    for heading, renderer in config.extra_sections:
        try:
            rendered = renderer(metrics, gate)
        except Exception as e:
            logger.exception(
                '[%s] extra section %r renderer failed: %s',
                config.log_prefix, heading, e,
            )
            rendered = [f'_Section renderer failed: {type(e).__name__}_']
        if not rendered:
            continue
        lines.append(f'## {heading}')
        lines.extend(rendered)
        lines.append('')

    # Agent narrative block (or error line if unavailable).
    if narrative:
        lines.extend([
            '---',
            '',
            f'## {config.agent_name} Analysis',
            '',
            narrative,
        ])
    elif narrative_error:
        lines.extend([
            '---',
            '',
            f'_{config.agent_name} narrative unavailable: {narrative_error}_',
        ])

    # Recommended Actions — always last per Template v1.
    extractor = config.recommended_actions_extractor or default_extract_recommended_actions
    actions = extractor(narrative or '', config.recommended_actions_max)
    lines.extend(['', '---', '', f'## Recommended Actions (max {config.recommended_actions_max})'])
    if actions:
        lines.extend(f'{i + 1}. {a}' for i, a in enumerate(actions))
    else:
        lines.append(
            f'_None extracted from {config.agent_name} narrative — review the '
            f'analysis above for next steps._'
        )

    return '\n'.join(lines), actions


# =============================================================================
# Payload cap
# =============================================================================

def _apply_payload_cap(
    payload: Dict[str, Any],
    cap_bytes: int,
) -> Dict[str, Any]:
    """3-stage trim to fit under cap_bytes. Mutates a copy of payload."""
    trimmed = dict(payload)

    def _size(p: Dict[str, Any]) -> int:
        try:
            return len(json.dumps(p, default=str))
        except Exception:
            return cap_bytes + 1

    if _size(trimmed) <= cap_bytes:
        return trimmed

    # Stage 1: trim list fields to top-5
    for k in list(trimmed.keys()):
        v = trimmed.get(k)
        if isinstance(v, list) and len(v) > 5:
            trimmed[k] = v[:5]

    # Stage 2: truncate long string fields
    for k in ('error', 'dispatch_error', 'agent_error', 'cto_error', 'narrative'):
        v = trimmed.get(k)
        if isinstance(v, str) and len(v) > 1024:
            trimmed[k] = v[:1024] + '... [truncated]'

    # Stage 3: drop optional list fields
    if _size(trimmed) > cap_bytes:
        for k in ('new_signatures_24h', 'spiking_agents', 'top_signatures_24h'):
            trimmed.pop(k, None)
        trimmed['_payload_truncated'] = True

    return trimmed


# =============================================================================
# Runner — Task A (run_<name>)
# =============================================================================

def run_diagnostic(config: DiagnosticConfig) -> Dict[str, Any]:
    """Generic run-phase: feature flag → metrics → gate → dedupe → dispatch → enqueue post.

    Returns a status dict. Status values:
      - 'skipped'                — feature flag OFF
      - 'error'                  — metrics collection crashed
      - 'clear'                  — gate not tripped
      - 'gated_by_dedupe_or_cooldown'
      - 'log_only'               — posting flag OFF (observation mode)
      - 'dispatched'             — agent dispatched + post enqueued
      - 'enqueue_failed'         — post enqueue crashed

    Callers should treat the dict as opaque logging payload — only 'dispatched'
    actually creates user-visible effects.
    """
    from django.core.cache import cache
    from django.utils import timezone
    from datetime import timedelta

    prefix = config.log_prefix

    if not _env_bool(config.enabled_env, default=False):
        logger.info('[%s] %s=false — skipping', prefix, config.enabled_env)
        return {'status': 'skipped', 'reason': 'disabled'}

    posting_enabled = _env_bool(config.posting_enabled_env, default=False)

    now = timezone.now()
    cutoff_24h = now - timedelta(hours=24)
    cutoff_7d = now - timedelta(days=7)

    # ── 1. Collect metrics
    try:
        metrics = config.metrics_collector(now, cutoff_24h, cutoff_7d)
    except Exception as e:
        logger.exception('[%s] metrics collection failed: %s', prefix, e)
        return {'status': 'error', 'stage': 'collect_metrics', 'error': str(e)}

    # ── 2. Gate
    try:
        gate = config.gate_evaluator(metrics)
    except Exception as e:
        logger.exception('[%s] gate evaluator failed: %s', prefix, e)
        return {'status': 'error', 'stage': 'evaluate_gate', 'error': str(e)}

    logger.info(
        '[%s] gate=%s severity=%s reasons=%s',
        prefix, gate.get('tripped'), gate.get('severity'), gate.get('reasons'),
    )

    if not gate.get('tripped'):
        return {'status': 'clear', 'gate': gate, 'metrics_summary': _summary(metrics)}

    # ── 3. Dedupe + cooldown
    dedupe_check = _dedupe_and_cooldown_check(config, now, gate, metrics)
    if not dedupe_check['should_post']:
        logger.info(
            '[%s] gate tripped (severity=%s) but skipping: %s',
            prefix, gate.get('severity'), dedupe_check['reason'],
        )
        return {
            'status': 'gated_by_dedupe_or_cooldown',
            'gate': gate,
            'skip_reason': dedupe_check['reason'],
            'dedupe_hash': dedupe_check['dedupe_hash'],
        }

    # ── 4. Dispatch agent async (no .get())
    workspace_id = _env_value(config.workspace_id_env) if config.workspace_id_env else None
    agent_prompt = config.prompt_builder(metrics, gate)
    agent_async_id = None
    dispatch_error = None
    try:
        from core.tasks import execute_agent_task
        async_result = execute_agent_task.apply_async(
            kwargs={
                'agent_name': config.agent_name,
                'task': agent_prompt,
                'context': {
                    'source': config.diagnostic_type,
                    'workspace_id': workspace_id,
                    'severity': gate.get('severity'),
                    'gate_reasons': gate.get('reasons', []),
                },
            },
            queue=config.queue,
            expires=config.agent_task_expires_seconds,
        )
        agent_async_id = async_result.id
    except Exception as e:
        dispatch_error = f'{type(e).__name__}: {e}'
        logger.exception('[%s] %s dispatch failed: %s', prefix, config.agent_name, dispatch_error)

    # ── 5. Title + structured payload (narrative filled in by post task)
    date_label = _date_bucket(now, config.timezone_name)
    title = config.title_builder(metrics, gate, date_label)
    structured_payload = _build_structured_payload(
        metrics, gate, dedupe_check['dedupe_hash'], agent_async_id, dispatch_error,
    )

    # ── 6. Observation mode
    if not posting_enabled:
        logger.info(
            '[%s] would post (%s=false): severity=%s title=%r dedupe_hash=%s agent_async_id=%s',
            prefix, config.posting_enabled_env, gate.get('severity'), title,
            dedupe_check['dedupe_hash'], agent_async_id,
        )
        return {
            'status': 'log_only',
            'gate': gate,
            'title': title,
            'agent_async_task_id': agent_async_id,
            'dispatch_error': dispatch_error,
            'dedupe_hash': dedupe_check['dedupe_hash'],
        }

    # ── 7. Set dedupe/cooldown NOW so concurrent runs can't double-post
    try:
        cache.set(dedupe_check['dedupe_key'], '1', timeout=config.dedupe_ttl_hours * 3600)
        cache.set(
            dedupe_check['cooldown_key'], now.isoformat(),
            timeout=dedupe_check['cooldown_hours'] * 3600,
        )
    except Exception as e:
        logger.warning('[%s] dedupe/cooldown set failed (non-fatal): %s', prefix, e)

    # ── 8. Enqueue post task
    if not config.post_task_import_path:
        logger.error('[%s] post_task_import_path empty — cannot enqueue', prefix)
        return {
            'status': 'enqueue_failed',
            'gate': gate,
            'error': 'post_task_import_path not configured',
            'agent_async_task_id': agent_async_id,
            'dedupe_hash': dedupe_check['dedupe_hash'],
        }

    try:
        post_task = _resolve_import_path(config.post_task_import_path)
    except Exception as e:
        logger.exception(
            '[%s] failed to resolve post_task_import_path=%r: %s',
            prefix, config.post_task_import_path, e,
        )
        return {
            'status': 'enqueue_failed',
            'gate': gate,
            'error': f'resolve_post_task: {type(e).__name__}: {e}',
            'agent_async_task_id': agent_async_id,
            'dedupe_hash': dedupe_check['dedupe_hash'],
        }

    countdown = config.agent_timeout_seconds + config.post_countdown_slack_seconds
    try:
        post_async = post_task.apply_async(
            kwargs={
                'agent_async_task_id': agent_async_id,
                'title': title,
                'severity': gate.get('severity'),
                'gate': gate,
                'metrics': metrics,
                'structured_payload': structured_payload,
            },
            countdown=countdown,
            queue=config.queue,
            expires=config.post_task_expires_seconds,
        )
        logger.info(
            '[%s] dispatched %s (async_id=%s) and queued post (post_id=%s, countdown=%ds)',
            prefix, config.agent_name, agent_async_id, post_async.id, countdown,
        )
        return {
            'status': 'dispatched',
            'gate': gate,
            'title': title,
            'agent_async_task_id': agent_async_id,
            'post_async_task_id': post_async.id,
            'dedupe_hash': dedupe_check['dedupe_hash'],
        }
    except Exception as e:
        logger.exception('[%s] post follow-up enqueue failed: %s', prefix, e)
        return {
            'status': 'enqueue_failed',
            'gate': gate,
            'error': str(e),
            'agent_async_task_id': agent_async_id,
            'dedupe_hash': dedupe_check['dedupe_hash'],
        }


def _summary(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the most-commonly-useful slice of metrics for log lines.

    Tolerates missing keys — different diagnostics have different shapes.
    """
    w24 = metrics.get('window_24h') or {}
    return {
        'total_24h': w24.get('total'),
        'failed_24h': w24.get('failed'),
        'fail_rate_24h': w24.get('fail_rate'),
        'delta_vs_7d': metrics.get('delta_vs_7d'),
    }


def _build_structured_payload(
    metrics: Dict[str, Any],
    gate: Dict[str, Any],
    dedupe_hash: str,
    agent_async_id: Optional[str],
    dispatch_error: Optional[str],
) -> Dict[str, Any]:
    """Build the structured payload passed to post task.

    Preserves the CTO shape keys (window_24h, window_7d, delta_vs_7d,
    top_failing_agents, top_signatures_24h, new_signatures_24h,
    spiking_agents) when present, since CTO tests + downstream consumers
    depend on them. Other diagnostics that don't have those keys just
    won't include them — the keys are dropped gracefully via `.get`.
    """
    payload: Dict[str, Any] = {
        'severity': gate.get('severity'),
        'gate_reasons': gate.get('reasons', []),
        'dedupe_hash': dedupe_hash,
        'agent_async_task_id': agent_async_id,
        'dispatch_error': dispatch_error,
    }
    # Preserve CTO-shape keys when collector provides them (backwards compat)
    for key in ('window_24h', 'window_7d', 'delta_vs_7d',
                'top_signatures_24h', 'new_signatures_24h'):
        if key in metrics:
            payload[key] = metrics[key]
    if 'top_failing_agents_24h' in metrics:
        payload['top_failing_agents'] = metrics['top_failing_agents_24h'][:10]
    if 'spiking_agents' in gate:
        payload['spiking_agents'] = gate['spiking_agents']
    return payload


# =============================================================================
# Runner — Task B (post_<name>)
# =============================================================================

def post_diagnostic(
    config: DiagnosticConfig,
    agent_async_task_id: Optional[str],
    title: str,
    severity: str,
    gate: Dict[str, Any],
    metrics: Dict[str, Any],
    structured_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """Generic post-phase: load agent result → compose body → post.

    Idempotent via posted_key. Safe to re-invoke.

    Returns a status dict. Status values:
      - 'already_posted'     — short-circuited via posted_key
      - 'posted'             — new attention item created
      - 'post_failed'        — attention_bridge raised
    """
    from django.core.cache import cache
    from core.services.human_attention_bridge import attention_bridge

    prefix = f'{config.log_prefix}-POST'
    dedupe_hash = structured_payload.get('dedupe_hash', '')
    posted_key = (
        f'{config.cache_key_prefix}:posted:{dedupe_hash[:12]}'
        if dedupe_hash else f'{config.cache_key_prefix}:posted:unknown'
    )

    if cache.get(posted_key):
        logger.info(
            '[%s] already posted (key=%s) — skipping duplicate post',
            prefix, posted_key,
        )
        return {'status': 'already_posted', 'severity': severity, 'posted_key': posted_key}

    narrative, narrative_error, execution_id, result_status = _load_agent_result(
        agent_async_task_id, structured_payload.get('dispatch_error'), prefix
    )

    body, actions = _compose_body(config, metrics, gate, narrative, narrative_error)

    # Final payload = structured_payload + agent follow-up data, size-capped
    final_payload = dict(structured_payload)
    final_payload.update({
        'agent_execution_id': execution_id,
        'agent_result_status': result_status,
        'agent_error': narrative_error,
        'narrative_present': bool(narrative),
        'recommended_actions_extracted': len(actions),
    })
    final_payload = _apply_payload_cap(final_payload, config.payload_cap_bytes)

    try:
        attention_bridge.create_diagnostic_alert(
            diagnostic_type=config.diagnostic_type,
            source_agent=config.source_agent,
            title=title[:200],
            summary=body[:8000],
            urgency=severity,
            payload=final_payload,
        )
    except Exception as e:
        logger.exception('[%s] attention_bridge.create_diagnostic_alert failed: %s', prefix, e)
        return {
            'status': 'post_failed',
            'severity': severity,
            'error': f'{type(e).__name__}: {e}',
            'posted_key': posted_key,
        }

    try:
        cache.set(posted_key, '1', timeout=config.posted_marker_ttl_hours * 3600)
    except Exception as e:
        logger.warning('[%s] posted marker set failed (non-fatal): %s', prefix, e)

    logger.info(
        '[%s] posted via attention_bridge: severity=%s title=%r narrative_present=%s actions=%d',
        prefix, severity, title, bool(narrative), len(actions),
    )
    return {
        'status': 'posted',
        'severity': severity,
        'title': title,
        'agent_execution_id': execution_id,
        'narrative_present': bool(narrative),
        'agent_error': narrative_error,
        'posted_key': posted_key,
        'recommended_actions_count': len(actions),
    }


def _load_agent_result(
    agent_async_task_id: Optional[str],
    dispatch_error: Optional[str],
    log_prefix: str,
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """Fetch agent narrative via AsyncResult (non-blocking check).

    Returns (narrative, error, execution_id, result_status).
    """
    narrative: Optional[str] = None
    error: Optional[str] = dispatch_error
    execution_id: Optional[str] = None
    result_status: Optional[str] = None

    if not agent_async_task_id:
        return narrative, error, execution_id, result_status

    try:
        from celery.result import AsyncResult
        ar = AsyncResult(agent_async_task_id)
        if ar.ready():
            result = ar.get(propagate=False) or {}
            if isinstance(result, dict):
                execution_id = result.get('execution_id')
                result_status = result.get('status')
                narrative = (
                    result.get('content')
                    or result.get('output')
                    or result.get('message')
                    or ''
                ) or None
                if result_status == 'failed':
                    error = error or result.get('error') or 'agent failed'
        else:
            error = error or (
                f'agent task {agent_async_task_id} not ready after countdown — '
                f'narrative unavailable'
            )
    except Exception as e:
        error = error or f'{type(e).__name__}: {e}'
        logger.exception(
            '[%s] failed to load agent result %s: %s',
            log_prefix, agent_async_task_id, error,
        )

    return narrative, error, execution_id, result_status
