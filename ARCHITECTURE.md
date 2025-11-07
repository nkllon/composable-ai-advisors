# Architecture Diagram

## System Architecture

```mermaid
graph TB
    subgraph "User Interface"
        UI[React Frontend<br/>Cloud Run Service]
    end
    
    subgraph "API Layer"
        API[FastAPI Backend<br/>Cloud Run Service]
    end
    
    subgraph "AI Services"
        GEMINI[Google Gemini AI<br/>Generative AI]
    end
    
    subgraph "Data Layer"
        GUIDANCE[guidance.ttl<br/>RDF/Turtle]
        SPORE[spore_registry.ttl<br/>RDF/Turtle]
        PODS[PoD Files<br/>RDF/Turtle]
    end
    
    subgraph "Google Cloud Platform"
        CR1[Cloud Run<br/>Frontend Service]
        CR2[Cloud Run<br/>Backend Service]
        GCR[Google Container Registry]
        SECRETS[Secret Manager<br/>Gemini API Key]
    end
    
    UI -->|HTTPS| CR1
    CR1 -->|API Calls| CR2
    CR2 -->|Read/Parse| GUIDANCE
    CR2 -->|Read/Parse| SPORE
    CR2 -->|Read/Parse| PODS
    CR2 -->|Generate PoD| GEMINI
    GEMINI -->|API Key| SECRETS
    CR1 -.->|Docker Image| GCR
    CR2 -.->|Docker Image| GCR
    
    style UI fill:#667eea,stroke:#333,stroke-width:2px,color:#fff
    style API fill:#764ba2,stroke:#333,stroke-width:2px,color:#fff
    style GEMINI fill:#4285f4,stroke:#333,stroke-width:2px,color:#fff
    style CR1 fill:#34a853,stroke:#333,stroke-width:2px,color:#fff
    style CR2 fill:#34a853,stroke:#333,stroke-width:2px,color:#fff
```

## Technology Stack

### Frontend
- **Framework**: React 18.2
- **HTTP Client**: Axios
- **Web Server**: Nginx (Alpine)
- **Container**: Docker
- **Deployment**: Google Cloud Run

### Backend
- **Framework**: FastAPI (Python 3.11)
- **RDF Processing**: RDFLib
- **AI Integration**: Google Generative AI (Gemini)
- **Container**: Docker
- **Deployment**: Google Cloud Run

### Data Storage
- **Format**: RDF/Turtle (.ttl files)
- **Ontology**: Custom ontology for Plans of Day and Spores
- **Storage**: File-based (included in container)

### Cloud Services
- **Compute**: Google Cloud Run (serverless containers)
- **Container Registry**: Google Container Registry
- **Secrets**: Google Secret Manager (for Gemini API key)
- **AI**: Google Gemini Pro (via Generative AI API)

## Request Flow

1. **User accesses frontend** → Cloud Run serves React app
2. **User views PoD/Spore data** → Frontend calls backend API
3. **Backend parses RDF files** → Returns structured JSON
4. **User generates new PoD** → Frontend sends prompt to backend
5. **Backend calls Gemini AI** → Generates structured PoD
6. **Response returned** → Frontend displays generated PoD

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Google Cloud Run                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  Frontend        │         │  Backend         │     │
│  │  Service         │────────▶│  Service         │     │
│  │  (Port 80)       │  HTTPS  │  (Port 8080)     │     │
│  │                  │         │                  │     │
│  │  - React App     │         │  - FastAPI       │     │
│  │  - Nginx         │         │  - RDFLib        │     │
│  │  - Static Files  │         │  - Gemini AI     │     │
│  └──────────────────┘         └──────────────────┘     │
│                                                          │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  Gemini AI API   │
                   │  (External)      │
                   └──────────────────┘
```

## Key Features

1. **Multi-Service Architecture**: Separate frontend and backend services on Cloud Run
2. **AI-Powered Generation**: Uses Google Gemini AI for intelligent PoD creation
3. **RDF-Based Ontology**: Leverages semantic web standards for structured data
4. **Serverless & Scalable**: Cloud Run automatically scales based on traffic
5. **Containerized**: Both services run in Docker containers





