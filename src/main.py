import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.ingestion.router import router as ingestion_router
from src.notion.poller import notion_poller

# Configure Logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("campusdesk.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle events."""
    logger.info("Initializing CampusDesk AI Backend Engine...")
    logger.info(f"Environment: {settings.ENVIRONMENT} | Mock Notion: {settings.MOCK_NOTION} | Mock Email: {settings.MOCK_EMAIL}")

    # Start background poller for Notion Human Approval Gate
    await notion_poller.start()
    
    yield
    
    # Shutdown poller cleanly
    logger.info("Shutting down CampusDesk AI Background Workers...")
    await notion_poller.stop()


app = FastAPI(
    title="CampusDesk AI Engine",
    description="Autonomous Student Request & Approval Engine with Notion Operational Interface",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(ingestion_router)


@app.get("/", include_in_schema=False)
@app.get("/form", include_in_schema=False)
async def serve_student_form():
    """Serve built-in visual student request web portal."""
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "form.html")
    return FileResponse(template_path)


@app.get("/health", tags=["Health & Status"])
async def health_check():
    """System Health Check endpoint."""
    return {
        "status": "healthy",
        "engine": "campusdesk-backend",
        "version": "1.0.0",
        "mock_notion": settings.MOCK_NOTION,
        "mock_email": settings.MOCK_EMAIL,
        "poller_active": notion_poller._running
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=True)
