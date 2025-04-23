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

st.markdown(
    "<div class='section-title'>Enter Consumer Sentiment and VIX Data</div>",
    unsafe_allow_html=True
)

# ─── Load & Validate Data ─────────────────────────────────
if "filtered_df" not in st.session_state:
    st.error("No business day data found. Please run the Dashboard page first.")
    st.stop()

# Copy & index by Business Day
df = st.session_state["filtered_df"].copy()
df["Business Day"] = pd.to_datetime(df["Business Day"])
df.set_index("Business Day", inplace=True)

today = pd.to_datetime(date.today())

# ─── Ensure Columns Exist ────────────────────────────────
for col in ["diff_CSD", "VIX_close"]:
    if col not in df.columns:
        df[col] = np.nan
df["diff_CSD"]  = pd.to_numeric(df["diff_CSD"], errors="coerce")
df["VIX_close"] = pd.to_numeric(df["VIX_close"], errors="coerce")

# ─── Define Editable Range ───────────────────────────────
editable_mask = df.index >= today
editable_df   = df.loc[editable_mask]

# ─── Build Input UI ───────────────────────────────────────
inputs = {}
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='label-title'>Date</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='label-title'>Cumulative CSD</div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='label-title'>VIX Close</div>", unsafe_allow_html=True)

for i, (day, row) in enumerate(editable_df.iterrows()):
    date_str = day.strftime("%Y-%m-%d")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='date-box'>{date_str}</div>", unsafe_allow_html=True)
    with c2:
        csd_cum = st.number_input(
            "CSD", key=f"cs_{i}", label_visibility="collapsed",
            value=float(row["diff_CSD"]) if not np.isnan(row["diff_CSD"]) else 0.0,
            format="%.2f"
        )
    with c3:
        vix = st.number_input(
            "VIX", key=f"vix_{i}", label_visibility="collapsed",
            value=float(row["VIX_close"]) if not np.isnan(row["VIX_close"]) else 0.0,
            format="%.2f"
        )
    inputs[date_str] = {"cum_CSD": csd_cum, "VIX_close": vix}

# ─── Save & Process ───────────────────────────────────────
_, center, _ = st.columns([4,1,4])
with center:
    if st.button("Save Data"):
        # 1) Gather raw cumulative CSD inputs (0.0 → NaN for interpolate)
        raw_cum = {
            pd.to_datetime(dstr): vals["cum_CSD"] if vals["cum_CSD"] != 0.0 else np.nan
            for dstr, vals in inputs.items()
        }

        # 2) Build a Series over every editable date
        cum_series = pd.Series(raw_cum).reindex(editable_df.index)

        # 3) Interpolate forward & fill leading NaNs with 0 (just like VIX)
        cum_series = (
            cum_series
            .interpolate(method="linear", limit_direction="forward")
            .fillna(0.0)
        )

        # 4) Compute diff_CSD as day-over-day delta of that smooth curve
        diff_series = cum_series.diff().fillna(cum_series)

        # 5) Write diff_CSD back into DataFrame
        df.loc[editable_mask, "diff_CSD"] = diff_series.values

        # 6) Overwrite VIX inputs and interpolate as before
        df.loc[editable_mask, "VIX_close"] = [
            inputs[d.strftime("%Y-%m-%d")]["VIX_close"]
            for d in editable_df.index
        ]
        v = df.loc[editable_mask, "VIX_close"].replace(0, np.nan)
        df.loc[editable_mask, "VIX_close"] = (
            v.interpolate(method="linear", limit_direction="forward")
             .fillna(0)
        )

        # 7) Commit & preview
        df.reset_index(inplace=True)
        st.session_state["filtered_df"] = df
        st.success(
            "Data saved:\n"
            "- `diff_CSD` interpolated on your cumulative inputs and then differenced\n"
            "- `VIX_close` forward‐interpolated over gaps"
        )
        st.markdown("### Preview")
        st.dataframe(df, use_container_width=True)

# ─── Navigation ───────────────────────────────────────────
c1, _, c2 = st.columns([1,6,1])
with c1:
    if st.button("⬅️ Previous"):
        st.switch_page("pages/data1.py")
with c2:
    if st.button("Next ➡️"):
        st.switch_page("pages/data3.py")
############### DO NOT FUCKING CHANGE THIS LINE ###############