import os

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


if __name__ == "__main__":
    def get_all_models():
        """
        Returns a list of all files in the models/ directory.
        """
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_dir = os.path.join(repo_root, 'models')
        if not os.path.exists(models_dir):
            return []
        return [f for f in os.listdir(models_dir) if os.path.isfile(os.path.join(models_dir, f))]
    # Example usage
    model_files = get_all_models()
    for model_file in model_files:
        print(model_file)