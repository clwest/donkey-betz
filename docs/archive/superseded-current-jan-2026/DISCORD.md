<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** Discord bot snapshot
>
> **Where to look now:**
> - [docs/DISCORD_INTEGRATION.md](/docs/DISCORD_INTEGRATION.md)
> - [docs/DISCORD_COMMANDS.md](/docs/DISCORD_COMMANDS.md)
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# Discord Integration Documentation

**Total Commands:** 112
**Command Cogs:** 29
**Location:** `core/services/discord_bot.py`
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Setup](#setup)
3. [Command Categories](#command-categories)
4. [Complete Command List](#complete-command-list)
5. [Notification Channels](#notification-channels)
6. [Server Templates](#server-templates)

---

## Overview

The Discord bot provides full access to the AI Studio platform via slash commands, voice interaction, and automated notifications.

### Features
- 112 slash commands across 29 categories
- Voice AI (Whisper → GPT → TTS)
- Voice cloning marketplace
- Client management
- Real-time notifications
- Cross-platform session sync

### Bot Architecture
```
Discord.py Bot
     │
     ├── Slash Commands (112)
     │   └── 29 Cogs (command groups)
     │
     ├── Voice Features
     │   ├── Voice channel join/leave
     │   ├── Whisper transcription
     │   └── TTS responses
     │
     ├── Notifications
     │   ├── #agent-dreams
     │   ├── #agent-conversations
     │   ├── #agent-learning
     │   ├── #boardroom
     │   └── #system-status
     │
     └── Events
         ├── on_ready
         ├── on_message
         └── on_voice_state_update
```

---

## Setup

### Environment Variables
```bash
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_CLIENT_ID=your-client-id
DISCORD_CLIENT_SECRET=your-client-secret
```

### Invite Bot to Server
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot%20applications.commands
```

### Start Bot
```bash
# Starts automatically with Django
make start

# Or manually
python manage.py run_discord_bot
```

---

## Command Categories

### Status Commands (1)

| Command | Description |
|---------|-------------|
| `/status` | Check system health and status |

### Agent Commands (2)

| Command | Description |
|---------|-------------|
| `/agents` | List active agents with stats |
| `/agent <name>` | Get details for a specific agent |

### Spider Commands (10)

| Command | Description |
|---------|-------------|
| `/trending` | Get trending topics from spider data |
| `/spiders` | List spider network stats |
| `/predictions` | View prediction market signals (Kalshi) |
| `/odds` | View sports betting odds |
| `/arb` | Scan for arbitrage opportunities |
| `/bankroll` | View betting bankroll and stats |
| `/bet` | Log a new bet |
| `/resolve` | Resolve a pending bet |
| `/futures` | View championship futures odds |
| `/slip` | Generate a bet slip |

### Interactive Commands (7)

| Command | Description |
|---------|-------------|
| `/ask <question>` | Ask the Personal Assistant |
| `/create <prompt>` | Generate an image with AI |
| `/research <topic>` | Search spider data |
| `/clear` | Clear conversation history |
| `/sessions` | View/manage conversation sessions |
| `/link` | Link Discord to web account |
| `/unlink` | Unlink Discord from web account |

### Content Commands (11)

| Command | Description |
|---------|-------------|
| `/gallery` | View recent AI-generated images |
| `/profile` | View AI Studio profile and stats |
| `/opportunities` | View matching income opportunities |
| `/apply <id>` | Apply to an opportunity |
| `/track` | Track job applications |
| `/digest` | Get daily/weekly activity digest |
| `/alerts` | Manage opportunity alerts |
| `/subscribe` | Subscribe to Pro/Premium |
| `/tier` | View subscription tier and usage |
| `/cancel` | Cancel subscription |
| `/billing` | Access billing portal |

### Voice Commands (3)

| Command | Description |
|---------|-------------|
| `/voice` | Join voice channel for interaction |
| `/speak <message>` | Make bot speak in voice channel |
| `/ask-voice <question>` | Ask AI and hear response |

### Voice Marketplace Commands (3)

| Command | Description |
|---------|-------------|
| `/voice-market` | Browse and manage AI voices |
| `/voice-buy` | Purchase voice credits |
| `/voice-clone` | Clone your voice |

### Content Pipeline Commands (3)

| Command | Description |
|---------|-------------|
| `/create-content` | Create complete content packages |
| `/content-status` | Check package status |
| `/showroom` | Browse content marketplace |

### Series Commands (4)

| Command | Description |
|---------|-------------|
| `/series-create` | Create multi-episode series |
| `/series-status` | Check series status |
| `/series-list` | List your series |
| `/series-view` | View episode content |

### Studio Commands (7)

| Command | Description |
|---------|-------------|
| `/studio-create` | Create autonomous content channel |
| `/studio-list` | List content channels |
| `/studio-status` | Check channel status |
| `/studio-pause` | Pause content generation |
| `/studio-resume` | Resume content generation |
| `/studio-performance` | View channel analytics |
| `/studio-episode` | View episode content |

### Gumroad Commands (2)

| Command | Description |
|---------|-------------|
| `/publish-gumroad` | Publish image to Gumroad |
| `/gumroad-status` | Check Gumroad connection |

### Pipeline Learning Commands (4)

| Command | Description |
|---------|-------------|
| `/rate-series` | Rate series/episode |
| `/learning-stats` | View learning statistics |
| `/style-recommend` | Get style recommendations |
| `/style-leaderboard` | View top styles |

### Server Setup Commands (1)

| Command | Description |
|---------|-------------|
| `/setup` | Set up AI Studio channels |

### Client Commands (4)

| Command | Description |
|---------|-------------|
| `/client-add` | Create new client |
| `/client-list` | List all clients |
| `/client-deliver` | Send deliverable to client |
| `/client-invite` | Generate client invite |

### Agent Access Commands (2)

| Command | Description |
|---------|-------------|
| `/agent-list` | List agents by category |
| `/agent-task` | Execute task with specific agent |

### Resolve Commands (6)

| Command | Description |
|---------|-------------|
| `/videos-list` | List available videos |
| `/resolve-render` | Start professional render |
| `/color-grade` | Apply color grading |
| `/render-status` | Check render status |
| `/render-download` | Download rendered video |
| `/trending-grades` | View trend-matched grades |

### Podcast Commands (4)

| Command | Description |
|---------|-------------|
| `/podcast-create` | Create new podcast show |
| `/podcast-episode` | Generate episode |
| `/podcast-list` | List shows |
| `/podcast-status` | Check episode status |

### Narrative Commands (4)

| Command | Description |
|---------|-------------|
| `/narratives` | List tracked narratives |
| `/narrative-status` | Check narrative status |
| `/narrative-shifts` | View recent shifts |
| `/narrative-alerts` | Manage narrative alerts |

### Situation Commands (4)

| Command | Description |
|---------|-------------|
| `/situations` | List autonomous situations |
| `/situation-status` | Check situation status |
| `/situation-run` | Manually run situation |
| `/situation-alerts` | View situation alerts |

### Developer Commands (2)

| Command | Description |
|---------|-------------|
| `/code-generate` | Generate code with AI |
| `/code-review` | Review code |

### Legal Commands (3)

| Command | Description |
|---------|-------------|
| `/legal-upload` | Upload legal document |
| `/legal-analyze` | Analyze document |
| `/legal-draft` | Draft legal document |

### Review Commands (5)

| Command | Description |
|---------|-------------|
| `/review-decision` | Review boardroom decision |
| `/review-promote` | Promote decision |
| `/review-reject` | Reject decision |
| `/review-list` | List pending reviews |
| `/review-stats` | View review statistics |

---

## Complete Command List (112)

```
# Status (1)
/status

# Agents (2)
/agents, /agent

# Spiders (10)
/trending, /spiders, /predictions, /odds, /arb
/bankroll, /bet, /resolve, /futures, /slip

# Interactive (7)
/ask, /create, /research, /clear, /sessions, /link, /unlink

# Content (11)
/gallery, /profile, /opportunities, /apply, /track
/digest, /alerts, /subscribe, /tier, /cancel, /billing

# Voice (3)
/voice, /speak, /ask-voice

# Voice Marketplace (3)
/voice-market, /voice-buy, /voice-clone

# Content Pipeline (3)
/create-content, /content-status, /showroom

# Series (4)
/series-create, /series-status, /series-list, /series-view

# Studio (7)
/studio-create, /studio-list, /studio-status
/studio-pause, /studio-resume, /studio-performance, /studio-episode

# Gumroad (2)
/publish-gumroad, /gumroad-status

# Pipeline Learning (4)
/rate-series, /learning-stats, /style-recommend, /style-leaderboard

# Server Setup (1)
/setup

# Clients (4)
/client-add, /client-list, /client-deliver, /client-invite

# Agent Access (2)
/agent-list, /agent-task

# Resolve (6)
/videos-list, /resolve-render, /color-grade
/render-status, /render-download, /trending-grades

# Podcasts (4)
/podcast-create, /podcast-episode, /podcast-list, /podcast-status

# Narratives (4)
/narratives, /narrative-status, /narrative-shifts, /narrative-alerts

# Situations (4)
/situations, /situation-status, /situation-run, /situation-alerts

# Developer (2)
/code-generate, /code-review

# Legal (3)
/legal-upload, /legal-analyze, /legal-draft

# Review (5)
/review-decision, /review-promote, /review-reject
/review-list, /review-stats
```

---

## Notification Channels

### #agent-dreams (Purple Embeds)
Agent creative thoughts generated during idle time.

### #agent-conversations (Pink Embeds)
HiveMind sessions and multi-agent debates.

### #agent-learning (Blue Embeds)
Knowledge sharing between agents.

### #boardroom (Gold Embeds)
Strategic decisions from governance system.

### #system-status (Variable Colors)
System health, alerts, and status updates.

### #market-intelligence (Green Embeds)
Daily market briefs and alerts.

---

## Server Templates

### Solo Creator
Personal workspace for individual creators.

Channels:
- #ai-studio (main interaction)
- #gallery (generated content)
- #notifications (alerts)

### Freelancer
Individual with client management.

Channels:
- #ai-studio
- #gallery
- #clients (client channels)
- #deliverables
- #notifications

### Agency
Team + client management.

Channels:
- #ai-studio
- #team-chat
- #gallery
- #clients (client channels)
- #deliverables
- #billing
- #notifications

---

## User Linking

Link Discord account to web account for:
- Session sync across platforms
- Unified profile
- Cross-platform notifications

```
/link
# Bot sends verification code
# Enter code on web dashboard
# Accounts linked!
```

---

## Voice AI Flow

```
1. /voice - Bot joins your voice channel
2. Speak your question
3. Whisper transcribes audio
4. GPT processes question
5. ElevenLabs generates response
6. Bot speaks response in channel
```

---

## Related Documentation

- [AGENTS.md](AGENTS.md) - Agents accessible via Discord
- [AUTONOMOUS_SYSTEMS.md](AUTONOMOUS_SYSTEMS.md) - Situations with Discord alerts
- [DAVINCI_RESOLVE.md](../DAVINCI_RESOLVE.md) - Resolve commands detail