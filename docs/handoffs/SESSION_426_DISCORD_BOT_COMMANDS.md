# Session 426: Basic Discord Bot Commands

**Date:** December 11, 2025
**Status:** COMPLETE
**Previous Session:** 425 - Opportunity Pipeline Automation

---

## Summary

Implemented a Discord bot with slash commands for system monitoring and data access:
- `/status` - System health check
- `/agents` - List active agents with stats
- `/agent <name>` - Get specific agent details
- `/trending` - Get trending topics from spider data
- `/spiders` - Spider network statistics
- `/help` - Command reference

---

## New Files Created

### `core/services/discord_bot.py`
Main bot implementation using discord.py 2.6.4:

| Class | Purpose |
|-------|---------|
| `DonkeyBetzBot` | Main bot class with setup_hook and on_ready |
| `StatusCommands` | `/status` command - system health |
| `AgentCommands` | `/agents`, `/agent` commands - agent info |
| `SpiderCommands` | `/trending`, `/spiders` commands - data access |
| `HelpCommands` | `/help` command - reference |

### `core/management/commands/run_discord_bot.py`
Django management command to run the bot:
```bash
# Check token configuration
python manage.py run_discord_bot --check

# Run the bot
python manage.py run_discord_bot
```

---

## Slash Commands Reference

| Command | Description | Parameters |
|---------|-------------|------------|
| `/status` | System health check | - |
| `/agents` | List active agents | `limit` (default: 10) |
| `/agent` | Get agent details | `name` (required) |
| `/trending` | Trending spider data | `category`, `limit` |
| `/spiders` | Spider network stats | - |
| `/help` | Command reference | - |

---

## Makefile Targets

Added to `Makefile`:
```makefile
# Start Discord bot (background)
make discord-bot

# Stop Discord bot
make discord-bot-stop

# Check bot status
make discord-bot-status

# Tail bot logs
make discord-bot-logs
```

---

## Environment Requirements

```bash
# Required
export DISCORD_BOT_TOKEN='your-bot-token-here'
```

Get token from Discord Developer Portal:
1. Go to https://discord.com/developers/applications
2. Select your application
3. Go to Bot section
4. Copy the token

---

## Bot Permissions Required

Enable in Discord Developer Portal:
- `applications.commands` - For slash commands
- `bot` with these permissions:
  - Send Messages
  - Embed Links
  - Read Message History

---

## Command Output Examples

### `/status`
```
System Status
━━━━━━━━━━━━━━━━━━
Services:
  Django API   : Online
  Celery       : Active
  Redis        : Connected
  PostgreSQL   : Connected

Agents: 34
Spider Data: 12,250
Images: 500+
Dreams: 2,080
HiveMind: 117
Bot Uptime: 0:15:30
```

### `/agents`
```
Active Agents (Top 10)
━━━━━━━━━━━━━━━━━━
🎯 ResearchAgent (Lv.15)
   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ | XP: 15,000

🎨 CreativeDirectorAgent (Lv.12)
   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ | XP: 12,500
...
```

### `/trending`
```
Trending (Last 7 Days)
━━━━━━━━━━━━━━━━━━
💻 OpenAI announces GPT-5
   Source: techcrunch

💰 Bitcoin hits new ATH
   Source: coingecko

🎨 Figma releases AI features
   Source: theverge
...
```

---

## Architecture

```
Discord API
    ↓
DonkeyBetzBot (discord.py)
    ↓
Cog Commands (StatusCommands, AgentCommands, etc.)
    ↓
Django ORM (Agent, SpiderData, etc.)
    ↓
Response Embed → Discord API
```

---

## Files Modified

| File | Changes |
|------|---------|
| `Makefile` | Added discord-bot targets |
| `requirements.txt` | Added discord.py>=2.0 (implicit via pip) |

---

## Testing

```bash
# Check token is configured
python manage.py run_discord_bot --check

# Run bot in foreground (for testing)
python manage.py run_discord_bot

# Run bot in background
make discord-bot

# Check status
make discord-bot-status

# View logs
make discord-bot-logs
```

---

## Dependencies

- `discord.py>=2.0` - Discord API wrapper with slash command support
- Django models (Agent, SpiderData, AgentDream, etc.)
- DISCORD_BOT_TOKEN environment variable

---

## Next Session: 427

**Topic:** Advanced Discord Bot Commands

**Goals:**
- Implement `/ask <question>` - Query Personal Assistant
- Implement `/create <prompt>` - Trigger image generation
- Implement `/research <topic>` - Run spider search
- Add command cooldowns and rate limiting
- Add user permission levels

---

## Key Takeaways

1. **discord.py 2.x** - Uses `app_commands` for slash commands
2. **Cog Pattern** - Organized commands into logical groups
3. **Deferred Responses** - `await interaction.response.defer()` for DB queries
4. **Rich Embeds** - Visual formatting with colors, fields, timestamps
5. **Management Command** - Django integration via `run_discord_bot`
6. **Background Operation** - Makefile targets for daemon-style running
