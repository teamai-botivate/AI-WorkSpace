# 🤖 Botivate HR Support

**Agentic AI-powered HR System — Fully Dynamic, Multi-Company, Zero-Configuration**

Botivate HR Support is a standalone HR platform where a single AI-powered chatbot handles everything — leave requests, policy queries, grievances, resignations, approvals, and more. No forms, no portals, no manual HR emails. Just one chatbot, one login, one source of truth.

---

## ✨ Key Features

- 🏢 **Multi-Company Isolation** — Each company gets a fully isolated environment
- 🧠 **Automatic Schema Adaptation** — AI analyzes any database schema with zero manual mapping
- 📜 **Policy RAG Engine** — Answers strictly from uploaded company documents (never guesses)
- 🔐 **Role-Based Access Control** — Employee, Manager, HR, CEO — enforced by AI
- ✅ **Zero Auto-Approval Policy** — AI never approves; all decisions require human authorization
- 🔔 **Smart Notifications** — In-app bell + 48h reminders + 72h escalation
- 🗄️ **Pluggable Database Adapters** — Google Sheets (default), PostgreSQL, MongoDB (extensible)
- 📧 **OAuth 2.0 Gmail Integration** — Emails are securely sent on behalf of HR without requiring passwords
- 🧾 **Professional Email UI** — Next-Gen, responsive HTML/CSS email templates for all notifications and credentials

---

## 🛠️ Tech Stack

| Layer        | Technologies                                                            |
| ------------ | ----------------------------------------------------------------------- |
| **Backend**  | FastAPI, LangGraph, LangChain, Pydantic, SQLAlchemy, ChromaDB           |
| **Frontend** | React, Tailwind CSS, React Router, Axios                                |
| **AI/LLM**   | OpenAI GPT-4o-mini (configurable)                                       |
| **Database** | SQLite (master), Google Sheets (employee data), ChromaDB (vector store) |
| **Auth**     | JWT (python-jose)                                                       |
| **Email**    | aiosmtplib + Jinja2 templates                                           |

---

## 📋 Prerequisites

- **Python 3.12** (required)
- **Node.js 18+** and **npm**
- **uv** (Python package manager) — [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **OpenAI API Key**
- **Google Service Account JSON** (for Google Sheets integration)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/HR_Support.git
cd HR_Support
```

### 2. Backend Setup

#### 2.1 Check Python Version

```bash
python --version
```

Make sure the output shows **Python 3.12.x**. If not, install Python 3.12 from [python.org](https://www.python.org/downloads/).

#### 2.2 Install uv (if not installed)

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:

```bash
uv --version
```

#### 2.3 Create Virtual Environment & Install Dependencies

```bash
cd backend

# Create a virtual environment with Python 3.12
uv venv --python 3.12

# Activate the virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Windows (CMD):
.venv\Scripts\activate.bat

# macOS / Linux:
source .venv/bin/activate

# Install all requirements using uv
uv pip install -r requirements.txt
```

#### 2.4 Configure Environment Variables

```bash
# Copy the example env file
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
```

Open `.env` and fill in the required values:

```env
OPENAI_API_KEY=sk-your-openai-api-key
GOOGLE_SERVICE_ACCOUNT_JSON=path/to/your/service-account.json
JWT_SECRET_KEY=a-strong-random-secret-key
APP_SECRET_KEY=another-strong-random-secret
```

#### 2.5 Run the Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at **http://localhost:8000**

You can view the interactive API docs at **http://localhost:8000/docs**

---

### 3. Frontend Setup

Open a **new terminal** (keep the backend running):

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at **http://localhost:5173**

The Vite dev server automatically proxies `/api` requests to the backend on port 8000.

---

## 📂 Project Structure

```
HR_Support/
├── backend/                    ← FastAPI + LangGraph + Pydantic
│   ├── .env.example            ← Environment variable template
│   ├── requirements.txt        ← Python dependencies
│   └── app/
│       ├── main.py             ← FastAPI entry + background scheduler
│       ├── config.py           ← Centralized config (from env vars)
│       ├── database.py         ← SQLAlchemy async engine
│       ├── models/             ← ORM models + Pydantic schemas
│       ├── adapters/           ← Pluggable DB adapters (Google Sheets, etc.)
│       ├── services/           ← Business logic (onboarding, RAG, approvals)
│       ├── agents/             ← LangGraph agentic chatbot
│       ├── routers/            ← API endpoints
│       └── utils/              ← Auth, email, password utilities
│
├── frontend/                   ← React + Tailwind CSS
│   ├── vite.config.js          ← Vite + Tailwind + API proxy
│   └── src/
│       ├── api.js              ← Axios API client
│       ├── context/            ← Auth context
│       ├── components/         ← Layout, NotificationBell, SupportCard, UI kit
│       └── pages/              ← Login, Onboarding, Chat
│
├── docs/                       ← Original documentation & workflow
├── ai_prompts/                 ← AI prompt references
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🔧 Configuration

All configuration is managed through environment variables (`.env` file). **Nothing is hardcoded.**

| Variable                      | Description                                |
| ----------------------------- | ------------------------------------------ |
| `OPENAI_API_KEY`              | Your OpenAI API key for LLM                |
| `OPENAI_MODEL`                | Model name (default: `gpt-4o-mini`)        |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Path to Google service account credentials |
| `DATABASE_URL`                | Master DB URL (default: SQLite)            |
| `JWT_SECRET_KEY`              | Secret for JWT token signing               |
| `SMTP_HOST`                   | SMTP server (default: `smtp.gmail.com`)    |
| `SMTP_PORT`                   | SMTP port (default: `587`)                 |
| `CHROMA_PERSIST_DIR`          | ChromaDB storage path                      |
| `APP_BASE_URL`                | Base URL for login links in emails         |

---

## 🏗️ How It Works

1. **HR registers** their company via the Onboarding Dashboard
2. **HR uploads** policies (text or documents) and connects the employee database (Google Sheet)
3. **AI automatically analyzes** the database schema — no manual column mapping
4. **System auto-generates** passwords and emails credentials to every employee
5. **Employees log in** with Company ID + Employee ID + Password + Role
6. **AI chatbot** greets them by name, knows their profile, and answers based on company data only
7. **Approval requests** (leave, resignation, etc.) are routed to authorities with zero auto-approval
8. **48h reminders** and **72h escalations** run automatically in the background

---

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
