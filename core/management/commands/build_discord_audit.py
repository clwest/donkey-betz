"""Generate ``docs/DISCORD_AUDIT.md`` by AST-parsing ``core/services/discord_bot.py``.

Built in Session 1115, sixth subsystem audit. Discord cogs live in a single
~11.7k-line file. Importing it side-effects (it tries to construct the bot
and may touch Discord client setup), so this command uses Python's ``ast``
module to read declarations statically. Same DOC-AUTOGEN pattern as the
other audits.

What it captures per Cog class:
- Class docstring (first paragraph).
- Every ``@app_commands.command`` and ``@commands.command`` method with
  the slash-command name, description string, method docstring, and
  file:line.

What it doesn't capture: command groups (``@app_commands.Group``),
context-menu commands, or autocomplete handlers. Those can be added if
they surface as gaps.

Run::

    python manage.py build_discord_audit
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand


REPO_ROOT = Path(__file__).resolve().parents[3]
DISCORD_FILE = REPO_ROOT / 'core' / 'services' / 'discord_bot.py'
OUTPUT_PATH = REPO_ROOT / 'docs' / 'DISCORD_AUDIT.md'


class Command(BaseCommand):
    help = "Regenerate docs/DISCORD_AUDIT.md from discord_bot.py AST."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--check', action='store_true',
            help='Print the would-be file to stdout instead of writing.',
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        if not DISCORD_FILE.exists():
            self.stderr.write(f"Discord file not found at {DISCORD_FILE}")
            return

        src = DISCORD_FILE.read_text(errors='ignore')
        tree = ast.parse(src)
        cogs = self._extract_cogs(tree)

        findings = self._collect_findings(cogs)
        rendered = self._render(cogs, findings=findings, source_lines=len(src.splitlines()))

        if opts['check']:
            self.stdout.write(rendered)
            return

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(rendered)
        n_commands = sum(len(c['commands']) for c in cogs)
        self.stdout.write(self.style.SUCCESS(
            f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} "
            f"({len(cogs)} Cog classes · {n_commands} commands · "
            f"{sum(1 for c in cogs if c['docstring']) } cogs with docstrings)"
        ))

    # ----------------------------------------------------------- inspect

    def _extract_cogs(self, tree: ast.AST) -> list[dict]:
        cogs: list[dict] = []
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if not self._inherits_cog(node):
                continue
            cogs.append({
                'name': node.name,
                'line': node.lineno,
                'docstring': self._first_paragraph(ast.get_docstring(node) or ''),
                'commands': self._extract_commands(node),
            })
        cogs.sort(key=lambda c: c['name'])
        return cogs

    def _inherits_cog(self, cls: ast.ClassDef) -> bool:
        for base in cls.bases:
            # Match `commands.Cog`, `discord.commands.Cog`, plain `Cog`, etc.
            text = ast.unparse(base) if hasattr(ast, 'unparse') else ''
            if 'Cog' in text:
                return True
        return False

    def _extract_commands(self, cls: ast.ClassDef) -> list[dict]:
        items: list[dict] = []
        for stmt in cls.body:
            if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in stmt.decorator_list:
                cmd = self._command_from_decorator(dec)
                if cmd is None:
                    continue
                method_doc = ast.get_docstring(stmt) or ''
                items.append({
                    'kind': cmd['kind'],
                    'name': cmd['name'] or stmt.name,
                    'description': cmd['description'],
                    'method': stmt.name,
                    'line': stmt.lineno,
                    'docstring': self._first_paragraph(method_doc),
                    'is_async': isinstance(stmt, ast.AsyncFunctionDef),
                })
                break  # one command decorator per method
        items.sort(key=lambda i: (i['kind'], i['name']))
        return items

    def _command_from_decorator(self, dec: ast.AST) -> dict | None:
        """Return {kind, name, description} if this is a command decorator."""
        if not isinstance(dec, ast.Call):
            return None
        unparsed = ast.unparse(dec.func) if hasattr(ast, 'unparse') else ''
        if 'app_commands.command' in unparsed:
            kind = 'slash'
        elif unparsed.endswith('.command') and not unparsed.endswith('app_commands.command'):
            kind = 'prefix'
        else:
            return None

        name = ''
        description = ''
        for kw in dec.keywords:
            if kw.arg == 'name' and isinstance(kw.value, ast.Constant):
                name = str(kw.value.value)
            elif kw.arg == 'description' and isinstance(kw.value, ast.Constant):
                description = str(kw.value.value)
        return {'kind': kind, 'name': name, 'description': description}

    # ---------------------------------------------------------- helpers

    def _first_paragraph(self, doc: str) -> str:
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

    # ---------------------------------------------------------- findings

    def _collect_findings(self, cogs: list[dict]) -> list[str]:
        findings: list[str] = []

        all_cmds = [(c['name'], cmd) for c in cogs for cmd in c['commands']]

        no_doc_cogs = [c['name'] for c in cogs if not c['docstring']]
        if no_doc_cogs:
            findings.append(
                f"Cogs with no class docstring: "
                f"`{', '.join(no_doc_cogs)}`. The audit uses the docstring "
                f"as the Cog's high-level description; missing one means the "
                f"reader has to inspect each command individually."
            )

        no_desc_cmds = [
            (cog, cmd['name']) for cog, cmd in all_cmds
            if cmd['kind'] == 'slash' and not cmd['description']
        ]
        if no_desc_cmds:
            findings.append(
                f"Slash commands with no `description=` — Discord shows the "
                f"description in the picker UI; missing one makes the command "
                f"invisible at use time: "
                + ', '.join(f'`{cog}::{name}`' for cog, name in no_desc_cmds[:10])
                + ('…' if len(no_desc_cmds) > 10 else '')
            )

        # Duplicate slash names across cogs
        from collections import Counter
        slash_names = Counter(
            cmd['name'] for cog, cmd in all_cmds if cmd['kind'] == 'slash'
        )
        dupes = sorted(n for n, c in slash_names.items() if c > 1)
        if dupes:
            findings.append(
                f"Duplicate slash command names across cogs (Discord will "
                f"refuse to sync the second one): {', '.join(f'`{n}`' for n in dupes)}."
            )

        # Big-cog heuristic
        big = sorted(cogs, key=lambda c: -len(c['commands']))[:3]
        big_summary = ', '.join(f"`{c['name']}` ({len(c['commands'])})" for c in big)
        findings.append(
            f"Largest cogs by command count: {big_summary}. Worth knowing if "
            f"you want to split for clarity."
        )

        return findings

    # ------------------------------------------------------------ render

    def _render(self, cogs: list[dict], *, findings: list[str], source_lines: int) -> str:
        n_cogs = len(cogs)
        all_cmds = [(c['name'], cmd) for c in cogs for cmd in c['commands']]
        n_slash = sum(1 for _, cmd in all_cmds if cmd['kind'] == 'slash')
        n_prefix = sum(1 for _, cmd in all_cmds if cmd['kind'] == 'prefix')

        out: list[str] = []
        out.append(
            '<!-- DOC-AUTOGEN: regenerated by '
            '`python manage.py build_discord_audit`. Do not hand-edit. -->'
        )
        out.append('')
        out.append('# Capability Audit — Discord Bot')
        out.append('')
        out.append(
            f"**Source of truth:** `core/services/discord_bot.py` "
            f"({source_lines:,} lines). AST-parsed in place (no import "
            f"side-effects)."
        )
        out.append('')
        out.append('## Headline')
        out.append('')
        out.append(f'- **Cog classes:** {n_cogs}')
        out.append(f'- **Slash commands (`@app_commands.command`):** {n_slash}')
        out.append(f'- **Prefix commands (`@*.command`):** {n_prefix}')
        out.append(
            f'- **Total commands:** {n_slash + n_prefix}. (Session 1115 '
            f'corrected the long-standing CLAUDE.md "144" figure — that '
            f'came from a regex that double-counted slash commands; AST '
            f'parsing gives the accurate {n_slash + n_prefix}.)'
        )
        out.append(
            f'- **Cogs with class docstrings:** '
            f'{sum(1 for c in cogs if c["docstring"])} / {n_cogs}'
        )
        out.append('')
        out.append(
            '> Discord users see slash commands in the picker UI; the '
            '`description=` argument is what shows up there. Prefix commands '
            '(`!foo`) are the older interaction style and don\'t have '
            'descriptions in the same way.'
        )
        out.append('')

        if findings:
            out.append('## Findings')
            out.append('')
            for f in findings:
                out.append(f'- {f}')
            out.append('')

        # Cog overview
        out.append('## Cogs overview')
        out.append('')
        out.append('| Cog | Line | Commands | Description |')
        out.append('|---|---:|---:|---|')
        for c in cogs:
            n_cmds = len(c['commands'])
            desc = c['docstring'] or '_(no docstring)_'
            desc = desc.replace('|', '\\|')
            if len(desc) > 100:
                desc = desc[:97] + '…'
            out.append(
                f'| `{c["name"]}` | {c["line"]} | {n_cmds} | {desc} |'
            )
        out.append('')

        # Per-cog detail
        out.append('## Per-cog command appendix')
        out.append('')
        out.append(
            'One block per Cog with its commands. The `description=` text on '
            'each slash command is what Discord shows in the picker; the '
            'method docstring (when present) is the implementer-facing note.'
        )
        out.append('')
        for c in cogs:
            out.append(
                f'### `{c["name"]}` '
                f'([line {c["line"]}](../core/services/discord_bot.py))'
            )
            out.append('')
            if c['docstring']:
                out.append(c['docstring'])
                out.append('')
            else:
                out.append('_(no Cog class docstring)_')
                out.append('')
            if not c['commands']:
                out.append('_(no command decorators found in this Cog)_')
                out.append('')
                continue
            out.append('| Type | Name | Method | Line | Description |')
            out.append('|:-:|---|---|---:|---|')
            for cmd in c['commands']:
                desc = cmd['description'] or cmd['docstring'] or '_(no description / docstring)_'
                desc = desc.replace('|', '\\|')
                if len(desc) > 90:
                    desc = desc[:87] + '…'
                kind_label = '/' if cmd['kind'] == 'slash' else '!'
                out.append(
                    f'| `{kind_label}` | `{cmd["name"]}` | `{cmd["method"]}` | '
                    f'{cmd["line"]} | {desc} |'
                )
            out.append('')

        return '\n'.join(out) + '\n'
