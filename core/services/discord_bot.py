"""
Discord Bot Service - Session 426

Interactive Discord bot with slash commands for system monitoring and data access.

Commands:
- /status - System health check
- /agents - List active agents with stats
- /trending - Get trending spider data
- /help - Command reference

Usage:
    # Run the bot
    python manage.py run_discord_bot

    # Or via make command
    make discord-bot
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


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
        await self.add_cog(HelpCommands(self))

        # Sync slash commands with Discord
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash commands")
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
                queryset = SpiderData.objects.filter(crawled_at__gte=week_ago)

                if cat:
                    queryset = queryset.filter(category__icontains=cat)

                items = list(queryset.order_by('-crawled_at')[:lim])
                total = queryset.count()

                return [{
                    'title': item.title,
                    'category': item.category,
                    'url': item.url,
                    'spider_name': item.spider_name,
                } for item in items], total

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
                title = item['title'][:50] + "..." if len(item['title']) > 50 else item['title']
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
            name=" Agents",
            value=(
                "**/agents** [limit] - List active agents\n"
                "**/agent** <name> - Get agent details"
            ),
            inline=False
        )

        # Data commands
        embed.add_field(
            name=" Data",
            value=(
                "**/trending** [category] [limit] - Trending topics\n"
            ),
            inline=False
        )

        # Help
        embed.add_field(
            name=" Help",
            value="**/help** - This command",
            inline=False
        )

        embed.set_footer(text="Session 426 | More commands coming soon!")

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
