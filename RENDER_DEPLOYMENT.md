# SafeLand - Render Deployment Guide

## Pre-Deployment Checklist ✅

### 1. **Frontend Build Setup**
- [x] Frontend build script configured in `app/package.json`
- [x] Frontend static files will be served by backend
- [x] Build command: `npm run build` creates `dist/` folder

### 2. **Backend Configuration**
- [x] Flask app updated to serve frontend static files
- [x] Port configuration uses environment variable `$PORT`
- [x] Debug mode disabled in production (controlled by `FLASK_DEBUG` env var)
- [x] CORS enabled for API requests
- [x] `Procfile` configured for Render with `gunicorn`

### 3. **Dependencies**
- [x] `requirements.txt` includes all backend dependencies
- [x] Frontend dependencies in `app/package.json`
- [x] `gunicorn` included in Python requirements

### 4. **Environment Variables to Set in Render**
You need to configure these in the Render dashboard:

```
BHUVAN_API_KEY=<your_bhuvan_api_key>
IMD_API_KEY=<your_imd_api_key>
FLASK_DEBUG=False
```

These correspond to the `.env.example` file in the project.

---

## Deployment Steps

### Step 1: Prepare Repository
```bash
# Commit deployment files
git add Procfile .render.yaml backend/app.py
git commit -m "Add Render deployment configuration"
git push
```

### Step 2: Create Render Service
1. Go to [render.com](https://render.com) and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `safeland`
   - **Runtime**: `Python`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT backend.app:app`
   - **Build Command**: Leave default or use: 
     ```bash
     cd app && npm install && npm run build && cd ..
     pip install -r backend/requirements.txt
     ```

### Step 3: Set Environment Variables
In the Render dashboard, go to **Environment** and add:
- `BHUVAN_API_KEY` = your_key
- `IMD_API_KEY` = your_key  
- `FLASK_DEBUG` = `False`

### Step 4: Deploy
1. Click **"Deploy"**
2. Monitor the build in the Render dashboard
3. Once deployed, your app will be available at: `https://safeland.onrender.com`

---

## Project Structure for Deployment

```
.
├── Procfile                    # ← Added for Render
├── .render.yaml               # ← Added for Render (optional)
├── backend/
│   ├── app.py                 # ← Updated for production
│   ├── config.py
│   ├── requirements.txt
│   └── data_sources/
├── app/                        # Frontend (React)
│   ├── package.json
│   ├── dist/                   # Generated after npm build
│   └── src/
├── ml/                         # ML models
│   ├── flood_risk_model.pkl
│   └── label_encoder.pkl
└── data/                       # Data files
```

---

## Important Notes

### Model Files
The ML model files (`flood_risk_model.pkl` and `label_encoder.pkl`) must be:
1. **Committed to Git** (currently in `.gitignore`?) or
2. **Downloaded during build** or
3. **Pre-uploaded to Render** via storage

**Recommendation**: If files are large, configure Render Disk or download them in a build script.

### API Keys
- `BHUVAN_API_KEY` - Required for elevation and location data
- `IMD_API_KEY` - Required for rainfall data

Without these, the `/predict` endpoint will fail.

### Build Time
The build may take 10-15 minutes due to:
- npm dependency installation
- Frontend TypeScript compilation
- Python package installation

---

## Testing After Deployment

Once deployed, test these endpoints:

```bash
# Health check
curl https://yourdomain.onrender.com/health

# Predict flood risk (example)
curl -X POST https://yourdomain.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"latitude": 10.85, "longitude": 76.27}'
```

---

## Troubleshooting

### Build Fails
- Check Node.js version compatibility in `app/package.json`
- Ensure all Python dependencies are listed in `requirements.txt`
- Check logs in Render dashboard

### App Crashes on Startup
- Check environment variables are set correctly
- Verify ML model files exist
- Check logs for API key issues

### 502 Bad Gateway
- Usually means the app crashed
- Check Render logs for errors
- Verify port binding is working (uses `$PORT`)

### Frontend Not Loading
- Ensure `npm run build` completes successfully
- Check if `app/dist/index.html` exists
- Verify `static_folder` path in Flask app

---

## Production Checklist

- [ ] All environment variables set in Render
- [ ] ML model files available (in repo or downloadable)
- [ ] API keys configured
- [ ] Frontend builds successfully locally (`npm run build`)
- [ ] Backend runs successfully locally (`python backend/app.py`)
- [ ] CORS is configured correctly
- [ ] No `debug=True` left in production code
- [ ] Tested `/health` endpoint after deployment
- [ ] Performance tested with sample requests

---

**Ready to deploy! 🚀**
