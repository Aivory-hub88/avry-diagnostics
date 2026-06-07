"""AVRY-Diagnostics Service"""
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import settings

@asynccontextmanager
async def lifespan(app):
    print(f"[{datetime.now().isoformat()}] AVRY-Diagnostics starting...")
    yield
    print(f"[{datetime.now().isoformat()}] AVRY-Diagnostics shutting down...")

app = FastAPI(title="AVRY Diagnostics", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register the proper router (has auth, persistence, etc.)
try:
    from app.routes.diagnostic import router as diagnostic_router
    app.include_router(diagnostic_router)
    print("[✓] Diagnostic routes registered")
except Exception as e:
    print(f"[!] Could not import diagnostic routes: {e}")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "avry-diagnostics", "port": int(os.getenv("PORT", "8085")), "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/debug/info")
async def debug_info():
    return {"service": "avry-diagnostics", "port": int(os.getenv("PORT", "8085")), "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", settings.port or 8085))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
