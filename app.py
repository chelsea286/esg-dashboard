import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ESG · SCM Intelligence",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Design System ─────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=DM+Mono:wght@300;400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css">
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/fill/style.css">
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/duotone/style.css">

<style>
/* ── Global reset & base ── */
*, *::before, *::after { box-sizing: border-box; transition: all 0.25s ease; }

html, body, [data-testid="stAppViewContainer"] {
    background: #07101d !important;
    font-family: 'DM Sans', sans-serif;
    color: #c8d6e8;
}

/* ── Scrollbar & selection ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #07101d; }
::-webkit-scrollbar-thumb { background: #1e3354; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2a4a70; }
::selection { background: rgba(91, 163, 245, 0.3); color: #e2eaf4; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #060e1a !important;
    border-right: 1px solid #112035;
}
[data-testid="stSidebar"] .stRadio > label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    color: #7a9ab8 !important;
}
[data-testid="stSidebar"] .stRadio [role="radio"] {
    background: transparent !important;
}
[data-testid="stSidebar"] .stRadio [aria-checked="true"] + div > label {
    color: #5ba3f5 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-family: 'Syne', sans-serif !important;
    color: #e2eaf4 !important;
}
[data-testid="stSidebar"] .stFileUploader label {
    font-size: 0.78rem;
    color: #6b8aaa;
}

/* ── Main title ── */
h1 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.75rem !important;
    color: #e2eaf4 !important;
    letter-spacing: -0.02em;
}
h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    color: #c8d6e8 !important;
    letter-spacing: -0.01em;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #0c1828;
    border: 1px solid #152236;
    border-radius: 10px;
    padding: 18px 22px !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
}
[data-testid="metric-container"]:hover {
    border-color: #1e4a7a;
    box-shadow: 0 4px 20px rgba(91, 163, 245, 0.1);
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem !important;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #4d718f !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif;
    font-size: 2rem !important;
    font-weight: 700;
    color: #e2eaf4 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #112035;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.82rem;
    font-weight: 500;
    color: #4d718f !important;
    border-bottom: 2px solid transparent;
    padding: 10px 18px;
    background: transparent !important;
    transition: color 0.2s ease, border-color 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #7a9ab8 !important;
}
.stTabs [aria-selected="true"] {
    color: #5ba3f5 !important;
    border-bottom: 2px solid #5ba3f5 !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #112035;
    border-radius: 8px;
    overflow: hidden;
}

/* ── Divider ── */
hr {
    border-color: #112035 !important;
    margin: 20px 0 !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #0c1828 !important;
    border: 1px solid #152236 !important;
    border-radius: 8px !important;
    margin-bottom: 8px;
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
}
[data-testid="stExpander"]:hover {
    border-color: #1e3354 !important;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
}
[data-testid="stExpander"] summary {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    color: #c8d6e8 !important;
}

/* ── Alert boxes ── */
[data-testid="stAlert"] {
    background: #0c1828 !important;
    border-color: #152236 !important;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
}

/* ── Selectbox / multiselect / slider ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: #0c1828 !important;
    border-color: #1e3354 !important;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    color: #c8d6e8 !important;
}
.stSlider [data-testid="stSlider"] {
    color: #5ba3f5;
}

/* ═══════════════════════════════════════════════════════════════════════════ */
/* ── ENHANCED UI COMPONENTS ────────────────────────────────────────────────── */
/* ═══════════════════════════════════════════════════════════════════════════ */

/* ── Sidebar wordmark with icon ── */
.sidebar-wordmark {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    color: #e2eaf4;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.sidebar-wordmark i {
    font-size: 1.4rem;
    color: #34d399;
}
.sidebar-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    color: #3d6282;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 20px;
}

/* ── Glass morphism card ── */
.glass-card {
    background: rgba(12, 24, 40, 0.7);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(21, 34, 54, 0.8);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
    transition: all 0.3s ease;
}
.glass-card:hover {
    border-color: rgba(30, 52, 84, 1);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
.glass-card-glow {
    box-shadow: 0 0 20px rgba(91, 163, 245, 0.1);
}

/* ── Custom metric card ── */
.metric-card {
    background: linear-gradient(135deg, rgba(12, 24, 40, 0.9) 0%, rgba(7, 16, 29, 0.95) 100%);
    border: 1px solid #152236;
    border-radius: 12px;
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-color, #5ba3f5), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.metric-card:hover {
    border-color: var(--accent-color, #5ba3f5);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
    transform: translateY(-2px);
}
.metric-card:hover::before {
    opacity: 1;
}
.metric-card-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    background: rgba(91, 163, 245, 0.1);
    color: var(--accent-color, #5ba3f5);
    margin-bottom: 4px;
}
.metric-card-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4d718f;
}
.metric-card-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #e2eaf4;
    line-height: 1;
}
.metric-card-delta {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #6b8aaa;
}

/* ── Icon box ── */
.icon-box {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    transition: transform 0.25s ease;
}
.icon-box:hover {
    transform: scale(1.08);
}
.icon-box-blue   { background: rgba(91, 163, 245, 0.12);  color: #5ba3f5; }
.icon-box-green  { background: rgba(52, 211, 153, 0.12); color: #34d399; }
.icon-box-red    { background: rgba(248, 113, 113, 0.12); color: #f87171; }
.icon-box-yellow { background: rgba(251, 191, 36, 0.12);  color: #fbbf24; }
.icon-box-purple { background: rgba(167, 139, 250, 0.12); color: #a78bfa; }

/* ── Glow text ── */
.glow-text {
    text-shadow: 0 0 20px currentColor;
}

/* ── Hero section ── */
.hero-section {
    background: linear-gradient(135deg, rgba(12, 24, 40, 0.6) 0%, rgba(7, 16, 29, 0.8) 100%);
    border: 1px solid #152236;
    border-radius: 16px;
    padding: 48px 56px;
    text-align: center;
    margin: 20px 0 32px;
    position: relative;
    overflow: hidden;
}
.hero-section::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 50%, rgba(91, 163, 245, 0.05) 0%, transparent 50%);
    pointer-events: none;
}
.hero-section h1 {
    font-size: 2.2rem !important;
    margin-bottom: 12px !important;
}
.hero-section p {
    font-size: 0.95rem;
    color: #4d718f;
    max-width: 500px;
    margin: 0 auto;
}

/* ── Risk badge ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    font-weight: 400;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 4px;
}
.badge i { font-size: 0.75rem; }
.badge-high   { background: rgba(239,68,68,0.12);  color: #f87171; border: 1px solid rgba(239,68,68,0.25); }
.badge-medium { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.25); }
.badge-low    { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.25); }
.badge-na     { background: rgba(100,116,139,0.12); color: #64748b; border: 1px solid rgba(100,116,139,0.2); }

/* ── Alert cards ── */
.alert-card {
    background: linear-gradient(135deg, rgba(12, 24, 40, 0.85) 0%, rgba(7, 16, 29, 0.95) 100%);
    backdrop-filter: blur(8px);
    border: 1px solid #152236;
    border-left: 3px solid;
    border-radius: 0 10px 10px 0;
    padding: 16px 20px;
    margin-bottom: 12px;
    font-family: 'DM Sans', sans-serif;
    transition: all 0.25s ease;
}
.alert-card:hover {
    transform: translateX(4px);
    box-shadow: -4px 0 20px rgba(0, 0, 0, 0.2);
}
.alert-card-high   { border-left-color: #ef4444; }
.alert-card-medium { border-left-color: #f59e0b; }
.alert-card-low    { border-left-color: #10b981; }
.alert-card strong { color: #e2eaf4; font-weight: 600; font-size: 0.9rem; }
.alert-card small  { color: #4d718f; font-size: 0.8rem; display: block; margin-top: 6px; line-height: 1.5; }
.alert-card .alert-icon {
    font-size: 1.1rem;
    margin-right: 8px;
}

/* ── Section label ── */
.section-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #2d5070;
    margin-bottom: 14px;
    margin-top: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label i {
    font-size: 0.8rem;
    color: #3d6282;
}

/* ── Info panel ── */
.info-panel {
    background: linear-gradient(135deg, rgba(12, 24, 40, 0.7) 0%, rgba(7, 16, 29, 0.85) 100%);
    backdrop-filter: blur(10px);
    border: 1px dashed #1e3354;
    border-radius: 12px;
    padding: 32px 36px;
    text-align: center;
    margin: 16px 0;
    transition: all 0.3s ease;
}
.info-panel:hover {
    border-color: #2a4a70;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
}
.info-panel p {
    font-family: 'DM Sans', sans-serif;
    color: #4d718f;
    font-size: 0.88rem;
    margin: 8px 0 0;
    line-height: 1.6;
}
.info-panel h4 {
    font-family: 'Syne', sans-serif;
    color: #7a9ab8;
    font-size: 0.95rem;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}
.info-panel h4 i {
    font-size: 1.2rem;
    color: #5ba3f5;
}

/* ── Correlation strength pill ── */
.strength-pill {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    padding: 2px 7px;
    border-radius: 4px;
    background: rgba(91,163,245,0.1);
    color: #5ba3f5;
    border: 1px solid rgba(91,163,245,0.2);
}

/* ── Recommendation cards ── */
.rec-card {
    background: rgba(12, 24, 40, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid #152236;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 12px;
    transition: all 0.3s ease;
}
.rec-card:hover {
    border-color: #1e3354;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    transform: translateY(-2px);
}
.rec-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}
.rec-card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #e2eaf4;
}
.rec-card-body {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    color: #8aacc8;
    line-height: 1.6;
}
.rec-card-meta {
    display: flex;
    gap: 12px;
    margin-top: 12px;
    flex-wrap: wrap;
}
.rec-card-tag {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    padding: 3px 8px;
    border-radius: 4px;
    background: rgba(91, 163, 245, 0.1);
    color: #5ba3f5;
}

/* ── Data upload card ── */
.upload-card {
    background: linear-gradient(135deg, rgba(12, 24, 40, 0.6) 0%, rgba(7, 16, 29, 0.8) 100%);
    border: 1px solid #152236;
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    transition: all 0.3s ease;
}
.upload-card:hover {
    border-color: #1e3354;
}
.upload-card i {
    font-size: 2rem;
    color: #5ba3f5;
    margin-bottom: 12px;
}
.upload-card h4 {
    font-family: 'Syne', sans-serif;
    color: #c8d6e8;
    font-size: 0.9rem;
    margin: 0 0 6px;
}
.upload-card p {
    font-size: 0.78rem;
    color: #4d718f;
    margin: 0;
}

/* ── Divider with icon ── */
.fancy-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 24px 0;
    color: #1e3354;
}
.fancy-divider::before,
.fancy-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, #152236, transparent);
}
.fancy-divider i {
    font-size: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ──────────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#8aacc8", size=12),
    title_font=dict(family="Syne, sans-serif", color="#c8d6e8", size=14),
    xaxis=dict(gridcolor="#0e1f33", linecolor="#152236", tickcolor="#152236", tickfont=dict(size=11), zeroline=False),
    yaxis=dict(gridcolor="#0e1f33", linecolor="#152236", tickcolor="#152236", tickfont=dict(size=11), zeroline=False),
    legend=dict(
        bgcolor="rgba(12,24,40,0.8)",
        bordercolor="#152236",
        borderwidth=1,
        font=dict(size=11, family="DM Sans, sans-serif"),
    ),
    hoverlabel=dict(
        bgcolor="#0c1828",
        bordercolor="#1e3354",
        font=dict(family="DM Mono, monospace", size=11, color="#c8d6e8"),
    ),
    margin=dict(l=16, r=16, t=44, b=16),
)

ACCENT_COLORS = [
    "#5ba3f5", "#34d399", "#f59e0b", "#a78bfa", "#fb7185",
    "#22d3ee", "#fbbf24", "#4ade80", "#e879f9", "#60a5fa",
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def safe(d, *keys, default="N/A"):
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k, default)
        if d is None:
            return default
    return d

def risk_badge(r):
    """Risk badge with Phosphor icon."""
    icons = {"High": "ph-warning-circle", "Medium": "ph-warning", "Low": "ph-check-circle"}
    icon = icons.get(r, "ph-minus")
    cls = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}.get(r, "badge-na")
    return f'<span class="badge {cls}"><i class="ph {icon}"></i>{r if r != "N/A" else "—"}</span>'

def risk_dot(r):
    """Emoji dot indicator for expander titles."""
    return {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(r, "⚪")

def metric_card(label, value, icon, delta=None, accent="#5ba3f5"):
    """Custom HTML metric card with icon."""
    delta_html = f'<div class="metric-card-delta">{delta}</div>' if delta else ''
    return f"""
    <div class="metric-card" style="--accent-color:{accent}">
        <div class="metric-card-icon"><i class="ph {icon}"></i></div>
        <div class="metric-card-label">{label}</div>
        <div class="metric-card-value">{value}</div>
        {delta_html}
    </div>
    """

def corr_matrix(df, esg_cols, scm_cols):
    rows = []
    for e in esg_cols:
        row = []
        for s in scm_cols:
            sub = df[[e, s]].dropna()
            row.append(round(sub[e].corr(sub[s]), 3) if len(sub) > 2 else None)
        rows.append(row)
    return pd.DataFrame(rows, index=esg_cols, columns=scm_cols)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-wordmark"><i class="ph ph-duotone ph-leaf"></i> ESG · SCM</div>
    <div class="sidebar-sub">Intelligence Dashboard</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label"><i class="ph ph-database"></i> Data Sources</div>', unsafe_allow_html=True)
    json_file  = st.file_uploader("n8n JSON output",  type="json",
                                   help="Post-processor output from n8n workflow")
    excel_file = st.file_uploader("Excel data file",  type=["xlsx", "xls"],
                                   help="Original ESG-SCM spreadsheet")

    st.markdown('<div class="section-label" style="margin-top:24px"><i class="ph ph-compass"></i> Navigation</div>',
                unsafe_allow_html=True)
    page = st.radio("", [
        "Overview",
        "Correlation Heatmap",
        "Company Comparison",
        "What-If Simulator",
        "Risk Alert Panel",
        "AI Recommendations",
        "Trend Analysis",
    ], label_visibility="collapsed")

    st.markdown("""
    <div style="margin-top:auto;padding-top:40px">
        <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#1e3a58;letter-spacing:0.05em">
            <i class="ph ph-map-pin" style="font-size:0.7rem"></i> INDONESIA · CONSUMER GOODS<br>
            <span style="margin-left:14px">Food & Tobacco Sector</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

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

# ── Empty state / Welcome screen ─────────────────────────────────────────────
if not companies and df_raw is None:
    st.markdown("""
    <div class="hero-section">
        <i class="ph ph-duotone ph-chart-pie-slice" style="font-size:3rem;color:#5ba3f5;margin-bottom:16px"></i>
        <h1>ESG · SCM Intelligence</h1>
        <p>Indonesia Consumer Goods — Food & Tobacco Sector<br>
           Upload your data to unlock AI-powered insights</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="upload-card">
            <i class="ph ph-duotone ph-file-js"></i>
            <h4>n8n JSON Output</h4>
            <p>Upload your workflow output for AI analysis,<br>
               risk data, and recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="upload-card">
            <i class="ph ph-duotone ph-file-xls"></i>
            <h4>Excel Data File</h4>
            <p>Upload your ESG-SCM spreadsheet for correlation<br>
               heatmap, what-if simulator, and trend analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "Overview":
    st.title("Overview")
    st.markdown(f"""
    <div style="font-family:'DM Sans',sans-serif;font-size:0.8rem;color:#3d6282;
                letter-spacing:0.05em;text-transform:uppercase;margin-top:-10px;margin-bottom:20px">
        <i class="ph ph-map-pin" style="font-size:0.75rem"></i> Indonesia · Food &amp; Tobacco &nbsp;·&nbsp; {len(companies)} companies analysed
    </div>
    """, unsafe_allow_html=True)

    if companies:
        risk_counts = pd.Series(
            [safe(c, "risk_assessment", "overall_risk") for c in companies]
        ).value_counts()

        # Custom metric cards row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(metric_card(
                "Companies",
                len(companies),
                "ph-buildings",
                accent="#5ba3f5"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(metric_card(
                "High Risk",
                risk_counts.get("High", 0),
                "ph-warning-circle",
                accent="#ef4444"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(metric_card(
                "Medium Risk",
                risk_counts.get("Medium", 0),
                "ph-warning",
                accent="#f59e0b"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(metric_card(
                "Low Risk",
                risk_counts.get("Low", 0),
                "ph-check-circle",
                accent="#34d399"
            ), unsafe_allow_html=True)

        st.markdown('<div class="fancy-divider"><i class="ph ph-chart-line-down"></i></div>', unsafe_allow_html=True)

        # Overview table
        rows = []
        for c in companies:
            rows.append({
                "Company":        safe(c, "analysis_metadata", "company"),
                "Risk Level":     safe(c, "risk_assessment", "overall_risk"),
                "Confidence":     safe(c, "analysis_metadata", "confidence_level"),
                "ESG Strongest":  safe(c, "esg_performance", "strongest_dimension"),
                "ESG Weakest":    safe(c, "esg_performance", "weakest_dimension"),
                "Data Quality":   str(safe(c, "_quality_score", "default", 100)) + "%",
            })
        ov_df = pd.DataFrame(rows)

        def colour_risk(val):
            m = {
                "High":   "background-color:rgba(239,68,68,0.1);color:#f87171",
                "Medium": "background-color:rgba(245,158,11,0.1);color:#fbbf24",
                "Low":    "background-color:rgba(16,185,129,0.1);color:#34d399",
            }
            return m.get(val, "")

        st.dataframe(
            ov_df.style.map(colour_risk, subset=["Risk Level"]),
            use_container_width=True,
            height=420,
        )

        st.markdown('<div class="fancy-divider"><i class="ph ph-note"></i></div>', unsafe_allow_html=True)
        st.subheader("Executive Summaries")

        for c in companies:
            name = safe(c, "analysis_metadata", "company")
            risk = safe(c, "risk_assessment", "overall_risk")
            badge_cls = {"High": "badge-high", "Medium": "badge-medium",
                         "Low": "badge-low"}.get(risk, "badge-na")

            with st.expander(f"{risk_dot(risk)} {name}"):
                st.markdown(
                    f'<span class="badge {badge_cls}">{risk} Risk</span>'
                    f'&nbsp;&nbsp;<span style="font-family:\'DM Sans\';font-size:0.78rem;color:#3d6282">'
                    f'{safe(c,"analysis_metadata","confidence_level")} confidence</span>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    f'<div style="font-family:\'DM Sans\';font-size:0.88rem;color:#8aacc8;'
                    f'line-height:1.7;margin-top:12px">{safe(c,"executive_summary")}</div>',
                    unsafe_allow_html=True
                )
    else:
        st.markdown("""
        <div class="info-panel">
            <h4><i class="ph ph-warning"></i> No data loaded</h4>
            <p>Upload your n8n JSON file to see company overview and risk analysis.</p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CORRELATION HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Correlation Heatmap":
    st.title("Correlation Heatmap")
    st.markdown(
        '<div class="section-label"><i class="ph ph-chart-scatter"></i> ESG Dimensions vs SCM / Financial Metrics · Pearson r</div>',
        unsafe_allow_html=True
    )

    if df_raw is None:
        st.markdown("""
        <div class="info-panel">
            <h4><i class="ph ph-file-xls"></i> Excel file required</h4>
            <p>Upload your ESG-SCM spreadsheet to generate the correlation heatmap.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    ESG_OPTIONS = [c for c in [
        "ESG_SCORE","EMISSIONS_SCORE","ENVIRONMENTAL_INNOVATION_SCORE",
        "RESOURCE_USE_SCORE","COMMUNITY_SCORE","HUMAN_RIGHTS_SCORE",
        "PRODUCT_RESPONSIBILITY_SCORE","WORKFORCE_SCORE",
        "CSR_STRATEGY_SCORE","MANAGEMENT_SCORE","SHAREHOLDERS_SCORE"
    ] if c in df_raw.columns]

    SCM_OPTIONS = [c for c in [
        "CASH_CONVERSION_CYCLE","AVERAGE_INVENTORY_DAYS",
        "INVENTORY_TURNOVER","DAYS_SALES_OUTSTANDING",
        "DAYS_PAYABLES_OUTSTANDING","ROA_TOTAL_ASSETS",
        "PROFIT_MARGIN","EBITDA_MARGIN"
    ] if c in df_raw.columns]

    col1, col2 = st.columns(2)
    sel_esg = col1.multiselect("ESG dimensions",         ESG_OPTIONS, default=ESG_OPTIONS[:5])
    sel_scm = col2.multiselect("SCM / Financial metrics", SCM_OPTIONS, default=SCM_OPTIONS[:4])

    if sel_esg and sel_scm:
        if "YEAR" in df_raw.columns:
            years = sorted(df_raw["YEAR"].dropna().unique().astype(int).tolist())
            sel_years = st.select_slider("Year range", options=years,
                                          value=(years[0], years[-1]))
            df_f = df_raw[df_raw["YEAR"].between(sel_years[0], sel_years[1])].copy()
        else:
            df_f = df_raw.copy()

        for c in sel_esg + sel_scm:
            df_f[c] = pd.to_numeric(df_f[c], errors="coerce")

        cm = corr_matrix(df_f, sel_esg, sel_scm)

        fig = px.imshow(
            cm,
            text_auto=".2f",
            color_continuous_scale=[
                [0.0,  "#ef4444"],
                [0.25, "#b45309"],
                [0.5,  "#1e3354"],
                [0.75, "#1a5c3a"],
                [1.0,  "#10b981"],
            ],
            zmin=-1, zmax=1,
            aspect="auto",
        )
        fig.update_layout(
            **PLOT_LAYOUT,
            height=420,
            coloraxis_colorbar=dict(
                title="r",
                tickfont=dict(family="DM Mono, monospace", size=10, color="#4d718f"),
                titlefont=dict(family="DM Sans, sans-serif", size=11, color="#4d718f"),
            ),
        )
        fig.update_traces(
            textfont=dict(family="DM Mono, monospace", size=11)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Strongest Correlations")
        pairs = []
        for e in sel_esg:
            for s in sel_scm:
                v = cm.loc[e, s]
                if pd.notna(v):
                    pairs.append({"ESG": e, "SCM / Finance": s, "r": v, "|r|": abs(v)})

        pairs_df = pd.DataFrame(pairs).sort_values("|r|", ascending=False).head(8)

        def interp(r):
            a = abs(r)
            if a < 0.2: return "Negligible"
            if a < 0.4: return "Weak"
            if a < 0.6: return "Moderate"
            if a < 0.8: return "Strong"
            return "Very strong"

        pairs_df["Strength"]  = pairs_df["r"].apply(interp)
        pairs_df["Direction"] = pairs_df["r"].apply(lambda x: "Positive" if x > 0 else "Negative")
        st.dataframe(
            pairs_df[["ESG", "SCM / Finance", "r", "Strength", "Direction"]],
            use_container_width=True,
        )
    else:
        st.info("Select at least one ESG dimension and one SCM metric.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: COMPANY COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Company Comparison":
    st.title("Company Comparison")

    if df_raw is None and not companies:
        st.markdown("""
        <div class="info-panel">
            <h4><i class="ph ph-warning"></i> No data loaded</h4>
            <p>Upload your Excel file and/or n8n JSON to compare companies.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    if df_raw is not None and "COMPANY" in df_raw.columns:
        company_list = sorted(df_raw["COMPANY"].dropna().unique().tolist())
        sel = st.multiselect("Select companies", company_list, default=company_list[:4])

        if sel:
            if "YEAR" in df_raw.columns:
                df_latest = df_raw.sort_values("YEAR").groupby("COMPANY").last().reset_index()
            else:
                df_latest = df_raw.copy()
            df_sel = df_latest[df_latest["COMPANY"].isin(sel)]

            # Radar chart
            radar_cols = [c for c in [
                "ESG_SCORE","EMISSIONS_SCORE","COMMUNITY_SCORE",
                "MANAGEMENT_SCORE","INVENTORY_TURNOVER","ROA_TOTAL_ASSETS"
            ] if c in df_raw.columns]

            if radar_cols:
                st.subheader("Multi-Dimension Radar")
                fig = go.Figure()
                for i, (_, row) in enumerate(df_sel.iterrows()):
                    vals = [pd.to_numeric(row.get(c, 0), errors="coerce") or 0 for c in radar_cols]
                    maxv = [df_raw[c].dropna().apply(pd.to_numeric, errors="coerce").max() for c in radar_cols]
                    norm = [v / m * 100 if m and m > 0 else 0 for v, m in zip(vals, maxv)]
                    
                    c = ACCENT_COLORS[i % len(ACCENT_COLORS)]
                    r_rgb, g_rgb, b_rgb = tuple(int(c.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                    
                    fig.add_trace(go.Scatterpolar(
                        r=norm + [norm[0]],
                        theta=radar_cols + [radar_cols[0]],
                        fill="toself",
                        name=str(row["COMPANY"]),
                        opacity=0.65,
                        line=dict(color=c, width=1.5),
                        fillcolor=f"rgba({r_rgb},{g_rgb},{b_rgb},0.1)",
                    ))

                fig.update_layout(
                    **PLOT_LAYOUT,
                    polar=dict(
                        bgcolor="rgba(0,0,0,0)",
                        angularaxis=dict(
                            tickfont=dict(size=10, family="DM Mono, monospace", color="#4d718f"),
                            linecolor="#152236", gridcolor="#0e1f33",
                        ),
                        radialaxis=dict(
                            visible=True, range=[0, 100],
                            tickfont=dict(size=9, family="DM Mono, monospace", color="#2d5070"),
                            linecolor="#152236", gridcolor="#0e1f33",
                        ),
                    ),
                    height=500,
                    legend=dict(orientation="h", y=-0.12),
                )
                st.plotly_chart(fig, use_container_width=True)

            # Bar comparison
            st.subheader("Side-by-Side Metric")
            num_cols = [c for c in [
                "ESG_SCORE","CASH_CONVERSION_CYCLE","INVENTORY_TURNOVER",
                "ROA_TOTAL_ASSETS","PROFIT_MARGIN","AVERAGE_INVENTORY_DAYS"
            ] if c in df_raw.columns]
            metric = st.selectbox("Metric", num_cols)
            df_bar = df_sel[["COMPANY", metric]].copy()
            df_bar[metric] = pd.to_numeric(df_bar[metric], errors="coerce")

            fig2 = px.bar(
                df_bar, x="COMPANY", y=metric,
                color="COMPANY",
                color_discrete_sequence=ACCENT_COLORS,
            )
            fig2.update_layout(**PLOT_LAYOUT, showlegend=False, height=360)
            fig2.update_traces(marker_line_width=0)
            st.plotly_chart(fig2, use_container_width=True)

            # Benchmark
            st.subheader("Benchmark vs Industry")
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
                    if col not in df_raw.columns:
                        continue
                    val = pd.to_numeric(row.get(col), errors="coerce")
                    if pd.isna(val):
                        continue
                    status = ("In range" if lo <= val <= hi
                              else ("Above range" if val > hi else "Below range"))
                    bm_rows.append({
                        "Company":   row["COMPANY"],
                        "Metric":    col,
                        "Value":     round(val, 3),
                        "Benchmark": f"{lo}–{hi} {unit}",
                        "Status":    status,
                    })
            if bm_rows:
                bm_df = pd.DataFrame(bm_rows)

                def colour_status(val):
                    if val == "In range":  return "color:#34d399"
                    if val == "Above range": return "color:#f87171"
                    return "color:#fbbf24"

                st.dataframe(
                    bm_df.style.map(colour_status, subset=["Status"]),
                    use_container_width=True,
                )
    else:
        st.info("Upload your Excel file to use the comparison tool.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: WHAT-IF SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "What-If Simulator":
    st.title("What-If Simulator")
    st.markdown(
        '<div class="section-label"><i class="ph ph-magic-wand"></i> Estimate how ESG improvement affects supply chain performance</div>',
        unsafe_allow_html=True
    )

    if df_raw is None:
        st.markdown("""
        <div class="info-panel">
            <h4><i class="ph ph-file-xls"></i> Excel file required</h4>
            <p>Upload your ESG-SCM spreadsheet to use the What-If Simulator.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    for c in df_raw.columns:
        if c not in ["COMPANY"]:
            df_raw[c] = pd.to_numeric(df_raw[c], errors="coerce")

    ESG_DIMS = {
        "Environmental (avg)": ["EMISSIONS_SCORE","ENVIRONMENTAL_INNOVATION_SCORE","RESOURCE_USE_SCORE"],
        "Social (avg)":        ["COMMUNITY_SCORE","HUMAN_RIGHTS_SCORE","PRODUCT_RESPONSIBILITY_SCORE","WORKFORCE_SCORE"],
        "Governance (avg)":    ["CSR_STRATEGY_SCORE","MANAGEMENT_SCORE","SHAREHOLDERS_SCORE"],
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
    target_choice = col2.selectbox("Target metric", list(TARGETS.keys()))
    improvement   = st.slider("ESG improvement (%)", 1, 50, 10)

    esg_cols = [c for c in ESG_DIMS[esg_choice] if c in df_raw.columns]
    tgt_col  = TARGETS[target_choice]

    if not esg_cols or tgt_col not in df_raw.columns:
        st.warning("Some required columns are missing from your Excel file.")
        st.stop()

    df_sim = df_raw.copy()
    df_sim["_esg"] = df_sim[esg_cols].mean(axis=1)
    df_sim = df_sim[["COMPANY", "YEAR", "_esg", tgt_col]].dropna() if "YEAR" in df_raw.columns \
        else df_sim[["COMPANY", "_esg", tgt_col]].dropna()

    r = df_sim["_esg"].corr(df_sim[tgt_col])

    if "YEAR" in df_sim.columns:
        df_latest = df_sim.sort_values("YEAR").groupby("COMPANY").last().reset_index()
    else:
        df_latest = df_sim.copy()

    df_latest["ESG Current"]   = df_latest["_esg"]
    df_latest["ESG Projected"] = df_latest["_esg"] * (1 + improvement / 100)

    x = df_sim["_esg"].values
    y = df_sim[tgt_col].values
    slope = np.polyfit(x, y, 1)[0] if len(x) > 2 else r

    df_latest[f"{target_choice} Current"]   = df_latest[tgt_col]
    df_latest[f"{target_choice} Projected"] = (
        df_latest[tgt_col]
        + slope * (df_latest["ESG Projected"] - df_latest["ESG Current"])
    )

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Correlation (r)",    f"{r:.3f}")
    c2.metric("Regression slope",   f"{slope:.4f}")
    c3.metric("ESG improvement",    f"+{improvement}%")

    if abs(r) < 0.2:
        st.info("Correlation is weak (|r| < 0.2) — projection is indicative only.")
    elif r > 0:
        st.success(f"Positive correlation: improving {esg_choice} tends to increase {target_choice}.")
    else:
        st.success(f"Negative correlation: improving {esg_choice} tends to decrease {target_choice} (favourable for CCC / DIO).")

    fig = go.Figure()
    for i, (_, row) in enumerate(df_latest.iterrows()):
        color = ACCENT_COLORS[i % len(ACCENT_COLORS)]
        fig.add_trace(go.Bar(
            name=str(row["COMPANY"]),
            x=["Current", f"Projected (+{improvement}%)"],
            y=[row[f"{target_choice} Current"], row[f"{target_choice} Projected"]],
            text=[f"{row[f'{target_choice} Current']:.2f}",
                  f"{row[f'{target_choice} Projected']:.2f}"],
            textposition="outside",
            textfont=dict(family="DM Mono, monospace", size=10),
            marker_color=color,
            marker_line_width=0,
        ))

    fig.update_layout(
        **PLOT_LAYOUT,
        barmode="group",
        title=f"Projected impact on {target_choice} — {esg_choice} +{improvement}%",
        height=440,
        xaxis_title="",
        yaxis_title=target_choice,
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Company-level Projections")
    tbl = df_latest[["COMPANY",
                      f"{target_choice} Current",
                      f"{target_choice} Projected"]].copy()
    tbl["Change"]   = tbl[f"{target_choice} Projected"] - tbl[f"{target_choice} Current"]
    tbl["Change %"] = (tbl["Change"] / tbl[f"{target_choice} Current"].abs() * 100).round(2)
    st.dataframe(tbl.round(3), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: RISK ALERT PANEL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Risk Alert Panel":
    st.title("Risk Alert Panel")

    if not companies:
        st.markdown("""
        <div class="info-panel">
            <h4><i class="ph ph-warning"></i> No data loaded</h4>
            <p>Upload your n8n JSON file to view risk alerts and flags.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    CONTROVERSIES = {
        "AALI.JK": "Deforestation & palm oil sustainability concerns — RSPO compliance issues",
        "GGRM.JK": "Tobacco health impact — increasing regulatory pressure in Indonesia",
        "HMSP.JK": "Tobacco sector — ESG exclusion risk from institutional investors",
        "UNVR.JK": "Negative ROA — financial distress signals despite strong ESG score",
        "CPIN.JK": "Poultry supply chain — animal welfare & antibiotic use concerns",
    }

    high   = [c for c in companies if safe(c, "risk_assessment", "overall_risk") == "High"]
    medium = [c for c in companies if safe(c, "risk_assessment", "overall_risk") == "Medium"]
    low    = [c for c in companies if safe(c, "risk_assessment", "overall_risk") == "Low"]

    # Custom metric cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(metric_card(
            "High Risk",
            len(high),
            "ph-warning-circle",
            accent="#ef4444"
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card(
            "Medium Risk",
            len(medium),
            "ph-warning",
            accent="#f59e0b"
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card(
            "Low Risk",
            len(low),
            "ph-check-circle",
            accent="#34d399"
        ), unsafe_allow_html=True)

    st.markdown('<div class="fancy-divider"><i class="ph ph-flag"></i></div>', unsafe_allow_html=True)

    # ESG Controversy flags
    st.subheader("ESG Controversy Flags")
    flagged = [
        (c, CONTROVERSIES[safe(c, "analysis_metadata", "company")])
        for c in companies
        if safe(c, "analysis_metadata", "company") in CONTROVERSIES
    ]

    if flagged:
        for c, note in flagged:
            name = safe(c, "analysis_metadata", "company")
            risk = safe(c, "risk_assessment", "overall_risk")
            cls  = {"High": "alert-card-high", "Medium": "alert-card-medium",
                    "Low": "alert-card-low"}.get(risk, "alert-card-high")
            icon = {"High": "ph-fire", "Medium": "ph-warning", "Low": "ph-info"}.get(risk, "ph-warning")
            st.markdown(f"""
            <div class="alert-card {cls}">
                <span class="alert-icon"><i class="ph {icon}"></i></span>
                <strong>{name}</strong>
                &nbsp;{risk_badge(risk)}
                <small>{note}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No controversy flags for current companies.")

    st.markdown('<div class="fancy-divider"><i class="ph ph-buildings"></i></div>', unsafe_allow_html=True)

    # Risk breakdown
    st.subheader("Company Risk Breakdown")
    risk_filter = st.multiselect(
        "Filter by risk level",
        ["High", "Medium", "Low"],
        default=["High", "Medium"]
    )

    for c in companies:
        name    = safe(c, "analysis_metadata", "company")
        overall = safe(c, "risk_assessment", "overall_risk")
        risk    = overall
        if overall not in risk_filter:
            continue

        op_r  = c.get("risk_assessment", {}).get("operational_risks",  []) or []
        rep_r = c.get("risk_assessment", {}).get("reputational_risks", []) or []
        fin_r = c.get("risk_assessment", {}).get("financial_risks",    []) or []

        with st.expander(f"{risk_dot(overall)} {name}"):
            st.markdown(risk_badge(overall), unsafe_allow_html=True)
            st.markdown("")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="section-label"><i class="ph ph-gear"></i> Operational</div>', unsafe_allow_html=True)
                for r in (op_r if isinstance(op_r, list) else [op_r]):
                    st.markdown(
                        f'<div style="font-family:\'DM Sans\';font-size:0.83rem;'
                        f'color:#8aacc8;padding:3px 0"><i class="ph ph-caret-right" style="font-size:0.7rem;margin-right:6px;color:#4d718f"></i>{r}</div>',
                        unsafe_allow_html=True
                    )
            with col2:
                st.markdown('<div class="section-label"><i class="ph ph-users"></i> Reputational</div>', unsafe_allow_html=True)
                for r in (rep_r if isinstance(rep_r, list) else [rep_r]):
                    st.markdown(
                        f'<div style="font-family:\'DM Sans\';font-size:0.83rem;'
                        f'color:#8aacc8;padding:3px 0"><i class="ph ph-caret-right" style="font-size:0.7rem;margin-right:6px;color:#4d718f"></i>{r}</div>',
                        unsafe_allow_html=True
                    )
            with col3:
                st.markdown('<div class="section-label"><i class="ph ph-currency-dollar"></i> Financial</div>', unsafe_allow_html=True)
                for r in (fin_r if isinstance(fin_r, list) else [fin_r]):
                    st.markdown(
                        f'<div style="font-family:\'DM Sans\';font-size:0.83rem;'
                        f'color:#8aacc8;padding:3px 0"><i class="ph ph-caret-right" style="font-size:0.7rem;margin-right:6px;color:#4d718f"></i>{r}</div>',
                        unsafe_allow_html=True
                    )

    st.markdown('<div class="fancy-divider"><i class="ph ph-chart-bar"></i></div>', unsafe_allow_html=True)

    # Risk distribution
    st.subheader("Risk Distribution")
    risk_df = pd.DataFrame([{
        "Company":    safe(c, "analysis_metadata", "company"),
        "Risk":       safe(c, "risk_assessment", "overall_risk"),
        "Confidence": safe(c, "analysis_metadata", "confidence_level"),
    } for c in companies])

    dist = (
        risk_df["Risk"]
        .value_counts()
        .reindex(["High", "Medium", "Low"], fill_value=0)
        .reset_index(name="count")
        .rename(columns={"index": "Risk"})
    )
    fig = px.bar(
        dist, x="Risk", y="count",
        color="Risk",
        color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"},
        text="count",
    )
    fig.update_layout(**PLOT_LAYOUT, showlegend=False, height=300)
    fig.update_traces(textposition="outside", marker_line_width=0,
                      textfont=dict(family="DM Mono, monospace", size=11))
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AI RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "AI Recommendations":
    st.title("AI Recommendations")
    st.markdown(
        '<div class="section-label"><i class="ph ph-robot"></i> Powered by n8n AI Agent</div>',
        unsafe_allow_html=True
    )

    if not companies:
        st.markdown("""
        <div class="info-panel">
            <h4><i class="ph ph-warning"></i> No data loaded</h4>
            <p>Upload your n8n JSON file to see AI-generated recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    rec_rows = []
    for c in companies:
        name = safe(c, "analysis_metadata", "company")
        for r in (c.get("recommendations") or []):
            rec_rows.append({
                "Company":  name,
                "Priority": r.get("priority",        "N/A"),
                "Category": r.get("category",        "N/A"),
                "Action":   r.get("action",          "N/A"),
                "Impact":   r.get("expected_impact", "N/A"),
                "Timeline": r.get("timeline",        "N/A"),
            })
    rec_df = pd.DataFrame(rec_rows)

    if rec_df.empty:
        st.info("No recommendations found in JSON.")
        st.stop()

    col1, col2, col3 = st.columns(3)
    pri_f = col1.multiselect("Priority", ["High", "Medium", "Low"],
                              default=["High", "Medium", "Low"])
    cat_f = col2.multiselect("Category", rec_df["Category"].unique().tolist(),
                              default=rec_df["Category"].unique().tolist())
    co_f  = col3.multiselect("Company",  rec_df["Company"].unique().tolist(),
                              default=rec_df["Company"].unique().tolist())

    filtered = rec_df[
        rec_df["Priority"].isin(pri_f) &
        rec_df["Category"].isin(cat_f) &
        rec_df["Company"].isin(co_f)
    ]

    st.markdown(
        f'<div class="section-label"><i class="ph ph-list-checks"></i> {len(filtered)} recommendations</div>',
        unsafe_allow_html=True
    )

    # Display recommendations as cards in a grid
    priority_colors = {
        "High": ("#ef4444", "badge-high"),
        "Medium": ("#f59e0b", "badge-medium"),
        "Low": ("#34d399", "badge-low"),
    }
    priority_icons = {
        "High": "ph-arrow-circle-up",
        "Medium": "ph-minus-circle",
        "Low": "ph-arrow-circle-down",
    }
    category_icons = {
        "Operational": "ph-gear",
        "Financial": "ph-currency-dollar",
        "Environmental": "ph-leaf",
        "Social": "ph-users",
        "Governance": "ph-scales",
        "N/A": "ph-question",
    }

    # Show cards in 2-column layout
    if len(filtered) > 0:
        card_cols = st.columns(2)
        for idx, (_, row) in enumerate(filtered.iterrows()):
            col = card_cols[idx % 2]
            with col:
                pri = row["Priority"]
                pri_color, pri_class = priority_colors.get(pri, ("#64748b", "badge-na"))
                pri_icon = priority_icons.get(pri, "ph-minus")
                cat_icon = category_icons.get(row["Category"], "ph-tag")
                
                st.markdown(f"""
                <div class="rec-card">
                    <div class="rec-card-header">
                        <div class="rec-card-title">
                            <i class="ph {pri_icon}" style="color:{pri_color};margin-right:8px;font-size:1rem"></i>
                            {row["Action"]}
                        </div>
                        <span class="badge {pri_class}"><i class="ph {pri_icon}"></i>{pri}</span>
                    </div>
                    <div class="rec-card-body">{row["Impact"]}</div>
                    <div class="rec-card-meta">
                        <span class="rec-card-tag"><i class="ph {cat_icon}" style="margin-right:4px"></i>{row["Category"]}</span>
                        <span class="rec-card-tag"><i class="ph ph-buildings" style="margin-right:4px"></i>{row["Company"]}</span>
                        <span class="rec-card-tag"><i class="ph ph-clock" style="margin-right:4px"></i>{row["Timeline"]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('<div class="fancy-divider"><i class="ph ph-chart-pie"></i></div>', unsafe_allow_html=True)

    def colour_priority(val):
        m = {
            "High":   "background-color:rgba(239,68,68,0.1);color:#f87171",
            "Medium": "background-color:rgba(245,158,11,0.1);color:#fbbf24",
            "Low":    "background-color:rgba(16,185,129,0.1);color:#34d399",
        }
        return m.get(val, "")

    st.subheader("Recommendations Table")
    st.dataframe(
        filtered.style.map(colour_priority, subset=["Priority"]),
        use_container_width=True,
        height=300,
    )

    st.markdown('<div class="fancy-divider"><i class="ph ph-chart-bar"></i></div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("By Priority")
        pc = filtered["Priority"].value_counts().reset_index()
        fig = px.pie(
            pc, names="Priority", values="count",
            hole=0.52,
            color="Priority",
            color_discrete_map={
                "High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"
            },
        )
        fig.update_layout(**PLOT_LAYOUT, height=280,
                          legend=dict(orientation="h", y=-0.15))
        fig.update_traces(
            textfont=dict(family="DM Mono, monospace", size=10),
            marker=dict(line=dict(color="#07101d", width=3)),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("By Category")
        cc = filtered["Category"].value_counts().reset_index()
        fig2 = px.bar(
            cc, x="Category", y="count",
            color="Category",
            color_discrete_sequence=ACCENT_COLORS,
        )
        fig2.update_layout(**PLOT_LAYOUT, showlegend=False, height=280)
        fig2.update_traces(marker_line_width=0)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Priority by Company")
    pivot = filtered.groupby(["Company", "Priority"]).size().reset_index(name="Count")
    fig3 = px.bar(
        pivot, x="Company", y="Count",
        color="Priority", barmode="stack",
        color_discrete_map={
            "High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"
        },
    )
    fig3.update_layout(**PLOT_LAYOUT, height=360, xaxis_tickangle=-30)
    fig3.update_traces(marker_line_width=0)
    st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: TREND ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Trend Analysis":
    st.title("Trend Analysis")
    st.markdown(
        '<div class="section-label"><i class="ph ph-trend-up"></i> Year-over-year performance across ESG &amp; SCM metrics</div>',
        unsafe_allow_html=True
    )

    if df_raw is None:
        st.markdown("""
        <div class="info-panel">
            <h4><i class="ph ph-file-xls"></i> Excel file required</h4>
            <p>Upload your ESG-SCM spreadsheet to see trend analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    if "YEAR" not in df_raw.columns or "COMPANY" not in df_raw.columns:
        st.error("Excel file must contain YEAR and COMPANY columns.")
        st.stop()

    df_raw["YEAR"] = pd.to_numeric(df_raw["YEAR"], errors="coerce")
    company_list = sorted(df_raw["COMPANY"].dropna().unique().tolist())

    col1, col2 = st.columns(2)
    sel_companies = col1.multiselect("Companies", company_list, default=company_list[:4])

    TREND_METRICS = [c for c in [
        "ESG_SCORE","EMISSIONS_SCORE","COMMUNITY_SCORE","MANAGEMENT_SCORE",
        "CASH_CONVERSION_CYCLE","AVERAGE_INVENTORY_DAYS","INVENTORY_TURNOVER",
        "ROA_TOTAL_ASSETS","PROFIT_MARGIN","EBITDA_MARGIN"
    ] if c in df_raw.columns]

    sel_metric = col2.selectbox("Metric", TREND_METRICS)

    if sel_companies and sel_metric:
        df_trend = (
            df_raw[df_raw["COMPANY"].isin(sel_companies)][["COMPANY", "YEAR", sel_metric]]
            .copy()
        )
        df_trend["YEAR"]      = pd.to_numeric(df_trend["YEAR"],      errors="coerce")
        df_trend[sel_metric]  = pd.to_numeric(df_trend[sel_metric],  errors="coerce")
        df_trend = df_trend.dropna(subset=["COMPANY", "YEAR"]).sort_values(["COMPANY", "YEAR"])

        fig = px.line(
            df_trend, x="YEAR", y=sel_metric,
            color="COMPANY", markers=True,
            color_discrete_sequence=ACCENT_COLORS,
        )
        fig.update_layout(**PLOT_LAYOUT, height=400, xaxis=dict(dtick=1))
        fig.update_traces(line=dict(width=1.8), marker=dict(size=6))
        st.plotly_chart(fig, use_container_width=True)

        # YoY table
        st.subheader("Year-over-Year Change")
        yoy_rows = []
        for comp in sel_companies:
            sub = df_trend[df_trend["COMPANY"] == comp].sort_values("YEAR").copy()
            sub["YoY Change"] = sub[sel_metric].diff()
            sub["YoY %"]      = sub[sel_metric].pct_change() * 100
            yoy_rows.append(sub)
        if yoy_rows:
            yoy_df = pd.concat(yoy_rows).round(3)
            st.dataframe(yoy_df, use_container_width=True, height=320)

        # ESG vs SCM correlation over time
        st.subheader("ESG vs SCM — Correlation by Year")
        ESG_C = [c for c in ["ESG_SCORE", "EMISSIONS_SCORE"]              if c in df_raw.columns]
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
                                "r":    round(vals[e].corr(vals[s]), 3),
                            })
            if corr_by_year:
                cy_df = pd.DataFrame(corr_by_year)
                fig2 = px.line(
                    cy_df, x="Year", y="r",
                    color="Pair", markers=True,
                    color_discrete_sequence=ACCENT_COLORS,
                )
                fig2.add_hline(y=0, line_dash="dot", line_color="#1e3354", opacity=0.8)
                fig2.update_layout(**PLOT_LAYOUT, height=380, xaxis=dict(dtick=1),
                                   yaxis_title="Pearson r")
                fig2.update_traces(line=dict(width=1.8), marker=dict(size=6))
                st.plotly_chart(fig2, use_container_width=True)
