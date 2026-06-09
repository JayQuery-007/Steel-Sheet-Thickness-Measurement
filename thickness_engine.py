"""Core thickness calculation utilities.

This module exposes three functions used by the Streamlit app:
- `prepare_dataframe` normalises incoming CSV column names.
- `calculate_thickness` interpolates top/bottom profiles onto a common X
  grid and computes thickness = bottom - top.
- `statistics` computes simple summary statistics on the thickness array.
"""

import pandas as pd
import numpy as np
from scipy.interpolate import interp1d


def prepare_dataframe(df):
    """Normalize column names for upstream processing.

    The function accepts CSVs with either (X,Z) or (X,Y,Z) layouts and
    ensures the returned DataFrame contains at least `X` and `Z`.
    """

    if len(df.columns) == 3:
        df.columns = ["X", "Y", "Z"]
    elif len(df.columns) == 2:
        df.columns = ["X", "Z"]

    return df


def calculate_thickness(top_df, bottom_df):
    """Interpolate top/bottom profiles to a common grid and compute thickness.

    Returns a tuple: (common_x, top_interp, bottom_interp, thickness, top_source, bottom_source)
    where `*_source` indicates whether the value came from an actual measurement
    or was interpolated onto the common grid.
    """

    top_x = top_df["X"].values
    top_z = top_df["Z"].values

    bottom_x = bottom_df["X"].values
    bottom_z = bottom_df["Z"].values

    # union of measurement positions from both sensors
    common_x = np.sort(np.unique(np.concatenate([top_x, bottom_x])))

    top_interp_func = interp1d(top_x, top_z, kind="linear", bounds_error=False, fill_value="extrapolate")
    bottom_interp_func = interp1d(bottom_x, bottom_z, kind="linear", bounds_error=False, fill_value="extrapolate")

    top_interp = top_interp_func(common_x)
    bottom_interp = bottom_interp_func(common_x)

    thickness = bottom_interp - top_interp

    top_actual_set = set(top_x)
    bottom_actual_set = set(bottom_x)

    top_source = ["Actual" if x in top_actual_set else "Interpolated" for x in common_x]
    bottom_source = ["Actual" if x in bottom_actual_set else "Interpolated" for x in common_x]

    return common_x, top_interp, bottom_interp, thickness, top_source, bottom_source


def statistics(thickness):
    """Compute basic statistics for the thickness array.

    Returns a dictionary with `minimum`, `maximum`, `mean` and `std`.
    """

    return {
        "minimum": float(np.min(thickness)),
        "maximum": float(np.max(thickness)),
        "mean": float(np.mean(thickness)),
        "std": float(np.std(thickness)),
    }