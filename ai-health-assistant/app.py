"""
app.py
------
Personal AI Health Assistant — main Streamlit application.
Pages: Dashboard, Nutrition Log, AI Health Coach.
AI processing runs 100% locally through Ollama (see utils/ai_helper.py).

Visual theme: "Fresh Obsidian" — a deep ocean-gradient dark palette
(Obsidian #010C22 -> Midnight Blue #01305A -> Cobalt #024F86 -> Dark
Cyan #048AC1), pulled from a leaf/reef color study. Dark Cyan is the
signal accent throughout. Headings use a bold serif to match the
reference palette's labeling, paired with a clean sans body and a
monospace face for readings. Motion is continuous and noticeable:
staggered card entrances, a traveling pulse-line divider, glowing
button hovers, and breathing status indicators.
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

from utils import ai_helper
from utils import data_analyzer as da
from utils import charts

# --------------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Care Sphere",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

DIET_LOG_PATH = os.path.join("data", "diet_logs.json")
HEALTH_CSV_PATH = "sample_health_data.csv"

# --------------------------------------------------------------------------
# CUSTOM CSS — "Fresh Obsidian" theme
# --------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --obsidian: #010C22;
    --obsidian-2: #011C3B;
    --midnight: #01305A;
    --cobalt: #024F86;
    --cyan: #048AC1;
    --cyan-bright: #21B4E8;
    --cyan-dim: rgba(4,138,193,0.16);
    --surface: rgba(4,138,193,0.07);
    --surface-solid: #011C3B;
    --border: rgba(4,138,193,0.22);
    --border-strong: rgba(33,180,232,0.55);
    --ink: #EAF4FA;
    --ink-soft: #7FA0BE;
    --ink-faint: #4C6580;
    --amber: #F0B429;
    --amber-dim: rgba(240,180,41,0.14);
    --rose: #FF6B81;
    --rose-dim: rgba(255,107,129,0.14);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 85% -10%, rgba(4,138,193,0.16) 0%, transparent 45%),
        radial-gradient(circle at 5% 105%, rgba(2,79,134,0.14) 0%, transparent 42%),
        linear-gradient(180deg, var(--obsidian) 0%, #030F26 55%, var(--obsidian) 100%);
    color: var(--ink);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #00081A;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * {
    color: var(--ink) !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 14.5px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    transition: color 0.15s ease;
}
section[data-testid="stSidebar"] hr {
    border-color: var(--border) !important;
}
section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {
    color: var(--ink-soft) !important;
}

.brand-mark {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'Playfair Display', serif;
    font-size: 21px;
    font-weight: 700;
    letter-spacing: -0.01em;
    padding: 4px 0 2px 0;
}
.brand-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--cyan);
    box-shadow: 0 0 0 0 rgba(4,138,193,0.65);
    animation: pulse-ring 2s ease-out infinite;
    flex-shrink: 0;
}

/* Hide default streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {background: rgba(0,0,0,0);}

/* Cards */
.vital-card {
    position: relative;
    background: linear-gradient(160deg, var(--surface), rgba(1,28,59,0.35));
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 22px 24px;
    margin-bottom: 18px;
    overflow: hidden;
    opacity: 0;
    animation: card-in 0.55s cubic-bezier(0.2, 0.7, 0.3, 1) forwards;
    transition: border-color 0.2s ease, transform 0.25s ease, box-shadow 0.25s ease;
}
.vital-card:nth-of-type(1) { animation-delay: 0.02s; }
.vital-card:nth-of-type(2) { animation-delay: 0.09s; }
.vital-card:nth-of-type(3) { animation-delay: 0.16s; }
.vital-card:nth-of-type(4) { animation-delay: 0.23s; }
.vital-card:nth-of-type(5) { animation-delay: 0.30s; }
.vital-card:nth-of-type(6) { animation-delay: 0.37s; }
.vital-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--card-accent, var(--cyan)), transparent 85%);
    opacity: 0.9;
}
.vital-card:hover {
    border-color: var(--border-strong);
    transform: translateY(-3px);
    box-shadow: 0 14px 34px rgba(4,138,193,0.20);
}

.metric-label {
    font-size: 11.5px;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: var(--ink-soft);
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 32px;
    font-weight: 700;
    color: var(--ink);
    font-family: 'JetBrains Mono', monospace;
    font-variant-numeric: tabular-nums;
    line-height: 1.1;
}
.metric-sub {
    font-size: 12.5px;
    margin-top: 10px;
    font-weight: 500;
    color: var(--ink-soft);
    font-family: 'JetBrains Mono', monospace;
}
.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
    position: relative;
    top: -1px;
    box-shadow: 0 0 0 0 currentColor;
    animation: pulse-ring 2.2s ease-out infinite;
}

/* Page title + animated gradient sheen */
.app-title {
    font-family: 'Playfair Display', serif;
    font-size: 40px;
    font-weight: 700;
    letter-spacing: -0.01em;
    margin-bottom: 2px;
    background: linear-gradient(100deg, #EAF4FA 20%, var(--cyan-bright) 45%, #EAF4FA 65%);
    background-size: 250% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: title-sheen 5s linear infinite;
}
.app-subtitle {
    color: var(--ink-soft);
    font-size: 15px;
    font-family: 'Inter', sans-serif;
    margin-bottom: 4px;
}

/* Signature: live pulse-line divider, animates continuously */
.pulse-divider {
    width: 100%;
    height: 34px;
    margin: 10px 0 26px 0;
    display: block;
    overflow: visible;
}
.pulse-path {
    stroke-dasharray: 1;
    stroke-dashoffset: 1;
    animation: draw-line 1.2s cubic-bezier(0.3, 0.8, 0.3, 1) 0.1s forwards;
}
.pulse-baseline { opacity: 0.22; }
.pulse-dot-travel {
    animation: travel-dot 3.2s ease-in-out 1.3s infinite;
}

.section-heading {
    font-family: 'Playfair Display', serif;
    font-size: 21px;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: var(--ink);
    margin: 26px 0 16px 0;
    border-left: 3px solid var(--cyan);
    padding-left: 12px;
    opacity: 0;
    animation: fade-in-left 0.5s ease-out forwards;
}

/* Chat bubbles */
.chat-bubble-user {
    background: linear-gradient(135deg, var(--cobalt), var(--cyan-bright));
    color: #011224;
    padding: 12px 18px;
    border-radius: 16px 16px 4px 16px;
    margin: 6px 0;
    max-width: 78%;
    margin-left: auto;
    font-weight: 500;
    font-family: 'Inter', sans-serif;
    opacity: 0;
    animation: pop-in 0.32s cubic-bezier(0.2, 0.8, 0.3, 1.15) forwards;
}
.chat-bubble-ai {
    background: var(--surface-solid);
    border: 1px solid var(--border);
    color: var(--ink);
    padding: 12px 18px;
    border-radius: 16px 16px 16px 4px;
    margin: 6px 0;
    max-width: 78%;
    font-family: 'Inter', sans-serif;
    opacity: 0;
    animation: pop-in 0.32s cubic-bezier(0.2, 0.8, 0.3, 1.15) forwards;
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(135deg, var(--cobalt), var(--cyan-bright));
    background-size: 200% auto;
    color: #011224;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
    border: none;
    border-radius: 9px;
    padding: 0.55em 1.4em;
    transition: transform 0.18s ease, box-shadow 0.25s ease, background-position 0.4s ease;
}
div.stButton > button:hover {
    background-position: right center;
    transform: translateY(-2px) scale(1.015);
    box-shadow: 0 8px 24px rgba(4,138,193,0.42);
}
div.stButton > button:active {
    transform: translateY(0px) scale(0.99);
}

/* Tabs */
button[data-baseweb="tab"] {
    transition: color 0.2s ease, border-color 0.2s ease;
}
div[data-baseweb="tab-highlight"] {
    background-color: var(--cyan) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"],
.stNumberInput input, .stDateInput input {
    background: var(--surface-solid) !important;
    color: var(--ink) !important;
    border-radius: 9px !important;
    border: 1px solid var(--border) !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 3px var(--cyan-dim) !important;
}

/* Alerts */
div[data-testid="stAlert"] {
    border-radius: 10px;
    border: 1px solid var(--border);
    background: var(--surface-solid);
    font-family: 'Inter', sans-serif;
    opacity: 0;
    animation: fade-in-up 0.4s ease-out forwards;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.06em;
    font-family: 'JetBrains Mono', monospace;
    transition: transform 0.15s ease;
}
.badge-good { background: var(--cyan-dim); color: var(--cyan-bright); }
.badge-warning { background: var(--amber-dim); color: var(--amber); }
.badge-bad { background: var(--rose-dim); color: var(--rose); }
.badge-neutral { background: rgba(127,160,190,0.14); color: var(--ink-soft); }

/* Delete buttons — rose accent, distinct from the primary action color */
.delete-btn button {
    background: rgba(255,107,129,0.14) !important;
    color: var(--rose) !important;
    border: 1px solid var(--rose-dim) !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}
.delete-btn button:hover {
    background: rgba(255,107,129,0.24) !important;
    color: #FFE1E6 !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(255,107,129,0.25) !important;
}

/* Keyframes */
@keyframes fade-in-up {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fade-in-left {
    from { opacity: 0; transform: translateX(-10px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes card-in {
    from { opacity: 0; transform: translateY(16px) scale(0.98); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes pop-in {
    from { opacity: 0; transform: scale(0.92) translateY(6px); }
    to   { opacity: 1; transform: scale(1) translateY(0); }
}
@keyframes draw-line {
    to { stroke-dashoffset: 0; }
}
@keyframes travel-dot {
    0%   { offset-distance: 0%;   opacity: 0; }
    5%   { opacity: 1; }
    95%  { opacity: 1; }
    100% { offset-distance: 100%; opacity: 0; }
}
@keyframes pulse-ring {
    0%   { box-shadow: 0 0 0 0 currentColor; opacity: 1; }
    70%  { box-shadow: 0 0 0 7px transparent; opacity: 1; }
    100% { box-shadow: 0 0 0 0 transparent; opacity: 1; }
}
@keyframes title-sheen {
    0%   { background-position: 0% center; }
    100% { background-position: -250% center; }
}

@media (prefers-reduced-motion: reduce) {
    .vital-card, .chat-bubble-user, .chat-bubble-ai, div[data-testid="stAlert"], .section-heading {
        animation: none !important;
        opacity: 1 !important;
    }
    .pulse-path { animation: none !important; stroke-dashoffset: 0 !important; }
    .pulse-dot-travel, .brand-dot, .status-dot, .app-title { animation: none !important; }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------------
def load_diet_logs() -> list:
    if not os.path.exists(DIET_LOG_PATH):
        return []
    try:
        with open(DIET_LOG_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_diet_logs(logs: list):
    os.makedirs(os.path.dirname(DIET_LOG_PATH), exist_ok=True)
    with open(DIET_LOG_PATH, "w") as f:
        json.dump(logs, f, indent=2)


def delete_diet_entry(index_in_full_list: int):
    """Remove a single entry from the diet log by its index in the
    full (unsliced) logs list, then persist and rerun."""
    logs = load_diet_logs()
    if 0 <= index_in_full_list < len(logs):
        logs.pop(index_in_full_list)
        save_diet_logs(logs)
    st.rerun()


def delete_health_entry(row_index: int):
    """Remove a single row from the health CSV by its positional index,
    then persist and rerun."""
    df = pd.read_csv(HEALTH_CSV_PATH)
    if 0 <= row_index < len(df):
        df = df.drop(df.index[row_index]).reset_index(drop=True)
        df.to_csv(HEALTH_CSV_PATH, index=False)
    st.rerun()


def pulse_divider(color: str = "#048AC1"):
    """Signature element — a waveform that draws itself in, then keeps
    a small glowing dot traveling along it continuously."""
    st.markdown(
        f"""
        <svg class="pulse-divider" viewBox="0 0 600 34" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
            <path class="pulse-baseline" d="M0,17 L600,17" stroke="{color}" stroke-width="1" stroke-linecap="round"/>
            <path id="pulseTrack" class="pulse-path" pathLength="1"
                  d="M0,17 L235,17 L252,17 L262,4 L272,30 L282,-4 L292,26 L302,17 L600,17"
                  stroke="{color}" stroke-width="2" fill="none"
                  stroke-linecap="round" stroke-linejoin="round"/>
            <circle class="pulse-dot-travel" r="4" fill="{color}"
                    style="offset-path: path('M0,17 L235,17 L252,17 L262,4 L272,30 L282,-4 L292,26 L302,17 L600,17');">
            </circle>
        </svg>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value, unit: str, status: dict, sub_text: str = ""):
    st.markdown(
        f"""
        <div class="vital-card" style="--card-accent: {status['color']};">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}<span style="font-size:14px; font-family:'Inter',sans-serif; font-weight:500; color:var(--ink-soft);"> {unit}</span></div>
            <div class="metric-sub">
                <span class="status-dot" style="background:{status['color']}; color:{status['color']};"></span>
                <span class="badge badge-{status['level']}">{status['level'].upper()}</span>
                &nbsp; {sub_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="brand-mark"><span class="brand-dot"></span>Care Sphere</div>',
        unsafe_allow_html=True,
    )
    st.caption("Running 100% locally via Ollama")
    page = st.radio(
        "Navigate",
        ["Dashboard", "Nutrition Log", "AI Health Coach"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    ollama_ok = ai_helper.is_ollama_running()
    if ollama_ok:
        st.success("Ollama: Connected")
        models = ai_helper.get_installed_models()
        if models:
            st.caption("Installed models: " + ", ".join(models))
        else:
            st.warning("No models pulled yet. Run `ollama pull llama3.2`.")
    else:
        st.error("Ollama: Not reachable")
        st.caption("Start the Ollama app, then refresh this page.")

    st.markdown("---")
    st.caption("Built with Streamlit + Ollama · Private & offline")


# --------------------------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------------------------
health_df = da.load_health_data(HEALTH_CSV_PATH)

# ==========================================================================
# PAGE 1: DASHBOARD
# ==========================================================================
if page == "Dashboard":
    st.markdown('<div class="app-title">Health Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">A snapshot of your recent activity, sleep, and vitals.</div>',
                unsafe_allow_html=True)
    pulse_divider()

    if health_df.empty:
        st.info("No health data yet. Add your first entry below to get started.")
        with st.form("add_entry_form_empty", clear_on_submit=True):
            entry_date = st.date_input("Date")
            col_a, col_b = st.columns(2)
            with col_a:
                steps_in = st.number_input("Steps walked", min_value=0, max_value=50000, value=7000)
                sleep_in = st.number_input("Hours of sleep", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
                hr_in = st.number_input("Resting heart rate (bpm)", min_value=30, max_value=200, value=72)
            with col_b:
                cal_in = st.number_input("Calories burned", min_value=500, max_value=6000, value=2200)
                water_in = st.number_input("Water intake (liters)", min_value=0.0, max_value=6.0, value=2.0, step=0.1)
                mood_in = st.slider("Mood (1 = bad, 10 = great)", min_value=1, max_value=10, value=6)

            submitted = st.form_submit_button("Save First Entry")
            if submitted:
                da.append_entry(HEALTH_CSV_PATH, {
                    "date": entry_date.strftime("%Y-%m-%d"),
                    "steps": steps_in,
                    "sleep_hours": sleep_in,
                    "heart_rate": hr_in,
                    "calories_burned": cal_in,
                    "water_intake_l": water_in,
                    "mood_score": mood_in,
                })
                st.success("Saved! Refreshing dashboard...")
                st.rerun()
    else:
        latest = da.get_latest_metrics(health_df)
        weekly = da.weekly_summary(health_df)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            status = da.get_status("steps", latest["steps"])
            change = weekly.get("steps", {}).get("pct_change", 0)
            metric_card("Steps Today", f"{int(latest['steps']):,}", "steps", status,
                        f"{change:+.1f}% vs last week")
        with col2:
            status = da.get_status("sleep_hours", latest["sleep_hours"])
            change = weekly.get("sleep_hours", {}).get("pct_change", 0)
            metric_card("Sleep", f"{latest['sleep_hours']}", "hrs", status,
                        f"{change:+.1f}% vs last week")
        with col3:
            status = da.get_status("heart_rate", latest["heart_rate"])
            change = weekly.get("heart_rate", {}).get("pct_change", 0)
            metric_card("Resting Heart Rate", f"{int(latest['heart_rate'])}", "bpm", status,
                        f"{change:+.1f}% vs last week")
        with col4:
            status = da.get_status("mood_score", latest["mood_score"])
            change = weekly.get("mood_score", {}).get("pct_change", 0)
            metric_card("Mood Score", f"{int(latest['mood_score'])}", "/ 10", status,
                        f"{change:+.1f}% vs last week")

        st.markdown('<div class="section-heading">Trends</div>', unsafe_allow_html=True)

        if len(health_df) < 2:
            st.info("Add at least 2 entries (different dates) to see trend charts here.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="vital-card">', unsafe_allow_html=True)
                st.plotly_chart(charts.steps_chart(health_df), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="vital-card">', unsafe_allow_html=True)
                st.plotly_chart(charts.sleep_chart(health_df), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            c3, c4 = st.columns(2)
            with c3:
                st.markdown('<div class="vital-card">', unsafe_allow_html=True)
                st.plotly_chart(charts.heart_rate_chart(health_df), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c4:
                st.markdown('<div class="vital-card">', unsafe_allow_html=True)
                corr = da.compute_correlations(health_df)
                st.plotly_chart(charts.correlation_heatmap(corr), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="vital-card">', unsafe_allow_html=True)
            st.plotly_chart(charts.multi_metric_chart(health_df), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("View raw data table"):
            st.dataframe(health_df, use_container_width=True)

        st.markdown('<div class="section-heading">Add a New Entry</div>', unsafe_allow_html=True)
        with st.expander("Enter today's (or someone's) health numbers"):
            with st.form("add_entry_form", clear_on_submit=True):
                entry_date = st.date_input("Date")
                col_a, col_b = st.columns(2)
                with col_a:
                    steps_in = st.number_input("Steps walked", min_value=0, max_value=50000, value=7000,
                                                help="Total steps taken that day")
                    sleep_in = st.number_input("Hours of sleep", min_value=0.0, max_value=14.0, value=7.0, step=0.1,
                                                help="How many hours they slept the night before")
                    hr_in = st.number_input("Resting heart rate (bpm)", min_value=30, max_value=200, value=72,
                                             help="Heart beats per minute while resting — most fitness trackers show this")
                with col_b:
                    cal_in = st.number_input("Calories burned", min_value=500, max_value=6000, value=2200,
                                              help="Estimated total calories burned that day")
                    water_in = st.number_input("Water intake (liters)", min_value=0.0, max_value=6.0, value=2.0, step=0.1,
                                                help="Total water drunk that day, in liters")
                    mood_in = st.slider("Mood (1 = bad, 10 = great)", min_value=1, max_value=10, value=6)

                submitted = st.form_submit_button("Save Entry")
                if submitted:
                    da.append_entry(HEALTH_CSV_PATH, {
                        "date": entry_date.strftime("%Y-%m-%d"),
                        "steps": steps_in,
                        "sleep_hours": sleep_in,
                        "heart_rate": hr_in,
                        "calories_burned": cal_in,
                        "water_intake_l": water_in,
                        "mood_score": mood_in,
                    })
                    st.success("Saved! Refreshing dashboard...")
                    st.rerun()

        st.markdown('<div class="section-heading">Delete an Entry</div>', unsafe_allow_html=True)
        with st.expander("Remove an entry from your health log"):
            options = [
                f"{row['date']} · {int(row['steps'])} steps · {row['sleep_hours']}h sleep · {int(row['heart_rate'])} bpm"
                for _, row in health_df.iterrows()
            ]
            selected_label = st.selectbox("Choose the entry to delete", options, key="delete_health_select")
            selected_idx = options.index(selected_label)
            st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
            if st.button("🗑️ Delete This Entry", key="delete_health_btn"):
                delete_health_entry(selected_idx)
            st.markdown('</div>', unsafe_allow_html=True)


# ==========================================================================
# PAGE 2: NUTRITION LOG
# ==========================================================================
elif page == "Nutrition Log":
    st.markdown('<div class="app-title">Nutrition Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Log meals by photo or text — analyzed locally by Ollama.</div>',
                unsafe_allow_html=True)
    pulse_divider("#01305A")

    tab1, tab2 = st.tabs(["Photo Analyzer", "Type a Food"])

    with tab1:
        st.markdown('<div class="vital-card">', unsafe_allow_html=True)
        st.write("Upload a photo of your meal. Requires a vision model like `llava` pulled in Ollama.")
        uploaded_image = st.file_uploader("Upload food photo", type=["jpg", "jpeg", "png"])
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded meal", width=320)
            if st.button("Analyze Photo", key="analyze_photo_btn"):
                with st.spinner("Asking the local vision model... (first run can take a minute or two)"):
                    result = ai_helper.analyze_food_image(uploaded_image.getvalue())
                st.markdown(result)

                logs = load_diet_logs()
                logs.append({
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "type": "image",
                    "input": uploaded_image.name,
                    "analysis": result,
                })
                save_diet_logs(logs)
                st.success("Saved to your nutrition log.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="vital-card">', unsafe_allow_html=True)
        st.write("No vision model installed, or prefer typing? Describe your meal below.")
        food_text = st.text_area("What did you eat?", placeholder="e.g. Grilled chicken breast with rice and broccoli")
        if st.button("Analyze Food", key="analyze_text_btn"):
            if food_text.strip():
                with st.spinner("Asking the local model..."):
                    result = ai_helper.analyze_food_text(food_text)
                st.markdown(result)

                logs = load_diet_logs()
                logs.append({
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "type": "text",
                    "input": food_text,
                    "analysis": result,
                })
                save_diet_logs(logs)
                st.success("Saved to your nutrition log.")
            else:
                st.warning("Type something first!")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Recent Entries</div>', unsafe_allow_html=True)
    logs = load_diet_logs()
    if not logs:
        st.info("No entries yet. Log a meal above to get started.")
    else:
        recent = logs[-15:]
        offset = len(logs) - len(recent)  # index of recent[0] in the full logs list
        for i in range(len(recent) - 1, -1, -1):
            entry = recent[i]
            full_index = offset + i
            card_col, btn_col = st.columns([9, 1])
            with card_col:
                st.markdown(f"""
                <div class="vital-card">
                    <div class="metric-label">{entry['timestamp']} · {entry['type'].upper()}</div>
                    <div style="font-weight:700; margin:4px 0 8px 0; font-family:'Playfair Display', serif; font-size:18px;">{entry['input']}</div>
                    <div style="color:var(--ink-soft); font-size:14px; white-space:pre-wrap; font-family:'Inter',sans-serif;">{entry['analysis']}</div>
                </div>
                """, unsafe_allow_html=True)
            with btn_col:
                st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_diet_{full_index}", help="Delete this entry"):
                    delete_diet_entry(full_index)
                st.markdown('</div>', unsafe_allow_html=True)


# ==========================================================================
# PAGE 3: AI HEALTH COACH
# ==========================================================================
elif page == "AI Health Coach":
    st.markdown('<div class="app-title">AI Health Coach</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Chat about your health data — powered by your local Ollama model.</div>',
                unsafe_allow_html=True)
    pulse_divider("#024F86")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    health_context = da.build_context_string(health_df)
    with st.expander("Health context being sent to the AI"):
        st.text(health_context)

    for msg in st.session_state.chat_history:
        bubble_class = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-ai"
        align = "flex-end" if msg["role"] == "user" else "flex-start"
        st.markdown(
            f'<div style="display:flex; justify-content:{align};">'
            f'<div class="{bubble_class}">{msg["content"]}</div></div>',
            unsafe_allow_html=True,
        )

    user_input = st.chat_input("Ask your coach anything about your health, sleep, or diet...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("Your coach is thinking..."):
            reply = ai_helper.chat_with_coach(
                user_input,
                st.session_state.chat_history[:-1],
                health_context,
            )
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("Clear conversation"):
            st.session_state.chat_history = []
            st.rerun()