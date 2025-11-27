"""
Behance Spider - Creative Portfolio & Project Intelligence
==========================================================

Session 218: Specialized spider for Behance creative platform.
Focuses on creative projects, design portfolios, and artistic trends.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class BehanceSpider(BaseIntelligenceSpider):
    """Behance creative spider - projects, portfolios, and creative work"""

    # Behance RSS Feeds
    RSS_FEEDS = {
        'featured': 'https://www.behance.net/feeds/projects',
        'curated': 'https://www.behance.net/feeds/curated',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.creative_fields = {
            'graphic_design': ['graphic design', 'poster', 'print', 'layout', 'editorial'],
            'branding': ['branding', 'brand', 'identity', 'logo', 'visual identity'],
            'ui_ux': ['ui', 'ux', 'interface', 'app design', 'web design', 'interaction'],
            'illustration': ['illustration', 'digital art', 'character', 'concept art'],
            'photography': ['photography', 'photo', 'portrait', 'landscape', 'commercial'],
            'motion': ['motion graphics', 'animation', 'video', 'after effects', '3d animation'],
            'advertising': ['advertising', 'campaign', 'ad', 'commercial', 'marketing'],
            'packaging': ['packaging', 'package design', 'label', 'product packaging'],
            'architecture': ['architecture', 'interior', 'space design', 'architectural'],
            'fashion': ['fashion', 'apparel', 'clothing', 'textile', 'fashion design'],
            '3d_cgi': ['3d', 'cgi', 'render', 'blender', 'cinema 4d', 'octane'],
        }

        self.project_types = {
            'commercial': ['client', 'brand', 'company', 'agency', 'commissioned'],
            'personal': ['personal project', 'self-initiated', 'passion project', 'side project'],
            'concept': ['concept', 'experimental', 'exploration', 'study'],
            'student': ['student', 'school', 'university', 'thesis', 'graduate'],
        }

        self.quality_indicators = {
            'featured': ['featured', 'curated', 'gallery', 'appreciated'],
            'detailed': ['process', 'case study', 'behind the scenes', 'making of'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from Behance"""
        try:
            all_projects = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:20]:
                            # Extract image from content
                            image_url = ''
                            description = ''

                            if hasattr(entry, 'content') and entry.content:
                                content = entry.content[0].get('value', '')
                                description = content[:400]
                                # Try to extract image
                                if 'src="' in content:
                                    start = content.find('src="') + 5
                                    end = content.find('"', start)
                                    image_url = content[start:end]
                            elif hasattr(entry, 'summary'):
                                description = entry.summary[:400]

                            project = {
                                'title': entry.get('title', ''),
                                'description': description,
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'author': entry.get('author', 'Creative'),
                                'image_url': image_url,
                                'tags': [tag.term for tag in entry.get('tags', [])] if hasattr(entry, 'tags') else [],
                                'feed_source': feed_name,
                            }
                            if project['title']:
                                all_projects.append(project)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'projects': all_projects, 'source': 'behance'}

        except Exception as e:
            self.logger.error(f"Error fetching Behance data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Behance projects"""
        try:
            projects = raw_data.get('projects', [])
            processed_projects = []

            for project in projects:
                processed = self._process_project(project)
                if processed:
                    processed_projects.append(processed)

            # Generate creative insights
            insights = self._generate_creative_insights(processed_projects)

            content = {
                'projects': processed_projects,
                'insights': insights,
                'field_analysis': self._analyze_creative_fields(processed_projects),
                'trending_fields': self._get_trending_fields(processed_projects),
                'featured_work': self._extract_featured_work(processed_projects),
                'creative_inspiration': self._generate_inspiration(processed_projects),
            }

            quality_score = min(1.0, len(processed_projects) / 30 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='behance.net',
                data_type='creative_portfolio',
                content=content,
                metadata={
                    'project_count': len(processed_projects),
                    'source': 'behance',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                    'featured_count': len([p for p in processed_projects if p.get('is_featured')]),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['design', 'creative', 'portfolio', 'art', 'branding', 'illustration'],
                target_agents=['design_agent', 'trend_analysis_agent', 'creative_agent'],
                target_advisors=['creative_director', 'art_director']
            )

        except Exception as e:
            self.logger.error(f"Error processing Behance data: {e}")
            return None

    def _process_project(self, project: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual project"""
        try:
            title = project.get('title', '')
            description = project.get('description', '')
            text = f"{title} {description}".lower()
            tags = project.get('tags', [])
            tag_text = ' '.join(tags).lower()
            full_text = f"{text} {tag_text}"

            # Identify creative fields
            fields = []
            for field, keywords in self.creative_fields.items():
                if any(kw in full_text for kw in keywords):
                    fields.append(field)

            # Identify project type
            project_type = 'personal'
            for ptype, keywords in self.project_types.items():
                if any(kw in full_text for kw in keywords):
                    project_type = ptype
                    break

            # Check quality indicators
            is_featured = project.get('feed_source') == 'featured' or project.get('feed_source') == 'curated'
            has_case_study = any(ind in full_text for ind in self.quality_indicators['detailed'])

            return {
                'title': title,
                'description': description[:300] if description else '',
                'link': project.get('link', ''),
                'published': project.get('published', ''),
                'author': project.get('author', ''),
                'image_url': project.get('image_url', ''),
                'creative_fields': fields or ['mixed_media'],
                'project_type': project_type,
                'is_featured': is_featured,
                'has_case_study': has_case_study,
                'tags': tags,
            }

        except Exception as e:
            self.logger.warning(f"Error processing project: {e}")
            return None

    def _generate_creative_insights(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate creative trend insights"""
        if not projects:
            return {}

        featured = [p for p in projects if p.get('is_featured')]
        case_studies = [p for p in projects if p.get('has_case_study')]

        # Count fields
        field_counts = {}
        for project in projects:
            for field in project.get('creative_fields', []):
                field_counts[field] = field_counts.get(field, 0) + 1

        # Count project types
        type_counts = {}
        for project in projects:
            ptype = project.get('project_type', 'personal')
            type_counts[ptype] = type_counts.get(ptype, 0) + 1

        top_fields = sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            'total_projects': len(projects),
            'featured_projects': len(featured),
            'case_studies': len(case_studies),
            'hot_fields': [f[0] for f in top_fields],
            'project_mix': type_counts,
            'creative_pulse': 'high' if len(featured) > len(projects) // 2 else 'steady',
        }

    def _analyze_creative_fields(self, projects: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze projects by creative field"""
        fields = {}

        for project in projects:
            for field in project.get('creative_fields', ['mixed_media']):
                if field not in fields:
                    fields[field] = {'count': 0, 'featured': 0, 'examples': []}
                fields[field]['count'] += 1
                if project.get('is_featured'):
                    fields[field]['featured'] += 1
                if len(fields[field]['examples']) < 2:
                    fields[field]['examples'].append(project.get('title'))

        return fields

    def _get_trending_fields(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get trending creative fields"""
        field_counts = {}
        for project in projects:
            for field in project.get('creative_fields', []):
                field_counts[field] = field_counts.get(field, 0) + 1

        sorted_fields = sorted(field_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'field': f[0], 'count': f[1]} for f in sorted_fields[:8]]

    def _extract_featured_work(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract featured creative work"""
        featured = []
        for project in projects:
            if project.get('is_featured'):
                featured.append({
                    'title': project.get('title'),
                    'author': project.get('author'),
                    'fields': project.get('creative_fields'),
                    'link': project.get('link'),
                    'image': project.get('image_url'),
                    'has_case_study': project.get('has_case_study'),
                })
        return featured[:10]

    def _generate_inspiration(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate creative inspiration from top projects"""
        inspiration = []

        # Prioritize featured projects with case studies
        sorted_projects = sorted(
            projects,
            key=lambda x: (x.get('is_featured', False), x.get('has_case_study', False)),
            reverse=True
        )

        for project in sorted_projects[:8]:
            inspiration.append({
                'title': project.get('title'),
                'author': project.get('author'),
                'fields': project.get('creative_fields'),
                'type': project.get('project_type'),
                'link': project.get('link'),
                'image': project.get('image_url'),
            })

        return inspiration

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['design', 'creative', 'portfolio', 'branding', 'illustration', 'art']
