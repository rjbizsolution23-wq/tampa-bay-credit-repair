# services/api/app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import sentry_sdk
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn

from app.core.config import settings
from app.core.database import engine
from app.api.routes import auth, users, credit_reports, disputes, payments, webhooks, admin, blueprint
from app.models import base

# ═══════════════════════════════════════════════════════════════
# SENTRY INITIALIZATION
# ═══════════════════════════════════════════════════════════════

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

# ═══════════════════════════════════════════════════════════════
# LIFESPAN EVENTS
# ═══════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Tampa Bay Credit Repair API...")
    # Create database tables (if using SQLAlchemy direct creation, typically mostly strictly for dev)
    # base.Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    print("👋 Shutting down API...")

# ═══════════════════════════════════════════════════════════════
# APP INITIALIZATION
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Professional Credit Repair Services API - Built by RJ Business Solutions",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# ═══════════════════════════════════════════════════════════════
# RATE LIMITING
# ═══════════════════════════════════════════════════════════════

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ═══════════════════════════════════════════════════════════════
# MIDDLEWARE
# ═══════════════════════════════════════════════════════════════

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# ═══════════════════════════════════════════════════════════════
# PROMETHEUS METRICS
# ═══════════════════════════════════════════════════════════════

Instrumentator().instrument(app).expose(app)

# ═══════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(credit_reports.router, prefix="/api/credit-reports", tags=["Credit Reports"])
app.include_router(disputes.router, prefix="/api/disputes", tags=["Disputes"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(blueprint.router, prefix="/api/blueprint", tags=["Blueprint Audit"])

# ═══════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/api/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
