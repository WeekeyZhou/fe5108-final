# Part 5 validation notes

Completed 1 November 2026. Numerical checks are reproduced by `python part5/python_source/run_part5.py`; exact inputs, package versions and computed quantities are in `validation_results.json`.

## Inputs

All essential files were present: the ten-page official assignment, source workbook, Part 1 notebooks and CSV outputs, and Part 1/3 report examples. Official Part 5 is on pages 9–10 and is worth 26/100, superseding the provisional team plan. The complete project README, shared conventions and Part 5 placeholder were reviewed.

The MSCI source identifies Gross USD total-return levels. December 1994 is available as the first return's base. We retain exactly 343 unique, consecutive and complete monthly observations, January 1995–July 2023. FF observations are the supplied historical monthly series in percent, converted to decimals. MSCI copyright footers and FF annual observations are excluded. No observations are filled or invented.

The four-decimal Part 1 return export is a presentation artifact. Its maximum discrepancy from the mean of its rounded components is 0.000075 decimal return (0.75 basis point). Part 5 recovers Part 1C's original unrounded calculation from the same workbook and reconciles every exported cell within 0.00005 (0.5 basis point), then verifies all six original annual performance rows to their saved-table rounding. Existing Part 1 outputs remain untouched.

## Numerical evidence

The final run passes **29 checks**, including:

- An independent `numpy.linalg.lstsq` calculation of all five OLS coefficients.
- Independent conventional coefficient covariance and standard errors; Student-t p values with 338 residual degrees of freedom.
- Full-rank design, intercept, explicitly estimated RF and conventional non-HAC inference.
- Replication equals the four weighted factor series without alpha; mean Value-minus-replication equals alpha; the monthly gap equals alpha plus the residual; squared correlation equals regression R².
- Arithmetic return, sample volatility and the assignment's Sharpe formula with aligned FF RF.
- Active-return and annualization identities; tracking-error squared agrees with annual active variance.
- Covariance decomposition, independent covariance quadratic form and percentage shares summing to one.
- A synthetic hedge check showing that negative risk contributions remain negative.
- All 13 CSVs, three charts and two requested Word documents exist.
- SHA-256 comparison verifies that every previously tracked file outside the authorized Part 5 scope remains unchanged during execution.

Monthly active variance and the sum of contributions both equal approximately **0.00009558134087859056**, in squared decimal-return units. The final numeric run reports an identity error of zero at its stored floating-point precision. Displayed table entries are rounded; calculate the identity from full-precision CSV values rather than rounded Word cells.

Both Word files are generated directly from saved CSVs. The report has all six answers; the appendix has four tables, three embedded charts, linked source references and native editable math equations. No numerical results are manually entered in the report builder.

## Visual verification

The packaged DOCX renderer was attempted and failed with `FileNotFoundError: LibreOffice soffice.exe was not found on PATH`. Microsoft Word was available, so the reference Part 3 report and exhibits were exported read-only to PDFs and rasterized with bundled `pypdfium2`. The same process was applied to both Part 5 documents.

All two report pages, all three exhibit pages and all three standalone 300-dpi figures were inspected. Tables, source notes, legends, equations and plotted labels are readable; no text is clipped or overlapping. The documents retain the Part 3 A4/Arial style with black headings and light blue table headers. Figures are inserted at their native printed dimensions.

QA PDFs and page PNGs are under the ignored `part5/.qa/` directory and are not submission deliverables. The Word sources are not saved or edited by the renderer.

## Interpretation limits

- No essential inputs are missing. Class slides were not supplied. The limits-to-arbitrage discussion uses the cited primary academic paper rather than attributing specific statements to an unavailable lecture.
- The MSCI methodology source is the February 2021 version requested by the assignment. Its description is not a claim that every historical index return used those exact rules.
- The assignment calls for a panel regression but supplies one dependent return series. The implemented model is monthly time-series OLS; no artificial panel observations are created.
- Classical inference is deliberately unadjusted as instructed. It relies on the usual OLS error assumptions.
- Replication coefficients are estimated in the full sample, without trading costs, funding constraints or investable factor proxies. Better gross in-sample Sharpe is not proof of a feasible live strategy or a statistically significant alpha difference.
- No shared files, Parts 1–4, raw data or original outputs were modified; no Git commit or push was performed.
