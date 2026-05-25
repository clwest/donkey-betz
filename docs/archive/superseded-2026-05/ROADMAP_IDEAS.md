# Roadmap Ideas

**Created:** December 16, 2025 - Session 458
**Updated:** December 16, 2025 - Session 461
**Status:** Ideas to revisit when looking for next features

---

## Quick Wins

| Idea | Description | Effort | Status |
|------|-------------|--------|--------|
| Voice Output in Chat | Personal Assistant speaks responses using cloned ElevenLabs voice | Medium | ✅ Done (Session 458) |
| Profile Follow-ups | Deeper interview questions for better personalization | Low | Pending |
| "While You Were Away" Dashboard | Summary of agent activity, spider data, notifications | Medium | ✅ Done (Session 459) |
| Autonomous Intelligence Loop | Background monitoring (SEC, jobs, content) | High | ✅ Done (Session 460) |
| **Blockchain Audit Agents** | **Autonomous blockchain security monitoring** | **High** | **In Progress (Session 461)** |

---

## Bigger Picture Questions

### What's the main use case?
- Content creation (images, video, audio, 3D)?
- Voice cloning marketplace?
- Agent-powered research and analysis?
- Discord bot for community?

### Revenue Angle
- Voice marketplace ready (70/30 split)
- Content factory has pricing tiers ($5-$50K)
- Service for others vs personal content creation?

### Discord vs Web Priority
- 29 Discord commands available
- Full web UI at /ai-studio/
- Which audience matters more?

---

## Feature Ideas

### Automation & Scheduling
- [ ] Scheduled content generation (daily/weekly automated runs)
- [ ] Auto-post to social media platforms
- [ ] Recurring spider crawls with notifications

### Agent Enhancements
- [ ] Agent "personalities" affecting output style
- [ ] Agent memory of user preferences across sessions
- [ ] Agent collaboration improvements

### User Experience
- [ ] Onboarding wizard for new users
- [ ] Quick actions / favorites on dashboard
- [ ] Mobile-friendly PWA version

### Content Pipeline
- [ ] Batch content generation
- [ ] Content calendar view
- [ ] Asset library with tagging/search

### Integration Ideas
- [ ] YouTube direct upload
- [ ] TikTok integration
- [ ] Shopify product image generation

---

## Technical Debt

- [ ] Test coverage improvements
- [ ] Performance optimization audit
- [ ] Documentation for external developers

---

## Notes

Add notes here as ideas come up during development sessions.

### Session 461 Notes (Blockchain Audit)
- **Blockchain Audit Agent Group** - Autonomous security monitoring for blockchain ecosystems
- **New Agents:** SmartContractAuditorAgent, TransactionMonitorAgent, WhaleWatcherAgent, ExploitDetectorAgent
- **New Spiders:** EtherscanAPISpider (real txs), DefiLlamaSpider (TVL), RektNewsSpider (exploits)
- **Leverages:** Existing autonomous loop, CodeReviewAgent, Discord notifications
- **Goal:** 24/7 blockchain security nervous system with Discord alerts

### Session 460 Notes (Autonomous Loop)
- **Autonomous Intelligence Loop** - The conductor that makes everything work together
- **Components:** SEC filing alerts, content scanner, job scanner
- **Celery Beat:** 15-min full cycle, 5-min SEC (market hours), daily digest at 8 AM
- **Foundation for:** Blockchain audit, advisor intelligence, content pipeline

### Session 459 Notes
- **Landing Page Overhaul** - Completely redesigned Assistant Tab to show FULL platform capabilities (not just content creation)
- **"While You Were Away"** - Personalized greeting with activity summary since last visit
- **API Key Audit** - Documented all external services: SEC (FREE!), Polygon, Alpha Vantage, Finnhub, etc.
- **Platform Positioning** - This is an AI Intelligence Platform, not just content creation!

### Session 458 Notes
- **Assistant Tab (Landing Page)** - Review and improve the main landing page experience. Currently the first thing users see when they load the app. Could be more engaging/useful.
- **Voice Output** - Implemented! 🔊 Speak button on chat messages using ElevenLabs + cloned voice.

