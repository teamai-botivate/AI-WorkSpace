# 📧 Comprehensive Google Workspace Integration Guide
**Botivate HR System: Multi-Tenant Architecture**

This document provides a detailed, step-by-step guide on how the Botivate HR system integrates with Google Workspace (Gmail, Google Sheets, Google Drive) and how dynamic, multi-tenant email formatting is functioning behind the scenes.

---

## 1. Multi-Tenant Email Formatting Architecture
Since Botivate HR acts as a central SaaS engine serving multiple companies, hardcoding "Botivate HR" in emails would ruin the white-label experience for client companies. 

**How we made it dynamic:**
- We redesigned the `NOTIFICATION_TEMPLATE` in `email_service.py` to accept dynamic kwargs: `company_name`, `action_by`, `action_role`, and `status`.
- The template now uses a sleek `135deg` linear gradient header that adapts the `<h1>` text to the `{{ company_name }}`.
- Below the email body, a clean info box specifically states who triggered the action (`{{ action_by }}`) and their role (`{{ action_role }}`), along with the current Request Status.
- In `approval_service.py`, whenever an Employee submits a request OR a Manager makes a decision, the code dynamically injects `company.name` and the specific user's info into the renderer before handing it off to the OAuth email sender.
- **Result:** Employees receive premium emails from their specific company ("TCS", "Zomato", etc.) without knowing that Botivate handled the heavy lifting.

---

## 2. Setting Up Google Cloud Credentials (The Prerequisites)
To enable Google Sheets, Drive, and Gmail access, the backend requires a single **Google Cloud Project** connected to a Service Account and an OAuth 2.0 Web Client.

### Step 2.1: Create the Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com).
2. Click **Create Project** -> Name it "Botivate HR Integration".
3. Wait for the project to provision.

### Step 2.2: Enable The APIs
In your new project, navigate to **APIs & Services > Library**.
Search for and explicitly ENABLE the following three APIs:
- **Gmail API**
- **Google Sheets API**
- **Google Drive API**

---

## 3. Google Sheets & Google Drive (Service Account Integration)
The system uses a **Service Account** to silently read and write to employee databases (Sheets) and handle files (Drive) on the backend without user intervention.

### How to configure:
1. Go to **APIs & Services > Credentials**.
2. Click **Create Credentials > Service Account**.
3. Name it `botivate-db-agent`. Click **Create and Continue**.
4. Skip role assignments for now and click **Done**.
5. Click on the newly created Service Account -> go to the **Keys** tab.
6. Click **Add Key > Create New Key > JSON**.
7. Download this JSON file. 
8. **CRITICAL:** Place this file inside your backend directory safely and reference its path in your `.env` as `GOOGLE_SERVICE_ACCOUNT_JSON=path/to/credentials.json`.
9. **Share the Files:** For Botivate to access a company's Google Sheet or Drive Folder, the Company HR MUST "Share" their Sheet/Folder with the exact email address of the Service Account (e.g., `botivate-db-agent@project-id.iam.gserviceaccount.com`).

---

## 4. Gmail Access via OAuth 2.0 (Client Integration)
Unlike the Service Account which is a "robot" account, **we want emails to actually come from the HR's real Gmail ID**. This requires OAuth 2.0 flow.

### Step 4.1: Create OAuth 2.0 Client ID
1. In Google Cloud Console, go to **APIs & Services > OAuth Consent Screen**.
2. Select **External**, fill in App Name ("Botivate HR") and user support email.
3. Under **Scopes**, click "Add or Remove Scopes" and manually add `https://www.googleapis.com/auth/gmail.send`.
4. Proceed and save.
5. Next, go to **Credentials > Create Credentials > OAuth Client ID**.
6. Set Application type to **Web Application**.
7. Add an **Authorized Redirect URI**:
   - `http://localhost:5173/oauth-callback` (for local development)
8. Click Create. Copy the **Client ID** and **Client Secret**.
9. Add these to your backend `.env`:
   ```env
   GOOGLE_OAUTH_CLIENT_ID="your_client_id_here"
   GOOGLE_OAUTH_CLIENT_SECRET="your_client_secret_here"
   GOOGLE_OAUTH_REDIRECT_URI="http://localhost:5173/oauth-callback"
   ```

### Step 4.2: The OAuth Flow (How it actually works)
1. **The Consent:** In the React Frontend (`OAuthCallbackPage.jsx`), an HR logs into their Google Account and accepts the prompt that says "Botivate HR wants to send email on your behalf".
2. **The Code:** Google redirects them back to `localhost:5173/oauth-callback` and attaches an Authorization `code` in the URL.
3. **The Exchange:** The frontend sends this code to our FastAPI backend (`/api/companies/oauth-exchange`). The backend exchanges the code for a **Refresh Token**.
4. **The Storage:** We encrypt and store this `refresh_token` in the SQLite database specifically tied to that HR's Company ID.
5. **The Magic Dispatch:** Later, when Manager X approves a leave, `email_service.py::send_oauth_email()` pulls the `refresh_token` for Manager X's company. It dynamically recreates Google Credentials on-the-fly, generates an Access Token in milliseconds, packages the beautiful `NOTIFICATION_TEMPLATE`, and hits the Gmail API's `messages().send(userId='me', body=...)`. 
6. **Delivery:** The email fires, perfectly bypassing SMTP locks, perfectly branded, originating natively from the HR's real sent folder.
