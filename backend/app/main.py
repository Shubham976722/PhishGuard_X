
import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import Response

from backend.app.api.auth import router as auth_router
from backend.app.api.scans import router as scans_router
from backend.app.api.assistant import router as assistant_router
from backend.app.api.dependencies import get_db

from backend.app.exceptions.handlers import (
    validation_exception_handler,
    http_exception_handler,
    database_exception_handler,
    general_exception_handler
)


# Application logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("phishguard")


app = FastAPI(
    title="PhishGuard X API",
    description="AI-powered phishing detection and browser protection platform",
    version="1.0.0"
)

# Cross-Origin Resource Sharing (CORS) Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"^chrome-extension://.*$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security HTTP Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


logger.info("PhishGuard X API initialization started")


# Centralized exception handlers
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler
)

app.add_exception_handler(
    SQLAlchemyError,
    database_exception_handler
)

app.add_exception_handler(
    Exception,
    general_exception_handler
)


# Root endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to PhishGuard X API",
        "status": "running"
    }


# Liveness check
@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy"
    }


# Readiness check
@app.get("/api/v1/health/ready")
def readiness(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {
        "status": "ready",
        "database": "connected"
    }


# Register API routers
app.include_router(auth_router)
app.include_router(scans_router)
app.include_router(assistant_router)


logger.info("PhishGuard X API initialization completed")
