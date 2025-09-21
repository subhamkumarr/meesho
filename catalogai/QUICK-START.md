# 🚀 CatalogAI Quick Start

Get CatalogAI running on your new laptop in 5 minutes!

## Option 1: Docker (Easiest)

### Step 1: Install Docker Desktop
- Download: https://www.docker.com/products/docker-desktop/
- Install and start Docker Desktop
- Wait for it to fully load (green icon in system tray)

### Step 2: Get the Code
```bash
git clone <your-repo-url>
cd catalogai
```

### Step 3: Run Everything
```bash
cd ops
docker-compose up --build -d
```

### Step 4: Open App
- Go to: http://localhost:3000
- Done! 🎉

---

## Option 2: Local Development

### Prerequisites
```bash
# Install Node.js (v18+)
# Install Python (3.11+)
# Install Git
```

### Backend
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux  
source venv/bin/activate

pip install -r requirements.txt
cd ../data/seeds && python seed_run.py && cd ../../backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

### Access
- App: http://localhost:3000
- API: http://localhost:8000

---

## Troubleshooting

### Docker Issues
```bash
# If Docker fails to start
# Windows: Run as Administrator
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# If ports are busy
docker-compose down
netstat -ano | findstr :3000
# Kill the process using the port

# Clean restart
docker system prune -a
docker-compose up --build --force-recreate
```

### Local Issues
```bash
# Python issues
pip install --upgrade pip
pip install -r requirements.txt

# Node issues
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

---

## What You Get

✅ **Image Upload**: Drag & drop images for authenticity analysis  
✅ **Real-time Results**: Get instant AI-powered authenticity scores  
✅ **Admin Panel**: Adjust detection thresholds  
✅ **Scan History**: View all previous analyses  
✅ **API Access**: Full REST API at `/docs`  

---

## Test It Works

1. Go to http://localhost:3000
2. Upload any image
3. See authenticity results
4. Check admin panel at `/admin`
5. View history at `/scans`

**That's it!** You're ready to detect AI-generated images! 🔍