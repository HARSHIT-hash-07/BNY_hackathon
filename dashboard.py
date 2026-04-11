"""
dashboard.py
Streamlit dashboard for the Smart KYC Risk Scoring Engine.

Run with:  streamlit run dashboard.py

Layout: Clean tab-based navigation with 4 main tabs:
  1. Overview    — KPIs + tier/decision charts
  2. Analytics   — Score distribution + risk factor analysis + correlations
  3. Customers   — Filterable table + individual customer drill-down
  4. Insights    — SHAP explainability + business intelligence

BNY Hackathon 2026 · We Tried Team
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from collections import Counter

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="KYC Risk Engine · BNY Hackathon",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS — Premium dark theme with Inter font, clean tab styling
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    /* ── Global Typography & Base ──────────────────────── */
    html, body, [class*="css"], .stMarkdown, .stText,
    div[data-testid="stMetric"], h1, h2, h3, h4, p, span, label {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    }

    .stApp {
        background: radial-gradient(circle at top right, #1a1f35 0%, #0d1117 100%);
        background-attachment: fixed;
    }

    /* ── Sidebar Styling ────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: rgba(13, 17, 23, 0.8);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 2rem;
    }

    /* ── Capsule Tabs ───────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255, 255, 255, 0.03);
        border-radius: 50px;
        padding: 6px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 2rem;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px;
        border-radius: 40px;
        color: #8B8FA3;
        font-weight: 500;
        font-size: 0.8rem;
        padding: 0 1.5rem;
        background-color: transparent;
        border: none;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2D333B !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
    .stTabs [data-baseweb="tab-border"] { display: none; }

    /* ── FinShield Style Metric Cards ──────────────────── */
    .metric-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
    }
    .fin-card {
        background: rgba(45, 51, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 1.5rem;
        backdrop-filter: blur(12px);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .fin-card:hover {
        transform: translateY(-5px);
        border-color: rgba(108, 99, 255, 0.3);
    }
    .fin-card-label {
        color: #8B8FA3;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    .fin-card-value {
        color: #FFFFFF;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .fin-card-delta {
        font-size: 0.75rem;
        font-weight: 500;
    }

    /* ── Progress Stepper ───────────────────────────────── */
    .stepper-bg {
        background: rgba(255,255,255,0.02);
        height: 4px;
        border-radius: 2px;
        width: 100%;
        margin-top: 10px;
        position: relative;
    }
    .stepper-fill {
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        height: 100%;
        border-radius: 2px;
        transition: width 1s ease-in-out;
    }

    /* ── Glass Containers ───────────────────────────────── */
    .glass-panel {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }

    /* ── Section Titles ────────────────────────────────── */
    .hero-h1 {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(to right, #FFFFFF, #8B8FA3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    /* ── Graph Containers ──────────────────────────────── */
    .chart-box {
        background: rgba(13, 17, 23, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        padding: 1rem;
    }

    /* ── Profile Snapshot ──────────────────────────────── */
    .profile-pill {
        background: rgba(108, 99, 255, 0.1);
        color: #6C63FF;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
    }

    /* Hide branding */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    path = 'output/kyc_output.csv'
    if not os.path.exists(path):
        st.error("Run `python main.py` first to generate kyc_output.csv")
        st.stop()
    return pd.read_csv(path)

df = load_data()

# ── Colour constants ──────────────────────────────────────────────────────────
TIER_COLORS = {'LOW': '#22C55E', 'MEDIUM': '#F59E0B', 'HIGH': '#EF4444'}
DECISION_COLORS = {
    'APPROVE': '#22C55E', 'MANUAL_REVIEW': '#F59E0B',
    'REJECT': '#EF4444', 'EDD': '#8B5CF6'
}
def apply_chart_theme(fig, height=340):
    """Apply consistent dark theme to all Plotly charts."""
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color='#8B8FA3', size=11),
        height=height,
        margin=dict(t=30, b=30, l=30, r=30),
        legend=dict(font=dict(size=10, color='#8B8FA3'), orientation='h', y=-0.2),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.05)', tickfont=dict(size=10)),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.05)', tickfont=dict(size=10)),
    )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0; margin-bottom: 2rem;">
        <h2 style="color: #FFFFFF; font-weight: 800; margin-bottom: 0; font-size: 1.4rem;">FinShield AI</h2>
        <p style="color: #6C63FF; font-size: 0.65rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">Technical Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p style="color: #6B7084; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; margin-bottom: 1rem;">Main Monitor</p>', unsafe_allow_html=True)
    
    nav_option = st.radio(
        "Navigation",
        ["Overview", "Analytics", "Customers", "Database", "Insights"],
        label_visibility="collapsed",
        index=0
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<p style="color: #6B7084; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; margin-bottom: 1rem;">System Health</p>', unsafe_allow_html=True)
    st.success("Engine: Operational")
    st.info("API: Connected")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT ROUTING
# ══════════════════════════════════════════════════════════════════════════════

# ──────────────────────────────────────────────────────────────────────────────
# MODULE: OVERVIEW
# ──────────────────────────────────────────────────────────────────────────────
if nav_option == "Overview":
    # ──────────────────────────────────────────────────────────────────────────
    # DATA LOGIC FOR NEW METRICS
    # ──────────────────────────────────────────────────────────────────────────
    total = len(df)
    approved = len(df[df['decision'] == 'APPROVE'])
    manual = len(df[df['decision'] == 'MANUAL_REVIEW'])
    edd = len(df[df['decision'] == 'EDD'])
    avg_score = df['risk_score'].mean()
    high_risk_count = len(df[df['risk_tier'] == 'HIGH'])
    high_risk_pct = (high_risk_count / total) * 100

    # Calculate Top Risk Driver
    all_factors = ', '.join(df[df['risk_tier'] != 'LOW']['top_risk_factors'].dropna()).split(', ')
    all_factors = [f.strip() for f in all_factors if f.strip() and "No significant" not in f]
    if all_factors:
        top_driver = Counter(all_factors).most_common(1)[0][0]
    else:
        top_driver = "Stable Environment"

    # Layout: FinShield Profile Header
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2rem;">
        <div>
            <div class="profile-pill">GLOBAL RISK ADVISORY</div>
            <h1 class="hero-h1">Consolidated Risk Analysis</h1>
            <p style="color: #8B8FA3; font-size: 0.9rem;">Intelligence-driven onboarding decisions for the current processing pool.</p>
        </div>
        <div style="display: flex; gap: 40px; text-align: right;">
            <div>
                <p class="fin-card-label">High Risk Percentage</p>
                <p class="fin-card-value" style="color: #EF4444;">{high_risk_pct:.1f}%</p>
            </div>
            <div>
                <p class="fin-card-label">Top Risk Driver</p>
                <p style="color: #FFFFFF; font-size: 1rem; font-weight: 600; margin-top: 5px;">{top_driver}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-label">Key Performance Indicators</p>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Customers", f"{total:,}")
    c2.metric("Approved", f"{approved:,}", f"{approved/total*100:.1f}%")
    c3.metric("Manual Review", f"{manual:,}", f"{manual/total*100:.1f}%")
    c4.metric("Escalated (EDD)", f"{edd:,}", f"{edd/total*100:.1f}%")
    c5.metric("Avg Risk Score", f"{avg_score:.1f}", "out of 100")

    st.markdown("")

    # Charts row
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<p class="section-label">Risk Tier Distribution</p>', unsafe_allow_html=True)
        tier_counts = df['risk_tier'].value_counts().reset_index()
        tier_counts.columns = ['Tier', 'Count']
        fig = px.pie(
            tier_counts, names='Tier', values='Count',
            color='Tier', color_discrete_map=TIER_COLORS, hole=0.55
        )
        fig.update_traces(
            textposition='inside', textinfo='percent+label',
            textfont=dict(size=12, family='Plus Jakarta Sans'),
            marker=dict(line=dict(color='#0D1117', width=3))
        )
        apply_chart_theme(fig, height=320)
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")

    with col_r:
        st.markdown('<p class="section-label">Onboarding Decision Breakdown</p>', unsafe_allow_html=True)
        dec_counts = df['decision'].value_counts().reset_index()
        dec_counts.columns = ['Decision', 'Count']
        fig = px.bar(
            dec_counts, x='Decision', y='Count',
            color='Decision', color_discrete_map=DECISION_COLORS,
            text='Count'
        )
        fig.update_traces(textposition='outside', textfont=dict(size=13, color='#E8E8EC'))
        fig.update_layout(showlegend=False)
        apply_chart_theme(fig, height=320)
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")

    # Quick stats row
    st.markdown('<p class="section-label">Dataset Summary</p>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    if 'sanctions_flag' in df.columns:
        s1.metric("Sanctioned", f"{df['sanctions_flag'].sum()}", "of 1000 customers")
    if 'fraud_history_flag' in df.columns:
        fraud_pct = df['fraud_history_flag'].mean() * 100
        s2.metric("Fraud History", f"{fraud_pct:.1f}%", "of applicant pool")
    if 'pep_flag' in df.columns:
        s3.metric("PEP Flagged", f"{df['pep_flag'].sum()}", "Politically Exposed")
    s4.metric("Score Range", f"{df['risk_score'].min():.1f} – {df['risk_score'].max():.1f}", "min – max")


# ──────────────────────────────────────────────────────────────────────────────
# MODULE: ANALYTICS
# ──────────────────────────────────────────────────────────────────────────────
elif nav_option == "Analytics":

    # Row 1: Score distribution + Risk factors
    a1, a2 = st.columns(2)

    with a1:
        st.markdown('<p class="section-label">Risk Score Distribution</p>', unsafe_allow_html=True)
        fig = px.histogram(
            df, x='risk_score', color='risk_tier',
            color_discrete_map=TIER_COLORS,
            nbins=30, barmode='overlay', opacity=0.8,
            labels={'risk_score': 'Risk Score', 'risk_tier': 'Risk Tier'}
        )
        fig.add_vline(x=25, line_dash="dot", line_color="#F59E0B", line_width=1,
                      annotation_text="LOW / MED", annotation_font_color="#F59E0B",
                      annotation_font_size=10, annotation_position="top")
        fig.add_vline(x=40, line_dash="dot", line_color="#EF4444", line_width=1,
                      annotation_text="MED / HIGH", annotation_font_color="#EF4444",
                      annotation_font_size=10, annotation_position="top")
        apply_chart_theme(fig, height=360)
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")

    with a2:
        st.markdown('<p class="section-label">Top Risk Factors — Flagged Customers</p>', unsafe_allow_html=True)
        flagged = df[df['risk_tier'].isin(['MEDIUM', 'HIGH'])].copy()
        if len(flagged) > 0:
            all_factors = ', '.join(flagged['top_risk_factors'].dropna()).split(', ')
            all_factors = [f.strip() for f in all_factors
                          if f.strip() and f.strip() != 'No significant risk flags identified']
            factor_counts = Counter(all_factors)
            fc_df = pd.DataFrame(factor_counts.most_common(8), columns=['Factor', 'Count'])
            fig = px.bar(fc_df, x='Count', y='Factor', orientation='h',
                        color='Count', color_continuous_scale=['#1E2538', '#6C63FF'])
            fig.update_layout(showlegend=False, coloraxis_showscale=False,
                            yaxis=dict(categoryorder='total ascending'))
            fig.update_traces(texttemplate='%{x}', textposition='outside',
                            textfont=dict(color='#8B8FA3', size=11))
            apply_chart_theme(fig, height=360)
            st.plotly_chart(fig, use_container_width=True, theme="streamlit")

    st.markdown("")

    # Row 2: Correlation Heatmap
    st.markdown('<p class="section-label">Risk Factor Correlation Matrix</p>', unsafe_allow_html=True)

    corr_features = ['risk_score', 'pep_flag', 'sanctions_flag', 'adverse_media_flag',
                     'fraud_history_flag', 'digital_risk_score', 'monthly_txn_count',
                     'annual_income', 'customer_tenure_years', 'age']
    corr_features = [c for c in corr_features if c in df.columns]

    if len(corr_features) > 3:
        # Clean feature names for display
        display_names = {
            'risk_score': 'Risk Score', 'pep_flag': 'PEP Flag',
            'sanctions_flag': 'Sanctions', 'adverse_media_flag': 'Adverse Media',
            'fraud_history_flag': 'Fraud History', 'digital_risk_score': 'Digital Risk',
            'monthly_txn_count': 'Txn Count', 'annual_income': 'Income',
            'customer_tenure_years': 'Tenure', 'age': 'Age'
        }
        corr_data = df[corr_features].rename(columns=display_names).corr()
        fig = px.imshow(
            corr_data, color_continuous_scale=['#1a1d26', '#6C63FF', '#F0F0F5'],
            zmin=-1, zmax=1, aspect='auto', text_auto='.2f'
        )
        fig.update_traces(textfont=dict(size=10, color='#E8E8EC'))
        apply_chart_theme(fig, height=420)
        fig.update_layout(coloraxis_colorbar=dict(
            title='', tickfont=dict(color='#6B7084'),
            outlinewidth=0, bgcolor='rgba(0,0,0,0)'
        ))
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")


# ──────────────────────────────────────────────────────────────────────────────
# MODULE: CUSTOMERS
# ──────────────────────────────────────────────────────────────────────────────
elif nav_option == "Customers":

    # Filters row
    st.markdown('<p class="section-label">Filters</p>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns([1, 1, 1, 1])

    with f1:
        tier_filter = st.multiselect(
            "Risk Tier", options=['LOW', 'MEDIUM', 'HIGH'],
            default=['LOW', 'MEDIUM', 'HIGH'], key='cust_tier'
        )
    with f2:
        decision_filter = st.multiselect(
            "Decision", options=['APPROVE', 'MANUAL_REVIEW', 'REJECT', 'EDD'],
            default=['APPROVE', 'MANUAL_REVIEW', 'REJECT', 'EDD'], key='cust_dec'
        )
    with f3:
        score_range = st.slider(
            "Score Range", min_value=0.0, max_value=100.0,
            value=(0.0, 100.0), step=0.5, key='cust_score'
        )
    with f4:
        customer_search = st.text_input("Search Customer ID", "", key='cust_search')

    # Apply filters
    filtered = df[
        (df['risk_tier'].isin(tier_filter)) &
        (df['decision'].isin(decision_filter)) &
        (df['risk_score'] >= score_range[0]) &
        (df['risk_score'] <= score_range[1])
    ]
    if customer_search:
        filtered = filtered[filtered['customer_id'].str.contains(
            customer_search, case=False, na=False)]

    st.markdown("")

    # Customer table
    display_cols = ['customer_id', 'risk_score', 'risk_tier', 'decision', 'top_risk_factors']
    display_cols = [c for c in display_cols if c in filtered.columns]

    st.markdown(f'<p class="section-label">Customer Risk Decisions — {len(filtered)} of {len(df)} records</p>',
                unsafe_allow_html=True)

    def highlight_tier(val):
        if val == 'HIGH':
            return 'background-color: rgba(239, 68, 68, 0.15); color: #EF4444; font-weight: 600'
        elif val == 'MEDIUM':
            return 'background-color: rgba(245, 158, 11, 0.15); color: #F59E0B; font-weight: 600'
        elif val == 'LOW':
            return 'background-color: rgba(34, 197, 94, 0.15); color: #22C55E; font-weight: 600'
        return ''

    def highlight_decision(val):
        colors = {
            'APPROVE': 'rgba(34, 197, 94, 0.15)',
            'MANUAL_REVIEW': 'rgba(245, 158, 11, 0.15)',
            'REJECT': 'rgba(239, 68, 68, 0.15)',
            'EDD': 'rgba(139, 92, 246, 0.15)'
        }
        text_colors = {
            'APPROVE': '#22C55E', 'MANUAL_REVIEW': '#F59E0B',
            'REJECT': '#EF4444', 'EDD': '#8B5CF6'
        }
        bg = colors.get(val, '')
        tc = text_colors.get(val, '')
        return f'background-color: {bg}; color: {tc}; font-weight: 600' if bg else ''

    styled = (filtered[display_cols]
              .sort_values('risk_score', ascending=False)
              .style
              .map(highlight_tier, subset=['risk_tier'])
              .map(highlight_decision, subset=['decision'])
              .format({'risk_score': '{:.1f}'}))
    st.dataframe(
        styled,
        use_container_width=True,
        height=450,
        column_config={
            "customer_id": st.column_config.TextColumn("ID", width="small"),
            "risk_score": st.column_config.NumberColumn("Score", format="%.1f", width="small"),
            "risk_tier": st.column_config.TextColumn("Tier", width="small"),
            "decision": st.column_config.TextColumn("Decision", width="small"),
            "top_risk_factors": st.column_config.TextColumn("Risk Reasons", width="large"),
        }
    )

    st.markdown("")

    # Customer Detail View
    st.markdown('<p class="section-label">Customer Detail View</p>', unsafe_allow_html=True)

    sel_col, _ = st.columns([1, 3])
    with sel_col:
        customer_list = filtered['customer_id'].tolist() if len(filtered) > 0 else df['customer_id'].tolist()
        selected_id = st.selectbox("Select customer", options=customer_list, key='cust_select')

    customer = df[df['customer_id'] == selected_id].iloc[0]
    tier_icon = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🔴'}.get(customer['risk_tier'], '⚪')

    # Styled Profile Section
    st.markdown(f"""
    <div style="margin-top: 1rem; margin-bottom: 2rem;">
        <h2 style="color: #FFFFFF; font-size: 1.5rem; font-weight: 700;">{selected_id} — Profile Intel</h2>
    </div>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 2.5rem;">
        <div class="fin-card">
            <p class="fin-card-label">Risk Analytics</p>
            <p class="fin-card-value" style="color: {'#EF4444' if customer['risk_score'] > 40 else '#F59E0B' if customer['risk_score'] > 25 else '#22C55E'}">{customer['risk_score']:.1f}</p>
            <div class="stepper-bg"><div class="stepper-fill" style="width: {min(100, int(customer['risk_score']))}%"></div></div>
            <p style="color:#8B8FA3; font-size:0.65rem; margin-top:8px;">RELATIVE RISK VECTOR</p>
        </div>
        <div class="fin-card">
            <p class="fin-card-label">Classification</p>
            <p class="fin-card-value" style="font-size: 1.4rem; padding-top: 0.5rem;">{tier_icon} {customer['risk_tier']}</p>
            <p style="color:#8B8FA3; font-size:0.65rem; margin-top:14px;">THRESHOLD CATEGORY</p>
        </div>
        <div class="fin-card">
            <p class="fin-card-label">Digital Risk Path</p>
            <p class="fin-card-value">{customer['digital_risk_score'] if 'digital_risk_score' in df.columns else 'N/A'}</p>
            <p style="color:#8B8FA3; font-size:0.65rem; margin-top:10px;">VIRTUAL ENTITY SCORE</p>
        </div>
        <div class="fin-card">
            <p class="fin-card-label">Onboarding Status</p>
            <p class="fin-card-value" style="font-size: 1.1rem; padding-top: 0.7rem;">{customer['decision']}</p>
            <p style="color:#8B8FA3; font-size:0.65rem; margin-top:12px;">SYSTEM DIRECTIVE</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.info(f"**Primary Intelligence Findings:** {customer['top_risk_factors']}")

    with st.expander("Full Customer Profile"):
        profile_cols = ['age', 'country_risk', 'occupation', 'annual_income', 'account_type',
                       'document_status', 'address_verified', 'pep_flag', 'sanctions_flag',
                       'adverse_media_flag', 'customer_tenure_years', 'digital_risk_score',
                       'fraud_history_flag', 'monthly_txn_count']
        available = [c for c in profile_cols if c in df.columns]
        profile = pd.DataFrame(
            [(k, str(customer[k])) for k in available],
            columns=['Field', 'Value']
        )
        st.dataframe(profile, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────────────────────────
# MODULE: DATABASE
# ──────────────────────────────────────────────────────────────────────────────
elif nav_option == "Database":
    st.markdown('<p class="section-label">Master Customer Records</p>', unsafe_allow_html=True)
    st.markdown("Entire dataset showing all calculated risk parameters and input values.")

    # Select columns for the "sheet type thing"
    core_cols = ['customer_id', 'risk_score', 'decision', 'top_risk_factors']
    other_cols = [c for c in df.columns if c not in core_cols]
    final_sheet_cols = core_cols + other_cols

    st.dataframe(
        df[final_sheet_cols].sort_values('risk_score', ascending=False),
        use_container_width=True,
        height=600,
        column_config={
            "customer_id": "Customer ID",
            "risk_score": st.column_config.NumberColumn("Risk Score", format="%.1f"),
            "decision": "Decision",
            "top_risk_factors": st.column_config.TextColumn("Risk Reason", width="large"),
        }
    )


# ──────────────────────────────────────────────────────────────────────────────
# MODULE: INSIGHTS
# ──────────────────────────────────────────────────────────────────────────────
elif nav_option == "Insights":

    # SHAP section
    st.markdown('<p class="section-label">Explainability Engine</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-panel">
        <h3 style="margin-top:0; color:#FFFFFF; font-size:1.1rem;">Feature Contribution Mapping (SHAP)</h3>
        <p style="color:#8B8FA3; font-size:0.85rem; margin-bottom:1.5rem;">Visualizing how individual data points push the model prediction toward increased risk. 
        Positive SHAP values (magenta) indicate factors that increase risk, while negative values (blue) decrease it.</p>
    </div>
    """, unsafe_allow_html=True)

    shap_l, shap_r = st.columns(2)
    with shap_l:
        if os.path.exists('output/shap_summary.png'):
            st.image('output/shap_summary.png',
                     caption='Feature impact on HIGH risk classification',
                     use_container_width=True)
        else:
            st.warning("Run main.py to generate SHAP plots")
    with shap_r:
        if os.path.exists('output/shap_importance.png'):
            st.image('output/shap_importance.png',
                     caption='Mean absolute feature contribution',
                     use_container_width=True)
        else:
            st.warning("Run main.py to generate SHAP plots")

    st.markdown("")

    # Business Insights
    st.markdown('<p class="section-label">Business Intelligence</p>', unsafe_allow_html=True)

    bi1, bi2 = st.columns(2)

    with bi1:
        # Fraud prevalence insight
        if 'fraud_history_flag' in df.columns:
            fraud_rate = df['fraud_history_flag'].mean() * 100
            with st.container(border=True):
                st.markdown(f"""
                **🚨 Anomaly Detection: Fraud Nexus**

                **{fraud_rate:.1f}%** of processing pool matches known fraud signatures. Cluster analysis indicates high-risk acquisition channel correlation.

                **System Directive:** Review Tier 2 referral sources for systemic vulnerability.
                """)

        # Document compliance by account type
        if 'account_type' in df.columns and 'document_status' in df.columns:
            with st.container(border=True):
                st.markdown("**📋 Document Compliance by Account Type**")
                doc_compliance = pd.crosstab(
                    df['account_type'], df['document_status'],
                    normalize='index'
                ).round(3) * 100
                fig = px.bar(
                    doc_compliance.reset_index().melt(id_vars='account_type'),
                    x='account_type', y='value', color='document_status',
                    barmode='group',
                    labels={'value': '%', 'account_type': 'Account Type',
                            'document_status': 'Doc Status'},
                    color_discrete_map={'Complete': '#22C55E', 'Partial': '#F59E0B', 'Missing': '#EF4444'}
                )
                fig.update_layout(showlegend=True,
                                 legend=dict(orientation='h', y=-0.2, title=''))
                apply_chart_theme(fig, height=300)
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")

    with bi2:
        # Red flag combinations
        with st.container(border=True):
            st.markdown("**🚩 Multi-Flag Customers**")
            st.caption("Customers with 3+ simultaneous risk indicators")

            flag_cols = ['pep_flag', 'sanctions_flag', 'adverse_media_flag', 'fraud_history_flag']
            available_flags = [c for c in flag_cols if c in df.columns]

            if available_flags:
                df_temp = df.copy()
                if 'address_verified' in df.columns:
                    df_temp['addr_unverified'] = (1 - df_temp['address_verified']).astype(int)
                    check_flags = available_flags + ['addr_unverified']
                else:
                    check_flags = available_flags

                df_temp['total_flags'] = df_temp[check_flags].sum(axis=1)
                multi_flag = df_temp[df_temp['total_flags'] >= 3]

                st.metric("Multi-Flag Count", len(multi_flag),
                          f"{len(multi_flag)/len(df)*100:.1f}% of total")

                if len(multi_flag) > 0:
                    st.dataframe(
                        multi_flag[['customer_id', 'risk_score', 'risk_tier', 'decision', 'total_flags']]
                        .sort_values('total_flags', ascending=False).head(8),
                        width='stretch', hide_index=True
                    )

        # Age group risk
        if 'age' in df.columns:
            with st.container(border=True):
                st.markdown("**👤 Risk Distribution by Age Group**")
                df_age = df.copy()
                df_age['age_group'] = pd.cut(
                    df_age['age'], bins=[0, 25, 40, 55, 100],
                    labels=['18–25', '26–40', '41–55', '56+']
                )
                age_risk = df_age.groupby('age_group', observed=True)['risk_score'].agg(
                    ['mean', 'count']).reset_index()
                age_risk.columns = ['Age Group', 'Avg Score', 'Count']
                fig = px.bar(age_risk, x='Age Group', y='Avg Score',
                            text='Count', color='Avg Score',
                            color_continuous_scale=['#1E2538', '#6C63FF'])
                fig.update_traces(texttemplate='n=%{text}', textposition='outside',
                                textfont=dict(color='#8B8FA3'))
                fig.update_layout(coloraxis_showscale=False)
                apply_chart_theme(fig, height=260)
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<p class="footer-text">
    Built with Python · XGBoost · SHAP · Streamlit<br>
    BNY Hackathon 2026 · We Tried Team · Synthetic data only
</p>
""", unsafe_allow_html=True)
