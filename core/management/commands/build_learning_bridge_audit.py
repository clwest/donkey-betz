"""Generate ``docs/LEARNING_BRIDGE_AUDIT.md`` — what each learning bridge does.

Built in Session 1115, eighth subsystem audit. Learning bridges are Django-
signal-driven shims that connect runtime events (agent executions, job
applications, advisor consultations, spider data) to the unified learning
pipeline. They self-register at app startup (`core/apps.py`).

The directory `core/learning_bridges/` is itself the registry — every
`*_bridge.py` file is one bridge. Each file defines one or more "learning
loop" / "learning bridge" classes. AST-parsed in place.

Run::

    python manage.py build_learning_bridge_audit
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand


REPO_ROOT = Path(__file__).resolve().parents[3]
BRIDGES_DIR = REPO_ROOT / 'core' / 'learning_bridges'
OUTPUT_PATH = REPO_ROOT / 'docs' / 'LEARNING_BRIDGE_AUDIT.md'


class Command(BaseCommand):
    help = "Regenerate docs/LEARNING_BRIDGE_AUDIT.md from learning_bridges/ AST."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--check', action='store_true',
            help='Print the would-be file to stdout instead of writing.',
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        rows: list[dict] = []
        for path in sorted(BRIDGES_DIR.glob('*_bridge.py')):
            rows.append(self._inspect(path))

        findings = self._collect_findings(rows)
        rendered = self._render(rows, findings=findings)

        if opts['check']:
            self.stdout.write(rendered)
            return

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(rendered)
        n_with_doc = sum(1 for r in rows if r['module_docstring'])
        n_classes = sum(len(r['classes']) for r in rows)
        self.stdout.write(self.style.SUCCESS(
            f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} "
            f"({len(rows)} bridges · {n_classes} learning-loop classes · "
            f"{n_with_doc}/{len(rows)} modules with docstrings)"
        ))

    # ----------------------------------------------------------- inspect

    def _inspect(self, path: Path) -> dict:
        rel = str(path.relative_to(REPO_ROOT))
        info = {
            'name': path.stem,  # e.g. agent_execution_bridge
            'pretty_name': self._pretty(path.stem),
            'module_path': rel,
            'module_docstring': '',
            'classes': [],
            'signal_registration_lines': [],
        }
        try:
            tree = ast.parse(path.read_text(errors='ignore'))
        except SyntaxError:
            return info
        info['module_docstring'] = ast.get_docstring(tree) or ''
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            # Skip Django models if present.
            base_text = ' '.join(
                ast.unparse(b) if hasattr(ast, 'unparse') else ''
                for b in node.bases
            )
            if 'models.Model' in base_text:
                continue
            doc = ast.get_docstring(node) or ''
            info['classes'].append({
                'name': node.name,
                'line': node.lineno,
                'docstring': doc,
                'docstring_first_line': _first_meaningful_line(doc),
                'methods': [
                    m.name for m in node.body
                    if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and not m.name.startswith('_')
                ],
            })

        # Capture "signal registered" log lines so the audit shows which
        # bridges have explicit registration confirmation.
        src = path.read_text(errors='ignore')
        for i, line in enumerate(src.splitlines(), start=1):
            if 'signal registered' in line.lower() or 'signal_registered' in line.lower():
                info['signal_registration_lines'].append((i, line.strip()))

        return info

    def _pretty(self, slug: str) -> str:
        return ' '.join(part.capitalize() for part in slug.split('_'))

    # ---------------------------------------------------------- findings

    def _collect_findings(self, rows: list[dict]) -> list[str]:
        findings: list[str] = []

        no_doc = [r['name'] for r in rows if not r['module_docstring']]
        if no_doc:
            findings.append(
                f"Bridge modules with no module docstring: "
                f"`{', '.join(no_doc)}`. The audit uses the module "
                f"docstring as the bridge's high-level purpose."
            )

        no_classes = [r['name'] for r in rows if not r['classes']]
        if no_classes:
            findings.append(
                f"Bridge files with no learning-loop class detected: "
                f"`{', '.join(no_classes)}`. Verify the file isn't an empty "
                f"stub or that the class doesn't follow the expected naming."
            )

        no_class_doc = [
            f"{r['name']}::{c['name']}"
            for r in rows for c in r['classes']
            if not c['docstring']
        ]
        if no_class_doc:
            findings.append(
                f"Learning-loop classes without a docstring: "
                f"`{', '.join(no_class_doc)}`. Per-class docstring is what "
                f"shows up in the bridge audit's class table."
            )

        # Naming-consistency observation (not a bug per se).
        loops = sum(
            1 for r in rows for c in r['classes']
            if c['name'].endswith('LearningLoop')
        )
        bridges = sum(
            1 for r in rows for c in r['classes']
            if c['name'].endswith('LearningBridge')
        )
        if loops and bridges:
            findings.append(
                f"Naming inconsistency: {loops} classes end in `LearningLoop`, "
                f"{bridges} end in `LearningBridge`. Same concept, different "
                f"suffix. Pick one in a future cleanup pass."
            )

        return findings

    # ------------------------------------------------------------ render

    def _render(self, rows: list[dict], *, findings: list[str]) -> str:
        n_total = len(rows)
        n_classes = sum(len(r['classes']) for r in rows)
        n_with_doc = sum(1 for r in rows if r['module_docstring'])

        out: list[str] = []
        out.append(
            '<!-- DOC-AUTOGEN: regenerated by '
            '`python manage.py build_learning_bridge_audit`. Do not hand-edit. -->'
        )
        out.append('')
        out.append('# Capability Audit — Learning Bridges')
        out.append('')
        out.append(
            "**Source of truth:** every `*_bridge.py` file under "
            "`core/learning_bridges/`. Each file is a Django-signal-driven "
            "shim that feeds runtime events into the unified learning "
            "pipeline. Bridges self-register at app startup via "
            "`core/learning_bridges/apps.py` (hooked from `core/apps.py:35`)."
        )
        out.append('')
        out.append('## Headline')
        out.append('')
        out.append(f'- **Bridge modules:** {n_total}')
        out.append(f'- **Learning-loop classes:** {n_classes}')
        out.append(
            f'- **Modules with docstrings:** {n_with_doc} / {n_total}'
        )
        out.append('')
        out.append(
            "> Each bridge listens for a specific runtime event (agent "
            "executed, application submitted, advisor consulted, etc.) and "
            "transforms it into a learning-pipeline record. They are "
            "side-effect-only — they don't return values, they emit "
            "training signal."
        )
        out.append('')

        if findings:
            out.append('## Findings')
            out.append('')
            for f in findings:
                out.append(f'- {f}')
            out.append('')

        # Bridges overview
        out.append('## Bridges overview')
        out.append('')
        out.append('| Bridge | Module | Classes | Summary |')
        out.append('|---|---|:-:|---|')
        for r in rows:
            summary = (
                _first_paragraph_short(r['module_docstring'])
                or (r['classes'][0]['docstring_first_line'] if r['classes'] else '')
                or '_(no docstring)_'
            ).replace('|', '\\|')
            if len(summary) > 100:
                summary = summary[:97] + '…'
            out.append(
                f'| `{r["name"]}` | `{r["module_path"]}` | '
                f'{len(r["classes"])} | {summary} |'
            )
        out.append('')

        # Detail appendix
        out.append('## Detail appendix')
        out.append('')
        out.append(
            "One block per bridge. Module docstring (first paragraph) "
            "is the high-level purpose; each contained class is a separate "
            "learning loop."
        )
        out.append('')
        for r in rows:
            out.append(f'### `{r["name"]}` — {r["pretty_name"]}')
            out.append('')
            out.append(f'**Module:** `{r["module_path"]}`')
            out.append('')
            if r['module_docstring']:
                out.append(_first_paragraph(r['module_docstring']))
                out.append('')
            else:
                out.append('_(no module docstring)_')
                out.append('')
            for c in r['classes']:
                out.append(
                    f'**Class `{c["name"]}` (line {c["line"]}):**'
                )
                out.append('')
                if c['docstring']:
                    out.append(_first_paragraph(c['docstring']))
                else:
                    out.append('_(no class docstring)_')
                out.append('')
                if c['methods']:
                    public = ', '.join(f'`{m}`' for m in c['methods'][:10])
                    if len(c['methods']) > 10:
                        public += f' (+ {len(c["methods"]) - 10} more)'
                    out.append(f'_Public methods: {public}_')
                    out.append('')
            if r['signal_registration_lines']:
                out.append('**Signal registration log lines:**')
                out.append('')
                for line_no, text in r['signal_registration_lines']:
                    # Truncate text for readability
                    txt = text if len(text) <= 110 else text[:107] + '…'
                    out.append(f'- L{line_no}: `{txt}`')
                out.append('')

        return '\n'.join(out) + '\n'


# helpers

def _first_meaningful_line(doc: str) -> str:
    for line in doc.splitlines():
        s = line.strip()
        if s:
            return s
    return ''


def _first_paragraph(doc: str) -> str:
    import textwrap
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
    paragraph = ' '.join(line.strip() for line in lines).strip()
    return textwrap.fill(paragraph, width=88) if paragraph else ''


def _first_paragraph_short(doc: str) -> str:
    """Like _first_paragraph but a single line, no wrap."""
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
