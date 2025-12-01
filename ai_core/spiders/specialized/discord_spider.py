"""
Discord Spider - Community Server Intelligence
===============================================

Session 294: Customer research spider for Discord communities.
Monitors public messages in AI/creator community servers.

Uses Discord Bot API with credentials from environment.
Note: Requires a Discord bot to be added to target servers.
"""

import aiohttp
import asyncio
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class DiscordSpider(BaseIntelligenceSpider):
    """Discord spider - community discussions and pain points"""

    # Public Discord servers/channels to monitor (need bot access)
    # These would need to be configured based on which servers the bot is in
    TARGET_CHANNELS = []  # Will be populated from environment or config

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.bot_token = os.getenv('DISCORD_BOT_TOKEN', '')
        self.app_id = os.getenv('DISCORD_APP_ID', '')
        self.public_key = os.getenv('DISCORD_PUBLIC_KEY', '')
        self.base_url = "https://discord.com/api/v10"

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch messages from Discord channels"""
        if not self.bot_token:
            self.logger.warning("Discord bot token not configured (DISCORD_BOT_TOKEN)")
            # Return helpful info about what's needed
            return {
                'messages': [],
                'source': 'discord',
                'status': 'not_configured',
                'setup_instructions': {
                    'step1': 'Create a Discord bot at https://discord.com/developers/applications',
                    'step2': 'Add DISCORD_BOT_TOKEN to .env',
                    'step3': 'Invite bot to target servers with read message permissions',
                    'step4': 'Configure TARGET_CHANNELS with channel IDs to monitor',
                }
            }

        try:
            all_messages = []
            headers = {
                'Authorization': f'Bot {self.bot_token}',
                'Content-Type': 'application/json',
            }

            async with aiohttp.ClientSession(headers=headers) as session:
                # Get guilds the bot is in
                guilds_url = f"{self.base_url}/users/@me/guilds"

                async with session.get(guilds_url, timeout=10) as response:
                    if response.status == 200:
                        guilds = await response.json()
                        self.logger.info(f"Bot is in {len(guilds)} servers")

                        # For each guild, get channels and recent messages
                        for guild in guilds[:5]:  # Limit to 5 servers
                            guild_id = guild['id']
                            guild_name = guild['name']

                            # Get channels
                            channels_url = f"{self.base_url}/guilds/{guild_id}/channels"
                            async with session.get(channels_url, timeout=10) as ch_response:
                                if ch_response.status == 200:
                                    channels = await ch_response.json()

                                    # Get text channels only
                                    text_channels = [c for c in channels if c.get('type') == 0]

                                    for channel in text_channels[:3]:  # Limit channels per server
                                        channel_id = channel['id']
                                        channel_name = channel['name']

                                        # Fetch recent messages
                                        messages_url = f"{self.base_url}/channels/{channel_id}/messages"
                                        params = {'limit': 50}

                                        try:
                                            async with session.get(messages_url, params=params, timeout=10) as msg_response:
                                                if msg_response.status == 200:
                                                    messages = await msg_response.json()

                                                    for msg in messages:
                                                        if msg.get('content') and not msg.get('author', {}).get('bot'):
                                                            all_messages.append({
                                                                'content': msg.get('content', '')[:500],
                                                                'author': msg.get('author', {}).get('username', ''),
                                                                'channel': channel_name,
                                                                'guild': guild_name,
                                                                'timestamp': msg.get('timestamp', ''),
                                                                'reactions': len(msg.get('reactions', [])),
                                                                'source': 'discord',
                                                                'type': 'message',
                                                            })

                                        except Exception as e:
                                            self.logger.warning(f"Error fetching messages from {channel_name}: {e}")

                                        await asyncio.sleep(0.3)

                    elif response.status == 401:
                        self.logger.error("Discord bot token is invalid")
                        return {'messages': [], 'source': 'discord', 'error': 'Invalid bot token'}
                    else:
                        self.logger.warning(f"Discord API error: {response.status}")

            return {'messages': all_messages, 'source': 'discord'}

        except Exception as e:
            self.logger.error(f"Error fetching Discord data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Discord messages into intelligence"""
        try:
            messages = raw_data.get('messages', [])

            # Pain point detection
            pain_keywords = ['help', 'issue', 'problem', 'bug', 'broken', 'doesn\'t work',
                           'frustrated', 'confused', 'stuck', 'how do i', 'anyone know',
                           'hate', 'annoying', 'wish']

            pain_point_messages = []
            question_messages = []

            for msg in messages:
                text = msg.get('content', '').lower()
                if any(kw in text for kw in pain_keywords):
                    pain_point_messages.append(msg)
                if '?' in msg.get('content', ''):
                    question_messages.append(msg)

            content = {
                'messages': messages[:100],
                'pain_point_messages': pain_point_messages[:30],
                'questions': question_messages[:30],
                'total_messages': len(messages),
                'pain_points_found': len(pain_point_messages),
                'questions_found': len(question_messages),
                'servers_scanned': len(set(m.get('guild', '') for m in messages)),
            }

            quality_score = min(1.0, len(messages) / 100 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='discord.com',
                data_type='community_intelligence',
                content=content,
                metadata={
                    'message_count': len(messages),
                    'pain_points': len(pain_point_messages),
                    'questions': len(question_messages),
                    'source': 'discord',
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['discord', 'community', 'discussions', 'pain_points', 'questions'],
                target_agents=['customer_research_agent', 'trend_analysis_agent'],
                target_advisors=['community_advisor', 'product_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing Discord data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['content']

    def get_relevance_keywords(self) -> List[str]:
        return ['discord', 'community', 'chat', 'discussion', 'help', 'question']
