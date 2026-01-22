"""
Agent Execution Tracker - Real-Time Metrics Collection
Created: 9/26/25 11:46 AM MST
"""

import redis
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from django.conf import settings
import pytz

logger = logging.getLogger(__name__)

class AgentExecutionTracker:
    """
    Tracks all agent executions and metrics in Redis for real-time dashboard updates
    """

    def __init__(self):
        import os
        redis_url = os.environ.get('REDIS_URL', getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0'))
        self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
        self.mst = pytz.timezone('America/Denver')

    def track_agent_execution(self, agent_name: str, execution_data: Dict[str, Any]) -> None:
        """
        Track an agent execution with all metrics
        """
        try:
            timestamp = datetime.now(self.mst).isoformat()

            # Update agent-specific stats
            agent_key = f"agent:{agent_name}:stats"

            # Increment execution counters
            is_real = execution_data.get('is_real_execution', False)
            if is_real:
                self.redis_client.hincrby(agent_key, 'real_executions', 1)
            else:
                self.redis_client.hincrby(agent_key, 'demo_executions', 1)

            # Track code generation
            if execution_data.get('code_generated'):
                lines = execution_data.get('lines_of_code', 0)
                self.redis_client.hincrby(agent_key, 'code_generated', 1)
                self.redis_client.hincrby(agent_key, 'total_lines', lines)

                # Daily stats
                today_key = f"stats:code_generated:today"
                self.redis_client.hincrby(today_key, 'count', 1)
                self.redis_client.hincrby(today_key, 'lines', lines)
                self.redis_client.expire(today_key, 86400)  # Expire after 24 hours

            # Track quality metrics
            if 'quality_score' in execution_data:
                self.redis_client.hset(agent_key, 'last_quality_score', execution_data['quality_score'])

            if 'complexity_score' in execution_data:
                self.redis_client.hset(agent_key, 'last_complexity_score', execution_data['complexity_score'])

            # Track success/failure
            if execution_data.get('success', False):
                self.redis_client.hincrby(agent_key, 'successful_executions', 1)
            else:
                self.redis_client.hincrby(agent_key, 'failed_executions', 1)

            # Store last task info
            self.redis_client.hset(agent_key, 'last_execution', timestamp)
            if execution_data.get('task_description'):
                self.redis_client.hset(agent_key, 'last_task', execution_data['task_description'])

            # Update global metrics
            self._update_global_metrics(execution_data)

            # Add to recent executions list (for activity feed)
            self._track_recent_execution(agent_name, execution_data, timestamp)

            # Publish to WebSocket for real-time updates
            self._publish_metrics_update()

            logger.info(f"✅ Tracked execution for {agent_name}: {execution_data.get('task_description', 'Unknown task')}")

        except Exception as e:
            logger.error(f"Error tracking agent execution: {e}")

    def track_file_creation(self, file_data: Dict[str, Any]) -> None:
        """
        Track when an agent creates a file
        """
        try:
            # Increment file counter
            self.redis_client.incr('stats:files:total')

            # Daily file count
            today_key = "stats:files:today"
            self.redis_client.incr(today_key)
            self.redis_client.expire(today_key, 86400)

            # Track by agent if specified
            if file_data.get('agent_name'):
                agent_key = f"agent:{file_data['agent_name']}:stats"
                self.redis_client.hincrby(agent_key, 'files_created', 1)

            # Add to recent files list
            recent_file = {
                'path': file_data.get('path', 'unknown'),
                'agent': file_data.get('agent_name', 'system'),
                'timestamp': datetime.now(self.mst).isoformat(),
                'size': file_data.get('size', 0)
            }

            self.redis_client.lpush('recent:files', json.dumps(recent_file))
            self.redis_client.ltrim('recent:files', 0, 99)  # Keep last 100 files

            # Publish update
            self._publish_metrics_update()

        except Exception as e:
            logger.error(f"Error tracking file creation: {e}")

    def get_active_agent_count(self) -> int:
        """
        Get count of agents that have executed in the last hour
        """
        try:
            active_count = 0
            one_hour_ago = datetime.now(self.mst) - timedelta(hours=1)

            # Check all agent keys
            for key in self.redis_client.keys('agent:*:stats'):
                last_exec = self.redis_client.hget(key, 'last_execution')
                if last_exec:
                    exec_time = datetime.fromisoformat(last_exec)
                    if exec_time.replace(tzinfo=self.mst) > one_hour_ago:
                        active_count += 1

            return active_count

        except Exception as e:
            logger.error(f"Error getting active agent count: {e}")
            return 0

    def calculate_success_rate(self) -> float:
        """
        Calculate overall success rate across all agents
        """
        try:
            total_success = 0
            total_failed = 0

            for key in self.redis_client.keys('agent:*:stats'):
                stats = self.redis_client.hgetall(key)
                total_success += int(stats.get('successful_executions', 0))
                total_failed += int(stats.get('failed_executions', 0))

            total = total_success + total_failed
            if total > 0:
                return round((total_success / total) * 100, 1)
            return 0.0

        except Exception as e:
            logger.error(f"Error calculating success rate: {e}")
            return 0.0

    def calculate_learning_rate(self) -> float:
        """
        Calculate learning rate based on quality improvements
        """
        try:
            # Get quality scores from recent executions
            quality_scores = []

            for key in self.redis_client.keys('agent:*:stats'):
                score = self.redis_client.hget(key, 'last_quality_score')
                if score:
                    quality_scores.append(float(score))

            if quality_scores:
                # Learning rate = average quality score (simplified for now)
                return round(sum(quality_scores) / len(quality_scores), 1)

            return 0.0

        except Exception as e:
            logger.error(f"Error calculating learning rate: {e}")
            return 0.0

    def get_total_files_created(self) -> int:
        """
        Get total number of files created
        """
        try:
            return int(self.redis_client.get('stats:files:total') or 0)
        except Exception as e:
            logger.error(f"Error getting total files: {e}")
            return 0

    def get_projects_completed(self) -> int:
        """
        Get number of completed projects
        """
        try:
            # Count successful executions that were projects
            count = 0
            for key in self.redis_client.keys('agent:*:stats'):
                stats = self.redis_client.hgetall(key)
                # Count agents with successful executions as "projects" for now
                if int(stats.get('successful_executions', 0)) > 0:
                    count += 1
            return count
        except Exception as e:
            logger.error(f"Error getting projects completed: {e}")
            return 0

    def _update_global_metrics(self, execution_data: Dict[str, Any]) -> None:
        """
        Update global platform metrics
        """
        try:
            # Track total executions
            self.redis_client.incr('stats:total_executions')

            # Track by type
            if execution_data.get('is_real_execution'):
                self.redis_client.incr('stats:real_executions')
            else:
                self.redis_client.incr('stats:demo_executions')

            # Update active sessions count
            self.redis_client.sadd('active_learning_sessions', execution_data.get('session_id', 'default'))

        except Exception as e:
            logger.error(f"Error updating global metrics: {e}")

    def _track_recent_execution(self, agent_name: str, execution_data: Dict[str, Any], timestamp: str) -> None:
        """
        Track recent execution for activity feed
        """
        try:
            activity = {
                'agent': agent_name,
                'task': execution_data.get('task_description', 'Task execution'),
                'success': execution_data.get('success', False),
                'timestamp': timestamp,
                'type': 'execution'
            }

            self.redis_client.lpush('recent:activities', json.dumps(activity))
            self.redis_client.ltrim('recent:activities', 0, 49)  # Keep last 50 activities

        except Exception as e:
            logger.error(f"Error tracking recent execution: {e}")

    def _publish_metrics_update(self) -> None:
        """
        Publish metrics update to WebSocket channel
        """
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()

            # Get current metrics
            metrics = {
                'type': 'stats_update',
                'stats': {
                    'active_agents': self.get_active_agent_count(),
                    'files_created': self.get_total_files_created(),
                    'success_rate': self.calculate_success_rate(),
                    'learning_rate': self.calculate_learning_rate(),
                    'projects_completed': self.get_projects_completed()
                }
            }

            # Send to WebSocket group
            async_to_sync(channel_layer.group_send)(
                'build_activity',
                {
                    'type': 'send_stats_update',
                    'data': metrics
                }
            )

        except Exception as e:
            logger.debug(f"Could not publish WebSocket update: {e}")

    def get_agent_performance_details(self) -> List[Dict[str, Any]]:
        """
        Get detailed performance stats for each agent
        """
        try:
            agent_details = []

            for key in self.redis_client.keys('agent:*:stats'):
                agent_name = key.split(':')[1] if ':' in key else 'unknown'
                stats = self.redis_client.hgetall(key)

                # Calculate performance metrics
                successful = int(stats.get('successful_executions', 0))
                failed = int(stats.get('failed_executions', 0))
                total = successful + failed

                if total > 0:
                    success_rate = round((successful / total) * 100, 1)

                    agent_detail = {
                        'name': agent_name,
                        'total_executions': total,
                        'successful': successful,
                        'failed': failed,
                        'success_rate': success_rate,
                        'quality_score': float(stats.get('last_quality_score', 0)),
                        'last_task': stats.get('last_task', 'No recent task'),
                        'last_execution': stats.get('last_execution', ''),
                        'code_generated': int(stats.get('code_generated', 0)),
                        'lines_of_code': int(stats.get('total_lines', 0))
                    }

                    agent_details.append(agent_detail)

            # Sort by total executions (most active first)
            agent_details.sort(key=lambda x: x['total_executions'], reverse=True)

            return agent_details

        except Exception as e:
            logger.error(f"Error getting agent performance details: {e}")
            return []

    def track_spider_activity(self, spider_name: str, activity_data: Dict[str, Any]) -> None:
        """
        Track spider activity for real-time metrics
        """
        try:
            timestamp = datetime.now(self.mst).isoformat()

            # Update spider-specific stats
            spider_key = f"spider:{spider_name}:stats"

            # Track activity
            self.redis_client.hincrby(spider_key, 'total_activities', 1)
            self.redis_client.hset(spider_key, 'last_activity', timestamp)

            # Track data collection
            if activity_data.get('data_collected'):
                self.redis_client.hincrby(spider_key, 'data_points_collected', activity_data.get('data_points', 1))

            # Track success/failure
            if activity_data.get('success', False):
                self.redis_client.hincrby(spider_key, 'successful_activities', 1)
            else:
                self.redis_client.hincrby(spider_key, 'failed_activities', 1)

            # Update hourly task count
            hour_key = f"spider:tasks:hour:{datetime.now(self.mst).strftime('%Y%m%d%H')}"
            self.redis_client.incr(hour_key)
            self.redis_client.expire(hour_key, 3600)  # Expire after 1 hour

            # Add to recent spider activities
            activity = {
                'spider': spider_name,
                'task': activity_data.get('task_description', 'Data collection'),
                'success': activity_data.get('success', False),
                'timestamp': timestamp,
                'type': 'spider_activity'
            }

            self.redis_client.lpush('recent:spider_activities', json.dumps(activity))
            self.redis_client.ltrim('recent:spider_activities', 0, 49)  # Keep last 50

            logger.info(f"✅ Tracked spider activity for {spider_name}")

        except Exception as e:
            logger.error(f"Error tracking spider activity: {e}")

    def get_active_spider_count(self) -> int:
        """
        Get REAL count of active spiders from Redis
        """
        try:
            # First, check the active_spiders set for REAL deployed spiders
            active_spiders = self.redis_client.scard('active_spiders')
            if active_spiders > 0:
                logger.info(f"Found {active_spiders} REAL spiders in Redis!")
                return active_spiders

            # Fallback to checking recent activity (for compatibility)
            active_count = 0
            one_hour_ago = datetime.now(self.mst) - timedelta(hours=1)

            # Check all spider keys
            for key in self.redis_client.keys('spider:*:stats'):
                last_activity = self.redis_client.hget(key, 'last_activity')
                if last_activity:
                    activity_time = datetime.fromisoformat(last_activity)
                    if activity_time.replace(tzinfo=self.mst) > one_hour_ago:
                        active_count += 1

            return active_count

        except Exception as e:
            logger.error(f"Error getting active spider count: {e}")
            return 0

    def get_spider_tasks_per_hour(self) -> int:
        """
        Get spider tasks completed in the current hour
        """
        try:
            current_hour_key = f"spider:tasks:hour:{datetime.now(self.mst).strftime('%Y%m%d%H')}"
            return int(self.redis_client.get(current_hour_key) or 0)
        except Exception as e:
            logger.error(f"Error getting spider tasks per hour: {e}")
            return 0

    def get_spider_network_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive spider network statistics
        """
        try:
            # Get total spider files from filesystem (real count)
            from ai_core.spiders.consciousness import ConsciousnessBridge
            consciousness = ConsciousnessBridge()
            understanding = consciousness.understand_self()
            total_spiders = understanding['capabilities'].get('by_type', {}).get('spider', 0)

            # Get active spiders
            active_spiders = self.get_active_spider_count()

            # Get tasks per hour
            tasks_per_hour = self.get_spider_tasks_per_hour()

            # Get recent spider activities
            recent_activities = []
            try:
                for activity_json in self.redis_client.lrange('recent:spider_activities', 0, 9):
                    recent_activities.append(json.loads(activity_json))
            except:
                pass

            return {
                'total_spiders': total_spiders,
                'active_spiders': active_spiders,
                'tasks_per_hour': tasks_per_hour,
                'recent_activities': recent_activities,
                'network_status': 'active' if active_spiders > 0 else 'dormant'
            }

        except Exception as e:
            logger.error(f"Error getting spider network stats: {e}")
            return {
                'total_spiders': 0,
                'active_spiders': 0,
                'tasks_per_hour': 0,
                'recent_activities': [],
                'network_status': 'offline'
            }

    def track_learning_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Track learning-related events for analytics
        """
        try:
            timestamp = datetime.now(self.mst).isoformat()

            # Track different learning events
            if event_type == 'feedback_processed':
                self.redis_client.incr('learning:feedback_processed:total')
                # Daily count
                daily_key = f"learning:feedback_processed:day:{datetime.now(self.mst).strftime('%Y%m%d')}"
                self.redis_client.incr(daily_key)
                self.redis_client.expire(daily_key, 86400)

            elif event_type == 'insight_generated':
                self.redis_client.incr('learning:insights_generated:total')
                insight_data = {
                    'timestamp': timestamp,
                    'insight': event_data.get('insight', ''),
                    'confidence': event_data.get('confidence', 0)
                }
                self.redis_client.lpush('learning:recent_insights', json.dumps(insight_data))
                self.redis_client.ltrim('learning:recent_insights', 0, 19)  # Keep last 20

            elif event_type == 'optimization_applied':
                self.redis_client.incr('learning:optimizations_applied:total')
                optimization_data = {
                    'timestamp': timestamp,
                    'type': event_data.get('optimization_type', ''),
                    'improvement': event_data.get('improvement_score', 0)
                }
                self.redis_client.lpush('learning:recent_optimizations', json.dumps(optimization_data))
                self.redis_client.ltrim('learning:recent_optimizations', 0, 19)

            # Update learning activity status
            self.redis_client.setex('learning:activity_status', 300, 'active')  # 5 min expiry

            logger.info(f"✅ Tracked learning event: {event_type}")

        except Exception as e:
            logger.error(f"Error tracking learning event: {e}")

    def calculate_learning_improvement_rate(self) -> float:
        """
        Calculate learning improvement rate based on quality score trends
        """
        try:
            quality_scores = []
            improvement_rate = 0.0

            # Get quality scores from recent executions
            for key in self.redis_client.keys('agent:*:stats'):
                score = self.redis_client.hget(key, 'last_quality_score')
                if score:
                    quality_scores.append(float(score))

            if len(quality_scores) >= 2:
                # Simple improvement calculation
                recent_avg = sum(quality_scores[-5:]) / min(5, len(quality_scores))
                older_avg = sum(quality_scores[:-5]) / max(1, len(quality_scores) - 5) if len(quality_scores) > 5 else recent_avg
                improvement_rate = max(0, ((recent_avg - older_avg) / max(older_avg, 1)) * 100)

            return round(improvement_rate, 1)

        except Exception as e:
            logger.error(f"Error calculating learning improvement rate: {e}")
            return 0.0

    def get_learning_analytics_data(self) -> Dict[str, Any]:
        """
        Get comprehensive learning analytics data
        """
        try:
            # Get learning metrics from Redis
            feedback_processed = int(self.redis_client.get('learning:feedback_processed:total') or 0)
            insights_generated = int(self.redis_client.get('learning:insights_generated:total') or 0)
            optimizations_applied = int(self.redis_client.get('learning:optimizations_applied:total') or 0)

            # Check if learning is currently active
            learning_active = bool(self.redis_client.get('learning:activity_status'))

            # Get recent insights
            recent_insights = []
            try:
                for insight_json in self.redis_client.lrange('learning:recent_insights', 0, 4):
                    recent_insights.append(json.loads(insight_json))
            except:
                pass

            # Get recent optimizations
            recent_optimizations = []
            try:
                for opt_json in self.redis_client.lrange('learning:recent_optimizations', 0, 4):
                    recent_optimizations.append(json.loads(opt_json))
            except:
                pass

            # Calculate improvement rate
            improvement_rate = self.calculate_learning_improvement_rate()

            # Get daily feedback count
            daily_key = f"learning:feedback_processed:day:{datetime.now(self.mst).strftime('%Y%m%d')}"
            daily_feedback = int(self.redis_client.get(daily_key) or 0)

            return {
                'learning_active': learning_active,
                'feedback_processed': feedback_processed,
                'insights_generated': insights_generated,
                'optimizations_applied': optimizations_applied,
                'improvement_rate': improvement_rate,
                'daily_feedback': daily_feedback,
                'recent_insights': recent_insights,
                'recent_optimizations': recent_optimizations,
                'learning_status': 'active' if learning_active else 'dormant'
            }

        except Exception as e:
            logger.error(f"Error getting learning analytics data: {e}")
            return {
                'learning_active': False,
                'feedback_processed': 0,
                'insights_generated': 0,
                'optimizations_applied': 0,
                'improvement_rate': 0.0,
                'daily_feedback': 0,
                'recent_insights': [],
                'recent_optimizations': [],
                'learning_status': 'offline'
            }

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """
        Get all stats for API response
        """
        try:
            # Count total agents in database
            from core.models.agents_registry import UnifiedAgentTemplate
            total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()

            # Get active agent stats
            active_agents = self.get_active_agent_count()

            # Get execution metrics
            total_real = int(self.redis_client.get('stats:real_executions') or 0)
            total_demo = int(self.redis_client.get('stats:demo_executions') or 0)

            # Get today's code generation
            today_stats = self.redis_client.hgetall('stats:code_generated:today') or {}

            # Get file metrics
            files_created = self.get_total_files_created()

            # Calculate rates
            success_rate = self.calculate_success_rate()
            learning_rate = self.calculate_learning_rate()

            # Get recent activities
            recent_activities = []
            for activity_json in self.redis_client.lrange('recent:activities', 0, 9):
                try:
                    recent_activities.append(json.loads(activity_json))
                except:
                    pass

            return {
                'active_agents': active_agents,
                'total_agents': total_agents,
                'total_real_executions': total_real,
                'total_demo_executions': total_demo,
                'files_created': files_created,
                'success_rate': success_rate,
                'learning_rate': learning_rate,
                'projects_completed': self.get_projects_completed(),
                'code_generated_today': int(today_stats.get('count', 0)),
                'lines_today': int(today_stats.get('lines', 0)),
                'recent_activities': recent_activities,
                'timestamp': datetime.now(self.mst).isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting comprehensive stats: {e}")
            return {
                'active_agents': 0,
                'total_agents': 0,
                'total_real_executions': 0,
                'total_demo_executions': 0,
                'files_created': 0,
                'success_rate': 0,
                'learning_rate': 0,
                'projects_completed': 0,
                'code_generated_today': 0,
                'lines_today': 0,
                'recent_activities': [],
                'timestamp': datetime.now(self.mst).isoformat()
            }

# Global instance
execution_tracker = AgentExecutionTracker()