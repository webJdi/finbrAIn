from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
try:
    from app.routers import agents, analysis
    ROUTERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import routers: {e}")
    ROUTERS_AVAILABLE = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting FinbrAIn Backend Server...")
    yield
    # Shutdown
    print("👋 Shutting down FinbrAIn Backend Server...")

# Create FastAPI app
app = FastAPI(
    title="FinbrAIn - Multi-Agent Financial Advisory System",
    description="AI-powered financial research and analysis system using LangChain and LangGraph",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "FinbrAIn Multi-Agent Financial Advisory System",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "finbrain-backend"}

# Include routers
if ROUTERS_AVAILABLE:
    app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
    app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
    print("✅ API routers loaded successfully")
else:
    print("⚠️  API routers not available - some endpoints may not work")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "true").lower() == "true"
    )