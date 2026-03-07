# Botivate AI Workspace — Setup Guide

Step-by-step instructions to get the workspace running locally on Windows.

---

## Prerequisites

| Tool    | Version  | Purpose                      |
| ------- | -------- | ---------------------------- |
| Python  | 3.10+    | Backend (FastAPI)            |
| Node.js | 18+      | Frontend (React + Vite)      |
| uv      | latest   | Fast Python package manager  |
| Git     | any      | Clone the repository         |

### Install uv (if not already installed)

```powershell
# Option 1 — standalone installer (recommended)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Option 2 — via pip
pip install uv

# Option 3 — via winget
winget install --id=astral-sh.uv -e
```

Verify installation:

```powershell
uv --version
```

---

## Step 1 — Clone & Navigate

```powershell
cd C:\Users\YourUser\Desktop
git clone <repo-url> AI_Workspace
cd AI_Workspace\AI_Workspace
```

---

## Step 2 — Environment Variables

```powershell
# Create .env from template
Copy-Item .env.example .env
```

Open `.env` in your editor and fill in the required API keys:

| Key                | Required | Where to get it                                    |
| ------------------ | -------- | -------------------------------------------------- |
| `OPENAI_API_KEY`   | Yes*     | https://platform.openai.com/api-keys               |
| `GROQ_API_KEY`     | Yes*     | https://console.groq.com/keys                      |
| `APP_SECRET_KEY`   | Yes      | Any random strong string                           |
| `JWT_SECRET_KEY`   | Yes      | Any random strong string                           |
| `SMTP_USER`        | Optional | Gmail address for email features                   |
| `SMTP_PASSWORD`    | Optional | Gmail App Password                                 |
| `GOOGLE_OAUTH_*`   | Optional | Google Cloud Console → OAuth 2.0 credentials       |

> \* At least one LLM key (OpenAI or Groq) is needed for AI agents to work. Agents with missing keys will show as "missing credentials" on the dashboard — the workspace itself still runs fine.

---

## Step 3 — Backend Setup (Python + uv)

### 3a. Create virtual environment with uv

```powershell
cd backend

# Create a virtual environment
uv venv

# Activate it
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` in your terminal prompt.

### 3b. Install Python dependencies

```powershell
# Install all packages from requirements.txt using uv
uv pip install -r requirements.txt
```

This installs FastAPI, LangChain, ChromaDB, SQLAlchemy, and all other backend dependencies.

### 3c. Verify installation

```powershell
python -c "import fastapi; print(f'FastAPI {fastapi.__version__} installed')"
```

```powershell
cd ..
```

---

## Step 4 — Frontend Setup (Node.js)

```powershell
cd frontend

# Install npm packages
npm install

cd ..
```

---

## Step 5 — Create Data Directories

The backend stores databases and vector embeddings in `data/`. Create it:

```powershell
New-Item -ItemType Directory -Path data -Force
New-Item -ItemType Directory -Path data\chroma -Force
New-Item -ItemType Directory -Path data\agents -Force
```

---

## Step 6 — Run the Workspace

### Option A — Using the startup script (recommended)

```powershell
.\start-dev.ps1
```

This launches both backend and frontend in separate terminal windows and opens the browser.

### Option B — Manual (two terminals)

**Terminal 1 — Backend:**

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
cd ..
$env:PYTHONPATH = (Get-Location).Path
uvicorn backend.app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```powershell
cd frontend
npm run dev
```

---

## Step 7 — First Launch

1. Open **http://localhost:3000** in your browser
2. The **Setup Wizard** appears on first launch
3. Enter your company name, tagline, logo URL, and pick brand colors
4. Click **Launch Workspace** — your branded dashboard loads with all active agents

---

## Verify Everything Works

| Check                | URL / Command                          | Expected                    |
| -------------------- | -------------------------------------- | --------------------------- |
| Backend health       | http://localhost:8000/api/health       | `{"status": "healthy"}`     |
| API docs             | http://localhost:8000/docs             | Swagger UI                  |
| Agent registry       | http://localhost:8000/api/agents       | List of discovered agents   |
| Frontend             | http://localhost:3000                  | Setup Wizard or Dashboard   |

---

## Stopping the Servers

```powershell
.\start-dev.ps1 -Stop
```

Or close the terminal windows manually.

---

## Troubleshooting

### uv: command not found
Restart your terminal after installing uv, or add it to your PATH manually:
```powershell
$env:Path += ";$env:USERPROFILE\.cargo\bin"
```

### Module not found errors
Make sure the virtual environment is activated (`(.venv)` in prompt) and you installed from the correct directory:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

### Port already in use
Kill existing processes:
```powershell
# Find process on port 8000
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object OwningProcess
# Kill it
Stop-Process -Id <PID> -Force
```

### ChromaDB / SQLite errors
Delete the data directory and let the app recreate it:
```powershell
Remove-Item -Recurse -Force data
New-Item -ItemType Directory -Path data -Force
```

### Frontend proxy errors
The Vite dev server proxies `/api` to the backend. Make sure the backend is running on port 8000 before starting the frontend.

---

## Project Structure Reference

```
AI_Workspace/
├── .env.example              ← API keys template
├── .env                      ← Your actual keys (git-ignored)
├── start-dev.ps1             ← One-command dev startup
├── workspace.config.json     ← Branding + agent config (auto-created by Setup Wizard)
├── backend/
│   ├── requirements.txt      ← Python dependencies
│   ├── .venv/                ← Virtual environment (created by uv)
│   └── app/
│       ├── main.py           ← FastAPI entry point
│       ├── config.py         ← Settings loader
│       ├── plugin_loader.py  ← Auto-discovers agents
│       ├── core/             ← Shared services (auth, email, LLM)
│       └── agents/           ← Plugin folders (hr_support, resume_screening)
├── frontend/
│   ├── package.json          ← Node dependencies
│   └── src/                  ← React + TypeScript source
├── data/                     ← Runtime data (SQLite, ChromaDB)
└── docs/                     ← Additional documentation
```

---

## Next Steps

- **Add API keys** — Fill in `.env` to activate agents
- **Customize branding** — Re-run setup or edit `workspace.config.json`
- **Add a new agent** — See [docs/CUSTOMIZATION.md](docs/CUSTOMIZATION.md)
- **Deploy to production** — See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **Set up Google credentials** — See [docs/CREDENTIALS_GUIDE.md](docs/CREDENTIALS_GUIDE.md)
