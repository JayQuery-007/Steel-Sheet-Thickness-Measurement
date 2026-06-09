"""Render a simple one-row heatmap indicating pass/warn/fail.

The visualization maps each X position to a categorical status:
0 = nominal (within tolerance), 1 = near-limit (within 2× tolerance),
2 = out-of-spec. This function is intentionally lightweight for quick
visual feedback in the Streamlit UI.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np


def show_heatmap(result_df, target_thickness, tolerance):
    """Display a compact thickness heatmap in the Streamlit app.

    Parameters
    - result_df: DataFrame with `X` and `Thickness` columns.
    - target_thickness: nominal thickness value (float)
    - tolerance: allowable deviation (float)
    """

    st.subheader("Thickness Heatmap")

    thickness = result_df["Thickness"].values
    x = result_df["X"].values

    status_values = []
    for t in thickness:
        # 0: within tolerance, 1: within 2× tolerance, 2: out-of-spec
        if target_thickness - tolerance <= t <= target_thickness + tolerance:
            status_values.append(0)
        elif target_thickness - 2 * tolerance <= t <= target_thickness + 2 * tolerance:
            status_values.append(1)
        else:
            status_values.append(2)

    heatmap_data = np.array([status_values])

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data,
            x=x,
            colorscale=[[0.0, "green"], [0.5, "yellow"], [1.0, "red"]],
            colorbar=dict(title="Thickness"),
        )
    )

    fig.update_layout(height=300, xaxis_title="Width Position (mm)", yaxis_visible=False)

    st.plotly_chart(fig, use_container_width=True)

    st.info(
        f"""
Target Thickness : {target_thickness:.3f} mm

Tolerance : ±{tolerance:.3f} mm

Green regions indicate nominal thickness.

Red regions indicate deviation from target.
"""
    )