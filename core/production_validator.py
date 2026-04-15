"""
Production Validation Suite
Tests all critical systems for 95%+ production readiness
"""

import asyncio
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from django.conf import settings
from channels.testing import WebsocketCommunicator
import redis

logger = logging.getLogger(__name__)


class ProductionValidator:
    """Comprehensive production readiness validation"""

    def __init__(self):
        self.results = {}
        self.overall_score = 0.0
        self.critical_issues = []
        self.warnings = []
        self.performance_metrics = {}

    async def run_full_validation(self) -> Dict[str, Any]:
        """Run complete production validation suite"""
        logger.info("Starting Production Validation Suite")
        start_time = time.time()

        # Test infrastructure components
        await self.test_redis_production_config()
        await self.test_websocket_stability()
        await self.test_channel_layer_performance()

        # Test WebSocket consumers
        await self.test_revenue_dashboard_websocket()
        await self.test_neural_orchestra_websocket()
        await self.test_unified_hub_performance()

        # Test database performance
        await self.test_database_performance()

        # Test error handling
        await self.test_error_recovery()

        # Test load handling
        await self.test_concurrent_connections()

        # Calculate overall score
        self.calculate_overall_score()

        validation_time = time.time() - start_time
        logger.info(f"Production validation completed in {validation_time:.2f}s")

        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'validation_time': validation_time,
            'overall_score': self.overall_score,
            'production_ready': self.overall_score >= 95.0,
            'results': self.results,
            'critical_issues': self.critical_issues,
            'warnings': self.warnings,
            'performance_metrics': self.performance_metrics,
            'recommendations': self.generate_recommendations()
        }

    async def test_redis_production_config(self):
        """Test Redis production configuration"""
        test_name = "redis_production_config"
        try:
            # Test Redis connection with production settings
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/1')
            r = redis.from_url(
                redis_url,
                socket_connect_timeout=5,
                socket_timeout=5,
                socket_keepalive=True,
                health_check_interval=30,
                retry_on_timeout=True
            )

            # Test basic operations
            start_time = time.time()
            r.ping()
            ping_time = (time.time() - start_time) * 1000

            # Test connection pool
            pool_info = r.connection_pool.connection_kwargs
            max_connections = r.connection_pool.max_connections

            # Test persistence settings
            config = r.config_get()

            score = 95.0
            issues = []

            # Check configuration
            if ping_time > 100:  # >100ms is concerning
                score -= 10
                issues.append(f"High Redis latency: {ping_time:.2f}ms")

            if max_connections < 20:
                score -= 5
                issues.append(f"Low connection pool size: {max_connections}")

            self.results[test_name] = {
                'score': score,
                'ping_time_ms': ping_time,
                'max_connections': max_connections,
                'issues': issues,
                'status': 'pass' if score >= 90 else 'fail'
            }

            if score < 90:
                self.critical_issues.extend(issues)

        except Exception as e:
            self.results[test_name] = {
                'score': 0,
                'error': str(e),
                'status': 'fail'
            }
            self.critical_issues.append(f"Redis connection failed: {e}")

    async def test_websocket_stability(self):
        """Test WebSocket connection stability"""
        test_name = "websocket_stability"
        try:
            pass

            # Test multiple connections
            stability_score = 100.0
            connection_results = []

            # Test Revenue Dashboard WebSocket
            revenue_result = await self.test_websocket_endpoint('/ws/revenue-dashboard/')
            connection_results.append(('revenue_dashboard', revenue_result))

            # Test Neural Orchestra WebSocket
            orchestra_result = await self.test_websocket_endpoint('/ws/neural-orchestra/')
            connection_results.append(('neural_orchestra', orchestra_result))

            # Calculate overall stability
            failed_connections = sum(1 for _, result in connection_results if not result['connected'])
            if failed_connections > 0:
                stability_score -= (failed_connections / len(connection_results)) * 50

            # Test heartbeat functionality
            heartbeat_score = await self.test_heartbeat_mechanism()
            stability_score = (stability_score + heartbeat_score) / 2

            self.results[test_name] = {
                'score': stability_score,
                'connection_results': connection_results,
                'heartbeat_score': heartbeat_score,
                'status': 'pass' if stability_score >= 90 else 'fail'
            }

            if stability_score < 90:
                self.critical_issues.append("WebSocket stability below production standards")

        except Exception as e:
            self.results[test_name] = {
                'score': 0,
                'error': str(e),
                'status': 'fail'
            }
            self.critical_issues.append(f"WebSocket stability test failed: {e}")

    async def test_websocket_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Test individual WebSocket endpoint"""
        try:
            from core.asgi import application

            communicator = WebsocketCommunicator(application, endpoint)

            # Test connection
            start_time = time.time()
            connected, subprotocol = await communicator.connect()
            connection_time = (time.time() - start_time) * 1000

            if not connected:
                return {
                    'connected': False,
                    'error': 'Failed to connect',
                    'connection_time_ms': connection_time
                }

            # Test message exchange
            test_message = {'type': 'ping', 'timestamp': time.time()}
            await communicator.send_json_to(test_message)

            # Wait for response
            try:
                response = await asyncio.wait_for(
                    communicator.receive_json_from(),
                    timeout=5.0
                )
                message_round_trip = True
            except asyncio.TimeoutError:
                message_round_trip = False
                response = None

            # Test graceful disconnect
            await communicator.disconnect()

            return {
                'connected': True,
                'connection_time_ms': connection_time,
                'message_round_trip': message_round_trip,
                'response': response
            }

        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'connection_time_ms': 0
            }

    async def test_heartbeat_mechanism(self) -> float:
        """Test WebSocket heartbeat mechanism"""
        try:
            from core.asgi import application

            communicator = WebsocketCommunicator(application, '/ws/revenue-dashboard/')
            connected, _ = await communicator.connect()

            if not connected:
                return 0.0

            # Wait for heartbeat
            heartbeat_received = False
            for _ in range(3):  # Wait up to 3 messages
                try:
                    message = await asyncio.wait_for(
                        communicator.receive_json_from(),
                        timeout=35.0  # Heartbeat should come within 30s + buffer
                    )
                    if message.get('type') == 'heartbeat':
                        heartbeat_received = True
                        break
                except asyncio.TimeoutError:
                    break

            await communicator.disconnect()

            return 100.0 if heartbeat_received else 50.0

        except Exception as e:
            logger.error(f"Heartbeat test error: {e}")
            return 0.0

    async def test_revenue_dashboard_websocket(self):
        """Test Revenue Dashboard WebSocket specifically"""
        test_name = "revenue_dashboard_websocket"
        try:
            from core.asgi import application

            communicator = WebsocketCommunicator(application, '/ws/revenue-dashboard/')
            connected, _ = await communicator.connect()

            score = 100.0
            issues = []

            if not connected:
                score = 0
                issues.append("Failed to connect to Revenue Dashboard WebSocket")
            else:
                # Test data request
                await communicator.send_json_to({'type': 'get_data'})

                # Wait for response
                try:
                    response = await asyncio.wait_for(
                        communicator.receive_json_from(),
                        timeout=10.0
                    )

                    if response.get('type') not in ['metrics_update', 'connection_status']:
                        score -= 20
                        issues.append("Unexpected response format")

                    if not response.get('is_real'):
                        score -= 10
                        issues.append("Not receiving real data")

                except asyncio.TimeoutError:
                    score -= 30
                    issues.append("Revenue Dashboard response timeout")

                await communicator.disconnect()

            self.results[test_name] = {
                'score': score,
                'issues': issues,
                'status': 'pass' if score >= 90 else 'fail'
            }

            if score < 90:
                self.critical_issues.extend(issues)

        except Exception as e:
            self.results[test_name] = {
                'score': 0,
                'error': str(e),
                'status': 'fail'
            }
            self.critical_issues.append(f"Revenue Dashboard WebSocket test failed: {e}")

    async def test_neural_orchestra_websocket(self):
        """Test Neural Orchestra WebSocket specifically"""
        test_name = "neural_orchestra_websocket"
        try:
            from core.asgi import application

            communicator = WebsocketCommunicator(application, '/ws/neural-orchestra/')
            connected, _ = await communicator.connect()

            score = 100.0
            issues = []

            if not connected:
                score = 0
                issues.append("Failed to connect to Neural Orchestra WebSocket")
            else:
                # Test orchestra data request
                await communicator.send_json_to({'type': 'get_orchestra_data'})

                # Wait for response
                try:
                    response = await asyncio.wait_for(
                        communicator.receive_json_from(),
                        timeout=10.0
                    )

                    if not response.get('agents'):
                        score -= 20
                        issues.append("No agent data returned")

                    if len(response.get('agents', [])) < 50:
                        score -= 10
                        issues.append(f"Low agent count: {len(response.get('agents', []))}")

                except asyncio.TimeoutError:
                    score -= 30
                    issues.append("Neural Orchestra response timeout")

                await communicator.disconnect()

            self.results[test_name] = {
                'score': score,
                'issues': issues,
                'status': 'pass' if score >= 90 else 'fail'
            }

            if score < 90:
                self.critical_issues.extend(issues)

        except Exception as e:
            self.results[test_name] = {
                'score': 0,
                'error': str(e),
                'status': 'fail'
            }
            self.critical_issues.append(f"Neural Orchestra WebSocket test failed: {e}")

    async def test_channel_layer_performance(self):
        """Test Django Channels performance"""
        test_name = "channel_layer_performance"
        try:
            from channels.layers import get_channel_layer

            channel_layer = get_channel_layer()

            # Test basic operations
            start_time = time.time()

            # Test group operations
            test_group = "performance_test"
            test_channel = "test.channel.1"

            await channel_layer.group_add(test_group, test_channel)
            await channel_layer.group_send(test_group, {
                'type': 'test.message',
                'data': 'performance_test'
            })
            await channel_layer.group_discard(test_group, test_channel)

            operation_time = (time.time() - start_time) * 1000

            score = 100.0
            issues = []

            if operation_time > 500:  # >500ms is concerning
                score -= 20
                issues.append(f"Slow channel operations: {operation_time:.2f}ms")

            # Check if Redis backend is being used
            backend_type = str(type(channel_layer))
            if 'Redis' not in backend_type:
                score -= 10
                issues.append("Not using Redis channel layer backend")

            self.results[test_name] = {
                'score': score,
                'operation_time_ms': operation_time,
                'backend_type': backend_type,
                'issues': issues,
                'status': 'pass' if score >= 90 else 'fail'
            }

            if score < 90:
                self.critical_issues.extend(issues)

        except Exception as e:
            self.results[test_name] = {
                'score': 0,
                'error': str(e),
                'status': 'fail'
            }
            self.critical_issues.append(f"Channel layer performance test failed: {e}")

    async def test_database_performance(self):
        """Test database performance"""
        test_name = "database_performance"
        try:
            from django.db import connection
            from core.models.agents_registry import UnifiedAgentTemplate

            # Test database query performance
            start_time = time.time()
            agent_count = UnifiedAgentTemplate.objects.filter(is_active=True).count()
            query_time = (time.time() - start_time) * 1000

            score = 100.0
            issues = []

            if query_time > 100:  # >100ms for simple query
                score -= 15
                issues.append(f"Slow database query: {query_time:.2f}ms")

            if agent_count < 50:
                score -= 5
                issues.append(f"Low agent count: {agent_count}")

            # Test connection pooling
            db_settings = connection.settings_dict
            if db_settings.get('CONN_MAX_AGE', 0) < 300:
                score -= 10
                issues.append("Database connection pooling not optimized")

            self.results[test_name] = {
                'score': score,
                'query_time_ms': query_time,
                'agent_count': agent_count,
                'issues': issues,
                'status': 'pass' if score >= 90 else 'fail'
            }

            if score < 90:
                self.critical_issues.extend(issues)

        except Exception as e:
            self.results[test_name] = {
                'score': 0,
                'error': str(e),
                'status': 'fail'
            }
            self.critical_issues.append(f"Database performance test failed: {e}")

    async def test_error_recovery(self):
        """Test error handling and recovery mechanisms"""
        test_name = "error_recovery"
        try:
            score = 100.0
            recovery_tests = []

            # Test WebSocket error handling
            from core.asgi import application
            communicator = WebsocketCommunicator(application, '/ws/revenue-dashboard/')
            connected, _ = await communicator.connect()

            if connected:
                # Send invalid JSON
                await communicator.send_to(text_data="invalid json")

                # Should receive error response
                try:
                    response = await asyncio.wait_for(
                        communicator.receive_json_from(),
                        timeout=5.0
                    )
                    if response.get('type') == 'error':
                        recovery_tests.append(('invalid_json_handling', 'pass'))
                    else:
                        recovery_tests.append(('invalid_json_handling', 'fail'))
                        score -= 20
                except asyncio.TimeoutError:
                    recovery_tests.append(('invalid_json_handling', 'fail'))
                    score -= 20

                await communicator.disconnect()
            else:
                score -= 50
                recovery_tests.append(('websocket_connection', 'fail'))

            self.results[test_name] = {
                'score': score,
                'recovery_tests': recovery_tests,
                'status': 'pass' if score >= 90 else 'fail'
            }

            if score < 90:
                self.critical_issues.append("Error recovery mechanisms insufficient")

        except Exception as e:
            self.results[test_name] = {
                'score': 0,
                'error': str(e),
                'status': 'fail'
            }
            self.critical_issues.append(f"Error recovery test failed: {e}")

    async def test_concurrent_connections(self):
        """Test handling of concurrent WebSocket connections"""
        test_name = "concurrent_connections"
        try:
            from core.asgi import application

            concurrent_count = 10
            communicators = []

            # Create multiple connections
            start_time = time.time()
            for i in range(concurrent_count):
                communicator = WebsocketCommunicator(application, '/ws/revenue-dashboard/')
                connected, _ = await communicator.connect()
                if connected:
                    communicators.append(communicator)

            connection_time = time.time() - start_time

            # Test message broadcasting
            successful_messages = 0
            for communicator in communicators:
                try:
                    await communicator.send_json_to({'type': 'ping', 'timestamp': time.time()})
                    response = await asyncio.wait_for(
                        communicator.receive_json_from(),
                        timeout=5.0
                    )
                    if response:
                        successful_messages += 1
                except Exception as _e:
                    logger.warning(
                        "production_validator.__init__: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

            # Clean up connections
            for communicator in communicators:
                await communicator.disconnect()

            score = 100.0
            issues = []

            success_rate = successful_messages / concurrent_count if concurrent_count > 0 else 0
            if success_rate < 0.9:
                score -= 30
                issues.append(f"Low concurrent message success rate: {success_rate:.2%}")

            if connection_time > 5.0:
                score -= 20
                issues.append(f"Slow concurrent connection time: {connection_time:.2f}s")

            self.results[test_name] = {
                'score': score,
                'concurrent_connections': len(communicators),
                'success_rate': success_rate,
                'connection_time': connection_time,
                'issues': issues,
                'status': 'pass' if score >= 90 else 'fail'
            }

            if score < 90:
                self.critical_issues.extend(issues)

        except Exception as e:
            self.results[test_name] = {
                'score': 0,
                'error': str(e),
                'status': 'fail'
            }
            self.critical_issues.append(f"Concurrent connections test failed: {e}")

    async def test_unified_hub_performance(self):
        """Test Unified Hub performance and reliability"""
        test_name = "unified_hub_performance"
        try:
            from core.unified_hub import UnifiedWebSocketHub

            hub = UnifiedWebSocketHub()

            # Test data retrieval performance
            start_time = time.time()
            revenue_data = await hub.get_real_revenue_data()
            orchestra_data = await hub.get_real_orchestra_data()
            data_fetch_time = (time.time() - start_time) * 1000

            score = 100.0
            issues = []

            if data_fetch_time > 1000:  # >1 second
                score -= 20
                issues.append(f"Slow data fetch: {data_fetch_time:.2f}ms")

            if not revenue_data.get('is_real'):
                score -= 15
                issues.append("Revenue data not marked as real")

            if not orchestra_data.get('is_real'):
                score -= 15
                issues.append("Orchestra data not marked as real")

            agent_count = len(orchestra_data.get('agents', []))
            if agent_count < 50:
                score -= 10
                issues.append(f"Low agent count in orchestra: {agent_count}")

            self.results[test_name] = {
                'score': score,
                'data_fetch_time_ms': data_fetch_time,
                'agent_count': agent_count,
                'revenue_data_real': revenue_data.get('is_real', False),
                'orchestra_data_real': orchestra_data.get('is_real', False),
                'issues': issues,
                'status': 'pass' if score >= 90 else 'fail'
            }

            if score < 90:
                self.critical_issues.extend(issues)

        except Exception as e:
            self.results[test_name] = {
                'score': 0,
                'error': str(e),
                'status': 'fail'
            }
            self.critical_issues.append(f"Unified Hub performance test failed: {e}")

    def calculate_overall_score(self):
        """Calculate overall production readiness score"""
        if not self.results:
            self.overall_score = 0.0
            return

        # Weight different test categories
        weights = {
            'redis_production_config': 0.20,
            'websocket_stability': 0.25,
            'revenue_dashboard_websocket': 0.15,
            'neural_orchestra_websocket': 0.15,
            'channel_layer_performance': 0.10,
            'database_performance': 0.05,
            'error_recovery': 0.05,
            'concurrent_connections': 0.03,
            'unified_hub_performance': 0.02
        }

        total_score = 0.0
        total_weight = 0.0

        for test_name, weight in weights.items():
            if test_name in self.results:
                score = self.results[test_name].get('score', 0)
                total_score += score * weight
                total_weight += weight

        # Normalize score based on completed tests
        if total_weight > 0:
            self.overall_score = total_score / total_weight
        else:
            self.overall_score = 0.0

        # Apply penalty for critical issues
        critical_penalty = min(len(self.critical_issues) * 5, 20)
        self.overall_score = max(0, self.overall_score - critical_penalty)

    def generate_recommendations(self) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []

        if self.overall_score < 95:
            recommendations.append("Platform requires optimization before production deployment")

        if len(self.critical_issues) > 0:
            recommendations.append("Address all critical issues before proceeding")

        # Specific recommendations based on test results
        redis_score = self.results.get('redis_production_config', {}).get('score', 0)
        if redis_score < 90:
            recommendations.append("Optimize Redis configuration for production load")

        websocket_score = self.results.get('websocket_stability', {}).get('score', 0)
        if websocket_score < 90:
            recommendations.append("Improve WebSocket connection stability and error handling")

        if self.overall_score >= 95:
            recommendations.append("Platform ready for production deployment!")
            recommendations.append("Continue monitoring performance metrics")

        return recommendations


# Command line interface
async def run_production_validation():
    """Run production validation and return results"""
    validator = ProductionValidator()
    return await validator.run_full_validation()