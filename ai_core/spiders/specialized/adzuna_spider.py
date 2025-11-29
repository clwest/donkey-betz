"""
Adzuna Spider - Global Job Market Intelligence
===============================================

Session 263: Specialized spider for Adzuna job aggregator API.
Provides comprehensive job market data, salary trends, and employment
intelligence from thousands of job boards worldwide.

Requires ADZUNA_APP_ID and ADZUNA_APP_KEY environment variables.
Free tier available for development/educational use.
"""

import os
import asyncio
import aiohttp
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from collections import Counter

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class AdzunaSpider(BaseIntelligenceSpider):
    """Adzuna spider - global job market intelligence and salary data"""

    BASE_URL = 'https://api.adzuna.com/v1/api'

    # Countries to search (Adzuna supports 16+ countries)
    COUNTRIES = {
        'us': 'United States',
        'gb': 'United Kingdom',
        'ca': 'Canada',
        'au': 'Australia',
        'de': 'Germany',
    }

    # Job categories relevant to content creators and tech professionals
    CATEGORIES = [
        'it-jobs',
        'creative-design-jobs',
        'marketing-jobs',
        'media-digital-jobs',
        'engineering-jobs',
    ]

    # Keywords for remote/freelance detection
    REMOTE_KEYWORDS = ['remote', 'work from home', 'wfh', 'anywhere', 'distributed', 'telecommute']
    FREELANCE_KEYWORDS = ['freelance', 'contract', 'contractor', 'consultant', 'part-time', 'gig']

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.app_id = os.getenv('ADZUNA_APP_ID', '')
        self.app_key = os.getenv('ADZUNA_APP_KEY', '')

        # Skill keywords to track
        self.skill_keywords = {
            'programming': ['python', 'javascript', 'typescript', 'react', 'node', 'java', 'go', 'rust'],
            'design': ['figma', 'photoshop', 'illustrator', 'ui/ux', 'graphic design', 'canva'],
            'ai_ml': ['machine learning', 'ai', 'artificial intelligence', 'deep learning', 'nlp', 'llm'],
            'data': ['sql', 'data analysis', 'analytics', 'tableau', 'power bi', 'excel'],
            'content': ['content writing', 'copywriting', 'seo', 'social media', 'marketing'],
            'video': ['video editing', 'premiere', 'after effects', 'final cut', 'davinci'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch job listings from Adzuna API"""
        if not self.app_id or not self.app_key:
            self.logger.warning("ADZUNA credentials not configured - using simulated data")
            return self._get_fallback_data()

        try:
            all_jobs = []
            salary_data = {}
            category_stats = {}

            async with aiohttp.ClientSession() as session:
                # Search for jobs in each category
                for country in ['us', 'gb']:  # Limit to 2 countries to avoid rate limits
                    for category in self.CATEGORIES[:3]:  # Limit categories
                        try:
                            params = {
                                'app_id': self.app_id,
                                'app_key': self.app_key,
                                'results_per_page': 20,
                                'what': 'remote',  # Focus on remote jobs
                                'content-type': 'application/json',
                            }

                            url = f"{self.BASE_URL}/jobs/{country}/search/1"
                            async with session.get(url, params=params, timeout=10) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    results = data.get('results', [])

                                    for job in results:
                                        job_data = self._extract_job_data(job, country, category)
                                        all_jobs.append(job_data)

                                    # Store category stats
                                    category_stats[f"{country}_{category}"] = {
                                        'count': data.get('count', 0),
                                        'mean_salary': data.get('mean', 0),
                                    }

                            await asyncio.sleep(0.5)  # Respect rate limits

                        except asyncio.TimeoutError:
                            self.logger.warning(f"Timeout fetching {country}/{category}")
                        except Exception as e:
                            self.logger.warning(f"Error fetching {country}/{category}: {e}")

                # Fetch salary histogram for top skills
                for skill in ['python', 'javascript', 'design']:
                    try:
                        params = {
                            'app_id': self.app_id,
                            'app_key': self.app_key,
                            'what': skill,
                        }
                        url = f"{self.BASE_URL}/jobs/us/histogram"
                        async with session.get(url, params=params, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                salary_data[skill] = data.get('histogram', {})
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        self.logger.warning(f"Error fetching salary for {skill}: {e}")

            return {
                'jobs': all_jobs,
                'salary_data': salary_data,
                'category_stats': category_stats,
                'source': 'adzuna'
            }

        except Exception as e:
            self.logger.error(f"Error fetching Adzuna data: {e}")
            return self._get_fallback_data()

    def _get_fallback_data(self) -> Dict[str, Any]:
        """Provide fallback data when API is not available"""
        return {
            'jobs': [],
            'salary_data': {},
            'category_stats': {},
            'source': 'adzuna_fallback',
            'note': 'API credentials not configured - using empty fallback'
        }

    def _extract_job_data(self, job: Dict[str, Any], country: str, category: str) -> Dict[str, Any]:
        """Extract relevant data from job listing"""
        title = job.get('title', '')
        description = job.get('description', '')
        text = f"{title} {description}".lower()

        return {
            'id': job.get('id', ''),
            'title': title,
            'description': description[:500] if description else '',
            'company': job.get('company', {}).get('display_name', ''),
            'location': job.get('location', {}).get('display_name', ''),
            'country': country,
            'category': category,
            'salary_min': job.get('salary_min', 0),
            'salary_max': job.get('salary_max', 0),
            'salary_is_predicted': job.get('salary_is_predicted', ''),
            'contract_type': job.get('contract_type', ''),
            'contract_time': job.get('contract_time', ''),
            'redirect_url': job.get('redirect_url', ''),
            'created': job.get('created', ''),
            'is_remote': any(kw in text for kw in self.REMOTE_KEYWORDS),
            'is_freelance': any(kw in text for kw in self.FREELANCE_KEYWORDS),
            'detected_skills': self._detect_skills(text),
        }

    def _detect_skills(self, text: str) -> List[str]:
        """Detect skills mentioned in job text"""
        detected = []
        for category, keywords in self.skill_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    detected.append(keyword)
        return list(set(detected))

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Adzuna job data into market intelligence"""
        try:
            jobs = raw_data.get('jobs', [])
            salary_data = raw_data.get('salary_data', {})
            category_stats = raw_data.get('category_stats', {})

            processed_jobs = []
            for job in jobs:
                processed = self._process_job(job)
                if processed:
                    processed_jobs.append(processed)

            insights = self._generate_insights(processed_jobs)
            skill_demand = self._analyze_skill_demand(processed_jobs)
            salary_insights = self._analyze_salaries(processed_jobs, salary_data)
            opportunity_score = self._calculate_opportunity_scores(processed_jobs)

            content = {
                'jobs': processed_jobs[:50],  # Limit stored jobs
                'insights': insights,
                'skill_demand': skill_demand,
                'salary_insights': salary_insights,
                'opportunity_scores': opportunity_score,
                'remote_opportunities': self._filter_remote_jobs(processed_jobs),
                'freelance_opportunities': self._filter_freelance_jobs(processed_jobs),
                'category_breakdown': category_stats,
                'high_paying_roles': self._get_high_paying_roles(processed_jobs),
            }

            quality_score = min(1.0, len(processed_jobs) / 40 + 0.4)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='adzuna.com',
                data_type='job_market',
                content=content,
                metadata={
                    'job_count': len(processed_jobs),
                    'source': raw_data.get('source', 'adzuna'),
                    'countries': list(set(j.get('country', '') for j in jobs)),
                    'categories': list(set(j.get('category', '') for j in jobs)),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['adzuna', 'jobs', 'salary', 'remote work', 'freelance', 'skills', 'hiring trends'],
                target_agents=['opportunity_scoring_agent', 'research_agent', 'content_strategy_agent'],
                target_advisors=['career_advisor', 'income_strategist', 'freelance_consultant']
            )

        except Exception as e:
            self.logger.error(f"Error processing Adzuna data: {e}")
            return None

    def _process_job(self, job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual job listing"""
        try:
            # Calculate salary midpoint
            salary_min = job.get('salary_min', 0) or 0
            salary_max = job.get('salary_max', 0) or 0
            salary_mid = (salary_min + salary_max) / 2 if salary_min and salary_max else 0

            # Opportunity score based on multiple factors
            opportunity_score = 0

            # Remote work bonus
            if job.get('is_remote'):
                opportunity_score += 20

            # Salary bonus
            if salary_mid > 80000:
                opportunity_score += 30
            elif salary_mid > 50000:
                opportunity_score += 20
            elif salary_mid > 30000:
                opportunity_score += 10

            # Skills bonus (more skills = more specialized = better opportunity)
            skills = job.get('detected_skills', [])
            opportunity_score += min(30, len(skills) * 5)

            # Freelance flexibility bonus
            if job.get('is_freelance'):
                opportunity_score += 15

            return {
                'id': job.get('id'),
                'title': job.get('title'),
                'company': job.get('company'),
                'location': job.get('location'),
                'country': job.get('country'),
                'category': job.get('category'),
                'salary_min': salary_min,
                'salary_max': salary_max,
                'salary_mid': salary_mid,
                'is_remote': job.get('is_remote'),
                'is_freelance': job.get('is_freelance'),
                'skills': skills,
                'opportunity_score': min(100, opportunity_score),
                'url': job.get('redirect_url'),
                'created': job.get('created'),
            }

        except Exception as e:
            self.logger.warning(f"Error processing job: {e}")
            return None

    def _generate_insights(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate job market insights"""
        if not jobs:
            return {}

        # Remote vs on-site
        remote_jobs = [j for j in jobs if j.get('is_remote')]
        freelance_jobs = [j for j in jobs if j.get('is_freelance')]

        # Country distribution
        countries = Counter(j.get('country', 'unknown') for j in jobs)

        # Category distribution
        categories = Counter(j.get('category', 'other') for j in jobs)

        # Average salary
        salaries = [j.get('salary_mid', 0) for j in jobs if j.get('salary_mid', 0) > 0]
        avg_salary = sum(salaries) / len(salaries) if salaries else 0

        # Average opportunity score
        scores = [j.get('opportunity_score', 0) for j in jobs]
        avg_score = sum(scores) / len(scores) if scores else 0

        return {
            'total_jobs': len(jobs),
            'remote_percentage': round(len(remote_jobs) / len(jobs) * 100, 1) if jobs else 0,
            'freelance_percentage': round(len(freelance_jobs) / len(jobs) * 100, 1) if jobs else 0,
            'country_distribution': dict(countries.most_common(5)),
            'category_distribution': dict(categories.most_common(5)),
            'average_salary': round(avg_salary, 2),
            'average_opportunity_score': round(avg_score, 1),
            'market_health': 'strong' if len(jobs) > 30 else 'moderate' if len(jobs) > 15 else 'limited',
        }

    def _analyze_skill_demand(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze which skills are most in demand"""
        all_skills = []
        for job in jobs:
            all_skills.extend(job.get('skills', []))

        skill_counts = Counter(all_skills)

        # Group by category
        category_demand = {}
        for category, keywords in self.skill_keywords.items():
            category_count = sum(skill_counts.get(kw, 0) for kw in keywords)
            category_demand[category] = category_count

        return {
            'top_skills': skill_counts.most_common(10),
            'category_demand': dict(sorted(category_demand.items(), key=lambda x: x[1], reverse=True)),
            'emerging_skills': [s for s, c in skill_counts.items() if c >= 2][:5],
            'skill_diversity': len(skill_counts),
        }

    def _analyze_salaries(self, jobs: List[Dict[str, Any]], salary_data: Dict) -> Dict[str, Any]:
        """Analyze salary trends"""
        jobs_with_salary = [j for j in jobs if j.get('salary_mid', 0) > 0]

        if not jobs_with_salary:
            return {'note': 'Insufficient salary data'}

        salaries = [j.get('salary_mid', 0) for j in jobs_with_salary]

        # Salary by remote status
        remote_salaries = [j.get('salary_mid', 0) for j in jobs_with_salary if j.get('is_remote')]
        onsite_salaries = [j.get('salary_mid', 0) for j in jobs_with_salary if not j.get('is_remote')]

        return {
            'min': min(salaries),
            'max': max(salaries),
            'average': round(sum(salaries) / len(salaries), 2),
            'median': sorted(salaries)[len(salaries) // 2],
            'remote_average': round(sum(remote_salaries) / len(remote_salaries), 2) if remote_salaries else 0,
            'onsite_average': round(sum(onsite_salaries) / len(onsite_salaries), 2) if onsite_salaries else 0,
            'sample_size': len(jobs_with_salary),
            'skill_premiums': salary_data,
        }

    def _calculate_opportunity_scores(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate and summarize opportunity scores"""
        scores = [j.get('opportunity_score', 0) for j in jobs]

        if not scores:
            return {}

        high_opportunity = [j for j in jobs if j.get('opportunity_score', 0) >= 70]
        medium_opportunity = [j for j in jobs if 40 <= j.get('opportunity_score', 0) < 70]

        return {
            'average_score': round(sum(scores) / len(scores), 1),
            'max_score': max(scores),
            'high_opportunity_count': len(high_opportunity),
            'medium_opportunity_count': len(medium_opportunity),
            'top_opportunities': sorted(jobs, key=lambda x: x.get('opportunity_score', 0), reverse=True)[:5],
        }

    def _filter_remote_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and return remote job opportunities"""
        remote = [j for j in jobs if j.get('is_remote')]
        return sorted(remote, key=lambda x: x.get('opportunity_score', 0), reverse=True)[:10]

    def _filter_freelance_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and return freelance opportunities"""
        freelance = [j for j in jobs if j.get('is_freelance')]
        return sorted(freelance, key=lambda x: x.get('opportunity_score', 0), reverse=True)[:10]

    def _get_high_paying_roles(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get highest paying roles"""
        with_salary = [j for j in jobs if j.get('salary_mid', 0) > 0]
        sorted_jobs = sorted(with_salary, key=lambda x: x.get('salary_mid', 0), reverse=True)
        return [
            {
                'title': j.get('title'),
                'company': j.get('company'),
                'salary_mid': j.get('salary_mid'),
                'is_remote': j.get('is_remote'),
                'skills': j.get('skills'),
            }
            for j in sorted_jobs[:10]
        ]

    def get_required_fields(self) -> List[str]:
        return ['id', 'title']

    def get_relevance_keywords(self) -> List[str]:
        return ['adzuna', 'jobs', 'hiring', 'salary', 'remote', 'freelance', 'career', 'employment']
