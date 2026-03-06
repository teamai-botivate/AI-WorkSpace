# Botivate AI Workspace — Deployment Guide

> **Complete guide for anyone cloning this repo and deploying to production on AWS, Render, Railway, DigitalOcean, or any cloud platform.**

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Pre-Deployment Checklist](#2-pre-deployment-checklist)
3. [Option A: Deploy on Render (Easiest)](#3-option-a-deploy-on-render-easiest)
4. [Option B: Deploy on AWS (EC2 — Single Server)](#4-option-b-deploy-on-aws-ec2--single-server)
5. [Option C: Deploy on AWS (ECS/Fargate — Containerized)](#5-option-c-deploy-on-aws-ecs-fargate--containerized)
6. [Option D: Deploy on Railway](#6-option-d-deploy-on-railway)
7. [Option E: Deploy on DigitalOcean App Platform](#7-option-e-deploy-on-digitalocean-app-platform)
8. [Docker Setup](#8-docker-setup)
9. [Environment Variables Reference](#9-environment-variables-reference)
10. [Google Cloud OAuth — Production Redirect URIs](#10-google-cloud-oauth--production-redirect-uris)
11. [Database Considerations for Production](#11-database-considerations-for-production)
12. [Nginx Reverse Proxy Setup](#12-nginx-reverse-proxy-setup)
13. [SSL / HTTPS Setup](#13-ssl--https-setup)
14. [CI/CD Pipeline](#14-cicd-pipeline)
15. [Monitoring & Logs](#15-monitoring--logs)
16. [Cost Estimates](#16-cost-estimates)

---

## 1. Architecture Overview

Botivate is a **multi-service** application. You're deploying **5 services** that talk to each other:

```
                    ┌────────────────────────────┐
       Users ──────▸│  Main Dashboard (React)    │ Port 3000
                    │  (Static files — Vite build)│
                    └────────────┬───────────────┘
                                 │ API calls
                                 ▼
                    ┌────────────────────────────┐
                    │  Gateway API (FastAPI)      │ Port 9000
                    │  /api/config, /api/agents   │
                    └─────┬──────────┬───────────┘
                          │          │
              ┌───────────▼──┐  ┌───▼─────────────────┐
              │ Resume Agent │  │ HR Support Backend   │ Port 8001
              │ (FastAPI)    │  │ (FastAPI + LangGraph)│
              │ Port 8000    │  └───┬─────────────────┘
              │ (unified —   │      │
              │  serves its  │  ┌───▼─────────────────┐
              │  own frontend│  │ HR Support Frontend  │ Port 5175
              │  too)        │  │ (React — Vite build) │
              └──────────────┘  └─────────────────────┘
```

### Key Facts for Deployment

| Service | Framework | Entry Point | Port | Notes |
|---------|-----------|-------------|------|-------|
| Main Dashboard | React + Vite + TS | `frontend/` | 3000 | Static build, serve with Nginx/CDN |
| Gateway API | FastAPI | `backend/app/main.py` | 9000 | Lightweight proxy, reads `config/workspace.config.json` |
| Resume Screening Agent | FastAPI | `Resume-Screening-Agent/Backend/app/unified_server.py` | 8000 | Serves both API + HTML frontend |
| HR Support Backend | FastAPI | `HR_Support/backend/app/main.py` | 8001 | LangGraph + ChromaDB + SQLite |
| HR Support Frontend | React + Vite | `HR_Support/frontend/` | 5175 | Static build, serve with Nginx/CDN |

---

## 2. Pre-Deployment Checklist

Before deploying anywhere, complete these steps:

### 2.1 Clone the Repo

```bash
git clone https://github.com/teamai-botivate/AI-WorkSpace.git
cd AI-WorkSpace
```

### 2.2 Get All API Keys

You need these credentials **before** deploying:

| Credential | Where to Get | Used By |
|------------|-------------|---------|
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/) | HR Support chatbot, Resume visual analysis |
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com/) | Resume Screening (LLaMA) |
| `HUGGINGFACE_API_TOKEN` | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) | Sentence embeddings |
| Google Service Account JSON | Google Cloud Console | HR Support → Google Sheets |
| Google OAuth Client ID + Secret | Google Cloud Console | HR Support → Gmail sending |
| SMTP credentials | Gmail App Password | Resume Screening → Email sending |

### 2.3 Build Frontends

Both React frontends must be **built** for production (not `npm run dev`):

```bash
# Main Dashboard
cd frontend
npm install
npm run build    # → creates frontend/dist/

# HR Support Frontend
cd ../HR_Support/frontend
npm install
npm run build    # → creates HR_Support/frontend/dist/
```

### 2.4 Update workspace.config.json for Production

You must update `config/workspace.config.json` to point to production URLs instead of `localhost`:

```json
{
  "gateway": {
    "port": 9000,
    "corsOrigins": [
      "https://botivate.yourdomain.com",
      "https://hr-support.yourdomain.com"
    ]
  },
  "agents": [
    {
      "id": "hr-recruiter",
      "backend": {
        "port": 8000,
        "deployed": true,
        "deployedUrl": "https://resume-agent.yourdomain.com"
      },
      "frontend": {
        "url": "https://resume-agent.yourdomain.com",
        "deployed": true
      }
    },
    {
      "id": "hr-support",
      "backend": {
        "port": 8001,
        "deployed": true,
        "deployedUrl": "https://hr-api.yourdomain.com"
      },
      "frontend": {
        "url": "https://hr-support.yourdomain.com",
        "deployed": true
      }
    }
  ]
}
```

### 2.5 Update Google OAuth Redirect URIs

In Google Cloud Console → Credentials → Your OAuth Client → **Authorized redirect URIs**:

Replace `http://localhost:5175/oauth-callback` with:
```
https://hr-support.yourdomain.com/oauth-callback
```

And update `.env`:
```env
GOOGLE_OAUTH_REDIRECT_URI=https://hr-support.yourdomain.com/oauth-callback
```

---

## 3. Option A: Deploy on Render (Easiest)

[Render](https://render.com) is the simplest option — no Docker needed, auto-deploys from GitHub.

### Step 1: Create a Render Account

1. Go to [render.com](https://render.com) → Sign up (free tier available)
2. Connect your GitHub account

### Step 2: Deploy Gateway API (Web Service)

1. Click **New → Web Service**
2. Connect your repo: `teamai-botivate/AI-WorkSpace`
3. Settings:
   - **Name:** `botivate-gateway`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables (none needed for gateway — it only reads config)
5. Click **Create Web Service**

> Render assigns a URL like `https://botivate-gateway.onrender.com`

### Step 3: Deploy Resume Screening Agent (Web Service)

1. Click **New → Web Service**
2. Settings:
   - **Name:** `botivate-resume-agent`
   - **Root Directory:** `Resume-Screening-Agent/Backend`
   - **Runtime:** Python 3
   - **Build Command:**
     ```bash
     pip install -r ../../requirements.txt && python -m spacy download en_core_web_sm
     ```
     > Note: requirements.txt is in the Resume-Screening-Agent root. Adjust path if Render can't find it. You may need to copy it into the Backend/ folder.
   - **Start Command:** `uvicorn app.unified_server:app --host 0.0.0.0 --port $PORT`
3. Add environment variables:
   ```
   GROQ_API_KEY=gsk_your-key
   HUGGINGFACE_API_TOKEN=hf_your-token
   OPENAI_API_KEY=sk-proj-your-key
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```
4. **Instance Type:** At least **Standard** ($7/mo) — the AI models need 2GB+ RAM
5. Click **Create Web Service**

### Step 4: Deploy HR Support Backend (Web Service)

1. Click **New → Web Service**
2. Settings:
   - **Name:** `botivate-hr-backend`
   - **Root Directory:** `HR_Support/backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add environment variables (see [Section 9](#9-environment-variables-reference) for full list)
4. **Disk:** Add a Render Disk for persistent SQLite + ChromaDB:
   - Mount path: `/data`
   - Update env: `DATABASE_URL=sqlite+aiosqlite:///data/botivate.db`
   - Update env: `CHROMA_PERSIST_DIR=/data/chroma`
5. Upload `service-account.json` as a **Secret File** (or base64-encode it into an env var)
6. Click **Create Web Service**

### Step 5: Deploy Frontends (Static Sites)

**Main Dashboard:**
1. Click **New → Static Site**
2. Settings:
   - **Name:** `botivate-dashboard`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
3. Add env var: `VITE_API_URL=https://botivate-gateway.onrender.com`

**HR Support Frontend:**
1. Click **New → Static Site**
2. Settings:
   - **Name:** `botivate-hr-frontend`
   - **Root Directory:** `HR_Support/frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
3. Add env var: `VITE_API_URL=https://botivate-hr-backend.onrender.com`

### Step 6: Update Config & Redeploy Gateway

Update `config/workspace.config.json` with the Render URLs:

```json
"corsOrigins": [
  "https://botivate-dashboard.onrender.com",
  "https://botivate-hr-frontend.onrender.com"
]
```

And update agent backend `deployedUrl` fields to the Render URLs.

### Render Pricing

| Service | Plan | Cost |
|---------|------|------|
| Gateway API | Free | $0/mo |
| Resume Agent | Standard | $7/mo (needs 2GB+ RAM for BART model) |
| HR Support Backend | Standard | $7/mo |
| Dashboard (Static) | Free | $0/mo |
| HR Frontend (Static) | Free | $0/mo |
| Render Disk (1GB) | — | $0.25/mo |
| **Total** | | **~$14/mo** |

> ⚠️ Free tier on Render spins down after 15 min of inactivity (cold starts ~30s). Use Standard for production.

---

## 4. Option B: Deploy on AWS (EC2 — Single Server)

Best for: **Full control, single server, cost-effective for small teams.**

### Step 1: Launch an EC2 Instance

1. Go to AWS Console → EC2 → **Launch Instance**
2. Settings:
   - **AMI:** Ubuntu 22.04 LTS
   - **Instance Type:** `t3.medium` (2 vCPU, 4GB RAM) minimum — `t3.large` recommended
   - **Storage:** 30 GB gp3
   - **Security Group:** Open ports 80 (HTTP), 443 (HTTPS), 22 (SSH)
3. Create/select a key pair for SSH
4. Launch

### Step 2: SSH and Install Dependencies

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# System updates
sudo apt update && sudo apt upgrade -y

# Install Python 3.10
sudo apt install -y python3.10 python3.10-venv python3.10-dev python3-pip

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Nginx (reverse proxy)
sudo apt install -y nginx

# Install Certbot (SSL)
sudo apt install -y certbot python3-certbot-nginx

# Install Git
sudo apt install -y git
```

### Step 3: Clone and Setup

```bash
cd /opt
sudo git clone https://github.com/teamai-botivate/AI-WorkSpace.git botivate
sudo chown -R ubuntu:ubuntu botivate
cd botivate

# --- Gateway Backend ---
cd backend
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate

# --- Resume Screening Agent ---
cd ../Resume-Screening-Agent
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
deactivate

# --- HR Support Backend ---
cd ../HR_Support/backend
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate

# --- Main Dashboard ---
cd ../../frontend
npm install
npm run build

# --- HR Support Frontend ---
cd ../HR_Support/frontend
npm install
VITE_API_URL=https://yourdomain.com/api/hr npm run build
```

### Step 4: Create .env Files

```bash
# Resume Screening Agent
cat > /opt/botivate/Resume-Screening-Agent/.env << 'EOF'
GROQ_API_KEY=gsk_your-key
HUGGINGFACE_API_TOKEN=hf_your-token
OPENAI_API_KEY=sk-proj-your-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EOF

# HR Support Backend
cat > /opt/botivate/HR_Support/backend/.env << 'EOF'
APP_NAME="Botivate HR Support"
APP_ENV=production
APP_SECRET_KEY=$(openssl rand -hex 32)
APP_BASE_URL=https://yourdomain.com
DATABASE_URL=sqlite+aiosqlite:///./botivate_master.db
OPENAI_API_KEY=sk-proj-your-key
OPENAI_MODEL=gpt-4o-mini
GOOGLE_SERVICE_ACCOUNT_JSON=service-account.json
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-your-secret
GOOGLE_OAUTH_REDIRECT_URI=https://yourdomain.com/hr/oauth-callback
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=480
CHROMA_PERSIST_DIR=./chroma_data
UPLOAD_DIR=./uploads
EOF
```

### Step 5: Create Systemd Services

Create a service file for each backend so they auto-start and auto-restart:

```bash
# Gateway Service
sudo cat > /etc/systemd/system/botivate-gateway.service << 'EOF'
[Unit]
Description=Botivate Gateway API
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory=/opt/botivate/backend
ExecStart=/opt/botivate/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 9000
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Resume Screening Agent Service
sudo cat > /etc/systemd/system/botivate-resume.service << 'EOF'
[Unit]
Description=Botivate Resume Screening Agent
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory=/opt/botivate/Resume-Screening-Agent/Backend
EnvironmentFile=/opt/botivate/Resume-Screening-Agent/.env
ExecStart=/opt/botivate/Resume-Screening-Agent/.venv/bin/uvicorn app.unified_server:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# HR Support Backend Service
sudo cat > /etc/systemd/system/botivate-hr.service << 'EOF'
[Unit]
Description=Botivate HR Support Backend
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory=/opt/botivate/HR_Support/backend
EnvironmentFile=/opt/botivate/HR_Support/backend/.env
ExecStart=/opt/botivate/HR_Support/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Enable and start all services
sudo systemctl daemon-reload
sudo systemctl enable botivate-gateway botivate-resume botivate-hr
sudo systemctl start botivate-gateway botivate-resume botivate-hr

# Check status
sudo systemctl status botivate-gateway botivate-resume botivate-hr
```

### Step 6: Configure Nginx

See [Section 12](#12-nginx-reverse-proxy-setup) for the full Nginx config.

### Step 7: SSL Certificate

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### AWS EC2 Pricing

| Instance | vCPU | RAM | Cost (on-demand) | Cost (reserved 1yr) |
|----------|------|-----|-------------------|---------------------|
| t3.medium | 2 | 4GB | ~$30/mo | ~$19/mo |
| t3.large | 2 | 8GB | ~$60/mo | ~$38/mo |
| t3.xlarge | 4 | 16GB | ~$120/mo | ~$76/mo |

> **Recommended:** `t3.large` (8GB RAM) — BART model alone needs ~2GB, plus ChromaDB, plus LangGraph.

---

## 5. Option C: Deploy on AWS (ECS/Fargate — Containerized)

Best for: **Auto-scaling, zero server management, enterprise-grade.**

### Prerequisites

- Docker installed locally
- AWS CLI configured
- ECR (Elastic Container Registry) repository created for each service

### Step 1: Create Dockerfiles

See [Section 8](#8-docker-setup) for all Dockerfiles.

### Step 2: Build and Push to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build and push each service
docker build -t botivate-gateway -f docker/Dockerfile.gateway .
docker tag botivate-gateway:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/botivate-gateway:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/botivate-gateway:latest

# Repeat for resume-agent, hr-backend, dashboard, hr-frontend
```

### Step 3: Create ECS Cluster

1. Go to AWS Console → ECS → **Create Cluster**
2. Name: `botivate-cluster`
3. Infrastructure: **AWS Fargate** (serverless)
4. Create

### Step 4: Create Task Definitions

Create a task definition for each service with:
- Container image from ECR
- Port mappings
- Environment variables
- CPU/Memory allocations:
  - Gateway: 0.25 vCPU, 512MB
  - Resume Agent: 1 vCPU, 4GB (BART model)
  - HR Backend: 0.5 vCPU, 2GB
  - Frontends: 0.25 vCPU, 512MB

### Step 5: Create Services

Create ECS Services with:
- Desired count: 1 (start small)
- ALB (Application Load Balancer) for routing
- Service discovery for inter-service communication

### Step 6: Application Load Balancer Rules

| Path Pattern | Target Group |
|-------------|-------------|
| `/` | Main Dashboard |
| `/api/*` | Gateway (port 9000) |
| `/resume/*` | Resume Agent (port 8000) |
| `/hr/api/*` | HR Backend (port 8001) |
| `/hr/*` | HR Frontend |

---

## 6. Option D: Deploy on Railway

[Railway](https://railway.app) is great for multi-service deployments with a nice UI.

### Steps

1. Go to [railway.app](https://railway.app) → Sign up
2. Click **New Project → Deploy from GitHub Repo**
3. Connect your repo

4. For each service, create a **New Service** in the project:

**Gateway:**
- Root directory: `backend`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- No special env vars needed

**Resume Agent:**
- Root directory: `Resume-Screening-Agent/Backend`
- Build command: `pip install -r ../../requirements.txt && python -m spacy download en_core_web_sm`
- Start command: `uvicorn app.unified_server:app --host 0.0.0.0 --port $PORT`
- Add env vars (GROQ, HF, OpenAI, SMTP)

**HR Support Backend:**
- Root directory: `HR_Support/backend`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Add all env vars + attach a Railway volume for persistent storage

**Frontends:** Deploy as static sites with `npm run build` → serve `dist/`

### Railway Pricing

- **Hobby:** $5/mo + usage
- **Pro:** $20/mo per member + usage
- Usage: ~$0.000231/min per vCPU, ~$0.000231/min per GB RAM

---

## 7. Option E: Deploy on DigitalOcean App Platform

### Steps

1. Go to [cloud.digitalocean.com](https://cloud.digitalocean.com) → **App Platform**
2. Click **Create App** → Select GitHub repo
3. Add each service as a **component**:

| Component | Type | Source Directory | Run Command |
|-----------|------|-----------------|-------------|
| Gateway | Web Service | `backend/` | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Resume Agent | Worker/Web | `Resume-Screening-Agent/Backend/` | `uvicorn app.unified_server:app --host 0.0.0.0 --port $PORT` |
| HR Backend | Web Service | `HR_Support/backend/` | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Dashboard | Static Site | `frontend/` | Build: `npm run build`, Output: `dist` |
| HR Frontend | Static Site | `HR_Support/frontend/` | Build: `npm run build`, Output: `dist` |

4. Add env vars per component
5. Deploy

### Pricing: ~$12/mo (Basic plan per service)

---

## 8. Docker Setup

### Dockerfile — Gateway

Create `docker/Dockerfile.gateway`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app/ ./app/
COPY config/ ./config/

EXPOSE 9000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
```

### Dockerfile — Resume Screening Agent

Create `docker/Dockerfile.resume-agent`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY Resume-Screening-Agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY Resume-Screening-Agent/Backend/ ./Backend/
COPY Resume-Screening-Agent/Frontend/ ./Frontend/
COPY Resume-Screening-Agent/JD_Generator/ ./JD_Generator/
COPY Resume-Screening-Agent/Aptitude_Generator/ ./Aptitude_Generator/
COPY Resume-Screening-Agent/config.ini ./config.ini

WORKDIR /app/Backend

EXPOSE 8000

CMD ["uvicorn", "app.unified_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile — HR Support Backend

Create `docker/Dockerfile.hr-backend`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY HR_Support/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY HR_Support/backend/app/ ./app/

# Create directories for persistent data
RUN mkdir -p /data/chroma /data/uploads

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Dockerfile — Frontends (Multi-stage build)

Create `docker/Dockerfile.dashboard`:

```dockerfile
FROM node:20-alpine AS build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY docker/nginx-spa.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx SPA Config

Create `docker/nginx-spa.conf`:

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### docker-compose.yml (All-in-One)

Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  gateway:
    build:
      context: .
      dockerfile: docker/Dockerfile.gateway
    ports:
      - "9000:9000"
    volumes:
      - ./config:/app/config:ro
    restart: always

  resume-agent:
    build:
      context: .
      dockerfile: docker/Dockerfile.resume-agent
    ports:
      - "8000:8000"
    env_file:
      - Resume-Screening-Agent/.env
    volumes:
      - resume-data:/app/Backend/chroma_db
      - resume-reports:/app/Backend/Reports
    restart: always

  hr-backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.hr-backend
    ports:
      - "8001:8001"
    env_file:
      - HR_Support/backend/.env
    volumes:
      - hr-data:/data
      - ./HR_Support/backend/service-account.json:/app/service-account.json:ro
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///data/botivate.db
      - CHROMA_PERSIST_DIR=/data/chroma
      - UPLOAD_DIR=/data/uploads
    restart: always

  dashboard:
    build:
      context: .
      dockerfile: docker/Dockerfile.dashboard
      args:
        VITE_API_URL: http://localhost:9000
    ports:
      - "3000:80"
    restart: always

  hr-frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.dashboard
      args:
        VITE_API_URL: http://localhost:8001
    ports:
      - "5175:80"
    restart: always

volumes:
  resume-data:
  resume-reports:
  hr-data:
```

### Run with Docker Compose

```bash
# Build all images
docker compose build

# Start everything
docker compose up -d

# Check logs
docker compose logs -f

# Stop
docker compose down
```

---

## 9. Environment Variables Reference

### Resume Screening Agent (`Resume-Screening-Agent/.env`)

| Variable | Required | Example |
|----------|----------|---------|
| `GROQ_API_KEY` | ✅ | `gsk_abc123...` |
| `HUGGINGFACE_API_TOKEN` | ✅ | `hf_abc123...` |
| `OPENAI_API_KEY` | ✅ | `sk-proj-abc123...` |
| `SMTP_SERVER` | ✅ | `smtp.gmail.com` |
| `SMTP_PORT` | ✅ | `587` |
| `SMTP_USER` | ✅ | `hiring@company.com` |
| `SMTP_PASSWORD` | ✅ | `abcd efgh ijkl mnop` |

### HR Support Backend (`HR_Support/backend/.env`)

| Variable | Required | Example |
|----------|----------|---------|
| `APP_ENV` | ✅ | `production` |
| `APP_SECRET_KEY` | ✅ | Random 64-char hex string |
| `APP_BASE_URL` | ✅ | `https://hr-api.yourdomain.com` |
| `DATABASE_URL` | ✅ | `sqlite+aiosqlite:///./botivate_master.db` |
| `OPENAI_API_KEY` | ✅ | `sk-proj-abc123...` |
| `OPENAI_MODEL` | Optional | `gpt-4o-mini` (default) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | ✅ | `service-account.json` |
| `GOOGLE_OAUTH_CLIENT_ID` | ✅ | `123.apps.googleusercontent.com` |
| `GOOGLE_OAUTH_CLIENT_SECRET` | ✅ | `GOCSPX-xxx` |
| `GOOGLE_OAUTH_REDIRECT_URI` | ✅ | `https://hr.yourdomain.com/oauth-callback` |
| `SMTP_HOST` | Optional | `smtp.gmail.com` |
| `SMTP_PORT` | Optional | `587` |
| `SMTP_USER` | Optional | `hr@company.com` |
| `SMTP_PASSWORD` | Optional | `abcd efgh ijkl mnop` |
| `JWT_SECRET_KEY` | ✅ | Random 64-char hex string |
| `CHROMA_PERSIST_DIR` | Optional | `./chroma_data` or `/data/chroma` |
| `UPLOAD_DIR` | Optional | `./uploads` or `/data/uploads` |

> **Generate secrets:** `openssl rand -hex 32` or `python -c "import secrets; print(secrets.token_hex(32))"`

---

## 10. Google Cloud OAuth — Production Redirect URIs

When you move to production, you **must** update your Google Cloud Console:

### Step 1: Update Redirect URIs

Go to **APIs & Services → Credentials → Your OAuth Client → Edit**

**Remove:**
```
http://localhost:5175/oauth-callback
```

**Add:**
```
https://hr-support.yourdomain.com/oauth-callback
```

### Step 2: Add Authorized JavaScript Origins (if needed)

```
https://hr-support.yourdomain.com
```

### Step 3: Publish the OAuth App

If you're serving external companies (not just test users):

1. Go to **OAuth consent screen**
2. Click **"Publish App"**
3. Submit for Google verification (see SETUP.md for full process)

### Step 4: Update Authorized Domains

1. Go to **OAuth consent screen → Edit App**
2. Under **Authorized domains**, add: `yourdomain.com`
3. You may need to verify domain ownership via Google Search Console

---

## 11. Database Considerations for Production

### Current: SQLite (Development)

The HR Support agent uses SQLite by default. This works fine for **single-instance** deployments but has limitations:

- **No concurrent writes** — Only one writer at a time
- **No horizontal scaling** — Can't run multiple instances pointing to the same file
- **Backup** — You need to backup the `.db` file manually

### Upgrade to PostgreSQL (Recommended for Production)

If you need multiple instances or better reliability:

1. **Create a PostgreSQL database** (AWS RDS, Render Postgres, Supabase, etc.)

2. **Install the driver:**
   ```bash
   pip install asyncpg
   ```

3. **Update `.env`:**
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@host:5432/botivate
   ```

4. The SQLAlchemy models should work with PostgreSQL without code changes (they use async SQLAlchemy).

### ChromaDB in Production

ChromaDB stores vector embeddings for the RAG pipeline. For production:

- **Single server:** Mount a persistent volume (`/data/chroma`)
- **Multi-server:** Use ChromaDB's [Client/Server mode](https://docs.trychroma.com/usage-guide#running-chroma-in-clientserver-mode) — deploy ChromaDB as a separate service
- **Alternative:** Switch to Pinecone, Weaviate, or Qdrant for managed vector search

---

## 12. Nginx Reverse Proxy Setup

For single-server deployments (EC2, VPS), Nginx routes all traffic:

Create `/etc/nginx/sites-available/botivate`:

```nginx
# Main Dashboard
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Main dashboard (static files)
    root /opt/botivate/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Gateway API
    location /api/ {
        proxy_pass http://127.0.0.1:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Resume Screening Agent (full app)
    location /resume/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HR Support (separate subdomain recommended)
server {
    listen 80;
    server_name hr.yourdomain.com;

    # HR frontend (static files)
    root /opt/botivate/HR_Support/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # HR Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (for streaming chat)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # File uploads
    client_max_body_size 50M;
}
```

Enable the config:

```bash
sudo ln -s /etc/nginx/sites-available/botivate /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

---

## 13. SSL / HTTPS Setup

### Option 1: Certbot (Free — Let's Encrypt)

```bash
# Install
sudo apt install -y certbot python3-certbot-nginx

# Get certificate (auto-configures Nginx)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d hr.yourdomain.com

# Auto-renewal (already set up by certbot)
sudo certbot renew --dry-run
```

### Option 2: AWS ACM (If using ALB/CloudFront)

1. Go to AWS Certificate Manager → **Request Certificate**
2. Add domains: `yourdomain.com`, `*.yourdomain.com`
3. Validate via DNS (add CNAME record)
4. Attach to ALB or CloudFront distribution

### Option 3: Cloudflare (Free SSL + CDN)

1. Add your domain to Cloudflare
2. Change nameservers to Cloudflare's
3. Enable **Full (strict)** SSL mode
4. Cloudflare handles SSL termination + CDN caching for static files

---

## 14. CI/CD Pipeline

### GitHub Actions — Auto-Deploy on Push

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Botivate

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Build frontends
      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Build Dashboard
        run: cd frontend && npm ci && npm run build

      - name: Build HR Frontend
        run: cd HR_Support/frontend && npm ci && npm run build

      # Deploy to server via SSH
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_IP }}
          username: ubuntu
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/botivate
            git pull origin main
            
            # Rebuild Python venvs if requirements changed
            cd backend && source .venv/bin/activate && pip install -r requirements.txt && deactivate
            cd ../Resume-Screening-Agent && source .venv/bin/activate && pip install -r requirements.txt && deactivate
            cd ../HR_Support/backend && source .venv/bin/activate && pip install -r requirements.txt && deactivate
            
            # Copy built frontends
            cd /opt/botivate
            
            # Restart services
            sudo systemctl restart botivate-gateway botivate-resume botivate-hr
            
            echo "Deployed successfully!"
```

Add these **GitHub Secrets:**
- `SERVER_IP` — Your EC2/VPS IP
- `SSH_PRIVATE_KEY` — Your SSH key contents

### For Render / Railway

They auto-deploy on push to `main` — no CI/CD config needed.

---

## 15. Monitoring & Logs

### Systemd Logs (EC2)

```bash
# View live logs
sudo journalctl -u botivate-gateway -f
sudo journalctl -u botivate-resume -f
sudo journalctl -u botivate-hr -f

# View last 100 lines
sudo journalctl -u botivate-hr -n 100 --no-pager
```

### Docker Logs

```bash
docker compose logs -f hr-backend
docker compose logs --tail=100 resume-agent
```

### Health Check Endpoints

Set up a monitoring service (UptimeRobot, Better Uptime, etc.) to ping:

| Endpoint | Expected |
|----------|----------|
| `https://yourdomain.com/api/health` | `{"status": "healthy"}` |
| `https://yourdomain.com/api/agents/health/all` | All agents healthy |
| `https://resume-agent.yourdomain.com/health` | `{"status": "healthy"}` |
| `https://hr-api.yourdomain.com/health` | `{"status": "healthy"}` |

### Recommended Monitoring Stack

| Tool | Purpose | Cost |
|------|---------|------|
| [UptimeRobot](https://uptimerobot.com) | Uptime monitoring | Free (50 monitors) |
| [Sentry](https://sentry.io) | Error tracking | Free (5K events/mo) |
| CloudWatch (AWS) | Metrics & alarms | Included with EC2 |

---

## 16. Cost Estimates

### Single Server (EC2 / VPS)

| Component | Monthly Cost |
|-----------|-------------|
| EC2 t3.large (8GB RAM) | $38/mo (reserved) |
| EBS 30GB storage | $2.40/mo |
| Elastic IP | Free (if attached) |
| Domain name | ~$12/year |
| SSL (Certbot) | Free |
| **Total** | **~$41/mo** |

### Render (Managed PaaS)

| Component | Monthly Cost |
|-----------|-------------|
| Gateway (Free tier) | $0 |
| Resume Agent (Standard) | $7/mo |
| HR Backend (Standard) | $7/mo |
| Dashboard (Static - Free) | $0 |
| HR Frontend (Static - Free) | $0 |
| Disk (1GB) | $0.25/mo |
| **Total** | **~$14/mo** |

### Railway

| Component | Monthly Cost |
|-----------|-------------|
| 3 services (~1GB RAM each) | ~$15-25/mo (usage-based) |
| Hobby plan | $5/mo |
| **Total** | **~$20-30/mo** |

### AWS ECS/Fargate (Enterprise)

| Component | Monthly Cost |
|-----------|-------------|
| 3 Fargate tasks | ~$40-80/mo |
| ALB | $16/mo |
| ECR | ~$1/mo |
| RDS PostgreSQL (if used) | $15-30/mo |
| **Total** | **~$72-127/mo** |

---

## Quick Decision Guide

| Scenario | Recommended Platform |
|----------|---------------------|
| **Demo / Personal project** | Render (free + standard) |
| **Startup / Small team** | EC2 single server or Railway |
| **Enterprise / Auto-scaling** | AWS ECS/Fargate or Kubernetes |
| **Zero DevOps** | Render or Railway |
| **Full control + cheapest** | EC2 t3.large + Nginx |
| **India-based (low latency)** | AWS Mumbai (`ap-south-1`) or DigitalOcean Bangalore |

---

## Final Production Checklist

- [ ] All API keys set as environment variables (never in code)
- [ ] `APP_SECRET_KEY` and `JWT_SECRET_KEY` are random, strong, and unique
- [ ] `APP_ENV=production` in HR Support `.env`
- [ ] Google OAuth redirect URI updated to production URL
- [ ] Google OAuth app published (or test users added)
- [ ] `service-account.json` securely stored (not in git)
- [ ] CORS origins updated to production domains
- [ ] `workspace.config.json` updated with production URLs
- [ ] Frontends built with `npm run build` (not dev mode)
- [ ] SSL/HTTPS enabled
- [ ] Monitoring/health checks configured
- [ ] Backup strategy for SQLite DB (if not using PostgreSQL)
- [ ] `--reload` flag REMOVED from uvicorn production commands
- [ ] Log level set appropriately (INFO or WARNING, not DEBUG)
