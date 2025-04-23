import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils.all_tariffs import all_tariffs
from utils.all_maturities import all_maturities 
from utils.all_models import all_models
from utils.non_tariff_columns import non_tariff_columns


# for debugging purposes
all_models = [
    "arima_model_2-year_monthly_tariff_ffr_cpi_m1.pkl",
    "arima_model_7-year_monthly_tariff_ffr_cpi_m1.pkl",
    "arima_model_2-year_monthly_tariff_vix_cs_m1.pkl",
    "arima_model_7-year_monthly_tariff_vix_cs.pkl",
    "arima_model_20-year_monthly_tariff_ffr_cpi_m1.pkl",
    "arima_model_5-year_monthly_tariff.pkl",
    "arima_model_2-year_monthly_tariff_m1.pkl",
    "arima_model_3-year_monthly_tariff_m1.pkl",
    "arima_model_5-year_monthly_tariff_ffr_cpi_vix_cs.pkl",
    "arima_model_5-year_monthly_tariff_ffr_cpi_m1.pkl",
    "arima_model_10-year_monthly_tariff_vix_cs_m1.pkl",
    "arima_model_7-year_monthly_tariff_vix_cs_m1.pkl",
    "arima_model_20-year_monthly_tariff.pkl",
    "arima_model_3-year_monthly_tariff_vix_cs_m1.pkl",
    "arima_model_3-year_monthly_tariff_ffr_cpi_m1.pkl",
    "arima_model_10-year_monthly_tariff_ffr_cpi_m1.pkl",
    "arima_model_5-year_monthly_tariff_m1.pkl",
    "arima_model_5-year_monthly_tariff_vix_cs.pkl",
    "arima_model_20-year_monthly_tariff_vix_cs.pkl",
    "arima_model_5-year_monthly_tariff_vix_cs_m1.pkl",
    "arima_model_20-year_monthly_tariff_ffr_cpi.pkl",
    "arima_model_10-year_monthly_tariff_ffr_cpi.pkl",
    "arima_model_20-year_monthly_tariff_vix_cs_m1.pkl",
    "arima_model_5-year_monthly_tariff_ffr_cpi.pkl",
    "arima_model_10-year_monthly_tariff_m1.pkl",
    "arima_model_2-year_monthly_tariff_ffr_cpi_vix_cs.pkl",
    "arima_model_2-year_monthly_tariff_vix_cs.pkl",
    "arima_model_10-year_monthly_tariff_ffr_cpi_vix_cs.pkl",
    "arima_model_3-year_monthly_tariff_ffr_cpi.pkl",
    "arima_model_20-year_monthly_tariff_ffr_cpi_vix_cs.pkl",
    "arima_model_7-year_monthly_tariff_ffr_cpi_vix_cs.pkl",
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

class YieldForecastCalculator:
    def __init__(self, future_data):
        """
        Initializes the YieldForecastCalculator with future data and exogenous columns.

        Parameters:
        future_data (pd.DataFrame): DataFrame containing the future data with exogenous variables.
        """
        self.future_data = future_data
        self.exog_columns = [col for col in future_data.columns if col != "Business Day"]
        self.predictions = {}
        self._validate_inputs()
        self._load_models_and_predict()

    def _validate_inputs(self):
        """
        Validates the input exogenous columns to determine the model type.
        """
        contains_tariff = any(tariff in self.exog_columns for tariff in all_tariffs)
        contains_non_tariff = any(non_tariff in self.exog_columns for non_tariff in non_tariff_columns)

        if contains_tariff and contains_non_tariff:
            if all(non_tariff in self.exog_columns for non_tariff in ["FFR", "Inflation", "M1 Supply"]):
                self.model_type = "tariff_ffr_cpi_m1"
            elif all(non_tariff in self.exog_columns for non_tariff in ["VIX", "M1 Supply"]):
                self.model_type = "tariff_vix_cs_m1"
            elif "VIX" in self.exog_columns:
                self.model_type = "tariff_vix_cs"
            elif all(non_tariff in self.exog_columns for non_tariff in ["FFR", "Inflation", "VIX", "M1 Supply"]):
                self.model_type = "tariff_ffr_cpi_vix_cs"
            elif "M1 Supply" in self.exog_columns:
                self.model_type = "tariff_m1"
            elif all(non_tariff in self.exog_columns for non_tariff in ["FFR", "Inflation"]):
                self.model_type = "tariff_ffr_cpi"
            else:
                raise ValueError("The exog_columns must contain valid non-tariff columns for the selected tariff model.")
        elif contains_non_tariff:
            raise ValueError("Non-tariff columns are present without any tariff columns. At least one tariff column is required.")
        else:
            raise ValueError("The exog_columns must contain at least one tariff or non-tariff column.")

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

    def _predict_single_yield(self, model_pickle_path):
        """
        Predicts and returns the yield for a specific maturity using a pre-trained model.

        Parameters:
        model_pickle_path (str): Path to the pickled model file.

        Returns:
        tuple: The predicted yield mean, lower bound, and upper bound for the confidence interval.
        """
        with open(model_pickle_path, 'rb') as f:
            model = pickle.load(f)

        self.future_data.index = pd.to_datetime(self.future_data.index)
        exog_test = self.future_data[self.exog_columns]

        forecast = model.get_forecast(steps=len(self.future_data), exog=exog_test, alpha=0.2)
        forecast_ci = forecast.conf_int()

        forecast_lower = pd.Series(forecast_ci.iloc[:, 0].values, index=self.future_data.index)
        forecast_upper = pd.Series(forecast_ci.iloc[:, 1].values, index=self.future_data.index)
        forecast_mean = pd.Series(forecast.predicted_mean.values, index=self.future_data.index)

        return forecast_mean, forecast_lower, forecast_upper

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
