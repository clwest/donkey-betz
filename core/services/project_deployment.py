# Session 728: Migrated from agents/project_deployment.py
"""
Project Agent Deployment System

This module provides functionality for deploying specific agents to projects,
managing agent assignments, and tracking project-agent relationships.
"""

import uuid
from typing import List, Dict, Any
from datetime import datetime
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models.agents_registry import (
    UnifiedAgentTemplate,
    AgentTaskExecution,
    AgentOrchestration,
    AgentRegistry,
    AgentChannel,
    AgentChannelMessage
)
from core.models import GeneratedProject


class ProjectAgentDeploymentManager:
    """
    Manages the deployment of agents to specific projects
    """

    def __init__(self):
        self.registry = self._get_or_create_registry()

    def _get_or_create_registry(self):
        """Get or create the unified agent registry"""
        registry, _ = AgentRegistry.objects.get_or_create(
            registry_name='unified_agent_registry'
        )
        return registry

    def assign_agents_to_project(
        self,
        project: GeneratedProject,
        agent_names: List[str],
        deployment_strategy: str = 'sequential'
    ) -> AgentOrchestration:
        """
        Assign specific agents to a project and create an orchestration

        Args:
            project: The GeneratedProject instance
            agent_names: List of agent names to deploy
            deployment_strategy: How to execute agents (sequential, parallel, etc.)

        Returns:
            AgentOrchestration instance
        """
        with transaction.atomic():
            # Verify all agents exist and are active
            agents = []
            for agent_name in agent_names:
                try:
                    agent = UnifiedAgentTemplate.objects.get(
                        name=agent_name,
                        is_active=True
                    )
                    agents.append(agent)
                except UnifiedAgentTemplate.DoesNotExist:
                    raise ValidationError(f"Agent '{agent_name}' not found or not active")

            # Create orchestration for the project
            orchestration = AgentOrchestration.objects.create(
                name=f"Project: {project.name} - Agent Deployment",
                description=f"Agent deployment for {project.project_type} project: {project.description}",
                workflow_definition={
                    'project_id': str(project.id),
                    'project_name': project.name,
                    'project_type': project.project_type,
                    'agents': agent_names,
                    'deployment_time': datetime.now().isoformat()
                },
                agent_sequence=agent_names,
                execution_strategy=deployment_strategy,
                user=project.user
            )

            # Update project metadata with agent assignments
            if not project.metadata:
                project.metadata = {}

            project.metadata['assigned_agents'] = agent_names
            project.metadata['orchestration_id'] = str(orchestration.id)
            project.metadata['deployment_strategy'] = deployment_strategy
            project.agents_used.extend(agent_names)
            project.save()

            # Create a project channel for agent communication
            channel = AgentChannel.objects.create(
                name=f"project-{project.id}",
                display_name=f"Project: {project.name}",
                description=f"Agent collaboration channel for {project.name}",
                channel_type='project',
                orchestration=orchestration,
                created_by=project.user,
                metadata={
                    'project_id': str(project.id),
                    'project_type': project.project_type,
                    'agents': agent_names
                }
            )

            # Send initial system message
            AgentChannelMessage.objects.create(
                channel=channel,
                message_type='system_message',
                content=f"Project deployment initiated for '{project.name}' with {len(agents)} agents",
                rich_content={
                    'project': {
                        'id': str(project.id),
                        'name': project.name,
                        'type': project.project_type
                    },
                    'agents': [{'name': a.name, 'specialization': a.specialization} for a in agents]
                }
            )

            return orchestration

    def deploy_ml_agents_to_ecommerce(
        self,
        project: GeneratedProject,
        ml_features: List[str]
    ) -> Dict[str, Any]:
        """
        Deploy ML-specific agents to e-commerce projects

        Args:
            project: The e-commerce project
            ml_features: List of ML features to implement
                        (recommendation, pricing, segmentation, etc.)

        Returns:
            Dictionary with deployment details
        """
        ml_agent_mapping = {
            'recommendation': [
                'ml-recommendation-engine',
                'collaborative-filtering-agent',
                'content-based-recommender'
            ],
            'pricing': [
                'dynamic-pricing-optimizer',
                'market-analysis-agent',
                'price-elasticity-calculator'
            ],
            'segmentation': [
                'customer-segmentation-ml',
                'behavior-analysis-agent',
                'clustering-algorithm-agent'
            ],
            'inventory': [
                'demand-forecasting-agent',
                'inventory-optimization-ml',
                'supply-chain-predictor'
            ],
            'fraud': [
                'fraud-detection-ml',
                'anomaly-detection-agent',
                'transaction-security-validator'
            ]
        }

        # Collect all agents needed for requested features
        agents_to_deploy = []
        feature_agent_map = {}

        for feature in ml_features:
            if feature in ml_agent_mapping:
                feature_agents = ml_agent_mapping[feature]
                agents_to_deploy.extend(feature_agents)
                feature_agent_map[feature] = feature_agents

        # Remove duplicates while preserving order
        agents_to_deploy = list(dict.fromkeys(agents_to_deploy))

        # Create or get ML agents (placeholder - would need actual agent creation)
        created_agents = self._ensure_ml_agents_exist(agents_to_deploy)

        # Deploy agents with parallel strategy for ML tasks
        orchestration = self.assign_agents_to_project(
            project=project,
            agent_names=agents_to_deploy,
            deployment_strategy='parallel'
        )

        # Create ML-specific configuration
        ml_config = {
            'features_requested': ml_features,
            'feature_agent_mapping': feature_agent_map,
            'agents_deployed': agents_to_deploy,
            'orchestration_id': str(orchestration.id),
            'ml_pipeline_config': {
                'data_source': f'/ai_generated_projects/{project.name}/data/',
                'model_output': f'/ai_generated_projects/{project.name}/models/',
                'api_endpoints': [
                    f'/api/ml/{feature}' for feature in ml_features
                ]
            }
        }

        # Update project with ML configuration
        if not project.metadata:
            project.metadata = {}
        project.metadata['ml_configuration'] = ml_config
        project.save()

        return {
            'success': True,
            'orchestration': orchestration,
            'ml_config': ml_config,
            'agents_deployed': len(agents_to_deploy),
            'features_enabled': ml_features
        }

    def _ensure_ml_agents_exist(self, agent_names: List[str]) -> List[UnifiedAgentTemplate]:
        """
        Ensure ML agents exist in the system (create if necessary)

        This is a placeholder that would create actual ML agent templates
        """
        created_agents = []

        for agent_name in agent_names:
            agent, created = UnifiedAgentTemplate.objects.get_or_create(
                name=agent_name,
                defaults={
                    'display_name': agent_name.replace('-', ' ').title(),
                    'description': f"ML Agent for {agent_name.replace('-', ' ')}",
                    'specialization': 'technical',
                    'capabilities': ['machine-learning', 'data-analysis', 'model-training'],
                    'system_prompt': f"You are an ML agent specialized in {agent_name.replace('-', ' ')}",
                    'llm_model': 'gpt-5-mini',
                    'routing_keywords': agent_name.split('-'),
                    'domain_tags': ['ml', 'ai', 'ecommerce']
                }
            )
            created_agents.append(agent)

        return created_agents

    def get_project_agents(self, project: GeneratedProject) -> List[UnifiedAgentTemplate]:
        """
        Get all agents assigned to a project

        Args:
            project: The GeneratedProject instance

        Returns:
            List of UnifiedAgentTemplate instances
        """
        if project.metadata and 'assigned_agents' in project.metadata:
            agent_names = project.metadata['assigned_agents']
            return list(UnifiedAgentTemplate.objects.filter(
                name__in=agent_names,
                is_active=True
            ))
        return []

    def get_agent_recommendations(
        self,
        project: GeneratedProject,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get agent recommendations based on project type and description

        Args:
            project: The GeneratedProject instance
            limit: Maximum number of recommendations

        Returns:
            List of recommended agents with scores
        """
        # Use the registry to find suitable agents
        task_description = f"{project.project_type}: {project.description}"

        # Map project types to capabilities
        project_capabilities_map = {
            'ecommerce': ['api-development', 'database-design', 'payment-integration', 'ml-recommendation'],
            'content_factory': ['content-generation', 'seo-optimization', 'publishing', 'analytics'],
            'crypto_trading': ['market-analysis', 'algorithmic-trading', 'risk-assessment', 'blockchain'],
            'social_media': ['content-creation', 'engagement-analysis', 'scheduling', 'growth-hacking'],
            'saas': ['subscription-management', 'user-authentication', 'billing', 'dashboard-creation']
        }

        required_capabilities = project_capabilities_map.get(
            project.project_type.lower(),
            ['general-development']
        )

        # Find agents using the registry
        recommendations = self.registry.find_agents_for_task(
            task_description=task_description,
            required_capabilities=required_capabilities,
            limit=limit
        )

        return recommendations

    def execute_agent_for_project(
        self,
        project: GeneratedProject,
        agent_name: str,
        task_description: str,
        context: Dict[str, Any] = None
    ) -> AgentTaskExecution:
        """
        Execute a specific agent for a project task

        Args:
            project: The GeneratedProject instance
            agent_name: Name of the agent to execute
            task_description: Description of the task
            context: Additional context for execution

        Returns:
            AgentTaskExecution instance
        """
        # Get the agent template
        try:
            agent = UnifiedAgentTemplate.objects.get(
                name=agent_name,
                is_active=True
            )
        except UnifiedAgentTemplate.DoesNotExist:
            raise ValidationError(f"Agent '{agent_name}' not found or not active")

        # Prepare execution context
        execution_context = {
            'project': {
                'id': str(project.id),
                'name': project.name,
                'type': project.project_type,
                'description': project.description
            },
            'project_files': list(project.code_files.values_list('filename', flat=True))
        }

        if context:
            execution_context.update(context)

        # Create execution
        execution = AgentTaskExecution.objects.create(
            template=agent,
            user=project.user,
            task_description=task_description,
            task_type=f"project_{project.project_type}",
            context=execution_context,
            input_data={
                'project_id': str(project.id),
                'task': task_description
            }
        )

        # Update project metadata
        if not project.metadata:
            project.metadata = {}

        if 'executions' not in project.metadata:
            project.metadata['executions'] = []

        project.metadata['executions'].append({
            'execution_id': execution.execution_id,
            'agent': agent_name,
            'task': task_description,
            'started_at': execution.created_at.isoformat()
        })
        project.save()

        return execution


class ProjectStorageEnhancer:
    """
    Enhances project storage with versioning and metadata tracking
    """

    def __init__(self):
        pass

    def version_project(self, project: GeneratedProject, version_tag: str = None) -> Dict[str, Any]:
        """
        Create a version snapshot of a project

        Args:
            project: The GeneratedProject instance
            version_tag: Optional version tag

        Returns:
            Version information dictionary
        """
        version_info = {
            'version_id': str(uuid.uuid4()),
            'version_tag': version_tag or f"v{project.version}",
            'timestamp': datetime.now().isoformat(),
            'project_state': {
                'name': project.name,
                'type': project.project_type,
                'description': project.description,
                'status': project.status,
                'agents_used': project.agents_used,
                'advisors_consulted': project.advisors_consulted
            },
            'files': []
        }

        # Capture all current files
        for code_file in project.code_files.filter(is_latest=True):
            version_info['files'].append({
                'filename': code_file.filename,
                'file_path': code_file.file_path,
                'language': code_file.language,
                'content_hash': hash(code_file.content),
                'agent_creator': code_file.agent_creator
            })

        # Store version in metadata
        if not project.metadata:
            project.metadata = {}

        if 'versions' not in project.metadata:
            project.metadata['versions'] = []

        project.metadata['versions'].append(version_info)
        project.version += 1
        project.save()

        return version_info

    def track_performance_metrics(
        self,
        project: GeneratedProject,
        metrics: Dict[str, Any]
    ) -> None:
        """
        Track performance metrics for a project

        Args:
            project: The GeneratedProject instance
            metrics: Dictionary of metrics to track
        """
        if not project.metadata:
            project.metadata = {}

        if 'performance_metrics' not in project.metadata:
            project.metadata['performance_metrics'] = []

        metric_entry = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics
        }

        project.metadata['performance_metrics'].append(metric_entry)
        project.save()

    def add_collaboration_log(
        self,
        project: GeneratedProject,
        agent1: str,
        agent2: str,
        interaction_type: str,
        details: Dict[str, Any]
    ) -> None:
        """
        Log agent collaboration events

        Args:
            project: The GeneratedProject instance
            agent1: First agent name
            agent2: Second agent name
            interaction_type: Type of interaction
            details: Interaction details
        """
        if not project.metadata:
            project.metadata = {}

        if 'collaboration_logs' not in project.metadata:
            project.metadata['collaboration_logs'] = []

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agents': [agent1, agent2],
            'interaction_type': interaction_type,
            'details': details
        }

        project.metadata['collaboration_logs'].append(log_entry)
        project.save()