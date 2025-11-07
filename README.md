# Ontology Framework - Cloud Run Hackathon Submission

## 🎯 Project Overview

The **Ontology Framework** is a full-stack application built on Google Cloud Run that manages Plans of Day (PoD) and Spore registries using RDF/Turtle ontologies. The system provides a modern web interface for visualizing structured workflow data and leverages Google Gemini AI to intelligently generate new Plans of Day based on natural language prompts.

## ✨ Features

### Core Functionality
- **Plans of Day (PoD) Management**: View and manage structured daily plans following the Plan-Do-Check-Act (PDCA) workflow
- **Spore Registry**: Track spore propagation and linking to milestones for multi-agent continuity
- **RDF/Turtle Ontology**: Uses semantic web standards for structured, machine-readable data
- **RESTful API**: FastAPI backend providing JSON endpoints for all operations

### AI-Powered Features
- **Gemini AI Integration**: Generate new Plans of Day using Google Gemini AI based on natural language descriptions
- **Intelligent Workflow Generation**: AI automatically structures prompts into proper PDCA workflow phases
- **Context-Aware Planning**: AI understands context and creates relevant references and timing

### User Interface
- **Modern React Frontend**: Beautiful, responsive web interface
- **Real-time Data Visualization**: View PoDs, Spores, and their relationships
- **Interactive AI Generation**: Simple prompt-based interface for generating new PoDs

## 🏗️ Architecture

The application consists of two Cloud Run services:

1. **Frontend Service** (React + Nginx)
   - Serves the React application
   - Handles routing and static assets
   - Communicates with backend API

2. **Backend Service** (FastAPI + Python)
   - RESTful API endpoints
   - RDF/Turtle file parsing using RDFLib
   - Google Gemini AI integration
   - Ontology data management

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture diagram and technology stack.

## 🚀 Technologies Used

### Backend
- **Python 3.11**: Core programming language
- **FastAPI**: Modern, fast web framework for building APIs
- **RDFLib**: RDF/Turtle parsing and processing
- **Google Generative AI**: Gemini Pro model for AI-powered PoD generation
- **Uvicorn**: ASGI server

### Frontend
- **React 18.2**: UI framework
- **Axios**: HTTP client for API calls
- **Nginx**: Web server for production
- **CSS3**: Modern styling with gradients and animations

### Cloud Services
- **Google Cloud Run**: Serverless container platform (both services)
- **Google Container Registry**: Docker image storage
- **Google Secret Manager**: Secure API key storage (Gemini)
- **Google Generative AI API**: Gemini AI service

### Data Format
- **RDF/Turtle**: Semantic web standard for ontology representation
- **JSON**: API response format

## 📦 Project Structure

```
ontology-framework/
├── backend/                 # FastAPI backend service
│   ├── main.py             # Main application file
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend container definition
│   └── service.yaml        # Cloud Run service config
├── frontend/               # React frontend service
│   ├── src/               # React source code
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Styling
│   │   └── index.js       # Entry point
│   ├── public/            # Static files
│   ├── package.json       # Node dependencies
│   ├── Dockerfile         # Frontend container definition
│   └── nginx.conf         # Nginx configuration
├── docs/                  # Documentation and PoD files
│   └── pod/              # Plan of Day examples
├── guidance.ttl          # Guidance registry (RDF)
├── spore_registry.ttl    # Spore registry (RDF)
├── deploy.sh             # Deployment script
├── cloudbuild-*.yaml     # Cloud Build configurations
├── ARCHITECTURE.md       # Architecture documentation
└── README.md             # This file
```

## 🚀 Getting Started

### Prerequisites

- Google Cloud Platform account with billing enabled
- `gcloud` CLI installed and configured
- Docker installed (for local development)
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Gemini API key (for AI features)

### Local Development

#### Backend

```bash
cd backend
pip install -r requirements.txt
export GEMINI_API_KEY=your-api-key-here
export PORT=8080
python main.py
```

The backend will be available at `http://localhost:8080`

#### Frontend

```bash
cd frontend
npm install
export REACT_APP_API_URL=http://localhost:8080
npm start
```

The frontend will be available at `http://localhost:3000`

### Deployment to Cloud Run

#### Option 1: Using the deployment script

```bash
chmod +x deploy.sh
./deploy.sh YOUR_PROJECT_ID
```

#### Option 2: Using Cloud Build

```bash
# Deploy backend
gcloud builds submit --config=cloudbuild-backend.yaml --project=YOUR_PROJECT_ID

# Deploy frontend (after backend is deployed)
# Update _BACKEND_URL in cloudbuild-frontend.yaml first
gcloud builds submit --config=cloudbuild-frontend.yaml --project=YOUR_PROJECT_ID
```

#### Option 3: Manual deployment

```bash
# Build and deploy backend
cd backend
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ontology-backend
gcloud run deploy ontology-backend \
    --image gcr.io/YOUR_PROJECT_ID/ontology-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-secrets=GEMINI_API_KEY=gemini-api-key:latest

# Build and deploy frontend
cd ../frontend
npm run build
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ontology-frontend
gcloud run deploy ontology-frontend \
    --image gcr.io/YOUR_PROJECT_ID/ontology-frontend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars=REACT_APP_API_URL=https://ontology-backend-XXXXX-uc.a.run.app
```

### Setting up Gemini API Key

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a secret in Secret Manager:

```bash
echo -n "YOUR_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
```

3. Grant Cloud Run service account access:

```bash
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## 📡 API Endpoints

### Backend API

- `GET /` - API information
- `GET /health` - Health check
- `GET /api/pods` - Get all Plans of Day
- `GET /api/pods/{pod_id}` - Get specific PoD
- `GET /api/spores` - Get all Spores
- `POST /api/pods/generate` - Generate new PoD using AI

### Example API Call

```bash
# Get all PoDs
curl https://ontology-backend-XXXXX-uc.a.run.app/api/pods

# Generate new PoD
curl -X POST https://ontology-backend-XXXXX-uc.a.run.app/api/pods/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "I need to work on Cloud Run deployment and test the API endpoints"}'
```

## 🎬 Demonstration Video

[Link to demonstration video will be added here]

The video demonstrates:
- Accessing the web interface
- Viewing existing Plans of Day and Spores
- Generating a new PoD using AI
- Understanding the PDCA workflow structure
- API functionality

## 📊 Data Sources

### Primary Data
- **guidance.ttl**: Registry of all registered Plans of Day
- **spore_registry.ttl**: Registry of all Spores and their relationships
- **docs/pod/2025/**: Individual PoD files in RDF/Turtle format

### External Services
- **Google Gemini AI**: For intelligent PoD generation

## 🎓 Learnings and Findings

### Technical Learnings

1. **RDF/Turtle Processing**: Successfully integrated RDFLib for parsing semantic web ontologies, enabling structured data representation while maintaining human readability.

2. **Cloud Run Multi-Service Architecture**: Implemented a microservices-style architecture with separate frontend and backend services, demonstrating Cloud Run's flexibility for containerized applications.

3. **AI Integration**: Integrated Google Gemini AI for natural language understanding and structured output generation, showcasing practical AI application in workflow management.

4. **Serverless Scaling**: Leveraged Cloud Run's automatic scaling capabilities, allowing the application to handle varying loads efficiently with zero configuration.

### Challenges Overcome

1. **RDF Parsing Complexity**: Implemented custom parsing logic to extract structured data from RDF/Turtle files while maintaining ontology relationships.

2. **CORS Configuration**: Configured proper CORS settings to allow frontend-backend communication across different Cloud Run services.

3. **Environment Variables**: Managed environment-specific configuration, particularly for API URLs and secrets in a serverless environment.

4. **Container Build Optimization**: Optimized Docker builds for both Python and Node.js applications, ensuring fast deployment times.

### Future Enhancements

- Persistent storage integration (Cloud Storage or Firestore)
- Real-time updates using WebSockets
- User authentication and multi-user support
- Advanced AI features for PoD optimization
- Export functionality (PDF, JSON, Turtle)
- Version control for PoD history

## 📝 Hackathon Submission Details

### Category
**General / Open Category**

### Project URL
[Add your Cloud Run frontend URL here after deployment]

### Code Repository
[Add your public GitHub repository URL here]

### Architecture Diagram
See [ARCHITECTURE.md](./ARCHITECTURE.md) for the complete architecture diagram with Mermaid visualization.

### Required Developer Tools
- ✅ Google Cloud Run (multiple services)
- ✅ Google AI (Gemini)

### Optional Contributions
- [ ] Blog post or article about the project
- [ ] Social media post with #CloudRunHackathon hashtag

## 🔗 Related Projects

### Graph RAG Chat Application
This project was inspired by and builds upon concepts from the [Graph RAG project](https://github.com/nkllon/graph_RAG), which demonstrates advanced RDF/SPARQL integration with knowledge graphs using GraphDB and Microsoft Agent Framework. While this project focuses on Cloud Run deployment with file-based RDF storage, the Graph RAG project showcases:

- **GraphDB Integration**: SPARQL query execution against RDF triple stores
- **LLM-driven Query Generation**: Natural language to SPARQL translation
- **Graph RAG Pattern**: Retrieval-Augmented Generation with knowledge graphs
- **Multi-Agent Frameworks**: Microsoft Agent Framework for agent orchestration

Both projects share a common interest in:
- **Semantic Web Standards**: RDF/Turtle ontology representation
- **Multi-Agent Continuity**: Managing context across agent sessions (Spores in this project)
- **AI-Powered Ontology Work**: Using LLMs to work with structured knowledge

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This project is created for the Google Cloud Run Hackathon 2024.

## 👤 Author

**Lou** - BeastMost Systems / nkllon observatory

---

**Built with ❤️ for the Cloud Run Hackathon**

