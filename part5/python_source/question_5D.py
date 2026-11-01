"""5D: in-sample factor replication, excluding the regression intercept."""
from part5_common import FACTORS, SOURCE, UNIVERSE, config, utils, save, load_inputs, fit_model
import matplotlib.pyplot as plt
import pandas as pd


def run(returns, ff, model):
    legs = ff[FACTORS].mul(model.params[FACTORS])
    replication = legs.sum(axis=1)
    monthly = pd.DataFrame({"MSCI_Value": returns["Value"], "Replication": replication,
                            "RF": ff["RF"], "Value_minus_replication": returns["Value"] - replication,
                            "OLS_residual": model.resid})
    monthly = monthly.join(legs.add_prefix("weighted_"))
    save(monthly, "tab_5D_replication_monthly")
    correlation = monthly["MSCI_Value"].corr(replication)
    rows = []
    for name in ["MSCI_Value", "Replication"]:
        r = monthly[name]
        rows.append({"strategy": name, "annual_arithmetic_return_decimal": utils.annualized_return(r, "arithmetic"),
                     "annual_volatility_decimal": utils.annualized_volatility(r),
                     "annual_risk_free_return_decimal": utils.annualized_return(ff["RF"], "arithmetic"),
                     "sharpe_ratio": utils.sharpe_ratio(r, ff["RF"], "arithmetic"),
                     "annual_geometric_return_decimal": utils.annualized_return(r, "geometric"),
                     "correlation_with_msci_value": 1.0 if name == "MSCI_Value" else correlation,
                     "nobs": len(r)})
    performance = pd.DataFrame(rows).set_index("strategy")
    save(performance, "tab_5D_replication_performance")
    config.apply_style()
    fig, ax = utils.new_fig("full")
    wealth = utils.cumulative_value(monthly[["MSCI_Value", "Replication"]])
    # Include the initial dollar at the preceding month end.
    wealth = pd.concat([pd.DataFrame([[1, 1]], index=pd.PeriodIndex(["1994-12"], freq="M"),
                                     columns=wealth.columns), wealth])
    for name, label, color in [("MSCI_Value", "MSCI USA Value", config.COLOR_MARKET),
                                ("Replication", "Factor replication (in sample)", config.COLORS[0])]:
        ax.plot(wealth.index.to_timestamp("M"), wealth[name], label=label, color=color)
    ax.set(title="MSCI Value and factor replication", xlabel="Month", ylabel="Growth of USD 1 (log scale)")
    ax.set_yscale("log")
    from matplotlib.ticker import ScalarFormatter
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.legend(loc="upper left")
    utils.save_fig(fig, "fig_5D_replication", source=SOURCE + "\n" + UNIVERSE)
    plt.close(fig)
    return monthly, performance


if __name__ == "__main__":
    r, f, _, _ = load_inputs()
    print(run(r, f, fit_model(r, f))[1])
