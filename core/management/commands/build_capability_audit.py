"""Generate ``docs/CAPABILITY_AUDIT.md`` from live agent code.

Built in Session 1115. Code is the source of truth — this command introspects
every entry in ``AgentRouter.AGENT_MAP``, pulls its docstring / tools / wiring
signal directly from the class, and writes a deterministic markdown doc with
a ``<!-- DOC-AUTOGEN -->`` header so it goes through the same regeneration
pipeline as ``docs/INDEX.md``.

Run::

    python manage.py build_capability_audit

To regenerate after touching ``core/agents/`` or ``core/agent_router.py``.

The output is intentionally narrow:

- One row per ``AGENT_MAP`` entry.
- Columns: name, status, file path, docstring summary, tool count.
- Section per status bucket (enabled / rerouted / blocked) so the structure
  matches the live taxonomy already verified by ``verify_doc_claims``
  ``agent_taxonomy_reconciliation``.
- An appendix per agent with its full first-paragraph docstring and the list
  of named tool functions, so readers can scan WHAT an agent does without
  having to open the source file.

If an agent class is missing a docstring, that's a real finding, surfaced as
``(no docstring)``. The verifier follow-up adds a claim that flags such
agents so future drift gets caught.
"""
from __future__ import annotations

import inspect
import re
import textwrap
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_PATH = REPO_ROOT / 'docs' / 'CAPABILITY_AUDIT.md'

# Same hardcoded set as `core/epa_handlers/td_handlers_ops.py:3618` and
# `core/services/doc_claim_verification.py::_claude_agent_taxonomy`.
_NON_SPECIALIST = frozenset({
    # Session 1115 follow-up: ContentDistributionAgent removed —
    # kept in sync with td_handlers_ops.py + agent_router.py.
    'WorkflowAgent', 'VideoAgent', 'CodeGeneratorAgent', 'DevOpsAgent',
    'FullStackDeveloperAgent', 'CodeReviewAgent',
    'COOAgent', 'CTOAgent', 'AudioAgent',
})


class Command(BaseCommand):
    help = 'Regenerate docs/CAPABILITY_AUDIT.md from AGENT_MAP introspection.'

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
        except Exception as e:  # noqa: BLE001 — DB may be unavailable
            self.stderr.write(self.style.WARNING(
                f"AgentControlEntry unreachable ({type(e).__name__}); "
                f"falling back to hardcoded blocked={{'CodeGeneratorAgent'}}"
            ))
            blocked = {'CodeGeneratorAgent'}

        agent_map = AgentRouter.AGENT_MAP
        agent_map_keys = set(agent_map.keys())

        rows: list[dict] = []
        for name, cls in agent_map.items():
            row = self._inspect(name, cls, blocked)
            rows.append(row)

        rows.sort(key=lambda r: (r['status_order'], r['name']))

        # Findings: things the introspection caught that look wrong.
        findings: list[str] = []
        phantom_non_specialist = sorted(_NON_SPECIALIST - agent_map_keys)
        if phantom_non_specialist:
            findings.append(
                f"`_NON_SPECIALIST` references names that don't exist in AGENT_MAP: "
                f"`{', '.join(phantom_non_specialist)}`. Caught Session 1115. "
                f"Fixed in `platform_inventory.py` and "
                f"`doc_claim_verification.py`; routing layer in "
                f"`core/epa_handlers/td_handlers_ops.py` still contains the "
                f"entry — leaving it as a documented oddity rather than a code "
                f"behavior change."
            )
        no_doc = [r['name'] for r in rows if not r['has_docstring']]
        if no_doc:
            findings.append(
                f"Agents with no class docstring: `{', '.join(no_doc)}`. "
                f"Docstrings drive this audit; missing ones mean the agent's "
                f"capability won't show up here."
            )
        mismatched = [
            (r['name'], r['declared_name']) for r in rows
            if r['declared_name'] and not r['name_matches']
        ]
        if mismatched:
            findings.append(
                f"AGENT_MAP key ≠ class `name` attribute: "
                f"{', '.join(f'`{k}` (class declares `{v}`)' for k, v in mismatched)}."
            )

        rendered = self._render(rows, total=len(agent_map), findings=findings)

        if opts['check']:
            self.stdout.write(rendered)
            return

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(rendered)
        self.stdout.write(self.style.SUCCESS(
            f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} "
            f"({len(rows)} agents, {sum(1 for r in rows if r['has_docstring'])} "
            f"with docstrings, {sum(1 for r in rows if r['tool_count']) } "
            f"with explicit tool lists)"
        ))

    # ------------------------------------------------------------------ inspect

    def _inspect(self, name: str, cls: type, blocked: set[str]) -> dict:
        if name in blocked:
            status, status_order = 'blocked', 2
        elif name in _NON_SPECIALIST:
            status, status_order = 'rerouted', 1
        else:
            status, status_order = 'enabled', 0

        # File + line
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

        # Docstring
        doc = inspect.getdoc(cls) or ''
        has_docstring = bool(doc.strip())
        first_line = _first_meaningful_line(doc)

        # Tools (class attribute, list of OpenAI-style function specs OR raw)
        tools = getattr(cls, 'tools', None)
        tool_names: list[str] = []
        if isinstance(tools, (list, tuple)):
            for entry in tools:
                tname = _tool_name(entry)
                if tname:
                    tool_names.append(tname)
        tool_count = len(tool_names)

        # The agent's `name` attribute should match the AGENT_MAP key.
        declared_name = getattr(cls, 'name', None)
        name_matches = (declared_name == name) if declared_name else None

        return {
            'name': name,
            'class_name': cls.__name__,
            'declared_name': declared_name,
            'name_matches': name_matches,
            'status': status,
            'status_order': status_order,
            'file': str(rel_path) if rel_path else '(unknown)',
            'line': line_no,
            'has_docstring': has_docstring,
            'docstring_first_line': first_line,
            'docstring_full': doc,
            'tool_count': tool_count,
            'tool_names': tool_names,
        }

    # ----------------------------------------------------------------- render

    def _render(self, rows: list[dict], *, total: int, findings: list[str]) -> str:
        by_status = {'enabled': [], 'rerouted': [], 'blocked': []}
        for r in rows:
            by_status[r['status']].append(r)

        n_enabled = len(by_status['enabled'])
        n_rerouted = len(by_status['rerouted'])
        n_blocked = len(by_status['blocked'])
        n_with_doc = sum(1 for r in rows if r['has_docstring'])
        n_with_tools = sum(1 for r in rows if r['tool_count'])

        out: list[str] = []
        out.append(
            '<!-- DOC-AUTOGEN: regenerated by '
            '`python manage.py build_capability_audit`. Do not hand-edit. -->'
        )
        out.append('')
        out.append('# Capability Audit — Agents')
        out.append('')
        out.append(
            f'**Source of truth:** `core/agent_router.AgentRouter.AGENT_MAP`. '
            f'Class docstrings + `tools` class attribute introspected live.'
        )
        out.append('')
        out.append('## Headline')
        out.append('')
        out.append(f'- **Total agents in AGENT_MAP:** {total}')
        out.append(
            f'- **Taxonomy:** {n_enabled} enabled · {n_rerouted} rerouted '
            f'(hardcoded `_NON_SPECIALIST` set) · {n_blocked} blocked '
            f'(AgentControlEntry rows)'
        )
        out.append(
            f'- **Docstring coverage:** {n_with_doc} / {total} agents have a '
            f'class docstring ({_pct(n_with_doc, total)}%)'
        )
        out.append(
            f'- **Explicit `tools` lists:** {n_with_tools} / {total} '
            f'({_pct(n_with_tools, total)}%) — the rest delegate to '
            f'`BaseAgent` fallback tools or use direct LLM calls.'
        )
        out.append('')
        out.append(
            '> This is a static-code audit. Whether an agent is *actually '
            'wired* into a Celery task or a PA tool route is a different '
            'question — tracked separately (Session 1116+).'
        )
        out.append('')

        if findings:
            out.append('## Findings')
            out.append('')
            for f in findings:
                out.append(f'- {f}')
            out.append('')

        # Per-status overview tables
        for status_key, label in (
            ('enabled', 'Enabled'),
            ('rerouted', 'Rerouted'),
            ('blocked', 'Blocked'),
        ):
            bucket = by_status[status_key]
            if not bucket:
                continue
            out.append(f'## {label} agents ({len(bucket)})')
            out.append('')
            if status_key == 'rerouted':
                out.append(
                    '> Rerouted = `core/epa_handlers/td_handlers_ops.py` '
                    '`_NON_SPECIALIST` set sends these through a non-specialist '
                    'handler instead of the agent class directly.'
                )
                out.append('')
            elif status_key == 'blocked':
                out.append(
                    '> Blocked = a live `AgentControlEntry` row marks the agent '
                    'as disabled. Class still exists; AgentRouter refuses to '
                    'dispatch.'
                )
                out.append('')
            out.append('| Agent | File | Docs? | Tools | Summary |')
            out.append('|---|---|:-:|:-:|---|')
            for r in bucket:
                summary = (r['docstring_first_line'] or '_(no docstring)_').replace('|', '\\|')
                if len(summary) > 110:
                    summary = summary[:107] + '…'
                file_link = (
                    f'`{r["file"]}:{r["line"]}`' if r['line'] else f'`{r["file"]}`'
                )
                doc_mark = '✓' if r['has_docstring'] else '·'
                tools_cell = str(r['tool_count']) if r['tool_count'] else '—'
                out.append(
                    f'| `{r["name"]}` | {file_link} | {doc_mark} | {tools_cell} | {summary} |'
                )
            out.append('')

        # Detail appendix: full first-paragraph docstring + named tool list
        out.append('## Detail appendix')
        out.append('')
        out.append(
            'One block per agent, in the same status / alphabetical order as '
            'the tables above. The docstring text is exactly what `inspect.getdoc()` '
            'returns; the tool list is every OpenAI function-spec `name` found in '
            'the class\'s `tools` attribute.'
        )
        out.append('')
        for r in rows:
            out.append(f'### `{r["name"]}` — {r["status"]}')
            out.append('')
            out.append(f'**Location:** `{r["file"]}:{r["line"]}`')
            out.append('')
            if r['declared_name'] and not r['name_matches']:
                out.append(
                    f'> ⚠ AGENT_MAP key `{r["name"]}` does not match '
                    f'`name = "{r["declared_name"]}"` on the class.'
                )
                out.append('')
            if r['has_docstring']:
                paragraph = _first_paragraph(r['docstring_full'])
                out.append(_indent_paragraph(paragraph))
            else:
                out.append('_(no class docstring)_')
            out.append('')
            if r['tool_names']:
                out.append('**Tools:**')
                out.append('')
                for t in r['tool_names']:
                    out.append(f'- `{t}`')
                out.append('')
            else:
                out.append('**Tools:** _(none declared on class — uses BaseAgent fallback or direct LLM)_')
                out.append('')
        return '\n'.join(out) + '\n'


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _first_meaningful_line(doc: str) -> str:
    for line in doc.splitlines():
        s = line.strip()
        if s:
            return s
    return ''


def _first_paragraph(doc: str) -> str:
    lines: list[str] = []
    started = False
    for raw in doc.splitlines():
        s = raw.rstrip()
        if not s:
            if started:
                break
            continue
        started = True
        lines.append(s)
    return ' '.join(line.strip() for line in lines).strip()


def _indent_paragraph(text: str) -> str:
    if not text:
        return ''
    return textwrap.fill(text, width=88)


_TOOL_NAME_RE = re.compile(r"['\"]name['\"]\s*:\s*['\"]([\w-]+)['\"]")


def _tool_name(entry: Any) -> str:
    """Pull the function name out of an OpenAI-style tool spec.

    Handles both the canonical ``{"type": "function", "function": {"name": …}}``
    shape and the older flat ``{"name": …}`` shape.
    """
    if isinstance(entry, dict):
        fn = entry.get('function')
        if isinstance(fn, dict) and isinstance(fn.get('name'), str):
            return fn['name']
        if isinstance(entry.get('name'), str):
            return entry['name']
    return ''


def _pct(n: int, total: int) -> int:
    return int(round(100.0 * n / total)) if total else 0
