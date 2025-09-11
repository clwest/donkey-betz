"""
Management command to clean mythology from embeddings and create guards.
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone
from datetime import datetime
import time

from mythology.models import (
    MythologyCleanup, MythPattern, MythologyGuard,
    MythologyEvent, MythologyAlert
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
        """Clean mythologies from embeddings."""
        self.stdout.write(self.style.SUCCESS('\n🔍 Scanning embeddings for mythologies...'))
        
        with connection.cursor() as cursor:
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM unified_embeddings")
            total_count = cursor.fetchone()[0]
            self.stdout.write(f'  Total embeddings: {total_count}')
            
            # Specific mythology queries
            mythologies_to_clean = [
                {
                    'name': 'Dart/Flutter',
                    'query': "SELECT id FROM unified_embeddings WHERE content_text ILIKE '%dart%' OR content_text ILIKE '%flutter%'",
                    'field': 'dart_flutter_removed'
                },
                {
                    'name': 'Fitness Dashboard',
                    'query': "SELECT id FROM unified_embeddings WHERE content_text ILIKE '%fitness%dashboard%'",
                    'field': 'fitness_dashboard_removed'
                },
                {
                    'name': '350 Deployments',
                    'query': "SELECT id FROM unified_embeddings WHERE content_text LIKE '%350%' AND content_text ILIKE '%deployment%'",
                    'field': 'deployments_350_removed'
                },
                {
                    'name': 'Capability Exaggerations',
                    'query': "SELECT id FROM unified_embeddings WHERE content_text ILIKE '%unlimited%' OR content_text ILIKE '%infinite%' OR content_text ILIKE '%perfect%'",
                    'field': 'capability_exaggerations_removed'
                }
            ]
            
            cleanup.items_scanned = total_count
            total_cleaned = 0
            
            for myth_config in mythologies_to_clean:
                self.stdout.write(f'\n  Checking for {myth_config["name"]}...')
                
                # Get IDs to delete
                cursor.execute(myth_config['query'])
                ids_to_delete = [row[0] for row in cursor.fetchall()]
                count = len(ids_to_delete)
                
                if count > 0:
                    self.stdout.write(self.style.WARNING(f'    ⚠️ Found {count} embeddings with {myth_config["name"]}'))
                    
                    if not self.dry_run:
                        # Delete in batches
                        batch_size = 100
                        for i in range(0, len(ids_to_delete), batch_size):
                            batch = ids_to_delete[i:i+batch_size]
                            placeholders = ','.join(['%s'] * len(batch))
                            cursor.execute(
                                f"DELETE FROM unified_embeddings WHERE id IN ({placeholders})",
                                batch
                            )
                        
                        self.stdout.write(self.style.SUCCESS(f'    ✓ Deleted {count} embeddings'))
                    else:
                        self.stdout.write(self.style.WARNING(f'    [DRY RUN] Would delete {count} embeddings'))
                    
                    # Update cleanup record
                    setattr(cleanup, myth_config['field'], count)
                    total_cleaned += count
                else:
                    self.stdout.write(f'    ✓ No {myth_config["name"]} found')
            
            cleanup.items_cleaned = total_cleaned
            cleanup.save()
            
            # Create alert if significant mythologies found
            if total_cleaned > 100:
                MythologyAlert.objects.create(
                    alert_type='cleanup_needed',
                    severity='high' if total_cleaned > 500 else 'medium',
                    title=f'Mythology cleanup performed: {total_cleaned} items',
                    description=f'Cleaned {total_cleaned} mythology-contaminated embeddings from the system',
                    data={
                        'cleanup_id': str(cleanup.id),
                        'items_cleaned': total_cleaned,
                        'dry_run': self.dry_run
                    }
                )
    
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