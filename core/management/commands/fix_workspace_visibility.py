"""
Fix workspace visibility and deliverable assignment on Railway.

1. Activate all 9 app workspaces
2. Assign orphaned deliverables to correct workspaces by title matching
3. Deduplicate business plans (keep newest, delete older copies)

Usage:
    python manage.py fix_workspace_visibility --dry-run
    python manage.py fix_workspace_visibility
"""

import re
from django.core.management.base import BaseCommand
from django.db.models import Count


# Workspace IDs from Railway
APP_WORKSPACES = {
    'Ironwood Protocol': '032e89c7-9ebe-4d9d-bb90-873790c298bc',
    'ComplianceSentinel': '187ed794-edc1-421f-ba5a-9b151128a2c3',
    'MentorForge': 'f85a2066-992f-4450-92c0-c1aadf0222f4',
    'DealFlowTracker': '6d2fd306-82b0-4287-875e-901dc45b1d06',
    'SignalStudio': 'bfed742d-7b53-459f-aa6a-ff269232fc63',
    'SellerPilot': '1258d765-5d84-47c0-832b-138ebf4bc88f',
    'Contract Concierge': 'f80d7f7d-29a8-4aa8-8b51-699a3dbe03bb',
    'ScoutPlays': 'cc437f2f-23cf-4d8c-88a4-010fdfe0ca26',
    'PitchDeckForge': '39522dab-8fdc-4a99-b1aa-8bdfbdb7387b',
}

# Title patterns to match orphaned deliverables to workspaces
TITLE_PATTERNS = {
    'Ironwood Protocol': [r'(?i)ironwood'],
    'ComplianceSentinel': [r'(?i)compliance\s*sentinel'],
    'MentorForge': [r'(?i)mentor\s*forge'],
    'DealFlowTracker': [r'(?i)deal\s*flow\s*tracker'],
    'SignalStudio': [r'(?i)signal\s*studio'],
    'SellerPilot': [r'(?i)seller\s*pilot'],
    'Contract Concierge': [r'(?i)contract\s*concierge'],
    'ScoutPlays': [r'(?i)scout\s*plays'],
    'PitchDeckForge': [r'(?i)pitch\s*deck\s*forge'],
}


class Command(BaseCommand):
    help = "Fix workspace visibility and deliverable assignment"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        tag = "[DRY RUN] " if dry_run else ""

        from core.models_deliverables import Deliverable
        from core.models_skin_layer import ProjectWorkspace

        # ── Step 1: Activate all app workspaces ──
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  Step 1: Activate App Workspaces")
        self.stdout.write(f"{'='*60}\n")

        activated = 0
        for name, ws_id in APP_WORKSPACES.items():
            try:
                ws = ProjectWorkspace.objects.get(id=ws_id)
                if not ws.is_active:
                    if not dry_run:
                        ws.is_active = True
                        ws.save(update_fields=['is_active'])
                    activated += 1
                    self.stdout.write(self.style.SUCCESS(f"  {tag}Activated: {name}"))
                else:
                    self.stdout.write(f"  Already active: {name}")
            except ProjectWorkspace.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  NOT FOUND: {name} ({ws_id})"))

        self.stdout.write(f"\n  {tag}{activated} workspaces activated\n")

        # ── Step 2: Assign orphaned deliverables ──
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  Step 2: Assign Orphaned Deliverables")
        self.stdout.write(f"{'='*60}\n")

        orphans = Deliverable.objects.filter(workspace__isnull=True)
        total_orphans = orphans.count()
        self.stdout.write(f"  Found {total_orphans} orphaned deliverables\n")

        assigned = 0
        for deliverable in orphans:
            title = deliverable.title or ''
            matched_ws = None

            for ws_name, patterns in TITLE_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, title):
                        matched_ws = ws_name
                        break
                if matched_ws:
                    break

            if matched_ws:
                ws_id = APP_WORKSPACES[matched_ws]
                if not dry_run:
                    try:
                        ws = ProjectWorkspace.objects.get(id=ws_id)
                        deliverable.workspace = ws
                        deliverable.save(update_fields=['workspace'])
                    except ProjectWorkspace.DoesNotExist:
                        continue
                assigned += 1
                self.stdout.write(f"  {tag}Assigned to {matched_ws}: {title[:60]}")

        self.stdout.write(f"\n  {tag}{assigned}/{total_orphans} orphans assigned to workspaces\n")

        # ── Step 3: Deduplicate business plans ──
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  Step 3: Deduplicate Business Plans")
        self.stdout.write(f"{'='*60}\n")

        # Find titles that appear more than once within the same workspace
        deleted = 0
        for ws_name, ws_id in APP_WORKSPACES.items():
            try:
                ws = ProjectWorkspace.objects.get(id=ws_id)
            except ProjectWorkspace.DoesNotExist:
                continue

            # Get deliverables in this workspace grouped by normalized title
            ws_deliverables = Deliverable.objects.filter(workspace=ws).order_by('-created_at')
            seen_titles = {}

            for d in ws_deliverables:
                # Normalize: strip whitespace, lowercase, remove "(Investor-Ready)" suffix
                norm = re.sub(r'\s*\(investor[- ]ready\)\s*', '', d.title.strip(), flags=re.IGNORECASE).lower()
                norm = re.sub(r'\s+', ' ', norm)

                if norm in seen_titles:
                    # This is a duplicate — delete the older one (we ordered by -created_at, so first seen is newest)
                    if not dry_run:
                        d.delete()
                    deleted += 1
                    self.stdout.write(f"  {tag}Deleted duplicate in {ws_name}: {d.title[:50]}")
                else:
                    seen_titles[norm] = d.id

        # Also deduplicate orphans (deliverables without workspace that have identical titles)
        orphan_dupes = (
            Deliverable.objects.filter(workspace__isnull=True)
            .values('title')
            .annotate(cnt=Count('id'))
            .filter(cnt__gt=1)
        )
        for group in orphan_dupes:
            dupes = Deliverable.objects.filter(
                workspace__isnull=True, title=group['title']
            ).order_by('-created_at')
            # Keep newest, delete rest
            for d in dupes[1:]:
                if not dry_run:
                    d.delete()
                deleted += 1

        self.stdout.write(f"\n  {tag}{deleted} duplicates removed\n")

        # ── Summary ──
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  Summary")
        self.stdout.write(f"{'='*60}")
        remaining_orphans = Deliverable.objects.filter(workspace__isnull=True).count() if not dry_run else total_orphans - assigned
        total_remaining = Deliverable.objects.count() if not dry_run else "N/A (dry run)"
        self.stdout.write(f"  Workspaces activated: {activated}")
        self.stdout.write(f"  Orphans assigned: {assigned}")
        self.stdout.write(f"  Duplicates removed: {deleted}")
        self.stdout.write(f"  Remaining orphans: {remaining_orphans}")
        self.stdout.write(f"  Total deliverables: {total_remaining}")
        self.stdout.write(f"{'='*60}\n")
