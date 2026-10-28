# 🚀 Deployment Guide: Streamlit Cloud & Render

This guide provides step-by-step instructions for deploying **Secure Enterprise RAG Copilot (RBAC)** across modern cloud platforms.

The application follows an **enterprise decoupled architecture**:
- **Backend (API + Vector Store)**: Hosted on **Render** (FastAPI + ChromaDB + SentenceTransformers).
- **Frontend (UI)**: Hosted on **Streamlit Community Cloud** (Zero-cost managed Streamlit hosting).

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────┐           ┌──────────────────────────────────────┐
│     Streamlit Community Cloud   │           │             Render Cloud             │
│    (frontend/app.py)            │           │         (FastAPI + ChromaDB)         │
│                                 │   HTTPS   │                                      │
│  • Modern Dark Glassmorphic UI  │ ────────> │  • /login (JWT Authentication)       │
│  • 5 Multi-Tab Workspaces       │   REST    │  • /ask (Pre-retrieval RBAC filter)  │
│  • Observability Telemetry      │           │  • /catalog & /system-info           │
│  • Connection Resolver          │           │  • ChromaDB Local HNSW Vector Store  │
└─────────────────────────────────┘           └──────────────────────────────────────┘
                                                                 │
                                                                 ▼
                                                      Groq LPU Cloud (LLM)
```

---

## Part 1: Deploy Backend on Render (FastAPI + ChromaDB)

### Option A: Using Render Blueprint (`render.yaml`) — *Recommended (1-Click)*

1. Push your repository to GitHub:
   ```bash
   git push origin main
   ```
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** ➔ **Blueprint**.
4. Connect your GitHub repository `Secure-Enterprise-RAG-Copilot-RBAC-`.
5. Render detects `render.yaml`. Click **Apply**.
6. Under **Environment Variables**, set your `GROQ_API_KEY`:
   - `GROQ_API_KEY`: `gsk_...` (from [console.groq.com](https://console.groq.com))
7. Click **Create Service**.

---

### Option B: Manual Web Service Setup on Render

1. Log in to [Render Dashboard](https://dashboard.render.com) and click **New +** ➔ **Web Service**.
2. Select **Build and deploy from a Git repository** and connect your repository.
3. Configure the following settings:
   - **Name:** `secure-enterprise-rag-backend`
   - **Region:** Any (e.g. `Oregon (US West)` or `Frankfurt (EU)`)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python -m backend.ingest
     ```
   - **Start Command:**
     ```bash
     uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type:** `Free`

4. Add the following **Environment Variables**:
   | Variable | Value | Description |
   | :--- | :--- | :--- |
   | `PYTHON_VERSION` | `3.11.9` | Ensures stable binary compatibility |
   | `GROQ_API_KEY` | `gsk_your_groq_key` | From [console.groq.com](https://console.groq.com) |
   | `GROQ_MODEL` | `openai/gpt-oss-20b` | High-speed LLM on Groq |
   | `SECRET_KEY` | *(generate a random string)* | Used for JWT signing |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `120` | Session lifetime |
   | `CHROMA_DB_PATH` | `./chroma_db` | Persistent vector store path |

5. Click **Create Web Service**.
6. Once deployed, copy your Render URL:
   `https://secure-enterprise-rag-backend.onrender.com`

---

## Part 2: Deploy Frontend on Streamlit Community Cloud

1. Log in to [Streamlit Community Cloud](https://share.streamlit.io).
2. Click **New app**.
3. Select your repository:
   - **Repository:** `gagan8605/Secure-Enterprise-RAG-Copilot-RBAC-`
   - **Branch:** `main`
   - **Main file path:** `frontend/app.py`
4. Expand **Advanced settings...** ➔ **Secrets**.
5. Paste your Render backend URL into the secrets editor:
   ```toml
   BACKEND_URL = "https://your-render-service-name.onrender.com"
   ```
6. Click **Deploy!**

Your Streamlit app will build and go live at `https://<your-app-name>.streamlit.app`!

---

## ⚡ Handling Render Free-Tier Cold Starts

> [!NOTE]
> Render free-tier web services spin down after 15 minutes of inactivity. The first request after sleep takes 30-50 seconds while the container boots up.

The frontend includes **built-in cold start tolerance**:
- Requests have a 60-second timeout buffer.
- The login and status modules display helpful progress spinners during server wake-up.
- Users can test backend health anytime via the **⚙️ Backend Server Connection & Status** expander in the UI.

---

## 🔍 Verification & Health Checks

1. Test Backend Health:
   ```bash
   curl https://<your-render-url>/health
   # Expected response: {"status": "healthy", "service": "Secure Enterprise RAG Copilot"}
   ```
2. Test System Architecture Info:
   ```bash
   curl https://<your-render-url>/system-info
   ```
3. Interactive Swagger API Docs:
   Visit `https://<your-render-url>/docs` in your browser.
