from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus
import json

import pandas as pd


# ============================================================
# NASA EXOPLANET ARCHIVE
# ============================================================

BASE_API_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
TAP_QUERY = "select * from ps where default_flag=1"
API_URL = f"{BASE_API_URL}?query={quote_plus(TAP_QUERY)}&format=csv"


# ============================================================
# RUTAS
# ============================================================

ROOT = Path(__file__).resolve().parent

OUTPUT_DIR = ROOT / "outputs"
CSV_PATH = OUTPUT_DIR / "exoplanets_ps_default.csv"
METADATA_PATH = OUTPUT_DIR / "metadata.json"


# ============================================================
# COLUMNAS
# ============================================================

KEY_COLUMNS = [
    "pl_name",
    "hostname",
    "pl_letter",
    "discoverymethod",
    "sy_pnum",
    "pl_orbsmax",
    "pl_orbper",
    "pl_rade",
    "pl_bmasse",
    "pl_orbeccen",
    "st_mass",
    "st_teff",
]

NUMERIC_COLUMNS = [
    "sy_pnum",
    "pl_orbsmax",
    "pl_orbper",
    "pl_rade",
    "pl_bmasse",
    "pl_orbeccen",
    "st_mass",
    "st_teff",
    "sy_snum",
]

PLOT_COLUMNS = {
    "pl_orbsmax": "Semieje mayor (AU)",
    "pl_orbper": "Período orbital (días)",
    "pl_rade": "Radio del planeta (radios terrestres)",
    "pl_bmasse": "Masa del planeta (masas terrestres)",
    "pl_orbeccen": "Excentricidad orbital",
    "st_mass": "Masa estelar (masas solares)",
    "st_teff": "Temperatura estelar (K)",
    "sy_pnum": "Planetas reportados en el sistema",
}


# ============================================================
# FUNCIONES
# ============================================================

def ensure_directories() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def clean_catalog(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    if "hostname" in df.columns and "pl_name" in df.columns:
        df["system_planet_count"] = df.groupby("hostname")["pl_name"].transform("count")

    if "pl_name" in df.columns:
        df["planet_suffix"] = df["pl_name"].astype(str).str.extract(
            r" ([b-z])$",
            expand=False,
        )

    return df


def save_csv_atomically(df: pd.DataFrame, path: Path) -> None:
    ensure_directories()

    temporary_path = path.with_suffix(".tmp.csv")
    df.to_csv(temporary_path, index=False, encoding="utf-8")
    temporary_path.replace(path)


def write_metadata(df: pd.DataFrame) -> None:
    ensure_directories()

    metadata = {
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "NASA Exoplanet Archive",
        "tap_query": TAP_QUERY,
        "api_url": API_URL,
        "csv_path": str(CSV_PATH),
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
    }

    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def read_metadata() -> dict:
    if not METADATA_PATH.exists():
        return {}

    try:
        return json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def available_plot_columns(df: pd.DataFrame) -> dict[str, str]:
    return {
        column: label
        for column, label in PLOT_COLUMNS.items()
        if column in df.columns and df[column].notna().any()
    }


def download_catalog() -> pd.DataFrame:
    """
    Descarga el catálogo actualizado desde NASA Exoplanet Archive,
    limpia tipos numéricos y reemplaza el CSV local.
    """
    ensure_directories()

    df = pd.read_csv(API_URL, low_memory=False)
    df = clean_catalog(df)

    save_csv_atomically(df, CSV_PATH)
    write_metadata(df)

    return df


def load_local_catalog() -> pd.DataFrame:
    """
    Carga el CSV local.
    """
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No existe el CSV local: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH, low_memory=False)
    df = clean_catalog(df)

    return df


def load_catalog(force_download: bool = False) -> pd.DataFrame:
    """
    Función usada por app.py.

    force_download=False:
        - carga el CSV local si existe;
        - si no existe, descarga el catálogo una vez.

    force_download=True:
        - descarga el catálogo actualizado desde NASA;
        - reemplaza outputs/exoplanets_ps_default.csv.

    Si la descarga falla, pero ya existe un CSV local, usa el CSV anterior.
    """
    ensure_directories()

    if force_download:
        try:
            return download_catalog()
        except Exception:
            if CSV_PATH.exists():
                return load_local_catalog()
            raise

    if CSV_PATH.exists():
        return load_local_catalog()

    return download_catalog()


if __name__ == "__main__":
    catalog = load_catalog(force_download=True)
    print(f"Catálogo actualizado: {len(catalog)} filas")
    print(f"CSV guardado en: {CSV_PATH}")