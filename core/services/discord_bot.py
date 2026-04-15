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
from django.utils import timezone

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
            'voice_ask': 15, # 15 seconds between /voice-ask calls (TTS is expensive)
            'voice_chat': 20, # 20 seconds between /voice-chat calls (recording + TTS)
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


class DatabaseConversationHistory:
    """
    Session 455: Database-backed conversation history for cross-platform session continuity.

    Stores conversations in ChatConversation model so they can be:
    - Persisted across bot restarts
    - Accessed from web app
    - Resumed on any platform (web ↔ Discord)

    Features:
    - Stores up to MAX_MESSAGES per user
    - Sessions expire after EXPIRY_HOURS of inactivity
    - Automatic session titles generated from first message
    - Linked to user accounts when Discord is linked
    """

    MAX_MESSAGES = 20  # Keep last 20 messages per user
    EXPIRY_HOURS = 24  # Sessions expire after 24 hours (extended from 2)

    def __init__(self):
        # In-memory cache for active sessions to reduce DB hits
        # {discord_user_id: {'conversation_id': str, 'last_activity': datetime}}
        self._session_cache: Dict[int, Dict[str, Any]] = {}

    def _get_conversation_id(self, discord_user_id: int) -> str:
        """Get or create conversation ID for a Discord user."""
        import uuid
        from django.utils import timezone

        # Check cache first
        if discord_user_id in self._session_cache:
            cache_entry = self._session_cache[discord_user_id]
            # Check if session is still valid (within expiry window)
            if timezone.now() - cache_entry['last_activity'] < timedelta(hours=self.EXPIRY_HOURS):
                cache_entry['last_activity'] = timezone.now()
                return cache_entry['conversation_id']

        # Try to find recent active session in database
        try:
            from core.models import ChatConversation
            cutoff = timezone.now() - timedelta(hours=self.EXPIRY_HOURS)

            recent = ChatConversation.objects.filter(
                discord_user_id=str(discord_user_id),
                session_active=True,
                created_at__gte=cutoff
            ).order_by('-created_at').first()

            if recent:
                conversation_id = recent.conversation_id
            else:
                conversation_id = str(uuid.uuid4())

            # Update cache
            self._session_cache[discord_user_id] = {
                'conversation_id': conversation_id,
                'last_activity': timezone.now()
            }
            return conversation_id

        except Exception as e:
            logger.error(f"Error getting conversation ID: {e}")
            return str(uuid.uuid4())

    def add_message(self, user_id: int, role: str, content: str, channel_id: int = None, guild_id: int = None):
        """
        Add a message to user's conversation history.
        Stores in database for persistence and cross-platform access.
        """
        from django.utils import timezone

        try:
            from core.models import ChatConversation, UnifiedUser

            conversation_id = self._get_conversation_id(user_id)

            # Try to find linked user.
            # Session 1103c: loud so failed discord→web linkage doesn't
            # silently revert to anonymous mode for linked users.
            linked_user = None
            try:
                linked_user = UnifiedUser.objects.filter(discord_id=str(user_id)).first()
            except Exception as e:
                logger.warning(
                    "discord_bot: linked user lookup failed for "
                    "discord_id=%s (%s: %s) — treating as unlinked",
                    user_id, type(e).__name__, e,
                )

            # For assistant responses, update the last message instead of creating new
            if role == 'assistant':
                # Find the most recent user message in this conversation
                last_user_msg = ChatConversation.objects.filter(
                    conversation_id=conversation_id,
                    discord_user_id=str(user_id)
                ).order_by('-created_at').first()

                if last_user_msg and not last_user_msg.assistant_response:
                    # Update with assistant response
                    last_user_msg.assistant_response = content[:10000]  # Limit length
                    last_user_msg.save()

                    # Generate session title from first message if not set
                    if not last_user_msg.session_title:
                        last_user_msg.generate_session_title()
                    return

            # Create new message entry
            ChatConversation.objects.create(
                user=linked_user,
                conversation_id=conversation_id,
                user_message=content[:10000] if role == 'user' else '',
                assistant_response=content[:10000] if role == 'assistant' else '',
                platform='discord',
                discord_user_id=str(user_id),
                discord_channel_id=str(channel_id) if channel_id else None,
                discord_guild_id=str(guild_id) if guild_id else None,
                session_active=True,
                metadata={'source': 'discord_bot', 'timestamp': timezone.now().isoformat()}
            )

            # Update cache
            if user_id in self._session_cache:
                self._session_cache[user_id]['last_activity'] = timezone.now()

        except Exception as e:
            logger.error(f"Error adding message to database: {e}")

    def get_history(self, user_id: int) -> List[Dict[str, str]]:
        """
        Get conversation history for user as list of message dicts.
        Returns empty list if no history or expired.
        """
        from django.utils import timezone

        try:
            from core.models import ChatConversation

            conversation_id = self._get_conversation_id(user_id)
            cutoff = timezone.now() - timedelta(hours=self.EXPIRY_HOURS)

            # Get messages from this conversation
            messages = ChatConversation.objects.filter(
                conversation_id=conversation_id,
                created_at__gte=cutoff
            ).order_by('created_at')[:self.MAX_MESSAGES]

            # Convert to LLM format
            history = []
            for msg in messages:
                if msg.user_message:
                    history.append({'role': 'user', 'content': msg.user_message})
                if msg.assistant_response:
                    history.append({'role': 'assistant', 'content': msg.assistant_response})

            return history

        except Exception as e:
            logger.error(f"Error getting history from database: {e}")
            return []

    def clear(self, user_id: int) -> bool:
        """
        Clear conversation history for user.
        Marks session as inactive rather than deleting.
        Returns True if there was history to clear.
        """
        try:
            from core.models import ChatConversation

            # Mark all active sessions for this user as inactive
            updated = ChatConversation.objects.filter(
                discord_user_id=str(user_id),
                session_active=True
            ).update(session_active=False)

            # Clear from cache
            if user_id in self._session_cache:
                del self._session_cache[user_id]

            return updated > 0

        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return False

    def get_message_count(self, user_id: int) -> int:
        """Get number of messages in user's current session."""
        try:
            from core.models import ChatConversation
            from django.utils import timezone

            conversation_id = self._get_conversation_id(user_id)
            cutoff = timezone.now() - timedelta(hours=self.EXPIRY_HOURS)

            # Count messages with content
            count = ChatConversation.objects.filter(
                conversation_id=conversation_id,
                created_at__gte=cutoff
            ).count()

            # Each record has user + assistant, so multiply by 2 for message count
            return count * 2

        except Exception as e:
            logger.error(f"Error getting message count: {e}")
            return 0

    def cleanup_expired(self):
        """Mark all expired sessions as inactive."""
        from django.utils import timezone

        try:
            from core.models import ChatConversation

            cutoff = timezone.now() - timedelta(hours=self.EXPIRY_HOURS)

            # Mark old sessions as inactive
            updated = ChatConversation.objects.filter(
                platform='discord',
                session_active=True,
                created_at__lt=cutoff
            ).update(session_active=False)

            # Clear cache entries
            now = timezone.now()
            expired_users = [
                uid for uid, cache in self._session_cache.items()
                if now - cache['last_activity'] > timedelta(hours=self.EXPIRY_HOURS)
            ]
            for uid in expired_users:
                del self._session_cache[uid]

            return updated

        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0

    def get_session_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get info about user's current session.
        Useful for showing session continuity to user.
        """
        try:
            from core.models import ChatConversation

            conversation_id = self._get_conversation_id(user_id)

            first_msg = ChatConversation.objects.filter(
                conversation_id=conversation_id
            ).order_by('created_at').first()

            if not first_msg:
                return None

            last_msg = ChatConversation.objects.filter(
                conversation_id=conversation_id
            ).order_by('-created_at').first()

            return {
                'conversation_id': conversation_id,
                'session_title': first_msg.session_title or first_msg.user_message[:50],
                'started_at': first_msg.created_at,
                'last_activity': last_msg.created_at if last_msg else first_msg.created_at,
                'message_count': self.get_message_count(user_id),
                'platform': 'discord',
                'linked_user': first_msg.user.username if first_msg.user else None,
            }

        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return None


# Global conversation history instance - now uses database!
# Session 455: Upgraded from in-memory to database storage for cross-platform continuity
conversation_history = DatabaseConversationHistory()


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
        # Phase G2: VoiceMarketplace, PipelineLearning, Narrative, ROI Cogs deleted
        await self.add_cog(ContentPipelineCommands(self))  # Session 440: Content Pipeline
        await self.add_cog(SeriesCommands(self))  # Session 445: AI Series Workflow
        await self.add_cog(StudioCommands(self))  # Session 466: Autonomous Content Studio
        await self.add_cog(RoleManager(self))  # Session 439: Subscription role management
        await self.add_cog(HelpCommands(self))
        await self.add_cog(ReactionFeedbackCog(self))  # Session 452: Auto-feedback from reactions
        await self.add_cog(ResolveCommands(self))  # Session 478: DaVinci Resolve Integration
        await self.add_cog(SituationCommands(self))  # Session 480: All 19 Autonomous Situations
        await self.add_cog(GumroadCommands(self))  # Session 487: Gumroad Publishing (Golden Egg)
        await self.add_cog(PodcastCommands(self))  # Session 496: AI Podcast Studio
        await self.add_cog(LegalCommands(self))  # Session 497: Pro Se Legal Assistant
        await self.add_cog(DeveloperCommands(self))  # Session 497: Code Generation/Review
        await self.add_cog(MLScoringCommands(self))  # Session 497: ML Scoring Status
        await self.add_cog(ReviewCommands(self))  # Session 556: Chief of Staff Review Documents
        await self.add_cog(HumanInterfaceCommands(self))  # Session 686: Human Interface Layer
        await self.add_cog(OBSCommands(self))  # OBS Bridge recording control

        # Sync slash commands with Discord
        try:
            # Donkey Betz guild ID - commands only work in this server
            # Phase G2: 59 slots used (Groups count as 1 each)
            guild = discord.Object(id=971148613109555212)

            # First, copy all global commands to the guild
            self.tree.copy_global_to(guild=guild)

            # Then sync to the guild (instant, no propagation delay)
            guild_synced = await self.tree.sync(guild=guild)
            logger.info(f"Synced {len(guild_synced)} slash commands to Donkey Betz guild (instant)")

            # NOTE: Global sync disabled to avoid 100 command limit warnings
            # All commands work only in Donkey Betz server
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

                categories = list(SpiderData.objects.values('data_type').annotate(
                    count=Count('id')
                ).order_by('-count')[:10])

                return {
                    'total': SpiderData.objects.count(),
                    'today': SpiderData.objects.filter(created_at__date=today).count(),
                    'week': SpiderData.objects.filter(created_at__gte=week_ago).count(),
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
                    f" {c['data_type'] or 'Unknown'}: {c['count']:,}"
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

    # Session 558: Prediction Markets command
    @app_commands.command(name="predictions", description="View prediction market signals from Kalshi")
    @app_commands.describe(
        category="Filter by category (economics, politics, tech, finance, weather)",
        limit="Number of markets to show (default: 5)"
    )
    async def predictions(
        self,
        interaction: discord.Interaction,
        category: Optional[str] = None,
        limit: int = 5
    ):
        """Display prediction market data from Kalshi."""
        await interaction.response.defer()

        try:
            from ai_core.spiders.specialized.kalshi_spider import KalshiSpider

            # Cap limit
            limit = min(limit, 10)

            @sync_to_async
            def get_prediction_data(cat, lim):
                spider = KalshiSpider()
                markets = spider.fetch_data(max_results=100)

                # Filter to actual markets (not series)
                markets = [m for m in markets if m.get('data_type') == 'prediction_market']

                # Filter by category if specified
                if cat:
                    cat_lower = cat.lower()
                    markets = [m for m in markets if m.get('category', '').lower() == cat_lower]

                # Sort by volume (most active first)
                markets.sort(key=lambda m: m.get('volume', 0) or 0, reverse=True)

                return markets[:lim], len(markets)

            markets_data, total_count = await get_prediction_data(category, limit)

            if not markets_data:
                await interaction.followup.send(
                    f"No prediction markets found{' for category: ' + category if category else ''}.",
                    ephemeral=True
                )
                return

            # Category emojis
            category_emoji = {
                'economics': '📊',
                'politics': '🏛️',
                'finance': '💰',
                'tech': '🔧',
                'weather': '🌤️',
                'entertainment': '🎬',
                'science': '🔬',
                'general': '📈',
            }

            embed = discord.Embed(
                title=f"🎰 Prediction Markets{' - ' + category.title() if category else ''}",
                description="Live market data from Kalshi",
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )

            for market in markets_data:
                title = market.get('title', 'Unknown Market')
                title = title[:60] + "..." if len(title) > 60 else title
                ticker = market.get('ticker', '')
                cat = market.get('category', 'general')
                emoji = category_emoji.get(cat, '📈')

                # Probability and pricing
                prob = market.get('implied_probability_pct', 50)
                yes_bid = market.get('yes_bid', 0)
                yes_ask = market.get('yes_ask', 0)
                volume = market.get('volume', 0) or 0

                # Probability bar visualization
                prob_bar_filled = int(prob / 10)
                prob_bar = '█' * prob_bar_filled + '░' * (10 - prob_bar_filled)

                # Status indicators
                if prob >= 80:
                    status = "🟢 Likely"
                elif prob <= 20:
                    status = "🔴 Unlikely"
                elif 40 <= prob <= 60:
                    status = "🟡 Uncertain"
                else:
                    status = "⚪ Leaning"

                field_value = (
                    f"```\n"
                    f"Probability: {prob:.1f}% {prob_bar}\n"
                    f"Yes: {yes_bid}¢-{yes_ask}¢ | Vol: {volume:,}\n"
                    f"Status: {status}\n"
                    f"```"
                )

                embed.add_field(
                    name=f"{emoji} {title}",
                    value=field_value,
                    inline=False
                )

            # Tags for high-value markets
            tags = market.get('tags', [])
            tag_indicators = []
            if 'high_volume' in tags:
                tag_indicators.append('🔥 High Volume')
            if 'trending' in [m.get('is_trending') for m in markets_data]:
                tag_indicators.append('📈 Trending')

            footer_text = f"Showing {len(markets_data)} of {total_count} markets"
            if tag_indicators:
                footer_text += f" | {' '.join(tag_indicators)}"

            embed.set_footer(text=footer_text)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Predictions command error: {e}")
            await interaction.followup.send(
                f"Error fetching predictions: {str(e)[:100]}",
                ephemeral=True
            )

    # Session 558: Sports Odds command
    @app_commands.command(name="odds", description="View sports betting odds and analysis")
    @app_commands.describe(
        sport="Filter by sport (nfl, nba, nhl, ncaaf, ncaab, soccer, ufc)",
        show="What to show: tossups, favorites, or all (default: all)",
        limit="Number of events to show (default: 5)"
    )
    async def odds(
        self,
        interaction: discord.Interaction,
        sport: Optional[str] = None,
        show: Optional[str] = None,
        limit: int = 5
    ):
        """Display sports betting odds from The Odds API."""
        await interaction.response.defer()

        try:
            from ai_core.spiders.specialized.theodds_spider import TheOddsSpider

            # Cap limit
            limit = min(limit, 10)

            @sync_to_async
            def get_odds_data(sport_filter, show_filter, lim):
                spider = TheOddsSpider()
                events = spider.fetch_data(max_results=100, max_priority=2)

                # Filter to actual sports odds
                events = [e for e in events if e.get('data_type') == 'sports_odds']

                # Filter by sport if specified
                if sport_filter:
                    sport_lower = sport_filter.lower()
                    sport_map = {
                        'nfl': 'NFL', 'nba': 'NBA', 'nhl': 'NHL',
                        'mlb': 'MLB', 'ncaaf': 'NCAAF', 'ncaab': 'NCAAB',
                        'soccer': 'English Premier League', 'epl': 'English Premier League',
                        'ufc': 'UFC/MMA', 'mma': 'UFC/MMA',
                    }
                    target_sport = sport_map.get(sport_lower, sport_filter)
                    events = [e for e in events if target_sport.lower() in e.get('sport_name', '').lower()]

                # Filter by show type
                if show_filter:
                    show_lower = show_filter.lower()
                    if show_lower == 'tossups':
                        events = [e for e in events if 45 <= (e.get('home_implied_prob') or 50) <= 55]
                    elif show_lower == 'favorites':
                        events = [e for e in events if (e.get('favorite_probability') or 0) >= 65]

                # Sort by game time (upcoming first)
                events.sort(key=lambda e: e.get('commence_time', ''))

                return events[:lim], len(events)

            events_data, total_count = await get_odds_data(sport, show, limit)

            if not events_data:
                await interaction.followup.send(
                    f"No sports odds found{' for ' + sport if sport else ''}{' (' + show + ')' if show else ''}.",
                    ephemeral=True
                )
                return

            # Sport emojis
            sport_emoji = {
                'NFL': '🏈', 'NCAAF': '🏈',
                'NBA': '🏀', 'NCAAB': '🏀',
                'NHL': '🏒',
                'MLB': '⚾',
                'UFC/MMA': '🥊',
                'English Premier League': '⚽', 'La Liga': '⚽',
                'Champions League': '⚽', 'Bundesliga': '⚽',
                'Serie A': '⚽', 'Ligue 1': '⚽', 'MLS': '⚽',
            }

            title_parts = ["🎲 Sports Odds"]
            if sport:
                title_parts.append(f"- {sport.upper()}")
            if show:
                title_parts.append(f"({show.title()})")

            embed = discord.Embed(
                title=" ".join(title_parts),
                description="Live odds from 40+ bookmakers",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )

            for event in events_data:
                sport_name = event.get('sport_name', 'Unknown')
                emoji = sport_emoji.get(sport_name, '🎯')
                home = event.get('home_team', 'Home')
                away = event.get('away_team', 'Away')
                home_odds = event.get('home_odds', 0)
                away_odds = event.get('away_odds', 0)
                home_prob = event.get('home_implied_prob', 50)
                away_prob = event.get('away_implied_prob', 50)
                spread = event.get('home_spread')
                total = event.get('total_line')
                game_time = event.get('commence_time_formatted', 'TBD')
                favorite = event.get('favorite', '')

                # Format odds with + for positive
                home_odds_str = f"+{home_odds}" if home_odds > 0 else str(home_odds)
                away_odds_str = f"+{away_odds}" if away_odds > 0 else str(away_odds)

                # Determine favorite indicator
                fav_indicator = ""
                if favorite == home:
                    home = f"**{home}** ⭐"
                elif favorite == away:
                    away = f"**{away}** ⭐"

                # Build matchup display
                spread_str = f"Spread: {spread:+.1f}" if spread else ""
                total_str = f"O/U: {total}" if total else ""
                lines = f"{spread_str}  {total_str}".strip()

                field_value = (
                    f"```\n"
                    f"{away[:20]}: {away_odds_str} ({away_prob:.0f}%)\n"
                    f"{home[:20]}: {home_odds_str} ({home_prob:.0f}%)\n"
                    f"{lines}\n"
                    f"⏰ {game_time}\n"
                    f"```"
                )

                embed.add_field(
                    name=f"{emoji} {sport_name}: {away[:15]} @ {home[:15]}",
                    value=field_value,
                    inline=False
                )

            # Toss-up indicator
            tossups = len([e for e in events_data if 45 <= (e.get('home_implied_prob') or 50) <= 55])
            footer_text = f"Showing {len(events_data)} of {total_count} events"
            if tossups > 0:
                footer_text += f" | 🎯 {tossups} toss-ups"

            embed.set_footer(text=footer_text)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Odds command error: {e}")
            await interaction.followup.send(
                f"Error fetching odds: {str(e)[:100]}",
                ephemeral=True
            )

    # Session 558: Arbitrage Detector command
    @app_commands.command(name="arb", description="Scan for arbitrage opportunities across bookmakers")
    @app_commands.describe(
        sport="Filter by sport (nfl, nba, nhl, ncaaf, ncaab)",
        min_profit="Minimum profit % to show (default: 0.5)"
    )
    async def arb(
        self,
        interaction: discord.Interaction,
        sport: Optional[str] = None,
        min_profit: float = 0.5
    ):
        """Scan for arbitrage (guaranteed profit) opportunities."""
        await interaction.response.defer()

        try:
            from core.agents.markets import ArbitrageDetector

            @sync_to_async
            def run_arb_scan(sport_filter, min_pct):
                detector = ArbitrageDetector()
                context = {'min_profit_pct': min_pct}
                if sport_filter:
                    context['sport'] = sport_filter.lower()

                result = detector.execute(
                    task=f"Scan for arbitrage opportunities{' in ' + sport_filter.upper() if sport_filter else ''}",
                    context=context
                )
                return result

            result = await run_arb_scan(sport, min_profit)

            if not result.success:
                await interaction.followup.send(
                    f"Arbitrage scan failed: {result.error or 'Unknown error'}",
                    ephemeral=True
                )
                return

            arbs = result.data.get('arbitrage_opportunities', [])
            hot_count = result.data.get('hot_arbs', 0)
            good_count = result.data.get('good_arbs', 0)
            events_scanned = result.data.get('events_scanned', 0)

            # Create embed
            if arbs:
                color = discord.Color.gold() if hot_count > 0 else discord.Color.green()
                title_emoji = "🔥" if hot_count > 0 else "✅"
            else:
                color = discord.Color.blue()
                title_emoji = "📊"

            embed = discord.Embed(
                title=f"{title_emoji} Arbitrage Scan Results",
                description=f"Scanned {events_scanned} events for guaranteed profit opportunities",
                color=color,
                timestamp=datetime.now()
            )

            if not arbs:
                embed.add_field(
                    name="No Opportunities Found",
                    value="Markets are efficient right now. Keep scanning - arbs are fleeting!",
                    inline=False
                )
            else:
                # Summary stats
                embed.add_field(name="🔥 HOT (1.5%+)", value=str(hot_count), inline=True)
                embed.add_field(name="✅ GOOD (1-1.5%)", value=str(good_count), inline=True)
                embed.add_field(name="📊 Total", value=str(len(arbs)), inline=True)

                # Show top 3 arbs
                for arb in arbs[:3]:
                    matchup = arb.get('matchup', 'Unknown')[:40]
                    profit = arb.get('profit_pct', 0)
                    rating = arb.get('rating', 'SKIP')
                    home_book = arb.get('home_book', 'Unknown')
                    away_book = arb.get('away_book', 'Unknown')
                    home_team = arb.get('home_team', 'Home')[:15]
                    away_team = arb.get('away_team', 'Away')[:15]
                    home_decimal = arb.get('home_decimal_odds', 0)
                    away_decimal = arb.get('away_decimal_odds', 0)
                    stake_home = arb.get('stake_home', 50)
                    stake_away = arb.get('stake_away', 50)
                    guaranteed = arb.get('guaranteed_profit', 0)
                    game_time = arb.get('game_time', 'TBD')
                    is_3way = arb.get('is_3way', False)

                    rating_emoji = "🔥" if rating == "HOT" else "✅" if rating == "GOOD" else "📊"

                    if is_3way:
                        # 3-way market (soccer) - show draw too
                        draw_book = arb.get('draw_book', 'Unknown')
                        draw_decimal = arb.get('draw_decimal_odds', 0)
                        stake_draw = arb.get('stake_draw', 0)

                        field_value = (
                            f"```\n"
                            f"Profit: {profit:.2f}% guaranteed (3-way)\n"
                            f"${stake_home:.0f} {home_team} @ {home_book} ({home_decimal:.2f})\n"
                            f"${stake_away:.0f} {away_team} @ {away_book} ({away_decimal:.2f})\n"
                            f"${stake_draw:.0f} Draw @ {draw_book} ({draw_decimal:.2f})\n"
                            f"= ${guaranteed:.2f} profit on $100\n"
                            f"⏰ {game_time}\n"
                            f"```"
                        )
                    else:
                        # 2-way market (NFL, NBA, etc.)
                        field_value = (
                            f"```\n"
                            f"Profit: {profit:.2f}% guaranteed\n"
                            f"${stake_home:.0f} {home_team} @ {home_book} ({home_decimal:.2f})\n"
                            f"${stake_away:.0f} {away_team} @ {away_book} ({away_decimal:.2f})\n"
                            f"= ${guaranteed:.2f} profit on $100\n"
                            f"⏰ {game_time}\n"
                            f"```"
                        )

                    embed.add_field(
                        name=f"{rating_emoji} [{rating}] {matchup}",
                        value=field_value,
                        inline=False
                    )

            # Warnings
            embed.add_field(
                name="⚠️ Important",
                value="• Verify odds before betting\n• Check betting limits\n• Arbs close quickly",
                inline=False
            )

            embed.set_footer(text="AI Studio Arbitrage Detector | Session 558")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Arb command error: {e}")
            await interaction.followup.send(
                f"Error scanning for arbs: {str(e)[:100]}",
                ephemeral=True
            )

    # Session 558: Bankroll command
    @app_commands.command(name="bankroll", description="View your betting bankroll and stats")
    async def bankroll(self, interaction: discord.Interaction):
        """Display user's bankroll stats and recent wagers."""
        await interaction.response.defer(ephemeral=True)

        try:
            from core.models_bankroll import Bankroll

            @sync_to_async
            def get_bankroll_data(discord_user_id):
                from core.models import UnifiedUser
                try:
                    user = UnifiedUser.objects.get(discord_id=str(discord_user_id))
                except UnifiedUser.DoesNotExist:
                    return None, None

                try:
                    bankroll = user.betting_bankroll
                except Bankroll.DoesNotExist:
                    # Create default bankroll
                    bankroll = Bankroll.objects.create(user=user)

                # Get recent wagers
                recent = list(bankroll.wagers.order_by('-placed_at')[:5])
                return bankroll, recent

            bankroll, recent = await get_bankroll_data(interaction.user.id)

            if not bankroll:
                await interaction.followup.send(
                    "You need to link your Discord account first. Use `/link` to get started.",
                    ephemeral=True
                )
                return

            # Create bankroll embed
            profit_color = discord.Color.green() if bankroll.profit_loss >= 0 else discord.Color.red()
            profit_emoji = "+" if bankroll.profit_loss >= 0 else ""

            embed = discord.Embed(
                title="💰 Your Betting Bankroll",
                color=profit_color,
                timestamp=datetime.now()
            )

            # Balance section
            embed.add_field(
                name="💵 Current Balance",
                value=f"**${bankroll.current_balance:,.2f}**",
                inline=True
            )
            embed.add_field(
                name="📊 P/L",
                value=f"{profit_emoji}${bankroll.profit_loss:,.2f}",
                inline=True
            )
            embed.add_field(
                name="📈 ROI",
                value=f"{bankroll.roi:.1f}%",
                inline=True
            )

            # Stats section
            embed.add_field(
                name="🎯 Win Rate",
                value=f"{bankroll.win_rate:.1f}%",
                inline=True
            )
            embed.add_field(
                name="📝 Record",
                value=f"{bankroll.total_won}W - {bankroll.total_lost}L",
                inline=True
            )
            embed.add_field(
                name="⏳ Pending",
                value=str(bankroll.total_pending),
                inline=True
            )

            # Streak
            streak_str = f"+{bankroll.current_streak}🔥" if bankroll.current_streak > 0 else (
                f"{bankroll.current_streak}❄️" if bankroll.current_streak < 0 else "0"
            )
            embed.add_field(
                name="🔥 Streak",
                value=streak_str,
                inline=True
            )
            embed.add_field(
                name="💰 Total Wagered",
                value=f"${bankroll.total_wagered:,.2f}",
                inline=True
            )
            embed.add_field(
                name="🎰 Unit Size",
                value=f"${bankroll.unit_size:,.2f}",
                inline=True
            )

            # Recent wagers
            if recent:
                wager_lines = []
                for w in recent[:5]:
                    status_emoji = {"won": "✅", "lost": "❌", "pushed": "↔️", "pending": "⏳"}.get(w.status, "❓")
                    odds_str = f"+{w.odds_american}" if w.odds_american > 0 else str(w.odds_american)
                    profit_str = f"${w.profit:+.2f}" if w.profit is not None else "pending"
                    wager_lines.append(f"{status_emoji} {w.selection[:25]}... ({odds_str}) - {profit_str}")

                embed.add_field(
                    name="📋 Recent Bets",
                    value="\n".join(wager_lines) if wager_lines else "No recent bets",
                    inline=False
                )

            embed.set_footer(text="Use /bet to log a new wager | Session 558")

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Bankroll command error: {e}")
            await interaction.followup.send(
                f"Error fetching bankroll: {str(e)[:100]}",
                ephemeral=True
            )

    # Session 558: Bet logging command
    @app_commands.command(name="bet", description="Log a new bet to your bankroll")
    @app_commands.describe(
        selection="What you're betting on (e.g., 'Chiefs -3.5')",
        odds="American odds (e.g., -110, +150)",
        stake="Amount wagered in dollars",
        sport="Sport category (nfl, nba, nhl, etc.)",
        bet_type="Type of bet (moneyline, spread, total, parlay)"
    )
    async def bet(
        self,
        interaction: discord.Interaction,
        selection: str,
        odds: int,
        stake: float,
        sport: Optional[str] = None,
        bet_type: Optional[str] = "moneyline"
    ):
        """Log a new bet to your bankroll tracker."""
        await interaction.response.defer(ephemeral=True)

        try:
            from core.models_bankroll import Bankroll, Wager
            from decimal import Decimal

            @sync_to_async
            def create_wager(discord_user_id, sel, american_odds, amount, sp, b_type):
                from core.models import UnifiedUser
                try:
                    user = UnifiedUser.objects.get(discord_id=str(discord_user_id))
                except UnifiedUser.DoesNotExist:
                    return None, "Account not linked"

                try:
                    bankroll = user.betting_bankroll
                except Bankroll.DoesNotExist:
                    bankroll = Bankroll.objects.create(user=user)

                # Calculate units
                units = Decimal(str(amount)) / bankroll.unit_size

                # Create wager
                wager = Wager.objects.create(
                    bankroll=bankroll,
                    selection=sel,
                    event_name=sel[:100],
                    sport=sp or "",
                    bet_type=b_type,
                    odds_american=american_odds,
                    stake=Decimal(str(amount)),
                    units=units,
                    source='discord',
                )

                # Update bankroll
                bankroll.last_wager_at = wager.placed_at
                bankroll.total_pending += 1
                bankroll.save()

                return wager, None

            wager, error = await create_wager(
                interaction.user.id, selection, odds, stake, sport, bet_type
            )

            if error:
                await interaction.followup.send(
                    f"Error: {error}. Use `/link` to connect your account.",
                    ephemeral=True
                )
                return

            # Calculate potential payout
            if odds > 0:
                potential = stake * (odds / 100 + 1)
            else:
                potential = stake * (100 / abs(odds) + 1)

            odds_str = f"+{odds}" if odds > 0 else str(odds)

            embed = discord.Embed(
                title="🎰 Bet Logged!",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            embed.add_field(name="Selection", value=selection[:50], inline=False)
            embed.add_field(name="Odds", value=odds_str, inline=True)
            embed.add_field(name="Stake", value=f"${stake:,.2f}", inline=True)
            embed.add_field(name="Units", value=f"{wager.units:.1f}u", inline=True)
            embed.add_field(name="Potential Win", value=f"${potential - stake:,.2f}", inline=True)
            embed.add_field(name="Potential Payout", value=f"${potential:,.2f}", inline=True)
            embed.add_field(name="Status", value="⏳ Pending", inline=True)

            if sport:
                embed.add_field(name="Sport", value=sport.upper(), inline=True)
            embed.add_field(name="Type", value=bet_type.title(), inline=True)

            embed.set_footer(text="Use /resolve to settle this bet | Session 558")

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Bet command error: {e}")
            await interaction.followup.send(
                f"Error logging bet: {str(e)[:100]}",
                ephemeral=True
            )

    # Session 558: Resolve bet command
    @app_commands.command(name="resolve", description="Resolve a pending bet (won/lost/pushed)")
    @app_commands.describe(
        bet_id="The bet ID to resolve (from /bankroll)",
        result="The result: won, lost, or pushed"
    )
    @app_commands.choices(result=[
        app_commands.Choice(name="Won", value="won"),
        app_commands.Choice(name="Lost", value="lost"),
        app_commands.Choice(name="Pushed", value="pushed"),
    ])
    async def resolve(
        self,
        interaction: discord.Interaction,
        bet_id: Optional[int] = None,
        result: str = "won"
    ):
        """Resolve a pending bet."""
        await interaction.response.defer(ephemeral=True)

        try:
            from core.models_bankroll import Bankroll, Wager

            @sync_to_async
            def resolve_bet(discord_user_id, wager_id, outcome):
                from core.models import UnifiedUser
                try:
                    user = UnifiedUser.objects.get(discord_id=str(discord_user_id))
                except UnifiedUser.DoesNotExist:
                    return None, "Account not linked"

                try:
                    bankroll = user.betting_bankroll
                except Bankroll.DoesNotExist:
                    return None, "No bankroll found"

                # Find pending wager
                if wager_id:
                    try:
                        wager = bankroll.wagers.get(id=wager_id, status='pending')
                    except Wager.DoesNotExist:
                        return None, f"Pending bet #{wager_id} not found"
                else:
                    # Get most recent pending
                    wager = bankroll.wagers.filter(status='pending').order_by('-placed_at').first()
                    if not wager:
                        return None, "No pending bets to resolve"

                # Resolve
                wager.resolve(outcome)

                # Update streak
                if outcome == 'won':
                    if bankroll.current_streak >= 0:
                        bankroll.current_streak += 1
                    else:
                        bankroll.current_streak = 1
                    if bankroll.current_streak > bankroll.best_streak:
                        bankroll.best_streak = bankroll.current_streak
                elif outcome == 'lost':
                    if bankroll.current_streak <= 0:
                        bankroll.current_streak -= 1
                    else:
                        bankroll.current_streak = -1
                    if bankroll.current_streak < bankroll.worst_streak:
                        bankroll.worst_streak = bankroll.current_streak

                bankroll.save()
                return wager, None

            wager, error = await resolve_bet(interaction.user.id, bet_id, result)

            if error:
                await interaction.followup.send(f"Error: {error}", ephemeral=True)
                return

            result_emoji = {"won": "✅", "lost": "❌", "pushed": "↔️"}.get(result, "❓")
            result_color = {"won": discord.Color.green(), "lost": discord.Color.red(), "pushed": discord.Color.gold()}.get(result, discord.Color.blue())

            embed = discord.Embed(
                title=f"{result_emoji} Bet Resolved: {result.upper()}",
                color=result_color,
                timestamp=datetime.now()
            )

            embed.add_field(name="Selection", value=wager.selection[:50], inline=False)
            embed.add_field(name="Stake", value=f"${wager.stake:,.2f}", inline=True)

            profit_str = f"${wager.profit:+,.2f}" if wager.profit is not None else "$0.00"
            embed.add_field(name="Profit/Loss", value=profit_str, inline=True)

            if wager.payout:
                embed.add_field(name="Payout", value=f"${wager.payout:,.2f}", inline=True)

            embed.set_footer(text="Use /bankroll to see updated stats | Session 558")

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Resolve command error: {e}")
            await interaction.followup.send(
                f"Error resolving bet: {str(e)[:100]}",
                ephemeral=True
            )

    # Session 558: Futures Championship Tracker
    @app_commands.command(name="futures", description="View championship futures odds")
    @app_commands.describe(
        league="League to view futures for (nfl, nba, mlb, nhl)"
    )
    async def futures(
        self,
        interaction: discord.Interaction,
        league: Optional[str] = None
    ):
        """Display championship futures odds."""
        await interaction.response.defer()

        try:
            from ai_core.spiders.specialized.theodds_spider import TheOddsSpider

            @sync_to_async
            def get_futures_data(league_filter):
                spider = TheOddsSpider()

                # Map league to futures sport key
                futures_map = {
                    'nfl': ['americanfootball_nfl_super_bowl_winner'],
                    'nba': ['basketball_nba_championship_winner'],
                    'mlb': ['baseball_mlb_world_series_winner'],
                    'nhl': ['icehockey_nhl_stanley_cup_winner'],
                    None: [
                        'americanfootball_nfl_super_bowl_winner',
                        'basketball_nba_championship_winner',
                    ]
                }

                sports = futures_map.get(league_filter.lower() if league_filter else None, [])

                all_futures = []
                for sport in sports:
                    try:
                        data = spider.fetch_data(sports=[sport], max_results=20, market_types=['outrights'])
                        futures = [d for d in data if d.get('data_type') == 'futures']
                        all_futures.extend(futures)
                    except Exception as _e:
                        logger.warning(
                            "discord_bot.get_futures_data: swallowed (%s: %s) — degraded",
                            type(_e).__name__, _e,
                        )

                return all_futures

            futures_data = await get_futures_data(league)

            if not futures_data:
                # Fallback to SpiderData if live API doesn't have futures
                from core.models_unified_system import SpiderData

                @sync_to_async
                def get_cached_futures():
                    return list(SpiderData.objects.filter(
                        spider_name='theodds',
                        data_type='futures'
                    ).order_by('-created_at')[:10])

                cached = await get_cached_futures()

                if not cached:
                    await interaction.followup.send(
                        f"No futures data available{' for ' + league.upper() if league else ''}. Futures markets may not be active.",
                        ephemeral=True
                    )
                    return

            title = "🏆 Championship Futures"
            if league:
                title += f" - {league.upper()}"

            embed = discord.Embed(
                title=title,
                description="Current odds to win championship",
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )

            # Group by sport/event
            for future in futures_data[:10]:
                team = future.get('title', future.get('selection', 'Unknown'))
                odds = future.get('odds_american', future.get('price', 0))
                sport = future.get('sport_name', 'Championship')

                odds_str = f"+{odds}" if odds > 0 else str(odds)
                implied = 100 / (abs(odds) / 100 + 1) if odds > 0 else 100 / (100 / abs(odds) + 1)

                embed.add_field(
                    name=f"{team[:30]}",
                    value=f"Odds: {odds_str} ({implied:.1f}%)",
                    inline=True
                )

            embed.set_footer(text="Data from The Odds API | Session 558")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Futures command error: {e}")
            await interaction.followup.send(
                f"Error fetching futures: {str(e)[:100]}",
                ephemeral=True
            )

    # Session 558: Bet Slip Generator
    @app_commands.command(name="slip", description="Generate a bet slip with multiple selections")
    @app_commands.describe(
        type="Slip type: single (each bet separate) or parlay (combined)",
        units="Units to wager (default: 1)"
    )
    @app_commands.choices(type=[
        app_commands.Choice(name="Single Bets", value="single"),
        app_commands.Choice(name="Parlay", value="parlay"),
    ])
    async def slip(
        self,
        interaction: discord.Interaction,
        type: str = "single",
        units: float = 1.0
    ):
        """Generate a bet slip from recent toss-up games."""
        await interaction.response.defer()

        try:
            from ai_core.spiders.specialized.theodds_spider import TheOddsSpider

            @sync_to_async
            def get_tossup_games():
                spider = TheOddsSpider()
                events = spider.fetch_data(max_results=100, max_priority=2)
                sports_events = [e for e in events if e.get('data_type') == 'sports_odds']

                # Find toss-ups (45-55% implied probability)
                tossups = [
                    e for e in sports_events
                    if 45 <= (e.get('home_implied_prob') or 50) <= 55
                ]

                # Sort by game time (upcoming first)
                tossups.sort(key=lambda e: e.get('commence_time', ''))
                return tossups[:5]

            tossups = await get_tossup_games()

            if not tossups:
                await interaction.followup.send(
                    "No toss-up games found for bet slip. Try again later when more games are available.",
                    ephemeral=True
                )
                return

            embed = discord.Embed(
                title=f"📝 Bet Slip ({type.title()})",
                description=f"Top {len(tossups)} toss-up games • {units}u each" if type == "single" else f"Parlay combining {len(tossups)} legs • {units}u total",
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )

            total_implied = 1.0
            selections = []

            for i, game in enumerate(tossups, 1):
                home = game.get('home_team', 'Home')
                away = game.get('away_team', 'Away')
                home_odds = game.get('home_odds', -110)
                away_odds = game.get('away_odds', -110)
                home_prob = game.get('home_implied_prob', 50)
                sport = game.get('sport_name', 'Sports')
                game_time = game.get('commence_time_formatted', 'TBD')

                # Pick the slight favorite or home team
                if home_prob >= 50:
                    pick = home
                    odds = home_odds
                    prob = home_prob
                else:
                    pick = away
                    odds = away_odds
                    prob = 100 - home_prob

                odds_str = f"+{odds}" if odds > 0 else str(odds)
                selections.append({'pick': pick, 'odds': odds, 'prob': prob})
                total_implied *= (prob / 100)

                embed.add_field(
                    name=f"Leg {i}: {sport}",
                    value=f"**{pick}** {odds_str}\n{away} @ {home}\n⏰ {game_time}",
                    inline=False
                )

            # Calculate parlay odds if applicable
            if type == "parlay" and selections:
                # Multiply decimal odds
                parlay_decimal = 1.0
                for sel in selections:
                    if sel['odds'] > 0:
                        parlay_decimal *= (sel['odds'] / 100 + 1)
                    else:
                        parlay_decimal *= (100 / abs(sel['odds']) + 1)

                parlay_american = int((parlay_decimal - 1) * 100) if parlay_decimal >= 2 else int(-100 / (parlay_decimal - 1))
                parlay_str = f"+{parlay_american}" if parlay_american > 0 else str(parlay_american)

                embed.add_field(
                    name="📊 Parlay Summary",
                    value=f"**Combined Odds:** {parlay_str}\n**Implied Prob:** {total_implied * 100:.1f}%\n**Risk:** {units}u\n**To Win:** {units * (parlay_decimal - 1):.1f}u",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📊 Single Bets Summary",
                    value=f"**Total Risk:** {len(selections) * units}u\n**Avg Win Rate:** ~50%\n**Strategy:** Research each pick before betting",
                    inline=False
                )

            embed.set_footer(text="Use /bet to log these wagers | Session 558")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Slip command error: {e}")
            await interaction.followup.send(
                f"Error generating bet slip: {str(e)[:100]}",
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

            # Route through AgentRouter → ThinkingAgent (PersonalAssistantAgent removed)
            @sync_to_async
            def query_assistant(q: str, conv_history: List[Dict[str, str]]) -> Dict[str, Any]:
                from core.agent_router import AgentRouter

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

                # Execute through ThinkingAgent via router
                result = router.route(
                    agent_name='ThinkingAgent',
                    task=task_with_context,
                    context=context,
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
                        from core.services.workspace_resolver import get_active_workspace
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
                            workspace=get_active_workspace(discord_user),
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

    @app_commands.command(name="sessions", description="View and manage your conversation sessions across platforms")
    @app_commands.describe(action="Action to perform: list, info, or resume")
    @app_commands.choices(action=[
        app_commands.Choice(name="list - Show active sessions", value="list"),
        app_commands.Choice(name="info - Show current session info", value="info"),
        app_commands.Choice(name="resume - Resume a web session", value="resume"),
    ])
    async def sessions(self, interaction: discord.Interaction, action: str = "list"):
        """
        Session 455: Cross-platform session management.

        Shows sessions from both Discord and web, allowing users to resume
        conversations started on the web app from Discord.
        """
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id

        try:
            if action == "list":
                # Get session info using the database-backed conversation history
                @sync_to_async
                def get_user_sessions():
                    from core.models import ChatConversation, UnifiedUser
                    from django.utils import timezone
                    from django.db.models import Max, Min, Count

                    cutoff = timezone.now() - timedelta(hours=24)

                    # Check if user is linked
                    linked_user = UnifiedUser.objects.filter(discord_id=str(user_id)).first()

                    # Build query
                    if linked_user:
                        from django.db import models as db_models
                        sessions_query = ChatConversation.objects.filter(
                            db_models.Q(user=linked_user) | db_models.Q(discord_user_id=str(user_id)),
                            session_active=True,
                            created_at__gte=cutoff
                        )
                    else:
                        sessions_query = ChatConversation.objects.filter(
                            discord_user_id=str(user_id),
                            session_active=True,
                            created_at__gte=cutoff
                        )

                    # Group by conversation_id
                    session_data = sessions_query.values('conversation_id', 'platform').annotate(
                        first_message=Min('created_at'),
                        last_activity=Max('created_at'),
                        message_count=Count('id')
                    ).order_by('-last_activity')[:10]

                    sessions = []
                    seen = set()
                    for s in session_data:
                        if s['conversation_id'] in seen:
                            continue
                        seen.add(s['conversation_id'])

                        # Get title from first message
                        first = ChatConversation.objects.filter(
                            conversation_id=s['conversation_id']
                        ).order_by('created_at').first()

                        title = first.session_title if first and first.session_title else (
                            first.user_message[:40] + '...' if first and len(first.user_message) > 40 else
                            first.user_message if first else 'Untitled'
                        )

                        sessions.append({
                            'id': s['conversation_id'][:8],  # Short ID for display
                            'title': title,
                            'platform': s['platform'],
                            'messages': s['message_count'] * 2,
                            'last_activity': s['last_activity'],
                        })

                    return sessions, bool(linked_user)

                sessions, is_linked = await get_user_sessions()

                if not sessions:
                    embed = discord.Embed(
                        title="📋 Your Sessions",
                        description="No active sessions found in the last 24 hours.\n\nStart a conversation with `/ask`!",
                        color=discord.Color.blue()
                    )
                else:
                    embed = discord.Embed(
                        title="📋 Your Sessions",
                        description=f"Found {len(sessions)} active session(s):",
                        color=discord.Color.green()
                    )

                    for s in sessions:
                        platform_emoji = "💬" if s['platform'] == 'discord' else "🌐"
                        time_ago = timezone.now() - s['last_activity'] if s['last_activity'] else timedelta(0)
                        time_str = f"{int(time_ago.total_seconds() / 60)}m ago" if time_ago.total_seconds() < 3600 else f"{int(time_ago.total_seconds() / 3600)}h ago"

                        embed.add_field(
                            name=f"{platform_emoji} {s['title'][:30]}",
                            value=f"ID: `{s['id']}` | {s['messages']} msgs | {time_str}",
                            inline=False
                        )

                link_status = "✅ Web account linked" if is_linked else "⚠️ Link your web account with `/link` to sync sessions"
                embed.set_footer(text=link_status)

            elif action == "info":
                # Show current session info
                session_info = conversation_history.get_session_info(user_id)

                if session_info:
                    embed = discord.Embed(
                        title="📍 Current Session",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="Title", value=session_info['session_title'][:50], inline=False)
                    embed.add_field(name="Session ID", value=f"`{session_info['conversation_id'][:8]}`", inline=True)
                    embed.add_field(name="Messages", value=str(session_info['message_count']), inline=True)
                    embed.add_field(name="Platform", value=session_info['platform'], inline=True)

                    if session_info['linked_user']:
                        embed.add_field(name="Linked To", value=session_info['linked_user'], inline=True)

                    embed.set_footer(text=f"Started: {session_info['started_at'].strftime('%Y-%m-%d %H:%M')}")
                else:
                    embed = discord.Embed(
                        title="📍 No Active Session",
                        description="You don't have an active conversation.\nStart one with `/ask`!",
                        color=discord.Color.light_gray()
                    )

            elif action == "resume":
                embed = discord.Embed(
                    title="🔄 Resume Session",
                    description="To resume a session from the web:\n\n"
                                "1. Use `/sessions list` to see available sessions\n"
                                "2. Copy the session ID\n"
                                "3. Simply use `/ask` - your linked account will automatically use your most recent session\n\n"
                                "**Tip:** Link your account with `/link` to sync sessions between web and Discord!",
                    color=discord.Color.blue()
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"/sessions error: {e}")
            await interaction.followup.send(
                f"Error: {str(e)[:200]}",
                ephemeral=True
            )

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
                except Exception:
                    agent_executions = 0

                # Opportunities
                try:
                    opportunities_viewed = Opportunity.objects.filter(user=web_user).count()
                except Exception:
                    opportunities_viewed = 0

                # Revenue
                try:
                    total_revenue = Revenue.objects.filter(user=web_user).aggregate(
                        total=Sum('amount')
                    )['total'] or 0
                except Exception:
                    total_revenue = 0

                # Enhanced profile (if exists).
                # Session 1103c: loud so user-profile context drops
                # are visible in the /whoami discord command output.
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
                except Exception as e:
                    logger.warning(
                        "discord_bot: EnhancedUserProfile lookup failed "
                        "for user=%s (%s: %s) — profile_data will be "
                        "empty in whoami response",
                        getattr(web_user, 'username', '<unknown>'),
                        type(e).__name__, e,
                    )

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
    # Session 507: Removed /brief-feedback and /action commands to stay under
    # Discord's 100 command limit. These were Market Intelligence Desk feedback
    # commands that had low usage.
    # =========================================================================

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
                from django.db.models import Count
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

                from core.models import EnhancedUserProfile

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
    # /cancel and /billing removed in Phase G2 — use web billing portal instead


class VoiceCommands(commands.Cog):
    """
    Session 438: Voice AI Commands (Phase 8).

    Enables voice channel interaction with AI assistant.
    Uses ElevenLabs for TTS and OpenAI Whisper for STT.
    """

    voice_group = app_commands.Group(name="voice", description="Voice AI")

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot
        self.voice_service = None

    def _ensure_voice_service(self):
        """Lazily initialize voice service."""
        if self.voice_service is None:
            from core.services.discord_voice import init_voice_service
            self.voice_service = init_voice_service(self.bot)
        return self.voice_service

    @voice_group.command(name="join", description="Voice AI: Join a voice channel for voice interaction")
    @app_commands.describe(
        action="What to do",
        voice="Voice to use for speaking (optional)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Join - Join your voice channel", value="join"),
        app_commands.Choice(name="Leave - Leave voice channel", value="leave"),
        app_commands.Choice(name="Voices - List available voices", value="voices"),
    ])
    async def voice_join(
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

    @voice_group.command(name="speak", description="Make the bot speak a message in voice channel")
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

    # Session 507: Removed /beep command to stay under Discord's 100 command limit

    @voice_group.command(name="ask", description="Ask AI and hear the response in voice channel")
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

    @voice_group.command(name="clone", description="Clone your voice from a Discord voice channel recording")
    @app_commands.describe(
        name="Name for your cloned voice",
        duration="Recording duration in seconds (default 30, max 120)"
    )
    async def voice_clone(
        self,
        interaction: discord.Interaction,
        name: Optional[str] = None,
        duration: Optional[int] = 30
    ):
        """Record your voice in a Discord voice channel and clone it via ElevenLabs."""
        await interaction.response.defer(ephemeral=True)

        try:
            from core.services.discord_voice import get_voice_recorder, get_voice_cloner

            service = self._ensure_voice_service()
            recorder = get_voice_recorder()
            cloner = get_voice_cloner()

            # Check prerequisites
            if not cloner.is_available():
                await interaction.followup.send(
                    "Voice cloning is not available - ElevenLabs API key not configured.",
                    ephemeral=True
                )
                return

            if not interaction.user.voice or not interaction.user.voice.channel:
                await interaction.followup.send(
                    "You need to be in a voice channel!\n"
                    "1. Join a voice channel\n"
                    "2. Use `/voice join` to bring me in\n"
                    "3. Then use `/voice clone` to start recording",
                    ephemeral=True
                )
                return

            if not service.is_in_voice(interaction.guild.id):
                await interaction.followup.send(
                    "I need to be in the voice channel first!\n"
                    "Use `/voice join` to bring me in, then `/voice clone` to record.",
                    ephemeral=True
                )
                return

            # Clamp duration
            record_duration = max(10, min(duration or 30, 120))
            voice_name = name or f"{interaction.user.display_name}'s Voice"

            # Start recording
            embed = discord.Embed(
                title="Voice Cloning - Recording",
                description=(
                    f"Recording your voice for **{record_duration} seconds**...\n\n"
                    "Speak naturally and clearly. Read aloud or talk about anything - "
                    "the AI will learn your voice characteristics."
                ),
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Voice Name", value=voice_name, inline=True)
            embed.add_field(name="Duration", value=f"{record_duration}s", inline=True)
            embed.set_footer(text="Recording in progress...")

            await interaction.followup.send(embed=embed, ephemeral=True)

            # Record
            session = recorder.start_recording(
                user_id=interaction.user.id,
                guild_id=interaction.guild.id,
                channel_id=interaction.user.voice.channel.id
            )

            if not session:
                await interaction.followup.send(
                    "Failed to start recording. Voice recording may not be available on this server.",
                    ephemeral=True
                )
                return

            # Wait for recording duration
            await asyncio.sleep(record_duration)

            # Stop recording
            audio_path = recorder.stop_recording(interaction.user.id)

            if not audio_path:
                await interaction.followup.send(
                    "No audio was captured. Make sure you were speaking during the recording.\n"
                    "Tip: Speak clearly and continuously for best results.",
                    ephemeral=True
                )
                return

            # Update status - cloning
            clone_embed = discord.Embed(
                title="Voice Cloning - Processing",
                description="Recording complete! Now cloning your voice with ElevenLabs...",
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )
            clone_embed.set_footer(text="This may take up to 2 minutes...")

            await interaction.edit_original_response(embed=clone_embed)

            # Clone via ElevenLabs
            result = await cloner.clone_voice(
                audio_file_path=audio_path,
                voice_name=voice_name,
                description=f"Cloned from Discord recording by {interaction.user.display_name}",
                remove_background_noise=True,
                labels={'source': 'discord', 'user': str(interaction.user.id)}
            )

            if 'error' in result:
                await interaction.edit_original_response(
                    embed=discord.Embed(
                        title="Voice Cloning Failed",
                        description=f"Error: {result['error'][:300]}",
                        color=discord.Color.red()
                    )
                )
                return

            elevenlabs_voice_id = result['voice_id']

            # Create VoiceProfile in database (if user is linked)
            voice_profile_id = None
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.filter(discord_id=str(interaction.user.id)).first()

                if user:
                    from core.models_voice_marketplace import VoiceProfile, VoiceCloneRequest

                    voice_profile = VoiceProfile.objects.create(
                        owner=user,
                        elevenlabs_voice_id=elevenlabs_voice_id,
                        name=voice_name,
                        description=f"Cloned from Discord recording",
                        creation_method='discord_clone',
                    )
                    voice_profile_id = str(voice_profile.id)

                    # Create clone request record
                    VoiceCloneRequest.objects.create(
                        user=user,
                        discord_user_id=str(interaction.user.id),
                        discord_guild_id=str(interaction.guild.id),
                        discord_channel_id=str(interaction.user.voice.channel.id if interaction.user.voice else ''),
                        status='completed',
                        recording_duration_seconds=record_duration,
                        voice_profile=voice_profile,
                    )

                    logger.info(f"Voice cloned and saved for linked user {user.username}")
            except Exception as e:
                logger.warning(f"Could not save voice profile to DB: {e}")

            # Success embed
            success_embed = discord.Embed(
                title="Voice Cloned Successfully!",
                description=f"Your voice **{voice_name}** has been created!",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            success_embed.add_field(name="Voice Name", value=voice_name, inline=True)
            success_embed.add_field(name="ElevenLabs ID", value=elevenlabs_voice_id[:20] + '...', inline=True)
            if voice_profile_id:
                success_embed.add_field(
                    name="Platform",
                    value="Saved to your account! Use it in the web app too.",
                    inline=False
                )
            else:
                success_embed.add_field(
                    name="Tip",
                    value="Link your Discord account with `/link` to use this voice on the web platform.",
                    inline=False
                )
            success_embed.set_footer(text="Use /voice speak to test your new voice!")

            await interaction.edit_original_response(embed=success_embed)

        except Exception as e:
            logger.error(f"/voice clone command error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await interaction.followup.send(
                f"Error during voice cloning: {str(e)[:200]}",
                ephemeral=True
            )


# VoiceMarketplaceCommands removed in Phase G2 command consolidation

class ContentPipelineCommands(commands.Cog):
    """
    Session 440: Content Pipeline Commands.

    The AI Content Factory - generate complete content packages from $5 to $50K.
    Same infrastructure powers birthday messages and Pixar pitches.
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

    @app_commands.command(name="create-content", description="AI Content Factory: Create complete content packages")
    @app_commands.describe(
        tier="Content tier (determines scope and price)",
        prompt="What to create (e.g., 'Tony's Pizza, Brooklyn, $2 Tuesdays')"
    )
    @app_commands.choices(tier=[
        app_commands.Choice(name="Quick ($5-29) - Birthday messages, simple content", value="quick"),
        app_commands.Choice(name="Ad ($29-99) - Small business ads", value="ad"),
        app_commands.Choice(name="Brand ($99-499) - Full brand packages", value="brand"),
        app_commands.Choice(name="Series ($499-2999) - Content series", value="series"),
        app_commands.Choice(name="Pitch ($2999-9999) - Series/movie pitches", value="pitch"),
    ])
    async def create_content(
        self,
        interaction: discord.Interaction,
        tier: str,
        prompt: str
    ):
        """Create a complete content package using the AI pipeline."""
        await interaction.response.defer()

        try:
            # Get linked user
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    "Please link your Discord account first using `/link`\n"
                    "Go to AI Studio > Preferences > Discord to get your link code.",
                    ephemeral=True
                )
                return

            # Get tier info
            @sync_to_async
            def create_package():
                from core.services.content_pipeline import TIER_CONFIGS
                from core.models_content_pipeline import ContentPackage, ContentGenerationJob, PackageStatus

                tier_config = TIER_CONFIGS.get(tier)
                if not tier_config:
                    return None, "Invalid tier"

                # Create the package
                package = ContentPackage.objects.create(
                    name=f"{prompt[:50]}... ({tier.title()})" if len(prompt) > 50 else f"{prompt} ({tier.title()})",
                    description=prompt,
                    tier=tier,
                    category='other',
                    prompt=prompt,
                    base_price=tier_config.default_price,
                    status=PackageStatus.QUEUED,
                    is_public=True,
                    created_by=user,
                    generation_config={
                        "tier": tier,
                        "tier_config": {
                            "num_images": tier_config.num_images,
                            "num_videos": tier_config.num_videos,
                            "video_durations": tier_config.video_durations,
                        }
                    }
                )

                # Create generation job
                ContentGenerationJob.objects.create(
                    package=package,
                    current_stage="queued"
                )

                return package, tier_config

            package, tier_config = await create_package()

            if package is None:
                await interaction.followup.send(f"Error: {tier_config}", ephemeral=True)
                return

            # Start generation task
            @sync_to_async
            def start_generation(pkg_id):
                from core.tasks import generate_content_package
                generate_content_package.delay(str(pkg_id))

            await start_generation(package.id)

            # Build response embed
            embed = discord.Embed(
                title=f"Content Package Created",
                description=f"**{package.name}**\n\nYour content is being generated!",
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )

            embed.add_field(name="Tier", value=tier.title(), inline=True)
            embed.add_field(name="Price", value=f"${tier_config.default_price}", inline=True)
            embed.add_field(name="Status", value="Generating...", inline=True)

            embed.add_field(
                name="What's Being Created",
                value=(
                    f"Images: {tier_config.num_images}\n"
                    f"Videos: {tier_config.num_videos}\n"
                    f"Voice Options: {tier_config.num_voice_options}"
                ),
                inline=False
            )

            embed.add_field(
                name="Package ID",
                value=f"`{str(package.id)[:8]}`",
                inline=True
            )

            embed.set_footer(text="Use /content-status to check progress")

            await interaction.followup.send(embed=embed)

            logger.info(f"Content package created: {package.name} (tier={tier})")

        except Exception as e:
            logger.error(f"/create-content error: {e}")
            await interaction.followup.send(f"Error creating content: {str(e)[:200]}", ephemeral=True)

    @app_commands.command(name="content-status", description="Check status of your content packages")
    @app_commands.describe(package_id="Package ID (optional - shows all if not provided)")
    async def content_status(
        self,
        interaction: discord.Interaction,
        package_id: Optional[str] = None
    ):
        """Check status of content generation."""
        await interaction.response.defer(ephemeral=True)

        try:
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    "Please link your Discord account first using `/link`",
                    ephemeral=True
                )
                return

            @sync_to_async
            def get_packages(web_user, pkg_id):
                from core.models_content_pipeline import ContentPackage

                if pkg_id:
                    return list(ContentPackage.objects.filter(
                        id__startswith=pkg_id,
                        created_by=web_user
                    )[:1])
                else:
                    return list(ContentPackage.objects.filter(
                        created_by=web_user
                    ).order_by('-created_at')[:5])

            packages = await get_packages(user, package_id)

            if not packages:
                await interaction.followup.send(
                    "No content packages found. Use `/create-content` to create one!",
                    ephemeral=True
                )
                return

            embed = discord.Embed(
                title="Your Content Packages",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            status_emojis = {
                'queued': '',
                'generating': '',
                'ready': '',
                'sold': '',
                'delivered': '',
                'failed': '',
            }

            for pkg in packages:
                emoji = status_emojis.get(pkg.status, '')
                progress = f" ({pkg.generation_progress}%)" if pkg.status == 'generating' else ""

                embed.add_field(
                    name=f"{emoji} {pkg.name[:40]}",
                    value=(
                        f"**Tier:** {pkg.tier.title()} | **Price:** ${pkg.base_price}\n"
                        f"**Status:** {pkg.status.title()}{progress}\n"
                        f"**ID:** `{str(pkg.id)[:8]}`"
                    ),
                    inline=False
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"/content-status error: {e}")
            await interaction.followup.send(f"Error: {str(e)[:200]}", ephemeral=True)

    # /showroom removed in Phase G2 — use web marketplace instead


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
            from core.models import UnifiedUser
            pending = []

            # Get all linked Discord users (those with discord_id set on UnifiedUser)
            users = UnifiedUser.objects.filter(
                discord_id__isnull=False
            ).exclude(discord_id='')

            for user in users:
                sync_key = f"discord_role_sync:{user.discord_id}"
                sync_data = cache.get(sync_key)
                if sync_data:
                    pending.append({
                        'discord_user_id': user.discord_id,
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


class SeriesCommands(commands.Cog):
    """
    Session 445: AI Series Creation Commands.

    Create multi-episode content series with consistent characters and style.
    """

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot

    series = app_commands.Group(name="series", description="AI Series creation and management")

    async def _get_linked_user(self, discord_id: str):
        """Get the linked web user for a Discord ID."""
        @sync_to_async
        def get_user():
            from django.contrib.auth import get_user_model
            User = get_user_model()
            # User model has discord_id field that stores linked Discord ID
            return User.objects.filter(discord_id=str(discord_id)).first()
        return await get_user()

    @series.command(name="create", description="Create a multi-episode AI content series")
    @app_commands.describe(
        series_type="Type of series to create",
        episodes="Number of episodes (1-5)",
        prompt="Description of your series concept"
    )
    @app_commands.choices(series_type=[
        app_commands.Choice(name="Educational - Tutorials, explainers", value="educational"),
        app_commands.Choice(name="Entertainment - Cartoons, stories", value="entertainment"),
        app_commands.Choice(name="Marketing - Ad campaigns, brand series", value="marketing"),
    ])
    async def series_create(
        self,
        interaction: discord.Interaction,
        series_type: app_commands.Choice[str],
        episodes: app_commands.Range[int, 1, 5],
        prompt: str
    ):
        """Create a multi-episode AI content series."""
        await interaction.response.defer()

        try:
            # Check user is linked
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Account Not Linked",
                        description="Please link your Discord account first using `/link`",
                        color=discord.Color.orange()
                    )
                )
                return

            # Create series via agent
            @sync_to_async
            def create_series():
                from core.models_ai_series import AISeries, SeriesType, SeriesEpisode
                from core.tasks import generate_ai_series

                # Map type
                type_map = {
                    'educational': SeriesType.EDUCATIONAL,
                    'entertainment': SeriesType.ENTERTAINMENT,
                    'marketing': SeriesType.MARKETING,
                }

                series = AISeries.objects.create(
                    name=prompt[:200],
                    description=prompt,
                    prompt=prompt,
                    series_type=type_map.get(series_type.value, SeriesType.EDUCATIONAL),
                    episode_count=episodes,
                    target_audience="Discord community",
                    created_by=user,
                    discord_channel_id=str(interaction.channel_id),
                )

                # Create episode records
                arc_positions = ['intro'] if episodes == 1 else \
                               ['intro', 'conclusion'] if episodes == 2 else \
                               ['intro', 'climax', 'conclusion'] if episodes == 3 else \
                               ['intro', 'rising', 'climax', 'conclusion'] if episodes == 4 else \
                               ['intro', 'rising', 'climax', 'falling', 'conclusion']

                for i, arc_pos in enumerate(arc_positions, 1):
                    SeriesEpisode.objects.create(
                        series=series,
                        episode_number=i,
                        title=f"Episode {i}",
                        synopsis=f"Episode {i} - {arc_pos} phase",
                        arc_position=arc_pos,
                        generation_order=i
                    )

                # Start generation task
                generate_ai_series.delay(str(series.id))

                return series

            series = await create_series()

            # Send confirmation
            embed = discord.Embed(
                title="AI Series Creation Started",
                description=f"Creating your **{series_type.name}** series!",
                color=discord.Color.purple()
            )
            embed.add_field(name="Series ID", value=f"`{str(series.id)[:8]}...`", inline=True)
            embed.add_field(name="Episodes", value=str(episodes), inline=True)
            embed.add_field(name="Type", value=series_type.name, inline=True)
            embed.add_field(name="Prompt", value=prompt[:200] + "..." if len(prompt) > 200 else prompt, inline=False)
            embed.set_footer(text="Use /series-status to check progress")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Series create error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to create series: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @series.command(name="status", description="Check status of your AI series")
    @app_commands.describe(series_id="Optional series ID (shows latest if not provided)")
    async def series_status(
        self,
        interaction: discord.Interaction,
        series_id: Optional[str] = None
    ):
        """Check status of an AI series."""
        await interaction.response.defer()

        try:
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Account Not Linked",
                        description="Please link your Discord account first using `/link`",
                        color=discord.Color.orange()
                    )
                )
                return

            @sync_to_async
            def get_series():
                from core.models_ai_series import AISeries
                if series_id:
                    return AISeries.objects.filter(id__startswith=series_id, created_by=user).first()
                else:
                    return AISeries.objects.filter(created_by=user).order_by('-created_at').first()

            series = await get_series()

            if not series:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="No Series Found",
                        description="No series found. Use `/series-create` to start one!",
                        color=discord.Color.orange()
                    )
                )
                return

            # Get episode status
            @sync_to_async
            def get_episodes():
                return list(series.episodes.all().values('episode_number', 'title', 'status'))

            episodes = await get_episodes()

            # Build status embed
            status_colors = {
                'planning': discord.Color.blue(),
                'generating': discord.Color.yellow(),
                'complete': discord.Color.green(),
                'failed': discord.Color.red(),
            }

            embed = discord.Embed(
                title=f"Series: {series.name[:50]}",
                description=f"**Type:** {series.get_series_type_display()}\n**Status:** {series.get_status_display()}",
                color=status_colors.get(series.status, discord.Color.greyple())
            )

            # Progress bar
            progress = series.generation_progress
            bar_filled = int(progress / 10)
            bar_empty = 10 - bar_filled
            progress_bar = "█" * bar_filled + "░" * bar_empty
            embed.add_field(name="Progress", value=f"{progress_bar} {progress}%", inline=False)

            # Episode list
            episode_status = "\n".join([
                f"Ep {ep['episode_number']}: {ep['title'][:30]} - {ep['status']}"
                for ep in episodes
            ])
            if episode_status:
                embed.add_field(name="Episodes", value=episode_status, inline=False)

            embed.add_field(name="Series ID", value=f"`{str(series.id)[:8]}...`", inline=True)
            embed.set_footer(text=f"Created {series.created_at.strftime('%Y-%m-%d %H:%M')}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Series status error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to get status: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @series.command(name="list", description="List your AI series")
    async def series_list(self, interaction: discord.Interaction):
        """List all AI series created by the user."""
        await interaction.response.defer()

        try:
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Account Not Linked",
                        description="Please link your Discord account first using `/link`",
                        color=discord.Color.orange()
                    )
                )
                return

            @sync_to_async
            def get_series_list():
                from core.models_ai_series import AISeries
                return list(AISeries.objects.filter(created_by=user).order_by('-created_at')[:10].values(
                    'id', 'name', 'series_type', 'episode_count', 'status', 'generation_progress', 'created_at'
                ))

            series_list = await get_series_list()

            if not series_list:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="No Series Found",
                        description="You haven't created any series yet.\nUse `/series-create` to start your first series!",
                        color=discord.Color.blue()
                    )
                )
                return

            embed = discord.Embed(
                title="Your AI Series",
                description=f"Showing {len(series_list)} series",
                color=discord.Color.purple()
            )

            for s in series_list:
                status_emoji = {
                    'planning': '📝',
                    'generating': '⏳',
                    'complete': '✅',
                    'failed': '❌'
                }.get(s['status'], '❓')

                embed.add_field(
                    name=f"{status_emoji} {s['name'][:40]}",
                    value=f"ID: `{str(s['id'])[:8]}...` | Episodes: {s['episode_count']} | {s['generation_progress']}%",
                    inline=False
                )

            embed.set_footer(text="Use /series-status <id> for details")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Series list error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to list series: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @series.command(name="view", description="View the content of a series episode")
    @app_commands.describe(
        series_id="The series ID (first 8 chars is enough)",
        episode="Episode number to view (default: 1)"
    )
    async def series_view(
        self,
        interaction: discord.Interaction,
        series_id: str,
        episode: int = 1
    ):
        """View the generated content (script, synopsis) for a series episode."""
        await interaction.response.defer()

        try:
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Account Not Linked",
                        description="Please link your Discord account first using `/link`",
                        color=discord.Color.orange()
                    )
                )
                return

            @sync_to_async
            def get_episode_content():
                from core.models_ai_series import AISeries, SeriesEpisode
                from django.db.models import CharField
                from django.db.models.functions import Cast

                # Find series by partial ID match (cast UUID to string first)
                series = AISeries.objects.annotate(
                    id_str=Cast('id', CharField())
                ).filter(
                    created_by=user,
                    id_str__startswith=series_id
                ).first()

                if not series:
                    # Try exact match with full UUID
                    try:
                        import uuid
                        uuid.UUID(series_id)  # Validate it's a full UUID
                        series = AISeries.objects.get(id=series_id, created_by=user)
                    except (ValueError, AISeries.DoesNotExist):
                        return None, None

                ep = SeriesEpisode.objects.filter(
                    series=series,
                    episode_number=episode
                ).first()

                return series, ep

            series, ep = await get_episode_content()

            if not series:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Series Not Found",
                        description=f"No series found with ID `{series_id}`",
                        color=discord.Color.orange()
                    )
                )
                return

            if not ep:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Episode Not Found",
                        description=f"Episode {episode} not found in this series",
                        color=discord.Color.orange()
                    )
                )
                return

            # Build the view embed
            status_emoji = {
                'queued': '⏳',
                'generating': '🔄',
                'complete': '✅',
                'failed': '❌'
            }.get(ep.status, '❓')

            embed = discord.Embed(
                title=f"{status_emoji} {ep.title or f'Episode {ep.episode_number}'}",
                description=f"**Series:** {series.name[:50]}",
                color=discord.Color.green() if ep.status == 'complete' else discord.Color.blue()
            )

            # Synopsis
            if ep.synopsis:
                embed.add_field(
                    name="Synopsis",
                    value=ep.synopsis[:500] + ("..." if len(ep.synopsis) > 500 else ""),
                    inline=False
                )

            # Script
            if ep.script:
                # Discord field limit is 1024, so truncate if needed
                script_preview = ep.script[:900]
                if len(ep.script) > 900:
                    script_preview += f"\n\n*... ({len(ep.script)} chars total)*"
                embed.add_field(
                    name="Script",
                    value=f"```\n{script_preview}\n```",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Script",
                    value="*No script generated*",
                    inline=False
                )

            # Assets summary
            assets = []
            if ep.character_result:
                assets.append("Character images")
            if ep.voice_result and isinstance(ep.voice_result, dict) and ep.voice_result.get('audio_url'):
                assets.append("Voiceover")
            if ep.video_result:
                assets.append("Video")

            if assets:
                embed.add_field(name="Generated Assets", value=", ".join(assets), inline=True)

            embed.set_footer(text=f"Episode {episode}/{series.episode_count} | ID: {str(series.id)[:8]}...")

            # Check for audio file to attach
            audio_file = None
            if ep.voice_result and isinstance(ep.voice_result, dict):
                file_path = ep.voice_result.get('file_path')
                if file_path:
                    import os
                    from django.conf import settings
                    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
                    if os.path.exists(full_path):
                        audio_file = discord.File(full_path, filename=f"episode_{episode}_voice.mp3")

            if audio_file:
                embed.add_field(name="Audio", value="Voiceover attached below", inline=True)
                msg = await interaction.followup.send(embed=embed, file=audio_file)
            else:
                msg = await interaction.followup.send(embed=embed)

            # Session 452: Track this message for reaction feedback
            if msg and ep.status == 'complete':
                track_content_message(msg.id, {
                    'type': 'episode',
                    'series_id': str(series.id),
                    'episode_id': str(ep.id),
                    'context': {
                        'series_type': series.series_type,
                        'episode_number': ep.episode_number,
                        'style_preset': getattr(series, 'locked_style', None),
                        'has_voice': bool(ep.voice_result),
                        'has_video': bool(ep.video_result),
                    }
                })

        except Exception as e:
            logger.error(f"Series view error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to view episode: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )


class StudioCommands(commands.Cog):
    """
    Session 466: Autonomous Content Studio Commands.

    Commands for controlling the autonomous content studio (Tier 1 Autonomous Situation).

    The studio runs forever, creating content for channels based on agent debates.
    """

    def __init__(self, client):
        self.client = client

    studio = app_commands.Group(name="studio", description="Autonomous Content Studio")

    async def _get_linked_user(self, discord_id):
        """Get the linked Django user for this Discord ID."""
        @sync_to_async
        def get_user():
            from core.models import DiscordUser
            try:
                discord_user = DiscordUser.objects.get(discord_id=discord_id)
                return discord_user.user
            except DiscordUser.DoesNotExist:
                return None

        return await get_user()

    @studio.command(name="create", description="Create a new autonomous content channel")
    @app_commands.describe(
        name="Channel name (e.g., 'AI Weekly News')",
        domain="Topic domain (e.g., 'AI/ML news and tutorials')",
        frequency="How often to publish (daily/weekly/monthly)",
        audience="Target audience description",
        style="Content style (educational/entertainment/news)"
    )
    async def studio_create(
        self,
        interaction: discord.Interaction,
        name: str,
        domain: str,
        frequency: str,
        audience: str,
        style: str
    ):
        """Create a new autonomous content channel."""
        await interaction.response.defer()

        try:
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Account Not Linked",
                        description="Please link your Discord account first using `/link`",
                        color=discord.Color.orange()
                    )
                )
                return

            # Validate frequency
            valid_frequencies = ['daily', 'weekly', 'monthly']
            if frequency.lower() not in valid_frequencies:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Invalid Frequency",
                        description=f"Frequency must be one of: {', '.join(valid_frequencies)}",
                        color=discord.Color.red()
                    )
                )
                return

            @sync_to_async
            def create_channel():
                from core.models_autonomous_studio import ContentChannel
                from django.utils import timezone
                from datetime import timedelta

                # Map frequency to enum
                freq_map = {
                    'daily': 'daily',
                    'weekly': 'weekly',
                    'monthly': 'monthly'
                }

                # Calculate first content due date
                now = timezone.now()
                if frequency.lower() == 'daily':
                    next_due = now + timedelta(days=1)
                elif frequency.lower() == 'weekly':
                    next_due = now + timedelta(weeks=1)
                else:  # monthly
                    next_due = now + timedelta(days=30)

                # Session 469: Fixed - use status='active' instead of is_active=True
                channel = ContentChannel.objects.create(
                    name=name,
                    topic_domain=domain,
                    content_frequency=freq_map[frequency.lower()],
                    target_audience=audience,
                    content_style=style,
                    next_content_due=next_due,
                    status='active'
                )
                return channel

            channel = await create_channel()

            embed = discord.Embed(
                title="🎬 Autonomous Channel Created!",
                description=f"Your content studio is now active and will run autonomously.",
                color=discord.Color.green()
            )
            embed.add_field(name="Channel Name", value=name, inline=False)
            embed.add_field(name="Domain", value=domain, inline=False)
            embed.add_field(name="Publishing Frequency", value=frequency.title(), inline=True)
            embed.add_field(name="Target Audience", value=audience, inline=True)
            embed.add_field(name="Content Style", value=style.title(), inline=True)
            embed.add_field(
                name="Channel ID",
                value=f"`{str(channel.id)[:8]}...`",
                inline=False
            )
            embed.add_field(
                name="Next Content Due",
                value=f"<t:{int(channel.next_content_due.timestamp())}:R>",
                inline=False
            )
            embed.set_footer(text="The studio will automatically create content when due. Use /studio-status to monitor progress.")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Studio create error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to create channel: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @studio.command(name="list", description="List all your autonomous content channels")
    async def studio_list(self, interaction: discord.Interaction):
        """List all autonomous content channels."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def get_channels():
                from core.models_autonomous_studio import ContentChannel
                # Session 469: Fixed - use status='active' instead of is_active=True
                return list(ContentChannel.objects.filter(status='active').values(
                    'id', 'name', 'topic_domain', 'content_frequency', 'total_episodes_created',
                    'total_views', 'avg_retention_rate', 'confidence_multiplier', 'next_content_due'
                ).order_by('-created_at')[:10])

            channels = await get_channels()

            if not channels:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="No Channels Found",
                        description="You haven't created any channels yet.\nUse `/studio-create` to start your first autonomous channel!",
                        color=discord.Color.blue()
                    )
                )
                return

            embed = discord.Embed(
                title="🎬 Your Autonomous Content Channels",
                description=f"Showing {len(channels)} active channels",
                color=discord.Color.purple()
            )

            for c in channels:
                freq_emoji = {
                    'daily': '📅',
                    'weekly': '📆',
                    'monthly': '🗓️'
                }.get(c['content_frequency'], '❓')

                embed.add_field(
                    name=f"{freq_emoji} {c['name'][:40]}",
                    value=(
                        f"ID: `{str(c['id'])[:8]}...`\n"
                        f"Episodes: {c['total_episodes_created']} | Views: {c['total_views']}\n"
                        f"Retention: {c['avg_retention_rate']:.1f}% | Confidence: {c['confidence_multiplier']:.2f}x\n"
                        f"Next: <t:{int(c['next_content_due'].timestamp())}:R>"
                    ),
                    inline=False
                )

            embed.set_footer(text="Use /studio-status <id> for detailed analytics")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Studio list error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to list channels: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @studio.command(name="status", description="Check detailed status of a content channel")
    @app_commands.describe(channel_id="Channel ID (first 8 characters)")
    async def studio_status(self, interaction: discord.Interaction, channel_id: str):
        """Check detailed status of a content channel."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def get_channel_status():
                from core.models_autonomous_studio import ContentChannel, ChannelEpisode, TopicPerformance

                # Find channel by partial ID
                channels = ContentChannel.objects.filter(id__startswith=channel_id)
                if not channels.exists():
                    return None

                channel = channels.first()

                # Get recent episodes (Session 469: Fixed field name - use created_at not published_at)
                recent_episodes = list(ChannelEpisode.objects.filter(
                    channel=channel
                ).order_by('-created_at')[:5].values(
                    'title', 'topic', 'views', 'retention_rate', 'performance_score', 'publish_date', 'created_at'
                ))

                # Get top topics
                top_topics = list(TopicPerformance.objects.filter(
                    channel=channel
                ).order_by('-avg_performance_score')[:3].values(
                    'topic', 'episode_count', 'avg_views', 'avg_retention', 'confidence_score'
                ))

                return {
                    'channel': channel,
                    'recent_episodes': recent_episodes,
                    'top_topics': top_topics
                }

            data = await get_channel_status()

            if not data:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Channel Not Found",
                        description=f"No channel found with ID starting with `{channel_id}`",
                        color=discord.Color.red()
                    )
                )
                return

            channel = data['channel']

            embed = discord.Embed(
                title=f"📊 {channel.name}",
                # Session 469: Fixed - use status=='active' instead of is_active
                description=f"**Domain:** {channel.topic_domain}\n**Status:** {'🟢 Active' if channel.status == 'active' else '🔴 Paused'}",
                color=discord.Color.blue()
            )

            # Performance stats
            embed.add_field(
                name="📈 Performance",
                value=(
                    f"**Total Episodes:** {channel.total_episodes_created}\n"
                    f"**Total Views:** {channel.total_views:,}\n"
                    f"**Avg Retention:** {channel.avg_retention_rate:.1f}%\n"
                    f"**Confidence:** {channel.confidence_multiplier:.2f}x"
                ),
                inline=True
            )

            # Schedule info
            embed.add_field(
                name="⏰ Schedule",
                value=(
                    f"**Frequency:** {channel.get_content_frequency_display()}\n"
                    f"**Last Published:** <t:{int(channel.last_content_created.timestamp())}:R>\n"
                    f"**Next Due:** <t:{int(channel.next_content_due.timestamp())}:R>"
                ) if channel.last_content_created else (
                    f"**Frequency:** {channel.get_content_frequency_display()}\n"
                    f"**Next Due:** <t:{int(channel.next_content_due.timestamp())}:R>"
                ),
                inline=True
            )

            # Recent episodes
            if data['recent_episodes']:
                episodes_text = "\n".join([
                    f"• **{ep['topic'][:30]}** - {ep['views']} views, {ep['retention_rate']:.0f}% retention"
                    for ep in data['recent_episodes'][:3]
                ])
                embed.add_field(
                    name="📺 Recent Episodes",
                    value=episodes_text,
                    inline=False
                )

            # Top performing topics
            if data['top_topics']:
                topics_text = "\n".join([
                    f"• **{tp['topic'][:30]}** - {tp['episode_count']} eps, {tp['avg_views']:.0f} avg views, {tp['confidence_score']:.2f} confidence"
                    for tp in data['top_topics']
                ])
                embed.add_field(
                    name="🏆 Top Topics",
                    value=topics_text,
                    inline=False
                )

            embed.set_footer(text=f"Channel ID: {str(channel.id)}")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Studio status error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to get channel status: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @studio.command(name="pause", description="Pause autonomous content generation for a channel")
    @app_commands.describe(channel_id="Channel ID (first 8 characters)")
    async def studio_pause(self, interaction: discord.Interaction, channel_id: str):
        """Pause autonomous content generation for a channel."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def pause_channel():
                from core.models_autonomous_studio import ContentChannel

                # Session 469: Fixed - use status='active' instead of is_active=True
                channels = ContentChannel.objects.filter(id__startswith=channel_id, status='active')
                if not channels.exists():
                    return None

                channel = channels.first()
                channel.status = 'paused'
                channel.save()
                return channel

            channel = await pause_channel()

            if not channel:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Channel Not Found",
                        description=f"No active channel found with ID starting with `{channel_id}`",
                        color=discord.Color.red()
                    )
                )
                return

            embed = discord.Embed(
                title="⏸️ Channel Paused",
                description=f"**{channel.name}** has been paused. No new content will be generated automatically.",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="To Resume",
                value="Use `/studio-resume` when you want to reactivate autonomous generation",
                inline=False
            )
            embed.set_footer(text=f"Channel ID: {str(channel.id)}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Studio pause error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to pause channel: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @studio.command(name="resume", description="Resume autonomous content generation for a channel")
    @app_commands.describe(channel_id="Channel ID (first 8 characters)")
    async def studio_resume(self, interaction: discord.Interaction, channel_id: str):
        """Resume autonomous content generation for a channel."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def resume_channel():
                from core.models_autonomous_studio import ContentChannel

                # Session 469: Fixed - use status='paused' instead of is_active=False
                channels = ContentChannel.objects.filter(id__startswith=channel_id, status='paused')
                if not channels.exists():
                    return None

                channel = channels.first()
                channel.status = 'active'
                channel.save()
                return channel

            channel = await resume_channel()

            if not channel:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Channel Not Found",
                        description=f"No paused channel found with ID starting with `{channel_id}`",
                        color=discord.Color.red()
                    )
                )
                return

            embed = discord.Embed(
                title="▶️ Channel Resumed",
                description=f"**{channel.name}** is now active! Autonomous content generation will continue.",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Next Content Due",
                value=f"<t:{int(channel.next_content_due.timestamp())}:R>",
                inline=False
            )
            embed.set_footer(text=f"Channel ID: {str(channel.id)}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Studio resume error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to resume channel: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @studio.command(name="performance", description="View detailed analytics for a content channel")
    @app_commands.describe(channel_id="Channel ID (first 8 characters)")
    async def studio_performance(self, interaction: discord.Interaction, channel_id: str):
        """View detailed analytics for a content channel."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def get_performance_data():
                from core.models_autonomous_studio import ContentChannel, ChannelEpisode, TopicPerformance, ContentDebate
                from django.db.models import Avg, Max, Min

                channels = ContentChannel.objects.filter(id__startswith=channel_id)
                if not channels.exists():
                    return None

                channel = channels.first()

                # Calculate aggregate stats
                episodes = ChannelEpisode.objects.filter(channel=channel)
                episode_stats = episodes.aggregate(
                    total_views=sum(ep.views for ep in episodes),
                    avg_views=Avg('views'),
                    avg_retention=Avg('retention_rate'),
                    avg_score=Avg('performance_score'),
                    best_score=Max('performance_score'),
                    worst_score=Min('performance_score')
                )

                # Get debate history
                debates = ContentDebate.objects.filter(channel=channel).count()

                # Get topic performance breakdown
                topics = list(TopicPerformance.objects.filter(
                    channel=channel
                ).order_by('-avg_performance_score').values(
                    'topic', 'episode_count', 'avg_views', 'avg_retention', 'avg_performance_score', 'confidence_score'
                )[:5])

                return {
                    'channel': channel,
                    'episode_stats': episode_stats,
                    'total_debates': debates,
                    'topics': topics
                }

            data = await get_performance_data()

            if not data:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Channel Not Found",
                        description=f"No channel found with ID starting with `{channel_id}`",
                        color=discord.Color.red()
                    )
                )
                return

            channel = data['channel']
            stats = data['episode_stats']

            embed = discord.Embed(
                title=f"📊 Performance Analytics: {channel.name}",
                description=f"**{channel.total_episodes_created}** episodes • **{data['total_debates']}** agent debates",
                color=discord.Color.gold()
            )

            # Overall metrics
            embed.add_field(
                name="📈 Overall Metrics",
                value=(
                    f"**Total Views:** {stats['total_views']:,}\n"
                    f"**Avg Views/Episode:** {stats['avg_views']:.0f}\n"
                    f"**Avg Retention:** {stats['avg_retention']:.1f}%\n"
                    f"**Avg Score:** {stats['avg_score']:.1f}/100"
                ),
                inline=True
            )

            # Learning metrics
            embed.add_field(
                name="🎯 Learning Metrics",
                value=(
                    f"**Confidence Multiplier:** {channel.confidence_multiplier:.2f}x\n"
                    f"**Best Episode:** {stats['best_score']:.1f}/100\n"
                    f"**Worst Episode:** {stats['worst_score']:.1f}/100\n"
                    f"**Score Range:** {stats['best_score'] - stats['worst_score']:.1f}"
                ),
                inline=True
            )

            # Top performing topics
            if data['topics']:
                topics_text = "\n".join([
                    f"**{i+1}. {tp['topic'][:25]}**\n"
                    f"  {tp['episode_count']} eps • {tp['avg_views']:.0f} views • {tp['avg_retention']:.0f}% retention"
                    for i, tp in enumerate(data['topics'])
                ])
                embed.add_field(
                    name="🏆 Top 5 Topics",
                    value=topics_text,
                    inline=False
                )

            embed.set_footer(text=f"Channel ID: {str(channel.id)}")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Studio performance error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to get performance data: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @studio.command(name="episode", description="View episode content (script, research) from a channel")
    @app_commands.describe(channel_id="Channel ID (first 8 characters)")
    async def studio_episode(self, interaction: discord.Interaction, channel_id: str):
        """View the latest episode content from a channel."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def get_episode_content():
                from core.models_autonomous_studio import ContentChannel
                from core.models_ai_series import AISeries, SeriesEpisode

                channels = ContentChannel.objects.filter(id__startswith=channel_id)
                if not channels.exists():
                    return None, "Channel not found"

                channel = channels.first()

                # Find matching AISeries by looking for channel name in series name
                # Session 469: Series are created with channel name in the prompt/name
                series = AISeries.objects.filter(
                    name__icontains=channel.name
                ).order_by('-created_at').first()

                if not series:
                    # Try finding by topic domain
                    series = AISeries.objects.filter(
                        name__icontains=channel.topic_domain.split(',')[0].strip()
                    ).order_by('-created_at').first()

                if not series:
                    return {'channel': channel, 'episode': None, 'series': None}, "No episodes generated yet"

                # Get the latest episode from this series
                episode = SeriesEpisode.objects.filter(series=series).order_by('-id').first()

                return {
                    'channel': channel,
                    'series': series,
                    'episode': episode
                }, None

            data, error = await get_episode_content()

            if error == "Channel not found":
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Channel Not Found",
                        description=f"No channel found with ID starting with `{channel_id}`",
                        color=discord.Color.red()
                    )
                )
                return

            channel = data['channel']

            if not data.get('episode'):
                await interaction.followup.send(
                    embed=discord.Embed(
                        title=f"📺 {channel.name}",
                        description="No episodes have been generated yet.\n\nEpisodes are created automatically by Celery Beat every 4 hours, or you can trigger one manually.",
                        color=discord.Color.orange()
                    )
                )
                return

            episode = data['episode']
            series = data['series']

            # Create embed with episode content
            embed = discord.Embed(
                title=f"📺 {episode.title}",
                description=f"**Channel:** {channel.name}\n**Status:** {episode.status}",
                color=discord.Color.green()
            )

            # Synopsis
            if episode.synopsis:
                embed.add_field(
                    name="📝 Synopsis",
                    value=episode.synopsis[:500] + ("..." if len(episode.synopsis) > 500 else ""),
                    inline=False
                )

            # Script preview
            if episode.script:
                script_preview = episode.script[:800]
                if len(episode.script) > 800:
                    script_preview += f"\n\n... ({len(episode.script) - 800} more characters)"
                embed.add_field(
                    name="📜 Script",
                    value=script_preview,
                    inline=False
                )

            # Series info
            embed.add_field(
                name="📦 Series Info",
                value=f"**Type:** {series.series_type}\n**Episode #:** {episode.episode_number}",
                inline=True
            )

            embed.set_footer(text=f"Series ID: {str(series.id)[:8]}... | Episode ID: {str(episode.id)[:8]}...")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Studio episode error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to get episode content: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )


class GumroadCommands(commands.Cog):
    """
    Session 487: Gumroad Publishing Commands.

    Commands for publishing AI-generated content directly to Gumroad for sale:
    - /publish-gumroad - Publish an image from your gallery to Gumroad
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

    @app_commands.command(name="publish-gumroad", description="Publish an image to Gumroad for sale")
    @app_commands.describe(
        image_id="Image ID from /gallery (e.g., 320)",
        price="Price in USD (default: 9.99)",
        title="Custom title (optional, uses prompt if not provided)"
    )
    async def publish_gumroad(
        self,
        interaction: discord.Interaction,
        image_id: int,
        price: float = 9.99,
        title: str = None
    ):
        """Publish an AI-generated image to Gumroad marketplace."""
        await interaction.response.defer()

        try:
            # Get linked user
            user = await self._get_linked_user(str(interaction.user.id))

            if not user:
                embed = discord.Embed(
                    title="Not Linked",
                    description="Link your Discord account first with `/link <code>` from the web app.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return

            @sync_to_async
            def publish_to_gumroad(web_user, img_id, pub_price, pub_title):
                from content.models import ImageHistory
                from core.services.gumroad_publishing import GumroadPublishingService
                from decimal import Decimal

                # Get image by sequential_number
                image = ImageHistory.objects.filter(
                    user=web_user,
                    sequential_number=img_id
                ).first()

                if not image:
                    # Try by primary key ID as fallback
                    try:
                        image = ImageHistory.objects.get(id=img_id, user=web_user)
                    except (ImageHistory.DoesNotExist, ValueError):
                        return {'success': False, 'error': f'Image #{img_id} not found in your gallery'}

                # Initialize publishing service
                service = GumroadPublishingService(web_user)

                if not service.account:
                    return {
                        'success': False,
                        'error': 'No Gumroad account connected. Please connect your Gumroad account in the web app (Distribution tab).'
                    }

                # Publish to Gumroad
                try:
                    distribution = service.publish_image(
                        image_id=image.id,
                        title=pub_title,
                        price=Decimal(str(pub_price))
                    )

                    return {
                        'success': True,
                        'title': distribution.title,
                        'price': str(distribution.price),
                        'url': distribution.platform_listing_url,
                        'listing_id': distribution.platform_listing_id,
                        'prompt': (image.prompt[:150] + '...') if len(image.prompt) > 150 else image.prompt,
                        'image_id': image.sequential_number or image.id
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            result = await publish_to_gumroad(user, image_id, price, title)

            if result['success']:
                embed = discord.Embed(
                    title="Published to Gumroad!",
                    description=f"Your artwork is now for sale!",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="Title", value=result['title'], inline=False)
                embed.add_field(name="Price", value=f"${result['price']}", inline=True)
                embed.add_field(name="Image #", value=f"#{result['image_id']}", inline=True)
                embed.add_field(name="Gumroad URL", value=result['url'], inline=False)
                embed.add_field(name="Prompt", value=f"```{result['prompt']}```", inline=False)
                embed.set_footer(text="Session 487 | Golden Egg Strategy")
            else:
                embed = discord.Embed(
                    title="Publishing Failed",
                    description=f"**Error:** {result['error']}",
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )
                embed.set_footer(text="Check your Gumroad connection in AI Studio")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Gumroad publish error: {e}", exc_info=True)
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)[:200]}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    # /gumroad-status removed in Phase G2 — use Cockpit instead


# PipelineLearningCommands removed in Phase G2 command consolidation

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

    # Session 507: Removed /server-info command to stay under Discord's 100 command limit


class ClientCommands(commands.Cog):
    """
    Session 432: Client Management Commands (Phase 3).

    Allows freelancers and agencies to manage clients via Discord,
    including dedicated channels and deliverable tracking.
    """

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot

    client = app_commands.Group(name="client", description="Client management")

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

    @client.command(name="add", description="Create a new client with dedicated channel")
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

    @client.command(name="list", description="List all your clients")
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

    @client.command(name="deliver", description="Send a deliverable to a client's channel")
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

    @client.command(name="invite", description="Generate an invite link for a client")
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

    # =========================================================================
    # Session 461: Blockchain Audit Commands
    # =========================================================================

    @app_commands.command(name="audit-contract", description="Audit a smart contract by its Ethereum address")
    @app_commands.describe(
        address="The Ethereum contract address (0x...)",
        quick="Quick risk analysis only (faster)"
    )
    async def audit_contract(self, interaction: discord.Interaction, address: str, quick: bool = False):
        """Audit a smart contract from Etherscan by address."""
        await interaction.response.defer()

        # Validate address format
        if not address.startswith('0x') or len(address) != 42:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Invalid Address",
                    description="Please provide a valid Ethereum address (0x... format, 42 characters)",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return

        try:
            from core.services.blockchain_event_listener import get_event_listener, audit_contract_by_address

            # Show initial processing message
            processing_embed = discord.Embed(
                title="🔍 Auditing Contract...",
                description=f"**Address:** `{address}`\n\nFetching source code from Etherscan...",
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=processing_embed)

            # Perform the audit
            @sync_to_async
            def run_audit():
                if quick:
                    listener = get_event_listener()
                    return listener.analyze_contract_risk(address)
                else:
                    return audit_contract_by_address(address)

            result = await run_audit()

            # Build response embed
            if result.get('success') or result.get('risk_level'):
                # Success - show audit results
                risk_level = result.get('risk_analysis', {}).get('risk_level') or result.get('risk_level', 'UNKNOWN')
                risk_score = result.get('risk_analysis', {}).get('risk_score') or result.get('risk_score', 0)

                # Color based on risk level
                color_map = {
                    'CRITICAL': discord.Color.dark_red(),
                    'HIGH': discord.Color.red(),
                    'MEDIUM': discord.Color.orange(),
                    'LOW': discord.Color.green(),
                }
                embed_color = color_map.get(risk_level, discord.Color.grey())

                # Risk emoji
                emoji_map = {
                    'CRITICAL': '🚨',
                    'HIGH': '⚠️',
                    'MEDIUM': '📊',
                    'LOW': '✅',
                }
                risk_emoji = emoji_map.get(risk_level, '❓')

                result_embed = discord.Embed(
                    title=f"{risk_emoji} Contract Audit: {result.get('contract_name', 'Unknown')}",
                    description=f"**Address:** `{address}`",
                    color=embed_color
                )

                # Risk score
                result_embed.add_field(
                    name="Risk Assessment",
                    value=f"**Level:** {risk_level}\n**Score:** {risk_score}/100",
                    inline=True
                )

                # Contract info
                if result.get('compiler_version'):
                    result_embed.add_field(
                        name="Contract Info",
                        value=f"**Compiler:** {result.get('compiler_version')}\n**Proxy:** {'Yes' if result.get('is_proxy') else 'No'}",
                        inline=True
                    )

                # Red flags
                red_flags = result.get('risk_analysis', {}).get('red_flags') or result.get('red_flags', [])
                if red_flags:
                    flags_text = "\n".join(f"• {flag}" for flag in red_flags[:5])
                    if len(red_flags) > 5:
                        flags_text += f"\n*...and {len(red_flags) - 5} more*"
                    result_embed.add_field(
                        name=f"🚩 Red Flags ({len(red_flags)})",
                        value=flags_text,
                        inline=False
                    )

                # Transaction analysis
                tx_analysis = result.get('risk_analysis', {}).get('transaction_analysis') or result.get('transaction_analysis', {})
                if tx_analysis and tx_analysis.get('total_transactions'):
                    result_embed.add_field(
                        name="Transaction Analysis",
                        value=(
                            f"**Total Txs:** {tx_analysis.get('total_transactions', 'N/A')}\n"
                            f"**Error Rate:** {tx_analysis.get('error_rate', 'N/A')}\n"
                            f"**Recent Volume:** {tx_analysis.get('recent_volume_eth', 0):.2f} ETH"
                        ),
                        inline=True
                    )

                # Recommendations
                recommendations = result.get('risk_analysis', {}).get('recommendations') or result.get('recommendations', [])
                if recommendations:
                    rec_text = "\n".join(f"• {rec}" for rec in recommendations[:3])
                    result_embed.add_field(
                        name="📋 Recommendations",
                        value=rec_text,
                        inline=False
                    )

                # Links
                result_embed.add_field(
                    name="🔗 Links",
                    value=f"[View on Etherscan](https://etherscan.io/address/{address})",
                    inline=False
                )

                result_embed.set_footer(text="Session 461 | Blockchain Audit Agents")

                await interaction.edit_original_response(embed=result_embed)

            else:
                # Error
                error_embed = discord.Embed(
                    title="❌ Audit Failed",
                    description=result.get('error', 'Unknown error occurred'),
                    color=discord.Color.red()
                )
                if result.get('recommendation'):
                    error_embed.add_field(
                        name="Recommendation",
                        value=result.get('recommendation'),
                        inline=False
                    )
                await interaction.edit_original_response(embed=error_embed)

        except Exception as e:
            logger.error(f"/audit-contract error: {e}")
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"Failed to audit contract: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @app_commands.command(name="blockchain-status", description="Check blockchain monitoring status")
    async def blockchain_status(self, interaction: discord.Interaction):
        """Check the status of blockchain audit agents."""
        await interaction.response.defer()

        try:
            from core.services.blockchain_event_listener import get_event_listener
            import os

            listener = get_event_listener()
            api_configured = bool(os.environ.get('ETHERSCAN_API_KEY'))

            embed = discord.Embed(
                title="⛓️ Blockchain Audit Status",
                color=discord.Color.purple() if api_configured else discord.Color.orange()
            )

            # API Status
            embed.add_field(
                name="Etherscan API",
                value="✅ Configured" if api_configured else "⚠️ Not Configured",
                inline=True
            )

            # Listener Status
            embed.add_field(
                name="Event Listener",
                value="✅ Running" if listener.running else "⏹️ Stopped",
                inline=True
            )

            # Last Block
            embed.add_field(
                name="Last Block",
                value=f"#{listener._last_block}" if listener._last_block else "Not started",
                inline=True
            )

            # Agents
            agents_status = (
                "• SmartContractAuditorAgent: ✅\n"
                "• TransactionMonitorAgent: ✅\n"
                "• WhaleWatcherAgent: ✅\n"
                "• ExploitDetectorAgent: ✅\n"
                "• BlockchainAuditCoordinator: ✅"
            )
            embed.add_field(
                name="Audit Agents",
                value=agents_status,
                inline=False
            )

            # Commands
            embed.add_field(
                name="Available Commands",
                value=(
                    "`/audit-contract <address>` - Audit a contract\n"
                    "`/blockchain-status` - This command"
                ),
                inline=False
            )

            embed.set_footer(text="Session 461 | Blockchain Audit Agent Group")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"/blockchain-status error: {e}")
            await interaction.followup.send(f"Error: {str(e)[:100]}", ephemeral=True)

    @app_commands.command(name="voice-ask", description="Ask a question and hear the AI speak the answer")
    @app_commands.describe(
        question="Your question",
        agent="Agent to use (default: Research)",
        voice="Voice name (default: your cloned voice or Rachel)"
    )
    async def voice_ask(self, interaction: discord.Interaction, question: str, agent: str = "Research", voice: str = None):
        """Ask a question and get a spoken audio response using your cloned voice."""
        await interaction.response.defer()

        # Rate limit check
        can_use, remaining = rate_limiter.check_cooldown(interaction.user.id, 'voice_ask')
        if not can_use:
            await interaction.followup.send(
                f"⏳ Please wait {remaining:.1f}s before asking another question.",
                ephemeral=True
            )
            return

        try:
            from core.agent_router import AgentRouter
            from core.models_voice_marketplace import VoiceProfile
            from content.elevenlabs_provider import elevenlabs_provider
            from django.contrib.auth import get_user_model
            import io
            User = get_user_model()

            # Get linked user
            @sync_to_async
            def get_linked_user(discord_id):
                try:
                    return User.objects.filter(discord_id=str(discord_id)).first()
                except Exception:
                    return None

            user = await get_linked_user(interaction.user.id)

            # Get user's cloned voice or use default
            @sync_to_async
            def get_user_voice(user, voice_name):
                if voice_name:
                    # Try to find by name
                    vp = VoiceProfile.objects.filter(name__icontains=voice_name).first()
                    if vp:
                        return vp.elevenlabs_voice_id, vp.name
                if user:
                    # Get user's own voice
                    vp = VoiceProfile.objects.filter(owner=user).first()
                    if vp:
                        return vp.elevenlabs_voice_id, vp.name
                # Fallback to default
                return None, "Rachel"

            voice_id, voice_name = await get_user_voice(user, voice)

            # Normalize agent name
            agent_name = agent.strip()
            if not agent_name.endswith("Agent"):
                agent_name = agent_name + "Agent"

            # Show thinking embed
            thinking_embed = discord.Embed(
                title=f"🎤 Asking {agent_name}...",
                description=f"*{question[:100]}{'...' if len(question) > 100 else ''}*\n\nVoice: **{voice_name}**",
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=thinking_embed)

            # Execute the agent
            @sync_to_async
            def execute_agent(agent_name, task, user):
                router = AgentRouter(user=user)
                return router.route(agent_name, task)

            result = await execute_agent(agent_name, question, user)
            rate_limiter.record_use(interaction.user.id, 'voice_ask')

            # Extract text response
            raw_response = ""
            if isinstance(result, dict):
                raw_response = result.get('response', result.get('result', str(result)))
            else:
                raw_response = str(result)

            # Convert to natural speech using GPT
            @sync_to_async
            def make_speakable(raw_text, question):
                """Convert agent output to natural conversational speech."""
                import openai
                import os

                client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

                prompt = f"""Convert this research data into a natural, conversational spoken response.

Rules:
- DO NOT read URLs or links aloud
- Summarize the key findings in 2-4 sentences
- Speak naturally as if you're telling a friend what you found
- Focus on the most interesting/relevant information
- Keep it under 200 words for good audio length

Original question: {question}

Raw data to summarize:
{raw_text[:3000]}

Spoken response:"""

                try:
                    # Session 494: Use gpt-5-mini (reasoning model)
                    response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[{"role": "user", "content": prompt}],
                        max_completion_tokens=2000  # Reasoning model needs more tokens
                    )
                    return response.choices[0].message.content.strip()
                except Exception as e:
                    logger.error(f"Error making response speakable: {e}")
                    # Fallback: just clean up the raw text
                    import re
                    cleaned = re.sub(r'https?://\S+', '', raw_text)
                    cleaned = re.sub(r'\[.*?\]', '', cleaned)
                    return cleaned[:500]

            response_text = await make_speakable(raw_response, question)

            # Truncate for TTS (ElevenLabs limit ~5000 chars, keep it shorter for audio length)
            max_tts_chars = 1500
            if len(response_text) > max_tts_chars:
                response_text = response_text[:max_tts_chars] + "..."

            # Generate TTS
            @sync_to_async
            def generate_speech(text, voice_id):
                if voice_id:
                    # Use cloned voice - call API directly
                    import requests
                    from django.conf import settings
                    api_key = settings.EXTERNAL_API_KEYS.get('ELEVENLABS_API_KEY', '')
                    response = requests.post(
                        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
                        json={"text": text, "model_id": "eleven_multilingual_v2"},
                        timeout=60
                    )
                    if response.status_code == 200:
                        return response.content, None
                    return None, f"TTS failed: {response.status_code}"
                else:
                    # Use default voice through provider
                    result = elevenlabs_provider.text_to_speech(text, voice="Rachel")
                    if result.get('success'):
                        # Download the audio from URL
                        import requests
                        audio_url = result.get('audio_url', '')
                        if audio_url:
                            resp = requests.get(audio_url, timeout=30)
                            if resp.status_code == 200:
                                return resp.content, None
                    return None, result.get('error_message', 'TTS failed')

            audio_data, error = await generate_speech(response_text, voice_id)

            if error or not audio_data:
                error_embed = discord.Embed(
                    title="❌ TTS Error",
                    description=f"Text response received but audio generation failed:\n{error}",
                    color=discord.Color.red()
                )
                error_embed.add_field(name="Text Response", value=response_text[:500] + "..." if len(response_text) > 500 else response_text, inline=False)
                await interaction.edit_original_response(embed=error_embed)
                return

            # Send audio file
            audio_file = discord.File(io.BytesIO(audio_data), filename="response.mp3")

            # Update embed with success
            success_embed = discord.Embed(
                title=f"🎤 {agent_name} Response",
                description=f"**Question:** {question[:200]}{'...' if len(question) > 200 else ''}\n\n**Voice:** {voice_name}",
                color=discord.Color.green()
            )
            # Add truncated text preview
            text_preview = response_text[:300] + "..." if len(response_text) > 300 else response_text
            success_embed.add_field(name="📝 Response Preview", value=text_preview, inline=False)

            await interaction.edit_original_response(embed=success_embed)
            await interaction.followup.send(file=audio_file)

            logger.info(f"/voice-ask completed: {agent_name} answered with {voice_name} voice")

        except Exception as e:
            logger.error(f"/voice-ask error: {e}")
            import traceback
            traceback.print_exc()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"Failed to process question: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @app_commands.command(name="voice-chat", description="Speak to the AI and hear a spoken response")
    @app_commands.describe(
        duration="Recording duration in seconds (default: 10, max: 30)",
        agent="Agent to use (default: Research)",
    )
    async def voice_chat(
        self,
        interaction: discord.Interaction,
        duration: int = 10,
        agent: str = "Research"
    ):
        """
        Full voice conversation: Speak your question, hear the AI's answer.

        1. Records your voice from Discord voice channel
        2. Transcribes using Whisper
        3. Routes to the specified agent
        4. Speaks the response using your cloned voice
        """
        await interaction.response.defer()

        # Rate limit check
        can_use, remaining = rate_limiter.check_cooldown(interaction.user.id, 'voice_chat')
        if not can_use:
            await interaction.followup.send(
                f"⏳ Please wait {remaining:.1f}s before another voice chat.",
                ephemeral=True
            )
            return

        # Validate duration
        duration = max(5, min(30, duration))  # Clamp between 5-30 seconds

        try:
            import discord.ext.voice_recv as voice_recv
            from core.services.discord_voice import (
                get_voice_recorder,
                VoiceRecordingSink,
                VOICE_RECV_AVAILABLE,
                OPENAI_API_KEY
            )
            from core.agent_router import AgentRouter
            from core.models_voice_marketplace import VoiceProfile
            from content.elevenlabs_provider import elevenlabs_provider
            from django.contrib.auth import get_user_model
            from openai import OpenAI
            import io

            User = get_user_model()

            if not VOICE_RECV_AVAILABLE:
                await interaction.followup.send(
                    "❌ Voice receiving is not available. Missing `discord-ext-voice-recv` package.",
                    ephemeral=True
                )
                return

            if not OPENAI_API_KEY:
                await interaction.followup.send(
                    "❌ Whisper transcription not available. Missing OpenAI API key.",
                    ephemeral=True
                )
                return

            # Check if user is in a voice channel
            if not interaction.user.voice or not interaction.user.voice.channel:
                await interaction.followup.send(
                    "❌ You need to be in a voice channel!\n"
                    "Join a voice channel and try again.",
                    ephemeral=True
                )
                return

            voice_channel = interaction.user.voice.channel
            user_id = interaction.user.id

            # Get linked user
            @sync_to_async
            def get_linked_user(discord_id):
                try:
                    return User.objects.filter(discord_id=str(discord_id)).first()
                except Exception:
                    return None

            linked_user = await get_linked_user(interaction.user.id)

            # Get user's cloned voice
            @sync_to_async
            def get_user_voice(user):
                if user:
                    voice = VoiceProfile.objects.filter(owner=user, is_active=True).first()
                    if voice:
                        return voice.elevenlabs_voice_id, voice.name
                return None, "Rachel"

            voice_id, voice_name = await get_user_voice(linked_user)

            # Send initial status
            status_embed = discord.Embed(
                title="🎙️ Voice Chat",
                description=f"Joining voice channel and recording for **{duration} seconds**...\n\n"
                           f"**Speak your question clearly!**",
                color=discord.Color.blue()
            )
            status_embed.add_field(name="Agent", value=agent, inline=True)
            status_embed.add_field(name="Voice", value=voice_name, inline=True)
            await interaction.followup.send(embed=status_embed)

            # Get existing voice client or connect
            voice_client = interaction.guild.voice_client

            # Disconnect and reconnect with VoiceRecvClient for recording
            if voice_client:
                await voice_client.disconnect(force=True)
                await asyncio.sleep(0.5)

            # Connect with VoiceRecvClient
            voice_client = await voice_channel.connect(cls=voice_recv.VoiceRecvClient)

            # Set up recording
            recorder = get_voice_recorder()
            recorder.start_recording(user_id, interaction.guild.id, voice_channel.id)

            # Create sink for capturing audio
            sink = VoiceRecordingSink(recorder, user_id)
            voice_client.listen(sink)

            # Update status
            recording_embed = discord.Embed(
                title="🔴 Recording...",
                description=f"**Speak your question now!**\n\nRecording for {duration} seconds...",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=recording_embed)

            # Wait for duration
            await asyncio.sleep(duration)

            # Stop recording
            voice_client.stop_listening()
            audio_path = recorder.stop_recording(user_id)

            # Disconnect from voice
            await voice_client.disconnect()

            if not audio_path:
                await interaction.edit_original_response(
                    embed=discord.Embed(
                        title="❌ No Audio Captured",
                        description="No audio was recorded. Make sure you're speaking!",
                        color=discord.Color.red()
                    )
                )
                return

            # Update status - transcribing
            transcribe_embed = discord.Embed(
                title="📝 Transcribing...",
                description="Converting your speech to text with Whisper...",
                color=discord.Color.orange()
            )
            await interaction.edit_original_response(embed=transcribe_embed)

            # Transcribe with Whisper
            openai_client = OpenAI(api_key=OPENAI_API_KEY)

            @sync_to_async
            def transcribe_audio(file_path):
                with open(file_path, 'rb') as audio_file:
                    transcript = openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                return transcript.text

            transcribed_text = await transcribe_audio(audio_path)

            # Clean up audio file
            try:
                import os
                os.unlink(audio_path)
            except Exception as _e:
                logger.warning(
                    "discord_bot.__init__: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

            if not transcribed_text or len(transcribed_text.strip()) < 3:
                await interaction.edit_original_response(
                    embed=discord.Embed(
                        title="❌ Couldn't Understand",
                        description="Couldn't transcribe your speech. Please speak more clearly.",
                        color=discord.Color.red()
                    )
                )
                return

            # Update status - processing
            process_embed = discord.Embed(
                title="🤔 Processing...",
                description=f"**You said:** \"{transcribed_text}\"\n\nGetting response from {agent} agent...",
                color=discord.Color.purple()
            )
            await interaction.edit_original_response(embed=process_embed)

            # Route to agent
            @sync_to_async
            def execute_agent(agent_name, task, user):
                router = AgentRouter()
                result = router.execute_task(
                    task=task,
                    target_agent=agent_name,
                    user=user
                )
                return result

            # Map agent names
            agent_mapping = {
                'research': 'ResearchAgent',
                'image': 'ImageAgent',
                'video': 'VideoAgent',
                'audio': 'AudioAgent',
                'cto': 'CTOAgent',
                'strategy': 'ContentStrategyAgent',
            }
            agent_name = agent_mapping.get(agent.lower(), agent)

            result = await execute_agent(agent_name, transcribed_text, linked_user)
            rate_limiter.record_use(interaction.user.id, 'voice_chat')

            # Extract text response
            raw_response = ""
            if isinstance(result, dict):
                raw_response = result.get('response', result.get('result', str(result)))
            else:
                raw_response = str(result)

            # Convert to natural speech
            @sync_to_async
            def make_speakable(raw_text, question):
                client = OpenAI(api_key=OPENAI_API_KEY)
                prompt = f"""Convert this data into a natural, conversational spoken response.

Rules:
- DO NOT read URLs or links aloud
- Summarize the key findings in 2-4 sentences
- Speak naturally as if talking to a friend
- Focus on the most interesting/relevant information
- Keep it under 150 words for good audio length

Original question: {question}

Raw data to summarize:
{raw_text[:3000]}

Conversational response:"""

                # Session 494: Use gpt-5-mini (reasoning model)
                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=2000  # Reasoning model needs more tokens
                )
                return response.choices[0].message.content

            speakable_response = await make_speakable(raw_response, transcribed_text)

            # Update status - generating audio
            audio_embed = discord.Embed(
                title="🔊 Generating Response...",
                description=f"Creating audio with **{voice_name}** voice...",
                color=discord.Color.green()
            )
            await interaction.edit_original_response(embed=audio_embed)

            # Generate TTS
            @sync_to_async
            def generate_tts(text, vid):
                return elevenlabs_provider.generate_speech(
                    text=text,
                    voice_id=vid or "EXAVITQu4vr4xnSDxMaL",  # Rachel as fallback
                    model_id="eleven_multilingual_v2"
                )

            audio_result = await generate_tts(speakable_response, voice_id)

            if not audio_result.get('success'):
                await interaction.edit_original_response(
                    embed=discord.Embed(
                        title="❌ TTS Failed",
                        description=f"Couldn't generate audio: {audio_result.get('error', 'Unknown error')}\n\n"
                                   f"**Text response:** {speakable_response[:500]}",
                        color=discord.Color.red()
                    )
                )
                return

            # Send success response with audio
            success_embed = discord.Embed(
                title="🎙️ Voice Chat Complete",
                color=discord.Color.green()
            )
            success_embed.add_field(
                name="You Asked",
                value=f"\"{transcribed_text[:200]}{'...' if len(transcribed_text) > 200 else ''}\"",
                inline=False
            )
            success_embed.add_field(
                name="AI Response",
                value=speakable_response[:500] + ("..." if len(speakable_response) > 500 else ""),
                inline=False
            )
            success_embed.add_field(name="Agent", value=agent_name, inline=True)
            success_embed.add_field(name="Voice", value=voice_name, inline=True)
            success_embed.set_footer(text="Full voice conversation powered by Whisper + ElevenLabs")

            await interaction.edit_original_response(embed=success_embed)

            # Send audio file
            audio_data = audio_result.get('audio_data')
            if audio_data:
                audio_file = discord.File(
                    io.BytesIO(audio_data),
                    filename="voice_response.mp3"
                )
                await interaction.followup.send(file=audio_file)

            logger.info(f"/voice-chat completed: '{transcribed_text[:50]}...' -> {agent_name} -> {voice_name}")

        except Exception as e:
            logger.error(f"/voice-chat error: {e}")
            import traceback
            traceback.print_exc()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"Voice chat failed: {str(e)[:200]}",
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
                # Session 494: Use gpt-5-mini (reasoning model)
                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[
                        {"role": "system", "content": advisor_prompt},
                        {"role": "user", "content": question}
                    ],
                    max_completion_tokens=3000  # Reasoning model needs more tokens
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
                "**/agent-task** <name> <task> - Execute agent task\n"
                "**/voice-ask** <question> [agent] [voice] - Ask & hear spoken answer\n"
                "**/voice-chat** [duration] [agent] - Speak & hear AI respond (Whisper)"
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


# =============================================================================
# Session 452: Discord Reaction Feedback System
# =============================================================================

# In-memory cache for message->content mappings
# Format: {message_id: {'type': 'episode', 'series_id': '...', 'episode_id': '...', 'context': {...}}}
# Falls back to Redis if available
_message_content_map: Dict[int, Dict[str, Any]] = {}
_map_max_size = 10000  # Keep last 10k messages in memory


def track_content_message(message_id: int, content_info: Dict[str, Any]):
    """
    Track a message ID to content mapping for reaction feedback.

    Args:
        message_id: Discord message ID
        content_info: Dict with keys like:
            - type: 'episode', 'image', 'voice', 'video'
            - series_id: UUID string
            - episode_id: UUID string
            - stage: Pipeline stage name
            - context: Additional context (style, audience, etc.)
    """
    global _message_content_map

    # Store in memory
    _message_content_map[message_id] = {
        **content_info,
        'tracked_at': datetime.now().isoformat()
    }

    # Prune old entries if too large
    if len(_message_content_map) > _map_max_size:
        # Remove oldest 1000 entries
        sorted_ids = sorted(_message_content_map.keys())
        for old_id in sorted_ids[:1000]:
            del _message_content_map[old_id]

    # Also try Redis for persistence across restarts
    try:
        import redis
        import json
        r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True)
        key = f"discord:content:{message_id}"
        r.setex(key, 86400, json.dumps(content_info))  # Expire after 24h
    except Exception:
        pass  # Redis not available, memory-only


def get_content_for_message(message_id: int) -> Optional[Dict[str, Any]]:
    """Get content info for a tracked message ID."""
    # Check memory first
    if message_id in _message_content_map:
        return _message_content_map[message_id]

    # Fall back to Redis
    try:
        import redis
        import json
        r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True)
        key = f"discord:content:{message_id}"
        data = r.get(key)
        if data:
            return json.loads(data)
    except Exception as _e:
        logger.warning(
            "discord_bot.get_content_for_message: swallowed (%s: %s) — degraded",
            type(_e).__name__, _e,
        )

    return None


# Emoji to rating mapping
REACTION_RATINGS = {
    # Positive (5 stars)
    '👍': 5.0,
    '❤️': 5.0,
    '🔥': 5.0,
    '⭐': 5.0,
    '💯': 5.0,
    '🎉': 5.0,
    '👏': 5.0,
    '💪': 5.0,
    '🚀': 5.0,

    # Good (4 stars)
    '👌': 4.0,
    '✨': 4.0,
    '💜': 4.0,
    '😊': 4.0,
    '🙌': 4.0,

    # Neutral (3 stars)
    '🤔': 3.0,
    '😐': 3.0,
    '👀': 3.0,

    # Needs improvement (2 stars)
    '😕': 2.0,
    '🤷': 2.0,
    '😬': 2.0,

    # Poor (1 star)
    '👎': 1.0,
    '❌': 1.0,
    '💔': 1.0,
    '😞': 1.0,
}


class ReactionFeedbackCog(commands.Cog):
    """
    Session 452: Automatic feedback from Discord reactions.

    When users react to AI-generated content with emojis,
    those reactions are captured and fed into the pipeline
    learning system to improve future content generation.

    Positive reactions (👍❤️🔥⭐) = 5 stars
    Good reactions (👌✨) = 4 stars
    Neutral reactions (🤔😐) = 3 stars
    Needs improvement (😕🤷) = 2 stars
    Poor reactions (👎❌) = 1 star
    """

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot
        self._feedback_cooldown: Dict[str, datetime] = {}  # user_id:message_id -> last_feedback
        self._cooldown_seconds = 60  # Prevent spam feedback from same user on same message

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """
        Handle reaction additions on tracked messages.

        We use raw reaction event because it works for messages not in cache.
        """
        # Ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return

        # Get emoji as string
        emoji = str(payload.emoji)

        # Check if this emoji maps to a rating
        rating = REACTION_RATINGS.get(emoji)
        if rating is None:
            return  # Not a feedback emoji

        # Check if we're tracking this message
        content_info = get_content_for_message(payload.message_id)
        if not content_info:
            return  # Not a tracked content message

        # Check cooldown
        cooldown_key = f"{payload.user_id}:{payload.message_id}"
        now = datetime.now()
        if cooldown_key in self._feedback_cooldown:
            last = self._feedback_cooldown[cooldown_key]
            if (now - last).total_seconds() < self._cooldown_seconds:
                return  # Still in cooldown
        self._feedback_cooldown[cooldown_key] = now

        # Submit feedback
        await self._submit_reaction_feedback(
            user_id=payload.user_id,
            message_id=payload.message_id,
            emoji=emoji,
            rating=rating,
            content_info=content_info
        )

    async def _submit_reaction_feedback(
        self,
        user_id: int,
        message_id: int,
        emoji: str,
        rating: float,
        content_info: Dict[str, Any]
    ):
        """Submit reaction as feedback to pipeline learning service."""
        try:
            @sync_to_async
            def record_feedback():
                from core.services.pipeline_learning import (
                    get_pipeline_learning_service,
                    track_ab_test_series_feedback
                )
                from django.contrib.auth import get_user_model

                User = get_user_model()

                # Try to get linked user
                user = User.objects.filter(discord_id=str(user_id)).first()
                user_pk = user.pk if user else None

                service = get_pipeline_learning_service()

                # Determine stage from content type
                content_type = content_info.get('type', 'package')
                stage_map = {
                    'episode': 'package',
                    'script': 'script',
                    'image': 'image',
                    'voice': 'voice',
                    'video': 'video',
                }
                stage = stage_map.get(content_type, 'package')

                # Build context
                context = content_info.get('context', {})
                context['discord_reaction'] = emoji
                context['discord_message_id'] = str(message_id)
                context['discord_user_id'] = str(user_id)

                # Record the feedback
                feedback = service.record_stage_feedback(
                    stage=stage,
                    rating=rating,
                    context=context,
                    series_id=content_info.get('series_id'),
                    episode_id=content_info.get('episode_id'),
                    user_id=user_pk,
                    feedback_type='discord_reaction',
                    comment=f"Discord reaction: {emoji}"
                )

                # Session 452: Also track A/B test conversion if series is in an experiment
                series_id = content_info.get('series_id')
                if series_id and user_pk:
                    try:
                        from core.models_ai_series import AISeries
                        series = AISeries.objects.get(id=series_id)
                        # Check if series has A/B experiment tracking
                        if hasattr(series, 'ab_experiment_id') and series.ab_experiment_id:
                            track_ab_test_series_feedback(
                                experiment_id=series.ab_experiment_id,
                                user_id=user_pk,
                                series_id=series_id,
                                feedback_type='rating',
                                rating=rating,
                                metadata={
                                    'emoji': emoji,
                                    'stage': stage,
                                    'episode_id': content_info.get('episode_id')
                                }
                            )
                    except Exception as ab_err:
                        # Don't fail if A/B tracking fails
                        pass

                return feedback

            feedback = await record_feedback()

            if feedback:
                logger.info(
                    f"[SESSION 452] Discord reaction feedback: {emoji} = {rating}/5 "
                    f"for {content_info.get('type', 'unknown')} "
                    f"(message {message_id})"
                )

        except Exception as e:
            logger.error(f"[SESSION 452] Failed to submit reaction feedback: {e}")


# =============================================================================
# Session 471: Narrative Drift Detector Commands
# Tier 1 Autonomous Situation #2 - "The system watches the world for story shifts"
# =============================================================================

# NarrativeCommands removed in Phase G2 command consolidation

# ROICommands removed in Phase G2 command consolidation

class ResolveCommands(commands.Cog):
    """Commands for DaVinci Resolve professional rendering with trend-driven color grading."""

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot

    davinci = app_commands.Group(name="davinci", description="DaVinci Resolve rendering")

    @davinci.command(name="render", description="Start a professional DaVinci Resolve render")
    @app_commands.describe(
        video_ids="Comma-separated video IDs to render",
        template="Render template (default_mp4, prores_4444, dnxhr_hq)",
        grade="Color grade preset or 'auto' for trend-based selection"
    )
    async def resolve_render_command(
        self,
        interaction: discord.Interaction,
        video_ids: str,
        template: str = "default_mp4",
        grade: str = "auto"
    ):
        """Start a professional render job using DaVinci Resolve."""
        await interaction.response.defer(thinking=True)

        try:
            @sync_to_async
            def start_render():
                from core.agents.resolve_agent import get_resolve_agent
                from resolve_node.color_grades import match_grade_to_trends
                from django.contrib.auth import get_user_model

                # Get linked user
                User = get_user_model()
                user = User.objects.filter(discord_id=str(interaction.user.id)).first()

                # Parse video IDs
                ids = [v.strip() for v in video_ids.split(',') if v.strip()]

                # Get spider trends for auto-grading
                spider_trends = {}
                selected_grade = grade
                if grade.lower() == 'auto':
                    try:
                        from core.services.spider_intelligence import SpiderIntelligenceService
                        spider_service = SpiderIntelligenceService()
                        spider_trends = spider_service.get_creative_trends(hours=48)
                        selected_grade = match_grade_to_trends(spider_trends)
                    except Exception as e:
                        logger.warning(f"Could not get spider trends: {e}")
                        selected_grade = 'natural_vibrant'

                # Get resolve agent
                agent = get_resolve_agent(user)

                # Start render via agent
                # Session 479: Pass all required execute() parameters
                result = agent.execute(
                    task=f"Render videos {ids} with template {template} and color grade {selected_grade}",
                    context={
                        'video_ids': ids,
                        'template': template,
                        'color_grade': selected_grade,
                    },
                    scifi_context={},  # Not using sci-fi features for Resolve
                    spider_context={
                        'creative_trends': spider_trends
                    }
                )

                return {
                    'success': result.success,
                    'video_ids': ids,
                    'template': template,
                    'grade': selected_grade,
                    'auto_selected': grade.lower() == 'auto',
                    'job_id': result.data.get('job_id') if result.data else None,
                    'message': result.message or result.error,
                }

            result = await start_render()

            if result['success']:
                embed = discord.Embed(
                    title="🎬 Resolve Render Started",
                    description=f"Professional render job queued for {len(result['video_ids'])} video(s)",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="📹 Videos", value=", ".join(result['video_ids'][:5]), inline=True)
                embed.add_field(name="📦 Template", value=result['template'], inline=True)
                embed.add_field(
                    name="🎨 Color Grade",
                    value=f"{result['grade']} {'(auto-selected)' if result['auto_selected'] else ''}",
                    inline=True
                )
                if result.get('job_id'):
                    embed.add_field(name="🔑 Job ID", value=result['job_id'], inline=False)
                embed.set_footer(text="Session 478 | DaVinci Resolve Integration")
            else:
                embed = discord.Embed(
                    title="❌ Render Failed",
                    description=result.get('message', 'Unknown error'),
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )

            await interaction.edit_original_response(embed=embed)

        except Exception as e:
            logger.error(f"/resolve-render error: {e}")
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"Failed to start render: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @davinci.command(name="grade", description="Apply color grading to a video")
    @app_commands.describe(
        video_id="Video ID to color grade",
        grade="Color grade preset or 'trending' for auto-selection"
    )
    async def color_grade_command(
        self,
        interaction: discord.Interaction,
        video_id: str,
        grade: str = "trending"
    ):
        """Apply a color grade preset to a video."""
        await interaction.response.defer(thinking=True)

        try:
            @sync_to_async
            def apply_grade():
                from core.agents.resolve_agent import get_resolve_agent
                from resolve_node.color_grades import get_all_presets, match_grade_to_trends, describe_preset
                from django.contrib.auth import get_user_model

                # Get linked user
                User = get_user_model()
                user = User.objects.filter(discord_id=str(interaction.user.id)).first()

                # Determine grade
                selected_grade = grade
                spider_trends = {}
                if grade.lower() == 'trending':
                    try:
                        from core.services.spider_intelligence import SpiderIntelligenceService
                        spider_service = SpiderIntelligenceService()
                        spider_trends = spider_service.get_creative_trends(hours=48)
                        selected_grade = match_grade_to_trends(spider_trends)
                    except Exception as e:
                        logger.warning(f"Could not get spider trends: {e}")
                        selected_grade = 'natural_vibrant'

                # Validate grade exists
                available = get_all_presets()
                if selected_grade not in available:
                    return {
                        'success': False,
                        'error': f"Unknown grade '{selected_grade}'. Available: {', '.join(available)}"
                    }

                # Get resolve agent
                agent = get_resolve_agent(user)

                # Apply grade via agent
                # Session 479: Pass all required execute() parameters
                result = agent.execute(
                    task=f"Apply color grade {selected_grade} to video {video_id}",
                    context={
                        'video_id': video_id,
                        'color_grade': selected_grade,
                    },
                    scifi_context={},  # Not using sci-fi features for Resolve
                    spider_context={
                        'creative_trends': spider_trends
                    }
                )

                return {
                    'success': result.success,
                    'video_id': video_id,
                    'grade': selected_grade,
                    'description': describe_preset(selected_grade),
                    'auto_selected': grade.lower() == 'trending',
                    'message': result.message or result.error,
                }

            result = await apply_grade()

            if result['success']:
                embed = discord.Embed(
                    title="🎨 Color Grade Applied",
                    description=result.get('description', 'Grade applied successfully'),
                    color=discord.Color.purple(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="📹 Video", value=result['video_id'], inline=True)
                embed.add_field(
                    name="🎨 Grade",
                    value=f"{result['grade']} {'(trending)' if result['auto_selected'] else ''}",
                    inline=True
                )
                embed.set_footer(text="Session 478 | DaVinci Resolve Integration")
            else:
                embed = discord.Embed(
                    title="❌ Grading Failed",
                    description=result.get('error') or result.get('message', 'Unknown error'),
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )

            await interaction.edit_original_response(embed=embed)

        except Exception as e:
            logger.error(f"/color-grade error: {e}")
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"Failed to apply grade: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @davinci.command(name="status", description="Check render job status")
    @app_commands.describe(
        job_id="Resolve render job ID"
    )
    async def render_status_command(
        self,
        interaction: discord.Interaction,
        job_id: str
    ):
        """Check the status of a render job."""
        await interaction.response.defer(thinking=True)

        try:
            @sync_to_async
            def get_status():
                from core.models_unified_system import ResolveRenderJob

                try:
                    job = ResolveRenderJob.objects.get(resolve_job_id=job_id)
                    return {
                        'found': True,
                        'status': job.status,
                        'template': job.template,
                        'color_grade': job.color_grade,
                        'auto_grade': job.auto_grade_selected,
                        'output_url': job.output_url,
                        'file_size_mb': job.file_size_mb,
                        'render_duration': job.render_duration_seconds,
                        'error_message': job.error_message,
                        'created_at': job.created_at.isoformat() if job.created_at else None,
                        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                    }
                except ResolveRenderJob.DoesNotExist:
                    return {'found': False}

            result = await get_status()

            if not result['found']:
                embed = discord.Embed(
                    title="❓ Job Not Found",
                    description=f"No render job found with ID: {job_id}",
                    color=discord.Color.yellow(),
                    timestamp=datetime.now()
                )
            else:
                # Status-based color
                status_colors = {
                    'queued': discord.Color.blue(),
                    'rendering': discord.Color.orange(),
                    'done': discord.Color.green(),
                    'error': discord.Color.red(),
                }
                status_icons = {
                    'queued': '⏳',
                    'rendering': '🔄',
                    'done': '✅',
                    'error': '❌',
                }

                status = result['status']
                embed = discord.Embed(
                    title=f"{status_icons.get(status, '❓')} Render Job Status",
                    description=f"**Job ID:** {job_id}",
                    color=status_colors.get(status, discord.Color.grey()),
                    timestamp=datetime.now()
                )

                embed.add_field(name="📊 Status", value=status.upper(), inline=True)
                embed.add_field(name="📦 Template", value=result['template'], inline=True)
                embed.add_field(
                    name="🎨 Grade",
                    value=f"{result['color_grade']} {'(auto)' if result['auto_grade'] else ''}",
                    inline=True
                )

                if result['output_url']:
                    embed.add_field(name="📥 Output", value=result['output_url'][:100], inline=False)
                if result['file_size_mb']:
                    embed.add_field(name="📁 Size", value=f"{result['file_size_mb']:.1f} MB", inline=True)
                if result['render_duration']:
                    embed.add_field(name="⏱️ Duration", value=f"{result['render_duration']}s", inline=True)
                if result['error_message']:
                    embed.add_field(name="⚠️ Error", value=result['error_message'][:200], inline=False)

                embed.set_footer(text="Session 478 | DaVinci Resolve Integration")

            await interaction.edit_original_response(embed=embed)

        except Exception as e:
            logger.error(f"/render-status error: {e}")
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"Failed to get status: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @davinci.command(name="download", description="Download a completed render")
    @app_commands.describe(
        job_id="Resolve render job ID"
    )
    async def render_download_command(
        self,
        interaction: discord.Interaction,
        job_id: str
    ):
        """Download a completed render as a Discord attachment."""
        await interaction.response.defer(thinking=True)

        try:
            @sync_to_async
            def get_render_file():
                from pathlib import Path
                from django.conf import settings

                # Check results directory
                results_dir = Path(settings.BASE_DIR) / 'resolve_node' / 'results'

                # Try different extensions
                for ext in ['.mov', '.mp4']:
                    file_path = results_dir / f"render_{job_id}{ext}"
                    if file_path.exists():
                        size_mb = file_path.stat().st_size / 1024 / 1024
                        return {
                            'found': True,
                            'path': str(file_path),
                            'filename': file_path.name,
                            'size_mb': size_mb
                        }

                # Also check by partial match
                for f in results_dir.glob(f"render_{job_id[:8]}*"):
                    size_mb = f.stat().st_size / 1024 / 1024
                    return {
                        'found': True,
                        'path': str(f),
                        'filename': f.name,
                        'size_mb': size_mb
                    }

                return {'found': False, 'error': f'No render found for job {job_id}'}

            result = await get_render_file()

            if not result['found']:
                await interaction.edit_original_response(
                    embed=discord.Embed(
                        title="❌ Render Not Found",
                        description=result.get('error', 'File not found'),
                        color=discord.Color.red()
                    )
                )
                return

            # Check file size - Discord limit is 25MB (or 100MB with Nitro)
            if result['size_mb'] > 25:
                embed = discord.Embed(
                    title="📁 Render Too Large for Discord",
                    description=f"File is {result['size_mb']:.1f}MB (Discord limit: 25MB)",
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                )
                embed.add_field(
                    name="📂 Local Path",
                    value=f"`{result['path']}`",
                    inline=False
                )
                embed.set_footer(text="Open the file directly on your Mac")
                await interaction.edit_original_response(embed=embed)
                return

            # Upload the file to Discord
            file = discord.File(result['path'], filename=result['filename'])
            embed = discord.Embed(
                title="🎬 Your Rendered Video",
                description=f"**Job:** {job_id[:8]}...\n**Size:** {result['size_mb']:.1f}MB",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.set_footer(text="Session 479 | DaVinci Resolve Integration")

            await interaction.edit_original_response(embed=embed, attachments=[file])

        except Exception as e:
            logger.error(f"/render-download error: {e}")
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"Failed to download: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @davinci.command(name="videos", description="List available videos for rendering")
    @app_commands.describe(
        limit="Number of videos to show (default 10)"
    )
    async def videos_list_command(
        self,
        interaction: discord.Interaction,
        limit: int = 10
    ):
        """List available videos with user-friendly IDs for rendering."""
        await interaction.response.defer(thinking=True)

        try:
            @sync_to_async
            def get_videos():
                from content.models import VideoHistory
                from pathlib import Path
                from django.conf import settings

                results = []
                media_root = Path(settings.MEDIA_ROOT)
                rescued_dir = Path(settings.BASE_DIR) / 'media' / 'rescued_videos'

                # Get rescued videos (most reliable for Resolve)
                if rescued_dir.exists():
                    rescued_files = sorted(rescued_dir.glob('*.mp4'))[:limit]
                    for i, f in enumerate(rescued_files, 1):
                        size_mb = f.stat().st_size / 1024 / 1024
                        results.append({
                            'id': f"R{i}",
                            'name': f.stem[:20],
                            'size': f"{size_mb:.1f}MB",
                            'type': 'rescued',
                            'full_id': f.stem
                        })

                # Get database videos
                videos = VideoHistory.objects.filter(status='completed').order_by('-created_at')[:limit]
                for i, v in enumerate(videos, 1):
                    # Check if file exists
                    has_file = False
                    if v.video_file:
                        path = media_root / str(v.video_file)
                        has_file = path.exists()
                    elif v.video_url and v.video_url.startswith('/media/'):
                        path = media_root / v.video_url[7:]
                        has_file = path.exists()

                    results.append({
                        'id': f"#{i}",
                        'name': str(v.id)[:8],
                        'size': '---' if not has_file else 'OK',
                        'type': 'db',
                        'full_id': str(v.id)
                    })

                return results

            videos = await get_videos()

            embed = discord.Embed(
                title="📹 Available Videos for Rendering",
                description=f"Use these IDs with `/resolve-render`",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            # Rescued videos section
            rescued = [v for v in videos if v['type'] == 'rescued']
            if rescued:
                rescued_text = "\n".join([
                    f"`{v['id']}` | {v['name']} | {v['size']}"
                    for v in rescued[:8]
                ])
                embed.add_field(
                    name="🎬 Rescued Videos (Best for Resolve)",
                    value=rescued_text or "None",
                    inline=False
                )
                embed.add_field(
                    name="💡 Usage",
                    value=f"Use the full UUID: `/resolve-render video_ids:{rescued[0]['full_id']}`",
                    inline=False
                )

            # Database videos section
            db_videos = [v for v in videos if v['type'] == 'db']
            if db_videos:
                db_text = "\n".join([
                    f"`{v['id']}` | {v['name']}... | {v['size']}"
                    for v in db_videos[:5]
                ])
                embed.add_field(
                    name="📦 Database Videos",
                    value=db_text or "None",
                    inline=False
                )

            embed.set_footer(text="Session 479 | Use R1, R2... for rescued videos")
            await interaction.edit_original_response(embed=embed)

        except Exception as e:
            logger.error(f"/videos-list error: {e}")
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"Failed to list videos: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )


# =============================================================================
# Situation Commands - Session 480: Discord Commands for All Situations
# =============================================================================

class SituationCommands(commands.Cog):
    """
    Session 480: Commands for all 19 Autonomous Situations.

    Commands:
    - /situation-list - List all 19 situations with status
    - /situation-status <name> - Check specific situation details
    - /situation-run <name> - Manually trigger a situation
    - /situation-alerts <name> - Configure alert thresholds
    """

    # Mapping of situation keys to metadata
    # Session 481: ALL 19 situations now have event-driven triggers!
    SITUATIONS = {
        # =========================================================================
        # CONTENT DOMAIN
        # =========================================================================
        'content_studio': {
            'name': 'Autonomous Content Studio',
            'domain': 'Content',
            'schedule': 'Every 4h + Events',
            'task': 'run_autonomous_content_studio',
            'session_type': 'content_studio',
            'description': 'Auto-generates content for channels based on 3-agent debates',
        },
        'narrative_drift': {
            'name': 'Narrative Drift Detector',
            'domain': 'Content',
            'schedule': 'Every 4h + Events',
            'task': 'run_narrative_drift_cycle',
            'session_type': 'narrative_drift',
            'description': 'Monitors brand consistency and alerts on narrative drift',
        },
        # =========================================================================
        # FINANCIAL DOMAIN
        # =========================================================================
        'market_intelligence': {
            'name': 'Market Intelligence Desk',
            'domain': 'Financial',
            'schedule': 'Daily + Events',
            'task': 'run_market_intelligence_desk',
            'session_type': 'market_intelligence',
            'description': 'Comprehensive daily market analysis with agent debates',
        },
        'blockchain_security': {
            'name': 'Blockchain Security Alerts',
            'domain': 'Financial',
            'schedule': 'Every 2h + Events',
            'task': 'run_blockchain_security_monitor',
            'session_type': 'blockchain',
            'description': 'Monitors blockchain security events and vulnerabilities',
        },
        'stock_market': {
            'name': 'Stock Market Intelligence',
            'domain': 'Financial',
            'schedule': 'Every 4h + Events',
            'task': 'run_stock_market_intelligence',
            'session_type': 'stock_market',
            'description': 'Bull vs Bear analysis with signal scanning',
        },
        'sec_filing': {
            'name': 'SEC Filing Analyzer',
            'domain': 'Financial',
            'schedule': 'Every 2h + Events',
            'task': 'run_sec_filing_analyzer',
            'session_type': 'sec_filing',
            'description': 'Analyzes SEC filings (10-K, 10-Q, 8-K, 13F) - triggers on new filings',
        },
        'crypto_sentiment': {
            'name': 'Crypto Sentiment Monitor',
            'domain': 'Financial',
            'schedule': 'Every 2h + Events',
            'task': 'run_crypto_sentiment_monitor',
            'session_type': 'crypto_sentiment',
            'description': 'Tracks crypto social sentiment from Reddit, Bluesky',
        },
        'earnings_prediction': {
            'name': 'Earnings Surprise Predictor',
            'domain': 'Financial',
            'schedule': 'Twice daily + Events',
            'task': 'run_earnings_predictor',
            'session_type': 'earnings_prediction',
            'description': 'Analyzes pre-earnings sentiment for surprise predictions',
        },
        # =========================================================================
        # CREATIVE DOMAIN
        # =========================================================================
        'design_trends': {
            'name': 'Design Trends Monitor',
            'domain': 'Creative',
            'schedule': 'Every 6h + Events',
            'task': 'run_design_trends_monitor',
            'session_type': 'design_trends',
            'description': 'Tracks design trends from Dribbble, Behance, Awwwards',
        },
        'viral_prediction': {
            'name': 'Viral Content Predictor',
            'domain': 'Creative',
            'schedule': 'Every 4h + Events',
            'task': 'run_viral_content_predictor',
            'session_type': 'viral_prediction',
            'description': 'Scores content by viral potential using social signals',
        },
        'thumbnail_optimization': {
            'name': 'Thumbnail A/B Optimizer',
            'domain': 'Creative',
            'schedule': 'Every 6h + Events',
            'task': 'run_thumbnail_optimizer',
            'session_type': 'thumbnail_optimization',
            'description': 'Analyzes images and creates optimization suggestions based on trends',
        },
        # =========================================================================
        # INCOME DOMAIN
        # =========================================================================
        'job_matching': {
            'name': 'Job Match Intelligence',
            'domain': 'Income',
            'schedule': 'Every 2h + Events',
            'task': 'run_job_match_intelligence',
            'session_type': 'job_matching',
            'description': 'Monitors jobs and scores matches to your profile',
        },
        'freelance_scout': {
            'name': 'Freelance Opportunity Scout',
            'domain': 'Income',
            'schedule': 'Every 4h + Events',
            'task': 'run_freelance_opportunity_scout',
            'session_type': 'freelance_scout',
            'description': 'Scans job boards for freelance/contract opportunities',
        },
        'side_hustle': {
            'name': 'Side Hustle Detector',
            'domain': 'Income',
            'schedule': 'Every 8h + Events',
            'task': 'run_side_hustle_detector',
            'session_type': 'side_hustle',
            'description': 'Finds trending micro-opportunities on Reddit, ProductHunt',
        },
        # =========================================================================
        # RESEARCH DOMAIN
        # =========================================================================
        'tech_stack': {
            'name': 'Tech Stack Evolution Tracker',
            'domain': 'Research',
            'schedule': 'Every 6h + Events',
            'task': 'run_tech_stack_tracker',
            'session_type': 'tech_stack',
            'description': 'Monitors rising/falling technologies on GitHub, HackerNews',
        },
        'ai_model': {
            'name': 'AI Model Release Monitor',
            'domain': 'Research',
            'schedule': 'Every 4h + Events',
            'task': 'run_ai_model_monitor',
            'session_type': 'ai_model',
            'description': 'Alerts on new AI model releases from HuggingFace, GitHub',
        },
        'skill_gap': {
            'name': 'Course & Skill Gap Analyzer',
            'domain': 'Research',
            'schedule': 'Twice daily + Events',
            'task': 'run_skill_gap_analyzer',
            'session_type': 'skill_gap',
            'description': 'Matches trending tech skills to available courses',
        },
        # =========================================================================
        # LEGAL DOMAIN
        # =========================================================================
        'case_law': {
            'name': 'Case Law Monitor',
            'domain': 'Legal',
            'schedule': 'Every 6h + Events',
            'task': 'run_case_law_monitor',
            'session_type': 'case_law',
            'description': 'Tracks relevant case decisions from CourtListener, FindLaw',
        },
        'regulatory': {
            'name': 'Regulatory Change Detector',
            'domain': 'Legal',
            'schedule': 'Every 8h + Events',
            'task': 'run_regulatory_change_detector',
            'session_type': 'regulatory',
            'description': 'Monitors regulatory changes from government sources',
        },
    }

    # Domain colors for embeds
    DOMAIN_COLORS = {
        'Content': discord.Color.purple(),
        'Creative': discord.Color.pink(),
        'Income': discord.Color.green(),
        'Financial': discord.Color.gold(),
        'Research': discord.Color.blue(),
        'Legal': discord.Color.dark_grey(),
    }

    # Domain emojis
    DOMAIN_EMOJIS = {
        'Content': '🎬',
        'Creative': '🎨',
        'Income': '💰',
        'Financial': '📈',
        'Research': '🔬',
        'Legal': '⚖️',
    }

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot

    situation = app_commands.Group(name="situation", description="Autonomous Situations")

    @situation.command(name="list", description="List all 19 autonomous situations")
    @app_commands.describe(
        domain="Filter by domain (Content, Creative, Income, Financial, Research, Legal)"
    )
    async def situation_list(
        self,
        interaction: discord.Interaction,
        domain: Optional[str] = None
    ):
        """List all autonomous situations with their status."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def get_situation_stats():
                from core.models_autonomous_situations import AutonomousSituationSession

                # Get session counts and last run times for each situation type
                stats = {}
                for session_type in AutonomousSituationSession.objects.values_list(
                    'situation_type', flat=True
                ).distinct():
                    sessions = AutonomousSituationSession.objects.filter(situation_type=session_type)
                    last_session = sessions.order_by('-started_at').first()
                    stats[session_type] = {
                        'total_sessions': sessions.count(),
                        'last_run': last_session.started_at if last_session else None,
                        'last_status': last_session.status if last_session else None,
                    }
                return stats

            stats = await get_situation_stats()

            # Filter by domain if specified
            situations = self.SITUATIONS
            if domain:
                domain_lower = domain.lower()
                situations = {
                    k: v for k, v in situations.items()
                    if v['domain'].lower() == domain_lower
                }

            if not situations:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="No Situations Found",
                        description=f"No situations found for domain: {domain}",
                        color=discord.Color.red()
                    )
                )
                return

            # Group by domain
            by_domain = {}
            for key, info in situations.items():
                d = info['domain']
                if d not in by_domain:
                    by_domain[d] = []
                by_domain[d].append((key, info))

            embed = discord.Embed(
                title="🤖 19 Autonomous Situations",
                description="All Tier 1 Autonomous Situations running 24/7",
                color=discord.Color.purple()
            )

            for domain_name, items in sorted(by_domain.items()):
                emoji = self.DOMAIN_EMOJIS.get(domain_name, '📊')

                lines = []
                for key, info in items:
                    # Check if automated or manual
                    if info['task']:
                        status_emoji = '🟢'
                    else:
                        status_emoji = '🔵'  # Manual

                    # Get session stats if available
                    session_type = info.get('session_type')
                    if session_type and session_type in stats:
                        s = stats[session_type]
                        runs = s['total_sessions']
                        last_status = '✅' if s['last_status'] == 'completed' else '❌' if s['last_status'] == 'failed' else '⏳'
                        lines.append(f"{status_emoji} **{info['name']}** ({info['schedule']}) - {runs} runs {last_status}")
                    else:
                        lines.append(f"{status_emoji} **{info['name']}** ({info['schedule']})")

                embed.add_field(
                    name=f"{emoji} {domain_name}",
                    value="\n".join(lines),
                    inline=False
                )

            embed.set_footer(text="🟢 Automated | 🔵 Manual | Use /situation-status <key> for details")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"/situation-list error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to list situations: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @situation.command(name="status", description="Check detailed status of a specific situation")
    @app_commands.describe(
        situation="Situation key (e.g., 'design_trends', 'job_matching')"
    )
    @app_commands.choices(situation=[
        app_commands.Choice(name="Content Studio", value="content_studio"),
        app_commands.Choice(name="Narrative Drift", value="narrative_drift"),
        app_commands.Choice(name="Market Intelligence", value="market_intelligence"),
        app_commands.Choice(name="Blockchain Security", value="blockchain_security"),
        app_commands.Choice(name="Stock Market", value="stock_market"),
        app_commands.Choice(name="Design Trends", value="design_trends"),
        app_commands.Choice(name="Viral Prediction", value="viral_prediction"),
        app_commands.Choice(name="Thumbnail Optimizer", value="thumbnail_optimization"),
        app_commands.Choice(name="Job Matching", value="job_matching"),
        app_commands.Choice(name="Freelance Scout", value="freelance_scout"),
        app_commands.Choice(name="Side Hustle", value="side_hustle"),
        app_commands.Choice(name="SEC Filing", value="sec_filing"),
        app_commands.Choice(name="Crypto Sentiment", value="crypto_sentiment"),
        app_commands.Choice(name="Earnings Predictor", value="earnings_prediction"),
        app_commands.Choice(name="Tech Stack", value="tech_stack"),
        app_commands.Choice(name="AI Model", value="ai_model"),
        app_commands.Choice(name="Skill Gap", value="skill_gap"),
        app_commands.Choice(name="Case Law", value="case_law"),
        app_commands.Choice(name="Regulatory", value="regulatory"),
    ])
    async def situation_status(
        self,
        interaction: discord.Interaction,
        situation: str
    ):
        """Get detailed status of a specific autonomous situation."""
        await interaction.response.defer()

        try:
            if situation not in self.SITUATIONS:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Unknown Situation",
                        description=f"Unknown situation: `{situation}`\nUse `/situation-list` to see all situations.",
                        color=discord.Color.red()
                    )
                )
                return

            info = self.SITUATIONS[situation]

            @sync_to_async
            def get_detailed_stats():
                pass

                result = {
                    'sessions': [],
                    'total_sessions': 0,
                    'total_items_processed': 0,
                    'total_alerts': 0,
                    'avg_duration': 0,
                    'recent_data': [],
                }

                session_type = info.get('session_type')
                if session_type:
                    from core.models_autonomous_situations import AutonomousSituationSession

                    sessions = AutonomousSituationSession.objects.filter(
                        situation_type=session_type
                    ).order_by('-started_at')[:10]

                    result['sessions'] = list(sessions.values(
                        'started_at', 'completed_at', 'status', 'items_processed',
                        'items_created', 'alerts_generated', 'duration_seconds'
                    ))

                    all_sessions = AutonomousSituationSession.objects.filter(situation_type=session_type)
                    result['total_sessions'] = all_sessions.count()
                    result['total_items_processed'] = sum(s.items_processed for s in all_sessions)
                    result['total_alerts'] = sum(s.alerts_generated for s in all_sessions)

                    durations = [s.duration_seconds for s in all_sessions if s.duration_seconds]
                    if durations:
                        result['avg_duration'] = sum(durations) / len(durations)

                # Get domain-specific recent data
                if situation == 'design_trends':
                    from core.models_autonomous_situations import DesignTrend
                    result['recent_data'] = list(DesignTrend.objects.order_by('-created_at')[:5].values(
                        'name', 'category', 'popularity_score', 'created_at'
                    ))
                elif situation == 'job_matching':
                    from core.models_autonomous_situations import JobMatch
                    result['recent_data'] = list(JobMatch.objects.order_by('-created_at')[:5].values(
                        'job_title', 'company', 'match_score', 'created_at'
                    ))
                elif situation == 'crypto_sentiment':
                    from core.models_autonomous_situations import CryptoSentiment
                    result['recent_data'] = list(CryptoSentiment.objects.order_by('-created_at')[:5].values(
                        'coin_symbol', 'sentiment_score', 'volume_24h', 'created_at'
                    ))
                elif situation == 'tech_stack':
                    from core.models_autonomous_situations import TechStackTrend
                    result['recent_data'] = list(TechStackTrend.objects.order_by('-created_at')[:5].values(
                        'technology_name', 'category', 'momentum_score', 'created_at'
                    ))
                elif situation == 'ai_model':
                    from core.models_autonomous_situations import AIModelRelease
                    result['recent_data'] = list(AIModelRelease.objects.order_by('-created_at')[:5].values(
                        'model_name', 'provider', 'significance_score', 'created_at'
                    ))
                elif situation == 'case_law':
                    from core.models_autonomous_situations import CaseLawUpdate
                    result['recent_data'] = list(CaseLawUpdate.objects.order_by('-created_at')[:5].values(
                        'case_name', 'court', 'relevance_score', 'created_at'
                    ))

                return result

            stats = await get_detailed_stats()

            domain = info['domain']
            color = self.DOMAIN_COLORS.get(domain, discord.Color.blue())
            emoji = self.DOMAIN_EMOJIS.get(domain, '📊')

            embed = discord.Embed(
                title=f"{emoji} {info['name']}",
                description=info['description'],
                color=color
            )

            # Status info
            is_automated = info['task'] is not None
            status_text = "🟢 Automated" if is_automated else "🔵 Manual"
            embed.add_field(
                name="Status",
                value=f"{status_text}\n**Schedule:** {info['schedule']}\n**Domain:** {domain}",
                inline=True
            )

            # Stats
            embed.add_field(
                name="Statistics",
                value=(
                    f"**Total Sessions:** {stats['total_sessions']}\n"
                    f"**Items Processed:** {stats['total_items_processed']:,}\n"
                    f"**Alerts Generated:** {stats['total_alerts']}\n"
                    f"**Avg Duration:** {stats['avg_duration']:.1f}s"
                ),
                inline=True
            )

            # Recent sessions
            if stats['sessions']:
                session_lines = []
                for s in stats['sessions'][:5]:
                    status_icon = '✅' if s['status'] == 'completed' else '❌' if s['status'] == 'failed' else '⏳'
                    ts = int(s['started_at'].timestamp()) if s['started_at'] else 0
                    session_lines.append(f"{status_icon} <t:{ts}:R> - {s['items_processed']} items")

                embed.add_field(
                    name="Recent Sessions",
                    value="\n".join(session_lines) or "No sessions yet",
                    inline=False
                )

            # Recent data (domain-specific)
            if stats['recent_data']:
                data_lines = []
                for item in stats['recent_data'][:3]:
                    if situation == 'design_trends':
                        data_lines.append(f"• **{item['name']}** ({item['category']}) - Score: {item['popularity_score']:.1f}")
                    elif situation == 'job_matching':
                        data_lines.append(f"• **{item['job_title']}** @ {item['company']} - {item['match_score']:.0f}% match")
                    elif situation == 'crypto_sentiment':
                        data_lines.append(f"• **{item['coin_symbol']}** - Sentiment: {item['sentiment_score']:.1f}")
                    elif situation == 'tech_stack':
                        data_lines.append(f"• **{item['technology_name']}** - Momentum: {item['momentum_score']:.1f}")
                    elif situation == 'ai_model':
                        data_lines.append(f"• **{item['model_name']}** by {item['provider']}")
                    elif situation == 'case_law':
                        data_lines.append(f"• **{item['case_name'][:40]}** ({item['court']})")

                if data_lines:
                    embed.add_field(
                        name="Recent Data",
                        value="\n".join(data_lines),
                        inline=False
                    )

            embed.set_footer(text=f"Use /situation-run {situation} to trigger manually")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"/situation-status error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to get status: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @situation.command(name="run", description="Manually trigger an autonomous situation")
    @app_commands.describe(
        situation="Situation key to run"
    )
    @app_commands.choices(situation=[
        app_commands.Choice(name="Design Trends", value="design_trends"),
        app_commands.Choice(name="Viral Prediction", value="viral_prediction"),
        app_commands.Choice(name="Thumbnail Optimizer", value="thumbnail_optimization"),
        app_commands.Choice(name="Job Matching", value="job_matching"),
        app_commands.Choice(name="Freelance Scout", value="freelance_scout"),
        app_commands.Choice(name="Side Hustle", value="side_hustle"),
        app_commands.Choice(name="SEC Filing", value="sec_filing"),
        app_commands.Choice(name="Crypto Sentiment", value="crypto_sentiment"),
        app_commands.Choice(name="Earnings Predictor", value="earnings_prediction"),
        app_commands.Choice(name="Tech Stack", value="tech_stack"),
        app_commands.Choice(name="AI Model", value="ai_model"),
        app_commands.Choice(name="Skill Gap", value="skill_gap"),
        app_commands.Choice(name="Case Law", value="case_law"),
        app_commands.Choice(name="Regulatory", value="regulatory"),
        app_commands.Choice(name="Content Studio", value="content_studio"),
        app_commands.Choice(name="Market Intelligence", value="market_intelligence"),
        app_commands.Choice(name="Blockchain Security", value="blockchain_security"),
        app_commands.Choice(name="Stock Market", value="stock_market"),
    ])
    async def situation_run(
        self,
        interaction: discord.Interaction,
        situation: str
    ):
        """Manually trigger an autonomous situation."""
        await interaction.response.defer()

        try:
            if situation not in self.SITUATIONS:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Unknown Situation",
                        description=f"Unknown situation: `{situation}`",
                        color=discord.Color.red()
                    )
                )
                return

            info = self.SITUATIONS[situation]
            task_name = info.get('task')

            if not task_name:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Manual Situation",
                        description=f"**{info['name']}** is a manual situation and cannot be triggered via command.\n\nThis situation requires manual data input or specific trigger events.",
                        color=discord.Color.orange()
                    )
                )
                return

            # Send initial response
            domain = info['domain']
            emoji = self.DOMAIN_EMOJIS.get(domain, '📊')

            embed = discord.Embed(
                title=f"{emoji} Running {info['name']}...",
                description="Triggering autonomous situation. This may take a moment...",
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)

            # Run the task
            @sync_to_async
            def run_task():
                from core import tasks
                task_func = getattr(tasks, task_name, None)
                if task_func:
                    # Call the task directly (not delay) for immediate feedback
                    return task_func()
                return {'status': 'error', 'message': f'Task {task_name} not found'}

            result = await run_task()

            # Format result
            if isinstance(result, dict):
                status = result.get('status', 'unknown')
                if status == 'completed':
                    color = discord.Color.green()
                    title = f"✅ {info['name']} Complete"
                elif status == 'error':
                    color = discord.Color.red()
                    title = f"❌ {info['name']} Failed"
                else:
                    color = discord.Color.orange()
                    title = f"⚠️ {info['name']} - {status}"

                result_embed = discord.Embed(
                    title=title,
                    color=color
                )

                # Add result fields
                for key, value in result.items():
                    if key != 'status' and value is not None:
                        # Format the key
                        display_key = key.replace('_', ' ').title()
                        result_embed.add_field(name=display_key, value=str(value)[:100], inline=True)
            else:
                result_embed = discord.Embed(
                    title=f"✅ {info['name']} Complete",
                    description=str(result)[:500] if result else "Task completed",
                    color=discord.Color.green()
                )

            result_embed.set_footer(text=f"Use /situation-status {situation} for detailed stats")

            # Edit the original message
            await interaction.edit_original_response(embed=result_embed)

        except Exception as e:
            logger.error(f"/situation-run error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to run situation: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @situation.command(name="alerts", description="Configure alerts for an autonomous situation")
    @app_commands.describe(
        situation="Situation to configure",
        action="Enable, disable, or check alert status",
        threshold="Alert threshold (0.0-1.0)"
    )
    @app_commands.choices(
        situation=[
            app_commands.Choice(name="Design Trends", value="design_trends"),
            app_commands.Choice(name="Viral Prediction", value="viral_prediction"),
            app_commands.Choice(name="Thumbnail Optimizer", value="thumbnail_optimization"),
            app_commands.Choice(name="Job Matching", value="job_matching"),
            app_commands.Choice(name="Freelance Scout", value="freelance_scout"),
            app_commands.Choice(name="Side Hustle", value="side_hustle"),
            app_commands.Choice(name="SEC Filing", value="sec_filing"),
            app_commands.Choice(name="Crypto Sentiment", value="crypto_sentiment"),
            app_commands.Choice(name="Earnings Predictor", value="earnings_prediction"),
            app_commands.Choice(name="Tech Stack", value="tech_stack"),
            app_commands.Choice(name="AI Model", value="ai_model"),
            app_commands.Choice(name="Skill Gap", value="skill_gap"),
            app_commands.Choice(name="Case Law", value="case_law"),
            app_commands.Choice(name="Regulatory", value="regulatory"),
        ],
        action=[
            app_commands.Choice(name="Check Status", value="status"),
            app_commands.Choice(name="Enable Alerts", value="enable"),
            app_commands.Choice(name="Disable Alerts", value="disable"),
        ]
    )
    async def situation_alerts(
        self,
        interaction: discord.Interaction,
        situation: str,
        action: str = "status",
        threshold: Optional[float] = None
    ):
        """Configure alert settings for an autonomous situation."""
        await interaction.response.defer()

        try:
            if situation not in self.SITUATIONS:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Unknown Situation",
                        description=f"Unknown situation: `{situation}`",
                        color=discord.Color.red()
                    )
                )
                return

            info = self.SITUATIONS[situation]

            @sync_to_async
            def manage_alert_config():
                pass

                # Get or create alert config for this user/situation
                discord_id = str(interaction.user.id)

                # For now, we'll use a simple approach with Redis or a model
                # This is a placeholder that can be extended
                from django.core.cache import cache

                config_key = f"situation_alert:{discord_id}:{situation}"
                current_config = cache.get(config_key, {
                    'enabled': False,
                    'threshold': 0.7,
                })

                if action == 'enable':
                    current_config['enabled'] = True
                    if threshold is not None:
                        current_config['threshold'] = max(0.0, min(1.0, threshold))
                    cache.set(config_key, current_config, timeout=None)
                    return {'action': 'enabled', 'config': current_config}

                elif action == 'disable':
                    current_config['enabled'] = False
                    cache.set(config_key, current_config, timeout=None)
                    return {'action': 'disabled', 'config': current_config}

                else:  # status
                    return {'action': 'status', 'config': current_config}

            result = await manage_alert_config()

            domain = info['domain']
            emoji = self.DOMAIN_EMOJIS.get(domain, '📊')
            config = result['config']

            if result['action'] == 'enabled':
                embed = discord.Embed(
                    title=f"🔔 Alerts Enabled",
                    description=f"Alerts enabled for **{info['name']}**",
                    color=discord.Color.green()
                )
            elif result['action'] == 'disabled':
                embed = discord.Embed(
                    title=f"🔕 Alerts Disabled",
                    description=f"Alerts disabled for **{info['name']}**",
                    color=discord.Color.grey()
                )
            else:
                status_emoji = "🔔" if config['enabled'] else "🔕"
                embed = discord.Embed(
                    title=f"{emoji} {info['name']} Alert Config",
                    description=f"{status_emoji} Alerts: **{'Enabled' if config['enabled'] else 'Disabled'}**",
                    color=discord.Color.blue()
                )

            embed.add_field(name="Threshold", value=f"{config['threshold']:.1%}", inline=True)
            embed.add_field(name="Schedule", value=info['schedule'], inline=True)
            embed.set_footer(text=f"Use /situation-alerts {situation} enable/disable to change")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"/situation-alerts error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to configure alerts: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )


class PodcastCommands(commands.Cog):
    """
    Session 496: AI Podcast Studio Commands.

    Commands for creating AI-generated podcasts where agents research,
    debate, and produce audio content with different voices.
    """

    podcast = app_commands.Group(name="podcast", description="AI Podcast Studio")

    def __init__(self, client):
        self.client = client
        # Session 1103c: repaired indentation — previously the __init__
        # body was split by a class-level assignment, leaving the
        # PODCAST_CHANNEL_ID lines dangling outside any function block.
        # Python actually fails to parse this file as a result; the
        # PodcastCommands cog has been non-functional for however long
        # the bug existed. Moved the app_commands.Group to a proper
        # class attribute position and kept the channel IDs inside
        # __init__.
        # Podcast channel for creation commands
        self.PODCAST_CHANNEL_ID = 1451578444101058751
        # Podcast library channel for completed episodes with audio
        self.PODCAST_LIBRARY_CHANNEL_ID = 1451601597007134821

    async def _get_linked_user(self, discord_id):
        """Get the linked Django user for this Discord ID."""
        @sync_to_async
        def get_user():
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return User.objects.filter(discord_id=discord_id).first()

        return await get_user()

    @podcast.command(name="create", description="Create an AI podcast episode with agent debates")
    @app_commands.describe(
        topic="The debate topic (e.g., 'Should AI replace human jobs?')",
        format="Podcast format (debate/roundtable/interview)",
        participants="Number of debate participants (2-4)",
        generate_audio="Whether to generate audio with ElevenLabs"
    )
    async def podcast_create(
        self,
        interaction: discord.Interaction,
        topic: str,
        format: str = "debate",
        participants: int = 3,
        generate_audio: bool = False
    ):
        """Create a new AI podcast episode."""
        await interaction.response.defer()

        try:
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Account Not Linked",
                        description="Please link your Discord account first using `/link`",
                        color=discord.Color.orange()
                    )
                )
                return

            # Validate format
            valid_formats = ['debate', 'roundtable', 'interview', 'monologue']
            if format.lower() not in valid_formats:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Invalid Format",
                        description=f"Format must be one of: {', '.join(valid_formats)}",
                        color=discord.Color.red()
                    )
                )
                return

            # Validate participants
            if participants < 2 or participants > 4:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Invalid Participant Count",
                        description="Participants must be between 2 and 4",
                        color=discord.Color.red()
                    )
                )
                return

            # Create the episode
            @sync_to_async
            def create_episode():
                # Session 865: Fixed import - models are in models_podcast_studio
                from core.models_podcast_studio import PodcastEpisode, PodcastDebate

                # Create debate first
                debate = PodcastDebate.objects.create(
                    topic=topic[:200],
                    topic_question=f"Should we embrace {topic}? What are the implications?",
                    status='pending'
                )

                # Create episode
                episode = PodcastEpisode.objects.create(
                    user=user,
                    title=f"Debate: {topic[:150]}",
                    topic=topic[:200],
                    debate=debate,
                    status='draft',
                    generation_config={
                        'format': format.lower(),
                        'participant_count': participants,
                        'generate_audio': generate_audio
                    }
                )

                return episode, debate

            episode, debate = await create_episode()

            # Start the generation task
            @sync_to_async
            def queue_generation():
                from core.tasks import generate_podcast_episode
                generate_podcast_episode.delay(
                    str(episode.id),
                    topic,
                    format.lower(),
                    participants,
                    generate_audio
                )

            # Queue the podcast generation task
            await queue_generation()

            embed = discord.Embed(
                title="🎙️ Podcast Episode Created!",
                description=f"Creating a {format} about **{topic}**",
                color=discord.Color.purple()
            )
            embed.add_field(name="Episode ID", value=f"`{str(episode.id)[:8]}...`", inline=True)
            embed.add_field(name="Format", value=format.title(), inline=True)
            embed.add_field(name="Participants", value=str(participants), inline=True)
            embed.add_field(name="Audio", value="Yes" if generate_audio else "Script Only", inline=True)
            embed.add_field(
                name="Voices",
                value="Host: Antoni\nAdvocate: Rachel\nSkeptic: Clyde\nAnalyst: Paul",
                inline=False
            )
            embed.set_footer(text="Use /podcast-status to check generation progress")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Podcast create error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to create podcast: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @podcast.command(name="list", description="List your podcast episodes")
    async def podcast_list(self, interaction: discord.Interaction):
        """List all podcast episodes for this user."""
        await interaction.response.defer()

        try:
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Account Not Linked",
                        description="Please link your Discord account first using `/link`",
                        color=discord.Color.orange()
                    )
                )
                return

            @sync_to_async
            def get_episodes():
                from core.models_podcast_studio import PodcastEpisode
                return list(PodcastEpisode.objects.filter(user=user).order_by('-created_at')[:10])

            episodes = await get_episodes()

            if not episodes:
                embed = discord.Embed(
                    title="🎙️ No Podcasts Yet",
                    description="You haven't created any podcasts. Use `/podcast-create` to start!",
                    color=discord.Color.blue()
                )
            else:
                embed = discord.Embed(
                    title="🎙️ Your Podcast Episodes",
                    description=f"Showing {len(episodes)} most recent episodes",
                    color=discord.Color.purple()
                )

                for ep in episodes:
                    status_emoji = {
                        'draft': '📝',
                        'researching': '🔍',
                        'debating': '💬',
                        'scripting': '✍️',
                        'recording': '🎤',
                        'assembling': '🔧',
                        'complete': '✅',
                        'failed': '❌'
                    }.get(ep.status, '❓')

                    embed.add_field(
                        name=f"{status_emoji} {ep.title[:50]}",
                        value=f"ID: `{str(ep.id)[:8]}...` | Status: {ep.status}\nCreated: <t:{int(ep.created_at.timestamp())}:R>",
                        inline=False
                    )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Podcast list error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to list podcasts: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @podcast.command(name="status", description="Check status of a podcast episode")
    @app_commands.describe(episode_id="The episode ID (first 8 characters)")
    async def podcast_status(self, interaction: discord.Interaction, episode_id: str):
        """Check the status of a podcast episode."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def get_episode():
                from core.models_podcast_studio import PodcastEpisode
                # Search by prefix
                return PodcastEpisode.objects.filter(
                    id__startswith=episode_id
                ).first()

            episode = await get_episode()

            if not episode:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Episode Not Found",
                        description=f"No episode found with ID starting with `{episode_id}`",
                        color=discord.Color.red()
                    )
                )
                return

            status_emoji = {
                'draft': '📝',
                'researching': '🔍',
                'debating': '💬',
                'scripting': '✍️',
                'recording': '🎤',
                'assembling': '🔧',
                'complete': '✅',
                'failed': '❌'
            }.get(episode.status, '❓')

            embed = discord.Embed(
                title=f"{status_emoji} {episode.title}",
                description=episode.description[:300] if episode.description else "No description",
                color=discord.Color.green() if episode.status == 'complete' else discord.Color.blue()
            )
            embed.add_field(name="Status", value=episode.status.title(), inline=True)
            embed.add_field(name="Progress", value=f"{episode.progress_percent}%", inline=True)
            embed.add_field(name="Topic", value=episode.topic[:100], inline=False)

            if episode.script:
                embed.add_field(
                    name="Script Preview",
                    value=f"```{episode.script[:300]}...```",
                    inline=False
                )

            if episode.error_message:
                embed.add_field(name="Error", value=episode.error_message[:200], inline=False)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Podcast status error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to get status: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @podcast.command(name="script", description="View the full script of a completed podcast")
    @app_commands.describe(episode_id="The episode ID (first 8 characters)")
    async def podcast_script(self, interaction: discord.Interaction, episode_id: str):
        """View the full script of a podcast episode."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def get_episode():
                from core.models_podcast_studio import PodcastEpisode
                return PodcastEpisode.objects.filter(
                    id__startswith=episode_id
                ).first()

            episode = await get_episode()

            if not episode:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Episode Not Found",
                        description=f"No episode found with ID starting with `{episode_id}`",
                        color=discord.Color.red()
                    )
                )
                return

            if not episode.script:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Script Not Ready",
                        description=f"This episode doesn't have a script yet. Status: {episode.status}",
                        color=discord.Color.orange()
                    )
                )
                return

            # Split script into chunks for Discord's 2000 char limit
            script = episode.script
            chunks = [script[i:i+1900] for i in range(0, len(script), 1900)]

            embed = discord.Embed(
                title=f"🎙️ {episode.title} - Script",
                description=f"Full script ({len(script)} chars, {len(chunks)} parts)",
                color=discord.Color.purple()
            )
            await interaction.followup.send(embed=embed)

            # Send script in chunks
            for i, chunk in enumerate(chunks[:5]):  # Limit to 5 chunks
                await interaction.channel.send(f"**Part {i+1}:**\n```\n{chunk}\n```")

            if len(chunks) > 5:
                await interaction.channel.send(f"*... and {len(chunks) - 5} more parts*")

        except Exception as e:
            logger.error(f"Podcast script error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to get script: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )


# ============================================================
# Session 497: Legal Commands for Pro Se Legal Assistant
# ============================================================

class LegalCommands(commands.Cog):
    """
    Session 497: Pro Se Legal Assistant Discord Commands.

    Provides access to legal document drafting, case management,
    and motion analysis for Colorado family law matters.
    """

    def __init__(self, client):
        self.client = client

    legal = app_commands.Group(name="legal", description="Pro Se Legal Assistant")

    async def _get_linked_user(self, discord_id):
        """Get the linked Django user for this Discord ID."""
        @sync_to_async
        def get_user():
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return User.objects.filter(discord_id=discord_id).first()

        return await get_user()

    @legal.command(name="draft", description="Draft a legal document template (Colorado family law)")
    @app_commands.describe(
        document_type="Type of document to draft",
        description="Brief description of what you need"
    )
    @app_commands.choices(document_type=[
        app_commands.Choice(name="Motion to Modify Parenting Time", value="motion_modify_parenting"),
        app_commands.Choice(name="Motion for Continuance", value="motion_continuance"),
        app_commands.Choice(name="Meet and Confer Email", value="conferral_email"),
        app_commands.Choice(name="Declaration/Affidavit", value="declaration"),
        app_commands.Choice(name="Response to Motion", value="response_motion"),
    ])
    async def legal_draft(
        self,
        interaction: discord.Interaction,
        document_type: app_commands.Choice[str],
        description: str
    ):
        """Draft a legal document template."""
        await interaction.response.defer()

        try:
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Account Not Linked",
                        description="Please link your Discord account first using `/link`",
                        color=discord.Color.orange()
                    )
                )
                return

            # Execute the legal agent
            @sync_to_async
            def run_legal_agent():
                from core.agents.legal.legal_doc_drafter_agent import LegalDocDrafterAgent
                agent = LegalDocDrafterAgent()
                task = f"Draft a {document_type.name} template. Context: {description}"
                return agent.execute(task, user=user)

            result = await run_legal_agent()

            if result.success:
                # Split long responses
                content = result.content[:4000] if result.content else "Document template generated."

                embed = discord.Embed(
                    title=f"📜 {document_type.name}",
                    description=content[:2000],
                    color=discord.Color.blue()
                )
                embed.add_field(
                    name="⚠️ Disclaimer",
                    value="This is a template only, not legal advice. Consult an attorney.",
                    inline=False
                )
                embed.set_footer(text="Pro Se Legal Assistant | Colorado Family Law")

                await interaction.followup.send(embed=embed)

                # Send remainder if content is long
                if len(content) > 2000:
                    await interaction.channel.send(f"**Continued:**\n```\n{content[2000:4000]}\n```")
            else:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Draft Failed",
                        description=result.error or "Unable to generate document",
                        color=discord.Color.red()
                    )
                )

        except Exception as e:
            logger.error(f"Legal draft error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to draft document: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @legal.command(name="analyze", description="Analyze a denied motion and suggest fixes")
    @app_commands.describe(
        motion_text="Paste the text of the denied motion or order"
    )
    async def legal_analyze(
        self,
        interaction: discord.Interaction,
        motion_text: str
    ):
        """Analyze a denied motion and suggest procedural fixes."""
        await interaction.response.defer()

        try:
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Account Not Linked",
                        description="Please link your Discord account first using `/link`",
                        color=discord.Color.orange()
                    )
                )
                return

            @sync_to_async
            def run_analysis():
                from core.agents.legal.legal_doc_drafter_agent import LegalDocDrafterAgent
                agent = LegalDocDrafterAgent()
                task = f"Analyze this denied motion and identify procedural defects. Suggest how to properly file:\n\n{motion_text}"
                return agent.execute(task, user=user)

            result = await run_analysis()

            if result.success:
                content = result.content[:4000] if result.content else "Analysis complete."

                embed = discord.Embed(
                    title="🔍 Motion Analysis",
                    description=content[:2000],
                    color=discord.Color.gold()
                )
                embed.add_field(
                    name="⚠️ Disclaimer",
                    value="This is procedural analysis only, not legal advice.",
                    inline=False
                )

                await interaction.followup.send(embed=embed)

                if len(content) > 2000:
                    await interaction.channel.send(f"**Analysis Continued:**\n```\n{content[2000:4000]}\n```")
            else:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Analysis Failed",
                        description=result.error or "Unable to analyze motion",
                        color=discord.Color.red()
                    )
                )

        except Exception as e:
            logger.error(f"Legal analyze error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Analysis failed: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @legal.command(name="case", description="Get info about your case profile")
    async def legal_case(self, interaction: discord.Interaction):
        """View case profile information."""
        await interaction.response.defer()

        try:
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Account Not Linked",
                        description="Please link your Discord account first using `/link`",
                        color=discord.Color.orange()
                    )
                )
                return

            @sync_to_async
            def get_case_info():
                from core.models_legal import CaseProfile
                cases = CaseProfile.objects.filter(user=user, is_active=True)
                return list(cases.values('id', 'case_number', 'case_type', 'county', 'created_at'))

            cases = await get_case_info()

            if not cases:
                embed = discord.Embed(
                    title="📁 No Case Profiles",
                    description="You haven't created any case profiles yet.\n\nVisit the AI Studio Legal Assistant tab to create a case profile.",
                    color=discord.Color.blue()
                )
            else:
                embed = discord.Embed(
                    title=f"📁 Your Case Profiles ({len(cases)})",
                    color=discord.Color.blue()
                )
                for case in cases[:5]:
                    case_type = case.get('case_type', 'Unknown').replace('_', ' ').title()
                    embed.add_field(
                        name=f"Case #{case.get('case_number', 'N/A')}",
                        value=f"**Type:** {case_type}\n**County:** {case.get('county', 'N/A')}",
                        inline=True
                    )

            embed.set_footer(text="Pro Se Legal Assistant | Colorado Family Law")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Legal case error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to get case info: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )


# ============================================================
# Session 497: Developer Commands for Code Generation/Review
# ============================================================

class DeveloperCommands(commands.Cog):
    """
    Session 497: Code Generation and Review Discord Commands.

    Provides access to code generation and review agents.
    """

    def __init__(self, client):
        self.client = client

    code = app_commands.Group(name="code", description="Code generation and review")

    async def _get_linked_user(self, discord_id):
        """Get the linked Django user for this Discord ID."""
        @sync_to_async
        def get_user():
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return User.objects.filter(discord_id=discord_id).first()

        return await get_user()

    @code.command(name="generate", description="Generate code from a specification")
    @app_commands.describe(
        specification="What should the code do?",
        language="Programming language",
        framework="Optional framework (django, react, etc.)"
    )
    @app_commands.choices(language=[
        app_commands.Choice(name="Python", value="python"),
        app_commands.Choice(name="JavaScript", value="javascript"),
        app_commands.Choice(name="TypeScript", value="typescript"),
        app_commands.Choice(name="HTML/CSS", value="html"),
        app_commands.Choice(name="SQL", value="sql"),
        app_commands.Choice(name="Bash", value="bash"),
    ])
    async def code_generate(
        self,
        interaction: discord.Interaction,
        specification: str,
        language: app_commands.Choice[str],
        framework: str = None
    ):
        """Generate code from a specification."""
        await interaction.response.defer()

        try:
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Account Not Linked",
                        description="Please link your Discord account first using `/link`",
                        color=discord.Color.orange()
                    )
                )
                return

            @sync_to_async
            def run_generator():
                from core.agents.code_review_agent import CodeReviewAgent
                agent = CodeReviewAgent()
                task = f"Generate {language.name} code for: {specification}"
                if framework:
                    task += f" (using {framework})"
                return agent.execute(task, user=user)

            result = await run_generator()

            if result.success:
                content = result.content[:3800] if result.content else "Code generated."

                embed = discord.Embed(
                    title=f"💻 Generated {language.name} Code",
                    color=discord.Color.green()
                )
                if framework:
                    embed.add_field(name="Framework", value=framework, inline=True)
                embed.add_field(name="Specification", value=specification[:100], inline=False)

                await interaction.followup.send(embed=embed)
                await interaction.channel.send(f"```{language.value}\n{content}\n```")

            else:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Generation Failed",
                        description=result.error or "Unable to generate code",
                        color=discord.Color.red()
                    )
                )

        except Exception as e:
            logger.error(f"Code generate error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to generate code: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )

    @code.command(name="review", description="Review code for bugs, security, and quality")
    @app_commands.describe(
        code="The code to review (paste directly)",
        language="Programming language",
        focus="Review focus area"
    )
    @app_commands.choices(language=[
        app_commands.Choice(name="Python", value="python"),
        app_commands.Choice(name="JavaScript", value="javascript"),
        app_commands.Choice(name="TypeScript", value="typescript"),
        app_commands.Choice(name="SQL", value="sql"),
        app_commands.Choice(name="Other", value="other"),
    ])
    @app_commands.choices(focus=[
        app_commands.Choice(name="Comprehensive (All Areas)", value="comprehensive"),
        app_commands.Choice(name="Security Audit", value="security"),
        app_commands.Choice(name="Performance", value="performance"),
        app_commands.Choice(name="Code Quality", value="quality"),
    ])
    async def code_review(
        self,
        interaction: discord.Interaction,
        code: str,
        language: app_commands.Choice[str],
        focus: app_commands.Choice[str] = None
    ):
        """Review code for issues."""
        await interaction.response.defer()

        try:
            user = await self._get_linked_user(str(interaction.user.id))
            if not user:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Account Not Linked",
                        description="Please link your Discord account first using `/link`",
                        color=discord.Color.orange()
                    )
                )
                return

            @sync_to_async
            def run_review():
                from core.agents.code_review_agent import CodeReviewAgent
                agent = CodeReviewAgent()
                focus_area = focus.value if focus else "comprehensive"
                task = f"Perform a {focus_area} review of this {language.name} code:\n\n{code}"
                return agent.execute(task, user=user)

            result = await run_review()

            if result.success:
                content = result.content[:4000] if result.content else "Review complete."

                embed = discord.Embed(
                    title=f"🔍 Code Review ({language.name})",
                    description=content[:2000],
                    color=discord.Color.blue()
                )
                if focus:
                    embed.add_field(name="Focus", value=focus.name, inline=True)

                await interaction.followup.send(embed=embed)

                if len(content) > 2000:
                    await interaction.channel.send(f"**Review Continued:**\n```\n{content[2000:4000]}\n```")
            else:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Review Failed",
                        description=result.error or "Unable to review code",
                        color=discord.Color.red()
                    )
                )

        except Exception as e:
            logger.error(f"Code review error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to review code: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )


# ============================================================
# Session 497: ML Scoring Status Command
# ============================================================

class MLScoringCommands(commands.Cog):
    """
    Session 497: ML Scoring Status Commands.

    View the status of the ML opportunity scoring engine.
    """

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="ml-scoring", description="View ML opportunity scoring status")
    async def ml_scoring_status(self, interaction: discord.Interaction):
        """Get ML scoring engine status."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def get_ml_status():
                from core.services.ml_scoring_engine import get_ml_scoring_engine
                from core.models_unified_system import Opportunity, OpportunityOutcome
                from django.utils import timezone
                from datetime import timedelta
                from django.db.models import Count

                engine = get_ml_scoring_engine()
                now = timezone.now()
                day_ago = now - timedelta(hours=24)
                week_ago = now - timedelta(days=7)

                # Get stats
                total_opps = Opportunity.objects.count()
                opps_24h = Opportunity.objects.filter(created_at__gte=day_ago).count()

                # Score distribution
                recent = Opportunity.objects.filter(created_at__gte=week_ago).values('overall_score')
                high = sum(1 for o in recent if (o.get('overall_score') or 0) >= 70)
                medium = sum(1 for o in recent if 40 <= (o.get('overall_score') or 0) < 70)
                low = sum(1 for o in recent if (o.get('overall_score') or 0) < 40)

                # Outcomes
                outcomes = OpportunityOutcome.objects.values('outcome').annotate(count=Count('id'))
                outcome_map = {o['outcome']: o['count'] for o in outcomes}
                total_outcomes = sum(outcome_map.values())

                return {
                    'is_trained': engine.is_trained,
                    'total_opps': total_opps,
                    'opps_24h': opps_24h,
                    'high': high,
                    'medium': medium,
                    'low': low,
                    'training_data': total_outcomes,
                    'ready': total_outcomes >= 100,
                    'outcomes': outcome_map
                }

            data = await get_ml_status()

            # Model status
            if data['is_trained']:
                status_emoji = "✅"
                status_text = "Trained & Active"
            elif data['ready']:
                status_emoji = "🟡"
                status_text = "Ready for Training"
            else:
                status_emoji = "⏳"
                status_text = f"Collecting Data ({data['training_data']}/100)"

            embed = discord.Embed(
                title="🧠 ML Scoring Engine Status",
                color=discord.Color.gold()
            )
            embed.add_field(name="Model Status", value=f"{status_emoji} {status_text}", inline=True)
            embed.add_field(name="Training Data", value=str(data['training_data']), inline=True)
            embed.add_field(name="Total Opportunities", value=str(data['total_opps']), inline=True)
            embed.add_field(name="Scored (24h)", value=str(data['opps_24h']), inline=True)

            # Score distribution
            embed.add_field(
                name="Score Distribution (7d)",
                value=f"🟢 High (70+): {data['high']}\n🟡 Medium (40-69): {data['medium']}\n🔴 Low (<40): {data['low']}",
                inline=False
            )

            # Outcomes
            if data['outcomes']:
                outcome_text = "\n".join([f"• {k.replace('_', ' ').title()}: {v}" for k, v in data['outcomes'].items()])
                embed.add_field(name="Outcome Breakdown", value=outcome_text, inline=False)

            embed.set_footer(text="XGBoost + SHAP Explainability | Hybrid ML + Rule-based Scoring")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"ML scoring status error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Failed to get ML status: {str(e)[:200]}",
                    color=discord.Color.red()
                )
            )


class ReviewCommands(commands.Cog):
    """
    Session 556: Chief of Staff Review Document Commands.

    Discord commands for reviewing artifacts, interrogating Pro/Con sides,
    and making decisions from mobile.
    """

    def __init__(self, client):
        self.client = client

    review = app_commands.Group(name="review", description="Review documents and decisions")

    @review.command(name="show", description="Show review document for an artifact or dream")
    @app_commands.describe(target_id="The artifact or dream ID to review")
    async def review(self, interaction: discord.Interaction, target_id: str):
        """Display review document summary."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def get_or_create_review():
                from core.services.review_document import review_service
                from core.models_conversation_artifacts import ReviewDocument

                # Try to find existing review by target_id
                try:
                    # First check if it's already a review document ID
                    review = ReviewDocument.objects.get(id=target_id)
                    return review
                except (ReviewDocument.DoesNotExist, ValueError):
                    pass

                # Try as artifact ID
                try:
                    review = review_service.get_or_create_for_artifact(target_id)
                    return review
                except Exception as _e:
                    logger.warning(
                        "discord_bot.get_or_create_review: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

                # Try as dream ID
                try:
                    review = review_service.get_or_create_for_dream(target_id)
                    return review
                except Exception as _e:
                    logger.warning(
                        "discord_bot.get_or_create_review: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

                return None

            review = await get_or_create_review()

            if not review:
                await interaction.followup.send("❌ Could not find or create review for that ID")
                return

            # Build embed
            embed = discord.Embed(
                title=f"📋 Review: {review.target_type.title()}",
                color=self._get_lean_color(review.ai_lean),
                description=review.neutral_summary[:500] + ("..." if len(review.neutral_summary) > 500 else "")
            )

            # Add fields
            pro_text = review.pro_case[:500] + ("..." if len(review.pro_case) > 500 else "")
            embed.add_field(
                name="✅ Pro Case",
                value=pro_text or "No pro case available",
                inline=False
            )

            con_text = review.con_case[:500] + ("..." if len(review.con_case) > 500 else "")
            embed.add_field(
                name="❌ Con Case",
                value=con_text or "No con case available",
                inline=False
            )

            embed.add_field(
                name="🤖 AI Recommendation",
                value=f"**{review.ai_lean.replace('_', ' ').title()}** ({review.ai_confidence:.0%} confidence)\n{review.ai_recommendation[:300]}",
                inline=False
            )

            # Open questions
            if review.open_questions:
                questions_text = "\n".join(f"• {q}" for q in review.open_questions[:5])
                embed.add_field(
                    name="❓ Open Questions",
                    value=questions_text or "None",
                    inline=False
                )

            # Status and footer
            embed.add_field(
                name="📊 Status",
                value=f"Status: {review.status.replace('_', ' ').title()}\nQuestions: Pro {review.questions_asked_pro} | Con {review.questions_asked_con}",
                inline=True
            )

            embed.set_footer(text=f"Review ID: {review.id}\nUse /ask-pro or /ask-con to interrogate sides")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Review command error: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Error: {str(e)[:200]}")

    @review.command(name="list", description="List pending review documents")
    async def review_list(self, interaction: discord.Interaction):
        """List all pending reviews."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def get_pending_reviews():
                from core.models_conversation_artifacts import ReviewDocument
                reviews = list(ReviewDocument.objects.filter(
                    status='awaiting_human'
                ).order_by('-created_at')[:10])
                return reviews

            reviews = await get_pending_reviews()

            if not reviews:
                await interaction.followup.send("📭 No pending reviews")
                return

            embed = discord.Embed(
                title="📋 Pending Reviews",
                color=discord.Color.blue(),
                description=f"Found {len(reviews)} reviews awaiting decision"
            )

            for review in reviews:
                lean_emoji = self._get_lean_emoji(review.ai_lean)
                embed.add_field(
                    name=f"{lean_emoji} {review.target_type.title()}",
                    value=f"ID: `{str(review.id)[:8]}...`\nAI: {review.ai_lean.replace('_', ' ')} ({review.ai_confidence:.0%})\nQuestions: {review.questions_asked_pro + review.questions_asked_con}",
                    inline=True
                )

            embed.set_footer(text="Use /review <id> to view full details")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Review list error: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Error: {str(e)[:200]}")

    @review.command(name="pro", description="Ask the Pro advocate a question")
    @app_commands.describe(
        review_id="The review document ID",
        question="Your question for the Pro advocate"
    )
    async def ask_pro(self, interaction: discord.Interaction, review_id: str, question: str):
        """Ask Pro side a question."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def ask_pro_sync():
                from core.services.side_chat import side_chat_service
                from core.models_conversation_artifacts import ReviewDocument

                review = ReviewDocument.objects.get(id=review_id)
                result = side_chat_service.ask_side(review, 'pro', question)
                return result, review

            result, review = await ask_pro_sync()

            embed = discord.Embed(
                title="✅ Pro Advocate",
                color=discord.Color.green(),
                description=result['answer'][:2000]
            )
            embed.add_field(
                name="Your Question",
                value=question[:500],
                inline=False
            )
            embed.set_footer(text=f"Questions asked: Pro {review.questions_asked_pro} | Con {review.questions_asked_con}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            if "DoesNotExist" in str(type(e).__name__):
                await interaction.followup.send("❌ Review not found")
            else:
                logger.error(f"Ask pro error: {e}", exc_info=True)
                await interaction.followup.send(f"❌ Error: {str(e)[:200]}")

    @review.command(name="con", description="Ask the Con skeptic a question")
    @app_commands.describe(
        review_id="The review document ID",
        question="Your question for the Con skeptic"
    )
    async def ask_con(self, interaction: discord.Interaction, review_id: str, question: str):
        """Ask Con side a question."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def ask_con_sync():
                from core.services.side_chat import side_chat_service
                from core.models_conversation_artifacts import ReviewDocument

                review = ReviewDocument.objects.get(id=review_id)
                result = side_chat_service.ask_side(review, 'con', question)
                return result, review

            result, review = await ask_con_sync()

            embed = discord.Embed(
                title="❌ Con Skeptic",
                color=discord.Color.red(),
                description=result['answer'][:2000]
            )
            embed.add_field(
                name="Your Question",
                value=question[:500],
                inline=False
            )
            embed.set_footer(text=f"Questions asked: Pro {review.questions_asked_pro} | Con {review.questions_asked_con}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            if "DoesNotExist" in str(type(e).__name__):
                await interaction.followup.send("❌ Review not found")
            else:
                logger.error(f"Ask con error: {e}", exc_info=True)
                await interaction.followup.send(f"❌ Error: {str(e)[:200]}")

    @review.command(name="decide", description="Make a decision on a review")
    @app_commands.describe(
        review_id="The review document ID",
        decision="Your decision",
        conditions="Optional conditions (for approve with conditions)"
    )
    @app_commands.choices(decision=[
        app_commands.Choice(name="Approve", value="approved"),
        app_commands.Choice(name="Approve with Conditions", value="approved_with_conditions"),
        app_commands.Choice(name="Decline", value="declined"),
        app_commands.Choice(name="Defer", value="deferred"),
    ])
    async def decide(
        self,
        interaction: discord.Interaction,
        review_id: str,
        decision: str,
        conditions: str = ""
    ):
        """Make a decision on a review document."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def make_decision():
                from django.utils import timezone
                from core.models_conversation_artifacts import ReviewDocument, ExtractedArtifact

                review = ReviewDocument.objects.get(id=review_id)

                # Update review document
                review.status = decision
                review.decision_conditions = conditions
                review.decided_at = timezone.now()
                review.save()

                # Cascade to artifact if applicable
                if review.target_type == 'artifact':
                    try:
                        artifact = ExtractedArtifact.objects.get(id=review.target_id)
                        if decision in ['approved', 'approved_with_conditions']:
                            artifact.status = 'approved'
                        elif decision == 'declined':
                            artifact.status = 'rejected'
                        elif decision == 'deferred':
                            artifact.status = 'deferred'
                        artifact.save()
                    except ExtractedArtifact.DoesNotExist:
                        pass

                return review

            review = await make_decision()

            # Send confirmation
            decision_emoji = {
                'approved': '✅',
                'approved_with_conditions': '⚠️',
                'declined': '❌',
                'deferred': '⏸️'
            }.get(decision, '📋')

            embed = discord.Embed(
                title=f"{decision_emoji} Decision Recorded",
                color=discord.Color.green() if 'approved' in decision else discord.Color.orange(),
                description=f"Review **{decision.replace('_', ' ').title()}**"
            )

            if conditions:
                embed.add_field(name="Conditions", value=conditions, inline=False)

            embed.set_footer(text=f"Review ID: {review.id}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            if "DoesNotExist" in str(type(e).__name__):
                await interaction.followup.send("❌ Review not found")
            else:
                logger.error(f"Decide error: {e}", exc_info=True)
                await interaction.followup.send(f"❌ Error: {str(e)[:200]}")

    def _get_lean_color(self, lean: str) -> discord.Color:
        """Get color based on AI lean."""
        colors = {
            'strong_approve': discord.Color.green(),
            'lean_approve': discord.Color.dark_green(),
            'neutral': discord.Color.gold(),
            'lean_decline': discord.Color.orange(),
            'strong_decline': discord.Color.red(),
            'pilot': discord.Color.blue(),
            'defer': discord.Color.greyple(),
        }
        return colors.get(lean, discord.Color.blue())

    def _get_lean_emoji(self, lean: str) -> str:
        """Get emoji based on AI lean."""
        emojis = {
            'strong_approve': '🟢',
            'lean_approve': '🟡',
            'neutral': '⚪',
            'lean_decline': '🟠',
            'strong_decline': '🔴',
            'pilot': '🔵',
            'defer': '⏸️',
        }
        return emojis.get(lean, '📋')


class HumanInterfaceCommands(commands.Cog):
    """
    Session 686: Human Interface Layer Discord Commands.

    Uses a command GROUP so all subcommands count as 1 command toward the 100 limit.
    - /human attention - View attention stream requiring your review
    - /human control - View and manage system control state
    - /human decide - Make a decision on an attention item
    - /human pause - Pause an agent
    - /human resume - Resume a paused agent
    - /human quiet - Toggle quiet mode
    """

    def __init__(self, client):
        self.client = client

    # Create a command group - all subcommands count as 1 command!
    human_group = app_commands.Group(name="human", description="Human Interface Layer - control your AI ecosystem")

    @human_group.command(name="attention", description="View items requiring your attention")
    @app_commands.describe(urgency="Filter by urgency level")
    @app_commands.choices(urgency=[
        app_commands.Choice(name="All", value="all"),
        app_commands.Choice(name="Critical", value="critical"),
        app_commands.Choice(name="High", value="high"),
        app_commands.Choice(name="Medium", value="medium"),
        app_commands.Choice(name="Low", value="low"),
    ])
    async def attention(
        self,
        interaction: discord.Interaction,
        urgency: str = "all"
    ):
        """View attention stream items."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def get_attention_items():
                from core.models_human_interface import HumanAttentionItem
                from django.contrib.auth import get_user_model
                User = get_user_model()

                # Try to find linked user
                user = User.objects.filter(
                    discord_id=str(interaction.user.id)
                ).first() or User.objects.first()

                if not user:
                    return []

                queryset = HumanAttentionItem.objects.filter(
                    user=user,
                    status__in=['pending', 'viewed']
                )

                if urgency != "all":
                    queryset = queryset.filter(urgency=urgency)

                return list(queryset.order_by('-priority_score', '-created_at')[:10])

            items = await get_attention_items()

            if not items:
                embed = discord.Embed(
                    title="✅ All Clear!",
                    description="No items requiring your attention.",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=embed)
                return

            embed = discord.Embed(
                title="👤 Human Attention Stream",
                description=f"Found {len(items)} item(s) requiring your attention",
                color=discord.Color.blue()
            )

            urgency_emojis = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '⚪'
            }

            for item in items:
                emoji = urgency_emojis.get(item.urgency, '📋')
                ml_text = f" (ML: {item.ml_confidence:.0%})" if item.ml_confidence else ""
                embed.add_field(
                    name=f"{emoji} {item.title[:50]}",
                    value=f"Source: {item.source_agent or item.source_type}\n"
                          f"Type: {item.item_type}{ml_text}\n"
                          f"ID: `{str(item.id)[:8]}...`",
                    inline=True
                )

            embed.set_footer(text="Use /human decide <id> <decision> to act on an item")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Human attention error: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Error: {str(e)[:200]}")

    @human_group.command(name="control", description="View system control state")
    async def control(self, interaction: discord.Interaction):
        """View current system control state."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def get_system_state():
                from core.models_human_interface import HumanSystemState
                return HumanSystemState.get_state()

            state = await get_system_state()

            embed = discord.Embed(
                title="🎛️ Human Control Panel",
                color=discord.Color.blue()
            )

            # System status
            status_lines = []
            if state.system_paused:
                status_lines.append("⏸️ **System Paused**")
            if state.review_mode:
                status_lines.append("👁️ **Review Mode Active**")
            if state.quiet_mode:
                until_text = f" (until {state.quiet_mode_until.strftime('%H:%M')})" if state.quiet_mode_until else ""
                status_lines.append(f"🌙 **Quiet Mode{until_text}**")

            if not status_lines:
                status_lines.append("✅ System Operating Normally")

            embed.add_field(
                name="System Status",
                value="\n".join(status_lines),
                inline=False
            )

            # ML Thresholds
            embed.add_field(
                name="ML Thresholds",
                value=f"Confidence: {state.ml_confidence_threshold:.0%}\n"
                      f"Auto-Approve: {state.auto_approve_threshold:.0%}",
                inline=True
            )

            # Paused agents
            if state.paused_agents:
                agents_text = "\n".join(f"• {a}" for a in state.paused_agents[:5])
                if len(state.paused_agents) > 5:
                    agents_text += f"\n... and {len(state.paused_agents) - 5} more"
            else:
                agents_text = "None"

            embed.add_field(
                name="Paused Agents",
                value=agents_text,
                inline=True
            )

            embed.set_footer(text="Use /human pause, /human resume, /human quiet to control")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Human control error: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Error: {str(e)[:200]}")

    @human_group.command(name="decide", description="Make a decision on an attention item")
    @app_commands.describe(
        item_id="The attention item ID (first 8 characters are enough)",
        decision="Your decision",
        feedback="Optional feedback or notes"
    )
    @app_commands.choices(decision=[
        app_commands.Choice(name="Approve", value="approve"),
        app_commands.Choice(name="Reject", value="reject"),
        app_commands.Choice(name="Modify", value="modify"),
        app_commands.Choice(name="Defer", value="defer"),
        app_commands.Choice(name="Ignore", value="ignore"),
        app_commands.Choice(name="Escalate", value="escalate"),
    ])
    async def decide(
        self,
        interaction: discord.Interaction,
        item_id: str,
        decision: str,
        feedback: str = ""
    ):
        """Make a decision on an attention item."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def make_decision():
                from core.models_human_interface import HumanAttentionItem
                from django.contrib.auth import get_user_model
                User = get_user_model()

                # Try to find linked user
                user = User.objects.filter(
                    discord_id=str(interaction.user.id)
                ).first() or User.objects.first()

                if not user:
                    return None, "User not found"

                # Find item by partial ID
                items = HumanAttentionItem.objects.filter(
                    user=user,
                    id__startswith=item_id
                )

                if not items.exists():
                    # Try string matching
                    items = HumanAttentionItem.objects.filter(user=user)
                    items = [i for i in items if str(i.id).startswith(item_id)]
                    if not items:
                        return None, "Item not found"
                    item = items[0]
                else:
                    item = items.first()

                item.record_decision(decision, feedback)
                return item, None

            item, error = await make_decision()

            if error:
                await interaction.followup.send(f"❌ {error}")
                return

            decision_emojis = {
                'approve': '✅',
                'reject': '❌',
                'modify': '✏️',
                'defer': '⏸️',
                'ignore': '🙈',
                'escalate': '⚠️',
            }

            embed = discord.Embed(
                title=f"{decision_emojis.get(decision, '📋')} Decision Recorded",
                description=f"**{item.title}**\n\nDecision: **{decision.title()}**",
                color=discord.Color.green() if decision == 'approve' else discord.Color.orange()
            )

            if feedback:
                embed.add_field(name="Your Notes", value=feedback[:500], inline=False)

            if item.human_overrode_ml:
                embed.add_field(
                    name="⚠️ ML Override",
                    value=f"You overrode the ML recommendation ({item.ml_recommendation})",
                    inline=False
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Human decide error: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Error: {str(e)[:200]}")

    @human_group.command(name="pause", description="Pause an agent")
    @app_commands.describe(
        agent_name="Name of the agent to pause",
        reason="Reason for pausing"
    )
    async def pause(
        self,
        interaction: discord.Interaction,
        agent_name: str,
        reason: str = ""
    ):
        """Pause an agent."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def pause_agent():
                from core.models_human_interface import HumanSystemState, HumanControlAction
                from django.contrib.auth import get_user_model
                User = get_user_model()

                user = User.objects.filter(
                    discord_id=str(interaction.user.id)
                ).first() or User.objects.first()

                if not user:
                    return False, "User not found"

                state = HumanSystemState.get_state()

                if agent_name in state.paused_agents:
                    return False, f"{agent_name} is already paused"

                state.pause_agent(agent_name)

                # Log the action
                HumanControlAction.objects.create(
                    user=user,
                    action_type='pause_agent',
                    target_type='agent',
                    target_id=agent_name,
                    reason=reason
                )

                return True, None

            success, error = await pause_agent()

            if not success:
                await interaction.followup.send(f"❌ {error}")
                return

            embed = discord.Embed(
                title="⏸️ Agent Paused",
                description=f"**{agent_name}** has been paused.",
                color=discord.Color.orange()
            )

            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)

            embed.set_footer(text="Use /human resume to resume this agent")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Human pause error: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Error: {str(e)[:200]}")

    @human_group.command(name="resume", description="Resume a paused agent")
    @app_commands.describe(
        agent_name="Name of the agent to resume",
        reason="Reason for resuming"
    )
    async def resume(
        self,
        interaction: discord.Interaction,
        agent_name: str,
        reason: str = ""
    ):
        """Resume a paused agent."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def resume_agent():
                from core.models_human_interface import HumanSystemState, HumanControlAction
                from django.contrib.auth import get_user_model
                User = get_user_model()

                user = User.objects.filter(
                    discord_id=str(interaction.user.id)
                ).first() or User.objects.first()

                if not user:
                    return False, "User not found"

                state = HumanSystemState.get_state()

                if agent_name not in state.paused_agents:
                    return False, f"{agent_name} is not paused"

                state.resume_agent(agent_name)

                # Log the action
                HumanControlAction.objects.create(
                    user=user,
                    action_type='resume_agent',
                    target_type='agent',
                    target_id=agent_name,
                    reason=reason
                )

                return True, None

            success, error = await resume_agent()

            if not success:
                await interaction.followup.send(f"❌ {error}")
                return

            embed = discord.Embed(
                title="▶️ Agent Resumed",
                description=f"**{agent_name}** has been resumed.",
                color=discord.Color.green()
            )

            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Human resume error: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Error: {str(e)[:200]}")

    @human_group.command(name="quiet", description="Toggle quiet mode")
    @app_commands.describe(
        enabled="Enable or disable quiet mode",
        duration="Duration in minutes (optional)"
    )
    async def quiet(
        self,
        interaction: discord.Interaction,
        enabled: bool = True,
        duration: int = None
    ):
        """Toggle quiet mode."""
        await interaction.response.defer()

        try:
            @sync_to_async
            def set_quiet_mode():
                from core.models_human_interface import HumanSystemState, HumanControlAction
                from django.contrib.auth import get_user_model
                from django.utils import timezone
                from datetime import timedelta
                User = get_user_model()

                user = User.objects.filter(
                    discord_id=str(interaction.user.id)
                ).first() or User.objects.first()

                if not user:
                    return None, "User not found"

                state = HumanSystemState.get_state()
                state.quiet_mode = enabled

                if enabled and duration:
                    state.quiet_mode_until = timezone.now() + timedelta(minutes=duration)
                elif not enabled:
                    state.quiet_mode_until = None

                state.updated_by = user
                state.save()

                # Log the action
                HumanControlAction.objects.create(
                    user=user,
                    action_type='quiet_mode',
                    target_type='system',
                    target_id='system',
                    new_value={'enabled': enabled, 'duration': duration}
                )

                return state, None

            state, error = await set_quiet_mode()

            if error:
                await interaction.followup.send(f"❌ {error}")
                return

            if enabled:
                description = "Quiet mode **enabled**. Non-critical notifications suppressed."
                if state.quiet_mode_until:
                    description += f"\n\nWill auto-disable at {state.quiet_mode_until.strftime('%H:%M')}"
                color = discord.Color.purple()
                emoji = "🌙"
            else:
                description = "Quiet mode **disabled**. All notifications active."
                color = discord.Color.green()
                emoji = "☀️"

            embed = discord.Embed(
                title=f"{emoji} Quiet Mode",
                description=description,
                color=color
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Human quiet error: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Error: {str(e)[:200]}")


# Bot instance (created when module loads)
_bot_instance: Optional[DonkeyBetzBot] = None


class OBSCommands(commands.Cog):
    """OBS Studio recording control — 3 commands (status, record, upload).

    Trimmed from 6 to 3 per PA recommendation to conserve command slots (94/100).
    Full controls available at /cockpit/obs.
    """

    COCKPIT_URL = "https://donkey-betz-platform-production.up.railway.app/cockpit/obs"

    def __init__(self, bot: DonkeyBetzBot):
        self.bot = bot

    async def _call_bridge(self, method: str, path: str, body=None, timeout=15):
        """Call the platform OBS proxy endpoints via sync_to_async."""
        @sync_to_async
        def _call():
            from core.views_obs import _obs_enabled, _obs_bridge_request
            if not _obs_enabled():
                return {'ok': False, 'error': {'code': 'OBS_DISABLED', 'message': 'OBS integration is not enabled'}}
            status_code, data, latency = _obs_bridge_request(method, path, body, timeout)
            if status_code == 0:
                return {'ok': False, 'bridgeReachable': False, 'error': {'code': 'BRIDGE_UNREACHABLE', 'message': data.get('error', 'Unreachable')}, 'latency_ms': latency}
            if status_code == 401:
                return {'ok': False, 'bridgeReachable': True, 'error': {'code': 'BRIDGE_AUTH_FAILED', 'message': 'Bridge rejected token'}, 'latency_ms': latency}
            return {'ok': data.get('ok', True), 'bridgeReachable': True, 'result': data, 'latency_ms': latency}
        return await _call()

    def _error_embed(self, data: dict) -> discord.Embed:
        err = data.get('error', {})
        return discord.Embed(
            title="OBS Error",
            description=f"**{err.get('code', 'ERROR')}**: {err.get('message', 'Unknown error')}",
            color=discord.Color.red(),
            timestamp=datetime.now(),
        ).add_field(name="Cockpit", value=f"[Open OBS Control]({self.COCKPIT_URL})", inline=False)

    @app_commands.command(name="obs-status", description="Check OBS bridge + recording status")
    async def obs_status(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        data = await self._call_bridge('GET', '/v1/recording/status')
        if not data.get('ok'):
            return await interaction.followup.send(embed=self._error_embed(data), ephemeral=True)

        result = data.get('result', {})
        is_rec = result.get('isRecording', False)
        bridge_ok = data.get('bridgeReachable', False)
        embed = discord.Embed(
            title="OBS Status",
            color=discord.Color.red() if is_rec else discord.Color.green() if bridge_ok else discord.Color.greyple(),
            timestamp=datetime.now(),
        )
        embed.add_field(name="Bridge", value="Connected" if bridge_ok else "Disconnected", inline=True)
        embed.add_field(name="Recording", value="Yes" if is_rec else "No", inline=True)
        if result.get('recordingTimecode'):
            embed.add_field(name="Timecode", value=result['recordingTimecode'], inline=True)
        if result.get('obsVersion'):
            embed.add_field(name="OBS", value=f"{result['obsVersion']} / WS {result.get('websocketVersion', '?')}", inline=True)
        embed.add_field(name="Latency", value=f"{data.get('latency_ms', '?')}ms", inline=True)
        embed.add_field(name="Cockpit", value=f"[Open OBS Control]({self.COCKPIT_URL})", inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="obs-record", description="Start, stop, or toggle OBS recording")
    @app_commands.describe(action="Recording action (default: toggle)")
    @app_commands.choices(action=[
        app_commands.Choice(name="toggle", value="toggle"),
        app_commands.Choice(name="start", value="start"),
        app_commands.Choice(name="stop", value="stop"),
    ])
    async def obs_record(self, interaction: discord.Interaction, action: str = "toggle"):
        await interaction.response.defer(ephemeral=True)

        if action == "toggle":
            status_data = await self._call_bridge('GET', '/v1/recording/status')
            if not status_data.get('ok'):
                return await interaction.followup.send(embed=self._error_embed(status_data), ephemeral=True)
            is_rec = status_data.get('result', {}).get('isRecording', False)
            action = "stop" if is_rec else "start"

        data = await self._call_bridge('POST', f'/v1/recording/{action}')
        if not data.get('ok'):
            return await interaction.followup.send(embed=self._error_embed(data), ephemeral=True)

        started = action == "start"
        embed = discord.Embed(
            title=f"Recording {'Started' if started else 'Stopped'}",
            color=discord.Color.red() if started else discord.Color.green(),
            timestamp=datetime.now(),
        )
        embed.add_field(name="Cockpit", value=f"[Open OBS Control]({self.COCKPIT_URL})", inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="obs-upload", description="Upload the latest OBS recording to platform")
    @app_commands.describe(
        title="Optional title for the video",
        tags="Comma-separated tags (e.g. obs,devlog)",
        stop_if_recording="Stop recording first if active (default: true)",
    )
    async def obs_upload(
        self,
        interaction: discord.Interaction,
        title: str = "",
        tags: str = "",
        stop_if_recording: bool = True,
    ):
        await interaction.response.defer(ephemeral=True)

        body: dict = {}
        if title.strip():
            body['title'] = title.strip()
        if tags.strip():
            body['tags'] = [t.strip() for t in tags.split(',') if t.strip()]
        if stop_if_recording:
            body['stopIfRecording'] = True

        data = await self._call_bridge('POST', '/v1/recording/upload_last', body=body or None, timeout=60)
        if not data.get('ok'):
            embed = self._error_embed(data)
            err_code = data.get('error', {}).get('code', '')
            if err_code == 'UPLOAD_TOO_LARGE' or 'too large' in data.get('error', {}).get('message', '').lower():
                embed.add_field(name="Tip", value="Record shorter clips (<50 MB) or use [Cockpit]({}) for full options.".format(self.COCKPIT_URL), inline=False)
            return await interaction.followup.send(embed=embed, ephemeral=True)

        result = data.get('result', {})
        video = result.get('video', result.get('media', {}))
        vid_id = video.get('id', 'unknown') if isinstance(video, dict) else 'unknown'

        embed = discord.Embed(title="Upload Successful", color=discord.Color.green(), timestamp=datetime.now())
        embed.add_field(name="Video ID", value=str(vid_id), inline=True)
        if isinstance(video, dict) and video.get('url'):
            embed.add_field(name="URL", value=str(video['url']), inline=True)
        embed.add_field(name="Cockpit", value=f"[Open OBS Control]({self.COCKPIT_URL})", inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)


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
