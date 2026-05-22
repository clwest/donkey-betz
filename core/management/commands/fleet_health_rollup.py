"""fleet_health_rollup — ping every Dockerized fleet app and report up/down.

Reads `config/external_repos/*.json`, filters to entries with
`docker.enabled = true`, hits each app's `api_url + healthchecks.api.path`,
and reports a one-line-per-app status table. Designed for "what's broken
right now?" in ~2 seconds.

The probe function (`probe_fleet`) is also called by the
`fleet_health` PA tool handler — see core/services/td_handlers_core.py.
Keep this file the single source of truth for the probe logic.

Usage:
    python manage.py fleet_health_rollup
    python manage.py fleet_health_rollup --json
    python manage.py fleet_health_rollup --repo mentorforge
    python manage.py fleet_health_rollup --timeout 5

Exit codes:
    0 — every probed app is healthy
    1 — at least one app failed (down, timeout, unexpected status)
    2 — no Docker-enabled fleet apps found (likely misconfiguration)
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

CONFIG_DIR_REL = Path("config/external_repos")
DEFAULT_TIMEOUT_S = 3.0


def _load_fleet_configs(repo_filter: str | None) -> list[tuple[str, dict]]:
    """Return [(slug, config_dict)] for every fleet repo with docker.enabled.

    `slug` is the basename without `.json` extension. Skips repos whose
    JSON has no `docker` block or `docker.enabled` is false.
    """
    root = Path(settings.BASE_DIR) / CONFIG_DIR_REL
    if not root.is_dir():
        raise CommandError(f"config dir not found: {root}")
    out: list[tuple[str, dict]] = []
    for path in sorted(root.glob("*.json")):
        slug = path.stem
        if repo_filter and slug != repo_filter:
            continue
        try:
            cfg = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            out.append((slug, {"_load_error": f"invalid JSON: {e}"}))
            continue
        docker = cfg.get("docker") or {}
        if not docker.get("enabled"):
            continue
        out.append((slug, cfg))
    return out


def _probe_one(slug: str, cfg: dict, timeout_s: float) -> dict[str, Any]:
    """Hit api_url + healthcheck path; return a status row."""
    if cfg.get("_load_error"):
        return {
            "slug": slug, "ok": False, "status": "CONFIG_ERROR",
            "detail": cfg["_load_error"], "latency_ms": None,
        }
    docker = cfg["docker"]
    api_url = (docker.get("base_urls") or {}).get("api_url")
    hc = (docker.get("healthchecks") or {}).get("api") or {}
    path = hc.get("path", "/api/health")
    expected = hc.get("expect_status", [200])
    if not api_url:
        return {
            "slug": slug, "ok": False, "status": "NO_API_URL",
            "detail": "docker.base_urls.api_url missing",
            "latency_ms": None,
        }
    url = api_url.rstrip("/") + path

    started = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=timeout_s) as resp:
            code = resp.status
            latency_ms = int((time.monotonic() - started) * 1000)
    except urllib.error.HTTPError as e:
        code = e.code
        latency_ms = int((time.monotonic() - started) * 1000)
    except (urllib.error.URLError, TimeoutError) as e:
        return {
            "slug": slug, "ok": False, "status": "UNREACHABLE",
            "detail": f"{type(e).__name__}: {getattr(e, 'reason', e)}",
            "latency_ms": int((time.monotonic() - started) * 1000),
            "url": url,
        }

    ok = code in expected
    return {
        "slug": slug, "ok": ok, "status": "HEALTHY" if ok else "UNHEALTHY",
        "detail": f"HTTP {code} (expected {expected})" if not ok else "",
        "latency_ms": latency_ms,
        "url": url,
    }


def probe_fleet(
    repo_filter: str | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """Probe every Dockerized fleet app and return a structured payload.

    This is the public entrypoint shared between the mgmt command and the
    `fleet_health` PA tool handler. Returns:
        {
          "generated_at": "ISO-8601 UTC",
          "overall_status": "healthy" | "degraded" | "empty",
          "apps": [{slug, status, ok, latency_ms, detail, url?}, ...],
          "probed_count": int,
          "healthy_count": int,
        }
    """
    from datetime import datetime, timezone as dt_timezone

    configs = _load_fleet_configs(repo_filter)
    rows = [_probe_one(slug, cfg, timeout_s) for slug, cfg in configs]
    healthy = sum(1 for r in rows if r["ok"])
    overall = (
        "empty" if not rows
        else "healthy" if healthy == len(rows)
        else "degraded"
    )
    return {
        "generated_at": datetime.now(dt_timezone.utc).isoformat(timespec="seconds"),
        "overall_status": overall,
        "apps": rows,
        "probed_count": len(rows),
        "healthy_count": healthy,
    }


def _render_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "(no fleet apps to probe)\n"
    width = max(len(r["slug"]) for r in rows)
    lines = [
        f"{'app':<{width}}  {'status':<13}  {'latency':>9}  detail",
        f"{'-' * width}  {'-' * 13}  {'-' * 9}  {'-' * 40}",
    ]
    for r in rows:
        mark = "✓" if r["ok"] else "✗"
        lat = f"{r['latency_ms']}ms" if r["latency_ms"] is not None else "—"
        lines.append(
            f"{r['slug']:<{width}}  {mark} {r['status']:<11}  {lat:>9}  {r.get('detail', '')}"
        )
    return "\n".join(lines) + "\n"


class Command(BaseCommand):
    help = (
        "Ping each Dockerized fleet app's health endpoint and report up/down. "
        "Reads docker.base_urls.api_url + docker.healthchecks.api.path from "
        "config/external_repos/*.json."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--json", action="store_true",
            help="Emit a JSON array instead of the human table.",
        )
        parser.add_argument(
            "--repo", default=None,
            help="Probe a single repo by slug (e.g. --repo mentorforge).",
        )
        parser.add_argument(
            "--timeout", type=float, default=DEFAULT_TIMEOUT_S,
            help=f"Per-request timeout in seconds (default {DEFAULT_TIMEOUT_S}).",
        )

    def handle(self, *args, **opts):
        result = probe_fleet(opts["repo"], opts["timeout"])
        rows = result["apps"]

        if not rows:
            msg = (
                f"no fleet apps to probe"
                + (f" matching --repo {opts['repo']}" if opts["repo"] else
                   " (no config/external_repos/*.json has docker.enabled=true)")
            )
            if opts["json"]:
                self.stdout.write(json.dumps({**result, "error": msg}))
            else:
                self.stderr.write(self.style.WARNING(msg))
            sys.exit(2)

        if opts["json"]:
            self.stdout.write(json.dumps(result, indent=2))
        else:
            self.stdout.write(_render_table(rows))

        sys.exit(0 if result["overall_status"] == "healthy" else 1)
