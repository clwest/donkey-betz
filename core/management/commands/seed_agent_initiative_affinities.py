"""Session 1198 — Seed static AgentInitiativeAffinity rows for the
§6.2 Phase 2 inference cascade.

Bootstrap seed list is intentionally **conservative** — only pin
agents we're confident about. Aggressive seeding can cause wrong
auto-attachments. The inference cascade ALSO requires kind-policy
checks at runtime, so even a seeded row only fires if the target
Initiative satisfies the recency + kind constraints (see
``initiative_inference.infer_initiative_id``, PR1C).

Default is **dry-run**. ``--apply`` is the explicit opt-in.

Idempotent:
- Existing rows matched by (workspace_id, agent_name, initiative_id)
  triple (unique constraint).
- Re-running the cmd is a no-op once SPEC rows exist.

Usage:

  # Dry-run (default)
  python manage.py seed_agent_initiative_affinities

  # Apply
  python manage.py seed_agent_initiative_affinities --apply

  # Apply against a different workspace (default = Donkey Betz)
  python manage.py seed_agent_initiative_affinities --apply \\
      --workspace-id <uuid>

  # JSON output only
  python manage.py seed_agent_initiative_affinities --json-only

Spec: docs/specs/INITIATIVES_FIRST_BACKBONE.md §6.2 (PR1E will land
the full design write-up).
"""

import json

from django.core.management.base import BaseCommand
from django.db import transaction


DONKEY_BETZ_WORKSPACE_ID = "b4503364-2573-4401-9e28-61a739e0ce50"


# ============================================================================
# SPEC — static seed affinities
# ============================================================================
#
# Each entry is a conservative pin. Rationale lives in `notes`. Add new
# pins via PR (preferred — code-reviewable) or via the manual_pin path
# (operator escape hatch — Phase 2 follow-up).
#
# Top orphan creators NOT seeded here + why:
# - Rigby (33 orphans): coordinator agent that touches every workstream;
#   no single Initiative is the right default. Let inference fall
#   through to heuristics (PR3) or diagnostic mark.
# - ContentWriterAgent (9 orphans): natural target is
#   `Business News Tracker — June 2026` (kind=recurring_artifact).
#   recurring_artifact is hard-blocked from auto-attach in §6.2 Step 3.
#   Operator-pin via manual_pin if needed.
# ============================================================================

SPEC = [
    {
        "agent_name": "ResearchAgent",
        "initiative_id": "23cf3acb-6554-407d-958b-4298b44ddfd6",
        "initiative_name": "Spider Context Utilization — Retune & Implementation",
        "confidence": 0.92,
        "notes": (
            "ResearchAgent owned the Session 1187-1189 6-axis recon "
            "that produced this Initiative's retune list. Natural "
            "follow-on attachment for its outputs."
        ),
    },
    {
        "agent_name": "ClaudeCode",
        "initiative_id": "6941372d-b13c-4631-91c8-749fa65c55a0",
        "initiative_name": "Initiatives-First Wiring + No-Orphan Output",
        "confidence": 0.90,
        "notes": (
            "ClaudeCode shipped the backbone work across Sessions 1194-"
            "1198 (Plan C Phase 1, Session 1196 initiative diagnostic, "
            "Session 1197 kind enum, this Session 1198 inference). "
            "Default attach target for new ClaudeCode deliverables "
            "without an explicit initiative_id."
        ),
    },
]


def _resolve_workspace(workspace_id):
    from core.models_skin_layer import ProjectWorkspace
    return ProjectWorkspace.objects.filter(id=workspace_id).first()


def _resolve_initiative(initiative_id):
    from core.models_document_registry import Initiative
    return Initiative.objects.filter(id=initiative_id).first()


class Command(BaseCommand):
    help = (
        "Seed static AgentInitiativeAffinity rows for §6.2 Phase 2 "
        "inference. Default is dry-run; --apply executes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true",
            help="Execute the seed inserts (default: dry-run).",
        )
        parser.add_argument(
            "--workspace-id", type=str, default=DONKEY_BETZ_WORKSPACE_ID,
            help=f"Target workspace UUID (default: Donkey Betz {DONKEY_BETZ_WORKSPACE_ID}).",
        )
        parser.add_argument(
            "--json-only", action="store_true",
            help="Emit JSON only; suppress human-readable output.",
        )

    def handle(self, *args, **opts):
        from core.models_inference import AgentInitiativeAffinity

        workspace = _resolve_workspace(opts["workspace_id"])
        if not workspace:
            raise SystemExit(f"Workspace {opts['workspace_id']} not found.")

        plan = self._build_plan(AgentInitiativeAffinity, workspace)
        applied = None

        if opts["apply"]:
            applied = self._execute(AgentInitiativeAffinity, plan, workspace)

        report = {
            "workspace_id": str(workspace.id),
            "spec_rows": len(SPEC),
            "mode": "apply" if opts["apply"] else "dry-run",
            "plan": plan,
            "applied": applied,
        }

        if not opts["json_only"]:
            self._print_human(plan, applied)
        self.stdout.write(json.dumps(report, indent=2, default=str))

    def _build_plan(self, model, workspace):
        plan_rows = []
        for entry in SPEC:
            initiative = _resolve_initiative(entry["initiative_id"])
            if not initiative:
                plan_rows.append({
                    "agent_name": entry["agent_name"],
                    "action": "skip_no_initiative",
                    "initiative_id": entry["initiative_id"],
                    "reason": "Initiative not found in DB",
                })
                continue
            if initiative.target_workspace_id and \
                    str(initiative.target_workspace_id) != str(workspace.id):
                plan_rows.append({
                    "agent_name": entry["agent_name"],
                    "action": "skip_wrong_workspace",
                    "initiative_id": str(initiative.id),
                    "initiative_workspace": str(initiative.target_workspace_id),
                    "target_workspace": str(workspace.id),
                })
                continue

            existing = model.objects.filter(
                workspace=workspace,
                agent_name=entry["agent_name"],
                initiative=initiative,
            ).first()
            if existing:
                plan_rows.append({
                    "agent_name": entry["agent_name"],
                    "action": "exists",
                    "id": str(existing.id),
                    "initiative_name": entry["initiative_name"],
                })
            else:
                plan_rows.append({
                    "agent_name": entry["agent_name"],
                    "action": "create",
                    "initiative_id": str(initiative.id),
                    "initiative_name": entry["initiative_name"],
                    "kind": initiative.kind,
                    "confidence": entry["confidence"],
                })
        return plan_rows

    @transaction.atomic
    def _execute(self, model, plan, workspace):
        created_ids = []
        for row in plan:
            if row["action"] != "create":
                continue
            entry = next(e for e in SPEC if e["agent_name"] == row["agent_name"])
            obj = model.objects.create(
                workspace=workspace,
                agent_name=entry["agent_name"],
                initiative_id=entry["initiative_id"],
                confidence=entry["confidence"],
                source=model.Source.STATIC_SEED,
                notes=entry["notes"],
            )
            created_ids.append(str(obj.id))
        return {"created_ids": created_ids, "skipped": len(plan) - len(created_ids)}

    def _print_human(self, plan, applied):
        self.stdout.write("=" * 80)
        self.stdout.write("Session 1198 AgentInitiativeAffinity seed plan")
        self.stdout.write("=" * 80)
        for row in plan:
            if row["action"] == "create":
                self.stdout.write(
                    f"  {row['agent_name']:<24} → {row['initiative_name'][:50]} "
                    f"(kind={row['kind']}, conf={row['confidence']})"
                )
            elif row["action"] == "exists":
                self.stdout.write(
                    f"  {row['agent_name']:<24} = (already pinned) {row['initiative_name'][:50]}"
                )
            else:
                self.stdout.write(f"  {row['agent_name']:<24} ! SKIP — {row['action']}")
        if applied:
            self.stdout.write("-" * 80)
            self.stdout.write(
                f"APPLIED. Created: {len(applied['created_ids'])} rows. "
                f"Skipped (exists/error): {applied['skipped']}."
            )
        else:
            self.stdout.write("-" * 80)
            self.stdout.write("DRY-RUN — pass --apply to execute.")
        self.stdout.write("=" * 80)
