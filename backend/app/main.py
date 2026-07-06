import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, async_session
from app.middleware.logging import StructuredLoggingMiddleware
from app.api.v1.router import api_router
from app.seed import seed_houses_and_sections
try:
    from app.services.search.client import get_es_client, init_index
except ImportError:
    get_es_client = init_index = None

logger = logging.getLogger("argus_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup database tables on startup (especially for SQLite in-memory or local dev)
    # When using alembic, tables might be created via migrations, but doing create_all
    # ensures that we can run tests and dev server out-of-the-box easily.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as db:
        if await seed_houses_and_sections(db):
            logger.info("Database seeded with default Houses and Sections.")
        # Initialize Elasticsearch index if needed
    if get_es_client and init_index:
        try:
            es = await get_es_client()
            await init_index(es)
            logger.info("Elasticsearch index ensured on startup.")
        except Exception as e:
            logger.error("Failed to initialize Elasticsearch index: %s", e)
    yield
    # Cleanup on shutdown
    await engine.dispose()

app = FastAPI(
    title="Argus Gamified LMS API",
    description="Principal backend API for Argus EdTech platform, featuring planetary progression and multi-currency economy.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Logging Middleware
app.add_middleware(StructuredLoggingMiddleware)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Format validation errors nicely for frontend display."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "detail": exc.errors(),
            "body": exc.body
        })
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return a structured 500 response."""
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Include Router
app.include_router(api_router, prefix="/api/v1")

frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"


@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(frontend_dir / "index.html")


@app.get("/dashboard", include_in_schema=False)
async def serve_dashboard():
    return FileResponse(frontend_dir / "dashboard.html")


@app.get("/app.js", include_in_schema=False)
async def serve_frontend_script():
    return FileResponse(frontend_dir / "app.js")


@app.get("/healthz", tags=["system"])
async def health_check():
    from datetime import datetime
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
