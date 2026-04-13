"""
viz/misc.py — Bonus visualizations for the Misc tab.

1. 🏆 Personal Best Days  — horizontal bar of each athlete's single best day
2. 🧬 Activity DNA        — per-athlete stacked bar by activity type miles
3. 📅 Training Consistency — weekly active-day heatmap per athlete
4. 🐆 Speed vs Animals    — compare athlete top speeds to animals & vehicles
5. 🎬 Moving Time         — total hours expressed as movies, flights, work days
6. ❤️ Heart Rate Highs    — highest recorded heart rate per athlete
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
_SWIM_COLOR = "#19D3F3"
_COLOR_MAP  = {"Run": _RUN_COLOR, "Walk": _WALK_COLOR, "Ride": _RIDE_COLOR, "Swim": _SWIM_COLOR}

_ATHLETE_COLORS = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
    "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52",
]


# ─────────────────────────────────────────────────────────────────────────────
# VIZ 1 — Personal Best Days
# ─────────────────────────────────────────────────────────────────────────────

def _chart_personal_bests(df: pd.DataFrame, use_miles: bool, use_hours: bool) -> None:
    """Horizontal bar chart: each athlete's best single-day distance (or hours)."""
    st.subheader("🏆 Personal Best Days")
    st.caption("The single biggest day each athlete has logged so far.")

    if df.empty:
        st.info("No data available.")
        return

    if use_hours and "moving_time_hours" in df.columns:
        display_unit = "hrs"
        value_col    = "moving_time_hours"
        x_label      = "Best single-day time (hrs)"
    else:
        display_unit = unit_label(use_miles)
        factor       = config.KM_TO_MI if use_miles else 1.0
        value_col    = "km"
        x_label      = f"Best single-day distance ({display_unit})"

    # Sum all activities per athlete per day, then find the max day
    daily = (
        df.groupby(["athlete_name", "date"])[value_col]
        .sum()
        .reset_index()
    )

    if use_hours and "moving_time_hours" in df.columns:
        bests = (
            daily.groupby("athlete_name")[value_col]
            .max()
            .reset_index()
            .rename(columns={value_col: display_unit})
            .sort_values(display_unit, ascending=True)
        )
    else:
        bests = (
            daily.groupby("athlete_name")[value_col]
            .max()
            .mul(factor)
            .reset_index()
            .rename(columns={value_col: display_unit})
            .sort_values(display_unit, ascending=True)
        )

    colors = [
        _ATHLETE_COLORS[i % len(_ATHLETE_COLORS)]
        for i in range(len(bests))
    ]

    fig = go.Figure(
        go.Bar(
            x=bests[display_unit].round(1),
            y=bests["athlete_name"],
            orientation="h",
            marker_color=colors,
            text=bests[display_unit].round(1).astype(str) + f" {display_unit}",
            textposition="outside",
        )
    )
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title="",
        margin=dict(t=20, b=40, l=20, r=80),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# VIZ 2 — Activity DNA
# ─────────────────────────────────────────────────────────────────────────────

def _chart_activity_dna(df: pd.DataFrame, use_miles: bool, use_hours: bool) -> None:
    """
    Per-athlete stacked horizontal bar showing how many miles or hours came from
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

    if use_hours and "moving_time_hours" in df.columns:
        display_unit = "hrs"
        value_col    = "moving_time_hours"
        x_label      = f"Total {display_unit}"
    else:
        display_unit = unit_label(use_miles)
        factor       = config.KM_TO_MI if use_miles else 1.0
        value_col    = "km"
        x_label      = f"Total {display_unit}"

    totals = (
        df.groupby(["athlete_name", "activity_type"])[value_col]
        .sum()
        .reset_index()
        .rename(columns={value_col: display_unit})
    )

    if not (use_hours and "moving_time_hours" in df.columns):
        totals[display_unit] = totals[display_unit] * factor

    athletes = totals["athlete_name"].unique().tolist()
    activity_types = totals["activity_type"].unique().tolist()

    fig = go.Figure()
    for act_type in activity_types:
        subset = totals[totals["activity_type"] == act_type]
        # Align to full athlete list
        values = [
            float(subset[subset["athlete_name"] == a][display_unit].sum())
            for a in athletes
        ]
        fig.add_trace(
            go.Bar(
                name=act_type,
                y=athletes,
                x=[round(v, 1) for v in values],
                orientation="h",
                marker_color=_COLOR_MAP.get(act_type, "#AB63FA"),
                text=[f"{v:.1f} {display_unit}" for v in values],
                textposition="inside",
            )
        )

    fig.update_layout(
        barmode="stack",
        xaxis_title=x_label,
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
    dates_dt = pd.to_datetime(active["date"])
    iso_cal  = dates_dt.dt.isocalendar()
    active["week"] = iso_cal.week.astype(int)
    active["year"] = iso_cal.year.astype(int)
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
# VIZ 4 — Speed vs Animals
# ─────────────────────────────────────────────────────────────────────────────

# Reference speeds in km/h (name, speed_kph, color, emoji)
_SPEED_REFS: list[tuple[str, float, str, str]] = [
    ("Tortoise",   0.3,  "#556B2F", "🐢"),
    ("Chicken",   14.0,  "#FFA500", "🐓"),
    ("Pig",       18.0,  "#FF69B4", "🐷"),
    ("Squirrel",  19.0,  "#8B4513", "🐿️"),
    ("Deer",      40.0,  "#228B22", "🦌"),
]


# ─────────────────────────────────────────────────────────────────────────────
# VIZ 6 — Heart Rate constants (shared by _hr_color and reference lines)
# ─────────────────────────────────────────────────────────────────────────────

# (bpm_threshold, zone_label, color)  — listed from lowest to highest
_HR_ZONES: list[tuple[int, str, str]] = [
    (140, "Aerobic zone",    "#FFB300"),
    (160, "Threshold zone",  "#FF6600"),
    (180, "Red zone",        "#FF0000"),
]


def _chart_speed_vs_animals(df: pd.DataFrame) -> None:
    """Horizontal grouped bar comparing athlete top speeds to reference speeds."""
    st.subheader("🐆 Speed vs Animals")
    st.caption("Your recorded top speed versus some well-known fast creatures.")

    if df.empty or "max_speed_kph" not in df.columns:
        st.info("No speed data available.")
        return

    # Athlete top speeds
    athlete_tops = (
        df.groupby("athlete_name")["max_speed_kph"]
        .max()
        .reset_index()
        .rename(columns={"max_speed_kph": "speed_kph"})
    )

    fig = go.Figure()

    # Athlete bars
    for idx, row in athlete_tops.iterrows():
        color = _ATHLETE_COLORS[idx % len(_ATHLETE_COLORS)]
        fig.add_trace(
            go.Bar(
                name=row["athlete_name"],
                y=[row["athlete_name"]],
                x=[row["speed_kph"]],
                orientation="h",
                marker_color=color,
                text=f"{row['speed_kph']:.1f} km/h",
                textposition="outside",
                hovertemplate=(
                    f"<b>{row['athlete_name']}</b><br>"
                    f"Top speed: {row['speed_kph']:.1f} km/h<extra></extra>"
                ),
            )
        )

    # Reference vertical lines
    for ref_name, ref_speed, ref_color, ref_emoji in _SPEED_REFS:
        fig.add_vline(
            x=ref_speed,
            line_dash="dot",
            line_color=ref_color,
            line_width=1.5,
            opacity=0.7,
            annotation_text=f"{ref_emoji} {ref_name} ({ref_speed:.0f})",
            annotation_position="top",
            annotation_font_size=10,
            annotation_font_color=ref_color,
        )

    # Find a sensible x-axis range
    max_speed = max(
        athlete_tops["speed_kph"].max() if not athlete_tops.empty else 0,
        max(s for _, s, _, _ in _SPEED_REFS),
    )

    fig.update_layout(
        xaxis_title="Speed (km/h)",
        xaxis_range=[0, max_speed * 1.15],
        yaxis_title="",
        showlegend=False,
        margin=dict(t=60, b=40, l=20, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# VIZ 5 — Moving Time Equivalents
# ─────────────────────────────────────────────────────────────────────────────

# (label, hours, emoji)
_TIME_REFS: list[tuple[str, float, str]] = [
    ("8-hr work day",        8.0,  "💼"),
    ("Average movie",        1.9,  "🎬"),
    ("Flight to Europe",     9.0,  "✈️"),
    ("Season of a TV show",  9.0,  "📺"),
    ("Cross-country road trip", 40.0, "🚗"),
]


def _chart_moving_time(df: pd.DataFrame) -> None:
    """Table of total moving time expressed as everyday time units."""
    st.subheader("🎬 Moving Time Equivalents")
    st.caption("How does your total moving time compare to everyday activities?")

    if df.empty or "moving_time_hours" not in df.columns:
        st.info("No moving-time data available.")
        return

    athlete_hours = (
        df.groupby("athlete_name")["moving_time_hours"]
        .sum()
        .reset_index()
        .rename(columns={"moving_time_hours": "hours"})
    )

    rows = []
    for _, row in athlete_hours.iterrows():
        entry: dict = {"Athlete": row["athlete_name"], "Total hours": f"{row['hours']:,.1f}"}
        for eq_label, eq_hours, eq_emoji in _TIME_REFS:
            entry[f"{eq_emoji} {eq_label}"] = f"{row['hours'] / eq_hours:,.1f}"
        rows.append(entry)
    st.dataframe(pd.DataFrame(rows).set_index("Athlete"), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# VIZ 6 — Heart Rate Highs
# ─────────────────────────────────────────────────────────────────────────────

def _chart_heart_rate_highs(df: pd.DataFrame) -> None:
    """Horizontal bar chart of the highest recorded heart rate per athlete."""
    st.subheader("❤️‍🔥 Heart Rate Highs")
    st.caption("The highest recorded heart rate for each athlete — how deep in the red zone?")

    if df.empty or "max_heartrate" not in df.columns:
        st.info("No heart rate data available.")
        return

    hr_df = df.dropna(subset=["max_heartrate"])
    if hr_df.empty:
        st.info("No heart rate data available.")
        return

    bests = (
        hr_df.groupby("athlete_name")["max_heartrate"]
        .max()
        .reset_index()
        .sort_values("max_heartrate", ascending=True)
    )

    # Colour-code by heart rate zone using shared _HR_ZONES constant
    def _hr_color(bpm: float) -> str:
        for threshold, _, color in reversed(_HR_ZONES):
            if bpm >= threshold:
                return color
        return "#00CC96"  # easy / below aerobic threshold

    colors = [_hr_color(float(v)) for v in bests["max_heartrate"]]

    fig = go.Figure(
        go.Bar(
            x=bests["max_heartrate"],
            y=bests["athlete_name"],
            orientation="h",
            marker_color=colors,
            text=[f"{int(v)} bpm" for v in bests["max_heartrate"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Max HR: %{x:.0f} bpm<extra></extra>",
        )
    )

    # Reference zone lines (drawn from shared _HR_ZONES constant)
    for bpm, label, color in _HR_ZONES:
        fig.add_vline(
            x=bpm,
            line_dash="dot",
            line_color=color,
            line_width=1.5,
            opacity=0.6,
            annotation_text=label,
            annotation_position="top",
            annotation_font_size=10,
            annotation_font_color=color,
        )

    fig.update_layout(
        xaxis_title="Heart rate (bpm)",
        yaxis_title="",
        margin=dict(t=20, b=40, l=20, r=100),
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
    use_hours: bool = False,
) -> None:
    """Render all Misc visualizations."""
    _chart_activity_dna(df, use_miles, use_hours)
    st.divider()
    _chart_personal_bests(df, use_miles, use_hours)
    st.divider()
    _chart_consistency_heatmap(df, start, end)
    st.divider()
    _chart_speed_vs_animals(df)
    st.divider()
    _chart_moving_time(df)
    st.divider()
    _chart_heart_rate_highs(df)
