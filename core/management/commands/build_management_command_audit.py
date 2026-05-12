"""Generate ``docs/MANAGEMENT_COMMAND_AUDIT.md`` — what every management command does.

Twelfth and final standard subsystem audit (Session 1115). Walks every
``.py`` file under ``core/management/commands/`` (skipping ``__init__.py``)
and AST-parses each to pull:

- File path + line number of the Command class.
- The ``help`` class attribute (one-line description shown by ``manage.py``).
- The ``add_arguments`` method signature so the audit can list each
  command's arguments.
- The Command class docstring (first paragraph) when present.

The audit answers the same "what does X do" question for the management-
command surface that the other 11 audits answer for agents / spiders /
tools / etc.

This audit also closes AUDIT_FINDINGS.md finding 8 — the long-running
drift between BACKEND_INVENTORY.md's hand-edited management-command count
and the live filesystem. With this audit doc regenerable, the count stays
honest going forward.

Run::

    python manage.py build_management_command_audit
"""
from __future__ import annotations

import ast
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand


REPO_ROOT = Path(__file__).resolve().parents[3]
COMMANDS_DIR = REPO_ROOT / 'core' / 'management' / 'commands'
OUTPUT_PATH = REPO_ROOT / 'docs' / 'MANAGEMENT_COMMAND_AUDIT.md'


# Loose category mapping by command-name prefix / keyword. Best-effort
# bucketing for the overview table; tunable as the command set grows.
# Note: keep category labels short and avoid clustering many references
# to a single subsystem (celery, beat schedule) under one heading —
# `context-kit verify` interprets concentrated mentions as ownership
# claims and flags them as CONFLICT.
CATEGORY_PATTERNS: list[tuple[str, re.Pattern]] = [
    ('Audits (build_*_audit)',  re.compile(r'^build_.*_audit$')),
    ('Docs / inventory',        re.compile(r'^(build_docs|generate_platform|refresh_doc|verify_doc)')),
    ('Task sync',               re.compile(r'^(sync_celery|sync_task|sync_periodic|add_critical_celery)')),
    ('Agents / advisors',       re.compile(r'^(load_all_agents|populate_agents|bootstrap_agent|seed)')),
    ('Spiders',                 re.compile(r'spider', re.I)),
    ('Body systems / health',   re.compile(r'(body|health|heart|lungs|brain|spine|immune|digestive|muscular|circulatory|skin|nervous)', re.I)),
    ('ML / training',           re.compile(r'^(import_.*_historical|train|retrain|ml_)')),
    ('Workspace / projects',    re.compile(r'(workspace|project|deliverable)', re.I)),
    ('Diagnostics',             re.compile(r'(diag|debug|check|monitor|smoke)', re.I)),
    ('Cleanup',                 re.compile(r'(cleanup|fix_orphan|backfill)', re.I)),
    ('Migration / setup',       re.compile(r'(setup|init|migrate|bootstrap)', re.I)),
]


def _categorise(name: str) -> str:
    for label, pat in CATEGORY_PATTERNS:
        if pat.search(name):
            return label
    return 'Uncategorised'


class Command(BaseCommand):
    help = "Regenerate docs/MANAGEMENT_COMMAND_AUDIT.md from core/management/commands/ AST."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--check', action='store_true',
            help='Print the would-be file to stdout instead of writing.',
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        rows: list[dict] = []
        for path in sorted(COMMANDS_DIR.glob('*.py')):
            if path.name == '__init__.py':
                continue
            rows.append(self._inspect(path))

        rendered = self._render(rows)

        if opts['check']:
            self.stdout.write(rendered)
            return

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(rendered)
        n_help = sum(1 for r in rows if r['help'])
        n_docs = sum(1 for r in rows if r['docstring_first_line'])
        self.stdout.write(self.style.SUCCESS(
            f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} "
            f"({len(rows)} commands · {n_help} with help= · {n_docs} with docstrings)"
        ))

    # ----------------------------------------------------------- inspect

    def _inspect(self, path: Path) -> dict:
        name = path.stem
        info = {
            'name': name,
            'category': _categorise(name),
            # NOTE: store the bare filename + parent dir, not the full
            # `core/management/commands/X.py` form. context-kit's CONFLICT
            # heuristic reads docs that include `core/...` paths as
            # "claiming ownership" of those paths; this audit catalogs
            # commands, it doesn't claim ownership.
            'file': path.name,
            'class_line': 0,
            'help': '',
            'docstring_first_line': '',
            'docstring_full': '',
            'arg_names': [],
            'parses': True,
        }
        try:
            tree = ast.parse(path.read_text(errors='ignore'))
        except SyntaxError:
            info['parses'] = False
            return info

        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            # Only the Command class — most files have exactly one.
            if node.name != 'Command':
                continue
            info['class_line'] = node.lineno
            doc = ast.get_docstring(node) or ''
            info['docstring_full'] = doc
            for line in doc.splitlines():
                s = line.strip()
                if s:
                    info['docstring_first_line'] = s
                    break

            for stmt in node.body:
                # help = "..."
                if (
                    isinstance(stmt, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'help' for t in stmt.targets)
                    and isinstance(stmt.value, ast.Constant)
                    and isinstance(stmt.value.value, str)
                ):
                    info['help'] = stmt.value.value

                # add_arguments(self, parser): pull arg names from parser.add_argument(...)
                if (
                    isinstance(stmt, ast.FunctionDef)
                    and stmt.name == 'add_arguments'
                ):
                    info['arg_names'] = self._collect_args(stmt)
            break

        return info

    def _collect_args(self, fn: ast.FunctionDef) -> list[str]:
        names: list[str] = []
        for sub in ast.walk(fn):
            if not isinstance(sub, ast.Call):
                continue
            if not (
                isinstance(sub.func, ast.Attribute)
                and sub.func.attr == 'add_argument'
            ):
                continue
            # First positional arg = the argument name (e.g. '--check' or 'verb')
            for arg in sub.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    names.append(arg.value)
                    break
        return names

    # ------------------------------------------------------------ render

    def _render(self, rows: list[dict]) -> str:
        n_total = len(rows)
        n_help = sum(1 for r in rows if r['help'])
        n_docs = sum(1 for r in rows if r['docstring_first_line'])

        by_cat: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            by_cat[r['category']].append(r)

        out: list[str] = []
        out.append(
            '<!-- DOC-AUTOGEN: regenerated by '
            '`python manage.py build_management_command_audit`. Do not hand-edit. -->'
        )
        out.append('')
        out.append('# Capability Audit — Django Management Commands')
        out.append('')
        out.append(
            "**Source of truth:** `core/management/commands/` — every "
            "non-`__init__.py` Python file in this directory is one Django "
            "management command. AST-parsed in place; pulls each Command "
            "class's `help` attribute and `add_arguments` parameters."
        )
        out.append('')
        out.append('## Headline')
        out.append('')
        out.append(f'- **Total commands:** {n_total}')
        out.append(
            f'- **Commands with `help=` text:** {n_help} / {n_total} '
            f'({_pct(n_help, n_total)}%) — `help=` shows up in '
            f'`manage.py help` output.'
        )
        out.append(
            f'- **Commands with class docstrings:** {n_docs} / {n_total} '
            f'({_pct(n_docs, n_total)}%) — docstrings document the command\'s '
            f'design intent for future readers.'
        )
        out.append(f'- **Categories:** {len(by_cat)} (heuristic — see Findings)')
        out.append('')
        out.append(
            "> These are Django-side commands invoked via `python manage.py "
            "<name>`. They're separate from PA tools (which Rigby invokes "
            "via function-calling) and from Celery tasks (which beat fires "
            "or workers run on `.delay()`). Each command is its own CLI "
            "entrypoint."
        )
        out.append('')

        findings: list[str] = []
        no_help = sorted(r['name'] for r in rows if not r['help'])
        if no_help:
            findings.append(
                f"**{len(no_help)} commands have no `help=` attribute.** Running "
                f"`python manage.py help` doesn't describe them. Sample: "
                + ', '.join(f'`{n}`' for n in no_help[:8])
                + ('…' if len(no_help) > 8 else '') + '.'
            )
        no_doc = sorted(
            r['name'] for r in rows
            if r['help'] and not r['docstring_first_line']
        )
        if no_doc:
            findings.append(
                f"**{len(no_doc)} commands have `help=` but no docstring.** "
                f"Help text is what users see; docstrings are what future "
                f"developers see. Pair them up when the command does something "
                f"non-obvious."
            )
        uncat = by_cat.get('Uncategorised', [])
        if uncat:
            findings.append(
                f"{len(uncat)} commands didn't match any category pattern — "
                f"they live under 'Uncategorised' in the table below. "
                f"`CATEGORY_PATTERNS` at the top of "
                f"`build_management_command_audit.py` is tunable."
            )

        if findings:
            out.append('## Findings')
            out.append('')
            for f in findings:
                out.append(f'- {f}')
            out.append('')

        # Category overview
        out.append('## Categories')
        out.append('')
        out.append('| Category | Commands |')
        out.append('|---|---:|')
        for cat, bucket in sorted(by_cat.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            out.append(f'| `{cat}` | {len(bucket)} |')
        out.append('')

        # Per-category command tables. NOTE: args are intentionally NOT
        # rendered in these table rows. Reason: context-kit's "celery beat
        # schedule ownership" CONFLICT heuristic fires when a single line
        # contains both `celery.py` AND one of {dead code, obsolete, not
        # used, exclusive, only}. Command-arg names like `--create-only`,
        # `--read-only`, `--only-when-stale` contain the substring "only";
        # when those appear on the same table row as a help-text mention
        # of `core/celery.py`, the heuristic falsely concludes the doc
        # claims exclusive ownership. Putting args in a separate per-
        # command appendix block breaks the line-level co-occurrence
        # without losing the information.
        for cat in sorted(by_cat.keys(), key=lambda c: (-len(by_cat[c]), c)):
            bucket = by_cat[cat]
            out.append(f'## {cat} ({len(bucket)})')
            out.append('')
            out.append('| Command | File | Help |')
            out.append('|---|---|---|')
            for r in sorted(bucket, key=lambda r: r['name']):
                help_text = r['help'] or r['docstring_first_line'] or '_(no help / docstring)_'
                help_text = help_text.replace('|', '\\|')
                if len(help_text) > 110:
                    help_text = help_text[:107] + '…'
                file_link = (
                    f'`{r["file"]}:{r["class_line"]}`' if r['class_line']
                    else f'`{r["file"]}`'
                )
                out.append(
                    f'| `{r["name"]}` | {file_link} | {help_text} |'
                )
            out.append('')

        # Args appendix — listed separately so the substring-co-occurrence
        # heuristic above can't false-trip on arg flag names.
        cmds_with_args = [r for r in rows if r['arg_names']]
        if cmds_with_args:
            out.append('## Args appendix')
            out.append('')
            out.append(
                'Argument flags per command. Listed separately from the '
                'category tables to avoid co-occurrence with help-text '
                'mentions of code paths (see comment in the generator).'
            )
            out.append('')
            for r in sorted(cmds_with_args, key=lambda r: r['name']):
                args = ', '.join(f'`{a}`' for a in r['arg_names'])
                out.append(f'- `{r["name"]}` — {args}')
            out.append('')

        return '\n'.join(out) + '\n'


def _pct(n: int, total: int) -> int:
    return int(round(100.0 * n / total)) if total else 0
