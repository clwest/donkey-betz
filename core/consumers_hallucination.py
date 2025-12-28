"""
WebSocket consumer for real-time hallucination monitoring
"""
import asyncio
import json
import logging
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
import redis.asyncio as redis

logger = logging.getLogger(__name__)
from ai_core.agents.mythology_validator import mythology_enforcer
from mythology.services import MythologyDetectionService


class HallucinationMonitorConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer that streams blocked hallucinations in real-time
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = None
        self.monitoring_active = False
        self.detection_service = MythologyDetectionService()

    async def connect(self):
        """Accept WebSocket connection"""
        await self.accept()

        # Initialize Redis connection
        self.redis_client = await redis.Redis(
            host='localhost',
            port=6379,
            db=2,
            decode_responses=True
        )

        # Send initial status
        await self.send(json.dumps({
            'type': 'connection_established',
            'message': 'Connected to Hallucination Monitor',
            'timestamp': datetime.now().isoformat(),
            'status': 'active'
        }))

        # Start monitoring
        self.monitoring_active = True
        asyncio.create_task(self.monitor_hallucinations())

        # Send current stats
        await self.send_current_stats()

    async def disconnect(self, close_code):
        """Handle disconnection"""
        self.monitoring_active = False
        if self.redis_client:
            await self.redis_client.close()

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            command = data.get('command')

            if command == 'get_stats':
                await self.send_current_stats()
            elif command == 'test_hallucination':
                # Test with a known hallucination
                await self.test_hallucination(data.get('text', ''))
            elif command == 'clear_history':
                await self.clear_history()

        except json.JSONDecodeError:
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON received'
            }))

    async def monitor_hallucinations(self):
        """Monitor Redis for hallucination events"""
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe('hallucination_events')

        try:
            while self.monitoring_active:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)

                if message and message['type'] == 'message':
                    # Parse and send hallucination event
                    event_data = json.loads(message['data'])
                    await self.send_hallucination_event(event_data)

                await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"Monitor error: {e}")
        finally:
            await pubsub.unsubscribe('hallucination_events')

    async def send_hallucination_event(self, event_data):
        """Send hallucination event to frontend"""
        await self.send(json.dumps({
            'type': 'hallucination_blocked',
            'timestamp': datetime.now().isoformat(),
            'agent': event_data.get('agent', 'unknown'),
            'original_text': event_data.get('original_text', '')[:200],
            'patterns_detected': event_data.get('patterns', []),
            'risk_score': event_data.get('risk_score', 0),
            'corrected_text': event_data.get('corrected_text', '')[:200],
            'severity': event_data.get('severity', 'medium')
        }))

    async def send_current_stats(self):
        """Send current hallucination statistics"""
        # Get stats from Redis
        stats = await self.redis_client.hgetall('mythology_learning:stats')

        # Get enforcement report
        report = mythology_enforcer.get_report()

        await self.send(json.dumps({
            'type': 'stats_update',
            'timestamp': datetime.now().isoformat(),
            'stats': {
                'total_checked': report['stats'].get('total_checks', 0),
                'violations_found': report['stats'].get('violations_found', 0),
                'corrections_made': report['stats'].get('corrections_made', 0),
                'violation_rate': report['stats'].get('violation_rate', 0),
                'validated_learnings': int(stats.get('validated_learnings', 0)),
                'perfect_learnings': int(stats.get('perfect_learnings', 0)),
                'corrected_count': int(stats.get('corrected_count', 0))
            },
            'recent_violations': report['stats'].get('recent_violations', [])
        }))

    async def test_hallucination(self, text):
        """Test a text for hallucinations"""
        if not text:
            text = "Generate guaranteed $10000 daily with 100% success rate"

        # Detect mythologies
        detection_result = self.detection_service.detect_mythologies(text, 'test')

        # Validate with mythology enforcer
        validation = mythology_enforcer.enforce('test_agent', text)

        # Send test result
        await self.send(json.dumps({
            'type': 'test_result',
            'timestamp': datetime.now().isoformat(),
            'original_text': text,
            'detected': detection_result['detected'],
            'patterns_found': detection_result['patterns_found'],
            'risk_score': detection_result['risk_score'],
            'severity': detection_result['severity'],
            'corrected': validation.get('mythology_corrected', False),
            'corrected_text': str(validation.get('result', text))
        }))

        # Also publish as event
        await self.redis_client.publish('hallucination_events', json.dumps({
            'agent': 'test_agent',
            'original_text': text,
            'patterns': detection_result['patterns_found'],
            'risk_score': detection_result['risk_score'],
            'corrected_text': str(validation.get('result', text)),
            'severity': detection_result['severity']
        }))

    async def clear_history(self):
        """Clear hallucination history"""
        # Clear recent violations from memory
        mythology_enforcer.validator.violation_log = []

        await self.send(json.dumps({
            'type': 'history_cleared',
            'timestamp': datetime.now().isoformat(),
            'message': 'Hallucination history cleared'
        }))