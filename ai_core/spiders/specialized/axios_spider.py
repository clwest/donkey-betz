"""
Axios Spider - Concise Business & Tech News Intelligence
========================================================

Session 218: Specialized spider for Axios news coverage.
Known for "Smart Brevity" - concise, impactful news summaries.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class AxiosSpider(BaseIntelligenceSpider):
    """Axios news spider - concise business and tech news"""

    # RSS Feed URLs for different Axios sections
    RSS_FEEDS = {
        'main': 'https://api.axios.com/feed/',
        'technology': 'https://api.axios.com/feed/technology',
        'business': 'https://api.axios.com/feed/business',
        'markets': 'https://api.axios.com/feed/markets',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.news_categories = {
            'technology': ['tech', 'software', 'app', 'digital', 'internet', 'cyber'],
            'ai': ['ai', 'artificial intelligence', 'chatgpt', 'openai', 'machine learning', 'llm'],
            'business': ['business', 'company', 'corporate', 'ceo', 'executive'],
            'markets': ['market', 'stock', 'trading', 'investor', 'wall street'],
            'policy': ['policy', 'regulation', 'government', 'congress', 'bill', 'law'],
            'climate': ['climate', 'energy', 'renewable', 'ev', 'electric', 'sustainability'],
            'healthcare': ['health', 'medical', 'pharma', 'drug', 'fda', 'hospital'],
        }

        self.impact_indicators = {
            'high': ['breaking', 'exclusive', 'first', 'major', 'unprecedented'],
            'medium': ['significant', 'important', 'notable', 'new'],
            'low': ['update', 'minor', 'slight'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from Axios"""
        try:
            all_articles = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:12]:
                            article = {
                                'title': entry.get('title', ''),
                                'summary': entry.get('summary', entry.get('description', '')),
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'author': entry.get('author', 'Axios'),
                                'feed_source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'articles': all_articles, 'source': 'axios'}

        except Exception as e:
            self.logger.error(f"Error fetching Axios data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Axios articles"""
        try:
            articles = raw_data.get('articles', [])
            processed_articles = []

            for article in articles:
                processed = self._process_article(article)
                if processed:
                    processed_articles.append(processed)

            # Generate insights (Axios style - brief and impactful)
            insights = self._generate_smart_brevity_insights(processed_articles)

            content = {
                'articles': processed_articles,
                'insights': insights,
                'top_stories': self._get_top_stories(processed_articles),
                'category_summary': self._summarize_by_category(processed_articles),
                'market_pulse': self._extract_market_pulse(processed_articles),
            }

            quality_score = min(1.0, len(processed_articles) / 25 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='axios.com',
                data_type='business_news',
                content=content,
                metadata={
                    'article_count': len(processed_articles),
                    'source': 'axios',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['business', 'tech', 'policy', 'markets', 'news'],
                target_agents=['research_agent', 'trend_analysis_agent', 'market_agent'],
                target_advisors=['business_strategist', 'market_analyst']
            )

        except Exception as e:
            self.logger.error(f"Error processing Axios data: {e}")
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
                'tone': 'positive' if blob.sentiment.polarity > 0.1 else 'negative' if blob.sentiment.polarity < -0.1 else 'neutral'
            }

            # Categorize
            categories = []
            for cat, keywords in self.news_categories.items():
                if any(kw in text for kw in keywords):
                    categories.append(cat)

            # Determine impact level
            impact = 'low'
            for level, indicators in self.impact_indicators.items():
                if any(ind in text for ind in indicators):
                    impact = level
                    break

            # Extract "Why it matters" (Axios signature)
            why_it_matters = self._extract_why_it_matters(title, summary)

            return {
                'title': title,
                'summary': summary[:400] if summary else '',
                'link': article.get('link', ''),
                'published': article.get('published', ''),
                'author': article.get('author', ''),
                'sentiment': sentiment,
                'categories': categories or ['general'],
                'impact_level': impact,
                'why_it_matters': why_it_matters,
                'feed_source': article.get('feed_source', ''),
            }

        except Exception as e:
            self.logger.warning(f"Error processing article: {e}")
            return None

    def _extract_why_it_matters(self, title: str, summary: str) -> str:
        """Generate a 'Why it matters' summary (Axios style)"""
        text = f"{title}. {summary}"

        # Simple extraction - first sentence after any "why it matters" or "the big picture"
        lower_text = text.lower()

        for trigger in ['why it matters', 'the big picture', 'what to watch', 'bottom line']:
            if trigger in lower_text:
                idx = lower_text.find(trigger)
                remaining = text[idx:]
                # Get the sentence after the trigger
                sentences = remaining.split('.')
                if len(sentences) > 1:
                    return sentences[1].strip()[:200]

        # Default: return first 100 chars of summary
        return summary[:100] + '...' if len(summary) > 100 else summary

    def _generate_smart_brevity_insights(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Axios-style 'Smart Brevity' insights"""
        if not articles:
            return {}

        # Categorize sentiment
        positive = [a for a in articles if a.get('sentiment', {}).get('tone') == 'positive']
        negative = [a for a in articles if a.get('sentiment', {}).get('tone') == 'negative']

        # Find high-impact stories
        high_impact = [a for a in articles if a.get('impact_level') == 'high']

        return {
            'the_big_picture': f"{len(articles)} stories tracked. Sentiment: {len(positive)} positive, {len(negative)} negative.",
            'what_to_watch': [a.get('title') for a in high_impact[:3]],
            'category_focus': self._get_dominant_category(articles),
            'mood': 'optimistic' if len(positive) > len(negative) else 'cautious' if len(negative) > len(positive) else 'mixed',
        }

    def _get_dominant_category(self, articles: List[Dict[str, Any]]) -> str:
        """Get the most common category"""
        cat_counts = {}
        for article in articles:
            for cat in article.get('categories', []):
                cat_counts[cat] = cat_counts.get(cat, 0) + 1

        if cat_counts:
            return max(cat_counts.items(), key=lambda x: x[1])[0]
        return 'general'

    def _get_top_stories(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get top stories by impact"""
        # Sort by impact level
        impact_order = {'high': 0, 'medium': 1, 'low': 2}
        sorted_articles = sorted(articles, key=lambda x: impact_order.get(x.get('impact_level', 'low'), 2))

        return [
            {
                'title': a.get('title'),
                'why_it_matters': a.get('why_it_matters'),
                'impact': a.get('impact_level'),
                'link': a.get('link'),
            }
            for a in sorted_articles[:5]
        ]

    def _summarize_by_category(self, articles: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Summarize articles by category"""
        summaries = {}

        for article in articles:
            for cat in article.get('categories', ['general']):
                if cat not in summaries:
                    summaries[cat] = {'count': 0, 'sentiment_avg': 0, 'titles': []}
                summaries[cat]['count'] += 1
                summaries[cat]['sentiment_avg'] += article.get('sentiment', {}).get('polarity', 0)
                if len(summaries[cat]['titles']) < 3:
                    summaries[cat]['titles'].append(article.get('title'))

        # Calculate averages
        for cat in summaries:
            if summaries[cat]['count'] > 0:
                summaries[cat]['sentiment_avg'] /= summaries[cat]['count']
                summaries[cat]['sentiment_avg'] = round(summaries[cat]['sentiment_avg'], 2)

        return summaries

    def _extract_market_pulse(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract market-related insights"""
        market_articles = [a for a in articles if 'markets' in a.get('categories', [])]

        if not market_articles:
            return {'available': False}

        return {
            'available': True,
            'article_count': len(market_articles),
            'sentiment': sum(a.get('sentiment', {}).get('polarity', 0) for a in market_articles) / len(market_articles),
            'top_headlines': [a.get('title') for a in market_articles[:3]],
        }

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['business', 'tech', 'market', 'policy', 'axios']
