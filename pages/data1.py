import streamlit as st
import pandas as pd
from utils.all_tariffs import all_tariffs

st.set_page_config(page_title="Select Variables", layout="wide", initial_sidebar_state="collapsed")

hide_nav_style = """
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
"""
st.markdown(hide_nav_style, unsafe_allow_html=True)

# ─── CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #000000 0%, #072f5f 100%);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}
.page-title {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 1.5rem;
}
.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
    color: #cbf0ff;
    display: flex; align-items: center; gap: 0.5rem;
}
.card {
    background-color: rgba(255,255,255,0.05);
    border-left: 4px solid #58cced;
    border-radius: 6px;
    padding: 1rem 1.5rem;
    margin-bottom: 2rem;
}
.stButton > button {
    background: linear-gradient(90deg, #3895d3, #58cced) !important;
    color: white !important;
    font-weight: 600;
    padding: 0.75rem 2rem;
    border: none !important;
    border-radius: 6px !important;
    transition: box-shadow 0.2s ease-in-out;
    width: 100%;
}
.stButton > button:hover {
    box-shadow: 0 0 10px #58cced, 0 0 20px #58cced;
}
</style>
""", unsafe_allow_html=True)

# ─── Initialize session state ───────────────────────────────────────────
if "selected_vars" not in st.session_state:
    st.session_state["selected_vars"] = []
if "selected_tariffs" not in st.session_state:
    st.session_state["selected_tariffs"] = []
if "filtered_df" not in st.session_state:
    st.session_state["filtered_df"] = None

# ─── UI Layout ───────────────────────────────────────────────────────────
st.markdown("<div class='page-title'>Select Variables to Display</div>", unsafe_allow_html=True)
left_col, right_col = st.columns([3, 2], gap="large")

# ─── Variable selection ─────────────────────────────────────────────────
with left_col:
    st.markdown("<div class='section-title'>Include these:</div>", unsafe_allow_html=True)
    all_options = ["Consumer Sentiment / VIX", "M1 Supply", "Inflation / FFR"]
    new_var_selection = st.multiselect(
        "Select variables",
        options=all_options,
        default=st.session_state["selected_vars"]
    )

# ─── Tariff selection ───────────────────────────────────────────────────
with right_col:
    st.markdown("<div class='section-title'>Tariffs Detail</div>", unsafe_allow_html=True)
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
    new_tariff_selection = st.multiselect("Choose a tariff", options=["None"] + all_tariffs, default=st.session_state["selected_tariffs"])
    if "None" in new_tariff_selection and len(new_tariff_selection) > 1:
        new_tariff_selection.remove("None")
    elif "None" in new_tariff_selection:
        new_tariff_selection = []

# ─── Apply changes manually ─────────────────────────────────────────────
if st.button("Apply Selections", use_container_width=True):
    st.session_state["selected_vars"] = new_var_selection
    st.session_state["selected_tariffs"] = new_tariff_selection

    if st.session_state["filtered_df"] is not None:
        df = st.session_state["filtered_df"][["Business Day"]].copy()

        if "Consumer Sentiment / VIX" in new_var_selection:
            df["Consumer Sentiment"] = 0
            df["VIX"] = 0
        if "Inflation / FFR" in new_var_selection:
            df["Inflation"] = 0
            df["FFR"] = 0
        if "M1 Supply" in new_var_selection:
            df["M1 Supply"] = 0

        for tariff in new_tariff_selection:
            df[tariff] = 0

        st.session_state["filtered_df"] = df
        st.success("Selections applied to dataset.")
    else:
        st.warning("No business day data found. Please run the Dashboard page first.")

# ─── Show updated dataframe ─────────────────────────────────────────────
if st.session_state["filtered_df"] is not None:
    st.dataframe(st.session_state["filtered_df"])

# ─── Nav buttons ─────────────────────────────────────────────────────────
col1, _, col2 = st.columns([1, 6, 1])
with col1:
    if st.button("⬅️ Previous", key="prev"):
        st.switch_page("pages/Dashboard.py")
with col2:
    if st.button("Next ➡️", key="next"):
        st.switch_page("pages/data2.py")
