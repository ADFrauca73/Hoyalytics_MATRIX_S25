import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Final Data Overview",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Hide Sidebar Nav ─────────────────────────────────────
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# ─── Styling ──────────────────────────────────────────────
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #000000 0%, #072f5f 100%);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}
.page-title {
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 1.5rem;
    color: #cbf0ff;
}
.stDataFrame {
    background: #001e3c;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ─── Title ────────────────────────────────────────────────
st.markdown("<div class='page-title'>📊 Final Combined Data Preview</div>", unsafe_allow_html=True)

# ─── Show Final DataFrame ─────────────────────────────────
if "filtered_df" in st.session_state:
    df = st.session_state["filtered_df"]
    st.dataframe(df, use_container_width=True)
else:
    st.warning("⚠️ No data found. Please run the Dashboard page first.")

# ─── Navigation ───────────────────────────────────────────
c1, _, c2 = st.columns([1, 6, 1])
with c1:
    if st.button("⬅️ Previous"):
        st.switch_page("pages/data5.py")
with c2:
    if st.button("Predictions"):
        st.switch_page("pages/newtester.py")

