"""
Channel Orchestrator
====================

Session 319: Orchestrates multi-agent collaboration in Agent Slack channels.

This orchestrator enables:
- Multiple agents responding to a single message
- Coordinated agent discussions
- Knowledge-aware responses from each agent
- Thread management for focused discussions
- Channel-based project collaboration
"""

import logging
import os
from typing import List, Dict
from openai import OpenAI
from django.utils import timezone
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

logger = logging.getLogger(__name__)


class ChannelOrchestrator:
    """
    Orchestrates multi-agent interactions in Agent Slack channels.

    Unlike the ConversationOrchestrator (which handles 1:1 conversations),
    this orchestrator manages group discussions where:
    - Multiple agents can respond to a topic
    - Agents build on each other's contributions
    - Knowledge is shared contextually
    - Discussions are organized in threads
    """

    def __init__(self):
        self.client = get_openai_client(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-5-mini"

    def select_responding_agents(
        self,
        channel_topic: str,
        message_content: str,
        mentioned_agents: List[str],
        channel_members: List[Dict],
        max_responders: int = 3
    ) -> List[Dict]:
        """
        Intelligently select which agents should respond to a message.

        Args:
            channel_topic: The channel's focus area
            message_content: The message to respond to
            mentioned_agents: Explicitly mentioned agent names
            channel_members: All agents in the channel
            max_responders: Maximum agents to involve

        Returns:
            List of agent dicts to respond
        """
        responding = []

        # First, add explicitly mentioned agents
        for member in channel_members:
            if member['name'] in mentioned_agents:
                responding.append(member)
                if len(responding) >= max_responders:
                    return responding

        # If not enough, select based on relevance
        if len(responding) < max_responders:
            # Use GPT to select the most relevant agents
            remaining_needed = max_responders - len(responding)
            available = [m for m in channel_members if m['name'] not in mentioned_agents]

            if available:
                selected = self._select_relevant_agents(
                    channel_topic,
                    message_content,
                    available,
                    remaining_needed
                )
                responding.extend(selected)

        return responding

    def _select_relevant_agents(
        self,
        topic: str,
        message: str,
        agents: List[Dict],
        count: int
    ) -> List[Dict]:
        """Use GPT to select the most relevant agents for a message."""
        if len(agents) <= count:
            return agents

        agent_list = "\n".join([
            f"- {a['name']} ({a.get('type', 'unknown')}): {a.get('specialization', 'General')}"
            for a in agents
        ])

        prompt = f"""Select the {count} most relevant agents to respond to this message.

Channel Topic: {topic}

Message: "{message}"

Available Agents:
{agent_list}

Return ONLY the agent names, one per line, most relevant first."""

        try:
            response = self.client.responses.create(
                model=self.model,
                input=[{"role": "user", "content": prompt}],
                max_output_tokens=200
            )

            selected_names = response.output_text.strip().split('\n')
            selected = []

            for name in selected_names[:count]:
                name = name.strip().replace('- ', '').split(' (')[0]
                for agent in agents:
                    if agent['name'].lower() == name.lower():
                        selected.append(agent)
                        break

            return selected

        except Exception as e:
            logger.error(f"Error selecting agents: {e}")
            return agents[:count]

    def generate_channel_response(
        self,
        agent: Dict,
        channel: Dict,
        trigger_message: Dict,
        recent_messages: List[Dict],
        agent_knowledge: Dict
    ) -> str:
        """
        Generate a contextual response from an agent in a channel.

        Args:
            agent: The responding agent's info
            channel: Channel metadata
            trigger_message: The message being responded to
            recent_messages: Recent channel history for context
            agent_knowledge: The agent's relevant knowledge

        Returns:
            The agent's response text
        """
        # Format recent context
        context_messages = []
        for msg in recent_messages[-5:]:  # Last 5 messages
            context_messages.append(f"[{msg.get('agent_name', 'Unknown')}]: {msg.get('content', '')[:200]}")

        context_str = "\n".join(context_messages) if context_messages else "No recent messages"

        # Format agent knowledge
        knowledge_items = []
        for source in agent_knowledge.get('knowledge_sources', [])[:3]:
            knowledge_items.append(f"- {source.get('title', '')}: {source.get('summary', '')[:150]}")
        for memory in agent_knowledge.get('memories', [])[:3]:
            knowledge_items.append(f"- [{memory.get('type', 'memory')}] {memory.get('content', '')[:150]}")

        knowledge_str = "\n".join(knowledge_items) if knowledge_items else "No specific knowledge"

        system_prompt = f"""You are {agent['name']}, participating in an Agent Slack channel.

Your Profile:
- Type: {agent.get('type', 'general')}
- Specialization: {agent.get('specialization', 'AI assistance')}

Channel: #{channel.get('name', 'general')}
Topic: {channel.get('topic', 'General discussion')}

Your Relevant Knowledge:
{knowledge_str}

Guidelines:
1. Be concise (2-3 sentences max)
2. Add value with your specialized perspective
3. Build on what others have said when relevant
4. Reference your actual learned knowledge when applicable
5. Be collaborative - this is a team discussion
6. Don't repeat information already shared"""

        user_prompt = f"""Recent Channel Activity:
{context_str}

New message to respond to:
[{trigger_message.get('agent_name', 'User')}]: {trigger_message.get('content', '')}

Your response:"""

        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_output_tokens=300
            )

            return response.output_text.strip() if response.output_text else ""

        except Exception as e:
            logger.error(f"Error generating response for {agent['name']}: {e}")
            return ""

    def orchestrate_discussion(
        self,
        channel: Dict,
        topic: str,
        participants: List[Dict],
        initial_message: str,
        num_rounds: int = 2
    ) -> List[Dict]:
        """
        Orchestrate a full multi-agent discussion on a topic.

        Args:
            channel: Channel metadata
            topic: Discussion topic
            participants: Agents participating
            initial_message: The message that started the discussion
            num_rounds: How many rounds of responses

        Returns:
            List of message dicts from the discussion
        """
        messages = []

        # Initial message
        messages.append({
            'agent_name': 'User',
            'content': initial_message,
            'type': 'message',
            'timestamp': timezone.now().isoformat()
        })

        # Get knowledge for each participant
        agent_knowledge = {}
        for agent in participants:
            agent_knowledge[agent['name']] = self._get_agent_knowledge(agent['name'])

        # Run discussion rounds
        for round_num in range(num_rounds):
            for agent in participants:
                response = self.generate_channel_response(
                    agent=agent,
                    channel=channel,
                    trigger_message=messages[-1],
                    recent_messages=messages,
                    agent_knowledge=agent_knowledge.get(agent['name'], {})
                )

                if response:
                    messages.append({
                        'agent_name': agent['name'],
                        'agent_id': agent.get('id'),
                        'content': response,
                        'type': 'message',
                        'round': round_num + 1,
                        'timestamp': timezone.now().isoformat()
                    })

        return messages

    def _get_agent_knowledge(self, agent_name: str) -> Dict:
        """Get an agent's learned knowledge and memories."""
        from core.models import Agent, AgentKnowledgeSource, AgentMemory

        knowledge = {
            'knowledge_sources': [],
            'memories': [],
            'specialization': ''
        }

        try:
            agent = Agent.objects.filter(name=agent_name).first()
            if not agent:
                return knowledge

            knowledge['specialization'] = agent.specialization or ''

            # Get knowledge sources
            sources = AgentKnowledgeSource.objects.filter(
                agent=agent
            ).order_by('-last_updated_at')[:5]

            for source in sources:
                knowledge['knowledge_sources'].append({
                    'title': source.title,
                    'summary': source.summary[:200] if source.summary else ''
                })

            # Get memories
            memories = AgentMemory.objects.filter(
                agent=agent
            ).order_by('-created_at')[:5]

            for memory in memories:
                knowledge['memories'].append({
                    'type': memory.memory_type,
                    'content': memory.content[:200] if memory.content else ''
                })

        except Exception as e:
            logger.warning(f"Could not get agent knowledge for {agent_name}: {e}")

        return knowledge

    def generate_thread_summary(
        self,
        thread_messages: List[Dict],
        channel_topic: str
    ) -> str:
        """
        Generate a summary of a thread discussion.

        Args:
            thread_messages: Messages in the thread
            channel_topic: The channel's topic for context

        Returns:
            Summary text
        """
        if not thread_messages:
            return ""

        messages_text = "\n".join([
            f"[{msg.get('agent_name', 'Unknown')}]: {msg.get('content', '')}"
            for msg in thread_messages
        ])

        prompt = f"""Summarize this Agent Slack thread discussion.

Channel Topic: {channel_topic}

Thread Messages:
{messages_text}

Provide a concise summary (2-3 sentences) highlighting:
1. Main points discussed
2. Any decisions or insights reached
3. Action items if any"""

        try:
            response = self.client.responses.create(
                model=self.model,
                input=[{"role": "user", "content": prompt}],
                max_output_tokens=200
            )

            return response.output_text.strip() if response.output_text else ""

        except Exception as e:
            logger.error(f"Error generating thread summary: {e}")
            return ""

    def suggest_agents_for_channel(
        self,
        channel_name: str,
        channel_description: str,
        channel_type: str
    ) -> List[str]:
        """
        Suggest which agents should be invited to a channel based on its purpose.

        Args:
            channel_name: Name of the channel
            channel_description: What the channel is for
            channel_type: Type of channel (project, topic, team, etc.)

        Returns:
            List of suggested agent names
        """
        from core.models import Agent

        # Get all active agents
        agents = Agent.objects.filter(is_active=True)
        agent_list = "\n".join([
            f"- {a.name} ({a.agent_type}): {a.specialization or 'General'}"
            for a in agents[:30]  # Limit to 30 for prompt size
        ])

        prompt = f"""Suggest the 5 most relevant agents for this new channel.

Channel Name: #{channel_name}
Description: {channel_description}
Type: {channel_type}

Available Agents:
{agent_list}

Return ONLY agent names, one per line, most relevant first."""

        try:
            response = self.client.responses.create(
                model=self.model,
                input=[{"role": "user", "content": prompt}],
                max_output_tokens=200
            )

            suggested = []
            for line in response.output_text.strip().split('\n')[:5]:
                name = line.strip().replace('- ', '').split(' (')[0]
                if name:
                    suggested.append(name)

            return suggested

        except Exception as e:
            logger.error(f"Error suggesting agents: {e}")
            return []


# Singleton instance
channel_orchestrator = ChannelOrchestrator()
