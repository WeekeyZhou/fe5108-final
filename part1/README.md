# Part 1 - Factor investing (1A-1E)

**Owner:** Member 1 Zhang Jiaxin

**Data:** `data/raw/class project data (FF MSCI) (parts 1 and 5).xlsx` — Fama-French 3 factors, Fama-French portfolios sorted on beta and on prior return (value-weighted, monthly), and the five MSCI USA index levels (gross, USD).

## Final deliverables

- Report: `part1/documents/Part1_report.docx`
- Exhibits (Tables 1.1-1.4, Figures 1.1-1.3): `part1/documents/Part1_exhibits.docx`
- Figures: `output/figures/fig_1*.png`; tables: `output/tables/tab_1*.csv`

## Notebooks (`python_source/`)

| Notebook | Question | Main outputs |
|---|---|---|
| `question_1A.ipynb` | Factor premia and t-statistics, 1927-1992 vs 1993-Jul 2023; momentum and low-minus-high beta spreads | `tab_1A_factor_premiums.csv`, `tab_1A_factor_spreads.csv` |
| `question_1C.ipynb` | MSCI factor indexes and multi-factor index: annualized return and Sharpe ratio, Jan 1995-Jul 2023 | `tab_1C_performance.csv`, `tab_1C_monthly_returns.csv`, `fig_1C_return.png`, `fig_1C_sharpe.png` |
| `question_1D.ipynb` | Correlations between MSCI factor spreads and Fama-French spreads (4 x 4) | `tab_1D_correlations.csv` |
| `question_1E.ipynb` | Momentum profitability across trailing 12-month market-volatility regimes, Dec 1995-Jul 2023 | `tab_1E_*.csv`, `fig_1E_regime_momentum.png` |

1B (MSCI Momentum index methodology) is answered in the report text; the source is the MSCI Momentum Indexes Methodology (December 2013).

## How to run

From the repository root, after `pip install -r requirements.txt`: run the four notebooks in order (1A, 1C, 1D, 1E), then

```bash
python part1/python_source/build_part1_docs.py
```

The builder reads the saved tables and figures and rewrites both Word documents. **Rerunning overwrites them**; keep manual edits in a separate copy.

Part 5E reuses the Part 1C multi-factor index; `tab_1C_monthly_returns.csv` is reconciled in `part5/` (see `part5/README.md`).
