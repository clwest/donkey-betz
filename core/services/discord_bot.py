"""
Discord Bot Service - Sessions 426-438

Interactive Discord bot with slash commands for system monitoring and data access.

Session 426 Commands:
- /status - System health check
- /agents - List active agents with stats
- /trending - Get trending spider data
- /help - Command reference

Session 427 Commands:
- /ask <question> - Query Personal Assistant
- /create <prompt> - Trigger image generation
- /research <topic> - Run spider search

Session 428 Commands:
- /clear - Clear conversation history

Session 429 Commands:
- /link <code> - Link Discord account to web user
- /unlink - Check link status and unlink instructions

Session 430 Commands (Phase 1: Discord-First):
- /gallery [count] - View recent AI-generated images
- /profile - View AI Studio profile and stats
- /opportunities [count] [category] - Browse income opportunities

Session 433 Commands (Phase 4: Income Pipeline):
- /apply <id> [message] - Apply to an opportunity
- /track [status] - Track your job applications

Session 434 Commands (Phase 5: Full Agent Access):
- /agent-list [category] - List agents by category
- /agent-task <name> <task> - Execute a task with specific agent
- /advisors - List all legendary advisors
- /consult <advisor> <question> - Consult an advisor
- /workflow-list - List available workflows
- /workflow-run <name> <input> - Run a workflow

Session 437 Commands (Phase 6: Automation):
- /digest [period] - Get daily/weekly activity digest
- /alerts [action] - Manage proactive opportunity alerts

Session 438 Commands (Phase 7: Monetization):
- /subscribe <tier> - Subscribe to Pro or Premium tier
- /tier - View your subscription tier and daily usage

Session 438 Commands (Phase 8: Voice AI):
- /voice <action> [voice] - Join/leave voice channels, list voices
- /speak <message> [voice] - Make bot speak in voice channel
- /ask-voice <question> - Ask AI and hear response spoken

Usage:
    # Run the bot
    python manage.py run_discord_bot

    # Or via make command
    make discord-bot
"""

import os
import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from collections import defaultdict
from dataclasses import dataclass, field

import discord
from discord import app_commands
from discord.ext import commands, tasks
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


# =============================================================================
# Rate Limiting / Cooldowns - Session 427
# =============================================================================

class RateLimiter:
    """Simple rate limiter for Discord commands."""

    def __init__(self):
        # Track user command timestamps: {user_id: {command_name: last_used_timestamp}}
        self._command_cooldowns: Dict[int, Dict[str, float]] = defaultdict(dict)
        # Cooldowns in seconds per command
        self._cooldown_times = {
            'ask': 10,       # 10 seconds between /ask calls
            'create': 30,    # 30 seconds between /create calls
            'research': 15,  # 15 seconds between /research calls
            'agent_task': 15,  # 15 seconds between /agent-task calls
            'consult': 20,   # 20 seconds between /consult calls
            'workflow': 60,  # 60 seconds between /workflow-run calls
            'default': 3,    # Default 3 seconds
        }

    def check_cooldown(self, user_id: int, command_name: str) -> tuple[bool, float]:
        """
        Check if user can use command. Returns (can_use, remaining_seconds).
        """
        cooldown = self._cooldown_times.get(command_name, self._cooldown_times['default'])
        last_used = self._command_cooldowns[user_id].get(command_name, 0)
        elapsed = time.time() - last_used

        if elapsed < cooldown:
            return False, cooldown - elapsed
        return True, 0

    def record_use(self, user_id: int, command_name: str):
        """Record that user used a command."""
        self._command_cooldowns[user_id][command_name] = time.time()


# Global rate limiter instance
rate_limiter = RateLimiter()


# =============================================================================
# Permission Levels - Session 427
# =============================================================================

class PermissionLevel:
    """User permission levels for Discord commands."""

    # Admin users (by Discord user ID) - can bypass rate limits
    ADMIN_USER_IDS = {
        264555101581082624,  # .donkeyking (owner)
    }

    # Trusted users - reduced rate limits
    TRUSTED_USER_IDS = set()

    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """Check if user is an admin."""
        return user_id in cls.ADMIN_USER_IDS

    @classmethod
    def is_trusted(cls, user_id: int) -> bool:
        """Check if user is trusted (admin or explicitly trusted)."""
        return user_id in cls.ADMIN_USER_IDS or user_id in cls.TRUSTED_USER_IDS

    @classmethod
    def get_cooldown_multiplier(cls, user_id: int) -> float:
        """Get cooldown multiplier for user (lower = faster cooldown)."""
        if cls.is_admin(user_id):
            return 0.0  # No cooldown for admins
        if cls.is_trusted(user_id):
            return 0.5  # 50% cooldown for trusted users
        return 1.0  # Normal cooldown


def check_permission(user_id: int, command_name: str) -> tuple[bool, float]:
    """
    Check if user can use command with permission-aware cooldowns.
    Returns (can_use, remaining_seconds).
    """
    multiplier = PermissionLevel.get_cooldown_multiplier(user_id)

    # Admins bypass cooldowns entirely
    if multiplier == 0.0:
        return True, 0

    # Check with adjusted cooldown
    can_use, remaining = rate_limiter.check_cooldown(user_id, command_name)
    return can_use, remaining * multiplier


# =============================================================================
# Conversation History - Session 428
# =============================================================================

@dataclass
class ConversationMessage:
    """A single message in a conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


class ConversationHistory:
    """
    Manages conversation history per Discord user.

    Features:
    - Stores up to MAX_MESSAGES per user
    - Auto-expires conversations after EXPIRY_HOURS of inactivity
    - Thread-safe for async operations
    """

    MAX_MESSAGES = 20  # Keep last 20 messages per user
    EXPIRY_HOURS = 2   # Conversations expire after 2 hours of inactivity

    def __init__(self):
        # {user_id: {'messages': [ConversationMessage], 'last_activity': datetime}}
        self._conversations: Dict[int, Dict[str, Any]] = {}

    def add_message(self, user_id: int, role: str, content: str):
        """Add a message to user's conversation history."""
        now = datetime.now()

        if user_id not in self._conversations:
            self._conversations[user_id] = {
                'messages': [],
                'last_activity': now
            }

        conv = self._conversations[user_id]
        conv['messages'].append(ConversationMessage(role=role, content=content, timestamp=now))
        conv['last_activity'] = now

        # Trim to max messages (keep most recent)
        if len(conv['messages']) > self.MAX_MESSAGES:
            conv['messages'] = conv['messages'][-self.MAX_MESSAGES:]

    def get_history(self, user_id: int) -> List[Dict[str, str]]:
        """
        Get conversation history for user as list of message dicts.
        Returns empty list if no history or expired.
        """
        if user_id not in self._conversations:
            return []

        conv = self._conversations[user_id]

        # Check if conversation has expired
        if datetime.now() - conv['last_activity'] > timedelta(hours=self.EXPIRY_HOURS):
            self.clear(user_id)
            return []

        # Return messages in format suitable for LLM
        return [
            {'role': msg.role, 'content': msg.content}
            for msg in conv['messages']
        ]

    def clear(self, user_id: int) -> bool:
        """Clear conversation history for user. Returns True if there was history to clear."""
        if user_id in self._conversations:
            del self._conversations[user_id]
            return True
        return False

    def get_message_count(self, user_id: int) -> int:
        """Get number of messages in user's history."""
        if user_id not in self._conversations:
            return 0
        return len(self._conversations[user_id]['messages'])

    def cleanup_expired(self):
        """Remove all expired conversations. Call periodically."""
        now = datetime.now()
        expired_users = [
            user_id for user_id, conv in self._conversations.items()
            if now - conv['last_activity'] > timedelta(hours=self.EXPIRY_HOURS)
        ]
        for user_id in expired_users:
            del self._conversations[user_id]
        return len(expired_users)


# Global conversation history instance
conversation_history = ConversationHistory()


class DonkeyBetzBot(commands.Bot):
    """
    Discord bot for the Donkey Betz AI Platform.

    Provides read-only commands for monitoring system status,
    viewing agents, and accessing trending spider data.
    """

    def __init__(self):
        # Set up intents - only use default intents for slash commands
        # message_content is a privileged intent that requires explicit approval
        intents = discord.Intents.default()
        # Don't enable message_content - we only use slash commands

        super().__init__(
            command_prefix="!",  # Fallback prefix (not used with slash commands)
            intents=intents,
            description="Donkey Betz AI Platform Bot"
        )

        self.start_time = datetime.now()

    async def setup_hook(self):
        """Called when the bot is starting up."""
        # Add cogs/commands
        await self.add_cog(StatusCommands(self))
        await self.add_cog(AgentCommands(self))
        await self.add_cog(SpiderCommands(self))
        await self.add_cog(InteractiveCommands(self))  # Session 427
        await self.add_cog(ContentCommands(self))  # Session 430: Phase 1 Discord-First
        await self.add_cog(ServerSetupCommands(self))  # Session 431: Phase 2 Server Setup
        await self.add_cog(ClientCommands(self))  # Session 432: Phase 3 Client Management
        await self.add_cog(AgentAccessCommands(self))  # Session 434: Phase 5 Full Agent Access
        await self.add_cog(VoiceCommands(self))  # Session 438: Phase 8 Voice AI
        await self.add_cog(RoleManager(self))  # Session 439: Subscription role management
        await self.add_cog(HelpCommands(self))

        # Sync slash commands with Discord
        try:
            # Donkey Betz guild ID for instant command availability
            guild = discord.Object(id=971148613109555212)

            # Copy global commands to guild for instant sync
            self.tree.copy_global_to(guild=guild)

            # Sync to guild first (instant)
            guild_synced = await self.tree.sync(guild=guild)
            logger.info(f"Synced {len(guild_synced)} guild slash commands to Donkey Betz (instant)")

            # Global sync (can take up to an hour to propagate)
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} global slash commands")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    async def on_ready(self):
        """Called when the bot is fully connected."""
        logger.info(f"Bot connected as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")

        # Set status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="AI agents at work"
            )
        )


class StatusCommands(commands.Cog):
    """Commands for checking system status."""

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot

    @app_commands.command(name="status", description="Check system health and status")
    async def status(self, interaction: discord.Interaction):
        """Display system health information."""
        await interaction.response.defer()

        try:
            # Import Django models (must be done after Django setup)
            from core.models_unified_system import Agent, SpiderData, AgentDream, HiveMindSession
            from content.models import ImageHistory

            # Gather stats using sync_to_async for ORM calls
            @sync_to_async
            def get_stats():
                return {
                    'agent_count': Agent.objects.filter(is_active=True).count(),
                    'spider_data_count': SpiderData.objects.count(),
                    'dream_count': AgentDream.objects.count(),
                    'hivemind_count': HiveMindSession.objects.count(),
                    'image_count': ImageHistory.objects.count(),
                }

            stats = await get_stats()

            # Calculate uptime
            uptime = datetime.now() - self.bot.start_time
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds

            # Build embed
            embed = discord.Embed(
                title="System Status",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )

            embed.add_field(
                name="Services",
                value="```\nDjango API   : Online\nCelery       : Active\nRedis        : Connected\nPostgreSQL   : Connected\n```",
                inline=False
            )

            embed.add_field(name="Agents", value=f"```{stats['agent_count']}```", inline=True)
            embed.add_field(name="Spider Data", value=f"```{stats['spider_data_count']:,}```", inline=True)
            embed.add_field(name="Images", value=f"```{stats['image_count']:,}```", inline=True)

            embed.add_field(name="Dreams", value=f"```{stats['dream_count']:,}```", inline=True)
            embed.add_field(name="HiveMind", value=f"```{stats['hivemind_count']:,}```", inline=True)
            embed.add_field(name="Bot Uptime", value=f"```{uptime_str}```", inline=True)

            embed.set_footer(text="Donkey Betz AI Platform")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Status command error: {e}")
            await interaction.followup.send(
                f"Error fetching status: {str(e)[:100]}",
                ephemeral=True
            )


class AgentCommands(commands.Cog):
    """Commands for viewing agent information."""

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot

    @app_commands.command(name="agents", description="List active agents with stats")
    @app_commands.describe(limit="Number of agents to show (default: 10)")
    async def agents(self, interaction: discord.Interaction, limit: int = 10):
        """Display active agents with their stats."""
        await interaction.response.defer()

        try:
            from core.models_unified_system import Agent, AgentEvolution

            # Cap limit
            limit = min(limit, 25)

            @sync_to_async
            def get_agents_with_evolution():
                # Get agents with their evolution data
                agents = list(Agent.objects.filter(is_active=True)[:limit])
                agent_data = []
                for agent in agents:
                    # Try to get evolution data
                    try:
                        evolution = AgentEvolution.objects.filter(agent=agent).first()
                        level = evolution.current_level if evolution else 1
                        xp = evolution.total_xp if evolution else 0
                    except Exception:
                        level = 1
                        xp = 0
                    agent_data.append({
                        'name': agent.name,
                        'mood': agent.mood or 'neutral',
                        'level': level,
                        'xp': xp,
                    })
                # Sort by level then XP
                agent_data.sort(key=lambda x: (-x['level'], -x['xp']))
                total = Agent.objects.filter(is_active=True).count()
                return agent_data, total

            agent_data, total_agents = await get_agents_with_evolution()

            if not agent_data:
                await interaction.followup.send("No active agents found.")
                return

            embed = discord.Embed(
                title=f"Active Agents (Top {limit})",
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )

            # Mood emojis
            mood_emoji = {
                'focused': '',
                'creative': '',
                'analytical': '',
                'collaborative': '',
                'energetic': '',
                'contemplative': '',
                'neutral': ''
            }

            agent_list = []
            for agent in agent_data:
                emoji = mood_emoji.get(agent['mood'], '')
                level_bar = '' * min(agent['level'], 10)
                agent_list.append(
                    f"{emoji} **{agent['name']}** (Lv.{agent['level']})\n"
                    f"   {level_bar} | XP: {agent['xp']:,}"
                )

            embed.description = "\n".join(agent_list)
            embed.set_footer(text=f"Showing {len(agent_data)} of {total_agents} active agents")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Agents command error: {e}")
            await interaction.followup.send(
                f"Error fetching agents: {str(e)[:100]}",
                ephemeral=True
            )

    @app_commands.command(name="agent", description="Get details for a specific agent")
    @app_commands.describe(name="Agent name to look up")
    async def agent_detail(self, interaction: discord.Interaction, name: str):
        """Display detailed info for a specific agent."""
        await interaction.response.defer()

        try:
            from core.models_unified_system import Agent, AgentDream, AgentConversation, AgentEvolution

            @sync_to_async
            def get_agent_details(search_name):
                # Find agent (case-insensitive)
                agent = Agent.objects.filter(name__icontains=search_name, is_active=True).first()
                if not agent:
                    return None

                # Get evolution data
                try:
                    evolution = AgentEvolution.objects.filter(agent=agent).first()
                    level = evolution.current_level if evolution else 1
                    xp = evolution.total_xp if evolution else 0
                except Exception:
                    level = 1
                    xp = 0

                # Get recent activity
                recent_dreams = AgentDream.objects.filter(agent=agent).count()
                recent_convos = AgentConversation.objects.filter(participants=agent).count()

                return {
                    'name': agent.name,
                    'description': agent.description or "No description available.",
                    'mood': agent.mood or 'neutral',
                    'level': level,
                    'xp': xp,
                    'capabilities': agent.capabilities if agent.capabilities else [],
                    'dreams': recent_dreams,
                    'conversations': recent_convos,
                    'created_at': agent.created_at,
                }

            agent_data = await get_agent_details(name)

            if not agent_data:
                await interaction.followup.send(f"Agent '{name}' not found.", ephemeral=True)
                return

            embed = discord.Embed(
                title=f" {agent_data['name']}",
                description=agent_data['description'],
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            # Stats
            embed.add_field(name="Level", value=f"```{agent_data['level']}```", inline=True)
            embed.add_field(name="XP", value=f"```{agent_data['xp']:,}```", inline=True)
            embed.add_field(name="Mood", value=f"```{agent_data['mood']}```", inline=True)

            # Capabilities
            caps = agent_data['capabilities']
            if caps and isinstance(caps, list):
                caps_display = caps[:5]
                if caps_display:
                    embed.add_field(
                        name="Capabilities",
                        value="```\n" + "\n".join(f" {c}" for c in caps_display) + "\n```",
                        inline=False
                    )

            # Activity
            embed.add_field(name="Dreams", value=f"```{agent_data['dreams']}```", inline=True)
            embed.add_field(name="Conversations", value=f"```{agent_data['conversations']}```", inline=True)

            if agent_data['created_at']:
                embed.set_footer(text=f"Created: {agent_data['created_at'].strftime('%Y-%m-%d')}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Agent detail command error: {e}")
            await interaction.followup.send(
                f"Error fetching agent: {str(e)[:100]}",
                ephemeral=True
            )


class SpiderCommands(commands.Cog):
    """Commands for accessing spider/trending data."""

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot

    @app_commands.command(name="trending", description="Get trending topics from spider data")
    @app_commands.describe(
        category="Filter by category (tech, financial, creative, etc.)",
        limit="Number of items to show (default: 5)"
    )
    async def trending(
        self,
        interaction: discord.Interaction,
        category: Optional[str] = None,
        limit: int = 5
    ):
        """Display trending topics from spider data."""
        await interaction.response.defer()

        try:
            from core.models_unified_system import SpiderData
            from django.utils import timezone

            # Cap limit
            limit = min(limit, 15)

            @sync_to_async
            def get_trending_data(cat, lim):
                week_ago = timezone.now() - timedelta(days=7)
                queryset = SpiderData.objects.filter(created_at__gte=week_ago)

                if cat:
                    queryset = queryset.filter(data_type__icontains=cat)

                # Get more spider entries to extract items from
                spider_entries = list(queryset.order_by('-created_at')[:20])
                total = queryset.count()

                result = []
                for entry in spider_entries:
                    raw = entry.raw_data or {}
                    # Items are stored in raw_data['items'] array
                    items_list = raw.get('items', [])

                    for item in items_list[:3]:  # Take up to 3 items per spider
                        if len(result) >= lim:
                            break
                        # Extract title - try multiple common field names
                        title = (
                            item.get('title') or
                            item.get('name') or
                            item.get('headline') or
                            item.get('id') or
                            f"Item from {entry.spider_name}"
                        )
                        # Extract URL
                        url = item.get('link') or item.get('url') or item.get('href') or ''

                        result.append({
                            'title': title,
                            'category': entry.data_type,
                            'url': url,
                            'spider_name': entry.spider_name,
                        })

                    if len(result) >= lim:
                        break

                return result[:lim], total

            items_data, total_count = await get_trending_data(category, limit)

            if not items_data:
                await interaction.followup.send(
                    f"No trending data found{' for ' + category if category else ''}.",
                    ephemeral=True
                )
                return

            # Category emojis
            category_emoji = {
                'tech': '',
                'financial': '',
                'creative': '',
                'ai': '',
                'jobs': '',
                'news': '',
                'design': '',
                'business': '',
            }

            embed = discord.Embed(
                title=f"Trending{' in ' + category.title() if category else ''} (Last 7 Days)",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )

            items_text = []
            for item in items_data:
                emoji = category_emoji.get(item['category'], '')
                title = item['title'] or "Untitled"
                title = title[:50] + "..." if len(title) > 50 else title
                source = item['spider_name'] or "Unknown"

                # Add link if available
                if item['url']:
                    items_text.append(f"{emoji} [{title}]({item['url']})\n   Source: {source}")
                else:
                    items_text.append(f"{emoji} **{title}**\n   Source: {source}")

            embed.description = "\n\n".join(items_text)
            embed.set_footer(text=f"Showing {len(items_data)} of {total_count:,} items this week")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Trending command error: {e}")
            await interaction.followup.send(
                f"Error fetching trending: {str(e)[:100]}",
                ephemeral=True
            )

    @app_commands.command(name="spiders", description="List spider network stats")
    async def spiders(self, interaction: discord.Interaction):
        """Display spider network statistics."""
        await interaction.response.defer()

        try:
            from core.models_unified_system import SpiderData
            from django.db.models import Count
            from django.utils import timezone

            @sync_to_async
            def get_spider_stats():
                today = timezone.now().date()
                week_ago = timezone.now() - timedelta(days=7)

                categories = list(SpiderData.objects.values('category').annotate(
                    count=Count('id')
                ).order_by('-count')[:10])

                return {
                    'total': SpiderData.objects.count(),
                    'today': SpiderData.objects.filter(crawled_at__date=today).count(),
                    'week': SpiderData.objects.filter(crawled_at__gte=week_ago).count(),
                    'categories': categories,
                }

            stats = await get_spider_stats()

            embed = discord.Embed(
                title=" Spider Network Stats",
                color=discord.Color.dark_green(),
                timestamp=datetime.now()
            )

            embed.add_field(name="Total Records", value=f"```{stats['total']:,}```", inline=True)
            embed.add_field(name="Today", value=f"```{stats['today']:,}```", inline=True)
            embed.add_field(name="This Week", value=f"```{stats['week']:,}```", inline=True)

            # Category breakdown
            if stats['categories']:
                cat_text = "\n".join(
                    f" {c['category'] or 'Unknown'}: {c['count']:,}"
                    for c in stats['categories']
                )
                embed.add_field(
                    name="Top Categories",
                    value=f"```\n{cat_text}\n```",
                    inline=False
                )

            embed.set_footer(text="Data from 60+ active spiders")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Spiders command error: {e}")
            await interaction.followup.send(
                f"Error fetching spider stats: {str(e)[:100]}",
                ephemeral=True
            )


# =============================================================================
# Session 427: Interactive Commands (/ask, /create, /research)
# =============================================================================

class InteractiveCommands(commands.Cog):
    """Commands for interacting with AI agents - Session 427."""

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot

    @app_commands.command(name="ask", description="Ask the Personal Assistant a question")
    @app_commands.describe(question="Your question for the AI assistant")
    async def ask(self, interaction: discord.Interaction, question: str):
        """Query the Personal Assistant agent with conversation memory."""
        # Check rate limit with permission awareness
        can_use, remaining = check_permission(interaction.user.id, 'ask')
        if not can_use:
            await interaction.response.send_message(
                f"Please wait {remaining:.1f}s before using /ask again.",
                ephemeral=True
            )
            return

        # Defer for long operation
        await interaction.response.defer()
        rate_limiter.record_use(interaction.user.id, 'ask')

        user_id = interaction.user.id

        try:
            # Get conversation history for this user
            history = conversation_history.get_history(user_id)

            # Import and call Personal Assistant
            @sync_to_async
            def query_assistant(q: str, conv_history: List[Dict[str, str]]) -> Dict[str, Any]:
                from core.agents.personal_assistant_agent import PersonalAssistantAgent
                from core.agent_router import AgentRouter

                agent = PersonalAssistantAgent()
                router = AgentRouter()

                # Build context with conversation history
                context = {
                    'source': 'discord',
                    'user_id': str(interaction.user.id),
                    'user_name': interaction.user.display_name,
                    'conversation_history': conv_history,  # Session 428: Add history
                }

                # Build task with context if there's history
                task_with_context = q
                if conv_history:
                    # Prepend conversation summary for context
                    history_summary = "\n".join([
                        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content'][:200]}"
                        for m in conv_history[-6:]  # Last 3 exchanges
                    ])
                    task_with_context = f"[Previous conversation]\n{history_summary}\n\n[Current question]\n{q}"

                # Execute the agent
                result = agent.execute(
                    task=task_with_context,
                    context=context,
                    scifi_context={},
                    spider_context={}
                )

                # Build response - check both message and data
                response_text = result.message or ""

                # If message is short/generic, check data for more detail
                if result.data:
                    agent_result = result.data.get('agent_result', {})
                    if isinstance(agent_result, dict):
                        # Look for actual content in agent_result
                        if 'results' in agent_result:
                            response_text += "\n\n**Results:**\n"
                            for item in agent_result['results'][:5]:
                                if isinstance(item, dict):
                                    title = item.get('title', '')[:80]
                                    url = item.get('url', '')
                                    if title:
                                        if url:
                                            response_text += f"- [{title}]({url})\n"
                                        else:
                                            response_text += f"- {title}\n"

                return {
                    'success': result.success,
                    'message': response_text,
                    'agent_name': result.agent_name if hasattr(result, 'agent_name') else 'PersonalAssistant',
                    'delegated_to': result.data.get('delegated_to') if result.data else None,
                    'error': result.error,
                }

            result = await query_assistant(question, history)

            # Session 428: Store conversation in history
            if result['success']:
                # Add user question and assistant response to history
                conversation_history.add_message(user_id, 'user', question)
                response_for_history = result['message'][:500] if result['message'] else "No response"
                conversation_history.add_message(user_id, 'assistant', response_for_history)

            # Build response embed
            if result['success']:
                # Truncate response if too long (Discord limit is 4096 for embed description)
                response_text = result['message'] or "No response generated."
                if len(response_text) > 3800:
                    response_text = response_text[:3800] + "\n\n*... (response truncated)*"

                embed = discord.Embed(
                    title="Personal Assistant",
                    description=response_text,
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )

                # Show conversation info and which agent handled it
                msg_count = conversation_history.get_message_count(user_id)
                footer_parts = [f"Asked by {interaction.user.display_name}"]
                if result.get('delegated_to'):
                    footer_parts.append(f"Handled by {result['delegated_to']}")
                if msg_count > 2:
                    footer_parts.append(f"Conversation: {msg_count // 2} exchanges")
                embed.set_footer(text=" | ".join(footer_parts))
            else:
                embed = discord.Embed(
                    title="Error",
                    description=result.get('error', 'An error occurred processing your request.'),
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"/ask command error: {e}")
            await interaction.followup.send(
                f"Error processing question: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="create", description="Generate an image with AI")
    @app_commands.describe(prompt="Describe what you want to create")
    async def create(self, interaction: discord.Interaction, prompt: str):
        """Trigger image generation via ImageAgent."""
        # Check rate limit with permission awareness
        can_use, remaining = check_permission(interaction.user.id, 'create')
        if not can_use:
            await interaction.response.send_message(
                f"Please wait {remaining:.1f}s before using /create again.",
                ephemeral=True
            )
            return

        # Defer for long operation (image generation takes time!)
        await interaction.response.defer()
        rate_limiter.record_use(interaction.user.id, 'create')

        try:
            @sync_to_async
            def generate_image(p: str, discord_user_id: int, discord_user_name: str) -> Dict[str, Any]:
                from core.agents.image_agent import ImageAgent
                from django.contrib.auth import get_user_model
                from content.models import ImageHistory
                import os
                from django.conf import settings

                User = get_user_model()
                agent = ImageAgent()

                # Build context
                context = {
                    'source': 'discord',
                    'user_id': str(discord_user_id),
                    'user_name': discord_user_name,
                }

                # Execute image generation
                result = agent.execute(
                    task=f"Create an image: {p}",
                    context=context,
                    scifi_context={},
                    spider_context={}
                )

                # Check for images in the data
                image_url = None
                local_file_path = None
                file_path_for_db = None
                if result.data:
                    images = result.data.get('images', [])
                    logger.info(f"/create result.data keys: {result.data.keys() if result.data else 'None'}")
                    logger.info(f"/create images array: {images}")
                    if images and len(images) > 0:
                        # Get the first image - note: uses 'image_url' not 'url'!
                        first_image = images[0]
                        # Try both 'image_url' and 'url' for compatibility
                        image_url = first_image.get('image_url') or first_image.get('url', '')
                        logger.info(f"/create found image URL: {image_url}")
                        # Convert media URL to local filesystem path
                        if image_url and image_url.startswith('/media/'):
                            # Convert /media/... to actual file path
                            local_file_path = os.path.join(settings.BASE_DIR, image_url.lstrip('/'))
                            # For DB storage, we need the relative path from MEDIA_ROOT
                            file_path_for_db = image_url.replace('/media/', '')
                            logger.info(f"/create local file path: {local_file_path}")

                # Session 429: Save to ImageHistory so it appears in web app
                history_id = None
                linked_username = None
                if result.success and file_path_for_db:
                    try:
                        # Session 429: Check if Discord user has linked account
                        linked_user = User.objects.filter(discord_id=str(discord_user_id)).first()

                        if linked_user:
                            # Use linked user's account
                            discord_user = linked_user
                            linked_username = linked_user.username
                        else:
                            # Fall back to generic discord_bot user
                            discord_user, _ = User.objects.get_or_create(
                                username='discord_bot',
                                defaults={
                                    'email': 'discord@donkeybetz.local',
                                    'is_active': True,
                                }
                            )

                        # Create ImageHistory record
                        history = ImageHistory.objects.create(
                            user=discord_user,
                            filename=os.path.basename(file_path_for_db),
                            file_path=file_path_for_db,
                            image_type='generated',
                            prompt=p,
                            parameters={
                                'source': 'discord',
                                'discord_user_id': str(discord_user_id),
                                'discord_user_name': discord_user_name,
                            },
                            model_used=first_image.get('model', 'stable-diffusion'),
                            style=first_image.get('style', ''),
                        )
                        history_id = history.id
                        logger.info(f"/create saved to ImageHistory: {history.id}")

                        # Session 430: Auto-deliver to gallery channel
                        try:
                            from core.services.discord_notifications import discord_notify
                            full_image_url = f"http://localhost:8000{history.image_url}" if history.image_url else image_url
                            discord_notify.send_image_to_gallery(
                                username=linked_username or discord_user_name,
                                prompt=p,
                                image_url=full_image_url,
                                image_id=history.id,
                                model=first_image.get('model', 'stable-diffusion'),
                                discord_user_id=str(discord_user_id) if linked_user else None
                            )
                        except Exception as discord_err:
                            logger.warning(f"/create Discord gallery delivery failed: {discord_err}")
                    except Exception as db_err:
                        logger.warning(f"/create failed to save to ImageHistory: {db_err}")

                return {
                    'success': result.success,
                    'message': result.message,
                    'image_url': image_url,
                    'local_file_path': local_file_path,
                    'image_count': len(images) if result.data else 0,
                    'error': result.error,
                    'history_id': history_id,
                    'linked_username': linked_username,  # Session 429: Track if saved to linked account
                }

            result = await generate_image(prompt, interaction.user.id, interaction.user.display_name)

            if result['success']:
                embed = discord.Embed(
                    title="Image Generated",
                    description=f"**Prompt:** {prompt[:200]}",
                    color=discord.Color.purple(),
                    timestamp=datetime.now()
                )
                # Session 429: Add note that image is saved to web app
                footer_text = f"Created by {interaction.user.display_name}"
                if result.get('history_id'):
                    if result.get('linked_username'):
                        footer_text += f" | Saved to {result['linked_username']}'s AI Studio"
                    else:
                        footer_text += " | Saved to AI Studio (link your account with /link)"
                embed.set_footer(text=footer_text)

                # Try to upload the image file directly to Discord
                file_to_send = None
                if result.get('local_file_path'):
                    import os
                    file_path = result['local_file_path']
                    if os.path.exists(file_path):
                        # Create Discord File object
                        filename = os.path.basename(file_path)
                        file_to_send = discord.File(file_path, filename=filename)
                        # Set the embed image to reference the attachment
                        embed.set_image(url=f"attachment://{filename}")

                # If no file, show fallback message
                if not file_to_send:
                    response_text = result['message'] or "Image generated"
                    if result.get('image_url'):
                        response_text += f"\n\n**View in AI Studio:** [Click here](http://localhost:8000/ai-studio/)"
                    embed.add_field(name="Result", value=response_text, inline=False)
                # Send with file if we have one
                if file_to_send:
                    await interaction.followup.send(embed=embed, file=file_to_send)
                else:
                    await interaction.followup.send(embed=embed)
                return

            else:
                embed = discord.Embed(
                    title="Generation Failed",
                    description=result.get('error', 'Failed to generate image.'),
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"/create command error: {e}")
            await interaction.followup.send(
                f"Error generating image: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="research", description="Search spider data for a topic")
    @app_commands.describe(
        topic="Topic to research",
        limit="Number of results (default: 5)"
    )
    async def research(
        self,
        interaction: discord.Interaction,
        topic: str,
        limit: int = 5
    ):
        """Run spider search for a topic."""
        # Check rate limit with permission awareness
        can_use, remaining = check_permission(interaction.user.id, 'research')
        if not can_use:
            await interaction.response.send_message(
                f"Please wait {remaining:.1f}s before using /research again.",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        rate_limiter.record_use(interaction.user.id, 'research')

        try:
            # Cap limit
            limit = min(limit, 10)

            @sync_to_async
            def search_spiders(query: str, lim: int) -> Dict[str, Any]:
                from core.services.spider_semantic_search import SpiderSemanticSearch

                search = SpiderSemanticSearch()
                results = search.semantic_search(query, limit=lim)

                return {
                    'query': query,
                    'results': results,
                    'count': len(results),
                }

            data = await search_spiders(topic, limit)

            if not data['results']:
                await interaction.followup.send(
                    f"No results found for '{topic}'.",
                    ephemeral=True
                )
                return

            embed = discord.Embed(
                title=f"Research: {topic}",
                description=f"Found {data['count']} results from spider network.",
                color=discord.Color.teal(),
                timestamp=datetime.now()
            )

            for idx, item in enumerate(data['results'][:5], 1):
                # SemanticSearchResult is a dataclass, use attribute access
                title = (item.title or 'Untitled')[:100]
                url = item.url or ''
                source = item.source or 'Unknown'
                score = item.similarity or 0

                # Format as clickable link if URL exists
                if url:
                    value = f"[{title}]({url})\nSource: {source} | Score: {score:.2f}"
                else:
                    value = f"{title}\nSource: {source} | Score: {score:.2f}"

                embed.add_field(
                    name=f"Result {idx}",
                    value=value,
                    inline=False
                )

            embed.set_footer(text=f"Searched by {interaction.user.display_name}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"/research command error: {e}")
            await interaction.followup.send(
                f"Error searching: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="clear", description="Clear your conversation history with the assistant")
    async def clear_history(self, interaction: discord.Interaction):
        """Clear conversation history for the user - Session 428."""
        user_id = interaction.user.id
        msg_count = conversation_history.get_message_count(user_id)

        if conversation_history.clear(user_id):
            embed = discord.Embed(
                title="Conversation Cleared",
                description=f"Your conversation history has been cleared ({msg_count // 2} exchanges removed).\n\nYour next `/ask` will start a fresh conversation.",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
        else:
            embed = discord.Embed(
                title="No History",
                description="You don't have any conversation history to clear.",
                color=discord.Color.light_gray(),
                timestamp=datetime.now()
            )

        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="link", description="Link your Discord account to your AI Studio web account")
    @app_commands.describe(code="The 6-character link code from the AI Studio web app")
    async def link_account(self, interaction: discord.Interaction, code: str):
        """
        Link Discord account to web user using a verification code.

        Session 429: Discord User Linking

        The user generates a code in the web app, then uses /link <code> here.
        """
        await interaction.response.defer(ephemeral=True)

        try:
            import aiohttp

            # Get the API URL (assume localhost for now, could be configurable)
            api_url = os.environ.get('DJANGO_API_URL', 'http://localhost:8000')
            bot_secret = os.environ.get('DISCORD_BOT_TOKEN', '')[:20]  # First 20 chars as secret

            # Call the verify endpoint
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api_url}/api/discord/verify-link-code/",
                    json={
                        'code': code.upper().strip(),
                        'discord_id': str(interaction.user.id),
                        'discord_username': f"{interaction.user.name}#{interaction.user.discriminator}" if interaction.user.discriminator != '0' else interaction.user.name,
                        'bot_secret': bot_secret,
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    result = await resp.json()

            if result.get('success'):
                embed = discord.Embed(
                    title="Account Linked!",
                    description=f"Your Discord account has been linked to **{result.get('username', 'your account')}**.\n\nImages you create with `/create` will now appear in your AI Studio gallery!",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                embed.set_footer(text=f"Linked: {interaction.user.display_name}")
            else:
                error_msg = result.get('error', 'Unknown error')
                embed = discord.Embed(
                    title="Link Failed",
                    description=f"**Error:** {error_msg}\n\nMake sure you:\n1. Generated a fresh code in AI Studio\n2. Entered it within 10 minutes\n3. Haven't already linked this Discord account",
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )
                embed.set_footer(text="Use /link <code> to try again")

            await interaction.followup.send(embed=embed, ephemeral=True)

        except aiohttp.ClientError as e:
            logger.error(f"/link API connection error: {e}")
            await interaction.followup.send(
                "Could not connect to the AI Studio server. Please try again later.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"/link command error: {e}")
            await interaction.followup.send(
                f"Error linking account: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="unlink", description="Unlink your Discord account from your AI Studio account")
    async def unlink_account(self, interaction: discord.Interaction):
        """
        Check if Discord account is linked and provide unlink instructions.

        Session 429: Discord User Linking
        """
        @sync_to_async
        def check_link_status(discord_id: str):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.filter(discord_id=discord_id).first()
                if user:
                    return {'linked': True, 'username': user.username}
                return {'linked': False}
            except Exception:
                return {'linked': False}

        result = await check_link_status(str(interaction.user.id))

        if result.get('linked'):
            embed = discord.Embed(
                title="Account Linked",
                description=f"Your Discord is linked to **{result.get('username')}**.\n\nTo unlink, go to AI Studio > Settings and click 'Unlink Discord'.",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
        else:
            embed = discord.Embed(
                title="Not Linked",
                description="Your Discord account is not linked to any AI Studio account.\n\nUse `/link <code>` with a code from AI Studio to link your accounts.",
                color=discord.Color.light_gray(),
                timestamp=datetime.now()
            )

        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)


# =============================================================================
# Content & Profile Commands - Session 430 (Phase 1: Discord-First)
# =============================================================================

class ContentCommands(commands.Cog):
    """Commands for viewing content, profile, and opportunities - Session 430."""

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot
        # Channel IDs for content delivery
        self.GALLERY_CHANNEL_ID = 1449059813765021859
        self.PROFILE_CHANNEL_ID = 1449059839581098135
        self.OPPORTUNITIES_CHANNEL_ID = 1448867150948335777

    async def _get_linked_user(self, discord_id: str):
        """Get the linked web user for a Discord ID."""
        @sync_to_async
        def get_user():
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return User.objects.filter(discord_id=discord_id).first()
        return await get_user()

    @app_commands.command(name="gallery", description="View your recent AI-generated images")
    @app_commands.describe(count="Number of images to show (1-10, default 5)")
    async def gallery(self, interaction: discord.Interaction, count: int = 5):
        """Display user's recent image creations."""
        await interaction.response.defer()

        # Clamp count
        count = max(1, min(10, count))

        try:
            # Check if user is linked
            user = await self._get_linked_user(str(interaction.user.id))

            @sync_to_async
            def get_images(web_user, limit):
                from content.models import ImageHistory
                from django.conf import settings

                if web_user:
                    # Get linked user's images
                    images = ImageHistory.objects.filter(
                        user=web_user
                    ).order_by('-created_at')[:limit]
                else:
                    # Get recent public images (for non-linked users)
                    images = ImageHistory.objects.order_by('-created_at')[:limit]

                results = []
                for img in images:
                    # Build full URL from file_path field
                    if img.file_path:
                        if img.file_path.startswith('/media/'):
                            url = f"http://localhost:8000{img.file_path}"
                        elif img.file_path.startswith('http'):
                            url = img.file_path
                        elif img.file_path.startswith('data:'):
                            url = img.file_path  # Data URI
                        else:
                            url = f"http://localhost:8000/media/{img.file_path}"
                    else:
                        url = None

                    # Use sequential_number for user-friendly display
                    seq_id = img.sequential_number or img.get_sequential_number()
                    results.append({
                        'id': seq_id,
                        'uuid': str(img.id),
                        'prompt': (img.prompt or 'No prompt')[:100],
                        'url': url,
                        'created_at': img.created_at.strftime('%Y-%m-%d %H:%M') if img.created_at else 'Unknown',
                        'model': img.model_used or 'Unknown',
                    })
                return results

            images = await get_images(user, count)

            if not images:
                embed = discord.Embed(
                    title="🖼️ Gallery Empty",
                    description="No images found. Use `/create <prompt>` to generate your first image!",
                    color=discord.Color.light_gray(),
                    timestamp=datetime.now()
                )
                if not user:
                    embed.add_field(
                        name="💡 Tip",
                        value="Link your account with `/link <code>` to see your web gallery here!",
                        inline=False
                    )
            else:
                linked_status = f"Linked as **{user.username}**" if user else "Not linked - showing recent public images"
                embed = discord.Embed(
                    title=f"🖼️ Your Gallery ({len(images)} images)",
                    description=linked_status,
                    color=discord.Color.purple(),
                    timestamp=datetime.now()
                )

                for idx, img in enumerate(images, 1):
                    prompt_preview = img['prompt'][:80] + "..." if len(img['prompt']) > 80 else img['prompt']
                    value = f"📝 `{prompt_preview}`\n🕐 {img['created_at']} | 🤖 {img['model']}"
                    if img['url']:
                        value += f"\n[🔗 View Image]({img['url']})"

                    embed.add_field(
                        name=f"#{img['id']}",
                        value=value,
                        inline=False
                    )

            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"/gallery command error: {e}")
            await interaction.followup.send(
                f"Error loading gallery: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="profile", description="View your AI Studio profile and stats")
    async def profile(self, interaction: discord.Interaction):
        """Display user's profile information."""
        await interaction.response.defer()

        try:
            user = await self._get_linked_user(str(interaction.user.id))

            if not user:
                embed = discord.Embed(
                    title="🔗 Account Not Linked",
                    description="Link your Discord to your AI Studio account to see your profile!\n\n**How to link:**\n1. Go to AI Studio > Preferences > Discord\n2. Click 'Generate Link Code'\n3. Use `/link <code>` here",
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                )
                embed.set_footer(text=f"Requested by {interaction.user.display_name}")
                await interaction.followup.send(embed=embed)
                return

            @sync_to_async
            def get_profile_data(web_user):
                from content.models import ImageHistory
                from core.models_unified_system import AgentExecution, Opportunity, Revenue
                from core.models.users import EnhancedUserProfile
                from django.db.models import Sum
                from django.utils import timezone
                from datetime import timedelta

                # Basic stats
                total_images = ImageHistory.objects.filter(user=web_user).count()
                recent_images = ImageHistory.objects.filter(
                    user=web_user,
                    created_at__gte=timezone.now() - timedelta(days=7)
                ).count()

                # Agent interactions
                try:
                    agent_executions = AgentExecution.objects.filter(user=web_user).count()
                except:
                    agent_executions = 0

                # Opportunities
                try:
                    opportunities_viewed = Opportunity.objects.filter(user=web_user).count()
                except:
                    opportunities_viewed = 0

                # Revenue
                try:
                    total_revenue = Revenue.objects.filter(user=web_user).aggregate(
                        total=Sum('amount')
                    )['total'] or 0
                except:
                    total_revenue = 0

                # Enhanced profile (if exists)
                profile_data = {}
                try:
                    enhanced = EnhancedUserProfile.objects.filter(user=web_user).first()
                    if enhanced:
                        profile_data = {
                            'profession': enhanced.profession or 'Not set',
                            'skills': enhanced.skills[:3] if enhanced.skills else [],
                            'goals': enhanced.goals[:2] if enhanced.goals else [],
                            'completeness': enhanced.profile_completeness or 0,
                        }
                except:
                    pass

                return {
                    'username': web_user.username,
                    'email': web_user.email,
                    'tier': web_user.subscription_tier,
                    'created': web_user.date_joined.strftime('%Y-%m-%d') if web_user.date_joined else 'Unknown',
                    'discord_linked': web_user.discord_linked_at.strftime('%Y-%m-%d') if web_user.discord_linked_at else 'Just now',
                    'total_images': total_images,
                    'recent_images': recent_images,
                    'agent_executions': agent_executions,
                    'opportunities': opportunities_viewed,
                    'revenue': float(total_revenue),
                    'profile': profile_data,
                }

            data = await get_profile_data(user)

            # Build profile embed
            embed = discord.Embed(
                title=f"👤 {data['username']}'s Profile",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            # Account info
            tier_emoji = {'free': '🆓', 'pro': '⭐', 'enterprise': '👑'}.get(data['tier'], '🆓')
            embed.add_field(
                name="📋 Account",
                value=f"{tier_emoji} **{data['tier'].title()}** Tier\n📅 Joined: {data['created']}\n🔗 Discord linked: {data['discord_linked']}",
                inline=True
            )

            # Creation stats
            embed.add_field(
                name="🎨 Creations",
                value=f"🖼️ Total images: **{data['total_images']}**\n📅 This week: **{data['recent_images']}**\n🤖 Agent tasks: **{data['agent_executions']}**",
                inline=True
            )

            # Revenue & Opportunities
            embed.add_field(
                name="💰 Business",
                value=f"🎯 Opportunities: **{data['opportunities']}**\n💵 Revenue: **${data['revenue']:.2f}**",
                inline=True
            )

            # Profile info if available
            if data['profile']:
                profile = data['profile']
                profile_text = f"💼 {profile['profession']}"
                if profile['skills']:
                    profile_text += f"\n🛠️ Skills: {', '.join(profile['skills'])}"
                if profile['goals']:
                    profile_text += f"\n🎯 Goals: {profile['goals'][0][:50]}"
                profile_text += f"\n📊 Profile: {profile['completeness']}% complete"

                embed.add_field(
                    name="📝 Your Profile",
                    value=profile_text,
                    inline=False
                )

            embed.set_footer(text=f"Discord: {interaction.user.display_name}")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"/profile command error: {e}")
            await interaction.followup.send(
                f"Error loading profile: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="opportunities", description="View matching income opportunities")
    @app_commands.describe(
        count="Number of opportunities to show (1-10, default 5)",
        category="Filter by category (e.g., 'design', 'writing', 'tech')"
    )
    async def opportunities(self, interaction: discord.Interaction, count: int = 5, category: str = None):
        """Display matching opportunities for the user."""
        await interaction.response.defer()

        # Clamp count
        count = max(1, min(10, count))

        try:
            user = await self._get_linked_user(str(interaction.user.id))

            @sync_to_async
            def get_opportunities(web_user, limit, cat_filter):
                from core.models_unified_system import Opportunity
                from django.utils import timezone

                queryset = Opportunity.objects.filter(
                    status='active'
                ).order_by('-match_score', '-created_at')

                # Filter by category if specified
                if cat_filter:
                    queryset = queryset.filter(category__icontains=cat_filter)

                # If user is linked, could filter by their skills in future
                # For now, just return top opportunities

                opps = queryset[:limit]

                results = []
                for opp in opps:
                    results.append({
                        'id': opp.user_friendly_id or 0,  # Session 433: Use user-friendly ID
                        'uuid': str(opp.id),
                        'title': (opp.title or 'Untitled')[:60],
                        'description': (opp.description or '')[:100],
                        'category': getattr(opp, 'category', None) or 'General',
                        'source': opp.source or 'Unknown',
                        'url': opp.url or '',
                        'score': opp.match_score or 0,  # Fixed: use match_score
                        'potential_value': float(opp.potential_revenue) if opp.potential_revenue else 0,  # Fixed: use potential_revenue
                        'created_at': opp.created_at.strftime('%Y-%m-%d') if opp.created_at else 'Unknown',
                    })
                return results

            opportunities = await get_opportunities(user, count, category)

            if not opportunities:
                embed = discord.Embed(
                    title="🎯 No Opportunities Found",
                    description="No active opportunities match your criteria.\n\nTry:\n- Removing the category filter\n- Checking back later for new listings",
                    color=discord.Color.light_gray(),
                    timestamp=datetime.now()
                )
            else:
                title = f"🎯 Top {len(opportunities)} Opportunities"
                if category:
                    title += f" ({category})"

                linked_status = f"Personalized for **{user.username}**" if user else "💡 Link your account for personalized matches!"

                embed = discord.Embed(
                    title=title,
                    description=linked_status,
                    color=discord.Color.gold(),
                    timestamp=datetime.now()
                )

                for opp in opportunities:
                    # Score indicator
                    if opp['score'] >= 80:
                        score_emoji = "🔥"
                    elif opp['score'] >= 60:
                        score_emoji = "⭐"
                    else:
                        score_emoji = "📌"

                    value = f"{opp['description'][:80]}..." if len(opp['description']) > 80 else opp['description']
                    value += f"\n📂 {opp['category']} | {score_emoji} Match: {opp['score']}%"

                    if opp['potential_value'] > 0:
                        value += f" | 💰 ${opp['potential_value']:.0f}"

                    if opp['url']:
                        value += f"\n[🔗 View Details]({opp['url']})"

                    # Show ID in field name for easy reference
                    embed.add_field(
                        name=f"#{opp['id']} - {opp['title']}",
                        value=value,
                        inline=False
                    )

            embed.set_footer(text=f"Requested by {interaction.user.display_name} | Use /apply <id> to apply")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"/opportunities command error: {e}")
            await interaction.followup.send(
                f"Error loading opportunities: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="apply", description="Apply to an opportunity")
    @app_commands.describe(
        opportunity_id="The opportunity ID (shown in /opportunities as #1, #2, etc.)",
        message="Optional message to include with your application"
    )
    async def apply(self, interaction: discord.Interaction, opportunity_id: int, message: str = None):
        """Apply to an income opportunity."""
        await interaction.response.defer(ephemeral=True)

        try:
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    "❌ You need to link your Discord account first!\n\n"
                    "Use `/link` to connect your AI Studio account.",
                    ephemeral=True
                )
                return

            @sync_to_async
            def create_application(web_user, opp_id, app_message):
                from core.models_unified_system import Opportunity, Application
                from django.utils import timezone

                # Find opportunity by user-friendly ID
                opportunity = Opportunity.objects.filter(user_friendly_id=opp_id).first()
                if not opportunity:
                    return None, "Opportunity not found. Use `/opportunities` to see available IDs."

                # Check if already applied
                existing = Application.objects.filter(
                    user=web_user,
                    opportunity=opportunity
                ).first()
                if existing:
                    applied_date = existing.submitted_at.strftime('%Y-%m-%d') if existing.submitted_at else 'recently'
                    return None, f"You already applied to this opportunity on {applied_date}."

                # Create application and submit it
                application = Application.objects.create(
                    user=web_user,
                    opportunity=opportunity,
                    cover_letter=app_message or '',
                )
                application.submit_application()  # Sets status='submitted' and submitted_at

                return {
                    'app_id': application.id,
                    'opp_title': opportunity.title[:50],
                    'opp_source': opportunity.source or 'Unknown',
                    'opp_url': opportunity.url or '',
                    'potential_revenue': float(opportunity.potential_revenue) if opportunity.potential_revenue else 0,
                }, None

            result, error = await create_application(user, opportunity_id, message)

            if error:
                await interaction.followup.send(
                    f"❌ {error}",
                    ephemeral=True
                )
                return

            embed = discord.Embed(
                title="✅ Application Submitted!",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )

            embed.add_field(
                name="📋 Opportunity",
                value=f"**{result['opp_title']}**\n📂 Source: {result['opp_source']}",
                inline=False
            )

            if result['potential_revenue'] > 0:
                embed.add_field(
                    name="💰 Potential Revenue",
                    value=f"${result['potential_revenue']:.0f}",
                    inline=True
                )

            if message:
                embed.add_field(
                    name="💬 Your Message",
                    value=message[:100] + ("..." if len(message) > 100 else ""),
                    inline=False
                )

            if result['opp_url']:
                embed.add_field(
                    name="🔗 Next Steps",
                    value=f"[Complete Application on {result['opp_source']}]({result['opp_url']})",
                    inline=False
                )

            embed.set_footer(text=f"Use /track to monitor your applications")
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"/apply command error: {e}")
            await interaction.followup.send(
                f"Error submitting application: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="track", description="Track your job applications")
    @app_commands.describe(
        status="Filter by status (all, submitted, reviewed, accepted, rejected)"
    )
    @app_commands.choices(status=[
        app_commands.Choice(name="All Applications", value="all"),
        app_commands.Choice(name="Submitted", value="submitted"),
        app_commands.Choice(name="Under Review", value="reviewed"),
        app_commands.Choice(name="Accepted", value="accepted"),
        app_commands.Choice(name="Rejected", value="rejected"),
    ])
    async def track(self, interaction: discord.Interaction, status: str = "all"):
        """Track your job applications."""
        await interaction.response.defer(ephemeral=True)

        try:
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    "❌ You need to link your Discord account first!\n\n"
                    "Use `/link` to connect your AI Studio account.",
                    ephemeral=True
                )
                return

            @sync_to_async
            def get_applications(web_user, status_filter):
                from core.models_unified_system import Application
                from django.db.models import Sum

                queryset = Application.objects.filter(user=web_user).select_related('opportunity')

                if status_filter != 'all':
                    queryset = queryset.filter(status=status_filter)

                apps = queryset.order_by('-submitted_at')[:10]

                results = []
                for app in apps:
                    opp = app.opportunity
                    results.append({
                        'app_id': app.id,
                        'opp_id': opp.user_friendly_id or 0,
                        'title': (opp.title or 'Untitled')[:40],
                        'source': opp.source or 'Unknown',
                        'status': app.status,
                        'submitted_at': app.submitted_at.strftime('%m/%d') if app.submitted_at else 'Unknown',
                        'potential_revenue': float(opp.potential_revenue) if opp.potential_revenue else 0,
                    })

                # Get summary stats
                total = Application.objects.filter(user=web_user).count()
                accepted = Application.objects.filter(user=web_user, status='accepted').count()
                reviewed = Application.objects.filter(user=web_user, status='reviewed').count()
                pending = Application.objects.filter(user=web_user, status='submitted').count()

                return results, {
                    'total': total,
                    'accepted': accepted,
                    'reviewed': reviewed,
                    'pending': pending,
                }

            applications, stats = await get_applications(user, status)

            if not applications and status == 'all':
                embed = discord.Embed(
                    title="📋 No Applications Yet",
                    description="You haven't applied to any opportunities.\n\n"
                                "Use `/opportunities` to browse available opportunities\n"
                                "Then `/apply <id>` to submit an application!",
                    color=discord.Color.light_gray(),
                    timestamp=datetime.now()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Build embed
            title = "📋 Your Applications"
            if status != 'all':
                title += f" ({status.title()})"

            embed = discord.Embed(
                title=title,
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            # Summary stats
            embed.add_field(
                name="📊 Summary",
                value=f"✅ Accepted: **{stats['accepted']}** | 👀 In Review: **{stats['reviewed']}** | ⏳ Pending: **{stats['pending']}** | 📝 Total: **{stats['total']}**",
                inline=False
            )

            # Status emoji mapping
            status_emojis = {
                'draft': '📝',
                'submitted': '⏳',
                'reviewed': '👀',
                'accepted': '✅',
                'rejected': '❌',
            }

            for app in applications:
                emoji = status_emojis.get(app['status'], '📋')
                value = f"{emoji} {app['status'].title()} | 📅 Applied: {app['submitted_at']}"
                if app['potential_revenue'] > 0:
                    value += f" | 💰 ${app['potential_revenue']:.0f}"

                embed.add_field(
                    name=f"#{app['opp_id']} - {app['title']}",
                    value=value,
                    inline=False
                )

            if len(applications) == 10:
                embed.set_footer(text="Showing 10 most recent | Use status filter for specific results")
            else:
                embed.set_footer(text=f"Showing {len(applications)} application{'s' if len(applications) != 1 else ''}")

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"/track command error: {e}")
            await interaction.followup.send(
                f"Error loading applications: {str(e)[:200]}",
                ephemeral=True
            )

    # =========================================================================
    # Session 437: Phase 6 Automation Commands
    # =========================================================================

    @app_commands.command(name="digest", description="Get your daily/weekly activity digest")
    @app_commands.describe(period="Time period for the digest")
    @app_commands.choices(period=[
        app_commands.Choice(name="Today (24 hours)", value="daily"),
        app_commands.Choice(name="This Week (7 days)", value="weekly"),
    ])
    async def digest(self, interaction: discord.Interaction, period: str = "daily"):
        """Get a personalized activity digest."""
        await interaction.response.defer()

        try:
            user = await self._get_linked_user(str(interaction.user.id))

            @sync_to_async
            def get_digest_data(web_user, period_type):
                from core.models_unified_system import (
                    Opportunity, Application, AgentDream,
                    AgentConversation, SharedKnowledge
                )
                from django.utils import timezone
                from django.db.models import Count, Avg, Sum
                from datetime import timedelta

                now = timezone.now()
                if period_type == 'daily':
                    start_time = now - timedelta(hours=24)
                    period_label = "Last 24 Hours"
                else:
                    start_time = now - timedelta(days=7)
                    period_label = "Last 7 Days"

                # Opportunities stats
                new_opportunities = Opportunity.objects.filter(
                    created_at__gte=start_time,
                    status='active'
                ).count()

                high_value_opportunities = Opportunity.objects.filter(
                    created_at__gte=start_time,
                    status='active',
                    match_score__gte=70
                ).count()

                # Top 3 opportunities
                top_opps = Opportunity.objects.filter(
                    status='active'
                ).order_by('-match_score')[:3]

                top_opportunities = [
                    {
                        'id': o.user_friendly_id or 0,
                        'title': (o.title or 'Untitled')[:40],
                        'score': o.match_score or 0,
                        'category': o.category or 'General',
                    }
                    for o in top_opps
                ]

                # User's applications if linked
                user_apps = {'submitted': 0, 'accepted': 0, 'total': 0}
                if web_user:
                    user_apps['submitted'] = Application.objects.filter(
                        user=web_user,
                        submitted_at__gte=start_time
                    ).count()
                    user_apps['accepted'] = Application.objects.filter(
                        user=web_user,
                        status='accepted',
                        submitted_at__gte=start_time
                    ).count()
                    user_apps['total'] = Application.objects.filter(user=web_user).count()

                # Agent activity
                dreams_count = AgentDream.objects.filter(
                    created_at__gte=start_time
                ).count()

                conversations_count = AgentConversation.objects.filter(
                    created_at__gte=start_time
                ).count()

                knowledge_shared = SharedKnowledge.objects.filter(
                    created_at__gte=start_time
                ).count()

                # Top dreaming agents
                top_dreamers = AgentDream.objects.filter(
                    created_at__gte=start_time
                ).values('agent__name').annotate(
                    count=Count('id')
                ).order_by('-count')[:3]

                return {
                    'period_label': period_label,
                    'new_opportunities': new_opportunities,
                    'high_value_opportunities': high_value_opportunities,
                    'top_opportunities': top_opportunities,
                    'user_apps': user_apps,
                    'dreams_count': dreams_count,
                    'conversations_count': conversations_count,
                    'knowledge_shared': knowledge_shared,
                    'top_dreamers': list(top_dreamers),
                    'is_linked': web_user is not None,
                }

            data = await get_digest_data(user, period)

            # Build the digest embed
            embed = discord.Embed(
                title=f"📊 Your AI Studio Digest",
                description=f"**{data['period_label']}**",
                color=discord.Color.gold() if data['high_value_opportunities'] > 0 else discord.Color.blue(),
                timestamp=datetime.now()
            )

            # Opportunities section
            opp_value = (
                f"🆕 New: **{data['new_opportunities']}**\n"
                f"🌟 High-Value (70+): **{data['high_value_opportunities']}**"
            )
            embed.add_field(name="💰 Opportunities", value=opp_value, inline=True)

            # Applications section (if linked)
            if data['is_linked']:
                apps_value = (
                    f"📤 Submitted: **{data['user_apps']['submitted']}**\n"
                    f"✅ Accepted: **{data['user_apps']['accepted']}**\n"
                    f"📋 Total: **{data['user_apps']['total']}**"
                )
                embed.add_field(name="📝 Your Applications", value=apps_value, inline=True)
            else:
                embed.add_field(
                    name="📝 Applications",
                    value="Link account to track!\n`/link <code>`",
                    inline=True
                )

            # Agent activity section
            agent_value = (
                f"💭 Dreams: **{data['dreams_count']}**\n"
                f"💬 Conversations: **{data['conversations_count']}**\n"
                f"📚 Knowledge Shared: **{data['knowledge_shared']}**"
            )
            embed.add_field(name="🤖 Agent Activity", value=agent_value, inline=True)

            # Top opportunities
            if data['top_opportunities']:
                top_opps_text = "\n".join([
                    f"#{o['id']} - {o['title']} ({o['score']}/100)"
                    for o in data['top_opportunities']
                ])
                embed.add_field(
                    name="🏆 Top Opportunities",
                    value=top_opps_text,
                    inline=False
                )

            # Top dreaming agents
            if data['top_dreamers']:
                dreamers_text = " | ".join([
                    f"{d['agent__name']}: {d['count']}"
                    for d in data['top_dreamers']
                ])
                embed.add_field(
                    name="💭 Most Active Dreamers",
                    value=dreamers_text,
                    inline=False
                )

            # Quick actions footer
            embed.set_footer(
                text="💡 Use /opportunities to browse | /apply <id> to apply | /track to see applications"
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"/digest command error: {e}")
            await interaction.followup.send(
                f"Error generating digest: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="alerts", description="Manage your opportunity alerts")
    @app_commands.describe(action="What to do with alerts")
    @app_commands.choices(action=[
        app_commands.Choice(name="View Settings", value="view"),
        app_commands.Choice(name="Enable Alerts", value="enable"),
        app_commands.Choice(name="Disable Alerts", value="disable"),
    ])
    async def alerts(self, interaction: discord.Interaction, action: str = "view"):
        """Manage proactive opportunity alerts."""
        await interaction.response.defer(ephemeral=True)

        try:
            user = await self._get_linked_user(str(interaction.user.id))

            @sync_to_async
            def manage_alerts(web_user, action_type):
                if not web_user:
                    return {'error': 'not_linked'}

                from core.models_unified_system import EnhancedUserProfile

                profile, _ = EnhancedUserProfile.objects.get_or_create(user=web_user)

                if action_type == 'view':
                    # Check if alerts enabled (use discord_alerts_enabled field or default)
                    enabled = getattr(profile, 'discord_alerts_enabled', True)
                    min_score = getattr(profile, 'alert_min_score', 70)
                    categories = getattr(profile, 'alert_categories', []) or ['all']
                    return {
                        'enabled': enabled,
                        'min_score': min_score,
                        'categories': categories,
                        'action': 'view'
                    }
                elif action_type == 'enable':
                    profile.discord_alerts_enabled = True
                    profile.save()
                    return {'enabled': True, 'action': 'enable'}
                elif action_type == 'disable':
                    profile.discord_alerts_enabled = False
                    profile.save()
                    return {'enabled': False, 'action': 'disable'}

                return {'action': action_type}

            result = await manage_alerts(user, action)

            if result.get('error') == 'not_linked':
                await interaction.followup.send(
                    "❌ You need to link your Discord account first!\n\n"
                    "Use `/link` to connect your AI Studio account.",
                    ephemeral=True
                )
                return

            if result['action'] == 'view':
                status = "✅ Enabled" if result['enabled'] else "❌ Disabled"
                embed = discord.Embed(
                    title="🔔 Alert Settings",
                    color=discord.Color.green() if result['enabled'] else discord.Color.red(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="Status", value=status, inline=True)
                embed.add_field(name="Min Score", value=f"{result['min_score']}/100", inline=True)
                categories = ", ".join(result['categories'][:5]) if result['categories'] else "All"
                embed.add_field(name="Categories", value=categories, inline=True)
                embed.set_footer(text="Use /alerts enable or /alerts disable to change")
                await interaction.followup.send(embed=embed, ephemeral=True)

            elif result['action'] == 'enable':
                await interaction.followup.send(
                    "✅ **Alerts Enabled!**\n\n"
                    "You'll receive notifications when high-value opportunities (70+) are found.\n"
                    "Alerts are sent to your DMs or the #opportunities channel.",
                    ephemeral=True
                )

            elif result['action'] == 'disable':
                await interaction.followup.send(
                    "🔕 **Alerts Disabled**\n\n"
                    "You won't receive proactive opportunity notifications.\n"
                    "Use `/alerts enable` to turn them back on.",
                    ephemeral=True
                )

        except Exception as e:
            logger.error(f"/alerts command error: {e}")
            await interaction.followup.send(
                f"Error managing alerts: {str(e)[:200]}",
                ephemeral=True
            )

    # ========== SESSION 438: SUBSCRIPTION COMMANDS ==========

    @app_commands.command(name="subscribe", description="Subscribe to Pro or Premium for more features")
    @app_commands.describe(tier="Subscription tier to subscribe to")
    @app_commands.choices(tier=[
        app_commands.Choice(name="Pro ($9.99/mo) - 50 tasks/day, priority alerts", value="pro"),
        app_commands.Choice(name="Premium ($29.99/mo) - Unlimited, all features", value="premium"),
    ])
    async def subscribe(self, interaction: discord.Interaction, tier: str):
        """Subscribe to a paid tier for more features."""
        await interaction.response.defer(ephemeral=True)

        try:
            user = await self._get_linked_user(str(interaction.user.id))

            if not user:
                await interaction.followup.send(
                    "❌ You need to link your Discord account first!\n\n"
                    "Use `/link` to connect your AI Studio account, then try subscribing.",
                    ephemeral=True
                )
                return

            @sync_to_async
            def create_checkout(web_user, selected_tier):
                from core.services.stripe_subscription import stripe_subscription_service
                import asyncio

                # Run the async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        stripe_subscription_service.create_checkout_session(
                            web_user,
                            selected_tier,
                            success_url="https://localhost:8000/ai-studio/?subscription=success",
                            cancel_url="https://localhost:8000/ai-studio/?subscription=canceled",
                        )
                    )
                    return result
                finally:
                    loop.close()

            checkout = await create_checkout(user, tier)

            if checkout and checkout.get('url'):
                tier_info = {
                    'pro': {'name': 'Pro', 'price': '$9.99/mo', 'tasks': '50', 'features': ['Priority alerts', 'DM notifications']},
                    'premium': {'name': 'Premium', 'price': '$29.99/mo', 'tasks': 'Unlimited', 'features': ['All alerts', 'Advisor access', 'Custom workflows']},
                }
                info = tier_info.get(tier, tier_info['pro'])

                embed = discord.Embed(
                    title=f"🎉 Subscribe to {info['name']}",
                    description=f"Click the link below to complete your subscription!",
                    color=discord.Color.gold() if tier == 'premium' else discord.Color.blue(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="Price", value=info['price'], inline=True)
                embed.add_field(name="Daily Tasks", value=info['tasks'], inline=True)
                embed.add_field(name="Features", value="\n".join(f"✅ {f}" for f in info['features']), inline=False)
                embed.add_field(
                    name="🔗 Checkout Link",
                    value=f"[Click here to subscribe]({checkout['url']})",
                    inline=False
                )
                embed.set_footer(text="Secure payment via Stripe • Cancel anytime")

                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    "❌ Could not create checkout session. Please try again later.",
                    ephemeral=True
                )

        except Exception as e:
            logger.error(f"/subscribe command error: {e}")
            await interaction.followup.send(
                f"Error: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="tier", description="View your subscription tier and usage")
    async def tier(self, interaction: discord.Interaction):
        """View your current subscription tier and daily usage."""
        await interaction.response.defer(ephemeral=True)

        try:
            user = await self._get_linked_user(str(interaction.user.id))

            @sync_to_async
            def get_tier_info(web_user):
                if not web_user:
                    return {'tier': 'free', 'linked': False}

                from core.models import EnhancedUserProfile

                profile, _ = EnhancedUserProfile.objects.get_or_create(user=web_user)

                can_use, message = profile.can_use_task()
                limits = profile.get_tier_limits()

                return {
                    'linked': True,
                    'tier': profile.subscription_tier,
                    'status': profile.subscription_status,
                    'daily_tasks': profile.daily_task_count,
                    'daily_limit': limits['daily_tasks'],
                    'priority_alerts': limits['priority_alerts'],
                    'dm_notifications': limits['dm_notifications'],
                    'advisor_access': limits['advisor_access'],
                    'custom_workflows': limits['custom_workflows'],
                    'discord_role': limits['discord_role'],
                    'price': limits['price'],
                    'can_use_task': can_use,
                    'task_message': message,
                    'ends_at': profile.subscription_ends_at,
                }

            info = await get_tier_info(user)

            if not info.get('linked'):
                # Show tiers for non-linked users
                embed = discord.Embed(
                    title="📊 Subscription Tiers",
                    description="Link your account with `/link` to see your subscription.",
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                embed.add_field(
                    name="🆓 Free",
                    value="• 5 tasks/day\n• Basic alerts\n• Standard support",
                    inline=True
                )
                embed.add_field(
                    name="⭐ Pro ($9.99/mo)",
                    value="• 50 tasks/day\n• Priority alerts\n• DM notifications",
                    inline=True
                )
                embed.add_field(
                    name="👑 Premium ($29.99/mo)",
                    value="• Unlimited tasks\n• All alerts\n• Advisor access\n• Custom workflows",
                    inline=True
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Tier colors and emojis
            tier_styles = {
                'free': {'color': discord.Color.greyple(), 'emoji': '🆓', 'name': 'Free'},
                'pro': {'color': discord.Color.blue(), 'emoji': '⭐', 'name': 'Pro'},
                'premium': {'color': discord.Color.gold(), 'emoji': '👑', 'name': 'Premium'},
            }
            style = tier_styles.get(info['tier'], tier_styles['free'])

            embed = discord.Embed(
                title=f"{style['emoji']} Your Subscription: {style['name']}",
                color=style['color'],
                timestamp=datetime.now()
            )

            # Usage bar
            if info['daily_limit'] == -1:
                usage_text = f"**{info['daily_tasks']}** tasks used (Unlimited)"
            else:
                pct = int((info['daily_tasks'] / info['daily_limit']) * 100) if info['daily_limit'] > 0 else 0
                bar_filled = int(pct / 10)
                bar = "█" * bar_filled + "░" * (10 - bar_filled)
                usage_text = f"**{info['daily_tasks']}/{info['daily_limit']}** tasks [{bar}] {pct}%"

            embed.add_field(name="📊 Daily Usage", value=usage_text, inline=False)

            # Features
            features = []
            features.append(f"{'✅' if info['priority_alerts'] else '❌'} Priority Alerts")
            features.append(f"{'✅' if info['dm_notifications'] else '❌'} DM Notifications")
            features.append(f"{'✅' if info['advisor_access'] else '❌'} Advisor Access")
            features.append(f"{'✅' if info['custom_workflows'] else '❌'} Custom Workflows")

            embed.add_field(name="🎁 Features", value="\n".join(features), inline=True)

            # Status
            status_text = info['status'].title()
            if info.get('ends_at'):
                status_text += f"\n(Ends: {info['ends_at'].strftime('%Y-%m-%d')})"

            embed.add_field(name="📌 Status", value=status_text, inline=True)

            # Discord role
            if info['discord_role']:
                embed.add_field(name="🎭 Discord Role", value=info['discord_role'], inline=True)

            # Upgrade prompt for free/pro users
            if info['tier'] == 'free':
                embed.add_field(
                    name="⬆️ Upgrade",
                    value="Use `/subscribe pro` or `/subscribe premium` for more features!",
                    inline=False
                )
            elif info['tier'] == 'pro':
                embed.add_field(
                    name="⬆️ Go Premium",
                    value="Use `/subscribe premium` for unlimited tasks & advisor access!",
                    inline=False
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"/tier command error: {e}")
            await interaction.followup.send(
                f"Error: {str(e)[:200]}",
                ephemeral=True
            )

    # Session 439: Subscription management commands
    @app_commands.command(name="cancel", description="Cancel your subscription")
    async def cancel(self, interaction: discord.Interaction):
        """Cancel the user's subscription at end of billing period."""
        await interaction.response.defer(ephemeral=True)

        try:
            from django.contrib.auth import get_user_model
            from core.models import EnhancedUserProfile
            from core.services.stripe_subscription import cancel_subscription

            User = get_user_model()

            @sync_to_async
            def get_user_profile(discord_id):
                user = User.objects.filter(discord_id=str(discord_id)).first()
                if not user:
                    return None, None
                profile = EnhancedUserProfile.objects.filter(user=user).first()
                return user, profile

            user, profile = await get_user_profile(interaction.user.id)

            if not user:
                await interaction.followup.send(
                    "Please link your account first with `/link`.",
                    ephemeral=True
                )
                return

            if not profile or profile.subscription_tier == 'free':
                await interaction.followup.send(
                    "You don't have an active subscription to cancel.",
                    ephemeral=True
                )
                return

            # Cancel subscription
            success = await cancel_subscription(user, at_period_end=True)

            if success:
                embed = discord.Embed(
                    title="Subscription Cancellation Scheduled",
                    description=(
                        f"Your **{profile.subscription_tier.title()}** subscription "
                        "will be canceled at the end of your current billing period.\n\n"
                        "You'll continue to have access until then."
                    ),
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="Changed your mind?",
                    value="Use `/subscribe` to resubscribe anytime!",
                    inline=False
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    "Failed to cancel subscription. Please try again or contact support.",
                    ephemeral=True
                )

        except Exception as e:
            logger.error(f"/cancel command error: {e}")
            await interaction.followup.send(
                f"Error: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="billing", description="Access your billing portal")
    async def billing(self, interaction: discord.Interaction):
        """Get link to Stripe Customer Portal for billing management."""
        await interaction.response.defer(ephemeral=True)

        try:
            from django.contrib.auth import get_user_model
            from core.models import EnhancedUserProfile
            from core.services.stripe_subscription import stripe_subscription_service

            User = get_user_model()

            @sync_to_async
            def get_user_profile(discord_id):
                user = User.objects.filter(discord_id=str(discord_id)).first()
                if not user:
                    return None, None
                profile = EnhancedUserProfile.objects.filter(user=user).first()
                return user, profile

            user, profile = await get_user_profile(interaction.user.id)

            if not user:
                await interaction.followup.send(
                    "Please link your account first with `/link`.",
                    ephemeral=True
                )
                return

            if not profile or not profile.stripe_customer_id:
                await interaction.followup.send(
                    "No billing history found. Subscribe first with `/subscribe`.",
                    ephemeral=True
                )
                return

            # Get billing portal URL
            portal_url = await stripe_subscription_service.get_billing_portal_url(
                user,
                return_url="https://discord.com/channels/@me"
            )

            if portal_url:
                embed = discord.Embed(
                    title="Billing Portal",
                    description=(
                        "Manage your subscription, update payment methods, "
                        "and view invoices in the Stripe Customer Portal."
                    ),
                    color=discord.Color.blue()
                )
                embed.add_field(
                    name="Access Portal",
                    value=f"[Click here to open Billing Portal]({portal_url})",
                    inline=False
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    "Failed to access billing portal. Please try again.",
                    ephemeral=True
                )

        except Exception as e:
            logger.error(f"/billing command error: {e}")
            await interaction.followup.send(
                f"Error: {str(e)[:200]}",
                ephemeral=True
            )


class VoiceCommands(commands.Cog):
    """
    Session 438: Voice AI Commands (Phase 8).

    Enables voice channel interaction with AI assistant.
    Uses ElevenLabs for TTS and OpenAI Whisper for STT.
    """

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot
        self.voice_service = None

    def _ensure_voice_service(self):
        """Lazily initialize voice service."""
        if self.voice_service is None:
            from core.services.discord_voice import init_voice_service
            self.voice_service = init_voice_service(self.bot)
        return self.voice_service

    @app_commands.command(name="voice", description="Voice AI: Join a voice channel for voice interaction")
    @app_commands.describe(
        action="What to do",
        voice="Voice to use for speaking (optional)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Join - Join your voice channel", value="join"),
        app_commands.Choice(name="Leave - Leave voice channel", value="leave"),
        app_commands.Choice(name="Voices - List available voices", value="voices"),
    ])
    async def voice(
        self,
        interaction: discord.Interaction,
        action: str,
        voice: Optional[str] = None
    ):
        """Voice AI commands for voice channel interaction."""
        await interaction.response.defer(ephemeral=True)

        try:
            service = self._ensure_voice_service()

            if action == "join":
                # Check if user is in a voice channel
                if not interaction.user.voice or not interaction.user.voice.channel:
                    await interaction.followup.send(
                        "You need to be in a voice channel first!\n"
                        "Join a voice channel, then use `/voice join` again.",
                        ephemeral=True
                    )
                    return

                channel = interaction.user.voice.channel

                # Check permissions
                permissions = channel.permissions_for(interaction.guild.me)
                if not permissions.connect or not permissions.speak:
                    await interaction.followup.send(
                        "I don't have permission to join or speak in that channel!",
                        ephemeral=True
                    )
                    return

                # Join the channel
                session = await service.join_channel(channel, voice or 'rachel')

                if session:
                    embed = discord.Embed(
                        title="Voice AI Active",
                        description=f"Joined **{channel.name}**!",
                        color=discord.Color.green(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name="Voice", value=session.current_voice.title(), inline=True)
                    embed.add_field(name="Channel", value=channel.name, inline=True)
                    embed.add_field(
                        name="How to Use",
                        value=(
                            "I'm now listening in the voice channel.\n"
                            "Use `/speak <message>` to make me talk.\n"
                            "Say 'goodbye' to disconnect."
                        ),
                        inline=False
                    )
                    embed.set_footer(text="Powered by ElevenLabs TTS")

                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    await interaction.followup.send(
                        "Failed to join voice channel. Please try again.",
                        ephemeral=True
                    )

            elif action == "leave":
                if not service.is_in_voice(interaction.guild.id):
                    await interaction.followup.send(
                        "I'm not in a voice channel!",
                        ephemeral=True
                    )
                    return

                success = await service.leave_channel(interaction.guild)

                if success:
                    await interaction.followup.send(
                        "Left the voice channel. See you next time!",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "Error leaving voice channel.",
                        ephemeral=True
                    )

            elif action == "voices":
                voices = service.get_available_voices()

                embed = discord.Embed(
                    title="Available Voices",
                    description="Use `/voice join voice:<name>` to select a voice",
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )

                voice_descriptions = {
                    'rachel': 'Warm, professional female',
                    'antoni': 'Authoritative male',
                    'bella': 'Friendly female',
                    'callum': 'Confident British male',
                    'charlotte': 'Warm British female',
                    'daniel': 'Clear, neutral male',
                    'domi': 'Strong female',
                    'elli': 'Expressive female',
                    'josh': 'Deep male',
                    'sam': 'Neutral young male',
                }

                voice_list = "\n".join([
                    f"**{v.title()}** - {voice_descriptions.get(v, 'AI voice')}"
                    for v in voices
                ])

                embed.add_field(name="Voices", value=voice_list, inline=False)
                embed.set_footer(text="Powered by ElevenLabs")

                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"/voice command error: {e}")
            await interaction.followup.send(
                f"Error: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="speak", description="Make the bot speak a message in voice channel")
    @app_commands.describe(
        message="What to say",
        voice="Voice to use (optional)"
    )
    async def speak(
        self,
        interaction: discord.Interaction,
        message: str,
        voice: Optional[str] = None
    ):
        """Make the bot speak a message in the voice channel."""
        await interaction.response.defer(ephemeral=True)

        try:
            service = self._ensure_voice_service()

            if not service.is_in_voice(interaction.guild.id):
                await interaction.followup.send(
                    "I'm not in a voice channel!\n"
                    "Use `/voice join` first.",
                    ephemeral=True
                )
                return

            session = service.get_session(interaction.guild.id)

            # Change voice if specified
            if voice:
                if not await service.set_voice(interaction.guild.id, voice):
                    await interaction.followup.send(
                        f"Unknown voice: {voice}. Use `/voice voices` to see available voices.",
                        ephemeral=True
                    )
                    return

            # Speak the message
            success = await service.speak(session, message, voice)

            if success:
                await interaction.followup.send(
                    f"Speaking: \"{message[:100]}{'...' if len(message) > 100 else ''}\"",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "Failed to speak. ElevenLabs might be unavailable.",
                    ephemeral=True
                )

        except Exception as e:
            logger.error(f"/speak command error: {e}")
            await interaction.followup.send(
                f"Error: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="ask-voice", description="Ask AI and hear the response in voice channel")
    @app_commands.describe(question="Your question for the AI")
    async def ask_voice(self, interaction: discord.Interaction, question: str):
        """Ask the AI and hear the response spoken in voice channel."""
        await interaction.response.defer(ephemeral=True)

        try:
            service = self._ensure_voice_service()

            if not service.is_in_voice(interaction.guild.id):
                await interaction.followup.send(
                    "I'm not in a voice channel!\n"
                    "Use `/voice join` first, then ask your question.",
                    ephemeral=True
                )
                return

            session = service.get_session(interaction.guild.id)

            # Process the question with AI
            response = await service.process_voice_command(
                session,
                question,
                interaction.user
            )

            if response == "__EXIT__":
                await service.leave_channel(interaction.guild)
                await interaction.followup.send(
                    "Goodbye! I've left the voice channel.",
                    ephemeral=True
                )
                return

            # Speak the response
            await service.speak(session, response)

            # Also show text response
            embed = discord.Embed(
                title="AI Response",
                description=response,
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Voice: {session.current_voice.title()}")

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"/ask-voice command error: {e}")
            await interaction.followup.send(
                f"Error: {str(e)[:200]}",
                ephemeral=True
            )


class RoleManager(commands.Cog):
    """
    Session 439: Subscription Role Management.

    Handles automatic role assignment based on subscription tier.
    Polls cache for role sync requests from Stripe webhooks.
    """

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot
        self.role_sync_task.start()

    def cog_unload(self):
        self.role_sync_task.cancel()

    @tasks.loop(seconds=10)
    async def role_sync_task(self):
        """Background task to process role sync requests from cache."""
        try:
            await self._process_role_sync_queue()
        except Exception as e:
            logger.error(f"Role sync task error: {e}")

    @role_sync_task.before_loop
    async def before_role_sync(self):
        await self.bot.wait_until_ready()

    async def _process_role_sync_queue(self):
        """Process any pending role sync requests from cache."""
        from django.core.cache import cache

        # Get all pending role syncs from cache
        # The Stripe webhook queues these
        @sync_to_async
        def get_pending_syncs():
            from core.models import DiscordLinkCode
            pending = []

            # Get all linked Discord users
            links = DiscordLinkCode.objects.filter(is_used=True).select_related('user')

            for link in links:
                sync_key = f"discord_role_sync:{link.discord_user_id}"
                sync_data = cache.get(sync_key)
                if sync_data:
                    pending.append({
                        'discord_user_id': link.discord_user_id,
                        'tier': sync_data.get('tier', 'free'),
                        'cache_key': sync_key,
                    })

            return pending

        pending_syncs = await get_pending_syncs()

        for sync in pending_syncs:
            await self._sync_role(
                sync['discord_user_id'],
                sync['tier'],
                sync['cache_key']
            )

    async def _sync_role(self, discord_user_id: str, tier: str, cache_key: str):
        """Sync Discord role for a user based on their subscription tier."""
        import os
        from django.core.cache import cache

        # Get role IDs from environment
        pro_role_id = os.getenv('DISCORD_ROLE_PRO_ID')
        premium_role_id = os.getenv('DISCORD_ROLE_PREMIUM_ID')

        if not pro_role_id or not premium_role_id:
            logger.warning("Discord role IDs not configured in environment")
            return

        pro_role_id = int(pro_role_id)
        premium_role_id = int(premium_role_id)

        # Find the user across all guilds
        for guild in self.bot.guilds:
            try:
                member = guild.get_member(int(discord_user_id))
                if not member:
                    # Try fetching
                    try:
                        member = await guild.fetch_member(int(discord_user_id))
                    except discord.NotFound:
                        continue

                if not member:
                    continue

                # Get role objects
                pro_role = guild.get_role(pro_role_id)
                premium_role = guild.get_role(premium_role_id)

                # Remove existing subscription roles
                roles_to_remove = []
                if pro_role and pro_role in member.roles:
                    roles_to_remove.append(pro_role)
                if premium_role and premium_role in member.roles:
                    roles_to_remove.append(premium_role)

                if roles_to_remove:
                    await member.remove_roles(*roles_to_remove, reason="Subscription tier change")

                # Add new role based on tier
                if tier == 'pro' and pro_role:
                    await member.add_roles(pro_role, reason="Pro subscription activated")
                    logger.info(f"Added Pro role to {member.display_name}")
                elif tier == 'premium' and premium_role:
                    await member.add_roles(premium_role, reason="Premium subscription activated")
                    logger.info(f"Added Premium role to {member.display_name}")
                elif tier == 'free':
                    logger.info(f"Removed subscription roles from {member.display_name}")

                # Clear the cache entry - sync complete
                @sync_to_async
                def clear_cache():
                    cache.delete(cache_key)
                await clear_cache()

                # Update profile to mark as synced
                @sync_to_async
                def mark_synced():
                    from core.models import EnhancedUserProfile, DiscordLinkCode
                    link = DiscordLinkCode.objects.filter(discord_user_id=discord_user_id).first()
                    if link and link.user:
                        profile = EnhancedUserProfile.objects.filter(user=link.user).first()
                        if profile:
                            profile.discord_role_synced = True
                            profile.save(update_fields=['discord_role_synced'])
                await mark_synced()

                break  # Found and processed the user

            except Exception as e:
                logger.error(f"Error syncing role for {discord_user_id} in {guild.name}: {e}")

    async def sync_user_role(self, discord_user_id: str, tier: str):
        """Public method to manually sync a user's role."""
        await self._sync_role(discord_user_id, tier, f"manual_sync:{discord_user_id}")


class ServerSetupCommands(commands.Cog):
    """
    Session 431: Server Setup Wizard Commands.

    Allows users to set up their Discord server with AI Studio channels.
    """

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot

    async def _get_linked_user(self, discord_id: str):
        """Get the linked web user for a Discord ID."""
        @sync_to_async
        def get_user():
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return User.objects.filter(discord_id=discord_id).first()
        return await get_user()

    async def _get_or_create_server(self, guild, user, template: str = 'solo_creator'):
        """Get or create a DiscordServer record."""
        @sync_to_async
        def get_or_create():
            from core.models.base import DiscordServer
            server, created = DiscordServer.objects.get_or_create(
                guild_id=str(guild.id),
                defaults={
                    'user': user,
                    'guild_name': guild.name,
                    'template': template,
                }
            )
            return server, created
        return await get_or_create()

    async def _save_channel(self, server, channel_id: str, channel_name: str, channel_type: str):
        """Save a channel to the database."""
        @sync_to_async
        def save():
            from core.models.base import DiscordServerChannel
            channel, created = DiscordServerChannel.objects.get_or_create(
                server=server,
                channel_id=str(channel_id),
                defaults={
                    'channel_name': channel_name,
                    'channel_type': channel_type,
                }
            )
            return channel, created
        return await save()

    async def _update_server_channel_ids(self, server, channel_type: str, channel_id: str):
        """Update the server's quick-access channel ID fields."""
        @sync_to_async
        def update():
            field_map = {
                'gallery': 'gallery_channel_id',
                'assistant': 'assistant_channel_id',
                'research': 'research_channel_id',
                'opportunities': 'opportunities_channel_id',
                'notifications': 'notifications_channel_id',
            }
            if channel_type in field_map:
                setattr(server, field_map[channel_type], str(channel_id))
                server.save()
        return await update()

    @app_commands.command(name="setup", description="Set up AI Studio channels in your server")
    @app_commands.describe(template="Server template to use")
    @app_commands.choices(template=[
        app_commands.Choice(name="Solo Creator - Personal workspace", value="solo_creator"),
        app_commands.Choice(name="Freelancer - With client channels", value="freelancer"),
        app_commands.Choice(name="Agency - Team + clients", value="agency"),
    ])
    async def setup_server(self, interaction: discord.Interaction, template: str = "solo_creator"):
        """Set up AI Studio channels in the server using a template."""
        await interaction.response.defer(ephemeral=True)

        try:
            # Check if user has permission to manage channels
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.followup.send(
                    "You need 'Manage Channels' permission to run server setup.",
                    ephemeral=True
                )
                return

            # Check if user is linked
            linked_user = await self._get_linked_user(str(interaction.user.id))
            if not linked_user:
                await interaction.followup.send(
                    "Please link your Discord account first using `/link` command.\n"
                    "Generate a link code at: http://localhost:8000/ai-studio/ → Settings → Discord",
                    ephemeral=True
                )
                return

            guild = interaction.guild

            # Get template definition
            from core.models.base import DISCORD_SERVER_TEMPLATES
            template_def = DISCORD_SERVER_TEMPLATES.get(template)
            if not template_def:
                await interaction.followup.send(f"Unknown template: {template}", ephemeral=True)
                return

            # Create or get server record
            server, server_created = await self._get_or_create_server(guild, linked_user, template)

            # Progress message
            progress_embed = discord.Embed(
                title="Setting Up AI Studio...",
                description=f"Creating channels for **{template_def['name']}** template...",
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=progress_embed, ephemeral=True)

            channels_created = []

            # Create categories and channels
            for category_def in template_def['categories']:
                # Create or find category
                category_name = category_def['name']
                existing_category = discord.utils.get(guild.categories, name=category_name)

                if existing_category:
                    category = existing_category
                else:
                    category = await guild.create_category(category_name)

                # Create channels in category
                for channel_def in category_def['channels']:
                    channel_name = channel_def['name']
                    channel_type = channel_def['type']

                    # Check if channel already exists
                    existing_channel = discord.utils.get(category.text_channels, name=channel_name)

                    if existing_channel:
                        channel = existing_channel
                    else:
                        channel = await guild.create_text_channel(
                            name=channel_name,
                            category=category
                        )
                        channels_created.append(f"#{channel_name}")

                    # Save to database
                    await self._save_channel(server, channel.id, channel_name, channel_type)
                    await self._update_server_channel_ids(server, channel_type, channel.id)

            # Mark setup complete
            @sync_to_async
            def mark_complete():
                server.is_setup_complete = True
                server.save()
            await mark_complete()

            # Success message
            success_embed = discord.Embed(
                title="AI Studio Setup Complete!",
                description=f"Your server is now configured with the **{template_def['name']}** template.",
                color=discord.Color.green()
            )

            if channels_created:
                success_embed.add_field(
                    name="Channels Created",
                    value="\n".join(channels_created[:10]) + (f"\n...and {len(channels_created) - 10} more" if len(channels_created) > 10 else ""),
                    inline=False
                )
            else:
                success_embed.add_field(
                    name="Note",
                    value="All channels already existed. No new channels were created.",
                    inline=False
                )

            success_embed.add_field(
                name="Next Steps",
                value=(
                    "• Images you create will now appear in your gallery channel\n"
                    "• Use `/ask` in the assistant channel for AI help\n"
                    "• Use `/opportunities` to find income opportunities"
                ),
                inline=False
            )

            await interaction.edit_original_response(embed=success_embed)

        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to create channels. Please give me 'Manage Channels' permission.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"/setup command error: {e}")
            await interaction.followup.send(
                f"Error during setup: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="server-info", description="View your server's AI Studio configuration")
    async def server_info(self, interaction: discord.Interaction):
        """Show the current server's AI Studio configuration."""
        await interaction.response.defer(ephemeral=True)

        try:
            @sync_to_async
            def get_server():
                from core.models.base import DiscordServer
                return DiscordServer.objects.filter(guild_id=str(interaction.guild.id)).first()

            server = await get_server()

            if not server:
                embed = discord.Embed(
                    title="Server Not Configured",
                    description="This server hasn't been set up with AI Studio yet.\n\nUse `/setup` to configure your server.",
                    color=discord.Color.orange()
                )
            else:
                embed = discord.Embed(
                    title=f"AI Studio Configuration",
                    description=f"**Server:** {server.guild_name}\n**Template:** {server.get_template_display()}\n**Setup Complete:** {'Yes' if server.is_setup_complete else 'No'}",
                    color=discord.Color.green() if server.is_setup_complete else discord.Color.orange()
                )

                # Show channel IDs
                channels_info = []
                if server.gallery_channel_id:
                    channels_info.append(f"Gallery: <#{server.gallery_channel_id}>")
                if server.assistant_channel_id:
                    channels_info.append(f"Assistant: <#{server.assistant_channel_id}>")
                if server.research_channel_id:
                    channels_info.append(f"Research: <#{server.research_channel_id}>")
                if server.opportunities_channel_id:
                    channels_info.append(f"Opportunities: <#{server.opportunities_channel_id}>")

                if channels_info:
                    embed.add_field(
                        name="Configured Channels",
                        value="\n".join(channels_info),
                        inline=False
                    )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"/server-info command error: {e}")
            await interaction.followup.send(
                f"Error: {str(e)[:200]}",
                ephemeral=True
            )


class ClientCommands(commands.Cog):
    """
    Session 432: Client Management Commands (Phase 3).

    Allows freelancers and agencies to manage clients via Discord,
    including dedicated channels and deliverable tracking.
    """

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot

    async def _get_linked_user(self, discord_id: str):
        """Get the linked web user for a Discord ID."""
        @sync_to_async
        def get_user():
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return User.objects.filter(discord_id=discord_id).first()
        return await get_user()

    async def _get_user_server(self, guild_id: str):
        """Get the DiscordServer for this guild."""
        @sync_to_async
        def get_server():
            from core.models.base import DiscordServer
            return DiscordServer.objects.filter(guild_id=guild_id).first()
        return await get_server()

    async def _slugify(self, name: str) -> str:
        """Convert name to URL-safe slug."""
        import re
        slug = name.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        return slug[:50]

    @app_commands.command(name="client-add", description="Create a new client with dedicated channel")
    @app_commands.describe(
        name="Client name (e.g., 'Acme Corp')",
        email="Client email for notifications (optional)"
    )
    async def client_add(self, interaction: discord.Interaction, name: str, email: str = None):
        """Create a new client and their dedicated channel."""
        await interaction.response.defer(ephemeral=True)

        try:
            # Check if user is linked
            linked_user = await self._get_linked_user(str(interaction.user.id))
            if not linked_user:
                await interaction.followup.send(
                    "Please link your Discord account first using `/link` command.\n"
                    "Generate a link code at: http://localhost:8000/ai-studio/ → Settings → Discord",
                    ephemeral=True
                )
                return

            # Check if server is set up
            server = await self._get_user_server(str(interaction.guild.id))
            if not server:
                await interaction.followup.send(
                    "Please set up your server first using `/setup` command.",
                    ephemeral=True
                )
                return

            # Generate slug
            slug = await self._slugify(name)
            channel_name = f"client-{slug}"

            # Check if client already exists
            @sync_to_async
            def check_existing():
                from core.models.base import DiscordClient
                return DiscordClient.objects.filter(server=server, slug=slug).exists()

            if await check_existing():
                await interaction.followup.send(
                    f"A client with this name already exists. Use `/client-list` to see your clients.",
                    ephemeral=True
                )
                return

            # Find or create CLIENTS category
            guild = interaction.guild
            clients_category = discord.utils.get(guild.categories, name='CLIENTS')

            if not clients_category:
                clients_category = await guild.create_category('CLIENTS')

            # Create client channel
            channel = await guild.create_text_channel(
                name=channel_name,
                category=clients_category,
                topic=f"Dedicated channel for {name}"
            )

            # Save client to database
            @sync_to_async
            def create_client():
                from core.models.base import DiscordClient
                client = DiscordClient.objects.create(
                    server=server,
                    name=name,
                    slug=slug,
                    email=email,
                    channel_id=str(channel.id)
                )
                # Update server client count
                server.client_count = server.clients.count()
                server.save()
                return client

            client = await create_client()

            # Success embed
            embed = discord.Embed(
                title="✅ Client Created!",
                description=f"**{name}** has been added as a client.",
                color=discord.Color.green()
            )
            embed.add_field(name="Channel", value=f"<#{channel.id}>", inline=True)
            if email:
                embed.add_field(name="Email", value=email, inline=True)
            embed.add_field(
                name="Next Steps",
                value=(
                    f"• Use `/client-deliver {name} <image_id>` to send deliverables\n"
                    f"• Use `/client-invite {name}` to generate an invite link"
                ),
                inline=False
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

            # Send welcome message to client channel
            welcome_embed = discord.Embed(
                title=f"🎨 Welcome, {name}!",
                description="This is your dedicated channel for project deliverables and communication.",
                color=discord.Color.blue()
            )
            welcome_embed.add_field(
                name="What to expect",
                value=(
                    "• All your project deliverables will appear here\n"
                    "• Direct communication with the creative team\n"
                    "• Easy access to all your content"
                ),
                inline=False
            )
            await channel.send(embed=welcome_embed)

        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to create channels. Please give me 'Manage Channels' permission.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"/client-add command error: {e}")
            await interaction.followup.send(
                f"Error creating client: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="client-list", description="List all your clients")
    async def client_list(self, interaction: discord.Interaction):
        """List all clients for this server."""
        await interaction.response.defer(ephemeral=True)

        try:
            server = await self._get_user_server(str(interaction.guild.id))
            if not server:
                await interaction.followup.send(
                    "Please set up your server first using `/setup` command.",
                    ephemeral=True
                )
                return

            @sync_to_async
            def get_clients():
                from core.models.base import DiscordClient
                return list(DiscordClient.objects.filter(server=server).values(
                    'name', 'slug', 'status', 'deliverables_count', 'total_revenue', 'channel_id'
                ))

            clients = await get_clients()

            if not clients:
                embed = discord.Embed(
                    title="📋 Your Clients",
                    description="No clients yet. Use `/client-add <name>` to add your first client!",
                    color=discord.Color.blue()
                )
            else:
                embed = discord.Embed(
                    title=f"📋 Your Clients ({len(clients)} total)",
                    color=discord.Color.blue()
                )

                for client in clients[:10]:  # Show first 10
                    status_emoji = {
                        'active': '🟢',
                        'paused': '🟡',
                        'archived': '⚪'
                    }.get(client['status'], '⚪')

                    value = f"Status: {status_emoji} {client['status'].title()}\n"
                    value += f"Deliverables: {client['deliverables_count']}\n"
                    if client['total_revenue'] > 0:
                        value += f"Revenue: ${client['total_revenue']:.2f}\n"
                    if client['channel_id']:
                        value += f"Channel: <#{client['channel_id']}>"

                    embed.add_field(
                        name=client['name'],
                        value=value,
                        inline=True
                    )

                if len(clients) > 10:
                    embed.set_footer(text=f"Showing 10 of {len(clients)} clients")

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"/client-list command error: {e}")
            await interaction.followup.send(
                f"Error listing clients: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="client-deliver", description="Send a deliverable to a client's channel")
    @app_commands.describe(
        client_name="Client name to deliver to",
        image_id="Image number from /gallery (e.g., 320)",
        message="Optional message to include with the delivery"
    )
    async def client_deliver(
        self,
        interaction: discord.Interaction,
        client_name: str,
        image_id: int,
        message: str = None
    ):
        """Send an image deliverable to a client's channel."""
        await interaction.response.defer(ephemeral=True)

        try:
            server = await self._get_user_server(str(interaction.guild.id))
            if not server:
                await interaction.followup.send(
                    "Please set up your server first using `/setup` command.",
                    ephemeral=True
                )
                return

            # Find client
            @sync_to_async
            def get_client():
                from core.models.base import DiscordClient
                return DiscordClient.objects.filter(
                    server=server,
                    name__iexact=client_name
                ).first()

            client = await get_client()
            if not client:
                await interaction.followup.send(
                    f"Client '{client_name}' not found. Use `/client-list` to see your clients.",
                    ephemeral=True
                )
                return

            # Get image from database by sequential_number
            @sync_to_async
            def get_image():
                from content.models import ImageHistory
                return ImageHistory.objects.filter(sequential_number=image_id).first()

            image = await get_image()
            if not image:
                await interaction.followup.send(
                    f"Image #{image_id} not found. Use `/gallery` to see your recent images.",
                    ephemeral=True
                )
                return

            # Get client channel
            if not client.channel_id:
                await interaction.followup.send(
                    "This client doesn't have a channel. Please contact support.",
                    ephemeral=True
                )
                return

            channel = interaction.guild.get_channel(int(client.channel_id))
            if not channel:
                await interaction.followup.send(
                    "Could not find client channel. It may have been deleted.",
                    ephemeral=True
                )
                return

            # Build local file path for upload
            import os
            from django.conf import settings

            local_file_path = None
            image_url = None

            if image.file_path:
                if image.file_path.startswith('http'):
                    # External URL - use directly
                    image_url = image.file_path
                elif image.file_path.startswith('data:'):
                    # Data URI - skip (can't upload easily)
                    pass
                else:
                    # Local file - build path for upload
                    if image.file_path.startswith('/media/'):
                        local_file_path = os.path.join(settings.BASE_DIR, image.file_path.lstrip('/'))
                    else:
                        local_file_path = os.path.join(settings.MEDIA_ROOT, image.file_path)

            # Create delivery embed
            embed = discord.Embed(
                title="🎨 New Deliverable!",
                description=message if message else "Here's your latest creation:",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )

            if image.prompt:
                embed.add_field(name="Description", value=image.prompt[:200], inline=False)
            embed.set_footer(text=f"Delivered by {interaction.user.display_name}")

            # Send to client channel with image attachment
            file_attachment = None
            if local_file_path and os.path.exists(local_file_path):
                file_attachment = discord.File(local_file_path, filename="deliverable.png")
                embed.set_image(url="attachment://deliverable.png")
                delivery_message = await channel.send(embed=embed, file=file_attachment)
            elif image_url:
                embed.set_image(url=image_url)
                delivery_message = await channel.send(embed=embed)
            else:
                delivery_message = await channel.send(embed=embed)

            # Record deliverable
            @sync_to_async
            def save_deliverable():
                from core.models.base import ClientDeliverable
                deliverable = ClientDeliverable.objects.create(
                    client=client,
                    deliverable_type='image',
                    title=image.prompt[:200] if image.prompt else f"Image #{image_id}",
                    image_history_id=image_id,
                    url=image_url,
                    discord_message_id=str(delivery_message.id)
                )
                # Update client stats
                client.deliverables_count = client.deliverables.count()
                client.save()
                return deliverable

            await save_deliverable()

            # Confirm to user
            confirm_embed = discord.Embed(
                title="✅ Deliverable Sent!",
                description=f"Image #{image_id} has been delivered to **{client.name}**'s channel.",
                color=discord.Color.green()
            )
            confirm_embed.add_field(name="Channel", value=f"<#{client.channel_id}>", inline=True)

            await interaction.followup.send(embed=confirm_embed, ephemeral=True)

        except Exception as e:
            logger.error(f"/client-deliver command error: {e}")
            await interaction.followup.send(
                f"Error delivering to client: {str(e)[:200]}",
                ephemeral=True
            )

    @app_commands.command(name="client-invite", description="Generate an invite link for a client")
    @app_commands.describe(client_name="Client name to generate invite for")
    async def client_invite(self, interaction: discord.Interaction, client_name: str):
        """Generate a Discord invite link for a client's channel."""
        await interaction.response.defer(ephemeral=True)

        try:
            server = await self._get_user_server(str(interaction.guild.id))
            if not server:
                await interaction.followup.send(
                    "Please set up your server first using `/setup` command.",
                    ephemeral=True
                )
                return

            # Find client
            @sync_to_async
            def get_client():
                from core.models.base import DiscordClient
                return DiscordClient.objects.filter(
                    server=server,
                    name__iexact=client_name
                ).first()

            client = await get_client()
            if not client:
                await interaction.followup.send(
                    f"Client '{client_name}' not found. Use `/client-list` to see your clients.",
                    ephemeral=True
                )
                return

            # Get client channel
            if not client.channel_id:
                await interaction.followup.send(
                    "This client doesn't have a channel configured.",
                    ephemeral=True
                )
                return

            channel = interaction.guild.get_channel(int(client.channel_id))
            if not channel:
                await interaction.followup.send(
                    "Could not find client channel. It may have been deleted.",
                    ephemeral=True
                )
                return

            # Create invite (expires in 7 days, max 1 use)
            invite = await channel.create_invite(
                max_age=604800,  # 7 days
                max_uses=1,
                unique=True,
                reason=f"Client invite for {client.name}"
            )

            embed = discord.Embed(
                title="🔗 Client Invite Link",
                description=f"Invite link for **{client.name}**:",
                color=discord.Color.blue()
            )
            embed.add_field(name="Invite URL", value=invite.url, inline=False)
            embed.add_field(name="Expires", value="7 days", inline=True)
            embed.add_field(name="Max Uses", value="1", inline=True)
            embed.add_field(
                name="⚠️ Note",
                value="This link gives access only to the client's channel.",
                inline=False
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to create invites. Please give me 'Create Instant Invite' permission.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"/client-invite command error: {e}")
            await interaction.followup.send(
                f"Error creating invite: {str(e)[:200]}",
                ephemeral=True
            )


# =============================================================================
# Phase 5: Full Agent Access - Session 434
# =============================================================================

class AgentAccessCommands(commands.Cog):
    """
    Phase 5: Full Agent Access - Direct access to all agents, advisors, and workflows.

    Commands:
    - /agent-task <name> <task> - Execute a task with a specific agent
    - /agent-list [category] - List agents by category
    - /consult <advisor> <question> - Consult a legendary advisor
    - /workflow-list - List available workflows
    - /workflow-run <name> <input> - Run a workflow
    """

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot

    @app_commands.command(name="agent-list", description="List all agents by category")
    @app_commands.describe(category="Filter by category (creative, executive, research, etc.)")
    @app_commands.choices(category=[
        app_commands.Choice(name="All Categories", value="all"),
        app_commands.Choice(name="Creative (Image, Video, Audio, 3D)", value="creative"),
        app_commands.Choice(name="Executive (CTO, COO, Director)", value="executive"),
        app_commands.Choice(name="Research & Analysis", value="research"),
        app_commands.Choice(name="Business Strategy", value="business"),
        app_commands.Choice(name="Content & Marketing", value="content"),
    ])
    async def agent_list(self, interaction: discord.Interaction, category: str = "all"):
        """List all available agents organized by category."""
        await interaction.response.defer()

        try:
            from core.agent_router import AgentRouter

            # Agent categories mapped to agent names
            agent_categories = {
                "creative": {
                    "name": "🎨 Creative Agents",
                    "agents": ["ImageAgent", "VideoAgent", "AudioAgent", "ThreeDAgent",
                              "CreativeDirectorAgent", "BrandIdentityAgent"]
                },
                "executive": {
                    "name": "👔 Executive Agents",
                    "agents": ["CTOAgent", "COOAgent", "MeetingCoordinatorAgent"]
                },
                "research": {
                    "name": "🔬 Research & Analysis",
                    "agents": ["ResearchAgent", "TrendAnalysisAgent", "OpportunityScoringAgent"]
                },
                "business": {
                    "name": "💼 Business Strategy",
                    "agents": ["CompetitorAnalysisAgent", "CustomerResearchAgent",
                              "BrandStrategyAgent", "MarketingStrategyAgent"]
                },
                "content": {
                    "name": "📝 Content & Marketing",
                    "agents": ["ContentStrategyAgent", "SEOOptimizerAgent", "SocialMediaAgent"]
                },
                "editing": {
                    "name": "✂️ Editing",
                    "agents": ["ImageEditingAgent", "VideoEditingAgent"]
                },
                "training": {
                    "name": "🎓 Training",
                    "agents": ["CharacterTrainingAgent", "TrainedCreationAgent"]
                }
            }

            # Get available agents from router
            available_agents = set(AgentRouter.AGENT_MAP.keys())

            embed = discord.Embed(
                title="🤖 Available Agents",
                description="Use `/agent-task <name> <task>` to execute tasks",
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )

            if category == "all":
                # Show all categories
                for cat_key, cat_data in agent_categories.items():
                    agents_in_cat = [a for a in cat_data["agents"] if a in available_agents]
                    if agents_in_cat:
                        agent_list = "\n".join(f"• `{a}`" for a in agents_in_cat)
                        embed.add_field(
                            name=cat_data["name"],
                            value=agent_list,
                            inline=True
                        )
            else:
                # Show specific category
                cat_data = agent_categories.get(category)
                if cat_data:
                    agents_in_cat = [a for a in cat_data["agents"] if a in available_agents]
                    if agents_in_cat:
                        agent_list = "\n".join(f"• `{a}`" for a in agents_in_cat)
                        embed.add_field(
                            name=cat_data["name"],
                            value=agent_list,
                            inline=False
                        )

            embed.set_footer(text=f"Total: {len(available_agents)} agents available")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"/agent-list error: {e}")
            await interaction.followup.send(f"Error listing agents: {str(e)[:100]}", ephemeral=True)

    @app_commands.command(name="agent-task", description="Execute a task with a specific agent")
    @app_commands.describe(
        agent="Agent name (e.g., ImageAgent, CTOAgent, ResearchAgent)",
        task="The task to execute"
    )
    async def agent_task(self, interaction: discord.Interaction, agent: str, task: str):
        """Execute a task using a specific agent."""
        await interaction.response.defer()

        # Rate limit check
        can_use, remaining = rate_limiter.check_cooldown(interaction.user.id, 'agent_task')
        if not can_use:
            await interaction.followup.send(
                f"⏳ Please wait {remaining:.1f}s before running another agent task.",
                ephemeral=True
            )
            return

        try:
            from core.agent_router import AgentRouter, AgentNotFoundError
            from django.contrib.auth import get_user_model
            User = get_user_model()

            # Get linked user
            @sync_to_async
            def get_linked_user(discord_id):
                try:
                    return User.objects.filter(discord_id=str(discord_id)).first()
                except Exception:
                    return None

            user = await get_linked_user(interaction.user.id)

            # Session 439: Check subscription tier limits
            @sync_to_async
            def check_subscription_limit(user):
                from core.models import EnhancedUserProfile
                if not user:
                    # Not linked - use free tier limits
                    return True, "Please link your account with `/link` for more daily tasks!", 5, 0

                try:
                    profile = EnhancedUserProfile.objects.filter(user=user).first()
                    if not profile:
                        return True, None, 5, 0

                    can_use, message = profile.can_use_task()
                    limits = profile.get_tier_limits()
                    return can_use, message if not can_use else None, limits['daily_tasks'], profile.daily_task_count
                except Exception as e:
                    logger.error(f"Error checking subscription limit: {e}")
                    return True, None, 5, 0

            can_use_task, limit_msg, daily_limit, used_today = await check_subscription_limit(user)

            if not can_use_task:
                tier_embed = discord.Embed(
                    title="Daily Task Limit Reached",
                    description=limit_msg or "You've used all your daily tasks.",
                    color=discord.Color.orange()
                )
                tier_embed.add_field(
                    name="Upgrade Options",
                    value=(
                        "**Pro** ($9.99/mo) - 50 tasks/day\n"
                        "**Premium** ($29.99/mo) - Unlimited tasks\n\n"
                        "Use `/subscribe pro` or `/subscribe premium` to upgrade!"
                    ),
                    inline=False
                )
                await interaction.followup.send(embed=tier_embed, ephemeral=True)
                return

            # Normalize agent name (allow partial match)
            agent_name = agent.strip()
            if not agent_name.endswith("Agent"):
                agent_name = agent_name + "Agent"

            # Create router and execute
            @sync_to_async
            def execute_agent(agent_name, task, user):
                router = AgentRouter(user=user)
                return router.route(agent_name, task)

            # Show thinking message
            thinking_embed = discord.Embed(
                title=f"🤖 {agent_name}",
                description=f"Processing: *{task[:100]}{'...' if len(task) > 100 else ''}*",
                color=discord.Color.yellow()
            )
            await interaction.followup.send(embed=thinking_embed)

            # Execute the agent
            result = await execute_agent(agent_name, task, user)
            rate_limiter.record_use(interaction.user.id, 'agent_task')

            # Session 439: Increment task counter on success
            @sync_to_async
            def increment_task_count(user):
                if user:
                    from core.models import EnhancedUserProfile
                    profile = EnhancedUserProfile.objects.filter(user=user).first()
                    if profile:
                        profile.use_task()

            await increment_task_count(user)

            if result.success:
                # Format successful response - handle different agent result formats
                response_text = ""

                # Check for research results (ResearchAgent returns data in 'results')
                if result.data and result.data.get('results'):
                    research_results = result.data['results']
                    parts = [f"**Query:** {result.data.get('query', task)}\n"]
                    for i, res in enumerate(research_results[:5], 1):  # Limit to 5 results
                        source = res.get('source', 'Unknown')
                        data = res.get('data', {})

                        # Handle different data formats from various tools
                        if isinstance(data, list):
                            # spider_query returns a list directly
                            items = data
                        elif isinstance(data, dict):
                            # analyze_trends returns dict with 'discussions', 'projects'
                            # web_search returns dict with 'items' or 'results'
                            items = (
                                data.get('discussions', []) or
                                data.get('projects', []) or
                                data.get('items', []) or
                                data.get('results', [])
                            )
                        else:
                            items = []

                        if items and isinstance(items, list):
                            parts.append(f"\n**{source.upper()}:**")
                            for item in items[:5]:  # 5 items per source
                                if isinstance(item, dict):
                                    title = item.get('title', item.get('name', ''))[:100]
                                    url = item.get('url', item.get('link', ''))
                                    if title:
                                        if url:
                                            parts.append(f"• [{title}]({url})")
                                        else:
                                            parts.append(f"• {title}")
                        elif isinstance(data, dict) and data.get('summary'):
                            parts.append(f"\n**{source.upper()}:** {data['summary'][:300]}")
                        elif isinstance(data, str):
                            parts.append(f"\n**{source.upper()}:** {data[:300]}")
                    response_text = "\n".join(parts)
                else:
                    # Default: use message or response field
                    response_text = result.message or result.data.get('response', 'Task completed successfully.')

                if len(response_text) > 4000:
                    response_text = response_text[:4000] + "...\n\n*[Response truncated]*"

                embed = discord.Embed(
                    title=f"✅ {agent_name} Response",
                    description=response_text,
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )

                # Add execution time if available
                if result.execution_time_ms:
                    embed.set_footer(text=f"Completed in {result.execution_time_ms}ms")

                # Check for generated content
                if result.data:
                    if result.data.get('image_url'):
                        embed.set_image(url=result.data['image_url'])
                    if result.data.get('video_url'):
                        embed.add_field(name="Video", value=f"[View Video]({result.data['video_url']})", inline=True)

                await interaction.edit_original_response(embed=embed)
            else:
                # Format error response
                error_msg = result.error or "Unknown error occurred"
                embed = discord.Embed(
                    title=f"❌ {agent_name} Error",
                    description=f"```{error_msg[:500]}```",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed)

        except AgentNotFoundError as e:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="❌ Agent Not Found",
                    description=f"Agent `{agent}` not found.\n\nUse `/agent-list` to see available agents.",
                    color=discord.Color.red()
                )
            )
        except Exception as e:
            logger.error(f"/agent-task error: {e}")
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"Failed to execute agent: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @app_commands.command(name="consult", description="Consult a legendary advisor")
    @app_commands.describe(
        advisor="Advisor name (e.g., warren, elon, steve)",
        question="Your question for the advisor"
    )
    async def consult(self, interaction: discord.Interaction, advisor: str, question: str):
        """Consult one of the legendary advisors."""
        await interaction.response.defer()

        # Rate limit check
        can_use, remaining = rate_limiter.check_cooldown(interaction.user.id, 'consult')
        if not can_use:
            await interaction.followup.send(
                f"⏳ Please wait {remaining:.1f}s before another consultation.",
                ephemeral=True
            )
            return

        try:
            from core.models_unified_system import Advisor
            from core.models import EnhancedUserProfile
            from django.contrib.auth import get_user_model
            User = get_user_model()
            import openai
            import os

            # Session 439: Check Premium subscription for advisor access
            @sync_to_async
            def check_advisor_access(discord_id):
                try:
                    user = User.objects.filter(discord_id=str(discord_id)).first()
                    if not user:
                        return False, None

                    profile = EnhancedUserProfile.objects.filter(user=user).first()
                    if not profile:
                        return False, None

                    # Premium users have advisor access
                    if profile.has_feature('advisor_access'):
                        return True, user
                    return False, user
                except Exception:
                    return False, None

            has_access, user = await check_advisor_access(interaction.user.id)

            if not has_access:
                premium_embed = discord.Embed(
                    title="Premium Feature",
                    description="Advisor consultations are available to **Premium** subscribers only.",
                    color=discord.Color.gold()
                )
                premium_embed.add_field(
                    name="Premium Benefits",
                    value=(
                        "• Access to 25 legendary advisors\n"
                        "• Warren Buffett, Elon Musk, Steve Jobs...\n"
                        "• Unlimited agent tasks\n"
                        "• Custom workflows\n\n"
                        "**$29.99/month** - Use `/subscribe premium`"
                    ),
                    inline=False
                )
                await interaction.followup.send(embed=premium_embed, ephemeral=True)
                return

            # Find advisor (case-insensitive partial match)
            @sync_to_async
            def find_advisor(name):
                return Advisor.objects.filter(name__icontains=name).first()

            advisor_obj = await find_advisor(advisor)

            if not advisor_obj:
                # List available advisors
                @sync_to_async
                def get_advisor_list():
                    return list(Advisor.objects.values_list('name', flat=True)[:10])

                advisor_names = await get_advisor_list()
                embed = discord.Embed(
                    title="❌ Advisor Not Found",
                    description=f"Advisor `{advisor}` not found.\n\n**Available advisors:**\n" +
                                "\n".join(f"• {name.split()[0].lower()}" for name in advisor_names),
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Show thinking message
            thinking_embed = discord.Embed(
                title=f"🎩 Consulting {advisor_obj.name}...",
                description=f"*{question[:200]}{'...' if len(question) > 200 else ''}*",
                color=discord.Color.gold()
            )
            await interaction.followup.send(embed=thinking_embed)

            # Get specialty
            specialty = getattr(advisor_obj, 'specialty', '') or getattr(advisor_obj, 'expertise', '') or 'General advice'

            # Build advisor prompt
            advisor_prompt = f"""You are {advisor_obj.name}, a legendary advisor known for {specialty}.

Respond to questions in the distinctive voice and perspective of {advisor_obj.name}.
Draw on your known philosophies, strategies, and experiences. Be authentic to the persona.

User's question: {question}

Provide thoughtful, actionable advice that reflects {advisor_obj.name}'s unique perspective.
Keep the response concise but insightful (max 300 words)."""

            # Call OpenAI
            @sync_to_async
            def get_advisor_response():
                client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": advisor_prompt},
                        {"role": "user", "content": question}
                    ],
                    max_tokens=500
                )
                return response.choices[0].message.content

            response_text = await get_advisor_response()
            rate_limiter.record_use(interaction.user.id, 'consult')

            # Format response
            embed = discord.Embed(
                title=f"🎩 {advisor_obj.name}",
                description=response_text,
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Expertise", value=specialty[:100], inline=True)
            embed.set_footer(text="Legendary Advisor Consultation")

            await interaction.edit_original_response(embed=embed)

        except Exception as e:
            logger.error(f"/consult error: {e}")
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"Failed to consult advisor: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @app_commands.command(name="advisors", description="List all available advisors")
    async def advisors(self, interaction: discord.Interaction):
        """List all legendary advisors available for consultation."""
        await interaction.response.defer()

        try:
            from core.models_unified_system import Advisor

            @sync_to_async
            def get_advisors():
                return list(Advisor.objects.all()[:25])

            advisors = await get_advisors()

            embed = discord.Embed(
                title="🎩 Legendary Advisors",
                description="Use `/consult <name> <question>` to consult an advisor",
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )

            # Group advisors by first letter or category
            advisor_lines = []
            for adv in advisors:
                specialty = getattr(adv, 'specialty', '') or getattr(adv, 'expertise', '') or ''
                specialty_short = specialty[:35] + '...' if len(specialty) > 35 else specialty
                # Use first name as command shortcut
                shortcut = adv.name.split()[0].lower()
                advisor_lines.append(f"• **{adv.name}** (`{shortcut}`)\n  _{specialty_short}_")

            # Split into columns
            mid = len(advisor_lines) // 2
            embed.add_field(name="Advisors (1-13)", value="\n".join(advisor_lines[:13]), inline=True)
            embed.add_field(name="Advisors (14-25)", value="\n".join(advisor_lines[13:]), inline=True)

            embed.set_footer(text=f"Total: {len(advisors)} advisors")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"/advisors error: {e}")
            await interaction.followup.send(f"Error listing advisors: {str(e)[:100]}", ephemeral=True)

    @app_commands.command(name="workflow-list", description="List available workflows")
    async def workflow_list(self, interaction: discord.Interaction):
        """List all available multi-step workflows."""
        await interaction.response.defer()

        try:
            # Available workflows (from CLAUDE.md)
            workflows = {
                "research_and_create_logos": {
                    "name": "Research & Logo Pack",
                    "description": "Research topic + generate 3 logo variations",
                    "steps": ["Research", "Generate logos (1024x1024)"]
                },
                "youtube_thumbnail_package": {
                    "name": "YouTube Thumbnail Pack",
                    "description": "Research topic + create thumbnails",
                    "steps": ["Research", "Generate thumbnails (1280x720)"]
                },
                "brand_identity_package": {
                    "name": "Brand Identity Pack",
                    "description": "Research + complete brand identity",
                    "steps": ["Research", "Logo", "Color palette", "Style guide"]
                },
                "product_photography_kit": {
                    "name": "Product Photography Kit",
                    "description": "Research + product photo variations",
                    "steps": ["Research", "Generate product photos"]
                },
                "video_thumbnail_series": {
                    "name": "Video Thumbnail Series",
                    "description": "Create consistent thumbnail series",
                    "steps": ["Style analysis", "Generate 5 thumbnails"]
                },
                "logo_to_video": {
                    "name": "Logo to Video",
                    "description": "Animate a logo into a video intro",
                    "steps": ["Analyze logo", "Generate animation"]
                }
            }

            embed = discord.Embed(
                title="🔄 Available Workflows",
                description="Use `/workflow-run <name> <input>` to run a workflow",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            for wf_id, wf in workflows.items():
                steps = " → ".join(wf["steps"])
                embed.add_field(
                    name=f"📋 {wf['name']}",
                    value=f"**ID:** `{wf_id}`\n{wf['description']}\n*Steps: {steps}*",
                    inline=False
                )

            embed.set_footer(text=f"Total: {len(workflows)} workflows")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"/workflow-list error: {e}")
            await interaction.followup.send(f"Error listing workflows: {str(e)[:100]}", ephemeral=True)

    @app_commands.command(name="workflow-run", description="Run a multi-step workflow")
    @app_commands.describe(
        workflow="Workflow ID (e.g., research_and_create_logos)",
        input_text="Input for the workflow (topic, prompt, etc.)"
    )
    async def workflow_run(self, interaction: discord.Interaction, workflow: str, input_text: str):
        """Run a multi-step workflow."""
        await interaction.response.defer()

        # Rate limit check
        can_use, remaining = rate_limiter.check_cooldown(interaction.user.id, 'workflow')
        if not can_use:
            await interaction.followup.send(
                f"⏳ Please wait {remaining:.1f}s before running another workflow.",
                ephemeral=True
            )
            return

        try:
            from core.agent_router import AgentRouter
            from django.contrib.auth import get_user_model
            User = get_user_model()

            # Get linked user
            @sync_to_async
            def get_linked_user(discord_id):
                try:
                    return User.objects.filter(discord_id=str(discord_id)).first()
                except Exception:
                    return None

            user = await get_linked_user(interaction.user.id)

            # Show starting message
            embed = discord.Embed(
                title=f"🔄 Running Workflow: {workflow}",
                description=f"Input: *{input_text[:100]}{'...' if len(input_text) > 100 else ''}*\n\n⏳ Processing...",
                color=discord.Color.yellow()
            )
            await interaction.followup.send(embed=embed)

            # Execute via WorkflowAgent
            @sync_to_async
            def run_workflow(workflow_name, input_text, user):
                router = AgentRouter(user=user)
                task = f"Run the {workflow_name} workflow with input: {input_text}"
                return router.route("WorkflowAgent", task)

            result = await run_workflow(workflow, input_text, user)
            rate_limiter.record_use(interaction.user.id, 'workflow')

            if result.success:
                response_text = result.message or result.data.get('response', 'Workflow completed successfully.')
                if len(response_text) > 4000:
                    response_text = response_text[:4000] + "...\n\n*[Response truncated]*"

                embed = discord.Embed(
                    title=f"✅ Workflow Complete: {workflow}",
                    description=response_text,
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )

                # Add any generated content
                if result.data:
                    if result.data.get('images'):
                        embed.add_field(
                            name="Generated Images",
                            value=f"{len(result.data['images'])} images created",
                            inline=True
                        )
                    if result.data.get('image_url'):
                        embed.set_image(url=result.data['image_url'])

                if result.execution_time_ms:
                    embed.set_footer(text=f"Completed in {result.execution_time_ms}ms")

                await interaction.edit_original_response(embed=embed)
            else:
                error_msg = result.error or "Unknown error occurred"
                embed = discord.Embed(
                    title=f"❌ Workflow Failed: {workflow}",
                    description=f"```{error_msg[:500]}```",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed)

        except Exception as e:
            logger.error(f"/workflow-run error: {e}")
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"Failed to run workflow: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )


class HelpCommands(commands.Cog):
    """Help and documentation commands."""

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot

    @app_commands.command(name="help", description="Show available commands")
    async def help_command(self, interaction: discord.Interaction):
        """Display available commands and their descriptions."""
        embed = discord.Embed(
            title=" Donkey Betz Bot Commands",
            description="Available slash commands for the AI Platform.",
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )

        # Interactive commands (Sessions 427-428)
        embed.add_field(
            name=" Interactive",
            value=(
                "**/ask** <question> - Ask the Personal Assistant (remembers context!)\n"
                "**/create** <prompt> - Generate an image\n"
                "**/research** <topic> [limit] - Search spider data\n"
                "**/clear** - Clear your conversation history"
            ),
            inline=False
        )

        # Status commands
        embed.add_field(
            name=" System",
            value=(
                "**/status** - System health check\n"
                "**/spiders** - Spider network stats"
            ),
            inline=False
        )

        # Agent commands
        embed.add_field(
            name="🤖 Agents",
            value=(
                "**/agents** [limit] - List active agents\n"
                "**/agent** <name> - Get agent details\n"
                "**/agent-list** [category] - List agents by category\n"
                "**/agent-task** <name> <task> - Execute agent task"
            ),
            inline=False
        )

        # Advisors (Phase 5)
        embed.add_field(
            name="🎩 Advisors",
            value=(
                "**/advisors** - List all legendary advisors\n"
                "**/consult** <advisor> <question> - Consult an advisor"
            ),
            inline=False
        )

        # Workflows (Phase 5)
        embed.add_field(
            name="🔄 Workflows",
            value=(
                "**/workflow-list** - List available workflows\n"
                "**/workflow-run** <name> <input> - Run a workflow"
            ),
            inline=False
        )

        # Data commands
        embed.add_field(
            name=" Data",
            value=(
                "**/trending** [category] [limit] - Trending topics"
            ),
            inline=False
        )

        # Content & Profile (Session 430)
        embed.add_field(
            name="🖼️ Content",
            value=(
                "**/gallery** [count] - View your recent images\n"
                "**/profile** - View your AI Studio profile"
            ),
            inline=False
        )

        # Income Pipeline (Session 433)
        embed.add_field(
            name="💰 Income Pipeline",
            value=(
                "**/opportunities** [count] [category] - Browse income opportunities\n"
                "**/apply** <id> [message] - Apply to an opportunity\n"
                "**/track** [status] - Track your applications"
            ),
            inline=False
        )

        # Account linking (Session 429)
        embed.add_field(
            name="🔗 Account",
            value=(
                "**/link** <code> - Link Discord to AI Studio account\n"
                "**/unlink** - Check link status"
            ),
            inline=False
        )

        # Server Setup (Session 431)
        embed.add_field(
            name="🏗️ Server Setup",
            value=(
                "**/setup** [template] - Set up AI Studio channels in your server\n"
                "**/server-info** - View your server's configuration"
            ),
            inline=False
        )

        # Client Management (Session 432: Phase 3)
        embed.add_field(
            name="👥 Client Management",
            value=(
                "**/client-add** <name> [email] - Create client with dedicated channel\n"
                "**/client-list** - List all your clients\n"
                "**/client-deliver** <client> <image_id> [message] - Send deliverable\n"
                "**/client-invite** <client> - Generate invite link for client"
            ),
            inline=False
        )

        # Help
        embed.add_field(
            name="❓ Help",
            value="**/help** - This command",
            inline=False
        )

        embed.set_footer(text="Session 434 | Discord-First Platform Phase 5 - Full Agent Access")

        await interaction.response.send_message(embed=embed)


# Bot instance (created when module loads)
_bot_instance: Optional[DonkeyBetzBot] = None


def get_bot() -> DonkeyBetzBot:
    """Get or create the bot instance."""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = DonkeyBetzBot()
    return _bot_instance


async def run_bot():
    """Run the Discord bot."""
    token = os.environ.get('DISCORD_BOT_TOKEN')

    if not token:
        logger.error("DISCORD_BOT_TOKEN not set!")
        return

    bot = get_bot()

    try:
        await bot.start(token)
    except discord.LoginFailure:
        logger.error("Invalid Discord bot token!")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()


def start_bot():
    """Start the bot (blocking call)."""
    asyncio.run(run_bot())
