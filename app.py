import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIG & SECRETARÍA DE ECONOMÍA THEME (gob.mx/se)
# ==============================================================================
st.set_page_config(
    page_title="SE · Mexican Light-Vehicle Industry (RAIAVL)",
    page_icon="🇲🇽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Official Gobierno de México / Secretaría de Economía Palette
SE_GUINDA = "#611232"
SE_GUINDA_DARK = "#470D24"
SE_VERDE = "#1E5B4F"
SE_VERDE_LIGHT = "#E6F0EE"
SE_DORADO = "#A57F2C"
SE_DORADO_LIGHT = "#BC955C"
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
        padding-top: 1.4rem;
        padding-bottom: 2.5rem;
        max-width: 1320px;
    }}

    /* Hero Banner (Secretaría de Economía Institutional Style) */
    .se-hero {{
        background: linear-gradient(125deg, {SE_GUINDA_DARK} 0%, {SE_GUINDA} 48%, {SE_VERDE} 100%);
        border-bottom: 4px solid {SE_DORADO_LIGHT};
        border-radius: 14px;
        padding: 1.5rem 1.8rem;
        color: #FFFFFF;
        margin-bottom: 1.25rem;
        box-shadow: 0 6px 20px rgba(22, 26, 29, 0.10);
    }}
    .se-kicker {{
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #E8D5B5;
        margin-bottom: 0.35rem;
    }}
    .se-title {{
        font-size: 1.75rem;
        font-weight: 800;
        line-height: 1.15;
        margin: 0 0 0.3rem 0;
        color: #FFFFFF;
    }}
    .se-subtitle {{
        font-size: 0.92rem;
        color: rgba(255, 255, 255, 0.86);
        margin: 0 0 1.1rem 0;
    }}
    .hero-kpi-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.85rem;
    }}
    .hero-kpi-box {{
        background: rgba(255, 255, 255, 0.10);
        border: 1px solid rgba(255, 255, 255, 0.20);
        border-radius: 10px;
        padding: 0.7rem 0.9rem;
        backdrop-filter: blur(4px);
    }}
    .hero-kpi-label {{
        font-size: 0.70rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #E8D5B5;
        font-weight: 600;
    }}
    .hero-kpi-val {{
        font-size: 1.35rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.2;
        margin-top: 0.15rem;
    }}
    .hero-kpi-sub {{
        font-size: 0.74rem;
        color: rgba(255, 255, 255, 0.82);
    }}

    /* Section Header Badge */
    .sec-header {{
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin: 1.35rem 0 0.15rem 0;
    }}
    .sec-badge {{
        background-color: {SE_GUINDA};
        color: #FFFFFF;
        font-size: 0.74rem;
        font-weight: 800;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        letter-spacing: 0.04em;
    }}
    .sec-title {{
        font-size: 1.15rem;
        font-weight: 800;
        color: {SE_TEXT};
        margin: 0;
    }}
    .sec-caption {{
        font-size: 0.84rem;
        color: {SE_SLATE};
        margin-bottom: 0.85rem;
    }}

    /* Number-Only KPI Cards with Instant Hover Pop-up */
    .kpi-card {{
        position: relative;
        background: {SE_CARD};
        border: 1px solid #E2E8F0;
        border-top: 3px solid {SE_GUINDA};
        border-radius: 12px;
        padding: 0.95rem 1.1rem;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        cursor: default;
    }}
    .kpi-card.verde {{
        border-top-color: {SE_VERDE};
    }}
    .kpi-card.dorado {{
        border-top-color: {SE_DORADO};
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
        z-index: 50;
    }}
    .kpi-top {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.78rem;
        font-weight: 600;
        color: {SE_SLATE};
    }}
    .kpi-info-icon {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: #F1F5F9;
        color: {SE_GUINDA};
        font-size: 0.70rem;
        font-weight: 800;
        border: 1px solid #CBD5E1;
    }}
    .kpi-number {{
        font-size: 1.85rem;
        font-weight: 800;
        color: {SE_TEXT};
        line-height: 1.15;
        margin: 0.35rem 0 0.45rem 0;
        letter-spacing: -0.02em;
    }}
    .kpi-pill {{
        display: inline-block;
        font-size: 0.74rem;
        font-weight: 700;
        padding: 0.18rem 0.55rem;
        border-radius: 999px;
    }}
    .pill-neg {{
        background: #FDF2F4;
        color: {SE_GUINDA};
    }}
    .pill-pos {{
        background: {SE_VERDE_LIGHT};
        color: {SE_VERDE};
    }}
    .pill-neu {{
        background: #FBF6EC;
        color: #8A661C;
    }}

    /* Floating Hover Pop-up Tooltip */
    .kpi-tooltip {{
        visibility: hidden;
        opacity: 0;
        position: absolute;
        left: 0;
        right: 0;
        top: calc(100% + 8px);
        background: #161A1D;
        color: #F8FAFC;
        font-size: 0.78rem;
        line-height: 1.45;
        padding: 0.75rem 0.9rem;
        border-radius: 9px;
        border-left: 3px solid {SE_DORADO_LIGHT};
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.22);
        transition: opacity 0.16s ease, visibility 0.16s ease;
        z-index: 999;
        pointer-events: none;
    }}
    .kpi-card:hover .kpi-tooltip {{
        visibility: visible;
        opacity: 1;
    }}

    /* Chart Headers & Chart-Specific Micro-Footnote */
    .chart-header-row {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.25rem;
    }}
    .chart-title {{
        font-size: 0.98rem;
        font-weight: 700;
        color: {SE_TEXT};
        margin: 0;
    }}
    .chart-sub {{
        font-size: 0.79rem;
        color: {SE_SLATE};
        margin: 0;
    }}
    .chart-caveat {{
        font-size: 0.73rem;
        color: {SE_SLATE};
        background: #F8FAFC;
        border-left: 3px solid {SE_DORADO};
        padding: 0.35rem 0.65rem;
        border-radius: 0 6px 6px 0;
        margin-top: -0.35rem;
        margin-bottom: 0.6rem;
    }}

    /* Compact Recommendation Cards */
    .rec-card {{
        background: {SE_CARD};
        border: 1px solid #E2E8F0;
        border-top: 3px solid {SE_VERDE};
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
        border-radius: 5px;
        background: {SE_VERDE_LIGHT};
        color: {SE_VERDE};
        margin-bottom: 0.45rem;
    }}
    .rec-tag.guinda {{
        background: #FDF2F4;
        color: {SE_GUINDA};
    }}
    .rec-tag.dorado {{
        background: #FBF6EC;
        color: #8A661C;
    }}
    .rec-title {{
        font-size: 1.02rem;
        font-weight: 800;
        color: {SE_TEXT};
        margin-bottom: 0.55rem;
    }}
    .rec-stats {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.5rem;
        margin-bottom: 0.65rem;
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
        font-size: 0.70rem;
        color: {SE_SLATE};
    }}
    .rec-action {{
        font-size: 0.80rem;
        color: {SE_TEXT};
        border-top: 1px solid #F1F5F9;
        padding-top: 0.55rem;
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

SEGMENT_MAP = {
    "SUV": "SUVs",
    "SUVS": "SUVs",
    "CAMIONES LIGEROS": "SUVs",
    "PICK UP": "Pickups",
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
    key = str(val).strip().upper()
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
# 3. COMPACT SIDEBAR CONTROLS
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

ps = prod_sales_df.copy()
ex = exports_df.copy()

if ytd_mode:
    ps = ps[ps["MES"] <= max_month_latest]
    ex = ex[ex["MES"] <= max_month_latest]

if sel_brands:
    ps = ps[ps["MARCA"].isin(sel_brands)]
    ex = ex[ex["MARCA"].isin(sel_brands)]

if sel_segments:
    ps = ps[ps["SEG_CLEAN"].isin(sel_segments)]
    ex = ex[ex["SEG_CLEAN"].isin(sel_segments)]


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

suv_exp_curr = ex.loc[(ex["ANIO"] == max_year) & (ex["SEG_CLEAN"] == "SUVs"), "EXPORTACION"].sum()
suv_exp_share = min((suv_exp_curr / suv_curr * 100.0), 99.9) if suv_curr > 0 else 0.0

sub_sales_curr = ps.loc[(ps["ANIO"] == max_year) & (ps["SEG_CLEAN"] == "Subcompacts"), "VENTAS"].sum()
sub_exp_curr = ex.loc[(ex["ANIO"] == max_year) & (ex["SEG_CLEAN"] == "Subcompacts"), "EXPORTACION"].sum()
sub_dom_share = (
    (sub_sales_curr / (sub_sales_curr + sub_exp_curr) * 100.0)
    if (sub_sales_curr + sub_exp_curr) > 0
    else 0.0
)

period_tag = f"Jan–Oct {max_year} YTD" if ytd_mode else f"Full Year {max_year}"


# ==============================================================================
# 5. HERO HEADER
# ==============================================================================
st.markdown(
    f"""
    <div class="se-hero">
        <div class="se-kicker">Secretaría de Economía · México · Registro Administrativo (RAIAVL 2005–{max_year})</div>
        <div class="se-title">Mexican Light-Vehicle Industry: Tariff Exposure &amp; Structural Split</div>
        <div class="se-subtitle">Assembly performance, U.S. vs. non-U.S. export resilience, and domestic segment buffer ({period_tag})</div>
        <div class="hero-kpi-grid">
            <div class="hero-kpi-box">
                <div class="hero-kpi-label">{period_tag} Assembly</div>
                <div class="hero-kpi-val">{fmt_units(prod_curr)}</div>
                <div class="hero-kpi-sub">{prod_yoy:+.1f}% vs. {prev_year}</div>
            </div>
            <div class="hero-kpi-box">
                <div class="hero-kpi-label">U.S. Exports</div>
                <div class="hero-kpi-val">{fmt_units(us_curr)}</div>
                <div class="hero-kpi-sub">{us_yoy:+.1f}% vs. {prev_year}</div>
            </div>
            <div class="hero-kpi-box">
                <div class="hero-kpi-label">Non-U.S. Exports</div>
                <div class="hero-kpi-val">{fmt_units(non_us_curr)}</div>
                <div class="hero-kpi-sub">{non_us_yoy:+.1f}% shock absorber</div>
            </div>
            <div class="hero-kpi-box">
                <div class="hero-kpi-label">SUV Assembly Mix</div>
                <div class="hero-kpi-val">{suv_mix:.1f}%</div>
                <div class="hero-kpi-sub">{suv_exp_share:.1f}% exported abroad</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# 6. SECTION 01: KEY NUMBERS WITH HOVER POP-UPS & ASSEMBLY CHARTS
# ==============================================================================
st.markdown(
    f"""
    <div class="sec-header">
        <span class="sec-badge">01</span>
        <h2 class="sec-title">Output &amp; Trade Inflection</h2>
    </div>
    <div class="sec-caption">Hover over any metric card (ⓘ) to inspect structural drivers and segment details.</div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)

with k1:
    pill_cls = "pill-neg" if prod_yoy < 0 else "pill-pos"
    arrow = "↓" if prod_yoy < 0 else "↑"
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span>Total Assembly ({period_tag})</span>
                <span class="kpi-info-icon">ⓘ</span>
            </div>
            <div class="kpi-number">{fmt_units(prod_curr)}</div>
            <span class="kpi-pill {pill_cls}">{arrow} {prod_yoy:+.1f}% YoY vs. {prev_year}</span>
            <div class="kpi-tooltip">
                <strong>Output Inflection:</strong> Total assembly stands at <b>{fmt_units(prod_curr)} units</b>
                ({prod_yoy:+.1f}% YoY), led by <b>SUVs ({suv_mix:.1f}% of mix)</b>. Pickups remain ahead of
                seasonal pace, while Compacts and SUVs absorbed the tariff pullback.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    pill_cls = "pill-neg" if us_yoy < 0 else "pill-pos"
    arrow = "↓" if us_yoy < 0 else "↑"
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span>U.S.-Bound Shipments</span>
                <span class="kpi-info-icon">ⓘ</span>
            </div>
            <div class="kpi-number">{fmt_units(us_curr)}</div>
            <span class="kpi-pill {pill_cls}">{arrow} {us_yoy:+.1f}% YoY</span>
            <div class="kpi-tooltip">
                <strong>Tariff Pressure:</strong> U.S.-bound shipments moved <b>{us_yoy:+.1f}% YoY</b>
                ({fmt_units(us_curr)} units), reflecting heightened North American trade friction in {max_year}.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    pill_cls = "pill-pos" if non_us_yoy >= 0 else "pill-neg"
    arrow = "↑" if non_us_yoy >= 0 else "↓"
    st.markdown(
        f"""
        <div class="kpi-card verde">
            <div class="kpi-top">
                <span>Non-U.S. Exports</span>
                <span class="kpi-info-icon">ⓘ</span>
            </div>
            <div class="kpi-number">{fmt_units(non_us_curr)}</div>
            <span class="kpi-pill {pill_cls}">{arrow} {non_us_yoy:+.1f}% YoY</span>
            <div class="kpi-tooltip">
                <strong>Trade Divergence:</strong> Non-U.S. exports expanded <b>{non_us_yoy:+.1f}% YoY</b>
                ({fmt_units(non_us_curr)} units), confirming Latin America and Europe as critical shock absorbers.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        f"""
        <div class="kpi-card dorado">
            <div class="kpi-top">
                <span>Two-Speed Segment Split</span>
                <span class="kpi-info-icon">ⓘ</span>
            </div>
            <div class="kpi-number">{suv_exp_share:.1f}% / {sub_dom_share:.1f}%</div>
            <span class="kpi-pill pill-neu">SUV Export vs. Subcompact Domestic</span>
            <div class="kpi-tooltip">
                <strong>Two-Speed Split:</strong> <b>{suv_exp_share:.1f}% of Mexican-built SUVs</b> are exported
                abroad (highest tariff sensitivity), whereas <b>{sub_dom_share:.1f}% of Subcompacts</b> are sold
                domestically inside Mexico.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

c1, c2 = st.columns([1.15, 1.0], gap="large")

with c1:
    st.markdown(
        f"""
        <div class="chart-header-row">
            <div>
                <p class="chart-title">Annual Light-Vehicle Assembly ({period_tag})</p>
                <p class="chart-sub">2026 pullback interrupts post-COVID recovery</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    ann_prod = (
        ps[ps["ANIO"].between(year_range[0], year_range[1])]
        .groupby("ANIO", as_index=False)["PRODUCCION"]
        .sum()
        .sort_values("ANIO")
    )
    colors = [
        SE_GUINDA if y == max_year else (SE_VERDE if y == prev_year else "#CBD5E1")
        for y in ann_prod["ANIO"]
    ]
    fig_ann = go.Figure(
        data=[
            go.Bar(
                x=ann_prod["ANIO"],
                y=ann_prod["PRODUCCION"],
                marker_color=colors,
                text=[fmt_units(v) for v in ann_prod["PRODUCCION"]],
                textposition="outside",
                textfont=dict(size=10, color=SE_TEXT),
                hovertemplate="<b>%{x}</b><br>Assembly: %{y:,.0f} units<extra></extra>",
            )
        ]
    )
    if year_range[0] <= 2020 <= year_range[1]:
        fig_ann.add_vrect(
            x0=2019.5, x1=2021.5, fillcolor="#94A3B8", opacity=0.14, line_width=0,
            annotation_text="COVID-19 / Chips", annotation_position="top left",
            annotation_font=dict(size=10, color=SE_SLATE),
        )
    if year_range[1] >= 2026:
        fig_ann.add_vrect(
            x0=2025.5, x1=2026.5, fillcolor=SE_GUINDA, opacity=0.08, line_width=0,
            annotation_text="2026 Tariffs", annotation_position="top right",
            annotation_font=dict(size=10, color=SE_GUINDA),
        )
    fig_ann.update_layout(
        height=330,
        margin=dict(l=10, r=10, t=28, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(dtick=1, showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", rangemode="tozero", tickformat=".2s"),
        showlegend=False,
    )
    st.plotly_chart(fig_ann, use_container_width=True)
    st.markdown(
        f"""
        <div class="chart-caveat" title="ESTATUS: 2005–2023 = Definitive Figures; 2024–Sep 2026 = Revised Figures; Oct 2026 = Preliminary Figures.">
            ⓘ <strong>Coverage &amp; Vintage:</strong> Matched Jan–Oct YTD comparison (10 mos) to avoid seasonal drop.
            <code>ESTATUS</code>: 2005–2023 Definitive · 2024–Sep 2026 Revised · Oct 2026 Preliminary.
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    h_left, h_right = st.columns([1.4, 1.0])
    with h_left:
        st.markdown(
            f"""
            <p class="chart-title">Assembly by Vehicle Segment</p>
            <p class="chart-sub">SUVs &amp; Pickups anchor Mexican output</p>
            """,
            unsafe_allow_html=True,
        )
    with h_right:
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

    seg_palette = {
        "SUVs": SE_GUINDA,
        "Pickups": SE_VERDE,
        "Compacts": SE_DORADO,
        "Subcompacts": "#64748B",
        "Other": "#CBD5E1",
    }
    fig_seg = go.Figure()
    for seg_name in ["SUVs", "Pickups", "Compacts", "Subcompacts", "Other"]:
        sub_df = seg_grp[seg_grp["SEG_GROUP"] == seg_name].sort_values("ANIO")
        if not sub_df.empty:
            fig_seg.add_trace(
                go.Bar(
                    x=sub_df["ANIO"],
                    y=sub_df["VAL"],
                    name=seg_name,
                    marker_color=seg_palette[seg_name],
                    hovertemplate=hover_tmpl,
                )
            )
    fig_seg.update_layout(
        barmode="stack",
        height=330,
        margin=dict(l=10, r=10, t=28, b=10),
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


# ==============================================================================
# 7. SECTION 02: TRADE DIVERGENCE (U.S. VS. NON-U.S.)
# ==============================================================================
st.markdown(
    f"""
    <div class="sec-header">
        <span class="sec-badge" style="background-color:{SE_VERDE};">02</span>
        <h2 class="sec-title">Trade Divergence: U.S. Exposure vs. Global Shock Absorbers</h2>
    </div>
    <div class="sec-caption">Non-U.S. export destinations expanded while U.S.-bound shipments contracted.</div>
    """,
    unsafe_allow_html=True,
)

t1, t2 = st.columns([1.15, 1.0], gap="large")

with t1:
    st.markdown(
        f"""
        <p class="chart-title">Export Trajectory: U.S. vs. Rest of World ({period_tag})</p>
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
    for dest_label, line_col in [("United States", SE_GUINDA), ("Non-U.S. Markets", SE_VERDE)]:
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
        height=320,
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
        <p class="chart-title">Top Non-U.S. Destinations ({period_tag})</p>
        <p class="chart-sub">Canada, Germany &amp; Latin America buffer North American tariff friction</p>
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
        .head(7)
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
                marker_color=SE_VERDE,
                text=top_dest["LABEL"],
                textposition="outside",
                textfont=dict(size=10, color=SE_TEXT),
                hovertemplate="<b>%{y}</b><br>Exports: %{x:,.0f} units<extra></extra>",
            )
        ]
    )
    fig_dest.update_layout(
        height=320,
        margin=dict(l=10, r=65, t=28, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", rangemode="tozero", tickformat=".2s"),
        yaxis=dict(showgrid=False, tickfont=dict(size=11)),
    )
    st.plotly_chart(fig_dest, use_container_width=True)


# ==============================================================================
# 8. SECTION 03: TWO-SPEED SEGMENT SPLIT & DOMESTIC MARKET SCOPE
# ==============================================================================
st.markdown(
    f"""
    <div class="sec-header">
        <span class="sec-badge" style="background-color:{SE_DORADO};">03</span>
        <h2 class="sec-title">Two-Speed Segment Split &amp; Domestic Shield</h2>
    </div>
    <div class="sec-caption">Export-dependent SUVs vs. domestically absorbed Subcompacts and Compacts.</div>
    """,
    unsafe_allow_html=True,
)

s1, s2 = st.columns([1.05, 1.05], gap="large")

with s1:
    st.markdown(
        f"""
        <p class="chart-title">Export vs. Domestic Sales Orientation by Segment ({max_year})</p>
        <p class="chart-sub">Share of total destination volume shipped abroad vs. sold in Mexico</p>
        """,
        unsafe_allow_html=True,
    )
    seg_exp = (
        ex[ex["ANIO"] == max_year]
        .groupby("SEG_CLEAN", as_index=False)["EXPORTACION"]
        .sum()
    )
    seg_dom = (
        ps[ps["ANIO"] == max_year]
        .groupby("SEG_CLEAN", as_index=False)["VENTAS"]
        .sum()
    )
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
            marker_color=SE_VERDE,
            text=[f"{v:.1f}%" if v >= 12 else "" for v in seg_split["DOM_PCT"]],
            textposition="inside",
            textfont=dict(color="white", size=10),
            hovertemplate="<b>%{y}</b><br>Domestic Sales: %{x:.1f}%<extra></extra>",
        )
    )
    fig_split.update_layout(
        barmode="stack",
        height=320,
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
        <div class="chart-caveat" title="GM Silverado 2500 / GMC Sierra and Stellantis RAM 2500 record export shipments in 2025–2026 from inventory/model-code splits against zero new production rows.">
            ⓘ <strong>Heavy-Duty Pickup Lag:</strong> GM Silverado 2500 / GMC Sierra and Stellantis RAM 2500 record
            2025–2026 export shipments from inventory/model-code splits against zero new production rows.
        </div>
        """,
        unsafe_allow_html=True,
    )

with s2:
    st.markdown(
        f"""
        <p class="chart-title">Domestic Retail Sales by Automaker — Top 10 ({period_tag})</p>
        <p class="chart-sub">AMIA-affiliated registry leaders anchoring internal demand</p>
        """,
        unsafe_allow_html=True,
    )
    brand_dom = (
        ps[ps["ANIO"] == max_year]
        .groupby("MARCA", as_index=False)["VENTAS"]
        .sum()
        .sort_values("VENTAS", ascending=False)
        .head(10)
        .sort_values("VENTAS", ascending=True)
    )
    fig_brand = go.Figure(
        data=[
            go.Bar(
                x=brand_dom["VENTAS"],
                y=brand_dom["MARCA"],
                orientation="h",
                marker_color=SE_DORADO,
                text=[fmt_units(v) for v in brand_dom["VENTAS"]],
                textposition="outside",
                textfont=dict(size=10, color=SE_TEXT),
                hovertemplate="<b>%{y}</b><br>Domestic Sales: %{x:,.0f} units<extra></extra>",
            )
        ]
    )
    fig_brand.update_layout(
        height=320,
        margin=dict(l=10, r=45, t=28, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", rangemode="tozero", tickformat=".2s"),
        yaxis=dict(showgrid=False, tickfont=dict(size=11)),
    )
    st.plotly_chart(fig_brand, use_container_width=True)
    st.markdown(
        f"""
        <div class="chart-caveat" title="RAIAVL inner-joins Production, Exports, and Retail Sales of AMIA-affiliated automakers.">
            ⓘ <strong>Panel Scope:</strong> AMIA-affiliated RAIAVL registry; non-reporting Chinese brands
            (<strong>BYD, MG, Chirey, Omoda, Geely</strong>) and import-only brands without Mexican plants are excluded.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# 9. SECTION 04: POLICY SIMULATOR & STRATEGIC ACTIONS
# ==============================================================================
st.markdown(
    f"""
    <div class="sec-header">
        <span class="sec-badge">04</span>
        <h2 class="sec-title">Policy Levers &amp; Tariff Stress-Test</h2>
    </div>
    <div class="sec-caption">Adjust U.S. tariff contraction and non-U.S. market absorption to evaluate net assembly impact.</div>
    """,
    unsafe_allow_html=True,
)

sim_c1, sim_c2, sim_c3 = st.columns([1.0, 1.0, 1.2], gap="medium")
with sim_c1:
    us_shock_pct = st.slider("Additional U.S. Tariff Shock (%)", min_value=-25, max_value=10, value=-8, step=1)
with sim_c2:
    non_us_boost_pct = st.slider("Non-U.S. Diversification Gain (%)", min_value=0, max_value=30, value=12, step=1)
with sim_c3:
    delta_us_units = us_curr * (us_shock_pct / 100.0)
    delta_non_us_units = non_us_curr * (non_us_boost_pct / 100.0)
    net_impact_units = delta_us_units + delta_non_us_units
    net_cls = "pill-pos" if net_impact_units >= 0 else "pill-neg"
    st.markdown(
        f"""
        <div class="kpi-card verde" style="padding: 0.7rem 1rem;">
            <div class="kpi-top">
                <span>Simulated Net Export Delta</span>
                <span class="kpi-info-icon">ⓘ</span>
            </div>
            <div class="kpi-number" style="font-size:1.5rem; margin:0.2rem 0;">{net_impact_units:+,.0f} units</div>
            <span class="kpi-pill {net_cls}">U.S. {delta_us_units:+,.0f} | Non-U.S. {delta_non_us_units:+,.0f}</span>
            <div class="kpi-tooltip">
                Applies <b>{us_shock_pct:+d}%</b> to current U.S. volume ({fmt_units(us_curr)}) and
                <b>{non_us_boost_pct:+d}%</b> to non-U.S. exports ({fmt_units(non_us_curr)}).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
                    <div class="rec-stat-lbl">SUV export share</div>
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
        <div class="rec-card" style="border-top-color:{SE_DORADO};">
            <span class="rec-tag dorado">03 · Domestic Anchor</span>
            <div class="rec-title">Strengthen Local Fleet Renewal</div>
            <div class="rec-stats">
                <div class="rec-stat-box">
                    <div class="rec-stat-num">{sub_dom_share:.1f}%</div>
                    <div class="rec-stat-lbl">Subcompacts sold locally</div>
                </div>
                <div class="rec-stat-box">
                    <div class="rec-stat-num">{fmt_units(ps.loc[ps["ANIO"] == max_year, "VENTAS"].sum())}</div>
                    <div class="rec-stat-lbl">{period_tag} retail sales</div>
                </div>
            </div>
            <div class="rec-action"><strong>Action:</strong> Target NAFIN/Bancomext financing incentives toward domestically assembled subcompacts and light commercial pickups.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )