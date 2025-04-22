import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="graph", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        180deg,
        #000000 0%,
        #072f5f 100%
    );
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* Button Flash Hover Effect */
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
    transition: 0.2s ease-in-out;
}
</style>
""", unsafe_allow_html=True)

# Title top-left
st.markdown("<h1 style='text-align: left; margin-top: 2rem;'>Bond Yield Dashboard</h1>", unsafe_allow_html=True)

# Model section label
st.markdown(
    """
    <div style="
        margin-top: 1rem;
        font-size: 20px;
        color: #cbf0ff;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border-left: 4px solid #58cced;
        background-color: rgba(255,255,255,0.05);
        border-radius: 6px;
        width: fit-content;
    ">
    """,
    unsafe_allow_html=True
)

# Split content evenly across screen width
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Disclaimer")
    st.write(
        "This tool provides an estimated bond yield and is for educational purposes only. "
        "Please consult a financial advisor before making any investment decisions."
    )
    if st.button("Run Full Prediction"):
        st.switch_page("pages/data1.py")

with col2:
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
            One Day Prediction (Placeholder)
        </div>
        """,
        unsafe_allow_html=True
    )
