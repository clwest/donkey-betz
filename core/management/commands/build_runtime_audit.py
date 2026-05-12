"""Generate ``docs/RUNTIME_AUDIT.md`` — telemetry-driven "what's actually executing".

Built in Session 1115, eleventh and final audit. Every prior audit asks
"what does the code say should happen." This one asks "what actually
runs?" It cross-references three registries against three telemetry
tables:

| Registry | Telemetry table | "Used" predicate |
|---|---|---|
| `AgentRouter.AGENT_MAP` + DB `Agent` rows | `AgentExecution` | `task` field references the agent name |
| `core.celery.app.tasks` | `CeleryTaskEvent` | `task_name` exact match |
| `PA_TOOL_SCHEMAS` | `ToolCallRecord` | `tool_name` exact match |

For each, the audit reports:
- Registered N
- Executed in last 30 days
- Executed ever
- **Never executed** — declared in code but no row in telemetry

The "never executed" set is the clearest read on dead-or-unused
capability. Combined with the Celery audit's orphan list, this
answers Chris's "is there anything we haven't connected yet" question
from two complementary angles (static caller-graph + runtime
telemetry).

**Requires a database with telemetry rows to be informative.** On a
fresh local DB the counts will all be 0; the framework is what matters.
Re-run against production for the real picture.

Run::

    python manage.py build_runtime_audit
"""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand
from django.utils import timezone


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_PATH = REPO_ROOT / 'docs' / 'RUNTIME_AUDIT.md'
RECENT_WINDOW_DAYS = 30


class Command(BaseCommand):
    help = "Regenerate docs/RUNTIME_AUDIT.md from telemetry tables vs code registries."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--check', action='store_true',
            help='Print the would-be file to stdout instead of writing.',
        )
        parser.add_argument(
            '--window-days', type=int, default=RECENT_WINDOW_DAYS,
            help=f'Recent-execution window in days (default {RECENT_WINDOW_DAYS}).',
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        window = max(1, int(opts.get('window_days') or RECENT_WINDOW_DAYS))
        cutoff = timezone.now() - timedelta(days=window)

        agents = self._inspect_agents(cutoff)
        tasks = self._inspect_tasks(cutoff)
        tools = self._inspect_tools(cutoff)

        rendered = self._render(agents, tasks, tools, window=window)

        if opts['check']:
            self.stdout.write(rendered)
            return

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(rendered)
        self.stdout.write(self.style.SUCCESS(
            f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} "
            f"(window={window}d · agents {agents['executed_ever']}/{agents['total']} "
            f"ever · tasks {tasks['executed_ever']}/{tasks['total']} ever · "
            f"tools {tools['executed_ever']}/{tools['total']} ever)"
        ))

    # ------------------------------------------------------------- agents

    def _inspect_agents(self, cutoff) -> dict:
        from core.agent_router import AgentRouter
        from core.models_unified_system import Agent
        from core.models import AgentExecution

        agent_map_names = set(AgentRouter.AGENT_MAP.keys())
        # DB Agent rows by name. The execution table uses `agent` FK + `task`
        # text. Build a name set from both registries.
        db_agent_names = set(Agent.objects.values_list('name', flat=True))
        registered = agent_map_names | db_agent_names

        # Distinct agent names that have AT LEAST ONE AgentExecution row.
        # AgentExecution.agent is FK to Agent; the agent's `name` shows the
        # canonical agent identifier. We can also fall back to the `task`
        # text column for older rows.
        executed_ever_q = AgentExecution.objects.values_list(
            'agent__name', flat=True
        ).distinct()
        executed_recent_q = AgentExecution.objects.filter(
            created_at__gte=cutoff
        ).values_list('agent__name', flat=True).distinct()
        executed_ever = {n for n in executed_ever_q if n}
        executed_recent = {n for n in executed_recent_q if n}

        never_executed = sorted(registered - executed_ever)
        # Subset summaries by source registry
        agent_map_never = sorted(agent_map_names - executed_ever)
        db_only_never = sorted(db_agent_names - agent_map_names - executed_ever)

        return {
            'total': len(registered),
            'agent_map_total': len(agent_map_names),
            'db_total': len(db_agent_names),
            'overlap': len(agent_map_names & db_agent_names),
            'executed_ever': len(registered & executed_ever),
            'executed_recent': len(registered & executed_recent),
            'never_executed': never_executed,
            'agent_map_never': agent_map_never,
            'db_only_never': db_only_never,
            'telemetry_rows': AgentExecution.objects.count(),
        }

    # -------------------------------------------------------------- tasks

    def _inspect_tasks(self, cutoff) -> dict:
        from core.celery import app as celery_app
        from core.models_celery_telemetry import CeleryTaskEvent

        registered = {
            t for t in celery_app.tasks.keys() if not t.startswith('celery.')
        }
        executed_ever_q = CeleryTaskEvent.objects.values_list(
            'task_name', flat=True
        ).distinct()
        executed_recent_q = CeleryTaskEvent.objects.filter(
            started_at__gte=cutoff
        ).values_list('task_name', flat=True).distinct()
        executed_ever = set(executed_ever_q)
        executed_recent = set(executed_recent_q)

        never_executed = sorted(registered - executed_ever)
        # Telemetry rows pointing at tasks NOT in registry (drifted task name).
        telemetry_unknown = sorted(executed_ever - registered)

        return {
            'total': len(registered),
            'executed_ever': len(registered & executed_ever),
            'executed_recent': len(registered & executed_recent),
            'never_executed': never_executed,
            'telemetry_unknown_tasks': telemetry_unknown,
            'telemetry_rows': CeleryTaskEvent.objects.count(),
        }

    # -------------------------------------------------------------- tools

    def _inspect_tools(self, cutoff) -> dict:
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        from core.models import ToolCallRecord

        registered = {
            (s.get('name') or '') for s in PA_TOOL_SCHEMAS if s.get('name')
        }
        executed_ever = set(
            ToolCallRecord.objects.values_list('tool_name', flat=True).distinct()
        )
        executed_recent = set(
            ToolCallRecord.objects.filter(
                created_at__gte=cutoff
            ).values_list('tool_name', flat=True).distinct()
        )

        never_executed = sorted(registered - executed_ever)
        telemetry_unknown = sorted(executed_ever - registered)

        # Success metrics for the things that DID run
        success_metrics: dict[str, dict] = {}
        for tool in sorted(registered & executed_ever):
            qs = ToolCallRecord.objects.filter(tool_name=tool)
            total = qs.count()
            success = qs.filter(success=True).count()
            success_metrics[tool] = {
                'calls': total,
                'success_rate': round(100.0 * success / total, 1) if total else 0,
            }

        return {
            'total': len(registered),
            'executed_ever': len(registered & executed_ever),
            'executed_recent': len(registered & executed_recent),
            'never_executed': never_executed,
            'telemetry_unknown_tools': telemetry_unknown,
            'success_metrics': success_metrics,
            'telemetry_rows': ToolCallRecord.objects.count(),
        }

    # ------------------------------------------------------------ render

    def _render(
        self,
        agents: dict,
        tasks: dict,
        tools: dict,
        *,
        window: int,
    ) -> str:
        out: list[str] = []
        out.append(
            '<!-- DOC-AUTOGEN: regenerated by '
            '`python manage.py build_runtime_audit`. Do not hand-edit. -->'
        )
        out.append('')
        out.append('# Capability Audit — Runtime Telemetry')
        out.append('')
        out.append(
            "**Source of truth:** three telemetry tables in the live "
            "database, cross-referenced against the code-side registries "
            "captured by the other audits:"
        )
        out.append('')
        out.append(
            "- `AgentExecution` (core.models) vs "
            "`AGENT_MAP` + DB `Agent` rows."
        )
        out.append(
            "- `CeleryTaskEvent` (core.models_celery_telemetry) vs "
            "`core.celery.app.tasks`."
        )
        out.append(
            "- `ToolCallRecord` (core.models) vs `PA_TOOL_SCHEMAS`."
        )
        out.append('')
        out.append(
            f"**Recent-execution window:** last {window} days. "
            f"Override with `--window-days N`."
        )
        out.append('')

        out.append(
            "> This audit is only as informative as the DB it runs against. "
            "Fresh local DBs show ~all-zero (nothing has executed yet). Run "
            "against a production-mirror to see what's actually live vs "
            "dead. The **never-executed** set is the answer to "
            "'declared but not connected'."
        )
        out.append('')

        # Database telemetry context
        total_rows = (
            agents['telemetry_rows']
            + tasks['telemetry_rows']
            + tools['telemetry_rows']
        )
        out.append(f'**Telemetry row counts:** '
                   f'AgentExecution={agents["telemetry_rows"]}, '
                   f'CeleryTaskEvent={tasks["telemetry_rows"]}, '
                   f'ToolCallRecord={tools["telemetry_rows"]} '
                   f'(total {total_rows}).')
        if total_rows == 0:
            out.append('')
            out.append(
                '> ⚠ All three telemetry tables are empty. This audit is '
                'showing the framework, not real activity. The numbers '
                'below are guaranteed to read "0 of N executed ever" until '
                'agents / tasks / tools actually start logging telemetry. '
                'For meaningful output, re-run against a DB with real '
                'execution history.'
            )
        out.append('')

        out.append('## Headline')
        out.append('')
        out.append(
            f'| Registry | Registered | Executed ever | Executed (≤{window}d) | Never executed |'
        )
        out.append('|---|---:|---:|---:|---:|')
        out.append(
            f'| **Agents** (`AGENT_MAP` ∪ DB) | {agents["total"]} | '
            f'{agents["executed_ever"]} | {agents["executed_recent"]} | '
            f'{len(agents["never_executed"])} |'
        )
        out.append(
            f'| **Celery tasks** | {tasks["total"]} | '
            f'{tasks["executed_ever"]} | {tasks["executed_recent"]} | '
            f'{len(tasks["never_executed"])} |'
        )
        out.append(
            f'| **PA tools** | {tools["total"]} | '
            f'{tools["executed_ever"]} | {tools["executed_recent"]} | '
            f'{len(tools["never_executed"])} |'
        )
        out.append('')

        # Agents
        out.append('## Agents')
        out.append('')
        out.append(
            f'- AGENT_MAP entries: {agents["agent_map_total"]}'
        )
        out.append(
            f'- DB Agent rows: {agents["db_total"]}'
        )
        out.append(
            f'- Overlap (same name in both): {agents["overlap"]}'
        )
        out.append(
            f'- Executed at least once in the last {window} days: '
            f'{agents["executed_recent"]} / {agents["total"]}'
        )
        out.append(
            f'- Executed at any time on record: '
            f'{agents["executed_ever"]} / {agents["total"]}'
        )
        out.append(
            f'- **Never executed** (any time): '
            f'{len(agents["never_executed"])}'
        )
        out.append('')
        if agents["agent_map_never"]:
            out.append('### AGENT_MAP entries with zero AgentExecution rows')
            out.append('')
            out.append(
                'These are routable in code but have never produced an '
                'execution record. Subset of "never executed" — flagged '
                'separately because routable agents are the most likely '
                'to surface real usage.'
            )
            out.append('')
            for name in agents["agent_map_never"][:50]:
                out.append(f'- `{name}`')
            if len(agents["agent_map_never"]) > 50:
                out.append(f'- … (+{len(agents["agent_map_never"]) - 50} more)')
            out.append('')

        # Tasks
        out.append('## Celery tasks')
        out.append('')
        out.append(
            f'- Registered tasks: {tasks["total"]}'
        )
        out.append(
            f'- Executed at least once in the last {window} days: '
            f'{tasks["executed_recent"]} / {tasks["total"]}'
        )
        out.append(
            f'- Executed at any time on record: '
            f'{tasks["executed_ever"]} / {tasks["total"]}'
        )
        out.append(
            f'- **Never executed**: {len(tasks["never_executed"])}'
        )
        out.append('')
        if tasks['telemetry_unknown_tasks']:
            out.append('### CeleryTaskEvent rows pointing at unknown tasks')
            out.append('')
            out.append(
                'Telemetry references task names that AREN\'T in the '
                'current Celery registry. Either the task got renamed / '
                'removed, or the telemetry was written by a different '
                'app version. Forensic interest only.'
            )
            out.append('')
            for name in tasks['telemetry_unknown_tasks'][:30]:
                out.append(f'- `{name}`')
            out.append('')

        if tasks['never_executed']:
            out.append('### Tasks with zero CeleryTaskEvent rows')
            out.append('')
            out.append(
                f'**{len(tasks["never_executed"])} of {tasks["total"]}** '
                f'tasks have never been recorded as executing. Cross-'
                f'reference with `docs/CELERY_AUDIT.md` orphans list — '
                f'tasks that are both **orphan** (no caller) AND **never '
                f'executed** are the highest-confidence dead code.'
            )
            out.append('')
            # Limit display
            for name in tasks['never_executed'][:50]:
                out.append(f'- `{name}`')
            if len(tasks['never_executed']) > 50:
                out.append(
                    f'- … (+{len(tasks["never_executed"]) - 50} more — '
                    f'see full list with `python manage.py build_runtime_audit '
                    f'--check` and grep)'
                )
            out.append('')

        # Tools
        out.append('## PA tools (Rigby)')
        out.append('')
        out.append(
            f'- Registered schemas: {tools["total"]}'
        )
        out.append(
            f'- Invoked at least once in the last {window} days: '
            f'{tools["executed_recent"]} / {tools["total"]}'
        )
        out.append(
            f'- Invoked at any time on record: '
            f'{tools["executed_ever"]} / {tools["total"]}'
        )
        out.append(
            f'- **Never invoked**: {len(tools["never_executed"])}'
        )
        out.append('')
        if tools['success_metrics']:
            out.append('### Tool success rates (executed tools)')
            out.append('')
            out.append('| Tool | Calls | Success rate |')
            out.append('|---|---:|---:|')
            for tool, m in sorted(
                tools['success_metrics'].items(),
                key=lambda kv: -kv[1]['calls']
            )[:30]:
                out.append(
                    f'| `{tool}` | {m["calls"]} | {m["success_rate"]}% |'
                )
            out.append('')

        if tools['telemetry_unknown_tools']:
            out.append('### ToolCallRecord rows pointing at unknown tools')
            out.append('')
            out.append(
                'Telemetry references tool names that AREN\'T in '
                '`PA_TOOL_SCHEMAS`. Either renamed or telemetry from a '
                'different app version.'
            )
            out.append('')
            for name in tools['telemetry_unknown_tools'][:30]:
                out.append(f'- `{name}`')
            out.append('')

        if tools['never_executed']:
            out.append('### Tools with zero ToolCallRecord rows')
            out.append('')
            for name in tools['never_executed'][:50]:
                out.append(f'- `{name}`')
            if len(tools['never_executed']) > 50:
                out.append(
                    f'- … (+{len(tools["never_executed"]) - 50} more)'
                )
            out.append('')

        return '\n'.join(out) + '\n'
