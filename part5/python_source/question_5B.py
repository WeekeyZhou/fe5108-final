"""5B: single-index monthly OLS with conventional (non-HAC) inference."""
from part5_common import FACTORS, fit_model, load_inputs, save
import pandas as pd


def run(returns, ff):
    model = fit_model(returns, ff)
    ci = model.conf_int()
    table = pd.DataFrame({"coefficient": model.params, "standard_error": model.bse,
                          "t_statistic": model.tvalues, "p_value": model.pvalues,
                          "ci95_lower": ci[0], "ci95_upper": ci[1]})
    table.index.name = "term"
    save(table, "tab_5B_regression")
    save(pd.DataFrame([{"nobs": int(model.nobs), "residual_df": int(model.df_resid),
                        "r_squared": model.rsquared, "adjusted_r_squared": model.rsquared_adj,
                        "residual_std_monthly_decimal": model.mse_resid ** 0.5,
                        "covariance_type": model.cov_type,
                        "sample_start": "1995-01", "sample_end": "2023-07"}]),
         "tab_5B_model_summary")
    save(returns[["Value"]].join(ff[FACTORS]), "tab_5B_regression_inputs")
    return model


if __name__ == "__main__":
    r, f, _, _ = load_inputs()
    print(run(r, f).summary())
