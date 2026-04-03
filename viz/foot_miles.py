"""
viz/foot_miles.py — Foot mile progress tracker (walk + run).

Shows cumulative foot miles per athlete against the 1 mi/day pace target.
The status table includes how many miles ahead or behind pace each athlete
is, plus an emoji that reflects their level of performance.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import config
from viz.shared import pace_delta_label, pace_emoji, to_display, unit_label


# Colour palette — same order as athlete_mile_progress for consistency
_ATHLETE_COLORS = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
    "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52",
]


def render(
    df: pd.DataFrame,
    start: date,
    end: date,
    athletes: list[dict],
    use_miles: bool = True,
) -> None:
    """Render the Foot Mile Progress section."""
    st.subheader("🦶 Foot Mile Progress (Walk + Run)")

    unit   = unit_label(use_miles)
    factor = config.KM_TO_MI if use_miles else 1.0

    # Filter to foot activities only
    foot_df = (
        df[df["activity_type"].isin(["Run", "Walk"])].copy()
        if "activity_type" in df.columns
        else df.copy()
    )

    if foot_df.empty:
        st.info("No walking or running data available for the selected date range.")
        return

    # Build cumulative foot-mile table (in km internally)
    all_dates = pd.date_range(start=start, end=min(end, date.today()), freq="D")
    pivot = foot_df.pivot_table(
        index="date", columns="athlete_name", values="km", aggfunc="sum"
    ).reindex(all_dates, fill_value=0)
    pivot.index.name = "date"
    cumulative_foot = pivot.fillna(0).cumsum()

    # Pace: 1 foot mile per person per day → convert to km for internal comparison
    foot_mi_per_day_km = 1.0 / config.KM_TO_MI
    elapsed_days       = len(all_dates)
    target_km          = foot_mi_per_day_km * elapsed_days

    # ── Status table ──────────────────────────────────────────────────────────
    latest_foot = cumulative_foot.iloc[-1]
    rows = []
    for name in latest_foot.index:
        actual_km   = float(latest_foot[name])
        actual_disp = actual_km * factor
        target_disp = target_km * factor
        emoji  = pace_emoji(actual_disp, target_disp)
        delta  = pace_delta_label(actual_disp, target_disp, unit)
        rows.append(
            {
                "Athlete":                name,
                f"Foot {unit}":           round(actual_disp, 1),
                f"Pace target ({unit})":  round(target_disp, 1),
                "Pace":                   f"{emoji}  {delta}",
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Line chart ────────────────────────────────────────────────────────────
    fig = go.Figure()
    dates_list = cumulative_foot.index.tolist()

    for idx, name in enumerate(cumulative_foot.columns):
        color  = _ATHLETE_COLORS[idx % len(_ATHLETE_COLORS)]
        values = (cumulative_foot[name] * factor).tolist()
        fig.add_trace(
            go.Scatter(
                x=dates_list,
                y=values,
                mode="lines",
                name=name,
                line=dict(color=color, width=2),
            )
        )

    # Pace reference line (linear: 1 mi/day per person)
    pace_km_series = pd.Series(
        [foot_mi_per_day_km * (i + 1) for i in range(len(all_dates))],
        index=all_dates,
    )
    pace_disp = pace_km_series * factor
    fig.add_trace(
        go.Scatter(
            x=all_dates.tolist(),
            y=pace_disp.tolist(),
            mode="lines",
            name=f"Pace (1 {unit}/day)",
            line=dict(color="#888888", width=2, dash="dash"),
        )
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=f"Cumulative foot {unit}",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40, b=40, l=40, r=20),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    pace_total_disp = target_km * factor
    st.caption(
        f"Dashed line = 1 {unit}/day pace target "
        f"({pace_total_disp:.1f} {unit} after {elapsed_days} days elapsed)."
    )
