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
    /* Global Canvas */
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

    /* Chart Card Wrapper & Chart-Specific Micro-Footnote */
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

    /* Compact Recommendation Cards (Bottom Section) */
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

    # Exact grain deduplication: Production & Retail Sales are monthly-model level,
    # whereas Exports are disaggregated by PAIS_DESTINO.
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
# 3. COMPACT SIDEBAR CONTROLS (Clean & Unobtrusive)
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

# Apply filters
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
# 4. CORE METRICS COMPUTATION (Dynamic + Exact YTD)
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

# Two-speed segment split
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
# 5. HERO HEADER (Zero "Decision Brief" Wall of Text)
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
# 6. KEY NUMBERS WITH HOVER POP-UPS (Replaces Long Insight Text Cards)
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

# Row 1 Charts: Assembly Trajectory & Segment Mix
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
        go.Bar
    )
