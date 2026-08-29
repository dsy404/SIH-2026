from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.routes import datasets

app = FastAPI(title=settings.app_name, version="0.1.0")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasets.router, prefix=settings.api_prefix)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name}
