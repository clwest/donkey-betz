# Agent 1.7: Discord Commands Discovery

**Date:** December 21, 2025
**Status:** Complete
**Total Commands Discovered:** 99 slash commands

---

## Summary

Discovered **99 Discord slash commands** in `core/services/discord_bot.py`:
- Full parity with web interface for most features
- Voice interaction capabilities
- Client/agency management

---

## 1. Core Commands (8)

| Command | Description |
|---------|-------------|
| `/status` | Check system health and status |
| `/help` | Show available commands |
| `/setup` | Set up AI Studio channels in server |
| `/link` | Link Discord to AI Studio account |
| `/unlink` | Unlink Discord account |
| `/profile` | View AI Studio profile |
| `/clear` | Clear conversation history |
| `/sessions` | View conversation sessions |

---

## 2. AI & Agent Commands (12)

| Command | Description |
|---------|-------------|
| `/ask` | Ask the Personal Assistant |
| `/agents` | List active agents with stats |
| `/agent` | Get details for specific agent |
| `/agent-list` | List agents by category |
| `/agent-task` | Execute task with specific agent |
| `/consult` | Consult a legendary advisor |
| `/advisors` | List all advisors |
| `/workflow-list` | List available workflows |
| `/workflow-run` | Run multi-step workflow |
| `/learning-stats` | View learning statistics |
| `/style-recommend` | Get style recommendation |
| `/style-leaderboard` | View top styles |

---

## 3. Spider & Intelligence Commands (5)

| Command | Description |
|---------|-------------|
| `/trending` | Get trending topics |
| `/spiders` | List spider network stats |
| `/research` | Search spider data |
| `/ml-scoring` | View ML scoring status |

---

## 4. Content Creation Commands (8)

| Command | Description |
|---------|-------------|
| `/create` | Generate an image with AI |
| `/gallery` | View recent images |
| `/create-content` | Create content packages |
| `/content-status` | Check content status |
| `/showroom` | Browse content marketplace |
| `/publish-gumroad` | Publish to Gumroad |
| `/gumroad-status` | Check Gumroad connection |
| `/rate-series` | Rate series/episode |

---

## 5. AI Series Commands (5)

| Command | Description |
|---------|-------------|
| `/series-create` | Create AI content series |
| `/series-status` | Check series status |
| `/series-list` | List AI series |
| `/series-view` | View episode content |

---

## 6. Autonomous Studio Commands (7)

| Command | Description |
|---------|-------------|
| `/studio-create` | Create autonomous channel |
| `/studio-list` | List content channels |
| `/studio-status` | Check channel status |
| `/studio-pause` | Pause generation |
| `/studio-resume` | Resume generation |
| `/studio-performance` | View analytics |
| `/studio-episode` | View episode content |

---

## 7. Opportunity Commands (5)

| Command | Description |
|---------|-------------|
| `/opportunities` | View matching opportunities |
| `/apply` | Apply to an opportunity |
| `/track` | Track job applications |
| `/digest` | Get activity digest |
| `/alerts` | Manage opportunity alerts |

---

## 8. Voice Commands (8)

| Command | Description |
|---------|-------------|
| `/voice` | Join voice channel |
| `/speak` | Make bot speak message |
| `/ask-voice` | Ask AI with voice response |
| `/voice-ask` | Ask and hear AI response |
| `/voice-chat` | Speak to AI |
| `/voice-market` | Browse voice marketplace |
| `/voice-buy` | Purchase voice credits |
| `/voice-clone` | Clone voice for marketplace |

---

## 9. Subscription Commands (4)

| Command | Description |
|---------|-------------|
| `/subscribe` | Subscribe to Pro/Premium |
| `/tier` | View subscription tier |
| `/cancel` | Cancel subscription |
| `/billing` | Access billing portal |

---

## 10. Client Management Commands (5)

| Command | Description |
|---------|-------------|
| `/client-add` | Create new client |
| `/client-list` | List all clients |
| `/client-deliver` | Send deliverable |
| `/client-invite` | Generate invite link |

---

## 11. Blockchain Commands (3)

| Command | Description |
|---------|-------------|
| `/audit-contract` | Audit smart contract |
| `/blockchain-status` | Check monitoring status |

---

## 12. Narrative Drift Commands (10)

| Command | Description |
|---------|-------------|
| `/narratives` | List tracked narratives |
| `/narrative-shifts` | List recent shifts |
| `/narrative-scan` | Run narrative scan |
| `/narrative-seed` | Seed narratives |
| `/narrative-status` | Get system status |
| `/narrative-evidence` | View evidence |
| `/narrative-domains` | Domain overview |
| `/narrative-watch` | Watch narrative |
| `/narrative-trending` | Trending narratives |

---

## 13. ROI & Analytics Commands (5)

| Command | Description |
|---------|-------------|
| `/roi-summary` | ROI summary metrics |
| `/roi-dashboard` | ROI dashboard |
| `/roi-brief` | Weekly intelligence brief |
| `/roi-funnel` | Conversion funnel |
| `/roi-attribution` | Revenue attribution |

---

## 14. DaVinci Resolve Commands (6)

| Command | Description |
|---------|-------------|
| `/resolve-render` | Start Resolve render |
| `/color-grade` | Apply color grading |
| `/render-status` | Check render status |
| `/render-download` | Download render |
| `/trending-grades` | Trending color grades |
| `/videos-list` | List available videos |

---

## 15. Autonomous Situations Commands (4)

| Command | Description |
|---------|-------------|
| `/situation-list` | List 19 situations |
| `/situation-status` | Check situation status |
| `/situation-run` | Trigger situation |
| `/situation-alerts` | Configure alerts |

---

## 16. Podcast Commands (4)

| Command | Description |
|---------|-------------|
| `/podcast-create` | Create podcast episode |
| `/podcast-list` | List episodes |
| `/podcast-status` | Check status |
| `/podcast-script` | View script |

---

## 17. Legal Commands (3)

| Command | Description |
|---------|-------------|
| `/legal-draft` | Draft legal document |
| `/legal-analyze` | Analyze denied motion |
| `/legal-case` | Get case info |

---

## 18. Development Commands (2)

| Command | Description |
|---------|-------------|
| `/code-generate` | Generate code |
| `/code-review` | Review code |

---

## 19. Command Categories Summary

| Category | Count |
|----------|-------|
| Core | 8 |
| AI & Agents | 12 |
| Spider/Intelligence | 5 |
| Content Creation | 8 |
| AI Series | 5 |
| Autonomous Studio | 7 |
| Opportunities | 5 |
| Voice | 8 |
| Subscription | 4 |
| Client Management | 5 |
| Blockchain | 3 |
| Narrative Drift | 10 |
| ROI & Analytics | 5 |
| DaVinci Resolve | 6 |
| Autonomous Situations | 4 |
| Podcast | 4 |
| Legal | 3 |
| Development | 2 |
| **TOTAL** | **99** |

---

## 20. Gaps Identified

### P1 - High
1. **No error handling in some commands** - Some commands lack try/catch
2. **Rate limiting** - May need per-command rate limits

### P2 - Medium
3. **Command discoverability** - 99 commands is a lot to navigate
4. **Help organization** - Could be categorized better in /help

---

*Generated by Agent 1.7: Discord Commands Discovery*
