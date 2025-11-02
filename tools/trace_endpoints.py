
import argparse, re
from pathlib import Path

FE_ATTR_PATTERNS = [
    r'href=["\'](?P<u>/[^"\']+)["\']',
    r'action=["\'](?P<u>/[^"\']+)["\']',
    r'data-url=["\'](?P<u>/[^"\']+)["\']',
    r'fetch\(\s*["\'](?P<u>/[^"\']+)["\']',
    r'axios\.(?:get|post|put|patch|delete)\(\s*["\'](?P<u>/[^"\']+)["\']',
]
DJ_TAG_URL = re.compile(r"""{%\s*url\s+['"](?P<name>[a-zA-Z0-9_:\-\.]+)['"][^%]*%}""")

DJ_PATH = re.compile(r"""path\(\s*['"](?P<route>[^'"]+)['"]\s*,\s*[^,]+(?:,\s*name=['"](?P<name>[^'"]+)['"])?""")
DJ_REPATH = re.compile(r"""re_path\(\s*(?:r|rf|fr)?['"](?P<route>[^'"]+)['"]\s*,\s*[^,]+(?:,\s*name=['"](?P<name>[^'"]+)['"])?""")
DJ_ROUTER = re.compile(r"""router\.register\(\s*['"](?P<prefix>[^'"]+)['"]\s*,\s*(?P<viewset>[A-Za-z_][A-Za-z0-9_]*)\s*(?:,\s*basename=['"](?P<basename>[^'"]+)['"])?\s*\)""")

def scan_templates(tpl_dir: Path, api_prefix: str):
    api_urls, named_urls = set(), set()
    attr_res = [re.compile(p) for p in FE_ATTR_PATTERNS]
    for p in tpl_dir.rglob("*.html"):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for r in attr_res:
            for m in r.finditer(txt):
                u = m.group("u")
                if u.startswith(api_prefix):
                    api_urls.add(u.split("?")[0].rstrip("/"))
        for m in DJ_TAG_URL.finditer(txt):
            named_urls.add(m.group("name"))
    return api_urls, named_urls

def scan_backend(backend_dir: Path, api_prefix: str):
    routes, names, drf = set(), {}, set()
    for p in backend_dir.rglob("*.py"):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in DJ_PATH.finditer(txt):
            route = "/" + m.group("route").lstrip("/")
            if route.startswith(api_prefix):
                routes.add(route.rstrip("/"))
                if m.group("name"):
                    names[m.group("name")] = route.rstrip("/")
        for m in DJ_REPATH.finditer(txt):
            route = m.group("route")
            route = route.strip("^$").replace("\\/", "/")
            route = "/" + route.lstrip("/")
            if route.startswith(api_prefix):
                routes.add(route.rstrip("/"))
                if m.group("name"):
                    names[m.group("name")] = route.rstrip("/")
        for m in DJ_ROUTER.finditer(txt):
            prefix = "/" + m.group("prefix").strip("/").rstrip("/")
            if prefix.startswith(api_prefix):
                routes.add(prefix)              # list
                routes.add(prefix + "/<id>")    # detail exemplar
                if m.group("basename"):
                    drf.add(m.group("basename"))
    return routes, names, drf

def write_report(out_path: Path, tpl_urls, tpl_names, be_routes, be_names, be_drf, api_prefix):
    lines = []
    lines.append(f"# Endpoint Trace Report\n")
    lines.append(f"**API prefix:** `{api_prefix}`\n")

    lines.append("## A. Template-discovered API URLs")
    lines += [f"- `{u}`" for u in sorted(tpl_urls)] or ["_none found_"]
    lines.append("")

    lines.append("## B. Template `{% url %}` names")
    if tpl_names:
        for n in sorted(tpl_names):
            target = be_names.get(n, "_unresolved_")
            lines.append(f"- `{n}` → {target}")
    else:
        lines.append("_none found_")
    lines.append("")

    lines.append("## C. Backend routes (urls.py + DRF router)")
    lines += [f"- `{r}`" for r in sorted(be_routes)] or ["_none found_"]
    if be_drf:
        lines.append("\n_Backbone (DRF router basenames):_ " + ", ".join(sorted(be_drf)))
    lines.append("")

    missing_in_backend = sorted(u for u in tpl_urls if u not in be_routes)
    unused_in_templates = sorted(r for r in be_routes if r not in tpl_urls)

    lines.append("## D. Potential issues")
    if missing_in_backend:
        lines.append("**Template calls not found in backend (literal match):**")
        lines += [f"- `{u}`" for u in missing_in_backend]
    else:
        lines.append("- No missing backend endpoints by literal match.")
    lines.append("")
    if unused_in_templates:
        lines.append("**Backend endpoints not referenced in templates (literal):**")
        lines += [f"- `{r}`" for r in unused_in_templates]
    else:
        lines.append("- No obviously unused backend endpoints by literal match.")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--templates", required=True, help="Path to Django templates root")
    ap.add_argument("--backend", required=True, help="Path to Django backend root (where urls live)")
    ap.add_argument("--api-prefix", default="/api", help="API prefix to track (default: /api)")
    ap.add_argument("--report", default="endpoint_trace_report.md")
    args = ap.parse_args()

    tpl_urls, tpl_names = scan_templates(Path(args.templates), args.api_prefix)
    be_routes, be_names, be_drf = scan_backend(Path(args.backend), args.api_prefix)
    write_report(Path(args.report), tpl_urls, tpl_names, be_routes, be_names, be_drf, args.api_prefix)

if __name__ == "__main__":
    main()