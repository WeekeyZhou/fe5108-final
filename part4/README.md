# Part 4: Product Innovation (NVDL vs NVDA)

Tests whether GraniteShares 2x Long NVDA Daily ETF (NVDL) delivers 2x NVDA's daily return, and how that breaks down over longer horizons.

## Data
- `data/raw/class project data (part 4 - product innovation).xlsx`
- Daily total returns of NVDA and NVDL, 2024-02-01 to 2024-08-30 (147 trading days), stored as decimals and sorted newest-first (the notebooks re-sort ascending).
- Reference: `documents/` (NVDL factsheet as of 2024-06-30, class project instructions).

## Notebooks (`python_source/`)

| Notebook | Question | Key result |
|---|---|---|
| `4A_risk_metrics.ipynb` | Std. dev., 95% VaR, 95% CVaR | NVDL risk is about 2x NVDA |
| `4B_regression.ipynb` | NVDL on NVDA regression | beta = 1.996, 95% CI [1.987, 2.005], contains 2 |
| `4C_performance_drag.ipynb` | Annualized intercept vs 1.15% net expense ratio | about -15.4% per year, far above the stated fee |
| `4D_cumulative_returns.ipynb` | Monthly and full-window compounded returns | NVDA +94.0%, NVDL +181.5% (1.93x, not 2x) |
| `4E_two_day_example.ipynb` | +10% then -9% example | NVDA +0.1%, NVDL -1.6% |
| `4F_trader_vs_investor.ipynb` | Stock or ETF? | Trader: ETF. Long-term investor: stock |

Each notebook is self-contained and can be run independently, in any order.

## How to run
1. Install: `pip install pandas numpy matplotlib statsmodels openpyxl jupyter`
2. Open a notebook from `part4/python_source/` and run all cells. Paths are relative to that folder (`../../data/raw`, `../../output/part4`).
3. Tables (csv) and figures (png) are saved to `output/part4/`.
