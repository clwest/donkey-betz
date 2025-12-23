"""
Horse Racing Spider - Racing & Betting Intelligence
====================================================

Session 534: Simplified to work with spider network interface.
Aggregates horse racing content from RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class HorseRacingSpider:
    """Horse racing spider - racing news, betting tips, and track conditions"""

    name = "horse_racing"

    # Horse racing RSS feeds
    RSS_FEEDS = {
        'bloodhorse': 'https://www.bloodhorse.com/rss/headlines.xml',
        'horse_racing_nation': 'https://www.horseracingnation.com/rss',
        'paulick_report': 'https://www.paulickreport.com/feed/',
        'tdn': 'https://www.thoroughbreddailynews.com/feed/',
    }

    # Reddit horse racing (using RSS)
    REDDIT_FEEDS = {
        'r_horseracing': 'https://www.reddit.com/r/horseracing/.rss',
    }

    # Racing categories
    CATEGORIES = [
        ('Derby', 'derby', 'Kentucky Derby and related races.'),
        ('Stakes', 'stakes', 'Stakes races and graded events.'),
        ('Handicapping', 'handicapping', 'Handicapping tips and analysis.'),
        ('Breeding', 'breeding', 'Bloodlines and breeding news.'),
        ('Industry', 'industry', 'Industry news and regulations.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.racing_keywords = {
            'positive': ['favorite', 'strong', 'fast', 'winning', 'value', 'hot', 'sharp'],
            'negative': ['slow', 'weak', 'injured', 'cold', 'avoid', 'scratch'],
            'track_conditions': ['fast', 'muddy', 'sloppy', 'good', 'yielding', 'soft', 'heavy'],
        }
        self.racing_topics = {
            'derby': ['derby', 'kentucky derby', 'preakness', 'belmont', 'triple crown'],
            'stakes': ['stakes', 'graded', 'grade 1', 'grade 2', 'grade 3', 'breeders cup'],
            'handicapping': ['handicap', 'pick', 'bet', 'tip', 'value', 'longshot', 'odds'],
            'breeding': ['breed', 'sire', 'dam', 'bloodline', 'stud', 'foal'],
            'industry': ['racing', 'track', 'jockey', 'trainer', 'owner', 'purse'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch horse racing content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of racing content dictionaries
        """
        all_items = []
        seen_urls = set()

        # Fetch from racing RSS feeds
        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name)
                for item in items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # Fetch from Reddit RSS
        for feed_name, feed_url in self.REDDIT_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name)
                for item in items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # Add category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting racing categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Horse racing spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from horse racing RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:15]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:500]

                # Detect racing topic
                text = f"{title} {summary}".lower()
                topic = self._detect_topic(text)
                track_conditions = self._extract_track_conditions(text)
                sentiment = self._analyze_sentiment(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'topic': topic,
                    'category': topic,
                    'track_conditions': track_conditions,
                    'sentiment': sentiment,
                    'is_betting_tip': 'handicapping' in topic,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'horse_racing',
                    'platform': 'horse_racing',
                    'tags': ['horse_racing', 'betting', topic],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_topic(self, text: str) -> str:
        """Detect racing topic from text."""
        for topic, keywords in self.racing_topics.items():
            if any(kw in text for kw in keywords):
                return topic
        return 'general'

    def _extract_track_conditions(self, text: str) -> List[str]:
        """Extract track condition mentions."""
        conditions = []
        for condition in self.racing_keywords['track_conditions']:
            if condition in text:
                conditions.append(condition)
        return list(set(conditions))

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze racing sentiment from text."""
        positive_count = sum(1 for word in self.racing_keywords['positive'] if word in text)
        negative_count = sum(1 for word in self.racing_keywords['negative'] if word in text)

        if positive_count > negative_count * 1.5:
            return 'positive'
        elif negative_count > positive_count * 1.5:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return racing category links."""
        return [
            {
                'title': f"Racing: {name}",
                'url': f'https://www.bloodhorse.com/{slug}',
                'link': f'https://www.bloodhorse.com/{slug}',
                'summary': desc,
                'description': desc,
                'topic': slug,
                'category': slug,
                'source': 'Horse Racing',
                'data_type': 'racing_category',
                'platform': 'horse_racing',
                'tags': ['horse_racing', 'betting', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Derby Coverage', 'derby', 'Triple Crown and major stakes.'),
            ('Stakes Races', 'stakes', 'Graded stakes coverage.'),
            ('Handicapping Tips', 'handicapping', 'Expert picks and analysis.'),
            ('Breeding News', 'breeding', 'Bloodlines and foal news.'),
            ('Industry Updates', 'industry', 'Racing industry news.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.bloodhorse.com/{category}',
                'link': f'https://www.bloodhorse.com/{category}',
                'summary': desc,
                'description': desc,
                'topic': category,
                'category': category,
                'source': 'Horse Racing',
                'data_type': 'racing_topic',
                'platform': 'horse_racing',
                'tags': ['horse_racing', 'betting', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
