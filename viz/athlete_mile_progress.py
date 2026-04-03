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
from viz.shared import build_cumulative, pace_delta_label, pace_emoji, to_display, unit_label


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
) -> None:
    """Render the Athlete Mile Progress section."""
    st.subheader("📈 Athlete Mile Progress")

    cumulative = build_cumulative(df, start, end)

    if cumulative.empty:
        st.info("No data available for the selected date range.")
        return

    total_days   = (end - start).days
    elapsed_days = (min(date.today(), end) - start).days
    progress_frac = elapsed_days / total_days if total_days > 0 else 0

    n_athletes       = len(athletes)
    per_athlete_goal = goal_km / n_athletes if n_athletes > 0 else goal_km
    trend_today_km   = per_athlete_goal * progress_frac

    unit   = unit_label(use_miles)
    factor = config.KM_TO_MI if use_miles else 1.0

    # ── Status table ──────────────────────────────────────────────────────────
    latest = cumulative.iloc[-1]
    rows = []
    for name in cumulative.columns:
        actual_km  = float(latest.get(name, 0))
        actual_disp = actual_km * factor
        trend_disp  = trend_today_km * factor
        emoji  = pace_emoji(actual_disp, trend_disp)
        delta  = pace_delta_label(actual_disp, trend_disp, unit)
        rows.append(
            {
                "Athlete":                name,
                f"Total {unit}":          round(actual_disp, 1),
                f"Trend target ({unit})": round(trend_disp, 1),
                "Pace":                   f"{emoji}  {delta}",
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Line chart ────────────────────────────────────────────────────────────
    fig = go.Figure()

    dates_list = cumulative.index.tolist()

    for idx, name in enumerate(cumulative.columns):
        color = _ATHLETE_COLORS[idx % len(_ATHLETE_COLORS)]
        values = (cumulative[name] * factor).tolist()
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
    trend_values = np.linspace(0, per_athlete_goal * factor, len(trend_dates))
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
        yaxis_title=f"Cumulative {unit}",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40, b=40, l=40, r=20),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    goal_disp = to_display(per_athlete_goal, use_miles)
    st.caption(
        f"Dashed line shows on-trend pace ({goal_disp:.0f} {unit} per athlete "
        f"by {end}). {progress_frac * 100:.0f}% of the challenge has elapsed."
    )
