import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.database import engine, Base
from app.routes.match_routes import router as match_router
from app.routes.health_routes import router as health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def wait_for_db(retries: int = 10, delay: int = 3):
    """Wait for PostgreSQL to be ready before starting up."""
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Database is ready.")
            return
        except OperationalError as e:
            logger.warning(f"⏳ DB not ready (attempt {attempt}/{retries}): {e}")
            time.sleep(delay)
    raise RuntimeError("❌ Could not connect to the database after multiple retries.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    wait_for_db()
    # Import all models so Base knows about them before create_all
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created / verified.")
    yield
    # Shutdown
    engine.dispose()
    logger.info("🛑 Database connection pool disposed.")


app = FastAPI(
    title="AI Resume ↔ JD Matcher",
    description="Upload a resume and paste a job description to get a semantic match score, skill gap analysis, and recommendations.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(match_router, prefix="/api", tags=["Match"])
app.include_router(health_router, tags=["Health"])


@app.get("/")
def root():
    return {"message": "AI Resume Matcher is running 🚀", "docs": "/docs"}
