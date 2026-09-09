from pathlib import Path
from shapely.geometry import Point
import geopandas as gpd
from backend.services.evidence_service import load_evidence

CANDIDATES_PATH = Path(
    "/app/data/candidate_zones/candidate_zones.gpkg"
)

EXPECTED_CANDIDATES = 8433


def load_candidates():
    """
    Carga y valida las zonas candidatas identificadas
    mediante Isolation Forest.
    """

    if not CANDIDATES_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {CANDIDATES_PATH}"
        )

    gdf = gpd.read_file(
        CANDIDATES_PATH,
        engine="pyogrio"
    )

    if gdf.empty:
        raise ValueError(
            "El GeoPackage de zonas candidatas está vacío."
        )

    required_columns = [
        "candidate_id",
        "zone_id",
        "recorte",
        "area_m2",
        "n_cells",
        "score_mean",
        "score_max",
        "has_core_2_5pct",
        "has_strict_core",
        "geometry",
    ]

    missing = [
        column
        for column in required_columns
        if column not in gdf.columns
    ]

    if missing:
        raise ValueError(
            f"Faltan columnas requeridas: {missing}"
        )

    if gdf.crs is None:
        raise ValueError(
            "Las zonas candidatas no tienen CRS definido."
        )

    if len(gdf) != EXPECTED_CANDIDATES:
        raise ValueError(
            f"Se encontraron {len(gdf)} zonas candidatas; "
            f"se esperaban {EXPECTED_CANDIDATES}."
        )

    if gdf.geometry.isna().any():
        raise ValueError(
            "Existen zonas candidatas sin geometría."
        )

    return gdf


def get_candidates_summary():
    """
    Genera un resumen del dataset de zonas candidatas.
    """

    gdf = load_candidates()

    return {
        "status": "ok",
        "total_candidates": len(gdf),
        "total_recortes": int(gdf["recorte"].nunique()),
        "crs": gdf.crs.to_string(),
        "total_area_m2": float(gdf["area_m2"].sum()),
        "strict_core_candidates": int(
            gdf["has_strict_core"].sum()
        ),
        "recortes": sorted(
            gdf["recorte"].unique().tolist()
        ),
    }

def find_candidates_by_point(lat: float, lon: float):
    """
    Determina si una coordenada WGS84 (EPSG:4326)
    intersecta una o más zonas candidatas.

    Las zonas representan anomalías espectrales superficiales
    identificadas mediante Isolation Forest.
    """

    gdf = load_candidates()

    # Crear punto en WGS84
    point_gdf = gpd.GeoDataFrame(
        geometry=[Point(lon, lat)],
        crs="EPSG:4326"
    )

    # Transformar al CRS propio de las zonas candidatas
    point_gdf = point_gdf.to_crs(gdf.crs)

    point = point_gdf.geometry.iloc[0]

    # Consulta espacial
    matches = gdf[gdf.geometry.intersects(point)]

    if matches.empty:
        return {
            "intersects_candidate": False,
            "total_matches": 0,
            "candidates": []
        }

    candidates = []

    for _, row in matches.iterrows():

        candidates.append({
            "candidate_id": str(row["candidate_id"]),
            "zone_id": str(row["zone_id"]),
            "recorte": str(row["recorte"]),

            "area_m2": float(row["area_m2"]),
            "n_cells": int(row["n_cells"]),

            "score_mean": float(row["score_mean"]),
            "score_max": float(row["score_max"]),

            "ndvi_median_zone": float(
                row["ndvi_median_zone"]
            ),

            "ndvi_iqr_zone": float(
                row["ndvi_iqr_zone"]
            ),

            "ndwi_iqr_zone": float(
                row["ndwi_iqr_zone"]
            ),

            "has_core_2_5pct": bool(
                row["has_core_2_5pct"]
            ),

            "core_fraction_area": float(
                row["core_fraction_area"]
            ),

            "has_strict_core": bool(
                row["has_strict_core"]
            ),
        })

    return {
        "intersects_candidate": True,
        "total_matches": len(candidates),
        "candidates": candidates
    }

def get_candidates_geojson(evidence_filter: str = "all"):
    """
    Retorna las zonas candidatas como GeoJSON, opcionalmente
    filtradas según la evidencia independiente del recorte.

    Filtros:
        all         -> todos los candidatos
        hydrothermal -> recortes con evidencia H robusta
        structural   -> recortes con evidencia F robusta
        convergence  -> recortes con convergencia H + F
    """

    candidates = load_candidates()
    evidence = load_evidence()

    # --------------------------------------------------------
    # Incorporar evidencia a cada candidato
    # --------------------------------------------------------

    candidates = candidates.merge(
        evidence[
            [
                "recorte",
                "hydrothermal_robust",
                "structural_robust",
                "convergence_hf",
                "evidence_class",
            ]
        ],
        on="recorte",
        how="left",
        validate="many_to_one",
    )

    # Comprobar que todos encontraron evidencia
    if candidates["evidence_class"].isna().any():

        missing = (
            candidates.loc[
                candidates["evidence_class"].isna(),
                "recorte"
            ]
            .unique()
            .tolist()
        )

        raise ValueError(
            f"Existen candidatos sin clasificación "
            f"de evidencia: {missing}"
        )

    # --------------------------------------------------------
    # Aplicar filtro
    # --------------------------------------------------------

    if evidence_filter == "hydrothermal":

        candidates = candidates[
            candidates["hydrothermal_robust"]
        ]

    elif evidence_filter == "structural":

        candidates = candidates[
            candidates["structural_robust"]
        ]

    elif evidence_filter == "convergence":

        candidates = candidates[
            candidates["convergence_hf"]
        ]

    elif evidence_filter != "all":

        raise ValueError(
            "Filtro no válido. Use: all, hydrothermal, "
            "structural o convergence."
        )

    # --------------------------------------------------------
    # Transformación para mapa web
    # --------------------------------------------------------

    candidates = candidates.to_crs("EPSG:4326")

    # Solo enviamos lo necesario al navegador
    candidates = candidates[
        [
            "candidate_id",
            "zone_id",
            "recorte",
            "area_m2",
            "score_mean",
            "score_max",
            "has_strict_core",
            "hydrothermal_robust",
            "structural_robust",
            "convergence_hf",
            "evidence_class",
            "geometry",
        ]
    ].copy()

    return candidates.__geo_interface__

def get_candidates_filter_summary(evidence_filter: str = "all"):
    """
    Valida cuántos candidatos quedan después de aplicar
    un filtro de evidencia y en qué recortes se encuentran.
    """

    candidates = load_candidates()
    evidence = load_evidence()

    candidates = candidates.merge(
        evidence[
            [
                "recorte",
                "hydrothermal_robust",
                "structural_robust",
                "convergence_hf",
                "evidence_class",
            ]
        ],
        on="recorte",
        how="left",
        validate="many_to_one",
    )

    if candidates["evidence_class"].isna().any():
        raise ValueError(
            "Existen candidatos sin clasificación de evidencia."
        )

    if evidence_filter == "hydrothermal":
        candidates = candidates[
            candidates["hydrothermal_robust"]
        ]

    elif evidence_filter == "structural":
        candidates = candidates[
            candidates["structural_robust"]
        ]

    elif evidence_filter == "convergence":
        candidates = candidates[
            candidates["convergence_hf"]
        ]

    elif evidence_filter != "all":
        raise ValueError(
            "Filtro no válido. Use: all, hydrothermal, "
            "structural o convergence."
        )

    counts = (
        candidates["recorte"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    return {
        "filter": evidence_filter,
        "total_candidates": len(candidates),
        "total_recortes": int(candidates["recorte"].nunique()),
        "recortes": sorted(
            candidates["recorte"].unique().tolist()
        ),
        "candidates_by_recorte": counts,
    }