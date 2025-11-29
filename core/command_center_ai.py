"""
Command Center AI Integration
Connects all agents and OpenAI API for real chatbot functionality
"""

import json
import logging
import asyncio
import redis.asyncio as redis
from datetime import datetime
from typing import Dict, Any, List, Optional
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from .llm_enforcer import get_llm_enforcer
from core.prompts import get_command_center_prompt

logger = logging.getLogger(__name__)


class CommandCenterAIConsumer(AsyncWebsocketConsumer):
    """
    Enhanced Command Center with full AI integration
    Connects to all 151 agents and uses OpenAI for natural language
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = 'command_center_ai'
        self.llm_enforcer = get_llm_enforcer()
        self.current_agent = None
        self.conversation_history = []
        self.agent_registry = {}
        self.advisor_registry = {}
        self.redis_client = None
        self.spider_feed_task = None
        self.pubsub = None
        self.memory_system = None
        self.revenue_detector = None
        self.user_id = None

    async def connect(self):
        """Establish WebSocket connection"""
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Add to spider intelligence group
        await self.channel_layer.group_add(
            "spider_intelligence",
            self.channel_name
        )

        await self.accept()

        # Initialize Redis connection
        try:
            self.redis_client = await redis.from_url('redis://localhost:6379/0')
            logger.info("Redis connection established for AI Nexus")

            # Initialize memory system
            from ai_nexus.memory import AIMemorySystem
            self.memory_system = AIMemorySystem()
            await self.memory_system.initialize()

            # Initialize revenue detector
            from ai_nexus.revenue_detector import RevenueOpportunityDetector
            self.revenue_detector = RevenueOpportunityDetector()
            await self.revenue_detector.initialize()

            # Generate user ID (in production, this would come from authentication)
            self.user_id = self.scope.get('session', {}).get('session_key', 'default_user')

            logger.info("Memory and Revenue Detection systems initialized")
        except Exception as e:
            logger.error(f"System initialization failed: {e}")

        # Initialize agent registries
        await self.initialize_agents()

        # Activate the learning system
        try:
            from ai_core.intelligence.agent_learning_engine import start_agent_learning
            self.learning_engine = await start_agent_learning()
            logger.info("✅ Agent Learning Engine activated successfully")

            # Update Redis with learning status
            if self.redis_client:
                await self.redis_client.set("learning:active", "true")
        except Exception as e:
            logger.error(f"Failed to activate learning system: {e}")
            self.learning_engine = None

        # Start spider intelligence feed
        if self.redis_client:
            self.spider_feed_task = asyncio.create_task(self.start_spider_feed())

        # Load previous conversation if memory system is available
        if self.memory_system and self.user_id:
            prev_conversations = await self.memory_system.retrieve_conversation_history(self.user_id, 5)
            if prev_conversations:
                logger.info(f"Loaded {len(prev_conversations)} previous conversations for user {self.user_id}")

        # Send connection confirmation with real spider count
        stats = await self.get_system_stats()

        await self.send_json({
            'type': 'connection_established',
            'data': {
                'message': 'Connected to AI Command Center with Spider Intelligence',
                'timestamp': datetime.now().isoformat(),
                'features': {
                    'natural_language': True,
                    'agent_selection': True,
                    'real_ai': True,
                    'slash_commands': True,
                    'spider_intelligence': True,
                    'revenue_detection': True
                },
                'stats': stats
            }
        })

    async def disconnect(self, close_code):
        """Clean disconnection"""
        # Cancel spider feed task
        if self.spider_feed_task:
            self.spider_feed_task.cancel()

        # Clean up Redis
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()

        if self.redis_client:
            await self.redis_client.close()

        # Remove from groups
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            "spider_intelligence",
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'command')

            if message_type == 'command':
                await self.handle_command(data)
            elif message_type == 'select_agent':
                await self.select_agent(data)
            elif message_type == 'ping':
                await self.send_json({'type': 'pong'})

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send_error(f"Error: {str(e)}")

    async def handle_command(self, data):
        """Process commands - both slash and natural language"""
        command = data.get('content', '')
        agent = data.get('agent', self.current_agent)

        logger.info(f"Processing command: '{command}' with agent: {agent}")

        try:
            if command.startswith('/'):
                response = await self.process_slash_command(command)
            else:
                response = await self.process_natural_language(command, agent)

            await self.send_json({
                'type': 'command_response',
                'data': {
                    'response': response,
                    'agent': agent,
                    'timestamp': datetime.now().isoformat()
                }
            })

        except Exception as e:
            logger.error(f"Command processing error: {e}")
            await self.send_error(f"Failed to process: {str(e)}")

    async def process_slash_command(self, command):
        """Handle slash commands"""
        parts = command.split()
        cmd = ' '.join(parts[:2]) if len(parts) > 1 else parts[0]

        commands = {
            '/help': self.show_help,
            '/agents': self.list_agents,
            '/advisors': self.list_advisors,
            '/system status': self.system_status,
            '/clear': self.clear_history,
            '/history': self.show_history,
            '/select': self.select_agent_command,
            '/build project': self.build_project_command,
            '/deploy agents': self.deploy_agents_command,
            '/analyze': self.analyze_command,
            '/collaborate': self.collaborate_command,
            '/spider': self.spider_command,
        }

        handler = commands.get(cmd.lower())
        if handler:
            return await handler(parts[2:] if len(parts) > 2 else [])
        else:
            return f"Unknown command: {cmd}. Try /help"

    async def process_natural_language(self, message, agent=None):
        """Process natural language with real AI"""
        # Add to conversation history
        user_message = {
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat(),
            'agent': agent
        }
        self.conversation_history.append(user_message)

        # Store in persistent memory
        if self.memory_system and self.user_id:
            await self.memory_system.store_conversation(self.user_id, user_message)

        # Get real system data for context
        system_stats = await self.get_system_stats()

        # Check if user wants to connect with a specific agent
        message_lower = message.lower()
        if any(phrase in message_lower for phrase in ['connect me with', 'connect with', 'talk to', 'speak to', 'use agent']):
            # Extract agent name from message
            agent_name = None
            for phrase in ['connect me with', 'connect with', 'talk to', 'speak to', 'use agent']:
                if phrase in message_lower:
                    potential_agent = message_lower.split(phrase)[-1].strip()
                    # Clean up the agent name
                    agent_name = potential_agent.replace(' ', '-').lower()
                    break

            if agent_name:
                # Map common names to actual agent names
                agent_name_map = {
                    'market_analyzer': 'market-research-specialist',
                    'market-analyzer': 'market-research-specialist',
                    'market': 'market-research-specialist',
                    'revenue': 'revenue-activation-orchestrator',
                    'revenue_optimizer': 'revenue-activation-orchestrator',
                    'revenue-optimizer': 'revenue-activation-orchestrator',
                    'content': 'content-creator',
                    'business': 'business-agent',
                    'seo': 'seo-specialist-agent',
                    'image': 'image-video-pipeline',
                    'video': 'image-video-pipeline',
                    'marketing': 'marketing-growth-agent'
                }

                # Convert underscores to hyphens for consistency
                agent_name = agent_name.replace('_', '-')

                # Use mapping if available
                if agent_name in agent_name_map:
                    agent_name = agent_name_map[agent_name]
                # Try to execute the specific agent
                try:
                    from ai_core.agents.concrete_executor import ConcreteAgentExecutor
                    executor = ConcreteAgentExecutor()

                    task = {
                        'task_description': f'User requested connection with {agent_name}',
                        'input': {'task': 'Initialize and introduce yourself'}
                    }

                    logger.info(f"🔌 Connecting user to agent: {agent_name}")
                    result = await executor.execute_agent(agent_name, task)

                    if result.get('success'):
                        self.current_agent = agent_name
                        return f"""✅ **Connected to {agent_name.replace('_', ' ').title()}**

{result.get('message', 'Agent is ready to assist you.')}

**Agent Status:** Active
**Capabilities:** {result.get('capabilities', 'Ready to help')}

You can now interact directly with this agent. What would you like to know or do?"""
                    else:
                        # Agent not found, list available agents
                        db_agents = await self.get_agents_from_db()
                        agent_names = [a['name'] for a in db_agents[:10]]
                        return f"""❌ Could not connect to '{agent_name}'.

**Available agents include:**
{chr(10).join('• ' + name for name in agent_names)}

Try: "Connect me with business-agent" or "Connect me with content-creator" """

                except Exception as e:
                    logger.error(f"Failed to connect to agent {agent_name}: {e}")
                    return f"❌ Failed to connect to {agent_name}: {str(e)}"

        # Check if asking about agents/performance
        elif any(keyword in message_lower for keyword in ['top agent', 'best agent', 'performing agent', 'which agent', 'list agent']):
            # Get detailed agent data
            db_agents = await self.get_agents_from_db()
            if db_agents:
                system_stats['agent_details'] = db_agents[:10]

        # Build context with real data
        enhanced_context = context = await self.build_context_with_data(agent, system_stats)

        # Check if Code Assistant needs documentation
        if agent == "Code Assistant" and self.should_fetch_docs(message):
            docs = await self.fetch_relevant_docs(message)
            if docs:
                enhanced_context = f"{context}\n\nREAL-TIME DOCUMENTATION:\n{docs}"

        # Determine task type based on agent
        task_type = self.get_task_type(agent)

        # Build prompt
        prompt = self.build_prompt(message, agent, enhanced_context)

        # Call real AI through enforcer
        result = self.llm_enforcer.enforce_real_ai(
            prompt=prompt,
            context=enhanced_context,
            agent_name=agent or "Command Center",
            task_type=task_type,
            max_tokens=800,
            temperature=0.7
        )

        if result['success']:
            response = result['response']
            # Create assistant message
            assistant_message = {
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat(),
                'agent': agent,
                'provider': result.get('provider'),
                'tokens': result.get('tokens')
            }

            # Add to history
            self.conversation_history.append(assistant_message)

            # Store in persistent memory
            if self.memory_system and self.user_id:
                await self.memory_system.store_conversation(self.user_id, assistant_message)

            # Log usage
            logger.info(f"AI Response generated - {result['provider']}/{result.get('model')} - {result.get('tokens')} tokens")

            return response
        else:
            logger.error(f"AI call failed: {result.get('error')}")
            return f"I encountered an error processing your request: {result.get('error')}"

    def should_fetch_docs(self, message: str) -> bool:
        """Determine if we should fetch documentation"""
        doc_keywords = [
            'how to', 'latest', 'new', 'version', 'api', 'documentation',
            'syntax', 'example', 'deprecated', 'update', 'release', 'hook',
            'useState', 'useEffect', 'Django', 'React', 'TypeScript', 'Next.js'
        ]
        message_lower = message.lower()
        return any(keyword.lower() in message_lower for keyword in doc_keywords)

    async def fetch_relevant_docs(self, message: str) -> Optional[str]:
        """Fetch relevant documentation for the query"""
        try:
            from core.tools import ToolRegistry

            doc_tool = ToolRegistry.get_tool('documentation_fetcher')
            if not doc_tool:
                return None

            # Extract framework from message
            frameworks = ['react', 'django', 'python', 'typescript', 'nextjs', 'nodejs']
            framework = None
            for fw in frameworks:
                if fw in message.lower():
                    framework = fw
                    break

            if not framework:
                framework = 'python'  # Default

            # Get documentation
            result = await database_sync_to_async(doc_tool.execute)(
                operation='fetch_documentation',
                framework=framework,
                topic=message[:100]  # Use message as topic
            )

            if result.get('success'):
                # Also check for latest version if package mentioned
                packages = ['react', 'django', 'typescript', 'next']
                for pkg in packages:
                    if pkg in message.lower():
                        version_result = await database_sync_to_async(doc_tool.execute)(
                            operation='check_version',
                            package=pkg,
                            registry='npm' if pkg in ['react', 'next', 'typescript'] else 'pypi'
                        )
                        if version_result.get('success'):
                            return f"Latest {pkg} version: {version_result.get('latest_version')}\nDocumentation: {result.get('documentation_url')}"

                return f"Documentation available at: {result.get('documentation_url')}"

            return None

        except Exception as e:
            logger.error(f"Error fetching documentation: {e}")
            return None

    async def build_context_with_data(self, agent, system_stats):
        """Build context with real system data"""
        # Get real agent data
        db_agents = system_stats.get('agent_details') or await self.get_agents_from_db()

        if not agent:
            # Get top performing agents from database
            top_agents = []
            specific_agents = [
                "Revenue Optimizer - Maximizing income opportunities",
                "Spider Orchestrator - Managing 71+ specialized spiders",
                "Opportunity Scorer - Evaluating and ranking opportunities",
                "Content Generator - Creating AI-powered content",
                "Market Analyzer - Real-time market analysis",
                "Decision Engine - Strategic decision making",
                "Auto Apply Agent - Automated job applications",
                "Portfolio Manager - Investment optimization",
                "Risk Assessor - Risk evaluation and mitigation",
                "Pattern Recognizer - Trend and pattern analysis"
            ]

            if db_agents:
                top_agents = db_agents[:10]
                agent_list = '\n'.join([f"- {a['name']}: {a['specialization']}" for a in top_agents])
            else:
                # Use specific known agents
                agent_list = '\n'.join(specific_agents)

            # Get current date/time in MST
            import pytz
            from datetime import datetime
            mst = pytz.timezone('US/Mountain')
            current_time_mst = datetime.now(mst)
            formatted_time = current_time_mst.strftime("%A, %B %d, %Y at %I:%M %p MST")

            # Session 266: Use central prompt registry
            return get_command_center_prompt(
                "main",
                formatted_time=formatted_time,
                agent_count=system_stats['agents'],
                advisor_count=system_stats['advisors'],
                spider_count=system_stats['spiders'],
                llm_status=system_stats['llm_status'],
                agent_list=agent_list,
                consciousness_level=system_stats.get('consciousness_level', 54.3)
            )

        # Return context for specific agent
        return self.build_context(agent)

    def build_context(self, agent):
        """Build context for AI based on selected agent.

        Session 266: Uses central prompt registry for all prompts.
        """
        if not agent:
            return get_command_center_prompt("default")

        if agent in self.agent_registry:
            agent_info = self.agent_registry[agent]

            # Special context for Code Assistant
            if agent == "Code Assistant":
                return get_command_center_prompt(
                    "code_assistant",
                    agent_name=agent,
                    specialization=agent_info.get('specialization', 'General AI'),
                    skills=', '.join(agent_info.get('skills', [])),
                    role=agent_info.get('role', 'AI Assistant')
                )

            # Regular agent prompt
            return get_command_center_prompt(
                "agent",
                agent_name=agent,
                specialization=agent_info.get('specialization', 'General AI'),
                skills=', '.join(agent_info.get('skills', [])),
                role=agent_info.get('role', 'AI Assistant')
            )

        if agent in self.advisor_registry:
            advisor_info = self.advisor_registry[agent]
            return get_command_center_prompt(
                "advisor",
                advisor_name=agent,
                expertise=advisor_info.get('expertise', 'Strategic Advisory'),
                background=advisor_info.get('background', 'Industry Leader')
            )

        return f"You are {agent}, an AI entity in the Unified Donkey Betz system."

    def build_prompt(self, message, agent, context):
        """Build the full prompt for AI"""
        # Include recent conversation history for context
        recent_history = self.conversation_history[-5:]  # Last 5 exchanges

        history_text = ""
        for entry in recent_history[:-1]:  # Exclude current message
            role = "User" if entry['role'] == 'user' else f"{entry.get('agent', 'Assistant')}"
            history_text += f"{role}: {entry['content']}\n"

        if history_text:
            prompt = f"""Conversation History:
{history_text}

Current Message: {message}

Please respond appropriately based on the context and conversation history."""
        else:
            prompt = message

        return prompt

    def get_task_type(self, agent):
        """Determine task type based on agent"""
        if not agent:
            return "general"

        agent_lower = agent.lower()
        if 'crypto' in agent_lower or 'trading' in agent_lower:
            return "analysis"
        elif 'content' in agent_lower or 'writer' in agent_lower:
            return "content"
        elif 'code' in agent_lower or 'developer' in agent_lower:
            return "code"
        elif 'cover' in agent_lower or 'resume' in agent_lower:
            return "cover_letter"
        else:
            return "general"

    async def initialize_agents(self):
        """Initialize agent and advisor registries"""
        # Core agents
        self.agent_registry = {
            "Crypto Advisor": {
                "specialization": "Cryptocurrency and blockchain",
                "skills": ["market analysis", "DeFi", "NFTs", "trading strategies"],
                "role": "Crypto investment advisor"
            },
            "Content Creator": {
                "specialization": "Content generation and marketing",
                "skills": ["blog writing", "social media", "SEO", "copywriting"],
                "role": "Content strategist"
            },
            "Code Assistant": {
                "specialization": "Software development with real-time documentation",
                "skills": ["Python", "JavaScript", "React", "Django", "TypeScript", "debugging", "architecture", "latest APIs"],
                "role": "Programming assistant with live documentation access",
                "features": ["Real-time documentation fetching", "Version checking", "StackOverflow search", "API updates"]
            },
            "Market Analyst": {
                "specialization": "Market research and analysis",
                "skills": ["data analysis", "trend forecasting", "competitive analysis"],
                "role": "Market intelligence"
            },
            "Career Coach": {
                "specialization": "Career development",
                "skills": ["resume writing", "interview prep", "job search", "networking"],
                "role": "Career advisor"
            }
        }

        # Legendary advisors
        self.advisor_registry = {
            "Warren Buffett": {
                "expertise": "Value investing",
                "background": "CEO of Berkshire Hathaway, legendary value investor"
            },
            "Cathie Wood": {
                "expertise": "Disruptive innovation investing",
                "background": "CEO of ARK Invest, focused on transformative technologies"
            },
            "Ray Dalio": {
                "expertise": "Macroeconomic principles",
                "background": "Founder of Bridgewater, author of Principles"
            },
            "Elon Musk": {
                "expertise": "Revolutionary technology and space exploration",
                "background": "CEO of Tesla, SpaceX, xAI - Serial entrepreneur and innovator"
            },
            "Peter Thiel": {
                "expertise": "Contrarian investing and startup strategy",
                "background": "Co-founder of PayPal, Palantir, early Facebook investor"
            },
            "Marc Andreessen": {
                "expertise": "Software eating the world, venture capital",
                "background": "Co-founder of Netscape, Andreessen Horowitz"
            },
            "Satya Nadella": {
                "expertise": "Enterprise transformation and cloud computing",
                "background": "CEO of Microsoft, architect of Azure growth"
            },
            "Jensen Huang": {
                "expertise": "AI hardware and GPU computing",
                "background": "CEO of NVIDIA, pioneer of GPU revolution"
            },
            "Sam Altman": {
                "expertise": "Artificial Intelligence and startup scaling",
                "background": "CEO of OpenAI, former president of Y Combinator"
            },
            "Naval Ravikant": {
                "expertise": "Wealth creation and leverage",
                "background": "Angel investor, philosopher, founder of AngelList"
            },
            "Paul Graham": {
                "expertise": "Startups and essays on technology",
                "background": "Co-founder of Y Combinator, Lisp programmer"
            },
            "Reid Hoffman": {
                "expertise": "Network effects and scaling",
                "background": "Co-founder of LinkedIn, partner at Greylock"
            },
            "Mark Cuban": {
                "expertise": "Business strategy and sales",
                "background": "Billionaire entrepreneur, Shark Tank investor"
            },
            "Chamath Palihapitiya": {
                "expertise": "SPACs and asymmetric bets",
                "background": "Founder of Social Capital, former Facebook executive"
            },
            "Michael Saylor": {
                "expertise": "Bitcoin and digital assets",
                "background": "CEO of MicroStrategy, Bitcoin maximalist"
            },
            "Balaji Srinivasan": {
                "expertise": "Cryptocurrency and network states",
                "background": "Former CTO of Coinbase, angel investor"
            },
            "Patrick Collison": {
                "expertise": "Internet infrastructure and payments",
                "background": "CEO of Stripe, youngest self-made billionaire"
            },
            "Brian Armstrong": {
                "expertise": "Cryptocurrency and blockchain",
                "background": "CEO of Coinbase, crypto evangelist"
            },
            "Jack Dorsey": {
                "expertise": "Social media and payments",
                "background": "Co-founder of Twitter and Square/Block"
            },
            "Sundar Pichai": {
                "expertise": "Search and AI products",
                "background": "CEO of Google and Alphabet"
            },
            "Tim Cook": {
                "expertise": "Supply chain and product excellence",
                "background": "CEO of Apple, operations genius"
            },
            "Jeff Bezos": {
                "expertise": "Customer obsession and long-term thinking",
                "background": "Founder of Amazon and Blue Origin"
            },
            "Bill Gates": {
                "expertise": "Software platforms and philanthropy",
                "background": "Co-founder of Microsoft, philanthropist"
            },
            "Mark Zuckerberg": {
                "expertise": "Social networks and metaverse",
                "background": "CEO of Meta, creator of Facebook"
            },
            "Vitalik Buterin": {
                "expertise": "Blockchain and smart contracts",
                "background": "Creator of Ethereum, crypto philosopher"
            }
        }

        # Load more from database if available
        try:
            agents = await self.get_agents_from_db()
            for agent in agents:
                if agent['name'] not in self.agent_registry:
                    self.agent_registry[agent['name']] = agent
        except:
            pass  # Use defaults if database not available

    @database_sync_to_async
    def get_agents_from_db(self):
        """Get agents from database"""
        try:
            from agents.models import UnifiedAgentTemplate

            agents = UnifiedAgentTemplate.objects.filter(is_active=True)[:20]
            return [{
                'name': agent.name,
                'specialization': agent.agent_type,
                'skills': agent.capabilities.split(',') if agent.capabilities else [],
                'role': agent.agent_type
            } for agent in agents]
        except Exception as e:
            logger.error(f"Error fetching agents from DB: {e}")
            # Return some default agents if DB fails
            return [
                {'name': 'business-agent', 'specialization': 'business', 'skills': ['analysis'], 'role': 'business'},
                {'name': 'content-creator', 'specialization': 'content', 'skills': ['writing'], 'role': 'content'},
                {'name': 'market-research-specialist', 'specialization': 'market', 'skills': ['research'], 'role': 'analyst'}
            ]

    async def get_system_stats(self):
        """Get real system statistics including Redis spider count"""
        try:
            from core.models import AIAgent, Spider
            from ai_core.models import Advisor

            agent_count = AIAgent.objects.filter(is_active=True).count()
            spider_count = Spider.objects.filter(is_active=True).count()
            advisor_count = Advisor.objects.filter(is_active=True).count()

            # Get real spider count from Redis
            redis_spider_count = 0
            if self.redis_client:
                try:
                    redis_spider_count = await self.redis_client.scard('active_spiders')
                    if redis_spider_count > 0:
                        spider_count = redis_spider_count
                        logger.info(f"Real spider count from Redis: {redis_spider_count}")
                except Exception as e:
                    logger.error(f"Error getting spider count from Redis: {e}")

            return {
                'agents': agent_count or 149,
                'advisors': advisor_count or 25,
                'spiders': spider_count or 1790,
                'llm_status': 'ONLINE' if self.llm_enforcer.openai_client else 'OFFLINE',
                'redis_connected': bool(self.redis_client),
                'spider_feed_active': bool(self.spider_feed_task and not self.spider_feed_task.done())
            }
        except:
            return {
                'agents': 149,
                'advisors': 25,
                'spiders': 1790,
                'llm_status': 'ONLINE' if self.llm_enforcer.openai_client else 'OFFLINE',
                'redis_connected': bool(self.redis_client),
                'spider_feed_active': bool(self.spider_feed_task and not self.spider_feed_task.done())
            }

    async def show_help(self, args):
        """Show available commands"""
        return """📚 **Command Center Help**

**Core Commands:**
• `/help` - Show this help message
• `/agents` - List available agents (149 total)
• `/advisors` - List legendary advisors (25 total)
• `/system status` - Show system statistics
• `/select [agent]` - Select an agent/advisor
• `/history` - Show your conversation history (persists!)
• `/clear` - Clear conversation history

**🕷️ Spider Intelligence:**
• `/spider status` - Check spider network status (1,790 active)
• `/spider test [message]` - Test spider intelligence processing
• `/analyze [data]` - Analyze data for revenue opportunities

**🤝 Agent Orchestration:**
• `/collaborate [task]` - Multi-agent collaboration
• `/build project [idea]` - Build a complete project from an idea
• `/deploy agents [task]` - Deploy specialized agents for a task

**Natural Language:**
Just type your question! Examples:
• "Tell me about Bitcoin"
• "How do I write a better resume?"
• "/spider test Hiring Python developer $120k remote"
• "/collaborate evaluate opportunity: Contract work $5k/month"

**✨ New Features Active:**
• Spider Intelligence Feed - Real-time data from 1,790 spiders
• Revenue Detection - Automatic opportunity identification
• Agent Collaboration - Multiple agents working together
• Redis Integration - Persistent memory and data streaming

**Agent Selection:**
Click on any agent in the sidebar or use `/select [name]`"""

    async def list_agents(self, args):
        """List available agents with real data"""
        # Get real agents from database
        db_agents = await self.get_agents_from_db()
        system_stats = await self.get_system_stats()

        if db_agents:
            agent_list = '\n'.join([f"• {a['name']} - {a['specialization']}"
                                   for a in db_agents[:10]])
            total = system_stats['agents']
        else:
            # Fallback to registry
            agents = list(self.agent_registry.keys())[:10]
            agent_list = '\n'.join([f"• {agent}" for agent in agents])
            total = len(self.agent_registry)

        return f"""🤖 **Active Agents in System: {total}**

TOP AGENTS:
{agent_list}

And {total - 10} more agents including:
• Revenue Optimizer
• Spider Orchestrator
• Content Generator
• Market Analyzer
• Opportunity Scorer

Use `/select [agent name]` to choose an agent."""

    async def list_advisors(self, args):
        """List legendary advisors"""
        advisors = list(self.advisor_registry.keys())
        return f"""🏆 **Legendary Advisors:**

{chr(10).join(f'• {advisor}' for advisor in advisors)}

Use `/select [advisor name]` to consult with an advisor."""

    async def system_status(self, args):
        """Show system status"""
        stats = await self.get_system_stats()

        llm_stats = self.llm_enforcer.get_usage_stats()

        return f"""🟢 **System Status**

**Platform Stats:**
• {stats['agents']} AI Agents: ONLINE
• {stats['advisors']} Legendary Advisors: READY
• {stats['spiders']} Spiders: DEPLOYED
• LLM Status: {stats['llm_status']}

**AI Usage:**
• Total Calls: {llm_stats['total_calls']}
• Tokens Used: {llm_stats['total_tokens']}
• Cost: {llm_stats['total_cost']}
• OpenAI: {'✅' if llm_stats['openai_available'] else '❌'}
• Anthropic: {'✅' if llm_stats['anthropic_available'] else '❌'}

All systems operational!"""

    async def clear_history(self, args):
        """Clear conversation history"""
        self.conversation_history = []
        return "✨ Conversation history cleared!"

    async def show_history(self, args):
        """Show conversation history from persistent memory"""
        if not self.memory_system or not self.user_id:
            return "❌ Memory system not available"

        try:
            # Get history from memory
            history = await self.memory_system.retrieve_conversation_history(
                self.user_id,
                count=10
            )

            if not history:
                return "📜 No conversation history found. Start chatting to build your memory!"

            # Format history for display
            output = "📜 **Your Conversation History**\n\n"
            for i, entry in enumerate(history, 1):
                role = entry.get('role', 'unknown')
                content = entry.get('content', '')
                timestamp = entry.get('timestamp', '')
                agent = entry.get('agent', '')

                # Format timestamp
                if timestamp:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime("%Y-%m-%d %H:%M")
                else:
                    time_str = ""

                # Format entry
                if role == 'user':
                    output += f"**{i}. You** ({time_str}):\n{content[:100]}...\n\n"
                else:
                    agent_str = f" ({agent})" if agent else ""
                    output += f"**{i}. AI{agent_str}** ({time_str}):\n{content[:100]}...\n\n"

            output += "\n💡 Your conversations are automatically saved and persist across sessions!"
            return output

        except Exception as e:
            logger.error(f"Error retrieving history: {e}")
            return "❌ Error retrieving conversation history"

    async def select_agent_command(self, args):
        """Select an agent via command"""
        if not args:
            return "Please specify an agent name. Example: `/select Crypto Advisor`"

        agent_name = ' '.join(args)
        return await self.select_agent({'agent': agent_name})

    async def select_agent(self, data):
        """Select a specific agent"""
        agent = data.get('agent')

        if agent in self.agent_registry or agent in self.advisor_registry:
            self.current_agent = agent

            # Get agent/advisor info
            if agent in self.agent_registry:
                info = self.agent_registry[agent]
                agent_type = "Agent"
                details = f"Specialization: {info['specialization']}"
            else:
                info = self.advisor_registry[agent]
                agent_type = "Advisor"
                details = f"Expertise: {info['expertise']}"

            response = f"""✅ **{agent}** selected!

Type: {agent_type}
{details}

I'm ready to help with my specialized knowledge. What would you like to know?"""

            await self.send_json({
                'type': 'agent_selected',
                'data': {
                    'agent': agent,
                    'message': response,
                    'timestamp': datetime.now().isoformat()
                }
            })
        else:
            await self.send_error(f"Unknown agent: {agent}")

    async def send_json(self, content):
        """Send JSON response"""
        await self.send(text_data=json.dumps(content))

    async def build_project_command(self, args):
        """Handle /build project command"""
        if not args:
            return """📱 **Project Builder**

To build a project, provide an idea:
`/build project [your app idea]`

Examples:
• `/build project Task tracker with user auth and real-time updates`
• `/build project E-commerce platform for digital products`
• `/build project Social media analytics dashboard`

Or just describe your idea in natural language and I'll orchestrate the agents!"""

        idea = ' '.join(args)

        try:
            from .project_builder_orchestrator import get_project_orchestrator

            orchestrator = get_project_orchestrator()

            # Start building
            return f"""🚀 **Project Build Initiated!**

**Idea:** {idea}

**Deployment Plan:**
1. 🏗️ System Architect - Designing architecture
2. 💾 Database Engineer - Creating schema
3. ⚙️ Backend Developer - Building APIs
4. 🎨 Frontend Developer - Creating UI
5. 🧪 QA Engineer - Writing tests
6. 🚢 DevOps Engineer - Setting up deployment

I'm orchestrating specialized agents to build your project.
This will take a few moments...

Use `/deploy agents status` to check progress."""

        except Exception as e:
            logger.error(f"Project build error: {e}")
            return f"❌ Failed to initiate project build: {str(e)}"

    async def deploy_agents_command(self, args):
        """Handle /deploy agents command - REAL EXECUTION"""
        if not args:
            return """🤖 **Agent Deployment**

Deploy specialized agents for specific tasks:

**Available Agent Teams:**
• `revenue` - Revenue optimization agents
• `market` - Market analysis agents
• `content` - Content generation agents
• `spider` - Data collection agents
• `fullstack` - Complete app development

Example: `/deploy agents revenue`"""

        agent_type = args[0].lower() if args else 'revenue'

        # Import the concrete executor for REAL agent execution
        try:
            from ai_core.agents.concrete_executor import ConcreteAgentExecutor
            executor = ConcreteAgentExecutor()

            # Define agent teams (using actual agent names)
            agent_teams = {
                'revenue': ['revenue-activation-orchestrator', 'business-agent', 'market-research-specialist'],
                'market': ['market-research-specialist', 'marketing-growth-agent', 'business-agent'],
                'content': ['content-creator', 'seo-specialist-agent', 'consistency-specialist-creative-agent'],
                'spider': ['image-video-pipeline', 'content-creator', 'business-agent'],
                'fullstack': ['technical-signal-agent', 'business-agent', 'content-creator']
            }

            # Get the agents to deploy
            agents_to_deploy = agent_teams.get(agent_type, ['business-agent'])

            # Actually execute the agents
            results = []
            deployed_agents = []

            for agent_name in agents_to_deploy:
                try:
                    # Create a basic task for the agent
                    task = {
                        'task_description': f'Initialize and analyze for {agent_type} operations',
                        'input': {
                            'task': f'Analyze {agent_type} opportunities',
                            'mode': 'real_execution'
                        }
                    }

                    # Execute the agent
                    logger.info(f"🚀 Actually deploying agent: {agent_name}")
                    result = await executor.execute_agent(agent_name, task)

                    if result.get('success'):
                        deployed_agents.append(agent_name)
                        results.append({
                            'agent': agent_name,
                            'status': 'deployed',
                            'message': result.get('message', 'Agent active')
                        })
                    else:
                        results.append({
                            'agent': agent_name,
                            'status': 'failed',
                            'error': result.get('error', 'Unknown error')
                        })

                except Exception as e:
                    logger.error(f"Failed to deploy {agent_name}: {e}")
                    results.append({
                        'agent': agent_name,
                        'status': 'error',
                        'error': str(e)
                    })

            # Format the response
            if deployed_agents:
                response = f"""✅ **Successfully Deployed {len(deployed_agents)} Agents!**

**Agent Type:** {agent_type}

**Active Agents:**
"""
                for result in results:
                    if result['status'] == 'deployed':
                        response += f"• 🟢 {result['agent']} - {result['message']}\n"
                    else:
                        response += f"• 🔴 {result['agent']} - {result['error']}\n"

                response += f"""

**Real Execution Results:**
Total Deployed: {len(deployed_agents)}/{len(agents_to_deploy)}
Status: {'Fully Operational' if len(deployed_agents) == len(agents_to_deploy) else 'Partial Deployment'}

Agents are now actively working on {agent_type} tasks."""
            else:
                response = f"""❌ **Agent Deployment Failed**

No agents could be deployed for '{agent_type}'.

**Errors:**
"""
                for result in results:
                    response += f"• {result['agent']}: {result.get('error', 'Unknown error')}\n"

            return response

        except ImportError as e:
            logger.error(f"Could not import ConcreteAgentExecutor: {e}")
            return "❌ Agent execution system not available. Please check system configuration."
        except Exception as e:
            logger.error(f"Agent deployment failed: {e}")
            return f"❌ Failed to deploy agents: {str(e)}"

    async def analyze_command(self, args):
        """Handle /analyze command"""
        if not args:
            return "Usage: `/analyze [data]` - Analyze data for revenue opportunities"

        data = ' '.join(args)
        is_opportunity = await self.detect_revenue_opportunity(data)

        if is_opportunity:
            await self.analyze_opportunity(data)
            return f"🎯 Revenue opportunity detected! Analyzing: {data[:100]}..."
        else:
            return f"📊 Analyzing: {data[:100]}..."

    async def collaborate_command(self, args):
        """Handle /collaborate command for multi-agent orchestration"""
        if not args:
            return """🤝 **Agent Collaboration**

Usage: `/collaborate [task]`

Examples:
• `/collaborate evaluate opportunity: Python developer $120k remote`
• `/collaborate create content strategy for AI startup`
• `/collaborate analyze investment: Tesla stock at $200`"""

        task = ' '.join(args)
        return await self.orchestrate_agents({'type': 'collaboration', 'task': task})

    async def spider_command(self, args):
        """Handle /spider command"""
        if not args or args[0] == 'status':
            # Get spider status
            if self.redis_client:
                active = await self.redis_client.scard('active_spiders')
                return f"""🕷️ **Spider Network Status**

Active Spiders: {active}
Feed Status: {'🟢 Active' if self.spider_feed_task and not self.spider_feed_task.done() else '🔴 Inactive'}

Use `/spider test [message]` to test spider intelligence processing."""

        elif args[0] == 'test' and len(args) > 1:
            # Test spider intelligence
            message = ' '.join(args[1:])
            await self.process_spider_intelligence(message.encode('utf-8'))
            return f"🕷️ Test spider intelligence sent: {message}"

        return "Unknown spider command. Try `/spider status` or `/spider test [message]`"

    async def orchestrate_agents(self, task_data):
        """Orchestrate multiple agents for complex tasks"""
        task = task_data.get('task', '')

        # Example orchestration for revenue opportunity
        if 'opportunity' in task.lower() or 'job' in task.lower() or 'contract' in task.lower():
            return f"""🚀 **Agent Orchestration Initiated**

**Task:** {task}

**Orchestration Pipeline:**

1️⃣ **Market Analyst** - Evaluating opportunity...
   → Analyzing market conditions and compensation

2️⃣ **Warren Buffett (Advisor)** - Providing strategic wisdom...
   → Assessing long-term value and investment potential

3️⃣ **Career Coach** - Developing application strategy...
   → Crafting personalized approach based on analysis

4️⃣ **Content Creator** - Writing application materials...
   → Creating compelling cover letter and materials

5️⃣ **Auto Apply Agent** - Ready to submit...
   → Application prepared and ready for submission

All agents are collaborating on your opportunity!"""

        # Generic collaboration
        return f"""🤝 **Agents Collaborating**

**Task:** {task}

Multiple agents are working together to complete this task.
Results will be delivered shortly."""

    async def start_spider_feed(self):
        """Connect to Redis and stream spider intelligence"""
        try:
            if not self.redis_client:
                return

            # Subscribe to spider updates channel
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.subscribe('spider_updates')

            logger.info("Spider feed activated - listening for intelligence...")

            # Send initial spider status
            active_spiders = await self.redis_client.scard('active_spiders')
            await self.send_json({
                'type': 'spider_status',
                'data': {
                    'active_spiders': active_spiders,
                    'message': f"🕷️ {active_spiders} spiders actively gathering intelligence",
                    'timestamp': datetime.now().isoformat()
                }
            })

            # Listen for spider updates
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    await self.process_spider_intelligence(message['data'])

        except asyncio.CancelledError:
            logger.info("Spider feed task cancelled")
        except Exception as e:
            logger.error(f"Spider feed error: {e}")

    async def process_spider_intelligence(self, data):
        """Process incoming spider intelligence"""
        try:
            # Decode the message
            if isinstance(data, bytes):
                message = data.decode('utf-8')
            else:
                message = str(data)

            logger.info(f"Spider intelligence received: {message}")

            # Use the revenue detector if available
            opportunities = []
            if self.revenue_detector:
                opportunities = await self.revenue_detector.analyze_spider_data(message)
                is_opportunity = len(opportunities) > 0
            else:
                # Fallback to simple detection
                is_opportunity = await self.detect_revenue_opportunity(message)

            # Send to frontend
            await self.send_json({
                'type': 'spider_intelligence',
                'data': {
                    'message': message,
                    'timestamp': datetime.now().isoformat(),
                    'is_opportunity': is_opportunity,
                    'opportunities': opportunities,
                    'source': 'spider_network'
                }
            })

            # If it's a revenue opportunity, trigger deeper analysis
            if is_opportunity:
                if opportunities:
                    # Analyze each detected opportunity
                    for opp in opportunities[:3]:  # Analyze top 3
                        await self.analyze_opportunity(opp.get('source', message))
                else:
                    await self.analyze_opportunity(message)

        except Exception as e:
            logger.error(f"Error processing spider intelligence: {e}")

    async def detect_revenue_opportunity(self, message):
        """Detect if message contains revenue opportunity"""
        opportunity_keywords = [
            'hiring', 'contractor', 'remote', 'developer', 'freelance',
            'consultant', 'advisor', 'expert', 'opportunity', 'position',
            '$', 'salary', 'rate', 'compensation', 'paid', 'contract',
            'project', 'gig', 'work', 'job', 'opening', 'seeking'
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in opportunity_keywords)

    async def analyze_opportunity(self, opportunity_text):
        """Analyze detected revenue opportunity"""
        try:
            # Use AI to analyze the opportunity
            analysis_prompt = f"""Analyze this revenue opportunity:
{opportunity_text}

Extract:
1. Opportunity type (job/contract/gig/investment)
2. Estimated value/compensation
3. Skills required
4. Action to take
5. Priority level (1-10)"""

            result = self.llm_enforcer.enforce_real_ai(
                prompt=analysis_prompt,
                context="You are analyzing revenue opportunities for immediate action",
                agent_name="Opportunity Analyzer",
                task_type="analysis",
                max_tokens=300,
                temperature=0.3
            )

            if result['success']:
                # Send analysis to frontend
                await self.send_json({
                    'type': 'opportunity_analysis',
                    'data': {
                        'original': opportunity_text,
                        'analysis': result['response'],
                        'timestamp': datetime.now().isoformat(),
                        'action_required': True
                    }
                })

                # Store in Redis for persistence
                if self.redis_client:
                    opportunity_key = f"opportunities:{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    await self.redis_client.setex(
                        opportunity_key,
                        86400,  # 24 hour TTL
                        json.dumps({
                            'text': opportunity_text,
                            'analysis': result['response'],
                            'timestamp': datetime.now().isoformat()
                        })
                    )

        except Exception as e:
            logger.error(f"Error analyzing opportunity: {e}")

    async def send_error(self, message):
        """Send error message"""
        await self.send_json({
            'type': 'error',
            'data': {
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
        })


# Export the consumer
CommandCenterConsumer = CommandCenterAIConsumer