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

    goal_km = st.sidebar.number_input(
        "Goal distance (km)",
        min_value=100.0,
        max_value=50000.0,
        value=float(config.GOAL_KM),
        step=50.0,
    )

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

    # Status table
    status_df = pd.DataFrame(
        {
            "Athlete":       list(latest.index),
            "Total km":      [round(latest[n], 1) for n in latest.index],
            "Trend target":  [round(trend_today, 1)] * len(latest),
            "Status":        [status[n] for n in latest.index],
        }
    )
    st.dataframe(status_df, use_container_width=True, hide_index=True)

    # Area chart
    st.area_chart(cumulative, use_container_width=True)

    # Trend line overlay note
    st.caption(
        f"Trend target today: **{trend_today:.1f} km** per athlete "
        f"({progress_frac*100:.0f}% of challenge elapsed, "
        f"goal {per_athlete_goal:.0f} km each)."
    )


# ─────────────────────────────────────────────────────────────────────────────
# CHART 2: Group progress vs trend line
# ─────────────────────────────────────────────────────────────────────────────

def _chart_group_progress(
    df: pd.DataFrame,
    start: date,
    end: date,
    goal_km: float,
) -> None:
    st.subheader("📈 Group Progress vs Trend")

    cumulative    = _build_cumulative(df, start, end)
    group_series  = cumulative.sum(axis=1).rename("Group total (km)")

    if group_series.empty:
        st.info("No data available.")
        return

    total_days = (end - start).days

    # Build trend line from start (0 km) to end (goal_km)
    trend_dates = pd.date_range(start=start, end=end, freq="D")
    trend_values = np.linspace(0, goal_km, len(trend_dates))
    trend_series = pd.Series(trend_values, index=trend_dates, name="Trend (km)")

    combined = pd.concat([group_series, trend_series], axis=1)

    st.line_chart(combined, use_container_width=True)

    current_total = float(group_series.iloc[-1])
    pct = current_total / goal_km * 100 if goal_km > 0 else 0
    st.metric("Group total", f"{current_total:.1f} km", f"{pct:.1f}% of {goal_km:.0f} km goal")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 3: Route map
# ─────────────────────────────────────────────────────────────────────────────

def _chart_route_map(
    df: pd.DataFrame,
    start: date,
    end: date,
    city_route: list[dict],
) -> None:
    st.subheader("🗺️ Virtual European Route")

    cumulative    = _build_cumulative(df, start, end)
    group_total   = float(cumulative.sum(axis=1).iloc[-1]) if not cumulative.empty else 0.0

    # Determine current position on the route
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

    # Distance to next city
    if next_city_idx is not None:
        next_city          = city_route[next_city_idx]
        dist_to_next       = next_city["cumulative_km"] - group_total
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
        folium.Marker(
            location=[city["lat"], city["lon"]],
            tooltip=(
                f"{city['name']} — {city['cumulative_km']} km"
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

    folium.Marker(
        location=[lat, lon],
        tooltip=f"📍 Group position: {group_total:.1f} km",
        icon=folium.Icon(color="red", icon="users", prefix="fa"),
    ).add_to(m)

    st_folium(m, width=900, height=500)

    col1, col2 = st.columns(2)
    col1.metric("Current position", current_city["name"])
    if next_city_idx is not None:
        col2.metric(f"Next city: {next_city_label}", f"{dist_to_next:.1f} km to go")
    else:
        col2.metric("Route complete! 🎉", f"{group_total:.1f} km total")


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

    if end_date <= start_date:
        st.error("Please fix the date range in the sidebar.")
        st.stop()

    st.title("🏃 Migos Fitness Challenge")
    st.markdown(
        f"**Goal:** {goal_km:.0f} km &nbsp;|&nbsp; "
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
    _chart_group_progress(df, start_date, end_date, goal_km)
    st.divider()
    _chart_per_athlete(df, start_date, end_date, goal_km, config.ATHLETES)
    st.divider()
    _chart_route_map(df, start_date, end_date, config.CITY_ROUTE)


if __name__ == "__main__":
    main()
