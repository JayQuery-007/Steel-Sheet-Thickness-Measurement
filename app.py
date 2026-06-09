"""Streamlit application for steel sheet thickness inspection.

This module implements the UI: file upload, quality settings, analysis
workflow and visualization. The Streamlit app assembles utilities from
other modules in this package to compute thickness and export reports.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from data_cleaner import clean_profile
from heatmap_view import show_heatmap
from export_excel import (
    generate_excel_report
)

from export_pdf import (
    generate_pdf_report
)
from thickness_engine import (
    prepare_dataframe,
    calculate_thickness,
    statistics
)

defects_df = pd.DataFrame()

st.set_page_config(
    page_title="Steel Thickness System",
    page_icon="📏",
    layout="wide"
)

st.title(
    "Steel Sheet Thickness Measurement System"
)

st.markdown(
    "Industrial Thickness Analysis Dashboard"
)

st.sidebar.header("Profile Upload")

st.sidebar.header("Quality Settings")

cleaning_mode = st.sidebar.selectbox(
    "Data Cleaning Mode",
    [
        "Basic",
        "Statistical"
    ]
)

TARGET_THICKNESS = st.sidebar.number_input(
    "Target Thickness (mm)",
    value=3.0,
    step=0.01
)

TOLERANCE = st.sidebar.number_input(
    "Tolerance (± mm)",
    value=0.10,
    step=0.01
)

top_file = st.sidebar.file_uploader(
    "Upload Top Profile",
    type=["csv"]
)

bottom_file = st.sidebar.file_uploader(
    "Upload Bottom Profile",
    type=["csv"]
)

if top_file and bottom_file:

    top_df = pd.read_csv(top_file)
    bottom_df = pd.read_csv(bottom_file)

    top_df = prepare_dataframe(top_df)
    bottom_df = prepare_dataframe(bottom_df)

    top_df, top_quality = clean_profile(top_df,cleaning_mode)

    bottom_df, bottom_quality = clean_profile(bottom_df,cleaning_mode)

    (
        x,
        top_interp,
        bottom_interp,
        thickness,
        top_source,
        bottom_source
    ) = calculate_thickness(
        top_df,
        bottom_df
    )

    stats = statistics(thickness)

    lower_limit = TARGET_THICKNESS - TOLERANCE
    upper_limit = TARGET_THICKNESS + TOLERANCE

    result_df = pd.DataFrame({
        "X": x,
        "Top_Z": top_interp,
        "Bottom_Z": bottom_interp,
        "Thickness": thickness,
        "Top_Source": top_source,
        "Bottom_Source": bottom_source
    })

    result_df["Status"] = np.where(
        (
            (result_df["Thickness"] >= lower_limit)
            &
            (result_df["Thickness"] <= upper_limit)
        ),
        "PASS",
        "FAIL"
    )

    result_df["Interpolation_Type"] = (
        result_df["Top_Source"]
        + " / "
        + result_df["Bottom_Source"]
    )
    

    # PROBABLE CAUSE ANALYSIS


    top_reference = result_df[
        "Top_Z"
    ].mean()

    bottom_reference = result_df[
        "Bottom_Z"
    ].mean()

    result_df["Top_Deviation"] = (
        result_df["Top_Z"]
        - top_reference
    )

    result_df["Bottom_Deviation"] = (
        result_df["Bottom_Z"]
        - bottom_reference
    )

    def probable_cause(row):

        top_dev = abs(
            row["Top_Deviation"]
        )

        bottom_dev = abs(
            row["Bottom_Deviation"]
        )

        threshold = 0.01

        if abs(
            top_dev - bottom_dev
        ) < threshold:

            return "Both"

        elif top_dev > bottom_dev:

            return "Top Surface"

        else:

            return "Bottom Surface"


    result_df["Probable_Cause"] = (
        result_df.apply(
            probable_cause,
            axis=1
        )
    )

    # DEFECT ANALYSIS


    defects_df = result_df[
    result_df["Status"] == "FAIL"
    ]

    top_issue_count = len(
    defects_df[
        defects_df["Probable_Cause"]
        == "Top Surface"
    ]
    )

    bottom_issue_count = len(
    defects_df[
        defects_df["Probable_Cause"]
        == "Bottom Surface"
    ]
    )

    both_issue_count = len(
    defects_df[
        defects_df["Probable_Cause"]
        == "Both"
    ]
    )

    overall_status = (
    "PASS"
    if len(defects_df) == 0
    else "FAIL"
    )

    # EXECUTIVE DASHBOARD


    st.success(
        "Thickness computation completed successfully"
    )

    st.subheader(
    "Data Quality"
)

    q1, q2 = st.columns(2)

    with q1:

        st.info(
            f"""
            Top Profile

            Original Points:
            {top_quality['original_points']}

            Invalid Removed:
            {top_quality['invalid_removed']}

            Outliers Removed:
            {top_quality['outliers_removed']}

            Final Points:
            {top_quality['final_points']}
            """
        )

    with q2:

        st.info(
            f"""
            Bottom Profile

            Original Points:
            {bottom_quality['original_points']}

            Invalid Removed:
            {bottom_quality['invalid_removed']}

            Outliers Removed:
            {bottom_quality['outliers_removed']}

            Final Points:
            {bottom_quality['final_points']}
            """
        )

    st.subheader(
        "Inspection Summary"
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Status",
        overall_status
    )

    c2.metric(
        "Mean Thickness",
        f"{stats['mean']:.3f} mm"
    )

    c3.metric(
        "Minimum",
        f"{stats['minimum']:.3f} mm"
    )

    c4.metric(
        "Maximum",
        f"{stats['maximum']:.3f} mm"
    )

    c5.metric(
        "Defects",
        len(defects_df)
    )

    c6, c7, c8 = st.columns(3)

    c6.metric(
        "Top Surface Issues",
        top_issue_count
    )

    c7.metric(
        "Bottom Surface Issues",
        bottom_issue_count
    )

    c8.metric(
        "Both Surfaces",
        both_issue_count
    )


# CAUSE DISTRIBUTION


    if not defects_df.empty:

        cause_df = pd.DataFrame({
            "Cause": [
                "Top Surface",
                "Bottom Surface",
                "Both"
            ],
            "Count": [
                top_issue_count,
                bottom_issue_count,
                both_issue_count
            ]
        })

        cause_fig = go.Figure(
            data=[
                go.Pie(
                    labels=cause_df["Cause"],
                    values=cause_df["Count"],
                    hole=0.4
                )
            ]
        )

        cause_fig.update_layout(
            title="Probable Cause Distribution"
        )

        st.plotly_chart(
            cause_fig,
            use_container_width=True,
            key="executive_summary_pie_chart"
        )

    else:

        st.info(
            """
            All measurements are within tolerance.

            No defect classification or
            root-cause analysis was required.
            """
        )
  
        # INSPECTION SUMMARY

    top_issue_count = len(
            defects_df[
                defects_df["Probable_Cause"]
                == "Top Surface"
            ]
        )

    bottom_issue_count = len(
            defects_df[
                defects_df["Probable_Cause"]
                == "Bottom Surface"
            ]
        )

    both_issue_count = len(
            defects_df[
                defects_df["Probable_Cause"]
                == "Both"
            ]
        )

    overall_status = (
            "PASS"
            if len(defects_df) == 0
            else "FAIL"
        )
    excel_file = generate_excel_report(
        result_df,
        defects_df,
        stats,
        TARGET_THICKNESS,
        TOLERANCE
    )

    pdf_file = generate_pdf_report(
    result_df,
    stats,
    defects_df,
    TARGET_THICKNESS,
    TOLERANCE
    )

    c1, c2 = st.columns(2)

    with c1:

        st.download_button(
            "Download Excel Report",
            data=excel_file,
            file_name="inspection_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with c2:

        st.download_button(
            "Download PDF Report",
            data=pdf_file,
            file_name="inspection_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

  
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Minimum Thickness",
        f"{stats['minimum']:.3f} mm"
    )

    col2.metric(
        "Maximum Thickness",
        f"{stats['maximum']:.3f} mm"
    )

    col3.metric(
        "Mean Thickness",
        f"{stats['mean']:.3f} mm"
    )

    col4.metric(
        "Std Deviation",
        f"{stats['std']:.3f}"
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Raw Profiles",
    "Thickness Analysis",
    "Interpolation Details",
    "Quality Report",
    "Thickness Heatmap"
])


    # TAB 1 : RAW PROFILES

    with tab1:

        st.subheader("Top Profile")

        st.dataframe(
            top_df,
            use_container_width=True
        )

        st.subheader("Bottom Profile")

        st.dataframe(
            bottom_df,
            use_container_width=True
        )

    # TAB 2 : THICKNESS ANALYSIS

    with tab2:

        st.subheader(
            "Steel Sheet Geometry"
        )

        profile_fig = go.Figure()


        # TOP SURFACE


        profile_fig.add_trace(
            go.Scatter(
                x=x,
                y=top_interp,
                mode="lines",
                name="Top Sensor Profile",
                line=dict(
                    width=4
                )
            )
        )

   
        # BOTTOM SURFACE + FILL


        profile_fig.add_trace(
            go.Scatter(
                x=x,
                y=bottom_interp,
                mode="lines",
                fill="tonexty",
                name="Material Region",
                line=dict(
                    width=4
                )
            )
        )

        # DEFECT LOCATIONS


        bad_points = result_df[
            result_df["Status"] == "FAIL"
        ]
        
        top_defects = bad_points[
            bad_points["Probable_Cause"]
            == "Top Surface"
        ]

        bottom_defects = bad_points[
            bad_points["Probable_Cause"]
            == "Bottom Surface"
        ]

        both_defects = bad_points[
            bad_points["Probable_Cause"]
            == "Both"
        ]

        profile_fig.add_trace(
        go.Scatter(
            x=top_defects["X"],
            y=(
                top_defects["Top_Z"]
                +
                top_defects["Bottom_Z"]
            ) / 2,
            mode="markers",
            name="Top Surface Issue",
            marker=dict(
                color="orange",
                size=12,
                symbol="x"
            )
        )
    )
        
        profile_fig.add_trace(
        go.Scatter(
            x=bottom_defects["X"],
            y=(
                bottom_defects["Top_Z"]
                +
                bottom_defects["Bottom_Z"]
            ) / 2,
            mode="markers",
            name="Bottom Surface Issue",
            marker=dict(
                color="red",
                size=12,
                symbol="x"
            )
        )
    )
        
        profile_fig.add_trace(
        go.Scatter(
            x=both_defects["X"],
            y=(
                both_defects["Top_Z"]
                +
                both_defects["Bottom_Z"]
            ) / 2,
            mode="markers",
            name="Both Surfaces",
            marker=dict(
                color="purple",
                size=12,
                symbol="x"
            )
        )
    )

        profile_fig.update_layout(
            title="Steel Sheet Geometry",
            xaxis_title="Width Position (mm)",
            yaxis_title="Height (mm)",
            height=650,
            legend=dict(
                orientation="h"
            )
        )

        st.plotly_chart(
            profile_fig,
            use_container_width=True
        )


        # THICKNESS PROFILE


        st.subheader(
            "Thickness Distribution Across Sheet Width"
        )

        thickness_fig = go.Figure()

        thickness_fig.add_trace(
            go.Scatter(
                x=x,
                y=thickness,
                mode="lines",
                name="Thickness",

                customdata=np.column_stack([
                    top_interp,
                    bottom_interp
                ]),

                hovertemplate=
                (
                    "X: %{x:.3f}<br>"
                    "Top Z: %{customdata[0]:.3f}<br>"
                    "Bottom Z: %{customdata[1]:.3f}<br>"
                    "Thickness: %{y:.3f}<br>"
                    "<extra></extra>"
                )
            )
        )

        # OUT OF TOLERANCE POINTS
 

        if len(bad_points) > 0:

            thickness_fig.add_trace(
                go.Scatter(
                    x=bad_points["X"],
                    y=bad_points["Thickness"],
                    mode="markers",
                    name="Out Of Tolerance",
                    marker=dict(
                        color="red",
                        size=8
                    )
                )
            )

        # TARGET & TOLERANCE LINES


        thickness_fig.add_hline(
            y=TARGET_THICKNESS,
            line_dash="dash",
            annotation_text="Target"
        )

        thickness_fig.add_hline(
            y=upper_limit,
            line_dash="dot",
            annotation_text="Upper Limit"
        )

        thickness_fig.add_hline(
            y=lower_limit,
            line_dash="dot",
            annotation_text="Lower Limit"
        )

        thickness_fig.update_layout(
            title="Thickness Distribution",
            xaxis_title="Width Position (mm)",
            yaxis_title="Thickness (mm)",
            height=650
        )

        st.plotly_chart(
            thickness_fig,
            use_container_width=True
        )

    # TAB 3 : INTERPOLATION DETAILS


    with tab3:
        

        st.info(
            """
            Thickness is computed using a common X grid
            generated from the union of top and bottom
            sensor positions.

            Both profiles are interpolated onto this
            common grid before thickness calculation.
            """
        )

        st.subheader(
            "Interpolation Calculation Table"
        )

        st.dataframe(
            result_df,
            use_container_width=True
        )

        selected_x = st.selectbox(
            "Inspect X Position",
            result_df["X"],
            key="interpolation_inspector"
        )

        row = result_df[
            result_df["X"] == selected_x
        ].iloc[0]

        st.subheader(
            "Point Inspection"
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Top Surface Z",
                f"{row['Top_Z']:.4f}"
            )
            st.caption(
                f"Source: {row['Top_Source']}"
            )

        with c2:
            st.metric(
                "Bottom Surface Z",
                f"{row['Bottom_Z']:.4f}"
            )
            st.caption(
                f"Source: {row['Bottom_Source']}"
            )

        with c3:
            st.metric(
                "Thickness",
                f"{row['Thickness']:.4f}"
            )

        st.info(
            f"""
        Top Source: {row['Top_Source']}

        Bottom Source: {row['Bottom_Source']}

        Interpolation Type:
        {row['Interpolation_Type']}
        """
        )

        st.subheader(
            "Interpolation Verification"
        )
        
        interp_fig = go.Figure()

        interp_fig.add_trace(
        go.Scatter(
            x=top_df["X"],
            y=top_df["Z"],
            mode="markers",
            name="Top Actual Points"
        )
    )
        
        interp_fig.add_trace(
        go.Scatter(
            x=x,
            y=top_interp,
            mode="lines",
            name="Top Interpolated"
        )
    )
        
        interp_fig.add_trace(
        go.Scatter(
            x=bottom_df["X"],
            y=bottom_df["Z"],
            mode="markers",
            name="Bottom Actual Points"
        )
    )

        interp_fig.add_trace(
        go.Scatter(
            x=x,
            y=bottom_interp,
            mode="lines",
            name="Bottom Interpolated"
        )
    )
        
        interp_fig.update_layout(
        title="Actual vs Interpolated Profiles",
        xaxis_title="Width Position (mm)",
        yaxis_title="Height (mm)",
        height=650
    )
        st.plotly_chart(
        interp_fig,
        use_container_width=True
    )
        
        actual_top_points = len(top_df)

        actual_bottom_points = len(bottom_df)

        common_grid_points = len(x)

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Top Points",
            actual_top_points
        )

        c2.metric(
            "Bottom Points",
            actual_bottom_points
        )

        c3.metric(
            "Interpolated Grid Points",
            common_grid_points
        )

        
        
        st.info(
        """
        The top and bottom sensors do not always measure
        at identical X positions.

        A common X-grid is generated using the union of
        all available measurement positions.

        Missing values are estimated using linear
        interpolation before thickness calculation.
        """
    )

    # TAB 4 : QUALITY REPORT


    with tab4:

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Target Thickness",
                f"{TARGET_THICKNESS:.3f} mm"
            )

        with c2:
            st.metric(
                "Tolerance",
                f"±{TOLERANCE:.3f} mm"
            )

        fail_count = len(
            result_df[
                result_df["Status"] == "FAIL"
            ]
        )

        with c3:
            st.metric(
                "Out Of Tolerance Points",
                fail_count
            )

        defects = result_df[
            result_df["Status"] == "FAIL"
        ]

        if len(defects) == 0:

            st.success(
                "PASS : All points within tolerance"
            )

        else:

            st.error(
                f"FAIL : {len(defects)} points outside tolerance"
            )

            st.subheader(
                "Out Of Tolerance Locations"
            )

            st.dataframe(
               defects[
                [
                    "X",
                    "Thickness",
                    "Top_Deviation",
                    "Bottom_Deviation",
                    "Probable_Cause",
                    "Interpolation_Type"
                ]
            ],
            use_container_width=True
            )

    with tab5:

                show_heatmap(
                    result_df,
                    TARGET_THICKNESS,
                    TOLERANCE
                )