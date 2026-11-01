"""5C: magnitude and conventional OLS uncertainty of the monthly intercept."""
from part5_common import fit_model, load_inputs, save
import pandas as pd


def run(model):
    alpha = model.params["const"]
    ci = model.conf_int().loc["const"]
    result = pd.DataFrame([{"alpha_monthly_decimal": alpha,
                            "alpha_annual_arithmetic_decimal": 12 * alpha,
                            "alpha_annual_arithmetic_basis_points": 120000 * alpha,
                            "t_statistic": model.tvalues["const"],
                            "p_value": model.pvalues["const"],
                            "ci95_annual_lower_decimal": 12 * ci.iloc[0],
                            "ci95_annual_upper_decimal": 12 * ci.iloc[1]}])
    save(result, "tab_5C_alpha")
    return result


if __name__ == "__main__":
    r, f, _, _ = load_inputs()
    print(run(fit_model(r, f)).to_string(index=False))
