# 🚀 Botivate — AI Workforce Portal

**A unified, config-driven AI workspace that connects multiple independent AI agents under one professional dashboard.**

Each agent has its own backend and frontend — the main shell dynamically discovers and launches them from a single config file.

---

## 🏗️ Architecture

```
AI_Workspace/
├── config/
│   └── workspace.config.json    ← Master config (agents, ports, theme)
│
├── backend/                     ← Gateway API (FastAPI)
│   └── app/
│       ├── main.py              ← Agent registry, health checks, config API
│       └── config.py            ← Config loader
│
├── frontend/                    ← Main Shell (React + Tailwind + Vite)
│   └── src/
│       ├── App.tsx              ← Shell: Dashboard or Agent iframe
│       ├── components/
│       │   ├── layout/          ← Header
│       │   ├── dashboard/       ← Dashboard, AgentCard, Stats, Welcome
│       │   ├── agent/           ← AgentShell (iframe loader)
│       │   └── common/          ← LoadingScreen, ErrorScreen, ComingSoon
│       ├── context/             ← WorkspaceContext (config provider)
│       ├── types/               ← TypeScript interfaces
│       └── utils/               ← Icon mapping
│
├── HR_Support/                  ← Agent: HR Employee Support (full-stack)
│   ├── backend/                 ← FastAPI + LangGraph + RAG
│   └── frontend/                ← React + Tailwind
│
├── Resume-Screening-Agent/      ← Agent: HR Recruiter & Screener (full-stack)
│   ├── Backend/                 ← FastAPI + GPT-4o + ChromaDB
│   ├── Frontend/                ← Vanilla HTML/JS
│   ├── JD_Generator/            ← Sub-module: JD creation
│   └── Aptitude_Generator/      ← Sub-module: Test generation
│
└── start-dev.ps1                ← One-click launcher (reads config → starts all)
```

---

## ✨ Key Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Zero Hardcoding** | All agent names, ports, URLs come from `workspace.config.json` |
| **Config-Driven** | Add a new agent = add one entry in config + drop the folder |
| **Multi-Company Ready** | Change company name/logo/theme in config = instant white-label |
| **Independent Agents** | Each agent has its own backend + frontend, runs on its own ports |
| **Iframe Integration** | Agent frontends load inside the shell via iframe — zero code changes to existing agents |
| **Gateway Health Checks** | Central API checks which agents are online/offline in real-time |

---

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** & **npm**
- **Python 3.12+**
- **uv** (Python package manager) — `pip install uv`

### 1. Clone
```bash
git clone https://github.com/teamai-botivate/AI-WorkSpace.git
cd AI-WorkSpace
```

### 2. Install Frontend Shell
```bash
cd frontend
npm install
cd ..
```

### 3. Install Gateway Backend
```bash
cd backend
uv venv --python 3.12
.venv/Scripts/Activate.ps1   # Windows
uv pip install -r requirements.txt
cd ..
```

### 4. Setup Agent Backends
Each agent folder has its own setup. See their respective READMEs:
- `HR_Support/README.md`
- `Resume-Screening-Agent/README.md`

**Important:** Create `.env` files from `.env.example` in each agent folder.

### 5. Launch Everything
```powershell
.\start-dev.ps1
```

This reads `config/workspace.config.json` and starts:
- All active agent backends & frontends
- The gateway API (port 9000)
- The main shell (port 3000)

Open **http://localhost:3000** in your browser.

### Stop All Services
```powershell
.\start-dev.ps1 -Stop
```

---

## 📦 Adding a New Agent

1. **Create the agent folder** with its own backend + frontend
2. **Add an entry** in `config/workspace.config.json`:
```json
{
  "id": "my-new-agent",
  "name": "My New Agent",
  "description": "What this agent does",
  "icon": "Bot",
  "gradient": ["#f59e0b", "#d97706"],
  "status": "active",
  "category": "Operations",
  "features": ["Feature 1", "Feature 2"],
  "backend": {
    "port": 8002,
    "healthCheck": "/docs",
    "startCommand": "uvicorn app.main:app --port 8002 --reload",
    "workDir": "my-new-agent/backend"
  },
  "frontend": {
    "port": 5176,
    "url": "http://localhost:5176",
    "type": "vite",
    "startCommand": "npm run dev -- --port 5176",
    "workDir": "my-new-agent/frontend"
  }
}
```
3. **Run** `.\start-dev.ps1` — the new agent auto-appears on the dashboard.

---

## 🛡️ Security

- **No credentials are committed.** All secrets live in `.env` files (git-ignored).
- Copy `.env.example` files to `.env` and fill in your keys.
- The master `.gitignore` blocks: `.env`, `credentials.json`, `token.json`, `service-account.json`, `client_secret*.json`, `chroma_data/`, `uploads/`, etc.

---

## 📋 Current Agents

| Agent | Status | Backend Port | Frontend Port |
|-------|--------|-------------|--------------|
| HR Recruiter & Screener | ✅ Active | 8000 | 5174 |
| HR Employee Support | ✅ Active | 8001 | 5175 |

---

## 🗺️ Roadmap

See `TODO.txt` for the detailed remaining tasks.

---

## 📄 License

Private — Botivate Team
