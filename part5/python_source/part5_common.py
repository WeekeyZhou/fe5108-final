"""Validated Part 1 inputs and shared conventions for Questions 5A--5F.

The Part 1 CSV is a rounded exhibit (four decimal places). We recover its
unrounded series from the original levels using precisely the Part 1C method,
then reconcile every cell. No Part 1 files are changed or executed for export.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PART5 = ROOT / "part5"
# Optional task-local dependencies; a normal project Python environment also works.
if (PART5 / ".deps").is_dir():
    sys.path.insert(0, str(PART5 / ".deps"))
sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(PART5 / ".mplconfig"))

import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd
from src import config, utils

MONTHS = pd.period_range("1995-01", "2023-07", freq="M", name="month")
LEVEL_MONTHS = pd.period_range("1994-12", "2023-07", freq="M", name="month")
COMPONENTS = ["Value", "MinVol", "EqualWeight", "Momentum"]
FACTORS = ["RF", "Mkt-RF", "HML", "SMB"]
LABELS = {"Market": "MSCI USA", "Value": "Value", "MinVol": "Minimum volatility",
          "EqualWeight": "Equal weight", "Momentum": "Momentum", "MultiFactor": "Multi-factor"}
SOURCE = "Source: supplied MSCI / French workbook. Jan 1995 - Jul 2023 (343 months)."
UNIVERSE = "MSCI USA large/mid cap, gross USD; US academic factors where shown."


def check_months(frame, expected=MONTHS):
    """Reject gaps, duplicates, non-finite values, and unexpectedly reordered data."""
    if not frame.index.equals(expected):
        raise ValueError(f"Monthly index mismatch; missing={list(expected.difference(frame.index))}; "
                         f"duplicates={list(frame.index[frame.index.duplicated()])}")
    if not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError("Missing or non-finite observations; no filling is permitted.")


def save(frame, name):
    # Override the shared helper's four-place exhibit default, preserving results.
    return utils.save_table(frame, name, float_format="%.17g")


def read_saved(name, **kwargs):
    return pd.read_csv(config.TAB_DIR / f"{name}.csv", float_precision="round_trip", **kwargs)


def load_inputs():
    raw_ff = pd.read_excel(config.FILE_FF_MSCI, sheet_name=config.SHEET_FF3, header=None)
    if raw_ff.iloc[3, 1:].tolist() != ["Mkt-RF", "SMB", "HML", "RF"]:
        raise ValueError("Unexpected Fama-French workbook header.")
    date_text = raw_ff.iloc[:, 0].astype(str).str.strip()
    ff = raw_ff.loc[date_text.str.fullmatch(r"\d{6}(\.0)?")].copy()
    ff.columns = ["Date", "Mkt-RF", "SMB", "HML", "RF"]
    ff["Date"] = ff["Date"].astype(float).astype(int).astype(str)
    ff = ff.set_index("Date").apply(pd.to_numeric, errors="raise")
    if ff.isin([-99.99, -999]).any().any():
        raise ValueError("Fama-French missing-value sentinel found.")
    ff = utils.to_monthly_index(utils.pct_to_decimal(ff)).loc["1995-01":"2023-07"]
    check_months(ff)

    raw = pd.read_excel(config.FILE_FF_MSCI, sheet_name=config.SHEET_MSCI, header=None)
    if str(raw.iloc[2, 1]).strip() != "Gross" or str(raw.iloc[3, 1]).strip() != "USD":
        raise ValueError("Expected MSCI gross USD total-return levels.")
    expected_headers = ["Date", "USA Standard (Large+Mid Cap)",
                        "USA VALUE Standard (Large+Mid Cap)",
                        "USA MINIMUM VOLATILITY (USD) Standard (Large+Mid Cap)",
                        "USA EQUAL WEIGHTED Standard (Large+Mid Cap)",
                        "USA MOMENTUM Standard (Large+Mid Cap)"]
    if raw.iloc[6].astype(str).str.strip().tolist() != expected_headers:
        raise ValueError("Unexpected MSCI header; inspect original workbook.")
    levels = raw.iloc[7:].copy()
    levels.columns = ["Date", "Market", *COMPONENTS]
    # The worksheet ends with MSCI copyright text. Exclude footer rows, then
    # require every date in the analysis window; a malformed data row creates
    # a gap and fails check_months below rather than being silently filled.
    parsed_dates = pd.to_datetime(levels["Date"], format="%b %d, %Y", errors="coerce")
    levels = levels.loc[parsed_dates.notna()].copy()
    levels["Date"] = parsed_dates.loc[parsed_dates.notna()]
    levels = utils.to_monthly_index(levels.set_index("Date"))
    levels = levels.apply(lambda x: pd.to_numeric(x.astype(str).str.replace(",", ""), errors="raise"))
    levels = levels.loc["1994-12":"2023-07"]
    check_months(levels, LEVEL_MONTHS)
    if (levels <= 0).any().any():
        raise ValueError("Non-positive MSCI index level.")
    # Same shared conversion and monthly-rebalanced equal weighting as Part 1C.
    returns = utils.levels_to_returns(levels)
    returns["MultiFactor"] = returns[COMPONENTS].mean(axis=1)
    check_months(returns)
    direct = levels.to_numpy()[1:] / levels.to_numpy()[:-1] - 1
    np.testing.assert_allclose(returns[["Market", *COMPONENTS]], direct, rtol=0, atol=1e-15)

    rounded = read_saved("tab_1C_monthly_returns", index_col="month")
    rounded.index = pd.PeriodIndex(rounded.index, freq="M", name="month")
    check_months(rounded)
    if rounded.columns.tolist() != returns.columns.tolist():
        raise ValueError("Part 1C CSV columns differ from expected index definitions.")
    diff = (returns - rounded).abs()
    # One-half of 0.0001 decimal return = 0.5 basis point of monthly return.
    if diff.to_numpy().max() > 0.000050000001:
        raise ValueError("Part 1C mismatch exceeds four-decimal CSV rounding.")
    audit = pd.DataFrame({"max_abs_csv_rounding_difference_decimal": diff.max(),
                          "max_abs_csv_rounding_difference_basis_points": diff.max() * 10000})
    rounded_identity_error = float((rounded["MultiFactor"] - rounded[COMPONENTS].mean(axis=1)).abs().max())
    return returns, ff, audit, rounded_identity_error


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fit_model(returns, ff):
    import statsmodels.api as sm
    check_months(returns)
    check_months(ff)
    x = sm.add_constant(ff[FACTORS], has_constant="add")
    # The dependent variable is TOTAL return. RF is explicitly estimated,
    # not subtracted or constrained to one. One index => time-series OLS.
    return sm.OLS(returns["Value"], x, missing="raise").fit(cov_type="nonrobust")
