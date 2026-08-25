"""FastAPI entry point for CreditWise."""

from contextlib import asynccontextmanager
import logging
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.modeling import load_model
from app.schemas import LoanApplication, PredictionResponse


STATIC_DIR = Path(__file__).resolve().parent / "static"
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model, app.state.metadata = load_model()
    yield


app = FastAPI(
    title="CreditWise Loan Approval API",
    version="1.0.0",
    description="Loan approval predictions based on the CreditWise supervised ML project.",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
async def health(request: Request) -> dict:
    return {"status": "healthy", "model": request.app.state.metadata["model"]}


@app.get("/api/model-info")
async def model_info(request: Request) -> dict:
    return request.app.state.metadata


@app.post("/api/predict", response_model=PredictionResponse)
async def predict(application: LoanApplication, request: Request) -> PredictionResponse:
    frame = pd.DataFrame([application.model_dump()])
    probability = float(request.app.state.model.predict_proba(frame)[0, 1])
    approved = probability >= request.app.state.metadata.get("threshold", 0.5)
    return PredictionResponse(
        approved=approved,
        decision="Approved" if approved else "Not Approved",
        approval_probability=round(probability, 4),
        confidence=round(max(probability, 1 - probability), 4),
        model=request.app.state.metadata["model"],
        disclaimer="This is an educational model estimate, not a lending decision.",
    )


@app.exception_handler(Exception)
async def unexpected_error(_: Request, error: Exception) -> JSONResponse:
    logger.error(
        "Unhandled error while processing a request",
        exc_info=(type(error), error, error.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "The prediction service encountered an unexpected error."},
    )
