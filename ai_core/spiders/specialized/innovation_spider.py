"""
Innovation Tracking Spider - Disruptive Tech Intelligence
===========================================================

Session 534: Simplified to work with spider network interface.
Aggregates innovation and disruptive tech content via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class InnovationTrackingSpider:
    """Innovation spider - disruptive tech, research, and breakthrough tracking"""

    name = "innovation"

    # Innovation and research RSS feeds
    RSS_FEEDS = {
        'mit_tech_review': 'https://www.technologyreview.com/feed/',
        'wired_science': 'https://www.wired.com/feed/category/science/latest/rss',
        'ars_technica': 'https://feeds.arstechnica.com/arstechnica/index',
        'singularity_hub': 'https://singularityhub.com/feed/',
        'ieee_spectrum': 'https://spectrum.ieee.org/feeds/feed.rss',
    }

    # ArXiv RSS feeds for research papers
    ARXIV_FEEDS = {
        'arxiv_ai': 'http://export.arxiv.org/rss/cs.AI',
        'arxiv_ml': 'http://export.arxiv.org/rss/cs.LG',
    }

    # Innovation domains
    DOMAINS = [
        ('AI & ML', 'ai_ml', 'Artificial intelligence and machine learning.'),
        ('Robotics', 'robotics', 'Robotics and automation.'),
        ('Biotech', 'biotech', 'Biotechnology and genomics.'),
        ('Quantum', 'quantum', 'Quantum computing and physics.'),
        ('Clean Energy', 'clean_energy', 'Renewable energy and sustainability.'),
        ('Space Tech', 'space', 'Space exploration and technology.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.innovation_domains = {
            'ai_ml': ['ai', 'machine learning', 'neural', 'gpt', 'llm', 'deep learning'],
            'robotics': ['robot', 'automation', 'autonomous', 'drone', 'self-driving'],
            'biotech': ['biotech', 'genomics', 'crispr', 'gene', 'dna', 'cell therapy'],
            'quantum': ['quantum', 'qubit', 'superposition', 'entanglement'],
            'clean_energy': ['solar', 'wind', 'battery', 'ev', 'electric', 'renewable'],
            'space': ['space', 'rocket', 'satellite', 'mars', 'moon', 'starship'],
            'blockchain': ['blockchain', 'crypto', 'web3', 'defi', 'nft'],
        }
        self.breakthrough_keywords = [
            'breakthrough', 'revolutionary', 'disruptive', 'novel', 'unprecedented',
            'first-time', 'groundbreaking', 'paradigm-shift', 'game-changing'
        ]

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch innovation content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of innovation content dictionaries
        """
        all_items = []
        seen_urls = set()

        # Fetch from innovation RSS feeds
        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name)
                for item in items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # Fetch from ArXiv RSS feeds
        for feed_name, feed_url in self.ARXIV_FEEDS.items():
            try:
                items = self._fetch_arxiv_rss(feed_url, feed_name)
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
            logger.warning(f"Error getting innovation domains: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Innovation spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from innovation RSS feed."""
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

                # Detect innovation domain
                text = f"{title} {summary}".lower()
                domain = self._detect_domain(text)
                is_breakthrough = self._is_breakthrough(text)
                breakthrough_score = self._calculate_breakthrough_score(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'domain': domain,
                    'category': domain,
                    'is_breakthrough': is_breakthrough,
                    'breakthrough_score': breakthrough_score,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'innovation_news',
                    'platform': 'innovation',
                    'tags': ['innovation', 'technology', domain],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _fetch_arxiv_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch research papers from ArXiv RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:10]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:600]

                # Extract authors
                authors = []
                if hasattr(entry, 'authors'):
                    authors = [a.get('name', '') for a in entry.authors[:5]]

                # Detect domain and breakthrough potential
                text = f"{title} {summary}".lower()
                domain = self._detect_domain(text)
                breakthrough_score = self._calculate_breakthrough_score(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'authors': authors,
                    'domain': domain,
                    'category': 'research',
                    'is_research_paper': True,
                    'breakthrough_score': breakthrough_score,
                    'source': 'ArXiv',
                    'data_type': 'research_paper',
                    'platform': 'innovation',
                    'tags': ['innovation', 'research', 'arxiv', domain],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing ArXiv RSS: {e}")

        return items

    def _detect_domain(self, text: str) -> str:
        """Detect innovation domain from text."""
        for domain, keywords in self.innovation_domains.items():
            if any(kw in text for kw in keywords):
                return domain
        return 'general'

    def _is_breakthrough(self, text: str) -> bool:
        """Check if content describes a breakthrough."""
        return any(kw in text for kw in self.breakthrough_keywords)

    def _calculate_breakthrough_score(self, text: str) -> float:
        """Calculate breakthrough potential score."""
        score = 0.0

        # Breakthrough keywords
        for keyword in self.breakthrough_keywords:
            if keyword in text:
                score += 0.1

        # Performance improvements
        improvement_patterns = [
            r'(\d+)%?\s*improvement',
            r'(\d+)x\s*faster',
            r'state.of.the.art',
            r'outperform',
        ]
        for pattern in improvement_patterns:
            if re.search(pattern, text):
                score += 0.1

        return min(1.0, score)

    def _get_domain_links(self) -> List[Dict[str, Any]]:
        """Return innovation domain links."""
        return [
            {
                'title': f"Innovation: {name}",
                'url': f'https://www.technologyreview.com/topic/{slug}/',
                'link': f'https://www.technologyreview.com/topic/{slug}/',
                'summary': desc,
                'description': desc,
                'domain': slug,
                'category': slug,
                'source': 'Innovation',
                'data_type': 'innovation_domain',
                'platform': 'innovation',
                'tags': ['innovation', 'technology', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.DOMAINS
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('AI Breakthroughs', 'ai_ml', 'AI and machine learning advances.'),
            ('Robotics Innovation', 'robotics', 'Robotics and automation news.'),
            ('Biotech Research', 'biotech', 'Biotechnology developments.'),
            ('Quantum Computing', 'quantum', 'Quantum technology progress.'),
            ('Clean Energy Tech', 'clean_energy', 'Renewable energy innovations.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.technologyreview.com/topic/{category}/',
                'link': f'https://www.technologyreview.com/topic/{category}/',
                'summary': desc,
                'description': desc,
                'domain': category,
                'category': category,
                'source': 'Innovation',
                'data_type': 'innovation_topic',
                'platform': 'innovation',
                'tags': ['innovation', 'technology', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
