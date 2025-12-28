"""
Real Job Spider - Actually searches for real freelance opportunities
Phase 1: Real data collection implementation
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_request_layer import web_request_layer

logger = logging.getLogger(__name__)


class RealJobSpider:
    """
    Spider that searches REAL job boards and freelance platforms
    for actual opportunities you can apply to
    """

    def __init__(self):
        self.opportunities = []
        self.web_layer = web_request_layer

        # Real job search APIs and sources
        self.sources = {
            'remoteok': {
                'url': 'https://remoteok.io/api',
                'params': {},
                'requires_auth': False
            },
            'remotive': {
                'url': 'https://remotive.com/api/remote-jobs',
                'params': {'category': 'software-dev', 'limit': 20},
                'requires_auth': False
            },
            'github_jobs': {
                'url': 'https://jobs.github.com/positions.json',
                'params': {'description': 'python', 'location': 'remote'},
                'requires_auth': False
            },
            'indeed': {
                'url': 'https://www.indeed.com/jobs',
                'params': {'q': 'python developer remote', 'l': 'Remote'},
                'requires_auth': False,
                'scraping_required': True
            },
            'upwork': {
                'url': 'https://www.upwork.com/freelance-jobs/api',
                'params': {},
                'requires_auth': True,
                'scraping_required': True
            },
            'freelancer': {
                'url': 'https://www.freelancer.com/api/projects',
                'params': {'limit': 20},
                'requires_auth': False
            }
        }

    async def initialize(self):
        """Initialize the spider and its resources"""
        # Initialize web layer if needed
        await self.web_layer.initialize()
        logger.info("✅ RealJobSpider initialized")
        return self

    async def search_real_jobs(self, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for REAL job opportunities based on keywords

        Args:
            keywords: List of keywords to search for

        Returns:
            List of real job opportunities
        """
        await self.web_layer.initialize()

        if not keywords:
            keywords = ['python', 'ai', 'machine learning', 'content writing', 'freelance', 'remote']

        all_opportunities = []

        # 1. Search RemoteOK (no API key needed, returns JSON)
        logger.info("🕷️ Searching RemoteOK for real jobs...")
        remoteok_opportunities = await self._search_remoteok(keywords)
        all_opportunities.extend(remoteok_opportunities)

        # 2. Search Remotive (public API)
        logger.info("🕷️ Searching Remotive for real jobs...")
        remotive_opportunities = await self._search_remotive(keywords)
        all_opportunities.extend(remotive_opportunities)

        # 3. Search WeWorkRemotely (RSS feed)
        logger.info("🕷️ Searching WeWorkRemotely...")
        wwr_opportunities = await self._search_weworkremotely(keywords)
        all_opportunities.extend(wwr_opportunities)

        # 4. Search Stack Overflow Jobs (RSS feed)
        logger.info("🕷️ Searching Stack Overflow Jobs...")
        so_opportunities = await self._search_stackoverflow_jobs(keywords)
        all_opportunities.extend(so_opportunities)

        # 5. Search DEV.to Listings (public API)
        logger.info("🕷️ Searching DEV.to job listings...")
        devto_opportunities = await self._search_dev_to_listings(keywords)
        all_opportunities.extend(devto_opportunities)

        # 6. Search HackerNews Who's Hiring
        logger.info("🕷️ Searching HackerNews Who's Hiring...")
        hn_opportunities = await self._search_hackernews_jobs()
        all_opportunities.extend(hn_opportunities)

        # 7. Search Wellfound (formerly AngelList) startup jobs
        logger.info("🕷️ Searching Wellfound for startup jobs...")
        wellfound_opportunities = await self._search_wellfound_startup_jobs(keywords)
        all_opportunities.extend(wellfound_opportunities)

        # 8. Search CryptoJobsList (free tier)
        logger.info("🕷️ Searching CryptoJobsList...")
        crypto_opportunities = await self._search_crypto_jobs(keywords)
        all_opportunities.extend(crypto_opportunities)

        # 9. Search USAJobs (government jobs)
        logger.info("🕷️ Searching USAJobs.gov...")
        usa_opportunities = await self._search_usajobs(keywords)
        all_opportunities.extend(usa_opportunities)

        # 10. Aggregate RSS feeds from multiple sources
        logger.info("🕷️ Aggregating RSS feeds...")
        rss_opportunities = await self._aggregate_rss_feeds(keywords)
        all_opportunities.extend(rss_opportunities)

        # Log summary
        logger.info(f"✅ Total real opportunities found: {len(all_opportunities)}")
        sources = ['RemoteOK', 'Remotive', 'WeWorkRemotely', 'StackOverflow', 'DEV.to',
                   'HackerNews', 'Wellfound', 'CryptoJobs', 'USAJobs', 'RSS Feeds']
        for source in sources:
            count = len([o for o in all_opportunities if o['source'] == source])
            if count > 0:
                logger.info(f"  - {source}: {count} opportunities")

        return all_opportunities

    async def _search_remoteok(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search RemoteOK for real jobs"""
        opportunities = []
        try:
            response = await self.web_layer.fetch('https://remoteok.io/api')

            if response['status'] == 200 and response['json']:
                # RemoteOK returns array, first item is metadata
                jobs = response['json'][1:21] if len(response['json']) > 1 else []

                for job in jobs:
                    if isinstance(job, dict):
                        # Filter by keywords
                        job_text = f"{job.get('position', '')} {job.get('tags', [])} {job.get('description', '')}".lower()
                        if any(keyword.lower() in job_text for keyword in keywords):
                            opportunity = {
                                'source': 'RemoteOK',
                                'title': job.get('position', 'Unknown Position'),
                                'company': job.get('company', 'Unknown Company'),
                                'salary_min': job.get('salary_min', 0),
                                'salary_max': job.get('salary_max', 0),
                                'url': job.get('url', ''),
                                'description': job.get('description', '')[:500],
                                'tags': job.get('tags', []),
                                'date_posted': job.get('date', ''),
                                'is_real': True,
                                'application_url': job.get('apply_url', job.get('url', '')),
                                'location': job.get('location', 'Remote'),
                                'found_at': datetime.now().isoformat(),
                                'match_score': self._calculate_match_score(job_text, keywords)
                            }
                            opportunities.append(opportunity)

                logger.info(f"✅ Found {len(opportunities)} real jobs from RemoteOK")
            else:
                logger.warning(f"RemoteOK API returned status {response['status']}")

        except Exception as e:
            logger.error(f"Error searching RemoteOK: {e}")

        return opportunities

    async def _search_remotive(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search Remotive for real jobs"""
        opportunities = []
        try:
            url = 'https://remotive.com/api/remote-jobs'
            params = {'category': 'software-dev', 'limit': 20}
            response = await self.web_layer.fetch(url, params=params)

            if response['status'] == 200 and response['json']:
                jobs = response['json'].get('jobs', [])

                for job in jobs[:20]:
                    job_text = f"{job.get('title', '')} {job.get('category', '')} {job.get('description', '')}".lower()
                    if any(keyword.lower() in job_text for keyword in keywords):
                        opportunity = {
                            'source': 'Remotive',
                            'title': job.get('title', 'Unknown Position'),
                            'company': job.get('company_name', 'Unknown Company'),
                            'salary': job.get('salary', 'Not specified'),
                            'url': job.get('url', ''),
                            'description': job.get('description', '')[:500],
                            'category': job.get('category', ''),
                            'date_posted': job.get('publication_date', ''),
                            'is_real': True,
                            'application_url': job.get('url', ''),
                            'location': job.get('candidate_required_location', 'Remote'),
                            'found_at': datetime.now().isoformat(),
                            'match_score': self._calculate_match_score(job_text, keywords)
                        }
                        opportunities.append(opportunity)

                logger.info(f"✅ Found {len(opportunities)} real jobs from Remotive")

        except Exception as e:
            logger.error(f"Error searching Remotive: {e}")

        return opportunities

    async def _search_github_jobs(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search GitHub Jobs (if still available)"""
        opportunities = []
        try:
            # Note: GitHub Jobs API was deprecated, but trying alternative endpoints
            url = 'https://jobs.github.com/positions.json'
            params = {'description': ' '.join(keywords[:3]), 'location': 'remote'}
            response = await self.web_layer.fetch(url, params=params)

            if response['status'] == 200 and response['json']:
                for job in response['json'][:10]:
                    opportunity = {
                        'source': 'GitHub',
                        'title': job.get('title', 'Unknown Position'),
                        'company': job.get('company', 'Unknown Company'),
                        'url': job.get('url', ''),
                        'description': job.get('description', '')[:500],
                        'type': job.get('type', ''),
                        'date_posted': job.get('created_at', ''),
                        'is_real': True,
                        'application_url': job.get('how_to_apply', ''),
                        'location': job.get('location', 'Remote'),
                        'found_at': datetime.now().isoformat()
                    }
                    opportunities.append(opportunity)

                logger.info(f"✅ Found {len(opportunities)} real jobs from GitHub Jobs")

        except Exception as e:
            logger.debug(f"GitHub Jobs API might be deprecated: {e}")

        return opportunities

    async def _search_hackernews_jobs(self) -> List[Dict[str, Any]]:
        """Search HackerNews Who's Hiring threads"""
        opportunities = []
        try:
            # Get latest "Who's Hiring" thread
            url = 'https://hacker-news.firebaseio.com/v0/user/whoishiring.json'
            response = await self.web_layer.fetch(url)

            if response['status'] == 200 and response['json']:
                # Get the submitted items (these are the monthly Who's Hiring posts)
                submitted = response['json'].get('submitted', [])[:3]  # Last 3 months

                for story_id in submitted[:1]:  # Just get the latest one to avoid rate limiting
                    story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
                    story_response = await self.web_layer.fetch(story_url)

                    if story_response['status'] == 200 and story_response['json']:
                        story = story_response['json']
                        if 'hiring' in story.get('title', '').lower():
                            # Get top comments (job postings)
                            kids = story.get('kids', [])[:10]  # Get first 10 job posts

                            for comment_id in kids:
                                comment_url = f'https://hacker-news.firebaseio.com/v0/item/{comment_id}.json'
                                comment_response = await self.web_layer.fetch(comment_url)

                                if comment_response['status'] == 200 and comment_response['json']:
                                    comment = comment_response['json']
                                    text = comment.get('text', '')

                                    # Parse job posting from comment text
                                    if text and len(text) > 100:
                                        opportunity = {
                                            'source': 'HackerNews',
                                            'title': self._extract_title_from_hn(text),
                                            'company': self._extract_company_from_hn(text),
                                            'description': text[:500],
                                            'date_posted': datetime.fromtimestamp(comment.get('time', 0)).isoformat(),
                                            'is_real': True,
                                            'url': f"https://news.ycombinator.com/item?id={comment_id}",
                                            'application_url': f"https://news.ycombinator.com/item?id={comment_id}",
                                            'location': 'See description',
                                            'found_at': datetime.now().isoformat()
                                        }
                                        opportunities.append(opportunity)

                logger.info(f"✅ Found {len(opportunities)} real jobs from HackerNews")

        except Exception as e:
            logger.error(f"Error searching HackerNews: {e}")

        return opportunities

    async def _search_weworkremotely(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search WeWorkRemotely RSS feed for jobs"""
        opportunities = []
        try:
            import xml.etree.ElementTree as ET

            url = 'https://weworkremotely.com/categories/remote-programming-jobs.rss'
            response = await self.web_layer.fetch(url)

            if response['status'] == 200 and response['text']:
                root = ET.fromstring(response['text'])

                for item in root.findall('.//item')[:20]:
                    title = item.find('title')
                    link = item.find('link')
                    description = item.find('description')
                    pub_date = item.find('pubDate')

                    if title is not None and link is not None:
                        job_text = f"{title.text} {description.text if description is not None else ''}".lower()
                        if any(keyword.lower() in job_text for keyword in keywords):
                            # Extract company from title (usually format: "Company: Position")
                            title_parts = title.text.split(':')
                            company = title_parts[0].strip() if len(title_parts) > 1 else 'Company'
                            position = title_parts[1].strip() if len(title_parts) > 1 else title.text

                            opportunity = {
                                'source': 'WeWorkRemotely',
                                'title': position,
                                'company': company,
                                'url': link.text,
                                'description': description.text[:500] if description is not None else '',
                                'date_posted': pub_date.text if pub_date is not None else '',
                                'is_real': True,
                                'application_url': link.text,
                                'location': 'Remote',
                                'found_at': datetime.now().isoformat(),
                                'match_score': self._calculate_match_score(job_text, keywords)
                            }
                            opportunities.append(opportunity)

                logger.info(f"✅ Found {len(opportunities)} real jobs from WeWorkRemotely")

        except Exception as e:
            logger.error(f"Error searching WeWorkRemotely: {e}")

        return opportunities

    async def _search_stackoverflow_jobs(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search Stack Overflow Jobs RSS feed"""
        opportunities = []
        try:
            import xml.etree.ElementTree as ET

            # Build search query
            query = '+'.join(keywords[:3])
            url = f'https://stackoverflow.com/jobs/feed?q={query}&r=true'  # r=true for remote
            response = await self.web_layer.fetch(url)

            if response['status'] == 200 and response['text']:
                root = ET.fromstring(response['text'])

                for item in root.findall('.//item')[:15]:
                    title = item.find('title')
                    link = item.find('link')
                    description = item.find('description')
                    pub_date = item.find('pubDate')

                    if title is not None and link is not None:
                        opportunity = {
                            'source': 'StackOverflow',
                            'title': title.text,
                            'company': self._extract_company_from_so(title.text),
                            'url': link.text,
                            'description': description.text[:500] if description is not None else '',
                            'date_posted': pub_date.text if pub_date is not None else '',
                            'is_real': True,
                            'application_url': link.text,
                            'location': 'Remote',
                            'found_at': datetime.now().isoformat(),
                            'match_score': self._calculate_match_score(title.text + (description.text or ''), keywords)
                        }
                        opportunities.append(opportunity)

                logger.info(f"✅ Found {len(opportunities)} real jobs from Stack Overflow")

        except Exception as e:
            logger.error(f"Error searching Stack Overflow Jobs: {e}")

        return opportunities

    async def _search_dev_to_listings(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search DEV.to job listings via public API"""
        opportunities = []
        try:
            url = 'https://dev.to/api/listings'
            params = {'category': 'jobs', 'per_page': 30}
            response = await self.web_layer.fetch(url, params=params)

            if response['status'] == 200 and response['json']:
                for listing in response['json'][:20]:
                    job_text = f"{listing.get('title', '')} {listing.get('body_markdown', '')}".lower()
                    if any(keyword.lower() in job_text for keyword in keywords):
                        opportunity = {
                            'source': 'DEV.to',
                            'title': listing.get('title', 'Unknown Position'),
                            'company': listing.get('organization', {}).get('name', 'Unknown Company'),
                            'url': f"https://dev.to{listing.get('path', '')}",
                            'description': listing.get('body_markdown', '')[:500],
                            'tags': listing.get('tags', []),
                            'date_posted': listing.get('published_at', ''),
                            'is_real': True,
                            'application_url': f"https://dev.to{listing.get('path', '')}",
                            'location': listing.get('location', 'Remote'),
                            'found_at': datetime.now().isoformat(),
                            'match_score': self._calculate_match_score(job_text, keywords)
                        }
                        opportunities.append(opportunity)

                logger.info(f"✅ Found {len(opportunities)} real jobs from DEV.to")

        except Exception as e:
            logger.error(f"Error searching DEV.to listings: {e}")

        return opportunities

    async def _search_wellfound_startup_jobs(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search Wellfound (formerly AngelList) for startup jobs"""
        opportunities = []
        try:
            # Wellfound has public job listings accessible without auth
            base_url = 'https://wellfound.com/api/public/jobs'

            # Try their public endpoint
            response = await self.web_layer.fetch(base_url)

            if response['status'] == 200 and response['json']:
                jobs = response['json'].get('jobs', [])

                for job in jobs[:15]:
                    job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
                    if any(keyword.lower() in job_text for keyword in keywords):
                        opportunity = {
                            'source': 'Wellfound',
                            'title': job.get('title', 'Unknown Position'),
                            'company': job.get('startup', {}).get('name', 'Startup'),
                            'salary_min': job.get('salary_min', 0),
                            'salary_max': job.get('salary_max', 0),
                            'equity_min': job.get('equity_min', 0),
                            'equity_max': job.get('equity_max', 0),
                            'url': job.get('url', ''),
                            'description': job.get('description', '')[:500],
                            'date_posted': job.get('created_at', ''),
                            'is_real': True,
                            'application_url': job.get('apply_url', ''),
                            'location': job.get('location', 'Remote'),
                            'found_at': datetime.now().isoformat(),
                            'match_score': self._calculate_match_score(job_text, keywords)
                        }
                        opportunities.append(opportunity)

                logger.info(f"✅ Found {len(opportunities)} real jobs from Wellfound")
            else:
                logger.debug("Wellfound API may require different approach")

        except Exception as e:
            logger.debug(f"Wellfound search needs alternative approach: {e}")

        return opportunities

    async def _search_crypto_jobs(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search CryptoJobsList for blockchain/crypto jobs"""
        opportunities = []
        try:
            url = 'https://cryptojobslist.com/api/jobs'
            response = await self.web_layer.fetch(url)

            if response['status'] == 200 and response['json']:
                jobs = response['json'].get('jobs', response['json']) if isinstance(response['json'], dict) else response['json']

                for job in jobs[:10] if isinstance(jobs, list) else []:
                    job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
                    # Include crypto jobs even if keywords don't match - they're specialized
                    opportunity = {
                        'source': 'CryptoJobs',
                        'title': job.get('title', 'Unknown Position'),
                        'company': job.get('company', 'Crypto Startup'),
                        'salary': job.get('salary', 'Competitive'),
                        'url': job.get('url', ''),
                        'description': job.get('description', '')[:500],
                        'tags': job.get('tags', ['blockchain', 'crypto']),
                        'date_posted': job.get('posted', ''),
                        'is_real': True,
                        'application_url': job.get('apply_url', job.get('url', '')),
                        'location': job.get('location', 'Remote'),
                        'found_at': datetime.now().isoformat(),
                        'match_score': self._calculate_match_score(job_text, keywords + ['crypto', 'blockchain'])
                    }
                    opportunities.append(opportunity)

                logger.info(f"✅ Found {len(opportunities)} real jobs from CryptoJobsList")

        except Exception as e:
            logger.debug(f"CryptoJobsList search: {e}")

        return opportunities

    async def _search_usajobs(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search USAJobs.gov for government positions"""
        opportunities = []
        try:
            # USAJobs has a public API
            base_url = 'https://data.usajobs.gov/api/search'
            headers = {
                'Host': 'data.usajobs.gov',
                'User-Agent': 'job-search-spider'
            }

            params = {
                'Keyword': ' '.join(keywords[:3]),
                'LocationName': '',
                'RemoteIndicator': 'true'
            }

            response = await self.web_layer.fetch(base_url, params=params, headers=headers)

            if response['status'] == 200 and response['json']:
                results = response['json'].get('SearchResult', {}).get('SearchResultItems', [])

                for item in results[:10]:
                    job = item.get('MatchedObjectDescriptor', {})
                    opportunity = {
                        'source': 'USAJobs',
                        'title': job.get('PositionTitle', 'Unknown Position'),
                        'company': job.get('OrganizationName', 'US Government'),
                        'salary_min': job.get('PositionRemuneration', [{}])[0].get('MinimumRange', 0),
                        'salary_max': job.get('PositionRemuneration', [{}])[0].get('MaximumRange', 0),
                        'url': job.get('PositionURI', ''),
                        'description': job.get('UserArea', {}).get('Details', {}).get('JobSummary', '')[:500],
                        'date_posted': job.get('PositionStartDate', ''),
                        'is_real': True,
                        'application_url': job.get('ApplyURI', [{}])[0].get('URL', '') if job.get('ApplyURI') else '',
                        'location': job.get('PositionLocationDisplay', 'Various'),
                        'found_at': datetime.now().isoformat(),
                        'match_score': self._calculate_match_score(job.get('PositionTitle', '') + job.get('JobSummary', ''), keywords)
                    }
                    opportunities.append(opportunity)

                logger.info(f"✅ Found {len(opportunities)} real jobs from USAJobs")

        except Exception as e:
            logger.debug(f"USAJobs search: {e}")

        return opportunities

    async def _aggregate_rss_feeds(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Aggregate jobs from multiple RSS feeds"""
        opportunities = []

        rss_feeds = [
            {'url': 'https://remoteok.io/remote-jobs.rss', 'source': 'RemoteOK-RSS'},
            {'url': 'https://nodesk.co/remote-work/index.xml', 'source': 'NoDesk'},
            {'url': 'https://remotejobs.com/rss', 'source': 'RemoteJobs'},
            {'url': 'https://jobspresso.co/feed/', 'source': 'Jobspresso'},
            {'url': 'https://remote.co/feed/', 'source': 'Remote.co'},
        ]

        try:
            import xml.etree.ElementTree as ET

            for feed in rss_feeds:
                try:
                    response = await self.web_layer.fetch(feed['url'])

                    if response['status'] == 200 and response['text']:
                        root = ET.fromstring(response['text'])

                        for item in root.findall('.//item')[:10]:  # Limit to 10 per feed
                            title = item.find('title')
                            link = item.find('link')
                            description = item.find('description')

                            if title is not None and link is not None:
                                job_text = f"{title.text} {description.text if description is not None else ''}".lower()
                                if any(keyword.lower() in job_text for keyword in keywords):
                                    opportunity = {
                                        'source': 'RSS Feeds',
                                        'feed_source': feed['source'],
                                        'title': title.text,
                                        'company': self._extract_company_from_rss(title.text),
                                        'url': link.text,
                                        'description': description.text[:500] if description is not None else '',
                                        'is_real': True,
                                        'application_url': link.text,
                                        'location': 'Remote',
                                        'found_at': datetime.now().isoformat(),
                                        'match_score': self._calculate_match_score(job_text, keywords)
                                    }
                                    opportunities.append(opportunity)

                except Exception as e:
                    logger.debug(f"Error fetching {feed['source']}: {e}")

            logger.info(f"✅ Found {len(opportunities)} jobs from RSS feeds")

        except Exception as e:
            logger.error(f"Error aggregating RSS feeds: {e}")

        return opportunities

    def _extract_company_from_so(self, title: str) -> str:
        """Extract company name from Stack Overflow job title"""
        # Usually format: "Position at Company (location)"
        import re
        match = re.search(r'at\s+([^(]+)', title)
        if match:
            return match.group(1).strip()
        return 'Company'

    def _extract_company_from_rss(self, title: str) -> str:
        """Extract company name from RSS feed job title"""
        # Common patterns: "Company - Position" or "Position at Company"
        import re

        # Try pattern 1: "Company - Position"
        if ' - ' in title:
            return title.split(' - ')[0].strip()

        # Try pattern 2: "Position at Company"
        match = re.search(r'at\s+([^(]+)', title)
        if match:
            return match.group(1).strip()

        # Try pattern 3: "Company: Position"
        if ':' in title:
            return title.split(':')[0].strip()

        return 'Company'

    async def _search_angellist(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search AngelList for startup jobs - Deprecated, use Wellfound instead"""
        # This method is kept for backward compatibility but redirects to Wellfound
        return await self._search_wellfound_startup_jobs(keywords)

    def _calculate_match_score(self, text: str, keywords: List[str]) -> float:
        """Calculate how well a job matches the keywords"""
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        return min(1.0, matches / len(keywords)) if keywords else 0.0

    def _extract_title_from_hn(self, text: str) -> str:
        """Extract job title from HackerNews posting"""
        # Usually the first line or contains keywords like "Engineer", "Developer"
        lines = text.split('\n')
        for line in lines[:3]:
            if any(word in line for word in ['Engineer', 'Developer', 'Designer', 'Manager', 'Lead']):
                return line.strip()[:100]
        return lines[0].strip()[:100] if lines else "Position at Startup"

    def _extract_company_from_hn(self, text: str) -> str:
        """Extract company name from HackerNews posting"""
        # Usually in the first line or after company indicators
        lines = text.split('\n')
        first_line = lines[0] if lines else ""

        # Common patterns: "Company (location)", "Company |", etc.
        import re
        company_match = re.search(r'^([A-Z][A-Za-z0-9\s]+)[\(\|\-]', first_line)
        if company_match:
            return company_match.group(1).strip()

        # Fallback to first few words
        words = first_line.split()[:3]
        return ' '.join(words) if words else "Startup"

    async def score_opportunity(self, opportunity: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advanced scoring algorithm for matching opportunities to user profiles

        Args:
            opportunity: Job opportunity
            user_profile: User's skills, experience, preferences

        Returns:
            Dict with detailed scoring breakdown and overall score
        """
        scoring_breakdown = {
            'skill_match': 0.0,
            'experience_match': 0.0,
            'salary_match': 0.0,
            'location_match': 0.0,
            'industry_match': 0.0,
            'company_size_match': 0.0,
            'job_type_match': 0.0,
            'recency_score': 0.0,
            'keyword_density': 0.0,
            'overall_score': 0.0,
            'match_reasons': [],
            'missing_requirements': []
        }

        job_text = f"{opportunity.get('title', '')} {opportunity.get('description', '')} {' '.join(opportunity.get('tags', []))}".lower()

        # 1. Skill Match (30% weight) - Enhanced with skill levels
        if 'skills' in user_profile:
            skills = user_profile['skills']
            primary_skills = skills.get('primary', []) if isinstance(skills, dict) else skills[:3] if isinstance(skills, list) else []
            secondary_skills = skills.get('secondary', []) if isinstance(skills, dict) else skills[3:] if isinstance(skills, list) else []

            primary_matches = sum(1 for skill in primary_skills if skill.lower() in job_text)
            secondary_matches = sum(1 for skill in secondary_skills if skill.lower() in job_text)

            # Primary skills worth more
            skill_score = (primary_matches * 0.2) + (secondary_matches * 0.05)
            scoring_breakdown['skill_match'] = min(0.3, skill_score)

            if primary_matches > 0:
                scoring_breakdown['match_reasons'].append(f"Matches {primary_matches} of your primary skills")
            if secondary_matches > 0:
                scoring_breakdown['match_reasons'].append(f"Matches {secondary_matches} of your secondary skills")

        # 2. Experience Level Match (15% weight)
        if 'experience_years' in user_profile:
            exp_years = user_profile['experience_years']
            job_exp_keywords = {
                'entry': ['entry', 'junior', 'graduate', '0-2 years', 'no experience'],
                'mid': ['mid', 'intermediate', '2-5 years', '3-5 years', 'some experience'],
                'senior': ['senior', 'lead', 'principal', '5+ years', '7+ years', 'expert'],
                'executive': ['director', 'vp', 'cto', 'head of', 'manager']
            }

            if exp_years <= 2:
                level = 'entry'
            elif exp_years <= 5:
                level = 'mid'
            elif exp_years <= 10:
                level = 'senior'
            else:
                level = 'executive'

            if any(keyword in job_text for keyword in job_exp_keywords[level]):
                scoring_breakdown['experience_match'] = 0.15
                scoring_breakdown['match_reasons'].append(f"Matches your experience level ({level})")
            elif level == 'mid' and any(keyword in job_text for keyword in job_exp_keywords['entry']):
                scoring_breakdown['experience_match'] = 0.1  # Overqualified but might work
            elif level == 'senior' and any(keyword in job_text for keyword in job_exp_keywords['mid']):
                scoring_breakdown['experience_match'] = 0.1

        # 3. Salary Match (20% weight) - Enhanced with range analysis
        if 'desired_salary' in user_profile:
            salary_min = opportunity.get('salary_min', 0)
            salary_max = opportunity.get('salary_max', 0)
            desired = user_profile['desired_salary']
            flexibility = user_profile.get('salary_flexibility', 0.1)  # 10% flexibility by default

            if salary_min and salary_max:
                if salary_min <= desired <= salary_max:
                    scoring_breakdown['salary_match'] = 0.2
                    scoring_breakdown['match_reasons'].append(f"Salary range ${salary_min:,}-${salary_max:,} matches your target")
                elif salary_max >= desired * (1 - flexibility):
                    scoring_breakdown['salary_match'] = 0.15
                    scoring_breakdown['match_reasons'].append("Salary close to your target")
                elif salary_min <= desired * (1 + flexibility):
                    scoring_breakdown['salary_match'] = 0.1
                    scoring_breakdown['match_reasons'].append("Salary negotiable to your range")
            elif 'competitive' in job_text or 'negotiable' in job_text:
                scoring_breakdown['salary_match'] = 0.1
                scoring_breakdown['match_reasons'].append("Competitive salary offered")

        # 4. Location Match (10% weight) - Enhanced with remote preferences
        if 'location_preferences' in user_profile:
            location_prefs = user_profile['location_preferences']
            job_location = opportunity.get('location', '').lower()

            if isinstance(location_prefs, dict):
                if location_prefs.get('remote_only', False) and 'remote' in job_location:
                    scoring_breakdown['location_match'] = 0.1
                    scoring_breakdown['match_reasons'].append("Fully remote position")
                elif location_prefs.get('hybrid_ok', False) and 'hybrid' in job_location:
                    scoring_breakdown['location_match'] = 0.08
                    scoring_breakdown['match_reasons'].append("Hybrid work available")
                elif 'cities' in location_prefs:
                    for city in location_prefs['cities']:
                        if city.lower() in job_location:
                            scoring_breakdown['location_match'] = 0.1
                            scoring_breakdown['match_reasons'].append(f"Located in {city}")
                            break
            elif isinstance(location_prefs, str) and location_prefs.lower() in job_location:
                scoring_breakdown['location_match'] = 0.1
                scoring_breakdown['match_reasons'].append("Location match")

        # 5. Industry/Domain Match (10% weight)
        if 'industries' in user_profile or 'domains' in user_profile:
            industries = user_profile.get('industries', []) + user_profile.get('domains', [])
            if any(industry.lower() in job_text for industry in industries):
                scoring_breakdown['industry_match'] = 0.1
                scoring_breakdown['match_reasons'].append("Industry/domain match")

        # 6. Company Size Preference (5% weight)
        if 'company_size_preference' in user_profile:
            size_pref = user_profile['company_size_preference']
            company_keywords = {
                'startup': ['startup', 'early stage', 'seed', 'series a', 'small team'],
                'medium': ['growing', 'scale-up', 'series b', 'series c', '50-500'],
                'enterprise': ['fortune', 'enterprise', 'large', 'established', '1000+']
            }

            if size_pref in company_keywords and any(keyword in job_text for keyword in company_keywords[size_pref]):
                scoring_breakdown['company_size_match'] = 0.05
                scoring_breakdown['match_reasons'].append(f"{size_pref.title()} company as preferred")

        # 7. Job Type Match (5% weight)
        if 'job_type_preference' in user_profile:
            job_type = user_profile['job_type_preference']
            type_keywords = {
                'full-time': ['full-time', 'full time', 'permanent'],
                'contract': ['contract', 'freelance', 'consultant'],
                'part-time': ['part-time', 'part time', 'flexible hours']
            }

            if job_type in type_keywords and any(keyword in job_text for keyword in type_keywords[job_type]):
                scoring_breakdown['job_type_match'] = 0.05
                scoring_breakdown['match_reasons'].append(f"{job_type.replace('-', ' ').title()} position")

        # 8. Recency Bonus (5% weight)
        if 'date_posted' in opportunity:
            try:
                from dateutil import parser
                posted_date = parser.parse(opportunity['date_posted'])
                days_old = (datetime.now(posted_date.tzinfo) - posted_date).days

                if days_old <= 1:
                    scoring_breakdown['recency_score'] = 0.05
                    scoring_breakdown['match_reasons'].append("Posted today!")
                elif days_old <= 3:
                    scoring_breakdown['recency_score'] = 0.04
                    scoring_breakdown['match_reasons'].append("Posted recently")
                elif days_old <= 7:
                    scoring_breakdown['recency_score'] = 0.03
                    scoring_breakdown['match_reasons'].append("Posted this week")
                elif days_old <= 14:
                    scoring_breakdown['recency_score'] = 0.02
            except:
                pass

        # Calculate overall score
        scoring_breakdown['overall_score'] = sum([
            scoring_breakdown['skill_match'],
            scoring_breakdown['experience_match'],
            scoring_breakdown['salary_match'],
            scoring_breakdown['location_match'],
            scoring_breakdown['industry_match'],
            scoring_breakdown['company_size_match'],
            scoring_breakdown['job_type_match'],
            scoring_breakdown['recency_score']
        ])

        # Add keyword density as a bonus (can push score above 1.0 for exceptional matches)
        if 'keywords' in user_profile:
            keyword_matches = sum(1 for kw in user_profile['keywords'] if kw.lower() in job_text)
            scoring_breakdown['keyword_density'] = min(0.2, keyword_matches * 0.02)
            scoring_breakdown['overall_score'] += scoring_breakdown['keyword_density']

        # Identify missing requirements
        common_requirements = ['python', 'javascript', 'react', 'django', 'aws', 'docker', 'kubernetes', 'sql']
        for req in common_requirements:
            if req in job_text and 'skills' in user_profile:
                all_skills = user_profile['skills']
                if isinstance(all_skills, dict):
                    all_skills = all_skills.get('primary', []) + all_skills.get('secondary', [])
                if not any(req in skill.lower() for skill in all_skills):
                    scoring_breakdown['missing_requirements'].append(req.upper())

        return scoring_breakdown

    async def apply_to_opportunity(self, opportunity: Dict[str, Any], application_data: Dict[str, Any]) -> bool:
        """
        Auto-apply to an opportunity (when implemented)

        Args:
            opportunity: The job opportunity
            application_data: Resume, cover letter, etc.

        Returns:
            True if application was successful
        """
        logger.info(f"Would apply to: {opportunity['title']} at {opportunity['company']}")
        # This would implement actual application logic
        # For now, it's a placeholder
        return False

    async def close(self):
        """Clean up resources"""
        await self.web_layer.close()


async def test_real_job_spider():
    """Test the real job spider"""
    spider = RealJobSpider()

    # Search for real opportunities
    keywords = ['python', 'ai', 'remote', 'developer']
    opportunities = await spider.search_real_jobs(keywords)

    print(f"\n🎯 Found {len(opportunities)} real job opportunities!\n")

    # Display first 5 opportunities
    for i, opp in enumerate(opportunities[:5], 1):
        print(f"{i}. {opp['title']} at {opp['company']}")
        print(f"   Source: {opp['source']}")
        print(f"   URL: {opp.get('url', 'N/A')}")
        if opp.get('salary_min'):
            print(f"   Salary: ${opp.get('salary_min', 0):,} - ${opp.get('salary_max', 0):,}")
        print(f"   Match Score: {opp.get('match_score', 0):.2%}")
        print()

    # Test scoring with an enhanced user profile
    user_profile = {
        'skills': {
            'primary': ['python', 'machine learning', 'ai'],
            'secondary': ['django', 'react', 'aws', 'docker']
        },
        'experience_years': 5,
        'desired_salary': 120000,
        'salary_flexibility': 0.15,  # 15% flexibility
        'location_preferences': {
            'remote_only': True,
            'hybrid_ok': True,
            'cities': ['San Francisco', 'New York', 'Austin']
        },
        'industries': ['tech', 'fintech', 'ai', 'saas'],
        'company_size_preference': 'startup',
        'job_type_preference': 'full-time',
        'keywords': ['innovation', 'growth', 'leadership', 'cutting-edge']
    }

    if opportunities:
        scored_opps = []
        for opp in opportunities[:20]:  # Score more opportunities
            score_breakdown = await spider.score_opportunity(opp, user_profile)
            opp['scoring'] = score_breakdown
            opp['user_match_score'] = score_breakdown['overall_score']
            scored_opps.append(opp)

        # Sort by score
        scored_opps.sort(key=lambda x: x['user_match_score'], reverse=True)

        print("\n🎯 Top matches for your profile (Enhanced Scoring):")
        print("=" * 80)
        for i, opp in enumerate(scored_opps[:5], 1):
            print(f"\n{i}. {opp['title']} at {opp['company']}")
            print(f"   📍 Location: {opp.get('location', 'Not specified')}")
            print(f"   🔗 Source: {opp['source']}")
            print(f"   💰 Salary: ", end="")
            if opp.get('salary_min'):
                print(f"${opp.get('salary_min', 0):,} - ${opp.get('salary_max', 0):,}")
            else:
                print(opp.get('salary', 'Not specified'))
            print(f"   📊 Match Score: {opp['user_match_score']:.1%}")

            # Show match reasons
            if opp['scoring']['match_reasons']:
                print(f"   ✅ Why it's a match:")
                for reason in opp['scoring']['match_reasons'][:3]:
                    print(f"      • {reason}")

            # Show missing requirements
            if opp['scoring']['missing_requirements']:
                print(f"   ⚠️  Missing skills: {', '.join(opp['scoring']['missing_requirements'][:3])}")

            print(f"   🔗 Apply: {opp.get('application_url', opp.get('url', 'N/A'))[:60]}...")

        # Show scoring breakdown for the top match
        if scored_opps:
            top_match = scored_opps[0]
            print("\n" + "=" * 80)
            print("📊 DETAILED SCORING BREAKDOWN FOR TOP MATCH:")
            print("=" * 80)
            print(f"Job: {top_match['title']} at {top_match['company']}")
            print("\nScoring Components:")
            breakdown = top_match['scoring']
            print(f"  • Skill Match:        {breakdown['skill_match']:.1%} of 30%")
            print(f"  • Experience Match:   {breakdown['experience_match']:.1%} of 15%")
            print(f"  • Salary Match:       {breakdown['salary_match']:.1%} of 20%")
            print(f"  • Location Match:     {breakdown['location_match']:.1%} of 10%")
            print(f"  • Industry Match:     {breakdown['industry_match']:.1%} of 10%")
            print(f"  • Company Size:       {breakdown['company_size_match']:.1%} of 5%")
            print(f"  • Job Type:           {breakdown['job_type_match']:.1%} of 5%")
            print(f"  • Recency:            {breakdown['recency_score']:.1%} of 5%")
            print(f"  • Keyword Bonus:      {breakdown['keyword_density']:.1%} (bonus)")
            print(f"\n  🎯 OVERALL SCORE:     {breakdown['overall_score']:.1%}")

    await spider.close()


if __name__ == "__main__":
    asyncio.run(test_real_job_spider())