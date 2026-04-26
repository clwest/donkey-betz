# README - 2-minute Quick Start & Surprise Test

_Workspace: PitchDeckForge · ID: ac97d633-bfe3-42bb-be20-bea7d4a305b3 · Created: 2026-04-06 · Updated: 2026-04-15_

2-minute Quick Start:
- git clone <repo_url>
- cp .env.example .env and fill DATABASE_URL, SECRET_KEY, OPENAI_API_KEY
- Backend: uvicorn app.main:app --reload
- Frontend: cd frontend && yarn && yarn dev
- Open http://localhost:3000 and sign in with demo@example.com / password
Surprise Test (curl):
- POST /api/v1/health -> expect 200
- POST /api/v1/<primary_generate_endpoint> (sample body) -> expect 200 + id
Notes: Attach demo creds, repo link, and .env.example in workspace.