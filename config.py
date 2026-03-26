"""
config.py — Challenge settings for the Migos Fitness Challenge app.
Edit these values to customise the challenge, or override them in the sidebar.
"""

from datetime import date

# ── Challenge dates & goal ────────────────────────────────────────────────────
CHALLENGE_START: date = date(2025, 1, 1)
CHALLENGE_END: date   = date(2025, 3, 31)
GOAL_KM: float        = 1000.0   # total group distance goal in kilometres
KM_TO_MI: float       = 0.621371  # conversion factor: 1 km → miles

# ── Athletes ──────────────────────────────────────────────────────────────────
# Each entry: {"id": <strava_athlete_id>, "name": "<Display Name>"}
# Replace the IDs with real Strava athlete IDs when USE_DUMMY_DATA is False.
ATHLETES: list[dict] = [
    {"id": 111111, "name": "Logan McKerlich"},
    {"id": 222222, "name": "Jamie Nguyen"},
    {"id": 333333, "name": "Sam Torres"},
    {"id": 444444, "name": "Alex Rivera"},
    {"id": 555555, "name": "Casey Kim"},
]

# ── European city route ───────────────────────────────────────────────────────
# The group's virtual journey through Europe.
# Each city has a cumulative distance from the start of the route (in km).
# Adjust cities and distances to match your chosen route.
CITY_ROUTE: list[dict] = [
    {"name": "Lisbon",    "lat": 38.7169, "lon": -9.1395,  "cumulative_km": 0},
    {"name": "Madrid",    "lat": 40.4168, "lon": -3.7038,  "cumulative_km": 640},
    {"name": "Barcelona", "lat": 41.3851, "lon":  2.1734,  "cumulative_km": 1160},
    {"name": "Marseille", "lat": 43.2965, "lon":  5.3698,  "cumulative_km": 1440},
    {"name": "Lyon",      "lat": 45.7640, "lon":  4.8357,  "cumulative_km": 1620},
    {"name": "Paris",     "lat": 48.8566, "lon":  2.3522,  "cumulative_km": 1920},
    {"name": "Brussels",  "lat": 50.8503, "lon":  4.3517,  "cumulative_km": 2050},
    {"name": "Amsterdam", "lat": 52.3676, "lon":  4.9041,  "cumulative_km": 2210},
    {"name": "Berlin",    "lat": 52.5200, "lon": 13.4050,  "cumulative_km": 2650},
    {"name": "Prague",    "lat": 50.0755, "lon": 14.4378,  "cumulative_km": 2930},
    {"name": "Vienna",    "lat": 48.2082, "lon": 16.3738,  "cumulative_km": 3180},
    {"name": "Rome",      "lat": 41.9028, "lon": 12.4964,  "cumulative_km": 3750},
]
