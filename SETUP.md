# Setup & Installation Guide

> Complete guide to set up the Botivate AI Workspace from scratch.

**OS:** Windows 10/11 (PowerShell 5.1+)
**Time:** ~15 minutes

---

## Prerequisites

Install these before starting:

| Tool | Version | Install |
|------|---------|---------|
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org) |
| **Python** | 3.10+ | [python.org](https://python.org) |
| **uv** (recommended) | Latest | `pip install uv` or [docs.astral.sh/uv](https://docs.astral.sh/uv/) |
| **Git** | Latest | [git-scm.com](https://git-scm.com) |

Verify installation:
```powershell
node --version    # v18+ required
python --version  # 3.10+ required
uv --version      # Optional but recommended
git --version
```

---

## Step 1: Clone the Repository

```powershell
git clone https://github.com/teamai-botivate/AI-WorkSpace.git
cd AI-WorkSpace
```

---

## Step 2: Frontend Shell (React + Tailwind)

```powershell
cd frontend
npm install
cd ..
```

This installs React 18, Vite 6, Tailwind CSS 3, TypeScript, and Lucide icons.

> **Windows Defender Note:** If `npm install` fails with `EFTYPE` error on `esbuild.exe`, add the `node_modules` folder to Windows Defender exclusions, delete `node_modules` and `package-lock.json`, then retry.

---

## Step 3: Gateway Backend (FastAPI)

```powershell
cd backend

# Create virtual environment
uv venv --python 3.12
# OR: python -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -r requirements.txt
# OR: pip install -r requirements.txt

# Deactivate
deactivate
cd ..
```

**Dependencies:** FastAPI, uvicorn, httpx, pydantic, pydantic-settings

---

## Step 4: Resume Screening Agent (HR Recruiter)

```powershell
cd Resume-Screening-Agent

# Create virtual environment (requires Python 3.10)
uv venv --python 3.10
# OR: python -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -r requirements.txt
# OR: pip install -r requirements.txt

# Download spaCy English model (REQUIRED)
python -m spacy download en_core_web_sm

# Deactivate
deactivate
cd ..
```

### Environment Variables

Create `Resume-Screening-Agent/.env`:
```env
OPENAI_API_KEY=sk-your-openai-key-here
```

If using Gmail integration, also place your `credentials.json` (Google OAuth) in the `Resume-Screening-Agent/` folder (see `GMAIL_INTEGRATION_GUIDE.md` inside that folder).

> **Note:** The BART-large-MNLI model (~1.6GB) will auto-download on first run. This is normal and one-time only.

---

## Step 5: HR Support Agent (Optional — Deployed on Render)

The HR Support agent is already **deployed on Render** at `https://botivate-hr-support.onrender.com`. No local setup needed — it works out of the box via the iframe.

If you want to run it **locally** instead:

```powershell
cd HR_Support/backend

# Create virtual environment
uv venv --python 3.10

# Activate
.\.venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -r requirements.txt

deactivate

# Install frontend deps
cd ../frontend
npm install
cd ../..
```

Create `HR_Support/backend/.env`:
```env
OPENAI_API_KEY=sk-your-openai-key-here
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

Then in `config/workspace.config.json`, set `deployed: false` for both backend and frontend of the `hr-support` agent, and update URLs to localhost.

---

## Step 6: Launch Everything

```powershell
.\start-dev.ps1
```

This will:
1. Read `config/workspace.config.json`
2. Start each active agent's backend (skipping deployed ones)
3. Start each active agent's frontend (skipping deployed/unified ones)
4. Start the Gateway API on port 9000
5. Start the Frontend Shell on port 3000

**Output example:**
```
  ========================================
      BOTIVATE AI WORKSPACE
      Development Launcher
  ========================================

[INFO] Workspace: Botivate v1.0.0
[INFO] Agents registered: 2

[AGENT] Starting: HR Recruiter & Screener
   [OK] Backend  -> port 8000
   [INFO] Frontend served by backend (unified server)

[AGENT] Starting: HR Employee Support
   [CLOUD] Backend -> DEPLOYED at https://botivate-hr-support.onrender.com
   [CLOUD] Frontend -> DEPLOYED at https://botivate-hr-support.onrender.com

[GATEWAY] Starting Gateway Backend
   [OK] Gateway  -> port 9000

[SHELL] Starting Main Frontend
   [OK] Frontend -> port 3000

  ========================================
    Open http://localhost:3000 in browser
    Gateway: http://localhost:9000/docs
    Stop all: .\start-dev.ps1 -Stop
  ========================================
```

---

## Step 7: Verify

| What | URL | Expected |
|------|-----|----------|
| Dashboard | http://localhost:3000 | Agent cards visible |
| Gateway Docs | http://localhost:9000/docs | Swagger UI |
| Gateway Config | http://localhost:9000/api/config | JSON config |
| All Health | http://localhost:9000/api/agents/health/all | All agents healthy |
| HR Recruiter | Click card on dashboard | Resume Screening UI in iframe |
| HR Support | Click card on dashboard | Support UI in iframe (Render) |

---

## Stopping Services

```powershell
.\start-dev.ps1 -Stop
```

This kills all `python`, `uvicorn`, and `node` processes.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `npm install` fails with EFTYPE | Add `node_modules` to Windows Defender exclusions |
| `spacy` model not found | Run `python -m spacy download en_core_web_sm` in the agent venv |
| `pip` not found in venv | Run `python -m ensurepip --upgrade` inside the venv |
| PowerShell can't parse `start-dev.ps1` | Ensure file is ASCII/UTF-8 without BOM |
| Port already in use | Run `.\start-dev.ps1 -Stop` first, or kill the process manually |
| iframe shows "refused to connect" | Agent backend isn't running — check the terminal window |
| BART model download slow | First launch downloads ~1.6GB. Wait for it to complete |
| HR Support shows "cold start" | Render free tier sleeps after inactivity. First load takes ~30s |
| Gateway returns 404 for agent | Check agent `id` matches in config |
| Agent card shows "Coming Soon" | Change `status` from `"coming-soon"` to `"active"` in config |

---

## Useful Commands

```powershell
# Check what's running
Get-Process python, node, uvicorn -ErrorAction SilentlyContinue | Format-Table Id, ProcessName, StartTime

# Kill specific port
Get-NetTCPConnection -LocalPort 8000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

# Rebuild frontend
cd frontend; npm run build; cd ..

# Check gateway health
Invoke-RestMethod http://localhost:9000/api/agents/health/all | ConvertTo-Json -Depth 5
```

---

## Directory of .env Files

| Agent | Location | Required Variables |
|-------|----------|--------------------|
| Resume Screener | `Resume-Screening-Agent/.env` | `OPENAI_API_KEY` |
| HR Support | `HR_Support/backend/.env` | `OPENAI_API_KEY`, `DATABASE_URL` |
| Gateway | `backend/.env` (optional) | None required currently |

> **NEVER commit `.env` files.** They are listed in `.gitignore`.
