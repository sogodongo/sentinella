import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.routes import evaluate

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("policy service starting", extra={"env": settings.sentinella_env})
    yield
    logger.info("policy service shutting down")


app = FastAPI(
    title="Sentinella Policy Service",
    description="OPA-backed governance policy evaluation for AI inference requests",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.sentinella_env == "development" else None,
    redoc_url=None,
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(evaluate.router)


@app.get("/healthz", include_in_schema=False)
async def liveness():
    return JSONResponse({"status": "ok", "service": settings.service_name})


@app.get("/readyz", include_in_schema=False)
async def readiness():
    return JSONResponse({"status": "ready", "service": settings.service_name})
