"""
strava.py — Strava API integration for the Migos Fitness Challenge app.

Set USE_DUMMY_DATA = True (default) to run the app without real Strava
credentials.  Set it to False once you have completed the steps in TODO.md
and have valid access tokens stored in .streamlit/secrets.toml.
"""

from __future__ import annotations

import os
import random
from datetime import date, timedelta, datetime
from typing import Optional

import pandas as pd
import requests

# ── Feature flag ──────────────────────────────────────────────────────────────
USE_DUMMY_DATA: bool = false   # ← flip to False to use the live Strava API

# ── Strava OAuth constants ────────────────────────────────────────────────────
STRAVA_BASE_URL = "https://www.strava.com/api/v3"
AUTH_URL        = "https://www.strava.com/oauth/token"

# ─────────────────────────────────────────────────────────────────────────────
# DUMMY DATA
# ─────────────────────────────────────────────────────────────────────────────

# Seed random for reproducible dummy data
_RNG = random.Random(42)


def _generate_dummy_daily_distances(
    athletes: list[dict],
    start: date,
    end: date,
) -> pd.DataFrame:
    """
    Generate plausible per-athlete daily distance rows (km).
    Returns a DataFrame with columns: date, athlete_id, athlete_name, km.
    """
    rows = []
    total_days = (end - start).days + 1
    for athlete in athletes:
        # Each athlete runs 3-5 times per week with distances 5-25 km
        for day_offset in range(total_days):
            current_date = start + timedelta(days=day_offset)
            # ~55 % chance of a run on any given day
            if _RNG.random() < 0.55:
                km = round(_RNG.uniform(4.0, 22.0), 2)
            else:
                km = 0.0
            rows.append(
                {
                    "date": current_date,
                    "athlete_id": athlete["id"],
                    "athlete_name": athlete["name"],
                    "km": km,
                }
            )
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


# ─────────────────────────────────────────────────────────────────────────────
# STRAVA API HELPERS
# ─────────────────────────────────────────────────────────────────────────────


def _refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    """Exchange a refresh token for a fresh access token."""
    resp = requests.post(
        AUTH_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _fetch_athlete_activities(
    access_token: str,
    after: date,
    before: date,
) -> list[dict]:
    """Fetch all activities for a single authenticated athlete in the date range."""
    activities: list[dict] = []
    page = 1
    after_ts  = int(datetime.combine(after,  datetime.min.time()).timestamp())
    before_ts = int(datetime.combine(before, datetime.max.time()).timestamp())

    while True:
        resp = requests.get(
            f"{STRAVA_BASE_URL}/athlete/activities",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "after":  after_ts,
                "before": before_ts,
                "per_page": 200,
                "page":   page,
            },
            timeout=15,
        )
        resp.raise_for_status()
        page_data = resp.json()
        if not page_data:
            break
        activities.extend(page_data)
        page += 1

    return activities


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────


def get_athlete_daily_distances(
    athletes: list[dict],
    start: date,
    end: date,
    secrets: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Return a DataFrame with columns: date, athlete_id, athlete_name, km.

    When USE_DUMMY_DATA is True, returns synthetic data.
    When USE_DUMMY_DATA is False, fetches real data from the Strava API using
    per-athlete refresh tokens stored in `secrets`.

    `secrets` should be the dict-like object from st.secrets, containing:
        secrets["strava"]["client_id"]
        secrets["strava"]["client_secret"]
        secrets["athletes"][str(athlete_id)]["refresh_token"]
    """
    if USE_DUMMY_DATA:
        return _generate_dummy_daily_distances(athletes, start, end)

    # ── Live Strava API path ──────────────────────────────────────────────────
    if secrets is None:
        raise RuntimeError(
            "secrets must be provided when USE_DUMMY_DATA is False. "
            "See TODO.md for setup instructions."
        )

    try:
        client_id     = secrets["strava"]["client_id"]
        client_secret = secrets["strava"]["client_secret"]
    except KeyError as exc:
        raise RuntimeError(
            f"Missing Strava credentials in secrets: {exc}. See TODO.md."
        ) from exc

    rows: list[dict] = []
    for athlete in athletes:
        athlete_id = str(athlete["id"])
        try:
            refresh_token = secrets["athletes"][athlete_id]["refresh_token"]
        except KeyError:
            raise RuntimeError(
                f"No refresh token found for athlete {athlete_id}. See TODO.md."
            )

        access_token = _refresh_access_token(client_id, client_secret, refresh_token)
        raw_activities = _fetch_athlete_activities(access_token, start, end)

        for act in raw_activities:
            # Only count running-type activities (edit to include rides, etc.)
            if act.get("type") not in ("Run", "VirtualRun", "TrailRun"):
                continue
            act_date = datetime.strptime(act["start_date_local"][:10], "%Y-%m-%d").date()
            km = round(act["distance"] / 1000, 2)
            rows.append(
                {
                    "date": pd.Timestamp(act_date),
                    "athlete_id": athlete["id"],
                    "athlete_name": athlete["name"],
                    "km": km,
                }
            )

    if not rows:
        return pd.DataFrame(columns=["date", "athlete_id", "athlete_name", "km"])

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df
