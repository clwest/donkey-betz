"""
Session 1119 — Run an agent survey against a registered external repo.

v0 path: load the latest Repo Snapshot + pinned Repo Profile, feed them to
gpt-5-mini with the chosen agent's persona, and persist the result as a
``CTO Survey: <repo> — YYYY-MM-DD`` deliverable in that workspace.

This bypasses the agent_router's u-d-b-aware tool loop on purpose. The
external repo's data already lives in the snapshot; the survey is a
focused analysis pass over that material — no tool calls into u-d-b
platform internals. v1+ can promote agents to native repo-aware tool
surfaces.

Usage:
    python manage.py survey_external_repo --repo character-os --agent cto
    python manage.py survey_external_repo --repo character-os --agent coo
    python manage.py survey_external_repo --repo character-os --agent cto --dry-run
"""

from datetime import datetime, timezone
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()

REPO_PROFILE_CATEGORY = "repo_profile"
SNAPSHOT_CATEGORY = "repo_snapshot"
SURVEY_CATEGORY = "repo_survey"

AGENT_PERSONAS = {
    "cto": {
        "agent_name": "CTOAgent",
        "label": "CTO Survey",
        "system_prompt": (
            "You are CTOAgent, the Chief Technology Officer for the operator's "
            "laptop-local project fleet. You are surveying an EXTERNAL repo (not "
            "the u-d-b platform itself). Your job: read the supplied Repo Profile "
            "+ latest Snapshot and produce a tight technical survey.\n\n"
            "Output sections (markdown, in this order):\n"
            "1. **Health snapshot** — git state, dirty/clean, branch, last commits\n"
            "2. **What's shipped** — pull from anchor docs + handoffs\n"
            "3. **Active fronts** — what is in flight, paused, queued\n"
            "4. **Risks / blockers** — concrete, citable; mark hunches as such\n"
            "5. **Recommended next actions** — 3-7 bullets, ordered by leverage\n"
            "6. **Open questions for the operator** — short, answerable\n\n"
            "Tone: terse, executive, no hedging fluff. Never invent stats — only "
            "cite what appears in the supplied material. If something is unclear, "
            "list it as an open question rather than fabricating."
        ),
    },
    "coo": {
        "agent_name": "COOAgent",
        "label": "COO Survey",
        "system_prompt": (
            "You are COOAgent. You are surveying an EXTERNAL repo on the "
            "operator's laptop. Focus on operational health: what's running, "
            "what's stuck, what slows the operator down day-to-day, what queue "
            "depth or maintenance debt is accruing. Don't recommend product "
            "features; recommend operational fixes."
        ),
    },
    "editor": {
        "agent_name": "EditorAgent",
        "label": "Doc Editor Survey",
        "system_prompt": (
            "You are EditorAgent. Survey the supplied docs (anchors + handoffs) "
            "for the EXTERNAL repo. Flag drift between narrative anchor and "
            "runtime anchor, missing or stale handoffs, broken cross-references, "
            "and anything that would confuse a new collaborator."
        ),
    },
}


def _load_workspace(repo_id: str, username: str):
    from core.models_skin_layer import ProjectWorkspace
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist as e:
        raise CommandError(f"User {username!r} does not exist") from e
    workspace = ProjectWorkspace.objects.filter(user=user, name=repo_id).first()
    if not workspace:
        raise CommandError(
            f"No ProjectWorkspace named {repo_id!r} owned by {user.username}. "
            "Run register_external_repo first."
        )
    return user, workspace


def _latest_snapshot(workspace):
    from core.models_deliverables import Deliverable
    return (
        Deliverable.objects.filter(
            workspace=workspace, category=SNAPSHOT_CATEGORY
        )
        .order_by("-created_at")
        .first()
    )


def _repo_profile(workspace):
    from core.models_deliverables import Deliverable
    return (
        Deliverable.objects.filter(
            workspace=workspace,
            category=REPO_PROFILE_CATEGORY,
            is_pinned=True,
        )
        .order_by("-created_at")
        .first()
    )


def _build_user_prompt(workspace: Any, repo_profile, snapshot) -> str:
    parts = [
        f"# Survey target: {workspace.name}",
        "",
        f"Repo root: `{workspace.root_path}`",
        "",
        "## Repo Profile (canonical config — pinned)",
        "",
        repo_profile.content if repo_profile else "_(no Repo Profile found)_",
        "",
        "## Latest Repo Snapshot",
        "",
        snapshot.content if snapshot else "_(no snapshot found — run refresh_repo_context first)_",
        "",
        "## Task",
        "",
        "Produce the survey in the sections specified by your system prompt. "
        "Cite the supplied material; do not fabricate. Stay tight.",
    ]
    return "\n".join(parts)


def _call_gpt(system_prompt: str, user_prompt: str) -> tuple[str, dict]:
    from core.services.openai_client_factory import get_openai_client
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_completion_tokens=4000,
    )
    text = response.choices[0].message.content or ""
    usage = {
        "model": response.model,
        "prompt_tokens": getattr(response.usage, "prompt_tokens", None) if response.usage else None,
        "completion_tokens": getattr(response.usage, "completion_tokens", None) if response.usage else None,
        "total_tokens": getattr(response.usage, "total_tokens", None) if response.usage else None,
    }
    return text, usage


class Command(BaseCommand):
    help = (
        "Run an agent survey against a registered external repo. Persists "
        "result as a 'repo_survey' deliverable in the repo's workspace."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--repo",
            type=str,
            required=True,
            help="Repo id (workspace name), e.g. character-os",
        )
        parser.add_argument(
            "--agent",
            type=str,
            default="cto",
            choices=sorted(AGENT_PERSONAS.keys()),
            help="Agent persona to use (default: cto)",
        )
        parser.add_argument(
            "--user",
            type=str,
            default="donkeyking",
            help="Username that owns the workspace",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Build the prompt but don't call the LLM",
        )

    def handle(self, *args, **options):
        from core.services.deliverable_factory import create_deliverable

        repo_id = options["repo"]
        agent_key = options["agent"]
        persona = AGENT_PERSONAS[agent_key]

        user, workspace = _load_workspace(repo_id, options["user"])
        repo_profile = _repo_profile(workspace)
        snapshot = _latest_snapshot(workspace)

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE(
            f"SURVEY EXTERNAL REPO — {persona['agent_name']}"
        ))
        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(f"\nRepo: {repo_id}")
        self.stdout.write(f"Workspace id: {workspace.id}")
        self.stdout.write(f"Repo Profile: {'found' if repo_profile else 'MISSING'}")
        self.stdout.write(f"Latest snapshot: {snapshot.id if snapshot else 'MISSING'}")

        if not snapshot:
            raise CommandError(
                "No Repo Snapshot found. Run `python manage.py "
                f"refresh_repo_context --repo {repo_id}` first."
            )

        user_prompt = _build_user_prompt(workspace, repo_profile, snapshot)
        self.stdout.write(
            f"\nPrompt size: system={len(persona['system_prompt'])} chars, "
            f"user={len(user_prompt)} chars"
        )

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("\nDRY RUN — no LLM call, no DB write."))
            preview = user_prompt[:1200]
            self.stdout.write("\n--- User prompt preview ---\n")
            self.stdout.write(preview)
            if len(user_prompt) > 1200:
                self.stdout.write("\n[truncated]")
            return

        self.stdout.write("\nCalling gpt-5-mini…")
        try:
            text, usage = _call_gpt(persona["system_prompt"], user_prompt)
        except Exception as e:  # noqa: BLE001 — surface any LLM error cleanly
            raise CommandError(f"LLM call failed: {e}") from e

        self.stdout.write(
            f"  Tokens: prompt={usage.get('prompt_tokens')}, "
            f"completion={usage.get('completion_tokens')}, "
            f"total={usage.get('total_tokens')}"
        )
        if not text.strip():
            raise CommandError("LLM returned empty response.")

        now = datetime.now(timezone.utc)
        title = f"{persona['label']}: {workspace.name} — {now.strftime('%Y-%m-%d')}"

        survey_metadata = {
            "agent_persona": persona["agent_name"],
            "repo_id": repo_id,
            "workspace_id": str(workspace.id),
            "based_on_snapshot_id": str(snapshot.id),
            "based_on_repo_profile_id": str(repo_profile.id) if repo_profile else None,
            "llm_usage": usage,
            "surveyed_at": now.isoformat(timespec="seconds"),
            "schema_version": 1,
        }

        deliverable = create_deliverable(
            title=title,
            content=text,
            agent_name=persona["agent_name"],
            category=SURVEY_CATEGORY,
            deliverable_type="document",
            user=user,
            workspace_id=str(workspace.id),
            tags=["repo_survey", "multi-repo-v0", repo_id, agent_key],
            content_format="markdown",
            is_pinned=False,
            is_saved=True,
            agent_task=f"Survey external repo: {repo_id}",
            metadata=survey_metadata,
            publish_intent="internal_only",
        )
        if deliverable is None:
            raise CommandError(
                "DeliverableFactory rejected the survey deliverable (quality gate)."
            )

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("SURVEY COMPLETE"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(f"Survey deliverable id: {deliverable.id}")
        self.stdout.write(f"Title: {title}")
        self.stdout.write(f"\nFirst 500 chars of survey:\n")
        self.stdout.write(text[:500])
        if len(text) > 500:
            self.stdout.write("\n[truncated — view full deliverable in workspace]")
