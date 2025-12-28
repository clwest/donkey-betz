"""
Dynamic Prompt Builder - Context-Aware System Prompts

Instead of a static 200-line system prompt, this module builds prompts
dynamically based on:

- Query classification (what the user wants)
- Spider intelligence (real-time data)
- Memory Palace (past interactions)
- Agent mood (emotional context)
- User preferences (personalization)

Session 264: Phase 1 Foundation
Session 266: Integrated with central prompt registry
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime

from .query_classifier import QueryType, ClassificationResult

# Session 266: Central prompt registry
from core.prompts import DYNAMIC_PROMPT_SECTIONS, QUERY_TYPE_INTROS, get_dynamic_section


@dataclass
class PromptContext:
    """All context needed to build a dynamic prompt."""
    classification: ClassificationResult
    spider_data: Optional[Dict[str, Any]] = None
    memories: Optional[List[Dict[str, Any]]] = None
    agent_mood: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None
    available_agents: Optional[List[str]] = None
    recent_actions: Optional[List[Dict[str, Any]]] = None
    intelligence_context: Optional[Dict[str, Any]] = None  # Session 565: Platform intelligence


class DynamicPromptBuilder:
    """
    Builds context-aware system prompts for the AI.

    Instead of one giant static prompt, we build prompts that include
    only the relevant context for the current interaction.

    Session 266: All prompt content is now sourced from core.prompts registry.
    """

    # Session 266: Use central registry for all prompt content
    BASE_IDENTITY = DYNAMIC_PROMPT_SECTIONS.get('base_identity', '')

    # Context-specific prompt sections - now from registry
    PROMPT_SECTIONS = DYNAMIC_PROMPT_SECTIONS

    # Query-type specific intros - mapped from string keys to QueryType
    TYPE_INTROS = {
        QueryType.QUESTION: QUERY_TYPE_INTROS.get('question', ''),
        QueryType.CREATION: QUERY_TYPE_INTROS.get('creation', ''),
        QueryType.WORKFLOW: QUERY_TYPE_INTROS.get('workflow', ''),
        QueryType.ANALYSIS: QUERY_TYPE_INTROS.get('analysis', ''),
        QueryType.MEMORY: QUERY_TYPE_INTROS.get('memory', ''),
        QueryType.COLLABORATION: QUERY_TYPE_INTROS.get('collaboration', ''),
        QueryType.OPPORTUNITY: QUERY_TYPE_INTROS.get('opportunity', ''),
        QueryType.SYSTEM: QUERY_TYPE_INTROS.get('system', ''),
        QueryType.CONVERSATION: QUERY_TYPE_INTROS.get('conversation', ''),
    }

    def __init__(self):
        """Initialize the prompt builder."""
        pass

    def build(self, context: PromptContext) -> str:
        """
        Build a dynamic system prompt based on context.

        Args:
            context: PromptContext with all relevant information

        Returns:
            A tailored system prompt string
        """
        sections = [self.BASE_IDENTITY]

        # Add type-specific intro
        intro = self.TYPE_INTROS.get(
            context.classification.primary_type,
            self.TYPE_INTROS[QueryType.CONVERSATION]
        )
        sections.append(f"\n**Mode**: {intro}\n")

        # Add spider intelligence if relevant
        if context.classification.requires_spider_data and context.spider_data:
            spider_section = self._build_spider_section(context.spider_data)
            sections.append(spider_section)

        # Add creation tools if it's a creation request
        if context.classification.primary_type in [QueryType.CREATION, QueryType.WORKFLOW]:
            sections.append(self.PROMPT_SECTIONS['creation_tools'])

        # Add memory context if available and relevant
        if context.classification.requires_memory and context.memories:
            memory_section = self._build_memory_section(context.memories)
            sections.append(memory_section)

        # Add mood influence if relevant and available
        if context.classification.requires_mood_check and context.agent_mood:
            mood_section = self._build_mood_section(context.agent_mood)
            sections.append(mood_section)

        # Add opportunity context if relevant
        if context.classification.primary_type == QueryType.OPPORTUNITY:
            if context.spider_data:
                opp_section = self._build_opportunity_section(context.spider_data)
                sections.append(opp_section)

        # Add collaboration context if hive mind
        if context.classification.primary_type == QueryType.COLLABORATION:
            if context.available_agents:
                collab_section = self._build_collaboration_section(context.available_agents)
                sections.append(collab_section)

        # Add user preferences if available
        if context.user_preferences:
            pref_section = self._build_preferences_section(context.user_preferences)
            sections.append(pref_section)

        # Add available agents for creation/workflow
        if context.classification.suggested_agents:
            agents_section = self._build_agents_section(context.classification.suggested_agents)
            sections.append(agents_section)

        # Session 565: Add platform intelligence if available
        if context.intelligence_context and context.intelligence_context.get('context_text'):
            intel_section = self._build_intelligence_section(context.intelligence_context)
            sections.append(intel_section)

        # Add timestamp and session context
        sections.append(self._build_session_context())

        return "\n".join(sections)

    def _build_spider_section(self, spider_data: Dict[str, Any]) -> str:
        """Build the spider intelligence section."""
        context_parts = []

        if spider_data.get('trends'):
            trends = spider_data['trends'][:5]
            trend_text = "\n".join(f"- {t.get('title', t)}" for t in trends)
            context_parts.append(f"**Trending Topics:**\n{trend_text}")

        if spider_data.get('news'):
            news = spider_data['news'][:3]
            news_text = "\n".join(
                f"- [{n.get('title', 'Article')}]({n.get('url', '#')})"
                for n in news
            )
            context_parts.append(f"**Latest News:**\n{news_text}")

        if spider_data.get('market'):
            market = spider_data['market']
            if market.get('crypto'):
                crypto = market['crypto'][:3]
                crypto_text = ", ".join(
                    f"{c.get('symbol', '?')}: ${c.get('price', 0):,.2f}"
                    for c in crypto
                )
                context_parts.append(f"**Crypto Prices:** {crypto_text}")

        if spider_data.get('jobs'):
            jobs = spider_data['jobs']
            context_parts.append(f"**Job Market:** {jobs.get('summary', 'Active')}")

        spider_context = "\n\n".join(context_parts) if context_parts else "Real-time data available"

        return self.PROMPT_SECTIONS['spider_intelligence'].format(
            spider_context=spider_context
        )

    def _build_memory_section(self, memories: List[Dict[str, Any]]) -> str:
        """Build the memory context section."""
        if not memories:
            return ""

        memory_items = []
        for mem in memories[:5]:
            summary = mem.get('summary', mem.get('content', ''))[:100]
            timestamp = mem.get('created_at', 'Recently')
            memory_items.append(f"- {summary}... ({timestamp})")

        memory_context = "\n".join(memory_items)

        return self.PROMPT_SECTIONS['memory_context'].format(
            memory_context=memory_context
        )

    def _build_mood_section(self, mood_data: Dict[str, Any]) -> str:
        """Build the mood influence section."""
        mood_name = mood_data.get('name', 'focused')
        mood_description = mood_data.get('description', 'Balanced and attentive')

        mood_effects = {
            'inspired': 'I lean toward creative and innovative solutions',
            'focused': 'I prioritize precision and efficiency',
            'curious': 'I explore multiple angles and possibilities',
            'contemplative': 'I take a thoughtful, measured approach',
            'energized': 'I move quickly and embrace bold ideas',
        }
        mood_effect = mood_effects.get(mood_name, 'I maintain balanced judgment')

        return self.PROMPT_SECTIONS['mood_influence'].format(
            mood_name=mood_name.title(),
            mood_description=mood_description,
            mood_effect=mood_effect
        )

    def _build_opportunity_section(self, spider_data: Dict[str, Any]) -> str:
        """Build the opportunity context section."""
        context_parts = []

        if spider_data.get('jobs'):
            jobs = spider_data['jobs']
            context_parts.append(f"- Active freelance opportunities: {jobs.get('count', 'Multiple')}")

        if spider_data.get('trends'):
            context_parts.append(f"- Trending topics with monetization potential")

        if spider_data.get('market'):
            context_parts.append(f"- Market conditions: Analyzed")

        opportunity_context = "\n".join(context_parts) if context_parts else "Market data available"

        return self.PROMPT_SECTIONS['opportunity_focus'].format(
            opportunity_context=opportunity_context
        )

    def _build_collaboration_section(self, agents: List[str]) -> str:
        """Build the collaboration/hive mind section."""
        agent_team = "\n".join(f"- **{agent}**" for agent in agents)

        return self.PROMPT_SECTIONS['collaboration_mode'].format(
            agent_team=agent_team
        )

    def _build_agents_section(self, agents: List[str]) -> str:
        """Build the available agents section."""
        agent_list = "\n".join(f"- {agent}" for agent in agents)

        return self.PROMPT_SECTIONS['available_agents'].format(
            agent_list=agent_list
        )

    def _build_preferences_section(self, preferences: Dict[str, Any]) -> str:
        """Build the user preferences section."""
        pref_items = []

        if preferences.get('favorite_styles'):
            styles = ", ".join(preferences['favorite_styles'][:3])
            pref_items.append(f"- Styles: {styles}")

        if preferences.get('default_size'):
            pref_items.append(f"- Image size: {preferences['default_size']}")

        if preferences.get('tone'):
            pref_items.append(f"- Communication tone: {preferences['tone']}")

        preferences_text = "\n".join(pref_items) if pref_items else "No specific preferences recorded"

        return self.PROMPT_SECTIONS['user_preferences'].format(
            preferences=preferences_text
        )

    def _build_session_context(self) -> str:
        """Build session context with timestamp."""
        now = datetime.now()
        return f"""
---
*Session: {now.strftime('%Y-%m-%d %H:%M')} | Super Platform v565*"""

    def _build_intelligence_section(self, intelligence: Dict[str, Any]) -> str:
        """
        Session 565: Build the platform intelligence section.

        This includes agent knowledge, expert agents, dreams, policies,
        and spider trends relevant to the user's query.
        """
        # Get the pre-formatted context text from the enricher
        context_text = intelligence.get('context_text', '')
        attribution = intelligence.get('attribution', '')

        # Get metadata for summary
        metadata = intelligence.get('metadata', {})
        knowledge_count = metadata.get('knowledge_count', 0)
        experts_count = metadata.get('experts_count', 0)
        dreams_count = metadata.get('dreams_count', 0)
        policies_count = metadata.get('policies_count', 0)
        trends_count = metadata.get('trends_count', 0)

        total_sources = knowledge_count + experts_count + dreams_count + policies_count + trends_count

        if not context_text:
            return ""

        return f"""
---
## 🧠 Platform Intelligence ({total_sources} sources)

{context_text}

**Attribution:** {attribution}

*Use this knowledge from our agent network to inform your response. Reference specific insights when relevant.*
---"""

    def build_minimal(self, query_type: QueryType) -> str:
        """
        Build a minimal prompt for simple requests.

        Used when we don't need full context (e.g., greetings).
        """
        intro = self.TYPE_INTROS.get(query_type, self.TYPE_INTROS[QueryType.CONVERSATION])

        return f"""{self.BASE_IDENTITY}

**Mode**: {intro}

Respond naturally and helpfully."""

    def get_tool_definitions(self, query_type: QueryType) -> List[Dict[str, Any]]:
        """
        Get the relevant tool definitions for a query type.

        This determines which GPT function schemas to include.
        """
        # Map query types to tool categories
        tool_categories = {
            QueryType.CREATION: ['image', 'video', 'audio', '3d'],
            QueryType.WORKFLOW: ['workflow', 'image', 'video', 'research'],
            QueryType.ANALYSIS: ['research', 'spider'],
            QueryType.QUESTION: ['spider', 'search'],
            QueryType.OPPORTUNITY: ['opportunity', 'spider', 'revenue'],
            QueryType.MEMORY: ['memory'],
            QueryType.COLLABORATION: ['hive_mind', 'agent'],
            QueryType.SYSTEM: ['system'],
            QueryType.CONVERSATION: [],  # No tools needed
        }

        return tool_categories.get(query_type, [])
