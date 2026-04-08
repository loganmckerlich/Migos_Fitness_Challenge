"""
viz/athlete_mile_progress.py — Per-athlete cumulative mile progress chart.

Shows each athlete as an unfilled line (no fill) with a dashed "on-trend"
reference line.  A status table shows how many miles each athlete is
ahead of or behind pace, decorated with an emoji.
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


# A colour palette for up to ~10 athletes
_ATHLETE_COLORS = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
    "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52",
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
    """Render the Athlete Mile Progress section."""
    st.subheader("📈 Athlete Mile Progress")

    total_days    = (end - start).days
    elapsed_days  = (min(date.today(), end) - start).days
    progress_frac = elapsed_days / total_days if total_days > 0 else 0

    n_athletes       = len(athletes)
    per_athlete_goal = goal_km / n_athletes if n_athletes > 0 else goal_km

    # ── Build cumulative series in the chosen display unit ────────────────────
    if use_hours and "moving_time_hours" in df.columns:
        avg_pace              = compute_avg_pace_hr_per_km(df)
        cumulative            = build_cumulative(df, start, end, "moving_time_hours")
        per_athlete_goal_disp = per_athlete_goal * avg_pace
        trend_today_disp      = per_athlete_goal_disp * progress_frac
        display_unit          = "hrs"
    else:
        factor                = config.KM_TO_MI if use_miles else 1.0
        cumulative            = build_cumulative(df, start, end, "km") * factor
        per_athlete_goal_disp = to_display(per_athlete_goal, use_miles)
        trend_today_disp      = to_display(per_athlete_goal * progress_frac, use_miles)
        display_unit          = unit_label(use_miles)

    if cumulative.empty:
        st.info("No data available for the selected date range.")
        return

    # ── Status table ──────────────────────────────────────────────────────────
    latest = cumulative.iloc[-1]
    rows = []
    for name in cumulative.columns:
        actual_disp = float(latest.get(name, 0))
        emoji  = pace_emoji(actual_disp, trend_today_disp)
        delta  = pace_delta_label(actual_disp, trend_today_disp, display_unit)
        rows.append(
            {
                "Athlete":                          name,
                f"Total {display_unit}":            round(actual_disp, 1),
                f"Trend target ({display_unit})":   round(trend_today_disp, 1),
                "Pace":                             f"{emoji}  {delta}",
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Line chart ────────────────────────────────────────────────────────────
    fig = go.Figure()

    dates_list = cumulative.index.tolist()

    for idx, name in enumerate(cumulative.columns):
        color = _ATHLETE_COLORS[idx % len(_ATHLETE_COLORS)]
        values = cumulative[name].tolist()
        fig.add_trace(
            go.Scatter(
                x=dates_list,
                y=values,
                mode="lines",
                name=name,
                line=dict(color=color, width=2),
            )
        )

    # On-trend reference line (linear from 0 → per_athlete_goal)
    trend_dates  = pd.date_range(start=start, end=end, freq="D")
    trend_values = np.linspace(0, per_athlete_goal_disp, len(trend_dates))
    fig.add_trace(
        go.Scatter(
            x=trend_dates.tolist(),
            y=trend_values.tolist(),
            mode="lines",
            name="On Trend",
            line=dict(color="#888888", width=2, dash="dash"),
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
            f"Dashed line shows on-trend pace ({per_athlete_goal_disp:.0f} hrs per athlete "
            f"by {end}, estimated from historical pace). "
            f"{progress_frac * 100:.0f}% of the challenge has elapsed."
        )
    else:
        st.caption(
            f"Dashed line shows on-trend pace ({per_athlete_goal_disp:.0f} {display_unit} per athlete "
            f"by {end}). {progress_frac * 100:.0f}% of the challenge has elapsed."
        )

