"""
sign_in_app/app.py — Strava authorisation-code helper.

Usage
-----
1. The Strava authorisation URL is read from st.secrets["strava"]["auth_url"]
   and displayed as a clickable button in the app.
2. The athlete clicks the button, authorises the app on Strava, and is
   redirected to a "broken" localhost URL in their browser address bar.
3. The athlete pastes the full redirect URL into the input box.
4. If client_id and client_secret are configured in secrets the app
   exchanges the code for a token automatically and shows the athlete their
   Strava Athlete ID (and refresh token) to send to Logan — no manual code
   copying required.  Without those secrets the app falls back to showing
   just the raw auth code.

Deploy for free on Streamlit Community Cloud:
    https://share.streamlit.io

Secrets required (in .streamlit/secrets.toml):
    [strava]
    auth_url      = "https://www.strava.com/oauth/authorize?client_id=..."
    client_id     = "YOUR_STRAVA_CLIENT_ID"
    client_secret = "YOUR_STRAVA_CLIENT_SECRET"
"""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import requests
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Migos Fitness — Strava Sign-In Helper",
    page_icon="🏃",
    layout="centered",
)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────


def _extract_code(raw_url: str) -> str | None:
    """
    Parse `raw_url` and return the value of the ``code`` query parameter,
    or ``None`` if it is not present.

    Handles both a full URL and a bare query string (e.g. ``?code=abc&…``).
    """
    raw_url = raw_url.strip()
    if not raw_url:
        return None

    # If the user only pasted the query string portion, prepend a dummy scheme
    # so urlparse can handle it correctly.
    if raw_url.startswith("?"):
        raw_url = "http://localhost/" + raw_url

    parsed = urlparse(raw_url)
    params = parse_qs(parsed.query)
    code_list = params.get("code")
    if not code_list:
        return None
    return code_list[0]


def _get_auth_url() -> str | None:
    """Return the Strava auth URL from secrets, or None if not configured."""
    try:
        return st.secrets["strava"]["auth_url"]
    except (KeyError, FileNotFoundError):
        return None


def _get_strava_credentials() -> tuple[str | None, str | None]:
    """Return (client_id, client_secret) from secrets, or (None, None)."""
    try:
        return (
            str(st.secrets["strava"]["client_id"]),
            str(st.secrets["strava"]["client_secret"]),
        )
    except (KeyError, FileNotFoundError):
        return None, None


def _exchange_code(code: str) -> dict | None:
    """
    Exchange a Strava auth code for an access/refresh token.

    Returns the full JSON response dict (which includes ``athlete.id`` and
    ``refresh_token``) on success, or ``None`` if credentials are not
    configured or the request fails.
    """
    client_id, client_secret = _get_strava_credentials()
    if not client_id or not client_secret:
        return None
    try:
        resp = requests.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except (requests.RequestException, ValueError):
        return None


# ─────────────────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────────────────

st.title("🏃 Migos Fitness — Strava Sign-In Helper")

auth_url = _get_auth_url()

_client_id, _client_secret = _get_strava_credentials()
_has_credentials = bool(_client_id and _client_secret)

_STEP_5 = (
    "5. Copy the **Athlete ID** and **Refresh Token** shown below and "
    "**send them to Logan**. 🎉"
    if _has_credentials
    else "5. Copy the code shown and **send it to Logan**. 🎉"
)

_STEPS_COMMON = (
    "2. After you click **Authorize** on Strava your browser will try to load a\n"
    "   page that looks broken — that's totally normal.\n"
    "3. **Copy the full URL** from your browser's address bar — it will look\n"
    "   something like:\n"
    "   ```\n"
    "   http://localhost/?state=&code=abc123xyz789&scope=read,activity:read_all\n"
    "   ```\n"
    "4. **Paste that URL into the box below.**\n"
    + _STEP_5 + "\n"
)

if auth_url:
    st.markdown(
        "### How to use this app\n\n"
        "1. **Click the button below** to authorise Strava access.\n"
        + _STEPS_COMMON
    )
    st.link_button("🔗 Authorise on Strava", auth_url, use_container_width=True)
else:
    st.markdown(
        "### How to use this app\n\n"
        "1. **Click the link Logan sent you** to authorise Strava access.\n"
        + _STEPS_COMMON
    )

st.divider()

pasted_url = st.text_input(
    "Paste the full URL from your browser's address bar here:",
    placeholder="http://localhost/?state=&code=abc123xyz789&scope=read,activity:read_all",
)

if pasted_url:
    code = _extract_code(pasted_url)
    if code:
        token_data = _exchange_code(code)
        if token_data and "athlete" in token_data:
            athlete = token_data["athlete"]
            athlete_id = athlete.get("id", "unknown")
            refresh_token = token_data.get("refresh_token", "")
            first_name = athlete.get("firstname", "")

            st.success(
                f"✅ All done{', ' + first_name if first_name else ''}! "
                "Here is the info to send to Logan:"
            )

            st.markdown("#### 🪪 Your Strava Athlete ID")
            st.code(str(athlete_id), language=None)

            st.markdown("#### 🔑 Your Refresh Token")
            st.code(refresh_token, language=None)

            st.markdown(
                "📱 **Copy both values above and send them to Logan.** "
                "That's all you need to do! 🎉"
            )
        else:
            # Credentials not configured or exchange failed — fall back to
            # showing the raw auth code and manual athlete-ID instructions.
            st.success("✅ Got it! Here is the code to send to Logan:")
            st.code(code, language=None)

            st.markdown(
                "📱 **Copy that code and send it to Logan.**\n\n"
                "---\n\n"
                "### 🪪 Also send Logan your Strava Athlete ID\n\n"
                "To find your Athlete ID:\n\n"
                "1. Open [strava.com](https://www.strava.com) in your browser "
                "and make sure you're logged in.\n"
                "2. Click your profile picture (top-right) → **My Profile**.\n"
                "3. Look at the address bar — the number at the end is your "
                "Athlete ID:\n"
                "   ```\n"
                "   https://www.strava.com/athletes/12345678\n"
                "                                  ^^^^^^^^\n"
                "                                  This number\n"
                "   ```\n"
                "4. Copy that number and send it to Logan along with the code "
                "above. 🎉"
            )
    else:
        st.error(
            "⚠️ Couldn't find a `code` in that URL. "
            "Make sure you copied the **full** address from your browser's address bar "
            "after clicking Authorize on Strava."
        )

st.divider()
st.caption(
    "When credentials are configured this app contacts Strava once to retrieve "
    "your Athlete ID and refresh token — no other data is stored or shared. "
    "Without credentials it only reads the URL you paste and never connects to Strava."
)
