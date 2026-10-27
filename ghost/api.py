"""api.py: FastAPI backend wiring TabPFN (decide) and Gemma (write).

GET  /api/health      -> status + engine
GET  /api/catalog     -> the service catalog for the logo-tile input
GET  /api/scorecard   -> honest held-out evaluation
POST /api/analyze     -> given a list of the user's subscriptions, rank the ghosts
POST /api/verdict     -> Gemma verdict + action for one ghost
GET  /                -> the UI

Everything runs locally on CPU. No bank login, nothing uploaded.
"""

import os

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ghost import __version__, catalog
from ghost.predict import GHOST_LABELS, evaluate, ghost_type, load_rows, rank
from ghost.remember import write_verdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")

app = FastAPI(title="Subscription Ghost", version=__version__)

_ROWS = load_rows()
_RANKED, _ENGINE = rank(_ROWS)
_SCORECARD = evaluate(_ROWS)


class Subscription(BaseModel):
    name: str
    tier: str = ""
    monthly_cost: float = 0
    annual_cost: float = 0
    uses_per_month: float = 0
    months_active: float = 12
    price_creep_pct: float = 0
    is_annual_prepaid: int = 0
    trial_converted: int = 0
    n_tiers: int = 1
    category: str = "other"


class AnalyzeRequest(BaseModel):
    subscriptions: list[Subscription]


class VerdictRequest(BaseModel):
    ghost: dict


@app.get("/api/health")
def health():
    return {"ok": True, "version": __version__, "engine": _ENGINE,
            "note": "Runs locally on CPU. No bank login. Nothing uploaded."}


@app.get("/api/catalog")
def get_catalog():
    return {"categories": catalog.CATEGORIES, "services": catalog.CATALOG}


@app.get("/api/scorecard")
def scorecard():
    return _SCORECARD


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    rows = []
    for s in req.subscriptions:
        d = s.model_dump()
        d["stopped_using"] = 1 if d["uses_per_month"] == 0 else 0
        rows.append(d)
    ranked, engine = rank(rows)
    overlaps = catalog.find_overlaps(rows)
    total = sum(r["predicted_waste"] for r in ranked if r["ghost_type"] != "worth-it")
    overlap_save = sum(o["could_save"] for o in overlaps)
    return {"engine": engine, "total_waste": total, "ghosts": ranked,
            "overlaps": overlaps, "overlap_save": overlap_save}


@app.post("/api/verdict")
def verdict(req: VerdictRequest):
    return write_verdict(req.ghost)


@app.get("/")
def index():
    return FileResponse(os.path.join(WEB, "index.html"))


if os.path.isdir(os.path.join(WEB, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(WEB, "assets")), name="assets")
