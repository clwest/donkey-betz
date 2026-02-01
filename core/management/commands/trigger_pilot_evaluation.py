"""
Session 897: Manually trigger pilot evaluation task.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Trigger the pilot evaluation task to process eligible pilots'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sync',
            action='store_true',
            help='Run synchronously instead of async via Celery',
        )

    def handle(self, *args, **options):
        from core.tasks import evaluate_and_complete_pilots

        if options['sync']:
            self.stdout.write("Running pilot evaluation synchronously...")
            result = evaluate_and_complete_pilots()
            self.stdout.write(self.style.SUCCESS(f"\nResult: {result}"))
        else:
            result = evaluate_and_complete_pilots.delay()
            self.stdout.write(self.style.SUCCESS(
                f"Triggered pilot evaluation task: {result.id}\n"
                "Check Celery logs for progress."
            ))
