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

st.markdown("<div class='section-title'>Enter M1 Supply Data</div>", unsafe_allow_html=True)

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

# ─── Monthly/Daily Toggle ────────────────────────────────
if "monthly_inputs_m1" not in st.session_state:
    st.session_state.monthly_inputs_m1 = False

label = "Switch to Monthly Inputs" if not st.session_state.monthly_inputs_m1 else "Switch to Daily Inputs"
if st.button(label):
    st.session_state.monthly_inputs_m1 = not st.session_state.monthly_inputs_m1

# ─── Define Editable Range ───────────────────────────────
editable_mask = df.index >= today
editable_df = df.loc[editable_mask]

if st.session_state.monthly_inputs_m1:
    input_df = editable_df.groupby(editable_df.index.to_period("M")).head(1)
else:
    input_df = editable_df

# ─── Build Input UI ───────────────────────────────────────
inputs = {}
col1, col2 = st.columns(2)
with col1:
    st.markdown("<div class='label-title'>Date</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='label-title'>M1 Supply Level</div>", unsafe_allow_html=True)

for i, (day, row) in enumerate(input_df.iterrows()):
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

        level_m1 = (
            pd.Series(raw_m1)
            .reindex(editable_df.index)
            .interpolate(method="linear", limit_direction="forward")
            .fillna(0.0)
        )
        diff_m1 = level_m1.diff().fillna(level_m1)

        df.loc[editable_mask, "diff_M1_supply"] = diff_m1.values

        df.reset_index(inplace=True)
        st.session_state["filtered_df"] = df

        st.success("M1 Supply differences saved.")
        st.markdown("### Full Dataset Preview")
        st.dataframe(df, use_container_width=True)

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Full Dataset as CSV",
            data=csv_data,
            file_name="full_dataset_with_m1.csv",
            mime="text/csv"
        )

# ─── Navigation ───────────────────────────────────────────
c1, _, c2 = st.columns([1,6,1])
with c1:
    if st.button("⬅️ Previous"):
        st.switch_page("pages/ffr_entry.py")
with c2:
    if st.button("Next ➡️"):
        st.switch_page("pages/preview.py")

############### DO NOT FUCKING CHANGE THIS LINE ###############
