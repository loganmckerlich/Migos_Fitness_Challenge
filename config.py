"""
config.py — Challenge settings for the Migos Fitness Challenge app.
Edit these values to customise the challenge, or override them in the sidebar.
"""

from datetime import date

# ── Challenge dates & goal ────────────────────────────────────────────────────
CHALLENGE_START: date = date(2026, 1, 1)
CHALLENGE_END: date   = date(2026, 12, 31)
KM_TO_MI: float       = 0.621371                  # conversion factor: 1 km → miles
GOAL_MI: float        = 7298.0                    # total group distance goal in miles
GOAL_KM: float        = GOAL_MI / KM_TO_MI        # total group distance goal in kilometres

# ── Athletes ──────────────────────────────────────────────────────────────────
# Each entry: {"id": <strava_athlete_id>, "name": "<Display Name>"}
# Replace the IDs with real Strava athlete IDs when USE_DUMMY_DATA is False.
ATHLETES: list[dict] = [
    {"id": 56163722, "name": "Logan McKerlich"},
#    {"id": 222222, "name": "Jamie Nguyen"},
#    {"id": 333333, "name": "Sam Torres"},
#    {"id": 444444, "name": "Alex Rivera"},
#    {"id": 555555, "name": "Casey Kim"},
]

# ── European city route ───────────────────────────────────────────────────────
# The group's virtual journey through Europe (duplicates removed).
# Lat/lon coordinates and cumulative distances are computed dynamically in
# app.py using the Nominatim geocoding API and the haversine formula.
CITY_STOPS: list[str] = [
    "Lisbon",
    "Sines",
    "Albufeira",
    "Huelva",
    "Seville",
    "Jerez",
    "Gibraltar",
    "Malaga",
    "Roquetas de Mar",
    "Puerto Lumbreras",
    "Alicante",
    "Valencia",
    "Peniscola",
    "Tarragona",
    "Barcelona",
    "Girona",
    "Perpignan",
    "Montpellier",
    "Arles",
    "Marseille",
    "Les Arcs",
    "Monte Carlo",
    "Genoa",
    "La Spezia",
    "Florence",
    "Orvieto",
    "Rome",
    "Pescara",
    "Civitanova Marche",
    "San Marino",
    "Bologna",
    "Venice",
    "Tolmin",
    "Bled",
    "Ljubljana",
    "Zagreb",
    "Senj",
    "Zadar",
    "Split",
    "Tomislavgrad",
    "Sarajevo",
    "Foca",
    "Niksic",
    "Kotor",
    "Shkoder",
    "Tirana",
    "Lushnje",
    "Vlore",
    "Sarande",
    "Preveza",
    "Patras",
    "Athens",
    "Marathon",
    "Lamia",
    "Larissa",
    "Thessaloniki",
    "Kavardarci",
    "Skopje",
    "Vranje",
    "Sofia",
    "Plovdiv",
    "Sliven",
    "Burgas",
    "Varna",
    "Razgrad",
    "Bucharest",
    "Buzau",
    "Cahul",
    "Chisinau",
    "Balta",
    "Uman",
    "Kiev",
    "Naroulia",
    "Babruysk",
    "Baranavichy",
    "Brest",
    "Warsaw",
    "Poznan",
    "Berlin",
    "Hamburg",
    "Bremen",
    "Meppen",
    "Zwolle",
    "Amsterdam",
    "Dordrecht",
    "Brussels",
    "Mons",
    "Saint-Quentin",
    "Paris",
]
