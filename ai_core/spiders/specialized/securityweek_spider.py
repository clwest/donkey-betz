"""
SecurityWeek Spider - Cybersecurity & Infosec Intelligence
============================================================

Session 495: Added for cybersecurity sector coverage.
Covers cybersecurity startups, breaches, vulnerabilities, CISO perspectives.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class SecurityWeekSpider(BaseIntelligenceSpider):
    """SecurityWeek spider - cybersecurity and infosec news"""

    RSS_FEEDS = {
        'main': 'https://www.securityweek.com/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.categories = {
            'vulnerabilities': ['vulnerability', 'cve', 'exploit', 'zero-day', 'patch', 'security flaw'],
            'breaches': ['breach', 'data leak', 'hack', 'compromised', 'stolen data', 'ransomware'],
            'malware': ['malware', 'ransomware', 'trojan', 'botnet', 'phishing', 'spyware'],
            'cloud_security': ['cloud security', 'aws', 'azure', 'gcp', 'cloud misconfiguration'],
            'iam': ['identity', 'authentication', 'access management', 'sso', 'mfa', 'zero trust'],
            'funding': ['funding', 'raises', 'series', 'investment', 'venture', 'acquisition'],
            'startups': ['startup', 'cybersecurity startup', 'security startup', 'founded'],
            'enterprise': ['enterprise security', 'ciso', 'soc', 'security operations', 'siem'],
            'nation_state': ['nation-state', 'apt', 'chinese hackers', 'russian hackers', 'cyber espionage'],
            'compliance': ['compliance', 'gdpr', 'hipaa', 'pci', 'regulatory', 'audit'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from SecurityWeek"""
        try:
            all_articles = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:30]:
                            article = {
                                'title': entry.get('title', ''),
                                'summary': entry.get('summary', entry.get('description', '')),
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'author': entry.get('author', 'SecurityWeek'),
                                'tags': [tag.term for tag in entry.get('tags', [])],
                                'feed_source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'articles': all_articles, 'source': 'securityweek'}

        except Exception as e:
            self.logger.error(f"Error fetching SecurityWeek data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process SecurityWeek articles"""
        try:
            articles = raw_data.get('articles', [])
            processed_articles = []

            for article in articles:
                processed = self._process_article(article)
                if processed:
                    processed_articles.append(processed)

            analytics = self._generate_analytics(processed_articles)

            content = {
                'articles': processed_articles,
                'analytics': analytics,
                'vulnerability_alerts': [a for a in processed_articles if 'vulnerabilities' in a.get('categories', [])],
                'breach_news': [a for a in processed_articles if 'breaches' in a.get('categories', [])],
                'startup_funding': [a for a in processed_articles if 'funding' in a.get('categories', []) or 'startups' in a.get('categories', [])],
                'threat_intel': [a for a in processed_articles if 'malware' in a.get('categories', []) or 'nation_state' in a.get('categories', [])],
                'trending_topics': self._extract_trending_topics(processed_articles),
            }

            quality_score = min(1.0, len(processed_articles) / 25 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='securityweek.com',
                data_type='cybersecurity_news',
                content=content,
                metadata={
                    'article_count': len(processed_articles),
                    'source': 'securityweek',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['cybersecurity', 'infosec', 'vulnerabilities', 'breaches', 'security startups'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['security_analyst', 'ciso_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing SecurityWeek data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual article"""
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()

            blob = TextBlob(f"{title} {summary}")
            sentiment = {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity,
                'classification': 'positive' if blob.sentiment.polarity > 0.1 else 'negative' if blob.sentiment.polarity < -0.1 else 'neutral'
            }

            categories = []
            for cat, keywords in self.categories.items():
                if any(kw in text for kw in keywords):
                    categories.append(cat)

            # Determine severity for security news
            severity = self._assess_severity(text)

            return {
                'title': title,
                'summary': summary[:500] if summary else '',
                'link': article.get('link', ''),
                'published': article.get('published', ''),
                'author': article.get('author', ''),
                'sentiment': sentiment,
                'categories': categories or ['general'],
                'tags': article.get('tags', []),
                'feed_source': article.get('feed_source', 'main'),
                'severity': severity,
                'is_vulnerability': 'vulnerabilities' in categories,
                'is_breach': 'breaches' in categories,
                'is_funding_news': 'funding' in categories,
            }

        except Exception as e:
            self.logger.warning(f"Error processing article: {e}")
            return None

    def _assess_severity(self, text: str) -> str:
        """Assess security severity from text"""
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

    def _generate_analytics(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate analytics from articles"""
        total = len(articles)
        if total == 0:
            return {}

        return {
            'total_articles': total,
            'vulnerability_count': sum(1 for a in articles if a.get('is_vulnerability')),
            'breach_count': sum(1 for a in articles if a.get('is_breach')),
            'funding_news_count': sum(1 for a in articles if a.get('is_funding_news')),
            'severity_breakdown': {
                'critical': sum(1 for a in articles if a.get('severity') == 'critical'),
                'high': sum(1 for a in articles if a.get('severity') == 'high'),
                'medium': sum(1 for a in articles if a.get('severity') == 'medium'),
                'informational': sum(1 for a in articles if a.get('severity') == 'informational'),
            },
            'category_distribution': self._count_categories(articles),
        }

    def _count_categories(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count articles per category"""
        counts = {}
        for article in articles:
            for cat in article.get('categories', []):
                counts[cat] = counts.get(cat, 0) + 1
        return counts

    def _extract_trending_topics(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending topics"""
        topic_counts = {}
        for article in articles:
            for cat in article.get('categories', []):
                topic_counts[cat] = topic_counts.get(cat, 0) + 1

        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'topic': t, 'count': c} for t, c in sorted_topics[:10]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['cybersecurity', 'security', 'vulnerability', 'breach', 'hack', 'infosec', 'ransomware']
