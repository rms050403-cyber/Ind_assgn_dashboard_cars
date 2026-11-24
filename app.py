import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ==============================================================================
# PAGE CONFIGURATION & GLOBAL STYLING
# ==============================================================================
st.set_page_config(
    page_title="Mexico Light-Vehicle Industry | RAIAVL Strategic Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Storytelling with Data Palette (Knaflic / Dr. Sabur Butt)
GREY       = "#A6A6A6"   # context data
LIGHT_GREY = "#D9D9D9"   # axes, faint elements
BG_SHADE   = "#EFEFEF"   # shock shading
TEXT_GREY  = "#6E6E6E"   # axis labels, subtitles, notes
DARK       = "#2B2B2B"   # headlines, primary text
BLUE       = "#1F5A96"   # primary strategic focus (SUVs / North America)
LIGHT_BLUE = "#9DC3E6"   # secondary positive highlight
ORANGE     = "#E46C0A"   # alert / tariff risk / contraction
TEAL       = "#2A7B76"   # diversification / Rest of World

SEGMENT_MAP = {
    "SUV's": "SUVs",
    "Compactos": "Compacts",
    "Pick Ups": "Pickups",
    "Subcompactos": "Subcompacts",
    "Minivans": "Minivans",
}

TIPO_MAP = {
    "Automóviles": "Passenger Cars",
    "Camiones ligeros": "Light Trucks (SUVs, Pickups & Minivans)",
}

COUNTRY_MAP = {
    "Estados Unidos": "United States",
    "Canadá": "Canada",
    "Alemania": "Germany",
    "Brasil": "Brazil",
    "Colombia": "Colombia",
    "Argentina": "Argentina",
    "Chile": "Chile",
    "China": "China",
    "Puerto Rico": "Puerto Rico",
    "Perú": "Peru",
    "Italia": "Italy",
    "Panamá": "Panama",
    "Guatemala": "Guatemala",
    "Uruguay": "Uruguay",
    "Costa Rica": "Costa Rica",
    "Ecuador": "Ecuador",
    "Curazao": "Curacao",
    "El Salvador": "El Salvador",
    "República Dominicana": "Dominican Republic",
    "Japón": "Japan",
    "Corea del Sur": "South Korea",
    "México": "Mexico",
    "No Especificado": "Unspecified",
}

MONTH_MAP = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12,
}

STATUS_MAP = {
    "Cifras Definitivas": "Definitive Figures",
    "Cifras Revisadas": "Revised Figures",
    "Cifras Preliminares": "Preliminary Figures",
}

# Custom CSS for clean executive typography and KPI cards
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2.5rem;
        max-width: 1380px;
    }
    .role-banner {
        background-color: #F4F7FA;
        border-left: 5px solid #1F5A96;
        padding: 1rem 1.25rem;
        border-radius: 6px;
        margin-bottom: 0.9rem;
    }
    .coverage-banner {
        background-color: #FFF8F1;
        border-left: 5px solid #E46C0A;
        padding: 0.85rem 1.2rem;
        border-radius: 6px;
        margin-bottom: 1.2rem;
        font-size: 0.92rem;
        color: #333333;
    }
    .insight-box {
        background-color: #F8F9FA;
        border-left: 4px solid #1F5A96;
        padding: 0.9rem 1.15rem;
        border-radius: 4px;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 0.95rem 1.1rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .kpi-label {
        font-size: 0.80rem;
        font-weight: 600;
        color: #6E6E6E;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 0.25rem;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1F5A96;
        line-height: 1.15;
    }
    .kpi-delta-pos {
        font-size: 0.83rem;
        font-weight: 600;
        color: #2A7B76;
        margin-top: 0.25rem;
    }
    .kpi-delta-neg {
        font-size: 0.83rem;
        font-weight: 600;
        color: #E46C0A;
        margin-top: 0.25rem;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: #7F7F7F;
        margin-top: 0.15rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# DATA LOADING, HARMONIZATION & EXACT DEDUPLICATION PIPELINE
# ==============================================================================
@st.cache_data
def load_and_clean_data(csv_path: str = "dataset_final_raiavl.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["MES_NUM"] = df["MES"].map(MONTH_MAP)
    df["DATE"] = pd.to_datetime(
        dict(year=df["ANIO"], month=df["MES_NUM"], day=1)
    )
    df["SEGMENT_EN"] = df["SEGMENTO"].map(SEGMENT_MAP).fillna(df["SEGMENTO"])
    df["TIPO_EN"] = df["TIPO"].map(TIPO_MAP).fillna(df["TIPO"])
    df["DEST_EN"] = df["PAIS_DESTINO"].map(COUNTRY_MAP).fillna(df["PAIS_DESTINO"])
    df["ORIGIN_COUNTRY_EN"] = (
        df["DESC_PAIS_ORIGEN"].map(COUNTRY_MAP).fillna(df["DESC_PAIS_ORIGEN"])
    )
    df["ORIGIN_TYPE_EN"] = np.where(
        df["ORIGEN"] == "NACIONAL",
        "Domestic (Made in Mexico)",
        "Imported Supplement",
    )
    df["STATUS_EN"] = df["ESTATUS"].map(STATUS_MAP).fillna(df["ESTATUS"])
    return df


def prepare_filtered_tables(
    df: pd.DataFrame,
    year_range: tuple[int, int],
    selected_segments: list[str],
    selected_brands: list[str],
    selected_dest_groups: list[str],
    harmonize_stellantis: bool,
):
    """
    Applies brand harmonization and deduplicates each RAIAVL metric at its exact
    structural grain so inner-join Cartesian expansion never inflates totals.
    """
    work = df.copy()
    if harmonize_stellantis:
        work["BRAND_CLEAN"] = work["MARCA"].replace(
            {"Chrysler": "Stellantis (Chrysler + Fiat)", "Fiat": "Stellantis (Chrysler + Fiat)"}
        )
    else:
        work["BRAND_CLEAN"] = work["MARCA"]

    # Map destination into analytical buckets for filtering
    top_countries = {"United States", "Canada", "Germany", "Brazil", "Colombia", "Argentina", "Chile"}
    work["DEST_BUCKET"] = np.where(
        work["DEST_EN"].isin(top_countries),
        work["DEST_EN"],
        "Other / Unspecified",
    )

    # Apply common filters
    mask = (
        work["ANIO"].between(year_range[0], year_range[1])
        & work["SEGMENT_EN"].isin(selected_segments)
        & work["BRAND_CLEAN"].isin(selected_brands)
    )
    sub = work[mask].copy()

    # Exact deduplication grains
    prod_keys = ["ANIO", "MES_NUM", "DATE", "BRAND_CLEAN", "MARCA", "MODELO", "TIPO_EN", "SEGMENT_EN"]
    sales_keys = prod_keys + ["ORIGIN_TYPE_EN", "ORIGIN_COUNTRY_EN"]
    exp_keys = prod_keys + ["DEST_EN", "DEST_BUCKET"]

    df_prod = sub.drop_duplicates(subset=prod_keys)[
        prod_keys + ["UNI_VEH_PRODUCCION", "STATUS_EN"]
    ].copy()

    df_sales = sub.drop_duplicates(subset=sales_keys)[
        sales_keys + ["UNI_VEH_VENTAS", "STATUS_EN"]
    ].copy()

    sub_exp = sub[sub["DEST_BUCKET"].isin(selected_dest_groups)].copy()
    df_exp = sub_exp.drop_duplicates(subset=exp_keys)[
        exp_keys + ["UNI_VEH_EXPORTACION", "STATUS_EN"]
    ].copy()

    return sub, df_prod, df_sales, df_exp


# ==============================================================================
# PLOTLY STORYTELLING HELPERS
# ==============================================================================
def style_plotly_story(
    fig: go.Figure,
    title: str,
    subtitle: str,
    y_title: str = "",
    x_title: str = "",
    height: int = 430,
    show_legend: bool = False,
) -> go.Figure:
    """Applies Knaflic/Butt decluttering, hierarchy, and action-title styling."""
    fig.update_layout(
        title=dict(
            text=(
                f"<span style='font-size:17px; font-weight:700; color:{DARK};'>{title}</span>"
                f"<br><span style='font-size:12.5px; font-weight:400; color:{TEXT_GREY};'>{subtitle}</span>"
            ),
            x=0.0,
            xanchor="left",
            y=0.96,
            yanchor="top",
        ),
        height=height,
        margin=dict(l=55, r=145, t=82, b=52),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, Helvetica, Arial, sans-serif", color=DARK, size=12),
        showlegend=show_legend,
        hovermode="x unified",
    )
    fig.update_xaxes(
        title=dict(text=x_title, font=dict(size=12, color=TEXT_GREY)),
        showgrid=False,
        linecolor=LIGHT_GREY,
        linewidth=1,
        tickfont=dict(color=TEXT_GREY, size=11),
        zeroline=False,
    )
    fig.update_yaxes(
        title=dict(text=y_title, font=dict(size=12, color=TEXT_GREY)),
        showgrid=False,
        linecolor=LIGHT_GREY,
        linewidth=1,
        tickfont=dict(color=TEXT_GREY, size=11),
        rangemode="tozero",
        zeroline=True,
        zerolinecolor=LIGHT_GREY,
        zerolinewidth=1,
    )
    return fig


# ==============================================================================
# MAIN APPLICATION
# ==============================================================================
def main():
    if not os.path.exists("dataset_final_raiavl.csv"):
        st.error("File `dataset_final_raiavl.csv` not found in the working directory.")
        st.stop()

    raw_df = load_and_clean_data("dataset_final_raiavl.csv")

    # --------------------------------------------------------------------------
    # SIDEBAR: INTERACTIVE CONTROLS & COVERAGE METADATA
    # --------------------------------------------------------------------------
    st.sidebar.markdown("## 🎛️ Analytical Controls")
    st.sidebar.caption("Filter across all 22 years of INEGI RAIAVL records (2005–Oct 2026).")

    min_yr, max_yr = int(raw_df["ANIO"].min()), int(raw_df["ANIO"].max())
    year_range = st.sidebar.slider(
        "Time Window (Years)",
        min_value=min_yr,
        max_value=max_yr,
        value=(2005, 2026),
        step=1,
    )

    harmonize_stellantis = st.sidebar.checkbox(
        "Harmonize Stellantis (Chrysler + Fiat)",
        value=True,
        help="Consolidates Chrysler (2005–2026) and Fiat (2011–2019) into Stellantis to reflect the 2021 corporate merger.",
    )

    all_segments = ["SUVs", "Compacts", "Pickups", "Subcompacts", "Minivans"]
    selected_segments = st.sidebar.multiselect(
        "Vehicle Segment",
        options=all_segments,
        default=all_segments,
    )

    temp_brands = (
        raw_df["MARCA"]
        .replace({"Chrysler": "Stellantis (Chrysler + Fiat)", "Fiat": "Stellantis (Chrysler + Fiat)"})
        .unique()
        if harmonize_stellantis
        else raw_df["MARCA"].unique()
    )
    all_brands = sorted(temp_brands.tolist())
    selected_brands = st.sidebar.multiselect(
        "Automaker (AMIA Registry)",
        options=all_brands,
        default=all_brands,
    )

    dest_options = [
        "United States", "Canada", "Germany", "Brazil",
        "Colombia", "Argentina", "Chile", "China", "Other / Unspecified",
    ]
    selected_dest_groups = st.sidebar.multiselect(
        "Export Destination Market",
        options=dest_options,
        default=dest_options,
    )

    time_mode = st.sidebar.radio(
        "Temporal Aggregation Mode",
        options=[
            "Annual + 2026 Jan–Oct YTD Pace",
            "Monthly 12-Month Rolling Total",
        ],
        index=0,
        help="Accounts for seasonality and partial-year 2026 coverage (Jan–Oct).",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"""
        <div style="font-size:0.82rem; color:{TEXT_GREY}; line-height:1.45;">
        <b>Data Vintage & Coverage Note</b><br>
        • <b>Source:</b> INEGI RAIAVL (Production, Exports & Domestic Sales merged on locally assembled model lines).<br>
        • <b>2026 Coverage:</b> Jan–Oct 2026 (10 months). Oct 2026 is <i>Preliminary</i>; Jan–Sep 2026 is <i>Revised</i>.<br>
        • <b>Panel Scope:</b> Non-reporting import brands (e.g., BYD, MG, Chirey) and post-2009 Renault imports are outside this local-assembly panel.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not selected_segments or not selected_brands or not selected_dest_groups:
        st.warning("Please select at least one Segment, Automaker, and Export Destination in the sidebar.")
        st.stop()

    sub_raw, df_prod, df_sales, df_exp = prepare_filtered_tables(
        raw_df,
        year_range=year_range,
        selected_segments=selected_segments,
        selected_brands=selected_brands,
        selected_dest_groups=selected_dest_groups,
        harmonize_stellantis=harmonize_stellantis,
    )

    # --------------------------------------------------------------------------
    # HEADER & STAKEHOLDER CONTEXT
    # --------------------------------------------------------------------------
    st.markdown(
        f"""
        <h1 style="margin-bottom:0.15rem; color:{DARK}; font-size:2.05rem;">
        Mexico's Light-Vehicle Industry: Structural Pivot & Trade Exposure (2005–2026)
        </h1>
        <p style="color:{TEXT_GREY}; font-size:1.02rem; margin-bottom:0.85rem;">
        An interactive strategic intelligence dashboard built on INEGI's <i>Registro Administrativo de la Industria Automotriz de Vehículos Ligeros (RAIAVL)</i>
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="role-banner">
        <b>Role & Stakeholder Context:</b> Prepared from the perspective of a <b>Senior Industrial & Trade Strategy Analyst at Mexico's Ministry of Economy (Secretaría de Economía)</b> advising the <b>Undersecretary of Industry & Commerce</b> ahead of the <b>2026 USMCA Review</b>.<br>
        <b>Core Strategic Decision:</b> How should Mexico calibrate industrial incentives, trade diversification, and supplier localization to protect its 3+ million-unit manufacturing base against U.S. tariff shocks and high export concentration?
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="coverage-banner">
        <b>⚠️ On-Screen Data Coverage & Methodological Transparency:</b>
        (1) <b>2026 Partial-Year Coverage:</b> Dataset runs through <b>October 2026</b> (Oct 2026 = <i>Preliminary Figures</i>; 2024–Sep 2026 = <i>Revised Figures</i>; 2005–2023 = <i>Definitive Figures</i>). All 2026 comparisons use <b>Jan–Oct Year-to-Date (YTD)</b> or <b>12-Month Rolling Totals</b> to prevent false seasonal drops.
        (2) <b>Panel Scope:</b> Covers domestically assembled model lines across Production, Exports, and Domestic Retail Sales; import-only brands without Mexican assembly (e.g., BYD, MG, Chirey) do not report to RAIAVL's production table.
        (3) <b>Pickup Reporting Lag:</b> Heavy-duty pickups (GM Silverado 2500 / GMC Sierra, Stellantis RAM 2500) record exports from inventory/model-code splits in 2025–2026 while reporting zero new production rows.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------------------------
    # TOP-LINE DYNAMIC KPI CARDS (WINDOW-AWARE + JAN-OCT YTD SEASONALITY CONTROL)
    # --------------------------------------------------------------------------
    months_26 = sorted(df_prod[df_prod["ANIO"] == 2026]["MES_NUM"].unique().tolist())
    if not months_26:
        months_26 = list(range(1, 11))

    anchor_yr = min(year_range[1], 2025) if year_range[0] <= 2025 else 2026
    start_yr = year_range[0]
    has_ytd_comp = (2026 in range(year_range[0], year_range[1] + 1)) and (2025 in range(year_range[0], year_range[1] + 1))

    prod_anchor = df_prod[df_prod["ANIO"] == anchor_yr]["UNI_VEH_PRODUCCION"].sum()
    prod_25_ytd = df_prod[(df_prod["ANIO"] == 2025) & (df_prod["MES_NUM"].isin(months_26))]["UNI_VEH_PRODUCCION"].sum()
    prod_26_ytd = df_prod[(df_prod["ANIO"] == 2026) & (df_prod["MES_NUM"].isin(months_26))]["UNI_VEH_PRODUCCION"].sum()
    prod_yoy = ((prod_26_ytd - prod_25_ytd) / prod_25_ytd * 100) if prod_25_ytd > 0 else 0.0

    exp_anchor = df_exp[df_exp["ANIO"] == anchor_yr]["UNI_VEH_EXPORTACION"].sum()
    exp_25_ytd = df_exp[(df_exp["ANIO"] == 2025) & (df_exp["MES_NUM"].isin(months_26))]["UNI_VEH_EXPORTACION"].sum()
    exp_26_ytd = df_exp[(df_exp["ANIO"] == 2026) & (df_exp["MES_NUM"].isin(months_26))]["UNI_VEH_EXPORTACION"].sum()
    exp_yoy = ((exp_26_ytd - exp_25_ytd) / exp_25_ytd * 100) if exp_25_ytd > 0 else 0.0
    export_ratio_anchor = (exp_anchor / prod_anchor * 100) if prod_anchor > 0 else 0.0

    us_exp_anchor = df_exp[(df_exp["ANIO"] == anchor_yr) & (df_exp["DEST_EN"] == "United States")]["UNI_VEH_EXPORTACION"].sum()
    us_share_anchor = (us_exp_anchor / exp_anchor * 100) if exp_anchor > 0 else 0.0
    us_25_ytd = df_exp[(df_exp["ANIO"] == 2025) & (df_exp["MES_NUM"].isin(months_26)) & (df_exp["DEST_EN"] == "United States")]["UNI_VEH_EXPORTACION"].sum()
    us_26_ytd = df_exp[(df_exp["ANIO"] == 2026) & (df_exp["MES_NUM"].isin(months_26)) & (df_exp["DEST_EN"] == "United States")]["UNI_VEH_EXPORTACION"].sum()
    us_yoy = ((us_26_ytd - us_25_ytd) / us_25_ytd * 100) if us_25_ytd > 0 else 0.0

    lt_anchor = df_prod[(df_prod["ANIO"] == anchor_yr) & (df_prod["SEGMENT_EN"].isin(["SUVs", "Pickups", "Minivans"]))]["UNI_VEH_PRODUCCION"].sum()
    lt_share_anchor = (lt_anchor / prod_anchor * 100) if prod_anchor > 0 else 0.0
    lt_start = df_prod[(df_prod["ANIO"] == start_yr) & (df_prod["SEGMENT_EN"].isin(["SUVs", "Pickups", "Minivans"]))]["UNI_VEH_PRODUCCION"].sum()
    prod_start = df_prod[df_prod["ANIO"] == start_yr]["UNI_VEH_PRODUCCION"].sum()
    lt_share_start = (lt_start / prod_start * 100) if prod_start > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        delta_cls = "kpi-delta-pos" if prod_yoy >= 0 else "kpi-delta-neg"
        delta_txt = (
            f"{prod_yoy:+.1f}% Jan–Oct 2026 YoY ({prod_26_ytd/1e6:.2f}M YTD)"
            if has_ytd_comp
            else f"Window total: {df_prod['UNI_VEH_PRODUCCION'].sum()/1e6:.2f}M units ({start_yr}–{year_range[1]})"
        )
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{anchor_yr} Assembly Output</div>
                <div class="kpi-value">{prod_anchor/1e6:.2f}M</div>
                <div class="{delta_cls}">{delta_txt}</div>
                <div class="kpi-sub">Filtered selection · {anchor_yr} anchor year</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        delta_cls = "kpi-delta-pos" if exp_yoy >= 0 else "kpi-delta-neg"
        delta_txt = (
            f"{exp_yoy:+.1f}% Jan–Oct 2026 Exports YoY"
            if has_ytd_comp
            else f"Window exports: {df_exp['UNI_VEH_EXPORTACION'].sum()/1e6:.2f}M units"
        )
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Export Dependence ({anchor_yr})</div>
                <div class="kpi-value">{export_ratio_anchor:.1f}%</div>
                <div class="{delta_cls}">{delta_txt}</div>
                <div class="kpi-sub">{exp_anchor/1e6:.2f}M units shipped abroad in {anchor_yr}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        delta_cls = "kpi-delta-pos" if us_yoy >= 0 else "kpi-delta-neg"
        delta_txt = (
            f"{us_yoy:+.1f}% U.S. Shipments YoY (Jan–Oct 2026)"
            if has_ytd_comp
            else f"{us_exp_anchor/1e6:.2f}M units shipped to U.S. in {anchor_yr}"
        )
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">U.S. Export Concentration</div>
                <div class="kpi-value">{us_share_anchor:.1f}%</div>
                <div class="{delta_cls}">{delta_txt}</div>
                <div class="kpi-sub">Single-market exposure across NAFTA/USMCA</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        pp_diff = lt_share_anchor - lt_share_start
        delta_cls = "kpi-delta-pos" if pp_diff >= 0 else "kpi-delta-neg"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Light-Truck & SUV Mix ({anchor_yr})</div>
                <div class="kpi-value">{lt_share_anchor:.1f}%</div>
                <div class="{delta_cls}">{pp_diff:+.1f} pp vs. {start_yr} ({lt_share_start:.1f}%)</div>
                <div class="kpi-sub">Light trucks vs. passenger cars in assembly</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # NARRATIVE CHAPTER TABS (COVERING THE ENTIRE DATASET)
    # --------------------------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1 · Production Pivot (Segments & Shocks)",
        "2 · Trade & U.S. Tariff Exposure",
        "3 · Domestic Market vs. Exports",
        "4 · Automakers & Top Models",
        "5 · Data Governance & Policy Brief",
    ])

    # ==========================================================================
    # TAB 1: PRODUCTION TRANSFORMATION & SHOCKS
    # ==========================================================================
    with tab1:
        st.markdown(
            """
            <div class="insight-box">
            <b>Chapter 1 Takeaway — Structural Re-engineering of Mexican Plants:</b> Between 2005 and 2025, Mexico transformed from a small-car assembly hub (61.6% Compacts in 2005) into a specialized <b>SUV and Light-Truck powerhouse</b>. SUVs overtook Compacts in <b>2018</b> and multiplied <b>27-fold</b> by 2025. However, the <b>January 2026 U.S. tariff shock</b> reversed momentum, pushing Jan–Oct 2026 SUV assembly down <b>-7.4% YoY</b> and Compacts down <b>-16.1% YoY</b>.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if time_mode == "Annual + 2026 Jan–Oct YTD Pace":
            piv_yr = df_prod.pivot_table(
                index="ANIO", columns="SEGMENT_EN", values="UNI_VEH_PRODUCCION",
                aggfunc="sum", fill_value=0
            ).sort_index()

            piv_full = piv_yr[piv_yr.index <= 2025].copy()
            has_2026 = (2026 in piv_yr.index) and (len(months_26) > 0)

            fig1 = go.Figure()

            # Shock shading bands
            if year_range[0] <= 2009 and year_range[1] >= 2008:
                fig1.add_vrect(
                    x0=2008.0, x1=2009.4, fillcolor=BG_SHADE, opacity=0.65, line_width=0,
                    annotation_text="2008–09 Global<br>Financial Crisis",
                    annotation_position="top left",
                    annotation_font=dict(size=10, color=TEXT_GREY),
                )
            if year_range[0] <= 2022 and year_range[1] >= 2020:
                fig1.add_vrect(
                    x0=2019.7, x1=2022.3, fillcolor=BG_SHADE, opacity=0.75, line_width=0,
                    annotation_text="COVID-19 (2020) &<br>Chip Shortage (2021–22)",
                    annotation_position="top left",
                    annotation_font=dict(size=10.5, color=DARK),
                )

            seg_order = [s for s in ["SUVs", "Compacts", "Pickups", "Subcompacts", "Minivans"] if s in piv_full.columns]

            for seg in seg_order:
                if seg == "Minivans" and piv_full[seg].sum() == 0:
                    continue
                is_suv = (seg == "SUVs")
                is_comp = (seg == "Compacts")
                color = BLUE if is_suv else (DARK if is_comp else GREY)
                width = 3.8 if is_suv else (2.4 if is_comp else 1.8)

                fig1.add_trace(
                    go.Scatter(
                        x=piv_full.index,
                        y=piv_full[seg],
                        mode="lines+markers" if is_suv else "lines",
                        name=seg,
                        line=dict(color=color, width=width),
                        marker=dict(size=6, color=color),
                        hovertemplate=f"<b>{seg}</b><br>Year: %{{x}}<br>Units: %{{y:,.0f}}<extra></extra>",
                    )
                )

                # 2026 annualized pace (dashed alert segment from 2025 -> 2026)
                if has_2026 and (2025 in piv_full.index):
                    pace_26 = piv_yr.loc[2026, seg] * (12.0 / len(months_26))
                    val_25 = piv_full.loc[2025, seg]
                    ytd_25 = df_prod[(df_prod["ANIO"] == 2025) & (df_prod["MES_NUM"].isin(months_26)) & (df_prod["SEGMENT_EN"] == seg)]["UNI_VEH_PRODUCCION"].sum()
                    ytd_26 = piv_yr.loc[2026, seg]
                    yoy_seg = ((ytd_26 - ytd_25) / ytd_25 * 100) if ytd_25 > 0 else 0.0

                    line_col = ORANGE if seg in ["SUVs", "Compacts"] else GREY
                    fig1.add_trace(
                        go.Scatter(
                            x=[2025, 2026],
                            y=[val_25, pace_26],
                            mode="lines+markers",
                            name=f"{seg} (2026 Pace)",
                            line=dict(color=line_col, width=width, dash="dash"),
                            marker=dict(size=7, color=line_col),
                            hovertemplate=(
                                f"<b>{seg} (2026 Annualized Pace)</b><br>"
                                f"Jan–Oct 2026 Actual: {ytd_26:,.0f} ({yoy_seg:+.1f}% YoY)<br>"
                                f"Annualized Run-Rate: %{{y:,.0f}}<extra></extra>"
                            ),
                        )
                    )
                    # Direct end-of-line label
                    fig1.add_annotation(
                        x=2026.12,
                        y=pace_26,
                        text=f"<b>{seg}</b> ({yoy_seg:+.1f}% YTD)" if is_suv else f"{seg} ({yoy_seg:+.1f}%)",
                        showarrow=False,
                        xanchor="left",
                        font=dict(
                            size=11.5 if is_suv else 10.5,
                            color=ORANGE if is_suv else TEXT_GREY,
                        ),
                    )
                elif len(piv_full) > 0:
                    last_yr = piv_full.index[-1]
                    last_val = piv_full.loc[last_yr, seg]
                    fig1.add_annotation(
                        x=last_yr + 0.12,
                        y=last_val,
                        text=f"<b>{seg}</b> ({last_val/1e6:.2f}M)" if is_suv else f"{seg} ({last_val/1e6:.2f}M)",
                        showarrow=False,
                        xanchor="left",
                        font=dict(size=11, color=color),
                    )

            # Event callouts on Chart 1
            if "SUVs" in piv_full.columns and 2018 in piv_full.index:
                fig1.add_annotation(
                    x=2018,
                    y=piv_full.loc[2018, "SUVs"],
                    text="<b>2018 Crossover:</b><br>SUVs surpass Compacts",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor=BLUE,
                    ax=-55,
                    ay=-45,
                    font=dict(size=11, color=BLUE),
                )

            if has_2026:
                fig1.add_vline(x=2025.85, line_width=1.3, line_dash="dot", line_color=ORANGE)
                fig1.add_annotation(
                    x=2025.85,
                    y=piv_full.max().max() * 0.98 if len(piv_full) else 1.8e6,
                    text="<b>Jan 2026 Tariff Shock</b><br>U.S. trade friction hits output",
                    showarrow=False,
                    xanchor="right",
                    xshift=-8,
                    font=dict(size=10.5, color=ORANGE),
                )

            style_plotly_story(
                fig1,
                title="SUVs overtook Compacts in 2018 and grew 27x, but 2026 tariffs triggered a sharp pullback",
                subtitle="Annual light-vehicle assembly in Mexico by segment (2026 dashed line = Jan–Oct annualized run-rate)",
                y_title="Vehicles Assembled",
                height=460,
            )
            if has_2026:
                fig1.update_xaxes(range=[year_range[0] - 0.3, 2028.8])
            st.plotly_chart(fig1, use_container_width=True)

        else:
            # Monthly 12-Month Rolling Total mode
            monthly = (
                df_prod.groupby(["DATE", "ANIO", "MES_NUM", "SEGMENT_EN"])["UNI_VEH_PRODUCCION"]
                .sum()
                .reset_index()
                .sort_values("DATE")
            )
            piv_m = monthly.pivot(index="DATE", columns="SEGMENT_EN", values="UNI_VEH_PRODUCCION").fillna(0)
            piv_roll = piv_m.rolling(12, min_periods=12).sum().dropna()

            fig1_m = go.Figure()
            for seg in [s for s in ["SUVs", "Compacts", "Pickups", "Subcompacts"] if s in piv_roll.columns]:
                is_suv = (seg == "SUVs")
                color = BLUE if is_suv else (DARK if seg == "Compacts" else GREY)
                fig1_m.add_trace(
                    go.Scatter(
                        x=piv_roll.index,
                        y=piv_roll[seg],
                        mode="lines",
                        name=seg,
                        line=dict(color=color, width=3.5 if is_suv else 2.0),
                        hovertemplate=f"<b>{seg} (12M Rolling)</b><br>%{{x|%b %Y}}: %{{y:,.0f}}<extra></extra>",
                    )
                )
            fig1_m.add_vrect(
                x0="2020-03-01", x1="2022-08-01", fillcolor=BG_SHADE, opacity=0.7, line_width=0,
                annotation_text="COVID-19 & Chip Shortage", annotation_position="top left",
            )
            fig1_m.add_vline(x="2026-01-01", line_width=1.5, line_dash="dot", line_color=ORANGE)
            style_plotly_story(
                fig1_m,
                title="12-Month Rolling Assembly eliminates seasonality and confirms the 2026 inflection",
                subtitle="Trailing 12-month sum of vehicles assembled in Mexico by segment",
                y_title="12-Month Rolling Units",
                height=450,
                show_legend=True,
            )
            fig1_m.update_layout(margin=dict(r=40))
            st.plotly_chart(fig1_m, use_container_width=True)

        # Second row in Tab 1: Two side-by-side complementary charts
        col_t1_a, col_t1_b = st.columns(2)

        with col_t1_a:
            # 100% Stacked Bar: Passenger Cars vs Light Trucks
            tipo_yr = df_prod.pivot_table(
                index="ANIO", columns="TIPO_EN", values="UNI_VEH_PRODUCCION",
                aggfunc="sum", fill_value=0
            )
            tipo_pct = tipo_yr.div(tipo_yr.sum(axis=1), axis=0) * 100

            fig_tipo = go.Figure()
            lt_col = "Light Trucks (SUVs, Pickups & Minivans)"
            pc_col = "Passenger Cars"

            if lt_col in tipo_pct.columns:
                fig_tipo.add_trace(
                    go.Bar(
                        x=tipo_pct.index.astype(str),
                        y=tipo_pct[lt_col],
                        name="Light Trucks (SUVs/Pickups)",
                        marker_color=BLUE,
                        hovertemplate="<b>Light Trucks</b><br>Year: %{x}<br>Share: %{y:.1f}%<extra></extra>",
                    )
                )
            if pc_col in tipo_pct.columns:
                fig_tipo.add_trace(
                    go.Bar(
                        x=tipo_pct.index.astype(str),
                        y=tipo_pct[pc_col],
                        name="Passenger Cars (Sedans/Hatchbacks)",
                        marker_color=LIGHT_GREY,
                        hovertemplate="<b>Passenger Cars</b><br>Year: %{x}<br>Share: %{y:.1f}%<extra></extra>",
                    )
                )
            fig_tipo.update_layout(barmode="stack")
            style_plotly_story(
                fig_tipo,
                title="Light Trucks grew from 23% to 76% of assembly",
                subtitle="Annual share (%) of Passenger Cars vs. Light Trucks (2026 = Jan–Oct)",
                y_title="Share of Total Assembly (%)",
                height=390,
                show_legend=True,
            )
            fig_tipo.update_layout(
                margin=dict(r=25, b=65),
                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
            )
            fig_tipo.update_yaxes(range=[0, 100])
            st.plotly_chart(fig_tipo, use_container_width=True)

        with col_t1_b:
            # Seasonality Profile: Average Monthly Output (Pre-2026 vs 2026)
            m_25 = (
                df_prod[df_prod["ANIO"].between(2018, 2025)]
                .groupby("MES_NUM")["UNI_VEH_PRODUCCION"]
                .sum() / 8.0
            )
            m_26 = (
                df_prod[df_prod["ANIO"] == 2026]
                .groupby("MES_NUM")["UNI_VEH_PRODUCCION"]
                .sum()
            )
            month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

            fig_seas = go.Figure()
            fig_seas.add_trace(
                go.Scatter(
                    x=month_names,
                    y=[m_25.get(i, np.nan) for i in range(1, 13)],
                    mode="lines+markers",
                    name="2018–2025 Monthly Avg",
                    line=dict(color=GREY, width=2.5),
                    marker=dict(size=6, color=GREY),
                )
            )
            fig_seas.add_trace(
                go.Scatter(
                    x=month_names[:len(m_26)],
                    y=[m_26.get(i, np.nan) for i in range(1, len(m_26) + 1)],
                    mode="lines+markers",
                    name="2026 Actual (Jan–Oct)",
                    line=dict(color=ORANGE, width=3.2),
                    marker=dict(size=7, color=ORANGE),
                )
            )
            fig_seas.add_annotation(
                x="Dec", y=m_25.get(12, 200000),
                text="Dec retooling dip", showarrow=True, arrowhead=1, ax=-30, ay=-30,
                font=dict(size=10, color=TEXT_GREY),
            )
            style_plotly_story(
                fig_seas,
                title="Seasonality check: 2026 trails historical monthly pace",
                subtitle="Monthly assembly volume: 2026 actuals vs. 2018–2025 seasonal average",
                y_title="Monthly Units",
                height=390,
                show_legend=True,
            )
            fig_seas.update_layout(
                margin=dict(r=25, b=65),
                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
            )
            st.plotly_chart(fig_seas, use_container_width=True)

    # ==========================================================================
    # TAB 2: TRADE & U.S. TARIFF EXPOSURE (EXPORTS)
    # ==========================================================================
    with tab2:
        st.markdown(
            """
            <div class="insight-box">
            <b>Chapter 2 Takeaway — The 80% Single-Market Vulnerability:</b> Nearly <b>4 out of every 5 exported vehicles</b> go to the United States (<b>79.9% in 2025</b>, up from 62.5% in 2011). When U.S. tariff friction escalated in <b>January 2026</b>, Jan–Oct U.S. shipments dropped <b>-10.0% YoY</b> (-205k units), whereas exports to the <b>Rest of the World grew +5.5% YoY</b>—proving that geographic diversification is Mexico's strongest macro hedge.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Two aligned charts sharing the x-axis (never a dual y-axis!)
        exp_clean = df_exp.copy()
        exp_clean["DEST_GROUP"] = np.where(
            exp_clean["DEST_EN"] == "United States", "United States", "Rest of World"
        )
        exp_yr = exp_clean.pivot_table(
            index="ANIO", columns="DEST_GROUP", values="UNI_VEH_EXPORTACION",
            aggfunc="sum", fill_value=0
        )
        exp_yr_full = exp_yr[exp_yr.index <= 2025].copy()
        if "United States" not in exp_yr_full.columns:
            exp_yr_full["United States"] = 0
        if "Rest of World" not in exp_yr_full.columns:
            exp_yr_full["Rest of World"] = 0
        exp_yr_full["Total"] = exp_yr_full["United States"] + exp_yr_full["Rest of World"]
        exp_yr_full["US_Share"] = np.where(
            exp_yr_full["Total"] > 0,
            exp_yr_full["United States"] / exp_yr_full["Total"] * 100,
            0,
        )

        fig_trade = make_subplots(
            rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.10,
            row_heights=[0.62, 0.38],
        )

        fig_trade.add_trace(
            go.Bar(
                x=exp_yr_full.index,
                y=exp_yr_full["United States"],
                name="United States",
                marker_color=BLUE,
                hovertemplate="<b>United States</b><br>Year: %{x}<br>Exports: %{y:,.0f}<extra></extra>",
            ),
            row=1, col=1,
        )
        fig_trade.add_trace(
            go.Bar(
                x=exp_yr_full.index,
                y=exp_yr_full["Rest of World"],
                name="Rest of World",
                marker_color=LIGHT_BLUE,
                hovertemplate="<b>Rest of World</b><br>Year: %{x}<br>Exports: %{y:,.0f}<extra></extra>",
            ),
            row=1, col=1,
        )
        fig_trade.add_trace(
            go.Scatter(
                x=exp_yr_full.index,
                y=exp_yr_full["US_Share"],
                mode="lines+markers",
                name="U.S. Share (%)",
                line=dict(color=ORANGE, width=2.8),
                marker=dict(size=6, color=ORANGE),
                hovertemplate="<b>U.S. Export Share</b><br>Year: %{x}<br>Share: %{y:.1f}%<extra></extra>",
            ),
            row=2, col=1,
        )

        fig_trade.update_layout(
            barmode="stack",
            title=dict(
                text=(
                    f"<span style='font-size:17px; font-weight:700; color:{DARK};'>"
                    "U.S. export dependence climbed from 62.5% (2011) to ~80%, magnifying 2026 tariff risk</span>"
                    f"<br><span style='font-size:12.5px; color:{TEXT_GREY};'>"
                    "Top: Annual export volume by destination group (2005–2025) · Bottom: U.S. share of total exports (%)</span>"
                ),
                x=0.0, y=0.97,
            ),
            height=480,
            margin=dict(l=60, r=35, t=85, b=45),
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
            hovermode="x unified",
        )
        fig_trade.update_xaxes(showgrid=False, linecolor=LIGHT_GREY, tickfont=dict(color=TEXT_GREY))
        fig_trade.update_yaxes(
            title_text="Exported Units", showgrid=False, linecolor=LIGHT_GREY,
            tickfont=dict(color=TEXT_GREY), rangemode="tozero", row=1, col=1,
        )
        fig_trade.update_yaxes(
            title_text="U.S. Share (%)", showgrid=False, linecolor=LIGHT_GREY,
            tickfont=dict(color=TEXT_GREY), range=[0, 100], row=2, col=1,
        )
        st.plotly_chart(fig_trade, use_container_width=True)

        col_t2_a, col_t2_b = st.columns(2)

        with col_t2_a:
            # Top 10 Secondary Destinations (excluding United States)
            non_us = (
                df_exp[df_exp["DEST_EN"] != "United States"]
                .groupby("DEST_EN")["UNI_VEH_EXPORTACION"]
                .sum()
                .sort_values(ascending=True)
                .tail(10)
            )
            bar_colors = [TEAL if idx in ["Canada", "Germany", "Brazil"] else LIGHT_GREY for idx in non_us.index]
            fig_dest = go.Figure(
                go.Bar(
                    x=non_us.values,
                    y=non_us.index,
                    orientation="h",
                    marker_color=bar_colors,
                    text=[f"{v/1e6:.2f}M" if v >= 1e6 else f"{v/1e3:,.0f}k" for v in non_us.values],
                    textposition="outside",
                    textfont=dict(size=11, color=DARK),
                    hovertemplate="<b>%{y}</b><br>Cumulative Exports: %{x:,.0f}<extra></extra>",
                )
            )
            style_plotly_story(
                fig_dest,
                title="Canada, Germany & Brazil lead non-U.S. demand",
                subtitle="Top 10 secondary export destinations (cumulative units, filtered window)",
                height=410,
            )
            fig_dest.update_layout(margin=dict(l=110, r=55, t=78, b=35))
            fig_dest.update_xaxes(visible=False, range=[0, non_us.max() * 1.22 if len(non_us) else 10])
            fig_dest.update_yaxes(linecolor="white", tickfont=dict(color=DARK, size=11.5))
            st.plotly_chart(fig_dest, use_container_width=True)

        with col_t2_b:
            # Jan-Oct 2025 vs Jan-Oct 2026 YoY Change by Major Export Destination
            ytd_dest = df_exp[df_exp["ANIO"].isin([2025, 2026]) & df_exp["MES_NUM"].isin(months_26)].pivot_table(
                index="DEST_EN", columns="ANIO", values="UNI_VEH_EXPORTACION", aggfunc="sum", fill_value=0
            )
            if 2025 in ytd_dest.columns and 2026 in ytd_dest.columns:
                ytd_dest = ytd_dest[ytd_dest[2025] >= 5000].copy()
                ytd_dest["YoY_%"] = (ytd_dest[2026] - ytd_dest[2025]) / ytd_dest[2025] * 100
                ytd_dest = ytd_dest.sort_values("YoY_%")

                colors_yoy = [ORANGE if v < 0 else TEAL for v in ytd_dest["YoY_%"]]
                fig_yoy_d = go.Figure(
                    go.Bar(
                        x=ytd_dest["YoY_%"],
                        y=ytd_dest.index,
                        orientation="h",
                        marker_color=colors_yoy,
                        text=[f"{v:+.1f}%" for v in ytd_dest["YoY_%"]],
                        textposition="outside",
                        textfont=dict(size=11, color=DARK),
                        hovertemplate="<b>%{y}</b><br>Jan–Oct 2026 YoY: %{x:+.1f}%<extra></extra>",
                    )
                )
                style_plotly_story(
                    fig_yoy_d,
                    title="2026 YTD: U.S. shipments fell -10%, while LatAm & Germany grew",
                    subtitle="Jan–Oct 2026 vs. Jan–Oct 2025 export growth (%) for destinations >5k units",
                    height=410,
                )
                fig_yoy_d.update_layout(margin=dict(l=115, r=55, t=78, b=35))
                xmin = min(ytd_dest["YoY_%"].min() * 1.35, -15) if len(ytd_dest) else -20
                xmax = max(ytd_dest["YoY_%"].max() * 1.35, 15) if len(ytd_dest) else 20
                fig_yoy_d.update_xaxes(visible=False, range=[xmin, xmax])
                fig_yoy_d.update_yaxes(linecolor="white", tickfont=dict(color=DARK, size=11.5))
                st.plotly_chart(fig_yoy_d, use_container_width=True)

    # ==========================================================================
    # TAB 3: DOMESTIC MARKET VS. EXPORT ALLOCATION
    # ==========================================================================
    with tab3:
        st.markdown(
            """
            <div class="insight-box">
            <b>Chapter 3 Takeaway — A Two-Speed Industry:</b> Crossing Production, Exports, and Domestic Retail Sales exposes a stark structural divide. <b>SUVs are built almost exclusively for export (93.5% exported in 2025)</b>, whereas <b>Subcompacts rely 80.8% on Mexican consumers</b>. Meanwhile, domestic retail sales of locally produced model lines have yet to regain their 2016 peak (570k units), even as automakers supplement local lines with targeted imports from Japan, China, and the U.S.
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_t3_a, col_t3_b = st.columns(2)

        with col_t3_a:
            # 100% Horizontal Stacked Bar: Exported vs Domestic Absorption by Segment (2025)
            p_seg = df_prod[df_prod["ANIO"] == 2025].groupby("SEGMENT_EN")["UNI_VEH_PRODUCCION"].sum()
            e_seg = df_exp[df_exp["ANIO"] == 2025].groupby("SEGMENT_EN")["UNI_VEH_EXPORTACION"].sum()
            s_seg = df_sales[(df_sales["ANIO"] == 2025) & (df_sales["ORIGIN_TYPE_EN"] == "Domestic (Made in Mexico)")].groupby("SEGMENT_EN")["UNI_VEH_VENTAS"].sum()

            alloc_df = pd.DataFrame({"Exported": e_seg, "Domestic_Sold": s_seg}).fillna(0)
            alloc_df = alloc_df[alloc_df.sum(axis=1) > 0]
            alloc_pct = alloc_df.div(alloc_df.sum(axis=1), axis=0) * 100
            alloc_pct = alloc_pct.sort_values("Exported", ascending=True)

            fig_alloc = go.Figure()
            fig_alloc.add_trace(
                go.Bar(
                    y=alloc_pct.index,
                    x=alloc_pct["Exported"],
                    name="Exported Abroad (%)",
                    orientation="h",
                    marker_color=BLUE,
                    text=[f"{v:.1f}%" for v in alloc_pct["Exported"]],
                    textposition="inside",
                    insidetextanchor="middle",
                    textfont=dict(color="white", size=11.5, family="Inter, Arial"),
                )
            )
            fig_alloc.add_trace(
                go.Bar(
                    y=alloc_pct.index,
                    x=alloc_pct["Domestic_Sold"],
                    name="Sold in Mexico (%)",
                    orientation="h",
                    marker_color=LIGHT_GREY,
                    text=[f"{v:.1f}%" if v >= 10 else "" for v in alloc_pct["Domestic_Sold"]],
                    textposition="inside",
                    insidetextanchor="middle",
                    textfont=dict(color=DARK, size=11.5, family="Inter, Arial"),
                )
            )
            fig_alloc.update_layout(barmode="stack")
            style_plotly_story(
                fig_alloc,
                title="93% of SUVs go abroad, while 81% of Subcompacts stay in Mexico",
                subtitle="2025 destination split (%) of Mexican-built vehicles (Exports vs. Domestic Retail Sales)",
                height=410,
                show_legend=True,
            )
            fig_alloc.update_layout(
                margin=dict(l=105, r=25, t=82, b=40),
                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
            )
            fig_alloc.update_xaxes(visible=False, range=[0, 100])
            fig_alloc.update_yaxes(linecolor="white", tickfont=dict(color=DARK, size=12))
            st.plotly_chart(fig_alloc, use_container_width=True)

        with col_t3_b:
            # Domestic Sales Trend: Nacional vs Importado Supplement
            sales_yr = df_sales[df_sales["ANIO"] <= 2025].pivot_table(
                index="ANIO", columns="ORIGIN_TYPE_EN", values="UNI_VEH_VENTAS",
                aggfunc="sum", fill_value=0
            )
            fig_dom = go.Figure()
            if "Domestic (Made in Mexico)" in sales_yr.columns:
                fig_dom.add_trace(
                    go.Bar(
                        x=sales_yr.index,
                        y=sales_yr["Domestic (Made in Mexico)"],
                        name="Made in Mexico (NACIONAL)",
                        marker_color=GREY,
                    )
                )
            if "Imported Supplement" in sales_yr.columns:
                fig_dom.add_trace(
                    go.Bar(
                        x=sales_yr.index,
                        y=sales_yr["Imported Supplement"],
                        name="Imported Supplement (Japan/China/US/Korea)",
                        marker_color=ORANGE,
                    )
                )
            fig_dom.update_layout(barmode="stack")
            style_plotly_story(
                fig_dom,
                title="Domestic sales of locally built lines remain 18% below 2016 peak",
                subtitle="Annual Mexican retail sales of registry model lines by origin (2005–2025)",
                y_title="Domestic Retail Units",
                height=410,
                show_legend=True,
            )
            fig_dom.update_layout(
                margin=dict(r=25, b=45),
                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
            )
            st.plotly_chart(fig_dom, use_container_width=True)

        # Origin breakdown table for Imported Supplement units
        imp_origins = (
            df_sales[df_sales["ORIGIN_TYPE_EN"] == "Imported Supplement"]
            .groupby(["ORIGIN_COUNTRY_EN", "BRAND_CLEAN"])["UNI_VEH_VENTAS"]
            .sum()
            .reset_index()
            .sort_values("UNI_VEH_VENTAS", ascending=False)
            .head(8)
        )
        if not imp_origins.empty:
            with st.expander("🔍 Inspect Imported Supplement Breakdown (Dual-Sourced Model Lines in RAIAVL)"):
                st.caption(
                    "Even within model lines assembled in Mexico, automakers import supplemental trims from Japan, China, the U.S., and South Korea to meet domestic demand."
                )
                imp_origins.columns = ["Source Country", "Automaker", "Cumulative Domestic Units"]
                st.dataframe(imp_origins, use_container_width=True, hide_index=True)

    # ==========================================================================
    # TAB 4: AUTOMAKERS, NEW ENTRANTS & TOP MODELS
    # ==========================================================================
    with tab4:
        st.markdown(
            """
            <div class="insight-box">
            <b>Chapter 4 Takeaway — Wave of Asian & European Entrants Reshaped Output:</b> While legacy leaders (<b>Nissan, General Motors, Ford, Volkswagen, Stellantis</b>) still anchor volume, Mexico's production surge since 2014 was powered by new assembly plants from <b>Mazda (2014)</b>, <b>KIA (2016)</b>, <b>Audi (2017)</b>, <b>Toyota's Tacoma expansion</b>, and <b>Acura (2025)</b>.
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_t4_a, col_t4_b = st.columns(2)

        with col_t4_a:
            # Slopegraph / Dumbbell comparison: 2015 vs 2025 Assembly by Automaker
            b_comp = df_prod[df_prod["ANIO"].isin([2015, 2025])].pivot_table(
                index="BRAND_CLEAN", columns="ANIO", values="UNI_VEH_PRODUCCION",
                aggfunc="sum", fill_value=0
            )
            if 2015 in b_comp.columns and 2025 in b_comp.columns:
                b_comp = b_comp[(b_comp[2015] > 0) | (b_comp[2025] > 0)].sort_values(2025, ascending=True)
                fig_brand = go.Figure()

                for brand, row in b_comp.iterrows():
                    v15, v25 = row[2015], row[2025]
                    is_new_wave = brand in ["KIA", "Audi", "Toyota", "Acura", "Ford Motor"] and v25 > v15
                    seg_col = BLUE if is_new_wave else GREY
                    fig_brand.add_trace(
                        go.Scatter(
                            x=[v15, v25],
                            y=[brand, brand],
                            mode="lines",
                            line=dict(color=seg_col, width=2.8 if is_new_wave else 1.8),
                            showlegend=False,
                            hoverinfo="skip",
                        )
                    )

                fig_brand.add_trace(
                    go.Scatter(
                        x=b_comp[2015],
                        y=b_comp.index,
                        mode="markers",
                        name="2015 Assembly",
                        marker=dict(color=LIGHT_GREY, size=10, line=dict(color=DARK, width=1)),
                        hovertemplate="<b>%{y} (2015)</b>: %{x:,.0f} units<extra></extra>",
                    )
                )
                fig_brand.add_trace(
                    go.Scatter(
                        x=b_comp[2025],
                        y=b_comp.index,
                        mode="markers",
                        name="2025 Assembly",
                        marker=dict(color=BLUE, size=11),
                        hovertemplate="<b>%{y} (2025)</b>: %{x:,.0f} units<extra></extra>",
                    )
                )
                style_plotly_story(
                    fig_brand,
                    title="KIA, Audi, Toyota & Ford drove net assembly gains (2015 vs. 2025)",
                    subtitle="Dumbbell comparison of annual assembly by automaker (2015 grey vs. 2025 blue)",
                    x_title="Vehicles Assembled",
                    height=440,
                    show_legend=True,
                )
                fig_brand.update_layout(
                    margin=dict(l=155, r=30, t=82, b=45),
                    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
                )
                fig_brand.update_yaxes(tickfont=dict(color=DARK, size=11))
                st.plotly_chart(fig_brand, use_container_width=True)

        with col_t4_b:
            # Top 10 Vehicle Models in Filtered Period
            top_models = (
                df_prod.groupby(["BRAND_CLEAN", "MODELO", "SEGMENT_EN"])["UNI_VEH_PRODUCCION"]
                .sum()
                .reset_index()
                .sort_values("UNI_VEH_PRODUCCION", ascending=True)
                .tail(10)
            )
            top_models["LABEL"] = top_models["BRAND_CLEAN"].str.replace("Stellantis (Chrysler + Fiat)", "Stellantis", regex=False) + " · " + top_models["MODELO"].str.rstrip("-")
            m_colors = [BLUE if s == "SUVs" else LIGHT_GREY for s in top_models["SEGMENT_EN"]]

            fig_mod = go.Figure(
                go.Bar(
                    x=top_models["UNI_VEH_PRODUCCION"],
                    y=top_models["LABEL"],
                    orientation="h",
                    marker_color=m_colors,
                    text=[f"{v/1e6:.2f}M" if v >= 1e6 else f"{v/1e3:,.0f}k" for v in top_models["UNI_VEH_PRODUCCION"]],
                    textposition="outside",
                    textfont=dict(size=10.5, color=DARK),
                    customdata=top_models["SEGMENT_EN"],
                    hovertemplate="<b>%{y}</b><br>Segment: %{customdata}<br>Units: %{x:,.0f}<extra></extra>",
                )
            )
            style_plotly_story(
                fig_mod,
                title="Top 10 assembled models (Blue = SUVs, Grey = Sedans/Pickups)",
                subtitle="Cumulative assembly volume across the selected time window & filters",
                height=440,
            )
            fig_mod.update_layout(margin=dict(l=170, r=55, t=82, b=35))
            fig_mod.update_xaxes(visible=False, range=[0, top_models["UNI_VEH_PRODUCCION"].max() * 1.22 if len(top_models) else 10])
            fig_mod.update_yaxes(linecolor="white", tickfont=dict(color=DARK, size=11))
            st.plotly_chart(fig_mod, use_container_width=True)

    # ==========================================================================
    # TAB 5: DATA GOVERNANCE, LIMITATIONS & POLICY RECOMMENDATIONS
    # ==========================================================================
    with tab5:
        st.markdown("### 1. Registry Coverage, Data Vintage & Administrative Limitations")
        col_g1, col_g2 = st.columns([1.15, 1.0])

        with col_g1:
            st.markdown(
                """
                INEGI's **RAIAVL** is an **administrative registry** compiled from voluntary monthly reports by AMIA-affiliated automakers—not a statistical sample. To ensure analytical integrity for Ministry of Economy decision-makers, four structural limitations must be weighed:

                1. **Blind Spot on Non-Reporting Brands (Chinese EV/ICE Challengers):** Fast-growing Chinese entrants such as **BYD, MG, Chirey (Chery), Omoda, and Geely** do not report monthly volumes to INEGI (and panel changes such as GAC's retroactive entry or Motornation's exit shift aggregate totals). Furthermore, because this dataset inner-joins Production, Exports, and Sales, import-only brands without Mexican assembly plants are excluded.
                2. **Absence of Value-Added, Pricing & Powertrain Granularity:** RAIAVL tracks physical unit counts (`UNI_VEH`), not export dollar value, transaction prices, or EV/Hybrid battery content—meaning high-margin electric SUVs (e.g., Ford Mustang Mach-E, GM Equinox EV) carry the same unit weight as entry-level subcompacts.
                3. **Loss of Plant-Level / State Geography in Multi-Table Merge:** While INEGI's standalone Production table includes state (`ENTIDAD_FEDERATIVA`), merging across Production, Domestic Sales, and Exports drops state-level assembly attribution, preventing direct plant-by-plant tariff stress testing across Coahuila, Guanajuato, Nuevo León, Puebla, and Sonora.
                4. **Administrative Revisions & Inventory Lags (`ESTATUS`):** Records from **2024–Sep 2026** remain *Revised Figures* (`Cifras Revisadas`) and **October 2026** is *Preliminary* (`Cifras Preliminares`). In heavy-duty pickups (GM Silverado 2500 / GMC Sierra, Stellantis RAM 2500), export shipments are logged against zero new production rows due to inventory drawdowns and model-code nomenclature splits.
                """
            )

        with col_g2:
            status_yr = (
                raw_df.groupby(["ANIO", "STATUS_EN"])
                .size()
                .reset_index(name="Records")
                .pivot(index="ANIO", columns="STATUS_EN", values="Records")
                .fillna(0)
            )
            fig_stat = go.Figure()
            stat_palette = {
                "Definitive Figures": GREY,
                "Revised Figures": BLUE,
                "Preliminary Figures": ORANGE,
            }
            for st_name in ["Definitive Figures", "Revised Figures", "Preliminary Figures"]:
                if st_name in status_yr.columns:
                    fig_stat.add_trace(
                        go.Bar(
                            x=status_yr.index.astype(str),
                            y=status_yr[st_name],
                            name=st_name,
                            marker_color=stat_palette[st_name],
                        )
                    )
            fig_stat.update_layout(barmode="stack")
            style_plotly_story(
                fig_stat,
                title="Data Vintage Audit: 2024–2026 figures remain open to revision",
                subtitle="Merged dataset record count by INEGI statistical status (ESTATUS)",
                y_title="Merged Records",
                height=370,
                show_legend=True,
            )
            fig_stat.update_layout(
                margin=dict(r=20, b=55),
                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
            )
            st.plotly_chart(fig_stat, use_container_width=True)

        st.markdown("---")
        st.markdown("### 2. Strategic Recommendations for the Ministry of Economy (Secretaría de Economía)")

        rec1, rec2, rec3 = st.columns(3)
        with rec1:
            st.markdown(
                f"""
                <div class="kpi-card" style="border-top: 4px solid {BLUE};">
                    <div class="kpi-label">Pillar 1 · USMCA Shield</div>
                    <h4 style="margin:0.3rem 0; color:{DARK};">Regional Content & EV/SUV Rules</h4>
                    <p style="font-size:0.88rem; color:{DARK}; margin-bottom:0;">
                    With <b>93.5% of Mexican SUVs exported</b> and <b>79.9% bound for the U.S.</b>, prioritize Tier-1/Tier-2 battery, powertrain, and aluminum localization incentives in northern and Bajío clusters so Mexican-built SUVs qualify for zero-tariff USMCA regional value content (RVC) thresholds.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with rec2:
            st.markdown(
                f"""
                <div class="kpi-card" style="border-top: 4px solid {TEAL};">
                    <div class="kpi-label">Pillar 2 · Trade Diversification</div>
                    <h4 style="margin:0.3rem 0; color:{DARK};">Accelerate LatAm & EU Corridors</h4>
                    <p style="font-size:0.88rem; color:{DARK}; margin-bottom:0;">
                    While U.S. shipments fell <b>-10.0% YTD in 2026</b>, exports to non-U.S. partners grew <b>+5.5%</b>. Leverage updated EU-Mexico and Pacific Alliance / Mercosur automotive quotas (Germany, Brazil, Colombia, Chile) to absorb compact and SUV capacity.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with rec3:
            st.markdown(
                f"""
                <div class="kpi-card" style="border-top: 4px solid {ORANGE};">
                    <div class="kpi-label">Pillar 3 · Registry Modernization</div>
                    <h4 style="margin:0.3rem 0; color:{DARK};">Mandatory Reporting & Plant Tracking</h4>
                    <p style="font-size:0.88rem; color:{DARK}; margin-bottom:0;">
                    Partner with INEGI and AMIA to mandate customs-linked reporting for non-AMIA import brands (closing the Chinese EV blind spot) and standardize model IDs across Production and Export tables to eliminate pickup reporting lags.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
