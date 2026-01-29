# Session 862: ContentClassifier - Route content to appropriate type
# Determines if content is public (blog), internal (build log), or strategic (dossier)

import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result from content classification."""
    content_type: str  # 'public', 'internal', 'strategic'
    suggested_category: str  # 'blog', 'build_log', 'playbook', 'dossier', etc.
    confidence: float  # 0-1
    signals_found: List[str]
    reasoning: str


class ContentClassifier:
    """
    Classifies content to determine appropriate routing.

    Content Types:
    - public: External audience, SEO, marketing, thought leadership
    - internal: System learning, team reference, operational knowledge
    - strategic: Operators, partners, investors, decision support

    Categories by Type:
    - public: blog, research_brief
    - internal: build_log, internal_note, playbook
    - strategic: dossier, audit, technical_document
    """

    # Classification rules
    CLASSIFICATION_RULES = {
        'internal': {
            'title_patterns': [
                'how we built', 'lessons learned', 'what we discovered',
                'system notes', 'internal:', 'build log:', 'team update',
                'retrospective', 'postmortem', 'debugging session',
            ],
            'content_patterns': [
                'we built this', 'our agents', 'our spiders', 'our system',
                'internally we', 'team reflection', 'action items for us',
                'next session:', 'todo for next', 'improvement areas:',
                'celery task', 'django model', 'migration file',
            ],
            'technical_density_threshold': 5,  # Number of technical terms
            'categories': ['build_log', 'internal_note', 'playbook'],
        },
        'strategic': {
            'title_patterns': [
                'audit:', 'analysis:', 'dossier:', 'report:',
                'market analysis', 'competitive analysis', 'risk assessment',
                'investment thesis', 'due diligence', 'strategy:',
            ],
            'content_patterns': [
                'recommend to stakeholders', 'executive summary',
                'key findings', 'risk factors', 'market opportunity',
                'investment consideration', 'strategic implications',
            ],
            'categories': ['dossier', 'audit', 'technical_document'],
        },
        'public': {
            'title_patterns': [
                'how to', 'guide to', 'introduction to', 'understanding',
                'why you should', 'the future of', 'trends in',
                'best practices for', 'tips for', 'secrets of',
            ],
            'content_patterns': [
                'in this article', 'you will learn', 'readers will',
                'we\'ll explore', 'let\'s dive into', 'you can apply',
                'your business', 'your team', 'industry trends',
            ],
            'categories': ['blog', 'research_brief'],
        },
    }

    TECHNICAL_TERMS = [
        'spider', 'agent', 'celery', 'django', 'redis', 'postgres',
        'api', 'endpoint', 'websocket', 'migration', 'model',
        'kalshi', 'polygon', 'openai', 'anthropic', 'llm',
        'embedding', 'vector', 'database', 'cache', 'queue',
        'task', 'worker', 'beat', 'cron', 'async', 'await',
    ]

    def classify(self, title: str, content: str, existing_category: str = None) -> ClassificationResult:
        """
        Classify content based on title and content.

        Args:
            title: Content title
            content: Full content text
            existing_category: Current category if any

        Returns:
            ClassificationResult with type, category, and reasoning
        """
        title_lower = title.lower() if title else ''
        content_lower = content.lower() if content else ''
        full_text = f"{title_lower} {content_lower}"

        signals = []
        scores = {'internal': 0, 'strategic': 0, 'public': 0}

        # Check each content type
        for content_type, rules in self.CLASSIFICATION_RULES.items():
            # Check title patterns
            for pattern in rules['title_patterns']:
                if pattern in title_lower:
                    scores[content_type] += 2
                    signals.append(f"title:'{pattern}'→{content_type}")

            # Check content patterns
            for pattern in rules['content_patterns']:
                if pattern in content_lower:
                    scores[content_type] += 1
                    signals.append(f"content:'{pattern}'→{content_type}")

        # Check technical density for internal classification
        technical_count = sum(1 for term in self.TECHNICAL_TERMS if term in full_text)
        if technical_count >= self.CLASSIFICATION_RULES['internal']['technical_density_threshold']:
            scores['internal'] += 3
            signals.append(f"technical_density:{technical_count}")

        # Consider existing category as hint
        if existing_category:
            for content_type, rules in self.CLASSIFICATION_RULES.items():
                if existing_category in rules['categories']:
                    scores[content_type] += 1
                    signals.append(f"existing_category:'{existing_category}'→{content_type}")

        # Determine winner
        total_score = sum(scores.values()) + 1  # Avoid division by zero
        max_score = max(scores.values())
        winner = max(scores, key=scores.get)
        confidence = max_score / total_score

        # If no clear winner, default to public
        if max_score < 2:
            winner = 'public'
            confidence = 0.3
            signals.append("no_strong_signals→default_public")

        # Suggest category
        suggested_category = self._suggest_category(winner, title_lower, content_lower)

        # Build reasoning
        reasoning = self._build_reasoning(winner, scores, signals, technical_count)

        return ClassificationResult(
            content_type=winner,
            suggested_category=suggested_category,
            confidence=confidence,
            signals_found=signals[:10],  # Limit to top 10
            reasoning=reasoning,
        )

    def _suggest_category(self, content_type: str, title: str, content: str) -> str:
        """Suggest specific category within content type."""

        if content_type == 'internal':
            if any(x in title for x in ['lesson', 'learned', 'retrospective']):
                return 'build_log'
            elif any(x in title for x in ['playbook', 'doctrine', 'process', 'practice']):
                return 'playbook'
            else:
                return 'internal_note'

        elif content_type == 'strategic':
            if any(x in title for x in ['audit', 'review', 'assessment']):
                return 'audit'
            elif any(x in title for x in ['analysis', 'dossier', 'report']):
                return 'dossier'
            else:
                return 'technical_document'

        else:  # public
            if any(x in title for x in ['research', 'study', 'findings']):
                return 'research_brief'
            else:
                return 'blog'

    def _build_reasoning(
        self,
        winner: str,
        scores: Dict[str, int],
        signals: List[str],
        technical_count: int
    ) -> str:
        """Build human-readable reasoning for classification."""

        parts = [f"Classified as '{winner}' content."]

        # Score summary
        parts.append(f"Scores: internal={scores['internal']}, strategic={scores['strategic']}, public={scores['public']}.")

        # Technical density
        if technical_count >= 5:
            parts.append(f"High technical density ({technical_count} terms) suggests internal/operational content.")
        elif technical_count >= 3:
            parts.append(f"Moderate technical density ({technical_count} terms).")

        # Key signals
        if signals:
            key_signals = [s for s in signals if '→' + winner in s][:3]
            if key_signals:
                parts.append(f"Key signals: {', '.join(key_signals)}.")

        return ' '.join(parts)

    def classify_blog(self, blog) -> ClassificationResult:
        """
        Classify a SelfBlog instance.

        Args:
            blog: SelfBlog model instance

        Returns:
            ClassificationResult
        """
        # Extract full content
        content_parts = [
            blog.meta_description or '',
            blog.intro or '',
        ]

        if blog.sections:
            for section in blog.sections:
                if isinstance(section, dict):
                    content_parts.append(section.get('header', ''))
                    content_parts.append(section.get('content', ''))

        content_parts.append(blog.conclusion or '')
        content_parts.append(blog.full_text or '')

        full_content = ' '.join(content_parts)

        return self.classify(
            title=blog.title,
            content=full_content,
            existing_category=blog.category,
        )

    def apply_to_blog(self, blog, save: bool = True) -> ClassificationResult:
        """
        Classify and optionally update blog.

        Args:
            blog: SelfBlog instance
            save: Whether to save changes

        Returns:
            ClassificationResult
        """
        result = self.classify_blog(blog)

        # Update blog fields
        blog.content_type = result.content_type

        # Update category if different and confidence is high
        if (result.suggested_category != blog.category and
            result.confidence > 0.6 and
            blog.category == 'blog'):  # Only auto-change from default 'blog'
            logger.info(f"Changing category from '{blog.category}' to '{result.suggested_category}'")
            blog.category = result.suggested_category

        if save:
            blog.save(update_fields=['content_type', 'category'])
            logger.info(f"Updated blog {blog.id}: type={result.content_type}, category={blog.category}")

        return result


# Convenience functions
def classify_content(title: str, content: str) -> ClassificationResult:
    """Quick classification of content."""
    classifier = ContentClassifier()
    return classifier.classify(title, content)


def classify_blog_by_id(blog_id: str, save: bool = True) -> ClassificationResult:
    """Classify a blog by ID."""
    from core.models_unified_system import SelfBlog

    blog = SelfBlog.objects.get(id=blog_id)
    classifier = ContentClassifier()
    return classifier.apply_to_blog(blog, save=save)


def classify_all_blogs(save: bool = False) -> List[Dict[str, Any]]:
    """
    Classify all blogs and return summary.

    Args:
        save: Whether to save classification results

    Returns:
        List of classification results with blog info
    """
    from core.models_unified_system import SelfBlog

    classifier = ContentClassifier()
    results = []

    for blog in SelfBlog.objects.all():
        result = classifier.classify_blog(blog)
        results.append({
            'id': str(blog.id),
            'title': blog.title[:60],
            'current_category': blog.category,
            'suggested_category': result.suggested_category,
            'content_type': result.content_type,
            'confidence': result.confidence,
            'reasoning': result.reasoning,
        })

        if save:
            classifier.apply_to_blog(blog, save=True)

    return results


def get_classification_stats() -> Dict[str, Any]:
    """Get statistics on content classification."""
    from core.models_unified_system import SelfBlog
    from django.db.models import Count

    return {
        'by_content_type': dict(
            SelfBlog.objects.values('content_type').annotate(
                count=Count('id')
            ).values_list('content_type', 'count')
        ),
        'by_category': dict(
            SelfBlog.objects.values('category').annotate(
                count=Count('id')
            ).values_list('category', 'count')
        ),
        'needs_reclassification': SelfBlog.objects.filter(
            category='blog',
            content_type='internal'
        ).count(),
    }
