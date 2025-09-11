#!/usr/bin/env python3
"""
Learning Loop Engine - Makes the platform actually learn and optimize

This engine analyzes feedback, identifies patterns, generates optimizations,
and continuously improves the system based on real usage data.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from collections import defaultdict
import json
import statistics
from typing import Dict, List, Any, Optional

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q
from django.utils import timezone

from core.models import SystemConfiguration, PlatformMetrics
from content.models import (
    ContentGeneration, ContentTemplate, Feedback, 
    ContentAnalytics, Document, KnowledgeBase
)

User = get_user_model()


class LearningLoopEngine:
    """
    Core learning engine that analyzes platform usage and generates insights
    """
    
    def __init__(self):
        self.insights = []
        self.optimizations = []
        self.patterns = {}
        
    def run_full_learning_cycle(self):
        """Execute complete learning cycle"""
        print("🧠 Starting Learning Cycle...")
        
        # Step 1: Analyze feedback patterns
        feedback_insights = self.analyze_feedback_patterns()
        
        # Step 2: Analyze content performance
        content_insights = self.analyze_content_performance()
        
        # Step 3: Identify optimization opportunities
        optimization_insights = self.identify_optimizations()
        
        # Step 4: Generate recommendations
        recommendations = self.generate_recommendations()
        
        # Step 5: Store learning insights
        self.store_learning_insights(feedback_insights, content_insights, optimization_insights)
        
        # Step 6: Apply automatic optimizations
        applied_optimizations = self.apply_optimizations(recommendations)
        
        print(f"✅ Learning cycle complete: {len(applied_optimizations)} optimizations applied")
        
        return {
            'feedback_insights': len(feedback_insights),
            'content_insights': len(content_insights),
            'optimizations_applied': len(applied_optimizations),
            'recommendations': recommendations
        }
    
    def analyze_feedback_patterns(self):
        """Analyze user feedback to identify patterns"""
        print("🔍 Analyzing feedback patterns...")
        
        insights = []
        
        # Get all feedback from last 30 days
        recent_feedback = Feedback.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        )
        
        if not recent_feedback.exists():
            print("   No recent feedback found")
            return insights
        
        # Overall satisfaction trends
        avg_rating = recent_feedback.aggregate(avg_rating=Avg('overall_rating'))['avg_rating']
        total_feedback = recent_feedback.count()
        positive_feedback = recent_feedback.filter(overall_rating__gte=4).count()
        negative_feedback = recent_feedback.filter(overall_rating__lte=2).count()
        
        satisfaction_rate = (positive_feedback / total_feedback * 100) if total_feedback > 0 else 0
        
        insights.append({
            'type': 'satisfaction_trend',
            'avg_rating': round(avg_rating, 2) if avg_rating else 0,
            'satisfaction_rate': round(satisfaction_rate, 1),
            'total_feedback': total_feedback,
            'positive': positive_feedback,
            'negative': negative_feedback
        })
        
        # Content type performance
        content_type_feedback = {}
        for feedback in recent_feedback:
            content_type = feedback.content_type
            if content_type not in content_type_feedback:
                content_type_feedback[content_type] = []
            content_type_feedback[content_type].append(feedback.overall_rating)
        
        for content_type, ratings in content_type_feedback.items():
            avg_rating = statistics.mean(ratings)
            insights.append({
                'type': 'content_type_performance',
                'content_type': content_type,
                'avg_rating': round(avg_rating, 2),
                'feedback_count': len(ratings),
                'performance': 'excellent' if avg_rating >= 4.5 else 'good' if avg_rating >= 3.5 else 'needs_improvement'
            })
        
        # Common complaint analysis
        complaint_keywords = defaultdict(int)
        suggestions = []
        
        for feedback in recent_feedback.filter(overall_rating__lte=3):
            if feedback.comments:
                # Simple keyword extraction for complaints
                words = feedback.comments.lower().split()
                complaint_words = ['slow', 'error', 'bad', 'wrong', 'failed', 'broken', 'poor', 'terrible']
                for word in words:
                    if word in complaint_words:
                        complaint_keywords[word] += 1
            
            if feedback.suggestions:
                suggestions.append(feedback.suggestions)
        
        if complaint_keywords:
            insights.append({
                'type': 'common_complaints',
                'keywords': dict(complaint_keywords),
                'top_complaint': max(complaint_keywords.items(), key=lambda x: x[1])[0]
            })
        
        print(f"   Generated {len(insights)} feedback insights")
        return insights
    
    def analyze_content_performance(self):
        """Analyze content generation performance metrics"""
        print("📊 Analyzing content performance...")
        
        insights = []
        
        # Recent content generations
        recent_generations = ContentGeneration.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        )
        
        if not recent_generations.exists():
            print("   No recent content generations found")
            return insights
        
        # Success rate analysis
        total_generations = recent_generations.count()
        successful_generations = recent_generations.filter(status='completed').count()
        failed_generations = recent_generations.filter(status='failed').count()
        
        success_rate = (successful_generations / total_generations * 100) if total_generations > 0 else 0
        
        insights.append({
            'type': 'generation_success_rate',
            'success_rate': round(success_rate, 1),
            'total_generations': total_generations,
            'successful': successful_generations,
            'failed': failed_generations
        })
        
        # Template performance
        template_performance = {}
        for generation in recent_generations:
            if generation.template:
                template_name = generation.template.name
                if template_name not in template_performance:
                    template_performance[template_name] = {'total': 0, 'successful': 0, 'avg_time': []}
                
                template_performance[template_name]['total'] += 1
                if generation.status == 'completed':
                    template_performance[template_name]['successful'] += 1
                
                if generation.generation_time_ms:
                    template_performance[template_name]['avg_time'].append(generation.generation_time_ms)
        
        for template_name, stats in template_performance.items():
            success_rate = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
            avg_time = statistics.mean(stats['avg_time']) if stats['avg_time'] else 0
            
            insights.append({
                'type': 'template_performance',
                'template': template_name,
                'success_rate': round(success_rate, 1),
                'avg_generation_time_ms': round(avg_time, 0),
                'total_uses': stats['total'],
                'performance_rating': 'excellent' if success_rate >= 95 else 'good' if success_rate >= 80 else 'needs_optimization'
            })
        
        # Performance trends
        daily_stats = defaultdict(lambda: {'count': 0, 'success': 0})
        for generation in recent_generations:
            day = generation.created_at.date()
            daily_stats[day]['count'] += 1
            if generation.status == 'completed':
                daily_stats[day]['success'] += 1
        
        trend_data = []
        for day, stats in sorted(daily_stats.items()):
            success_rate = (stats['success'] / stats['count'] * 100) if stats['count'] > 0 else 0
            trend_data.append({
                'date': day.isoformat(),
                'generations': stats['count'],
                'success_rate': round(success_rate, 1)
            })
        
        insights.append({
            'type': 'performance_trend',
            'daily_data': trend_data[-7:]  # Last 7 days
        })
        
        print(f"   Generated {len(insights)} performance insights")
        return insights
    
    def identify_optimizations(self):
        """Identify specific optimization opportunities"""
        print("🎯 Identifying optimization opportunities...")
        
        optimizations = []
        
        # Slow generation optimization
        slow_generations = ContentGeneration.objects.filter(
            generation_time_ms__gt=30000,  # > 30 seconds
            created_at__gte=timezone.now() - timedelta(days=30)
        )
        
        if slow_generations.exists():
            avg_slow_time = slow_generations.aggregate(
                avg_time=Avg('generation_time_ms')
            )['avg_time']
            
            optimizations.append({
                'type': 'performance_optimization',
                'issue': 'slow_generation',
                'description': f'Found {slow_generations.count()} slow generations (avg: {int(avg_slow_time)}ms)',
                'recommendation': 'Optimize prompts, reduce context size, or implement caching',
                'priority': 'high' if slow_generations.count() > 10 else 'medium'
            })
        
        # Failed generation optimization
        failed_generations = ContentGeneration.objects.filter(
            status='failed',
            created_at__gte=timezone.now() - timedelta(days=30)
        )
        
        if failed_generations.exists():
            optimizations.append({
                'type': 'reliability_optimization',
                'issue': 'generation_failures',
                'description': f'Found {failed_generations.count()} failed generations',
                'recommendation': 'Implement retry logic, improve error handling, validate prompts',
                'priority': 'high'
            })
        
        # Template optimization
        templates = ContentTemplate.objects.all()
        for template in templates:
            recent_uses = ContentGeneration.objects.filter(
                template=template,
                created_at__gte=timezone.now() - timedelta(days=30)
            )
            
            if recent_uses.count() >= 5:  # Only analyze templates with sufficient data
                success_rate = recent_uses.filter(status='completed').count() / recent_uses.count()
                
                if success_rate < 0.8:  # Less than 80% success
                    optimizations.append({
                        'type': 'template_optimization',
                        'issue': 'low_template_success_rate',
                        'template': template.name,
                        'success_rate': round(success_rate * 100, 1),
                        'description': f'Template "{template.name}" has {success_rate*100:.1f}% success rate',
                        'recommendation': 'Review and optimize template prompts',
                        'priority': 'medium'
                    })
        
        # User experience optimization
        feedback_with_low_ratings = Feedback.objects.filter(
            overall_rating__lte=2,
            created_at__gte=timezone.now() - timedelta(days=30)
        )
        
        if feedback_with_low_ratings.count() > 5:
            optimizations.append({
                'type': 'user_experience_optimization',
                'issue': 'low_user_satisfaction',
                'description': f'Found {feedback_with_low_ratings.count()} low ratings (≤2 stars)',
                'recommendation': 'Analyze feedback comments, improve content quality, add user guidance',
                'priority': 'high'
            })
        
        print(f"   Identified {len(optimizations)} optimization opportunities")
        return optimizations
    
    def generate_recommendations(self):
        """Generate actionable recommendations based on analysis"""
        print("💡 Generating recommendations...")
        
        recommendations = []
        
        # Analyze system configuration for recommendations
        configs = SystemConfiguration.objects.all()
        
        # Check if we have performance monitoring configured
        has_monitoring = configs.filter(key__icontains='monitoring').exists()
        if not has_monitoring:
            recommendations.append({
                'category': 'monitoring',
                'title': 'Enable Performance Monitoring',
                'description': 'Set up comprehensive performance monitoring to track system health',
                'action': 'configure_monitoring',
                'priority': 'medium'
            })
        
        # Check content generation limits
        has_rate_limits = configs.filter(key__icontains='rate_limit').exists()
        if not has_rate_limits:
            recommendations.append({
                'category': 'performance',
                'title': 'Implement Rate Limiting',
                'description': 'Add rate limiting to prevent system overload during peak usage',
                'action': 'setup_rate_limits',
                'priority': 'medium'
            })
        
        # User feedback improvements
        recent_feedback_count = Feedback.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        if recent_feedback_count < 10:
            recommendations.append({
                'category': 'user_engagement',
                'title': 'Increase Feedback Collection',
                'description': 'Low feedback volume detected. Implement more feedback prompts',
                'action': 'enhance_feedback_collection',
                'priority': 'low'
            })
        
        # Template optimization recommendations
        templates_count = ContentTemplate.objects.count()
        if templates_count < 5:
            recommendations.append({
                'category': 'content_quality',
                'title': 'Expand Template Library',
                'description': 'Add more specialized templates to improve content generation quality',
                'action': 'create_more_templates',
                'priority': 'medium'
            })
        
        print(f"   Generated {len(recommendations)} recommendations")
        return recommendations
    
    def store_learning_insights(self, feedback_insights, content_insights, optimization_insights):
        """Store learning insights in the database"""
        print("💾 Storing learning insights...")
        
        # Store feedback insights as platform metrics
        for insight in feedback_insights:
            PlatformMetrics.objects.create(
                metric_name=f"learning_feedback_{insight['type']}",
                metric_value=insight.get('avg_rating', insight.get('satisfaction_rate', 1.0)),
                metric_type='gauge',
                subsystem='learning',
                labels=insight
            )
        
        # Store content performance insights
        for insight in content_insights:
            metric_value = insight.get('success_rate', insight.get('avg_generation_time_ms', 0))
            PlatformMetrics.objects.create(
                metric_name=f"learning_content_{insight['type']}",
                metric_value=metric_value,
                metric_type='gauge',
                subsystem='learning',
                labels=insight
            )
        
        # Store optimization insights
        for optimization in optimization_insights:
            PlatformMetrics.objects.create(
                metric_name=f"learning_optimization_{optimization['type']}",
                metric_value=1.0,  # Binary metric indicating optimization identified
                metric_type='counter',
                subsystem='learning',
                labels=optimization
            )
        
        # Store overall learning cycle completion
        PlatformMetrics.objects.create(
            metric_name="learning_cycle_completed",
            metric_value=1.0,
            metric_type='counter',
            subsystem='learning',
            labels={
                'timestamp': timezone.now().isoformat(),
                'insights_generated': len(feedback_insights) + len(content_insights),
                'optimizations_identified': len(optimization_insights)
            }
        )
        
        print(f"   Stored {len(feedback_insights + content_insights + optimization_insights)} insights")
    
    def apply_optimizations(self, recommendations):
        """Apply automatic optimizations that are safe to implement"""
        print("🔧 Applying safe optimizations...")
        
        applied = []
        
        for rec in recommendations:
            if rec['action'] == 'configure_monitoring':
                # Enable basic monitoring
                SystemConfiguration.set_config(
                    'monitoring_enabled',
                    True,
                    'Enable system performance monitoring',
                    'performance'
                )
                applied.append('monitoring_enabled')
            
            elif rec['action'] == 'setup_rate_limits':
                # Set conservative rate limits
                SystemConfiguration.set_config(
                    'content_generation_rate_limit',
                    {'requests_per_hour': 100, 'requests_per_minute': 10},
                    'Rate limits for content generation',
                    'performance'
                )
                applied.append('rate_limits_configured')
            
            elif rec['action'] == 'enhance_feedback_collection':
                # Enable feedback prompts
                SystemConfiguration.set_config(
                    'feedback_prompt_frequency',
                    {'show_after_generations': 3, 'show_probability': 0.3},
                    'Settings for feedback collection prompts',
                    'user_experience'
                )
                applied.append('feedback_enhancement')
        
        # Record optimization metrics
        for optimization in applied:
            PlatformMetrics.objects.create(
                metric_name=f"optimization_applied_{optimization}",
                metric_value=1.0,
                metric_type='counter',
                subsystem='optimization',
                labels={
                    'timestamp': timezone.now().isoformat(),
                    'auto_applied': True
                }
            )
        
        print(f"   Applied {len(applied)} optimizations")
        return applied
    
    def get_learning_summary(self):
        """Get summary of recent learning activities"""
        recent_metrics = PlatformMetrics.objects.filter(
            metric_name__startswith='learning_',
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')
        
        return {
            'recent_learning_activities': recent_metrics.count(),
            'last_learning_cycle': recent_metrics.filter(
                metric_name='learning_cycle_completed'
            ).first(),
            'optimization_count': PlatformMetrics.objects.filter(
                metric_name__startswith='optimization_applied_',
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count()
        }


if __name__ == "__main__":
    engine = LearningLoopEngine()
    results = engine.run_full_learning_cycle()
    
    print("\n" + "="*50)
    print("🎓 LEARNING CYCLE SUMMARY")
    print("="*50)
    print(f"📊 Feedback insights generated: {results['feedback_insights']}")
    print(f"📈 Content insights generated: {results['content_insights']}")
    print(f"🔧 Optimizations applied: {results['optimizations_applied']}")
    print(f"💡 Recommendations generated: {len(results['recommendations'])}")
    
    if results['recommendations']:
        print(f"\n🎯 TOP RECOMMENDATIONS:")
        for rec in results['recommendations'][:3]:
            print(f"   • {rec['title']}: {rec['description']}")