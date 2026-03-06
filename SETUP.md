# Botivate AI Workspace — Complete Setup Guide

> **One guide to set up the entire AI Workspace from scratch after cloning.**
> If you just cloned this repo, follow this step-by-step.

**OS:** Windows 10/11 (PowerShell 5.1+)
**Total Time:** ~20-30 minutes (first time setup)

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Clone & Open](#2-clone--open)
3. [API Keys & Credentials (Get These First)](#3-api-keys--credentials)
4. [Frontend Shell Setup](#4-frontend-shell-setup)
5. [Gateway Backend Setup](#5-gateway-backend-setup)
6. [Resume Screening Agent Setup](#6-resume-screening-agent-setup)
7. [HR Support Agent Setup](#7-hr-support-agent-setup)
8. [Configuration File](#8-configuration-file)
9. [Launch Everything](#9-launch-everything)
10. [Verify](#10-verify)
11. [Stopping Services](#11-stopping-services)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Prerequisites

Install these tools **before** starting:

| Tool | Version | Download | Why Needed |
|------|---------|----------|------------|
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org) | Frontend (React, Vite) |
| **Python** | 3.10.x | [python.org/downloads](https://www.python.org/downloads/release/python-3100/) | All backends |
| **uv** | Latest | `pip install uv` | Fast Python package manager (recommended) |
| **Git** | Latest | [git-scm.com](https://git-scm.com) | Clone the repo |

> ⚠️ **Use Python 3.10 specifically.** Some libraries (spaCy, torch) have issues with 3.12+.

### Verify Installation

Open PowerShell and run:

```powershell
node --version      # Should show v18+ (e.g., v22.15.0)
python --version    # Should show Python 3.10.x
uv --version        # Should show uv version (optional but recommended)
git --version       # Should show git version
```

### Fix PowerShell Execution Policy (Windows)

If PowerShell blocks scripts with "not digitally signed" error:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

Or run scripts with bypass:

```powershell
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1
```

---

## 2. Clone & Open

```powershell
git clone https://github.com/teamai-botivate/AI-WorkSpace.git
cd AI-WorkSpace
code .    # Open in VS Code
```

---

## 3. API Keys & Credentials

Before setting up any agent, you need to obtain these credentials. **Get all of these first, then proceed to setup.**

### 3.1 OpenAI API Key (Required for Both Agents)

1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign In → Click your profile (top-right) → **"API Keys"**
3. Click **"Create new secret key"**
4. Name it: `Botivate Workspace`
5. Copy the key (starts with `sk-proj-...`)
6. **Save it somewhere safe** — you'll use this in multiple `.env` files

> 💡 **Costs:** Uses `gpt-4o-mini` by default (~$0.15 per 1M input tokens). Very cheap.

### 3.2 Groq API Key (Required for Resume Screening Agent)

1. Go to [console.groq.com](https://console.groq.com/)
2. Sign Up / Sign In
3. Go to **API Keys** → **"Create API Key"**
4. Copy the key (starts with `gsk_...`)

> 💡 **Free tier:** Groq provides generous free API access for LLaMA models.

### 3.3 HuggingFace API Token (Required for Resume Screening Agent)

1. Go to [huggingface.co](https://huggingface.co/)
2. Sign Up / Sign In
3. Click your profile → **Settings** → **Access Tokens**
4. Create a new token with **Read** access
5. Copy the token (starts with `hf_...`)

### 3.4 Google Cloud Setup (Required for HR Support Agent — Gmail & Sheets)

This is the most involved step. You need **two things** from Google Cloud:
- **OAuth 2.0 Client ID** → For Gmail sending via HR's actual email
- **Service Account JSON** → For reading/writing Google Sheets as employee database

#### Step A: Create Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Click project dropdown (top bar) → **"New Project"**
3. Name: `Botivate HR Integration`
4. Click **Create** → Select the new project from dropdown

#### Step B: Enable APIs

1. Go to **APIs & Services** → **Library**
2. Search and **Enable** each of these (click each → hit "Enable"):
   - ✅ **Gmail API**
   - ✅ **Google Sheets API**
   - ✅ **Google Drive API**

#### Step C: Create Service Account (for Google Sheets access)

1. Go to **APIs & Services** → **Credentials**
2. Click **"+ CREATE CREDENTIALS"** → **"Service Account"**
3. Name: `botivate-db-agent` → **Create and Continue**
4. Skip role assignment → Click **Done**
5. Click on the service account you just created
6. Go to **Keys** tab → **Add Key** → **Create New Key** → **JSON**
7. A JSON file downloads automatically
8. **Rename** it to `service-account.json`
9. **Place** it inside: `HR_Support/backend/service-account.json`
10. **Note down** the service account email from the JSON file (e.g., `botivate-db-agent@project-id.iam.gserviceaccount.com`) — you'll need this later

> 📝 **Important:** When connecting a Google Sheet as employee database, the company HR must **Share** the Sheet with the service account email (found in the JSON file) with **Editor** access.

#### Step D: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **External** → **Create**
3. Fill in:
   - App Name: `Botivate HR`
   - User Support Email: your email
   - Developer Contact Email: your email
4. Click **Save and Continue**
5. **Scopes** page:
   - Click **"Add or Remove Scopes"**
   - Add: `https://www.googleapis.com/auth/gmail.send`
   - Click **Update** → **Save and Continue**
6. **Test Users** page:
   - Click **"Add Users"**
   - Add the Gmail address(es) you'll test with (the HR email)
   - Click **Save and Continue** → **Back to Dashboard**

> ⚠️ **The app starts in "Testing" mode** — only emails added as Test Users can authenticate. To allow any Gmail user, click **"PUBLISH APP"** on the consent screen page.

#### Step E: Create OAuth 2.0 Client ID

1. Go to **APIs & Services** → **Credentials**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Application type: **Web application**
4. Name: `Botivate HR Web Client`
5. Under **Authorized JavaScript origins**, add:
   ```
   http://localhost:5175
   ```
6. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:5175/oauth/callback
   ```
7. Click **Create**
8. A popup shows **Client ID** and **Client Secret** — **copy both and save them**

> 📝 **You now have these values for your `.env` file:**
> - `GOOGLE_OAUTH_CLIENT_ID` = Client ID (ends with `.apps.googleusercontent.com`)
> - `GOOGLE_OAUTH_CLIENT_SECRET` = Client Secret (starts with `GOCSPX-...`)

> ⚠️ **Redirect URI must EXACTLY match** the port your HR Support frontend runs on. Default is `5175`. If you change it, update both Google Console and `.env`.

### 3.5 SMTP Email Credentials (for HR Support email notifications)

The system sends email notifications (leave approved, request submitted, etc.) via SMTP.

**Using Gmail SMTP:**

1. Go to [myaccount.google.com](https://myaccount.google.com/)
2. **Security** → **2-Step Verification** → Turn ON (if not already)
3. After enabling 2FA, go to: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
4. Select **App:** Mail, **Device:** Other → Name it `Botivate`
5. Click **Generate** → Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)
6. Remove spaces → that's your `SMTP_PASSWORD`

> 📝 **You now have:**
> - `SMTP_USER` = your Gmail address (e.g., `team.ai@botivate.in`)
> - `SMTP_PASSWORD` = the 16-char app password without spaces

### 3.6 Gmail OAuth for Resume Screening Agent (Optional — for inbox resume fetching)

If you want the Resume Screening Agent to auto-fetch resumes from a Gmail inbox:

1. In the **same Google Cloud project** (from Step 3.4), go to **Credentials**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Application type: **Web application**
4. Name: `Resume Screening Gmail`
5. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:8000/auth/gmail/callback
   ```
6. Click **Create** → **DOWNLOAD JSON**
7. Rename the downloaded file to `client_secret.json`
8. Place it at: `Resume-Screening-Agent/Backend/client_secret.json`

> Also enable **Gmail API** (Step 3.4B) and add `gmail.readonly` scope in the OAuth Consent Screen.

---

## 4. Frontend Shell Setup

The main dashboard UI (React + Vite + Tailwind).

```powershell
cd frontend
npm install
cd ..
```

> **Windows Defender Note:** If `npm install` fails with `EFTYPE` error on `esbuild.exe`:
> 1. Open **Windows Security** → Virus & threat protection → Manage settings
> 2. Under Exclusions, add the `frontend/node_modules` folder
> 3. Delete `node_modules` and `package-lock.json`, then retry `npm install`

---

## 5. Gateway Backend Setup

The central FastAPI gateway that routes requests to all agents.

```powershell
cd backend

# Create virtual environment with Python 3.10
uv venv --python 3.10
# OR: python -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# Install pip if missing
python -m ensurepip --upgrade

# Install dependencies
uv pip install -r requirements.txt
# OR: pip install -r requirements.txt

deactivate
cd ..
```

**No `.env` file needed** for the gateway — it reads everything from `config/workspace.config.json`.

---

## 6. Resume Screening Agent Setup

> For detailed agent-specific setup, see: [`Resume-Screening-Agent/SETUP.md`](Resume-Screening-Agent/SETUP.md)

```powershell
cd Resume-Screening-Agent

# Create venv with Python 3.10
uv venv --python 3.10
# OR: python -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -r requirements.txt
# OR: pip install -r requirements.txt

# Download spaCy English model (REQUIRED)
python -m spacy download en_core_web_sm

deactivate
cd ..
```

### Create `.env` file at `Resume-Screening-Agent/.env`:

```env
# =============================================
# Resume Screening Agent — Environment Config
# =============================================

# --- API Keys (Required) ---
GROQ_API_KEY=gsk_your-groq-key-here
HUGGINGFACE_API_TOKEN=hf_your-huggingface-token-here
OPENAI_API_KEY=sk-proj-your-openai-key-here

# --- SMTP (For sending screening results & assessment emails) ---
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
```

> 📝 **First Run Note:** The BART-large-MNLI model (~1.6GB) will auto-download on first run. This is normal and one-time only.

---

## 7. HR Support Agent Setup

> For detailed agent-specific setup, see: [`HR_Support/SETUP.md`](HR_Support/SETUP.md)

### Backend:

```powershell
cd HR_Support/backend

# Create venv with Python 3.10
uv venv --python 3.10
# OR: python -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -r requirements.txt
# OR: pip install -r requirements.txt

deactivate
cd ..
```

### Frontend:

```powershell
cd frontend
npm install
cd ../..
```

### Create `.env` file at `HR_Support/backend/.env`:

```env
# =============================================
# Botivate HR Support — Environment Config
# =============================================

# --- Application ---
APP_NAME="Botivate HR Support"
APP_ENV="development"
APP_SECRET_KEY="generate-a-random-32-char-secret-here"
APP_BASE_URL="http://localhost:5175"

# --- Database (Master DB — auto-created on first run) ---
DATABASE_URL="sqlite+aiosqlite:///./botivate_master.db"

# --- OpenAI / LLM ---
OPENAI_API_KEY="sk-proj-your-openai-key-here"
OPENAI_MODEL="gpt-4o-mini"

# --- Google Sheets / OAuth (from Section 3.4) ---
GOOGLE_SERVICE_ACCOUNT_JSON="./service-account.json"
GOOGLE_OAUTH_CLIENT_ID="your-client-id.apps.googleusercontent.com"
GOOGLE_OAUTH_CLIENT_SECRET="GOCSPX-your-secret-here"
GOOGLE_OAUTH_REDIRECT_URI="http://localhost:5175/oauth/callback"

# --- Email / SMTP (from Section 3.5) ---
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-16-char-app-password"

# --- JWT Auth ---
JWT_SECRET_KEY="generate-another-random-32-char-secret"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_MINUTES=480

# --- Storage ---
CHROMA_PERSIST_DIR="./chroma_data"
UPLOAD_DIR="./uploads"
```

> ⚠️ **Make sure `GOOGLE_OAUTH_REDIRECT_URI` matches EXACTLY** what you added in Google Cloud Console (Section 3.4E). Including the port number.

### Place Service Account JSON:

Copy the `service-account.json` (from Section 3.4C) to: `HR_Support/backend/service-account.json`

---

## 8. Configuration File

The central config lives at `config/workspace.config.json`. It defines all agents, ports, and commands.

**Default ports:**

| Service | Port | URL |
|---------|------|-----|
| Main Frontend (Dashboard) | 3000 | http://localhost:3000 |
| Gateway API | 9000 | http://localhost:9000 |
| Resume Screening Backend | 8000 | http://localhost:8000 |
| HR Support Backend | 8001 | http://localhost:8001 |
| HR Support Frontend | 5175 | http://localhost:5175 |

> If you change any port in `workspace.config.json`, also update the corresponding `.env` files and Google Cloud redirect URIs.

---

## 9. Launch Everything

```powershell
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1
```

Or if execution policy is already set:

```powershell
.\start-dev.ps1
```

**Expected output:**

```
  ========================================
      BOTIVATE AI WORKSPACE
      Development Launcher
  ========================================

[INFO] Workspace: Botivate v1.0.0
[INFO] Agents registered: 2

[AGENT] Starting: HR Recruiter & Screener
   [OK] Backend  -> port 8000 (Background)
   [INFO] Frontend served by backend (unified server)

[AGENT] Starting: HR Employee Support
   [OK] Backend  -> port 8001 (Background)
   [OK] Frontend -> port 5175 (Background)

[GATEWAY] Starting Gateway Backend
   [OK] Gateway  -> port 9000 (Background)

[SHELL] Starting Main Frontend
   [OK] Frontend -> port 3000 (http://localhost:3000)

  ========================================
    Open http://localhost:3000 in browser
    Gateway: http://localhost:9000/docs
    Stop all: .\start-dev.ps1 -Stop
  ========================================
```

---

## 10. Verify

| What | URL | Expected |
|------|-----|----------|
| Dashboard | http://localhost:3000 | Agent cards visible |
| Gateway Docs | http://localhost:9000/docs | Swagger UI |
| Gateway Config | http://localhost:9000/api/config | JSON config |
| All Health | http://localhost:9000/api/agents/health/all | All agents healthy |
| HR Recruiter | http://localhost:8000 | Resume Screening UI |
| HR Support API | http://localhost:8001/health | `{"status": "ok"}` |
| HR Support UI | http://localhost:5175 | HR Support Frontend |

---

## 11. Stopping Services

```powershell
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1 -Stop
```

This kills all `python`, `uvicorn`, and `node` processes.

---

## 12. Troubleshooting

| Problem | Fix |
|---------|-----|
| PowerShell "not digitally signed" | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force` |
| `npm install` fails with EFTYPE | Add `node_modules` to Windows Defender exclusions |
| `spacy` model not found | `python -m spacy download en_core_web_sm` in the Resume agent venv |
| `pip` not found in venv | `python -m ensurepip --upgrade` inside the venv |
| Port already in use | `.\start-dev.ps1 -Stop` first, or kill manually |
| `redirect_uri_mismatch` on Google OAuth | Redirect URI in Google Console must **exactly** match `.env` value (including port) |
| BART model download slow | First launch downloads ~1.6GB. One-time — wait for it |
| Google Sheets "permission denied" | Share the Sheet with the Service Account email from `service-account.json` |
| "App not verified" Google warning | Click **Advanced** → **Go to app (unsafe)**. Normal for testing mode |
| OAuth "access_denied" | Gmail not added as Test User in Google Console → OAuth consent screen |
| Gateway returns 404 | Check agent `id` matches in `config/workspace.config.json` |

---

## Summary: What Each Agent Needs

| Component | Resume Screening Agent | HR Support Agent | Gateway |
|-----------|----------------------|-----------------|---------|
| Python venv | ✅ 3.10 | ✅ 3.10 | ✅ 3.10 |
| npm install | ❌ | ✅ (frontend) | ❌ |
| `.env` file | ✅ | ✅ | ❌ |
| OpenAI Key | ✅ | ✅ | ❌ |
| Groq Key | ✅ | ❌ | ❌ |
| HuggingFace Token | ✅ | ❌ | ❌ |
| Google OAuth | Optional (Gmail fetch) | ✅ (Gmail send) | ❌ |
| Service Account JSON | ❌ | ✅ (Sheets) | ❌ |
| SMTP Credentials | ✅ | ✅ | ❌ |
| spaCy model | ✅ | ❌ | ❌ |

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

> ⚠️ **NEVER commit `.env` files to Git.** They contain secrets and are listed in `.gitignore`.
