"""
viz/route_map.py — Virtual European route map visualization.

Shows the group's cumulative progress as a position on a folium map
through the pre-defined European city route.
"""

from __future__ import annotations

import math
from datetime import date

import folium
import streamlit as st
from streamlit_folium import st_folium

from viz.shared import build_cumulative, to_display, unit_label


# ─────────────────────────────────────────────────────────────────────────────
# HAVERSINE (kept here since only used by route map)
# ─────────────────────────────────────────────────────────────────────────────

def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in km between two (lat, lon) points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@st.cache_data(show_spinner="Building route…")
def build_city_route(city_stops: tuple[dict, ...]) -> list[dict]:
    """Compute cumulative route distances from pre-geocoded city coordinates."""
    route: list[dict] = []
    cumulative        = 0.0
    prev_lat = prev_lon = None

    for stop in city_stops:
        lat = stop["lat"]
        lon = stop["lon"]
        if prev_lat is not None:
            cumulative += _haversine(prev_lat, prev_lon, lat, lon)
        route.append(
            {
                "name":          stop["name"],
                "lat":           lat,
                "lon":           lon,
                "cumulative_km": round(cumulative, 1),
            }
        )
        prev_lat, prev_lon = lat, lon

    return route


def render(
    df: "pd.DataFrame",
    start: date,
    end: date,
    city_route: list[dict],
    use_miles: bool = True,
) -> None:
    """Render the Virtual European Route map."""
    st.subheader("🗺️ Virtual European Route")

    cumulative  = build_cumulative(df, start, end)
    group_total = float(cumulative.sum(axis=1).iloc[-1]) if not cumulative.empty else 0.0

    unit = unit_label(use_miles)

    # Determine current position on the route (comparison in km)
    current_city_idx = 0
    next_city_idx    = 1 if len(city_route) > 1 else None

    for i, city in enumerate(city_route):
        if group_total >= city["cumulative_km"]:
            current_city_idx = i
        else:
            next_city_idx = i
            break
    else:
        next_city_idx = None

    current_city = city_route[current_city_idx]

    if next_city_idx is not None:
        next_city       = city_route[next_city_idx]
        dist_to_next_km = next_city["cumulative_km"] - group_total
        dist_to_next    = to_display(dist_to_next_km, use_miles)
        next_city_label = next_city["name"]
    else:
        dist_to_next    = 0.0
        next_city_label = "—"

    # ── Folium map ────────────────────────────────────────────────────────────
    m = folium.Map(
        location=[current_city["lat"], current_city["lon"]],
        zoom_start=5,
        tiles="CartoDB positron",
    )

    route_fg = folium.FeatureGroup(name="Route")
    route_coords = [[c["lat"], c["lon"]] for c in city_route]
    folium.PolyLine(
        locations=route_coords,
        color="#3388ff",
        weight=3,
        opacity=0.7,
        tooltip="Challenge route",
    ).add_to(route_fg)

    cities_fg = folium.FeatureGroup(name="Cities")
    for i, city in enumerate(city_route):
        reached = group_total >= city["cumulative_km"]
        color   = "green" if reached else "gray"
        icon    = "flag" if (i == current_city_idx and next_city_idx is not None) else (
                  "trophy" if reached and i == len(city_route) - 1 else "map-marker"
        )
        city_dist_display = round(to_display(city["cumulative_km"], use_miles), 1)
        folium.Marker(
            location=[city["lat"], city["lon"]],
            tooltip=(
                f"{city['name']} — {city_dist_display} {unit}"
                + (" ✅" if reached else "")
            ),
            icon=folium.Icon(color=color, icon=icon, prefix="fa"),
        ).add_to(cities_fg)

    position_fg = folium.FeatureGroup(name="Group position")
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

    group_total_display = round(to_display(group_total, use_miles), 1)
    folium.Marker(
        location=[lat, lon],
        tooltip=f"📍 Group position: {group_total_display} {unit}",
        icon=folium.Icon(color="red", icon="users", prefix="fa"),
    ).add_to(position_fg)

    st_folium(
        m,
        feature_group_to_add=[route_fg, cities_fg, position_fg],
        width=900,
        height=500,
    )

    col1, col2 = st.columns(2)
    col1.metric("Current position", current_city["name"])
    if next_city_idx is not None:
        col2.metric(f"Next city: {next_city_label}", f"{dist_to_next:.1f} {unit} to go")
    else:
        col2.metric("Route complete! 🎉", f"{group_total_display:.1f} {unit} total")
