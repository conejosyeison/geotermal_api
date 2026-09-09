from fastapi import FastAPI
from backend.services.spatial_service import (get_footprints_summary,get_footprints_geojson,
                                              find_recortes_by_point,
)
from backend.services.candidate_service import (
    get_candidates_summary,
    find_candidates_by_point,
    get_candidates_geojson,
    get_candidates_filter_summary,
)
from backend.services.evidence_service import (
    get_evidence_summary,
)

from backend.services.spring_service import (
    get_springs_summary,
    get_springs_geojson,
    find_nearest_spring,
)
from backend.services.fault_service import (
    get_faults_summary,
    get_faults_geojson,
    find_nearest_fault,
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

@app.get("/api/evidence/status")
def evidence_status():
    return get_evidence_summary()

@app.get("/api/candidates")
def candidates_geojson(evidence: str = "all"):
    return get_candidates_geojson(evidence)

@app.get("/api/candidates/filter-summary")
def candidates_filter_summary(evidence: str = "all"):
    return get_candidates_filter_summary(evidence)

@app.get("/api/springs/status")
def springs_status():
    return get_springs_summary()


@app.get("/api/springs")
def springs_geojson():
    return get_springs_geojson()


@app.get("/api/springs/nearest")
def nearest_spring(lat: float, lon: float):
    return find_nearest_spring(lat, lon)

@app.get("/api/faults/status")
def faults_status():
    return get_faults_summary()


@app.get("/api/faults")
def faults_geojson():
    return get_faults_geojson()


@app.get("/api/faults/nearest")
def nearest_fault(lat: float, lon: float):
    return find_nearest_fault(lat, lon)