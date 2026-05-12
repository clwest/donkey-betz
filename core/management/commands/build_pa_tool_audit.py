"""Generate ``docs/PA_TOOL_AUDIT.md`` — the runtime-derived "what can Rigby do?".

Built in Session 1115, sibling to ``build_capability_audit`` (agents) and
``build_spider_audit`` (spiders). Walks the live PA tool registry:

- ``core.services.pa_tool_schemas.PA_TOOL_SCHEMAS`` — list of OpenAI
  function-calling specs the LLM sees.
- ``core.services.tool_dispatcher.ToolDispatcher`` — runtime registry that
  maps a tool name to a handler callable.

The interesting cross-checks aren't the totals, they're the *gaps*:

- Schemas with no registered handler ⇒ the LLM can pick the tool, nothing
  answers, user sees a failure.
- Handlers with no schema ⇒ dead registration, handler will never fire
  because the LLM has no way to know it exists.

Run::

    python manage.py build_pa_tool_audit
"""
from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_PATH = REPO_ROOT / 'docs' / 'PA_TOOL_AUDIT.md'


class Command(BaseCommand):
    help = "Regenerate docs/PA_TOOL_AUDIT.md from PA schema + dispatcher introspection."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--check',
            action='store_true',
            help='Print the would-be file to stdout instead of writing.',
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        from core.services.tool_dispatcher import ToolDispatcher
        td = ToolDispatcher()
        handlers: dict[str, Any] = td._tool_handlers  # noqa: SLF001

        schema_names = {s.get('name', ''): s for s in PA_TOOL_SCHEMAS if s.get('name')}
        handler_names = set(handlers.keys())

        rows: list[dict] = []
        for name in sorted(schema_names.keys() | handler_names):
            schema = schema_names.get(name)
            handler = handlers.get(name)
            rows.append(self._inspect(name, schema, handler))

        # Capture the run_agent meta-tool's agent_name enum so the findings
        # logic can recognise its target list as "by design, not broken."
        run_agent_schema = schema_names.get('run_agent') or {}
        run_agent_targets: set[str] = set()
        params = run_agent_schema.get('parameters', {}) or {}
        props = params.get('properties', {}) or {}
        agent_name_enum = (props.get('agent_name') or {}).get('enum', []) or []
        run_agent_targets = set(agent_name_enum)

        findings = self._collect_findings(rows, run_agent_targets=run_agent_targets)
        rendered = self._render(rows, findings=findings)

        if opts['check']:
            self.stdout.write(rendered)
            return

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(rendered)
        n_schemas = sum(1 for r in rows if r['has_schema'])
        n_handlers = sum(1 for r in rows if r['has_handler'])
        n_both = sum(1 for r in rows if r['has_schema'] and r['has_handler'])
        self.stdout.write(self.style.SUCCESS(
            f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} "
            f"({len(rows)} tool names · {n_schemas} schemas · "
            f"{n_handlers} handlers · {n_both} wired both sides)"
        ))

    # ----------------------------------------------------------- inspect

    def _inspect(self, name: str, schema: dict | None, handler: Any | None) -> dict:
        actions: list[str] = []
        action_desc = ''
        description = ''
        required: list[str] = []
        param_names: list[str] = []
        if schema:
            description = schema.get('description', '') or ''
            params = schema.get('parameters', {}) or {}
            props = params.get('properties', {}) or {}
            param_names = list(props.keys())
            required = list(params.get('required', []) or [])
            action_prop = props.get('action') or {}
            actions = list(action_prop.get('enum', []) or [])
            action_desc = action_prop.get('description', '') or ''

        handler_name = ''
        handler_file = ''
        handler_line = 0
        if handler is not None:
            try:
                handler_name = getattr(handler, '__qualname__', '') or getattr(handler, '__name__', '')
                handler_file = inspect.getfile(handler)
                try:
                    handler_file = str(Path(handler_file).resolve().relative_to(REPO_ROOT))
                except ValueError:
                    pass
                try:
                    _, handler_line = inspect.getsourcelines(handler)
                except (OSError, TypeError):
                    handler_line = 0
            except (TypeError, OSError):
                pass

        return {
            'name': name,
            'has_schema': schema is not None,
            'has_handler': handler is not None,
            'description': description,
            'param_names': param_names,
            'required': required,
            'actions': actions,
            'action_desc': action_desc,
            'handler_name': handler_name,
            'handler_file': handler_file,
            'handler_line': handler_line,
        }

    # ---------------------------------------------------------- findings

    def _collect_findings(self, rows: list[dict], run_agent_targets: set[str]) -> list[str]:
        findings: list[str] = []

        # `run_agent` is intercepted at unified_pa_entrypoint.py:1488 (the
        # meta-tool decomposition) BEFORE reaching the dispatcher, so it
        # legitimately has no handler. Its `agent_name` enum lists the agent
        # tools that ARE expected to be handler-only — the LLM reaches them
        # via `run_agent(agent_name="x")`, not via direct schema, so they
        # don't need their own LLM-visible schema either.
        META_NO_HANDLER = {'run_agent'}

        no_handler = sorted(
            r['name'] for r in rows
            if r['has_schema'] and not r['has_handler']
            and r['name'] not in META_NO_HANDLER
        )
        if no_handler:
            findings.append(
                f"Schemas with **no registered handler** — LLM can call these "
                f"but nothing answers, user sees a failure: "
                f"`{', '.join(no_handler)}`."
            )

        no_schema_real = sorted(
            r['name'] for r in rows
            if r['has_handler'] and not r['has_schema']
            and r['name'] not in run_agent_targets
        )
        if no_schema_real:
            findings.append(
                f"Handlers with **no schema and not reachable via** `run_agent` "
                f"— dead registration, LLM has no way to invoke these: "
                f"`{', '.join(no_schema_real)}`."
            )
        no_schema_via_run_agent = sorted(
            r['name'] for r in rows
            if r['has_handler'] and not r['has_schema']
            and r['name'] in run_agent_targets
        )
        if no_schema_via_run_agent:
            findings.append(
                f"Handler-only entries that the LLM reaches via the "
                f"`run_agent(agent_name=…)` meta-tool (by design, not a bug): "
                f"{len(no_schema_via_run_agent)} agents — these are the "
                f"agent-routing bypass paths sharing `_handle_agent_tool`."
            )

        no_desc = sorted(
            r['name'] for r in rows
            if r['has_schema'] and not r['description'].strip()
        )
        if no_desc:
            findings.append(
                f"Schemas with **no description** — the LLM uses the "
                f"description as the routing signal, so a missing one means "
                f"the tool is invisible at function-calling time: "
                f"`{', '.join(no_desc)}`."
            )

        # Handler-side sharing: how many tool names point at the same handler?
        from collections import Counter
        handler_share = Counter(
            r['handler_name'] for r in rows
            if r['has_handler'] and r['handler_name']
        )
        shared = {h: n for h, n in handler_share.items() if n >= 5}
        if shared:
            top = ', '.join(
                f'`{h}` ({n})' for h, n in sorted(shared.items(), key=lambda kv: -kv[1])[:5]
            )
            findings.append(
                f"Heavily-shared handlers (≥5 tool names route to the same "
                f"function — usually a gateway / meta-tool by design): {top}."
            )

        return findings

    # ------------------------------------------------------------ render

    def _render(self, rows: list[dict], *, findings: list[str]) -> str:
        n_total = len(rows)
        n_schemas = sum(1 for r in rows if r['has_schema'])
        n_handlers = sum(1 for r in rows if r['has_handler'])
        n_both = sum(1 for r in rows if r['has_schema'] and r['has_handler'])
        n_action_based = sum(1 for r in rows if r['actions'])

        out: list[str] = []
        out.append(
            '<!-- DOC-AUTOGEN: regenerated by '
            '`python manage.py build_pa_tool_audit`. Do not hand-edit. -->'
        )
        out.append('')
        out.append('# Capability Audit — PA (Rigby) Tools')
        out.append('')
        out.append(
            "**Source of truth:** "
            "`core.services.pa_tool_schemas.PA_TOOL_SCHEMAS` (the function-"
            "calling specs the LLM sees) + "
            "`core.services.tool_dispatcher.ToolDispatcher._tool_handlers` "
            "(the runtime name→handler registry). Cross-referenced live."
        )
        out.append('')
        out.append('## Headline')
        out.append('')
        out.append(f'- **Unique tool names across both sides:** {n_total}')
        out.append(f'- **Schemas (LLM sees):** {n_schemas}')
        out.append(f'- **Handlers (runtime registered):** {n_handlers}')
        out.append(
            f'- **Wired on both sides (schema ↔ handler):** {n_both} '
            f'({_pct(n_both, n_total)}% of unique tool names)'
        )
        out.append(
            f'- **Action-based tools:** {n_action_based} of {n_schemas} schemas '
            f'(use an `action` enum to multiplex verbs into a single tool)'
        )
        out.append('')
        out.append(
            "> The Rigby (PA) function-calling pipeline lives in "
            "`core.services.unified_pa_entrypoint`. The LLM sees these "
            "schemas, decides which tool(s) to call, the dispatcher routes "
            "the call to its handler."
        )
        out.append('')

        if findings:
            out.append('## Findings')
            out.append('')
            for f in findings:
                out.append(f'- {f}')
            out.append('')

        # Overview table
        out.append('## Tool overview')
        out.append('')
        out.append('| Tool | Wiring | Actions | Required | Summary |')
        out.append('|---|:-:|:-:|:-:|---|')
        for r in rows:
            wiring = (
                '✓ ✓' if (r['has_schema'] and r['has_handler']) else
                ('schema only' if r['has_schema'] else 'handler only')
            )
            n_actions = len(r['actions'])
            n_required = len(r['required'])
            summary = r['description'].split('. ')[0].replace('|', '\\|')
            if len(summary) > 110:
                summary = summary[:107] + '…'
            out.append(
                f'| `{r["name"]}` | {wiring} | {n_actions or "—"} | '
                f'{n_required or "—"} | {summary or "_(no description)_"} |'
            )
        out.append('')

        # Detail appendix
        out.append('## Detail appendix')
        out.append('')
        out.append(
            'One block per tool name (union of schemas and handlers). The '
            'description is the natural-language routing signal the LLM uses '
            'to pick the tool. Action enum values are how the same tool '
            'multiplexes verbs.'
        )
        out.append('')
        for r in rows:
            out.append(f'### `{r["name"]}`')
            out.append('')
            wiring_bits = []
            if r['has_schema']:
                wiring_bits.append('schema in `pa_tool_schemas.py`')
            if r['has_handler']:
                if r['handler_file']:
                    wiring_bits.append(
                        f'handler `{r["handler_name"]}` '
                        f'in `{r["handler_file"]}'
                        + (f':{r["handler_line"]}`' if r['handler_line'] else '`')
                    )
                else:
                    wiring_bits.append(f'handler `{r["handler_name"]}`')
            out.append('**Wiring:** ' + ' · '.join(wiring_bits))
            out.append('')
            if r['description']:
                desc = r['description'].strip()
                out.append(desc)
                out.append('')
            else:
                out.append('_(no schema description)_')
                out.append('')
            if r['actions']:
                out.append('**Actions:**')
                out.append('')
                for action in r['actions']:
                    out.append(f'- `{action}`')
                out.append('')
            if r['required']:
                out.append(f'**Required parameters:** {", ".join(f"`{p}`" for p in r["required"])}')
                out.append('')

        return '\n'.join(out) + '\n'


def _pct(n: int, total: int) -> int:
    return int(round(100.0 * n / total)) if total else 0
