CatalogAI - Authenticity Detection
=================================

Overview
--------
CatalogAI is a full‑stack template for detecting AI‑generated/synthetic product images. It ships with:

- Backend (FastAPI, Python 3.11): image preprocessing, feature extraction, SVM classifier, retraining APIs
- Frontend (Next.js/React): modern UI to upload images, view results, manage thresholds, and retrain
- Seeds and training pipeline: reproducible synthetic/realistic data generators plus optional real images


Tech stack
----------
- Backend
  - Python 3.11, FastAPI, Uvicorn
  - NumPy, SciPy, scikit‑learn, joblib
  - Pillow (PIL), OpenCV
  - SQLModel/SQLite for config persistence
  - Logging via Python `logging`
- Frontend
  - Next.js 14, React 18
  - Axios for API calls, lucide‑react for icons
  - Custom CSS (no Tailwind in Docker mode)
- DevOps
  - Docker, docker‑compose (dev and prod variants)
  - Healthchecks for services, standalone builds


Architecture at a glance
------------------------
- `backend/app/pipeline/` implements preprocessing (`features.py`), model train/load/predict (`classifier.py`).
- `backend/app/routers/` exposes REST endpoints: `/scans`, `/admin/thresholds`, `/admin/train`, `/admin/metrics`, `/health`.
- Artifacts are persisted in `backend/app/pipeline/artifacts/` (model.joblib, scaler.joblib, metrics.json).
- Frontend calls the backend via `NEXT_PUBLIC_API_BASE` and renders results.


Quickstart (local dev, Windows PowerShell)
-----------------------------------------
Backend
```powershell
cd D:\meesho_dice2-kroo\catalogai\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DB_URL="sqlite:///app.db"
$env:THRESH_AUTH="0.15"
$env:THRESH_SYN="0.70"
$env:MAX_IMAGE_MB="8"
$env:LOG_LEVEL="INFO"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Frontend
```powershell
cd D:\meesho_dice2-kroo\catalogai\frontend
npm install
$env:NEXT_PUBLIC_API_BASE="http://localhost:8000"
npm run dev
```
Open `http://localhost:3000`.


Run with Docker (prod-like)
---------------------------
```powershell
cd D:\meesho_dice2-kroo\catalogai\ops
docker compose -f docker-compose.yml build --no-cache
docker compose -f docker-compose.yml up -d
```
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
Stop with:
```powershell
docker compose -f docker-compose.yml down
```


Run in Docker (dev mode with live reload)
----------------------------------------
```powershell
cd D:\meesho_dice2-kroo\catalogai\ops
docker compose -f docker-compose.dev.yml up --build
```


Using the app
-------------
1. Upload images on the Home page. The backend returns, per image:
   - synthetic probability, label (`authentic`, `suspicious`, `synthetic`), confidence bar, and reasons.
2. Scans page shows history (paginated) and per-image details.
3. Admin page lets you:
   - View/adjust thresholds (`Authentic`, `Synthetic` cutoffs)
   - Retrain the model (details below)
   - View current metrics


Training and retraining
-----------------------
The classifier is an SVM with probability calibration trained on engineered features (edges, color statistics, compression/texture/noise and FFT measures). Artifacts are stored in `backend/app/pipeline/artifacts/`.

Initial model
- On first backend startup, if artifacts are missing, the server trains an initial model from the seed generators under `catalogai/data/seeds`.

Retrain via Admin UI
1. Open Admin page.
2. Click “Retrain Model”.
3. After completion, new metrics are written to `metrics.json` and the app hot‑loads the updated model.

Retrain via API
```bash
curl -X POST http://localhost:8000/admin/train
```

Include your own real images (improves accuracy)
1. Place real images under the backend folder:
   ```
   catalogai/backend/data/real/
   ```
   (nested subfolders are fine; jpg/jpeg/png/bmp are read)
2. Retrain (UI or API). The pipeline will automatically mix in up to 2,000 real images from `data/real/` alongside synthetic/"realistic" seeds. Images are downscaled to a max edge of 768px for performance.
3. Check Admin → Metrics. You’ll see `disk_real_images_used` indicating how many files were ingested.

Fetching example “real” data from ABO (optional)
```bash
mkdir -p scratch data/real/abo data/real
aws s3 ls --no-sign-request s3://amazon-berkeley-objects/images/ --recursive | awk '{print $4}' > scratch/abo_all_keys.txt
shuf -n 1500 scratch/abo_all_keys.txt > scratch/abo_keys_1.5k.txt
while IFS= read -r key; do
  mkdir -p "data/real/abo/$(dirname "$key")"
  aws s3 cp --no-sign-request "s3://amazon-berkeley-objects/$key" "data/real/abo/$key" >/dev/null
done < scratch/abo_keys_1.5k.txt
find data/real/abo -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) -print0 | xargs -0 -I{} cp "{}" data/real/
```


Thresholds
----------
- `Authentic threshold` (default 0.15): below this synthetic probability → authentic.
- `Synthetic threshold` (default 0.70): above this → synthetic.
- Values in between are labeled `suspicious`.
You can tweak these on the Admin page. Updates persist in the DB and take immediate effect.


API reference (selected)
------------------------
- `GET /health/` – service health
- `POST /scans/` – multipart file upload, returns per‑image results
- `GET /admin/thresholds` / `PUT /admin/thresholds` – read/update thresholds
- `POST /admin/train` – retrain model
- `GET /admin/metrics` – current training metrics


Common problems
---------------
- “Training Error” in Admin: check backend logs. Ensure you have write access to `backend/app/pipeline/artifacts/` and that `catalogai/backend/data/real/` exists if you’re mixing real images.
- Frontend looks unstyled in Docker: rebuild without cache to avoid stale assets.
  ```powershell
  cd D:\meesho_dice2-kroo\catalogai\frontend
  .\run-dev.ps1
  ```


Project layout
--------------
```
catalogai/
  backend/
    app/
      routers/            # health, scans, admin
      pipeline/           # features, classifier, artifacts/
      models.py, schemas.py, db.py, main.py
    requirements.txt
  frontend/
    app/                  # Next.js app, components, pages
  data/
    seeds/                # seed generators used at train time
  ops/                    # docker compose files & helpers
```


