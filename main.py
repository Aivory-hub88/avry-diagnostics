"""
avry-diagnostics Microservice Entry Point
Description: Diagnostic calculations, scoring
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AVRY Diagnostics Service",
    description="Diagnostic calculations, scoring",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routes
try:
    from app.routes.diagnostic import router as diagnostic_router
    app.include_router(diagnostic_router)
    print("[✓] Diagnostic routes registered")
except Exception as e:
    print(f"[!] Warning: Could not import diagnostic routes: {e}")
try:
    from app.routes import *
    # Include routers here as needed
except Exception as e:
    print(f"Warning: Could not import routes: {e}")

# Health check endpoint
@app.get("/health")
async def health():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "avry-diagnostics",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Service info"""
    return {
        "service": "AVRY Diagnostics Service",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8085"))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENVIRONMENT", "production") == "development"
    )
