"""Generate ``docs/CELERY_AUDIT.md`` — every Celery task, who calls it, who doesn't.

Built in Session 1115, tenth subsystem audit. The beat audit
(`BEAT_AUDIT.md`) covers the **42 scheduled** tasks. This audit walks
the **full** Celery task registry (~365–375 tasks) and answers two
questions per task:

1. Where is it defined (file:line + docstring + decorator args)?
2. Is it actually wired into anything? Specifically, does any code path
   call it via `task_name.delay(...)` or `apply_async(...)`, or is it
   listed in `app.conf.beat_schedule`?

Tasks with **no callers anywhere and no beat-schedule entry** are
orphans — they ship but nothing fires them.

The audit is the highest-leverage place to find "code we built but
never connected." It explicitly answers Chris's "is there anything we
haven't connected yet" question for the task layer.

Run::

    python manage.py build_celery_audit
"""
from __future__ import annotations

import ast
import inspect
import re
import subprocess
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_PATH = REPO_ROOT / 'docs' / 'CELERY_AUDIT.md'


class Command(BaseCommand):
    help = 'Regenerate docs/CELERY_AUDIT.md from the full Celery task registry.'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--check', action='store_true',
            help='Print the would-be file to stdout instead of writing.',
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        from core.celery import app as celery_app
        registry = {
            name: task for name, task in celery_app.tasks.items()
            if not name.startswith('celery.')
        }
        scheduled = {
            (entry or {}).get('task', '') or ''
            for entry in (celery_app.conf.beat_schedule or {}).values()
        }
        scheduled.discard('')

        # Caller cache: grep once, build callers-per-task lookup.
        callers_by_short, callers_by_full = self._build_caller_index()

        rows: list[dict] = []
        for name in sorted(registry):
            rows.append(self._inspect(
                name, registry[name],
                scheduled=scheduled,
                callers_by_short=callers_by_short,
                callers_by_full=callers_by_full,
            ))

        findings = self._collect_findings(rows)
        rendered = self._render(rows, findings=findings)

        if opts['check']:
            self.stdout.write(rendered)
            return

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(rendered)
        n_orphans = sum(1 for r in rows if r['is_orphan'])
        n_scheduled = sum(1 for r in rows if r['is_scheduled'])
        n_with_callers = sum(1 for r in rows if r['callers'])
        self.stdout.write(self.style.SUCCESS(
            f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} "
            f"({len(rows)} tasks · {n_scheduled} scheduled · "
            f"{n_with_callers} have callers · {n_orphans} orphans)"
        ))

    # ----------------------------------------------------------- inspect

    def _build_caller_index(self) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
        """Build two indices of "who calls this task":

        ``callers_by_short`` — short-name keyed (``foo_task`` → callers
        via ``foo_task.delay()`` / ``foo_task.apply_async()`` /
        ``foo_task.s()`` / ``foo_task.si()``).

        ``callers_by_full`` — full-dotted-path keyed (``module.path.foo``).
        Caller sources cross-checked:

          - ``send_task('module.path.foo')`` / ``current_app.send_task(...)``
            dynamic dispatch.
          - ``add_critical_celery_tasks.py`` task dict — a *second*
            scheduler source that creates `PeriodicTask` rows separate
            from `app.conf.beat_schedule`. Session 1115 batch-1 audit
            of #12 surfaced this as a major missing caller path.
          - ``ops_autopilot/budget.py`` task-budget dict — the autopilot
            dispatches these tasks within daily budgets.
          - Same-name `core/management/commands/<short>.py` — when a
            management command exists matching the task short-name, it's
            a real public caller path. Session 1115 batch-1 confirmed
            several "orphans" are CLI-only.

        Each indirect path appends a marker entry (e.g.
        `[add_critical_celery_tasks:LINE]`) so the audit's per-task
        caller list shows which kind of caller found it.
        """
        callers_by_short: dict[str, list[str]] = {}
        callers_by_full: dict[str, list[str]] = {}

        # 1) Method-call shape: `name.delay/apply_async/s/si(`
        try:
            r1 = subprocess.run(
                ['grep', '-rEn',
                 r'\b\w+\.(delay|apply_async|s|si)\s*\(',
                 str(REPO_ROOT),
                 '--include=*.py',
                 '--exclude-dir=.venv',
                 '--exclude-dir=__pycache__',
                 '--exclude-dir=node_modules',
                 '--exclude-dir=archive',
                ],
                capture_output=True, text=True, timeout=120,
            )
        except subprocess.TimeoutExpired:
            r1 = None
        method_pattern = re.compile(
            r'(?P<file>[^:]+):(?P<line>\d+):.*?(?P<name>\b\w+)\.(?:delay|apply_async|s|si)\s*\('
        )
        for line in (r1.stdout.splitlines() if r1 else []):
            m = method_pattern.search(line)
            if not m:
                continue
            short = m.group('name')
            # Filter out obvious false positives: very common short names that
            # are almost certainly NOT task references (`obj.s(` for a string,
            # `self.s(` for an attribute, etc.). `.delay(` and `.apply_async(`
            # are far more specific so let those through unfiltered.
            if '.s(' in line or '.si(' in line:
                # `.s(`/`.si(` are noisier — accept only if the short name
                # looks task-shaped (snake_case, ends in known suffixes, or
                # is a known task short name).
                if not re.match(r'^[a-z_]+_(task|run|job|scan|cleanup|backfill|process|sync|update|generate|enrich|check|monitor|fetch|collect|warm|broadcast|trigger|review|send|build|train|retrain|orchestrate|create)$', short) \
                   and not short.endswith('_task') and not short.startswith('task_'):
                    continue
            file_ = m.group('file')
            try:
                rel = str(Path(file_).resolve().relative_to(REPO_ROOT))
            except ValueError:
                rel = file_
            callers_by_short.setdefault(short, []).append(
                f'{rel}:{m.group("line")}'
            )

        # 2) String-dispatch shape: `send_task('full.path.task_name'...)`
        try:
            r2 = subprocess.run(
                ['grep', '-rEn',
                 r'send_task\s*\(\s*[\'"][^\'"]+[\'"]',
                 str(REPO_ROOT),
                 '--include=*.py',
                 '--exclude-dir=.venv',
                 '--exclude-dir=__pycache__',
                 '--exclude-dir=node_modules',
                 '--exclude-dir=archive',
                ],
                capture_output=True, text=True, timeout=60,
            )
        except subprocess.TimeoutExpired:
            r2 = None
        full_pattern = re.compile(
            r'(?P<file>[^:]+):(?P<line>\d+):.*?send_task\s*\(\s*[\'"](?P<name>[^\'"]+)[\'"]'
        )
        for line in (r2.stdout.splitlines() if r2 else []):
            m = full_pattern.search(line)
            if not m:
                continue
            full = m.group('name')
            file_ = m.group('file')
            try:
                rel = str(Path(file_).resolve().relative_to(REPO_ROOT))
            except ValueError:
                rel = file_
            callers_by_full.setdefault(full, []).append(
                f'{rel}:{m.group("line")}'
            )

        # 3) `add_critical_celery_tasks.py` task dict — second scheduler source.
        cct = REPO_ROOT / 'core' / 'management' / 'commands' / 'add_critical_celery_tasks.py'
        if cct.exists():
            try:
                src = cct.read_text(errors='ignore')
                for i, line in enumerate(src.splitlines(), start=1):
                    m = re.search(r"'task':\s*'([\w.]+)'", line)
                    if m:
                        callers_by_full.setdefault(m.group(1), []).append(
                            f'core/management/commands/add_critical_celery_tasks.py:{i}'
                        )
            except OSError:
                pass

        # 4) ops_autopilot/budget.py task-budget dict — autopilot caller path.
        autop = REPO_ROOT / 'core' / 'services' / 'ops_autopilot' / 'budget.py'
        if autop.exists():
            try:
                src = autop.read_text(errors='ignore')
                for i, line in enumerate(src.splitlines(), start=1):
                    # Match lines like `'core.tasks.foo': 2,`
                    m = re.search(r"'(core\.tasks\.[\w.]+|[a-z_]+\.[a-z_.]+)'\s*:\s*\d+", line)
                    if m:
                        callers_by_full.setdefault(m.group(1), []).append(
                            f'core/services/ops_autopilot/budget.py:{i}'
                        )
            except OSError:
                pass

        # 5) Same-name management command — if `core/management/commands/<short>.py`
        #    exists for a registered task, the CLI is a real public caller.
        cmd_dir = REPO_ROOT / 'core' / 'management' / 'commands'
        if cmd_dir.exists():
            cmd_stems = {
                p.stem for p in cmd_dir.glob('*.py') if p.name != '__init__.py'
            }
            for stem in cmd_stems:
                # If a task short-name matches, register the .py as a caller.
                callers_by_short.setdefault(stem, []).append(
                    f'core/management/commands/{stem}.py'
                )

        # 6) Generic string-literal scan. Some dispatch sites pass task names
        #    via dict entries like `'task': 'run_foo'` or string maps like
        #    `{'foo': 'run_foo'}`. Session 1115 batch-2 surfaced this pattern
        #    in `tasks_ops.py`, `discord_bot.py`, and `views_autonomous_dashboard.py`.
        #
        #    Strategy: grep for any quoted string that exactly matches one of
        #    the registered task short-names or full paths. Filter out the
        #    task's own definition file. Conservative — only counts EXACT
        #    matches with surrounding quotes, so noise like substrings in
        #    docstrings is excluded.
        # NOTE: BSD grep / POSIX ERE doesn't understand `\w` shorthand, so
        # use an explicit `[[:alnum:]_]` character class. Python's re module
        # below does understand `\w`, so the token_pattern can stay terse.
        try:
            r3 = subprocess.run(
                ['grep', '-rEon', r"['\"][[:alnum:]_.]+['\"]",
                 str(REPO_ROOT),
                 '--include=*.py',
                 '--exclude-dir=.venv',
                 '--exclude-dir=__pycache__',
                 '--exclude-dir=node_modules',
                 '--exclude-dir=archive',
                ],
                capture_output=True, text=True, timeout=180,
            )
        except subprocess.TimeoutExpired:
            r3 = None
        # Build sets of names we care about
        # (these need to come from `_inspect` — but at the point this method
        #  runs, we don't have the registry. Pull from the task dispatcher.)
        from core.celery import app as celery_app
        registry = {
            t for t in celery_app.tasks.keys() if not t.startswith('celery.')
        }
        short_names_set = {t.rsplit('.', 1)[-1] for t in registry}
        # Match the file:line prefix then capture ALL quoted strings on the
        # line. Earlier version only captured the first quoted string per
        # line, which missed dict-VALUE positions like
        # `'job_matching': 'run_foo_task'` (key matched, value lost).
        prefix_pattern = re.compile(r'^([^:]+):(\d+):(.*)$')
        token_pattern = re.compile(r'[\'"]([\w.]+)[\'"]')
        # Files to skip entirely — these are task DEFINITION files where the
        # `@shared_task(name='X')` decorator names the task but isn't a
        # caller of it. Specifically core/tasks.py + tasks_*.py adjacent
        # modules. Other tasks.py files in different apps (intelligence,
        # ai_core, etc.) CAN be legitimate callers of core tasks.
        skip_files = {'core/tasks.py'}
        for line in (r3.stdout.splitlines() if r3 else []):
            pm = prefix_pattern.match(line)
            if not pm:
                continue
            file_, lineno, rest = pm.group(1), pm.group(2), pm.group(3)
            try:
                rel = str(Path(file_).resolve().relative_to(REPO_ROOT))
            except ValueError:
                rel = file_
            if rel in skip_files:
                continue
            for val_match in token_pattern.finditer(rest):
                val = val_match.group(1)
                if val in registry:
                    callers_by_full.setdefault(val, []).append(f'{rel}:{lineno}')
                elif val in short_names_set:
                    callers_by_short.setdefault(val, []).append(f'{rel}:{lineno}')

        # 7) Importlib-style path scan: `'module.path:task_name'`. Used by
        #    `scheduled_diagnostic_runner` and similar dispatchers that
        #    resolve a task via importlib at runtime. These are correctly
        #    wired callers — the runner enqueues the task with
        #    apply_async(countdown=240) — but the path string uses `:` as
        #    the module/func separator, which the standard quoted-token
        #    scan above doesn't catch (`:` isn't in [[:alnum:]_.]).
        try:
            r4 = subprocess.run(
                ['grep', '-rEon',
                 r"['\"][[:alnum:]_.]+:[[:alnum:]_]+['\"]",
                 str(REPO_ROOT),
                 '--include=*.py',
                 '--exclude-dir=.venv',
                 '--exclude-dir=__pycache__',
                 '--exclude-dir=node_modules',
                 '--exclude-dir=archive',
                ],
                capture_output=True, text=True, timeout=60,
            )
        except subprocess.TimeoutExpired:
            r4 = None
        importlib_pattern = re.compile(r'[\'"]([\w.]+):(\w+)[\'"]')
        for line in (r4.stdout.splitlines() if r4 else []):
            pm = prefix_pattern.match(line)
            if not pm:
                continue
            file_, lineno, rest = pm.group(1), pm.group(2), pm.group(3)
            try:
                rel = str(Path(file_).resolve().relative_to(REPO_ROOT))
            except ValueError:
                rel = file_
            if rel in skip_files:
                continue
            for path_match in importlib_pattern.finditer(rest):
                module_path = path_match.group(1)
                func_name = path_match.group(2)
                full = f'{module_path}.{func_name}'
                if full in registry:
                    callers_by_full.setdefault(full, []).append(f'{rel}:{lineno}')
                elif func_name in short_names_set:
                    callers_by_short.setdefault(func_name, []).append(f'{rel}:{lineno}')

        return callers_by_short, callers_by_full

    def _inspect(
        self,
        name: str,
        task,
        *,
        scheduled: set[str],
        callers_by_short: dict[str, list[str]],
        callers_by_full: dict[str, list[str]],
    ) -> dict:
        # Short name = last dotted segment, used to match `.delay(` callers.
        short = name.rsplit('.', 1)[-1]
        run_fn = getattr(task, 'run', None)
        file_path = ''
        line_no = 0
        docstring_first_line = ''
        if run_fn is not None:
            try:
                file_path_raw = inspect.getfile(run_fn)
                try:
                    file_path = str(Path(file_path_raw).resolve().relative_to(REPO_ROOT))
                except ValueError:
                    file_path = file_path_raw
            except (TypeError, OSError):
                pass
            try:
                _, line_no = inspect.getsourcelines(run_fn)
            except (OSError, TypeError):
                pass
            doc = inspect.getdoc(run_fn) or ''
            for ln in doc.splitlines():
                s = ln.strip()
                if s:
                    docstring_first_line = s
                    break
        # Decorator config
        queue = getattr(task, 'queue', None) or ''
        soft_time_limit = getattr(task, 'soft_time_limit', None)
        time_limit = getattr(task, 'time_limit', None)
        ignore_result = bool(getattr(task, 'ignore_result', False))
        bind = bool(getattr(task, '_bound', False))  # heuristic

        # Caller cross-reference. Combine static (.delay/.apply_async/.s/.si)
        # and dynamic (send_task('full.path')) lookups. Filter out only the
        # task's own definition LINE from static callers. The original filter
        # excluded the whole definition file, which dropped legitimate
        # intra-file parent→child chains (e.g. `intelligence/tasks.py` has
        # `submit_proposal_automatically.delay(...)` at line 1192 chaining
        # into the task defined at line 1209 — both lines live in the same
        # file but the dispatch is real). Session 1115 batch-5 fix.
        raw_static = callers_by_short.get(short, [])
        own_marker = f'{file_path}:{line_no}' if file_path and line_no else None
        static_callers = [
            c for c in raw_static
            if own_marker is None or c != own_marker
        ]
        dynamic_callers = callers_by_full.get(name, [])
        callers = static_callers + dynamic_callers

        is_scheduled = name in scheduled
        is_orphan = (not callers) and (not is_scheduled)

        return {
            'name': name,
            'short_name': short,
            'module': '.'.join(name.split('.')[:-1]),
            'file': file_path or '(unknown)',
            'line': line_no,
            'docstring_first_line': docstring_first_line,
            'queue': queue,
            'soft_time_limit': soft_time_limit,
            'time_limit': time_limit,
            'ignore_result': ignore_result,
            'is_scheduled': is_scheduled,
            'callers': callers,
            'caller_count': len(callers),
            'is_orphan': is_orphan,
        }

    # ---------------------------------------------------------- findings

    def _collect_findings(self, rows: list[dict]) -> list[str]:
        findings: list[str] = []

        orphans = [r for r in rows if r['is_orphan']]
        if orphans:
            sample = ', '.join(f'`{r["short_name"]}`' for r in orphans[:8])
            findings.append(
                f"**Orphan tasks** — {len(orphans)} tasks have no caller via "
                f"`.delay(...)` / `.apply_async(...)` AND aren't in "
                f"`app.conf.beat_schedule`. They ship but nothing fires "
                f"them. Top: {sample}"
                + ('…' if len(orphans) > 8 else '')
                + '. Full list in the appendix.'
            )

        no_doc = [r for r in rows if not r['docstring_first_line']]
        if no_doc:
            pct = round(100.0 * len(no_doc) / len(rows))
            findings.append(
                f"Tasks with no docstring: {len(no_doc)} of {len(rows)} "
                f"({pct}%). The audit relies on the function docstring "
                f"to describe what each task does."
            )

        scheduled_orphans = [
            r for r in rows
            if r['is_scheduled'] and not r['callers']
        ]
        # That's normal — schedule is the caller. Not a finding.

        from collections import Counter
        by_queue = Counter(r['queue'] or '<default>' for r in rows)
        biggest = by_queue.most_common(1)[0]
        findings.append(
            f"Queue distribution (top 5): "
            + ', '.join(
                f'`{q}` ({n})' for q, n in by_queue.most_common(5)
            )
            + f". `{biggest[0]}` carries {biggest[1]} of {len(rows)} tasks."
        )

        # Cross-reference with beat audit's broken refs
        broken_short_names = {
            'clean_stale_data', 'cleanup_old_model_files',
            'cleanup_old_predictions', 'cleanup_old_opportunities',
            'collect_real_opportunities', 'scan_spider_opportunities',
            'warm_up_spider_network',
        }
        found_broken = [
            r['name'] for r in rows
            if r['short_name'] in broken_short_names
        ]
        if found_broken:
            findings.append(
                f"Cross-reference: the 7 broken beat refs (BEAT_AUDIT.md "
                f"finding 3) point at tasks that DO exist in the registry "
                f"once their modules are imported — found in this audit at: "
                + ', '.join(f'`{n}`' for n in found_broken)
                + '. The issue is autodiscover at worker startup, not '
                f'missing tasks.'
            )

        return findings

    # ------------------------------------------------------------ render

    def _render(self, rows: list[dict], *, findings: list[str]) -> str:
        n_total = len(rows)
        n_scheduled = sum(1 for r in rows if r['is_scheduled'])
        n_with_callers = sum(1 for r in rows if r['callers'])
        n_orphans = sum(1 for r in rows if r['is_orphan'])
        n_with_doc = sum(1 for r in rows if r['docstring_first_line'])

        out: list[str] = []
        out.append(
            '<!-- DOC-AUTOGEN: regenerated by '
            '`python manage.py build_celery_audit`. Do not hand-edit. -->'
        )
        out.append('')
        out.append('# Capability Audit — Celery Tasks')
        out.append('')
        out.append(
            "**Source of truth:** `core.celery.app.tasks` (the full Celery "
            "registry after auto-discovery), cross-referenced against "
            "`app.conf.beat_schedule` and a codebase-wide grep for "
            "`.delay(` / `.apply_async(` callers."
        )
        out.append('')
        out.append('## Headline')
        out.append('')
        out.append(f'- **User-defined tasks (`!celery.*`):** {n_total}')
        out.append(f'- **Scheduled in `beat_schedule`:** {n_scheduled} of {n_total}')
        out.append(
            f'- **Has at least one `.delay()` / `.apply_async()` caller:** '
            f'{n_with_callers} of {n_total}'
        )
        out.append(
            f'- **Orphans (no caller AND not scheduled):** **{n_orphans}** '
            f'of {n_total}. These ship but nothing fires them.'
        )
        out.append(
            f'- **Tasks with docstrings:** {n_with_doc} of {n_total} '
            f'({_pct(n_with_doc, n_total)}%)'
        )
        out.append('')
        out.append(
            "> A task can be wired by either path: a `beat_schedule` "
            "entry (cron-fires it) or an explicit `.delay(...)` from view / "
            "service / agent code. Tasks with neither are dead-on-arrival — "
            "the function exists but no execution path reaches it."
        )
        out.append('')

        if findings:
            out.append('## Findings')
            out.append('')
            for f in findings:
                out.append(f'- {f}')
            out.append('')

        # Orphan section
        orphans = [r for r in rows if r['is_orphan']]
        if orphans:
            out.append(f'## Orphan tasks ({len(orphans)})')
            out.append('')
            out.append(
                "Tasks with no static caller and no beat-schedule entry. "
                "Worth a manual review — some may be invoked dynamically "
                "(reflection, name-based dispatch) and a few may be intentionally "
                "kept warm for future use, but most are likely dead code "
                "or got disconnected during a refactor."
            )
            out.append('')
            out.append('| Task | Module | File | Queue | Description |')
            out.append('|---|---|---|---|---|')
            for r in orphans:
                desc = r['docstring_first_line'] or '_(no docstring)_'
                desc = desc.replace('|', '\\|')
                if len(desc) > 80:
                    desc = desc[:77] + '…'
                file_link = (
                    f'`{r["file"]}:{r["line"]}`' if r['line']
                    else f'`{r["file"]}`'
                )
                out.append(
                    f'| `{r["short_name"]}` | `{r["module"]}` | {file_link} | '
                    f'`{r["queue"] or "<default>"}` | {desc} |'
                )
            out.append('')

        # Module rollup
        from collections import defaultdict
        by_mod: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            by_mod[r['module']].append(r)
        out.append(f'## Tasks by module ({len(by_mod)} modules)')
        out.append('')
        out.append('| Module | Tasks | Scheduled | Wired | Orphans |')
        out.append('|---|---:|---:|---:|---:|')
        for mod, bucket in sorted(by_mod.items(), key=lambda kv: -len(kv[1])):
            scheduled_n = sum(1 for r in bucket if r['is_scheduled'])
            wired_n = sum(1 for r in bucket if r['callers'])
            orphan_n = sum(1 for r in bucket if r['is_orphan'])
            out.append(
                f'| `{mod}` | {len(bucket)} | {scheduled_n} | {wired_n} | '
                f'{orphan_n} |'
            )
        out.append('')

        # Full table (compact)
        out.append('## Full task list')
        out.append('')
        out.append(
            "All tasks, alphabetical by short name. `Sched.` = beat schedule. "
            "`Callers` = file:line sites that call `.delay()` / `.apply_async()` "
            "on this task name (the count, not the list). `Orphan` flags "
            "tasks with neither."
        )
        out.append('')
        out.append('| Task | Module | Line | Queue | Sched. | Callers | Orphan | Description |')
        out.append('|---|---|---:|---|:-:|---:|:-:|---|')
        for r in sorted(rows, key=lambda r: (r['short_name'], r['name'])):
            desc = r['docstring_first_line'] or '_(no docstring)_'
            desc = desc.replace('|', '\\|')
            if len(desc) > 70:
                desc = desc[:67] + '…'
            sched = '✓' if r['is_scheduled'] else '·'
            orphan = '⚠' if r['is_orphan'] else '·'
            out.append(
                f'| `{r["short_name"]}` | `{r["module"]}` | {r["line"] or "?"} | '
                f'`{r["queue"] or "<default>"}` | {sched} | '
                f'{r["caller_count"]} | {orphan} | {desc} |'
            )
        out.append('')

        return '\n'.join(out) + '\n'


def _pct(n: int, total: int) -> int:
    return int(round(100.0 * n / total)) if total else 0
