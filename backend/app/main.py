import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import APP_NAME, APP_DESCRIPTION, API_V1_STR, BASE_DIR, FRONTEND_DIR
from app.db.database import db_manager
from app.db.seed_data import initialize_seed_data
from app.api.auth import router as auth_router
from app.api.resumes import router as resumes_router
from app.api.matching import router as matching_router
from app.api.jobs import router as jobs_router

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router, prefix=API_V1_STR)
app.include_router(resumes_router, prefix=API_V1_STR)
app.include_router(matching_router, prefix=API_V1_STR)
app.include_router(jobs_router, prefix=API_V1_STR)

# Startup Event
@app.on_event("startup")
async def startup_event():
    await db_manager.connect()
    await initialize_seed_data()
    print("CareerPulse AI backend initialized and ready.")

# Health check
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": APP_NAME,
        "database": "MongoDB" if db_manager.is_mongo else "Resilient Adapter"
    }

# Mount Frontend Static Files
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # If path starts with api, return 404 json
    if full_path.startswith("api/"):
        return JSONResponse(status_code=404, content={"detail": "API route not found"})
    
    # Try direct file in frontend folder
    frontend_file = FRONTEND_DIR / full_path
    if full_path and frontend_file.exists() and frontend_file.is_file():
        return FileResponse(str(frontend_file))
    
    # Fallback to index.html for SPA routing
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    return JSONResponse(status_code=200, content={"message": "CareerPulse AI API running. Frontend loading..."})
