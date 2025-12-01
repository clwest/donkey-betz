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
                 'techcrunch', 'theverge', 'wired', 'mit_tech_review', 'axios', 'hashnode',
                 'medium', 'substack'],
        'financial': ['coingecko', 'yahoo_finance', 'etherscan', 'financial', 'seekingalpha'],
        'jobs': ['weworkremotely', 'remote_jobs', 'github_jobs', 'stackoverflow_jobs', 'flexjobs',
                 'remoteok', 'weworkremotely'],
        'news': ['news_harvester', 'reuters', 'bbc', 'techcrunch', 'axios', 'theverge', 'wired',
                 'mit_tech_review'],
        # Session 294: Added bluesky and youtube for customer research
        'social': ['reddit', 'bluesky', 'twitter_trends', 'social_sentiment'],
        'video': ['youtube'],
        'creative': ['dribbble', 'behance', 'medium', 'substack'],
        'crypto': ['coingecko', 'etherscan', 'nft_tracker', 'defi_tracker'],
        # Session 294: Community category for customer research spiders
        'community': ['reddit', 'bluesky', 'discord', 'indiehackers'],
    }

    def __init__(self):
        # Lazy import to avoid circular imports
        from core.models_unified_system import SpiderData
        self.SpiderData = SpiderData

    # Session 237: Common stopwords to filter out from trending topics
    STOPWORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
        'she', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why',
        'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
        'than', 'too', 'very', 'just', 'also', 'now', 'new', 'first', 'last',
        'long', 'great', 'little', 'own', 'other', 'old', 'right', 'big',
        'high', 'different', 'small', 'large', 'next', 'early', 'young',
        'important', 'public', 'bad', 'good', 'best', 'top', 'get', 'got',
        'your', 'our', 'my', 'up', 'out', 'about', 'into', 'over', 'after',
        'beneath', 'under', 'above', 'between', 'through', 'during', 'before',
        'here', 'there', 'am', 'being', 'if', 'then', 'else', 'while',
        # Common but non-specific web/tech words
        'http', 'https', 'www', 'com', 'org', 'net', 'html', 'click', 'read',
        'watch', 'see', 'know', 'like', 'make', 'way', 'look', 'come', 'think',
        'use', 'find', 'give', 'tell', 'work', 'call', 'try', 'ask', 'feel',
        'seem', 'leave', 'put', 'keep', 'let', 'begin', 'show', 'hear', 'play',
        'run', 'move', 'live', 'believe', 'hold', 'bring', 'happen', 'write',
        # Generic content words
        'today', 'year', 'years', 'day', 'days', 'time', 'week', 'month',
        'people', 'world', 'life', 'thing', 'things', 'part', 'place', 'case',
        'point', 'government', 'company', 'system', 'number', 'hand', 'course',
        'fact', 'group', 'problem', 'home', 'side', 'kind', 'head', 'area',
        'lot', 'end', 'money', 'word', 'business', 'issue', 'night', 'state',
        # News-specific generic words
        'news', 'report', 'says', 'said', 'officials', 'according', 'sources',
        'update', 'latest', 'breaking', 'live', 'watch', 'video', 'photo',
        'deals', 'deal', 'sale', 'sales', 'shopping', 'buy', 'price', 'prices',
        'gear', 'guide', 'review', 'reviews', 'list', 'best', 'coupon', 'coupons',
        'discount', 'discounts', 'offer', 'offers', 'promo', 'save', 'savings',
        'gift', 'gifts', 'holiday', 'holidays', 'black', 'friday', 'cyber', 'monday'
    }

    def get_trending_topics(self, category: str = None, hours: int = 24, limit: int = 10) -> list:
        """
        Session 237: Improved trending topic extraction.

        Get trending topics from spider data with smarter extraction:
        1. Prioritize tags/keywords from articles (most reliable)
        2. Extract meaningful phrases from titles (not single words)
        3. Filter out common stopwords aggressively
        4. Show actual headlines for context

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

        # Separate tracking for tags vs extracted keywords
        tag_counts = Counter()  # Tags are highest quality
        tag_sources = defaultdict(set)

        keyword_counts = Counter()  # Extracted keywords
        keyword_sources = defaultdict(set)

        # Also collect top headlines per source for context
        headlines_by_source = defaultdict(list)

        for entry in queryset:
            if not entry.raw_data:
                continue

            items = entry.raw_data.get('items', [])
            for item in items:
                title = item.get('title') or item.get('name') or ''

                # Collect headlines
                if title and not title.startswith('Spider') and len(title) > 10:
                    headlines_by_source[entry.spider_name].append(title)

                # Priority 1: Extract tags (most reliable indicator of topic)
                tags = item.get('tags', [])
                if isinstance(tags, str):
                    tags = [t.strip() for t in tags.split(',') if t.strip()]
                elif not isinstance(tags, list):
                    tags = []

                for tag in tags:
                    tag_clean = tag.lower().strip()
                    if tag_clean and len(tag_clean) > 1 and tag_clean not in self.STOPWORDS:
                        tag_counts[tag_clean] += 1
                        tag_sources[tag_clean].add(entry.spider_name)

                # Priority 2: Extract meaningful keywords from titles
                if title:
                    keywords = self._extract_meaningful_keywords(title)
                    for kw in keywords:
                        keyword_counts[kw] += 1
                        keyword_sources[kw].add(entry.spider_name)

        # Build trending list - prioritize tags, then keywords
        trending = []
        seen_topics = set()

        # First add high-quality tags
        for tag, count in tag_counts.most_common(limit * 3):
            if tag in seen_topics:
                continue
            source_count = len(tag_sources[tag])
            # Tags get a quality boost
            score = count * (1.5 + 0.5 * source_count)
            trending.append({
                'topic': tag,
                'mentions': count,
                'sources': list(tag_sources[tag]),
                'source_count': source_count,
                'score': round(score, 2),
                'type': 'tag'  # Indicates this came from article tags
            })
            seen_topics.add(tag)

        # Then add extracted keywords (lower priority)
        for kw, count in keyword_counts.most_common(limit * 3):
            if kw in seen_topics:
                continue
            source_count = len(keyword_sources[kw])
            # Keywords get base score
            score = count * (1 + 0.3 * source_count)
            # Only add if significant
            if count >= 2 or source_count >= 2:
                trending.append({
                    'topic': kw,
                    'mentions': count,
                    'sources': list(keyword_sources[kw]),
                    'source_count': source_count,
                    'score': round(score, 2),
                    'type': 'keyword'
                })
                seen_topics.add(kw)

        # Sort by score and limit
        trending.sort(key=lambda x: x['score'], reverse=True)
        return trending[:limit]

    def _extract_meaningful_keywords(self, title: str) -> list:
        """
        Session 237: Extract meaningful keywords from a title.
        Focuses on tech terms, proper nouns, and multi-word phrases.
        """
        keywords = []

        # Tech/business terms to always capture
        tech_terms = {
            'ai', 'ml', 'api', 'sdk', 'llm', 'gpt', 'claude', 'openai', 'anthropic',
            'python', 'javascript', 'typescript', 'rust', 'golang', 'java', 'kotlin',
            'react', 'vue', 'angular', 'svelte', 'nextjs', 'nodejs', 'django', 'fastapi',
            'docker', 'kubernetes', 'k8s', 'aws', 'gcp', 'azure', 'cloud',
            'startup', 'saas', 'fintech', 'crypto', 'bitcoin', 'ethereum', 'blockchain',
            'devops', 'devsecops', 'cicd', 'agile', 'scrum',
            'frontend', 'backend', 'fullstack', 'microservices', 'serverless',
            'database', 'postgres', 'mysql', 'mongodb', 'redis', 'graphql',
            'linux', 'windows', 'macos', 'ios', 'android',
            'security', 'cybersecurity', 'privacy', 'encryption',
            'remote', 'hybrid', 'onsite', 'freelance', 'contractor',
            'senior', 'junior', 'lead', 'staff', 'principal', 'architect',
            'engineer', 'developer', 'designer', 'manager', 'director'
        }

        # Clean and tokenize
        title_lower = title.lower()
        words = re.findall(r'\b[a-z][a-z0-9+#.-]*\b', title_lower)

        # Extract tech terms
        for word in words:
            if word in tech_terms:
                keywords.append(word)

        # Extract capitalized phrases (likely proper nouns/names)
        # Match sequences like "Sand Battery", "Black Friday", company names
        proper_nouns = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', title)
        for noun in proper_nouns:
            noun_lower = noun.lower()
            if noun_lower not in self.STOPWORDS and len(noun_lower) > 3:
                keywords.append(noun_lower)

        return keywords

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

    def get_tech_trends(self, hours: int = 24, limit: int = 15, topic_filter: str = None, include_producthunt: bool = True) -> dict:
        """
        Get technology trends from HackerNews, DevTo, TechCrunch, etc.

        Args:
            hours: Look back period
            limit: Max results per category
            topic_filter: Optional filter like 'ai', 'web', 'security' to focus results
            include_producthunt: Whether to include ProductHunt in projects (default True).
                                 Set to False for research results where ProductHunt is less useful.

        Returns:
            Dict with tech topics, discussions, and projects
        """
        since = timezone.now() - timedelta(hours=hours)

        # Session 272: For design queries, also include creative spiders (Behance, Dribbble)
        spider_sources = list(self.CATEGORY_MAPPINGS['tech'])
        if topic_filter == 'design':
            spider_sources.extend(['dribbble', 'behance', 'figma', 'canva', 'unsplash'])

        tech_data = self.SpiderData.objects.filter(
            spider_name__in=spider_sources,
            created_at__gte=since
        ).order_by('-created_at')

        # Session 272: Topic-specific keywords for filtering (all lowercase for matching)
        topic_keywords = {
            'ai': [' ai ', ' ai,', ' ai.', 'artificial intelligence', 'machine learning', ' ml ',
                   'llm', 'gpt-', 'gpt4', 'gpt 4', 'claude', 'openai', 'anthropic', 'neural',
                   'deep learning', 'chatgpt', 'chat gpt', 'gemini', 'copilot', 'diffusion',
                   'transformer', 'language model', 'hugging face', 'huggingface', 'langchain',
                   'vector database', 'embedding', 'rag ', 'llama', 'mistral', 'ollama'],
            'web': ['javascript', 'typescript', 'react', 'vue', 'angular', 'nextjs', 'frontend',
                    'backend', 'fullstack', 'api', 'rest', 'graphql', 'html', 'css', 'nodejs'],
            'security': ['security', 'vulnerability', 'hack', 'breach', 'exploit', 'malware',
                        'encryption', 'privacy', 'authentication', 'cybersecurity'],
            'cloud': ['aws', 'azure', 'gcp', 'kubernetes', 'docker', 'serverless', 'cloud',
                     'devops', 'infrastructure', 'microservices'],
            'design': [' design', 'design ', 'designer', 'ui design', 'ux design', 'ui/ux',
                      'figma', 'sketch app', 'adobe xd', 'illustrator', 'illustration',
                      'typography', 'branding', 'logo design', 'graphic design', 'visual design',
                      'web design', 'product design', 'interaction design', 'motion design',
                      'dribbble', 'behance', 'color palette', 'layout', 'mockup', 'wireframe',
                      'prototype', 'user interface', 'user experience', 'photoshop', 'canva',
                      'iconography', 'infographic', 'brand identity', 'style guide'],
        }

        # Words to filter OUT (shopping/deals content)
        blacklist_words = ['black friday', 'cyber monday', 'deal', 'deals', 'sale', 'discount',
                          'coupon', 'promo', 'shopping', 'buy now', 'price drop', 'save $',
                          'off today', '% off', 'limited time']

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
                description = (item.get('description', '') or '')[:200]

                if title:
                    # Session 222: Deduplicate by normalized title
                    title_key = title.lower().strip()
                    if title_key in seen_titles:
                        continue

                    # Session 272: Filter out shopping/deals content
                    combined_text = (title + ' ' + description).lower()
                    if any(blacklist in combined_text for blacklist in blacklist_words):
                        continue

                    # Session 272: Apply topic filter if specified
                    if topic_filter and topic_filter in topic_keywords:
                        filter_keywords = topic_keywords[topic_filter]
                        if not any(kw in combined_text for kw in filter_keywords):
                            continue  # Skip items that don't match the topic

                    seen_titles.add(title_key)

                    # Session 272: Include all tech news sources as discussions
                    discussion_sources = ['hackernews', 'devto', 'techcrunch', 'theverge',
                                          'wired', 'mit_tech_review', 'axios', 'hashnode',
                                          'medium', 'substack', 'huggingface', 'kaggle']
                    # Session 274: Optionally exclude ProductHunt for cleaner research results
                    if include_producthunt:
                        project_sources = ['github_trending', 'producthunt']
                    else:
                        project_sources = ['github_trending']

                    if source in discussion_sources:
                        trends['discussions'].append({
                            'title': title,
                            'url': url,
                            'score': score,
                            'source': source,
                            'tags': item.get('tags', []),
                            'description': description
                        })
                    elif source in project_sources:
                        trends['projects'].append({
                            'name': title,
                            'description': description,
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

        # Session 272: Sort discussions with source diversity
        # Group by source, then interleave to get variety
        from collections import defaultdict
        by_source = defaultdict(list)
        for d in trends['discussions']:
            by_source[d['source']].append(d)

        # Sort each source's items by score (if available)
        for source in by_source:
            by_source[source].sort(key=lambda x: x.get('score', 0) or 0, reverse=True)

        # Interleave sources to ensure diversity
        interleaved = []
        source_keys = list(by_source.keys())
        idx = 0
        while len(interleaved) < len(trends['discussions']) and source_keys:
            source = source_keys[idx % len(source_keys)]
            if by_source[source]:
                interleaved.append(by_source[source].pop(0))
            else:
                source_keys.remove(source)
            idx += 1

        trends['discussions'] = interleaved[:limit]

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

        Session 294: Enhanced to handle multi-word queries better.
        - Strips boolean operators (OR, AND, quotes)
        - Splits query into individual terms
        - Matches if ANY term is found (OR logic)
        - Scores by number of matching terms

        Args:
            query: Search query
            category: Optional category filter
            hours: Look back period
            limit: Maximum results

        Returns:
            List of matching items
        """
        since = timezone.now() - timedelta(hours=hours)

        # Session 294: Clean up complex queries from GPT
        # Remove boolean operators and quotes
        clean_query = query.lower()
        for operator in [' or ', ' and ', '"', "'", '(', ')']:
            clean_query = clean_query.replace(operator, ' ')

        # Split into individual search terms (min 2 chars)
        search_terms = [term.strip() for term in clean_query.split() if len(term.strip()) >= 2]

        # Filter out common words that are too generic
        stopwords = {'the', 'for', 'and', 'with', 'that', 'this', 'from', 'are', 'was', 'were'}
        search_terms = [t for t in search_terms if t not in stopwords]

        if not search_terms:
            return []

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
                tags = ' '.join(item.get('tags', []) if isinstance(item.get('tags'), list) else [])

                searchable = f"{title} {description} {tags}".lower()

                # Session 294: Match if ANY term is found
                matching_terms = [term for term in search_terms if term in searchable]
                if matching_terms:
                    # Deduplicate
                    item_key = f"{title}:{item.get('url', '')}".lower()
                    if item_key in seen:
                        continue

                    # Calculate relevance based on matching term count
                    term_relevance = len(matching_terms) / len(search_terms)
                    seen.add(item_key)

                    results.append({
                        'title': title,
                        'description': description[:200] if description else '',
                        'content': description,  # Full content for pain point analysis
                        'url': item.get('url', ''),
                        'source': entry.spider_name,
                        'category': entry.data_type,
                        'found_at': entry.created_at.isoformat(),
                        'matching_terms': matching_terms,
                        'relevance': term_relevance
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

    def get_creative_trends(self, hours: int = 48, limit: int = 10) -> dict:
        """
        Session 266: Get trending creative/design styles from spider data.

        Queries creative spiders (Dribbble, Behance, Medium, Etsy, etc.)
        for trending styles, colors, and design patterns.

        Returns:
            Dict with trending styles, colors, and design patterns for AI generation
        """
        since = timezone.now() - timedelta(hours=hours)

        # Creative spider sources
        creative_spiders = [
            'dribbble', 'behance', 'medium', 'etsy', 'creativemarket',
            'envato', 'unsplash', 'pinterest', 'figma', 'canva'
        ]

        creative_data = self.SpiderData.objects.filter(
            spider_name__in=creative_spiders,
            created_at__gte=since
        ).order_by('-created_at')

        # Design terms to extract
        design_styles = {
            'abstract', 'geometric', 'minimalist', 'maximalist', 'vintage', 'retro',
            'modern', 'contemporary', 'boho', 'bohemian', 'scandinavian', 'industrial',
            'art-deco', 'art-nouveau', 'bauhaus', 'brutalist', 'cyberpunk', 'vaporwave',
            'watercolor', 'line-art', 'illustration', 'vector', 'flat-design',
            'gradient', '3d', 'isometric', 'hand-drawn', 'sketch', 'botanical',
            'floral', 'nature', 'organic', 'textured', 'grunge', 'clean', 'sleek',
            'playful', 'elegant', 'luxury', 'rustic', 'coastal', 'tropical',
            'psychedelic', 'surreal', 'pop-art', 'collage', 'mixed-media'
        }

        color_palettes = {
            'earth-tones', 'pastels', 'neutrals', 'monochrome', 'jewel-tones',
            'neon', 'muted', 'vibrant', 'warm', 'cool', 'terracotta', 'sage',
            'blush', 'dusty-rose', 'mustard', 'olive', 'navy', 'burgundy',
            'coral', 'teal', 'mauve', 'cream', 'charcoal', 'forest-green'
        }

        # Count occurrences
        style_counts = Counter()
        color_counts = Counter()
        keywords = []
        sources_found = set()

        for entry in creative_data:
            if not entry.raw_data:
                continue

            sources_found.add(entry.spider_name)
            items = entry.raw_data.get('items', [])

            for item in items:
                # Extract from title, description, tags
                text_fields = [
                    item.get('title', ''),
                    item.get('description', ''),
                    ' '.join(item.get('tags', []) if isinstance(item.get('tags'), list) else []),
                    item.get('category', ''),
                ]
                combined_text = ' '.join(text_fields).lower()

                # Count style mentions
                for style in design_styles:
                    if style in combined_text or style.replace('-', ' ') in combined_text:
                        style_counts[style] += 1

                # Count color palette mentions
                for color in color_palettes:
                    if color in combined_text or color.replace('-', ' ') in combined_text:
                        color_counts[color] += 1

                # Extract notable keywords
                if item.get('tags'):
                    tags = item.get('tags')
                    if isinstance(tags, list):
                        keywords.extend([t.lower() for t in tags[:5]])

        # Build trending results
        trending_styles = [
            {'style': style, 'count': count, 'type': 'design'}
            for style, count in style_counts.most_common(limit)
        ]

        trending_colors = [
            {'palette': color, 'count': count, 'type': 'color'}
            for color, count in color_counts.most_common(limit)
        ]

        # Get unique relevant keywords
        keyword_counts = Counter(keywords)
        top_keywords = [kw for kw, _ in keyword_counts.most_common(20)
                        if kw not in self.STOPWORDS and len(kw) > 3]

        # If no spider data, provide curated defaults based on current design trends
        if not trending_styles:
            trending_styles = [
                {'style': 'abstract', 'count': 0, 'type': 'default'},
                {'style': 'botanical', 'count': 0, 'type': 'default'},
                {'style': 'geometric', 'count': 0, 'type': 'default'},
                {'style': 'watercolor', 'count': 0, 'type': 'default'},
                {'style': 'line-art', 'count': 0, 'type': 'default'},
            ]

        if not trending_colors:
            trending_colors = [
                {'palette': 'earth-tones', 'count': 0, 'type': 'default'},
                {'palette': 'sage', 'count': 0, 'type': 'default'},
                {'palette': 'neutrals', 'count': 0, 'type': 'default'},
                {'palette': 'terracotta', 'count': 0, 'type': 'default'},
            ]

        return {
            'trending_styles': trending_styles,
            'trending_colors': trending_colors,
            'keywords': top_keywords[:10],
            'sources_queried': list(sources_found),
            'data_freshness_hours': hours,
            'has_live_data': len(sources_found) > 0,
            'summary': self._build_creative_summary(trending_styles, trending_colors)
        }

    def _build_creative_summary(self, styles: list, colors: list) -> str:
        """Build a human-readable summary of creative trends."""
        parts = []

        if styles:
            style_names = [s['style'] for s in styles[:5]]
            parts.append(f"Trending styles: {', '.join(style_names)}")

        if colors:
            color_names = [c['palette'] for c in colors[:5]]
            parts.append(f"Popular palettes: {', '.join(color_names)}")

        if not parts:
            parts.append("Using curated 2024 design trends")

        return '. '.join(parts) + '.'


# Convenience function for quick access
def get_spider_intelligence() -> SpiderIntelligenceService:
    """Get a SpiderIntelligenceService instance."""
    return SpiderIntelligenceService()
