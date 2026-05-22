"""
Session 1120 — Draft 3 doc-claim verifier specs for a fleet repo.

v0 path: load the pinned Repo Profile + latest Snapshot + latest CTO
Survey for a registered external repo, feed them to gpt-5-mini, and
produce a structured-prose proposal of 3 doc-vs-runtime claims targeting
docs/PROJECT_WHAT_IT_IS.md. Persist as a ``verifier_plan`` deliverable
so it surfaces in Rigby's workspace tooling.

Companion to the fleet-wide doc-verifier rollout that uses
``scripts/verify_doc_claims.py`` (ported from u-d-b's Session 1099
verifier; mentorforge#8 is the canonical FastAPI reference impl).

Usage:
    python manage.py draft_repo_verifier_claims --repo pitchdeckforge
    python manage.py draft_repo_verifier_claims --repo X --dry-run
"""

from datetime import datetime, timezone
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()

REPO_PROFILE_CATEGORY = "repo_profile"
SNAPSHOT_CATEGORY = "repo_snapshot"
SURVEY_CATEGORY = "repo_survey"
VERIFIER_PLAN_CATEGORY = "verifier_plan"


SYSTEM_PROMPT = (
    "You are CTOAgent proposing doc-vs-runtime verification claims for an "
    "external repo on the operator's laptop. You are NOT verifying "
    "anything yourself — you are proposing claims that a separate script "
    "(scripts/verify_doc_claims.py, ported from u-d-b's Session 1099 "
    "verifier framework) will run on every commit.\n\n"
    "Given the supplied Repo Profile + latest Snapshot + latest CTO "
    "Survey, propose exactly 3 doc-vs-code claims anchored to "
    "docs/PROJECT_WHAT_IT_IS.md. Each claim must compare a count, list, "
    "or constant that exists BOTH in the narrative anchor doc AND in the "
    "code, so the verifier can detect drift between them.\n\n"
    "**IMPORTANT CONSTRAINT:** `target_file` MUST be a Python file in the "
    "repo (almost always `backend/app/*.py`). The verifier framework is "
    "Python-native and uses Python's `ast` module or direct `import` for "
    "extraction — it does NOT parse TypeScript, JavaScript, or YAML. If "
    "the only obvious targets are frontend/config files, propose Python-"
    "side equivalents (the backend usually has the canonical constant — "
    "e.g. `SLIDE_STRUCTURE` in `backend/app/main.py` for a 'N slides' "
    "claim). If you genuinely cannot find 3 Python-side targets, propose "
    "fewer claims and explain in `## Notes`.\n\n"
    "Output 3 structured blocks, separated by a blank line, in this shape:\n\n"
    "claim_id: <snake_case_id>\n"
    "description: <one-line; what the verifier checks>\n"
    "target_file: <repo-relative path to a Python file, e.g. backend/app/tiers.py>\n"
    "extraction: <import OR ast — pick `import` only if target_file's "
    "imports are minimal (dataclasses/stdlib only); pick `ast` if it "
    "pulls heavy deps like FastAPI, SQLAlchemy, dotenv, SQLite>\n"
    "target_symbol: <module-level name to read, e.g. TIERS or PERSONAS>\n"
    "how_to_count: <one sentence describing the count, e.g. \"len(TIERS) "
    "→ number of dict keys\" or \"AST walk for `PERSONAS = [...]` and "
    "count list elements\">\n"
    "doc_says: <the line from PROJECT_WHAT_IT_IS.md that asserts the "
    "count; cite the exact text if visible in the snapshot; if the doc "
    "has placeholders instead of concrete counts, write "
    "\"(placeholder — no concrete count in doc)\">\n"
    "expected_value: <integer the doc claims; or \"(unknown)\" if the "
    "doc only has placeholders>\n"
    "rationale: <one-line; why this claim is worth tracking>\n\n"
    "After the 3 blocks, output a `## Notes` section (markdown header) "
    "with caveats — e.g., which files are dirty, which claims might "
    "need ast over import, warnings about heavy imports, gaps in the "
    "supplied snapshot.\n\n"
    "Tone: terse. Cite the supplied material; never fabricate. If you "
    "cannot confidently identify 3 claims from what's in the snapshot, "
    "propose what you can and explain the gap in `## Notes`."
)


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


def _latest(workspace, category: str):
    from core.models_deliverables import Deliverable
    return (
        Deliverable.objects.filter(workspace=workspace, category=category)
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


def _latest_cto_survey(workspace):
    """Return the most recent CTOAgent survey deliverable for this workspace."""
    from core.models_deliverables import Deliverable
    return (
        Deliverable.objects.filter(
            workspace=workspace,
            category=SURVEY_CATEGORY,
            title__icontains="CTO Survey",
        )
        .order_by("-created_at")
        .first()
    )


def _build_user_prompt(workspace: Any, repo_profile, snapshot, cto_survey) -> str:
    parts = [
        f"# Repo: {workspace.name}",
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
        "## Latest CTO Survey (for context on what's already known)",
        "",
        cto_survey.content if cto_survey else "_(no CTO survey found — run survey_external_repo --agent cto first)_",
        "",
        "## Task",
        "",
        "Propose 3 doc-vs-runtime verification claims per the system "
        "prompt's structured output format. Anchor each claim to "
        "docs/PROJECT_WHAT_IT_IS.md as the source-of-truth doc.",
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
        "Draft 3 doc-vs-runtime claim specs for a registered external repo. "
        "Persists as a 'verifier_plan' deliverable in the repo's workspace."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--repo",
            type=str,
            required=True,
            help="Repo id (workspace name), e.g. pitchdeckforge",
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
        user, workspace = _load_workspace(repo_id, options["user"])
        repo_profile = _repo_profile(workspace)
        snapshot = _latest(workspace, SNAPSHOT_CATEGORY)
        cto_survey = _latest_cto_survey(workspace)

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE(f"DRAFT VERIFIER CLAIMS — {repo_id}"))
        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(f"\nWorkspace id: {workspace.id}")
        self.stdout.write(f"Repo Profile: {'found' if repo_profile else 'MISSING'}")
        self.stdout.write(f"Latest snapshot: {snapshot.id if snapshot else 'MISSING'}")
        self.stdout.write(f"Latest CTO survey: {cto_survey.id if cto_survey else 'MISSING'}")

        if not snapshot:
            raise CommandError(
                "No Repo Snapshot found. Run `python manage.py "
                f"refresh_repo_context --repo {repo_id}` first."
            )
        if not cto_survey:
            raise CommandError(
                "No CTO survey found. Run `python manage.py "
                f"survey_external_repo --repo {repo_id} --agent cto` first."
            )

        user_prompt = _build_user_prompt(workspace, repo_profile, snapshot, cto_survey)
        self.stdout.write(
            f"\nPrompt size: system={len(SYSTEM_PROMPT)} chars, "
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
            text, usage = _call_gpt(SYSTEM_PROMPT, user_prompt)
        except Exception as e:  # noqa: BLE001
            raise CommandError(f"LLM call failed: {e}") from e

        self.stdout.write(
            f"  Tokens: prompt={usage.get('prompt_tokens')}, "
            f"completion={usage.get('completion_tokens')}, "
            f"total={usage.get('total_tokens')}"
        )
        if not text.strip():
            raise CommandError("LLM returned empty response.")

        now = datetime.now(timezone.utc)
        title = f"Verifier Plan: {workspace.name} — {now.strftime('%Y-%m-%d')}"

        plan_metadata = {
            "agent_persona": "CTOAgent",
            "repo_id": repo_id,
            "workspace_id": str(workspace.id),
            "based_on_snapshot_id": str(snapshot.id),
            "based_on_repo_profile_id": str(repo_profile.id) if repo_profile else None,
            "based_on_cto_survey_id": str(cto_survey.id),
            "llm_usage": usage,
            "drafted_at": now.isoformat(timespec="seconds"),
            "schema_version": 1,
        }

        deliverable = create_deliverable(
            title=title,
            content=text,
            agent_name="CTOAgent",
            category=VERIFIER_PLAN_CATEGORY,
            deliverable_type="document",
            user=user,
            workspace_id=str(workspace.id),
            tags=["verifier_plan", "multi-repo-v0", "doc-verifier-rollout", repo_id],
            content_format="markdown",
            is_pinned=False,
            is_saved=True,
            agent_task=f"Draft doc-verifier claims for: {repo_id}",
            metadata=plan_metadata,
            publish_intent="internal_only",
        )
        if deliverable is None:
            raise CommandError(
                "DeliverableFactory rejected the verifier_plan deliverable."
            )

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("VERIFIER PLAN COMPLETE"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(f"Plan deliverable id: {deliverable.id}")
        self.stdout.write(f"Title: {title}")
        self.stdout.write(f"\n--- Full plan ---\n")
        self.stdout.write(text)
