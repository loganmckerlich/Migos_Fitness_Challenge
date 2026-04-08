"""
viz/activity_breakdown.py — Activity type pie chart breakdown.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import config
from viz.shared import unit_label


def render(df: pd.DataFrame, use_miles: bool = True, use_hours: bool = False) -> None:
    """Pie chart showing total distance (or hours) broken down by activity type."""
    st.subheader("🥧 Activity Type Breakdown")

    if "activity_type" not in df.columns or df.empty:
        st.info("No activity type data available.")
        return

    if use_hours and "moving_time_hours" in df.columns:
        display_unit = "hrs"
        totals = (
            df.groupby("activity_type")["moving_time_hours"]
            .sum()
            .reset_index()
            .rename(columns={"moving_time_hours": display_unit})
        )
        chart_title = f"Total time by activity type ({display_unit})"
    else:
        display_unit = unit_label(use_miles)
        factor = config.KM_TO_MI if use_miles else 1.0
        totals = (
            df.groupby("activity_type")["km"]
            .sum()
            .mul(factor)
            .reset_index()
            .rename(columns={"km": display_unit})
        )
        chart_title = f"Total distance by activity type ({display_unit})"

    if totals.empty:
        st.info("No data to display.")
        return

    color_map = {"Run": "#EF553B", "Walk": "#00CC96", "Ride": "#636EFA"}
    colors = [color_map.get(t, "#AB63FA") for t in totals["activity_type"]]

    fig = go.Figure(
        go.Pie(
            labels=totals["activity_type"],
            values=totals[display_unit].round(1),
            textinfo="label+percent+value",
            texttemplate="%{label}<br>%{percent}<br>%{value:.1f} " + display_unit,
            marker_colors=colors,
            hole=0.35,
        )
    )
    fig.update_layout(
        title=dict(text=chart_title, x=0.5),
        showlegend=True,
        margin=dict(t=60, b=20, l=20, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)

