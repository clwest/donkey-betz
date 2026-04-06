"""
Learning Pattern Engine
Session 744 Phase 3: Mine and inject learning patterns from agent history.
Session 766: Enhanced to query LearningPattern model and track pattern application.

This service:
1. Queries AgentLearning records to find successful patterns
2. Queries LearningPattern model for stored patterns (NEW - Session 766)
3. Identifies what task types each agent excels at
4. Extracts knowledge transfer insights
5. Formats patterns for prompt injection
6. Tracks pattern application (NEW - Session 766)

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
        self._learning_pattern_model = None  # Session 766

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

    @property
    def LearningPattern(self):
        """Session 766: Lazy-load LearningPattern model."""
        if self._learning_pattern_model is None:
            from core.models_unified_system import LearningPattern
            self._learning_pattern_model = LearningPattern
        return self._learning_pattern_model

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
                'stored_patterns': [],  # Session 766: From LearningPattern model
                'applied_pattern_ids': [],  # Session 766: IDs of patterns we're applying
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

            # 3.5 Session 766: Get patterns from LearningPattern model
            try:
                # Query patterns that apply to this agent or are global
                stored_patterns = self.LearningPattern.objects.filter(
                    is_active=True,
                    confidence__gte=0.3  # Only patterns with reasonable confidence
                ).filter(
                    Q(applies_to_agents__contains=[agent_name]) |
                    Q(applies_to_agents__len=0)  # Global patterns with no specific agents
                ).order_by('-confidence')[:max_patterns]

                for pattern in stored_patterns:
                    patterns['stored_patterns'].append({
                        'id': str(pattern.id),
                        'type': pattern.pattern_type,
                        'description': pattern.description,
                        'confidence': round(pattern.confidence, 2),
                        'data': pattern.pattern_data,
                        'times_applied': pattern.times_applied,
                        'effectiveness': pattern.effectiveness_rate(),
                    })
                    patterns['applied_pattern_ids'].append(str(pattern.id))

                if patterns['stored_patterns']:
                    logger.info(
                        f"📦 [Session 766] Found {len(patterns['stored_patterns'])} stored patterns for {agent_name}"
                    )
            except Exception as e:
                logger.debug(f"Could not get stored learning patterns: {e}")

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
                patterns['collaboration_insights'] or
                patterns['stored_patterns']  # Session 766: Include stored patterns
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

        # Session 766: Stored patterns from LearningPattern model
        # Type-aware rendering extracts actionable data from pattern_data
        stored = patterns.get('stored_patterns', [])
        if stored:
            rendered_types = set()
            generic_types = []

            for p in stored[:8]:
                ptype = p['type']
                if ptype in rendered_types:
                    continue
                pdata = p.get('data', {})

                if ptype == 'agent_success_rate':
                    rate = pdata.get('success_rate')
                    total = pdata.get('total_executions', 0)
                    if rate is not None and total:
                        parts.append(f"Success rate: {rate}% ({total} runs)")
                        rendered_types.add(ptype)
                    continue

                if ptype == 'content_quality':
                    avg_q = pdata.get('avg_quality')
                    saved = pdata.get('saved_pct', 0)
                    if avg_q is not None:
                        parts.append(f"Content quality: {avg_q:.2f}" + (f", {saved}% saved" if saved else ""))
                        rendered_types.add(ptype)
                    continue

                if ptype == 'tool_reliability':
                    tool = pdata.get('tool_name', '')
                    rate = pdata.get('success_rate')
                    if tool and rate is not None:
                        parts.append(f"Tool '{tool}': {rate}% reliable")
                        rendered_types.add(ptype)
                    continue

                if ptype == 'prediction_accuracy':
                    sport = pdata.get('sport_type', '')
                    acc = pdata.get('accuracy_pct')
                    if sport and acc is not None:
                        parts.append(f"{sport} predictions: {acc}% accurate")
                        rendered_types.add(ptype)
                    continue

                if ptype == 'agent_tool_effectiveness':
                    tool = pdata.get('tool_name', '')
                    rate = pdata.get('success_rate')
                    if tool and rate is not None:
                        parts.append(f"Best tool: {tool} ({rate}%)")
                        rendered_types.add(ptype)
                    continue

                if ptype == 'collaboration_effectiveness':
                    delta = pdata.get('quality_delta')
                    if delta is not None and delta > 0:
                        parts.append(f"Collab boost: +{delta:.0%} in group sessions")
                        rendered_types.add(ptype)
                    continue

                if ptype == 'spider_data_value':
                    dt = pdata.get('data_type', '')
                    act = pdata.get('actionable_pct', 0)
                    if dt and act > 0:
                        parts.append(f"Spider '{dt}': {act}% actionable")
                        rendered_types.add(ptype)
                    continue

                generic_types.append(ptype)

            # Fall back to generic rendering for unrecognized types
            if generic_types:
                unique = list(dict.fromkeys(generic_types))[:3]
                parts.append(f"Known patterns: {', '.join(unique)}")

        return " | ".join(parts) if parts else ""

    def track_pattern_application(
        self,
        pattern_ids: List[str],
        was_successful: bool = True
    ) -> Dict[str, Any]:
        """
        Session 766: Track when patterns are applied to agent execution.

        This should be called after an agent execution completes to update
        the times_applied and success metrics on the LearningPattern records.

        Args:
            pattern_ids: List of pattern IDs that were applied (from applied_pattern_ids)
            was_successful: Whether the execution was successful

        Returns:
            Dict with tracking results
        """
        if not pattern_ids:
            return {'tracked': 0, 'patterns': []}

        tracked = []
        try:
            from django.db.models import F

            for pattern_id in pattern_ids:
                try:
                    pattern = self.LearningPattern.objects.get(id=pattern_id)

                    # Increment times_applied
                    pattern.times_applied = F('times_applied') + 1
                    if was_successful:
                        pattern.success_when_applied = F('success_when_applied') + 1
                    pattern.save(update_fields=['times_applied', 'success_when_applied'])

                    # Refresh to get actual values
                    pattern.refresh_from_db()

                    tracked.append({
                        'id': str(pattern.id),
                        'type': pattern.pattern_type,
                        'times_applied': pattern.times_applied,
                        'success_when_applied': pattern.success_when_applied,
                    })

                    logger.info(
                        f"📊 [Session 766] Pattern {pattern.pattern_type} applied "
                        f"(total: {pattern.times_applied}, success: {pattern.success_when_applied})"
                    )
                except Exception as e:
                    logger.warning(f"Could not track pattern {pattern_id}: {e}")

            return {
                'tracked': len(tracked),
                'patterns': tracked,
                'was_successful': was_successful,
            }

        except Exception as e:
            logger.error(f"Failed to track pattern application: {e}")
            return {'tracked': 0, 'error': str(e)}

    def decay_stale_patterns(self, inactive_days: int = 30, decay_factor: float = 0.9) -> Dict[str, Any]:
        """
        Session 1085: Reduce confidence of patterns that haven't been applied recently.

        Patterns that sit unused for 30+ days lose 10% confidence per cycle.
        Patterns with <20% effectiveness lose 20% confidence.
        Patterns with confidence < 0.1 are archived (deleted).

        Args:
            inactive_days: Days without application before decay starts
            decay_factor: Multiply confidence by this (0.9 = 10% reduction)

        Returns:
            Dict with decay stats
        """
        from django.utils import timezone
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(days=inactive_days)
        decayed = 0
        archived = 0

        try:
            # Decay stale patterns (not applied recently)
            stale = self.LearningPattern.objects.filter(
                updated_at__lt=cutoff,
                confidence__gt=0.1,
            )
            for pattern in stale:
                # Extra penalty for ineffective patterns
                if pattern.times_applied > 5:
                    effectiveness = pattern.success_when_applied / pattern.times_applied
                    if effectiveness < 0.2:
                        pattern.confidence *= (decay_factor * 0.8)  # 28% reduction
                    else:
                        pattern.confidence *= decay_factor
                else:
                    pattern.confidence *= decay_factor

                pattern.save(update_fields=['confidence', 'updated_at'])
                decayed += 1

            # Archive patterns with very low confidence
            archived = self.LearningPattern.objects.filter(confidence__lt=0.1).delete()[0]

            logger.info(
                f"📉 [Session 1085] Pattern decay: {decayed} decayed, {archived} archived "
                f"(inactive_days={inactive_days}, decay_factor={decay_factor})"
            )

            return {'decayed': decayed, 'archived': archived}

        except Exception as e:
            logger.error(f"Pattern decay failed: {e}")
            return {'decayed': 0, 'archived': 0, 'error': str(e)}

    def mine_patterns(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Mine real performance data to create LearningPattern entries.

        Queries actual outcome tables (AgentExecution, Deliverable,
        ToolCallRecord, MLPrediction) instead of synthetic AgentLearning
        records. Replaces the Session 767 synthetic miners.

        Should be run periodically via Celery task (every 12h).

        Args:
            days_back: How many days of data to analyze

        Returns:
            Dict with mining results (patterns_created, patterns_updated)
        """
        from django.db.models import Count, Avg, F, Q, Case, When, FloatField, Value
        from django.utils import timezone

        since = timezone.now() - timedelta(days=days_back)
        patterns_created = 0
        patterns_updated = 0

        logger.info(f"Mining learning patterns from real data (last {days_back} days)...")

        try:
            # One-time cleanup: deactivate old synthetic patterns
            old_types = ['spider_effectiveness', 'agent_collaboration', 'learning_type_impact', 'top_teacher']
            cleaned = self.LearningPattern.objects.filter(
                pattern_type__in=old_types, is_active=True
            ).update(is_active=False)
            if cleaned > 0:
                logger.info(f"  Deactivated {cleaned} old synthetic patterns")

            # === Miner A: Agent Success Rate (from AgentExecution) ===
            from core.models_unified_system import AgentExecution

            agent_stats = AgentExecution.objects.filter(
                created_at__gte=since,
                status__in=['completed', 'failed'],
            ).values('agent__name').annotate(
                total=Count('id'),
                completed=Count('id', filter=Q(status='completed')),
                failed=Count('id', filter=Q(status='failed')),
                avg_ms=Avg('execution_time_ms'),
                avg_cost=Avg('cost'),
            ).filter(total__gte=5).order_by('-total')[:50]

            for row in agent_stats:
                agent_name = row['agent__name']
                success_rate = round(row['completed'] / row['total'] * 100, 1)
                avg_ms = round(row['avg_ms'] or 0)
                avg_cost = float(row['avg_cost'] or 0)
                confidence = min(0.95, 0.4 + (row['total'] / 200))

                pattern, created = self.LearningPattern.objects.update_or_create(
                    pattern_type='agent_success_rate',
                    applies_to_agents__contains=[agent_name],
                    defaults={
                        'description': (
                            f"{agent_name} has {success_rate}% success rate "
                            f"({row['total']} executions, avg {avg_ms}ms)"
                        ),
                        'confidence': round(confidence, 3),
                        'pattern_data': {
                            'agent_name': agent_name,
                            'success_rate': success_rate,
                            'total_executions': row['total'],
                            'completed': row['completed'],
                            'failed': row['failed'],
                            'avg_execution_ms': avg_ms,
                            'avg_cost': round(avg_cost, 4),
                            'days_analyzed': days_back,
                            'mined_at': timezone.now().isoformat(),
                        },
                        'applies_to_agents': [agent_name],
                        'is_active': True,
                    }
                )
                if created:
                    patterns_created += 1
                else:
                    patterns_updated += 1

            logger.info(f"  Miner A (agent_success_rate): {patterns_created} created, {patterns_updated} updated")
            a_total = patterns_created + patterns_updated

            # === Miner B: Content Quality (from Deliverable) ===
            from core.models_deliverables import Deliverable

            quality_stats = Deliverable.objects.filter(
                created_at__gte=since,
            ).values('agent_name').annotate(
                total=Count('id'),
                avg_quality=Avg('quality_score'),
                saved=Count('id', filter=Q(is_saved=True)),
                starred=Count('id', filter=Q(is_starred=True)),
            ).filter(total__gte=3).order_by('-total')[:50]

            for row in quality_stats:
                agent_name = row['agent_name']
                avg_q = round(row['avg_quality'] or 0, 3)
                saved_pct = round(row['saved'] / row['total'] * 100, 1) if row['total'] else 0
                starred_pct = round(row['starred'] / row['total'] * 100, 1) if row['total'] else 0

                # Get per-type breakdown
                by_type = list(
                    Deliverable.objects.filter(
                        created_at__gte=since,
                        agent_name=agent_name,
                    ).values('deliverable_type').annotate(
                        count=Count('id'),
                        avg_quality=Avg('quality_score'),
                    ).order_by('-count')[:5]
                )
                for bt in by_type:
                    bt['avg_quality'] = round(bt['avg_quality'] or 0, 3)

                confidence = min(0.9, 0.3 + (row['total'] / 100))

                pattern, created = self.LearningPattern.objects.update_or_create(
                    pattern_type='content_quality',
                    applies_to_agents__contains=[agent_name],
                    defaults={
                        'description': (
                            f"{agent_name} produces content with avg quality {avg_q} "
                            f"({row['total']} deliverables, {saved_pct}% saved)"
                        ),
                        'confidence': round(confidence, 3),
                        'pattern_data': {
                            'agent_name': agent_name,
                            'avg_quality': avg_q,
                            'total_deliverables': row['total'],
                            'by_type': by_type,
                            'saved_pct': saved_pct,
                            'starred_pct': starred_pct,
                            'days_analyzed': days_back,
                            'mined_at': timezone.now().isoformat(),
                        },
                        'applies_to_agents': [agent_name],
                        'is_active': True,
                    }
                )
                if created:
                    patterns_created += 1
                else:
                    patterns_updated += 1

            b_total = (patterns_created + patterns_updated) - a_total
            logger.info(f"  Miner B (content_quality): {b_total} patterns")

            # === Miner C: Tool Reliability (from ToolCallRecord) ===
            from core.models_tool_calls import ToolCallRecord

            tool_stats = ToolCallRecord.objects.filter(
                created_at__gte=since,
            ).values('tool_name').annotate(
                total=Count('id'),
                successes=Count('id', filter=Q(success=True)),
                avg_latency=Avg('latency_ms'),
            ).filter(total__gte=10).order_by('-total')[:50]

            for row in tool_stats:
                tool_name = row['tool_name']
                success_rate = round(row['successes'] / row['total'] * 100, 1)
                avg_latency = round(row['avg_latency'] or 0)

                # Find top agents using this tool
                top_agents = list(
                    ToolCallRecord.objects.filter(
                        created_at__gte=since,
                        tool_name=tool_name,
                    ).values('agent_name').annotate(
                        count=Count('id'),
                    ).order_by('-count')[:5].values_list('agent_name', flat=True)
                )

                confidence = min(0.95, 0.5 + (row['total'] / 500))

                pattern, created = self.LearningPattern.objects.update_or_create(
                    pattern_type='tool_reliability',
                    pattern_data__tool_name=tool_name,
                    defaults={
                        'description': (
                            f"Tool '{tool_name}' has {success_rate}% success rate "
                            f"({row['total']} calls, avg {avg_latency}ms)"
                        ),
                        'confidence': round(confidence, 3),
                        'pattern_data': {
                            'tool_name': tool_name,
                            'success_rate': success_rate,
                            'avg_latency_ms': avg_latency,
                            'total_calls': row['total'],
                            'top_agents': top_agents,
                            'days_analyzed': days_back,
                            'mined_at': timezone.now().isoformat(),
                        },
                        'applies_to_agents': [],  # Global pattern
                        'is_active': True,
                    }
                )
                if created:
                    patterns_created += 1
                else:
                    patterns_updated += 1

            c_total = (patterns_created + patterns_updated) - a_total - b_total
            logger.info(f"  Miner C (tool_reliability): {c_total} patterns")

            # === Miner D: Prediction Accuracy (from MLPrediction) ===
            try:
                from sports.models import MLPrediction

                pred_stats = MLPrediction.objects.filter(
                    was_correct__isnull=False,
                    evaluated_at__gte=since,
                ).values('sport_type').annotate(
                    total=Count('id'),
                    correct=Count('id', filter=Q(was_correct=True)),
                    avg_confidence=Avg('confidence'),
                ).filter(total__gte=5).order_by('-total')

                for row in pred_stats:
                    sport = row['sport_type']
                    accuracy = round(row['correct'] / row['total'] * 100, 1)
                    avg_conf = round(row['avg_confidence'] or 0, 1)
                    confidence = min(0.9, 0.4 + (row['total'] / 200))

                    pattern, created = self.LearningPattern.objects.update_or_create(
                        pattern_type='prediction_accuracy',
                        pattern_data__sport_type=sport,
                        defaults={
                            'description': (
                                f"Predictions for {sport} are {accuracy}% accurate "
                                f"({row['total']} evaluated, avg confidence {avg_conf}%)"
                            ),
                            'confidence': round(confidence, 3),
                            'pattern_data': {
                                'sport_type': sport,
                                'accuracy_pct': accuracy,
                                'total_evaluated': row['total'],
                                'correct': row['correct'],
                                'avg_confidence': avg_conf,
                                'days_analyzed': days_back,
                                'mined_at': timezone.now().isoformat(),
                            },
                            'applies_to_agents': ['GamePredictor'],
                            'is_active': True,
                        }
                    )
                    if created:
                        patterns_created += 1
                    else:
                        patterns_updated += 1
            except Exception as e:
                logger.warning(f"  Miner D (prediction_accuracy) skipped: {e}")

            d_total = (patterns_created + patterns_updated) - a_total - b_total - c_total
            logger.info(f"  Miner D (prediction_accuracy): {d_total} patterns")

            # === Miner E: Agent-Tool Effectiveness (from ToolCallRecord) ===
            agent_tool_stats = ToolCallRecord.objects.filter(
                created_at__gte=since,
            ).values('agent_name', 'tool_name').annotate(
                total=Count('id'),
                successes=Count('id', filter=Q(success=True)),
                avg_latency=Avg('latency_ms'),
            ).filter(total__gte=5).order_by('-total')[:100]

            for row in agent_tool_stats:
                agent_name = row['agent_name']
                tool_name = row['tool_name']
                success_rate = round(row['successes'] / row['total'] * 100, 1)
                avg_latency = round(row['avg_latency'] or 0)
                confidence = min(0.9, 0.3 + (row['total'] / 100))

                pattern, created = self.LearningPattern.objects.update_or_create(
                    pattern_type='agent_tool_effectiveness',
                    pattern_data__agent_name=agent_name,
                    pattern_data__tool_name=tool_name,
                    defaults={
                        'description': (
                            f"{agent_name} uses {tool_name} effectively "
                            f"({success_rate}% success, {avg_latency}ms avg)"
                        ),
                        'confidence': round(confidence, 3),
                        'pattern_data': {
                            'agent_name': agent_name,
                            'tool_name': tool_name,
                            'success_rate': success_rate,
                            'avg_latency_ms': avg_latency,
                            'call_count': row['total'],
                            'days_analyzed': days_back,
                            'mined_at': timezone.now().isoformat(),
                        },
                        'applies_to_agents': [agent_name],
                        'is_active': True,
                    }
                )
                if created:
                    patterns_created += 1
                else:
                    patterns_updated += 1

            e_total = (patterns_created + patterns_updated) - a_total - b_total - c_total - d_total
            logger.info(f"  Miner E (agent_tool_effectiveness): {e_total} patterns")

            # === Miner F: Collaboration Effectiveness ===
            # Which agents perform better in multi-agent conversations?
            # Source: AgentConversation (14k+ records, M2M participants, quality_score)
            f_total = patterns_created + patterns_updated
            try:
                from core.models_unified_system import AgentConversation

                # Concluded conversations with 3+ participants (true collaboration)
                collab_ids = list(
                    AgentConversation.objects.filter(
                        status='concluded',
                        started_at__gte=since,
                    )
                    .annotate(n_parts=Count('participants'))
                    .filter(n_parts__gte=3)
                    .values_list('id', flat=True)
                )

                # Pair conversations (exactly 2 participants) as baseline
                pair_ids = list(
                    AgentConversation.objects.filter(
                        status='concluded',
                        started_at__gte=since,
                    )
                    .annotate(n_parts=Count('participants'))
                    .filter(n_parts=2)
                    .values_list('id', flat=True)
                )

                if collab_ids:
                    # Per-agent avg quality in 3+ participant conversations
                    collab_stats = (
                        AgentConversation.objects.filter(id__in=collab_ids)
                        .values('participants__name')
                        .annotate(
                            avg_quality=Avg('quality_score'),
                            count=Count('id'),
                        )
                        .filter(count__gte=3)
                    )

                    # Per-agent avg quality in pair conversations (baseline)
                    pair_avg_map = {}
                    if pair_ids:
                        pair_stats = (
                            AgentConversation.objects.filter(id__in=pair_ids)
                            .values('participants__name')
                            .annotate(avg_quality=Avg('quality_score'))
                        )
                        pair_avg_map = {r['participants__name']: r['avg_quality'] for r in pair_stats}

                    for row in collab_stats:
                        agent_name = row['participants__name']
                        avg_quality = round(row['avg_quality'], 3)
                        pair_avg = pair_avg_map.get(agent_name)
                        delta = round(avg_quality - pair_avg, 3) if pair_avg is not None else None
                        confidence = min(0.85, 0.3 + (row['count'] / 50))

                        delta_str = f", {delta:+.3f} vs pairs" if delta is not None else ""
                        pattern, created = self.LearningPattern.objects.update_or_create(
                            pattern_type='collaboration_effectiveness',
                            pattern_data__agent_name=agent_name,
                            defaults={
                                'description': (
                                    f"{agent_name} averages {avg_quality:.2f} quality in "
                                    f"multi-agent conversations ({row['count']} sessions"
                                    f"{delta_str})"
                                ),
                                'confidence': round(confidence, 3),
                                'pattern_data': {
                                    'agent_name': agent_name,
                                    'avg_quality': avg_quality,
                                    'collab_count': row['count'],
                                    'pair_avg_quality': round(pair_avg, 3) if pair_avg is not None else None,
                                    'quality_delta': delta,
                                    'days_analyzed': days_back,
                                    'mined_at': timezone.now().isoformat(),
                                },
                                'applies_to_agents': [agent_name],
                                'is_active': True,
                            }
                        )
                        if created:
                            patterns_created += 1
                        else:
                            patterns_updated += 1

            except Exception as e:
                logger.warning(f"  Miner F (collaboration_effectiveness) failed: {e}")

            f_total = (patterns_created + patterns_updated) - f_total
            logger.info(f"  Miner F (collaboration_effectiveness): {f_total} patterns")

            # === Miner G: Spider Data Value ===
            # Which spider data types are most valuable (volume, relevance, actionability)?
            g_total = patterns_created + patterns_updated
            try:
                from core.models_unified_system import SpiderData

                spider_stats = (
                    SpiderData.objects.filter(created_at__gte=since)
                    .values('data_type')
                    .annotate(
                        total=Count('id'),
                        avg_relevance=Avg('relevance_score'),
                        actionable_count=Count('id', filter=Q(is_actionable=True)),
                        processed_count=Count('id', filter=Q(is_processed=True)),
                    )
                    .filter(total__gte=10)
                    .order_by('-total')
                )

                for row in spider_stats:
                    data_type = row['data_type']
                    avg_rel = round(row['avg_relevance'] or 0, 1)
                    actionable_pct = round(row['actionable_count'] / row['total'] * 100, 1)
                    processed_pct = round(row['processed_count'] / row['total'] * 100, 1)
                    confidence = min(0.9, 0.4 + (row['total'] / 500))

                    pattern, created = self.LearningPattern.objects.update_or_create(
                        pattern_type='spider_data_value',
                        pattern_data__data_type=data_type,
                        defaults={
                            'description': (
                                f"Spider data type '{data_type}' has avg relevance "
                                f"{avg_rel}/100 ({row['total']} items, {actionable_pct}% actionable)"
                            ),
                            'confidence': round(confidence, 3),
                            'pattern_data': {
                                'data_type': data_type,
                                'total_items': row['total'],
                                'avg_relevance': avg_rel,
                                'actionable_count': row['actionable_count'],
                                'actionable_pct': actionable_pct,
                                'processed_pct': processed_pct,
                                'days_analyzed': days_back,
                                'mined_at': timezone.now().isoformat(),
                            },
                            'applies_to_agents': [],
                            'is_active': True,
                        }
                    )
                    if created:
                        patterns_created += 1
                    else:
                        patterns_updated += 1

            except Exception as e:
                logger.warning(f"  Miner G (spider_data_value) failed: {e}")

            g_total = (patterns_created + patterns_updated) - g_total
            logger.info(f"  Miner G (spider_data_value): {g_total} patterns")

            # === Deactivate stale patterns ===
            stale_cutoff = timezone.now() - timedelta(days=60)
            stale_patterns = self.LearningPattern.objects.filter(
                is_active=True,
                updated_at__lt=stale_cutoff,
                pattern_type__in=[
                    'agent_success_rate', 'content_quality', 'tool_reliability',
                    'prediction_accuracy', 'agent_tool_effectiveness',
                    'collaboration_effectiveness', 'spider_data_value',
                ]
            )
            stale_count = stale_patterns.update(is_active=False)
            if stale_count > 0:
                logger.info(f"  Deactivated {stale_count} stale patterns (>60 days old)")

            total_patterns = self.LearningPattern.objects.filter(is_active=True).count()

            result = {
                'patterns_created': patterns_created,
                'patterns_updated': patterns_updated,
                'stale_deactivated': stale_count,
                'total_active_patterns': total_patterns,
                'days_analyzed': days_back,
                'mined_at': timezone.now().isoformat(),
            }

            logger.info(
                f"Pattern mining complete: "
                f"{patterns_created} created, {patterns_updated} updated, {stale_count} deactivated"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to mine patterns: {e}")
            return {
                'error': str(e),
                'patterns_created': patterns_created,
                'patterns_updated': patterns_updated,
            }

    def maintain_knowledge_freshness(self) -> Dict[str, Any]:
        """
        Session 767: Maintain knowledge source freshness scores.

        This method:
        1. Decays freshness_score based on age (newer = fresher)
        2. Deactivates sources that are too stale (freshness < 0.1)
        3. Marks expired sources as inactive
        4. Prioritizes agents with stale knowledge for re-learning

        Returns:
            Dict with maintenance statistics
        """
        from django.utils import timezone
        from django.db.models import F, Q
        from core.models_unified_system import AgentKnowledgeSource

        now = timezone.now()
        sources_decayed = 0
        sources_deactivated = 0
        sources_expired = 0

        logger.info("🔄 [Session 767] Running knowledge freshness maintenance...")

        try:
            # === Step 1: Mark expired sources as inactive ===
            expired = AgentKnowledgeSource.objects.filter(
                is_active=True,
                expires_at__lt=now
            )
            sources_expired = expired.update(is_active=False, freshness_score=0.0)
            if sources_expired > 0:
                logger.info(f"  ⏰ Marked {sources_expired} expired sources as inactive")

            # === Step 2: Decay freshness scores based on age ===
            # Formula: freshness = max(0.1, 1.0 - (days_old / 60))
            # 0 days = 1.0, 30 days = 0.5, 60+ days = 0.1 (minimum)
            active_sources = AgentKnowledgeSource.objects.filter(is_active=True)

            for source in active_sources:
                days_old = (now - source.last_updated_at).days
                if days_old > 0:
                    # Calculate new freshness
                    new_freshness = max(0.1, 1.0 - (days_old / 60))

                    if abs(source.freshness_score - new_freshness) > 0.05:
                        source.freshness_score = round(new_freshness, 2)
                        source.save(update_fields=['freshness_score'])
                        sources_decayed += 1

            # === Step 3: Deactivate very stale sources (freshness < 0.1, > 90 days old) ===
            very_stale = AgentKnowledgeSource.objects.filter(
                is_active=True,
                freshness_score__lt=0.1,
                last_updated_at__lt=now - timedelta(days=90)
            )
            sources_deactivated = very_stale.update(is_active=False)
            if sources_deactivated > 0:
                logger.info(f"  🗑️ Deactivated {sources_deactivated} very stale sources (>90 days, <0.1 freshness)")

            # === Step 4: Get freshness statistics ===
            total_active = AgentKnowledgeSource.objects.filter(is_active=True).count()
            total_inactive = AgentKnowledgeSource.objects.filter(is_active=False).count()

            fresh_count = AgentKnowledgeSource.objects.filter(
                is_active=True, freshness_score__gte=0.7
            ).count()
            moderate_count = AgentKnowledgeSource.objects.filter(
                is_active=True, freshness_score__gte=0.3, freshness_score__lt=0.7
            ).count()
            stale_count = AgentKnowledgeSource.objects.filter(
                is_active=True, freshness_score__lt=0.3
            ).count()

            # === Step 5: Identify agents needing re-learning ===
            from django.db.models import Avg
            agents_by_freshness = AgentKnowledgeSource.objects.filter(
                is_active=True
            ).values('agent__name').annotate(
                avg_freshness=Avg('freshness_score')
            ).filter(
                avg_freshness__lt=0.3  # Agents with average freshness < 0.3
            ).order_by('avg_freshness')[:10]

            agents_needing_refresh = [
                {'name': a['agent__name'], 'avg_freshness': round(a['avg_freshness'], 2)}
                for a in agents_by_freshness
            ]

            result = {
                'sources_decayed': sources_decayed,
                'sources_deactivated': sources_deactivated,
                'sources_expired': sources_expired,
                'total_active': total_active,
                'total_inactive': total_inactive,
                'freshness_distribution': {
                    'fresh (≥0.7)': fresh_count,
                    'moderate (0.3-0.7)': moderate_count,
                    'stale (<0.3)': stale_count,
                },
                'agents_needing_refresh': agents_needing_refresh,
                'maintained_at': now.isoformat(),
            }

            logger.info(
                f"🔄 [Session 767] Freshness maintenance complete: "
                f"{sources_decayed} decayed, {sources_deactivated} deactivated, "
                f"{total_active} active sources"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to maintain knowledge freshness: {e}")
            return {
                'error': str(e),
                'sources_decayed': sources_decayed,
                'sources_deactivated': sources_deactivated,
            }

    def promote_to_shared_knowledge(self, min_confidence: float = 0.7) -> Dict[str, Any]:
        """
        Session 767: Promote high-confidence knowledge to SharedKnowledge.

        Scans AgentKnowledgeSource and KnowledgeTransfer for high-quality
        knowledge and promotes it to the SharedKnowledge repository.

        Args:
            min_confidence: Minimum confidence score for promotion (default 0.7)

        Returns:
            Dict with promotion statistics
        """
        from django.utils import timezone
        from core.models_unified_system import (
            AgentKnowledgeSource, KnowledgeTransfer, SharedKnowledge
        )

        promoted_from_sources = 0
        promoted_from_transfers = 0
        skipped_existing = 0

        logger.info(f"🚀 [Session 767] Promoting high-confidence knowledge (min: {min_confidence})...")

        try:
            # === Promote from AgentKnowledgeSource ===
            high_conf_sources = AgentKnowledgeSource.objects.filter(
                is_active=True,
                confidence_score__gte=min_confidence,
                freshness_score__gte=0.3  # Not too stale
            ).select_related('agent').order_by('-confidence_score')[:50]

            for source in high_conf_sources:
                # Check if already shared
                existing = SharedKnowledge.objects.filter(
                    title=source.title,
                    source_agent=source.agent.name
                ).exists()

                if existing:
                    skipped_existing += 1
                    continue

                SharedKnowledge.objects.create(
                    source_agent=source.agent.name,
                    knowledge_type='insight',  # From spider knowledge
                    title=source.title,
                    description=source.summary,
                    knowledge_content={
                        'key_insights': source.key_insights,
                        'source_spiders': source.source_spider_names,
                        'data_points': source.data_points_count,
                        'original_source_id': str(source.id),
                        'promoted_from': 'AgentKnowledgeSource',
                        'session': 767,
                    },
                    domain=source.knowledge_type,
                    tags=source.source_spider_names[:5],
                    effectiveness_score=source.confidence_score,
                    learned_by_agents=[source.agent.name],
                )
                promoted_from_sources += 1

            # === Promote from high-usefulness KnowledgeTransfer ===
            high_useful_transfers = KnowledgeTransfer.objects.filter(
                usefulness_score__gte=0.8,
                was_useful=True
            ).select_related('connection__teacher_agent', 'source_knowledge').order_by('-usefulness_score')[:30]

            for transfer in high_useful_transfers:
                teacher = transfer.connection.teacher_agent
                source_knowledge = transfer.source_knowledge

                # Check if already shared
                existing = SharedKnowledge.objects.filter(
                    title=transfer.transfer_summary[:200],
                    source_agent=teacher.name
                ).exists()

                if existing:
                    skipped_existing += 1
                    continue

                SharedKnowledge.objects.create(
                    source_agent=teacher.name,
                    knowledge_type='technique',  # From knowledge transfer
                    title=transfer.transfer_summary[:200],
                    description=transfer.transfer_summary,
                    knowledge_content={
                        'key_points': transfer.key_points,
                        'original_source_id': str(source_knowledge.id) if source_knowledge else None,
                        'transfer_id': str(transfer.id),
                        'was_applied': transfer.was_applied,
                        'application_result': transfer.application_result,
                        'promoted_from': 'KnowledgeTransfer',
                        'session': 767,
                    },
                    domain=source_knowledge.knowledge_type if source_knowledge else 'general',
                    tags=['knowledge_transfer', f'from_{teacher.name.lower()}'],
                    effectiveness_score=transfer.usefulness_score,
                    learned_by_agents=[teacher.name, transfer.connection.student_agent.name],
                )
                promoted_from_transfers += 1

            total_shared = SharedKnowledge.objects.count()

            result = {
                'promoted_from_sources': promoted_from_sources,
                'promoted_from_transfers': promoted_from_transfers,
                'skipped_existing': skipped_existing,
                'total_shared_knowledge': total_shared,
                'min_confidence': min_confidence,
                'promoted_at': timezone.now().isoformat(),
            }

            logger.info(
                f"🚀 [Session 767] Knowledge promotion complete: "
                f"{promoted_from_sources} from sources, {promoted_from_transfers} from transfers, "
                f"{total_shared} total shared knowledge"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to promote knowledge: {e}")
            return {
                'error': str(e),
                'promoted_from_sources': promoted_from_sources,
                'promoted_from_transfers': promoted_from_transfers,
            }

    def get_summary(
        self,
        agent_name: str,
        task: str = '',
        max_chars: int = 150
    ) -> str:
        """
        Session 806: Build a compact summary of learning patterns.

        This method returns a single-line summary suitable for prompt injection
        with minimal token usage (~40 tokens vs ~200 for full context).

        Args:
            agent_name: Name of the agent
            task: Current task description
            max_chars: Maximum characters for the summary

        Returns:
            Compact summary string like:
            "Effectiveness: +15% as teacher | Best collaborators: ResearchAgent"
        """
        try:
            patterns = self.get_patterns_for_agent(agent_name, task)

            if not patterns.get('has_patterns'):
                return ""

            # Use the built-in summary if available and short enough
            summary = patterns.get('summary', '')
            if summary and len(summary) <= max_chars:
                return summary

            # Build more compact summary
            parts = []

            # Effectiveness improvement (most important)
            improvement = patterns.get('effectiveness_improvement', {})
            if improvement:
                if improvement.get('as_teacher'):
                    parts.append(f"+{improvement['as_teacher']}% teaching")
                if improvement.get('as_student'):
                    parts.append(f"+{improvement['as_student']}% learning")

            # Best collaborator (just one)
            collabs = patterns.get('collaboration_insights', [])
            if collabs and 'Works well with' in collabs[0]:
                name = collabs[0].split('Works well with ')[1].split(' (')[0]
                parts.append(f"Works with {name}")

            # Success area (just one)
            success = patterns.get('success_patterns', [])
            if success:
                task_type = success[0].get('task_type', '')
                if task_type:
                    parts.append(f"Excels: {task_type}")

            # Stored pattern highlights (one line per type, most impactful first)
            stored = patterns.get('stored_patterns', [])
            rendered_types = set()
            for p in stored:
                ptype = p['type']
                if ptype in rendered_types:
                    continue
                pdata = p.get('data', {})

                if ptype == 'agent_success_rate':
                    rate = pdata.get('success_rate')
                    if rate is not None:
                        parts.append(f"{rate}% success")
                        rendered_types.add(ptype)
                elif ptype == 'content_quality':
                    avg_q = pdata.get('avg_quality')
                    if avg_q is not None:
                        parts.append(f"Quality: {avg_q:.2f}")
                        rendered_types.add(ptype)
                elif ptype == 'collaboration_effectiveness':
                    delta = pdata.get('quality_delta')
                    if delta is not None and delta > 0:
                        parts.append(f"Collab: +{delta:.0%}")
                        rendered_types.add(ptype)
                elif ptype == 'prediction_accuracy':
                    acc = pdata.get('accuracy_pct')
                    if acc is not None:
                        parts.append(f"Pred: {acc}%")
                        rendered_types.add(ptype)

            result = " | ".join(parts)

            if len(result) > max_chars:
                result = result[:max_chars - 3] + "..."

            logger.debug(f"📚 [Session 806] Learning summary: {len(result)} chars")
            return result

        except Exception as e:
            logger.warning(f"Failed to build learning summary: {e}")
            return ""

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
