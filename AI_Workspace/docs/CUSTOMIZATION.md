# Customization Guide

## White-Label Branding

Edit `workspace.config.json` in the project root:

```json
{
  "company": {
    "name": "Your Company Name",
    "tagline": "Your Tagline",
    "logo": "/assets/logo.png",
    "primaryColor": "#your-hex-color"
  }
}
```

No code changes needed — the frontend reads this config at runtime.

## Adding a New Agent

### 1. Create Backend Plugin

```
backend/app/agents/your_agent/
├── agent.json          ← Metadata + required env keys
├── __init__.py         ← Exports `router` (FastAPI APIRouter)
├── routers/            ← API endpoint files
├── services/           ← Business logic
└── models/             ← Database models (optional)
```

### 2. agent.json Example

```json
{
  "name": "My Custom Agent",
  "description": "What this agent does",
  "version": "1.0.0",
  "icon": "Bot",
  "gradient": ["#8b5cf6", "#6d28d9"],
  "category": "Custom",
  "features": ["Feature 1", "Feature 2"],
  "enabled": true,
  "required_env_keys": ["OPENAI_API_KEY"]
}
```

### 3. __init__.py Example

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/hello")
async def hello():
    return {"message": "Hello from my agent!"}
```

### 4. Register in workspace.config.json (Optional)

```json
{
  "agents": {
    "your_agent": {
      "enabled": true,
      "displayName": "My Custom Agent"
    }
  }
}
```

### 5. Add Frontend Page (Optional)

Create `frontend/src/agents/your_agent/index.tsx` and register it in `App.tsx`.

### 6. Restart

```bash
# Dev mode
uvicorn backend.app.main:app --reload

# Docker
docker-compose restart
```

Your agent appears on the dashboard automatically.

## Removing an Agent

Three options (pick one):
1. Delete the folder: `backend/app/agents/your_agent/`
2. Set `"enabled": false` in the agent's `agent.json`
3. Set `"enabled": false` in `workspace.config.json`

Restart the server. No other agents affected.

## Feature Flags

Control features in `workspace.config.json`:

```json
{
  "features": {
    "gmail_integration": true,
    "email_notifications": false,
    "google_sheets_sync": true
  }
}
```

## Available Icons

The frontend supports these Lucide icons for agent cards:
`Headphones`, `UserSearch`, `Bot`, `Shield`, `Brain`, `FileText`, `Mail`, `Settings`, `BarChart3`, `Calendar`, `Users`, `Briefcase`
