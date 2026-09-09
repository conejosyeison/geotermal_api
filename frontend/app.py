import streamlit as st
import requests
import folium
from streamlit_folium import st_folium


# ============================================================
# CONFIGURACIÓN
# ============================================================

API_URL = "http://backend:8000"

st.set_page_config(
    page_title="Geotermal Platform",
    page_icon="🌋",
    layout="wide"
)


# ============================================================
# TÍTULO
# ============================================================

st.title("Geotermal Platform")

st.subheader(
    "Sistema de apoyo a la priorización de anomalías superficiales "
    "para exploración geotérmica"
)

st.sidebar.header("Capas de análisis")

mostrar_candidatos = st.sidebar.checkbox(
    "Mostrar zonas candidatas",
    value=False
)

filtro_evidencia = st.sidebar.radio(
    "Filtro de evidencia",
    options=[
        "Todas",
        "Hidrotermal robusta",
        "Estructural robusta",
        "Convergencia H + F",
    ],
    index=3,
)

filtros_api = {
    "Todas": "all",
    "Hidrotermal robusta": "hydrothermal",
    "Estructural robusta": "structural",
    "Convergencia H + F": "convergence",
}
descripcion_filtros = {
    "Todas": (
        "Muestra todas las zonas candidatas de anomalía espectral "
        "identificadas mediante Isolation Forest."
    ),
    "Hidrotermal robusta": (
        "Muestra zonas candidatas pertenecientes a recortes con "
        "evidencia hidrotermal robusta."
    ),
    "Estructural robusta": (
        "Muestra zonas candidatas pertenecientes a recortes con "
        "evidencia estructural robusta."
    ),
    "Convergencia H + F": (
        "Muestra zonas candidatas pertenecientes a recortes con "
        "convergencia robusta de evidencia hidrotermal y estructural. "
        "En este estudio corresponde a PAIPA-10 y PAIPA-16."
    ),
}

st.sidebar.caption(
    descripcion_filtros[filtro_evidencia]
)
st.write(
    "Exploración interactiva de los resultados geoespaciales "
    "obtenidos para la zona Paipa–Iza."
)


# ============================================================
# OBTENER FOOTPRINTS DESDE FASTAPI
# ============================================================

try:

    response = requests.get(
        f"{API_URL}/api/recortes",
        timeout=30
    )

    response.raise_for_status()

    footprints = response.json()

except requests.RequestException as error:

    st.error(
        "No fue posible obtener los recortes desde FastAPI."
    )

    st.exception(error)
    st.stop()


# ============================================================
# MAPA
# ============================================================

# Centro inicial aproximado de Paipa–Iza
mapa = folium.Map(
    location=[5.72, -73.05],
    zoom_start=11,
    tiles="OpenStreetMap"
)


# ============================================================
# FOOTPRINTS
# ============================================================

folium.GeoJson(
    footprints,
    name="Recortes UAS",
    style_function=lambda feature: {
        "fillOpacity": 0.15,
        "weight": 2,
    },
    highlight_function=lambda feature: {
        "fillOpacity": 0.35,
        "weight": 4,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=[
            "recorte",
            "resolution_x",
            "resolution_y",
            "area_m2",
        ],
        aliases=[
            "Recorte:",
            "Resolución X (m):",
            "Resolución Y (m):",
            "Área (m²):",
        ],
        localize=True,
        sticky=True,
    ),
).add_to(mapa)

if mostrar_candidatos:

    try:
        candidate_map_response = requests.get(
            f"{API_URL}/api/candidates",
            params={
                "evidence": filtros_api[filtro_evidencia]
            },
            timeout=30
        )

        candidate_map_response.raise_for_status()
        candidate_geojson = candidate_map_response.json()
        def estilo_candidato(feature):
            properties = feature["properties"]
            if properties["convergence_hf"]:
                color = "#8B0000"       # Convergencia H + F
            elif properties["hydrothermal_robust"]:
                color = "#E67E22"       # Evidencia hidrotermal
            elif properties["structural_robust"]:
                color = "#6C3483"       # Evidencia estructural
            else:
                color = "#2471A3"       # Candidato espectral
            return {
                "color": color,
                "fillColor": color,
                "fillOpacity": 0.65,
                "weight": 1,
                "opacity": 0.9,
            }



        folium.GeoJson(
            candidate_geojson,
            name=f"Zonas candidatas — {filtro_evidencia}",
            style_function=estilo_candidato,
            highlight_function=lambda feature: {
                "fillOpacity": 0.9,
                "weight": 3,
            },

            tooltip=folium.GeoJsonTooltip(
                fields=[
                   "candidate_id",
                   "recorte",
                   "score_mean",
                   "area_m2",
                   "evidence_class",
                ],
                aliases=[
                    "Candidato:",
                    "Recorte:",
                    "Score medio:",
                    "Área (m²):",
                    "Evidencia del recorte:",
                ],
                localize=True,
                sticky=True,


            ),

        ).add_to(mapa)

    except requests.RequestException as error:
        st.error(
            "No fue posible cargar las zonas candidatas."
        )
        st.exception(error)
# ============================================================
# CONTROL DE CAPAS
# ============================================================

leyenda_html = """
<div style="
    position: fixed;
    bottom: 40px;
    left: 40px;
    width: 245px;
    background-color: white;
    border: 2px solid grey;
    z-index: 9999;
    font-size: 14px;
    padding: 10px;
    border-radius: 6px;
">
    <b>Nivel de evidencia</b><br><br>

    <span style="color:#2471A3;">■</span>
    Anomalía espectral<br>

    <span style="color:#E67E22;">■</span>
    Evidencia hidrotermal robusta<br>

    <span style="color:#6C3483;">■</span>
    Evidencia estructural robusta<br>

    <span style="color:#8B0000;">■</span>
    Convergencia robusta H + F<br>
</div>
"""

mapa.get_root().html.add_child(
    folium.Element(leyenda_html)
)
folium.LayerControl().add_to(mapa)


# ============================================================
# MOSTRAR MAPA
# ============================================================

resultado_mapa = st_folium(
    mapa,
    width=None,
    height=650,
    returned_objects=["last_clicked"],
    
)


# ============================================================
# CLIC DEL USUARIO
# ============================================================

st.subheader("Punto seleccionado")

if resultado_mapa and resultado_mapa.get("last_clicked"):

    lat = resultado_mapa["last_clicked"]["lat"]
    lon = resultado_mapa["last_clicked"]["lng"]
    st.subheader("Resultado de la consulta espacial")

    try:
        query_response = requests.get(
            f"{API_URL}/api/recortes/query",
            params={
                "lat": lat,
                "lon": lon
            },
            timeout=10
        )

        query_response.raise_for_status()
        resultado = query_response.json()

        if resultado["inside"]:

            st.success(
                f"El punto se encuentra dentro de "
                f"{resultado['total_matches']} recorte(s)."
            )

            for recorte in resultado["recortes"]:

                st.write(
                    f"**Recorte:** {recorte['recorte']}"
                )

                st.write(
                    f"Área del recorte: "
                    f"{recorte['area_m2'] / 1_000_000:.3f} km²"
                )

                st.write(
                    f"Resolución espacial: "
                    f"{recorte['resolution_x']:.3f} × "
                    f"{recorte['resolution_y']:.3f} m"
                )

        else:

            st.warning(
                "El punto seleccionado está fuera de los "
                "27 recortes analizados."
            )

    except requests.RequestException as error:

        st.error(
            "No fue posible realizar la consulta espacial."
        )

        st.exception(error)

    st.subheader("Anomalías espectrales")

    try:
        candidate_response = requests.get(
            f"{API_URL}/api/candidates/query",
            params={
                "lat": lat,
                "lon": lon
            },
            timeout=10
        )

        candidate_response.raise_for_status()
        candidate_result = candidate_response.json()

        if candidate_result["intersects_candidate"]:

            st.success(
                f"El punto intersecta "
                f"{candidate_result['total_matches']} "
                f"zona(s) candidata(s)."
            )

            for candidate in candidate_result["candidates"]:

                with st.expander(
                    f"{candidate['candidate_id']} — "
                    f"{candidate['recorte']}",
                    expanded=True
                ):

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Área",
                            f"{candidate['area_m2']:.2f} m²"
                        )

                    with col2:
                        st.metric(
                            "Celdas",
                            candidate["n_cells"]
                        )

                    with col3:
                        st.metric(
                            "Score medio",
                            f"{candidate['score_mean']:.3f}"
                        )

                    st.write(
                        f"**Zone ID:** {candidate['zone_id']}"
                    )

                    st.write(
                        f"**Score máximo:** "
                        f"{candidate['score_max']:.3f}"
                    )

                    st.write(
                        f"**NDVI mediano:** "
                        f"{candidate['ndvi_median_zone']:.3f}"
                    )

                    st.write(
                        f"**IQR NDVI:** "
                        f"{candidate['ndvi_iqr_zone']:.3f}"
                    )

                    st.write(
                        f"**IQR NDWI:** "
                        f"{candidate['ndwi_iqr_zone']:.3f}"
                    )

                    st.write(
                        "**Núcleo estricto (2.5 %):** "
                        + (
                            "Sí"
                            if candidate["has_strict_core"]
                            else "No"
                        )
                    )

                    st.write(
                        f"**Fracción del área en núcleo:** "
                        f"{candidate['core_fraction_area']:.1%}"
                    )

            st.info(
                "La zona corresponde a una anomalía espectral "
                "superficial identificada mediante Isolation Forest. "
                "Su presencia no constituye por sí sola evidencia "
                "de un recurso geotérmico."
            )

        else:

            st.info(
                "El punto seleccionado no intersecta una zona "
                "candidata de anomalía espectral."
            )

    except requests.RequestException as error:

        st.error(
            "No fue posible consultar las zonas candidatas."
        )

        st.exception(error)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Latitud",
            f"{lat:.6f}"
        )

    with col2:
        st.metric(
            "Longitud",
            f"{lon:.6f}"
        )

else:

    st.info(
        "Haz clic sobre cualquier punto del mapa para "
        "seleccionar una ubicación."
    )