import streamlit as st
from utils.all_tariffs import all_tariffs
import pandas as pd

st.set_page_config(page_title="data1", layout="wide", initial_sidebar_state="collapsed")

hide_nav_style = """
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
"""
st.markdown(hide_nav_style, unsafe_allow_html=True)

# ——— Inject CSS ———
st.markdown("""
<style>
/* Background + Font */
.stApp {
    background: linear-gradient(180deg, #000000 0%, #072f5f 100%);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* Data placeholder box */
.data-box {
    border: 2px solid #58cced;
    border-radius: 10px;
    padding: 4rem;
    margin: 2rem auto;
    text-align: center;
    font-size: 1.3rem;
    color: #cbf0ff;
    max-width: 80%;
}

/* Styled Streamlit buttons */
.stButton > button {
    padding: 0.9rem 2.5rem;
    min-width: 180px;      
    text-align: center;   
    font-size: 1.1rem;
    font-weight: 600;
    background: linear-gradient(to right, #3895d3, #58cced);
    color: white !important;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: background 0.3s ease;
}
.stButton > button:hover {
    background: #58cced !important;
}
.stButton>button:hover {
    background: #58cced !important;
}
</style>
""", unsafe_allow_html=True)

# ——— Data Placeholder ———
st.markdown('<div class="data-box">📊 <strong>Placeholder for Data Display</strong></div>', unsafe_allow_html=True)

# ——— Select tariff dates ———
if "filtered_df" in st.session_state:
    selected_tariffs = [tariff for tariff in st.session_state["filtered_df"].columns if tariff in all_tariffs]
    st.write("Selected Tariffs:", selected_tariffs)
    
    # ——— Dropdown for each selected tariff ———
    if "business_days_df" in st.session_state:
        business_days = st.session_state["business_days_df"]["Business Day"].tolist()
        for tariff in selected_tariffs:
            selected_days = st.multiselect(
                f"Select dates for {tariff}",
                options=business_days,
                key=f"{tariff}_selected_dates"
            )
            
            # Update the filtered_df columns based on selected days
            for day in selected_days:
                st.session_state["filtered_df"].loc[
                    st.session_state["filtered_df"]["Business Day"] == day, tariff
                ] = 1

    st.write("Updated DataFrame:", st.session_state["filtered_df"])
# ——— Navigation Buttons ———
col1, col2, col3 = st.columns([1, 5, 1])

with col1:
    if st.button("⬅️ Previous"):
        st.switch_page("pages/data2.py")

with col3:
    if st.button("Next ➡️"):
        st.switch_page("pages/data4.py")
