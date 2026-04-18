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
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    body, [data-testid="stAppViewContainer"] {
        background:#07101d;
        color:#c8d6e8;
        font-family: 'Segoe UI', sans-serif;
    }

    [data-testid="stSidebar"]{
        background:#050c17;
        border-right:1px solid #132033;
    }

    .metric-card{
        background:#0c1828;
        border-radius:12px;
        padding:16px 20px;
        border-left:4px solid #3b82f6;
        margin-bottom:8px
    }

    .alert-high{
        background:#2a0a0a;
        border-left:4px solid #ef4444;
        padding:10px 14px;
        border-radius:6px;
        margin:4px 0
    }

    .alert-med{
        background:#2a1a03;
        border-left:4px solid #f59e0b;
        padding:10px 14px;
        border-radius:6px;
        margin:4px 0
    }

    .section-hdr{
        font-size:1rem;
        font-weight:600;
        color:#93c5fd;
        margin:12px 0 4px;
        border-bottom:1px solid #1f2a3a;
        padding-bottom:4px
    }

    .stTabs [data-baseweb="tab"]{
        font-weight:500;
        color:#9ca3af;
    }

    .stTabs [aria-selected="true"]{
        color:#60a5fa !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def safe(d, *keys, default="N/A"):
    for k in keys:
        if not isinstance(d, dict): return default
        d = d.get(k, default)
        if d is None: return default
    return d

def risk_emoji(r):
    return {"High":"🔴","Medium":"🟡","Low":"🟢"}.get(r,"⚪")

def corr_matrix(df, esg_cols, scm_cols):
    rows = []
    for e in esg_cols:
        row = []
        for s in scm_cols:
            sub = df[[e,s]].dropna()
            row.append(round(sub[e].corr(sub[s]),3) if len(sub)>2 else None)
        rows.append(row)
    return pd.DataFrame(rows, index=esg_cols, columns=scm_cols)

# ── Sidebar: file uploads ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 ESG-SCM Dashboard")
    st.caption("Indonesia Consumer Goods Company")
    st.divider()

    st.markdown("### Upload Data")
    json_file  = st.file_uploader("n8n JSON output",  type="json", help="Post-processor output from n8n")
    excel_file = st.file_uploader("Excel data file",  type=["xlsx","xls"], help="Your original ESG-SCM spreadsheet")

    st.divider()
    page = st.radio("Navigation", [
        "🏠 Overview",
        "🌡️ Correlation Heatmap",
        "🔍 Company Comparison",
        "🎛️ What-If Simulator",
        "⚠️ Risk Alert Panel",
        "💡 AI Recommendations",
        "📈 Trend Analysis",
    ])

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
    df_raw.columns = [c.strip().upper().replace(" ","_") for c in df_raw.columns]

# ── No data ───────────────────────────────────────────────────────────────────
if not companies and df_raw is None:
    st.title("ESG-SCM Interactive Dashboard")
    col1, col2 = st.columns(2)
    col1.info("📁 Upload your **n8n JSON output** for AI analysis, recommendations and risk data.")
    col2.info("📊 Upload your **Excel file** for correlation heatmap, what-if simulator and trend analysis.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("Overview")
    st.caption(f"Indonesia Food & Tobacco · {len(companies)} companies analysed")

    if companies:
        risk_counts = pd.Series([safe(c,"risk_assessment","overall_risk") for c in companies]).value_counts()
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Companies",    len(companies))
        c2.metric("🔴 High Risk",  risk_counts.get("High",0))
        c3.metric("🟡 Medium Risk",risk_counts.get("Medium",0))
        c4.metric("🟢 Low Risk",   risk_counts.get("Low",0))
        st.divider()

        # Overview table
        rows = []
        for c in companies:
            rows.append({
                "Company":       safe(c,"analysis_metadata","company"),
                "Risk":          safe(c,"risk_assessment","overall_risk"),
                "Confidence":    safe(c,"analysis_metadata","confidence_level"),
                "ESG Strongest": safe(c,"esg_performance","strongest_dimension"),
                "ESG Weakest":   safe(c,"esg_performance","weakest_dimension"),
                "Quality":       str(safe(c,"_quality_score","default",100))+"%",
            })
        ov_df = pd.DataFrame(rows)

        def colour_risk(val):
            m = {"High":"background-color:#450a0a;color:#fca5a5",
                 "Medium":"background-color:#451a03;color:#fcd34d",
                 "Low":"background-color:#052e16;color:#6ee7b7"}
            return m.get(val,"")

        st.dataframe(ov_df.style.map(colour_risk, subset=["Risk"]),
                     use_container_width=True, height=450)

        # Exec summaries
        st.divider()
        st.subheader("Executive Summaries")
        for c in companies:
            name = safe(c,"analysis_metadata","company")
            risk = safe(c,"risk_assessment","overall_risk")
            with st.expander(f"{risk_emoji(risk)} **{name}** — {risk} Risk"):
                st.write(safe(c,"executive_summary"))
    else:
        st.info("Upload your n8n JSON to see company overview.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CORRELATION HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🌡️ Correlation Heatmap":
    st.title("ESG–SCM Correlation Heatmap")

    if df_raw is None:
        st.warning("Upload your Excel file to see the correlation heatmap.")
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

    col1, col2 = st.columns(2)
    sel_esg = col1.multiselect("ESG dimensions", ESG_OPTIONS, default=ESG_OPTIONS[:5])
    sel_scm = col2.multiselect("SCM / Financial metrics", SCM_OPTIONS, default=SCM_OPTIONS[:4])

    if sel_esg and sel_scm:
        # Year filter
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
            color_continuous_scale="RdYlGn",
            zmin=-1, zmax=1,
            aspect="auto",
            title="Pearson Correlation: ESG Dimensions vs SCM/Financial Metrics"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=420,
            coloraxis_colorbar=dict(title="r")
        )
        st.plotly_chart(fig, use_container_width=True)

        # Interpretation
        st.subheader("Strongest Correlations")
        pairs = []
        for e in sel_esg:
            for s in sel_scm:
                v = cm.loc[e,s]
                if pd.notna(v):
                    pairs.append({"ESG":e,"SCM/Finance":s,"r":v,"|r|":abs(v)})
        pairs_df = pd.DataFrame(pairs).sort_values("|r|",ascending=False).head(8)

        def interp(r):
            if abs(r) < 0.2:  return "Negligible"
            if abs(r) < 0.4:  return "Weak"
            if abs(r) < 0.6:  return "Moderate"
            if abs(r) < 0.8:  return "Strong"
            return "Very strong"

        pairs_df["Strength"] = pairs_df["r"].apply(interp)
        pairs_df["Direction"] = pairs_df["r"].apply(lambda x: "Positive ↑" if x>0 else "Negative ↓")
        st.dataframe(pairs_df[["ESG","SCM/Finance","r","Strength","Direction"]],
                     use_container_width=True)
    else:
        st.info("Select at least one ESG dimension and one SCM metric.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: COMPANY COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Company Comparison":
    st.title("Company Comparison Tool")

    if df_raw is None and not companies:
        st.warning("Upload Excel and/or n8n JSON to compare companies.")
        st.stop()

    if df_raw is not None and "COMPANY" in df_raw.columns:
        company_list = sorted(df_raw["COMPANY"].dropna().unique().tolist())
        sel = st.multiselect("Select companies to compare", company_list,
                              default=company_list[:4])

        if sel:
            # Latest year per company
            if "YEAR" in df_raw.columns:
                df_latest = df_raw.sort_values("YEAR").groupby("COMPANY").last().reset_index()
            else:
                df_latest = df_raw.copy()
            df_sel = df_latest[df_latest["COMPANY"].isin(sel)]

            # Radar chart
            radar_cols = [c for c in ["ESG_SCORE","EMISSIONS_SCORE","COMMUNITY_SCORE",
                                       "MANAGEMENT_SCORE","INVENTORY_TURNOVER","ROA_TOTAL_ASSETS"]
                          if c in df_raw.columns]

            if radar_cols:
                st.subheader("Radar Chart — Multi-Dimension Comparison")
                fig = go.Figure()
                for _, row in df_sel.iterrows():
                    vals = [pd.to_numeric(row.get(c,0), errors="coerce") or 0 for c in radar_cols]
                    # Normalise 0-100
                    maxv = [df_raw[c].dropna().apply(pd.to_numeric,errors="coerce").max() for c in radar_cols]
                    norm = [v/m*100 if m and m>0 else 0 for v,m in zip(vals,maxv)]
                    fig.add_trace(go.Scatterpolar(
                        r=norm+[norm[0]],
                        theta=radar_cols+[radar_cols[0]],
                        fill="toself",
                        name=str(row["COMPANY"]),
                        opacity=0.7
                    ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="white", height=480,
                    legend=dict(orientation="h", y=-0.15)
                )
                st.plotly_chart(fig, use_container_width=True)

            # Bar comparison
            st.subheader("Side-by-Side Metrics")
            num_cols = [c for c in ["ESG_SCORE","CASH_CONVERSION_CYCLE","INVENTORY_TURNOVER",
                                     "ROA_TOTAL_ASSETS","PROFIT_MARGIN","AVERAGE_INVENTORY_DAYS"]
                        if c in df_raw.columns]
            metric = st.selectbox("Metric to compare", num_cols)
            df_bar = df_sel[["COMPANY",metric]].copy()
            df_bar[metric] = pd.to_numeric(df_bar[metric], errors="coerce")
            fig2 = px.bar(df_bar, x="COMPANY", y=metric, color="COMPANY",
                          title=f"{metric} comparison",
                          color_discrete_sequence=px.colors.qualitative.Vivid)
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                                showlegend=False, height=380)
            st.plotly_chart(fig2, use_container_width=True)

            # Benchmark lines
            st.subheader("Benchmark vs Industry")
            BENCHMARKS = {
                "CASH_CONVERSION_CYCLE": (45,60,"days"),
                "AVERAGE_INVENTORY_DAYS": (55,70,"days"),
                "ESG_SCORE": (45,60,"score"),
                "ROA_TOTAL_ASSETS": (0.05,0.08,"%"),
                "PROFIT_MARGIN": (0.08,0.12,"%"),
            }
            bm_rows = []
            for _, row in df_sel.iterrows():
                for col,(lo,hi,unit) in BENCHMARKS.items():
                    if col not in df_raw.columns: continue
                    val = pd.to_numeric(row.get(col), errors="coerce")
                    if pd.isna(val): continue
                    status = "✅ In range" if lo<=val<=hi else ("🔴 Above" if val>hi else "🟡 Below")
                    bm_rows.append({"Company":row["COMPANY"],"Metric":col,
                                    "Value":round(val,3),"Benchmark":f"{lo}–{hi} {unit}","Status":status})
            if bm_rows:
                st.dataframe(pd.DataFrame(bm_rows), use_container_width=True)
    else:
        st.info("Upload your Excel file to use the comparison tool.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: WHAT-IF SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🎛️ What-If Simulator":
    st.title("What-If Simulator")
    st.caption("Estimate how improving an ESG dimension affects supply chain and financial performance")

    if df_raw is None:
        st.warning("Upload your Excel file to use the simulator.")
        st.stop()

    for c in df_raw.columns:
        df_raw[c] = pd.to_numeric(df_raw[c], errors="coerce") if c not in ["COMPANY"] else df_raw[c]

    ESG_DIMS = {
        "Environmental (avg)": ["EMISSIONS_SCORE","ENVIRONMENTAL_INNOVATION_SCORE","RESOURCE_USE_SCORE"],
        "Social (avg)": ["COMMUNITY_SCORE","HUMAN_RIGHTS_SCORE","PRODUCT_RESPONSIBILITY_SCORE","WORKFORCE_SCORE"],
        "Governance (avg)": ["CSR_STRATEGY_SCORE","MANAGEMENT_SCORE","SHAREHOLDERS_SCORE"],
        "ESG Overall": ["ESG_SCORE"],
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

    # Build ESG column
    esg_cols = [c for c in ESG_DIMS[esg_choice] if c in df_raw.columns]
    tgt_col  = TARGETS[target_choice]

    if not esg_cols or tgt_col not in df_raw.columns:
        st.warning("Some required columns are missing from your Excel file.")
        st.stop()

    df_sim = df_raw.copy()
    df_sim["_esg"] = df_sim[esg_cols].mean(axis=1)
    df_sim = df_sim[["COMPANY","YEAR","_esg",tgt_col]].dropna()

    # Correlation
    r = df_sim["_esg"].corr(df_sim[tgt_col])

    # Current vs projected (latest year)
    if "YEAR" in df_sim.columns:
        df_latest = df_sim.sort_values("YEAR").groupby("COMPANY").last().reset_index()
    else:
        df_latest = df_sim.copy()

    df_latest["ESG Current"]   = df_latest["_esg"]
    df_latest["ESG Projected"] = df_latest["_esg"] * (1 + improvement/100)

    # Simple linear projection using slope
    from numpy.polynomial import polynomial as P
    x = df_sim["_esg"].values
    y = df_sim[tgt_col].values
    if len(x) > 2:
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
    else:
        slope = r

    df_latest[f"{target_choice} Current"]   = df_latest[tgt_col]
    df_latest[f"{target_choice} Projected"] = df_latest[tgt_col] + slope * (df_latest["ESG Projected"] - df_latest["ESG Current"])

    # Show results
    st.divider()
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Correlation (r)", f"{r:.3f}")
    col_b.metric("Regression slope", f"{slope:.4f}")
    col_c.metric("ESG improvement", f"+{improvement}%")

    if abs(r) < 0.2:
        st.info("⚠️ Correlation is weak (r < 0.2) — projection is indicative only.")
    elif r > 0:
        st.success(f"📈 Positive correlation: improving {esg_choice} tends to **increase** {target_choice}")
    else:
        st.success(f"📉 Negative correlation: improving {esg_choice} tends to **decrease** {target_choice} (good for CCC/DIO)")

    # Chart
    fig = go.Figure()
    for _, row in df_latest.iterrows():
        fig.add_trace(go.Bar(
            name=str(row["COMPANY"]),
            x=[f"Current", f"Projected (+{improvement}%)"],
            y=[row[f"{target_choice} Current"], row[f"{target_choice} Projected"]],
            text=[f"{row[f'{target_choice} Current']:.2f}", f"{row[f'{target_choice} Projected']:.2f}"],
            textposition="outside",
        ))
    fig.update_layout(
        barmode="group",
        title=f"Projected impact on {target_choice} if {esg_choice} improves by {improvement}%",
        paper_bgcolor="rgba(0,0,0,0)", font_color="white",
        height=460, xaxis_title="", yaxis_title=target_choice,
        legend=dict(orientation="h", y=-0.2)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Table
    st.subheader("Company-level Projections")
    tbl = df_latest[["COMPANY", f"{target_choice} Current", f"{target_choice} Projected"]].copy()
    tbl["Change"] = tbl[f"{target_choice} Projected"] - tbl[f"{target_choice} Current"]
    tbl["Change %"] = (tbl["Change"] / tbl[f"{target_choice} Current"].abs() * 100).round(2)
    tbl = tbl.round(3)
    st.dataframe(tbl, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: RISK ALERT PANEL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚠️ Risk Alert Panel":
    st.title("Risk Alert Panel")

    if not companies:
        st.warning("Upload your n8n JSON to see risk alerts.")
        st.stop()

    # Known ESG controversies (can be expanded)
    CONTROVERSIES = {
        "AALI.JK":  "⚠️ Deforestation & palm oil sustainability concerns (RSPO compliance issues)",
        "GGRM.JK":  "⚠️ Tobacco health impact — increasing regulatory pressure in Indonesia",
        "HMSP.JK":  "⚠️ Tobacco sector — ESG exclusion risk from institutional investors",
        "UNVR.JK":  "⚠️ Negative ROA — financial distress signals despite strong ESG score",
        "CPIN.JK":  "⚠️ Poultry supply chain — animal welfare & antibiotic use concerns",
    }

    # Summary metrics
    high   = [c for c in companies if safe(c,"risk_assessment","overall_risk")=="High"]
    medium = [c for c in companies if safe(c,"risk_assessment","overall_risk")=="Medium"]
    low    = [c for c in companies if safe(c,"risk_assessment","overall_risk")=="Low"]

    c1,c2,c3 = st.columns(3)
    c1.metric("🔴 High Risk Companies",   len(high))
    c2.metric("🟡 Medium Risk Companies", len(medium))
    c3.metric("🟢 Low Risk Companies",    len(low))

    st.divider()

    # ESG Controversy flags
    st.subheader("🚩 ESG Controversy Flags")
    flagged = [(c, CONTROVERSIES[safe(c,"analysis_metadata","company")])
               for c in companies
               if safe(c,"analysis_metadata","company") in CONTROVERSIES]

    if flagged:
        for c, note in flagged:
            name = safe(c,"analysis_metadata","company")
            risk = safe(c,"risk_assessment","overall_risk")
            st.markdown(f"""
            <div class="alert-high">
                <strong>{risk_emoji(risk)} {name}</strong> — {risk} Risk<br/>
                <small>{note}</small>
            </div>""", unsafe_allow_html=True)
    else:
        st.success("No controversy flags for current companies.")

    st.divider()

    # Risk filter
    st.subheader("Company Risk Breakdown")
    risk_filter = st.multiselect("Filter by risk level",
                                  ["High","Medium","Low"],
                                  default=["High","Medium"])

    for c in companies:
        name    = safe(c,"analysis_metadata","company")
        overall = safe(c,"risk_assessment","overall_risk")
        if overall not in risk_filter: continue

        op_r  = c.get("risk_assessment",{}).get("operational_risks",  []) or []
        rep_r = c.get("risk_assessment",{}).get("reputational_risks", []) or []
        fin_r = c.get("risk_assessment",{}).get("financial_risks",    []) or []

        with st.expander(f"{risk_emoji(overall)} **{name}** — {overall} Risk"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Operational**")
                for r in (op_r if isinstance(op_r,list) else [op_r]):
                    st.write(f"• {r}")
            with col2:
                st.markdown("**Reputational**")
                for r in (rep_r if isinstance(rep_r,list) else [rep_r]):
                    st.write(f"• {r}")
            with col3:
                st.markdown("**Financial**")
                for r in (fin_r if isinstance(fin_r,list) else [fin_r]):
                    st.write(f"• {r}")

    st.divider()

    # Risk distribution chart
    st.subheader("Risk Distribution")
    risk_df = pd.DataFrame([{
        "Company": safe(c,"analysis_metadata","company"),
        "Risk":    safe(c,"risk_assessment","overall_risk"),
        "Confidence": safe(c,"analysis_metadata","confidence_level"),
    } for c in companies])

    fig = px.bar(
        risk_df["Risk"].value_counts().reindex(["High","Medium","Low"],fill_value=0).reset_index(),
        x="Risk", y="count",
        color="Risk",
        color_discrete_map={"High":"#dc2626","Medium":"#f59e0b","Low":"#16a34a"},
        text="count"
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                      showlegend=False, height=320)
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AI RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💡 AI Recommendations":
    st.title("AI-Generated Recommendations")
    st.caption("Powered by your n8n AI Agent")

    if not companies:
        st.warning("Upload your n8n JSON to see AI recommendations.")
        st.stop()

    # Build flat rec list
    rec_rows = []
    for c in companies:
        name = safe(c,"analysis_metadata","company")
        for r in (c.get("recommendations") or []):
            rec_rows.append({
                "Company":  name,
                "Priority": r.get("priority","N/A"),
                "Category": r.get("category","N/A"),
                "Action":   r.get("action","N/A"),
                "Impact":   r.get("expected_impact","N/A"),
                "Timeline": r.get("timeline","N/A"),
            })
    rec_df = pd.DataFrame(rec_rows)

    if rec_df.empty:
        st.info("No recommendations found in JSON.")
        st.stop()

    # Filters
    col1,col2,col3 = st.columns(3)
    pri_f = col1.multiselect("Priority",  ["High","Medium","Low"], default=["High","Medium","Low"])
    cat_f = col2.multiselect("Category",  rec_df["Category"].unique().tolist(), default=rec_df["Category"].unique().tolist())
    co_f  = col3.multiselect("Company",   rec_df["Company"].unique().tolist(),  default=rec_df["Company"].unique().tolist())

    filtered = rec_df[rec_df["Priority"].isin(pri_f) & rec_df["Category"].isin(cat_f) & rec_df["Company"].isin(co_f)]
    st.caption(f"Showing {len(filtered)} recommendations")

    def colour_priority(val):
        m = {"High":"background-color:#450a0a;color:#fca5a5",
             "Medium":"background-color:#451a03;color:#fcd34d",
             "Low":"background-color:#052e16;color:#6ee7b7"}
        return m.get(val,"")

    st.dataframe(filtered.style.map(colour_priority,subset=["Priority"]),
                 use_container_width=True, height=500)

    st.divider()

    # Charts
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("By Priority")
        pc = filtered["Priority"].value_counts().reset_index()
        fig = px.pie(pc, names="Priority", values="count", hole=0.45,
                     color="Priority",
                     color_discrete_map={"High":"#dc2626","Medium":"#f59e0b","Low":"#16a34a"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("By Category")
        cc = filtered["Category"].value_counts().reset_index()
        fig2 = px.bar(cc, x="Category", y="count", color="Category",
                      color_discrete_sequence=px.colors.qualitative.Vivid)
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                           showlegend=False, height=300)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Priority by Company")
    pivot = filtered.groupby(["Company","Priority"]).size().reset_index(name="Count")
    fig3 = px.bar(pivot, x="Company", y="Count", color="Priority", barmode="stack",
                  color_discrete_map={"High":"#dc2626","Medium":"#f59e0b","Low":"#16a34a"})
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                       height=380, xaxis_tickangle=-30)
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: TREND ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Trend Analysis":
    st.title("Yearly Trend Analysis")

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

        fig = px.line(df_trend, x="YEAR", y=sel_metric, color="COMPANY",
                      markers=True, title=f"{sel_metric} over time",
                      color_discrete_sequence=px.colors.qualitative.Vivid)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                          height=420, xaxis=dict(dtick=1))
        st.plotly_chart(fig, use_container_width=True)

        # Year-over-year change
        st.subheader("Year-over-Year Change")
        yoy_rows = []
        for comp in sel_companies:
            sub = df_trend[df_trend["COMPANY"]==comp].sort_values("YEAR")
            sub["YoY Change"] = sub[sel_metric].diff()
            sub["YoY %"] = sub[sel_metric].pct_change() * 100
            yoy_rows.append(sub)
        if yoy_rows:
            yoy_df = pd.concat(yoy_rows).round(3)
            st.dataframe(yoy_df, use_container_width=True, height=340)

        # Multi-metric correlation over time
        st.subheader("ESG vs SCM — Correlation by Year")
        ESG_C = [c for c in ["ESG_SCORE","EMISSIONS_SCORE"] if c in df_raw.columns]
        SCM_C = [c for c in ["CASH_CONVERSION_CYCLE","INVENTORY_TURNOVER"] if c in df_raw.columns]

        if ESG_C and SCM_C:
            corr_by_year = []
            for yr in sorted(df_raw["YEAR"].dropna().unique()):
                sub = df_raw[df_raw["YEAR"]==yr]
                for e in ESG_C:
                    for s in SCM_C:
                        vals = sub[[e,s]].apply(pd.to_numeric,errors="coerce").dropna()
                        if len(vals) > 2:
                            corr_by_year.append({
                                "Year": int(yr),
                                "Pair": f"{e} vs {s}",
                                "r": round(vals[e].corr(vals[s]),3)
                            })
            if corr_by_year:
                cy_df = pd.DataFrame(corr_by_year)
                fig2 = px.line(cy_df, x="Year", y="r", color="Pair", markers=True,
                               title="How ESG–SCM correlations change over time",
                               color_discrete_sequence=px.colors.qualitative.Pastel)
                fig2.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=380)
                st.plotly_chart(fig2, use_container_width=True)
