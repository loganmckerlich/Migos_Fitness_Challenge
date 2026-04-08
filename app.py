"""
app.py — Migos Fitness Challenge · Streamlit app entry point.

Features
────────
1. Password protection via st.secrets
2. Athlete Mile Progress — unfilled per-athlete lines + on-trend reference
3. Group Progress vs Trend — stacked area chart per athlete + trend line
4. Virtual route map (Folium) through European cities
5. Foot mile progress tracker with emoji pace indicators
6. Misc — Activity DNA, Personal Bests, Training Consistency heatmap

Run locally:
    streamlit run app.py
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

import config
import strava
from viz import activity_breakdown, athlete_mile_progress, foot_miles, group_progress, misc, route_map
from viz.shared import to_display as _to_display, unit_label as _unit_label


# ─────────────────────────────────────────────────────────────────────────────
# PASSWORD PROTECTION
# ─────────────────────────────────────────────────────────────────────────────

def _check_password() -> bool:
    """Return True once the correct password has been entered."""
    try:
        correct_password = st.secrets["app"]["password"]
    except (KeyError, FileNotFoundError):
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

    unit      = st.sidebar.radio("Units", ["miles", "km"], index=0)
    use_miles = unit == "miles"

    mode      = st.sidebar.radio("Display mode", ["Distance", "Hours"], index=0)
    use_hours = mode == "Hours"

    goal_km    = config.GOAL_KM
    start_date = config.CHALLENGE_START
    end_date   = config.CHALLENGE_END

    ulabel       = _unit_label(use_miles)
    goal_display = round(_to_display(goal_km, use_miles))
    st.sidebar.caption(f"🎯 Goal: {goal_display:,} {ulabel}")
    st.sidebar.markdown("---")
    st.sidebar.caption(f"📅 Challenge period: {start_date} → {end_date}")
    st.sidebar.caption(
        "Data source: "
        + ("🟡 Dummy data" if strava.USE_DUMMY_DATA else "🟢 Live Strava API")
    )

    return {
        "goal_km":    goal_km,
        "start_date": start_date,
        "end_date":   end_date,
        "use_miles":  use_miles,
        "use_hours":  use_hours,
    }


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def _load_data(athletes_frozen: tuple, start: date, end: date) -> pd.DataFrame:
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
# INFO TAB
# ─────────────────────────────────────────────────────────────────────────────

def _tab_info() -> None:
    """Render the Info tab."""
    st.subheader("ℹ️ About the Migos Fitness Challenge")
    st.markdown(
        """
        Welcome to the **Migos Fitness Challenge** — a year-long group fitness
        challenge where everyone tracks their running, walking, and cycling
        distances together towards a shared goal.

        ---

        ### 📅 Challenge Timeline
        | | |
        |---|---|
        | **Start date** | December 29, 2025 |
        | **End date** | December 29, 2026 |
        | **Duration** | 1 year |

        ---

        ### 🎯 The Goal
        The group aims to collectively cover **7,298 miles** (≈ 11,750 km) over
        the course of the year — roughly the distance from **Lisbon to Paris**
        along the virtual European route shown in the 🗺️ Euro Map tab.

        ---

        ### 📊 What Data Do We Use?
        Activity data is pulled automatically from each participant's
        **Strava** account via the Strava API. Only the following fields are
        read from each activity:
        - Distance (km)
        - Activity date
        - Activity type

        No personal profile details, heart-rate data, GPS routes, photos, or
        private notes are accessed or stored.

        ---

        ### ✅ What Counts Towards the Challenge?
        All **outdoor and virtual** activities in the following categories count:

        | Category | Included Strava activity types |
        |---|---|
        | 🏃 **Run** | Run, Trail Run, Virtual Run |
        | 🚶 **Walk** | Walk, Hike |
        | 🚴 **Ride** | Ride, Virtual Ride, Mountain Bike Ride, Gravel Ride |

        Every kilometre (or mile) logged in any of these activity types is added
        to both the group total and your personal total.

        ---

        ### 🔒 Privacy
        Your Strava data is only used for this challenge leaderboard and is not
        shared with any third parties. You can revoke access at any time via
        [Strava Settings → My Apps](https://www.strava.com/settings/apps).
        """
    )


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

    cfg        = _sidebar()
    goal_km    = cfg["goal_km"]
    start_date = cfg["start_date"]
    end_date   = cfg["end_date"]
    use_miles  = cfg["use_miles"]
    use_hours  = cfg["use_hours"]

    unit         = _unit_label(use_miles)
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

    athletes_frozen = tuple((a["id"], a["name"]) for a in config.ATHLETES)
    df = _load_data(athletes_frozen, start_date, end_date)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Overall Progress",
        "📊 Athlete Progress",
        "🦶 Foot Miles",
        "🗺️ Euro Map",
        "🎲 Misc",
        "ℹ️ Info",
    ])

    with tab1:
        group_progress.render(df, start_date, end_date, goal_km, config.ATHLETES, use_miles, use_hours)
        st.divider()
        activity_breakdown.render(df, use_miles, use_hours)

    with tab2:
        athlete_mile_progress.render(df, start_date, end_date, goal_km, config.ATHLETES, use_miles, use_hours)

    with tab3:
        foot_miles.render(df, start_date, end_date, config.ATHLETES, use_miles, use_hours)

    with tab4:
        city_route = route_map.build_city_route(tuple(config.CITY_STOPS))
        route_map.render(df, start_date, end_date, city_route, use_miles)

    with tab5:
        misc.render(df, start_date, end_date, use_miles, use_hours)

    with tab6:
        _tab_info()

    st.divider()
    fallback = "⚡ Powered by <strong>Strava</strong>"
    st.markdown(
        f"""
        <div style='text-align: center; padding: 8px 0 4px 0;'>
            <a href='https://www.strava.com' target='_blank' rel='noopener noreferrer'>
                <img src='https://upload.wikimedia.org/wikipedia/commons/c/cb/Strava_Logo.svg'
                     alt='Powered by Strava' height='28'
                     onerror="this.onerror=null;this.parentElement.innerHTML='<span style=&quot;font-size:0.85em;color:#FC4C02;&quot;>{fallback}</span>';">
            </a>
            <p style='margin: 4px 0 0 0; font-size: 0.78em; color: #888;'>
                All activity data is provided by Strava.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
