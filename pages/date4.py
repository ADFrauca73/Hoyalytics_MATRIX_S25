import streamlit as st
import pandas as pd

st.set_page_config(page_title="data2", layout="wide", initial_sidebar_state="collapsed")

# ─── Hide Sidebar Navigation ───────────────────────────────
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# ─── Page Styling ──────────────────────────────────────────
st.markdown("""
<style>
  .stApp {
    background: linear-gradient(180deg, #000000 0%, #072f5f 100%);
    color: white;
    font-family: 'Segoe UI', sans-serif;
  }
  .section-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: #cbf0ff;
    margin-bottom: 1.5rem;
  }
  input[type=number] {
    appearance: textfield;
    width: 100% !important;
  }
  .date-box {
    background-color: rgba(0, 0, 0, 0.7);
    border-left: 4px solid #58cced;
    border-radius: 6px;
    padding: 0.5rem 0;
    font-weight: 600;
    font-size: 1rem;
    color: #cbf0ff;
    text-align: center;
    margin-bottom: 0.4rem;
  }
  .label-title {
    font-weight: 600;
    font-size: 1rem;
    color: #cbf0ff;
    text-align: center;
    padding-bottom: 0.5rem;
  }
  .stButton > button {
    background: linear-gradient(90deg, #3895d3, #58cced);
    color: white !important;
    font-weight: 600;
    padding: 0.6rem 2rem;
    border: none;
    border-radius: 6px;
  }
  .stButton > button:hover {
    box-shadow: 0 0 10px #58cced, 0 0 20px #58cced;
  }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='section-title'>Enter FFR and Inflation Data</div>", unsafe_allow_html=True)

# ─── Load & Validate Data ─────────────────────────────────
if "filtered_df" not in st.session_state:
    st.error("No business day data found. Please run the Dashboard page first.")
    st.stop()

df = st.session_state["filtered_df"].copy()
df["Business Day"] = pd.to_datetime(df["Business Day"])

# Ensure required columns exist
for col in ["FFR", "Inflation"]:
    if col not in df.columns:
        df[col] = pd.NA

df["FFR"] = pd.to_numeric(df["FFR"], errors="coerce")
df["Inflation"] = pd.to_numeric(df["Inflation"], errors="coerce")

# ─── Ask for day-before values ────────────────────────────
first_date = df["Business Day"].min().strftime("%Y-%m-%d")

prev_ffr = st.number_input(
    f"FFR on the day before {first_date}",
    value=0.0,
    step=None,
    format="%.2f"
)

prev_inflation = st.number_input(
    f"Inflation on the day before {first_date}",
    value=0.0,
    step=None,
    format="%.2f"
)

# ─── Frequency selection ──────────────────────────────────
spacing_options = {
    "2 weeks": pd.Timedelta(weeks=2),
    "Half month": pd.Timedelta(days=15),
    "3 months": pd.DateOffset(months=3),
    "6 months": pd.DateOffset(months=6),
    "12 months": pd.DateOffset(months=12),
    "All": None
}

min_date, max_date = df["Business Day"].min(), df["Business Day"].max()
valid_options = []
for label, offset in spacing_options.items():
    if offset is None:
        valid_options.append(label)
    else:
        count, temp = 0, min_date
        while temp <= max_date:
            count += 1
            temp += offset
        if count <= len(df):
            valid_options.append(label)

time_range = st.selectbox("How frequently would you like to enter data?", valid_options)
spacing = spacing_options[time_range]

# ─── Filter Dates to Display ──────────────────────────────
if spacing is None:
    display_df = df.copy()
else:
    spaced = []
    current = min_date
    while current <= max_date:
        match = df[df["Business Day"] >= current]
        if not match.empty:
            spaced.append(match.iloc[0]["Business Day"])
        current += spacing
    if max_date not in spaced:
        spaced.append(max_date)
    display_df = df[df["Business Day"].isin(spaced)].copy()

# ─── Input Interface ──────────────────────────────────────
inputs = {}
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='label-title'>Date</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='label-title'>FFR</div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='label-title'>Inflation</div>", unsafe_allow_html=True)

for i, row in display_df.iterrows():
    date_str = row["Business Day"].strftime("%Y-%m-%d")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='date-box'>{date_str}</div>", unsafe_allow_html=True)
    with c2:
        ffr = st.number_input(
            "FFR", label_visibility="collapsed",
            key=f"ffr_{i}",
            value=float(row["FFR"]) if pd.notna(row["FFR"]) else 0.0,
            step=None, format="%.2f"
        )
    with c3:
        inf = st.number_input(
            "Inflation", label_visibility="collapsed",
            key=f"infl_{i}",
            value=float(row["Inflation"]) if pd.notna(row["Inflation"]) else 0.0,
            step=None, format="%.2f"
        )
    inputs[date_str] = {"FFR": ffr, "Inflation": inf}

# ─── Save, Interpolate, and Compute Deltas ────────────────
_, center, _ = st.columns([4, 1, 4])
with center:
    if st.button("Save Data", key="save"):
        df["FFR"] = pd.NA
        df["Inflation"] = pd.NA

        for _, row in display_df.iterrows():
            ds = row["Business Day"].strftime("%Y-%m-%d")
            df.loc[df["Business Day"] == row["Business Day"], "FFR"] = inputs[ds]["FFR"]
            df.loc[df["Business Day"] == row["Business Day"], "Inflation"] = inputs[ds]["Inflation"]

        df["FFR"] = pd.to_numeric(df["FFR"], errors="coerce").interpolate(method="linear")
        df["Inflation"] = pd.to_numeric(df["Inflation"], errors="coerce").interpolate(method="linear")

        # Day-over-day differences
        ffr_raw = df["FFR"].tolist()
        ffr_delta = [ffr_raw[0] - prev_ffr] + [ffr_raw[i] - ffr_raw[i-1] for i in range(1, len(ffr_raw))]

        infl_raw = df["Inflation"].tolist()
        infl_delta = [infl_raw[0] - prev_inflation] + [infl_raw[i] - infl_raw[i-1] for i in range(1, len(infl_raw))]

        df["FFR"] = ffr_delta
        df["Inflation"] = infl_delta

        st.session_state["filtered_df"] = df
        st.success("FFR and Inflation converted to day-over-day changes.")
        st.markdown("### Preview")
        st.dataframe(df[["Business Day", "FFR", "Inflation"]].reset_index(drop=True))

# ─── Navigation Buttons ───────────────────────────────────
c1, _, c2 = st.columns([1, 6, 1])
with c1:
    if st.button("⬅️ Previous", key="prev_btn"):
        st.switch_page("pages/data1.py")
with c2:
    if st.button("Next ➡️", key="next_btn"):
        st.switch_page("pages/data3.py")
