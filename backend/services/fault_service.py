from pathlib import Path

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


FAULTS_PATH = Path("/app/data/faults/faults_sgc.gpkg")
FAULTS_LAYER = "faults_sgc"

EXPECTED_FAULTS = 91
EXPECTED_CRS = "EPSG:9377"


def load_faults():
    """
    Carga y valida las fallas del SGC.
    """

    if not FAULTS_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {FAULTS_PATH}"
        )

    gdf = gpd.read_file(
        FAULTS_PATH,
        layer=FAULTS_LAYER,
        engine="pyogrio"
    )

    if gdf.empty:
        raise ValueError(
            "El archivo de fallas está vacío."
        )

    required_columns = [
        "OBJECTID",
        "ID_FALLA",
        "TIPO",
        "EXACTITUD_LOCALIZACION",
        "NOMBRE_FALLA",
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

    if len(gdf) != EXPECTED_FAULTS:
        raise ValueError(
            f"Se encontraron {len(gdf)} fallas; "
            f"se esperaban {EXPECTED_FAULTS}."
        )

    if gdf.crs is None:
        raise ValueError(
            "La capa de fallas no tiene CRS."
        )

    if gdf.crs.to_string() != EXPECTED_CRS:
        raise ValueError(
            f"CRS incorrecto: {gdf.crs}. "
            f"Se esperaba {EXPECTED_CRS}."
        )

    if gdf.geometry.isna().any():
        raise ValueError(
            "Existen fallas sin geometría."
        )

    if gdf.geometry.is_empty.any():
        raise ValueError(
            "Existen geometrías de falla vacías."
        )

    return gdf


def get_faults_summary():
    """
    Retorna información general de la capa.
    """

    gdf = load_faults()

    return {
        "status": "ok",
        "total_faults": len(gdf),
        "crs": gdf.crs.to_string(),
    }


def get_faults_geojson():
    """
    Retorna las fallas en EPSG:4326 para visualización web.
    """

    gdf = load_faults()

    gdf_web = gdf.to_crs("EPSG:4326")

    gdf_web = gdf_web[
        [
            "OBJECTID",
            "ID_FALLA",
            "TIPO",
            "EXACTITUD_LOCALIZACION",
            "NOMBRE_FALLA",
            "geometry",
        ]
    ].copy()

    return gdf_web.__geo_interface__


def find_nearest_fault(lat: float, lon: float):
    """
    Encuentra la falla más cercana a una coordenada y
    calcula la distancia mínima punto-línea en metros.
    """

    gdf = load_faults()

    point = (
        gpd.GeoSeries(
            [Point(lon, lat)],
            crs="EPSG:4326"
        )
        .to_crs(gdf.crs)
        .iloc[0]
    )

    distances = gdf.geometry.distance(point)

    nearest_index = distances.idxmin()
    nearest = gdf.loc[nearest_index]

    distance_m = float(
        distances.loc[nearest_index]
    )

    return {
        "OBJECTID": str(nearest["OBJECTID"]),
        "ID_FALLA": (
            None
            if pd.isna(nearest["ID_FALLA"])
            else str(nearest["ID_FALLA"])
        ),
        "distance_m": distance_m,
        "tipo": (
            None
            if pd.isna(nearest["TIPO"])
            else str(nearest["TIPO"])
        ),
        "exactitud_localizacion": (
            None
            if pd.isna(nearest["EXACTITUD_LOCALIZACION"])
            else str(nearest["EXACTITUD_LOCALIZACION"])
        ),
        "nombre_falla": (
            None
            if pd.isna(nearest["NOMBRE_FALLA"])
            else str(nearest["NOMBRE_FALLA"])
        ),
    }