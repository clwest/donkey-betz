#!/usr/bin/env python
"""
Enhanced Learning Workflow API
===============================
API endpoints for triggering and managing real-time agent learning workflows
"""

import os
import sys
import json
import time
import asyncio
import uuid
from datetime import datetime
from threading import Thread
from typing import Dict, List, Optional

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Django imports
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View

# Channel layer for WebSocket communication
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Import learning systems
try:
    from real_agent_learning_system import RealLearningSystem, RealLearningAgent
    from agent_to_agent_learning import TeachingAgent, create_specialist_agent
    from agent_spider_learning_system import SpiderAgent, LearningAgent
except ImportError as e:
    print(f"Warning: Learning systems not available: {e}")
    RealLearningSystem = None
    TeachingAgent = None
    SpiderAgent = None


class EnhancedLearningWorkflowAPI:
    """
    API class for managing enhanced learning workflows
    """

    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.active_workflows = {}

    def send_websocket_update(self, message_type: str, data: Dict):
        """Send update to WebSocket clients"""
        if self.channel_layer:
            async_to_sync(self.channel_layer.group_send)(
                'neural_orchestra',
                {
                    'type': message_type,
                    'data': data
                }
            )

    def start_learning_workflow(self, topic: str) -> Dict:
        """Start a comprehensive learning workflow"""
        workflow_id = str(uuid.uuid4())

        try:
            # Store workflow
            self.active_workflows[workflow_id] = {
                'id': workflow_id,
                'topic': topic,
                'status': 'started',
                'start_time': datetime.now().isoformat(),
                'phases': [],
                'agents': [],
                'metrics': {
                    'total_agents': 0,
                    'knowledge_items': 0,
                    'collaborations': 0,
                    'tokens_used': 0
                }
            }

            # Start workflow in background thread
            workflow_thread = Thread(
                target=self._run_workflow_background,
                args=(workflow_id, topic),
                daemon=True
            )
            workflow_thread.start()

            # Send initial WebSocket update
            self.send_websocket_update('workflow_started', {
                'workflow_id': workflow_id,
                'topic': topic,
                'status': 'started',
                'timestamp': datetime.now().isoformat()
            })

            return {
                'success': True,
                'workflow_id': workflow_id,
                'topic': topic,
                'status': 'started'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _run_workflow_background(self, workflow_id: str, topic: str):
        """Run the complete learning workflow in background"""
        try:
            workflow = self.active_workflows[workflow_id]

            # Phase 1: Spider Data Collection
            self._run_phase_1(workflow_id, topic)
            time.sleep(2)

            # Phase 2: Initial Agent Learning
            self._run_phase_2(workflow_id, topic)
            time.sleep(2)

            # Phase 3: Dynamic Team Formation
            self._run_phase_3(workflow_id, topic)
            time.sleep(2)

            # Phase 4: Agent-to-Agent Learning
            self._run_phase_4(workflow_id, topic)
            time.sleep(2)

            # Phase 5: Content Generation
            self._run_phase_5(workflow_id, topic)

            # Mark workflow complete
            workflow['status'] = 'completed'
            workflow['end_time'] = datetime.now().isoformat()

            self.send_websocket_update('workflow_complete', {
                'workflow_id': workflow_id,
                'status': 'completed',
                'timestamp': datetime.now().isoformat(),
                'summary': workflow['metrics']
            })

        except Exception as e:
            print(f"Workflow error: {e}")
            self.send_websocket_update('workflow_error', {
                'workflow_id': workflow_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })

    def _run_phase_1(self, workflow_id: str, topic: str):
        """Phase 1: Spider Data Collection"""
        self.send_websocket_update('phase_update', {
            'workflow_id': workflow_id,
            'phase': 1,
            'status': 'active',
            'description': 'Spider agents gathering data'
        })

        # Simulate spider data collection
        spiders = ['TechSpider', 'NewsSpider', 'ResearchSpider']

        for spider_name in spiders:
            spider_data = {
                'spider': spider_name,
                'source': f'{spider_name} Data Source',
                'summary': f'Collected data about {topic}',
                'dataPoints': 15 + len(spider_name),
                'timestamp': datetime.now().isoformat()
            }

            self.send_websocket_update('spider_data', spider_data)
            time.sleep(1)

        self.send_websocket_update('phase_update', {
            'workflow_id': workflow_id,
            'phase': 1,
            'status': 'complete',
            'description': 'Spider data collection completed'
        })

    def _run_phase_2(self, workflow_id: str, topic: str):
        """Phase 2: Initial Agent Learning"""
        self.send_websocket_update('phase_update', {
            'workflow_id': workflow_id,
            'phase': 2,
            'status': 'active',
            'description': 'Primary agent analyzing data'
        })

        # Create primary learning agent
        primary_agent = {
            'name': 'PrimaryAnalyst',
            'specialization': f'{topic} analysis and research',
            'knowledgeCount': 0
        }

        self.active_workflows[workflow_id]['agents'].append(primary_agent)

        self.send_websocket_update('agent_created', {
            'workflow_id': workflow_id,
            'agent': primary_agent
        })

        # Simulate learning process
        learning_steps = [
            f"Analyzing {topic} fundamentals",
            f"Processing {topic} applications",
            f"Identifying {topic} challenges and opportunities"
        ]

        for step in learning_steps:
            self.send_websocket_update('agent_conversation', {
                'agent': 'PrimaryAnalyst',
                'message': step,
                'type': 'agent',
                'timestamp': datetime.now().isoformat()
            })

            primary_agent['knowledgeCount'] += 1
            self.active_workflows[workflow_id]['metrics']['knowledge_items'] += 1
            self.active_workflows[workflow_id]['metrics']['tokens_used'] += 150
            time.sleep(1)

        self.send_websocket_update('phase_update', {
            'workflow_id': workflow_id,
            'phase': 2,
            'status': 'complete',
            'description': 'Initial learning completed'
        })

    def _run_phase_3(self, workflow_id: str, topic: str):
        """Phase 3: Dynamic Team Formation"""
        self.send_websocket_update('phase_update', {
            'workflow_id': workflow_id,
            'phase': 3,
            'status': 'active',
            'description': 'Creating specialist team'
        })

        # Create specialist agents based on topic
        specialists = self._determine_specialists(topic)

        for specialist in specialists:
            self.active_workflows[workflow_id]['agents'].append(specialist)
            self.active_workflows[workflow_id]['metrics']['total_agents'] += 1

            self.send_websocket_update('agent_created', {
                'workflow_id': workflow_id,
                'agent': specialist
            })

            self.send_websocket_update('agent_conversation', {
                'agent': 'System',
                'message': f"Created specialist: {specialist['name']} ({specialist['specialization']})",
                'type': 'system',
                'timestamp': datetime.now().isoformat()
            })
            time.sleep(1)

        self.send_websocket_update('phase_update', {
            'workflow_id': workflow_id,
            'phase': 3,
            'status': 'complete',
            'description': 'Specialist team formed'
        })

    def _run_phase_4(self, workflow_id: str, topic: str):
        """Phase 4: Agent-to-Agent Learning"""
        self.send_websocket_update('phase_update', {
            'workflow_id': workflow_id,
            'phase': 4,
            'status': 'active',
            'description': 'Agents teaching each other'
        })

        agents = self.active_workflows[workflow_id]['agents']

        # Simulate teaching sessions between agents
        for i, teacher in enumerate(agents[:3]):  # First 3 agents teach
            for j, student in enumerate(agents[1:4]):  # Next 3 learn
                if teacher != student:
                    self._simulate_teaching_session(workflow_id, teacher, student, topic)
                    time.sleep(1)

        self.send_websocket_update('phase_update', {
            'workflow_id': workflow_id,
            'phase': 4,
            'status': 'complete',
            'description': 'Knowledge sharing completed'
        })

    def _run_phase_5(self, workflow_id: str, topic: str):
        """Phase 5: Content Generation"""
        self.send_websocket_update('phase_update', {
            'workflow_id': workflow_id,
            'phase': 5,
            'status': 'active',
            'description': 'Generating content'
        })

        content_types = [
            ('research_report', f'Comprehensive {topic} Research Report'),
            ('guide', f'Practical Guide to {topic}'),
            ('analysis', f'{topic} Market Analysis')
        ]

        for content_type, title in content_types:
            agent = self.active_workflows[workflow_id]['agents'][0]  # Use first agent

            content = {
                'type': content_type,
                'title': title,
                'summary': f'Generated content about {topic} covering key insights and practical applications',
                'agent': agent['name'],
                'tokens': 450,
                'timestamp': datetime.now().isoformat()
            }

            self.active_workflows[workflow_id]['metrics']['tokens_used'] += content['tokens']

            self.send_websocket_update('content_generated', content)
            time.sleep(1)

        self.send_websocket_update('phase_update', {
            'workflow_id': workflow_id,
            'phase': 5,
            'status': 'complete',
            'description': 'Content generation completed'
        })

    def _determine_specialists(self, topic: str) -> List[Dict]:
        """Determine what specialists are needed for the topic"""
        topic_lower = topic.lower()

        if 'quantum' in topic_lower:
            return [
                {'name': 'QuantumTheoryExpert', 'specialization': 'Quantum mechanics and theory', 'knowledgeCount': 0},
                {'name': 'ApplicationSpecialist', 'specialization': 'Quantum computing applications', 'knowledgeCount': 0},
                {'name': 'TechnologyIntegrator', 'specialization': 'Quantum technology implementation', 'knowledgeCount': 0}
            ]
        elif 'ai' in topic_lower or 'artificial' in topic_lower:
            return [
                {'name': 'MLSpecialist', 'specialization': 'Machine learning algorithms', 'knowledgeCount': 0},
                {'name': 'EthicsExpert', 'specialization': 'AI ethics and governance', 'knowledgeCount': 0},
                {'name': 'ApplicationArchitect', 'specialization': 'AI system design and deployment', 'knowledgeCount': 0}
            ]
        elif 'energy' in topic_lower or 'sustainable' in topic_lower:
            return [
                {'name': 'RenewableExpert', 'specialization': 'Renewable energy systems', 'knowledgeCount': 0},
                {'name': 'PolicyAnalyst', 'specialization': 'Energy policy and regulations', 'knowledgeCount': 0},
                {'name': 'TechInnovator', 'specialization': 'Clean technology innovation', 'knowledgeCount': 0}
            ]
        else:
            return [
                {'name': 'ResearchSpecialist', 'specialization': f'{topic} research and analysis', 'knowledgeCount': 0},
                {'name': 'PracticalExpert', 'specialization': f'{topic} practical applications', 'knowledgeCount': 0},
                {'name': 'FutureStrategist', 'specialization': f'{topic} trends and future outlook', 'knowledgeCount': 0}
            ]

    def _simulate_teaching_session(self, workflow_id: str, teacher: Dict, student: Dict, topic: str):
        """Simulate a teaching session between two agents"""
        self.send_websocket_update('agent_conversation', {
            'agent': teacher['name'],
            'message': f"Teaching {student['name']} about {topic} from my {teacher['specialization']} perspective",
            'type': 'agent',
            'timestamp': datetime.now().isoformat()
        })

        # Knowledge transfer
        knowledge_transfer = {
            'from': teacher['name'],
            'to': student['name'],
            'topic': topic,
            'tokens': 200,
            'timestamp': datetime.now().isoformat()
        }

        self.send_websocket_update('knowledge_transfer', knowledge_transfer)

        # Update metrics
        self.active_workflows[workflow_id]['metrics']['collaborations'] += 1
        self.active_workflows[workflow_id]['metrics']['tokens_used'] += 200
        student['knowledgeCount'] += 1

        # Send response from student
        self.send_websocket_update('agent_conversation', {
            'agent': student['name'],
            'message': f"Thank you {teacher['name']}, I now understand {topic} better from the {teacher['specialization']} angle",
            'type': 'agent',
            'timestamp': datetime.now().isoformat()
        })

    def get_workflow_status(self, workflow_id: str) -> Dict:
        """Get current workflow status"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]

            # Update metrics
            metrics = workflow['metrics']
            metrics['total_agents'] = len(workflow['agents'])

            return {
                'success': True,
                'workflow': workflow,
                'complete': workflow['status'] == 'completed'
            }
        else:
            return {
                'success': False,
                'error': 'Workflow not found'
            }

    def get_current_data(self) -> Dict:
        """Get current learning system data"""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)

            # Get real data from Redis
            learning_metrics = r.hgetall("learning:system:metrics")
            final_metrics = r.hgetall("learning:system:final")

            current_data = {
                'agents': [],
                'conversations': [],
                'knowledgeTransfers': [],
                'spiderData': [],
                'metrics': {
                    'totalAgents': int(learning_metrics.get('total_agents', 0)) or int(final_metrics.get('agents_trained', 0)),
                    'knowledgeItems': int(final_metrics.get('total_knowledge_items', 0)) or int(learning_metrics.get('total_learnings', 0)),
                    'collaborations': int(final_metrics.get('total_collaborations', 0)),
                    'tokensUsed': int(learning_metrics.get('total_tokens', 0)) or int(final_metrics.get('total_tokens_used', 0))
                },
                'generatedContent': []
            }

            # Get generated content
            content_list = r.lrange("generated_content", 0, 2)
            for content_json in content_list:
                try:
                    content = json.loads(content_json)
                    current_data['generatedContent'].append({
                        'type': content.get('type', 'content'),
                        'title': content.get('topic', 'Generated Content'),
                        'summary': content.get('content', '')[:100] + '...',
                        'agent': content.get('agent', 'AI Agent'),
                        'tokens': content.get('tokens_used', 0),
                        'timestamp': content.get('timestamp', datetime.now().isoformat())
                    })
                except:
                    pass

            return {
                'success': True,
                'data': current_data
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Global API instance
learning_workflow_api = EnhancedLearningWorkflowAPI()


# Django Views
@method_decorator(csrf_exempt, name='dispatch')
class StartLearningWorkflowView(View):
    """API view to start a learning workflow"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            topic = data.get('topic', '').strip()

            if not topic:
                return JsonResponse({
                    'success': False,
                    'error': 'Topic is required'
                }, status=400)

            result = learning_workflow_api.start_learning_workflow(topic)
            return JsonResponse(result)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class WorkflowStatusView(View):
    """API view to get workflow status"""

    def get(self, request, workflow_id):
        result = learning_workflow_api.get_workflow_status(workflow_id)
        return JsonResponse(result)


@method_decorator(csrf_exempt, name='dispatch')
class CurrentDataView(View):
    """API view to get current learning data"""

    def get(self, request):
        result = learning_workflow_api.get_current_data()
        return JsonResponse(result)


# URL Configuration (to be added to core/urls.py)
def get_enhanced_learning_urls():
    """Get URL patterns for enhanced learning workflow API"""
    from django.urls import path

    return [
        path('api/neural-orchestra/start-learning/', StartLearningWorkflowView.as_view(), name='start_learning_workflow'),
        path('api/neural-orchestra/workflow-status/<str:workflow_id>/', WorkflowStatusView.as_view(), name='workflow_status'),
        path('api/neural-orchestra/current-data/', CurrentDataView.as_view(), name='current_learning_data'),
    ]


if __name__ == "__main__":
    # Test the API
    api = EnhancedLearningWorkflowAPI()
    result = api.start_learning_workflow("Quantum Computing Applications")
    print(f"Started workflow: {result}")

    time.sleep(5)

    status = api.get_workflow_status(result['workflow_id'])
    print(f"Workflow status: {status}")