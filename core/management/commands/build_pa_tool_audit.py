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
    python manage.py build_pa_tool_audit --check           # dry-run stdout
    python manage.py build_pa_tool_audit --include-validation-xref  # S2795: adds Category+Lint cols
    python manage.py build_pa_tool_audit --emit-gap-json   # S2795: JSON gap map on stdout
    python manage.py build_pa_tool_audit --gap-only        # S2795: standalone gap-map artifact
    python manage.py build_pa_tool_audit --gap-only \\
        --output docs/audits/PA_TOOLS_GAP_MAP_S2795.md     # S2795: override output path

S2795 additions (this session): validation-doc cross-reference,
per-tool coverage categorization, schema-quality lint, triage slices.
Default behavior (no flags) unchanged for BC.
"""
from __future__ import annotations

import ast
import inspect
import json as _json
from pathlib import Path
from typing import Any, Optional

from django.core.management.base import BaseCommand


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_PATH = REPO_ROOT / 'docs' / 'PA_TOOL_AUDIT.md'
VALIDATION_DOCS_DIR = REPO_ROOT / 'docs' / 'research' / 'tools' / 'validation'


# Per-file cache so the same handler module is only read+parsed once even
# though many tools resolve to the same handler file (e.g. mixin surfaces
# like ``td_handlers_content.py`` host 6 tools). Keyed by absolute path.
_HANDLER_MODULE_CACHE: dict[str, tuple[str, str]] = {}


def _load_handler_module(handler_file_rel: str) -> tuple[str, str]:
    """Return ``(source_text, module_docstring)`` for a handler file.

    Ledger #5 substrate (S2938) — needed by the schema-vs-handler
    consistency lint in ``pa_tools_gap_map.lint_schema_vs_handler``.
    Silent-fail on read/parse errors (returns two empty strings) so
    handler introspection stays advisory and does not break the audit.
    """
    if not handler_file_rel:
        return ('', '')
    abs_path = str(REPO_ROOT / handler_file_rel)
    cached = _HANDLER_MODULE_CACHE.get(abs_path)
    if cached is not None:
        return cached
    try:
        source = Path(abs_path).read_text(encoding='utf-8', errors='replace')
    except OSError:
        _HANDLER_MODULE_CACHE[abs_path] = ('', '')
        return ('', '')
    docstring = ''
    try:
        docstring = ast.get_docstring(ast.parse(source)) or ''
    except (SyntaxError, ValueError):
        docstring = ''
    result = (source, docstring)
    _HANDLER_MODULE_CACHE[abs_path] = result
    return result


class Command(BaseCommand):
    help = "Regenerate docs/PA_TOOL_AUDIT.md from PA schema + dispatcher introspection."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--check',
            action='store_true',
            help='Print the would-be file to stdout instead of writing.',
        )
        # ── S2795 flags (all optional; default behavior unchanged) ─
        parser.add_argument(
            '--include-validation-xref',
            action='store_true',
            help=(
                'S2795: cross-reference validation docs at '
                'docs/research/tools/validation/ and add Category + Lint '
                'columns to the standard PA_TOOL_AUDIT.md table.'
            ),
        )
        parser.add_argument(
            '--emit-gap-json',
            action='store_true',
            help=(
                'S2795: emit the gap-map summary (categories, lints, '
                'triage slices, validation-doc totals) as JSON on stdout. '
                'Suppresses default markdown output when combined with '
                '--check.'
            ),
        )
        parser.add_argument(
            '--gap-only',
            action='store_true',
            help=(
                'S2795: write the standalone gap-map artifact only. '
                'Does NOT regenerate docs/PA_TOOL_AUDIT.md; produces the '
                'coverage/lint/triage table at --output (default: '
                'docs/audits/PA_TOOLS_GAP_MAP.md).'
            ),
        )
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help=(
                'S2795: override the output path (only meaningful with '
                '--gap-only). Path resolved relative to repo root.'
            ),
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

        # ── S2795: gap-map enrichment ────────────────────────────
        want_xref = bool(opts.get('include_validation_xref'))
        want_gap_json = bool(opts.get('emit_gap_json'))
        want_gap_only = bool(opts.get('gap_only'))
        gap_summary: Optional[dict] = None
        docs_index: Optional[dict] = None
        if want_xref or want_gap_json or want_gap_only:
            from core.services.pa_tools_gap_map import (
                build_gap_map,
                index_validation_docs,
                render_gap_map_markdown,
            )
            docs_index = index_validation_docs(VALIDATION_DOCS_DIR)
            gap_summary = build_gap_map(
                rows=rows,
                docs_index=docs_index,
                schemas_by_name=schema_names,
                run_agent_targets=run_agent_targets,
            )

        if want_gap_only:
            # Standalone gap-map artifact. Skip the default PA_TOOL_AUDIT.md
            # regeneration entirely — this path exists for the S2795 first
            # emit + any future one-shot re-runs Chris wants without
            # touching the established doc.
            assert gap_summary is not None and docs_index is not None
            output_path_str = opts.get('output')
            if output_path_str:
                target = Path(output_path_str)
                if not target.is_absolute():
                    target = REPO_ROOT / target
            else:
                target = REPO_ROOT / 'docs' / 'audits' / 'PA_TOOLS_GAP_MAP.md'
            rendered_gap = render_gap_map_markdown(
                rows=rows, summary=gap_summary, docs_index=docs_index
            )
            if opts.get('check'):
                self.stdout.write(rendered_gap)
                if want_gap_json:
                    self.stdout.write(_json.dumps(gap_summary, indent=2))
                return
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rendered_gap)
            headline = gap_summary['headline']
            self.stdout.write(self.style.SUCCESS(
                f"Wrote {target.relative_to(REPO_ROOT)} "
                f"(gap map · {headline['total_rows']} tool names · "
                f"{headline['per_category'].get('validated_full', 0)} full · "
                f"{headline['per_category'].get('validated_partial', 0)} partial · "
                f"{headline['per_category'].get('validated_doc_exists_unknown', 0)} unknown · "
                f"{headline['per_category'].get('untested', 0)} untested)"
            ))
            if want_gap_json:
                self.stdout.write(_json.dumps(gap_summary, indent=2))
            return

        findings = self._collect_findings(rows, run_agent_targets=run_agent_targets)
        rendered = self._render(
            rows,
            findings=findings,
            include_xref=want_xref,
            gap_summary=gap_summary,
        )

        if opts['check']:
            self.stdout.write(rendered)
            if want_gap_json and gap_summary is not None:
                self.stdout.write(_json.dumps(gap_summary, indent=2))
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
        if want_gap_json and gap_summary is not None:
            self.stdout.write(_json.dumps(gap_summary, indent=2))

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

        handler_source, handler_docstring = _load_handler_module(handler_file)

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
            'handler_source': handler_source,
            'handler_docstring': handler_docstring,
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

    def _render(
        self,
        rows: list[dict],
        *,
        findings: list[str],
        include_xref: bool = False,
        gap_summary: Optional[dict] = None,
    ) -> str:
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

        # S2795: optional gap-map section preceding the overview table.
        if include_xref and gap_summary is not None:
            from core.services.pa_tools_gap_map import CATEGORY_LABEL
            out.append('## Validation coverage (S2795)')
            out.append('')
            headline = gap_summary['headline']
            for cat, n in sorted(
                headline['per_category'].items(), key=lambda kv: -kv[1]
            ):
                label = CATEGORY_LABEL.get(cat, cat)
                out.append(f'- `{cat}` ({label}): **{n}**')
            per_lint = headline.get('per_lint') or {}
            if per_lint:
                out.append('')
                out.append('**Schema quality lints:**')
                for tag, n in sorted(per_lint.items(), key=lambda kv: -kv[1]):
                    out.append(f'- `{tag}`: **{n}** tools')
            out.append('')

        # Overview table
        out.append('## Tool overview')
        out.append('')
        if include_xref:
            out.append(
                '| Tool | Wiring | Actions | Required | Category | Lint | Summary |'
            )
            out.append('|---|:-:|:-:|:-:|---|---|---|')
        else:
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
            if include_xref:
                cat = r.get('category', '')
                lints_str = ', '.join(r.get('lints', [])) or '—'
                out.append(
                    f'| `{r["name"]}` | {wiring} | {n_actions or "—"} | '
                    f'{n_required or "—"} | {cat or "—"} | {lints_str} | '
                    f'{summary or "_(no description)_"} |'
                )
            else:
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
