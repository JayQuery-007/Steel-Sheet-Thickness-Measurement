"""PDF report generation for inspection results using ReportLab.

The `generate_pdf_report` function builds a simple multi-page PDF
containing an executive summary, statistics table and defect details.
"""

from io import BytesIO
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
)

from reportlab.lib import colors

from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf_report(
    result_df,
    stats,
    defects_df,
    target,
    tolerance,
):
    """Build a PDF report and return it as a BytesIO buffer.

    The returned buffer is positioned at the start and can be passed to
    a web framework or saved to disk.
    """

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    # Header with generation timestamp and overall status
    report_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    overall_status = "PASS" if len(defects_df) == 0 else "FAIL"

    story.append(Paragraph("Steel Sheet Thickness Inspection Report", styles["Title"]))
    story.append(Paragraph(f"Generated: {report_time}", styles["BodyText"]))
    story.append(Spacer(1, 20))

    # Executive summary
    story.append(Paragraph("Executive Summary", styles["Heading1"]))
    story.append(
        Paragraph(
            f"""
            A total of {len(result_df)} measurement
            locations were analyzed using top and
            bottom sensor profiles.

            The target thickness was
            {target:.3f} mm with an allowable
            tolerance of ±{tolerance:.3f} mm.

            {len(defects_df)} locations were found
            outside the specified tolerance band.

            Overall Inspection Result:
            <b>{overall_status}</b>
            """,
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 15))

    # Summary table
    story.append(Paragraph("Inspection Statistics", styles["Heading1"]))
    summary_table = Table([
        ["Metric", "Value"],
        ["Target Thickness", f"{target:.3f} mm"],
        ["Tolerance", f"±{tolerance:.3f} mm"],
        ["Minimum Thickness", f"{stats['minimum']:.3f} mm"],
        ["Maximum Thickness", f"{stats['maximum']:.3f} mm"],
        ["Mean Thickness", f"{stats['mean']:.3f} mm"],
        ["Std Deviation", f"{stats['std']:.3f}"],
        ["Defect Count", str(len(defects_df))],
        ["Overall Result", overall_status],
    ])
    summary_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ])
    )
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # Probable cause analysis (if available)
    if "Probable_Cause" in defects_df.columns:
        top_count = len(defects_df[defects_df["Probable_Cause"] == "Top Surface"])
        bottom_count = len(defects_df[defects_df["Probable_Cause"] == "Bottom Surface"])
        both_count = len(defects_df[defects_df["Probable_Cause"] == "Both"])

        story.append(Paragraph("Probable Cause Analysis", styles["Heading1"]))
        cause_table = Table([
            ["Cause", "Count"],
            ["Top Surface", top_count],
            ["Bottom Surface", bottom_count],
            ["Both Surfaces", both_count],
        ])
        cause_table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ])
        )
        story.append(cause_table)

    story.append(PageBreak())

    # Defect details
    story.append(Paragraph("Defect Details", styles["Heading1"]))
    if len(defects_df) == 0:
        story.append(Paragraph("No defects detected.", styles["BodyText"]))
    else:
        defect_rows = [["X Position", "Thickness", "Cause"]]
        for _, row in defects_df.head(25).iterrows():
            cause = row["Probable_Cause"] if "Probable_Cause" in defects_df.columns else "N/A"
            defect_rows.append([f"{row['X']:.3f}", f"{row['Thickness']:.3f}", str(cause)])

        defect_table = Table(defect_rows)
        defect_table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ])
        )
        story.append(defect_table)

    doc.build(story)
    buffer.seek(0)
    return buffer