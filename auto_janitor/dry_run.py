"""Dry-run report for Auto-Janitor, with no LLM call and no writes.

``dry_run_report`` inspects a DataFrame and returns the cleaning plan
it *would* follow, plus row counts, without changing the data.
Use it before ``clean_csv`` when you want to review the plan first.
This module is deterministic: it only counts missing values,
duplicates, and simple format issues. It does not call an LLM and
does not write any output file.
"""

from typing import Any

import pandas as pd


def dry_run_report(df: pd.DataFrame) -> dict[str, Any]:
    """Return a dry-run plan for ``df`` without modifying it."""
    missing = df.isnull().sum()
    missing_by_column = {str(k): int(v) for k, v in missing.items() if v > 0}
    duplicate_rows = int(df.duplicated().sum())
    currency_columns = []
    for col in df.columns:
        sample = df[col].dropna().astype(str).head(50)
        if sample.str.contains(r"[$€£]", regex=True).any():
            currency_columns.append(str(col))

    planned_steps: list[str] = []
    if missing_by_column:
        planned_steps.append(
            "Impute or drop missing values in: "
            + ", ".join(missing_by_column.keys())
        )
    if duplicate_rows:
        planned_steps.append(f"Remove {duplicate_rows} duplicate row(s).")
    if currency_columns:
        planned_steps.append(
            "Strip currency symbols and convert to numeric in: "
            + ", ".join(currency_columns)
        )
    planned_steps.append("Trim whitespace and normalise case where applicable.")
    if not planned_steps:
        planned_steps.append("No issues detected; no cleaning steps planned.")

    return {
        "row_count_before": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": [str(c) for c in df.columns],
        "missing_by_column": missing_by_column,
        "duplicate_rows": duplicate_rows,
        "currency_columns": currency_columns,
        "planned_steps": planned_steps,
        "applied": False,
        "note": "Dry run only: no rows were changed and no file was written.",
    }


def format_dry_run_report(report: dict[str, Any]) -> str:
    """Render a dry-run report as human-readable text."""
    lines = [
        f"Dry run: {report['row_count_before']} rows x {report['column_count']} columns",
        f"Missing values: {report['missing_by_column'] or 'none'}",
        f"Duplicate rows: {report['duplicate_rows']}",
        "Planned steps:",
    ]
    lines.extend(f"  - {step}" for step in report["planned_steps"])
    lines.append(report["note"])
    return "\n".join(lines)


def dry_run_csv(csv_path: str) -> dict[str, Any]:
    """Dry-run report for a CSV file, without writing anything."""
    return dry_run_report(pd.read_csv(csv_path))
