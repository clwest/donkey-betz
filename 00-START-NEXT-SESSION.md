# Next Session — Start Here

**Date:** April 8, 2026
**Previous Session:** Founder Toolkit Cross-App Flow + Build Planning Mode + UI Polish
**PA Conversation:** Create fresh — use Rigby's starter template below
**Status:** 226 Agents | 86 Spiders | 25 Advisors | 4 Founder Toolkit apps LIVE with Stripe | Build Planning mentors added | 21 PRs merged this session

---

## What Was Done (April 7-8, 2026) — 21 PRs Merged

### Main Platform (donkey-betz-platform)
- **PR #1842** — Fix: staff users (Jessica) can view any deliverable detail (403 fix)

### Founder Toolkit — Cross-App Data Flow (all 4 apps)
- Shared `founder_projects` table connecting MentorForge → PitchDeckForge → DealFlowTracker → Contract Concierge
- Each app exports/imports via the shared table with stage progression
- PitchDeckForge import crash fix (brief.project relationship)

### MentorForge (7 PRs: #1-7)
- **Cross-app data flow** — Export to Project button in chat
- **AI Mentor Recommendation** — "Find Your Perfect Mentor" search box, 40+ keyword mappings, GPT-5-mini rationale, color-coded scores
- **Chat UX Polish** — Pinned mentor card, live session timer, auto-resize textarea, Shift+Enter
- **Pro tier fix** — gpt-5.2 streaming params (max_completion_tokens), Chris upgraded to pro
- **Build Planning Mode** — 2 new mentors (Alex Rivera MVP Architect, Nina Kowalski Product Designer), build_planning session mode, structured JSON spec output
- **Download Build Spec** — Extracts JSON spec from conversation, downloadable button in chat
- **Tailwind JIT fix** — Static classes replacing dynamic interpolation

### PitchDeckForge (6 PRs: #1-6)
- Cross-app import from founder project
- Import preview panel (mentor notes + template picker)
- 5-step progress stepper
- Tailwind JIT fix

### DealFlowTracker (4 PRs: #1-4)
- Cross-app import from founder project
- 5-step progress stepper
- Tailwind JIT fix

### Contract Concierge (4 PRs: #1-4)
- Cross-app import from founder project with contract prefill
- 5-step progress stepper
- Tailwind JIT fix

---

## PRIORITY 1: Test the Full Flow (THIS SESSION)

### Steps to test:
1. **Seed build mentors** — run in browser console on MentorForge:
   ```javascript
   fetch('https://mentorforge-bj25.onrender.com/api/admin/seed-build-mentors', {
     method: 'POST',
     headers: { Authorization: `Bearer ${localStorage.getItem('mf_token')}` }
   }).then(r => r.json()).then(console.log)
   ```
2. **MentorForge** — Find mentor → Start session → Chat → Export to Project
3. **PitchDeckForge** — Import from Mentor → Preview → Generate Deck → Export PDF
4. **DealFlowTracker** — Import from Project → Create Deal
5. **Contract Concierge** — Import from Project → Create Contract
6. **Build Planning** — Find Alex Rivera → Start Build Planning session → Describe app → Download Build Spec

### Demo Recording
- Canonical demo script ready (initiative fc0d398b)
- Teleprompter script + SRT captions prepared by Rigby
- GreenRoots Community Gardens nonprofit example ($250k seed raise)
- Target runtime: ~2:55

## PRIORITY 2: AppForge Concept (Future)

### The Big Idea
Add a "Build MVP" step: ① Mentor → ② **Build** → ③ Deck → ④ Pipeline → ⑤ Contracts

- Near-term: Mentor exports structured build spec → founder brings to Claude Code CLI → app scaffolded and deployed
- Long-term: claude_code_engineer on Railway does it autonomously (needs Anthropic API credits)
- Full investigation done with Rigby — see PA conversation pa-d82ae92a6a52

### What's Built for This
- 2 Build Planning mentors (Alex Rivera, Nina Kowalski)
- build_planning session mode with JSON spec output
- Download Build Spec button
- founder_projects.build_spec field
- 5-step progress stepper showing Build step

## PRIORITY 3: Backlog

- Deploy remaining 5 apps (SellerPilot, SignalStudio, ScoutPlays, ComplianceSentinel, Ironwood)
- Attachments upload for Packs (initiative eb551452 — ON_HOLD)
- Spider embedding backlog (20% → target 80%)
- Initiative pipeline (0 completed → needs auto-approve)

---

## Accounts

- `donkeyking` (Chris) — superuser/owner, pro tier on MentorForge
- `jessica` — superuser, business side
- `jeremy` — superuser, patent lawyer

## How to Work with Rigby

```bash
# Create a fresh conversation first, then:
python tools/pa_chat.py "message" --tools --conversation <NEW_CONVERSATION_ID>

# Local
bash tools/pa_local.sh "message"
```

## Founder Toolkit Repos
- Landing: github.com/clwest/founder-toolkit
- MentorForge: github.com/clwest/mentorforge (Render: mentorforge-bj25.onrender.com)
- PitchDeck: github.com/clwest/pitchdeckforge
- DealFlow: github.com/clwest/dealflowtracker
- Contracts: github.com/clwest/contract-concierge

## Stripe
- Payment Link ($299 Sprint): https://buy.stripe.com/5kQ7sM9CwdgAcPIerc14400
- Dashboard: https://dashboard.stripe.com
