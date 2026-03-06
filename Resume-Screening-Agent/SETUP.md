# Resume Screening Agent — Setup Guide

> **Complete guide to set up the HR Recruiter & Resume Screening Agent from scratch.**

**Runs on:** Python 3.10 | FastAPI | Port 8000
**Time:** ~10 minutes (first time)

---

## Table of Contents

1. [What This Agent Does](#1-what-this-agent-does)
2. [Prerequisites](#2-prerequisites)
3. [Python Environment Setup](#3-python-environment-setup)
4. [Environment Variables (.env)](#4-environment-variables-env)
5. [Gmail Integration (Optional)](#5-gmail-integration-optional)
6. [Configuration (config.ini)](#6-configuration-configini)
7. [First Run Notes](#7-first-run-notes)
8. [Running the Agent](#8-running-the-agent)
9. [Folder Structure](#9-folder-structure)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. What This Agent Does

The Resume Screening Agent is an AI-powered HR recruitment tool that:

- **JD Generator** — AI-generates Job Descriptions from minimal input
- **Resume Screening** — Uploads, parses, and AI-scores resumes against a JD
- **Aptitude Tests** — Generates aptitude assessments for shortlisted candidates
- **Gmail Integration** — Auto-fetches resumes from a Gmail inbox (optional)
- **Email Automation** — Sends screening results and test links to candidates

### Sub-Applications

| Sub-App | URL Path | Port |
|---------|----------|------|
| Resume Screening | http://localhost:8000/resume | 8000 |
| JD Generator | http://localhost:8000/jd-tools | 8000 |
| Aptitude Generator | http://localhost:8000/aptitude | 8000 |
| API Docs | http://localhost:8000/docs | 8000 |

> All sub-apps run on a **unified server** on port 8000. No separate frontend server needed.

---

## 2. Prerequisites

| Tool | Version | Required |
|------|---------|----------|
| Python | 3.10.x | ✅ Yes |
| uv | Latest | Recommended (faster installs) |
| Node.js | Not needed | ❌ (frontend is served by the backend) |

```powershell
python --version    # Must be 3.10.x
uv --version        # Optional but recommended
```

---

## 3. Python Environment Setup

```powershell
cd Resume-Screening-Agent

# Create virtual environment with Python 3.10
uv venv --python 3.10
# OR: python -m venv .venv

# Activate the venv
.\.venv\Scripts\Activate.ps1

# Install all dependencies
uv pip install -r requirements.txt
# OR: pip install -r requirements.txt

# Download spaCy English language model (REQUIRED — used for NER/NLP)
python -m spacy download en_core_web_sm

# Verify spaCy model installed correctly
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('OK')"

# Deactivate when done
deactivate
```

### What Gets Installed

| Package | Purpose |
|---------|---------|
| `fastapi` + `uvicorn` | Web server & API |
| `langchain-community` + `langchain-huggingface` | AI/LLM chains |
| `chromadb` | Vector database for semantic resume search |
| `spacy` | NLP / Named Entity Recognition |
| `sentence-transformers` | Embedding model for semantic matching |
| `transformers` + `torch` | BART model for zero-shot classification |
| `groq` | Groq API client (LLaMA models) |
| `openai` | OpenAI API client (GPT-4o for visual analysis) |
| `google-api-python-client` | Gmail API for inbox fetching |
| `pypdf` + `PyMuPDF` | PDF parsing |
| `pandas` + `openpyxl` | Data handling |

---

## 4. Environment Variables (.env)

Create a file named `.env` in the `Resume-Screening-Agent/` root folder (NOT inside `Backend/`):

**File:** `Resume-Screening-Agent/.env`

```env
# =============================================
# Resume Screening Agent — Environment Config
# =============================================

# --- Groq API Key (Required) ---
# Used for: JD Generation, Resume Analysis (LLaMA models via Groq)
# Get it from: https://console.groq.com/ → API Keys → Create
# Starts with: gsk_
GROQ_API_KEY=gsk_your-groq-key-here

# --- HuggingFace API Token (Required) ---
# Used for: Sentence embeddings, model downloads
# Get it from: https://huggingface.co/ → Settings → Access Tokens → Create (Read access)
# Starts with: hf_
HUGGINGFACE_API_TOKEN=hf_your-huggingface-token-here

# --- OpenAI API Key (Required) ---
# Used for: GPT-4o visual resume analysis, advanced scoring
# Get it from: https://platform.openai.com/ → API Keys → Create
# Starts with: sk-proj-
OPENAI_API_KEY=sk-proj-your-openai-key-here

# --- SMTP Configuration (Required for Email Features) ---
# Used for: Sending screening results, assessment links, rejection emails to candidates
# For Gmail: Enable 2FA → Create App Password at https://myaccount.google.com/apppasswords
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password-no-spaces
```

### How to Get Each Key

| Key | Where to Get | Free? |
|-----|-------------|-------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com/) → API Keys | ✅ Generous free tier |
| `HUGGINGFACE_API_TOKEN` | [huggingface.co](https://huggingface.co/) → Settings → Access Tokens | ✅ Free |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/) → API Keys | 💰 Pay-as-you-go (~$0.15/1M tokens) |
| `SMTP_PASSWORD` | [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) | ✅ Free (needs 2FA enabled) |

---

## 5. Gmail Integration (Optional)

If you want the system to **automatically fetch candidate resumes from a Gmail inbox** (e.g., `hiring@yourcompany.com`), you need to set up Gmail OAuth.

> If you DON'T need this, skip to Section 6. You can always upload resumes manually.

### Step 1: Google Cloud Project Setup

1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Create a new project or use an existing one
3. Enable the **Gmail API**:
   - Go to **APIs & Services** → **Library**
   - Search "Gmail API" → Click **Enable**

### Step 2: OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **External** → Create
3. Fill in:
   - App Name: `Agentic Hiring Suite`
   - User support email: your email
   - Developer contact email: your email
4. Click **Save and Continue**

### Step 2.1: Add Scopes (Important!)

This step tells Google **what permissions** your app needs. Without the correct scope, Gmail inbox access will fail.

1. On the **Scopes** page, click the **"Add or Remove Scopes"** button
2. In the popup that appears, you have two options:

   **Option 1 — Search in the table:**
   - Scroll through the scope list or use the filter
   - Find and check: `https://www.googleapis.com/auth/gmail.readonly`

   **Option 2 — Manually add (recommended):**
   - Scroll to the bottom of the popup
   - Find the text box labeled **"Manually add scopes"**
   - Paste this exact URL:
     ```
     https://www.googleapis.com/auth/gmail.readonly
     ```
   - Click **"Add to Table"**

3. Verify the scope appears in the table with description: *"View your email messages and settings"*
4. Click **"Update"** to save
5. Click **Save and Continue**

> 💡 **What does `gmail.readonly` do?** It ONLY allows reading emails. It cannot send, delete, or modify any emails. The system uses this to fetch resumes received as attachments.

### Step 2.2: Add Test Users

1. On the **Test Users** page → click **"+ Add Users"**
2. Enter the Gmail address you'll use for receiving resumes (e.g., `hiring@yourcompany.com`)
3. Click **Add** → then **Save and Continue**

> ⚠️ While your app is in **"Testing"** publishing status, **only** the listed Test Users can complete the OAuth flow. All other users will see `Error 403: access_denied`.

### Step 2.3: Moving to Production (Remove Test User Limit)

By default, your OAuth consent screen is in **"Testing"** mode — only manually added test users can connect. To allow **any Google user** to connect their Gmail:

1. Go to **APIs & Services → OAuth consent screen**
2. You'll see **Publishing status: Testing** at the top
3. Click the **"Publish App"** button
4. Google will show a confirmation dialog — click **"Confirm"**

**What happens next depends on your scopes:**

| Scope Sensitivity | What Google Requires | Timeline |
|------------------|----------------------|----------|
| Non-sensitive scopes | Auto-approved, no review needed | Instant |
| Sensitive scopes (like `gmail.readonly`) | Google security review required | 2-6 weeks |
| Restricted scopes (full Gmail access) | Full verification + security assessment | 4-8 weeks |

**For `gmail.readonly` (sensitive scope), Google will require:**

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

### Step 3: Create OAuth Client ID

1. Go to **APIs & Services** → **Credentials**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Application type: **Web application**
4. Name: `Resume Screening Gmail`
5. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:8000/auth/gmail/callback
   ```
6. Click **Create**

### Step 4: Download & Place the JSON

1. Click **DOWNLOAD JSON** from the popup
2. Rename the downloaded file to exactly: `client_secret.json`
3. Place it at: `Resume-Screening-Agent/Backend/client_secret.json`

**The JSON should look like this:**

```json
{
  "web": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "your-project-name",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "GOCSPX-your-secret-here",
    "redirect_uris": ["http://localhost:8000/auth/gmail/callback"]
  }
}
```

> ⚠️ **Key Check:** The JSON must have `"web"` as root key (not `"installed"`).

### Step 5: Connect Gmail

1. Start the agent server (see Section 8)
2. Open http://localhost:8000 in browser
3. Click **"Connect Gmail"**
4. Sign in with your hiring Gmail account
5. You may see "This app isn't verified" → Click **Advanced** → **Go to app (unsafe)** (normal for testing)
6. Click **Allow** to grant read-only access
7. ✅ Done! Token is saved at `Backend/tokens/default_company_token.pickle`

> 💡 You only do this **once**. The token refreshes automatically.

### Gmail Security Notes

- The system only has **READ-ONLY** access (`gmail.readonly` scope)
- It **CANNOT** send, delete, or modify your emails
- Token is stored **locally** — never uploaded anywhere
- Revoke anytime: [myaccount.google.com/permissions](https://myaccount.google.com/permissions)

---

## 6. Configuration (config.ini)

The file `config.ini` in the agent root controls scoring weights and behavior. **You usually don't need to change this.**

**File:** `Resume-Screening-Agent/config.ini`

```ini
# ATS Scoring Configuration — HYBRID MODE (Text 70 + Visual 30 = 100)
[scoring]
keyword_match_weight = 25      # How much keyword matching matters
experience_weight = 20         # Years of experience scoring
education_weight = 10          # Education level matching
location_weight = 10           # Location preference matching
text_format_weight = 5         # Resume formatting quality
visual_analysis_weight = 30    # GPT-4o visual analysis score

[llm]
model = llama-3.3-70b-versatile   # Groq model for text analysis
temperature = 0.7
max_tokens = 1500

[embeddings]
model_name = sentence-transformers/all-MiniLM-L6-v2
chunk_size = 1000
chunk_overlap = 100
```

> Default settings work well for most use cases. Only modify if you want to adjust scoring priorities.

---

## 7. First Run Notes

On the **very first run**, the following will happen automatically:

| What Downloads | Size | Time | One-Time? |
|---------------|------|------|-----------|
| BART-large-MNLI model | ~1.6 GB | 2-10 min | ✅ Yes |
| Sentence-transformers model | ~80 MB | 30 sec | ✅ Yes |
| spaCy en_core_web_sm | ~12 MB | Already done in setup | ✅ Yes |

> 💡 **Don't panic** if the first run takes a few minutes — it's downloading AI models. Subsequent runs start instantly.

---

## 8. Running the Agent

### Option A: Via the Master Launcher (Recommended)

From the workspace root:

```powershell
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1
```

This starts ALL agents including this one on port 8000.

### Option B: Standalone

```powershell
cd Resume-Screening-Agent

# Activate venv
.\.venv\Scripts\Activate.ps1

# Run the unified server
cd Backend
uvicorn app.unified_server:app --host 127.0.0.1 --port 8000 --reload

# OR from workspace root:
# cd Resume-Screening-Agent/Backend
# uvicorn app.unified_server:app --port 8000 --reload
```

### Access Points

| Feature | URL |
|---------|-----|
| Main UI | http://localhost:8000 |
| Resume Screening | http://localhost:8000/resume |
| JD Generator | http://localhost:8000/jd-tools |
| Aptitude Tests | http://localhost:8000/aptitude |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |
| Gmail Status | http://localhost:8000/auth/gmail/status |

---

## 9. Folder Structure

```
Resume-Screening-Agent/
├── .env                          ← YOUR API keys go here
├── config.ini                    ← Scoring weights & model config
├── requirements.txt              ← Python dependencies
├── credentials.json              ← Google OAuth (if using Gmail)
├── Backend/
│   ├── client_secret.json        ← Gmail OAuth client secret
│   ├── app/
│   │   ├── unified_server.py     ← Main entry point (all sub-apps)
│   │   ├── core/
│   │   │   └── config.py         ← Settings loader (reads .env)
│   │   ├── routers/              ← API routes
│   │   ├── services/             ← Business logic
│   │   └── ...
│   ├── chroma_db/                ← Vector database (auto-created)
│   ├── Reports/                  ← Generated screening reports
│   ├── temp/                     ← Temporary uploaded files
│   └── tokens/                   ← Gmail OAuth tokens (auto-created)
├── Frontend/
│   ├── index.html                ← Resume Screening UI
│   ├── script.js
│   └── styles.css
├── JD_Generator/
│   ├── backend/                  ← JD generation API
│   └── frontend/                 ← JD Generator UI
└── Aptitude_Generator/
    ├── backend/                  ← Aptitude test API
    └── frontend/                 ← Aptitude test UI
```

---

## 10. Troubleshooting

| Problem | Fix |
|---------|-----|
| `GROQ_API_KEY Not Found` | Make sure `.env` is in `Resume-Screening-Agent/` root (not inside `Backend/`) |
| `spacy` model not found | Run `python -m spacy download en_core_web_sm` with the venv activated |
| `ModuleNotFoundError: torch` | Run `pip install torch` or `uv pip install torch` in the venv |
| BART model download stuck | Check internet connection. First download is ~1.6GB |
| `client_secret.json not found` | Place the Gmail OAuth JSON at `Backend/client_secret.json` |
| `redirect_uri_mismatch` (Gmail) | In Google Console, add `http://localhost:8000/auth/gmail/callback` as redirect URI |
| `Error 403: access_denied` | Your Gmail is not added as Test User in Google Console |
| "Token expired" for Gmail | Delete `Backend/tokens/` folder and reconnect Gmail |
| Port 8000 already in use | Kill the process: `Get-NetTCPConnection -LocalPort 8000 \| ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }` |
| `pip` not found in venv | Run `python -m ensurepip --upgrade` inside the venv |

---

## Quick Start Checklist

- [ ] Python 3.10 installed
- [ ] Virtual environment created & packages installed
- [ ] spaCy `en_core_web_sm` downloaded
- [ ] `.env` file created with `GROQ_API_KEY`, `HUGGINGFACE_API_TOKEN`, `OPENAI_API_KEY`
- [ ] SMTP credentials added to `.env` (for email features)
- [ ] (Optional) `client_secret.json` placed for Gmail integration
- [ ] First run — let BART model download (~1.6GB)
- [ ] Open http://localhost:8000 and verify
