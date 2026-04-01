"""
config.py — Challenge settings for the Migos Fitness Challenge app.
Edit these values to customise the challenge, or override them in the sidebar.
"""

from datetime import date

# ── Challenge dates & goal ────────────────────────────────────────────────────
CHALLENGE_START: date = date(2025, 12, 29)
CHALLENGE_END: date   = date(2026, 12, 29)
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
# The group's virtual journey through Europe.
# Lat/lon coordinates are pre-geocoded; cumulative distances are computed in
# app.py using the haversine formula.
CITY_STOPS: list[dict] = [
    {"name": "Lisbon",             "lat": 38.7169, "lon":  -9.1399},
    {"name": "Sines",              "lat": 37.9562, "lon":  -8.8697},
    {"name": "Albufeira",          "lat": 37.0896, "lon":  -8.2485},
    {"name": "Huelva",             "lat": 37.2614, "lon":  -6.9447},
    {"name": "Seville",            "lat": 37.3886, "lon":  -5.9823},
    {"name": "Jerez",              "lat": 36.6863, "lon":  -6.1362},
    {"name": "Gibraltar",          "lat": 36.1408, "lon":  -5.3536},
    {"name": "Malaga",             "lat": 36.7195, "lon":  -4.4200},
    {"name": "Roquetas de Mar",    "lat": 36.7640, "lon":  -2.6152},
    {"name": "Puerto Lumbreras",   "lat": 37.5645, "lon":  -1.8091},
    {"name": "Alicante",           "lat": 38.3459, "lon":  -0.4910},
    {"name": "Valencia",           "lat": 39.4699, "lon":  -0.3763},
    {"name": "Peniscola",          "lat": 40.3590, "lon":   0.4036},
    {"name": "Tarragona",          "lat": 41.1172, "lon":   1.2546},
    {"name": "Barcelona",          "lat": 41.3851, "lon":   2.1734},
    {"name": "Girona",             "lat": 41.9794, "lon":   2.8214},
    {"name": "Perpignan",          "lat": 42.6988, "lon":   2.8956},
    {"name": "Montpellier",        "lat": 43.6108, "lon":   3.8767},
    {"name": "Arles",              "lat": 43.6768, "lon":   4.6277},
    {"name": "Marseille",          "lat": 43.2965, "lon":   5.3698},
    {"name": "Les Arcs",           "lat": 43.4584, "lon":   6.4783},
    {"name": "Monte Carlo",        "lat": 43.7396, "lon":   7.4261},
    {"name": "Genoa",              "lat": 44.4056, "lon":   8.9463},
    {"name": "La Spezia",          "lat": 44.1024, "lon":   9.8240},
    {"name": "Florence",           "lat": 43.7696, "lon":  11.2558},
    {"name": "Orvieto",            "lat": 42.7185, "lon":  12.1107},
    {"name": "Rome",               "lat": 41.9028, "lon":  12.4964},
    {"name": "Pescara",            "lat": 42.4584, "lon":  14.2144},
    {"name": "Civitanova Marche",  "lat": 43.3026, "lon":  13.7283},
    {"name": "San Marino",         "lat": 43.9424, "lon":  12.4578},
    {"name": "Bologna",            "lat": 44.4949, "lon":  11.3426},
    {"name": "Venice",             "lat": 45.4408, "lon":  12.3155},
    {"name": "Tolmin",             "lat": 46.1854, "lon":  13.7313},
    {"name": "Bled",               "lat": 46.3683, "lon":  14.1146},
    {"name": "Ljubljana",          "lat": 46.0569, "lon":  14.5058},
    {"name": "Zagreb",             "lat": 45.8150, "lon":  15.9819},
    {"name": "Senj",               "lat": 44.9921, "lon":  14.9060},
    {"name": "Zadar",              "lat": 44.1194, "lon":  15.2314},
    {"name": "Split",              "lat": 43.5081, "lon":  16.4402},
    {"name": "Tomislavgrad",       "lat": 43.7171, "lon":  17.2191},
    {"name": "Sarajevo",           "lat": 43.8563, "lon":  18.4131},
    {"name": "Foca",               "lat": 43.5068, "lon":  18.7795},
    {"name": "Niksic",             "lat": 42.7737, "lon":  18.9456},
    {"name": "Kotor",              "lat": 42.4249, "lon":  18.7712},
    {"name": "Shkoder",            "lat": 42.0683, "lon":  19.5126},
    {"name": "Tirana",             "lat": 41.3317, "lon":  19.8319},
    {"name": "Lushnje",            "lat": 40.9418, "lon":  19.7050},
    {"name": "Vlore",              "lat": 40.4667, "lon":  19.4836},
    {"name": "Sarande",            "lat": 39.8757, "lon":  20.0063},
    {"name": "Preveza",            "lat": 38.9601, "lon":  20.7526},
    {"name": "Patras",             "lat": 38.2466, "lon":  21.7346},
    {"name": "Athens",             "lat": 37.9838, "lon":  23.7275},
    {"name": "Marathon",           "lat": 38.1546, "lon":  23.9667},
    {"name": "Lamia",              "lat": 38.8987, "lon":  22.4346},
    {"name": "Larissa",            "lat": 39.6368, "lon":  22.4141},
    {"name": "Thessaloniki",       "lat": 40.6401, "lon":  22.9444},
    {"name": "Kavardarci",         "lat": 41.4334, "lon":  22.0115},
    {"name": "Skopje",             "lat": 41.9981, "lon":  21.4254},
    {"name": "Vranje",             "lat": 42.5488, "lon":  21.9001},
    {"name": "Sofia",              "lat": 42.6977, "lon":  23.3219},
    {"name": "Plovdiv",            "lat": 42.1354, "lon":  24.7453},
    {"name": "Sliven",             "lat": 42.6870, "lon":  26.3228},
    {"name": "Burgas",             "lat": 42.5048, "lon":  27.4626},
    {"name": "Varna",              "lat": 43.2141, "lon":  27.9147},
    {"name": "Razgrad",            "lat": 43.5274, "lon":  26.5133},
    {"name": "Bucharest",          "lat": 44.4268, "lon":  26.1025},
    {"name": "Buzau",              "lat": 45.1502, "lon":  26.8198},
    {"name": "Cahul",              "lat": 45.9021, "lon":  28.2016},
    {"name": "Chisinau",           "lat": 47.0105, "lon":  28.8638},
    {"name": "Balta",              "lat": 47.9414, "lon":  29.6271},
    {"name": "Uman",               "lat": 48.7467, "lon":  30.2256},
    {"name": "Kiev",               "lat": 50.4501, "lon":  30.5234},
    {"name": "Naroulia",           "lat": 51.8002, "lon":  30.6965},
    {"name": "Babruysk",           "lat": 53.1438, "lon":  29.2208},
    {"name": "Baranavichy",        "lat": 53.1324, "lon":  26.0138},
    {"name": "Brest",              "lat": 52.0976, "lon":  23.7341},
    {"name": "Warsaw",             "lat": 52.2297, "lon":  21.0122},
    {"name": "Poznan",             "lat": 52.4064, "lon":  16.9252},
    {"name": "Berlin",             "lat": 52.5200, "lon":  13.4050},
    {"name": "Hamburg",            "lat": 53.5753, "lon":  10.0153},
    {"name": "Bremen",             "lat": 53.0793, "lon":   8.8017},
    {"name": "Meppen",             "lat": 52.6949, "lon":   7.2916},
    {"name": "Zwolle",             "lat": 52.5168, "lon":   6.0830},
    {"name": "Amsterdam",          "lat": 52.3676, "lon":   4.9041},
    {"name": "Dordrecht",          "lat": 51.8133, "lon":   4.6901},
    {"name": "Brussels",           "lat": 50.8503, "lon":   4.3517},
    {"name": "Mons",               "lat": 50.4542, "lon":   3.9563},
    {"name": "Saint-Quentin",      "lat": 49.8460, "lon":   3.2868},
    {"name": "Paris",              "lat": 48.8566, "lon":   2.3522},
]
