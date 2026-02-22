# app/main.py
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Body, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
import json

# PaperClip imports
from app.core import settings, setup_logging, validate_settings, get_logger
from app.core.exceptions import PaperClipException, ValidationError
from app.core.validators import QueryValidator, UserIdValidator
from app.tools import all_tools
from app.research_suite import (
    generate_research_bundle,
    _search_arxiv,
    _summarize_papers,
    _generate_ideation,
    _generate_experiment_design,
)
from app.auth import router as auth_router, get_current_user, get_optional_user
from app.db import (
    init_db,
    create_workspace,
    list_workspaces,
    get_workspace,
    delete_workspace,
    add_message,
    list_messages,
    add_memory_item,
    list_memory_items,
    delete_memory_item,
    create_ideation_item,
    list_ideation_items,
    delete_ideation_item,
    create_experiment_plan,
    list_experiment_plans,
    delete_experiment_plan,
    create_resource,
    get_resources,
)

# Lightweight keyword detection for auto tool routing
TOOL_KEYWORDS = {
    "domain_discovery": ["domain", "field", "area", "topic", "subfield"],
    "paper_summarizer": ["paper", "arxiv", "summary", "summarize", "literature"],
    "professor_finder": ["professor", "faculty", "advisor", "supervisor", "lecturer"],
    "dataset_hub": ["dataset", "data set", "huggingface", "hf dataset"],
    "pretrained_models": ["model", "pretrained", "checkpoint", "weights"],
    "generate_code": ["code", "snippet", "boilerplate", "implementation", "starter"]
}

TOOL_SYSTEM_PROMPTS = {
    "domain_discovery": (
        "You are the Domain Discovery Expert. Your goal is to help researchers find their niche. "
        "Analyze the provided field and suggest emerging subfields, current trends, and 'white spaces' "
        "where research is lacking. Provide your analysis in a structured format with clear headings."
    ),
    "paper_summarizer": (
        "You are the Paper Summarizer AI. You provide concise, accurate, and insightful summaries of "
        "research papers. Focus on: What problem are they solving? What is the main contribution? "
        "What are the limitations? Provide a structured summary with a TL;DR section."
    ),
    "professor_finder": (
        "You are the Faculty Search Assistant. Help users find top researchers, professors, and labs. "
        "Suggest institutions known for specific research strengths and provide names of prominent "
        "researchers in those areas. Note: Use your internal knowledge of academic rankings and history."
    ),
    "dataset_hub": (
        "You are the Dataset Librarian. Help users find datasets suitable for their research goals. "
        "Suggest datasets from HuggingFace, Kaggle, or academic repositories. Explain the size, "
        "license type, and common use cases for each suggested dataset."
    ),
    "pretrained_models": (
        "You are the Model Architect. Assist in finding and comparing state-of-the-art pretrained models. "
        "Discuss model architecture, parameter count, specialized training objectives, and 'which model "
        "to use when' scenarios."
    ),
    "generate_code": (
        "You are the Research Engineer. Generate high-quality code snippets for research. "
        "This includes data preprocessing, training loops (PyTorch/TensorFlow), evaluation scripts, "
        "and visualization code. Ensure code is commented, efficient, and reproducible."
    )
}


def detect_tool_from_query(query: str) -> Optional[str]:
    """Return a tool name if the query hints at one of the known tools."""
    q_lower = query.lower()
    for tool_name, keywords in TOOL_KEYWORDS.items():
        if any(keyword in q_lower for keyword in keywords):
            return tool_name
    return None


def _format_history(messages: List[Dict[str, Any]], limit: int = 10) -> str:
    if not messages:
        return ""
    recent = messages[-limit:]
    lines = []
    for msg in recent:
        role = str(msg.get("role", "")).strip().lower()
        content = str(msg.get("content", "")).strip()
        if not content:
            continue
        label = "User" if role == "user" else "Assistant" if role == "assistant" else "System"
        lines.append(f"{label}: {content}")
    return "\n".join(lines)


def _build_context(request: "QueryRequest") -> str:
    context_parts = []

    if request.workspace_id is not None:
        # 1. Fetch memory items (facts/user-defined info)
        memory_items = list_memory_items(request.workspace_id)
        if memory_items:
            memory_lines = [f"- {item.get('key')}: {item.get('value')}" for item in memory_items]
            context_parts.append("Workspace memory (key facts):\n" + "\n".join(memory_lines))

        # 2. Fetch workspace resources (papers, snippets, links)
        resources = get_resources(request.workspace_id)
        if resources:
            resource_lines = [f"[{r.get('title', 'Untitled')}]: {r.get('content', '')}" for r in resources]
            context_parts.append("The following resources are available in the current workspace:\n" + "\n".join(resource_lines))

        # 3. Recent chat history
        messages = list_messages(request.workspace_id, limit=50, offset=0)
        history = _format_history(messages, limit=12)
        if history:
            context_parts.append("Recent chat history:\n" + history)

    elif request.conversation_history:
        history = _format_history(request.conversation_history, limit=12)
        if history:
            context_parts.append("Recent chat history:\n" + history)

    return "\n\n".join(context_parts)

load_dotenv()

# Setup logging
setup_logging(settings.log_level)
logger = get_logger(__name__)

# Validate configuration at startup
try:
    validate_settings()
    logger.info(f"✅ Configuration validated - Running {settings.app_name}")
except Exception as e:
    logger.error(f"Configuration error: {e}")
    raise

# --- INITIALIZATION ---
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    servers=[{"url": f"http://{settings.host}:{settings.port}", "description": "Local Development Server"}]
)
app.add_middleware(CORSMiddleware, 
                  allow_origins=settings.cors_origins, 
                  allow_credentials=settings.cors_allow_credentials, 
                  allow_methods=settings.cors_allow_methods, 
                  allow_headers=settings.cors_allow_headers)

app.include_router(auth_router)

@app.on_event("startup")
def on_startup() -> None:
    """Initialize SQLite database for workspaces and memory."""
    init_db()

# Exception handlers
@app.exception_handler(PaperClipException)
async def paperclip_exception_handler(request, exc: PaperClipException):
    logger.error(f"{exc.error_code}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc: ValidationError):
    logger.warning(f"Validation error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

# --- Pydantic Models ---
class QueryRequest(BaseModel):
    user_id: str = "guest"
    query: str
    command: Optional[str] = None
    university: Optional[str] = None
    model_name: Optional[str] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None
    workspace_id: Optional[int] = None
    tool_type: Optional[str] = None
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v: Optional[str]) -> str:
        user_id = v or "guest"
        try:
            UserIdValidator(user_id=user_id)
        except ValueError as e:
            raise ValueError(str(e))
        return user_id
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        try:
            QueryValidator(query=v)
        except ValueError as e:
            raise ValueError(str(e))
        return v


class WorkspaceCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class MessageCreateRequest(BaseModel):
    role: str
    content: str


class MemoryItemRequest(BaseModel):
    key: str
    value: str


class IdeationRequest(BaseModel):
    topic: str
    goal: Optional[str] = None
    constraints: Optional[str] = None
    workspace_id: Optional[int] = None


class ExperimentDesignRequest(BaseModel):
    topic: str
    idea: Optional[str] = None
    constraints: Optional[str] = None
    workspace_id: Optional[int] = None


class ResourceCreateRequest(BaseModel):
    type: str # file/snippet/paper
    title: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

# --- API ENDPOINTS ---
@app.options("/query")
async def options_query():
    """Handle CORS preflight for /query endpoint"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/query")
def handle_query(request: QueryRequest, user: Optional[Dict[str, Any]] = Depends(get_optional_user)):
    """Handles all user queries - calls appropriate research tools."""
    logger.info(f"Query from {request.user_id}: {request.query[:50]}...")
    workspace_id = request.workspace_id

    if workspace_id is not None:
        if not user:
            raise HTTPException(status_code=401, detail="Authorization required for workspaces")
        if not get_workspace(workspace_id, user["id"]):
            raise HTTPException(status_code=404, detail="Workspace not found")

    # If explicit command provided, trust it; otherwise try to detect from query text
    command = request.command if (request.command and request.command in all_tools) else detect_tool_from_query(request.query)

    if command and command in all_tools:
        tool_to_run = all_tools[command]
        tool_args = {}

        if command in ["domain_discovery", "paper_summarizer", "dataset_hub", "pretrained_models"]:
            tool_args['topic'] = request.query
        elif command == "professor_finder":
            tool_args['topic'] = request.query
            tool_args['university'] = request.university
        elif command == "generate_code":
            tool_args['topic'] = request.query
            tool_args['model_name'] = request.model_name

        # Required arguments missing: ask user for specifics instead of failing silently
        if any(v is None for v in tool_args.values()):
            missing = [k for k, v in tool_args.items() if v is None]
            return {"response": f"I can run the {command.replace('_', ' ')} tool, but I still need: {', '.join(missing)}."}

        try:
            response_text = tool_to_run.invoke(tool_args)
            logger.info(f"Tool {command} completed successfully")
            if workspace_id is not None:
                add_message(workspace_id, "user", request.query, tool_type=command)
                add_message(workspace_id, "assistant", response_text, tool_type=command)
            return {"response": response_text}
        except Exception as e:
            logger.error(f"Tool {command} failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # No tool triggered: use research-oriented conversational AI
    try:
        from app.tools import safe_invoke
        context_block = _build_context(request)
        
        # Determine the base system prompt
        if request.tool_type and request.tool_type in TOOL_SYSTEM_PROMPTS:
            base_prompt = TOOL_SYSTEM_PROMPTS[request.tool_type]
            # Extra context-aware instructions for dynamic tools
            system_prompt = (
                f"{base_prompt}\n\n"
                "Constraints:\n"
                "- Focus EXCLUSIVELY on this specialized tool identity.\n"
                "- Use the provided workspace context (memory, resources, and history) to inform your specialized response.\n"
                "- Keep responses high-quality, research-oriented, and concise."
            )
        else:
            system_prompt = (
                "You are PaperClip, an AI research assistant. Provide research-focused responses with:\n"
                "- Clear explanations of concepts, methods, and techniques\n"
                "- References to key papers or researchers when relevant\n"
                "- Suggestions for further reading or exploration\n"
                "- Practical advice for research workflows\n\n"
                "Use the provided workspace context (memory, resources, and history) only if it is relevant to the user's query. "
                "Do not mention the context explicitly. Keep responses concise (2-4 paragraphs) and actionable."
            )

        if context_block:
            full_prompt = (
                f"{system_prompt}\n\n{context_block}\n\n"
                f"User Query: {request.query}\n\nResponse:"
            )
        else:
            full_prompt = f"{system_prompt}\n\nUser Query: {request.query}\n\nResponse:"
        
        llm_response = safe_invoke(full_prompt)
        if workspace_id is not None:
            add_message(workspace_id, "user", request.query, tool_type=request.tool_type)
            add_message(workspace_id, "assistant", llm_response.content, tool_type=request.tool_type)
        return {"response": llm_response.content}
    except Exception as e:
        logger.error(f"LLM chat fallback failed: {e}", exc_info=True)
        return {"response": f"I encountered an error processing your request. Please ensure the LLM provider is configured. Error: {str(e)}"}

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }

@app.get("/health")
def health_check():
    """Enhanced health check with system info"""
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "tools_available": len(all_tools)
    }

@app.get("/tools")
def list_tools():
    """List all available research tools"""
    tools_info = []
    for tool_name, tool_obj in all_tools.items():
        tools_info.append({
            "name": tool_name,
            "description": getattr(tool_obj, 'description', "Research tool"),
            "capabilities": getattr(tool_obj, 'capabilities', [])
        })
    return {"tools": tools_info, "total_count": len(tools_info)}

@app.get("/stats")
def get_stats():
    """Get platform statistics"""
    return {
        "total_queries": 0,
        "papers_found": 0,
        "code_snippets": 0,
        "avg_response_time": 0.0,
        # Additional context if needed by other clients
        "research_papers": "1M+",
        "datasets": "50K+",
        "models": "10K+",
        "universities": "500+",
        "active_researchers": "5K+"
    }

# --- Phase 3: Workspaces & Memory ---
@app.get("/workspaces")
def list_workspaces_endpoint(user: Dict[str, Any] = Depends(get_current_user)):
    workspaces = list_workspaces(user["id"])
    return {"workspaces": workspaces, "total_count": len(workspaces)}


@app.post("/workspaces")
def create_workspace_endpoint(request: WorkspaceCreateRequest, user: Dict[str, Any] = Depends(get_current_user)):
    name = request.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Workspace name is required")
    return create_workspace(user["id"], name, request.description)


@app.get("/workspaces/{workspace_id}")
def get_workspace_endpoint(workspace_id: int, user: Dict[str, Any] = Depends(get_current_user)):
    workspace = get_workspace(workspace_id, user["id"])
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@app.delete("/workspaces/{workspace_id}")
def delete_workspace_endpoint(workspace_id: int, user: Dict[str, Any] = Depends(get_current_user)):
    deleted = delete_workspace(workspace_id, user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"deleted": True}


@app.get("/workspaces/{workspace_id}/messages")
def list_workspace_messages(workspace_id: int, limit: int = 200, offset: int = 0, user: Dict[str, Any] = Depends(get_current_user)):
    if not get_workspace(workspace_id, user["id"]):
        raise HTTPException(status_code=404, detail="Workspace not found")
    messages = list_messages(workspace_id, limit=limit, offset=offset)
    return {"messages": messages, "count": len(messages)}


@app.post("/workspaces/{workspace_id}/messages")
def add_workspace_message(workspace_id: int, request: MessageCreateRequest, user: Dict[str, Any] = Depends(get_current_user)):
    if not get_workspace(workspace_id, user["id"]):
        raise HTTPException(status_code=404, detail="Workspace not found")
    role = request.role.strip().lower()
    if role not in {"user", "assistant", "system"}:
        raise HTTPException(status_code=400, detail="Invalid role")
    content = request.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Content is required")
    return add_message(workspace_id, role, content)


@app.get("/workspaces/{workspace_id}/memory")
def list_workspace_memory(workspace_id: int, user: Dict[str, Any] = Depends(get_current_user)):
    if not get_workspace(workspace_id, user["id"]):
        raise HTTPException(status_code=404, detail="Workspace not found")
    items = list_memory_items(workspace_id)
    return {"memory": items, "count": len(items)}


@app.post("/workspaces/{workspace_id}/memory")
def add_workspace_memory(workspace_id: int, request: MemoryItemRequest, user: Dict[str, Any] = Depends(get_current_user)):
    if not get_workspace(workspace_id, user["id"]):
        raise HTTPException(status_code=404, detail="Workspace not found")
    key = request.key.strip()
    value = request.value.strip()
    if not key or not value:
        raise HTTPException(status_code=400, detail="Memory key and value are required")
    return add_memory_item(workspace_id, key, value)


@app.delete("/workspaces/{workspace_id}/memory/{key}")
def delete_workspace_memory(workspace_id: int, key: str, user: Dict[str, Any] = Depends(get_current_user)):
    if not get_workspace(workspace_id, user["id"]):
        raise HTTPException(status_code=404, detail="Workspace not found")
    deleted = delete_memory_item(workspace_id, key)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory item not found")
    return {"deleted": True}

# --- Phase 4: Ideation & Experiment Design ---
@app.post("/ideation")
def generate_ideation(request: IdeationRequest, user: Optional[Dict[str, Any]] = Depends(get_optional_user)):
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    workspace_id = request.workspace_id
    if workspace_id is not None:
        if not user:
            raise HTTPException(status_code=401, detail="Authorization required for workspaces")
        if not get_workspace(workspace_id, user["id"]):
            raise HTTPException(status_code=404, detail="Workspace not found")

    ideation = _generate_ideation(topic, request.goal, request.constraints)
    response = {"topic": topic, "ideation": ideation}

    if workspace_id is not None:
        saved = create_ideation_item(workspace_id, topic, ideation)
        response["saved"] = saved

    return response


@app.post("/experiment-design")
def generate_experiment_design(request: ExperimentDesignRequest, user: Optional[Dict[str, Any]] = Depends(get_optional_user)):
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    workspace_id = request.workspace_id
    if workspace_id is not None:
        if not user:
            raise HTTPException(status_code=401, detail="Authorization required for workspaces")
        if not get_workspace(workspace_id, user["id"]):
            raise HTTPException(status_code=404, detail="Workspace not found")

    experiment = _generate_experiment_design(topic, request.idea, request.constraints)
    response = {"topic": topic, "experiment": experiment}

    if workspace_id is not None:
        saved = create_experiment_plan(workspace_id, topic, experiment)
        response["saved"] = saved

    return response


@app.get("/workspaces/{workspace_id}/ideation")
def list_workspace_ideation(workspace_id: int, user: Dict[str, Any] = Depends(get_current_user)):
    if not get_workspace(workspace_id, user["id"]):
        raise HTTPException(status_code=404, detail="Workspace not found")
    items = list_ideation_items(workspace_id)
    return {"items": items, "count": len(items)}


@app.delete("/workspaces/{workspace_id}/ideation/{item_id}")
def delete_workspace_ideation(workspace_id: int, item_id: int, user: Dict[str, Any] = Depends(get_current_user)):
    if not get_workspace(workspace_id, user["id"]):
        raise HTTPException(status_code=404, detail="Workspace not found")
    deleted = delete_ideation_item(workspace_id, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ideation item not found")
    return {"deleted": True}


@app.get("/workspaces/{workspace_id}/experiments")
def list_workspace_experiments(workspace_id: int, user: Dict[str, Any] = Depends(get_current_user)):
    if not get_workspace(workspace_id, user["id"]):
        raise HTTPException(status_code=404, detail="Workspace not found")
    plans = list_experiment_plans(workspace_id)
    return {"items": plans, "count": len(plans)}


@app.delete("/workspaces/{workspace_id}/experiments/{plan_id}")
def delete_workspace_experiment(workspace_id: int, plan_id: int, user: Dict[str, Any] = Depends(get_current_user)):
    if not get_workspace(workspace_id, user["id"]):
        raise HTTPException(status_code=404, detail="Workspace not found")
    deleted = delete_experiment_plan(workspace_id, plan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Experiment plan not found")
    return {"deleted": True}


@app.get("/workspaces/{workspace_id}/resources")
def list_workspace_resources(workspace_id: int, user: Dict[str, Any] = Depends(get_current_user)):
    if not get_workspace(workspace_id, user["id"]):
        raise HTTPException(status_code=404, detail="Workspace not found")
    resources = get_resources(workspace_id)
    return {"resources": resources, "count": len(resources)}


@app.post("/workspaces/{workspace_id}/resources")
def add_workspace_resource(workspace_id: int, request: ResourceCreateRequest, user: Dict[str, Any] = Depends(get_current_user)):
    if not get_workspace(workspace_id, user["id"]):
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    resource_type = request.type.strip().lower()
    if not resource_type:
        raise HTTPException(status_code=400, detail="Resource type is required")
        
    title = request.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Resource title is required")
        
    content = request.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Resource content is required")

    return create_resource(
        workspace_id=workspace_id,
        type=resource_type,
        title=title,
        content=content,
        metadata=request.metadata
    )


# Enhanced research endpoints (Phase 2)
@app.get("/quick-search")
@app.post("/quick-search")
def quick_search(topic: str = Query(..., min_length=3, max_length=200, alias="q")):
    """Quick search across all research tools"""
    results = {
        "topic": topic,
        "suggestions": []
    }
    
    try:
        domain_tool = all_tools.get("domain_discovery")
        if domain_tool:
            suggestions = domain_tool.invoke({"topic": topic})
            results["suggestions"] = suggestions
        
        return results
    except Exception as e:
        logger.error(f"Quick search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/popular-topics")
def get_popular_topics():
    """Get popular research topics"""
    return {
        "topics": [
            {"name": "Large Language Models", "category": "AI", "trend": "🔥 Hot"},
            {"name": "Computer Vision", "category": "AI", "trend": "📈 Growing"},
            {"name": "Reinforcement Learning", "category": "ML", "trend": "⭐ Stable"},
            {"name": "Quantum Computing", "category": "Physics", "trend": "🔥 Hot"},
            {"name": "Bioinformatics", "category": "Biology", "trend": "📈 Growing"},
            {"name": "Climate Modeling", "category": "Environmental", "trend": "🔥 Hot"},
            {"name": "Graph Neural Networks", "category": "AI", "trend": "📈 Growing"},
            {"name": "Federated Learning", "category": "ML", "trend": "⭐ Stable"}
        ]
    }


@app.post("/research-suite")
def research_suite(topic: str = Query(..., min_length=3, max_length=200)):
    """Composite research bundle: papers, summaries, mind map, podcast script, code, experiments, outline."""
    try:
        bundle = generate_research_bundle(topic)
        return bundle
    except Exception as e:
        logger.error(f"Research suite failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mindmap")
def generate_mindmap(topic: str = Query(..., min_length=3, max_length=200)):
    """Generate a Mermaid mind map for a research topic."""
    try:
        from app.research_suite import _search_arxiv, _summarize_papers, _generate_mind_map
        papers = _search_arxiv(topic, max_results=3)
        paper_summaries = _summarize_papers(papers)
        bullets = paper_summaries.get("bullets", "")
        mind_map = _generate_mind_map(topic, bullets)
        
        return {
            "topic": topic,
            "mermaid_code": mind_map,
            "papers_count": len(papers)
        }
    except Exception as e:
        logger.error(f"Mind map generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/podcast")
def generate_podcast(topic: str = Query(..., min_length=3, max_length=200)):
    """Generate a two-speaker podcast script for a research topic."""
    try:
        from app.research_suite import _search_arxiv, _summarize_papers, _podcast_script
        papers = _search_arxiv(topic, max_results=3)
        paper_summaries = _summarize_papers(papers)
        bullets = paper_summaries.get("bullets", "")
        script = _podcast_script(topic, bullets)
        
        return {
            "topic": topic,
            "script": script,
            "papers_count": len(papers)
        }
    except Exception as e:
        logger.error(f"Podcast generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/citations")
def generate_citations(topic: str = Query(..., min_length=3, max_length=200)):
    """Get paper citations with inline references and BibTeX."""
    try:
        from app.research_suite import _search_arxiv, _summarize_papers
        papers = _search_arxiv(topic, max_results=5)
        paper_summaries = _summarize_papers(papers)
        
        return {
            "topic": topic,
            "papers": papers,
            "summary_with_citations": paper_summaries.get("bullets", ""),
            "bibtex_entries": paper_summaries.get("bibtex", []),
            "total_papers": len(papers)
        }
    except Exception as e:
        logger.error(f"Citations generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _build_export_payload(messages: List[Dict]) -> Dict[str, Any]:
    return {
        "exported_at": datetime.utcnow().isoformat(),
        "message_count": len(messages),
        "messages": messages
    }

@app.get("/export-chat")
def export_chat_get(format: str = Query("json", alias="format")):
    """Export chat history (GET variant used by frontend)."""
    try:
        messages: List[Dict[str, Any]] = []
        return _build_export_payload(messages)
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export-chat")
def export_chat_post(messages: List[Dict] = Body(default=[])):
    """Export chat history (POST variant)."""
    try:
        return _build_export_payload(messages)
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))