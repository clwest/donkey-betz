"""
Smart Trending Service - Dynamic Topic Extraction & Spider Routing
===================================================================

Session 495: Replaces hardcoded if/elif topic filters with dynamic matching.
Works for ANY topic without needing code changes.

Features:
1. Dynamic topic extraction from natural language queries
2. Semantic matching to spider categories (with keyword fallback)
3. Category-aware spider data fetching
4. Caching layer for performance
5. Trending keyword extraction
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db.models import Count, Q
from django.utils import timezone

logger = logging.getLogger(__name__)


class SmartTrendingService:
    """
    Intelligent trending data service that dynamically matches queries to spider categories.

    Instead of hardcoded if/elif chains, this service:
    1. Extracts the topic from natural language
    2. Maps topics to spider categories using comprehensive keyword matching
    3. Fetches relevant spider data
    4. Returns formatted trends and articles
    """

    # Comprehensive category-to-keywords mapping
    # Easy to extend - just add keywords to existing categories or add new categories
    CATEGORY_KEYWORDS = {
        # Startup & Business
        'startups': [
            'startup', 'startups', 'founder', 'founders', 'entrepreneurship', 'entrepreneur',
            'venture', 'vc', 'seed', 'series a', 'series b', 'series c', 'funding round',
            'unicorn', 'valuation', 'pitch', 'accelerator', 'incubator', 'y combinator',
            'techstars', 'raise', 'raised', 'fundraising', 'pre-seed', 'angel investor'
        ],
        'business': [
            'business', 'enterprise', 'corporate', 'company', 'companies', 'industry',
            'market', 'commerce', 'b2b', 'b2c', 'strategy', 'management', 'leadership',
            'ceo', 'executive', 'merger', 'acquisition', 'm&a', 'ipo', 'public offering'
        ],
        'financial': [
            'finance', 'financial', 'stock', 'stocks', 'market', 'trading', 'investment',
            'investing', 'portfolio', 'hedge fund', 'etf', 'bonds', 'earnings', 'revenue',
            'profit', 'sec', '10-k', '10k', '8-k', '8k', 'quarterly', 'annual report',
            'wall street', 'nasdaq', 'nyse', 's&p', 'dow jones', 'bitcoin', 'crypto',
            'cryptocurrency', 'ethereum', 'defi', 'web3', 'blockchain', 'nft'
        ],

        # Technology
        'tech': [
            'tech', 'technology', 'software', 'hardware', 'computer', 'computing',
            'digital', 'innovation', 'disruption', 'silicon valley', 'big tech',
            'faang', 'google', 'apple', 'microsoft', 'amazon', 'meta', 'facebook'
        ],
        'ai_ml': [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
            'neural network', 'gpt', 'llm', 'large language model', 'chatgpt', 'openai',
            'anthropic', 'claude', 'gemini', 'transformer', 'generative ai', 'genai',
            'computer vision', 'nlp', 'natural language', 'robotics', 'automation'
        ],
        'cybersecurity': [
            'cybersecurity', 'cyber security', 'security', 'infosec', 'hacking', 'hacker',
            'breach', 'data breach', 'ransomware', 'malware', 'vulnerability', 'exploit',
            'zero-day', 'cve', 'patch', 'encryption', 'privacy', 'gdpr', 'ciso', 'soc',
            'threat', 'phishing', 'ddos', 'firewall', 'vpn', 'authentication'
        ],
        'web_development': [
            'web', 'web dev', 'web development', 'frontend', 'front-end', 'backend',
            'back-end', 'fullstack', 'full-stack', 'javascript', 'typescript', 'react',
            'vue', 'angular', 'node', 'python', 'django', 'flask', 'ruby', 'rails',
            'css', 'html', 'api', 'rest', 'graphql', 'microservices'
        ],
        'innovation': [
            'innovation', 'innovative', 'breakthrough', 'cutting-edge', 'emerging',
            'future', 'futuristic', 'next-gen', 'next generation', 'disruptive',
            'revolutionary', 'pioneering', 'research', 'r&d', 'patent'
        ],

        # Sector-Specific
        'healthtech': [
            'healthtech', 'health tech', 'healthcare', 'health care', 'medical',
            'medicine', 'biotech', 'biotechnology', 'pharma', 'pharmaceutical',
            'clinical', 'clinical trial', 'fda', 'drug', 'therapy', 'treatment',
            'diagnosis', 'telehealth', 'telemedicine', 'digital health', 'wearable',
            'fitness', 'wellness', 'mental health', 'genomics', 'precision medicine'
        ],
        'defense_tech': [
            'defense', 'defence', 'military', 'dod', 'department of defense', 'pentagon',
            'government contract', 'aerospace', 'space', 'satellite', 'rocket', 'missile',
            'drone', 'uav', 'autonomous weapons', 'defense contractor', 'lockheed',
            'raytheon', 'northrop', 'boeing defense', 'darpa', 'national security'
        ],
        'climate': [
            'climate', 'climate tech', 'cleantech', 'clean tech', 'sustainability',
            'sustainable', 'green', 'renewable', 'solar', 'wind', 'energy', 'carbon',
            'emissions', 'net zero', 'ev', 'electric vehicle', 'battery', 'hydrogen',
            'nuclear', 'fusion', 'environmental', 'esg'
        ],

        # Media & Content
        'news': [
            'news', 'breaking', 'headlines', 'current events', 'journalism',
            'media', 'press', 'reporter', 'coverage', 'story', 'stories'
        ],
        'entertainment': [
            'entertainment', 'movies', 'film', 'tv', 'television', 'streaming',
            'netflix', 'disney', 'hbo', 'hollywood', 'celebrity', 'music',
            'gaming', 'games', 'esports', 'twitch', 'youtube'
        ],
        'design': [
            'design', 'designer', 'ui', 'ux', 'user interface', 'user experience',
            'graphic design', 'visual', 'creative', 'branding', 'logo', 'typography',
            'figma', 'sketch', 'adobe', 'photoshop', 'illustrator', 'dribbble', 'behance'
        ],

        # Work & Career
        'jobs': [
            'jobs', 'job', 'career', 'hiring', 'employment', 'recruitment', 'recruiting',
            'talent', 'workforce', 'remote work', 'work from home', 'wfh', 'hybrid',
            'salary', 'compensation', 'benefits', 'interview', 'resume', 'linkedin'
        ],
        'remote_work': [
            'remote', 'remote work', 'work from home', 'wfh', 'distributed',
            'async', 'asynchronous', 'digital nomad', 'coworking', 'hybrid work'
        ],
        'freelance': [
            'freelance', 'freelancer', 'freelancing', 'gig', 'gig economy',
            'contractor', 'consulting', 'consultant', 'self-employed', 'solopreneur'
        ],

        # Other Verticals
        'real_estate': [
            'real estate', 'realestate', 'property', 'housing', 'home', 'homes',
            'mortgage', 'rent', 'rental', 'commercial real estate', 'proptech'
        ],
        'education': [
            'education', 'edtech', 'learning', 'school', 'university', 'college',
            'course', 'courses', 'training', 'skills', 'certification', 'online learning',
            'mooc', 'coursera', 'udemy', 'bootcamp'
        ],
        'science': [
            'science', 'scientific', 'research', 'study', 'discovery', 'physics',
            'chemistry', 'biology', 'astronomy', 'space', 'nasa', 'quantum'
        ],
        'legal': [
            'legal', 'law', 'lawyer', 'attorney', 'court', 'lawsuit', 'regulation',
            'compliance', 'litigation', 'contract', 'ip', 'intellectual property',
            'patent', 'trademark', 'copyright'
        ],
    }

    # Category aliases - map user-friendly terms to our categories
    CATEGORY_ALIASES = {
        'vc': 'startups',
        'venture capital': 'startups',
        'funding': 'startups',
        'tech startups': 'startups',

        'stocks': 'financial',
        'crypto': 'financial',
        'blockchain': 'financial',
        'trading': 'financial',
        'investing': 'financial',

        'artificial intelligence': 'ai_ml',
        'machine learning': 'ai_ml',
        'llms': 'ai_ml',
        'generative ai': 'ai_ml',

        'security': 'cybersecurity',
        'infosec': 'cybersecurity',
        'hacking': 'cybersecurity',

        'web dev': 'web_development',
        'frontend': 'web_development',
        'backend': 'web_development',

        'health': 'healthtech',
        'medical': 'healthtech',
        'biotech': 'healthtech',

        'defense': 'defense_tech',
        'military': 'defense_tech',
        'aerospace': 'defense_tech',

        'green tech': 'climate',
        'cleantech': 'climate',
        'sustainability': 'climate',

        'ui/ux': 'design',
        'graphic design': 'design',

        'careers': 'jobs',
        'hiring': 'jobs',
    }

    # Cache settings
    CACHE_TTL = 3600  # 1 hour
    CACHE_PREFIX = 'smart_trending_'

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_trending_for_query(
        self,
        query: str,
        hours: int = 72,
        article_limit: int = 15,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Main entry point: Get trending data for ANY natural language query.

        Args:
            query: Natural language query like "What's trending in startups?"
            hours: How far back to look for data (default 72 hours)
            article_limit: Max articles to return
            use_cache: Whether to use cached results

        Returns:
            {
                'trends': ['keyword1', 'keyword2', ...],
                'articles': [{'title': ..., 'url': ..., 'source': ...}, ...],
                'categories': ['startups', 'tech'],  # Matched categories
                'topic': 'startups',  # Extracted topic
                'cache_hit': True/False
            }
        """
        # Check cache first
        cache_key = f"{self.CACHE_PREFIX}{hash(query.lower())}_{hours}"
        if use_cache:
            cached = cache.get(cache_key)
            if cached:
                self.logger.info(f"Cache hit for query: {query[:50]}")
                cached['cache_hit'] = True
                return cached

        # Extract topic from query
        topic = self._extract_topic(query)
        self.logger.info(f"Extracted topic '{topic}' from query: {query[:50]}")

        # Map topic to spider categories
        categories = self._map_topic_to_categories(topic, query)
        self.logger.info(f"Mapped to categories: {categories}")

        # Fetch spider data for those categories
        articles = self._fetch_articles_for_categories(categories, hours, article_limit)

        # Extract trending keywords from articles
        trends = self._extract_trending_keywords(articles, topic)

        result = {
            'trends': trends,
            'articles': articles,
            'categories': categories,
            'topic': topic,
            'cache_hit': False
        }

        # Cache the result
        if use_cache:
            cache.set(cache_key, result, self.CACHE_TTL)

        return result

    def _extract_topic(self, query: str) -> str:
        """
        Extract the main topic from a natural language query.

        Examples:
            "What's trending in startups?" -> "startups"
            "Tell me about AI trends" -> "ai"
            "Show me cybersecurity news" -> "cybersecurity"
        """
        query_lower = query.lower()

        # Pattern 1: "trending in X" or "trends in X"
        patterns = [
            r"trending\s+in\s+([a-z\s\-]+?)(?:\?|$|\.|\s+and|\s+or)",
            r"trends?\s+in\s+([a-z\s\-]+?)(?:\?|$|\.|\s+and|\s+or)",
            r"what'?s?\s+(?:hot|new|happening)\s+in\s+([a-z\s\-]+?)(?:\?|$|\.)",
            r"news\s+(?:about|on|in)\s+([a-z\s\-]+?)(?:\?|$|\.)",
            r"(?:show|tell|give)\s+me\s+([a-z\s\-]+?)\s+(?:trends?|news|updates?)(?:\?|$|\.)",
            r"([a-z\s\-]+?)\s+(?:trends?|news|updates?)(?:\?|$|\.)",
        ]

        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                topic = match.group(1).strip()
                # Clean up common words
                topic = re.sub(r'\b(the|a|an|some|any|latest|recent|current)\b', '', topic).strip()
                if topic and len(topic) > 1:
                    return topic

        # Pattern 2: Direct category mention
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return keyword

        # Pattern 3: Check aliases
        for alias, category in self.CATEGORY_ALIASES.items():
            if alias in query_lower:
                return alias

        # Default: try to find the last noun-like word before ?
        words = re.findall(r'\b([a-z]{3,})\b', query_lower)
        stopwords = {'what', 'trending', 'trends', 'tell', 'show', 'give', 'about', 'the', 'and', 'for'}
        meaningful_words = [w for w in words if w not in stopwords]
        if meaningful_words:
            return meaningful_words[-1]

        return ''  # No topic found

    def _map_topic_to_categories(self, topic: str, query: str) -> List[str]:
        """
        Map an extracted topic to one or more spider categories.

        Uses both the topic and full query for better matching.
        """
        if not topic:
            # No specific topic - return general categories
            return ['tech', 'news', 'startups']

        topic_lower = topic.lower()
        query_lower = query.lower()
        matched_categories = []

        # Check direct aliases first
        if topic_lower in self.CATEGORY_ALIASES:
            matched_categories.append(self.CATEGORY_ALIASES[topic_lower])

        # Check each category's keywords
        category_scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in topic_lower:
                    score += 3  # Strong match on topic
                if keyword in query_lower:
                    score += 1  # Weaker match on full query
            if score > 0:
                category_scores[category] = score

        # Sort by score and take top matches
        sorted_categories = sorted(category_scores.items(), key=lambda x: -x[1])
        for cat, score in sorted_categories[:3]:  # Max 3 categories
            if score >= 2 and cat not in matched_categories:  # Threshold
                matched_categories.append(cat)

        # If still no matches, try fuzzy matching
        if not matched_categories:
            # Check if topic is similar to a category name
            for category in self.CATEGORY_KEYWORDS.keys():
                if topic_lower in category or category in topic_lower:
                    matched_categories.append(category)
                    break

        # Fallback to general categories
        if not matched_categories:
            matched_categories = ['tech', 'news']

        return matched_categories

    def _fetch_articles_for_categories(
        self,
        categories: List[str],
        hours: int,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Fetch spider data for the given categories.
        Handles different data formats from various spiders.
        """
        from core.models_unified_system import SpiderData
        from ai_core.spiders.spider_registry import SpiderRegistry

        # Get spiders for each category
        registry = SpiderRegistry()
        spider_names = []

        for category in categories:
            category_spiders = registry.get_spiders_by_category(category)
            spider_names.extend(category_spiders.keys())

        if not spider_names:
            # Fallback: get all spiders
            spider_names = list(registry.spider_classes.keys())[:20]

        # Query database
        cutoff = timezone.now() - timedelta(hours=hours)

        articles = []
        seen_titles = set()

        queryset = SpiderData.objects.filter(
            spider_name__in=spider_names,
            created_at__gte=cutoff
        ).order_by('-created_at')[:limit * 5]  # Fetch extra for dedup and format variations

        for item in queryset:
            raw_data = item.raw_data or {}

            # Handle different data formats
            extracted_articles = self._extract_articles_from_raw_data(raw_data, item.spider_name, item.source_url, item.created_at)

            for article in extracted_articles:
                title = article.get('title', '')

                # Deduplicate by title
                title_key = title.lower()[:50] if title else ''
                if title_key and title_key in seen_titles:
                    continue
                seen_titles.add(title_key)

                if title:
                    articles.append(article)

                if len(articles) >= limit:
                    break

            if len(articles) >= limit:
                break

        return articles

    def _extract_articles_from_raw_data(
        self,
        raw_data: Dict[str, Any],
        spider_name: str,
        source_url: str,
        created_at
    ) -> List[Dict[str, Any]]:
        """
        Extract article data from various raw_data formats.
        Different spiders store data differently - this normalizes them.
        """
        articles = []

        # Format 1: Direct title/summary (news spiders)
        if raw_data.get('title'):
            articles.append({
                'title': raw_data.get('title', ''),
                'url': raw_data.get('link', raw_data.get('url', source_url)),
                'source': spider_name,
                'summary': self._clean_html(raw_data.get('summary', raw_data.get('description', '')))[:300],
                'published': raw_data.get('published', ''),
                'created_at': created_at.isoformat() if created_at else '',
            })

        # Format 2: Items array (huggingface, kaggle, etc.)
        elif raw_data.get('items'):
            items = raw_data.get('items', [])
            for item in items[:5]:  # Limit items per spider record
                if isinstance(item, dict):
                    title = item.get('title', item.get('name', item.get('id', '')))
                    if title:
                        articles.append({
                            'title': title,
                            'url': item.get('url', item.get('link', source_url)),
                            'source': spider_name,
                            'summary': self._clean_html(item.get('description', item.get('summary', '')))[:300],
                            'published': item.get('published', item.get('created_at', '')),
                            'created_at': created_at.isoformat() if created_at else '',
                        })

        # Format 3: Name field (models, datasets)
        elif raw_data.get('name'):
            articles.append({
                'title': raw_data.get('name', ''),
                'url': raw_data.get('url', source_url),
                'source': spider_name,
                'summary': self._clean_html(raw_data.get('description', ''))[:300],
                'published': raw_data.get('created_at', ''),
                'created_at': created_at.isoformat() if created_at else '',
            })

        return articles

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags and clean up text."""
        if not text:
            return ''
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', str(text))
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

    def _extract_trending_keywords(
        self,
        articles: List[Dict[str, Any]],
        topic: str
    ) -> List[str]:
        """
        Extract trending keywords from article titles and summaries.
        Filters out HTML artifacts and common web terms.
        """
        from collections import Counter

        # Stopwords to filter out (including HTML/web artifacts)
        stopwords = {
            # Common English words
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
            'this', 'that', 'these', 'those', 'it', 'its', 'they', 'their',
            'what', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how',
            'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 'just', 'also', 'now', 'new', 'first', 'last', 'long', 'great',
            'little', 'own', 'other', 'old', 'right', 'big', 'high', 'different',
            'small', 'large', 'next', 'early', 'young', 'important', 'public',
            'says', 'said', 'year', 'years', 'day', 'days', 'week', 'month',
            'time', 'way', 'world', 'life', 'hand', 'part', 'place', 'case',
            'after', 'before', 'during', 'about', 'into', 'through', 'over',
            'between', 'out', 'up', 'down', 'off', 'above', 'below', 'under',
            'again', 'further', 'then', 'once', 'here', 'there', 'where', 'why',
            'how', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            # HTML/web artifacts
            'href', 'https', 'http', 'www', 'com', 'org', 'net', 'html', 'htm',
            'div', 'span', 'class', 'style', 'src', 'alt', 'img', 'link', 'rel',
            'dir', 'ltr', 'rtl', 'lang', 'amp', 'nbsp', 'quot', 'apos', 'lt', 'gt',
            'post', 'read', 'click', 'continue', 'article', 'content', 'page',
            # Common filler words
            'one', 'two', 'get', 'got', 'use', 'used', 'using', 'make', 'made',
            'see', 'look', 'like', 'want', 'know', 'think', 'take', 'come', 'give',
            'find', 'tell', 'ask', 'seem', 'feel', 'try', 'leave', 'call', 'keep',
            'let', 'begin', 'seem', 'help', 'show', 'hear', 'play', 'run', 'move',
        }

        word_counts = Counter()

        for article in articles:
            # Use cleaned title and summary
            title = self._clean_html(article.get('title', ''))
            summary = self._clean_html(article.get('summary', ''))
            text = f"{title} {summary}"

            # Extract words (3+ chars, alphabetic only)
            words = re.findall(r'\b([a-zA-Z]{3,})\b', text.lower())
            for word in words:
                if word not in stopwords and len(word) >= 3 and not word.isdigit():
                    word_counts[word] += 1

        # Get top 15 keywords, excluding the topic itself
        topic_words = set(topic.lower().split())
        trending = [
            word for word, count in word_counts.most_common(25)
            if word not in topic_words and count >= 2
        ][:15]

        return trending

    def get_categories(self) -> Dict[str, List[str]]:
        """Return all available categories and their keywords for debugging."""
        return self.CATEGORY_KEYWORDS

    def clear_cache(self, query: str = None):
        """Clear cache for a specific query or all trending caches."""
        if query:
            cache_key = f"{self.CACHE_PREFIX}{hash(query.lower())}_72"
            cache.delete(cache_key)
        else:
            # Note: Django cache doesn't support prefix deletion easily
            # This would need a more sophisticated cache implementation
            pass


# Singleton instance for easy import
_smart_trending_service = None

def get_smart_trending_service() -> SmartTrendingService:
    """Get the singleton SmartTrendingService instance."""
    global _smart_trending_service
    if _smart_trending_service is None:
        _smart_trending_service = SmartTrendingService()
    return _smart_trending_service
