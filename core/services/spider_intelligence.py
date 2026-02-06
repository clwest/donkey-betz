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
from django.db.models import Count
from typing import Optional
import json
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
    # Session 936: Expanded to include ALL 77 registered spiders
    CATEGORY_MAPPINGS = {
        'tech': [
            'hackernews', 'devto', 'github', 'producthunt', 'huggingface', 'kaggle',
            'techcrunch', 'theverge', 'wired', 'mit_tech_review', 'axios',
            'medium', 'substack', 'arstechnica', 'venturebeat', 'techcrunch_startups',
            'hackernoon', 'freecodecamp', 'smashingmagazine',
        ],
        'financial': [
            'coingecko', 'yahoo_finance', 'etherscan', 'etherscan_api', 'finnhub',
            'polygon_finance', 'sec_edgar', 'crunchbase', 'kickstarter',
        ],
        'jobs': [
            'weworkremotely', 'github_jobs', 'remoteok', 'adzuna',
        ],
        'news': [
            'reuters_rss', 'bbc', 'cnn', 'npr', 'axios', 'google_news', 'newsapi',
            'business_news', 'defenseone',
        ],
        # Session 294: Added bluesky and youtube for customer research
        'social': ['reddit', 'bluesky', 'discord', 'discord_training'],
        'video': ['youtube', 'giphy'],
        'creative': ['behance', 'medium', 'substack', 'awwwards', 'unsplash'],
        'crypto': ['coingecko', 'etherscan', 'etherscan_api'],
        # Session 294: Community category for customer research spiders
        'community': ['reddit', 'bluesky', 'discord'],
        # Session 936: New categories for comprehensive coverage
        'legal': [
            'courtlistener', 'findlaw', 'justia', 'lii', 'colorado_family_law',
            'justia_family_law', 'legal_news', 'government',
        ],
        'sports': ['theodds', 'kalshi'],
        'entertainment': ['youtube', 'spotify', 'variety', 'polygon_gaming', 'giphy'],
        'science': ['science', 'kaggle', 'huggingface', 'arxiv', 'library'],
        'lifestyle': ['food', 'travel', 'parenting', 'health', 'real_estate', 'lifehacker'],
        'education': ['coursera', 'udemy', 'teachable', 'education_rss'],
        'security': ['securityweek'],
        'health': ['mobihealthnews', 'health'],
        'weather': ['noaa_weather', 'openmeteo'],
    }

    # Session 385: Job spiders to exclude from general trending topics
    # These spiders pollute trends with job titles like "developer", "designer", etc.
    # Job data should only appear in the dedicated Jobs sub-tab
    JOB_SPIDERS = {
        'weworkremotely', 'remote_jobs', 'github_jobs', 'stackoverflow_jobs',
        'flexjobs', 'remoteok', 'adzuna', 'angellist', 'toptal', 'guru',
        'peopleperhour', 'ninetyninedesigns'
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

    def _parse_raw_data(self, raw_data) -> Optional[dict]:
        """
        Session 535: Helper to safely parse raw_data which may be a string or dict.

        Returns:
            dict if successfully parsed, None otherwise
        """
        if not raw_data:
            return None

        if isinstance(raw_data, dict):
            return raw_data

        if isinstance(raw_data, str):
            try:
                parsed = json.loads(raw_data)
                if isinstance(parsed, dict):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass

        return None

    def get_trending_topics(self, category: str = None, hours: int = 168, limit: int = 10, include_jobs: bool = False) -> list:
        """
        Session 237: Improved trending topic extraction.
        Session 385: Enhanced to include sample articles for each topic.
        Session 385: Exclude job spiders by default to prevent job titles polluting trends.

        Get trending topics from spider data with smarter extraction:
        1. Prioritize tags/keywords from articles (most reliable)
        2. Extract meaningful phrases from titles (not single words)
        3. Filter out common stopwords aggressively
        4. Show actual headlines for context
        5. Include sample articles for each topic (Session 385)
        6. Exclude job spiders by default (Session 385)

        Args:
            category: Filter by category (tech, financial, jobs, etc.)
            hours: Look back period in hours
            limit: Maximum number of topics to return
            include_jobs: If True, include job spiders in trends (default False)

        Returns:
            List of trending topics with scores and sample articles
        """
        since = timezone.now() - timedelta(hours=hours)

        # Build query
        queryset = self.SpiderData.objects.filter(created_at__gte=since)

        # Session 385: Exclude job spiders unless explicitly requested or filtering by jobs category
        if not include_jobs and category != 'jobs':
            queryset = queryset.exclude(spider_name__in=self.JOB_SPIDERS)

        if category:
            spider_names = self.CATEGORY_MAPPINGS.get(category, [])
            if spider_names:
                queryset = queryset.filter(spider_name__in=spider_names)

        # Separate tracking for tags vs extracted keywords
        tag_counts = Counter()  # Tags are highest quality
        tag_sources = defaultdict(set)

        keyword_counts = Counter()  # Extracted keywords
        keyword_sources = defaultdict(set)

        # Session 385: Track articles per topic for display
        tag_articles = defaultdict(list)  # tag -> list of articles
        keyword_articles = defaultdict(list)  # keyword -> list of articles

        # Session 814: Limit entries scanned to prevent slow queries
        for entry in queryset[:self.MAX_ENTRIES_TO_SCAN]:
            if not entry.raw_data:
                continue

            # Session 535: Handle raw_data being string or dict
            raw_data = self._parse_raw_data(entry.raw_data)
            if raw_data is None:
                continue

            items = raw_data.get('items', [])
            for item in items:
                title = item.get('title') or item.get('name') or ''
                url = item.get('url') or item.get('link') or ''

                # Skip items without title or url
                if not title or len(title) < 10:
                    continue

                # Build article object for later use
                article = {
                    'title': title[:100],  # Truncate long titles
                    'url': url,
                    'source': entry.spider_name,
                    'description': (item.get('description') or item.get('summary') or '')[:150],
                    'tags': item.get('tags', [])[:5] if isinstance(item.get('tags'), list) else [],
                }

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
                        # Session 385: Track article for this tag (limit to 5 per tag)
                        if len(tag_articles[tag_clean]) < 5 and url:
                            tag_articles[tag_clean].append(article)

                # Priority 2: Extract meaningful keywords from titles
                if title:
                    keywords = self._extract_meaningful_keywords(title)
                    for kw in keywords:
                        keyword_counts[kw] += 1
                        keyword_sources[kw].add(entry.spider_name)
                        # Session 385: Track article for this keyword (limit to 5 per keyword)
                        if len(keyword_articles[kw]) < 5 and url:
                            keyword_articles[kw].append(article)

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
                'type': 'tag',
                'articles': tag_articles[tag][:5]  # Session 385: Include sample articles
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
                    'type': 'keyword',
                    'articles': keyword_articles[kw][:5]  # Session 385: Include sample articles
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
        # Session 814: Limit entries to prevent slow queries
        seen_crypto = set()
        for entry in crypto_data[:self.MAX_ENTRIES_TO_SCAN]:
            raw_data = self._parse_raw_data(entry.raw_data)
            if raw_data is None:
                continue
            items = raw_data.get('items', [])
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
        # Session 814: Limit entries to prevent slow queries
        seen_stocks = set()
        for entry in stock_data[:self.MAX_ENTRIES_TO_SCAN]:
            raw_data = self._parse_raw_data(entry.raw_data)
            if raw_data is None:
                continue
            items = raw_data.get('items', [])
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
        # Session 957: For 3D queries, include creative spiders that may have 3D content
        spider_sources = list(self.CATEGORY_MAPPINGS['tech'])
        if topic_filter == 'design':
            spider_sources.extend(['dribbble', 'behance', 'figma', 'canva', 'unsplash'])
        elif topic_filter == '3d':
            spider_sources.extend(['dribbble', 'behance', 'sketchfab', 'blender', 'cgtrader'])

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
            # Session 957: 3D modeling and design keywords
            '3d': ['3d model', '3d design', '3d print', '3d render', 'blender', 'maya', '3ds max',
                   'cinema 4d', 'c4d', 'unreal engine', 'unity 3d', 'sketchup', 'zbrush',
                   'substance painter', 'substance designer', 'houdini', 'rhino 3d', 'rhinoceros',
                   'solidworks', 'cad ', ' cad', 'autocad', 'fusion 360', 'tinkercad',
                   'game asset', 'game model', 'character model', 'environment art', 'prop art',
                   'hard surface', 'sculpting', 'texturing', 'uv mapping', 'rigging', 'animation',
                   'glb', 'gltf', 'fbx', 'obj file', 'stl file', 'mesh', 'polygon', 'voxel',
                   'metaverse', 'virtual world', 'ar model', 'vr model', 'spatial computing',
                   'sketchfab', 'cgtrader', 'turbosquid', 'artstation 3d', 'polycount'],
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

        # Session 814: Limit entries scanned to prevent slow queries
        for entry in tech_data[:self.MAX_ENTRIES_TO_SCAN]:
            raw_data = self._parse_raw_data(entry.raw_data)
            if raw_data is None:
                continue

            source = entry.spider_name
            items = raw_data.get('items', [])

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

        # Session 814: Limit entries to prevent slow queries
        for entry in job_data[:self.MAX_ENTRIES_TO_SCAN]:
            raw_data = self._parse_raw_data(entry.raw_data)
            if raw_data is None:
                continue

            source = entry.spider_name
            items = raw_data.get('items', [])

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

    # Session 814: Performance limit - max SpiderData entries to scan per search
    # Prevents timeouts when searching through thousands of entries
    MAX_ENTRIES_TO_SCAN = 300

    def search_spider_data(self, query: str, category: str = None,
                           hours: int = 72, limit: int = 50) -> list:
        """
        Full-text search across spider data.

        Session 294: Enhanced to handle multi-word queries better.
        - Strips boolean operators (OR, AND, quotes)
        - Splits query into individual terms
        - Matches if ANY term is found (OR logic)
        - Scores by number of matching terms

        Session 814: Performance optimization - limits entries scanned to MAX_ENTRIES_TO_SCAN
        to prevent 10+ minute query times when spider data volume is high.

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

        # Session 411: Whitelist of important short terms that should always be searched
        # These are valid tech/business terms that would otherwise be filtered
        important_short_terms = {'ai', 'ml', 'vr', 'ar', 'ux', 'ui', 'cv', 'nlp', 'api', 'sdk', 'b2b', 'b2c', 'saas', 'iot'}

        # Split into individual search terms (min 3 chars, but allow whitelisted short terms)
        # Session 411: Increased min length from 2 to 3 to reduce false positives
        search_terms = []
        for term in clean_query.split():
            term = term.strip()
            if len(term) >= 3:
                search_terms.append(term)
            elif term in important_short_terms:
                search_terms.append(term)

        # Filter out common words that are too generic
        # Session 411: Expanded stopwords list significantly
        stopwords = {
            'the', 'for', 'and', 'with', 'that', 'this', 'from', 'are', 'was', 'were',
            'has', 'have', 'had', 'been', 'being', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'shall', 'need', 'how', 'what', 'when',
            'where', 'why', 'who', 'which', 'all', 'any', 'both', 'each', 'few',
            'more', 'most', 'other', 'some', 'such', 'only', 'own', 'same', 'than',
            'too', 'very', 'just', 'also', 'now', 'new', 'your', 'our', 'his', 'her',
            'its', 'their', 'about', 'into', 'over', 'after', 'under', 'above',
            'pro', 'use', 'get', 'got', 'make', 'made', 'take', 'set', 'way', 'see'
        }
        search_terms = [t for t in search_terms if t not in stopwords]

        if not search_terms:
            return []

        # Build queryset
        queryset = self.SpiderData.objects.filter(created_at__gte=since)

        if category:
            spider_names = self.CATEGORY_MAPPINGS.get(category, [])
            if spider_names:
                queryset = queryset.filter(spider_name__in=spider_names)

        # Session 411: Exclude noisy spiders from general search
        # Weather, GIFs, and music don't help with business research
        noisy_spiders = {'noaa_weather', 'giphy', 'spotify', 'discord'}
        queryset = queryset.exclude(spider_name__in=noisy_spiders)

        results = []
        seen = set()

        # Session 814: Limit entries scanned to prevent timeouts
        # Most relevant data is in recent entries anyway (ordered by -created_at)
        for entry in queryset.order_by('-created_at')[:self.MAX_ENTRIES_TO_SCAN]:
            raw_data = self._parse_raw_data(entry.raw_data)
            if raw_data is None:
                continue

            items = raw_data.get('items', [])
            for item in items:
                # Search in title, description, tags
                title = item.get('title', '') or item.get('name', '')
                description = item.get('description', '') or item.get('summary', '')
                tags = ' '.join(item.get('tags', []) if isinstance(item.get('tags'), list) else [])

                searchable = f"{title} {description} {tags}".lower()

                # Session 411: Use word boundary matching instead of substring
                # This prevents "ai" matching "advis-ai-ry" or "f-ai-led"
                matching_terms = []
                for term in search_terms:
                    # Check if term appears as a whole word (with word boundaries)
                    pattern = r'\b' + re.escape(term) + r'\b'
                    if re.search(pattern, searchable):
                        matching_terms.append(term)

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

        # Session 814: Limit entries to prevent slow queries
        for entry in creative_data[:self.MAX_ENTRIES_TO_SCAN]:
            raw_data = self._parse_raw_data(entry.raw_data)
            if raw_data is None:
                continue

            sources_found.add(entry.spider_name)
            items = raw_data.get('items', [])

            for item in items:
                # Extract from title, description, tags
                # Session 646: Filter out None values to prevent join errors
                raw_tags = item.get('tags', [])
                safe_tags = [str(t) for t in raw_tags if t is not None] if isinstance(raw_tags, list) else []
                text_fields = [
                    item.get('title', '') or '',
                    item.get('description', '') or '',
                    ' '.join(safe_tags),
                    item.get('category', '') or '',
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
                        # Session 646: Filter None values before calling lower()
                        keywords.extend([str(t).lower() for t in tags[:5] if t is not None])

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
