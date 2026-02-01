"""
Session 897: Test initiatives API performance after optimization.
"""
from django.core.management.base import BaseCommand
import time


class Command(BaseCommand):
    help = 'Test initiatives API query performance'

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative, InitiativeStage
        from django.db.models import Prefetch

        self.stdout.write("\n=== Initiatives API Performance Test ===\n")

        # Test 1: Without prefetch (old way)
        start = time.time()
        initiatives = Initiative.objects.all().order_by('-updated_at')[:50]
        for init in initiatives:
            _ = list(init.stages.all())  # Force query
            _ = list(init.source_decisions.all())  # Force query
        old_time = time.time() - start
        self.stdout.write(f"Without prefetch: {old_time:.2f}s")

        # Test 2: With prefetch (new way)
        start = time.time()
        initiatives = Initiative.objects.all().order_by('-updated_at').prefetch_related(
            Prefetch('stages', queryset=InitiativeStage.objects.all()),
            Prefetch('source_decisions'),
        )[:50]
        for init in initiatives:
            _ = list(init.stages.all())  # Uses prefetched data
            _ = list(init.source_decisions.all())  # Uses prefetched data
        new_time = time.time() - start
        self.stdout.write(f"With prefetch: {new_time:.2f}s")

        speedup = old_time / new_time if new_time > 0 else float('inf')
        self.stdout.write(self.style.SUCCESS(f"\nSpeedup: {speedup:.1f}x faster"))
