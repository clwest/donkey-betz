"""
Internal Data Source Registry
==============================

Session 866: Provides agents with knowledge of internal DonkeyBetz data sources.

Problem: Agents ask for "BigQuery access" or "Snowflake export" when the data
exists in our own database. This registry teaches agents what internal data
sources are available and how to query them.

Usage:
    from core.services.internal_data_registry import (
        get_internal_data_registry,
        get_data_source_for_topic,
        build_agent_data_context
    )

    # Get all available sources
    registry = get_internal_data_registry()

    # Find relevant sources for a topic
    sources = get_data_source_for_topic("failed experiments")

    # Build context string for agent prompts
    context = build_agent_data_context("experiment analysis")
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# INTERNAL DATA SOURCE REGISTRY
# =============================================================================

INTERNAL_DATA_REGISTRY: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # EXPERIMENT & EXECUTION DATA
    # Session 882: Fixed to match actual schema (was using non-existent ExperimentExecution model)
    # =========================================================================
    'experiments': {
        'name': 'Experiments',
        'model': 'core.models.Experiment',
        'description': 'All experiment runs including A/B tests and agent experiments',
        'keywords': ['experiment', 'a/b test', 'variant', 'control', 'treatment', 'halt', 'failed'],
        'query_examples': [
            "Experiment.objects.filter(status='failure').order_by('-created_at')[:20]",
            "Experiment.objects.filter(is_halted=True).order_by('-halted_at')[:20]",
            "Experiment.objects.filter(created_at__gte=timezone.now()-timedelta(days=7))",
            "Experiment.objects.values('status').annotate(cnt=Count('id'))",
        ],
        'key_fields': [
            ('id', 'UUID', 'Unique experiment identifier'),
            ('name', 'str', 'Experiment name'),
            ('hypothesis', 'text', 'Experiment hypothesis'),
            ('status', 'str', 'running/success/failure/partial/inconclusive'),
            ('is_halted', 'bool', 'Whether experiment was halted'),
            ('halted_by', 'str', 'Who/what halted: auto/manual/system'),
            ('halt_reason', 'text', 'Why experiment was halted'),
            ('result_summary', 'text', 'Summary of results'),
            ('learnings', 'text', 'Key learnings extracted'),
            ('extracted_metrics', 'JSON', 'Experiment metrics and results'),
            ('halt_conditions', 'JSON', 'Conditions that trigger halt'),
            ('primary_kpi', 'str', 'Primary KPI being measured'),
            ('created_at', 'datetime', 'When experiment was created'),
            ('started_at', 'datetime', 'When experiment started running'),
            ('ended_at', 'datetime', 'When experiment ended'),
        ],
        'related_models': ['ExperimentLearning', 'ABExperiment'],
        'access_pattern': 'direct_query',
        'status_values': ['running', 'success', 'failure', 'partial', 'inconclusive'],
    },

    'agent_executions': {
        'name': 'Agent Execution Logs',
        'model': 'core.models.AgentExecution',
        'description': 'Every agent task execution with timing, success/failure, and output',
        'keywords': ['agent', 'execution', 'task', 'failed', 'error', 'performance', 'timing'],
        # Session 882: Fixed to match actual schema
        'query_examples': [
            "AgentExecution.objects.filter(status='failed').order_by('-created_at')[:50]",
            "AgentExecution.objects.filter(agent__name='ResearchAgent', created_at__gte=last_week)",
            "AgentExecution.objects.values('agent__name').annotate(avg_time=Avg('execution_time_ms'))",
            "AgentExecution.objects.values('status').annotate(cnt=Count('id'))",
        ],
        'key_fields': [
            ('id', 'UUID', 'Execution ID'),
            ('agent', 'FK', 'Foreign key to Agent model'),
            ('user', 'FK', 'Foreign key to User who triggered'),
            ('experiment', 'FK', 'Foreign key to Experiment if part of one'),
            ('task', 'text', 'Task description'),
            ('status', 'str', 'completed/failed/in_progress'),
            ('error_message', 'text', 'Error details if failed'),
            ('execution_time_ms', 'int', 'How long it took in milliseconds'),
            ('tokens_used', 'int', 'LLM tokens consumed'),
            ('cost', 'decimal', 'Cost of execution'),
            ('input_data', 'JSON', 'Input provided to agent'),
            ('output_data', 'JSON', 'Agent output'),
            ('created_at', 'datetime', 'When execution started'),
            ('completed_at', 'datetime', 'When execution finished'),
        ],
        'related_models': ['Agent', 'User', 'Experiment'],
        'access_pattern': 'direct_query',
        'status_values': ['completed', 'failed', 'in_progress'],
    },

    # =========================================================================
    # CONTENT & RESEARCH DATA
    # =========================================================================
    'research_briefs': {
        'name': 'Research Briefs',
        'model': 'core.models_unified_system.SelfBlog',
        'description': 'Auto-generated research reports and briefs (category=research_brief)',
        'keywords': ['research', 'brief', 'report', 'analysis', 'findings'],
        'query_examples': [
            "SelfBlog.objects.filter(category='research_brief').order_by('-created_at')[:20]",
            "SelfBlog.objects.filter(category='research_brief', stats_snapshot__parent_topic__icontains='experiment')",
        ],
        'key_fields': [
            ('id', 'UUID', 'Research brief ID'),
            ('title', 'str', 'Research title'),
            ('full_text', 'text', 'Full research content'),
            ('stats_snapshot', 'JSON', 'Metadata including parent_topic, deliverables'),
            ('quality_score', 'float', 'Content quality 0-1'),
            ('created_at', 'datetime', 'When created'),
        ],
        'filter_hint': "category='research_brief'",
        'access_pattern': 'direct_query',
    },

    'content_blogs': {
        'name': 'Content & Blogs',
        'model': 'core.models_unified_system.SelfBlog',
        'description': 'All blog posts and content pieces',
        'keywords': ['blog', 'content', 'article', 'post', 'publish'],
        'query_examples': [
            "SelfBlog.objects.filter(category='blog').order_by('-created_at')",
            "SelfBlog.objects.filter(publish_status='published')",
            "SelfBlog.objects.filter(quality_score__lt=0.6, needs_enhancement=True)",
        ],
        'key_fields': [
            ('id', 'UUID', 'Content ID'),
            ('title', 'str', 'Content title'),
            ('category', 'str', 'blog/research_brief/internal'),
            ('publish_status', 'str', 'draft/internal/published'),
            ('quality_score', 'float', 'Quality 0-1'),
            ('novelty_score', 'float', 'Uniqueness 0-1'),
            ('structure_score', 'float', 'Structure quality 0-1'),
            ('needs_enhancement', 'bool', 'Flagged for improvement'),
        ],
        'access_pattern': 'direct_query',
    },

    'deliverables': {
        'name': 'Deliverables',
        'model': 'core.models_unified_system.Deliverable',
        'description': 'Formal deliverables from initiatives and projects',
        'keywords': ['deliverable', 'output', 'artifact', 'document', 'stage'],
        'query_examples': [
            "Deliverable.objects.filter(initiative__isnull=False).select_related('initiative')",
            "Deliverable.objects.filter(stage=3, status='completed')",
        ],
        'key_fields': [
            ('id', 'UUID', 'Deliverable ID'),
            ('title', 'str', 'Deliverable name'),
            ('stage', 'int', 'Pipeline stage 1-5'),
            ('status', 'str', 'pending/in_progress/completed'),
            ('content', 'text', 'Deliverable content'),
            ('initiative', 'FK', 'Parent initiative'),
        ],
        'access_pattern': 'direct_query',
    },

    # =========================================================================
    # SPIDER & EXTERNAL DATA
    # =========================================================================
    'spider_data': {
        'name': 'Spider Collected Data',
        'model': 'core.models.SpiderData',
        'description': 'All data collected by the 77 spiders from external sources',
        'keywords': ['spider', 'crawl', 'scrape', 'external', 'news', 'feed', 'source'],
        'query_examples': [
            "SpiderData.objects.filter(spider_name='hackernews').order_by('-created_at')[:100]",
            "SpiderData.objects.filter(created_at__gte=last_24h).values('spider_name').annotate(count=Count('id'))",
            "SpiderData.objects.filter(category='tech', quality_score__gte=0.7)",
        ],
        'key_fields': [
            ('id', 'UUID', 'Data record ID'),
            ('spider_name', 'str', 'Which spider collected this'),
            ('source_url', 'str', 'Original source URL'),
            ('title', 'str', 'Content title'),
            ('content', 'text', 'Collected content'),
            ('category', 'str', 'Content category'),
            ('quality_score', 'float', 'Data quality 0-1'),
            ('created_at', 'datetime', 'When collected'),
        ],
        'access_pattern': 'direct_query',
    },

    'business_research': {
        'name': 'Business Research Results',
        'model': 'core.models.BusinessResearchResult',
        'description': 'Structured business research (market, competitor, customer analysis)',
        'keywords': ['market', 'competitor', 'customer', 'business', 'research', 'analysis'],
        'query_examples': [
            "BusinessResearchResult.objects.filter(research_type='market_analysis')",
            "BusinessResearchResult.objects.filter(research_type='competitor', company__icontains='OpenAI')",
        ],
        'key_fields': [
            ('id', 'UUID', 'Research ID'),
            ('research_type', 'str', 'market_analysis/competitor/customer/industry'),
            ('subject', 'str', 'What was researched'),
            ('findings', 'JSON', 'Research findings'),
            ('confidence_score', 'float', 'Confidence 0-1'),
            ('created_at', 'datetime', 'When researched'),
        ],
        'access_pattern': 'direct_query',
    },

    # =========================================================================
    # INITIATIVE & PROJECT DATA
    # =========================================================================
    'initiatives': {
        'name': 'Initiatives (Projects)',
        'model': 'core.models_initiative.Initiative',
        'description': '5-stage project pipeline from idea to completion',
        'keywords': ['initiative', 'project', 'pipeline', 'stage', 'dream', 'goal'],
        'query_examples': [
            "Initiative.objects.filter(status='active').order_by('-priority')",
            "Initiative.objects.filter(current_stage__lt=5, blocked=False)",
            "Initiative.objects.annotate(doc_count=Count('documents'))",
        ],
        'key_fields': [
            ('id', 'UUID', 'Initiative ID'),
            ('title', 'str', 'Initiative name'),
            ('description', 'text', 'What this initiative aims to achieve'),
            ('current_stage', 'int', 'Current pipeline stage 1-5'),
            ('status', 'str', 'active/paused/completed/abandoned'),
            ('priority', 'int', 'Priority ranking'),
            ('blocked', 'bool', 'Whether blocked'),
            ('block_reason', 'str', 'Why blocked'),
        ],
        'related_models': ['InitiativeStage', 'Deliverable', 'SelfBlog'],
        'access_pattern': 'direct_query',
    },

    'conceptforge_runs': {
        'name': 'ConceptForge Pipeline Runs',
        'model': 'core.models_conceptforge.ConceptForgeRun',
        'description': '6-stage autonomous think tank pipeline (Research→Debate→Feasibility→Risk→Market→Synthesis)',
        'keywords': ['conceptforge', 'dossier', 'think tank', 'feasibility', 'risk', 'debate'],
        'query_examples': [
            "ConceptForgeRun.objects.filter(status='completed').order_by('-created_at')",
            "ConceptForgeRun.objects.filter(status='failed').values('current_stage', 'error')",
        ],
        'key_fields': [
            ('id', 'UUID', 'Run ID'),
            ('source_title', 'str', 'What was analyzed'),
            ('domain', 'str', 'Domain (tech/legal/market/etc)'),
            ('status', 'str', 'pending/running/completed/failed'),
            ('current_stage', 'str', 'Which stage'),
            ('quality_score', 'float', 'Output quality'),
            ('duration_ms', 'int', 'Total runtime'),
        ],
        'related_models': ['ConceptForgeStageRun', 'ConceptForgeArtifact'],
        'access_pattern': 'direct_query',
    },

    # =========================================================================
    # LEARNING & FEEDBACK DATA
    # =========================================================================
    'agent_learnings': {
        'name': 'Agent Learning Records',
        'model': 'core.models.AgentLearning',
        'description': 'What agents have learned from executions and feedback',
        'keywords': ['learning', 'pattern', 'improvement', 'feedback', 'success', 'failure'],
        'query_examples': [
            "AgentLearning.objects.filter(learning_type='success_pattern').order_by('-created_at')",
            "AgentLearning.objects.filter(agent_name='ThinkingAgent', applied=True)",
        ],
        'key_fields': [
            ('id', 'UUID', 'Learning ID'),
            ('agent_name', 'str', 'Which agent learned'),
            ('learning_type', 'str', 'success_pattern/failure_pattern/optimization'),
            ('description', 'text', 'What was learned'),
            ('confidence', 'float', 'Confidence 0-1'),
            ('applied', 'bool', 'Whether applied to agent'),
        ],
        'access_pattern': 'direct_query',
    },

    'decision_records': {
        'name': 'Decision Records',
        'model': 'core.models_feedback_processing.DecisionRecord',
        'description': 'Autonomous decisions made by the system',
        'keywords': ['decision', 'autonomous', 'choice', 'action', 'reasoning'],
        'query_examples': [
            "DecisionRecord.objects.filter(decision_type='auto_halt').order_by('-created_at')",
            "DecisionRecord.objects.filter(outcome='negative', created_at__gte=last_week)",
        ],
        'key_fields': [
            ('id', 'UUID', 'Decision ID'),
            ('decision_type', 'str', 'Type of decision'),
            ('context', 'JSON', 'Decision context'),
            ('reasoning', 'text', 'Why this decision was made'),
            ('outcome', 'str', 'positive/negative/neutral'),
            ('created_at', 'datetime', 'When decided'),
        ],
        'access_pattern': 'direct_query',
    },

    'tool_call_records': {
        'name': 'Tool Call Records',
        'model': 'core.models_feedback_processing.ToolCallRecord',
        'description': 'Every tool call made by agents',
        'keywords': ['tool', 'call', 'api', 'function', 'invocation'],
        'query_examples': [
            "ToolCallRecord.objects.filter(tool_name='web_search').order_by('-created_at')",
            "ToolCallRecord.objects.filter(success=False).values('tool_name').annotate(failures=Count('id'))",
        ],
        'key_fields': [
            ('id', 'UUID', 'Record ID'),
            ('tool_name', 'str', 'Which tool was called'),
            ('agent_name', 'str', 'Which agent called it'),
            ('input_params', 'JSON', 'Tool input'),
            ('output', 'JSON', 'Tool output'),
            ('success', 'bool', 'Whether succeeded'),
            ('duration_ms', 'int', 'Call duration'),
        ],
        'access_pattern': 'direct_query',
    },

    # =========================================================================
    # USER & CONVERSATION DATA
    # =========================================================================
    'conversations': {
        'name': 'Conversations',
        'model': 'core.models.Conversation',
        'description': 'User conversations with agents',
        'keywords': ['conversation', 'chat', 'message', 'user', 'dialogue'],
        'query_examples': [
            "Conversation.objects.filter(status='completed').order_by('-created_at')",
            "Conversation.objects.filter(user=user, agent_name='PersonalAssistant')",
        ],
        'key_fields': [
            ('id', 'UUID', 'Conversation ID'),
            ('user', 'FK', 'User who conversed'),
            ('agent_name', 'str', 'Primary agent'),
            ('status', 'str', 'active/completed/abandoned'),
            ('message_count', 'int', 'Number of messages'),
            ('satisfaction_score', 'float', 'User satisfaction'),
        ],
        'access_pattern': 'direct_query',
    },

    'user_profiles': {
        'name': 'Extended User Profiles',
        'model': 'core.models.ExtendedUserProfile',
        'description': 'User skills, preferences, and goals',
        'keywords': ['user', 'profile', 'skills', 'preferences', 'goals'],
        'query_examples': [
            "ExtendedUserProfile.objects.filter(skills__contains=['python'])",
            "ExtendedUserProfile.objects.filter(income_goal__gte=5000)",
        ],
        'key_fields': [
            ('user', 'FK', 'User'),
            ('skills', 'JSON', 'User skills list'),
            ('experience', 'JSON', 'Work experience'),
            ('preferences', 'JSON', 'User preferences'),
            ('income_goal', 'decimal', 'Monthly income goal'),
        ],
        'access_pattern': 'direct_query',
    },

    # =========================================================================
    # WORKSPACE & OPERATIONS DATA
    # =========================================================================
    'workspace_operations': {
        'name': 'Workspace Operations',
        'model': 'core.models_workspace.WorkspaceOperation',
        'description': 'File operations performed by agents in workspaces',
        'keywords': ['workspace', 'file', 'operation', 'edit', 'create', 'delete', 'rollback'],
        'query_examples': [
            "WorkspaceOperation.objects.filter(success=False).order_by('-created_at')",
            "WorkspaceOperation.objects.filter(operation_type='edit', pending_review=True)",
            "WorkspaceOperation.objects.filter(agent_name='FullStackDeveloperAgent')",
        ],
        'key_fields': [
            ('id', 'UUID', 'Operation ID'),
            ('operation_type', 'str', 'create/edit/delete'),
            ('file_path', 'str', 'File affected'),
            ('agent_name', 'str', 'Agent that performed'),
            ('success', 'bool', 'Whether succeeded'),
            ('pending_review', 'bool', 'Needs human review'),
            ('can_rollback', 'bool', 'Can be undone'),
            ('diff', 'text', 'Change diff'),
        ],
        'access_pattern': 'direct_query',
    },

    # =========================================================================
    # PODCAST & MEDIA DATA
    # =========================================================================
    'podcast_episodes': {
        'name': 'Podcast Episodes',
        'model': 'core.models_podcast_studio.PodcastEpisode',
        'description': 'Generated podcast episodes with scripts and audio',
        'keywords': ['podcast', 'episode', 'audio', 'script', 'tts', 'voice'],
        'query_examples': [
            "PodcastEpisode.objects.filter(audio_url__isnull=False).order_by('-created_at')",
            "PodcastEpisode.objects.filter(script__isnull=False, audio_url__isnull=True)",
        ],
        'key_fields': [
            ('id', 'UUID', 'Episode ID'),
            ('title', 'str', 'Episode title'),
            ('script', 'text', 'Episode script'),
            ('audio_url', 'str', 'Generated audio URL'),
            ('duration_seconds', 'int', 'Audio duration'),
            ('status', 'str', 'draft/scripted/recorded/published'),
        ],
        'access_pattern': 'direct_query',
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_internal_data_registry() -> Dict[str, Dict[str, Any]]:
    """Get the complete internal data registry."""
    return INTERNAL_DATA_REGISTRY


def get_data_source_for_topic(topic: str) -> List[Dict[str, Any]]:
    """
    Find relevant internal data sources for a given topic.

    Args:
        topic: The research topic or query

    Returns:
        List of matching data source definitions
    """
    topic_lower = topic.lower()
    matches = []

    for source_key, source_def in INTERNAL_DATA_REGISTRY.items():
        # Check keywords
        keyword_match = any(kw in topic_lower for kw in source_def.get('keywords', []))

        # Check name and description
        name_match = source_def.get('name', '').lower() in topic_lower or \
                     any(word in source_def.get('name', '').lower() for word in topic_lower.split())
        desc_match = any(word in source_def.get('description', '').lower() for word in topic_lower.split() if len(word) > 3)

        if keyword_match or name_match or desc_match:
            matches.append({
                'key': source_key,
                **source_def,
                'relevance': 'high' if keyword_match else 'medium'
            })

    # Sort by relevance
    matches.sort(key=lambda x: 0 if x['relevance'] == 'high' else 1)
    return matches


def build_agent_data_context(topic: str, max_sources: int = 5) -> str:
    """
    Build a context string for agent prompts explaining available internal data.

    Args:
        topic: The research topic
        max_sources: Maximum number of sources to include

    Returns:
        Formatted context string for agent prompts
    """
    sources = get_data_source_for_topic(topic)[:max_sources]

    if not sources:
        return ""

    context_parts = [
        "## Available Internal Data Sources",
        "",
        "You have DIRECT ACCESS to the following DonkeyBetz database tables.",
        "DO NOT ask for BigQuery, Snowflake, or CSV exports - query these directly:",
        "",
    ]

    for source in sources:
        context_parts.append(f"### {source['name']}")
        context_parts.append(f"**Model:** `{source['model']}`")
        context_parts.append(f"**Description:** {source['description']}")
        context_parts.append("")
        context_parts.append("**Example Queries:**")
        for example in source.get('query_examples', [])[:2]:
            context_parts.append(f"```python\n{example}\n```")
        context_parts.append("")
        context_parts.append("**Key Fields:**")
        for field_name, field_type, field_desc in source.get('key_fields', [])[:5]:
            context_parts.append(f"- `{field_name}` ({field_type}): {field_desc}")
        context_parts.append("")

    return "\n".join(context_parts)


def get_query_for_request(request_type: str, **kwargs) -> Optional[str]:
    """
    Generate a Django ORM query string for common request types.

    Args:
        request_type: Type of data request
        **kwargs: Additional parameters

    Returns:
        Query string or None if not recognized
    """
    # Session 882: Fixed to use correct model and field names
    query_templates = {
        'failed_experiments': (
            "Experiment.objects.filter(status='failure')"
            ".order_by('-created_at')[:{limit}]"
        ),
        'recent_agent_errors': (
            "AgentExecution.objects.filter(status='failed', created_at__gte=timezone.now()-timedelta(days={days}))"
            ".order_by('-created_at')"
        ),
        'halted_experiments': (
            "Experiment.objects.filter(is_halted=True)"
            ".order_by('-halted_at')[:{limit}]"
        ),
        'low_quality_content': (
            "SelfBlog.objects.filter(quality_score__lt={threshold}, category='blog')"
            ".order_by('quality_score')"
        ),
        'blocked_initiatives': (
            "Initiative.objects.filter(blocked=True)"
            ".order_by('-priority')"
        ),
        'recent_spider_data': (
            "SpiderData.objects.filter(created_at__gte=timezone.now()-timedelta(hours={hours}))"
            ".values('spider_name').annotate(count=Count('id'))"
        ),
    }

    template = query_templates.get(request_type)
    if template:
        # Apply default values
        defaults = {'limit': 20, 'days': 7, 'threshold': 0.6, 'hours': 24}
        params = {**defaults, **kwargs}
        return template.format(**params)
    return None


# =============================================================================
# INTEGRATION WITH RESEARCH AGENT
# =============================================================================

def inject_data_context_into_prompt(original_prompt: str, topic: str) -> str:
    """
    Inject internal data source context into an agent prompt.

    This helps agents understand they can query internal data directly
    instead of asking for external database access.

    Args:
        original_prompt: The original agent prompt
        topic: The research topic

    Returns:
        Enhanced prompt with data context
    """
    data_context = build_agent_data_context(topic)

    if not data_context:
        return original_prompt

    # Insert data context before the main task
    enhanced_prompt = f"""{data_context}

---

{original_prompt}

---

**IMPORTANT:** Use the internal data sources listed above. Do NOT request BigQuery,
Snowflake, CSV exports, or external database access. You have direct Django ORM
access to all DonkeyBetz data.
"""

    return enhanced_prompt


# =============================================================================
# DIAGNOSTIC HELPER - For the specific experiment analysis request
# =============================================================================

def get_experiment_diagnostic_sources() -> Dict[str, str]:
    """
    Get the specific data sources and queries for experiment diagnostics.

    This is tailored for the "analyze failed experiments" use case.

    Session 882: Fixed to use correct model (Experiment, not ExperimentExecution)
    and correct field names and status values.
    """
    return {
        'failed_experiments': """
from core.models import Experiment
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta

# Get last 20 failed experiments
# Status values: running, success, failure, partial, inconclusive
failed_experiments = Experiment.objects.filter(
    status='failure'
).order_by('-created_at')[:20]

for exp in failed_experiments:
    print(f"ID: {exp.id}")
    print(f"Name: {exp.name}")
    print(f"Status: {exp.status}")
    print(f"Hypothesis: {exp.hypothesis}")
    print(f"Is Halted: {exp.is_halted}")
    print(f"Halt Reason: {exp.halt_reason}")
    print(f"Result Summary: {exp.result_summary}")
    print(f"Learnings: {exp.learnings}")
    print("---")
""",
        'halt_analysis': """
# Analyze halted experiments
from core.models import Experiment
from django.db.models import Count

# Get experiments that were halted
halted = Experiment.objects.filter(is_halted=True)
print(f"Total halted experiments: {halted.count()}")

# Breakdown by halted_by (auto/manual/system)
by_halted_by = halted.values('halted_by').annotate(
    count=Count('id')
).order_by('-count')

print("\\nHalted By Distribution:")
for item in by_halted_by:
    print(f"  {item['halted_by']}: {item['count']}")

# Recent halt reasons
print("\\nRecent Halt Reasons:")
for exp in halted.order_by('-halted_at')[:10]:
    print(f"  {exp.name}: {exp.halt_reason[:100] if exp.halt_reason else 'No reason'}")
""",
        'status_distribution': """
# Get experiment status distribution
from core.models import Experiment
from django.db.models import Count

status_counts = Experiment.objects.values('status').annotate(
    count=Count('id')
).order_by('-count')

total = Experiment.objects.count()
print(f"Total Experiments: {total}")
print("\\nStatus Distribution:")
for item in status_counts:
    pct = item['count'] / total * 100 if total > 0 else 0
    print(f"  {item['status']}: {item['count']} ({pct:.1f}%)")
""",
        'agent_execution_failures': """
# Check agent execution failures
from core.models import AgentExecution
from django.db.models import Count

# Status values: completed, failed, in_progress
status_counts = AgentExecution.objects.values('status').annotate(
    count=Count('id')
).order_by('-count')

total = AgentExecution.objects.count()
print(f"Total Agent Executions: {total}")
print("\\nStatus Distribution:")
for item in status_counts:
    pct = item['count'] / total * 100 if total > 0 else 0
    print(f"  {item['status']}: {item['count']} ({pct:.1f}%)")

# Recent failures with error messages
print("\\nRecent Failed Executions:")
for exec in AgentExecution.objects.filter(status='failed').order_by('-created_at')[:10]:
    print(f"  {exec.agent}: {exec.error_message[:80] if exec.error_message else 'No error message'}...")
""",
    }
