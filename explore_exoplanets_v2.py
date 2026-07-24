from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent
# URL directa de la API de la NASA para descargar el catálogo actualizado
API_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+*+from+ps+where+default_flag=1&format=csv"

OUTPUT_DIR = ROOT / "outputs"
PLOTS_DIR = OUTPUT_DIR / "plots"
SUMMARY_PATH = OUTPUT_DIR / "summary.md"

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

PLOT_COLUMNS = {
    "pl_orbsmax": "Semieje mayor (AU)",
    "pl_orbper": "Período orbital (días)",
    "pl_rade": "Radio del planeta (Tierras)",
    "pl_bmasse": "Masa del planeta (Tierras)",
    "pl_orbeccen": "Excentricidad orbital",
    "st_mass": "Masa estelar (soles)",
    "st_teff": "Temperatura estelar (K)",
    "sy_pnum": "Planetas reportados en el sistema",
}


def load_catalog() -> pd.DataFrame:
    print("Descargando catálogo desde NASA Exoplanet Archive (esto puede tomar unos segundos)...")
    df = pd.read_csv(API_URL, low_memory=False)

    numeric_columns = [
        "sy_pnum",
        "pl_orbsmax",
        "pl_orbper",
        "pl_rade",
        "pl_bmasse",
        "pl_orbeccen",
        "st_mass",
        "st_teff",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["system_planet_count"] = df.groupby("hostname")["pl_name"].transform("count")
    df["planet_suffix"] = df["pl_name"].str.extract(r" ([b-z])$", expand=False)

    print(f"Descarga completada: {len(df)} exoplanetas cargados.")
    return df


def available_plot_columns(df: pd.DataFrame) -> dict[str, str]:
    return {
        column: label
        for column, label in PLOT_COLUMNS.items()
        if column in df.columns and df[column].notna().any()
    }


def write_summary(df: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    PLOTS_DIR.mkdir(exist_ok=True)

    counts = df[KEY_COLUMNS].notna().sum().sort_values(ascending=False)
    top_methods = df["discoverymethod"].value_counts().head(8)
    top_systems = (
        df.groupby("hostname")
        .agg(
            planets=("pl_name", "count"),
            names=("pl_name", lambda s: ", ".join(s.head(8))),
        )
        .sort_values(["planets", "hostname"], ascending=[False, True])
        .head(10)
    )

    lines = [
        "# Resumen inicial del catálogo PS",
        "",
        f"- Filas: {len(df)}",
        f"- Columnas: {len(df.columns)}",
        "- Fuente: API TAP del NASA Exoplanet Archive con `default_flag = 1`.",
        "",
        "## Cobertura de columnas clave",
        "",
    ]
    lines.extend(
        f"- `{column}`: {int(value)} valores no nulos" for column, value in counts.items()
    )
    lines.extend(
        [
            "",
            "## Métodos de descubrimiento más frecuentes",
            "",
        ]
    )
    lines.extend(f"- `{method}`: {count}" for method, count in top_methods.items())
    lines.extend(
        [
            "",
            "## Sistemas con más planetas en la tabla",
            "",
        ]
    )
    lines.extend(
        f"- `{hostname}`: {int(row.planets)} planetas ({row.names})"
        for hostname, row in top_systems.iterrows()
    )

    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def scatter_plot(
        df: pd.DataFrame,
        *,
        x: str,
        y: str,
        color: str | None,
        title: str,
        filename: str,
        xscale: str = "log",
        yscale: str = "log",
) -> None:
    cols = [x, y] + ([color] if color else [])
    plot_df = df[cols].dropna().copy()
    plot_df = plot_df[(plot_df[x] > 0) & (plot_df[y] > 0)]

    plt.figure(figsize=(10, 7))
    sns.scatterplot(
        data=plot_df,
        x=x,
        y=y,
        hue=color,
        alpha=0.7,
        s=35,
        linewidth=0,
        palette="viridis" if color else None,
        legend="brief" if color else False,
    )
    plt.xscale(xscale)
    plt.yscale(yscale)
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / filename, dpi=180)
    plt.close()


def plot_method_comparison(df: pd.DataFrame) -> None:
    methods = ["Transit", "Radial Velocity", "Microlensing", "Imaging"]
    plot_df = df[
        df["discoverymethod"].isin(methods)
        & df["pl_orbsmax"].notna()
        & df["pl_bmasse"].notna()
        & (df["pl_orbsmax"] > 0)
        & (df["pl_bmasse"] > 0)
        ].copy()

    plt.figure(figsize=(10, 7))
    sns.scatterplot(
        data=plot_df,
        x="pl_orbsmax",
        y="pl_bmasse",
        hue="discoverymethod",
        alpha=0.75,
        s=40,
        linewidth=0,
    )
    plt.xscale("log")
    plt.yscale("log")
    plt.title("Masa vs semieje mayor por método de descubrimiento")
    plt.xlabel("pl_orbsmax")
    plt.ylabel("pl_bmasse")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "mass_vs_semimajor_by_method.png", dpi=180)
    plt.close()


def plot_multiplanet_histogram(df: pd.DataFrame) -> None:
    counts = (
        df.groupby("hostname")["pl_name"]
        .count()
        .rename("planet_count")
        .reset_index()
    )
    plt.figure(figsize=(9, 6))
    sns.histplot(counts, x="planet_count", discrete=True, binwidth=1, color="#1f77b4")
    plt.title("Cantidad de planetas por sistema")
    plt.xlabel("Planetas en el sistema")
    plt.ylabel("Número de sistemas")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "planets_per_system_histogram.png", dpi=180)
    plt.close()


def main() -> None:
    sns.set_theme(style="whitegrid")
    df = load_catalog()

    print("Generando resumen y gráficos...")
    write_summary(df)

    scatter_plot(
        df,
        x="pl_orbsmax",
        y="pl_bmasse",
        color=None,
        title="Masa del planeta vs semieje mayor",
        filename="mass_vs_semimajor.png",
    )
    scatter_plot(
        df,
        x="pl_orbsmax",
        y="pl_rade",
        color=None,
        title="Radio del planeta vs semieje mayor",
        filename="radius_vs_semimajor.png",
    )
    scatter_plot(
        df,
        x="pl_orbper",
        y="pl_orbsmax",
        color="pl_orbeccen",
        title="Período orbital vs semieje mayor (color = excentricidad)",
        filename="period_vs_semimajor_eccentricity.png",
        yscale="log",
    )
    scatter_plot(
        df,
        x="st_teff",
        y="pl_rade",
        color=None,
        title="Radio del planeta vs temperatura estelar",
        filename="radius_vs_stellar_temperature.png",
        xscale="log",
    )
    plot_method_comparison(df)
    plot_multiplanet_histogram(df)

    print(f"Resumen guardado en: {SUMMARY_PATH}")
    print(f"Gráficos guardados en: {PLOTS_DIR}")


if __name__ == "__main__":
    main()