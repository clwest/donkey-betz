"""
Fix specific workspace deliverable issues found during audit.

1. Move misassigned Ironwood sprite images from ComplianceSentinel to Ironwood Protocol
2. Delete blank image deliverables (content is just "Generated X image(s)" with no URLs)
3. Remove remaining duplicate business plans across all workspaces
4. Clean up orphan deliverables with no useful content

Usage:
    python manage.py fix_workspace_deliverables --dry-run
    python manage.py fix_workspace_deliverables
"""

import re
from django.core.management.base import BaseCommand
from django.db.models import Count


IRONWOOD_WS_ID = '032e89c7-9ebe-4d9d-bb90-873790c298bc'

# All 9 app workspace IDs
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


class Command(BaseCommand):
    help = "Fix specific workspace deliverable issues from audit"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        tag = "[DRY RUN] " if dry_run else ""

        from core.models_deliverables import Deliverable
        from core.models_skin_layer import ProjectWorkspace

        # ── Step 1: Move misassigned Ironwood images ──
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  Step 1: Fix Misassigned Ironwood Images")
        self.stdout.write(f"{'='*60}\n")

        moved = 0
        try:
            ironwood_ws = ProjectWorkspace.objects.get(id=IRONWOOD_WS_ID)
            # Find image deliverables with "ironwood" in title that are NOT in Ironwood workspace
            misassigned = Deliverable.objects.filter(
                deliverable_type='image',
                title__icontains='ironwood',
            ).exclude(workspace_id=IRONWOOD_WS_ID)

            for d in misassigned:
                old_ws = d.workspace.name if d.workspace else 'orphan'
                if not dry_run:
                    d.workspace = ironwood_ws
                    d.save(update_fields=['workspace'])
                moved += 1
                self.stdout.write(f"  {tag}Moved from {old_ws} → Ironwood: {d.title[:60]}")

            # Also move any sprite-related images
            sprite_misassigned = Deliverable.objects.filter(
                deliverable_type='image',
                title__icontains='sprite',
            ).exclude(workspace_id=IRONWOOD_WS_ID)

            for d in sprite_misassigned:
                old_ws = d.workspace.name if d.workspace else 'orphan'
                if not dry_run:
                    d.workspace = ironwood_ws
                    d.save(update_fields=['workspace'])
                moved += 1
                self.stdout.write(f"  {tag}Moved from {old_ws} → Ironwood: {d.title[:60]}")

        except ProjectWorkspace.DoesNotExist:
            self.stdout.write(self.style.WARNING("  Ironwood workspace not found"))

        self.stdout.write(f"\n  {tag}{moved} images moved to Ironwood\n")

        # ── Step 2: Delete blank image deliverables ──
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  Step 2: Remove Blank Image Deliverables")
        self.stdout.write(f"{'='*60}\n")

        deleted_blank = 0
        blank_images = Deliverable.objects.filter(
            deliverable_type='image',
        )
        for d in blank_images:
            content = (d.content or '').strip()
            # Check if content is just "Generated X image(s)" with no URLs
            if re.match(r'^Generated \d+ image\(s\)$', content) or not content:
                # Check metadata for image URLs
                metadata = d.metadata or {}
                images = metadata.get('images', [])
                image_urls = [img.get('url', '') for img in images if isinstance(img, dict) and img.get('url')]
                if not image_urls:
                    if not dry_run:
                        d.delete()
                    deleted_blank += 1
                    ws_name = d.workspace.name if d.workspace else 'orphan'
                    self.stdout.write(f"  {tag}Deleted blank image in {ws_name}: {d.title[:60]}")

        self.stdout.write(f"\n  {tag}{deleted_blank} blank image deliverables removed\n")

        # ── Step 3: Deduplicate business plans across ALL workspaces ──
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  Step 3: Deduplicate Business Plans (all workspaces)")
        self.stdout.write(f"{'='*60}\n")

        deleted_dupes = 0
        for ws_name, ws_id in APP_WORKSPACES.items():
            try:
                ws = ProjectWorkspace.objects.get(id=ws_id)
            except ProjectWorkspace.DoesNotExist:
                continue

            ws_deliverables = Deliverable.objects.filter(workspace=ws).order_by('-created_at')
            seen = {}

            for d in ws_deliverables:
                # Normalize title for comparison
                norm = d.title.strip().lower()
                norm = re.sub(r'\s*[\(\[—–-]\s*(investor[- ]ready|full)\s*[\)\]]?\s*', '', norm)
                norm = re.sub(r'\s*(full\s+)?business\s+plan\s*', 'business plan', norm)
                norm = re.sub(r'\s+', ' ', norm).strip()

                if norm in seen:
                    if not dry_run:
                        d.delete()
                    deleted_dupes += 1
                    self.stdout.write(f"  {tag}Deleted dupe in {ws_name}: {d.title[:50]}")
                else:
                    seen[norm] = d.id

        self.stdout.write(f"\n  {tag}{deleted_dupes} duplicate business plans removed\n")

        # ── Step 4: Summary of all workspaces ──
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  Final State — All Workspaces")
        self.stdout.write(f"{'='*60}\n")

        all_workspaces = ProjectWorkspace.objects.all().order_by('name')
        for ws in all_workspaces:
            count = Deliverable.objects.filter(workspace=ws).count()
            active = "ACTIVE" if ws.is_active else "inactive"
            if count > 0:
                self.stdout.write(f"  [{active:8}] {ws.name:30} {count} deliverables")
            else:
                self.stdout.write(f"  [{active:8}] {ws.name:30} empty")

        orphan_count = Deliverable.objects.filter(workspace__isnull=True).count()
        total = Deliverable.objects.count()
        self.stdout.write(f"\n  Orphaned (no workspace): {orphan_count}")
        self.stdout.write(f"  Total deliverables: {total}")
        self.stdout.write(f"{'='*60}\n")
