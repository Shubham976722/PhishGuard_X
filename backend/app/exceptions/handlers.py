
import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    safe_errors = [
        {
            "location": list(error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        }
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "details": safe_errors
            }
        }
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
):
    detail = exc.detail

    if isinstance(detail, str):
        message = detail
    else:
        message = "The requested operation could not be completed."

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": message
            }
        },
        headers=exc.headers
    )


async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError
):
    logger.exception("Database operation failed")

    return JSONResponse(
        status_code=503,
        content={
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": "A database operation could not be completed."
            }
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
):
    logger.exception("Unexpected application error")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred."
            }
        }
    )
