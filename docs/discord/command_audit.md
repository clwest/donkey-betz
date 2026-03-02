# Discord Command Audit — Phase G1

**Date:** 2026-03-01
**Bot:** Donkey Betz AI Platform Bot
**App ID:** 1444884424339755008
**Guild:** 971148613109555212 (all commands guild-scoped)
**Token env var:** `DISCORD_BOT_TOKEN`
**Source file:** `core/services/discord_bot.py` (14.6k lines)

## Slot Budget

| Metric | Count |
|--------|-------|
| Discord limit | 100 |
| Active (registered) | **94** |
| Disabled (commented out) | 21 |
| Free slots | **6** |
| Target after Phase G2 | ≤ 70 |

## Active Cogs (25) — 94 Commands

### StatusCommands (1 command)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/status` | 555 | Check system health and status | **Keep** — core command |

### AgentCommands (2 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/agents` | 621 | List active agents with stats | **Merge** → `/agents action:list` |
| `/agent` | 702 | Get details for a specific agent | **Merge** → `/agents action:detail` |

### SpiderCommands (10 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/trending` | 795 | Get trending topics from spider data | **Keep** |
| `/spiders` | 912 | List spider network stats | **Keep** |
| `/predictions` | 974 | View prediction market signals from Kalshi | **Keep** |
| `/odds` | 1105 | View sports betting odds and analysis | **Keep** |
| `/arb` | 1257 | Scan for arbitrage opportunities | **Keep** |
| `/bankroll` | 1400 | View your betting bankroll and stats | **Keep** |
| `/bet` | 1526 | Log a new bet to your bankroll | **Keep** |
| `/resolve` | 1635 | Resolve a pending bet (won/lost/pushed) | **Keep** |
| `/futures` | 1740 | View championship futures odds | **Keep** |
| `/slip` | 1844 | Generate a bet slip | **Keep** |

> SpiderCommands is heavily used for sports betting — all 10 kept as-is.

### InteractiveCommands (7 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/ask` | 1976 | Ask the Personal Assistant a question | **Keep** — core command |
| `/create` | 2110 | Generate an image with AI | **Keep** — core command |
| `/research` | 2304 | Search spider data for a topic | **Keep** |
| `/clear` | 2391 | Clear your conversation history | **Keep** |
| `/sessions` | 2415 | View/manage conversation sessions | **Keep** |
| `/link` | 2570 | Link Discord account to web account | **Keep** |
| `/unlink` | 2636 | Unlink Discord account | **Keep** |

### ContentCommands (11 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/gallery` | 2699 | View recent AI-generated images | **Keep** |
| `/profile` | 2798 | View AI Studio profile and stats | **Keep** |
| `/opportunities` | 2938 | View matching income opportunities | **Keep** |
| `/apply` | 3044 | Apply to an opportunity | **Keep** |
| `/track` | 3149 | Track your job applications | **Keep** |
| `/digest` | 3288 | Get daily/weekly activity digest | **Keep** |
| `/alerts` | 3471 | Manage opportunity alerts | **Keep** |
| `/subscribe` | 3565 | Subscribe to Pro or Premium | **Keep** |
| `/tier` | 3646 | View subscription tier and usage | **Keep** |
| `/cancel` | 3780 | Cancel subscription | **Drop** — redirect to web |
| `/billing` | 3848 | Access billing portal | **Drop** — redirect to web |

### VoiceCommands (3 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/voice` | 3938 | Join voice channel for interaction | **Merge** → `/voice action:join` |
| `/speak` | 4072 | Make bot speak in voice channel | **Merge** → `/voice action:speak` |
| `/ask-voice` | 4131 | Ask AI and hear response in voice | **Merge** → `/voice action:ask` |

### ContentPipelineCommands (3 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/create-content` | 5280 | AI Content Factory | **Keep** |
| `/content-status` | 5403 | Check content package status | **Keep** |
| `/showroom` | 5480 | Browse content marketplace | **Drop** — redirect to web |

### SeriesCommands (4 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/series-create` | 5737 | Create multi-episode series | **Merge** → `/series action:create` |
| `/series-status` | 5843 | Check series status | **Merge** → `/series action:status` |
| `/series-list` | 5936 | List your series | **Merge** → `/series action:list` |
| `/series-view` | 6005 | View episode content | **Merge** → `/series action:view` |

### StudioCommands (7 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/studio-create` | 6205 | Create autonomous content channel | **Merge** → `/studio action:create` |
| `/studio-list` | 6319 | List content channels | **Merge** → `/studio action:list` |
| `/studio-status` | 6383 | Check channel status | **Merge** → `/studio action:status` |
| `/studio-pause` | 6505 | Pause content generation | **Merge** → `/studio action:pause` |
| `/studio-resume` | 6562 | Resume content generation | **Merge** → `/studio action:resume` |
| `/studio-performance` | 6619 | View channel analytics | **Merge** → `/studio action:performance` |
| `/studio-episode` | 6736 | View episode content | **Merge** → `/studio action:episode` |

### GumroadCommands (2 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/publish-gumroad` | 6872 | Publish image to Gumroad | **Keep** |
| `/gumroad-status` | 6984 | Check Gumroad connection | **Drop** — very niche |

### RoleManager (0 commands)

No slash commands — event-driven Cog only. **Keep** as-is.

### HelpCommands (1 command)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/help` | 9546 | Show available commands | **Keep** — core command |

### ReactionFeedbackCog (0 commands)

No slash commands — event-driven Cog only. **Keep** as-is.

### ServerSetupCommands (1 command)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/setup` | 7489 | Set up AI Studio channels | **Keep** |

### ClientCommands (4 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/client-add` | 7663 | Create new client | **Merge** → `/client action:add` |
| `/client-list` | 7790 | List clients | **Merge** → `/client action:list` |
| `/client-deliver` | 7857 | Send deliverable to client | **Merge** → `/client action:deliver` |
| `/client-invite` | 8010 | Generate invite for client | **Merge** → `/client action:invite` |

### AgentAccessCommands (10 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/agent-list` | 8114 | List agents by category | **Merge** → `/agents action:list` (with AgentCommands) |
| `/agent-task` | 8206 | Execute task with specific agent | **Merge** → `/agents action:task` |
| `/audit-contract` | 8415 | Audit smart contract | **Keep** — unique blockchain function |
| `/blockchain-status` | 8574 | Blockchain monitoring status | **Keep** |
| `/voice-ask` | 8644 | Ask question, hear AI speak | **Merge** → `/voice action:ask` (duplicate of VoiceCommands) |
| `/voice-chat` | 8848 | Speak to AI, hear response | **Merge** → `/voice action:chat` |
| `/consult` | 9186 | Consult a legendary advisor | **Keep** — unique feature |
| `/advisors` | 9338 | List available advisors | **Keep** |
| `/workflow-list` | 9380 | List workflows | **Merge** → `/workflow action:list` |
| `/workflow-run` | 9442 | Run a workflow | **Merge** → `/workflow action:run` |

### ResolveCommands (6 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/resolve-render` | 11349 | Start DaVinci Resolve render | **Merge** → `/davinci action:render` |
| `/color-grade` | 11459 | Apply color grading | **Merge** → `/davinci action:grade` |
| `/render-status` | 11567 | Check render job status | **Merge** → `/davinci action:status` |
| `/render-download` | 11665 | Download completed render | **Merge** → `/davinci action:download` |
| `/trending-grades` | 11761 | Show trending color grades | **Drop** — very niche |
| `/videos-list` | 11859 | List videos for rendering | **Merge** → `/davinci action:videos` |

> Note: Renamed hub from `/resolve` to `/davinci` to avoid collision with SpiderCommands `/resolve` (bet resolution).

### SituationCommands (4 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/situation-list` | 12184 | List 19 autonomous situations | **Merge** → `/situation action:list` |
| `/situation-status` | 12291 | Check situation status | **Merge** → `/situation action:status` |
| `/situation-run` | 12491 | Trigger a situation | **Merge** → `/situation action:run` |
| `/situation-alerts` | 12616 | Configure situation alerts | **Merge** → `/situation action:alerts` |

### PodcastCommands (4 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/podcast-create` | 12768 | Create AI podcast episode | **Merge** → `/podcast action:create` |
| `/podcast-list` | 12895 | List podcast episodes | **Merge** → `/podcast action:list` |
| `/podcast-status` | 12962 | Check podcast status | **Merge** → `/podcast action:status` |
| `/podcast-script` | 13031 | View full podcast script | **Merge** → `/podcast action:script` |

### LegalCommands (3 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/legal-draft` | 13121 | Draft legal document | **Merge** → `/legal action:draft` |
| `/legal-analyze` | 13204 | Analyze denied motion | **Merge** → `/legal action:analyze` |
| `/legal-case` | 13274 | Get case profile info | **Merge** → `/legal action:case` |

### DeveloperCommands (2 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/code-generate` | 13356 | Generate code from spec | **Merge** → `/code action:generate` |
| `/code-review` | 13436 | Review code for bugs/security | **Merge** → `/code action:review` |

### MLScoringCommands (1 command)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/ml-scoring` | 13536 | View ML scoring status | **Keep** |

### ReviewCommands (5 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/review` | 13642 | Show review document | **Merge** → `/review action:show` |
| `/review-list` | 13736 | List pending reviews | **Merge** → `/review action:list` |
| `/ask-pro` | 13778 | Ask Pro advocate | **Merge** → `/review action:pro` |
| `/ask-con` | 13820 | Ask Con skeptic | **Merge** → `/review action:con` |
| `/decide` | 13862 | Make a decision on review | **Merge** → `/review action:decide` |

### HumanInterfaceCommands (0 commands)

No slash commands — event-driven Cog only. **Keep** as-is.

### OBSCommands (3 commands)

| Command | Line | Description | Proposed Action |
|---------|------|-------------|-----------------|
| `/obs-status` | 14492 | Check OBS bridge + recording | **Keep** (already consolidated) |
| `/obs-record` | 14517 | Start/stop/toggle recording | **Keep** (already consolidated) |
| `/obs-upload` | 14547 | Upload last recording | **Keep** (already consolidated) |

---

## Disabled Cogs (4) — 21 Commands

| Cog | Commands | Status |
|-----|----------|--------|
| VoiceMarketplaceCommands | 3 (voice-market, voice-buy, voice-clone) | Disabled since Session 558 |
| PipelineLearningCommands | 4 (rate-series, learning-stats, style-recommend, style-leaderboard) | Disabled since Session 558 |
| NarrativeCommands | 9 (narratives, narrative-shifts, etc.) | Disabled since Session 558 |
| ROICommands | 5 (roi-summary, roi-dashboard, etc.) | Disabled since Session 558 |

**Recommendation:** Delete dead code for all 4 disabled Cogs in Phase G2 cleanup PR.

---

## Consolidation Summary

### Proposed Merges (save 31 slots)

| Hub Command | Replaces | Saves |
|-------------|----------|-------|
| `/agents action:list\|detail\|task` | /agent, /agents, /agent-list, /agent-task | 3 |
| `/studio action:create\|list\|status\|pause\|resume\|performance\|episode` | 7 studio-* commands | 6 |
| `/davinci action:render\|grade\|status\|download\|videos` | 5 resolve/render commands | 4 |
| `/series action:create\|list\|status\|view` | 4 series-* commands | 3 |
| `/situation action:list\|status\|run\|alerts` | 4 situation-* commands | 3 |
| `/podcast action:create\|list\|status\|script` | 4 podcast-* commands | 3 |
| `/client action:add\|list\|deliver\|invite` | 4 client-* commands | 3 |
| `/review action:show\|list\|pro\|con\|decide` | 5 review/ask-pro/ask-con/decide commands | 4 |
| `/voice action:join\|speak\|ask\|chat` | 5 voice commands across 2 cogs | 4 |
| `/legal action:draft\|analyze\|case` | 3 legal-* commands | 2 |
| `/workflow action:list\|run` | workflow-list, workflow-run | 1 |
| `/code action:generate\|review` | code-generate, code-review | 1 |

### Proposed Drops (save 5 slots)

| Command | Reason |
|---------|--------|
| `/cancel` | Redirect to web billing portal |
| `/billing` | Redirect to web billing portal |
| `/showroom` | Redirect to web marketplace |
| `/gumroad-status` | Very niche, use Cockpit |
| `/trending-grades` | Very niche, use Cockpit |

### Projected Result

| Metric | Before | After |
|--------|--------|-------|
| Active commands | 94 | **58** |
| Free slots | 6 | **42** |
| Dead code removed | 0 | 21 (4 disabled Cogs) |

---

## Commands Kept As-Is (no change)

These 58 commands survive Phase G2 as either standalone or hub commands:

**Standalone (33):** status, trending, spiders, predictions, odds, arb, bankroll, bet, resolve, futures, slip, ask, create, research, clear, sessions, link, unlink, gallery, profile, opportunities, apply, track, digest, alerts, subscribe, tier, create-content, content-status, setup, audit-contract, blockchain-status, consult, advisors, publish-gumroad, help, ml-scoring

**Hub commands (12):** agents, studio, davinci, series, situation, podcast, client, review, voice, legal, workflow, code

**OBS (3):** obs-status, obs-record, obs-upload

---

## Orphan Registrations

No orphan registrations detected — all commands in source are either active or disabled in setup_hook. Discord API REST fetch returned 403 (token lacks `applications.commands` OAuth2 scope for REST endpoint; commands sync via `discord.py` `bot.tree.sync(guild=...)`).

---

## Next Steps

1. **Phase G2:** Implement consolidation merges + drops (target ≤ 70)
2. **Phase G3:** Add startup command-count gate (warn at 85, fail at 95)
