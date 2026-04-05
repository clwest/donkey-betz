# Next Session — Start Here

**Date:** April 5, 2026
**Previous Session:** Business plan fixes + Ironwood Protocol gameplay overhaul
**PA Conversation:** pa-c95ff6e96bd6
**Status:** 218 Agents | 80 Spiders | 25 Advisors | PA function calling LIVE (GPT-5.2) | 9 standalone apps + RTS game

---

## What Was Done This Session

### Business Plans — ALL 9 COMPLETE
- Fixed MentorForge, SignalStudio, Ironwood Protocol, ComplianceSentinel business plans (had placeholder text)
- ScoutPlays was already good (12K chars)
- All 4 fixed plans now have real content + correct workspace FK assignments
- PR #1816: Added workspace_id to deliverable detail API response

### Ironwood Protocol — Major Gameplay Overhaul (5 commits)
1. **A* pathfinding** — units navigate around water/rocks instead of getting stuck
2. **All 5 modules working:**
   - Pulse: AoE damage to all enemies in range
   - EMP: disables target 20 ticks (can't move/attack) + visual indicator
   - Support: deploys temporary auto-turrets every 200 ticks
   - Repair: heals ALL nearby allies + buildings (not just one)
   - Ballistic: can now target buildings too
3. **Strategic AI:** build orders, counter-picks, retreat logic, defensive turrets, double production
4. **Resource economy fix:** generators work for players (+4E +2B/tick), faster tick rate (3s), visible income
5. **Mission 1 instant-win bug FIXED:** enemyHadHQ flag persisted from createGameState default
6. **Resource UX overhaul:** bigger HUD, node capture notifications, contextual progressive hints
7. **Guided gameplay:** step-by-step hints panel, better briefing, training UI with tooltips, SUP module button added

### Sprite Generation — COMPLETE
- 15/15 sprites generated via SD3 (digital sci-fi style), all clean top-down views
- Management command: `python manage.py generate_ironwood_sprites` (reusable)
- Manifest: `ironwood_sprite_manifest.json` with all URLs
- Sprites integrated into Ironwood engine with team-color multiply tinting
- New files: `sprites.ts` (loader + tinter), modified `engine.ts` + `App.tsx`
- TypeScript clean, Vite build passes
- Sprites are 1024x1024 originals — need downsizing to 64x64 for production

## Accounts

- `donkeyking` (Chris) — superuser/owner
- `jessica` — superuser, business side
- `jeremy` — superuser, patent lawyer
- All apps: demo user with password `demo123`

## PRIORITY 1: Ironwood Protocol Sprites — DONE
- ~~Pull manifest~~ DONE — 15/15 sprites generated and manifest saved
- ~~Integrate into game engine~~ DONE — sprites.ts + engine.ts + App.tsx modified
- Remaining: downsize 1024x1024 originals to 64x64, convert to WebP, playtest tinting

## PRIORITY 2: Ironwood Protocol Polish
- Playtest remaining campaign missions (2-6)
- AI balance tuning
- Audio system (SFX + music)
- Multiplayer testing with 2 browser tabs

## PRIORITY 3: Platform Carryover
- Content Packets UI — packet detail page
- Evidence Cards monitoring
- Rewrite quality improvements
- Duplicate dispatch rate limiting

## Known Issues

### Sprite Pipeline — RESOLVED
- ~~ImageAgent generates concept art sheets~~ FIXED: bypass GPT prompt rewriting, call _execute_generate_image directly with strict prompts
- ~~1 image per run~~ SOLVED: management command loops through 15 entities individually
- Sprites at 1024x1024 need downsizing for production (bandwidth)

### Apps — Deployment Parked
- All 9 apps run locally only — no Railway/Vercel deploys yet
- GitHub repos created and pushed but no CI/CD

## How to Start Ironwood Protocol

```bash
cd ~/development/ironwood-protocol
bash start.sh
# Backend: http://localhost:8009
# Frontend: http://localhost:5181
# Demo: demo@ironwood.dev / demo123
```

## How to Work with Rigby

```bash
python tools/pa_chat.py "your message" --tools --conversation pa-c95ff6e96bd6
```

## Troubleshooting

```bash
# Kill all app servers
pkill -f uvicorn; pkill -f vite

# Full platform restart
pkill -f daphne; pkill -f redis; pkill -f celery
rm -f .daphne.pid .celery.pid .celery-beat.pid
make start && make celery
```
