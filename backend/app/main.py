import os
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

from app.api.v1 import auth, oauth, sessions, meta
from app.core.config import settings
from app.core.logging import logger, setup_logging


# ─── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    logger.info("startup", app=settings.APP_NAME, env=settings.ENVIRONMENT)
    yield
    logger.info("shutdown", app=settings.APP_NAME)


# ─── App Factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Production-ready FastAPI backend — Clean Architecture 2026",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ─── Middleware ─────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# ─── Global Exception Handlers ─────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning("validation_error", path=str(request.url), errors=exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status_code": 422,
            "code": "VALIDATION_ERROR",
            "detail": exc.errors(),
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    logger.warning("value_error", path=str(request.url), error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status_code": 400,
            "code": "BAD_REQUEST",
            "detail": str(exc),
        },
    )


@app.exception_handler(PermissionError)
async def permission_error_handler(
    request: Request, exc: PermissionError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"status_code": 403, "code": "FORBIDDEN", "detail": str(exc)},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "unhandled_exception",
        path=str(request.url),
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": 500,
            "code": "INTERNAL_ERROR",
            "detail": "An unexpected error occurred.",
        },
    )


# ─── Routers ───────────────────────────────────────────────────────────────────

PREFIX = "/api/v1"

app.include_router(auth.router, prefix=PREFIX)
app.include_router(oauth.router, prefix=PREFIX)
app.include_router(sessions.router, prefix=PREFIX)
app.include_router(meta.router, prefix=PREFIX)

from fastapi.staticfiles import StaticFiles
add_pagination(app)

# ─── Static Files ──────────────────────────────────────────────────────────────

if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)

app.mount(settings.UPLOAD_URL, StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# ─── Health Check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    return {"status": "ok", "app": settings.APP_NAME}
