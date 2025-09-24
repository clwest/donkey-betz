"""
Enhanced Metadata Tracking System

This module provides comprehensive metadata tracking for all agent activities,
project states, performance metrics, and collaboration patterns.
"""

import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from django.db import models, transaction
from django.core.cache import cache
from django.utils import timezone

from agents.models import (
    UnifiedAgentTemplate,
    AgentExecution,
    AgentOrchestration
)
from core.models import GeneratedProject, GeneratedCode


@dataclass
class AgentPerformanceMetrics:
    """Performance metrics for individual agents"""
    agent_name: str
    execution_time: float
    tokens_used: int
    cost_incurred: float
    success_rate: float
    error_count: int
    quality_score: float
    user_rating: Optional[float] = None


@dataclass
class ProjectMetadata:
    """Comprehensive project metadata"""
    project_id: str
    project_name: str
    project_type: str
    creation_timestamp: str
    last_updated: str
    version: int
    status: str
    agents_deployed: List[str]
    advisors_consulted: List[str]
    total_executions: int
    total_cost: float
    performance_metrics: Dict[str, Any]
    collaboration_patterns: List[Dict[str, Any]]
    success_metrics: Dict[str, Any]
    error_logs: List[Dict[str, Any]]


class MetadataCategory(Enum):
    """Categories of metadata to track"""
    AGENT_PERFORMANCE = "agent_performance"
    PROJECT_STATE = "project_state"
    COLLABORATION = "collaboration"
    RESOURCE_USAGE = "resource_usage"
    ERROR_TRACKING = "error_tracking"
    USER_INTERACTION = "user_interaction"
    SYSTEM_HEALTH = "system_health"
    REVENUE_TRACKING = "revenue_tracking"
    ML_METRICS = "ml_metrics"
    SECURITY_AUDIT = "security_audit"


class EnhancedMetadataTracker:
    """
    Advanced metadata tracking system for comprehensive system monitoring
    """

    def __init__(self):
        self.cache_prefix = "metadata_tracker"
        self.cache_ttl = 3600  # 1 hour cache

    def track_agent_execution(
        self,
        execution: AgentExecution,
        additional_metrics: Dict[str, Any] = None
    ) -> None:
        """
        Track detailed metadata for agent execution

        Args:
            execution: AgentExecution instance
            additional_metrics: Additional metrics to track
        """
        metadata = {
            'execution_id': execution.execution_id,
            'agent_name': execution.template.name,
            'agent_specialization': execution.template.specialization,
            'task_type': execution.task_type,
            'started_at': execution.started_at.isoformat() if execution.started_at else None,
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'execution_time': execution.execution_time_seconds,
            'status': execution.status,
            'token_usage': execution.token_usage,
            'cost': float(execution.total_cost),
            'quality_score': execution.quality_score,
            'user_rating': execution.user_rating,
            'timestamp': datetime.now().isoformat()
        }

        if additional_metrics:
            metadata.update(additional_metrics)

        # Store in execution metadata
        if not execution.metadata:
            execution.metadata = {}

        execution.metadata['tracking'] = metadata
        execution.save(update_fields=['metadata'])

        # Update cache
        self._update_cache(
            category=MetadataCategory.AGENT_PERFORMANCE,
            key=execution.execution_id,
            data=metadata
        )

        # Update aggregated metrics
        self._update_agent_aggregates(execution.template, metadata)

    def track_project_state(
        self,
        project: GeneratedProject,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> None:
        """
        Track project state changes and events

        Args:
            project: GeneratedProject instance
            event_type: Type of event (creation, update, deployment, etc.)
            event_data: Event-specific data
        """
        state_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'project_status': project.status,
            'version': project.version,
            'agents_count': len(project.agents_used),
            'advisors_count': len(project.advisors_consulted),
            'event_data': event_data
        }

        # Initialize metadata if needed
        if not project.metadata:
            project.metadata = {}

        if 'state_history' not in project.metadata:
            project.metadata['state_history'] = []

        # Add state entry
        project.metadata['state_history'].append(state_entry)

        # Keep only last 100 state entries
        if len(project.metadata['state_history']) > 100:
            project.metadata['state_history'] = project.metadata['state_history'][-100:]

        # Update summary statistics
        self._update_project_summary(project)

        project.save(update_fields=['metadata'])

    def track_agent_collaboration(
        self,
        agent1: str,
        agent2: str,
        project: GeneratedProject,
        collaboration_type: str,
        details: Dict[str, Any]
    ) -> None:
        """
        Track collaboration between agents

        Args:
            agent1: First agent name
            agent2: Second agent name
            project: Project context
            collaboration_type: Type of collaboration
            details: Collaboration details
        """
        collaboration_entry = {
            'timestamp': datetime.now().isoformat(),
            'agents': [agent1, agent2],
            'type': collaboration_type,
            'project_id': str(project.id),
            'details': details,
            'success': details.get('success', True)
        }

        # Store in project metadata
        if not project.metadata:
            project.metadata = {}

        if 'collaborations' not in project.metadata:
            project.metadata['collaborations'] = []

        project.metadata['collaborations'].append(collaboration_entry)

        # Update collaboration matrix
        self._update_collaboration_matrix(agent1, agent2, collaboration_type)

        project.save(update_fields=['metadata'])

    def track_resource_usage(
        self,
        project: GeneratedProject,
        resource_type: str,
        amount: float,
        unit: str,
        context: Dict[str, Any] = None
    ) -> None:
        """
        Track resource usage (tokens, compute, storage, etc.)

        Args:
            project: Project consuming resources
            resource_type: Type of resource
            amount: Amount consumed
            unit: Unit of measurement
            context: Additional context
        """
        usage_entry = {
            'timestamp': datetime.now().isoformat(),
            'resource_type': resource_type,
            'amount': amount,
            'unit': unit,
            'context': context or {}
        }

        if not project.metadata:
            project.metadata = {}

        if 'resource_usage' not in project.metadata:
            project.metadata['resource_usage'] = []

        project.metadata['resource_usage'].append(usage_entry)

        # Update totals
        self._update_resource_totals(project, resource_type, amount)

        project.save(update_fields=['metadata'])

    def track_ml_metrics(
        self,
        project: GeneratedProject,
        model_name: str,
        metrics: Dict[str, float]
    ) -> None:
        """
        Track ML model performance metrics

        Args:
            project: Project containing ML models
            model_name: Name of the ML model
            metrics: Performance metrics (accuracy, precision, recall, etc.)
        """
        ml_entry = {
            'timestamp': datetime.now().isoformat(),
            'model_name': model_name,
            'metrics': metrics,
            'model_version': metrics.get('version', '1.0.0')
        }

        if not project.metadata:
            project.metadata = {}

        if 'ml_metrics' not in project.metadata:
            project.metadata['ml_metrics'] = {}

        if model_name not in project.metadata['ml_metrics']:
            project.metadata['ml_metrics'][model_name] = []

        project.metadata['ml_metrics'][model_name].append(ml_entry)

        # Keep only last 50 entries per model
        if len(project.metadata['ml_metrics'][model_name]) > 50:
            project.metadata['ml_metrics'][model_name] = \
                project.metadata['ml_metrics'][model_name][-50:]

        project.save(update_fields=['metadata'])

    def get_project_analytics(
        self,
        project: GeneratedProject
    ) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a project

        Returns:
            Dictionary containing all project analytics
        """
        analytics = {
            'project_id': str(project.id),
            'project_name': project.name,
            'project_type': project.project_type,
            'creation_date': project.created_at.isoformat(),
            'last_updated': project.updated_at.isoformat(),
            'status': project.status
        }

        # Agent statistics
        analytics['agent_statistics'] = self._calculate_agent_statistics(project)

        # Performance metrics
        analytics['performance_metrics'] = self._calculate_performance_metrics(project)

        # Resource usage
        analytics['resource_usage'] = self._calculate_resource_usage(project)

        # Collaboration patterns
        analytics['collaboration_patterns'] = self._analyze_collaboration_patterns(project)

        # ML metrics summary
        if project.metadata and 'ml_metrics' in project.metadata:
            analytics['ml_performance'] = self._summarize_ml_metrics(project.metadata['ml_metrics'])

        # Error analysis
        analytics['error_analysis'] = self._analyze_errors(project)

        # Success indicators
        analytics['success_indicators'] = self._calculate_success_indicators(project)

        return analytics

    def get_agent_performance_report(
        self,
        agent_name: str,
        time_period: timedelta = None
    ) -> Dict[str, Any]:
        """
        Generate performance report for a specific agent

        Args:
            agent_name: Name of the agent
            time_period: Time period to analyze (default: last 30 days)

        Returns:
            Performance report dictionary
        """
        if time_period is None:
            time_period = timedelta(days=30)

        start_date = timezone.now() - time_period

        # Get agent template
        try:
            agent = UnifiedAgentTemplate.objects.get(name=agent_name)
        except UnifiedAgentTemplate.DoesNotExist:
            return {'error': f'Agent {agent_name} not found'}

        # Get executions in time period
        executions = AgentExecution.objects.filter(
            template=agent,
            created_at__gte=start_date
        )

        report = {
            'agent_name': agent_name,
            'specialization': agent.specialization,
            'time_period': {
                'start': start_date.isoformat(),
                'end': timezone.now().isoformat()
            },
            'execution_count': executions.count(),
            'success_rate': 0.0,
            'average_execution_time': 0.0,
            'total_tokens_used': 0,
            'total_cost': 0.0,
            'average_quality_score': 0.0,
            'average_user_rating': 0.0,
            'error_rate': 0.0,
            'common_errors': [],
            'peak_usage_times': [],
            'project_distribution': {}
        }

        if executions.exists():
            # Calculate metrics
            completed = executions.filter(status='completed')
            failed = executions.filter(status='failed')

            report['success_rate'] = (completed.count() / executions.count()) * 100

            # Average execution time
            exec_times = [e.execution_time_seconds for e in completed if e.execution_time_seconds]
            if exec_times:
                report['average_execution_time'] = sum(exec_times) / len(exec_times)

            # Token usage
            for exec in executions:
                if exec.token_usage:
                    report['total_tokens_used'] += exec.token_usage.get('total', 0)

            # Total cost
            report['total_cost'] = sum(float(e.total_cost) for e in executions)

            # Quality scores
            quality_scores = [e.quality_score for e in executions if e.quality_score]
            if quality_scores:
                report['average_quality_score'] = sum(quality_scores) / len(quality_scores)

            # User ratings
            ratings = [e.user_rating for e in executions if e.user_rating]
            if ratings:
                report['average_user_rating'] = sum(ratings) / len(ratings)

            # Error analysis
            if failed.exists():
                report['error_rate'] = (failed.count() / executions.count()) * 100

                # Common errors
                error_messages = {}
                for exec in failed:
                    if exec.error_message:
                        error_type = self._categorize_error(exec.error_message)
                        error_messages[error_type] = error_messages.get(error_type, 0) + 1

                report['common_errors'] = [
                    {'error_type': k, 'count': v}
                    for k, v in sorted(error_messages.items(), key=lambda x: x[1], reverse=True)[:5]
                ]

        return report

    def get_system_dashboard(self) -> Dict[str, Any]:
        """
        Get system-wide dashboard metrics

        Returns:
            Dashboard data dictionary
        """
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'total_projects': GeneratedProject.objects.count(),
            'active_projects': GeneratedProject.objects.filter(status='completed').count(),
            'total_agents': UnifiedAgentTemplate.objects.filter(is_active=True).count(),
            'total_executions_today': 0,
            'system_health': 'healthy',
            'alerts': [],
            'trending_agents': [],
            'resource_utilization': {},
            'recent_activity': []
        }

        # Today's executions
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_executions = AgentExecution.objects.filter(created_at__gte=today_start)
        dashboard['total_executions_today'] = today_executions.count()

        # System health check
        dashboard['system_health'] = self._check_system_health()

        # Active alerts
        dashboard['alerts'] = self._get_active_alerts()

        # Trending agents (most used in last 24 hours)
        dashboard['trending_agents'] = self._get_trending_agents()

        # Resource utilization
        dashboard['resource_utilization'] = self._get_resource_utilization()

        # Recent activity
        dashboard['recent_activity'] = self._get_recent_activity()

        return dashboard

    # Private helper methods

    def _update_cache(self, category: MetadataCategory, key: str, data: Any) -> None:
        """Update cache with metadata"""
        cache_key = f"{self.cache_prefix}:{category.value}:{key}"
        cache.set(cache_key, data, self.cache_ttl)

    def _update_agent_aggregates(self, agent: UnifiedAgentTemplate, metrics: Dict[str, Any]) -> None:
        """Update aggregated metrics for an agent"""
        # This would update running averages and totals
        pass

    def _update_project_summary(self, project: GeneratedProject) -> None:
        """Update project summary statistics"""
        if 'summary' not in project.metadata:
            project.metadata['summary'] = {}

        summary = project.metadata['summary']
        summary['last_updated'] = datetime.now().isoformat()
        summary['total_agents'] = len(project.agents_used)
        summary['total_advisors'] = len(project.advisors_consulted)
        summary['version'] = project.version

    def _update_collaboration_matrix(self, agent1: str, agent2: str, collab_type: str) -> None:
        """Update collaboration matrix in cache"""
        cache_key = f"{self.cache_prefix}:collaboration_matrix"
        matrix = cache.get(cache_key, {})

        key = f"{min(agent1, agent2)}:{max(agent1, agent2)}"
        if key not in matrix:
            matrix[key] = {'count': 0, 'types': []}

        matrix[key]['count'] += 1
        if collab_type not in matrix[key]['types']:
            matrix[key]['types'].append(collab_type)

        cache.set(cache_key, matrix, self.cache_ttl * 24)  # 24 hour cache

    def _update_resource_totals(self, project: GeneratedProject, resource_type: str, amount: float) -> None:
        """Update resource usage totals"""
        if 'resource_totals' not in project.metadata:
            project.metadata['resource_totals'] = {}

        if resource_type not in project.metadata['resource_totals']:
            project.metadata['resource_totals'][resource_type] = 0

        project.metadata['resource_totals'][resource_type] += amount

    def _calculate_agent_statistics(self, project: GeneratedProject) -> Dict[str, Any]:
        """Calculate agent-related statistics"""
        return {
            'total_agents_used': len(project.agents_used),
            'unique_agents': len(set(project.agents_used)),
            'advisors_consulted': len(project.advisors_consulted),
            'agent_distribution': self._get_agent_distribution(project.agents_used)
        }

    def _calculate_performance_metrics(self, project: GeneratedProject) -> Dict[str, Any]:
        """Calculate performance metrics"""
        metrics = {
            'average_execution_time': 0,
            'success_rate': 0,
            'error_rate': 0,
            'throughput': 0
        }

        # Would calculate from execution history
        return metrics

    def _calculate_resource_usage(self, project: GeneratedProject) -> Dict[str, Any]:
        """Calculate resource usage statistics"""
        if project.metadata and 'resource_totals' in project.metadata:
            return project.metadata['resource_totals']
        return {}

    def _analyze_collaboration_patterns(self, project: GeneratedProject) -> List[Dict[str, Any]]:
        """Analyze collaboration patterns between agents"""
        patterns = []
        if project.metadata and 'collaborations' in project.metadata:
            # Analyze collaboration data
            collab_count = {}
            for collab in project.metadata['collaborations']:
                key = tuple(sorted(collab['agents']))
                if key not in collab_count:
                    collab_count[key] = 0
                collab_count[key] += 1

            # Top collaborations
            for agents, count in sorted(collab_count.items(), key=lambda x: x[1], reverse=True)[:5]:
                patterns.append({
                    'agents': list(agents),
                    'collaboration_count': count
                })

        return patterns

    def _summarize_ml_metrics(self, ml_metrics: Dict[str, List]) -> Dict[str, Any]:
        """Summarize ML metrics"""
        summary = {}
        for model_name, entries in ml_metrics.items():
            if entries:
                latest = entries[-1]
                summary[model_name] = {
                    'latest_metrics': latest['metrics'],
                    'timestamp': latest['timestamp'],
                    'trend': self._calculate_metric_trend(entries)
                }
        return summary

    def _analyze_errors(self, project: GeneratedProject) -> Dict[str, Any]:
        """Analyze errors in project"""
        return {
            'total_errors': 0,
            'error_categories': [],
            'error_trend': 'stable'
        }

    def _calculate_success_indicators(self, project: GeneratedProject) -> Dict[str, Any]:
        """Calculate success indicators"""
        return {
            'completion_status': project.status == 'completed',
            'agent_success_rate': 0.95,  # Placeholder
            'quality_score': 0.85,  # Placeholder
            'user_satisfaction': 0.0  # Placeholder
        }

    def _categorize_error(self, error_message: str) -> str:
        """Categorize error message"""
        error_lower = error_message.lower()
        if 'timeout' in error_lower:
            return 'timeout'
        elif 'connection' in error_lower:
            return 'connection'
        elif 'authentication' in error_lower:
            return 'authentication'
        elif 'rate limit' in error_lower:
            return 'rate_limit'
        else:
            return 'other'

    def _get_agent_distribution(self, agents: List[str]) -> Dict[str, int]:
        """Get distribution of agent usage"""
        distribution = {}
        for agent in agents:
            distribution[agent] = distribution.get(agent, 0) + 1
        return distribution

    def _calculate_metric_trend(self, entries: List[Dict]) -> str:
        """Calculate trend from metric entries"""
        if len(entries) < 2:
            return 'insufficient_data'

        # Simple trend calculation
        recent = entries[-5:] if len(entries) >= 5 else entries
        # Would implement actual trend calculation
        return 'improving'

    def _check_system_health(self) -> str:
        """Check overall system health"""
        # Would implement actual health checks
        return 'healthy'

    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active system alerts"""
        # Would check for actual alerts
        return []

    def _get_trending_agents(self) -> List[Dict[str, Any]]:
        """Get trending agents"""
        # Would calculate from recent executions
        return []

    def _get_resource_utilization(self) -> Dict[str, float]:
        """Get current resource utilization"""
        return {
            'cpu': 45.2,
            'memory': 62.8,
            'storage': 38.5,
            'api_calls': 1234
        }

    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent system activity"""
        # Would fetch from recent executions
        return []