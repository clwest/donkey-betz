"""
Django management command to run the Discord bot.

Session 426: Basic Discord Bot Commands

Usage:
    python manage.py run_discord_bot

Environment:
    DISCORD_BOT_TOKEN - Required bot token from Discord Developer Portal
"""

import os
import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run the Discord bot with slash commands'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            action='store_true',
            help='Check if bot token is configured without starting the bot',
        )

    def handle(self, *args, **options):
        token = os.environ.get('DISCORD_BOT_TOKEN')

        if not token:
            self.stderr.write(self.style.ERROR(
                "DISCORD_BOT_TOKEN not set!\n"
                "Set it in your environment or .env file:\n"
                "  export DISCORD_BOT_TOKEN='your-bot-token-here'"
            ))
            return

        if options['check']:
            self.stdout.write(self.style.SUCCESS(
                f"Discord bot token is configured (starts with {token[:10]}...)"
            ))
            return

        self.stdout.write(self.style.SUCCESS("Starting Discord bot..."))
        self.stdout.write("Press Ctrl+C to stop\n")

        try:
            from core.services.discord_bot import start_bot
            start_bot()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nBot stopped by user"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Bot error: {e}"))
            raise
