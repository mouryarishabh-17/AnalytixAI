from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AnalytixAI")

async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to catch all unhandled exceptions
    and return a consistent JSON error response.
    """
    
    # Log the full stack trace for debugging
    error_msg = str(exc)
    traceback_str = traceback.format_exc()
    logger.error(f"Unhandled Exception: {error_msg}\n{traceback_str}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later.",
            # Only show technical details in development (optional)
            # "technical_detail": error_msg 
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handler for explicit HTTPExceptions (e.g., 404, 400)
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": "Request Failed",
            "detail": exc.detail
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler for Pydantic validation errors (e.g., missing fields)
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"])
        msg = error["msg"]
        errors.append(f"{field}: {msg}")
        
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Validation Error",
            "detail": "; ".join(errors)
        }
    )
