import streamlit as st
import pandas as pd
import platform
import subprocess
import sys
from utils.all_tariffs import all_tariffs

# ─── Install calendar component if needed ──────────────────────
try:
    from streamlit_calendar import calendar
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "streamlit-calendar"])
    from streamlit_calendar import calendar

# ─── Setup ──────────────────────────────────────────────────────
st.set_page_config(page_title="Tariff Calendar", layout="wide", initial_sidebar_state="collapsed")

# Page + Calendar-Only Font Shrinking Styles
st.markdown("""
<style>
    [data-testid="stSidebarNav"] { display: none; }
    .stApp {
        background: linear-gradient(180deg, #000000 0%, #072f5f 100%);
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        background: linear-gradient(to right, #3895d3, #58cced);
        color: white !important;
        border: none;
        border-radius: 8px;
        cursor: pointer;
    }
    .stButton>button:hover {
        box-shadow: 0 0 10px #58cced, 0 0 20px #58cced;
    }
    .tariff-label {
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 1rem;
        color: #cbf0ff;
    }

    /* Smaller calendar font size */
    .fc {
        font-size: 0.65rem !important;
    }
    .fc .fc-toolbar-title {
        font-size: 0.8rem !important;
    }
    .fc .fc-daygrid-day-number {
        font-size: 0.7rem !important;
    }
    .fc .fc-event-title {
        font-size: 0.65rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Tariff Implementation Dates")
st.write("Click dates on the calendar for each tariff to mark them for implementation.")

# ─── Preconditions ──────────────────────────────────────────────
if "filtered_df" not in st.session_state or "business_days_df" not in st.session_state:
    st.error("Missing business-day data. Please run the Dashboard page first.")
    st.stop()

df = st.session_state["filtered_df"]
business_dates = pd.to_datetime(st.session_state["business_days_df"]["Business Day"]).dt.date.tolist()
df["Business Day"] = pd.to_datetime(df["Business Day"]).dt.date

selected_tariffs = st.session_state.get("selected_tariffs", [])
if not selected_tariffs:
    st.error("No tariffs selected. Please return to the Variables page and choose tariffs.")
    st.stop()

# ─── Initialize state ────────────────────────────────────────────
if "calendar_picks" not in st.session_state:
    st.session_state["calendar_picks"] = {}

# ─── Render calendar for each tariff ─────────────────────────────
for tariff in selected_tariffs:
    st.markdown(f"<div class='tariff-label'>{tariff}</div>", unsafe_allow_html=True)

    # Pre-load previously selected dates as calendar events
    events = []
    existing = st.session_state["calendar_picks"].get(tariff, [])
    for d in existing:
        events.append({"title": "Marked", "start": str(d), "color": "#58cced"})

    options = {
        "initialView": "dayGridMonth",
        "editable": True,
        "selectable": True,
        "selectMirror": True,
        "dayMaxEvents": True,
        "events": events,
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay"
        },
        "aspectRatio": 1.4,
        "contentHeight": 300
    }

    with st.container():
        st.markdown('<div style="width: 360px; margin-bottom: 0;">', unsafe_allow_html=True)
        result = calendar(key=f"{tariff}_calendar", options=options)
        st.markdown('</div>', unsafe_allow_html=True)

    # Get date from calendar click result
    if result and "dateClick" in result and "date" in result["dateClick"]:
        selected_date = pd.to_datetime(result["dateClick"]["date"]).date()
        if selected_date in business_dates:
            st.session_state["calendar_picks"].setdefault(tariff, [])
            if selected_date not in st.session_state["calendar_picks"][tariff]:
                st.session_state["calendar_picks"][tariff].append(selected_date)

# ─── Debug View of Stored Picks ─────────────────────────────────
st.markdown("### 🧪 Picked Dates by Tariff")
st.write(st.session_state["calendar_picks"])

# ─── Save and Clear Logic ───────────────────────────────────────
save_col, clear_col = st.columns([1, 1])
with save_col:
    if st.button("💾 Save Selections"):
        changed = []
        picks = st.session_state["calendar_picks"]
        for tariff, days in picks.items():
            for day in days:
                mask = df["Business Day"] == day
                if not mask.any():
                    continue
                if df.loc[mask, tariff].values[0] != 1:
                    df.loc[mask, tariff] = 1
                    changed.append((tariff, str(day)))
        st.session_state["filtered_df"] = df
        if changed:
            st.success("✅ Tariff dates updated:")
            for t, d in changed:
                st.markdown(f"- **{t}** on **{d}** ➝ `1`")
        else:
            st.info("No new changes were made.")
        st.markdown("### 🧪 Filtered Data Preview")
        st.dataframe(df[df[selected_tariffs].sum(axis=1) > 0])

with clear_col:
    if st.button("🗑️ Clear All Selections"):
        st.session_state["calendar_picks"] = {}
        st.experimental_rerun()

# ─── Navigation ──────────────────────────────────────────────────
c1, _, c3 = st.columns([1, 5, 1])
with c1:
    if st.button("⬅️ Previous", key="prev_btn"):
        st.switch_page("pages/data2.py")
with c3:
    if st.button("Next ➡️", key="next_btn"):
        st.switch_page("pages/tester.py")
