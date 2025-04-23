import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils.all_tariffs import all_tariffs
from utils.all_maturities import all_maturities 
#from utils.all_models import all_models
#from utils.non_tariff_columns import non_tariff_columns


class YieldForecastCalculator:
    def __init__(self, future_data):
        """
        Initializes the YieldForecastCalculator with future data and exogenous columns.

        Parameters:
        future_data (pd.DataFrame): DataFrame containing the future data with exogenous variables.
        """
        self.future_data = future_data
        self.exog_columns = [col for col in future_data.columns if col != "date"]
        self.predictions = {}
        self._validate_inputs()
        self._load_models_and_predict()

    def _validate_inputs(self):
        """
        Validates the input exogenous columns and determines the model type.
        """
        contains_tariff = any(tariff in self.exog_columns for tariff in all_tariffs)
        if not contains_tariff:
            # Ensure all tariff columns are present and set to 0 if missing
            for tariff in all_tariffs:
                if tariff not in self.future_data.columns:
                    self.future_data[tariff] = 0
            self.exog_columns.extend(all_tariffs)

        # Determine model type based on non-tariff columns
        contains_ffr_cpi = all(non_tariff in self.exog_columns for non_tariff in ["FFR", "Inflation"])
        contains_vix_cs = all(non_tariff in self.exog_columns for non_tariff in ["VIX", "Consumer Sentiment"])
        contains_m1 = "M1 Supply" in self.exog_columns

        if contains_ffr_cpi and contains_vix_cs and contains_m1:
            self.model_type = "tariff_ffr_cpi_vix_cs_m1"
        elif contains_ffr_cpi and contains_vix_cs:
            self.model_type = "tariff_ffr_cpi_vix_cs"
        elif contains_ffr_cpi and contains_m1:
            self.model_type = "tariff_ffr_cpi_m1"
        elif contains_vix_cs and contains_m1:
            self.model_type = "tariff_vix_cs_m1"
        elif contains_ffr_cpi:
            self.model_type = "tariff_ffr_cpi"
        elif contains_vix_cs:
            self.model_type = "tariff_vix_cs"
        elif contains_m1:
            self.model_type = "tariff_m1"
        else:
            raise ValueError("The exog_columns must contain valid non-tariff columns for the selected tariff model.")

    def _load_models_and_predict(self):
        """
        Loads the models for each maturity and performs predictions.
        """
        selected_models = [
            f"arima_model_{maturity}-year_monthly_tariff_{self.model_type}.pkl"
            for maturity in all_maturities
        ]

        for maturity, model_path in zip(all_maturities, selected_models):
            forecast_mean, forecast_lower, forecast_upper = self._predict_single_yield(model_path)
            self.predictions[f"{maturity}-year"] = {
                "mean": forecast_mean,
                "lower": forecast_lower,
                "upper": forecast_upper,
            }

    def predict_single_yield(self, model_pickle_path):
        """
        Predicts and returns the yield for a specific maturity using a pre-trained model.

        Parameters:
        model_pickle_path (str): Path to the pickled model file.

        Returns:
        tuple: The predicted yield mean, lower bound, and upper bound for the confidence interval.
        """
        with open(model_pickle_path, 'rb') as f:
            model = pickle.load(f)

        self.future_data.index = pd.to_datetime(self.future_data.index).to_period("M")
        exog_test = self.future_data[self.exog_columns]

        forecast = model.get_forecast(steps=len(self.future_data), exog=exog_test, alpha=0.2)
        forecast_ci = forecast.conf_int()

        forecast_lower = pd.Series(forecast_ci.iloc[:, 0].values, index=self.future_data.index)
        forecast_upper = pd.Series(forecast_ci.iloc[:, 1].values, index=self.future_data.index)
        forecast_mean = pd.Series(forecast.predicted_mean.values, index=self.future_data.index)

        return forecast_mean, forecast_lower, forecast_upper

    def plot_forecasts(self):
        """
        Plots the forecasted yields for all maturities on a single graph.
        """
        plt.figure(figsize=(12, 8))
        for maturity, data in self.predictions.items():
            plt.plot(data["mean"].index, data["mean"].values, label=f"{maturity} Mean")
            plt.fill_between(
                data["mean"].index,
                data["lower"].values,
                data["upper"].values,
                alpha=0.2,
                label=f"{maturity} Confidence Interval"
            )
        plt.title("Yield Forecasts")
        plt.xlabel("Date")
        plt.ylabel("Yield")
        plt.legend()
        plt.grid()
        plt.show()

    def get_forecast(self):
        """
        Returns the forecasted mean values for all maturities.

        Returns:
        dict: A dictionary where keys are maturity names and values are forecasted mean values.
        """
        return {maturity: data["mean"] for maturity, data in self.predictions.items()}

    def get_prediction_intervals(self):
        """
        Returns the prediction intervals (lower and upper bounds) for all maturities.

        Returns:
        dict: A dictionary where keys are maturity names and values are tuples of (lower, upper) bounds.
        """
        return {
            maturity: (data["lower"], data["upper"])
            for maturity, data in self.predictions.items()
        }

    def get_step_by_step_predictions(self):
        """
        Returns the full prediction details (mean, lower, upper) for all maturities.

        Returns:
        dict: A dictionary where keys are maturity names and values are dictionaries with mean, lower, and upper bounds.
        """
        return self.predictions

import pickle
import pandas as pd

def get_yield_forecast_at_end_date(model_path, future_data, end_date):
    """
    Returns the yield forecast at the specified end date using a pre-trained model.

    Parameters:
    model_path (str): Path to the pickled model file.
    future_data (pd.DataFrame): DataFrame containing the future data with exogenous variables.
    end_date (str): The end date for which the forecast is required (in 'YYYY-MM-DD' format).

    Returns:
    dict: A dictionary containing the forecasted mean, lower bound, and upper bound at the end date.
    """
    # Ensure the end_date is in datetime format
    end_date = pd.to_datetime(end_date)

    # Load the model
    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    # Prepare the future data
    future_data.index = pd.to_datetime(future_data.index).to_period("M")
    exog_columns = [col for col in future_data.columns if col != "date"]
    exog_test = future_data[exog_columns]

    # Generate the forecast
    forecast = model.get_forecast(steps=len(future_data), exog=exog_test, alpha=0.2)
    forecast_ci = forecast.conf_int()

    # Extract the forecasted mean, lower, and upper bounds
    forecast_mean = pd.Series(forecast.predicted_mean.values, index=future_data.index)
    forecast_lower = pd.Series(forecast_ci.iloc[:, 0].values, index=future_data.index)
    forecast_upper = pd.Series(forecast_ci.iloc[:, 1].values, index=future_data.index)

    # Get the forecast at the specified end date
    if end_date not in forecast_mean.index:
        raise ValueError(f"The specified end date {end_date} is not within the forecast range.")

    return forecast_mean.loc[end_date]