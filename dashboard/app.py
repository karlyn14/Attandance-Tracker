"""Student Success Ledger — full-page wide dashboard with real dataset."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from data import load_dataset, get_student_subjects, get_student_timeline
from components.charts import make_chart, setup_theme
from components.overview_cards import h_ledger, h_risk_bars, h_stat
from components.student_detail import render_student_detail

setup_theme()


st.set_page_config(
    page_title="Student Success Ledger",
    page_icon="-",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design tokens ──────────────────────────────────────────────────────────
INK        = "#16213E"
INK_SOFT   = "#5a6370"
PAPER      = "#F3F3EF"
PAPER_CARD = "#EAEBE6"
RULE       = "#CACCC6"
BRASS      = "#A9812E"
BRASS_SOFT = "#D8C48F"
HIGH       = "#B23A48"
MED        = "#C98A2D"
LOW        = "#4C7A5E"
RISK_COLOR = {"High": HIGH, "Moderate": MED, "Low": LOW}

# ── CSS via st.html() — immune to Markdown parsing ────────────────────────
st.html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    color: #16213E;
}
.stApp { background-color: #F3F3EF; }
div[data-testid="stAppViewContainer"] { background-color: #F3F3EF; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ──────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background-color: #16213E !important;
    border-right: 2px solid #A9812E;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem;
    padding-left: 1.4rem;
    padding-right: 1.4rem;
}
section[data-testid="stSidebar"] * { color: #F3F3EF !important; }
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    border-left: 3px solid transparent;
    padding: 0.55rem 0 0.55rem 0.8rem !important;
    border-radius: 0 !important;
    font-size: 0.92rem;
    transition: border-color 0.15s;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    border-left: 3px solid #A9812E !important;
    background: rgba(169,129,46,0.12) !important;
}

/* ── Main content ─────────────────────────────────────────────── */
.block-container {
    padding: 2rem 2.5rem 3rem 2.5rem !important;
    max-width: 100% !important;
}

/* ── Typography helpers ───────────────────────────────────────── */
.pg-head {
    font-family: 'Source Serif 4', serif;
    font-size: 2rem;
    font-weight: 400;
    color: #16213E;
    margin: 0 0 0.2rem 0;
}
.gold-rule {
    border: none;
    border-top: 1.5px solid #A9812E;
    margin: 0 0 1.6rem 0;
}
.hairline {
    border: none;
    border-top: 1px solid #CACCC6;
    margin: 0 0 0.5rem 0;
}
.hero-num {
    font-family: 'Source Serif 4', serif;
    font-size: 5rem;
    line-height: 1;
    color: #16213E;
    font-variant-numeric: tabular-nums;
    margin: 0;
}
.hero-lbl { font-size: 0.92rem; color: #5a6370; margin: 0.5rem 0 0.2rem; }
.hero-dlt { font-size: 0.88rem; color: #4C7A5E; font-weight: 500; margin-bottom: 1.5rem; }

/* ── Ledger rows ──────────────────────────────────────────────── */
.lrow {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 0.8rem 0;
    border-bottom: 1px solid #CACCC6;
}
.lrow:first-child { border-top: 1px solid #CACCC6; }
.ll { font-size: 0.92rem; color: #5a6370; }
.lv {
    font-family: 'Source Serif 4', serif;
    font-size: 1.35rem;
    font-variant-numeric: tabular-nums;
    color: #16213E;
}

/* ── Section label ────────────────────────────────────────────── */
.slbl {
    font-family: 'Source Serif 4', serif;
    font-size: 1.2rem;
    color: #16213E;
    margin: 2rem 0 0.35rem;
    font-weight: 400;
}

/* ── Risk bars ────────────────────────────────────────────────── */
.rrow { display: flex; align-items: center; margin-bottom: 0.75rem; }
.rlbl { width: 70px; font-size: 0.92rem; color: #5a6370; flex-shrink: 0; }
.rtrack {
    flex-grow: 1;
    height: 10px;
    background: #dddeda;
    border-radius: 2px;
    margin: 0 1rem;
    overflow: hidden;
}
.rfill { height: 100%; border-radius: 2px; }
.rcnt { width: 28px; text-align: right; font-size: 0.92rem; color: #16213E; flex-shrink: 0; }

/* ── Stat card ────────────────────────────────────────────────── */
.stat-card {
    background: #EAEBE6;
    border: 1px solid #CACCC6;
    border-top: 3px solid #A9812E;
    padding: 1.2rem 1.4rem 1rem;
    height: 100%;
}
.stat-label { font-size: 0.85rem; color: #5a6370; margin-bottom: 0.3rem; }
.stat-value {
    font-family: 'Source Serif 4', serif;
    font-size: 2.4rem;
    font-variant-numeric: tabular-nums;
    color: #16213E;
    line-height: 1;
}

/* ── Record card ──────────────────────────────────────────────── */
.rec-hdr {
    background: #EAEBE6;
    border: 1px solid #CACCC6;
    border-top: 3px solid #A9812E;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1.4rem;
}
.rec-name { font-family: 'Source Serif 4', serif; font-size: 2rem; color: #16213E; }
.rec-meta { font-size: 0.92rem; color: #5a6370; margin-top: 0.15rem; }
.risk-tag {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 2px;
    font-size: 0.82rem;
    font-weight: 600;
    color: #F3F3EF;
    margin-top: 0.5rem;
}

/* ── Sidebar title classes ────────────────────────────────────── */
.sb-title {
    font-family: 'Source Serif 4', serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: #fff !important;
    margin: 0 0 0.15rem 0;
    line-height: 1.2;
}
.sb-sub {
    font-size: 0.74rem;
    color: #D8C48F !important;
    margin: 0 0 1rem 0;
    padding-bottom: 0.9rem;
    border-bottom: 1px solid rgba(216,196,143,0.3);
}

/* ── Streamlit widget tweaks ──────────────────────────────────── */
div[data-testid="stPlotlyChart"] { margin: 0 !important; }
div[data-testid="stDataFrame"] { border: 1px solid #CACCC6; border-radius: 2px; }
.stButton > button {
    background: #16213E;
    color: #F3F3EF;
    border: none;
    border-radius: 2px;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.88rem;
    padding: 0.4rem 1rem;
}
.stButton > button:hover { background: #A9812E; color: #16213E; }
div[data-testid="stTextInput"] input {
    background: #EAEBE6 !important;
    border-color: #CACCC6 !important;
}
</style>
""")

# ── Data Loading ───────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_dataset()

students, raw_df, trend = get_data()

for k, v in [("nav", "Overview"), ("student", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.html(
        '<p class="sb-title">Student Success Ledger</p>'
        '<p class="sb-sub">Attendance &amp; risk register</p>'
    )
    nav = st.radio(
        "nav",
        ["Overview", "Student List"],
        label_visibility="collapsed",
        index=["Overview", "Student List"].index(st.session_state.nav),
    )
    st.session_state.nav = nav
    if nav == "Student List" and st.session_state.student is not None:
        pass
    st.caption(f"Academic Ledger prototype  |  {len(students)} students")


# ── Overview ───────────────────────────────────────────────────────────────
def render_overview():
    st.html('<p class="pg-head">Overview</p><hr class="gold-rule">')

    att_mean = trend["pct"].mean() if not trend.empty else 0.0
    if len(trend) >= 7:
        delta = trend["pct"].iloc[-7:].mean() - trend["pct"].iloc[:7].mean()
    else:
        delta = 0.0

    total    = len(students)
    at_risk  = (students.risk_level != "Low").sum()
    avg_gpa  = students.gpa.mean()
    counts   = students.risk_level.value_counts().to_dict()
    arrow    = "&#9650;" if delta >= 0 else "&#9660;"

    # Top row: hero + 3 stat cards
    hero_col, c1, c2, c3 = st.columns([2.2, 1, 1, 1], gap="large")
    with hero_col:
        st.html(
            '<div class="hero-num">%.1f%%</div>'
            '<p class="hero-lbl">Cohort attendance rate (Active Dataset)</p>'
            '<p class="hero-dlt">%s %.1f pts trend change across semester</p>'
            % (att_mean, arrow, abs(delta))
        )
    with c1:
        st.html(h_stat("Total students", str(total)))
    with c2:
        st.html(h_stat("Students at risk", str(at_risk)))
    with c3:
        st.html(h_stat("Average GPA", "%.2f" % avg_gpa))

    st.write("")

    # Bottom row: trend chart + risk bars + summary
    chart_col, risk_col = st.columns([1.6, 1], gap="large")
    with chart_col:
        st.html('<p class="slbl">Cohort Attendance Trend (Jan 2026 – Jun 2026)</p><hr class="hairline">')
        make_chart(trend["date"], trend["pct"], "ov_trend", height=280)

    with risk_col:
        st.html('<p class="slbl">Risk distribution</p><hr class="hairline">')
        st.html(h_risk_bars(counts, total, RISK_COLOR))
        st.html('<p class="slbl" style="margin-top:1.5rem;">Cohort summary</p><hr class="hairline">')
        st.html(h_ledger([
            ("Total students",   str(total)),
            ("Students at risk", str(at_risk)),
            ("Average GPA",      "%.2f" % avg_gpa),
            ("Avg attendance",   "%.1f%%" % att_mean),
        ]))

# ── Student list ───────────────────────────────────────────────────────────
def render_student_list():
    st.html('<p class="pg-head">Student List</p><hr class="gold-rule">')

    sc, fc = st.columns([2.5, 1.5])
    with sc:
        query = st.text_input("Search", placeholder="Search by name or student ID...")
    with fc:
        status_filter = st.multiselect(
            "Status", ["Present", "Absent", "Late", "On Duty", "Unknown"],
            default=["Present", "Absent", "Late", "On Duty", "Unknown"]
        )

    # Use the raw dataset directly — exact columns from CSV
    filtered = raw_df[raw_df.status.isin(status_filter)].copy()
    if query:
        q = query.strip().lower()
        filtered = filtered[
            filtered.student_name.str.lower().str.contains(q, na=False) |
            filtered.student_id.str.lower().str.contains(q, na=False)
        ]

    st.html(
        '<p style="font-size:0.88rem;color:#5a6370;margin-bottom:0.5rem;">%d records</p>'
        % len(filtered)
    )

    # Show exactly the 9 CSV columns
    display_cols = ["student_id", "student_name", "department", "year", "section", "subject", "date", "period", "status"]

    event = st.dataframe(
        filtered[display_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "student_id":    "Student ID",
            "student_name":  "Student Name",
            "department":    "Department",
            "year":          "Year",
            "section":       "Section",
            "subject":       "Subject",
            "date":          "Date",
            "period":        "Period",
            "status":        "Status",
        },
        on_select="rerun",
        selection_mode="single-row",
    )

    if event and event.selection and event.selection.get("rows"):
        idx = event.selection["rows"][0]
        st.session_state.student = filtered.iloc[idx]["student_id"]
        st.rerun()

# ── Router ─────────────────────────────────────────────────────────────────
if st.session_state.student:
    render_student_detail(st.session_state.student, students, raw_df, RISK_COLOR)
elif st.session_state.nav == "Overview":
    render_overview()
else:
    render_student_list()

