import json
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .contracts import FoundationResponse, Provenance, ProvenanceResponse, RouteRequest
from .facilities import load_local_shelter_context, load_processed_facilities
from .routing import build_route
from .simulation import router as simulation_router
from .goal4a import router as goal4a_router
from .goal5a import router as goal5a_router
from .modes import router as modes_router
from .optional_modules import router as optional_modules_router
from .flood_readiness import router as flood_readiness_router
from .readiness import readiness_payload
from services.release.version import release_version


app = FastAPI(title="SAFE-Twin Anyang API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
app.include_router(simulation_router)
app.include_router(goal4a_router)
app.include_router(goal5a_router)
app.include_router(modes_router)
app.include_router(optional_modules_router)
app.include_router(flood_readiness_router)


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "service": "safe-twin-anyang", "product_scope": "FINAL_RELEASE_4D_ADMIN_WHAT_IF"}


@app.get("/readyz")
def readyz() -> dict:
    payload = readiness_payload()
    if payload["status"] != "READY":
        raise HTTPException(status_code=503, detail={"status": payload["status"], "mandatory_checks": payload["mandatory_checks"]})
    return {"status": "ready", "mandatory_checks": payload["mandatory_checks"]}

SOURCE_AVAILABILITY = {
    "CIVIL_DEFENSE_SHELTER": {"status": "DOWNLOADED", "data": "real", "count": 231},
    "EMERGENCY_WATER": {"status": "DOWNLOADED", "data": "real", "count": 71},
    "AED": {"status": "DOWNLOADED", "data": "real", "count": 305},
    "EARTHQUAKE_OUTDOOR_SHELTER": {"status": "HUMAN_AUTH_REQUIRED", "data": []},
    "EMERGENCY_MEDICAL": {"status": "HUMAN_AUTH_REQUIRED", "data": []},
    "FIRE_WATER": {"status": "HUMAN_AUTH_REQUIRED", "data": []},
    "TEMPORARY_HOUSING": {"status": "INTENTIONALLY_EXCLUDED", "data": []},
    "CIVIL_DEFENSE_SHELTER_LOCAL": {"status": "DOWNLOADED", "data": "real", "count": 224},
}


@lru_cache(maxsize=1)
def real_facilities() -> list[dict]:
    return load_processed_facilities()


@lru_cache(maxsize=1)
def local_shelter_context() -> list[dict]:
    return load_local_shelter_context()


@lru_cache(maxsize=1)
def osm_payload() -> dict:
    path = Path(__file__).resolve().parents[2] / "data/raw/openstreetmap/anyang_pedestrian_broad/overpass.json"
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/foundation", response_model=FoundationResponse)
def foundation() -> FoundationResponse:
    return FoundationResponse(
        name="SAFE-Twin Anyang",
        stage="Goal 2 real-data spatial foundation",
        provenance=Provenance.OFFICIAL,
        fixture=False,
        allowed_provenance=list(Provenance),
        counts={"CIVIL_DEFENSE_SHELTER": 231, "EMERGENCY_WATER": 71, "AED": 305},
    )


@app.get("/api/facilities", response_model=ProvenanceResponse)
def facilities(type: str = Query(default="civil_defense")) -> ProvenanceResponse:
    aliases = {"civil_defense": "CIVIL_DEFENSE_SHELTER", "shelter": "CIVIL_DEFENSE_SHELTER", "water": "EMERGENCY_WATER", "aed": "AED", "local_shelter": "CIVIL_DEFENSE_SHELTER_LOCAL"}
    category = aliases.get(type, type.upper())
    source_items = local_shelter_context() if category == "CIVIL_DEFENSE_SHELTER_LOCAL" else real_facilities()
    items = [item for item in source_items if item["category"] == category]
    return ProvenanceResponse(
        provenance=Provenance.OFFICIAL if items else Provenance.STALE_OR_UNKNOWN,
        fixture=False,
        items=items,
        source_availability=SOURCE_AVAILABILITY,
    )


@app.get("/api/data-sources")
def data_sources() -> dict:
    return {"provenance": Provenance.OFFICIAL, "sources": SOURCE_AVAILABILITY}


@app.get("/api/release/readiness")
def release_readiness() -> dict:
    return readiness_payload()


@app.get("/api/release/version")
def release_version_endpoint() -> dict[str, str]:
    return release_version()


@app.post("/api/routes")
def routes(request: RouteRequest) -> dict:
    try:
        return build_route(
            osm_payload(),
            (request.origin["latitude"], request.origin["longitude"]),
            (request.destination["latitude"], request.destination["longitude"]),
        )
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


DIST = Path(__file__).resolve().parents[2] / "dist"
if DIST.exists():
    @app.get("/admin", include_in_schema=False)
    @app.get("/simulate", include_in_schema=False)
    @app.get("/about-data", include_in_schema=False)
    def spa_entry() -> FileResponse:
        return FileResponse(DIST / "index.html")

    app.mount("/", StaticFiles(directory=DIST, html=True), name="web")
