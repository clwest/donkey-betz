"""
Session 1119 — Refresh repo context for a registered external repo.

Reads the pinned Repo Profile deliverable + the workspace's entry_points
to discover anchor docs, handoffs, and the inventory command. Runs git
status/log, reads the docs, optionally runs the inventory command, then
writes a non-pinned "Repo Snapshot YYYY-MM-DD" deliverable.

Snapshots are append-only with a retention cap (default: keep last 20).
The pinned Repo Profile's metadata is updated with last_refresh_at,
last_git_head, last_branch, health_status.

Usage:
    python manage.py refresh_repo_context --repo character-os
    python manage.py refresh_repo_context --repo character-os --skip-inventory
    python manage.py refresh_repo_context --repo character-os --user donkeyking
"""

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()

SNAPSHOT_AGENT_NAME = "RepoOnboard"
SNAPSHOT_CATEGORY = "repo_snapshot"
REPO_PROFILE_CATEGORY = "repo_profile"
DEFAULT_MAX_SNAPSHOTS = 20
DEFAULT_HANDOFF_TAIL_LINES = 40
DEFAULT_ANCHOR_TAIL_LINES = 60
INVENTORY_TIMEOUT_SECONDS = 30
GIT_TIMEOUT_SECONDS = 10


def _run(cmd: list[str], cwd: str, timeout: int = GIT_TIMEOUT_SECONDS) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"
    except FileNotFoundError as e:
        return 127, "", str(e)


def _git_snapshot(root: str) -> dict:
    head_rc, head_out, head_err = _run(["git", "rev-parse", "HEAD"], root)
    branch_rc, branch_out, _ = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], root)
    status_rc, status_out, _ = _run(["git", "status", "--porcelain"], root)
    log_rc, log_out, _ = _run(
        ["git", "log", "--oneline", "-5"], root
    )
    return {
        "head": head_out if head_rc == 0 else None,
        "head_error": head_err if head_rc != 0 else None,
        "branch": branch_out if branch_rc == 0 else None,
        "dirty": bool(status_out) if status_rc == 0 else None,
        "dirty_files_count": len(status_out.splitlines()) if status_rc == 0 else None,
        "recent_commits": log_out.splitlines() if log_rc == 0 else [],
    }


def _read_doc_tail(path: Path, max_lines: int) -> str:
    if not path.exists():
        return f"_(missing: {path})_"
    try:
        with path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        return f"_(unreadable: {e})_"
    if len(lines) <= max_lines:
        return "".join(lines)
    head = "".join(lines[:10])
    tail = "".join(lines[-(max_lines - 10):])
    return f"{head}\n\n_… {len(lines) - max_lines} lines elided …_\n\n{tail}"


def _latest_handoffs(handoffs_dir: Path, limit: int = 2) -> list[Path]:
    if not handoffs_dir.exists() or not handoffs_dir.is_dir():
        return []
    candidates = [
        p for p in handoffs_dir.iterdir()
        if p.is_file() and p.suffix.lower() == ".md" and "SESSION" in p.name.upper()
    ]
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[:limit]


def _run_inventory(workspace: Any) -> dict:
    """Run the repo's inventory command. If `inventory_venv` is declared,
    wrap in `bash -c "source <venv> && cd <cwd> && <cmd>"` so repos with
    third-party deps (Django, FastAPI, etc.) can import them. Otherwise
    run the bare command (fits stdlib-only repos like context-kit)."""
    entry = workspace.entry_points or {}
    cmd_str = entry.get("inventory_command")
    if not cmd_str:
        return {"skipped": True, "reason": "no inventory_command configured"}

    cwd = workspace.root_path
    cwd_sub = entry.get("inventory_cwd")
    if cwd_sub:
        cwd = os.path.join(workspace.root_path, cwd_sub)
    if not os.path.isdir(cwd):
        return {"skipped": True, "reason": f"cwd does not exist: {cwd}"}

    venv_rel = entry.get("inventory_venv")
    env_file_rel = entry.get("inventory_env_file")
    wrapped = False
    venv_abs = None
    env_file_abs = None

    if venv_rel or env_file_rel:
        # Build a bash -c wrapper. Order:
        #   1. unset Django/Python env vars that leak from the parent
        #      process (u-d-b's worker has DJANGO_SETTINGS_MODULE +
        #      PYTHONPATH set; those would break a sibling Django repo)
        #   2. source the env file (so the target repo can re-set what
        #      it needs)
        #   3. activate venv
        #   4. cd into inventory cwd
        #   5. run command
        parts: list[str] = [
            "unset DJANGO_SETTINGS_MODULE PYTHONPATH PYTHONHOME VIRTUAL_ENV",
        ]
        if env_file_rel:
            env_file_abs = os.path.join(workspace.root_path, env_file_rel)
            if not os.path.exists(env_file_abs):
                return {
                    "skipped": True,
                    "reason": f"inventory_env_file declared but missing: {env_file_abs}",
                }
            parts.append(f"set -a && source {_sh_quote(env_file_abs)} && set +a")
        if venv_rel:
            venv_abs = os.path.join(workspace.root_path, venv_rel)
            if not os.path.exists(venv_abs):
                return {
                    "skipped": True,
                    "reason": f"inventory_venv declared but activate script missing: {venv_abs}",
                }
            parts.append(f"source {_sh_quote(venv_abs)}")
        parts.append(f"cd {_sh_quote(cwd)}")
        parts.append(cmd_str)
        shell_cmd = " && ".join(parts)
        argv = ["bash", "-c", shell_cmd]
        exec_cwd = workspace.root_path
        wrapped = True
    else:
        argv = cmd_str.split()
        exec_cwd = cwd

    rc, out, err = _run(argv, exec_cwd, timeout=INVENTORY_TIMEOUT_SECONDS)
    return {
        "command": cmd_str,
        "cwd": cwd,
        "venv": venv_abs,
        "env_file": env_file_abs,
        "wrapped": wrapped,
        "returncode": rc,
        "stdout_tail": out[-1500:] if out else "",
        "stderr_tail": err[-500:] if err else "",
        "succeeded": rc == 0,
    }


def _sh_quote(s: str) -> str:
    """Minimal shell-quote for paths inside bash -c strings. Wraps in
    single quotes and escapes any embedded single quote."""
    return "'" + s.replace("'", "'\"'\"'") + "'"


def _build_snapshot_markdown(
    workspace: Any,
    repo_profile_metadata: dict,
    git_info: dict,
    anchor_docs: dict[str, str],
    handoff_excerpts: dict[str, str],
    inventory_result: dict,
    refreshed_at: str,
) -> str:
    lines: list[str] = [
        f"# Repo Snapshot: {workspace.name} — {refreshed_at[:10]}",
        "",
        f"**Refreshed at:** `{refreshed_at}`",
        f"**Root:** `{workspace.root_path}`",
        "",
        "## Git state",
        "",
        f"- HEAD: `{git_info.get('head') or 'unknown'}`",
        f"- Branch: `{git_info.get('branch') or 'unknown'}`",
        f"- Dirty: `{git_info.get('dirty')}` "
        f"({git_info.get('dirty_files_count') or 0} files)",
        "",
        "### Recent commits",
        "",
    ]
    for commit in git_info.get("recent_commits", []):
        lines.append(f"- `{commit}`")
    if not git_info.get("recent_commits"):
        lines.append("_(none / unavailable)_")

    lines.extend([
        "",
        "## Inventory",
        "",
    ])
    if inventory_result.get("skipped"):
        lines.append(f"_Skipped: {inventory_result['reason']}_")
    else:
        inv_rc = inventory_result.get("returncode")
        inv_status = "OK" if inventory_result.get("succeeded") else f"FAILED (rc={inv_rc})"
        lines.extend([
            f"- Command: `{inventory_result['command']}`",
            f"- Cwd: `{inventory_result['cwd']}`",
            f"- venv: `{inventory_result.get('venv') or 'none'}` "
            f"({'wrapped' if inventory_result.get('wrapped') else 'bare'})",
            f"- Result: {inv_status}",
        ])
        if inventory_result.get("stderr_tail"):
            lines.extend([
                "",
                "### stderr tail",
                "",
                "```",
                inventory_result["stderr_tail"],
                "```",
            ])
        if inventory_result.get("stdout_tail"):
            lines.extend([
                "",
                "### stdout tail",
                "",
                "```",
                inventory_result["stdout_tail"],
                "```",
            ])

    if handoff_excerpts:
        lines.extend(["", "## Latest handoffs", ""])
        for name, body in handoff_excerpts.items():
            lines.extend([f"### `{name}`", "", body, ""])

    if anchor_docs:
        lines.extend(["", "## Anchor docs", ""])
        for label, body in anchor_docs.items():
            lines.extend([f"### {label}", "", body, ""])

    lines.extend([
        "",
        "---",
        "",
        "_Auto-generated by `refresh_repo_context`. This is an append-only "
        "snapshot. The pinned Repo Profile holds the canonical config; this "
        "row captures point-in-time state._",
    ])
    return "\n".join(lines)


def _enforce_retention(workspace: Any, max_snapshots: int, stdout) -> None:
    from core.models_deliverables import Deliverable
    snaps = list(
        Deliverable.objects.filter(workspace=workspace, category=SNAPSHOT_CATEGORY)
        .order_by("-created_at")
    )
    if len(snaps) <= max_snapshots:
        return
    excess = snaps[max_snapshots:]
    archived = 0
    for d in excess:
        if d.status != "archived":
            d.status = "archived"
            d.save(update_fields=["status", "updated_at"])
            archived += 1
    if archived:
        stdout.write(f"  Retention: archived {archived} old snapshot(s) "
                     f"(kept {max_snapshots}).")


def _update_repo_profile(workspace: Any, refreshed_at: str, git_info: dict, stdout) -> None:
    from core.models_deliverables import Deliverable
    profile = Deliverable.objects.filter(
        workspace=workspace,
        category=REPO_PROFILE_CATEGORY,
        is_pinned=True,
    ).first()
    if not profile:
        stdout.write("  WARN: No pinned Repo Profile found to update.")
        return
    metadata = dict(profile.metadata or {})
    metadata["last_refresh_at"] = refreshed_at
    metadata["last_git_head"] = git_info.get("head")
    metadata["last_branch"] = git_info.get("branch")
    metadata["health_status"] = "dirty" if git_info.get("dirty") else "clean"
    profile.metadata = metadata
    profile.save(update_fields=["metadata", "updated_at"])
    stdout.write(f"  Updated pinned Repo Profile metadata (id={profile.id}).")


class Command(BaseCommand):
    help = (
        "Refresh repo context for a registered external repo. Creates an "
        "append-only Repo Snapshot deliverable and updates the pinned "
        "Repo Profile metadata."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--repo",
            type=str,
            required=True,
            help="Repo id / workspace name (e.g. character-os)",
        )
        parser.add_argument(
            "--user",
            type=str,
            default="donkeyking",
            help="Username that owns the workspace (default: donkeyking)",
        )
        parser.add_argument(
            "--skip-inventory",
            action="store_true",
            help="Skip the inventory command even if configured",
        )
        parser.add_argument(
            "--max-snapshots",
            type=int,
            default=DEFAULT_MAX_SNAPSHOTS,
            help=f"Retention cap (default: {DEFAULT_MAX_SNAPSHOTS})",
        )

    def handle(self, *args, **options):
        from core.models_skin_layer import ProjectWorkspace
        from core.services.deliverable_factory import create_deliverable

        repo_id = options["repo"]
        try:
            user = User.objects.get(username=options["user"])
        except User.DoesNotExist as e:
            raise CommandError(f"User {options['user']!r} does not exist") from e

        workspace = ProjectWorkspace.objects.filter(user=user, name=repo_id).first()
        if not workspace:
            raise CommandError(
                f"No ProjectWorkspace named {repo_id!r} owned by {user.username}. "
                "Run `python manage.py register_external_repo --repo "
                f"{repo_id}` first."
            )

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("REFRESH REPO CONTEXT (multi-repo v0)"))
        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(f"\nRepo: {repo_id}")
        self.stdout.write(f"Workspace id: {workspace.id}")
        self.stdout.write(f"Root: {workspace.root_path}")

        # Git snapshot
        self.stdout.write("\nReading git state…")
        git_info = _git_snapshot(workspace.root_path)
        self.stdout.write(
            f"  HEAD={git_info.get('head')!s:.16} "
            f"branch={git_info.get('branch')} "
            f"dirty={git_info.get('dirty')}"
        )

        # Anchor docs
        self.stdout.write("\nReading anchor docs…")
        entry = workspace.entry_points or {}
        anchor_docs: dict[str, str] = {}
        for label, key in [
            ("Start here", "anchor_start"),
            ("Narrative anchor", "anchor_narrative"),
            ("Runtime anchor", "anchor_runtime"),
            ("CLAUDE.md", "anchor_claude"),
        ]:
            rel = entry.get(key)
            if not rel:
                continue
            full = Path(workspace.root_path) / rel
            anchor_docs[f"{label} — `{rel}`"] = _read_doc_tail(full, DEFAULT_ANCHOR_TAIL_LINES)
            self.stdout.write(f"  {label}: {full.exists()}")

        # Latest handoffs
        self.stdout.write("\nReading latest handoffs…")
        handoffs_dir = entry.get("handoffs_dir")
        handoff_excerpts: dict[str, str] = {}
        if handoffs_dir:
            handoffs_path = Path(workspace.root_path) / handoffs_dir
            for h in _latest_handoffs(handoffs_path, limit=2):
                handoff_excerpts[h.name] = _read_doc_tail(h, DEFAULT_HANDOFF_TAIL_LINES)
                self.stdout.write(f"  {h.name}")

        # Inventory
        self.stdout.write("\nRunning inventory command…")
        if options["skip_inventory"]:
            inventory_result = {"skipped": True, "reason": "--skip-inventory flag"}
        else:
            inventory_result = _run_inventory(workspace)
        if inventory_result.get("skipped"):
            self.stdout.write(f"  Skipped: {inventory_result['reason']}")
        else:
            self.stdout.write(
                f"  rc={inventory_result['returncode']} "
                f"({'OK' if inventory_result['succeeded'] else 'FAILED'})"
            )

        refreshed_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

        # Build + write snapshot deliverable
        self.stdout.write("\nWriting Repo Snapshot deliverable…")
        profile_metadata = {}
        from core.models_deliverables import Deliverable
        profile = Deliverable.objects.filter(
            workspace=workspace,
            category=REPO_PROFILE_CATEGORY,
            is_pinned=True,
        ).first()
        if profile:
            profile_metadata = dict(profile.metadata or {})

        markdown = _build_snapshot_markdown(
            workspace=workspace,
            repo_profile_metadata=profile_metadata,
            git_info=git_info,
            anchor_docs=anchor_docs,
            handoff_excerpts=handoff_excerpts,
            inventory_result=inventory_result,
            refreshed_at=refreshed_at,
        )
        snapshot_metadata = {
            "refreshed_at": refreshed_at,
            "git": git_info,
            "inventory": inventory_result,
            "handoff_files": list(handoff_excerpts.keys()),
            "anchor_docs_read": list(anchor_docs.keys()),
            "repo_id": profile_metadata.get("repo_id", repo_id),
            "schema_version": 1,
        }
        snapshot = create_deliverable(
            title=f"Repo Snapshot: {workspace.name} — {refreshed_at[:10]}",
            content=markdown,
            agent_name=SNAPSHOT_AGENT_NAME,
            category=SNAPSHOT_CATEGORY,
            deliverable_type="document",
            user=user,
            workspace_id=str(workspace.id),
            tags=["repo_snapshot", "multi-repo-v0", repo_id],
            content_format="markdown",
            is_pinned=False,
            is_saved=False,
            agent_task=f"Refresh repo context: {repo_id}",
            metadata=snapshot_metadata,
            publish_intent="internal_only",
        )
        if snapshot is None:
            raise CommandError(
                "DeliverableFactory rejected the snapshot (quality gate). "
                "Check content length."
            )
        self.stdout.write(f"  Created Repo Snapshot deliverable (id={snapshot.id}).")

        # Update pinned Repo Profile metadata
        self.stdout.write("\nUpdating pinned Repo Profile metadata…")
        _update_repo_profile(workspace, refreshed_at, git_info, self.stdout)

        # Retention
        self.stdout.write("\nApplying retention…")
        _enforce_retention(workspace, options["max_snapshots"], self.stdout)

        # Update workspace timestamp + ops counter
        workspace.last_operation_at = datetime.now(timezone.utc)
        workspace.current_branch = git_info.get("branch") or workspace.current_branch
        workspace.total_operations = (workspace.total_operations or 0) + 1
        workspace.save(update_fields=[
            "last_operation_at", "current_branch",
            "total_operations", "updated_at",
        ])

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("REFRESH COMPLETE"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(f"Snapshot id: {snapshot.id}")
        self.stdout.write(f"Refreshed at: {refreshed_at}")
