"""
Ontology Framework Backend API
FastAPI service for managing Plans of Day (PoD) and Spore registries
"""
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import os
import json
import re
from pathlib import Path
import threading
from rdflib import Graph, URIRef, BNode, Namespace
from rdflib.namespace import RDF, RDFS
import google.generativeai as genai

ENABLE_MCP = os.getenv("ENABLE_MCP_API", "0").lower() in ("1", "true", "yes")

@asynccontextmanager
async def lifespan(app: FastAPI):
	# Initialize MCP if enabled
	if ENABLE_MCP:
		try:
			# Import the shared manager from the router and ensure initial load
			from backend.mcp.router import _ensure_loaded  # type: ignore
			await _ensure_loaded()
		except Exception:
			# Non-fatal during startup; endpoints also ensure lazy load
			pass
	yield

app = FastAPI(title="Ontology Framework API", version="1.0.0", lifespan=lifespan)

# CORS middleware for frontend
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")
ALLOWED_ORIGINS = [o.strip() for o in FRONTEND_ORIGIN.split(",")] if FRONTEND_ORIGIN else ["*"]
app.add_middleware(
	CORSMiddleware,
	allow_origins=ALLOWED_ORIGINS,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Initialize Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-001")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Optionally enable MCP API
if ENABLE_MCP:
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
ALLOWED_POD_ROOT = (BASE_DIR / "docs" / "pod").resolve()

_ONTOLOGY_CACHE: Dict[Path, Tuple[float, Graph]] = {}
_CACHE_LOCK = threading.Lock()


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
    """Load a Turtle file into an RDF graph with basic caching"""
    if not file_path.exists():
        return Graph()

    try:
        mtime = file_path.stat().st_mtime
    except OSError:
        return Graph()

    with _CACHE_LOCK:
        cached_entry = _ONTOLOGY_CACHE.get(file_path)
        if cached_entry and cached_entry[0] >= mtime:
            return cached_entry[1]

    graph = Graph()
    graph.parse(file_path, format="turtle")

    with _CACHE_LOCK:
        _ONTOLOGY_CACHE[file_path] = (mtime, graph)

    return graph


def resolve_pod_file_path(file_path: str) -> Optional[Path]:
    """Resolve and validate PoD file paths against the allowed directory"""
    if not file_path:
        return None

    candidate = (BASE_DIR / file_path).resolve()

    try:
        candidate.relative_to(ALLOWED_POD_ROOT)
    except ValueError:
        return None

    if not candidate.is_file():
        return None

    return candidate


def extract_json_object(text: str) -> Dict[str, Any]:
    """Extract the first JSON object from model output"""
    if not text:
        raise ValueError("Empty response from model")

    cleaned = text.strip()

    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned, re.IGNORECASE)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    decoder = json.JSONDecoder()
    idx = 0
    while idx < len(cleaned):
        try:
            obj, _ = decoder.raw_decode(cleaned, idx)
            return obj
        except json.JSONDecodeError:
            next_start = cleaned.find("{", idx + 1)
            if next_start == -1:
                break
            idx = next_start

    raise ValueError("No valid JSON object found in model response")


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

@app.get("/health/ai")
async def health_ai():
	"""AI readiness check: key presence and model availability"""
	configured = bool(GEMINI_API_KEY)
	result: Dict[str, Any] = {
		"configured": configured,
		"model": GEMINI_MODEL,
		"ok": False,
	}
	if not configured:
		return result
	try:
		model = genai.GenerativeModel(GEMINI_MODEL)
		resp = model.generate_content("ping")
		text = getattr(resp, "text", "")
		result["ok"] = bool(text is not None)
		return result
	except Exception as e:
		result["error"] = str(e)
		return result


@app.get("/api/pods", response_model=List[PlanOfDay])
async def get_all_pods():
    """Get all Plans of Day from the guidance registry"""
    guidance_file = BASE_DIR / "guidance.ttl"
    graph = load_ontology_file(guidance_file)
    
    pods = []
    for pod_uri in graph.subjects(RDF.type, PLAN.PlanOfDay):
        file_path = str(graph.value(pod_uri, PLAN.filePath) or "")
        pod_file = resolve_pod_file_path(file_path)
        if pod_file is None:
            continue

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

    pod_file = resolve_pod_file_path(file_path)
    if pod_file is None:
        raise HTTPException(status_code=404, detail="PoD not found")

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
        # Use model from env (default to a supported AI Studio model)
        model = genai.GenerativeModel(GEMINI_MODEL)
        
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

        response_text = getattr(response, "text", "")
        pod_data = extract_json_object(response_text)
        if not isinstance(pod_data, dict):
            raise ValueError("Model response did not contain a JSON object")

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





