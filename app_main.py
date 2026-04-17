import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ESG · SCM Intelligence",
    page_icon="🌀",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────
# DESIGN SYSTEM (SIMPLIFIED CLEAN VERSION)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
body, [data-testid="stAppViewContainer"] {
    background: #07101d;
    color: #c8d6e8;
    font-family: 'Segoe UI', sans-serif;
}
[data-testid="stSidebar"] {
    background: #060e1a;
}
.metric-card {
    background:#0c1828;
    border:1px solid #152236;
    border-radius:12px;
    padding:20px;
}
.badge {
    padding:4px 10px;
    border-radius:6px;
    font-size:0.7rem;
}
.badge-high {background:#2a0a0a;color:#f87171;}
.badge-medium {background:#2a1a03;color:#fbbf24;}
.badge-low {background:#052e16;color:#34d399;}
.alert-card {
    background:#0c1828;
    border-left:3px solid;
    padding:12px;
    border-radius:8px;
    margin-bottom:10px;
}
.alert-card-high {border-color:#ef4444;}
.alert-card-medium {border-color:#f59e0b;}
.alert-card-low {border-color:#10b981;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HELPERS (LOGIC KEPT)
# ─────────────────────────────────────────────────────────────
def safe(d, *keys, default="N/A"):
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k, default)
        if d is None:
            return default
    return d

def corr_matrix(df, esg_cols, scm_cols):
    rows = []
    for e in esg_cols:
        row = []
        for s in scm_cols:
            sub = df[[e, s]].dropna()
            row.append(round(sub[e].corr(sub[s]), 3) if len(sub) > 2 else np.nan)
        rows.append(row)
    return pd.DataFrame(rows, index=esg_cols, columns=scm_cols)

def risk_badge(r):
    cls = {"High":"badge-high","Medium":"badge-medium","Low":"badge-low"}.get(r,"badge-low")
    return f'<span class="badge {cls}">{r}</span>'

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("ESG · SCM")
    st.caption("Intelligence Dashboard")

    json_file = st.file_uploader("Upload JSON", type="json")
    excel_file = st.file_uploader("Upload Excel", type=["xlsx","xls"])

    page = st.radio("Navigation", [
        "Overview",
        "Correlation Heatmap",
        "Company Comparison",
        "What-If Simulator",
        "Risk Alert Panel",
        "AI Recommendations",
        "Trend Analysis"
    ])

# ─────────────────────────────────────────────────────────────
# LOAD DATA (ORIGINAL LOGIC)
# ─────────────────────────────────────────────────────────────
companies, df_raw = [], None

if json_file:
    raw = json.load(json_file)
    if isinstance(raw, list):
        raw = raw[0]
    companies = raw.get("companies", [])

if excel_file:
    df_raw = pd.read_excel(excel_file)
    df_raw.columns = [c.strip().upper().replace(" ","_") for c in df_raw.columns]

# ─────────────────────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────────────────────
if not companies and df_raw is None:
    st.title("ESG · SCM Intelligence")
    st.info("Upload JSON and/or Excel to begin.")
    st.stop()

# ─────────────────────────────────────────────────────────────
# OVERVIEW
# ─────────────────────────────────────────────────────────────
if page == "Overview":
    st.title("Overview")

    if companies:
        risk_counts = pd.Series([
            safe(c,"risk_assessment","overall_risk") for c in companies
        ]).value_counts()

        col1,col2,col3,col4 = st.columns(4)
        col1.metric("Companies", len(companies))
        col2.metric("High Risk", risk_counts.get("High",0))
        col3.metric("Medium Risk", risk_counts.get("Medium",0))
        col4.metric("Low Risk", risk_counts.get("Low",0))

        rows = []
        for c in companies:
            rows.append({
                "Company": safe(c,"analysis_metadata","company"),
                "Risk": safe(c,"risk_assessment","overall_risk"),
                "Confidence": safe(c,"analysis_metadata","confidence_level"),
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        for c in companies:
            name = safe(c,"analysis_metadata","company")
            risk = safe(c,"risk_assessment","overall_risk")

            with st.expander(name):
                st.markdown(risk_badge(risk), unsafe_allow_html=True)
                st.write(safe(c,"executive_summary"))

# ─────────────────────────────────────────────────────────────
# CORRELATION HEATMAP
# ─────────────────────────────────────────────────────────────
elif page == "Correlation Heatmap":
    st.title("Correlation Heatmap")

    if df_raw is None:
        st.warning("Upload Excel.")
        st.stop()

    esg = [c for c in df_raw.columns if "SCORE" in c]
    scm = [c for c in df_raw.columns if "MARGIN" in c or "CYCLE" in c]

    cm = corr_matrix(df_raw, esg[:5], scm[:5])

    fig = px.imshow(cm, text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# COMPANY COMPARISON
# ─────────────────────────────────────────────────────────────
elif page == "Company Comparison":
    st.title("Company Comparison")

    if df_raw is None:
        st.warning("Upload Excel.")
        st.stop()

    companies_list = df_raw["COMPANY"].unique()
    sel = st.multiselect("Select", companies_list)

    df_sel = df_raw[df_raw["COMPANY"].isin(sel)]

    metric = st.selectbox("Metric", df_raw.columns)

    fig = px.bar(df_sel, x="COMPANY", y=metric)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# WHAT IF
# ─────────────────────────────────────────────────────────────
elif page == "What-If Simulator":
    st.title("What-If Simulator")

    if df_raw is None:
        st.warning("Upload Excel.")
        st.stop()

    col = st.selectbox("Column", df_raw.columns)
    improvement = st.slider("Improvement %", 1, 50, 10)

    df_raw["Projected"] = df_raw[col]*(1+improvement/100)

    st.dataframe(df_raw[["COMPANY",col,"Projected"]])

# ─────────────────────────────────────────────────────────────
# RISK PANEL
# ─────────────────────────────────────────────────────────────
elif page == "Risk Alert Panel":
    st.title("Risk Alerts")

    for c in companies:
        risk = safe(c,"risk_assessment","overall_risk")
        name = safe(c,"analysis_metadata","company")

        st.markdown(f"""
        <div class="alert-card alert-card-high">
        <strong>{name}</strong> - {risk}
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# AI RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────
elif page == "AI Recommendations":
    st.title("AI Recommendations")

    for c in companies:
        for r in (c.get("recommendations") or []):
            st.write(f"{r.get('action')} — {r.get('priority')}")

# ─────────────────────────────────────────────────────────────
# TREND
# ─────────────────────────────────────────────────────────────
elif page == "Trend Analysis":
    st.title("Trend Analysis")

    if df_raw is None:
        st.warning("Upload Excel.")
        st.stop()

    metric = st.selectbox("Metric", df_raw.columns)

    fig = px.line(df_raw, x="YEAR", y=metric, color="COMPANY")
    st.plotly_chart(fig, use_container_width=True)
