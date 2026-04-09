"""
viz/elevation_viz.py — Hybrid elevation chart.

Overlays a line chart of each athlete's cumulative elevation gain on top of
a bar chart of real-world tall landmarks.  Horizontal dotted reference lines
mark the top of each landmark bar so it's easy to see when an athlete crosses
a milestone.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from viz.shared import build_cumulative


# ── Landmark definitions ──────────────────────────────────────────────────────
# (name, height_m, bar_color, emoji)
_LANDMARKS: list[tuple[str, float, str, str]] = [
    ("Tallest Tree (Hyperion)", 116.0,    "#228B22", "🌲"),
    ("Space Needle",            184.0,    "#4682B4", "🗼"),
    ("Eiffel Tower",            330.0,    "#C0A060", "🗼"),
    ("Empire State Bldg",       443.0,    "#708090", "🏢"),
    ("Burj Khalifa",            828.0,    "#C8A84B", "🏙️"),
    ("Mount Si",              1_270.0,   "#6B8E23", "⛰️"),
    ("Mount Rainier",         4_392.0,   "#8B7D7B", "🏔️"),
    ("Mount Everest",         8_848.9,   "#A9A9A9", "🏔️"),
]

# Athlete colour palette
_ATHLETE_COLORS = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
    "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52",
]


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def render(df: pd.DataFrame, start: date, end: date) -> None:
    """Render the Elevation Milestones hybrid chart."""
    st.subheader("🏔️ Elevation Milestones")
    st.caption(
        "Cumulative elevation gain overlaid on real-world landmark heights. "
        "Dotted lines show each milestone — see when you've 'climbed' past them!"
    )

    if df.empty or "elevation_gain_m" not in df.columns:
        st.info("No elevation data available.")
        return

    # ── Build cumulative elevation per athlete ────────────────────────────────
    cumulative = build_cumulative(df, start, end, "elevation_gain_m")
    if cumulative.empty:
        st.info("No elevation data available.")
        return

    athletes = cumulative.columns.tolist()
    max_athlete_elev = float(cumulative.max().max()) if not cumulative.empty else 0.0

    # Determine which landmarks to show (only those below 2× the max athlete value,
    # or always show up to Everest for context)
    show_limit = max(max_athlete_elev * 2, _LANDMARKS[-1][1])
    visible_landmarks = [lm for lm in _LANDMARKS if lm[1] <= show_limit]

    fig = go.Figure()

    # ── Landmark bars ─────────────────────────────────────────────────────────
    for name, height, color, emoji in visible_landmarks:
        display_name = f"{emoji} {name}"
        fig.add_trace(
            go.Bar(
                name=display_name,
                x=[display_name],
                y=[height],
                xaxis="x2",
                marker_color=color,
                marker_line_color="rgba(0,0,0,0.3)",
                marker_line_width=1,
                width=0.6,
                showlegend=True,
                legendgroup="landmarks",
                legendgrouptitle_text="Landmarks",
                hovertemplate=(
                    f"<b>{display_name}</b><br>Height: {height:,.0f} m<extra></extra>"
                ),
            )
        )

        # Dotted horizontal reference line at the top of this bar
        fig.add_hline(
            y=height,
            line_dash="dot",
            line_color=color,
            line_width=1.5,
            opacity=0.6,
            annotation_text=f"{emoji} {height:,.0f} m",
            annotation_position="top right",
            annotation_font_size=10,
        )

    # ── Per-athlete cumulative elevation lines ────────────────────────────────
    dates_list = cumulative.index.tolist()
    for idx, athlete in enumerate(athletes):
        color = _ATHLETE_COLORS[idx % len(_ATHLETE_COLORS)]
        values = cumulative[athlete].tolist()
        current = values[-1] if values else 0.0
        fig.add_trace(
            go.Scatter(
                x=dates_list,
                y=values,
                mode="lines",
                name=f"{athlete} ({current:,.0f} m)",
                line=dict(color=color, width=2.5),
                legendgroup="athletes",
                legendgrouptitle_text="Athletes",
                hovertemplate=(
                    f"<b>{athlete}</b><br>Date: %{{x|%b %d}}<br>"
                    "Cumulative elevation: %{y:,.0f} m<extra></extra>"
                ),
            )
        )

    # ── Layout ────────────────────────────────────────────────────────────────
    fig.update_layout(
        yaxis_title="Elevation (m)",
        xaxis_title="",
        # Secondary x-axis for landmark bars: categorical and evenly spaced,
        # overlaid on the date-based primary axis; tick labels hidden.
        xaxis2=dict(
            overlaying="x",
            side="bottom",
            showticklabels=False,
            showgrid=False,
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01,
            groupclick="toggleitem",
        ),
        margin=dict(t=40, b=60, l=60, r=160),
        hovermode="x unified",
        barmode="group",
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Milestone achievement table ───────────────────────────────────────────
    with st.expander("🏅 Milestone achievements"):
        rows = []
        for athlete in athletes:
            final_elev = float(cumulative[athlete].iloc[-1]) if not cumulative.empty else 0.0
            crossed = [
                f"{emoji} {name} ({height:,.0f} m)"
                for name, height, _, emoji in visible_landmarks
                if final_elev >= height
            ]
            rows.append({
                "Athlete": athlete,
                "Total elevation (m)": f"{final_elev:,.0f}",
                "Milestones crossed": len(crossed),
                "Latest milestone": crossed[-1] if crossed else "—",
            })
        st.dataframe(pd.DataFrame(rows).set_index("Athlete"), use_container_width=True)
