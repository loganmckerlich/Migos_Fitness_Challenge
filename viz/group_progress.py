"""
viz/group_progress.py — Group progress vs trend (stacked area + trend line).

Each athlete's contribution is stacked on top of the others so the top line
represents the total group distance.  A dashed trend line shows where the
group should be if on pace.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import config
from viz.shared import (
    build_cumulative,
    compute_avg_pace_hr_per_km,
    pace_delta_label,
    pace_emoji,
    to_display,
    unit_label,
)


# Colour palette — one per athlete (same order as athlete_mile_progress)
# Each entry is (solid_hex, fill_rgba) for the stacked area chart.
_ATHLETE_COLORS = [
    ("#636EFA", "rgba(99,110,250,0.6)"),
    ("#EF553B", "rgba(239,85,59,0.6)"),
    ("#00CC96", "rgba(0,204,150,0.6)"),
    ("#AB63FA", "rgba(171,99,250,0.6)"),
    ("#FFA15A", "rgba(255,161,90,0.6)"),
    ("#19D3F3", "rgba(25,211,243,0.6)"),
    ("#FF6692", "rgba(255,102,146,0.6)"),
    ("#B6E880", "rgba(182,232,128,0.6)"),
    ("#FF97FF", "rgba(255,151,255,0.6)"),
    ("#FECB52", "rgba(254,203,82,0.6)"),
]


def render(
    df: pd.DataFrame,
    start: date,
    end: date,
    goal_km: float,
    athletes: list[dict],
    use_miles: bool = True,
    use_hours: bool = False,
) -> None:
    """Render the Group Progress vs Trend section."""
    st.subheader("🏆 Group Progress vs Trend")

    # ── Build cumulative series in the chosen display unit ────────────────────
    if use_hours and "moving_time_hours" in df.columns:
        avg_pace      = compute_avg_pace_hr_per_km(df)
        cumulative    = build_cumulative(df, start, end, "moving_time_hours")
        goal_display  = goal_km * avg_pace
        display_unit  = "hrs"
    else:
        factor        = config.KM_TO_MI if use_miles else 1.0
        cumulative    = build_cumulative(df, start, end, "km") * factor
        goal_display  = to_display(goal_km, use_miles)
        display_unit  = unit_label(use_miles)

    if cumulative.empty:
        st.info("No data available.")
        return

    # ── Summary metric ────────────────────────────────────────────────────────
    group_series  = cumulative.sum(axis=1)
    current_total = float(group_series.iloc[-1])
    pct           = current_total / goal_display * 100 if goal_display > 0 else 0

    total_days    = (end - start).days
    elapsed_days  = (min(date.today(), end) - start).days
    progress_frac = elapsed_days / total_days if total_days > 0 else 0
    trend_today   = goal_display * progress_frac

    emoji = pace_emoji(current_total, trend_today)
    delta = pace_delta_label(current_total, trend_today, display_unit)

    col1, col2 = st.columns(2)
    col1.metric(
        "Group total",
        f"{current_total:.1f} {display_unit}",
        f"{pct:.1f}% of {goal_display:.0f} {display_unit} goal",
    )
    col2.metric(
        "vs Trend",
        f"{emoji}  {delta}",
    )

    # ── Stacked area chart ────────────────────────────────────────────────────
    fig = go.Figure()

    dates_list = cumulative.index.tolist()

    for idx, name in enumerate(cumulative.columns):
        solid, fill = _ATHLETE_COLORS[idx % len(_ATHLETE_COLORS)]
        values = cumulative[name].tolist()
        fig.add_trace(
            go.Scatter(
                x=dates_list,
                y=values,
                mode="lines",
                name=name,
                stackgroup="one",
                line=dict(width=0.5, color=solid),
                fillcolor=fill,
            )
        )

    # Trend line from 0 → goal (not stacked)
    trend_dates  = pd.date_range(start=start, end=end, freq="D")
    trend_values = np.linspace(0, goal_display, len(trend_dates))
    fig.add_trace(
        go.Scatter(
            x=trend_dates.tolist(),
            y=trend_values.tolist(),
            mode="lines",
            name=f"Trend ({display_unit})",
            line=dict(color="#ff3399", width=2, dash="dash"),
        )
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=f"Cumulative {display_unit}",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40, b=40, l=40, r=20),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    if use_hours:
        st.caption(
            f"Each coloured band shows one athlete's contribution to the group total (hours). "
            f"The dashed trend line is estimated from your historical pace "
            f"({avg_pace * 60:.1f} min/km average) towards {goal_display:.0f} hrs by {end}."
        )
    else:
        st.caption(
            f"Each coloured band shows one athlete's contribution to the group total. "
            f"The dashed line is the on-trend pace towards {goal_display:.0f} {display_unit} by {end}."
        )

