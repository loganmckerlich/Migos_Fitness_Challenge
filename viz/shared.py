"""
viz/shared.py — Shared helpers used across multiple visualization modules.
"""

from __future__ import annotations

from datetime import date

import pandas as pd

import config


# ─────────────────────────────────────────────────────────────────────────────
# UNIT HELPERS
# ─────────────────────────────────────────────────────────────────────────────


def to_display(km_value: float, use_miles: bool) -> float:
    """Convert a km value to the display unit (miles or km)."""
    return km_value * config.KM_TO_MI if use_miles else km_value


def unit_label(use_miles: bool) -> str:
    """Return the abbreviated unit label for the current display preference."""
    return "mi" if use_miles else "km"


# ─────────────────────────────────────────────────────────────────────────────
# PACE EMOJI
# ─────────────────────────────────────────────────────────────────────────────

# Emoji tiers based on % above/below target pace
_PACE_TIERS = [
    (25,  "🚀"),   # crushing it — ≥ 25 % ahead
    (15,  "🔥"),   # on fire      — ≥ 15 %
    (5,   "😄"),   # great        — ≥ 5 %
    (0,   "🙂"),   # on pace      — 0–5 %
    (-5,  "😐"),   # slightly off — −5–0 %
    (-15, "😟"),   # behind       — −15 – −5 %
    (-30, "😰"),   # really behind — −30 – −15 %
]
_PACE_WORST = "🚨"  # more than 30 % behind


def pace_emoji(actual: float, target: float) -> str:
    """
    Return an emoji that represents how far *actual* is from *target*.

    Works in any unit — the comparison is purely proportional.
    Returns the worst emoji when both are 0.
    """
    if target <= 0:
        return "🙂" if actual >= 0 else _PACE_WORST
    pct = (actual - target) / target * 100
    for threshold, emoji in _PACE_TIERS:
        if pct >= threshold:
            return emoji
    return _PACE_WORST


def pace_delta_label(actual: float, target: float, unit: str) -> str:
    """
    Return a human-readable string like '+5.3 mi ahead', 'on pace', or '-2.1 mi behind'.
    """
    diff = actual - target
    if abs(diff) < 0.05:
        return "on pace"
    if diff > 0:
        return f"+{diff:.1f} {unit} ahead"
    return f"{diff:.1f} {unit} behind"


# ─────────────────────────────────────────────────────────────────────────────
# CUMULATIVE DATA BUILDER
# ─────────────────────────────────────────────────────────────────────────────


def build_cumulative(
    df: pd.DataFrame,
    start: date,
    end: date,
    value_col: str = "km",
) -> pd.DataFrame:
    """
    Pivot daily values into a cumulative daily table.

    Parameters
    ----------
    df : DataFrame with at least ``date``, ``athlete_name``, and ``value_col`` columns.
    start, end : Challenge date range.
    value_col : Column to accumulate (default ``"km"``; use ``"moving_time_hours"``
                for hours-based visualizations).

    Returns
    -------
    DataFrame with columns = athlete names and a DatetimeIndex ``date``.
    Values are the running cumulative total of *value_col* up to each day.
    """
    all_dates = pd.date_range(start=start, end=min(end, date.today()), freq="D")

    if value_col not in df.columns:
        # Graceful fallback: return zeros for all athletes
        athletes = df["athlete_name"].unique() if not df.empty else []
        empty = pd.DataFrame(0.0, index=all_dates, columns=athletes)
        empty.index.name = "date"
        return empty

    pivot = df.pivot_table(
        index="date", columns="athlete_name", values=value_col, aggfunc="sum"
    ).reindex(all_dates, fill_value=0)
    pivot.index.name = "date"

    cumulative = pivot.fillna(0).cumsum()
    return cumulative


# ─────────────────────────────────────────────────────────────────────────────
# HOURS / PACE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

_DEFAULT_PACE_HR_PER_KM: float = 0.1  # ~6 min/km — sensible running fallback


def compute_avg_pace_hr_per_km(df: pd.DataFrame) -> float:
    """
    Return the average pace in **hours per km** estimated from *df*.

    The estimate is ``total_moving_time_hours / total_km``.  Falls back to
    ``_DEFAULT_PACE_HR_PER_KM`` when there is no usable data.
    """
    if df.empty or "moving_time_hours" not in df.columns:
        return _DEFAULT_PACE_HR_PER_KM
    total_hours = df["moving_time_hours"].sum()
    total_km = df["km"].sum()
    if total_km <= 0:
        return _DEFAULT_PACE_HR_PER_KM
    return total_hours / total_km

