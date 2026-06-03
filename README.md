# EarlyBird Convert — PDF / DOCX → Excel

Convert Task Allocation documents (PDF, DOCX, DOC) to a structured Excel sheet using a deterministic offline parsing engine. Saves conversion results automatically to MongoDB.

---

## Architecture

```
┌─────────────────────────────┐        ┌───────────────────────────┐
│  Next.js Frontend (Vercel)  │──HTTP──▶│  FastAPI Backend (Railway) │
│  /api/convert  (proxy)      │        │  /convert                 │
└─────────────────────────────┘        └───────────────────────────┘
                                                     │
                                               (Save Results)
                                                     │
                                                     ▼
                                          ┌──────────────────────┐
                                          │     MongoDB Atlas    │
                                          └──────────────────────┘
```

- **Frontend** — Next.js 15, deployed on **Vercel**
- **Backend** — FastAPI (Python), deployed on **Railway** (or Render/Fly.io)
- **Database** — MongoDB (for storing history and parsed results)

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
cp .env.example .env   # fill in your MONGODB_URI

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

## Production Deployment & Build Commands

### Backend → Railway (or Render)

- **Build Command / Nixpacks config**: Auto-detected (FastAPI / python)
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT` (defined in `pdf_service/Procfile`)
- **Environment Variables**:
  - `MONGODB_URI`: `mongodb+srv://user:password@cluster.mongodb.net/?appName=Cluster0`

### Frontend → Vercel

- **Framework Preset**: Next.js
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Install Command**: `npm install`
- **Environment Variables**:
  - `PYTHON_SERVICE_URL`: `https://your-backend.railway.app`
  - `NEXT_PUBLIC_MAX_FILE_SIZE_MB`: `50`
  - `NEXT_PUBLIC_APP_NAME`: `EarlyBird Convert`

---

## Environment Variables Reference

| File | Variable | Description |
|---|---|---|
| `.env.local` | `PYTHON_SERVICE_URL` | URL of the Python backend |
| `.env.local` | `NEXT_PUBLIC_MAX_FILE_SIZE_MB` | Max upload size shown in UI |
| `pdf_service/.env` | `MONGODB_URI` | MongoDB Connection String |

---

## Supported File Types

| Type | Extension | Parser |
|---|---|---|
| PDF | `.pdf` | pdfplumber + Deterministic Regex Parsing |
| Word (modern) | `.docx` | python-docx + Deterministic Regex Parsing |
| Word (legacy) | `.doc` | docx2txt fallback |

---

## License

MIT
