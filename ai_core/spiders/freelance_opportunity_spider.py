"""
Freelance Opportunity Spider
Finds real freelance jobs that can be completed by our AI agents
"""
import asyncio
import aiohttp
import json
import re
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import logging
from urllib.parse import quote
from html import unescape
import html2text

logger = logging.getLogger(__name__)


@dataclass
class FreelanceOpportunity:
    """Structured freelance job opportunity"""
    job_id: str
    platform: str
    title: str
    description: str
    budget: Optional[float]
    budget_type: str  # 'fixed' or 'hourly'
    skills_required: List[str]
    deadline: Optional[str]
    client_rating: Optional[float]
    url: str
    agent_suitability: float  # 0-1 score for how well agents can do this
    recommended_agents: List[str]
    estimated_completion_time: int  # hours
    confidence_score: float


class FreelanceOpportunitySpider:
    """
    Spider that finds freelance jobs suitable for AI agent completion.
    Focuses on: content writing, data analysis, code generation, design work.
    """

    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.session = None

        # Initialize HTML to text converter
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True
        self.html_converter.body_width = 0  # Don't wrap lines

        # Agent capabilities mapping
        self.agent_capabilities = {
            'content_writing': [
                'content_creator_agent',
                'viral_content_agent',
                'seo_optimizer_agent',
                'copywriting_agent'
            ],
            'data_analysis': [
                'data_analyst_agent',
                'market_research_agent',
                'business_intelligence_agent',
                'report_generator_agent'
            ],
            'programming': [
                'code_generator_agent',
                'api_builder_agent',
                'automation_agent',
                'script_writer_agent'
            ],
            'design': [
                'ui_designer_agent',
                'graphics_creator_agent',
                'presentation_designer_agent'
            ],
            'research': [
                'research_analyst_agent',
                'competitive_analysis_agent',
                'market_research_agent'
            ]
        }

    async def initialize(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': 'FreelanceBot/1.0'}
            )

    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()

    async def find_opportunities(self, use_real_data: bool = False) -> List[FreelanceOpportunity]:
        """
        Main method to find freelance opportunities.
        Can use real Upwork RSS feeds or mock data for testing.
        """
        opportunities = []

        if use_real_data:
            # Use real Upwork RSS feeds
            real_opportunities = await self._fetch_real_opportunities()
            opportunities_data = real_opportunities
        else:
            # Use mock data for testing
            opportunities_data = await self._generate_mock_opportunities()

        for opp_data in opportunities_data:
            opportunity = await self._analyze_opportunity(opp_data)
            if opportunity.agent_suitability >= 0.7:  # Only high-confidence jobs
                opportunities.append(opportunity)
                await self._store_opportunity(opportunity)

        logger.info(f"🎯 Found {len(opportunities)} suitable freelance opportunities")
        return opportunities

    async def _fetch_real_opportunities(self) -> List[Dict]:
        """
        Fetch REAL opportunities from actual freelance platforms.
        Uses working APIs: Hacker News Jobs, RemoteOK, and others.
        """
        logger.info("🌐 Fetching REAL job opportunities from live APIs...")

        all_opportunities = []

        # Fetch from Hacker News Jobs API
        try:
            hn_jobs = await self._fetch_hackernews_jobs()
            all_opportunities.extend(hn_jobs)
        except Exception as e:
            logger.error(f"Failed to fetch Hacker News jobs: {e}")

        # Fetch from RemoteOK API
        try:
            remote_jobs = await self._fetch_remoteok_jobs()
            all_opportunities.extend(remote_jobs)
        except Exception as e:
            logger.error(f"Failed to fetch RemoteOK jobs: {e}")

        # Fetch from Freelancer.com RSS
        try:
            freelancer_jobs = await self._fetch_freelancer_jobs()
            all_opportunities.extend(freelancer_jobs)
        except Exception as e:
            logger.error(f"Failed to fetch Freelancer jobs: {e}")

        logger.info(f"🎯 Fetched {len(all_opportunities)} REAL opportunities from live sources")
        return all_opportunities

    async def _fetch_hackernews_jobs(self) -> List[Dict]:
        """Fetch real jobs from Hacker News API"""
        url = "https://hn.algolia.com/api/v1/search_by_date?tags=job&hitsPerPage=20"

        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                jobs = []

                for hit in data.get('hits', []):
                    try:
                        # Extract relevant job info
                        job = {
                            'job_id': f"hn_{hit.get('objectID', '')}",
                            'platform': 'Hacker News',
                            'title': hit.get('title', '').replace('[Hiring]', '').strip(),
                            'description': self._clean_html_description(hit.get('comment_text', hit.get('story_text', ''))),
                            'budget': None,  # HN doesn't specify budgets
                            'budget_type': 'unknown',
                            'skills': self._extract_skills_from_text(hit.get('title', '') + ' ' + hit.get('comment_text', '')),
                            'deadline': None,
                            'client_rating': None,
                            'url': f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
                        }

                        if job['title'] and len(job['title']) > 10:  # Valid job title
                            jobs.append(job)

                    except Exception as e:
                        logger.warning(f"Failed to parse HN job: {e}")
                        continue

                logger.info(f"📰 Fetched {len(jobs)} jobs from Hacker News")
                return jobs

        return []

    async def _fetch_remoteok_jobs(self) -> List[Dict]:
        """Fetch real jobs from RemoteOK API"""
        url = "https://remoteok.io/api"

        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                jobs = []

                # Skip first item (it's metadata)
                for job_data in data[1:21]:  # Get up to 20 jobs
                    try:
                        job = {
                            'job_id': f"rok_{job_data.get('id', '')}",
                            'platform': 'RemoteOK',
                            'title': job_data.get('position', ''),
                            'description': self._clean_html_description(job_data.get('description', '')),
                            'budget': self._parse_salary(job_data.get('salary_min'), job_data.get('salary_max')),
                            'budget_type': 'salary' if job_data.get('salary_min') else 'unknown',
                            'skills': job_data.get('tags', []) if isinstance(job_data.get('tags'), list) else [],
                            'deadline': None,
                            'client_rating': None,
                            'url': f"https://remoteok.io/remote-jobs/{job_data.get('id', '')}"
                        }

                        if job['title'] and len(job['title']) > 5:  # Valid job
                            jobs.append(job)

                    except Exception as e:
                        logger.warning(f"Failed to parse RemoteOK job: {e}")
                        continue

                logger.info(f"🌍 Fetched {len(jobs)} jobs from RemoteOK")
                return jobs

        return []

    async def _fetch_freelancer_jobs(self) -> List[Dict]:
        """Fetch real jobs from Freelancer.com RSS feed"""
        url = "https://www.freelancer.com/jobs/rss.xml"

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    xml_content = await response.text()

                    # Parse RSS feed
                    import feedparser
                    feed = feedparser.parse(xml_content)
                    jobs = []

                    for entry in feed.entries[:15]:  # Get up to 15 jobs
                        try:
                            job = {
                                'job_id': f"fl_{entry.get('id', entry.get('link', '').split('/')[-1])}",
                                'platform': 'Freelancer.com',
                                'title': entry.get('title', ''),
                                'description': self._clean_html_description(entry.get('summary', entry.get('description', ''))),
                                'budget': self._extract_budget_from_text(entry.get('title', '') + ' ' + entry.get('summary', ''))[0] if self._extract_budget_from_text(entry.get('title', '') + ' ' + entry.get('summary', '')) else None,
                                'budget_type': 'fixed',
                                'skills': self._extract_skills_from_text(entry.get('title', '') + ' ' + entry.get('summary', '')),
                                'deadline': None,
                                'client_rating': None,
                                'url': entry.get('link', '')
                            }

                            if job['title'] and len(job['title']) > 5:
                                jobs.append(job)

                        except Exception as e:
                            logger.warning(f"Failed to parse Freelancer job: {e}")
                            continue

                    logger.info(f"💼 Fetched {len(jobs)} jobs from Freelancer.com")
                    return jobs

        except Exception as e:
            logger.error(f"Failed to fetch Freelancer RSS: {e}")

        return []

    def _parse_salary(self, min_salary, max_salary):
        """Parse salary information"""
        try:
            if min_salary and max_salary:
                return int((int(min_salary) + int(max_salary)) / 2)
            elif min_salary:
                return int(min_salary)
            elif max_salary:
                return int(max_salary)
        except:
            pass
        return None

    async def _parse_rss_entry(self, entry, platform: str) -> Optional[Dict]:
        """Parse RSS entry into our job format"""
        try:
            # Extract basic info
            title = getattr(entry, 'title', '')
            description = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
            link = getattr(entry, 'link', '')

            # Generate unique job ID
            job_id = hashlib.md5(f"{platform}_{link}".encode()).hexdigest()[:12]

            # Extract budget and skills from description if possible
            budget, budget_type = self._extract_budget_from_text(description)
            skills = self._extract_skills_from_text(title + ' ' + description)

            # Calculate basic deadline (assume 1-2 weeks for most jobs)
            deadline_date = datetime.now().strftime('%Y-%m-%d')

            return {
                'job_id': f"{platform.lower()}_{job_id}",
                'platform': platform,
                'title': title,
                'description': description[:500],  # Limit description length
                'budget': budget,
                'budget_type': budget_type,
                'skills': skills,
                'deadline': deadline_date,
                'client_rating': 4.5,  # Default rating
                'url': link
            }

        except Exception as e:
            logger.warning(f"Failed to parse RSS entry: {e}")
            return None

    def _extract_budget_from_text(self, text: str) -> tuple:
        """Extract budget information from job text"""
        text_lower = text.lower()

        # Look for budget patterns
        budget_patterns = [
            r'\$(\d+)-\$(\d+)',  # $100-$500
            r'\$(\d+)',          # $500
            r'budget[:\s]+\$?(\d+)',  # Budget: $500
            r'(\d+)\s*dollars?',      # 500 dollars
        ]

        for pattern in budget_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if len(matches[0]) == 2:  # Range like $100-$500
                    return float(matches[0][1]), 'fixed'  # Take upper range
                else:
                    return float(matches[0]), 'fixed'

        # Check for hourly indicators
        if any(word in text_lower for word in ['hourly', 'per hour', '/hour', '/hr']):
            # Default hourly budget
            return 25.0, 'hourly'

        # Default budget if none found
        return 300.0, 'fixed'

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract relevant skills from job text"""
        text_lower = text.lower()

        skill_keywords = {
            'content writing': ['content', 'writing', 'blog', 'article', 'copywriting'],
            'seo': ['seo', 'search engine', 'optimization', 'keywords'],
            'python': ['python', 'django', 'flask', 'pandas'],
            'data analysis': ['data', 'analysis', 'analytics', 'excel', 'sql'],
            'research': ['research', 'analysis', 'report', 'study'],
            'web development': ['web', 'html', 'css', 'javascript', 'react'],
            'social media': ['social media', 'facebook', 'instagram', 'twitter'],
            'marketing': ['marketing', 'advertising', 'promotion', 'campaign']
        }

        found_skills = []
        for skill, keywords in skill_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_skills.append(skill)

        # Always include at least one skill
        if not found_skills:
            found_skills = ['general']

        return found_skills

    async def _generate_mock_opportunities(self) -> List[Dict]:
        """Generate realistic mock freelance opportunities"""
        return [
            {
                'job_id': 'upw_001',
                'platform': 'Upwork',
                'title': 'Write 10 SEO Blog Posts on AI Tools',
                'description': 'Need 10 high-quality blog posts about AI productivity tools. Each post should be 1500-2000 words, SEO optimized, with examples and screenshots.',
                'budget': 500,
                'budget_type': 'fixed',
                'skills': ['content writing', 'SEO', 'AI knowledge'],
                'deadline': '2025-09-27',
                'client_rating': 4.8,
                'url': 'https://upwork.com/jobs/fake_001'
            },
            {
                'job_id': 'fl_002',
                'platform': 'Freelancer',
                'title': 'Python Script for Data Analysis',
                'description': 'Create Python script to analyze CSV sales data, generate reports with visualizations, and export to PDF.',
                'budget': 300,
                'budget_type': 'fixed',
                'skills': ['Python', 'pandas', 'data visualization'],
                'deadline': '2025-09-25',
                'client_rating': 4.5,
                'url': 'https://freelancer.com/projects/fake_002'
            },
            {
                'job_id': 'fiv_003',
                'platform': 'Fiverr',
                'title': 'Market Research Report on EV Industry',
                'description': 'Comprehensive market research report on electric vehicle industry, including competitor analysis, market trends, and growth projections.',
                'budget': 750,
                'budget_type': 'fixed',
                'skills': ['market research', 'business analysis', 'report writing'],
                'deadline': '2025-09-30',
                'client_rating': 4.9,
                'url': 'https://fiverr.com/gigs/fake_003'
            },
            {
                'job_id': 'upw_004',
                'platform': 'Upwork',
                'title': 'Build REST API with Node.js',
                'description': 'Need REST API for e-commerce platform. Must include user auth, product CRUD, order management, and payment integration.',
                'budget': 1200,
                'budget_type': 'fixed',
                'skills': ['Node.js', 'REST API', 'MongoDB', 'JWT'],
                'deadline': '2025-10-05',
                'client_rating': 4.7,
                'url': 'https://upwork.com/jobs/fake_004'
            },
            {
                'job_id': 'top_005',
                'platform': 'Toptal',
                'title': 'Financial Data Analysis Dashboard',
                'description': 'Create interactive dashboard for financial data analysis with real-time updates and predictive analytics.',
                'budget': 150,
                'budget_type': 'hourly',
                'skills': ['data analysis', 'dashboard creation', 'financial modeling'],
                'deadline': None,
                'client_rating': 5.0,
                'url': 'https://toptal.com/projects/fake_005'
            }
        ]

    async def _analyze_opportunity(self, opp_data: Dict) -> FreelanceOpportunity:
        """
        Analyze opportunity to determine agent suitability.
        Uses AI to understand requirements and match with agent capabilities.
        """
        # Determine which agents can handle this job
        recommended_agents = []
        job_categories = self._categorize_job(opp_data['skills'])

        for category in job_categories:
            if category in self.agent_capabilities:
                recommended_agents.extend(self.agent_capabilities[category])

        # Calculate suitability score
        suitability = self._calculate_suitability(opp_data, recommended_agents)

        # Estimate completion time based on job type
        completion_time = self._estimate_completion_time(opp_data)

        # Calculate confidence score
        confidence = self._calculate_confidence(opp_data, recommended_agents)

        return FreelanceOpportunity(
            job_id=opp_data['job_id'],
            platform=opp_data['platform'],
            title=opp_data['title'],
            description=opp_data['description'],
            budget=opp_data.get('budget'),
            budget_type=opp_data['budget_type'],
            skills_required=opp_data['skills'],
            deadline=opp_data.get('deadline'),
            client_rating=opp_data.get('client_rating'),
            url=opp_data['url'],
            agent_suitability=suitability,
            recommended_agents=list(set(recommended_agents)),
            estimated_completion_time=completion_time,
            confidence_score=confidence
        )

    def _categorize_job(self, skills: List[str]) -> List[str]:
        """Categorize job based on required skills"""
        categories = []
        skills_lower = [s.lower() for s in skills]

        if any(term in ' '.join(skills_lower) for term in ['content', 'writing', 'blog', 'seo', 'article']):
            categories.append('content_writing')

        if any(term in ' '.join(skills_lower) for term in ['data', 'analysis', 'analytics', 'visualization']):
            categories.append('data_analysis')

        if any(term in ' '.join(skills_lower) for term in ['python', 'javascript', 'api', 'node', 'code', 'script']):
            categories.append('programming')

        if any(term in ' '.join(skills_lower) for term in ['design', 'ui', 'ux', 'graphics']):
            categories.append('design')

        if any(term in ' '.join(skills_lower) for term in ['research', 'market', 'competitive', 'report']):
            categories.append('research')

        return categories

    def _calculate_suitability(self, opp_data: Dict, agents: List[str]) -> float:
        """Calculate how suitable this job is for our agents"""
        score = 0.0

        # Have capable agents
        if len(agents) > 0:
            score += 0.3

        # Good budget
        if opp_data.get('budget'):
            if opp_data['budget'] >= 200:
                score += 0.2
            if opp_data['budget'] >= 500:
                score += 0.1

        # Reasonable deadline
        if opp_data.get('deadline'):
            days_to_deadline = self._days_until(opp_data['deadline'])
            if days_to_deadline >= 3:
                score += 0.2
        else:
            score += 0.2  # No deadline is good

        # Good client rating
        client_rating = opp_data.get('client_rating', 0)
        if client_rating and client_rating >= 4.5:
            score += 0.1

        # Job type matches our strengths
        job_types = self._categorize_job(opp_data['skills'])
        if 'content_writing' in job_types or 'data_analysis' in job_types:
            score += 0.1

        return min(score, 1.0)

    def _estimate_completion_time(self, opp_data: Dict) -> int:
        """Estimate hours needed to complete the job"""
        base_time = 4  # Base time for any job

        # Adjust based on job type
        if 'content writing' in ' '.join(opp_data['skills']).lower():
            if '10' in opp_data['title'] or 'multiple' in opp_data['description'].lower():
                base_time = 12
            else:
                base_time = 4

        if 'api' in ' '.join(opp_data['skills']).lower():
            base_time = 16

        if 'research' in ' '.join(opp_data['skills']).lower():
            base_time = 8

        return base_time

    def _calculate_confidence(self, opp_data: Dict, agents: List[str]) -> float:
        """Calculate confidence in successful completion"""
        confidence = 0.5  # Base confidence

        # More agents = higher confidence
        if len(agents) >= 3:
            confidence += 0.2
        elif len(agents) >= 1:
            confidence += 0.1

        # Clear requirements = higher confidence
        if len(opp_data['description']) > 100:
            confidence += 0.1

        # Good budget = higher confidence
        budget = opp_data.get('budget', 0)
        if budget and budget >= 500:
            confidence += 0.1

        # Platform reputation
        if opp_data['platform'] in ['Upwork', 'Toptal']:
            confidence += 0.1

        return min(confidence, 0.95)

    def _days_until(self, date_str: str) -> int:
        """Calculate days until deadline"""
        try:
            deadline = datetime.strptime(date_str, '%Y-%m-%d')
            delta = deadline - datetime.now()
            return delta.days
        except:
            return 30  # Default to 30 days if parsing fails

    def _clean_html_description(self, html_content: str) -> str:
        """Clean HTML content and convert to readable text"""
        if not html_content:
            return ""

        try:
            # First decode HTML entities
            text = unescape(html_content)

            # Convert HTML to text using the html2text library
            text = self.html_converter.handle(text)

            # Clean up markdown artifacts from html2text
            text = re.sub(r'\*\*([^*]*)\*\*', r'\1', text)  # Remove bold markers, keep content
            text = re.sub(r'__([^_]*)__', r'\1', text)      # Remove underline markers, keep content
            text = re.sub(r'_([^_]*)_', r'\1', text)        # Remove italic markers, keep content
            text = re.sub(r'\*\*\s*\*\*', '', text)         # Remove empty bold markers
            text = re.sub(r'__\s*__', '', text)             # Remove empty underline markers
            text = re.sub(r'_\s*_', '', text)               # Remove empty italic markers

            # Clean up extra whitespace and newlines
            text = re.sub(r'\n\s*\n+', '\n\n', text)        # Normalize multiple newlines
            text = re.sub(r'[ \t]+', ' ', text)             # Normalize spaces
            text = re.sub(r'\n ', '\n', text)               # Remove spaces after newlines

            # Remove markdown headers
            text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

            # Clean up special characters but preserve Unicode
            # Only remove control characters and problematic symbols
            text = re.sub(r'[^\w\s\.\,\!\?\-\(\)\[\]\'\"\:\;\/\\\@\#\$\%\^\&\*\+\=\|\~\`\u00C0-\u017F\u0100-\u024F]', '', text)

            text = text.strip()

            # Limit length
            if len(text) > 500:
                text = text[:500] + "..."

            return text

        except Exception as e:
            logger.warning(f"Failed to clean HTML content: {e}")
            # Fallback to simple HTML tag removal and entity decoding
            text = unescape(html_content)
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'[^\w\s\.\,\!\?\-\(\)\[\]\'\"\:\;\/\\\@\#\$\%\^\&\*\+\=\|\~\`]', '', text)
            return text[:500]

    async def _store_opportunity(self, opportunity: FreelanceOpportunity):
        """Store opportunity in Redis for processing"""
        if self.redis_client:
            key = f"freelance:opportunity:{opportunity.job_id}"
            data = {
                'job_id': opportunity.job_id,
                'platform': opportunity.platform,
                'title': opportunity.title,
                'description': opportunity.description,
                'budget': opportunity.budget,
                'budget_type': opportunity.budget_type,
                'skills_required': opportunity.skills_required,
                'deadline': opportunity.deadline,
                'client_rating': opportunity.client_rating,
                'url': opportunity.url,
                'agent_suitability': opportunity.agent_suitability,
                'recommended_agents': opportunity.recommended_agents,
                'estimated_completion_time': opportunity.estimated_completion_time,
                'confidence_score': opportunity.confidence_score,
                'found_at': datetime.now().isoformat(),
                'status': 'new'
            }

            self.redis_client.setex(key, 86400, json.dumps(data))  # 24 hour TTL

            # Add to opportunity queue
            self.redis_client.lpush('freelance:queue:new', opportunity.job_id)

            # Publish notification
            self.redis_client.publish('freelance:new_opportunity', json.dumps({
                'job_id': opportunity.job_id,
                'title': opportunity.title,
                'budget': opportunity.budget,
                'platform': opportunity.platform
            }))