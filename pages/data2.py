import streamlit as st
import pandas as pd

st.set_page_config(page_title="data1", layout="wide", initial_sidebar_state="collapsed")

hide_nav_style = """
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
"""
st.markdown(hide_nav_style, unsafe_allow_html=True)

# Inject styling
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
input[type=number]::-webkit-inner-spin-button, 
input[type=number]::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
}
input[type=number] {
    appearance: textfield;
    width: 100% !important;
}
/* Date box styling */
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
/* Input labels */
.label-title {
    font-weight: 600;
    font-size: 1rem;
    color: #cbf0ff;
    text-align: center;
    padding-bottom: 0.5rem;
}
/* Button styling */
.stButton > button {
    background: linear-gradient(90deg, #3895d3, #58cced);
    color: white !important;
    font-weight: 600;
    padding: 0.6rem 2rem;
    border: none;
    border-radius: 6px;
    transition: box-shadow 0.2s ease-in-out;
}
.stButton > button:hover {
    box-shadow: 0 0 10px #58cced, 0 0 20px #58cced;
}
</style>
""", unsafe_allow_html=True)

# Page header
st.markdown("<div class='section-title'>Enter Consumer Sentiment and VIX Data</div>", unsafe_allow_html=True)

# Load filtered business days dataframe
if "filtered_df" not in st.session_state:
    st.error("No business day data found. Please run the Dashboard page first.")
else:
    df = st.session_state["filtered_df"]

    # Ensure columns exist
    for col in ["Consumer Sentiment", "VIX"]:
        if col not in df.columns:
            df[col] = 0.0

    inputs = {}

    # Top row labels
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='label-title'>Date</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='label-title'>Consumer Sentiment</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='label-title'>VIX</div>", unsafe_allow_html=True)

    # Input rows
    for i, row in df.iterrows():
        date_str = row["Business Day"].strftime("%Y-%m-%d")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"<div class='date-box'>{date_str}</div>", unsafe_allow_html=True)
        with col2:
            sentiment = st.number_input(
                label="Consumer Sentiment",
                label_visibility="collapsed",
                key=f"sentiment_{i}",
                value=float(df.at[i, "Consumer Sentiment"]),
                step=None,
                format="%.2f"
            )
        with col3:
            vix = st.number_input(
                label="VIX",
                label_visibility="collapsed",
                key=f"vix_{i}",
                value=float(df.at[i, "VIX"]),
                step=None,
                format="%.2f"
            )

        inputs[date_str] = {"Consumer Sentiment": sentiment, "VIX": vix}

    # Globally centered Save Data button
left_spacer, center, right_spacer = st.columns([4, 1, 4])
with center:
    if st.button("Save Data", key="save"):
        for i, row in df.iterrows():
            date_str = row["Business Day"].strftime("%Y-%m-%d")
            df.at[i, "Consumer Sentiment"] = inputs[date_str]["Consumer Sentiment"]
            df.at[i, "VIX"] = inputs[date_str]["VIX"]
        st.session_state["filtered_df"] = df
        st.success("Data updated successfully.")

# Navigation Buttons
col1, _, col2 = st.columns([1, 6, 1])
with col1:
    if st.button("⬅️ Previous", key="prev_btn"):
        st.switch_page("pages/data1.py")
with col2:
    if st.button("Next ➡️", key="next_btn"):
        st.switch_page("pages/data3.py")
