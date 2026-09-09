from pathlib import Path
from shapely.geometry import Point
import geopandas as gpd


FOOTPRINTS_PATH = Path("/app/data/footprints/recortes_27.gpkg")
FOOTPRINTS_LAYER = "recortes_27"
EXPECTED_CRS = "EPSG:9377"
EXPECTED_RECORTES = 27


def load_footprints():
    """
    Carga y valida los footprints de los 27 recortes UAS.
    """

    if not FOOTPRINTS_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {FOOTPRINTS_PATH}"
        )

    gdf = gpd.read_file(
        FOOTPRINTS_PATH,
        layer=FOOTPRINTS_LAYER,
        engine="pyogrio"
    )

    # Validaciones básicas
    if gdf.empty:
        raise ValueError("El GeoPackage no contiene geometrías.")

    if "recorte" not in gdf.columns:
        raise ValueError(
            "El GeoPackage no contiene la columna 'recorte'."
        )

    if gdf.crs is None:
        raise ValueError(
            "Los footprints no tienen un CRS definido."
        )

    if gdf.crs.to_string().upper() != EXPECTED_CRS:
        raise ValueError(
            f"CRS inesperado: {gdf.crs}. "
            f"Se esperaba {EXPECTED_CRS}."
        )

    if len(gdf) != EXPECTED_RECORTES:
        raise ValueError(
            f"Se encontraron {len(gdf)} recortes. "
            f"Se esperaban {EXPECTED_RECORTES}."
        )

    if gdf.geometry.isna().any():
        raise ValueError(
            "Existen recortes sin geometría."
        )

    return gdf


def get_footprints_summary():
    """
    Retorna información general para comprobar el dataset.
    """

    gdf = load_footprints()

    return {
        "status": "ok",
        "total_recortes": len(gdf),
        "crs": gdf.crs.to_string(),
        "recortes": sorted(gdf["recorte"].tolist()),
        "area_total_m2": float(gdf["area_m2"].sum()),
    }

def get_footprints_geojson():
    """
    Retorna los footprints en EPSG:4326 para visualización web.
    """

    gdf = load_footprints()

    # Los mapas web trabajan con longitud/latitud
    gdf_web = gdf.to_crs("EPSG:4326")

    # Solo enviamos los atributos necesarios al frontend
    gdf_web = gdf_web[
        [
            "recorte",
            "resolution_x",
            "resolution_y",
            "area_m2",
            "geometry",
        ]
    ].copy()

    return gdf_web.__geo_interface__

def find_recortes_by_point(lat: float, lon: float):
    """
    Determina qué recorte(s) contienen una coordenada
    recibida en WGS84 (EPSG:4326).
    """

    gdf = load_footprints()

    # Crear punto en coordenadas geográficas
    point_gdf = gpd.GeoDataFrame(
        geometry=[Point(lon, lat)],
        crs="EPSG:4326"
    )

    # Transformar al mismo CRS de los footprints
    point_gdf = point_gdf.to_crs(gdf.crs)

    point = point_gdf.geometry.iloc[0]

    # intersects incluye también puntos exactamente sobre el borde
    matches = gdf[gdf.geometry.intersects(point)]

    if matches.empty:
        return {
            "inside": False,
            "total_matches": 0,
            "recortes": []
        }

    recortes = []

    for _, row in matches.iterrows():
        recortes.append({
            "recorte": row["recorte"],
            "area_m2": float(row["area_m2"]),
            "resolution_x": float(row["resolution_x"]),
            "resolution_y": float(row["resolution_y"]),
        })

    return {
        "inside": True,
        "total_matches": len(recortes),
        "recortes": recortes
    }