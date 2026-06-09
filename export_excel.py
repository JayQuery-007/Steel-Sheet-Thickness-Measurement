"""Helpers to generate Excel reports for inspection results.

This module uses pandas + openpyxl to build an in-memory Excel file
containing summary, defect and full-results worksheets and returns a
BytesIO buffer ready for download.
"""

import pandas as pd
from io import BytesIO


def generate_excel_report(
    result_df,
    defects_df,
    stats,
    target,
    tolerance,
):
    """Create an Excel workbook (in-memory) with inspection data.

    Returns a `BytesIO` object positioned at start suitable for
    streaming to a web client (e.g. Streamlit `download_button`).
    """

    output = BytesIO()

    # Use pandas ExcelWriter with openpyxl engine to write multiple sheets
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary_df = pd.DataFrame(
            {
                "Metric": [
                    "Minimum Thickness",
                    "Maximum Thickness",
                    "Mean Thickness",
                    "Std Deviation",
                    "Target Thickness",
                    "Tolerance",
                    "Defect Count",
                ],
                "Value": [
                    stats["minimum"],
                    stats["maximum"],
                    stats["mean"],
                    stats["std"],
                    target,
                    tolerance,
                    len(defects_df),
                ],
            }
        )

        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        defects_df.to_excel(writer, sheet_name="Defects", index=False)
        result_df.to_excel(writer, sheet_name="Full Results", index=False)

    output.seek(0)
    return output