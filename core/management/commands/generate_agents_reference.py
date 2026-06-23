"""Generate ``docs/AGENTS_REFERENCE.md`` — schema-only per-agent reference.

Sibling to ``build_capability_audit`` (Session 1115) which groups by
status. This one groups by **category** (mirroring the AGENT_MAP comment
headings) and emits a denser per-agent schema card for each:

  - Class name + file path + line number
  - Status (enabled / rerouted / blocked)
  - Workspace-aware flag (writes files via SKIN Layer)
  - Phase B receipt_only adoption (URC v0.1 Session 1210+)
  - ``requires_system_context`` flag (CLAUDE.md + critical-docs injection)
  - Docstring first line
  - Tools list (function-call schemas): name + description per entry
  - Actionable config: declared actions + payload_fields (these are
    the documented ``result.data`` keys)

Run::

    python manage.py generate_agents_reference            # write to docs/
    python manage.py generate_agents_reference --check    # stdout only

If a new agent lands in AGENT_MAP that isn't in CATEGORY_MAP below, the
command exits non-zero with a list of unmapped names so the drift is
explicit. Built per Session 1211 close-state ask from Chris — "every
agent + params + expected outcome".
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_PATH = REPO_ROOT / 'docs' / 'AGENTS_REFERENCE.md'

# Same `_NON_SPECIALIST` set as platform_inventory.collect_agents() and
# build_capability_audit. Drift sentinel: if this diverges, fix here AND
# at the two other sites — they're all reading the same taxonomy.
_NON_SPECIALIST = frozenset({
    'WorkflowAgent', 'VideoAgent', 'CodeGeneratorAgent', 'DevOpsAgent',
    'FullStackDeveloperAgent', 'CodeReviewAgent',
    'COOAgent', 'CTOAgent', 'AudioAgent',
})

# Source for WORKSPACE_AWARE_AGENTS list at runtime — the constant lives
# inside a function body at core/epa_handlers_tools.py so we parse it
# rather than import it.
_WORKSPACE_AWARE_SOURCE = REPO_ROOT / 'core' / 'epa_handlers_tools.py'

# Category groupings mirror the comment headings in
# core/agent_router.py:318 AGENT_MAP. If you add a new agent there, add
# it here too (or the generator will error). Order matches AGENT_MAP for
# readability — readers can cross-reference with the source.
CATEGORY_MAP: list[tuple[str, list[str]]] = [
    ('Creation', [
        'ImageAgent', 'VideoAgent', 'AudioAgent',
        'TalkingCharacterAgent', 'ThreeDAgent',
    ]),
    ('Editing', [
        'ImageEditingAgent', 'VideoEditingAgent',
    ]),
    ('Research', [
        'ResearchAgent',
    ]),
    ('Audit', [
        'PlatformAuditAgent',
    ]),
    ('Writing', [
        'ContentWriterAgent',
    ]),
    ('Content Enhancement', [
        'EditorAgent',
    ]),
    ('Strategy', [
        'ContentStrategyAgent', 'BrandIdentityAgent',
        'SEOOptimizerAgent', 'SocialMediaAgent',
    ]),
    ('Executive', [
        'CTOAgent', 'COOAgent',
        'CreativeDirectorAgent', 'MeetingCoordinatorAgent',
    ]),
    ('Analysis', [
        'TrendAnalysisAgent', 'OpportunityScoringAgent',
    ]),
    ('Training', [
        'CharacterTrainingAgent', 'TrainedCreationAgent',
    ]),
    ('Security', [
        'MemoryIsolationAgent', 'ContentAuditAgent',
    ]),
    ('Prompt Engineering', [
        'PromptEngineeringAgent',
    ]),
    ('Business Research', [
        'CompetitorAnalysisAgent', 'CustomerResearchAgent',
        'BrandStrategyAgent', 'MarketingStrategyAgent',
        'MarketIntelligenceAgent',
    ]),
    ('Legal', [
        'LegalDocDrafterAgent',
    ]),
    ('Development', [
        'CodeGeneratorAgent', 'FullStackDeveloperAgent',
        'CodeReviewAgent', 'DevOpsAgent',
    ]),
    ('Stock Audit', [
        'StockAuditCoordinator', 'StockAnalystAgent',
        'MarketMovementMonitorAgent', 'InstitutionalWatcherAgent',
        'MarketAnomalyDetectorAgent', 'BullCaseAgent', 'BearCaseAgent',
        'SignalScannerAgent', 'MarketIntelligenceCoordinator',
    ]),
    ('Blockchain Audit', [
        'BlockchainAuditCoordinator', 'SmartContractAuditorAgent',
        'TransactionMonitorAgent', 'WhaleWatcherAgent',
        'ExploitDetectorAgent',
    ]),
    ('Narrative Drift', [
        'NarrativeDriftCoordinator', 'NarrativeHistorianAgent',
        'TrendBreakDetectorAgent', 'CulturalImpactAgent',
    ]),
    ('Series Workflow', [
        'AISeriesWorkflowAgent',
    ]),
    ('Autonomous Content Studio', [
        'AutonomousContentStudioCoordinator', 'TopicMinerAgent',
        'ContrarianAgent', 'PerformanceAnalystAgent',
        'DistributionAgent', 'VoiceCriticAgent',
        'ContentDiversityOrchestrator',
    ]),
    ('Rendering', [
        'ResolveAgent',
    ]),
    ('Podcast Studio', [
        'PodcastCoordinatorAgent', 'DebateAdvocateAgent',
        'DebateSkepticAgent', 'ModeratorAgent',
    ]),
    ('Orchestration', [
        'WorkflowAgent',
    ]),
    ('Campaign Orchestrator', [
        'CampaignOrchestratorAgent',
    ]),
    ('Markets', [
        'PredictionMarketAnalyst', 'SportsOddsAnalyst',
        'ArbitrageDetector', 'GamePredictor', 'LineMovementAnalyzer',
        'SharpActionDetector', 'BookmakerAgent',
    ]),
    ('Orchestration & Utility', [
        'OpportunityPipelineAgent', 'ContentExecutorAgent',
        'WorkflowOrchestrationAgent', 'ThinkingAgent',
        'TechnicalDocumentAgent',
    ]),
    ('System Intelligence', [
        'SystemIntelligenceAgent',
    ]),
    ('Decision Enforcement', [
        'DecisionEnforcerAgent',
    ]),
]


def _slug(s: str) -> str:
    """Lowercase + alphanumerics + dashes — for markdown anchors."""
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def _first_line(text: str) -> str:
    if not text:
        return ''
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return ''


def _load_workspace_aware() -> set[str]:
    """Parse WORKSPACE_AWARE_AGENTS list from core/epa_handlers_tools.py.

    The constant lives inside a function so we can't ``from ... import``
    it. Stable-enough regex extraction works because the list is plain
    ``'Name',`` lines and has a closing ``]``.
    """
    try:
        src = _WORKSPACE_AWARE_SOURCE.read_text()
    except OSError:
        return set()
    m = re.search(
        r'WORKSPACE_AWARE_AGENTS\s*=\s*\[(.*?)\]',
        src, re.DOTALL,
    )
    if not m:
        return set()
    body = m.group(1)
    return set(re.findall(r"'([A-Za-z0-9_]+)'", body))


def _tool_entry(entry: Any) -> dict[str, str] | None:
    """Normalize a tool schema entry to ``{name, description}``.

    Handles both the OpenAI function-call shape
    ``{"type": "function", "function": {"name": ..., "description": ...}}``
    and the bare ``{"name": ..., "description": ...}`` fallback.
    """
    if not isinstance(entry, dict):
        return None
    fn = entry.get('function') if entry.get('type') == 'function' else entry
    if not isinstance(fn, dict):
        return None
    name = fn.get('name')
    if not isinstance(name, str) or not name:
        return None
    desc = fn.get('description') or ''
    return {'name': name, 'description': desc.strip()}


def _has_receipt_only(cls: type) -> bool:
    """True iff the class declares its own _is_receipt_only_mode helper.

    We check ``__dict__`` to avoid inherited methods from BaseAgent (the
    helper is currently agent-defined; if BaseAgent later gains a
    default impl, this stays correct — we want adopters to override it
    explicitly until the contract stabilizes).
    """
    return '_is_receipt_only_mode' in cls.__dict__


class Command(BaseCommand):
    help = 'Regenerate docs/AGENTS_REFERENCE.md (schema per agent, grouped by category).'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--check',
            action='store_true',
            help='Print the would-be file to stdout instead of writing.',
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        from core.agent_router import AgentRouter

        try:
            from core.models_unified_system import AgentControlEntry
            blocked = set(AgentControlEntry.get_blocked_names())
        except Exception as e:  # noqa: BLE001 — DB unavailable
            self.stderr.write(self.style.WARNING(
                f"AgentControlEntry unreachable ({type(e).__name__}); "
                f"falling back to hardcoded blocked={{'CodeGeneratorAgent'}}"
            ))
            blocked = {'CodeGeneratorAgent'}

        workspace_aware = _load_workspace_aware()
        agent_map = AgentRouter.AGENT_MAP

        # Drift check: every AGENT_MAP key must appear in CATEGORY_MAP.
        # If a new agent lands and isn't categorized, fail loud rather
        # than silently dropping it from the doc.
        mapped = {name for _, names in CATEGORY_MAP for name in names}
        unmapped = sorted(set(agent_map.keys()) - mapped)
        stale = sorted(mapped - set(agent_map.keys()))
        if unmapped:
            raise CommandError(
                f"AGENT_MAP contains {len(unmapped)} agent(s) not in "
                f"CATEGORY_MAP: {unmapped}. Add them to CATEGORY_MAP in "
                f"core/management/commands/generate_agents_reference.py."
            )
        if stale:
            raise CommandError(
                f"CATEGORY_MAP lists {len(stale)} agent(s) not in "
                f"AGENT_MAP (stale references): {stale}. Remove from "
                f"CATEGORY_MAP."
            )

        # Inspect each agent.
        rows_by_cat: list[tuple[str, list[dict]]] = []
        all_rows: list[dict] = []
        for cat_name, agent_names in CATEGORY_MAP:
            cat_rows: list[dict] = []
            for name in agent_names:
                cls = agent_map[name]
                row = self._inspect(
                    name, cls, cat_name, blocked, workspace_aware,
                )
                cat_rows.append(row)
                all_rows.append(row)
            rows_by_cat.append((cat_name, cat_rows))

        rendered = self._render(rows_by_cat, all_rows, total=len(agent_map))

        if opts['check']:
            self.stdout.write(rendered)
            return

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(rendered)
        n_enabled = sum(1 for r in all_rows if r['status'] == 'enabled')
        n_rerouted = sum(1 for r in all_rows if r['status'] == 'rerouted')
        n_blocked = sum(1 for r in all_rows if r['status'] == 'blocked')
        n_phase_b = sum(1 for r in all_rows if r['phase_b'])
        n_workspace = sum(1 for r in all_rows if r['workspace_aware'])
        self.stdout.write(self.style.SUCCESS(
            f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} — "
            f"{len(all_rows)} agents "
            f"({n_enabled} enabled, {n_rerouted} rerouted, {n_blocked} blocked), "
            f"{n_phase_b} with Phase B receipt_only, "
            f"{n_workspace} workspace-aware."
        ))

    # ------------------------------------------------------------------ inspect

    def _inspect(
        self,
        name: str,
        cls: type,
        category: str,
        blocked: set[str],
        workspace_aware: set[str],
    ) -> dict:
        if name in blocked:
            status = 'blocked'
        elif name in _NON_SPECIALIST:
            status = 'rerouted'
        else:
            status = 'enabled'

        try:
            file_path = Path(inspect.getfile(cls)).resolve()
            try:
                rel_path = file_path.relative_to(REPO_ROOT)
            except ValueError:
                rel_path = file_path
            _, line_no = inspect.getsourcelines(cls)
        except (OSError, TypeError):
            rel_path = None
            line_no = 0

        doc = inspect.getdoc(cls) or ''
        first_line = _first_line(doc)

        declared_name = getattr(cls, 'name', None)

        tools = getattr(cls, 'tools', None)
        tool_entries: list[dict[str, str]] = []
        if isinstance(tools, (list, tuple)):
            for entry in tools:
                normalized = _tool_entry(entry)
                if normalized is not None:
                    tool_entries.append(normalized)

        actionable = getattr(cls, 'actionable_config', None)
        actions: list[str] = []
        payload_fields: list[str] = []
        if actionable is not None:
            raw_actions = getattr(actionable, 'actions', None)
            if isinstance(raw_actions, (list, tuple)):
                actions = [str(a) for a in raw_actions]
            raw_payload = getattr(actionable, 'payload_fields', None)
            if isinstance(raw_payload, (list, tuple)):
                payload_fields = [str(p) for p in raw_payload]

        requires_sysctx = bool(getattr(cls, 'requires_system_context', False))
        phase_b = _has_receipt_only(cls)

        return {
            'name': name,
            'class_name': cls.__name__,
            'declared_name': declared_name,
            'category': category,
            'status': status,
            'file': str(rel_path) if rel_path else '(unknown)',
            'line': line_no,
            'docstring_first_line': first_line,
            'tool_entries': tool_entries,
            'actions': actions,
            'payload_fields': payload_fields,
            'requires_system_context': requires_sysctx,
            'workspace_aware': name in workspace_aware,
            'phase_b': phase_b,
        }

    # ----------------------------------------------------------------- render

    def _render(
        self,
        rows_by_cat: list[tuple[str, list[dict]]],
        all_rows: list[dict],
        *,
        total: int,
    ) -> str:
        n_enabled = sum(1 for r in all_rows if r['status'] == 'enabled')
        n_rerouted = sum(1 for r in all_rows if r['status'] == 'rerouted')
        n_blocked = sum(1 for r in all_rows if r['status'] == 'blocked')
        n_phase_b = sum(1 for r in all_rows if r['phase_b'])
        n_workspace = sum(1 for r in all_rows if r['workspace_aware'])
        n_with_tools = sum(1 for r in all_rows if r['tool_entries'])
        n_with_actionable = sum(
            1 for r in all_rows if r['actions'] or r['payload_fields']
        )

        out: list[str] = []
        out.append(
            '<!-- DOC-AUTOGEN: regenerated by '
            '`python manage.py generate_agents_reference`. Do not hand-edit. -->'
        )
        out.append('')
        out.append('# Agents Reference — Schema by Category')
        out.append('')
        out.append(
            '**Source of truth:** `core/agent_router.AgentRouter.AGENT_MAP`. '
            'Class docstrings, `tools` schemas, and `actionable_config` '
            'introspected live. Status pulled from `AgentControlEntry` '
            '(blocked) + hardcoded `_NON_SPECIALIST` set (rerouted).'
        )
        out.append('')
        out.append(
            '> **Companion docs:** [`CAPABILITY_AUDIT.md`](CAPABILITY_AUDIT.md) '
            'groups the same agents by status; this doc groups by category '
            'and exposes the per-agent schema (tools, actions, payload '
            'fields, Phase B status, workspace-aware flag).'
        )
        out.append('')

        # ── Headline ────────────────────────────────────────────────
        out.append('## Headline')
        out.append('')
        out.append(f'- **Total agents:** {total}')
        out.append(
            f'- **Status:** {n_enabled} enabled · {n_rerouted} rerouted · '
            f'{n_blocked} blocked'
        )
        out.append(
            f'- **Phase B receipt_only adopters (URC v0.1):** {n_phase_b}'
        )
        out.append(
            f'- **Workspace-aware (writes via SKIN Layer):** {n_workspace}'
        )
        out.append(f'- **With explicit `tools` schema:** {n_with_tools}')
        out.append(
            f'- **With `actionable_config` (declared actions + payload '
            f'fields):** {n_with_actionable}'
        )
        out.append('')

        # ── Legend ──────────────────────────────────────────────────
        out.append('## Legend')
        out.append('')
        out.append(
            '- **Status**: `enabled` (live), `rerouted` (in AGENT_MAP but '
            'dispatch routes elsewhere via `_NON_SPECIALIST` set), `blocked` '
            '(AgentControlEntry status=blocked).'
        )
        out.append(
            '- **Phase B**: ✓ if the agent declares `_is_receipt_only_mode` '
            '— means `context={"mode":"receipt_only"}` short-circuits to a '
            'URC v0.1 skipped receipt with no LLM/IO.'
        )
        out.append(
            '- **Workspace-aware**: ✓ if listed in `WORKSPACE_AWARE_AGENTS` '
            '(core/epa_handlers_tools.py). Agent can write files via SKIN '
            'Layer when `write_to_workspace=True`.'
        )
        out.append(
            '- **System ctx**: ✓ if `requires_system_context = True` — gets '
            'CLAUDE.md + critical-docs injected on every call.'
        )
        out.append(
            '- **Params**: every agent\'s `execute()` takes the same 4 '
            'positional args: `task: str`, `context: Dict[str, Any]`, '
            '`scifi_context: Dict[str, Any]`, `spider_context: Dict[str, '
            'Any]`. Per-agent schemas below describe what each agent reads '
            'from those dicts via tools + actionable_config.'
        )
        out.append(
            '- **Expected outcome**: `AgentResult` (defined in '
            '`core/agents/base_agent.py`) with `success: bool`, `message: '
            'str`, `data: Dict[str, Any]`, `error: Optional[str]`, '
            '`tool_calls: List[Dict]`. The `actionable_config.payload_fields` '
            'column lists the documented keys in `data`.'
        )
        out.append('')

        # ── Table of Contents ───────────────────────────────────────
        out.append('## Table of Contents')
        out.append('')
        for cat_name, _rows in rows_by_cat:
            out.append(f'- [{cat_name}](#{_slug(cat_name)})')
        out.append('')

        # ── Overview table ──────────────────────────────────────────
        out.append('## Overview')
        out.append('')
        out.append('| Agent | Category | Status | Phase B | Workspace | Sys-ctx | Tools | Actions |')
        out.append('|---|---|---|---|---|---|---|---|')
        for r in all_rows:
            status_label = {
                'enabled': '✓ enabled',
                'rerouted': '↻ rerouted',
                'blocked': '✗ blocked',
            }[r['status']]
            phase_b = '✓' if r['phase_b'] else ''
            workspace = '✓' if r['workspace_aware'] else ''
            sysctx = '✓' if r['requires_system_context'] else ''
            n_tools = len(r['tool_entries']) or ''
            n_actions = len(r['actions']) or ''
            out.append(
                f"| `{r['name']}` | {r['category']} | {status_label} | "
                f"{phase_b} | {workspace} | {sysctx} | {n_tools} | "
                f"{n_actions} |"
            )
        out.append('')

        # ── Per-category sections ───────────────────────────────────
        for cat_name, rows in rows_by_cat:
            out.append(f'## {cat_name}')
            out.append('')
            for r in rows:
                out.extend(self._render_agent_card(r))
                out.append('')

        out.append('---')
        out.append('')
        out.append(
            '*Regenerate via `python manage.py generate_agents_reference`. '
            'Drift caught at generation time — new AGENT_MAP entries that '
            'aren\'t in CATEGORY_MAP cause the command to fail loud.*'
        )
        out.append('')
        return '\n'.join(out)

    def _render_agent_card(self, r: dict) -> list[str]:
        """Render one agent's schema card."""
        out: list[str] = []
        out.append(f"### `{r['name']}`")
        out.append('')

        # Status line
        status_label = {
            'enabled': '✓ enabled',
            'rerouted': '↻ rerouted',
            'blocked': '✗ blocked',
        }[r['status']]
        flags = []
        if r['phase_b']:
            flags.append('Phase B receipt_only')
        if r['workspace_aware']:
            flags.append('workspace-aware')
        if r['requires_system_context']:
            flags.append('requires system context')
        flag_str = (' · ' + ' · '.join(flags)) if flags else ''
        out.append(f"**Status:** {status_label}{flag_str}")
        out.append('')

        # File + class
        if r['line']:
            out.append(f"**Source:** `{r['file']}:{r['line']}` (class `{r['class_name']}`)")
        else:
            out.append(f"**Source:** `{r['file']}` (class `{r['class_name']}`)")
        if r['declared_name'] and r['declared_name'] != r['name']:
            out.append(
                f"**Declared name mismatch:** class attribute `name = "
                f"'{r['declared_name']}'` ≠ AGENT_MAP key `{r['name']}`"
            )
        out.append('')

        # One-liner
        if r['docstring_first_line']:
            out.append(f"**Purpose:** {r['docstring_first_line']}")
        else:
            out.append('**Purpose:** *(no class docstring)*')
        out.append('')

        # Tools
        if r['tool_entries']:
            out.append(f"**Tools ({len(r['tool_entries'])}):**")
            out.append('')
            for t in r['tool_entries']:
                desc = t['description'] or '*(no description)*'
                # Single-line description; collapse internal whitespace.
                desc = re.sub(r'\s+', ' ', desc).strip()
                out.append(f"- `{t['name']}` — {desc}")
            out.append('')
        else:
            out.append(
                '**Tools:** *(none declared — delegates to BaseAgent '
                'fallback or direct LLM call)*'
            )
            out.append('')

        # Actionable config
        if r['actions'] or r['payload_fields']:
            out.append('**Actionable output:**')
            if r['actions']:
                acts = ', '.join(f"`{a}`" for a in r['actions'])
                out.append(f"- **Actions:** {acts}")
            if r['payload_fields']:
                fields = ', '.join(f"`{p}`" for p in r['payload_fields'])
                out.append(f"- **Payload fields (`result.data` keys):** {fields}")
            out.append('')
        else:
            out.append(
                '**Actionable output:** *(no `actionable_config` declared '
                '— `result.data` shape is agent-specific; see source)*'
            )
            out.append('')

        return out
