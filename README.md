# FE5108 Portfolio Theory and Investments — Class Project (Fall 2026)

Practitioner segment class project, NUS Risk Management Institute. Instructor: Sanne de Boer.

**Final submission:** [`report/FE5108_Group_Report.pdf`](report/FE5108_Group_Report.pdf) (Word version: [`report/FE5108_Group_Report.docx`](report/FE5108_Group_Report.docx))

| Pages | Content |
|---|---|
| 1 | Cover page with team members and contributions |
| 2–9 | Main text, Parts 1–5 (within the 8-page limit; Arial 11 pt) |
| 10–31 | Appendix of exhibits, numbered by part (e.g. Table 3.1, Figure 4.2); each exhibit states its data source, period and universe |

The code, data and all generated tables and figures behind the report are in this repository.

---

## Team and contributions

| Member | Part | Contribution |
|---|---|---|
| Zhang Jiaxin | Part 1 — Factor investing (22 pts) | Fama-French factor premia and t-statistics before and after 1993; MSCI Momentum index methodology; multi-factor index and Sharpe ratios; MSCI vs Fama-French factor-spread correlations; momentum across market-volatility regimes |
| Sato Yuki | Part 2 — Security-level data (20 pts) | Data cleaning and validation; market proxy vs MSCI USA; three Value portfolio constructions; tracking error and correlation with HML |
| Zhou Mo (Weekey) | Part 3 — Portfolio construction (21 pts) | Minimum-variance and inverse-volatility portfolios; in-sample and out-of-sample volatility; re-optimization; crisis performance. Also set up this repository and the shared code conventions, allocated the work and integrated the final report |
| Zhang Yin | Part 4 — Product innovation (11 pts) | NVDL vs NVDA risk metrics, regression and performance drag, monthly and two-day compounding, trader vs investor choice |
| Wu Shuhan | Part 5 — Portfolio analytics (26 pts) | MSCI vs Fama-French value definitions; factor regression and alpha; replicating portfolio; active return, tracking error and information ratio; risk decomposition |

Each member owns the data loading, code, exhibits and write-up of their part.

---

## Repository structure

```
Final Project/
├── README.md                    This file
├── requirements.txt             Python packages for the whole project
├── Read it before you do!/      Assignment PDF and team plan
├── data/raw/                    Data provided by the instructor (not modified)
├── src/
│   ├── config.py                Shared paths, analysis periods and chart style
│   └── utils.py                 Shared helpers: units, dates, annualization, charts, tables
├── part1/ … part5/              One folder per part
│   ├── README.md                Part-specific notes
│   ├── python_source/           Notebooks / scripts and the part's Word builder
│   └── documents/               PartN_report.docx (text) and PartN_exhibits.docx (exhibits)
├── output/
│   ├── figures/                 All figures (PNG), named by question, e.g. fig_3C_oos_vol.png
│   └── tables/                  All numerical tables (CSV), e.g. tab_3C_oos_vol.csv
└── report/
    ├── build_report.py          Builds the integrated group report from the part documents
    ├── FE5108_Group_Report.docx
    └── FE5108_Group_Report.pdf
```

## Data

| File (`data/raw/`) | Contents | Used in |
|---|---|---|
| `class project data (FF MSCI) (parts 1 and 5).xlsx` | Fama-French portfolios sorted on beta and on prior return, Fama-French 3 factors, MSCI USA / Value / Minimum Volatility / Equal Weighted / Momentum index levels (gross, USD) | Parts 1, 3E, 5 |
| `class project data (part 2 - factor portfolio construction).csv` | Anonymized stock-level data from *Machine Learning for Factor Investing* (Coqueret and Guida), Nov 1998 – Mar 2019 | Part 2 |
| `class project data (part 3 - pf construction).xlsx` | Fama-French 49 industry portfolios, value-weighted monthly total returns, Jan 1995 – Jul 2023 | Part 3 |
| `class project data (part 4 - product innovation).xlsx` | Daily total returns of NVDA and NVDL, Feb – Aug 2024 | Part 4 |

Cross-check: MSCI USA return for January 1995 is 2.781% in every part that uses it (Parts 1, 2, 3 and 5).

---

## Reproducing the results

Python 3.12 is recommended. From the repository root:

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Run each part, then rebuild the integrated report. Notebooks can be run in Jupyter ("Restart & Run All") or from the command line with `jupyter nbconvert --to notebook --execute --inplace <notebook>`.

| Part | Run, in this order | Builds |
|---|---|---|
| 1 | `part1/python_source/question_1A.ipynb`, `1C`, `1D`, `1E` notebooks, then `python part1/python_source/build_part1_docs.py` | `part1/documents/Part1_*.docx` |
| 2 | `python part2/python_source/question_2A.py`, `diagnostic_2A_pb_flag.py`, `question_2A5.py`, `question_2B.py`, `question_2C.py`, `question_2D.py`, then `build_consolidated.py` (details in `part2/README.md`) | `part2/documents/Part2_*.docx` |
| 3 | `part3/python_source/question_3A_EN.ipynb` … `question_3E_EN.ipynb` (3A first: it saves the weights used by 3B–3E), then `python part3/python_source/build_part3_docs.py` | `part3/documents/Part3_*.docx` |
| 4 | `part4/python_source/4A_risk_metrics.ipynb` … `4F_trader_vs_investor.ipynb` (independent of each other) | figures and tables in `output/` |
| 5 | `python part5/python_source/run_part5.py` (runs 5B–5F and builds the documents; details in `part5/README.md`) | `part5/documents/Part5_*.docx` |
| Report | `python report/build_report.py` | `report/FE5108_Group_Report.docx` |

Notes:

- **Rerunning a builder overwrites its Word output.** Keep manual edits to a document in a separate copy.
- Part 1B and Part 5A are methodology reviews answered in the text; Part 5A's sources are in `part5/python_source/question_5A.md`.
- Part 3 also contains Chinese-language versions of its notebooks (`question_3A.ipynb` …), used as team working notes. The `_EN` versions are identical apart from the language.
- The PDF of the group report was exported with LibreOffice; exporting the `.docx` from Word gives the same layout.

## Conventions used across parts

All shared conventions are implemented in `src/config.py` and `src/utils.py`.

- **Units:** returns are decimals in code (0.01 = 1%); Fama-French percent data are converted on loading, MSCI index levels are converted to month-end to month-end returns.
- **Dates:** monthly `Period` index; each row is the return earned in that month. Analysis periods from the assignment are defined once in `config.PERIODS`.
- **Annualization:** volatility = standard deviation of monthly returns × √12; the arithmetic or geometric annualized return is chosen per question and stated in the text; Sharpe ratio as defined in footnote 2 of the assignment.
- **Exhibits:** figures saved at printed size with a source line (data source, period, universe), labelled axes, colour-blind-safe palette.
