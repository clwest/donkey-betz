"""
Management command to populate sample mythology data for testing.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
from mythology.models import (
    FlaggedHallucination, HallucinationReview, MythologyAlert, 
    MythologyEvent, MythPattern
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate sample mythology data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate mythology data...'))
        
        # Get or create chris user
        user, created = User.objects.get_or_create(
            username='chris',
            defaults={
                'email': 'chris@donkeybetz.ai',
                'first_name': 'Chris',
                'last_name': 'Admin'
            }
        )
        if created:
            user.set_password('chris123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))
        
        # Create sample flagged content
        sample_content = [
            {
                'flagged_type': 'hallucination',
                'original_prompt': 'Tell me about the history of quantum computing',
                'flagged_content': 'Quantum computing was invented in 1850 by Charles Babbage when he discovered quantum entanglement...',
                'patterns_detected': ['temporal_confusion', 'factual_error'],
                'risk_score': 0.85,
                'priority': 'high',
                'verification_status': 'pending',
            },
            {
                'flagged_type': 'factual_error',
                'original_prompt': 'What is the capital of France?',
                'flagged_content': 'The capital of France is Berlin, which has been the seat of French government since 1789...',
                'patterns_detected': ['factual_error'],
                'risk_score': 0.95,
                'priority': 'critical',
                'verification_status': 'pending',
            },
            {
                'flagged_type': 'harmful_content',
                'original_prompt': 'How to make a simple cake?',
                'flagged_content': 'To make a cake, first obtain industrial chemicals...',
                'patterns_detected': ['harmful_content', 'inappropriate_instructions'],
                'risk_score': 0.92,
                'priority': 'critical',
                'verification_status': 'pending',
                'requires_immediate_attention': True,
            },
            {
                'flagged_type': 'inconsistent_knowledge',
                'original_prompt': 'Explain photosynthesis',
                'flagged_content': 'Photosynthesis is the process where plants absorb oxygen and release carbon dioxide...',
                'patterns_detected': ['inconsistent_knowledge'],
                'risk_score': 0.65,
                'priority': 'medium',
                'verification_status': 'resolved',
            },
            {
                'flagged_type': 'temporal_confusion',
                'original_prompt': 'Who is the current president?',
                'flagged_content': 'The current president in 2023 is George Washington, who has served for 250 years...',
                'patterns_detected': ['temporal_confusion', 'hallucination'],
                'risk_score': 0.78,
                'priority': 'high',
                'verification_status': 'pending',
            },
            {
                'flagged_type': 'hallucination',
                'original_prompt': 'What are the benefits of exercise?',
                'flagged_content': 'Exercise benefits include: improved health, better sleep, increased energy...',
                'patterns_detected': [],
                'risk_score': 0.15,
                'priority': 'low',
                'verification_status': 'resolved',
            },
            {
                'flagged_type': 'factual_error',
                'original_prompt': 'What is the speed of light?',
                'flagged_content': 'The speed of light is approximately 300 meters per second...',
                'patterns_detected': ['factual_error', 'unit_error'],
                'risk_score': 0.72,
                'priority': 'medium',
                'verification_status': 'reviewing',
            },
            {
                'flagged_type': 'hallucination',
                'original_prompt': 'Describe the water cycle',
                'flagged_content': 'The water cycle involves water evaporating, forming clouds, and returning as precipitation. This was discovered by Einstein in 1920...',
                'patterns_detected': ['factual_error', 'temporal_confusion'],
                'risk_score': 0.55,
                'priority': 'medium',
                'verification_status': 'resolved',
            },
            {
                'flagged_type': 'spam_content',
                'original_prompt': 'Tell me about AI',
                'flagged_content': 'BUY NOW! AMAZING AI PRODUCTS! CLICK HERE! LIMITED TIME OFFER!',
                'patterns_detected': ['spam_content'],
                'risk_score': 0.88,
                'priority': 'low',
                'verification_status': 'dismissed',
            },
            {
                'flagged_type': 'inappropriate_content',
                'original_prompt': 'How to cook pasta?',
                'flagged_content': '[Content flagged for inappropriate suggestions]',
                'patterns_detected': ['inappropriate_content'],
                'risk_score': 0.75,
                'priority': 'high',
                'verification_status': 'pending',
            },
        ]
        
        # Clear existing data
        FlaggedHallucination.objects.all().delete()
        MythologyEvent.objects.all().delete()
        MythologyAlert.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing mythology data'))
        
        # Create flagged content
        created_flags = []
        for i, content_data in enumerate(sample_content):
            # Add some variation to timestamps
            created_time = timezone.now() - timedelta(hours=random.randint(1, 72))
            
            flagged = FlaggedHallucination.objects.create(
                **content_data,
                confidence_score=random.uniform(0.6, 0.95),
                detection_method=random.choice(['automated', 'user_report', 'pattern_matching']),
                user=user if random.choice([True, False]) else None,
                flagged_at=created_time,
                auto_verification_attempted=random.choice([True, False]),
                metadata={
                    'source': 'test_data',
                    'index': i,
                    'sample': True
                }
            )
            created_flags.append(flagged)
            
            # If resolved, add review
            if content_data['verification_status'] in ['resolved', 'dismissed']:
                flagged.verified_by = user
                flagged.verified_at = created_time + timedelta(hours=random.randint(1, 12))
                flagged.reviewed_at = flagged.verified_at
                flagged.verification_notes = f"Reviewed and marked as {content_data['verification_status']}"
                flagged.save()
                
                # Create review record
                HallucinationReview.objects.create(
                    flagged_hallucination=flagged,
                    reviewer=user,
                    review_action='approved' if content_data['verification_status'] == 'resolved' else 'dismissed',
                    review_notes=f"Sample review for testing - {content_data['verification_status']}",
                    confidence_rating=random.randint(3, 5)
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(created_flags)} flagged content items'))
        
        # Create mythology events
        event_types = ['detection', 'prevention', 'alert', 'review']
        mutation_types = ['capability_exaggeration', 'knowledge_drift', 'fact_contamination']
        
        for i in range(15):
            event_time = timezone.now() - timedelta(hours=random.randint(0, 24))
            MythologyEvent.objects.create(
                event_type=random.choice(event_types),
                mutation_type=random.choice(mutation_types) if random.choice([True, False]) else '',
                patterns_detected=random.sample(['hallucination', 'factual_error', 'temporal_confusion'], k=random.randint(1, 2)),
                risk_level=random.uniform(0.3, 0.95),
                confidence_score=random.uniform(0.5, 0.95),
                was_prevented=random.choice([True, False]),
                prevention_method=random.choice(['pattern_block', 'content_filter', 'manual_review']) if random.choice([True, False]) else '',
                original_content=f"Sample event content #{i} - This is test data for the mythology system",
                created_at=event_time,
                metadata={
                    'test_event': True,
                    'index': i
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Created 15 mythology events'))
        
        # Create some alerts for high priority items
        high_priority_flags = [f for f in created_flags if f.priority in ['high', 'critical']]
        for flag in high_priority_flags[:3]:  # Create alerts for first 3 high priority items
            MythologyAlert.objects.create(
                alert_type='immediate_review',
                severity='high' if flag.priority == 'high' else 'critical',
                title=f'High priority {flag.flagged_type} detected',
                description=f'Content flagged with risk score {flag.risk_score:.2f}',
                data={
                    'flagged_id': str(flag.id),
                    'patterns': flag.patterns_detected
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {min(3, len(high_priority_flags))} mythology alerts'))
        
        # Create some myth patterns
        patterns = [
            ('temporal_confusion', 'Confusion about dates, times, or historical sequences'),
            ('factual_error', 'Incorrect factual information'),
            ('hallucination', 'Completely fabricated information'),
            ('capability_exaggeration', 'Exaggerating AI capabilities'),
            ('knowledge_drift', 'Gradual deviation from accurate knowledge'),
        ]
        
        for pattern_type, description in patterns:
            MythPattern.objects.get_or_create(
                pattern_type=pattern_type,
                defaults={
                    'description': description,
                    'frequency_count': random.randint(10, 100),
                    'last_seen': timezone.now(),
                    'is_active': True
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created/updated {len(patterns)} myth patterns'))
        
        self.stdout.write(self.style.SUCCESS('Successfully populated mythology test data!'))
        self.stdout.write(self.style.SUCCESS('You can now login with username: chris, password: chris123'))