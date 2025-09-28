"""
Real Job Spider - Actually searches for real freelance opportunities
Phase 1: Real data collection implementation
"""

import asyncio
import json
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

        # 3. Search GitHub Jobs (if still available)
        logger.info("🕷️ Searching GitHub Jobs...")
        github_opportunities = await self._search_github_jobs(keywords)
        all_opportunities.extend(github_opportunities)

        # 4. Search HackerNews Who's Hiring
        logger.info("🕷️ Searching HackerNews Who's Hiring...")
        hn_opportunities = await self._search_hackernews_jobs()
        all_opportunities.extend(hn_opportunities)

        # 5. Search AngelList (public data)
        logger.info("🕷️ Searching AngelList for startup jobs...")
        angellist_opportunities = await self._search_angellist(keywords)
        all_opportunities.extend(angellist_opportunities)

        # Log summary
        logger.info(f"✅ Total real opportunities found: {len(all_opportunities)}")
        for source in ['RemoteOK', 'Remotive', 'GitHub', 'HackerNews', 'AngelList']:
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

    async def _search_angellist(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search AngelList for startup jobs"""
        opportunities = []
        try:
            # AngelList requires more complex authentication, so we'll scrape public pages
            # For now, we'll use a simplified approach
            base_url = 'https://angel.co/jobs'

            # This is a placeholder - in production you'd implement proper scraping
            logger.debug("AngelList scraping would be implemented here")

        except Exception as e:
            logger.error(f"Error searching AngelList: {e}")

        return opportunities

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

    async def score_opportunity(self, opportunity: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """
        Score how well an opportunity matches a user's profile

        Args:
            opportunity: Job opportunity
            user_profile: User's skills, experience, preferences

        Returns:
            Score between 0 and 1
        """
        score = 0.0

        # Check skill match
        if 'skills' in user_profile:
            job_text = f"{opportunity.get('title', '')} {opportunity.get('description', '')}".lower()
            skill_matches = sum(1 for skill in user_profile['skills'] if skill.lower() in job_text)
            score += min(0.4, skill_matches * 0.1)  # Up to 40% for skills

        # Check salary match
        if 'desired_salary' in user_profile:
            salary_min = opportunity.get('salary_min', 0)
            salary_max = opportunity.get('salary_max', 0)
            desired = user_profile['desired_salary']

            if salary_min and salary_max:
                if salary_min <= desired <= salary_max:
                    score += 0.3  # 30% for salary match
                elif salary_max >= desired * 0.8:
                    score += 0.15  # 15% for close match

        # Check location preference
        if 'location_preference' in user_profile:
            if user_profile['location_preference'].lower() in opportunity.get('location', '').lower():
                score += 0.2  # 20% for location match

        # Recency bonus
        if 'date_posted' in opportunity:
            try:
                posted_date = datetime.fromisoformat(opportunity['date_posted'])
                days_old = (datetime.now() - posted_date).days
                if days_old <= 7:
                    score += 0.1  # 10% for fresh opportunities
            except:
                pass

        return min(1.0, score)

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

    # Test scoring with a user profile
    user_profile = {
        'skills': ['python', 'machine learning', 'ai'],
        'desired_salary': 100000,
        'location_preference': 'remote'
    }

    if opportunities:
        scored_opps = []
        for opp in opportunities[:10]:
            score = await spider.score_opportunity(opp, user_profile)
            opp['user_match_score'] = score
            scored_opps.append(opp)

        # Sort by score
        scored_opps.sort(key=lambda x: x['user_match_score'], reverse=True)

        print("\n🎯 Top matches for your profile:")
        for i, opp in enumerate(scored_opps[:3], 1):
            print(f"{i}. {opp['title']} - Score: {opp['user_match_score']:.2%}")

    await spider.close()


if __name__ == "__main__":
    asyncio.run(test_real_job_spider())