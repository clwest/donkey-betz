"""
Real-time monitoring system with 15% increment updates
Monitors API calls, embeddings, errors, and learning progress
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import psycopg2
from django.core.cache import cache
from django.db.models import Count, Avg, Q
from content.models import ContentGeneration

logger = logging.getLogger(__name__)


class RealTimeMonitor:
    """Monitor system metrics with threshold-based alerts"""
    
    THRESHOLDS = [0.15, 0.30, 0.45, 0.60, 0.75, 0.90, 1.00]
    
    def __init__(self):
        self.metrics = {
            'api_calls': 0,
            'embeddings_generated': 0,
            'conversations_saved': 0,
            'errors': 0,
            'response_time_ms': 0,
            'cache_hit_rate': 0,
            'learning_rate': 0
        }
        self.start_time = datetime.now()
        
    def update_metric(self, metric_name: str, value: float) -> Dict[str, Any]:
        """
        Update a metric and check thresholds
        
        Returns alert if threshold crossed
        """
        old_value = self.metrics.get(metric_name, 0)
        self.metrics[metric_name] = value
        
        # Check which thresholds were crossed
        alerts = []
        for threshold in self.THRESHOLDS:
            if old_value < threshold <= value or old_value > threshold >= value:
                percentage = int(threshold * 100)
                alerts.append({
                    'metric': metric_name,
                    'threshold': percentage,
                    'value': value,
                    'timestamp': datetime.now().isoformat(),
                    'direction': 'up' if value > old_value else 'down'
                })
                logger.info(f"Threshold {percentage}% crossed for {metric_name}: {value}")
        
        # Cache the metric for quick access
        cache.set(f'metric_{metric_name}', value, timeout=300)
        
        return {'alerts': alerts, 'current_value': value}
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time statistics from all sources"""
        stats = {}
        
        try:
            # 1. API Call metrics from ContentGeneration
            last_hour = datetime.now() - timedelta(hours=1)
            api_calls = ContentGeneration.objects.filter(
                created_at__gte=last_hour
            ).count()
            
            avg_response_time = ContentGeneration.objects.filter(
                created_at__gte=last_hour
            ).aggregate(
                avg_time=Avg('generation_time_ms')
            )['avg_time'] or 0
            
            stats['api_calls_per_hour'] = api_calls
            stats['avg_response_time_ms'] = round(avg_response_time)
            
            # 2. Embedding metrics from ai_unified_platform
            conn = psycopg2.connect(
                host='localhost',
                database='ai_unified_platform',
                user='ai_unified_user',
                password='ai_unified_pass_2025'
            )
            cursor = conn.cursor()
            
            # Embeddings created today
            cursor.execute("""
                SELECT COUNT(*) FROM unified_embeddings 
                WHERE created_at >= CURRENT_DATE
            """)
            today_embeddings = cursor.fetchone()[0]
            
            # Conversations saved today
            cursor.execute("""
                SELECT COUNT(*) FROM unified_embeddings 
                WHERE content_type = 'conversation'
                AND created_at >= CURRENT_DATE
                AND metadata->>'learned' = 'true'
            """)
            today_conversations = cursor.fetchone()[0]
            
            # Total knowledge base size
            cursor.execute("SELECT COUNT(*) FROM unified_embeddings WHERE embedding IS NOT NULL")
            total_knowledge = cursor.fetchone()[0]
            
            conn.close()
            
            stats['embeddings_today'] = today_embeddings
            stats['conversations_today'] = today_conversations
            stats['total_knowledge_base'] = total_knowledge
            stats['learning_rate'] = today_conversations  # New learnings today
            
            # 3. Calculate percentages for monitoring
            daily_target = 100  # Target conversations per day
            stats['learning_progress'] = min(100, (today_conversations / daily_target) * 100)
            
            # Update metrics with thresholds
            self.update_metric('learning_progress', stats['learning_progress'] / 100)
            self.update_metric('api_calls', api_calls)
            self.update_metric('response_time_ms', avg_response_time)
            
        except Exception as e:
            logger.error(f"Failed to get real-time stats: {e}")
            stats['error'] = str(e)
        
        stats['timestamp'] = datetime.now().isoformat()
        stats['monitoring_active'] = True
        return stats
    
    def get_threshold_status(self) -> Dict[str, Any]:
        """Get current threshold status for all metrics"""
        status = {}
        for metric_name, value in self.metrics.items():
            # Find which threshold we're at
            current_threshold = 0
            for threshold in self.THRESHOLDS:
                if value >= threshold:
                    current_threshold = int(threshold * 100)
            
            status[metric_name] = {
                'value': value,
                'percentage': current_threshold,
                'next_threshold': self._get_next_threshold(value)
            }
        
        return status
    
    def _get_next_threshold(self, value: float) -> int:
        """Get the next threshold percentage"""
        for threshold in self.THRESHOLDS:
            if value < threshold:
                return int(threshold * 100)
        return 100


# Global monitor instance
monitor = RealTimeMonitor()