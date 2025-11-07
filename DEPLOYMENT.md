# Deployment Guide

## Quick Start

### Prerequisites Setup

1. **Install Google Cloud SDK**
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Or download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate and Set Project**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable Required APIs**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   ```

4. **Get Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create an API key
   - Save it for later use

5. **Create Secret for Gemini API Key**
   ```bash
   echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
   
   # Grant access to Cloud Run service account
   PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")
   gcloud secrets add-iam-policy-binding gemini-api-key \
     --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

## Deployment Methods

### Method 1: Automated Script (Recommended)

```bash
chmod +x deploy.sh
./deploy.sh YOUR_PROJECT_ID
```

This script will:
1. Enable required APIs
2. Build and deploy backend
3. Get backend URL
4. Build and deploy frontend with backend URL
5. Display both URLs

### Method 2: Cloud Build (Manual)

#### Step 1: Deploy Backend

```bash
# From project root
gcloud builds submit --config=cloudbuild-backend.yaml .

# Get the backend URL
BACKEND_URL=$(gcloud run services describe ontology-backend \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)')

echo "Backend URL: $BACKEND_URL"
```

#### Step 2: Update Frontend Config

Edit `cloudbuild-frontend.yaml` and update the `_BACKEND_URL` substitution with your actual backend URL.

#### Step 3: Deploy Frontend

```bash
gcloud builds submit --config=cloudbuild-frontend.yaml \
  --substitutions=_BACKEND_URL=$BACKEND_URL .
```

### Method 3: Manual Docker Build

#### Backend

```bash
# Build from project root
docker build -t gcr.io/YOUR_PROJECT_ID/ontology-backend:latest -f backend/Dockerfile .

# Push to Container Registry
docker push gcr.io/YOUR_PROJECT_ID/ontology-backend:latest

# Deploy to Cloud Run
gcloud run deploy ontology-backend \
  --image gcr.io/YOUR_PROJECT_ID/ontology-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --set-secrets=GEMINI_API_KEY=gemini-api-key:latest
```

#### Frontend

```bash
# Build React app locally first
cd frontend
REACT_APP_API_URL=https://YOUR_BACKEND_URL npm run build
cd ..

# Build Docker image
docker build -t gcr.io/YOUR_PROJECT_ID/ontology-frontend:latest -f frontend/Dockerfile frontend

# Push to Container Registry
docker push gcr.io/YOUR_PROJECT_ID/ontology-frontend:latest

# Deploy to Cloud Run
gcloud run deploy ontology-frontend \
  --image gcr.io/YOUR_PROJECT_ID/ontology-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 80 \
  --memory 512Mi \
  --cpu 1
```

## Post-Deployment

### Get Service URLs

```bash
# Backend URL
gcloud run services describe ontology-backend \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'

# Frontend URL
gcloud run services describe ontology-frontend \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

### Test the Deployment

1. **Test Backend Health**
   ```bash
   curl https://YOUR_BACKEND_URL/health
   ```

2. **Test Backend API**
   ```bash
   curl https://YOUR_BACKEND_URL/api/pods
   ```

3. **Open Frontend**
   - Navigate to your frontend URL in a browser
   - Test viewing PoDs and Spores
   - Test AI PoD generation

### Update Frontend API URL (if needed)

If you need to update the frontend's API URL after deployment:

1. Rebuild the frontend with the correct API URL:
   ```bash
   cd frontend
   REACT_APP_API_URL=https://YOUR_BACKEND_URL npm run build
   ```

2. Rebuild and redeploy:
   ```bash
   docker build -t gcr.io/YOUR_PROJECT_ID/ontology-frontend:latest -f frontend/Dockerfile frontend
   docker push gcr.io/YOUR_PROJECT_ID/ontology-frontend:latest
   gcloud run deploy ontology-frontend \
     --image gcr.io/YOUR_PROJECT_ID/ontology-frontend:latest \
     --platform managed \
     --region us-central1
   ```

## Troubleshooting

### Backend Issues

**Issue: "Gemini API key not configured"**
- Solution: Ensure the secret is created and the service account has access
- Check: `gcloud secrets versions access latest --secret="gemini-api-key"`

**Issue: "Module not found" errors**
- Solution: Check that `requirements.txt` is properly copied in Dockerfile
- Verify: `docker run gcr.io/YOUR_PROJECT_ID/ontology-backend:latest pip list`

**Issue: "Cannot find ontology files"**
- Solution: Ensure ontology files are copied in Dockerfile
- Check: Files are in the correct location relative to Dockerfile context

### Frontend Issues

**Issue: "API calls failing"**
- Solution: Check CORS settings in backend
- Verify: Frontend API URL is correct in build-time environment variable
- Check: Backend URL is accessible from browser

**Issue: "404 errors"**
- Solution: Ensure nginx configuration is correct
- Check: React Router is configured for client-side routing

### Cloud Run Issues

**Issue: "Service not accessible"**
- Solution: Check `--allow-unauthenticated` flag is set
- Verify: Service is in the correct region
- Check: IAM permissions are correct

**Issue: "Cold start timeouts"**
- Solution: Increase memory allocation
- Consider: Setting `--min-instances 1` for production

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt
export GEMINI_API_KEY=your-key-here
export PORT=8080
python main.py
```

Backend will be available at `http://localhost:8080`

### Frontend

```bash
cd frontend
npm install
export REACT_APP_API_URL=http://localhost:8080
npm start
```

Frontend will be available at `http://localhost:3000`

## Environment Variables

### Backend
- `PORT`: Server port (default: 8080)
- `GEMINI_API_KEY`: Google Gemini API key (from Secret Manager in Cloud Run)

### Frontend
- `REACT_APP_API_URL`: Backend API URL (set at build time)

## Cost Considerations

- **Cloud Run**: Pay per request and compute time
- **Container Registry**: Storage costs for images
- **Gemini API**: Per API call (check current pricing)
- **Secret Manager**: Free tier available

To minimize costs:
- Use `--min-instances 0` (default) to scale to zero
- Set appropriate memory/CPU limits
- Monitor usage in Cloud Console





