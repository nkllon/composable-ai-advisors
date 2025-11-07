#!/bin/bash

# Cloud Run Deployment Script for Ontology Framework
# Usage: ./deploy.sh [PROJECT_ID]

set -e

PROJECT_ID=${1:-${GOOGLE_CLOUD_PROJECT}}
if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID must be provided"
    echo "Usage: ./deploy.sh PROJECT_ID"
    exit 1
fi

echo "Deploying to project: $PROJECT_ID"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and deploy backend
echo "Building backend..."
cd backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/ontology-backend --config=../cloudbuild-backend.yaml ..
cd ..
gcloud run deploy ontology-backend \
    --image gcr.io/$PROJECT_ID/ontology-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars PORT=8080 \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --min-instances 0

BACKEND_URL=$(gcloud run services describe ontology-backend --platform managed --region us-central1 --format 'value(status.url)')
echo "Backend deployed at: $BACKEND_URL"

# Build and deploy frontend
echo "Building frontend..."
cd frontend

# Update API URL in cloudbuild config
sed -i.bak "s|_BACKEND_URL:.*|_BACKEND_URL: '$BACKEND_URL'|" ../cloudbuild-frontend.yaml

# Build and deploy using Cloud Build
gcloud builds submit --config=../cloudbuild-frontend.yaml --substitutions=_BACKEND_URL=$BACKEND_URL ..
cd ..

FRONTEND_URL=$(gcloud run services describe ontology-frontend --platform managed --region us-central1 --format 'value(status.url)')
echo "Frontend deployed at: $FRONTEND_URL"

echo ""
echo "Deployment complete!"
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""
echo "To set the Gemini API key:"
echo "  gcloud secrets create gemini-api-key --data-file=- <<< 'YOUR_API_KEY'"
echo "  gcloud run services update ontology-backend --update-secrets=GEMINI_API_KEY=gemini-api-key:latest"

