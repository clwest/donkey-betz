"""
MIT Technology Review Spider - Deep Tech & Research Intelligence
================================================================

Session 218: Specialized spider for MIT Technology Review.
Focuses on breakthrough technologies, AI research, and emerging tech.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class MITTechReviewSpider(BaseIntelligenceSpider):
    """MIT Technology Review spider - deep tech research and breakthroughs"""

    # RSS Feed URLs
    RSS_FEEDS = {
        'main': 'https://www.technologyreview.com/feed/',
        'ai': 'https://www.technologyreview.com/topic/artificial-intelligence/feed/',
        'computing': 'https://www.technologyreview.com/topic/computing/feed/',
        'biotech': 'https://www.technologyreview.com/topic/biotechnology/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.research_domains = {
            'ai_ml': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network', 'gpt', 'llm', 'transformer'],
            'quantum': ['quantum', 'qubit', 'quantum computing', 'superposition', 'entanglement'],
            'biotech': ['crispr', 'gene', 'genomic', 'mrna', 'biotech', 'synthetic biology', 'protein'],
            'climate_tech': ['climate', 'carbon', 'renewable', 'solar', 'fusion', 'battery', 'ev'],
            'robotics': ['robot', 'autonomous', 'drone', 'humanoid', 'automation'],
            'space': ['space', 'rocket', 'satellite', 'mars', 'moon', 'starship', 'spacex'],
            'materials': ['material', 'graphene', 'semiconductor', 'chip', 'nanomaterial'],
            'computing': ['computing', 'processor', 'chip', 'memory', 'algorithm'],
        }

        self.impact_levels = {
            'breakthrough': ['breakthrough', 'revolutionary', 'first-ever', 'paradigm shift', 'game-changing'],
            'significant': ['significant', 'major', 'important', 'notable', 'key'],
            'emerging': ['emerging', 'promising', 'potential', 'early-stage', 'developing'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from MIT Technology Review"""
        try:
            all_articles = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:12]:
                            # Extract content
                            content = ''
                            if hasattr(entry, 'content') and entry.content:
                                content = entry.content[0].get('value', '')
                            elif hasattr(entry, 'summary'):
                                content = entry.summary

                            article = {
                                'title': entry.get('title', ''),
                                'summary': content[:600] if content else '',
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'author': entry.get('author', 'MIT Technology Review'),
                                'tags': [tag.term for tag in entry.get('tags', [])] if hasattr(entry, 'tags') else [],
                                'feed_source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'articles': all_articles, 'source': 'mit_tech_review'}

        except Exception as e:
            self.logger.error(f"Error fetching MIT Tech Review data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process MIT Technology Review articles"""
        try:
            articles = raw_data.get('articles', [])
            processed_articles = []

            for article in articles:
                processed = self._process_article(article)
                if processed:
                    processed_articles.append(processed)

            # Generate research insights
            insights = self._generate_research_insights(processed_articles)

            content = {
                'articles': processed_articles,
                'insights': insights,
                'breakthroughs': self._extract_breakthroughs(processed_articles),
                'research_domains': self._analyze_research_domains(processed_articles),
                'emerging_tech': self._identify_emerging_tech(processed_articles),
                'ai_developments': self._extract_ai_developments(processed_articles),
            }

            quality_score = min(1.0, len(processed_articles) / 25 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='technologyreview.com',
                data_type='research_innovation',
                content=content,
                metadata={
                    'article_count': len(processed_articles),
                    'source': 'mit_tech_review',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                    'breakthrough_count': len([a for a in processed_articles if a.get('impact_level') == 'breakthrough']),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['research', 'innovation', 'ai', 'breakthrough', 'deep_tech'],
                target_agents=['research_agent', 'trend_analysis_agent', 'innovation_agent'],
                target_advisors=['research_advisor', 'tech_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing MIT Tech Review data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual article"""
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()

            # Sentiment analysis
            blob = TextBlob(f"{title} {summary}")
            sentiment = {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity,
                'tone': 'optimistic' if blob.sentiment.polarity > 0.1 else 'cautious' if blob.sentiment.polarity < -0.1 else 'neutral'
            }

            # Identify research domains
            domains = []
            for domain, keywords in self.research_domains.items():
                if any(kw in text for kw in keywords):
                    domains.append(domain)

            # Determine impact level
            impact_level = 'emerging'
            for level, keywords in self.impact_levels.items():
                if any(kw in text for kw in keywords):
                    impact_level = level
                    break

            # Extract key concepts
            key_concepts = self._extract_key_concepts(title, summary)

            # Check for specific indicators
            is_ai_related = 'ai_ml' in domains
            is_breakthrough = impact_level == 'breakthrough'
            mentions_research = any(word in text for word in ['research', 'study', 'scientists', 'researchers', 'paper', 'published'])

            return {
                'title': title,
                'summary': summary[:500] if summary else '',
                'link': article.get('link', ''),
                'published': article.get('published', ''),
                'author': article.get('author', ''),
                'sentiment': sentiment,
                'research_domains': domains or ['general'],
                'impact_level': impact_level,
                'key_concepts': key_concepts,
                'is_ai_related': is_ai_related,
                'is_breakthrough': is_breakthrough,
                'mentions_research': mentions_research,
                'tags': article.get('tags', []),
            }

        except Exception as e:
            self.logger.warning(f"Error processing article: {e}")
            return None

    def _extract_key_concepts(self, title: str, summary: str) -> List[str]:
        """Extract key technical concepts"""
        import re

        text = f"{title} {summary}"
        concepts = []

        # Technical terms pattern (capitalized words, acronyms)
        patterns = [
            r'\b([A-Z]{2,5})\b',  # Acronyms like AI, ML, GPT
            r'\b([A-Z][a-z]+(?:Net|AI|ML|Tech|Bot))\b',  # Technical product names
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            concepts.extend(matches)

        # Filter common false positives
        false_positives = {'The', 'MIT', 'This', 'That', 'What', 'Why', 'How', 'When'}
        concepts = [c for c in concepts if c not in false_positives]

        return list(set(concepts))[:8]

    def _generate_research_insights(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate research-focused insights"""
        if not articles:
            return {}

        breakthroughs = [a for a in articles if a.get('is_breakthrough')]
        ai_articles = [a for a in articles if a.get('is_ai_related')]
        research_articles = [a for a in articles if a.get('mentions_research')]

        # Count domains
        domain_counts = {}
        for article in articles:
            for domain in article.get('research_domains', []):
                domain_counts[domain] = domain_counts.get(domain, 0) + 1

        hot_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            'total_articles': len(articles),
            'breakthrough_count': len(breakthroughs),
            'ai_coverage': len(ai_articles),
            'research_coverage': len(research_articles),
            'hot_domains': [d[0] for d in hot_domains],
            'innovation_pulse': 'high' if len(breakthroughs) >= 2 else 'moderate' if len(breakthroughs) >= 1 else 'steady',
            'overall_sentiment': self._calculate_overall_sentiment(articles),
        }

    def _calculate_overall_sentiment(self, articles: List[Dict[str, Any]]) -> str:
        """Calculate overall sentiment"""
        if not articles:
            return 'neutral'

        avg = sum(a.get('sentiment', {}).get('polarity', 0) for a in articles) / len(articles)
        return 'optimistic' if avg > 0.1 else 'cautious' if avg < -0.1 else 'neutral'

    def _extract_breakthroughs(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract breakthrough articles"""
        breakthroughs = []
        for article in articles:
            if article.get('is_breakthrough') or article.get('impact_level') == 'breakthrough':
                breakthroughs.append({
                    'title': article.get('title'),
                    'domains': article.get('research_domains'),
                    'key_concepts': article.get('key_concepts'),
                    'link': article.get('link'),
                })
        return breakthroughs[:5]

    def _analyze_research_domains(self, articles: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze coverage by research domain"""
        domains = {}

        for article in articles:
            for domain in article.get('research_domains', ['general']):
                if domain not in domains:
                    domains[domain] = {'count': 0, 'sentiment_sum': 0, 'breakthroughs': 0}
                domains[domain]['count'] += 1
                domains[domain]['sentiment_sum'] += article.get('sentiment', {}).get('polarity', 0)
                if article.get('is_breakthrough'):
                    domains[domain]['breakthroughs'] += 1

        # Calculate averages
        for domain in domains:
            if domains[domain]['count'] > 0:
                domains[domain]['avg_sentiment'] = round(domains[domain]['sentiment_sum'] / domains[domain]['count'], 2)
            del domains[domain]['sentiment_sum']

        return domains

    def _identify_emerging_tech(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify emerging technologies"""
        emerging = []
        for article in articles:
            if article.get('impact_level') == 'emerging':
                emerging.append({
                    'title': article.get('title'),
                    'domains': article.get('research_domains'),
                    'sentiment': article.get('sentiment', {}).get('tone'),
                    'link': article.get('link'),
                })
        return emerging[:8]

    def _extract_ai_developments(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract AI-specific developments"""
        ai_devs = []
        for article in articles:
            if article.get('is_ai_related'):
                ai_devs.append({
                    'title': article.get('title'),
                    'key_concepts': article.get('key_concepts'),
                    'impact_level': article.get('impact_level'),
                    'sentiment': article.get('sentiment', {}).get('tone'),
                    'link': article.get('link'),
                })
        return ai_devs[:10]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['research', 'breakthrough', 'ai', 'technology', 'innovation', 'science']
