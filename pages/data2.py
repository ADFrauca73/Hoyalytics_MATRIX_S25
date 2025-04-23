import streamlit as st
import pandas as pd

st.set_page_config(page_title="data1", layout="wide", initial_sidebar_state="collapsed")

# ─── Hide Sidebar Navigation ───────────────────────────────
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# ─── Custom Styling ───────────────────────────────────────
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

st.markdown("<div class='section-title'>Enter Consumer Sentiment and VIX Data</div>", unsafe_allow_html=True)

# ─── Load & Validate Data ─────────────────────────────────
if "filtered_df" not in st.session_state:
    st.error("No business day data found. Please run the Dashboard page first.")
    st.stop()

df = st.session_state["filtered_df"].copy()
df["Business Day"] = pd.to_datetime(df["Business Day"])

# Ensure columns exist
for col in ["Consumer Sentiment", "VIX"]:
    if col not in df.columns:
        df[col] = pd.NA

df["Consumer Sentiment"] = pd.to_numeric(df["Consumer Sentiment"], errors="coerce")
df["VIX"] = pd.to_numeric(df["VIX"], errors="coerce")

# ─── Ask for previous‐day sentiment ───────────────────────────
first_date = df["Business Day"].min().strftime("%Y-%m-%d")
prev_sentiment = st.number_input(
    f"Consumer Sentiment on the day before {first_date}",
    value=50.0,
    step=None,
    format="%.2f",
    help="This is your 'day 0' baseline, used to compute the first delta."
)

# ─── User Input Interval Selection ────────────────────────
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
    st.markdown("<div class='label-title'>Consumer Sentiment</div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='label-title'>VIX</div>", unsafe_allow_html=True)

for i, row in display_df.iterrows():
    date_str = row["Business Day"].strftime("%Y-%m-%d")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='date-box'>{date_str}</div>", unsafe_allow_html=True)
    with c2:
        sent = st.number_input(
            "Consumer Sentiment", label_visibility="collapsed",
            key=f"sentiment_{i}",
            value=float(row["Consumer Sentiment"]) if pd.notna(row["Consumer Sentiment"]) else 50.0,
            step=None, format="%.2f"
        )
    with c3:
        vix = st.number_input(
            "VIX", label_visibility="collapsed",
            key=f"vix_{i}",
            value=float(row["VIX"]) if pd.notna(row["VIX"]) else 20.0,
            step=None, format="%.2f"
        )
    inputs[date_str] = {"Consumer Sentiment": sent, "VIX": vix}

# ─── Save, Interpolate & Difference ───────────────────────
_, center, _ = st.columns([4,1,4])
with center:
    if st.button("Save Data", key="save"):
        # Clear existing
        df["Consumer Sentiment"] = pd.NA
        df["VIX"] = pd.NA

        # Fill user inputs
        for _, row in display_df.iterrows():
            ds = row["Business Day"].strftime("%Y-%m-%d")
            df.loc[df["Business Day"] == row["Business Day"], "Consumer Sentiment"] = inputs[ds]["Consumer Sentiment"]
            df.loc[df["Business Day"] == row["Business Day"], "VIX"] = inputs[ds]["VIX"]

        # Interpolate raw series
        df["Consumer Sentiment"] = pd.to_numeric(df["Consumer Sentiment"], errors="coerce").interpolate(method="linear")
        df["VIX"] = pd.to_numeric(df["VIX"], errors="coerce").interpolate(method="linear")

        # Compute day-over-day changes, using prev_sentiment for the first delta
        raw = df["Consumer Sentiment"].tolist()
        changes = [raw[0] - prev_sentiment] + [raw[i] - raw[i-1] for i in range(1, len(raw))]
        df["Consumer Sentiment"] = changes

        # Save back and preview
        st.session_state["filtered_df"] = df
        st.success("Consumer Sentiment converted to daily changes; VIX remains level.")
        st.markdown("### Preview")
        st.dataframe(df[["Business Day", "Consumer Sentiment", "VIX"]].reset_index(drop=True))

# ─── Navigation Buttons ───────────────────────────────────
c1, _, c2 = st.columns([1,6,1])
with c1:
    if st.button("⬅️ Previous", key="prev_btn"):
        st.switch_page("pages/data1.py")
with c2:
    if st.button("Next ➡️", key="next_btn"):
        st.switch_page("pages/data3.py")
