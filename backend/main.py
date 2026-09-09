from fastapi import FastAPI
from backend.services.spatial_service import (get_footprints_summary,get_footprints_geojson,
                                              find_recortes_by_point,
)
from backend.services.candidate_service import (
    get_candidates_summary,
    find_candidates_by_point,
)
app = FastAPI(
    title="Geotermal API",
    description="API para el sistema de apoyo a la priorización de anomalías superficiales para exploración geotérmica",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Geotermal API funcionando correctamente"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }
@app.get("/api/recortes/status")
def recortes_status():
    return get_footprints_summary()

@app.get("/api/recortes")
def recortes_geojson():
    return get_footprints_geojson()

@app.get("/api/recortes/query")
def query_recorte(lat: float, lon: float):
    return find_recortes_by_point(lat, lon)

@app.get("/api/candidates/status")
def candidates_status():
    return get_candidates_summary()

@app.get("/api/candidates/query")
def query_candidate(lat: float, lon: float):
    return find_candidates_by_point(lat, lon)
