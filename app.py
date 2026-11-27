import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIG & HIGH-CONTRAST INSTITUTIONAL PALETTE
# ==============================================================================
st.set_page_config(
    page_title="SE · Mexican Light-Vehicle Industry (RAIAVL)",
    page_icon="🇲🇽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# High-contrast accessible palette (distinct luminance & hue separation)
SE_GUINDA = "#A61C3C"       # Vivid Crimson-Guinda (Tariff exposure / Contraction / U.S.)
SE_GUINDA_DARK = "#5C1024"  # Hero gradient anchor
SE_TEAL = "#0D9488"         # Bright Turquoise-Teal (Shock absorbers / Expansion / Domestic)
SE_TEAL_DARK = "#0F766E"    # Active tab & hero gradient anchor
SE_TEAL_LIGHT = "#CCFBF1"
SE_AMBER = "#D97706"        # Warm Gold-Amber (Benchmarks / Totals / Compacts)
SE_BLUE = "#3B82F6"         # Crisp Blue (Subcompacts / Secondary)
SE_SLATE = "#64748B"
SE_BG = "#F6F7F9"
SE_CARD = "#FFFFFF"
SE_TEXT = "#161A1D"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {SE_BG};
        color: {SE_TEXT};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    .block-container {{
        padding-top: 1.3rem;
        padding-bottom: 2.8rem;
        max-width: 1340px;
    }}

    /* Institutional Hero Banner */
    .se-hero {{
        background: linear-gradient(125deg, {SE_GUINDA_DARK} 0%, {SE_GUINDA} 52%, {SE_TEAL_DARK} 100%);
        border-bottom: 4px solid #F59E0B;
        border-radius: 16px;
        padding: 1.5rem 1.85rem;
        color: #FFFFFF;
        margin-bottom: 1.15rem;
        box-shadow: 0 8px 24px rgba(22, 26, 29, 0.12);
    }}
    .se-kicker {{
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #FDE68A;
        margin-bottom: 0.3rem;
    }}
    .se-title {{
        font-size: 1.75rem;
        font-weight: 800;
        line-height: 1.15;
        margin: 0 0 0.28rem 0;
        color: #FFFFFF;
    }}
    .se-subtitle {{
        font-size: 0.90rem;
        color: rgba(255, 255, 255, 0.88);
        margin: 0 0 1.1rem 0;
    }}
    .hero-kpi-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.9rem;
    }}
    .hero-kpi-box {{
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.24);
        border-radius: 12px;
        padding: 0.75rem 0.95rem;
        backdrop-filter: blur(4px);
    }}
    .hero-kpi-label {{
        font-size: 0.70rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #FDE68A;
        font-weight: 700;
    }}
    .hero-kpi-val {{
        font-size: 1.45rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.2;
        margin-top: 0.15rem;
    }}
    .hero-kpi-sub {{
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.86);
        margin-top: 0.1rem;
    }}

    /* Smooth Pill Navigation Tabs (Removes sharp default highlight rectangle) */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background-color: #FFFFFF;
        padding: 0.45rem 0.55rem;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        margin-bottom: 1.1rem;
    }}
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {{
        display: none !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 40px;
        border-radius: 10px !important;
        padding: 0 1.1rem !important;
        font-size: 0.84rem;
        font-weight: 700;
        color: {SE_SLATE};
        background-color: transparent;
        border: none !important;
        transition: all 0.18s ease;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: #F1F5F9;
        color: {SE_TEXT};
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {SE_TEAL} 0%, {SE_TEAL_DARK} 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 3px 10px rgba(13, 148, 136, 0.28);
    }}

    /* Section Headers */
    .sec-header {{
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin: 0.35rem 0 0.12rem 0;
    }}
    .sec-badge {{
        background-color: {SE_TEAL};
        color: #FFFFFF;
        font-size: 0.73rem;
        font-weight: 800;
        padding: 0.2rem 0.55rem;
        border-radius: 7px;
        letter-spacing: 0.04em;
    }}
    .sec-title {{
        font-size: 1.15rem;
        font-weight: 800;
        color: {SE_TEXT};
        margin: 0;
    }}
    .sec-caption {{
        font-size: 0.83rem;
        color: {SE_SLATE};
        margin-bottom: 0.85rem;
    }}

    /* Simulator Metric Card */
    .kpi-card {{
        position: relative;
        background: {SE_CARD};
        border: 1px solid #E2E8F0;
        border-top: 3px solid {SE_TEAL};
        border-radius: 12px;
        padding: 0.9rem 1.05rem;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
    }}
    .kpi-top {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.77rem;
        font-weight: 600;
        color: {SE_SLATE};
    }}
    .kpi-number {{
        font-size: 1.75rem;
        font-weight: 800;
        color: {SE_TEXT};
        line-height: 1.15;
        margin: 0.3rem 0 0.4rem 0;
        letter-spacing: -0.02em;
    }}
    .kpi-pill {{
        display: inline-block;
        font-size: 0.73rem;
        font-weight: 700;
        padding: 0.16rem 0.52rem;
        border-radius: 999px;
    }}
    .pill-neg {{ background: #FFE4E6; color: {SE_GUINDA}; }}
    .pill-pos {{ background: {SE_TEAL_LIGHT}; color: {SE_TEAL_DARK}; }}

    /* Chart Titles & Chart-Specific Micro-Caveats */
    .chart-title {{
        font-size: 0.96rem;
        font-weight: 700;
        color: {SE_TEXT};
        margin: 0;
    }}
    .chart-sub {{
        font-size: 0.78rem;
        color: {SE_SLATE};
        margin: 0 0 0.25rem 0;
    }}
    .chart-caveat {{
        font-size: 0.72rem;
        color: {SE_SLATE};
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 3px solid {SE_AMBER};
        padding: 0.38rem 0.68rem;
        border-radius: 0 8px 8px 0;
        margin-top: -0.25rem;
        margin-bottom: 0.6rem;
    }}

    /* Compact Recommendation Cards */
    .rec-card {{
        background: {SE_CARD};
        border: 1px solid #E2E8F0;
        border-top: 3px solid {SE_TEAL};
        border-radius: 12px;
        padding: 1rem 1.1rem;
        height: 100%;
    }}
    .rec-tag {{
        display: inline-block;
        font-size: 0.68rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 0.16rem 0.5rem;
        border-radius: 6px;
        background: {SE_TEAL_LIGHT};
        color: {SE_TEAL_DARK};
        margin-bottom: 0.42rem;
    }}
    .rec-tag.guinda {{ background: #FFE4E6; color: {SE_GUINDA}; }}
    .rec-tag.amber {{ background: #FEF3C7; color: #B45309; }}
    .rec-title {{
        font-size: 1.00rem;
        font-weight: 800;
        color: {SE_TEXT};
        margin-bottom: 0.5rem;
    }}
    .rec-stats {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.5rem;
        margin-bottom: 0.6rem;
    }}
    .rec-stat-box {{
        background: #F8FAFC;
        border-radius: 8px;
        padding: 0.45rem 0.6rem;
    }}
    .rec-stat-num {{
        font-size: 1.05rem;
        font-weight: 800;
        color: {SE_TEXT};
    }}
    .rec-stat-lbl {{
        font-size: 0.69rem;
        color: {SE_SLATE};
    }}
    .rec-action {{
        font-size: 0.79rem;
        color: {SE_TEXT};
        border-top: 1px solid #F1F5F9;
        padding-top: 0.5rem;
        line-height: 1.4;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# 2. DATA LOADING & EXACT GRAIN DEDUPLICATION
# ==============================================================================
MONTH_MAP = {
    "ENERO": 1, "ENE": 1, "1": 1, "01": 1, "1.0": 1,
    "FEBRERO": 2, "FEB": 2, "2": 2, "02": 2, "2.0": 2,
    "MARZO": 3, "MAR": 3, "3": 3, "03": 3, "3.0": 3,
    "ABRIL": 4, "ABR": 4, "4": 4, "04": 4, "4.0": 4,
    "MAYO": 5, "MAY": 5, "5": 5, "05": 5, "5.0": 5,
    "JUNIO": 6, "JUN": 6, "6": 6, "06": 6, "6.0": 6,
    "JULIO": 7, "JUL": 7, "7": 7, "07": 7, "7.0": 7,
    "AGOSTO": 8, "AGO": 8, "8": 8, "08": 8, "8.0": 8,
    "SEPTIEMBRE": 9, "SETIEMBRE": 9, "SEP": 9, "9": 9, "09": 9, "9.0": 9,
    "OCTUBRE": 10, "OCT": 10, "10": 10, "10.0": 10,
    "NOVIEMBRE": 11, "NOV": 11, "11": 11, "11.0": 11,
    "DICIEMBRE": 12, "DIC": 12, "12": 12, "12.0": 12,
}

MONTH_SHORT = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}

SEGMENT_MAP = {
    "SUV": "SUVs",
    "SUVS": "SUVs",
    "CAMIONES LIGEROS": "SUVs",
    "PICK UP": "Pickups",
    "PICK UPS": "Pickups",
    "PICKUPS": "Pickups",
    "PICK-UP": "Pickups",
    "SUBCOMPACTO": "Subcompacts",
    "SUBCOMPACTOS": "Subcompacts",
    "COMPACTO": "Compacts",
    "COMPACTOS": "Compacts",
    "MINIVAN": "Minivans",
    "MINIVANS": "Minivans",
    "DE LUJO": "Luxury",
    "LUJO": "Luxury",
    "DEPORTIVO": "Sports",
    "DEPORTIVOS": "Sports",
}


def normalize_segment(val: str) -> str:
    if pd.isna(val):
        return "Other"
    # Strip apostrophes so "SUV'S" and "SUV’S" normalize cleanly to "SUVs"
    key = str(val).strip().upper().replace("'", "").replace("’", "").replace("´", "")
    return SEGMENT_MAP.get(key, str(val).strip().title())


def is_usa(val: str) -> bool:
    if pd.isna(val):
        return False
    s = str(val).strip().upper()
    return any(tok in s for tok in ["ESTADOS UNIDOS", "UNITED STATES", "USA", "E.U.A", "EE.UU"])


@st.cache_data(show_spinner=False)
def load_raiavl_data():
    candidates = [
        "dataset_final_raiavl.csv",
        "dataset_final_raiavl.csv.gz",
        "data/dataset_final_raiavl.csv",
        "data/dataset_final_raiavl.csv.gz",
    ]
    path = next((p for p in candidates if os.path.exists(p)), None)
    if path is None:
        st.error("Dataset `dataset_final_raiavl.csv` not found in repository root.")
        st.stop()

    df = pd.read_csv(path)
    df.columns = [c.strip().upper() for c in df.columns]

    for col in ["UNI_VEH_PRODUCCION", "UNI_VEH_VENTAS", "UNI_VEH_EXPORTACION"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0

    df["ANIO"] = pd.to_numeric(df["ANIO"], errors="coerce")
    df["MES"] = df["MES"].astype(str).str.strip().str.upper().map(MONTH_MAP)
    df = df.dropna(subset=["ANIO", "MES"]).copy()
    df["ANIO"] = df["ANIO"].astype(int)
    df["MES"] = df["MES"].astype(int)

    df["MARCA"] = df["MARCA"].fillna("Unknown").astype(str).str.strip()
    df["MODELO"] = df["MODELO"].fillna("Unknown").astype(str).str.strip()
    df["SEG_CLEAN"] = df["SEGMENTO"].apply(normalize_segment) if "SEGMENTO" in df.columns else "Other"
    df["PAIS_DESTINO"] = df["PAIS_DESTINO"].fillna("Unreported").astype(str).str.strip()
    df["IS_USA"] = df["PAIS_DESTINO"].apply(is_usa)

    grain_cols = ["ANIO", "MES", "MARCA", "MODELO", "SEG_CLEAN"]

    prod_sales = (
        df.groupby(grain_cols, as_index=False)
        .agg(
            PRODUCCION=("UNI_VEH_PRODUCCION", "max"),
            VENTAS=("UNI_VEH_VENTAS", "max"),
        )
    )

    exports = (
        df.groupby(grain_cols + ["PAIS_DESTINO", "IS_USA"], as_index=False)
        .agg(EXPORTACION=("UNI_VEH_EXPORTACION", "sum"))
    )

    return prod_sales, exports


prod_sales_df, exports_df = load_raiavl_data()

max_year = int(prod_sales_df["ANIO"].max())
max_month_latest = int(prod_sales_df.loc[prod_sales_df["ANIO"] == max_year, "MES"].max())
prev_year = max_year - 1


# ==============================================================================
# 3. GLOBAL SIDEBAR CONTROLS
# ==============================================================================
with st.sidebar:
    st.markdown("### 🇲🇽 Filters · RAIAVL")
    ytd_mode = st.toggle(
        f"Match Jan–Oct YTD ({max_year} cutoff)",
        value=True,
        help=f"Compares months 1–{max_month_latest} across all years to eliminate seasonal bias.",
    )
    all_brands = sorted(prod_sales_df["MARCA"].unique())
    sel_brands = st.multiselect("Automaker (MARCA)", options=all_brands, default=[])

    all_segments = sorted(prod_sales_df["SEG_CLEAN"].unique())
    sel_segments = st.multiselect("Vehicle Segment", options=all_segments, default=[])

    year_range = st.slider(
        "Historical Window",
        min_value=int(prod_sales_df["ANIO"].min()),
        max_value=max_year,
        value=(2015, max_year),
    )

ps_full = prod_sales_df.copy()
ex_full = exports_df.copy()

if sel_brands:
    ps_full = ps_full[ps_full["MARCA"].isin(sel_brands)]
    ex_full = ex_full[ex_full["MARCA"].isin(sel_brands)]

if sel_segments:
    ps_full = ps_full[ps_full["SEG_CLEAN"].isin(sel_segments)]
    ex_full = ex_full[ex_full["SEG_CLEAN"].isin(sel_segments)]

ps = ps_full[ps_full["MES"] <= max_month_latest].copy() if ytd_mode else ps_full.copy()
ex = ex_full[ex_full["MES"] <= max_month_latest].copy() if ytd_mode else ex_full.copy()


# ==============================================================================
# 4. CORE METRICS COMPUTATION
# ==============================================================================
def fmt_units(val: float) -> str:
    if abs(val) >= 1_000_000:
        return f"{val / 1_000_000:.2f}M"
    if abs(val) >= 1_000:
        return f"{val / 1_000:.0f}k"
    return f"{val:,.0f}"


def pct_delta(curr: float, prev: float) -> float:
    return ((curr - prev) / prev * 100.0) if prev > 0 else 0.0


prod_curr = ps.loc[ps["ANIO"] == max_year, "PRODUCCION"].sum()
prod_prev = ps.loc[ps["ANIO"] == prev_year, "PRODUCCION"].sum()
prod_yoy = pct_delta(prod_curr, prod_prev)

suv_curr = ps.loc[(ps["ANIO"] == max_year) & (ps["SEG_CLEAN"] == "SUVs"), "PRODUCCION"].sum()
suv_mix = (suv_curr / prod_curr * 100.0) if prod_curr > 0 else 0.0

us_curr = ex.loc[(ex["ANIO"] == max_year) & (ex["IS_USA"]), "EXPORTACION"].sum()
us_prev = ex.loc[(ex["ANIO"] == prev_year) & (ex["IS_USA"]), "EXPORTACION"].sum()
us_yoy = pct_delta(us_curr, us_prev)

non_us_curr = ex.loc[(ex["ANIO"] == max_year) & (~ex["IS_USA"]), "EXPORTACION"].sum()
non_us_prev = ex.loc[(ex["ANIO"] == prev_year) & (~ex["IS_USA"]), "EXPORTACION"].sum()
non_us_yoy = pct_delta(non_us_curr, non_us_prev)

tot_exp_curr = us_curr + non_us_curr
us_dep_pct = (us_curr / tot_exp_curr * 100.0) if tot_exp_curr > 0 else 0.0

suv_exp_curr = ex.loc[(ex["ANIO"] == max_year) & (ex["SEG_CLEAN"] == "SUVs"), "EXPORTACION"].sum()
suv_sales_curr = ps.loc[(ps["ANIO"] == max_year) & (ps["SEG_CLEAN"] == "SUVs"), "VENTAS"].sum()
suv_exp_share = (
    (suv_exp_curr / (suv_exp_curr + suv_sales_curr) * 100.0)
    if (suv_exp_curr + suv_sales_curr) > 0
    else 0.0
)

sub_sales_curr = ps.loc[(ps["ANIO"] == max_year) & (ps["SEG_CLEAN"] == "Subcompacts"), "VENTAS"].sum()
sub_exp_curr = ex.loc[(ex["ANIO"] == max_year) & (ex["SEG_CLEAN"] == "Subcompacts"), "EXPORTACION"].sum()
sub_dom_share = (
    (sub_sales_curr / (sub_sales_curr + sub_exp_curr) * 100.0)
    if (sub_sales_curr + sub_exp_curr) > 0
    else 0.0
)

period_tag = f"Jan–Oct {max_year} YTD" if ytd_mode else f"Full Year {max_year}"


# ==============================================================================
# 5. SINGLE INTEGRATED HERO HEADER (Eliminates Duplicate KPI Row)
# ==============================================================================
st.markdown(
    f"""
    <div class="se-hero">
        <div class="se-kicker">Secretaría de Economía · México · Registro Administrativo (RAIAVL 2005–{max_year})</div>
        <div class="se-title">Mexican Light-Vehicle Industry: Tariff Exposure &amp; Structural Split</div>
        <div class="se-subtitle">Assembly pivot, U.S. vs. global export divergence, and domestic segment buffer ({period_tag})</div>
        <div class="hero-kpi-grid">
            <div class="hero-kpi-box">
                <div class="hero-kpi-label">{period_tag} Assembly</div>
                <div class="hero-kpi-val">{fmt_units(prod_curr)}</div>
                <div class="hero-kpi-sub">{prod_yoy:+.1f}% YoY vs. {prev_year}</div>
            </div>
            <div class="hero-kpi-box">
                <div class="hero-kpi-label">U.S.-Bound Exports</div>
                <div class="hero-kpi-val">{fmt_units(us_curr)}</div>
                <div class="hero-kpi-sub">{us_yoy:+.1f}% YoY · {us_dep_pct:.1f}% of all exports</div>
            </div>
            <div class="hero-kpi-box">
                <div class="hero-kpi-label">Non-U.S. Exports</div>
                <div class="hero-kpi-val">{fmt_units(non_us_curr)}</div>
                <div class="hero-kpi-sub">{non_us_yoy:+.1f}% YoY shock absorber</div>
            </div>
            <div class="hero-kpi-box">
                <div class="hero-kpi-label">SUV Assembly Share</div>
                <div class="hero-kpi-val">{suv_mix:.1f}%</div>
                <div class="hero-kpi-sub">{suv_exp_share:.1f}% of SUVs exported abroad</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# 6. FIVE STORYTELLING CHAPTERS (13 VISUALIZATIONS WITH EXPLICIT LEGENDS)
# ==============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "01 · Production & Segment Pivot",
        "02 · U.S. vs. Global Trade",
        "03 · Domestic Split & Peer Benchmark",
        "04 · Seasonality & Shock Matrix",
        "05 · Tariff Waterfall & Policy Levers",
    ]
)

# Shared segment palette (high contrast + consistent across charts)
SEG_PALETTE = {
    "SUVs": SE_GUINDA,
    "Pickups": SE_TEAL,
    "Compacts": SE_AMBER,
    "Subcompacts": SE_BLUE,
    "Other": "#94A3B8",
}

# ------------------------------------------------------------------------------
# TAB 1: PRODUCTION & SEGMENT PIVOT (4 CHARTS)
# ------------------------------------------------------------------------------
with tab1:
    st.markdown(
        f"""
        <div class="sec-header">
            <span class="sec-badge">01</span>
            <h2 class="sec-title">Assembly Trajectory &amp; Structural Segment Pivot</h2>
        </div>
        <div class="sec-caption">How SUVs and Pickups reshaped Mexican plants and absorbed the {max_year} tariff shock.</div>
        """,
        unsafe_allow_html=True,
    )

    r1_c1, r1_c2 = st.columns([1.15, 1.0], gap="large")

    with r1_c1:
        st.markdown(
            f"""
            <p class="chart-title">1. Annual Light-Vehicle Assembly ({period_tag})</p>
            <p class="chart-sub">2026 pullback interrupts post-COVID recovery</p>
            """,
            unsafe_allow_html=True,
        )
        ann_prod = (
            ps[ps["ANIO"].between(year_range[0], year_range[1])]
            .groupby("ANIO", as_index=False)["PRODUCCION"]
            .sum()
            .sort_values("ANIO")
        )
        ann_prod["CAT"] = np.where(
            ann_prod["ANIO"] == max_year,
            f"{max_year} Tariff Pullback",
            np.where(ann_prod["ANIO"] == prev_year, f"{prev_year} Benchmark", "Historical (2015–2024)"),
        )
        cat_styles = [
            ("Historical (2015–2024)", "#CBD5E1"),
            (f"{prev_year} Benchmark", SE_TEAL),
            (f"{max_year} Tariff Pullback", SE_GUINDA),
        ]
        fig_ann = go.Figure()
        for cat_label, cat_col in cat_styles:
            sub_a = ann_prod[ann_prod["CAT"] == cat_label]
            if not sub_a.empty:
                fig_ann.add_trace(
                    go.Bar(
                        x=sub_a["ANIO"],
                        y=sub_a["PRODUCCION"],
                        name=cat_label,
                        marker_color=cat_col,
                        text=[fmt_units(v) for v in sub_a["PRODUCCION"]],
                        textposition="outside",
                        textfont=dict(size=10, color=SE_TEXT),
                        hovertemplate="<b>%{x}</b><br>Assembly: %{y:,.0f} units<extra></extra>",
                    )
                )
        if year_range[0] <= 2020 <= year_range[1]:
            fig_ann.add_vrect(
                x0=2019.5, x1=2021.5, fillcolor="#94A3B8", opacity=0.14, line_width=0,
                annotation_text="COVID-19 / Chips", annotation_position="top left",
                annotation_font=dict(size=10, color=SE_SLATE),
            )
        fig_ann.update_layout(
            barmode="overlay",
            height=340,
            margin=dict(l=10, r=10, t=32, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10)),
            xaxis=dict(dtick=1, showgrid=False, tickfont=dict(size=11)),
            yaxis=dict(
                showgrid=True,
                gridcolor="#F1F5F9",
                range=[0, ann_prod["PRODUCCION"].max() * 1.15],
                tickformat=".2s",
            ),
        )
        st.plotly_chart(fig_ann, use_container_width=True)
        st.markdown(
            f"""
            <div class="chart-caveat">
                ⓘ <strong>Coverage &amp; Vintage:</strong> Matched Jan–Oct YTD comparison (10 mos) to avoid seasonal drop.
                <code>ESTATUS</code>: 2005–2023 Definitive · 2024–Sep 2026 Revised · Oct 2026 Preliminary.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r1_c2:
        h_l, h_r = st.columns([1.45, 1.0])
        with h_l:
            st.markdown(
                f"""
                <p class="chart-title">2. Assembly Mix by Vehicle Segment</p>
                <p class="chart-sub">SUVs &amp; Pickups replaced compact cars</p>
                """,
                unsafe_allow_html=True,
            )
        with h_r:
            seg_view = st.radio(
                "View",
                ["Units", "% Mix"],
                horizontal=True,
                label_visibility="collapsed",
                key="seg_mix_toggle",
            )

        seg_hist = (
            ps[ps["ANIO"].between(year_range[0], year_range[1])]
            .groupby(["ANIO", "SEG_CLEAN"], as_index=False)["PRODUCCION"]
            .sum()
        )
        top_segs = ["SUVs", "Pickups", "Compacts", "Subcompacts"]
        seg_hist["SEG_GROUP"] = seg_hist["SEG_CLEAN"].apply(lambda s: s if s in top_segs else "Other")
        seg_grp = seg_hist.groupby(["ANIO", "SEG_GROUP"], as_index=False)["PRODUCCION"].sum()

        if seg_view == "% Mix":
            totals = seg_grp.groupby("ANIO")["PRODUCCION"].transform("sum")
            seg_grp["VAL"] = np.where(totals > 0, seg_grp["PRODUCCION"] / totals * 100.0, 0)
            y_fmt = ".0f"
            hover_tmpl = "<b>%{fullData.name}</b> (%{x})<br>Share: %{y:.1f}%<extra></extra>"
        else:
            seg_grp["VAL"] = seg_grp["PRODUCCION"]
            y_fmt = ".2s"
            hover_tmpl = "<b>%{fullData.name}</b> (%{x})<br>Units: %{y:,.0f}<extra></extra>"

        fig_seg = go.Figure()
        for seg_name in ["SUVs", "Pickups", "Compacts", "Subcompacts", "Other"]:
            sub_df = seg_grp[seg_grp["SEG_GROUP"] == seg_name].sort_values("ANIO")
            if not sub_df.empty:
                fig_seg.add_trace(
                    go.Bar(
                        x=sub_df["ANIO"],
                        y=sub_df["VAL"],
                        name=seg_name,
                        marker_color=SEG_PALETTE[seg_name],
                        hovertemplate=hover_tmpl,
                    )
                )
        fig_seg.update_layout(
            barmode="stack",
            height=340,
            margin=dict(l=10, r=10, t=32, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10)),
            xaxis=dict(dtick=1, showgrid=False, tickfont=dict(size=11)),
            yaxis=dict(
                showgrid=True,
                gridcolor="#F1F5F9",
                tickformat=y_fmt,
                ticksuffix="%" if seg_view == "% Mix" else "",
            ),
        )
        st.plotly_chart(fig_seg, use_container_width=True)

    st.write("")
    r2_c1, r2_c2 = st.columns([1.0, 1.15], gap="large")

    with r2_c1:
        st.markdown(
            f"""
            <p class="chart-title">3. YoY Assembly Growth by Segment ({max_year} vs. {prev_year})</p>
            <p class="chart-sub">Dashed line = total industry pace ({prod_yoy:+.1f}%)</p>
            """,
            unsafe_allow_html=True,
        )
        seg_yoy_df = (
            ps[ps["ANIO"].isin([prev_year, max_year])]
            .groupby(["SEG_CLEAN", "ANIO"], as_index=False)["PRODUCCION"]
            .sum()
            .pivot(index="SEG_CLEAN", columns="ANIO", values="PRODUCCION")
            .fillna(0)
            .reset_index()
        )
        if prev_year in seg_yoy_df.columns and max_year in seg_yoy_df.columns:
            seg_yoy_df = seg_yoy_df[(seg_yoy_df[prev_year] > 0) | (seg_yoy_df[max_year] > 0)].copy()
            seg_yoy_df["YOY"] = np.where(
                seg_yoy_df[prev_year] > 0,
                (seg_yoy_df[max_year] - seg_yoy_df[prev_year]) / seg_yoy_df[prev_year] * 100.0,
                0.0,
            )
            seg_yoy_df = seg_yoy_df.sort_values("YOY", ascending=True)

            fig_seg_yoy = go.Figure()
            for dir_label, dir_col, mask in [
                ("YoY Expansion (>0%)", SE_TEAL, seg_yoy_df["YOY"] >= 0),
                ("YoY Contraction (<0%)", SE_GUINDA, seg_yoy_df["YOY"] < 0),
            ]:
                sub_y = seg_yoy_df[mask]
                if not sub_y.empty:
                    fig_seg_yoy.add_trace(
                        go.Bar(
                            y=sub_y["SEG_CLEAN"],
                            x=sub_y["YOY"],
                            name=dir_label,
                            orientation="h",
                            marker_color=dir_col,
                            text=[f"{v:+.1f}%" for v in sub_y["YOY"]],
                            textposition="outside",
                            textfont=dict(size=10, color=SE_TEXT),
                            hovertemplate="<b>%{y}</b><br>YoY Change: %{x:+.1f}%<extra></extra>",
                        )
                    )
            fig_seg_yoy.add_vline(
                x=prod_yoy,
                line_dash="dash",
                line_color=SE_AMBER,
                annotation_text=f"Total {prod_yoy:+.1f}%",
                annotation_position="top",
                annotation_font=dict(size=10, color=SE_AMBER),
            )
            min_x = min(seg_yoy_df["YOY"].min(), prod_yoy)
            max_x = max(seg_yoy_df["YOY"].max(), 0)
            fig_seg_yoy.update_layout(
                barmode="overlay",
                height=330,
                margin=dict(l=10, r=20, t=32, b=10),
                plot_bgcolor="white",
                paper_bgcolor="white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10)),
                xaxis=dict(
                    showgrid=True,
                    gridcolor="#F1F5F9",
                    ticksuffix="%",
                    range=[min_x - 4.5, max_x + 4.5],
                ),
                yaxis=dict(showgrid=False, tickfont=dict(size=11)),
            )
            st.plotly_chart(fig_seg_yoy, use_container_width=True)

    with r2_c2:
        st.markdown(
            f"""
            <p class="chart-title">4. Top 10 Assembled Nameplates in Mexico ({period_tag})</p>
            <p class="chart-sub">Top 10 models by assembly volume</p>
            """,
            unsafe_allow_html=True,
        )
        top_models = (
            ps[ps["ANIO"] == max_year]
            .groupby(["MODELO", "MARCA", "SEG_CLEAN"], as_index=False)["PRODUCCION"]
            .sum()
            .sort_values("PRODUCCION", ascending=False)
            .head(10)
            .sort_values("PRODUCCION", ascending=True)
        )
        top_models["LABEL_NAME"] = top_models["MODELO"].str.rstrip("-") + " (" + top_models["MARCA"] + ")"
        top_models["SEG_PLOT"] = top_models["SEG_CLEAN"].apply(lambda s: s if s in SEG_PALETTE else "Other")

        fig_models = go.Figure()
        for seg_name in ["SUVs", "Pickups", "Compacts", "Subcompacts", "Other"]:
            sub_m = top_models[top_models["SEG_PLOT"] == seg_name]
            if not sub_m.empty:
                fig_models.add_trace(
                    go.Bar(
                        x=sub_m["PRODUCCION"],
                        y=sub_m["LABEL_NAME"],
                        name=seg_name,
                        orientation="h",
                        marker_color=SEG_PALETTE[seg_name],
                        text=[fmt_units(v) for v in sub_m["PRODUCCION"]],
                        textposition="outside",
                        textfont=dict(size=10, color=SE_TEXT),
                        hovertemplate=f"<b>%{{y}}</b><br>Segment: {seg_name}<br>Assembled: %{{x:,.0f}} units<extra></extra>",
                    )
                )
        fig_models.update_layout(
            barmode="overlay",
            height=330,
            margin=dict(l=10, r=20, t=32, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10)),
            xaxis=dict(
                showgrid=True,
                gridcolor="#F1F5F9",
                range=[0, top_models["PRODUCCION"].max() * 1.18],
                tickformat=".2s",
            ),
            yaxis=dict(
                showgrid=False,
                tickfont=dict(size=10),
                categoryorder="array",
                categoryarray=top_models["LABEL_NAME"].tolist(),
            ),
        )
        st.plotly_chart(fig_models, use_container_width=True)


# ------------------------------------------------------------------------------
# TAB 2: U.S. VS. GLOBAL TRADE (3 CHARTS)
# ------------------------------------------------------------------------------
with tab2:
    st.markdown(
        f"""
        <div class="sec-header">
            <span class="sec-badge">02</span>
            <h2 class="sec-title">Trade Divergence &amp; Automaker Tariff Exposure</h2>
        </div>
        <div class="sec-caption">U.S. shipments contracted while Latin America and Europe absorbed assembly capacity.</div>
        """,
        unsafe_allow_html=True,
    )

    t1, t2 = st.columns([1.15, 1.0], gap="large")

    with t1:
        st.markdown(
            f"""
            <p class="chart-title">5. Export Trajectory: U.S. vs. Rest of World ({period_tag})</p>
            <p class="chart-sub">U.S. shipments fell {us_yoy:+.1f}% YoY while non-U.S. markets rose {non_us_yoy:+.1f}%</p>
            """,
            unsafe_allow_html=True,
        )
        exp_trend = (
            ex[ex["ANIO"].between(year_range[0], year_range[1])]
            .groupby(["ANIO", "IS_USA"], as_index=False)["EXPORTACION"]
            .sum()
        )
        exp_trend["DEST"] = np.where(exp_trend["IS_USA"], "United States", "Non-U.S. Markets")

        fig_trade = go.Figure()
        for dest_label, line_col in [("United States", SE_GUINDA), ("Non-U.S. Markets", SE_TEAL)]:
            d_sub = exp_trend[exp_trend["DEST"] == dest_label].sort_values("ANIO")
            fig_trade.add_trace(
                go.Scatter(
                    x=d_sub["ANIO"],
                    y=d_sub["EXPORTACION"],
                    mode="lines+markers+text",
                    name=dest_label,
                    line=dict(color=line_col, width=3),
                    marker=dict(size=6, color=line_col),
                    text=[
                        fmt_units(v) if y in (year_range[0], max_year) else ""
                        for y, v in zip(d_sub["ANIO"], d_sub["EXPORTACION"])
                    ],
                    textposition="top center",
                    textfont=dict(size=10, color=line_col),
                    hovertemplate=f"<b>{dest_label}</b> (%{{x}})<br>Exports: %{{y:,.0f}} units<extra></extra>",
                )
            )
        fig_trade.update_layout(
            height=330,
            margin=dict(l=10, r=20, t=28, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=11)),
            xaxis=dict(dtick=1, showgrid=False, tickfont=dict(size=11)),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9", rangemode="tozero", tickformat=".2s"),
        )
        st.plotly_chart(fig_trade, use_container_width=True)

    with t2:
        st.markdown(
            f"""
            <p class="chart-title">6. Top Non-U.S. Shock-Absorber Markets ({period_tag})</p>
            <p class="chart-sub">Canada, Germany &amp; Latin America offset North American friction</p>
            """,
            unsafe_allow_html=True,
        )
        non_us_curr_df = (
            ex[(ex["ANIO"] == max_year) & (~ex["IS_USA"])]
            .groupby("PAIS_DESTINO", as_index=False)["EXPORTACION"]
            .sum()
        )
        non_us_prev_df = (
            ex[(ex["ANIO"] == prev_year) & (~ex["IS_USA"])]
            .groupby("PAIS_DESTINO", as_index=False)["EXPORTACION"]
            .sum()
            .rename(columns={"EXPORTACION": "PREV_EXP"})
        )
        top_dest = (
            non_us_curr_df.merge(non_us_prev_df, on="PAIS_DESTINO", how="left")
            .fillna(0)
            .sort_values("EXPORTACION", ascending=False)
            .head(8)
            .sort_values("EXPORTACION", ascending=True)
        )
        top_dest["YOY"] = np.where(
            top_dest["PREV_EXP"] > 0,
            (top_dest["EXPORTACION"] - top_dest["PREV_EXP"]) / top_dest["PREV_EXP"] * 100.0,
            0.0,
        )
        top_dest["LABEL"] = [
            f"{fmt_units(u)} ({y:+.1f}%)" for u, y in zip(top_dest["EXPORTACION"], top_dest["YOY"])
        ]
        fig_dest = go.Figure(
            data=[
                go.Bar(
                    x=top_dest["EXPORTACION"],
                    y=top_dest["PAIS_DESTINO"],
                    orientation="h",
                    marker_color=SE_TEAL,
                    text=top_dest["LABEL"],
                    textposition="outside",
                    textfont=dict(size=10, color=SE_TEXT),
                    hovertemplate="<b>%{y}</b><br>Exports: %{x:,.0f} units<extra></extra>",
                )
            ]
        )
        fig_dest.update_layout(
            height=330,
            margin=dict(l=10, r=20, t=28, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(
                showgrid=True,
                gridcolor="#F1F5F9",
                range=[0, top_dest["EXPORTACION"].max() * 1.28],
                tickformat=".2s",
            ),
            yaxis=dict(showgrid=False, tickfont=dict(size=11)),
        )
        st.plotly_chart(fig_dest, use_container_width=True)

    st.write("")
    st.markdown(
        f"""
        <p class="chart-title">7. Automaker Tariff Exposure Matrix ({period_tag})</p>
        <p class="chart-sub">Export scale vs. U.S. dependency · Bubble size = total assembly</p>
        """,
        unsafe_allow_html=True,
    )
    oem_exp = (
        ex[ex["ANIO"] == max_year]
        .groupby(["MARCA", "IS_USA"], as_index=False)["EXPORTACION"]
        .sum()
    )
    oem_piv = oem_exp.pivot(index="MARCA", columns="IS_USA", values="EXPORTACION").fillna(0).reset_index()
    oem_piv.columns.name = None
    if True not in oem_piv.columns:
        oem_piv[True] = 0.0
    if False not in oem_piv.columns:
        oem_piv[False] = 0.0
    oem_piv["US_EXP"] = oem_piv[True]
    oem_piv["NON_US_EXP"] = oem_piv[False]
    oem_piv["TOT_EXP"] = oem_piv["US_EXP"] + oem_piv["NON_US_EXP"]
    oem_piv = oem_piv[oem_piv["TOT_EXP"] > 0].copy()
    oem_piv["US_SHARE"] = oem_piv["US_EXP"] / oem_piv["TOT_EXP"] * 100.0

    oem_prod = (
        ps[ps["ANIO"] == max_year]
        .groupby("MARCA", as_index=False)["PRODUCCION"]
        .sum()
    )
    oem_mat = oem_piv.merge(oem_prod, on="MARCA", how="left").fillna(0)
    avg_us_share = us_dep_pct if us_dep_pct > 0 else 77.6

    fig_quad = go.Figure()
    for grp_label, grp_col, grp_mask in [
        (f"High U.S. Exposure (≥{avg_us_share:.1f}%)", SE_GUINDA, oem_mat["US_SHARE"] >= avg_us_share),
        (f"More Diversified (<{avg_us_share:.1f}%)", SE_TEAL, oem_mat["US_SHARE"] < avg_us_share),
    ]:
        sub_q = oem_mat[grp_mask]
        if not sub_q.empty:
            fig_quad.add_trace(
                go.Scatter(
                    x=sub_q["TOT_EXP"],
                    y=sub_q["US_SHARE"],
                    mode="markers+text",
                    name=grp_label,
                    text=sub_q["MARCA"],
                    textposition="top center",
                    textfont=dict(size=10, color=SE_TEXT),
                    marker=dict(
                        size=np.clip(np.sqrt(sub_q["PRODUCCION"].clip(lower=1000)) / 18.0, 14, 52),
                        color=grp_col,
                        opacity=0.85,
                        line=dict(width=1.5, color="white"),
                    ),
                    customdata=np.stack([sub_q["US_EXP"], sub_q["NON_US_EXP"]], axis=-1),
                    hovertemplate=(
                        "<b>%{text}</b><br>"
                        "Total Exports: %{x:,.0f}<br>"
                        "U.S. Share: %{y:.1f}%<br>"
                        "U.S.: %{customdata[0]:,.0f} | Non-U.S.: %{customdata[1]:,.0f}<extra></extra>"
                    ),
                )
            )
    fig_quad.add_hline(
        y=avg_us_share,
        line_dash="dash",
        line_color=SE_AMBER,
        annotation_text=f"Industry U.S. Share ({avg_us_share:.1f}%)",
        annotation_position="bottom right",
        annotation_font=dict(size=10, color=SE_AMBER),
    )
    fig_quad.update_layout(
        height=360,
        margin=dict(l=10, r=25, t=30, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=11)),
        xaxis=dict(title="Total Export Volume (Units)", showgrid=True, gridcolor="#F1F5F9", tickformat=".2s"),
        yaxis=dict(title="U.S. Export Share (%)", range=[0, 108], ticksuffix="%", showgrid=True, gridcolor="#F1F5F9"),
    )
    st.plotly_chart(fig_quad, use_container_width=True)


# ------------------------------------------------------------------------------
# TAB 3: DOMESTIC SPLIT & PEER BENCHMARK (3 CHARTS)
# ------------------------------------------------------------------------------
with tab3:
    st.markdown(
        f"""
        <div class="sec-header">
            <span class="sec-badge">03</span>
            <h2 class="sec-title">Two-Speed Segment Split &amp; Automaker Peer Benchmark</h2>
        </div>
        <div class="sec-caption">Export-reliant SUVs vs. domestically absorbed Subcompacts, plus brand ranking dynamics.</div>
        """,
        unsafe_allow_html=True,
    )

    s1, s2 = st.columns([1.05, 1.05], gap="large")

    with s1:
        st.markdown(
            f"""
            <p class="chart-title">8. Export vs. Domestic Orientation by Segment ({max_year})</p>
            <p class="chart-sub">Export vs. domestic market split by segment</p>
            """,
            unsafe_allow_html=True,
        )
        seg_exp = ex[ex["ANIO"] == max_year].groupby("SEG_CLEAN", as_index=False)["EXPORTACION"].sum()
        seg_dom = ps[ps["ANIO"] == max_year].groupby("SEG_CLEAN", as_index=False)["VENTAS"].sum()
        seg_split = seg_exp.merge(seg_dom, on="SEG_CLEAN", how="outer").fillna(0)
        seg_split["TOTAL"] = seg_split["EXPORTACION"] + seg_split["VENTAS"]
        seg_split = seg_split[seg_split["TOTAL"] > 0].copy()
        seg_split["EXP_PCT"] = seg_split["EXPORTACION"] / seg_split["TOTAL"] * 100.0
        seg_split["DOM_PCT"] = seg_split["VENTAS"] / seg_split["TOTAL"] * 100.0
        seg_split = seg_split.sort_values("EXP_PCT", ascending=True)

        fig_split = go.Figure()
        fig_split.add_trace(
            go.Bar(
                y=seg_split["SEG_CLEAN"],
                x=seg_split["EXP_PCT"],
                name="Exported Abroad",
                orientation="h",
                marker_color=SE_GUINDA,
                text=[f"{v:.1f}%" if v >= 12 else "" for v in seg_split["EXP_PCT"]],
                textposition="inside",
                textfont=dict(color="white", size=10),
                hovertemplate="<b>%{y}</b><br>Exported: %{x:.1f}%<extra></extra>",
            )
        )
        fig_split.add_trace(
            go.Bar(
                y=seg_split["SEG_CLEAN"],
                x=seg_split["DOM_PCT"],
                name="Domestic Retail (Mexico)",
                orientation="h",
                marker_color=SE_TEAL,
                text=[f"{v:.1f}%" if v >= 12 else "" for v in seg_split["DOM_PCT"]],
                textposition="inside",
                textfont=dict(color="white", size=10),
                hovertemplate="<b>%{y}</b><br>Domestic Sales: %{x:.1f}%<extra></extra>",
            )
        )
        fig_split.update_layout(
            barmode="stack",
            height=330,
            margin=dict(l=10, r=10, t=28, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10)),
            xaxis=dict(range=[0, 100], ticksuffix="%", showgrid=False),
            yaxis=dict(showgrid=False, tickfont=dict(size=11)),
        )
        st.plotly_chart(fig_split, use_container_width=True)
        st.markdown(
            f"""
            <div class="chart-caveat">
                ⓘ <strong>Heavy-Duty Pickup Lag:</strong> GM Silverado 2500 / GMC Sierra and Stellantis RAM 2500 record
                2025–2026 export shipments from inventory/model-code splits against zero new production rows.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with s2:
        st.markdown(
            f"""
            <p class="chart-title">9. Automaker Production Rank Trajectory (Bump Chart)</p>
            <p class="chart-sub">Annual assembly ranking among top 7 automakers</p>
            """,
            unsafe_allow_html=True,
        )
        top_oems = (
            ps[ps["ANIO"] == max_year]
            .groupby("MARCA", as_index=False)["PRODUCCION"]
            .sum()
            .sort_values("PRODUCCION", ascending=False)
            .head(7)["MARCA"]
            .tolist()
        )
        bump_df = (
            ps[(ps["ANIO"].between(max(year_range[0], 2018), year_range[1])) & (ps["MARCA"].isin(top_oems))]
            .groupby(["ANIO", "MARCA"], as_index=False)["PRODUCCION"]
            .sum()
        )
        bump_df["RANK"] = bump_df.groupby("ANIO")["PRODUCCION"].rank(ascending=False, method="min")

        bump_palette = [SE_GUINDA, SE_TEAL, SE_AMBER, SE_BLUE, "#8B5CF6", "#EC4899", "#475569"]
        fig_bump = go.Figure()
        for idx, brand in enumerate(top_oems):
            b_sub = bump_df[bump_df["MARCA"] == brand].sort_values("ANIO")
            col = bump_palette[idx % len(bump_palette)]
            fig_bump.add_trace(
                go.Scatter(
                    x=b_sub["ANIO"],
                    y=b_sub["RANK"],
                    mode="lines+markers+text",
                    name=brand,
                    line=dict(color=col, width=2.8),
                    marker=dict(size=7, color=col),
                    text=[f"#{int(r)}" if y == max_year else "" for y, r in zip(b_sub["ANIO"], b_sub["RANK"])],
                    textposition="middle right",
                    textfont=dict(size=10, color=col),
                    hovertemplate=f"<b>{brand}</b> (%{{x}})<br>Rank: #%{{y:.0f}}<extra></extra>",
                )
            )
        fig_bump.update_layout(
            height=330,
            margin=dict(l=10, r=35, t=28, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10)),
            xaxis=dict(dtick=1, showgrid=False, tickfont=dict(size=11)),
            yaxis=dict(autorange="reversed", dtick=1, range=[7.5, 0.5], showgrid=True, gridcolor="#F1F5F9", title="Rank"),
        )
        st.plotly_chart(fig_bump, use_container_width=True)

    st.write("")
    st.markdown(
        f"""
        <p class="chart-title">10. Head-to-Head Automaker Benchmark ({period_tag})</p>
        <p class="chart-sub">Historical trajectory comparison across selected automakers</p>
        """,
        unsafe_allow_html=True,
    )
    avail_oems = (
        ps.groupby("MARCA", as_index=False)["PRODUCCION"]
        .sum()
        .sort_values("PRODUCCION", ascending=False)["MARCA"]
        .tolist()
    )
    if len(avail_oems) >= 2:
        hh1, hh2, hh3 = st.columns([1.0, 1.0, 1.0])
        with hh1:
            oem_a = st.selectbox("Automaker A", options=avail_oems, index=0, key="hh_a")
        with hh2:
            oem_b = st.selectbox("Automaker B", options=avail_oems, index=min(1, len(avail_oems) - 1), key="hh_b")
        with hh3:
            hh_metric = st.radio(
                "Metric",
                ["Assembly (PRODUCCION)", "Domestic Retail (VENTAS)"],
                horizontal=True,
                key="hh_metric",
            )
        col_m = "PRODUCCION" if "Assembly" in hh_metric else "VENTAS"
        hh_hist = (
            ps[(ps["ANIO"].between(year_range[0], year_range[1])) & (ps["MARCA"].isin([oem_a, oem_b]))]
            .groupby(["ANIO", "MARCA"], as_index=False)[col_m]
            .sum()
        )
        fig_hh = go.Figure()
        for brand_name, col_hex, txt_pos in [(oem_a, SE_GUINDA, "top center"), (oem_b, SE_TEAL, "bottom center")]:
            sub_h = hh_hist[hh_hist["MARCA"] == brand_name].sort_values("ANIO")
            fig_hh.add_trace(
                go.Scatter(
                    x=sub_h["ANIO"],
                    y=sub_h[col_m],
                    mode="lines+markers+text",
                    name=brand_name,
                    line=dict(color=col_hex, width=3),
                    marker=dict(size=6, color=col_hex),
                    text=[fmt_units(v) if y == max_year else "" for y, v in zip(sub_h["ANIO"], sub_h[col_m])],
                    textposition=txt_pos,
                    textfont=dict(size=10, color=col_hex),
                    hovertemplate=f"<b>{brand_name}</b> (%{{x}})<br>Units: %{{y:,.0f}}<extra></extra>",
                )
            )
        fig_hh.update_layout(
            height=295,
            margin=dict(l=10, r=30, t=24, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=11)),
            xaxis=dict(dtick=1, showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9", rangemode="tozero", tickformat=".2s"),
        )
        st.plotly_chart(fig_hh, use_container_width=True)
        st.markdown(
            f"""
            <div class="chart-caveat">
                ⓘ <strong>Panel Scope:</strong> AMIA-affiliated RAIAVL registry; non-reporting Chinese brands
                (<strong>BYD, MG, Chirey, Omoda, Geely</strong>) and import-only brands without Mexican plants are excluded.
            </div>
            """,
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------------------------
# TAB 4: SEASONALITY & SHOCK MATRIX (2 CHARTS)
# ------------------------------------------------------------------------------
with tab4:
    st.markdown(
        f"""
        <div class="sec-header">
            <span class="sec-badge">04</span>
            <h2 class="sec-title">Seasonality Matrix &amp; Cumulative YTD Pace</h2>
        </div>
        <div class="sec-caption">Monthly heatmap isolating the 2020 plant shutdown and tracking {max_year} cumulative pace.</div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2 = st.columns([1.2, 1.0], gap="large")

    with m1:
        st.markdown(
            f"""
            <p class="chart-title">11. Monthly Assembly Seasonality Heatmap (Year × Month)</p>
            <p class="chart-sub">Monthly assembly intensity (2015–{max_year}) · Isolates 2020 plant shutdowns</p>
            """,
            unsafe_allow_html=True,
        )
        heat_df = (
            ps_full[ps_full["ANIO"].between(max(year_range[0], 2015), year_range[1])]
            .groupby(["ANIO", "MES"], as_index=False)["PRODUCCION"]
            .sum()
        )
        heat_piv = heat_df.pivot(index="ANIO", columns="MES", values="PRODUCCION").sort_index(ascending=False)
        for m_idx in range(1, 13):
            if m_idx not in heat_piv.columns:
                heat_piv[m_idx] = np.nan
        heat_piv = heat_piv[list(range(1, 13))]
        x_months = [MONTH_SHORT[m] for m in range(1, 13)]
        y_years = [str(y) for y in heat_piv.index]

        fig_heat = go.Figure(
            data=[
                go.Heatmap(
                    z=heat_piv.values,
                    x=x_months,
                    y=y_years,
                    colorscale=[
                        [0.0, "#F8FAFC"],
                        [0.35, "#99F6E4"],
                        [0.70, SE_TEAL],
                        [1.0, SE_GUINDA_DARK],
                    ],
                    hovertemplate="<b>%{y} · %{x}</b><br>Assembly: %{z:,.0f} units<extra></extra>",
                    colorbar=dict(title="Units", thickness=12, tickformat=".2s"),
                )
            ]
        )
        fig_heat.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=24, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(side="top"),
            yaxis=dict(type="category"),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    with m2:
        st.markdown(
            f"""
            <p class="chart-title">12. Cumulative YTD Assembly Pace (Jan–Oct)</p>
            <p class="chart-sub">{max_year} trajectory vs. {prev_year} and 2022–{prev_year} average</p>
            """,
            unsafe_allow_html=True,
        )
        cum_df = (
            ps_full[(ps_full["ANIO"] >= 2022) & (ps_full["MES"] <= max_month_latest)]
            .groupby(["ANIO", "MES"], as_index=False)["PRODUCCION"]
            .sum()
            .sort_values(["ANIO", "MES"])
        )
        cum_df["CUM_PROD"] = cum_df.groupby("ANIO")["PRODUCCION"].cumsum()

        avg_hist = (
            cum_df[cum_df["ANIO"].between(2022, prev_year)]
            .groupby("MES", as_index=False)["CUM_PROD"]
            .mean()
            .sort_values("MES")
        )

        fig_cum = go.Figure()
        for yr, col_c, w_c in [(max_year, SE_GUINDA, 3.2), (prev_year, SE_TEAL, 2.8)]:
            sub_c = cum_df[cum_df["ANIO"] == yr]
            if not sub_c.empty:
                fig_cum.add_trace(
                    go.Scatter(
                        x=[MONTH_SHORT[m] for m in sub_c["MES"]],
                        y=sub_c["CUM_PROD"],
                        mode="lines+markers",
                        name=str(yr),
                        line=dict(color=col_c, width=w_c),
                        marker=dict(size=6, color=col_c),
                        hovertemplate=f"<b>{yr} (%{{x}} YTD)</b><br>Cumulative: %{{y:,.0f}} units<extra></extra>",
                    )
                )
        if not avg_hist.empty:
            fig_cum.add_trace(
                go.Scatter(
                    x=[MONTH_SHORT[m] for m in avg_hist["MES"]],
                    y=avg_hist["CUM_PROD"],
                    mode="lines+markers",
                    name=f"2022–{prev_year} Avg",
                    line=dict(color=SE_AMBER, width=2.2, dash="dot"),
                    marker=dict(size=5, color=SE_AMBER),
                    hovertemplate=f"<b>2022–{prev_year} Avg (%{{x}} YTD)</b><br>Cumulative: %{{y:,.0f}} units<extra></extra>",
                )
            )
        fig_cum.update_layout(
            height=350,
            margin=dict(l=10, r=15, t=24, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=11)),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9", rangemode="tozero", tickformat=".2s"),
        )
        st.plotly_chart(fig_cum, use_container_width=True)


# ------------------------------------------------------------------------------
# TAB 5: TARIFF WATERFALL SIMULATOR & POLICY LEVERS (CHART 13 + ACTION CARDS)
# ------------------------------------------------------------------------------
with tab5:
    st.markdown(
        f"""
        <div class="sec-header">
            <span class="sec-badge">05</span>
            <h2 class="sec-title">Tariff Waterfall Simulator &amp; Policy Levers</h2>
        </div>
        <div class="sec-caption">Stress-test U.S. tariff contraction against non-U.S. diversification and domestic incentives.</div>
        """,
        unsafe_allow_html=True,
    )

    sim_left, sim_right = st.columns([1.0, 1.45], gap="large")

    with sim_left:
        us_shock_pct = st.slider(
            "Additional U.S. Tariff Shock (%)", min_value=-25, max_value=10, value=-8, step=1
        )
        non_us_boost_pct = st.slider(
            "Non-U.S. Diversification Gain (%)", min_value=0, max_value=30, value=12, step=1
        )
        dom_boost_pct = st.slider(
            "Domestic Market Stimulus (%)", min_value=0, max_value=20, value=5, step=1
        )

        dom_curr = ps.loc[ps["ANIO"] == max_year, "VENTAS"].sum()
        delta_us = us_curr * (us_shock_pct / 100.0)
        delta_non_us = non_us_curr * (non_us_boost_pct / 100.0)
        delta_dom = dom_curr * (dom_boost_pct / 100.0)
        net_delta = delta_us + delta_non_us + delta_dom
        projected_total = prod_curr + net_delta
        net_cls = "pill-pos" if net_delta >= 0 else "pill-neg"

        st.markdown(
            f"""
            <div class="kpi-card" style="margin-top:0.4rem;">
                <div class="kpi-top">
                    <span>Simulated Net Assembly Impact</span>
                </div>
                <div class="kpi-number">{net_delta:+,.0f} units</div>
                <span class="kpi-pill {net_cls}">Projected Total: {fmt_units(projected_total)} units</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with sim_right:
        st.markdown(
            f"""
            <p class="chart-title">13. Assembly Stress-Test Waterfall ({period_tag} Baseline)</p>
            <p class="chart-sub">Bridge from current assembly to post-shock projected volume</p>
            """,
            unsafe_allow_html=True,
        )
        fig_wf = go.Figure(
            data=[
                go.Waterfall(
                    orientation="v",
                    measure=["absolute", "relative", "relative", "relative", "total"],
                    x=[
                        f"{max_year} Baseline",
                        "U.S. Tariff Shock",
                        "Non-U.S. Diversification",
                        "Domestic Stimulus",
                        "Projected Volume",
                    ],
                    y=[prod_curr, delta_us, delta_non_us, delta_dom, 0],
                    text=[
                        fmt_units(prod_curr),
                        f"{delta_us:+,.0f}",
                        f"{delta_non_us:+,.0f}",
                        f"{delta_dom:+,.0f}",
                        fmt_units(projected_total),
                    ],
                    textposition="outside",
                    textfont=dict(size=10, color=SE_TEXT),
                    connector={"line": {"color": "#CBD5E1", "width": 1.5}},
                    increasing={"marker": {"color": SE_TEAL}},
                    decreasing={"marker": {"color": SE_GUINDA}},
                    totals={"marker": {"color": SE_AMBER}},
                    showlegend=False,
                )
            ]
        )
        # Explicit legend markers for Waterfall color coding
        for wf_lbl, wf_col in [
            ("Baseline / Projected Total", SE_AMBER),
            ("Negative Tariff Shock", SE_GUINDA),
            ("Positive Diversification / Stimulus", SE_TEAL),
        ]:
            fig_wf.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    name=wf_lbl,
                    marker=dict(size=10, symbol="square", color=wf_col),
                )
            )
        fig_wf.update_layout(
            height=340,
            margin=dict(l=10, r=10, t=32, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10)),
            yaxis=dict(
                showgrid=True,
                gridcolor="#F1F5F9",
                range=[0, max(prod_curr, projected_total) * 1.16],
                tickformat=".2s",
            ),
        )
        st.plotly_chart(fig_wf, use_container_width=True)

    st.write("")
    r1, r2, r3 = st.columns(3, gap="medium")

    with r1:
        st.markdown(
            f"""
            <div class="rec-card" style="border-top-color:{SE_GUINDA};">
                <span class="rec-tag guinda">01 · USMCA Shield</span>
                <div class="rec-title">Regional Content Compliance</div>
                <div class="rec-stats">
                    <div class="rec-stat-box">
                        <div class="rec-stat-num">{fmt_units(us_curr)}</div>
                        <div class="rec-stat-lbl">U.S.-bound units</div>
                    </div>
                    <div class="rec-stat-box">
                        <div class="rec-stat-num">{suv_exp_share:.1f}%</div>
                        <div class="rec-stat-lbl">SUVs exported abroad</div>
                    </div>
                </div>
                <div class="rec-action"><strong>Action:</strong> Accelerate Tier-1/Tier-2 North American powertrain &amp; battery localization in SUV plants to preserve zero-tariff USMCA qualification.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r2:
        st.markdown(
            f"""
            <div class="rec-card">
                <span class="rec-tag">02 · Trade Diversification</span>
                <div class="rec-title">Expand LATAM &amp; EU Corridors</div>
                <div class="rec-stats">
                    <div class="rec-stat-box">
                        <div class="rec-stat-num">{fmt_units(non_us_curr)}</div>
                        <div class="rec-stat-lbl">Non-U.S. volume</div>
                    </div>
                    <div class="rec-stat-box">
                        <div class="rec-stat-num">{non_us_yoy:+.1f}%</div>
                        <div class="rec-stat-lbl">YoY growth pace</div>
                    </div>
                </div>
                <div class="rec-action"><strong>Action:</strong> Leverage ACE-55 (Brazil/Mercosur) and EU-Mexico trade agreements to absorb excess compact &amp; SUV assembly capacity.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r3:
        st.markdown(
            f"""
            <div class="rec-card" style="border-top-color:{SE_AMBER};">
                <span class="rec-tag amber">03 · Domestic Anchor</span>
                <div class="rec-title">Strengthen Local Fleet Renewal</div>
                <div class="rec-stats">
                    <div class="rec-stat-box">
                        <div class="rec-stat-num">{sub_dom_share:.1f}%</div>
                        <div class="rec-stat-lbl">Subcompacts sold locally</div>
                    </div>
                    <div class="rec-stat-box">
                        <div class="rec-stat-num">{fmt_units(dom_curr)}</div>
                        <div class="rec-stat-lbl">{period_tag} retail sales</div>
                    </div>
                </div>
                <div class="rec-action"><strong>Action:</strong> Target NAFIN/Bancomext financing incentives toward domestically assembled subcompacts and light commercial pickups.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )