"""
Management command: Backfill workspace FK on ImageHistory, VideoHistory, AudioHistory.

Matches existing media records to workspaces using the record's user field
and their active (or most recently updated) workspace.

Usage:
    # Dry run
    python manage.py backfill_media_workspaces

    # Apply
    python manage.py backfill_media_workspaces --apply
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Backfill workspace FK on media models (ImageHistory, VideoHistory, AudioHistory)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply', action='store_true',
            help='Actually apply changes (default is dry run)',
        )

    def handle(self, *args, **options):
        apply = options['apply']
        from content.models import ImageHistory, VideoHistory, AudioHistory
        from core.models_skin_layer import ProjectWorkspace
        from django.contrib.auth import get_user_model
        User = get_user_model()

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\n{'APPLYING' if apply else 'DRY RUN'}: Media Workspace Backfill"
        ))

        # Build user → workspace mapping (active workspace, or most recent)
        user_ws_map = {}
        for ws in ProjectWorkspace.objects.select_related('user').order_by('-updated_at'):
            uid = ws.user_id
            if uid and uid not in user_ws_map:
                # Prefer active workspace
                if ws.is_active:
                    user_ws_map[uid] = ws
                elif uid not in user_ws_map:
                    user_ws_map[uid] = ws

        # Also map by active workspace specifically
        for ws in ProjectWorkspace.objects.filter(is_active=True).select_related('user'):
            if ws.user_id:
                user_ws_map[ws.user_id] = ws

        self.stdout.write(f"User→Workspace mappings: {len(user_ws_map)}")

        total_fixed = 0

        for model_name, Model in [
            ('ImageHistory', ImageHistory),
            ('VideoHistory', VideoHistory),
            ('AudioHistory', AudioHistory),
        ]:
            orphans = Model.objects.filter(workspace__isnull=True).select_related('user')
            total = orphans.count()

            if total == 0:
                self.stdout.write(f"  {model_name}: 0 records without workspace")
                continue

            matched = 0
            unmatched = 0

            for record in orphans.iterator():
                ws = user_ws_map.get(record.user_id)
                if ws:
                    if apply:
                        Model.objects.filter(id=record.id).update(workspace=ws)
                    matched += 1
                else:
                    unmatched += 1

            total_fixed += matched

            if apply:
                self.stdout.write(self.style.SUCCESS(
                    f"  {model_name}: {matched}/{total} linked to workspaces "
                    f"({unmatched} unmatched — no workspace for user)"
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"  {model_name}: {matched}/{total} can be linked "
                    f"({unmatched} unmatched)"
                ))

        self.stdout.write(self.style.MIGRATE_HEADING("\n--- Summary ---"))
        if apply:
            self.stdout.write(self.style.SUCCESS(f"Total media records linked: {total_fixed}"))
        else:
            self.stdout.write(self.style.WARNING(
                f"Total media records to link: {total_fixed} (run with --apply)"
            ))
