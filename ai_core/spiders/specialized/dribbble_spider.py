"""
Dribbble Spider - Design Portfolio & Trends Intelligence
========================================================

Session 218: Specialized spider for Dribbble design platform.
Focuses on design trends, popular styles, and creative inspiration.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class DribbbleSpider(BaseIntelligenceSpider):
    """Dribbble design spider - portfolios, trends, and creative work"""

    # Dribbble RSS Feeds (Popular shots and categories)
    RSS_FEEDS = {
        'popular': 'https://dribbble.com/shots/popular.rss',
        'recent': 'https://dribbble.com/shots/recent.rss',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.design_categories = {
            'ui_ux': ['ui', 'ux', 'interface', 'user experience', 'dashboard', 'app design', 'mobile app'],
            'branding': ['logo', 'brand', 'identity', 'branding', 'logotype', 'brand identity'],
            'illustration': ['illustration', 'illustrator', 'character', 'drawing', 'artwork'],
            'web_design': ['website', 'web design', 'landing page', 'homepage', 'web'],
            'motion': ['animation', 'motion', 'animated', 'gif', 'lottie', 'video'],
            'typography': ['typography', 'type', 'font', 'lettering', 'typeface'],
            'icon': ['icon', 'iconography', 'icon set', 'icons'],
            '3d': ['3d', 'render', 'blender', 'cinema4d', 'c4d', 'octane'],
            'product': ['product design', 'mockup', 'packaging', 'product'],
        }

        self.style_indicators = {
            'minimalist': ['minimal', 'minimalist', 'clean', 'simple', 'whitespace'],
            'colorful': ['colorful', 'vibrant', 'gradient', 'bold colors', 'neon'],
            'dark_mode': ['dark', 'dark mode', 'dark theme', 'dark ui'],
            'retro': ['retro', 'vintage', 'nostalgic', '80s', '90s'],
            'futuristic': ['futuristic', 'cyber', 'tech', 'sci-fi', 'neon'],
            'organic': ['organic', 'nature', 'natural', 'botanical', 'earthy'],
            'glassmorphism': ['glass', 'glassmorphism', 'blur', 'frosted'],
            'neumorphism': ['neumorphism', 'soft ui', 'neumorphic'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from Dribbble"""
        try:
            all_shots = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:20]:
                            # Extract image from content if available
                            image_url = ''
                            if hasattr(entry, 'content') and entry.content:
                                content = entry.content[0].get('value', '')
                                # Try to extract image URL from content
                                if 'src="' in content:
                                    start = content.find('src="') + 5
                                    end = content.find('"', start)
                                    image_url = content[start:end]

                            shot = {
                                'title': entry.get('title', ''),
                                'description': entry.get('summary', entry.get('description', ''))[:300],
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'author': entry.get('author', 'Designer'),
                                'image_url': image_url,
                                'feed_source': feed_name,
                            }
                            if shot['title']:
                                all_shots.append(shot)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'shots': all_shots, 'source': 'dribbble'}

        except Exception as e:
            self.logger.error(f"Error fetching Dribbble data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Dribbble shots"""
        try:
            shots = raw_data.get('shots', [])
            processed_shots = []

            for shot in shots:
                processed = self._process_shot(shot)
                if processed:
                    processed_shots.append(processed)

            # Generate design insights
            insights = self._generate_design_insights(processed_shots)

            content = {
                'shots': processed_shots,
                'insights': insights,
                'trending_styles': self._analyze_trending_styles(processed_shots),
                'category_breakdown': self._analyze_categories(processed_shots),
                'top_designers': self._extract_top_designers(processed_shots),
                'style_inspiration': self._generate_style_inspiration(processed_shots),
            }

            quality_score = min(1.0, len(processed_shots) / 30 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='dribbble.com',
                data_type='design_portfolio',
                content=content,
                metadata={
                    'shot_count': len(processed_shots),
                    'source': 'dribbble',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['design', 'ui', 'ux', 'illustration', 'branding', 'creative'],
                target_agents=['design_agent', 'trend_analysis_agent', 'creative_agent'],
                target_advisors=['design_director', 'creative_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Dribbble data: {e}")
            return None

    def _process_shot(self, shot: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual shot"""
        try:
            title = shot.get('title', '')
            description = shot.get('description', '')
            text = f"{title} {description}".lower()

            # Identify design categories
            categories = []
            for cat, keywords in self.design_categories.items():
                if any(kw in text for kw in keywords):
                    categories.append(cat)

            # Identify style indicators
            styles = []
            for style, keywords in self.style_indicators.items():
                if any(kw in text for kw in keywords):
                    styles.append(style)

            # Determine if it's a popular shot (from popular feed)
            is_popular = shot.get('feed_source') == 'popular'

            return {
                'title': title,
                'description': description,
                'link': shot.get('link', ''),
                'published': shot.get('published', ''),
                'author': shot.get('author', ''),
                'image_url': shot.get('image_url', ''),
                'categories': categories or ['general'],
                'styles': styles or ['contemporary'],
                'is_popular': is_popular,
            }

        except Exception as e:
            self.logger.warning(f"Error processing shot: {e}")
            return None

    def _generate_design_insights(self, shots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate design trend insights"""
        if not shots:
            return {}

        popular = [s for s in shots if s.get('is_popular')]

        # Count categories
        cat_counts = {}
        for shot in shots:
            for cat in shot.get('categories', []):
                cat_counts[cat] = cat_counts.get(cat, 0) + 1

        # Count styles
        style_counts = {}
        for shot in shots:
            for style in shot.get('styles', []):
                style_counts[style] = style_counts.get(style, 0) + 1

        top_categories = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_styles = sorted(style_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            'total_shots': len(shots),
            'popular_shots': len(popular),
            'hot_categories': [c[0] for c in top_categories],
            'trending_styles': [s[0] for s in top_styles],
            'design_mood': self._assess_design_mood(shots),
        }

    def _assess_design_mood(self, shots: List[Dict[str, Any]]) -> str:
        """Assess overall design mood"""
        style_counts = {}
        for shot in shots:
            for style in shot.get('styles', []):
                style_counts[style] = style_counts.get(style, 0) + 1

        if style_counts.get('minimalist', 0) > len(shots) // 4:
            return 'clean & minimal'
        elif style_counts.get('colorful', 0) > len(shots) // 4:
            return 'vibrant & bold'
        elif style_counts.get('dark_mode', 0) > len(shots) // 4:
            return 'dark & moody'
        return 'diverse'

    def _analyze_trending_styles(self, shots: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze trending design styles"""
        style_counts = {}
        for shot in shots:
            for style in shot.get('styles', []):
                style_counts[style] = style_counts.get(style, 0) + 1

        return dict(sorted(style_counts.items(), key=lambda x: x[1], reverse=True))

    def _analyze_categories(self, shots: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze shots by category"""
        categories = {}

        for shot in shots:
            for cat in shot.get('categories', ['general']):
                if cat not in categories:
                    categories[cat] = {'count': 0, 'popular': 0, 'examples': []}
                categories[cat]['count'] += 1
                if shot.get('is_popular'):
                    categories[cat]['popular'] += 1
                if len(categories[cat]['examples']) < 2:
                    categories[cat]['examples'].append(shot.get('title'))

        return categories

    def _extract_top_designers(self, shots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract top designers from popular shots"""
        designer_counts = {}
        for shot in shots:
            if shot.get('is_popular'):
                author = shot.get('author', 'Unknown')
                if author not in designer_counts:
                    designer_counts[author] = {'count': 0, 'works': []}
                designer_counts[author]['count'] += 1
                if len(designer_counts[author]['works']) < 2:
                    designer_counts[author]['works'].append(shot.get('title'))

        sorted_designers = sorted(designer_counts.items(), key=lambda x: x[1]['count'], reverse=True)
        return [{'name': d[0], **d[1]} for d in sorted_designers[:5]]

    def _generate_style_inspiration(self, shots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate style inspiration from popular shots"""
        inspiration = []
        for shot in shots:
            if shot.get('is_popular') and shot.get('styles'):
                inspiration.append({
                    'title': shot.get('title'),
                    'styles': shot.get('styles'),
                    'categories': shot.get('categories'),
                    'link': shot.get('link'),
                    'image': shot.get('image_url'),
                })
        return inspiration[:10]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['design', 'ui', 'ux', 'illustration', 'logo', 'branding', 'creative']
