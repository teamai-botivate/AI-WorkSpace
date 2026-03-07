# Credentials Setup Guide

## Overview

All credentials are stored in the `credentials/` folder and referenced via `.env`.

## Required Credentials

### 1. OpenAI API Key
- **Used by:** HR Support chatbot (RAG + chat)
- **Get it:** https://platform.openai.com/api-keys
- **Set in .env:** `OPENAI_API_KEY=sk-...`

### 2. Groq API Key
- **Used by:** Resume Screening (AI analysis, JD generation)
- **Get it:** https://console.groq.com/keys (free tier available)
- **Set in .env:** `GROQ_API_KEY=gsk_...`

## Optional Credentials

### 3. Google Service Account
- **Used by:** Google Sheets integration
- **Setup:**
  1. Google Cloud Console → Create Project
  2. Enable Google Sheets API + Google Drive API
  3. Create Service Account → Download JSON
  4. Save to `credentials/google/service-account.json`

### 4. Google OAuth Client
- **Used by:** Gmail integration (fetching resumes from email)
- **Setup:**
  1. Google Cloud Console → APIs & Services → Credentials
  2. Create OAuth 2.0 Client ID (Web Application)
  3. Authorized redirect URI: `http://localhost:8000/api/auth/google/callback`
  4. Save client secret to `credentials/google/client_secret.json`
  5. Set in .env: `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`

### 5. HuggingFace Token
- **Used by:** Visual resume analysis
- **Get it:** https://huggingface.co/settings/tokens
- **Set in .env:** `HUGGINGFACE_API_TOKEN=hf_...`

### 6. SMTP Credentials
- **Used by:** Email automation (candidate outreach, notifications)
- **For Gmail:**
  - `SMTP_SERVER=smtp.gmail.com`
  - `SMTP_PORT=587`
  - `SMTP_USER=your-email@gmail.com`
  - `SMTP_PASSWORD=your-app-password`
  - Note: Use Gmail App Passwords, not your regular password

## Security Best Practices

- Never commit `.env` or credential files to git
- Use Docker secrets or environment variables in production
- Rotate API keys periodically
- Use least-privilege service accounts
