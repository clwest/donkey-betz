#!/usr/bin/env python3
import csv, hashlib, os, re
from pathlib import Path

CSV_PATH = Path("endpoint_crossref.csv")
OUT_DIR = Path("backend/auto_endpoints")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def fn_name_for(route: str) -> str:
    # stable function name from normalized route
    base = re.sub(r'[^a-z0-9]+', '_', route.strip('/').lower())
    h = hashlib.md5(route.encode()).hexdigest()[:8]
    return f"stub_{base or 'root'}_{h}"

def django_path_pattern(route: str) -> str:
    """
    Convert normalized route (e.g., /api/users/<var>/notes/<var>)
    into a Django path pattern with slug converters:
    /api/users/<slug:param1>/notes/<slug:param2>
    """
    parts = [p for p in route.strip("/").split("/") if p]
    out, i = [], 1
    for p in parts:
        if p == "<var>":
            out.append(f"<slug:param{i}>")
            i += 1
        else:
            out.append(p)
    return "/".join(out) + "/"

def main():
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV not found at {CSV_PATH}. Run trace_endpoints_plus.py first.")

    missing = []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if (row.get("matched_backend") or "").strip().lower() != "yes":
                norm = (row.get("norm") or "").strip()
                url = (row.get("url") or "").strip()
                if norm.startswith("/api"):
                    missing.append(norm)

    missing = sorted(set(missing))
    if not missing:
        print("No missing /api routes detected — nothing to generate.")
        return

    # build views.py
    views_lines = [
        "from django.http import JsonResponse",
        "from django.views.decorators.http import require_http_methods",
        "",
    ]
    for route in missing:
        fn = fn_name_for(route)
        views_lines += [
            "@require_http_methods(['GET','POST','PUT','PATCH','DELETE'])",
            f"def {fn}(request, *args, **kwargs):",
            "    return JsonResponse({",
            f"        'status': 'stub',",
            f"        'route': request.path,",
            f"        'method': request.method,",
            f"        'params': kwargs,",
            "    })",
            "",
        ]

    (OUT_DIR / "views.py").write_text("\n".join(views_lines), encoding="utf-8")

    # build urls.py
    from_imports = ["from django.urls import path", "from . import views", "", "urlpatterns = ["]
    url_lines = []
    for route in missing:
        pat = django_path_pattern(route)
        fn = fn_name_for(route)
        url_lines.append(f"    path('{pat}', views.{fn}, name='{fn}'),")
    tail = ["]", ""]
    (OUT_DIR / "urls.py").write_text("\n".join(from_imports + url_lines + tail), encoding="utf-8")

    print(f"Generated {OUT_DIR/'views.py'}")
    print(f"Generated {OUT_DIR/'urls.py'}\n")
    print("👉 Add this include to your ROOT urls.py (usually backend/core/urls.py):\n")
    print("    from django.urls import include, path")
    print("    urlpatterns += [")
    print("        path('', include('auto_endpoints.urls')),  # temporary stubs")
    print("    ]\n")
    print("Then restart Django and click through the UI — you’ll get JSON stubs where endpoints were missing.")
if __name__ == '__main__':
    main()
