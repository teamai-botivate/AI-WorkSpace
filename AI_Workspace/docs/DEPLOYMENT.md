# Deployment Guide

## Quick Start (Docker)

```bash
# 1. Clone the repository
git clone <repo-url>
cd AI_Workspace

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Add credentials
# Place Google service account JSON in credentials/google/
# See credentials/README.md for details

# 4. Deploy
docker-compose up -d --build
```

Your workspace will be available at `http://localhost` (port 80).

## Development Mode

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on port 3000, proxies `/api/*` to backend on 8000.

## Production Deployment

### Recommended Specs
- **RAM:** 4GB minimum (6GB recommended)
- **CPU:** 2 cores minimum
- **Storage:** 20GB+
- **OS:** Ubuntu 22.04 LTS

### DigitalOcean / AWS
1. Spin up a droplet/instance (4GB RAM, 2 vCPU)
2. Install Docker and Docker Compose
3. Clone repo, configure .env, deploy with `docker-compose up -d`

### Environment Variables
All configuration is done through `.env` — see `.env.example` for the full list.

### SSL/HTTPS
Add Let's Encrypt with Certbot or use a reverse proxy (Cloudflare, AWS ALB).

## Architecture

```
Browser → Nginx (port 80)
              ├── /api/*     → FastAPI (port 8000)
              ├── /static/*  → Agent static files
              └── /*         → React SPA (built files)
```

## Monitoring

- Health check: `GET /api/health`
- Agent status: `GET /api/agents`
- Per-agent health: `GET /api/agents/{name}/health`
