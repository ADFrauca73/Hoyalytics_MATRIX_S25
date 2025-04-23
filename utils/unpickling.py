import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils.all_tariffs import all_tariffs
from utils.all_maturities import all_maturities 
from utils.all_models import get_all_models
from utils.non_tariff_columns import non_tariff_columns
#model_files = get_all_models()

# for debugging purposes
model_files = [
    "arima_model_7-year_monthly_tariff_ffr_cpi_m1.pkl",
    "arima_model_2-year_monthly_tariff_vix_cs_m1.pkl",
    "arima_model_20-year_monthly_tariff_ffr_cpi_m1.pkl",
    "arima_model_5-year_monthly_tariff_ffr_cpi_m1.pkl",
    "arima_model_10-year_monthly_tariff_vix_cs_m1.pkl",
    "arima_model_7-year_monthly_tariff_vix_cs_m1.pkl",
    "arima_model_3-year_monthly_tariff_vix_cs_m1.pkl",
    "arima_model_3-year_monthly_tariff_ffr_cpi_m1.pkl",
    "arima_model_10-year_monthly_tariff_ffr_cpi_m1.pkl",
    "arima_model_5-year_monthly_tariff_vix_cs_m1.pkl",
    "arima_model_20-year_monthly_tariff_vix_cs_m1.pkl",
]
all_maturities = [2, 3, 5, 7, 10, 20]
non_tariff_columns = [
    "Consumer Sentiment",
    "VIX",
    "Inflation",
    "FFR",
    "M1 Supply"
]
all_tariffs = [
    "Chapter 39 – Plastics and articles thereof",
    "Chapter 40 – Rubber and articles thereof",
    "Chapter 72 – Iron and steel",
    "Chapter 73 – Articles of iron or steel",
    "Chapter 74 – Copper and articles thereof",
    "Chapter 75 – Nickel and articles thereof",
    "Chapter 76 – Aluminum and articles thereof",
    "Chapter 78 – Lead and articles thereof",
    "Chapter 79 – Zinc and articles thereof",
    "Chapter 80 – Tin and articles thereof",
    "Chapter 81 – Other base metals; cermets; articles thereof",
    "Chapter 82 – Tools, implements, cutlery, spoons and forks, of base metal",
    "Chapter 83 – Miscellaneous articles of base metal",
    "Chapter 84 – Nuclear reactors, boilers, machinery and mechanical appliances",
    "Chapter 85 – Electrical machinery and equipment; sound recorders and reproducers, etc.",
    "Chapter 86 – Railway or tramway locomotives, rolling-stock, and parts",
    "Chapter 87 – Vehicles other than railway or tramway rolling-stock",
    "Chapter 88 – Aircraft, spacecraft, and parts thereof",
    "Chapter 89 – Ships, boats, and floating structures",
    "Chapter 90 – Optical, photographic, cinematographic, measuring, checking, precision, medical instruments",
    "Chapter 96 – Miscellaneous manufactured articles",
    "Chapter 98 – Special classification provisions (e.g., U.S. goods returned, duty exemptions)"
]

def predict_single_yield(model_pickle_path, future_data, exog_columns):
    """
    Predicts and returns the yield for a specific maturity using a pre-trained model

    Parameters:
    model_pickle_path (str): Path to the pickled model file.
    future_data (pd.DataFrame): DataFrame containing the future data with exogenous variables.
    exog_columns (list): List of column names for exogenous variables.

    Returns:
    the predicted yield for the future period, a lower bound, and an upper bound for the confidence interval
    """
    # Load the model
    with open(model_pickle_path, 'rb') as f:
        result = pickle.load(f)

    # Prepare the future data
    future_data.index = pd.to_datetime(future_data.index)
    #start = future_data.index[0]
    #end = future_data.index[-1]
    exog_test = future_data[exog_columns]  # Replace with your actual column names

    # Forecast and predictions
    #predictions = result.predict(start=start, end=end, exog=exog_test, typ='levels')
    forecast = result.get_forecast(steps=len(future_data), exog=exog_test, alpha=0.2)
    forecast_ci = forecast.conf_int()

    ## Extract forecast components
    forecast_lower = pd.Series(forecast_ci.iloc[:, 0].values, index=future_data.index)
    forecast_upper = pd.Series(forecast_ci.iloc[:, 1].values, index=future_data.index)
    forecast_mean = pd.Series(forecast.predicted_mean.values, index=future_data.index)

    return forecast_mean, forecast_lower, forecast_upper

def predict_all_yields(future_data, exog_columns): # currently a stub
    """
    Predicts and returns the yields for all maturities using pre-trained models

    Parameters:
    future_data (pd.DataFrame): DataFrame containing the future data with exogenous variables.
    exog_columns (list): List of column names for exogenous variables.

    Returns:
    dict: A dictionary where keys are maturity names and values are the predicted yields.
    """
    # Determine the type of model based on exog_columns
    contains_tariff = any(tariff in exog_columns for tariff in all_tariffs)
    contains_non_tariff = any(non_tariff in exog_columns for non_tariff in non_tariff_columns)

    # FLESH THIS OUT
    if contains_tariff and contains_non_tariff:
        model_type = "ffr_cpi_m1"
    elif contains_non_tariff:
        model_type = "vix_cs_m1"
    else:
        raise ValueError("The exog_columns must contain at least one non-tariff column.")
    # end FLESH THIS OUT

    # Generate the list of model paths for each maturity
    selected_models = [
        f"arima_model_{maturity}-year_monthly_tariff_{model_type}.pkl"
        for maturity in all_maturities
    ]

    # Predict yields for all maturities
    predictions = {}
    for maturity, model_path in zip(all_maturities, selected_models):
        forecast_mean, forecast_lower, forecast_upper = predict_single_yield(
            model_path, future_data, exog_columns
        )
        predictions[f"{maturity}-year"] = {
            "mean": forecast_mean,
            "lower": forecast_lower,
            "upper": forecast_upper,
        }

    return predictions
    

"""
if __name__ == "__main__":
    #future_data is the dataframe with the exogenous variables for the future period




    # Load the model
    with open('saved_model.pkl', 'rb') as f:
        result = pickle.load(f)

    # Prepare the future data
    future_data.index = pd.to_datetime(future_data.index)
    start = future_data.index[0]
    end = future_data.index[-1]
    exog_test = future_data[exog_columns]  # Replace with your actual column names

    # Forecast and predictions
    predictions = result.predict(start=start, end=end, exog=exog_test, typ='levels')
    forecast = result.get_forecast(steps=len(future_data), exog=exog_test, alpha=0.2)
    forecast_ci = forecast.conf_int()

    # Extract forecast components
    forecast_lower = pd.Series(forecast_ci.iloc[:, 0].values, index=future_data.index)
    forecast_upper = pd.Series(forecast_ci.iloc[:, 1].values, index=future_data.index)
    forecast_mean = pd.Series(forecast.predicted_mean.values, index=future_data.index)

    # --------- PLOTTING ---------
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='#1e1e1e')
    ax.set_facecolor('#1e1e1e')

    forecast_mean.plot(ax=ax, label='Forecast Mean', color='lime')
    forecast_lower.plot(ax=ax, label='Lower Bound (80%)', linestyle='--', color='gray')
    forecast_upper.plot(ax=ax, label='Upper Bound (80%)', linestyle='--', color='gray')

    # Styling
    plt.title('Forecasted Values from Time Series Model', fontsize=20, fontweight='bold', color='white', fontname='Avenir')
    plt.xlabel('Date', fontsize=16, fontweight='bold', color='white', fontname='Avenir')
    plt.ylabel('Prediction', fontsize=16, fontweight='bold', color='white', fontname='Avenir')

    ax.tick_params(colors='white', labelsize=12)
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontname('Avenir')

    ax.grid(color='white', linestyle='--', linewidth=0.3, alpha=0.4)

    legend = ax.legend(fontsize=12, facecolor='#595959')
    for text in legend.get_texts():
        text.set_color('white')
        text.set_fontname('Avenir')

    plt.tight_layout()
    plt.show()

    # Print the last forecasted value
    print("Final forecast value:", forecast_mean.iloc[-1])

    predicted_Value = forecast_mean.iloc[-1]
"""