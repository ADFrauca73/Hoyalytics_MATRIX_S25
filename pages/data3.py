import streamlit as st
import pandas as pd
import platform
import subprocess
import sys

# ─── Install streamlit-calendar if needed ─────────────────────────────
try:
    from streamlit_calendar import calendar
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "streamlit-calendar"], check=True)
    from streamlit_calendar import calendar

# ─── Setup ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Tariff Calendar", layout="wide", initial_sidebar_state="collapsed")

# ─── Styles ────────────────────────────────────────────────────────────
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
.fc { font-size: 0.65rem !important; }
.fc .fc-toolbar-title { font-size: 0.8rem !important; }
.fc .fc-daygrid-day-number { font-size: 0.7rem !important; }
.fc .fc-event-title { font-size: 0.65rem !important; }
</style>
""", unsafe_allow_html=True)

# ─── Hardcoded Descriptive Tariff Mapping ─────────────────────────────
label_mapping = {
    "Chapter 39 – Plastics and articles thereof": "start_tariff_39",
    "Chapter 40 – Rubber and articles thereof": "start_tariff_40",
    "Chapter 72 – Iron and steel": "start_tariff_72",
    "Chapter 73 – Articles of iron or steel": "start_tariff_73",
    "Chapter 74 – Copper and articles thereof": "start_tariff_74",
    "Chapter 75 – Nickel and articles thereof": "start_tariff_75",
    "Chapter 76 – Aluminum and articles thereof": "start_tariff_76",
    "Chapter 78 – Lead and articles thereof": "start_tariff_78",
    "Chapter 79 – Zinc and articles thereof": "start_tariff_79",
    "Chapter 80 – Tin and articles thereof": "start_tariff_80",
    "Chapter 81 – Other base metals; cermets; articles thereof": "start_tariff_81",
    "Chapter 82 – Tools, implements, cutlery, spoons and forks, of base metal": "start_tariff_82",
    "Chapter 83 – Miscellaneous articles of base metal": "start_tariff_83",
    "Chapter 84 – Nuclear reactors, boilers, machinery and mechanical appliances": "start_tariff_84",
    "Chapter 85 – Electrical machinery and equipment; sound recorders and reproducers, etc.": "start_tariff_85",
    "Chapter 86 – Railway or tramway locomotives, rolling-stock, and parts": "start_tariff_86",
    "Chapter 87 – Vehicles other than railway or tramway rolling-stock": "start_tariff_87",
    "Chapter 88 – Aircraft, spacecraft, and parts thereof": "start_tariff_88",
    "Chapter 89 – Ships, boats, and floating structures": "start_tariff_89",
    "Chapter 90 – Optical, photographic, cinematographic, measuring, checking, precision, medical instruments": "start_tariff_90",
    "Chapter 96 – Miscellaneous manufactured articles": "start_tariff_96",
    "Chapter 98 – Special classification provisions (e.g., U.S. goods returned, duty exemptions)": "start_tariff_98"
}
column_to_label = {v: k for k, v in label_mapping.items()}

# ─── Page Content ─────────────────────────────────────────────────────
st.title("Tariff Implementation Dates")
st.write("Click dates on the calendar for each tariff to mark them for implementation.")

# ─── Preconditions ────────────────────────────────────────────────────
if "filtered_df" not in st.session_state or "base_df" not in st.session_state:
    st.error("Missing required data. Please run the Dashboard page first.")
    st.stop()

# Copy data
df = st.session_state["filtered_df"].copy()
base_df = st.session_state["base_df"].copy()

# Prepare dates
business_dates = pd.to_datetime(base_df["Business Day"]).dt.date.tolist()
df["Business Day"] = pd.to_datetime(df["Business Day"]).dt.date

selected_tariffs = st.session_state.get("selected_tariffs", [])

# ─── Init picks ────────────────────────────────────────────────────────
if "calendar_picks" not in st.session_state:
    st.session_state["calendar_picks"] = {}

# ─── Calendar UI ───────────────────────────────────────────────────────
if not selected_tariffs:
    st.warning("No tariffs selected. Please return to the Variables page and choose tariffs to use the calendar.")
else:
    for tariff in selected_tariffs:
        label = column_to_label.get(tariff, tariff)
        st.markdown(f"<div class='tariff-label'>{label}</div>", unsafe_allow_html=True)

        # Load previous picks
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

        # Record clicks
        if result and result.get("dateClick") and result["dateClick"].get("date"):
            selected_date = pd.to_datetime(result["dateClick"]["date"]).date()
            if selected_date in business_dates:
                st.session_state["calendar_picks"].setdefault(tariff, [])
                if selected_date not in st.session_state["calendar_picks"][tariff]:
                    st.session_state["calendar_picks"][tariff].append(selected_date)

# ─── Save + Clear Buttons ─────────────────────────────────────────────
save_col, clear_col = st.columns([1, 1])

with save_col:
    if st.button("💾 Save Selections"):
        changed = []
        picks = st.session_state["calendar_picks"]
        for tariff, days in picks.items():
            if tariff not in df.columns:
                df[tariff] = 0
            for day in days:
                mask = df["Business Day"] == day
                if not mask.any():
                    continue
                if df.loc[mask, tariff].values[0] != 1:
                    df.loc[mask, tariff] = 1
                    changed.append((tariff, day))
        st.session_state["filtered_df"] = df
        if changed:
            st.success("✅ Tariff dates updated:")
            for t, d in changed:
                label = column_to_label.get(t, t)
                st.markdown(f"- **{label}** on **{d}** ➝ `1`")
        else:
            st.info("No new changes were made.")
        st.markdown("### 🧪 Filtered Data Preview")
        preview = df[df[selected_tariffs].sum(axis=1) > 0] if selected_tariffs else df
        st.dataframe(preview, use_container_width=True)

with clear_col:
    if st.button("🗑️ Clear All Selections"):
        st.session_state["calendar_picks"] = {}
        st.experimental_rerun()

# ─── Navigation ───────────────────────────────────────────────────────
c1, _, c3 = st.columns([1, 5, 1])
with c1:
    if st.button("⬅️ Previous", key="prev_btn"):
        st.switch_page("pages/data2.py")
with c3:
    if st.button("Next ➡️", key="next_btn"):
        st.switch_page("pages/date4.py")
