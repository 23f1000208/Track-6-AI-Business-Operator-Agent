# OpsPilot AI — Setup & Local Running Guide

Follow these instructions to run OpsPilot AI locally or deploy to Google Cloud Run.

---

## Prerequisites
- Python 3.10+ (Tested on Python 3.12)
- Node.js 18+ & npm 9+
- (Optional) Docker

---

## 1. Quick Local Start (Demo Mode - No API keys required!)

OpsPilot AI works out of the box in high-fidelity Demo Mode with synthetic business data across 15 payments and 10 corporate accounts.

### Step 1: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Build the React Frontend
```bash
cd ../frontend
npm install
npm run build
```

### Step 3: Launch the Application
```bash
cd ../backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 4: Open in Browser
Open `http://localhost:8000` in your web browser! The Command Center UI and all API endpoints are fully active.

---

## 2. Running Frontend in Hot-Reload Dev Mode (Optional)

If you are developing UI features:
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```
Open `http://localhost:5173`. Vite proxies `/api` calls directly to the FastAPI server at port 8000.

---

## 3. Running Automated Tests

Run the full pytest suite verifying business rules, security, idempotency, failure simulation, and end-to-end execution:
```bash
pytest backend/tests/test_opspilot.py -v
```

---

## 4. Google Cloud Run Deployment

Deploy to Google Cloud Run with single-command Docker build:

```bash
# 1. Build Docker image
docker build -t gcr.io/YOUR_PROJECT_ID/opspilot-ai:latest .

# 2. Push to Google Container Registry / Artifact Registry
docker push gcr.io/YOUR_PROJECT_ID/opspilot-ai:latest

# 3. Deploy to Cloud Run (min-instances=0 for cost efficiency)
gcloud run deploy opspilot-ai \
  --image gcr.io/YOUR_PROJECT_ID/opspilot-ai:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --set-env-vars DEMO_MODE=true
```
