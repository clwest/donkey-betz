"""
Component Data Pipelines - Platform Unification Orchestrator
Establishes data flow between all 7 components for seamless integration.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class ComponentDataPipeline:
    """Establishes data flow between components"""

    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.pipelines = {
            'opportunity_flow': self.create_opportunity_pipeline(),
            'revenue_flow': self.create_revenue_pipeline(),
            'execution_flow': self.create_execution_pipeline(),
            'monitoring_flow': self.create_monitoring_pipeline(),
            'decision_flow': self.create_decision_pipeline()
        }
        self.pipeline_stats = {}

    def create_opportunity_pipeline(self):
        """Spider → Income Builder → Decision Command → Agents → Revenue"""
        return {
            'name': 'opportunity_flow',
            'description': 'Flow opportunities from discovery to revenue generation',
            'source': 'spider_network',
            'stages': [
                {
                    'component': 'income_builder',
                    'action': 'analyze_opportunity',
                    'output': 'scored_opportunity',
                    'timeout': 30
                },
                {
                    'component': 'decision_command',
                    'action': 'create_decision',
                    'output': 'action_plan',
                    'timeout': 15
                },
                {
                    'component': 'neural_orchestra',
                    'action': 'assign_agents',
                    'output': 'agent_assignments',
                    'timeout': 10
                },
                {
                    'component': 'agent_executor',
                    'action': 'execute_plan',
                    'output': 'execution_result',
                    'timeout': 300
                }
            ],
            'destination': 'revenue_dashboard',
            'success_criteria': ['revenue_generated', 'plan_completed'],
            'fallback_actions': ['retry', 'escalate', 'abort']
        }

    def create_revenue_pipeline(self):
        """Execution → Revenue Dashboard → Control Center → Monetization Hub"""
        return {
            'name': 'revenue_flow',
            'description': 'Track revenue from execution to aggregation',
            'source': 'agent_execution',
            'stages': [
                {
                    'component': 'monetization_engine',
                    'action': 'record_revenue',
                    'output': 'revenue_record',
                    'timeout': 5
                },
                {
                    'component': 'revenue_dashboard',
                    'action': 'update_metrics',
                    'output': 'updated_metrics',
                    'timeout': 5
                },
                {
                    'component': 'control_center',
                    'action': 'aggregate_stats',
                    'output': 'system_stats',
                    'timeout': 10
                },
                {
                    'component': 'monetization_hub',
                    'action': 'optimize_streams',
                    'output': 'optimization_plan',
                    'timeout': 15
                }
            ],
            'destination': 'analytics_store',
            'success_criteria': ['metrics_updated', 'stats_aggregated'],
            'fallback_actions': ['retry', 'manual_record']
        }

    def create_execution_pipeline(self):
        """Decision Command → Neural Orchestra → Agents → Results"""
        return {
            'name': 'execution_flow',
            'description': 'Execute decisions through agent orchestration',
            'source': 'decision_command',
            'stages': [
                {
                    'component': 'neural_orchestra',
                    'action': 'prepare_workflow',
                    'output': 'workflow_ready',
                    'timeout': 15
                },
                {
                    'component': 'agent_orchestration',
                    'action': 'execute_workflow',
                    'output': 'workflow_result',
                    'timeout': 300
                },
                {
                    'component': 'result_processor',
                    'action': 'process_results',
                    'output': 'processed_results',
                    'timeout': 30
                }
            ],
            'destination': 'income_builder',
            'success_criteria': ['workflow_completed', 'results_processed'],
            'fallback_actions': ['retry', 'partial_execution', 'abort']
        }

    def create_monitoring_pipeline(self):
        """All Components → Control Center → System Health"""
        return {
            'name': 'monitoring_flow',
            'description': 'Aggregate monitoring data from all components',
            'source': 'all_components',
            'stages': [
                {
                    'component': 'metrics_collector',
                    'action': 'collect_metrics',
                    'output': 'component_metrics',
                    'timeout': 10
                },
                {
                    'component': 'control_center',
                    'action': 'aggregate_metrics',
                    'output': 'system_metrics',
                    'timeout': 15
                },
                {
                    'component': 'health_monitor',
                    'action': 'assess_health',
                    'output': 'health_status',
                    'timeout': 5
                }
            ],
            'destination': 'system_dashboard',
            'success_criteria': ['metrics_collected', 'health_assessed'],
            'fallback_actions': ['partial_collection', 'alert_admin']
        }

    def create_decision_pipeline(self):
        """Revenue Opportunities → Decision Command → Action Plans"""
        return {
            'name': 'decision_flow',
            'description': 'Transform opportunities into actionable decisions',
            'source': 'revenue_opportunities',
            'stages': [
                {
                    'component': 'opportunity_analyzer',
                    'action': 'analyze_opportunity',
                    'output': 'opportunity_analysis',
                    'timeout': 20
                },
                {
                    'component': 'decision_command',
                    'action': 'generate_decision',
                    'output': 'decision_plan',
                    'timeout': 15
                },
                {
                    'component': 'plan_validator',
                    'action': 'validate_plan',
                    'output': 'validated_plan',
                    'timeout': 10
                }
            ],
            'destination': 'neural_orchestra',
            'success_criteria': ['decision_generated', 'plan_validated'],
            'fallback_actions': ['revise_analysis', 'manual_review']
        }

    async def execute_pipeline(self, pipeline_name: str, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete pipeline"""
        pipeline = self.pipelines.get(pipeline_name)
        if not pipeline:
            raise ValueError(f"Unknown pipeline: {pipeline_name}")

        execution_id = f"{pipeline_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Starting pipeline execution: {execution_id}")

        pipeline_start = datetime.now()
        current_data = initial_data
        results = {
            'pipeline_name': pipeline_name,
            'execution_id': execution_id,
            'started_at': pipeline_start.isoformat(),
            'stages_completed': [],
            'success': False,
            'error': None
        }

        try:
            for stage_index, stage in enumerate(pipeline['stages']):
                stage_start = datetime.now()
                logger.info(f"Executing stage {stage_index + 1}/{len(pipeline['stages'])}: {stage['component']}")

                # Execute stage
                stage_result = await self.execute_stage(stage, current_data, execution_id)

                # Check for stage failure
                if not stage_result.get('success', False):
                    await self.handle_stage_failure(pipeline, stage, stage_result, execution_id)
                    results['error'] = stage_result.get('error', 'Stage execution failed')
                    break

                # Update current data with stage output
                current_data.update(stage_result.get('output', {}))

                # Record stage completion
                stage_duration = (datetime.now() - stage_start).total_seconds()
                stage_info = {
                    'stage': stage['component'],
                    'action': stage['action'],
                    'duration': stage_duration,
                    'success': True
                }
                results['stages_completed'].append(stage_info)

                # Notify monitoring
                await self.notify_monitoring(pipeline_name, stage, stage_result, execution_id)

            # Check if all stages completed successfully
            if len(results['stages_completed']) == len(pipeline['stages']):
                results['success'] = True

                # Store final result in destination
                await self.store_result(pipeline['destination'], current_data, execution_id)

                # Notify completion
                await self.notify_pipeline_completion(pipeline_name, current_data, execution_id)

        except Exception as e:
            logger.error(f"Pipeline execution error: {e}")
            results['error'] = str(e)

        # Record execution time
        results['completed_at'] = datetime.now().isoformat()
        results['total_duration'] = (datetime.now() - pipeline_start).total_seconds()
        results['final_data'] = current_data

        # Update pipeline stats
        await self.update_pipeline_stats(pipeline_name, results)

        logger.info(f"Pipeline execution completed: {execution_id}, Success: {results['success']}")
        return results

    async def execute_stage(self, stage: Dict[str, Any], input_data: Dict[str, Any],
                           execution_id: str) -> Dict[str, Any]:
        """Execute a single pipeline stage"""
        component = stage['component']
        action = stage['action']
        timeout = stage.get('timeout', 30)

        try:
            # Route stage execution based on component
            if component == 'income_builder':
                return await self.execute_income_builder_stage(action, input_data, execution_id)
            elif component == 'decision_command':
                return await self.execute_decision_command_stage(action, input_data, execution_id)
            elif component == 'neural_orchestra':
                return await self.execute_neural_orchestra_stage(action, input_data, execution_id)
            elif component == 'revenue_dashboard':
                return await self.execute_revenue_dashboard_stage(action, input_data, execution_id)
            elif component == 'control_center':
                return await self.execute_control_center_stage(action, input_data, execution_id)
            elif component == 'monetization_engine':
                return await self.execute_monetization_stage(action, input_data, execution_id)
            else:
                return await self.execute_generic_stage(component, action, input_data, execution_id)

        except asyncio.TimeoutError:
            return {
                'success': False,
                'error': f'Stage timeout after {timeout} seconds',
                'component': component,
                'action': action
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'component': component,
                'action': action
            }

    async def execute_income_builder_stage(self, action: str, input_data: Dict[str, Any],
                                         execution_id: str) -> Dict[str, Any]:
        """Execute Income Builder stage"""
        try:
            if action == 'analyze_opportunity':
                # Use real Income Builder analysis
                from backend.intelligence.income_builder import income_builder

                opportunity = input_data.get('opportunity', {})
                analysis = await income_builder.analyze_user_potential(opportunity)

                return {
                    'success': True,
                    'output': {
                        'analyzed_opportunity': analysis,
                        'score': analysis.get('success_probability', 0),
                        'recommendations': analysis.get('recommended_path', [])
                    }
                }

            return {'success': False, 'error': f'Unknown Income Builder action: {action}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def execute_neural_orchestra_stage(self, action: str, input_data: Dict[str, Any],
                                           execution_id: str) -> Dict[str, Any]:
        """Execute Neural Orchestra stage"""
        try:
            if action == 'assign_agents':
                # Get appropriate agents for the task
                agents = await self.get_suitable_agents(input_data)

                return {
                    'success': True,
                    'output': {
                        'assigned_agents': agents,
                        'workflow_id': f"workflow_{execution_id}",
                        'estimated_duration': 300
                    }
                }

            elif action == 'prepare_workflow':
                # Prepare agent workflow
                workflow = await self.prepare_agent_workflow(input_data)

                return {
                    'success': True,
                    'output': {
                        'workflow': workflow,
                        'ready': True
                    }
                }

            return {'success': False, 'error': f'Unknown Neural Orchestra action: {action}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    @database_sync_to_async
    def get_suitable_agents(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get suitable agents for the task"""
        try:
            from agents.models import UnifiedAgentTemplate

            # Get agents based on task requirements
            task_type = input_data.get('task_type', 'general')

            agents = UnifiedAgentTemplate.objects.filter(
                is_active=True,
                success_rate__gte=60  # Only agents with good success rate
            ).order_by('-success_rate')[:5]

            return [
                {
                    'id': str(agent.id),
                    'name': agent.name,
                    'specialization': agent.specialization,
                    'success_rate': agent.success_rate,
                    'estimated_time': 30
                }
                for agent in agents
            ]

        except Exception as e:
            logger.error(f"Error getting suitable agents: {e}")
            return []

    async def notify_monitoring(self, pipeline_name: str, stage: Dict[str, Any],
                              result: Dict[str, Any], execution_id: str):
        """Notify monitoring system of stage completion"""
        try:
            await self.channel_layer.group_send(
                'unified_component_control_center',
                {
                    'type': 'pipeline_stage_update',
                    'pipeline_name': pipeline_name,
                    'stage': stage['component'],
                    'action': stage['action'],
                    'success': result.get('success', False),
                    'execution_id': execution_id,
                    'timestamp': datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error notifying monitoring: {e}")

    async def notify_pipeline_completion(self, pipeline_name: str, final_data: Dict[str, Any],
                                       execution_id: str):
        """Notify all components of pipeline completion"""
        try:
            # Notify all components about pipeline completion
            components = ['income_builder', 'revenue_dashboard', 'neural_orchestra',
                         'control_center', 'decision_command']

            for component in components:
                await self.channel_layer.group_send(
                    f'unified_component_{component}',
                    {
                        'type': 'pipeline_completed',
                        'pipeline_name': pipeline_name,
                        'execution_id': execution_id,
                        'data': final_data,
                        'timestamp': datetime.now().isoformat()
                    }
                )

        except Exception as e:
            logger.error(f"Error notifying pipeline completion: {e}")

    async def store_result(self, destination: str, data: Dict[str, Any], execution_id: str):
        """Store pipeline result in destination"""
        try:
            # Store results based on destination
            if destination == 'revenue_dashboard':
                await self.store_revenue_result(data, execution_id)
            elif destination == 'analytics_store':
                await self.store_analytics_result(data, execution_id)
            elif destination == 'system_dashboard':
                await self.store_system_result(data, execution_id)
            else:
                logger.info(f"Storing result in {destination}: {execution_id}")

        except Exception as e:
            logger.error(f"Error storing result: {e}")

    async def update_pipeline_stats(self, pipeline_name: str, results: Dict[str, Any]):
        """Update pipeline performance statistics"""
        try:
            if pipeline_name not in self.pipeline_stats:
                self.pipeline_stats[pipeline_name] = {
                    'total_executions': 0,
                    'successful_executions': 0,
                    'failed_executions': 0,
                    'average_duration': 0,
                    'last_execution': None
                }

            stats = self.pipeline_stats[pipeline_name]
            stats['total_executions'] += 1
            stats['last_execution'] = results['completed_at']

            if results['success']:
                stats['successful_executions'] += 1
            else:
                stats['failed_executions'] += 1

            # Update average duration
            duration = results.get('total_duration', 0)
            current_avg = stats['average_duration']
            total_exec = stats['total_executions']
            stats['average_duration'] = ((current_avg * (total_exec - 1)) + duration) / total_exec

            logger.info(f"Updated stats for {pipeline_name}: {stats}")

        except Exception as e:
            logger.error(f"Error updating pipeline stats: {e}")

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline performance statistics"""
        return self.pipeline_stats

    async def handle_stage_failure(self, pipeline: Dict[str, Any], stage: Dict[str, Any],
                                 result: Dict[str, Any], execution_id: str):
        """Handle stage failure with fallback actions"""
        try:
            fallback_actions = pipeline.get('fallback_actions', ['abort'])

            for action in fallback_actions:
                if action == 'retry':
                    # Implement retry logic
                    logger.info(f"Retrying failed stage: {stage['component']}")
                    # Could implement actual retry here
                    break
                elif action == 'escalate':
                    # Escalate to manual intervention
                    await self.escalate_failure(pipeline, stage, result, execution_id)
                    break
                elif action == 'abort':
                    # Abort pipeline execution
                    logger.error(f"Aborting pipeline due to stage failure: {execution_id}")
                    break

        except Exception as e:
            logger.error(f"Error handling stage failure: {e}")

    async def escalate_failure(self, pipeline: Dict[str, Any], stage: Dict[str, Any],
                             result: Dict[str, Any], execution_id: str):
        """Escalate pipeline failure for manual intervention"""
        try:
            await self.channel_layer.group_send(
                'unified_component_control_center',
                {
                    'type': 'pipeline_failure_escalation',
                    'pipeline_name': pipeline['name'],
                    'failed_stage': stage['component'],
                    'error': result.get('error', 'Unknown error'),
                    'execution_id': execution_id,
                    'requires_intervention': True,
                    'timestamp': datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error escalating failure: {e}")


# Global pipeline manager instance
pipeline_manager = ComponentDataPipeline()


# Pipeline execution functions for easy access
async def execute_opportunity_pipeline(opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute opportunity discovery to revenue pipeline"""
    return await pipeline_manager.execute_pipeline('opportunity_flow', opportunity_data)

async def execute_revenue_pipeline(execution_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute revenue tracking pipeline"""
    return await pipeline_manager.execute_pipeline('revenue_flow', execution_data)

async def execute_monitoring_pipeline() -> Dict[str, Any]:
    """Execute system monitoring pipeline"""
    return await pipeline_manager.execute_pipeline('monitoring_flow', {})

async def get_pipeline_health() -> Dict[str, Any]:
    """Get health status of all pipelines"""
    return {
        'stats': pipeline_manager.get_pipeline_stats(),
        'active_pipelines': list(pipeline_manager.pipelines.keys()),
        'last_updated': datetime.now().isoformat()
    }