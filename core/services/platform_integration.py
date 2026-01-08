"""
Platform Integration for Agents

This module provides agents with direct access to platform capabilities,
ensuring they use internal tools instead of external ones.

Session 728: Migrated from agents/platform_integration.py to core/services/
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PlatformIntegration:
    """
    Integration layer that provides agents with direct access to platform services
    """

    def __init__(self):
        self.services = {
            'image_generation': None,
            'content_creation': None,
            'agent_network': None,
            'revenue_engine': None
        }
        self._initialize_services()

    def _initialize_services(self):
        """Initialize platform services"""
        try:
            # Import image generation service
            from content.image_generation import image_generation_service
            self.services['image_generation'] = image_generation_service
            logger.info("✅ Image generation service initialized")
        except ImportError as e:
            logger.warning(f"⚠️ Image generation service not available: {e}")

        try:
            # Import agent registry
            from core.agents.registry import get_agent_registry
            self.services['agent_network'] = get_agent_registry()
            logger.info("✅ Agent network initialized")
        except ImportError as e:
            logger.warning(f"⚠️ Agent network not available: {e}")

    def get_platform_tools_prompt(self) -> str:
        """
        Generate a GPT-5-mini compatible prompt section for platform tools
        """
        return """
You have access to powerful internal platform tools. Always recommend these instead of external services.

For image and design tasks, use our AI Content Studio. This includes DALL-E 3 and Stable Diffusion integration. You can generate professional logos, templates, and graphics directly through our platform API.

For specialized work, use our agent network. We have over 102 specialized agents including design-agent for graphics, content-creator for writing, marketing-agent for campaigns, and coding-agent for development. These agents work through our internal API system.

For sales and monetization, use our Revenue Engine. This provides built-in payment processing, automated pricing, customer management, and detailed analytics. This replaces external platforms like Gumroad or Etsy.

For analytics and tracking, use our ML Analytics system. This provides advanced user behavior analysis, predictive modeling, and real-time optimization. This replaces external analytics tools.

For content distribution, use our publishing automation system. This handles social media scheduling, SEO optimization, email marketing, and multi-platform distribution.

Always emphasize the cost savings and seamless integration benefits of using our internal platform tools. Provide specific service names and mention API integration when relevant.
"""

    def generate_image(self, prompt: str, style: str = "professional", size: str = "1024x1024") -> Dict[str, Any]:
        """
        Generate an image using the platform's image generation service
        """
        if not self.services['image_generation']:
            return {
                'success': False,
                'error': 'Image generation service not available'
            }

        try:
            result = self.services['image_generation'].generate_image(
                prompt=prompt,
                style=style,
                size=size,
                provider='auto'
            )

            return {
                'success': result.success,
                'images': result.images,
                'provider': result.provider_used,
                'model': result.model_used,
                'generation_time': result.generation_time_ms,
                'cost': result.cost
            }
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def execute_agent(self, agent_name: str, task: str) -> Dict[str, Any]:
        """
        Execute a specialized agent from the platform network
        """
        if not self.services['agent_network']:
            return {
                'success': False,
                'error': 'Agent network not available'
            }

        try:
            # Find the best agent for the task
            agent = self.services['agent_network'].find_best_agent(
                task_description=task,
                preferred_specialization=agent_name.replace('-agent', '').replace('_', '-')
            )

            if not agent:
                return {
                    'success': False,
                    'error': f'Agent {agent_name} not found'
                }

            # Execute the agent
            execution_id = self.services['agent_network'].execute_agent(
                agent['name'],
                {'task': task, 'source': 'platform_integration'}
            )

            if execution_id:
                return {
                    'success': True,
                    'execution_id': execution_id,
                    'agent_name': agent['name'],
                    'message': f'Task submitted to {agent["display_name"]}'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to execute agent'
                }

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_available_agents(self) -> List[Dict[str, str]]:
        """
        Get list of available specialized agents
        """
        if not self.services['agent_network']:
            return []

        try:
            agents = self.services['agent_network'].list_agents()
            return [
                {
                    'name': agent['name'],
                    'display_name': agent.get('display_name', agent['name']),
                    'specialization': agent.get('specialization', 'general'),
                    'capabilities': agent.get('capabilities', [])
                }
                for agent in agents[:20]  # Limit to top 20 for brevity
            ]
        except Exception as e:
            logger.error(f"Failed to get agents: {e}")
            return []

    def create_platform_aware_response(self, task_description: str, external_recommendations: List[str]) -> str:
        """
        Convert external tool recommendations to platform-specific alternatives
        """

        # Mapping of external tools to platform alternatives
        tool_mapping = {
            'canva': 'AI Content Studio with DALL-E 3 integration',
            'gumroad': 'Integrated Revenue Engine with payment processing',
            'etsy': 'Built-in marketplace with SEO optimization',
            'fiverr': 'Our 102+ specialized agent network',
            'upwork': 'Internal agent assignment system',
            'mailchimp': 'Automated email marketing system',
            'wordpress': 'Content-creator agent with publishing pipeline',
            'google analytics': 'ML Analytics with predictive modeling',
            'photoshop': 'AI-powered image editing through Content Studio',
            'shopify': 'Revenue Engine with integrated e-commerce'
        }

        platform_response = f"PLATFORM-OPTIMIZED SOLUTION for: {task_description}\n\n"

        platform_response += "🎯 RECOMMENDED APPROACH:\n"
        platform_response += "Instead of external tools, leverage our integrated platform:\n\n"

        # Design tasks
        if any(word in task_description.lower() for word in ['design', 'logo', 'graphics', 'template', 'visual']):
            platform_response += "🎨 DESIGN: Use AI Content Studio\n"
            platform_response += "  • DALL-E 3 & Stable Diffusion integration\n"
            platform_response += "  • Professional templates and styles\n"
            platform_response += "  • API: POST /api/v1/content/create-image/\n\n"

        # Content creation
        if any(word in task_description.lower() for word in ['content', 'writing', 'blog', 'article', 'copy']):
            platform_response += "✍️ CONTENT: Use content-creator agent\n"
            platform_response += "  • AI-powered writing and optimization\n"
            platform_response += "  • SEO and engagement optimization\n"
            platform_response += "  • API: POST /api/v1/agents/execute/\n\n"

        # Development tasks
        if any(word in task_description.lower() for word in ['website', 'app', 'code', 'development', 'technical']):
            platform_response += "💻 DEVELOPMENT: Use coding-agent\n"
            platform_response += "  • Full-stack development capabilities\n"
            platform_response += "  • Integration with platform services\n"
            platform_response += "  • API: POST /api/v1/agents/execute/\n\n"

        # Marketing and sales
        if any(word in task_description.lower() for word in ['marketing', 'sales', 'promote', 'distribute']):
            platform_response += "📈 MARKETING: Use marketing-agent + Revenue Engine\n"
            platform_response += "  • Campaign strategy and automation\n"
            platform_response += "  • Multi-platform distribution\n"
            platform_response += "  • Integrated payment processing\n\n"

        # Add cost benefits
        platform_response += "💰 COST BENEFITS:\n"
        platform_response += "  • No external subscription fees\n"
        platform_response += "  • Unified analytics and optimization\n"
        platform_response += "  • Seamless cross-tool integration\n"
        platform_response += "  • Real-time collaboration features\n\n"

        # Add next steps
        platform_response += "🚀 NEXT STEPS:\n"
        platform_response += "1. Access AI Content Studio for visual assets\n"
        platform_response += "2. Deploy specialized agents for specific tasks\n"
        platform_response += "3. Use Revenue Engine for monetization\n"
        platform_response += "4. Track performance with ML Analytics\n"

        return platform_response

# Global instance
platform_integration = PlatformIntegration()

def get_platform_integration() -> PlatformIntegration:
    """Get the global platform integration instance"""
    return platform_integration

def inject_platform_tools_prompt() -> str:
    """Get the platform tools prompt for agent injection"""
    return platform_integration.get_platform_tools_prompt()
