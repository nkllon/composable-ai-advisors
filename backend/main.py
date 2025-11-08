"""
Ontology Framework Backend API
FastAPI service for managing Plans of Day (PoD) and Spore registries
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import json
from pathlib import Path
import rdflib
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, XSD
import google.generativeai as genai

app = FastAPI(title="Ontology Framework API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Optionally enable MCP API
if os.getenv("ENABLE_MCP_API", "0").lower() in ("1", "true", "yes"):
	try:
		from backend.mcp.router import router as mcp_router
		app.include_router(mcp_router)
	except Exception:
		# MCP not yet available; ignore during early scaffolding
		pass

# Namespaces
PLAN = Namespace("https://ontology.beastmost.com/plan#")
SPORE = Namespace("https://ontology.beastmost.com/spore#")
PROV = Namespace("http://www.w3.org/ns/prov#")
TIME = Namespace("http://www.w3.org/2006/time#")

BASE_DIR = Path(__file__).parent.parent


class WorkflowPhase(BaseModel):
    phaseName: str
    description: str
    phaseOrder: int
    hasTime: Optional[str] = None


class Reference(BaseModel):
    referenceType: str
    referenceValue: str


class PlanOfDay(BaseModel):
    uri: str
    label: str
    date: str
    workflowPhases: List[WorkflowPhase]
    references: List[Reference]
    status: str
    generatedBy: Optional[str] = None
    generatedAt: Optional[str] = None


class Spore(BaseModel):
    uri: str
    label: str
    linksTo: Optional[str] = None
    derivedFrom: str
    createdAt: str
    status: str


def load_ontology_file(file_path: Path) -> Graph:
    """Load a Turtle file into an RDF graph"""
    g = Graph()
    if file_path.exists():
        g.parse(file_path, format="turtle")
    return g


def parse_pod(graph: Graph, pod_uri: URIRef) -> Optional[PlanOfDay]:
    """Parse a PlanOfDay from the RDF graph"""
    if not (pod_uri, RDF.type, PLAN.PlanOfDay) in graph:
        return None
    
    label = str(graph.value(pod_uri, RDFS.label) or "")
    date = str(graph.value(pod_uri, PLAN.date) or "")
    status = str(graph.value(pod_uri, PLAN.status) or "active")
    generated_by = str(graph.value(pod_uri, PROV.wasGeneratedBy) or "")
    generated_at = str(graph.value(pod_uri, PROV.generatedAtTime) or "")
    
    # Parse workflow phases
    phases = []
    for phase_node in graph.objects(pod_uri, PLAN.workflowPhase):
        if isinstance(phase_node, BNode):
            phase_name = str(graph.value(phase_node, PLAN.phaseName) or "")
            description = str(graph.value(phase_node, PLAN.description) or "")
            phase_order = int(graph.value(phase_node, PLAN.phaseOrder) or 0)
            has_time = str(graph.value(phase_node, TIME.hasTime) or "")
            phases.append(WorkflowPhase(
                phaseName=phase_name,
                description=description,
                phaseOrder=phase_order,
                hasTime=has_time if has_time else None
            ))
    
    phases.sort(key=lambda x: x.phaseOrder)
    
    # Parse references
    references = []
    for ref_node in graph.objects(pod_uri, PLAN.references):
        if isinstance(ref_node, BNode):
            ref_type = str(graph.value(ref_node, PLAN.referenceType) or "")
            ref_value = str(graph.value(ref_node, PLAN.referenceValue) or "")
            references.append(Reference(
                referenceType=ref_type,
                referenceValue=ref_value
            ))
    
    return PlanOfDay(
        uri=str(pod_uri),
        label=label,
        date=date,
        workflowPhases=phases,
        references=references,
        status=status,
        generatedBy=generated_by if generated_by else None,
        generatedAt=generated_at if generated_at else None
    )


def parse_spore(graph: Graph, spore_uri: URIRef) -> Optional[Spore]:
    """Parse a Spore from the RDF graph"""
    if not (spore_uri, RDF.type, SPORE.Spore) in graph:
        return None
    
    label = str(graph.value(spore_uri, RDFS.label) or "")
    links_to = str(graph.value(spore_uri, SPORE.linksTo) or "")
    derived_from = str(graph.value(spore_uri, SPORE.derivedFrom) or "")
    created_at = str(graph.value(spore_uri, SPORE.createdAt) or "")
    status = str(graph.value(spore_uri, SPORE.status) or "active")
    
    return Spore(
        uri=str(spore_uri),
        label=label,
        linksTo=links_to if links_to else None,
        derivedFrom=derived_from,
        createdAt=created_at,
        status=status
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ontology Framework API",
        "version": "1.0.0",
        "endpoints": {
            "pods": "/api/pods",
            "spores": "/api/spores",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/pods", response_model=List[PlanOfDay])
async def get_all_pods():
    """Get all Plans of Day from the guidance registry"""
    guidance_file = BASE_DIR / "guidance.ttl"
    graph = load_ontology_file(guidance_file)
    
    pods = []
    for pod_uri in graph.subjects(RDF.type, PLAN.PlanOfDay):
        file_path = str(graph.value(pod_uri, PLAN.filePath) or "")
        if file_path:
            pod_file = BASE_DIR / file_path
            pod_graph = load_ontology_file(pod_file)
            pod = parse_pod(pod_graph, pod_uri)
            if pod:
                pods.append(pod)
    
    return pods


@app.get("/api/pods/{pod_id}", response_model=PlanOfDay)
async def get_pod(pod_id: str):
    """Get a specific Plan of Day by ID"""
    guidance_file = BASE_DIR / "guidance.ttl"
    graph = load_ontology_file(guidance_file)
    
    pod_uri = URIRef(f"https://ontology.beastmost.com/pod/{pod_id}")
    file_path = str(graph.value(pod_uri, PLAN.filePath) or "")
    
    if not file_path:
        raise HTTPException(status_code=404, detail="PoD not found")
    
    pod_file = BASE_DIR / file_path
    pod_graph = load_ontology_file(pod_file)
    pod = parse_pod(pod_graph, pod_uri)
    
    if not pod:
        raise HTTPException(status_code=404, detail="PoD not found")
    
    return pod


@app.get("/api/spores", response_model=List[Spore])
async def get_all_spores():
    """Get all Spores from the spore registry"""
    spore_file = BASE_DIR / "spore_registry.ttl"
    graph = load_ontology_file(spore_file)
    
    spores = []
    for spore_uri in graph.subjects(RDF.type, SPORE.Spore):
        spore = parse_spore(graph, spore_uri)
        if spore:
            spores.append(spore)
    
    return spores


@app.post("/api/pods/generate")
async def generate_pod_with_ai(prompt: Dict[str, Any]):
    """Generate a new Plan of Day using Google Gemini AI"""
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key not configured"
        )
    
    user_prompt = prompt.get("prompt", "")
    if not user_prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        system_prompt = """You are an assistant that helps create Plans of Day (PoD) in a structured format.
A PoD follows the Plan-Do-Check-Act (PDCA) workflow cycle with 4 phases:
1. Plan - Review and plan activities
2. Do - Execute actions
3. Check - Validate and verify
4. Act - Feed changes back

Generate a PoD based on the user's input. Return a JSON object with:
{
    "label": "PoD YYYY-MM-DD: Brief description",
    "date": "YYYY-MM-DD",
    "phases": [
        {
            "phaseName": "Plan",
            "description": "...",
            "phaseOrder": 1
        },
        {
            "phaseName": "Do",
            "description": "...",
            "phaseOrder": 2
        },
        {
            "phaseName": "Check",
            "description": "...",
            "phaseOrder": 3,
            "hasTime": "YYYY-MM-DDTHH:MM:00" (optional)
        },
        {
            "phaseName": "Act",
            "description": "...",
            "phaseOrder": 4
        }
    ],
    "references": [
        {
            "referenceType": "...",
            "referenceValue": "..."
        }
    ]
}

Only return the JSON, no other text."""
        
        full_prompt = f"{system_prompt}\n\nUser request: {user_prompt}"
        response = model.generate_content(full_prompt)
        
        # Parse JSON from response
        response_text = response.text.strip()
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        response_text = response_text.strip()
        
        pod_data = json.loads(response_text)
        
        return {
            "success": True,
            "pod": pod_data,
            "message": "PoD generated successfully"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating PoD: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)





