# Part 5 Portfolio Analytics (5A–5F)

Official assignment: **26/100 points**, pp. 9–10 of `Read it before you do!/class project (fall 2026) (in full).pdf`.
The earlier team plan's provisional point allocation is superseded by that assignment.

## Review the deliverables

1. Read `documents/Part5_report.docx`: concise academic English answers to 5A–5F (627 body words, two rendered A4 pages).
2. Read `documents/Part5_exhibits.docx`: four tables and three figures, with definitions, source notes and linked references (three rendered A4 pages).
3. Check `documents/validation_results.json` and `documents/validation_notes.md` for numerical checks, provenance, rendering and limitations.
4. Inspect the full-precision CSVs in `output/tables/tab_5*.csv` and PNGs in `output/figures/fig_5*.png`.

The report is deliberately short for integration into the group's eight-page text limit. The Markdown report is an accessible text companion, not an additional assignment requirement.

## Main results

- **5A:** MSCI combines three value indicators and five growth indicators with size, industry and missing-data exceptions. Unlike HML's book-to-market long-short spread, MSCI USA Value is a long-only large/mid-cap index. Sources and the historical methodology version are in `python_source/question_5A.md` and the exhibit appendix.
- **5B:** Monthly time-series OLS, not an invented panel: RF 0.864636, market 0.948032, HML 0.321642, SMB −0.174374. R² 0.948414; adjusted R² 0.947804; N = 343. Conventional, non-HAC inference.
- **5C:** Monthly intercept −0.0007128052 (−0.07128%), annual arithmetic alpha −0.85537%; t = −0.906, p = 0.366. No statistically persuasive incremental benefit from MSCI's definition in this specification.
- **5D:** Intercept-free replication correlation 0.973866. Annual arithmetic return / volatility / Sharpe: replication 10.7291% / 14.8677% / 0.5761; Value 9.8737% / 15.2667% / 0.5050. These are gross, in-sample comparisons of a statistical replication.
- **5E:** Multi-factor annual arithmetic active return 0.1519%, tracking error 3.3867%, information ratio 0.04485. Full-sample compounded relative wealth gain is a different quantity: 9.0765%.
- **5F:** Active-variance shares: Value 23.2574%, Minimum Volatility 34.0766%, Equal Weight 17.8560%, Momentum 24.8101%. Minimum Volatility is the largest contributor and is more natural for an absolute-risk mandate than a tight benchmark-relative mandate.

## Inputs and precision

- Original data: `data/raw/class project data (FF MSCI) (parts 1 and 5).xlsx`.
- FF monthly sheet columns: date, Mkt-RF, SMB, HML, RF; original units are percent. Six-digit dates identify monthly observations; annual observations are excluded. The two columns in `tab_1A_factor_spreads.csv` are Momentum and LowMinusHighBeta, so that file cannot supply the four regressors for 5B.
- MSCI sheet explicitly says **Gross**, **USD**. The five series are total-return index **levels**. December 1994 supplies the base for the first January 1995 return. Exactly 343 consecutive monthly returns through July 2023 are retained, with no filling or invented observations.
- We reuse **Part 1C's definitions and exact unrounded algorithm**. Its saved `tab_1C_monthly_returns.csv` has only four decimal places. Recovering the pre-export values from the same workbook is necessary: the rounded multi-factor series can differ from the mean of rounded components by 0.75 basis point. Every recovered cell reconciles to within the 0.5-basis-point CSV rounding bound; all six annual Part 1C performance rows also reconcile to their saved-table rounding.
- Tables use decimal returns unless the column explicitly says percent or basis points. Variance contributions are in **squared decimal-return units**. CSVs retain 17 significant digits; Word tables round for display.
- The shared `src/config.py` and `src/utils.py` are imported unchanged. Table export overrides only the shared helper's precision argument.

## Reproduce

Run from the repository root in a Python environment with the project dependencies:

```bash
python -m pip install -r part5/requirements_lock.txt
python part5/python_source/run_part5.py
```

`requirements_lock.txt` records the seven direct package versions actually used; the recorded environment used Python 3.12. The code also works with suitable existing project dependencies. On this workstation the bundled Codex Python was used, and the missing analysis packages were installed in the ignored `part5/.deps/` directory. Do not commit that directory or add it to another Python version's environment.

The runner generates all numeric exhibits and both Word files, performs 29 numerical/scope checks, records input SHA-256 hashes and package versions, and prints the results. It can also be called from another working directory using its resolved script path. It never reruns Part 1 notebooks or writes Part 1 outputs.

To inspect individual stages:

```bash
python part5/python_source/question_5B.py
python part5/python_source/question_5C.py
python part5/python_source/question_5D.py
python part5/python_source/question_5E.py
python part5/python_source/question_5F.py
python part5/python_source/build_part5_docs.py
```

The common loader verifies all months, units, original workbook headers, index identities and Part 1 CSV reconciliation each time. 5C and 5D estimate the same 5B model when invoked alone; 5F regenerates its 5E inputs when invoked alone. The document builder reads saved Part 5 tables and figures; run the complete pipeline first.

**Rerunning overwrites Part 5 generated outputs**, including the two Word files and generated Markdown/JSON. Keep manual edits in a separate copy, or edit the document builder so changes remain reproducible.

## Annualization and interpretation

- Return = 12 × monthly mean. Volatility = sample standard deviation × √12, ddof = 1.
- Sharpe = [12 × mean(strategy) − 12 × mean(FF RF)] / annualized **total-return** volatility, as assignment footnote 2 specifies. Do not subtract a fitted RF allocation instead of the actual RF return.
- Active return = strategy minus MSCI USA. Annual tracking error = √12 × std(active); information ratio = annual mean active return / annual tracking error.
- Relative wealth = product(1 + strategy return) / product(1 + benchmark return) − 1. Neither compounding nor summing monthly active differences produces this ratio.
- 5B uses total MSCI Value returns, explicitly estimated RF, an intercept, and the three FF spreads. 5D omits the intercept without renormalizing or refitting the slopes. These slopes are exposures, not four conventional fully invested fund weights. Full-sample estimation makes replication an in-sample exercise.
- 5F uses `0.25 × Cov(active_i, active_multi)` and divides by `Var(active_multi)` for shares. Annual contributions multiply monthly contributions by 12. Negative covariance contributions would remain negative. Allocating volatility itself would require dividing annual variance contributions by annual tracking error; those are different units.

## Rendering and validation

The packaged `render_docx.py` was attempted but could not find LibreOffice. This Windows host has Microsoft Word; all report and exhibit pages were therefore rendered read-only with Word's native PDF export, rasterized with the bundled PDFium library, and visually inspected. The reference Part 3 documents were inspected the same way. Native editable Word math is used for the variance equations.

To repeat native rendering on a Windows machine with Word installed:

```powershell
& part5/python_source/render_word_qa.ps1
python part5/python_source/render_pdf_qa.py
```

The Word renderer starts a hidden automation instance, opens source documents read-only, exports QA PDFs and closes that instance. It does not modify the DOCX sources. Intermediate PDFs, page images, dependency files and font caches are ignored, and are not submission deliverables.

## File inventory

| Path | Purpose |
|---|---|
| `python_source/part5_common.py` | Paths, validated data loader, precision, OLS helper |
| `python_source/question_5A.md` | Source-based methodology explanation |
| `python_source/question_5B.py` … `question_5F.py` | Question-specific analysis and charts |
| `python_source/run_part5.py` | Complete reproducible workflow and independent validation |
| `python_source/build_part5_docs.py` | Word/report text builder reading saved CSVs |
| `python_source/render_word_qa.ps1`, `render_pdf_qa.py` | Optional native Word/PDFium visual QA |
| `documents/Part5_report.docx`, `Part5_exhibits.docx` | Submission-ready report and exhibit appendix |
| `documents/Part5_report.md` | Generated text companion |
| `documents/validation_results.json`, `validation_notes.md` | Machine-readable checks and review notes |
| `requirements_lock.txt`, `.gitignore`, `README.md` | Reproduction, local-file exclusions and instructions |
| `output/tables/tab_5B_regression.csv` | Coefficients, standard errors, t, p, confidence intervals |
| `output/tables/tab_5B_model_summary.csv` | N, residual df, R², adjusted R² and inference type |
| `output/tables/tab_5B_regression_inputs.csv` | Aligned dependent variable and four regressors |
| `output/tables/tab_5C_alpha.csv` | Alpha magnitude, significance and annual confidence interval |
| `output/tables/tab_5D_replication_performance.csv` | Original-versus-replication performance |
| `output/tables/tab_5D_replication_monthly.csv` | Monthly replication, factor legs, RF, gap and residual |
| `output/tables/tab_5E_active_performance.csv` | Annual relative metrics for all five strategies |
| `output/tables/tab_5E_active_monthly.csv` | Monthly active returns for all five strategies |
| `output/tables/tab_5E_relative_wealth_monthly.csv` | Compounded relative wealth paths |
| `output/tables/tab_5F_risk_decomposition.csv` | Absolute variance contributions and shares |
| `output/tables/tab_5F_active_covariance.csv` | Sample component-active covariance matrix |
| `output/tables/tab_5_data_reconciliation.csv` | Full-precision-versus-Part-1-export checks |
| `output/tables/tab_5_validated_monthly_returns.csv` | Full-precision Part 1C series for audit |
| `output/figures/fig_5D_replication.png` | Compounded dollar growth |
| `output/figures/fig_5E_active_performance.png` | Compounded relative wealth |
| `output/figures/fig_5F_risk_decomposition.png` | Signed active-variance contribution chart |

No essential assignment or data files are missing. Class lecture slides are not in the repository, so the discussion of limits to arbitrage cites Shleifer and Vishny (1997) and does not invent a lecture quotation or class-specific information-ratio threshold. The current runner is deterministic for the supplied historical workbook; it does not download or replace returns with a revised external data vintage.

## Commit later after review

No commit or push has been performed. From the repository root:

```bash
git status --short
git add -- part5 'output/tables/tab_5*.csv' 'output/figures/fig_5*.png'
git diff --cached --stat
git diff --cached --name-only
git commit -m "Complete Part 5 portfolio analytics and reports"
git push
```

Check the staged file list before committing. It should include only `part5/` and Part 5 outputs. Parts 1–4, shared source, original data, remotes and existing outputs are unchanged.
