"""
Serializers for the Agent Registry API

Session 728: Migrated from agents/serializers.py to core/serializers_agents.py
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

# Session 392: Updated to use canonical import path
from core.models.agents_registry import (
    UnifiedAgentTemplate,
    AgentExecution,
    AgentOrchestration,
    AgentTool,
    AgentRegistry,
    AgentChannel,
    AgentChannelMessage,
    AgentChannelMembership
)

User = get_user_model()


class UnifiedAgentTemplateSerializer(serializers.ModelSerializer):
    """Serializer for agent templates"""
    
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    capability_tags = serializers.SerializerMethodField()
    execution_count = serializers.SerializerMethodField()
    can_handle_task_result = serializers.SerializerMethodField()
    
    class Meta:
        model = UnifiedAgentTemplate
        fields = [
            'id', 'name', 'display_name', 'description', 'specialization',
            'capabilities', 'required_tools', 'optional_tools',
            'system_prompt', 'personality_traits',
            'llm_provider', 'llm_model', 'llm_config',
            'fallback_provider', 'fallback_model',
            'routing_keywords', 'routing_patterns', 'domain_tags',
            'confidence_score', 'avg_completion_time', 'success_rate',
            'usage_count', 'avg_user_rating', 'estimated_cost_per_execution',
            'avg_token_usage', 'resource_requirements',
            'agent_version', 'parent_template', 'is_template', 'is_public',
            'is_verified', 'supports_streaming', 'supports_interruption',
            'supports_collaboration', 'max_concurrent_executions',
            'learning_enabled', 'self_improvement_enabled',
            'collaboration_history', 'creator', 'creator_name', 'organization',
            'created_at', 'updated_at', 'is_active',
            'capability_tags', 'execution_count', 'can_handle_task_result'
        ]
        read_only_fields = [
            'id', 'usage_count', 'success_rate', 'avg_completion_time',
            'avg_user_rating', 'avg_token_usage', 'created_at', 'updated_at',
            'capability_tags', 'execution_count', 'can_handle_task_result'
        ]
    
    def get_capability_tags(self, obj):
        """Get all capability tags for this agent"""
        return obj.get_capability_tags()
    
    def get_execution_count(self, obj):
        """Get total number of executions"""
        return obj.executions.count()
    
    def get_can_handle_task_result(self, obj):
        """Get task handling capability check if task_description provided"""
        request = self.context.get('request')
        if request and 'task_description' in request.query_params:
            task_description = request.query_params['task_description']
            required_capabilities = request.query_params.getlist('required_capabilities')
            can_handle, reason = obj.can_handle_task(task_description, required_capabilities)
            return {
                'can_handle': can_handle,
                'reason': reason
            }
        return None


class UnifiedAgentTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for agent template lists"""
    
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    
    class Meta:
        model = UnifiedAgentTemplate
        fields = [
            'id', 'name', 'display_name', 'specialization',
            'confidence_score', 'success_rate', 'usage_count',
            'avg_user_rating', 'is_public', 'is_verified',
            'llm_provider', 'llm_model', 'creator_name',
            'created_at', 'updated_at', 'is_active'
        ]


class AgentExecutionSerializer(serializers.ModelSerializer):
    """Serializer for agent executions"""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    duration_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = AgentExecution
        fields = [
            'id', 'execution_id', 'template', 'template_name', 'user', 'user_username',
            'task_description', 'task_type', 'context', 'input_data',
            'status', 'status_display', 'priority', 'priority_display',
            'progress_percentage', 'current_step', 'steps_completed',
            'estimated_completion_time', 'result', 'output_files',
            'error_message', 'error_details', 'warnings',
            'started_at', 'completed_at', 'execution_time_seconds',
            'token_usage', 'cost_breakdown', 'total_cost', 'memory_usage_mb',
            'user_rating', 'user_feedback', 'quality_score',
            'parent_orchestration', 'collaboration_context', 'websocket_channel',
            'created_at', 'updated_at', 'duration_display'
        ]
        read_only_fields = [
            'id', 'execution_id', 'template_name', 'user_username',
            'status_display', 'priority_display', 'started_at', 'completed_at',
            'execution_time_seconds', 'created_at', 'updated_at', 'duration_display'
        ]
    
    def get_duration_display(self, obj):
        """Get human-readable duration"""
        if obj.execution_time_seconds is not None:
            minutes = obj.execution_time_seconds // 60
            seconds = obj.execution_time_seconds % 60
            if minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        return None


class AgentExecutionListSerializer(serializers.ModelSerializer):
    """Serializer for execution lists - includes results for frontend display"""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AgentExecution
        fields = [
            'id', 'execution_id', 'template_name', 'user_username',
            'task_description', 'status', 'priority', 'progress_percentage',
            'started_at', 'completed_at', 'execution_time_seconds',
            'total_cost', 'user_rating', 'created_at',
            'result', 'output_data', 'llm_response', 'error_message'
        ]


class AgentOrchestrationSerializer(serializers.ModelSerializer):
    """Serializer for agent orchestrations"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    current_agent_name = serializers.SerializerMethodField()
    execution_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AgentOrchestration
        fields = [
            'id', 'name', 'description', 'user', 'user_username',
            'workflow_definition', 'agent_sequence', 'execution_strategy',
            'status', 'status_display', 'current_agent_index', 'progress_percentage',
            'intermediate_results', 'final_result', 'total_execution_time',
            'total_cost', 'websocket_channel', 'created_at', 'updated_at',
            'current_agent_name', 'execution_count'
        ]
        read_only_fields = [
            'id', 'user_username', 'status_display', 'progress_percentage',
            'intermediate_results', 'final_result', 'total_execution_time',
            'created_at', 'updated_at', 'current_agent_name', 'execution_count'
        ]
    
    def get_current_agent_name(self, obj):
        """Get current agent name"""
        current_agent = obj.get_current_agent()
        return current_agent.name if current_agent else None
    
    def get_execution_count(self, obj):
        """Get number of agent executions in this orchestration"""
        return obj.agent_executions.count()


class AgentToolSerializer(serializers.ModelSerializer):
    """Serializer for agent tools"""
    
    compatible_agent_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AgentTool
        fields = [
            'id', 'name', 'display_name', 'description', 'tool_type',
            'endpoint_url', 'authentication_config', 'tool_config',
            'supported_operations', 'required_permissions',
            'usage_count', 'avg_response_time_ms', 'success_rate',
            'tool_version', 'compatible_agents', 'compatible_agent_count',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = [
            'id', 'usage_count', 'avg_response_time_ms', 'success_rate',
            'created_at', 'updated_at', 'compatible_agent_count'
        ]
    
    def get_compatible_agent_count(self, obj):
        """Get number of compatible agents"""
        return obj.compatible_agents.count()


class AgentRegistrySerializer(serializers.ModelSerializer):
    """Serializer for agent registry"""
    
    class Meta:
        model = AgentRegistry
        fields = [
            'id', 'registry_name', 'description',
            'total_agents', 'active_agents', 'total_executions',
            'capability_index', 'specialization_index', 'keyword_index',
            'avg_success_rate', 'avg_execution_time', 'last_updated',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_agents', 'active_agents', 'total_executions',
            'capability_index', 'specialization_index', 'keyword_index',
            'avg_success_rate', 'avg_execution_time', 'last_updated',
            'created_at', 'updated_at'
        ]


class AgentTaskMatchSerializer(serializers.Serializer):
    """Serializer for agent task matching requests"""
    
    task_description = serializers.CharField(
        help_text="Description of the task to find agents for"
    )
    required_capabilities = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of required capabilities"
    )
    specialization = serializers.CharField(
        required=False,
        help_text="Preferred agent specialization"
    )
    limit = serializers.IntegerField(
        default=5,
        min_value=1,
        max_value=20,
        help_text="Maximum number of agents to return"
    )


class AgentTaskMatchResultSerializer(serializers.Serializer):
    """Serializer for agent task matching results"""
    
    agent_name = serializers.CharField()
    score = serializers.FloatField()
    agent = UnifiedAgentTemplateListSerializer()


class ExecuteAgentSerializer(serializers.Serializer):
    """Serializer for agent execution requests"""
    
    agent_id = serializers.UUIDField(
        help_text="ID of the agent template to execute"
    )
    task_description = serializers.CharField(
        help_text="Description of the task to perform"
    )
    task_type = serializers.CharField(
        required=False,
        help_text="Type/category of the task"
    )
    context = serializers.JSONField(
        default=dict,
        help_text="Additional context for the execution"
    )
    input_data = serializers.JSONField(
        default=dict,
        help_text="Input data for the agent"
    )
    priority = serializers.ChoiceField(
        choices=[
            ('low', 'Low Priority'),
            ('normal', 'Normal Priority'),
            ('high', 'High Priority'),
            ('urgent', 'Urgent Priority'),
            ('critical', 'Critical Priority')
        ],
        default='normal'
    )
    websocket_channel = serializers.CharField(
        required=False,
        help_text="WebSocket channel for real-time updates"
    )


class CreateOrchestrationSerializer(serializers.Serializer):
    """Serializer for orchestration creation requests"""
    
    name = serializers.CharField(max_length=200)
    description = serializers.CharField()
    agent_sequence = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of agent names to execute in order"
    )
    execution_strategy = serializers.ChoiceField(
        choices=[
            ('sequential', 'Sequential Execution'),
            ('parallel', 'Parallel Execution'),
            ('conditional', 'Conditional Execution'),
            ('adaptive', 'Adaptive Execution'),
        ],
        default='sequential'
    )
    workflow_definition = serializers.JSONField(
        help_text="Complete workflow definition"
    )
    websocket_channel = serializers.CharField(
        required=False,
        help_text="WebSocket channel for orchestration updates"
    )


class AgentRegistryStatsSerializer(serializers.Serializer):
    """Serializer for registry statistics"""
    
    total_agents = serializers.IntegerField()
    active_agents = serializers.IntegerField()
    total_executions = serializers.IntegerField()
    total_orchestrations = serializers.IntegerField()
    avg_success_rate = serializers.FloatField()
    avg_execution_time = serializers.IntegerField()
    specialization_breakdown = serializers.DictField()
    provider_breakdown = serializers.DictField()
    recent_activity = serializers.ListField()
    top_performing_agents = serializers.ListField()
    capability_coverage = serializers.DictField()


# =============================================================================
# Agent Channel Serializers - "Slack for AI Agents"
# =============================================================================

class AgentChannelSerializer(serializers.ModelSerializer):
    """Serializer for agent channels"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    message_count = serializers.IntegerField(read_only=True)
    member_count = serializers.SerializerMethodField()
    active_agents = serializers.SerializerMethodField()
    recent_messages = serializers.SerializerMethodField()
    
    class Meta:
        model = AgentChannel
        fields = [
            'id', 'name', 'display_name', 'description', 'channel_type',
            'orchestration', 'is_active', 'is_archived', 'is_public',
            'metadata', 'message_count', 'created_by',
            'created_by_username', 'created_at', 'updated_at',
            'member_count', 'active_agents', 'recent_messages'
        ]
        read_only_fields = [
            'id', 'message_count', 'created_by_username', 
            'created_at', 'updated_at', 'member_count', 
            'active_agents', 'recent_messages'
        ]
    
    def get_member_count(self, obj):
        """Get total number of members in channel"""
        return obj.memberships.count()
    
    def get_active_agents(self, obj):
        """Get count of active agent members"""
        return obj.memberships.filter(agent_template__isnull=False).count()
    
    def get_recent_messages(self, obj):
        """Get last 5 messages preview"""
        recent = obj.messages.order_by('-created_at')[:5]
        return AgentChannelMessageListSerializer(recent, many=True).data


class AgentChannelListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for channel lists"""
    
    message_count = serializers.IntegerField(read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AgentChannel
        fields = [
            'id', 'name', 'display_name', 'description', 'channel_type',
            'is_active', 'message_count', 'member_count',
            'created_at', 'updated_at'
        ]
    
    def get_member_count(self, obj):
        """Get total number of members"""
        return obj.memberships.count()


class AgentChannelMessageSerializer(serializers.ModelSerializer):
    """Serializer for channel messages"""
    
    agent_name = serializers.SerializerMethodField()
    user_username = serializers.CharField(source='user.username', read_only=True)
    channel_name = serializers.CharField(source='channel.name', read_only=True)
    reactions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AgentChannelMessage
        fields = [
            'id', 'channel', 'channel_name', 'message_type',
            'agent_template', 'agent_name', 'user', 'user_username',
            'content', 'rich_content', 'timestamp', 'thread_id',
            'parent_message', 'reactions', 'reactions_count',
            'edited_at', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'channel_name', 'agent_name', 'user_username',
            'timestamp', 'reactions_count', 'created_at', 'updated_at'
        ]
    
    def get_agent_name(self, obj):
        """Get agent template name if agent message"""
        if obj.agent_template:
            return obj.agent_template.display_name or obj.agent_template.name
        return None
    
    def get_reactions_count(self, obj):
        """Get total reaction count"""
        if obj.reactions:
            return sum(len(users) for users in obj.reactions.values())
        return 0


class AgentChannelMessageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for message lists"""
    
    agent_name = serializers.SerializerMethodField()
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AgentChannelMessage
        fields = [
            'id', 'channel', 'message_type', 'agent_name', 'user_username',
            'content', 'timestamp', 'thread_id', 'created_at'
        ]
    
    def get_agent_name(self, obj):
        """Get agent name for quick display"""
        if obj.agent_template:
            return obj.agent_template.name
        return None


class AgentChannelMembershipSerializer(serializers.ModelSerializer):
    """Serializer for channel memberships"""
    
    channel_name = serializers.CharField(source='channel.name', read_only=True)
    agent_name = serializers.SerializerMethodField()
    user_username = serializers.CharField(source='user.username', read_only=True)
    member_display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AgentChannelMembership
        fields = [
            'id', 'channel', 'channel_name', 'agent_template', 'agent_name',
            'user', 'user_username', 'role', 'notification_level',
            'is_watching', 'last_read_at', 'joined_at',
            'is_active', 'metadata', 'created_at', 'updated_at',
            'member_display_name'
        ]
        read_only_fields = [
            'id', 'channel_name', 'agent_name', 'user_username',
            'joined_at', 'created_at', 'updated_at', 'member_display_name'
        ]
    
    def get_agent_name(self, obj):
        """Get agent name if agent membership"""
        if obj.agent_template:
            return obj.agent_template.display_name or obj.agent_template.name
        return None
    
    def get_member_display_name(self, obj):
        """Get display name for the member"""
        if obj.user:
            return obj.user.username
        elif obj.agent_template:
            return obj.agent_template.display_name or obj.agent_template.name
        return "Unknown"


class CreateChannelSerializer(serializers.Serializer):
    """Serializer for creating new channels"""
    
    name = serializers.CharField(
        max_length=100,
        help_text="Unique channel name (e.g., 'general', 'project-x')"
    )
    display_name = serializers.CharField(
        max_length=200,
        help_text="Display name for the channel"
    )
    description = serializers.CharField(
        required=False,
        help_text="Channel description"
    )
    channel_type = serializers.ChoiceField(
        choices=[
            ('project', 'Project Channel'),
            ('topic', 'Topic Channel'),
            ('team', 'Team Channel'),
            ('general', 'General Channel'),
            ('system', 'System Channel'),
            ('orchestration', 'Orchestration Channel'),
        ],
        default='general'
    )
    metadata = serializers.JSONField(
        default=dict,
        help_text="Additional channel metadata"
    )


class PostMessageSerializer(serializers.Serializer):
    """Serializer for posting messages to channels"""
    
    message_type = serializers.ChoiceField(
        choices=[
            ('agent_message', 'Agent Message'),
            ('system_message', 'System Message'),
            ('user_message', 'User Message'),
            ('status_update', 'Status Update'),
            ('task_update', 'Task Update'),
            ('tool_usage', 'Tool Usage'),
            ('collaboration_request', 'Collaboration Request'),
            ('result_share', 'Result Share'),
            ('error_report', 'Error Report'),
        ],
        default='user_message'
    )
    content = serializers.CharField(
        help_text="Message content"
    )
    rich_content = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Rich content (code, links, etc.)"
    )
    thread_id = serializers.CharField(
        required=False,
        help_text="Thread ID for threaded messages"
    )
    parent_message = serializers.UUIDField(
        required=False,
        help_text="Parent message ID for replies"
    )