import streamlit as st
import pandas as pd
import numpy as np


st.set_page_config(page_title="graph", layout="centered")

# Hoyalytics branding 
st.markdown(
    """
    <div style="
        margin-top: 2rem;
        font-size: 20px;
        color: #cbf0ff;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border-left: 4px solid #58cced;
        background-color: rgba(255,255,255,0.05);
        border-radius: 6px;
        width: fit-content;
    ">
        stInsert the Model here:
    </div>
    """,
    unsafe_allow_html=True
)

st.title("Bond Yield Dashboard")
st.subheader("Powered by Me after Uber")


st.sidebar.header("Input Parameters")
face_value = st.sidebar.number_input("Face Value ($)", value=1000)
coupon_rate = st.sidebar.number_input("Coupon Rate (%)", value=5.0, step=0.1)
years_to_maturity = st.sidebar.slider("Years to Maturity", min_value=1, max_value=30, value=10)
market_price = st.sidebar.number_input("Market Price", value=950)
tax_rate = st.sidebar.number_input("Tax Rate (%)", value=100)

if st.sidebar.button("Predict Yield"):
    coupon_payment = face_value * (coupon_rate / 100)
    estimated_yield = (coupon_payment + (face_value - market_price) / years_to_maturity) / ((face_value + market_price) / 2) #random code for the button

    st.markdown("### Estimated Bond Yield")
    st.markdown(
        f"<div style='font-size: 24px; background-color:#0066cc; color:white; padding:10px; border-radius:8px; width:fit-content;'>{estimated_yield * 100:.2f}%</div>",
        unsafe_allow_html=True
    )

st.markdown("Insert the Model here: \n")
