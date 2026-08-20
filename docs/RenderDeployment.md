# Render Cloud Deployment Guide — CampusDesk AI

Follow this 2-minute guide to deploy **CampusDesk AI** to Render.com with a permanent, 24/7 HTTPS URL.

---

## 🚀 Step 1: Connect GitHub Repo to Render

1. Go to **[Render.com Dashboard](https://dashboard.render.com)** and log in with GitHub.
2. Click **New +** (top right) $\rightarrow$ Select **Web Service**.
3. Choose **Build and deploy from a Git repository**.
4. Select your repository: **`ArnavPundir22/campusdesk-ai`**.

---

## ⚙️ Step 2: Configure Render Build Settings

Render will auto-detect `render.yaml` and `requirements.txt`. Verify these settings:

- **Name:** `campusdesk-ai`
- **Environment:** `Python`
- **Region:** `Oregon (US West)` or nearest
- **Branch:** `main`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

---

## 🔑 Step 3: Set Environment Variables on Render

Under the **Environment Variables** tab in Render, add these 6 secrets:

| Key | Description |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API Key |
| `NOTION_API_KEY` | Your Notion Integration Token |
| `NOTION_REQUESTS_DB_ID` | `3c282ead-0f2a-8197-a296-f423e734e8e3` |
| `NOTION_RUN_LOG_DB_ID` | `3c282ead-0f2a-81f5-bb22-f8d901375430` |
| `NOTION_RULEBOOK_DB_ID` | `3c282ead-0f2a-812c-9bc8-f4c9f07339f3` |
| `RESEND_API_KEY` | Your Resend API Key |
| `MOCK_NOTION` | `false` |
| `MOCK_EMAIL` | `false` |

---

## 🎉 Step 4: Click Deploy!

1. Click **Create Web Service**.
2. Render will build and deploy your service in ~60 seconds.
3. You will get a permanent public URL, for example:  
   `https://campusdesk-ai.onrender.com`

---

## 🔗 Step 5: Update Your Google Form Webhook

In your Google Apps Script `Code.gs`, update line 2 with your permanent Render URL:

```javascript
var BACKEND_URL = "https://campusdesk-ai.onrender.com/api/v1/requests/submit";
```

Your system is now **live 24/7 on the cloud**!
