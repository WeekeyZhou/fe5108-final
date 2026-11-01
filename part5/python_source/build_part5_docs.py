"""Build concise English report and exhibit appendix from saved Part 5 CSVs.

Reuse Part 3's actual Word section/style definitions; never modify the reference.
All numerical prose is interpolated from full-precision saved analysis outputs.
"""
from __future__ import annotations

import re
from part5_common import ROOT, PART5, LABELS, config, read_saved
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.shared import Inches, Pt, RGBColor
import pandas as pd

DOCS = PART5 / "documents"
MSCI = "https://www.msci.com/eqb/methodology/meth_docs/MSCI_GIMIVGMethod_Feb2021.pdf"
FRENCH = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/f-f_factors.html"
SV = "https://doi.org/10.1111/j.1540-6261.1997.tb03807.x"
SCOPE = ("Source and scope: supplied MSCI / Kenneth French workbook; US large/mid-cap MSCI indexes "
         "(gross total returns, USD) and US academic factors where applicable; Jan 1995 - Jul 2023 (343 months). ")


def pct(x, digits=2):
    return f"{100*x:.{digits}f}%"


def document(title):
    d = Document(ROOT / "part3/documents/Part3_report.docx")
    for child in list(d.element.body):
        if child.tag != qn("w:sectPr"):
            d.element.body.remove(child)
    d.core_properties.title = title
    d.core_properties.author = "FE5108 Part 5"
    for style in ["Normal", "Title", "Heading 1", "Heading 2"]:
        d.styles[style].font.color.rgb = RGBColor(0, 0, 0)
    d.add_paragraph(title, "Title")
    return d


def note(d, text, size=8):
    p = d.add_paragraph(text)
    p.paragraph_format.space_after = Pt(5)
    for run in p.runs:
        run.font.size = Pt(size)
        run.font.color.rgb = RGBColor.from_string("555555")
    return p


def hyperlink(p, label, url):
    rel = p.part.relate_to(url, RT.HYPERLINK, is_external=True)
    element = OxmlElement("w:hyperlink")
    element.set(qn("r:id"), rel)
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    size = OxmlElement("w:sz"); size.set(qn("w:val"), "16"); props.append(size)
    run.append(props)
    text = OxmlElement("w:t"); text.text = label; run.append(text)
    element.append(run)
    p._p.append(element)


def table(d, frame, widths, highlight=()):
    t = d.add_table(rows=1, cols=len(frame.columns))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for col, width in zip(t.columns, widths):
        col.width = Inches(width)
    for cell, text in zip(t.rows[0].cells, frame.columns):
        cell.text = str(text)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
    for values in frame.itertuples(index=False, name=None):
        for cell, value in zip(t.add_row().cells, values):
            cell.text = str(value)
    for ri, row in enumerate(t.rows):
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for ci, cell in enumerate(row.cells):
            cell.width = Inches(widths[ci])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            pr = cell._tc.get_or_add_tcPr()
            borders = OxmlElement("w:tcBorders")
            for side in ["top", "bottom", "left", "right"]:
                edge = OxmlElement("w:" + side)
                for name, value in [("val", "single"), ("sz", "4"), ("color", "D9D9D9")]:
                    edge.set(qn("w:" + name), value)
                borders.append(edge)
            pr.append(borders)
            margins = OxmlElement("w:tcMar")
            for side in ["top", "bottom", "left", "right"]:
                edge = OxmlElement("w:" + side)
                edge.set(qn("w:w"), "70"); edge.set(qn("w:type"), "dxa")
                margins.append(edge)
            pr.append(margins)
            fill = "E8EEF2" if ri == 0 else "D9EEE8" if (ri - 1) in highlight else None
            if fill:
                shade = OxmlElement("w:shd"); shade.set(qn("w:fill"), fill); pr.append(shade)
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.size = Pt(8)
                    run.bold = ri == 0 or (ri - 1) in highlight
    return t


def equation(d, text):
    """Native editable Word math, for simple linear equations without fractions."""
    p = d.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    math = OxmlElement("m:oMath")
    run = OxmlElement("m:r")
    token = OxmlElement("m:t"); token.text = text
    run.append(token); math.append(run); p._p.append(math)
    return p


def figure(d, filename):
    # Respect native 300-dpi printed size; do not rescale figures in Word.
    shape = d.add_picture(str(config.FIG_DIR / filename))
    if shape.width.inches > 6.27:
        raise ValueError(f"Figure exceeds page width: {filename}")


def build():
    DOCS.mkdir(parents=True, exist_ok=True)
    reg = read_saved("tab_5B_regression", index_col="term")
    summary = read_saved("tab_5B_model_summary").iloc[0]
    alpha = read_saved("tab_5C_alpha").iloc[0]
    perf = read_saved("tab_5D_replication_performance", index_col="strategy")
    active = read_saved("tab_5E_active_performance", index_col="strategy")
    risk = read_saved("tab_5F_risk_decomposition", index_col="component")
    mf = active.loc["MultiFactor"]
    ms, rep = perf.loc["MSCI_Value"], perf.loc["Replication"]
    r = document("Part 5 Portfolio Analytics")
    sections = []

    def section(title, text):
        r.add_heading(title, level=1)
        r.add_paragraph(text)
        sections.append((title, text))

    section("5A Factor composite definitions",
        "MSCI averages book value/price, forward 12-month earnings/price and dividend-yield z-scores to define value. "
        "Growth uses long- and short-term forecast EPS growth, internal growth (ROE times earnings retention), "
        "and historical EPS and sales-per-share trends. Standard indexes double-weight long-term forecast growth. "
        "Value and growth are separate dimensions, so a security may have both characteristics and partial inclusion in both indexes. "
        "Small Cap omits long-term forecast growth. Banks and Diversified Financials omit sales growth, except Multi-Sector Holdings "
        "and Financial Exchanges & Data. Missing signals are excluded and remaining weights renormalized; share-class dividend "
        "differences can change internal growth. Economically, these exceptions accommodate differences in accounting relevance "
        "and data availability. Fama-French HML instead uses book-to-market alone: average small- and big-value returns minus "
        "average small- and big-growth returns. HML is a long-short spread; MSCI USA Value is a long-only, free-float-weighted "
        "large/mid-cap style index (MSCI, 2021, Sections 1.2, 2.1-2.3; French Data Library).")
    section("5B Identifying strategy factor exposures",
        "Using all 343 months from January 1995 to July 2023, we regress gross USD MSCI Value total returns on an intercept, "
        "RF, Mkt-RF, HML and SMB, in decimal units. One index provides a time series, so the assignment's pooled-panel wording "
        "is implemented as time-series OLS. Conventional standard errors are used without Newey-West adjustment. "
        f"Market exposure is {reg.loc['Mkt-RF','coefficient']:.3f}, HML {reg.loc['HML','coefficient']:.3f}, "
        f"and SMB {reg.loc['SMB','coefficient']:.3f}, all significant at 1%. The positive value tilt and large-cap bias are as advertised "
        f"(R² = {pct(summary.r_squared)}). RF exposure is {reg.loc['RF','coefficient']:.3f}; it is estimated rather than fixed at one (Table 5.1).")
    section("5C Enhancing factor performance",
        f"The intercept is {pct(alpha.alpha_monthly_decimal,3)} monthly, or {pct(alpha.alpha_annual_arithmetic_decimal)} "
        f"per year arithmetically ({alpha.alpha_annual_arithmetic_basis_points:.1f} basis points). It equals the mean return gap "
        f"between MSCI Value and its intercept-excluding replication. With t = {alpha.t_statistic:.3f} and p = {alpha.p_value:.3f}, "
        f"it is not statistically significant; the annualized 95% interval is [{pct(alpha.ci95_annual_lower_decimal)}, "
        f"{pct(alpha.ci95_annual_upper_decimal)}]. The estimate is economically unfavorable, but the uncertainty does not establish "
        "underperformance. There is no evidence here that MSCI's elaboration improves returns beyond these factor exposures; "
        "the regression does not identify a causal methodology effect.")
    section("5D Fund replication",
        f"We sum each same-month factor return times its estimated slope, excluding alpha. Correlation with MSCI Value is "
        f"{rep.correlation_with_msci_value:.3f}, indicating effective in-sample replication (Figure 5.1). Replication earns "
        f"{pct(rep.annual_arithmetic_return_decimal)} annually versus {pct(ms.annual_arithmetic_return_decimal)}, "
        f"with volatility of {pct(rep.annual_volatility_decimal)} versus {pct(ms.annual_volatility_decimal)} and Sharpe ratios "
        f"of {rep.sharpe_ratio:.3f} versus {ms.sharpe_ratio:.3f} (Table 5.2). Arithmetic returns are monthly means times 12; "
        "volatility is sample monthly standard deviation times √12. Sharpe subtracts the aligned FF risk-free mean and divides "
        "by total-return volatility, following assignment footnote 2. Replication ranks better historically before costs. "
        "Selection still requires evaluating turnover and fees, shorting/financing and liquidity, and out-of-sample stability. "
        "These unconstrained loadings on academic spreads do not define an automatically tradable, fully invested portfolio.")
    section("5E Relative performance analysis",
        "We reuse Part 1C's monthly-rebalanced average of Value, Minimum Volatility, Equal Weight and Momentum, "
        "restoring unrounded values from the original levels and reconciling the rounded CSV. Active returns subtract MSCI USA. "
        f"The multi-factor portfolio earns {pct(mf.annual_active_return_arithmetic_decimal,3)} per year actively, "
        f"with {pct(mf.annual_tracking_error_decimal)} tracking error and information ratio {mf.information_ratio:.3f} "
        "(Table 5.3). The reward is small relative to benchmark risk despite the improved absolute Sharpe in Part 1C. "
        f"Compounded relative wealth gains {pct(mf.cumulative_relative_wealth_gain_decimal)} over the full sample "
        "(Figure 5.2); this wealth ratio is distinct from annualized mean active return.")
    section("5F Risk decomposition",
        "For each component, active-variance contribution equals 0.25 times its covariance with multi-factor active returns. "
        f"Minimum Volatility contributes the most ({risk.loc['MinVol','variance_contribution_percent']:.1f}%), followed by "
        f"Momentum ({risk.loc['Momentum','variance_contribution_percent']:.1f}%), Value ({risk.loc['Value','variance_contribution_percent']:.1f}%) "
        f"and Equal Weight ({risk.loc['EqualWeight','variance_contribution_percent']:.1f}%). Contributions sum exactly to sample active variance "
        "within floating-point tolerance; all are positive here (Table 5.4; Figure 5.3). These allocate variance, not volatility. "
        "Minimum Volatility is more natural as a standalone defensive equity allocation for investors focused on absolute risk. "
        "Its defensive exposure can lag a rising benchmark and strain tracking-error budgets. Such relative losses may trigger "
        "redemptions or manager dismissal before recovery, illustrating limits to arbitrage through constrained investor capital "
        "(Shleifer and Vishny, 1997). Suitability still depends on mandate and costs.")
    note(r, "References: MSCI (2021), Global Investable Market Value and Growth Index Methodology, February; "
         "Kenneth R. French Data Library, Description of Fama/French Factors; Shleifer, A. and Vishny, R. W. (1997), "
         "The Limits of Arbitrage, Journal of Finance 52(1), 35-55. Links and methodological details appear in the exhibit appendix.", size=8)
    r.save(DOCS / "Part5_report.docx")
    (DOCS / "Part5_report.md").write_text("# Part 5 Portfolio Analytics\n\n" + "\n\n".join(
        f"## {heading}\n\n{text}" for heading, text in sections) + "\n", encoding="utf-8")

    d = document("Part 5 Selected Exhibits")
    note(d, "These exhibits evaluate value-index replication and benchmark-relative multi-factor risk. "
         "The factor fit explains most Value variation, while the multi-factor portfolio earns little per unit of tracking error.", 9)
    d.add_heading("Table 5.1 MSCI Value factor attribution", 1)
    rows = []
    for term, row in reg.iterrows():
        rows.append(["Intercept (decimal/month)" if term == "const" else term,
                     f"{row.coefficient:.6f}", f"{row.standard_error:.6f}", f"{row.t_statistic:.3f}",
                     f"{row.p_value:.3g}"])
    table(d, pd.DataFrame(rows, columns=["Term", "Coefficient", "Std error", "t statistic", "p value"]),
          [2.1, 1.04, 1.04, 1.04, 1.04])
    note(d, SCOPE + "OLS on total returns with an intercept. Slopes are dimensionless; the intercept is a monthly decimal return. "
         f"N = {int(summary.nobs)}, residual df = {int(summary.residual_df)}, R² = {summary.r_squared:.6f}, adjusted R² = {summary.adjusted_r_squared:.6f}. "
         "Standard errors and two-sided Student t tests are conventional, without HAC/Newey-West adjustment. "
         f"Annual arithmetic alpha = {pct(alpha.alpha_annual_arithmetic_decimal)}; 95% interval "
         f"[{pct(alpha.ci95_annual_lower_decimal)}, {pct(alpha.ci95_annual_upper_decimal)}].")
    d.add_heading("Table 5.2 Replication and original index performance", 1)
    rows = [[label, pct(rec.annual_arithmetic_return_decimal), pct(rec.annual_volatility_decimal),
             f"{rec.sharpe_ratio:.3f}", pct(rec.annual_geometric_return_decimal)]
            for label, rec in [("MSCI USA Value", ms), ("Factor replication", rep)]]
    table(d, pd.DataFrame(rows, columns=["Strategy", "Annual return\narithmetic", "Annual\nvolatility", "Sharpe\nratio", "Annual return\ngeometric"]),
          [2.1, 1.04, 1.04, 1.04, 1.04])
    note(d, SCOPE + f"Correlation = {rep.correlation_with_msci_value:.6f}. Replication excludes alpha and uses full-sample slopes. "
         f"Annual mean RF = {pct(ms.annual_risk_free_return_decimal)}. Return = 12 × monthly mean; volatility = sample std × √12; "
         "Sharpe = (annual arithmetic return - annual mean RF) / annual volatility. Geometric return is compounded wealth^(12/343) - 1. "
         "All results are gross of costs; replication is an in-sample statistical portfolio, not an investability claim.")
    d.add_heading("Figure 5.1 Growth of one dollar", 1)
    figure(d, "fig_5D_replication.png")

    d.add_page_break()
    d.add_heading("Table 5.3 Benchmark relative performance", 1)
    rows = [[LABELS[name], pct(rec.annual_active_return_arithmetic_decimal,3), pct(rec.annual_tracking_error_decimal),
             f"{rec.information_ratio:.3f}", pct(rec.cumulative_relative_wealth_gain_decimal)] for name, rec in active.iterrows()]
    table(d, pd.DataFrame(rows, columns=["Strategy", "Annual active\nreturn", "Annual tracking\nerror", "Information\nratio", "Cumulative relative\nwealth gain"]),
          [1.65, 1.15, 1.15, 1.0, 1.31], highlight=(4,))
    note(d, SCOPE + "Benchmark: MSCI USA Standard. All strategies hold long-only MSCI indexes. Multi-factor weights are 25% each, reset monthly. "
         "Monthly active return = strategy return - benchmark return; annual active return = 12 × mean(active); "
         "tracking error = sample std(active) × √12; information ratio = annual active return / tracking error. "
         "These annualizations do not adjust for serial correlation.")
    d.add_heading("Figure 5.2 Compounded performance relative to the benchmark", 1)
    figure(d, "fig_5E_active_performance.png")
    note(d, "Relative wealth = product(1 + strategy return) / product(1 + benchmark return) - 1. "
         "It is neither the sum nor the compounded product of monthly active returns. For the multi-factor portfolio, "
         f"the cumulative gain is {pct(mf.cumulative_relative_wealth_gain_decimal)} and the annual relative-wealth growth rate is "
         f"{pct(mf.annual_relative_wealth_growth_decimal,3)}, versus {pct(mf.annual_active_return_arithmetic_decimal,3)} annualized arithmetic active return.")
    d.add_heading("Data precision and alignment", 1)
    note(d, "The workbook labels the MSCI levels Gross and USD. December 1994 levels provide the base for January 1995 returns; "
         "all 343 months are present and aligned with monthly FF percentage data divided by 100. Annual FF rows and MSCI copyright footers are excluded. "
         "Part 1C's exported monthly CSV rounds to four decimals. Every recovered return differs from its saved value by at most 0.5 basis point. "
         "Its rounded multi-factor column can differ from the mean of rounded components by 0.75 basis point. "
         "We therefore recover Part 1C's full-precision calculation without changing its inputs, algorithm or files. "
         "All original Part 1 performance statistics reconcile to saved-table rounding. Raw input hashes and numerical checks are saved separately.", 9)

    d.add_page_break()
    d.add_heading("Table 5.4 Contributions to multi factor active variance", 1)
    rows = [[LABELS[name], "25%", f"{rec.monthly_variance_contribution_decimal_squared:.9f}",
             f"{rec.annual_variance_contribution_decimal_squared:.9f}", f"{rec.variance_contribution_percent:.2f}%"]
            for name, rec in risk.iterrows()]
    rows.append(["Total", "100%", f"{risk.monthly_variance_contribution_decimal_squared.sum():.9f}",
                 f"{risk.annual_variance_contribution_decimal_squared.sum():.9f}", "100.00%"])
    table(d, pd.DataFrame(rows, columns=["Component", "Weight", "Monthly variance\ncontribution", "Annual variance\ncontribution", "Variance\nshare"]),
          [1.65, 0.65, 1.45, 1.45, 1.06], highlight=(1,4))
    note(d, SCOPE + "All covariances use benchmark-relative active returns and sample ddof = 1. Absolute contributions are in squared decimal-return units. "
         "Annual variance contributions = 12 × monthly contributions. Percentages use monthly multi-factor active variance as denominator.")
    equation(d, "aₘ = 0.25(aᵥ + aₗ + aₑ + aₚ)")
    equation(d, "Cᵢ = 0.25 Cov(aᵢ, aₘ)     Σᵢ Cᵢ = Var(aₘ)     Shareᵢ = Cᵢ / Var(aₘ)")
    note(d, "Here a denotes a monthly strategy-minus-benchmark return; subscripts v, l, e and p denote Value, Minimum Volatility, "
         "Equal Weight and Momentum. Covariance contributions may be negative and must not be clipped. "
         "This is a decomposition of tracking-error squared. Contributions to tracking error itself would instead equal "
         "annual variance contributions divided by annual tracking error and would have return, not squared-return, units.")
    d.add_heading("Figure 5.3 Allocation of benchmark relative risk", 1)
    figure(d, "fig_5F_risk_decomposition.png")
    d.add_heading("Sources and interpretation", 1)
    for label, url in [("MSCI (February 2021), Global Investable Market Value and Growth Index Methodology, Sections 1.2, 2.1-2.3 and Appendix I.", MSCI),
                       ("Kenneth R. French Data Library, Description of Fama/French Factors.", FRENCH),
                       ("Shleifer, A. and Vishny, R. W. (1997), The Limits of Arbitrage, Journal of Finance 52(1), 35-55.", SV)]:
        p = note(d, "", 8)
        hyperlink(p, label, url)
    note(d, "Sources accessed 1 November 2026. The assignment specifies the February 2021 MSCI methodology; "
         "we do not assume its rules were unchanged across the historical return sample. The limits-to-arbitrage interpretation "
         "applies the cited capital-constraint mechanism; class lecture slides were not included in the repository.")
    d.save(DOCS / "Part5_exhibits.docx")

    # Structural delivery checks, including all six answers and four tables/three figures.
    report_check = Document(DOCS / "Part5_report.docx")
    exhibit_check = Document(DOCS / "Part5_exhibits.docx")
    assert len(exhibit_check.tables) == 4
    assert len(exhibit_check.inline_shapes) == 3
    assert all(any(p.text.startswith(q) for p in report_check.paragraphs) for q in ["5A", "5B", "5C", "5D", "5E", "5F"])
    body_words = len(re.findall(r"\S+", " ".join(text for _, text in sections)))
    return {"body_words": body_words, "exhibit_tables": 4, "exhibit_figures": 3}


if __name__ == "__main__":
    print(build())
