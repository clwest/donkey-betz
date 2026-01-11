"""
Learning Pattern Engine
Session 744 Phase 3: Mine and inject learning patterns from agent history.

This service:
1. Queries AgentLearning records to find successful patterns
2. Identifies what task types each agent excels at
3. Extracts knowledge transfer insights
4. Formats patterns for prompt injection

The goal is to make agents aware of their past successes and learnings,
enabling them to apply proven strategies to new tasks.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import timedelta
from collections import defaultdict
from django.utils import timezone
from django.db.models import Count, Avg, F, Q

logger = logging.getLogger(__name__)


class LearningPatternEngine:
    """
    Session 744: Mines learning patterns from AgentLearning records.

    Usage:
        from core.services.learning_pattern_engine import get_learning_pattern_engine

        engine = get_learning_pattern_engine()
        patterns = engine.get_patterns_for_agent('ResearchAgent', task='analyze AI trends')
    """

    def __init__(self):
        self._agent_model = None
        self._learning_model = None
        self._execution_memory_model = None

    @property
    def Agent(self):
        """Lazy-load Agent model."""
        if self._agent_model is None:
            from core.models_unified_system import Agent
            self._agent_model = Agent
        return self._agent_model

    @property
    def AgentLearning(self):
        """Lazy-load AgentLearning model."""
        if self._learning_model is None:
            from core.models_unified_system import AgentLearning
            self._learning_model = AgentLearning
        return self._learning_model

    @property
    def AgentExecutionMemory(self):
        """Lazy-load AgentExecutionMemory model."""
        if self._execution_memory_model is None:
            from core.models_agent_memory import AgentExecutionMemory
            self._execution_memory_model = AgentExecutionMemory
        return self._execution_memory_model

    def get_patterns_for_agent(
        self,
        agent_name: str,
        task: str = '',
        days_back: int = 30,
        max_patterns: int = 5
    ) -> Dict[str, Any]:
        """
        Get learning patterns relevant to an agent and task.

        Args:
            agent_name: Name of the agent
            task: Current task description (for relevance matching)
            days_back: How far back to look for patterns
            max_patterns: Maximum number of patterns to return

        Returns:
            Dict with learned patterns, success rates, and recommendations
        """
        try:
            since = timezone.now() - timedelta(days=days_back)

            patterns = {
                'agent_name': agent_name,
                'learned_from_teaching': [],
                'learned_from_studying': [],
                'success_patterns': [],
                'collaboration_insights': [],
                'effectiveness_improvement': None,
                'best_practices': [],
                'summary': '',
                'has_patterns': False,
            }

            # Get agent record
            agent = self.Agent.objects.filter(name=agent_name).first()
            if not agent:
                logger.debug(f"Agent not found: {agent_name}")
                return patterns

            # 1. Get patterns from when this agent was a TEACHER
            teaching_records = self.AgentLearning.objects.filter(
                teacher_agent=agent,
                created_at__gte=since,
                implementation_success=True
            ).select_related('student_agent', 'solution')[:max_patterns * 2]

            if teaching_records.exists():
                taught_to = defaultdict(int)
                teaching_effectiveness = []

                for record in teaching_records:
                    taught_to[record.student_agent.name] += 1
                    improvement = record.effectiveness_after - record.effectiveness_before
                    if improvement > 0:
                        teaching_effectiveness.append({
                            'student': record.student_agent.name,
                            'improvement': round(improvement, 1),
                            'learning_type': record.learning_type,
                        })

                # Top students this agent has taught
                patterns['learned_from_teaching'] = [
                    f"Successfully taught {name} ({count} times)"
                    for name, count in sorted(taught_to.items(), key=lambda x: -x[1])[:3]
                ]

                if teaching_effectiveness:
                    avg_improvement = sum(t['improvement'] for t in teaching_effectiveness) / len(teaching_effectiveness)
                    patterns['effectiveness_improvement'] = {
                        'as_teacher': round(avg_improvement, 1),
                        'teaching_sessions': len(teaching_records),
                    }

            # 2. Get patterns from when this agent was a STUDENT
            learning_records = self.AgentLearning.objects.filter(
                student_agent=agent,
                created_at__gte=since,
                implementation_success=True
            ).select_related('teacher_agent', 'solution')[:max_patterns * 2]

            if learning_records.exists():
                learned_from = defaultdict(int)
                learning_improvements = []

                for record in learning_records:
                    learned_from[record.teacher_agent.name] += 1
                    improvement = record.effectiveness_after - record.effectiveness_before
                    if improvement > 0:
                        learning_improvements.append({
                            'teacher': record.teacher_agent.name,
                            'improvement': round(improvement, 1),
                            'learning_type': record.learning_type,
                        })

                # Best teachers for this agent
                patterns['learned_from_studying'] = [
                    f"Learned {record['learning_type']} from {record['teacher']} (+{record['improvement']}%)"
                    for record in sorted(learning_improvements, key=lambda x: -x['improvement'])[:3]
                ]

                if learning_improvements:
                    avg_improvement = sum(l['improvement'] for l in learning_improvements) / len(learning_improvements)
                    if patterns['effectiveness_improvement']:
                        patterns['effectiveness_improvement']['as_student'] = round(avg_improvement, 1)
                    else:
                        patterns['effectiveness_improvement'] = {'as_student': round(avg_improvement, 1)}

            # 3. Get success patterns from execution memory
            try:
                exec_memories = self.AgentExecutionMemory.objects.filter(
                    agent_name=agent_name,
                    success_score__gte=0.8  # High success executions
                ).order_by('-execution_date')[:max_patterns]

                for memory in exec_memories:
                    patterns['success_patterns'].append({
                        'task_type': memory.task_type,
                        'success_score': round(memory.success_score, 2),
                        'outcome': memory.outcome_description[:100] if memory.outcome_description else '',
                    })
            except Exception as e:
                logger.debug(f"Could not get execution memories: {e}")

            # 4. Find best collaboration partners
            collaboration_counts = defaultdict(lambda: {'count': 0, 'success': 0})

            # Count collaborations as teacher
            teacher_collabs = self.AgentLearning.objects.filter(
                teacher_agent=agent,
                created_at__gte=since
            ).values('student_agent__name').annotate(
                count=Count('id'),
                avg_success=Avg('effectiveness_after')
            )

            for collab in teacher_collabs:
                partner = collab['student_agent__name']
                collaboration_counts[partner]['count'] += collab['count']
                collaboration_counts[partner]['success'] = max(
                    collaboration_counts[partner]['success'],
                    collab['avg_success'] or 0
                )

            # Count collaborations as student
            student_collabs = self.AgentLearning.objects.filter(
                student_agent=agent,
                created_at__gte=since
            ).values('teacher_agent__name').annotate(
                count=Count('id'),
                avg_success=Avg('effectiveness_after')
            )

            for collab in student_collabs:
                partner = collab['teacher_agent__name']
                collaboration_counts[partner]['count'] += collab['count']
                collaboration_counts[partner]['success'] = max(
                    collaboration_counts[partner]['success'],
                    collab['avg_success'] or 0
                )

            # Top collaborators
            top_collaborators = sorted(
                collaboration_counts.items(),
                key=lambda x: (-x[1]['count'], -x[1]['success'])
            )[:3]

            patterns['collaboration_insights'] = [
                f"Works well with {partner} ({data['count']} sessions, {data['success']:.0f}% effectiveness)"
                for partner, data in top_collaborators
            ]

            # 5. Generate best practices from all data
            patterns['best_practices'] = self._generate_best_practices(
                agent_name,
                patterns,
                task
            )

            # 6. Build summary for prompt injection
            patterns['summary'] = self._build_pattern_summary(patterns)
            patterns['has_patterns'] = bool(
                patterns['learned_from_teaching'] or
                patterns['learned_from_studying'] or
                patterns['success_patterns'] or
                patterns['collaboration_insights']
            )

            if patterns['has_patterns']:
                logger.info(
                    f"📚 [Session 744] Learning patterns found for {agent_name}: "
                    f"{len(patterns['learned_from_teaching'])} teaching, "
                    f"{len(patterns['learned_from_studying'])} learning, "
                    f"{len(patterns['collaboration_insights'])} collaborations"
                )

            return patterns

        except Exception as e:
            logger.error(f"Failed to get learning patterns for {agent_name}: {e}")
            return {
                'agent_name': agent_name,
                'learned_from_teaching': [],
                'learned_from_studying': [],
                'success_patterns': [],
                'collaboration_insights': [],
                'effectiveness_improvement': None,
                'best_practices': [],
                'summary': '',
                'has_patterns': False,
                'error': str(e),
            }

    def _generate_best_practices(
        self,
        agent_name: str,
        patterns: Dict[str, Any],
        task: str
    ) -> List[str]:
        """Generate actionable best practices from patterns."""
        practices = []

        # Teaching-based practices
        if patterns.get('learned_from_teaching'):
            practices.append(
                "As an experienced teacher, provide clear explanations and actionable guidance"
            )

        # Learning-based practices
        if patterns.get('learned_from_studying'):
            # Extract the most effective learning types
            for pattern in patterns['learned_from_studying'][:1]:
                if 'spider_intelligence' in pattern:
                    practices.append(
                        "Leverage real-time spider data for current trends and insights"
                    )

        # Success pattern practices
        success_types = [p['task_type'] for p in patterns.get('success_patterns', [])]
        if success_types:
            unique_types = list(set(success_types))[:2]
            practices.append(
                f"This agent excels at {', '.join(unique_types)} tasks"
            )

        # Collaboration practices
        if patterns.get('collaboration_insights'):
            collaborators = [c.split('Works well with ')[1].split(' (')[0]
                          for c in patterns['collaboration_insights']
                          if 'Works well with' in c]
            if collaborators:
                practices.append(
                    f"Consider consulting with {collaborators[0]} for complex tasks"
                )

        # Effectiveness improvement insight
        improvement = patterns.get('effectiveness_improvement', {})
        if improvement:
            if improvement.get('as_teacher', 0) > 10:
                practices.append(
                    f"Teaching others has improved this agent's effectiveness by {improvement['as_teacher']}%"
                )
            if improvement.get('as_student', 0) > 10:
                practices.append(
                    f"Learning from others has improved effectiveness by {improvement['as_student']}%"
                )

        return practices[:5]

    def _build_pattern_summary(self, patterns: Dict[str, Any]) -> str:
        """Build a concise summary for prompt injection."""
        parts = []

        # Effectiveness
        improvement = patterns.get('effectiveness_improvement', {})
        if improvement:
            if improvement.get('as_teacher') and improvement.get('as_student'):
                parts.append(
                    f"Effectiveness: +{improvement['as_teacher']}% as teacher, "
                    f"+{improvement['as_student']}% as student"
                )
            elif improvement.get('as_teacher'):
                parts.append(f"Teaching effectiveness: +{improvement['as_teacher']}%")
            elif improvement.get('as_student'):
                parts.append(f"Learning effectiveness: +{improvement['as_student']}%")

        # Best collaborators
        if patterns.get('collaboration_insights'):
            # Extract just the names
            collaborators = []
            for insight in patterns['collaboration_insights'][:2]:
                if 'Works well with' in insight:
                    name = insight.split('Works well with ')[1].split(' (')[0]
                    collaborators.append(name)
            if collaborators:
                parts.append(f"Best collaborators: {', '.join(collaborators)}")

        # Success areas
        success_types = [p['task_type'] for p in patterns.get('success_patterns', [])]
        if success_types:
            unique_types = list(set(success_types))[:2]
            parts.append(f"Excels at: {', '.join(unique_types)}")

        return " | ".join(parts) if parts else ""

    def get_global_learning_stats(self) -> Dict[str, Any]:
        """Get overall learning system statistics."""
        try:
            total_learning = self.AgentLearning.objects.count()
            successful_learning = self.AgentLearning.objects.filter(
                implementation_success=True
            ).count()

            # Most effective teachers
            top_teachers = self.AgentLearning.objects.values(
                'teacher_agent__name'
            ).annotate(
                teaching_count=Count('id'),
                avg_improvement=Avg(F('effectiveness_after') - F('effectiveness_before'))
            ).order_by('-avg_improvement')[:5]

            # Most improved students
            top_students = self.AgentLearning.objects.values(
                'student_agent__name'
            ).annotate(
                learning_count=Count('id'),
                avg_improvement=Avg(F('effectiveness_after') - F('effectiveness_before'))
            ).order_by('-avg_improvement')[:5]

            # Learning types breakdown
            learning_types = self.AgentLearning.objects.values(
                'learning_type'
            ).annotate(count=Count('id')).order_by('-count')[:10]

            return {
                'total_learning_events': total_learning,
                'successful_events': successful_learning,
                'success_rate': round(successful_learning / total_learning * 100, 1) if total_learning > 0 else 0,
                'top_teachers': list(top_teachers),
                'top_students': list(top_students),
                'learning_types': list(learning_types),
            }

        except Exception as e:
            logger.error(f"Failed to get learning stats: {e}")
            return {'error': str(e)}


# Singleton instance
_learning_pattern_engine: Optional[LearningPatternEngine] = None


def get_learning_pattern_engine() -> LearningPatternEngine:
    """Get the singleton LearningPatternEngine instance."""
    global _learning_pattern_engine
    if _learning_pattern_engine is None:
        _learning_pattern_engine = LearningPatternEngine()
    return _learning_pattern_engine
