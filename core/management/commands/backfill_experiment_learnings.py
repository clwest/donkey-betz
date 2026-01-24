"""
Session 805: Backfill ExperimentLearning records for experiments missing learnings.

Many experiments were halted or completed but never had learnings extracted.
This command creates learning records for those experiments.

Usage:
    python manage.py backfill_experiment_learnings
    python manage.py backfill_experiment_learnings --dry-run
    python manage.py backfill_experiment_learnings --halted-only
"""

import logging

from django.core.management.base import BaseCommand

from core.models_pilot_readiness import Experiment, ExperimentLearning

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Backfill ExperimentLearning records for experiments missing learnings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--halted-only',
            action='store_true',
            help='Only process halted experiments',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of experiments to process',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        halted_only = options['halted_only']
        limit = options['limit']

        self.stdout.write(self.style.NOTICE(
            f"[Session 805] Backfilling experiment learnings..."
        ))

        # Find experiments without learning records
        experiments_with_learnings = ExperimentLearning.objects.values_list(
            'experiment_id', flat=True
        )

        missing_qs = Experiment.objects.exclude(
            id__in=experiments_with_learnings
        ).filter(
            status__in=['success', 'failure', 'partial', 'inconclusive']
        )

        if halted_only:
            missing_qs = missing_qs.filter(is_halted=True)

        if limit:
            missing_qs = missing_qs[:limit]

        experiments = list(missing_qs)
        total = len(experiments)

        self.stdout.write(f"Found {total} experiments without learnings")

        created = 0
        failed = 0

        for i, experiment in enumerate(experiments, 1):
            try:
                if dry_run:
                    self.stdout.write(
                        f"  [{i}/{total}] Would create learning for: "
                        f"{experiment.name[:50]}... (status: {experiment.status})"
                    )
                    created += 1
                    continue

                # Build analysis based on experiment state
                decision = None
                decision_type = 'general'
                if experiment.pilot and experiment.pilot.gate:
                    decision = experiment.pilot.gate.decision
                    if decision:
                        decision_type = decision.decision_type or 'general'

                analysis = {
                    'decision_type': decision_type,
                }

                if experiment.is_halted:
                    # Halted experiments - capture halt reason
                    analysis['what_failed'] = f"Experiment halted: {experiment.halt_reason or 'Unknown reason'}"
                    analysis['key_insight'] = (
                        f"The {decision_type} experiment was halted. "
                        f"Reason: {experiment.halt_reason or 'Unknown'}. "
                        f"Review halt conditions for future experiments."
                    )
                    analysis['recommendation'] = (
                        "Do not proceed with current approach. "
                        "Address the halt condition before retrying."
                    )
                elif experiment.status == 'success':
                    analysis['what_worked'] = experiment.result_summary or "Achieved objectives"
                    analysis['key_insight'] = f"The {decision_type} approach proved effective."
                    analysis['recommendation'] = "Proceed with implementation."
                elif experiment.status == 'partial':
                    analysis['what_worked'] = "Partial objectives achieved"
                    analysis['what_failed'] = experiment.result_summary or "Some aspects need improvement"
                    analysis['key_insight'] = f"Mixed results for {decision_type} approach."
                    analysis['recommendation'] = "Iterate and refine before scaling."
                else:  # failure or inconclusive
                    analysis['what_failed'] = experiment.result_summary or "Did not meet success criteria"
                    analysis['key_insight'] = f"The {decision_type} approach needs revision."
                    analysis['recommendation'] = "Review approach before retrying."

                # Create learning record
                learning = ExperimentLearning.create_from_experiment(experiment, analysis)

                if learning:
                    # Update with our analysis
                    if analysis.get('what_worked'):
                        learning.what_worked = analysis['what_worked']
                    if analysis.get('what_failed'):
                        learning.what_failed = analysis['what_failed']
                    if analysis.get('key_insight'):
                        learning.key_insight = analysis['key_insight']
                    if analysis.get('recommendation'):
                        learning.future_recommendation = analysis['recommendation']
                    learning.save()

                    created += 1
                    self.stdout.write(
                        f"  [{i}/{total}] Created learning for: {experiment.name[:50]}..."
                    )
                else:
                    failed += 1
                    self.stdout.write(self.style.WARNING(
                        f"  [{i}/{total}] Failed to create learning for: {experiment.name[:50]}..."
                    ))

            except Exception as e:
                failed += 1
                self.stdout.write(self.style.ERROR(
                    f"  [{i}/{total}] Error processing {experiment.id}: {e}"
                ))

        # Summary
        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"\n[DRY RUN] Would create {created} learnings"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\n[Session 805] Created {created} learnings, {failed} failed"
            ))
