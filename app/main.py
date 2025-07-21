"""
Main FastAPI application for IDM Latent Space platform
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import time
import logging
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from app.api.endpoints import datasets, models, analysis, auth, metrics
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting IDM Latent Space API")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down IDM Latent Space API")

# Create FastAPI app
app = FastAPI(
    title="IDM Latent Space API",
    description="""
    A comprehensive machine learning platform for analyzing and generating 
    electronic music synthesizer presets.
    
    ## Features
    
    * **Dataset Management** - Upload, validate, and preprocess SysEx files
    * **Machine Learning** - Train models for classification and generation  
    * **Real-time Analysis** - Instant preset analysis and similarity search
    * **Visualization** - Interactive exploration of latent spaces
    """,
    version="1.0.0",
    contact={
        "name": "Shepherd Vovkes",
        "email": "contact@idmlatentspace.com",
        "url": "https://github.com/shepherdvovkes/idmlatentspace"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time and metrics"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Update metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(process_time)
    
    return response

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "idm-latent-space-api"}

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # Add database connectivity check here
    return {"status": "ready", "service": "idm-latent-space-api"}

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# API Routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(datasets.router, prefix="/api/v1/datasets", tags=["Datasets"])
app.include_router(models.router, prefix="/api/v1/models", tags=["Models"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])

# Serve static files
try:
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")
    
    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        """Serve React frontend"""
        try:
            with open("frontend/build/index.html", "r") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            return HTMLResponse(
                content="""
                <html>
                    <head><title>IDM Latent Space</title></head>
                    <body>
                        <h1>IDM Latent Space API</h1>
                        <p>Frontend not built. Please run: <code>cd frontend && npm run build</code></p>
                        <p>API Documentation: <a href="/docs">/docs</a></p>
                    </body>
                </html>
                """,
                status_code=200
            )
except Exception:
    logger.warning("Frontend static files not found")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "IDM Latent Space API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )