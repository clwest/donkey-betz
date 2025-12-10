# Discord Bot Setup Guide

**Created:** Session 399 (December 2025)
**Bot Name:** Donkey Betz#7496
**Bot ID:** 1444884424339755008

---

## Current Status

- **Bot Token:** Configured in `.env` as `DISCORD_BOT_TOKEN`
- **Bot Status:** Active and valid
- **Guilds:** Needs to be invited to servers

---

## Quick Start

### 1. Invite the Bot to a Server

Click this link (requires admin permissions on the target server):

```
https://discord.com/api/oauth2/authorize?client_id=1444884424339755008&permissions=66560&scope=bot
```

**Permissions included (66560):**
- View Channels
- Read Message History

### 2. Verify Bot is Working

```bash
.venv/bin/python -c "
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from ai_core.spiders.real_data_collector import _collect_discord_data

async def test():
    result = await _collect_discord_data()
    print(f'Items collected: {len(result.get(\"items\", []))}')
    for item in result.get('items', [])[:5]:
        print(f'  - {item.get(\"title\")}')

asyncio.run(test())
"
```

---

## Environment Variables

Add to `.env`:

```bash
DISCORD_BOT_TOKEN="your_bot_token_here"
```

---

## API Reference

### Base URL
```
https://discord.com/api/v10
```

### Authentication Header
```
Authorization: Bot {DISCORD_BOT_TOKEN}
```

### Key Endpoints Used

| Endpoint | Description |
|----------|-------------|
| `GET /users/@me` | Get bot's own user info |
| `GET /users/@me/guilds` | List guilds bot is in |
| `GET /guilds/{guild_id}/channels` | List channels in a guild |
| `GET /channels/{channel_id}/messages` | Get messages from a channel |

### Rate Limits
- Global: 50 requests/second
- Per-route limits vary
- Always include 0.3s delay between requests

---

## Spider Implementation

**File:** `ai_core/spiders/real_data_collector.py`
**Function:** `_collect_discord_data()`

### What it Collects

1. **Guild Info** (servers the bot is in)
   - Guild name and ID
   - Icon URL
   - Owner status
   - Permissions

2. **Channel Info** (text channels in each guild)
   - Channel name and ID
   - Channel topic
   - Parent guild

### Data Structure

```python
{
    'items': [
        {
            'title': 'Server: My Discord Server',
            'description': 'Discord server with ID 123456789',
            'guild_id': '123456789',
            'guild_name': 'My Discord Server',
            'icon': 'https://cdn.discordapp.com/icons/...',
            'source': 'discord',
            'type': 'guild',
            'fetched_at': '2025-12-09T...'
        },
        {
            'title': '#general in My Discord Server',
            'description': 'Welcome to our server!',
            'channel_id': '987654321',
            'channel_name': 'general',
            'guild_name': 'My Discord Server',
            'source': 'discord',
            'type': 'channel',
            'fetched_at': '2025-12-09T...'
        }
    ],
    'item_count': 2,
    'source': 'discord',
    'collected_at': '2025-12-09T...'
}
```

---

## Creating a New Discord Bot

If you need to create a new bot:

### 1. Create Application
1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Name it and create

### 2. Create Bot User
1. Go to "Bot" section in left sidebar
2. Click "Add Bot"
3. Copy the token (only shown once!)

### 3. Configure Bot Settings
- **Public Bot:** Off (recommended for private use)
- **Requires OAuth2 Code Grant:** Off
- **Presence Intent:** Off (not needed)
- **Server Members Intent:** Off (not needed)
- **Message Content Intent:** On (if you want to read messages)

### 4. Generate Invite URL
1. Go to "OAuth2" > "URL Generator"
2. Select scopes: `bot`
3. Select permissions:
   - View Channels
   - Read Message History
   - (Add more as needed)
4. Copy the generated URL

---

## Extending the Spider

### Adding Message Collection

To collect actual messages (requires Message Content Intent):

```python
# Get recent messages from a channel
messages_url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit=50"
async with session.get(messages_url, headers=headers) as response:
    if response.status == 200:
        messages = await response.json()
        for msg in messages:
            item = {
                'title': f"Message from {msg.get('author', {}).get('username')}",
                'description': msg.get('content', '')[:500],
                'message_id': msg.get('id'),
                'author': msg.get('author', {}).get('username'),
                'timestamp': msg.get('timestamp'),
                'source': 'discord',
                'type': 'message'
            }
```

### Adding Webhook Support

For real-time updates, create a webhook:

```python
# Create webhook in a channel (requires MANAGE_WEBHOOKS permission)
webhook_url = f"https://discord.com/api/v10/channels/{channel_id}/webhooks"
payload = {'name': 'Spider Alerts'}
async with session.post(webhook_url, headers=headers, json=payload) as response:
    webhook = await response.json()
    # Save webhook.url for sending messages
```

---

## Troubleshooting

### "Invalid bot token"
- Check token is correctly copied to `.env`
- Ensure no extra spaces or quotes
- Token may have been regenerated - get new one from Discord Developer Portal

### "Bot is in 0 guilds"
- Bot needs to be invited to at least one server
- Use the invite URL above
- You need admin permissions on the target server

### "Missing Access" errors
- Bot doesn't have permission to view that channel
- Check bot's role permissions in the server
- Some channels may be restricted

### Rate Limited
- Add delays between requests: `await asyncio.sleep(0.5)`
- Check response headers for `X-RateLimit-*` values
- Implement exponential backoff for 429 responses

---

## Related Files

- **Spider Handler:** `ai_core/spiders/real_data_collector.py` (`_collect_discord_data`)
- **Spider Registry:** `ai_core/spiders/spider_registry.py`
- **Environment:** `.env` (`DISCORD_BOT_TOKEN`)
