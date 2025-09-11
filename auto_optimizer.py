#!/usr/bin/env python3
"""
Auto-Optimizer - Continuously optimizes system performance

This module automatically monitors performance, identifies bottlenecks,
and applies optimizations to improve system efficiency and user experience.
"""

import os
import sys
import django
from datetime import datetime, timedelta
import json
import statistics
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Max, Min, Q
from django.utils import timezone
from decimal import Decimal

from core.models import SystemConfiguration, PlatformMetrics
from content.models import (
    ContentGeneration, ContentTemplate, Feedback,
    ContentAnalytics, Document, KnowledgeBase
)

User = get_user_model()


class AutoOptimizer:
    """
    Automated system optimizer that runs performance analysis and improvements
    """
    
    def __init__(self):
        self.optimizations_applied = []
        self.performance_metrics = {}
        self.baseline_metrics = {}
        
    def run_optimization_cycle(self):
        """Execute complete auto-optimization cycle"""
        print("🚀 Starting Auto-Optimization Cycle...")
        
        # Step 1: Collect baseline performance metrics
        self.collect_baseline_metrics()
        
        # Step 2: Analyze current performance
        performance_issues = self.analyze_performance_issues()
        
        # Step 3: Optimize templates based on performance
        template_optimizations = self.optimize_templates()
        
        # Step 4: Optimize system configurations
        config_optimizations = self.optimize_system_configs()
        
        # Step 5: Optimize resource usage
        resource_optimizations = self.optimize_resource_usage()
        
        # Step 6: Record optimization metrics
        self.record_optimization_metrics()
        
        total_optimizations = len(template_optimizations + config_optimizations + resource_optimizations)
        
        print(f"✅ Auto-optimization complete: {total_optimizations} optimizations applied")
        
        return {
            'performance_issues': len(performance_issues),
            'template_optimizations': len(template_optimizations),
            'config_optimizations': len(config_optimizations), 
            'resource_optimizations': len(resource_optimizations),
            'total_optimizations': total_optimizations,
            'baseline_metrics': self.baseline_metrics
        }
    
    def collect_baseline_metrics(self):
        """Collect current system performance baseline"""
        print("📊 Collecting baseline metrics...")
        
        # Content generation performance
        recent_generations = ContentGeneration.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        )
        
        if recent_generations.exists():
            self.baseline_metrics['avg_generation_time'] = recent_generations.aggregate(
                avg_time=Avg('generation_time_ms')
            )['avg_time'] or 0
            
            self.baseline_metrics['success_rate'] = (
                recent_generations.filter(status='completed').count() / 
                recent_generations.count() * 100
            )
            
            self.baseline_metrics['total_generations'] = recent_generations.count()
        else:
            self.baseline_metrics = {
                'avg_generation_time': 0,
                'success_rate': 0,
                'total_generations': 0
            }
        
        # User satisfaction metrics
        recent_feedback = Feedback.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        )
        
        if recent_feedback.exists():
            self.baseline_metrics['avg_user_rating'] = recent_feedback.aggregate(
                avg_rating=Avg('overall_rating')
            )['avg_rating'] or 0
            
            self.baseline_metrics['feedback_count'] = recent_feedback.count()
        else:
            self.baseline_metrics['avg_user_rating'] = 0
            self.baseline_metrics['feedback_count'] = 0
        
        # System resource metrics
        self.baseline_metrics['active_templates'] = ContentTemplate.objects.filter(
            is_active=True
        ).count()
        
        self.baseline_metrics['document_count'] = Document.objects.count()
        
        print(f"   Baseline: {self.baseline_metrics['success_rate']:.1f}% success rate, "
              f"{self.baseline_metrics['avg_generation_time']:.0f}ms avg time")
    
    def analyze_performance_issues(self):
        """Identify current performance bottlenecks"""
        print("🔍 Analyzing performance issues...")
        
        issues = []
        
        # Slow generation analysis
        slow_generations = ContentGeneration.objects.filter(
            generation_time_ms__gt=20000,  # > 20 seconds
            created_at__gte=timezone.now() - timedelta(days=7)
        )
        
        if slow_generations.count() > 0:
            avg_slow_time = slow_generations.aggregate(
                avg_time=Avg('generation_time_ms')
            )['avg_time']
            
            issues.append({
                'type': 'slow_generation',
                'severity': 'high' if slow_generations.count() > 5 else 'medium',
                'count': slow_generations.count(),
                'avg_time': avg_slow_time,
                'description': f'{slow_generations.count()} slow generations detected'
            })
        
        # High failure rate analysis
        if self.baseline_metrics['success_rate'] < 80:
            issues.append({
                'type': 'low_success_rate',
                'severity': 'high',
                'current_rate': self.baseline_metrics['success_rate'],
                'description': f'Success rate below 80%: {self.baseline_metrics["success_rate"]:.1f}%'
            })
        
        # Low user satisfaction
        if self.baseline_metrics['avg_user_rating'] < 3.5 and self.baseline_metrics['feedback_count'] > 5:
            issues.append({
                'type': 'low_satisfaction',
                'severity': 'medium',
                'current_rating': self.baseline_metrics['avg_user_rating'],
                'description': f'User rating below 3.5: {self.baseline_metrics["avg_user_rating"]:.1f}'
            })
        
        # Template performance issues
        poor_templates = []
        for template in ContentTemplate.objects.filter(is_active=True):
            recent_uses = ContentGeneration.objects.filter(
                template=template,
                created_at__gte=timezone.now() - timedelta(days=14)
            )
            
            if recent_uses.count() >= 3:
                success_rate = recent_uses.filter(status='completed').count() / recent_uses.count()
                if success_rate < 0.7:  # Less than 70% success
                    poor_templates.append({
                        'template': template.name,
                        'success_rate': success_rate * 100,
                        'uses': recent_uses.count()
                    })
        
        if poor_templates:
            issues.append({
                'type': 'poor_template_performance',
                'severity': 'medium',
                'templates': poor_templates,
                'description': f'{len(poor_templates)} templates with low success rates'
            })
        
        print(f"   Identified {len(issues)} performance issues")
        return issues
    
    def optimize_templates(self):
        """Optimize content templates based on performance data"""
        print("🎯 Optimizing templates...")
        
        optimizations = []
        
        # Update template statistics and optimize poor performers
        for template in ContentTemplate.objects.filter(is_active=True):
            recent_uses = ContentGeneration.objects.filter(
                template=template,
                created_at__gte=timezone.now() - timedelta(days=30)
            )
            
            if recent_uses.count() >= 2:  # Minimum data for optimization
                # Calculate updated statistics
                total_uses = recent_uses.count()
                successful_uses = recent_uses.filter(status='completed').count()
                success_rate = successful_uses / total_uses if total_uses > 0 else 0
                
                # Calculate average generation time
                completed_uses = recent_uses.filter(
                    status='completed',
                    generation_time_ms__isnull=False
                )
                
                if completed_uses.exists():
                    avg_time = completed_uses.aggregate(
                        avg_time=Avg('generation_time_ms')
                    )['avg_time']
                else:
                    avg_time = template.avg_generation_time * 1000  # Convert to ms
                
                # Update template statistics
                old_success_rate = template.success_rate
                template.success_rate = success_rate
                template.avg_generation_time = avg_time / 1000 if avg_time else 0  # Convert to seconds
                template.usage_count = template.usage_count + total_uses
                
                # Optimize based on performance
                optimization_applied = False
                
                # If success rate is low, adjust generation config
                if success_rate < 0.8 and success_rate < old_success_rate:
                    # Increase temperature for more creativity or reduce for more consistency
                    current_config = template.generation_config
                    if 'temperature' in current_config:
                        if current_config['temperature'] > 0.7:
                            current_config['temperature'] = max(0.3, current_config['temperature'] - 0.2)
                            optimization_applied = True
                        elif current_config['temperature'] < 0.3:
                            current_config['temperature'] = min(0.7, current_config['temperature'] + 0.2)
                            optimization_applied = True
                    else:
                        current_config['temperature'] = 0.5
                        optimization_applied = True
                    
                    template.generation_config = current_config
                
                # If generation time is too high, optimize for speed
                if avg_time and avg_time > 30000:  # > 30 seconds
                    current_config = template.generation_config
                    if 'max_tokens' in current_config and current_config['max_tokens'] > 1000:
                        current_config['max_tokens'] = min(current_config['max_tokens'], 2000)
                        optimization_applied = True
                    
                    template.generation_config = current_config
                
                if optimization_applied or abs(template.success_rate - old_success_rate) > 0.05:
                    template.save()
                    optimizations.append({
                        'template': template.name,
                        'old_success_rate': old_success_rate,
                        'new_success_rate': success_rate,
                        'optimization_type': 'performance_tuning',
                        'config_updated': optimization_applied
                    })
        
        print(f"   Optimized {len(optimizations)} templates")
        return optimizations
    
    def optimize_system_configs(self):
        """Optimize system-wide configuration settings"""
        print("⚙️ Optimizing system configurations...")
        
        optimizations = []
        
        # Optimize content generation settings based on current performance
        if self.baseline_metrics['avg_generation_time'] > 15000:  # > 15 seconds
            # Set faster generation defaults
            SystemConfiguration.set_config(
                'content_generation_timeout',
                30000,  # 30 second timeout
                'Timeout for content generation operations',
                'performance'
            )
            
            SystemConfiguration.set_config(
                'default_max_tokens',
                1500,  # Reduce token limit for speed
                'Default maximum tokens for content generation',
                'performance'
            )
            
            optimizations.append({
                'type': 'generation_speed_optimization',
                'action': 'reduced_timeouts_and_tokens',
                'reason': f'Average generation time too high: {self.baseline_metrics["avg_generation_time"]:.0f}ms'
            })
        
        # Optimize for success rate if it's low
        if self.baseline_metrics['success_rate'] < 85:
            # Enable retry logic
            SystemConfiguration.set_config(
                'generation_retry_enabled',
                True,
                'Enable automatic retry for failed generations',
                'reliability'
            )
            
            SystemConfiguration.set_config(
                'generation_max_retries',
                2,
                'Maximum number of retries for failed generations',
                'reliability'
            )
            
            optimizations.append({
                'type': 'reliability_optimization',
                'action': 'enabled_retry_logic',
                'reason': f'Success rate below 85%: {self.baseline_metrics["success_rate"]:.1f}%'
            })
        
        # Optimize feedback collection if feedback is low
        if self.baseline_metrics['feedback_count'] < 5:
            SystemConfiguration.set_config(
                'feedback_collection_enabled',
                True,
                'Enable proactive feedback collection',
                'user_experience'
            )
            
            SystemConfiguration.set_config(
                'feedback_prompt_after_generations',
                2,  # Prompt after every 2 generations
                'Number of generations after which to prompt for feedback',
                'user_experience'
            )
            
            optimizations.append({
                'type': 'feedback_optimization',
                'action': 'increased_feedback_collection',
                'reason': f'Low feedback volume: {self.baseline_metrics["feedback_count"]} in last 7 days'
            })
        
        # Set up performance monitoring if not already configured
        monitoring_config = SystemConfiguration.objects.filter(
            key='performance_monitoring_enabled'
        ).first()
        
        if not monitoring_config or not monitoring_config.value:
            SystemConfiguration.set_config(
                'performance_monitoring_enabled',
                True,
                'Enable comprehensive performance monitoring',
                'monitoring'
            )
            
            SystemConfiguration.set_config(
                'performance_metrics_retention_days',
                30,
                'Number of days to retain performance metrics',
                'monitoring'
            )
            
            optimizations.append({
                'type': 'monitoring_optimization',
                'action': 'enabled_performance_monitoring',
                'reason': 'Performance monitoring was not configured'
            })
        
        print(f"   Applied {len(optimizations)} system configuration optimizations")
        return optimizations
    
    def optimize_resource_usage(self):
        """Optimize system resource usage and efficiency"""
        print("📈 Optimizing resource usage...")
        
        optimizations = []
        
        # Cleanup old analytics data
        old_analytics = ContentAnalytics.objects.filter(
            created_at__lt=timezone.now() - timedelta(days=90)
        )
        
        if old_analytics.count() > 100:
            deleted_count = old_analytics.count()
            old_analytics.delete()
            
            optimizations.append({
                'type': 'data_cleanup',
                'action': 'cleaned_old_analytics',
                'records_removed': deleted_count,
                'reason': 'Remove old analytics data to improve performance'
            })
        
        # Optimize document storage
        orphaned_docs = Document.objects.filter(
            status='deleted',
            created_at__lt=timezone.now() - timedelta(days=30)
        )
        
        if orphaned_docs.count() > 0:
            deleted_count = orphaned_docs.count()
            orphaned_docs.delete()
            
            optimizations.append({
                'type': 'storage_optimization',
                'action': 'removed_orphaned_documents',
                'records_removed': deleted_count,
                'reason': 'Clean up soft-deleted documents older than 30 days'
            })
        
        # Optimize template cache
        unused_templates = ContentTemplate.objects.filter(
            is_active=True,
            usage_count=0,
            created_at__lt=timezone.now() - timedelta(days=7)
        )
        
        if unused_templates.count() > 0:
            for template in unused_templates:
                template.is_active = False
                template.save()
            
            optimizations.append({
                'type': 'template_optimization',
                'action': 'deactivated_unused_templates',
                'templates_deactivated': unused_templates.count(),
                'reason': 'Deactivate templates that have not been used'
            })
        
        # Set up automatic resource monitoring
        SystemConfiguration.set_config(
            'auto_resource_optimization_enabled',
            True,
            'Enable automatic resource optimization',
            'performance'
        )
        
        SystemConfiguration.set_config(
            'resource_optimization_schedule',
            'weekly',  # Run weekly cleanup
            'Schedule for automatic resource optimization',
            'performance'
        )
        
        optimizations.append({
            'type': 'resource_monitoring',
            'action': 'enabled_auto_resource_optimization',
            'reason': 'Set up automated resource management'
        })
        
        print(f"   Applied {len(optimizations)} resource optimizations")
        return optimizations
    
    def record_optimization_metrics(self):
        """Record all optimization metrics and results"""
        print("📊 Recording optimization metrics...")
        
        # Record baseline metrics
        for metric_name, value in self.baseline_metrics.items():
            PlatformMetrics.objects.create(
                metric_name=f"optimization_baseline_{metric_name}",
                metric_value=float(value),
                metric_type='gauge',
                subsystem='optimization',
                labels={
                    'optimization_cycle': timezone.now().isoformat(),
                    'metric_type': 'baseline'
                }
            )
        
        # Record optimization completion
        PlatformMetrics.objects.create(
            metric_name="auto_optimization_cycle_completed",
            metric_value=1.0,
            metric_type='counter',
            subsystem='optimization',
            labels={
                'timestamp': timezone.now().isoformat(),
                'optimizations_applied': len(self.optimizations_applied),
                'baseline_success_rate': self.baseline_metrics.get('success_rate', 0),
                'baseline_avg_time': self.baseline_metrics.get('avg_generation_time', 0)
            }
        )
        
        # Record individual optimization actions
        for optimization in self.optimizations_applied:
            PlatformMetrics.objects.create(
                metric_name=f"optimization_action_{optimization}",
                metric_value=1.0,
                metric_type='counter',
                subsystem='optimization',
                labels={
                    'timestamp': timezone.now().isoformat(),
                    'action_type': optimization
                }
            )
        
        print(f"   Recorded optimization metrics for {len(self.optimizations_applied)} actions")
    
    def get_optimization_history(self, days=30):
        """Get history of optimization actions"""
        return PlatformMetrics.objects.filter(
            metric_name__startswith='optimization_',
            created_at__gte=timezone.now() - timedelta(days=days)
        ).order_by('-created_at')
    
    def get_performance_trend(self, days=7):
        """Get performance trend over time"""
        metrics = PlatformMetrics.objects.filter(
            metric_name__in=[
                'optimization_baseline_success_rate',
                'optimization_baseline_avg_generation_time',
                'optimization_baseline_avg_user_rating'
            ],
            created_at__gte=timezone.now() - timedelta(days=days)
        ).order_by('created_at')
        
        trends = defaultdict(list)
        for metric in metrics:
            trends[metric.metric_name].append({
                'timestamp': metric.created_at.isoformat(),
                'value': metric.metric_value
            })
        
        return dict(trends)


if __name__ == "__main__":
    optimizer = AutoOptimizer()
    results = optimizer.run_optimization_cycle()
    
    print("\n" + "="*50)
    print("🚀 AUTO-OPTIMIZATION SUMMARY")
    print("="*50)
    print(f"🎯 Performance issues identified: {results['performance_issues']}")
    print(f"📝 Template optimizations: {results['template_optimizations']}")  
    print(f"⚙️ System config optimizations: {results['config_optimizations']}")
    print(f"📈 Resource optimizations: {results['resource_optimizations']}")
    print(f"🔧 Total optimizations applied: {results['total_optimizations']}")
    
    print(f"\n📊 BASELINE METRICS:")
    for metric, value in results['baseline_metrics'].items():
        if isinstance(value, float):
            print(f"   • {metric}: {value:.2f}")
        else:
            print(f"   • {metric}: {value}")