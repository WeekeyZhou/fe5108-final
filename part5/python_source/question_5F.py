"""5F: Euler covariance decomposition of ACTIVE variance, sample ddof=1."""
from part5_common import COMPONENTS, LABELS, SOURCE, config, utils, save, load_inputs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from question_5E import run as run_5E


def decompose(active):
    multi = active["MultiFactor"]
    np.testing.assert_allclose(multi, active[COMPONENTS].mean(axis=1), rtol=0, atol=1e-15)
    variance = multi.var(ddof=1)
    contributions = pd.Series({name: 0.25 * active[name].cov(multi, ddof=1) for name in COMPONENTS})
    np.testing.assert_allclose(contributions.sum(), variance, rtol=1e-12, atol=1e-18)
    table = pd.DataFrame({"weight": 0.25, "monthly_variance_contribution_decimal_squared": contributions,
                          "annual_variance_contribution_decimal_squared": 12 * contributions,
                          "variance_share": contributions / variance,
                          "variance_contribution_percent": 100 * contributions / variance})
    table.index.name = "component"
    return table


def run(active):
    table = decompose(active)
    save(table, "tab_5F_risk_decomposition")
    save(active[COMPONENTS].cov(ddof=1), "tab_5F_active_covariance")
    config.apply_style()
    fig, ax = utils.new_fig("full")
    values = table["variance_contribution_percent"]
    bars = ax.barh([LABELS[x] for x in values.index], values,
                   color=[config.COLOR_NEG if x < 0 else config.COLORS[0] for x in values])
    ax.invert_yaxis()
    ax.axvline(0, color=config.COLOR_MARKET, linewidth=0.8)
    span = max(values.max(), 0) - min(values.min(), 0)
    ax.set_xlim(min(values.min(), 0) - 0.2 * span, max(values.max(), 0) + 0.2 * span)
    for bar, value in zip(bars, values):
        ax.text(value + (0.02 * span if value >= 0 else -0.02 * span),
                bar.get_y() + bar.get_height() / 2, f"{value:.1f}%", va="center",
                ha="left" if value >= 0 else "right", fontsize=config.FONT_SMALL)
    ax.set(title="Contributions to multi-factor active variance", xlabel="Share of active-return variance (%)",
           ylabel="Component (25% weight each)")
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    utils.save_fig(fig, "fig_5F_risk_decomposition", source=SOURCE + "\nMSCI USA large/mid cap, gross USD. Contribution = 0.25 x Cov(active component, active multi-factor).")
    plt.close(fig)
    return table


if __name__ == "__main__":
    print(run(run_5E(load_inputs()[0])[0]))
