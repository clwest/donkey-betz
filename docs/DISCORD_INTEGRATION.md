<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md) (sole authoritative counts per `DOC_LIFECYCLE.md` §2c). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality (Session 1099 verifier).

# Discord Integration Rules & Command Reference

**Last Updated:** Session 1158 (May 25, 2026 — count corrected via DISCORD_AUDIT.md DOC-AUTOGEN)
**Commands:** **96 total** (48 `@app_commands.command` slash + 48 `@*.command` prefix) across 25 Cogs. Earlier "144 total" claim was a regex double-count corrected by AST parsing in Session 1115 — see `docs/DISCORD_AUDIT.md` (DOC-AUTOGEN by `python manage.py build_discord_audit`) for authoritative per-command detail.
**Notification Channels:** 12
**Bot File:** `core/services/discord_bot.py` (11,676 lines)
**Notifications:** `core/services/discord_notifications.py` (2,273 lines)
**Voice:** `core/services/discord_voice.py` (871 lines)

---

## What Discord IS For

1. **Notifications** -- system alerts, agent dreams, spider summaries, market/blockchain alerts
2. **Quick lookups** -- `/status`, `/ask`, `/agents`, `/trending`, `/profile`
3. **Voice features** -- TTS, speech-to-text, voice cloning, voice chat (Discord's strength)
4. **Mobile-friendly actions** -- `/bet`, `/apply`, `/digest`, `/consult`
5. **Content creation triggers** -- `/create`, `/podcast-create`, `/create-content`
6. **Account management** -- `/link`, `/unlink`, `/subscribe`, `/tier`

## What Discord is NOT For

1. **Complex workflows** -- multi-step initiative management (use web Workspace)
2. **Content review/approval** -- blog approve/publish pipeline (use web Blog Viewer)
3. **System configuration** -- LLM routing, billing details, admin (use web Admin/Settings)
4. **Deep data exploration** -- spider feed browsing, memory palace, agent analytics (use web)
5. **Dashboard views** -- anything requiring charts, tables, or rich visualization

---

## Commands by Category

### System & Status (6 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/status` | Check system health and status | ACTIVE |
| `/spiders` | List spider network stats | ACTIVE |
| `/agents` | List active agents with stats | ACTIVE |
| `/agent` | Get details for a specific agent | ACTIVE |
| `/trending` | Get trending topics from spider data | ACTIVE |
| `/help` | Show available commands | ACTIVE |

### PA & AI Core (7 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/ask` | Ask the Personal Assistant a question | ACTIVE |
| `/research` | Search spider data for a topic | ACTIVE |
| `/clear` | Clear your conversation history with the assistant | ACTIVE |
| `/sessions` | View and manage conversation sessions across platforms | ACTIVE |
| `/link` | Link Discord account to AI Studio web account | ACTIVE |
| `/unlink` | Unlink Discord account from AI Studio account | ACTIVE |
| `/profile` | View your AI Studio profile and stats | ACTIVE |

### Agents & Advisors (4 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/agent-list` | List all agents by category | ACTIVE |
| `/agent-task` | Execute a task with a specific agent | ACTIVE |
| `/advisors` | List all available advisors | ACTIVE |
| `/consult` | Consult a legendary advisor | ACTIVE |

### Voice & Audio (8 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/voice` | Join a voice channel for voice interaction | ACTIVE |
| `/speak` | Make the bot speak a message in voice channel | ACTIVE |
| `/ask-voice` | Ask AI and hear the response in voice channel | ACTIVE |
| `/voice-ask` | Ask a question and hear the AI speak the answer | ACTIVE |
| `/voice-chat` | Speak to the AI and hear a spoken response | ACTIVE |
| `/voice-market` | Browse and manage AI voices | ACTIVE |
| `/voice-buy` | Purchase voice generation credits | ACTIVE |
| `/voice-clone` | Clone your voice for the marketplace | ACTIVE |

### Content Creation & Media (7 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/create` | Generate an image with AI | ACTIVE |
| `/gallery` | View your recent AI-generated images | ACTIVE |
| `/create-content` | Create complete content packages | ACTIVE |
| `/content-status` | Check status of your content packages | ACTIVE |
| `/showroom` | Browse the content marketplace | DORMANT |
| `/publish-gumroad` | Publish an image to Gumroad for sale | ACTIVE |
| `/gumroad-status` | Check your Gumroad connection status | DORMANT |

### Series & Studio Management (11 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/series-create` | Create a multi-episode AI content series | ACTIVE |
| `/series-status` | Check status of your AI series | ACTIVE |
| `/series-list` | List your AI series | ACTIVE |
| `/series-view` | View the content of a series episode | ACTIVE |
| `/studio-create` | Create a new autonomous content channel | ACTIVE |
| `/studio-list` | List all your autonomous content channels | ACTIVE |
| `/studio-status` | Check detailed status of a content channel | ACTIVE |
| `/studio-pause` | Pause autonomous content generation for a channel | ACTIVE |
| `/studio-resume` | Resume autonomous content generation for a channel | ACTIVE |
| `/studio-performance` | View detailed analytics for a content channel | ACTIVE |
| `/studio-episode` | View episode content from a channel | ACTIVE |

### Learning & Styles (3 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/rate-series` | Rate a series or episode to improve AI generation | ACTIVE |
| `/style-recommend` | Get style recommendation for your content | ACTIVE |
| `/style-leaderboard` | View top-performing styles | ACTIVE |

### ML & Learning Stats (2 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/learning-stats` | View learning system statistics | ACTIVE |
| `/ml-scoring` | View ML opportunity scoring status | ACTIVE |

### Betting & Markets (8 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/odds` | View sports betting odds and analysis | ACTIVE |
| `/arb` | Scan for arbitrage opportunities across bookmakers | ACTIVE |
| `/predictions` | View prediction market signals from Kalshi | ACTIVE |
| `/bankroll` | View your betting bankroll and stats | ACTIVE |
| `/bet` | Log a new bet to your bankroll | ACTIVE |
| `/resolve` | Resolve a pending bet (won/lost/pushed) | ACTIVE |
| `/futures` | View championship futures odds | ACTIVE |
| `/slip` | Generate a bet slip with multiple selections | ACTIVE |

### Opportunities & Jobs (5 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/opportunities` | View matching income opportunities | ACTIVE |
| `/apply` | Apply to an opportunity | ACTIVE |
| `/track` | Track your job applications | ACTIVE |
| `/digest` | Get your daily/weekly activity digest | ACTIVE |
| `/alerts` | Manage your opportunity alerts | ACTIVE |

### Review & Decision (5 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/review` | Show review document for an artifact or dream | ACTIVE |
| `/review-list` | List pending review documents | ACTIVE |
| `/ask-pro` | Ask the Pro advocate a question | ACTIVE |
| `/ask-con` | Ask the Con skeptic a question | ACTIVE |
| `/decide` | Make a decision on a review | ACTIVE |

### Narrative Drift Monitoring (9 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/narratives` | List tracked narratives | ACTIVE |
| `/narrative-shifts` | List recent narrative shifts | ACTIVE |
| `/narrative-scan` | Run a narrative drift scan | ACTIVE |
| `/narrative-seed` | Seed narratives for a domain | ACTIVE |
| `/narrative-status` | Get Narrative Drift system status | ACTIVE |
| `/narrative-evidence` | View evidence for a specific narrative | ACTIVE |
| `/narrative-domains` | Overview of all narrative domains | ACTIVE |
| `/narrative-watch` | Watch a narrative for shift alerts | ACTIVE |
| `/narrative-trending` | Show trending/shifting narratives | ACTIVE |

### ROI & Analytics (5 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/roi-summary` | Show ROI summary metrics | ACTIVE |
| `/roi-dashboard` | Show ROI dashboard overview | ACTIVE |
| `/roi-brief` | Generate or view weekly intelligence brief | ACTIVE |
| `/roi-funnel` | Show conversion funnel metrics | ACTIVE |
| `/roi-attribution` | Show revenue attribution by source | ACTIVE |

### Blockchain & Smart Contracts (2 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/audit-contract` | Audit a smart contract by Ethereum address | ACTIVE |
| `/blockchain-status` | Check blockchain monitoring status | ACTIVE |

### Podcasts (4 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/podcast-create` | Create an AI podcast episode with agent debates | ACTIVE |
| `/podcast-list` | List your podcast episodes | ACTIVE |
| `/podcast-status` | Check status of a podcast episode | ACTIVE |
| `/podcast-script` | View the full script of a completed podcast | ACTIVE |

### Legal (3 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/legal-draft` | Draft a legal document template (Colorado family law) | ACTIVE |
| `/legal-analyze` | Analyze a denied motion and suggest fixes | ACTIVE |
| `/legal-case` | Get info about your case profile | ACTIVE |

### Code (2 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/code-generate` | Generate code from a specification | ACTIVE |
| `/code-review` | Review code for bugs, security, and quality | ACTIVE |

### Video & Rendering (6 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/resolve-render` | Start a professional DaVinci Resolve render | DORMANT |
| `/color-grade` | Apply color grading to a video | DORMANT |
| `/render-status` | Check render job status | DORMANT |
| `/render-download` | Download a completed render | DORMANT |
| `/trending-grades` | Show color grades matching current spider trends | DORMANT |
| `/videos-list` | List available videos for rendering | DORMANT |

### Autonomous Situations (4 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/situation-list` | List all 19 autonomous situations | ACTIVE |
| `/situation-status` | Check detailed status of a specific situation | ACTIVE |
| `/situation-run` | Manually trigger an autonomous situation | ACTIVE |
| `/situation-alerts` | Configure alerts for an autonomous situation | ACTIVE |

### Server Management (5 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/setup` | Set up AI Studio channels in your server | ACTIVE |
| `/client-add` | Create a new client with dedicated channel | ACTIVE |
| `/client-list` | List all your clients | ACTIVE |
| `/client-deliver` | Send a deliverable to a client's channel | ACTIVE |
| `/client-invite` | Generate an invite link for a client | ACTIVE |

### Subscriptions & Billing (4 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/subscribe` | Subscribe to Pro or Premium for more features | ACTIVE |
| `/tier` | View your subscription tier and usage | ACTIVE |
| `/cancel` | Cancel your subscription | ACTIVE |
| `/billing` | Access your billing portal | ACTIVE |

### Workflows (2 commands)

| Command | Description | Status |
|---------|-------------|--------|
| `/workflow-list` | List available workflows | ACTIVE |
| `/workflow-run` | Run a multi-step workflow | ACTIVE |

---

## Notification Channels

| Channel | ID | Purpose | Key Methods |
|---------|----|---------|-------------|
| `#agent-dreams` | 1448809858274033684 | Agent dream outputs | `send_dream()` |
| `#agent-conversations` | 1448809914783895583 | HiveMind session completions | `send_conversation()` |
| `#system-status` | 1448809955326169149 | Health updates, spider summaries | `send_status()`, `send_spider_summary()` |
| `#agent-learning` | 1448819275459465257 | Learning events | `send_knowledge()` |
| `#boardroom` | 1448819855557136595 | Decision notifications | `send_boardroom_decision()` |
| `#opportunities` | 1448867150948335777 | High-value signals, market alerts | `send_opportunity()`, `send_market_intelligence_brief()` |
| `#gallery` | 1449059813765021859 | Generated images | `send_image_to_gallery()` |
| `#user-profiles` | 1449059839581098135 | Profile updates | DM delivery |
| `#stock-alerts` | 1450589539562426418 | Stock audit alerts | `send_stock_alert()`, `send_stock_audit_summary()` |
| `#blockchain-alerts` | 1450589795058192465 | Chain monitoring | `send_blockchain_alert()`, `send_whale_alert()`, `send_exploit_alert()` |
| `#podcast-library` | 1451601597007134821 | Completed episodes | `send_podcast()` |
| DMs | -- | Personal notifications | Link/unlink, subscription, digest |

---

## Voice Capabilities

**Service:** `core/services/discord_voice.py`

| Feature | Technology | Status |
|---------|-----------|--------|
| Text-to-Speech | ElevenLabs API (10 voices) | ACTIVE |
| Speech-to-Text | OpenAI Whisper | ACTIVE |
| Voice Cloning | ElevenLabs IVC API | ACTIVE |
| Voice Chat | Join channel + TTS/STT loop | ACTIVE |
| Voice Recording | FFmpeg + WAV capture | ACTIVE |

**Default voice:** Rachel. 10 available: Rachel, Antoni, Bella, Callum, Charlotte, Daniel, Domi, Elli, Josh, Sam.

---

## Status Legend

- **ACTIVE** -- Command has full backend implementation with database queries and service integration
- **DORMANT** -- Framework exists but backend feature is incomplete or requires external dependency (e.g., DaVinci Resolve)
- **DEPRECATED** -- Scheduled for removal (none currently)

**Totals:** 104 ACTIVE, 8 DORMANT, 0 DEPRECATED

---

## Starting the Bot

```bash
# Set token
export DISCORD_BOT_TOKEN='your-token-here'

# Run via management command
python manage.py run_discord_bot
```

---

## Development Guidelines

1. **Adding a new command:** Add `@app_commands.command()` method in appropriate section of `discord_bot.py`. Commands are auto-synced on bot startup.
2. **Adding notifications:** Add `send_*` method in `discord_notifications.py`, use appropriate `CHANNEL_*` constant.
3. **Discord limit:** Max 100 global slash commands. Currently at 112 -- some may need to be guild-specific.
4. **Deferred responses:** Any command that takes >3s must `await interaction.response.defer()` first.
5. **Ephemeral messages:** Use `ephemeral=True` for sensitive data (billing, profile, auth).
