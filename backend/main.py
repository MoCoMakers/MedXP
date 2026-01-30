"""
MedXP Context Enrichment Agent API

FastAPI application for enriching medical session context with relevant
SOPs, policies, guidelines, and clinical warnings.
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agents.context_enrichment import get_context_enrichment_agent
from config.settings import settings
from models.request import EnrichmentRequest
from models.response import EnrichmentResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup: Initialize agent and load knowledge bases
    print("Starting MedXP Context Enrichment Agent...")
    agent = get_context_enrichment_agent()
    print(f"Knowledge bases loaded from: {settings.data_dir}")
    yield
    # Shutdown: Cleanup
    print("Shutting down MedXP Context Enrichment Agent...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Context Enrichment Agent for NSCLC Medical Decision Support.
    
    This API accepts patient and session data, retrieves relevant medical knowledge
    (SOPs, policies, guidelines), and returns enriched context with clinical warnings
    for downstream analysis.
    """,
    lifespan=lifespan,
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
    }


@app.post(
    "/api/v1/enrich",
    response_model=EnrichmentResponse,
    tags=["Enrichment"],
    summary="Enrich session context",
    description="""
    Enrich a patient session with relevant medical knowledge.
    
    This endpoint:
    1. Accepts patient data, provider info, and session transcript
    2. Retrieves relevant SOPs, policies, and treatment guidelines
    3. Generates a patient summary with risk factors
    4. Identifies clinical warnings (drug interactions, critical values, etc.)
    5. Returns enriched context for downstream analysis
    """,
)
async def enrich_context(request: EnrichmentRequest) -> EnrichmentResponse:
    """
    Enrich session context with relevant medical knowledge.

    Args:
        request: EnrichmentRequest containing patient, provider, and transcript data

    Returns:
        EnrichmentResponse with enriched context, SOPs, policies, guidelines, and warnings
    """
    try:
        agent = get_context_enrichment_agent()
        response = await agent.enrich(request)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request data: {str(e)}",
        )
    except Exception as e:
        if settings.debug:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Enrichment failed: {str(e)}",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during context enrichment",
        )


@app.get("/api/v1/knowledge/stats", tags=["Knowledge Base"])
async def knowledge_stats():
    """Get statistics about loaded knowledge bases."""
    from services.knowledge_retriever import get_knowledge_retriever

    retriever = get_knowledge_retriever()

    return {
        "sops": {
            "count": len(retriever.sops.get("sops", [])),
            "version": retriever.sops.get("metadata", {}).get("version", "unknown"),
        },
        "policies": {
            "count": len(retriever.policies.get("policies", [])),
            "version": retriever.policies.get("metadata", {}).get("version", "unknown"),
        },
        "guidelines": {
            "count": len(retriever.guidelines.get("guidelines", [])),
            "version": retriever.guidelines.get("metadata", {}).get("version", "unknown"),
        },
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
