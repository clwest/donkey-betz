"""
Consolidate duplicate workspaces and assign orphaned deliverables.

1. Merge duplicate workspaces (move deliverables to primary, delete empty duplicate)
2. Assign orphaned deliverables to correct workspaces by content analysis
3. Report final state

Usage:
    python manage.py consolidate_workspaces --dry-run
    python manage.py consolidate_workspaces
"""

import re
from django.core.management.base import BaseCommand


# Duplicate workspace pairs: (keep, delete)
MERGE_PAIRS = [
    ('Contract Concierge', 'Contract Concierge Workspace'),
    ('MentorForge', 'MentorForge Workspace'),
    ('SignalStudio', 'SignalStudio Workspace'),
]

# Orphan assignment rules: regex pattern → workspace name
ORPHAN_RULES = [
    (r'(?i)newsletter.*v3|newsletter.*final.*test', 'Operator Edge — AI Newsletter Studio'),
    (r'(?i)why most ai teams|demo stage', 'Operator Edge — AI Newsletter Studio'),
    (r'(?i)autopilot ops|autopilot.*newsletter', 'Donkey Betz — Autopilot Ops Newsletter'),
    (r'(?i)producer owned reinsurance', 'Producer Owned Reinsurance'),
    (r'(?i)PR Checklist.*ResearchAgent', 'Donkey Betz'),
    (r'(?i)Tool Verification', 'Donkey Betz'),
    (r'(?i)Conversation Summary.*Workspace', 'Donkey Betz'),
    (r'(?i)workspace.*2028cb11', 'Donkey Betz — Autopilot Ops Newsletter'),
    (r'(?i)blog_post.*newsletter', 'Operator Edge — AI Newsletter Studio'),
    (r'(?i)blog_post.*workspace\s+6', 'Operator Edge — AI Newsletter Studio'),
    (r'(?i)topic mining.*spider|trend.*feeds', 'Operator Edge — AI Newsletter Studio'),
]


class Command(BaseCommand):
    help = "Consolidate duplicate workspaces and assign orphans"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        tag = "[DRY RUN] " if dry_run else ""

        from core.models_deliverables import Deliverable
        from core.models_skin_layer import ProjectWorkspace

        # ── Step 1: Merge duplicate workspaces ──
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  Step 1: Merge Duplicate Workspaces")
        self.stdout.write(f"{'='*60}\n")

        merged = 0
        for keep_name, delete_name in MERGE_PAIRS:
            keep_ws = ProjectWorkspace.objects.filter(name=keep_name).first()
            delete_ws = ProjectWorkspace.objects.filter(name=delete_name).first()

            if not keep_ws or not delete_ws:
                self.stdout.write(f"  Skipped: {keep_name} / {delete_name} (not found)")
                continue

            # Move deliverables from delete_ws to keep_ws
            move_count = Deliverable.objects.filter(workspace=delete_ws).count()
            if move_count > 0:
                if not dry_run:
                    Deliverable.objects.filter(workspace=delete_ws).update(workspace=keep_ws)
                self.stdout.write(f"  {tag}Moved {move_count} deliverables: {delete_name} → {keep_name}")
                merged += move_count

            # Delete the empty duplicate workspace
            remaining = Deliverable.objects.filter(workspace=delete_ws).count() if dry_run else 0
            if remaining == 0 or not dry_run:
                if not dry_run:
                    delete_ws.delete()
                self.stdout.write(f"  {tag}Deleted empty workspace: {delete_name}")

        # Also handle duplicate Newsletter Studio
        ns_with = ProjectWorkspace.objects.filter(name='Newsletter Studio').order_by('-updated_at')
        if ns_with.count() > 1:
            keep = None
            for ws in ns_with:
                c = Deliverable.objects.filter(workspace=ws).count()
                if c > 0 and not keep:
                    keep = ws
                elif keep and c == 0:
                    if not dry_run:
                        ws.delete()
                    self.stdout.write(f"  {tag}Deleted empty duplicate: Newsletter Studio ({ws.id})")
                elif keep and c > 0:
                    if not dry_run:
                        Deliverable.objects.filter(workspace=ws).update(workspace=keep)
                        ws.delete()
                    self.stdout.write(f"  {tag}Merged {c} deliverables and deleted duplicate Newsletter Studio")
                    merged += c

        self.stdout.write(f"\n  {tag}{merged} deliverables merged\n")

        # ── Step 2: Assign orphaned deliverables ──
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  Step 2: Assign Orphaned Deliverables")
        self.stdout.write(f"{'='*60}\n")

        orphans = Deliverable.objects.filter(workspace__isnull=True)
        total_orphans = orphans.count()
        assigned = 0

        # Cache workspace lookups
        ws_cache = {}
        for name in set(ws_name for _, ws_name in ORPHAN_RULES):
            ws = ProjectWorkspace.objects.filter(name=name).first()
            if ws:
                ws_cache[name] = ws

        for d in orphans:
            title = d.title or ''
            matched_ws_name = None

            for pattern, ws_name in ORPHAN_RULES:
                if re.search(pattern, title):
                    matched_ws_name = ws_name
                    break

            if matched_ws_name and matched_ws_name in ws_cache:
                if not dry_run:
                    d.workspace = ws_cache[matched_ws_name]
                    d.save(update_fields=['workspace'])
                assigned += 1
                self.stdout.write(f"  {tag}→ {matched_ws_name}: {title[:55]}")

        self.stdout.write(f"\n  {tag}{assigned}/{total_orphans} orphans assigned\n")

        # ── Final state ──
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  Final State")
        self.stdout.write(f"{'='*60}\n")

        remaining_orphans = Deliverable.objects.filter(workspace__isnull=True).count() if not dry_run else total_orphans - assigned
        total = Deliverable.objects.count() if not dry_run else "N/A"
        all_ws = ProjectWorkspace.objects.all().order_by('name')
        for ws in all_ws:
            c = Deliverable.objects.filter(workspace=ws).count()
            if c > 0:
                self.stdout.write(f"  {ws.name:50} {c:>3} deliverables")

        self.stdout.write(f"\n  Remaining orphans: {remaining_orphans}")
        self.stdout.write(f"  Total deliverables: {total}")
        self.stdout.write(f"{'='*60}\n")
