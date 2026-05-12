"""Generate ``docs/SPIDER_AUDIT.md`` from live spider registry.

Built in Session 1115, sibling to ``build_capability_audit`` (agents). Code
is the source of truth — this command introspects every entry in
``SpiderRegistry`` (the singleton at ``ai_core.spiders.spider_registry``),
pulls the class docstring + registered config (category, priority, targets,
placeholder flag) directly from the registry, and writes a deterministic
markdown doc with a ``<!-- DOC-AUTOGEN -->`` header.

Run::

    python manage.py build_spider_audit

To regenerate after touching ``ai_core/spiders/``. Doesn't need DB.

Output structure mirrors ``CAPABILITY_AUDIT.md``: a headline block, a
findings section that surfaces real problems caught by the introspection,
overview tables grouped by category, and a per-spider detail appendix with
the class docstring (first paragraph) and full target list.
"""
from __future__ import annotations

import inspect
import textwrap
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_PATH = REPO_ROOT / 'docs' / 'SPIDER_AUDIT.md'


class Command(BaseCommand):
    help = 'Regenerate docs/SPIDER_AUDIT.md from spider registry introspection.'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--check',
            action='store_true',
            help='Print the would-be file to stdout instead of writing.',
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        from ai_core.spiders.spider_registry import get_spider_registry
        reg = get_spider_registry()
        spider_classes = reg.spider_classes
        spider_configs = reg.spider_configs

        rows: list[dict] = []
        for name in sorted(spider_classes.keys()):
            cls = spider_classes[name]
            cfg = spider_configs.get(name, {}) or {}
            rows.append(self._inspect(name, cls, cfg))

        findings = self._collect_findings(rows)
        rendered = self._render(rows, findings=findings)

        if opts['check']:
            self.stdout.write(rendered)
            return

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(rendered)
        n_with_doc = sum(1 for r in rows if r['has_docstring'])
        n_placeholder = sum(1 for r in rows if r['placeholder'])
        self.stdout.write(self.style.SUCCESS(
            f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} "
            f"({len(rows)} spider entries, {n_with_doc} with docstrings, "
            f"{n_placeholder} placeholder)"
        ))

    # ------------------------------------------------------------- inspect

    def _inspect(self, name: str, cls: type, cfg: dict) -> dict:
        # File + line of the bound class.
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

        doc = inspect.getdoc(cls) or ''
        has_docstring = bool(doc.strip())
        first_line = _first_meaningful_line(doc)

        targets = cfg.get('targets') or []
        category = cfg.get('category', 'unknown')
        priority = cfg.get('priority', 5)
        rate_limit = cfg.get('rate_limit')
        placeholder = bool(cfg.get('placeholder', False))
        requires_auth = bool(cfg.get('requires_auth', False))
        description_cfg = cfg.get('description', '')

        return {
            'name': name,
            'class_name': cls.__name__,
            'file': str(rel_path) if rel_path else '(unknown)',
            'line': line_no,
            'has_docstring': has_docstring,
            'docstring_first_line': first_line,
            'docstring_full': doc,
            'category': category,
            'priority': priority,
            'rate_limit': rate_limit,
            'placeholder': placeholder,
            'requires_auth': requires_auth,
            'targets': [str(t) for t in targets],
            'target_count': len(targets) if isinstance(targets, list) else 0,
            'description_cfg': description_cfg,
        }

    # ------------------------------------------------------------ findings

    def _collect_findings(self, rows: list[dict]) -> list[str]:
        findings: list[str] = []

        # Spider names that share a class — fine if intentional, suspicious if not.
        by_class: dict[str, list[str]] = {}
        for r in rows:
            by_class.setdefault(r['class_name'], []).append(r['name'])
        shared = {k: v for k, v in by_class.items() if len(v) > 1}
        if shared:
            lines = [
                f"`{cls}` is shared by `{', '.join(sorted(names))}`"
                for cls, names in sorted(shared.items())
            ]
            findings.append(
                "Multiple registry names bound to the same spider class — fine "
                "if these are intentional aliases/variants, but worth a glance: "
                + "; ".join(lines)
            )

        placeholders = [r['name'] for r in rows if r['placeholder']]
        if placeholders:
            findings.append(
                f"Spiders marked `placeholder=True` (registered but the class "
                f"hasn't been wired): `{', '.join(placeholders)}`. These count "
                f"toward the 80 spider total but don't fetch anything live."
            )

        no_targets = [r['name'] for r in rows if not r['targets']]
        if no_targets:
            findings.append(
                f"Spiders with no `targets` in registry config "
                f"(`{', '.join(no_targets)}`) — either intentional (dynamic "
                f"target discovery) or a broken registration."
            )

        no_doc = [r['name'] for r in rows if not r['has_docstring']]
        if no_doc:
            findings.append(
                f"Spider classes without a docstring: `{', '.join(no_doc)}`. "
                f"The capability audit relies on docstrings to describe what "
                f"each spider fetches."
            )

        return findings

    # -------------------------------------------------------------- render

    def _render(self, rows: list[dict], *, findings: list[str]) -> str:
        total = len(rows)
        by_cat: dict[str, list[dict]] = {}
        for r in rows:
            by_cat.setdefault(r['category'], []).append(r)
        n_working = sum(1 for r in rows if not r['placeholder'])
        n_placeholder = total - n_working
        n_with_doc = sum(1 for r in rows if r['has_docstring'])
        n_categories = len(by_cat)
        total_targets = sum(r['target_count'] for r in rows)

        out: list[str] = []
        out.append(
            '<!-- DOC-AUTOGEN: regenerated by '
            '`python manage.py build_spider_audit`. Do not hand-edit. -->'
        )
        out.append('')
        out.append('# Capability Audit — Spiders')
        out.append('')
        out.append(
            '**Source of truth:** `ai_core.spiders.spider_registry.SpiderRegistry` '
            '(singleton at `get_spider_registry()`). Class docstrings + '
            'registry config (`category`, `priority`, `targets`, `placeholder`) '
            'introspected live.'
        )
        out.append('')
        out.append('## Headline')
        out.append('')
        out.append(f'- **Registered spider entries:** {total}')
        out.append(
            f'- **Working / placeholder:** {n_working} working · '
            f'{n_placeholder} placeholder'
        )
        out.append(f'- **Categories:** {n_categories} distinct')
        out.append(
            f'- **Docstring coverage:** {n_with_doc} / {total} '
            f'({_pct(n_with_doc, total)}%) spider classes have a class docstring'
        )
        out.append(f'- **Configured targets:** {total_targets} across all spiders')
        out.append('')
        out.append(
            '> Note: a "spider entry" is a registry `(name, class, config)` row. '
            'Multiple entries can share the same class — same crawler, different '
            'category / priority / targets. The registry total (80) and the '
            'physical spider class count are not the same number.'
        )
        out.append('')

        if findings:
            out.append('## Findings')
            out.append('')
            for f in findings:
                out.append(f'- {f}')
            out.append('')

        # Per-category overview
        out.append(f'## Per-category overview ({n_categories} categories)')
        out.append('')
        out.append('| Category | Spiders | Working | Placeholder |')
        out.append('|---|---:|---:|---:|')
        for cat, bucket in sorted(by_cat.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            n = len(bucket)
            working = sum(1 for r in bucket if not r['placeholder'])
            placeholder = n - working
            out.append(f'| `{cat}` | {n} | {working} | {placeholder} |')
        out.append('')

        # Per-spider tables grouped by category
        out.append('## Spider tables by category')
        out.append('')
        for cat, bucket in sorted(by_cat.items()):
            out.append(f'### `{cat}` ({len(bucket)})')
            out.append('')
            out.append('| Spider | Class | Targets | Priority | Status | Summary |')
            out.append('|---|---|:-:|:-:|:-:|---|')
            for r in sorted(bucket, key=lambda r: r['name']):
                summary = (
                    r['docstring_first_line']
                    or r['description_cfg']
                    or '_(no docstring or config description)_'
                ).replace('|', '\\|')
                if len(summary) > 100:
                    summary = summary[:97] + '…'
                file_link = (
                    f'`{r["file"]}:{r["line"]}`' if r['line']
                    else f'`{r["file"]}`'
                )
                status = 'placeholder' if r['placeholder'] else 'working'
                out.append(
                    f'| `{r["name"]}` | {file_link} | {r["target_count"]} | '
                    f'{r["priority"]} | {status} | {summary} |'
                )
            out.append('')

        # Detail appendix
        out.append('## Detail appendix')
        out.append('')
        out.append(
            'One block per registered spider, sorted alphabetically. The '
            'docstring text is exactly what `inspect.getdoc(cls)` returns. '
            'Targets are the registry-configured target list.'
        )
        out.append('')
        for r in sorted(rows, key=lambda r: r['name']):
            out.append(f'### `{r["name"]}` ({r["category"]})')
            out.append('')
            out.append(
                f'**Class:** `{r["class_name"]}` · '
                f'**Location:** `{r["file"]}:{r["line"]}` · '
                f'**Priority:** {r["priority"]}'
                + (f' · **Rate limit:** {r["rate_limit"]}/s' if r["rate_limit"] else '')
                + (' · **Auth required**' if r['requires_auth'] else '')
                + (' · **placeholder**' if r['placeholder'] else '')
            )
            out.append('')
            if r['has_docstring']:
                paragraph = _first_paragraph(r['docstring_full'])
                out.append(textwrap.fill(paragraph, width=88))
            elif r['description_cfg']:
                out.append(f'_(no class docstring; registry config description: {r["description_cfg"]})_')
            else:
                out.append('_(no class docstring or config description)_')
            out.append('')
            if r['targets']:
                out.append('**Targets:**')
                out.append('')
                for t in r['targets']:
                    out.append(f'- `{t}`')
                out.append('')
            else:
                out.append('**Targets:** _(none configured — dynamic discovery or stale registration)_')
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


def _pct(n: int, total: int) -> int:
    return int(round(100.0 * n / total)) if total else 0
