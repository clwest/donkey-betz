# Discord Commands Reference

**Last Updated:** Session 567 (December 28, 2025)
**Location:** `core/services/discord_bot.py`
**Total Commands:** 112 slash commands across 25 Cogs

---

## Overview

The Discord bot provides full platform access via slash commands. All commands are registered with Discord's application command system and support autocomplete where applicable.

---

## Command Summary by Cog

| Cog | Commands | Purpose |
|-----|----------|---------|
| StatusCommands | 1 | Bot status |
| AgentCommands | 2 | Agent listing and info |
| SpiderCommands | 10 | Betting, odds, arbitrage |
| InteractiveCommands | 7 | AI interaction, sessions |
| ContentCommands | 11 | Gallery, opportunities, subscriptions |
| VoiceCommands | 3 | Voice channel features |
| VoiceMarketplaceCommands | 3 | Voice clone marketplace |
| ContentPipelineCommands | 3 | Content creation pipeline |
| SeriesCommands | 4 | Video series management |
| StudioCommands | 7 | Autonomous content studio |
| GumroadCommands | 2 | Gumroad publishing |
| PipelineLearningCommands | 4 | Style learning system |
| ServerSetupCommands | 1 | Server configuration |
| ClientCommands | 4 | Client management |
| AgentAccessCommands | 10 | Direct agent access |
| HelpCommands | 1 | Help documentation |
| NarrativeCommands | 9 | Narrative drift tracking |
| ROICommands | 5 | ROI and analytics |
| ResolveCommands | 6 | DaVinci Resolve rendering |
| SituationCommands | 4 | Autonomous situations |
| PodcastCommands | 4 | Podcast generation |
| LegalCommands | 3 | Legal document assistance |
| DeveloperCommands | 2 | Code generation/review |
| MLScoringCommands | 1 | ML opportunity scoring |
| ReviewCommands | 5 | Chief of Staff reviews |

---

## 1. StatusCommands (1 Command)

### /status
**Description:** Show bot status and statistics
**Usage:** `/status`
**Response:** Displays bot uptime, connected servers, active agents, and system health metrics.

---

## 2. AgentCommands (2 Commands)

### /agents
**Description:** List all available agents
**Usage:** `/agents`
**Response:** Shows all 47 routable agents organized by category with their specializations.

### /agent
**Description:** Get detailed info about a specific agent
**Usage:** `/agent name:<agent_name>`
**Parameters:**
- `name` (required): Agent name (autocomplete enabled)
**Response:** Agent description, capabilities, evolution level, mood, and recent activity.

---

## 3. SpiderCommands (10 Commands)

### /trending
**Description:** Get trending topics from spider network
**Usage:** `/trending [category]`
**Parameters:**
- `category` (optional): Filter by category (tech, finance, sports, etc.)
**Response:** Top trending topics with engagement metrics and sources.

### /spiders
**Description:** List all active spiders and their status
**Usage:** `/spiders`
**Response:** All 77 spiders with last run time, record count, and health status.

### /predictions
**Description:** View AI predictions for upcoming events
**Usage:** `/predictions [sport]`
**Parameters:**
- `sport` (optional): Filter by sport type
**Response:** Predictions with confidence scores, expected value, and reasoning.

### /odds
**Description:** Get current odds for events
**Usage:** `/odds event:<event_name>`
**Parameters:**
- `event` (required): Event name or ID
**Response:** Current odds from multiple sportsbooks with line movement history.

### /arb
**Description:** Find arbitrage opportunities
**Usage:** `/arb [min_profit]`
**Parameters:**
- `min_profit` (optional): Minimum profit percentage (default: 1%)
**Response:** Current arbitrage opportunities with stake calculations.

### /bankroll
**Description:** View your bankroll and betting history
**Usage:** `/bankroll`
**Response:** Current balance, ROI, win rate, and recent bet history.

### /bet
**Description:** Log a bet
**Usage:** `/bet event:<event> amount:<amount> odds:<odds> pick:<pick>`
**Parameters:**
- `event` (required): Event name
- `amount` (required): Bet amount
- `odds` (required): Odds (American format)
- `pick` (required): Your selection
**Response:** Bet logged with expected value calculation.

### /resolve
**Description:** Resolve a pending bet
**Usage:** `/resolve bet_id:<id> result:<win/loss/push>`
**Parameters:**
- `bet_id` (required): Bet ID to resolve
- `result` (required): Outcome (win, loss, or push)
**Response:** Bet resolved, bankroll updated.

### /futures
**Description:** View futures bets and positions
**Usage:** `/futures`
**Response:** All open futures positions with current hedge values.

### /slip
**Description:** Create a bet slip with multiple selections
**Usage:** `/slip`
**Response:** Interactive bet slip builder with parlay calculations.

---

## 4. InteractiveCommands (7 Commands)

### /ask
**Description:** Ask the AI assistant a question
**Usage:** `/ask question:<your_question>`
**Parameters:**
- `question` (required): Your question
**Response:** AI response routed through Personal Assistant with agent consultation as needed.

### /create
**Description:** Create content with AI
**Usage:** `/create type:<type> prompt:<description>`
**Parameters:**
- `type` (required): Content type (image, video, audio, 3d)
- `prompt` (required): Description of what to create
**Response:** Generated content with download link.

### /research
**Description:** Start a research task
**Usage:** `/research topic:<topic> [depth]`
**Parameters:**
- `topic` (required): Research topic
- `depth` (optional): Research depth (quick, standard, comprehensive)
**Response:** Research report with sources and key findings.

### /clear
**Description:** Clear your conversation history
**Usage:** `/clear`
**Response:** Conversation cleared, fresh context started.

### /sessions
**Description:** View your active sessions
**Usage:** `/sessions`
**Response:** List of active conversations and their contexts.

### /link
**Description:** Link your Discord account to web platform
**Usage:** `/link code:<verification_code>`
**Parameters:**
- `code` (required): 6-digit verification code from web UI
**Response:** Account linked successfully.

### /unlink
**Description:** Unlink your Discord account
**Usage:** `/unlink`
**Response:** Account unlinked from web platform.

---

## 5. ContentCommands (11 Commands)

### /gallery
**Description:** View your generated content gallery
**Usage:** `/gallery [type] [limit]`
**Parameters:**
- `type` (optional): Filter by content type
- `limit` (optional): Number of items (default: 10)
**Response:** Gallery of your generated content with thumbnails.

### /profile
**Description:** View your user profile
**Usage:** `/profile`
**Response:** Profile stats, subscription tier, usage metrics.

### /opportunities
**Description:** View income opportunities
**Usage:** `/opportunities [category]`
**Parameters:**
- `category` (optional): Filter by category
**Response:** Curated opportunities matched to your skills.

### /apply
**Description:** Quick apply to an opportunity
**Usage:** `/apply opportunity_id:<id>`
**Parameters:**
- `opportunity_id` (required): Opportunity ID
**Response:** Application submitted with AI-generated cover letter.

### /track
**Description:** Track an opportunity or application
**Usage:** `/track opportunity_id:<id>`
**Parameters:**
- `opportunity_id` (required): ID to track
**Response:** Tracking enabled, you'll receive updates.

### /digest
**Description:** Get your personalized digest
**Usage:** `/digest [period]`
**Parameters:**
- `period` (optional): daily, weekly, or monthly
**Response:** Personalized summary of relevant updates.

### /alerts
**Description:** Configure your alert preferences
**Usage:** `/alerts`
**Response:** Interactive alert configuration panel.

### /subscribe
**Description:** Subscribe to a tier
**Usage:** `/subscribe tier:<tier_name>`
**Parameters:**
- `tier` (required): Subscription tier (basic, pro, enterprise)
**Response:** Stripe checkout link for subscription.

### /tier
**Description:** View subscription tier details
**Usage:** `/tier [tier_name]`
**Parameters:**
- `tier_name` (optional): Specific tier to view
**Response:** Tier features, pricing, and comparison.

### /cancel
**Description:** Cancel your subscription
**Usage:** `/cancel`
**Response:** Cancellation confirmation (subscription active until period end).

### /billing
**Description:** View billing history
**Usage:** `/billing`
**Response:** Recent invoices and payment history.

---

## 6. VoiceCommands (3 Commands)

### /voice
**Description:** Join a voice channel for recording
**Usage:** `/voice action:<join/leave>`
**Parameters:**
- `action` (required): join or leave
**Response:** Bot joins/leaves voice channel.

### /speak
**Description:** Make the bot speak in voice channel
**Usage:** `/speak text:<message> [voice]`
**Parameters:**
- `text` (required): Text to speak
- `voice` (optional): Voice ID to use
**Response:** Audio played in voice channel.

### /ask-voice
**Description:** Ask a question via voice
**Usage:** `/ask-voice`
**Response:** Bot listens for your question and responds via voice.

---

## 7. VoiceMarketplaceCommands (3 Commands)

### /voice-market
**Description:** Browse the voice clone marketplace
**Usage:** `/voice-market [category]`
**Parameters:**
- `category` (optional): Filter by voice category
**Response:** Available voice clones with samples and pricing.

### /voice-buy
**Description:** Purchase a voice clone
**Usage:** `/voice-buy voice_id:<id>`
**Parameters:**
- `voice_id` (required): Voice clone ID
**Response:** Stripe checkout for voice purchase.

### /voice-clone
**Description:** Create a voice clone from recording
**Usage:** `/voice-clone name:<name>`
**Parameters:**
- `name` (required): Name for your voice clone
**Response:** Voice clone created (requires prior voice recording).

---

## 8. ContentPipelineCommands (3 Commands)

### /create-content
**Description:** Start a content creation pipeline
**Usage:** `/create-content type:<type> prompt:<description> [tier]`
**Parameters:**
- `type` (required): Pipeline type (blog, video, social, full)
- `prompt` (required): Content description
- `tier` (optional): Quality tier ($5-$50K packages)
**Response:** Pipeline started, progress updates follow.

### /content-status
**Description:** Check content pipeline status
**Usage:** `/content-status job_id:<id>`
**Parameters:**
- `job_id` (required): Pipeline job ID
**Response:** Current stage, progress, and ETA.

### /showroom
**Description:** View content showroom
**Usage:** `/showroom [category]`
**Parameters:**
- `category` (optional): Filter by category
**Response:** Showcase of completed content projects.

---

## 9. SeriesCommands (4 Commands)

### /series-create
**Description:** Create a new video series
**Usage:** `/series-create name:<name> episodes:<count> theme:<theme>`
**Parameters:**
- `name` (required): Series name
- `episodes` (required): Number of episodes
- `theme` (required): Series theme/concept
**Response:** Series created, first episode generation started.

### /series-status
**Description:** Check series generation status
**Usage:** `/series-status series_id:<id>`
**Parameters:**
- `series_id` (required): Series ID
**Response:** Episode progress, render status, and preview links.

### /series-list
**Description:** List your video series
**Usage:** `/series-list`
**Response:** All your series with episode counts and status.

### /series-view
**Description:** View series details
**Usage:** `/series-view series_id:<id>`
**Parameters:**
- `series_id` (required): Series ID
**Response:** Full series details with episode list and metrics.

---

## 10. StudioCommands (7 Commands)

### /studio-create
**Description:** Create an autonomous content channel
**Usage:** `/studio-create name:<name> niche:<niche> frequency:<frequency>`
**Parameters:**
- `name` (required): Channel name
- `niche` (required): Content niche
- `frequency` (required): Publishing frequency (daily, weekly, etc.)
**Response:** Autonomous channel created, starts generating content.

### /studio-list
**Description:** List your content channels
**Usage:** `/studio-list`
**Response:** All autonomous channels with performance metrics.

### /studio-status
**Description:** Get channel status
**Usage:** `/studio-status channel_id:<id>`
**Parameters:**
- `channel_id` (required): Channel ID
**Response:** Channel health, recent episodes, and analytics.

### /studio-pause
**Description:** Pause autonomous generation
**Usage:** `/studio-pause channel_id:<id>`
**Parameters:**
- `channel_id` (required): Channel ID
**Response:** Generation paused (can resume anytime).

### /studio-resume
**Description:** Resume autonomous generation
**Usage:** `/studio-resume channel_id:<id>`
**Parameters:**
- `channel_id` (required): Channel ID
**Response:** Generation resumed, next episode scheduled.

### /studio-performance
**Description:** View channel performance analytics
**Usage:** `/studio-performance channel_id:<id>`
**Parameters:**
- `channel_id` (required): Channel ID
**Response:** Performance dashboard with trends and recommendations.

### /studio-episode
**Description:** View specific episode details
**Usage:** `/studio-episode episode_id:<id>`
**Parameters:**
- `episode_id` (required): Episode ID
**Response:** Episode details, debate log, and performance metrics.

---

## 11. GumroadCommands (2 Commands)

### /publish-gumroad
**Description:** Publish content to Gumroad
**Usage:** `/publish-gumroad content_id:<id> price:<price>`
**Parameters:**
- `content_id` (required): Content ID to publish
- `price` (required): Price in USD
**Response:** Gumroad listing created with purchase link.

### /gumroad-status
**Description:** Check Gumroad sales status
**Usage:** `/gumroad-status [product_id]`
**Parameters:**
- `product_id` (optional): Specific product ID
**Response:** Sales metrics, revenue, and customer data.

---

## 12. PipelineLearningCommands (4 Commands)

### /rate-series
**Description:** Rate a series for learning
**Usage:** `/rate-series series_id:<id> rating:<1-5> [feedback]`
**Parameters:**
- `series_id` (required): Series ID
- `rating` (required): Rating 1-5
- `feedback` (optional): Additional feedback
**Response:** Rating recorded, improves future generations.

### /learning-stats
**Description:** View learning system statistics
**Usage:** `/learning-stats`
**Response:** Learning metrics, style improvements, and adaptation rate.

### /style-recommend
**Description:** Get style recommendations
**Usage:** `/style-recommend content_type:<type>`
**Parameters:**
- `content_type` (required): Type of content
**Response:** Recommended styles based on your preferences and performance.

### /style-leaderboard
**Description:** View top performing styles
**Usage:** `/style-leaderboard [category]`
**Parameters:**
- `category` (optional): Content category
**Response:** Leaderboard of styles by performance metrics.

---

## 13. ServerSetupCommands (1 Command)

### /setup
**Description:** Configure bot for this server
**Usage:** `/setup`
**Permission:** Administrator required
**Response:** Interactive setup wizard for server configuration.

---

## 14. ClientCommands (4 Commands)

### /client-add
**Description:** Add a new client
**Usage:** `/client-add name:<name> email:<email> [company]`
**Parameters:**
- `name` (required): Client name
- `email` (required): Client email
- `company` (optional): Company name
**Response:** Client added to your roster.

### /client-list
**Description:** List your clients
**Usage:** `/client-list`
**Response:** All clients with project counts and status.

### /client-deliver
**Description:** Deliver content to a client
**Usage:** `/client-deliver client_id:<id> content_id:<content_id>`
**Parameters:**
- `client_id` (required): Client ID
- `content_id` (required): Content to deliver
**Response:** Content delivered, client notified.

### /client-invite
**Description:** Invite client to Discord
**Usage:** `/client-invite client_id:<id>`
**Parameters:**
- `client_id` (required): Client ID
**Response:** Invitation link generated for client.

---

## 15. AgentAccessCommands (10 Commands)

### /agent-list
**Description:** List agents by category
**Usage:** `/agent-list [category]`
**Parameters:**
- `category` (optional): Agent category
**Response:** Agents in category with availability status.

### /agent-task
**Description:** Assign a task to specific agent
**Usage:** `/agent-task agent:<name> task:<description>`
**Parameters:**
- `agent` (required): Agent name
- `task` (required): Task description
**Response:** Task assigned, agent working on it.

### /audit-contract
**Description:** Audit a smart contract
**Usage:** `/audit-contract address:<address> [chain]`
**Parameters:**
- `address` (required): Contract address
- `chain` (optional): Blockchain (default: ethereum)
**Response:** Security audit report with vulnerability assessment.

### /blockchain-status
**Description:** Get blockchain monitoring status
**Usage:** `/blockchain-status [chain]`
**Parameters:**
- `chain` (optional): Specific blockchain
**Response:** Monitored addresses, alerts, and recent events.

### /voice-ask
**Description:** Ask using voice input
**Usage:** `/voice-ask`
**Response:** Voice input mode activated.

### /voice-chat
**Description:** Start voice conversation mode
**Usage:** `/voice-chat`
**Response:** Continuous voice conversation started.

### /consult
**Description:** Consult with an advisor
**Usage:** `/consult advisor:<name> question:<question>`
**Parameters:**
- `advisor` (required): Advisor name (Warren Buffett, etc.)
- `question` (required): Your question
**Response:** Advisor's perspective on your question.

### /advisors
**Description:** List available advisors
**Usage:** `/advisors`
**Response:** All 25 advisors with their specializations.

### /workflow-list
**Description:** List available workflows
**Usage:** `/workflow-list`
**Response:** All workflows with descriptions and triggers.

### /workflow-run
**Description:** Run a workflow
**Usage:** `/workflow-run workflow:<name> [params]`
**Parameters:**
- `workflow` (required): Workflow name
- `params` (optional): Workflow parameters (JSON)
**Response:** Workflow started, progress updates follow.

---

## 16. HelpCommands (1 Command)

### /help
**Description:** Get help with commands
**Usage:** `/help [command]`
**Parameters:**
- `command` (optional): Specific command name
**Response:** Command documentation and examples.

---

## 17. NarrativeCommands (9 Commands)

### /narratives
**Description:** View active narratives
**Usage:** `/narratives [domain]`
**Parameters:**
- `domain` (optional): Filter by domain
**Response:** Active narratives with momentum and confidence.

### /narrative-shifts
**Description:** View recent narrative shifts
**Usage:** `/narrative-shifts [hours]`
**Parameters:**
- `hours` (optional): Lookback period (default: 24)
**Response:** Detected narrative shifts with evidence.

### /narrative-scan
**Description:** Scan for emerging narratives
**Usage:** `/narrative-scan topic:<topic>`
**Parameters:**
- `topic` (required): Topic to scan
**Response:** Emerging narratives around the topic.

### /narrative-seed
**Description:** Seed a narrative hypothesis
**Usage:** `/narrative-seed narrative:<description> [evidence]`
**Parameters:**
- `narrative` (required): Narrative description
- `evidence` (optional): Supporting evidence
**Response:** Narrative seeded, tracking started.

### /narrative-status
**Description:** Get narrative tracking status
**Usage:** `/narrative-status narrative_id:<id>`
**Parameters:**
- `narrative_id` (required): Narrative ID
**Response:** Narrative strength, evidence, and trajectory.

### /narrative-evidence
**Description:** View evidence for a narrative
**Usage:** `/narrative-evidence narrative_id:<id>`
**Parameters:**
- `narrative_id` (required): Narrative ID
**Response:** All evidence supporting/contradicting the narrative.

### /narrative-domains
**Description:** List narrative domains
**Usage:** `/narrative-domains`
**Response:** All tracked domains with active narrative counts.

### /narrative-watch
**Description:** Watch a narrative for updates
**Usage:** `/narrative-watch narrative_id:<id>`
**Parameters:**
- `narrative_id` (required): Narrative ID
**Response:** Watching enabled, you'll receive shift alerts.

### /narrative-trending
**Description:** View trending narratives
**Usage:** `/narrative-trending [domain]`
**Parameters:**
- `domain` (optional): Filter by domain
**Response:** Top trending narratives by momentum.

---

## 18. ROICommands (5 Commands)

### /roi-summary
**Description:** Get ROI summary
**Usage:** `/roi-summary [period]`
**Parameters:**
- `period` (optional): Time period (week, month, quarter)
**Response:** ROI metrics across all activities.

### /roi-dashboard
**Description:** View full ROI dashboard
**Usage:** `/roi-dashboard`
**Response:** Comprehensive ROI dashboard with charts.

### /roi-brief
**Description:** Get quick ROI brief
**Usage:** `/roi-brief`
**Response:** One-line ROI status with key metrics.

### /roi-funnel
**Description:** View conversion funnel
**Usage:** `/roi-funnel [source]`
**Parameters:**
- `source` (optional): Traffic source
**Response:** Funnel visualization with conversion rates.

### /roi-attribution
**Description:** View attribution analysis
**Usage:** `/roi-attribution [model]`
**Parameters:**
- `model` (optional): Attribution model (first, last, linear)
**Response:** Revenue attribution by source and channel.

---

## 19. ResolveCommands (6 Commands)

### /resolve-render
**Description:** Render video in DaVinci Resolve
**Usage:** `/resolve-render project:<project> [settings]`
**Parameters:**
- `project` (required): Project name or ID
- `settings` (optional): Render preset (4k, 1080p, etc.)
**Response:** Render job queued, progress updates follow.

### /color-grade
**Description:** Apply color grading
**Usage:** `/color-grade video_id:<id> style:<style>`
**Parameters:**
- `video_id` (required): Video ID
- `style` (required): Grading style (cinematic, vivid, etc.)
**Response:** Color grading applied, preview available.

### /render-status
**Description:** Check render job status
**Usage:** `/render-status job_id:<id>`
**Parameters:**
- `job_id` (required): Render job ID
**Response:** Render progress, ETA, and queue position.

### /render-download
**Description:** Download rendered video
**Usage:** `/render-download job_id:<id>`
**Parameters:**
- `job_id` (required): Render job ID
**Response:** Download link for completed render.

### /trending-grades
**Description:** View trending color grades
**Usage:** `/trending-grades`
**Response:** Popular color grading styles with samples.

### /videos-list
**Description:** List your videos
**Usage:** `/videos-list [status]`
**Parameters:**
- `status` (optional): Filter by status (draft, rendering, complete)
**Response:** Your videos with status and metrics.

---

## 20. SituationCommands (4 Commands)

### /situation-list
**Description:** List autonomous situations
**Usage:** `/situation-list [status]`
**Parameters:**
- `status` (optional): Filter by status (active, paused, completed)
**Response:** All autonomous situations with health status.

### /situation-status
**Description:** Get situation status
**Usage:** `/situation-status situation_id:<id>`
**Parameters:**
- `situation_id` (required): Situation ID
**Response:** Situation health, triggers, actions, and metrics.

### /situation-run
**Description:** Manually trigger a situation
**Usage:** `/situation-run situation_id:<id>`
**Parameters:**
- `situation_id` (required): Situation ID
**Response:** Situation triggered, execution started.

### /situation-alerts
**Description:** View situation alerts
**Usage:** `/situation-alerts [situation_id]`
**Parameters:**
- `situation_id` (optional): Filter by situation
**Response:** Recent alerts and notifications from situations.

---

## 21. PodcastCommands (4 Commands)

### /podcast-create
**Description:** Create a new podcast episode
**Usage:** `/podcast-create topic:<topic> [guests] [duration]`
**Parameters:**
- `topic` (required): Episode topic
- `guests` (optional): Guest names (comma-separated)
- `duration` (optional): Target duration in minutes
**Response:** Podcast generation started.

### /podcast-list
**Description:** List your podcast episodes
**Usage:** `/podcast-list [show]`
**Parameters:**
- `show` (optional): Filter by show name
**Response:** Your podcast episodes with status.

### /podcast-status
**Description:** Check podcast generation status
**Usage:** `/podcast-status episode_id:<id>`
**Parameters:**
- `episode_id` (required): Episode ID
**Response:** Generation progress, script status, audio status.

### /podcast-script
**Description:** View/edit podcast script
**Usage:** `/podcast-script episode_id:<id>`
**Parameters:**
- `episode_id` (required): Episode ID
**Response:** Episode script with editing options.

---

## 22. LegalCommands (3 Commands)

### /legal-draft
**Description:** Draft a legal document
**Usage:** `/legal-draft type:<type> context:<context>`
**Parameters:**
- `type` (required): Document type (motion, response, declaration, etc.)
- `context` (required): Case context and requirements
**Response:** Draft document with proper formatting.

### /legal-analyze
**Description:** Analyze a legal document
**Usage:** `/legal-analyze document_id:<id>`
**Parameters:**
- `document_id` (required): Document ID or URL
**Response:** Document analysis with key points and concerns.

### /legal-case
**Description:** Get case status and timeline
**Usage:** `/legal-case case_id:<id>`
**Parameters:**
- `case_id` (required): Case ID
**Response:** Case timeline, deadlines, and document status.

---

## 23. DeveloperCommands (2 Commands)

### /code-generate
**Description:** Generate code with AI
**Usage:** `/code-generate language:<lang> task:<description>`
**Parameters:**
- `language` (required): Programming language
- `task` (required): What the code should do
**Response:** Generated code with explanation.

### /code-review
**Description:** Review code for issues
**Usage:** `/code-review code:<code_block>`
**Parameters:**
- `code` (required): Code to review
**Response:** Code review with suggestions and issues.

---

## 24. MLScoringCommands (1 Command)

### /ml-scoring
**Description:** Score an opportunity with ML
**Usage:** `/ml-scoring opportunity_id:<id>`
**Parameters:**
- `opportunity_id` (required): Opportunity ID
**Response:** ML score with SHAP explanation and confidence.

---

## 25. ReviewCommands (5 Commands)

### /review
**Description:** Generate a Chief of Staff review document
**Usage:** `/review topic:<topic> [context]`
**Parameters:**
- `topic` (required): Decision topic
- `context` (optional): Additional context
**Response:** Pro/Con review document with recommendations.

### /review-list
**Description:** List recent review documents
**Usage:** `/review-list [status]`
**Parameters:**
- `status` (optional): Filter by status (pending, approved, rejected)
**Response:** Recent reviews with status and outcomes.

### /ask-pro
**Description:** Get Pro perspective on a decision
**Usage:** `/ask-pro topic:<topic>`
**Parameters:**
- `topic` (required): Decision topic
**Response:** Arguments in favor of the decision.

### /ask-con
**Description:** Get Con perspective on a decision
**Usage:** `/ask-con topic:<topic>`
**Parameters:**
- `topic` (required): Decision topic
**Response:** Arguments against the decision.

### /decide
**Description:** Record a decision outcome
**Usage:** `/decide review_id:<id> decision:<approve/reject> [notes]`
**Parameters:**
- `review_id` (required): Review document ID
- `decision` (required): approve or reject
- `notes` (optional): Decision notes
**Response:** Decision recorded, learning updated.

---

## Quick Reference

### Most Used Commands

| Command | Purpose |
|---------|---------|
| `/ask` | Ask AI anything |
| `/create` | Generate content |
| `/research` | Deep research |
| `/agents` | List all agents |
| `/trending` | See what's trending |
| `/odds` | Get betting odds |
| `/arb` | Find arbitrage |
| `/help` | Get help |

### Admin Commands

| Command | Purpose |
|---------|---------|
| `/setup` | Configure server |
| `/link` | Link Discord to web |
| `/alerts` | Configure alerts |

### Power User Commands

| Command | Purpose |
|---------|---------|
| `/agent-task` | Direct agent access |
| `/consult` | Advisor consultation |
| `/workflow-run` | Run workflows |
| `/studio-create` | Autonomous content |
| `/narrative-scan` | Narrative intelligence |

---

## See Also

- [AGENTS.md](AGENTS.md) - All 71 agents
- [SPIDERS.md](SPIDERS.md) - All 77 spiders
- [SERVICES.md](SERVICES.md) - All 93 services
- [CAPABILITIES.md](CAPABILITIES.md) - Full feature list
