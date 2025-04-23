import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def predict_single_yield(model_pickle_path, future_data, exog_columns):
    """
    Predicts and returns the yield for a specific maturity using a pre-trained model

    Parameters:
    model_pickle_path (str): Path to the pickled model file.
    future_data (pd.DataFrame): DataFrame containing the future data with exogenous variables.
    exog_columns (list): List of column names for exogenous variables.

    Returns:
    the predicted yield for the future period.
    """
    # Load the model
    with open(model_pickle_path, 'rb') as f:
        result = pickle.load(f)

    # Prepare the future data
    future_data.index = pd.to_datetime(future_data.index)
    start = future_data.index[0]
    end = future_data.index[-1]
    exog_test = future_data[exog_columns]  # Replace with your actual column names

    # Forecast and predictions
    #predictions = result.predict(start=start, end=end, exog=exog_test, typ='levels')
    forecast = result.get_forecast(steps=len(future_data), exog=exog_test, alpha=0.2)
    #forecast_ci = forecast.conf_int()

    ## Extract forecast components
    #forecast_lower = pd.Series(forecast_ci.iloc[:, 0].values, index=future_data.index)
    #forecast_upper = pd.Series(forecast_ci.iloc[:, 1].values, index=future_data.index)
    forecast_mean = pd.Series(forecast.predicted_mean.values, index=future_data.index)

    return forecast_mean

def predict_all_yields(future_data, exog_columns): # currently a stub
    """
    Predicts and returns the yields for all maturities using pre-trained models

    Parameters:
    future_data (pd.DataFrame): DataFrame containing the future data with exogenous variables.
    exog_columns (list): List of column names for exogenous variables.

    Returns:
    dict: A dictionary where keys are maturity names and values are the predicted yields.
    """
    pass
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