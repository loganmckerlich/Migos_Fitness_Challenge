"""
app.py — Migos Fitness Challenge · Streamlit app entry point.

Features
────────
1. Password protection via st.secrets
2. Per-athlete cumulative distance bar/area chart + trend overlay
3. Group progress vs trend line
4. Virtual route map (Folium) showing progress through European cities

Run locally:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from datetime import date, timedelta

import config
import strava

# ─────────────────────────────────────────────────────────────────────────────
# UNIT HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _to_display(km_value: float, use_miles: bool) -> float:
    """Convert a km value to the display unit (miles or km)."""
    return km_value * config.KM_TO_MI if use_miles else km_value


def _unit_label(use_miles: bool) -> str:
    """Return the abbreviated unit label for the current display preference."""
    return "mi" if use_miles else "km"


# ─────────────────────────────────────────────────────────────────────────────
# PASSWORD PROTECTION
# ─────────────────────────────────────────────────────────────────────────────

def _check_password() -> bool:
    """Return True once the correct password has been entered."""
    try:
        correct_password = st.secrets["app"]["password"]
    except (KeyError, FileNotFoundError):
        # No secret configured — allow access in local dev without secrets
        return True

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        return True

    st.title("🏃 Migos Fitness Challenge")
    pwd = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if pwd == correct_password:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
    return False


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR CONFIG
# ─────────────────────────────────────────────────────────────────────────────

def _sidebar() -> dict:
    """Render sidebar controls and return the current configuration."""
    st.sidebar.header("⚙️ Challenge Settings")

    unit = st.sidebar.radio("Units", ["miles", "km"], index=0)
    use_miles = unit == "miles"

    default_goal = (
        round(config.GOAL_KM * config.KM_TO_MI) if use_miles else config.GOAL_KM
    )
    unit_label = _unit_label(use_miles)
    goal_input = st.sidebar.number_input(
        f"Goal distance ({unit_label})",
        min_value=60.0 if use_miles else 100.0,
        max_value=31000.0 if use_miles else 50000.0,
        value=float(default_goal),
        step=25.0 if use_miles else 50.0,
    )
    # Always store goal internally in km
    goal_km = goal_input / config.KM_TO_MI if use_miles else goal_input

    start_date = st.sidebar.date_input(
        "Challenge start date",
        value=config.CHALLENGE_START,
    )

    end_date = st.sidebar.date_input(
        "Challenge end date",
        value=config.CHALLENGE_END,
    )

    if end_date <= start_date:
        st.sidebar.error("End date must be after start date.")

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Data source: "
        + ("🟡 Dummy data" if strava.USE_DUMMY_DATA else "🟢 Live Strava API")
    )

    return {
        "goal_km": goal_km,
        "start_date": start_date,
        "end_date": end_date,
        "use_miles": use_miles,
    }


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def _load_data(
    athletes_frozen: tuple,
    start: date,
    end: date,
) -> pd.DataFrame:
    """Load (or generate) daily distance data."""
    athletes = [{"id": a[0], "name": a[1]} for a in athletes_frozen]
    secrets = None
    if not strava.USE_DUMMY_DATA:
        try:
            secrets = st.secrets
        except Exception:
            pass
    return strava.get_athlete_daily_distances(athletes, start, end, secrets)


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: build cumulative per-athlete data
# ─────────────────────────────────────────────────────────────────────────────

def _build_cumulative(df: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    """
    Pivot daily distances into a cumulative daily table.
    Columns: date + one column per athlete name.
    """
    # Create full date range
    all_dates = pd.date_range(start=start, end=min(end, date.today()), freq="D")

    pivot = df.pivot_table(
        index="date", columns="athlete_name", values="km", aggfunc="sum"
    ).reindex(all_dates, fill_value=0)
    pivot.index.name = "date"

    # Forward-fill any gaps then cumsum
    cumulative = pivot.fillna(0).cumsum()
    return cumulative


# ─────────────────────────────────────────────────────────────────────────────
# CHART 1: Per-athlete cumulative distances
# ─────────────────────────────────────────────────────────────────────────────

def _chart_per_athlete(
    df: pd.DataFrame,
    start: date,
    end: date,
    goal_km: float,
    athletes: list[dict],
    use_miles: bool = True,
) -> None:
    st.subheader("📊 Per-Athlete Cumulative Distance")

    cumulative = _build_cumulative(df, start, end)

    if cumulative.empty:
        st.info("No data available for the selected date range.")
        return

    total_days    = (end - start).days
    elapsed_days  = (min(date.today(), end) - start).days
    progress_frac = elapsed_days / total_days if total_days > 0 else 0

    n_athletes        = len(athletes)
    per_athlete_goal  = goal_km / n_athletes if n_athletes > 0 else goal_km

    # Trend value for each athlete today
    trend_today = per_athlete_goal * progress_frac

    latest = cumulative.iloc[-1]

    # Highlight ahead/behind
    status = {}
    for name in cumulative.columns:
        val = latest.get(name, 0)
        status[name] = "✅ Ahead" if val >= trend_today else "⚠️ Behind"

    unit = _unit_label(use_miles)

    # Status table
    status_df = pd.DataFrame(
        {
            "Athlete":                   list(latest.index),
            f"Total {unit}":             [round(_to_display(latest[n], use_miles), 1) for n in latest.index],
            f"Trend target ({unit})":    [round(_to_display(trend_today, use_miles), 1)] * len(latest),
            "Status":                    [status[n] for n in latest.index],
        }
    )
    st.dataframe(status_df, use_container_width=True, hide_index=True)

    # Area chart — convert all values for display
    display_cumulative = cumulative * (config.KM_TO_MI if use_miles else 1)
    st.area_chart(display_cumulative, use_container_width=True)

    # Trend line overlay note
    trend_display = _to_display(trend_today, use_miles)
    goal_display  = _to_display(per_athlete_goal, use_miles)
    st.caption(
        f"Trend target today: **{trend_display:.1f} {unit}** per athlete "
        f"({progress_frac*100:.0f}% of challenge elapsed, "
        f"goal {goal_display:.0f} {unit} each)."
    )


# ─────────────────────────────────────────────────────────────────────────────
# CHART 2: Group progress vs trend line
# ─────────────────────────────────────────────────────────────────────────────

def _chart_group_progress(
    df: pd.DataFrame,
    start: date,
    end: date,
    goal_km: float,
    use_miles: bool = True,
) -> None:
    st.subheader("📈 Group Progress vs Trend")

    cumulative    = _build_cumulative(df, start, end)
    group_series  = cumulative.sum(axis=1)

    if group_series.empty:
        st.info("No data available.")
        return

    unit = _unit_label(use_miles)
    goal_display = _to_display(goal_km, use_miles)

    # Convert group series to display units
    group_display = (group_series * config.KM_TO_MI if use_miles else group_series).rename(f"Group total ({unit})")

    # Build trend line from start (0) to end (goal) in display units
    trend_dates  = pd.date_range(start=start, end=end, freq="D")
    trend_values = np.linspace(0, goal_display, len(trend_dates))
    trend_series = pd.Series(trend_values, index=trend_dates, name=f"Trend ({unit})")

    combined = pd.concat([group_display, trend_series], axis=1)

    st.line_chart(combined, use_container_width=True)

    current_total_display = float(group_display.iloc[-1])
    pct = current_total_display / goal_display * 100 if goal_display > 0 else 0
    st.metric(
        "Group total",
        f"{current_total_display:.1f} {unit}",
        f"{pct:.1f}% of {goal_display:.0f} {unit} goal",
    )


# ─────────────────────────────────────────────────────────────────────────────
# CHART 3: Route map
# ─────────────────────────────────────────────────────────────────────────────

def _chart_route_map(
    df: pd.DataFrame,
    start: date,
    end: date,
    city_route: list[dict],
    use_miles: bool = True,
) -> None:
    st.subheader("🗺️ Virtual European Route")

    cumulative    = _build_cumulative(df, start, end)
    # group_total stays in km for route position calculations (route uses cumulative_km)
    group_total   = float(cumulative.sum(axis=1).iloc[-1]) if not cumulative.empty else 0.0

    unit = _unit_label(use_miles)

    # Determine current position on the route (comparison stays in km)
    current_city_idx  = 0
    next_city_idx     = 1 if len(city_route) > 1 else None

    for i, city in enumerate(city_route):
        if group_total >= city["cumulative_km"]:
            current_city_idx = i
        else:
            next_city_idx = i
            break
    else:
        # Reached or passed the last city
        next_city_idx = None

    current_city = city_route[current_city_idx]

    # Distance to next city (computed in km, displayed in selected unit)
    if next_city_idx is not None:
        next_city          = city_route[next_city_idx]
        dist_to_next_km    = next_city["cumulative_km"] - group_total
        dist_to_next       = _to_display(dist_to_next_km, use_miles)
        next_city_label    = next_city["name"]
    else:
        dist_to_next       = 0.0
        next_city_label    = "—"

    # ── Build Folium map ──────────────────────────────────────────────────────
    # Centre map on the current city
    m = folium.Map(
        location=[current_city["lat"], current_city["lon"]],
        zoom_start=5,
        tiles="CartoDB positron",
    )

    # Draw route line
    route_coords = [[c["lat"], c["lon"]] for c in city_route]
    folium.PolyLine(
        locations=route_coords,
        color="#3388ff",
        weight=3,
        opacity=0.7,
        tooltip="Challenge route",
    ).add_to(m)

    # City markers
    for i, city in enumerate(city_route):
        reached = group_total >= city["cumulative_km"]
        color   = "green" if reached else "gray"
        icon    = "flag" if (i == current_city_idx and next_city_idx is not None) else (
                  "trophy" if reached and i == len(city_route) - 1 else "map-marker"
        )
        city_dist_display = round(_to_display(city["cumulative_km"], use_miles), 1)
        folium.Marker(
            location=[city["lat"], city["lon"]],
            tooltip=(
                f"{city['name']} — {city_dist_display} {unit}"
                + (" ✅" if reached else "")
            ),
            icon=folium.Icon(color=color, icon=icon, prefix="fa"),
        ).add_to(m)

    # Current progress marker (interpolated position)
    if next_city_idx is not None:
        seg_start = city_route[current_city_idx]
        seg_end   = city_route[next_city_idx]
        seg_total = seg_end["cumulative_km"] - seg_start["cumulative_km"]
        seg_done  = group_total - seg_start["cumulative_km"]
        frac      = seg_done / seg_total if seg_total > 0 else 0
        lat = seg_start["lat"] + frac * (seg_end["lat"] - seg_start["lat"])
        lon = seg_start["lon"] + frac * (seg_end["lon"] - seg_start["lon"])
    else:
        lat = city_route[-1]["lat"]
        lon = city_route[-1]["lon"]

    group_total_display = round(_to_display(group_total, use_miles), 1)
    folium.Marker(
        location=[lat, lon],
        tooltip=f"📍 Group position: {group_total_display} {unit}",
        icon=folium.Icon(color="red", icon="users", prefix="fa"),
    ).add_to(m)

    st_folium(m, width=900, height=500)

    col1, col2 = st.columns(2)
    col1.metric("Current position", current_city["name"])
    if next_city_idx is not None:
        col2.metric(f"Next city: {next_city_label}", f"{dist_to_next:.1f} {unit} to go")
    else:
        col2.metric("Route complete! 🎉", f"{group_total_display:.1f} {unit} total")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config(
        page_title="Migos Fitness Challenge",
        page_icon="🏃",
        layout="wide",
    )

    if not _check_password():
        st.stop()

    cfg = _sidebar()
    goal_km    = cfg["goal_km"]
    start_date = cfg["start_date"]
    end_date   = cfg["end_date"]
    use_miles  = cfg["use_miles"]

    if end_date <= start_date:
        st.error("Please fix the date range in the sidebar.")
        st.stop()

    unit = _unit_label(use_miles)
    goal_display = _to_display(goal_km, use_miles)
    st.title("🏃 Migos Fitness Challenge")
    st.markdown(
        f"**Goal:** {goal_display:.0f} {unit} &nbsp;|&nbsp; "
        f"**Period:** {start_date} → {end_date}"
    )

    if strava.USE_DUMMY_DATA:
        st.info(
            "ℹ️ Running with **dummy data**. "
            "See `TODO.md` for steps to connect the live Strava API.",
            icon="🟡",
        )

    # Load data
    athletes_frozen = tuple((a["id"], a["name"]) for a in config.ATHLETES)
    df = _load_data(athletes_frozen, start_date, end_date)

    # Render charts
    _chart_group_progress(df, start_date, end_date, goal_km, use_miles)
    st.divider()
    _chart_per_athlete(df, start_date, end_date, goal_km, config.ATHLETES, use_miles)
    st.divider()
    _chart_route_map(df, start_date, end_date, config.CITY_ROUTE, use_miles)


if __name__ == "__main__":
    main()
