#!/usr/bin/env python
"""Run the Discord bot."""
import os
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from core.services.discord_bot import run_bot

if __name__ == '__main__':
    asyncio.run(run_bot())
