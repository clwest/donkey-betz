# Next Session — Start Here

**Date:** April 4, 2026
**Previous Session:** Massive pipeline overhaul — 25 PRs, Evidence Cards, Content Packets, focused rewrite, editor gatekeeper
**PA Conversation:** Ask Chris for conversation ID
**Status:** 218 Agents | 80 Spiders | 25 Advisors | PA function calling LIVE (GPT-5.2) | Workspaces LIVE | Newsletter Pipeline LIVE with Evidence Cards

---

## What Was Built Last Session (25 PRs)

### Pipeline Overhaul (PRs #1788-1812)
- **Docs audit** — fixed stale counts across 8 docs (agents 92→84, workers 7→9, routes 26→69)
- **LLM upgrade** — gpt-4o-mini → gpt-5.2 in 4 live code files
- **Pipeline UX** — dismiss/clear stale runs, history dropdown, brief save confirmation, workspace list all types
- **Stage detail API** — expandable stages showing tools, sources, deliverable preview
- **DistributionAgent fixes** — slice crash on dict content, context defaults, deliverable fetch
- **WorkflowAgent deliverable saving** — sub-agent results now saved as deliverables
- **Tool synthesis** — 9 agents now synthesize tool results instead of dumping raw "Count: 0"
- **GPT-crafted pipeline prompts** — replaces rigid templates with intelligent briefings
- **ResearchAgent brief topic** — searches the actual brief topic, not generic task string
- **Footnote citations** — [1] [2] style with Sources section at bottom
- **EditorAgent gatekeeper** — 5 quality checks (topic alignment, hook enforcement, audience relevance, actionability, evidence quality) with PASS/FAIL behavior
- **ContentWriterAgent brief enforcement** — hook MUST open the article, audience/tone/notes as NON-NEGOTIABLE requirements
- **Content Packets** — deliverables grouped by pipeline run (ContentPacket + ContentPacketItem models, API, frontend UI)
- **Final Rewrite stage** — receives editor + fact check feedback, produces corrected draft
- **Focused rewrite mode** — skips heavy context injection, uses only draft + feedback + brief
- **JSON recovery** — writer recovers content as plain text when JSON parse fails, 16k token limit
- **Evidence Cards MVP** — extracts structured citable evidence from research (claim + excerpt + source + confidence)
- **Evidence Cards timeout fix** — card generation runs at pipeline level with 60s cap, not inside stage timeout
- **Brief saves as deliverable** — versioned tracking of workspace briefs
- **Superuser workspace access** — Jessica/Jeremy can see all workspaces

### New Workspace
- **Operator Edge — AI Newsletter Studio** (id: 4b5d4df8) — first run completed successfully with Rigby's voice

### Pipeline Architecture (Current)
```
Topic Mining + Deep Research (parallel, discovery group)
  → Quality Gate (topic alignment + research depth)
  → Evidence Cards (60s timeout, pipeline level)
  → Content Strategy
  → Write Draft (brief enforcement, Evidence Cards, 16k tokens)
  → Edit & Polish + Fact Check (parallel, review group)
  → Final Rewrite (focused mode — draft + feedback + brief only)
  → SEO & Headlines
  → Hooks & Distribution
  → Review & Approve (human)
  → Publish
```

## Accounts

- `donkeyking` (Chris) — superuser/owner
- `jessica` — superuser, business side, now has access to all workspaces
- `jeremy` — superuser, patent lawyer

## Key Rules (from memory)

- **Vertical slice:** Every feature ships backend + API + frontend + demo. Nothing is done until visible in UI.
- **Last mile UI:** If Chris can't see it in the browser, it's not done.
- **Rigby collaboration:** Read Rigby's FULL responses, answer every question, agree on plan BEFORE building.
- **Workspace assignment:** All deliverables go to a workspace (default: Donkey Betz).
- **Rigby-first comms:** Route questions through Rigby via `python tools/pa_chat.py`.

## How to Work with Rigby (CRITICAL — read this)

Rigby is the PA (Personal Assistant). She runs on GPT-5.2 with 130+ tools.

**How to communicate:**
```bash
python tools/pa_chat.py "your message" --tools --conversation <conversation_id>
```

## Known Issues / Next Steps

- **Content Packets UI** — packets display on dashboard but "View" links go to flat deliverables list instead of packet detail view. Needs dedicated packet detail page.
- **Editor FAIL → Rewrite loop** — editor fails draft, rewrite stage runs, but rewrite only makes editorial changes, not structural. Need stronger rewrite instructions or iterative retry.
- **Evidence Cards validation** — Rigby setting up gates (cards >= 6, unique domains >= 3). Monitor first 10 runs for card quality.
- **Rigby's voice** — Operator Edge newsletter uses Rigby's POV. She should sound human, not AI. No "As an AI..." disclaimers.
- **Pipeline stage UI** — stages show on dashboard but deliverable viewing experience needs work. Content Packets should be the primary way to browse pipeline output.
- **Distribution deliverables** — sometimes show raw JSON instead of formatted markdown. Content extractor updated but needs verification.

## Troubleshooting

```bash
# Full restart
pkill -f daphne; pkill -f redis; pkill -f celery
rm -f .daphne.pid .celery.pid .celery-beat.pid
make start && make celery

# Kill stuck pipeline run
railway run python manage.py shell -c "
from core.models_workspace_templates import PipelineRun
from django.utils import timezone
runs = PipelineRun.objects.filter(workspace_id='WORKSPACE_ID', status='running')
for r in runs:
    r.status = 'failed'
    r.error_message = 'Manually killed'
    r.finished_at = timezone.now()
    r.save(update_fields=['status', 'error_message', 'finished_at'])
"
```
