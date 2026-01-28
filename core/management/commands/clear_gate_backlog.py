"""
Session 855: Clear gate backlog management command.

Gates stuck in 'not_started' create bottlenecks in the decision pipeline.
This command provides options for clearing gate backlogs:

1. Auto-waive low-risk gates (safe, default)
2. Auto-waive medium-risk stale gates (after --stale-hours threshold)
3. Move high-risk gates to 'blocked' for human review

Usage:
    # See current backlog status
    python manage.py clear_gate_backlog --status

    # Preview what would be cleared (dry run)
    python manage.py clear_gate_backlog --dry-run

    # Clear with default settings (only low-risk)
    python manage.py clear_gate_backlog

    # Clear including stale medium-risk gates (>72h)
    python manage.py clear_gate_backlog --include-stale-medium --stale-hours 72

    # Clear all low-risk and flag high-risk for review
    python manage.py clear_gate_backlog --flag-high-risk
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count


class Command(BaseCommand):
    help = 'Clear gate backlog to prevent decision pipeline bottlenecks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--status',
            action='store_true',
            help='Just show current backlog status without clearing',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleared without making changes',
        )
        parser.add_argument(
            '--include-stale-medium',
            action='store_true',
            help='Also auto-waive stale medium-risk gates',
        )
        parser.add_argument(
            '--stale-hours',
            type=int,
            default=72,
            help='Hours after which a gate is considered stale (default: 72)',
        )
        parser.add_argument(
            '--flag-high-risk',
            action='store_true',
            help='Move high-risk gates to blocked status for human review',
        )
        parser.add_argument(
            '--max-process',
            type=int,
            default=100,
            help='Maximum gates to process (default: 100)',
        )

    def handle(self, *args, **options):
        from core.models_pilot_readiness import PilotReadinessGate

        now = timezone.now()

        # Get backlog stats
        pending_gates = PilotReadinessGate.objects.filter(status='not_started')
        total_pending = pending_gates.count()

        if total_pending == 0:
            self.stdout.write(self.style.SUCCESS('No pending gates in backlog'))
            return

        # Get oldest pending
        oldest = pending_gates.order_by('created_at').first()
        oldest_age_hours = (now - oldest.created_at).total_seconds() / 3600 if oldest else 0

        # Count by risk level
        risk_counts = pending_gates.values('risk_level').annotate(count=Count('id'))
        risk_by_level = {r['risk_level']: r['count'] for r in risk_counts}

        # Show status
        self.stdout.write('\n=== Gate Backlog Status ===')
        self.stdout.write(f'Total pending (not_started): {total_pending}')
        self.stdout.write(f'Oldest pending: {oldest_age_hours:.1f} hours')
        self.stdout.write(f'\nBy risk level:')
        for level in ['low', 'medium', 'high', 'critical']:
            count = risk_by_level.get(level, 0)
            self.stdout.write(f'  {level}: {count}')

        # Count stale gates
        stale_threshold = now - timedelta(hours=options['stale_hours'])
        stale_medium = pending_gates.filter(
            risk_level='medium',
            created_at__lt=stale_threshold
        ).count()
        self.stdout.write(f'\nStale medium-risk (>{options["stale_hours"]}h): {stale_medium}')

        if options['status']:
            return

        # Triage parameters
        dry_run = options['dry_run']
        include_stale_medium = options['include_stale_medium']
        flag_high_risk = options['flag_high_risk']
        max_process = options['max_process']

        self.stdout.write(f'\n=== Triage Settings ===')
        self.stdout.write(f'Include stale medium-risk: {include_stale_medium}')
        self.stdout.write(f'Stale threshold: {options["stale_hours"]} hours')
        self.stdout.write(f'Flag high-risk for review: {flag_high_risk}')
        self.stdout.write(f'Max to process: {max_process}')
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - no changes will be made'))

        # Categorize gates
        results = {
            'waived_low': [],
            'waived_stale_medium': [],
            'flagged_high': [],
            'skipped': [],
        }

        # Process low-risk gates first
        low_risk_gates = pending_gates.filter(
            risk_level='low'
        ).select_related('decision')[:max_process]

        for gate in low_risk_gates:
            decision_topic = gate.decision.topic[:50] if gate.decision else 'Unknown'
            age_hours = (now - gate.created_at).total_seconds() / 3600

            # Skip initiative-linked gates
            if gate.initiative is not None:
                results['skipped'].append({
                    'id': str(gate.id)[:8],
                    'topic': decision_topic,
                    'reason': 'Linked to initiative',
                    'risk_level': gate.risk_level,
                })
                continue

            results['waived_low'].append({
                'id': str(gate.id)[:8],
                'topic': decision_topic,
                'age_hours': round(age_hours, 1),
                'risk_level': gate.risk_level,
            })

        # Process stale medium-risk gates if enabled
        if include_stale_medium:
            remaining = max_process - len(results['waived_low'])
            if remaining > 0:
                stale_medium_gates = pending_gates.filter(
                    risk_level='medium',
                    created_at__lt=stale_threshold
                ).select_related('decision')[:remaining]

                for gate in stale_medium_gates:
                    decision_topic = gate.decision.topic[:50] if gate.decision else 'Unknown'
                    age_hours = (now - gate.created_at).total_seconds() / 3600

                    # Skip initiative-linked gates
                    if gate.initiative is not None:
                        results['skipped'].append({
                            'id': str(gate.id)[:8],
                            'topic': decision_topic,
                            'reason': 'Linked to initiative',
                            'risk_level': gate.risk_level,
                        })
                        continue

                    results['waived_stale_medium'].append({
                        'id': str(gate.id)[:8],
                        'topic': decision_topic,
                        'age_hours': round(age_hours, 1),
                        'risk_level': gate.risk_level,
                    })

        # Flag high-risk gates if enabled
        if flag_high_risk:
            remaining = max_process - len(results['waived_low']) - len(results['waived_stale_medium'])
            if remaining > 0:
                high_risk_gates = pending_gates.filter(
                    risk_level__in=['high', 'critical']
                ).select_related('decision')[:remaining]

                for gate in high_risk_gates:
                    decision_topic = gate.decision.topic[:50] if gate.decision else 'Unknown'
                    age_hours = (now - gate.created_at).total_seconds() / 3600

                    results['flagged_high'].append({
                        'id': str(gate.id)[:8],
                        'topic': decision_topic,
                        'age_hours': round(age_hours, 1),
                        'risk_level': gate.risk_level,
                    })

        # Show what will happen
        self.stdout.write(f'\n=== Triage Plan ===')
        self.stdout.write(f'Waiving low-risk: {len(results["waived_low"])}')
        for g in results['waived_low'][:5]:
            self.stdout.write(f'  + [{g["risk_level"]}] {g["topic"]} ({g["age_hours"]}h)')
        if len(results['waived_low']) > 5:
            self.stdout.write(f'  ... and {len(results["waived_low"]) - 5} more')

        self.stdout.write(f'\nWaiving stale medium-risk: {len(results["waived_stale_medium"])}')
        for g in results['waived_stale_medium'][:5]:
            self.stdout.write(f'  + [{g["risk_level"]}] {g["topic"]} ({g["age_hours"]}h)')
        if len(results['waived_stale_medium']) > 5:
            self.stdout.write(f'  ... and {len(results["waived_stale_medium"]) - 5} more')

        self.stdout.write(f'\nFlagging high-risk for review: {len(results["flagged_high"])}')
        for g in results['flagged_high'][:5]:
            self.stdout.write(f'  ! [{g["risk_level"]}] {g["topic"]} ({g["age_hours"]}h)')
        if len(results['flagged_high']) > 5:
            self.stdout.write(f'  ... and {len(results["flagged_high"]) - 5} more')

        self.stdout.write(f'\nSkipped (initiative-linked): {len(results["skipped"])}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDry run complete - no changes made'))
            return

        # Execute triage
        self.stdout.write(f'\n=== Executing Triage ===')

        # Waive low-risk gates
        if results['waived_low']:
            # Direct bulk update for efficiency (avoids ID issues)
            # Use correct field names: approved_by, approval_notes, gate_approved_at
            updated = PilotReadinessGate.objects.filter(
                status='not_started',
                risk_level='low',
                initiative__isnull=True
            ).update(
                status='waived',
                gate_approved_at=now,
                approved_by='clear_gate_backlog_command',
                approval_notes='Auto-waived: low-risk gate cleared by Session 855 backlog triage'
            )
            self.stdout.write(self.style.SUCCESS(f'Waived {updated} low-risk gates'))

        # Waive stale medium-risk gates
        stale_medium_updated = 0
        if results['waived_stale_medium']:
            stale_medium_updated = PilotReadinessGate.objects.filter(
                status='not_started',
                risk_level='medium',
                created_at__lt=stale_threshold,
                initiative__isnull=True
            ).update(
                status='waived',
                gate_approved_at=now,
                approved_by='clear_gate_backlog_command',
                approval_notes=f'Auto-waived: stale medium-risk gate (>{options["stale_hours"]}h) cleared by Session 855 backlog triage'
            )
            self.stdout.write(self.style.SUCCESS(
                f'Waived {stale_medium_updated} stale medium-risk gates'
            ))

        # Flag high-risk gates
        high_flagged = 0
        if results['flagged_high']:
            high_flagged = PilotReadinessGate.objects.filter(
                status='not_started',
                risk_level__in=['high', 'critical']
            ).update(
                status='blocked',
                approval_notes='BLOCKED: Flagged for human review by Session 855 backlog triage'
            )
            self.stdout.write(self.style.SUCCESS(
                f'Flagged {high_flagged} high-risk gates for review'
            ))

        total_processed = (
            len(results['waived_low']) +
            len(results['waived_stale_medium']) +
            len(results['flagged_high'])
        )
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Total processed: {total_processed}'))
        remaining = total_pending - total_processed
        self.stdout.write(f'Remaining in backlog: {remaining}')
