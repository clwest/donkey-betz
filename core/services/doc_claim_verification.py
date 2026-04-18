"""Doc-vs-Reality claim verification framework (Session 1099).

Compare what the authoritative documentation claims about the platform
against what the runtime actually shows. Built from the rotation and
agent-system audits performed in Session 1099 that surfaced ~7 distinct
drift findings between docs and reality in a single subsystem.

## Concepts

- ``ClaimResult`` — the structured verdict for a single claim
- ``register_claim`` — decorator that adds a claim to the registry
- ``run_all``/``run_filtered`` — execute claims and collect results

## Adding a new claim

```python
from core.services.doc_claim_verification import register_claim, ClaimResult

@register_claim(doc="CLAUDE.md", claim_id="agent_map_count",
                description="CLAUDE.md header table lists AGENT_MAP count")
def verify_agent_map_count() -> ClaimResult:
    from core.agent_router import AgentRouter
    expected = 84
    actual = len(AgentRouter().AGENT_MAP)
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity='medium' if expected != actual else 'ok',
        fix_suggestion=(
            f"Update CLAUDE.md to '{actual} AGENT_MAP' if the drift is real"
            if expected != actual else None
        ),
    )
```

## Severity guidance

- ``critical`` — docs describe a feature that does not exist at all
- ``high``  — docs describe behaviour that materially differs (scheduled daily but is on-demand only)
- ``medium`` — counts or configuration values drift but feature functions
- ``low``   — cosmetic drift (off-by-one, label disagreement)
- ``ok``    — matches

## CLI

```
python manage.py verify_doc_claims                  # all claims
python manage.py verify_doc_claims --doc CLAUDE.md  # one doc
python manage.py verify_doc_claims --format json    # machine-readable
python manage.py verify_doc_claims --only-drift     # hide matches
```
"""
from __future__ import annotations

import logging
import time
import traceback
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


SEVERITIES = ('ok', 'low', 'medium', 'high', 'critical', 'error')


@dataclass
class ClaimResult:
    """Structured verdict for a single verification."""
    matched: bool
    expected: Any
    actual: Any
    severity: str = 'ok'
    note: Optional[str] = None
    fix_suggestion: Optional[str] = None
    # Populated by the runner:
    doc: str = ''
    claim_id: str = ''
    description: str = ''
    runtime_ms: int = 0
    error: Optional[str] = None

    @classmethod
    def build(
        cls,
        expected: Any,
        actual: Any,
        severity: str = 'ok',
        note: Optional[str] = None,
        fix_suggestion: Optional[str] = None,
    ) -> 'ClaimResult':
        """Convenience constructor — caller doesn't need to compute ``matched``."""
        if severity not in SEVERITIES:
            raise ValueError(f"severity must be one of {SEVERITIES}, got {severity!r}")
        return cls(
            matched=(severity == 'ok'),
            expected=expected,
            actual=actual,
            severity=severity,
            note=note,
            fix_suggestion=fix_suggestion,
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        # Coerce any non-serializable values
        for k, v in list(d.items()):
            if isinstance(v, (list, tuple, set)):
                d[k] = [str(x) if not isinstance(x, (str, int, float, bool, type(None))) else x for x in v]
            elif not isinstance(v, (str, int, float, bool, type(None), dict, list)):
                d[k] = str(v)
        return d


@dataclass
class _RegisteredClaim:
    doc: str
    claim_id: str
    description: str
    verifier: Callable[[], ClaimResult]


_REGISTRY: list[_RegisteredClaim] = []


def register_claim(doc: str, claim_id: str, description: str = ''):
    """Decorator: register a verifier function for a documentation claim.

    The verifier takes no arguments and returns a :class:`ClaimResult`.
    Its ``doc``, ``claim_id``, and ``description`` fields are filled in
    automatically by the runner, so ``ClaimResult.build`` suffices.
    """
    def _deco(fn: Callable[[], ClaimResult]) -> Callable[[], ClaimResult]:
        _REGISTRY.append(_RegisteredClaim(
            doc=doc,
            claim_id=claim_id,
            description=description or fn.__doc__ or '',
            verifier=fn,
        ))
        return fn
    return _deco


def list_registered() -> list[dict]:
    """Return a preview list of all registered claims — for CLI ``--list`` mode."""
    return [
        {'doc': c.doc, 'claim_id': c.claim_id, 'description': (c.description or '').strip().splitlines()[0] if c.description else ''}
        for c in _REGISTRY
    ]


def run_one(claim: _RegisteredClaim) -> ClaimResult:
    """Execute one claim, trapping exceptions as ``severity='error'`` results."""
    t0 = time.monotonic()
    try:
        result = claim.verifier()
        if not isinstance(result, ClaimResult):
            raise TypeError(
                f"Claim {claim.doc}:{claim.claim_id} returned {type(result).__name__}, "
                f"expected ClaimResult"
            )
    except Exception as e:  # noqa: BLE001
        result = ClaimResult(
            matched=False,
            expected=None,
            actual=None,
            severity='error',
            note=f"Verifier raised {type(e).__name__}: {e}",
            error=traceback.format_exc(limit=3),
        )
    result.doc = claim.doc
    result.claim_id = claim.claim_id
    result.description = claim.description
    result.runtime_ms = int((time.monotonic() - t0) * 1000)
    return result


def run_all(doc_filter: Optional[str] = None, only_drift: bool = False) -> list[ClaimResult]:
    """Run every registered claim (optionally filtered by doc path)."""
    results: list[ClaimResult] = []
    for claim in _REGISTRY:
        if doc_filter and claim.doc != doc_filter:
            continue
        r = run_one(claim)
        if only_drift and r.severity == 'ok':
            continue
        results.append(r)
    return results


def summarize(results: list[ClaimResult]) -> dict:
    """Roll up counts by severity + by doc."""
    by_severity: dict[str, int] = {s: 0 for s in SEVERITIES}
    by_doc: dict[str, dict] = {}
    for r in results:
        by_severity[r.severity] = by_severity.get(r.severity, 0) + 1
        d = by_doc.setdefault(r.doc, {'total': 0, 'ok': 0, 'drift': 0, 'error': 0})
        d['total'] += 1
        if r.severity == 'ok':
            d['ok'] += 1
        elif r.severity == 'error':
            d['error'] += 1
        else:
            d['drift'] += 1
    return {
        'total': len(results),
        'by_severity': by_severity,
        'by_doc': by_doc,
    }


# =============================================================================
# Seed claims — drifts surfaced during the Session 1099 agent-system audit
# =============================================================================
#
# Each claim mirrors a specific line from an anchor doc against a specific
# runtime query.  When adding more claims, prefer the smallest verifiable
# assertion possible — one doc line ↔ one ClaimResult.


@register_claim(
    doc='CLAUDE.md',
    claim_id='agent_map_count',
    description="CLAUDE.md stats table: '84 AGENT_MAP'",
)
def _agent_map_count() -> ClaimResult:
    from core.agent_router import AgentRouter
    expected = 84
    actual = len(AgentRouter().AGENT_MAP)
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity='low' if actual != expected else 'ok',
        fix_suggestion=(
            f"Update CLAUDE.md stats table to '{actual} AGENT_MAP'"
            if actual != expected else None
        ),
    )


@register_claim(
    doc='CLAUDE.md',
    claim_id='persona_agent_count',
    description="CLAUDE.md stats table: '~139 DB persona agents (via DynamicPersonaAgent)'",
)
def _persona_agent_count() -> ClaimResult:
    from core.models_unified_system import Agent
    from django.db.models import Q
    persona_count = Agent.objects.filter(
        Q(agent_type__icontains='persona') | Q(agent_type='dynamic') | Q(name__icontains='persona')
    ).count()
    expected = 139
    # Tolerate ±20 because personas drift naturally
    lo, hi = expected - 20, expected + 20
    severity = 'ok' if lo <= persona_count <= hi else 'high'
    note = (
        f"Found only {persona_count} persona-typed Agent rows; CLAUDE.md overcounts by ~{expected - persona_count}"
        if severity != 'ok' else None
    )
    return ClaimResult.build(
        expected=f"{lo}..{hi}",
        actual=persona_count,
        severity=severity,
        note=note,
        fix_suggestion=(
            f"Either backfill persona agents, or update CLAUDE.md to stop claiming ~139 DynamicPersonaAgent rows"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='CLAUDE.md',
    claim_id='total_agent_count_claim',
    description="CLAUDE.md header: 'Agents | 218'",
)
def _total_agent_count_claim() -> ClaimResult:
    from core.agent_router import AgentRouter
    from core.models_unified_system import Agent
    from django.db.models import Q
    routable = len(AgentRouter().AGENT_MAP)
    personas = Agent.objects.filter(
        Q(agent_type__icontains='persona') | Q(agent_type='dynamic') | Q(name__icontains='persona')
    ).count()
    actual_total = routable + personas
    expected = 218
    drift = abs(actual_total - expected)
    severity = 'ok' if drift <= 5 else ('high' if drift > 50 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual_total,
        severity=severity,
        note=f"AGENT_MAP({routable}) + persona({personas}) = {actual_total}",
        fix_suggestion=(
            f"Update CLAUDE.md total to {actual_total} (or reconcile persona-agent definition)"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/agent-system.md',
    claim_id='provenance_tracked_count',
    description="'26 provenance-tracked' agents",
)
def _provenance_tracked_count() -> ClaimResult:
    import subprocess
    from pathlib import Path
    base = Path(__file__).resolve().parent.parent / 'agents'
    # grep -l 'build_provenance(' on all agent files, excluding base_agent + report_schemas
    r = subprocess.run(
        ['grep', '-rln', 'build_provenance(', str(base), '--include=*.py'],
        capture_output=True, text=True
    )
    files = [
        line for line in r.stdout.split('\n')
        if line and 'base_agent' not in line and 'report_schemas' not in line and '__pycache__' not in line
    ]
    expected = 26
    actual = len(files)
    severity = 'ok' if actual == expected else 'low'
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"Agent files calling build_provenance(): {actual}",
        fix_suggestion=(
            f"Either wire {expected - actual} more agents or update docs to say {actual}"
            if actual < expected else
            f"Update docs/topics/agent-system.md to say {actual} provenance-tracked"
            if actual > expected else None
        ),
    )


@register_claim(
    doc='docs/topics/agent-system.md',
    claim_id='intelligence_desks_scheduled',
    description="'Session 1000: 4 Intelligence Desks run 21 agents daily at 6 AM via run_all_desks_intelligence Celery task'",
)
def _intelligence_desks_scheduled() -> ClaimResult:
    from django_celery_beat.models import PeriodicTask
    pt = PeriodicTask.objects.filter(
        task='core.tasks.run_all_desks_intelligence'
    ).first()
    if not pt:
        return ClaimResult.build(
            expected='scheduled daily',
            actual='no PeriodicTask exists',
            severity='high',
            note=(
                "run_all_desks_intelligence exists as a Celery task function but is not "
                "scheduled in PeriodicTask. Only run_market_intelligence_desk (stocks only) "
                "runs daily. 3 of 4 claimed desks are on-demand only."
            ),
            fix_suggestion=(
                "Either add a beat schedule for run_all_desks_intelligence, or correct the "
                "docs to describe the current on-demand-only reality."
            ),
        )
    if not pt.enabled:
        return ClaimResult.build(
            expected='enabled, daily',
            actual='disabled',
            severity='high',
            fix_suggestion="Re-enable the scheduled task, or correct the docs.",
        )
    return ClaimResult.build(
        expected='scheduled daily',
        actual=f"enabled, schedule={pt.crontab or pt.interval}",
        severity='ok',
    )


@register_claim(
    doc='docs/topics/celery-workers.md',
    claim_id='celery_task_count',
    description="'271 Celery tasks across 9 worker processes'",
)
def _celery_task_count() -> ClaimResult:
    # Authoritative task list comes from the Celery app's discovered registry
    from core.celery import app as celery_app
    # Filter out celery-internal tasks (e.g. celery.backend_cleanup) to match
    # the '271' project-task figure
    user_tasks = [t for t in celery_app.tasks.keys() if not t.startswith('celery.')]
    actual = len(user_tasks)
    expected = 271
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 15 else ('medium' if drift <= 50 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        fix_suggestion=(
            f"Update docs/topics/celery-workers.md to '{actual} Celery tasks'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/spider-network.md',
    claim_id='spider_count',
    description="'79 spiders across 18 categories'",
)
def _spider_count() -> ClaimResult:
    try:
        from ai_core.spiders.spider_registry import get_spider_registry
        stats = get_spider_registry().get_spider_count()
        actual: int = stats.get('total', len(get_spider_registry().list_spiders()))
        category_count = len(stats.get('by_category', {}))
    except Exception as e:
        return ClaimResult.build(
            expected=79,
            actual=None,
            severity='error',
            note=f'Could not introspect spider registry: {e}',
        )
    expected = 79
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 2 else ('low' if drift <= 5 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"categories={category_count} (docs claim 18)",
        fix_suggestion=(
            f"Update docs/topics/spider-network.md to '{actual} spiders across {category_count} categories'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='core/services/priority/governor.py',
    claim_id='platform_operations_whitelist_integrity',
    description="Whitelisted agents must exist in AGENT_MAP",
)
def _platform_operations_whitelist_integrity() -> ClaimResult:
    from core.models_unified_system import ActivePriority
    from core.agent_router import AgentRouter
    am = set(AgentRouter().AGENT_MAP.keys())
    phantom: list[str] = []
    for p in ActivePriority.objects.filter(status='active'):
        for w in (p.agent_whitelist or []):
            if w not in am:
                phantom.append(f"{p.name}:{w}")
    severity = 'ok' if not phantom else 'medium'
    return ClaimResult.build(
        expected='all whitelist entries in AGENT_MAP',
        actual=phantom or 'no phantoms',
        severity=severity,
        note=f"{len(phantom)} whitelist entries reference agents not in AGENT_MAP" if phantom else None,
        fix_suggestion=(
            f"Remove these phantom whitelist entries: {phantom}"
            if phantom else None
        ),
    )


@register_claim(
    doc='CLAUDE.md',
    claim_id='celery_worker_processes',
    description="CLAUDE.md stats table: 'Celery Tasks | 269 | 9 worker processes'",
)
def _celery_worker_processes() -> ClaimResult:
    # Parse Procfile for non-release worker entries
    from pathlib import Path
    procfile = Path(__file__).resolve().parent.parent.parent / 'Procfile'
    if not procfile.exists():
        return ClaimResult.build(
            expected=9, actual=None, severity='error',
            note='Procfile not found at expected location',
        )
    workers = []
    for line in procfile.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('release:'):
            continue
        if ':' not in line:
            continue
        name = line.split(':', 1)[0].strip()
        if name:
            workers.append(name)
    expected = 9
    actual = len(workers)
    drift = abs(actual - expected)
    severity = 'ok' if drift == 0 else ('low' if drift <= 1 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"Procfile processes: {', '.join(workers)}",
    )
