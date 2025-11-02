#!/usr/bin/env python3
import argparse, re
from pathlib import Path
from typing import List, Tuple, Dict

# --- helpers to normalize dynamic bits like IDs, UUIDs, slugs ---
DYN_SEG_RE = re.compile(r"""
    (?:
        \d{1,20} |                                     # ints
        [0-9a-fA-F]{8}-[0-9a-fA-F]{4}-                # uuid-ish
        [0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12} |
        [A-Za-z0-9_-]{6,}                              # generic slug
    )
""", re.VERBOSE)

def norm_url(u: str) -> str:
    u = u.split("?")[0].rstrip("/")
    if not u.startswith("/"):
        u = "/" + u
    # replace each path segment that looks dynamic with a placeholder
    parts = [p for p in u.split("/") if p != ""]
    normed = []
    for p in parts:
        if DYN_SEG_RE.fullmatch(p):
            normed.append("<var>")
        else:
            normed.append(p)
    return "/" + "/".join(normed)

# --- scan templates: capture file+line + literal and normalized URL ---
ATTR_PATTERNS = [
    r'href=["\'](?P<u>/[^"\']+)["\']',
    r'action=["\'](?P<u>/[^"\']+)["\']',
    r'data-url=["\'](?P<u>/[^"\']+)["\']',
    r'fetch\(\s*["\'](?P<u>/[^"\']+)["\']',
    r'axios\.(?:get|post|put|patch|delete)\(\s*["\'](?P<u>/[^"\']+)["\']',
]
ATTR_RES = [re.compile(p) for p in ATTR_PATTERNS]
DJ_TAG_URL = re.compile(r"""{%\s*url\s+['"](?P<name>[a-zA-Z0-9_:\-\.]+)['"][^%]*%}""")

def scan_templates(tpl_root: Path, api_prefix: str):
    hits: List[Dict] = []
    names = set()
    for p in tpl_root.rglob("*.html"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines, start=1):
            for rx in ATTR_RES:
                for m in rx.finditer(line):
                    u = m.group("u").split("?")[0]
                    if u.startswith(api_prefix):
                        hits.append({
                            "file": str(p), "line": i,
                            "url": u.rstrip("/"),
                            "norm": norm_url(u)
                        })
            for m in DJ_TAG_URL.finditer(line):
                names.add(m.group("name"))
    return hits, names

# --- scan backend: build normalized exemplars from path()/re_path()/router.register() ---
DJ_PATH = re.compile(r"""path\(\s*['"](?P<route>[^'"]+)['"]\s*,\s*[^,]+(?:,\s*name=['"](?P<name>[^'"]+)['"])?""")
DJ_REPATH = re.compile(r"""re_path\(\s*(?:r|rf|fr)?['"](?P<route>[^'"]+)['"]\s*,\s*[^,]+(?:,\s*name=['"](?P<name>[^'"]+)['"])?""")
DJ_ROUTER = re.compile(r"""router\.register\(\s*['"](?P<prefix>[^'"]+)['"]\s*,\s*(?P<viewset>[A-Za-z_][A-Za-z0-9_]*)\s*(?:,\s*basename=['"](?P<basename>[^'"]+)['"])?\s*\)""")

def expand_path_route(route: str) -> List[str]:
    # convert django converters to <var>
    r = "/" + route.lstrip("/").rstrip("/")
    r = re.sub(r"<[^>]+>", "<var>", r)
    return [r]

def best_effort_from_regex(route: str) -> List[str]:
    # strip anchors and escapes, then turn capturing groups into <var>
    s = route.strip("^$")
    s = s.replace("\\/", "/")
    s = re.sub(r"\(\?P<[^>]+>[^)]+\)", "<var>", s)  # named groups
    s = re.sub(r"\([^)]*\)", "<var>", s)            # other groups
    if not s.startswith("/"):
        s = "/" + s
    return ["/" + "/".join(seg for seg in s.split("/") if seg)]  # cheap normalize

def scan_backend(be_root: Path, api_prefix: str):
    routes_norm: Set[str] = set()
    names_map: Dict[str, str] = {}
    drf_basenames = set()

    for p in be_root.rglob("*.py"):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for m in DJ_PATH.finditer(txt):
            route = m.group("route")
            fulls = expand_path_route(route)
            for f in fulls:
                if f.startswith(api_prefix):
                    routes_norm.add(f)
            if m.group("name"):
                names_map[m.group("name")] = "/" + route.lstrip("/").rstrip("/")

        for m in DJ_REPATH.finditer(txt):
            route = m.group("route")
            fulls = best_effort_from_regex(route)
            for f in fulls:
                if f.startswith(api_prefix):
                    routes_norm.add(f)
            if m.group("name"):
                names_map[m.group("name")] = best_effort_from_regex(route)[0]

        for m in DJ_ROUTER.finditer(txt):
            prefix = "/" + m.group("prefix").strip("/").rstrip("/")
            if prefix.startswith(api_prefix):
                routes_norm.add(prefix)              # list
                routes_norm.add(prefix + "/<var>")   # detail exemplar
                if m.group("basename"):
                    drf_basenames.add(m.group("basename"))

    return routes_norm, names_map, drf_basenames

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--templates", required=True)
    ap.add_argument("--backend", required=True)
    ap.add_argument("--api-prefix", default="/api")
    ap.add_argument("--report", default="endpoint_trace_report_detailed.md")
    ap.add_argument("--csv", default="endpoint_crossref.csv")
    args = ap.parse_args()

    tpl_hits, tpl_names = scan_templates(Path(args.templates), args.api_prefix)
    be_routes_norm, be_names, be_drf = scan_backend(Path(args.backend), args.api_prefix)

    # cross-ref: which template calls do NOT match any backend normalized route?
    missing = [h for h in tpl_hits if h["norm"] not in be_routes_norm]
    used = [h for h in tpl_hits if h["norm"] in be_routes_norm]
    unused_backend = sorted([r for r in be_routes_norm if r not in {h["norm"] for h in tpl_hits}])

    # write md
    out = []
    out.append(f"# Endpoint Trace (parameter-aware)")
    out.append(f"- API prefix: `{args.api_prefix}`")
    out.append(f"- Templates scanned: {len(set(h['file'] for h in tpl_hits))}")
    out.append(f"- Template calls found: {len(tpl_hits)}")
    out.append(f"- Backend routes (normalized): {len(be_routes_norm)}\n")

    out.append("## A. Missing in backend (after normalization)")
    if missing:
        for h in missing:
            out.append(f"- `{h['url']}` → norm `{h['norm']}` — {h['file']}:{h['line']}")
    else:
        out.append("- _none_")
    out.append("")

    out.append("## B. Backend routes unused in templates")
    if unused_backend:
        for r in unused_backend:
            out.append(f"- `{r}`")
    else:
        out.append("- _none_")
    out.append("")

    out.append("## C. Template `{% url %}` names (best-effort resolution)")
    if tpl_names:
        for n in sorted(tpl_names):
            tgt = be_names.get(n, "_unresolved_")
            out.append(f"- `{n}` → {tgt}")
    else:
        out.append("- _none_")

    Path(args.report).write_text("\n".join(out), encoding="utf-8")

    # write CSV of all hits (file,line,url,norm,matched)
    import csv
    with open(args.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file","line","url","norm","matched_backend"])
        be_set = set(be_routes_norm)
        for h in tpl_hits:
            w.writerow([h["file"], h["line"], h["url"], h["norm"], "yes" if h["norm"] in be_set else "no"])

    print(f"Wrote {args.report}")
    print(f"Wrote {args.csv}")

if __name__ == "__main__":
    main()
