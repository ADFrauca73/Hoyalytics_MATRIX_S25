import streamlit as st
import pandas as pd
from datetime import date, timedelta
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

# ─── Page Config ───────────────────────────────────────────
st.set_page_config(page_title="Bond Yield Dashboard", layout="wide", initial_sidebar_state="collapsed")

# ─── Hide Sidebar ──────────────────────────────────────────
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# ─── CSS Styling ───────────────────────────────────────────
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #000000 0%, #072f5f 100%);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}
.stButton > button {
    background-color: #3895d3;
    color: white;
    border: none;
    font-weight: 600;
    padding: 0.6rem 1.5rem;
    border-radius: 6px;
    transition: 0.3s ease-in-out;
}
.stButton > button:hover {
    background-color: #58cced;
    box-shadow: 0 0 10px #58cced, 0 0 20px #58cced;
}
</style>
""", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────
st.markdown("<h1 style='text-align: left; margin-top:2rem;'>Bond Yield Dashboard</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Disclaimer")
    st.write(
        "This tool provides an estimated bond yield and is for educational purposes only. "
        "Please consult a financial advisor before making any investment decisions."
    )
    if st.button("Run Full Prediction"):
        st.switch_page("pages/data1.py")

# ─── Business Day Generation ───────────────────────────────
start_date = pd.to_datetime("2025-03-21").date()
today = date.today()
two_years_later = start_date + timedelta(days=730)

us_bd = CustomBusinessDay(calendar=USFederalHolidayCalendar())
all_business_days = pd.date_range(start=start_date, end=two_years_later, freq=us_bd)
df_all_business_days = pd.DataFrame({'Business Day': all_business_days})

# ─── Date Picker ───────────────────────────────────────────
end_date = st.date_input(
    "Select an end date",
    value=today,
    min_value=today,
    max_value=two_years_later,
    help="You may select any end date within 2 years of the fixed start (March 21, 2025)"
)

# ─── Filter Dates ──────────────────────────────────────────
df_selected_days = df_all_business_days[
    (df_all_business_days["Business Day"] >= pd.to_datetime(start_date)) &
    (df_all_business_days["Business Day"] <= pd.to_datetime(end_date))
]

# ─── Merge with Historical CSV ─────────────────────────────
csv_path = "mnt/data/filtered.csv"
try:
    historical_df = pd.read_csv(csv_path, parse_dates=["date"])
    historical_df.rename(columns={"date": "Business Day"}, inplace=True)
    historical_df.drop(columns=["Unnamed: 0"], inplace=True, errors="ignore")

    merged_df = pd.merge(
        df_selected_days,
        historical_df,
        on="Business Day",
        how="left"
    )
    st.session_state["filtered_df"] = merged_df
    st.success("Historical data successfully merged.")
except Exception as e:
    st.warning(f"Could not load or merge historical data: {e}")
    st.session_state["filtered_df"] = df_selected_days.copy()

# ─── Store base frame if not present ──────────────────────
if "base_df" not in st.session_state:
    st.session_state["base_df"] = df_all_business_days.copy()

# ─── Display Result ───────────────────────────────────────
st.subheader(f"Business Days from {start_date} to {end_date}")
st.dataframe(st.session_state["filtered_df"], use_container_width=True)
