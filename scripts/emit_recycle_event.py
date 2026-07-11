"""S2768 N7: enrich recycle-all JSONL with worker PIDs before/after.

Wraps the `make recycle-all` target so the emitted event includes:
- pids_before: PID snapshot read from local pidfiles BEFORE `make restart` runs
- pids_after: PID snapshot read AFTER restart completes
- partial_recycle: True if any per-role PID survived the restart
- surviving_processes: list of role names whose PID did not rotate

Used by the Makefile as a two-phase wrapper:

    python scripts/emit_recycle_event.py snapshot > /tmp/recycle_pids_before.json
    make restart
    python scripts/emit_recycle_event.py emit --before /tmp/recycle_pids_before.json

No Django dependency — reads pidfiles as plain files so the recycle path
stays fast even after Django startup grows. See PLAYBOOK-7.4.4 and
docs/handoffs/SESSION_2768_RECYCLE_EMITTER_WORKER_PIDS_RATIFIED.md.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "logs" / "recycle_events.jsonl"

# Role name → pidfile path relative to repo root. Order defines the
# canonical role set for partial-recycle detection.
PIDFILES: dict[str, Path] = {
    "daphne": REPO_ROOT / ".daphne.pid",
    "celery_default": REPO_ROOT / ".celery.pid",
    "celery_pa": REPO_ROOT / ".celery-pa.pid",
    "celery_long_running": REPO_ROOT / ".celery-long-running.pid",
    "celery_broadcast": REPO_ROOT / ".celery-broadcast.pid",
    "celery_code_jobs": REPO_ROOT / ".celery-code-jobs.pid",
    "celery_beat": REPO_ROOT / ".celery-beat.pid",
}


def read_pid(pidfile: Path) -> int | None:
    """Return the PID recorded in ``pidfile`` or None if unreadable/missing."""
    try:
        text = pidfile.read_text().strip()
    except (FileNotFoundError, OSError):
        return None
    if not text:
        return None
    parts = text.split()
    if not parts:
        return None
    try:
        return int(parts[0])
    except ValueError:
        return None


def snapshot_pids() -> dict[str, int | None]:
    """Return {role: pid_or_None} for every known pidfile."""
    return {role: read_pid(path) for role, path in PIDFILES.items()}


def compute_partial(
    before: dict[str, int | None], after: dict[str, int | None]
) -> tuple[bool, list[str]]:
    """Return (partial_recycle, surviving_processes).

    A role is "surviving" if its before-PID is non-null and equal to its
    after-PID. `partial_recycle` is True if any role survived. Roles
    whose before-PID or after-PID is None (i.e. pidfile absent on one
    side) are NOT flagged — that's a start/stop transition, not a
    survivor. This keeps the signal specific to "process claimed
    restarted but kept the same PID."
    """
    surviving: list[str] = []
    for role in PIDFILES:
        pid_before = before.get(role)
        pid_after = after.get(role)
        if pid_before is None or pid_after is None:
            continue
        if pid_before == pid_after:
            surviving.append(role)
    return bool(surviving), surviving


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def head_sha() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return out.stdout.strip() or "unknown"
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return "unknown"


def cmd_snapshot(args: argparse.Namespace) -> int:
    del args  # unused; argparse dispatch always passes the namespace
    json.dump(snapshot_pids(), sys.stdout)
    sys.stdout.write("\n")
    return 0


def cmd_emit(args: argparse.Namespace) -> int:
    before_path = Path(args.before)
    before: dict[str, int | None] = {}
    try:
        before = json.loads(before_path.read_text())
    except (FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        # Fail-open: emit a legacy-shape event so PLAYBOOK-7.4.4 evidence
        # still lands. Downstream reader tolerates absent fields.
        print(
            f"[emit_recycle_event] before-file unreadable ({exc!s}); "
            "emitting legacy event without PIDs.",
            file=sys.stderr,
        )
        before = {}

    after = snapshot_pids()
    partial, surviving = compute_partial(before, after)

    event = {
        "ts": utc_now_iso(),
        "sha": head_sha(),
        "label": args.label,
        "pids_before": before,
        "pids_after": after,
        "partial_recycle": partial,
        "surviving_processes": surviving,
    }

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(event, separators=(",", ":"))
    # Defensive: if the file exists and its last byte isn't a newline
    # (an earlier writer crashed mid-line, or an external tool appended
    # without a trailing \n), prepend one so our record starts on its
    # own line. The reader splits on \n, so a glued record silently
    # drops both events from the tail; the byte is cheap insurance.
    prefix = b""
    try:
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > 0:
            with open(LOG_PATH, "rb") as f:
                f.seek(-1, os.SEEK_END)
                if f.read(1) != b"\n":
                    prefix = b"\n"
    except OSError:
        pass
    # Append is POSIX-atomic for writes < PIPE_BUF; the line is well
    # under that threshold. os.write on an O_APPEND fd is the safe
    # primitive — TextIOWrapper adds buffering that can interleave;
    # direct fd write avoids that.
    fd = os.open(LOG_PATH, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, prefix + (line + "\n").encode("utf-8"))
    finally:
        os.close(fd)

    marker = "PARTIAL" if partial else "clean"
    print(
        f"[emit_recycle_event] {marker} recycle recorded "
        f"(sha={event['sha'][:12]}, surviving={surviving or 'none'})"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Enrich recycle-all JSONL with worker PIDs before/after (S2768 N7).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_snap = sub.add_parser("snapshot", help="Print JSON snapshot of pidfiles to stdout.")
    p_snap.set_defaults(func=cmd_snapshot)

    p_emit = sub.add_parser("emit", help="Snapshot after + append enriched JSONL event.")
    p_emit.add_argument(
        "--before",
        required=True,
        help="Path to JSON file written by an earlier `snapshot` call.",
    )
    p_emit.add_argument("--label", default="recycle-all", help="Event label (default: recycle-all).")
    p_emit.set_defaults(func=cmd_emit)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
