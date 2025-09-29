"""
Unified Job Search Interface
Aggregates jobs from all free sources and provides intelligent matching
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import sys

# Handle Django imports gracefully
try:
    from django.core.cache import cache
    from django.db import models
    from django.contrib.auth.models import User
except:
    # For standalone testing
    class MockCache:
        def get(self, key, default=None):
            return default
        def set(self, key, value, timeout=None):
            pass
    cache = MockCache()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_core.spiders.real_job_spider import RealJobSpider

logger = logging.getLogger(__name__)


class UnifiedJobSearch:
    """
    Unified interface for searching and managing job opportunities
    from multiple free sources without API keys
    """

    def __init__(self):
        self.spider = RealJobSpider()
        self.cache_duration = 3600  # Cache for 1 hour

    async def search_jobs(
        self,
        keywords: List[str] = None,
        user_profile: Dict[str, Any] = None,
        filters: Dict[str, Any] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Search for jobs across all sources with intelligent filtering and scoring

        Args:
            keywords: Search keywords
            user_profile: User profile for personalized scoring
            filters: Additional filters (location, salary, etc.)
            limit: Maximum number of results

        Returns:
            Dict containing jobs, metadata, and analytics
        """
        # Generate cache key
        cache_key = self._generate_cache_key(keywords, filters)

        # Check cache first
        cached_results = cache.get(cache_key)
        if cached_results and not user_profile:
            logger.info("Returning cached job results")
            return cached_results

        # Search for jobs
        logger.info(f"Searching for jobs with keywords: {keywords}")
        all_opportunities = await self.spider.search_real_jobs(keywords)

        # Apply filters
        if filters:
            all_opportunities = self._apply_filters(all_opportunities, filters)

        # Score opportunities if user profile provided
        if user_profile:
            all_opportunities = await self._score_and_sort(all_opportunities, user_profile)
        else:
            # Sort by recency
            all_opportunities.sort(
                key=lambda x: self._parse_date(x.get('date_posted', '')),
                reverse=True
            )

        # Limit results
        all_opportunities = all_opportunities[:limit]

        # Generate analytics
        analytics = self._generate_analytics(all_opportunities)

        result = {
            'jobs': all_opportunities,
            'total_found': len(all_opportunities),
            'sources_searched': self._get_sources_searched(),
            'analytics': analytics,
            'search_timestamp': datetime.now().isoformat(),
            'keywords': keywords,
            'filters': filters
        }

        # Cache results if no user profile (non-personalized)
        if not user_profile:
            cache.set(cache_key, result, self.cache_duration)

        return result

    async def get_personalized_recommendations(
        self,
        user_profile: Dict[str, Any],
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get personalized job recommendations based on user profile

        Args:
            user_profile: Complete user profile with skills, preferences
            limit: Maximum number of recommendations

        Returns:
            Personalized job recommendations with match explanations
        """
        # Generate smart keywords from profile
        keywords = self._extract_keywords_from_profile(user_profile)

        # Search with extracted keywords
        all_jobs = await self.spider.search_real_jobs(keywords)

        # Score all jobs
        scored_jobs = []
        for job in all_jobs:
            score_breakdown = await self.spider.score_opportunity(job, user_profile)
            job['scoring'] = score_breakdown
            job['match_score'] = score_breakdown['overall_score']
            scored_jobs.append(job)

        # Sort by match score
        scored_jobs.sort(key=lambda x: x['match_score'], reverse=True)

        # Get top matches
        top_matches = scored_jobs[:limit]

        # Group by match quality
        excellent_matches = [j for j in top_matches if j['match_score'] >= 0.8]
        good_matches = [j for j in top_matches if 0.6 <= j['match_score'] < 0.8]
        potential_matches = [j for j in top_matches if j['match_score'] < 0.6]

        return {
            'recommendations': top_matches,
            'excellent_matches': excellent_matches,
            'good_matches': good_matches,
            'potential_matches': potential_matches,
            'profile_summary': self._generate_profile_summary(user_profile),
            'search_insights': self._generate_search_insights(scored_jobs),
            'timestamp': datetime.now().isoformat()
        }

    async def _score_and_sort(
        self,
        opportunities: List[Dict[str, Any]],
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Score and sort opportunities based on user profile"""
        scored_opps = []
        for opp in opportunities:
            score_breakdown = await self.spider.score_opportunity(opp, user_profile)
            opp['scoring'] = score_breakdown
            opp['match_score'] = score_breakdown['overall_score']
            scored_opps.append(opp)

        # Sort by match score
        scored_opps.sort(key=lambda x: x['match_score'], reverse=True)
        return scored_opps

    def _apply_filters(
        self,
        opportunities: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply filters to job opportunities"""
        filtered = opportunities

        # Location filter
        if filters.get('location'):
            location_filter = filters['location'].lower()
            filtered = [
                j for j in filtered
                if location_filter in j.get('location', '').lower()
            ]

        # Salary filter
        if filters.get('min_salary'):
            min_salary = filters['min_salary']
            filtered = [
                j for j in filtered
                if j.get('salary_max', 0) >= min_salary or
                j.get('salary_min', 0) >= min_salary * 0.8
            ]

        # Source filter
        if filters.get('sources'):
            sources = filters['sources']
            filtered = [
                j for j in filtered
                if j.get('source') in sources
            ]

        # Date filter
        if filters.get('posted_within_days'):
            days = filters['posted_within_days']
            cutoff_date = datetime.now() - timedelta(days=days)

            def is_recent(date_str):
                parsed = self._parse_date(date_str)
                # Make both dates timezone-naive for comparison
                if parsed.tzinfo:
                    parsed = parsed.replace(tzinfo=None)
                if cutoff_date.tzinfo:
                    cutoff_date_naive = cutoff_date.replace(tzinfo=None)
                else:
                    cutoff_date_naive = cutoff_date
                return parsed >= cutoff_date_naive

            filtered = [
                j for j in filtered
                if is_recent(j.get('date_posted', ''))
            ]

        # Job type filter
        if filters.get('job_type'):
            job_type = filters['job_type'].lower()
            filtered = [
                j for j in filtered
                if job_type in j.get('title', '').lower() or
                job_type in j.get('description', '').lower()
            ]

        return filtered

    def _generate_analytics(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate analytics from job opportunities"""
        if not opportunities:
            return {}

        # Source distribution
        source_counts = {}
        for job in opportunities:
            source = job.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1

        # Salary statistics
        salaries = [
            j.get('salary_max', 0) for j in opportunities
            if j.get('salary_max', 0) > 0
        ]

        salary_stats = {}
        if salaries:
            salary_stats = {
                'average': sum(salaries) / len(salaries),
                'min': min(salaries),
                'max': max(salaries),
                'median': sorted(salaries)[len(salaries) // 2]
            }

        # Location distribution
        location_counts = {}
        for job in opportunities:
            location = job.get('location', 'Unknown')
            if location:
                location_counts[location] = location_counts.get(location, 0) + 1

        # Top companies
        company_counts = {}
        for job in opportunities:
            company = job.get('company', 'Unknown')
            company_counts[company] = company_counts.get(company, 0) + 1

        top_companies = sorted(
            company_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            'source_distribution': source_counts,
            'salary_statistics': salary_stats,
            'location_distribution': dict(
                sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            'top_hiring_companies': dict(top_companies),
            'total_opportunities': len(opportunities)
        }

    def _extract_keywords_from_profile(self, user_profile: Dict[str, Any]) -> List[str]:
        """Extract intelligent keywords from user profile"""
        keywords = []

        # Extract from skills
        if 'skills' in user_profile:
            skills = user_profile['skills']
            if isinstance(skills, dict):
                keywords.extend(skills.get('primary', []))
                keywords.extend(skills.get('secondary', [])[:2])
            elif isinstance(skills, list):
                keywords.extend(skills[:5])

        # Extract from industries
        if 'industries' in user_profile:
            keywords.extend(user_profile['industries'][:2])

        # Extract from job preferences
        if 'job_type_preference' in user_profile:
            keywords.append(user_profile['job_type_preference'])

        # Add location if remote
        if 'location_preferences' in user_profile:
            loc_prefs = user_profile['location_preferences']
            if isinstance(loc_prefs, dict) and loc_prefs.get('remote_only'):
                keywords.append('remote')

        # Deduplicate and return
        return list(dict.fromkeys(keywords))[:10]

    def _generate_profile_summary(self, user_profile: Dict[str, Any]) -> str:
        """Generate a summary of the user profile"""
        summary_parts = []

        if 'experience_years' in user_profile:
            summary_parts.append(f"{user_profile['experience_years']} years experience")

        if 'skills' in user_profile:
            skills = user_profile['skills']
            if isinstance(skills, dict) and 'primary' in skills:
                summary_parts.append(f"Expert in {', '.join(skills['primary'][:3])}")
            elif isinstance(skills, list):
                summary_parts.append(f"Skilled in {', '.join(skills[:3])}")

        if 'desired_salary' in user_profile:
            salary = user_profile['desired_salary']
            summary_parts.append(f"Target salary: ${salary:,}")

        return " | ".join(summary_parts) if summary_parts else "No profile information"

    def _generate_search_insights(self, scored_jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights from search results"""
        if not scored_jobs:
            return {}

        # Match score distribution
        excellent = len([j for j in scored_jobs if j['match_score'] >= 0.8])
        good = len([j for j in scored_jobs if 0.6 <= j['match_score'] < 0.8])
        fair = len([j for j in scored_jobs if 0.4 <= j['match_score'] < 0.6])
        poor = len([j for j in scored_jobs if j['match_score'] < 0.4])

        # Most common missing requirements
        missing_reqs = {}
        for job in scored_jobs[:20]:
            for req in job.get('scoring', {}).get('missing_requirements', []):
                missing_reqs[req] = missing_reqs.get(req, 0) + 1

        top_missing = sorted(
            missing_reqs.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            'match_distribution': {
                'excellent': excellent,
                'good': good,
                'fair': fair,
                'poor': poor
            },
            'top_missing_skills': dict(top_missing),
            'average_match_score': sum(j['match_score'] for j in scored_jobs) / len(scored_jobs) if scored_jobs else 0,
            'recommendation': self._generate_recommendation(excellent, good, top_missing)
        }

    def _generate_recommendation(self, excellent: int, good: int, top_missing: List) -> str:
        """Generate actionable recommendation based on search results"""
        if excellent >= 5:
            return "Excellent matches found! You have many opportunities that align perfectly with your profile."
        elif excellent + good >= 10:
            return "Good opportunities available. Consider applying to your top matches soon."
        elif top_missing:
            missing_skill = top_missing[0][0] if top_missing else "additional skills"
            return f"Consider adding {missing_skill} to your skillset to access more opportunities."
        else:
            return "Broaden your search criteria or consider updating your profile for better matches."

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        if not date_str:
            return datetime.min

        try:
            from dateutil import parser
            return parser.parse(date_str)
        except:
            try:
                # Try common formats
                for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except:
                        continue
            except:
                pass

        return datetime.min

    def _generate_cache_key(self, keywords: List[str] = None, filters: Dict = None) -> str:
        """Generate cache key for search results"""
        key_parts = ['job_search']

        if keywords:
            key_parts.append('_'.join(sorted(keywords)[:5]))

        if filters:
            filter_str = '_'.join(f"{k}_{v}" for k, v in sorted(filters.items())[:3])
            key_parts.append(filter_str)

        return ':'.join(key_parts)

    def _get_sources_searched(self) -> List[str]:
        """Get list of all sources being searched"""
        return [
            'RemoteOK',
            'Remotive',
            'WeWorkRemotely',
            'StackOverflow Jobs',
            'DEV.to',
            'HackerNews',
            'Wellfound',
            'CryptoJobsList',
            'USAJobs',
            'RSS Aggregator (5+ sources)'
        ]

    async def save_search_results(
        self,
        user_id: int,
        search_results: Dict[str, Any]
    ) -> bool:
        """Save search results for user history"""
        try:
            # This would integrate with your Django models
            # For now, we'll cache it
            cache_key = f"user_search_history:{user_id}"
            history = cache.get(cache_key, [])

            # Add new search to history
            history.insert(0, {
                'timestamp': datetime.now().isoformat(),
                'keywords': search_results.get('keywords'),
                'results_count': search_results.get('total_found'),
                'top_match': search_results['jobs'][0] if search_results.get('jobs') else None
            })

            # Keep only last 10 searches
            history = history[:10]

            cache.set(cache_key, history, 86400 * 7)  # Cache for 7 days
            return True
        except Exception as e:
            logger.error(f"Error saving search results: {e}")
            return False


async def test_unified_search():
    """Test the unified job search interface"""
    search = UnifiedJobSearch()

    # Test 1: Basic search
    print("=" * 80)
    print("TEST 1: Basic Job Search")
    print("=" * 80)

    results = await search.search_jobs(
        keywords=['python', 'remote', 'developer'],
        filters={
            'posted_within_days': 7,
            'location': 'remote'
        },
        limit=10
    )

    print(f"Found {results['total_found']} jobs from {len(results['sources_searched'])} sources")
    print(f"\nTop 3 jobs:")
    for i, job in enumerate(results['jobs'][:3], 1):
        print(f"{i}. {job['title']} at {job['company']} ({job['source']})")

    print(f"\nAnalytics:")
    print(f"Source distribution: {results['analytics'].get('source_distribution', {})}")

    # Test 2: Personalized recommendations
    print("\n" + "=" * 80)
    print("TEST 2: Personalized Recommendations")
    print("=" * 80)

    user_profile = {
        'skills': {
            'primary': ['python', 'django', 'machine learning'],
            'secondary': ['javascript', 'react', 'aws']
        },
        'experience_years': 5,
        'desired_salary': 120000,
        'location_preferences': {
            'remote_only': True
        },
        'industries': ['tech', 'ai', 'fintech'],
        'company_size_preference': 'startup',
        'job_type_preference': 'full-time'
    }

    recommendations = await search.get_personalized_recommendations(
        user_profile=user_profile,
        limit=10
    )

    print(f"Profile: {recommendations['profile_summary']}")
    print(f"\nExcellent matches: {len(recommendations['excellent_matches'])}")
    print(f"Good matches: {len(recommendations['good_matches'])}")
    print(f"Potential matches: {len(recommendations['potential_matches'])}")

    if recommendations['excellent_matches']:
        print(f"\nTop excellent match:")
        top = recommendations['excellent_matches'][0]
        print(f"  {top['title']} at {top['company']}")
        print(f"  Match score: {top['match_score']:.1%}")
        print(f"  Why it matches: {', '.join(top['scoring']['match_reasons'][:3])}")

    print(f"\nSearch Insights:")
    insights = recommendations['search_insights']
    print(f"  Average match score: {insights.get('average_match_score', 0):.1%}")
    print(f"  Recommendation: {insights.get('recommendation', '')}")

    await search.spider.close()


if __name__ == "__main__":
    asyncio.run(test_unified_search())