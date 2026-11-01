"""5E: active returns are differences; compounded relative wealth is a ratio."""
from part5_common import COMPONENTS, LABELS, SOURCE, config, utils, save, load_inputs
import matplotlib.pyplot as plt
import pandas as pd


def run(returns):
    active = returns[[*COMPONENTS, "MultiFactor"]].sub(returns["Market"], axis=0)
    save(active, "tab_5E_active_monthly")
    relative = utils.cumulative_value(returns[active.columns]).div(
        utils.cumulative_value(returns["Market"]), axis=0) - 1
    save(relative, "tab_5E_relative_wealth_monthly")
    rows = []
    for name in active.columns:
        a = active[name]
        annual_active = utils.annualized_return(a, "arithmetic")
        te = utils.tracking_error(returns[name], returns["Market"])
        rows.append({"strategy": name, "annual_active_return_arithmetic_decimal": annual_active,
                     "annual_tracking_error_decimal": te, "information_ratio": annual_active / te,
                     "cumulative_relative_wealth_gain_decimal": relative[name].iloc[-1],
                     "annual_relative_wealth_growth_decimal": (1 + relative[name].iloc[-1]) ** (12 / len(a)) - 1,
                     "nobs": len(a)})
    performance = pd.DataFrame(rows).set_index("strategy")
    save(performance, "tab_5E_active_performance")
    config.apply_style()
    fig, ax = utils.new_fig("full")
    relative = pd.concat([pd.DataFrame(0.0, index=pd.PeriodIndex(["1994-12"], freq="M"),
                                      columns=relative.columns), relative])
    for i, name in enumerate(relative.columns):
        ax.plot(relative.index.to_timestamp("M"), relative[name], label=LABELS[name],
                color=config.COLORS[4] if name == "MultiFactor" else config.COLORS[i],
                linewidth=1.8 if name == "MultiFactor" else 0.9,
                alpha=1 if name == "MultiFactor" else 0.8)
    ax.axhline(0, color=config.COLOR_MARKET, linewidth=0.8)
    ax.set(title="Compounded performance relative to MSCI USA", xlabel="Month",
           ylabel="Strategy wealth / benchmark wealth - 1")
    utils.percent_axis(ax)
    ax.legend(ncol=3, loc="upper left")
    utils.save_fig(fig, "fig_5E_active_performance", source=SOURCE + "\nMSCI USA large/mid cap, gross USD; ratio of compounded total returns.")
    plt.close(fig)
    return active, performance


if __name__ == "__main__":
    print(run(load_inputs()[0])[1])
