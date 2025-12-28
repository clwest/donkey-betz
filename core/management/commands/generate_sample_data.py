"""
Generate sample data to demonstrate the system working
This creates real opportunities, revenue, and activities
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models_unified_system import (
    Agent, Advisor, Revenue, Opportunity,
    AgentExecution, Collaboration, SpiderData,
    AdvisorInsight
)
from decimal import Decimal
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate sample data to demonstrate the complete system'

    def handle(self, *args, **options):
        self.stdout.write("🎲 GENERATING SAMPLE DATA TO DEMONSTRATE THE SYSTEM!")

        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Demo',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('demo123')
            user.save()

        # Get some agents and advisors
        agents = list(Agent.objects.filter(is_active=True)[:10])
        advisors = list(Advisor.objects.filter(is_active=True)[:5])

        if not agents:
            self.stdout.write(self.style.ERROR("No agents found! Run load_all_agents_advisors first."))
            return

        # Create opportunities
        self.stdout.write("📋 Creating opportunities...")
        opportunities_data = [
            ('Senior Python Developer', 'job', 150000, 'LinkedIn'),
            ('React Frontend Contract', 'gig', 85000, 'Upwork'),
            ('AI Consultant Role', 'consulting', 200000, 'Direct'),
            ('Machine Learning Engineer', 'job', 175000, 'Indeed'),
            ('Full Stack Developer', 'job', 140000, 'AngelList'),
            ('Blockchain Developer', 'contract', 95000, 'Crypto Jobs'),
            ('Data Science Lead', 'job', 180000, 'Glassdoor'),
            ('Mobile App Developer', 'gig', 70000, 'Fiverr'),
            ('DevOps Engineer', 'job', 160000, 'Stack Overflow'),
            ('Technical Writer', 'contract', 60000, 'Remote.co')
        ]

        for title, opp_type, revenue, source in opportunities_data:
            opportunity, created = Opportunity.objects.get_or_create(
                user=user,
                title=title,
                defaults={
                    'opportunity_type': opp_type,
                    'source': source,
                    'potential_revenue': Decimal(str(revenue)),
                    'hourly_rate': Decimal(str(revenue / 2000)) if opp_type == 'gig' else None,
                    'status': random.choice(['active', 'pending', 'applied']),
                    'match_score': random.randint(70, 95),
                    'recommended_by': random.choice(agents),
                    'description': f'Great opportunity for {title} via {source}',
                    'requirements': ['Python', 'Django', 'React', 'AWS'][:random.randint(2, 4)]
                }
            )
            if created:
                self.stdout.write(f"  ✅ Created opportunity: {title}")

        # Create revenue entries
        self.stdout.write("💰 Creating revenue entries...")
        revenue_data = [
            ('Freelance Project', 'gig', 5000, 'completed'),
            ('Contract Work', 'contract', 12000, 'completed'),
            ('Consulting Fee', 'consulting', 8500, 'completed'),
            ('Side Project', 'project', 3200, 'completed'),
            ('Commission', 'commission', 1850, 'completed'),
            ('Referral Bonus', 'referral', 500, 'completed'),
            ('Teaching Income', 'teaching', 2400, 'pending'),
            ('Investment Return', 'investment', 4200, 'completed')
        ]

        total_revenue = Decimal('0')
        for description, source_type, amount, status in revenue_data:
            revenue = Revenue.objects.create(
                user=user,
                source_type=source_type,
                amount=Decimal(str(amount)),
                status=status,
                description=description,
                agent=random.choice(agents) if random.random() > 0.3 else None,
                earned_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            if status == 'completed':
                total_revenue += revenue.amount
            self.stdout.write(f"  ✅ Created revenue: {description} - ${amount}")

        # Create agent executions
        self.stdout.write("🤖 Creating agent executions...")
        for _ in range(20):
            agent = random.choice(agents)
            execution = AgentExecution.objects.create(
                agent=agent,
                user=user,
                task=f"Task: {random.choice(['Find opportunities', 'Analyze market', 'Generate content', 'Optimize profile'])}",
                status=random.choice(['completed', 'completed', 'completed', 'in_progress']),
                tokens_used=random.randint(100, 5000),
                cost=Decimal(str(random.uniform(0.01, 2.00))),
                execution_time_ms=random.randint(100, 5000)
            )

        # Create advisor insights
        self.stdout.write("💡 Creating advisor insights...")
        for advisor in advisors[:3]:
            for _ in range(2):
                insight = AdvisorInsight.objects.create(
                    advisor=advisor,
                    user=user,
                    content=f"{advisor.name} recommends: {random.choice(['Focus on high-value opportunities', 'Diversify your income streams', 'Invest in skill development', 'Build your personal brand'])}",
                    category=random.choice(['strategy', 'investment', 'career', 'growth']),
                    confidence=random.randint(75, 95),
                    is_actionable=True
                )

        # Create a collaboration
        self.stdout.write("🤝 Creating collaborations...")
        collaboration = Collaboration.objects.create(
            user=user,
            lead_agent=agents[0],
            objective="Find and apply to best matching opportunities",
            status='active'
        )
        collaboration.collaborating_agents.set(agents[1:4])
        collaboration.advisors.set(advisors[:2])

        # Create spider data
        self.stdout.write("🕷️ Creating spider data...")
        for _ in range(10):
            SpiderData.objects.create(
                spider_name=f"JobSpider_{random.randint(1, 5)}",
                source_url=f"https://example.com/job/{random.randint(1000, 9999)}",
                data_type='job_posting',
                raw_data={'title': 'Sample Job', 'salary': random.randint(50000, 200000)},
                relevance_score=random.randint(60, 95),
                is_processed=True,
                is_actionable=random.random() > 0.5
            )

        # Summary
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("✅ SAMPLE DATA GENERATION COMPLETE!"))
        self.stdout.write(f"📊 Total Revenue Generated: ${total_revenue}")
        self.stdout.write(f"💼 Active Opportunities: {Opportunity.objects.filter(user=user, status='active').count()}")
        self.stdout.write(f"🤖 Agent Executions: {AgentExecution.objects.filter(user=user).count()}")
        self.stdout.write(f"💡 Advisor Insights: {AdvisorInsight.objects.filter(user=user).count()}")
        self.stdout.write(f"🕷️ Spider Data Points: {SpiderData.objects.count()}")
        self.stdout.write("\n🔑 Login with: username='demo_user', password='demo123'")