"""Utilities for cleaning raw sensor profile data.

This module provides a single public function `clean_profile` which
removes invalid measurement markers, NaNs and (optionally) statistical
outliers using the IQR rule.
"""

import pandas as pd


INVALID_VALUES = [-9999, 0]


def clean_profile(
    df,
    mode="Basic"
):
    """Clean a profile DataFrame.

    Parameters
    - df: pandas.DataFrame with at least a "Z" column.
    - mode: "Basic" to remove NaN/invalid markers; "Statistical"
      to also remove IQR outliers.

    Returns
    - (cleaned_df, quality_report): tuple where `quality_report` is a
      dict summarizing how many points were removed.
    """

    original_points = len(df)

    # Remove rows with missing values
    df = df.dropna()

    # Remove explicit invalid marker values (e.g. sensor error codes)
    df = df[~df["Z"].isin(INVALID_VALUES)]

    invalid_removed = original_points - len(df)

    outliers_removed = 0

    # Optionally remove statistical outliers using the IQR rule
    if mode == "Statistical":
        before_outlier = len(df)

        q1 = df["Z"].quantile(0.25)
        q3 = df["Z"].quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        df = df[(df["Z"] >= lower) & (df["Z"] <= upper)]

        outliers_removed = before_outlier - len(df)

    final_points = len(df)

    quality_report = {
        "original_points": original_points,
        "invalid_removed": invalid_removed,
        "outliers_removed": outliers_removed,
        "final_points": final_points,
    }

    return df, quality_report