# Botivate — AI Workforce Portal

> **One platform. Every department. AI-powered.**

![Version](https://img.shields.io/badge/version-1.0.0-6366f1)
![Agents](https://img.shields.io/badge/agents-2%20active%20%7C%205%20planned-green)
![Stack](https://img.shields.io/badge/stack-React%20%2B%20FastAPI%20%2B%20LangGraph-blue)

---

## Vision & Idea

**Botivate** is a **unified AI Workforce Management Portal** that replaces manual, disconnected department workflows with intelligent, autonomous AI agents — all accessible from a single dashboard.

### The Problem

In most organizations, every department (HR, Sales, Production, Maintenance, Operations) runs its own tools, spreadsheets, and manual processes. There is no single view, no cross-department intelligence, and no automation connecting them.

### Our Solution

A **config-driven micro-frontend architecture** where:

- Each **department** gets its own **AI Agent** (independent backend + frontend)
- All agents are orchestrated through a **single portal** (the Botivate Shell)
- A **Super Agent** (planned) will connect all agents for cross-department intelligence
- **Zero hardcoding** — adding a new agent = 1 folder + 1 config entry
- Supports both **local** and **cloud-deployed** agents simultaneously

### Target Users

| Role | AI Agents Serving Them |
|------|----------------------|
| HR Teams | Automated recruiting, employee support, leave management |
| Production Managers | Order-driven production planning, stock alerts |
| Sales Teams | Lead tracking, complaint handling, service automation |
| Maintenance | Asset tracking, preventive schedules, spare parts |
| Operations / MIS | Real-time dashboards, auto-generated reports |
| Leadership | Super Agent — cross-department insights & actions |

---

## Architecture

```
┌───────────────────────────────────────────────────────────┐
│              Botivate Frontend Shell (React:3000)          │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│   │ Agent    │  │ Agent    │  │ Agent    │  ...           │
│   │ Card 1   │  │ Card 2   │  │ Card N   │               │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│        │iframe       │iframe       │iframe                │
│   ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐               │
│   │ Agent 1  │  │ Agent 2  │  │ Agent N  │               │
│   │ Frontend │  │ Frontend │  │ Frontend │               │
│   └──────────┘  └──────────┘  └──────────┘               │
└────────────────────────┬──────────────────────────────────┘
                         │ /api/*
                ┌────────▼────────┐
                │  Gateway API    │
                │  (FastAPI:9000) │
                └────────┬────────┘
                         │ reads
                ┌────────▼────────┐
                │ workspace       │
                │ .config.json    │  ← Single Source of Truth
                └─────────────────┘
```

**Design Principles:**

| Principle | How |
|-----------|-----|
| Config-Driven | `workspace.config.json` controls all ports, URLs, features, status |
| Micro-Frontend | Each agent frontend runs in an iframe, fully isolated |
| Independent Agents | Each agent has its own backend, frontend, venv, dependencies |
| Hybrid Deployment | Agents can run locally OR be deployed remotely (Render, AWS) |
| Gateway Pattern | Central API for config, health checks, agent discovery |
| One-Click Launch | `start-dev.ps1` reads config and starts everything |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend Shell | React 18 + TypeScript 5 + Vite 6 + Tailwind 3 | Main portal UI |
| Gateway | FastAPI + httpx + Pydantic | Config server, health checks |
| Agent Backends | FastAPI + LangChain/LangGraph + OpenAI GPT-4o | Individual AI services |
| Agent Frontends | React / Vanilla JS / Any framework | Loaded via iframe |
| Vector DB | ChromaDB | RAG and semantic search |
| LLM | OpenAI GPT-4o | AI analysis, chat, generation |
| NLP | spaCy + HuggingFace BART-large-MNLI | Resume parsing, role matching |
| Launcher | PowerShell (`start-dev.ps1`) | One-click startup |

---

## Project Structure

```
AI_Workspace/
├── README.md                          # This file
├── SETUP.md                           # Installation & setup guide
├── AGENT_INTEGRATION_GUIDE.md         # How to add new agents
├── PROGRESS.md                        # Completed vs remaining work
├── TODO.txt                           # Detailed task breakdown
├── start-dev.ps1                      # One-click dev launcher
├── .gitignore                         # Master ignore rules
│
├── config/
│   └── workspace.config.json          # SINGLE SOURCE OF TRUTH
│
├── backend/                           # Gateway API (port 9000)
│   ├── requirements.txt
│   └── app/
│       ├── main.py                    # Gateway endpoints
│       └── config.py                  # Config loader
│
├── frontend/                          # Main Shell (port 3000)
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx                    # Dashboard ↔ Agent Shell router
│       ├── context/WorkspaceContext   # Config provider (fetches /api/config)
│       ├── types/workspace.types.ts   # All TypeScript interfaces
│       ├── components/
│       │   ├── layout/Header.tsx      # Navigation bar
│       │   ├── dashboard/             # Dashboard, AgentCard, StatsBar, WelcomeBanner
│       │   ├── agent/AgentShell.tsx   # Iframe wrapper + health toolbar
│       │   └── common/               # Loading, Error, ComingSoon screens
│       └── utils/iconMap.ts           # Lucide icon resolver
│
├── Resume-Screening-Agent/            # Agent 1: HR Recruiter (LOCAL)
│   ├── Backend/                       # FastAPI unified server (port 8000)
│   ├── Frontend/                      # Vanilla JS UI
│   ├── JD_Generator/                  # Sub-tool: JD creation
│   └── Aptitude_Generator/            # Sub-tool: Test generation
│
└── HR_Support/                        # Agent 2: HR Support (DEPLOYED)
    ├── backend/                       # FastAPI + LangGraph + RAG
    └── frontend/                      # React + Vite
```

---

## Quick Start

```powershell
# 1. Clone the repository
git clone https://github.com/teamai-botivate/AI-WorkSpace.git
cd AI-WorkSpace

# 2. Install (see SETUP.md for full details)
cd frontend; npm install; cd ..

# 3. Launch everything
.\start-dev.ps1

# 4. Open browser → http://localhost:3000
```

> **Full installation guide:** [SETUP.md](SETUP.md)
>
> **Add your own agent:** [AGENT_INTEGRATION_GUIDE.md](AGENT_INTEGRATION_GUIDE.md)
>
> **Track progress:** [PROGRESS.md](PROGRESS.md)

---

## Active Agents

### 1. HR Recruiter & Screener — Local (Port 8000)

| Feature | Description |
|---------|-------------|
| JD Generator | AI-powered Job Description creation from simple inputs |
| Resume Screening | Upload resumes, AI scores/ranks/shortlists candidates |
| Aptitude Generator | Auto-generate technical assessments for shortlisted candidates |
| Email Automation | Gmail integration for interview invites and rejections |
| Scoring Engine | Zero-Shot NLI + Vector Embeddings + GPT-4o Deep Read |

### 2. HR Employee Support — Deployed on Render

| Feature | Description |
|---------|-------------|
| Leave Management | Apply, approve, reject leaves with AI assistance |
| Policy RAG | Upload policies, chatbot answers employee questions |
| Approval Workflows | Multi-level approval chains powered by LangGraph |
| Employee Lifecycle | Onboarding, transfers, exits managed by AI |
| Grievance System | File and track employee grievances |

---

## How It Works

1. **`workspace.config.json`** defines all agents (ports, URLs, features, deployment status)
2. **Gateway** reads config and exposes it via REST API (`/api/config`, `/api/agents`)
3. **Frontend Shell** fetches config on load → renders agent cards on dashboard
4. **User clicks an agent** → Shell loads that agent's frontend in an iframe
5. **Health monitoring** — Gateway polls each agent's health endpoint
6. **Deployed agents** → iframe points to the remote URL (e.g., Render) instead of localhost

---

## Gateway API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/config` | Full workspace configuration |
| `GET` | `/api/health` | Gateway health check |
| `GET` | `/api/agents` | List all active agents |
| `GET` | `/api/agents/{id}` | Get specific agent config |
| `GET` | `/api/agents/{id}/health` | Check specific agent health |
| `GET` | `/api/agents/health/all` | Health status of all agents |

Interactive docs: `http://localhost:9000/docs`

---

## Adding a New Agent

No code changes to the shell or gateway required.

1. Create your agent folder with backend + frontend
2. Add **one entry** to `config/workspace.config.json`
3. Run `start-dev.ps1` — it auto-discovers and launches your agent

> **Full guide with examples:** [AGENT_INTEGRATION_GUIDE.md](AGENT_INTEGRATION_GUIDE.md)

---

## Scripts

| Command | What it does |
|---------|-------------|
| `.\start-dev.ps1` | Start all services (reads config dynamically) |
| `.\start-dev.ps1 -Stop` | Kill all running services |
| `cd frontend && npm run dev` | Start only the frontend shell |
| `cd backend && uvicorn app.main:app --port 9000 --reload` | Start only the gateway |

---

## Environment Variables

Each agent has its own `.env` file (never committed). Common variables:

| Variable | Used By | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | All AI agents | OpenAI API key |
| `GOOGLE_API_KEY` | Resume Screener | Gmail API credentials |
| `VITE_API_URL` | HR Support FE | Backend URL |
| `DATABASE_URL` | HR Support BE | PostgreSQL connection |

---

## Team

**TeamAI Botivate** — Building the future of AI-powered workforce management.

GitHub: [github.com/teamai-botivate](https://github.com/teamai-botivate)
