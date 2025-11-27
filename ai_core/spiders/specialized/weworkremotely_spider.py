"""
WeWorkRemotely Spider - Remote Job Intelligence
================================================

Session 218: Specialized spider for WeWorkRemotely job board.
Focuses on remote job opportunities across tech, design, and business.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class WeWorkRemotelySpider(BaseIntelligenceSpider):
    """WeWorkRemotely spider - remote job opportunities"""

    # RSS Feed URLs
    RSS_FEEDS = {
        'programming': 'https://weworkremotely.com/categories/remote-programming-jobs.rss',
        'design': 'https://weworkremotely.com/categories/remote-design-jobs.rss',
        'devops': 'https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss',
        'management': 'https://weworkremotely.com/categories/remote-management-finance-jobs.rss',
        'customer_support': 'https://weworkremotely.com/categories/remote-customer-support-jobs.rss',
        'sales_marketing': 'https://weworkremotely.com/categories/remote-sales-marketing-jobs.rss',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.job_categories = {
            'programming': ['developer', 'engineer', 'programmer', 'software', 'backend', 'frontend', 'fullstack'],
            'design': ['designer', 'ui', 'ux', 'graphic', 'product design', 'visual'],
            'devops': ['devops', 'sysadmin', 'infrastructure', 'cloud', 'aws', 'kubernetes'],
            'data': ['data', 'analyst', 'scientist', 'machine learning', 'ai', 'analytics'],
            'management': ['manager', 'lead', 'director', 'head of', 'vp', 'chief'],
            'marketing': ['marketing', 'growth', 'seo', 'content', 'social media'],
        }

        self.seniority_levels = {
            'senior': ['senior', 'sr.', 'lead', 'principal', 'staff'],
            'mid': ['mid-level', 'intermediate', '3+ years', '5+ years'],
            'junior': ['junior', 'jr.', 'entry', 'associate', 'trainee'],
        }

        self.tech_stacks = {
            'python': ['python', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'react', 'vue', 'angular', 'node', 'typescript'],
            'ruby': ['ruby', 'rails', 'ruby on rails'],
            'java': ['java', 'spring', 'kotlin'],
            'go': ['golang', 'go '],
            'rust': ['rust'],
            'mobile': ['ios', 'android', 'swift', 'react native', 'flutter'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from WeWorkRemotely"""
        try:
            all_jobs = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:15]:
                            job = {
                                'title': entry.get('title', ''),
                                'description': entry.get('summary', entry.get('description', ''))[:500],
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'company': self._extract_company(entry),
                                'feed_category': feed_name,
                            }
                            if job['title']:
                                all_jobs.append(job)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'jobs': all_jobs, 'source': 'weworkremotely'}

        except Exception as e:
            self.logger.error(f"Error fetching WeWorkRemotely data: {e}")
            return None

    def _extract_company(self, entry) -> str:
        """Extract company name from entry"""
        title = entry.get('title', '')
        if ':' in title:
            return title.split(':')[0].strip()
        return 'Remote Company'

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process WeWorkRemotely jobs"""
        try:
            jobs = raw_data.get('jobs', [])
            processed_jobs = []

            for job in jobs:
                processed = self._process_job(job)
                if processed:
                    processed_jobs.append(processed)

            insights = self._generate_job_insights(processed_jobs)

            content = {
                'jobs': processed_jobs,
                'insights': insights,
                'by_category': self._group_by_category(processed_jobs),
                'by_seniority': self._group_by_seniority(processed_jobs),
                'tech_demand': self._analyze_tech_demand(processed_jobs),
                'top_companies': self._extract_top_companies(processed_jobs),
            }

            quality_score = min(1.0, len(processed_jobs) / 40 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='weworkremotely.com',
                data_type='remote_jobs',
                content=content,
                metadata={
                    'job_count': len(processed_jobs),
                    'source': 'weworkremotely',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['remote', 'jobs', 'programming', 'design', 'tech'],
                target_agents=['job_agent', 'career_agent', 'income_agent'],
                target_advisors=['career_advisor', 'income_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing WeWorkRemotely data: {e}")
            return None

    def _process_job(self, job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual job listing"""
        try:
            title = job.get('title', '')
            description = job.get('description', '')
            text = f"{title} {description}".lower()

            # Identify job category
            category = job.get('feed_category', 'general')
            for cat, keywords in self.job_categories.items():
                if any(kw in text for kw in keywords):
                    category = cat
                    break

            # Identify seniority level
            seniority = 'mid'
            for level, keywords in self.seniority_levels.items():
                if any(kw in text for kw in keywords):
                    seniority = level
                    break

            # Identify tech stack
            tech_stack = []
            for tech, keywords in self.tech_stacks.items():
                if any(kw in text for kw in keywords):
                    tech_stack.append(tech)

            return {
                'title': title,
                'company': job.get('company', ''),
                'description': description[:300],
                'link': job.get('link', ''),
                'published': job.get('published', ''),
                'category': category,
                'seniority': seniority,
                'tech_stack': tech_stack,
                'is_fully_remote': True,
            }

        except Exception as e:
            self.logger.warning(f"Error processing job: {e}")
            return None

    def _generate_job_insights(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate job market insights"""
        if not jobs:
            return {}

        cat_counts = {}
        for job in jobs:
            cat = job.get('category', 'general')
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        seniority_counts = {}
        for job in jobs:
            level = job.get('seniority', 'mid')
            seniority_counts[level] = seniority_counts.get(level, 0) + 1

        return {
            'total_jobs': len(jobs),
            'hot_categories': sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'seniority_distribution': seniority_counts,
            'market_health': 'strong' if len(jobs) > 30 else 'moderate' if len(jobs) > 15 else 'quiet',
        }

    def _group_by_category(self, jobs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group jobs by category"""
        groups = {}
        for job in jobs:
            cat = job.get('category', 'general')
            if cat not in groups:
                groups[cat] = []
            groups[cat].append({'title': job.get('title'), 'company': job.get('company'), 'link': job.get('link')})
        return groups

    def _group_by_seniority(self, jobs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count jobs by seniority level"""
        counts = {}
        for job in jobs:
            level = job.get('seniority', 'mid')
            counts[level] = counts.get(level, 0) + 1
        return counts

    def _analyze_tech_demand(self, jobs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze tech stack demand"""
        tech_counts = {}
        for job in jobs:
            for tech in job.get('tech_stack', []):
                tech_counts[tech] = tech_counts.get(tech, 0) + 1
        return dict(sorted(tech_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_top_companies(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract companies with most listings"""
        company_counts = {}
        for job in jobs:
            company = job.get('company', 'Unknown')
            if company not in company_counts:
                company_counts[company] = {'count': 0, 'jobs': []}
            company_counts[company]['count'] += 1
            if len(company_counts[company]['jobs']) < 2:
                company_counts[company]['jobs'].append(job.get('title'))

        sorted_companies = sorted(company_counts.items(), key=lambda x: x[1]['count'], reverse=True)
        return [{'name': c[0], **c[1]} for c in sorted_companies[:5]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['remote', 'job', 'developer', 'designer', 'engineer', 'work from home']
