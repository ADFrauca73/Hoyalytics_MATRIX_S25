import streamlit as st
import pandas as pd

st.set_page_config(page_title="Select Variables", layout="wide")

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

# ─── Title ───────────────────────────────────────────────────────────────
st.markdown("<div class='page-title'>Select Variables to Display</div>", unsafe_allow_html=True)

# ─── Layout ──────────────────────────────────────────────────────────────
left_col, right_col = st.columns([3, 2], gap="large")

# Variables Section
with left_col:
    st.markdown("<div class='section-title'>📊 Include these:</div>", unsafe_allow_html=True)
    all_vars = ["Consumer Sentiment", "VIX", "M1 Supply", "Inflation / FFR"]
    selected_vars = []

    for var in all_vars:
        if st.checkbox(var, value=var in st.session_state.get("selected_vars", [])):
            selected_vars.append(var)

    st.session_state["selected_vars"] = selected_vars
    st.markdown(f"**Currently selected:** {', '.join(selected_vars) if selected_vars else 'None'}")

# Tariff Section
with right_col:
    st.markdown("<div class='section-title'>📂 Tariffs Detail</div>", unsafe_allow_html=True)
    all_tariffs = ["Tariff A", "Tariff B", "Tariff C"]
    selected_tariffs = st.multiselect("Choose a tariff", options=["None"] + all_tariffs)

    # Remove "None" if others are selected
    if "None" in selected_tariffs and len(selected_tariffs) > 1:
        selected_tariffs.remove("None")
    elif "None" in selected_tariffs:
        selected_tariffs = []

    st.session_state["selected_tariffs"] = selected_tariffs

# ——— Apply to DataFrame ———
if "filtered_df" in st.session_state:
    df = st.session_state["filtered_df"].copy()

    # Drop all columns that might have been previously added
    for col in all_vars + all_tariffs:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # Add selected vars and tariffs as new 0-filled columns
    for col in selected_vars + selected_tariffs:
        df[col] = 0

    st.dataframe(df)

    # Optional: update stored df
    st.session_state["filtered_df"] = df
else:
    st.warning("No business day data found. Please run the Dashboard page first.")

# Nav buttons
col1, _, col2 = st.columns([1, 6, 1])
with col1:
    if st.button("⬅️ Previous"):
        st.switch_page("pages/Dashboard.py")
with col2:
    if st.button("Next ➡️"):
        st.switch_page("pages/data3.py")
