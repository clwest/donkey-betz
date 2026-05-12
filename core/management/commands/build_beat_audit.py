"""Generate ``docs/BEAT_AUDIT.md`` — the runtime-derived "what runs on a schedule".

Built in Session 1115, sibling to the agent / spider / PA audits. Walks the
static beat schedule (``app.conf.beat_schedule``) registered in
``core.celery``, and cross-references each entry against Celery's task
registry to flag broken references.

What it doesn't do: enumerate the live ``PeriodicTask`` rows in the DB.
That side is dynamic (operators can add ad-hoc rows via ``django-celery-beat``)
and the static schedule is the source of truth for what's intended to run.
The DB side is captured by the existing ``beat_schedule_count`` claim and
by ``platform_inventory.py`` (DB-required, surfaces as `skipped` without a
live database).

Run::

    python manage.py build_beat_audit
"""
from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_PATH = REPO_ROOT / 'docs' / 'BEAT_AUDIT.md'


class Command(BaseCommand):
    help = "Regenerate docs/BEAT_AUDIT.md from app.conf.beat_schedule introspection."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--check',
            action='store_true',
            help='Print the would-be file to stdout instead of writing.',
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        from core.celery import app as celery_app
        schedule = dict(celery_app.conf.beat_schedule or {})
        registered_tasks = set(celery_app.tasks.keys())

        rows: list[dict] = []
        for name in sorted(schedule.keys()):
            entry = schedule[name] or {}
            rows.append(self._inspect(name, entry, registered_tasks))

        findings = self._collect_findings(rows)
        rendered = self._render(
            rows,
            findings=findings,
            registered_task_count=sum(
                1 for t in registered_tasks if not t.startswith('celery.')
            ),
        )

        if opts['check']:
            self.stdout.write(rendered)
            return

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(rendered)
        n_broken = sum(1 for r in rows if not r['task_resolves'])
        self.stdout.write(self.style.SUCCESS(
            f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} "
            f"({len(rows)} static beat entries · {n_broken} broken task refs)"
        ))

    # ----------------------------------------------------------- inspect

    def _inspect(self, name: str, entry: dict, registered: set[str]) -> dict:
        task = entry.get('task', '') or ''
        schedule = entry.get('schedule')
        options = entry.get('options', {}) or {}
        queue = options.get('queue', '<default>')
        expires = options.get('expires')
        kwargs = entry.get('kwargs')

        # Cron readability
        schedule_str = _format_schedule(schedule)

        task_resolves = bool(task) and task in registered
        task_doc = ''
        task_file = ''
        task_line = 0
        if task_resolves:
            try:
                from core.celery import app as celery_app
                fn = celery_app.tasks[task].run
                task_doc = (inspect.getdoc(fn) or '').strip()
                task_file = inspect.getfile(fn)
                try:
                    task_file = str(Path(task_file).resolve().relative_to(REPO_ROOT))
                except ValueError:
                    pass
                try:
                    _, task_line = inspect.getsourcelines(fn)
                except (OSError, TypeError):
                    task_line = 0
            except (KeyError, TypeError, OSError):
                pass

        return {
            'name': name,
            'task': task,
            'task_resolves': task_resolves,
            'task_file': task_file,
            'task_line': task_line,
            'task_doc': task_doc,
            'task_doc_first_line': _first_meaningful_line(task_doc),
            'schedule': schedule,
            'schedule_str': schedule_str,
            'queue': queue,
            'expires': expires,
            'kwargs': kwargs,
        }

    # ---------------------------------------------------------- findings

    def _collect_findings(self, rows: list[dict]) -> list[str]:
        findings: list[str] = []

        broken = [(r['name'], r['task']) for r in rows if not r['task_resolves']]
        if broken:
            lines = ', '.join(f'`{n}` → `{t or "(no task)"}`' for n, t in broken)
            findings.append(
                "Beat entries whose `task` reference doesn't resolve in the "
                "Celery task registry — these will fail at dispatch time: "
                + lines
                + '.'
            )

        no_doc = [r['name'] for r in rows if r['task_resolves'] and not r['task_doc']]
        if no_doc:
            findings.append(
                f"Beat entries whose underlying task has no docstring — fine "
                f"for stable infrastructure tasks, worth annotating for "
                f"anything domain-specific: {len(no_doc)} entries "
                f"({', '.join(f'`{n}`' for n in no_doc[:6])}"
                + ('…' if len(no_doc) > 6 else '')
                + ')'
            )

        # Cluster by queue — pretty noisy if everything is on one worker.
        from collections import Counter
        queue_counts = Counter(r['queue'] for r in rows)
        biggest = queue_counts.most_common(1)
        if biggest and biggest[0][1] >= len(rows) * 0.5:
            findings.append(
                f"Single queue carries the majority of scheduled work: "
                f"`{biggest[0][0]}` runs {biggest[0][1]} of {len(rows)} "
                f"entries. If that worker drops, half the platform stops "
                f"ticking."
            )

        return findings

    # ------------------------------------------------------------ render

    def _render(
        self,
        rows: list[dict],
        *,
        findings: list[str],
        registered_task_count: int,
    ) -> str:
        n_total = len(rows)
        n_broken = sum(1 for r in rows if not r['task_resolves'])
        n_with_doc = sum(1 for r in rows if r['task_resolves'] and r['task_doc'])
        from collections import Counter
        by_queue = Counter(r['queue'] for r in rows)

        out: list[str] = []
        out.append(
            '<!-- DOC-AUTOGEN: regenerated by '
            '`python manage.py build_beat_audit`. Do not hand-edit. -->'
        )
        out.append('')
        out.append('# Capability Audit — Beat (Static Schedule)')
        out.append('')
        out.append(
            "**Source of truth:** `app.conf.beat_schedule` in `core/celery.py`. "
            "Each entry's task path is cross-referenced against Celery's task "
            "registry at runtime to catch broken references."
        )
        out.append('')
        out.append('## Headline')
        out.append('')
        out.append(f'- **Static beat entries:** {n_total}')
        out.append(
            f'- **Task refs resolve in Celery registry:** '
            f'{n_total - n_broken} / {n_total}'
            + (f' ({_pct(n_total - n_broken, n_total)}%)' if n_total else '')
        )
        out.append(
            f'- **Underlying tasks with docstrings:** {n_with_doc} / '
            f'{n_total - n_broken}'
        )
        out.append(
            f'- **Total user-defined Celery tasks (registry):** '
            f'{registered_task_count} — many run on demand, not on schedule.'
        )
        out.append('')
        out.append(
            "> What this audit doesn't cover: ad-hoc `PeriodicTask` rows in "
            "the DB (django-celery-beat). Operators can add those at runtime; "
            "the static schedule here is what the codebase intends. DB rows "
            "are tracked separately by the `db_required` claims that surface "
            "as `skipped` without a live Postgres."
        )
        out.append('')

        if findings:
            out.append('## Findings')
            out.append('')
            for f in findings:
                out.append(f'- {f}')
            out.append('')

        # Queue distribution
        out.append('## Queue distribution')
        out.append('')
        out.append('| Queue | Entries |')
        out.append('|---|---:|')
        for queue, n in by_queue.most_common():
            out.append(f'| `{queue}` | {n} |')
        out.append('')

        # Full schedule table
        out.append('## Schedule table')
        out.append('')
        out.append('| Name | Task | Schedule | Queue | Resolves |')
        out.append('|---|---|---|:-:|:-:|')
        for r in rows:
            task_cell = f'`{r["task"]}`'
            if r['task_file'] and r['task_line']:
                task_cell = (
                    f'`{r["task"]}` ([src]({r["task_file"]}#L{r["task_line"]}))'
                )
            resolves = '✓' if r['task_resolves'] else '✗'
            out.append(
                f'| `{r["name"]}` | {task_cell} | `{r["schedule_str"]}` | '
                f'`{r["queue"]}` | {resolves} |'
            )
        out.append('')

        # Detail appendix
        out.append('## Detail appendix')
        out.append('')
        out.append(
            'One block per beat entry. Underlying task docstring (first '
            'paragraph) is included when present so the audit explains what '
            'the schedule actually triggers.'
        )
        out.append('')
        for r in rows:
            out.append(f'### `{r["name"]}`')
            out.append('')
            out.append(
                f'**Task:** `{r["task"]}` · **Schedule:** `{r["schedule_str"]}` '
                f'· **Queue:** `{r["queue"]}`'
                + (f' · **Expires:** {r["expires"]}s' if r['expires'] else '')
                + (f' · **kwargs:** `{r["kwargs"]}`' if r['kwargs'] else '')
            )
            out.append('')
            if r['task_resolves']:
                if r['task_doc']:
                    out.append(_first_paragraph(r['task_doc']))
                else:
                    out.append('_(task resolves but has no docstring)_')
                if r['task_file']:
                    out.append('')
                    out.append(
                        f'_Source: `{r["task_file"]}'
                        + (f':{r["task_line"]}' if r['task_line'] else '')
                        + '`_'
                    )
            else:
                out.append('_(task reference does NOT resolve in the Celery registry — broken)_')
            out.append('')

        return '\n'.join(out) + '\n'


# helpers

def _format_schedule(sched: Any) -> str:
    if sched is None:
        return '<none>'
    if isinstance(sched, (int, float)):
        if sched >= 3600:
            return f'every {sched/3600:g}h'
        if sched >= 60:
            return f'every {sched/60:g}m'
        return f'every {sched}s'
    # crontab repr looks like: <crontab: */30 * * * *  (m/h/d/dM/MY)>
    s = repr(sched)
    # Try to extract the cron expression cleanly.
    if 'crontab:' in s:
        # crontab: minute hour day_of_week day_of_month month_of_year
        try:
            inside = s.split('crontab:', 1)[1].split('(')[0].strip().rstrip('>').strip()
            return inside
        except Exception:  # noqa: BLE001
            pass
    return s


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


def _pct(n: int, total: int) -> int:
    return int(round(100.0 * n / total)) if total else 0
