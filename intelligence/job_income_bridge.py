"""
Bridge module to connect AI Job Tracker with Income Builder
This creates a unified pipeline where job opportunities flow seamlessly
"""

import logging
from typing import List, Dict, Any
from django.core.cache import cache
from datetime import datetime

logger = logging.getLogger(__name__)


class JobIncomeBridge:
    """Bridge to unify AI Job Tracker and Income Builder data"""

    @staticmethod
    def get_unified_opportunities() -> Dict[str, Any]:
        """
        Get unified opportunities from both AI Job Tracker and Income Builder
        Returns a merged dataset with jobs converted to income opportunities
        """

        # Get cached live jobs
        jobs = cache.get('live_jobs', [])

        # Convert jobs to income opportunities format
        job_opportunities = []

        for job in jobs[:20]:  # Take top 20 jobs
            # Calculate potential monthly from salary string
            salary = job.get('salary', '$3,000/month')
            if isinstance(salary, str):
                # Extract numbers from salary string
                import re
                numbers = re.findall(r'\d+(?:,\d+)*', salary.replace(',', ''))
                monthly = int(numbers[0]) if numbers else 3000
            else:
                monthly = 3000

            opportunity = {
                'id': f"job_{job.get('id', '')}",
                'title': job.get('title', 'Remote Opportunity'),
                'stream_type': 'Freelance/Contract',
                'description': job.get('description', '')[:300],
                'potential_monthly': f"${monthly:,}",
                'time_to_income': '1-2 weeks',
                'difficulty': 'intermediate',
                'initial_investment': 0,
                'success_rate': job.get('aiScore', 0.75) * 100,
                'market_demand': 85,
                'required_skills': job.get('tags', [])[:5] if job.get('tags') else ['communication', 'problem-solving'],
                'action_steps': [
                    'Review job requirements',
                    'Customize application with AI',
                    'Submit within 24 hours',
                    'Follow up in 3 days'
                ],
                'resources': [
                    {'name': 'View Job Posting', 'url': job.get('url', '#')},
                    {'name': f"{job.get('source', 'Job Board').title()} Platform", 'url': '#'}
                ],
                'match_reasons': [
                    f"AI Match Score: {job.get('aiScore', 0.75)*100:.0f}%",
                    f"Company: {job.get('company', 'Remote')}",
                    f"Source: {job.get('source', 'Job Board')}"
                ],
                'company': job.get('company', 'Unknown'),
                'url': job.get('url', '#'),
                'source': job.get('source', 'ai_job_tracker'),
                'job_id': job.get('id'),
                'posted_date': job.get('posted', datetime.now().isoformat()),
                'is_real_job': True
            }
            job_opportunities.append(opportunity)

        # Add Income Builder native opportunities (non-job based)
        income_opportunities = [
            {
                'id': 'income_ai_1',
                'title': 'AI Prompt Engineering Services',
                'stream_type': 'AI Services',
                'description': 'Offer prompt optimization for businesses using ChatGPT/Claude',
                'potential_monthly': '$2,000-$5,000',
                'time_to_income': '3-5 days',
                'difficulty': 'intermediate',
                'success_rate': 85,
                'market_demand': 95,
                'required_skills': ['AI knowledge', 'writing', 'testing'],
                'action_steps': [
                    'Create prompt templates',
                    'List on Promptbase',
                    'Offer on Fiverr',
                    'Network in AI communities'
                ],
                'match_reasons': [
                    'High demand skill',
                    'Low competition',
                    'Recurring revenue potential'
                ],
                'resources': [
                    {'name': 'Promptbase Marketplace', 'url': 'promptbase.com'},
                    {'name': 'Learn Prompting', 'url': 'learnprompting.org'}
                ],
                'is_real_job': False
            },
            {
                'id': 'income_auto_1',
                'title': 'Automation Consulting',
                'stream_type': 'Automation',
                'description': 'Help businesses automate with Zapier/Make.com',
                'potential_monthly': '$1,500-$4,000',
                'time_to_income': '1 week',
                'difficulty': 'beginner',
                'success_rate': 75,
                'market_demand': 85,
                'required_skills': ['logic', 'process mapping', 'communication'],
                'action_steps': [
                    'Learn Zapier basics',
                    'Create case studies',
                    'Target small businesses',
                    'Offer free consultation'
                ],
                'match_reasons': [
                    'Easy to learn',
                    'Businesses need it',
                    'Can charge premium'
                ],
                'resources': [
                    {'name': 'Zapier Academy', 'url': 'zapier.com/learn'},
                    {'name': 'Make Academy', 'url': 'academy.make.com'}
                ],
                'is_real_job': False
            }
        ]

        # Merge all opportunities
        all_opportunities = job_opportunities + income_opportunities

        # Sort by success rate and potential
        all_opportunities.sort(key=lambda x: (x.get('success_rate', 0), x.get('market_demand', 0)), reverse=True)

        # Calculate aggregate stats
        total_jobs = len(job_opportunities)
        total_income_streams = len(income_opportunities)
        avg_monthly_potential = sum([
            int(str(opp.get('potential_monthly', '$0')).replace('$', '').replace(',', '').split('-')[0])
            for opp in all_opportunities[:10]
        ]) / 10 if all_opportunities else 0

        return {
            'opportunities': all_opportunities,
            'stats': {
                'total_opportunities': len(all_opportunities),
                'real_jobs': total_jobs,
                'income_streams': total_income_streams,
                'avg_monthly_potential': avg_monthly_potential,
                'top_category': 'AI Services' if all_opportunities else 'None',
                'success_rate': sum(opp.get('success_rate', 0) for opp in all_opportunities[:5]) / 5 if all_opportunities else 0
            },
            'source': 'unified_bridge',
            'timestamp': datetime.now().isoformat()
        }

    @staticmethod
    def sync_to_income_builder(jobs: List[Dict]) -> None:
        """Sync AI Job Tracker jobs to Income Builder format"""
        # Store in shared cache for Income Builder to access
        cache.set('unified_opportunities', jobs, 3600)  # Cache for 1 hour
        logger.info(f"Synced {len(jobs)} jobs to Income Builder")

    @staticmethod
    def get_personalized_opportunities(user_profile: Dict) -> List[Dict]:
        """Get opportunities personalized for user profile"""
        all_data = JobIncomeBridge.get_unified_opportunities()
        opportunities = all_data['opportunities']

        # Filter based on user skills
        user_skills = set(user_profile.get('skills', []))

        if user_skills:
            # Score each opportunity based on skill match
            for opp in opportunities:
                required_skills = set(opp.get('required_skills', []))
                if required_skills:
                    match_score = len(user_skills.intersection(required_skills)) / len(required_skills)
                    opp['skill_match'] = match_score
                else:
                    opp['skill_match'] = 0.5

            # Sort by skill match
            opportunities.sort(key=lambda x: x.get('skill_match', 0), reverse=True)

        return opportunities[:20]  # Return top 20 personalized opportunities