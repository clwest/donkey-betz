"""Run documentation-vs-reality claim verification.

Built in Session 1099 after the agent-system audit surfaced ~7 distinct
drifts between what docs claim and what the runtime actually reports.

See ``core/services/doc_claim_verification.py`` for the framework and the
seed claim registry.

Examples::

    # Run every registered claim, human-readable
    python manage.py verify_doc_claims

    # Filter to a single doc
    python manage.py verify_doc_claims --doc CLAUDE.md

    # Show only drift (hide matches)
    python manage.py verify_doc_claims --only-drift

    # Machine-readable output
    python manage.py verify_doc_claims --format json

    # List registered claims without running them
    python manage.py verify_doc_claims --list

    # Fail the process on any drift (useful for CI)
    python manage.py verify_doc_claims --fail-on-drift
"""
from __future__ import annotations

import json
import sys
from typing import Any

from django.core.management.base import BaseCommand


SEVERITY_ICONS = {
    'ok': '✓',
    'low': '·',
    'medium': '●',
    'high': '▲',
    'critical': '■',
    'error': '?',
}


class Command(BaseCommand):
    help = 'Verify claims in authoritative docs against runtime reality.'

    def add_arguments(self, parser) -> None:
        parser.add_argument('--doc', help='Filter to a single doc path')
        parser.add_argument('--only-drift', action='store_true',
                            help='Hide matches — show only ok != True results')
        parser.add_argument('--format', choices=('text', 'json'), default='text',
                            help='Output format')
        parser.add_argument('--list', action='store_true',
                            help='List registered claims without running them')
        parser.add_argument('--fail-on-drift', action='store_true',
                            help='Exit non-zero when any non-ok result is found')

    def handle(self, *args: Any, **opts: Any) -> None:
        from core.services.doc_claim_verification import (
            list_registered, run_all, summarize,
        )

        if opts['list']:
            entries = list_registered()
            if opts['format'] == 'json':
                self.stdout.write(json.dumps(entries, indent=2))
            else:
                self._render_list(entries)
            return

        results = run_all(
            doc_filter=opts.get('doc'),
            only_drift=opts['only_drift'],
        )
        summary = summarize(results)

        if opts['format'] == 'json':
            payload = {
                'summary': summary,
                'results': [r.to_dict() for r in results],
            }
            self.stdout.write(json.dumps(payload, indent=2, default=str))
        else:
            self._render_text(results, summary)

        if opts['fail_on_drift']:
            non_ok = summary['by_severity'].get('ok', 0)
            total = summary['total']
            if total > 0 and non_ok < total:
                sys.exit(1)

    # ---- renderers ---------------------------------------------------------

    def _render_list(self, entries: list[dict]) -> None:
        by_doc: dict[str, list[dict]] = {}
        for e in entries:
            by_doc.setdefault(e['doc'], []).append(e)
        self.stdout.write(self.style.NOTICE(
            f"Registered claims: {len(entries)} across {len(by_doc)} docs\n"
        ))
        for doc, items in sorted(by_doc.items()):
            self.stdout.write(self.style.WARNING(f"\n  {doc}"))
            for it in items:
                desc = (it.get('description') or '').strip()
                self.stdout.write(f"    · {it['claim_id']:40} — {desc[:80]}")

    def _render_text(self, results: list, summary: dict) -> None:  # noqa: C901
        if not results:
            self.stdout.write("No matching claims to run.")
            return

        # Group by doc for readable output
        by_doc: dict[str, list] = {}
        for r in results:
            by_doc.setdefault(r.doc, []).append(r)

        for doc, items in sorted(by_doc.items()):
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(f"── {doc} ──"))
            for r in items:
                icon = SEVERITY_ICONS.get(r.severity, '·')
                style = (
                    self.style.SUCCESS if r.severity == 'ok'
                    else self.style.ERROR if r.severity in ('high', 'critical', 'error')
                    else self.style.WARNING
                )
                self.stdout.write(style(
                    f"  {icon} [{r.severity:>8}] {r.claim_id}"
                ))
                if r.description:
                    self.stdout.write(f"      claim: {r.description.strip().splitlines()[0][:100]}")
                if r.severity != 'ok':
                    self.stdout.write(f"      expected: {r.expected}")
                    self.stdout.write(f"      actual:   {r.actual}")
                if r.note:
                    self.stdout.write(f"      note:     {r.note}")
                if r.fix_suggestion:
                    self.stdout.write(self.style.NOTICE(f"      fix:      {r.fix_suggestion}"))
                if r.error:
                    self.stdout.write(self.style.ERROR(f"      error:    {r.error.strip().splitlines()[-1][:200]}"))

        # Summary footer
        self.stdout.write('')
        self.stdout.write(self.style.NOTICE("── Summary ──"))
        self.stdout.write(f"  total: {summary['total']}")
        for sev in ('ok', 'low', 'medium', 'high', 'critical', 'error'):
            n = summary['by_severity'].get(sev, 0)
            if n > 0:
                self.stdout.write(f"  {sev:>8}: {n}")
        self.stdout.write('')
        self.stdout.write("  by doc:")
        for doc, d in sorted(summary['by_doc'].items()):
            self.stdout.write(
                f"    {doc:40} ok={d['ok']:>2}  drift={d['drift']:>2}  error={d['error']:>2}"
            )
