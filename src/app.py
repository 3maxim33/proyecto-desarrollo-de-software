from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from explore_exoplanets import (
    CSV_PATH,
    METADATA_PATH,
    available_plot_columns,
    load_catalog,
    read_metadata,
)


ROOT = Path(__file__).resolve().parent

PLOTLY_CONFIG = {
    "responsive": True,
    "displaylogo": False,
    "scrollZoom": False,
}

PRESETS = {
    "Masa vs semieje mayor": {
        "x": "pl_orbsmax",
        "y": "pl_bmasse",
        "color": "discoverymethod",
        "log_x": True,
        "log_y": True,
    },
    "Radio vs semieje mayor": {
        "x": "pl_orbsmax",
        "y": "pl_rade",
        "color": "discoverymethod",
        "log_x": True,
        "log_y": True,
    },
    "Período vs semieje mayor": {
        "x": "pl_orbper",
        "y": "pl_orbsmax",
        "color": "pl_orbeccen",
        "log_x": True,
        "log_y": True,
    },
    "Radio vs temperatura estelar": {
        "x": "st_teff",
        "y": "pl_rade",
        "color": "st_mass",
        "log_x": False,
        "log_y": True,
    },
}


st.set_page_config(
    page_title="Atlas de Exoplanetas",
    page_icon=".",
    layout="wide",
    initial_sidebar_state="auto",
)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        :root {
            --bg-deep: #050b14;
            --bg-accent: #0b172a;
            --text-main: #e2e8f0;
            --text-muted: #94a3b8;
            --border-glow: rgba(56, 189, 248, 0.15);
            --neon-blue: #38bdf8;
            --neon-purple: #c084fc;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 15% 50%, rgba(56, 189, 248, 0.05), transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(192, 132, 252, 0.05), transparent 25%),
                linear-gradient(180deg, var(--bg-deep) 0%, #020617 100%);
            color: var(--text-main);
        }

        .hero {
            padding: 2.5rem;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.8) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }

        .hero::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, transparent, var(--neon-blue), var(--neon-purple), transparent);
        }

        .hero-kicker {
            color: var(--neon-blue);
            text-transform: uppercase;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.15em;
            margin-bottom: 0.5rem;
        }

        .hero h1 {
            color: #ffffff;
            font-weight: 700;
            margin-bottom: 0.5rem;
            font-size: 2.8rem;
        }

        .hero p {
            color: var(--text-muted);
            max-width: 800px;
            font-size: 1.1rem;
            line-height: 1.6;
        }

        [data-testid="stMetric"] {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 1.2rem;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        [data-testid="stMetricLabel"] p {
            color: var(--text-muted);
            font-weight: 600;
            font-size: 0.95rem;
        }

        [data-testid="stMetricValue"] {
            color: #ffffff;
            font-weight: 700;
        }

        [data-testid="stSidebar"] {
            background: rgba(9, 14, 23, 0.95) !important;
            border-right: 1px solid rgba(255,255,255,0.05);
        }

        hr {
            border-color: rgba(255,255,255,0.1);
        }

        /* =========================================================
           LAYOUT RESPONSIVE GENERAL
           ========================================================= */

        .block-container {
            max-width: 1600px;
            padding-top: 1.35rem;
            padding-bottom: 2rem;
            padding-left: clamp(1rem, 3vw, 3rem);
            padding-right: clamp(1rem, 3vw, 3rem);
        }

        [data-testid="stMainBlockContainer"] {
            width: 100%;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 18px;
        }

        [data-testid="stPlotlyChart"],
        [data-testid="stDataFrame"] {
            width: 100% !important;
            max-width: 100% !important;
        }

        [data-testid="stPlotlyChart"] > div,
        [data-testid="stPlotlyChart"] iframe {
            width: 100% !important;
            max-width: 100% !important;
        }

        /* Tabs desplazables en pantallas estrechas */
        [data-baseweb="tab-list"] {
            overflow-x: auto;
            overflow-y: hidden;
            scrollbar-width: thin;
            white-space: nowrap;
        }

        [data-baseweb="tab"] {
            flex-shrink: 0;
        }

        /* Evita cortes desagradables de texto */
        h1, h2, h3, p, label, [data-testid="stMetricLabel"] {
            overflow-wrap: anywhere;
        }

        /* =========================================================
           TABLET
           ========================================================= */

        @media (max-width: 1024px) {
            .block-container {
                padding-top: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .hero {
                padding: 1.8rem;
                border-radius: 20px;
                margin-bottom: 1.4rem;
            }

            .hero h1 {
                font-size: 2.2rem;
            }

            .hero p {
                font-size: 1rem;
            }
        }

        /* =========================================================
           CELULAR
           ========================================================= */

        @media (max-width: 768px) {
            .block-container {
                padding-top: 0.7rem;
                padding-bottom: 1.2rem;
                padding-left: 0.65rem;
                padding-right: 0.65rem;
            }

            .hero {
                padding: 1.25rem 1rem;
                border-radius: 16px;
                margin-bottom: 1rem;
                box-shadow: 0 10px 24px rgba(0,0,0,0.32);
            }

            .hero-kicker {
                font-size: 0.70rem;
                letter-spacing: 0.10em;
                line-height: 1.35;
            }

            .hero h1 {
                font-size: clamp(1.65rem, 8vw, 2rem);
                line-height: 1.12;
                margin-top: 0.25rem;
            }

            .hero p {
                font-size: 0.92rem;
                line-height: 1.45;
                margin-bottom: 0;
            }

            h1 {
                font-size: 1.75rem !important;
            }

            h2 {
                font-size: 1.35rem !important;
            }

            h3 {
                font-size: 1.12rem !important;
            }

            [data-testid="stMetric"] {
                padding: 0.85rem;
                border-radius: 13px;
                min-height: 92px;
            }

            [data-testid="stMetricLabel"] p {
                font-size: 0.78rem;
                line-height: 1.2;
            }

            [data-testid="stMetricValue"] {
                font-size: 1.25rem;
            }

            /* En móvil las columnas complejas se apilan verticalmente. */
            [data-testid="stHorizontalBlock"] {
                flex-wrap: wrap !important;
                gap: 0.65rem !important;
            }

            [data-testid="column"] {
                flex: 1 1 100% !important;
                width: 100% !important;
                min-width: 0 !important;
            }

            /* Controles grandes y fáciles de pulsar */
            .stButton > button,
            .stDownloadButton > button {
                width: 100% !important;
                min-height: 44px;
            }

            div[data-baseweb="select"],
            div[data-baseweb="input"] {
                width: 100% !important;
            }

            /* Tablas utilizables mediante desplazamiento horizontal. */
            [data-testid="stDataFrame"] {
                overflow-x: auto;
            }

            /* Reduce espacios verticales excesivos dentro de tarjetas. */
            [data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 14px;
            }
        }

        /* =========================================================
           CELULARES PEQUEÑOS
           ========================================================= */

        @media (max-width: 480px) {
            .block-container {
                padding-left: 0.45rem;
                padding-right: 0.45rem;
            }

            .hero {
                padding: 1rem 0.85rem;
            }

            .hero h1 {
                font-size: 1.55rem;
            }

            .hero p {
                font-size: 0.88rem;
            }

            [data-baseweb="tab"] {
                padding-left: 0.65rem !important;
                padding-right: 0.65rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner="Cargando catálogo de exoplanetas...")
def get_catalog() -> pd.DataFrame:
    return load_catalog(force_download=False)


def refresh_catalog() -> None:
    with st.spinner("Descargando catálogo actualizado desde NASA Exoplanet Archive..."):
        load_catalog(force_download=True)

    st.cache_data.clear()
    st.success("Catálogo actualizado correctamente.")
    st.rerun()


def format_axis_label(column: str, labels: dict[str, str]) -> str:
    return labels.get(column, column)


def set_preset_state(preset_name: str) -> None:
    preset = PRESETS[preset_name]
    st.session_state["x_axis"] = preset["x"]
    st.session_state["y_axis"] = preset["y"]
    st.session_state["color_mode"] = preset["color"]
    st.session_state["log_x"] = preset["log_x"]
    st.session_state["log_y"] = preset["log_y"]


def safe_mode_value(series: pd.Series) -> str:
    mode = series.dropna().mode()
    if mode.empty:
        return "N/D"
    return str(mode.iloc[0])


def build_scatter(
    df: pd.DataFrame,
    *,
    x: str,
    y: str,
    color: str,
    size_mode: str,
    log_x: bool,
    log_y: bool,
) -> px.scatter:
    required = ["pl_name", "hostname", "discoverymethod", x, y]

    if color != "none":
        required.append(color)

    if size_mode == "system":
        required.append("system_planet_count")

    columns = list(dict.fromkeys([column for column in required if column in df.columns]))

    plot_df = df[columns].dropna(subset=[x, y]).copy()

    if log_x:
        plot_df = plot_df[plot_df[x] > 0]

    if log_y:
        plot_df = plot_df[plot_df[y] > 0]

    if plot_df.empty:
        fig = px.scatter(pd.DataFrame({"x": [], "y": []}), x="x", y="y", height=560)
        fig.update_layout(
            title="No hay datos válidos para esta combinación de ejes y filtros.",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
        )
        return fig

    size = "system_planet_count" if size_mode == "system" and "system_planet_count" in plot_df.columns else None
    color_arg = None if color == "none" or color not in plot_df.columns else color
    continuous = color_arg in {"pl_orbeccen", "st_teff", "st_mass", "sy_pnum"}

    hover_data = {
        "hostname": True,
        "discoverymethod": True,
        x: ":.4g",
        y: ":.4g",
    }

    if size:
        hover_data["system_planet_count"] = True

    fig = px.scatter(
        plot_df,
        x=x,
        y=y,
        color=color_arg,
        size=size,
        hover_name="pl_name" if "pl_name" in plot_df.columns else None,
        hover_data=hover_data,
        color_continuous_scale="Viridis" if continuous else None,
        color_discrete_sequence=[
            "#38bdf8",
            "#c084fc",
            "#f472b6",
            "#fbbf24",
            "#34d399",
            "#f87171",
        ],
        opacity=0.85,
        height=560,
    )

    fig.update_traces(
        marker=dict(
            line=dict(width=0.5, color="rgba(255,255,255,0.2)")
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title_text="Atributo",
        autosize=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(15, 23, 42, 0.5)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
        ),
    )

    grid_color = "rgba(255, 255, 255, 0.05)"

    fig.update_xaxes(
        type="log" if log_x else "linear",
        gridcolor=grid_color,
        zerolinecolor=grid_color,
    )

    fig.update_yaxes(
        type="log" if log_y else "linear",
        gridcolor=grid_color,
        zerolinecolor=grid_color,
    )

    return fig


def filter_catalog(
    df: pd.DataFrame,
    *,
    methods: list[str],
    planet_count_range: tuple[int, int],
    selected_hosts: list[str],
) -> pd.DataFrame:
    filtered = df.copy()

    if methods and "discoverymethod" in filtered.columns:
        filtered = filtered[filtered["discoverymethod"].isin(methods)]

    if "system_planet_count" in filtered.columns:
        filtered = filtered[
            filtered["system_planet_count"].between(
                planet_count_range[0],
                planet_count_range[1],
            )
        ]

    if selected_hosts and "hostname" in filtered.columns:
        filtered = filtered[filtered["hostname"].isin(selected_hosts)]

    return filtered


def render_overview(df: pd.DataFrame) -> None:
    total_systems = df["hostname"].nunique()
    multi_systems = df.loc[df["system_planet_count"] > 1, "hostname"].nunique()

    with st.container(border=True):
        cols = st.columns(4)
        cols[0].metric("Planetas Confirmados", f"{len(df):,}".replace(",", "."))
        cols[1].metric("Sistemas Estelares", f"{total_systems:,}".replace(",", "."))
        cols[2].metric("Sistemas Múltiples", f"{multi_systems:,}".replace(",", "."))
        cols[3].metric("Métodos de Detección", df["discoverymethod"].nunique())


def render_sidebar(df: pd.DataFrame, labels: dict[str, str]) -> tuple[list[str], tuple[int, int], list[str], str, bool, str, bool, str, str]:
    default_methods = ["Transit", "Radial Velocity", "Microlensing", "Imaging"]

    with st.sidebar:
        st.markdown("### Datos")

        if st.button("Actualizar catálogo desde NASA", use_container_width=True):
            refresh_catalog()

        st.caption(f"CSV: `{CSV_PATH}`")

        metadata = read_metadata()
        downloaded_at = metadata.get("downloaded_at_utc")

        if downloaded_at:
            st.caption(f"Última descarga UTC: `{downloaded_at}`")

        if not CSV_PATH.exists():
            st.warning("No existe CSV local. Se descargará automáticamente al cargar.")

        st.divider()

        st.markdown("### Controles Principales")

        st.selectbox(
            "Vistas Sugeridas",
            options=list(PRESETS.keys()),
            key="preset",
            on_change=lambda: set_preset_state(st.session_state["preset"]),
        )

        st.divider()
        st.markdown("### Filtros de Catálogo")

        method_options = sorted(df["discoverymethod"].dropna().unique().tolist())

        methods = st.multiselect(
            "Método de Descubrimiento",
            options=method_options,
            key="methods",
            placeholder="Selecciona métodos...",
        )

        min_planets = int(df["system_planet_count"].min())
        max_planets = int(df["system_planet_count"].max())

        planet_count_range = st.slider(
            "Planetas por Sistema",
            min_value=min_planets,
            max_value=max_planets,
            value=(min_planets, max_planets),
        )

        st.divider()
        st.markdown("### Sistemas Específicos")

        host_options = sorted(df["hostname"].dropna().unique().tolist())
        host_query = st.text_input(
            "Buscar estrella anfitriona",
            placeholder="Ej: TRAPPIST, Kepler...",
        )

        matching_hosts = host_options
        if host_query:
            matching_hosts = [
                host for host in host_options
                if host_query.lower() in host.lower()
            ][:120]

        selected_hosts = st.multiselect(
            "Restringir a:",
            options=matching_hosts,
            placeholder="Todos los sistemas",
        )

        st.divider()
        st.markdown("### Configuración de Ejes")

        x_axis = st.selectbox(
            "Eje X",
            options=list(labels.keys()),
            key="x_axis",
            format_func=lambda column: format_axis_label(column, labels),
        )

        log_x = st.toggle("Logarítmico (X)", key="log_x")

        y_axis = st.selectbox(
            "Eje Y",
            options=list(labels.keys()),
            key="y_axis",
            format_func=lambda column: format_axis_label(column, labels),
        )

        log_y = st.toggle("Logarítmico (Y)", key="log_y")

        color_mode = st.selectbox(
            "Mapa de Color",
            options=["none", "discoverymethod", *labels.keys()],
            key="color_mode",
            format_func=lambda value: (
                "Sin color"
                if value == "none"
                else "Método"
                if value == "discoverymethod"
                else format_axis_label(value, labels)
            ),
        )

        size_mode = st.radio(
            "Tamaño del Marcador",
            options=["fixed", "system"],
            key="size_mode",
            format_func=lambda value: (
                "Fijo"
                if value == "fixed"
                else "Por multiplicidad del sistema"
            ),
        )

    if not methods:
        methods = default_methods
        st.sidebar.info("Restaurando métodos sugeridos por defecto.")

    return (
        methods,
        planet_count_range,
        selected_hosts,
        x_axis,
        log_x,
        y_axis,
        log_y,
        color_mode,
        size_mode,
    )


def render_visual_explorer(
    filtered: pd.DataFrame,
    labels: dict[str, str],
    *,
    x_axis: str,
    y_axis: str,
    color_mode: str,
    size_mode: str,
    log_x: bool,
    log_y: bool,
) -> None:
    with st.container(border=True):
        st.subheader(
            f"Diagrama espacial: {format_axis_label(y_axis, labels)} vs {format_axis_label(x_axis, labels)}"
        )

        st.caption(
            f"Mostrando **{len(filtered):,}** planetas en "
            f"**{filtered['hostname'].nunique():,}** sistemas estelares."
        )

        figure = build_scatter(
            filtered,
            x=x_axis,
            y=y_axis,
            color=color_mode,
            size_mode=size_mode,
            log_x=log_x,
            log_y=log_y,
        )

        figure.update_layout(
            xaxis_title=format_axis_label(x_axis, labels),
            yaxis_title=format_axis_label(y_axis, labels),
        )

        st.plotly_chart(figure, use_container_width=True, config=PLOTLY_CONFIG)


def render_top_systems(filtered: pd.DataFrame, labels: dict[str, str]) -> None:
    col1, col2 = st.columns([1.2, 1])

    with col1:
        with st.container(border=True):
            st.subheader("Sistemas Multiplanetarios Destacados")

            system_summary = (
                filtered.groupby("hostname")
                .agg(
                    planetas=("pl_name", "count"),
                    masa_estelar=("st_mass", "median"),
                    temp_estelar=("st_teff", "median"),
                    metodos=("discoverymethod", lambda s: ", ".join(sorted(set(s.dropna().astype(str))))),
                )
                .sort_values(["planetas", "hostname"], ascending=[False, True])
                .head(15)
                .reset_index()
            )

            st.dataframe(
                system_summary,
                use_container_width=True,
                hide_index=True,
            )

    with col2:
        with st.container(border=True):
            st.subheader("Integridad de Parámetros")

            completeness = (
                filtered[list(labels.keys())]
                .notna()
                .sum()
                .sort_values(ascending=True)
                .rename("valores")
                .reset_index()
                .rename(columns={"index": "parámetro"})
            )

            completeness["parámetro"] = completeness["parámetro"].map(labels)

            bar = px.bar(
                completeness,
                x="valores",
                y="parámetro",
                orientation="h",
                color="valores",
                color_continuous_scale="Purp",
                height=450,
            )

            bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"),
                autosize=True,
                margin=dict(l=10, r=20, t=10, b=20),
                coloraxis_showscale=False,
                yaxis_title="",
                xaxis_title="Registros no nulos",
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            )

            st.plotly_chart(bar, use_container_width=True, config=PLOTLY_CONFIG)

    st.divider()
    st.subheader("Análisis de Sistema Específico")

    if system_summary.empty:
        st.warning("No hay sistemas disponibles con los filtros actuales.")
        return

    selected_top_system = st.selectbox(
        "Selecciona un sistema top para visualizar su arquitectura:",
        options=system_summary["hostname"].tolist(),
        help="Elige una estrella para ver las métricas y la distribución de sus planetas.",
    )

    if not selected_top_system:
        return

    sys_df = (
        filtered[filtered["hostname"] == selected_top_system]
        .sort_values("pl_orbsmax", na_position="last")
        .copy()
    )

    with st.container(border=True):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Planetas Confirmados", len(sys_df))

        st_mass_val = sys_df["st_mass"].median()
        m2.metric(
            "Masa Estelar (Soles)",
            f"{st_mass_val:.2f}" if pd.notna(st_mass_val) else "N/D",
        )

        st_teff_val = sys_df["st_teff"].median()
        m3.metric(
            "Temp. Estelar (K)",
            f"{st_teff_val:.0f}" if pd.notna(st_teff_val) else "N/D",
        )

        if "sy_snum" in sys_df.columns:
            stars = sys_df["sy_snum"].iloc[0]
            m4.metric(
                "Estrellas en el sistema",
                int(stars) if pd.notna(stars) else 1,
            )
        else:
            m4.metric("Método Principal", safe_mode_value(sys_df["discoverymethod"]))

        st.markdown(f"**Arquitectura Orbital de {selected_top_system}**")

        x_col = "pl_orbper" if sys_df["pl_orbper"].notna().any() else "pl_orbsmax"
        y_col = "pl_bmasse" if sys_df["pl_bmasse"].notna().any() else "pl_rade"

        sys_df_plot = sys_df.dropna(subset=[x_col, y_col]).copy()
        sys_df_plot = sys_df_plot[(sys_df_plot[x_col] > 0) & (sys_df_plot[y_col] > 0)]

        if sys_df_plot.empty:
            st.warning("Este sistema no tiene datos positivos suficientes para graficar en escala logarítmica.")
        else:
            if sys_df_plot["pl_rade"].notna().any():
                sys_df_plot["marker_size"] = (
                    sys_df_plot["pl_rade"]
                    .fillna(sys_df_plot["pl_rade"].median())
                    .fillna(1.0)
                )
                size_col = "marker_size"
            else:
                size_col = None

            x_title = "Período Orbital (días)" if x_col == "pl_orbper" else "Semieje Mayor (UA)"
            y_title = "Masa (Masas Terrestres)" if y_col == "pl_bmasse" else "Radio (Radios Terrestres)"

            sys_fig = px.scatter(
                sys_df_plot,
                x=x_col,
                y=y_col,
                size=size_col,
                color="pl_name",
                text="pl_name",
                log_x=True,
                log_y=True,
                color_discrete_sequence=[
                    "#38bdf8",
                    "#c084fc",
                    "#f472b6",
                    "#fbbf24",
                    "#34d399",
                    "#f87171",
                ],
                height=400,
            )

            sys_fig.update_traces(
                textposition="top center",
                marker=dict(line=dict(width=1, color="rgba(255,255,255,0.5)")),
            )

            sys_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"),
                autosize=True,
                showlegend=False,
                xaxis_title=x_title,
                yaxis_title=y_title,
                margin=dict(l=20, r=20, t=20, b=20),
            )

            sys_fig.update_xaxes(
                gridcolor="rgba(255, 255, 255, 0.05)",
                zerolinecolor="rgba(255, 255, 255, 0.05)",
            )

            sys_fig.update_yaxes(
                gridcolor="rgba(255, 255, 255, 0.05)",
                zerolinecolor="rgba(255, 255, 255, 0.05)",
            )

            st.plotly_chart(sys_fig, use_container_width=True, config=PLOTLY_CONFIG)

        visible_sys_columns = [
            "pl_name",
            "discoverymethod",
            "pl_orbsmax",
            "pl_orbper",
            "pl_bmasse",
            "pl_rade",
        ]

        visible_sys_columns = [
            column for column in visible_sys_columns
            if column in sys_df.columns
        ]

        st.dataframe(
            sys_df[visible_sys_columns],
            use_container_width=True,
            hide_index=True,
        )


def render_csv_data(filtered: pd.DataFrame) -> None:
    with st.container(border=True):
        st.subheader("Catálogo de Datos Filtrados")

        visible_columns = [
            "pl_name",
            "hostname",
            "discoverymethod",
            "pl_orbsmax",
            "pl_orbper",
            "pl_rade",
            "pl_bmasse",
            "pl_orbeccen",
            "st_mass",
            "st_teff",
        ]

        visible_columns = [
            column for column in visible_columns
            if column in filtered.columns
        ]

        st.dataframe(
            filtered[visible_columns],
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Descargar CSV Muestra",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="exoplanets_filtrados.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True,
        )

        st.caption(f"Fuente de datos: `{CSV_PATH.name}`")


def initialize_session_state() -> None:
    default_methods = ["Transit", "Radial Velocity", "Microlensing", "Imaging"]

    if "preset" not in st.session_state:
        st.session_state["preset"] = "Masa vs semieje mayor"

    if "x_axis" not in st.session_state:
        set_preset_state(st.session_state["preset"])

    if "methods" not in st.session_state:
        st.session_state["methods"] = default_methods

    if "size_mode" not in st.session_state:
        st.session_state["size_mode"] = "fixed"


def validate_required_columns(df: pd.DataFrame) -> None:
    required_columns = [
        "pl_name",
        "hostname",
        "discoverymethod",
        "system_planet_count",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        st.error(f"Faltan columnas requeridas en el catálogo: {missing_columns}")
        st.stop()


def main() -> None:
    apply_theme()
    initialize_session_state()

    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">NASA Exoplanet Archive • Catálogo PS</div>
            <h1>Atlas de Exoplanetas</h1>
            <p>
                Explorador interactivo del catálogo confirmado de exoplanetas. Aplica filtros físicos
                y orbitales para analizar semieje mayor, período, masa, radio y propiedades estelares
                en busca de patrones de arquitectura planetaria.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        df = get_catalog()
    except Exception as error:
        st.error("No se pudo cargar el catálogo de exoplanetas.")
        st.exception(error)
        st.stop()

    validate_required_columns(df)

    labels = available_plot_columns(df)

    if not labels:
        st.error("No hay columnas numéricas disponibles para graficar.")
        st.stop()

    render_overview(df)

    (
        methods,
        planet_count_range,
        selected_hosts,
        x_axis,
        log_x,
        y_axis,
        log_y,
        color_mode,
        size_mode,
    ) = render_sidebar(df, labels)

    filtered = filter_catalog(
        df,
        methods=methods,
        planet_count_range=planet_count_range,
        selected_hosts=selected_hosts,
    )

    if filtered.empty:
        st.warning("Los filtros actuales excluyen todos los datos del catálogo.")
        return

    tab1, tab2, tab3 = st.tabs(["Explorador Visual", "Top Sistemas", "Datos CSV"])

    with tab1:
        render_visual_explorer(
            filtered,
            labels,
            x_axis=x_axis,
            y_axis=y_axis,
            color_mode=color_mode,
            size_mode=size_mode,
            log_x=log_x,
            log_y=log_y,
        )

    with tab2:
        render_top_systems(filtered, labels)

    with tab3:
        render_csv_data(filtered)


if __name__ == "__main__":
    main()