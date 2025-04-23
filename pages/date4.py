import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

st.set_page_config(
    page_title="Enter FFR & Inflation",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Hide Sidebar ─────────────────────────────────────────
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# ─── Styling ──────────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background: linear-gradient(180deg,#000 0%,#072f5f 100%); color: white; font-family: 'Segoe UI', sans-serif; }
  .section-title { font-size:1.75rem; font-weight:700; color:#cbf0ff; margin-bottom:1.5rem; }
  .label-title { font-weight:600; font-size:1rem; color:#cbf0ff; text-align:center; padding-bottom:0.5rem; }
  .date-box {
    background: rgba(0,0,0,0.7); border-left:4px solid #58cced; border-radius:6px;
    padding:0.5rem; color:#cbf0ff; text-align:center; margin-bottom:0.4rem; font-weight:600;
  }
  .stButton>button {
    background:linear-gradient(90deg,#3895d3,#58cced);
    color:white!important; font-weight:600; padding:0.6rem 2rem;
    border:none; border-radius:6px;
  }
  .stButton>button:hover { box-shadow:0 0 10px #58cced,0 0 20px #58cced; }
</style>
""", unsafe_allow_html=True)

st.markdown(
    "<div class='section-title'>Enter FFR and Inflation Data</div>",
    unsafe_allow_html=True
)

# ─── Load & Validate Data ─────────────────────────────────
if "filtered_df" not in st.session_state:
    st.error("No business day data found. Please run the Dashboard page first.")
    st.stop()

df = st.session_state["filtered_df"].copy()
df["Business Day"] = pd.to_datetime(df["Business Day"])
df.set_index("Business Day", inplace=True)

today = pd.to_datetime(date.today())

# ─── Ensure Columns Exist ────────────────────────────────
for col in ["diff_FFR", "diff_CPI"]:
    if col not in df.columns:
        df[col] = np.nan
df["diff_FFR"] = pd.to_numeric(df["diff_FFR"], errors="coerce")
df["diff_CPI"] = pd.to_numeric(df["diff_CPI"], errors="coerce")

# ─── Define Editable Range ───────────────────────────────
editable_mask = df.index >= today
editable_df   = df.loc[editable_mask]

# ─── Build Input UI ───────────────────────────────────────
inputs = {}
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='label-title'>Date</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='label-title'>FFR Level</div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='label-title'>Inflation (CPI) Level</div>", unsafe_allow_html=True)

for i, (day, row) in enumerate(editable_df.iterrows()):
    date_str = day.strftime("%Y-%m-%d")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='date-box'>{date_str}</div>", unsafe_allow_html=True)
    with c2:
        ffr = st.number_input(
            "FFR", key=f"ffr_{i}", label_visibility="collapsed",
            value=0.0, format="%.2f"
        )
    with c3:
        cpi = st.number_input(
            "CPI", key=f"cpi_{i}", label_visibility="collapsed",
            value=0.0, format="%.2f"
        )
    inputs[date_str] = {"FFR": ffr, "CPI": cpi}

# ─── Save & Process ───────────────────────────────────────
_, center, _ = st.columns([4,1,4])
with center:
    if st.button("Save Data"):
        # 1) Treat zero as 'not entered'
        raw_ffr = {
            pd.to_datetime(d): v["FFR"] if v["FFR"] != 0.0 else np.nan
            for d, v in inputs.items()
        }
        raw_cpi = {
            pd.to_datetime(d): v["CPI"] if v["CPI"] != 0.0 else np.nan
            for d, v in inputs.items()
        }

        # 2) Interpolate forward and fill early NaNs with 0
        level_ffr = pd.Series(raw_ffr).reindex(editable_df.index).interpolate(method="linear", limit_direction="forward").fillna(0.0)
        level_cpi = pd.Series(raw_cpi).reindex(editable_df.index).interpolate(method="linear", limit_direction="forward").fillna(0.0)

        # 3) Compute differences and store in diff columns
        diff_ffr = level_ffr.diff().fillna(level_ffr)
        diff_cpi = level_cpi.diff().fillna(level_cpi)

        df.loc[editable_mask, "diff_FFR"] = diff_ffr.values
        df.loc[editable_mask, "diff_CPI"] = diff_cpi.values

        # 4) Commit
        df.reset_index(inplace=True)
        st.session_state["filtered_df"] = df
        st.success("FFR and CPI levels interpolated; differences stored in diff_FFR and diff_CPI.")
        st.markdown("### Preview")
        st.dataframe(df[["Business Day", "diff_FFR", "diff_CPI"]], use_container_width=True)

# ─── Navigation ───────────────────────────────────────────
c1, _, c2 = st.columns([1,6,1])
with c1:
    if st.button("⬅️ Previous"):
        st.switch_page("pages/data3.py")
with c2:
    if st.button("Next ➡️"):
        st.switch_page("pages/date5.py")

############### DO NOT FUCKING CHANGE THIS LINE ###############
