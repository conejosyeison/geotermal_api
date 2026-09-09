from pathlib import Path

import pandas as pd


EVIDENCE_PATH = Path("/app/data/evidence/evidence_summary.csv")

EXPECTED_RECORTES = 27
EXPECTED_HYDROTHERMAL = 6
EXPECTED_STRUCTURAL = 7
EXPECTED_CONVERGENCE_HF = 2


def load_evidence():
    """
    Carga y valida la clasificación de evidencia independiente
    asociada a los 27 recortes UAS.
    """

    if not EVIDENCE_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {EVIDENCE_PATH}"
        )

    df = pd.read_csv(EVIDENCE_PATH)

    required_columns = [
        "recorte",
        "hydrothermal_robust",
        "structural_robust",
        "convergence_hf",
        "evidence_class",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Faltan columnas requeridas: {missing}"
        )

    # --------------------------------------------------------
    # Validaciones generales
    # --------------------------------------------------------

    if len(df) != EXPECTED_RECORTES:
        raise ValueError(
            f"Se encontraron {len(df)} recortes; "
            f"se esperaban {EXPECTED_RECORTES}."
        )

    if df["recorte"].duplicated().any():
        duplicates = df.loc[
            df["recorte"].duplicated(),
            "recorte"
        ].tolist()

        raise ValueError(
            f"Existen recortes duplicados: {duplicates}"
        )

    # --------------------------------------------------------
    # Normalizar booleanos
    # --------------------------------------------------------

    boolean_columns = [
        "hydrothermal_robust",
        "structural_robust",
        "convergence_hf",
    ]

    for column in boolean_columns:

        if df[column].dtype != bool:
            df[column] = (
                df[column]
                .astype(str)
                .str.strip()
                .str.lower()
                .map({
                    "true": True,
                    "false": False,
                })
            )

        if df[column].isna().any():
            raise ValueError(
                f"La columna {column} contiene valores "
                "booleanos no válidos."
            )

    # --------------------------------------------------------
    # Validaciones científicas
    # --------------------------------------------------------

    total_h = int(df["hydrothermal_robust"].sum())
    total_f = int(df["structural_robust"].sum())
    total_hf = int(df["convergence_hf"].sum())

    if total_h != EXPECTED_HYDROTHERMAL:
        raise ValueError(
            f"Se encontraron {total_h} recortes H robustos; "
            f"se esperaban {EXPECTED_HYDROTHERMAL}."
        )

    if total_f != EXPECTED_STRUCTURAL:
        raise ValueError(
            f"Se encontraron {total_f} recortes F robustos; "
            f"se esperaban {EXPECTED_STRUCTURAL}."
        )

    if total_hf != EXPECTED_CONVERGENCE_HF:
        raise ValueError(
            f"Se encontraron {total_hf} recortes H+F; "
            f"se esperaban {EXPECTED_CONVERGENCE_HF}."
        )

    # Todo H+F debe tener H=True y F=True
    invalid_hf = df[
        df["convergence_hf"]
        & ~(
            df["hydrothermal_robust"]
            & df["structural_robust"]
        )
    ]

    if not invalid_hf.empty:
        raise ValueError(
            "Existen recortes clasificados H+F sin "
            "evidencia H y F simultánea."
        )

    return df


def get_evidence_summary():
    """
    Retorna el resumen de evidencia independiente.
    """

    df = load_evidence()

    h = df[df["hydrothermal_robust"]]
    f = df[df["structural_robust"]]
    hf = df[df["convergence_hf"]]

    return {
        "status": "ok",
        "total_recortes": len(df),

        "hydrothermal_robust": {
            "total": len(h),
            "recortes": h["recorte"].tolist(),
        },

        "structural_robust": {
            "total": len(f),
            "recortes": f["recorte"].tolist(),
        },

        "convergence_hf": {
            "total": len(hf),
            "recortes": hf["recorte"].tolist(),
        },

        "classes": (
            df["evidence_class"]
            .value_counts()
            .to_dict()
        ),
    }