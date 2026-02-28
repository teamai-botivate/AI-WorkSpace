# Agent Integration Guide

> How to add a new AI agent to the Botivate Workspace — step by step.

**Time required:** ~15 minutes for an existing backend+frontend.

---

## Overview

The Botivate system is **config-driven**. To add a new agent you need:

1. An agent folder with a **backend** (FastAPI recommended) and a **frontend** (any framework)
2. **One JSON entry** in `config/workspace.config.json`

That's it. No changes to the gateway, shell, or launcher.

---

## Step 1: Create Your Agent Folder

```
AI_Workspace/
└── my-new-agent/
    ├── backend/
    │   ├── requirements.txt
    │   ├── .env                   # Your secrets (never committed)
    │   └── app/
    │       └── main.py            # FastAPI app
    └── frontend/
        ├── package.json           # (if React/Vite)
        └── index.html
```

### Backend Requirements

Your backend MUST:
- Expose a **health check endpoint** (e.g., `/docs`, `/health`, or `/api/health`)
- Run on a **unique port** (check existing ports below)
- Be startable via a **single command** (e.g., `uvicorn app.main:app --port 8005`)

### Frontend Requirements

Your frontend MUST:
- Be **accessible via a URL** (localhost or deployed)
- Work correctly when **loaded inside an iframe**
- Run on a **unique port** (or be served by the backend)

### Port Registry (Reserved)

| Port | Used By |
|------|---------|
| 3000 | Frontend Shell (React + Vite) |
| 8000 | HR Recruiter & Screener (Resume-Screening-Agent) |
| 8001 | HR Employee Support (when running locally) |
| 9000 | Gateway API |
| 8002 | *Available — Production Agent* |
| 8003 | *Available — Sales Agent* |
| 8004 | *Available — Maintenance Agent* |
| 8005 | *Available — Operations/MIS Agent* |
| 8006 | *Available — Super Agent* |

---

## Step 2: Add Config Entry

Open `config/workspace.config.json` and add an entry to the `agents` array:

```json
{
  "id": "my-agent",
  "name": "My New Agent",
  "description": "What this agent does in one line",
  "icon": "Bot",
  "gradient": ["#f59e0b", "#d97706"],
  "status": "active",
  "category": "Department Name",
  "features": ["Feature 1", "Feature 2", "Feature 3"],
  "backend": {
    "port": 8005,
    "healthCheck": "/docs",
    "startCommand": "uvicorn app.main:app --port 8005 --reload",
    "workDir": "my-new-agent/backend",
    "envFile": "my-new-agent/backend/.env",
    "activateVenv": "my-new-agent/backend/.venv/Scripts/Activate.ps1"
  },
  "frontend": {
    "port": 5180,
    "url": "http://localhost:5180",
    "type": "vite",
    "startCommand": "npm run dev -- --port 5180",
    "workDir": "my-new-agent/frontend"
  }
}
```

### Config Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique kebab-case identifier (e.g., `"sales-agent"`) |
| `name` | string | Yes | Display name shown on the dashboard card |
| `description` | string | Yes | One-line description |
| `icon` | string | Yes | Lucide icon name (see [lucide.dev/icons](https://lucide.dev/icons)) |
| `gradient` | [string, string] | Yes | Two hex colors for the card gradient |
| `status` | string | Yes | `"active"`, `"coming-soon"`, or `"disabled"` |
| `category` | string | Yes | Department grouping (e.g., `"Human Resources"`) |
| `features` | string[] | Yes | Feature tags shown on the card |

#### Backend Config

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `port` | number | Yes | Port the backend runs on |
| `healthCheck` | string | Yes | Endpoint to hit for health checks (e.g., `/docs`) |
| `startCommand` | string | Yes | Shell command to start the backend |
| `workDir` | string | Yes | Relative path from workspace root |
| `envFile` | string | No | Path to `.env` file |
| `activateVenv` | string | No | Path to Python venv activation script |
| `deployed` | boolean | No | `true` if backend is deployed remotely |
| `deployedUrl` | string | No | Full URL of deployed backend (e.g., `"https://my-app.onrender.com"`) |

#### Frontend Config

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `port` | number | Yes | Port the frontend runs on |
| `url` | string | Yes | URL loaded in the iframe |
| `type` | string | Yes | `"vite"`, `"static"`, `"next"`, or `"unified"` |
| `startCommand` | string | Yes | Shell command to start (empty string if served by backend) |
| `workDir` | string | Yes | Relative path from workspace root |
| `env` | object | No | Environment variables to set before starting |
| `deployed` | boolean | No | `true` if frontend is deployed remotely |

---

## Step 3: Set Up Your Agent's Environment

```powershell
cd my-new-agent/backend

# Create Python virtual environment
uv venv --python 3.12

# Activate it
.\.venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -r requirements.txt

# Create .env file with secrets
echo "OPENAI_API_KEY=sk-..." > .env

# Deactivate
deactivate
```

If your frontend is React/Vite:
```powershell
cd my-new-agent/frontend
npm install
```

---

## Step 4: Test Independently

Before integrating, make sure your agent works standalone:

```powershell
# Start backend
cd my-new-agent/backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --port 8005 --reload

# In another terminal — start frontend
cd my-new-agent/frontend
npm run dev -- --port 5180

# Verify:
# Backend health → http://localhost:8005/docs
# Frontend loads → http://localhost:5180
```

---

## Step 5: Launch with Botivate

```powershell
# From workspace root
.\start-dev.ps1
```

The launcher will:
1. Read `workspace.config.json`
2. Find your new agent (status: `"active"`)
3. Activate the venv (if configured)
4. Start the backend
5. Start the frontend
6. Your agent card appears on the dashboard

---

## Advanced Scenarios

### Scenario A: Frontend served by backend (Unified Server)

If your backend also serves the frontend (like Resume-Screening-Agent), set:

```json
"frontend": {
  "port": 8005,
  "url": "http://localhost:8005",
  "type": "unified",
  "startCommand": "",
  "workDir": "my-agent/frontend"
}
```

The empty `startCommand` tells the launcher to skip starting a separate frontend process.

### Scenario B: Deployed Agent (Remote)

If your agent is deployed on Render/AWS/Vercel:

```json
"backend": {
  "port": 8005,
  "healthCheck": "/docs",
  "deployed": true,
  "deployedUrl": "https://my-agent.onrender.com",
  "startCommand": "uvicorn app.main:app --port 8005 --reload",
  "workDir": "my-agent/backend"
},
"frontend": {
  "port": 443,
  "url": "https://my-agent.onrender.com",
  "type": "vite",
  "deployed": true,
  "startCommand": "npm run dev",
  "workDir": "my-agent/frontend"
}
```

The launcher will skip both backend and frontend. The gateway will health-check the deployed URL. The iframe will load the remote URL directly.

### Scenario C: Coming Soon (Placeholder)

Show a card on the dashboard without a running agent:

```json
{
  "id": "future-agent",
  "name": "Future Agent",
  "description": "Coming soon...",
  "icon": "Sparkles",
  "gradient": ["#6366f1", "#4f46e5"],
  "status": "coming-soon",
  ...
}
```

The card will show a "Coming Soon" badge. Clicking it shows a placeholder screen instead of an iframe.

---

## Available Lucide Icons

Some good choices for agent cards:

| Icon Name | Good For |
|-----------|----------|
| `UserSearch` | HR / Recruiting |
| `Headphones` | Support / Helpdesk |
| `Factory` | Production / Manufacturing |
| `ShoppingCart` | Sales / E-commerce |
| `Wrench` | Maintenance / Repair |
| `BarChart3` | Analytics / MIS |
| `Brain` | Super Agent / AI |
| `Bot` | General AI agent |
| `Shield` | Security / Compliance |
| `Truck` | Logistics / Supply Chain |

Full list: [lucide.dev/icons](https://lucide.dev/icons)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Agent card doesn't appear | Check `status` is `"active"` in config |
| Iframe shows "refused to connect" | Backend/frontend isn't running — check the port |
| Health shows "offline" | Verify `healthCheck` endpoint exists and returns 2xx |
| Agent not starting with `start-dev.ps1` | Check `workDir` path is correct relative to workspace root |
| Port conflict | Change the port in config and restart |
| CORS errors in iframe | Add iframe origin to your backend's CORS config |

---

## Checklist for New Agent

- [ ] Agent folder created with backend + frontend
- [ ] Backend has a health check endpoint
- [ ] Backend runs on a unique port
- [ ] Frontend works when loaded in an iframe
- [ ] Config entry added to `workspace.config.json`
- [ ] `.env` file created (not committed)
- [ ] Venv created and dependencies installed
- [ ] Agent tested standalone before integration
- [ ] `start-dev.ps1` launches it correctly
- [ ] Agent card visible on dashboard
- [ ] Health check shows green on dashboard
