import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ==============================================================================
# PAGE CONFIGURATION & GLOBAL STYLING
# Inspired by Wexler, Shaffer & Cotgreave, "The Big Book of Dashboards" (Wiley)
# ==============================================================================
st.set_page_config(
    page_title="Mexico Light-Vehicle Industry | RAIAVL Executive Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Color-Blind-Safe Palette (Maureen Stone / Tableau CVD-Safe — Ch. 1 & Ch. 33)
# Never uses red/green together; relies on Blue / Orange / Teal + 3-tier neutral greys
DARK_INK    = "#0F172A"   # Tier 1 typography: headlines & primary values
SLATE_TEXT  = "#475569"   # Tier 2 typography: subtitles & axis labels
MUTED_TEXT  = "#94A3B8"   # Tier 3 typography: footnotes & source metadata
GREY_CTX    = "#94A3B8"   # Context bars/lines (peers & historical background)
LIGHT_GREY  = "#CBD5E1"   # Hairline axes, gridlines & secondary bars
BG_SHADE    = "#F1F5F9"   # Event/shock background shading
BLUE        = "#1D4ED8"   # Primary focus / Ahead of pace / Spotlight brand
LIGHT_BLUE  = "#93C5FD"   # Secondary positive / Rest of World
ORANGE      = "#D97706"   # Alert / Tariff contraction / Behind pace (CVD-safe amber-orange)
DEEP_ORANGE = "#C2410C"   # Strong alert / 2026 YTD highlight
TEAL        = "#0F766E"   # Diversification / Growth corridors

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

MONTH_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

STATUS_MAP = {
    "Cifras Definitivas": "Definitive Figures",
    "Cifras Revisadas": "Revised Figures",
    "Cifras Preliminares": "Preliminary Figures",
}

# Clean Financial Times / Big Book of Dashboards CSS Grid & Typography Hierarchy
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 1420px;
    }
    .exec-header {
        border-bottom: 2px solid #0F172A;
        padding-bottom: 0.65rem;
        margin-bottom: 0.85rem;
    }
    .role-strip {
        background-color: #F8FAFC;
        border-left: 4px solid #1D4ED8;
        padding: 0.75rem 1.05rem;
        border-radius: 4px;
        margin-bottom: 0.75rem;
        font-size: 0.91rem;
        color: #1E293B;
    }
    .takeaway-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 3px solid #1D4ED8;
        border-radius: 6px;
        padding: 0.75rem 0.95rem;
        height: 100%;
        font-size: 0.88rem;
        color: #1E293B;
        line-height: 1.42;
    }
    .takeaway-title {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #1D4ED8;
        margin-bottom: 0.25rem;
    }
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 0.85rem 1.0rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }
    .kpi-label {
        font-size: 0.76rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.2rem;
    }
    .kpi-value {
        font-size: 1.72rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.15;
    }
    .kpi-delta-pos {
        font-size: 0.82rem;
        font-weight: 600;
        color: #0F766E;
        margin-top: 0.22rem;
    }
    .kpi-delta-neg {
        font-size: 0.82rem;
        font-weight: 600;
        color: #C2410C;
        margin-top: 0.22rem;
    }
    .kpi-sub {
        font-size: 0.76rem;
        color: #94A3B8;
        margin-top: 0.14rem;
    }
    .insight-callout {
        background-color: #F8FAFC;
        border-left: 4px solid #1D4ED8;
        padding: 0.8rem 1.05rem;
        border-radius: 4px;
        margin-bottom: 0.9rem;
        font-size: 0.92rem;
        color: #1E293B;
        line-height: 1.45;
    }
    .source-note {
        font-size: 0.77rem;
        color: #94A3B8;
        margin-top: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# DATA LOADING, HARMONIZATION & EXACT GRAIN DEDUPLICATION
# ==============================================================================
@st.cache_data
def load_and_clean_data(csv_path: str = "dataset_final_raiavl.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["MES_NUM"] = df["MES"].map(MONTH_MAP)
    df["DATE"] = pd.to_datetime(dict(year=df["ANIO"], month=df["MES_NUM"], day=1))
    df["SEGMENT_EN"] = df["SEGMENTO"].map(SEGMENT_MAP).fillna(df["SEGMENTO"])
    df["TIPO_EN"] = df["TIPO"].map(TIPO_MAP).fillna(df["TIPO"])
    df["DEST_EN"] = df["PAIS_DESTINO"].map(COUNTRY_MAP).fillna(df["PAIS_DESTINO"])
    df["ORIGIN_COUNTRY_EN"] = df["DESC_PAIS_ORIGEN"].map(COUNTRY_MAP).fillna(df["DESC_PAIS_ORIGEN"])
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
    Harmonizes Stellantis (Chrysler + Fiat) and deduplicates each RAIAVL table
    at its exact structural grain so inner-join keys never double-count volume.
    """
    work = df.copy()
    if harmonize_stellantis:
        work["BRAND_CLEAN"] = work["MARCA"].replace(
            {"Chrysler": "Stellantis (Chrysler + Fiat)", "Fiat": "Stellantis (Chrysler + Fiat)"}
        )
    else:
        work["BRAND_CLEAN"] = work["MARCA"]

    top_countries = {"United States", "Canada", "Germany", "Brazil", "Colombia", "Argentina", "Chile", "China"}
    work["DEST_BUCKET"] = np.where(
        work["DEST_EN"].isin(top_countries),
        work["DEST_EN"],
        "Other / Unspecified",
    )

    mask = (
        work["ANIO"].between(year_range[0], year_range[1])
        & work["SEGMENT_EN"].isin(selected_segments)
        & work["BRAND_CLEAN"].isin(selected_brands)
    )
    sub = work[mask].copy()

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
# CHART STYLING HELPER (BBOD Ch. 1, Ch. 2 & Ch. 28 FT Editorial Precision)
# ==============================================================================
def style_bbod_chart(
    fig: go.Figure,
    title: str,
    subtitle: str,
    y_title: str = "",
    x_title: str = "",
    height: int = 420,
    show_legend: bool = False,
    zero_y: bool = True,
) -> go.Figure:
    fig.update_layout(
        title=dict(
            text=(
                f"<span style='font-size:16.5px; font-weight:700; color:{DARK_INK};'>{title}</span>"
                f"<br><span style='font-size:12.2px; font-weight:400; color:{SLATE_TEXT};'>{subtitle}</span>"
            ),
            x=0.0,
            xanchor="left",
            y=0.96,
            yanchor="top",
        ),
        height=height,
        margin=dict(l=55, r=30, t=78, b=48),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", color=DARK_INK, size=12),
        showlegend=show_legend,
        hovermode="x unified",
    )
    fig.update_xaxes(
        title=dict(text=x_title, font=dict(size=11.5, color=SLATE_TEXT)),
        showgrid=False,
        linecolor=LIGHT_GREY,
        linewidth=1,
        tickfont=dict(color=SLATE_TEXT, size=11),
        zeroline=False,
    )
    y_kwargs = dict(
        title=dict(text=y_title, font=dict(size=11.5, color=SLATE_TEXT)),
        showgrid=True,
        gridcolor="#F1F5F9",
        gridwidth=1,
        linecolor=LIGHT_GREY,
        linewidth=1,
        tickfont=dict(color=SLATE_TEXT, size=11),
        zeroline=True,
        zerolinecolor=LIGHT_GREY,
        zerolinewidth=1,
    )
    if zero_y:
        y_kwargs["rangemode"] = "tozero"
    fig.update_yaxes(**y_kwargs)
    return fig


def short_brand(name: str) -> str:
    return name.replace("Stellantis (Chrysler + Fiat)", "Stellantis")


# ==============================================================================
# MAIN APPLICATION
# ==============================================================================
def main():
    if not os.path.exists("dataset_final_raiavl.csv"):
        st.error("File `dataset_final_raiavl.csv` not found in the repository root.")
        st.stop()

    raw_df = load_and_clean_data("dataset_final_raiavl.csv")

    # --------------------------------------------------------------------------
    # SIDEBAR: PERSONAL SPOTLIGHT & ANALYTICAL FILTERS (BBOD Ch. 3, Ch. 6, Ch. 30)
    # --------------------------------------------------------------------------
    st.sidebar.markdown("## 🎯 Personalize & Filter")
    st.sidebar.caption("Spotlight a specific automaker against peers or slice the 2005–2026 RAIAVL registry.")

    harmonize_stellantis = st.sidebar.checkbox(
        "Harmonize Stellantis (Chrysler + Fiat)",
        value=True,
        help="Consolidates Chrysler (2005–2026) and Fiat (2011–2019) into Stellantis.",
    )

    temp_brands = (
        raw_df["MARCA"]
        .replace({"Chrysler": "Stellantis (Chrysler + Fiat)", "Fiat": "Stellantis (Chrysler + Fiat)"})
        .unique()
        if harmonize_stellantis
        else raw_df["MARCA"].unique()
    )
    all_brands = sorted(temp_brands.tolist())

    # BBOD Chapter 30 ("Make Your Dashboards Personal") & Chapter 3 ("Comparing with Peers")
    spotlight_brand = st.sidebar.selectbox(
        "🔍 Spotlight Automaker (Peer Benchmark)",
        options=["None (Industry Overview)"] + all_brands,
        index=0,
        help="Highlights your chosen automaker in bold Blue against all industry peers in grey (BBOD Ch. 3 & Ch. 30).",
    )

    min_yr, max_yr = int(raw_df["ANIO"].min()), int(raw_df["ANIO"].max())
    year_range = st.sidebar.slider(
        "Historical Time Window",
        min_value=min_yr,
        max_value=max_yr,
        value=(2005, 2026),
        step=1,
    )

    # BBOD Chapter 6 ("Select Period" parameter control, p. 88)
    avail_years = list(range(year_range[1], max(year_range[0], 2006) - 1, -1))
    anchor_year = st.sidebar.selectbox(
        "Comparison Period ('Now' vs. Prior Year)",
        options=avail_years,
        index=0,
        help="Selects the primary period for 'Ranking by Now, Comparing with Then' (uses Jan–Oct YTD apples-to-apples when 2026 is selected).",
    )

    with st.sidebar.expander("⚙️ Dimension Filters (Segments, Brands, Markets)", expanded=False):
        all_segments = ["SUVs", "Compacts", "Pickups", "Subcompacts", "Minivans"]
        selected_segments = st.multiselect("Vehicle Segment", options=all_segments, default=all_segments)
        selected_brands = st.multiselect("Included Automakers", options=all_brands, default=all_brands)
        dest_options = [
            "United States", "Canada", "Germany", "Brazil",
            "Colombia", "Argentina", "Chile", "China", "Other / Unspecified",
        ]
        selected_dest_groups = st.multiselect("Export Destination", options=dest_options, default=dest_options)

    # Ensure spotlight brand is always included in selected_brands if chosen
    if spotlight_brand != "None (Industry Overview)" and spotlight_brand not in selected_brands:
        selected_brands = selected_brands + [spotlight_brand]

    if not selected_segments or not selected_brands or not selected_dest_groups:
        st.warning("Please select at least one Segment, Automaker, and Export Destination in the sidebar.")
        st.stop()

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"""
        <div style="font-size:0.80rem; color:{SLATE_TEXT}; line-height:1.45;">
        <b>Methodology & Vintage Guardrails</b><br>
        • <b>Source:</b> INEGI RAIAVL (2005–Oct 2026).<br>
        • <b>Seasonality Control:</b> When comparing 2026 (Jan–Oct), prior years are automatically matched to <b>Jan–Oct YTD</b>.<br>
        • <b>Vintage:</b> Oct 2026 = <i>Preliminary</i>; 2024–Sep 2026 = <i>Revised</i>; 2005–2023 = <i>Definitive</i>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    sub_raw, df_prod, df_sales, df_exp = prepare_filtered_tables(
        raw_df,
        year_range=year_range,
        selected_segments=selected_segments,
        selected_brands=selected_brands,
        selected_dest_groups=selected_dest_groups,
        harmonize_stellantis=harmonize_stellantis,
    )

    # Determine comparison months (if anchor_year == 2026, match Jan-Oct across both years)
    months_anchor = sorted(df_prod[df_prod["ANIO"] == anchor_year]["MES_NUM"].unique().tolist())
    if not months_anchor:
        months_anchor = list(range(1, 11)) if anchor_year == 2026 else list(range(1, 13))
    prev_year = anchor_year - 1
    period_label = f"Jan–{MONTH_SHORT[max(months_anchor)-1]} {anchor_year} YTD" if len(months_anchor) < 12 else f"Full-Year {anchor_year}"
    prev_label = f"Jan–{MONTH_SHORT[max(months_anchor)-1]} {prev_year}" if len(months_anchor) < 12 else f"{prev_year}"

    # --------------------------------------------------------------------------
    # EXECUTIVE HEADER & TOP-OF-PAGE KEY TAKEAWAYS (BBOD Ch. 7 Fig. 7.1 & Ch. 28)
    # --------------------------------------------------------------------------
    st.markdown(
        f"""
        <div class="exec-header">
            <h1 style="margin:0; color:{DARK_INK}; font-size:1.95rem; font-weight:800; letter-spacing:-0.01em;">
            Mexico's Light-Vehicle Industry: Structural Pivot & 2026 Tariff Shock
            </h1>
            <p style="margin:0.2rem 0 0 0; color:{SLATE_TEXT}; font-size:0.98rem;">
            Strategic Intelligence Dashboard · INEGI Administrative Registry (RAIAVL, 2005–Oct 2026) · Prepared for <b>Secretaría de Economía</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="role-strip">
        <b>Decision Brief (Undersecretary of Industry & Commerce · 2026 USMCA Review):</b> Mexico transformed into a 3.16M-unit SUV and light-truck export hub—but <b>~80% single-market U.S. dependence</b> left assembly plants exposed when U.S. tariff friction hit in <b>January 2026</b>. Use the controls on the left to benchmark any automaker against peers and stress-test trade diversification scenarios.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Dynamic calculation for the 3 top-level Executive Takeaway Bullets (BBOD Ch. 7)
    p_now_all = df_prod[(df_prod["ANIO"] == anchor_year) & (df_prod["MES_NUM"].isin(months_anchor))]["UNI_VEH_PRODUCCION"].sum()
    p_prev_all = df_prod[(df_prod["ANIO"] == prev_year) & (df_prod["MES_NUM"].isin(months_anchor))]["UNI_VEH_PRODUCCION"].sum()
    p_yoy_all = ((p_now_all - p_prev_all) / p_prev_all * 100) if p_prev_all > 0 else 0.0

    e_now_all = df_exp[(df_exp["ANIO"] == anchor_year) & (df_exp["MES_NUM"].isin(months_anchor))]["UNI_VEH_EXPORTACION"].sum()
    e_prev_all = df_exp[(df_exp["ANIO"] == prev_year) & (df_exp["MES_NUM"].isin(months_anchor))]["UNI_VEH_EXPORTACION"].sum()
    us_now_all = df_exp[(df_exp["ANIO"] == anchor_year) & (df_exp["MES_NUM"].isin(months_anchor)) & (df_exp["DEST_EN"] == "United States")]["UNI_VEH_EXPORTACION"].sum()
    us_prev_all = df_exp[(df_exp["ANIO"] == prev_year) & (df_exp["MES_NUM"].isin(months_anchor)) & (df_exp["DEST_EN"] == "United States")]["UNI_VEH_EXPORTACION"].sum()
    row_now_all = e_now_all - us_now_all
    row_prev_all = e_prev_all - us_prev_all
    us_yoy_all = ((us_now_all - us_prev_all) / us_prev_all * 100) if us_prev_all > 0 else 0.0
    row_yoy_all = ((row_now_all - row_prev_all) / row_prev_all * 100) if row_prev_all > 0 else 0.0

    suv_now = df_prod[(df_prod["ANIO"] == anchor_year) & (df_prod["MES_NUM"].isin(months_anchor)) & (df_prod["SEGMENT_EN"] == "SUVs")]["UNI_VEH_PRODUCCION"].sum()
    suv_share_now = (suv_now / p_now_all * 100) if p_now_all > 0 else 0.0

    tk1, tk2, tk3 = st.columns(3)
    with tk1:
        st.markdown(
            f"""
            <div class="takeaway-card">
                <div class="takeaway-title">1 · Output Inflection ({period_label})</div>
                Total assembly stands at <b>{p_now_all/1e6:.2f}M units</b> (<b>{p_yoy_all:+.1f}% YoY</b> vs. {prev_label}), led by <b>SUVs ({suv_share_now:.1f}% of mix)</b>. Pickups remain ahead of seasonal pace, while Compacts and SUVs absorbed the tariff pullback.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with tk2:
        st.markdown(
            f"""
            <div class="takeaway-card" style="border-top-color:{ORANGE};">
                <div class="takeaway-title" style="color:{DEEP_ORANGE};">2 · Trade Divergence (U.S. vs. Rest of World)</div>
                While U.S.-bound shipments changed <b>{us_yoy_all:+.1f}% YoY</b> ({us_now_all/1e6:.2f}M units), non-U.S. exports moved <b>{row_yoy_all:+.1f}% YoY</b> ({row_now_all/1e3:,.0f}k units), confirming Latin America and Europe as critical shock absorbers.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with tk3:
        if spotlight_brand != "None (Industry Overview)":
            sp_now = df_prod[(df_prod["ANIO"] == anchor_year) & (df_prod["MES_NUM"].isin(months_anchor)) & (df_prod["BRAND_CLEAN"] == spotlight_brand)]["UNI_VEH_PRODUCCION"].sum()
            sp_prev = df_prod[(df_prod["ANIO"] == prev_year) & (df_prod["MES_NUM"].isin(months_anchor)) & (df_prod["BRAND_CLEAN"] == spotlight_brand)]["UNI_VEH_PRODUCCION"].sum()
            sp_yoy = ((sp_now - sp_prev) / sp_prev * 100) if sp_prev > 0 else 0.0
            sp_share = (sp_now / p_now_all * 100) if p_now_all > 0 else 0.0
            st.markdown(
                f"""
                <div class="takeaway-card" style="border-top-color:{TEAL};">
                    <div class="takeaway-title" style="color:{TEAL};">3 · Spotlight: {short_brand(spotlight_brand)}</div>
                    Assembled <b>{sp_now:,.0f} units</b> in {period_label} (<b>{sp_yoy:+.1f}% YoY</b>), capturing <b>{sp_share:.1f}%</b> of total Mexican output across filtered segments.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="takeaway-card" style="border-top-color:{TEAL};">
                    <div class="takeaway-title" style="color:{TEAL};">3 · Two-Speed Segment Split</div>
                    <b>93.5% of Mexican-built SUVs</b> are exported abroad (highest tariff sensitivity), whereas <b>80.8% of Subcompacts</b> are sold domestically inside Mexico.
                </div>
                """,
                unsafe_allow_html=True,
            )

    with st.expander("⚠️ On-Screen Coverage, Panel Changes & Statistical Vintage Transparency (Click to expand)", expanded=False):
        st.markdown(
            """
            - **2026 Partial-Year Coverage:** Dataset covers **January–October 2026 (10 months)**. All 2026 comparisons match **Jan–Oct YTD** against **Jan–Oct of prior years** to prevent false seasonal drops.
            - **Statistical Status (`ESTATUS`):** `2005–2023` = *Definitive Figures*; `2024–Sep 2026` = *Revised Figures*; `Oct 2026` = *Preliminary Figures*.
            - **Non-Reporting Brands & Panel Scope:** Because RAIAVL is an administrative registry of AMIA-affiliated automakers and this dataset inner-joins Production, Exports, and Retail Sales, non-reporting Chinese brands (**BYD, MG, Chirey, Omoda, Geely**) and import-only brands without Mexican assembly plants are excluded.
            - **Heavy-Duty Pickup Lag:** GM Silverado 2500 / GMC Sierra and Stellantis RAM 2500 record export shipments in 2025–2026 from inventory/model-code splits against zero new production rows.
            """
        )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TOP-LINE KPI STRIP (BBOD Ch. 2, Ch. 5 & Ch. 33 CVD-Safe Directional Arrows)
    # --------------------------------------------------------------------------
    exp_ratio = (e_now_all / p_now_all * 100) if p_now_all > 0 else 0.0
    exp_yoy_all = ((e_now_all - e_prev_all) / e_prev_all * 100) if e_prev_all > 0 else 0.0
    us_share_now = (us_now_all / e_now_all * 100) if e_now_all > 0 else 0.0
    us_share_prev = (us_prev_all / e_prev_all * 100) if e_prev_all > 0 else 0.0
    us_share_pp = us_share_now - us_share_prev

    lt_now = df_prod[(df_prod["ANIO"] == anchor_year) & (df_prod["MES_NUM"].isin(months_anchor)) & (df_prod["SEGMENT_EN"].isin(["SUVs", "Pickups", "Minivans"]))]["UNI_VEH_PRODUCCION"].sum()
    lt_share_now = (lt_now / p_now_all * 100) if p_now_all > 0 else 0.0
    start_yr = year_range[0]
    p_start = df_prod[df_prod["ANIO"] == start_yr]["UNI_VEH_PRODUCCION"].sum()
    lt_start = df_prod[(df_prod["ANIO"] == start_yr) & (df_prod["SEGMENT_EN"].isin(["SUVs", "Pickups", "Minivans"]))]["UNI_VEH_PRODUCCION"].sum()
    lt_share_start = (lt_start / p_start * 100) if p_start > 0 else 0.0
    lt_pp = lt_share_now - lt_share_start

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        arrow = "▲" if p_yoy_all >= 0 else "▼"
        cls = "kpi-delta-pos" if p_yoy_all >= 0 else "kpi-delta-neg"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Assembly Output ({period_label})</div>
                <div class="kpi-value">{p_now_all/1e6:.2f}M</div>
                <div class="{cls}">{arrow} {p_yoy_all:+.1f}% vs. {prev_label} ({p_prev_all/1e6:.2f}M)</div>
                <div class="kpi-sub">Total filtered light vehicles assembled</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        arrow = "▲" if exp_yoy_all >= 0 else "▼"
        cls = "kpi-delta-pos" if exp_yoy_all >= 0 else "kpi-delta-neg"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Export Intensity ({period_label})</div>
                <div class="kpi-value">{exp_ratio:.1f}%</div>
                <div class="{cls}">{arrow} {exp_yoy_all:+.1f}% export volume YoY ({e_now_all/1e6:.2f}M)</div>
                <div class="kpi-sub">Share of Mexican assembly shipped abroad</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        arrow = "▲" if us_share_pp >= 0 else "▼"
        # Lower U.S. concentration reduces single-market risk, so shift is colored informatively
        cls = "kpi-delta-neg" if us_share_pp >= 0 else "kpi-delta-pos"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">U.S. Export Concentration</div>
                <div class="kpi-value">{us_share_now:.1f}%</div>
                <div class="{cls}">{arrow} {us_share_pp:+.1f} pp vs. {prev_label} ({us_share_prev:.1f}%)</div>
                <div class="kpi-sub">{us_now_all/1e6:.2f}M units shipped to U.S.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k4:
        arrow = "▲" if lt_pp >= 0 else "▼"
        cls = "kpi-delta-pos" if lt_pp >= 0 else "kpi-delta-neg"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Light-Truck & SUV Mix</div>
                <div class="kpi-value">{lt_share_now:.1f}%</div>
                <div class="{cls}">{arrow} {lt_pp:+.1f} pp since {start_yr} ({lt_share_start:.1f}%)</div>
                <div class="kpi-sub">Structural pivot from small cars to SUVs/Pickups</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:0.65rem'></div>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SIX NARRATIVE TABS (BBOD Architecture: Overview -> Peers -> Time -> Trade -> Domestic -> Simulator)
    # --------------------------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "1 · Executive Trajectory & 2026 Pace",
        "2 · Automaker Peers & Rank Shifts",
        "3 · Seasonality & Shock Matrix",
        "4 · Trade & U.S. Tariff Exposure",
        "5 · Domestic vs. Export Split",
        "6 · What-If Simulator & Explorer",
    ])

    # ==========================================================================
    # TAB 1: CUMULATIVE YTD INDEX (CH. 5 & CH. 31) + PACE CHART (CH. 7) + LONG RUN
    # ==========================================================================
    with tab1:
        col_ov_left, col_ov_right = st.columns([1.15, 1.0])

        with col_ov_left:
            # BBOD Chapter 5 (Fig. 5.1) & Chapter 31 (Fig. 31.30): Cumulative YTD Index Chart
            cum_df = (
                df_prod.groupby(["ANIO", "MES_NUM"])["UNI_VEH_PRODUCCION"]
                .sum()
                .reset_index()
                .sort_values(["ANIO", "MES_NUM"])
            )
            cum_df["CUM_UNITS"] = cum_df.groupby("ANIO")["UNI_VEH_PRODUCCION"].cumsum()

            fig_cum = go.Figure()
            highlight_years = {
                2026: (DEEP_ORANGE, 3.6, "2026 YTD (Tariff Shock)"),
                2025: (BLUE, 2.8, "2025"),
                2017: (TEAL, 2.2, "2017 Pre-COVID Peak"),
                2020: (DARK_INK, 2.0, "2020 COVID Shock"),
            }

            for yr in sorted(cum_df["ANIO"].unique()):
                sub_y = cum_df[cum_df["ANIO"] == yr]
                if yr in highlight_years:
                    col, w, lbl = highlight_years[yr]
                    fig_cum.add_trace(
                        go.Scatter(
                            x=[MONTH_SHORT[m - 1] for m in sub_y["MES_NUM"]],
                            y=sub_y["CUM_UNITS"],
                            mode="lines+markers" if yr == 2026 else "lines",
                            name=lbl,
                            line=dict(color=col, width=w, dash="dot" if yr == 2020 else "solid"),
                            marker=dict(size=6, color=col),
                            hovertemplate=f"<b>{lbl}</b><br>Through %{{x}}: %{{y:,.0f}} units<extra></extra>",
                        )
                    )
                    # Direct end-of-line label (BBOD Ch. 1 / Knaflic)
                    last_m = int(sub_y["MES_NUM"].iloc[-1])
                    last_v = sub_y["CUM_UNITS"].iloc[-1]
                    fig_cum.add_annotation(
                        x=MONTH_SHORT[last_m - 1],
                        y=last_v,
                        text=f" <b>{yr}</b> ({last_v/1e6:.2f}M)",
                        showarrow=False,
                        xanchor="left",
                        font=dict(size=10.5, color=col),
                    )
                else:
                    fig_cum.add_trace(
                        go.Scatter(
                            x=[MONTH_SHORT[m - 1] for m in sub_y["MES_NUM"]],
                            y=sub_y["CUM_UNITS"],
                            mode="lines",
                            name=str(yr),
                            line=dict(color="#E2E8F0", width=1.1),
                            showlegend=False,
                            hovertemplate=f"<b>{yr}</b><br>Through %{{x}}: %{{y:,.0f}} units<extra></extra>",
                        )
                    )

            style_bbod_chart(
                fig_cum,
                title="Cumulative YTD Pace: 2026 trails 2025 by 198k units through October",
                subtitle="Cumulative monthly light-vehicle assembly (Jan–Dec) across all years in window",
                y_title="Cumulative Vehicles Assembled",
                height=420,
                show_legend=False,
            )
            fig_cum.update_layout(margin=dict(r=85))
            st.plotly_chart(fig_cum, use_container_width=True)

        with col_ov_right:
            # BBOD Chapter 7 (Fig. 7.2 & Fig. 7.5): Seasonality-Adjusted Pace Chart
            # Compares Jan-Oct 2026 actuals as % of Full-Year 2025 vs. Expected Seasonal Pace (Jan-Oct 2025 / Full-Year 2025)
            p25_full_seg = df_prod[df_prod["ANIO"] == 2025].groupby("SEGMENT_EN")["UNI_VEH_PRODUCCION"].sum()
            p25_ytd_seg = df_prod[(df_prod["ANIO"] == 2025) & (df_prod["MES_NUM"].isin(months_anchor))].groupby("SEGMENT_EN")["UNI_VEH_PRODUCCION"].sum()
            p26_ytd_seg = df_prod[(df_prod["ANIO"] == 2026) & (df_prod["MES_NUM"].isin(months_anchor))].groupby("SEGMENT_EN")["UNI_VEH_PRODUCCION"].sum()

            pace_df = pd.DataFrame({
                "Full_2025": p25_full_seg,
                "YTD_2025": p25_ytd_seg,
                "YTD_2026": p26_ytd_seg,
            }).fillna(0)
            pace_df = pace_df[pace_df["Full_2025"] > 0].copy()
            pace_df["Actual_Pace_%"] = pace_df["YTD_2026"] / pace_df["Full_2025"] * 100
            pace_df["Expected_Pace_%"] = pace_df["YTD_2025"] / pace_df["Full_2025"] * 100
            pace_df["YoY_%"] = np.where(
                pace_df["YTD_2025"] > 0,
                (pace_df["YTD_2026"] - pace_df["YTD_2025"]) / pace_df["YTD_2025"] * 100,
                0,
            )
            pace_df = pace_df.sort_values("Actual_Pace_%", ascending=True)

            fig_pace = go.Figure()
            if not pace_df.empty:
                pace_colors = [
                    BLUE if r["YoY_%"] >= 1.0 else (GREY_CTX if r["YoY_%"] >= -2.5 else ORANGE)
                    for _, r in pace_df.iterrows()
                ]
                # Left-aligned Category + Value labels per BBOD Ch. 7 Fig. 7.5 (Steve Wexler eye-scan fix)
                y_labels = [
                    f"<b>{seg}</b><br><span style='font-size:10.5px; color:{SLATE_TEXT};'>{r['YTD_2026']/1e3:,.0f}k / {r['Full_2025']/1e3:,.0f}k</span>"
                    for seg, r in pace_df.iterrows()
                ]

                fig_pace.add_trace(
                    go.Bar(
                        y=y_labels,
                        x=pace_df["Actual_Pace_%"],
                        orientation="h",
                        marker_color=pace_colors,
                        width=0.52,
                        text=[f" {v:.1f}% ({yoy:+.1f}% YoY)" for v, yoy in zip(pace_df["Actual_Pace_%"], pace_df["YoY_%"])],
                        textposition="outside",
                        textfont=dict(size=11, color=DARK_INK),
                        name="Jan–Oct 2026 % of 2025 Full Year",
                        hovertemplate="<b>%{y}</b><br>2026 YTD Progress: %{x:.1f}% of 2025 Full Year<extra></extra>",
                    )
                )

                # Dotted vertical markers for Expected Seasonal Pace (Jan-Oct 2025 share of 2025)
                fig_pace.add_trace(
                    go.Scatter(
                        y=y_labels,
                        x=pace_df["Expected_Pace_%"],
                        mode="markers",
                        marker=dict(symbol="line-ns", size=22, line=dict(color=DARK_INK, width=2.5)),
                        name="Expected Seasonal Pace (Jan–Oct 2025)",
                        hovertemplate="Expected Seasonal Pace: %{x:.1f}%<extra></extra>",
                    )
                )

                # Solid vertical reference line at 100% (2025 Full-Year Target)
                fig_pace.add_vline(x=100, line_width=2, line_color=DARK_INK)
                fig_pace.add_annotation(
                    x=100, y=len(pace_df) - 0.42,
                    text="100% (2025 Full Year)", showarrow=False, xanchor="right", xshift=-4,
                    font=dict(size=10, color=DARK_INK),
                )

            style_bbod_chart(
                fig_pace,
                title="2026 Seasonal Pace Chart: Pickups beat pace; Compacts & SUVs lag",
                subtitle="Jan–Oct 2026 progress toward 2025 full-year volume (tick = expected seasonal pace)",
                height=420,
                show_legend=False,
            )
            fig_pace.update_layout(margin=dict(l=135, r=95, t=78, b=40))
            fig_pace.update_xaxes(range=[0, 122], ticksuffix="%", showgrid=True, gridcolor="#F1F5F9")
            fig_pace.update_yaxes(showgrid=False, linecolor="white")
            st.plotly_chart(fig_pace, use_container_width=True)

        # Full-Width Long-Run Structural Trajectory (2005–2026) with Historical Annotations
        piv_yr = df_prod.pivot_table(
            index="ANIO", columns="SEGMENT_EN", values="UNI_VEH_PRODUCCION",
            aggfunc="sum", fill_value=0
        ).sort_index()
        piv_full = piv_yr[piv_yr.index <= 2025].copy()
        has_2026 = (2026 in piv_yr.index) and (len(months_anchor) > 0)

        fig_long = go.Figure()
        if year_range[0] <= 2009 and year_range[1] >= 2008:
            fig_long.add_vrect(
                x0=2008.0, x1=2009.4, fillcolor=BG_SHADE, opacity=0.8, line_width=0,
                annotation_text="2008–09 GFC", annotation_position="top left",
                annotation_font=dict(size=10, color=SLATE_TEXT),
            )
        if year_range[0] <= 2022 and year_range[1] >= 2020:
            fig_long.add_vrect(
                x0=2019.7, x1=2022.3, fillcolor=BG_SHADE, opacity=0.85, line_width=0,
                annotation_text="COVID-19 (2020) & Chip Shortage (2021–22)", annotation_position="top left",
                annotation_font=dict(size=10.5, color=DARK_INK),
            )

        for seg in [s for s in ["SUVs", "Compacts", "Pickups", "Subcompacts", "Minivans"] if s in piv_full.columns]:
            if seg == "Minivans" and piv_full[seg].sum() == 0:
                continue
            is_suv = (seg == "SUVs")
            is_comp = (seg == "Compacts")
            col = BLUE if is_suv else (DARK_INK if is_comp else GREY_CTX)
            w = 3.5 if is_suv else (2.2 if is_comp else 1.6)

            fig_long.add_trace(
                go.Scatter(
                    x=piv_full.index,
                    y=piv_full[seg],
                    mode="lines+markers" if is_suv else "lines",
                    name=seg,
                    line=dict(color=col, width=w),
                    marker=dict(size=5.5, color=col),
                    hovertemplate=f"<b>{seg}</b><br>Year: %{{x}}<br>Units: %{{y:,.0f}}<extra></extra>",
                )
            )
            if has_2026 and (2025 in piv_full.index):
                n_m = len(df_prod[df_prod["ANIO"] == 2026]["MES_NUM"].unique())
                pace_26 = piv_yr.loc[2026, seg] * (12.0 / max(n_m, 1))
                val_25 = piv_full.loc[2025, seg]
                ytd_25 = df_prod[(df_prod["ANIO"] == 2025) & (df_prod["MES_NUM"] <= n_m) & (df_prod["SEGMENT_EN"] == seg)]["UNI_VEH_PRODUCCION"].sum()
                yoy_s = ((piv_yr.loc[2026, seg] - ytd_25) / ytd_25 * 100) if ytd_25 > 0 else 0.0
                p_col = ORANGE if seg in ["SUVs", "Compacts"] else GREY_CTX

                fig_long.add_trace(
                    go.Scatter(
                        x=[2025, 2026],
                        y=[val_25, pace_26],
                        mode="lines+markers",
                        name=f"{seg} (2026 Run-Rate)",
                        line=dict(color=p_col, width=w, dash="dash"),
                        marker=dict(size=6.5, color=p_col),
                        hovertemplate=f"<b>{seg} (2026 Annualized)</b><br>Run-rate: %{{y:,.0f}} ({yoy_s:+.1f}% YTD YoY)<extra></extra>",
                    )
                )
                fig_long.add_annotation(
                    x=2026.12, y=pace_26,
                    text=f"<b>{seg}</b> ({yoy_s:+.1f}% YTD)" if is_suv else f"{seg} ({yoy_s:+.1f}%)",
                    showarrow=False, xanchor="left",
                    font=dict(size=10.5, color=DEEP_ORANGE if is_suv else SLATE_TEXT),
                )

        if "SUVs" in piv_full.columns and 2018 in piv_full.index:
            fig_long.add_annotation(
                x=2018, y=piv_full.loc[2018, "SUVs"],
                text="<b>2018 Inflection:</b> SUVs surpass Compacts",
                showarrow=True, arrowhead=2, arrowcolor=BLUE, ax=-55, ay=-40,
                font=dict(size=10.5, color=BLUE),
            )
        if has_2026:
            fig_long.add_vline(x=2025.85, line_width=1.3, line_dash="dot", line_color=ORANGE)

        style_bbod_chart(
            fig_long,
            title="Two-Decade Structural Pivot: SUVs multiplied 27x (2005–2025) before 2026 tariff headwinds",
            subtitle="Annual light-vehicle assembly in Mexico by segment (dashed 2026 segment = Jan–Oct annualized run-rate)",
            y_title="Vehicles Assembled",
            height=410,
        )
        if has_2026:
            fig_long.update_xaxes(range=[year_range[0] - 0.3, 2028.6])
        fig_long.update_layout(margin=dict(r=135))
        st.plotly_chart(fig_long, use_container_width=True)

    # ==========================================================================
    # TAB 2: AUTOMAKER PEERS ("RANKING BY NOW, COMPARING WITH THEN", JITTERPLOT & BUMP CHART)
    # BBOD Chapter 3, Chapter 6, Chapter 10, Chapter 22 & Chapter 31
    # ==========================================================================
    with tab2:
        col_ctrl_t2, _ = st.columns([1.2, 2.0])
        with col_ctrl_t2:
            delta_metric_mode = st.radio(
                "YoY Comparison Scale (BBOD Ch. 6, p. 90):",
                options=["Percentage Change (% YoY)", "Unit Volume Difference (Units)"],
                horizontal=True,
            )

        # BBOD Chapter 6 ("Ranking by Now, Comparing with Then")
        b_now = df_prod[(df_prod["ANIO"] == anchor_year) & (df_prod["MES_NUM"].isin(months_anchor))].groupby("BRAND_CLEAN")["UNI_VEH_PRODUCCION"].sum()
        b_prev = df_prod[(df_prod["ANIO"] == prev_year) & (df_prod["MES_NUM"].isin(months_anchor))].groupby("BRAND_CLEAN")["UNI_VEH_PRODUCCION"].sum()

        rank_df = pd.DataFrame({"Now": b_now, "Prev": b_prev}).fillna(0)
        rank_df = rank_df[(rank_df["Now"] > 0) | (rank_df["Prev"] > 0)].copy()
        rank_df["Diff_Units"] = rank_df["Now"] - rank_df["Prev"]
        rank_df["Diff_Pct"] = np.where(rank_df["Prev"] > 0, rank_df["Diff_Units"] / rank_df["Prev"] * 100, np.nan)
        rank_df = rank_df.sort_values("Now", ascending=True)

        col_r1, col_r2 = st.columns([1.15, 1.0])

        with col_r1:
            fig_rank = make_subplots(
                rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.05,
                column_widths=[0.62, 0.38],
            )
            y_brands = [
                f"<b>{short_brand(b)}</b>" if b == spotlight_brand else short_brand(b)
                for b in rank_df.index
            ]

            bar_cols_now = [
                BLUE if b == spotlight_brand else (TEAL if d >= 0 else LIGHT_GREY)
                for b, d in zip(rank_df.index, rank_df["Diff_Units"])
            ]

            # Left panel: Current magnitude bars + Vertical tick marks for Prior Year ("Then")
            fig_rank.add_trace(
                go.Bar(
                    y=y_brands,
                    x=rank_df["Now"],
                    orientation="h",
                    marker_color=bar_cols_now,
                    name=period_label,
                    text=[f" {v/1e3:,.0f}k" for v in rank_df["Now"]],
                    textposition="outside",
                    textfont=dict(size=10.5, color=DARK_INK),
                    hovertemplate="<b>%{y}</b><br>" + period_label + ": %{x:,.0f}<extra></extra>",
                ),
                row=1, col=1,
            )
            fig_rank.add_trace(
                go.Scatter(
                    y=y_brands,
                    x=rank_df["Prev"],
                    mode="markers",
                    marker=dict(symbol="line-ns", size=18, line=dict(color=DARK_INK, width=2.2)),
                    name=prev_label,
                    hovertemplate="<b>%{y}</b><br>" + prev_label + ": %{x:,.0f}<extra></extra>",
                ),
                row=1, col=1,
            )

            # Right panel: Aligned YoY Delta (% or Units)
            if delta_metric_mode == "Percentage Change (% YoY)":
                delta_vals = rank_df["Diff_Pct"].fillna(0)
                delta_txt = [f"{v:+.1f}%" if not np.isnan(raw_v) else "New" for v, raw_v in zip(delta_vals, rank_df["Diff_Pct"])]
                x2_title = f"YoY % vs {prev_label}"
            else:
                delta_vals = rank_df["Diff_Units"]
                delta_txt = [f"{v/1e3:+.1f}k" for v in delta_vals]
                x2_title = f"Unit Delta vs {prev_label}"

            delta_cols = [
                BLUE if b == spotlight_brand else (TEAL if v >= 0 else ORANGE)
                for b, v in zip(rank_df.index, delta_vals)
            ]

            fig_rank.add_trace(
                go.Bar(
                    y=y_brands,
                    x=delta_vals,
                    orientation="h",
                    marker_color=delta_cols,
                    text=delta_txt,
                    textposition="outside",
                    textfont=dict(size=10.5, color=DARK_INK),
                    showlegend=False,
                    hovertemplate="<b>%{y}</b><br>Change: %{text}<extra></extra>",
                ),
                row=1, col=2,
            )

            fig_rank.update_layout(
                title=dict(
                    text=(
                        f"<span style='font-size:16px; font-weight:700; color:{DARK_INK};'>"
                        f"Ranking by Now ({period_label}), Comparing with Then ({prev_label})</span>"
                        f"<br><span style='font-size:12px; color:{SLATE_TEXT};'>"
                        f"Left: Assembly volume (vertical tick = {prev_label}) · Right: YoY change (Teal = growth, Orange = contraction)</span>"
                    ),
                    x=0.0, y=0.97,
                ),
                height=460,
                margin=dict(l=125, r=45, t=78, b=42),
                plot_bgcolor="white",
                paper_bgcolor="white",
                showlegend=False,
            )
            max_now = rank_df["Now"].max() if len(rank_df) else 100
            fig_rank.update_xaxes(range=[0, max_now * 1.24], showgrid=True, gridcolor="#F1F5F9", row=1, col=1)
            d_min = min(delta_vals.min() * 1.38, -10) if len(delta_vals) else -20
            d_max = max(delta_vals.max() * 1.38, 10) if len(delta_vals) else 20
            fig_rank.update_xaxes(range=[d_min, d_max], title_text=x2_title, showgrid=True, gridcolor="#F1F5F9", row=1, col=2)
            fig_rank.update_yaxes(showgrid=False, linecolor="white", tickfont=dict(color=DARK_INK, size=11))
            st.plotly_chart(fig_rank, use_container_width=True)

        with col_r2:
            # BBOD Chapter 3 ("Comparing Individual Performance with Peers"): Normalized Peer Strip Plot
            # Metrics across brands in anchor_year (Jan-Oct matched): Volume, Export %, US Share %, SUV/LightTruck %
            p_b = df_prod[(df_prod["ANIO"] == anchor_year) & (df_prod["MES_NUM"].isin(months_anchor))].groupby("BRAND_CLEAN")["UNI_VEH_PRODUCCION"].sum()
            e_b = df_exp[(df_exp["ANIO"] == anchor_year) & (df_exp["MES_NUM"].isin(months_anchor))].groupby("BRAND_CLEAN")["UNI_VEH_EXPORTACION"].sum()
            us_b = df_exp[(df_exp["ANIO"] == anchor_year) & (df_exp["MES_NUM"].isin(months_anchor)) & (df_exp["DEST_EN"] == "United States")].groupby("BRAND_CLEAN")["UNI_VEH_EXPORTACION"].sum()
            lt_b = df_prod[(df_prod["ANIO"] == anchor_year) & (df_prod["MES_NUM"].isin(months_anchor)) & (df_prod["SEGMENT_EN"].isin(["SUVs", "Pickups", "Minivans"]))].groupby("BRAND_CLEAN")["UNI_VEH_PRODUCCION"].sum()

            peer_df = pd.DataFrame({"Prod": p_b, "Exp": e_b, "US": us_b, "LT": lt_b}).fillna(0)
            peer_df = peer_df[peer_df["Prod"] > 0].copy()
            peer_df["Export_Rate_%"] = np.clip(peer_df["Exp"] / peer_df["Prod"] * 100, 0, 100)
            peer_df["US_Share_%"] = np.where(peer_df["Exp"] > 0, peer_df["US"] / peer_df["Exp"] * 100, 0)
            peer_df["LightTruck_Mix_%"] = peer_df["LT"] / peer_df["Prod"] * 100

            metrics_list = ["Export_Rate_%", "US_Share_%", "LightTruck_Mix_%"]
            metric_labels = ["Export Share (%)", "U.S. Export Share (%)", "SUV & Light-Truck Mix (%)"]

            fig_peer = go.Figure()
            np.random.seed(42)
            for idx_m, (col_m, lbl_m) in enumerate(zip(metrics_list, metric_labels)):
                vals = peer_df[col_m]
                q25, med, q75 = np.percentile(vals, [25, 50, 75]) if len(vals) > 0 else (0, 50, 100)

                # Interquartile shaded band (BBOD Ch. 3 Fig. 3.4)
                fig_peer.add_shape(
                    type="rect",
                    x0=idx_m - 0.28, x1=idx_m + 0.28,
                    y0=q25, y1=q75,
                    fillcolor="#E2E8F0", opacity=0.65, line_width=0,
                    layer="below",
                )
                # Median line
                fig_peer.add_shape(
                    type="line",
                    x0=idx_m - 0.30, x1=idx_m + 0.30,
                    y0=med, y1=med,
                    line=dict(color=DARK_INK, width=2, dash="dot"),
                )

                # Peer dots (jittered horizontally)
                others = peer_df[peer_df.index != spotlight_brand]
                jitter = np.random.uniform(-0.14, 0.14, size=len(others))
                fig_peer.add_trace(
                    go.Scatter(
                        x=np.full(len(others), idx_m) + jitter,
                        y=others[col_m],
                        mode="markers",
                        name="Peer Automakers" if idx_m == 0 else None,
                        showlegend=(idx_m == 0),
                        marker=dict(color=GREY_CTX, size=10, opacity=0.78, line=dict(color="white", width=1)),
                        text=[short_brand(b) for b in others.index],
                        hovertemplate=f"<b>%{{text}}</b><br>{lbl_m}: %{{y:.1f}}%<extra></extra>",
                    )
                )

                # Spotlight brand dot (centered, bold Blue)
                if spotlight_brand != "None (Industry Overview)" and spotlight_brand in peer_df.index:
                    sp_v = peer_df.loc[spotlight_brand, col_m]
                    fig_peer.add_trace(
                        go.Scatter(
                            x=[idx_m],
                            y=[sp_v],
                            mode="markers+text",
                            name=short_brand(spotlight_brand) if idx_m == 0 else None,
                            showlegend=(idx_m == 0),
                            marker=dict(color=BLUE, size=15, line=dict(color="white", width=2)),
                            text=[f"<b>{sp_v:.0f}%</b>"],
                            textposition="top center",
                            textfont=dict(size=11, color=BLUE),
                            hovertemplate=f"<b>{short_brand(spotlight_brand)}</b><br>{lbl_m}: %{{y:.1f}}%<extra></extra>",
                        )
                    )

            sp_sub = (
                f"Blue = <b>{short_brand(spotlight_brand)}</b> vs. peers (grey) · Shaded box = 25th–75th percentile"
                if spotlight_brand != "None (Industry Overview)"
                else "Select a 'Spotlight Automaker' in sidebar to highlight · Shaded box = IQR, dotted = median"
            )
            style_bbod_chart(
                fig_peer,
                title=f"Peer Structural Benchmark ({period_label})",
                subtitle=sp_sub,
                y_title="Percentage (%)",
                height=460,
                show_legend=False,
            )
            fig_peer.update_xaxes(
                tickvals=[0, 1, 2],
                ticktext=metric_labels,
                range=[-0.5, 2.5],
            )
            fig_peer.update_yaxes(range=[-5, 108])
            st.plotly_chart(fig_peer, use_container_width=True)

        # BBOD Chapter 22 & Chapter 31: Automaker Production Rank Bump Chart (2010–2026)
        bump_start = max(year_range[0], 2010)
        bump_df = df_prod[df_prod["ANIO"] >= bump_start].pivot_table(
            index="ANIO", columns="BRAND_CLEAN", values="UNI_VEH_PRODUCCION", aggfunc="sum", fill_value=0
        )
        if len(bump_df) >= 2:
            # Rank 1 = highest assembly volume in each year
            ranks_df = bump_df.rank(axis=1, ascending=False, method="min")
            # Keep brands active in recent years
            active_brands = [b for b in ranks_df.columns if bump_df[b].max() > 0]
            ranks_df = ranks_df[active_brands]

            fig_bump = go.Figure()
            default_highlights = {"KIA", "Volkswagen", "Nissan"} if spotlight_brand == "None (Industry Overview)" else {spotlight_brand}

            for b in active_brands:
                is_hi = b in default_highlights
                if b == spotlight_brand:
                    col = BLUE
                    w = 3.6
                elif b == "KIA" and spotlight_brand == "None (Industry Overview)":
                    col = TEAL
                    w = 2.8
                elif b == "Volkswagen" and spotlight_brand == "None (Industry Overview)":
                    col = BLUE
                    w = 2.8
                elif b == "Nissan" and spotlight_brand == "None (Industry Overview)":
                    col = ORANGE
                    w = 2.6
                else:
                    col = "#CBD5E1"
                    w = 1.4

                s_ranks = ranks_df[b].where(bump_df[b] > 0, np.nan)
                fig_bump.add_trace(
                    go.Scatter(
                        x=s_ranks.index,
                        y=s_ranks.values,
                        mode="lines+markers" if is_hi else "lines",
                        name=short_brand(b),
                        line=dict(color=col, width=w),
                        marker=dict(size=7, color=col),
                        hovertemplate=f"<b>{short_brand(b)}</b><br>Year: %{{x}}<br>Rank: #%{{y:.0f}}<extra></extra>",
                    )
                )
                # Label start and end ranks for highlighted brands (and end rank for all)
                valid_idx = s_ranks.dropna().index
                if len(valid_idx) > 0:
                    last_y = valid_idx[-1]
                    last_r = s_ranks.loc[last_y]
                    fig_bump.add_annotation(
                        x=last_y + 0.15,
                        y=last_r,
                        text=f"<b>#{int(last_r)} {short_brand(b)}</b>" if is_hi else f"#{int(last_r)} {short_brand(b)}",
                        showarrow=False,
                        xanchor="left",
                        font=dict(size=10.5 if is_hi else 9.5, color=col if is_hi else SLATE_TEXT),
                    )

            style_bbod_chart(
                fig_bump,
                title="Automaker Production Rank Evolution: Asian entrants climbed while legacy rankings shifted",
                subtitle="Annual rank by Mexican assembly volume (#1 = top producer; 2026 based on Jan–Oct YTD)",
                y_title="Industry Rank (#1 = Highest)",
                height=400,
                zero_y=False,
            )
            fig_bump.update_yaxes(autorange="reversed", dtick=1, range=[len(active_brands) + 0.6, 0.4])
            fig_bump.update_xaxes(range=[bump_start - 0.3, year_range[1] + 2.3], dtick=2)
            fig_bump.update_layout(margin=dict(r=145))
            st.plotly_chart(fig_bump, use_container_width=True)

    # ==========================================================================
    # TAB 3: SEASONALITY & SHOCK MATRIX (BBOD CH. 31 LABELED HIGHLIGHT TABLE)
    # ==========================================================================
    with tab3:
        st.markdown(
            """
            <div class="insight-callout">
            <b>Why a Labeled Highlight Table (BBOD Ch. 31, pp. 362–367):</b> Standard time-series lines obscure two-dimensional patterns. Reading <b>down each column</b> exposes multi-year secular expansion, while reading <b>across each row</b> reveals recurring monthly seasonality (April/May holiday dips, December plant retooling troughs) and exact shock troughs (April–May 2020 COVID freeze and 2026 tariff softening).
            </div>
            """,
            unsafe_allow_html=True,
        )

        hm_metric = st.radio(
            "Select Matrix Metric:",
            options=["Assembly Production (Thousands)", "Exports Shipped Abroad (Thousands)", "Domestic Retail Sales (Thousands)"],
            horizontal=True,
        )

        if hm_metric == "Assembly Production (Thousands)":
            hm_src = df_prod.groupby(["ANIO", "MES_NUM"])["UNI_VEH_PRODUCCION"].sum().unstack(fill_value=np.nan) / 1000.0
        elif hm_metric == "Exports Shipped Abroad (Thousands)":
            hm_src = df_exp.groupby(["ANIO", "MES_NUM"])["UNI_VEH_EXPORTACION"].sum().unstack(fill_value=np.nan) / 1000.0
        else:
            hm_src = df_sales.groupby(["ANIO", "MES_NUM"])["UNI_VEH_VENTAS"].sum().unstack(fill_value=np.nan) / 1000.0

        hm_src = hm_src.reindex(columns=range(1, 13))
        hm_src.columns = MONTH_SHORT
        hm_src = hm_src.sort_index(ascending=False)

        text_matrix = np.where(np.isnan(hm_src.values), "—", np.vectorize(lambda x: f"{x:,.0f}")(hm_src.values))

        fig_hm = go.Figure(
            data=go.Heatmap(
                z=hm_src.values,
                x=hm_src.columns,
                y=hm_src.index.astype(str),
                text=text_matrix,
                texttemplate="%{text}",
                textfont=dict(size=10.5),
                colorscale=[
                    [0.0, "#F8FAFC"],
                    [0.25, "#DBEAFE"],
                    [0.55, "#60A5FA"],
                    [0.85, "#1D4ED8"],
                    [1.0, "#1E3A8A"],
                ],
                colorbar=dict(title="Units (k)", thickness=12),
                hovertemplate="<b>%{y} · %{x}</b><br>Volume: %{z:,.1f}k units<extra></extra>",
            )
        )
        fig_hm.update_layout(
            title=dict(
                text=(
                    f"<span style='font-size:16.5px; font-weight:700; color:{DARK_INK};'>"
                    f"{hm_metric} across Year × Month (2005–2026)</span>"
                    f"<br><span style='font-size:12px; color:{SLATE_TEXT};'>"
                    "Darker blue = higher monthly volume · Notice the Apr–May 2020 COVID freeze and Dec retooling dips</span>"
                ),
                x=0.0, y=0.98,
            ),
            height=540,
            margin=dict(l=60, r=30, t=78, b=40),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        fig_hm.update_xaxes(side="top", tickfont=dict(color=DARK_INK, size=11.5))
        fig_hm.update_yaxes(type="category", tickfont=dict(color=DARK_INK, size=11))
        st.plotly_chart(fig_hm, use_container_width=True)

        # Monthly YoY % Growth Tracker for 2026 vs 2025
        m25 = df_prod[df_prod["ANIO"] == 2025].groupby("MES_NUM")["UNI_VEH_PRODUCCION"].sum()
        m26 = df_prod[df_prod["ANIO"] == 2026].groupby("MES_NUM")["UNI_VEH_PRODUCCION"].sum()
        if not m26.empty and not m25.empty:
            yoy_m = ((m26 - m25.reindex(m26.index)) / m25.reindex(m26.index) * 100).dropna()
            fig_myoy = go.Figure(
                go.Bar(
                    x=[MONTH_SHORT[int(m) - 1] for m in yoy_m.index],
                    y=yoy_m.values,
                    marker_color=[TEAL if v >= 0 else ORANGE for v in yoy_m.values],
                    text=[f"{v:+.1f}%" for v in yoy_m.values],
                    textposition="outside",
                    textfont=dict(size=11, color=DARK_INK),
                    hovertemplate="<b>%{x} 2026 vs. 2025</b><br>YoY Change: %{y:+.1f}%<extra></extra>",
                )
            )
            style_bbod_chart(
                fig_myoy,
                title="2026 Monthly YoY Trajectory: Contraction deepened after Q1 tariff implementation",
                subtitle="Month-over-same-month-prior-year assembly growth (%) in 2026 vs. 2025",
                y_title="YoY Change (%)",
                height=340,
                zero_y=False,
            )
            ymin = min(yoy_m.min() * 1.35, -10)
            ymax = max(yoy_m.max() * 1.35, 10)
            fig_myoy.update_yaxes(range=[ymin, ymax])
            st.plotly_chart(fig_myoy, use_container_width=True)

    # ==========================================================================
    # TAB 4: TRADE & U.S. TARIFF EXPOSURE
    # ==========================================================================
    with tab4:
        st.markdown(
            f"""
            <div class="insight-callout">
            <b>Trade Exposure Diagnosis:</b> U.S. export share rose from <b>62.5% in 2011</b> to <b>79.9% in 2025</b>, leaving Mexican assembly plants highly sensitive to U.S. tariff policy. In <b>{period_label}</b>, U.S.-bound shipments changed <b>{us_yoy_all:+.1f}% YoY</b>, while non-U.S. shipments moved <b>{row_yoy_all:+.1f}% YoY</b>.
            </div>
            """,
            unsafe_allow_html=True,
        )

        exp_clean = df_exp.copy()
        exp_clean["DEST_GROUP"] = np.where(exp_clean["DEST_EN"] == "United States", "United States", "Rest of World")
        exp_yr = exp_clean[exp_clean["ANIO"] <= 2025].pivot_table(
            index="ANIO", columns="DEST_GROUP", values="UNI_VEH_EXPORTACION", aggfunc="sum", fill_value=0
        )
        for c in ["United States", "Rest of World"]:
            if c not in exp_yr.columns:
                exp_yr[c] = 0
        exp_yr["Total"] = exp_yr["United States"] + exp_yr["Rest of World"]
        exp_yr["US_Share"] = np.where(exp_yr["Total"] > 0, exp_yr["United States"] / exp_yr["Total"] * 100, 0)

        fig_trade = make_subplots(
            rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.09, row_heights=[0.62, 0.38]
        )
        fig_trade.add_trace(
            go.Bar(x=exp_yr.index, y=exp_yr["United States"], name="United States", marker_color=BLUE),
            row=1, col=1,
        )
        fig_trade.add_trace(
            go.Bar(x=exp_yr.index, y=exp_yr["Rest of World"], name="Rest of World", marker_color=LIGHT_BLUE),
            row=1, col=1,
        )
        fig_trade.add_trace(
            go.Scatter(
                x=exp_yr.index, y=exp_yr["US_Share"], mode="lines+markers",
                name="U.S. Share (%)", line=dict(color=DEEP_ORANGE, width=2.8), marker=dict(size=6, color=DEEP_ORANGE),
            ),
            row=2, col=1,
        )
        fig_trade.update_layout(
            barmode="stack",
            title=dict(
                text=(
                    f"<span style='font-size:16.5px; font-weight:700; color:{DARK_INK};'>"
                    "Single-Market Concentration: U.S. export share climbed to ~80% by 2025</span>"
                    f"<br><span style='font-size:12px; color:{SLATE_TEXT};'>"
                    "Top: Annual export volume by destination group (2005–2025) · Bottom: U.S. share of total exports (%)</span>"
                ),
                x=0.0, y=0.97,
            ),
            height=450,
            margin=dict(l=60, r=30, t=80, b=40),
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
            hovermode="x unified",
        )
        fig_trade.update_xaxes(showgrid=False, linecolor=LIGHT_GREY)
        fig_trade.update_yaxes(title_text="Exported Units", showgrid=True, gridcolor="#F1F5F9", rangemode="tozero", row=1, col=1)
        fig_trade.update_yaxes(title_text="U.S. Share (%)", showgrid=True, gridcolor="#F1F5F9", range=[0, 100], row=2, col=1)
        st.plotly_chart(fig_trade, use_container_width=True)

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            non_us = (
                df_exp[df_exp["DEST_EN"] != "United States"]
                .groupby("DEST_EN")["UNI_VEH_EXPORTACION"]
                .sum()
                .sort_values(ascending=True)
                .tail(10)
            )
            fig_nonus = go.Figure(
                go.Bar(
                    x=non_us.values,
                    y=non_us.index,
                    orientation="h",
                    marker_color=[TEAL if c in ["Canada", "Germany", "Brazil"] else LIGHT_GREY for c in non_us.index],
                    text=[f" {v/1e6:.2f}M" if v >= 1e6 else f" {v/1e3:,.0f}k" for v in non_us.values],
                    textposition="outside",
                    textfont=dict(size=10.5, color=DARK_INK),
                )
            )
            style_bbod_chart(
                fig_nonus,
                title="Canada, Germany & Brazil anchor non-U.S. exports",
                subtitle="Top 10 secondary export markets (cumulative units in filtered window)",
                height=390,
            )
            fig_nonus.update_layout(margin=dict(l=110, r=55, t=75, b=30))
            fig_nonus.update_xaxes(visible=False, range=[0, non_us.max() * 1.24 if len(non_us) else 10])
            fig_nonus.update_yaxes(showgrid=False, linecolor="white")
            st.plotly_chart(fig_nonus, use_container_width=True)

        with col_d2:
            ytd_d = df_exp[df_exp["ANIO"].isin([prev_year, anchor_year]) & df_exp["MES_NUM"].isin(months_anchor)].pivot_table(
                index="DEST_EN", columns="ANIO", values="UNI_VEH_EXPORTACION", aggfunc="sum", fill_value=0
            )
            if prev_year in ytd_d.columns and anchor_year in ytd_d.columns:
                ytd_d = ytd_d[ytd_d[prev_year] >= 5000].copy()
                ytd_d["YoY_%"] = (ytd_d[anchor_year] - ytd_d[prev_year]) / ytd_d[prev_year] * 100
                ytd_d = ytd_d.sort_values("YoY_%")

                fig_dyoy = go.Figure(
                    go.Bar(
                        x=ytd_d["YoY_%"],
                        y=ytd_d.index,
                        orientation="h",
                        marker_color=[ORANGE if v < 0 else TEAL for v in ytd_d["YoY_%"]],
                        text=[f" {v:+.1f}%" for v in ytd_d["YoY_%"]],
                        textposition="outside",
                        textfont=dict(size=10.5, color=DARK_INK),
                    )
                )
                style_bbod_chart(
                    fig_dyoy,
                    title=f"{period_label} vs. {prev_label}: LatAm & Germany grew while U.S. fell",
                    subtitle="YoY export growth (%) for destination markets with ≥5,000 units",
                    height=390,
                    zero_y=False,
                )
                fig_dyoy.update_layout(margin=dict(l=115, r=55, t=75, b=30))
                xmin = min(ytd_d["YoY_%"].min() * 1.38, -15) if len(ytd_d) else -20
                xmax = max(ytd_d["YoY_%"].max() * 1.38, 15) if len(ytd_d) else 20
                fig_dyoy.update_xaxes(visible=False, range=[xmin, xmax])
                fig_dyoy.update_yaxes(showgrid=False, linecolor="white")
                st.plotly_chart(fig_dyoy, use_container_width=True)

    # ==========================================================================
    # TAB 5: DOMESTIC MARKET VS. EXPORTS (TWO-SPEED INDUSTRY)
    # ==========================================================================
    with tab5:
        st.markdown(
            """
            <div class="insight-callout">
            <b>Two-Speed Structural Divide:</b> Crossing RAIAVL Production, Exports, and Retail Sales proves that Mexican plants operate on two distinct tracks: <b>SUVs are 93.5% export-oriented</b>, whereas <b>Subcompacts rely 80.8% on domestic Mexican buyers</b>.
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            e_seg = df_exp[df_exp["ANIO"] == 2025].groupby("SEGMENT_EN")["UNI_VEH_EXPORTACION"].sum()
            s_seg = df_sales[(df_sales["ANIO"] == 2025) & (df_sales["ORIGIN_TYPE_EN"] == "Domestic (Made in Mexico)")].groupby("SEGMENT_EN")["UNI_VEH_VENTAS"].sum()
            alloc = pd.DataFrame({"Exported": e_seg, "Domestic": s_seg}).fillna(0)
            alloc = alloc[alloc.sum(axis=1) > 0]
            alloc_pct = alloc.div(alloc.sum(axis=1), axis=0) * 100
            alloc_pct = alloc_pct.sort_values("Exported", ascending=True)

            fig_al = go.Figure()
            fig_al.add_trace(
                go.Bar(
                    y=alloc_pct.index, x=alloc_pct["Exported"], name="Exported Abroad (%)",
                    orientation="h", marker_color=BLUE,
                    text=[f"{v:.1f}%" for v in alloc_pct["Exported"]],
                    textposition="inside", insidetextanchor="middle",
                    textfont=dict(color="white", size=11.5),
                )
            )
            fig_al.add_trace(
                go.Bar(
                    y=alloc_pct.index, x=alloc_pct["Domestic"], name="Sold in Mexico (%)",
                    orientation="h", marker_color=LIGHT_GREY,
                    text=[f"{v:.1f}%" if v >= 10 else "" for v in alloc_pct["Domestic"]],
                    textposition="inside", insidetextanchor="middle",
                    textfont=dict(color=DARK_INK, size=11.5),
                )
            )
            fig_al.update_layout(barmode="stack")
            style_bbod_chart(
                fig_al,
                title="93.5% of SUVs go abroad; 80.8% of Subcompacts stay in Mexico",
                subtitle="2025 destination split (%) of Mexican-assembled model lines",
                height=400,
                show_legend=True,
            )
            fig_al.update_layout(
                margin=dict(l=105, r=25, t=80, b=35),
                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
            )
            fig_al.update_xaxes(visible=False, range=[0, 100])
            fig_al.update_yaxes(showgrid=False, linecolor="white")
            st.plotly_chart(fig_al, use_container_width=True)

        with col_s2:
            sales_yr = df_sales[df_sales["ANIO"] <= 2025].pivot_table(
                index="ANIO", columns="ORIGIN_TYPE_EN", values="UNI_VEH_VENTAS", aggfunc="sum", fill_value=0
            )
            fig_dom = go.Figure()
            if "Domestic (Made in Mexico)" in sales_yr.columns:
                fig_dom.add_trace(
                    go.Bar(x=sales_yr.index, y=sales_yr["Domestic (Made in Mexico)"], name="Made in Mexico (NACIONAL)", marker_color=GREY_CTX)
                )
            if "Imported Supplement" in sales_yr.columns:
                fig_dom.add_trace(
                    go.Bar(x=sales_yr.index, y=sales_yr["Imported Supplement"], name="Imported Supplement (Japan/China/US/Korea)", marker_color=ORANGE)
                )
            fig_dom.update_layout(barmode="stack")
            style_bbod_chart(
                fig_dom,
                title="Domestic retail volume of registry lines remains below 2016 peak",
                subtitle="Annual Mexican retail sales of locally assembled model lines by origin (2005–2025)",
                y_title="Domestic Retail Units",
                height=400,
                show_legend=True,
            )
            fig_dom.update_layout(
                margin=dict(r=25, b=40),
                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
            )
            st.plotly_chart(fig_dom, use_container_width=True)

    # ==========================================================================
    # TAB 6: WHAT-IF POLICY SIMULATOR (CH. 4), DATA GOVERNANCE & AD-HOC EXPLORER (CH. 32 & 36)
    # ==========================================================================
    with tab6:
        st.markdown("### 1. Interactive 2026–2027 Tariff & Diversification Simulator (BBOD Ch. 4)")
        st.caption(
            "Model how U.S. tariff shocks, USMCA Regional Value Content (RVC) compliance, and non-U.S. trade corridor expansion impact annual Mexican vehicle demand (anchored on 2025 full-year baseline)."
        )

        sim_c1, sim_c2, sim_c3, sim_c4 = st.columns(4)
        with sim_c1:
            us_tariff_shock = st.slider("U.S. Tariff Demand Shock (%)", min_value=-30, max_value=0, value=-12, step=1)
        with sim_c2:
            rvc_shield = st.slider("USMCA RVC Tariff Shield (%)", min_value=0, max_value=100, value=55, step=5,
                                   help="Share of U.S.-bound vehicles meeting strict USMCA regional content rules and exempted from tariffs.")
        with sim_c3:
            row_growth = st.slider("LatAm & EU Export Expansion (%)", min_value=-10, max_value=40, value=12, step=2)
        with sim_c4:
            dom_growth = st.slider("Domestic Absorption Growth (%)", min_value=-10, max_value=30, value=6, step=2)

        # Compute baseline 2025 flows from filtered dataset
        base_us = df_exp[(df_exp["ANIO"] == 2025) & (df_exp["DEST_EN"] == "United States")]["UNI_VEH_EXPORTACION"].sum()
        base_row = df_exp[(df_exp["ANIO"] == 2025) & (df_exp["DEST_EN"] != "United States")]["UNI_VEH_EXPORTACION"].sum()
        base_dom = df_sales[(df_sales["ANIO"] == 2025) & (df_sales["ORIGIN_TYPE_EN"] == "Domestic (Made in Mexico)")]["UNI_VEH_VENTAS"].sum()
        base_total = base_us + base_row + base_dom

        unshielded_share = (100.0 - rvc_shield) / 100.0
        delta_us = base_us * unshielded_share * (us_tariff_shock / 100.0)
        delta_row = base_row * (row_growth / 100.0)
        delta_dom = base_dom * (dom_growth / 100.0)
        projected_total = base_total + delta_us + delta_row + delta_dom
        net_delta = projected_total - base_total

        sc_left, sc_right = st.columns([1.3, 1.0])
        with sc_left:
            # BBOD Chapter 24 Waterfall Chart showing net volume bridge
            fig_wf = go.Figure(
                go.Waterfall(
                    orientation="v",
                    measure=["absolute", "relative", "relative", "relative", "total"],
                    x=["2025 Baseline", "Unshielded U.S.<br>Tariff Loss", "LatAm & EU<br>Diversification", "Domestic Market<br>Absorption", "Projected<br>Annual Volume"],
                    y=[base_total, delta_us, delta_row, delta_dom, projected_total],
                    text=[
                        f"{base_total/1e6:.2f}M",
                        f"{delta_us/1e3:+,.0f}k",
                        f"{delta_row/1e3:+,.0f}k",
                        f"{delta_dom/1e3:+,.0f}k",
                        f"{projected_total/1e6:.2f}M",
                    ],
                    textposition="outside",
                    connector=dict(line=dict(color=LIGHT_GREY, width=1.2)),
                    decreasing=dict(marker=dict(color=ORANGE)),
                    increasing=dict(marker=dict(color=TEAL)),
                    totals=dict(marker=dict(color=BLUE)),
                )
            )
            style_bbod_chart(
                fig_wf,
                title=f"Scenario Impact Bridge: Net change of {net_delta:+,.0f} vehicles ({net_delta/max(base_total,1)*100:+.1f}%)",
                subtitle="Simulated annual volume impact across U.S. tariff exposure, RVC shield, and diversification levers",
                y_title="Vehicles (Units)",
                height=380,
            )
            fig_wf.update_yaxes(range=[0, max(base_total, projected_total) * 1.18 if base_total > 0 else 10])
            st.plotly_chart(fig_wf, use_container_width=True)

        with sc_right:
            st.markdown(
                f"""
                <div class="kpi-card" style="border-left:4px solid {BLUE}; margin-bottom:0.65rem;">
                    <div class="kpi-label">1 · USMCA Regional Value Content (RVC) Shield</div>
                    <div style="font-size:0.88rem; color:{DARK_INK};">
                    At <b>{rvc_shield}% RVC compliance</b>, U.S. tariff losses are contained to <b>{delta_us:,.0f} units</b>. Accelerating Tier-1/Tier-2 battery, aluminum, and powertrain localization in Nuevo León, Coahuila, and Guanajuato protects Mexico's core SUV export franchise.
                    </div>
                </div>
                <div class="kpi-card" style="border-left:4px solid {TEAL}; margin-bottom:0.65rem;">
                    <div class="kpi-label">2 · Non-U.S. Corridor Offtake</div>
                    <div style="font-size:0.88rem; color:{DARK_INK};">
                    A <b>{row_growth:+d}% expansion</b> across Canada, Germany, Brazil, Colombia, and Chile adds <b>{delta_row:+,.0f} units</b>—offsetting {abs(delta_row/min(delta_us, -1))*100:.0f}% of the unshielded U.S. tariff shock.
                    </div>
                </div>
                <div class="kpi-card" style="border-left:4px solid {ORANGE};">
                    <div class="kpi-label">3 · Registry Governance & Chinese Brand Blind Spot</div>
                    <div style="font-size:0.88rem; color:{DARK_INK};">
                    Secretaría de Economía and INEGI should mandate customs-linked monthly reporting for non-AMIA import brands (<b>BYD, MG, Chirey, Geely</b>) and unify model IDs across RAIAVL Production and Export tables.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        # BBOD Chapter 32 ("Beware the Dead-End Dashboard") & Chapter 36 ("Journey into the Unknown"):
        # Underlying Model-Level Explorer + CSV Export
        st.markdown("### 2. Ad-Hoc Model Explorer & Data Download (Avoid Dead-End Dashboards · BBOD Ch. 32 & 36)")
        st.caption("Drill down to individual vehicle models, inspect INEGI vintage status, or export the exact deduplicated slice.")

        model_summary = (
            df_prod.groupby(["BRAND_CLEAN", "MODELO", "SEGMENT_EN", "TIPO_EN"])["UNI_VEH_PRODUCCION"]
            .sum()
            .reset_index()
            .rename(columns={
                "BRAND_CLEAN": "Automaker",
                "MODELO": "Model",
                "SEGMENT_EN": "Segment",
                "TIPO_EN": "Vehicle Class",
                "UNI_VEH_PRODUCCION": "Assembled Units",
            })
            .sort_values("Assembled Units", ascending=False)
        )
        exp_by_mod = (
            df_exp.groupby(["BRAND_CLEAN", "MODELO"])["UNI_VEH_EXPORTACION"]
            .sum()
            .reset_index()
            .rename(columns={"BRAND_CLEAN": "Automaker", "MODELO": "Model", "UNI_VEH_EXPORTACION": "Exported Units"})
        )
        model_summary = model_summary.merge(exp_by_mod, on=["Automaker", "Model"], how="left").fillna({"Exported Units": 0})
        model_summary["Export Share (%)"] = np.where(
            model_summary["Assembled Units"] > 0,
            np.clip(model_summary["Exported Units"] / model_summary["Assembled Units"] * 100, 0, 100),
            0,
        ).round(1)

        col_exp_table, col_vintage = st.columns([1.45, 1.0])
        with col_exp_table:
            st.dataframe(
                model_summary.head(25),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Assembled Units": st.column_config.NumberColumn(format="%d"),
                    "Exported Units": st.column_config.NumberColumn(format="%d"),
                    "Export Share (%)": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f%%"),
                },
            )
            csv_bytes = model_summary.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Full Filtered Model Summary (CSV)",
                data=csv_bytes,
                file_name=f"raiavl_model_summary_{year_range[0]}_{year_range[1]}.csv",
                mime="text/csv",
            )

        with col_vintage:
            status_yr = (
                raw_df.groupby(["ANIO", "STATUS_EN"])
                .size()
                .reset_index(name="Records")
                .pivot(index="ANIO", columns="STATUS_EN", values="Records")
                .fillna(0)
            )
            fig_stat = go.Figure()
            for st_name, st_col in [
                ("Definitive Figures", GREY_CTX),
                ("Revised Figures", BLUE),
                ("Preliminary Figures", ORANGE),
            ]:
                if st_name in status_yr.columns:
                    fig_stat.add_trace(
                        go.Bar(x=status_yr.index.astype(str), y=status_yr[st_name], name=st_name, marker_color=st_col)
                    )
            fig_stat.update_layout(barmode="stack")
            style_bbod_chart(
                fig_stat,
                title="INEGI Vintage Audit (ESTATUS)",
                subtitle="2024–Sep 2026 = Revised; Oct 2026 = Preliminary",
                y_title="Merged Records",
                height=360,
                show_legend=True,
            )
            fig_stat.update_layout(
                margin=dict(r=15, b=45),
                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
            )
            st.plotly_chart(fig_stat, use_container_width=True)


if __name__ == "__main__":
    main()
