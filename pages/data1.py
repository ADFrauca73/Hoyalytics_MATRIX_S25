import streamlit as st
import pandas as pd

st.set_page_config(page_title="Select Variables", layout="wide", initial_sidebar_state="collapsed")

# ─── Hide the sidebar nav ─────────────────────────────────────────────
st.markdown("<style>[data-testid='stSidebarNav']{display:none;}</style>", unsafe_allow_html=True)

# ─── CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background: linear-gradient(180deg,#000 0%,#072f5f 100%); color:white; font-family:'Segoe UI',sans-serif; }
  .page-title { font-size:3rem; font-weight:800; margin-bottom:1.5rem; }
  .section-title { font-size:1.5rem; font-weight:600; margin-bottom:0.75rem; color:#cbf0ff; }
  .stButton>button {
      background: linear-gradient(90deg,#3895d3,#58cced)!important;
      color:white!important; font-weight:600; padding:0.75rem 2rem;
      border:none!important; border-radius:6px!important; width:100%;
      transition:box-shadow 0.2s ease-in-out;
  }
  .stButton>button:hover { box-shadow:0 0 10px #58cced,0 0 20px #58cced; }
</style>
""", unsafe_allow_html=True)

# ─── The ONE place we define all tariffs ─────────────────────────────
all_tariffs = [
    "Chapter 39 – Plastics and articles thereof",
    "Chapter 40 – Rubber and articles thereof",
    "Chapter 72 – Iron and steel",
    "Chapter 73 – Articles of iron or steel",
    "Chapter 74 – Copper and articles thereof",
    "Chapter 75 – Nickel and articles thereof",
    "Chapter 76 – Aluminum and articles thereof",
    "Chapter 78 – Lead and articles thereof",
    "Chapter 79 – Zinc and articles thereof",
    "Chapter 80 – Tin and articles thereof",
    "Chapter 81 – Other base metals; cermets; articles thereof",
    "Chapter 82 – Tools, implements, cutlery, spoons and forks, of base metal",
    "Chapter 83 – Miscellaneous articles of base metal",
    "Chapter 84 – Nuclear reactors, boilers, machinery and mechanical appliances",
    "Chapter 85 – Electrical machinery and equipment; sound recorders and reproducers, etc.",
    "Chapter 86 – Railway or tramway locomotives, rolling-stock, and parts",
    "Chapter 87 – Vehicles other than railway or tramway rolling-stock",
    "Chapter 88 – Aircraft, spacecraft, and parts thereof",
    "Chapter 89 – Ships, boats, and floating structures",
    "Chapter 90 – Optical, photographic, cinematographic, measuring, checking, precision, medical instruments",
    "Chapter 96 – Miscellaneous manufactured articles",
    "Chapter 98 – Special classification provisions (e.g., U.S. goods returned, duty exemptions)"
]

# ─── Initialize session state ──────────────────────────────────────────
if "selected_vars" not in st.session_state:
    st.session_state["selected_vars"] = []
if "selected_tariffs" not in st.session_state:
    st.session_state["selected_tariffs"] = []
if "filtered_df" not in st.session_state:
    st.session_state["filtered_df"] = None

# ─── Page header ───────────────────────────────────────────────────────
st.markdown("<div class='page-title'>Select Variables & Tariffs</div>", unsafe_allow_html=True)
left_col, right_col = st.columns([3, 2], gap="large")

# ─── Variable selection ───────────────────────────────────────────────
with left_col:
    st.markdown("<div class='section-title'>Include these:</div>", unsafe_allow_html=True)
    var_opts = ["Consumer Sentiment / VIX", "M1 Supply", "Inflation / FFR"]
    new_vars = st.multiselect(
        "Select variables",
        options=var_opts,
        default=st.session_state["selected_vars"]
    )

# ─── Tariff selection (for page 3’s calendar) ─────────────────────────
with right_col:
    st.markdown("<div class='section-title'>Choose tariffs:</div>", unsafe_allow_html=True)
    new_tariffs = st.multiselect(
        "Select one or more tariff chapters",
        options=all_tariffs,
        default=st.session_state["selected_tariffs"]
    )

# ─── Apply Selections ─────────────────────────────────────────────────
if st.button("Apply Selections", use_container_width=True):
    st.session_state["selected_vars"]    = new_vars
    st.session_state["selected_tariffs"] = new_tariffs

    if st.session_state["filtered_df"] is None:
        st.warning("No business-day data found. Please run the Dashboard page first.")
    else:
        # Start fresh from date-only
        df = st.session_state["filtered_df"][["Business Day"]].copy()

        # 1) Add all tariffs first (after the date column)
        for tariff in all_tariffs:
            df[tariff] = 0

        # 2) Then add any selected macro-variables
        if "Consumer Sentiment / VIX" in new_vars:
            df["Consumer Sentiment"] = 0
            df["VIX"]               = 0
        if "M1 Supply" in new_vars:
            df["M1 Supply"] = 0
        if "Inflation / FFR" in new_vars:
            df["Inflation"] = 0
            df["FFR"]       = 0

        st.session_state["filtered_df"] = df
        st.success("All tariffs (zeros) added, then your variables appended.")

# ─── Preview & Navigation ─────────────────────────────────────────────
if st.session_state["filtered_df"] is not None:
    st.dataframe(st.session_state["filtered_df"], use_container_width=True)

c1, _, c2 = st.columns([1, 6, 1])
with c1:
    if st.button("⬅️ Previous"):
        st.switch_page("pages/Dashboard.py")
with c2:
    if st.button("Next ➡️"):
        st.switch_page("pages/data2.py")
