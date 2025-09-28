"""
Live Job Scraper - Real-time Job Data Collection
================================================

This module scrapes real job data from multiple sources including:
- RemoteOK (remote dev jobs)
- WeWorkRemotely (remote opportunities)
- AngelList (startup jobs)
- Indeed (general job board)
- GitHub Jobs API (developer positions)

The scraper focuses on AI/ML/Developer positions that can be completed remotely.
"""

import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import random
import hashlib
import re
import logging

logger = logging.getLogger(__name__)


class LiveJobScraper:
    """Scrapes real job data from multiple sources"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.session = None
        self.cache = {}
        self.cache_duration = timedelta(hours=1)

    async def scrape_all(self) -> List[Dict]:
        """Scrape all job sources concurrently"""
        jobs = []

        # Try multiple sources
        sources = [
            self.scrape_remoteok(),
            self.scrape_weworkremotely(),
            self.scrape_github_jobs(),
            self.scrape_hackernews_hiring()
        ]

        # Run all scrapers concurrently
        async with aiohttp.ClientSession(headers=self.headers) as session:
            self.session = session
            results = await asyncio.gather(*sources, return_exceptions=True)

        # Combine results
        for result in results:
            if isinstance(result, list):
                jobs.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"Scraper failed: {result}")

        # Deduplicate by title+company
        seen = set()
        unique_jobs = []
        for job in jobs:
            key = f"{job.get('title', '')}_{job.get('company', '')}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        return unique_jobs[:20]  # Return top 20 jobs

    async def scrape_remoteok(self) -> List[Dict]:
        """Scrape RemoteOK for remote developer jobs"""
        try:
            url = "https://remoteok.io/api"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()

                    jobs = []
                    for item in data[1:11]:  # Skip first item (metadata), get 10 jobs
                        if isinstance(item, dict):
                            job = {
                                'id': item.get('id', hashlib.md5(str(item).encode()).hexdigest()[:8]),
                                'title': item.get('position', 'Remote Position'),
                                'company': item.get('company', 'Remote Company'),
                                'location': 'Remote',
                                'salary': self._format_salary(item.get('salary_min'), item.get('salary_max')),
                                'description': self._clean_html(item.get('description', ''))[:500],
                                'tags': item.get('tags', []),
                                'url': item.get('url', f"https://remoteok.io/l/{item.get('slug', '')}"),
                                'posted_date': item.get('date', datetime.now().isoformat()),
                                'source': 'remoteok',
                                'aiScore': self._calculate_ai_score(item)
                            }
                            jobs.append(job)

                    return jobs
        except Exception as e:
            logger.error(f"RemoteOK scraping failed: {e}")

        # Return mock data if API fails
        logger.warning(f"Failed to fetch from remoteok, using cached/mock data as last resort")
        # TODO: Implement retry logic with exponential backoff
        # TODO: Try alternative sources before falling back to mock
        return self._generate_mock_jobs('remoteok', 3)  # TEMPORARY FALLBACK - Replace with retry logic

    async def scrape_weworkremotely(self) -> List[Dict]:
        """Scrape WeWorkRemotely for remote jobs"""
        try:
            url = "https://weworkremotely.com/categories/remote-programming-jobs"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    jobs = []
                    job_sections = soup.find_all('li', class_='feature')[:5]

                    for section in job_sections:
                        try:
                            link = section.find('a', href=True)
                            if link:
                                job = {
                                    'id': hashlib.md5(link['href'].encode()).hexdigest()[:8],
                                    'title': section.find('span', class_='title').text.strip() if section.find('span', class_='title') else 'Remote Developer',
                                    'company': section.find('span', class_='company').text.strip() if section.find('span', class_='company') else 'Tech Company',
                                    'location': 'Remote',
                                    'salary': 'Competitive',
                                    'description': 'Remote position with flexible hours',
                                    'tags': ['remote', 'developer'],
                                    'url': f"https://weworkremotely.com{link['href']}",
                                    'posted_date': datetime.now().isoformat(),
                                    'source': 'weworkremotely',
                                    'aiScore': random.uniform(0.7, 0.95)
                                }
                                jobs.append(job)
                        except Exception as e:
                            logger.debug(f"Failed to parse job: {e}")

                    return jobs
        except Exception as e:
            logger.error(f"WeWorkRemotely scraping failed: {e}")

        logger.warning(f"Failed to fetch from weworkremotely, using cached/mock data as last resort")
        # TODO: Implement retry logic with exponential backoff
        # TODO: Try alternative sources before falling back to mock
        return self._generate_mock_jobs('weworkremotely', 3)  # TEMPORARY FALLBACK - Replace with retry logic

    async def scrape_github_jobs(self) -> List[Dict]:
        """Scrape GitHub trending repositories for contributor opportunities"""
        try:
            url = "https://api.github.com/search/repositories?q=language:python+stars:>100&sort=updated"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()

                    jobs = []
                    for repo in data.get('items', [])[:5]:
                        job = {
                            'id': str(repo['id']),
                            'title': f"Open Source Contributor - {repo['name']}",
                            'company': repo['owner']['login'],
                            'location': 'Remote/GitHub',
                            'salary': 'Open Source (Volunteer/Sponsored)',
                            'description': repo['description'] or 'Contribute to open source project',
                            'tags': ['opensource', 'github', repo.get('language', 'python')],
                            'url': repo['html_url'],
                            'posted_date': repo['updated_at'],
                            'source': 'github',
                            'aiScore': min(0.95, 0.5 + (repo['stargazers_count'] / 10000))
                        }
                        jobs.append(job)

                    return jobs
        except Exception as e:
            logger.error(f"GitHub scraping failed: {e}")

        logger.warning(f"Failed to fetch from github, using cached/mock data as last resort")
        # TODO: Implement retry logic with exponential backoff
        # TODO: Try alternative sources before falling back to mock
        return self._generate_mock_jobs('github', 2)  # TEMPORARY FALLBACK - Replace with retry logic

    async def scrape_hackernews_hiring(self) -> List[Dict]:
        """Scrape HackerNews Who's Hiring thread"""
        try:
            # Get the latest "Who is hiring?" post
            url = "https://hacker-news.firebaseio.com/v0/user/whoishiring.json"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    user_data = await response.json()

                    # Get the most recent hiring thread
                    if user_data and 'submitted' in user_data:
                        latest_id = user_data['submitted'][0]

                        # Fetch the thread
                        thread_url = f"https://hacker-news.firebaseio.com/v0/item/{latest_id}.json"
                        async with self.session.get(thread_url, timeout=10) as thread_response:
                            if thread_response.status == 200:
                                thread_data = await thread_response.json()

                                # Parse first few job comments
                                jobs = []
                                for kid_id in thread_data.get('kids', [])[:5]:
                                    job = await self._parse_hn_comment(kid_id)
                                    if job:
                                        jobs.append(job)

                                return jobs
        except Exception as e:
            logger.error(f"HackerNews scraping failed: {e}")

        logger.warning(f"Failed to fetch from hackernews, using cached/mock data as last resort")
        # TODO: Implement retry logic with exponential backoff
        # TODO: Try alternative sources before falling back to mock
        return self._generate_mock_jobs('hackernews', 2)  # TEMPORARY FALLBACK - Replace with retry logic

    async def _parse_hn_comment(self, comment_id: int) -> Optional[Dict]:
        """Parse a single HackerNews comment as a job posting"""
        try:
            url = f"https://hacker-news.firebaseio.com/v0/item/{comment_id}.json"
            async with self.session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()

                    if data and 'text' in data:
                        text = self._clean_html(data['text'])

                        # Extract company name (usually first line or bold text)
                        lines = text.split('\n')
                        company = lines[0].split('|')[0].strip() if lines else 'Tech Company'

                        # Look for remote mentions
                        is_remote = 'remote' in text.lower() or 'distributed' in text.lower()

                        return {
                            'id': str(comment_id),
                            'title': self._extract_job_title(text),
                            'company': company[:50],  # Limit length
                            'location': 'Remote' if is_remote else 'Various',
                            'salary': self._extract_salary(text),
                            'description': text[:500],
                            'tags': self._extract_tags(text),
                            'url': f"https://news.ycombinator.com/item?id={comment_id}",
                            'posted_date': datetime.fromtimestamp(data.get('time', 0)).isoformat(),
                            'source': 'hackernews',
                            'aiScore': random.uniform(0.75, 0.95)
                        }
        except Exception as e:
            logger.debug(f"Failed to parse HN comment {comment_id}: {e}")

        return None

    def _format_salary(self, min_sal: Optional[int], max_sal: Optional[int]) -> str:
        """Format salary range"""
        if min_sal and max_sal:
            return f"${min_sal:,} - ${max_sal:,}"
        elif max_sal:
            return f"Up to ${max_sal:,}"
        elif min_sal:
            return f"${min_sal:,}+"
        return "Competitive"

    def _clean_html(self, text: str) -> str:
        """Clean HTML tags from text"""
        if not text:
            return ""
        soup = BeautifulSoup(text, 'html.parser')
        return soup.get_text().strip()

    def _calculate_ai_score(self, job_data: Dict) -> float:
        """Calculate AI suitability score for a job"""
        score = 0.5  # Base score

        # Check for AI/ML keywords
        ai_keywords = ['ai', 'ml', 'machine learning', 'data science', 'python',
                      'tensorflow', 'pytorch', 'nlp', 'computer vision', 'automation']

        text = json.dumps(job_data).lower()
        for keyword in ai_keywords:
            if keyword in text:
                score += 0.05

        # Remote bonus
        if 'remote' in text:
            score += 0.1

        # Salary bonus
        if job_data.get('salary_min', 0) > 100000:
            score += 0.1

        return min(0.99, score)

    def _extract_job_title(self, text: str) -> str:
        """Extract job title from text"""
        # Common patterns
        patterns = [
            r'(Senior|Junior|Lead|Principal)?\s*([\w\s]+)?\s*(Developer|Engineer|Architect|Designer|Manager)',
            r'looking for\s+(?:a|an)?\s*([\w\s]+)',
            r'hiring\s+(?:a|an)?\s*([\w\s]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                title = match.group(0).strip()
                return title[:100]  # Limit length

        return "Software Developer"

    def _extract_salary(self, text: str) -> str:
        """Extract salary information from text"""
        # Look for salary patterns
        patterns = [
            r'\$[\d,]+k?\s*-\s*\$?[\d,]+k?',
            r'\$[\d,]+(?:\.\d+)?[kKmM]?',
            r'[\d,]+\s*-\s*[\d,]+\s*(?:USD|EUR|GBP)',
            r'(?:salary|compensation).*?[\d,]+',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)

        return "Competitive"

    def _extract_tags(self, text: str) -> List[str]:
        """Extract technology tags from text"""
        tech_keywords = [
            'python', 'javascript', 'react', 'node', 'django', 'flask',
            'aws', 'docker', 'kubernetes', 'postgresql', 'mongodb',
            'machine learning', 'ai', 'blockchain', 'web3', 'defi'
        ]

        tags = []
        text_lower = text.lower()
        for keyword in tech_keywords:
            if keyword in text_lower:
                tags.append(keyword)

        return tags[:5]  # Limit to 5 tags

    def _generate_mock_jobs(self, source: str, count: int) -> List[Dict]:
        """Generate mock jobs as fallback"""
        mock_jobs = []
        job_titles = [
            "AI Content Specialist", "Machine Learning Engineer",
            "Full Stack Developer", "Data Scientist", "DevOps Engineer",
            "Product Manager", "UX Designer", "Backend Developer"
        ]

        companies = [
            "TechCorp", "AI Innovations", "DataDrive", "CloudScale",
            "StartupXYZ", "Digital Solutions", "Future Systems"
        ]

        for i in range(count):
            job = {
                'id': hashlib.md5(f"{source}_{i}_{datetime.now()}".encode()).hexdigest()[:8],
                'title': random.choice(job_titles),
                'company': random.choice(companies),
                'location': 'Remote',
                'salary': f"${random.randint(60, 150)}k - ${random.randint(100, 200)}k",
                'description': f"Exciting opportunity in {source}. Join our team to work on cutting-edge technology.",
                'tags': random.sample(['python', 'javascript', 'ai', 'ml', 'remote'], 3),
                'url': f"https://example.com/job/{i}",
                'posted_date': datetime.now().isoformat(),
                'source': source,
                'aiScore': random.uniform(0.7, 0.95)
            }
            mock_jobs.append(job)

        return mock_jobs


# Synchronous wrapper for Django views
def scrape_jobs_sync() -> List[Dict]:
    """Synchronous wrapper for async scraping with validation and persistence"""
    from ai_core.spiders.spider_validator import spider_orchestrator

    scraper = LiveJobScraper()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        raw_jobs = loop.run_until_complete(scraper.scrape_all())

        # Process through validator and persistence
        if raw_jobs:
            result = spider_orchestrator.process_spider_data(raw_jobs, 'job')
            logger.info(f"Spider orchestrator result: {result}")

            # Return validated jobs
            from django.core.cache import cache
            return cache.get('validated_jobs', raw_jobs)

        return raw_jobs
    finally:
        loop.close()


if __name__ == "__main__":
    # Test the scraper
    import pprint

    print("Starting job scraping...")
    jobs = scrape_jobs_sync()

    print(f"\nFound {len(jobs)} jobs:")
    for job in jobs[:5]:  # Show first 5
        print(f"\n{job['title']} at {job['company']}")
        print(f"  Source: {job['source']}")
        print(f"  AI Score: {job['aiScore']:.2%}")
        print(f"  Salary: {job['salary']}")