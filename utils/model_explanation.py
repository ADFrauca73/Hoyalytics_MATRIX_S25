import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

def explain_afns_difference(current_params, future_params, thresholds=None):
    """
    Generate detailed textual explanations for changes in AFNS yield curve parameters,
    with attention to direction and sign.

    :param current_params: dict from fit_afns for the present curve
    :param future_params: dict from fit_afns for the forecasted curve
    :param thresholds: dict of thresholds for each parameter
    :return: List of natural language explanations
    """
    if thresholds is None:
        thresholds = {
            "level": 0.05,
            "slope": 0.05,
            "curvature": 0.05,
            "lambda": 0.05
        }

    explanations = []

    def describe_change(name, cur, fut, diff, thresh):
        cur = round(cur, 3)
        fut = round(fut, 3)
        diff = round(diff, 3)

        # LEVEL
        if name == "level" and abs(diff) > thresh:
            if diff > 0:
                return (f"The level factor increased from {cur} to {fut}, suggesting that long-term yields are expected to rise. "
                        f"This could reflect market expectations of higher long-run inflation or stronger economic growth.")
            else:
                return (f"The level factor decreased from {cur} to {fut}, indicating expectations for lower long-term interest rates. "
                        f"This may signal concerns about weaker growth or lower inflation in the future.")

        # SLOPE
        elif name == "slope" and abs(diff) > thresh:
            if cur < 0 and fut < 0:
                if diff > 0:
                    return (f"The slope factor increased from {cur} to {fut}, but both values remain negative. "
                            f"This indicates a still-inverted curve, though the inversion is expected to lessen—potentially a sign of easing recession fears.")
                else:
                    return (f"The slope factor decreased from {cur} to {fut}, deepening the yield curve inversion. "
                            f"This may reinforce market expectations of an economic slowdown.")
            elif cur < 0 < fut:
                return (f"The slope factor shifted from negative ({cur}) to positive ({fut}), marking a transition from an inverted yield curve to a normal upward-sloping one. "
                        f"This often signals improved economic outlooks.")
            elif cur > 0 and fut < 0:
                return (f"The slope factor flipped from positive ({cur}) to negative ({fut}), indicating an expected inversion of the yield curve—often viewed as a warning of recession.")
            elif diff > 0:
                return (f"The slope factor increased from {cur} to {fut}, steepening the yield curve. "
                        f"This could point to expectations for stronger economic activity or rising long-term rates.")
            else:
                return (f"The slope factor decreased from {cur} to {fut}, flattening the curve. "
                        f"A flatter curve may suggest market uncertainty or weakening economic momentum.")

        # CURVATURE
        elif name == "curvature" and abs(diff) > thresh:
            if cur < 0 and fut < 0:
                if diff > 0:
                    return (f"The curvature factor increased from {cur} to {fut}, though both values are negative. "
                            f"This means the mid-term yields are expected to be less depressed than before.")
                else:
                    return (f"The curvature factor decreased further into negative territory ({cur} to {fut}), indicating an even more pronounced dip in medium-term yields.")
            elif cur > 0 and fut < 0:
                return (f"The curvature factor changed from positive ({cur}) to negative ({fut}), suggesting a shift toward a concave yield curve—possibly reflecting mid-term pessimism.")
            elif cur < 0 and fut > 0:
                return (f"The curvature factor moved from negative ({cur}) to positive ({fut}), pointing to a shift toward more convexity—suggesting a possible mid-term rate rebound.")
            elif diff > 0:
                return (f"The curvature factor increased from {cur} to {fut}, indicating a more pronounced hump in the yield curve at intermediate maturities. "
                        f"This could reflect increased uncertainty or mixed expectations across time horizons.")
            else:
                return (f"The curvature factor decreased from {cur} to {fut}, smoothing out the mid-term segment of the curve. "
                        f"This suggests more consistency in market expectations across maturities.")

        # LAMBDA
        elif name == "lambda" and abs(diff) > thresh:
            if diff > 0:
                return (f"The lambda parameter rose from {cur} to {fut}, meaning yield curve factors decay more quickly with maturity. "
                        f"This suggests short-term influences are expected to play a stronger role in shaping yields.")
            else:
                return (f"The lambda parameter fell from {cur} to {fut}, indicating slower decay of yield curve components. "
                        f"This suggests that long-term expectations are expected to have more influence.")

        return None

    diffs = {
        "level": future_params["level"] - current_params["level"],
        "slope": future_params["slope"] - current_params["slope"],
        "curvature": future_params["curvature"] - current_params["curvature"],
        "lambda": future_params["lambda"] - current_params["lambda"],
    }

    for param in ["level", "slope", "curvature", "lambda"]:
        explanation = describe_change(
            name=param,
            cur=current_params[param],
            fut=future_params[param],
            diff=diffs[param],
            thresh=thresholds.get(param, 0.05)
        )
        if explanation:
            explanations.append(explanation)

    if not explanations:
        explanations.append("There are no significant changes in the yield curve parameters between the current and forecasted periods.")

    return explanations


# SEEMS SCUFFED, NEED TO FIX???
def afns_yield(maturities, x, lambda_):
    """AFNS yield curve function assuming Vasicek dynamics."""
    level, slope, curvature = x

    maturities = np.array(maturities)
    B1 = (1 - np.exp(-lambda_ * maturities)) / (lambda_ * maturities)
    B2 = B1 - np.exp(-lambda_ * maturities)

    return level + slope * B1 + curvature * B2

def fit_afns(maturities, yields, lambda_init=0.5):
    """
    Fit the AFNS model to observed yields.
    :param maturities: List or array of maturities (in years)
    :param yields: Observed yields corresponding to the maturities
    :param lambda_init: Initial guess for lambda (decay parameter)
    :return: Dictionary with optimal parameters
    """
    maturities = np.array(maturities)
    yields = np.array(yields)

    def objective(params):
        level, slope, curvature, lambda_ = params
        fitted = afns_yield(maturities, [level, slope, curvature], lambda_)
        return np.mean((fitted - yields) ** 2)

    # Initial guesses: level, slope, curvature, lambda
    initial_guess = [np.mean(yields), -1.0, 1.0, lambda_init]
    bounds = [(-10, 10), (-10, 10), (-10, 10), (0.01, 10.0)]

    result = minimize(objective, initial_guess, bounds=bounds)

    if not result.success:
        raise RuntimeError("AFNS fitting failed: " + result.message)

    level, slope, curvature, lambda_ = result.x
    return {
        "level": level,
        "slope": slope,
        "curvature": curvature,
        "lambda": lambda_,
        "fitted_yields": afns_yield(maturities, [level, slope, curvature], lambda_)
    }

import numpy as np
import matplotlib.pyplot as plt

def plot_yield_curve_comparison(maturities, observed_yields, forecast_yields, current_params, forecast_params):
    # Configurable colors
    observed_color = "navy"
    forecast_color = "darkgreen"
    higher_current_color = "blue"
    higher_forecast_color = "green"
    fitted_line_style = '--'

    # Interpolation grid
    x_vals = np.linspace(min(maturities), max(maturities), 300)

    # AFNS formula
    def afns_yields(params, taus):
        level = params["level"]
        slope = params["slope"]
        curvature = params["curvature"]
        lambd = params["lambda"]
        taus = np.array(taus)
        term1 = (1 - np.exp(-lambd * taus)) / (lambd * taus)
        term2 = term1 - np.exp(-lambd * taus)
        return level + slope * term1 + curvature * term2

    fitted_observed = afns_yields(current_params, x_vals)
    fitted_forecast = afns_yields(forecast_params, x_vals)

    # Plot 1: Observed vs Fitted (Current)
    plt.figure(figsize=(14, 4))
    plt.subplot(1, 3, 1)
    plt.plot(x_vals, fitted_observed, label="Fitted (current)", color=observed_color, linestyle=fitted_line_style)
    plt.scatter(maturities, observed_yields, label="Observed Yields", color=observed_color, zorder=5)
    plt.title("Current Yield Curve")
    plt.xlabel("Maturity (Years)")
    plt.ylabel("Yield (%)")
    plt.legend()
    plt.grid(True)

    # Plot 2: Forecast vs Fitted (Forecast)
    plt.subplot(1, 3, 2)
    plt.plot(x_vals, fitted_forecast, label="Fitted (forecast)", color=forecast_color, linestyle=fitted_line_style)
    plt.scatter(maturities, forecast_yields, label="Forecast Yields", color=forecast_color, zorder=5)
    plt.title("Forecasted Yield Curve")
    plt.xlabel("Maturity (Years)")
    plt.legend()
    plt.grid(True)

    # Plot 3: Fitted Comparison with Color Highlight
    plt.subplot(1, 3, 3)
    plt.plot(x_vals, fitted_observed, label="Current (Fitted)", color=observed_color)
    plt.plot(x_vals, fitted_forecast, label="Forecast (Fitted)", color=forecast_color)

    # Highlight which curve is higher
    for i in range(len(x_vals) - 1):
        x_segment = x_vals[i:i+2]
        y1_segment = fitted_observed[i:i+2]
        y2_segment = fitted_forecast[i:i+2]
        if np.mean(y1_segment) > np.mean(y2_segment):
            plt.fill_between(x_segment, y1_segment, y2_segment, color=higher_current_color, alpha=0.2)
        else:
            plt.fill_between(x_segment, y1_segment, y2_segment, color=higher_forecast_color, alpha=0.2)

    plt.title("Fitted Curve Comparison")
    plt.xlabel("Maturity (Years)")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    maturities = [1, 2, 3, 5, 10, 20, 30]  # in years
    observed_yields = [4.9, 4.8, 4.7, 4.5, 4.2, 4.1, 4.0]  # example yield curve
    forecast_yields = [4.8, 4.7, 4.6, 4.6, 4.4, 4.3, 4.2]  # example yield curve

    current_params = fit_afns(maturities, observed_yields)
    forecast_params = fit_afns(maturities, forecast_yields)

    plot_yield_curve_comparison(maturities, observed_yields, forecast_yields, current_params, forecast_params)

    print("Current params:")
    print(current_params)
    print("Forecast params:")
    print(forecast_params)
    explanations = explain_afns_difference(current_params, forecast_params)
    for explanation in explanations:
        print(explanation) #st.write