"""Generate ``docs/ML_AUDIT.md`` — the federated ML capability map.

Built in Session 1115, ninth and final subsystem audit. Unlike agents /
spiders / PA tools / advisors, ML doesn't have a single registry — it's a
federation of capability subdirectories under ``ml/`` (anomaly_detection,
graph_neural_network, reinforcement_learning, time_series, training,
auto_selection, automation, integrations, core). Each subdir contains
1–N implementation classes.

Strategy: enumerate the subdirs, AST-parse each ``*.py`` to find primary
classes (those whose name doesn't end in ``Config``/``Prediction``/
``Profile`` — those are usually dataclass shapes, not the engine itself),
pull the docstring and key methods. Plus top-level ``ml/models.py``
(Django models) and ``ml/tasks.py`` (Celery tasks) get their own
sections.

The audit doesn't try to enumerate every Django model — that's the
agent-side count already audited by the broader 570-models claim. It
focuses on the runtime ML capability surface.

Run::

    python manage.py build_ml_audit
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand


REPO_ROOT = Path(__file__).resolve().parents[3]
ML_DIR = REPO_ROOT / 'ml'
OUTPUT_PATH = REPO_ROOT / 'docs' / 'ML_AUDIT.md'

# Subdirs that hold actual capability implementations. Skipped:
# __pycache__, migrations, logs, management, data (data fixtures).
CAPABILITY_DIRS = [
    'core',
    'anomaly_detection',
    'auto_selection',
    'automation',
    'graph_neural_network',
    'integrations',
    'reinforcement_learning',
    'time_series',
    'training',
]


class Command(BaseCommand):
    help = "Regenerate docs/ML_AUDIT.md from ml/ subdirectory introspection."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--check', action='store_true',
            help='Print the would-be file to stdout instead of writing.',
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        if not ML_DIR.exists():
            self.stderr.write(f"ml/ directory not found at {ML_DIR}")
            return

        capabilities: list[dict] = []
        for slug in CAPABILITY_DIRS:
            cap_dir = ML_DIR / slug
            if not cap_dir.exists():
                continue
            capabilities.append(self._inspect_capability(slug, cap_dir))

        # Top-level files
        toplevel_models = self._inspect_file(ML_DIR / 'models.py', label='Django models')
        toplevel_tasks = self._inspect_file(ML_DIR / 'tasks.py', label='Celery tasks')

        findings = self._collect_findings(
            capabilities,
            toplevel_models=toplevel_models,
            toplevel_tasks=toplevel_tasks,
        )
        rendered = self._render(
            capabilities,
            toplevel_models=toplevel_models,
            toplevel_tasks=toplevel_tasks,
            findings=findings,
        )

        if opts['check']:
            self.stdout.write(rendered)
            return

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(rendered)
        n_classes = sum(len(c['primary_classes']) for c in capabilities)
        n_with_doc = sum(
            1 for c in capabilities for cl in c['primary_classes']
            if cl['docstring']
        )
        self.stdout.write(self.style.SUCCESS(
            f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} "
            f"({len(capabilities)} capabilities · {n_classes} primary classes "
            f"· {n_with_doc} with docstrings)"
        ))

    # ----------------------------------------------------------- inspect

    def _inspect_capability(self, slug: str, cap_dir: Path) -> dict:
        primary_classes: list[dict] = []
        for path in sorted(cap_dir.glob('*.py')):
            if path.name == '__init__.py':
                continue
            try:
                tree = ast.parse(path.read_text(errors='ignore'))
            except SyntaxError:
                continue
            for node in tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue
                # Filter out Django models + dataclass-shape classes
                if self._looks_like_django_model(node):
                    continue
                if self._looks_like_dataclass_shape(node):
                    continue
                primary_classes.append({
                    'name': node.name,
                    'file': str(path.relative_to(REPO_ROOT)),
                    'line': node.lineno,
                    'docstring': ast.get_docstring(node) or '',
                    'docstring_first_line': _first_meaningful_line(
                        ast.get_docstring(node) or ''
                    ),
                    'methods': [
                        m.name for m in node.body
                        if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and not m.name.startswith('_')
                    ],
                })
        primary_classes.sort(key=lambda c: c['name'])
        return {
            'slug': slug,
            'pretty': self._pretty(slug),
            'dir': str(cap_dir.relative_to(REPO_ROOT)),
            'primary_classes': primary_classes,
            'file_count': sum(
                1 for _ in cap_dir.glob('*.py') if _.name != '__init__.py'
            ),
        }

    def _inspect_file(self, path: Path, *, label: str) -> dict:
        info = {
            'path': str(path.relative_to(REPO_ROOT)),
            'label': label,
            'exists': path.exists(),
            'classes': [],
            'task_functions': [],
        }
        if not path.exists():
            return info
        try:
            tree = ast.parse(path.read_text(errors='ignore'))
        except SyntaxError:
            return info
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                info['classes'].append({
                    'name': node.name,
                    'line': node.lineno,
                    'docstring_first_line': _first_meaningful_line(
                        ast.get_docstring(node) or ''
                    ),
                })
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Heuristic: shared_task / app.task / task decorator
                for dec in node.decorator_list:
                    text = ast.unparse(dec) if hasattr(ast, 'unparse') else ''
                    if 'shared_task' in text or '.task' in text:
                        info['task_functions'].append({
                            'name': node.name,
                            'line': node.lineno,
                            'docstring_first_line': _first_meaningful_line(
                                ast.get_docstring(node) or ''
                            ),
                        })
                        break
        return info

    def _looks_like_django_model(self, cls: ast.ClassDef) -> bool:
        for base in cls.bases:
            text = ast.unparse(base) if hasattr(ast, 'unparse') else ''
            if 'models.Model' in text:
                return True
        return False

    def _looks_like_dataclass_shape(self, cls: ast.ClassDef) -> bool:
        # Classes named Config/Prediction/Profile/Result/Stats/Sample are
        # generally lightweight shape holders. Skip those from the
        # "primary class" list; they show up in detail if needed but
        # they're not the audit's interesting surface.
        suffixes = ('Config', 'Prediction', 'Profile', 'Result', 'Stats', 'Sample')
        for suffix in suffixes:
            if cls.name.endswith(suffix):
                # Allow if it has a heavy docstring (>2 lines) — that's
                # a genuine class even though it has the suffix.
                doc = ast.get_docstring(cls) or ''
                if len(doc.splitlines()) > 3:
                    return False
                return True
        return False

    def _pretty(self, slug: str) -> str:
        return ' '.join(part.capitalize() for part in slug.split('_'))

    # ---------------------------------------------------------- findings

    def _collect_findings(
        self, capabilities: list[dict], *, toplevel_models: dict, toplevel_tasks: dict
    ) -> list[str]:
        findings: list[str] = []

        # Capabilities with no primary class (might mean we filtered too
        # aggressively, or the subdir is hollow).
        empty = [c['slug'] for c in capabilities if not c['primary_classes']]
        if empty:
            findings.append(
                f"ML capabilities with no primary class detected: "
                f"`{', '.join(empty)}`. Either the subdir is empty or all "
                f"its classes look like dataclass shapes — worth a manual "
                f"glance to confirm."
            )

        no_doc = [
            f"{c['slug']}::{cls['name']}"
            for c in capabilities for cls in c['primary_classes']
            if not cls['docstring']
        ]
        if no_doc:
            findings.append(
                f"ML primary classes with no docstring: "
                f"`{', '.join(no_doc)}`. Audit relies on docstrings to "
                f"describe what each class is."
            )

        if toplevel_tasks['exists'] and toplevel_tasks['task_functions']:
            # Cross-reference with the broken beat refs from BEAT_AUDIT.md
            findings.append(
                f"`ml/tasks.py` defines "
                f"{len(toplevel_tasks['task_functions'])} `@shared_task` "
                f"functions. **`cleanup_old_model_files` is in the broken "
                f"beat refs list** (see `docs/BEAT_AUDIT.md` finding 3 + "
                f"`docs/AUDIT_FINDINGS.md` entry 3) — Celery autodiscover "
                f"doesn't pick up `ml.tasks` at worker startup. Same fix "
                f"as the others: add `'ml.tasks'` to `app.conf.imports` "
                f"in `core/celery.py:317`."
            )

        return findings

    # ------------------------------------------------------------ render

    def _render(
        self,
        capabilities: list[dict],
        *,
        toplevel_models: dict,
        toplevel_tasks: dict,
        findings: list[str],
    ) -> str:
        n_caps = len(capabilities)
        n_classes = sum(len(c['primary_classes']) for c in capabilities)
        n_with_doc = sum(
            1 for c in capabilities for cl in c['primary_classes']
            if cl['docstring']
        )

        out: list[str] = []
        out.append(
            '<!-- DOC-AUTOGEN: regenerated by '
            '`python manage.py build_ml_audit`. Do not hand-edit. -->'
        )
        out.append('')
        out.append('# Capability Audit — ML Pipelines')
        out.append('')
        out.append(
            "**Source of truth:** the `ml/` Django app, federated across "
            "capability subdirectories (no single registry, unlike agents / "
            "spiders / PA tools). Each subdirectory under `ml/<capability>/` "
            "implements one ML approach (anomaly detection, GNN, RL, time "
            "series, training, etc.). AST-parsed; dataclass-shape classes "
            "(suffixes `Config`/`Prediction`/`Profile`/`Result`/`Stats`/"
            "`Sample` with short docstrings) are filtered out so the audit "
            "focuses on engine classes."
        )
        out.append('')
        out.append('## Headline')
        out.append('')
        out.append(f'- **Capability subdirectories:** {n_caps}')
        out.append(f'- **Primary engine/pipeline classes:** {n_classes}')
        out.append(
            f'- **Classes with docstrings:** {n_with_doc} / {n_classes}'
        )
        if toplevel_models['exists']:
            out.append(
                f'- **Top-level `ml/models.py`:** '
                f'{len(toplevel_models["classes"])} Django model class(es).'
            )
        if toplevel_tasks['exists']:
            out.append(
                f'- **Top-level `ml/tasks.py`:** '
                f'{len(toplevel_tasks["task_functions"])} Celery task(s).'
            )
        out.append('')
        out.append(
            "> ML is the most federated subsystem. Unlike `AGENT_MAP` or "
            "`PA_TOOL_SCHEMAS`, there's no single registry to introspect. "
            "Each capability lives in its own subdirectory; this audit "
            "walks them and pulls the primary engine class out of each."
        )
        out.append('')

        if findings:
            out.append('## Findings')
            out.append('')
            for f in findings:
                out.append(f'- {f}')
            out.append('')

        # Capability overview
        out.append('## Capabilities overview')
        out.append('')
        out.append('| Capability | Directory | Files | Primary classes |')
        out.append('|---|---|---:|---|')
        for c in capabilities:
            class_list = ', '.join(f'`{cl["name"]}`' for cl in c['primary_classes'])
            if not class_list:
                class_list = '_(none detected)_'
            elif len(class_list) > 80:
                class_list = class_list[:77] + '…'
            out.append(
                f'| **{c["pretty"]}** | `{c["dir"]}/` | {c["file_count"]} | {class_list} |'
            )
        out.append('')

        # Top-level models + tasks
        if toplevel_models['exists']:
            out.append('## `ml/models.py` — Django models')
            out.append('')
            if not toplevel_models['classes']:
                out.append('_(no models detected)_')
            else:
                out.append('| Class | Line | Description |')
                out.append('|---|---:|---|')
                for c in toplevel_models['classes']:
                    desc = c['docstring_first_line'] or '_(no docstring)_'
                    desc = desc.replace('|', '\\|')
                    if len(desc) > 90:
                        desc = desc[:87] + '…'
                    out.append(f'| `{c["name"]}` | {c["line"]} | {desc} |')
            out.append('')

        if toplevel_tasks['exists']:
            out.append('## `ml/tasks.py` — Celery tasks')
            out.append('')
            if not toplevel_tasks['task_functions']:
                out.append('_(no @shared_task functions detected)_')
            else:
                out.append('| Task | Line | Description |')
                out.append('|---|---:|---|')
                for t in toplevel_tasks['task_functions']:
                    desc = t['docstring_first_line'] or '_(no docstring)_'
                    desc = desc.replace('|', '\\|')
                    if len(desc) > 90:
                        desc = desc[:87] + '…'
                    out.append(f'| `{t["name"]}` | {t["line"]} | {desc} |')
            out.append('')

        # Per-capability detail
        out.append('## Detail appendix')
        out.append('')
        out.append(
            "One section per capability with each primary class's docstring "
            "and a short list of public methods so the reader can answer "
            "'what does this engine actually expose'."
        )
        out.append('')
        for c in capabilities:
            out.append(f'### {c["pretty"]} — `{c["dir"]}/`')
            out.append('')
            if not c['primary_classes']:
                out.append('_(no primary classes detected — either empty subdir or filtered out as dataclass shapes)_')
                out.append('')
                continue
            for cls in c['primary_classes']:
                out.append(f'#### `{cls["name"]}` ([line {cls["line"]}](../{cls["file"]}))')
                out.append('')
                if cls['docstring']:
                    out.append(_first_paragraph(cls['docstring']))
                else:
                    out.append('_(no docstring)_')
                out.append('')
                if cls['methods']:
                    public = ', '.join(f'`{m}`' for m in cls['methods'][:10])
                    if len(cls['methods']) > 10:
                        public += f' (+ {len(cls["methods"]) - 10} more)'
                    out.append(f'_Public methods: {public}_')
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
