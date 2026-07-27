"""
Index actionable findings from docs/research/ into DocResearchFinding rows.

S2989 Phase B — narrow-scope v1 ingester. Walks:
  - docs/research/domains/**/*_canonical_summary.md
  - docs/research/domains/**/*_audit.md
  - docs/research/implementation/IMPLEMENTATION_DEBT.md

Skips (v1):
  - implementation/BACKLOG.md            (needs its own IOS-schema parser)
  - implementation/*/                    (design-prep subfolders, noisier)
  - implementation/RATIFICATION_*.md     (history log, not open findings)
  - platform/, process/, tools/          (design-space, less actionable)
  - domains/*_scoping.md                 (parent-scoping docs, noisier)

Idempotent: upserts by `(doc_path, text_hash)`. Findings that disappear
from source are NOT deleted — `last_seen_at` stays stale so status
history is preserved.

Usage:
    python manage.py index_doc_research_findings [--dry-run] [--verbose]

Rigby SIGN Cycle 1 folds baked in:
- F-B3: narrow v1 scope enforced here (not in the model)
- F-B2: each finding carries `confidence` + `source_heading` for downstream
  filtering
"""
from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models_audit_findings import DocResearchFinding

logger = logging.getLogger(__name__)


# Whitelisted H2 section titles that indicate a bullet list of findings.
# Match on the trailing header text (after `## N.` numbering) case-insensitively.
FINDING_SECTION_PATTERNS = [
    r"^known drift$",
    r"^known technical debt$",
    r"^boundary violations$",
    r"^duplicate or overlapping systems$",
    r"^ownership gaps$",
    r"^recommended future research$",
    r"^recommendations?$",
    r"^follow[- ]?on research queue$",
    r"^follow[- ]?ups?$",
    r"^open (items?|questions?|follow[- ]?ups?)$",
    r"^next actions?$",
    r"^unresolved unknowns$",
    r"^anchor[- ]update recommendations?$",
    r"^to[- ]?dos?$",
    r"^action items?$",
]
FINDING_SECTION_RE = re.compile("|".join(FINDING_SECTION_PATTERNS), re.IGNORECASE)

# Confidence heuristic — sections that are more "queued action" than
# "diagnostic observation" get higher confidence.
HIGH_CONFIDENCE_HEADINGS = {
    "next actions", "follow-on research queue", "follow-ups", "follow ups",
    "recommendations", "action items", "todos", "to-dos", "to dos",
    "open follow-ups", "open follow ups", "recommended future research",
}
LOW_CONFIDENCE_HEADINGS = {
    "boundary violations", "known drift", "duplicate or overlapping systems",
    "unresolved unknowns",
}


@dataclass
class ParsedFinding:
    doc_path: str
    domain_slug: str
    source_type: str
    source_heading: str
    text: str
    confidence: str
    tags: List[str]
    metadata: dict


def _strip_leading_numbering(header: str) -> str:
    """Turn '## 19. Recommended Future Research' → 'Recommended Future Research'."""
    stripped = header.lstrip("# ").strip()
    m = re.match(r"^\d+(?:\.\d+)*\.?\s*(.*)$", stripped)
    return (m.group(1) if m else stripped).strip()


def _text_hash(doc_path: str, text: str) -> str:
    h = hashlib.sha256()
    h.update(doc_path.encode("utf-8"))
    h.update(b"\x00")
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def _confidence_for(heading_bare: str) -> str:
    lower = heading_bare.lower()
    if lower in HIGH_CONFIDENCE_HEADINGS:
        return DocResearchFinding.CONFIDENCE_HIGH
    if lower in LOW_CONFIDENCE_HEADINGS:
        return DocResearchFinding.CONFIDENCE_LOW
    return DocResearchFinding.CONFIDENCE_MEDIUM


def _iter_target_files(base_dir: Path) -> Iterable[Path]:
    """Yield the narrow v1 scope of source files."""
    research_root = base_dir / "docs" / "research"
    if not research_root.exists():
        return

    domains_root = research_root / "domains"
    if domains_root.exists():
        for candidate in sorted(domains_root.rglob("*.md")):
            name = candidate.name
            if name.endswith("_canonical_summary.md") or name.endswith("_audit.md"):
                yield candidate

    impl_debt = research_root / "implementation" / "IMPLEMENTATION_DEBT.md"
    if impl_debt.exists():
        yield impl_debt


def _domain_slug_from_path(path: Path, base_dir: Path) -> str:
    """docs/research/domains/pa/2699_… → 'pa'; implementation/... → 'implementation'."""
    try:
        rel = path.resolve().relative_to(base_dir.resolve())
    except ValueError:
        return ""
    parts = rel.parts
    if len(parts) >= 4 and parts[0] == "docs" and parts[1] == "research" and parts[2] == "domains":
        return parts[3]
    if len(parts) >= 3 and parts[0] == "docs" and parts[1] == "research":
        return parts[2]
    return ""


def _rel_doc_path(path: Path, base_dir: Path) -> str:
    try:
        return str(path.resolve().relative_to(base_dir.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def _extract_bullets_under_heading(lines: List[str], start_idx: int) -> List[str]:
    """Grab consecutive bullet lines starting after start_idx, stopping at
    the next H1/H2/H3 header (or EOF).

    Bullets are lines matching:
        - text
        * text
        1. text
    Multi-line bullet continuations (indent > 2 spaces) are appended.
    """
    out: List[str] = []
    current: Optional[str] = None
    for line in lines[start_idx + 1 :]:
        stripped = line.rstrip()
        if not stripped:
            if current is not None:
                out.append(current)
                current = None
            continue
        if re.match(r"^#{1,3}\s", stripped):
            break
        m = re.match(r"^\s*(?:[-*]|\d+\.)\s+(.+)$", stripped)
        if m:
            if current is not None:
                out.append(current)
            current = m.group(1).strip()
            continue
        # continuation line for a bullet (indented text under a bullet)
        if current is not None and re.match(r"^\s{2,}\S", line):
            current += " " + stripped.strip()
            continue
        # non-bullet content — reset current
        if current is not None:
            out.append(current)
            current = None
    if current is not None:
        out.append(current)
    # Post-clean: drop trivially short entries and markdown-noise-only entries.
    return [
        b.strip() for b in out
        if len(b.strip()) >= 20 and not b.strip().startswith("(")
    ]


def _parse_finding_sections(
    doc_path_rel: str,
    domain_slug: str,
    source_type: str,
    content: str,
) -> List[ParsedFinding]:
    lines = content.split("\n")
    findings: List[ParsedFinding] = []
    for i, line in enumerate(lines):
        m = re.match(r"^(#{2,3})\s+(.+)$", line)
        if not m:
            continue
        header_bare = _strip_leading_numbering(line)
        if not FINDING_SECTION_RE.match(header_bare):
            continue
        bullets = _extract_bullets_under_heading(lines, i)
        confidence = _confidence_for(header_bare)
        for bullet_text in bullets:
            findings.append(
                ParsedFinding(
                    doc_path=doc_path_rel,
                    domain_slug=domain_slug,
                    source_type=source_type,
                    source_heading=header_bare,
                    text=bullet_text,
                    confidence=confidence,
                    tags=[domain_slug] if domain_slug else [],
                    metadata={"line_number": i + 1},
                )
            )
    return findings


def _parse_implementation_debt(doc_path_rel: str, content: str) -> List[ParsedFinding]:
    """Special-parse IMPLEMENTATION_DEBT.md — one finding per ACTIVE IDBT block.

    Structure:
        ### `IDBT-NNNN` — <debt_type> <severity> — <one-line summary>
        | Field | Value |
        |-------|-------|
        | `debt_id` | `IDBT-NNNN` |
        | ... |
        | `description` | <long form description> |
        | ... |
        | `status` | `ACTIVE` |

    Only status=ACTIVE rows become findings; text = description field.
    """
    findings: List[ParsedFinding] = []
    lines = content.split("\n")

    header_re = re.compile(r"^###\s+`(IDBT-\d+)`\s+—\s+(.+?)$")
    field_re = re.compile(r"^\|\s*`?([a-z_ ]+?)`?\s*\|\s*(.+?)\s*\|$")

    i = 0
    while i < len(lines):
        header_match = header_re.match(lines[i])
        if not header_match:
            i += 1
            continue
        idbt_id = header_match.group(1)
        one_liner = header_match.group(2).strip()

        # Walk the following block until next header or EOF, collecting field rows.
        fields: dict[str, str] = {}
        j = i + 1
        while j < len(lines):
            if re.match(r"^#{2,3}\s", lines[j]):
                break
            fm = field_re.match(lines[j])
            if fm:
                fields[fm.group(1).strip().lower()] = fm.group(2).strip()
            j += 1

        status_raw = (fields.get("status") or "").strip("`").upper()
        if status_raw == "ACTIVE":
            description = fields.get("description") or one_liner
            # Strip surrounding backticks / markdown noise from description
            description = description.strip()
            if len(description) >= 20:
                findings.append(
                    ParsedFinding(
                        doc_path=doc_path_rel,
                        domain_slug="implementation",
                        source_type=DocResearchFinding.SOURCE_TYPE_IMPLEMENTATION_DEBT,
                        source_heading=f"{idbt_id} — {one_liner}",
                        text=description,
                        confidence=DocResearchFinding.CONFIDENCE_HIGH,
                        tags=["implementation", "idbt", idbt_id.lower()],
                        metadata={
                            "idbt_id": idbt_id,
                            "one_liner": one_liner[:200],
                            "line_number": i + 1,
                            "debt_type": (fields.get("debt_type") or "").strip("`"),
                            "severity": (fields.get("severity") or "").strip("`"),
                        },
                    )
                )
        i = j

    return findings


def _source_type_for(path: Path) -> str:
    name = path.name
    if name == "IMPLEMENTATION_DEBT.md":
        return DocResearchFinding.SOURCE_TYPE_IMPLEMENTATION_DEBT
    if name.endswith("_canonical_summary.md"):
        return DocResearchFinding.SOURCE_TYPE_CANONICAL_SUMMARY
    return DocResearchFinding.SOURCE_TYPE_AUDIT


class Command(BaseCommand):
    help = "Index actionable findings from docs/research/ into DocResearchFinding."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse but do not write to DB.",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Print per-doc summary counts.",
        )

    def handle(self, *args, **options) -> None:
        base_dir = Path(settings.BASE_DIR)
        dry_run: bool = bool(options.get("dry_run"))
        verbose: bool = bool(options.get("verbose"))

        stats = {
            "files_scanned": 0,
            "findings_parsed": 0,
            "created": 0,
            "updated": 0,
            "skipped_dup": 0,
        }

        for path in _iter_target_files(base_dir):
            stats["files_scanned"] += 1
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(f"read failed: {path}: {exc}")
                continue

            doc_path_rel = _rel_doc_path(path, base_dir)
            domain_slug = _domain_slug_from_path(path, base_dir)
            source_type = _source_type_for(path)

            if source_type == DocResearchFinding.SOURCE_TYPE_IMPLEMENTATION_DEBT:
                parsed = _parse_implementation_debt(doc_path_rel, content)
            else:
                parsed = _parse_finding_sections(
                    doc_path_rel, domain_slug, source_type, content
                )
            stats["findings_parsed"] += len(parsed)

            if verbose:
                self.stdout.write(f"{doc_path_rel}: {len(parsed)} finding(s)")

            if dry_run:
                continue

            for pf in parsed:
                hash_ = _text_hash(pf.doc_path, pf.text)
                with transaction.atomic():
                    obj, created = DocResearchFinding.objects.update_or_create(
                        doc_path=pf.doc_path,
                        text_hash=hash_,
                        defaults={
                            "domain_slug": pf.domain_slug,
                            "source_type": pf.source_type,
                            "source_heading": pf.source_heading[:500],
                            "text": pf.text,
                            "confidence": pf.confidence,
                            "tags": pf.tags,
                            "metadata": pf.metadata,
                        },
                    )
                    if created:
                        stats["created"] += 1
                    else:
                        stats["updated"] += 1

        self.stdout.write(
            f"Files: {stats['files_scanned']}  "
            f"Findings parsed: {stats['findings_parsed']}  "
            f"Created: {stats['created']}  Updated: {stats['updated']}"
            + (" (dry-run)" if dry_run else "")
        )
