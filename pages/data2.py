import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

st.set_page_config(
    page_title="Consumer Sentiment & VIX",
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

st.markdown("<div class='section-title'>Enter Consumer Sentiment and VIX Data</div>", unsafe_allow_html=True)

# ─── Load & Validate ──────────────────────────────────────
if "filtered_df" not in st.session_state:
    st.error("No business day data found. Please run the Dashboard page first.")
    st.stop()

df = st.session_state["filtered_df"].copy()
df["Business Day"] = pd.to_datetime(df["Business Day"])
df.set_index("Business Day", inplace=True)

today = pd.to_datetime(date.today())
editable_df = df.loc[df.index >= today]

if editable_df.empty:
    st.info("All dates have data through yesterday. Nothing to input today.")
    st.stop()

# ─── Monthly / Daily Toggle ───────────────────────────────
if "monthly_inputs" not in st.session_state:
    st.session_state.monthly_inputs = False

label = "Switch to Monthly Inputs" if not st.session_state.monthly_inputs else "Switch to Daily Inputs"
if st.button(label):
    st.session_state.monthly_inputs = not st.session_state.monthly_inputs

if st.session_state.monthly_inputs:
    input_df = editable_df.groupby(editable_df.index.to_period("M")).head(1)
else:
    input_df = editable_df

# ─── Input Grid ───────────────────────────────────────────
inputs = {}
st.markdown(
    "<div style='display:flex'>"
    "<div class='label-title' style='flex:1'>Date</div>"
    "<div class='label-title' style='flex:1'>CSD Level</div>"
    "<div class='label-title' style='flex:1'>VIX Close</div>"
    "</div>",
    unsafe_allow_html=True
)

for i, (biz_day, _) in enumerate(input_df.iterrows()):
    ds = biz_day.strftime("%Y-%m-%d")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='date-box'>{ds}</div>", unsafe_allow_html=True)
    with c2:
        csd = st.number_input(
            label=f"csd_{ds}",
            key=f"csd_{i}",
            value=0.0,
            format="%.2f",
            label_visibility="collapsed"
        )
    with c3:
        vix = st.number_input(
            label=f"vix_{ds}",
            key=f"vix_{i}",
            value=0.0,
            format="%.2f",
            label_visibility="collapsed"
        )
    inputs[ds] = {"csd": csd, "vix": vix}

# ─── Save & Process ───────────────────────────────────────
_, center, _ = st.columns([4,1,4])
with center:
    if st.button("Save Data"):
        index = editable_df.index
        csd_series = pd.Series(index=index, dtype=float)
        vix_series = pd.Series(index=index, dtype=float)

        for ds, vals in inputs.items():
            dt = pd.to_datetime(ds)
            if dt in index:
                csd_series.loc[dt] = vals["csd"] if vals["csd"] != 0.0 else np.nan
                vix_series.loc[dt] = vals["vix"] if vals["vix"] != 0.0 else np.nan

        # Interpolate levels → get differences
        csd_interp = csd_series.interpolate(method="linear", limit_direction="both").fillna(0.0)
        diff_csd = csd_interp.diff().fillna(csd_interp)

        vix_interp = vix_series.interpolate(method="linear", limit_direction="forward").ffill().fillna(0.0)

        df.loc[index, "diff_CSD"] = diff_csd.values
        df.loc[index, "VIX_close"] = vix_interp.values

        df_reset = df.reset_index()
        st.session_state["filtered_df"] = df_reset

        st.success("CSD and VIX data saved and processed.")
        st.markdown("### Preview")
        st.dataframe(df_reset, use_container_width=True)

        csv_data = df_reset.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Updated Data as CSV",
            data=csv_data,
            file_name="vix_csd_output.csv",
            mime="text/csv"
        )

# ─── Navigation ───────────────────────────────────────────
c1, _, c2 = st.columns([1, 6, 1])
with c1:
    if st.button("⬅️ Previous"):
        st.switch_page("pages/data1.py")
with c2:
    if st.button("Next ➡️"):
        st.switch_page("pages/data3.py")

############### DO NOT FUCKING CHANGE THIS LINE ###############
