"""Generate ``docs/BODY_SYSTEM_AUDIT.md`` — what each of the 9 body systems monitors.

Built in Session 1115, seventh subsystem audit. The "body systems" are
9 named services in ``core/services/`` (heart, lungs, brain, spine,
immune, digestive, muscular, circulatory, skin), each exposing a
singleton getter and a ``get_vitals()``-style method. Plus the
``BodyCoordinator`` (``core/services/body_coordinator.py``) which is the
autonomic-reflex layer that consumes those vitals.

The canonical list of the 9 lives in ``core/tasks.py::run_all_systems_scan``
as the literal ``body_systems = [...]`` list. We use that list as the
source of truth for "which systems are monitored," then introspect each
service module for its class docstring + accessor.

AST-parsed (no module imports) so we never accidentally trigger a Heart
beat or a real DB call during audit generation.

Run::

    python manage.py build_body_system_audit
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand


REPO_ROOT = Path(__file__).resolve().parents[3]
CORE_TASKS = REPO_ROOT / 'core' / 'tasks.py'
SERVICES_DIR = REPO_ROOT / 'core' / 'services'
BODY_COORDINATOR = SERVICES_DIR / 'body_coordinator.py'
OUTPUT_PATH = REPO_ROOT / 'docs' / 'BODY_SYSTEM_AUDIT.md'


class Command(BaseCommand):
    help = "Regenerate docs/BODY_SYSTEM_AUDIT.md from body system service introspection."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--check', action='store_true',
            help='Print the would-be file to stdout instead of writing.',
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        systems = self._discover_canonical_list()
        rows: list[dict] = [self._inspect_system(name) for name in systems]
        coordinator = self._inspect_coordinator()
        findings = self._collect_findings(rows, coordinator=coordinator)
        rendered = self._render(rows, coordinator=coordinator, findings=findings)

        if opts['check']:
            self.stdout.write(rendered)
            return

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(rendered)
        ok = sum(1 for r in rows if r['module_exists'] and r['class_docstring'])
        self.stdout.write(self.style.SUCCESS(
            f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} "
            f"({len(rows)} systems · {ok} with class docstrings · "
            f"coordinator={'✓' if coordinator['exists'] else '✗'})"
        ))

    # ----------------------------------------------------------- discover

    def _discover_canonical_list(self) -> list[str]:
        """Pull the `body_systems = [...]` literal from `run_all_systems_scan`."""
        src = CORE_TASKS.read_text(errors='ignore')
        m = re.search(r"body_systems\s*=\s*\[([^\]]+)\]", src)
        if not m:
            return []
        names = re.findall(r"'([^']+)'", m.group(1))
        return names

    # ------------------------------------------------------------ inspect

    def _inspect_system(self, name: str) -> dict:
        path = SERVICES_DIR / f'{name}.py'
        info = {
            'name': name,
            'module_path': f'core/services/{name}.py',
            'module_exists': path.exists(),
            'service_class': '',
            'class_line': 0,
            'class_docstring': '',
            'class_first_line': '',
            'accessor': '',
            'has_get_vitals': False,
            'components': [],
        }
        if not path.exists():
            return info
        try:
            tree = ast.parse(path.read_text(errors='ignore'))
        except SyntaxError:
            return info

        # First class whose name ends with "Service" or "Monitor" or "Coordinator".
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if (
                node.name.endswith('Service')
                or node.name.endswith('Monitor')
                or node.name.endswith('Coordinator')
                or node.name.endswith('System')
            ):
                info['service_class'] = node.name
                info['class_line'] = node.lineno
                doc = ast.get_docstring(node) or ''
                info['class_docstring'] = doc
                info['class_first_line'] = _first_meaningful_line(doc)
                # get_vitals presence
                for stmt in node.body:
                    if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if stmt.name == 'get_vitals':
                            info['has_get_vitals'] = True
                    # COMPONENTS class attribute
                    if (
                        isinstance(stmt, ast.Assign)
                        and any(
                            isinstance(t, ast.Name) and t.id == 'COMPONENTS'
                            for t in stmt.targets
                        )
                        and isinstance(stmt.value, ast.Dict)
                    ):
                        info['components'] = [
                            _const_str(k) for k in stmt.value.keys
                            if _const_str(k)
                        ]
                break

        # Module-level accessor: `def get_<name>_<something>(...)`.
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith('get_') and (
                    name in node.name or 'monitor' in node.name or 'service' in node.name
                ):
                    info['accessor'] = node.name
                    break

        return info

    def _inspect_coordinator(self) -> dict:
        info = {'exists': BODY_COORDINATOR.exists(), 'docstring': '', 'class_name': '', 'line': 0}
        if not info['exists']:
            return info
        try:
            tree = ast.parse(BODY_COORDINATOR.read_text(errors='ignore'))
        except SyntaxError:
            return info
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == 'BodyCoordinator':
                info['class_name'] = node.name
                info['line'] = node.lineno
                info['docstring'] = _first_paragraph(ast.get_docstring(node) or '')
                break
        return info

    # ---------------------------------------------------------- findings

    def _collect_findings(self, rows: list[dict], *, coordinator: dict) -> list[str]:
        findings: list[str] = []

        missing = [r['name'] for r in rows if not r['module_exists']]
        if missing:
            findings.append(
                f"Body systems listed in `run_all_systems_scan` but with no "
                f"service module in `core/services/`: "
                f"`{', '.join(missing)}`. Either dead-name or missing service."
            )

        no_doc = [
            r['name'] for r in rows
            if r['module_exists'] and not r['class_docstring']
        ]
        if no_doc:
            findings.append(
                f"Body systems whose primary class has no docstring: "
                f"`{', '.join(no_doc)}`. The audit relies on the class "
                f"docstring as the 'what this system monitors' description."
            )

        no_vitals = [
            r['name'] for r in rows
            if r['module_exists'] and not r['has_get_vitals']
        ]
        if no_vitals:
            findings.append(
                f"Body systems whose primary class doesn't expose "
                f"`get_vitals()`: `{', '.join(no_vitals)}`. "
                f"`run_all_systems_scan` calls `service.get_vitals()` on most "
                f"systems — anything without it has to be special-cased in "
                f"the scan loop."
            )

        if not coordinator['exists']:
            findings.append(
                "`BodyCoordinator` service is missing — expected at "
                "`core/services/body_coordinator.py`."
            )

        return findings

    # ------------------------------------------------------------ render

    def _render(self, rows: list[dict], *, coordinator: dict, findings: list[str]) -> str:
        n_total = len(rows)
        n_ok = sum(
            1 for r in rows
            if r['module_exists'] and r['class_docstring'] and r['has_get_vitals']
        )

        out: list[str] = []
        out.append(
            '<!-- DOC-AUTOGEN: regenerated by '
            '`python manage.py build_body_system_audit`. Do not hand-edit. -->'
        )
        out.append('')
        out.append('# Capability Audit — Body Systems')
        out.append('')
        out.append(
            "**Source of truth:** the literal `body_systems = [...]` list "
            "in `core/tasks.py::run_all_systems_scan` enumerates which "
            "systems get monitored each scan cycle. Each name maps to a "
            "service module under `core/services/<name>.py`."
        )
        out.append('')
        out.append('## Headline')
        out.append('')
        out.append(f'- **Body systems monitored:** {n_total}')
        out.append(
            f'- **Fully wired** (module exists + class docstring + '
            f'`get_vitals()` method): {n_ok} / {n_total}'
        )
        if coordinator['exists']:
            out.append(
                f'- **BodyCoordinator:** present at '
                f'`core/services/body_coordinator.py:{coordinator["line"]}` — '
                f'autonomic-reflex layer consuming the vitals.'
            )
        else:
            out.append(f'- **BodyCoordinator:** ✗ missing')
        out.append('')
        out.append(
            "> The body-system metaphor comes from Session 701+ (HEART) "
            "onward. Each system is a singleton service that exposes a "
            "`get_vitals()` method returning a dict of health metrics. "
            "`run_all_systems_scan` (a daily Celery task) calls each one, "
            "aggregates the results, and feeds them to `BodyCoordinator` "
            "for cross-system reflex logic."
        )
        out.append('')

        if findings:
            out.append('## Findings')
            out.append('')
            for f in findings:
                out.append(f'- {f}')
            out.append('')

        # Overview table
        out.append('## Systems overview')
        out.append('')
        out.append('| System | Module | Class | get_vitals() | Accessor | Description |')
        out.append('|---|---|---|:-:|---|---|')
        for r in rows:
            summary = r['class_first_line'] or '_(no docstring)_'
            summary = summary.replace('|', '\\|')
            if len(summary) > 80:
                summary = summary[:77] + '…'
            module_cell = (
                f'`{r["module_path"]}:{r["class_line"]}`'
                if r['class_line']
                else f'`{r["module_path"]}`'
            )
            if not r['module_exists']:
                module_cell = '✗ missing'
            vitals = '✓' if r['has_get_vitals'] else '✗'
            accessor = f'`{r["accessor"]}()`' if r['accessor'] else '—'
            cls = f'`{r["service_class"]}`' if r['service_class'] else '—'
            out.append(
                f'| `{r["name"]}` | {module_cell} | {cls} | {vitals} | {accessor} | {summary} |'
            )
        out.append('')

        # BodyCoordinator block
        if coordinator['exists']:
            out.append('## BodyCoordinator')
            out.append('')
            out.append(
                f'**Class:** `{coordinator["class_name"]}` · '
                f'**Location:** `core/services/body_coordinator.py:{coordinator["line"]}`'
            )
            out.append('')
            if coordinator['docstring']:
                out.append(coordinator['docstring'])
                out.append('')
            else:
                out.append('_(no class docstring)_')
                out.append('')

        # Per-system detail appendix
        out.append('## Detail appendix')
        out.append('')
        out.append(
            'One block per body system. Class docstring (first paragraph) '
            'is the canonical "what does this system monitor" description. '
            '`COMPONENTS` are the named subsystems the service tracks '
            'internally (where defined).'
        )
        out.append('')
        for r in rows:
            out.append(f'### `{r["name"]}`')
            out.append('')
            if not r['module_exists']:
                out.append(f'_(no module at `{r["module_path"]}`)_')
                out.append('')
                continue
            out.append(
                f'**Class:** `{r["service_class"]}` · '
                f'**Location:** `{r["module_path"]}:{r["class_line"]}` · '
                + (f'**Accessor:** `{r["accessor"]}()`' if r['accessor'] else '**No accessor found**')
                + (' · **`get_vitals()` ✓**' if r['has_get_vitals'] else ' · **no `get_vitals()`**')
            )
            out.append('')
            if r['class_docstring']:
                out.append(_first_paragraph(r['class_docstring']))
            else:
                out.append('_(no class docstring)_')
            out.append('')
            if r['components']:
                out.append('**Components tracked internally:**')
                out.append('')
                for c in r['components']:
                    out.append(f'- `{c}`')
                out.append('')

        return '\n'.join(out) + '\n'


# helpers

def _const_str(node: ast.AST) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return ''


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
