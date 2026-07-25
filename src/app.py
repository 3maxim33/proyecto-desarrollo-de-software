from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from explore_exoplanets import CSV_PATH, available_plot_columns, load_catalog

ROOT = Path(__file__).resolve().parent

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

# Configuración inicial de la página
st.set_page_config(
    page_title="Atlas de Exoplanetas",
    page_icon=".",
    layout="wide",
    initial_sidebar_state="expanded",
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

        /* Glassmorphism Cards */
        .section-card {
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 1.5rem;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
            margin-bottom: 1.5rem;
            transition: border 0.3s ease;
        }

        .section-card:hover {
            border: 1px solid var(--border-glow);
        }

        /* Hero Header */
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

        /* Metrics Customization */
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

        /* Sidebar Customization */
        [data-testid="stSidebar"] {
            background: rgba(9, 14, 23, 0.95) !important;
            border-right: 1px solid rgba(255,255,255,0.05);
        }

        hr {
            border-color: rgba(255,255,255,0.1);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def get_catalog() -> pd.DataFrame:
    return load_catalog()


def format_axis_label(column: str, labels: dict[str, str]) -> str:
    return labels.get(column, column)


def set_preset_state(preset_name: str) -> None:
    preset = PRESETS[preset_name]
    st.session_state["x_axis"] = preset["x"]
    st.session_state["y_axis"] = preset["y"]
    st.session_state["color_mode"] = preset["color"]
    st.session_state["log_x"] = preset["log_x"]
    st.session_state["log_y"] = preset["log_y"]


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
    columns = ["pl_name", "hostname", "discoverymethod", x, y]
    if color != "none":
        columns.append(color)
    if size_mode == "system":
        columns.append("system_planet_count")
    columns = list(dict.fromkeys(columns))

    plot_df = df[columns].dropna().copy()
    if log_x:
        plot_df = plot_df[plot_df[x] > 0]
    if log_y:
        plot_df = plot_df[plot_df[y] > 0]

    size = "system_planet_count" if size_mode == "system" else None
    color_arg = None if color == "none" else color
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
        hover_name="pl_name",
        hover_data=hover_data,
        color_continuous_scale="Viridis" if continuous else None,
        color_discrete_sequence=[
            "#38bdf8", "#c084fc", "#f472b6", "#fbbf24", "#34d399", "#f87171"
        ],
        opacity=0.85,
        height=650,
    )

    # Transparent background and glowing markers
    fig.update_traces(marker=dict(line=dict(width=0.5, color='rgba(255,255,255,0.2)')))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title_text="Atributo",
        legend=dict(bgcolor="rgba(15, 23, 42, 0.5)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1)
    )

    # Subtle gridlines
    grid_color = "rgba(255, 255, 255, 0.05)"
    fig.update_xaxes(type="log" if log_x else "linear", gridcolor=grid_color, zerolinecolor=grid_color)
    fig.update_yaxes(type="log" if log_y else "linear", gridcolor=grid_color, zerolinecolor=grid_color)

    return fig


def filter_catalog(
        df: pd.DataFrame,
        *,
        methods: list[str],
        planet_count_range: tuple[int, int],
        selected_hosts: list[str],
) -> pd.DataFrame:
    filtered = df[df["discoverymethod"].isin(methods)].copy()
    filtered = filtered[
        filtered["system_planet_count"].between(planet_count_range[0], planet_count_range[1])
    ]
    if selected_hosts:
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


def main() -> None:
    apply_theme()
    df = get_catalog()
    labels = available_plot_columns(df)
    default_methods = ["Transit", "Radial Velocity", "Microlensing", "Imaging"]

    if "preset" not in st.session_state:
        st.session_state["preset"] = "Masa vs semieje mayor"
    if "x_axis" not in st.session_state:
        set_preset_state(st.session_state["preset"])
    if "methods" not in st.session_state:
        st.session_state["methods"] = default_methods
    if "size_mode" not in st.session_state:
        st.session_state["size_mode"] = "fixed"

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

    render_overview(df)

    with st.sidebar:
        st.markdown("### Controles Principales")
        preset_name = st.selectbox(
            "Vistas Sugeridas",
            options=list(PRESETS.keys()),
            key="preset",
            on_change=lambda: set_preset_state(st.session_state["preset"]),
        )

        st.divider()
        st.markdown("### Filtros de Catálogo")
        methods = st.multiselect(
            "Método de Descubrimiento",
            options=sorted(df["discoverymethod"].dropna().unique().tolist()),
            key="methods",
            placeholder="Selecciona métodos...",
        )
        planet_count_range = st.slider(
            "Planetas por Sistema",
            min_value=int(df["system_planet_count"].min()),
            max_value=int(df["system_planet_count"].max()),
            value=(
                int(df["system_planet_count"].min()),
                int(df["system_planet_count"].max()),
            ),
        )

        st.divider()
        st.markdown("### Sistemas Específicos")
        host_options = sorted(df["hostname"].dropna().unique().tolist())
        host_query = st.text_input("Buscar estrella anfitriona", placeholder="Ej: TRAPPIST, Kepler...")

        matching_hosts = host_options
        if host_query:
            matching_hosts = [host for host in host_options if host_query.lower() in host.lower()][:120]
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
            format_func=lambda value: "Sin color" if value == "none" else (
                "Método" if value == "discoverymethod" else format_axis_label(value, labels)),
        )
        size_mode = st.radio(
            "Tamaño del Marcador",
            options=["fixed", "system"],
            key="size_mode",
            format_func=lambda value: "Fijo" if value == "fixed" else "Por multiplicidad del sistema",
        )

    if not methods:
        methods = default_methods
        st.sidebar.info("Restaurando métodos sugeridos por defecto.")

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
        with st.container(border=True):
            st.subheader(
                f"Diagrama Espacial: {format_axis_label(y_axis, labels)} vs {format_axis_label(x_axis, labels)}")
            st.caption(
                f"Mostrando **{len(filtered):,}** planetas en **{filtered['hostname'].nunique():,}** sistemas estelares.")

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
            st.plotly_chart(figure, use_container_width=True)

    with tab2:
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
                        metodos=("discoverymethod", lambda s: ", ".join(sorted(set(s)))),
                    )
                    .sort_values(["planetas", "hostname"], ascending=[False, True])
                    .head(15)
                    .reset_index()
                )
                st.dataframe(system_summary, use_container_width=True, hide_index=True)

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
                    margin=dict(l=10, r=20, t=10, b=20),
                    coloraxis_showscale=False,
                    yaxis_title="",
                    xaxis_title="Registros no nulos",
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)")
                )
                st.plotly_chart(bar, use_container_width=True)

        # SECCIÓN DE DRILL-DOWN CON FIX PARA NANS EN PLOTLY
        st.divider()
        st.subheader("Análisis de Sistema Específico")

        selected_top_system = st.selectbox(
            "Selecciona un sistema top para visualizar su arquitectura:",
            options=system_summary["hostname"].tolist(),
            help="Elige una estrella para ver las métricas y la distribución de sus planetas."
        )

        if selected_top_system:
            sys_df = filtered[filtered["hostname"] == selected_top_system].sort_values("pl_orbsmax", na_position='last')

            with st.container(border=True):
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Planetas Confirmados", len(sys_df))

                st_mass_val = sys_df["st_mass"].median()
                m2.metric("Masa Estelar (Soles)", f"{st_mass_val:.2f}" if pd.notna(st_mass_val) else "N/D")

                st_teff_val = sys_df["st_teff"].median()
                m3.metric("Temp. Estelar (K)", f"{st_teff_val:.0f}" if pd.notna(st_teff_val) else "N/D")

                if "sy_snum" in sys_df.columns:
                    stars = sys_df["sy_snum"].iloc[0]
                    m4.metric("Estrellas en el sistema", int(stars) if pd.notna(stars) else 1)
                else:
                    m4.metric("Método Principal", sys_df["discoverymethod"].mode()[0] if not sys_df.empty else "N/D")

                st.markdown(f"**Arquitectura Orbital de {selected_top_system}**")

                x_col = "pl_orbper" if sys_df["pl_orbper"].notna().any() else "pl_orbsmax"
                y_col = "pl_bmasse" if sys_df["pl_bmasse"].notna().any() else "pl_rade"

                # SOLUCIÓN: Copia de DataFrame y manejo de NaNs en columna de tamaño
                sys_df_plot = sys_df.copy()
                if sys_df_plot["pl_rade"].notna().any():
                    sys_df_plot["marker_size"] = sys_df_plot["pl_rade"].fillna(sys_df_plot["pl_rade"].median()).fillna(
                        1.0)
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
                    color_discrete_sequence=["#38bdf8", "#c084fc", "#f472b6", "#fbbf24", "#34d399", "#f87171"],
                    height=400
                )

                sys_fig.update_traces(
                    textposition='top center',
                    marker=dict(line=dict(width=1, color='rgba(255,255,255,0.5)'))
                )

                sys_fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#94a3b8"),
                    showlegend=False,
                    xaxis_title=x_title,
                    yaxis_title=y_title,
                    margin=dict(l=20, r=20, t=20, b=20)
                )

                sys_fig.update_xaxes(gridcolor="rgba(255, 255, 255, 0.05)", zerolinecolor="rgba(255, 255, 255, 0.05)")
                sys_fig.update_yaxes(gridcolor="rgba(255, 255, 255, 0.05)", zerolinecolor="rgba(255, 255, 255, 0.05)")

                st.plotly_chart(sys_fig, use_container_width=True)

                st.dataframe(
                    sys_df[["pl_name", "discoverymethod", "pl_orbsmax", "pl_orbper", "pl_bmasse", "pl_rade"]],
                    use_container_width=True,
                    hide_index=True
                )

    with tab3:
        with st.container(border=True):
            st.subheader("Catálogo de Datos Filtrados")
            visible_columns = [
                "pl_name", "hostname", "discoverymethod", "pl_orbsmax",
                "pl_orbper", "pl_rade", "pl_bmasse", "pl_orbeccen",
                "st_mass", "st_teff",
            ]
            st.dataframe(filtered[visible_columns], use_container_width=True, hide_index=True)

            st.download_button(
                "Descargar CSV Muestra",
                data=filtered.to_csv(index=False).encode("utf-8"),
                file_name="exoplanets_filtrados.csv",
                mime="text/csv",
                type="primary"
            )
            st.caption(f"Fuente de datos: `{CSV_PATH.name}`")


if __name__ == "__main__":
    main()