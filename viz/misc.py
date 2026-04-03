"""
viz/misc.py — Three bonus visualizations for the Misc tab.

1. 🏆 Personal Best Days  — horizontal bar of each athlete's single best day
2. 🧬 Activity DNA        — per-athlete stacked bar: run vs walk vs ride miles
3. 📅 Training Consistency — weekly active-day heatmap per athlete
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import config
from viz.shared import unit_label


# Shared colour constants
_RUN_COLOR  = "#EF553B"
_WALK_COLOR = "#00CC96"
_RIDE_COLOR = "#636EFA"
_COLOR_MAP  = {"Run": _RUN_COLOR, "Walk": _WALK_COLOR, "Ride": _RIDE_COLOR}

_ATHLETE_COLORS = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
    "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52",
]


# ─────────────────────────────────────────────────────────────────────────────
# VIZ 1 — Personal Best Days
# ─────────────────────────────────────────────────────────────────────────────

def _chart_personal_bests(df: pd.DataFrame, use_miles: bool) -> None:
    """Horizontal bar chart: each athlete's best single-day distance."""
    st.subheader("🏆 Personal Best Days")
    st.caption("The single biggest day each athlete has logged so far.")

    if df.empty:
        st.info("No data available.")
        return

    unit   = unit_label(use_miles)
    factor = config.KM_TO_MI if use_miles else 1.0

    # Sum all activities per athlete per day, then find the max day
    daily = (
        df.groupby(["athlete_name", "date"])["km"]
        .sum()
        .reset_index()
    )
    bests = (
        daily.groupby("athlete_name")["km"]
        .max()
        .mul(factor)
        .reset_index()
        .rename(columns={"km": unit})
        .sort_values(unit, ascending=True)
    )

    colors = [
        _ATHLETE_COLORS[i % len(_ATHLETE_COLORS)]
        for i in range(len(bests))
    ]

    fig = go.Figure(
        go.Bar(
            x=bests[unit].round(1),
            y=bests["athlete_name"],
            orientation="h",
            marker_color=colors,
            text=bests[unit].round(1).astype(str) + f" {unit}",
            textposition="outside",
        )
    )
    fig.update_layout(
        xaxis_title=f"Best single-day distance ({unit})",
        yaxis_title="",
        margin=dict(t=20, b=40, l=20, r=80),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# VIZ 2 — Activity DNA
# ─────────────────────────────────────────────────────────────────────────────

def _chart_activity_dna(df: pd.DataFrame, use_miles: bool) -> None:
    """
    Per-athlete stacked horizontal bar showing how many miles came from
    each activity type — their unique "activity DNA".
    """
    st.subheader("🧬 Activity DNA")
    st.caption(
        "How each athlete's miles break down by activity type — "
        "a glimpse at their unique fitness personality."
    )

    if "activity_type" not in df.columns or df.empty:
        st.info("No activity type data available.")
        return

    unit   = unit_label(use_miles)
    factor = config.KM_TO_MI if use_miles else 1.0

    totals = (
        df.groupby(["athlete_name", "activity_type"])["km"]
        .sum()
        .mul(factor)
        .reset_index()
        .rename(columns={"km": unit})
    )

    athletes = totals["athlete_name"].unique().tolist()
    activity_types = totals["activity_type"].unique().tolist()

    fig = go.Figure()
    for act_type in activity_types:
        subset = totals[totals["activity_type"] == act_type]
        # Align to full athlete list
        values = [
            float(subset[subset["athlete_name"] == a][unit].sum())
            for a in athletes
        ]
        fig.add_trace(
            go.Bar(
                name=act_type,
                y=athletes,
                x=[round(v, 1) for v in values],
                orientation="h",
                marker_color=_COLOR_MAP.get(act_type, "#AB63FA"),
                text=[f"{v:.1f} {unit}" for v in values],
                textposition="inside",
            )
        )

    fig.update_layout(
        barmode="stack",
        xaxis_title=f"Total {unit}",
        yaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40, b=40, l=20, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# VIZ 3 — Training Consistency Heatmap
# ─────────────────────────────────────────────────────────────────────────────

def _chart_consistency_heatmap(
    df: pd.DataFrame,
    start: date,
    end: date,
) -> None:
    """
    GitHub-style training consistency: one cell per (athlete, calendar week)
    coloured by number of active days that week.
    """
    st.subheader("📅 Training Consistency")
    st.caption(
        "How many days per week each athlete logged at least one activity. "
        "Darker = more active days that week."
    )

    if df.empty:
        st.info("No data available.")
        return

    # Active days per athlete per ISO week
    active = (
        df[["athlete_name", "date"]]
        .drop_duplicates()
        .copy()
    )
    active["week"] = pd.to_datetime(active["date"]).dt.isocalendar().week.astype(int)
    active["year"] = pd.to_datetime(active["date"]).dt.isocalendar().year.astype(int)
    active["year_week"] = (
        active["year"].astype(str) + "-W"
        + active["week"].astype(str).str.zfill(2)
    )

    counts = (
        active.groupby(["athlete_name", "year_week"])
        .size()
        .reset_index(name="active_days")
    )

    pivot = counts.pivot(index="athlete_name", columns="year_week", values="active_days").fillna(0)
    # Sort columns chronologically
    pivot = pivot.reindex(sorted(pivot.columns), axis=1)

    athletes   = pivot.index.tolist()
    weeks      = pivot.columns.tolist()
    z_values   = pivot.values.tolist()

    fig = go.Figure(
        go.Heatmap(
            x=weeks,
            y=athletes,
            z=z_values,
            colorscale="YlGn",
            zmin=0,
            zmax=7,
            colorbar=dict(title="Active days", tickvals=[0, 1, 3, 5, 7]),
            hovertemplate="Week: %{x}<br>Athlete: %{y}<br>Active days: %{z}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis_title="ISO Week",
        yaxis_title="",
        margin=dict(t=20, b=60, l=20, r=20),
        xaxis=dict(tickangle=-45),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def render(
    df: pd.DataFrame,
    start: date,
    end: date,
    use_miles: bool = True,
) -> None:
    """Render all three Misc visualizations."""
    _chart_activity_dna(df, use_miles)
    st.divider()
    _chart_personal_bests(df, use_miles)
    st.divider()
    _chart_consistency_heatmap(df, start, end)
