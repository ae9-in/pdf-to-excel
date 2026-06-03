# EarlyBird Convert — PDF / DOCX → Excel

Convert Task Allocation documents (PDF, DOCX, DOC) to a structured Excel sheet using AI-powered parsing.

---

## Architecture

```
┌─────────────────────────────┐        ┌───────────────────────────┐
│  Next.js Frontend (Vercel)  │──HTTP──▶│  FastAPI Backend (Railway) │
│  /api/convert  (proxy)      │        │  /convert                 │
└─────────────────────────────┘        └───────────────────────────┘
```

- **Frontend** — Next.js 15, deployed on **Vercel**
- **Backend** — FastAPI (Python), deployed on **Railway** (or Render/Fly.io)

---

## Local Development

### 1. Start the Python backend

```bash
cd pdf_service
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # fill in your ANTHROPIC_API_KEY

uvicorn main:app --reload --port 8000
```

### 2. Start the Next.js frontend

```bash
# In the project root
cp .env.example .env.local   # PYTHON_SERVICE_URL=http://127.0.0.1:8000
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Production Deployment

### Backend → Railway (or Render)

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. Select the `pdf_service/` folder as the root directory
3. Add environment variables in the Railway dashboard (copy from `pdf_service/.env.example`)
4. Railway auto-detects the `Procfile` and runs:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. Copy the generated URL (e.g. `https://pdf-service-production.up.railway.app`)

### Frontend → Vercel

1. Push this repository to GitHub
2. Go to [vercel.com](https://vercel.com) → **New Project** → Import the repo
3. Set these **Environment Variables** in Vercel:
   | Variable | Value |
   |---|---|
   | `PYTHON_SERVICE_URL` | `https://your-backend.railway.app` |
   | `NEXT_PUBLIC_MAX_FILE_SIZE_MB` | `50` |
   | `NEXT_PUBLIC_APP_NAME` | `EarlyBird Convert` |
4. **Build settings** (auto-detected from `vercel.json`):
   - Framework: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`
5. Click **Deploy** ✓

---

## Environment Variables Reference

| File | Variable | Description |
|---|---|---|
| `.env.local` | `PYTHON_SERVICE_URL` | URL of the Python backend |
| `.env.local` | `NEXT_PUBLIC_MAX_FILE_SIZE_MB` | Max upload size shown in UI |
| `pdf_service/.env` | `ANTHROPIC_API_KEY` | Claude API key |
| `pdf_service/.env` | `ANTHROPIC_MODEL` | Claude model (optional) |

---

## Supported File Types

| Type | Extension | Parser |
|---|---|---|
| PDF | `.pdf` | pdfplumber + Claude AI |
| Word (modern) | `.docx` | python-docx + Claude AI |
| Word (legacy) | `.doc` | docx2txt fallback |

---

## License

MIT
