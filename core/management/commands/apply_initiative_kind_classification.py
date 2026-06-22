"""Session 1197 — Apply the locked Initiative-kind classification.

Sets ``kind`` on existing Initiative rows or creates new ones per the
11-row classification table locked in conversation pa-ea12236c83eb4826
(Rigby's Session 1197 design memo + Chris's agree-all ratification).

The 11 rows map to the 9 project-shaped clusters surfaced by the
Session 1193 cluster recon, with two clusters split into pairs
(3a/3b Spider Context Utilization; 9a/9b Weekend Digest Autopilot).
Split-pair rows are back-linked via the ``related_initiatives`` JSON
field using the directional ``spawns``/``spawned_from`` relation pair.

Default is **read-only dry-run**. ``--apply`` is the explicit opt-in.

Idempotent:
- Existing rows matched by explicit ID (preferred) or by exact name.
- Re-running the cmd is a no-op once kind is already set per SPEC.
- New-row creation is skipped if a row with the SPEC name already exists.
- Status is NOT touched — kind is orthogonal to lifecycle (per Rigby).

Output:
- Human-readable plan table
- JSON blob describing planned vs applied changes (machine-readable)

Usage:

  # Dry-run (default)
  python manage.py apply_initiative_kind_classification

  # Apply
  python manage.py apply_initiative_kind_classification --apply

  # Apply against a different workspace (default = Donkey Betz)
  python manage.py apply_initiative_kind_classification --apply \\
      --workspace-id <uuid>

  # JSON-only output
  python manage.py apply_initiative_kind_classification --json-only

Spec: docs/handoffs/SESSION_1193_DELIVERABLE_TAGGING_AND_PROJECT_CLUSTERING_INSIGHT.md
       docs/specs/DELIVERABLE_CLUSTERING_DEFERRED.md
"""

import json
from typing import Optional

from django.core.management.base import BaseCommand
from django.db import transaction


DONKEY_BETZ_WORKSPACE_ID = "b4503364-2573-4401-9e28-61a739e0ce50"


# ============================================================================
# SPEC — The 11-row classification table
# ============================================================================
# Locked design from Rigby's Session 1197 memo. Each row maps to one
# Initiative. `existing_id` is the known UUID when a matching row already
# exists in the DB; new rows are created when None.
#
# Schema:
#   key:           short stable key (1, 2, 3a, 3b, 4, 5, 6, 7, 8, 9a, 9b)
#   name:          canonical Initiative.name (used for new rows AND match fallback)
#   kind:          one of Initiative.Kind values
#   status:        target lifecycle status for NEW rows only — kind cmd does NOT
#                  reclassify status on existing rows (orthogonal axes)
#   existing_id:   UUID prefix of a known-existing row, or None to create
#   split_with:    sibling key for split-pair Initiatives (3a↔3b, 9a↔9b)
#   description:   stored on Initiative.description for new rows
# ============================================================================

SPEC = [
    {
        "key": "1",
        "name": "Session 1171 — ML Queue + Auth Middleware Triage",
        "kind": "project",
        "status": "ARCHIVED",  # existing 077ff8b4 is ARCHIVED — preserve
        "existing_id": "077ff8b4",
        "split_with": None,
        "description": (
            "Cluster wrapper for Session 1171 ML queue flood + auth "
            "middleware triage. Shipped via PR #2328. Has 4 sub-task "
            "Initiatives (1171-1/2/3/4) at status=COMPLETED."
        ),
    },
    {
        "key": "2",
        "name": "Session 1184 — Provenance Linkage",
        "kind": "project",
        "status": "COMPLETED",
        "existing_id": None,  # create new
        "split_with": None,
        "description": (
            "Cluster wrapper for Session 1184 provenance linkage work. "
            "Shipped via PRs #2362/#2364/#2365. Filed retroactively per "
            "Session 1197 Projects-in-Workspace-layer ship."
        ),
    },
    {
        "key": "3a",
        "name": "Spider Context Utilization — Recon & Findings",
        "kind": "investigation",
        "status": "COMPLETED",
        "existing_id": None,
        "split_with": "3b",
        "description": (
            "Recon half of the Spider Context Utilization workstream "
            "(Sessions 1187-1189). Six-axis recon produced findings + "
            "retune list. Recon side completes; impl side ('3b' Retune & "
            "Implementation) continues separately."
        ),
    },
    {
        "key": "3b",
        "name": "Spider Context Utilization — Retune & Implementation",
        "kind": "project",
        "status": "TRIAGE",
        "existing_id": None,
        "split_with": "3a",
        "description": (
            "Implementation half of the Spider Context Utilization "
            "workstream. Consumes the recon findings produced by '3a' "
            "Recon & Findings."
        ),
    },
    {
        "key": "4",
        "name": "Session 1192 — Workspace Consolidation Follow-ups",
        "kind": "spec_backlog",
        "status": "TRIAGE",
        "existing_id": None,
        "split_with": None,
        "description": (
            "spec_backlog wrapper for the 4 P2/P3 follow-ups filed during "
            "Session 1192 workspace consolidation: producer reroute, "
            "Initiative populate redesign, deliverable_tool tooling "
            "improvements, PA LLM iteration cap silent failure."
        ),
    },
    {
        "key": "5",
        "name": "COO Daily Analysis — Daily Run",
        "kind": "recurring_artifact",
        "status": "ACTIVE",
        "existing_id": None,
        "split_with": None,
        "description": (
            "Canonical container for the daily COO Analysis output stream. "
            "Replaces N independent deliverables with one Initiative "
            "holding periodic outputs."
        ),
    },
    {
        "key": "6",
        "name": "Orchestration Mapping Investigation — Parallel Agent Runs",
        "kind": "investigation",
        "status": "TRIAGE",
        "existing_id": None,
        "split_with": None,
        "description": (
            "Investigation container for the orchestration-control-plane "
            "mapping work — 11 parallel agent runs (CTO×3 + DevOps×4 + "
            "COO×1 + Research×3) on the same investigation. If this leads "
            "to implementation, spawn a separate kind=project Initiative "
            "via the rel:spawns: convention."
        ),
    },
    {
        "key": "7",
        "name": "Business News Tracker — June 2026",
        "kind": "recurring_artifact",
        "status": "ACTIVE",
        "existing_id": None,
        "split_with": None,
        "description": (
            "Content series Initiative for the Business News tracking "
            "beat in June 2026. Multiple ContentWriterAgent outputs on "
            "the same brief; treat as one stream, not N deliverables."
        ),
    },
    {
        "key": "8",
        "name": "MLB Run Line Desk v1 — 24h Board + DM Alerts",
        "kind": "project",
        "status": "ACTIVE",
        "existing_id": "997fb39b",
        "split_with": None,
        "description": (
            "Real 5-stage project Initiative for the MLB Run Line Desk v1 "
            "product spec. Cleanest example of the time-bounded project "
            "shape in the Donkey Betz pile."
        ),
    },
    {
        "key": "9a",
        "name": "Weekend Digest Autopilot — Build/Ship",
        "kind": "project",
        "status": "TRIAGE",  # existing 3e59354c is TRIAGE — preserve
        "existing_id": "3e59354c",
        "split_with": "9b",
        "description": (
            "Build/ship half of the Weekend Digest Autopilot workstream. "
            "Specs + test runs that produced the automation. Spawns '9b' "
            "Issue Production once the build completes."
        ),
    },
    {
        "key": "9b",
        "name": "Weekend Digest — Issue Production (Weekly)",
        "kind": "recurring_artifact",
        "status": "ACTIVE",
        "existing_id": None,
        "split_with": "9a",
        "description": (
            "Ongoing weekly issue production stream spawned from the "
            "Weekend Digest Autopilot build. Periodic outputs only — no "
            "5-stage arc."
        ),
    },
]


def _resolve_existing(initiative_model, spec_entry):
    """Resolve a SPEC entry to an existing Initiative row, or None."""
    if spec_entry["existing_id"]:
        match = initiative_model.objects.filter(
            id__startswith=spec_entry["existing_id"]
        ).first()
        if match:
            return match
    # Fallback: exact name match (idempotent re-run finds rows it created).
    return initiative_model.objects.filter(name=spec_entry["name"]).first()


def _build_related_link(sibling_init, relation):
    """Format a related_initiatives JSON entry."""
    return {
        "id": str(sibling_init.id),
        "relation": relation,
        "note": f"Session 1197 split-pair sibling: {sibling_init.name}",
    }


class Command(BaseCommand):
    help = (
        "Apply the Session 1197 Initiative-kind classification to the "
        "11 rows mapping the 9 Donkey Betz clusters. Default is dry-run; "
        "--apply executes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true",
            help="Execute the classification (default: dry-run).",
        )
        parser.add_argument(
            "--workspace-id", type=str, default=DONKEY_BETZ_WORKSPACE_ID,
            help=f"Target workspace UUID (default: Donkey Betz {DONKEY_BETZ_WORKSPACE_ID}).",
        )
        parser.add_argument(
            "--json-only", action="store_true",
            help="Suppress human-readable output; emit JSON only.",
        )

    def handle(self, *args, **opts):
        # Late import to keep CLI invocation fast even when Django isn't ready.
        from core.models_document_registry import Initiative

        plan = self._build_plan(Initiative, opts["workspace_id"])
        applied = None

        if opts["apply"]:
            applied = self._execute(Initiative, plan, opts["workspace_id"])

        report = {
            "workspace_id": opts["workspace_id"],
            "spec_rows": len(SPEC),
            "mode": "apply" if opts["apply"] else "dry-run",
            "plan": plan,
            "applied": applied,
        }

        if not opts["json_only"]:
            self._print_human(plan, applied)
        self.stdout.write(json.dumps(report, indent=2, default=str))

    def _build_plan(self, initiative_model, workspace_id):
        plan_rows = []
        for entry in SPEC:
            existing = _resolve_existing(initiative_model, entry)
            row = {
                "key": entry["key"],
                "name": entry["name"],
                "target_kind": entry["kind"],
                "split_with": entry["split_with"],
            }
            if existing:
                row["action"] = "update_existing"
                row["existing_id"] = str(existing.id)
                row["existing_kind"] = existing.kind
                row["existing_status"] = existing.status
                row["kind_changes"] = existing.kind != entry["kind"]
            else:
                row["action"] = "create_new"
                row["target_status"] = entry["status"]
                row["workspace_id"] = workspace_id
            plan_rows.append(row)
        return plan_rows

    @transaction.atomic
    def _execute(self, initiative_model, plan, workspace_id):
        """Apply the plan. Two-pass: create/update all rows first, then
        wire related_initiatives back-links for split pairs."""
        created_ids = {}
        updated_ids = {}
        for entry in SPEC:
            existing = _resolve_existing(initiative_model, entry)
            if existing:
                if existing.kind != entry["kind"]:
                    existing.kind = entry["kind"]
                    existing.save(update_fields=["kind", "updated_at"])
                    updated_ids[entry["key"]] = str(existing.id)
                created_ids[entry["key"]] = str(existing.id)
            else:
                new_init = initiative_model.objects.create(
                    name=entry["name"],
                    description=entry["description"],
                    status=entry["status"],
                    kind=entry["kind"],
                    target_workspace_id=workspace_id,
                    created_by="session-1197-kind-classifier",
                )
                created_ids[entry["key"]] = str(new_init.id)

        # Second pass: wire split-pair back-links.
        link_writes = []
        for entry in SPEC:
            if not entry["split_with"]:
                continue
            self_init = initiative_model.objects.get(id=created_ids[entry["key"]])
            sibling = initiative_model.objects.get(
                id=created_ids[entry["split_with"]]
            )
            # Directional convention: keys ending 'a' are upstream
            # (3a=Recon spawns 3b=Retune; 9a=Build/Ship spawns 9b=Issue
            # Production). Keys ending 'b' point back via spawned_from.
            relation = "spawns" if entry["key"].endswith("a") else "spawned_from"

            existing_links = self_init.related_initiatives or []
            link_entry = _build_related_link(sibling, relation)
            # Idempotent: skip if same (id, relation) pair already exists.
            already_linked = any(
                link.get("id") == link_entry["id"]
                and link.get("relation") == link_entry["relation"]
                for link in existing_links
            )
            if not already_linked:
                existing_links.append(link_entry)
                self_init.related_initiatives = existing_links
                self_init.save(update_fields=["related_initiatives", "updated_at"])
                link_writes.append({
                    "from": str(self_init.id),
                    "from_key": entry["key"],
                    "to": str(sibling.id),
                    "to_key": entry["split_with"],
                    "relation": relation,
                })

        return {
            "created_or_matched": created_ids,
            "kind_updated": updated_ids,
            "split_links_written": link_writes,
        }

    def _print_human(self, plan, applied):
        self.stdout.write("=" * 80)
        self.stdout.write("Session 1197 Initiative-Kind Classification — Plan")
        self.stdout.write("=" * 80)
        for row in plan:
            if row["action"] == "update_existing":
                kind_marker = "→" if row["kind_changes"] else "="
                self.stdout.write(
                    f"  [{row['key']:>3}] {row['action']:>16} "
                    f"id={row['existing_id'][:8]} "
                    f"kind={row['existing_kind']} {kind_marker} {row['target_kind']} "
                    f"(status={row['existing_status']}) "
                    f"— {row['name'][:60]}"
                )
            else:
                self.stdout.write(
                    f"  [{row['key']:>3}] {row['action']:>16} "
                    f"kind={row['target_kind']} status={row['target_status']} "
                    f"— {row['name'][:60]}"
                )
        if applied:
            self.stdout.write("-" * 80)
            self.stdout.write(f"APPLIED. Created/matched: {len(applied['created_or_matched'])} "
                              f"rows. Kind updates: {len(applied['kind_updated'])}. "
                              f"Split-link writes: {len(applied['split_links_written'])}.")
        else:
            self.stdout.write("-" * 80)
            self.stdout.write("DRY-RUN — pass --apply to execute.")
        self.stdout.write("=" * 80)
