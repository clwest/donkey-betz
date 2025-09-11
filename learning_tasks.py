#!/usr/bin/env python3
"""
Learning Tasks - Celery tasks for periodic learning cycles

This module defines Celery tasks that run the learning loops, auto-optimization,
and conversation analysis on scheduled intervals.
"""

import os
import sys
from datetime import datetime, timedelta

# Setup Django before importing Celery
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from celery import shared_task
from celery.schedules import crontab
from django.utils import timezone
from django.conf import settings

# Import our learning modules
from learning_engine import LearningLoopEngine
from auto_optimizer import AutoOptimizer
from conversation_memory import ConversationMemory

from core.models import SystemConfiguration, PlatformMetrics


@shared_task(bind=True, max_retries=3)
def run_learning_cycle(self):
    """
    Run the complete learning cycle
    Scheduled to run daily at 2 AM
    """
    try:
        print("🧠 Starting scheduled learning cycle...")
        
        engine = LearningLoopEngine()
        results = engine.run_full_learning_cycle()
        
        # Record task completion
        PlatformMetrics.objects.create(
            metric_name="scheduled_learning_cycle_success",
            metric_value=1.0,
            metric_type='counter',
            subsystem='learning_tasks',
            labels={
                'task_id': self.request.id,
                'timestamp': timezone.now().isoformat(),
                'feedback_insights': results['feedback_insights'],
                'content_insights': results['content_insights'],
                'optimizations_applied': results['optimizations_applied']
            }
        )
        
        return {
            'status': 'success',
            'results': results,
            'task_id': self.request.id,
            'completed_at': timezone.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Learning cycle failed: {str(e)}")
        
        # Record failure
        PlatformMetrics.objects.create(
            metric_name="scheduled_learning_cycle_failure",
            metric_value=1.0,
            metric_type='counter',
            subsystem='learning_tasks',
            labels={
                'task_id': self.request.id,
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
        )
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def run_auto_optimization(self):
    """
    Run auto-optimization cycle
    Scheduled to run every 6 hours
    """
    try:
        print("🚀 Starting scheduled auto-optimization...")
        
        optimizer = AutoOptimizer()
        results = optimizer.run_optimization_cycle()
        
        # Record task completion
        PlatformMetrics.objects.create(
            metric_name="scheduled_optimization_success",
            metric_value=1.0,
            metric_type='counter',
            subsystem='learning_tasks',
            labels={
                'task_id': self.request.id,
                'timestamp': timezone.now().isoformat(),
                'total_optimizations': results['total_optimizations'],
                'performance_issues': results['performance_issues']
            }
        )
        
        return {
            'status': 'success',
            'results': results,
            'task_id': self.request.id,
            'completed_at': timezone.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Auto-optimization failed: {str(e)}")
        
        # Record failure
        PlatformMetrics.objects.create(
            metric_name="scheduled_optimization_failure",
            metric_value=1.0,
            metric_type='counter',
            subsystem='learning_tasks',
            labels={
                'task_id': self.request.id,
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
        )
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=2)
def analyze_conversation_patterns(self):
    """
    Analyze conversation patterns and update insights
    Scheduled to run daily at 4 AM
    """
    try:
        print("🔍 Starting conversation pattern analysis...")
        
        memory = ConversationMemory()
        analysis = memory.analyze_conversation_patterns()
        
        # Store analysis results as platform metrics
        PlatformMetrics.objects.create(
            metric_name="conversation_analysis_total_interactions",
            metric_value=float(analysis['total_interactions']),
            metric_type='gauge',
            subsystem='conversation',
            labels=analysis
        )
        
        PlatformMetrics.objects.create(
            metric_name="conversation_analysis_unique_users",
            metric_value=float(analysis['unique_users']),
            metric_type='gauge',
            subsystem='conversation',
            labels=analysis
        )
        
        # Record task completion
        PlatformMetrics.objects.create(
            metric_name="scheduled_conversation_analysis_success",
            metric_value=1.0,
            metric_type='counter',
            subsystem='learning_tasks',
            labels={
                'task_id': self.request.id,
                'timestamp': timezone.now().isoformat(),
                'interactions_analyzed': analysis['total_interactions'],
                'users_analyzed': analysis['unique_users']
            }
        )
        
        return {
            'status': 'success',
            'analysis': analysis,
            'task_id': self.request.id,
            'completed_at': timezone.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Conversation analysis failed: {str(e)}")
        
        # Record failure
        PlatformMetrics.objects.create(
            metric_name="scheduled_conversation_analysis_failure",
            metric_value=1.0,
            metric_type='counter',
            subsystem='learning_tasks',
            labels={
                'task_id': self.request.id,
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
        )
        
        # Retry with shorter backoff for analysis tasks
        raise self.retry(exc=e, countdown=30 * (2 ** self.request.retries))


@shared_task(bind=True)
def cleanup_old_learning_data(self):
    """
    Clean up old learning data and metrics
    Scheduled to run weekly on Sunday at 1 AM
    """
    try:
        print("🧹 Starting learning data cleanup...")
        
        cleanup_date = timezone.now() - timedelta(days=90)
        
        # Clean up old platform metrics (keep 90 days)
        old_metrics = PlatformMetrics.objects.filter(
            created_at__lt=cleanup_date,
            subsystem__in=['learning', 'optimization', 'conversation', 'learning_tasks']
        )
        
        metrics_deleted = old_metrics.count()
        old_metrics.delete()
        
        # Clean up old conversation memory (keep 90 days for inactive users)
        old_conversation_configs = SystemConfiguration.objects.filter(
            key__startswith='conversation_',
            created_at__lt=cleanup_date,
            category='conversation'
        )
        
        # Only delete if the user hasn't been active recently
        configs_to_delete = []
        for config in old_conversation_configs:
            # Extract user_id from key
            if 'conversation_interaction_' in config.key:
                try:
                    user_id = int(config.key.split('_')[2])
                    # Check if user has recent activity
                    recent_activity = SystemConfiguration.objects.filter(
                        key__startswith=f'conversation_interaction_{user_id}_',
                        created_at__gte=cleanup_date
                    ).exists()
                    
                    if not recent_activity:
                        configs_to_delete.append(config)
                except (ValueError, IndexError):
                    # If we can't parse user_id, it's probably old/malformed data
                    configs_to_delete.append(config)
        
        conversations_deleted = len(configs_to_delete)
        for config in configs_to_delete:
            config.delete()
        
        # Record cleanup results
        PlatformMetrics.objects.create(
            metric_name="learning_data_cleanup_completed",
            metric_value=1.0,
            metric_type='counter',
            subsystem='learning_tasks',
            labels={
                'task_id': self.request.id,
                'timestamp': timezone.now().isoformat(),
                'metrics_deleted': metrics_deleted,
                'conversations_deleted': conversations_deleted,
                'cleanup_days': 90
            }
        )
        
        return {
            'status': 'success',
            'metrics_deleted': metrics_deleted,
            'conversations_deleted': conversations_deleted,
            'task_id': self.request.id,
            'completed_at': timezone.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Learning data cleanup failed: {str(e)}")
        
        # Record failure but don't retry cleanup tasks
        PlatformMetrics.objects.create(
            metric_name="learning_data_cleanup_failure",
            metric_value=1.0,
            metric_type='counter',
            subsystem='learning_tasks',
            labels={
                'task_id': self.request.id,
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
        )
        
        return {
            'status': 'failed',
            'error': str(e),
            'task_id': self.request.id
        }


@shared_task(bind=True)
def health_check_learning_system(self):
    """
    Perform health check on learning system components
    Scheduled to run every hour
    """
    try:
        print("🔍 Performing learning system health check...")
        
        health_status = {
            'timestamp': timezone.now().isoformat(),
            'components': {}
        }
        
        # Check if learning engine is functional
        try:
            engine = LearningLoopEngine()
            # Just check if we can instantiate and access basic methods
            health_status['components']['learning_engine'] = 'healthy'
        except Exception as e:
            health_status['components']['learning_engine'] = f'unhealthy: {str(e)}'
        
        # Check if auto-optimizer is functional
        try:
            optimizer = AutoOptimizer()
            health_status['components']['auto_optimizer'] = 'healthy'
        except Exception as e:
            health_status['components']['auto_optimizer'] = f'unhealthy: {str(e)}'
        
        # Check if conversation memory is functional
        try:
            memory = ConversationMemory()
            stats = memory.get_memory_stats()
            health_status['components']['conversation_memory'] = 'healthy'
            health_status['memory_stats'] = stats
        except Exception as e:
            health_status['components']['conversation_memory'] = f'unhealthy: {str(e)}'
        
        # Check recent learning activity
        recent_learning = PlatformMetrics.objects.filter(
            metric_name__in=[
                'learning_cycle_completed',
                'auto_optimization_cycle_completed',
                'conversation_analysis_total_interactions'
            ],
            created_at__gte=timezone.now() - timedelta(hours=48)
        ).count()
        
        health_status['recent_learning_activity'] = recent_learning
        
        # Determine overall health
        unhealthy_components = [
            comp for comp, status in health_status['components'].items() 
            if not status == 'healthy'
        ]
        
        overall_health = 'healthy' if len(unhealthy_components) == 0 else 'degraded'
        if len(unhealthy_components) >= 2:
            overall_health = 'unhealthy'
        
        health_status['overall_health'] = overall_health
        health_status['unhealthy_components'] = unhealthy_components
        
        # Record health check
        PlatformMetrics.objects.create(
            metric_name="learning_system_health_check",
            metric_value=1.0 if overall_health == 'healthy' else 0.5 if overall_health == 'degraded' else 0.0,
            metric_type='gauge',
            subsystem='learning_tasks',
            labels=health_status
        )
        
        return health_status
        
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e),
            'task_id': self.request.id
        }


# Manual task triggers for immediate execution
@shared_task
def trigger_immediate_learning():
    """Trigger immediate learning cycle (for manual execution)"""
    return run_learning_cycle.delay()


@shared_task  
def trigger_immediate_optimization():
    """Trigger immediate optimization cycle (for manual execution)"""
    return run_auto_optimization.delay()


@shared_task
def get_learning_system_status():
    """Get current status of learning system"""
    try:
        # Get recent task results
        recent_learning = PlatformMetrics.objects.filter(
            metric_name__in=[
                'scheduled_learning_cycle_success',
                'scheduled_optimization_success', 
                'scheduled_conversation_analysis_success'
            ],
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        recent_failures = PlatformMetrics.objects.filter(
            metric_name__in=[
                'scheduled_learning_cycle_failure',
                'scheduled_optimization_failure',
                'scheduled_conversation_analysis_failure'
            ],
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Get last health check
        last_health_check = PlatformMetrics.objects.filter(
            metric_name='learning_system_health_check'
        ).order_by('-created_at').first()
        
        last_health = 'unknown'
        if last_health_check and last_health_check.labels:
            last_health = last_health_check.labels.get('overall_health', 'unknown')
        
        # Get learning metrics
        memory = ConversationMemory()
        memory_stats = memory.get_memory_stats()
        
        return {
            'recent_successful_tasks': recent_learning,
            'recent_failed_tasks': recent_failures,
            'last_health_status': last_health,
            'last_health_check': last_health_check.created_at.isoformat() if last_health_check else None,
            'memory_statistics': memory_stats,
            'system_status': 'operational' if recent_failures == 0 else 'degraded'
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'system_status': 'error'
        }


if __name__ == "__main__":
    print("🧠 Learning Tasks Module")
    print("=" * 50)
    print("Available tasks:")
    print("• run_learning_cycle - Complete learning analysis")
    print("• run_auto_optimization - Performance optimization") 
    print("• analyze_conversation_patterns - Conversation analysis")
    print("• cleanup_old_learning_data - Data maintenance")
    print("• health_check_learning_system - System health check")
    print("\nManual triggers:")
    print("• trigger_immediate_learning")
    print("• trigger_immediate_optimization") 
    print("• get_learning_system_status")
    
    # Test system status
    print("\n📊 Current System Status:")
    from celery import Celery
    from django.conf import settings
    
    # Get status without Celery if possible
    try:
        status = get_learning_system_status()
        for key, value in status.items():
            print(f"   • {key}: {value}")
    except Exception as e:
        print(f"   Error getting status: {e}")