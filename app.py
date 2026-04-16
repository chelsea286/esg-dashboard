import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="ESG · SCM Intelligence",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Design System ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Page background ── */
.stApp { background: #F7F6F3; }
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E8E6E1;
}

/* ── Sidebar nav radio ── */
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.85rem;
    color: #6B6860;
    padding: 6px 10px;
    border-radius: 6px;
    cursor: pointer;
    display: block;
}
[data-testid="stSidebar"] .stRadio label:hover { background: #F7F6F3; color: #1A1916; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E8E6E1;
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #9B9890;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 2rem;
    font-weight: 600;
    color: #1A1916;
    line-height: 1.2;
}

/* ── Cards / containers ── */
.card {
    background: #FFFFFF;
    border: 1px solid #E8E6E1;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* ── Risk badges ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.badge-high   { background: #FEF2F2; color: #C53030; border: 1px solid #FED7D7; }
.badge-medium { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
.badge-low    { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }

/* ── Alert strips ── */
.alert-strip {
    border-radius: 10px;
    padding: 14px 18px;
    margin: 6px 0;
    border-left: 3px solid;
}
.alert-high-strip  { background: #FEF2F2; border-color: #FC8181; }
.alert-med-strip   { background: #FFFBEB; border-color: #F6AD55; }

/* ── Section headers ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9B9890;
    margin: 20px 0 10px;
}

/* ── Page title ── */
.page-title {
    font-size: 1.6rem;
    font-weight: 600;
    color: #1A1916;
    letter-spacing: -0.02em;
    margin-bottom: 2px;
}
.page-subtitle {
    font-size: 0.85rem;
    color: #9B9890;
    margin-bottom: 24px;
}

/* ── Divider ── */
hr { border: none; border-top: 1px solid #E8E6E1; margin: 20px 0; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #FFFFFF;
    border: 1px solid #E8E6E1 !important;
    border-radius: 10px !important;
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    font-weight: 500;
    font-size: 0.9rem;
    color: #1A1916;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #E8E6E1;
}

/* ── Inputs / selects / sliders ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: #FFFFFF !important;
    border-color: #E8E6E1 !important;
    border-radius: 8px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D1CEC7; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#1A1916", size=12),
    margin=dict(l=0, r=0, t=36, b=0),
    colorway=["#3B6CF6","#F6963B","#3BBCA0","#E05252","#9B5CF6","#F6C53B","#5CAF3B"],
)
GRID_STYLE = dict(
    xaxis=dict(gridcolor="#F0EEE9", zeroline=False, linecolor="#E8E6E1"),
    yaxis=dict(gridcolor="#F0EEE9", zeroline=False, linecolor="#E8E6E1"),
)

def safe(d, *keys, default="N/A"):
    for k in keys:
        if not isinstance(d, dict): return default
        d = d.get(k, default)
        if d is None: return default
    return d

def risk_icon(r):
    return {"High": "●", "Medium": "●", "Low": "●"}.get(r, "○")

def risk_badge_html(r):
    cls = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}.get(r, "")
    return f'<span class="badge {cls}">{r}</span>'

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
    <div style="padding: 8px 0 20px;">
        <div style="font-size:1.1rem;font-weight:600;color:#1A1916;letter-spacing:-0.01em;">◎ ESG · SCM</div>
        <div style="font-size:0.75rem;color:#9B9890;margin-top:2px;">Indonesia Consumer Goods</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Data Sources</div>', unsafe_allow_html=True)
    json_file  = st.file_uploader("n8n JSON output",  type="json",        label_visibility="collapsed", help="Post-processor output from n8n")
    excel_file = st.file_uploader("Excel data file",  type=["xlsx","xls"], label_visibility="collapsed", help="ESG-SCM spreadsheet")

    col_j, col_e = st.columns(2)
    col_j.caption("🟢 JSON" if json_file  else "⚪ JSON")
    col_e.caption("🟢 Excel" if excel_file else "⚪ Excel")

    st.markdown('<div class="section-label" style="margin-top:24px;">Navigation</div>', unsafe_allow_html=True)
    page = st.radio("", [
        "Overview",
        "Correlation Heatmap",
        "Company Comparison",
        "What-If Simulator",
        "Risk Alert Panel",
        "AI Recommendations",
        "Trend Analysis",
    ], label_visibility="collapsed")

# ── Load data ─────────────────────────────────────────────────────────────────
companies, summary, df_raw = [], {}, None

if json_file:
    raw = json.load(json_file)
    if isinstance(raw, list): raw = raw[0]
    companies = raw.get("companies", [])
    summary   = raw.get("processing_summary", {})

if excel_file:
    df_raw = pd.read_excel(excel_file)
    df_raw.columns = [c.strip().upper().replace(" ", "_") for c in df_raw.columns]

# ── No data splash ─────────────────────────────────────────────────────────────
if not companies and df_raw is None:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:70vh;text-align:center;">
        <div style="font-size:3rem;margin-bottom:16px;">◎</div>
        <div style="font-size:1.5rem;font-weight:600;color:#1A1916;letter-spacing:-0.02em;margin-bottom:8px;">ESG · SCM Intelligence</div>
        <div style="font-size:0.9rem;color:#9B9890;max-width:360px;line-height:1.6;">
            Upload your <strong>n8n JSON</strong> for AI analysis, risk data and recommendations.<br>
            Upload your <strong>Excel file</strong> for correlations, simulations and trends.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "Overview":
    st.markdown('<div class="page-title">Overview</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">Indonesia Food & Tobacco · {len(companies)} companies analysed</div>', unsafe_allow_html=True)

    if companies:
        risk_counts = pd.Series([safe(c, "risk_assessment", "overall_risk") for c in companies]).value_counts()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total companies", len(companies))
        c2.metric("High risk",   risk_counts.get("High",   0))
        c3.metric("Medium risk", risk_counts.get("Medium", 0))
        c4.metric("Low risk",    risk_counts.get("Low",    0))

        # Risk donut
        st.markdown("---")
        col_chart, col_table = st.columns([1, 2])

        with col_chart:
            st.markdown('<div class="section-label">Risk Distribution</div>', unsafe_allow_html=True)
            rd = pd.DataFrame({
                "Risk": ["High", "Medium", "Low"],
                "Count": [risk_counts.get("High", 0), risk_counts.get("Medium", 0), risk_counts.get("Low", 0)]
            })
            fig = go.Figure(go.Pie(
                labels=rd["Risk"], values=rd["Count"],
                hole=0.62,
                marker_colors=["#FC8181", "#F6AD55", "#68D391"],
                textinfo="label+value",
                textfont_size=12,
                insidetextorientation="radial"
            ))
            fig.update_layout(**CHART_LAYOUT, height=240, showlegend=False,
                              margin=dict(l=0,r=0,t=8,b=0))
            st.plotly_chart(fig, use_container_width=True)

        with col_table:
            st.markdown('<div class="section-label">Company Summary</div>', unsafe_allow_html=True)
            rows = []
            for c in companies:
                rows.append({
                    "Company":       safe(c, "analysis_metadata", "company"),
                    "Risk Level":    safe(c, "risk_assessment",   "overall_risk"),
                    "Confidence":    safe(c, "analysis_metadata", "confidence_level"),
                    "ESG Strength":  safe(c, "esg_performance",   "strongest_dimension"),
                    "ESG Weakness":  safe(c, "esg_performance",   "weakest_dimension"),
                })
            ov_df = pd.DataFrame(rows)

            def colour_risk(val):
                m = {
                    "High":   "background-color:#FEF2F2;color:#C53030",
                    "Medium": "background-color:#FFFBEB;color:#B45309",
                    "Low":    "background-color:#F0FDF4;color:#166534",
                }
                return m.get(val, "")

            st.dataframe(
                ov_df.style.map(colour_risk, subset=["Risk Level"]),
                use_container_width=True, height=240
            )

        # Executive summaries
        st.markdown("---")
        st.markdown('<div class="section-label">Executive Summaries</div>', unsafe_allow_html=True)
        for c in companies:
            name = safe(c, "analysis_metadata", "company")
            risk = safe(c, "risk_assessment",   "overall_risk")
            label_color = {"High": "#C53030", "Medium": "#B45309", "Low": "#166534"}.get(risk, "#9B9890")
            with st.expander(f"**{name}** · {risk} Risk"):
                st.write(safe(c, "executive_summary"))
    else:
        st.info("Upload your n8n JSON to see the company overview.")

# ══════════════════════════════════════════════════════════════════════════════
# CORRELATION HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Correlation Heatmap":
    st.markdown('<div class="page-title">ESG–SCM Correlation Heatmap</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Pearson correlations between ESG dimensions and supply chain metrics</div>', unsafe_allow_html=True)

    if df_raw is None:
        st.warning("Upload your Excel file to view correlation data.")
        st.stop()

    ESG_OPTIONS = [c for c in ["ESG_SCORE","EMISSIONS_SCORE","ENVIRONMENTAL_INNOVATION_SCORE",
                                "RESOURCE_USE_SCORE","COMMUNITY_SCORE","HUMAN_RIGHTS_SCORE",
                                "PRODUCT_RESPONSIBILITY_SCORE","WORKFORCE_SCORE",
                                "CSR_STRATEGY_SCORE","MANAGEMENT_SCORE","SHAREHOLDERS_SCORE"]
                   if c in df_raw.columns]
    SCM_OPTIONS = [c for c in ["CASH_CONVERSION_CYCLE","AVERAGE_INVENTORY_DAYS",
                                "INVENTORY_TURNOVER","DAYS_SALES_OUTSTANDING",
                                "DAYS_PAYABLES_OUTSTANDING","ROA_TOTAL_ASSETS",
                                "PROFIT_MARGIN","EBITDA_MARGIN"]
                   if c in df_raw.columns]

    with st.container():
        col1, col2 = st.columns(2)
        sel_esg = col1.multiselect("ESG dimensions", ESG_OPTIONS, default=ESG_OPTIONS[:5])
        sel_scm = col2.multiselect("SCM / Financial metrics", SCM_OPTIONS, default=SCM_OPTIONS[:4])

    if sel_esg and sel_scm:
        if "YEAR" in df_raw.columns:
            years = sorted(df_raw["YEAR"].dropna().unique().astype(int).tolist())
            sel_years = st.select_slider("Year range", options=years, value=(years[0], years[-1]))
            df_f = df_raw[df_raw["YEAR"].between(sel_years[0], sel_years[1])].copy()
        else:
            df_f = df_raw.copy()

        for c in sel_esg + sel_scm:
            df_f[c] = pd.to_numeric(df_f[c], errors="coerce")

        cm = corr_matrix(df_f, sel_esg, sel_scm)

        fig = px.imshow(
            cm, text_auto=".2f",
            color_continuous_scale=[[0,"#FC8181"],[0.5,"#FFFBEB"],[1,"#68D391"]],
            zmin=-1, zmax=1, aspect="auto",
        )
        fig.update_layout(
            **CHART_LAYOUT, height=400,
            coloraxis_colorbar=dict(title="r", tickfont=dict(size=11)),
            title=None,
        )
        fig.update_traces(textfont_size=11)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown('<div class="section-label">Strongest Correlations</div>', unsafe_allow_html=True)

        def interp(r):
            if abs(r) < 0.2: return "Negligible"
            if abs(r) < 0.4: return "Weak"
            if abs(r) < 0.6: return "Moderate"
            if abs(r) < 0.8: return "Strong"
            return "Very strong"

        pairs = []
        for e in sel_esg:
            for s in sel_scm:
                v = cm.loc[e, s]
                if pd.notna(v):
                    pairs.append({"ESG Dimension": e, "SCM / Finance": s, "r": round(v, 3),
                                  "|r|": abs(v), "Strength": interp(v),
                                  "Direction": "↑ Positive" if v > 0 else "↓ Negative"})
        pdf = pd.DataFrame(pairs).sort_values("|r|", ascending=False).head(10)
        st.dataframe(pdf[["ESG Dimension","SCM / Finance","r","Strength","Direction"]],
                     use_container_width=True)
    else:
        st.info("Select at least one ESG dimension and one SCM metric.")

# ══════════════════════════════════════════════════════════════════════════════
# COMPANY COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Company Comparison":
    st.markdown('<div class="page-title">Company Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Side-by-side analysis across ESG and supply chain metrics</div>', unsafe_allow_html=True)

    if df_raw is None and not companies:
        st.warning("Upload Excel and/or n8n JSON to compare companies.")
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

            radar_cols = [c for c in ["ESG_SCORE","EMISSIONS_SCORE","COMMUNITY_SCORE",
                                       "MANAGEMENT_SCORE","INVENTORY_TURNOVER","ROA_TOTAL_ASSETS"]
                          if c in df_raw.columns]

            col_radar, col_bar = st.columns(2)

            if radar_cols:
                with col_radar:
                    st.markdown('<div class="section-label">Multi-Dimension Radar</div>', unsafe_allow_html=True)
                    fig = go.Figure()
                    colors = ["#3B6CF6","#F6963B","#3BBCA0","#E05252","#9B5CF6","#F6C53B"]
                    for i, (_, row) in enumerate(df_sel.iterrows()):
                        vals = [pd.to_numeric(row.get(c, 0), errors="coerce") or 0 for c in radar_cols]
                        maxv = [df_raw[c].dropna().apply(pd.to_numeric, errors="coerce").max() for c in radar_cols]
                        norm = [v/m*100 if m and m > 0 else 0 for v, m in zip(vals, maxv)]
                        fig.add_trace(go.Scatterpolar(
                            r=norm+[norm[0]], theta=radar_cols+[radar_cols[0]],
                            fill="toself", name=str(row["COMPANY"]),
                            line_color=colors[i % len(colors)], opacity=0.75
                        ))
                    fig.update_layout(
                        **CHART_LAYOUT, height=340,
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0,100],
                                            gridcolor="#E8E6E1", tickfont_size=9,
                                            tickcolor="#9B9890"),
                            angularaxis=dict(gridcolor="#E8E6E1", tickfont_size=10),
                            bgcolor="rgba(0,0,0,0)"
                        ),
                        legend=dict(orientation="h", y=-0.15, font_size=11),
                        margin=dict(l=20, r=20, t=20, b=40)
                    )
                    st.plotly_chart(fig, use_container_width=True)

            num_cols = [c for c in ["ESG_SCORE","CASH_CONVERSION_CYCLE","INVENTORY_TURNOVER",
                                     "ROA_TOTAL_ASSETS","PROFIT_MARGIN","AVERAGE_INVENTORY_DAYS"]
                        if c in df_raw.columns]

            with col_bar:
                st.markdown('<div class="section-label">Single Metric Comparison</div>', unsafe_allow_html=True)
                metric = st.selectbox("Metric", num_cols, label_visibility="collapsed")
                df_bar = df_sel[["COMPANY", metric]].copy()
                df_bar[metric] = pd.to_numeric(df_bar[metric], errors="coerce")
                fig2 = px.bar(df_bar, x="COMPANY", y=metric, color="COMPANY",
                              color_discrete_sequence=["#3B6CF6","#F6963B","#3BBCA0","#E05252","#9B5CF6"])
                fig2.update_layout(**CHART_LAYOUT, **GRID_STYLE, height=314,
                                   showlegend=False, margin=dict(l=0,r=0,t=20,b=0))
                fig2.update_traces(marker_line_width=0)
                st.plotly_chart(fig2, use_container_width=True)

            # Benchmark table
            st.markdown("---")
            st.markdown('<div class="section-label">Industry Benchmarks</div>', unsafe_allow_html=True)
            BENCHMARKS = {
                "CASH_CONVERSION_CYCLE":  (45, 60, "days"),
                "AVERAGE_INVENTORY_DAYS": (55, 70, "days"),
                "ESG_SCORE":              (45, 60, "pts"),
                "ROA_TOTAL_ASSETS":       (0.05, 0.08, "%"),
                "PROFIT_MARGIN":          (0.08, 0.12, "%"),
            }
            bm_rows = []
            for _, row in df_sel.iterrows():
                for col, (lo, hi, unit) in BENCHMARKS.items():
                    if col not in df_raw.columns: continue
                    val = pd.to_numeric(row.get(col), errors="coerce")
                    if pd.isna(val): continue
                    status = "✓ In range" if lo <= val <= hi else ("↑ Above" if val > hi else "↓ Below")
                    bm_rows.append({"Company": row["COMPANY"], "Metric": col,
                                    "Value": round(val, 3), "Benchmark": f"{lo}–{hi} {unit}", "Status": status})
            if bm_rows:
                st.dataframe(pd.DataFrame(bm_rows), use_container_width=True)
    else:
        st.info("Upload your Excel file to use the comparison tool.")

# ══════════════════════════════════════════════════════════════════════════════
# WHAT-IF SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "What-If Simulator":
    st.markdown('<div class="page-title">What-If Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Model the projected impact of ESG improvements on supply chain performance</div>', unsafe_allow_html=True)

    if df_raw is None:
        st.warning("Upload your Excel file to use the simulator.")
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

    col1, col2, col3 = st.columns([2, 2, 1])
    esg_choice    = col1.selectbox("ESG dimension", list(ESG_DIMS.keys()))
    target_choice = col2.selectbox("Target metric",  list(TARGETS.keys()))
    improvement   = col3.number_input("ESG improvement (%)", min_value=1, max_value=50, value=10)

    esg_cols = [c for c in ESG_DIMS[esg_choice] if c in df_raw.columns]
    tgt_col  = TARGETS[target_choice]

    if not esg_cols or tgt_col not in df_raw.columns:
        st.warning("Some required columns are missing from your Excel file.")
        st.stop()

    df_sim = df_raw.copy()
    df_sim["_esg"] = df_sim[esg_cols].mean(axis=1)
    df_sim = df_sim[["COMPANY", "YEAR", "_esg", tgt_col]].dropna() if "YEAR" in df_sim.columns \
             else df_sim[["COMPANY", "_esg", tgt_col]].dropna()

    r = df_sim["_esg"].corr(df_sim[tgt_col])

    if "YEAR" in df_sim.columns:
        df_latest = df_sim.sort_values("YEAR").groupby("COMPANY").last().reset_index()
    else:
        df_latest = df_sim.copy()

    df_latest["ESG_Current"]   = df_latest["_esg"]
    df_latest["ESG_Projected"] = df_latest["_esg"] * (1 + improvement / 100)

    x, y = df_sim["_esg"].values, df_sim[tgt_col].values
    slope = np.polyfit(x, y, 1)[0] if len(x) > 2 else r

    df_latest[f"{target_choice}_Current"]   = df_latest[tgt_col]
    df_latest[f"{target_choice}_Projected"] = df_latest[tgt_col] + slope * (
        df_latest["ESG_Projected"] - df_latest["ESG_Current"])

    # KPIs
    st.markdown("---")
    ka, kb, kc = st.columns(3)
    ka.metric("Correlation (r)", f"{r:.3f}")
    kb.metric("Regression slope",  f"{slope:.4f}")
    kc.metric("ESG improvement",  f"+{improvement}%")

    if abs(r) < 0.2:
        st.info("Correlation is weak (r < 0.2) — projection is indicative only.")
    elif r > 0:
        st.success(f"Positive correlation: improving {esg_choice} tends to increase {target_choice}.")
    else:
        st.success(f"Negative correlation: improving {esg_choice} tends to decrease {target_choice} (beneficial for CCC/DIO).")

    # Chart
    fig = go.Figure()
    colors = ["#3B6CF6","#F6963B","#3BBCA0","#E05252","#9B5CF6"]
    for i, (_, row) in enumerate(df_latest.iterrows()):
        c = colors[i % len(colors)]
        curr = row[f"{target_choice}_Current"]
        proj = row[f"{target_choice}_Projected"]
        fig.add_trace(go.Bar(
            name=str(row["COMPANY"]),
            x=[f"Current", f"Projected +{improvement}%"],
            y=[curr, proj],
            text=[f"{curr:.2f}", f"{proj:.2f}"],
            textposition="outside",
            marker_color=[c, c],
            marker_opacity=[0.45, 1.0],
            marker_line_width=0,
        ))
    fig.update_layout(**CHART_LAYOUT, **GRID_STYLE,
                      barmode="group", height=420,
                      yaxis_title=target_choice,
                      legend=dict(orientation="h", y=-0.15, font_size=11),
                      margin=dict(l=0, r=0, t=20, b=60))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-label">Company-Level Projections</div>', unsafe_allow_html=True)
    tbl = df_latest[["COMPANY", f"{target_choice}_Current", f"{target_choice}_Projected"]].copy()
    tbl["Change"] = tbl[f"{target_choice}_Projected"] - tbl[f"{target_choice}_Current"]
    tbl["Change %"] = (tbl["Change"] / tbl[f"{target_choice}_Current"].abs() * 100).round(2)
    tbl = tbl.rename(columns={f"{target_choice}_Current": "Current", f"{target_choice}_Projected": "Projected"})
    st.dataframe(tbl.round(3), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# RISK ALERT PANEL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Risk Alert Panel":
    st.markdown('<div class="page-title">Risk Alert Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Operational, reputational and financial risk breakdown</div>', unsafe_allow_html=True)

    if not companies:
        st.warning("Upload your n8n JSON to see risk alerts.")
        st.stop()

    CONTROVERSIES = {
        "AALI.JK": "Deforestation & palm oil sustainability concerns (RSPO compliance issues)",
        "GGRM.JK": "Tobacco health impact — increasing regulatory pressure in Indonesia",
        "HMSP.JK": "Tobacco sector — ESG exclusion risk from institutional investors",
        "UNVR.JK": "Negative ROA — financial distress signals despite strong ESG score",
        "CPIN.JK": "Poultry supply chain — animal welfare & antibiotic use concerns",
    }

    high   = [c for c in companies if safe(c, "risk_assessment", "overall_risk") == "High"]
    medium = [c for c in companies if safe(c, "risk_assessment", "overall_risk") == "Medium"]
    low    = [c for c in companies if safe(c, "risk_assessment", "overall_risk") == "Low"]

    c1, c2, c3 = st.columns(3)
    c1.metric("High risk companies",   len(high))
    c2.metric("Medium risk companies", len(medium))
    c3.metric("Low risk companies",    len(low))

    # Risk distribution bar
    st.markdown("---")
    col_chart, col_flags = st.columns([1, 1])

    with col_chart:
        st.markdown('<div class="section-label">Risk Distribution</div>', unsafe_allow_html=True)
        rd = pd.DataFrame({
            "Level": ["High", "Medium", "Low"],
            "Count": [len(high), len(medium), len(low)]
        })
        fig = px.bar(rd, x="Level", y="Count", color="Level",
                     color_discrete_map={"High": "#FC8181", "Medium": "#F6AD55", "Low": "#68D391"},
                     text="Count")
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(**CHART_LAYOUT, **GRID_STYLE, showlegend=False, height=260,
                          margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_flags:
        st.markdown('<div class="section-label">ESG Controversy Flags</div>', unsafe_allow_html=True)
        flagged = [(c, CONTROVERSIES[safe(c, "analysis_metadata", "company")])
                   for c in companies
                   if safe(c, "analysis_metadata", "company") in CONTROVERSIES]
        if flagged:
            for c, note in flagged:
                name = safe(c, "analysis_metadata", "company")
                risk = safe(c, "risk_assessment",   "overall_risk")
                strip_cls = "alert-high-strip" if risk == "High" else "alert-med-strip"
                st.markdown(f"""
                <div class="alert-strip {strip_cls}">
                    <strong style="font-size:0.85rem">{name}</strong>
                    <span style="font-size:0.75rem;color:#9B9890;margin-left:6px">{risk}</span><br>
                    <span style="font-size:0.8rem;color:#6B6860">{note}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.success("No controversy flags for current companies.")

    st.markdown("---")
    st.markdown('<div class="section-label">Company Risk Detail</div>', unsafe_allow_html=True)
    risk_filter = st.multiselect("Filter by risk level", ["High","Medium","Low"], default=["High","Medium"])

    for c in companies:
        name    = safe(c, "analysis_metadata", "company")
        overall = safe(c, "risk_assessment",   "overall_risk")
        if overall not in risk_filter: continue

        op_r  = c.get("risk_assessment", {}).get("operational_risks",  []) or []
        rep_r = c.get("risk_assessment", {}).get("reputational_risks", []) or []
        fin_r = c.get("risk_assessment", {}).get("financial_risks",    []) or []

        with st.expander(f"**{name}** · {overall} Risk"):
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                st.markdown("**Operational**")
                for r in (op_r if isinstance(op_r, list) else [op_r]):
                    st.markdown(f"<span style='font-size:0.85rem'>· {r}</span>", unsafe_allow_html=True)
            with cc2:
                st.markdown("**Reputational**")
                for r in (rep_r if isinstance(rep_r, list) else [rep_r]):
                    st.markdown(f"<span style='font-size:0.85rem'>· {r}</span>", unsafe_allow_html=True)
            with cc3:
                st.markdown("**Financial**")
                for r in (fin_r if isinstance(fin_r, list) else [fin_r]):
                    st.markdown(f"<span style='font-size:0.85rem'>· {r}</span>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# AI RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "AI Recommendations":
    st.markdown('<div class="page-title">AI Recommendations</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Actionable insights generated by your n8n AI agent</div>', unsafe_allow_html=True)

    if not companies:
        st.warning("Upload your n8n JSON to see AI recommendations.")
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
    pri_f = col1.multiselect("Priority", ["High","Medium","Low"], default=["High","Medium","Low"])
    cat_f = col2.multiselect("Category", rec_df["Category"].unique().tolist(), default=rec_df["Category"].unique().tolist())
    co_f  = col3.multiselect("Company",  rec_df["Company"].unique().tolist(),  default=rec_df["Company"].unique().tolist())

    filtered = rec_df[
        rec_df["Priority"].isin(pri_f) &
        rec_df["Category"].isin(cat_f) &
        rec_df["Company"].isin(co_f)
    ]

    st.caption(f"{len(filtered)} recommendations")

    def colour_priority(val):
        m = {
            "High":   "background-color:#FEF2F2;color:#C53030",
            "Medium": "background-color:#FFFBEB;color:#B45309",
            "Low":    "background-color:#F0FDF4;color:#166534",
        }
        return m.get(val, "")

    st.dataframe(
        filtered.style.map(colour_priority, subset=["Priority"]),
        use_container_width=True, height=420
    )

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-label">By Priority</div>', unsafe_allow_html=True)
        pc = filtered["Priority"].value_counts().reset_index()
        fig = px.pie(pc, names="Priority", values="count", hole=0.55,
                     color="Priority",
                     color_discrete_map={"High":"#FC8181","Medium":"#F6AD55","Low":"#68D391"})
        fig.update_layout(**CHART_LAYOUT, height=280, showlegend=True,
                          legend=dict(orientation="h", y=-0.1, font_size=11),
                          margin=dict(l=0,r=0,t=10,b=30))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-label">By Category</div>', unsafe_allow_html=True)
        cc = filtered["Category"].value_counts().reset_index()
        fig2 = px.bar(cc, x="Category", y="count", color="Category",
                      color_discrete_sequence=["#3B6CF6","#F6963B","#3BBCA0","#E05252","#9B5CF6","#F6C53B"])
        fig2.update_traces(marker_line_width=0)
        fig2.update_layout(**CHART_LAYOUT, **GRID_STYLE, showlegend=False, height=280,
                           margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-label">Priority by Company</div>', unsafe_allow_html=True)
    pivot = filtered.groupby(["Company","Priority"]).size().reset_index(name="Count")
    fig3 = px.bar(pivot, x="Company", y="Count", color="Priority", barmode="stack",
                  color_discrete_map={"High":"#FC8181","Medium":"#F6AD55","Low":"#68D391"})
    fig3.update_traces(marker_line_width=0)
    fig3.update_layout(**CHART_LAYOUT, **GRID_STYLE, height=340,
                       xaxis_tickangle=-30, legend=dict(orientation="h", y=-0.2, font_size=11),
                       margin=dict(l=0,r=0,t=10,b=60))
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TREND ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Trend Analysis":
    st.markdown('<div class="page-title">Trend Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Year-over-year ESG and supply chain performance trajectories</div>', unsafe_allow_html=True)

    if df_raw is None:
        st.warning("Upload your Excel file to see trend analysis.")
        st.stop()

    if "YEAR" not in df_raw.columns or "COMPANY" not in df_raw.columns:
        st.error("Excel file must have YEAR and COMPANY columns.")
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
        df_trend = df_raw[df_raw["COMPANY"].isin(sel_companies)][["COMPANY","YEAR",sel_metric]].copy()
        df_trend["YEAR"] = pd.to_numeric(df_trend["YEAR"], errors="coerce")
        df_trend[sel_metric] = pd.to_numeric(df_trend[sel_metric], errors="coerce")
        df_trend = df_trend.dropna(subset=["COMPANY","YEAR"]).sort_values(["COMPANY","YEAR"])

        fig = px.line(df_trend, x="YEAR", y=sel_metric, color="COMPANY", markers=True,
                      color_discrete_sequence=["#3B6CF6","#F6963B","#3BBCA0","#E05252","#9B5CF6"])
        fig.update_traces(line_width=2, marker_size=7)
        fig.update_layout(**CHART_LAYOUT, **GRID_STYLE, height=380,
                          xaxis=dict(dtick=1, gridcolor="#F0EEE9"),
                          legend=dict(orientation="h", y=-0.15, font_size=11),
                          margin=dict(l=0,r=0,t=10,b=60))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown('<div class="section-label">Year-over-Year Change</div>', unsafe_allow_html=True)
        yoy_rows = []
        for comp in sel_companies:
            sub = df_trend[df_trend["COMPANY"] == comp].sort_values("YEAR")
            sub = sub.copy()
            sub["YoY Change"] = sub[sel_metric].diff()
            sub["YoY %"] = (sub[sel_metric].pct_change() * 100).round(2)
            yoy_rows.append(sub)
        if yoy_rows:
            yoy_df = pd.concat(yoy_rows).round(3)
            st.dataframe(yoy_df, use_container_width=True, height=300)

        st.markdown('<div class="section-label">ESG vs SCM Correlation over Time</div>', unsafe_allow_html=True)
        ESG_C = [c for c in ["ESG_SCORE","EMISSIONS_SCORE"] if c in df_raw.columns]
        SCM_C = [c for c in ["CASH_CONVERSION_CYCLE","INVENTORY_TURNOVER"] if c in df_raw.columns]

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
                                "r": round(vals[e].corr(vals[s]), 3)
                            })
            if corr_by_year:
                cy_df = pd.DataFrame(corr_by_year)
                fig2 = px.line(cy_df, x="Year", y="r", color="Pair", markers=True,
                               color_discrete_sequence=["#3B6CF6","#F6963B","#3BBCA0","#E05252"])
                fig2.add_hline(y=0, line_dash="dot", line_color="#D1CEC7", opacity=0.8)
                fig2.update_traces(line_width=2, marker_size=6)
                fig2.update_layout(**CHART_LAYOUT, **GRID_STYLE, height=340,
                                   yaxis=dict(range=[-1,1], gridcolor="#F0EEE9"),
                                   legend=dict(orientation="h", y=-0.2, font_size=11),
                                   margin=dict(l=0,r=0,t=10,b=60))
                st.plotly_chart(fig2, use_container_width=True)
