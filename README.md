# Brew
Brew better connections.

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm 9+

### 1) Setup (first time)
1. Create and activate a virtual environment (Windows Git Bash):
   - Create: `python -m venv .venv`
   - Install deps: `.venv/Scripts/pip.exe install -r requirements.txt`
   - Note: If activation is flaky in Git Bash, call Python directly as shown below.
2. Create a `.env` in project root:
   - `OPENAI_API_KEY=your_key_here`

### 2) Data locations
- Raw CSV: `src/data/raw/linkedinuserprofiles.csv`
- Processed profiles: `src/data/processed/profiles.json`
- Embeddings: `src/data/processed/{embeddings.json, embeddings.npy, embeddings_metadata.json}`

### 3) Generate processed profiles and embeddings
Run with the venv's Python to avoid PATH issues on Windows:

```bash
.venv/Scripts/python.exe src/preprocess.py
.venv/Scripts/python.exe src/create_embeddings.py
```

### 4) Run the services locally
In three terminals:

1) ML service (FastAPI):
```bash
.venv/Scripts/python.exe src/ml_service.py
# Serves on http://localhost:8000
```

2) Node backend (proxy API):
```bash
cd backend
npm install
# Point backend to ML service (optional if local default works)
# set PYTHON_ML_URL=http://127.0.0.1:8000  (Windows CMD)
# export PYTHON_ML_URL=http://127.0.0.1:8000 (bash)
npm start
# Serves on http://localhost:3001 (see backend logs)
```

3) React frontend:
```bash
cd frontend
npm install
npm start
# Opens http://localhost:3000
```

### 5) Quick checks
- ML service health:
```bash
curl "http://localhost:8000/health"
```
- Search directly (ML service):
```bash
curl "http://localhost:8000/search?query=waterloo%20grad&num_results=5"
```
- Search via Node backend:
```bash
curl "http://localhost:3001/api/search?query=waterloo%20grad&num_results=5"
```

### 6) Environment variables
- Root `.env` (used by Python):
  - `OPENAI_API_KEY` required to build/query embeddings
- Backend env (e.g., Railway/Render/local):
  - `PYTHON_ML_URL` points to the running ML service (e.g. `https://your-ml.onrender.com` or `http://127.0.0.1:8000`)

### 7) Common Windows notes
- If `pip`/`numpy` import issues occur in Git Bash, use the venv executables directly:
  - Install: `.venv/Scripts/pip.exe install -r requirements.txt`
  - Run: `.venv/Scripts/python.exe src/preprocess.py`
- Avoid `::1` (IPv6) loopback mismatches; prefer `http://127.0.0.1:8000` for `PYTHON_ML_URL` locally.

### 8) Deploy (brief)
- Frontend (Vercel): project root contains `vercel.json` that builds `frontend/`
- Backend (Railway/Render): set `PYTHON_ML_URL`
- ML service (Render recommended): ensure `OPENAI_API_KEY` is set and service port is provided via `PORT` env (the code respects it, defaults to 8000)

### Next:
- Move data to vector store
- Deploy ML service and backend with Railway or Render, frontend with Vercel
- Move message generation to modal/dropdown
- GET MORE DATA!