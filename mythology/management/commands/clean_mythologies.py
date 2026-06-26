"""
Management command to clean mythology from embeddings and create guards.

Session 1236 P5#3 audit Tranche 2 PR #1: `clean_embeddings()` was
retired to a no-op. Pre-pivot it queried the non-existent
`unified_embeddings` table for known hallucination patterns
(Dart/Flutter, Fitness Dashboard, "350 deployments", capability
exaggerations) via `connection.cursor()` raw SQL, then bulk-deleted
the matched rows. Every invocation silently caught the
"relation does not exist" exception and reported zero items cleaned
while still logging a "✅ Cleanup completed" success line.

The retirement preserves `setup_guards()`, `setup_patterns()`, and
`generate_summary()` which DO use real Django models (`MythPattern`,
`MythologyGuard`, `MythologyCleanup`, `MythologyAlert`). The
`--setup-guards` flag work continues to function. The cleanup step is
now a no-op that records zero counts.

Why retire not pivot: hallucination prevention now happens at WRITE
time via `core/conversation_memory.py:HALLUCINATION_INDICATORS`
(Session 1235 PR #2637 preserved the filter on the canonical
ConversationMemory write path). The post-hoc cleanup step is
redundant with prevention-at-write. If a future writer puts free-form
user content into `UserEmbedding` without an analogous filter, this
mgmt cmd can be repivoted with a proper target model at that time.

Zero callers outside this file at retirement time (verified via grep
across non-archive, non-cache codebase).
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
import time

from mythology.models import (
    MythologyCleanup, MythPattern, MythologyGuard,
    MythologyAlert
)
from mythology.services import MythologyDetectionService


class Command(BaseCommand):
    help = 'Clean mythologies from embeddings and set up prevention guards'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without actually deleting embeddings',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of embeddings to scan',
        )
        parser.add_argument(
            '--setup-guards',
            action='store_true',
            help='Set up mythology prevention guards',
        )
    
    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.limit = options['limit']
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('🧹 MYTHOLOGY CLEANUP SYSTEM'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be made\n'))
        
        # Initialize cleanup record
        cleanup = MythologyCleanup.objects.create(
            cleanup_type='embedding',
            notes='Automated mythology cleanup' + (' (dry run)' if self.dry_run else '')
        )
        
        start_time = time.time()
        
        try:
            # Step 1: Set up guards if requested
            if options['setup_guards']:
                self.setup_guards()
            
            # Step 2: Set up patterns
            self.setup_patterns()
            
            # Step 3: Clean embeddings
            self.clean_embeddings(cleanup)
            
            # Step 4: Generate summary
            self.generate_summary(cleanup)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error during cleanup: {e}'))
            cleanup.notes += f'\nError: {e}'
        
        finally:
            # Update cleanup record
            cleanup.completed_at = timezone.now()
            cleanup.duration_seconds = time.time() - start_time
            cleanup.save()
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Cleanup completed in {cleanup.duration_seconds:.2f} seconds'))
    
    def setup_guards(self):
        """Set up mythology prevention guards."""
        self.stdout.write(self.style.SUCCESS('\n📛 Setting up mythology guards...'))
        
        guards = [
            {
                'name': 'anti_mythology_instruction',
                'description': 'Inject anti-mythology instructions',
                'guard_type': 'instruction',
                'instruction': MythologyDetectionService.ANTI_MYTHOLOGY_INSTRUCTION,
                'priority': 100
            },
            {
                'name': 'detect_dart_flutter',
                'description': 'Detect and prevent Dart/Flutter references',
                'guard_type': 'pattern',
                'pattern': r'(dart|flutter|swift|kotlin)',
                'priority': 90
            },
            {
                'name': 'detect_fitness_dashboard',
                'description': 'Detect fitness dashboard false claims',
                'guard_type': 'pattern',
                'pattern': r'fitness\s*dashboard',
                'priority': 90
            },
            {
                'name': 'detect_350_deployments',
                'description': 'Detect the 350 deployments myth',
                'guard_type': 'pattern',
                'pattern': r'350\s*deployments?',
                'priority': 95
            },
            {
                'name': 'detect_capability_exaggeration',
                'description': 'Detect capability exaggerations',
                'guard_type': 'pattern',
                'pattern': r'(unlimited|infinite|perfect|can do anything)',
                'priority': 85
            }
        ]
        
        for guard_data in guards:
            guard, created = MythologyGuard.objects.get_or_create(
                name=guard_data['name'],
                defaults=guard_data
            )
            if created:
                self.stdout.write(f'  ✓ Created guard: {guard.name}')
            else:
                self.stdout.write(f'  • Guard exists: {guard.name}')
    
    def setup_patterns(self):
        """Set up mythology patterns."""
        self.stdout.write(self.style.SUCCESS('\n🎯 Setting up mythology patterns...'))
        
        detection_service = MythologyDetectionService()
        
        for pattern_type, regex in detection_service.MYTHOLOGY_PATTERNS.items():
            pattern, created = MythPattern.objects.get_or_create(
                pattern_type=pattern_type,
                defaults={
                    'description': f'Pattern for detecting {pattern_type}',
                    'regex_pattern': regex,
                    'severity_weight': detection_service._get_pattern_weight(pattern_type),
                    'prevention_strategies': ['instruction_injection', 'response_validation']
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created pattern: {pattern_type}')
            else:
                self.stdout.write(f'  • Pattern exists: {pattern_type}')
    
    def clean_embeddings(self, cleanup):
        """Retired no-op (Session 1236 P5#3 Tranche 2 PR #1).

        Pre-retirement: queried dead `unified_embeddings` table for
        known hallucination patterns and bulk-deleted matches. See
        module docstring for rationale.

        Post-retirement: records zero counts and prints a clear
        retirement notice. Hallucination prevention happens at WRITE
        time via the `HALLUCINATION_INDICATORS` filter in
        `core/conversation_memory.py`.
        """
        self.stdout.write(self.style.SUCCESS(
            '\n🔍 Scanning embeddings for mythologies...'
        ))
        self.stdout.write(
            '  [RETIRED] Post-Session 1236 PR #1 of Tranche 2: '
            'cleanup step no-op (no real backing model). '
            'Prevention happens at write-time via '
            'core/conversation_memory.HALLUCINATION_INDICATORS.'
        )

        cleanup.items_scanned = 0
        cleanup.items_cleaned = 0
        cleanup.dart_flutter_removed = 0
        cleanup.fitness_dashboard_removed = 0
        cleanup.deployments_350_removed = 0
        cleanup.capability_exaggerations_removed = 0
        cleanup.save()
    
    def generate_summary(self, cleanup):
        """Generate cleanup summary."""
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('📊 CLEANUP SUMMARY'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        self.stdout.write(f'\n  Items scanned: {cleanup.items_scanned}')
        self.stdout.write(f'  Items cleaned: {cleanup.items_cleaned}')
        
        if cleanup.dart_flutter_removed > 0:
            self.stdout.write(self.style.WARNING(f'  • Dart/Flutter removed: {cleanup.dart_flutter_removed}'))
        if cleanup.fitness_dashboard_removed > 0:
            self.stdout.write(self.style.WARNING(f'  • Fitness Dashboard removed: {cleanup.fitness_dashboard_removed}'))
        if cleanup.deployments_350_removed > 0:
            self.stdout.write(self.style.WARNING(f'  • 350 Deployments removed: {cleanup.deployments_350_removed}'))
        if cleanup.capability_exaggerations_removed > 0:
            self.stdout.write(self.style.WARNING(f'  • Capability Exaggerations removed: {cleanup.capability_exaggerations_removed}'))
        
        if cleanup.items_cleaned > 0:
            percentage = (cleanup.items_cleaned / cleanup.items_scanned) * 100
            self.stdout.write(self.style.WARNING(f'\n  Mythology contamination: {percentage:.2f}%'))
            
            if percentage > 30:
                self.stdout.write(self.style.ERROR('  ⚠️ HIGH CONTAMINATION - Immediate action required'))
            elif percentage > 10:
                self.stdout.write(self.style.WARNING('  ⚠️ MODERATE CONTAMINATION - Monitoring recommended'))
            else:
                self.stdout.write(self.style.SUCCESS('  ✓ LOW CONTAMINATION - System healthy'))
        else:
            self.stdout.write(self.style.SUCCESS('\n  ✓ No mythologies found - System clean!'))