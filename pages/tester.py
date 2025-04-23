import streamlit as st
import pandas as pd

from utils.unpickling import YieldForecastCalculator

# Set up the page configuration
st.set_page_config(page_title="Tester Page", layout="wide", initial_sidebar_state="collapsed")

# Hide the sidebar navigation
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# Page title
st.title("Tester Page")

# Ensure required session state data exists
if "filtered_df" not in st.session_state:
    st.error("No data found. Please complete the previous steps.")
    st.stop()

# Perform yield prediction calculations
st.subheader("Yield Prediction Results")
try:
    # Initialize the YieldForecastCalculator with the filtered DataFrame
    filtered_df = st.session_state["filtered_df"]
    calculator = YieldForecastCalculator(filtered_df)

    # Get the forecasted yields
    forecasts = calculator.get_forecast()
    prediction_intervals = calculator.get_prediction_intervals()

    # Display the forecasted yields
    for maturity, forecast in forecasts.items():
        st.write(f"### {maturity} Yield Forecast")
        st.line_chart(forecast)

    # Plot the forecasts with confidence intervals
    st.subheader("Yield Forecast Graphs")
    calculator.plot_forecasts()

except Exception as e:
    st.error(f"An error occurred during yield prediction: {e}")

# Navigation buttons
col1, _, col2 = st.columns([1, 6, 1])
with col1:
    if st.button("⬅️ Previous", key="prev_btn"):
        st.switch_page("pages/data3.py")
with col2:
    if st.button("Next ➡️", key="next_btn"):
        st.write("Next page functionality not implemented yet.")
