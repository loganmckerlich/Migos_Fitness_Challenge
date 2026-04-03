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
    Return a human-readable string like '+5.3 mi ahead' or '-2.1 mi behind'.
    """
    diff = actual - target
    if diff >= 0:
        return f"+{diff:.1f} {unit} ahead"
    return f"{diff:.1f} {unit} behind"


# ─────────────────────────────────────────────────────────────────────────────
# CUMULATIVE DATA BUILDER
# ─────────────────────────────────────────────────────────────────────────────


def build_cumulative(df: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    """
    Pivot daily distances into a cumulative daily table.
    Columns: date + one column per athlete name (values in km).
    """
    all_dates = pd.date_range(start=start, end=min(end, date.today()), freq="D")

    pivot = df.pivot_table(
        index="date", columns="athlete_name", values="km", aggfunc="sum"
    ).reindex(all_dates, fill_value=0)
    pivot.index.name = "date"

    cumulative = pivot.fillna(0).cumsum()
    return cumulative
