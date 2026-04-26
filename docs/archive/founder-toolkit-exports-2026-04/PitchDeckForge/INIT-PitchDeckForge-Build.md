# INIT-PitchDeckForge-Build

_Workspace: PitchDeckForge · ID: 07eacdf5-9788-45c3-9bc7-eb9c9c29c565 · Created: 2026-04-06 · Updated: 2026-04-15_

Owner: claude-code
Tasks:
- Repo scaffold (FastAPI + React/Vite/Tailwind)
- DB models & migrations (users, projects, briefs, decks, exports)
- /api/v1/decks/generate endpoint wiring to LLM generator stub
- Slides JSON render component + export-to-PDF endpoint
- CI: lint -> docker build -> smoke curl /health
- .env.example and README Surprise Test
Estimates: scaffold + generator stub 6–10 hours.
Acceptance: generate returns slides JSON (>=6 slides) + PDF export endpoint works.