from fastapi import FastAPI

from fund_direction_predictor.settings import load_config


app = FastAPI(
    title="Fund Direction Predictor",
    version="0.1.0",
    summary="Stage-one bootstrap service for project scope and status.",
)


@app.get("/")
def index() -> dict[str, str]:
    return {
        "project": "fund-direction-predictor",
        "stage": "stage-1-bootstrap",
        "message": "Project skeleton initialized. See /scope for the current decision config.",
    }


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "stage": "stage-1-bootstrap"}


@app.get("/scope")
def scope() -> dict[str, object]:
    return load_config()
