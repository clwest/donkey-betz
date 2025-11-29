"""
Unsplash Spider - Visual Trends & Photography Intelligence
============================================================

Session 263: Specialized spider for Unsplash visual trends.
Tracks trending photography styles, compositions, colors, and subjects
to inform AI image generation prompts and style recommendations.

Requires UNSPLASH_ACCESS_KEY environment variable.
Free tier: 50 requests/hour.
"""

import os
import asyncio
import aiohttp
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from collections import Counter

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class UnsplashSpider(BaseIntelligenceSpider):
    """Unsplash spider - visual trends and photography intelligence"""

    BASE_URL = 'https://api.unsplash.com'

    # Topics to track for visual trends
    TOPICS = [
        'technology',
        'business-work',
        'arts-culture',
        'nature',
        'architecture-interior',
        'experimental',
        'textures-patterns',
        '3d-renders',
    ]

    # Collections to monitor
    COLLECTIONS = {
        'editorial': 317099,  # Unsplash Editorial
        'trending': 3330448,  # Trending on Unsplash
        'minimal': 162468,    # Minimal
        'dark': 181581,       # Dark & Moody
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.access_key = os.getenv('UNSPLASH_ACCESS_KEY', '')

        self.headers = {
            'Authorization': f'Client-ID {self.access_key}',
            'Accept-Version': 'v1',
        }

        # Color palette categories for trend detection
        self.color_categories = {
            'warm': ['red', 'orange', 'yellow', 'brown'],
            'cool': ['blue', 'cyan', 'teal', 'green'],
            'neutral': ['black', 'white', 'gray', 'grey'],
            'vibrant': ['purple', 'pink', 'magenta'],
        }

        # Subject matter keywords
        self.subjects = {
            'portrait': ['portrait', 'face', 'person', 'people', 'model'],
            'landscape': ['landscape', 'nature', 'mountain', 'ocean', 'sky'],
            'urban': ['city', 'street', 'building', 'architecture', 'urban'],
            'abstract': ['abstract', 'texture', 'pattern', 'geometric', 'minimal'],
            'technology': ['tech', 'computer', 'digital', 'ai', 'robot'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch visual trends from Unsplash API"""
        if not self.access_key:
            self.logger.warning("UNSPLASH_ACCESS_KEY not configured - using limited public data")

        try:
            all_photos = []
            topic_photos = {}
            collection_photos = {}

            async with aiohttp.ClientSession(headers=self.headers) as session:
                # Fetch popular photos
                try:
                    url = f"{self.BASE_URL}/photos?order_by=popular&per_page=30"
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            photos = await response.json()
                            for photo in photos:
                                all_photos.append(self._extract_photo_data(photo, 'popular'))
                except Exception as e:
                    self.logger.warning(f"Error fetching popular photos: {e}")

                await asyncio.sleep(0.5)

                # Fetch from topics (limited to avoid rate limits)
                for topic in self.TOPICS[:4]:
                    try:
                        url = f"{self.BASE_URL}/topics/{topic}/photos?per_page=10"
                        async with session.get(url, timeout=10) as response:
                            if response.status == 200:
                                photos = await response.json()
                                topic_photos[topic] = []
                                for photo in photos:
                                    photo_data = self._extract_photo_data(photo, f'topic:{topic}')
                                    all_photos.append(photo_data)
                                    topic_photos[topic].append(photo_data)
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        self.logger.warning(f"Error fetching topic {topic}: {e}")

                # Fetch editorial/trending collections (limited)
                for collection_name, collection_id in list(self.COLLECTIONS.items())[:2]:
                    try:
                        url = f"{self.BASE_URL}/collections/{collection_id}/photos?per_page=10"
                        async with session.get(url, timeout=10) as response:
                            if response.status == 200:
                                photos = await response.json()
                                collection_photos[collection_name] = []
                                for photo in photos:
                                    photo_data = self._extract_photo_data(photo, f'collection:{collection_name}')
                                    all_photos.append(photo_data)
                                    collection_photos[collection_name].append(photo_data)
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        self.logger.warning(f"Error fetching collection {collection_name}: {e}")

            return {
                'photos': all_photos,
                'topic_photos': topic_photos,
                'collection_photos': collection_photos,
                'source': 'unsplash'
            }

        except Exception as e:
            self.logger.error(f"Error fetching Unsplash data: {e}")
            return None

    def _extract_photo_data(self, photo: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Extract relevant data from photo object"""
        return {
            'id': photo.get('id', ''),
            'description': photo.get('description') or photo.get('alt_description') or '',
            'width': photo.get('width', 0),
            'height': photo.get('height', 0),
            'color': photo.get('color', ''),
            'likes': photo.get('likes', 0),
            'downloads': photo.get('downloads', 0),
            'views': photo.get('views', 0),
            'urls': {
                'thumb': photo.get('urls', {}).get('thumb', ''),
                'small': photo.get('urls', {}).get('small', ''),
                'regular': photo.get('urls', {}).get('regular', ''),
            },
            'tags': [tag.get('title', '') for tag in photo.get('tags', [])[:10]],
            'user': photo.get('user', {}).get('username', ''),
            'source': source,
            'created_at': photo.get('created_at', ''),
        }

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Unsplash photos into visual trends intelligence"""
        try:
            photos = raw_data.get('photos', [])
            topic_photos = raw_data.get('topic_photos', {})
            collection_photos = raw_data.get('collection_photos', {})

            processed_photos = []
            for photo in photos:
                processed = self._process_photo(photo)
                if processed:
                    processed_photos.append(processed)

            insights = self._generate_insights(processed_photos)
            color_trends = self._analyze_color_trends(processed_photos)
            subject_trends = self._analyze_subject_trends(processed_photos)
            style_recommendations = self._generate_style_recommendations(processed_photos)

            content = {
                'photos': processed_photos[:50],  # Limit stored photos
                'insights': insights,
                'color_trends': color_trends,
                'subject_trends': subject_trends,
                'style_recommendations': style_recommendations,
                'topic_highlights': self._summarize_topics(topic_photos),
                'collection_highlights': self._summarize_collections(collection_photos),
                'trending_tags': self._extract_trending_tags(processed_photos),
            }

            quality_score = min(1.0, len(processed_photos) / 50 + 0.4)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='unsplash.com',
                data_type='visual_trends',
                content=content,
                metadata={
                    'photo_count': len(processed_photos),
                    'source': 'unsplash',
                    'topics_covered': list(topic_photos.keys()),
                    'collections_covered': list(collection_photos.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['unsplash', 'photography', 'visual trends', 'colors', 'styles', 'ai prompts'],
                target_agents=['image_agent', 'creative_director_agent', 'trend_analysis_agent'],
                target_advisors=['creative_advisor', 'visual_strategist', 'brand_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing Unsplash data: {e}")
            return None

    def _process_photo(self, photo: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual photo for trend analysis"""
        try:
            description = photo.get('description', '').lower()
            tags = [t.lower() for t in photo.get('tags', [])]
            text = f"{description} {' '.join(tags)}"

            # Detect subject category
            detected_subjects = []
            for subject, keywords in self.subjects.items():
                if any(kw in text for kw in keywords):
                    detected_subjects.append(subject)

            # Detect color category
            color = photo.get('color', '').lower().replace('#', '')
            color_category = self._categorize_color(color)

            # Calculate aspect ratio
            width = photo.get('width', 1)
            height = photo.get('height', 1)
            aspect_ratio = round(width / height, 2) if height > 0 else 1.0

            # Orientation
            if aspect_ratio > 1.2:
                orientation = 'landscape'
            elif aspect_ratio < 0.8:
                orientation = 'portrait'
            else:
                orientation = 'square'

            # Engagement score
            likes = photo.get('likes', 0)
            views = photo.get('views', 1) or 1
            engagement = min(1.0, (likes / views) * 100) if views > 0 else 0

            return {
                'id': photo.get('id'),
                'description': photo.get('description', ''),
                'tags': photo.get('tags', []),
                'color': photo.get('color', ''),
                'color_category': color_category,
                'subjects': detected_subjects,
                'aspect_ratio': aspect_ratio,
                'orientation': orientation,
                'likes': likes,
                'engagement': engagement,
                'urls': photo.get('urls', {}),
                'user': photo.get('user', ''),
                'source': photo.get('source', ''),
            }

        except Exception as e:
            self.logger.warning(f"Error processing photo: {e}")
            return None

    def _categorize_color(self, hex_color: str) -> str:
        """Categorize hex color into warm/cool/neutral/vibrant"""
        # Simplified color categorization based on hex
        if not hex_color or len(hex_color) < 6:
            return 'unknown'

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            # Neutral (grayscale-ish)
            if abs(r - g) < 30 and abs(g - b) < 30 and abs(r - b) < 30:
                return 'neutral'

            # Warm (red/orange/yellow dominant)
            if r > g and r > b:
                return 'warm'

            # Cool (blue/green dominant)
            if b > r and b >= g:
                return 'cool'

            if g > r and g > b:
                return 'cool'

            # Vibrant (purple/pink)
            if r > g and b > g:
                return 'vibrant'

            return 'neutral'

        except ValueError:
            return 'unknown'

    def _generate_insights(self, photos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate visual trend insights"""
        if not photos:
            return {}

        # Orientation distribution
        orientations = Counter(p.get('orientation', 'unknown') for p in photos)

        # Color category distribution
        colors = Counter(p.get('color_category', 'unknown') for p in photos)

        # Subject distribution
        all_subjects = []
        for p in photos:
            all_subjects.extend(p.get('subjects', []))
        subjects = Counter(all_subjects)

        # Average engagement
        engagements = [p.get('engagement', 0) for p in photos]
        avg_engagement = sum(engagements) / len(engagements) if engagements else 0

        return {
            'total_photos': len(photos),
            'orientation_distribution': dict(orientations),
            'color_distribution': dict(colors),
            'subject_distribution': dict(subjects.most_common(5)),
            'average_engagement': round(avg_engagement, 4),
            'dominant_orientation': orientations.most_common(1)[0][0] if orientations else 'unknown',
            'dominant_color_mood': colors.most_common(1)[0][0] if colors else 'unknown',
            'dominant_subject': subjects.most_common(1)[0][0] if subjects else 'general',
        }

    def _analyze_color_trends(self, photos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze color trends in photos"""
        colors = Counter(p.get('color_category', 'unknown') for p in photos)
        hex_colors = [p.get('color', '') for p in photos if p.get('color')]

        return {
            'category_distribution': dict(colors),
            'trending_palette': colors.most_common(3),
            'sample_hex_colors': hex_colors[:10],
            'mood': 'warm' if colors.get('warm', 0) > colors.get('cool', 0) else 'cool',
        }

    def _analyze_subject_trends(self, photos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze subject matter trends"""
        all_subjects = []
        for p in photos:
            all_subjects.extend(p.get('subjects', []))

        subject_counts = Counter(all_subjects)

        return {
            'distribution': dict(subject_counts),
            'trending': subject_counts.most_common(3),
            'emerging': [s for s, c in subject_counts.items() if c >= 2][:5],
        }

    def _generate_style_recommendations(self, photos: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate AI prompt style recommendations based on trends"""
        insights = self._generate_insights(photos)

        recommendations = []

        # Based on color mood
        color_mood = insights.get('dominant_color_mood', 'neutral')
        if color_mood == 'warm':
            recommendations.append({
                'style': 'Golden Hour',
                'prompt_modifier': 'warm golden lighting, orange and yellow tones, sunset ambiance',
            })
        elif color_mood == 'cool':
            recommendations.append({
                'style': 'Blue Hour',
                'prompt_modifier': 'cool blue tones, twilight atmosphere, serene and calm',
            })

        # Based on orientation
        orientation = insights.get('dominant_orientation', 'landscape')
        recommendations.append({
            'style': f'{orientation.title()} Composition',
            'prompt_modifier': f'{orientation} orientation, balanced composition, professional framing',
        })

        # Based on subject
        subject = insights.get('dominant_subject', 'general')
        subject_prompts = {
            'portrait': 'professional portrait photography, shallow depth of field, studio lighting',
            'landscape': 'epic landscape, dramatic sky, golden hour, high dynamic range',
            'urban': 'urban photography, city lights, architectural details, modern aesthetic',
            'abstract': 'abstract composition, geometric patterns, minimalist design',
            'technology': 'futuristic tech aesthetic, clean lines, digital art style',
        }
        recommendations.append({
            'style': f'{subject.title()} Focus',
            'prompt_modifier': subject_prompts.get(subject, 'professional photography style'),
        })

        return recommendations

    def _summarize_topics(self, topic_photos: Dict[str, List]) -> Dict[str, Dict]:
        """Summarize photos by topic"""
        summaries = {}
        for topic, photos in topic_photos.items():
            if photos:
                summaries[topic] = {
                    'count': len(photos),
                    'sample_tags': self._get_common_tags(photos)[:5],
                    'top_photo': photos[0].get('urls', {}).get('thumb', '') if photos else '',
                }
        return summaries

    def _summarize_collections(self, collection_photos: Dict[str, List]) -> Dict[str, Dict]:
        """Summarize photos by collection"""
        summaries = {}
        for collection, photos in collection_photos.items():
            if photos:
                summaries[collection] = {
                    'count': len(photos),
                    'sample_tags': self._get_common_tags(photos)[:5],
                    'mood': self._detect_collection_mood(photos),
                }
        return summaries

    def _get_common_tags(self, photos: List[Dict]) -> List[str]:
        """Get most common tags from photo list"""
        all_tags = []
        for photo in photos:
            all_tags.extend(photo.get('tags', []))
        return [tag for tag, _ in Counter(all_tags).most_common(10)]

    def _detect_collection_mood(self, photos: List[Dict]) -> str:
        """Detect overall mood of collection"""
        colors = Counter(p.get('color_category', 'neutral') for p in photos)
        return colors.most_common(1)[0][0] if colors else 'neutral'

    def _extract_trending_tags(self, photos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending tags across all photos"""
        all_tags = []
        for photo in photos:
            all_tags.extend(photo.get('tags', []))

        tag_counts = Counter(all_tags)
        return [{'tag': tag, 'count': count} for tag, count in tag_counts.most_common(20)]

    def get_required_fields(self) -> List[str]:
        return ['id']

    def get_relevance_keywords(self) -> List[str]:
        return ['unsplash', 'photography', 'visual', 'trends', 'colors', 'composition', 'style', 'ai prompts']
