from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import init_db
from app.routers import grid, sample_data, synthetic_grid, realtime, demo_grid, hrvc_risk, risk, usps, liquid_galaxy, drainage, decision, risk_memory, monitoring
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if production grid is available
try:
    from app.routers import production_grid
    PRODUCTION_GRID_AVAILABLE = True
except ImportError:
    PRODUCTION_GRID_AVAILABLE = False
    logger.warning("Production grid generation not available - install geospatial libraries")

app = FastAPI(
    title="PuneRakshak - Disaster Risk Assessment Platform",
    description="Layer 1: Data & Micro-Grid Spatial Foundation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include routers
app.include_router(grid.router)
app.include_router(sample_data.router)
app.include_router(synthetic_grid.router)
app.include_router(realtime.router)
app.include_router(demo_grid.router)
app.include_router(hrvc_risk.router)
app.include_router(risk.router)
app.include_router(usps.router)
app.include_router(liquid_galaxy.router)
app.include_router(drainage.router)
app.include_router(decision.router)
app.include_router(risk_memory.router)
app.include_router(monitoring.router)
if PRODUCTION_GRID_AVAILABLE:
    app.include_router(production_grid.router)
    logger.info("Production grid generation enabled")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Initializing database...")
    
    # Import all models to ensure they're registered with SQLAlchemy
    try:
        from app.models import grid_cell, risk_memory, monitoring
        logger.info("Models imported successfully")
    except Exception as e:
        logger.warning(f"Error importing models: {e}")
    
    init_db()
    logger.info("Database initialized successfully")

@app.get("/")
def root():
    """Serve the PuneRakshak homepage"""
    homepage = os.path.join(os.path.dirname(__file__), "static", "punerakshak.html")
    if os.path.exists(homepage):
        return FileResponse(homepage)
    
    # Fallback to old index
    static_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    
    endpoints = {
        "grid_cells": "/grid-cells",
        "sample_data": "/generate-sample-data",
        "synthetic_grid": "/synthetic/generate-pune-grid",
        "docs": "/docs"
    }
    
    if PRODUCTION_GRID_AVAILABLE:
        endpoints["production_grid"] = "/production/generate-grid"
    
    return {
        "message": "PuneRakshak API - Layer 1: Spatial Grid Foundation",
        "version": "1.0.0",
        "endpoints": endpoints,
        "production_grid_available": PRODUCTION_GRID_AVAILABLE
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "production_grid": PRODUCTION_GRID_AVAILABLE
    }
