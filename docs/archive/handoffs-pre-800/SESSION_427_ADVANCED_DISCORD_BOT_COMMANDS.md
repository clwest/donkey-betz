# Session 427: Advanced Discord Bot Commands

**Date:** December 11, 2025
**Status:** COMPLETE

---

## Summary

Extended the Discord bot with interactive commands that allow users to query AI agents, generate images, and search spider data directly from Discord. Fixed multiple bugs to get all commands working properly.

---

## New Commands

| Command | Description | Cooldown |
|---------|-------------|----------|
| `/ask <question>` | Query Personal Assistant | 10s |
| `/create <prompt>` | Generate image via ImageAgent | 30s |
| `/research <topic> [limit]` | Search spider semantic search | 15s |

---

## Features Implemented

### 1. Interactive Commands (InteractiveCommands Cog)

**`/ask <question>`**
- Queries the PersonalAssistantAgent
- Uses sync_to_async for Django ORM compatibility
- Extracts delegated agent results for better responses
- Truncates responses over 3800 chars (Discord embed limit)
- Returns green embed on success, red on error
- Shows which agent handled the request in footer

**`/create <prompt>`**
- Triggers ImageAgent for image generation
- **Uploads images directly to Discord** (not URLs)
- Uses `discord.File` with `attachment://` embed syntax
- Purple embed for results
- Shows image count in result field

**`/research <topic> [limit]`**
- Uses SpiderSemanticSearch for semantic search
- Returns up to 10 results (capped)
- Clickable links to source articles
- Shows similarity score per result
- Teal embed with results

### 2. Rate Limiting System

```python
class RateLimiter:
    _cooldown_times = {
        'ask': 10,       # 10 seconds
        'create': 30,    # 30 seconds (expensive operation)
        'research': 15,  # 15 seconds
        'default': 3,    # Default for other commands
    }
```

- Per-user, per-command tracking
- Ephemeral error messages for rate limits
- Shows remaining wait time

### 3. Permission Levels

```python
class PermissionLevel:
    ADMIN_USER_IDS = {264555101581082624}  # Owner
    TRUSTED_USER_IDS = set()  # Add trusted users here
```

**Permission Tiers:**
- **Admin (0x multiplier):** No cooldown at all
- **Trusted (0.5x multiplier):** Half cooldown
- **Normal (1.0x multiplier):** Full cooldown

---

## Bugs Fixed This Session

| Issue | Root Cause | Fix |
|-------|------------|-----|
| `/trending` field error | SpiderData uses `created_at` not `crawled_at` | Changed field name, extract from `raw_data['items']` |
| `/ask` not appearing | Global sync takes up to 1 hour | Added `copy_global_to(guild=guild)` for instant sync |
| `/ask` AttributeError | AgentResult uses `message` not `response` | Changed to `result.message` |
| `/create` no image | Images use `image_url` not `url` field | Changed to `first_image.get('image_url')` |
| `/create` image not visible | localhost URLs don't work in Discord | Implemented `discord.File` upload |
| `/research` wrong method | Method is `semantic_search` not `search` | Fixed method name |
| `/research` wrong param | Parameter is `limit` not `top_k` | Fixed parameter name |
| `/research` attribute error | SemanticSearchResult is dataclass | Use `item.title` not `item.get('title')` |

---

## Files Modified

| File | Changes |
|------|---------|
| `core/services/discord_bot.py` | Added InteractiveCommands cog, RateLimiter, PermissionLevel, fixed all bugs |

---

## Command Count

**Total Slash Commands: 9**
- Session 426: `/status`, `/agents`, `/agent`, `/trending`, `/spiders`, `/help`
- Session 427: `/ask`, `/create`, `/research`

---

## Updated Help Command

The `/help` command now shows:

```
Interactive
  /ask <question> - Ask the Personal Assistant
  /create <prompt> - Generate an image
  /research <topic> [limit] - Search spider data

System
  /status - System health check
  /spiders - Spider network stats

Agents
  /agents [limit] - List active agents
  /agent <name> - Get agent details

Data
  /trending [category] [limit] - Trending topics

Help
  /help - This command
```

---

## Technical Notes

### sync_to_async Pattern
All Django ORM calls wrapped in `@sync_to_async` decorated functions:

```python
@sync_to_async
def query_assistant(q: str) -> Dict[str, Any]:
    from core.agents.personal_assistant_agent import PersonalAssistantAgent
    agent = PersonalAssistantAgent()
    result = agent.execute(task=q, context={...}, ...)
    return {'success': result.success, 'message': result.message}

result = await query_assistant(question)
```

### Discord File Upload Pattern
For displaying generated images in Discord:

```python
# Get image path from ImageAgent result
image_url = first_image.get('image_url')  # e.g., /media/generated_images/...
local_file_path = os.path.join(settings.BASE_DIR, image_url.lstrip('/'))

# Create Discord File and attach to embed
file_to_send = discord.File(local_file_path, filename=filename)
embed.set_image(url=f"attachment://{filename}")
await interaction.followup.send(embed=embed, file=file_to_send)
```

### SemanticSearchResult Dataclass
Results from `SpiderSemanticSearch.semantic_search()` are dataclass objects:

```python
# Correct - attribute access
title = item.title
url = item.url
source = item.source
score = item.similarity

# Wrong - dict access
title = item.get('title')  # AttributeError!
```

### Discord Embed Limits
- Description: 4096 chars (we use 3800 to be safe)
- Field value: 1024 chars
- Total embed: 6000 chars

---

## Next Session: 428

**Focus: PA Discord Interface**
- Add conversation history tracking per user
- Remember context across multiple /ask calls
- Add `/clear` command to reset conversation
- Consider thread-based conversations

---

## Bot Management

```bash
# Start bot
make discord-bot

# Stop bot
make discord-bot-stop

# Check status
make discord-bot-status

# View logs
make discord-bot-logs
```

---

## Discord Channel Reference

| Channel | Purpose |
|---------|---------|
| #agent-dreams | Agent creative thoughts |
| #agent-conversations | HiveMind sessions |
| #system-status | System health + spider activity |
| #agent-learning | Knowledge sharing |
| #boardroom | Strategic decisions |
| #opportunities | High-value opportunity alerts |

---

**Session 427 COMPLETE - 3 new interactive commands with rate limiting, permission levels, and image upload!**
