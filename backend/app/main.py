"""
OpsPilot AI - Main FastAPI Application.
Coordinates Google ADK, Gemini, Python Deterministic Rules, and Swytchcode Integrations.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.utils.config import settings
from app.models.database import engine, Base
from app.api.agent_routes import router as agent_router
from app.api.approval_routes import router as approval_router
from app.api.integration_routes import router as integration_router
from app.api.dashboard_routes import router as dashboard_router
from app.api.demo_routes import router as demo_router

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Autonomous Business Operations Agent for Build with Swytchcode - Track 6"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(agent_router)
app.include_router(approval_router)
app.include_router(integration_router)
app.include_router(dashboard_router)
app.include_router(demo_router)


@app.get("/api/health")
async def health_check():
    return {
        "status": "HEALTHY",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "demo_mode": settings.DEMO_MODE,
        "google_adk": "ACTIVE",
        "integrations": ["paypal", "gmail", "slack", "jira", "notion"]
    }


# Mount built frontend if dist folder exists
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api"):
            return None
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Frontend not built yet. Access /api/health or run Vite dev server."}
