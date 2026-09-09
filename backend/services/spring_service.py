from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point
import pandas as pd


SPRINGS_PATH = Path("/app/data/springs/springs_sgc.gpkg")
SPRINGS_LAYER = "springs_sgc"

EXPECTED_SPRINGS = 21
EXPECTED_CRS = "EPSG:9377"


def load_springs():
    """
    Carga y valida los manantiales hidrotermales del SGC.
    """

    if not SPRINGS_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {SPRINGS_PATH}"
        )

    gdf = gpd.read_file(
        SPRINGS_PATH,
        layer=SPRINGS_LAYER,
        engine="pyogrio"
    )

    if gdf.empty:
        raise ValueError(
            "El archivo de manantiales está vacío."
        )

    required_columns = [
        "ID_MANANTIAL",
        "LATITUD",
        "LONGITUD",
        "FECHA",
        "TEMPERATUR",
        "PH_IN_SITU",
        "CONDUCTIVIDAD",
        "CLASIFICACIÓN",
        "ZONA_ESTUDIO",
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

    if len(gdf) != EXPECTED_SPRINGS:
        raise ValueError(
            f"Se encontraron {len(gdf)} manantiales; "
            f"se esperaban {EXPECTED_SPRINGS}."
        )

    if gdf.crs is None:
        raise ValueError(
            "La capa de manantiales no tiene CRS."
        )

    if gdf.crs.to_string() != EXPECTED_CRS:
        raise ValueError(
            f"CRS incorrecto: {gdf.crs}. "
            f"Se esperaba {EXPECTED_CRS}."
        )

    if gdf.geometry.isna().any():
        raise ValueError(
            "Existen manantiales sin geometría."
        )

    if gdf["ID_MANANTIAL"].duplicated().any():
        raise ValueError(
            "Existen ID_MANANTIAL duplicados."
        )

    return gdf


def get_springs_summary():
    """
    Retorna información general de la capa.
    """

    gdf = load_springs()

    return {
        "status": "ok",
        "total_springs": len(gdf),
        "crs": gdf.crs.to_string(),
    }


def get_springs_geojson():
    """
    Retorna los manantiales en EPSG:4326
    para visualización web.
    """

    gdf = load_springs()

    gdf_web = gdf.to_crs("EPSG:4326")

    columns = [
        "ID_MANANTIAL",
        "LATITUD",
        "LONGITUD",
        "FECHA",
        "TEMPERATUR",
        "PH_IN_SITU",
        "CONDUCTIVIDAD",
        "CLASIFICACIÓN",
        "ZONA_ESTUDIO",
        "geometry",
    ]

    gdf_web = gdf_web[columns].copy()

    return gdf_web.__geo_interface__


def find_nearest_spring(lat: float, lon: float):
    """
    Encuentra el manantial más cercano a una coordenada
    y calcula la distancia en metros.
    """

    gdf = load_springs()

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
    distance_m = float(distances.loc[nearest_index])

    return {
        "ID_MANANTIAL": str(nearest["ID_MANANTIAL"]),
        "distance_m": distance_m,
        "latitude": float(nearest["LATITUD"]),
        "longitude": float(nearest["LONGITUD"]),
        "fecha": (
            None
            if pd.isna(nearest["FECHA"])
            else str(nearest["FECHA"])
        ),
        "temperatura": (
            None
            if pd.isna(nearest["TEMPERATUR"])
            else float(nearest["TEMPERATUR"])
        ),
        "ph": (
            None
            if pd.isna(nearest["PH_IN_SITU"])
            else float(nearest["PH_IN_SITU"])
        ),
        "conductividad": (
            None
            if pd.isna(nearest["CONDUCTIVIDAD"])
            else float(nearest["CONDUCTIVIDAD"])
        ),
        "clasificacion": (
            None
            if pd.isna(nearest["CLASIFICACIÓN"])
            else str(nearest["CLASIFICACIÓN"])
        ),
        "zona_estudio": (
            None
            if pd.isna(nearest["ZONA_ESTUDIO"])
            else str(nearest["ZONA_ESTUDIO"])
        ),
    }