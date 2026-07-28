"""S3016 Fold G audit — candidate generator for PUBLIC_PATHS scoped-read risk.

**Candidate generator only.** This script identifies PUBLIC_PATHS prefixes
that hit views whose source contains one of the canonical scope predicate
names. It does NOT prove anonymous behavior is silent-empty vs loud
401/403 — that classification requires hand-review of each candidate (an
earlier `@superuser_required` decorator, for instance, will loudly reject
anon before the scope predicate ever runs).

Motivation (context): PR #3714 (S3015 hotfix) exposed the failure mode we
want to catch — `/api/initiatives/` sat as a bare prefix in PUBLIC_PATHS
and also caught the list endpoint, which was scoped by
`scope_queryset_initiative` and returned .none() for Token-auth-only
browsers. Rigby T0 REVISE 2: narrow the audit to prefixes whose matched
endpoints could exhibit that empty-200 silent-degradation.

Distinct from `PUBLIC_PATHS_AUDIT_S2789` (which audited mutation gating).

Usage:
    python manage.py shell < scripts/audit_public_paths_scoped_reads_s3016.py

Output:
    docs/audits/public_paths_bare_prefix_audit_s3016.json  (machine-readable
        candidate list — hand-review still required)
    Prints a Markdown-ready summary to stdout.
"""
import json
import inspect
from pathlib import Path

from django.urls import get_resolver

from core.auth_middleware import UnifiedTokenAuthenticationMiddleware


SCOPE_PREDICATES = [
    "scope_queryset_deliverable",
    "scope_queryset_chat_conversation",
    "scope_queryset_initiative",
    "scope_queryset_agent_execution",
    "scope_queryset_document",
]


def unwrap_view(view):
    """Deep-unwrap decorators and DRF wrappers to find the real callable."""
    seen = set()
    while True:
        vid = id(view)
        if vid in seen:
            return view
        seen.add(vid)
        if hasattr(view, "view_class"):
            view = view.view_class
            continue
        if hasattr(view, "__wrapped__"):
            view = view.__wrapped__
            continue
        return view


def get_source(view):
    """Return (file, lineno, source) or (None, None, '')."""
    try:
        source = inspect.getsource(view)
        file = inspect.getsourcefile(view)
        _, lineno = inspect.getsourcelines(view)
        return file, lineno, source
    except (TypeError, OSError):
        return None, None, ""


def walk_urlpatterns(patterns, prefix=""):
    for p in patterns:
        pattern = prefix + str(p.pattern)
        if hasattr(p, "url_patterns"):
            yield from walk_urlpatterns(p.url_patterns, pattern)
        else:
            yield pattern, p.callback


def matches_prefix(url_pattern: str, prefix: str) -> bool:
    """PUBLIC_PATHS startswith match — the middleware uses request.path.startswith(prefix).
    We normalize the URL pattern by stripping regex metacharacters at the head."""
    # Django patterns look like "^api/initiatives/" or "api/initiatives/<uuid:id>/action-items/"
    cleaned = url_pattern.lstrip("^")
    if not cleaned.startswith("/"):
        cleaned = "/" + cleaned
    return cleaned.startswith(prefix)


def audit():
    resolver = get_resolver()
    all_urls = list(walk_urlpatterns(resolver.url_patterns))
    public_paths = UnifiedTokenAuthenticationMiddleware.PUBLIC_PATHS

    findings = []
    for prefix in public_paths:
        matched = []
        for url, callback in all_urls:
            if not matches_prefix(url, prefix):
                continue
            view = unwrap_view(callback)
            file, lineno, source = get_source(view)
            uses_scope = [p for p in SCOPE_PREDICATES if p in source]
            if uses_scope:
                matched.append({
                    "url": url,
                    "view_name": getattr(view, "__qualname__", getattr(view, "__name__", str(view))),
                    "file": file.replace(str(Path.cwd()) + "/", "") if file else None,
                    "line": lineno,
                    "scope_predicates_called": uses_scope,
                })
        if matched:
            findings.append({
                "prefix": prefix,
                "matched_scoped_endpoints": matched,
            })
    return findings


results = audit()
out_path = Path("docs/audits/public_paths_bare_prefix_audit_s3016.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(results, indent=2, default=str))

print(f"\n=== Fold G candidate list (hand-review required) ===")
print(f"Prefixes with at least one candidate: {len(results)}")
print(f"Total candidate endpoints: {sum(len(r['matched_scoped_endpoints']) for r in results)}")
print(f"\nBy prefix:")
for r in results:
    print(f"\n{r['prefix']}")
    for m in r["matched_scoped_endpoints"]:
        preds = ",".join(m["scope_predicates_called"])
        print(f"  → {m['url']}  [{preds}]  {m['file']}:{m['line']}  {m['view_name']}")
print(f"\nJSON written to {out_path}")
