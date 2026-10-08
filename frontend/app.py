import html
from datetime import datetime

import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DecisionPulse | Decision Impact Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# THEME / CSS
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --bg: #071126;
        --panel: #0b1730;
        --panel-2: #0f1d39;
        --border: #1e3153;
        --muted: #91a1bb;
        --text: #f5f8ff;
        --blue: #3b82f6;
        --blue-2: #62a0ff;
        --red: #ff4d68;
        --red-soft: #2a1019;
        --green: #32d583;
        --amber: #f6b84b;
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: var(--bg);
    }

    [data-testid="stSidebar"] {
        background: #061022;
        border-right: 1px solid #172845;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.25rem;
        padding-bottom: 3rem;
    }

    /* Sidebar */
    .brand {
        font-size: 28px;
        font-weight: 850;
        letter-spacing: -1px;
        color: #ffffff;
        margin-bottom: 2px;
    }

    .brand-icon { color: #62a0ff; }

    .brand-subtitle {
        color: #7f90aa;
        font-size: 13px;
        margin-bottom: 25px;
    }

    .sidebar-label {
        color: #8ea2c0;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        margin: 20px 0 9px;
    }

    .monitor-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 24px;
        padding: 10px 13px;
        border-radius: 12px;
        border: 1px solid #155b43;
        background: #081f19;
        color: #49e79a;
        font-size: 13px;
        font-weight: 750;
    }

    .sync-text {
        color: #8293ad;
        font-size: 12px;
        margin-top: 9px;
    }


    /* Streamlit navigation / controls: keep text clearly readable */
    [data-testid="stSidebar"] .stRadio label {
        color: #cbd6e8 !important;
        font-size: 14px !important;
        font-weight: 650 !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] .stRadio label p,
    [data-testid="stSidebar"] .stRadio label span,
    [data-testid="stSidebar"] .stRadio label div {
        color: #cbd6e8 !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] > label[data-checked="true"],
    [data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) {
        color: #ffffff !important;
        background: #10244a !important;
        border-radius: 9px;
    }

    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #9aabc4 !important;
    }

    /* Hero */
    .eyebrow {
        color: var(--blue-2);
        font-size: 11px;
        font-weight: 850;
        letter-spacing: 2.5px;
        margin-bottom: 10px;
    }

    .hero-title {
        color: var(--text);
        font-size: 48px;
        line-height: 1.03;
        font-weight: 850;
        letter-spacing: -2px;
        margin: 0 0 14px;
    }

    .hero-description {
        color: #a4b1c5;
        font-size: 16px;
        line-height: 1.55;
        max-width: 880px;
        margin-bottom: 20px;
    }

    /* Metrics */
    .metric-card {
        background: linear-gradient(145deg, #0d1a33, #09152b);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 18px 19px;
        min-height: 118px;
    }

    .metric-label {
        color: #7385a1;
        font-size: 10px;
        font-weight: 850;
        letter-spacing: 1.5px;
    }

    .metric-value {
        color: #ffffff;
        font-size: 34px;
        font-weight: 850;
        margin-top: 8px;
        letter-spacing: -1px;
    }

    .metric-value.blue { color: #62a0ff; }
    .metric-value.red { color: #ff627b; }
    .metric-value.green { color: #49e79a; }

    .metric-note {
        color: #71839f;
        font-size: 12px;
        margin-top: 3px;
    }

    /* Section */
    .section-head {
        color: #7385a1;
        font-size: 11px;
        font-weight: 850;
        letter-spacing: 2px;
        margin: 28px 0 10px;
    }

    /* Simulation panel */
    .panel {
        background: #0a1730;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 19px;
    }

    .panel-title {
        color: #ffffff;
        font-size: 17px;
        font-weight: 800;
        margin-bottom: 3px;
    }

    .panel-subtitle {
        color: #91a2bb;
        font-size: 12px;
        margin-bottom: 15px;
    }

    .stTextInput input,
    [data-baseweb="select"] > div {
        background: #0f1d35 !important;
        color: #f5f8ff !important;
        border-color: #263c61 !important;
        border-radius: 9px !important;
    }

    .stTextInput label,
    .stSelectbox label {
        color: #8e9db4 !important;
        font-size: 12px !important;
        font-weight: 650 !important;
    }

    .stButton > button {
        border-radius: 9px;
        min-height: 44px;
        font-weight: 800;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3478ee, #245dcc);
        color: #ffffff !important;
        border: 1px solid #5b98ff;
        box-shadow: 0 8px 24px rgba(47,111,228,.24);
        font-size: 14px;
        min-height: 50px;
    }

    .stButton > button[kind="primary"]:hover {
        background: #3c7df0;
    }

    /* Change alert */
    .change-card {
        background: linear-gradient(135deg, #1d0b14, #120a12);
        border: 1px solid #5b2235;
        border-left: 5px solid var(--red);
        border-radius: 15px;
        padding: 17px 19px;
    }

    .change-title {
        color: #ffffff;
        font-size: 19px;
        font-weight: 820;
    }

    .change-meta {
        color: #a6b2c5;
        font-size: 13px;
        margin-top: 7px;
        line-height: 1.5;
    }

    .status-badge {
        display: inline-block;
        margin-left: 7px;
        padding: 4px 8px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 850;
        letter-spacing: .4px;
    }

    .badge-high {
        color: #ff8094;
        background: #35121e;
        border: 1px solid #7b2943;
    }

    .badge-medium {
        color: #ffc76d;
        background: #2f210c;
        border: 1px solid #72511a;
    }

    .badge-low {
        color: #52eaa0;
        background: #08251a;
        border: 1px solid #176044;
    }

    /* Impact pipeline */
    .pipeline {
        display: flex;
        align-items: stretch;
        gap: 8px;
        margin-top: 5px;
    }

    .pipe-node {
        flex: 1;
        min-height: 102px;
        background: #0d1a32;
        border: 1px solid #263c61;
        border-radius: 13px;
        padding: 15px;
    }

    .pipe-node.hot {
        border-color: #6b2940;
        background: #1a0d16;
    }

    .pipe-label {
        color: #6f82a0;
        font-size: 9px;
        font-weight: 850;
        letter-spacing: 1.3px;
    }

    .pipe-value {
        color: #f7f9ff;
        font-size: 17px;
        font-weight: 800;
        margin-top: 9px;
        line-height: 1.2;
    }

    .pipe-detail {
        color: #8393ab;
        font-size: 11px;
        margin-top: 5px;
    }

    .pipe-arrow {
        align-self: center;
        color: #4d88ef;
        font-size: 24px;
        font-weight: 800;
    }

    /* AI / action */
    .insight-card {
        background: linear-gradient(145deg, #0d1a33, #0a152b);
        border: 1px solid #294166;
        border-radius: 15px;
        padding: 19px;
    }

    .insight-title {
        color: #ffffff;
        font-size: 17px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .insight-text {
        color: #a5b2c6;
        font-size: 13px;
        line-height: 1.55;
    }

    .risk-chip {
        display: inline-block;
        margin-top: 13px;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 850;
        letter-spacing: 1px;
    }

    .risk-high { background: #35121e; color: #ff8195; border: 1px solid #7b2943; }
    .risk-medium { background: #30200b; color: #ffc76b; border: 1px solid #715019; }
    .risk-low { background: #08251a; color: #51e99f; border: 1px solid #176044; }

    .action-card {
        background: #102b60;
        border: 1px solid #2e6bd4;
        border-radius: 15px;
        padding: 19px;
    }

    .action-title {
        color: #ffffff;
        font-size: 17px;
        font-weight: 800;
        margin-bottom: 7px;
    }

    .action-text {
        color: #d5e3ff;
        font-size: 13px;
        line-height: 1.5;
    }

    /* Result summary */
    .result-summary {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-top: 12px;
    }

    .result-stat {
        background: #0c1830;
        border: 1px solid #203657;
        border-radius: 12px;
        padding: 13px 15px;
    }

    .result-stat-label {
        color: #91a3bd;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.1px;
        text-transform: uppercase;
    }

    .result-stat-value {
        color: #ffffff;
        font-size: 26px;
        font-weight: 850;
        margin-top: 4px;
    }

    .result-stat-value.red { color: #ff667e; }
    .result-stat-value.blue { color: #62a0ff; }

    .success-banner {
        margin-top: 12px;
        padding: 13px 16px;
        border-radius: 11px;
        background: #06271c;
        border: 1px solid #12623f;
        color: #55e7a0;
        font-size: 13px;
        font-weight: 700;
    }

    /* Secondary pages */
    .page-card {
        background: #0a1730;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 22px;
        margin-top: 10px;
    }

    .placeholder {
        color: #8999b1;
        font-size: 13px;
        line-height: 1.55;
    }

    .footer {
        text-align: center;
        color: #4f617e;
        font-size: 11px;
        margin-top: 45px;
    }

    @media (max-width: 900px) {
        .hero-title { font-size: 38px; }
        .pipeline { flex-direction: column; }
        .pipe-arrow { transform: rotate(90deg); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS / STATE
# ============================================================

if "analysis" not in st.session_state:
    st.session_state.analysis = None


def esc(value: str) -> str:
    return html.escape(str(value))


def analyze(status: str):
    if status in ("Expired", "Revoked"):
        return {
            "affected": 17,
            "high_risk": 4,
            "risk": "HIGH",
            "risk_class": "risk-high",
            "badge_class": "badge-high",
            "recommendation": "Revalidate affected decisions and hold high-risk decisions until evidence is revalidated.",
            "action": "Revalidate + Hold",
        }
    if status == "Expiring Soon":
        return {
            "affected": 9,
            "high_risk": 2,
            "risk": "MEDIUM",
            "risk_class": "risk-medium",
            "badge_class": "badge-medium",
            "recommendation": "Notify decision owners and schedule evidence revalidation before expiry.",
            "action": "Notify + Revalidate",
        }
    return {
        "affected": 0,
        "high_risk": 0,
        "risk": "LOW",
        "risk_class": "risk-low",
        "badge_class": "badge-low",
        "recommendation": "No immediate action required; continue monitoring the evidence.",
        "action": "Continue monitoring",
    }


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-icon">⚡</span> DecisionPulse</div>'
        '<div class="brand-subtitle">Decision Impact Intelligence</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-label">WORKSPACE</div>', unsafe_allow_html=True)

    page = st.radio(
        "Workspace",
        ["Command Center", "Impact Analysis", "AI Investigation", "Action Center"],
        label_visibility="collapsed",
    )

    st.markdown(
        '<div class="monitor-pill"><span>●</span> Monitoring active</div>'
        '<div class="sync-text">Last sync · Just now</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-label">DEMO SCENARIO</div>', unsafe_allow_html=True)
    st.caption("Vendor A · Compliance certificate · C-017")
    st.caption("Demo path: Evidence → Impact → Risk → Action")


# ============================================================
# COMMAND CENTER
# ============================================================

if page == "Command Center":
    # Keep the hero full-width. The old right-side status pill was redundant
    # with the sidebar's "Monitoring active" indicator and could be clipped
    # by Streamlit's responsive column layout.
    st.markdown('<div class="eyebrow">CONTINUOUS DECISION VALIDATION</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Know which decisions changed<br>before they fail.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-description">DecisionPulse detects changes in decision-supporting evidence, traces downstream impact, investigates risk, and turns the result into an actionable response.</div>',
        unsafe_allow_html=True,
    )

    # High-signal metrics
    c1, c2, c3, c4 = st.columns(4)
    metric_data = [
        ("EVIDENCE SIGNALS", "42", "blue", "Prototype evidence graph"),
        ("IMPACTED NOW", "17", "blue", "From latest evidence change"),
        ("HIGH RISK", "4", "red", "Priority handling required"),
        ("REVALIDATION QUEUE", "9", "green", "Actions awaiting review"),
    ]
    for col, (label, value, color, note) in zip((c1, c2, c3, c4), metric_data):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{label}</div>'
                f'<div class="metric-value {color}">{value}</div>'
                f'<div class="metric-note">{note}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-head">01 · SIMULATE AN EVIDENCE CHANGE</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="panel"><div class="panel-title">Trigger a decision-impact event</div>'
        '<div class="panel-subtitle">Use the demo scenario to show the full DecisionPulse loop in real time.</div>',
        unsafe_allow_html=True,
    )

    a, b, c = st.columns([1.0, 1.25, 1.1])
    with a:
        evidence_id = st.text_input("Evidence ID", value="C-017")
    with b:
        entity = st.text_input("Entity", value="Vendor A")
    with c:
        status = st.selectbox("Evidence status", ["Valid", "Expiring Soon", "Expired", "Revoked"], index=2)

    d, e = st.columns([1.15, 2.0])
    with d:
        decision = st.selectbox(
            "Dependent decision",
            ["Vendor Approval", "Procurement Eligibility", "Payment Authorization", "Access Approval"],
        )
    with e:
        change_reason = st.text_input("Change reason", value="Compliance certificate status changed")

    run_col, hint_col = st.columns([1.1, 2.9])
    with run_col:
        run = st.button("⚡ Run Impact Analysis", type="primary", use_container_width=True)
    with hint_col:
        st.markdown(
            '<div style="color:#8fa1bc;font-size:12px;padding:13px 0 0 8px;">One click demonstrates: change detection → dependency tracing → AI risk → recommended action.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

    if run:
        result = analyze(status)
        st.session_state.analysis = {
            "evidence_id": evidence_id,
            "entity": entity,
            "status": status,
            "decision": decision,
            "change_reason": change_reason,
            **result,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }

    result = st.session_state.analysis

    if result:
        # 02 — detected change
        st.markdown('<div class="section-head">02 · LATEST DETECTED CHANGE</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="change-card">'
            f'<div class="change-title">🔴 {esc(result["entity"])} '
            f'<span class="status-badge {result["badge_class"]}">{esc(result["status"].upper())}</span></div>'
            f'<div class="change-meta"><b>Evidence {esc(result["evidence_id"])}</b> changed status · {esc(result["change_reason"])} · detected {esc(result["timestamp"])}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # 03 — impact pipeline
        st.markdown('<div class="section-head">03 · LIVE IMPACT PROPAGATION</div>', unsafe_allow_html=True)
        pipeline_html = f"""
        <div class="pipeline">
            <div class="pipe-node hot">
                <div class="pipe-label">EVIDENCE CHANGE</div>
                <div class="pipe-value">{esc(result['evidence_id'])}</div>
                <div class="pipe-detail">{esc(result['status'])}</div>
            </div>
            <div class="pipe-arrow">→</div>
            <div class="pipe-node">
                <div class="pipe-label">DEPENDENT DECISION</div>
                <div class="pipe-value">{esc(result['decision'])}</div>
                <div class="pipe-detail">Evidence dependency detected</div>
            </div>
            <div class="pipe-arrow">→</div>
            <div class="pipe-node">
                <div class="pipe-label">IMPACTED DECISIONS</div>
                <div class="pipe-value">{result['affected']}</div>
                <div class="pipe-detail">Downstream decisions</div>
            </div>
            <div class="pipe-arrow">→</div>
            <div class="pipe-node hot">
                <div class="pipe-label">HIGH-RISK</div>
                <div class="pipe-value">{result['high_risk']}</div>
                <div class="pipe-detail">Priority handling</div>
            </div>
        </div>
        """
        st.markdown(pipeline_html, unsafe_allow_html=True)

        # 04 + 05 — investigation and action
        st.markdown('<div class="section-head">04 · AI INVESTIGATION &nbsp;&nbsp; 05 · ACTION</div>', unsafe_allow_html=True)
        left, right = st.columns([1.15, 1.0])
        with left:
            st.markdown(
                f'<div class="insight-card">'
                f'<div class="insight-title">AI Impact Assessment</div>'
                f'<div class="insight-text">The change in <b>{esc(result["evidence_id"])}</b> affects decisions dependent on evidence associated with <b>{esc(result["entity"])}</b>. The system prioritizes the affected decisions by risk.</div>'
                f'<span class="risk-chip {result["risk_class"]}">{esc(result["risk"])} RISK</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with right:
            st.markdown(
                f'<div class="action-card">'
                f'<div class="action-title">Recommended action</div>'
                f'<div class="action-text"><b>{esc(result["action"])}</b><br>{esc(result["recommendation"])}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # High-contrast result summary
        st.markdown(
            f"""
            <div class="result-summary">
                <div class="result-stat">
                    <div class="result-stat-label">Affected decisions</div>
                    <div class="result-stat-value blue">{result["affected"]}</div>
                </div>
                <div class="result-stat">
                    <div class="result-stat-label">High-risk decisions</div>
                    <div class="result-stat-value red">{result["high_risk"]}</div>
                </div>
                <div class="result-stat">
                    <div class="result-stat-label">Risk level</div>
                    <div class="result-stat-value red">{esc(result["risk"])}</div>
                </div>
            </div>
            <div class="success-banner">✓ DecisionPulse completed the impact path: evidence change → affected decisions → risk → action.</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="page-card"><div class="panel-title">Ready for the live demo</div>'
            '<div class="placeholder">Click <b>Run Impact Analysis</b>. A single expired certificate will propagate through the decision dependency path and surface the affected and high-risk decisions.</div></div>',
            unsafe_allow_html=True,
        )


# ============================================================
# IMPACT ANALYSIS
# ============================================================

elif page == "Impact Analysis":
    st.markdown('<div class="eyebrow">DECISION DEPENDENCY GRAPH</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Trace every downstream impact.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-description">Map evidence to decisions, then propagate an evidence change through the dependency graph.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-card"><div class="panel-title">Prototype dependency graph</div>'
        '<div class="placeholder">The final graph adapter can replace this demo panel with the Decision Impact Engine output from Mem1.</div></div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Evidence nodes", "42")
    with c2:
        st.metric("Decision nodes", "17")
    with c3:
        st.metric("High-risk paths", "4")


# ============================================================
# AI INVESTIGATION
# ============================================================

elif page == "AI Investigation":
    st.markdown('<div class="eyebrow">AI REASONING LAYER</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Investigate why a decision is affected.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-description">Trace the evidence change, explain the decision impact, classify risk, and produce an action recommendation.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-card"><div class="panel-title">Reasoning sequence</div>'
        '<div class="placeholder"><b>1. Evidence changed</b> → <b>2. Dependencies traced</b> → <b>3. Impact explained</b> → <b>4. Risk assessed</b> → <b>5. Action recommended</b></div></div>',
        unsafe_allow_html=True,
    )


# ============================================================
# ACTION CENTER
# ============================================================

else:
    st.markdown('<div class="eyebrow">AUTOMATED RESPONSE</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Turn impact into action.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-description">Risk-ranked actions make it clear what should happen next after evidence changes.</div>',
        unsafe_allow_html=True,
    )

    actions = [
        ("Revalidate", "9", "Review decisions against updated evidence."),
        ("Flag for Review", "4", "Send high-risk cases for human review."),
        ("Notify Owner", "7", "Notify decision owners about evidence changes."),
        ("Hold Decision", "2", "Temporarily block high-risk decisions."),
    ]

    for title, count, description in actions:
        c1, c2, c3 = st.columns([2.2, 1, 5])
        with c1:
            st.markdown(f"### {title}")
        with c2:
            st.metric("Queue", count)
        with c3:
            st.markdown(f'<div class="placeholder" style="padding-top:10px;">{esc(description)}</div>', unsafe_allow_html=True)
        st.divider()


st.markdown(
    '<div class="footer">DecisionPulse · Continuous Decision Validation · Prototype</div>',
    unsafe_allow_html=True,
)
