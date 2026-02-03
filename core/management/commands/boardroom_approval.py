"""
Session 914.6: Boardroom Approval Management

Management command to approve, revoke, or check boardroom approval for initiatives.

Usage:
    # List initiatives requiring boardroom approval
    python manage.py boardroom_approval --list-pending

    # Approve an initiative
    python manage.py boardroom_approval --approve <uuid> --by="founder" --notes="Reviewed and approved"

    # Revoke approval
    python manage.py boardroom_approval --revoke <uuid> --reason="Needs re-review"

    # Show approval status for an initiative
    python manage.py boardroom_approval --status <uuid>

    # Bulk approve all initiatives with founder intent set
    python manage.py boardroom_approval --auto-approve-with-intent
"""

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Manage boardroom approval for initiatives'

    def add_arguments(self, parser):
        parser.add_argument(
            '--list-pending',
            action='store_true',
            help='List all initiatives pending boardroom approval'
        )
        parser.add_argument(
            '--approve',
            type=str,
            help='Initiative UUID to approve'
        )
        parser.add_argument(
            '--by',
            type=str,
            default='boardroom',
            help='Who is approving (default: boardroom)'
        )
        parser.add_argument(
            '--notes',
            type=str,
            default='',
            help='Approval notes or conditions'
        )
        parser.add_argument(
            '--revoke',
            type=str,
            help='Initiative UUID to revoke approval'
        )
        parser.add_argument(
            '--reason',
            type=str,
            default='',
            help='Reason for revoking approval'
        )
        parser.add_argument(
            '--status',
            type=str,
            help='Initiative UUID to check status'
        )
        parser.add_argument(
            '--auto-approve-with-intent',
            action='store_true',
            help='Auto-approve all initiatives that have founder intent set'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would happen without making changes'
        )

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative

        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write(self.style.HTTP_INFO('Session 914.6: Boardroom Approval'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60))

        # List pending
        if options['list_pending']:
            self._list_pending()
            return

        # Approve
        if options['approve']:
            self._approve_initiative(
                options['approve'],
                options['by'],
                options['notes']
            )
            return

        # Revoke
        if options['revoke']:
            self._revoke_approval(
                options['revoke'],
                options['reason']
            )
            return

        # Status
        if options['status']:
            self._show_status(options['status'])
            return

        # Auto-approve with intent
        if options['auto_approve_with_intent']:
            self._auto_approve_with_intent(dry_run=options['dry_run'])
            return

        # Default: show summary
        self._show_summary()

    def _list_pending(self):
        from core.models_document_registry import Initiative

        # Find initiatives that require boardroom approval but don't have it
        pending = Initiative.objects.filter(
            requires_boardroom_approval=True,
            boardroom_approved=False,
            current_stage__lte=5
        ).order_by('-impact_score')

        self.stdout.write(f"\n📋 Initiatives Pending Boardroom Approval ({pending.count()}):\n")

        if not pending.exists():
            self.stdout.write("   No initiatives pending approval.")
            return

        for i, init in enumerate(pending[:20], 1):
            track = init.execution_track or 'unknown'
            stage = init.current_stage
            intent = '✅' if init.founder_intent_set else '❌'

            self.stdout.write(
                f"   {i}. [{track.upper()}] {init.name[:45]}..."
            )
            self.stdout.write(
                f"      Stage {stage}/5 | Intent: {intent} | Priority: {init.impact_score:.2f}"
            )
            self.stdout.write(f"      ID: {init.id}")
            self.stdout.write("")

        if pending.count() > 20:
            self.stdout.write(f"   ... and {pending.count() - 20} more")

    def _approve_initiative(self, initiative_id, approved_by, notes):
        from core.models_document_registry import Initiative

        try:
            init = Initiative.objects.get(id=initiative_id)
        except Initiative.DoesNotExist:
            self.stdout.write(self.style.ERROR("\n❌ Initiative not found"))
            return

        if init.boardroom_approved:
            self.stdout.write(self.style.WARNING(
                f"\n⚠️ Initiative already approved by {init.boardroom_approved_by}"
            ))
            return

        init.approve_in_boardroom(approved_by=approved_by, notes=notes)

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Boardroom approval granted!"
        ))
        self.stdout.write(f"   Initiative: {init.name[:50]}")
        self.stdout.write(f"   Approved by: {approved_by}")
        if notes:
            self.stdout.write(f"   Notes: {notes}")
        self.stdout.write(f"   Can auto-progress: {init.can_auto_progress}")

    def _revoke_approval(self, initiative_id, reason):
        from core.models_document_registry import Initiative

        try:
            init = Initiative.objects.get(id=initiative_id)
        except Initiative.DoesNotExist:
            self.stdout.write(self.style.ERROR("\n❌ Initiative not found"))
            return

        if not init.boardroom_approved:
            self.stdout.write(self.style.WARNING(
                "\n⚠️ Initiative was not approved"
            ))
            return

        init.revoke_boardroom_approval(reason=reason)

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Boardroom approval revoked!"
        ))
        self.stdout.write(f"   Initiative: {init.name[:50]}")
        if reason:
            self.stdout.write(f"   Reason: {reason}")

    def _show_status(self, initiative_id):
        from core.models_document_registry import Initiative

        try:
            init = Initiative.objects.get(id=initiative_id)
        except Initiative.DoesNotExist:
            self.stdout.write(self.style.ERROR("\n❌ Initiative not found"))
            return

        self.stdout.write(f"\n📊 Boardroom Approval Status:")
        self.stdout.write(f"   Initiative: {init.name[:50]}")
        self.stdout.write(f"   Execution Track: {init.execution_track}")
        self.stdout.write(f"   Current Stage: {init.current_stage}/5")
        self.stdout.write("")
        self.stdout.write(f"   Requires Approval: {'Yes' if init.requires_boardroom_approval else 'No'}")

        if init.boardroom_approved:
            self.stdout.write(self.style.SUCCESS(f"   Status: APPROVED"))
            self.stdout.write(f"   Approved By: {init.boardroom_approved_by}")
            self.stdout.write(f"   Approved At: {init.boardroom_approved_at}")
            if init.boardroom_approval_notes:
                self.stdout.write(f"   Notes: {init.boardroom_approval_notes}")
        elif init.requires_boardroom_approval:
            self.stdout.write(self.style.WARNING(f"   Status: PENDING"))
        else:
            self.stdout.write(f"   Status: Not Required")

        self.stdout.write("")
        self.stdout.write(f"   Founder Intent Set: {'Yes' if init.founder_intent_set else 'No'}")
        self.stdout.write(f"   Can Auto-Progress: {'Yes' if init.can_auto_progress else 'No'}")

        if init.progression_blocked_reason:
            self.stdout.write(self.style.WARNING(
                f"   Blocked Reason: {init.progression_blocked_reason}"
            ))

    def _auto_approve_with_intent(self, dry_run=False):
        from core.models_document_registry import Initiative

        # Find initiatives that:
        # - Require boardroom approval
        # - Are not yet approved
        # - Have founder intent set (manual oversight has occurred)
        candidates = Initiative.objects.filter(
            requires_boardroom_approval=True,
            boardroom_approved=False,
            founder_intent_set=True,
            current_stage__lte=5
        )

        count = candidates.count()
        self.stdout.write(f"\n🤖 Auto-Approve with Founder Intent:")
        self.stdout.write(f"   Found {count} candidates")

        if count == 0:
            self.stdout.write("   No initiatives to approve.")
            return

        if dry_run:
            self.stdout.write(self.style.WARNING("\n   [DRY RUN - No changes will be made]"))
            for init in candidates[:10]:
                self.stdout.write(f"   Would approve: {init.name[:50]}")
            if count > 10:
                self.stdout.write(f"   ... and {count - 10} more")
            return

        approved = 0
        for init in candidates:
            try:
                init.approve_in_boardroom(
                    approved_by='auto-boardroom',
                    notes='Auto-approved: Founder intent was set, indicating manual review occurred'
                )
                approved += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"   ❌ Failed to approve {init.id}: {e}"
                ))

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Auto-approved {approved} initiatives"
        ))

    def _show_summary(self):
        from core.models_document_registry import Initiative

        total = Initiative.objects.filter(current_stage__lte=5).count()

        requires_approval = Initiative.objects.filter(
            requires_boardroom_approval=True,
            current_stage__lte=5
        ).count()

        approved = Initiative.objects.filter(
            requires_boardroom_approval=True,
            boardroom_approved=True,
            current_stage__lte=5
        ).count()

        pending = Initiative.objects.filter(
            requires_boardroom_approval=True,
            boardroom_approved=False,
            current_stage__lte=5
        ).count()

        # Ready to approve (have founder intent)
        ready = Initiative.objects.filter(
            requires_boardroom_approval=True,
            boardroom_approved=False,
            founder_intent_set=True,
            current_stage__lte=5
        ).count()

        self.stdout.write(f"\n📊 Boardroom Approval Summary:")
        self.stdout.write(f"   Total Active Initiatives: {total}")
        self.stdout.write(f"   Require Boardroom Approval: {requires_approval}")
        self.stdout.write(f"   Approved: {approved}")
        self.stdout.write(f"   Pending Approval: {pending}")
        self.stdout.write(f"   Ready to Approve (w/ intent): {ready}")

        if pending > 0:
            self.stdout.write(self.style.WARNING(
                f"\n   💡 Run --list-pending to see pending initiatives"
            ))
            if ready > 0:
                self.stdout.write(self.style.HTTP_INFO(
                    f"   💡 Run --auto-approve-with-intent to bulk approve {ready} initiatives"
                ))
