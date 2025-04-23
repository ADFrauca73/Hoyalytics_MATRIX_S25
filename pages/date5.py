import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

st.set_page_config(
    page_title="Enter M1 Supply",
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
    "<div class='section-title'>Enter M1 Supply Data</div>",
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

# ─── Ensure Column Exists ────────────────────────────────
if "diff_M1_supply" not in df.columns:
    df["diff_M1_supply"] = np.nan
df["diff_M1_supply"] = pd.to_numeric(df["diff_M1_supply"], errors="coerce")

# ─── Define Editable Range ───────────────────────────────
editable_mask = df.index >= today
editable_df   = df.loc[editable_mask]

# ─── Build Input UI ───────────────────────────────────────
inputs = {}
col1, col2 = st.columns(2)
with col1:
    st.markdown("<div class='label-title'>Date</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='label-title'>M1 Supply Level</div>", unsafe_allow_html=True)

for i, (day, row) in enumerate(editable_df.iterrows()):
    date_str = day.strftime("%Y-%m-%d")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='date-box'>{date_str}</div>", unsafe_allow_html=True)
    with c2:
        m1 = st.number_input(
            "M1 Supply", key=f"m1_{i}", label_visibility="collapsed",
            value=0.0, format="%.2f"
        )
    inputs[date_str] = {"M1": m1}

# ─── Save & Process ───────────────────────────────────────
_, center, _ = st.columns([4,1,4])
with center:
    if st.button("Save Data"):
        raw_m1 = {
            pd.to_datetime(d): v["M1"] if v["M1"] != 0.0 else np.nan
            for d, v in inputs.items()
        }

        level_m1 = pd.Series(raw_m1).reindex(editable_df.index).interpolate(method="linear", limit_direction="forward").fillna(0.0)
        diff_m1 = level_m1.diff().fillna(level_m1)

        df.loc[editable_mask, "diff_M1_supply"] = diff_m1.values

        df.reset_index(inplace=True)
        st.session_state["filtered_df"] = df
        st.success("M1 Supply levels interpolated; differences stored in `diff_M1_supply`.")
        st.markdown("### Preview")
        st.dataframe(df[["Business Day", "diff_M1_supply"]], use_container_width=True)

# ─── Navigation ───────────────────────────────────────────
c1, _, c2 = st.columns([1,6,1])
with c1:
    if st.button("⬅️ Previous"):
        st.switch_page("pages/data4.py")
with c2:
    if st.button("Next ➡️"):
        st.switch_page("pages/data6.py")

############### DO NOT FUCKING CHANGE THIS LINE ###############
