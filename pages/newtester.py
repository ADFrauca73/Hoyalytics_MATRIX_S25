import streamlit as st
import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize
from scipy.special import expit
from scipy.stats import norm
import pandas as pd

from utils.unpickling import get_yield_forecast_at_end_date

# Ensure required session state data exists
if "filtered_df" not in st.session_state:
    st.error("No data found. Please complete the previous steps.")
    st.stop()

######################################################################### ADD HERE
#exogenous variable final values
exog_data = st.session_state["filtered_df"]
#########################################################################



exog_vars = [
    'start_tariff_39', 'start_tariff_40', 'start_tariff_72', 'start_tariff_73', 'start_tariff_74', 'start_tariff_75',
    'start_tariff_76', 'start_tariff_78', 'start_tariff_79', 'start_tariff_80', 'start_tariff_81', 'start_tariff_82',
    'start_tariff_83', 'start_tariff_84', 'start_tariff_85', 'start_tariff_86', 'start_tariff_87', 'start_tariff_88',
    'start_tariff_89', 'start_tariff_90', 'start_tariff_96', 'start_tariff_98','diff_FFR','diff_CPI', 'VIX_close', 'diff_CSD', 'diff_M1_supply'
]

tariffs = ['start_tariff_39', 'start_tariff_40', 'start_tariff_72', 'start_tariff_73', 'start_tariff_74', 'start_tariff_75',
    'start_tariff_76', 'start_tariff_78', 'start_tariff_79', 'start_tariff_80', 'start_tariff_81', 'start_tariff_82',
    'start_tariff_83', 'start_tariff_84', 'start_tariff_85', 'start_tariff_86', 'start_tariff_87', 'start_tariff_88',
    'start_tariff_89', 'start_tariff_90', 'start_tariff_96', 'start_tariff_98']


exog_data.index.name = "DATE"
exog_data_monthly = exog_data.resample('M').mean()

exogs = exog_data_monthly[exog_vars].dropna()

# contain if statements to check if ffr/cpi, vix/csd, and m1 are in selected by user

######################################################################### ADD HERE
FFR_BOOL = st.session_state("FFR_BOOL")
VIX_BOOL = st.session_state("VIX_BOOL")
M1_BOOL = st.session_state("M1_BOOL")

if FFR_BOOL == 0:
    exogs = exogs.drop(columns=['diff_FFR','diff_CPI'])

if VIX_BOOL == 0:
    exogs = exogs.drop(columns=['VIX_close','diff_CSD'])

if M1_BOOL == 0:
    exogs = exogs.drop(columns=['diff_M1_supply'])
#########################################################################

# make any value of exogs for tariff columns that is greater than 0 equal to 1
exogs[tariffs] = exogs[tariffs].applymap(lambda x: 1 if x > 0 else 0)

#create a new column for a lag effect before and after all tariffs in a new column called 'tariff_lag_effect' for each tariff column
for tariff in tariffs:
    exogs[f'{tariff}_lag_effect'] = exogs[tariff].shift(1).fillna(0)

for tariff in tariffs:
    exogs[f'{tariff}_future_effect'] = exogs[tariff].shift(-1).fillna(0) 

future_data = exogs

#unpickle correct model and 
import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize
from scipy.special import expit
from scipy.stats import norm
import pandas as pd

#blank list
# to store the file names
file_names = []

# "arima_model_2-year_monthly_tariff_vix_cs_m1.pkl", 

if FFR_BOOL == 1:
    if VIX_BOOL ==1:
        if M1_BOOL == 1:
            #all variables selected
            file_names.append("arima_model_2-year_monthly_all.pkl","arima_model_3-year_monthly_all.pkl","arima_model_5-year_monthly_all.pkl","arima_model_7-year_monthly_all.pkl","arima_model_10-year_monthly_all.pkl","arima_model_20-year_monthly_all.pkl")
        else:
            #ffr/cpi and vix/cs selected
            file_names.append("arima_model_2-year_monthly_tariff_ffr_cpi_vix_cs.pkl","arima_model_3-year_monthly_tariff_ffr_cpi_vix_cs.pkl","arima_model_5-year_monthly_tariff_ffr_cpi_vix_cs.pkl","arima_model_7-year_monthly_tariff_ffr_cpi_vix_cs.pkl","arima_model_10-year_monthly_tariff_ffr_cpi_vix_cs.pkl","arima_model_20-year_monthly_tariff_ffr_cpi_vix_cs.pkl",)
    elif M1_BOOL == 1:
        #ffr/cpi and m1 selected
        file_names.append("arima_model_2-year_monthly_tariff_ffr_cpi_m1.pkl","arima_model_3-year_monthly_tariff_ffr_cpi_m1.pkl","arima_model_5-year_monthly_tariff_ffr_cpi_m1.pkl","arima_model_7-year_monthly_tariff_ffr_cpi_m1.pkl","arima_model_10-year_monthly_tariff_ffr_cpi_m1.pkl","arima_model_20-year_monthly_tariff_ffr_cpi_m1.pkl")
    else:
        #only ffr/cpi selected
        file_names.append("arima_model_2-year_monthly_tariff_ffr_cpi.pkl","arima_model_3-year_monthly_tariff_ffr_cpi.pkl","arima_model_5-year_monthly_tariff_ffr_cpi.pkl","arima_model_7-year_monthly_tariff_ffr_cpi.pkl","arima_model_10-year_monthly_tariff_ffr_cpi.pkl","arima_model_20-year_monthly_tariff_ffr_cpi.pkl")
elif VIX_BOOL == 1:
    #only vix/cs selected
    file_names.append("arima_model_2-year_monthly_tariff_vix_cs.pkl","arima_model_3-year_monthly_tariff_vix_cs.pkl","arima_model_5-year_monthly_tariff_vix_cs.pkl","arima_model_7-year_monthly_tariff_vix_cs.pkl","arima_model_10-year_monthly_tariff_vix_cs.pkl","arima_model_20-year_monthly_tariff_vix_cs.pkl")
elif M1_BOOL == 1:
    #only m1 selected
    file_names.append("arima_model_2-year_monthly_tariff_m1.pkl","arima_model_3-year_monthly_tariff_m1.pkl","arima_model_5-year_monthly_tariff_m1.pkl","arima_model_7-year_monthly_tariff_m1.pkl","arima_model_10-year_monthly_tariff_m1.pkl","arima_model_20-year_monthly_tariff_m1.pkl")
else:
    #tariffs only selected
    file_names.append("arima_model_2-year_monthly_tariff.pkl","arima_model_3-year_monthly_tariff.pkl","arima_model_5-year_monthly_tariff.pkl","arima_model_7-year_monthly_tariff.pkl","arima_model_10-year_monthly_tariff.pkl","arima_model_20-year_monthly_tariff.pkl")


maturities = [2, 3, 5, 7, 10, 20]
# create an empty dictionary to store the output
output = {}
for maturity, model in zip(maturities, file_names):
    #adrian function
    # make the end date the last date in future_data
    end_date = future_data.index[-1]
    predicted_yield = get_yield_forecast_at_end_date(model, future_data, end_date)

    print(f"Running model: {model}")
    output[maturity] = predicted_yield

# Create a graph showing the predicted yields
import matplotlib.pyplot as plt

# Apply the theme
plt.style.use('dark_background')

# Plot the predicted yields
plt.figure(figsize=(10, 6))
plt.plot(output.keys(), output.values(), marker='o', linestyle='-', color='#3895d3')
plt.title('Predicted Yields by Maturity', color='#FFFFFF', fontsize=16)
plt.xlabel('Maturity (Years)', color='#FFFFFF', fontsize=12)
plt.ylabel('Yield', color='#FFFFFF', fontsize=12)
plt.grid(True, color='#072f5f')
plt.xticks(maturities, color='#FFFFFF')  # Ensure x-axis ticks match maturities
plt.yticks(color='#FFFFFF')
plt.tight_layout()

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
st.title("Predictions")


st.pyplot(plt)

# Navigation buttons
col1, _, col2 = st.columns([1, 6, 1])
with col1:
    if st.button("⬅️ Previous", key="prev_btn"):
        st.switch_page("pages/data6.py")
with col2:
    if st.button("Back to start", key="back_to_start_btn"):
        st.switch_page("pages/Dashboard.py")