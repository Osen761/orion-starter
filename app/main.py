"""FastAPI entry point for Orion."""

from __future__ import annotations

import logging
import time
import warnings

from fastapi import FastAPI, HTTPException, Request

warnings.filterwarnings(
    "ignore",
    message="The default value of `allowed_objects` will change in a future version.*",
)

from app.agent.agent import run_agent
from app.config.settings import settings
from app.schemas.models import AnalyzeRequest, AnalyzeResponse, HealthResponse


logger = logging.getLogger("orion.api")

app = FastAPI(
    title="AI Data Analyst Agent",
    version="1.0.0",
    description="Orion is an AI data analyst agent that answers natural-language questions about a CSV dataset.",
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log the request method, path, and total response time."""

    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "%s %s completed in %.2fms",
        request.method,
        request.url.path,
        duration_ms,
    )
    return response


@app.on_event("startup")
def warm_up_agent() -> None:
    """Warm the Orion agent during app startup."""

    run_agent("What columns are in the dataset?", "")


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return a basic health response for Cloud Run."""

    return HealthResponse(
        status="ok",
        model=f"{settings.LLM_PROVIDER}/{settings.LLM_MODEL}",
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Run the Orion agent against a user question."""

    try:
        result = run_agent(request.question, request.session_id or "")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc

    return AnalyzeResponse(**result)
