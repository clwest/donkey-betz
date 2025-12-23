"""
SecurityWeek Spider - Cybersecurity & Infosec Intelligence
============================================================

Session 534: Simplified to work with spider network interface.
SecurityWeek provides cybersecurity news via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class SecurityWeekSpider:
    """SecurityWeek spider - cybersecurity and infosec news via RSS"""

    name = "securityweek"

    # Note: Main feed may be blocked, use feedburner as fallback
    RSS_FEEDS = {
        'main': 'https://feeds.feedburner.com/securityweek',
        'alt': 'https://www.securityweek.com/feed/',
    }

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch news articles from SecurityWeek RSS feeds.

        Args:
            max_results: Maximum number of articles to fetch

        Returns:
            List of article dictionaries
        """
        all_articles = []
        seen_urls = set()

        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:30]:
                    url = entry.get('link', '')

                    # Skip duplicates
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    title = entry.get('title', '')
                    if not title:
                        continue

                    summary = entry.get('summary', entry.get('description', ''))
                    # Clean HTML from summary
                    if summary:
                        summary = re.sub(r'<[^>]+>', '', summary)[:500]

                    # Determine severity based on title/summary
                    severity = self._assess_severity(f"{title} {summary}".lower())

                    article = {
                        'title': title,
                        'url': url,
                        'summary': summary,
                        'description': summary,
                        'published': entry.get('published', ''),
                        'author': entry.get('author', 'SecurityWeek'),
                        'category': 'cybersecurity',
                        'source': 'SecurityWeek',
                        'data_type': 'security_news',
                        'severity': severity,
                        'tags': ['cybersecurity', 'infosec', 'security'],
                        'timestamp': datetime.now().isoformat(),
                    }
                    all_articles.append(article)

                    if len(all_articles) >= max_results:
                        break

            except Exception as e:
                logger.warning(f"Error fetching SecurityWeek {feed_name} feed: {e}")
                continue

            if len(all_articles) >= max_results:
                break

        # If RSS feeds are blocked/empty, return curated topics
        if len(all_articles) == 0:
            all_articles = self._get_curated_topics()

        logger.info(f"SecurityWeek spider collected {len(all_articles)} articles")
        return all_articles[:max_results]

    def _assess_severity(self, text: str) -> str:
        """Assess security severity from text."""
        critical_terms = ['critical', 'zero-day', 'actively exploited', 'emergency', 'widespread']
        high_terms = ['high severity', 'major breach', 'millions affected', 'ransomware attack']
        medium_terms = ['vulnerability', 'security flaw', 'patch available']

        if any(term in text for term in critical_terms):
            return 'critical'
        elif any(term in text for term in high_terms):
            return 'high'
        elif any(term in text for term in medium_terms):
            return 'medium'
        return 'informational'

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated security topics when RSS fails."""
        topics = [
            ('Critical Vulnerabilities', 'vulnerabilities', 'CVE tracking, zero-days, and critical security flaws.'),
            ('Data Breach Reports', 'breaches', 'Major data breaches, leak notifications, and incident reports.'),
            ('Ransomware Threats', 'ransomware', 'Ransomware gang activity, attacks, and mitigation strategies.'),
            ('Nation-State Cyber Activity', 'apt', 'APT groups, cyber espionage, and nation-state threats.'),
            ('Cloud Security', 'cloud', 'Cloud misconfiguration, AWS/Azure/GCP security issues.'),
            ('Identity & Access', 'iam', 'Identity security, MFA, zero trust architecture.'),
            ('Security Startup Funding', 'startups', 'Cybersecurity startup funding rounds and acquisitions.'),
            ('Enterprise Security', 'enterprise', 'SIEM, SOC, CISO perspectives, and security operations.'),
            ('Malware Analysis', 'malware', 'Malware families, threat intelligence, and analysis.'),
            ('Compliance Updates', 'compliance', 'GDPR, HIPAA, PCI-DSS, and regulatory developments.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.securityweek.com/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'SecurityWeek',
                'data_type': 'security_topic',
                'severity': 'informational',
                'tags': ['cybersecurity', 'infosec', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
