"""Session 1197 — Backfill-safety report for Initiative.kind classification.

Read-only diagnostic command per Rigby's Session 1197 design memo:
"Right after the apply step: run a dry-run report that shows counts by
kind/status and flags 'project initiatives that look recurring'
(heuristic: same title prefix, many similar deliverables) — even if
it's just printed counts, not an ML classifier."

Three signals surfaced:

1. **Cross-tab counts** (kind × status) — what the population looks like
   post-classification. Sanity check that the apply cmd landed expected
   distribution shape.

2. **Title-prefix clustering** — multiple Initiatives sharing a name
   prefix often signal a recurring artifact stream filed as N separate
   project rows (the failure mode the kind enum was designed to fix).
   Flags clusters of 3+ Initiatives sharing the first 24 chars of name.

3. **High deliverable count on a project** — a project Initiative with
   10+ deliverables attached may actually be a recurring artifact.
   (Heuristic only — a real long-arc project can also have many
   deliverables.)

4. **Default-only projects** — project Initiatives not named in the
   ``apply_initiative_kind_classification`` SPEC. Surfaces silent
   "everything is project" rot from rows that got the default kind
   at migration time but were never explicitly classified. Added
   Session 1197 close-out per Rigby's design memo addendum.

Usage:

  python manage.py report_initiative_kinds
  python manage.py report_initiative_kinds --workspace-id <uuid>
  python manage.py report_initiative_kinds --json-only
"""

import json
from collections import Counter, defaultdict

from django.core.management.base import BaseCommand


DONKEY_BETZ_WORKSPACE_ID = "b4503364-2573-4401-9e28-61a739e0ce50"
PREFIX_LEN = 24
PREFIX_CLUSTER_MIN = 3
HIGH_DELIVERABLE_COUNT = 10


class Command(BaseCommand):
    help = (
        "Read-only report over Initiative.kind classification. "
        "Cross-tab counts + heuristic flags for project rows that "
        "look like recurring artifacts."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--workspace-id", type=str, default=None,
            help=(
                "Scope to a single workspace. Default reports across all. "
                f"Donkey Betz: {DONKEY_BETZ_WORKSPACE_ID}"
            ),
        )
        parser.add_argument(
            "--json-only", action="store_true",
            help="Emit JSON only (suppress human-readable tables).",
        )

    def handle(self, *args, **opts):
        from core.models_document_registry import Initiative

        qs = Initiative.objects.all()
        if opts["workspace_id"]:
            qs = qs.filter(target_workspace_id=opts["workspace_id"])

        cross_tab = self._cross_tab(qs)
        prefix_clusters = self._prefix_clusters(qs)
        high_deliverable_projects = self._high_deliverable_projects(qs)
        default_only_projects = self._default_only_projects(qs)

        report = {
            "scope": opts["workspace_id"] or "all_workspaces",
            "total_initiatives": qs.count(),
            "cross_tab": cross_tab,
            "prefix_clusters": prefix_clusters,
            "high_deliverable_projects": high_deliverable_projects,
            "default_only_projects": default_only_projects,
        }

        if not opts["json_only"]:
            self._print_human(report)
        self.stdout.write(json.dumps(report, indent=2, default=str))

    def _cross_tab(self, qs):
        cell_counts = Counter()
        for kind, status in qs.values_list("kind", "status"):
            cell_counts[(kind, status)] += 1
        # Restructure as nested dict for readable JSON.
        nested = defaultdict(dict)
        for (kind, status), count in cell_counts.items():
            nested[kind][status] = count
        return dict(nested)

    def _prefix_clusters(self, qs):
        """Group project Initiatives by name prefix; flag clusters of 3+."""
        buckets = defaultdict(list)
        for init_id, name, kind in qs.values_list("id", "name", "kind"):
            if kind != "project":
                continue
            prefix = (name or "")[:PREFIX_LEN].strip()
            buckets[prefix].append({"id": str(init_id), "name": name})
        return [
            {
                "prefix": prefix,
                "count": len(rows),
                "members": rows,
                "note": "Same prefix on 3+ project rows may indicate a recurring_artifact stream filed as N projects.",
            }
            for prefix, rows in buckets.items()
            if len(rows) >= PREFIX_CLUSTER_MIN
        ]

    def _high_deliverable_projects(self, qs):
        """Project Initiatives with high deliverable counts may be misclassified."""
        results = []
        for init in qs.filter(kind="project"):
            count = init.deliverables.count()
            if count >= HIGH_DELIVERABLE_COUNT:
                results.append({
                    "id": str(init.id),
                    "name": init.name,
                    "status": init.status,
                    "deliverable_count": count,
                    "note": f"{count} deliverables on a project — review for recurring_artifact reclassification.",
                })
        return sorted(results, key=lambda r: -r["deliverable_count"])

    def _default_only_projects(self, qs):
        """Project Initiatives not named in the apply SPEC — silent default rot.

        Rationale (Rigby's Session 1197 close-out): default=project is a
        safe placeholder, not a semantic assertion. Rows that received
        the default via migration but were never explicitly classified
        sit in a grey zone — they LOOK classified but operationally
        weren't reviewed. This detector surfaces them so an operator can
        confirm "yes, project is right" or reclassify.
        """
        # Late import — avoid hard coupling to the apply module at
        # report-cmd import time (it's a peer mgmt cmd).
        from core.management.commands.apply_initiative_kind_classification import (
            SPEC as KIND_SPEC,
        )
        spec_names = {entry["name"] for entry in KIND_SPEC}
        results = []
        for init in qs.filter(kind="project"):
            if init.name in spec_names:
                continue
            results.append({
                "id": str(init.id),
                "name": init.name,
                "status": init.status,
                "note": (
                    "Project Initiative not named in apply SPEC — "
                    "verify the classification is intentional, not "
                    "default-rot from the migration."
                ),
            })
        return results

    def _print_human(self, report):
        self.stdout.write("=" * 80)
        self.stdout.write(
            f"Initiative-kind report — scope={report['scope']}, "
            f"total={report['total_initiatives']}"
        )
        self.stdout.write("=" * 80)
        self.stdout.write("\n[1] Cross-tab counts (kind × status):")
        for kind, status_counts in sorted(report["cross_tab"].items()):
            self.stdout.write(f"  {kind}:")
            for status, count in sorted(status_counts.items()):
                self.stdout.write(f"    {status:12} = {count}")

        self.stdout.write(
            f"\n[2] Project Initiatives sharing a name prefix "
            f"(≥{PREFIX_CLUSTER_MIN} rows, first {PREFIX_LEN} chars):"
        )
        if not report["prefix_clusters"]:
            self.stdout.write("  (no suspicious clusters)")
        for cluster in report["prefix_clusters"]:
            self.stdout.write(f"  prefix='{cluster['prefix']}' — {cluster['count']} rows:")
            for member in cluster["members"][:5]:
                self.stdout.write(f"    {member['id'][:8]} {member['name'][:60]}")
            if len(cluster["members"]) > 5:
                self.stdout.write(f"    ... +{len(cluster['members']) - 5} more")

        self.stdout.write(
            f"\n[3] Project Initiatives with ≥{HIGH_DELIVERABLE_COUNT} deliverables "
            "(possible recurring_artifact misclassification):"
        )
        if not report["high_deliverable_projects"]:
            self.stdout.write("  (none flagged)")
        for project in report["high_deliverable_projects"][:10]:
            self.stdout.write(
                f"  {project['id'][:8]} ({project['deliverable_count']:>3} deliverables) "
                f"{project['name'][:60]}"
            )

        self.stdout.write(
            "\n[4] Project Initiatives not named in apply SPEC "
            "(default-only — silent default-rot detector):"
        )
        default_only = report["default_only_projects"]
        if not default_only:
            self.stdout.write("  (none flagged — all project rows are SPEC-classified)")
        else:
            self.stdout.write(f"  {len(default_only)} project rows in scope but not in SPEC:")
            for project in default_only[:10]:
                self.stdout.write(
                    f"    {project['id'][:8]} status={project['status']:10} {project['name'][:60]}"
                )
            if len(default_only) > 10:
                self.stdout.write(f"    ... +{len(default_only) - 10} more")

        self.stdout.write("=" * 80)
