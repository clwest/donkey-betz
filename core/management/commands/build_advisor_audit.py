"""Generate ``docs/ADVISOR_AUDIT.md`` from the live advisor registry.

Built in Session 1115, fifth subsystem audit (after agents, spiders, PA
tools, beat schedule). Walks the singleton at
``advisors.registry.advisor_registry`` and introspects every
``AdvisorProfile`` it materializes.

Notable: this audit pulls AdvisorProfile dataclass fields directly,
not class docstrings. Advisors aren't classes (they're data) so the
"what does this thing do" answer comes from `background`,
`specializations`, `key_achievements`, and `consultation_types`.

Run::

    python manage.py build_advisor_audit
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_PATH = REPO_ROOT / 'docs' / 'ADVISOR_AUDIT.md'


class Command(BaseCommand):
    help = "Regenerate docs/ADVISOR_AUDIT.md from advisor registry introspection."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--check',
            action='store_true',
            help='Print the would-be file to stdout instead of writing.',
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        from advisors.registry import advisor_registry, AdvisorDomain

        all_domains = {d.value for d in AdvisorDomain}
        rows: list[dict] = []
        for profile in advisor_registry.advisors.values():
            rows.append(self._inspect(profile))
        rows.sort(key=lambda r: (r['domain'], r['name']))

        findings = self._collect_findings(rows, declared_domains=all_domains)
        rendered = self._render(rows, findings=findings, declared_domains=all_domains)

        if opts['check']:
            self.stdout.write(rendered)
            return

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(rendered)
        n_named = sum(1 for r in rows if r['is_named_figure'])
        self.stdout.write(self.style.SUCCESS(
            f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} "
            f"({len(rows)} advisors · {n_named} named figures · "
            f"{len({r['domain'] for r in rows})} domains used)"
        ))

    # ----------------------------------------------------------- inspect

    def _inspect(self, profile) -> dict:
        # Named figure = the registry tags the name with "(AI Model)" suffix.
        is_named_figure = '(AI Model)' in (profile.name or '')
        clean_name = (profile.name or '').replace(' (AI Model)', '').strip()
        domain_value = (
            profile.domain.value if hasattr(profile.domain, 'value')
            else str(profile.domain)
        )
        expertise_value = (
            profile.expertise_level.value if hasattr(profile.expertise_level, 'value')
            else str(profile.expertise_level)
        )
        return {
            'id': profile.id,
            'name': clean_name,
            'name_raw': profile.name,
            'is_named_figure': is_named_figure,
            'title': profile.title,
            'domain': domain_value,
            'expertise_level': expertise_value,
            'years_experience': profile.years_experience,
            'specializations': list(profile.specializations or []),
            'consultation_types': list(profile.consultation_types or []),
            'decision_frameworks': list(profile.decision_frameworks or []),
            'background': profile.background or '',
            'key_achievements': list(profile.key_achievements or []),
            'certifications': list(profile.certifications or []),
        }

    # ---------------------------------------------------------- findings

    def _collect_findings(self, rows: list[dict], *, declared_domains: set[str]) -> list[str]:
        findings: list[str] = []

        # ID uniqueness check (sanity)
        from collections import Counter
        id_counts = Counter(r['id'] for r in rows)
        dupes = [i for i, n in id_counts.items() if n > 1]
        if dupes:
            findings.append(
                f"Duplicate advisor IDs registered: `{', '.join(dupes)}`. "
                f"Should be unique."
            )

        # Domains declared in the AdvisorDomain enum but with no advisor.
        used_domains = {r['domain'] for r in rows}
        unused_domains = sorted(declared_domains - used_domains)
        if unused_domains:
            findings.append(
                f"`AdvisorDomain` enum values with no registered advisor "
                f"({len(unused_domains)} of {len(declared_domains)}): "
                f"`{', '.join(unused_domains)}`. Could mean the domain is "
                f"a future-state stub or that the registry is incomplete."
            )

        # Advisors missing key narrative fields.
        no_background = [r['name'] for r in rows if not r['background']]
        if no_background:
            findings.append(
                f"Advisors with no `background` text: "
                f"`{', '.join(no_background)}`. The background is the "
                f"primary description in the audit."
            )

        no_achievements = [r['name'] for r in rows if not r['key_achievements']]
        if no_achievements:
            findings.append(
                f"Advisors with no `key_achievements`: "
                f"`{', '.join(no_achievements)}`."
            )

        no_specializations = [r['name'] for r in rows if not r['specializations']]
        if no_specializations:
            findings.append(
                f"Advisors with no `specializations`: "
                f"`{', '.join(no_specializations)}`. Without these, the "
                f"`find_best_advisor` topic matcher has nothing to score."
            )

        # Named figures vs domain specialists.
        n_named = sum(1 for r in rows if r['is_named_figure'])
        n_specialists = len(rows) - n_named
        findings.append(
            f"Composition: **{n_named} named figures** "
            f"({', '.join(sorted(r['name'] for r in rows if r['is_named_figure']))}) "
            f"+ **{n_specialists} domain specialists**. Total {len(rows)}. "
            f"`CLAUDE.md` Detailed Breakdown claimed `32 (10 named + 22 "
            f"specialists)` at the start of Session 1115 — the registry "
            f"only materializes the count above. Documented mismatch; "
            f"verifier guard `advisor_count_matches_doc` flags drift on "
            f"either side."
        )

        return findings

    # ------------------------------------------------------------ render

    def _render(self, rows: list[dict], *, findings: list[str], declared_domains: set[str]) -> str:
        n_total = len(rows)
        n_named = sum(1 for r in rows if r['is_named_figure'])
        from collections import Counter
        by_domain = Counter(r['domain'] for r in rows)
        by_expertise = Counter(r['expertise_level'] for r in rows)

        out: list[str] = []
        out.append(
            '<!-- DOC-AUTOGEN: regenerated by '
            '`python manage.py build_advisor_audit`. Do not hand-edit. -->'
        )
        out.append('')
        out.append('# Capability Audit — Advisors')
        out.append('')
        out.append(
            "**Source of truth:** `advisors.registry.advisor_registry` "
            "(singleton built at module import). Each entry is an "
            "`AdvisorProfile` dataclass populated from "
            "`_initialize_advisor_network` in `advisors/registry.py`."
        )
        out.append('')
        out.append('## Headline')
        out.append('')
        out.append(f'- **Advisors registered:** {n_total}')
        out.append(
            f'- **Named figures (tagged `(AI Model)`):** {n_named} — public '
            'figures whose voice the platform models.'
        )
        out.append(
            f'- **Domain specialists:** {n_total - n_named} — fictional '
            'expert personas with detailed backgrounds.'
        )
        out.append(
            f'- **Domains covered:** {len(by_domain)} of '
            f'{len(declared_domains)} declared in `AdvisorDomain` enum.'
        )
        out.append(
            f'- **Expertise distribution:** '
            + ', '.join(f'`{k}`={v}' for k, v in by_expertise.most_common())
            + '.'
        )
        out.append('')
        out.append(
            "> Advisors are dataclasses, not classes — the 'what do they do' "
            "answer comes from `background`, `specializations`, and "
            "`consultation_types`. The audit surfaces those fields verbatim."
        )
        out.append('')

        if findings:
            out.append('## Findings')
            out.append('')
            for f in findings:
                out.append(f'- {f}')
            out.append('')

        # Domain distribution
        out.append('## Advisors by domain')
        out.append('')
        out.append('| Domain | Advisors |')
        out.append('|---|---:|')
        for domain, n in by_domain.most_common():
            names = sorted(r['name'] for r in rows if r['domain'] == domain)
            out.append(f'| `{domain}` | {n} — {", ".join(names)} |')
        out.append('')

        # Named figures roster
        named = [r for r in rows if r['is_named_figure']]
        if named:
            out.append(f'## Named figures ({len(named)})')
            out.append('')
            out.append('| Name | Title | Domain | Expertise | Years |')
            out.append('|---|---|---|:-:|---:|')
            for r in sorted(named, key=lambda r: r['name']):
                out.append(
                    f'| {r["name"]} | {r["title"]} | `{r["domain"]}` | '
                    f'`{r["expertise_level"]}` | {r["years_experience"]} |'
                )
            out.append('')

        # Domain specialists roster
        specialists = [r for r in rows if not r['is_named_figure']]
        if specialists:
            out.append(f'## Domain specialists ({len(specialists)})')
            out.append('')
            out.append('| Name | Title | Domain | Expertise | Years |')
            out.append('|---|---|---|:-:|---:|')
            for r in sorted(specialists, key=lambda r: (r['domain'], r['name'])):
                out.append(
                    f'| {r["name"]} | {r["title"]} | `{r["domain"]}` | '
                    f'`{r["expertise_level"]}` | {r["years_experience"]} |'
                )
            out.append('')

        # Detail appendix
        out.append('## Detail appendix')
        out.append('')
        out.append(
            "One block per advisor. Background + specializations + "
            "achievements + decision frameworks together describe what each "
            "advisor brings to a consultation."
        )
        out.append('')
        for r in rows:
            heading = f'### `{r["id"]}` — {r["name"]}'
            if r['is_named_figure']:
                heading += ' _(named figure)_'
            out.append(heading)
            out.append('')
            out.append(
                f'**{r["title"]}** · **Domain:** `{r["domain"]}` · '
                f'**Expertise:** `{r["expertise_level"]}` · '
                f'**Experience:** {r["years_experience"]} years'
            )
            out.append('')
            if r['background']:
                out.append(f'**Background:** {r["background"]}')
                out.append('')
            if r['specializations']:
                out.append(
                    '**Specializations:** '
                    + ', '.join(f'`{s}`' for s in r['specializations'])
                )
                out.append('')
            if r['consultation_types']:
                out.append(
                    '**Consultation types:** '
                    + ', '.join(f'`{c}`' for c in r['consultation_types'])
                )
                out.append('')
            if r['decision_frameworks']:
                out.append(
                    '**Decision frameworks:** '
                    + ', '.join(f'`{f}`' for f in r['decision_frameworks'])
                )
                out.append('')
            if r['key_achievements']:
                out.append('**Key achievements:**')
                for a in r['key_achievements']:
                    out.append(f'- {a}')
                out.append('')
            if r['certifications']:
                out.append(
                    '**Certifications:** '
                    + ', '.join(r['certifications'])
                )
                out.append('')

        return '\n'.join(out) + '\n'
