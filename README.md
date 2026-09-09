# Geotermal Platform

Sistema de apoyo a la priorización de anomalías superficiales para exploración geotérmica mediante análisis geoespacial, teledetección e integración de evidencias independientes.

## 1. Descripción

Geotermal Platform es una aplicación web desarrollada para consultar y visualizar los resultados de un proceso de detección y priorización de anomalías superficiales en la zona de estudio Paipa–Iza, Boyacá, Colombia.

El sistema integra resultados derivados de imágenes multiespectrales adquiridas mediante UAS con información geoespacial complementaria asociada a manifestaciones hidrotermales y estructuras geológicas.

La aplicación no identifica directamente recursos o reservorios geotérmicos. Las zonas mostradas corresponden a anomalías espectrales superficiales detectadas mediante aprendizaje no supervisado y posteriormente contextualizadas utilizando evidencia hidrotermal y estructural independiente.

## 2. Objetivo

Proporcionar una interfaz web interactiva que permita explorar espacialmente las anomalías espectrales detectadas y consultar su relación con diferentes fuentes de evidencia relevantes para la priorización de áreas de interés en exploración geotérmica.

## 3. Estado actual

Esta versión corresponde al **Módulo 1: Explorador Geoespacial Paipa–Iza**.

El módulo permite:

- visualizar los 27 recortes UAS utilizados en la síntesis final;
- visualizar 8.433 zonas candidatas de anomalía espectral;
- visualizar 21 manantiales hidrotermales;
- visualizar 91 geometrías de fallas geológicas;
- activar y desactivar capas desde la interfaz;
- filtrar las zonas candidatas según evidencia independiente;
- consultar espacialmente un punto mediante clic sobre el mapa;
- identificar los recortes que contienen el punto;
- identificar las zonas candidatas que intersectan el punto;
- consultar métricas asociadas a una zona candidata;
- identificar el manantial hidrotermal más cercano y su distancia;
- identificar la falla geológica más cercana y su distancia.

## 4. Metodología asociada

La detección inicial de anomalías se realizó independientemente de la información hidrotermal y estructural.

El flujo general fue:

```text
Imágenes multiespectrales UAS
            │
            ▼
Cálculo de índices espectrales
    NDVI / SAVI / NDWI
            │
            ▼
Unidades espaciales regulares
            │
            ▼
Características espectrales
            │
            ▼
     Isolation Forest
            │
            ▼
Sensibilidad de umbrales
  2.5 / 5 / 7.5 / 10 %
            │
            ▼
Consolidación espacial
            │
            ▼
8.433 zonas candidatas
            │
       ┌────┴────┐
       ▼         ▼
 Manantiales   Fallas
     SGC        SGC
       │         │
       ▼         ▼
 Evidencia H  Evidencia F
       └────┬────┘
            ▼
Convergencia de evidencias
```

Isolation Forest utilizó como variables finales:

- `ndvi_median`
- `ndvi_iqr`
- `ndwi_iqr`

Las zonas candidatas representan comportamientos espectrales superficiales atípicos y no constituyen, por sí mismas, evidencia de un recurso geotérmico.

## 5. Priorización mediante evidencia independiente

Después de detectar las anomalías espectrales se incorporaron fuentes de información independientes.

### Evidencia hidrotermal (H)

Se utilizaron 21 manantiales hidrotermales para evaluar la asociación espacial entre las anomalías y las manifestaciones hidrotermales.

Se identificaron seis recortes con evidencia hidrotermal robusta:

- IZA-7
- PAIPA-5
- PAIPA-10
- PAIPA-11
- PAIPA-14
- PAIPA-16

### Evidencia estructural (F)

Se utilizaron 91 geometrías de fallas geológicas y se evaluó la asociación espacial a diferentes escalas: 50 m, 100 m y 200 m.

Siete recortes presentaron evidencia estructural robusta en las tres escalas:

- IZA-15
- IZA-9
- PAIPA-10
- PAIPA-12
- PAIPA-16
- PAIPA-3
- PAIPA-6-2

### Convergencia H + F

La intersección de ambas evidencias identificó:

- PAIPA-10
- PAIPA-16

como los dos recortes con convergencia robusta de evidencia hidrotermal y estructural.

Estos dos recortes contienen 680 zonas candidatas:

| Recorte | Zonas candidatas |
|---|---:|
| PAIPA-10 | 203 |
| PAIPA-16 | 477 |
| **Total** | **680** |

Los 680 elementos no deben interpretarse como 680 zonas geotérmicas confirmadas. Son zonas candidatas de anomalía espectral pertenecientes a los dos recortes que presentaron convergencia robusta H + F.

## 6. Arquitectura tecnológica

La aplicación utiliza una arquitectura desacoplada:

```text
┌─────────────────────────────┐
│          Usuario            │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│          Streamlit          │
│          Frontend           │
│                             │
│  • Mapa interactivo         │
│  • Capas geográficas        │
│  • Filtros                  │
│  • Consulta por clic        │
└──────────────┬──────────────┘
               │ HTTP / JSON
               ▼
┌─────────────────────────────┐
│           FastAPI           │
│           Backend           │
│                             │
│  • API REST                 │
│  • Lógica espacial          │
│  • Validación de datos      │
│  • Consultas geográficas    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│     Servicios geoespaciales │
│                             │
│ spatial_service             │
│ candidate_service           │
│ evidence_service            │
│ spring_service              │
│ fault_service               │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       Datos geográficos     │
│                             │
│ GeoPackage / CSV            │
│ • Recortes                  │
│ • Candidatos                │
│ • Evidencias                │
│ • Manantiales               │
│ • Fallas                    │
└─────────────────────────────┘
```

## 7. Tecnologías

- Python 3.12
- FastAPI
- Streamlit
- GeoPandas
- Shapely
- Pyogrio
- Folium
- Streamlit-Folium
- Pandas
- Docker
- Docker Compose
- Git / GitHub

## 8. Estructura del proyecto

```text
geotermal_api/
│
├── backend/
│   ├── api/
│   ├── services/
│   │   ├── spatial_service.py
│   │   ├── candidate_service.py
│   │   ├── evidence_service.py
│   │   ├── spring_service.py
│   │   └── fault_service.py
│   ├── main.py
│   └── __init__.py
│
├── frontend/
│   ├── app.py
│   └── __init__.py
│
├── geothermal/
│   └── __init__.py
│
├── data/
│   ├── footprints/
│   │   └── recortes_27.gpkg
│   ├── candidate_zones/
│   │   └── candidate_zones.gpkg
│   ├── evidence/
│   │   └── evidence_summary.csv
│   ├── springs/
│   │   └── springs_sgc.gpkg
│   └── faults/
│       └── faults_sgc.gpkg
│
├── database/
├── models/
├── tests/
│
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md
```

## 9. Servicios del backend

El backend separa las responsabilidades mediante servicios especializados.

### `spatial_service.py`

Gestiona los 27 recortes de imágenes UAS:

- carga y validación;
- transformación de coordenadas;
- generación de GeoJSON;
- consulta de recortes por coordenada.

### `candidate_service.py`

Gestiona las 8.433 zonas candidatas:

- carga y validación;
- consulta punto-polígono;
- generación de GeoJSON;
- filtrado según evidencia;
- resumen de candidatos por filtro.

### `evidence_service.py`

Gestiona la clasificación de evidencia independiente de los 27 recortes:

- evidencia hidrotermal robusta;
- evidencia estructural robusta;
- convergencia H + F;
- clasificación general de evidencia.

### `spring_service.py`

Gestiona los 21 manantiales:

- carga y validación;
- visualización mediante GeoJSON;
- búsqueda del manantial más cercano;
- cálculo de distancia métrica.

### `fault_service.py`

Gestiona las 91 geometrías de fallas:

- carga y validación;
- visualización mediante GeoJSON;
- búsqueda de la falla más cercana;
- cálculo de distancia mínima punto–línea.

## 10. API REST

La documentación interactiva de la API se encuentra disponible durante la ejecución en:

```text
http://localhost:8000/docs
```

Principales endpoints:

```text
GET /health

GET /api/recortes/status
GET /api/recortes
GET /api/recortes/query

GET /api/candidates/status
GET /api/candidates
GET /api/candidates/query
GET /api/candidates/filter-summary

GET /api/evidence/status

GET /api/springs/status
GET /api/springs
GET /api/springs/nearest

GET /api/faults/status
GET /api/faults
GET /api/faults/nearest
```

## 11. Sistemas de referencia

Los datos destinados a cálculos métricos se manejan en:

```text
MAGNA-SIRGAS 2018 / Origen-Nacional
EPSG:9377
```

Para visualización web, las geometrías son transformadas por el backend a:

```text
WGS 84
EPSG:4326
```

Los datasets originales pueden proceder de otros CRS. La transformación se realiza durante la preparación o consulta de los datos según corresponda.

## 12. Ejecución con Docker

### Requisitos

- Git
- Docker Desktop
- Docker Compose
- WSL2 en Windows

Clonar el repositorio:

```bash
git clone <URL_DEL_REPOSITORIO>
cd geotermal_api
```

Construir e iniciar los servicios:

```bash
docker compose up --build
```

Una vez iniciados:

### Interfaz web

```text
http://localhost:8501
```

### API

```text
http://localhost:8000
```

### Swagger

```text
http://localhost:8000/docs
```

Para detener los contenedores:

```bash
docker compose down
```

## 13. Contenedores

La solución utiliza actualmente dos contenedores:

```text
geotermal-frontend
    │
    │ HTTP
    ▼
geotermal-backend
```

El frontend se comunica con el backend dentro de la red Docker mediante:

```text
http://backend:8000
```

Esto evita acoplar la interfaz directamente a los archivos geoespaciales y facilita una futura migración a infraestructura cloud.

## 14. Datos de gran tamaño

Los productos raster originales UAS no forman parte del repositorio Git.

Archivos como:

```text
*.tif
*.tiff
```

son excluidos mediante `.gitignore`.

La arquitectura está preparada para que estos productos puedan almacenarse posteriormente en servicios de almacenamiento de objetos, como Azure Blob Storage, sin incorporarlos directamente al repositorio ni a una base de datos relacional.

## 15. Limitaciones de la versión actual

Esta versión debe interpretarse como una herramienta de apoyo a la exploración superficial.

El sistema:

- no confirma la existencia de un reservorio geotérmico;
- no estima reservas geotérmicas;
- no determina profundidad del recurso;
- no sustituye estudios geológicos, geofísicos o geoquímicos;
- no utiliza manantiales o fallas como variables del Isolation Forest;
- no considera que la proximidad individual a una falla o manantial constituya automáticamente evidencia geotérmica.

Las fuentes hidrotermales y estructurales se utilizan como evidencias independientes para contextualización y priorización.


