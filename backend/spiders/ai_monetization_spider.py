#!/usr/bin/env python3
"""
AI Monetization Research Spider
Scrapes Medium, HackerNoon, Dev.to for AI money-making strategies and opportunities
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


class AIMonetizationSpider:
    """Scrapes AI monetization strategies from content platforms"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = None
        self.cache = {}
        self.cache_duration = timedelta(hours=6)  # Cache longer for articles

    async def research_all(self) -> List[Dict]:
        """Research all AI monetization sources"""
        strategies = []

        # Research sources
        sources = [
            self.scrape_medium_ai_monetization(),
            self.scrape_hackernoon_ai_business(),
            self.scrape_devto_ai_projects(),
            self.scrape_towards_datascience(),
            self.scrape_builtin_ai_startup()
        ]

        # Run all scrapers concurrently
        async with aiohttp.ClientSession(headers=self.headers) as session:
            self.session = session
            results = await asyncio.gather(*sources, return_exceptions=True)

        # Combine results
        for result in results:
            if isinstance(result, list):
                strategies.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"AI monetization scraper failed: {result}")

        # Deduplicate and score strategies
        unique_strategies = self._deduplicate_strategies(strategies)
        scored_strategies = self._score_strategies(unique_strategies)

        return scored_strategies[:15]  # Return top 15 strategies

    async def scrape_medium_ai_monetization(self) -> List[Dict]:
        """Scrape Medium for AI monetization articles"""
        try:
            # Search for AI monetization articles
            search_queries = [
                "make money with AI 2025",
                "AI side hustle",
                "monetize artificial intelligence",
                "AI business ideas",
                "ChatGPT business opportunities"
            ]

            strategies = []
            for query in search_queries[:2]:  # Limit queries
                url = f"https://medium.com/search?q={query.replace(' ', '%20')}"

                try:
                    async with self.session.get(url, timeout=15) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')

                            # Find article links
                            articles = soup.find_all('article')[:5]  # Top 5 per query

                            for article in articles:
                                try:
                                    title_element = article.find('h2') or article.find('h3')
                                    if not title_element:
                                        continue

                                    title = title_element.get_text(strip=True)

                                    # Extract link
                                    link_element = article.find('a', href=True)
                                    if link_element:
                                        article_url = link_element['href']
                                        if not article_url.startswith('http'):
                                            article_url = f"https://medium.com{article_url}"

                                        # Extract strategy details
                                        strategy = await self._extract_strategy_from_medium(article_url, title)
                                        if strategy:
                                            strategies.append(strategy)

                                except Exception as e:
                                    logger.debug(f"Failed to parse Medium article: {e}")

                except Exception as e:
                    logger.warning(f"Failed to search Medium for '{query}': {e}")

            return strategies

        except Exception as e:
            logger.error(f"Medium AI monetization scraping failed: {e}")
            return self._generate_fallback_strategies('medium', 3)

    async def scrape_hackernoon_ai_business(self) -> List[Dict]:
        """Scrape HackerNoon for AI business strategies"""
        try:
            # HackerNoon AI and business tags
            urls = [
                "https://hackernoon.com/tagged/artificial-intelligence",
                "https://hackernoon.com/tagged/ai-monetization",
                "https://hackernoon.com/tagged/startup"
            ]

            strategies = []
            for url in urls[:2]:  # Limit to 2 URLs
                try:
                    async with self.session.get(url, timeout=15) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')

                            # Find story cards
                            story_cards = soup.find_all('div', class_='story-card')[:3]

                            for card in story_cards:
                                try:
                                    title_element = card.find('h3') or card.find('h2')
                                    if not title_element:
                                        continue

                                    title = title_element.get_text(strip=True)

                                    # Check if it's AI monetization related
                                    if self._is_monetization_related(title):
                                        link_element = card.find('a', href=True)
                                        if link_element:
                                            article_url = link_element['href']
                                            if not article_url.startswith('http'):
                                                article_url = f"https://hackernoon.com{article_url}"

                                            strategy = await self._extract_strategy_from_hackernoon(article_url, title)
                                            if strategy:
                                                strategies.append(strategy)

                                except Exception as e:
                                    logger.debug(f"Failed to parse HackerNoon story: {e}")

                except Exception as e:
                    logger.warning(f"Failed to scrape HackerNoon URL {url}: {e}")

            return strategies

        except Exception as e:
            logger.error(f"HackerNoon AI business scraping failed: {e}")
            return self._generate_fallback_strategies('hackernoon', 2)

    async def scrape_devto_ai_projects(self) -> List[Dict]:
        """Scrape Dev.to for AI project ideas"""
        try:
            # Dev.to AI-related tags
            tags = ['ai', 'machinelearning', 'chatgpt', 'openai']
            strategies = []

            for tag in tags[:2]:  # Limit to 2 tags
                url = f"https://dev.to/t/{tag}"

                try:
                    async with self.session.get(url, timeout=15) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')

                            # Find article previews
                            articles = soup.find_all('div', class_='crayons-story')[:3]

                            for article in articles:
                                try:
                                    title_element = article.find('h3') or article.find('h2')
                                    if not title_element:
                                        continue

                                    title = title_element.get_text(strip=True)

                                    if self._is_project_related(title):
                                        link_element = article.find('a', href=True)
                                        if link_element:
                                            article_url = link_element['href']
                                            if not article_url.startswith('http'):
                                                article_url = f"https://dev.to{article_url}"

                                            strategy = await self._extract_strategy_from_devto(article_url, title)
                                            if strategy:
                                                strategies.append(strategy)

                                except Exception as e:
                                    logger.debug(f"Failed to parse Dev.to article: {e}")

                except Exception as e:
                    logger.warning(f"Failed to scrape Dev.to tag {tag}: {e}")

            return strategies

        except Exception as e:
            logger.error(f"Dev.to AI projects scraping failed: {e}")
            return self._generate_fallback_strategies('devto', 2)

    async def scrape_towards_datascience(self) -> List[Dict]:
        """Scrape Towards Data Science for AI business insights"""
        try:
            url = "https://towardsdatascience.com/"

            async with self.session.get(url, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    strategies = []
                    # Find featured articles
                    articles = soup.find_all('article')[:5]

                    for article in articles:
                        try:
                            title_element = article.find('h2') or article.find('h3')
                            if not title_element:
                                continue

                            title = title_element.get_text(strip=True)

                            if self._is_business_ai_related(title):
                                link_element = article.find('a', href=True)
                                if link_element:
                                    article_url = link_element['href']

                                    strategy = {
                                        'id': hashlib.md5(article_url.encode()).hexdigest()[:8],
                                        'title': title,
                                        'source': 'towards_datascience',
                                        'url': article_url,
                                        'strategy_type': 'data_science_monetization',
                                        'difficulty': 'intermediate',
                                        'potential_revenue': '$5,000-50,000/month',
                                        'time_to_implement': '2-4 weeks',
                                        'description': f"Data science strategy: {title}",
                                        'actionable_steps': [
                                            'Research the specific data science approach',
                                            'Build a prototype or proof of concept',
                                            'Create a business model around the solution',
                                            'Market to potential clients'
                                        ],
                                        'discovered_date': datetime.now().isoformat(),
                                        'implementation_score': random.uniform(0.7, 0.9)
                                    }
                                    strategies.append(strategy)

                        except Exception as e:
                            logger.debug(f"Failed to parse TDS article: {e}")

                    return strategies[:3]  # Return top 3

        except Exception as e:
            logger.error(f"Towards Data Science scraping failed: {e}")

        return self._generate_fallback_strategies('towards_datascience', 2)

    async def scrape_builtin_ai_startup(self) -> List[Dict]:
        """Scrape Built In for AI startup ideas"""
        try:
            url = "https://builtin.com/artificial-intelligence"

            async with self.session.get(url, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    strategies = []
                    # Find article links
                    articles = soup.find_all('article')[:4]

                    for article in articles:
                        try:
                            title_element = article.find('h2') or article.find('h3')
                            if not title_element:
                                continue

                            title = title_element.get_text(strip=True)

                            if self._is_startup_related(title):
                                link_element = article.find('a', href=True)
                                if link_element:
                                    article_url = link_element['href']
                                    if not article_url.startswith('http'):
                                        article_url = f"https://builtin.com{article_url}"

                                    strategy = {
                                        'id': hashlib.md5(article_url.encode()).hexdigest()[:8],
                                        'title': title,
                                        'source': 'builtin',
                                        'url': article_url,
                                        'strategy_type': 'ai_startup',
                                        'difficulty': 'advanced',
                                        'potential_revenue': '$10,000-100,000/month',
                                        'time_to_implement': '4-8 weeks',
                                        'description': f"AI startup opportunity: {title}",
                                        'actionable_steps': [
                                            'Validate the market need',
                                            'Build an MVP',
                                            'Secure initial funding or bootstrap',
                                            'Launch and iterate'
                                        ],
                                        'discovered_date': datetime.now().isoformat(),
                                        'implementation_score': random.uniform(0.6, 0.85)
                                    }
                                    strategies.append(strategy)

                        except Exception as e:
                            logger.debug(f"Failed to parse Built In article: {e}")

                    return strategies[:2]  # Return top 2

        except Exception as e:
            logger.error(f"Built In AI startup scraping failed: {e}")

        return self._generate_fallback_strategies('builtin', 1)

    async def _extract_strategy_from_medium(self, url: str, title: str) -> Optional[Dict]:
        """Extract detailed strategy from Medium article"""
        try:
            # For now, create strategy based on title analysis
            # TODO: Could scrape full article content for more details

            strategy_type = self._categorize_strategy(title)
            difficulty = self._assess_difficulty(title)
            revenue_potential = self._estimate_revenue(title, strategy_type)

            return {
                'id': hashlib.md5(url.encode()).hexdigest()[:8],
                'title': title,
                'source': 'medium',
                'url': url,
                'strategy_type': strategy_type,
                'difficulty': difficulty,
                'potential_revenue': revenue_potential,
                'time_to_implement': self._estimate_timeframe(difficulty),
                'description': f"AI monetization strategy from Medium: {title}",
                'actionable_steps': self._generate_action_steps(strategy_type),
                'discovered_date': datetime.now().isoformat(),
                'implementation_score': random.uniform(0.6, 0.9)
            }

        except Exception as e:
            logger.debug(f"Failed to extract strategy from {url}: {e}")
            return None

    async def _extract_strategy_from_hackernoon(self, url: str, title: str) -> Optional[Dict]:
        """Extract strategy from HackerNoon article"""
        strategy_type = self._categorize_strategy(title)

        return {
            'id': hashlib.md5(url.encode()).hexdigest()[:8],
            'title': title,
            'source': 'hackernoon',
            'url': url,
            'strategy_type': strategy_type,
            'difficulty': 'intermediate',
            'potential_revenue': '$3,000-30,000/month',
            'time_to_implement': '2-6 weeks',
            'description': f"Tech-focused AI strategy: {title}",
            'actionable_steps': self._generate_action_steps(strategy_type),
            'discovered_date': datetime.now().isoformat(),
            'implementation_score': random.uniform(0.7, 0.9)
        }

    async def _extract_strategy_from_devto(self, url: str, title: str) -> Optional[Dict]:
        """Extract strategy from Dev.to article"""
        strategy_type = self._categorize_strategy(title)

        return {
            'id': hashlib.md5(url.encode()).hexdigest()[:8],
            'title': title,
            'source': 'devto',
            'url': url,
            'strategy_type': strategy_type,
            'difficulty': 'beginner_to_intermediate',
            'potential_revenue': '$1,000-10,000/month',
            'time_to_implement': '1-4 weeks',
            'description': f"Developer-focused AI project: {title}",
            'actionable_steps': self._generate_action_steps(strategy_type),
            'discovered_date': datetime.now().isoformat(),
            'implementation_score': random.uniform(0.65, 0.85)
        }

    def _is_monetization_related(self, title: str) -> bool:
        """Check if title is related to monetization"""
        keywords = ['money', 'revenue', 'profit', 'business', 'monetize', 'earn', 'income', 'startup', 'saas', 'sell']
        return any(keyword in title.lower() for keyword in keywords)

    def _is_project_related(self, title: str) -> bool:
        """Check if title is related to buildable projects"""
        keywords = ['build', 'create', 'tutorial', 'guide', 'project', 'app', 'tool', 'api', 'chatbot']
        return any(keyword in title.lower() for keyword in keywords)

    def _is_business_ai_related(self, title: str) -> bool:
        """Check if title is AI business related"""
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'ml', 'chatgpt', 'gpt']
        business_keywords = ['business', 'startup', 'revenue', 'monetize', 'market']

        has_ai = any(keyword in title.lower() for keyword in ai_keywords)
        has_business = any(keyword in title.lower() for keyword in business_keywords)

        return has_ai and has_business

    def _is_startup_related(self, title: str) -> bool:
        """Check if title is startup related"""
        keywords = ['startup', 'entrepreneur', 'business', 'company', 'venture', 'funding']
        return any(keyword in title.lower() for keyword in keywords)

    def _categorize_strategy(self, title: str) -> str:
        """Categorize the strategy type"""
        title_lower = title.lower()

        if 'saas' in title_lower or 'software' in title_lower:
            return 'saas_development'
        elif 'chatbot' in title_lower or 'assistant' in title_lower:
            return 'ai_assistant'
        elif 'content' in title_lower or 'writing' in title_lower:
            return 'content_generation'
        elif 'api' in title_lower or 'service' in title_lower:
            return 'api_service'
        elif 'course' in title_lower or 'education' in title_lower:
            return 'educational_content'
        elif 'automation' in title_lower or 'tool' in title_lower:
            return 'automation_tool'
        else:
            return 'ai_application'

    def _assess_difficulty(self, title: str) -> str:
        """Assess implementation difficulty"""
        title_lower = title.lower()

        if 'beginner' in title_lower or 'simple' in title_lower or 'easy' in title_lower:
            return 'beginner'
        elif 'advanced' in title_lower or 'complex' in title_lower or 'enterprise' in title_lower:
            return 'advanced'
        else:
            return 'intermediate'

    def _estimate_revenue(self, title: str, strategy_type: str) -> str:
        """Estimate revenue potential"""
        revenue_ranges = {
            'saas_development': '$5,000-50,000/month',
            'ai_assistant': '$2,000-20,000/month',
            'content_generation': '$1,000-15,000/month',
            'api_service': '$3,000-30,000/month',
            'educational_content': '$2,000-25,000/month',
            'automation_tool': '$4,000-40,000/month',
            'ai_application': '$2,500-25,000/month'
        }

        return revenue_ranges.get(strategy_type, '$1,000-10,000/month')

    def _estimate_timeframe(self, difficulty: str) -> str:
        """Estimate implementation timeframe"""
        timeframes = {
            'beginner': '1-2 weeks',
            'intermediate': '2-4 weeks',
            'advanced': '4-8 weeks'
        }

        return timeframes.get(difficulty, '2-4 weeks')

    def _generate_action_steps(self, strategy_type: str) -> List[str]:
        """Generate actionable steps for strategy type"""
        step_templates = {
            'saas_development': [
                'Research market demand and competitors',
                'Design MVP with core AI features',
                'Build backend API and AI integration',
                'Create frontend interface',
                'Set up payment processing',
                'Launch beta and gather feedback'
            ],
            'ai_assistant': [
                'Define assistant scope and capabilities',
                'Set up OpenAI/Claude API integration',
                'Build conversation flow and context management',
                'Create deployment infrastructure',
                'Market to target audience'
            ],
            'content_generation': [
                'Identify content niche and audience',
                'Set up AI content generation pipeline',
                'Create quality control processes',
                'Build distribution channels',
                'Monetize through subscriptions or sales'
            ],
            'api_service': [
                'Design API endpoints and documentation',
                'Implement AI processing pipeline',
                'Set up authentication and rate limiting',
                'Create billing and usage tracking',
                'Market to developers and businesses'
            ],
            'educational_content': [
                'Research learning objectives and audience',
                'Create curriculum and lesson plans',
                'Develop interactive AI demos',
                'Build course platform or use existing',
                'Market and launch course'
            ],
            'automation_tool': [
                'Identify automation opportunities',
                'Design user-friendly interface',
                'Build AI-powered automation engine',
                'Create integration capabilities',
                'Launch and acquire customers'
            ]
        }

        return step_templates.get(strategy_type, [
            'Research the opportunity thoroughly',
            'Create a detailed implementation plan',
            'Build a minimum viable product',
            'Test with initial users',
            'Iterate and scale'
        ])

    def _deduplicate_strategies(self, strategies: List[Dict]) -> List[Dict]:
        """Remove duplicate strategies"""
        seen_titles = set()
        unique_strategies = []

        for strategy in strategies:
            title_lower = strategy['title'].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_strategies.append(strategy)

        return unique_strategies

    def _score_strategies(self, strategies: List[Dict]) -> List[Dict]:
        """Score and rank strategies"""
        for strategy in strategies:
            # Base score from implementation_score
            score = strategy.get('implementation_score', 0.5)

            # Bonus for certain strategy types
            strategy_type = strategy.get('strategy_type', '')
            if strategy_type in ['saas_development', 'api_service']:
                score += 0.1
            elif strategy_type in ['automation_tool', 'ai_assistant']:
                score += 0.05

            # Bonus for recent articles
            score += 0.05  # Recent discovery bonus

            strategy['final_score'] = min(0.99, score)

        # Sort by score
        return sorted(strategies, key=lambda x: x['final_score'], reverse=True)

    def _generate_fallback_strategies(self, source: str, count: int) -> List[Dict]:
        """Generate fallback strategies when scraping fails"""
        fallback_strategies = [
            {
                'title': 'AI-Powered Content Writing Service',
                'strategy_type': 'content_generation',
                'difficulty': 'beginner',
                'potential_revenue': '$2,000-15,000/month'
            },
            {
                'title': 'Custom ChatGPT Business Assistant',
                'strategy_type': 'ai_assistant',
                'difficulty': 'intermediate',
                'potential_revenue': '$3,000-25,000/month'
            },
            {
                'title': 'AI Automation Tools for Small Business',
                'strategy_type': 'automation_tool',
                'difficulty': 'intermediate',
                'potential_revenue': '$4,000-30,000/month'
            },
            {
                'title': 'AI-Enhanced SaaS Platform',
                'strategy_type': 'saas_development',
                'difficulty': 'advanced',
                'potential_revenue': '$5,000-50,000/month'
            }
        ]

        strategies = []
        for i, template in enumerate(fallback_strategies[:count]):
            strategy = {
                'id': hashlib.md5(f"{source}_fallback_{i}".encode()).hexdigest()[:8],
                'title': template['title'],
                'source': source,
                'url': f"https://example.com/{source}/fallback/{i}",
                'strategy_type': template['strategy_type'],
                'difficulty': template['difficulty'],
                'potential_revenue': template['potential_revenue'],
                'time_to_implement': self._estimate_timeframe(template['difficulty']),
                'description': f"Fallback AI monetization strategy: {template['title']}",
                'actionable_steps': self._generate_action_steps(template['strategy_type']),
                'discovered_date': datetime.now().isoformat(),
                'implementation_score': random.uniform(0.6, 0.8),
                'final_score': random.uniform(0.6, 0.8)
            }
            strategies.append(strategy)

        return strategies


# Synchronous wrapper for Django integration
def research_ai_monetization_sync() -> List[Dict]:
    """Synchronous wrapper for AI monetization research"""
    spider = AIMonetizationSpider()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        strategies = loop.run_until_complete(spider.research_all())
        logger.info(f"Found {len(strategies)} AI monetization strategies")
        return strategies
    finally:
        loop.close()


if __name__ == "__main__":
    # Test the spider
    print("🔍 Researching AI monetization strategies...")
    strategies = research_ai_monetization_sync()

    print(f"\n💡 Found {len(strategies)} strategies:")
    for strategy in strategies[:5]:  # Show top 5
        print(f"\n📈 {strategy['title']}")
        print(f"   Source: {strategy['source']}")
        print(f"   Type: {strategy['strategy_type']}")
        print(f"   Revenue: {strategy['potential_revenue']}")
        print(f"   Difficulty: {strategy['difficulty']}")
        print(f"   Score: {strategy.get('final_score', 0):.2f}")