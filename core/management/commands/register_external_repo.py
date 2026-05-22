"""
Session 1119 — Register an external repo as a managed ProjectWorkspace.

Multi-repo v0 (per Rigby's scoped plan): treat each laptop-local repo as a
project Rigby manages. The pa-managed ProjectWorkspace already supports the
"AI operates on this directory" shape (SKIN layer); this command wires up
the per-repo metadata + pinned Repo Profile deliverable from a JSON config.

Config schema lives at config/external_repos/<repo_id>.json. See the
character-os profile for the canonical shape. Zero migrations — every field
maps onto existing ProjectWorkspace / Deliverable columns.

Usage:
    # Register character-os from its config file
    python manage.py register_external_repo --repo character-os

    # Or by explicit path
    python manage.py register_external_repo --config config/external_repos/character-os.json

    # Recreate an existing workspace
    python manage.py register_external_repo --repo character-os --force

    # Preview without writing
    python manage.py register_external_repo --repo character-os --dry-run

    # Assign to a non-default user
    python manage.py register_external_repo --repo character-os --user donkeyking
"""

import json
import os
from pathlib import Path
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()

REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "repo_id",
    "name",
    "root_path",
    "workspace_type",
    "tech_stack",
    "entry_points",
    "protected_paths",
    "permissions",
    "repo_profile_metadata",
}
SUPPORTED_SCHEMA_VERSIONS = {1}
REPO_PROFILE_AGENT_NAME = "RepoOnboard"
REPO_PROFILE_CATEGORY = "repo_profile"


def _config_path_for_repo(repo_id: str) -> Path:
    """Resolve config path from project root (CWD-independent)."""
    project_root = Path(__file__).resolve().parents[3]
    return project_root / "config" / "external_repos" / f"{repo_id}.json"


def _load_config(config_path: Path) -> dict:
    if not config_path.exists():
        raise CommandError(f"Config file not found: {config_path}")
    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise CommandError(f"Config file is not valid JSON: {e}") from e

    missing = REQUIRED_TOP_LEVEL_KEYS - set(data.keys())
    if missing:
        raise CommandError(f"Config missing required keys: {sorted(missing)}")
    if data["schema_version"] not in SUPPORTED_SCHEMA_VERSIONS:
        raise CommandError(
            f"Unsupported schema_version {data['schema_version']!r} "
            f"(supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)})"
        )
    return data


def _validate_repo_path(root_path: str) -> None:
    if not os.path.isabs(root_path):
        raise CommandError(f"root_path must be absolute: {root_path!r}")
    if not os.path.isdir(root_path):
        raise CommandError(f"root_path does not exist or is not a directory: {root_path}")
    git_dir = os.path.join(root_path, ".git")
    if not os.path.exists(git_dir):
        raise CommandError(f"root_path is not a git repository (no .git): {root_path}")


def _render_repo_profile_markdown(config: dict) -> str:
    """Human-readable summary stored in the pinned Repo Profile deliverable."""
    md = config["repo_profile_metadata"]
    tech = config["tech_stack"]
    entry = config["entry_points"]
    lines: list[str] = [
        f"# Repo Profile: {config['name']}",
        "",
        f"**Repo ID:** `{config['repo_id']}`",
        f"**Root:** `{config['root_path']}`",
        f"**Workspace type:** `{config['workspace_type']}`",
        "",
        "## What it is",
        "",
        config["description"],
        "",
        "## Tech stack",
        "",
    ]
    for k, v in tech.items():
        if isinstance(v, dict):
            sub = ", ".join(f"{sk}={sv}" for sk, sv in v.items())
            lines.append(f"- **{k}:** {sub}")
        else:
            lines.append(f"- **{k}:** {v}")

    lines.extend([
        "",
        "## Anchor docs",
        "",
        f"- Narrative: `{entry.get('anchor_narrative', '—')}`",
        f"- Runtime: `{entry.get('anchor_runtime', '—')}`",
        f"- Start here: `{entry.get('anchor_start', '—')}`",
        f"- Claude project notes: `{entry.get('anchor_claude', '—')}`",
        f"- Handoffs: `{entry.get('handoffs_dir', '—')}` "
        f"(current pointer: `{md.get('session_log_pointer', '—')}`)",
        "",
        "## Code allowlist (filesystem read scope)",
        "",
    ])
    for path in entry.get("code_allowlist", []):
        lines.append(f"- `{path}`")

    lines.extend([
        "",
        "## Inventory + health",
        "",
        f"- Inventory: `{entry.get('inventory_command', '—')}` "
        f"(cwd: `{entry.get('inventory_cwd', '.')}`)",
        f"- Health/Doctor: `{md.get('doctor_command', entry.get('health_command', '—'))}`",
        "",
        "## Constraints (human-readable)",
        "",
    ])
    for c in md.get("constraints_text", []):
        lines.append(f"- {c}")

    rules = md.get("constraints_rules", [])
    if rules:
        lines.extend([
            "",
            "## Constraint rules (machine-readable)",
            "",
            "```json",
            json.dumps(rules, indent=2),
            "```",
        ])

    bridge = md.get("bridge_relationship")
    if bridge:
        lines.extend([
            "",
            "## Bridge relationship",
            "",
            f"- Reaches engine: **{bridge.get('reaches_engine', '—')}**",
            f"- Via: `{bridge.get('via', '—')}`",
            f"- Tools: {', '.join(bridge.get('tools', [])) or '—'}",
            f"- Status: {bridge.get('product_status', '—')}",
        ])
        if bridge.get("queued"):
            lines.append(f"- Queued: {bridge['queued']}")

    phase_status = md.get("phase_status")
    if phase_status:
        lines.extend([
            "",
            "## Phase status (at registration time)",
            "",
        ])
        for k, v in phase_status.items():
            lines.append(f"- **{k}:** {v}")

    lines.extend([
        "",
        "## State",
        "",
        f"- Last refresh: `{md.get('last_refresh_at') or 'never'}`",
        f"- Last git HEAD: `{md.get('last_git_head') or 'unknown'}`",
        f"- Last branch: `{md.get('last_branch') or 'unknown'}`",
        f"- Health: `{md.get('health_status') or 'unknown'}`",
        "",
        "---",
        "",
        "_This Repo Profile is a pinned Deliverable. It is the canonical "
        "machine + human description of an external repo Rigby manages. "
        "Run `refresh_repo_context` to update snapshot state._",
    ])
    return "\n".join(lines)


def _ensure_workspace(config: dict, user: Any, force: bool, stdout) -> Any:
    from core.models_skin_layer import ProjectWorkspace

    perms = config["permissions"]
    fields = {
        "user": user,
        "name": config["name"],
        "description": config["description"],
        "workspace_type": config["workspace_type"],
        "root_path": config["root_path"],
        "tech_stack": config["tech_stack"],
        "entry_points": config["entry_points"],
        "protected_paths": list(config["protected_paths"]),
        "allow_file_write": bool(perms.get("allow_file_write", True)),
        "allow_file_delete": bool(perms.get("allow_file_delete", False)),
        "allow_command_execution": bool(perms.get("allow_command_execution", True)),
        "allow_git_operations": bool(perms.get("allow_git_operations", True)),
        "allow_autonomous_writes": bool(perms.get("allow_autonomous_writes", False)),
        "require_human_review": bool(perms.get("require_human_review", False)),
    }

    existing = ProjectWorkspace.objects.filter(user=user, name=config["name"]).first()
    if existing and not force:
        stdout.write(
            f"  Workspace '{config['name']}' already exists (id={existing.id}). "
            "Use --force to update."
        )
        return existing

    if existing and force:
        for k, v in fields.items():
            setattr(existing, k, v)
        existing.save()
        stdout.write(f"  Updated existing workspace (id={existing.id}).")
        return existing

    workspace = ProjectWorkspace.objects.create(**fields)
    stdout.write(f"  Created new workspace (id={workspace.id}).")
    return workspace


def _ensure_repo_profile_deliverable(config: dict, workspace: Any, user: Any, force: bool, stdout) -> Any:
    from core.models_deliverables import Deliverable

    title = f"Repo Profile: {config['name']}"
    content = _render_repo_profile_markdown(config)
    metadata = dict(config["repo_profile_metadata"])
    metadata.setdefault("repo_id", config["repo_id"])
    metadata.setdefault("schema_version", config["schema_version"])
    metadata.setdefault("registered_at", _utc_now_iso())

    existing = Deliverable.objects.filter(
        workspace=workspace,
        category=REPO_PROFILE_CATEGORY,
        is_pinned=True,
    ).first()

    if existing and not force:
        stdout.write(
            f"  Repo Profile deliverable already exists "
            f"(id={existing.id}). Use --force to refresh."
        )
        return existing

    if existing and force:
        existing.title = title
        existing.content = content
        existing.preview_content = content[:500]
        existing.metadata = metadata
        existing.save(update_fields=[
            "title", "content", "preview_content", "metadata", "updated_at",
        ])
        stdout.write(f"  Updated existing Repo Profile deliverable (id={existing.id}).")
        return existing

    from core.services.deliverable_factory import create_deliverable
    deliverable = create_deliverable(
        title=title,
        content=content,
        agent_name=REPO_PROFILE_AGENT_NAME,
        category=REPO_PROFILE_CATEGORY,
        deliverable_type="document",
        user=user,
        workspace_id=str(workspace.id),
        tags=["repo_profile", "pinned", "multi-repo-v0", config["repo_id"]],
        content_format="markdown",
        is_pinned=True,
        is_saved=True,
        agent_task=f"Register external repo: {config['repo_id']}",
        metadata=metadata,
        publish_intent="internal_only",
    )
    if deliverable is None:
        raise CommandError(
            "DeliverableFactory rejected the Repo Profile (quality gate). "
            "Check content length + agent_name allowlist."
        )
    stdout.write(f"  Created Repo Profile deliverable (id={deliverable.id}).")
    return deliverable


def _utc_now_iso() -> str:
    from django.utils import timezone
    return timezone.now().isoformat()


class Command(BaseCommand):
    help = (
        "Register an external repo as a managed ProjectWorkspace + pinned "
        "Repo Profile deliverable. Multi-repo v0 (Session 1119)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--repo",
            type=str,
            default=None,
            help="Repo id; loads config from config/external_repos/<repo>.json",
        )
        parser.add_argument(
            "--config",
            type=str,
            default=None,
            help="Path to repo profile JSON (overrides --repo lookup)",
        )
        parser.add_argument(
            "--user",
            type=str,
            default="donkeyking",
            help="Username to own the workspace (default: donkeyking)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Update workspace + Repo Profile deliverable if they exist",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and preview without writing to the database",
        )

    def handle(self, *args, **options):
        if not options["repo"] and not options["config"]:
            raise CommandError("Provide --repo <repo_id> or --config <path>")
        if options["config"]:
            config_path = Path(options["config"]).expanduser().resolve()
        else:
            config_path = _config_path_for_repo(options["repo"])

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("REGISTER EXTERNAL REPO (multi-repo v0)"))
        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(f"\nConfig: {config_path}")

        config = _load_config(config_path)
        _validate_repo_path(config["root_path"])

        self.stdout.write(f"\nRepo: {config['repo_id']} ({config['name']})")
        self.stdout.write(f"Root: {config['root_path']}")
        self.stdout.write(f"Schema version: {config['schema_version']}")
        self.stdout.write(
            f"Anchors: narrative={config['entry_points'].get('anchor_narrative')}, "
            f"runtime={config['entry_points'].get('anchor_runtime')}"
        )
        self.stdout.write(f"Permissions: {config['permissions']}")

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("\nDRY RUN — no DB writes."))
            preview = _render_repo_profile_markdown(config)
            self.stdout.write("\n--- Repo Profile markdown preview (first 800 chars) ---")
            self.stdout.write(preview[:800])
            self.stdout.write("\n[truncated]" if len(preview) > 800 else "")
            return

        try:
            user = User.objects.get(username=options["user"])
        except User.DoesNotExist as e:
            raise CommandError(f"User {options['user']!r} does not exist") from e

        self.stdout.write(f"\nOwner: {user.username} (id={user.id})")

        self.stdout.write("\nWorkspace:")
        workspace = _ensure_workspace(config, user, options["force"], self.stdout)

        self.stdout.write("\nRepo Profile deliverable:")
        deliverable = _ensure_repo_profile_deliverable(
            config, workspace, user, options["force"], self.stdout,
        )

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("REGISTRATION COMPLETE"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(f"Workspace id: {workspace.id}")
        self.stdout.write(f"Repo Profile deliverable id: {deliverable.id}")
        self.stdout.write(
            "\nNext: run `python manage.py refresh_repo_context "
            f"--repo {config['repo_id']}` to take a first snapshot."
        )
