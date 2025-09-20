"""
Content Studio Agent Integration
=================================

This module integrates the Content Creation Studio with the 152 AI agents,
allowing agents to create content through the studio and enabling content
workflows that leverage agent capabilities.
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import the Content Studio Bridge
from agents.content_studio_bridge import (
    ContentStudioBridge,
    AgentContentCreator,
    agent_create_blog,
    agent_create_social,
    agent_create_image,
    agent_create_campaign
)

# Import agent executor
from backend.agents.concrete_executor import concrete_executor
from backend.agents.ai_enforced_base import AIEnforcedAgent
from agents.models import UnifiedAgentTemplate

logger = logging.getLogger(__name__)


class ContentStudioAgentIntegration:
    """
    Main integration class that connects Content Studio to all 152 agents
    """

    def __init__(self):
        self.concrete_executor = concrete_executor
        self.content_agents = self._identify_content_agents()
        self.active_bridges = {}
        logger.info(f"🎨 Initialized Content Studio Integration with {len(self.content_agents)} content-capable agents")

    def _identify_content_agents(self) -> List[str]:
        """Identify agents capable of content creation"""
        content_capable = []

        # Content-specific agent patterns
        content_patterns = [
            'content', 'writer', 'creator', 'blog', 'article', 'social',
            'marketing', 'copy', 'script', 'video', 'image', 'design',
            'seo', 'email', 'newsletter', 'story', 'narrative'
        ]

        for agent_name in self.concrete_executor.agent_classes.keys():
            agent_lower = agent_name.lower()
            if any(pattern in agent_lower for pattern in content_patterns):
                content_capable.append(agent_name)

        return content_capable

    async def create_content_through_agent(
        self,
        agent_name: str,
        content_type: str,
        topic: str,
        user=None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create content using a specific agent through the Content Studio

        Args:
            agent_name: Name of the agent to use
            content_type: Type of content (blog, social, video, image, campaign)
            topic: The topic for content creation
            user: Optional user context
            **kwargs: Additional parameters for content creation

        Returns:
            Dictionary with created content and metadata
        """
        try:
            # Verify agent exists
            if agent_name not in self.concrete_executor.agent_classes:
                return {
                    'success': False,
                    'error': f'Agent {agent_name} not found',
                    'available_agents': self.content_agents
                }

            # Get agent template from database
            agent_template = UnifiedAgentTemplate.objects.filter(
                name=agent_name.replace('_', '-')
            ).first()

            if not agent_template:
                # Create a temporary template for non-DB agents
                agent_template = UnifiedAgentTemplate(
                    name=agent_name,
                    specialization='content_creation',
                    description=f'Agent {agent_name} for content creation'
                )

            # Create content studio bridge for this agent
            bridge = ContentStudioBridge(agent=agent_template, user=user)
            self.active_bridges[agent_name] = bridge

            # Execute content creation based on type
            result = None

            if content_type == 'blog':
                result = bridge.create_blog_post(
                    topic=topic,
                    tone=kwargs.get('tone', 'professional'),
                    length=kwargs.get('length', 'medium'),
                    include_outline=kwargs.get('include_outline', True)
                )

            elif content_type == 'social':
                result = bridge.create_social_media_post(
                    platform=kwargs.get('platform', 'twitter'),
                    topic=topic,
                    tone=kwargs.get('tone', 'engaging'),
                    include_hashtags=kwargs.get('include_hashtags', True)
                )

            elif content_type == 'video':
                result = bridge.create_video_script(
                    topic=topic,
                    duration=kwargs.get('duration', 60),
                    style=kwargs.get('style', 'educational'),
                    include_narration=kwargs.get('include_narration', True)
                )

            elif content_type == 'image':
                result = bridge.create_image(
                    prompt=topic,
                    style=kwargs.get('style', 'realistic'),
                    size=kwargs.get('size', '1024x1024'),
                    negative_prompt=kwargs.get('negative_prompt', ''),
                    batch_size=kwargs.get('batch_size', 1)
                )

            elif content_type == 'campaign':
                result = bridge.create_multi_format_campaign(
                    campaign_topic=topic,
                    platforms=kwargs.get('platforms', ['blog', 'twitter', 'linkedin'])
                )

            else:
                # Use agent's native execution for custom content types
                task_data = {
                    'task': f"Create {content_type} content about: {topic}",
                    'input': {
                        'content_type': content_type,
                        'topic': topic,
                        **kwargs
                    }
                }

                result = await self.concrete_executor.execute_agent(
                    agent_name, task_data, user
                )

            # Log success
            if result and result.get('success'):
                logger.info(f"✅ Agent {agent_name} created {content_type} content successfully")
            else:
                logger.error(f"❌ Agent {agent_name} failed to create {content_type} content")

            return result

        except Exception as e:
            logger.error(f"Error in content creation through agent {agent_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'agent': agent_name,
                'content_type': content_type
            }

    async def orchestrate_content_workflow(
        self,
        workflow_type: str,
        topic: str,
        agents: List[str] = None,
        user=None
    ) -> Dict[str, Any]:
        """
        Orchestrate a complete content workflow using multiple agents

        Args:
            workflow_type: Type of workflow (full_campaign, research_to_content, etc.)
            topic: The main topic for the workflow
            agents: Specific agents to use (optional)
            user: User context

        Returns:
            Dictionary with workflow results
        """
        workflow_results = {
            'success': True,
            'workflow_type': workflow_type,
            'topic': topic,
            'stages': {},
            'timestamp': datetime.now().isoformat()
        }

        try:
            if workflow_type == 'full_campaign':
                # Stage 1: Research using research agents
                research_agent = self._find_best_agent(['research', 'analyst', 'data'], agents)
                if research_agent:
                    research_result = await self.concrete_executor.execute_agent(
                        research_agent,
                        {'task': f"Research topic: {topic}", 'input': {'topic': topic}},
                        user
                    )
                    workflow_results['stages']['research'] = research_result

                # Stage 2: Create blog post
                blog_agent = self._find_best_agent(['blog', 'article', 'writer'], agents)
                if blog_agent:
                    blog_result = await self.create_content_through_agent(
                        blog_agent, 'blog', topic, user, length='long'
                    )
                    workflow_results['stages']['blog'] = blog_result

                # Stage 3: Create social media posts
                social_agent = self._find_best_agent(['social', 'twitter', 'marketing'], agents)
                if social_agent:
                    # Twitter
                    twitter_result = await self.create_content_through_agent(
                        social_agent, 'social', topic, user, platform='twitter'
                    )
                    workflow_results['stages']['twitter'] = twitter_result

                    # LinkedIn
                    linkedin_result = await self.create_content_through_agent(
                        social_agent, 'social', topic, user, platform='linkedin'
                    )
                    workflow_results['stages']['linkedin'] = linkedin_result

                # Stage 4: Create visuals
                visual_agent = self._find_best_agent(['image', 'design', 'visual'], agents)
                if visual_agent:
                    image_result = await self.create_content_through_agent(
                        visual_agent, 'image', f"Professional image for {topic}",
                        user, batch_size=4
                    )
                    workflow_results['stages']['visuals'] = image_result

                # Stage 5: Create video script
                video_agent = self._find_best_agent(['video', 'script', 'multimedia'], agents)
                if video_agent:
                    video_result = await self.create_content_through_agent(
                        video_agent, 'video', topic, user, duration=120
                    )
                    workflow_results['stages']['video'] = video_result

            elif workflow_type == 'research_to_content':
                # Research → Analysis → Content Creation pipeline
                # Implementation for other workflow types...
                pass

            logger.info(f"✅ Completed {workflow_type} workflow for topic: {topic}")

        except Exception as e:
            logger.error(f"Workflow orchestration error: {e}")
            workflow_results['success'] = False
            workflow_results['error'] = str(e)

        return workflow_results

    def _find_best_agent(self, keywords: List[str], available_agents: List[str] = None) -> Optional[str]:
        """Find the best agent for a task based on keywords"""
        agents_to_search = available_agents or self.content_agents

        for keyword in keywords:
            for agent in agents_to_search:
                if keyword in agent.lower():
                    return agent

        # Return first content agent if no specific match
        return agents_to_search[0] if agents_to_search else None

    async def batch_content_creation(
        self,
        topics: List[str],
        content_type: str = 'blog',
        parallel: bool = True,
        user=None
    ) -> List[Dict[str, Any]]:
        """
        Create multiple pieces of content in batch

        Args:
            topics: List of topics to create content for
            content_type: Type of content to create
            parallel: Whether to create content in parallel
            user: User context

        Returns:
            List of content creation results
        """
        results = []

        if parallel:
            # Create content in parallel using different agents
            tasks = []
            for i, topic in enumerate(topics):
                # Rotate through content agents for variety
                agent = self.content_agents[i % len(self.content_agents)]
                task = self.create_content_through_agent(
                    agent, content_type, topic, user
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks)
        else:
            # Create content sequentially
            for topic in topics:
                agent = self.content_agents[0] if self.content_agents else 'content_creator'
                result = await self.create_content_through_agent(
                    agent, content_type, topic, user
                )
                results.append(result)

        # Summary statistics
        successful = sum(1 for r in results if r.get('success'))
        logger.info(f"✅ Batch created {successful}/{len(topics)} content pieces")

        return results

    def get_content_agent_stats(self) -> Dict[str, Any]:
        """Get statistics about content agent usage"""
        stats = {
            'total_agents': len(self.concrete_executor.agent_classes),
            'content_capable_agents': len(self.content_agents),
            'content_agents': self.content_agents,
            'active_bridges': list(self.active_bridges.keys()),
            'capabilities': {
                'blog': self._count_agents_with_keyword('blog'),
                'social': self._count_agents_with_keyword('social'),
                'video': self._count_agents_with_keyword('video'),
                'image': self._count_agents_with_keyword('image'),
                'seo': self._count_agents_with_keyword('seo'),
                'marketing': self._count_agents_with_keyword('marketing')
            }
        }
        return stats

    def _count_agents_with_keyword(self, keyword: str) -> int:
        """Count agents with specific keyword in their name"""
        return sum(1 for agent in self.content_agents if keyword in agent.lower())


# Global integration instance
content_studio_integration = ContentStudioAgentIntegration()


# Convenience functions for quick access
async def agent_create_content(agent_name: str, content_type: str, topic: str, **kwargs):
    """Quick function to create content through a specific agent"""
    return await content_studio_integration.create_content_through_agent(
        agent_name, content_type, topic, **kwargs
    )


async def orchestrate_campaign(topic: str, agents: List[str] = None, user=None):
    """Quick function to orchestrate a full content campaign"""
    return await content_studio_integration.orchestrate_content_workflow(
        'full_campaign', topic, agents, user
    )


async def batch_create(topics: List[str], content_type: str = 'blog', parallel: bool = True):
    """Quick function to create content in batch"""
    return await content_studio_integration.batch_content_creation(
        topics, content_type, parallel
    )


def get_content_agents():
    """Get list of content-capable agents"""
    return content_studio_integration.content_agents


def get_integration_stats():
    """Get content studio integration statistics"""
    return content_studio_integration.get_content_agent_stats()