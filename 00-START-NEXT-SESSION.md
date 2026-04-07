# Next Session — Start Here

**Date:** April 7, 2026
**Previous Session:** Platform Audit Complete + Founder Toolkit Live + Marketing Prep
**PA Conversation:** pa-d19c1674b936
**Status:** 226 Agents | 86 Spiders | 25 Advisors | 4 Founder Toolkit apps LIVE with Stripe | Landing page LIVE | 5 more apps ready to deploy

---

## What Was Done (April 6-7, 2026)

### Founder Toolkit — LIVE with Stripe Payments
| App | URL | Stripe | Status |
|-----|-----|--------|--------|
| **PitchDeckForge** | pitchdeckforge.vercel.app | $29/mo Pro, $79/mo Team | LIVE |
| **MentorForge** | mentorforge.vercel.app | $19/mo Pro, $49/mo Enterprise | LIVE |
| **DealFlowTracker** | dealflowtracker.vercel.app | $39/mo Pro, $99/mo Fund | LIVE |
| **Contract Concierge** | contract-concierge-pi.vercel.app | $29/mo Pro, $79/mo Business | LIVE |
| **Landing Page** | founder-toolkit.vercel.app | $299 Sprint (Stripe Payment Link) | LIVE |

**All apps share:** One PostgreSQL database, one login (SSO), Founder Toolkit cross-app nav bar, shared SECRET_KEY

### Apps Ready to Deploy (5 more)
| App | Repo | Status |
|-----|------|--------|
| SellerPilot | clwest/sellerpilot | Ready — pushed to GitHub |
| SignalStudio | clwest/signal-studio | Ready — pushed to GitHub |
| ScoutPlays | clwest/scoutplays | Ready — pushed to GitHub |
| ComplianceSentinel | clwest/compliancesentinel | Ready — pushed to GitHub |
| Ironwood Protocol | clwest/ironwood-protocol | Ready — deployed to Vercel + Render |

### 12-Dossier Platform Audit — COMPLETE
All 12 dossiers verified. 44 resolved, 31 design questions, 5 confirmed gaps, 0 open.
Location: `docs/audit-2026/`

### Key Platform Fixes
- Learning loop: XP bonuses applied, pattern decay added, SharedKnowledge consumption tracked
- Model selection: gpt-5.2 for tool-calling agents (gpt-5-mini was failing)
- Agent dedup guard, superuser workspace access, deliverable ownership
- PA thumbs up/down feedback, spider dynamic reliability, advisor injection
- A/B testing command: `python manage.py test_prompt_layer`
- 226 agents seeded to production (was 39)

### PitchDeckForge Improvements
- Target Market + Business Model fields added to brief
- Bonus slides use gpt-5.2 for clean JSON
- PDF export: proper text wrapping, Q&A formatting (Q on top, A below), continuation pages
- Slide delete button
- 4 deck strategies: Clean, Investor, Growth, Product-Led

---

## PRIORITY 1: Marketing & Revenue (THIS SESSION)

### Rigby's GTM Strategy
- **Sell:** "Fundraising Sprint Stack" — $299 one-time or $49/mo
- **Target:** Pre-seed/seed founders actively raising
- **Channels:** LinkedIn DMs (50-100/day), partner intros, founder communities
- **Copy:** "I'll get your raise materials investor-ready in 48h"
- **Demo video:** Record with OBS, 3 minutes, outcome-first

### Landing Page Live
- URL: https://founder-toolkit.vercel.app
- $299 Sprint button → Stripe Payment Link (LIVE)
- Demo video placeholder ready for embed
- Honest copy (verified claims only)

### Next Steps
1. **Record demo video** — show PitchDeck → DealFlow → Contract → Mentor flow
2. **Embed video** on landing page
3. **Send 30 outbound DMs** to founders raising on LinkedIn
4. **Post on** r/startups, Indie Hackers, X
5. **Contact accelerator mentors** for referral partnerships

## PRIORITY 2: Use Rigby as Marketing Assistant

Next session focus: Work WITH Rigby in production (not development) to:
- Write video scripts
- Draft DM templates for different audiences
- Create social media posts
- Analyze which pitch angles work best
- Track outreach results

## PRIORITY 3: Platform Improvements (if time)

- Deploy remaining 5 apps to Vercel/Render
- Spider embedding backlog (20% → target 80%)
- Re-enable agent scheduled runs
- Initiative pipeline (0 completed — needs auto-approve)
- Workspace UI tab fixes (ongoing)

---

## Accounts

- `donkeyking` (Chris) — superuser/owner
- `jessica` — superuser, business side
- `jeremy` — superuser, patent lawyer

## How to Work with Rigby

```bash
# Production (Railway)
python tools/pa_chat.py "message" --tools --conversation pa-d19c1674b936

# Local
bash tools/pa_local.sh "message"
```

## Local Development Setup

```bash
make start && make celery
# PA worker: OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES celery -A core worker -l info --pool=threads -c 2 -Q pa
```

## Founder Toolkit Repos
- Landing: github.com/clwest/founder-toolkit
- PitchDeck: github.com/clwest/pitchdeckforge
- MentorForge: github.com/clwest/mentorforge
- DealFlow: github.com/clwest/dealflowtracker
- Contracts: github.com/clwest/contract-concierge

## Stripe
- Payment Link ($299 Sprint): https://buy.stripe.com/5kQ7sM9CwdgAcPIerc14400
- Dashboard: https://dashboard.stripe.com
- Price IDs set on each Render service as env vars
