"""
viz/activity_breakdown.py — Activity type pie chart breakdown.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import config
from viz.shared import unit_label


def render(df: pd.DataFrame, use_miles: bool = True) -> None:
    """Pie chart showing total distance broken down by activity type."""
    st.subheader("🥧 Activity Type Breakdown")

    if "activity_type" not in df.columns or df.empty:
        st.info("No activity type data available.")
        return

    unit   = unit_label(use_miles)
    factor = config.KM_TO_MI if use_miles else 1.0

    totals = (
        df.groupby("activity_type")["km"]
        .sum()
        .mul(factor)
        .reset_index()
        .rename(columns={"km": unit})
    )

    if totals.empty:
        st.info("No data to display.")
        return

    color_map = {"Run": "#EF553B", "Walk": "#00CC96", "Ride": "#636EFA"}
    colors = [color_map.get(t, "#AB63FA") for t in totals["activity_type"]]

    fig = go.Figure(
        go.Pie(
            labels=totals["activity_type"],
            values=totals[unit].round(1),
            textinfo="label+percent+value",
            texttemplate="%{label}<br>%{percent}<br>%{value:.1f} " + unit,
            marker_colors=colors,
            hole=0.35,
        )
    )
    fig.update_layout(
        title=dict(text=f"Total distance by activity type ({unit})", x=0.5),
        showlegend=True,
        margin=dict(t=60, b=20, l=20, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)
