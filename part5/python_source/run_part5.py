"""Reproduce all Part 5 numeric exhibits, validation, and the two Word files."""
import json
from importlib.metadata import version
from part5_common import (ROOT, PART5, MONTHS, COMPONENTS, FACTORS, config, utils,
                          load_inputs, save, sha256)
import numpy as np
import pandas as pd
import question_5B as b
import question_5C as c
import question_5D as d
import question_5E as e
import question_5F as f


def main():
    # Record every tracked non-Part-5 file, so scope preservation is auditable.
    import subprocess
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    protected = {p: sha256(ROOT / p) for p in tracked if p and not (
        p.startswith("part5/") or p.startswith("output/tables/tab_5") or p.startswith("output/figures/fig_5"))
        and (ROOT / p).is_file()}
    r, ff, audit, rounded_error = load_inputs()
    save(audit, "tab_5_data_reconciliation")
    save(r, "tab_5_validated_monthly_returns")
    model = b.run(r, ff)
    alpha = c.run(model)
    monthly, perf = d.run(r, ff, model)
    active, aperf = e.run(r)
    risk = f.run(active)
    checks = {}

    def verify(name, condition):
        if not bool(condition):
            raise AssertionError(name)
        checks[name] = "PASS"

    verify("343 consecutive common months, no missing values", len(r) == 343 and r.index.equals(ff.index))
    verify("Part1 CSV differences within four-place rounding", audit.iloc[:, 0].max() <= 0.000050000001)
    verify("full-precision equal-weight identity", np.allclose(r.MultiFactor, r[COMPONENTS].mean(axis=1), rtol=0, atol=1e-15))
    x = np.column_stack([np.ones(len(ff)), ff[FACTORS].to_numpy()])
    y = r.Value.to_numpy()
    beta, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    residual = y - x @ beta
    covariance = residual @ residual / (len(y) - x.shape[1]) * np.linalg.inv(x.T @ x)
    verify("OLS independently matches numpy least squares", np.allclose(beta, model.params, rtol=0, atol=1e-12))
    verify("OLS standard errors match independent covariance", np.allclose(np.sqrt(np.diag(covariance)), model.bse, rtol=1e-10))
    from scipy.stats import t
    pvalues = 2 * t.sf(np.abs(beta / np.sqrt(np.diag(covariance))), df=len(y) - len(beta))
    verify("OLS p values match Student t with 338 residual df", np.allclose(pvalues, model.pvalues, rtol=1e-9, atol=1e-300))
    verify("OLS design full rank and conventional covariance", rank == 5 and model.cov_type == "nonrobust")
    verify("replication excludes intercept", np.allclose(monthly.Replication, ff[FACTORS].to_numpy() @ beta[1:], atol=1e-14))
    verify("mean replication gap equals alpha", abs(monthly.Value_minus_replication.mean() - beta[0]) < 1e-14)
    verify("replication gap equals alpha plus residual", np.allclose(monthly.Value_minus_replication, model.params["const"] + model.resid, atol=1e-14))
    verify("correlation squared equals OLS R squared", abs(monthly.MSCI_Value.corr(monthly.Replication)**2 - model.rsquared) < 1e-12)
    for name in perf.index:
        z = monthly[name]
        verify(f"{name} annualization and Sharpe", np.allclose(
            perf.loc[name, ["annual_arithmetic_return_decimal", "annual_volatility_decimal", "sharpe_ratio"]].to_numpy(dtype=float),
            [12*z.mean(), np.sqrt(12)*z.std(ddof=1), np.sqrt(12)*(z.mean()-ff.RF.mean())/z.std(ddof=1)]))
    part1_perf = pd.read_csv(config.TAB_DIR / "tab_1C_performance.csv", index_col="Strategy")
    for name in r.columns:
        actual = [100*utils.annualized_return(r[name], "arithmetic"), 100*utils.annualized_volatility(r[name]),
                  utils.sharpe_ratio(r[name], ff.RF, "arithmetic")]
        verify(f"{name} matches Part1 performance CSV rounding", np.max(np.abs(
            np.asarray(actual) - part1_perf.loc[name].to_numpy(dtype=float))) <= 0.000050000001)
    variance = active.MultiFactor.var(ddof=1)
    verify("active returns equal strategy minus benchmark", np.allclose(active.MultiFactor, r.MultiFactor - r.Market, rtol=0, atol=1e-15))
    verify("annual active return equals difference of annual means", abs(aperf.loc["MultiFactor", "annual_active_return_arithmetic_decimal"] - 12*(r.MultiFactor.mean()-r.Market.mean())) < 1e-14)
    verify("covariance contributions sum to monthly active variance", np.isclose(risk.iloc[:, 1].sum(), variance, rtol=1e-12))
    verify("variance shares sum to one", abs(risk.variance_share.sum() - 1) < 1e-12)
    weights = np.full(4, 0.25)
    verify("independent covariance quadratic form", np.isclose(weights @ active[COMPONENTS].cov().to_numpy() @ weights, variance, rtol=1e-12))
    verify("annual variance equals annual tracking error squared", np.isclose(12*variance, aperf.loc["MultiFactor", "annual_tracking_error_decimal"]**2, rtol=1e-12))
    # A meaningful edge case: a hedge may have a negative contribution.
    z = np.arange(1., 9.)
    hedge = pd.DataFrame(dict(zip(COMPONENTS, [z, -0.2*z, 0.5*z, 0.5*z])))
    hedge["MultiFactor"] = hedge.mean(axis=1)
    hedge_decomp = f.decompose(hedge)
    verify("negative covariance contributions are retained", hedge_decomp.loc["MinVol", "variance_share"] < 0 and np.isclose(hedge_decomp.variance_share.sum(), 1))
    from build_part5_docs import build
    doc_info = build()
    expected_tables = ["5_data_reconciliation", "5_validated_monthly_returns", "5B_regression",
                       "5B_model_summary", "5B_regression_inputs", "5C_alpha", "5D_replication_monthly",
                       "5D_replication_performance", "5E_active_monthly", "5E_relative_wealth_monthly",
                       "5E_active_performance", "5F_risk_decomposition", "5F_active_covariance"]
    verify("all 13 requested and supporting CSVs exist", all(
        (config.TAB_DIR / f"tab_{name}.csv").is_file() for name in expected_tables))
    verify("all 3 figures and 2 Word documents exist", all(path.is_file() for path in [
        *(config.FIG_DIR / f"fig_{name}.png" for name in ["5D_replication", "5E_active_performance", "5F_risk_decomposition"]),
        *(PART5 / "documents" / name for name in ["Part5_report.docx", "Part5_exhibits.docx"])]))
    verify("all protected tracked files unchanged", all(sha256(ROOT / p) == digest for p, digest in protected.items()))
    versions = {pkg: version(pkg) for pkg in ["numpy", "pandas", "scipy", "statsmodels", "matplotlib", "openpyxl", "python-docx"]}
    (PART5 / "requirements_lock.txt").write_text("\n".join(f"{k}=={v}" for k, v in versions.items()) + "\n", encoding="utf-8")
    inputs = [config.FILE_FF_MSCI, config.TAB_DIR/"tab_1C_monthly_returns.csv", config.TAB_DIR/"tab_1A_factor_spreads.csv",
              config.TAB_DIR/"tab_1C_performance.csv", ROOT/"part1/python_source/question_1C.ipynb",
              ROOT/"Read it before you do!/class project (fall 2026) (in full).pdf"]
    output = {"sample": {"start": str(MONTHS[0]), "end": str(MONTHS[-1]), "nobs": len(MONTHS)},
              "checks": checks, "versions": versions,
              "input_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in inputs},
              "max_rounded_csv_equal_weight_error_decimal": rounded_error,
              "variance_monthly_decimal_squared": variance,
              "sum_contributions_monthly_decimal_squared": float(risk.iloc[:, 1].sum()),
              "variance_identity_error_decimal_squared": float(risk.iloc[:, 1].sum() - variance),
              "documents": doc_info,
              "visual_qa": "Separate render-and-inspect workflow; see part5/documents/validation_notes.md."}
    (PART5 / "documents/validation_results.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(model.summary())
    print("\nREPLICATION\n", perf.to_string())
    print("\nACTIVE PERFORMANCE\n", aperf.to_string())
    print("\nRISK CONTRIBUTIONS\n", risk.to_string())
    print(f"\n{len(checks)} numerical/scope checks passed; body words: {doc_info['body_words']}.")


if __name__ == "__main__":
    main()
