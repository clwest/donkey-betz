"""
EnhancedPersonalAIAssistant EPAUtilityMixin — extracted handler methods.
"""


def _ensure_assets_dict(assistant):
    """Return the recently_generated_assets dict, creating it if missing.

    Works on both EPA (mixin-bearing) and PersonalAIAssistant (no mixin)
    cached assistant objects. Session 1103: track_generated_image/video
    used to be called as methods on the cached assistant — but when the
    cache returned a PersonalAIAssistant instead of the mixin class, the
    call silently raised AttributeError inside a try/except and the
    image/video chaining state never updated. The helpers below replace
    those method calls with direct dict mutation so the tracking works
    regardless of what class the cache returned.
    """
    existing = getattr(assistant, 'recently_generated_assets', None)
    if not isinstance(existing, dict):
        existing = {'images': [], 'videos': [], 'last_updated': None}
        try:
            setattr(assistant, 'recently_generated_assets', existing)
        except Exception as _e:
            logger.warning(
                "epa_handlers_utility._ensure_assets_dict: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )
    existing.setdefault('images', [])
    existing.setdefault('videos', [])
    return existing


def track_generated_image_on_assistant(assistant, image_id, image_url, prompt,
                                       asset_type='logo'):
    """Append a newly-generated image to the assistant's recent-assets state.

    Kept in sync with EPAUtilityMixin.track_generated_image so both EPA
    and PersonalAIAssistant objects can be tracked the same way.
    """
    from django.utils import timezone as _tz
    assets = _ensure_assets_dict(assistant)
    assets['images'].append({
        'id': image_id,
        'url': image_url,
        'prompt': prompt,
        'type': asset_type,
        'timestamp': _tz.now().isoformat(),
    })
    assets['last_updated'] = _tz.now().isoformat()
    assets['images'] = assets['images'][-10:]


def track_generated_video_on_assistant(assistant, video_id, video_url, prompt,
                                       source_image_id=None):
    """Append a newly-generated video to the assistant's recent-assets state."""
    from django.utils import timezone as _tz
    assets = _ensure_assets_dict(assistant)
    assets['videos'].append({
        'id': video_id,
        'url': video_url,
        'prompt': prompt,
        'source_image_id': source_image_id,
        'timestamp': _tz.now().isoformat(),
    })
    assets['last_updated'] = _tz.now().isoformat()
    assets['videos'] = assets['videos'][-10:]


"""
Enhanced Personal AI Assistant with Database and System Access
===============================================================

This module extends the Personal AI Assistant with direct database access,
system status monitoring, and agent execution capabilities.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from django.contrib.auth import get_user_model
from django.db import connection
from django.utils import timezone

from core.models import EnhancedUserProfile, UserMemoryContext
from core.personal_ai_assistant import PersonalAIAssistant
from core.llm_enforcer import LLMEnforcer
from core.unified_memory_manager import get_memory_manager
from core.services.memory_context_service import get_memory_context_service
from core.agents.registry import get_agent_registry
from advisors.registry import get_advisor_registry
try:
    from self_awareness.embeddings import CodebaseEmbeddings
except ImportError:
    # Fallback if CodebaseEmbeddings is not available
    class CodebaseEmbeddings:
        def __init__(self):
            pass

# Session 266: Super Platform Integration - Dynamic Prompting System
try:
    from core.super_platform import (
        QueryClassifier,
        ClassificationResult,
        ContextAggregator,
        AggregatedContext,
        get_learning_loop_service,
        get_scifi_integration_service,
        get_learning_companion_service,
    )
    SUPER_PLATFORM_AVAILABLE = True
except ImportError as e:
    SUPER_PLATFORM_AVAILABLE = False

# Session 482: Proactive Intelligence Integration - Connect 19 Autonomous Situations
try:
    from core.services.proactive_intelligence import (
        ProactiveIntelligenceService,
        get_proactive_intelligence_service
    )
    PROACTIVE_INTELLIGENCE_AVAILABLE = True
except ImportError as e:
    PROACTIVE_INTELLIGENCE_AVAILABLE = False
    ProactiveIntelligenceService = None
    get_proactive_intelligence_service = lambda user=None: None
    # Provide fallback classes for graceful degradation
    class QueryClassifier:
        def classify(self, query):
            return None
    class ContextAggregator:
        def __init__(self, user=None):
            pass
        def aggregate(self, classification, query):
            return None
    ClassificationResult = None
    AggregatedContext = None

# Session 482: Reference Resolution - Handle "it", "that", "the first one"
try:
    from core.services.reference_resolver import (
        ReferenceResolver,
        get_reference_resolver
    )
    REFERENCE_RESOLVER_AVAILABLE = True
except ImportError as e:
    REFERENCE_RESOLVER_AVAILABLE = False
    ReferenceResolver = None
    get_reference_resolver = lambda session_id='default': None

# Session 482: Smart Suggestions - Context-aware follow-up suggestions
try:
    from core.services.smart_suggestions import (
        SmartSuggestionsService,
        get_smart_suggestions_service
    )
    SMART_SUGGESTIONS_AVAILABLE = True
except ImportError as e:
    SMART_SUGGESTIONS_AVAILABLE = False
    SmartSuggestionsService = None
    get_smart_suggestions_service = lambda session_id='default': None

# Session 482: Task Memory - Multi-turn task tracking
try:
    from core.services.task_memory import (
        TaskMemoryService,
        get_task_memory_service
    )
    TASK_MEMORY_AVAILABLE = True
except ImportError as e:
    TASK_MEMORY_AVAILABLE = False
    TaskMemoryService = None
    get_task_memory_service = lambda session_id='default': None

# Session 806: Context Optimization Components
try:
    from core.services.context_budget_manager import (
        get_context_budget_manager,
        SectionPriority,
    )
    from core.services.lazy_context_loader import (
        get_lazy_context_loader,
        QueryType,
    )
    from core.services.context_summarizer import get_context_summarizer
    from core.assistant.tool_category_router import get_tool_category_router
    CONTEXT_OPTIMIZATION_AVAILABLE = True
except ImportError as e:
    CONTEXT_OPTIMIZATION_AVAILABLE = False
    get_context_budget_manager = lambda: None
    get_lazy_context_loader = lambda: None
    get_context_summarizer = lambda: None
    get_tool_category_router = lambda: None
    SectionPriority = None
    QueryType = None

logger = logging.getLogger(__name__)
User = get_user_model()




class EPAUtilityMixin:
    """Mixin providing handler methods for EnhancedPersonalAIAssistant."""

    def _build_proactive_intelligence_section(self, message: str, context: Dict[str, Any]) -> str:
        """
        Session 482: Build proactive intelligence section from 19 Autonomous Situations.

        This injects alerts, opportunities, and suggestions from the autonomous
        situation network into the GPT prompt, enabling proactive assistance.

        The 19 Situations by Domain:
        - Content: Content Studio, Narrative Drift
        - Creative: Design Trends, Viral Predictor, Thumbnails
        - Income: Job Match, Freelance Scout, Side Hustles
        - Financial: Market Intelligence, SEC Filing, Earnings, Crypto, Blockchain
        - Research: Tech Stack, AI Models, Skill Gaps
        - Legal: Case Law, Regulatory

        Args:
            message: User's current message
            context: Conversation context

        Returns:
            Formatted string section to append to system prompt
        """
        if not self.proactive_intelligence or not PROACTIVE_INTELLIGENCE_AVAILABLE:
            return ""

        try:
            # Get relevant intelligence based on message context
            intelligence = self.proactive_intelligence.get_relevant_intelligence(
                message=message,
                context=context,
                max_alerts=3,
                hours_lookback=24
            )

            # Cache for potential use in response suggestions
            self._last_proactive_intelligence = intelligence

            # Format for prompt injection
            formatted = self.proactive_intelligence.format_for_prompt(intelligence)

            # Session 803: Handle case where intelligence is a string instead of dict
            if formatted:
                if isinstance(intelligence, dict):
                    logger.info(f"📡 Session 482: Injected proactive intelligence "
                               f"({len(intelligence.get('alerts', []))} alerts, "
                               f"{len(intelligence.get('suggestions', []))} suggestions)")
                else:
                    logger.info(f"📡 Session 482: Injected proactive intelligence (formatted string)")

            return formatted

        except Exception as e:
            logger.warning(f"⚠️ Proactive intelligence injection failed: {e}")
            return ""

    def _build_pending_decisions_section(self) -> str:
        """
        Session 796: Build pending human decisions section for system prompt.

        This injects pending decisions that need human attention into the GPT prompt,
        making the PA aware of items requiring approval, review, or action.

        Returns:
            Formatted string section to append to system prompt
        """
        try:
            from core.models_human_interface import HumanAttentionItem

            # Get base queryset for counting (before slicing to avoid Django error)
            base_query = HumanAttentionItem.objects.filter(
                user=self.user,
                status__in=['pending', 'viewed']
            )

            count = base_query.count()
            if count == 0:
                return ""

            critical = base_query.filter(urgency='critical').count()
            high = base_query.filter(urgency='high').count()

            # Now get the sliced list for display
            pending_items = base_query.order_by('-priority_score', '-created_at')[:10]

            sections = ["\n\n--- PENDING HUMAN DECISIONS (Session 796) ---"]
            sections.append(f"⚠️ {count} item(s) need the user's attention")
            if critical > 0:
                sections.append(f"  🚨 {critical} CRITICAL priority")
            if high > 0:
                sections.append(f"  ⚠️ {high} HIGH priority")

            sections.append("\nTop items requiring action:")
            for i, item in enumerate(pending_items[:5], 1):
                urgency_emoji = {
                    'critical': '🚨',
                    'high': '⚠️',
                    'medium': '📋',
                    'low': 'ℹ️'
                }.get(item.urgency, '📋')
                sections.append(f"  {i}. {urgency_emoji} [{item.item_type}] {item.title[:60]}")

            sections.append("\n💡 IMPORTANT: When greeting or asked about system status, PROACTIVELY mention these pending items.")
            sections.append("   Use the human_decisions_tool to show details or help the user decide.")

            logger.info(f"📋 Session 796: Injected {count} pending decisions into prompt")
            return "\n".join(sections)

        except Exception as e:
            logger.warning(f"⚠️ Pending decisions injection failed: {e}")
            return ""

    def _build_workspace_context_section(self) -> str:
        """
        Session 798: Build workspace context section for system prompt.

        This injects the user's active workspace information into the GPT prompt,
        making the PA aware of the project structure, tech stack, key files,
        and directory purposes so it can provide contextual assistance.

        Returns:
            Formatted string section to append to system prompt
        """
        try:
            from core.services.workspace_manager import WorkspaceManager
            from core.models_skin_layer import ProjectWorkspace

            manager = WorkspaceManager(self.user)
            workspace = manager.get_active_workspace()

            if not workspace:
                return ""

            sections = ["\n\n--- ACTIVE WORKSPACE CONTEXT (Session 798) ---"]
            sections.append(f"📁 **Workspace:** {workspace.name}")
            sections.append(f"   Path: {workspace.root_path}")

            # Tech stack (on ProjectWorkspace)
            if workspace.tech_stack:
                tech_parts = []
                if workspace.tech_stack.get('frontend'):
                    tech_parts.append(f"Frontend: {workspace.tech_stack['frontend']}")
                if workspace.tech_stack.get('backend'):
                    tech_parts.append(f"Backend: {workspace.tech_stack['backend']}")
                if workspace.tech_stack.get('database'):
                    tech_parts.append(f"Database: {workspace.tech_stack['database']}")
                if workspace.tech_stack.get('languages'):
                    langs = workspace.tech_stack['languages']
                    if isinstance(langs, list):
                        tech_parts.append(f"Languages: {', '.join(langs[:5])}")
                if workspace.tech_stack.get('frameworks'):
                    frameworks = workspace.tech_stack['frameworks']
                    if isinstance(frameworks, list):
                        tech_parts.append(f"Frameworks: {', '.join(frameworks[:5])}")
                if tech_parts:
                    sections.append(f"\n   **Tech Stack:** {' | '.join(tech_parts)}")

            # Get WorkspaceContext if it exists (key_files, directory_purposes, etc. are on this model)
            ws_context = getattr(workspace, 'context', None)

            if ws_context:
                # Key files (on WorkspaceContext)
                if ws_context.key_files:
                    key_files_display = []
                    for purpose, path in list(ws_context.key_files.items())[:5]:
                        key_files_display.append(f"{purpose}: {path}")
                    if key_files_display:
                        sections.append(f"\n   **Key Files:**")
                        for kf in key_files_display:
                            sections.append(f"     - {kf}")

                # Directory purposes (on WorkspaceContext)
                if ws_context.directory_purposes:
                    dir_display = []
                    for dir_name, purpose in list(ws_context.directory_purposes.items())[:5]:
                        dir_display.append(f"{dir_name}: {purpose}")
                    if dir_display:
                        sections.append(f"\n   **Directory Structure:**")
                        for dd in dir_display:
                            sections.append(f"     - {dd}")

                # Import aliases and patterns (on WorkspaceContext)
                if ws_context.import_aliases:
                    sections.append(f"\n   **Import Aliases:** {', '.join(list(ws_context.import_aliases.keys())[:5])}")

                if ws_context.coding_patterns:
                    patterns = list(ws_context.coding_patterns.keys())[:3]
                    sections.append(f"\n   **Coding Patterns:** {', '.join(patterns)}")

            # Stats (on ProjectWorkspace)
            if workspace.total_files_written > 0 or workspace.total_operations > 0:
                sections.append(f"\n   **Stats:** {workspace.total_files_written} files written, {workspace.total_operations} operations")

            sections.append("\n💡 WORKSPACE AWARENESS: You know this project's structure. When asked about code, files, or development tasks, use this context to provide specific guidance.")
            sections.append("   Use the workspace_tool to read/write files, check git status, or create commits in this workspace.")

            logger.info(f"📁 Session 798: Injected workspace context for '{workspace.name}' into prompt")
            return "\n".join(sections)

        except Exception as e:
            logger.warning(f"⚠️ Workspace context injection failed: {e}")
            return ""

    def _build_operator_mode_section(self) -> str:
        """
        Session 800: Build Operator Mode section for system prompt.

        This addresses the critical feedback that the PA describes capabilities
        instead of current state. This section injects:
        1. What changed since last interaction (learning updates)
        2. What's currently happening (active agents, running tasks)
        3. What's blocked or needs decisions
        4. Specific actions needed from the user

        This transforms the PA from "tour guide" mode to "control plane" mode.

        Returns:
            Formatted string section to append to system prompt
        """
        sections = ["\n\n--- OPERATOR MODE: CURRENT STATE (Session 800) ---"]
        sections.append("**CRITICAL: Lead with state, not capabilities. You are a control plane, not a tour guide.**\n")

        try:
            from django.utils import timezone
            from datetime import timedelta

            now = timezone.now()
            last_hour = now - timedelta(hours=1)
            last_24h = now - timedelta(hours=24)

            # ============================================
            # 1. WHAT CHANGED: Recent Learning Updates
            # ============================================
            learning_section = []
            try:
                from core.models_unified_system import AgentMemory, KnowledgeTransfer

                # Recent knowledge transfers (agent-to-agent learning)
                recent_transfers = KnowledgeTransfer.objects.filter(
                    created_at__gte=last_24h
                ).order_by('-created_at')[:5]

                if recent_transfers.exists():
                    learning_section.append("📚 **Recent Learning (last 24h):**")
                    for kt in recent_transfers:
                        source = kt.source_agent.name if kt.source_agent else "System"
                        target = kt.target_agent.name if kt.target_agent else "All"
                        learning_section.append(f"  • {source} → {target}: {kt.knowledge_type}")

                # Recent agent memories created (insights learned)
                recent_insights = AgentMemory.objects.filter(
                    created_at__gte=last_24h,
                    memory_type__in=['insight', 'learning', 'realization']
                ).order_by('-created_at')[:3]

                if recent_insights.exists():
                    if not learning_section:
                        learning_section.append("📚 **Recent Learning (last 24h):**")
                    for mem in recent_insights:
                        agent_name = mem.agent.name if mem.agent else "System"
                        content_preview = mem.content[:80] + "..." if len(mem.content) > 80 else mem.content
                        learning_section.append(f"  • {agent_name} learned: {content_preview}")

            except Exception as e:
                logger.debug(f"Learning section error: {e}")

            if learning_section:
                sections.extend(learning_section)
            else:
                sections.append("📚 **Learning:** No new insights in the last 24 hours.")

            # ============================================
            # 2. WHAT'S HAPPENING: Active/Recent Executions
            # ============================================
            activity_section = []
            try:
                from core.models_unified_system import AgentExecution

                # Currently running or recent executions
                recent_executions = AgentExecution.objects.filter(
                    created_at__gte=last_hour
                ).order_by('-created_at')[:5]

                if recent_executions.exists():
                    activity_section.append("\n⚡ **Recent Agent Activity (last hour):**")
                    for exec in recent_executions:
                        status_emoji = "✅" if exec.success else "❌"
                        agent_name = exec.agent.name if exec.agent else "Unknown"
                        activity_section.append(f"  {status_emoji} {agent_name}: {exec.task_type or 'task'}")
                else:
                    # Check 24h if nothing in last hour
                    day_executions = AgentExecution.objects.filter(
                        created_at__gte=last_24h
                    ).count()
                    if day_executions > 0:
                        activity_section.append(f"\n⚡ **Activity:** {day_executions} agent executions in last 24h (none in last hour)")
                    else:
                        activity_section.append("\n⚡ **Activity:** No agent executions in the last 24 hours.")

            except Exception as e:
                logger.debug(f"Activity section error: {e}")

            sections.extend(activity_section)

            # ============================================
            # 3. WHAT'S BLOCKED: Gates, Consultations
            # ============================================
            blocked_section = []
            try:
                from core.models_unified_system import PilotReadinessGate
                from core.models_human_interface import HumanConsultation

                # Pending gates
                pending_gates = PilotReadinessGate.objects.filter(
                    status='pending'
                ).count()

                if pending_gates > 0:
                    blocked_section.append(f"\n🚧 **Blocked:** {pending_gates} pilot gate(s) awaiting review")

                # Pending consultations
                pending_consultations = HumanConsultation.objects.filter(
                    status='pending'
                ).count()

                if pending_consultations > 0:
                    blocked_section.append(f"🔔 **Consultations:** {pending_consultations} agent(s) waiting for human input")

            except Exception as e:
                logger.debug(f"Blocked section error: {e}")

            if blocked_section:
                sections.extend(blocked_section)

            # ============================================
            # 4. PRODUCTION STATUS: Content & Spiders
            # ============================================
            production_section = []
            try:
                from core.models_autonomous_studio import ContentChannel, ChannelEpisode
                from core.models_unified_system import SpiderData

                # Content channel status
                active_channels = ContentChannel.objects.filter(status='active').count()
                recent_episodes = ChannelEpisode.objects.filter(
                    created_at__gte=last_24h
                ).count()

                if active_channels > 0:
                    production_section.append(f"\n📺 **Content:** {active_channels} active channels, {recent_episodes} episodes created (24h)")

                # Spider data freshness
                recent_spider_data = SpiderData.objects.filter(
                    created_at__gte=last_hour
                ).count()

                if recent_spider_data > 0:
                    production_section.append(f"🕷️ **Spider Network:** {recent_spider_data} new data items (last hour)")

            except Exception as e:
                logger.debug(f"Production section error: {e}")

            if production_section:
                sections.extend(production_section)

            # ============================================
            # OPERATOR INSTRUCTIONS
            # ============================================
            sections.append("\n---")
            sections.append("**OPERATOR MODE INSTRUCTIONS:**")
            sections.append("1. When greeting the user, START with current state: \"Here's what's happening...\"")
            sections.append("2. If asked about the system, show WHAT CHANGED, not capabilities")
            sections.append("3. End with SPECIFIC decisions needed, not open-ended questions")
            sections.append("4. For system owner/builder, skip the tour - they know the system")

            logger.info("📊 Session 800: Injected Operator Mode context into prompt")
            return "\n".join(sections)

        except Exception as e:
            logger.warning(f"⚠️ Operator mode injection failed: {e}")
            return ""

    def _get_agent_scifi_context(self, agent_name: str, task: str) -> str:
        """
        Session 266: Get Sci-Fi context for an agent (mood, evolution, personality).

        This makes agent responses feel more alive by incorporating:
        - Current mood state
        - Evolution level and title
        - Personality traits

        Args:
            agent_name: Name of the agent
            task: Current task description

        Returns:
            Formatted context string for the agent
        """
        if not SUPER_PLATFORM_AVAILABLE:
            return ""

        # Lazy load sci-fi service
        if self._scifi_service is None:
            try:
                self._scifi_service = get_scifi_integration_service()
            except Exception as e:
                logger.warning(f"⚠️ Could not load sci-fi service: {e}")
                return ""

        if not self._scifi_service:
            return ""

        try:
            scifi_ctx = self._scifi_service.get_scifi_context(agent_name, task, self.user)
            parts = []

            if scifi_ctx and hasattr(scifi_ctx, 'mood') and scifi_ctx.mood:
                mood = scifi_ctx.mood
                if hasattr(mood, 'mood_type') and mood.mood_type:
                    parts.append(f"🎭 Mood: {mood.mood_type}")
                if hasattr(mood, 'description') and mood.description:
                    parts.append(f"   {mood.description}")

            if scifi_ctx and hasattr(scifi_ctx, 'evolution') and scifi_ctx.evolution:
                evo = scifi_ctx.evolution
                if hasattr(evo, 'level') and hasattr(evo, 'title'):
                    parts.append(f"⭐ Level {evo.level}: {evo.title}")

            return "\n".join(parts) if parts else ""
        except Exception as e:
            logger.debug(f"Sci-Fi context not available for {agent_name}: {e}")
            return ""

    def _get_learning_companion_context(self) -> str:
        """
        Session 266: Get Learning Companion context for system prompt.

        Injects:
        - User's charter (their ideal learning style)
        - Active learning track
        - Relevant spider categories for the track
        - Recently covered topics
        - Pending actions

        Returns:
            Formatted context string for the system prompt
        """
        if not SUPER_PLATFORM_AVAILABLE:
            return ""

        # Lazy load learning companion service
        if self._learning_companion_service is None:
            try:
                self._learning_companion_service = get_learning_companion_service(self.user)
            except Exception as e:
                logger.warning(f"⚠️ Could not load learning companion service: {e}")
                return ""

        if not self._learning_companion_service:
            return ""

        try:
            return self._learning_companion_service.get_learning_context_for_prompt()
        except Exception as e:
            logger.debug(f"Learning Companion context not available: {e}")
            return ""

    def _get_policy_context(self) -> str:
        """
        Session 324: Get canonical policies from Boardroom Decisions for system prompt.

        Injects adopted team policies that guide AI behavior and recommendations.
        These are policies that were discussed and voted on by the agent team.

        Returns:
            Formatted policy context string for the system prompt
        """
        try:
            from core.services.policy_context import get_policy_context_service
            policy_service = get_policy_context_service()
            # PolicyContextService.get_policies_for_agent returns a pre-formatted string
            policy_context = policy_service.get_policies_for_agent('PersonalAssistant')

            if policy_context:
                logger.debug("Session 324: Injecting policy context into assistant prompt")
                return policy_context

            return ""
        except Exception as e:
            logger.debug(f"Policy context not available: {e}")
            return ""

    def _get_agent_knowledge_context(self) -> str:
        """
        Session 324: Get recent agent knowledge transfers for system prompt.

        Injects insights from what agents have been learning from each other.
        This gives the assistant awareness of the collective agent intelligence.

        Returns:
            Formatted agent knowledge context string for the system prompt
        """
        try:
            from core.models import KnowledgeTransfer
            from django.utils import timezone
            from datetime import timedelta

            # Get recent successful knowledge transfers
            recent_transfers = KnowledgeTransfer.objects.filter(
                was_useful=True,
                created_at__gte=timezone.now() - timedelta(days=7)
            ).select_related(
                'connection__teacher_agent',
                'connection__student_agent'
            ).order_by('-created_at')[:5]

            if not recent_transfers:
                return ""

            sections = ["\n🧠 AGENT COLLECTIVE KNOWLEDGE (Recent Learnings):"]
            for transfer in recent_transfers:
                try:
                    teacher = transfer.connection.teacher_agent.name
                    student = transfer.connection.student_agent.name
                    summary = transfer.transfer_summary[:100] if transfer.transfer_summary else 'Knowledge shared'
                    if teacher == student:
                        sections.append(f"- {teacher} learned: {summary}")
                    else:
                        sections.append(f"- {teacher} → {student}: {summary}")
                except Exception:
                    continue

            if len(sections) > 1:
                sections.append("*Leverage this collective knowledge when assisting.*")
                return "\n".join(sections)

            return ""
        except Exception as e:
            logger.debug(f"Agent knowledge context not available: {e}")
            return ""

    def _get_project_brief_context(self) -> str:
        """
        Session 181: Build comprehensive project brief for AI context.

        Provides the AI Assistant with full project information including:
        - Project name and status
        - Goal and description (the creative brief)
        - Category and tags for style guidance
        - Color palette preferences

        This allows the AI to generate content that aligns with the project's
        vision without requiring the user to repeat the brief each time.

        Returns:
            Formatted project brief string, or empty string if no active project.
        """
        try:
            project = getattr(self, 'project', None)
            if not project:
                return ""

            lines = []
            lines.append(f"📁 **Active Project: {project.name}**")
            lines.append(f"   Status: {project.get_status_display()}")

            # Goal is the most important - the creative brief
            if project.goal:
                lines.append(f"   🎯 Goal: {project.goal}")

            # Description provides additional context
            if project.description:
                lines.append(f"   📝 Description: {project.description}")

            # Category helps with style decisions
            if project.category:
                lines.append(f"   📂 Category: {project.category}")

            # Color palette is critical for visual consistency
            if project.colors:
                lines.append(f"   🎨 Color Palette: {project.colors}")

            # Tags provide style keywords
            if project.tags and len(project.tags) > 0:
                lines.append(f"   🏷️ Style Tags: {', '.join(project.tags)}")

            # Add guidance for AI
            lines.append("")
            lines.append("**IMPORTANT - Project Brief Integration (Session 181):**")
            lines.append("- Use the Goal and Description above as your creative brief")
            lines.append("- Match the Color Palette when generating visual content")
            lines.append("- Incorporate Style Tags into image/video generation prompts")
            lines.append("- Maintain consistency with the project's Category aesthetic")
            lines.append("- If user's request is vague, infer style from project context")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error building project brief context: {e}")
            return ""

    def _get_style_preferences_context(self) -> str:
        """
        Session 169 Phase 3 + Session 179 Enhancement + Session 266 Creative Trends:
        Get user's learned style preferences for personalized generation.

        Session 179: Now also includes semantic style context from embeddings
        when available, enabling more sophisticated preference matching.

        Session 266: Now includes trending creative styles from the spider network
        to encourage variety and alignment with current design trends.

        Returns:
            Formatted string of style preferences, or empty string if no preferences.
        """
        lines = []

        # Session 266: Get trending creative styles from spider network FIRST
        # This provides fresh, varied style suggestions
        try:
            from core.services.spider_intelligence import get_spider_intelligence
            spider_intel = get_spider_intelligence()
            creative_trends = spider_intel.get_creative_trends(hours=48, limit=5)

            if creative_trends.get('has_live_data') or creative_trends.get('trending_styles'):
                lines.append("🎨 TRENDING DESIGN STYLES (from spider network):")
                lines.append("IMPORTANT: Vary styles based on the specific request! Don't always use the same style.")

                if creative_trends.get('trending_styles'):
                    style_names = [s['style'] for s in creative_trends['trending_styles'][:5]]
                    lines.append(f"- Hot styles: {', '.join(style_names)}")

                if creative_trends.get('trending_colors'):
                    color_names = [c['palette'] for c in creative_trends['trending_colors'][:5]]
                    lines.append(f"- Trending palettes: {', '.join(color_names)}")

                if creative_trends.get('keywords'):
                    lines.append(f"- Design keywords: {', '.join(creative_trends['keywords'][:8])}")

                lines.append("")
        except Exception as spider_err:
            logger.debug(f"Creative trends not available: {spider_err}")

        # Original style learning from user interactions
        try:
            from style_memory.models import StyleMemory, StylePattern

            # Get interaction counts
            total_interactions = StyleMemory.objects.filter(user=self.user).count()

            if total_interactions > 0:
                loved_count = StyleMemory.objects.filter(user=self.user, interaction_type='love').count()
                liked_count = StyleMemory.objects.filter(user=self.user, interaction_type='like').count()
                disliked_count = StyleMemory.objects.filter(user=self.user, interaction_type='dislike').count()

                # Get detected patterns
                patterns = StylePattern.objects.filter(user=self.user).order_by('-confidence', '-frequency')[:10]

                if patterns.exists() or total_interactions >= 3:
                    lines.append(f"📊 User Style Learning (based on {total_interactions} ratings: {loved_count}❤️, {liked_count}👍, {disliked_count}👎):")

                    if patterns.exists():
                        pattern_groups = {}
                        for p in patterns:
                            if p.pattern_type not in pattern_groups:
                                pattern_groups[p.pattern_type] = []
                            pattern_groups[p.pattern_type].append(p.pattern_value)

                        for ptype, values in pattern_groups.items():
                            lines.append(f"- User likes {ptype}: {', '.join(values[:3])}")

                    lines.append("")

            # Session 179: Try to add semantic context from embeddings
            try:
                from style_memory.embedding_bridge import get_style_context_for_user
                # Get the current prompt/context for semantic matching
                current_context = getattr(self, '_current_prompt', '')
                if current_context:
                    semantic_context = get_style_context_for_user(self.user, current_context)
                    if semantic_context:
                        lines.append("🔗 Semantic style match:")
                        lines.append(semantic_context)
            except Exception as embed_err:
                # Embeddings not available or not populated - that's fine
                logger.debug(f"Semantic style context not available: {embed_err}")

        except Exception as e:
            logger.debug(f"Error getting style preferences: {e}")

        # Session 266: Add instruction to vary styles
        if lines:
            lines.append("")
            lines.append("💡 STYLE VARIATION GUIDELINE: Match styles to the specific platform/use case:")
            lines.append("   - Etsy prints: botanical, watercolor, boho, line-art, abstract")
            lines.append("   - Tech/SaaS: geometric, minimalist, gradient, modern, clean")
            lines.append("   - Luxury brands: elegant, art-deco, gold accents, monochrome")
            lines.append("   - Kids/playful: colorful, hand-drawn, whimsical, vibrant")
            lines.append("   - Do NOT always default to the same style palette!")

        return "\n".join(lines) if lines else ""

    def _get_agent_context(self) -> Dict[str, Any]:
        """Get context data for agent execution."""
        return {
            'user_id': str(self.user.id),  # Convert to string
            'user_role': self.enhanced_profile.primary_role or 'Not specified',
            'user_goals': self.enhanced_profile.long_term_goals or [],
            'user_skills': list(self.enhanced_profile.core_competencies.keys()) if self.enhanced_profile.core_competencies else [],
            'current_projects': self.enhanced_profile.current_projects or [],
            'communication_style': self.enhanced_profile.communication_style or 'balanced',
            'timezone': self.enhanced_profile.time_zone or 'UTC',
            'timestamp': datetime.now().isoformat()
        }

    def _get_recent_decisions(self) -> List[Dict[str, Any]]:
        """Get recent user decisions for advisor context."""
        try:
            recent_decisions = self.retrieve_memories('decision', limit=5)
            return [
                {
                    'content': decision.content,
                    'timestamp': decision.created_at.isoformat(),
                    'importance': decision.importance
                }
                for decision in recent_decisions
            ]
        except Exception as e:
            logger.error(f"Error getting recent decisions: {e}")
            return []

    def _get_advisor_history(self, advisor_id: str) -> List[Dict[str, Any]]:
        """Get consultation history with specific advisor."""
        try:
            advisor_memories = self.retrieve_memories('advisor_consultation', limit=10)
            relevant_memories = [
                {
                    'content': memory.content,
                    'timestamp': memory.created_at.isoformat(),
                    'metadata': memory.metadata
                }
                for memory in advisor_memories
                if memory.metadata and memory.metadata.get('advisor_id') == advisor_id
            ]
            return relevant_memories
        except Exception as e:
            logger.error(f"Error getting advisor history: {e}")
            return []

    def _format_conversation_context(self, conversations: List[Dict[str, Any]]) -> str:
        """
        Format conversation history into context string.

        Args:
            conversations: List of conversation dictionaries

        Returns:
            Formatted conversation context string
        """
        if not conversations:
            return ""

        context_parts = ["Recent conversation history:"]

        # Reverse to show oldest first (chronological order)
        for conv in reversed(conversations):
            context_parts.append(f"User: {conv['message']}")
            context_parts.append(f"Assistant: {conv['response'][:100]}...")
            context_parts.append("")  # Empty line for readability

        return "\n".join(context_parts)

    def _track_tool_usage(self, tool_name: str, result: Dict[str, Any], start_time: float = None):
        """
        Session 761: Track tool usage metrics in AgentTool model.

        Updates usage_count, avg_response_time_ms, and success_rate.
        """
        try:
            from core.models.agents_registry.models import AgentTool
            import time

            # Calculate response time
            response_time_ms = 0.0
            if start_time:
                response_time_ms = (time.time() - start_time) * 1000

            # Determine success
            is_success = result.get('success', True) if isinstance(result, dict) else True

            # Update the tool record
            tool = AgentTool.objects.filter(name=tool_name).first()
            if tool:
                # Update usage count
                tool.usage_count += 1

                # Update rolling average response time
                if tool.usage_count == 1:
                    tool.avg_response_time_ms = response_time_ms
                else:
                    # Exponential moving average (gives more weight to recent calls)
                    alpha = 0.2  # Weight for new value
                    tool.avg_response_time_ms = (alpha * response_time_ms +
                                                  (1 - alpha) * tool.avg_response_time_ms)

                # Update success rate (rolling average)
                success_value = 1.0 if is_success else 0.0
                if tool.usage_count == 1:
                    tool.success_rate = success_value
                else:
                    alpha = 0.1  # Weight for new success/failure
                    tool.success_rate = (alpha * success_value +
                                         (1 - alpha) * tool.success_rate)

                tool.save(update_fields=['usage_count', 'avg_response_time_ms', 'success_rate'])
                logger.debug(f"📊 Tracked tool usage: {tool_name} - {tool.usage_count} uses, {tool.avg_response_time_ms:.0f}ms avg")
        except Exception as e:
            # Don't let tracking errors break tool execution
            logger.debug(f"Could not track tool usage for {tool_name}: {e}")

    # Session 131: Agent Handler Methods
    def _resolve_hybrid_image_id(self, image_id: str) -> str:
        """Convert sequential image numbers to UUIDs (Session 131, Session 196 - fixed)."""
        if image_id.isdigit():
            from content.models import ImageHistory
            try:
                seq_num = int(image_id)
                # Session 196: Try sequential_number field first (permanent identifier)
                image = ImageHistory.objects.filter(user=self.user, sequential_number=seq_num).first()
                if image:
                    resolved_id = str(image.id)
                    logger.info(f"✅ Converted image #{seq_num} (seq_number) → UUID {resolved_id[:8]}...")
                    return resolved_id
                # Fallback to positional index for backward compatibility
                image = ImageHistory.objects.filter(user=self.user).order_by('created_at')[seq_num - 1]
                resolved_id = str(image.id)
                logger.info(f"✅ Converted image #{seq_num} (positional) → UUID {resolved_id[:8]}...")
                return resolved_id
            except (IndexError, ImageHistory.DoesNotExist):
                raise ValueError(f'Image #{image_id} not found')
        return image_id

    def _parse_id_range(self, id_str: str) -> List[str]:
        """
        Parse image ID ranges into list of individual IDs (Session 152 - Batch Operations).

        Supports:
        - Single ID: "5" → ["5"]
        - Range: "20-25" → ["20", "21", "22", "23", "24", "25"]
        - List: "5, 8, 12" → ["5", "8", "12"]
        - Combined: "10-15, 20, 25-27" → ["10", "11", "12", "13", "14", "15", "20", "25", "26", "27"]
        - Spaces are ignored: "20 - 25, 30" → ["20", "21", "22", "23", "24", "25", "30"]

        Returns: List of ID strings (numbers or UUIDs)
        """
        id_str = id_str.strip()

        # Check if it's a UUID (contains dashes but is a valid UUID format)
        if '-' in id_str and ',' not in id_str:
            # Could be UUID or range - check if it's a valid UUID
            try:
                import uuid as uuid_module
                uuid_module.UUID(id_str)  # Will raise ValueError if not valid UUID
                return [id_str]  # Single UUID
            except ValueError:
                pass  # Not a UUID, parse as range

        # Parse comma-separated segments
        segments = [seg.strip() for seg in id_str.split(',')]
        result = []

        for segment in segments:
            segment = segment.strip()

            # Check if segment contains range (dash between numbers)
            if '-' in segment:
                # Try to parse as range
                parts = [p.strip() for p in segment.split('-')]
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    start = int(parts[0])
                    end = int(parts[1])
                    if start > end:
                        raise ValueError(f"Invalid range: {segment} (start > end)")
                    result.extend([str(i) for i in range(start, end + 1)])
                else:
                    # Not a valid range, treat as single ID
                    result.append(segment)
            else:
                # Single ID
                result.append(segment)

        # Remove duplicates while preserving order
        seen = set()
        unique_result = []
        for id_val in result:
            if id_val not in seen:
                seen.add(id_val)
                unique_result.append(id_val)

        logger.info(f"📋 Parsed ID range '{id_str}' → {len(unique_result)} IDs: {unique_result[:5]}{'...' if len(unique_result) > 5 else ''}")
        return unique_result

    def _execute_single_image_operation(self, operation: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single image operation (Session 152: Extracted for batch support)."""
        # Route to appropriate existing tool handler
        if operation == 'upscale':
            return self._tool_upscale_image(tool_args)
        elif operation == 'remove_background':
            return self._tool_remove_background(tool_args)
        elif operation == 'create_variations':
            return self._tool_create_variations(tool_args)
        elif operation == 'recolor':
            return self._tool_recolor_image(tool_args)
        elif operation == 'search_and_replace':
            return self._tool_search_and_replace(tool_args)  # Session 151 - also handles removal
        elif operation == 'creative_upscale':
            return self._tool_creative_upscale(tool_args)  # Session 151
        else:
            return {'success': False, 'error': f"Unknown image operation: {operation}"}

    def _execute_single_video_enhancement(self, operation: str, video_id: str, params: Dict[str, Any], project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a single video enhancement operation (upscale or apply_effect).
        Session 154: Calls the new ffmpeg-based video enhancement views.
        """
        from django.test.client import RequestFactory
        import json

        try:
            factory = RequestFactory()

            if operation == 'upscale':
                # Build request payload for upscale_video view
                scale_factor = params.get('scale_factor', 2)
                quality = params.get('quality', 'high')

                payload = {
                    'video_id': video_id,
                    'scale_factor': scale_factor,
                    'quality': quality,
                    'project_id': project_id  # Session 156: Pass project_id for linking
                }

                # Create POST request
                request = factory.post(
                    '/api/video/upscale/',
                    data=json.dumps(payload),
                    content_type='application/json'
                )
                request.user = self.user

                # Call the view
                from core.views_video import upscale_video
                response = upscale_video(request)

                # Parse response
                import json
                result = json.loads(response.content)
                logger.info(f"✅ [Session 154] Video upscale result: {result.get('success')}")

                # Normalize response format (convert 'error' to 'message')
                if not result.get('success') and 'error' in result and 'message' not in result:
                    result['message'] = result.pop('error')

                # Session 155: Add agent metadata for UI status indicators
                result['agent'] = 'VideoEditingAgent'
                result['operation'] = operation
                result['operation_display'] = f"Upscaling video {scale_factor}x"

                return result

            elif operation == 'apply_effect':
                # Build request payload for apply_video_effect view
                effect = params.get('effect', 'cinematic')
                intensity = params.get('intensity', 0.7)

                payload = {
                    'video_id': video_id,
                    'effect': effect,
                    'intensity': intensity
                }

                # Create POST request
                request = factory.post(
                    '/api/video/effects/',
                    data=json.dumps(payload),
                    content_type='application/json'
                )
                request.user = self.user

                # Call the view
                from core.views_video import apply_video_effect
                response = apply_video_effect(request)

                # Parse response
                import json
                result = json.loads(response.content)
                logger.info(f"✅ [Session 154] Video effect result: {result.get('success')}")

                # Normalize response format (convert 'error' to 'message')
                if not result.get('success') and 'error' in result and 'message' not in result:
                    result['message'] = result.pop('error')

                # Session 155: Add agent metadata for UI status indicators
                result['agent'] = 'VideoEditingAgent'
                result['operation'] = operation
                result['operation_display'] = f"Applying {effect} effect"

                return result

            else:
                return {'success': False, 'message': f"Unknown operation: {operation}"}

        except Exception as e:
            logger.error(f"❌ [Session 154] Video enhancement error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'success': False, 'message': str(e)}

    def _execute_single_batch_video_operation(self, operation: str, video_id: str, params: Dict[str, Any], project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Session 166: Execute a single video operation within a batch.
        Routes to the appropriate tool handler based on operation type.
        Supports all video editing operations for batch processing.
        """
        # Build tool arguments
        tool_args = {
            'video_id': video_id,
            'project_id': project_id
        }
        tool_args.update(params)  # Merge operation-specific params

        try:
            # Route to appropriate handler based on operation
            if operation == 'upscale':
                return self._execute_single_video_enhancement(operation, video_id, params, project_id)
            elif operation == 'apply_effect':
                return self._execute_single_video_enhancement(operation, video_id, params, project_id)
            elif operation == 'extract_frame':
                return self._tool_extract_video_frame(tool_args)
            elif operation == 'reverse':
                return self._tool_reverse_video(tool_args)
            elif operation == 'trim':
                return self._tool_trim_video(tool_args)
            elif operation == 'speed_change':
                return self._tool_change_video_speed(tool_args)
            elif operation == 'rotate_flip':
                return self._tool_rotate_flip(tool_args)
            elif operation == 'fade':
                return self._tool_fade_video(tool_args)
            elif operation == 'crop_resize':
                return self._tool_crop_resize(tool_args)
            elif operation == 'audio_control':
                return self._tool_audio_control(tool_args)
            elif operation == 'add_watermark':
                return self._tool_add_watermark(tool_args)
            elif operation == 'blur_region':
                return self._tool_blur_region(tool_args)
            elif operation == 'stabilize_video':
                return self._tool_stabilize_video(tool_args)
            elif operation == 'add_text_animation':
                return self._tool_add_text_animation(tool_args)
            elif operation == 'chroma_key':
                return self._tool_chroma_key(tool_args)
            elif operation == 'export_for_platform':
                return self._tool_export_for_platform(tool_args)
            elif operation == 'auto_caption':
                return self._tool_auto_caption(tool_args)
            # Session 167: DaVinci Resolve operations
            elif operation == 'render_professional':
                return self._tool_render_professional(tool_args)
            elif operation == 'apply_lut':
                return self._tool_apply_lut(tool_args)
            elif operation == 'color_grade_professional':
                return self._tool_color_grade_professional(tool_args)
            else:
                return {'success': False, 'error': f"Unsupported batch operation: {operation}"}
        except Exception as e:
            logger.error(f"❌ [Session 166] Batch operation error: {e}")
            return {'success': False, 'error': str(e), 'video_id': video_id}

    def _parse_video_id_range(self, video_id_str: str) -> list:
        """Parse video ID string into list of IDs. Supports '1-3' and '1, 2, 3' formats."""
        video_ids = []
        parts = video_id_str.replace(' ', '').split(',')
        for part in parts:
            if '-' in part:
                try:
                    start, end = part.split('-')
                    for i in range(int(start), int(end) + 1):
                        video_ids.append(str(i))
                except ValueError:
                    video_ids.append(part)
            else:
                video_ids.append(part)
        return video_ids

    def _ensure_enhanced_profile(self):
        """Ensure the user has an enhanced profile."""
        try:
            self.enhanced_profile = EnhancedUserProfile.objects.get(user=self.user)
        except EnhancedUserProfile.DoesNotExist:
            self.enhanced_profile = EnhancedUserProfile.objects.create(user=self.user)
            logger.info(f"Created enhanced profile for {self.user.username}")

    # Session 878: Goal Collection - Help users define their goals for personalization
    def _extract_goals_from_response(self, message: str) -> List[str]:
        """
        Extract goals from a user's response using pattern matching and AI.

        Session 878: Intelligently parse goals from natural language.

        Args:
            message: User's response containing their goals

        Returns:
            List of extracted goals, or empty list if none found
        """
        goals = []

        # First, try simple bullet/numbered list extraction
        import re

        # Match bullet points: - goal, * goal, • goal
        bullet_matches = re.findall(r'^[\s]*[-*•]\s*(.+)$', message, re.MULTILINE)
        if bullet_matches:
            goals.extend([m.strip() for m in bullet_matches if len(m.strip()) > 5])

        # Match numbered lists: 1. goal, 1) goal
        numbered_matches = re.findall(r'^[\s]*\d+[.)]\s*(.+)$', message, re.MULTILINE)
        if numbered_matches:
            goals.extend([m.strip() for m in numbered_matches if len(m.strip()) > 5])

        # If we found formatted goals, return them
        if goals:
            return goals[:5]  # Limit to 5 goals

        # Otherwise, try to split on common separators
        # Split on "and", commas, or newlines for conversational responses
        if '\n' in message:
            lines = [l.strip() for l in message.split('\n') if l.strip() and len(l.strip()) > 10]
            if len(lines) >= 2:
                return lines[:5]

        # If message is long enough and contains goal-like content, treat it as a single goal
        goal_indicators = ['want to', 'goal is', 'trying to', 'working on', 'hope to',
                          'plan to', 'aim to', 'need to', 'going to', 'looking to']

        if len(message) > 20 and any(ind in message.lower() for ind in goal_indicators):
            # Split by commas if multiple clauses
            if ',' in message and message.count(',') <= 4:
                parts = [p.strip() for p in message.split(',') if len(p.strip()) > 10]
                if len(parts) >= 2:
                    return parts[:5]

            # Treat the whole message as a goal statement
            return [message.strip()[:200]]

        # Fallback: if message is substantial, use it as a single goal
        if len(message) > 30:
            return [message.strip()[:200]]

        return []

    # Session 882: Interview System Integration - Auto-trigger for new users
    def track_generated_image(self, image_id: str, image_url: str, prompt: str, asset_type: str = 'logo'):
        """
        Track a newly generated image for intelligent chaining.

        Args:
            image_id: Database ID of the image
            image_url: URL to the generated image
            prompt: The prompt used to generate the image
            asset_type: Type of image (logo, social_media, general, etc.)
        """
        from django.utils import timezone

        asset_data = {
            'id': image_id,
            'url': image_url,
            'prompt': prompt,
            'type': asset_type,
            'timestamp': timezone.now().isoformat()
        }

        self.recently_generated_assets['images'].append(asset_data)
        self.recently_generated_assets['last_updated'] = timezone.now().isoformat()

        # Keep only last 10 images (prevent memory bloat)
        if len(self.recently_generated_assets['images']) > 10:
            self.recently_generated_assets['images'] = self.recently_generated_assets['images'][-10:]

        logger.info(f"📸 Tracked new image: {asset_type} (ID: {image_id})")

    def track_generated_video(self, video_id: str, video_url: str, prompt: str, source_image_id: Optional[str] = None):
        """
        Track a newly generated video for context awareness.

        Args:
            video_id: Database ID of the video
            video_url: URL to the generated video
            prompt: The prompt used to generate the video
            source_image_id: ID of source image if this was image-to-video
        """
        from django.utils import timezone

        asset_data = {
            'id': video_id,
            'url': video_url,
            'prompt': prompt,
            'source_image_id': source_image_id,
            'timestamp': timezone.now().isoformat()
        }

        self.recently_generated_assets['videos'].append(asset_data)
        self.recently_generated_assets['last_updated'] = timezone.now().isoformat()

        # Keep only last 10 videos
        if len(self.recently_generated_assets['videos']) > 10:
            self.recently_generated_assets['videos'] = self.recently_generated_assets['videos'][-10:]

        logger.info(f"🎬 Tracked new video (ID: {video_id}, source_image: {source_image_id})")

    def get_recent_assets_context(self) -> str:
        """
        Get formatted context of recently generated assets for AI prompt.

        Returns:
            Formatted string describing recent assets
        """
        from django.utils import timezone
        from datetime import timedelta

        images = self.recently_generated_assets.get('images', [])
        videos = self.recently_generated_assets.get('videos', [])

        if not images and not videos:
            return "No recently generated assets in this session."

        # Filter to assets from last 10 minutes (keep context fresh)
        cutoff_time = timezone.now() - timedelta(minutes=10)

        recent_images = [
            img for img in images
            if timezone.datetime.fromisoformat(img['timestamp']) > cutoff_time
        ]

        recent_videos = [
            vid for vid in videos
            if timezone.datetime.fromisoformat(vid['timestamp']) > cutoff_time
        ]

        context_parts = []

        if recent_images:
            context_parts.append(f"📸 {len(recent_images)} images generated in last 10 minutes:")
            for img in recent_images[-5:]:  # Show last 5
                context_parts.append(f"  - {img['type'].title()} (ID: {img['id']}): \"{img['prompt'][:50]}...\"")

        if recent_videos:
            context_parts.append(f"🎬 {len(recent_videos)} videos generated in last 10 minutes:")
            for vid in recent_videos[-5:]:
                source_info = f", from image {vid['source_image_id']}" if vid['source_image_id'] else ""
                context_parts.append(f"  - Video (ID: {vid['id']}{source_info}): \"{vid['prompt'][:50]}...\"")

        return "\n".join(context_parts)

    def get_latest_generated_images(self, limit: int = 5) -> List[Dict]:
        """
        Get the most recently generated images for use in image-to-video.

        Args:
            limit: Maximum number of images to return

        Returns:
            List of recent image data dictionaries
        """
        images = self.recently_generated_assets.get('images', [])
        return images[-limit:] if images else []

    def get_project_assets_context(self, project) -> str:
        """
        Get ALL assets from a specific project for long-term work.

        Session 122: Smart Hybrid - Use this when working in a project context
        for customer work that spans hours/days, not just 10-minute sessions.

        Args:
            project: CreativeProject instance

        Returns:
            Formatted string describing all project assets
        """
        from content.models import ImageHistory, VideoHistory

        try:
            # Session 129: Get MORE images so GPT can see early sequential numbers (not just recent)
            # Get images from project (last 50 - enough to see most assets including #1, #2, etc.)
            recent_images = ImageHistory.objects.filter(
                project=project
            ).order_by('created_at')[:50]  # Changed to chronological order so #1, #2, etc. appear first

            # Get videos from project (last 20)
            recent_videos = VideoHistory.objects.filter(
                project=project
            ).order_by('created_at')[:20]  # Changed to chronological order

            context_parts = [f"📁 **Project: {project.name}** (All assets available)"]

            if recent_images.exists():
                context_parts.append(f"\n📸 {recent_images.count()} recent images in project:")
                for img in recent_images:
                    # Determine type from prompt or image_type
                    img_type = 'image'
                    if 'logo' in img.prompt.lower():
                        img_type = 'logo'
                    elif any(word in img.prompt.lower() for word in ['character', 'mascot']):
                        img_type = 'character'
                    elif any(word in img.prompt.lower() for word in ['product', 'merchandise']):
                        img_type = 'product'

                    seq_num = img.get_sequential_number()
                    context_parts.append(f"  - Image #{seq_num}: {img_type.title()} (ID: {img.id}): \"{img.prompt[:50]}...\"")

            if recent_videos.exists():
                context_parts.append(f"\n🎬 {recent_videos.count()} recent videos in project:")
                for vid in recent_videos:
                    seq_num = vid.get_sequential_number()
                    source_info = f", from image {vid.source_image.id}" if vid.source_image else ""
                    context_parts.append(f"  - Video #{seq_num} (ID: {vid.id}{source_info}): \"{vid.prompt[:50]}...\"")

            if not recent_images.exists() and not recent_videos.exists():
                context_parts.append("\n⚠️ No assets in project yet")

            return "\n".join(context_parts)

        except Exception as e:
            logger.error(f"Error getting project assets context: {e}")
            return f"📁 Project: {project.name} (Unable to load assets)"

    def execute_database_query(self, query: str, params: List = None) -> Dict[str, Any]:
        """
        Execute a database query safely and return results.

        Args:
            query: SQL query to execute
            params: Query parameters for safe execution

        Returns:
            Dictionary with query results and metadata
        """
        try:
            with connection.cursor() as cursor:
                # Log the query for audit
                self.database_queries_executed.append({
                    'query': query,
                    'timestamp': timezone.now().isoformat(),
                    'user': self.user.username
                })

                # Execute query
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                # Fetch results
                if query.strip().upper().startswith('SELECT'):
                    columns = [col[0] for col in cursor.description]
                    results = cursor.fetchall()

                    # Convert to list of dictionaries
                    data = [dict(zip(columns, row)) for row in results]

                    return {
                        'success': True,
                        'data': data,
                        'count': len(data),
                        'query': query,
                        'columns': columns
                    }
                else:
                    # For non-SELECT queries, return affected rows
                    return {
                        'success': True,
                        'affected_rows': cursor.rowcount,
                        'query': query
                    }

        except Exception as e:
            logger.error(f"Database query error: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status including database, agents, and platform health.

        Returns:
            Dictionary with system status information
        """
        status = {
            'timestamp': timezone.now().isoformat(),
            'database': {},
            'agents': {},
            'embeddings': {},
            'platform': {},
            'websockets': {},
            'user': {}
        }

        try:
            # Check database status - use existing tables
            try:
                embeddings_count = self.execute_database_query(
                    "SELECT COUNT(*) as count FROM core_userembedding"
                )
                status['embeddings']['total_count'] = embeddings_count.get('data', [{}])[0].get('count', 0)

                # Check recent embeddings
                recent_embeddings = self.execute_database_query(
                    """
                    SELECT COUNT(*) as count
                    FROM core_userembedding
                    WHERE created_at > %s
                    """,
                    [timezone.now() - timedelta(days=1)]
                )
                status['embeddings']['last_24h'] = recent_embeddings.get('data', [{}])[0].get('count', 0)
            except Exception as e:
                logger.warning(f"Error checking embeddings: {e}")
                status['embeddings']['total_count'] = 0
                status['embeddings']['last_24h'] = 0

            # Check agents status
            agent_registry = get_agent_registry()
            status['agents']['total_registered'] = len(agent_registry.list_agents())
            status['agents']['categories'] = {}
            for agent in agent_registry.list_agents():
                category = agent.get('category', 'uncategorized')
                status['agents']['categories'][category] = status['agents']['categories'].get(category, 0) + 1

            # Check job applications
            job_apps_count = self.execute_database_query(
                "SELECT COUNT(*) as count FROM core_jobapplication WHERE user_id = %s",
                [self.user.id]
            )
            status['user']['job_applications'] = job_apps_count.get('data', [{}])[0].get('count', 0)

            # Check user embeddings
            user_embeddings_count = self.execute_database_query(
                "SELECT COUNT(*) as count FROM core_userembedding WHERE user_id = %s",
                [self.user.id]
            )
            status['user']['embeddings'] = user_embeddings_count.get('data', [{}])[0].get('count', 0)

            # Check WebSocket status
            try:
                from core.unified_hub import UnifiedWebSocketHub
                hub = UnifiedWebSocketHub()
                ws_status = hub.get_status()
                status['websockets'] = {
                    'active': ws_status.get('websocket_active', False),
                    'connections': ws_status.get('active_connections', 0),
                    'last_message': ws_status.get('last_message_time')
                }
            except Exception as e:
                status['websockets']['error'] = str(e)

            # Calculate platform operational percentage
            operational_checks = [
                status['embeddings']['total_count'] > 0,
                status['agents']['total_registered'] > 0,
                status.get('websockets', {}).get('active', False),
                'error' not in status.get('database', {})
            ]
            status['platform']['operational_percentage'] = (sum(operational_checks) / len(operational_checks)) * 100

            # Platform health summary
            status['platform']['health'] = 'healthy' if status['platform']['operational_percentage'] > 75 else 'degraded'
            status['platform']['summary'] = f"Platform is {status['platform']['operational_percentage']:.0f}% operational"

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            status['error'] = str(e)
            status['platform']['health'] = 'error'

        return status

    def search_embeddings(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search embeddings database for relevant content.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching embeddings with metadata
        """
        try:
            # Search in unified embeddings
            results = self.execute_database_query(
                """
                SELECT
                    id, content_type, content_id, content_text,
                    metadata, relevance_score, created_at
                FROM self_awareness_unifiedembedding
                WHERE content_text ILIKE %s
                ORDER BY relevance_score DESC, created_at DESC
                LIMIT %s
                """,
                [f'%{query}%', limit]
            )

            if results.get('success'):
                return results.get('data', [])

            # Fallback to user embeddings
            user_results = self.execute_database_query(
                """
                SELECT
                    id, content, confidence_score,
                    metadata, created_at
                FROM core_userembedding
                WHERE user_id = %s AND content ILIKE %s
                ORDER BY confidence_score DESC, created_at DESC
                LIMIT %s
                """,
                [self.user.id, f'%{query}%', limit]
            )

            return user_results.get('data', [])

        except Exception as e:
            logger.error(f"Error searching embeddings: {e}")
            return []

    def execute_agent(self, agent_name: str, task: str) -> Dict[str, Any]:
        """
        Execute an agent with a specific task.

        Args:
            agent_name: Name of the agent to execute
            task: Task description for the agent

        Returns:
            Agent execution results
        """
        try:
            agent_registry = get_agent_registry()

            # Find the agent
            agents = [a for a in agent_registry.list_agents() if agent_name.lower() in a.get('name', '').lower()]

            if not agents:
                return {
                    'success': False,
                    'error': f'Agent "{agent_name}" not found',
                    'available_agents': [a.get('name') for a in agent_registry.list_agents()[:10]]
                }

            agent = agents[0]

            # Execute agent (simplified - in production this would use proper agent execution)
            result = {
                'success': True,
                'agent': agent.get('name'),
                'task': task,
                'status': 'executed',
                'message': f"Agent {agent.get('name')} has been triggered with task: {task}",
                'metadata': {
                    'category': agent.get('category'),
                    'description': agent.get('description'),
                    'timestamp': datetime.now().isoformat()
                }
            }

            return result

        except Exception as e:
            logger.error(f"Error executing agent: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _generate_intelligent_fallback(self, message: str, context: Dict[str, Any]) -> str:
        """
        Generate an intelligent fallback response when AI is unavailable.
        Uses context and patterns to create relevant response.
        """
        # Extract user context properly
        user_context = context.get('user_context', {})
        user_name = user_context.get('first_name') or context.get('first_name', 'there')
        conversation_context = context.get('conversation_context', '')

        # Analyze message for key topics
        message_lower = message.lower()

        # Profile-related responses
        if any(word in message_lower for word in ['profile', 'professional', 'setup', 'setting up']):
            if 'professional' in message_lower:
                if any(word in message_lower for word in ['feeling out', 'exploring', 'looking at', 'checking out']):
                    return f"Hi {user_name}! I understand you're exploring the Professional profile section to see what options are available. The Professional profile typically includes advanced fields like core competencies, quarterly objectives, delegation preferences, and detailed work schedules. Would you like me to walk you through what each section does, or do you have specific areas you'd like to understand better?"
                else:
                    return f"Hi {user_name}! I can help you set up your Professional profile. This includes defining your primary role, core competencies, communication style, long-term goals, and work preferences. What aspect would you like to start with?"

        # Check for system commands
        if 'status' in message_lower:
            status = self.get_system_status()
            return f"Hi {user_name}! System is {status.get('platform', {}).get('operational_percentage', 0):.0f}% operational with {status.get('embeddings', {}).get('total_count', 0)} embeddings and {status.get('agents', {}).get('total_registered', 0)} agents ready."

        if 'help' in message_lower:
            return f"Hi {user_name}! I can help you with job searches, profile management, agent execution, and system queries. What would you like to explore?"

        if 'agent' in message_lower:
            return f"Hi {user_name}! I have access to {len(get_agent_registry().list_agents())} specialized agents. Would you like me to list them or execute a specific one?"

        # Context-aware responses
        if conversation_context and 'profile' in conversation_context.lower():
            return f"Hi {user_name}! Continuing our discussion about profiles - what specific aspect would you like to explore or set up next?"

        # Default personalized response
        recent_project = self.enhanced_profile.current_projects[0] if self.enhanced_profile.current_projects else None
        if recent_project:
            return f"Hi {user_name}! I see you're working on {recent_project}. How can I assist you with that today?"
        else:
            return f"Hello {user_name}! I'm here to help with your goals. What would you like to work on?"

    def _generate_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override parent's template-based response with real AI.

        Args:
            message: User's message
            context: Context dictionary

        Returns:
            Response dictionary with AI-generated content
        """
        logger.debug("_generate_response() ENTERED, calling _generate_ai_response()")
        # Generate real AI response
        ai_response = self._generate_ai_response(message, context)
        logger.debug(f"_generate_ai_response() returned type={type(ai_response)}")

        # Session 155 Fix: Handle dict response with tool_calls
        if isinstance(ai_response, dict) and 'tool_calls' in ai_response:
            # GPT requested tool calls - return them to frontend
            response_text = ai_response.get('text', '')
            raw_tool_calls = ai_response['tool_calls']

            # Transform Responses API format to frontend-expected format
            # Responses API: {function: {name, arguments}}
            # Frontend expects: {name, arguments} where arguments is a dict
            tool_calls = []
            for tool_call in raw_tool_calls:
                if 'function' in tool_call:
                    # Flatten the structure and parse arguments JSON string
                    arguments_str = tool_call['function']['arguments']
                    try:
                        # Parse JSON string to dict
                        arguments_dict = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
                    except json.JSONDecodeError:
                        logger.warning(f"⚠️ Could not parse arguments JSON: {arguments_str}")
                        arguments_dict = {}

                    tool_calls.append({
                        'name': tool_call['function']['name'],
                        'arguments': arguments_dict
                    })
                else:
                    # Already in correct format
                    tool_calls.append(tool_call)

            logger.info(f"🔧 Passing {len(tool_calls)} tool_calls to frontend (flattened format)")

            response_data = {
                'response': response_text,
                'tool_calls': tool_calls,
                'suggestions': self.generate_personalized_suggestions(message),
                'actions': [],  # No actions when tools are being called
                'confidence': 0.95,  # High confidence for tool execution
                'ai_generated': True,
                'model': 'gpt-5-mini'
            }

            # Session 518: Pass through project_created if content generated a project
            if isinstance(ai_response, dict) and 'project_created' in ai_response:
                response_data['project_created'] = ai_response['project_created']
                logger.info(f"📁 Session 518: Passing project_created to frontend: {ai_response['project_created'].get('project_name')}")

            return response_data

        # No tool calls - regular text response
        response_text = ai_response if isinstance(ai_response, str) else str(ai_response)

        # Determine intent for suggestions
        intent = context.get('intent', 'general')

        # Generate smart suggestions based on context and AI response
        suggestions = self.generate_personalized_suggestions(message)

        # Determine confidence based on whether we used real AI or fallback
        confidence = 0.9 if 'Generated REAL AI response' in str(logger) else 0.6

        # Build response dictionary
        response_data = {
            'response': response_text,
            'suggestions': suggestions,
            'actions': self._extract_actions_from_response(response_text),
            'confidence': confidence,
            'ai_generated': True,  # Flag to indicate real AI was used
            'model': 'gpt-5-mini' if self.llm_enforcer.openai_client else 'intelligent-fallback'
        }

        return response_data

    def _extract_actions_from_response(self, response: str) -> List[str]:
        """
        Extract potential actions from AI response.

        Args:
            response: AI-generated response

        Returns:
            List of action identifiers
        """
        actions = []
        response_lower = response.lower()

        # Map keywords to actions
        action_map = {
            'search': ['search_jobs', 'search_embeddings'],
            'agent': ['list_agents', 'execute_agent'],
            'profile': ['edit_profile', 'view_profile'],
            'job': ['search_jobs', 'view_applications'],
            'status': ['system_status', 'check_health'],
            'help': ['show_help_menu']
        }

        for keyword, action_list in action_map.items():
            if keyword in response_lower:
                actions.extend(action_list)

        return list(set(actions))[:5]  # Return unique actions, max 5

    def process_system_command(self, command: str) -> Dict[str, Any]:
        """
        Process system-level commands from the assistant.

        Args:
            command: System command to process

        Returns:
            Command execution results
        """
        command_lower = command.lower()

        # Database status command
        if 'database' in command_lower or 'embeddings count' in command_lower:
            status = self.get_system_status()
            return {
                'type': 'system_status',
                'embeddings': status.get('embeddings'),
                'database_health': status.get('platform', {}).get('health'),
                'response': f"Database contains {status.get('embeddings', {}).get('total_count', 0)} embeddings. "
                           f"Platform is {status.get('platform', {}).get('operational_percentage', 0):.0f}% operational."
            }

        # Search embeddings command
        elif 'search' in command_lower and 'embedding' in command_lower:
            # Extract search term (simple extraction)
            search_term = command.replace('search embeddings', '').replace('search embedding', '').strip()
            if search_term:
                results = self.search_embeddings(search_term, limit=3)
                return {
                    'type': 'search_results',
                    'query': search_term,
                    'count': len(results),
                    'results': results,
                    'response': f"Found {len(results)} embeddings matching '{search_term}'"
                }

        # WebSocket status
        elif 'websocket' in command_lower:
            status = self.get_system_status()
            ws_status = status.get('websockets', {})
            return {
                'type': 'websocket_status',
                'status': ws_status,
                'response': f"WebSocket hub is {'active' if ws_status.get('active') else 'inactive'}. "
                           f"Active connections: {ws_status.get('connections', 0)}"
            }

        # Agent list command
        elif 'list agents' in command_lower:
            agent_registry = get_agent_registry()
            agents = agent_registry.list_agents()[:10]  # First 10 agents
            return {
                'type': 'agent_list',
                'total_agents': len(agent_registry.list_agents()),
                'sample_agents': [a.get('name') for a in agents],
                'response': f"System has {len(agent_registry.list_agents())} registered agents. "
                           f"Sample: {', '.join([a.get('name') for a in agents[:5]])}"
            }

        # Execute agent command
        elif 'execute agent' in command_lower or 'run agent' in command_lower:
            # Simple parsing - in production this would be more sophisticated
            parts = command.split(' ')
            if len(parts) > 2:
                agent_name = parts[2] if 'agent' in parts else parts[1]
                task = ' '.join(parts[3:]) if len(parts) > 3 else 'default task'
                result = self.execute_agent(agent_name, task)
                return {
                    'type': 'agent_execution',
                    'result': result,
                    'response': result.get('message', 'Agent execution completed')
                }

        return {
            'type': 'unknown_command',
            'response': "I can help with database queries, embeddings search, system status, and agent execution. "
                       "Try: 'check database status', 'search embeddings [term]', 'list agents', or 'execute agent [name] [task]'"
        }

    def get_enhanced_context(self) -> Dict[str, Any]:
        """
        Get enhanced context with system status and profile data.

        Returns:
            Enhanced context dictionary
        """
        # Get base context
        context = self.get_personalized_context()

        # Add system status
        system_status = self.get_system_status()
        context['system'] = {
            'database_healthy': system_status.get('platform', {}).get('health') == 'healthy',
            'total_embeddings': system_status.get('embeddings', {}).get('total_count', 0),
            'total_agents': system_status.get('agents', {}).get('total_registered', 0),
            'websocket_active': system_status.get('websockets', {}).get('active', False),
            'operational_percentage': system_status.get('platform', {}).get('operational_percentage', 0)
        }

        # Add recent database queries
        context['system']['recent_queries'] = len(self.database_queries_executed)

        # Add enhanced profile context
        if hasattr(self, 'enhanced_profile'):
            context['enhanced_profile'] = self.enhanced_profile.get_context_for_ai('general')

        return context

    def store_memory(self, memory_type: str, content: str, **kwargs) -> UserMemoryContext:
        """
        Store a memory using UnifiedMemoryManager.

        Args:
            memory_type: Type of memory (decision, preference, etc.)
            content: Content of the memory
            **kwargs: Additional metadata

        Returns:
            Created UserMemoryContext instance
        """
        memory = self.memory_manager.store_memory(
            user=self.user,
            source='assistant',
            memory_type=memory_type,
            content=content,
            importance=kwargs.get('importance', 5),
            related_project=kwargs.get('related_project', ''),
            related_goal=kwargs.get('related_goal', ''),
            tags=kwargs.get('tags', []),
            metadata=kwargs.get('metadata', {})
        )
        logger.info(f"Stored {memory_type} memory via UnifiedMemoryManager for {self.user.username}: {content[:50]}...")
        return memory

    def retrieve_memories(self, memory_type: str = None, limit: int = 10) -> List[UserMemoryContext]:
        """
        Retrieve user memories.

        Args:
            memory_type: Filter by memory type (optional)
            limit: Maximum number of memories to retrieve

        Returns:
            List of UserMemoryContext instances
        """
        query = UserMemoryContext.objects.filter(user=self.user)

        if memory_type:
            query = query.filter(memory_type=memory_type)

        memories = query[:limit]

        # Update access counts
        for memory in memories:
            memory.accessed_count += 1
            memory.last_accessed = timezone.now()
            memory.save(update_fields=['accessed_count', 'last_accessed'])

        return list(memories)

    def update_profile_from_interaction(self, message: str, response: str):
        """
        Enhanced profile update with intelligent pattern extraction and learning.

        Args:
            message: User's message
            response: Assistant's response
        """
        message_lower = message.lower()
        updates_made = []

        # Detect and store preferences
        if 'prefer' in message_lower or 'like' in message_lower or 'favorite' in message_lower:
            self.store_memory('preference', message, importance=7)
            updates_made.append('preference')

        # Detect goals
        if 'goal' in message_lower or 'want to' in message_lower or 'plan to' in message_lower:
            self.store_memory('goal', message, importance=8)
            updates_made.append('goal')

            # Extract and update long-term goals if mentioned
            if 'long term' in message_lower or 'future' in message_lower:
                goal_text = self.extract_goal_text(message)
                if goal_text and goal_text not in (self.enhanced_profile.long_term_goals or []):
                    if not self.enhanced_profile.long_term_goals:
                        self.enhanced_profile.long_term_goals = []
                    self.enhanced_profile.long_term_goals.append(goal_text)
                    self.enhanced_profile.save(update_fields=['long_term_goals'])
                    logger.info(f"Added long-term goal for {self.user.username}: {goal_text}")

        # Detect decisions
        if 'decide' in message_lower or 'choose' in message_lower or 'selected' in message_lower:
            self.store_memory('decision', message, importance=6)
            updates_made.append('decision')

        # Extract skills mentioned
        skill_keywords = ['know', 'can', 'skilled in', 'experience with', 'worked with', 'expert in']
        if any(keyword in message_lower for keyword in skill_keywords):
            skills = self.extract_skills(message)
            if skills:
                current_skills = self.enhanced_profile.core_competencies or {}
                for skill in skills:
                    if skill not in current_skills:
                        # Add with default proficiency level 5
                        current_skills[skill] = 5
                if len(current_skills) > len(self.enhanced_profile.core_competencies or {}):
                    self.enhanced_profile.core_competencies = current_skills
                    self.enhanced_profile.save(update_fields=['core_competencies'])
                    new_skills = [s for s in skills if s not in (self.enhanced_profile.core_competencies or {})]
                    self.store_memory('skill', f"Identified skills: {', '.join(skills)}", importance=6)
                    logger.info(f"Added skills for {self.user.username}: {skills}")

        # Extract project mentions
        project_keywords = ['working on', 'project', 'building', 'developing', 'creating']
        if any(keyword in message_lower for keyword in project_keywords):
            projects = self.extract_projects(message)
            if projects:
                current_projects = self.enhanced_profile.current_projects or []
                new_projects = [p for p in projects if p not in current_projects]
                if new_projects:
                    self.enhanced_profile.current_projects = current_projects + new_projects
                    self.enhanced_profile.save(update_fields=['current_projects'])
                    self.store_memory('project', f"Working on: {', '.join(new_projects)}", importance=7)
                    logger.info(f"Added projects for {self.user.username}: {new_projects}")

        # Detect communication style patterns
        if self.enhanced_profile.interaction_count > 5:
            # After 5 interactions, start detecting patterns
            self.detect_communication_patterns(message)

        # Track profile access
        if hasattr(self, 'enhanced_profile'):
            self.enhanced_profile.interaction_count += 1
            self.enhanced_profile.save(update_fields=['interaction_count'])

        # Store summary of what was learned
        if updates_made:
            self.store_memory(
                'learning',
                f"Learned about: {', '.join(updates_made)}",
                importance=5,
                metadata={'message': message[:200], 'categories': updates_made}
            )

    def generate_personalized_suggestions(self, message: str) -> List[str]:
        """
        Generate personalized suggestions based on user profile and message context.

        Args:
            message: User's message

        Returns:
            List of personalized suggestions
        """
        suggestions = []

        # Base suggestions on user's primary role
        if self.enhanced_profile.primary_role:
            if 'engineer' in self.enhanced_profile.primary_role.lower():
                suggestions.extend(['Review code', 'Check system status', 'Run tests'])
            elif 'manager' in self.enhanced_profile.primary_role.lower():
                suggestions.extend(['Review team progress', 'Check project status', 'Schedule meeting'])
            elif 'designer' in self.enhanced_profile.primary_role.lower():
                suggestions.extend(['Review designs', 'Check feedback', 'Update portfolio'])

        # Add suggestions based on current projects
        if self.enhanced_profile.current_projects:
            for project in self.enhanced_profile.current_projects[:2]:
                suggestions.append(f"Update on {project}")

        # Add goal-based suggestions
        if self.enhanced_profile.long_term_goals:
            suggestions.append('Review goal progress')

        # Default suggestions if none generated
        if not suggestions:
            suggestions = ['Tell me more', 'Show options', 'Help me decide', 'What else?']

        return suggestions[:5]  # Limit to 5 suggestions

    def get_detailed_explanation(self, message: str) -> str:
        """
        Generate detailed explanation for users who prefer detailed communication.

        Args:
            message: User's message

        Returns:
            Detailed explanation string
        """
        explanations = []

        # Add context about the message type
        if 'how' in message.lower():
            explanations.append("This appears to be a how-to question. I'll provide step-by-step guidance.")
        elif 'why' in message.lower():
            explanations.append("This is a reasoning question. I'll explain the underlying concepts.")
        elif 'what' in message.lower():
            explanations.append("This is a definitional question. I'll provide clear explanations.")

        # Add profile-based context
        if self.enhanced_profile.learning_style == 'visual':
            explanations.append("Based on your visual learning style, I'll try to paint a clear picture.")
        elif self.enhanced_profile.learning_style == 'hands-on':
            explanations.append("Given your hands-on learning preference, I'll include practical examples.")

        return ' '.join(explanations) if explanations else ''

    def make_concise(self, response: str, max_length: int = 200) -> str:
        """
        Make response more concise for users who prefer brief communication.

        Args:
            response: Original response
            max_length: Maximum length for concise response

        Returns:
            Concise version of the response
        """
        if len(response) <= max_length:
            return response

        # Try to cut at sentence boundary
        sentences = response.split('. ')
        concise = []
        current_length = 0

        for sentence in sentences:
            if current_length + len(sentence) <= max_length:
                concise.append(sentence)
                current_length += len(sentence) + 2  # +2 for '. '
            else:
                break

        result = '. '.join(concise)
        if result and not result.endswith('.'):
            result += '.'

        return result if result else response[:max_length] + '...'

    def extract_goal_text(self, message: str) -> Optional[str]:
        """
        Extract goal text from user message.

        Args:
            message: User's message containing goal

        Returns:
            Extracted goal text or None
        """
        # Simple extraction - in production this would use NLP
        goal_phrases = ['want to', 'goal is to', 'plan to', 'aiming to', 'hoping to']

        for phrase in goal_phrases:
            if phrase in message.lower():
                start = message.lower().index(phrase) + len(phrase)
                # Extract up to next punctuation or end
                end = len(message)
                for punct in ['.', '!', '?', ',', ';']:
                    if punct in message[start:]:
                        end = start + message[start:].index(punct)
                        break

                goal = message[start:end].strip()
                # Clean up common words
                goal = goal.replace(' to ', ' ').replace(' the ', ' ')
                return goal[:100]  # Limit length

        return None

    def extract_skills(self, message: str) -> List[str]:
        """
        Extract skills mentioned in user message.

        Args:
            message: User's message

        Returns:
            List of extracted skills
        """
        skills = []

        # Common skill patterns
        skill_patterns = [
            'know ', 'skilled in ', 'experience with ', 'worked with ',
            'expert in ', 'familiar with ', 'proficient in '
        ]

        message_lower = message.lower()
        for pattern in skill_patterns:
            if pattern in message_lower:
                start = message_lower.index(pattern) + len(pattern)
                # Extract word or phrase after pattern
                words = message[start:].split()
                if words:
                    # Take up to 3 words as skill
                    skill = ' '.join(words[:3]).strip('.,!?;')
                    if len(skill) > 2:  # Minimum skill length
                        skills.append(skill)

        # Common tech skills mentioned directly
        tech_skills = ['Python', 'JavaScript', 'React', 'Django', 'SQL', 'Docker',
                      'AWS', 'Machine Learning', 'AI', 'DevOps', 'Kubernetes']

        for skill in tech_skills:
            if skill.lower() in message_lower and skill not in skills:
                skills.append(skill)

        return skills[:10]  # Limit to 10 skills

    def extract_projects(self, message: str) -> List[str]:
        """
        Extract project names or descriptions from message.

        Args:
            message: User's message

        Returns:
            List of project names/descriptions
        """
        projects = []

        # Project indicators
        project_patterns = [
            'working on ', 'building ', 'developing ', 'creating ',
            'project called ', 'project named '
        ]

        message_lower = message.lower()
        for pattern in project_patterns:
            if pattern in message_lower:
                start = message_lower.index(pattern) + len(pattern)
                # Extract following words
                words = message[start:].split()
                if words:
                    # Take up to 5 words as project description
                    project = ' '.join(words[:5]).strip('.,!?;')
                    if len(project) > 2:
                        projects.append(project)

        return projects[:5]  # Limit to 5 projects

    def detect_communication_patterns(self, message: str):
        """
        Detect and update communication style patterns.

        Args:
            message: User's message
        """
        # Analyze message length patterns
        recent_memories = self.retrieve_memories('interaction', limit=10)

        if len(recent_memories) >= 5:
            avg_length = sum(len(m.content) for m in recent_memories) / len(recent_memories)

            # Detect communication style
            if avg_length < 50:
                new_style = 'concise'
            elif avg_length > 200:
                new_style = 'detailed'
            else:
                new_style = 'balanced'

            # Update if different from current
            if self.enhanced_profile.communication_style != new_style:
                self.enhanced_profile.communication_style = new_style
                self.enhanced_profile.save(update_fields=['communication_style'])
                self.store_memory(
                    'pattern',
                    f"Communication style updated to: {new_style}",
                    importance=6
                )
                logger.info(f"Updated communication style for {self.user.username}: {new_style}")

        # Detect question patterns
        if '?' in message:
            # User asks questions - might prefer interactive style
            question_count = sum(1 for m in recent_memories if '?' in m.content)
            if question_count > len(recent_memories) * 0.7:  # 70% questions
                if self.enhanced_profile.learning_style != 'interactive':
                    self.enhanced_profile.learning_style = 'interactive'
                    self.enhanced_profile.save(update_fields=['learning_style'])
                    logger.info(f"Detected interactive learning style for {self.user.username}")

    def _store_conversation(self, message: str, response_data: Dict[str, Any]) -> None:
        """
        Store conversation in database for persistence and future retrieval.

        Args:
            message: User's message
            response_data: Assistant's response data
        """
        try:
            from core.models import ConversationMemory, ChatConversation
            import uuid

            # Store in ConversationMemory for learning
            ConversationMemory.objects.create(
                user=self.user,
                message=message,
                response=response_data.get('response', ''),
                agents_used=response_data.get('agents_used', []),
                intent=response_data.get('intent', 'general'),
                success=True
            )

            # Store in ChatConversation for detailed tracking
            ChatConversation.objects.create(
                user=self.user,
                conversation_id=str(uuid.uuid4()),
                user_message=message,
                assistant_response=response_data.get('response', ''),
                context_used=response_data.get('context', {}),
                metadata={
                    'confidence': response_data.get('confidence', 0.5),
                    'ai_generated': response_data.get('ai_generated', False),
                    'model': response_data.get('model', 'unknown'),
                    'actions': response_data.get('actions', []),
                    'suggestions': response_data.get('suggestions', [])
                },
                response_time_ms=response_data.get('response_time_ms', 0)
            )

            # Create embedding for the conversation
            self._create_conversation_embedding(message, response_data.get('response', ''))

            logger.info(f"💾 Stored conversation for {self.user.username}: {message[:50]}...")

        except Exception as e:
            logger.error(f"Error storing conversation: {e}")

    def _create_conversation_embedding(self, message: str, response: str) -> None:
        """
        Create embedding for conversation to enable semantic search.

        Args:
            message: User's message
            response: Assistant's response
        """
        try:
            from core.models import UserEmbedding

            # Combine message and response for comprehensive context
            combined_text = f"User: {message}\nAssistant: {response}"

            # Use wrapper method to create embedding (properly formats arguments)
            self.store_memory(
                'conversation',
                combined_text,
                metadata={
                    'message': message,
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                }
            )

            # Also create direct UserEmbedding for compatibility
            UserEmbedding.objects.create(
                user=self.user,
                content=combined_text,
                content_type='conversation',
                source='personal_assistant',
                metadata={
                    'message_length': len(message),
                    'response_length': len(response),
                    'conversation_type': 'interactive'
                }
            )

            logger.info(f"🧠 Created conversation embedding for {self.user.username}")

        except Exception as e:
            logger.error(f"Error creating conversation embedding: {e}")

    def _load_conversation_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Load recent conversation history from database.

        Args:
            limit: Maximum number of conversations to load

        Returns:
            List of conversation dictionaries
        """
        try:
            from core.models import ConversationMemory

            conversations = ConversationMemory.objects.filter(
                user=self.user
            ).order_by('-created_at')[:limit]

            return [
                {
                    'message': conv.message,
                    'response': conv.response,
                    'timestamp': conv.created_at.isoformat(),
                    'intent': conv.intent
                }
                for conv in conversations
            ]

        except Exception as e:
            logger.error(f"Error loading conversation history: {e}")
            return []

    def _analyze_user_patterns(self) -> Dict[str, Any]:
        """
        Analyze user conversation patterns and preferences.

        Returns:
            Dictionary containing user patterns and preferences
        """
        try:
            from core.models import ConversationMemory, UserProfile
            from collections import Counter
            import json

            # Get user conversations
            conversations = ConversationMemory.objects.filter(
                user=self.user
            ).order_by('-created_at')[:50]  # Last 50 conversations

            if not conversations:
                return {}

            # Analyze conversation patterns
            intents = [conv.intent for conv in conversations if conv.intent]
            agents_used = []
            for conv in conversations:
                if conv.agents_used:
                    if isinstance(conv.agents_used, str):
                        try:
                            agents_used.extend(json.loads(conv.agents_used))
                        except Exception as _e:
                            logger.warning(
                                "epa_handlers_utility._analyze_user_patterns: swallowed (%s: %s) — degraded",
                                type(_e).__name__, _e,
                            )
                    elif isinstance(conv.agents_used, list):
                        agents_used.extend(conv.agents_used)

            # Get user profile if exists
            user_profile = None
            try:
                user_profile = UserProfile.objects.get(user=self.user)
            except UserProfile.DoesNotExist:
                pass

            patterns = {
                'conversation_count': len(conversations),
                'common_intents': dict(Counter(intents).most_common(5)),
                'preferred_agents': dict(Counter(agents_used).most_common(5)),
                'interaction_frequency': self._calculate_interaction_frequency(conversations),
                'user_profile': {
                    'skills': user_profile.skills if user_profile and user_profile.skills else [],
                    'current_role': user_profile.current_role if user_profile and user_profile.current_role else '',
                    'occupation': user_profile.occupation if user_profile and user_profile.occupation else '',
                    'industries': user_profile.industries if user_profile and user_profile.industries else [],
                    'remote_only': user_profile.remote_only if user_profile else False,
                    'preferred_ai_model': user_profile.preferred_ai_model if user_profile and user_profile.preferred_ai_model else '',
                } if user_profile else {}
            }

            return patterns

        except Exception as e:
            logger.error(f"Error analyzing user patterns: {e}")
            return {}

    def _calculate_interaction_frequency(self, conversations) -> str:
        """Calculate user interaction frequency."""
        if len(conversations) < 2:
            return "new_user"

        from datetime import timedelta

        now = timezone.now()
        seven_days_ago = now - timedelta(days=7)
        # Session 802: Fix offset-naive vs offset-aware comparison
        # Compare created_at directly (both are timezone-aware in Django)
        recent_conversations = [
            conv for conv in conversations
            if conv.created_at >= seven_days_ago
        ]

        weekly_count = len(recent_conversations)

        if weekly_count >= 20:
            return "very_active"
        elif weekly_count >= 10:
            return "active"
        elif weekly_count >= 3:
            return "regular"
        else:
            return "occasional"

    def _create_personalized_context(self, message: str, patterns: Dict[str, Any]) -> str:
        """
        Create personalized context based on user patterns and current message.

        Args:
            message: Current user message
            patterns: User patterns from analysis

        Returns:
            Personalized context string
        """
        context_parts = []

        # User interaction profile
        frequency = patterns.get('interaction_frequency', 'new_user')
        conv_count = patterns.get('conversation_count', 0)

        if frequency == "very_active":
            context_parts.append("🔥 Very active user - provide detailed, advanced responses")
        elif frequency == "active":
            context_parts.append("⚡ Active user - can handle comprehensive information")
        elif frequency == "regular":
            context_parts.append("👤 Regular user - balance detail with clarity")
        else:
            context_parts.append("🌟 Welcome! Provide clear, helpful introductory responses")

        # User preferences and skills
        user_profile = patterns.get('user_profile', {})
        if user_profile.get('skills'):
            skills_text = ", ".join(user_profile['skills'][:3])
            context_parts.append(f"💼 User skills: {skills_text}")

        if user_profile.get('goals'):
            goals_text = ", ".join(user_profile['goals'][:2])
            context_parts.append(f"🎯 User goals: {goals_text}")

        # Common intents
        common_intents = patterns.get('common_intents', {})
        if common_intents:
            top_intent = next(iter(common_intents.keys()))
            context_parts.append(f"🧠 User typically asks about: {top_intent}")

        # Preferred agents
        preferred_agents = patterns.get('preferred_agents', {})
        if preferred_agents:
            top_agents = list(preferred_agents.keys())[:2]
            context_parts.append(f"🤖 Often uses: {', '.join(top_agents)}")

        # Message intent analysis
        message_lower = message.lower()
        if any(word in message_lower for word in ['urgent', 'asap', 'quickly', 'fast']):
            context_parts.append("⚡ URGENT REQUEST - Prioritize speed and direct answers")
        elif any(word in message_lower for word in ['explain', 'how', 'why', 'understand']):
            context_parts.append("📚 LEARNING REQUEST - Provide educational, detailed responses")
        elif any(word in message_lower for word in ['help', 'stuck', 'problem', 'issue']):
            context_parts.append("🆘 HELP REQUEST - Focus on practical solutions")

        if context_parts:
            return "PERSONALIZATION CONTEXT:\n" + "\n".join(context_parts) + "\n\n"

        return ""

    def _enhance_response_with_memory(self, response: str, patterns: Dict[str, Any]) -> str:
        """
        Enhance response with memory-based personalization.

        Args:
            response: Original response
            patterns: User patterns

        Returns:
            Enhanced response
        """
        try:
            # Add memory-based enhancements
            enhancements = []

            # Reference past interactions if relevant
            conv_count = patterns.get('conversation_count', 0)
            if conv_count > 5:
                frequency = patterns.get('interaction_frequency', 'new_user')
                if frequency in ['active', 'very_active']:
                    enhancements.append("Based on our previous conversations")

            # Suggest relevant agents based on past usage
            preferred_agents = patterns.get('preferred_agents', {})
            if preferred_agents and len(preferred_agents) > 0:
                top_agent = next(iter(preferred_agents.keys()))
                if 'opportunity' in response.lower() or 'job' in response.lower():
                    enhancements.append(f"You might also want to try the {top_agent} agent")

            # Add goal-oriented suggestions
            user_goals = patterns.get('user_profile', {}).get('goals', [])
            if user_goals and any(goal in response.lower() for goal in [g.lower() for g in user_goals]):
                enhancements.append("This aligns with your stated goals")

            # Enhance response if we have enhancements
            if enhancements:
                enhanced_parts = [response]
                enhanced_parts.append("\n💡 Personal Notes:")
                for enhancement in enhancements:
                    enhanced_parts.append(f"  • {enhancement}")

                return "\n".join(enhanced_parts)

            return response

        except Exception as e:
            logger.error(f"Error enhancing response with memory: {e}")
            return response

    # =====================================================
    # AGENT COMMUNICATION BRIDGE METHODS
    # =====================================================

    def route_to_agent(self, task: str, agent_type: str = None, required_capabilities: List[str] = None) -> Dict[str, Any]:
        """
        Route a task to the most appropriate agent.

        Args:
            task: Task description
            agent_type: Preferred agent type/specialization
            required_capabilities: Required agent capabilities

        Returns:
            Agent routing and execution results
        """
        try:
            # Find the best agent for the task
            best_agent = self.agent_registry.find_best_agent(
                task_description=task,
                required_capabilities=required_capabilities,
                preferred_specialization=agent_type
            )

            if not best_agent:
                return {
                    'success': False,
                    'error': 'No suitable agent found for this task',
                    'suggestions': self._suggest_alternative_agents(task)
                }

            # Execute the agent
            execution_id = self.agent_registry.execute_agent(
                agent_name=best_agent['name'],
                task_data={
                    'task': task,
                    'user_id': str(self.user.id),  # Convert to string for JSON serialization
                    'context': self._get_agent_context()
                }
            )

            if execution_id:
                # Store agent interaction as memory
                self.store_memory(
                    'agent_interaction',
                    f"Routed task to {best_agent['name']}: {task}",
                    importance=7,
                    metadata={
                        'agent_name': best_agent['name'],
                        'execution_id': execution_id,
                        'task': task
                    }
                )

                logger.info(f"🤖 Routed task to agent {best_agent['name']} for {self.user.username}")

                return {
                    'success': True,
                    'agent': best_agent,
                    'execution_id': execution_id,
                    'message': f"Task routed to {best_agent['display_name']} agent",
                    'status': 'initiated'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to execute agent',
                    'agent': best_agent
                }

        except Exception as e:
            logger.error(f"Error routing to agent: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_agent_response(self, agent_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get response from a specific agent.

        Args:
            agent_id: Agent identifier
            task_data: Task data to send to agent

        Returns:
            Agent response data
        """
        try:
            # Get agent details
            agent = self.agent_registry.get_agent(agent_id)
            if not agent:
                return {
                    'success': False,
                    'error': f'Agent {agent_id} not found'
                }

            # Execute agent with enhanced task data
            enhanced_task_data = {
                **task_data,
                'user_profile': self.enhanced_profile.get_context_for_ai('agent'),
                'user_preferences': {
                    'communication_style': self.enhanced_profile.communication_style,
                    'learning_style': self.enhanced_profile.learning_style
                },
                'context': self._get_agent_context()
            }

            execution_id = self.agent_registry.execute_agent(agent_id, enhanced_task_data)

            if execution_id:
                # Monitor execution status
                status = self.agent_registry.get_execution_status(execution_id)

                # Store interaction
                self.store_memory(
                    'agent_response',
                    f"Got response from {agent['name']}: {task_data.get('task', 'No task specified')}",
                    importance=6,
                    metadata={
                        'agent_id': agent_id,
                        'execution_id': execution_id,
                        'status': status
                    }
                )

                return {
                    'success': True,
                    'agent_id': agent_id,
                    'agent_name': agent['name'],
                    'execution_id': execution_id,
                    'status': status,
                    'response_available': status.get('status') == 'completed'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to get agent response'
                }

        except Exception as e:
            logger.error(f"Error getting agent response: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def aggregate_agent_results(self, execution_ids: List[str]) -> Dict[str, Any]:
        """
        Aggregate results from multiple agent executions.

        Args:
            execution_ids: List of agent execution IDs

        Returns:
            Aggregated results from all agents
        """
        try:
            results = []
            successful_executions = 0
            failed_executions = 0

            for execution_id in execution_ids:
                status = self.agent_registry.get_execution_status(execution_id)
                if status:
                    results.append(status)
                    if status.get('status') == 'completed':
                        successful_executions += 1
                    elif status.get('status') == 'failed':
                        failed_executions += 1

            # Analyze results for patterns and insights
            insights = self._analyze_agent_results(results)

            # Store aggregated results as memory
            self.store_memory(
                'agent_aggregation',
                f"Aggregated results from {len(execution_ids)} agents",
                importance=8,
                metadata={
                    'execution_ids': execution_ids,
                    'successful_count': successful_executions,
                    'failed_count': failed_executions,
                    'insights': insights
                }
            )

            return {
                'success': True,
                'total_executions': len(execution_ids),
                'successful_executions': successful_executions,
                'failed_executions': failed_executions,
                'results': results,
                'insights': insights,
                'summary': f"Processed {len(execution_ids)} agent executions with {successful_executions} successes"
            }

        except Exception as e:
            logger.error(f"Error aggregating agent results: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def communicate_with_advisor(self, advisor_id: str, consultation_topic: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Initiate communication with an advisor.

        Args:
            advisor_id: Advisor identifier
            consultation_topic: Topic for consultation
            context: Additional context for the consultation

        Returns:
            Advisor consultation results
        """
        try:
            # Get advisor profile
            advisor = self.advisor_registry.get_advisor(advisor_id)
            if not advisor:
                return {
                    'success': False,
                    'error': f'Advisor {advisor_id} not found'
                }

            # Create consultation context
            consultation_context = {
                'user_profile': self.enhanced_profile.get_context_for_ai('advisor'),
                'goals': self.enhanced_profile.long_term_goals,
                'current_projects': self.enhanced_profile.current_projects,
                'skills': self.enhanced_profile.core_competencies,
                'recent_decisions': self._get_recent_decisions(),
                'consultation_history': self._get_advisor_history(advisor_id)
            }

            if context:
                consultation_context.update(context)

            # Request consultation
            consultation_id = self.advisor_registry.request_consultation(
                advisor_id=advisor_id,
                user_id=str(self.user.id),
                topic=consultation_topic,
                consultation_type='strategy',
                initial_request=json.dumps(consultation_context)
            )

            if consultation_id:
                # Store advisor interaction
                self.store_memory(
                    'advisor_consultation',
                    f"Consulted with {advisor.name} about: {consultation_topic}",
                    importance=9,
                    metadata={
                        'advisor_id': advisor_id,
                        'advisor_name': advisor.name,
                        'consultation_id': consultation_id,
                        'topic': consultation_topic,
                        'domain': advisor.domain.value
                    }
                )

                logger.info(f"🎓 Initiated consultation with advisor {advisor.name} for {self.user.username}")

                return {
                    'success': True,
                    'advisor': {
                        'id': advisor.id,
                        'name': advisor.name,
                        'title': advisor.title,
                        'domain': advisor.domain.value,
                        'expertise_level': advisor.expertise_level.value
                    },
                    'consultation_id': consultation_id,
                    'message': f"Consultation initiated with {advisor.name}",
                    'expected_response_time': f"{advisor.response_time_hours} hours"
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to initiate consultation'
                }

        except Exception as e:
            logger.error(f"Error communicating with advisor: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def find_relevant_advisors(self, topic: str, domain: str = None) -> List[Dict[str, Any]]:
        """
        Find advisors relevant to a specific topic or domain.

        Args:
            topic: Topic or question for consultation
            domain: Specific domain to filter by

        Returns:
            List of relevant advisor recommendations
        """
        try:
            from advisors.registry import AdvisorDomain

            # Convert string domain to enum if provided
            domain_enum = None
            if domain:
                try:
                    domain_enum = AdvisorDomain(domain.lower())
                except ValueError:
                    # Try to find matching domain
                    for d in AdvisorDomain:
                        if domain.lower() in d.value:
                            domain_enum = d
                            break

            # Get advisor recommendations
            recommendations = self.advisor_registry.get_advisor_recommendations(topic, {
                'user_profile': self.enhanced_profile.get_context_for_ai('advisor'),
                'domain': domain_enum
            })

            # Store search as memory
            self.store_memory(
                'advisor_search',
                f"Searched for advisors on topic: {topic}",
                importance=5,
                metadata={
                    'topic': topic,
                    'domain': domain,
                    'recommendations_count': len(recommendations.get('recommendations', []))
                }
            )

            return recommendations

        except Exception as e:
            logger.error(f"Error finding relevant advisors: {e}")
            return {
                'error': str(e),
                'recommendations': []
            }

    def execute_multi_agent_workflow(self, workflow_name: str, task: str) -> Dict[str, Any]:
        """
        Execute a workflow involving multiple agents working together.

        Args:
            workflow_name: Name of the workflow to execute
            task: Primary task description

        Returns:
            Workflow execution results
        """
        try:
            # Define workflow templates
            workflows = {
                'opportunity_analysis': [
                    {'agent_type': 'research', 'capabilities': ['web_search', 'data_analysis']},
                    {'agent_type': 'analysis', 'capabilities': ['financial_analysis', 'risk_assessment']},
                    {'agent_type': 'recommendation', 'capabilities': ['strategy', 'planning']}
                ],
                'skill_development': [
                    {'agent_type': 'assessment', 'capabilities': ['skill_analysis', 'gap_analysis']},
                    {'agent_type': 'planning', 'capabilities': ['learning_path', 'curriculum']},
                    {'agent_type': 'tracking', 'capabilities': ['progress_monitoring', 'feedback']}
                ],
                'job_application': [
                    {'agent_type': 'research', 'capabilities': ['job_search', 'company_research']},
                    {'agent_type': 'application', 'capabilities': ['resume_optimization', 'cover_letter']},
                    {'agent_type': 'follow_up', 'capabilities': ['communication', 'tracking']}
                ]
            }

            if workflow_name not in workflows:
                return {
                    'success': False,
                    'error': f'Unknown workflow: {workflow_name}',
                    'available_workflows': list(workflows.keys())
                }

            workflow_steps = workflows[workflow_name]
            execution_ids = []
            step_results = []

            # Execute each step in the workflow
            for i, step in enumerate(workflow_steps):
                # Find agent for this step
                best_agent = self.agent_registry.find_best_agent(
                    task_description=f"{task} - Step {i+1}",
                    required_capabilities=step['capabilities'],
                    preferred_specialization=step['agent_type']
                )

                if best_agent:
                    # Execute step
                    execution_id = self.agent_registry.execute_agent(
                        agent_name=best_agent['name'],
                        task_data={
                            'task': task,
                            'workflow_step': i + 1,
                            'step_description': step,
                            'previous_results': step_results,
                            'user_context': self._get_agent_context()
                        }
                    )

                    if execution_id:
                        execution_ids.append(execution_id)
                        step_results.append({
                            'step': i + 1,
                            'agent': best_agent['name'],
                            'execution_id': execution_id
                        })

            # Store workflow execution
            self.store_memory(
                'workflow_execution',
                f"Executed {workflow_name} workflow: {task}",
                importance=9,
                metadata={
                    'workflow_name': workflow_name,
                    'task': task,
                    'execution_ids': execution_ids,
                    'steps_completed': len(step_results)
                }
            )

            logger.info(f"🔄 Executed {workflow_name} workflow with {len(execution_ids)} agents for {self.user.username}")

            return {
                'success': True,
                'workflow_name': workflow_name,
                'task': task,
                'total_steps': len(workflow_steps),
                'execution_ids': execution_ids,
                'step_results': step_results,
                'message': f"Workflow '{workflow_name}' initiated with {len(execution_ids)} agents"
            }

        except Exception as e:
            logger.error(f"Error executing multi-agent workflow: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _suggest_alternative_agents(self, task: str) -> List[str]:
        """Suggest alternative agents when no exact match is found."""
        try:
            # Get all available agents
            all_agents = self.agent_registry.list_agents()

            # Simple keyword matching for suggestions
            task_keywords = task.lower().split()
            suggestions = []

            for agent in all_agents[:10]:  # Top 10 agents
                agent_keywords = (agent.get('name', '') + ' ' +
                                agent.get('description', '') + ' ' +
                                ' '.join(agent.get('capabilities', []))).lower()

                # Check for keyword overlap
                if any(keyword in agent_keywords for keyword in task_keywords):
                    suggestions.append(agent.get('name', 'Unknown'))

            return suggestions[:5]  # Top 5 suggestions

        except Exception as e:
            logger.error(f"Error suggesting alternative agents: {e}")
            return []

    def _analyze_agent_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze agent execution results for insights."""
        try:
            total_time = sum(r.get('execution_time_ms', 0) for r in results)
            avg_time = total_time / len(results) if results else 0

            successful_agents = [r for r in results if r.get('status') == 'completed']
            failed_agents = [r for r in results if r.get('status') == 'failed']

            return {
                'total_executions': len(results),
                'successful_count': len(successful_agents),
                'failed_count': len(failed_agents),
                'success_rate': len(successful_agents) / len(results) if results else 0,
                'average_execution_time_ms': avg_time,
                'fastest_agent': min(results, key=lambda x: x.get('execution_time_ms', float('inf')))['agent_name'] if results else None,
                'slowest_agent': max(results, key=lambda x: x.get('execution_time_ms', 0))['agent_name'] if results else None
            }

        except Exception as e:
            logger.error(f"Error analyzing agent results: {e}")
            return {}

    def _extract_task_from_message(self, message: str) -> str:
        """Extract the task description from a user message requesting agent execution."""
        try:
            message_lower = message.lower()

            # Common patterns for task extraction
            task_patterns = [
                r'can you have an agent (.+?)(?:\?|$)',
                r'execute agent.+?to (.+?)(?:\?|$)',
                r'run agent.+?to (.+?)(?:\?|$)',
                r'use agent.+?to (.+?)(?:\?|$)',
                r'deploy agent.+?to (.+?)(?:\?|$)',
                r'get an agent to (.+?)(?:\?|$)',
                r'agent analyze (.+?)(?:\?|$)',
                r'agent help.+?with (.+?)(?:\?|$)',
                r'technical-signal-agent.+?to (.+?)(?:\?|$)',
                r'research agent.+?for (.+?)(?:\?|$)'
            ]

            import re
            for pattern in task_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    task = match.group(1).strip()
                    # Clean up the task description
                    task = task.replace(' and ', ' ').replace(' the ', ' ')
                    return task.capitalize()

            # If no specific pattern matches, try to extract after common trigger words
            trigger_words = ['analyze', 'research', 'help with', 'work on', 'examine', 'investigate']
            for trigger in trigger_words:
                if trigger in message_lower:
                    # Extract everything after the trigger word
                    start_idx = message_lower.find(trigger) + len(trigger)
                    remaining_text = message[start_idx:].strip()
                    # Remove common prefixes and suffixes
                    remaining_text = remaining_text.lstrip('the ').rstrip('?!.')
                    if remaining_text:
                        return remaining_text.capitalize()

            # Default fallback - return the original message without common prefixes
            cleaned_message = message.replace('Can you have an agent ', '').replace('Please ', '').strip()
            return cleaned_message.capitalize()

        except Exception as e:
            logger.error(f"Error extracting task from message: {e}")
            return message.strip()

    # =========================================================================
    # SESSION 672: ML Pipeline Management Tool Handlers
    # =========================================================================

    def _check_consultation_response(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Check if user's message is a response to a pending consultation.

        When PA creates a consultation via the 'consult' action, it awaits user response.
        This method detects if the user is responding to that consultation and interprets
        their intent (yes/no/proceed/abort/more info).

        Returns:
            Response dict if this is a consultation response, None otherwise
        """
        try:
            from core.models_human_interface import HumanAttentionItem
            from core.services.human_interface_service import get_human_interface_service

            # Find pending consultations from PA
            pending_consultations = HumanAttentionItem.objects.filter(
                user=self.user,
                source_type='assistant',
                status__in=['pending', 'viewed'],
                payload__consultation=True
            ).order_by('-created_at')

            if not pending_consultations.exists():
                return None  # No pending consultations

            # Get most recent consultation
            consultation = pending_consultations.first()

            # Check if message looks like a response
            message_lower = message.lower().strip()

            # Affirmative responses
            affirmative_patterns = [
                'yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'proceed',
                'go ahead', 'do it', 'approved', 'approve', 'confirm',
                'sounds good', 'let\'s do it', 'go for it', 'execute',
                'start', 'begin', 'launch', 'initiate'
            ]

            # Negative responses
            negative_patterns = [
                'no', 'nope', 'don\'t', 'stop', 'cancel', 'abort',
                'reject', 'decline', 'not now', 'hold off', 'wait',
                'later', 'never', 'negative', 'skip', 'pass'
            ]

            # Info request responses
            info_patterns = [
                'tell me more', 'more info', 'details', 'explain',
                'what do you mean', 'clarify', 'elaborate', 'why',
                'how', 'what', 'which'
            ]

            # Check for affirmative
            is_affirmative = any(p in message_lower for p in affirmative_patterns)
            is_negative = any(p in message_lower for p in negative_patterns)
            is_info_request = any(p in message_lower for p in info_patterns)

            # Only treat as consultation response if it clearly matches one of these
            if not (is_affirmative or is_negative or is_info_request):
                # Not clearly a consultation response - check if it's very short
                # Short messages after a consultation are likely responses
                if len(message_lower) > 50:
                    return None  # Probably a new topic

            service = get_human_interface_service(self.user)
            consultation_context = consultation.payload.get('context', consultation.summary)

            if is_negative:
                # User rejected - mark consultation as rejected
                service.record_decision(
                    item_id=str(consultation.id),
                    decision='reject',
                    feedback=f"User declined: {message}",
                    confidence=0.95
                )

                return {
                    'status': 'success',
                    'response': f"Understood. I won't proceed with: {consultation_context[:100]}...\n\nIs there something else I can help you with?",
                    'consultation_resolved': True,
                    'decision': 'rejected',
                    'format': 'text'
                }

            elif is_info_request:
                # User wants more info - keep consultation open
                consultation.status = 'viewed'
                consultation.save()

                return {
                    'status': 'success',
                    'response': f"Here's more context about what I was planning:\n\n**{consultation.title}**\n{consultation_context}\n\nWould you like me to proceed? (yes/no)",
                    'consultation_resolved': False,
                    'decision': 'info_requested',
                    'format': 'text'
                }

            elif is_affirmative:
                # User approved - mark consultation as approved and proceed
                service.record_decision(
                    item_id=str(consultation.id),
                    decision='approve',
                    feedback=f"User approved: {message}",
                    confidence=0.95
                )

                # Execute the intended action based on consultation payload
                action_result = self._execute_consultation_action(consultation)

                return {
                    'status': 'success',
                    'response': f"Great! Proceeding with: {consultation_context[:100]}...\n\n{action_result.get('message', 'Action initiated.')}",
                    'consultation_resolved': True,
                    'decision': 'approved',
                    'action_result': action_result,
                    'format': 'text'
                }

            return None

        except Exception as e:
            logger.error(f"Error checking consultation response: {e}", exc_info=True)
            return None

    def _execute_consultation_action(self, consultation) -> Dict[str, Any]:
        """
        Execute the action that was waiting for consultation approval.

        The consultation payload may contain:
        - 'intended_action': The action to execute (e.g., 'start_workflow', 'execute_pilot')
        - 'action_params': Parameters for the action

        Returns:
            Result dictionary from the executed action
        """
        try:
            payload = consultation.payload or {}
            intended_action = payload.get('intended_action', 'generic_approval')
            action_params = payload.get('action_params', {})

            logger.info(f"Executing consultation action: {intended_action} with params: {action_params}")

            if intended_action == 'start_workflow':
                # Trigger workflow orchestration
                from core.agents import get_workflow_orchestration_agent
                agent = get_workflow_orchestration_agent(user=self.user)
                return agent.execute(
                    task=action_params.get('task', 'Execute approved workflow'),
                    context={'consultation_approved': True}
                )

            elif intended_action == 'execute_pilot':
                # Execute a pilot
                from core.services.pilot_execution_service import PilotExecutionService
                service = PilotExecutionService(self.user)
                pilot_id = action_params.get('pilot_id')
                if pilot_id:
                    return service.execute_pilot(pilot_id)
                return {'success': False, 'message': 'No pilot_id specified'}

            elif intended_action == 'approve_gate':
                # Session 797: Approve a gate and start pilot via consultation
                from core.services.gate_progression_pipeline import gate_progression_pipeline
                gate_id = action_params.get('gate_id')
                if not gate_id:
                    return {'success': False, 'message': 'No gate_id specified'}

                # Use the pipeline's approval method (creates pilot automatically)
                result = gate_progression_pipeline.approve_gate_from_attention(consultation.id)
                if result.get('success'):
                    decision_title = action_params.get('decision_title', 'Unknown')
                    return {
                        'success': True,
                        'message': f"Gate approved for '{decision_title}'! Pilot has been started.",
                        'gate_id': result.get('gate_id'),
                        'pilot_id': result.get('pilot_id'),
                    }
                return result

            elif intended_action == 'waive_gate':
                # Session 797: Waive a stuck gate via consultation
                from core.services.gate_progression_pipeline import gate_progression_pipeline
                gate_id = action_params.get('gate_id')
                if not gate_id:
                    return {'success': False, 'message': 'No gate_id specified'}

                # Use the pipeline's waive method
                result = gate_progression_pipeline.waive_gate_from_attention(
                    consultation.id,
                    reason="Waived via PA consultation"
                )
                if result.get('success'):
                    decision_title = action_params.get('decision_title', 'Unknown')
                    return {
                        'success': True,
                        'message': f"Gate waived for '{decision_title}'! Pilot has been started.",
                        'gate_id': result.get('gate_id'),
                        'pilot_id': result.get('pilot_id'),
                    }
                return result

            elif intended_action == 'process_opportunity':
                # Process an opportunity
                from core.services.opportunity_service import OpportunityService
                service = OpportunityService(self.user)
                opp_id = action_params.get('opportunity_id')
                if opp_id:
                    return service.process_opportunity(opp_id)
                return {'success': False, 'message': 'No opportunity_id specified'}

            elif intended_action == 'execute_opportunity':
                # Session 797: Execute a high-value opportunity via consultation
                from core.services.opportunity_execution_pipeline import opportunity_execution_pipeline
                from core.models_unified_system import Opportunity

                opp_id = action_params.get('opportunity_id')
                if not opp_id:
                    return {'success': False, 'message': 'No opportunity_id specified'}

                try:
                    opportunity = Opportunity.objects.get(id=opp_id)

                    # Mark consultation as completed
                    consultation.status = 'decided'
                    consultation.decision = 'approve'
                    consultation.save(update_fields=['status', 'decision'])

                    # Execute the opportunity directly (bypass consultation check)
                    original_threshold = opportunity_execution_pipeline.HIGH_VALUE_REVENUE_THRESHOLD
                    opportunity_execution_pipeline.HIGH_VALUE_REVENUE_THRESHOLD = 999999999
                    try:
                        result = opportunity_execution_pipeline.execute_opportunity(
                            opportunity,
                            user=self.user
                        )
                    finally:
                        opportunity_execution_pipeline.HIGH_VALUE_REVENUE_THRESHOLD = original_threshold

                    if result.get('success'):
                        title = action_params.get('title', 'Opportunity')
                        return {
                            'success': True,
                            'message': f"Executing opportunity: '{title}'. Workflow started!",
                            'execution_id': result.get('execution_id'),
                            'project_id': result.get('project_id'),
                        }
                    return result

                except Opportunity.DoesNotExist:
                    return {'success': False, 'message': f'Opportunity {opp_id} not found'}
                except Exception as e:
                    logger.error(f"Error executing opportunity: {e}")
                    return {'success': False, 'message': f'Error: {str(e)}'}

            else:
                # Generic approval - just acknowledge
                return {
                    'success': True,
                    'message': f"Approval recorded for: {consultation.summary[:100]}"
                }

        except Exception as e:
            logger.error(f"Error executing consultation action: {e}", exc_info=True)
            return {'success': False, 'message': f'Error executing action: {str(e)}'}