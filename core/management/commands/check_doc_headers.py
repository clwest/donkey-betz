"""Check ``Last Updated: Session N`` headers in docs against body recency.

`verify_doc_claims` covers semantic claim drift (counts, registry sizes,
schedules). It does NOT catch a separate class of drift: the
``Last Updated: Session N`` header at the top of a doc lying because
someone added content to the body but never bumped the header.

This command parses every ``docs/**/*.md`` file, extracts the header
session, scans the body for the highest ``Session NNN`` reference, and
classifies each doc:

  • **clean**       — header session matches the latest body reference (or
                       the body has no session refs and the header is
                       within ``--frozen-after`` of the current session).
  • **header_lag**  — body references a session newer than the header
                       (lag >= ``--threshold``). Category A: doc is
                       maintained, header just isn't bumped.
  • **frozen**      — header session is older than
                       ``--current-session`` by more than ``--frozen-after``
                       and the body has no newer session refs. Category B:
                       likely a zombie doc.
  • **no_header**   — file has no ``Last Updated`` line at all.
  • **no_body_refs**— header present, body has no ``Session NNN`` refs;
                       cannot compute lag. Flagged separately so it isn't
                       mis-classified as clean.

Examples::

    python manage.py check_doc_headers
    python manage.py check_doc_headers --only-stale
    python manage.py check_doc_headers --threshold 5
    python manage.py check_doc_headers --format json
    python manage.py check_doc_headers --fail-on-stale  # CI gate

By default we read ``--current-session`` from the most-recent session
number visible across all docs/handoffs, so the command is self-anchoring.
Override with ``--current-session N`` for deterministic CI.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable

from django.conf import settings
from django.core.management.base import BaseCommand


HEADER_RE = re.compile(
    # Must say "Session NNN" explicitly — bare 4-digit numbers in
    # "Last Updated: 2026-05-24" would otherwise be mis-parsed as session
    # IDs. Date-only headers are intentionally treated as `no_header`.
    r'^\s*\**\s*Last\s+Updated\s*[:\-]\s*\**\s*Session\s+(\d{2,4})',
    re.IGNORECASE | re.MULTILINE,
)
BODY_SESSION_RE = re.compile(r'\bSession\s+(\d{2,4})\b')

DEFAULT_DOCS_ROOT = 'docs'
SKIP_NAMES = {
    # Auto-generated indexes — recency drift is irrelevant.
    'INDEX.md',
    '_index.json',
}
SKIP_DIR_PARTS = {
    'archive',  # Anything explicitly archived shouldn't be flagged.
    'handoffs',  # Each handoff is a frozen snapshot of its own session.
    'sessions',
}


@dataclass
class DocReport:
    path: str
    header_session: int | None
    body_latest_session: int | None
    lag: int | None  # body_latest - header (positive = header behind body)
    category: str
    note: str = ''

    def as_row(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Summary:
    total: int = 0
    by_category: dict[str, int] = field(default_factory=dict)

    def bump(self, category: str) -> None:
        self.total += 1
        self.by_category[category] = self.by_category.get(category, 0) + 1


def _iter_docs(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob('*.md')):
        if path.name in SKIP_NAMES:
            continue
        if any(part in SKIP_DIR_PARTS for part in path.parts):
            continue
        yield path


def _parse_header_session(text: str) -> int | None:
    """Top-of-doc Last-Updated line wins.

    Restricted to the first 30 lines so per-section ``Last Updated:`` lines
    inside the body (common in long reference docs like
    ``docs/archive/superseded-2026-05/agents/README.md``)
    don't shadow the real doc-level header. Returns the integer session number.
    """
    head = '\n'.join(text.splitlines()[:30])
    m = HEADER_RE.search(head)
    if not m:
        return None
    try:
        return int(m.group(1))
    except (ValueError, IndexError):
        return None


def _max_body_session(text: str) -> int | None:
    """Highest 'Session NNN' integer found in the body.

    Lines that match the header regex are excluded — a header note like
    ``Last Updated: Session 933 (... header bumped Session 1142)`` would
    otherwise pollute the body-latest calculation.
    """
    body_lines = [ln for ln in text.splitlines() if not HEADER_RE.match(ln)]
    body = '\n'.join(body_lines)
    nums = [int(m) for m in BODY_SESSION_RE.findall(body)]
    return max(nums) if nums else None


def _infer_current_session(reports: list[DocReport], handoffs_dir: Path) -> int:
    """Pick a sensible 'now' anchor.

    Preference order:
      1. The highest ``Session NNNN`` referenced in any handoff filename
         (``SESSION_1141_*.md``). Handoffs are append-only per session.
      2. The highest body_latest_session across the analyzed reports.
      3. 0 (degenerate; everything will look 'frozen').
    """
    if handoffs_dir.exists():
        session_re = re.compile(r'SESSION[_-]?(\d{2,4})', re.IGNORECASE)
        nums: list[int] = []
        for p in handoffs_dir.iterdir():
            m = session_re.search(p.name)
            if m:
                try:
                    nums.append(int(m.group(1)))
                except ValueError:
                    pass
        if nums:
            return max(nums)

    body_nums = [r.body_latest_session for r in reports if r.body_latest_session]
    return max(body_nums) if body_nums else 0


def _classify(
    header: int | None,
    body_latest: int | None,
    current_session: int,
    threshold: int,
    frozen_after: int,
) -> tuple[str, str]:
    if header is None:
        return 'no_header', 'no Last Updated header found'
    if body_latest is None:
        # Header exists, no body session refs at all → can't compute lag.
        # If the header is itself ancient, still flag as frozen.
        if header and (current_session - header) > frozen_after:
            return 'frozen', (
                f"header at Session {header}; no body refs and "
                f"{current_session - header} sessions behind current"
            )
        return 'no_body_refs', 'header present but body has no Session NNN refs'

    lag = body_latest - header
    if lag >= threshold:
        return 'header_lag', (
            f"body references Session {body_latest}, "
            f"header still at Session {header} (lag={lag})"
        )

    # Header agrees with body. Check whether the whole doc is stagnant.
    distance = current_session - max(header, body_latest)
    if distance > frozen_after:
        return 'frozen', (
            f"latest activity at Session {max(header, body_latest)}; "
            f"{distance} sessions behind current ({current_session})"
        )
    return 'clean', ''


class Command(BaseCommand):
    help = (
        'Check Last Updated headers in docs against latest Session N body '
        'references. Complements verify_doc_claims (semantic claim drift).'
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--root', default=DEFAULT_DOCS_ROOT,
            help='Docs root to walk (default: docs/)',
        )
        parser.add_argument(
            '--threshold', type=int, default=1,
            help='Lag in sessions to flag as header_lag (default: 1)',
        )
        parser.add_argument(
            '--frozen-after', type=int, default=100,
            help=(
                'Sessions of inactivity (current - max(header,body)) before '
                'a doc is classified frozen (default: 100)'
            ),
        )
        parser.add_argument(
            '--current-session', type=int, default=None,
            help=(
                'Override what "current" is. Defaults to highest session '
                'inferred from docs/handoffs/SESSION_NNNN_*.md filenames.'
            ),
        )
        parser.add_argument(
            '--only-stale', action='store_true',
            help='Hide clean rows; show only header_lag/frozen/no_header.',
        )
        parser.add_argument(
            '--include-no-header', action='store_true',
            help='Surface no_header docs (off by default — many are intentional).',
        )
        parser.add_argument(
            '--format', choices=('text', 'json'), default='text',
        )
        parser.add_argument(
            '--fail-on-stale', action='store_true',
            help='Exit non-zero when any stale doc is found.',
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        base_dir = Path(getattr(settings, 'BASE_DIR', '.'))
        docs_root = base_dir / opts['root']
        if not docs_root.exists():
            self.stderr.write(self.style.ERROR(
                f"Docs root not found: {docs_root}"
            ))
            sys.exit(2)

        # Pass 1: parse every doc, then resolve current_session.
        partial: list[tuple[Path, int | None, int | None]] = []
        for path in _iter_docs(docs_root):
            try:
                text = path.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue
            partial.append((
                path,
                _parse_header_session(text),
                _max_body_session(text),
            ))

        # Determine current session anchor.
        proto_reports = [
            DocReport(
                path=str(p.relative_to(base_dir)),
                header_session=h,
                body_latest_session=b,
                lag=(b - h) if (h is not None and b is not None) else None,
                category='',
            )
            for (p, h, b) in partial
        ]
        current_session = (
            opts['current_session']
            if opts['current_session'] is not None
            else _infer_current_session(proto_reports, base_dir / 'docs' / 'handoffs')
        )

        threshold = opts['threshold']
        frozen_after = opts['frozen_after']
        reports: list[DocReport] = []
        for r in proto_reports:
            category, note = _classify(
                r.header_session, r.body_latest_session,
                current_session, threshold, frozen_after,
            )
            r.category = category
            r.note = note
            reports.append(r)

        # Filter for display
        if opts['only_stale']:
            visible = [r for r in reports if r.category != 'clean']
        else:
            visible = list(reports)

        if not opts['include_no_header']:
            visible = [r for r in visible if r.category != 'no_header']

        summary = Summary()
        for r in reports:  # Summary always reflects everything analyzed.
            summary.bump(r.category)

        if opts['format'] == 'json':
            payload = {
                'current_session': current_session,
                'threshold': threshold,
                'frozen_after': frozen_after,
                'summary': {
                    'total': summary.total,
                    'by_category': summary.by_category,
                },
                'reports': [r.as_row() for r in visible],
            }
            self.stdout.write(json.dumps(payload, indent=2))
        else:
            self._render_text(visible, summary, current_session, threshold, frozen_after)

        if opts['fail_on_stale']:
            stale = sum(
                summary.by_category.get(c, 0)
                for c in ('header_lag', 'frozen', 'no_header')
            )
            if stale > 0:
                sys.exit(1)

    # ---- renderer ---------------------------------------------------------

    def _render_text(
        self,
        rows: list[DocReport],
        summary: Summary,
        current_session: int,
        threshold: int,
        frozen_after: int,
    ) -> None:
        if not rows:
            self.stdout.write(self.style.SUCCESS(
                f"No stale docs found (current_session={current_session}, "
                f"threshold={threshold}, frozen_after={frozen_after})."
            ))
        else:
            # Group by category for readability.
            order = ('header_lag', 'frozen', 'no_body_refs', 'no_header', 'clean')
            by_cat: dict[str, list[DocReport]] = {}
            for r in rows:
                by_cat.setdefault(r.category, []).append(r)

            for cat in order:
                items = by_cat.get(cat)
                if not items:
                    continue
                style = (
                    self.style.WARNING if cat in ('header_lag', 'frozen', 'no_header')
                    else self.style.NOTICE if cat == 'no_body_refs'
                    else self.style.SUCCESS
                )
                self.stdout.write('')
                self.stdout.write(style(f"── {cat} ({len(items)}) ──"))
                # Sort by largest lag (or oldest header if no body refs).
                def sort_key(r: DocReport) -> tuple[int, int]:
                    primary = -(r.lag or 0)
                    secondary = (r.header_session or 0)
                    return (primary, secondary)
                for r in sorted(items, key=sort_key):
                    self.stdout.write(
                        f"  {r.path:55s} "
                        f"header={r.header_session if r.header_session is not None else '—':>5} "
                        f"body_latest={r.body_latest_session if r.body_latest_session is not None else '—':>5} "
                        f"lag={r.lag if r.lag is not None else '—':>4}"
                    )
                    if r.note:
                        self.stdout.write(f"    {r.note}")

        self.stdout.write('')
        self.stdout.write(self.style.NOTICE("── Summary ──"))
        self.stdout.write(f"  current_session anchor: {current_session}")
        self.stdout.write(f"  threshold:              {threshold}")
        self.stdout.write(f"  frozen_after:           {frozen_after}")
        self.stdout.write(f"  total docs analyzed:    {summary.total}")
        for cat in ('clean', 'header_lag', 'frozen', 'no_body_refs', 'no_header'):
            n = summary.by_category.get(cat, 0)
            if n:
                self.stdout.write(f"  {cat:>16}: {n}")
