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


# =============================================================================
# Tier-2 seed claims (Session 1099 continuation)
# =============================================================================
#
# Tier-1 covered CLAUDE.md + a few docs/topics/ files surfaced by the
# agent-system audit.  Tier-2 extends into the remaining Tier-1 authoritative
# docs listed in the Session 1099 memory: top-level AGENTS/SPIDERS references
# and the personal-assistant topic deep-dive.


@register_claim(
    doc='docs/AGENTS.md',
    claim_id='total_agents_header',
    description="docs/AGENTS.md header: 'Total Agents: 76'",
)
def _agents_md_total() -> ClaimResult:
    from core.agent_router import AgentRouter
    expected = 76
    actual = len(AgentRouter().AGENT_MAP)
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 2 else ('medium' if drift <= 10 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note="docs/AGENTS.md is stamped 'Last Updated: Session 969b (Feb 8 2026)'",
        fix_suggestion=(
            f"Update docs/AGENTS.md overview to 'Total Agents: {actual}' "
            f"and refresh the category table"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/AGENTS.md',
    claim_id='workspace_aware_agents_count',
    description="docs/AGENTS.md: '22 agents are WORKSPACE_AWARE_AGENTS'",
)
def _agents_md_workspace_aware() -> ClaimResult:
    """Parse WORKSPACE_AWARE_AGENTS from core/epa_handlers_tools.py."""
    import re
    from pathlib import Path
    src = (Path(__file__).resolve().parent.parent / 'epa_handlers_tools.py').read_text()
    # Grab the block between 'WORKSPACE_AWARE_AGENTS = [' and its closing ']'
    m = re.search(r'WORKSPACE_AWARE_AGENTS\s*=\s*\[(.*?)\]', src, re.DOTALL)
    if not m:
        return ClaimResult.build(
            expected=22, actual=None, severity='error',
            note='WORKSPACE_AWARE_AGENTS constant not found',
        )
    # Count quoted identifiers inside the block
    names = re.findall(r"'([A-Za-z_]+Agent)'", m.group(1))
    expected = 22
    actual = len(names)
    severity = 'ok' if actual == expected else ('low' if abs(actual - expected) <= 2 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"WORKSPACE_AWARE_AGENTS contains {actual} agent names",
        fix_suggestion=(
            f"Update docs/AGENTS.md '22 agents' mention to {actual}"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/AGENTS.md',
    claim_id='pa_tool_count_89',
    description="docs/AGENTS.md Session 969b: 'PA now has 89 tools'",
)
def _agents_md_pa_tool_count() -> ClaimResult:
    """Compare 'PA now has 89 tools' against the live PA_TOOL_SCHEMAS list."""
    from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
    expected = 89
    actual = len(PA_TOOL_SCHEMAS)
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 3 else ('medium' if drift <= 20 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=(
            "Claim is from docs/AGENTS.md; CLAUDE.md says '85+ schemas'. "
            "Both should agree with PA_TOOL_SCHEMAS length."
        ),
        fix_suggestion=(
            f"Update docs/AGENTS.md Session 969b Addition to '{actual} tools'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/SPIDERS.md',
    claim_id='total_spiders_header',
    description="docs/SPIDERS.md header: 'Total Registered Spiders: 77'",
)
def _spiders_md_total() -> ClaimResult:
    try:
        from ai_core.spiders.spider_registry import get_spider_registry
        registry = get_spider_registry()
        total_raw = registry.get_spider_count().get('total')
        actual: int = total_raw if isinstance(total_raw, int) else len(registry.list_spiders())
    except Exception as e:
        return ClaimResult.build(
            expected=77, actual=None, severity='error',
            note=f'Could not introspect spider registry: {e}',
        )
    expected = 77
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 2 else ('low' if drift <= 5 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note="docs/SPIDERS.md is stamped 'Last Updated: Session 567 (Dec 28 2025)'",
        fix_suggestion=(
            f"Update docs/SPIDERS.md overview + Quick Stats to 'Total: {actual}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/SPIDERS.md',
    claim_id='working_spiders_72',
    description="docs/SPIDERS.md quick-stats: 'Working (no auth needed): 72'",
)
def _spiders_md_working() -> ClaimResult:
    """Non-placeholder spiders per get_active_spiders()."""
    try:
        from ai_core.spiders.spider_registry import get_spider_registry
        actual = len(get_spider_registry().get_active_spiders())
    except Exception as e:
        return ClaimResult.build(
            expected=72, actual=None, severity='error',
            note=f'Could not introspect spider registry: {e}',
        )
    expected = 72
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 2 else ('low' if drift <= 5 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note="'Working' in docs = non-placeholder config in registry",
        fix_suggestion=(
            f"Update docs/SPIDERS.md Quick Stats to 'Working: {actual}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/SPIDERS.md',
    claim_id='spider_categories_20',
    description="docs/SPIDERS.md overview: '77 data sources across 20+ categories'",
)
def _spiders_md_categories() -> ClaimResult:
    try:
        from ai_core.spiders.spider_registry import get_spider_registry
        by_cat = get_spider_registry().get_spider_count().get('by_category')
        actual = len(by_cat) if isinstance(by_cat, dict) else 0
    except Exception as e:
        return ClaimResult.build(
            expected=20, actual=None, severity='error',
            note=f'Could not introspect spider registry: {e}',
        )
    expected = 20
    # '20+' is a floor — drift high when we BLEW PAST it (registry proliferated
    # categories without the doc tracking them).
    if actual >= expected and actual <= expected + 5:
        severity = 'ok'
    elif actual > expected + 5:
        severity = 'medium'
    else:
        severity = 'high'
    return ClaimResult.build(
        expected=f">= {expected}",
        actual=actual,
        severity=severity,
        note=(
            "docs promised '20+' as a floor; Tier-1 spider-network audit "
            "already showed 41 actual categories — uncontrolled proliferation."
        ),
        fix_suggestion=(
            f"Either consolidate categories in spider_registry.py or update "
            f"docs/SPIDERS.md to '{actual} categories'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/personal-assistant.md',
    claim_id='pa_tool_schema_count_85',
    description="docs/topics/personal-assistant.md: '85+ tool schemas'",
)
def _pa_topics_schema_count() -> ClaimResult:
    from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
    expected = 85
    actual = len(PA_TOOL_SCHEMAS)
    # '85+' = floor.  OK if actual >= 85 and drift within +20; medium if far over.
    if actual < expected:
        severity = 'high'
    elif actual <= expected + 20:
        severity = 'ok'
    else:
        severity = 'medium'
    return ClaimResult.build(
        expected=f">= {expected}",
        actual=actual,
        severity=severity,
        fix_suggestion=(
            f"Update docs/topics/personal-assistant.md to '{actual} tool schemas'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/personal-assistant.md',
    claim_id='pa_tool_handler_count_120',
    description="docs/topics/personal-assistant.md: '120+ tool handlers'",
)
def _pa_topics_handler_count() -> ClaimResult:
    """Count self.register(...) calls in tool_dispatcher.py.

    ToolDispatcher registers handlers one-per-line via ``self.register(name, fn)``
    inside ``_register_default_handlers``; a grep is the authoritative count.
    """
    import re
    from pathlib import Path
    src = (Path(__file__).resolve().parent / 'tool_dispatcher.py').read_text()
    matches = re.findall(r'^\s*self\.register\(', src, re.MULTILINE)
    expected = 120
    actual = len(matches)
    if actual < expected:
        severity = 'high'
    elif actual <= expected + 30:
        severity = 'ok'
    else:
        severity = 'medium'
    return ClaimResult.build(
        expected=f">= {expected}",
        actual=actual,
        severity=severity,
        note=f"self.register(...) lines in tool_dispatcher.py: {actual}",
        fix_suggestion=(
            f"Update docs/topics/personal-assistant.md to '{actual} tool handlers'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/personal-assistant.md',
    claim_id='pa_gateway_tool_count',
    description="docs/topics/personal-assistant.md: '6 gateways (Session 1079 consolidation)'",
)
def _pa_topics_gateway_count() -> ClaimResult:
    from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
    gateways = {'governance_tool', 'work_tool', 'content_tool',
                'intelligence_tool', 'ops_tool', 'studio_tool'}
    names = {(s.get('name') if isinstance(s, dict) else None) for s in PA_TOOL_SCHEMAS}
    present = gateways & names
    missing = gateways - names
    expected = 6
    actual = len(present)
    severity = 'ok' if not missing else 'high'
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"missing={sorted(missing)}" if missing else "all 6 gateways present",
        fix_suggestion=(
            f"Either add the missing gateway schemas or update docs to "
            f"reference {actual} gateways"
            if missing else None
        ),
    )


@register_claim(
    doc='docs/topics/personal-assistant.md',
    claim_id='pa_enrichment_service_count',
    description="docs/topics/personal-assistant.md: 'Eight intelligence services inject context'",
)
def _pa_topics_enrichment_count() -> ClaimResult:
    """Count unique services referenced across INTENT_ENRICHMENT_MAP."""
    from core.services.unified_pa_entrypoint import UnifiedPAEntrypoint
    services: set[str] = set()
    for svc_list in getattr(UnifiedPAEntrypoint, 'INTENT_ENRICHMENT_MAP', {}).values():
        services.update(svc_list or [])
    expected = 8
    actual = len(services)
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 1 else ('low' if drift <= 3 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"unique services in INTENT_ENRICHMENT_MAP: {sorted(services)}",
        fix_suggestion=(
            f"Update docs/topics/personal-assistant.md to '{actual} intelligence services'"
            if severity != 'ok' else None
        ),
    )


# =============================================================================
# Tier-2 Round 2 — CAPABILITIES, SERVICES, and remaining docs/topics/ deep-dives
# =============================================================================
#
# docs/CAPABILITIES.md is stamped Jan 28 2026 (Session 858) and contradicts
# newer docs (AGENTS.md says 89 PA tools, CAPABILITIES.md says 86, current
# runtime is 101). SERVICES.md and content/initiative/body topics each carry
# additional verifiable constants.


@register_claim(
    doc='docs/CAPABILITIES.md',
    claim_id='total_agents_74',
    description="docs/CAPABILITIES.md system overview: 'Total Agents | 74'",
)
def _capabilities_total_agents() -> ClaimResult:
    from core.agent_router import AgentRouter
    expected = 74
    actual = len(AgentRouter().AGENT_MAP)
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 2 else ('medium' if drift <= 15 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=(
            "CAPABILITIES.md is stamped 'Last Updated: Session 858 (Jan 28 2026)'; "
            "AGENTS.md claims 76 total, this doc claims 74."
        ),
        fix_suggestion=(
            f"Reconcile CAPABILITIES.md + AGENTS.md to both say '{actual}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/CAPABILITIES.md',
    claim_id='pa_tools_86',
    description="docs/CAPABILITIES.md system overview: 'PA Tools | 86'",
)
def _capabilities_pa_tools() -> ClaimResult:
    from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
    expected = 86
    actual = len(PA_TOOL_SCHEMAS)
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 3 else ('medium' if drift <= 20 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=(
            "CAPABILITIES.md says 86, AGENTS.md says 89, docs/topics/PA says '85+'; "
            "all three should agree with PA_TOOL_SCHEMAS length."
        ),
        fix_suggestion=(
            f"Update CAPABILITIES.md 'PA Tools' row to {actual}"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/CAPABILITIES.md',
    claim_id='celery_tasks_235',
    description="docs/CAPABILITIES.md system overview: 'Celery Tasks | 235'",
)
def _capabilities_celery_tasks() -> ClaimResult:
    from core.celery import app as celery_app
    user_tasks = [t for t in celery_app.tasks.keys() if not t.startswith('celery.')]
    expected = 235
    actual = len(user_tasks)
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 15 else ('medium' if drift <= 60 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=(
            "CLAUDE.md says 269, docs/topics/celery-workers.md says 271, "
            "CAPABILITIES.md says 235 — three docs contradict each other."
        ),
        fix_suggestion=(
            f"Update CAPABILITIES.md + sibling docs to '{actual} Celery tasks'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/CAPABILITIES.md',
    claim_id='services_124',
    description="docs/CAPABILITIES.md system overview: 'Services | 124'",
)
def _capabilities_services_count() -> ClaimResult:
    """Compare '124 services' against actual *Service class count in core/services/."""
    import re
    from pathlib import Path
    services_dir = Path(__file__).resolve().parent
    class_count = 0
    for py in services_dir.rglob('*.py'):
        if '__pycache__' in py.parts or py.name == '__init__.py':
            continue
        try:
            src = py.read_text(errors='ignore')
        except OSError:
            continue
        class_count += len(re.findall(r'^class\s+[A-Z]\w*Service\b', src, re.MULTILINE))
    expected = 124
    drift = abs(class_count - expected)
    severity = 'ok' if drift <= 5 else ('medium' if drift <= 20 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=class_count,
        severity=severity,
        note=(
            "Counting top-level 'class *Service' definitions under core/services/; "
            "SERVICES.md claims 134, CLAUDE.md claims 135, CAPABILITIES.md claims 124."
        ),
        fix_suggestion=(
            f"Update CAPABILITIES.md Services count to {class_count}"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/SERVICES.md',
    claim_id='services_total_134',
    description="docs/SERVICES.md header: '134 service classes across 103 files'",
)
def _services_md_total() -> ClaimResult:
    import re
    from pathlib import Path
    services_dir = Path(__file__).resolve().parent
    class_count = 0
    for py in services_dir.rglob('*.py'):
        if '__pycache__' in py.parts or py.name == '__init__.py':
            continue
        try:
            src = py.read_text(errors='ignore')
        except OSError:
            continue
        class_count += len(re.findall(r'^class\s+[A-Z]\w*Service\b', src, re.MULTILINE))
    expected = 134
    drift = abs(class_count - expected)
    severity = 'ok' if drift <= 5 else ('medium' if drift <= 25 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=class_count,
        severity=severity,
        note="SERVICES.md is stamped 'Last Updated: Session 964 (Feb 7 2026)'",
        fix_suggestion=(
            f"Update docs/SERVICES.md to '{class_count} service classes'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/SERVICES.md',
    claim_id='services_file_count_103',
    description="docs/SERVICES.md header: '134 service classes across 103 files'",
)
def _services_md_file_count() -> ClaimResult:
    from pathlib import Path
    services_dir = Path(__file__).resolve().parent
    py_files = [
        p for p in services_dir.rglob('*.py')
        if '__pycache__' not in p.parts and p.name != '__init__.py'
    ]
    expected = 103
    actual = len(py_files)
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 10 else ('medium' if drift <= 50 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=(
            f"Counts all non-__init__ .py files in core/services/** — "
            f"includes {sum(1 for p in py_files if len(p.parts) > len(services_dir.parts) + 1)} nested-subdir files."
        ),
        fix_suggestion=(
            f"Update docs/SERVICES.md to '{actual} files'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/content-pipeline.md',
    claim_id='claimspack_max_claims_20',
    description="docs/topics/content-pipeline.md: 'Cap: Max 20 claims' per ClaimsPack",
)
def _content_claimspack_max() -> ClaimResult:
    """Compare ClaimsPackBuilder.build() default max_claims against the doc's cap."""
    import inspect
    from core.services.claims_pack_builder import ClaimsPackBuilder
    sig = inspect.signature(ClaimsPackBuilder.build)
    default = sig.parameters['max_claims'].default
    expected = 20
    severity = 'ok' if default == expected else 'medium'
    return ClaimResult.build(
        expected=expected,
        actual=default,
        severity=severity,
        note=f"ClaimsPackBuilder.build default: {default}",
        fix_suggestion=(
            f"Either change ClaimsPackBuilder default to {expected}, or update doc to '{default}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/initiative-pipeline.md',
    claim_id='signal_cluster_min_size_3',
    description="docs/topics/initiative-pipeline.md: 'MIN_CLUSTER_SIZE (3)'",
)
def _initiative_min_cluster_size() -> ClaimResult:
    from core.services.signal_aggregation_service import SignalAggregationService
    actual = getattr(SignalAggregationService, 'MIN_CLUSTER_SIZE', None)
    expected = 3
    severity = 'ok' if actual == expected else 'medium'
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        fix_suggestion=(
            f"Sync doc + constant; current constant is {actual}"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/initiative-pipeline.md',
    claim_id='signal_pattern_types_7',
    description="docs/topics/initiative-pipeline.md: '7 Pattern Types'",
)
def _initiative_pattern_types() -> ClaimResult:
    from core.models_signal_intelligence import SignalCluster
    actual = len(SignalCluster.PATTERN_TYPE_CHOICES)
    expected = 7
    drift = abs(actual - expected)
    severity = 'ok' if drift == 0 else ('low' if drift <= 2 else 'medium')
    names = [c[0] for c in SignalCluster.PATTERN_TYPE_CHOICES]
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"PATTERN_TYPE_CHOICES: {names}",
        fix_suggestion=(
            f"Update docs/topics/initiative-pipeline.md to '{actual} Pattern Types'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/body-systems.md',
    claim_id='body_systems_count_9',
    description="docs/topics/body-systems.md: '9 body systems'",
)
def _body_systems_count() -> ClaimResult:
    """Compare against the canonical 9-system list used by run_all_systems_scan."""
    from pathlib import Path
    import re
    src = (Path(__file__).resolve().parent.parent / 'tasks.py').read_text()
    m = re.search(
        r"body_systems\s*=\s*\[([^\]]+)\]",
        src,
    )
    if not m:
        return ClaimResult.build(
            expected=9, actual=None, severity='error',
            note='Could not find body_systems list in core/tasks.py',
        )
    items = [s.strip().strip("'\"") for s in m.group(1).split(',') if s.strip()]
    actual = len(items)
    expected = 9
    severity = 'ok' if actual == expected else 'medium'
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"body_systems list: {items}",
        fix_suggestion=(
            f"Sync doc + canonical list; current list length is {actual}"
            if severity != 'ok' else None
        ),
    )


# =============================================================================
# Tier-2 Round 3 — frontend + infrastructure
# =============================================================================
#
# Frontend claims are stale by a major refactor (WorkspacePageNew dropped from
# 9 tabs to 5 primary tabs). Infrastructure claims include provider registry
# membership and Redis DB fan-out.


def _frontend_root() -> Any:
    """Helper: resolve the frontend source root from this file's location."""
    from pathlib import Path
    return Path(__file__).resolve().parent.parent.parent / 'frontend' / 'src'


@register_claim(
    doc='docs/topics/frontend.md',
    claim_id='workspace_primary_tabs_9',
    description="docs/topics/frontend.md: '9 workspace tabs'",
)
def _frontend_workspace_tabs() -> ClaimResult:
    """Count primary WorkspaceTab union members in types.ts (before sub-tabs)."""
    import re
    types_file = _frontend_root() / 'pages' / 'workspace' / 'types.ts'
    if not types_file.exists():
        return ClaimResult.build(
            expected=9, actual=None, severity='error',
            note=f'{types_file} not found',
        )
    src = types_file.read_text()
    m = re.search(r'export type WorkspaceTab\s*=\s*((?:\s*\|\s*\'[^\']+\'\n?)+)', src)
    if not m:
        return ClaimResult.build(
            expected=9, actual=None, severity='error',
            note='Could not parse WorkspaceTab union',
        )
    body = m.group(1)
    before_subtabs = body.split('Sub-tab IDs')[0] if 'Sub-tab IDs' in src else body
    # Members appearing before the sub-tabs comment
    cutoff = src.find('Sub-tab IDs')
    preamble = src[m.start():cutoff] if cutoff > 0 else m.group(0)
    primary = re.findall(r"\|\s*'([^']+)'", preamble)
    actual = len(primary)
    expected = 9
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 1 else ('medium' if drift <= 4 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"primary WorkspaceTab members: {primary}",
        fix_suggestion=(
            f"Update docs/topics/frontend.md to '{actual} workspace tabs' "
            f"and refresh the tab table"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/frontend.md',
    claim_id='app_route_count_69',
    description="docs/topics/frontend.md: '69 route definitions in App.tsx'",
)
def _frontend_route_count() -> ClaimResult:
    """Count <Route ...> components in App.tsx."""
    import re
    app_tsx = _frontend_root() / 'App.tsx'
    if not app_tsx.exists():
        return ClaimResult.build(
            expected=69, actual=None, severity='error',
            note=f'{app_tsx} not found',
        )
    src = app_tsx.read_text()
    routes = re.findall(r'<Route\b', src)
    actual = len(routes)
    expected = 69
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 3 else ('medium' if drift <= 15 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        fix_suggestion=(
            f"Update docs/topics/frontend.md to '{actual} route definitions'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/frontend.md',
    claim_id='betting_dashboard_tabs_12',
    description="docs/topics/frontend.md: 'Betting Dashboard (12 tabs)'",
)
def _frontend_betting_tabs() -> ClaimResult:
    """Count entries in the top-level ``const tabs = [...]`` of BettingPage.tsx."""
    import re
    betting_tsx = _frontend_root() / 'pages' / 'BettingPage.tsx'
    if not betting_tsx.exists():
        return ClaimResult.build(
            expected=12, actual=None, severity='error',
            note=f'{betting_tsx} not found',
        )
    src = betting_tsx.read_text()
    m = re.search(r'const tabs\s*=\s*\[(.*?)\]\s*\n', src, re.DOTALL)
    if not m:
        return ClaimResult.build(
            expected=12, actual=None, severity='error',
            note='Could not locate `const tabs = [...]` in BettingPage.tsx',
        )
    entries = re.findall(r"id:\s*'([^']+)'", m.group(1))
    actual = len(entries)
    expected = 12
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 1 else ('medium' if drift <= 4 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"betting tab ids: {entries}",
        fix_suggestion=(
            f"Update docs/topics/frontend.md Betting Dashboard section to '{actual} tabs'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/infrastructure.md',
    claim_id='redis_db_fanout_4',
    description="docs/topics/infrastructure.md: 'Redis (DB0: channels, DB1: cache, DB2: broker, DB3: results)'",
)
def _infra_redis_db_count() -> ClaimResult:
    """Parse distinct /0../N redis DB indices from core/settings.py."""
    import re
    from pathlib import Path
    settings = (Path(__file__).resolve().parent.parent / 'settings.py').read_text()
    # Match lines like 'redis://...:6379/<N>' (or tls variant) and collect unique indices
    indices = set(re.findall(r"redis(?:s)?://[^'\"]*?/(\d+)\b", settings))
    actual = len(indices)
    expected = 4
    # Tolerate +/-1 because dev fixtures may bump this
    severity = 'ok' if actual == expected else ('low' if abs(actual - expected) <= 1 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"distinct redis DB indices in settings.py: {sorted(indices)}",
        fix_suggestion=(
            f"Update docs/topics/infrastructure.md to describe {actual} Redis DBs"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/infrastructure.md',
    claim_id='llm_providers_6',
    description="docs/topics/infrastructure.md: '6 LLM Providers' (OpenAI, Anthropic, Together, Ollama, DeepSeek, Gemini)",
)
def _infra_llm_provider_count() -> ClaimResult:
    """Count provider_classes entries in LLMProviderRegistry._initialize_providers()."""
    import re
    from pathlib import Path
    src = (Path(__file__).resolve().parent / 'llm_provider_registry.py').read_text()
    m = re.search(r'provider_classes\s*=\s*\{(.*?)\}', src, re.DOTALL)
    if not m:
        return ClaimResult.build(
            expected=6, actual=None, severity='error',
            note='Could not parse provider_classes dict in LLMProviderRegistry',
        )
    names = re.findall(r"'([^']+)'\s*:", m.group(1))
    actual = len(names)
    expected = 6
    drift = abs(actual - expected)
    severity = 'ok' if drift == 0 else ('low' if drift == 1 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"registered providers: {names}",
        fix_suggestion=(
            f"Sync doc + provider registry — registered count = {actual}"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/infrastructure.md',
    claim_id='database_models_386',
    description="docs/topics/infrastructure.md: 'PostgreSQL with pgvector extension (386+ models)'",
)
def _infra_database_models() -> ClaimResult:
    """Count concrete (non-abstract, non-proxy) Django models registered with the 'core' app."""
    from django.apps import apps
    models = apps.get_models()
    concrete = [m for m in models if not m._meta.abstract and not m._meta.proxy]
    actual = len(concrete)
    expected = 386
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 20 else ('medium' if drift <= 60 else 'high')
    core_count = sum(1 for m in concrete if m._meta.app_label == 'core')
    return ClaimResult.build(
        expected=f">= {expected}",
        actual=actual,
        severity=severity,
        note=f"core app models: {core_count}, total concrete across all apps: {actual}",
        fix_suggestion=(
            f"Update docs/topics/infrastructure.md to '{actual} models'"
            if severity != 'ok' else None
        ),
    )


# =============================================================================
# Tier-2 Round 4 — docs/current/ (stale INDEX) + ARCHITECTURE.md
# =============================================================================
#
# docs/current/INDEX.md is stamped 'January 2026 / Session 661+' and contains
# 5+ stats that are months stale. Flag the biggest ones so the doc either
# retires or gets a refresh. ARCHITECTURE.md claims 200K LOC — verify with a
# Python-only line count (coarse but actionable).


@register_claim(
    doc='docs/current/INDEX.md',
    claim_id='current_index_total_agents_72',
    description="docs/current/INDEX.md: 'Agents | 72 | 69 routable'",
)
def _current_index_agents() -> ClaimResult:
    from core.agent_router import AgentRouter
    expected = 72
    actual = len(AgentRouter().AGENT_MAP)
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 2 else ('medium' if drift <= 15 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note="docs/current/INDEX.md is stamped 'January 2026 / Session 661+'",
        fix_suggestion=(
            f"Retire or refresh docs/current/INDEX.md — agent count is {actual}"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/current/INDEX.md',
    claim_id='current_index_celery_tasks_127',
    description="docs/current/INDEX.md: 'Celery Tasks | 127+'",
)
def _current_index_celery() -> ClaimResult:
    from core.celery import app as celery_app
    user_tasks = [t for t in celery_app.tasks.keys() if not t.startswith('celery.')]
    expected = 127
    actual = len(user_tasks)
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 15 else ('medium' if drift <= 100 else 'high')
    return ClaimResult.build(
        expected=f">= {expected}",
        actual=actual,
        severity=severity,
        fix_suggestion=(
            f"Retire or refresh docs/current/INDEX.md — celery task count is {actual}"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/current/INDEX.md',
    claim_id='current_index_models_324',
    description="docs/current/INDEX.md: 'Database Models | 324+'",
)
def _current_index_models() -> ClaimResult:
    from django.apps import apps
    concrete = [m for m in apps.get_models() if not m._meta.abstract and not m._meta.proxy]
    expected = 324
    actual = len(concrete)
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 20 else ('medium' if drift <= 100 else 'high')
    return ClaimResult.build(
        expected=f">= {expected}",
        actual=actual,
        severity=severity,
        fix_suggestion=(
            f"Retire or refresh docs/current/INDEX.md — model count is {actual}"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/current/INDEX.md',
    claim_id='current_index_pa_tools_77',
    description="docs/current/INDEX.md: 'PA Tools | 77'",
)
def _current_index_pa_tools() -> ClaimResult:
    from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
    expected = 77
    actual = len(PA_TOOL_SCHEMAS)
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 3 else ('medium' if drift <= 25 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=(
            "docs/current/INDEX.md says 77; CAPABILITIES 86; AGENTS 89; "
            "topics/PA '85+'. Four contradictions, one source of truth: "
            "PA_TOOL_SCHEMAS length."
        ),
        fix_suggestion=(
            f"Retire or refresh docs/current/INDEX.md — PA tool count is {actual}"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/ARCHITECTURE.md',
    claim_id='total_lines_of_code_200k',
    description="docs/ARCHITECTURE.md header: 'Total Lines of Code: 200,000+'",
)
def _architecture_total_loc() -> ClaimResult:
    """Approximate LOC: concatenate Python files under core/ + ai_core/ and count lines.

    Uses a repo-local scan — identifies files the backend actually ships. Coarse
    but reproducible. Does not include frontend TS/TSX (separate claim if needed).
    """
    from pathlib import Path
    repo_root = Path(__file__).resolve().parent.parent.parent
    targets = [repo_root / 'core', repo_root / 'ai_core', repo_root / 'intelligence']
    total_lines = 0
    file_count = 0
    for root in targets:
        if not root.exists():
            continue
        for py in root.rglob('*.py'):
            if '__pycache__' in py.parts or '.venv' in py.parts or 'site-packages' in py.parts:
                continue
            try:
                total_lines += sum(1 for _ in py.open(encoding='utf-8', errors='ignore'))
                file_count += 1
            except OSError:
                continue
    expected = 200_000
    severity = 'ok' if total_lines >= expected else ('low' if total_lines >= expected * 0.8 else 'medium')
    return ClaimResult.build(
        expected=f">= {expected:,}",
        actual=total_lines,
        severity=severity,
        note=(
            f"python-only LOC across core/, ai_core/, intelligence/ ({file_count} files); "
            f"frontend TS/TSX not included"
        ),
        fix_suggestion=(
            f"Update ARCHITECTURE.md to '{total_lines:,}+' Python LOC "
            f"or include frontend in the total"
            if severity != 'ok' else None
        ),
    )


# =============================================================================
# Tier-2 Round 5 — remaining docs/current/ subfiles + content-pipeline deep-dive
# =============================================================================
#
# docs/current/{VIEWS, API_ENDPOINTS, MANAGEMENT_COMMANDS, SERVICES, DISCORD}.md
# all stamped 'January 2026' and carry explicit totals. Each gets one claim.


@register_claim(
    doc='docs/current/VIEWS.md',
    claim_id='view_file_count_143',
    description="docs/current/VIEWS.md: 'Total View Files: 143'",
)
def _current_views_count() -> ClaimResult:
    from pathlib import Path
    core_dir = Path(__file__).resolve().parent.parent
    view_files = [p for p in core_dir.glob('views*.py') if p.name != '__init__.py']
    actual = len(view_files)
    expected = 143
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 5 else ('medium' if drift <= 30 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"core/views*.py glob match count: {actual}",
        fix_suggestion=(
            f"Update docs/current/VIEWS.md to 'Total View Files: {actual}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/current/API_ENDPOINTS.md',
    claim_id='endpoint_count_200plus',
    description="docs/current/API_ENDPOINTS.md: 'Total Endpoints: 200+'",
)
def _current_endpoints_count() -> ClaimResult:
    """Count path(...) patterns across core/urls*.py."""
    import re
    from pathlib import Path
    core_dir = Path(__file__).resolve().parent.parent
    total = 0
    for urls_file in core_dir.glob('urls*.py'):
        try:
            src = urls_file.read_text()
        except OSError:
            continue
        total += len(re.findall(r'^\s*path\(', src, re.MULTILINE))
    expected = 200
    # '200+' is a floor. OK if floor met; but material undercount (>5x) warrants
    # a medium flag so the doc gets refreshed.
    if total < expected:
        severity = 'high'
    elif total <= expected * 3:
        severity = 'ok'
    else:
        severity = 'medium'
    return ClaimResult.build(
        expected=f">= {expected}",
        actual=total,
        severity=severity,
        note=f"core/urls*.py path() patterns: {total}",
        fix_suggestion=(
            f"Update docs/current/API_ENDPOINTS.md to '{total}+ endpoints'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/current/MANAGEMENT_COMMANDS.md',
    claim_id='management_command_count_43',
    description="docs/current/MANAGEMENT_COMMANDS.md: 'Total Commands: 43'",
)
def _current_mgmt_commands() -> ClaimResult:
    from pathlib import Path
    cmds_dir = Path(__file__).resolve().parent.parent / 'management' / 'commands'
    if not cmds_dir.exists():
        return ClaimResult.build(
            expected=43, actual=None, severity='error',
            note=f'{cmds_dir} not found',
        )
    cmds = [
        p for p in cmds_dir.iterdir()
        if p.is_file() and p.suffix == '.py' and p.name != '__init__.py'
    ]
    actual = len(cmds)
    expected = 43
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 5 else ('medium' if drift <= 40 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"core/management/commands/*.py (non-init): {actual}",
        fix_suggestion=(
            f"Update docs/current/MANAGEMENT_COMMANDS.md to 'Total Commands: {actual}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/current/SERVICES.md',
    claim_id='current_services_93plus',
    description="docs/current/SERVICES.md: 'Total Services: 93+'",
)
def _current_services_count() -> ClaimResult:
    """Same class-counting methodology as SERVICES.md claim — they should match."""
    import re
    from pathlib import Path
    services_dir = Path(__file__).resolve().parent
    class_count = 0
    for py in services_dir.rglob('*.py'):
        if '__pycache__' in py.parts or py.name == '__init__.py':
            continue
        try:
            src = py.read_text(errors='ignore')
        except OSError:
            continue
        class_count += len(re.findall(r'^class\s+[A-Z]\w*Service\b', src, re.MULTILINE))
    expected = 93
    # '93+' is a floor. OK if floor met.
    severity = 'ok' if class_count >= expected else 'high'
    return ClaimResult.build(
        expected=f">= {expected}",
        actual=class_count,
        severity=severity,
        note="Same metric as docs/SERVICES.md claim; both stale",
        fix_suggestion=(
            f"Retire docs/current/SERVICES.md or update to '{class_count}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/current/DISCORD.md',
    claim_id='discord_cogs_29',
    description="docs/current/DISCORD.md: 'Command Cogs: 29'",
)
def _current_discord_cogs() -> ClaimResult:
    import re
    from pathlib import Path
    bot_file = Path(__file__).resolve().parent / 'discord_bot.py'
    if not bot_file.exists():
        return ClaimResult.build(
            expected=29, actual=None, severity='error',
            note=f'{bot_file} not found',
        )
    src = bot_file.read_text()
    cogs = re.findall(r'^class\s+\w+\s*\([^)]*\bCog\b[^)]*\)\s*:', src, re.MULTILINE)
    actual = len(cogs)
    expected = 29
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 2 else ('medium' if drift <= 10 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"Cog-subclass definitions in discord_bot.py: {actual}",
        fix_suggestion=(
            f"Update docs/current/DISCORD.md to 'Command Cogs: {actual}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/content-pipeline.md',
    claim_id='domain_context_nine_domains',
    description="docs/topics/content-pipeline.md: 'Domain context (Session 891): platform data from 9 domains'",
)
def _content_pipeline_domains() -> ClaimResult:
    """Count entries in DomainContentContextBuilder's domain_builders dict."""
    import re
    from pathlib import Path
    src = (Path(__file__).resolve().parent / 'domain_content_context.py').read_text()
    m = re.search(r'domain_builders\s*=\s*\{(.*?)\}', src, re.DOTALL)
    if not m:
        return ClaimResult.build(
            expected=9, actual=None, severity='error',
            note='domain_builders dict not found',
        )
    keys = re.findall(r"'([a-z_]+)'\s*:", m.group(1))
    actual = len(keys)
    expected = 9
    drift = abs(actual - expected)
    severity = 'ok' if drift == 0 else ('low' if drift <= 2 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"domain_builders keys: {keys}",
        fix_suggestion=(
            f"Sync doc + code — domain_builders has {actual} entries"
            if severity != 'ok' else None
        ),
    )


# =============================================================================
# Tier-2 Round 6 — API path policy + assistant subsystem
# =============================================================================


@register_claim(
    doc='docs/API_PATH_POLICY.md',
    claim_id='api_prefix_count_1420',
    description="docs/API_PATH_POLICY.md: '/api/ prefix: 1,420+ (81.5%)'",
)
def _api_prefix_count() -> ClaimResult:
    """Count `path('api/...` (NOT `api/v1/`) patterns across core/urls*.py."""
    import re
    from pathlib import Path
    core_dir = Path(__file__).resolve().parent.parent
    total = 0
    for urls_file in core_dir.rglob('urls*.py'):
        if '__pycache__' in urls_file.parts:
            continue
        try:
            src = urls_file.read_text()
        except OSError:
            continue
        # Match path('api/...') but NOT path('api/v1/...')
        total += len(re.findall(r"path\(\s*['\"]api/(?!v1/)", src))
    expected = 1420
    drift = abs(total - expected)
    severity = 'ok' if drift <= 80 else ('medium' if drift <= 500 else 'high')
    return ClaimResult.build(
        expected=f">= {expected}",
        actual=total,
        severity=severity,
        note="Excludes /api/v1/ prefix (counted separately)",
        fix_suggestion=(
            f"Refresh docs/API_PATH_POLICY.md to '{total}' /api/ endpoints"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/API_PATH_POLICY.md',
    claim_id='api_v1_prefix_count_322',
    description="docs/API_PATH_POLICY.md: '/api/v1/ prefix: 322 (18.5%)'",
)
def _api_v1_prefix_count() -> ClaimResult:
    """Count `path('api/v1/...` patterns across core/urls*.py."""
    import re
    from pathlib import Path
    core_dir = Path(__file__).resolve().parent.parent
    total = 0
    for urls_file in core_dir.rglob('urls*.py'):
        if '__pycache__' in urls_file.parts:
            continue
        try:
            src = urls_file.read_text()
        except OSError:
            continue
        total += len(re.findall(r"path\(\s*['\"]api/v1/", src))
    expected = 322
    drift = abs(total - expected)
    severity = 'ok' if drift <= 20 else ('low' if drift <= 60 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=total,
        fix_suggestion=(
            f"Refresh docs/API_PATH_POLICY.md to '{total}' /api/v1/ endpoints"
            if severity != 'ok' else None
        ),
        severity=severity,
    )


@register_claim(
    doc='docs/current/ASSISTANT_SYSTEM.md',
    claim_id='assistant_dir_file_count_8',
    description="docs/current/ASSISTANT_SYSTEM.md: 'Total Files: 8' in core/assistant/",
)
def _assistant_dir_files() -> ClaimResult:
    from pathlib import Path
    assistant_dir = Path(__file__).resolve().parent.parent / 'assistant'
    if not assistant_dir.exists():
        return ClaimResult.build(
            expected=8, actual=0, severity='high',
            note='core/assistant/ directory missing',
            fix_suggestion='Retire docs/current/ASSISTANT_SYSTEM.md — subsystem removed',
        )
    py_files = [
        p for p in assistant_dir.iterdir()
        if p.is_file() and p.suffix == '.py' and p.name != '__init__.py'
    ]
    actual = len(py_files)
    expected = 8
    drift = abs(actual - expected)
    severity = 'ok' if drift == 0 else ('low' if drift <= 2 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"core/assistant/*.py (non-init): {sorted(p.name for p in py_files)}",
        fix_suggestion=(
            f"Update docs/current/ASSISTANT_SYSTEM.md to 'Total Files: {actual}'"
            if severity != 'ok' else None
        ),
    )


# =============================================================================
# Tier-2 Round 7 — BACKEND_INVENTORY.md + DISCORD_INTEGRATION.md
# =============================================================================
#
# BACKEND_INVENTORY.md (Jan 18 2026) is the 5th or 6th doc making claims about
# models/views/services/commands counts — each contradicts the others. Seeding
# its headline numbers exposes the multi-source-of-truth problem clearly.


@register_claim(
    doc='docs/BACKEND_INVENTORY.md',
    claim_id='backend_inventory_django_models_413',
    description="docs/BACKEND_INVENTORY.md summary: 'Django Models | 413'",
)
def _backend_inv_models() -> ClaimResult:
    from django.apps import apps
    concrete = [m for m in apps.get_models() if not m._meta.abstract and not m._meta.proxy]
    actual = len(concrete)
    expected = 413
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 20 else ('medium' if drift <= 100 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=(
            "Same metric as docs/topics/infrastructure.md '386+' and "
            "docs/current/INDEX.md '324+'. Three docs, three numbers, one truth."
        ),
        fix_suggestion=(
            f"Consolidate model count across docs to '{actual}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/BACKEND_INVENTORY.md',
    claim_id='backend_inventory_view_files_164',
    description="docs/BACKEND_INVENTORY.md summary: 'Views Files | 164'",
)
def _backend_inv_views() -> ClaimResult:
    from pathlib import Path
    core_dir = Path(__file__).resolve().parent.parent
    view_files = [p for p in core_dir.glob('views*.py') if p.name != '__init__.py']
    actual = len(view_files)
    expected = 164
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 10 else ('medium' if drift <= 40 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=(
            "docs/current/VIEWS.md says 143; BACKEND_INVENTORY.md says 164; "
            "actual count of core/views*.py files"
        ),
        fix_suggestion=(
            f"Reconcile VIEWS.md + BACKEND_INVENTORY.md to '{actual}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/BACKEND_INVENTORY.md',
    claim_id='backend_inventory_service_files_167',
    description="docs/BACKEND_INVENTORY.md summary: 'Services | 167 files'",
)
def _backend_inv_services_files() -> ClaimResult:
    from pathlib import Path
    services_dir = Path(__file__).resolve().parent
    py_files = [
        p for p in services_dir.rglob('*.py')
        if '__pycache__' not in p.parts and p.name != '__init__.py'
    ]
    actual = len(py_files)
    expected = 167
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 15 else ('medium' if drift <= 80 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=(
            "docs/SERVICES.md claims 103; BACKEND_INVENTORY.md claims 167; "
            "actual .py file count (excluding __init__.py)"
        ),
        fix_suggestion=(
            f"Reconcile SERVICES.md + BACKEND_INVENTORY.md to '{actual}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/BACKEND_INVENTORY.md',
    claim_id='backend_inventory_mgmt_cmds_63',
    description="docs/BACKEND_INVENTORY.md summary: 'Management Commands | 63'",
)
def _backend_inv_mgmt() -> ClaimResult:
    from pathlib import Path
    cmds_dir = Path(__file__).resolve().parent.parent / 'management' / 'commands'
    cmds = [
        p for p in cmds_dir.iterdir()
        if p.is_file() and p.suffix == '.py' and p.name != '__init__.py'
    ]
    actual = len(cmds)
    expected = 63
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 10 else ('medium' if drift <= 50 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=(
            "docs/current/MANAGEMENT_COMMANDS.md says 43; "
            "BACKEND_INVENTORY.md says 63; actual files in management/commands/"
        ),
        fix_suggestion=(
            f"Reconcile to '{actual}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/DISCORD_INTEGRATION.md',
    claim_id='discord_total_commands_112',
    description="docs/DISCORD_INTEGRATION.md header: 'Commands: 112 total'",
)
def _discord_total_commands() -> ClaimResult:
    """Count @*.command(...) decorators in discord_bot.py."""
    import re
    from pathlib import Path
    bot_file = Path(__file__).resolve().parent / 'discord_bot.py'
    if not bot_file.exists():
        return ClaimResult.build(
            expected=112, actual=None, severity='error',
            note='discord_bot.py not found',
        )
    src = bot_file.read_text()
    matches = re.findall(r'^\s*@\w+\.command\(', src, re.MULTILINE)
    actual = len(matches)
    expected = 112
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 5 else ('medium' if drift <= 25 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=(
            "Multiple docs contradict on this: DISCORD_COMMANDS.md 112/25 Cogs; "
            "DISCORD_INTEGRATION.md 112/20 cats; current/DISCORD.md 112/29 Cogs; "
            "CAPABILITIES.md 112; BACKEND_INVENTORY.md 231. Counting "
            "@*.command decorators in discord_bot.py."
        ),
        fix_suggestion=(
            f"Reconcile Discord command count to '{actual}' across all docs"
            if severity != 'ok' else None
        ),
    )


# =============================================================================
# Tier-2 Round 8 — Celery beat + MODELS + websocket consumers
# =============================================================================


@register_claim(
    doc='docs/current/CELERY_TASKS.md',
    claim_id='scheduled_tasks_53',
    description="docs/current/CELERY_TASKS.md header: 'Scheduled Tasks: 53'",
)
def _current_scheduled_tasks() -> ClaimResult:
    """Count enabled django-celery-beat PeriodicTask rows."""
    from django_celery_beat.models import PeriodicTask
    actual = PeriodicTask.objects.filter(enabled=True).count()
    expected = 53
    drift = abs(actual - expected)
    # Beat schedules grow rapidly as the platform adds monitors — a large over
    # is almost certainly a doc-stale signal, not a runtime problem.
    severity = 'ok' if drift <= 10 else ('medium' if drift <= 100 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=(
            f"PeriodicTask.objects.filter(enabled=True).count() == {actual} "
            f"(total including disabled: {PeriodicTask.objects.count()})"
        ),
        fix_suggestion=(
            f"Update docs/current/CELERY_TASKS.md to 'Scheduled Tasks: {actual}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/BACKEND_INVENTORY.md',
    claim_id='backend_inventory_celery_tasks_243',
    description="docs/BACKEND_INVENTORY.md summary: 'Celery Tasks | 243'",
)
def _backend_inv_celery() -> ClaimResult:
    from core.celery import app as celery_app
    user_tasks = [t for t in celery_app.tasks.keys() if not t.startswith('celery.')]
    expected = 243
    actual = len(user_tasks)
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 15 else ('medium' if drift <= 60 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=(
            "5-way contradiction across docs: current/INDEX 127+, "
            "CAPABILITIES 235, BACKEND_INVENTORY 243, CLAUDE 269, "
            "topics/celery-workers 271. Ground truth: celery_app.tasks."
        ),
        fix_suggestion=(
            f"Unify all docs to '{actual}' celery tasks"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/BACKEND_INVENTORY.md',
    claim_id='backend_inventory_websocket_consumers_52',
    description="docs/BACKEND_INVENTORY.md summary: 'WebSocket Consumers | 52'",
)
def _backend_inv_consumers() -> ClaimResult:
    """Count classes subclassing a channels Consumer across core/."""
    import re
    from pathlib import Path
    core_dir = Path(__file__).resolve().parent.parent
    consumer_count = 0
    pattern = re.compile(
        r'^class\s+\w+\s*\([^)]*(?:WebsocketConsumer|JsonWebsocketConsumer|AsyncConsumer|SyncConsumer)\b',
        re.MULTILINE,
    )
    for py in core_dir.rglob('*.py'):
        if '__pycache__' in py.parts:
            continue
        try:
            src = py.read_text(errors='ignore')
        except OSError:
            continue
        consumer_count += len(pattern.findall(src))
    expected = 52
    drift = abs(consumer_count - expected)
    severity = 'ok' if drift <= 5 else ('medium' if drift <= 20 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=consumer_count,
        severity=severity,
        note="Counts class definitions inheriting a channels Consumer subclass under core/",
        fix_suggestion=(
            f"Update docs/BACKEND_INVENTORY.md to 'WebSocket Consumers | {consumer_count}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/current/MODELS.md',
    claim_id='current_models_324plus',
    description="docs/current/MODELS.md header: 'Total Models: 324+'",
)
def _current_models_count() -> ClaimResult:
    from django.apps import apps
    concrete = [m for m in apps.get_models() if not m._meta.abstract and not m._meta.proxy]
    actual = len(concrete)
    expected = 324
    # Floor claim — OK when ≥ floor and within 2x; beyond 2x flags severe stale
    if actual < expected:
        severity = 'high'
    elif actual <= expected * 1.5:
        severity = 'ok'
    else:
        severity = 'medium'
    return ClaimResult.build(
        expected=f">= {expected}",
        actual=actual,
        severity=severity,
        note="Same metric as DATABASE_MODEL_REFERENCE 386+, BACKEND_INVENTORY 413, infrastructure 386+",
        fix_suggestion=(
            f"Retire or refresh docs/current/MODELS.md to '{actual}'"
            if severity != 'ok' else None
        ),
    )
