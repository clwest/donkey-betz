"""
Contract Monitor — detects schema/registry drift between components.

Session 1087: Autonomy Priority #2 — Contract/Schema Drift Detection

Checks:
1. PA Tool Schemas ↔ Tool Dispatcher handlers (tool_name mismatch)
2. Schema action enums ↔ handler action branches (action mismatch)
3. AGENT_MAP ↔ DB Agent records (stale/orphaned)
4. Celery Beat schedule ↔ registered tasks (phantom tasks)

Each check produces DriftFinding items classified by severity:
- critical: will cause runtime errors (missing handler, phantom task)
- warning: won't crash but indicates staleness (orphaned DB agents)
- info: cosmetic or expected (handler without schema = internal-only tool)
"""

import logging
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class DriftFinding:
    """A single drift finding."""
    check: str              # e.g. 'tool_schema_handler'
    severity: str           # 'critical', 'warning', 'info'
    component_a: str        # e.g. 'PA_TOOL_SCHEMAS'
    component_b: str        # e.g. 'ToolDispatcher'
    item: str               # e.g. 'run_agent'
    detail: str             # Human-readable explanation
    auto_repairable: bool = False
    repair_action: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class ContractMonitor:
    """
    Scans for drift between system contract surfaces.

    Usage:
        monitor = ContractMonitor()
        report = monitor.full_scan()
        # report = {
        #   'findings': [...],
        #   'critical': N,
        #   'warning': N,
        #   'info': N,
        #   'checks_run': [...],
        # }
    """

    def full_scan(self) -> dict:
        """Run all drift checks. Returns summary dict."""
        findings: list[DriftFinding] = []
        checks_run = []

        # Check 1: Tool schema ↔ handler registration
        try:
            findings.extend(self._check_tool_schema_handlers())
            checks_run.append('tool_schema_handlers')
        except Exception as e:
            logger.error(f"[ContractMonitor] tool_schema_handlers check error: {e}")

        # Check 2: Schema action enums ↔ handler action branches
        try:
            findings.extend(self._check_action_enum_coverage())
            checks_run.append('action_enum_coverage')
        except Exception as e:
            logger.error(f"[ContractMonitor] action_enum_coverage check error: {e}")

        # Check 3: AGENT_MAP ↔ DB Agent records
        try:
            findings.extend(self._check_agent_registry_drift())
            checks_run.append('agent_registry')
        except Exception as e:
            logger.error(f"[ContractMonitor] agent_registry check error: {e}")

        # Check 4: Celery Beat ↔ registered tasks
        try:
            findings.extend(self._check_celery_beat_drift())
            checks_run.append('celery_beat')
        except Exception as e:
            logger.error(f"[ContractMonitor] celery_beat check error: {e}")

        critical = sum(1 for f in findings if f.severity == 'critical')
        warning = sum(1 for f in findings if f.severity == 'warning')
        info = sum(1 for f in findings if f.severity == 'info')

        return {
            'findings': [f.to_dict() for f in findings],
            'critical': critical,
            'warning': warning,
            'info': info,
            'total': len(findings),
            'checks_run': checks_run,
        }

    # ── Check 1: Tool Schema ↔ Handler ────────────────────────────────

    def _check_tool_schema_handlers(self) -> list[DriftFinding]:
        """Compare PA_TOOL_SCHEMAS names vs ToolDispatcher registered handlers."""
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        from core.services.tool_dispatcher import ToolDispatcher

        findings = []

        schema_names = set()
        for s in PA_TOOL_SCHEMAS:
            if isinstance(s, dict):
                name = s.get('name', '')
                if name:
                    schema_names.add(name)

        td = ToolDispatcher()
        handler_names = set(td._tool_handlers.keys())

        # Schema defines tool but no handler → GPT will call it, handler 404
        # Exception: 'run_agent' is handled specially in the entrypoint
        meta_tools = {'run_agent'}
        for name in schema_names - handler_names - meta_tools:
            findings.append(DriftFinding(
                check='tool_schema_handler',
                severity='critical',
                component_a='PA_TOOL_SCHEMAS',
                component_b='ToolDispatcher',
                item=name,
                detail=f'Schema defines tool "{name}" but no handler registered. '
                       f'GPT-5.2 may call this tool and get a 404 error.',
            ))

        # Handler registered but no schema → tool exists but GPT can't call it
        # Exclude agent-delegation handlers — these are invoked via the `run_agent`
        # meta-tool and intentionally don't have individual schemas.
        agent_handler_names = {
            name for name, handler in td._tool_handlers.items()
            if getattr(handler, '__func__', handler).__name__ == '_handle_agent_tool'
        }
        orphan_handlers = handler_names - schema_names - agent_handler_names

        for name in orphan_handlers:
            findings.append(DriftFinding(
                check='tool_schema_handler',
                severity='info',
                component_a='ToolDispatcher',
                component_b='PA_TOOL_SCHEMAS',
                item=name,
                detail=f'Handler "{name}" registered but no PA schema. '
                       f'Tool exists but GPT cannot invoke it.',
            ))

        return findings

    # ── Check 2: Action Enum Coverage ─────────────────────────────────

    def _check_action_enum_coverage(self) -> list[DriftFinding]:
        """
        For tools with 'action' enum in schema, check that the handler
        has corresponding branches for each action value.

        This catches the common bug: schema has action='new_thing' but
        handler returns "Unknown action: new_thing".
        """
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        from core.services.tool_dispatcher import ToolDispatcher
        import inspect

        findings = []
        td = ToolDispatcher()

        for schema in PA_TOOL_SCHEMAS:
            if not isinstance(schema, dict):
                continue

            name = schema.get('name', '')
            params = schema.get('parameters', {})
            props = params.get('properties', {})
            action_prop = props.get('action', {})
            action_enum = action_prop.get('enum', [])

            if not action_enum or not name:
                continue

            # Get the handler source code
            handler = td._tool_handlers.get(name)
            if not handler:
                continue  # Already caught by check 1

            try:
                source = inspect.getsource(handler)
            except (TypeError, OSError):
                continue

            # Check which actions appear in the source
            missing_actions = []
            for action_value in action_enum:
                # Look for the action string in the handler source
                # Common patterns: == 'action_value', action == 'action_value',
                # 'action_value' in ..., elif action_value
                if (
                    f"'{action_value}'" not in source
                    and f'"{action_value}"' not in source
                ):
                    missing_actions.append(action_value)

            if missing_actions:
                findings.append(DriftFinding(
                    check='action_enum_coverage',
                    severity='warning',
                    component_a=f'PA_TOOL_SCHEMAS[{name}].action.enum',
                    component_b=f'ToolDispatcher._handle_{name}',
                    item=name,
                    detail=f'Schema defines actions {missing_actions} but '
                           f'they don\'t appear in handler source. '
                           f'GPT may request these and get "Unknown action".',
                ))

        return findings

    # ── Check 3: Agent Registry Drift ──────────────────────────────────

    def _check_agent_registry_drift(self) -> list[DriftFinding]:
        """Compare AGENT_MAP (code) vs Agent model (DB)."""
        findings = []

        try:
            from core.agent_router import AgentRouter
            agent_map = getattr(AgentRouter, 'AGENT_MAP', {})
            code_agents = set(agent_map.keys())
        except Exception:
            return findings

        try:
            from core.models_unified_system import Agent
            db_agents = set(
                Agent.objects.values_list('name', flat=True)
            )
        except Exception:
            return findings

        # In code but not in DB → agent class exists but not seeded
        for name in code_agents - db_agents:
            findings.append(DriftFinding(
                check='agent_registry',
                severity='info',
                component_a='AGENT_MAP',
                component_b='Agent (DB)',
                item=name,
                detail=f'Agent "{name}" in AGENT_MAP but not in DB. '
                       f'Agent works but won\'t appear in agent introspection.',
            ))

        # In DB but not in code → stale DB record (agent removed from code)
        # Filter out persona/dynamic agents (those are DB-only by design)
        try:
            from core.models_unified_system import Agent
            stale_candidates = Agent.objects.filter(
                name__in=list(db_agents - code_agents),
            ).exclude(
                category__name__in=['persona', 'dynamic', 'specialist'],
            ).exclude(
                # Dynamic persona agents have spaces in names (DB-only)
                name__regex=r'.+ .+',
            ).values_list('name', flat=True)

            for name in stale_candidates:
                findings.append(DriftFinding(
                    check='agent_registry',
                    severity='warning',
                    component_a='Agent (DB)',
                    component_b='AGENT_MAP',
                    item=name,
                    detail=f'Agent "{name}" in DB but not in AGENT_MAP. '
                           f'May be stale or a persona agent.',
                ))
        except Exception:
            pass

        return findings

    # ── Check 4: Celery Beat Drift ─────────────────────────────────────

    def _check_celery_beat_drift(self) -> list[DriftFinding]:
        """Check that Beat schedule references tasks that are actually registered."""
        findings = []

        try:
            from django.conf import settings
            beat_schedule = getattr(settings, 'CELERY_BEAT_SCHEDULE', {})
        except Exception:
            return findings

        try:
            from celery import current_app
            # Force task discovery
            current_app.loader.import_default_modules()
            registered_tasks = set(current_app.tasks.keys())
        except Exception:
            registered_tasks = set()

        if not registered_tasks:
            # Can't check if we don't have the registry
            return findings

        for schedule_name, config in beat_schedule.items():
            task_name = config.get('task', '')
            if not task_name:
                continue

            if task_name not in registered_tasks:
                findings.append(DriftFinding(
                    check='celery_beat',
                    severity='critical',
                    component_a=f'CELERY_BEAT_SCHEDULE[{schedule_name}]',
                    component_b='Celery task registry',
                    item=task_name,
                    detail=f'Beat schedule "{schedule_name}" references task '
                           f'"{task_name}" which is not registered. '
                           f'This task will silently fail on every beat cycle.',
                ))

        return findings

    # ── Summary for governance ─────────────────────────────────────────

    def summary_for_governance(self, report: dict) -> str:
        """Generate a human-readable summary for governance alerts."""
        lines = [
            f"**Contract Monitor Scan** — "
            f"{report['critical']} critical, "
            f"{report['warning']} warning, "
            f"{report['info']} info",
            f"Checks run: {', '.join(report['checks_run'])}",
        ]

        # Only show critical + warning in the summary
        for finding in report['findings']:
            if finding['severity'] in ('critical', 'warning'):
                lines.append(
                    f"- [{finding['severity'].upper()}] "
                    f"{finding['item']}: {finding['detail'][:120]}"
                )

        return '\n'.join(lines)
