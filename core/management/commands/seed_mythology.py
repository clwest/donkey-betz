"""
Seed Mythology Command - Session 819: Mythology System Fix

Seeds MythPattern and MythologyGuard tables with initial data
for the hallucination detection and prevention system.

Usage:
    python manage.py seed_mythology
    python manage.py seed_mythology --dry-run
    python manage.py seed_mythology --patterns-only
    python manage.py seed_mythology --guards-only
"""

import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Seed MythPattern and MythologyGuard tables for mythology detection'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be created without making changes',
        )
        parser.add_argument(
            '--patterns-only',
            action='store_true',
            help='Only seed MythPattern records',
        )
        parser.add_argument(
            '--guards-only',
            action='store_true',
            help='Only seed MythologyGuard records',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        patterns_only = options['patterns_only']
        guards_only = options['guards_only']

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - no changes will be made"))

        if not guards_only:
            self._seed_patterns(dry_run)

        if not patterns_only:
            self._seed_guards(dry_run)

        self.stdout.write(self.style.SUCCESS("Mythology seeding complete!"))

    def _seed_patterns(self, dry_run):
        """Seed MythPattern records."""
        from mythology.models import MythPattern

        self.stdout.write("\n=== Seeding MythPattern ===")

        patterns = [
            {
                'pattern_type': 'numeric_inflation',
                'description': 'Inflating numbers beyond reasonable bounds (e.g., "1000x improvement", "millions of users")',
                'regex_pattern': r'\b(\d{3,})\s*(x|times|percent|%)\b|\b(millions?|billions?|thousands?)\s+of\b',
                'detection_keywords': ['1000x', 'million', 'billion', 'exponential', 'unlimited'],
            },
            {
                'pattern_type': 'false_authority',
                'description': 'Claiming authority or citations that don\'t exist',
                'regex_pattern': r'(studies show|research proves|experts confirm|according to)',
                'detection_keywords': ['studies show', 'research proves', 'experts say', 'scientifically proven'],
            },
            {
                'pattern_type': 'capability_exaggeration',
                'description': 'Overstating system capabilities beyond what is implemented',
                'regex_pattern': r'(can do anything|fully automated|complete solution|100% accurate)',
                'detection_keywords': ['can do anything', 'fully automated', 'perfect', '100% accurate', 'never fails'],
            },
            {
                'pattern_type': 'temporal_confusion',
                'description': 'Mixing up past/present/future or claiming things that haven\'t happened',
                'regex_pattern': r'(has been deployed|is now live|already implemented)',
                'detection_keywords': ['already done', 'has been', 'is now', 'was completed'],
            },
            {
                'pattern_type': 'context_loss',
                'description': 'Losing track of what was actually discussed or decided',
                'regex_pattern': r'(as we discussed|you mentioned|we agreed)',
                'detection_keywords': ['as discussed', 'you said', 'we decided', 'previously'],
            },
            {
                'pattern_type': 'semantic_drift',
                'description': 'Gradually changing the meaning of terms during conversation',
                'regex_pattern': '',
                'detection_keywords': ['actually means', 'in other words', 'basically'],
            },
            {
                'pattern_type': 'confidence_decay',
                'description': 'Decreasing confidence in statements without basis',
                'regex_pattern': r'(might|maybe|possibly|could be)',
                'detection_keywords': ['might', 'maybe', 'possibly', 'I think', 'probably'],
            },
            {
                'pattern_type': 'false_action_claims',
                'description': 'Claiming to have taken actions that weren\'t actually performed',
                'regex_pattern': r'(I have (created|deployed|fixed|updated|sent))',
                'detection_keywords': ['I created', 'I deployed', 'I fixed', 'I sent', 'done'],
            },
            {
                'pattern_type': 'unverified_stats',
                'description': 'Citing statistics or metrics without verification',
                'regex_pattern': r'\b\d+(\.\d+)?%|\b\d+/\d+\b',
                'detection_keywords': ['percent', 'ratio', 'rate', 'average', 'median'],
            },
            {
                'pattern_type': 'false_technology',
                'description': 'Claiming technology capabilities that don\'t exist',
                'regex_pattern': r'(quantum|AGI|singularity|conscious AI)',
                'detection_keywords': ['quantum', 'AGI', 'singularity', 'sentient', 'conscious'],
            },
        ]

        created = 0
        for p in patterns:
            if dry_run:
                self.stdout.write(f"  [DRY RUN] Would create: {p['pattern_type']}")
                created += 1
            else:
                obj, was_created = MythPattern.objects.get_or_create(
                    pattern_type=p['pattern_type'],
                    defaults={
                        'description': p['description'],
                        'regex_pattern': p['regex_pattern'],
                        'detection_keywords': p['detection_keywords'],
                    }
                )
                if was_created:
                    created += 1
                    self.stdout.write(f"  ✅ Created: {p['pattern_type']}")
                else:
                    self.stdout.write(f"  ⏭️  Exists: {p['pattern_type']}")

        self.stdout.write(f"\nPatterns: {created} created, {MythPattern.objects.count()} total")

    def _seed_guards(self, dry_run):
        """Seed MythologyGuard records."""
        from mythology.models import MythologyGuard

        self.stdout.write("\n=== Seeding MythologyGuard ===")

        guards = [
            {
                'name': 'Numeric Inflation Detector',
                'description': 'Detects and prevents inflated numbers like "1000x", "millions of users"',
                'guard_type': 'pattern',
                'pattern': r'\b(\d{3,})\s*(x|times|percent|%)\b|\b(millions?|billions?)\s+of\b',
                'priority': 100,
            },
            {
                'name': 'False Authority Filter',
                'description': 'Blocks unverified claims of authority like "studies show", "experts confirm"',
                'guard_type': 'filter',
                'pattern': r'(studies show|research proves|experts confirm|scientists say)',
                'priority': 90,
            },
            {
                'name': 'Anti-Hallucination Instruction',
                'description': 'Injects instructions to prevent AI from making things up',
                'guard_type': 'instruction',
                'instruction': 'Never claim to have done something you haven\'t. Never invent statistics. Never cite sources that don\'t exist. If unsure, say so.',
                'priority': 100,
            },
            {
                'name': 'Capability Claim Validator',
                'description': 'Validates claims about system capabilities against actual implementation',
                'guard_type': 'validation',
                'validation_rules': {
                    'check_deployment_claims': True,
                    'verify_feature_existence': True,
                    'flag_superlatives': ['always', 'never', 'perfect', '100%'],
                },
                'priority': 80,
            },
            {
                'name': 'False Action Detector',
                'description': 'Detects claims of having taken actions that weren\'t performed',
                'guard_type': 'pattern',
                'pattern': r'I have (created|deployed|fixed|updated|sent|completed)',
                'priority': 95,
            },
            {
                'name': 'Grounding Instruction',
                'description': 'Injects instructions to keep AI grounded in facts',
                'guard_type': 'instruction',
                'instruction': 'Base all claims on verifiable data. Reference specific files, commits, or database records when making claims about the system.',
                'priority': 85,
            },
            {
                'name': 'Temporal Consistency Validator',
                'description': 'Validates temporal claims (past/present/future) are accurate',
                'guard_type': 'validation',
                'validation_rules': {
                    'check_tense_consistency': True,
                    'verify_completion_claims': True,
                },
                'priority': 75,
            },
            {
                'name': 'Statistics Verifier',
                'description': 'Flags unverified statistics and percentages for review',
                'guard_type': 'filter',
                'pattern': r'\b\d+(\.\d+)?%\b|\b\d+\s*/\s*\d+\b',
                'priority': 70,
            },
        ]

        created = 0
        for g in guards:
            if dry_run:
                self.stdout.write(f"  [DRY RUN] Would create: {g['name']}")
                created += 1
            else:
                obj, was_created = MythologyGuard.objects.get_or_create(
                    name=g['name'],
                    defaults={
                        'description': g['description'],
                        'guard_type': g['guard_type'],
                        'pattern': g.get('pattern', ''),
                        'instruction': g.get('instruction', ''),
                        'validation_rules': g.get('validation_rules', {}),
                        'priority': g['priority'],
                        'is_active': True,
                    }
                )
                if was_created:
                    created += 1
                    self.stdout.write(f"  ✅ Created: {g['name']}")
                else:
                    self.stdout.write(f"  ⏭️  Exists: {g['name']}")

        self.stdout.write(f"\nGuards: {created} created, {MythologyGuard.objects.count()} total")
