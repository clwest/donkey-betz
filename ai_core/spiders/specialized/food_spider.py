"""
Food Spider - Food, Cooking & Restaurant Industry
=================================================

Session 534: Simplified to work with spider network interface.
Aggregates food, cooking, and restaurant industry content via RSS.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class FoodSpider:
    """Food spider - recipes, cooking, and restaurant industry news"""

    name = "food"

    # Food and cooking RSS feeds
    RSS_FEEDS = {
        'serious_eats': 'https://www.seriouseats.com/feed.rss',
        'bon_appetit': 'https://www.bonappetit.com/feed/rss',
        'epicurious': 'https://www.epicurious.com/feed/rss',
        'eater': 'https://www.eater.com/rss/index.xml',
        'food52': 'https://food52.com/blog/feed',
        'budget_bytes': 'https://www.budgetbytes.com/feed/',
        'minimalist_baker': 'https://minimalistbaker.com/feed/',
    }

    # Food categories
    CATEGORIES = [
        ('Recipes', 'recipes', 'Cooking recipes and techniques.'),
        ('Restaurant', 'restaurant', 'Restaurant news and reviews.'),
        ('Healthy', 'healthy', 'Healthy eating and nutrition.'),
        ('Budget', 'budget', 'Budget-friendly cooking.'),
        ('Quick & Easy', 'quick', 'Fast and simple recipes.'),
        ('Baking', 'baking', 'Baking and desserts.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.food_categories = {
            'recipes': ['recipe', 'cook', 'bake', 'prepare', 'ingredient', 'dish'],
            'restaurant': ['restaurant', 'chef', 'dining', 'menu', 'reservation'],
            'healthy': ['healthy', 'vegan', 'vegetarian', 'organic', 'diet', 'nutrition'],
            'budget': ['budget', 'cheap', 'affordable', 'save', 'frugal'],
            'quick_easy': ['quick', 'easy', 'simple', 'minute', 'weeknight', 'fast'],
            'baking': ['bake', 'bread', 'cake', 'cookie', 'dessert', 'pastry'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch food content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of food content dictionaries
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

        # Add category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting food categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Food spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from food RSS feed."""
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
                    summary = re.sub(r'<[^>]+>', '', summary)[:400]

                # Detect food category
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                is_recipe = self._is_recipe(text)
                dietary = self._detect_dietary(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name.replace('_', ' ').title()),
                    'category': category,
                    'food_category': category,
                    'is_recipe': is_recipe,
                    'dietary_tags': dietary,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'food_content',
                    'platform': 'food',
                    'tags': ['food', 'cooking', category] + dietary,
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect food category from text."""
        for category, keywords in self.food_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _is_recipe(self, text: str) -> bool:
        """Check if content is a recipe."""
        recipe_words = ['recipe', 'ingredient', 'cook', 'bake', 'prepare', 'serve']
        return any(word in text for word in recipe_words)

    def _detect_dietary(self, text: str) -> List[str]:
        """Detect dietary tags from text."""
        dietary_map = {
            'vegan': ['vegan', 'plant-based'],
            'vegetarian': ['vegetarian', 'meatless'],
            'gluten_free': ['gluten-free', 'gluten free', 'celiac'],
            'dairy_free': ['dairy-free', 'dairy free', 'lactose'],
            'keto': ['keto', 'low-carb', 'low carb'],
            'paleo': ['paleo'],
        }
        tags = []
        for tag, keywords in dietary_map.items():
            if any(kw in text for kw in keywords):
                tags.append(tag)
        return tags

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return food category links."""
        return [
            {
                'title': f"Food: {name}",
                'url': f'https://www.seriouseats.com/{slug}',
                'link': f'https://www.seriouseats.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Food',
                'data_type': 'food_category',
                'platform': 'food',
                'tags': ['food', 'cooking', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Recipe Collections', 'recipes', 'Popular recipes and guides.'),
            ('Restaurant News', 'restaurant', 'Dining and chef news.'),
            ('Healthy Eating', 'healthy', 'Nutritious cooking.'),
            ('Budget Cooking', 'budget', 'Affordable meal ideas.'),
            ('Quick Meals', 'quick', 'Fast weeknight dinners.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.seriouseats.com/{category}',
                'link': f'https://www.seriouseats.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Food',
                'data_type': 'food_topic',
                'platform': 'food',
                'tags': ['food', 'cooking', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
