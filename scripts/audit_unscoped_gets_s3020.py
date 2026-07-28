"""S3020 Fold A audit — unscoped `Model.objects.get(id=...)` pattern candidate generator.

Ratified S3019 Fold-forward — S3020 Option A. The 4-session memory-palace
auth trajectory (S3016 F-2 audit → S3017 A.1 decorator → S3018 invariant →
S3019 A.2 predicate) closed ONE class of vulnerability. This audit checks
whether the same "unscoped .get() where a predicate exists" shape repeats
elsewhere across `core/views_*.py`.

**Candidate generator only.** Findings need hand-review — some views scope
the queryset via a helper, some intentionally allow superuser system-context
reads, and some are already-gated by `@superuser_required` decorators.

Method:
1. Enumerate the 6 canonical scope predicates + their target models
   (per `core/security/object_authz.py` public API).
2. For each model, grep `core/views_*.py` for patterns matching
   `<Model>.objects.*.get(...)` (both `get(id=)` and `get(pk=)` variants).
3. For each hit, check whether the same file contains a call to the
   corresponding `scope_queryset_<model>` predicate. If NOT, flag the
   line as a candidate.
4. Emit `docs/audits/UNSCOPED_GETS_S3020.md` with per-model breakdowns +
   `docs/audits/unscoped_gets_s3020.json` (machine-readable).

Usage:
    python manage.py shell < scripts/audit_unscoped_gets_s3020.py

Output:
    stdout: Markdown-ready summary
    docs/audits/unscoped_gets_s3020.json (per-hit rows)

Distinct from `PUBLIC_PATHS_BARE_PREFIX_AUDIT_S3016.md` — that audit was
about silent-empty reads under a bare-prefix bypass. This one is about
predicate-exists-but-not-called; the two failure modes intersect but
aren't identical.
"""
import json
import re
from pathlib import Path


# 6-predicate surface as of S3019 (ADR-0008). Each row:
# (predicate_name, model_name, model_regex).
# model_regex is used to grep for `Model.objects` patterns; we widen a bit
# to also catch `Model.objects.defer(...).get(...)` and `Model.objects.filter(...).get(...)`
# via the same base match.
PREDICATES = [
    ("scope_queryset_deliverable", "Deliverable"),
    ("scope_queryset_chat_conversation", "ChatConversation"),
    ("scope_queryset_initiative", "Initiative"),
    ("scope_queryset_agent_execution", "AgentExecution"),
    ("scope_queryset_document", "Document"),
    ("scope_queryset_agent_memory", "AgentMemory"),
]

VIEWS_ROOT = Path("core")
OUT_JSON = Path("docs/audits/unscoped_gets_s3020.json")


def find_view_files():
    """Return all `core/views*.py` files (top-level + subpackage variants)."""
    files = list(VIEWS_ROOT.glob("views*.py"))
    files += list(VIEWS_ROOT.glob("views/*.py"))
    files += list(VIEWS_ROOT.glob("agents/views_*.py"))
    return sorted(set(files))


def audit_file(path: Path):
    """Return list of candidate finding dicts for one view file."""
    source = path.read_text()
    hits = []
    for pred_name, model_name in PREDICATES:
        # Widened regex: catches both `Model.objects.get(...)` and
        # `Model.objects.<chain>.get(...)` where chain has no whitespace-
        # broken newlines. Multiline forms (parenthesized chains split
        # across lines) are missed — noted as a scope caveat.
        model_pattern = re.compile(
            rf"\b{model_name}\.objects\.[a-zA-Z0-9_.()\[\]',=\-\s]*?\.get\s*\(",
            re.MULTILINE,
        )
        # Simpler pattern for `Model.objects.get(...)` no-chain shape:
        direct_pattern = re.compile(
            rf"\b{model_name}\.objects\.get\s*\(",
            re.MULTILINE,
        )
        # Predicate presence anywhere in the file:
        pred_present = pred_name in source
        for pat in (direct_pattern, model_pattern):
            for m in pat.finditer(source):
                line_no = source[: m.start()].count("\n") + 1
                # Skip if predicate is present in the same file — that's a
                # signal the view already uses the scope path. Hand-review
                # can still catch cases where the predicate is called on a
                # DIFFERENT model instance in the same file. This is the
                # 'candidate generator' vs 'proof of leak' distinction.
                if pred_present:
                    continue
                # Extract a small source snippet around the match for
                # human review.
                snippet_start = source.rfind("\n", 0, m.start()) + 1
                snippet_end = source.find("\n", m.end())
                snippet = source[snippet_start:snippet_end].strip()
                hits.append(
                    {
                        "predicate": pred_name,
                        "model": model_name,
                        "file": str(path),
                        "line": line_no,
                        "snippet": snippet,
                        "predicate_in_file": pred_present,
                    }
                )
    # De-dup within a file (both regex patterns can match the same line).
    seen = set()
    unique = []
    for h in hits:
        key = (h["file"], h["line"], h["model"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(h)
    return unique


def audit_all():
    findings = []
    files = find_view_files()
    for path in files:
        findings.extend(audit_file(path))
    return findings, files


findings, files_scanned = audit_all()

# Group by model + by file for reporting.
by_model = {}
by_file = {}
for h in findings:
    by_model.setdefault(h["model"], []).append(h)
    by_file.setdefault(h["file"], []).append(h)

OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
OUT_JSON.write_text(json.dumps(findings, indent=2))

print("=== S3020 Fold A candidate list (hand-review required) ===")
print(f"View files scanned: {len(files_scanned)}")
print(f"Total candidate hits: {len(findings)}")
print()
print("By model:")
for model in sorted(by_model.keys()):
    print(f"  {model}: {len(by_model[model])} hits")
print()
print("Top files (≥3 hits):")
for f, hs in sorted(by_file.items(), key=lambda x: -len(x[1])):
    if len(hs) < 3:
        continue
    print(f"  {f}: {len(hs)} hits")
print()
print("First 10 candidates (for spot-check):")
for h in findings[:10]:
    print(f"  {h['file']}:{h['line']}  {h['model']}  {h['snippet'][:80]}")
print()
print(f"Full JSON: {OUT_JSON}")
