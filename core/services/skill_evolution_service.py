"""
Session 930: Skill Evolution Service

Tracks how user skills evolve over time based on successful deliverables
and demonstrations. Infers skills from content and updates proficiency levels.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg, Count, F

logger = logging.getLogger(__name__)


# Skill inference patterns - maps keywords to skills
SKILL_PATTERNS = {
    # Technical skills
    'python': ('Python', 'technical'),
    'javascript': ('JavaScript', 'technical'),
    'typescript': ('TypeScript', 'technical'),
    'react': ('React', 'technical'),
    'django': ('Django', 'technical'),
    'sql': ('SQL', 'technical'),
    'aws': ('AWS', 'technical'),
    'docker': ('Docker', 'technical'),
    'kubernetes': ('Kubernetes', 'technical'),
    'api': ('API Development', 'technical'),
    'machine learning': ('Machine Learning', 'technical'),
    'data science': ('Data Science', 'technical'),

    # Creative skills
    'writing': ('Writing', 'creative'),
    'copywriting': ('Copywriting', 'creative'),
    'design': ('Design', 'creative'),
    'video': ('Video Production', 'creative'),
    'podcast': ('Podcasting', 'creative'),
    'content creation': ('Content Creation', 'creative'),
    'storytelling': ('Storytelling', 'creative'),

    # Analytical skills
    'analysis': ('Analysis', 'analytical'),
    'research': ('Research', 'analytical'),
    'data analysis': ('Data Analysis', 'analytical'),
    'market research': ('Market Research', 'analytical'),
    'financial analysis': ('Financial Analysis', 'analytical'),
    'trend analysis': ('Trend Analysis', 'analytical'),

    # Communication skills
    'presentation': ('Presentation', 'communication'),
    'negotiation': ('Negotiation', 'communication'),
    'public speaking': ('Public Speaking', 'communication'),
    'marketing': ('Marketing', 'communication'),
    'sales': ('Sales', 'communication'),

    # Leadership skills
    'management': ('Management', 'leadership'),
    'project management': ('Project Management', 'leadership'),
    'team leadership': ('Team Leadership', 'leadership'),
    'strategy': ('Strategy', 'leadership'),

    # Domain knowledge
    'finance': ('Finance', 'domain'),
    'investment': ('Investment', 'domain'),
    'blockchain': ('Blockchain', 'domain'),
    'cryptocurrency': ('Cryptocurrency', 'domain'),
    'legal': ('Legal', 'domain'),
    'healthcare': ('Healthcare', 'domain'),
    'sports betting': ('Sports Betting', 'domain'),
}


@dataclass
class SkillGrowth:
    """Represents skill growth over time"""
    skill_name: str
    category: str
    current_level: int
    previous_level: int
    growth_rate: float  # Levels per month
    demonstrations_this_month: int
    trend: str  # 'growing', 'stable', 'declining'


class SkillEvolutionService:
    """
    Session 930: Track and evolve user skills based on deliverables.

    Infers skills from content, tracks proficiency levels,
    and provides growth visualizations.
    """

    def __init__(self):
        self._cache = {}

    def infer_skills_from_deliverable(
        self,
        deliverable,
        min_confidence: float = 0.5,
    ) -> List[tuple]:
        """
        Extract skills demonstrated in a deliverable.

        Analyzes deliverable content to identify skills.

        Args:
            deliverable: Deliverable to analyze
            min_confidence: Minimum confidence threshold

        Returns:
            List of (skill_name, category, confidence) tuples
        """
        # Build text corpus from deliverable
        text_parts = [
            getattr(deliverable, 'title', ''),
            getattr(deliverable, 'description', ''),
            getattr(deliverable, 'content', ''),
        ]

        # Include tags if available
        tags = getattr(deliverable, 'tags', None)
        if tags:
            if isinstance(tags, list):
                text_parts.extend(tags)
            elif isinstance(tags, str):
                text_parts.append(tags)

        text = ' '.join(str(p) for p in text_parts).lower()

        # Find matching skills
        found_skills = []
        for pattern, (skill_name, category) in SKILL_PATTERNS.items():
            # Check for pattern match
            if pattern in text:
                # Calculate confidence based on frequency
                count = text.count(pattern)
                confidence = min(1.0, 0.5 + (count * 0.1))

                if confidence >= min_confidence:
                    found_skills.append((skill_name, category, confidence))

        # Also check deliverable type for hints
        deliverable_type = getattr(deliverable, 'deliverable_type', '')
        if deliverable_type:
            type_lower = deliverable_type.lower()
            if 'code' in type_lower or 'technical' in type_lower:
                found_skills.append(('Programming', 'technical', 0.7))
            elif 'article' in type_lower or 'blog' in type_lower:
                found_skills.append(('Writing', 'creative', 0.8))
            elif 'report' in type_lower or 'analysis' in type_lower:
                found_skills.append(('Analysis', 'analytical', 0.7))

        # Dedupe by skill name, keeping highest confidence
        skill_map = {}
        for skill_name, category, confidence in found_skills:
            if skill_name not in skill_map or confidence > skill_map[skill_name][1]:
                skill_map[skill_name] = (category, confidence)

        return [
            (name, cat, conf)
            for name, (cat, conf) in skill_map.items()
        ]

    def record_skill_demonstration(
        self,
        user,
        skill_name: str,
        category: str,
        quality_score: float,
        deliverable=None,
        context: str = '',
        inference_source: str = 'deliverable',
    ) -> 'SkillDemonstration':
        """
        Record a skill demonstration and update proficiency.

        Args:
            user: User demonstrating skill
            skill_name: Name of skill
            category: Skill category
            quality_score: Quality of demonstration (0-1)
            deliverable: Optional linked deliverable
            context: How skill was demonstrated
            inference_source: How skill was inferred

        Returns:
            Created SkillDemonstration instance
        """
        from core.models_user_learning import UserSkill, SkillDemonstration

        # Get or create skill record
        skill, created = UserSkill.objects.get_or_create(
            user=user,
            skill_name=skill_name,
            defaults={
                'category': category,
                'proficiency_level': 1,
                'evidence_count': 0,
                'confidence': 0.5,
            }
        )

        # Create demonstration record
        demonstration = SkillDemonstration.objects.create(
            skill=skill,
            deliverable=deliverable,
            quality_score=quality_score,
            context=context,
            inference_source=inference_source,
        )

        logger.info(
            f"Recorded skill demonstration: user={user.username}, "
            f"skill={skill_name}, quality={quality_score:.2f}"
        )

        return demonstration

    def update_skills_from_deliverable(
        self,
        user,
        deliverable,
        base_quality: float = 0.7,
    ) -> List['SkillDemonstration']:
        """
        Analyze deliverable and update user skills based on content.

        Convenience method that combines inference and recording.

        Args:
            user: User who created deliverable
            deliverable: Deliverable to analyze
            base_quality: Base quality score to use

        Returns:
            List of created SkillDemonstration instances
        """
        # Infer skills from deliverable
        skills = self.infer_skills_from_deliverable(deliverable)

        demonstrations = []
        for skill_name, category, confidence in skills:
            # Adjust quality by confidence
            quality = base_quality * confidence

            demo = self.record_skill_demonstration(
                user=user,
                skill_name=skill_name,
                category=category,
                quality_score=quality,
                deliverable=deliverable,
                context=f"Demonstrated in: {getattr(deliverable, 'title', 'deliverable')}",
                inference_source='deliverable',
            )
            demonstrations.append(demo)

        return demonstrations

    def get_user_skills(self, user) -> List[Dict]:
        """
        Get all skills for a user with proficiency levels.

        Returns list of skill dictionaries ordered by proficiency.
        """
        from core.models_user_learning import UserSkill

        skills = UserSkill.objects.filter(user=user).order_by(
            '-proficiency_level', '-evidence_count'
        )

        return [
            {
                'id': str(skill.id),
                'name': skill.skill_name,
                'category': skill.category,
                'level': skill.proficiency_level,
                'evidence_count': skill.evidence_count,
                'confidence': round(skill.confidence, 2),
                'first_demonstrated': skill.first_demonstrated.isoformat(),
                'last_demonstrated': skill.last_demonstrated.isoformat(),
            }
            for skill in skills
        ]

    def get_skill_growth_chart(self, user, months: int = 6) -> Dict[str, Any]:
        """
        Get skill levels over time for visualization.

        Returns data structure suitable for charting.
        """
        from core.models_user_learning import UserSkill, SkillDemonstration

        now = timezone.now()
        cutoff = now - timedelta(days=months * 30)

        # Get all demonstrations in timeframe
        demos = SkillDemonstration.objects.filter(
            skill__user=user,
            created_at__gte=cutoff,
        ).select_related('skill').order_by('created_at')

        # Build timeline data
        timeline = {}  # skill_name -> [(date, level), ...]
        skill_levels = {}  # track running levels

        for demo in demos:
            skill_name = demo.skill.skill_name
            date_key = demo.created_at.strftime('%Y-%m-%d')

            if skill_name not in timeline:
                timeline[skill_name] = []
                skill_levels[skill_name] = 1

            # Simulate level progression
            if demo.quality_score >= 0.7:
                skill_levels[skill_name] = min(10, skill_levels[skill_name] + 0.2)

            timeline[skill_name].append({
                'date': date_key,
                'level': round(skill_levels[skill_name], 1),
                'quality': round(demo.quality_score, 2),
            })

        # Calculate growth rates
        growth_data = []
        for skill_name, points in timeline.items():
            if len(points) >= 2:
                start_level = points[0]['level']
                end_level = points[-1]['level']
                growth_rate = (end_level - start_level) / months if months > 0 else 0

                growth_data.append({
                    'skill': skill_name,
                    'start_level': start_level,
                    'current_level': end_level,
                    'growth_rate': round(growth_rate, 2),
                    'demonstrations': len(points),
                    'trend': 'growing' if growth_rate > 0.1 else (
                        'declining' if growth_rate < -0.1 else 'stable'
                    ),
                })

        return {
            'timeline': timeline,
            'growth_summary': growth_data,
            'total_skills': len(timeline),
            'period_months': months,
        }

    def get_skill_recommendations(self, user) -> List[Dict]:
        """
        Get skill improvement recommendations based on gaps.

        Analyzes user's goal and compares to current skills.
        """
        from core.models_user_learning import UserSkill

        current_skills = {
            s.skill_name.lower(): s.proficiency_level
            for s in UserSkill.objects.filter(user=user)
        }

        recommendations = []

        # Check user profile for goals
        profile = getattr(user, 'enhanced_profile', None)
        if profile:
            goals = getattr(profile, 'long_term_goals', []) or []

            for goal in goals[:5]:  # Check top 5 goals
                goal_lower = goal.lower() if isinstance(goal, str) else ''

                # Find skills related to goal
                for pattern, (skill_name, category) in SKILL_PATTERNS.items():
                    if pattern in goal_lower:
                        current_level = current_skills.get(skill_name.lower(), 0)
                        if current_level < 5:  # Recommend if below intermediate
                            recommendations.append({
                                'skill': skill_name,
                                'category': category,
                                'current_level': current_level,
                                'reason': f"Related to your goal: {goal[:50]}",
                                'priority': 'high' if current_level == 0 else 'medium',
                            })

        # Dedupe recommendations
        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec['skill'] not in seen:
                seen.add(rec['skill'])
                unique_recs.append(rec)

        return unique_recs[:10]  # Top 10 recommendations

    def get_skills_summary(self, user) -> Dict[str, Any]:
        """
        Get comprehensive skills summary for dashboard.
        """
        from core.models_user_learning import UserSkill, SkillDemonstration

        skills = UserSkill.objects.filter(user=user)

        # Count by category
        by_category = {}
        for skill in skills:
            if skill.category not in by_category:
                by_category[skill.category] = {
                    'count': 0,
                    'avg_level': 0,
                    'skills': [],
                }
            by_category[skill.category]['count'] += 1
            by_category[skill.category]['skills'].append({
                'name': skill.skill_name,
                'level': skill.proficiency_level,
            })

        # Calculate averages
        for cat_data in by_category.values():
            if cat_data['skills']:
                cat_data['avg_level'] = round(
                    sum(s['level'] for s in cat_data['skills']) / len(cat_data['skills']),
                    1
                )

        # Top skills
        top_skills = list(skills.order_by('-proficiency_level')[:5].values(
            'skill_name', 'proficiency_level', 'category'
        ))

        # Recent activity
        recent_demos = SkillDemonstration.objects.filter(
            skill__user=user
        ).order_by('-created_at')[:10]

        recent_activity = [
            {
                'skill': d.skill.skill_name,
                'quality': round(d.quality_score, 2),
                'date': d.created_at.isoformat(),
            }
            for d in recent_demos
        ]

        return {
            'total_skills': skills.count(),
            'total_demonstrations': SkillDemonstration.objects.filter(
                skill__user=user
            ).count(),
            'average_proficiency': round(
                skills.aggregate(avg=Avg('proficiency_level'))['avg'] or 0, 1
            ),
            'by_category': by_category,
            'top_skills': top_skills,
            'recent_activity': recent_activity,
            'recommendations': self.get_skill_recommendations(user),
        }


# Singleton instance
_skill_evolution_service = None


def get_skill_evolution_service() -> SkillEvolutionService:
    """Get singleton instance of SkillEvolutionService."""
    global _skill_evolution_service
    if _skill_evolution_service is None:
        _skill_evolution_service = SkillEvolutionService()
    return _skill_evolution_service
