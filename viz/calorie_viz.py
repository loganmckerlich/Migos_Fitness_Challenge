"""
viz/calorie_viz.py — Calorie equivalents visualization.

Displays a chart of calories burned by each athlete alongside fun
food/body-composition equivalents.

Toggle:
  • Cumulative  — total since the start of the challenge
  • Weekly avg  — per-week average since the start of the challenge
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── Calorie reference values ──────────────────────────────────────────────────
_CALORIE_REFS: dict[str, int] = {
    "Big Mac 🍔":         536,
    "Miller High Life 🍺": 146,
    "Egg 🥚":              78,
    "lb 80/20 beef 🥩":   1_150,
    "lb body fat 💪":      3_500,
}

# Athlete colour palette (mirrors misc.py / group_progress.py)
_ATHLETE_COLORS = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
    "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52",
]


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _weeks_elapsed(start: date, end: date) -> float:
    """Return the number of full/partial weeks between *start* and today (capped at *end*)."""
    days = (min(date.today(), end) - start).days + 1
    return max(days / 7.0, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# CHART — equivalents bar chart
# ─────────────────────────────────────────────────────────────────────────────

def _chart_equivalents(totals: pd.Series, label_suffix: str) -> None:
    """Render a grouped bar chart of calorie equivalents per athlete."""
    fig = go.Figure()

    for eq_name, eq_cal in _CALORIE_REFS.items():
        values = (totals / eq_cal).round(1)
        fig.add_trace(
            go.Bar(
                name=eq_name,
                x=totals.index.tolist(),
                y=values.tolist(),
                text=[f"{v:,.1f}" for v in values],
                textposition="outside",
                hovertemplate=(
                    f"<b>%{{x}}</b><br>{eq_name}: %{{y:,.1f}}{label_suffix}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        barmode="group",
        yaxis_title=f"Equivalents{label_suffix}",
        xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=40, l=20, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TABLE — summary table
# ─────────────────────────────────────────────────────────────────────────────

def _table_calories(totals: pd.Series, label_suffix: str) -> None:
    """Render a summary DataFrame table of calories and equivalents."""
    rows = []
    for athlete, cals in totals.items():
        row: dict = {"Athlete": athlete, f"Calories{label_suffix}": f"{cals:,.0f}"}
        for eq_name, eq_cal in _CALORIE_REFS.items():
            row[eq_name] = f"{cals / eq_cal:,.1f}"
        rows.append(row)
    st.dataframe(pd.DataFrame(rows).set_index("Athlete"), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def render(df: pd.DataFrame, start: date, end: date) -> None:
    """Render the Calorie Equivalents section."""
    st.subheader("🔥 Calorie Equivalents")

    # ── Reference tooltip ─────────────────────────────────────────────────────
    with st.expander("ℹ️ Calorie reference values"):
        ref_rows = [
            {"Item": name, "Calories": f"{cal:,} kcal"}
            for name, cal in _CALORIE_REFS.items()
        ]
        st.table(pd.DataFrame(ref_rows).set_index("Item"))

    if df.empty or "calories" not in df.columns:
        st.info("No calorie data available.")
        return

    # ── Toggle: cumulative vs weekly average ──────────────────────────────────
    mode = st.radio(
        "View mode",
        ["Cumulative", "Weekly average"],
        horizontal=True,
        key="calorie_mode",
    )

    athlete_cals = df.groupby("athlete_name")["calories"].sum()

    if mode == "Weekly average":
        weeks = _weeks_elapsed(start, end)
        totals = (athlete_cals / weeks).round(1)
        label_suffix = " / week"
        caption = (
            "Per-week average calories burned since the start of the challenge. "
            f"Based on {weeks:.1f} weeks elapsed."
        )
    else:
        totals = athlete_cals.round(0)
        label_suffix = " (total)"
        caption = "Total calories burned since the start of the challenge."

    st.caption(caption)

    # ── Summary metrics ───────────────────────────────────────────────────────
    cols = st.columns(len(totals))
    for col, (athlete, cals) in zip(cols, totals.items()):
        col.metric(athlete, f"{cals:,.0f} kcal")

    st.divider()

    # ── Bar chart ─────────────────────────────────────────────────────────────
    _chart_equivalents(totals, label_suffix)

    # ── Data table ────────────────────────────────────────────────────────────
    with st.expander("📋 Full equivalents table"):
        _table_calories(totals, label_suffix)
