# HR Support Agent — Setup Guide

> **Complete guide to set up the Botivate HR Support Agent from scratch.**

**Runs on:** Python 3.10 (backend) + Node.js (frontend)
**Ports:** 8001 (backend API) | 5175 (frontend dev server)
**Time:** ~10 minutes (first time)

---

## Table of Contents

1. [What This Agent Does](#1-what-this-agent-does)
2. [Prerequisites](#2-prerequisites)
3. [Backend Setup](#3-backend-setup)
4. [Frontend Setup](#4-frontend-setup)
5. [Environment Variables (.env)](#5-environment-variables-env)
6. [Google Cloud Setup](#6-google-cloud-setup)
7. [First Run & Company Onboarding](#7-first-run--company-onboarding)
8. [Running the Agent](#8-running-the-agent)
9. [Folder Structure](#9-folder-structure)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. What This Agent Does

The HR Support Agent is an AI-powered employee support chatbot and HR management platform that:

- **AI Chatbot** — LangGraph-powered conversational agent that answers HR policy questions
- **RAG Pipeline** — Retrieval-Augmented Generation from uploaded company policies (ChromaDB)
- **Leave/Expense Management** — Employees submit requests, managers approve/reject
- **Google Sheets Integration** — Reads/writes employee data from company Google Sheets (via Service Account)
- **Gmail Integration** — Sends approval/rejection notification emails from HR's real Gmail (via OAuth 2.0)
- **Multi-Tenant** — Supports multiple companies with isolated data and branding
- **Company Onboarding** — Self-service registration with Google Sheets + Gmail OAuth connection

### Architecture

```
┌─────────────────────┐     ┌─────────────────────────────────┐
│  React Frontend     │────▸│  FastAPI Backend (Port 8001)     │
│  (Port 5175)        │◂────│                                  │
│                     │     │  ├── LangGraph Agent (gpt-4o-mini)│
│  - Chat UI          │     │  ├── ChromaDB (RAG/policies)     │
│  - Dashboard        │     │  ├── SQLite (master DB)          │
│  - Onboarding Flow  │     │  ├── Google Sheets (employee DB) │
│  - Approval Panel   │     │  └── Gmail OAuth (email sender)  │
└─────────────────────┘     └─────────────────────────────────┘
```

---

## 2. Prerequisites

| Tool | Version | Required |
|------|---------|----------|
| Python | 3.10.x | ✅ Yes |
| Node.js | 18+ (LTS recommended) | ✅ Yes |
| npm | Bundled with Node.js | ✅ Yes |
| uv | Latest | Recommended (faster Python installs) |

```powershell
python --version    # Must be 3.10.x
node --version      # Must be 18+
npm --version
```

---

## 3. Backend Setup

```powershell
cd HR_Support/backend

# Create virtual environment with Python 3.10
uv venv --python 3.10
# OR: python -m venv .venv

# Activate the venv
.\.venv\Scripts\Activate.ps1

# Install all dependencies
uv pip install -r requirements.txt
# OR: pip install -r requirements.txt

# Verify key packages
python -c "import fastapi; import langchain; import chromadb; print('All OK')"

# Deactivate when done
deactivate
```

### What Gets Installed

| Package | Purpose |
|---------|---------|
| `fastapi` + `uvicorn` | Web server & API |
| `langchain` + `langgraph` | LLM orchestration & agent graph |
| `openai` | GPT-4o-mini for chatbot responses |
| `chromadb` | Vector database for policy document RAG |
| `sqlalchemy` + `aiosqlite` | Master SQLite database (companies, users, requests) |
| `google-api-python-client` | Google Sheets & Gmail API access |
| `google-auth` + `google-auth-oauthlib` | OAuth 2.0 flow + Service Account auth |
| `python-jose` | JWT token generation for auth |
| `passlib` + `bcrypt` | Password hashing |
| `python-multipart` | File uploads (policy documents) |
| `pydantic-settings` | Settings management from `.env` |

---

## 4. Frontend Setup

```powershell
cd HR_Support/frontend

# Install npm packages
npm install

# Verify installation
npm ls vite react
```

### Frontend Stack

| Package | Purpose |
|---------|---------|
| `react` + `react-dom` | UI framework |
| `vite` | Dev server & bundler |
| `tailwindcss` | Utility-first CSS |
| `axios` | HTTP client for API calls |
| `react-router-dom` | Client-side routing |
| `lucide-react` | Icon library |

---

## 5. Environment Variables (.env)

Create a file named `.env` in the `HR_Support/backend/` directory:

**File:** `HR_Support/backend/.env`

```env
# =============================================
# Botivate HR Support — Environment Config
# =============================================

# --- Application Settings ---
APP_NAME="Botivate HR Support"
APP_ENV=development
APP_SECRET_KEY=generate-a-random-secret-key-here
APP_BASE_URL=http://localhost:8001

# --- Master Database ---
# SQLite database for companies, users, approval requests, chat history
# Auto-created on first run. No setup needed.
DATABASE_URL=sqlite+aiosqlite:///./botivate_master.db

# --- OpenAI API Key (Required) ---
# Used for: LangGraph chatbot (gpt-4o-mini), policy analysis, intent classification
# Get it from: https://platform.openai.com/ → API Keys
OPENAI_API_KEY=sk-proj-your-openai-key-here

# --- OpenAI Model ---
# gpt-4o-mini is recommended (fast + cheap). gpt-4o for higher quality.
OPENAI_MODEL=gpt-4o-mini

# --- Google Service Account (Required for Google Sheets) ---
# Path to the Service Account JSON key file (relative to backend/ directory)
# See Section 6.2 below for how to create this
GOOGLE_SERVICE_ACCOUNT_JSON=service-account.json

# --- Google OAuth 2.0 (Required for Gmail Email Sending) ---
# See Section 6.3 below for how to get these
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-your-client-secret-here
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5175/oauth-callback

# --- SMTP Email (Fallback — if OAuth Gmail isn't configured) ---
# For Gmail: Enable 2FA → Create App Password
# https://myaccount.google.com/apppasswords
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password

# --- JWT Authentication ---
# Used for user login sessions. Change the secret!
JWT_SECRET_KEY=change-this-to-a-strong-random-jwt-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=480

# --- ChromaDB ---
# Directory where vector embeddings for policy documents are stored
CHROMA_PERSIST_DIR=./chroma_data

# --- Uploads ---
# Directory where uploaded policy documents are stored
UPLOAD_DIR=./uploads
```

### Variable Reference

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | ✅ | Powers the AI chatbot (all LLM calls) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | ✅ | Service Account JSON for Google Sheets read/write |
| `GOOGLE_OAUTH_CLIENT_ID` | ✅ | Gmail OAuth for sending emails from HR's account |
| `GOOGLE_OAUTH_CLIENT_SECRET` | ✅ | Gmail OAuth secret |
| `GOOGLE_OAUTH_REDIRECT_URI` | ✅ | Must match Google Console & frontend port |
| `DATABASE_URL` | Optional | Defaults to `sqlite+aiosqlite:///./botivate_master.db` |
| `SMTP_*` variables | Optional | Fallback email method if Gmail OAuth isn't used |
| `JWT_SECRET_KEY` | Optional | Defaults work for dev; change in production |
| `APP_SECRET_KEY` | Optional | Defaults work for dev; change in production |

---

## 6. Google Cloud Setup

The HR Support agent requires **two types** of Google credentials:

| Type | Purpose | Used For |
|------|---------|----------|
| **Service Account** | Server-to-server (no user interaction) | Reading/writing Google Sheets (employee database) |
| **OAuth 2.0 Client** | User-granted permission | Sending emails from HR's real Gmail account |

### 6.1 Google Cloud Project & APIs

1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Create a new project (or reuse the one from Resume Screening Agent)
3. Enable these 3 APIs (go to **APIs & Services → Library**):
   - ✅ **Gmail API**
   - ✅ **Google Sheets API**
   - ✅ **Google Drive API**

### 6.2 Service Account Setup (for Google Sheets)

The Service Account lets the backend silently read/write employee data from Google Sheets without user interaction.

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → Service Account**
3. Name: `botivate-db-agent` → Click **Create and Continue**
4. Skip role assignment → Click **Done**
5. Click the newly created Service Account → **Keys** tab
6. Click **Add Key → Create New Key → JSON**
7. Download the JSON file
8. **Rename** it to `service-account.json`
9. **Place** it at: `HR_Support/backend/service-account.json`
10. Set in `.env`: `GOOGLE_SERVICE_ACCOUNT_JSON=service-account.json`

> ⚠️ **Important:** When a company connects their Google Sheet during onboarding, they must **Share** that sheet with the Service Account email (e.g., `botivate-db-agent@your-project.iam.gserviceaccount.com`). The system prompts them to do this automatically.

### 6.3 OAuth 2.0 Setup (for Gmail Sending)

OAuth 2.0 lets the system send notification emails **from the HR manager's actual Gmail** (not a generic address). Emails appear in their Sent folder.

#### Step A: OAuth Consent Screen

1. Go to **APIs & Services → OAuth consent screen**
2. Select **External** → Create
3. Fill in:
   - App name: `Botivate HR`
   - User support email: your email
   - Developer contact: your email
4. Click **Save and Continue**

#### Step A.1: Add Scopes (Important!)

This step tells Google **what permissions** your app needs. Without the correct scope, Gmail sending will fail.

1. On the **Scopes** page, click the **"Add or Remove Scopes"** button
2. In the popup that appears, you have two options:

   **Option 1 — Search in the table:**
   - Scroll through the scope list or use the filter
   - Find and check: `https://www.googleapis.com/auth/gmail.send`

   **Option 2 — Manually add (recommended):**
   - Scroll to the bottom of the popup
   - Find the text box labeled **"Manually add scopes"**
   - Paste this exact URL:
     ```
     https://www.googleapis.com/auth/gmail.send
     ```
   - Click **"Add to Table"**

3. Verify the scope appears in the table with description: *"Send email on your behalf"*
4. Click **"Update"** to save
5. Click **Save and Continue**

> 💡 **What does `gmail.send` do?** It ONLY allows sending emails. It cannot read, delete, or modify any existing emails in the user's inbox. This is the most restrictive Gmail scope available for sending.

#### Step A.2: Add Test Users

1. On the **Test Users** page → click **"+ Add Users"**
2. Enter the Gmail addresses of HR managers who will connect their accounts
   - e.g., `hr@yourcompany.com`, `manager@yourcompany.com`
3. Click **Add** → then **Save and Continue** → **Back to Dashboard**

> ⚠️ While your app is in **"Testing"** publishing status, **only** the listed Test Users can complete the OAuth flow. All other users will see `Error 403: access_denied`.

#### Step A.3: Moving to Production (Remove Test User Limit)

By default, your OAuth consent screen is in **"Testing"** mode — only manually added test users can connect. To allow **any Google user** to connect their Gmail:

1. Go to **APIs & Services → OAuth consent screen**
2. You'll see **Publishing status: Testing** at the top
3. Click the **"Publish App"** button
4. Google will show a confirmation dialog — click **"Confirm"**

**What happens next depends on your scopes:**

| Scope Sensitivity | What Google Requires | Timeline |
|------------------|----------------------|----------|
| Non-sensitive scopes | Auto-approved, no review needed | Instant |
| Sensitive scopes (like `gmail.send`) | Google security review required | 2-6 weeks |
| Restricted scopes (like `gmail.readonly` full access) | Full verification + security assessment | 4-8 weeks |

**For `gmail.send` (sensitive scope), Google will require:**

1. **A privacy policy URL** — Host a simple privacy policy page (can be a Google Doc or GitHub page)
2. **Application homepage** — Your app's URL
3. **Authorized domains** — Domain verification via Google Search Console
4. **YouTube video** — A short video showing how your app uses the Google data (screen recording is fine)
5. **Written explanation** — Why your app needs this scope

**To submit for review:**

1. Go to **OAuth consent screen** → Click **"Edit App"**
2. Fill in the required fields:
   - App homepage: `https://yourdomain.com`
   - Privacy policy link: `https://yourdomain.com/privacy`
   - Terms of service link (optional)
3. Under **Authorized domains**, add and verify your domain
4. Save and click **"Submit for Verification"**
5. Upload the demo video and provide the explanation
6. Google will email you at the developer contact email with updates

> 💡 **For local development / demos**, staying in "Testing" mode is perfectly fine — just add all needed emails as Test Users. You only need production approval when deploying for real external users.

#### Step B: Create OAuth Client ID

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth client ID**
3. Application type: **Web application**
4. Name: `Botivate HR Gmail`
5. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:5175/oauth-callback
   ```
6. Click **Create**
7. Copy the **Client ID** and **Client Secret**
8. Add to your `.env`:
   ```env
   GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-your-secret
   GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5175/oauth-callback
   ```

> ⚠️ **CRITICAL:** The redirect URI must **exactly match** in three places:
> 1. Google Cloud Console → Authorized redirect URIs
> 2. `.env` → `GOOGLE_OAUTH_REDIRECT_URI`
> 3. The port your frontend actually runs on (default: **5175**)
>
> Mismatch = `redirect_uri_mismatch` error!

#### How the OAuth Flow Works

```
HR Manager clicks "Connect Gmail" in UI
         │
         ▼
Browser → Google Login → "Allow Botivate to send email?"
         │
         ▼ (redirect with auth code)
Frontend (port 5175) catches the code
         │
         ▼ (POST to backend)
Backend exchanges code for Refresh Token
         │
         ▼ (encrypted in SQLite)
Token stored per company. Used to send all future emails.
```

---

## 7. First Run & Company Onboarding

### What Happens on First Run

| What | Auto-Created? | Location |
|------|--------------|----------|
| SQLite database | ✅ Auto-created | `backend/botivate_master.db` |
| ChromaDB directory | ✅ Auto-created | `backend/chroma_data/` |
| Uploads directory | ✅ Auto-created | `backend/uploads/` |

> No manual database setup or migrations needed. Everything auto-initializes.

### Company Onboarding Flow

When a new company registers through the frontend:

1. **Register Company** — Company name, domain, admin email
2. **Connect Google Sheet** — Provide the Sheet URL containing employee data
   - The system instructs them to share the sheet with the Service Account email
   - Backend validates access and reads employee records
3. **Upload Policies** — Upload PDF/DOCX files of company HR policies
   - These are chunked, embedded, and stored in ChromaDB for RAG
4. **Connect Gmail (OAuth)** — HR manager authorizes Gmail sending
   - OAuth flow as described in Section 6.3
   - One-time setup; token auto-refreshes
5. **Company Ready** — Employees can now chat with the AI, submit requests, etc.

---

## 8. Running the Agent

### Option A: Via the Master Launcher (Recommended)

From the workspace root:

```powershell
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1
```

This starts **all** agents including the HR Support backend (8001) and frontend (5175).

### Option B: Standalone — Backend

```powershell
cd HR_Support/backend

# Activate venv
.\.venv\Scripts\Activate.ps1

# Run the backend API server
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### Option C: Standalone — Frontend

```powershell
cd HR_Support/frontend

# Start the Vite dev server
npm run dev
# Usually starts on port 5175
```

### Access Points

| Feature | URL |
|---------|-----|
| Frontend UI | http://localhost:5175 |
| Backend API | http://localhost:8001 |
| API Docs (Swagger) | http://localhost:8001/docs |
| Health Check | http://localhost:8001/health |

---

## 9. Folder Structure

```
HR_Support/
├── Gmail_Integration.md              ← Detailed Google integration docs
├── SPEED_OPTIMIZATION_PLAN.txt       ← Performance optimization roadmap
├── SETUP.md                          ← This file
├── backend/
│   ├── .env                          ← YOUR config goes here
│   ├── requirements.txt              ← Python dependencies
│   ├── service-account.json          ← Google Service Account key
│   ├── app/
│   │   ├── main.py                   ← FastAPI entry point
│   │   ├── config.py                 ← Settings loader (reads .env)
│   │   ├── database.py               ← SQLite/SQLAlchemy setup
│   │   ├── agents/
│   │   │   ├── hr_agent.py           ← LangGraph chatbot agent (~1100 lines)
│   │   │   └── db_agent.py           ← Database operations sub-agent
│   │   ├── models/                   ← SQLAlchemy models (Company, User, Request)
│   │   ├── routers/                  ← API routes (chat, companies, auth, etc.)
│   │   ├── services/                 ← Business logic (email, approvals, etc.)
│   │   └── adapters/                 ← Google Sheets/Gmail adapters
│   ├── chroma_data/                  ← ChromaDB vector store (auto-created)
│   ├── uploads/                      ← Uploaded policy documents
│   └── botivate_master.db            ← SQLite database (auto-created)
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/                          ← React source code
│       ├── components/               ← UI components
│       ├── pages/                    ← Route pages
│       └── services/                 ← API service layer
└── docs/
    └── complete flow.txt             ← System workflow documentation
```

---

## 10. Troubleshooting

| Problem | Fix |
|---------|-----|
| `OPENAI_API_KEY not set` | Create `.env` in `HR_Support/backend/` with your OpenAI key |
| `redirect_uri_mismatch` | Ensure Google Console, `.env`, and frontend port ALL use `http://localhost:5175/oauth-callback` |
| `Service account JSON not found` | Place `service-account.json` in `HR_Support/backend/` and set path in `.env` |
| `Google Sheets permission denied` | Share the Google Sheet with the Service Account email address |
| `Error 403: access_denied` (OAuth) | Your Gmail isn't added as Test User in Google Console |
| `sqlite3.OperationalError` | Delete `botivate_master.db` and restart — it auto-recreates |
| Frontend shows CORS error | Check backend is running on port 8001 and CORS allows `localhost:5175` |
| Chat returns empty response | Verify `OPENAI_API_KEY` is valid and has credits |
| Slow chatbot responses (8-15s) | See `SPEED_OPTIMIZATION_PLAN.txt` for known bottlenecks and solutions |
| Port 8001 already in use | `Get-NetTCPConnection -LocalPort 8001 \| ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }` |
| Port 5175 already in use | `Get-NetTCPConnection -LocalPort 5175 \| ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }` |
| `pip` not found in venv | Run `python -m ensurepip --upgrade` inside the activated venv |
| ChromaDB errors on startup | Delete `chroma_data/` folder and restart — it rebuilds when policies are re-uploaded |

---

## Quick Start Checklist

- [ ] Python 3.10 + Node.js installed
- [ ] Backend venv created & packages installed (`HR_Support/backend/.venv`)
- [ ] Frontend `node_modules` installed (`HR_Support/frontend/node_modules`)
- [ ] `.env` created in `HR_Support/backend/` with `OPENAI_API_KEY`
- [ ] Google Cloud Project created with Gmail, Sheets, Drive APIs enabled
- [ ] `service-account.json` placed in `HR_Support/backend/`
- [ ] OAuth 2.0 Client ID created with redirect URI `http://localhost:5175/oauth-callback`
- [ ] OAuth Client ID + Secret added to `.env`
- [ ] Backend starts on port 8001 (`uvicorn app.main:app --port 8001`)
- [ ] Frontend starts on port 5175 (`npm run dev`)
- [ ] Open http://localhost:5175 and register a company
