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


SEVERITIES = ('ok', 'skipped', 'low', 'medium', 'high', 'critical', 'error')
# `skipped` = claim is marked `db_required=True` and the runtime had no usable
# DB/extension to evaluate against. Surfaces in JSON but is not drift and does
# not fail `--fail-on-drift`. Set on a claim by passing `db_required=True` to
# `@register_claim(...)`.


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
    db_required: bool = False


_REGISTRY: list[_RegisteredClaim] = []


def register_claim(doc: str, claim_id: str, description: str = '', db_required: bool = False):
    """Decorator: register a verifier function for a documentation claim.

    The verifier takes no arguments and returns a :class:`ClaimResult`.
    Its ``doc``, ``claim_id``, and ``description`` fields are filled in
    automatically by the runner, so ``ClaimResult.build`` suffices.

    ``db_required=True`` tells the runner that this claim genuinely needs a
    live database (rows must exist, not just be queryable). When the verifier
    raises a recognised DB-availability error (``OperationalError``,
    ``InterfaceError``, ``ProgrammingError`` for missing extensions/tables),
    the runner returns ``severity='skipped'`` instead of ``'error'``, and the
    summary breaks `skipped` out separately. This keeps the verifier honest
    on developer machines that don't have the full local stack stood up.
    """
    def _deco(fn: Callable[[], ClaimResult]) -> Callable[[], ClaimResult]:
        _REGISTRY.append(_RegisteredClaim(
            doc=doc,
            claim_id=claim_id,
            description=description or fn.__doc__ or '',
            verifier=fn,
            db_required=db_required,
        ))
        return fn
    return _deco


def list_registered() -> list[dict]:
    """Return a preview list of all registered claims — for CLI ``--list`` mode."""
    return [
        {'doc': c.doc, 'claim_id': c.claim_id, 'description': (c.description or '').strip().splitlines()[0] if c.description else ''}
        for c in _REGISTRY
    ]


def _looks_like_db_unavailable(exc: BaseException) -> bool:
    """Return True if *exc* indicates the DB / required extension is missing.

    Recognised: ``django.db.utils.OperationalError`` (connection refused,
    fe_sendauth, no such host), ``InterfaceError`` (dead connection),
    ``ProgrammingError`` whose message mentions a missing extension or
    relation, and bare ``ImportError`` for the optional ``psycopg`` driver.
    Anything else is real and should still surface as ``severity='error'``.
    """
    try:
        from django.db.utils import (
            OperationalError, InterfaceError, ProgrammingError,
        )
    except Exception:  # noqa: BLE001
        return False
    if isinstance(exc, (OperationalError, InterfaceError)):
        return True
    if isinstance(exc, ProgrammingError):
        msg = str(exc).lower()
        # Missing pgvector extension, or tables that haven't been migrated yet.
        if 'extension' in msg and ('vector' in msg or 'not available' in msg):
            return True
        if 'does not exist' in msg or 'relation' in msg:
            return True
    if isinstance(exc, ImportError) and 'psycopg' in str(exc).lower():
        return True
    return False


def run_one(claim: _RegisteredClaim) -> ClaimResult:
    """Execute one claim, trapping exceptions as ``severity='error'`` results.

    If ``claim.db_required`` is set and the exception looks like a DB-
    availability problem (connection refused, missing pgvector, unmigrated
    tables), the result is returned with ``severity='skipped'`` instead so
    it shows up as informational rather than a hard error.
    """
    t0 = time.monotonic()
    try:
        result = claim.verifier()
        if not isinstance(result, ClaimResult):
            raise TypeError(
                f"Claim {claim.doc}:{claim.claim_id} returned {type(result).__name__}, "
                f"expected ClaimResult"
            )
    except Exception as e:  # noqa: BLE001
        if claim.db_required and _looks_like_db_unavailable(e):
            severity = 'skipped'
            note = f"DB unavailable ({type(e).__name__}); claim marked db_required=True"
        else:
            severity = 'error'
            note = f"Verifier raised {type(e).__name__}: {e}"
        result = ClaimResult(
            matched=False,
            expected=None,
            actual=None,
            severity=severity,
            note=note,
            error=traceback.format_exc(limit=3) if severity == 'error' else None,
        )
    result.doc = claim.doc
    result.claim_id = claim.claim_id
    result.description = claim.description
    result.runtime_ms = int((time.monotonic() - t0) * 1000)
    return result


def run_all(doc_filter: Optional[str] = None, only_drift: bool = False) -> list[ClaimResult]:
    """Run every registered claim (optionally filtered by doc path).

    ``only_drift`` hides both ``ok`` AND ``skipped`` — they're informational,
    not drift.
    """
    results: list[ClaimResult] = []
    for claim in _REGISTRY:
        if doc_filter and claim.doc != doc_filter:
            continue
        r = run_one(claim)
        if only_drift and r.severity in ('ok', 'skipped'):
            continue
        results.append(r)
    return results


def summarize(results: list[ClaimResult]) -> dict:
    """Roll up counts by severity + by doc.

    ``skipped`` is bucketed separately — not as drift, not as error, not as
    ok. Use it to spot claims that didn't get evaluated because the local
    stack lacks something (DB, pgvector, migrations, …).
    """
    by_severity: dict[str, int] = {s: 0 for s in SEVERITIES}
    by_doc: dict[str, dict] = {}
    for r in results:
        by_severity[r.severity] = by_severity.get(r.severity, 0) + 1
        d = by_doc.setdefault(
            r.doc,
            {'total': 0, 'ok': 0, 'drift': 0, 'error': 0, 'skipped': 0},
        )
        d['total'] += 1
        if r.severity == 'ok':
            d['ok'] += 1
        elif r.severity == 'error':
            d['error'] += 1
        elif r.severity == 'skipped':
            d['skipped'] += 1
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
    description="CLAUDE.md stats table: '83 AGENT_MAP'",
)
def _agent_map_count() -> ClaimResult:
    from core.agent_router import AgentRouter
    expected = 83  # refreshed Session 1100 — matches current CLAUDE.md
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
    description="CLAUDE.md stats table: '223 DB persona agents (via DynamicPersonaAgent)'",
    db_required=True,
)
def _persona_agent_count() -> ClaimResult:
    """Count rows in Agent table — these are the agents the AgentRouter
    falls back to via DynamicPersonaAgent when AGENT_MAP doesn't contain
    the requested name. Session 1099's narrow filter (agent_type='persona')
    only caught 3 rows, but the *eligible-for-DynamicPersonaAgent* count
    is the full Agent.objects.count() — that's what CLAUDE.md cites.
    """
    from core.models_unified_system import Agent
    actual = Agent.objects.count()
    expected = 223  # refreshed Session 1100 — matches current CLAUDE.md
    drift = abs(actual - expected)
    # Tolerate ±10 because personas drift naturally
    severity = 'ok' if drift <= 10 else ('medium' if drift <= 50 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"Agent.objects.count() = {actual} (all agent_types eligible for DynamicPersonaAgent fallback)",
        fix_suggestion=(
            f"Update CLAUDE.md stats table to '{actual} DB persona agents'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='CLAUDE.md',
    claim_id='total_agent_count_claim',
    description="CLAUDE.md header: 'Agents (total registered) | 306'",
    db_required=True,
)
def _total_agent_count_claim() -> ClaimResult:
    from core.agent_router import AgentRouter
    from core.models_unified_system import Agent
    routable = len(AgentRouter().AGENT_MAP)
    personas = Agent.objects.count()  # Session 1100: full Agent table, not narrow filter
    actual_total = routable + personas
    expected = 306  # refreshed Session 1100 — matches current CLAUDE.md
    drift = abs(actual_total - expected)
    severity = 'ok' if drift <= 10 else ('medium' if drift <= 50 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual_total,
        severity=severity,
        note=f"AGENT_MAP({routable}) + Agent rows({personas}) = {actual_total}",
        fix_suggestion=(
            f"Update CLAUDE.md total to {actual_total}"
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
    claim_id='intelligence_desks_partial_schedule',
    description=(
        "Session 1100 corrected claim: only `run_market_intelligence_desk` (stocks) "
        "is scheduled daily; 3 of 4 desks are on-demand only via /api/home/trigger-desks/"
    ),
    db_required=True,
)
def _intelligence_desks_partial_schedule() -> ClaimResult:
    """Verify the corrected claim: stocks desk IS scheduled, others are on-demand only.

    Session 1099 originally flagged this as a high-severity drift because the
    doc claimed all 4 desks ran daily but only stocks was scheduled. Session 1100
    corrected the doc to describe the actual partial-schedule reality. This
    verifier now confirms the doc matches reality:

    - run_market_intelligence_desk: enabled PeriodicTask present (✓)
    - run_all_desks_intelligence:   no PeriodicTask (✓ on-demand only, doc agrees)
    """
    from django_celery_beat.models import PeriodicTask
    stocks_pt = PeriodicTask.objects.filter(
        task='core.tasks.run_market_intelligence_desk'
    ).first()
    all_desks_pt = PeriodicTask.objects.filter(
        task='core.tasks.run_all_desks_intelligence'
    ).first()
    stocks_scheduled = bool(stocks_pt and stocks_pt.enabled)
    all_desks_scheduled = bool(all_desks_pt and all_desks_pt.enabled)
    expected_state = "stocks scheduled, other 3 on-demand only"
    if stocks_scheduled and not all_desks_scheduled:
        return ClaimResult.build(
            expected=expected_state,
            actual=expected_state,
            severity='ok',
        )
    parts: list[str] = []
    if not stocks_scheduled:
        parts.append("stocks desk NOT scheduled (doc says it should be)")
    if all_desks_scheduled:
        parts.append("run_all_desks_intelligence IS scheduled (doc says on-demand only)")
    return ClaimResult.build(
        expected=expected_state,
        actual="; ".join(parts) or "unknown",
        severity='medium',
        fix_suggestion=(
            "Either re-add stocks PeriodicTask, or update docs/topics/agent-system.md "
            "to describe whatever the actual schedule is now."
        ),
    )


@register_claim(
    doc='docs/topics/celery-workers.md',
    claim_id='celery_task_count',
    description="'365 Celery tasks across 7 worker processes'",
)
def _celery_task_count() -> ClaimResult:
    # Authoritative task list comes from the Celery app's discovered registry
    from core.celery import app as celery_app
    user_tasks = [t for t in celery_app.tasks.keys() if not t.startswith('celery.')]
    actual = len(user_tasks)
    expected = 365  # refreshed Session 1100 — matches CLAUDE.md + PLATFORM_INVENTORY
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
    db_required=True,
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
    expected = 10  # refreshed Session 1100 — Procfile has 10 worker entries
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
    expected = 83  # refreshed Session 1100 — matches new docs/AGENTS.md
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
    expected = 20  # refreshed Session 1100
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
    expected = 101  # refreshed Session 1100 — matches new docs/AGENTS.md
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
            expected=80, actual=None, severity='error',
            note=f'Could not introspect spider registry: {e}',
        )
    expected = 80  # refreshed Session 1100
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 2 else ('low' if drift <= 5 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note="docs/SPIDERS.md refreshed Session 1100 — was Session 567 (Dec 28 2025)",
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
    expected = 80  # refreshed Session 1100 — all 80 work
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
    claim_id='spider_categories_count',
    description="docs/SPIDERS.md overview: '80 data sources across 41 categories' (refreshed Session 1100)",
)
def _spiders_md_categories() -> ClaimResult:
    try:
        from ai_core.spiders.spider_registry import get_spider_registry
        by_cat = get_spider_registry().get_spider_count().get('by_category')
        actual = len(by_cat) if isinstance(by_cat, dict) else 0
    except Exception as e:
        return ClaimResult.build(
            expected=41, actual=None, severity='error',
            note=f'Could not introspect spider registry: {e}',
        )
    expected = 41  # refreshed Session 1100 — matches new docs/SPIDERS.md
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 3 else ('low' if drift <= 8 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=(
            "Session 1099 audit found uncontrolled category proliferation (was '20+' "
            "floor, actually 41). Doc refreshed Session 1100 to state '41 categories' "
            "explicitly. Future consolidation work tracked separately."
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
    expected = 166  # refreshed Session 1100
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
    expected = 83  # refreshed Session 1100 (CAPABILITIES.md table now states 306 = 83 + 223 personas)
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
    expected = 101  # refreshed Session 1100
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
    expected = 365  # refreshed Session 1100
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
    expected = 112  # refreshed Session 1100 — matches new docs/CAPABILITIES.md
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
    expected = 112  # refreshed Session 1100 — matches new docs/SERVICES.md
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
    expected = 320  # refreshed Session 1100 — matches new docs/SERVICES.md
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
    expected = 10  # refreshed Session 1100
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
    expected = 5  # refreshed Session 1100 — primary tabs only
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
    expected = 61  # refreshed Session 1100
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
    expected = 9  # refreshed Session 1100
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
    expected = 3  # refreshed Session 1100 — settings.py has DB1/2/3
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
    expected = 570  # refreshed Session 1100
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
# Tier-2 Round 4 — docs/current/ (RETIRED 2026-04-26) + ARCHITECTURE.md
# =============================================================================
#
# RETIRED 2026-04-26 (Session 1100): The four docs/current/INDEX.md claims
# (current_index_total_agents_72, current_index_celery_tasks_127,
# current_index_models_324, current_index_pa_tools_77) were removed because
# the underlying doc was archived to docs/archive/superseded-current-jan-2026/.
# Live counts for these metrics live in PLATFORM_INVENTORY.md. The
# ARCHITECTURE.md LOC claim below is still active.


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
# Tier-2 Round 5 — content-pipeline deep-dive (docs/current/* RETIRED)
# =============================================================================
#
# RETIRED 2026-04-26 (Session 1100): Five docs/current/* claims removed —
# view_file_count_143 (VIEWS.md), endpoint_count_200plus (API_ENDPOINTS.md),
# management_command_count_43 (MANAGEMENT_COMMANDS.md),
# current_services_93plus (SERVICES.md), discord_cogs_29 (DISCORD.md).
# Underlying docs archived to docs/archive/superseded-current-jan-2026/.


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


# RETIRED 2026-04-26 (Session 1100): assistant_dir_file_count_8 claim removed —
# docs/current/ASSISTANT_SYSTEM.md archived to docs/archive/superseded-current-jan-2026/.


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
    expected = 570  # refreshed Session 1100
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
    expected = 200  # refreshed Session 1100
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
    expected = 320  # refreshed Session 1100
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
    expected = 153  # refreshed Session 1100
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
    claim_id='discord_total_commands',
    description="docs/DISCORD_AUDIT.md header: '96 total commands (48 slash + 48 prefix)' in discord_bot.py",
)
def _discord_total_commands() -> ClaimResult:
    """Count Discord command decorators via AST — Session 1115 corrected the
    long-standing regex double-count.

    The previous version (Session 1100) added two regex match lists:
      classic = `^\\s*@\\w+\\.command\\(`         # matches @app_commands.command too
      app_cmds = `^\\s*@app_commands\\.command\\(`
      total = len(classic) + len(app_cmds)  # double-counts the 48 slash commands

    `@\\w+\\.command` already matches `@app_commands.command` (because
    `app_commands` is `\\w+`). Adding `app_cmds` again inflates by 48.
    Real total is `len(classic)` = 96 (48 slash + 48 prefix). Audited via
    AST in `core/management/commands/build_discord_audit.py`.
    """
    import ast
    from pathlib import Path
    bot_file = Path(__file__).resolve().parent / 'discord_bot.py'
    if not bot_file.exists():
        return ClaimResult.build(
            expected=96, actual=None, severity='error',
            note='discord_bot.py not found',
        )
    try:
        tree = ast.parse(bot_file.read_text(errors='ignore'))
    except SyntaxError as e:
        return ClaimResult.build(
            expected=96, actual=None, severity='error',
            note=f'discord_bot.py would not parse: {e}',
        )
    n_slash = n_prefix = 0
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            text = ast.unparse(dec.func) if hasattr(ast, 'unparse') else ''
            if 'app_commands.command' in text:
                n_slash += 1
                break
            if text.endswith('.command'):
                n_prefix += 1
                break
    actual = n_slash + n_prefix
    expected = 96  # 48 slash + 48 prefix per Session 1115 audit
    drift = abs(actual - expected)
    severity = 'ok' if drift <= 2 else ('medium' if drift <= 10 else 'high')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"{n_slash} slash + {n_prefix} prefix (AST-counted)",
        fix_suggestion=(
            f"Update CLAUDE.md Discord row + docs/DISCORD_AUDIT.md headline "
            f"to '{actual} commands ({n_slash} slash + {n_prefix} prefix)'"
            if severity != 'ok' else None
        ),
    )


# =============================================================================
# Tier-2 Round 8 — Celery beat + MODELS + websocket consumers
# =============================================================================


# RETIRED 2026-04-26 (Session 1100): scheduled_tasks_53 claim removed —
# docs/current/CELERY_TASKS.md archived to docs/archive/superseded-current-jan-2026/.


@register_claim(
    doc='docs/BACKEND_INVENTORY.md',
    claim_id='backend_inventory_celery_tasks_243',
    description="docs/BACKEND_INVENTORY.md summary: 'Celery Tasks | 243'",
)
def _backend_inv_celery() -> ClaimResult:
    from core.celery import app as celery_app
    user_tasks = [t for t in celery_app.tasks.keys() if not t.startswith('celery.')]
    expected = 365  # refreshed Session 1100
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
    expected = 67  # refreshed Session 1100
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


# RETIRED 2026-04-26 (Session 1100): current_models_324plus claim removed —
# docs/current/MODELS.md archived to docs/archive/superseded-current-jan-2026/.


# =============================================================================
# Tier-2 Round 9 — CLAUDE.md uncovered stats + code-level enum/choice constants
# =============================================================================


@register_claim(
    doc='CLAUDE.md',
    claim_id='llm_providers_6',
    description="CLAUDE.md stats table: 'LLM Providers | 6 | OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini'",
)
def _claude_llm_providers() -> ClaimResult:
    """Count provider_classes entries in LLMProviderRegistry._initialize_providers()."""
    import re
    from pathlib import Path
    src = (Path(__file__).resolve().parent / 'llm_provider_registry.py').read_text()
    m = re.search(r'provider_classes\s*=\s*\{(.*?)\}', src, re.DOTALL)
    if not m:
        return ClaimResult.build(
            expected=6, actual=None, severity='error',
            note='Could not parse provider_classes dict',
        )
    names = re.findall(r"'([^']+)'\s*:", m.group(1))
    expected = 6
    actual = len(names)
    severity = 'ok' if actual == expected else ('low' if abs(actual - expected) == 1 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"registered providers: {names}",
        fix_suggestion=(
            f"Update CLAUDE.md to '{actual} LLM Providers'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='CLAUDE.md',
    claim_id='services_module_count',
    description="CLAUDE.md stats table: 'Services | ~300' (service modules in core/services/)",
)
def _claude_services_count() -> ClaimResult:
    """Count .py files (modules) under core/services/ — that's the metric
    CLAUDE.md cites as '~300'. Class-count (112) is a different metric
    measured in SERVICES.md/CAPABILITIES.md.
    """
    from pathlib import Path
    services_dir = Path(__file__).resolve().parent
    module_count = 0
    for py in services_dir.rglob('*.py'):
        if '__pycache__' in py.parts or py.name == '__init__.py':
            continue
        module_count += 1
    expected = 300  # refreshed Session 1100 — CLAUDE.md claims '~300'
    drift = abs(module_count - expected)
    severity = 'ok' if drift <= 50 else ('medium' if drift <= 150 else 'high')
    return ClaimResult.build(
        expected=f"~{expected}",
        actual=module_count,
        severity=severity,
        note=(
            "Counts non-__init__.py files in core/services/. Service-class "
            "count (different metric) is measured by SERVICES.md/CAPABILITIES.md "
            "claims separately."
        ),
        fix_suggestion=(
            f"Update CLAUDE.md services row to '~{module_count}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='CLAUDE.md',
    claim_id='database_models_397',
    description="CLAUDE.md stats table: 'Database Models | 397+'",
)
def _claude_db_models() -> ClaimResult:
    from django.apps import apps
    concrete = [m for m in apps.get_models() if not m._meta.abstract and not m._meta.proxy]
    actual = len(concrete)
    expected = 397
    # Floor claim — OK if above
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
        note=(
            "Five contradictions: current/INDEX 324+, MODELS 324+, "
            "DATABASE_MODEL_REFERENCE 386+, infrastructure 386+, CLAUDE 397+, "
            "BACKEND_INVENTORY 413"
        ),
        fix_suggestion=(
            f"Unify all model count claims to '{actual}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='CLAUDE.md',
    claim_id='agent_taxonomy_reconciliation',
    description="CLAUDE.md stats: '83 AGENT_MAP (74 enabled, 8 rerouted, 1 blocked)'",
)
def _claude_agent_taxonomy() -> ClaimResult:
    """Verify the reconciliation sum: fully_enabled + rerouted + blocked == AGENT_MAP."""
    from core.agent_router import AgentRouter
    from core.models_unified_system import AgentControlEntry
    agent_map_keys = set(AgentRouter.AGENT_MAP.keys())
    total = len(agent_map_keys)
    blocked = list(AgentControlEntry.get_blocked_names())
    # Same hardcoded set as td_handlers_ops.py:3618. Note: this set is the
    # *routing* whitelist, and may include legacy names that no longer
    # exist in AGENT_MAP (Session 1115 audit caught ContentDistributionAgent
    # in this state). Counting must intersect with AGENT_MAP, otherwise
    # `fully_enabled` undercounts and the totals don't add to `total`.
    non_specialist = {
        'WorkflowAgent', 'VideoAgent', 'CodeGeneratorAgent', 'DevOpsAgent',
        'FullStackDeveloperAgent', 'CodeReviewAgent', 'ContentDistributionAgent',
        'COOAgent', 'CTOAgent', 'AudioAgent',
    }
    rerouted = sorted(non_specialist & agent_map_keys - set(blocked))
    fully_enabled = total - len(blocked) - len(rerouted)
    phantom = sorted(non_specialist - agent_map_keys)
    # Refreshed Session 1115 — matches AGENT_MAP-strict reality (74/8/1)
    expected_claim = "74 enabled + 8 rerouted + 1 blocked = 83"
    actual_claim = f"{fully_enabled} enabled + {len(rerouted)} rerouted + {len(blocked)} blocked = {total}"
    matches = (fully_enabled == 74 and len(rerouted) == 8 and len(blocked) == 1 and total == 83)
    severity = 'ok' if matches else 'medium'
    note_parts = [
        f"blocked (AgentControlEntry): {blocked}",
        f"rerouted (in AGENT_MAP ∩ _NON_SPECIALIST): {rerouted}",
    ]
    if phantom:
        note_parts.append(
            f"phantom _NON_SPECIALIST entries (not in AGENT_MAP): {phantom}"
        )
    return ClaimResult.build(
        expected=expected_claim,
        actual=actual_claim,
        severity=severity,
        note='; '.join(note_parts),
        fix_suggestion=(
            f"Update CLAUDE.md to '{fully_enabled} enabled, "
            f"{len(rerouted)} rerouted, {len(blocked)} blocked'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='core/epa_handlers/td_handlers_ops.py',
    claim_id='non_specialist_phantom_entries',
    description="`_NON_SPECIALIST` route set should not contain names that aren't in AGENT_MAP",
)
def _non_specialist_phantom_entries() -> ClaimResult:
    """Surface any `_NON_SPECIALIST` entries that don't resolve to an AGENT_MAP key.

    Session 1115 audit caught ``ContentDistributionAgent`` in this state: it
    was being counted as "rerouted" in the agent taxonomy and shown as such
    in CLAUDE.md, but no class with that name exists and AGENT_MAP doesn't
    reference it. The routing whitelist and the agent registry drifted apart.

    A phantom entry is fail-soft (the router never matches it) but it
    pollutes counts and is a sign that the routing layer hasn't been cleaned
    up after agent removals.
    """
    from core.agent_router import AgentRouter
    agent_map_keys = set(AgentRouter.AGENT_MAP.keys())
    non_specialist = {
        'WorkflowAgent', 'VideoAgent', 'CodeGeneratorAgent', 'DevOpsAgent',
        'FullStackDeveloperAgent', 'CodeReviewAgent', 'ContentDistributionAgent',
        'COOAgent', 'CTOAgent', 'AudioAgent',
    }
    phantom = sorted(non_specialist - agent_map_keys)
    severity = 'ok' if not phantom else 'low'
    return ClaimResult.build(
        expected='no _NON_SPECIALIST entries outside AGENT_MAP',
        actual=phantom or 'none',
        severity=severity,
        note=(
            f"_NON_SPECIALIST has {len(non_specialist)} entries; "
            f"{len(non_specialist & agent_map_keys)} resolve to AGENT_MAP"
        ),
        fix_suggestion=(
            "Remove the phantom name(s) from `_NON_SPECIALIST` in "
            "`core/epa_handlers/td_handlers_ops.py`, "
            "`core/services/platform_inventory.py`, and "
            "`core/services/doc_claim_verification.py` (kept in sync). "
            "If a legacy class is intentionally being kept on the reroute "
            "whitelist, document why with a comment."
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='core/models_unified_system.py',
    claim_id='agent_memory_types_7',
    description="AgentMemory.MEMORY_TYPE_CHOICES: docstring/docs claim 7 types (success/failure/preference/technique/insight/interaction/feedback)",
)
def _agent_memory_type_choices() -> ClaimResult:
    """Count MEMORY_TYPE_CHOICES on the AgentMemory model."""
    from core.models_unified_system import AgentMemory
    choices = getattr(AgentMemory, 'MEMORY_TYPE_CHOICES', [])
    actual = len(choices)
    expected = 7
    severity = 'ok' if actual == expected else ('low' if abs(actual - expected) <= 1 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"types: {[c[0] for c in choices]}",
        fix_suggestion=(
            f"Sync docs — MEMORY_TYPE_CHOICES has {actual} entries"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='core/models_document_registry.py',
    claim_id='initiative_pipeline_stages_5',
    description="STAGE_TYPES: docs claim 'Stage 1..5 (research, planning, evaluation, specification, execution)'",
)
def _initiative_stage_types() -> ClaimResult:
    from core.models_document_registry import STAGE_TYPES
    actual = len(STAGE_TYPES)
    expected = 5
    severity = 'ok' if actual == expected else 'medium'
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"stage types: {dict(STAGE_TYPES)}",
        fix_suggestion=(
            f"Sync docs — STAGE_TYPES defines {actual} stages"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/topics/content-pipeline.md',
    claim_id='reviewer_panel_always_two',
    description="docs/topics/content-pipeline.md: '3-reviewer panel (Skeptic + FactCheck always; Domain conditional)'",
)
def _content_reviewer_panel() -> ClaimResult:
    """Count reviewers invoked unconditionally in content_review_panel_v2.py."""
    import re
    from pathlib import Path
    src = (Path(__file__).resolve().parent / 'content_review_panel_v2.py').read_text()
    always_matches = re.findall(
        r"(?:_call_llm_reviewer|reviews\.append)\([^,]+,\s*[^,]+,\s*'(Skeptic|FactCheck)Reviewer'",
        src,
    )
    actual_always = len(set(always_matches))
    # Must have Skeptic + FactCheck both always
    expected_always = 2
    severity = 'ok' if actual_always == expected_always else 'medium'
    return ClaimResult.build(
        expected=f"{expected_always} always-run reviewers (Skeptic + FactCheck)",
        actual=f"{actual_always} always-run: {sorted(set(always_matches))}",
        severity=severity,
        note=(
            "DomainPersonaReviewer is conditional on domain confidence >= 0.2, "
            "so 3-panel claim is a max; 2 always run"
        ),
        fix_suggestion=(
            "Clarify docs/topics/content-pipeline.md: '2 always + 1 conditional'"
            if severity != 'ok' else None
        ),
    )


# ---------------------------------------------------------------------------
# Session 1115 — forward-drift guards (DB-free; safe in CI without Postgres).
# These exist so that future hand-edits / inventory-block refreshes that
# diverge from runtime get flagged without needing the autoblock pipeline.
# ---------------------------------------------------------------------------


@register_claim(
    doc='CLAUDE.md',
    claim_id='frontend_route_count',
    description="CLAUDE.md stats table: 'Frontend | 61 routes' in frontend/src/App.tsx",
)
def _claude_frontend_routes() -> ClaimResult:
    """Count `<Route ` declarations in App.tsx."""
    import re
    from pathlib import Path
    app = Path(__file__).resolve().parents[2] / 'frontend' / 'src' / 'App.tsx'
    if not app.exists():
        return ClaimResult.build(
            expected=61, actual=None, severity='error',
            note=f"App.tsx not at {app}",
        )
    actual = len(re.findall(r'<Route\s', app.read_text()))
    expected = 61
    severity = 'ok' if actual == expected else ('low' if abs(actual - expected) <= 2 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note="counts top-level `<Route ` JSX tags",
        fix_suggestion=(
            f"Update CLAUDE.md frontend row to '{actual} routes'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='CLAUDE.md',
    claim_id='procfile_entry_count',
    description="CLAUDE.md stats table: 'Procfile entries | 11' (release + web + 7 celery + code-worker + resolve-node)",
)
def _claude_procfile_entries() -> ClaimResult:
    """Count non-comment, non-blank lines in Procfile that look like `name: cmd`."""
    from pathlib import Path
    p = Path(__file__).resolve().parents[2] / 'Procfile'
    if not p.exists():
        return ClaimResult.build(
            expected=11, actual=None, severity='error', note='Procfile missing'
        )
    entries = [
        l for l in p.read_text().splitlines()
        if l.strip() and not l.lstrip().startswith('#') and ':' in l
    ]
    actual = len(entries)
    expected = 11
    severity = 'ok' if actual == expected else 'medium'
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"names: {[l.split(':',1)[0] for l in entries]}",
        fix_suggestion=(
            f"Update CLAUDE.md Procfile row to '{actual}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='CLAUDE.md',
    claim_id='signal_pattern_type_count',
    description="CLAUDE.md stats: '10 SignalCluster pattern types' (demand_spike, trend_emergence, …)",
)
def _claude_signal_pattern_types() -> ClaimResult:
    """Read SignalCluster.pattern_type choices."""
    from core.models import SignalCluster
    f = SignalCluster._meta.get_field('pattern_type')
    raw_choices = getattr(f, 'choices', None) or []
    choices = [c[0] for c in raw_choices]
    actual = len(choices)
    expected = 10
    severity = 'ok' if actual == expected else 'medium'
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"types: {choices}",
        fix_suggestion=(
            f"Update CLAUDE.md signal pattern types row to '{actual}'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='CLAUDE.md',
    claim_id='spider_registry_count',
    description="CLAUDE.md stats table: '80 spiders across 41 categories'",
)
def _claude_spider_count() -> ClaimResult:
    """Count registered spider classes via the module-level singleton."""
    from ai_core.spiders.spider_registry import get_spider_registry
    actual = len(get_spider_registry().list_spiders())
    expected = 80
    severity = 'ok' if actual == expected else ('low' if abs(actual - expected) <= 2 else 'medium')
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note='spider count comes from SpiderRegistry import-time registration',
        fix_suggestion=(
            f"Update CLAUDE.md spider row to '{actual} spiders'"
            if severity != 'ok' else None
        ),
    )


# ---------------------------------------------------------------------------
# Session 1115 — capability audit guards.
# These back the `docs/CAPABILITY_AUDIT.md` generator: if these regress,
# the audit doc silently loses information.
# ---------------------------------------------------------------------------


@register_claim(
    doc='docs/CAPABILITY_AUDIT.md',
    claim_id='all_agents_have_docstrings',
    description="Every AGENT_MAP class should have a class docstring (drives capability audit)",
)
def _all_agents_have_docstrings() -> ClaimResult:
    """Every class in AGENT_MAP must have a docstring.

    The capability audit (`docs/CAPABILITY_AUDIT.md`) uses class docstrings
    as the canonical "what does this agent do" string. An agent without one
    becomes invisible in the audit and Chris's "what is this thing capable of"
    answer.
    """
    import inspect as _inspect
    from core.agent_router import AgentRouter
    missing = sorted(
        name for name, cls in AgentRouter.AGENT_MAP.items()
        if not (_inspect.getdoc(cls) or '').strip()
    )
    severity = 'ok' if not missing else 'medium'
    return ClaimResult.build(
        expected='all 83 agents have a class docstring',
        actual=f"{len(AgentRouter.AGENT_MAP) - len(missing)} / "
               f"{len(AgentRouter.AGENT_MAP)} have docstrings",
        severity=severity,
        note=f"missing: {missing}" if missing else 'all good',
        fix_suggestion=(
            f"Add a class docstring to the {len(missing)} agent(s) listed in `note`. "
            f"First non-empty line of the docstring is what shows up in "
            f"`docs/CAPABILITY_AUDIT.md`."
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/SPIDER_AUDIT.md',
    claim_id='all_spiders_have_docstrings',
    description="Every registered spider class should have a class docstring (drives spider audit)",
)
def _all_spiders_have_docstrings() -> ClaimResult:
    """Every spider class registered with `SpiderRegistry` must have a docstring.

    The spider capability audit (`docs/SPIDER_AUDIT.md`) uses class docstrings
    as the "what does this spider fetch" string. Missing one means the spider
    becomes invisible in the audit.
    """
    import inspect as _inspect
    from ai_core.spiders.spider_registry import get_spider_registry
    reg = get_spider_registry()
    missing = sorted(
        name for name, cls in reg.spider_classes.items()
        if not (_inspect.getdoc(cls) or '').strip()
    )
    total = len(reg.spider_classes)
    severity = 'ok' if not missing else 'medium'
    return ClaimResult.build(
        expected='all registered spider classes have a class docstring',
        actual=f"{total - len(missing)} / {total} have docstrings",
        severity=severity,
        note=f"missing: {missing}" if missing else 'all good',
        fix_suggestion=(
            f"Add a class docstring to the {len(missing)} spider class(es) "
            f"listed in `note`. First non-empty line is what shows up in "
            f"`docs/SPIDER_AUDIT.md`."
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/SPIDER_AUDIT.md',
    claim_id='spider_category_count',
    description="docs/SPIDER_AUDIT.md headline: '41 distinct categories'",
)
def _spider_category_count() -> ClaimResult:
    """Count distinct categories in spider registry configs.

    The spider audit headlines the category count alongside the spider count.
    Drift on either is worth surfacing.
    """
    from ai_core.spiders.spider_registry import get_spider_registry
    reg = get_spider_registry()
    categories = {
        (cfg or {}).get('category', 'unknown')
        for cfg in reg.spider_configs.values()
    }
    actual = len(categories)
    expected = 41  # refreshed Session 1115 — matches current registry
    severity = 'ok' if actual == expected else (
        'low' if abs(actual - expected) <= 2 else 'medium'
    )
    return ClaimResult.build(
        expected=expected,
        actual=actual,
        severity=severity,
        note=f"categories: {sorted(categories)}",
        fix_suggestion=(
            f"Update docs/SPIDER_AUDIT.md headline + CLAUDE.md spider row to "
            f"'{actual} categories'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/ML_AUDIT.md',
    claim_id='ml_capability_dirs_present',
    description="All 9 ML capability subdirectories exist under ml/ (anomaly_detection, auto_selection, automation, core, graph_neural_network, integrations, reinforcement_learning, time_series, training)",
)
def _ml_capability_dirs_present() -> ClaimResult:
    """Catch ML capability subdirs being removed or renamed.

    The ML audit (`docs/ML_AUDIT.md`) is federated — it walks each named
    capability subdirectory under `ml/`. If a subdir disappears the audit
    silently drops that capability from its overview. This claim catches
    that.

    Session 1115 baseline: 9 capability subdirs.
    """
    from pathlib import Path
    repo_root = Path(__file__).resolve().parents[2]
    ml_dir = repo_root / 'ml'
    expected = {
        'anomaly_detection', 'auto_selection', 'automation', 'core',
        'graph_neural_network', 'integrations', 'reinforcement_learning',
        'time_series', 'training',
    }
    if not ml_dir.exists():
        return ClaimResult.build(
            expected=f"{len(expected)} ML capability dirs present",
            actual='ml/ missing',
            severity='high',
        )
    present = {p.name for p in ml_dir.iterdir() if p.is_dir() and not p.name.startswith('_')}
    missing = sorted(expected - present)
    extra = sorted(present - expected - {'data', 'logs', 'management', 'migrations'})
    severity = 'ok' if not missing else 'medium'
    return ClaimResult.build(
        expected=f"all of: {sorted(expected)}",
        actual=f"present: {sorted(expected & present)}; missing: {missing}",
        severity=severity,
        note=(
            f"missing: {missing}; "
            f"extra (not in expected): {extra}"
            if missing or extra else 'all good'
        ),
        fix_suggestion=(
            f"Restore the missing capability subdir(s) under ml/, or "
            f"update the expected set in `_ml_capability_dirs_present`. "
            f"If a new capability has been added (in `extra`), update the "
            f"expected set + add its primary class(es) to ML_AUDIT.md by "
            f"regenerating with `python manage.py build_ml_audit`."
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/LEARNING_BRIDGE_AUDIT.md',
    claim_id='learning_bridges_documented',
    description="Every learning bridge module under core/learning_bridges/ has a module docstring + at least one learning-loop class",
)
def _learning_bridges_documented() -> ClaimResult:
    """Catch under-documented learning bridges.

    Each `*_bridge.py` under `core/learning_bridges/` is supposed to be a
    Django-signal-driven shim that feeds runtime events to the learning
    pipeline. If the module has no docstring or contains no learning-loop
    class, the bridge audit can't describe what the bridge does.

    Session 1115 baseline: 8 bridges, 9 learning-loop classes, 8/8 with
    docstrings.
    """
    import ast
    from pathlib import Path
    repo_root = Path(__file__).resolve().parents[2]
    bridges_dir = repo_root / 'core' / 'learning_bridges'
    if not bridges_dir.exists():
        return ClaimResult.build(
            expected='core/learning_bridges/ exists',
            actual='missing',
            severity='high',
            note='directory removed?',
        )
    problems: list[str] = []
    total = 0
    for path in sorted(bridges_dir.glob('*_bridge.py')):
        total += 1
        try:
            tree = ast.parse(path.read_text(errors='ignore'))
        except SyntaxError as e:
            problems.append(f'{path.name}: parse error {e}')
            continue
        if not (ast.get_docstring(tree) or '').strip():
            problems.append(f'{path.name}: module docstring missing')
        has_class = any(
            isinstance(n, ast.ClassDef)
            and not any(
                isinstance(b, ast.Attribute) and getattr(b, 'attr', '') == 'Model'
                for b in n.bases
            )
            for n in tree.body
        )
        if not has_class:
            problems.append(f'{path.name}: no learning-loop class')
    severity = 'ok' if not problems else 'low'
    return ClaimResult.build(
        expected=f'all {total} bridges documented + have a class',
        actual=(
            f'{total - len(problems)} / {total} clean'
            if problems else f'{total}/{total} documented'
        ),
        severity=severity,
        note=f"problems: {problems}" if problems else 'all bridges documented',
        fix_suggestion=(
            "Add the missing module docstring or learning-loop class to "
            "each bridge listed in `note`."
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/BODY_SYSTEM_AUDIT.md',
    claim_id='body_systems_fully_wired',
    description="All 9 body systems in run_all_systems_scan resolve to a service module with a docstring + get_vitals()",
)
def _body_systems_fully_wired() -> ClaimResult:
    """Catch regressions in the body-system wiring.

    Each body system listed in `body_systems = [...]` inside
    `core/tasks.py::run_all_systems_scan` must:
      (a) have a module at `core/services/<name>.py`,
      (b) define a primary class with a docstring,
      (c) expose a `get_vitals()` method on that class.

    If any of those break, `run_all_systems_scan` will degrade — either
    raising an ImportError or skipping the system in its `if system == X`
    chain. Audit (Session 1115) confirms 9/9 wired; this claim catches
    future regressions.
    """
    import ast
    import re as _re
    from pathlib import Path
    repo_root = Path(__file__).resolve().parents[2]
    src = (repo_root / 'core' / 'tasks.py').read_text(errors='ignore')
    m = _re.search(r"body_systems\s*=\s*\[([^\]]+)\]", src)
    systems = _re.findall(r"'([^']+)'", m.group(1)) if m else []
    problems: list[str] = []
    for name in systems:
        mod_path = repo_root / 'core' / 'services' / f'{name}.py'
        if not mod_path.exists():
            problems.append(f'{name}: missing module {mod_path.name}')
            continue
        try:
            tree = ast.parse(mod_path.read_text(errors='ignore'))
        except SyntaxError as e:
            problems.append(f'{name}: parse error {e}')
            continue
        primary_class = None
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and (
                node.name.endswith('Service')
                or node.name.endswith('Monitor')
                or node.name.endswith('Coordinator')
                or node.name.endswith('System')
            ):
                primary_class = node
                break
        if primary_class is None:
            problems.append(f'{name}: no Service/Monitor class')
            continue
        if not (ast.get_docstring(primary_class) or '').strip():
            problems.append(f'{name}: class missing docstring')
        has_vitals = any(
            isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))
            and s.name == 'get_vitals'
            for s in primary_class.body
        )
        if not has_vitals:
            problems.append(f'{name}: no get_vitals()')
    severity = 'ok' if not problems else 'medium'
    return ClaimResult.build(
        expected=f'all {len(systems)} body systems fully wired',
        actual=(
            f'{len(systems) - sum(1 for _ in problems)} fully wired'
            if problems else f'{len(systems)}/{len(systems)} wired'
        ),
        severity=severity,
        note=f"systems: {systems}; problems: {problems}",
        fix_suggestion=(
            "Address each `<name>: <issue>` entry in `note` — restore the "
            "missing module, class docstring, or `get_vitals()` method."
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/ADVISOR_AUDIT.md',
    claim_id='advisor_count_matches_doc',
    description="advisors.registry.advisor_registry materializes the documented 25 advisors (14 named + 11 specialists)",
)
def _advisor_count_matches_doc() -> ClaimResult:
    """Compare the live AdvisorProfile registry against the documented total.

    The audit (Session 1115) caught CLAUDE.md claiming `32 (10 named + 22
    specialists)` while the registry only materializes 25 (14 named + 11
    specialists). Aligned in the same session; this claim catches future
    drift on either side.
    """
    from advisors.registry import advisor_registry
    rows = list(advisor_registry.advisors.values())
    n_total = len(rows)
    n_named = sum(1 for r in rows if '(AI Model)' in (r.name or ''))
    n_specialists = n_total - n_named
    expected_total = 25
    expected_named = 14
    expected_specialists = 11
    matches = (
        n_total == expected_total
        and n_named == expected_named
        and n_specialists == expected_specialists
    )
    severity = 'ok' if matches else 'medium'
    return ClaimResult.build(
        expected=f"{expected_total} total ({expected_named} named + "
                 f"{expected_specialists} specialists)",
        actual=f"{n_total} total ({n_named} named + {n_specialists} specialists)",
        severity=severity,
        note='from advisor_registry.advisors',
        fix_suggestion=(
            f"Update CLAUDE.md (Advisors row) + docs/ADVISOR_AUDIT.md to "
            f"'{n_total} ({n_named} named + {n_specialists} specialists)'"
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/ADVISOR_AUDIT.md',
    claim_id='all_advisors_have_background',
    description="Every AdvisorProfile should have a `background` text (drives ADVISOR_AUDIT.md per-advisor description)",
)
def _all_advisors_have_background() -> ClaimResult:
    """Background is the primary description shown for each advisor.

    Missing one makes the advisor effectively undescribed in the capability
    audit.
    """
    from advisors.registry import advisor_registry
    missing = sorted(
        (r.name or r.id) for r in advisor_registry.advisors.values()
        if not (r.background or '').strip()
    )
    total = len(advisor_registry.advisors)
    severity = 'ok' if not missing else 'low'
    return ClaimResult.build(
        expected='all advisors have a background',
        actual=f"{total - len(missing)} / {total}",
        severity=severity,
        note=f"missing: {missing}" if missing else 'all good',
        fix_suggestion=(
            f"Add a `background` to the advisor(s) in `note`. "
            f"Edit `advisors/registry.py::_initialize_advisor_network`."
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/BEAT_AUDIT.md',
    claim_id='beat_schedule_task_refs_resolve',
    description="Every static beat entry's `task` ref should resolve in the Celery task registry",
)
def _beat_schedule_task_refs_resolve() -> ClaimResult:
    """Catch scheduled tasks that fail at dispatch time.

    Each entry in `app.conf.beat_schedule` declares a task path. If that
    path isn't in `app.tasks` at worker start (autodiscover misses it, or
    the path is a typo), the schedule fires but Celery can't dispatch.
    Silent failure unless monitored.

    Session 1115 audit caught 7 of these in `core/celery.py`:
    `ai_core.tasks.{clean_stale_data, collect_real_opportunities,
    warm_up_spider_network}`, `ml.cleanup_old_model_files`,
    `sports.cleanup_old_predictions`,
    `intelligence.tasks.{cleanup_old_opportunities, scan_spider_opportunities}`.
    The underlying functions exist; Celery autodiscover isn't picking up
    those modules. Fix is to add them to `app.conf.imports` in
    `core/celery.py:317` or to ensure the apps' `tasks.py` modules import
    cleanly at boot.
    """
    from core.celery import app as celery_app
    registry = set(celery_app.tasks.keys())
    schedule = dict(celery_app.conf.beat_schedule or {})
    broken = sorted(
        f"{name} -> {(entry or {}).get('task', '<no task>')}"
        for name, entry in schedule.items()
        if (entry or {}).get('task') not in registry
    )
    severity = 'ok' if not broken else 'medium'
    return ClaimResult.build(
        expected='no broken task refs in app.conf.beat_schedule',
        actual=f"{len(broken)} broken" if broken else 'none',
        severity=severity,
        note=(
            f"{len(schedule)} static beat entries · "
            f"{len(registry)} registered tasks · broken: {broken[:8]}"
            + ('…' if len(broken) > 8 else '')
        ),
        fix_suggestion=(
            "For each broken ref: confirm the task function exists, then "
            "either add the parent app's `tasks` module to `app.conf.imports` "
            "in `core/celery.py:317`, or fix the dotted path in "
            "`app.conf.beat_schedule`."
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/PA_TOOL_AUDIT.md',
    claim_id='pa_schemas_have_descriptions',
    description="Every PA tool schema needs a `description` — the LLM uses it as the routing signal",
)
def _pa_schemas_have_descriptions() -> ClaimResult:
    """Schema description is the LLM's routing signal at function-call time.

    A schema with no description still appears in the function list, but
    the LLM has nothing to base its choice on — effectively invisible. The
    audit (`docs/PA_TOOL_AUDIT.md`) treats this as a hard finding.
    """
    from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
    missing = sorted(
        s.get('name', '<unnamed>')
        for s in PA_TOOL_SCHEMAS
        if not (s.get('description', '') or '').strip()
    )
    total = len(PA_TOOL_SCHEMAS)
    severity = 'ok' if not missing else 'medium'
    return ClaimResult.build(
        expected='all PA schemas have a description',
        actual=f"{total - len(missing)} / {total} have descriptions",
        severity=severity,
        note=f"missing: {missing}" if missing else 'all good',
        fix_suggestion=(
            "Add a description to the schema(s) in `note`. "
            "The LLM cannot route to a description-less tool."
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/PA_TOOL_AUDIT.md',
    claim_id='pa_handlers_reachable',
    description="Registered tool handlers should be reachable: either via a schema or `run_agent`",
)
def _pa_handlers_reachable() -> ClaimResult:
    """Catches handlers that the LLM has no way to invoke.

    A handler is reachable if:
      (a) a schema exists with the same name, OR
      (b) the handler's name is listed in `run_agent.agent_name.enum`.

    Anything else is a dead registration — the handler runs at startup but
    the LLM never calls it because it doesn't know it exists. Surfaces real
    drift (Session 1115 caught `distribution_agent` in this state).
    """
    from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
    from core.services.tool_dispatcher import ToolDispatcher
    td = ToolDispatcher()
    schema_names = {s.get('name', '') for s in PA_TOOL_SCHEMAS if s.get('name')}
    run_agent_schema = next(
        (s for s in PA_TOOL_SCHEMAS if s.get('name') == 'run_agent'), {}
    )
    params = (run_agent_schema or {}).get('parameters', {}) or {}
    props = params.get('properties', {}) or {}
    run_agent_targets = set(
        (props.get('agent_name') or {}).get('enum', []) or []
    )
    handlers = set(td._tool_handlers.keys())  # noqa: SLF001
    orphans = sorted(handlers - schema_names - run_agent_targets)
    severity = 'ok' if not orphans else 'low'
    return ClaimResult.build(
        expected='no handler-only registrations outside run_agent.agent_name enum',
        actual=orphans or 'none',
        severity=severity,
        note=(
            f"{len(handlers)} handlers · {len(schema_names)} schemas · "
            f"{len(run_agent_targets)} agents reachable via run_agent meta-tool"
        ),
        fix_suggestion=(
            "Either add the orphan(s) to `run_agent.agent_name.enum` in "
            "`core/services/pa_tool_schemas.py`, give them their own schema, "
            "or remove the `self.register(...)` call from "
            "`core/services/tool_dispatcher.py`."
            if severity != 'ok' else None
        ),
    )


@register_claim(
    doc='docs/CAPABILITY_AUDIT.md',
    claim_id='agent_map_key_matches_class_name',
    description="Each AGENT_MAP key should match the agent class's `name` class attribute",
)
def _agent_map_key_matches_class_name() -> ClaimResult:
    """The AGENT_MAP key is what callers use to route; the class `name`
    attribute is what the agent reports about itself in execution metadata.

    Mismatches cause confusing telemetry — an agent named ``Foo`` in
    AGENT_MAP shows up as ``Bar`` in AgentExecution rows. Worth catching.
    Agents that don't declare a `name` attribute at all are skipped (some
    base classes leave it unset).
    """
    from core.agent_router import AgentRouter
    mismatched = []
    for name, cls in AgentRouter.AGENT_MAP.items():
        declared = getattr(cls, 'name', None)
        if declared and declared != name:
            mismatched.append((name, declared))
    severity = 'ok' if not mismatched else 'low'
    return ClaimResult.build(
        expected='AGENT_MAP key == cls.name on every entry that declares one',
        actual=f"{len(mismatched)} mismatch(es)",
        severity=severity,
        note=(
            'mismatches: '
            + ', '.join(f'{k}->declares "{v}"' for k, v in mismatched)
            if mismatched else 'all matched'
        ),
        fix_suggestion=(
            "Update either the AGENT_MAP key or the class `name` attribute "
            "so they agree."
            if severity != 'ok' else None
        ),
    )
