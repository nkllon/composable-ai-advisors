#!/bin/bash

# Cloud Run Deployment Script for Ontology Framework
# Usage: ./deploy.sh [PROJECT_ID]

set -e

# Resolve GEMINI_API_KEY without sourcing arbitrary shell files
# Priority: existing env -> 1Password (beast vault) -> ~/.env -> ./.env (python-dotenv style)
read_dotenv_key() {
  FILE_PATH="$1"
  DOTENV_KEY="$2"
  awk -v key="$DOTENV_KEY" '
    BEGIN { FS="=" }
    /^[[:space:]]*#/ { next }
    /^[[:space:]]*$/ { next }
    {
      line=$0
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", line)
      sub(/^export[[:space:]]+/, "", line)
      split(line, arr, "=")
      k=arr[1]
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", k)
      if (k == key) {
        v=substr(line, index(line, "=")+1)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", v)
        if ((v ~ /^\".*\"$/) || (v ~ /^\\047.*\\047$/)) {
          v=substr(v,2,length(v)-2)
        }
        print v
        exit
      }
    }
  ' "$FILE_PATH"
}

resolve_gemini_key() {
  if [ -n "${GEMINI_API_KEY:-}" ]; then
    return 0
  fi
  if command -v op >/dev/null 2>&1; then
    set +e
    OP_VAL="$(op item get \"Composable AI Advisors: GEMINI_API_KEY\" --vault \"beast\" --fields password 2>/dev/null)"
    if [ -n "$OP_VAL" ]; then
      export GEMINI_API_KEY="$OP_VAL"
      set -e
      return 0
    fi
    set -e
  fi
  if [ -f "$HOME/.env" ]; then
    VAL="$(read_dotenv_key "$HOME/.env" "GEMINI_API_KEY")"
    if [ -n "$VAL" ]; then
      export GEMINI_API_KEY="$VAL"
      return 0
    fi
  fi
  if [ -f ".env" ]; then
    VAL="$(read_dotenv_key ".env" "GEMINI_API_KEY")"
    if [ -n "$VAL" ]; then
      export GEMINI_API_KEY="$VAL"
      return 0
    fi
  fi
  return 1
}

resolve_project_id() {
  # Priority: arg -> GOOGLE_CLOUD_PROJECT env -> gcloud config -> ~/.env -> ./.env
  if [ -n "${1:-}" ]; then
    echo "$1"
    return 0
  fi
  if [ -n "${GOOGLE_CLOUD_PROJECT:-}" ]; then
    echo "$GOOGLE_CLOUD_PROJECT"
    return 0
  fi
  GCLOUD_PROJ="$(gcloud config get-value project 2>/dev/null || true)"
  if [ -n "$GCLOUD_PROJ" ]; then
    echo "$GCLOUD_PROJ"
    return 0
  fi
  if [ -f "$HOME/.env" ]; then
    for key in PROJECT_ID GOOGLE_CLOUD_PROJECT GCP_PROJECT; do
      val="$(read_dotenv_key "$HOME/.env" "$key")"
      if [ -n "$val" ]; then
        echo "$val"
        return 0
      fi
    done
  fi
  if [ -f ".env" ]; then
    for key in PROJECT_ID GOOGLE_CLOUD_PROJECT GCP_PROJECT; do
      val="$(read_dotenv_key ".env" "$key")"
      if [ -n "$val" ]; then
        echo "$val"
        return 0
      fi
    done
  fi
  return 1
}

PROJECT_ID="$(resolve_project_id "${1:-}")" || {
  echo "Error: PROJECT_ID not provided and could not be resolved from env, gcloud, or dotenv files."
  echo "Usage: ./scripts/deploy.sh PROJECT_ID"
  exit 1
}

echo "Deploying to project: $PROJECT_ID"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Build and deploy backend
echo "Building backend..."
gcloud builds submit --config=scripts/cloudbuild-backend.yaml .

# Configure Secret Manager for GEMINI_API_KEY if available
SECRET_FLAGS=""
if resolve_gemini_key; then
    echo "Configuring Secret Manager for GEMINI_API_KEY..."
    echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=- --project "$PROJECT_ID" || \
    echo -n "$GEMINI_API_KEY" | gcloud secrets versions add gemini-api-key --data-file=- --project "$PROJECT_ID"

    PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
    SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
    gcloud secrets add-iam-policy-binding gemini-api-key \
      --member="serviceAccount:${SERVICE_ACCOUNT}" \
      --role="roles/secretmanager.secretAccessor" \
      --project "$PROJECT_ID"

    SECRET_FLAGS="--set-secrets=GEMINI_API_KEY=gemini-api-key:latest"
else
    echo "Warning: GEMINI_API_KEY not set. AI generation endpoint will be disabled."
    # Do not remove existing secret mapping; leave service as-is.
fi
gcloud run deploy ontology-backend \
    --image gcr.io/$PROJECT_ID/ontology-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --min-instances 0 \
    $SECRET_FLAGS

BACKEND_URL=$(gcloud run services describe ontology-backend --platform managed --region us-central1 --format 'value(status.url)')
echo "Backend deployed at: $BACKEND_URL"

# Build and deploy frontend
echo "Building frontend..."
# Build and deploy using Cloud Build with substitution
gcloud builds submit --config=scripts/cloudbuild-frontend.yaml --substitutions=_BACKEND_URL=$BACKEND_URL .

FRONTEND_URL=$(gcloud run services describe ontology-frontend --platform managed --region us-central1 --format 'value(status.url)')
echo "Frontend deployed at: $FRONTEND_URL"

# Update backend CORS to strict origin if available
if [ -n "$FRONTEND_URL" ]; then
  gcloud run services update ontology-backend \
    --platform managed \
    --region us-central1 \
    --set-env-vars FRONTEND_ORIGIN=$FRONTEND_URL
fi

echo ""
echo "Deployment complete!"
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""
echo "To set the Gemini API key:"
echo "  echo -n 'YOUR_API_KEY' | gcloud secrets create gemini-api-key --data-file=-"
echo "  gcloud run services update ontology-backend --update-secrets=GEMINI_API_KEY=gemini-api-key:latest"

