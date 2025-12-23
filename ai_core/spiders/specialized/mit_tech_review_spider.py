"""
MIT Technology Review Spider - Deep Tech & Research Intelligence
================================================================

Session 534: Simplified to work with spider network interface.
Aggregates breakthrough tech and research news via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class MITTechReviewSpider:
    """MIT Technology Review spider - deep tech research and breakthroughs"""

    name = "mit_tech_review"

    # MIT Tech Review and research RSS feeds
    RSS_FEEDS = {
        'main': 'https://www.technologyreview.com/feed/',
        'ai': 'https://www.technologyreview.com/topic/artificial-intelligence/feed/',
        'computing': 'https://www.technologyreview.com/topic/computing/feed/',
        'biotech': 'https://www.technologyreview.com/topic/biotechnology/feed/',
        'climate': 'https://www.technologyreview.com/topic/climate-change/feed/',
    }

    # Research domains
    DOMAINS = [
        ('AI & ML', 'ai_ml', 'Artificial intelligence and machine learning.'),
        ('Quantum', 'quantum', 'Quantum computing and physics.'),
        ('Biotech', 'biotech', 'Biotechnology and genomics.'),
        ('Climate Tech', 'climate', 'Climate and clean energy tech.'),
        ('Robotics', 'robotics', 'Robotics and automation.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.research_domains = {
            'ai_ml': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network', 'gpt', 'llm', 'transformer'],
            'quantum': ['quantum', 'qubit', 'quantum computing', 'superposition', 'entanglement'],
            'biotech': ['crispr', 'gene', 'genomic', 'mrna', 'biotech', 'synthetic biology', 'protein'],
            'climate': ['climate', 'carbon', 'renewable', 'solar', 'fusion', 'battery', 'ev'],
            'robotics': ['robot', 'autonomous', 'drone', 'humanoid', 'automation'],
            'space': ['space', 'rocket', 'satellite', 'mars', 'moon', 'starship', 'spacex'],
        }
        self.impact_keywords = {
            'breakthrough': ['breakthrough', 'revolutionary', 'first-ever', 'paradigm shift', 'game-changing'],
            'significant': ['significant', 'major', 'important', 'notable', 'key'],
            'emerging': ['emerging', 'promising', 'potential', 'early-stage', 'developing'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch tech research and breakthrough content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of research content dictionaries
        """
        all_items = []
        seen_urls = set()

        # Fetch from RSS feeds
        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name)
                for item in items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # Add domain links
        try:
            domains = self._get_domain_links()
            all_items.extend(domains)
        except Exception as e:
            logger.warning(f"Error getting research domains: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"MIT Tech Review spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from research RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:12]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:500]

                # Detect research domain and impact
                text = f"{title} {summary}".lower()
                domains = self._detect_domains(text)
                impact_level = self._detect_impact_level(text)
                is_ai_related = 'ai_ml' in domains
                is_breakthrough = impact_level == 'breakthrough'

                # Extract tags from feed entry
                entry_tags = []
                if hasattr(entry, 'tags'):
                    entry_tags = [tag.term for tag in entry.tags if hasattr(tag, 'term')][:5]

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', 'MIT Technology Review'),
                    'research_domains': domains,
                    'category': domains[0] if domains else 'general',
                    'impact_level': impact_level,
                    'is_ai_related': is_ai_related,
                    'is_breakthrough': is_breakthrough,
                    'entry_tags': entry_tags,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'research_innovation',
                    'platform': 'mit_tech_review',
                    'tags': ['mit_tech_review', 'research'] + domains[:2],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_domains(self, text: str) -> List[str]:
        """Detect research domains from text."""
        domains = []
        for domain, keywords in self.research_domains.items():
            if any(kw in text for kw in keywords):
                domains.append(domain)
        return domains if domains else ['general']

    def _detect_impact_level(self, text: str) -> str:
        """Detect impact level from text."""
        for level, keywords in self.impact_keywords.items():
            if any(kw in text for kw in keywords):
                return level
        return 'emerging'

    def _get_domain_links(self) -> List[Dict[str, Any]]:
        """Return research domain links."""
        return [
            {
                'title': f"MIT Tech Review: {name}",
                'url': f'https://www.technologyreview.com/topic/{slug}/',
                'link': f'https://www.technologyreview.com/topic/{slug}/',
                'summary': desc,
                'description': desc,
                'research_domains': [slug],
                'category': slug,
                'source': 'MIT Tech Review',
                'data_type': 'research_domain',
                'platform': 'mit_tech_review',
                'tags': ['mit_tech_review', 'research', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.DOMAINS
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('AI Breakthroughs', 'ai_ml', 'Artificial intelligence advances.'),
            ('Quantum Computing', 'quantum', 'Quantum technology progress.'),
            ('Biotech Research', 'biotech', 'Biotechnology developments.'),
            ('Climate Solutions', 'climate', 'Clean energy innovations.'),
            ('Robotics & Automation', 'robotics', 'Robotics breakthroughs.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.technologyreview.com/topic/{category}/',
                'link': f'https://www.technologyreview.com/topic/{category}/',
                'summary': desc,
                'description': desc,
                'research_domains': [category],
                'category': category,
                'source': 'MIT Tech Review',
                'data_type': 'research_topic',
                'platform': 'mit_tech_review',
                'tags': ['mit_tech_review', 'research', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
