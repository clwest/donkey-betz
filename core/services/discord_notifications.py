"""
Discord Notification Service - Session 419

Sends agent activity notifications to Discord channels:
- #agent-dreams - When agents dream
- #agent-conversations - When HiveMind sessions complete
- #system-status - System health and status updates

Usage:
    from core.services.discord_notifications import discord_notify

    # Send a dream notification
    discord_notify.send_dream(agent_name, dream_title, dream_content)

    # Send a conversation notification
    discord_notify.send_conversation(participants, topic, synthesis)

    # Send a status update
    discord_notify.send_status("System started", "All services running")
"""

import os
import logging
import requests
from datetime import datetime
from django.conf import settings
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class DiscordNotificationService:
    """Service for sending notifications to Discord channels."""

    # Discord channel IDs (provided by user)
    CHANNEL_DREAMS = "1448809858274033684"
    CHANNEL_CONVERSATIONS = "1448809914783895583"
    CHANNEL_STATUS = "1448809955326169149"
    CHANNEL_LEARNING = "1448819275459465257"  # Dedicated agent learning channel
    CHANNEL_BOARDROOM = "1448819855557136595"  # Boardroom decisions channel
    CHANNEL_OPPORTUNITIES = "1448867150948335777"  # Session 424: High-value opportunity alerts
    CHANNEL_GALLERY = "1449059813765021859"  # Session 430: User gallery for image delivery
    CHANNEL_PROFILE = "1449059839581098135"  # Session 430: User profile channel
    CHANNEL_MARKET_ALERTS = "1448867150948335777"  # Session 460: Market/SEC alerts (shares with opportunities)
    CHANNEL_STOCK_ALERTS = "1450589539562426418"  # Session 461: Stock audit agent alerts
    CHANNEL_BLOCKCHAIN_ALERTS = "1450589795058192465"  # Session 461: Blockchain audit agent alerts
    CHANNEL_PODCAST_LIBRARY = "1451601597007134821"  # Session 496: Podcast library for completed episodes

    # Discord API base URL
    API_BASE = "https://discord.com/api/v10"

    def __init__(self):
        # Try to get token from Django settings first, then fall back to os.environ
        try:
            self.bot_token = getattr(settings, 'DISCORD_BOT_TOKEN', None) or os.environ.get('DISCORD_BOT_TOKEN', '')
        except Exception:
            self.bot_token = os.environ.get('DISCORD_BOT_TOKEN', '')

        self.enabled = bool(self.bot_token)

        if not self.enabled:
            logger.warning("Discord notifications disabled - DISCORD_BOT_TOKEN not set")
        else:
            logger.info(f"Discord notifications ENABLED - bot token found ({self.bot_token[:20]}...)")

    def _get_headers(self) -> dict:
        """Get authorization headers for Discord API."""
        return {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json"
        }

    def _send_message(self, channel_id: str, content: str, embed: Optional[dict] = None) -> bool:
        """
        Send a message to a Discord channel.

        Args:
            channel_id: Discord channel ID
            content: Message content (can be empty if using embed)
            embed: Optional embed object for rich formatting

        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug(f"Discord disabled, would send to {channel_id}: {content[:50]}...")
            return False

        url = f"{self.API_BASE}/channels/{channel_id}/messages"

        payload = {}
        if content:
            payload["content"] = content[:2000]  # Discord limit
        if embed:
            payload["embeds"] = [embed]

        try:
            response = requests.post(url, headers=self._get_headers(), json=payload, timeout=10)

            if response.status_code == 200:
                logger.info(f"Discord message sent to channel {channel_id}")
                return True
            else:
                logger.error(f"Discord API error {response.status_code}: {response.text}")
                return False

        except requests.exceptions.Timeout:
            logger.error("Discord API timeout")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Discord request failed: {e}")
            return False

    def send_dream(self, agent_name: str, dream_title: str, dream_content: str,
                   dream_type: str = "creative", vividness: float = 0.0) -> bool:
        """
        Send a dream notification to #agent-dreams.

        Args:
            agent_name: Name of the dreaming agent
            dream_title: Title of the dream
            dream_content: Full dream content
            dream_type: Type of dream (creative_idea, what_if, prediction, observation)
            vividness: Vividness score (0-1)
        """
        # Dream type emojis
        type_emojis = {
            "creative_idea": "💡",
            "what_if": "🤔",
            "prediction": "🔮",
            "observation": "👁️",
            "nightmare": "😱",
            "lucid": "✨",
        }
        emoji = type_emojis.get(dream_type, "💭")

        # Create rich embed
        embed = {
            "title": f"{emoji} {dream_title}",
            "description": dream_content[:4096],  # Discord embed limit
            "color": 0x9B59B6,  # Purple for dreams
            "author": {
                "name": f"🤖 {agent_name} is dreaming..."
            },
            "fields": [
                {"name": "Dream Type", "value": dream_type.replace("_", " ").title(), "inline": True},
                {"name": "Vividness", "value": f"{'🌟' * int(vividness * 5)} ({vividness:.0%})", "inline": True}
            ],
            "footer": {
                "text": "AI Studio Agent Dreams"
            }
        }

        return self._send_message(self.CHANNEL_DREAMS, "", embed=embed)

    def send_conversation(self, participants: List[str], topic: str,
                          synthesis: str, mode: str = "conversation") -> bool:
        """
        Send a conversation/HiveMind notification to #agent-conversations.

        Args:
            participants: List of participating agent names
            topic: Conversation topic/question
            synthesis: The synthesized output
            mode: Session mode (conversation, brainstorm, consensus, debate)
        """
        # Mode emojis
        mode_emojis = {
            "conversation": "💬",
            "brainstorm": "🧠",
            "consensus": "🤝",
            "debate": "⚔️",
        }
        emoji = mode_emojis.get(mode, "💬")

        # Format participants
        participant_str = ", ".join(participants[:5])
        if len(participants) > 5:
            participant_str += f" +{len(participants) - 5} more"

        embed = {
            "title": f"{emoji} {topic[:200]}",
            "description": synthesis[:4096],
            "color": 0xE91E63,  # Pink for conversations
            "author": {
                "name": f"🐝 HiveMind Session ({len(participants)} agents)"
            },
            "fields": [
                {"name": "Participants", "value": participant_str, "inline": False},
                {"name": "Mode", "value": mode.title(), "inline": True}
            ],
            "footer": {
                "text": "AI Studio Collective Intelligence"
            }
        }

        return self._send_message(self.CHANNEL_CONVERSATIONS, "", embed=embed)

    def send_knowledge(self, agent_name: str, title: str, summary: str,
                       knowledge_type: str = "insight", confidence: float = 0.0) -> bool:
        """
        Send a knowledge learning notification to #agent-learning.

        Args:
            agent_name: Name of the learning agent
            title: Knowledge title
            summary: Knowledge summary
            knowledge_type: Type (best_practice, insight, lesson_learned, etc.)
            confidence: Confidence score (0-1)
        """
        type_emojis = {
            "best_practice": "⭐",
            "insight": "💡",
            "lesson_learned": "📚",
            "tip": "💡",
            "warning": "⚠️",
        }
        emoji = type_emojis.get(knowledge_type, "📖")

        embed = {
            "title": f"{emoji} {title}",
            "description": summary[:4096],
            "color": 0x3498DB,  # Blue for knowledge
            "author": {
                "name": f"🎓 {agent_name} learned something!"
            },
            "fields": [
                {"name": "Type", "value": knowledge_type.replace("_", " ").title(), "inline": True},
                {"name": "Confidence", "value": f"{'📊' * int(confidence * 5)} ({confidence:.0%})", "inline": True}
            ],
            "footer": {
                "text": "AI Studio Knowledge Sharing"
            }
        }

        return self._send_message(self.CHANNEL_LEARNING, "", embed=embed)

    def send_status(self, title: str, message: str, status_type: str = "info") -> bool:
        """
        Send a system status notification to #system-status.

        Args:
            title: Status title
            message: Status message
            status_type: Type (info, success, warning, error)
        """
        # Status colors and emojis
        status_config = {
            "info": {"color": 0x3498DB, "emoji": "ℹ️"},
            "success": {"color": 0x2ECC71, "emoji": "✅"},
            "warning": {"color": 0xF39C12, "emoji": "⚠️"},
            "error": {"color": 0xE74C3C, "emoji": "❌"},
        }
        config = status_config.get(status_type, status_config["info"])

        embed = {
            "title": f"{config['emoji']} {title}",
            "description": message[:4096],
            "color": config["color"],
            "footer": {
                "text": "AI Studio System Status"
            }
        }

        return self._send_message(self.CHANNEL_STATUS, "", embed=embed)

    def send_spider_activity(self, spider_name: str, records_collected: int,
                              topics: List[str] = None, duration_seconds: float = 0,
                              source_url: str = "", status: str = "success") -> bool:
        """
        Send a spider activity notification to #system-status (Session 423).

        Args:
            spider_name: Name of the spider
            records_collected: Number of records collected
            topics: List of topics found in the data
            duration_seconds: How long the crawl took
            source_url: Data source URL
            status: "success", "partial", or "error"
        """
        # Status colors and emojis
        status_config = {
            "success": {"color": 0x2ECC71, "emoji": "✅"},  # Green
            "partial": {"color": 0xF39C12, "emoji": "⚠️"},  # Orange
            "error": {"color": 0xE74C3C, "emoji": "❌"},    # Red
        }
        config = status_config.get(status, status_config["success"])

        # Format topics
        topic_str = ", ".join(topics[:5]) if topics else "general"
        if topics and len(topics) > 5:
            topic_str += f" +{len(topics) - 5} more"

        # Format duration
        if duration_seconds > 0:
            duration_str = f"{duration_seconds:.1f}s"
        else:
            duration_str = "N/A"

        embed = {
            "title": f"🕷️ Spider Activity: {spider_name}",
            "description": f"{config['emoji']} Collected **{records_collected}** records",
            "color": config["color"],
            "fields": [
                {"name": "📊 Records", "value": str(records_collected), "inline": True},
                {"name": "🏷️ Topics", "value": topic_str, "inline": True},
                {"name": "⏱️ Duration", "value": duration_str, "inline": True},
            ],
            "footer": {
                "text": "AI Studio Spider Network"
            }
        }

        # Add source URL if provided
        if source_url:
            embed["fields"].append({"name": "🔗 Source", "value": source_url[:100], "inline": False})

        return self._send_message(self.CHANNEL_STATUS, "", embed=embed)

    def send_spider_error(self, spider_name: str, error_message: str,
                          source_url: str = "") -> bool:
        """
        Send a spider error notification to #system-status (Session 423).

        Args:
            spider_name: Name of the spider that failed
            error_message: Error description
            source_url: Data source URL that failed
        """
        embed = {
            "title": f"🕷️ Spider Error: {spider_name}",
            "description": f"❌ **Failed to collect data**\n\n```{error_message[:500]}```",
            "color": 0xE74C3C,  # Red
            "fields": [],
            "footer": {
                "text": "AI Studio Spider Network"
            }
        }

        if source_url:
            embed["fields"].append({"name": "🔗 Source", "value": source_url[:100], "inline": False})

        return self._send_message(self.CHANNEL_STATUS, "", embed=embed)

    def send_spider_summary(self, total_spiders: int, successful: int, failed: int,
                            total_records: int, top_topics: List[str] = None,
                            duration_seconds: float = 0) -> bool:
        """
        Send a spider batch summary to #system-status (Session 423).

        Args:
            total_spiders: Total number of spiders run
            successful: Number of successful runs
            failed: Number of failed runs
            total_records: Total records collected across all spiders
            top_topics: Most common topics found
            duration_seconds: Total batch duration
        """
        # Determine overall status color
        if failed == 0:
            color = 0x2ECC71  # Green - all success
            status_emoji = "✅"
        elif failed < successful:
            color = 0xF39C12  # Orange - mostly success
            status_emoji = "⚠️"
        else:
            color = 0xE74C3C  # Red - mostly failed
            status_emoji = "❌"

        # Format topics
        topic_str = ", ".join(top_topics[:8]) if top_topics else "various"

        # Format duration
        if duration_seconds > 60:
            duration_str = f"{duration_seconds / 60:.1f} min"
        else:
            duration_str = f"{duration_seconds:.1f}s"

        embed = {
            "title": f"🕸️ Spider Network Summary",
            "description": f"{status_emoji} **{successful}/{total_spiders}** spiders completed successfully",
            "color": color,
            "fields": [
                {"name": "📊 Total Records", "value": f"**{total_records:,}**", "inline": True},
                {"name": "✅ Successful", "value": str(successful), "inline": True},
                {"name": "❌ Failed", "value": str(failed), "inline": True},
                {"name": "🏷️ Top Topics", "value": topic_str, "inline": False},
                {"name": "⏱️ Total Duration", "value": duration_str, "inline": True},
            ],
            "footer": {
                "text": "AI Studio Spider Network Batch Run"
            }
        }

        return self._send_message(self.CHANNEL_STATUS, "", embed=embed)

    # Legacy method for backwards compatibility
    def send_spider_update(self, spider_name: str, records_collected: int,
                           source: str = "") -> bool:
        """Legacy method - use send_spider_activity instead."""
        return self.send_spider_activity(spider_name, records_collected, source_url=source)

    def send_system_status(self, component: str, status: str, message: str,
                           details: dict = None) -> bool:
        """
        Send a system status update for a specific component (Session 423).

        Args:
            component: Component name (e.g., 'training_spider', 'celery', 'redis')
            status: Status (completed, running, error)
            message: Status message
            details: Optional dict with additional details
        """
        status_config = {
            "completed": {"color": 0x2ECC71, "emoji": "✅"},
            "running": {"color": 0x3498DB, "emoji": "🔄"},
            "error": {"color": 0xE74C3C, "emoji": "❌"},
            "warning": {"color": 0xF39C12, "emoji": "⚠️"},
        }
        config = status_config.get(status, status_config["running"])

        embed = {
            "title": f"{config['emoji']} {component.replace('_', ' ').title()}",
            "description": message[:4096],
            "color": config["color"],
            "footer": {
                "text": "AI Studio System Status"
            }
        }

        # Add details as fields if provided
        if details:
            fields = []
            for key, value in list(details.items())[:5]:  # Max 5 fields
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value[:5])
                fields.append({
                    "name": key.replace("_", " ").title(),
                    "value": str(value)[:100],
                    "inline": True
                })
            embed["fields"] = fields

        return self._send_message(self.CHANNEL_STATUS, "", embed=embed)

    def send_boardroom_decision(self, title: str, decision: str, participants: List[str],
                                decision_type: str = "policy", impact: str = "medium") -> bool:
        """
        Send a boardroom decision notification to #boardroom.

        Args:
            title: Decision title
            decision: The decision content
            participants: Agents involved in the decision
            decision_type: Type (policy, architecture, workflow, strategy)
            impact: Impact level (low, medium, high, critical)
        """
        # Decision type emojis
        type_emojis = {
            "policy": "📜",
            "architecture": "🏗️",
            "workflow": "⚙️",
            "strategy": "🎯",
            "feature": "✨",
            "process": "🔄",
        }
        emoji = type_emojis.get(decision_type, "📋")

        # Impact colors
        impact_colors = {
            "low": 0x3498DB,      # Blue
            "medium": 0xF39C12,   # Orange
            "high": 0xE74C3C,     # Red
            "critical": 0x9B59B6, # Purple
        }
        color = impact_colors.get(impact, 0x3498DB)

        participant_str = ", ".join(participants[:5])
        if len(participants) > 5:
            participant_str += f" +{len(participants) - 5} more"

        embed = {
            "title": f"{emoji} {title}",
            "description": decision[:4096],
            "color": color,
            "author": {
                "name": "🏛️ Boardroom Decision"
            },
            "fields": [
                {"name": "Type", "value": decision_type.title(), "inline": True},
                {"name": "Impact", "value": impact.upper(), "inline": True},
                {"name": "Decision Makers", "value": participant_str, "inline": False}
            ],
            "footer": {
                "text": "AI Studio Boardroom"
            }
        }

        return self._send_message(self.CHANNEL_BOARDROOM, "", embed=embed)

    def send_opportunity(self, title: str, score: float, category: str,
                         potential: str = "", source: str = "",
                         description: str = "", urgency: str = "normal",
                         score_scale: int = 100) -> bool:
        """
        Send a high-value opportunity notification to #opportunities (Session 424).

        Args:
            title: Opportunity title
            score: Opportunity score (0-100 or 0-10 depending on score_scale)
            category: Category (freelance, digital_products, content, affiliate, etc.)
            potential: Revenue potential (e.g., "$500-2000/month")
            source: Data source (e.g., "ProductHunt", "RemoteOK")
            description: Brief description of the opportunity
            urgency: Urgency level (low, normal, high, urgent)
            score_scale: Maximum score value (100 for match_score, 10 for normalized)

        Returns:
            True if notification sent successfully
        """
        # Normalize score to 0-10 scale for display
        if score_scale == 100:
            normalized_score = score / 10.0
            threshold = 70  # 70/100 = 7.0/10
        else:
            normalized_score = score
            threshold = 7.0

        # Only post high-value opportunities (70+/100 or 7+/10)
        if score < threshold:
            logger.debug(f"Opportunity '{title}' score {score}/{score_scale} below threshold, not posting")
            return False

        # Category emojis
        category_emojis = {
            "freelance": "💼",
            "digital_products": "📦",
            "content": "📝",
            "affiliate": "🔗",
            "saas": "☁️",
            "consulting": "🎯",
            "education": "📚",
            "creative": "🎨",
            "tech": "💻",
            "finance": "📈",
            "financial": "📈",
            "jobs": "💼",
            "remote_work": "🏠",
            "crowdfunding": "🚀",
        }
        cat_emoji = category_emojis.get(category.lower(), "💡")

        # Score-based colors (using normalized 0-10 scale)
        if normalized_score >= 9.0:
            color = 0xFFD700  # Gold - exceptional
            score_emoji = "🏆"
        elif normalized_score >= 8.0:
            color = 0x2ECC71  # Green - excellent
            score_emoji = "🌟"
        elif normalized_score >= 7.0:
            color = 0x3498DB  # Blue - good
            score_emoji = "✨"
        else:
            color = 0x95A5A6  # Gray - moderate
            score_emoji = "📊"

        # Urgency indicator
        urgency_indicators = {
            "low": "",
            "normal": "",
            "high": "🔥 ",
            "urgent": "🚨 ",
        }
        urgency_prefix = urgency_indicators.get(urgency, "")

        # Build embed
        embed = {
            "title": f"{urgency_prefix}💰 {title[:200]}",
            "description": description[:2000] if description else "High-value opportunity detected!",
            "color": color,
            "author": {
                "name": f"{cat_emoji} {category.replace('_', ' ').title()} Opportunity"
            },
            "fields": [
                {"name": f"{score_emoji} Score", "value": f"**{normalized_score:.1f}/10**", "inline": True},
                {"name": "📂 Category", "value": category.replace("_", " ").title(), "inline": True},
            ],
            "footer": {
                "text": "AI Studio Opportunity Scanner"
            }
        }

        # Add optional fields
        if potential:
            embed["fields"].append({"name": "💵 Potential", "value": potential, "inline": True})

        if source:
            embed["fields"].append({"name": "🔍 Source", "value": source, "inline": True})

        return self._send_message(self.CHANNEL_OPPORTUNITIES, "", embed=embed)

    def send_opportunity_summary(self, total_found: int, high_value_count: int,
                                  top_categories: List[str] = None,
                                  avg_score: float = 0.0) -> bool:
        """
        Send a summary of opportunity scanning to #opportunities (Session 424).

        Args:
            total_found: Total opportunities found
            high_value_count: Number of high-value (7+) opportunities
            top_categories: Most common opportunity categories
            avg_score: Average opportunity score
        """
        # Color based on high-value count
        if high_value_count >= 5:
            color = 0xFFD700  # Gold
            status_emoji = "🏆"
        elif high_value_count >= 2:
            color = 0x2ECC71  # Green
            status_emoji = "✅"
        else:
            color = 0x3498DB  # Blue
            status_emoji = "📊"

        categories_str = ", ".join(top_categories[:5]) if top_categories else "various"

        embed = {
            "title": f"{status_emoji} Opportunity Scan Complete",
            "description": f"Found **{high_value_count}** high-value opportunities!",
            "color": color,
            "fields": [
                {"name": "📊 Total Found", "value": str(total_found), "inline": True},
                {"name": "🌟 High Value (7+)", "value": str(high_value_count), "inline": True},
                {"name": "📈 Avg Score", "value": f"{avg_score:.1f}/10", "inline": True},
                {"name": "📂 Top Categories", "value": categories_str, "inline": False},
            ],
            "footer": {
                "text": "AI Studio Opportunity Scanner"
            }
        }

        return self._send_message(self.CHANNEL_OPPORTUNITIES, "", embed=embed)

    def send_weekly_opportunity_digest(self, period_start: str, period_end: str,
                                        total_opportunities: int, high_value_count: int,
                                        tasks_created: int, tasks_won: int, tasks_lost: int,
                                        total_revenue: float, win_rate: float,
                                        top_opportunities: list = None,
                                        by_category: dict = None) -> bool:
        """
        Send a weekly opportunity digest to #boardroom (Session 425).

        Args:
            period_start: Start date string
            period_end: End date string
            total_opportunities: Total opportunities found
            high_value_count: High-value (70+) opportunities
            tasks_created: Tasks auto-created from opportunities
            tasks_won: Tasks marked as won
            tasks_lost: Tasks marked as lost
            total_revenue: Total revenue from won tasks
            win_rate: Win rate percentage
            top_opportunities: List of top opportunity dicts
            by_category: Category breakdown dict
        """
        # Color based on performance
        if win_rate >= 50:
            color = 0xFFD700  # Gold
            performance_emoji = "🏆"
        elif win_rate >= 30:
            color = 0x2ECC71  # Green
            performance_emoji = "✅"
        elif tasks_won > 0:
            color = 0x3498DB  # Blue
            performance_emoji = "📊"
        else:
            color = 0x95A5A6  # Gray
            performance_emoji = "📋"

        # Build description
        description_lines = [
            f"**Period:** {period_start} to {period_end}",
            "",
            f"📊 **Total Opportunities Found:** {total_opportunities}",
            f"🌟 **High-Value (70+):** {high_value_count}",
            f"📋 **Tasks Created:** {tasks_created}",
        ]

        if tasks_won or tasks_lost:
            description_lines.append("")
            description_lines.append("**Outcomes:**")
            description_lines.append(f"✅ Won: {tasks_won} | ❌ Lost: {tasks_lost}")
            if win_rate > 0:
                description_lines.append(f"📈 Win Rate: **{win_rate:.1f}%**")

        if total_revenue > 0:
            description_lines.append("")
            description_lines.append(f"💰 **Total Revenue:** ${total_revenue:,.2f}")

        description = "\n".join(description_lines)

        embed = {
            "title": f"{performance_emoji} Weekly Opportunity Digest",
            "description": description,
            "color": color,
            "fields": [],
            "footer": {
                "text": "AI Studio Opportunity Pipeline"
            }
        }

        # Add top opportunities if provided
        if top_opportunities:
            top_opps_text = "\n".join([
                f"• **{opp.get('title', 'Unknown')[:30]}** (Score: {opp.get('score', 0)})"
                for opp in top_opportunities[:5]
            ])
            embed["fields"].append({
                "name": "🌟 Top Opportunities",
                "value": top_opps_text or "None",
                "inline": False
            })

        # Add category breakdown if provided
        if by_category:
            categories_text = "\n".join([
                f"• {cat.replace('_', ' ').title()}: {count}"
                for cat, count in list(by_category.items())[:5]
            ])
            embed["fields"].append({
                "name": "📂 By Category",
                "value": categories_text or "None",
                "inline": False
            })

        return self._send_message(self.CHANNEL_BOARDROOM, "", embed=embed)

    # =========================================================================
    # Session 555 Phase C: Weekly Synthesis
    # =========================================================================

    def send_weekly_synthesis(self, synthesis: 'WeeklySynthesis') -> bool:
        """
        Send weekly synthesis to #boardroom (Session 555 Phase C).

        Delivers the comprehensive weekly executive summary including:
        - Artifacts extracted
        - Decisions made
        - Execution results
        - AI-generated insights and recommendations

        Args:
            synthesis: WeeklySynthesis model object

        Returns:
            True if notification sent successfully
        """
        # Color based on execution success rate
        if synthesis.execution_success_rate >= 0.8:
            color = 0x22c55e  # Green
            performance = "Excellent"
            performance_emoji = "🟢"
        elif synthesis.execution_success_rate >= 0.6:
            color = 0xf59e0b  # Yellow/Amber
            performance = "Good"
            performance_emoji = "🟡"
        elif synthesis.executions_total > 0:
            color = 0xef4444  # Red
            performance = "Needs Attention"
            performance_emoji = "🔴"
        else:
            color = 0x3498DB  # Blue - no executions yet
            performance = "Getting Started"
            performance_emoji = "🔵"

        # Calculate total decisions
        total_decisions = (
            synthesis.decisions_approved +
            synthesis.decisions_rejected +
            synthesis.decisions_deferred
        )

        # Format executions display
        if synthesis.executions_total > 0:
            exec_display = f"{synthesis.executions_succeeded}/{synthesis.executions_total}"
        else:
            exec_display = "0"

        # Build embed
        embed = {
            "title": f"📊 Weekly Synthesis: {synthesis.period_start} to {synthesis.period_end}",
            "description": (
                synthesis.trend_analysis[:500]
                if synthesis.trend_analysis
                else "Weekly executive summary of agent activity and decisions."
            ),
            "color": color,
            "fields": [
                {"name": "📋 Artifacts Extracted", "value": str(synthesis.artifacts_extracted), "inline": True},
                {"name": "✅ Decisions Made", "value": str(total_decisions), "inline": True},
                {"name": "⚡ Executions", "value": exec_display, "inline": True},
                {"name": "📈 Success Rate", "value": f"{synthesis.execution_success_rate:.0%}", "inline": True},
                {"name": "⏱️ Avg Time", "value": f"{synthesis.avg_execution_time_ms}ms", "inline": True},
                {"name": f"{performance_emoji} Performance", "value": performance, "inline": True},
            ],
            "footer": {
                "text": "Chief of Staff Layer - Phase C | Session 555"
            }
        }

        # Add pending items alert if significant
        if synthesis.pending_high_priority > 0:
            embed["fields"].append({
                "name": "⚠️ Attention Required",
                "value": f"{synthesis.pending_high_priority} high-priority items pending",
                "inline": False
            })

        # Add recommendations if available (limit to top 3)
        if synthesis.recommendations:
            recs = synthesis.recommendations[:3]
            recs_text = "\n".join(f"• {r}" for r in recs)
            embed["fields"].append({
                "name": "💡 Recommendations",
                "value": recs_text[:1024],  # Discord field limit
                "inline": False
            })

        # Add key themes if available
        if synthesis.key_themes:
            themes = synthesis.key_themes[:3]
            themes_text = ", ".join(themes)
            embed["fields"].append({
                "name": "🔍 Key Themes",
                "value": themes_text[:1024],
                "inline": False
            })

        return self._send_message(self.CHANNEL_BOARDROOM, "", embed=embed)

    # =========================================================================
    # Session 460: Autonomous Intelligence Loop - SEC/Market Alerts
    # =========================================================================

    def send_sec_filing_alert(self, company: str, form_type: str, description: str,
                               filed_at: str, url: str = "", is_high_impact: bool = False,
                               items: List[str] = None) -> bool:
        """
        Send an SEC filing alert to #market-alerts (Session 460).

        Args:
            company: Company name
            form_type: Filing type (8-K, 10-K, 10-Q, etc.)
            description: Filing description or items
            filed_at: Filing date string
            url: URL to the SEC filing
            is_high_impact: Whether this is a high-impact filing
            items: List of 8-K items (e.g., "Item 2.02: Results of Operations")

        Returns:
            True if notification sent successfully
        """
        # Form type descriptions and colors
        form_config = {
            "8-K": {"emoji": "🚨", "color": 0xE74C3C, "desc": "Material Event"},
            "10-K": {"emoji": "📊", "color": 0x3498DB, "desc": "Annual Report"},
            "10-Q": {"emoji": "📈", "color": 0x2ECC71, "desc": "Quarterly Report"},
            "4": {"emoji": "👤", "color": 0xF39C12, "desc": "Insider Trading"},
            "S-1": {"emoji": "🚀", "color": 0x9B59B6, "desc": "IPO Registration"},
            "13F-HR": {"emoji": "🏦", "color": 0x1ABC9C, "desc": "Institutional Holdings"},
        }
        config = form_config.get(form_type, {"emoji": "📄", "color": 0x95A5A6, "desc": "Filing"})

        # High impact gets special treatment
        if is_high_impact:
            config["emoji"] = "🔥"
            config["color"] = 0xFFD700  # Gold

        # Build embed
        embed = {
            "title": f"{config['emoji']} {company} - {form_type}",
            "description": description[:2000] if description else f"{form_type} Filing",
            "color": config["color"],
            "author": {
                "name": f"📈 SEC EDGAR - {config['desc']}"
            },
            "fields": [
                {"name": "📅 Filed", "value": filed_at, "inline": True},
                {"name": "📋 Type", "value": form_type, "inline": True},
            ],
            "footer": {
                "text": "AI Studio Market Intelligence"
            }
        }

        # Add items if present (for 8-K filings)
        if items:
            items_str = "\n".join([f"• {item}" for item in items[:5]])
            embed["fields"].append({"name": "📝 Items", "value": items_str, "inline": False})

        # Add URL if present
        if url:
            embed["url"] = url

        # Add high impact indicator
        if is_high_impact:
            embed["fields"].insert(0, {"name": "⚠️ Impact", "value": "**HIGH IMPACT**", "inline": True})

        return self._send_message(self.CHANNEL_MARKET_ALERTS, "", embed=embed)

    def send_market_digest(self, filings_count: int, high_impact_count: int,
                           companies: List[str] = None, period: str = "24h") -> bool:
        """
        Send a market activity digest (Session 460).

        Args:
            filings_count: Total filings in period
            high_impact_count: Number of high-impact filings
            companies: List of company names with filings
            period: Time period (e.g., "24h", "7d")
        """
        # Color based on activity level
        if high_impact_count >= 5:
            color = 0xFFD700  # Gold - lots of action
            emoji = "🔥"
        elif high_impact_count >= 2:
            color = 0xE74C3C  # Red - some action
            emoji = "📊"
        else:
            color = 0x3498DB  # Blue - normal
            emoji = "📈"

        companies_str = ", ".join(companies[:10]) if companies else "Various"
        if companies and len(companies) > 10:
            companies_str += f" +{len(companies) - 10} more"

        embed = {
            "title": f"{emoji} Market Activity Digest",
            "description": f"**{filings_count}** SEC filings in the last **{period}**",
            "color": color,
            "fields": [
                {"name": "📊 Total Filings", "value": str(filings_count), "inline": True},
                {"name": "🔥 High Impact", "value": str(high_impact_count), "inline": True},
                {"name": "🏢 Companies", "value": companies_str, "inline": False},
            ],
            "footer": {
                "text": "AI Studio Market Intelligence"
            }
        }

        return self._send_message(self.CHANNEL_MARKET_ALERTS, "", embed=embed)

    def send_content_opportunity(self, topic: str, satire_angle: str, style_suggestion: str,
                                  source: str = "", urgency: str = "normal") -> bool:
        """
        Send a content creation opportunity notification (Session 460).

        Args:
            topic: The trending topic
            satire_angle: Suggested satire/commentary angle
            style_suggestion: Suggested art style (e.g., "South Park", "Political Cartoon")
            source: Where the topic was found
            urgency: How time-sensitive (low, normal, high)
        """
        urgency_config = {
            "low": {"emoji": "💡", "color": 0x3498DB},
            "normal": {"emoji": "🎨", "color": 0x9B59B6},
            "high": {"emoji": "🔥", "color": 0xE74C3C},
        }
        config = urgency_config.get(urgency, urgency_config["normal"])

        embed = {
            "title": f"{config['emoji']} Content Opportunity",
            "description": f"**Topic:** {topic[:500]}",
            "color": config["color"],
            "fields": [
                {"name": "🎭 Satire Angle", "value": satire_angle[:500], "inline": False},
                {"name": "🎨 Style", "value": style_suggestion, "inline": True},
            ],
            "footer": {
                "text": "AI Studio Content Opportunity Scanner"
            }
        }

        if source:
            embed["fields"].append({"name": "📰 Source", "value": source, "inline": True})

        return self._send_message(self.CHANNEL_OPPORTUNITIES, "", embed=embed)

    def send_daily_digest(self, date: str, sec_summary: dict = None,
                          tech_news: List[str] = None, job_opportunities: List[dict] = None,
                          content_ideas: List[str] = None, agent_activity: dict = None) -> bool:
        """
        Send a comprehensive daily intelligence digest (Session 460).

        Args:
            date: Date string
            sec_summary: Dict with {filings: int, high_impact: int, top_companies: []}
            tech_news: List of top tech headlines
            job_opportunities: List of {title, company, salary} dicts
            content_ideas: List of content opportunity descriptions
            agent_activity: Dict with {dreams: int, conversations: int, learnings: int}
        """
        # Build description sections
        sections = []

        # SEC Summary
        if sec_summary:
            sections.append(f"**📈 Market Activity**")
            sections.append(f"• {sec_summary.get('filings', 0)} SEC filings")
            sections.append(f"• {sec_summary.get('high_impact', 0)} high-impact events")
            if sec_summary.get('top_companies'):
                sections.append(f"• Top: {', '.join(sec_summary['top_companies'][:5])}")
            sections.append("")

        # Tech News
        if tech_news:
            sections.append(f"**💻 Tech News Highlights**")
            for headline in tech_news[:5]:
                sections.append(f"• {headline[:100]}")
            sections.append("")

        # Job Opportunities
        if job_opportunities:
            sections.append(f"**💼 Job Opportunities**")
            for job in job_opportunities[:5]:
                salary = job.get('salary', 'N/A')
                sections.append(f"• {job.get('title', 'Unknown')} @ {job.get('company', 'Unknown')} ({salary})")
            sections.append("")

        # Content Ideas
        if content_ideas:
            sections.append(f"**🎨 Content Ideas**")
            for idea in content_ideas[:3]:
                sections.append(f"• {idea[:100]}")
            sections.append("")

        # Agent Activity
        if agent_activity:
            sections.append(f"**🤖 Agent Activity**")
            sections.append(f"• {agent_activity.get('dreams', 0)} dreams")
            sections.append(f"• {agent_activity.get('conversations', 0)} conversations")
            sections.append(f"• {agent_activity.get('learnings', 0)} learnings")

        description = "\n".join(sections) if sections else "No activity to report."

        embed = {
            "title": f"☀️ Daily Intelligence Digest - {date}",
            "description": description[:4000],
            "color": 0xFFD700,  # Gold
            "footer": {
                "text": "AI Studio Autonomous Intelligence Loop"
            }
        }

        return self._send_message(self.CHANNEL_BOARDROOM, "", embed=embed)

    def send_embed(self, channel_name: str, title: str, description: str,
                   color: int = 0x3498db, fields: List[Dict[str, Any]] = None,
                   footer: str = None) -> bool:
        """
        Send a custom embed to any Discord channel by name.

        Session 642: Generic embed sender for flexible notifications.

        Args:
            channel_name: Channel name like 'boardroom', 'market-intelligence', etc.
            title: Embed title
            description: Embed description
            color: Embed color (hex int)
            fields: List of {'name': str, 'value': str, 'inline': bool} dicts
            footer: Optional footer text

        Returns:
            True if sent successfully
        """
        # Map channel names to IDs
        channel_map = {
            'dreams': self.CHANNEL_DREAMS,
            'agent-dreams': self.CHANNEL_DREAMS,
            'conversations': self.CHANNEL_CONVERSATIONS,
            'agent-conversations': self.CHANNEL_CONVERSATIONS,
            'status': self.CHANNEL_STATUS,
            'system-status': self.CHANNEL_STATUS,
            'learning': self.CHANNEL_LEARNING,
            'boardroom': self.CHANNEL_BOARDROOM,
            'opportunities': self.CHANNEL_OPPORTUNITIES,
            'gallery': self.CHANNEL_GALLERY,
            'profile': self.CHANNEL_PROFILE,
            'market-alerts': self.CHANNEL_MARKET_ALERTS,
            'market-intelligence': self.CHANNEL_MARKET_ALERTS,
            'stock-alerts': self.CHANNEL_STOCK_ALERTS,
            'blockchain-alerts': self.CHANNEL_BLOCKCHAIN_ALERTS,
            'podcast-library': self.CHANNEL_PODCAST_LIBRARY,
        }

        channel_id = channel_map.get(channel_name.lower())
        if not channel_id:
            logger.warning(f"Unknown Discord channel: {channel_name}")
            return False

        embed = {
            "title": title[:256],  # Discord limit
            "description": description[:4096],  # Discord limit
            "color": color,
            "timestamp": datetime.utcnow().isoformat()
        }

        if fields:
            embed["fields"] = [
                {
                    "name": f.get('name', '')[:256],
                    "value": f.get('value', '')[:1024],
                    "inline": f.get('inline', True)
                }
                for f in fields[:25]  # Max 25 fields
            ]

        if footer:
            embed["footer"] = {"text": footer[:2048]}

        return self._send_message(channel_id, "", embed=embed)

    # Channel name → ID map (shared with send_embed)
    _CHANNEL_MAP = {
        'dreams': 'CHANNEL_DREAMS',
        'agent-dreams': 'CHANNEL_DREAMS',
        'conversations': 'CHANNEL_CONVERSATIONS',
        'agent-conversations': 'CHANNEL_CONVERSATIONS',
        'status': 'CHANNEL_STATUS',
        'system-status': 'CHANNEL_STATUS',
        'learning': 'CHANNEL_LEARNING',
        'boardroom': 'CHANNEL_BOARDROOM',
        'opportunities': 'CHANNEL_OPPORTUNITIES',
        'gallery': 'CHANNEL_GALLERY',
        'profile': 'CHANNEL_PROFILE',
        'market-alerts': 'CHANNEL_MARKET_ALERTS',
        'market-intelligence': 'CHANNEL_MARKET_ALERTS',
        'stock-alerts': 'CHANNEL_STOCK_ALERTS',
        'blockchain-alerts': 'CHANNEL_BLOCKCHAIN_ALERTS',
        'podcast-library': 'CHANNEL_PODCAST_LIBRARY',
    }

    def send_to_channel(self, channel_name: str, message: str) -> bool:
        """
        Send a plain-text message to a Discord channel by name.

        Args:
            channel_name: Channel name like 'system-status', 'boardroom', etc.
            message: Message content (max 2000 chars, truncated automatically)

        Returns:
            True if sent successfully
        """
        attr = self._CHANNEL_MAP.get(channel_name.lower())
        if not attr:
            logger.warning(f"Unknown Discord channel: {channel_name}")
            return False
        channel_id = getattr(self, attr)
        return self._send_message(channel_id, message)

    def test_connection(self) -> dict:
        """
        Test the Discord connection by sending test messages to all channels.

        Returns:
            Dict with results for each channel
        """
        results = {}

        # Test dreams channel
        results["dreams"] = self.send_dream(
            agent_name="Test Agent",
            dream_title="Connection Test Dream",
            dream_content="This is a test message to verify Discord integration is working!",
            dream_type="creative_idea",
            vividness=0.8
        )

        # Test conversations channel
        results["conversations"] = self.send_conversation(
            participants=["Test Agent 1", "Test Agent 2"],
            topic="Testing Discord Integration",
            synthesis="The agents agreed that Discord integration is awesome!",
            mode="consensus"
        )

        # Test status channel
        results["status"] = self.send_status(
            title="Discord Integration Test",
            message="✅ All systems connected! AI Studio is now posting to Discord.",
            status_type="success"
        )

        # Test learning channel
        results["learning"] = self.send_knowledge(
            agent_name="Test Agent",
            title="Test Learning Entry",
            summary="Testing the new dedicated learning channel!",
            knowledge_type="insight",
            confidence=0.9
        )

        # Test boardroom channel
        results["boardroom"] = self.send_boardroom_decision(
            title="Test Boardroom Decision",
            decision="Testing the new boardroom decisions channel for agent governance!",
            participants=["CTO Agent", "COO Agent"],
            decision_type="policy",
            impact="low"
        )

        return results

    # =========================================================================
    # Session 430: Image Delivery to Gallery
    # =========================================================================

    def send_image_to_gallery(self, username: str, prompt: str, image_url: str,
                               image_id: int = None, model: str = "Unknown",
                               generation_time: float = 0, discord_user_id: str = None) -> bool:
        """
        Send a generated image to the #gallery channel (Session 430: Discord-First).

        This notifies the gallery channel when any user creates an image.
        For personalized delivery, use send_image_to_user() instead.

        Args:
            username: Username of the creator
            prompt: The prompt used to generate the image
            image_url: Full URL to the image
            image_id: Database ID of the image (for reference)
            model: Model used for generation
            generation_time: Time taken to generate (seconds)
            discord_user_id: Optional Discord user ID to mention

        Returns:
            True if notification sent successfully
        """
        # Truncate prompt for title
        prompt_preview = prompt[:100] + "..." if len(prompt) > 100 else prompt

        # Build embed with image
        embed = {
            "title": f"🎨 New Creation",
            "description": f"**Prompt:** {prompt_preview}",
            "color": 0x9B59B6,  # Purple for creations
            "author": {
                "name": f"👤 {username}"
            },
            "image": {
                "url": image_url
            },
            "fields": [
                {"name": "🤖 Model", "value": model, "inline": True},
            ],
            "footer": {
                "text": "AI Studio Gallery"
            }
        }

        # Add image ID for reference
        if image_id:
            embed["fields"].append({"name": "🆔 ID", "value": f"#{image_id}", "inline": True})

        # Add generation time if available
        if generation_time > 0:
            embed["fields"].append({"name": "⏱️ Time", "value": f"{generation_time:.1f}s", "inline": True})

        # Add mention if discord_user_id provided
        content = ""
        if discord_user_id:
            content = f"<@{discord_user_id}> Your image is ready!"

        return self._send_message(self.CHANNEL_GALLERY, content, embed=embed)

    def send_image_dm(self, discord_user_id: str, prompt: str, image_url: str,
                       image_id: int = None, model: str = "Unknown") -> bool:
        """
        Send a generated image directly to a user's DMs (Session 430).

        Args:
            discord_user_id: Discord user ID to DM
            prompt: The prompt used to generate the image
            image_url: Full URL to the image
            image_id: Database ID of the image
            model: Model used for generation

        Returns:
            True if DM sent successfully
        """
        if not self.enabled:
            logger.debug(f"Discord disabled, would DM {discord_user_id}")
            return False

        # First, create a DM channel with the user
        dm_url = f"{self.API_BASE}/users/@me/channels"
        dm_payload = {"recipient_id": discord_user_id}

        try:
            dm_response = requests.post(dm_url, headers=self._get_headers(), json=dm_payload, timeout=10)
            if dm_response.status_code != 200:
                logger.error(f"Failed to create DM channel: {dm_response.status_code} - {dm_response.text}")
                return False

            dm_channel_id = dm_response.json().get("id")
            if not dm_channel_id:
                logger.error("No DM channel ID returned")
                return False

            # Build embed
            prompt_preview = prompt[:100] + "..." if len(prompt) > 100 else prompt
            embed = {
                "title": f"🎨 Your Image is Ready!",
                "description": f"**Prompt:** {prompt_preview}",
                "color": 0x2ECC71,  # Green for success
                "image": {
                    "url": image_url
                },
                "fields": [
                    {"name": "🤖 Model", "value": model, "inline": True},
                ],
                "footer": {
                    "text": "AI Studio • Use /gallery to see all your creations"
                }
            }

            if image_id:
                embed["fields"].append({"name": "🆔 ID", "value": f"#{image_id}", "inline": True})

            # Send the DM
            return self._send_message(dm_channel_id, "", embed=embed)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send image DM: {e}")
            return False

    def deliver_image_to_user(self, user, image_url: str, prompt: str,
                               image_id: int = None, model: str = "Unknown",
                               generation_time: float = 0) -> dict:
        """
        Deliver an image to a user via Discord (Session 430).

        This is the main method to call after image generation.
        It will:
        1. Post to #gallery channel (public)
        2. Send DM to user if they have Discord linked

        Args:
            user: Django User object (must have discord_id attribute)
            image_url: Full URL to the image
            prompt: The generation prompt
            image_id: Database ID
            model: Model used
            generation_time: Generation time in seconds

        Returns:
            dict with 'gallery' and 'dm' keys indicating success
        """
        results = {"gallery": False, "dm": False}

        discord_user_id = getattr(user, 'discord_id', None) if user else None
        username = getattr(user, 'username', 'Anonymous') if user else 'Anonymous'

        # Always post to gallery channel
        results["gallery"] = self.send_image_to_gallery(
            username=username,
            prompt=prompt,
            image_url=image_url,
            image_id=image_id,
            model=model,
            generation_time=generation_time,
            discord_user_id=discord_user_id
        )

        # Send DM if user has Discord linked
        if discord_user_id:
            results["dm"] = self.send_image_dm(
                discord_user_id=discord_user_id,
                prompt=prompt,
                image_url=image_url,
                image_id=image_id,
                model=model
            )
            logger.info(f"Image delivered to Discord user {discord_user_id}: gallery={results['gallery']}, dm={results['dm']}")
        else:
            logger.debug(f"User {username} has no Discord linked, skipping DM")

        return results

    # =========================================================================
    # Session 461/477: Stock Market Intelligence Alerts
    # =========================================================================

    def send_stock_alert(self, alert_or_ticker, severity: str = None, alert_type: str = None,
                          message: str = None, details: List[dict] = None,
                          is_correlated: bool = False) -> bool:
        """
        Send a stock market alert to #stock-alerts (Session 461/477).

        Args:
            alert_or_ticker: StockMarketAlert model object OR ticker string (legacy)
            severity: Alert severity (only if ticker string provided)
            alert_type: Type of alert (only if ticker string provided)
            message: Alert message (only if ticker string provided)
            details: List of detailed findings (only if ticker string provided)
            is_correlated: Whether multiple systems flagged this stock

        Returns:
            True if notification sent successfully
        """
        # Handle StockMarketAlert model object (Session 477)
        if hasattr(alert_or_ticker, 'symbol'):
            alert = alert_or_ticker
            ticker = alert.symbol or 'UNKNOWN'
            alert_type = alert.alert_type or 'market_movement'
            title = alert.title or f'{ticker} Alert'
            summary = alert.summary or ''
            company_name = alert.company_name or ticker
            bull_case = alert.bull_case or ''
            bear_case = alert.bear_case or ''
            disagreement = alert.disagreement_level or 'mild'
            bull_score = alert.bull_score or 50
            bear_score = alert.bear_score or 50
            confidence = float(alert.confidence_score) if alert.confidence_score else 0.5
            current_price = float(alert.current_price) if alert.current_price else 0
            price_change = float(alert.price_change_24h) if alert.price_change_24h else 0
            recommended_action = alert.recommended_action or 'watch'

            # Determine severity from alert type and scores
            if alert_type in ['high_conviction_bull', 'high_conviction_bear']:
                severity = 'HIGH'
            elif alert_type == 'debate_zone':
                severity = 'MEDIUM'
            elif alert_type == 'risk_alert':
                severity = 'HIGH'
            else:
                severity = 'LOW'

            # Alert type emojis and colors
            type_config = {
                'high_conviction_bull': {'emoji': '🐂📈', 'color': 0x2ECC71},  # Green
                'high_conviction_bear': {'emoji': '🐻📉', 'color': 0xE74C3C},  # Red
                'debate_zone': {'emoji': '⚔️🤔', 'color': 0xFF00FF},  # Magenta - disagreement!
                'risk_alert': {'emoji': '🚨⚠️', 'color': 0xFFA500},  # Orange
                'momentum_shift': {'emoji': '🔄📊', 'color': 0x3498DB},  # Blue
                'institutional_activity': {'emoji': '🏛️💼', 'color': 0x9B59B6},  # Purple
                'anomaly_detected': {'emoji': '🔍❓', 'color': 0xF39C12},  # Yellow
                'earnings_alert': {'emoji': '📊💰', 'color': 0x1ABC9C},  # Teal
            }
            config = type_config.get(alert_type, {'emoji': '📈', 'color': 0x95A5A6})

            embed = {
                "title": f"{config['emoji']} {title[:150]}",
                "description": summary[:2000] if summary else f"Stock market alert for {ticker}",
                "color": config['color'],
                "author": {
                    "name": f"📈 Market Intelligence - {alert_type.replace('_', ' ').title()}"
                },
                "fields": [
                    {"name": "🏷️ Symbol", "value": f"**{ticker}**", "inline": True},
                ],
                "footer": {
                    "text": "AI Studio Market Intelligence Desk"
                },
                "timestamp": datetime.utcnow().isoformat()
            }

            # Add company name if different from ticker
            if company_name and company_name != ticker:
                embed["fields"].append({"name": "🏢 Company", "value": company_name[:50], "inline": True})

            # Add price info
            if current_price > 0:
                price_emoji = "📈" if price_change > 0 else "📉" if price_change < 0 else "➖"
                embed["fields"].append({"name": f"{price_emoji} Price", "value": f"${current_price:.2f}", "inline": True})

            if price_change != 0:
                change_color = "🟢" if price_change > 0 else "🔴"
                embed["fields"].append({"name": f"{change_color} 24h Change", "value": f"{price_change:+.2f}%", "inline": True})

            # Bull vs Bear analysis (key feature!)
            if bull_case or bear_case:
                # Show disagreement level with visual indicator
                disagreement_indicator = {
                    'consensus': '🤝 Consensus',
                    'mild': '🟡 Mild Disagreement',
                    'strong': '🟠 Strong Disagreement',
                    'extreme': '🔴 Extreme Disagreement'
                }
                embed["fields"].append({
                    "name": "⚖️ Agent Disagreement",
                    "value": disagreement_indicator.get(disagreement, disagreement),
                    "inline": True
                })

                # Bull score vs Bear score visualization
                bull_bar = "🟢" * (bull_score // 20) + "⚪" * (5 - bull_score // 20)
                bear_bar = "🔴" * (bear_score // 20) + "⚪" * (5 - bear_score // 20)
                embed["fields"].append({
                    "name": "🐂 Bull",
                    "value": f"{bull_bar} {bull_score}%",
                    "inline": True
                })
                embed["fields"].append({
                    "name": "🐻 Bear",
                    "value": f"{bear_bar} {bear_score}%",
                    "inline": True
                })

                if bull_case:
                    embed["fields"].append({
                        "name": "🐂 Bull Case",
                        "value": bull_case[:400],
                        "inline": False
                    })

                if bear_case:
                    embed["fields"].append({
                        "name": "🐻 Bear Case",
                        "value": bear_case[:400],
                        "inline": False
                    })

            # Add confidence
            embed["fields"].append({"name": "📊 Confidence", "value": f"{confidence:.0%}", "inline": True})

            # Add recommended action
            action_emojis = {
                'watch': '👀',
                'research': '🔍',
                'consider_buy': '💚',
                'consider_sell': '❤️',
                'hedge': '🛡️',
                'avoid': '🚫'
            }
            action_emoji = action_emojis.get(recommended_action, '📋')
            embed["fields"].append({
                "name": f"{action_emoji} Action",
                "value": recommended_action.replace('_', ' ').title(),
                "inline": True
            })

            return self._send_message(self.CHANNEL_STOCK_ALERTS, "", embed=embed)

        # Legacy: Handle ticker string (old API)
        ticker = alert_or_ticker
        severity = severity or 'MEDIUM'
        alert_type = alert_type or 'MARKET_MOVEMENT'
        message = message or 'Stock alert triggered'

        # Severity colors and emojis
        severity_config = {
            "CRITICAL": {"emoji": "🚨", "color": 0xFF0000},  # Red
            "HIGH": {"emoji": "⚠️", "color": 0xFFA500},  # Orange
            "MEDIUM": {"emoji": "📊", "color": 0xFFD700},  # Gold
            "LOW": {"emoji": "ℹ️", "color": 0x3498DB},  # Blue
        }
        config = severity_config.get(severity.upper(), {"emoji": "📈", "color": 0x95A5A6})

        # Correlated alerts get special treatment
        title_prefix = "🔗 CORRELATED " if is_correlated else ""

        # Build embed
        embed = {
            "title": f"{config['emoji']} {title_prefix}STOCK ALERT: {ticker}",
            "description": message[:2000],
            "color": config["color"],
            "author": {
                "name": f"📈 Stock Audit System - {severity}"
            },
            "fields": [
                {"name": "🎯 Severity", "value": severity, "inline": True},
                {"name": "📋 Type", "value": alert_type, "inline": True},
            ],
            "footer": {
                "text": "AI Studio Stock Intelligence"
            }
        }

        # Add correlation indicator if applicable
        if is_correlated:
            embed["fields"].append({
                "name": "🔗 Correlated",
                "value": "Multiple systems flagged this stock",
                "inline": True
            })

        # Add details if provided (limit to 3 to avoid spam)
        if details:
            detail_text = []
            for detail in details[:3]:
                detail_msg = detail.get('message', str(detail))[:100]
                detail_text.append(f"• {detail_msg}")
            if detail_text:
                embed["fields"].append({
                    "name": "📋 Details",
                    "value": "\n".join(detail_text),
                    "inline": False
                })

        return self._send_message(self.CHANNEL_STOCK_ALERTS, "", embed=embed)

    def send_stock_audit_summary(self, total_alerts: int, critical_count: int,
                                   high_count: int, tickers_flagged: List[str],
                                   correlated_count: int = 0) -> bool:
        """
        Send a summary of the stock audit cycle (Session 461).

        Args:
            total_alerts: Total number of alerts generated
            critical_count: Number of CRITICAL alerts
            high_count: Number of HIGH alerts
            tickers_flagged: List of tickers with alerts
            correlated_count: Number of correlated findings

        Returns:
            True if notification sent successfully
        """
        # Determine overall color based on severity
        if critical_count > 0:
            color = 0xFF0000  # Red
            emoji = "🚨"
        elif high_count > 0:
            color = 0xFFA500  # Orange
            emoji = "⚠️"
        elif total_alerts > 0:
            color = 0xFFD700  # Gold
            emoji = "📊"
        else:
            color = 0x2ECC71  # Green
            emoji = "✅"

        # Format tickers list
        tickers_str = ", ".join(tickers_flagged[:10]) if tickers_flagged else "None"
        if len(tickers_flagged) > 10:
            tickers_str += f" (+{len(tickers_flagged) - 10} more)"

        embed = {
            "title": f"{emoji} Stock Audit Cycle Complete",
            "description": f"Scanned market for anomalies and insider activity.",
            "color": color,
            "fields": [
                {"name": "📊 Total Alerts", "value": str(total_alerts), "inline": True},
                {"name": "🚨 Critical", "value": str(critical_count), "inline": True},
                {"name": "⚠️ High", "value": str(high_count), "inline": True},
                {"name": "🔗 Correlated", "value": str(correlated_count), "inline": True},
                {"name": "📈 Tickers Flagged", "value": tickers_str, "inline": False},
            ],
            "footer": {
                "text": "AI Studio Stock Audit System"
            }
        }

        return self._send_message(self.CHANNEL_STOCK_ALERTS, "", embed=embed)

    def send_market_intelligence_brief(self, brief: Dict[str, Any]) -> bool:
        """
        Send the daily Market Intelligence Brief to Discord (Session 462).

        This is the output of the first Tier 1 Autonomous Situation.
        The brief contains bull vs bear debate synthesis with internal disagreement.

        Args:
            brief: Market intelligence brief dict with executive_summary, debate_zone, etc.

        Returns:
            True if notification sent successfully
        """
        # Extract key metrics
        debate_count = brief.get('debate_zone_count', 0)
        bull_count = len(brief.get('bullish_opportunities', []))
        bear_count = len(brief.get('bearish_warnings', []))
        total_stocks = brief.get('total_stocks_analyzed', 0)

        # Determine color based on debate intensity
        if debate_count > 3:
            color = 0xFF00FF  # Magenta - High disagreement (interesting!)
            emoji = "⚔️"
        elif bull_count > bear_count:
            color = 0x2ECC71  # Green - Bullish tilt
            emoji = "📈"
        elif bear_count > bull_count:
            color = 0xFF0000  # Red - Bearish tilt
            emoji = "📉"
        else:
            color = 0xFFD700  # Gold - Balanced
            emoji = "⚖️"

        # Build debate zone summary
        debate_summary = "No major disagreements"
        if debate_count > 0:
            debate_tickers = [d.get('ticker', 'N/A') for d in brief.get('debate_zone', [])[:3]]
            debate_summary = f"{', '.join(debate_tickers)}"
            if debate_count > 3:
                debate_summary += f" (+{debate_count - 3} more)"

        # Build bullish/bearish summaries
        bull_summary = "None"
        if bull_count > 0:
            bull_tickers = [d.get('ticker', 'N/A') for d in brief.get('bullish_opportunities', [])[:3]]
            bull_summary = ", ".join(bull_tickers)
            if bull_count > 3:
                bull_summary += f" (+{bull_count - 3} more)"

        bear_summary = "None"
        if bear_count > 0:
            bear_tickers = [d.get('ticker', 'N/A') for d in brief.get('bearish_warnings', [])[:3]]
            bear_summary = ", ".join(bear_tickers)
            if bear_count > 3:
                bear_summary += f" (+{bear_count - 3} more)"

        # Risk alerts
        risk_count = len(brief.get('risk_alerts', []))
        risk_summary = f"{risk_count} alerts" if risk_count > 0 else "None"

        embed = {
            "title": f"{emoji} Daily Market Intelligence Brief",
            "description": brief.get('executive_summary', 'Market analysis complete'),
            "color": color,
            "fields": [
                {"name": "⚔️ Debate Zone", "value": f"{debate_count} stocks - {debate_summary}", "inline": False},
                {"name": "📈 Bullish", "value": f"{bull_count} opportunities - {bull_summary}", "inline": True},
                {"name": "📉 Bearish", "value": f"{bear_count} warnings - {bear_summary}", "inline": True},
                {"name": "🚨 Risk Alerts", "value": risk_summary, "inline": True},
                {"name": "📊 Stocks Analyzed", "value": str(total_stocks), "inline": True},
            ],
            "footer": {
                "text": "AI Studio Market Intelligence Desk | Autonomous Situation #1"
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        # Add "What Changed" if available
        changes = brief.get('changes_from_yesterday', {})
        if changes and not changes.get('is_first_run'):
            changes_msg = changes.get('message', 'Tracking changes')
            embed['fields'].insert(0, {
                "name": "📝 What Changed",
                "value": changes_msg[:1024],  # Discord field limit
                "inline": False
            })

        return self._send_message(self.CHANNEL_STOCK_ALERTS, "", embed=embed)

    # ==================== Session 461/477: Blockchain Audit Methods ====================

    def send_blockchain_alert(self, alert) -> bool:
        """
        Send a blockchain security alert to Discord (Session 461/477).

        Args:
            alert: BlockchainSecurityAlert model object OR dict with alert data

        Returns:
            True if notification sent successfully
        """
        # Handle both model objects and dicts
        if hasattr(alert, 'severity'):
            # It's a model object (BlockchainSecurityAlert)
            severity = alert.severity.upper() if alert.severity else 'MEDIUM'
            alert_type = alert.alert_type or 'unknown'
            title = alert.title or 'Security Alert'
            summary = alert.summary or ''
            address = alert.address or ''
            token_symbol = alert.token_symbol or ''
            chain = alert.chain or 'ethereum'
            value_usd = float(alert.value_usd) if alert.value_usd else 0
            detecting_agent = alert.detecting_agent or 'Unknown'
            confidence = float(alert.confidence_score) if alert.confidence_score else 0.5
            recommended_action = alert.recommended_action or ''
            risk_score = alert.risk_score or 50
            tx_hash = alert.transaction_hash or ''
        else:
            # It's a dict
            severity = alert.get('severity', 'MEDIUM').upper()
            alert_type = alert.get('type', alert.get('alert_type', 'unknown'))
            title = alert.get('title', 'Security Alert')
            summary = alert.get('description', alert.get('summary', ''))
            address = alert.get('address', '')
            token_symbol = alert.get('token_symbol', '')
            chain = alert.get('chain', 'ethereum')
            value_usd = alert.get('estimated_impact_usd', alert.get('value_usd', 0)) or 0
            detecting_agent = alert.get('detecting_agent', 'Unknown')
            confidence = alert.get('confidence', alert.get('confidence_score', 0.5))
            recommended_action = alert.get('recommended_action', '')
            risk_score = alert.get('risk_score', 50)
            tx_hash = alert.get('transaction_hash', '')

        # Determine color and emoji based on severity
        severity_config = {
            'CRITICAL': {'color': 0xFF0000, 'emoji': '🚨'},  # Red
            'HIGH': {'color': 0xFFA500, 'emoji': '⚠️'},      # Orange
            'MEDIUM': {'color': 0xFFD700, 'emoji': '📊'},    # Gold
            'LOW': {'color': 0x3498DB, 'emoji': 'ℹ️'},       # Blue
        }
        config = severity_config.get(severity, severity_config['MEDIUM'])

        # Alert type emojis
        type_emojis = {
            'whale_movement': '🐋',
            'price_manipulation': '📉',
            'unusual_volume': '📊',
            'contract_exploit': '💥',
            'flash_loan': '⚡',
            'rug_pull': '🏃',
            'suspicious_tx': '🔍',
            'governance_attack': '🏛️',
        }
        type_emoji = type_emojis.get(alert_type, '🔗')

        embed = {
            "title": f"{config['emoji']} {type_emoji} {title[:150]}",
            "description": summary[:2000] if summary else "Blockchain security alert triggered",
            "color": config['color'],
            "author": {
                "name": f"🔗 Blockchain Security Monitor - {severity}"
            },
            "fields": [
                {"name": "🎯 Severity", "value": severity, "inline": True},
                {"name": "📋 Type", "value": alert_type.replace('_', ' ').title(), "inline": True},
                {"name": "⛓️ Chain", "value": chain.title(), "inline": True},
            ],
            "footer": {
                "text": f"AI Studio Blockchain Audit • Detected by {detecting_agent}"
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        # Add token/address info
        if token_symbol:
            embed["fields"].append({"name": "🪙 Token", "value": token_symbol.upper(), "inline": True})

        if address:
            short_addr = f"`{address[:10]}...{address[-6:]}`" if len(address) > 16 else f"`{address}`"
            embed["fields"].append({"name": "📍 Address", "value": short_addr, "inline": True})

        # Add value if significant
        if value_usd and value_usd > 0:
            embed["fields"].append({"name": "💰 Value", "value": f"${value_usd:,.2f}", "inline": True})

        # Add risk score
        risk_emoji = "🔴" if risk_score >= 75 else "🟠" if risk_score >= 50 else "🟡" if risk_score >= 25 else "🟢"
        embed["fields"].append({"name": f"{risk_emoji} Risk Score", "value": f"{risk_score}/100", "inline": True})

        # Add confidence
        embed["fields"].append({"name": "📊 Confidence", "value": f"{confidence:.0%}", "inline": True})

        # Add recommended action
        if recommended_action:
            embed["fields"].append({
                "name": "💡 Recommended Action",
                "value": recommended_action[:500],
                "inline": False
            })

        # Add transaction hash if available
        if tx_hash:
            etherscan_link = f"https://etherscan.io/tx/{tx_hash}"
            embed["fields"].append({
                "name": "🔗 Transaction",
                "value": f"[View on Etherscan]({etherscan_link})",
                "inline": False
            })

        return self._send_message(self.CHANNEL_BLOCKCHAIN_ALERTS, "", embed=embed)

    def send_whale_alert(self, alert: dict) -> bool:
        """
        Send a whale movement alert to Discord (Session 461).

        Args:
            alert: Whale alert dict with token, amount, addresses, etc.

        Returns:
            True if notification sent successfully
        """
        severity = alert.get('severity', 'MEDIUM')
        market_impact = alert.get('market_impact', 'UNKNOWN')

        # Determine color based on market impact
        impact_colors = {
            'BULLISH': 0x2ECC71,   # Green
            'BEARISH': 0xFF6B6B,   # Red
            'NEUTRAL': 0x95A5A6,   # Gray
            'UNKNOWN': 0x3498DB,   # Blue
        }
        color = impact_colors.get(market_impact, 0x3498DB)

        # Format amount
        amount = alert.get('amount', 0)
        token = alert.get('token', 'ETH')
        usd_value = alert.get('usd_value', 0)

        embed = {
            "title": f"🐋 WHALE ALERT: {amount:,.2f} {token}",
            "description": f"Large {alert.get('subtype', 'transfer')} detected",
            "color": color,
            "fields": [
                {"name": "Amount", "value": f"{amount:,.2f} {token}", "inline": True},
                {"name": "USD Value", "value": f"${usd_value:,.0f}", "inline": True},
                {"name": "Market Impact", "value": market_impact, "inline": True},
            ],
            "footer": {
                "text": f"AI Studio Whale Watcher • {alert.get('timestamp', '')}"
            }
        }

        if alert.get('from_address'):
            from_addr = alert['from_address']
            embed["fields"].append({
                "name": "From",
                "value": f"`{from_addr[:10]}...{from_addr[-6:]}`",
                "inline": True
            })

        if alert.get('to_address'):
            to_addr = alert['to_address']
            embed["fields"].append({
                "name": "To",
                "value": f"`{to_addr[:10]}...{to_addr[-6:]}`",
                "inline": True
            })

        return self._send_message(self.CHANNEL_BLOCKCHAIN_ALERTS, "", embed=embed)

    def send_exploit_alert(self, alert: dict) -> bool:
        """
        Send an exploit detection alert to Discord (Session 461).

        Args:
            alert: Exploit alert dict with exploit_type, status, target_protocol, etc.

        Returns:
            True if notification sent successfully
        """
        severity = alert.get('severity', 'HIGH')
        status = alert.get('status', 'SUSPECTED')

        # Status emojis
        status_emoji = {
            'ACTIVE': '🔴',
            'COMPLETED': '⚫',
            'SUSPECTED': '🟡',
            'PREVENTED': '🟢',
        }
        emoji = status_emoji.get(status, '🟡')

        # Severity colors
        severity_colors = {
            'CRITICAL': 0xFF0000,
            'HIGH': 0xFFA500,
            'MEDIUM': 0xFFD700,
            'LOW': 0x3498DB,
        }
        color = severity_colors.get(severity, 0xFFA500)

        embed = {
            "title": f"{emoji} EXPLOIT DETECTED: {alert.get('exploit_type', 'Unknown')}",
            "description": f"Target: **{alert.get('target_protocol', 'Unknown Protocol')}**",
            "color": color,
            "fields": [
                {"name": "Severity", "value": severity, "inline": True},
                {"name": "Status", "value": status, "inline": True},
                {"name": "Exploit Type", "value": alert.get('exploit_type', 'Unknown'), "inline": True},
            ],
            "footer": {
                "text": f"AI Studio Exploit Detector • {alert.get('timestamp', '')}"
            }
        }

        if alert.get('estimated_loss_usd'):
            embed["fields"].append({
                "name": "Est. Loss",
                "value": f"${alert['estimated_loss_usd']:,.0f}",
                "inline": True
            })

        if alert.get('attacker_addresses'):
            addresses = alert['attacker_addresses'][:3]
            addr_text = "\n".join([f"`{a[:10]}...{a[-6:]}`" for a in addresses])
            embed["fields"].append({
                "name": "Attacker Addresses",
                "value": addr_text,
                "inline": False
            })

        if alert.get('recommended_actions'):
            actions = alert['recommended_actions'][:4]
            embed["fields"].append({
                "name": "Recommended Actions",
                "value": "\n".join([f"• {a}" for a in actions]),
                "inline": False
            })

        return self._send_message(self.CHANNEL_BLOCKCHAIN_ALERTS, "", embed=embed)

    def _upload_file(self, channel_id: str, file_path: str, filename: str,
                     content: str = "", embed: Optional[dict] = None) -> bool:
        """
        Upload a file to a Discord channel.

        Args:
            channel_id: Discord channel ID
            file_path: Path to the file to upload
            filename: Name for the uploaded file
            content: Optional message content
            embed: Optional embed object

        Returns:
            True if upload successful, False otherwise
        """
        if not self.enabled:
            logger.debug(f"Discord disabled, would upload {filename} to {channel_id}")
            return False

        url = f"{self.API_BASE}/channels/{channel_id}/messages"

        try:
            with open(file_path, 'rb') as f:
                files = {
                    'file': (filename, f, 'audio/mpeg')
                }
                data = {}
                if content:
                    data['content'] = content[:2000]
                if embed:
                    import json
                    data['payload_json'] = json.dumps({"embeds": [embed]})

                # Use different headers for file upload (no Content-Type)
                headers = {"Authorization": f"Bot {self.bot_token}"}

                response = requests.post(url, headers=headers, data=data, files=files, timeout=120)

                if response.status_code == 200:
                    logger.info(f"Discord file uploaded to channel {channel_id}: {filename}")
                    return True
                else:
                    logger.error(f"Discord file upload error {response.status_code}: {response.text}")
                    return False

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return False
        except requests.exceptions.Timeout:
            logger.error("Discord file upload timeout")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Discord file upload failed: {e}")
            return False

    def send_betting_digest(self, title: str, prediction_markets: List[dict] = None,
                             sports_events: List[dict] = None, tossups: List[dict] = None,
                             heavy_favorites: List[dict] = None, high_volume: List[dict] = None) -> bool:
        """
        Send a betting/prediction markets digest to #boardroom (Session 558).

        Args:
            title: Digest title
            prediction_markets: List of prediction market dicts
            sports_events: List of sports events with odds
            tossups: List of close/uncertain events
            heavy_favorites: List of events with heavy favorites
            high_volume: List of high-volume markets

        Returns:
            True if notification sent successfully
        """
        sections = []

        # High volume prediction markets
        if high_volume:
            sections.append("**📈 High Volume Markets**")
            for m in high_volume[:3]:
                ticker = m.get('ticker', m.get('title', 'Unknown'))[:30]
                volume = m.get('volume_24h', m.get('volume', 0))
                yes_price = m.get('yes_price', m.get('last_price', 0))
                sections.append(f"• {ticker}: {yes_price}¢ | Vol: ${volume:,.0f}")
            sections.append("")

        # Toss-ups (close games/markets)
        if tossups:
            sections.append("**🎲 Toss-Ups (50/50 Bets)**")
            for t in tossups[:5]:
                name = t.get('name', t.get('title', 'Unknown'))[:40]
                odds = t.get('odds', t.get('implied_probability', 50))
                sections.append(f"• {name}: ~{odds}%")
            sections.append("")

        # Heavy favorites
        if heavy_favorites:
            sections.append("**🏆 Heavy Favorites**")
            for f in heavy_favorites[:3]:
                name = f.get('name', f.get('title', 'Unknown'))[:40]
                odds = f.get('odds', f.get('implied_probability', 0))
                sections.append(f"• {name}: {odds}%")
            sections.append("")

        # Sports events
        if sports_events:
            sections.append("**🏈 Today's Sports**")
            for e in sports_events[:5]:
                home = e.get('home_team', 'Home')[:15]
                away = e.get('away_team', 'Away')[:15]
                sport = e.get('sport', 'Sports')[:10]
                sections.append(f"• [{sport}] {away} @ {home}")
            sections.append("")

        # Summary stats
        pm_count = len(prediction_markets) if prediction_markets else 0
        se_count = len(sports_events) if sports_events else 0
        tossup_count = len(tossups) if tossups else 0

        description = "\n".join(sections) if sections else "No betting data available."

        embed = {
            "title": f"🎰 {title}",
            "description": description[:4000],
            "color": 0x9B59B6,  # Purple
            "fields": [
                {"name": "📊 Prediction Markets", "value": str(pm_count), "inline": True},
                {"name": "🏈 Sports Events", "value": str(se_count), "inline": True},
                {"name": "🎲 Toss-Ups", "value": str(tossup_count), "inline": True},
            ],
            "footer": {
                "text": "AI Studio Betting Intelligence | Session 558"
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        return self._send_message(self.CHANNEL_BOARDROOM, "", embed=embed)

    def send_podcast(self, episode_id: str, topic: str, duration_seconds: int,
                     audio_file_path: str, segment_count: int = 0,
                     speakers: List[str] = None, audio_url: str = None) -> bool:
        """
        Send a completed podcast episode to #podcast-library.

        Args:
            episode_id: UUID of the podcast episode
            topic: Episode topic
            duration_seconds: Total audio duration
            audio_file_path: Path to the audio file
            segment_count: Number of speaker segments
            speakers: List of speaker names
            audio_url: Optional URL if file is too large to upload

        Returns:
            True if posted successfully, False otherwise
        """
        speakers = speakers or ["Host", "Advocate", "Skeptic", "Analyst"]

        # Format duration
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        duration_str = f"{minutes}:{seconds:02d}"

        # Check file size - Discord limit is 8MB for non-boosted servers
        file_size_mb = 0
        try:
            file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
        except Exception as _e:
            logger.warning(
                "discord_notifications.send_podcast: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        # Create embed
        embed = {
            "title": f"🎙️ {topic}",
            "description": f"A new AI podcast debate is ready to listen!",
            "color": 0x1DB954,  # Spotify green
            "fields": [
                {"name": "⏱️ Duration", "value": duration_str, "inline": True},
                {"name": "🎤 Segments", "value": str(segment_count), "inline": True},
                {"name": "🗣️ Voices", "value": ", ".join(speakers), "inline": False}
            ],
            "footer": {
                "text": f"AI Podcast Studio • Episode {episode_id[:8]}"
            }
        }

        # If file is too large, post embed with link instead of uploading
        if file_size_mb > 8:
            # Add download link to embed
            if audio_url:
                embed["fields"].append({
                    "name": "🔗 Listen",
                    "value": f"[Download MP3]({audio_url}) ({file_size_mb:.1f} MB)",
                    "inline": False
                })
            else:
                embed["fields"].append({
                    "name": "📁 File Size",
                    "value": f"{file_size_mb:.1f} MB (too large for Discord upload)",
                    "inline": False
                })

            logger.info(f"Podcast file too large ({file_size_mb:.1f}MB), posting embed only")
            return self._send_message(self.CHANNEL_PODCAST_LIBRARY, "", embed=embed)

        # Upload audio file with embed
        filename = f"podcast_{episode_id[:8]}.mp3"
        return self._upload_file(
            self.CHANNEL_PODCAST_LIBRARY,
            audio_file_path,
            filename,
            content="",
            embed=embed
        )


# Singleton instance for easy imports
discord_notify = DiscordNotificationService()


# Convenience functions for direct use
def send_dream_notification(agent_name: str, dream_title: str, dream_content: str,
                            dream_type: str = "creative", vividness: float = 0.0) -> bool:
    """Send a dream notification to Discord."""
    return discord_notify.send_dream(agent_name, dream_title, dream_content, dream_type, vividness)


def send_conversation_notification(participants: List[str], topic: str,
                                   synthesis: str, mode: str = "conversation") -> bool:
    """Send a conversation notification to Discord."""
    return discord_notify.send_conversation(participants, topic, synthesis, mode)


def send_knowledge_notification(agent_name: str, title: str, summary: str,
                                knowledge_type: str = "insight", confidence: float = 0.0) -> bool:
    """Send a knowledge notification to Discord."""
    return discord_notify.send_knowledge(agent_name, title, summary, knowledge_type, confidence)


def send_status_notification(title: str, message: str, status_type: str = "info") -> bool:
    """Send a status notification to Discord."""
    return discord_notify.send_status(title, message, status_type)


def send_boardroom_notification(title: str, decision: str, participants: List[str],
                                decision_type: str = "policy", impact: str = "medium") -> bool:
    """Send a boardroom decision notification to Discord."""
    return discord_notify.send_boardroom_decision(title, decision, participants, decision_type, impact)


def send_spider_activity_notification(spider_name: str, records_collected: int,
                                       topics: List[str] = None, duration_seconds: float = 0,
                                       source_url: str = "", status: str = "success") -> bool:
    """Send a spider activity notification to Discord (Session 423)."""
    return discord_notify.send_spider_activity(spider_name, records_collected, topics,
                                                duration_seconds, source_url, status)


def send_spider_error_notification(spider_name: str, error_message: str,
                                    source_url: str = "") -> bool:
    """Send a spider error notification to Discord (Session 423)."""
    return discord_notify.send_spider_error(spider_name, error_message, source_url)


def send_spider_summary_notification(total_spiders: int, successful: int, failed: int,
                                      total_records: int, top_topics: List[str] = None,
                                      duration_seconds: float = 0) -> bool:
    """Send a spider batch summary notification to Discord (Session 423)."""
    return discord_notify.send_spider_summary(total_spiders, successful, failed,
                                               total_records, top_topics, duration_seconds)


def send_opportunity_notification(title: str, score: float, category: str,
                                   potential: str = "", source: str = "",
                                   description: str = "", urgency: str = "normal") -> bool:
    """Send a high-value opportunity notification to Discord (Session 424)."""
    return discord_notify.send_opportunity(title, score, category, potential,
                                            source, description, urgency)


def send_opportunity_summary_notification(total_found: int, high_value_count: int,
                                           top_categories: List[str] = None,
                                           avg_score: float = 0.0) -> bool:
    """Send an opportunity scan summary notification to Discord (Session 424)."""
    return discord_notify.send_opportunity_summary(total_found, high_value_count,
                                                    top_categories, avg_score)


def send_weekly_opportunity_digest_notification(period_start: str, period_end: str,
                                                 total_opportunities: int, high_value_count: int,
                                                 tasks_created: int, tasks_won: int, tasks_lost: int,
                                                 total_revenue: float, win_rate: float,
                                                 top_opportunities: list = None,
                                                 by_category: dict = None) -> bool:
    """Send a weekly opportunity digest to Discord #boardroom (Session 425)."""
    return discord_notify.send_weekly_opportunity_digest(
        period_start, period_end, total_opportunities, high_value_count,
        tasks_created, tasks_won, tasks_lost, total_revenue, win_rate,
        top_opportunities, by_category
    )


# ==================== Session 461: Blockchain Audit Notifications ====================

def send_blockchain_alert_notification(alert: dict) -> bool:
    """Send blockchain security alert to Discord."""
    return discord_notify.send_blockchain_alert(alert)


def send_whale_alert_notification(alert: dict) -> bool:
    """Send whale movement alert to Discord."""
    return discord_notify.send_whale_alert(alert)


def send_exploit_alert_notification(alert: dict) -> bool:
    """Send exploit detection alert to Discord."""
    return discord_notify.send_exploit_alert(alert)


def send_to_channel(channel_name: str, message: str) -> bool:
    """Send a plain-text message to a Discord channel by name."""
    return discord_notify.send_to_channel(channel_name, message)
