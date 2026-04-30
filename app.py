import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ESG-SCM Dashboard",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS + Font Awesome injection ──────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

<style>
/* ── Global tokens ── */
:root {
    --bg-base:      #080d1a;
    --bg-surface:   #0f1629;
    --bg-elevated:  #162040;
    --bg-hover:     #1e2d52;
    --border:       #1f2f52;
    --border-light: #2a3f6b;
    --accent:       #3b7eff;
    --accent-glow:  rgba(59,126,255,0.18);
    --teal:         #06b6d4;
    --teal-glow:    rgba(6,182,212,0.15);
    --text-primary: #e8edf8;
    --text-muted:   #8899bb;
    --text-dim:     #4f6180;
    --red:          #ef4444;
    --red-bg:       #1a0808;
    --red-border:   rgba(239,68,68,0.35);
    --amber:        #f59e0b;
    --amber-bg:     #1a1008;
    --amber-border: rgba(245,158,11,0.35);
    --green:        #22c55e;
    --green-bg:     #081a0e;
    --green-border: rgba(34,197,94,0.35);
    --radius:       10px;
    --radius-sm:    6px;
    --shadow:       0 4px 24px rgba(0,0,0,0.4);
    --font:         'DM Sans', sans-serif;
    --mono:         'DM Mono', monospace;
}

/* ── Base resets ── */
html, body, [class*="css"] {
    font-family: var(--font) !important;
    color: var(--text-primary);
}

/* ── App background ── */
.stApp {
    background: var(--bg-base);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stRadio > label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 4px;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    border-radius: var(--radius-sm);
    padding: 8px 12px;
    margin: 2px 0;
    transition: background 0.15s;
    font-size: 0.875rem;
    color: var(--text-muted);
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
}

/* ── Page titles ── */
h1 {
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: var(--text-primary) !important;
    margin-bottom: 0 !important;
}
h2, h3 {
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.01em !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 20px !important;
    box-shadow: var(--shadow);
    transition: border-color 0.2s;
}
[data-testid="stMetric"]:hover {
    border-color: var(--border-light);
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    font-family: var(--mono) !important;
}

/* ── Dividers ── */
hr {
    border-color: var(--border) !important;
    margin: 20px 0 !important;
}

/* ── Dataframes ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden;
}
.stDataFrame iframe {
    background: var(--bg-surface) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border);
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    color: var(--text-muted) !important;
    padding: 10px 20px !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
    transition: all 0.15s;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--bg-surface) !important;
    margin-bottom: 6px;
}
[data-testid="stExpander"] summary {
    font-weight: 500 !important;
    padding: 12px 16px !important;
}
[data-testid="stExpander"]:hover {
    border-color: var(--border-light) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.15s, transform 0.1s;
}
.stButton > button:hover {
    opacity: 0.85 !important;
    transform: translateY(-1px);
}

/* ── Selects / multiselects ── */
[data-baseweb="select"] {
    background: var(--bg-elevated) !important;
    border-color: var(--border) !important;
    border-radius: var(--radius-sm) !important;
}
[data-baseweb="tag"] {
    background: var(--accent-glow) !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    border-radius: 4px !important;
}

/* ── Sliders ── */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
}

/* ── Info/Warning/Success boxes ── */
[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    border: 1px solid !important;
}

/* ── Custom components ── */
.page-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 4px;
}
.page-header .page-icon {
    width: 36px; height: 36px;
    background: var(--accent-glow);
    border: 1px solid rgba(59,126,255,0.3);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    color: var(--accent);
    font-size: 1rem;
}
.page-subtitle {
    font-size: 0.8rem;
    color: var(--text-dim);
    margin-top: 2px;
    margin-bottom: 16px;
    font-weight: 400;
}

.stat-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.pill-red    { background: var(--red-bg);   color: var(--red);   border: 1px solid var(--red-border); }
.pill-amber  { background: var(--amber-bg); color: var(--amber); border: 1px solid var(--amber-border); }
.pill-green  { background: var(--green-bg); color: var(--green); border: 1px solid var(--green-border); }
.pill-blue   { background: var(--accent-glow); color: var(--accent); border: 1px solid rgba(59,126,255,0.3); }

.alert-card {
    border-radius: var(--radius);
    padding: 12px 16px;
    margin: 5px 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.alert-high {
    background: var(--red-bg);
    border: 1px solid var(--red-border);
    border-left: 3px solid var(--red);
}
.alert-med {
    background: var(--amber-bg);
    border: 1px solid var(--amber-border);
    border-left: 3px solid var(--amber);
}
.alert-low {
    background: var(--green-bg);
    border: 1px solid var(--green-border);
    border-left: 3px solid var(--green);
}
.alert-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 8px;
}
.alert-body {
    font-size: 0.8rem;
    color: var(--text-muted);
    line-height: 1.5;
}

.section-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin: 20px 0 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

.sidebar-brand {
    padding: 4px 0 16px;
}
.sidebar-brand .brand-name {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}
.sidebar-brand .brand-sub {
    font-size: 0.72rem;
    color: var(--text-dim);
    margin-top: 2px;
}
.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    background: var(--accent-glow);
    color: var(--accent);
    border: 1px solid rgba(59,126,255,0.25);
}
.risk-dot-red   { color: var(--red);   }
.risk-dot-amber { color: var(--amber); }
.risk-dot-green { color: var(--green); }

.corr-table th {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--text-dim);
    border-bottom: 1px solid var(--border);
    padding: 8px 12px;
}
.corr-table td {
    padding: 8px 12px;
    font-size: 0.85rem;
    border-bottom: 1px solid var(--border);
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def df_display(df):
    df = df.copy()
    df.index = range(1, len(df) + 1)
    return df
    
def safe(d, *keys, default="N/A"):
    for k in keys:
        if not isinstance(d, dict): return default
        d = d.get(k, default)
        if d is None: return default
    return d

def risk_icon(r):
    icons = {
        "High":   '<i class="fa-solid fa-circle-exclamation risk-dot-red"></i>',
        "Medium": '<i class="fa-solid fa-triangle-exclamation risk-dot-amber"></i>',
        "Low":    '<i class="fa-solid fa-circle-check risk-dot-green"></i>',
    }
    return icons.get(r, '<i class="fa-regular fa-circle"></i>')

def risk_pill(r):
    cls = {"High": "pill-red", "Medium": "pill-amber", "Low": "pill-green"}.get(r, "pill-blue")
    icon = {"High": "fa-circle-exclamation", "Medium": "fa-triangle-exclamation", "Low": "fa-circle-check"}.get(r, "fa-circle")
    return f'<span class="stat-pill {cls}"><i class="fa-solid {icon}"></i> {r}</span>'

def corr_matrix(df, esg_cols, scm_cols):
    rows = []
    for e in esg_cols:
        row = []
        for s in scm_cols:
            sub = df[[e, s]].dropna()
            row.append(round(sub[e].corr(sub[s]), 3) if len(sub) > 2 else None)
        rows.append(row)
    return pd.DataFrame(rows, index=esg_cols, columns=scm_cols)

def page_header(icon_class, title, subtitle=""):
    st.markdown(f"""
    <div class="page-header">
        <div class="page-icon"><i class="fa-solid {icon_class}"></i></div>
        <div>
            <h1 style="margin:0;padding:0">{title}</h1>
        </div>
    </div>
    <div class="page-subtitle">{subtitle}</div>
    """, unsafe_allow_html=True)

def section_label(text):
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
            <div style="width:32px;height:32px;background:rgba(59,126,255,0.15);border:1px solid rgba(59,126,255,0.3);
                        border-radius:8px;display:flex;align-items:center;justify-content:center;">
                <i class="fa-solid fa-chart-line" style="color:#3b7eff;font-size:0.9rem"></i>
            </div>
            <div class="brand-name">ESG · SCM Dashboard</div>
        </div>
        <div class="brand-sub">Indonesia Consumer Goods &nbsp;·&nbsp; <span class="badge"><i class="fa-solid fa-shield-halved"></i> Analytics</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="section-label">Data Sources</div>', unsafe_allow_html=True)
    json_file  = st.file_uploader("n8n JSON output",  type="json",          help="Post-processor output from n8n")
    excel_file = st.file_uploader("Excel data file",  type=["xlsx", "xls"], help="Your original ESG-SCM spreadsheet")

    st.divider()

    st.markdown('<div class="section-label">Navigation</div>', unsafe_allow_html=True)
    page = st.radio("", [
        "Overview",
        "Correlation Heatmap",
        "Company Comparison",
        "What-If Simulator",
        "Risk Alert Panel",
        "AI Recommendations",
        "Trend Analysis",
    ], label_visibility="collapsed")

    st.divider()
    st.markdown('<div style="font-size:0.7rem;color:var(--text-dim,#4f6180);text-align:center">ESG-SCM Analytics Platform · v2.0</div>', unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
companies, summary, df_raw = [], {}, None

if json_file:
    raw = json.load(json_file)
    if isinstance(raw, list):
        raw = raw[0]
    companies = raw.get("companies", [])
    summary   = raw.get("processing_summary", {})

if excel_file:
    df_raw = pd.read_excel(excel_file)
    df_raw.columns = [c.strip().upper().replace(" ", "_") for c in df_raw.columns]

# ── No data ───────────────────────────────────────────────────────────────────
if not companies and df_raw is None:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                min-height:60vh;text-align:center;gap:16px;padding:40px">
        <div style="width:64px;height:64px;background:rgba(59,126,255,0.12);border:1px solid rgba(59,126,255,0.25);
                    border-radius:16px;display:flex;align-items:center;justify-content:center;margin:0 auto 8px">
            <i class="fa-solid fa-chart-line" style="font-size:1.6rem;color:#3b7eff"></i>
        </div>
        <h1 style="margin:0">ESG-SCM Intelligence Dashboard</h1>
        <p style="color:#8899bb;max-width:480px;line-height:1.7;margin:0">
            Upload your data sources in the sidebar to begin analysis. This dashboard provides
            AI-powered ESG and supply chain correlation insights for Indonesia's consumer goods sector.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.info("**n8n JSON** — Required for AI analysis, executive summaries, recommendations and risk data.", icon="ℹ️")
    with col2:
        st.info("**Excel File** — Required for correlation heatmap, what-if simulator and trend analysis.", icon="ℹ️")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "Overview":
    page_header("fa-house-chimney", "Overview",
                f"Indonesia Food &amp; Tobacco &nbsp;·&nbsp; {len(companies)} companies analysed")

    if companies:
        risk_counts = pd.Series([safe(c, "risk_assessment", "overall_risk") for c in companies]).value_counts()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Companies",  len(companies))
        c2.metric("High Risk",        risk_counts.get("High", 0))
        c3.metric("Medium Risk",      risk_counts.get("Medium", 0))
        c4.metric("Low Risk",         risk_counts.get("Low", 0))

        st.divider()
        section_label("Company Registry")

        rows = []
        for c in companies:
            rows.append({
                "Company":       safe(c, "analysis_metadata", "company"),
                "Risk":          safe(c, "risk_assessment", "overall_risk"),
                "Confidence":    safe(c, "analysis_metadata", "confidence_level"),
                "ESG Strongest": safe(c, "esg_performance", "strongest_dimension"),
                "ESG Weakest":   safe(c, "esg_performance", "weakest_dimension"),
            })
        ov_df = pd.DataFrame(rows)

        def colour_risk(val):
            m = {"High":   "background-color:#1a0808;color:#ef4444",
                 "Medium": "background-color:#1a1008;color:#f59e0b",
                 "Low":    "background-color:#081a0e;color:#22c55e"}
            return m.get(val, "")

        ov_df = pd.DataFrame(rows)
        ov_df.index = ov_df.index + 1
        
        st.dataframe(ov_df.style.map(colour_risk, subset=["Risk"]),
                     use_container_width=True, height=450)

        st.divider()
        section_label("Executive Summaries")

        # for c in companies:
        #     name = safe(c, "analysis_metadata", "company")
        #     risk = safe(c, "risk_assessment", "overall_risk")
        #     badge_cls = {"High": "pill-red", "Medium": "pill-amber", "Low": "pill-green"}.get(risk, "pill-blue")
        #     icon_cls  = {"High": "fa-circle-exclamation", "Medium": "fa-triangle-exclamation", "Low": "fa-circle-check"}.get(risk, "fa-circle")

        #     with st.expander(f"{name}  —  {risk} Risk"):
        #         st.markdown(f'<span class="stat-pill {badge_cls}"><i class="fa-solid {icon_cls}"></i> {risk} Risk</span>', unsafe_allow_html=True)
        #         st.write(safe(c, "executive_summary"))
        cols = st.columns(3)

        for i, c in enumerate(companies):
            col = cols[i % 3]
        
            name = safe(c,"analysis_metadata","company")
            risk = safe(c,"risk_assessment","overall_risk")
        
            # keep your exact color system
            if risk == "High":
                badge = '<span style="background:#450a0a;color:#fca5a5;padding:4px 10px;border-radius:6px;font-size:0.75rem;">High Risk</span>'
            elif risk == "Medium":
                badge = '<span style="background:#451a03;color:#fcd34d;padding:4px 10px;border-radius:6px;font-size:0.75rem;">Medium Risk</span>'
            else:
                badge = '<span style="background:#052e16;color:#6ee7b7;padding:4px 10px;border-radius:6px;font-size:0.75rem;">Low Risk</span>'
        
            with col:
                st.markdown(f"""
                <div style="
                    background:#0c1828;
                    border:1px solid #1f2a3a;
                    border-radius:10px;
                    padding:16px;
                    margin-bottom:14px;
                    min-height:180px;
                ">
                    <div style="font-weight:600;font-size:0.95rem;margin-bottom:8px;">
                        {name}
                    </div>
                    {badge}
                    <div style="margin-top:10px;font-size:0.85rem;line-height:1.5;">
                        {safe(c,"executive_summary")}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
    else:
        st.info("Upload your n8n JSON to see company overview.", icon="ℹ️")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CORRELATION HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Correlation Heatmap":
    page_header("fa-fire-flame-curved", "ESG–SCM Correlation Heatmap",
                "Pearson correlation between ESG dimensions and supply chain / financial metrics")

    if df_raw is None:
        st.warning("Upload your Excel file to see the correlation heatmap.", icon="⚠️")
        st.stop()

    ESG_OPTIONS = [c for c in ["ESG_SCORE", "EMISSIONS_SCORE", "ENVIRONMENTAL_INNOVATION_SCORE",
                                "RESOURCE_USE_SCORE", "COMMUNITY_SCORE", "HUMAN_RIGHTS_SCORE",
                                "PRODUCT_RESPONSIBILITY_SCORE", "WORKFORCE_SCORE",
                                "CSR_STRATEGY_SCORE", "MANAGEMENT_SCORE", "SHAREHOLDERS_SCORE"]
                   if c in df_raw.columns]
    SCM_OPTIONS = [c for c in ["CASH_CONVERSION_CYCLE", "AVERAGE_INVENTORY_DAYS",
                                "INVENTORY_TURNOVER", "DAYS_SALES_OUTSTANDING",
                                "DAYS_PAYABLES_OUTSTANDING", "ROA_TOTAL_ASSETS",
                                "PROFIT_MARGIN", "EBITDA_MARGIN"]
                   if c in df_raw.columns]

    col1, col2 = st.columns(2)
    sel_esg = col1.multiselect("ESG Dimensions", ESG_OPTIONS, default=ESG_OPTIONS[:5])
    sel_scm = col2.multiselect("SCM / Financial Metrics", SCM_OPTIONS, default=SCM_OPTIONS[:4])

    if sel_esg and sel_scm:
        if "YEAR" in df_raw.columns:
            years = sorted(df_raw["YEAR"].dropna().unique().astype(int).tolist())
            sel_years = st.select_slider("Year Range", options=years, value=(years[0], years[-1]))
            df_f = df_raw[df_raw["YEAR"].between(sel_years[0], sel_years[1])].copy()
        else:
            df_f = df_raw.copy()

        for c in sel_esg + sel_scm:
            df_f[c] = pd.to_numeric(df_f[c], errors="coerce")

        cm = corr_matrix(df_f, sel_esg, sel_scm)

        fig = px.imshow(
            cm,
            text_auto=".2f",
            color_continuous_scale="RdYlGn",
            zmin=-1, zmax=1,
            aspect="auto",
            title="Pearson Correlation: ESG Dimensions vs SCM / Financial Metrics"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8edf8", family="DM Sans"),
            height=420,
            title_font_size=14,
            coloraxis_colorbar=dict(title="r")
        )
        st.plotly_chart(fig, use_container_width=True)

        section_label("Strongest Correlations")

        pairs = []
        for e in sel_esg:
            for s in sel_scm:
                v = cm.loc[e, s]
                if pd.notna(v):
                    pairs.append({"ESG": e, "SCM / Finance": s, "r": v, "|r|": abs(v)})
        pairs_df = pd.DataFrame(pairs).sort_values("|r|", ascending=False).head(8)

        def interp(r):
            if abs(r) < 0.2: return "Negligible"
            if abs(r) < 0.4: return "Weak"
            if abs(r) < 0.6: return "Moderate"
            if abs(r) < 0.8: return "Strong"
            return "Very Strong"

        pairs_df["Strength"]  = pairs_df["r"].apply(interp)
        pairs_df["Direction"] = pairs_df["r"].apply(lambda x: "Positive" if x > 0 else "Negative")
        
        df_temp = df_display(pairs_df[["ESG", "SCM / Finance", "r", "Strength", "Direction"]])
        st.dataframe(df_temp, use_container_width=True)
    else:
        st.info("Select at least one ESG dimension and one SCM metric.", icon="ℹ️")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: COMPANY COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Company Comparison":
    page_header("fa-magnifying-glass-chart", "Company Comparison",
                "Radar, bar and benchmark analysis across selected companies")

    if df_raw is None and not companies:
        st.warning("Upload Excel and/or n8n JSON to compare companies.", icon="⚠️")
        st.stop()

    if df_raw is not None and "COMPANY" in df_raw.columns:
        company_list = sorted(df_raw["COMPANY"].dropna().unique().tolist())
        sel = st.multiselect("Select companies to compare", company_list, default=company_list[:4])

        if sel:
            if "YEAR" in df_raw.columns:
                df_latest = df_raw.sort_values("YEAR").groupby("COMPANY").last().reset_index()
            else:
                df_latest = df_raw.copy()
            df_sel = df_latest[df_latest["COMPANY"].isin(sel)]

            radar_cols = [c for c in ["ESG_SCORE", "EMISSIONS_SCORE", "COMMUNITY_SCORE",
                                       "MANAGEMENT_SCORE", "INVENTORY_TURNOVER", "ROA_TOTAL_ASSETS"]
                          if c in df_raw.columns]

            if radar_cols:
                section_label("Multi-Dimension Radar")
                fig = go.Figure()
                for _, row in df_sel.iterrows():
                    vals = [pd.to_numeric(row.get(c, 0), errors="coerce") or 0 for c in radar_cols]
                    maxv = [df_raw[c].dropna().apply(pd.to_numeric, errors="coerce").max() for c in radar_cols]
                    norm = [v / m * 100 if m and m > 0 else 0 for v, m in zip(vals, maxv)]
                    fig.add_trace(go.Scatterpolar(
                        r=norm + [norm[0]],
                        theta=radar_cols + [radar_cols[0]],
                        fill="toself",
                        name=str(row["COMPANY"]),
                        opacity=0.75
                    ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100],
                                        gridcolor="#1f2f52", tickfont=dict(color="#8899bb", size=10)),
                        angularaxis=dict(gridcolor="#1f2f52", tickfont=dict(color="#8899bb")),
                        bgcolor="rgba(0,0,0,0)"
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e8edf8", family="DM Sans"),
                    height=480,
                    legend=dict(orientation="h", y=-0.15)
                )
                st.plotly_chart(fig, use_container_width=True)

            section_label("Side-by-Side Metrics")
            num_cols = [c for c in ["ESG_SCORE", "CASH_CONVERSION_CYCLE", "INVENTORY_TURNOVER",
                                     "ROA_TOTAL_ASSETS", "PROFIT_MARGIN", "AVERAGE_INVENTORY_DAYS"]
                        if c in df_raw.columns]
            metric = st.selectbox("Select metric", num_cols)
            df_bar = df_sel[["COMPANY", metric]].copy()
            df_bar[metric] = pd.to_numeric(df_bar[metric], errors="coerce")
            fig2 = px.bar(df_bar, x="COMPANY", y=metric, color="COMPANY",
                          title=f"{metric} — Company Comparison",
                          color_discrete_sequence=px.colors.qualitative.Vivid)
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8edf8", family="DM Sans"),
                showlegend=False, height=380
            )
            st.plotly_chart(fig2, use_container_width=True)

            section_label("Benchmark vs Industry")
            BENCHMARKS = {
                "CASH_CONVERSION_CYCLE":  (45, 60, "days"),
                "AVERAGE_INVENTORY_DAYS": (55, 70, "days"),
                "ESG_SCORE":              (45, 60, "score"),
                "ROA_TOTAL_ASSETS":       (0.05, 0.08, "%"),
                "PROFIT_MARGIN":          (0.08, 0.12, "%"),
            }
            bm_rows = []
            for _, row in df_sel.iterrows():
                for col, (lo, hi, unit) in BENCHMARKS.items():
                    if col not in df_raw.columns: continue
                    val = pd.to_numeric(row.get(col), errors="coerce")
                    if pd.isna(val): continue
                    status = "In Range" if lo <= val <= hi else ("Above Range" if val > hi else "Below Range")
                    bm_rows.append({
                        "Company":   row["COMPANY"],
                        "Metric":    col,
                        "Value":     round(val, 3),
                        "Benchmark": f"{lo}–{hi} {unit}",
                        "Status":    status
                    })
            if bm_rows:
                df_temp = df_display(pd.DataFrame(bm_rows))
                st.dataframe(df_temp, use_container_width=True)
    else:
        st.info("Upload your Excel file to use the comparison tool.", icon="ℹ️")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: WHAT-IF SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "What-If Simulator":
    page_header("fa-sliders", "What-If Simulator",
                "Estimate how improving an ESG dimension affects supply chain and financial performance")

    if df_raw is None:
        st.warning("Upload your Excel file to use the simulator.", icon="⚠️")
        st.stop()

    for c in df_raw.columns:
        df_raw[c] = pd.to_numeric(df_raw[c], errors="coerce") if c not in ["COMPANY"] else df_raw[c]

    ESG_DIMS = {
        "Environmental (avg)": ["EMISSIONS_SCORE", "ENVIRONMENTAL_INNOVATION_SCORE", "RESOURCE_USE_SCORE"],
        "Social (avg)":        ["COMMUNITY_SCORE", "HUMAN_RIGHTS_SCORE", "PRODUCT_RESPONSIBILITY_SCORE", "WORKFORCE_SCORE"],
        "Governance (avg)":    ["CSR_STRATEGY_SCORE", "MANAGEMENT_SCORE", "SHAREHOLDERS_SCORE"],
        "ESG Overall":         ["ESG_SCORE"],
    }
    TARGETS = {
        "Cash Conversion Cycle": "CASH_CONVERSION_CYCLE",
        "Inventory Turnover":    "INVENTORY_TURNOVER",
        "Avg Inventory Days":    "AVERAGE_INVENTORY_DAYS",
        "ROA":                   "ROA_TOTAL_ASSETS",
        "Profit Margin":         "PROFIT_MARGIN",
    }

    col1, col2 = st.columns(2)
    esg_choice    = col1.selectbox("ESG dimension to improve", list(ESG_DIMS.keys()))
    target_choice = col2.selectbox("Target metric to estimate", list(TARGETS.keys()))
    improvement   = st.slider("ESG improvement (%)", 1, 50, 10)

    esg_cols = [c for c in ESG_DIMS[esg_choice] if c in df_raw.columns]
    tgt_col  = TARGETS[target_choice]

    if not esg_cols or tgt_col not in df_raw.columns:
        st.warning("Some required columns are missing from your Excel file.", icon="⚠️")
        st.stop()

    df_sim = df_raw.copy()
    df_sim["_esg"] = df_sim[esg_cols].mean(axis=1)
    df_sim = df_sim[["COMPANY", "YEAR", "_esg", tgt_col]].dropna()

    r = df_sim["_esg"].corr(df_sim[tgt_col])

    if "YEAR" in df_sim.columns:
        df_latest = df_raw.copy()  
        # df_sim.sort_values("YEAR").groupby("COMPANY").last().reset_index()
    else:
        df_latest = df_sim.copy()

    df_latest["ESG Current"]   = df_latest["_esg"]
    df_latest["ESG Projected"] = df_latest["_esg"] * (1 + improvement / 100)

    from numpy.polynomial import polynomial as P
    x = df_sim["_esg"].values
    y = df_sim[tgt_col].values
    if len(x) > 2:
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
    else:
        slope = r

    df_latest[f"{target_choice} Current"]   = df_latest[tgt_col]
    df_latest[f"{target_choice} Projected"] = (
        df_latest[tgt_col] + slope * (df_latest["ESG Projected"] - df_latest["ESG Current"])
    )

    st.divider()
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Correlation (r)",    f"{r:.3f}")
    col_b.metric("Regression Slope",   f"{slope:.4f}")
    col_c.metric("ESG Improvement",    f"+{improvement}%")

    if abs(r) < 0.2:
        st.info("Correlation is weak (r < 0.2) — projection is indicative only.", icon="ℹ️")
    elif r > 0:
        st.success(f"Positive correlation: improving **{esg_choice}** tends to increase **{target_choice}**.", icon="✅")
    else:
        st.success(f"Negative correlation: improving **{esg_choice}** tends to decrease **{target_choice}** (favourable for CCC/DIO).", icon="✅")

    section_label("Projected Impact by Company")
    fig = go.Figure()
    for _, row in df_latest.iterrows():
        fig.add_trace(go.Bar(
            name=str(row["COMPANY"]),
            x=["Current", f"Projected (+{improvement}%)"],
            y=[row[f"{target_choice} Current"], row[f"{target_choice} Projected"]],
            text=[f"{row[f'{target_choice} Current']:.2f}", f"{row[f'{target_choice} Projected']:.2f}"],
            textposition="outside",
        ))
    fig.update_layout(
        barmode="group",
        title=f"Projected impact on {target_choice} if {esg_choice} improves by {improvement}%",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8edf8", family="DM Sans"),
        height=460,
        xaxis_title="",
        yaxis_title=target_choice,
        legend=dict(orientation="h", y=-0.2)
    )
    st.plotly_chart(fig, use_container_width=True)

    section_label("Company-Level Projections Table")
    tbl = df_latest[["COMPANY", f"{target_choice} Current", f"{target_choice} Projected"]].copy()
    tbl["Change"]   = tbl[f"{target_choice} Projected"] - tbl[f"{target_choice} Current"]
    tbl["Change %"] = (tbl["Change"] / tbl[f"{target_choice} Current"].abs() * 100).round(2)
    tbl = tbl.round(3)
    st.dataframe(df_display(tbl), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: RISK ALERT PANEL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Risk Alert Panel":
    page_header("fa-shield-halved", "Risk Alert Panel",
                "Operational, reputational and financial risk classification by company")

    if not companies:
        st.warning("Upload your n8n JSON to see risk alerts.", icon="⚠️")
        st.stop()

    CONTROVERSIES = {
        "AALI.JK": "Deforestation &amp; palm oil sustainability concerns (RSPO compliance issues)",
        "GGRM.JK": "Tobacco health impact — increasing regulatory pressure in Indonesia",
        "HMSP.JK": "Tobacco sector — ESG exclusion risk from institutional investors",
        "UNVR.JK": "Negative ROA — financial distress signals despite strong ESG score",
        "CPIN.JK": "Poultry supply chain — animal welfare &amp; antibiotic use concerns",
    }

    high   = [c for c in companies if safe(c, "risk_assessment", "overall_risk") == "High"]
    medium = [c for c in companies if safe(c, "risk_assessment", "overall_risk") == "Medium"]
    low    = [c for c in companies if safe(c, "risk_assessment", "overall_risk") == "Low"]

    c1, c2, c3 = st.columns(3)
    c1.metric("High Risk Companies",   len(high))
    c2.metric("Medium Risk Companies", len(medium))
    c3.metric("Low Risk Companies",    len(low))

    st.divider()
    section_label("ESG Controversy Flags")

    flagged = [(c, CONTROVERSIES[safe(c, "analysis_metadata", "company")])
               for c in companies
               if safe(c, "analysis_metadata", "company") in CONTROVERSIES]

    if flagged:
        for c, note in flagged:
            name = safe(c, "analysis_metadata", "company")
            risk = safe(c, "risk_assessment", "overall_risk")
            icon = "fa-circle-exclamation" if risk == "High" else "fa-triangle-exclamation"
            st.markdown(f"""
            <div class="alert-card alert-high">
                <div class="alert-title">
                    <i class="fa-solid {icon} risk-dot-red"></i>
                    {name}
                    &nbsp;<span class="stat-pill pill-red" style="font-size:0.68rem">High Priority</span>
                </div>
                <div class="alert-body">{note}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.success("No controversy flags for current companies.", icon="✅")

    st.divider()
    section_label("Company Risk Breakdown")

    risk_filter = st.multiselect("Filter by risk level", ["High", "Medium", "Low"], default=["High", "Medium"])

    for c in companies:
        name    = safe(c, "analysis_metadata", "company")
        overall = safe(c, "risk_assessment", "overall_risk")
        if overall not in risk_filter: continue

        op_r  = c.get("risk_assessment", {}).get("operational_risks",  []) or []
        rep_r = c.get("risk_assessment", {}).get("reputational_risks", []) or []
        fin_r = c.get("risk_assessment", {}).get("financial_risks",    []) or []

        icon_cls  = {"High": "fa-circle-exclamation", "Medium": "fa-triangle-exclamation", "Low": "fa-circle-check"}.get(overall, "fa-circle")
        badge_cls = {"High": "pill-red", "Medium": "pill-amber", "Low": "pill-green"}.get(overall, "pill-blue")

        with st.expander(f"{name}  ·  {overall} Risk"):
            st.markdown(f'<span class="stat-pill {badge_cls}"><i class="fa-solid {icon_cls}"></i> {overall} Risk</span>', unsafe_allow_html=True)
            st.write("")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:#8899bb;margin-bottom:6px"><i class="fa-solid fa-gear" style="margin-right:5px"></i>Operational</div>', unsafe_allow_html=True)
                for r in (op_r if isinstance(op_r, list) else [op_r]):
                    st.write(f"• {r}")
            with col2:
                st.markdown('<div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:#8899bb;margin-bottom:6px"><i class="fa-solid fa-eye" style="margin-right:5px"></i>Reputational</div>', unsafe_allow_html=True)
                for r in (rep_r if isinstance(rep_r, list) else [rep_r]):
                    st.write(f"• {r}")
            with col3:
                st.markdown('<div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:#8899bb;margin-bottom:6px"><i class="fa-solid fa-coins" style="margin-right:5px"></i>Financial</div>', unsafe_allow_html=True)
                for r in (fin_r if isinstance(fin_r, list) else [fin_r]):
                    st.write(f"• {r}")

    st.divider()
    section_label("Risk Distribution")

    risk_df = pd.DataFrame([{
        "Company":    safe(c, "analysis_metadata", "company"),
        "Risk":       safe(c, "risk_assessment", "overall_risk"),
        "Confidence": safe(c, "analysis_metadata", "confidence_level"),
    } for c in companies])

    fig = px.bar(
        risk_df["Risk"].value_counts().reindex(["High", "Medium", "Low"], fill_value=0).reset_index(),
        x="Risk", y="count",
        color="Risk",
        color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"},
        text="count"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8edf8", family="DM Sans"),
        showlegend=False, height=320
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AI RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "AI Recommendations":
    page_header("fa-lightbulb", "AI-Generated Recommendations",
                "Powered by your n8n AI Agent — prioritised actions by company")

    if not companies:
        st.warning("Upload your n8n JSON to see AI recommendations.", icon="⚠️")
        st.stop()

    rec_rows = []
    for c in companies:
        name = safe(c, "analysis_metadata", "company")
        for r in (c.get("recommendations") or []):
            rec_rows.append({
                "Company":  name,
                "Priority": r.get("priority", "N/A"),
                "Category": r.get("category", "N/A"),
                "Action":   r.get("action", "N/A"),
                "Impact":   r.get("expected_impact", "N/A"),
                "Timeline": r.get("timeline", "N/A"),
            })
    rec_df = pd.DataFrame(rec_rows)

    if rec_df.empty:
        st.info("No recommendations found in JSON.", icon="ℹ️")
        st.stop()

    col1, col2, col3 = st.columns(3)
    pri_f = col1.multiselect("Priority",  ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
    cat_f = col2.multiselect("Category",  rec_df["Category"].unique().tolist(), default=rec_df["Category"].unique().tolist())
    co_f  = col3.multiselect("Company",   rec_df["Company"].unique().tolist(),  default=rec_df["Company"].unique().tolist())

    filtered = rec_df[rec_df["Priority"].isin(pri_f) & rec_df["Category"].isin(cat_f) & rec_df["Company"].isin(co_f)]
    st.caption(f"{len(filtered)} recommendations")

    def colour_priority(val):
        m = {"High":   "background-color:#1a0808;color:#ef4444",
             "Medium": "background-color:#1a1008;color:#f59e0b",
             "Low":    "background-color:#081a0e;color:#22c55e"}
        return m.get(val, "")
    df_temp = df_display(filtered)

    st.dataframe(df_temp.style.map(colour_priority, subset=["Priority"]),
                 use_container_width=True, height=500)

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        section_label("By Priority")
        pc = filtered["Priority"].value_counts().reset_index()
        fig = px.pie(pc, names="Priority", values="count", hole=0.5,
                     color="Priority",
                     color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"})
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8edf8", family="DM Sans"),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        section_label("By Category")
        cc = filtered["Category"].value_counts().reset_index()
        fig2 = px.bar(cc, x="Category", y="count", color="Category",
                      color_discrete_sequence=px.colors.qualitative.Vivid)
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8edf8", family="DM Sans"),
            showlegend=False, height=300
        )
        st.plotly_chart(fig2, use_container_width=True)

    section_label("Priority Distribution by Company")
    pivot = filtered.groupby(["Company", "Priority"]).size().reset_index(name="Count")
    fig3 = px.bar(pivot, x="Company", y="Count", color="Priority", barmode="stack",
                  color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"})
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8edf8", family="DM Sans"),
        height=380, xaxis_tickangle=-30
    )
    st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: TREND ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Trend Analysis":
    page_header("fa-chart-line", "Yearly Trend Analysis",
                "Time-series performance and ESG–SCM correlation evolution")

    if df_raw is None:
        st.warning("Upload your Excel file to see trend analysis.", icon="⚠️")
        st.stop()

    if "YEAR" not in df_raw.columns or "COMPANY" not in df_raw.columns:
        st.error("Excel file must have YEAR and COMPANY columns.", icon="🚫")
        st.stop()

    df_raw["YEAR"] = pd.to_numeric(df_raw["YEAR"], errors="coerce")
    company_list   = sorted(df_raw["COMPANY"].dropna().unique().tolist())

    col1, col2 = st.columns(2)
    sel_companies = col1.multiselect("Companies", company_list, default=company_list[:4])

    TREND_METRICS = [c for c in [
        "ESG_SCORE", "EMISSIONS_SCORE", "COMMUNITY_SCORE", "MANAGEMENT_SCORE",
        "CASH_CONVERSION_CYCLE", "AVERAGE_INVENTORY_DAYS", "INVENTORY_TURNOVER",
        "ROA_TOTAL_ASSETS", "PROFIT_MARGIN", "EBITDA_MARGIN"
    ] if c in df_raw.columns]

    sel_metric = col2.selectbox("Metric", TREND_METRICS)

    if sel_companies and sel_metric:
        df_trend = df_raw[df_raw["COMPANY"].isin(sel_companies)][["COMPANY", "YEAR", sel_metric]].copy()
        df_trend["YEAR"]      = pd.to_numeric(df_trend["YEAR"], errors="coerce")
        df_trend[sel_metric]  = pd.to_numeric(df_trend[sel_metric], errors="coerce")
        df_trend = df_trend.dropna(subset=["COMPANY", "YEAR"]).sort_values(["COMPANY", "YEAR"])

        section_label(f"{sel_metric} Over Time")
        fig = px.line(df_trend, x="YEAR", y=sel_metric, color="COMPANY",
                      markers=True, title=f"{sel_metric} — Historical Trend",
                      color_discrete_sequence=px.colors.qualitative.Vivid)
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8edf8", family="DM Sans"),
            height=420, xaxis=dict(dtick=1)
        )
        st.plotly_chart(fig, use_container_width=True)

        section_label("Year-over-Year Change")
        yoy_rows = []
        for comp in sel_companies:
            sub = df_trend[df_trend["COMPANY"] == comp].sort_values("YEAR")
            sub = sub.copy()
            sub["YoY Change"] = sub[sel_metric].diff()
            sub["YoY %"]      = sub[sel_metric].pct_change() * 100
            yoy_rows.append(sub)
        if yoy_rows:
            yoy_df = pd.concat(yoy_rows).round(3)
            st.dataframe(df_display(yoy_df), use_container_width=True, height=340)

        section_label("ESG vs SCM — Correlation by Year")
        ESG_C = [c for c in ["ESG_SCORE", "EMISSIONS_SCORE"] if c in df_raw.columns]
        SCM_C = [c for c in ["CASH_CONVERSION_CYCLE", "INVENTORY_TURNOVER"] if c in df_raw.columns]

        if ESG_C and SCM_C:
            corr_by_year = []
            for yr in sorted(df_raw["YEAR"].dropna().unique()):
                sub = df_raw[df_raw["YEAR"] == yr]
                for e in ESG_C:
                    for s in SCM_C:
                        vals = sub[[e, s]].apply(pd.to_numeric, errors="coerce").dropna()
                        if len(vals) > 2:
                            corr_by_year.append({
                                "Year": int(yr),
                                "Pair": f"{e} vs {s}",
                                "r":    round(vals[e].corr(vals[s]), 3)
                            })
            if corr_by_year:
                cy_df = pd.DataFrame(corr_by_year)
                fig2  = px.line(cy_df, x="Year", y="r", color="Pair", markers=True,
                                title="ESG–SCM Correlation Evolution Over Time",
                                color_discrete_sequence=px.colors.qualitative.Pastel)
                fig2.add_hline(y=0, line_dash="dash", line_color="#4f6180", opacity=0.7)
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e8edf8", family="DM Sans"),
                    height=380
                )
                st.plotly_chart(fig2, use_container_width=True)
