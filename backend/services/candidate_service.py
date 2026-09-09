from pathlib import Path
from shapely.geometry import Point
import geopandas as gpd


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