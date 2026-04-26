"""Platform Inventory — runtime-derived master snapshot of the platform (Session 1099).

Complements ``doc_claim_verification`` (which checks doc CLAIMS against code)
by producing a single authoritative dump of the platform's actual state. The
resulting Markdown is intended as the go-to reference when the docs are stale
or contradictory.

The data is produced in two phases:

1. ``gather_inventory()`` — returns a structured dict:
   ``{generated_at, git_sha, sections: [{slug, title, headline, items, notes}]}``

2. ``render_markdown(inventory)`` — renders the dict to a single Markdown string.

The ``generate_platform_inventory`` management command glues the two together
and writes to ``docs/PLATFORM_INVENTORY.md``.
"""
from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CORE_DIR = REPO_ROOT / 'core'
AI_CORE_DIR = REPO_ROOT / 'ai_core'
FRONTEND_DIR = REPO_ROOT / 'frontend' / 'src'


# =============================================================================
# Data shape
# =============================================================================


@dataclass
class InventorySection:
    slug: str
    title: str
    headline: str            # one-sentence summary with primary count
    items: list[Any] = field(default_factory=list)  # rows for the body table
    columns: Optional[list[str]] = None             # markdown table headers
    notes: Optional[str] = None                     # optional free text
    code_location: Optional[str] = None             # path or module reference
    error: Optional[str] = None                     # if collection failed


# =============================================================================
# Collectors
# =============================================================================


def _safe(fn: Callable[[], InventorySection]) -> InventorySection:
    """Run a collector, trapping exceptions into a section with ``error``."""
    try:
        return fn()
    except Exception as e:  # noqa: BLE001
        import traceback
        logger.warning("inventory collector failed: %s", e)
        return InventorySection(
            slug='error',
            title='Collector Error',
            headline=f'{type(e).__name__}: {e}',
            error=traceback.format_exc(limit=3),
        )


def collect_agents() -> InventorySection:
    from core.agent_router import AgentRouter
    from core.models_unified_system import Agent, AgentControlEntry
    agent_map = AgentRouter.AGENT_MAP
    blocked = list(AgentControlEntry.get_blocked_names())
    non_specialist = {
        'WorkflowAgent', 'VideoAgent', 'CodeGeneratorAgent', 'DevOpsAgent',
        'FullStackDeveloperAgent', 'CodeReviewAgent', 'ContentDistributionAgent',
        'COOAgent', 'CTOAgent', 'AudioAgent',
    }
    rerouted = sorted(non_specialist - set(blocked))
    fully_enabled = len(agent_map) - len(blocked) - len(rerouted)

    items: list[dict[str, Any]] = []
    for name in sorted(agent_map.keys()):
        cls = agent_map[name]
        if name in blocked:
            status = 'blocked'
        elif name in rerouted:
            status = 'rerouted'
        else:
            status = 'enabled'
        items.append({
            'name': name,
            'module': getattr(cls, '__module__', '?'),
            'status': status,
        })

    db_total = Agent.objects.count()
    by_type: dict[str, int] = {}
    for row in Agent.objects.values_list('agent_type', flat=True):
        by_type[row or '(blank)'] = by_type.get(row or '(blank)', 0) + 1

    type_breakdown = ', '.join(
        f"{t}={c}" for t, c in sorted(by_type.items(), key=lambda x: -x[1])[:10]
    )
    notes = (
        f"AGENT_MAP total = {len(agent_map)} "
        f"({fully_enabled} enabled + {len(rerouted)} rerouted + {len(blocked)} blocked). "
        f"DB Agent rows = {db_total}. "
        f"Top agent_type breakdown: {type_breakdown}. "
        f"Blocked: {blocked}. Rerouted: {rerouted}."
    )
    return InventorySection(
        slug='agents',
        title='Agents',
        headline=(
            f"{len(agent_map)} agents in AGENT_MAP ({fully_enabled} enabled, "
            f"{len(rerouted)} rerouted, {len(blocked)} blocked); "
            f"{db_total} rows in Agent table."
        ),
        items=items,
        columns=['Name', 'Module', 'Status'],
        notes=notes,
        code_location='core/agent_router.py AGENT_MAP',
    )


def collect_spiders() -> InventorySection:
    from ai_core.spiders.spider_registry import get_spider_registry
    reg = get_spider_registry()
    spiders = reg.list_spiders()
    stats = reg.get_spider_count()
    raw_by_cat = stats.get('by_category')
    by_cat: dict[str, int] = raw_by_cat if isinstance(raw_by_cat, dict) else {}

    items = []
    for name in sorted(spiders.keys()):
        info = spiders[name]
        items.append({
            'name': name,
            'category': info.get('category', 'unknown'),
            'class': info.get('class', ''),
            'priority': info.get('priority', 5),
            'placeholder': 'yes' if info.get('is_placeholder') else 'no',
        })

    working = sum(1 for s in spiders.values() if not s.get('is_placeholder'))
    categories_desc = ', '.join(f"{k}={v}" for k, v in sorted(by_cat.items(), key=lambda x: -x[1])[:10])
    notes = (
        f"Working (non-placeholder): {working}. "
        f"Categories ({len(by_cat)}): top 10 by count — {categories_desc}."
    )
    return InventorySection(
        slug='spiders',
        title='Spiders',
        headline=f"{len(spiders)} spiders across {len(by_cat)} categories ({working} working, {len(spiders)-working} placeholder)",
        items=items,
        columns=['Name', 'Category', 'Class', 'Priority', 'Placeholder'],
        notes=notes,
        code_location='ai_core/spiders/spider_registry.py',
    )


def collect_services() -> InventorySection:
    services_dir = CORE_DIR / 'services'
    files: list[Path] = [
        p for p in services_dir.rglob('*.py')
        if '__pycache__' not in p.parts and p.name != '__init__.py'
    ]
    service_classes: list[tuple[str, str]] = []  # (class_name, relative_path)
    for py in files:
        try:
            src = py.read_text(errors='ignore')
        except OSError:
            continue
        for m in re.finditer(r'^class\s+([A-Z]\w*Service)\b', src, re.MULTILINE):
            service_classes.append((m.group(1), str(py.relative_to(REPO_ROOT))))

    items = [{'class': c, 'file': f} for c, f in sorted(service_classes)]
    return InventorySection(
        slug='services',
        title='Services',
        headline=f"{len(service_classes)} `*Service` classes across {len(files)} files in core/services/",
        items=items,
        columns=['Class', 'File'],
        code_location='core/services/',
    )


def collect_celery_tasks() -> InventorySection:
    from core.celery import app as celery_app
    tasks = sorted(t for t in celery_app.tasks.keys() if not t.startswith('celery.'))
    prefix_counts: dict[str, int] = {}
    for t in tasks:
        prefix = '.'.join(t.split('.')[:-1]) or '(top-level)'
        prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
    prefix_desc = ', '.join(
        f"{k}={v}" for k, v in sorted(prefix_counts.items(), key=lambda x: -x[1])[:10]
    )
    return InventorySection(
        slug='celery-tasks',
        title='Celery Tasks',
        headline=f"{len(tasks)} user-defined Celery tasks (excludes celery.* internals)",
        items=[{'name': t} for t in tasks],
        columns=['Task'],
        notes=f"Top 10 modules by task count: {prefix_desc}",
        code_location='core/tasks.py + siblings',
    )


def collect_beat_schedule() -> InventorySection:
    from django_celery_beat.models import PeriodicTask
    enabled = PeriodicTask.objects.filter(enabled=True).count()
    total = PeriodicTask.objects.count()
    rows = PeriodicTask.objects.values('name', 'task', 'enabled', 'queue').order_by('name')
    items = [
        {
            'name': r['name'],
            'task': r['task'],
            'enabled': 'yes' if r['enabled'] else 'no',
            'queue': r['queue'] or '(default)',
        }
        for r in rows
    ]
    return InventorySection(
        slug='beat-schedule',
        title='Celery Beat — Scheduled Tasks',
        headline=f"{enabled} enabled + {total - enabled} disabled = {total} PeriodicTask rows",
        items=items,
        columns=['Name', 'Task', 'Enabled', 'Queue'],
        code_location='django_celery_beat.PeriodicTask + core/tasks_schedule.py',
    )


def collect_pa_tools() -> InventorySection:
    from core.services.pa_tool_schemas import (
        PA_TOOL_SCHEMAS,
        TOOL_ENRICHMENT_MAP,
        TOOL_TO_INTENT_MAP,
    )
    names: list[str] = sorted([
        str(s['name']) for s in PA_TOOL_SCHEMAS
        if isinstance(s, dict) and s.get('name')
    ])

    # Handler count from tool_dispatcher.py
    dispatcher = (CORE_DIR / 'services' / 'tool_dispatcher.py').read_text()
    handler_lines = re.findall(r'^\s*self\.register\(\s*"([^"]+)"', dispatcher, re.MULTILINE)

    enrichment_services = set()
    for lst in TOOL_ENRICHMENT_MAP.values():
        enrichment_services.update(lst or [])

    items = [{'schema': n, 'intent': TOOL_TO_INTENT_MAP.get(n, '')} for n in names]
    notes = (
        f"Schemas: {len(names)}. Handlers (self.register in tool_dispatcher.py): "
        f"{len(handler_lines)}. Intent-mapped: {len(TOOL_TO_INTENT_MAP)}. "
        f"Unique enrichment services ({len(enrichment_services)}): {sorted(enrichment_services)}."
    )
    return InventorySection(
        slug='pa-tools',
        title='Personal Assistant (PA) Tools',
        headline=(
            f"{len(names)} tool schemas + {len(handler_lines)} registered handlers; "
            f"{len(enrichment_services)} enrichment services"
        ),
        items=items,
        columns=['Schema name', 'Canonical intent'],
        notes=notes,
        code_location='core/services/pa_tool_schemas.py + tool_dispatcher.py',
    )


def collect_database_models() -> InventorySection:
    from django.apps import apps
    models = [m for m in apps.get_models() if not m._meta.abstract and not m._meta.proxy]
    by_app: dict[str, int] = {}
    items: list[dict[str, str]] = []
    for m in sorted(models, key=lambda x: (x._meta.app_label, x._meta.object_name)):
        label = m._meta.app_label
        by_app[label] = by_app.get(label, 0) + 1
        items.append({
            'model': m._meta.object_name,
            'app': label,
            'table': m._meta.db_table,
        })
    app_desc = ', '.join(f"{k}={v}" for k, v in sorted(by_app.items(), key=lambda x: -x[1]))
    return InventorySection(
        slug='database-models',
        title='Database Models',
        headline=f"{len(models)} concrete models across {len(by_app)} apps",
        items=items,
        columns=['Model', 'App', 'DB Table'],
        notes=f"By app: {app_desc}",
    )


def collect_url_routes() -> InventorySection:
    prefix_counts: dict[str, int] = {}
    total = 0
    for urls_file in CORE_DIR.rglob('urls*.py'):
        if '__pycache__' in urls_file.parts:
            continue
        try:
            src = urls_file.read_text()
        except OSError:
            continue
        for m in re.finditer(r"path\(\s*['\"]([^'\"]*)", src):
            prefix = m.group(1).split('/')[0] or '(root)'
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
            total += 1
    sorted_prefixes = sorted(prefix_counts.items(), key=lambda x: -x[1])
    items = [{'prefix': p, 'count': c} for p, c in sorted_prefixes]
    return InventorySection(
        slug='url-routes',
        title='URL Routes',
        headline=f"{total} path() patterns across all core/urls*.py files",
        items=items,
        columns=['Prefix', 'Count'],
        code_location='core/urls*.py',
    )


def collect_views_files() -> InventorySection:
    files = sorted(
        p.name for p in CORE_DIR.glob('views*.py')
        if p.name != '__init__.py'
    )
    items = [{'file': f} for f in files]
    return InventorySection(
        slug='views-files',
        title='Django View Files',
        headline=f"{len(files)} files matching core/views*.py",
        items=items,
        columns=['File'],
        code_location='core/views*.py',
    )


def collect_mgmt_commands() -> InventorySection:
    cmds_dir = CORE_DIR / 'management' / 'commands'
    files = sorted(
        p.stem for p in cmds_dir.iterdir()
        if p.is_file() and p.suffix == '.py' and p.name != '__init__.py'
    )
    items = [{'command': f"python manage.py {name}"} for name in files]
    return InventorySection(
        slug='management-commands',
        title='Django Management Commands',
        headline=f"{len(files)} management commands in core/management/commands/",
        items=items,
        columns=['Command'],
        code_location='core/management/commands/',
    )


def collect_discord() -> InventorySection:
    bot_file = CORE_DIR / 'services' / 'discord_bot.py'
    src = bot_file.read_text() if bot_file.exists() else ''
    cogs = re.findall(r'^class\s+(\w+)\s*\([^)]*\bCog\b[^)]*\)\s*:', src, re.MULTILINE)
    decorators = re.findall(r'^\s*@\w+\.command\(', src, re.MULTILINE)
    app_cmds = re.findall(r'^\s*@app_commands\.command', src, re.MULTILINE)
    items = [{'cog': c} for c in sorted(cogs)]
    return InventorySection(
        slug='discord',
        title='Discord Integration',
        headline=(
            f"{len(decorators)} @*.command decorators, {len(app_cmds)} @app_commands.command, "
            f"{len(cogs)} Cog classes in discord_bot.py"
        ),
        items=items,
        columns=['Cog'],
        code_location='core/services/discord_bot.py',
    )


def collect_body_systems() -> InventorySection:
    # Canonical list from core/tasks.py run_all_systems_scan
    src = (CORE_DIR / 'tasks.py').read_text()
    m = re.search(r"body_systems\s*=\s*\[([^\]]+)\]", src)
    systems = []
    if m:
        systems = [s.strip().strip("'\"") for s in m.group(1).split(',') if s.strip()]
    items = [{'system': s} for s in systems]
    return InventorySection(
        slug='body-systems',
        title='Body Systems',
        headline=f"{len(systems)} body systems monitored by run_all_systems_scan",
        items=items,
        columns=['System'],
        code_location='core/tasks.py (body_systems)',
    )


def collect_llm_providers() -> InventorySection:
    src = (CORE_DIR / 'services' / 'llm_provider_registry.py').read_text()
    m = re.search(r'provider_classes\s*=\s*\{(.*?)\}', src, re.DOTALL)
    names = re.findall(r"'([^']+)'\s*:", m.group(1)) if m else []
    items = [{'provider': n} for n in names]
    return InventorySection(
        slug='llm-providers',
        title='LLM Providers',
        headline=f"{len(names)} providers registered in LLMProviderRegistry",
        items=items,
        columns=['Provider'],
        code_location='core/services/llm_provider_registry.py',
    )


def collect_signal_intelligence() -> InventorySection:
    from core.models_signal_intelligence import SignalCluster
    from core.services.signal_aggregation_service import SignalAggregationService
    pattern_choices = SignalCluster.PATTERN_TYPE_CHOICES
    items = [{'pattern_type': c[0], 'label': c[1]} for c in pattern_choices]
    return InventorySection(
        slug='signal-intelligence',
        title='Signal Intelligence',
        headline=(
            f"{len(pattern_choices)} SignalCluster pattern types, "
            f"MIN_CLUSTER_SIZE={SignalAggregationService.MIN_CLUSTER_SIZE}"
        ),
        items=items,
        columns=['Pattern Type', 'Label'],
        code_location='core/models_signal_intelligence.py + services/signal_aggregation_service.py',
    )


def collect_memory_types() -> InventorySection:
    from core.models_unified_system import AgentMemory
    choices = getattr(AgentMemory, 'MEMORY_TYPE_CHOICES', [])
    items = [{'memory_type': c[0], 'label': c[1]} for c in choices]
    return InventorySection(
        slug='memory-types',
        title='AgentMemory Types',
        headline=f"{len(choices)} memory types tracked by AgentMemory model",
        items=items,
        columns=['Type', 'Label'],
        code_location='core/models_unified_system.py (AgentMemory.MEMORY_TYPE_CHOICES)',
    )


def collect_content_pipeline() -> InventorySection:
    import inspect
    from core.services.claims_pack_builder import ClaimsPackBuilder
    from core.services.domain_content_context import (
        DomainContentContextBuilder,  # noqa: F401 (imported for completeness)
    )
    reviewers_src = (CORE_DIR / 'services' / 'content_review_panel_v2.py').read_text()
    reviewer_names = set(re.findall(r"['\"]([A-Z]\w+Reviewer)\b", reviewers_src))
    domain_src = (CORE_DIR / 'services' / 'domain_content_context.py').read_text()
    dm = re.search(r'domain_builders\s*=\s*\{(.*?)\}', domain_src, re.DOTALL)
    domains = re.findall(r"'([a-z_]+)'\s*:", dm.group(1)) if dm else []
    sig = inspect.signature(ClaimsPackBuilder.build)
    max_claims_default = sig.parameters['max_claims'].default

    items = [
        {'component': 'Reviewers (always)', 'value': 'SkepticReviewer, FactCheckReviewer'},
        {'component': 'Reviewers (conditional)', 'value': 'DomainPersonaReviewer (when domain confidence ≥ 0.2)'},
        {'component': 'All reviewer names found', 'value': ', '.join(sorted(reviewer_names))},
        {'component': 'Domain builders', 'value': ', '.join(domains)},
        {'component': 'ClaimsPackBuilder default max_claims', 'value': str(max_claims_default)},
    ]
    return InventorySection(
        slug='content-pipeline',
        title='Content Pipeline',
        headline=(
            f"{len(reviewer_names)} reviewer classes referenced, {len(domains)} content domains, "
            f"max_claims default={max_claims_default}"
        ),
        items=items,
        columns=['Component', 'Value'],
        code_location='core/services/content_review_panel_v2.py + domain_content_context.py + claims_pack_builder.py',
    )


def collect_initiative_pipeline() -> InventorySection:
    from core.models_document_registry import STAGE_TYPES, STAGES_WITH_AUTO_DISPATCH
    items = [
        {'stage': k, 'type': v, 'auto_dispatch': 'yes' if k in STAGES_WITH_AUTO_DISPATCH else 'no'}
        for k, v in STAGE_TYPES.items()
    ]
    return InventorySection(
        slug='initiative-pipeline',
        title='Initiative Pipeline',
        headline=f"{len(STAGE_TYPES)} pipeline stages (auto-dispatch on stages {sorted(STAGES_WITH_AUTO_DISPATCH)})",
        items=items,
        columns=['Stage #', 'Type', 'Auto-dispatch'],
        code_location='core/models_document_registry.py (STAGE_TYPES)',
    )


def collect_frontend() -> InventorySection:
    app_tsx = FRONTEND_DIR / 'App.tsx'
    routes = 0
    if app_tsx.exists():
        routes = len(re.findall(r'<Route\b', app_tsx.read_text()))

    types_file = FRONTEND_DIR / 'pages' / 'workspace' / 'types.ts'
    primary_tabs: list[str] = []
    if types_file.exists():
        src = types_file.read_text()
        m = re.search(r'export type WorkspaceTab\s*=', src)
        if m:
            cutoff = src.find('Sub-tab IDs', m.start())
            preamble = src[m.start():cutoff] if cutoff > 0 else src[m.start():m.start() + 400]
            primary_tabs = re.findall(r"\|\s*'([^']+)'", preamble)

    betting_tsx = FRONTEND_DIR / 'pages' / 'BettingPage.tsx'
    betting_tabs: list[str] = []
    if betting_tsx.exists():
        src = betting_tsx.read_text()
        m = re.search(r'const tabs\s*=\s*\[(.*?)\]\s*\n', src, re.DOTALL)
        if m:
            betting_tabs = re.findall(r"id:\s*'([^']+)'", m.group(1))

    items = [
        {'surface': 'App.tsx <Route>', 'count': routes},
        {'surface': 'Workspace primary tabs', 'count': len(primary_tabs)},
        {'surface': 'Betting dashboard tabs', 'count': len(betting_tabs)},
    ]
    notes = (
        f"Workspace tabs: {primary_tabs}. Betting tabs: {betting_tabs}."
    )
    return InventorySection(
        slug='frontend',
        title='Frontend (React + Vite)',
        headline=(
            f"{routes} routes in App.tsx, {len(primary_tabs)} workspace primary tabs, "
            f"{len(betting_tabs)} betting dashboard tabs"
        ),
        items=items,
        columns=['Surface', 'Count'],
        notes=notes,
        code_location='frontend/src/App.tsx, pages/workspace/types.ts, pages/BettingPage.tsx',
    )


def collect_infrastructure() -> InventorySection:
    procfile = REPO_ROOT / 'Procfile'
    workers: list[str] = []
    if procfile.exists():
        for line in procfile.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('release:') or ':' not in line:
                continue
            workers.append(line.split(':', 1)[0].strip())

    settings = (CORE_DIR / 'settings.py').read_text()
    redis_dbs = sorted(set(re.findall(r"redis(?:s)?://[^'\"]*?/(\d+)\b", settings)))

    items = [
        {'component': 'Procfile processes', 'value': ', '.join(workers) or '(none)'},
        {'component': 'Redis DB indices (settings.py)', 'value': ', '.join(redis_dbs) or '(none)'},
    ]
    return InventorySection(
        slug='infrastructure',
        title='Infrastructure',
        headline=f"{len(workers)} Procfile processes, {len(redis_dbs)} distinct Redis DB indices in settings",
        items=items,
        columns=['Component', 'Value'],
        code_location='Procfile + core/settings.py',
    )


def collect_code_stats() -> InventorySection:
    items: list[dict[str, Any]] = []
    total_py = 0
    total_lines = 0
    for root_name in ['core', 'ai_core', 'intelligence']:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        files = 0
        lines = 0
        for py in root.rglob('*.py'):
            if '__pycache__' in py.parts or '.venv' in py.parts:
                continue
            files += 1
            try:
                lines += sum(1 for _ in py.open(encoding='utf-8', errors='ignore'))
            except OSError:
                continue
        items.append({'tree': root_name, 'files': files, 'lines': lines})
        total_py += files
        total_lines += lines
    items.append({'tree': 'TOTAL (python)', 'files': total_py, 'lines': total_lines})
    return InventorySection(
        slug='code-stats',
        title='Code Statistics',
        headline=f"{total_py:,} Python files, {total_lines:,} lines across core/ + ai_core/ + intelligence/",
        items=items,
        columns=['Tree', 'Files', 'Lines'],
    )


def collect_verifier_state() -> InventorySection:
    """Embed a summary of the current doc-vs-reality verifier state."""
    from core.services.doc_claim_verification import run_all, summarize
    results = run_all()
    summary = summarize(results)
    by_sev = summary['by_severity']
    by_doc = summary['by_doc']

    # Top N drifting docs by drift count
    top_drift = sorted(
        ((doc, stats) for doc, stats in by_doc.items() if stats['drift'] > 0),
        key=lambda x: -x[1]['drift'],
    )[:15]

    items = [
        {'doc': doc, 'ok': stats['ok'], 'drift': stats['drift'], 'error': stats['error']}
        for doc, stats in sorted(by_doc.items())
    ]
    notes = (
        f"Severity rollup: ok={by_sev.get('ok', 0)}, low={by_sev.get('low', 0)}, "
        f"medium={by_sev.get('medium', 0)}, high={by_sev.get('high', 0)}, "
        f"error={by_sev.get('error', 0)}. "
        f"Top drifting docs: {', '.join(d for d, _ in top_drift[:5])}."
    )
    return InventorySection(
        slug='verifier-state',
        title='Doc-vs-Reality Verifier State',
        headline=(
            f"{summary['total']} registered claims across {len(by_doc)} docs: "
            f"{by_sev.get('ok', 0)} OK, "
            f"{by_sev.get('low', 0) + by_sev.get('medium', 0) + by_sev.get('high', 0)} drifts"
        ),
        items=items,
        columns=['Doc', 'OK', 'Drift', 'Error'],
        notes=notes,
        code_location='core/services/doc_claim_verification.py (run via `python manage.py verify_doc_claims`)',
    )


# Ordered list of collectors. Executive Summary is built from these after.
_COLLECTORS: list[Callable[[], InventorySection]] = [
    collect_agents,
    collect_spiders,
    collect_services,
    collect_celery_tasks,
    collect_beat_schedule,
    collect_pa_tools,
    collect_database_models,
    collect_url_routes,
    collect_views_files,
    collect_mgmt_commands,
    collect_discord,
    collect_body_systems,
    collect_llm_providers,
    collect_signal_intelligence,
    collect_memory_types,
    collect_content_pipeline,
    collect_initiative_pipeline,
    collect_frontend,
    collect_infrastructure,
    collect_code_stats,
    collect_verifier_state,
]


# =============================================================================
# Renderer
# =============================================================================


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ['git', '-C', str(REPO_ROOT), 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return '(unavailable)'


def gather_inventory() -> dict:
    """Run every collector and return a structured dict."""
    sections: list[InventorySection] = [_safe(c) for c in _COLLECTORS]
    return {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z').strip() or
                        datetime.now().isoformat(),
        'git_sha': _git_sha(),
        'sections': sections,
    }


def _format_value(v: Any) -> str:
    if v is None:
        return ''
    if isinstance(v, bool):
        return 'yes' if v else 'no'
    s = str(v)
    # Escape markdown table pipe character to keep rendering clean
    return s.replace('|', '\\|')


def _render_section(section: InventorySection) -> str:
    lines: list[str] = []
    lines.append(f"## {section.title}")
    lines.append('')
    lines.append(f"**Headline:** {section.headline}")
    if section.code_location:
        lines.append('')
        lines.append(f"**Code location:** `{section.code_location}`")
    if section.notes:
        lines.append('')
        lines.append(f"**Notes:** {section.notes}")
    if section.error:
        lines.append('')
        lines.append('```')
        lines.append(section.error)
        lines.append('```')

    if section.items and section.columns:
        lines.append('')
        lines.append('| ' + ' | '.join(section.columns) + ' |')
        lines.append('|' + '|'.join(['---'] * len(section.columns)) + '|')
        # Table rows — cap very long tables to 400 rows with a trailer
        MAX_ROWS = 400
        rows = section.items[:MAX_ROWS]
        for row in rows:
            if isinstance(row, dict):
                # Order by columns list
                keys = [_key_for_column(col) for col in section.columns]
                vals = [_format_value(row.get(k, '')) for k in keys]
            else:
                vals = [_format_value(row)]
            lines.append('| ' + ' | '.join(vals) + ' |')
        if len(section.items) > MAX_ROWS:
            lines.append(f"| ... | _({len(section.items) - MAX_ROWS} more rows truncated)_ |")
    lines.append('')
    return '\n'.join(lines)


def _key_for_column(col: str) -> str:
    """Derive the dict key corresponding to a display column name.

    Keeps the renderer resilient when rows use snake_case keys but display
    headers are Title Case.
    """
    return col.lower().replace(' ', '_').replace('-', '_').replace('#', 'num').replace('(', '').replace(')', '').strip('_')


# =============================================================================
# Inventory Blocks (Session 1100) — auto-injected stat snippets
# =============================================================================
#
# Pattern: docs include an HTML-comment marker pair:
#
#   <!-- @inventory-block:NAME -->
#   ...auto-managed content...
#   <!-- @inventory-block:end -->
#
# `refresh_doc_blocks(path, inventory)` rewrites everything between the two
# markers using the renderer registered under NAME. Closes the doc-drift loop:
# the verifier no longer needs to maintain a hardcoded `expected` for these
# stats — the doc and runtime stay synced by `refresh_doc_inventory_blocks`.


def _section_by_slug(inventory: dict, slug: str) -> Optional[InventorySection]:
    for s in inventory.get('sections', []):
        if s.slug == slug:
            return s
    return None


def render_block_platform_stats(inventory: dict) -> str:
    """Master stats table for CLAUDE.md and similar overview docs."""
    agents = _section_by_slug(inventory, 'agents')
    spiders = _section_by_slug(inventory, 'spiders')
    services = _section_by_slug(inventory, 'services')
    celery = _section_by_slug(inventory, 'celery-tasks')
    beat = _section_by_slug(inventory, 'beat-schedule')
    pa = _section_by_slug(inventory, 'pa-tools')
    models = _section_by_slug(inventory, 'database-models')
    discord = _section_by_slug(inventory, 'discord')
    body = _section_by_slug(inventory, 'body-systems')
    llms = _section_by_slug(inventory, 'llm-providers')
    signals = _section_by_slug(inventory, 'signal-intelligence')
    frontend = _section_by_slug(inventory, 'frontend')

    def headline(sec: Optional[InventorySection], default: str = 'n/a') -> str:
        return sec.headline if sec else default

    rows = [
        ('**Agents**', headline(agents)),
        ('**Spiders**', headline(spiders)),
        ('**Services**', headline(services)),
        ('**Celery Tasks**', headline(celery)),
        ('**Beat Schedule**', headline(beat)),
        ('**PA Tools**', headline(pa)),
        ('**Database Models**', headline(models)),
        ('**Discord**', headline(discord)),
        ('**Body Systems**', headline(body)),
        ('**LLM Providers**', headline(llms)),
        ('**Signal Pattern Types**', headline(signals)),
        ('**Frontend**', headline(frontend)),
    ]
    lines = ['| Component | Live Count |', '|---|---|']
    for label, value in rows:
        lines.append(f'| {label} | {value} |')
    lines.append('')
    lines.append("_Auto-generated by `refresh_doc_inventory_blocks` from `gather_inventory()`. Do not hand-edit between markers._")
    return '\n'.join(lines)


def render_block_backend_summary(inventory: dict) -> str:
    """Backend inventory summary table for BACKEND_INVENTORY.md."""
    routes = _section_by_slug(inventory, 'url-routes')
    views = _section_by_slug(inventory, 'views-files')
    mgmt = _section_by_slug(inventory, 'management-commands')
    services = _section_by_slug(inventory, 'services')
    celery = _section_by_slug(inventory, 'celery-tasks')
    models = _section_by_slug(inventory, 'database-models')
    discord = _section_by_slug(inventory, 'discord')

    def headline(sec: Optional[InventorySection]) -> str:
        return sec.headline if sec else 'n/a'

    lines = ['| Metric | Live Count |', '|--------|------------|']
    lines.append(f'| **Django Models** | {headline(models)} |')
    lines.append(f'| **URL Endpoints** | {headline(routes)} |')
    lines.append(f'| **Celery Tasks** | {headline(celery)} |')
    lines.append(f'| **Services** | {headline(services)} |')
    lines.append(f'| **Views Files** | {headline(views)} |')
    lines.append(f'| **Management Commands** | {headline(mgmt)} |')
    lines.append(f'| **Discord Commands** | {headline(discord)} |')
    lines.append('')
    lines.append("_Auto-generated by `refresh_doc_inventory_blocks` from `gather_inventory()`. Do not hand-edit between markers._")
    return '\n'.join(lines)


def render_block_agent_summary(inventory: dict) -> str:
    """Agent inventory headline for AGENTS.md / topics/agent-system.md."""
    agents = _section_by_slug(inventory, 'agents')
    if not agents:
        return '_inventory section unavailable_'
    return (
        f'**Headline:** {agents.headline}\n\n'
        + (f'**Notes:** {agents.notes}\n\n' if agents.notes else '')
        + "_Auto-generated by `refresh_doc_inventory_blocks`. Do not hand-edit between markers._"
    )


def render_block_pa_summary(inventory: dict) -> str:
    """PA tools headline for personal-assistant.md / AGENTS.md."""
    pa = _section_by_slug(inventory, 'pa-tools')
    if not pa:
        return '_inventory section unavailable_'
    return (
        f'**Headline:** {pa.headline}\n\n'
        + (f'**Notes:** {pa.notes}\n\n' if pa.notes else '')
        + "_Auto-generated by `refresh_doc_inventory_blocks`. Do not hand-edit between markers._"
    )


# Block name → renderer. Add here when introducing new auto-managed blocks.
INVENTORY_BLOCKS: dict[str, Callable[[dict], str]] = {
    'platform-stats': render_block_platform_stats,
    'backend-summary': render_block_backend_summary,
    'agent-summary': render_block_agent_summary,
    'pa-summary': render_block_pa_summary,
}


def refresh_doc_blocks(
    file_path: Path,
    inventory: dict,
    blocks: Optional[dict[str, Callable[[dict], str]]] = None,
) -> tuple[int, int, list[str]]:
    """Replace content between `<!-- @inventory-block:NAME -->` markers.

    Returns ``(updated_count, skipped_count, unknown_block_names)``.
    Skipped = marker present but block name not registered.
    """
    blocks = blocks if blocks is not None else INVENTORY_BLOCKS
    if not file_path.exists():
        return 0, 0, []
    src = file_path.read_text()
    pattern = re.compile(
        r'(<!-- @inventory-block:([a-z0-9_-]+) -->)(.*?)(<!-- @inventory-block:end -->)',
        re.DOTALL,
    )
    updated = 0
    skipped = 0
    unknown: list[str] = []

    def _replace(match: re.Match) -> str:
        nonlocal updated, skipped
        opener, name, _body, closer = match.group(1), match.group(2), match.group(3), match.group(4)
        renderer = blocks.get(name)
        if renderer is None:
            skipped += 1
            unknown.append(name)
            return match.group(0)
        try:
            new_body = renderer(inventory)
        except Exception as e:  # noqa: BLE001
            logger.warning("inventory block renderer '%s' failed: %s", name, e)
            skipped += 1
            return match.group(0)
        updated += 1
        return f"{opener}\n{new_body}\n{closer}"

    new_src = pattern.sub(_replace, src)
    if new_src != src:
        file_path.write_text(new_src)
    return updated, skipped, unknown


def render_markdown(inventory: dict) -> str:
    sections: list[InventorySection] = inventory['sections']

    lines: list[str] = []
    lines.append('# Platform Master Inventory')
    lines.append('')
    lines.append(f"**Generated:** {inventory['generated_at']}")
    lines.append(f"**Git HEAD:** `{inventory['git_sha']}`")
    lines.append('')
    lines.append(
        '> Runtime-derived snapshot of the Donkey Betz platform. '
        'Regenerate with `python manage.py generate_platform_inventory`.'
    )
    lines.append(
        '> Companion to `core/services/doc_claim_verification.py` — this doc captures '
        'the ground truth; the verifier flags where doc claims drift from it.'
    )
    lines.append('')

    # ── Executive Summary ──
    lines.append('## Executive Summary')
    lines.append('')
    lines.append('| Subsystem | Headline |')
    lines.append('|---|---|')
    for s in sections:
        headline = s.headline.replace('|', '\\|')
        lines.append(f"| [{s.title}](#{s.slug}) | {headline} |")
    lines.append('')

    # ── TOC ──
    lines.append('## Table of Contents')
    lines.append('')
    for s in sections:
        lines.append(f"- [{s.title}](#{s.slug})")
    lines.append('')

    # ── Per-section body ──
    for s in sections:
        lines.append(f"<a id=\"{s.slug}\"></a>")
        lines.append(_render_section(s))

    lines.append('---')
    lines.append('')
    lines.append(
        '*Generated by `core.services.platform_inventory`. '
        'When the docs elsewhere in the repo disagree with anything in this file, '
        'this file is authoritative.*'
    )
    lines.append('')
    return '\n'.join(lines)
