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

        # Get cached opportunities from real spider
        jobs = cache.get('latest_opportunities', [])

        # If no jobs from spider cache, also check live_jobs for fallback
        if not jobs:
            jobs = cache.get('live_jobs', [])

        # Ensure jobs is a list
        if not isinstance(jobs, list):
            jobs = []

        # Convert jobs to income opportunities format
        job_opportunities = []

        for job in jobs[:50]:  # Take top 50 jobs (we have 76 real opportunities)
            # Calculate potential monthly from spider data structure
            if job.get('salary_min') and job.get('salary_max'):
                # Use average of salary range
                monthly = (job.get('salary_min', 0) + job.get('salary_max', 0)) // 2
            elif job.get('salary'):
                # Legacy salary string format
                salary = job.get('salary', '$3,000/month')
                if isinstance(salary, str):
                    import re
                    numbers = re.findall(r'\d+(?:,\d+)*', salary.replace(',', ''))
                    monthly = int(numbers[0]) if numbers else 3000
                else:
                    monthly = 3000
            else:
                monthly = 3000

            # Create unique ID from title and company (lowercase to match revenue consumer)
            job_id = job.get('id') or f"{job.get('source', 'spider').lower()}_{hash(job.get('title', '') + job.get('company', '')) % 10000}"

            opportunity = {
                'id': job_id,  # Remove "job_" prefix to match revenue opportunities consumer
                'title': job.get('title', 'Remote Opportunity'),
                'stream_type': f"{job.get('source', 'Remote').title()} Job",
                'description': job.get('description', '')[:300],
                'potential_monthly': f"${monthly:,}",
                'time_to_income': '1-2 weeks',
                'difficulty': 'intermediate',
                'initial_investment': 0,
                'success_rate': min(1.0, job.get('match_score', 75) / 100 if job.get('match_score', 75) > 1 else job.get('match_score', 0.75)),
                'market_demand': 0.85,
                'required_skills': job.get('tags', [])[:5] if job.get('tags') else ['remote work', 'communication'],
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
                    f"Match Score: {job.get('match_score', 75):.0f}%",
                    f"Company: {job.get('company', 'Remote Company')}",
                    f"Source: {job.get('source', 'Spider Network')}"
                ],
                'company': job.get('company', 'Unknown'),
                'url': job.get('url', '#'),
                'source': job.get('source', 'ai_job_tracker'),
                'job_id': job.get('id'),
                'posted_date': job.get('posted', datetime.now().isoformat()),
                'is_real_job': True
            }
            job_opportunities.append(opportunity)

        # Use only real job opportunities - no more hardcoded mock data
        all_opportunities = job_opportunities

        # Sort by match score and salary potential
        all_opportunities.sort(key=lambda x: (x.get('success_rate', 0),
                                            (x.get('salary_min', 0) + x.get('salary_max', 0)) / 2 if x.get('salary_min') else 0),
                             reverse=True)

        # Calculate aggregate stats from real data
        total_jobs = len(job_opportunities)
        avg_monthly_potential = sum([
            int(str(opp.get('potential_monthly', '$0')).replace('$', '').replace(',', '').split('-')[0])
            for opp in all_opportunities[:10]
        ]) / 10 if all_opportunities else 0

        return {
            'opportunities': all_opportunities,
            'stats': {
                'total_opportunities': len(all_opportunities),
                'real_jobs': total_jobs,
                'income_streams': 0,  # No more hardcoded income streams
                'avg_monthly_potential': avg_monthly_potential,
                'top_category': 'Remote Jobs' if all_opportunities else 'None',
                'avg_success_rate': sum(opp.get('success_rate', 0) for opp in all_opportunities[:5]) / 5 if all_opportunities else 0
            },
            'source': 'unified_bridge_real_jobs_only',
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