# Credentials Folder

This folder holds all sensitive credential files for the AI Workspace.

## Structure

```
credentials/
├── google/
│   ├── service-account.json    ← Google Sheets, Drive API access
│   └── client_secret.json      ← Google OAuth (Gmail integration)
├── tokens/                     ← Auto-generated after OAuth flows
│   └── (token files appear here automatically)
└── README.md                   ← This file
```

## Setup Instructions

### 1. Google Service Account (for Sheets/Drive)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable Google Sheets API & Google Drive API
3. Create a Service Account → Download JSON key
4. Save as `credentials/google/service-account.json`

### 2. Google OAuth Client (for Gmail)
1. In Google Cloud Console → APIs & Services → Credentials
2. Create OAuth 2.0 Client ID (Web Application)
3. Add authorized redirect URI: `http://localhost:8000/api/auth/google/callback`
4. Download client secret JSON
5. Save as `credentials/google/client_secret.json`

### 3. Tokens
The `tokens/` folder is auto-populated when users complete OAuth flows.
Do not manually add files here.

## Security
- **NEVER** commit credential files to git
- These paths are in `.gitignore` by default
- In production, mount credentials as Docker secrets or volumes
