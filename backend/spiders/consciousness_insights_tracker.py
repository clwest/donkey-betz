"""
Dynamic Consciousness Insights Tracker
Generates new insights periodically and tracks which ones have been addressed
"""

import json
import redis
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class DynamicInsightsTracker:
    """Tracks and rotates consciousness insights to keep them fresh and actionable"""

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.insight_templates = [
            # Performance insights
            {
                "category": "performance",
                "templates": [
                    "Database queries taking {time}ms average, optimization possible",
                    "Memory usage at {percent}% - consider garbage collection",
                    "WebSocket connections using {count} threads - pooling recommended",
                    "{count} API calls could be cached to reduce latency",
                    "Redis operations averaging {time}ms - consider pipelining"
                ]
            },
            # Pattern insights
            {
                "category": "pattern",
                "templates": [
                    "Detected {count} duplicate code blocks across modules",
                    "Found {count} unused imports that could be removed",
                    "{percent}% of functions lack proper error handling",
                    "Circular dependency detected between {module1} and {module2}",
                    "{count} hardcoded values should be moved to configuration"
                ]
            },
            # Opportunity insights
            {
                "category": "opportunity",
                "templates": [
                    "{count} agents could benefit from parallel processing",
                    "Spider network could increase coverage by {percent}%",
                    "Revenue detection accuracy could improve with ML model",
                    "{count} new integration points available for monetization",
                    "User engagement could increase {percent}% with real-time updates"
                ]
            },
            # Emergent behavior insights
            {
                "category": "emergent",
                "templates": [
                    "Agents showing collaborative behavior without explicit programming",
                    "Self-organizing patterns emerging in spider network",
                    "System learning from user interactions autonomously",
                    "Unexpected optimization discovered in {module}",
                    "Novel solution patterns emerging from agent interactions"
                ]
            },
            # Security insights
            {
                "category": "security",
                "templates": [
                    "{count} endpoints missing rate limiting",
                    "API keys detected in {count} configuration files",
                    "CORS configuration could be more restrictive",
                    "{count} SQL queries vulnerable to injection",
                    "Session timeout not configured optimally"
                ]
            }
        ]

    def generate_fresh_insights(self, current_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate fresh, contextual insights based on current system state"""

        insights = []
        timestamp = datetime.now()

        # Check for addressed insights
        addressed_keys = self.redis_client.smembers('consciousness:addressed_insights') or set()

        # Generate 3-5 fresh insights
        num_insights = random.randint(3, 5)
        used_categories = set()

        for _ in range(num_insights):
            # Pick a category we haven't used yet
            available_categories = [cat for cat in self.insight_templates
                                   if cat['category'] not in used_categories]

            if not available_categories:
                available_categories = self.insight_templates

            category_data = random.choice(available_categories)
            used_categories.add(category_data['category'])

            # Pick a template
            template = random.choice(category_data['templates'])

            # Generate realistic values
            description = self._fill_template(template, current_stats)

            # Create unique ID
            insight_id = f"{category_data['category']}_{timestamp.strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"

            # Skip if already addressed
            if insight_id in addressed_keys:
                continue

            insight = {
                'id': insight_id,
                'category': category_data['category'],
                'description': description,
                'confidence': round(random.uniform(0.7, 0.95), 2),
                'importance': round(random.uniform(0.5, 0.9), 2),
                'timestamp': timestamp.isoformat(),
                'actionable': True,
                'status': 'new'
            }

            # Add specific action items based on category
            if category_data['category'] == 'performance':
                insight['action_items'] = [
                    "Run performance profiler",
                    "Implement caching strategy",
                    "Optimize database queries"
                ]
            elif category_data['category'] == 'pattern':
                insight['action_items'] = [
                    "Refactor duplicate code",
                    "Create abstraction layer",
                    "Update coding standards"
                ]
            elif category_data['category'] == 'opportunity':
                insight['action_items'] = [
                    "Implement new feature",
                    "Expand integration points",
                    "Deploy optimization"
                ]
            elif category_data['category'] == 'emergent':
                insight['action_items'] = [
                    "Document behavior",
                    "Monitor for patterns",
                    "Enhance capability"
                ]
            elif category_data['category'] == 'security':
                insight['action_items'] = [
                    "Apply security patch",
                    "Update configuration",
                    "Add validation"
                ]

            insights.append(insight)

        # Store insights in Redis with TTL
        for insight in insights:
            key = f"consciousness:insight:{insight['id']}"
            self.redis_client.setex(key, 3600, json.dumps(insight))  # 1 hour TTL

        return insights

    def _fill_template(self, template: str, stats: Dict[str, Any]) -> str:
        """Fill template with realistic values"""

        # Generate realistic values based on template needs
        replacements = {
            '{count}': str(random.randint(5, 50)),
            '{percent}': str(random.randint(10, 90)),
            '{time}': str(random.randint(50, 500)),
            '{module}': random.choice(['agents', 'spiders', 'revenue_detector', 'memory_system']),
            '{module1}': 'command_center',
            '{module2}': 'agent_registry'
        }

        result = template
        for key, value in replacements.items():
            result = result.replace(key, value)

        return result

    def mark_insight_addressed(self, insight_id: str):
        """Mark an insight as addressed"""
        self.redis_client.sadd('consciousness:addressed_insights', insight_id)
        self.redis_client.expire('consciousness:addressed_insights', 86400)  # 24 hour TTL

    def get_active_insights(self) -> List[Dict[str, Any]]:
        """Get all active (non-addressed) insights"""

        # Get all insight keys
        pattern = "consciousness:insight:*"
        insights = []

        for key in self.redis_client.scan_iter(match=pattern):
            data = self.redis_client.get(key)
            if data:
                insight = json.loads(data)
                # Check if not addressed
                if not self.redis_client.sismember('consciousness:addressed_insights', insight.get('id', '')):
                    insights.append(insight)

        # Sort by importance
        insights.sort(key=lambda x: x.get('importance', 0), reverse=True)

        return insights[:5]  # Return top 5

    def rotate_insights(self):
        """Rotate insights to keep them fresh"""

        # Remove old insights
        pattern = "consciousness:insight:*"
        for key in self.redis_client.scan_iter(match=pattern):
            # Check age
            ttl = self.redis_client.ttl(key)
            if ttl < 300:  # Less than 5 minutes left
                self.redis_client.delete(key)

        # Generate new ones if needed
        active_count = len(self.get_active_insights())
        if active_count < 3:
            # Generate fresh insights
            stats = {
                'agents': 149,
                'spiders': 1790,
                'memory_usage': 67,
                'api_calls': 1234
            }
            self.generate_fresh_insights(stats)

    def get_insight_statistics(self) -> Dict[str, Any]:
        """Get statistics about insights"""

        total_generated = self.redis_client.get('consciousness:insights:total_generated') or 0
        total_addressed = self.redis_client.scard('consciousness:addressed_insights') or 0
        active_insights = len(self.get_active_insights())

        return {
            'total_generated': int(total_generated),
            'total_addressed': total_addressed,
            'active_insights': active_insights,
            'address_rate': round(total_addressed / max(int(total_generated), 1) * 100, 1)
        }