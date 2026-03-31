"""
sign_in_app/app.py — Strava authorisation-code helper.

Usage
-----
1. The Strava authorisation URL is read from st.secrets["strava"]["auth_url"]
   and displayed as a clickable button in the app.
2. The athlete clicks the button, authorises the app on Strava, and is
   redirected to a "broken" localhost URL in their browser address bar.
3. The athlete pastes the full redirect URL into the input box and is shown
   just the code they need to send to Logan.

Deploy for free on Streamlit Community Cloud:
    https://share.streamlit.io

Secrets required (in .streamlit/secrets.toml):
    [strava]
    auth_url = "https://www.strava.com/oauth/authorize?client_id=..."
"""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

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


# ─────────────────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────────────────

st.title("🏃 Migos Fitness — Strava Sign-In Helper")

auth_url = _get_auth_url()

_STEPS_COMMON = """\
2. After you click **Authorize** on Strava your browser will try to load a
   page that looks broken — that's totally normal.
3. **Copy the full URL** from your browser's address bar — it will look
   something like:
   ```
   http://localhost/?state=&code=abc123xyz789&scope=read,activity:read_all
   ```
4. **Paste that URL into the box below.**
5. Copy the code shown and **send it to Logan**. 🎉
"""

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
        st.success("✅ Got it! Here is the code to send to Logan:")
        st.code(code, language=None)
        st.markdown(
            "📱 **Copy that code and send it to Logan.** That's all you need to do!"
        )
    else:
        st.error(
            "⚠️ Couldn't find a `code` in that URL. "
            "Make sure you copied the **full** address from your browser's address bar "
            "after clicking Authorize on Strava."
        )

st.divider()
st.caption(
    "This app only reads the URL you paste — it never connects to Strava directly "
    "and does not store any of your data."
)
