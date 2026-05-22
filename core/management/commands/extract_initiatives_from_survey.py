"""
Session 1119 loose end #3 — Extract structured Initiatives from a repo
survey deliverable so survey findings become actionable u-d-b Initiative
rows rather than read-only markdown.

Takes a `repo_survey` deliverable, asks gpt-5-mini for a JSON array of
recommended actions, and creates Initiative rows with `status=TRIAGE`,
`target_workspace=<external repo's workspace>`. The survey's metadata
is updated with the created initiative IDs for traceability.

Usage:
    # By deliverable id
    python manage.py extract_initiatives_from_survey --deliverable <uuid>

    # By repo + agent (uses latest survey)
    python manage.py extract_initiatives_from_survey --repo character-os --agent cto

    # Preview without writing initiatives
    python manage.py extract_initiatives_from_survey --repo character-os --agent cto --dry-run

    # Max initiatives to create (defaults to 7 — matches survey's
    # "3-7 bullets, ordered by leverage" prompt)
    python manage.py extract_initiatives_from_survey --repo character-os --agent cto --max 5
"""

import json
from datetime import datetime, timezone
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()

SURVEY_CATEGORY = "repo_survey"
DEFAULT_MAX_INITIATIVES = 7

# Map structured category from the LLM to Initiative.Purpose choices.
# v0: best-effort. Default to LEARNING when uncertain (least disruptive).
CATEGORY_TO_PURPOSE = {
    "engineering": "stability",
    "ops": "stability",
    "infrastructure": "stability",
    "docs": "learning",
    "documentation": "learning",
    "product": "expansion",
    "feature": "expansion",
    "growth": "revenue",
    "revenue": "revenue",
    "monetization": "revenue",
    "maintenance": "maintenance",
    "research": "learning",
}

EXTRACT_SYSTEM_PROMPT = """You extract structured next-action items from \
a repo survey written by an executive agent (CTO/COO/Editor). The survey \
ends with a 'Recommended next actions' section. Your job: convert each \
recommendation into a single actionable Initiative.

Return JSON ONLY in this exact shape (no markdown, no commentary outside \
the JSON object):

{
  "initiatives": [
    {
      "name": "<short imperative title, <=80 chars, no period>",
      "description": "<full description: what to do, why, and the specific \
files/areas it touches if the survey says. 200-400 chars.>",
      "category": "engineering|ops|docs|product|growth|maintenance|research",
      "impact_score": 0.0-1.0,
      "urgency": 0.0-1.0,
      "confidence": 0.0-1.0,
      "rationale": "<one-sentence reason this action made the list>"
    }
  ]
}

Rules:
- One initiative per recommended action. Do NOT merge bullets.
- Skip generic items ('keep monitoring', 'investigate further') unless they
  name a specific file/system to investigate.
- Skip the 'Open questions for the operator' section — those are
  questions, not actions.
- impact_score / urgency / confidence are gut estimates from the survey
  text alone. If the survey gives no signal, use 0.5.
- name must be unique enough to disambiguate within a workspace (e.g.
  'Add INVENTORY git-SHA drift check', not just 'Add drift check').
- Skip recommendations that are already explicitly marked done or
  shipped in the survey.
"""


def _load_survey(deliverable_id: str | None, repo: str | None, agent: str | None, username: str):
    from core.models_deliverables import Deliverable
    from core.models_skin_layer import ProjectWorkspace

    user = User.objects.filter(username=username).first()
    if not user:
        raise CommandError(f"User {username!r} not found")

    if deliverable_id:
        try:
            d = Deliverable.objects.get(id=deliverable_id)
        except Deliverable.DoesNotExist as e:
            raise CommandError(f"Deliverable {deliverable_id} not found") from e
        if d.category != SURVEY_CATEGORY:
            raise CommandError(
                f"Deliverable {deliverable_id} has category {d.category!r}, "
                f"expected {SURVEY_CATEGORY!r}"
            )
        return user, d.workspace, d

    if not repo or not agent:
        raise CommandError("Provide --deliverable OR (--repo + --agent)")

    workspace = ProjectWorkspace.objects.filter(user=user, name=repo).first()
    if not workspace:
        raise CommandError(f"No workspace named {repo!r} owned by {user.username}")

    agent_map = {
        "cto": "CTOAgent",
        "coo": "COOAgent",
        "editor": "EditorAgent",
    }
    agent_name = agent_map.get(agent, agent)
    d = (
        Deliverable.objects.filter(
            workspace=workspace,
            category=SURVEY_CATEGORY,
            agent_name=agent_name,
        )
        .order_by("-created_at")
        .first()
    )
    if not d:
        raise CommandError(
            f"No {SURVEY_CATEGORY} deliverable found for repo={repo} "
            f"agent_name={agent_name}. Run survey_external_repo first."
        )
    return user, workspace, d


def _call_extract_llm(survey_content: str, max_initiatives: int) -> list[dict]:
    from core.services.openai_client_factory import get_openai_client
    client = get_openai_client()
    user_prompt = (
        f"Extract up to {max_initiatives} initiatives from this survey. "
        "Stop at the most leverage-bearing actions.\n\n---\n\n"
        f"{survey_content}"
    )
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_completion_tokens=4000,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "{}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise CommandError(f"LLM returned invalid JSON: {e}\nRaw: {raw[:500]}") from e
    items = parsed.get("initiatives", [])
    if not isinstance(items, list):
        raise CommandError(f"Expected 'initiatives' to be a list, got {type(items).__name__}")
    return items[:max_initiatives]


def _make_unique_name(base: str, repo_id: str, date_str: str) -> str:
    """Initiative.name is unique=True across the table. Prefix with
    repo + date so the same recommendation can re-surface in a later
    survey without colliding."""
    from core.models_document_registry import Initiative
    base = (base or "Untitled action").strip().rstrip(".").strip()
    base = base[:150]
    candidate = f"[{repo_id}] {base} — {date_str}"
    candidate = candidate[:200]
    n = 2
    while Initiative.objects.filter(name=candidate).exists():
        suffix = f" ({n})"
        candidate = f"[{repo_id}] {base} — {date_str}{suffix}"[:200]
        n += 1
        if n > 50:
            raise CommandError("Could not generate a unique initiative name (50 attempts).")
    return candidate


def _create_initiative(
    item: dict,
    workspace: Any,
    deliverable: Any,
    repo_id: str,
    date_str: str,
    agent_name: str,
):
    from core.models_document_registry import Initiative

    raw_category = (item.get("category") or "").strip().lower()
    purpose = CATEGORY_TO_PURPOSE.get(raw_category, "learning")

    impact = float(item.get("impact_score") or 0.5)
    urgency = float(item.get("urgency") or 0.5)
    confidence = float(item.get("confidence") or 0.5)
    impact = max(0.0, min(1.0, impact))
    urgency = max(0.0, min(1.0, urgency))
    confidence = max(0.0, min(1.0, confidence))

    description_parts = [
        item.get("description") or "",
    ]
    if item.get("rationale"):
        description_parts.append(f"\n\n_Rationale: {item['rationale']}_")
    description_parts.append(
        f"\n\n— Auto-extracted from {agent_name} survey "
        f"(deliverable {deliverable.id})."
    )
    description = "".join(description_parts).strip()

    initiative_name = _make_unique_name(
        item.get("name", "Untitled action"), repo_id, date_str,
    )

    return Initiative.objects.create(
        name=initiative_name,
        description=description,
        status=Initiative.Status.TRIAGE,
        purpose=purpose,
        program=Initiative.Program.UNCATEGORIZED,
        target_workspace=workspace,
        impact_score=impact,
        urgency=urgency,
        confidence=confidence,
        current_stage=0,
        created_by="multi-repo-survey",
        owner_agent=agent_name,
        parent_topic=f"repo:{repo_id}",
    )


class Command(BaseCommand):
    help = (
        "Extract structured Initiatives from a repo survey deliverable. "
        "Auto-creates Initiative rows with status=TRIAGE for operator review."
    )

    def add_arguments(self, parser):
        parser.add_argument("--deliverable", type=str, default=None,
                            help="Survey deliverable UUID")
        parser.add_argument("--repo", type=str, default=None,
                            help="Repo id (use with --agent to find latest survey)")
        parser.add_argument("--agent", type=str, default=None,
                            help="Agent persona that ran the survey (cto/coo/editor)")
        parser.add_argument("--user", type=str, default="donkeyking")
        parser.add_argument("--max", type=int, default=DEFAULT_MAX_INITIATIVES,
                            help=f"Max initiatives to create (default {DEFAULT_MAX_INITIATIVES})")
        parser.add_argument("--dry-run", action="store_true",
                            help="Extract + display but don't write Initiatives")

    def handle(self, *args, **options):
        user, workspace, deliverable = _load_survey(
            options.get("deliverable"),
            options.get("repo"),
            options.get("agent"),
            options["user"],
        )

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("EXTRACT INITIATIVES FROM SURVEY"))
        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(f"\nSurvey: {deliverable.id} ({deliverable.agent_name})")
        self.stdout.write(f"Workspace: {workspace.name} ({workspace.id})")
        self.stdout.write(f"Max initiatives: {options['max']}")

        survey_metadata = deliverable.metadata or {}
        repo_id = survey_metadata.get("repo_id") or workspace.name
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        self.stdout.write("\nCalling gpt-5-mini (json_object mode)…")
        items = _call_extract_llm(deliverable.content or "", options["max"])
        self.stdout.write(f"  Extracted {len(items)} candidate initiative(s)")

        if not items:
            self.stdout.write(self.style.WARNING(
                "No initiatives extracted. The survey may not have "
                "actionable recommendations."
            ))
            return

        for i, item in enumerate(items, 1):
            self.stdout.write(
                f"\n  [{i}] {item.get('name', '<no name>')}\n"
                f"      category={item.get('category')} "
                f"impact={item.get('impact_score')} "
                f"urgency={item.get('urgency')} "
                f"confidence={item.get('confidence')}"
            )

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("\nDRY RUN — no Initiative rows created."))
            return

        self.stdout.write("\nCreating Initiative rows…")
        created_ids: list[str] = []
        for item in items:
            initiative = _create_initiative(
                item=item,
                workspace=workspace,
                deliverable=deliverable,
                repo_id=repo_id,
                date_str=date_str,
                agent_name=deliverable.agent_name,
            )
            created_ids.append(str(initiative.id))
            self.stdout.write(f"  ✓ {initiative.id} — {initiative.name}")

        # Link the survey deliverable back to the first created Initiative
        # (Deliverable.initiative is single-FK; the rest live on
        # Initiative.target_workspace). Also store all ids in metadata.
        from core.models_deliverables import Deliverable
        survey_metadata.setdefault("auto_extracted", {})
        survey_metadata["auto_extracted"]["initiative_ids"] = created_ids
        survey_metadata["auto_extracted"]["extracted_at"] = (
            datetime.now(timezone.utc).isoformat(timespec="seconds")
        )
        survey_metadata["auto_extracted"]["count"] = len(created_ids)
        Deliverable.objects.filter(id=deliverable.id).update(
            metadata=survey_metadata,
        )

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("EXTRACTION COMPLETE"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(f"Initiatives created: {len(created_ids)}")
        self.stdout.write(f"All in status=TRIAGE — review and promote to ACTIVE.")
