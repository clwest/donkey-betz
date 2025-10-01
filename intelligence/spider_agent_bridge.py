"""
Spider-Agent Intelligence Bridge
Connects spider data collection to agent processing pipeline for real-time intelligence
"""

import asyncio
import json
import logging
import redis
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

from .agent_execution_pipeline import AgentExecutionPipeline
from ai_core.spiders.spider_army_orchestrator import SpiderArmyOrchestrator

logger = logging.getLogger(__name__)


@dataclass
class BridgeMetrics:
    """Bridge performance metrics"""
    spider_data_received: int = 0
    agent_executions_triggered: int = 0
    successful_processings: int = 0
    failed_processings: int = 0
    avg_processing_time_ms: float = 0.0
    uptime_start: datetime = None
    last_data_timestamp: datetime = None


class SpiderAgentBridge:
    """
    Bridge between spider intelligence and agent processing.
    Receives data from spider army and routes it to appropriate agents.
    """

    def __init__(self, redis_config: Dict[str, Any] = None):
        """Initialize the bridge"""
        self.redis_config = redis_config or {'host': 'localhost', 'port': 6379, 'db': 0}
        self.redis_client = redis.Redis(**self.redis_config)

        # Core components
        self.agent_pipeline = AgentExecutionPipeline()
        self.spider_orchestrator = None  # Will be set if needed

        # Bridge state
        self.is_running = False
        self.subscribers = {}
        self.metrics = BridgeMetrics(uptime_start=datetime.now(timezone.utc))

        # Data processing queues
        self.spider_data_queue = asyncio.Queue(maxsize=1000)
        self.agent_result_queue = asyncio.Queue(maxsize=500)

        # Channel subscriptions
        self.spider_channel = "spider_intelligence_bridge"
        self.agent_result_channel = "agent_results_bridge"

        self.logger = logging.getLogger(__name__)

    async def start_bridge(self):
        """Start the bridge processing"""
        if self.is_running:
            return

        self.is_running = True
        self.logger.info("🌉 Starting Spider-Agent Intelligence Bridge")

        # Start background tasks
        tasks = [
            asyncio.create_task(self._listen_for_spider_data()),
            asyncio.create_task(self._process_spider_data_queue()),
            asyncio.create_task(self._monitor_bridge_health()),
            asyncio.create_task(self._publish_metrics())
        ]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Bridge error: {e}")
            await self.stop_bridge()

    async def stop_bridge(self):
        """Stop the bridge processing"""
        self.is_running = False
        self.logger.info("🛑 Stopping Spider-Agent Intelligence Bridge")

    async def _listen_for_spider_data(self):
        """Listen for spider data on Redis channel"""
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(self.spider_channel)

        self.logger.info(f"🕷️ Listening for spider data on channel: {self.spider_channel}")

        try:
            while self.is_running:
                message = pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    try:
                        spider_data = json.loads(message['data'].decode('utf-8'))
                        await self._queue_spider_data(spider_data)
                        self.metrics.spider_data_received += 1
                        self.metrics.last_data_timestamp = datetime.now(timezone.utc)

                    except Exception as e:
                        self.logger.error(f"Error processing spider message: {e}")
                        self.metrics.failed_processings += 1

                await asyncio.sleep(0.1)

        except Exception as e:
            self.logger.error(f"Error in spider data listener: {e}")
        finally:
            pubsub.close()

    async def _queue_spider_data(self, spider_data: Dict[str, Any]):
        """Queue spider data for processing"""
        try:
            await self.spider_data_queue.put(spider_data)
            self.logger.debug(f"Queued spider data: {spider_data.get('swarm_id', 'unknown')}")
        except asyncio.QueueFull:
            self.logger.warning("Spider data queue full, dropping oldest data")
            try:
                # Remove oldest item and add new one
                await asyncio.wait_for(self.spider_data_queue.get(), timeout=0.1)
                await self.spider_data_queue.put(spider_data)
            except asyncio.TimeoutError:
                self.logger.error("Failed to manage queue, dropping spider data")

    async def _process_spider_data_queue(self):
        """Process queued spider data through agents"""
        self.logger.info("🤖 Starting spider data processing through agents")

        while self.is_running:
            try:
                # Get spider data with timeout
                spider_data = await asyncio.wait_for(
                    self.spider_data_queue.get(),
                    timeout=1.0
                )

                start_time = datetime.now()

                # Process through agent pipeline
                results = await self._process_through_agents(spider_data)

                # Calculate processing time
                processing_time = (datetime.now() - start_time).total_seconds() * 1000
                self.metrics.avg_processing_time_ms = (
                    (self.metrics.avg_processing_time_ms * self.metrics.successful_processings + processing_time) /
                    (self.metrics.successful_processings + 1)
                )

                if results:
                    self.metrics.successful_processings += 1
                    # Queue results for further processing
                    await self._queue_agent_results(results)
                else:
                    self.metrics.failed_processings += 1

                self.metrics.agent_executions_triggered += 1

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing spider data: {e}")
                self.metrics.failed_processings += 1

    async def _process_through_agents(self, spider_data: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Process spider data through appropriate agents"""
        try:
            # Extract key information from spider data
            swarm_id = spider_data.get('swarm_id', 'unknown')
            spider_type = spider_data.get('spider_type', 'general')
            data_points = spider_data.get('data_points', [])

            self.logger.info(f"🕷️➡️🤖 Processing {len(data_points)} data points from {swarm_id} through agents")

            # Convert spider data to agent-compatible format
            agent_compatible_data = self._convert_spider_data_for_agents(spider_data)

            # Use agent pipeline to process the data
            results = await self.agent_pipeline.process_spider_intelligence(agent_compatible_data)

            self.logger.info(f"✅ Processed spider data through {len(results)} agent executions")
            return results

        except Exception as e:
            self.logger.error(f"Error processing spider data through agents: {e}")
            return None

    def _convert_spider_data_for_agents(self, spider_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert spider data to format suitable for agent processing"""
        converted_data = []

        data_points = spider_data.get('data_points', [])
        swarm_id = spider_data.get('swarm_id', 'unknown')
        spider_type = spider_data.get('spider_type', 'general')

        for i, data_point in enumerate(data_points):
            converted_data.append({
                'spider_id': f"{swarm_id}_{i}",
                'spider_type': spider_type,
                'data': data_point,
                'timestamp': spider_data.get('timestamp', datetime.now().isoformat()),
                'confidence': data_point.get('confidence', 0.8),
                'source': data_point.get('source', 'spider_army'),
                'metadata': {
                    'swarm_id': swarm_id,
                    'spider_type': spider_type,
                    'data_index': i,
                    'total_points': len(data_points)
                }
            })

        return converted_data

    async def _queue_agent_results(self, results: List[Dict[str, Any]]):
        """Queue agent processing results"""
        try:
            for result in results:
                await self.agent_result_queue.put(result)

            # Publish results to Redis for other components
            combined_results = {
                'timestamp': datetime.now().isoformat(),
                'result_count': len(results),
                'results': results,
                'bridge_id': 'spider_agent_bridge'
            }

            self.redis_client.publish(
                self.agent_result_channel,
                json.dumps(combined_results)
            )

            self.logger.debug(f"Published {len(results)} agent results")

        except Exception as e:
            self.logger.error(f"Error queuing agent results: {e}")

    async def _monitor_bridge_health(self):
        """Monitor bridge health and performance"""
        while self.is_running:
            try:
                # Check queue health
                spider_queue_size = self.spider_data_queue.qsize()
                agent_queue_size = self.agent_result_queue.qsize()

                # Log health status
                if spider_queue_size > 800:  # Queue getting full
                    self.logger.warning(f"Spider data queue high: {spider_queue_size}/1000")

                if agent_queue_size > 400:  # Results queue getting full
                    self.logger.warning(f"Agent results queue high: {agent_queue_size}/500")

                # Check data freshness
                if self.metrics.last_data_timestamp:
                    time_since_data = (datetime.now(timezone.utc) - self.metrics.last_data_timestamp).total_seconds()
                    if time_since_data > 300:  # No data for 5 minutes
                        self.logger.warning(f"No spider data received for {time_since_data:.0f} seconds")

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Error in bridge health monitor: {e}")

    async def _publish_metrics(self):
        """Publish bridge metrics"""
        while self.is_running:
            try:
                # Calculate uptime
                uptime_seconds = (datetime.now(timezone.utc) - self.metrics.uptime_start).total_seconds()

                metrics_data = {
                    'bridge_id': 'spider_agent_bridge',
                    'timestamp': datetime.now().isoformat(),
                    'uptime_seconds': uptime_seconds,
                    'metrics': asdict(self.metrics),
                    'queue_sizes': {
                        'spider_data_queue': self.spider_data_queue.qsize(),
                        'agent_result_queue': self.agent_result_queue.qsize()
                    }
                }

                self.redis_client.publish('bridge_metrics', json.dumps(metrics_data))

                await asyncio.sleep(60)  # Publish every minute

            except Exception as e:
                self.logger.error(f"Error publishing metrics: {e}")

    def get_bridge_status(self) -> Dict[str, Any]:
        """Get current bridge status"""
        uptime_seconds = (datetime.now(timezone.utc) - self.metrics.uptime_start).total_seconds()

        # Convert metrics to dict and serialize datetime objects
        metrics_dict = asdict(self.metrics)
        if metrics_dict.get('uptime_start'):
            metrics_dict['uptime_start'] = metrics_dict['uptime_start'].isoformat()
        if metrics_dict.get('last_data_timestamp'):
            metrics_dict['last_data_timestamp'] = metrics_dict['last_data_timestamp'].isoformat()

        return {
            'is_running': self.is_running,
            'uptime_seconds': uptime_seconds,
            'metrics': metrics_dict,
            'queue_sizes': {
                'spider_data_queue': self.spider_data_queue.qsize(),
                'agent_result_queue': self.agent_result_queue.qsize()
            },
            'channels': {
                'spider_input': self.spider_channel,
                'agent_output': self.agent_result_channel
            }
        }

    async def trigger_spider_deployment(self, user_request: str, target_domains: List[str] = None) -> Dict[str, Any]:
        """Trigger spider deployment for specific intelligence gathering"""
        try:
            # This would integrate with the spider orchestrator
            if not self.spider_orchestrator:
                # Create a mock deployment response
                deployment_response = {
                    'deployment_id': f"deploy_{datetime.now().timestamp()}",
                    'user_request': user_request,
                    'target_domains': target_domains or ['general'],
                    'estimated_spiders': 50,
                    'estimated_completion_time': '2-5 minutes',
                    'status': 'deployed'
                }
            else:
                # Use real spider orchestrator
                deployment_response = await self.spider_orchestrator.deploy_spider_army(
                    user_request=user_request,
                    targets=target_domains
                )

            self.logger.info(f"🕷️ Triggered spider deployment: {deployment_response.get('deployment_id')}")
            return deployment_response

        except Exception as e:
            self.logger.error(f"Error triggering spider deployment: {e}")
            return {'error': str(e), 'status': 'failed'}


# Global bridge instance
_bridge_instance = None

def get_spider_agent_bridge() -> SpiderAgentBridge:
    """Get the global spider-agent bridge instance"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = SpiderAgentBridge()
    return _bridge_instance

# Convenience functions
async def start_bridge():
    """Start the bridge"""
    bridge = get_spider_agent_bridge()
    await bridge.start_bridge()

async def process_spider_data(spider_data: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """Process spider data through the bridge"""
    bridge = get_spider_agent_bridge()
    return await bridge._process_through_agents(spider_data)

def get_bridge_status() -> Dict[str, Any]:
    """Get bridge status"""
    bridge = get_spider_agent_bridge()
    return bridge.get_bridge_status()