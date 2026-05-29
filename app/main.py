from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from tactical_radio_gateway.scenario_state import GatewayRuntimeState, normalize_scenario


ROOT_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT_DIR / "app" / "static"
DEFAULT_SCENARIO = os.getenv("GATEWAY_DEFAULT_SCENARIO", "nominal")

app = FastAPI(
    title="Tactical Radio Cognitive Gateway",
    description="Synthetic defensive lab for radio-link health classification and dynamic gateway policy.",
    version="0.2.0",
)

runtime = GatewayRuntimeState(scenario=normalize_scenario(DEFAULT_SCENARIO))

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/scenarios")
def scenarios() -> dict:
    return {
        "scenarios": [
            {"id": "nominal", "label": "Nominal UHF"},
            {"id": "degraded_climate", "label": "Climate / Distance degradation"},
            {"id": "jammed_attack", "label": "Synthetic jamming-like pattern"},
        ]
    }


@app.get("/api/status")
def status() -> dict:
    return runtime.current_status().model_dump()


@app.post("/api/scenario/{scenario}")
def set_scenario(scenario: str) -> dict:
    try:
        return runtime.set_scenario(scenario).model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/tick")
def tick() -> dict:
    return runtime.tick().model_dump()


@app.get("/api/history")
def history() -> dict:
    return {"history": runtime.history()}


@app.get("/api/export-report")
def export_report() -> dict:
    return runtime.export_report()


@app.post("/api/playback")
def playback() -> dict:
    states = [item.model_dump() for item in runtime.playback()]
    return {"sequence": states, "history": runtime.history()}


@app.post("/api/run-gateway")
def run_gateway() -> dict:
    return runtime.tick().model_dump()
