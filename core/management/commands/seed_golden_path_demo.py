"""
Management Command: Seed Golden Path Demo Data

Session 110 - Golden Path Demo & Launch Polish

Seeds demo data for demonstrating both golden paths:
1. Strategic Decision Loop (Boardroom Meeting → Decision → Outcome)
2. Idea to Publish-Ready Assets (Creative Pipeline → Images/Video)

Safe to run multiple times (idempotent based on project name).
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from content.models import CreativeProject, AISession
from coleadership.models import (
    CoLeadershipDecision,
    AdvisorDecisionRecommendation,
    HumanDecision,
    DecisionOutcome,
)
from pipelines.models import CreativePipelineTemplate, CreativePipelineRun
from core.models.agents_registry import UnifiedAgentTemplate

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demo data for Golden Path demonstrations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username to assign demo data to (default: admin)'
        )

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User '{username}' not found. Please create user first."))
            return

        self.stdout.write(self.style.SUCCESS(f"Seeding demo data for user: {username}"))

        # Create or reuse demo project
        project = self._create_demo_project(user)

        # Seed Golden Path 1: Strategic Decision Loop
        decision = self._seed_strategic_decision(user, project)

        # Seed Golden Path 2: Creative Pipelines
        self._seed_creative_pipeline_runs(user, project)

        self.stdout.write(self.style.SUCCESS('✅ Golden Path demo data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS(f'   Project: {project.name} (ID: {project.id})'))
        self.stdout.write(self.style.SUCCESS(f'   Decision: {decision.title} (ID: {decision.id})'))
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('🎬 Ready to demo both golden paths!'))

    def _create_demo_project(self, user):
        """Create or reuse demo project"""
        project_name = "Golden Path Demo"

        project, created = CreativeProject.objects.get_or_create(
            user=user,
            name=project_name,
            defaults={
                'description': 'Demo project showcasing AI-Human Co-Leadership and Creative Pipelines',
                'goal': 'Demonstrate end-to-end AI-Human Co-Leadership workflows and Creative Pipelines',
                'status': 'in_progress',
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'   ✅ Created demo project: {project.name}'))
        else:
            self.stdout.write(f'   ℹ️  Reusing existing project: {project.name}')

        return project

    def _seed_strategic_decision(self, user, project):
        """Seed a complete Strategic Decision Loop"""
        self.stdout.write(self.style.SUCCESS('\n🎯 Seeding Strategic Decision Loop...'))

        # Create AISession for boardroom meeting
        session, _ = AISession.objects.get_or_create(
            title="Q1 2026 AI Feature Roadmap",
            defaults={
                'user': user,
                'session_type': 'boardroom',
                'project': project,
            }
        )

        # Create Decision
        decision, created = CoLeadershipDecision.objects.get_or_create(
            title="Q1 2026 AI Feature Roadmap",
            session=session,
            defaults={
                'project': project,
                'description': 'Should we build full automation or MVP-first for our AI content pipeline?',
                'initiated_by': user,
                'frozen_at': timezone.now() - timedelta(hours=2),  # Decision made 2 hours ago
            }
        )

        if not created:
            self.stdout.write(f'   ℹ️  Decision already exists: {decision.title}')
            return decision

        # Get agent templates (CTO, COO, Product Manager)
        cto = UnifiedAgentTemplate.objects.filter(role='cto').first()
        coo = UnifiedAgentTemplate.objects.filter(role='coo').first()
        pm = UnifiedAgentTemplate.objects.filter(role__icontains='product').first()

        # Create Agent Recommendations
        if cto:
            AdvisorDecisionRecommendation.objects.create(
                decision=decision,
                agent_template=cto,
                stance='support',
                summary='Full automation will give us competitive advantage',
                recommendation_text="""I recommend we build the full automation pipeline now.

Technical feasibility is high - we have the infrastructure, APIs are stable, and our ML models are production-ready. This will give us a 6-month lead over competitors.

Key benefits:
- Reduces manual work by 80%
- Enables real-time processing
- Scales to 10,000+ daily users

Risks are manageable with our DevOps team.""",
                risk_analysis='Infrastructure costs will increase 30%, need monitoring for API rate limits',
                confidence=0.85,
                time_horizon='medium_term',
                raw_payload={'reasoning': 'technical_feasibility', 'estimated_dev_time': '6-8 weeks'}
            )
            self.stdout.write('   ✅ CTO recommendation added')

        if coo:
            AdvisorDecisionRecommendation.objects.create(
                decision=decision,
                agent_template=coo,
                stance='concern',
                summary='Concerned about operational complexity and support burden',
                recommendation_text="""While I see the value, I have concerns about operational readiness.

Our support team isn't trained on AI workflows yet, and we don't have runbooks for failure scenarios. A phased rollout would be safer.

Concerns:
- Support team needs 2-3 weeks training
- No documented incident response procedures
- Current infrastructure monitoring is basic

Recommendation: Start with manual oversight, automate incrementally.""",
                risk_analysis='Customer satisfaction could drop if automated system fails without proper monitoring',
                confidence=0.70,
                time_horizon='short_term',
                raw_payload={'concern_areas': ['support', 'monitoring', 'training']}
            )
            self.stdout.write('   ✅ COO recommendation added')

        if pm:
            AdvisorDecisionRecommendation.objects.create(
                decision=decision,
                agent_template=pm,
                stance='alternative',
                summary='Ship MVP first to validate market fit, then automate',
                recommendation_text="""I propose an alternative path: MVP-first approach.

We should launch a minimal version with 3 core workflows, gather user feedback for 2-3 weeks, THEN automate based on actual usage patterns.

Why this is better:
- Validates product-market fit before heavy investment
- Allows us to pivot based on real user behavior
- Reduces technical debt from features nobody uses
- Still ships in Q1 with lower risk

This is how successful products are built - iterate, learn, scale.""",
                risk_analysis='Delays full automation by 4-6 weeks, but reduces risk of building wrong features',
                alternative_paths=[
                    {
                        'name': 'MVP Phase 1',
                        'duration': '2 weeks',
                        'features': ['Basic image generation', 'Simple pipeline', 'Manual review']
                    },
                    {
                        'name': 'Learn Phase',
                        'duration': '3 weeks',
                        'features': ['User feedback', 'Analytics', 'Usage patterns']
                    },
                    {
                        'name': 'Automation Phase 2',
                        'duration': '4 weeks',
                        'features': ['Automate proven workflows', 'Scale infrastructure']
                    }
                ],
                confidence=0.90,
                time_horizon='long_term',
                raw_payload={'market_validation': 'high_priority', 'customer_interviews': 12}
            )
            self.stdout.write('   ✅ Product Manager recommendation added')

        # Create Human Decision (chose Product Manager's alternative)
        HumanDecision.objects.create(
            decision=decision,
            chosen_path_summary="MVP-first approach with 3-week validation phase, then automation",
            justification="""After reviewing all recommendations, I'm going with the Product Manager's MVP-first approach.

The CTO makes a strong technical case, and I trust our engineering capability. But the COO's concerns about operational readiness are valid - we're not prepared for full automation yet.

Most importantly, the PM's insight about validating market fit resonates. We've built features nobody used before. Let's be smarter this time:
1. Ship minimal viable version
2. Watch how users actually use it
3. Automate the workflows that matter most

This de-risks the investment and gives us real data to inform automation priorities.""",
            is_override=True,  # Human overrode CTO's recommendation
            overridden_agent=cto if cto else None,
        )
        self.stdout.write('   ✅ Human decision committed (override: PM alternative)')

        # Create Decision Outcome (simulated: 3 weeks later, it worked!)
        DecisionOutcome.objects.create(
            decision=decision,
            status='success',
            realized_at=timezone.now() - timedelta(hours=1),
            outcome_summary="""MVP launched successfully! User feedback was overwhelmingly positive.

We validated product-market fit in 3 weeks:
- 47 beta users signed up
- 92% satisfaction score
- Users requested automation for the 3 workflows we built
- Identified 2 workflows we almost built that users DON'T want

Now automating with confidence based on real usage data.""",
            metrics={
                'beta_users': 47,
                'satisfaction_score': 0.92,
                'validated_workflows': 3,
                'avoided_waste_workflows': 2,
                'time_to_validation': '3 weeks'
            },
            attribution='human',  # Human (following PM) was more correct
            ai_confidence_snapshot=0.85,  # CTO's confidence
            human_confidence_snapshot=0.75,  # Human was less confident but right
            told_you_so_triggered=True,
            told_you_so_message="""🎯 Nice call on the MVP-first approach!

The Product Manager's intuition about market validation paid off - you avoided automating 2 workflows that users didn't want, and discovered exactly which features to prioritize.

This is what good co-leadership looks like: AI provides expert analysis, humans bring strategic judgment. Well played! 🤝"""
        )
        self.stdout.write('   ✅ Outcome logged (success: human + PM were right!)')
        self.stdout.write(self.style.SUCCESS(f'   🏆 Strategic Decision Loop complete'))

        return decision

    def _seed_creative_pipeline_runs(self, user, project):
        """Seed Creative Pipeline runs with demo outputs"""
        self.stdout.write(self.style.SUCCESS('\n🎨 Seeding Creative Pipeline Runs...'))

        # Get templates
        image_template = CreativePipelineTemplate.objects.filter(
            slug='idea_to_image_set', is_active=True
        ).first()

        video_template = CreativePipelineTemplate.objects.filter(
            slug='idea_to_promo_video', is_active=True
        ).first()

        if not image_template:
            self.stdout.write(self.style.WARNING('   ⚠️  Image template not found - run: python manage.py seed_pipelines'))
            return

        # Create session for pipeline runs
        session, _ = AISession.objects.get_or_create(
            title="Demo Creative Assets",
            defaults={
                'user': user,
                'session_type': 'content_package',
                'project': project,
            }
        )

        # Run 1: Idea to Image Set (completed successfully)
        run1, created = CreativePipelineRun.objects.get_or_create(
            template=image_template,
            user=user,
            input_payload={'idea': 'A futuristic co-working space where humans and AI robots collaborate at desks'},
            defaults={
                'project': project,
                'session': session,
                'status': 'completed',
                'current_step': 3,
                'total_steps': 3,
                'output_payload': {
                    'prompts': [
                        'A modern co-working space bathed in natural light, with sleek desks where a female professional works alongside a friendly humanoid AI robot, both engaged in collaborative design work on shared holographic displays',
                        'Close-up shot of a human hand and robotic hand collaborating on a digital tablet screen, fingers pointing at innovative interface elements, warm lighting emphasizing the partnership',
                        'Wide-angle view of a futuristic open-plan office with glass walls, showing multiple human-AI teams working together at various stations, advanced technology seamlessly integrated into the workspace'
                    ],
                    'images': [
                        {
                            'url': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800',
                            'prompt': 'Modern co-working space with natural light',
                            'index': 1
                        },
                        {
                            'url': 'https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=800',
                            'prompt': 'Collaborative workspace close-up',
                            'index': 2
                        },
                        {
                            'url': 'https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=800',
                            'prompt': 'Futuristic office wide shot',
                            'index': 3
                        }
                    ]
                },
                'log': """[2025-11-15 14:00:00] Pipeline started
[2025-11-15 14:00:01] Step 1/3: GPT Expansion
[2025-11-15 14:00:04] Generated 3 detailed prompts from idea
[2025-11-15 14:00:04] Step 2/3: Image Generation
[2025-11-15 14:00:24] Generated image 1/3
[2025-11-15 14:00:42] Generated image 2/3
[2025-11-15 14:00:58] Generated image 3/3
[2025-11-15 14:00:58] Step 3/3: Save Assets
[2025-11-15 14:00:59] Saved 3 images to ImageHistory
[2025-11-15 14:00:59] Pipeline completed successfully""",
                'error_message': '',
                'completed_at': timezone.now() - timedelta(hours=3),
            }
        )

        if created:
            self.stdout.write('   ✅ Pipeline Run 1: "Idea to Image Set" (completed)')

        # Run 2: Idea to Promo Video (if template exists)
        if video_template:
            run2, created = CreativePipelineRun.objects.get_or_create(
                template=video_template,
                user=user,
                input_payload={'idea': 'Launch video for AI-Human Co-Leadership platform', 'duration': 30},
                defaults={
                    'project': project,
                    'session': session,
                    'status': 'completed',
                    'current_step': 4,
                    'total_steps': 4,
                    'output_payload': {
                        'script': """[0-5s] Voiceover: "What if AI and humans worked as equals?"
[5-10s] Show human executive and AI agent reviewing data side-by-side
[10-15s] Voiceover: "Not AI replacing humans. AI empowering them."
[15-20s] Show strategic decision being made collaboratively
[20-25s] Voiceover: "Introducing AI-Human Co-Leadership."
[25-30s] Show platform logo and tagline: "Better decisions, together." """,
                        'keyframes': [
                            {'url': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=800', 'timestamp': 5},
                            {'url': 'https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800', 'timestamp': 15},
                            {'url': 'https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=800', 'timestamp': 25}
                        ],
                        'video_url': 'https://example.com/demo-promo-video.mp4'  # Placeholder for v1
                    },
                    'log': """[2025-11-15 15:30:00] Pipeline started
[2025-11-15 15:30:01] Step 1/4: GPT Script Generation
[2025-11-15 15:30:06] Generated 30-second script with shot list
[2025-11-15 15:30:06] Step 2/4: Image Generation (keyframes)
[2025-11-15 15:30:28] Generated 3 keyframe images
[2025-11-15 15:30:28] Step 3/4: Save Assets
[2025-11-15 15:30:29] Saved 3 keyframes to ImageHistory
[2025-11-15 15:30:29] Step 4/4: Video Creation
[2025-11-15 15:30:29] ⚠️  Video assembly not implemented in v1 (placeholder)
[2025-11-15 15:30:29] Pipeline completed""",
                    'error_message': '',
                    'completed_at': timezone.now() - timedelta(hours=1),
                }
            )

            if created:
                self.stdout.write('   ✅ Pipeline Run 2: "Idea to Promo Video" (completed)')

        self.stdout.write(self.style.SUCCESS(f'   🏆 Creative Pipeline runs complete'))
