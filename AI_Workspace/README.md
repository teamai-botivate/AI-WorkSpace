# Botivate AI Workspace — Unified Architecture

**One backend, one frontend, multiple AI agents as plugins.**

Any company clones it, fills in their keys, deploys with one command, and gets their own branded AI workspace.

## Quick Start

```bash
# 1. Clone & configure
cp .env.example .env     # Edit with your API keys

# 2. Install dependencies
cd backend && pip install -r requirements.txt && cd ..
cd frontend && npm install && cd ..

# 3. Run
.\start-dev.ps1          # Windows
# OR manually:
# Terminal 1: uvicorn backend.app.main:app --reload --port 8000
# Terminal 2: cd frontend && npm run dev
```

Open http://localhost:3000 — you'll see the dashboard with all active agents.

## Architecture

```
AI_Workspace/
├── .env.example              ← All API keys template
├── workspace.config.json     ← Branding + agent control
├── docker-compose.yml        ← One-command deploy
├── credentials/              ← Google OAuth, service accounts
├── backend/
│   ├── requirements.txt      ← One combined file
│   └── app/
│       ├── main.py           ← Single FastAPI entry point
│       ├── config.py         ← Loads .env + config
│       ├── plugin_loader.py  ← Auto-discovers agents
│       ├── core/             ← Shared services (auth, email, LLM, Sheets)
│       └── agents/
│           ├── hr_support/       ← Plugin: Leave, RAG, Approvals
│           └── resume_screening/ ← Plugin: JD Gen, Screening, Email
├── frontend/
│   └── src/
│       ├── App.tsx           ← Dashboard + lazy routing
│       ├── components/       ← Shared UI (Header, Cards)
│       └── agents/           ← Per-agent React pages
└── docs/                     ← Deployment, Credentials, Customization
```

## How Plugin Loading Works

1. Server starts → `plugin_loader.py` scans `backend/app/agents/`
2. Each valid folder must have `agent.json` + `__init__.py` (exports `router`)
3. Validates required API keys from `.env`
4. Mounts router at `/api/{agent_name}/`
5. Frontend calls `GET /api/agents` → renders agent cards on dashboard

## Adding an Agent

1. Create `backend/app/agents/your_agent/`
2. Add `agent.json` + `__init__.py` with a FastAPI router
3. Optionally add `frontend/src/agents/your_agent/index.tsx`
4. Restart — agent appears on dashboard automatically

## Removing an Agent

Delete the folder, or set `"enabled": false` in `agent.json`. Zero code changes.

## Production Deploy

```bash
docker-compose up -d --build
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for full guide.

## Current Agents

| Agent | Status | Description |
|-------|--------|-------------|
| HR Support | ✅ Active | Leave management, policy RAG, approval workflows |
| Resume Screening | ✅ Active | JD generation, multi-stage resume screening, email automation |

## Tech Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy (async), ChromaDB, LangChain
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
- **LLMs:** OpenAI GPT-4o-mini, Groq (Llama 3.1)
- **Deploy:** Docker, Nginx, Docker Compose
