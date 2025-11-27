"""
Spider Intelligence Service
Session 208: Enables agents to query and analyze spider data intelligently.

This service provides:
- Trending topic analysis
- Market insights (crypto, stocks)
- Tech trends (HackerNews, DevTo)
- Job market summaries
- Full-text search across spider data
- Data aggregation and summarization
"""

from datetime import timedelta
from collections import Counter, defaultdict
from django.utils import timezone
from django.db.models import Count, Q
from typing import Optional
import re


class SpiderIntelligenceService:
    """
    Service for agents to query spider data intelligently.

    Usage:
        from core.services import SpiderIntelligenceService

        service = SpiderIntelligenceService()
        trends = service.get_trending_topics(category='tech', hours=24)
        market = service.get_market_insights()
    """

    # Category mappings for spider classification
    # Session 222: Updated to include real data collector spider names
    CATEGORY_MAPPINGS = {
        'tech': ['hackernews', 'devto', 'github_trending', 'producthunt', 'huggingface', 'kaggle',
                 'techcrunch', 'theverge', 'wired', 'mit_tech_review', 'axios', 'hashnode'],
        'financial': ['coingecko', 'yahoo_finance', 'etherscan', 'financial', 'seekingalpha'],
        'jobs': ['weworkremotely', 'remote_jobs', 'github_jobs', 'stackoverflow_jobs', 'flexjobs',
                 'remoteok', 'weworkremotely'],
        'news': ['news_harvester', 'reuters', 'bbc', 'techcrunch', 'axios', 'theverge', 'wired',
                 'mit_tech_review'],
        'social': ['reddit', 'twitter_trends', 'social_sentiment'],
        'creative': ['dribbble', 'behance', 'medium', 'substack'],
        'crypto': ['coingecko', 'etherscan', 'nft_tracker', 'defi_tracker'],
    }

    def __init__(self):
        # Lazy import to avoid circular imports
        from core.models_unified_system import SpiderData
        self.SpiderData = SpiderData

    def get_trending_topics(self, category: str = None, hours: int = 24, limit: int = 10) -> list:
        """
        Get trending topics from spider data.

        Args:
            category: Filter by category (tech, financial, jobs, etc.)
            hours: Look back period in hours
            limit: Maximum number of topics to return

        Returns:
            List of trending topics with scores
        """
        since = timezone.now() - timedelta(hours=hours)

        # Build query
        queryset = self.SpiderData.objects.filter(created_at__gte=since)

        if category:
            spider_names = self.CATEGORY_MAPPINGS.get(category, [])
            if spider_names:
                queryset = queryset.filter(spider_name__in=spider_names)

        # Extract topics from raw_data
        topic_counts = Counter()
        topic_sources = defaultdict(set)

        for entry in queryset:
            if not entry.raw_data:
                continue

            items = entry.raw_data.get('items', [])
            for item in items:
                # Extract title/name as topic
                title = item.get('title') or item.get('name') or item.get('topic', '')
                if title:
                    # Clean and normalize
                    topic = self._normalize_topic(title)
                    if len(topic) > 3:  # Skip very short topics
                        topic_counts[topic] += 1
                        topic_sources[topic].add(entry.spider_name)

                # Also extract tags if present
                # Session 222: Handle tags as either list or comma-separated string
                tags = item.get('tags', [])
                if isinstance(tags, str):
                    # Split comma-separated string into list
                    tags = [t.strip() for t in tags.split(',') if t.strip()]
                elif not isinstance(tags, list):
                    tags = []

                for tag in tags:
                    if tag and len(tag) > 1:  # Skip single characters
                        topic_counts[tag.lower()] += 1
                        topic_sources[tag.lower()].add(entry.spider_name)

        # Calculate trending score (frequency * source diversity)
        trending = []
        for topic, count in topic_counts.most_common(limit * 2):
            source_count = len(topic_sources[topic])
            score = count * (1 + 0.5 * source_count)  # Boost for multi-source topics
            trending.append({
                'topic': topic,
                'mentions': count,
                'sources': list(topic_sources[topic]),
                'source_count': source_count,
                'score': round(score, 2)
            })

        # Sort by score and limit
        trending.sort(key=lambda x: x['score'], reverse=True)
        return trending[:limit]

    def get_market_insights(self) -> dict:
        """
        Get financial/crypto market insights from spider data.

        Returns:
            Dict with crypto prices, market trends, and notable movements
        """
        since = timezone.now() - timedelta(hours=24)

        # Get crypto data
        crypto_data = self.SpiderData.objects.filter(
            spider_name__in=['coingecko', 'etherscan', 'financial'],
            created_at__gte=since
        ).order_by('-created_at')

        # Get stock data
        stock_data = self.SpiderData.objects.filter(
            spider_name__in=['yahoo_finance', 'seekingalpha'],
            created_at__gte=since
        ).order_by('-created_at')

        insights = {
            'crypto': [],
            'stocks': [],
            'summary': '',
            'last_updated': None
        }

        # Process crypto data
        seen_crypto = set()
        for entry in crypto_data:
            if not entry.raw_data:
                continue
            items = entry.raw_data.get('items', [])
            for item in items:
                symbol = item.get('symbol', '').upper()
                if symbol and symbol not in seen_crypto:
                    seen_crypto.add(symbol)
                    insights['crypto'].append({
                        'symbol': symbol,
                        'name': item.get('name', symbol),
                        'price': item.get('price') or item.get('current_price'),
                        'change_24h': item.get('change_24h') or item.get('price_change_percentage_24h'),
                        'market_cap': item.get('market_cap'),
                        'source': entry.spider_name
                    })
            if not insights['last_updated']:
                insights['last_updated'] = entry.created_at.isoformat()

        # Process stock data
        seen_stocks = set()
        for entry in stock_data:
            if not entry.raw_data:
                continue
            items = entry.raw_data.get('items', [])
            for item in items:
                symbol = item.get('symbol', '').upper()
                if symbol and symbol not in seen_stocks:
                    seen_stocks.add(symbol)
                    insights['stocks'].append({
                        'symbol': symbol,
                        'name': item.get('name', symbol),
                        'price': item.get('price'),
                        'change': item.get('change'),
                        'source': entry.spider_name
                    })

        # Generate summary
        if insights['crypto']:
            top_crypto = insights['crypto'][:3]
            crypto_summary = ', '.join([
                f"{c['symbol']}: ${c['price']}" for c in top_crypto if c.get('price')
            ])
            insights['summary'] = f"Crypto: {crypto_summary}"

        return insights

    def get_tech_trends(self, hours: int = 24, limit: int = 15) -> dict:
        """
        Get technology trends from HackerNews, DevTo, TechCrunch, etc.

        Returns:
            Dict with tech topics, discussions, and projects
        """
        since = timezone.now() - timedelta(hours=hours)

        tech_data = self.SpiderData.objects.filter(
            spider_name__in=self.CATEGORY_MAPPINGS['tech'],
            created_at__gte=since
        ).order_by('-created_at')

        trends = {
            'discussions': [],  # Tech articles and discussions
            'projects': [],     # GitHub, ProductHunt
            'topics': [],       # Extracted topics
            'sources': {},
            'last_updated': None
        }

        topic_counts = Counter()
        seen_titles = set()  # Session 222: Deduplicate discussions

        for entry in tech_data:
            if not entry.raw_data:
                continue

            source = entry.spider_name
            items = entry.raw_data.get('items', [])

            # Track source contributions
            if source not in trends['sources']:
                trends['sources'][source] = 0
            trends['sources'][source] += len(items)

            for item in items:
                title = item.get('title', '')
                url = item.get('url', '') or item.get('link', '')
                score = item.get('score', 0) or item.get('points', 0) or 0

                if title:
                    # Session 222: Deduplicate by normalized title
                    title_key = title.lower().strip()
                    if title_key in seen_titles:
                        continue
                    seen_titles.add(title_key)

                    # Session 222: Include more sources as discussions (tech news)
                    discussion_sources = ['hackernews', 'devto', 'techcrunch', 'theverge',
                                          'wired', 'mit_tech_review', 'axios', 'hashnode']
                    project_sources = ['github_trending', 'producthunt']

                    if source in discussion_sources:
                        trends['discussions'].append({
                            'title': title,
                            'url': url,
                            'score': score,
                            'source': source,
                            'tags': item.get('tags', []),
                            'description': (item.get('description', '') or '')[:200]
                        })
                    elif source in project_sources:
                        trends['projects'].append({
                            'name': title,
                            'description': item.get('description', ''),
                            'url': url,
                            'stars': item.get('stars', 0),
                            'source': source
                        })

                    # Extract topics from title
                    words = self._extract_tech_keywords(title)
                    for word in words:
                        topic_counts[word] += 1

            if not trends['last_updated']:
                trends['last_updated'] = entry.created_at.isoformat()

        # Sort discussions by score (if available), then by recency
        trends['discussions'] = sorted(
            trends['discussions'],
            key=lambda x: (x.get('score', 0) or 0, x.get('title', '')),
            reverse=True
        )[:limit]

        trends['projects'] = sorted(
            trends['projects'],
            key=lambda x: x.get('stars', 0),
            reverse=True
        )[:limit]

        # Top topics
        trends['topics'] = [
            {'topic': t, 'count': c}
            for t, c in topic_counts.most_common(20)
        ]

        return trends

    def get_job_market_summary(self, hours: int = 48, limit: int = 20) -> dict:
        """
        Get remote job market summary.

        Returns:
            Dict with job listings, categories, and market insights
        """
        since = timezone.now() - timedelta(hours=hours)

        job_data = self.SpiderData.objects.filter(
            spider_name__in=self.CATEGORY_MAPPINGS['jobs'],
            created_at__gte=since
        ).order_by('-created_at')

        summary = {
            'jobs': [],
            'categories': Counter(),
            'companies': Counter(),
            'locations': Counter(),
            'total_found': 0,
            'sources': {},
            'last_updated': None
        }

        seen_jobs = set()

        for entry in job_data:
            if not entry.raw_data:
                continue

            source = entry.spider_name
            items = entry.raw_data.get('items', [])

            if source not in summary['sources']:
                summary['sources'][source] = 0

            for item in items:
                title = item.get('title', '')
                company = item.get('company', '') or item.get('author', '')

                # Session 222: Extract company from title if format is "Company: Job Title"
                if not company and ': ' in title:
                    parts = title.split(': ', 1)
                    if len(parts) == 2 and len(parts[0]) < 50:  # Reasonable company name length
                        company = parts[0]
                        title = parts[1]

                # Deduplicate by title + company
                job_key = f"{title}:{company}".lower()
                if job_key in seen_jobs:
                    continue
                seen_jobs.add(job_key)

                # Get category from tags if available
                tags = item.get('tags', [])
                if isinstance(tags, str):
                    tags = [t.strip() for t in tags.split(',') if t.strip()]
                category = tags[0] if tags else item.get('category', 'Engineering')

                # Extract salary info
                salary = item.get('salary')
                if not salary:
                    salary_min = item.get('salary_min')
                    salary_max = item.get('salary_max')
                    if salary_min and salary_max:
                        salary = f"${salary_min:,} - ${salary_max:,}"
                    elif salary_min:
                        salary = f"${salary_min:,}+"

                if title:
                    summary['jobs'].append({
                        'title': title,
                        'company': company,
                        'location': item.get('location', 'Remote'),
                        'url': item.get('url', item.get('link', item.get('apply_url', ''))),
                        'salary': salary,
                        'category': category,
                        'source': source,
                        'posted': item.get('posted', item.get('date', item.get('published')))
                    })

                    # Track categories and companies
                    category = item.get('category', 'Engineering')
                    summary['categories'][category] += 1
                    if company:
                        summary['companies'][company] += 1

                    location = item.get('location', 'Remote')
                    summary['locations'][location] += 1

                    summary['sources'][source] += 1

            if not summary['last_updated']:
                summary['last_updated'] = entry.created_at.isoformat()

        summary['total_found'] = len(summary['jobs'])
        summary['jobs'] = summary['jobs'][:limit]

        # Convert counters to lists for JSON
        summary['categories'] = [
            {'category': k, 'count': v}
            for k, v in summary['categories'].most_common(10)
        ]
        summary['companies'] = [
            {'company': k, 'count': v}
            for k, v in summary['companies'].most_common(10)
        ]
        summary['locations'] = [
            {'location': k, 'count': v}
            for k, v in summary['locations'].most_common(10)
        ]

        return summary

    def search_spider_data(self, query: str, category: str = None,
                           hours: int = 72, limit: int = 50) -> list:
        """
        Full-text search across spider data.

        Args:
            query: Search query
            category: Optional category filter
            hours: Look back period
            limit: Maximum results

        Returns:
            List of matching items
        """
        since = timezone.now() - timedelta(hours=hours)
        query_lower = query.lower()

        # Build queryset
        queryset = self.SpiderData.objects.filter(created_at__gte=since)

        if category:
            spider_names = self.CATEGORY_MAPPINGS.get(category, [])
            if spider_names:
                queryset = queryset.filter(spider_name__in=spider_names)

        results = []
        seen = set()

        for entry in queryset.order_by('-created_at'):
            if not entry.raw_data:
                continue

            items = entry.raw_data.get('items', [])
            for item in items:
                # Search in title, description, tags
                title = item.get('title', '') or item.get('name', '')
                description = item.get('description', '') or item.get('summary', '')
                tags = ' '.join(item.get('tags', []))

                searchable = f"{title} {description} {tags}".lower()

                if query_lower in searchable:
                    # Deduplicate
                    item_key = f"{title}:{item.get('url', '')}".lower()
                    if item_key in seen:
                        continue
                    seen.add(item_key)

                    results.append({
                        'title': title,
                        'description': description[:200] if description else '',
                        'url': item.get('url', ''),
                        'source': entry.spider_name,
                        'category': entry.data_type,
                        'found_at': entry.created_at.isoformat(),
                        'relevance': self._calculate_relevance(query_lower, searchable)
                    })

                    if len(results) >= limit:
                        break

            if len(results) >= limit:
                break

        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results

    def get_data_summary(self, spider_name: str = None, hours: int = 24) -> dict:
        """
        Get summary statistics for spider data.

        Args:
            spider_name: Optional filter by spider
            hours: Look back period

        Returns:
            Dict with summary statistics
        """
        since = timezone.now() - timedelta(hours=hours)

        queryset = self.SpiderData.objects.filter(created_at__gte=since)
        if spider_name:
            queryset = queryset.filter(spider_name=spider_name)

        # Basic counts
        total = queryset.count()
        by_spider = dict(
            queryset.values('spider_name')
            .annotate(count=Count('id'))
            .values_list('spider_name', 'count')
        )
        by_type = dict(
            queryset.values('data_type')
            .annotate(count=Count('id'))
            .values_list('data_type', 'count')
        )

        # Calculate total items
        total_items = 0
        for entry in queryset:
            if entry.raw_data and 'items' in entry.raw_data:
                total_items += len(entry.raw_data['items'])

        return {
            'total_entries': total,
            'total_items': total_items,
            'by_spider': by_spider,
            'by_type': by_type,
            'period_hours': hours,
            'generated_at': timezone.now().isoformat()
        }

    def get_insights_for_prompt(self, prompt: str, limit: int = 5) -> dict:
        """
        Get relevant insights for an AI prompt.
        Used by agents to enhance their responses with real data.

        Args:
            prompt: The user's prompt/question
            limit: Max insights per category

        Returns:
            Dict with relevant trends, data, and suggestions
        """
        prompt_lower = prompt.lower()

        insights = {
            'relevant_trends': [],
            'market_data': None,
            'related_discussions': [],
            'suggestions': []
        }

        # Detect prompt intent
        is_tech = any(w in prompt_lower for w in ['tech', 'code', 'programming', 'software', 'ai', 'ml'])
        is_crypto = any(w in prompt_lower for w in ['crypto', 'bitcoin', 'btc', 'eth', 'blockchain', 'nft'])
        is_finance = any(w in prompt_lower for w in ['stock', 'market', 'invest', 'trading', 'finance'])
        is_jobs = any(w in prompt_lower for w in ['job', 'career', 'work', 'remote', 'hire', 'salary'])
        is_design = any(w in prompt_lower for w in ['design', 'ui', 'ux', 'graphic', 'logo', 'brand'])

        # Get relevant data based on intent
        if is_tech:
            tech_trends = self.get_tech_trends(hours=24, limit=limit)
            insights['relevant_trends'] = tech_trends.get('topics', [])[:limit]
            insights['related_discussions'] = tech_trends.get('discussions', [])[:limit]
            insights['suggestions'].append("Consider referencing current tech trends in your response")

        if is_crypto or is_finance:
            market = self.get_market_insights()
            insights['market_data'] = {
                'crypto': market.get('crypto', [])[:5],
                'summary': market.get('summary', '')
            }
            insights['suggestions'].append("Include current market data for accuracy")

        if is_jobs:
            jobs = self.get_job_market_summary(hours=48, limit=limit)
            insights['job_market'] = {
                'total': jobs.get('total_found', 0),
                'top_categories': jobs.get('categories', [])[:5],
                'sample_jobs': jobs.get('jobs', [])[:3]
            }
            insights['suggestions'].append("Reference current job market trends")

        # Always do a quick search for relevant content
        search_results = self.search_spider_data(prompt, limit=3)
        if search_results:
            insights['related_content'] = search_results

        return insights

    # Helper methods

    def _normalize_topic(self, text: str) -> str:
        """Normalize topic text."""
        # Remove special characters, lowercase
        text = re.sub(r'[^\w\s-]', '', text.lower())
        # Truncate long topics
        words = text.split()[:8]
        return ' '.join(words)

    def _extract_tech_keywords(self, title: str) -> list:
        """Extract technology keywords from a title."""
        # Common tech keywords to look for
        tech_keywords = {
            'ai', 'ml', 'python', 'javascript', 'rust', 'go', 'react', 'vue',
            'docker', 'kubernetes', 'aws', 'gcp', 'azure', 'api', 'graphql',
            'llm', 'gpt', 'claude', 'openai', 'startup', 'saas', 'devops',
            'security', 'blockchain', 'web3', 'database', 'postgres', 'redis',
            'typescript', 'node', 'django', 'fastapi', 'nextjs', 'svelte'
        }

        words = re.findall(r'\b\w+\b', title.lower())
        return [w for w in words if w in tech_keywords]

    def _calculate_relevance(self, query: str, text: str) -> float:
        """Calculate relevance score for search results."""
        query_words = set(query.split())
        text_words = set(text.split())

        # Simple Jaccard-like similarity
        intersection = len(query_words & text_words)
        if not query_words:
            return 0.0

        # Bonus for exact phrase match
        phrase_bonus = 1.0 if query in text else 0.0

        return (intersection / len(query_words)) + phrase_bonus


# Convenience function for quick access
def get_spider_intelligence() -> SpiderIntelligenceService:
    """Get a SpiderIntelligenceService instance."""
    return SpiderIntelligenceService()
