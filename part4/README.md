# Part 4 - Product innovation (4A-4F): NVDL vs NVDA

**Owner:** Member 4 Zhang Yin

Tests whether the GraniteShares 2x Long NVDA Daily ETF (NVDL) delivers twice NVIDIA's (NVDA) daily return, and why that relationship breaks down over longer horizons.

## Data

- `data/raw/class project data (part 4 - product innovation).xlsx`
- Daily total returns of NVDA and NVDL, 1 Feb 2024 - 30 Aug 2024 (147 trading days), stored as decimals and sorted newest-first (the notebooks re-sort ascending).
- NVDL factsheet figures (as of 30 Jun 2024) quoted in the exhibits come from the GraniteShares NVDL product page referenced in the assignment.

## Final deliverables

- Report: `part4/documents/Part4_report.docx`
- Exhibits (Tables 4.1-4.6, Figures 4.1-4.5): `part4/documents/Part4_exhibits.docx`
- Figures saved to `output/figures/` (`4A_risk_metrics.png`, `4B_regression.png`, `4C_drag_vs_expense.png`, `4D_period_returns.png`, `4F_gap_vs_2x.png`)
- Tables saved to `output/tables/` (`4A_risk_metrics.csv`, `4B_regression.csv`, `4C_alpha.csv`, `4D_period_returns.csv`)

## Notebooks (`python_source/`)

| Notebook | Question | Key result |
|---|---|---|
| `4A_risk_metrics.ipynb` | Standard deviation, 95% VaR, 95% CVaR | NVDL risk is about 2x NVDA |
| `4B_regression.ipynb` | Regression of NVDL on NVDA | beta = 1.996, 95% CI [1.987, 2.005], contains 2 |
| `4C_performance_drag.ipynb` | Annualized intercept vs 1.15% net expense ratio | drag of about 15.4% per year, far above the stated fee |
| `4D_cumulative_returns.ipynb` | Monthly and full-window compounded returns | NVDA +94.0%, NVDL +181.5% (1.93x, not 2x) |
| `4E_two_day_example.ipynb` | NVDA +10% then -9% | NVDA +0.1%, NVDL -1.6% |
| `4F_trader_vs_investor.ipynb` | Stock or ETF? | Trader: ETF. Long-term investor: stock |

Each notebook is self-contained and can be run independently, in any order.

## How to run

1. From the repository root: `pip install -r requirements.txt`.
2. Open a notebook in `part4/python_source/` and run all cells (or `jupyter nbconvert --to notebook --execute --inplace <notebook>`). Paths are relative to that folder (`../../data/raw`, `../../output/figures`, `../../output/tables`).
