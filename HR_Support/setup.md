# Botivate HR - System Architecture & Gmail OAuth 2.0 Integration Setup

This document serves as a reference manual for the Botivate HR backend setup, and explicitly documents our **Gmail via OAuth 2.0** integration flow so you never forget how the email sending works autonomously.

---

## 🚀 1. Why Did We Use OAuth 2.0 for Gmail?
Normally, backend systems use simple SMTP (like `smtp.gmail.com` + App Passwords) to send emails. However, we wanted Botivate HR to be **Client-Centric**. 
We didn't want any HR company to send us their email ID and plaintext passwords. Instead, we allow them to log in via a Google Window ("Sign in with Google"). This way:
1. They grant our App (Client ID) **"Send Email" (`https://www.googleapis.com/auth/gmail.send`)** permission. 
2. We receive a secure **Refresh Token**.
3. We store that token in their company's `botivate_master.db` mapping.
4. Any time Ghanshyam (or any employee) requests leave, the system acts *on behalf of that specific HR company's email address* silently in the background!

---

## ⚙️ 2. The 3-Step Google Cloud Console Setup
To make this OAuth flow work, you must always ensure the Google Cloud Console is configured correctly:

### Step 1: Create the OAuth Client ID
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create/Select a Project.
3. Search for **APIs & Services > Credentials**.
4. Click **Create Credentials > OAuth Client ID** (Type: Web Application).
5. Add Authorized Redirect URIs:
   - `http://localhost:5173/oauth-callback` (For Local Dev)
   - `https://your-domain.com/oauth-callback` (For Prod)
6. Copy the Generated **Client ID** and **Client Secret**.

### Step 2: Enable Required APIs
You must explicitly tell Google which APIs this token will be allowed to use:
- **Gmail API**: Required to send emails (`service.users().messages().send`).
- **Google Sheets API**: Required to fetch and update employee databases.
- **Google Drive API**: Required to read file structures.

### Step 3: Set Environment Variables
The Backend `.env` requires these 3 keys to function:
```env
GOOGLE_OAUTH_CLIENT_ID="your-client-id.apps.googleusercontent.com"
GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret"
GOOGLE_OAUTH_REDIRECT_URI="http://localhost:5173/oauth-callback"
```

---

## 🧠 3. How the Backend Code Works (The OAuth Flow)

### Front-End Trigger (`OAuthCallbackPage.jsx`)
When the HR successfully logs into their Google Account, Google redirects them back to our Vite frontend: `http://localhost:5173/oauth-callback?code=4/0Axx...`
The frontend immediately takes this `code` and POSTs it to the backend (`/api/companies/oauth-exchange`).

### Back-End Token Exchange (`company_service.py`)
1. The backend hits `https://oauth2.googleapis.com/token` and trades the exact `code` for an `access_token` AND a `refresh_token`.
2. The `access_token` expires in 1 hour. But the **`refresh_token` never expires!**
3. We extract the user's Email address by decoding the ID Token (JWT).
4. We encrypt and save this `refresh_token` deep inside the `DatabaseConnection` nested config dictionary for that company.

### Back-End Async Email Dispatch (`email_service.py`)
Whenever an approval notification is fired (`approval_service.py`):
1. The backend queries the database for the Company's active `google_refresh_token`.
2. The custom `send_oauth_email()` helper rebuilds Google `Credentials`:
    ```python
    creds = Credentials(
        None, # Access token empty initially
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_oauth_client_id,
        client_secret=settings.google_oauth_client_secret
    )
    ```
3. The Google API Python Library automatically contacts Google servers, instantly gets a fresh Access Token using the refresh token.
4. It builds a `MIMEMultipart` HTML email, encodes it into safe **Base64 (urlsafe_b64encode)**.
5. It hits the Gmail API: `service.users().messages().send(userId='me', body={'raw': encoded_email}).execute()`.
6. Boom! The email is fired seamlessly from the HR's email address without them lifting a finger.

---

## 🎨 4. Email Formatting Layout
The `email_service.py` now includes a perfectly responsive HTML/Inline-CSS template `NOTIFICATION_TEMPLATE` that looks exactly like a Next-Gen Saas Notification:
- **Linear Gradient Header**
- **Box shadows**
- **Custom typography (`Inter`, `Segoe UI`)**
It dynamically renders the Title, Message Body, and a nice CTA button back to the Portal!
