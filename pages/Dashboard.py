import streamlit as st
import pandas as pd
from datetime import date, timedelta
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

st.set_page_config(page_title="graph", layout="wide")

no_sidebar_style = """
    <style>
        div[data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(no_sidebar_style, unsafe_allow_html=True)

# ————— GLOBAL CSS INJECTION —————
st.markdown("""
<style>
/* —— App background & text —————————————————— */
.stApp {
    background: linear-gradient(180deg, #000000 0%, #072f5f 100%);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* —— Button styling —————————————————————— */
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

/* —— MUI DatePicker: selected day ————————————————— */
.MuiPickersDay-root.Mui-selected {
    background-color: #3895d3 !important;
    color: white !important;
}
/* hover over that selected day */
.MuiPickersDay-root.Mui-selected:hover {
    background-color: #58cced !important;
}

/* —— MUI DatePicker: any day hover ———————————————— */
.MuiPickersDay-root:hover {
    background-color: #58cced !important;
    color: white !important;
}

/* —— Calendar nav arrows ————————————————————— */
.MuiSvgIcon-root {
    color: #58cced !important;
}

/* —— Input outline when focused ———————————————— */
.MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline {
    border-color: #58cced !important;
    box-shadow: 0 0 0 0.2rem rgba(88,204,237,0.25) !important;
}

/* —— Neutralize the HTML5 “error” state border ——————— */
.MuiFormControl-root.Mui-error .MuiOutlinedInput-notchedOutline {
    border-color: #58cced !important;
    box-shadow: 0 0 0 0.2rem rgba(88,204,237,0.25) !important;
}
</style>
""", unsafe_allow_html=True)


# ————— Title —————
st.markdown("<h1 style='text-align: left; margin-top:2rem;'>Bond Yield Dashboard</h1>", unsafe_allow_html=True)

# ————— Disclaimer Section —————
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Disclaimer")
    st.write(
        "This tool provides an estimated bond yield and is for educational purposes only. "
        "Please consult a financial advisor before making any investment decisions."
    )
    if st.button("Run Full Prediction"):
        st.switch_page("pages/data1.py")

# ————— Business Day Generator —————
st.title("Business Days Selector")

today = date.today()
two_years_later = today + timedelta(days=730)

us_bd = CustomBusinessDay(calendar=USFederalHolidayCalendar())
all_business_days = pd.date_range(start=today, end=two_years_later, freq=us_bd)
df_all_business_days = pd.DataFrame({'Business Day': all_business_days})



# ————— Date Input —————
end_date = st.date_input(
    "Select an end date",
    value=today,
    min_value=today,
    max_value=two_years_later,
    help="Calendar popup — only dates within the next 2 years"
)

# ————— Filter & Display —————
if end_date < today:
    st.error("End date cannot be before today.")
else:
    df_selected_days = df_all_business_days[df_all_business_days['Business Day'] <= pd.to_datetime(end_date)]

    st.session_state["business_days_df"] = df_selected_days.copy()

    st.subheader(f"Business Days from {today} to {end_date}")
    st.dataframe(df_selected_days)
# Save just the date column once (only if not already saved)
if "base_df" not in st.session_state:
    st.session_state["base_df"] = df_all_business_days.copy()

# Filter by selected range
df_selected_days = df_all_business_days[df_all_business_days['Business Day'] <= pd.to_datetime(end_date)]
st.session_state["filtered_df"] = df_selected_days.copy()
